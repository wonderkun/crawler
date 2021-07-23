> 原文链接: https://www.anquanke.com//post/id/189164 


# 工控安全入门（七）—— plc的网络


                                阅读量   
                                **692950**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01569d46c56c145fdc.jpg)](https://p3.ssl.qhimg.com/t01569d46c56c145fdc.jpg)



上一篇我们详细分析了bootram和Vxworks的基本启动流程，这篇文章中我们把视线转到plc的网络部分，同时来复现我们第一个、第二个工控安全漏洞。

## VxWorks的网络设备驱动

一般我们说有三种设备：块设备、字符设备、网络设备，但是考虑到有些特殊设备的重要性和常用性，VxWorks的设备驱动分为了六大驱动，分别是字符设备驱动、串口驱动、块设备驱动、Flash设备驱动、网络设备驱动、USB设备驱动，其中关于串口驱动的知识实际上我们在上篇文章中已经接触到了一些（还记得/tyCo/1和/tyCo/0吗？）。

在六大驱动中，网络设备驱动最为特殊，因为网络设备和IO不打交道，有些人可能会疑惑，我们读写网络数据不就是对于网络设备的IO操作吗？是这样没错，但是我们所说的它和IO不打交道主要是指它没有普通文件的接口，或者说它根本没有对应的设备节点。我们不是像操作磁盘那样，open一个设备，read数据，而是通过socket来进行操作，在socket的基础上再去read、write。也正是如此，所以对于网络设备驱动的研究我们单独拿了出来做一篇文章来讲解。

网络设备作为一种特殊的外设，享受到了与flash、磁盘等Vxworks常见的外设不同的待遇，除了基础的驱动程序之外，还在驱动程序与协议栈之间设置了MUX接口层。这样的设置让驱动层不再需要关注协议层需要什么，只需要提供最基本的读写接口给MUX层，从MUX层读写数据即可；而协议层也不需要关心底层驱动到底是啥样的，有什么特殊性，只需要调用MUX层给的接口来实现数据从MUX的读写即可，这也是操作系统中常见的“解决不了的就加个中间层”的思想。如下图所示：

[![](https://p5.ssl.qhimg.com/t01f51dcd0924ab96ef.png)](https://p5.ssl.qhimg.com/t01f51dcd0924ab96ef.png)

其实在早期的Vxworks中，采取的是协议栈与驱动直接交换数据的方式，但很显然，并不好用，所以后期发展成了这样的形式，当然除了这样的模型外还有满足BSD socket等的网络模型，但考虑到MUX的广泛运用，我们这里还是以MUX为主

在该体系下，对于网络设备驱动来说，又可以分为如下两种：
- END，Enhanced Network Driver，增强型网络驱动，它基于帧传递数据，其实和我们日常在Windows、Linux上接触到的网络驱动较为类似
- NPT，Network Protocol Toolkit，网络协议工具，它相当于是END的改良版或者是进化版，它不再保留链路层信息，以包的形式传递数据
在这两种网络驱动的基础上，到了我们的MUX层，虽说是MUX向上对接协议栈，但要注意，我们所说的协议栈往往是不包括链路层和物理层部分的，这一部分我们更愿意将其视为驱动和设备要完成的功能，我们的协议栈是纯软件的协议栈，如果非要拿TCP/IP来说的话，我们的MUX更像是插在了网络层和链路层之间，如下图所示：

[![](https://p3.ssl.qhimg.com/dm/1024_552_/t01ff7768a5c60f4bad.png)](https://p3.ssl.qhimg.com/dm/1024_552_/t01ff7768a5c60f4bad.png)

当然，你可以不太明白这到底是怎么做到的（比如：ARP之类的怎么办？），没关系，后面的逆向过程中我们再细聊这一部分。

为了更好的分析我们的固件，我们先大致看一下标准的网络初始化过程，为我们下面的逆向打好基础。
- 加载网络设备，因为有了mux层，所以我们需要将驱动程序注册到此处，这样网络设备的注册实际上就分了两个部分，一是设备的加载（驱动程序层），使用endLoad()；一个是mux的加载，muxDevLoad()
- 启动网络设备，同样需要再驱动层endStart()，在mux层muxDevStart()
- 初始化协议栈，说是协议栈，不过一般也就是TCP/IP了，通过usrNetProtoInit调用
- 加载网络协议，我们在完成了设备和mux之间的互动后就该让设备与协议栈联系起来了， ipAttach就是来实现这一步的
完成以上步骤后就可以开始进行网络通信了，通信的调用链一般如下：

muxReceive()-&gt; ipReceiveRtn()-&gt; ip_input()-&gt;…-&gt; tcp_input()-&gt; recv()

send()-&gt;…-&gt;tcp_output()-&gt;…-&gt;ip_output()-&gt;ipOutput()-&gt;…-&gt;ipTxRestart()-&gt;ipTxStartup()-&gt;muxSend()-&gt;send()



## 网络初始化及隐藏的危险

我们从usrRoot进入usrNetworkInit函数，这个函数是一切网络初始化的开始，上面我们所说的加载网络设备、启动网络设备等等工作都是在此进行的。

[![](https://p4.ssl.qhimg.com/t01963c2624f6ced70e.png)](https://p4.ssl.qhimg.com/t01963c2624f6ced70e.png)

可以又调用了一堆init函数，不要心急，我们一个一个来看。首先是我们说过关于协议初始化的usrNetProtoInit函数

[![](https://p0.ssl.qhimg.com/t01f0a122622bc14b7c.png)](https://p0.ssl.qhimg.com/t01f0a122622bc14b7c.png)

同样又是一堆调用，但这次比较有规律，大多数都是xxxLibInit格式，我们首先调用了usrBsdSockLibInit函数，我们前面说xxxLibInit一般是指库的初始化，但要注意凡是usr开头的函数，我们都尽量要去看看，因为里面很可能被用户做了某些自定义的操作。

[![](https://p2.ssl.qhimg.com/t01bcee7bc398ba0acc.png)](https://p2.ssl.qhimg.com/t01bcee7bc398ba0acc.png)

前面我们说过了，当ioGlobalStdSet将标准输入、输出重定向到串口后，我们就可以使用printf一类的函数了，所以这里报错不再是之前的log或是专门的err函数，而是通过打印字符串（当然这部分报错是可以显示给用户的，如果是比较“难”的错误还是会采取log的形式），在逆向过程中，这些字符串可以帮助我们推理出函数的大致流程。

这里可以看到uVar2作为返回值，首先进行sockLib库的初始化，失败了会打印相应的错误，并将uVar2设置为0xFFFFFFFF，下面同理，sockLibAdd实际上就是在根据用户的需要初始化bsdSockLib。只有当所有步骤都成功了才将uVar2置为0。

这里要注意，父函数中并没有对返回值进行检验，起初我以为是Ghidra的反汇编问题，但是查看汇编后发现确实是没有检验，查阅Vxworks给的源码发现同样没有检验，也就是说这里只会打印错误信息，哪怕初始化失败了也不影响系统的下一步运行。

回到usrNetProtoInit，往下都是常规的初始化操作，包括了host table、udp等的lib，这里就不再赘述了。再向上回到usrNetworkInit，进入usrEndLibInit函数。

[![](https://p3.ssl.qhimg.com/t0100ecbda7acf4e3ac.png)](https://p3.ssl.qhimg.com/t0100ecbda7acf4e3ac.png)

end是我们上文提到过的增强型网络驱动，首先使用了muxAddrResFuncAdd添加了arpsolve函数作为地址解析功能，也就是实现了plc的arp功能，所谓arp就是在网络中，将ip地址转换为mac地址的协议，我们可以通过arpsolve进一步分析arp的功能实现，这里不再赘述。

往下是个大循环，很显然循环变量为endDev_Table，每次加6，也就是说这个Table应该是五个一组的，而local_18看起来就是个普通的计数器。

而while循环内部，我们看到，muxDevLoad函数用来加载驱动到mux层，它的参数依次是table的0、1、2、3、4项，所以我们可以把这当做是突破点，我们看一下该函数的定义：

```
void * muxDevLoad
    (
    int                          unit,        /* unit number of device */
    END_OBJ * (* endLoad) (char* ,
    void*                        ),           /* load function of the driver */
    char *                       pInitString, /* init string for this driver */
    BOOL                         loaning,     /* we loan buffers */
    void *                       pBSP         /* for BSP group */
    )

```

显然table[0]代表的应该是驱动的编号，除此之外我们还要关注，table[1]则是驱动的方法，table[2]是驱动的方法，而在muxDevLoad成功装载后，会将table[5]设置为1，也就是标志位。之后再调用muxDevStart来启动设备。

我们在汇编部分可以看到，实际上驱动的函数就是Fec860EndLoad，Fec是fast Ethernet controller的简写，860指明我们的cpu型号。

向下走是usrNetworkBoot函数，该函数主要是处理网络的地址、设备名

[![](https://p3.ssl.qhimg.com/t013a6e5e8261abec20.png)](https://p3.ssl.qhimg.com/t013a6e5e8261abec20.png)

前三个函数都非常简单，分别是获取地址、掩码，usrNetDevNameGet函数用来获取网络设备名称。最后调用了usrNetworkDevStart来进行设备的启动

[![](https://p1.ssl.qhimg.com/t016bf9033483d2692c.png)](https://p1.ssl.qhimg.com/t016bf9033483d2692c.png)

主要是1个物理网络接口以及1个本地回路接口。其中还有包括读取用户设置等操作

[![](https://p5.ssl.qhimg.com/t0194c5cf1581d52469.png)](https://p5.ssl.qhimg.com/t0194c5cf1581d52469.png)

回到usrNetworkInit，接下来会进行Remote的初始化，主要是设置主机和创建Remote连接。

[![](https://p2.ssl.qhimg.com/t019f12a7b77043d28b.png)](https://p2.ssl.qhimg.com/t019f12a7b77043d28b.png)

完成上述步骤之后，我们的设备就算是“连上网了”。然后就终于到了网络初始化中和我们用户最最最最有关系的usrNetAppInit了，看这个酷似usrAppInit的名字我们就该意识到，这是在Vxworks网络方面用户自定义的部分。比如，我们希望在设备上开启nfs（network file system 用于远程文件访问）服务，我们在Tornado中添加NFS组件，INCLUDE_NFS_SERVER，之后会在该函数中自动生成相关的初始化函数

[![](https://p0.ssl.qhimg.com/t01b7b8a1fd701862c8.png)](https://p0.ssl.qhimg.com/t01b7b8a1fd701862c8.png)

rpc为Remote Procedure Call 远程过程调用，这是Vxworks默认会初始化的网络服务，毕竟，远程调用是一个系统要提供的最基本的服务了。

telnet协议是TCP/IP协议族中的一员，是Internet远程登录服务的标准协议和主要方式，同样是默认的

ftp则是File Transfer Protocol，用于在网络传输文件。

ping估计大家就更熟悉了，不再赘述。

snmp是Simple Network Management Protocol 简单网络管理协议，主要用来支持网络管理系统。

估计上面说的几个大家多少都听过，但像是sntpc这种估计就懵了，实际上这是Simple ntp client，ntp是最古老的网络协议之一，主要是用来同步时间的

这些都是初始化一类的函数，显然不是我们该关注的，而这个usrSecurity就比较有意思了，我们点进去看看

[![](https://p0.ssl.qhimg.com/t01b31950f8ac5cba10.png)](https://p0.ssl.qhimg.com/t01b31950f8ac5cba10.png)

loginInit创建了一张login的表，用来保存后续的login信息，而shellLoginInstall则是类似hook的一种函数，它的第一个参数是一个函数，用来替换shell登录时的函数，我们可以简单看一下主要部分（为了方便大家观看我对部分函数进行了重命名，有兴趣的可以自己对这些函数进行逆向，并不困难）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01694eccae86a6d1bf.png)

主要就是在时限内读取了login name和login pass，并检查是否正确，如果正确就登录成功了，当然中间有很多“插曲”，有兴趣有的可以自己探索一下。

最后usrSecurity调用了loginUserAdd

[![](https://p1.ssl.qhimg.com/t0118dfb9a21ad5ab2e.png)](https://p1.ssl.qhimg.com/t0118dfb9a21ad5ab2e.png)

首先去检查上面我们建立的usr表，如果有的话就直接报错，没有的话添加该用户到usr表里。这里就出现大问题了，由于loginUserAdd的参数都是明文字符串，那么我们只要找到登录的地方，是不是就可以直接按照该用户名和密码进行登录呢？

事实上确实是如此，我们暂时跳回到usrAppInit中，同样存在此类情况

[![](https://p0.ssl.qhimg.com/t01f45f9bb6ff70578a.png)](https://p0.ssl.qhimg.com/t01f45f9bb6ff70578a.png)

这就是CVE-2011-4859，著名的施耐德硬编码漏洞，如果我们通过后门账户进行登录，危害性可想而知。而这也是2018工控比赛的一道题目，有兴趣的朋友可以找找那场比赛的相关wp。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_497_/t013b24f89651b71d5c.png)

是不是很兴奋？经过我们七篇文章的积累，我们终于成功找到了我们的第一个工控漏洞，虽然说漏洞年代有点久远，而且漏洞偏简单，但这也是巨大的收获。

如果你有这款plc设备的话，可以利用升级时的bug，来实现让plc瘫痪的功能。使用osLoader软件，该软件用来升级plc的固件版本，只需要输入设备的ip，然后会利用现有的账号密码（其实就是这些我们发现的后门账户）来尝试登录设备然后进行升级，我们只需要指定一个错误的固件，就可以实现plc宕机了。

觉得这样就够了？其实这张小小的一张截图中还有一个CVE！这就是CVE-2011-4860，图中ComputePassword函数存在的漏洞。

该函数涉及到了两个参数，我们首先向上看看这俩参数是何方神圣。

[![](https://p1.ssl.qhimg.com/t0178d6da84137f8d96.png)](https://p1.ssl.qhimg.com/t0178d6da84137f8d96.png)

可以看到eth实际上是调用GetEthAddr，该函数如下：

[![](https://p4.ssl.qhimg.com/t0109d47a682a348525.png)](https://p4.ssl.qhimg.com/t0109d47a682a348525.png)

检测标志位是否为-1，如果是就获取到了mac地址，这里的mac地址并不是我们熟悉的格式，而是数组的形式进行存储。

下面的设备创建、文件系统建立过程我们暂且略过（留到下一篇文章中），看到sprintf，将eth划分了六部分，按照”.2X“的格式排列，实际上就是格式化mac地址。

最后调用ComputePassword进行运算，参数1就是mac地址的数组，参数2保存运算后的密码。

[![](https://p1.ssl.qhimg.com/t01777f5d3df400d503.png)](https://p1.ssl.qhimg.com/t01777f5d3df400d503.png)

可以看到逻辑非常简单将全局变量copy到pass，如下图所示，即开头为0x

[![](https://p5.ssl.qhimg.com/t0132f71358361a9fee.png)](https://p5.ssl.qhimg.com/t0132f71358361a9fee.png)

接着将数组的第三部分拼接到pass，然后调用strtoul，该函数将字符串转换为无符号整数，其中参数一为源，参数二为目标，参数三是基数，这里是0x10，也就是以16进制进行转换（这也就是为什么先把pass的开头部分置为0x的原因了）。

最终进行简单的位处理和异或操作，然后用sprintf将pass置为全局变量所给出的格式

[![](https://p5.ssl.qhimg.com/t0145bc22f0f179a2e1.png)](https://p5.ssl.qhimg.com/t0145bc22f0f179a2e1.png)

这就是最后的pass了，也就是说，我们只需要在知道mac地址的情况下只需要对该”算法“（简单到我都不知道能不能叫它算法）进行逆向即可得到密码。

mac地址的获取方法就多了，最简单的，知道ip了发送arp，即可得知设备的mac地址，然后就可以通过后门账户成功登陆了。



## 总结

这篇文章中我们主要是学习了Vxworks网络相关的知识，同时找到了CVE-2011-4859、CVE-2011-4860的出处，算是在工控安全的路上踏出了重要的一步，但是后面还有很多很多的知识在等着我们。从下一篇文章开始我们将从“main”函数出发，继续我们的固件逆向之旅，同时也会复现我们第三个工控漏洞。
