> 原文链接: https://www.anquanke.com//post/id/194037 


# VNC安全性分析


                                阅读量   
                                **1239546**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者kaspersky，文章来源：ics-cert.kaspersky.com
                                <br>原文地址：[https://ics-cert.kaspersky.com/reports/2019/11/22/vnc-vulnerability-research/](https://ics-cert.kaspersky.com/reports/2019/11/22/vnc-vulnerability-research/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01d4f753e31c436496.png)](https://p4.ssl.qhimg.com/t01d4f753e31c436496.png)



## 0x00 前言

最近我们针对VNC（Virtual Network Computing）远程访问系统做了相关研究，在本文中，我们将与大家分享这方面研究结果。我们发现了一些内存破坏漏洞，总共拿到了37个CVE编号。其中某些漏洞如果被攻击者利用，可能会实现远程代码执行效果。



## 0x01 研究背景

VNC系统可以帮助一台设备远程访问另一台设备的屏幕，需要注意的是，协议规范中并没有限制特定操作系统，允许跨平台实现。VNC在许多操作系统上都有对应的实现版本，包括GNU/Linux、Windows、Android以及其他一些小众系统。

由于跨平台实现以及许可证开源，现在VNC已经是最常用的一种远程管理工具。根据[shodan.io](https://www.shodan.io/search?query=%22rfb%22)统计，互联网上至少有600,000台VNC服务器在线。如果再算上仅在本地网络中可用的设备，这个数字将会变得更为庞大。

根据我们的统计数据，VNC广泛应用于工业自动化系统中。最近我们发布了一篇[文章](https://ics-cert.kaspersky.com/reports/2018/09/20/threats-posed-by-using-rats-in-ics)，介绍了远程管理工具在工业控制系统（ICS）中的应用。根据文章估计，大约有32%的工控系统电脑中安装了包括VNC在内的各种远程管理工具（RAT）。其中18.6%的ICS软件发行包中包含RAT，且会在软件安装时顺带安装，剩下81.4%的RAT则由员工或承包商手动安装。在另一篇[文章](https://ics-cert.kaspersky.com/reports/2018/08/01/attacks-on-industrial-enterprises-using-rms-and-teamviewer/)中，我们分析了一些攻击方法，其中攻击者会安装并使用一些远程管理工具。此外在某些情况下，攻击者还会在攻击过程中利用远程管理工具中的一些漏洞。

根据我们的估计，大多数ICS厂商会在产品中基于VNC来实现远程管理工具，因此对VNC安全性的分析就显得尤为重要。

2019年，Windows RDP（Remote Desktop Services）被曝存在BlueKeep漏洞（[CVE-2019-0708](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0708)），引起了公众的强烈反应。如果Windows主机上正在运行RDP服务器，那么该漏洞就允许未授权攻击者获得该主机的远程代码执行权限。该漏洞影响“较早版本的”操作系统，比如Windows 7 SP1、Windows 2008 Server SP1及SP2。

在Windows中，有些VNC服务端组件以服务形式存在，可以提供高权限访问服务，这意味着这些组件本身就具备系统的高访问权限。这也是我们研究VNC安全性的原因之一。



## 0x02 系统描述

VNC（Virtual Network Computing）是提供访问目标系统用户接口（桌面）的一种系统。VNC使用RFB（remote frame buffer，远程帧缓冲区）协议，在设备之间传输屏幕图像、鼠标移动及键盘事件。通常情况下，每个系统的实现都包括一个服务端组件及客户端组件。由于RFB协议是标准化协议，因此不同实现版本的客户端及服务端之间可以相互通信。服务端组件将服务端的桌面图像发送至客户端，供客户端查看。客户端会将客户端的事件（比如鼠标光标移动、按键、数据拷贝及粘贴）通过剪切缓冲区（cut buffer）发送回服务器。通过这种方式，如果远程主机正在运行VNC服务端，客户端上的用户就可以操控远程主机。

每当远程主机的桌面更新时，VNC服务端都会发送图像。更新操作可能在很多情况下发生，其中就包括客户端的操作。通过网络发送全新的完整截图显然是相对比较耗费资源的一种操作，因此协议没有发送整个屏幕截图，而是只更新因为某些操作或随时间改变的相应像素。RFB还支持多种屏幕更新压缩机编码方法，比如，协议可以使用zlib或者RLE（run-length encoding，行程编码）进行压缩。

虽然该软件本来的应用场景比较明确，但因为包含非常多的功能，因此开发者在研发阶段可能会出现一些纰漏。



## 0x03 可能的攻击点

由于VNC系统由服务端及客户端组件组成，因此我们可以思考如下两个主要的攻击点：

1、攻击者与VNC服务端处于同一个网络中，攻击服务端成功后，可以使用服务端权限在目标主机上执行代码。

2、用户使用VNC客户端连接至攻击者的“服务端”，攻击者利用客户端中的漏洞来攻击用户，在用户主机上执行代码。

显然，攻击者更喜欢在服务端上获得远程代码执行权限。然而，已发现的大多数漏洞都位于系统的客户端组件中。部分原因是因为客户端组件需要包含特定代码，用来解码服务端发送的各种格式的数据。开发者在编写数据解码组件时，经常会犯各种错误，导致出现内存破坏漏洞。

另一方面，服务端的代码量相对较少，只需要向客户端发送经过编码的屏幕更新数据，处理来自客户端的事件即可。根据协议规范，服务端必须支持至少6种消息类型，以提供正常操作所需的所有功能。这意味着大多数服务端组件几乎没有特别复杂的功能，从而减少了开发者出错的机会。然而，某些系统中实现了各种组件，用来增强服务端的功能（比如文件传输、客户端与服务端聊天等[功能](https://vncdotool.readthedocs.io/en/0.8.0/rfbproto.html#client-to-server-messages)）。我们的研究表明，大多数问题都出现在服务端的增强功能中。



## 0x04 研究目标

在此次研究中，我们选择了最广泛使用的几种VNC实现版本：

1、[LibVNC](http://libvnc.github.io/)。这是一个开源跨平台库，用来创建基于RFB协议的自定义应用。比如，VirtualBox使用了LibVNC的服务端组件来提供虚拟机的VNC访问功能。

2、[UltraVNC](https://www.uvnc.com/)。这是适用于Windows平台的较为流行的开源VNC实现方案。许多工业自动化公司会建议用户（如[[1]](https://www.proface.com/product/soft/gpproex/spec/PFXEXEDV40)及[[2]](https://support.industry.siemens.com/cs/document/78463889/how-do-you-remotely-access-wincc-stations-(wincc-v7-and-wincc-professional)-?dti=0&amp;lc=en-WW)）使用该方案，通过RFB协议连接到远程HMI接口。

3、[TightVNC](https://www.tightvnc.com/)。RFB协议的另一种常用实现方案。许多工业自动化系统厂商推荐用户使用该产品从*nix主机连接到HMI接口。

4、[TurboVNC](https://www.turbovnc.org/)。一种开源VNC实现，使用`libjpeg-turbo`库来压缩JPEG图像，以提高图像传输效率。

在本次研究中，我们并没有分析非常受欢迎的一款产品（RealVNC），因为该产品的许可证不允许我们对其进行逆向分析。



## 0x05 已有研究成果

在分析VNC具体实现之前，我们可以先收集相关材料，看这些产品中曾经出现过哪些漏洞。

2014年，Google Security Team发布了一份较短的LibVNC漏洞分析报告。由于该产品的代码量较少，因此我们认为Google工程师已经找到了LibVNC中存在的所有漏洞。然而，我还是在GitHub上找到了一些issue（比如[[3]](https://github.com/LibVNC/libvncserver/issues/218)及[[4]](https://github.com/LibVNC/libvncserver/issues/211)，这些issue时间点都在2014年之后）。

UltraVNC中找到的漏洞数不是特别多，大多数漏洞都与简单的[栈溢出](https://www.exploit-db.com/exploits/18666)问题有关，涉及到将任意长度数据写入栈上长度固定的缓冲区。

已发现的这些漏洞历史都比较久远，随着时间的推移，这些产品的代码量也在增加，情况可能会有所不同。



## 0x06 研究成果

### <a class="reference-link" name="LibVNC"></a>LibVNC

分析已有的漏洞后，我很快就发现文件传输功能的扩展代码中存在一些类似的漏洞。该扩展默认处于未启用状态：开发者必须显式启用该扩展，才能在基于LibVNC的项目中使用。这可能是因为这些漏洞之前没被发现的原因。

接下来我开始研究客户端代码，发现了该项目最为严重的一些漏洞，并且漏洞成因也各不相同，其中有些类别的漏洞同样存在于基于RFB协议的其他项目中。

我们可以认为，这些类别的漏洞与协议的规范密不可分。或者换句话说，协议的具体设计导致开发者无法完全避免这些bug，因此代码中可能存在这类缺陷。

为了对此有直观了解，我们可以观察VNC项目在处理网络消息时所使用的结构。这里我们可以打开`rfbproto.h`文件，该[文件](https://github.com/LibVNC/libvncserver/blob/e0a9d96d56f1cbb99f71d97491102192d2ee4ee4/rfb/rfbproto.h#L21)自从1999年开始已经在VNC项目中使用，存在于包括LibVNC在内的许多项目中。

我们可以参考`rfbClientCutTextMsg`结构来演示第一类漏洞，该结构用于将客户端剪切缓冲区变化信息发送给服务端。

```
typedef struct `{`
    uint8_t type; /* always rfbClientCutText */
    uint8_t pad1;
    uint16_t pad2;
    uint32_t length;
    /* followed by char text[length] */
`}` rfbClientCutTextMsg;
```

建立连接并完成初始化握手后，客户端和服务端协商同意使用特定的屏幕设置，传输的所有消息都使用相同格式。每条消息起始处都包含代表消息类型的1个字节。根据消息类型，服务端会选择匹配的消息处理程序及对应的结构。在不同的VNC客户端中，该结构都采用类似的方式进行[填充](https://github.com/LibVNC/libvncserver/blob/e0a9d96d56f1cbb99f71d97491102192d2ee4ee4/libvncclient/rfbproto.c#L1761)（如下C伪代码）：

```
ReadFullData(socket, ((char *)&amp;msg) + 1, sz_rfbServerSomeMessageType – 1);
```

通过这种方式，除了第1个字节之外，整个消息结构都会被填充。从代码中可知，远程用户可以控制该结构中的所有字段。还需注意的是，`msg`是个`union`类型，可以包含所有可能的消息结构。

由于剪切缓冲区的内容长度未定，因此会采用动态内存分配方式（`malloc`）。需要注意的是，剪切缓冲区中可能会包含文本，并且C语言中使用空字符作为文本数据结束符。考虑到这些信息，且远程用户可以完全控制`uint32_t`类型的`length`字段，这种情况下我们就可以找到一个典型的整数溢出问题（如下C伪代码所示）：

```
char *text = malloc(msg.length + 1);
ReadFullData(socket, text, msg.length);
text[msg.length] = 0;
```

如果攻击者发送的消息中`length`字段的值等于`UINT32_MAX = 2^32– 1 = 0xffffffff`，那么代码就会调用`malloc(0)`函数，导致整数溢出。如果使用的是标准的glibc `malloc`内存分配机制，那么该调用就会返回最小的内存chunk：`16`字节。与此同时，值等于`UINT32_MAX`的长度字段将会以参数形式传入`ReadFullData`函数，对于LibVNC，该操作将导致堆缓冲区溢出。

第二种漏洞类型同样可以用该结构来演示。根据协议或者[RFC](https://tools.ietf.org/html/rfc6143#section-7.5.6)规范，某些结构中为了字段对齐会包含一些填充值。然而从安全研究者的角度来看，这就留下了内存初始化错误的可能性（如[[5]](https://github.com/LibVNC/libvncserver/blob/79516a6aa3e875c8d9f4c83667076aa070fe5d6e/libvncclient/rfbproto.c#L1656)及[[6]](https://sourceforge.net/p/ultravnc/code/1199/)）。来看一下如下错误（C语言伪代码）：

```
rfbClientCutTextMsg cct;
cct.type = rfbClientCutText;
cct.length = length;
WriteToRFBServer(socket, &amp;cct, sz_rfbClientCutTextMsg);
WriteToRFBServer(socket, str, len);
```

该消息结构在栈上创建，填充**某些**字段值后发送给服务端。从代码中可知，结构中的`pad1`及`pad2`字段值为空。因此，未经初始化的值会通过网络发送，攻击者可以从栈中读取未初始化的内存。如果攻击者运气不错，可以访问的内存区域中可能包含堆、栈或者`text`区段的地址，导致攻击者可以绕过ASLR，在客户端上通过溢出实现远程代码执行。

在VNC项目中经常能发现这种琐碎的漏洞，因此我们决定将其归为单独的一类。

需要注意的是，分析LibVNC之类的跨平台解决方案并非易事。在分析这类项目时，我们应当忽略与特定操作系统、主机架构有关的因素，要从C语言标准的角度来分析项目，否则容易忽视代码中存在的明显[缺陷](https://github.com/LibVNC/libvncserver/issues/273)。比如，代码中的堆溢出漏洞在32位平台上没有被正确修复，因为`size_t`在`x86_64`平台上与32位的`x86`平台不一样。

我们已将这些漏洞相关信息反馈给开发者，漏洞已被修复（这里要感谢[Solar Designer](https://twitter.com/solardiz?lang=en)的帮助）。

### <a class="reference-link" name="TightVNC"></a>TightVNC

下面研究GNU/Linux平台上非常流行的VNC客户端实现。

我很快就在该系统中找到了一些漏洞，大多数漏洞非常直接，有些与LibVNC中的问题一样。这两个项目的代码片段对比如下：

[![](https://p3.ssl.qhimg.com/t0153b8807925cf835c.png)](https://p3.ssl.qhimg.com/t0153b8807925cf835c.png)

我们最早在LibVNC项目中找到了该漏洞，漏洞位于CoRRE解码方法中（参考上图右侧代码）。在如上代码中，任意长度的数据会被读取到`rfbClient`结构中长度固定的缓冲区，这样自然会导致缓冲区溢出。奇怪的是，函数指针位于结构中，非常靠近剪切缓冲区之后，因此这离代码执行只有一步之遥。

经过对比可知，除了某些微小的变动之外，LibVNC与TightVNC的代码片段基本一致。这两份代码片段都拷贝自AT&amp;T实验室，开发者在1999年就引入了该漏洞（我通过AT&amp;T实验室许可证中发现了该漏洞，其中也说明了哪位开发人员在哪个时期参与项目研发）。从那时起，代码已经过多次修改。比如在LibVNC中，静态的全局缓冲区已被移动到客户端的结构中。尽管如此，该漏洞在多次修改后依然存在。

此外还需注意的是，`HandleCoRREBPP`是非常原始的一个名称。如果我们在GitHub上搜索包含该字符串的代码，可以找到许多与VNC有关的项目，这些项目无意间拷贝了存在漏洞的解码函数。因此这些项目可能会永远存在漏洞，除非开发者更新项目内容，或者在代码中修复该漏洞。

`HandleCoRREBPP`字符串实际上并不是一个函数名，这里的`BPP`代表“Bits per Pixel”（位数每像素），其值等于8、16或者32，具体取决于客户端及服务端在初始化阶段设置的颜色深度。开发者有可能使用该文件，作为宏代码中的辅助文件，如下所示：

```
#ifndef HandleCoRRE8
#define BPP 32
#include ”corre.h”
#undef BPP
#endif
```

结果为几个函数：`HandleCoRRE8`、`HandleCoRRE16`及`HandleCoRRE32`。

由于该程序最开始由C而不是C++编写，没有模板可用，因此开发者需要使用这种技巧。然而，如果我们Google搜索`HandleCoRRE`或者`HandleCoRRE32`，会发现有些项目稍加修改，不管有没有使用这种格式，但还是可能会包含该漏洞。不幸的是，还有上百个项目未经修改就直接拷贝了这些代码，并且我们无法跟这些开发者取得联系。

TightVNC的漏洞就介绍到此。当我们向TightVNC开发者反馈相关漏洞时，他们向我们表示感谢，并且也表示已经停止开发TightVNC 1.X，不再修复发现的任何漏洞。与此同时，GlavSoft已经开始开发新的TightVNC 2.X，其中并没有包括任何GPL许可的第三方代码，因此会以商用产品方式推出。需要注意的是，适用于Unix系统的TightVNC 2.X只采用商用许可证发型，不会作为开源软件发布。

我们通过[oss-security](https://www.openwall.com/lists/oss-security/2018/12/10/5)报告了TightVNC中找到的漏洞，强调包维护人员需要自己修复这些漏洞。虽然我们在2019年1月份发送报告，但在本文公布时（2019年11月），漏洞仍然没被修复。

### <a class="reference-link" name="TurboVNC"></a>TurboVNC

这个VNC项目需要着重点出：我们发现的一个漏洞令人难以置信。

如下代码片段取自服务端主函数，用来[处理](https://github.com/TurboVNC/turbovnc/blob/8cf390455d62dfd50595f9edfc53bc1349a4c481/unix/Xvnc/programs/Xserver/hw/vnc/rfbserver.c#L1308)用户消息：

```
char data[64];
READ(((char *)&amp;msg) + 1, sz_rfbFenceMsg – 1)
READ(data, msg.f.length)
if (msg.f.length &gt; sizeof(data))
    rfbLog("Ignoring fence.  Payload of %d bytes is too large.\n",
           msg.f.length);
else
    HandleFence(cl, flags, msg.f.length, data);
return;
```

该代码会读取`rfbFenceType`格式的消息，该消息中包含`msg.f.length`长度信息以及`uint8_t`用户数据类型信息，用户数据紧跟在消息之后。由于将任意用户数据写入固定大小的缓冲区，因此存在栈溢出问题。更重要的是，当数据被读取到缓冲区之后，代码才对数据长度进行检查。

由于栈上没有溢出防护机制（即canary防护），该漏洞可能用来控制返回地址，在服务端上实现远程代码执行。然而攻击者首先需要获取认证凭据，才能连接到VNC服务端，或者需要在连接建立之前先控制客户端。

### <a class="reference-link" name="UltraVNC"></a>UltraVNC

对于UltraVNC，我在服务端及客户端组件中都发现了一些漏洞，总共拿到了22个CVE编号。

这个项目有个特点：只适用于Windows系统。当分析可以编译成GNU/Linux应用的项目时，我喜欢使用两种不同的方法来寻找漏洞，首先，我会分析代码，寻找其中的漏洞。其次，我会尝试弄清如何使用fuzz来搜索项目中的漏洞。我在分析LibVNC、TurboVNC及TightVNC时都采用了这个方法。对于这些项目，我很快就能写出基于[libfuzzer](http://llvm.org/docs/LibFuzzer.html)的封装工具，因为该项目并不依赖于特定的操作系统网络API，有一个抽象层负责处理网络数据。为了编写一个好的fuzzer，我们只需要自己实现目标函数，重写网络相关函数。这样来自fuzzer的数据可以反馈到目标程序中，模拟网络传输行为。

然而，在分析适用于Windows的项目时，即使有开源项目，我们也很难使用第二种方法，因为相关工具要么不可用，要么没有得到完美开发。在我开始分析时，适用于Windows的`libfuzzer`还没有发布。此外，Windows应用中使用了面向事件的方法，这意味着我们必须重写大量代码，才能实现良好的fuzz覆盖面。因此在分析UltraVNC时，我只能采用手动分析方法。

经过分析后，我在UltraVNC中发现了一大堆漏洞：从`strcpy`及`sprintf`中的缓冲区溢出漏洞到现实环境中很难碰到的一些奇怪漏洞。下面我们来分析其中某些漏洞。

#### <a class="reference-link" name="CVE-2018-15361"></a>CVE-2018-15361

该漏洞存在于UltraVNC客户端代码中。在初始化阶段，服务端应当提供与显示高度/宽度、色深、调色板及桌面名称等相关信息，这些信息可以显示在窗口的标题栏中。

桌面名称为长度未定的一个字符串。因此，字符串的长度首先会发送给客户端，后面才是字符串数据。相关的代码片段如下所示：

```
void ClientConnection::ReadServerInit()
`{`
    ReadExact((char *)&amp;m_si, sz_rfbServerInitMsg);

    m_si.framebufferWidth = Swap16IfLE(m_si.framebufferWidth);
    m_si.framebufferHeight = Swap16IfLE(m_si.framebufferHeight);
    m_si.format.redMax = Swap16IfLE(m_si.format.redMax);
    m_si.format.greenMax = Swap16IfLE(m_si.format.greenMax);
    m_si.format.blueMax = Swap16IfLE(m_si.format.blueMax);
    m_si.nameLength = Swap32IfLE(m_si.nameLength);

    m_desktopName = new TCHAR[m_si.nameLength + 4 + 256];
    m_desktopName_viewonly = new TCHAR[m_si.nameLength + 4 + 256+16];
    ReadString(m_desktopName, m_si.nameLength);
. . .
`}`
```

如果大家比较细心，可以发现上面存在一个整数溢出漏洞。然而，在这种情况下，该漏洞并不会导致`ReadString`函数存在堆缓冲区溢出问题，而是会带来更为奇怪的一些后果。

```
void ClientConnection::ReadString(char *buf, int length)
`{`
    if (length &gt; 0)
        ReadExact(buf, length);
    buf[length] = '\0';
`}`
```

从代码中可知，`ReadString`函数的功能是读取长度为`length`的一个字符串，然后将其以空字符结尾。需要注意的是，该函数第二个参数为有符号整数。

如果我们在`m_si.nameLength`中指定一个非常大的数字，那么将其作为参数传入`ReadString`函数时，该值会被当成负数。这将导致`length`无法通过条件判断语句，使得`buf`数组未经初始化。此时，`null`字节会被写入`buf + length`地址处。由于`length`是一个负值整数，因此我们可能将`null`字节写到相对`buf`偏移量为负的某个固定位置。

因此，当为`m_desktopName`分配空间，且缓冲区在进程的常规堆上分配时，如果这时候出现整数溢出，就有可能将`null`字节写到之前的一个chunk。如果整数溢出并没有发生，系统有足够的内存，那么就会分配一个较大的缓冲区以及新的堆。使用正确的参数后，远程攻击者可以将一个`null`字节写到`_NT_HEAP`结构中，该结构的位置直接位于大的chunk之前。该漏洞肯定能造成DoS效果，但是否能实现远程代码执行还有待讨论。如果大家在Windows用户态堆漏洞利用上经验丰富，那么可能将该漏洞变成一个RCE漏洞。

#### <a class="reference-link" name="CVE-2019-8262"></a>CVE-2019-8262

该漏洞位于负责数据编码的函数中，研究表明，该功能的安全性及可用性非常依赖于一个简单的线程。

编码函数中使用了来自于`minilzo`库的`lzo1x_decompress`函数。为了理解该漏洞原理，我们需要查看压缩及解压缩函数的原型。

为了调用解压缩函数，我们需要传入包含压缩数据、压缩数据长度、解压数据使用的缓冲区以及对应的缓冲区长度。需要注意的是，如果输入数据无法被解压缩，那么函数可能会返回错误。此外，开发者需要了解被释放到输出缓冲区的数据长度。这意味着除了错误代码之外，函数还应当返回已写入的字节数值。比如，我们可以使用指针参数来传入输出缓冲区长度。解压缩函数的典型原型如下所示：

```
int decompress(const unsigned char *in, size_t in_len, unsigned char *out, size_t *out_len)

```

该函数的前4个参数与`lzo1x_decompress`函数的前4个参数一样。

现在考虑如下UltraVNC代码片段，其中就包含一个严重的堆缓冲区溢出漏洞：

```
void ClientConnection::ReadUltraRect(rfbFramebufferUpdateRectHeader *pfburh) `{`

    UINT numpixels = pfburh-&gt;r.w * pfburh-&gt;r.h;

    UINT numRawBytes = numpixels * m_minPixelBytes;
    UINT numCompBytes;
    lzo_uint new_len;
    rfbZlibHeader hdr;

    // Read in the rfbZlibHeader
    omni_mutex_lock l(m_bitmapdcMutex);
    ReadExact((char *)&amp;hdr, sz_rfbZlibHeader);
    numCompBytes = Swap32IfLE(hdr.nBytes);

    CheckBufferSize(numCompBytes);
    ReadExact(m_netbuf, numCompBytes);
    CheckZlibBufferSize(numRawBytes);
    lzo1x_decompress((BYTE*)m_netbuf,numCompBytes,(BYTE*)m_zlibbuf,&amp;new_len,NULL);
       . . .
`}`
```

如上所示，UltraVNC开发者并没有检查`lzo1x_decompress`的返回代码，然而与另一个漏洞（没有正确使用`new_len`）相比，这个错误并没有那么重要。

未经初始化的`new_len`变量会被传递给`lzo1x_decompress`函数。在调用该函数时，该变量应该等于`m_zlibbuf`缓冲区的长度。此外，在调试`vncviewer.exe`时（该可执行文件提取自[UltraVNC官方网站](https://www.uvnc.com/)提供的发行版），我也找到了该代码能够通过测试的原因。事实证明，由于`new_len`变量未经初始化，因此会包含一个较大的text区段的地址值。因此，远程用户可能会将精心构造的数据作为输入传递给解压缩函数，确保该函数在写入`m_zlibbuf`缓冲区时，会将数据写到缓冲区边界外，导致堆溢出。



## 0x07 总结

在漏洞研究时，我经常会想到一个问题：可能我发现的漏洞太过于简单，导致之前许多人都没注意到这些问题。然而这的确是一个无法改变的事实，有些漏洞历史都比较久远。

此次研究中发现的某些漏洞类别存在于大量开源项目中，即使代码库经过重构，这些漏洞依然存在。有些项目的关联性并不是特别清晰，如果能够系统地识别包含漏洞的这类项目，那么对项目安全性的改进显得尤为重要。

我们分析的这些项目大多都没有经过单元测试，程序也没有使用静态代码分析或者fuzz方式来进行安全性测试。代码中充斥着大量魔术常量，因此会造成“纸牌屋”现象：只要一个常量发生改动，这种不稳定的结构可能就会出现新的漏洞。

从乐观的角度来看，在利用服务端代码时，我们通常都需要通过密码认证，并且服务端可能也不允许用户配置无需密码的认证方法（UltraVNC就采用这种方式）。在防范此类攻击时，客户端不应当连接到未知的VNC服务端，而管理员在配置服务端时，应当使用复杂的强密码。

此次研究获得的部分漏洞编码如下：

1、LibVNC
- [CVE-2018-6307](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-6307)
- [CVE-2018-15126](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-15126)
- [CVE-2018-15127](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-15127)
- [CVE-2018-20019](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20019)
- [CVE-2018-20020](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20020)
- [CVE-2018-20021](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20021)
- [CVE-2018-20022](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20022)
- [CVE-2018-20023](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20023)
- [CVE-2018-20024](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20024)
- [CVE-2019-15681](https://cve.mitre.org/cgi-bin/cvename.cgi?name=2019-15681)
2、TightVNC
- [CVE-2019-8287](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8287)
- [CVE-2019-15678](https://cve.mitre.org/cgi-bin/cvename.cgi?name=2019-15678)
- [CVE-2019-15679](https://cve.mitre.org/cgi-bin/cvename.cgi?name=2019-15679)
- [CVE-2019-15680](https://cve.mitre.org/cgi-bin/cvename.cgi?name=2019-15680)
3、TurboVNC
- [CVE-2019-15683](https://cve.mitre.org/cgi-bin/cvename.cgi?name=2019-15683)
4、UltraVNC
- [CVE-2018-15361](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-15361)
- [CVE-2019-8258](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8258)
- [CVE-2019-8259](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8259)
- [CVE-2019-8260](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8260)
- [CVE-2019-8261](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8261)
- [CVE-2019-8262](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8262)
- [CVE-2019-8263](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8263)
- [CVE-2019-8264](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8264)
- [CVE-2019-8265](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8265)
- [CVE-2019-8266](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8266)
- [CVE-2019-8267](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8267)
- [CVE-2019-8268](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8268)
- [CVE-2019-8269](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8269)
- [CVE-2019-8270](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8270)
- [CVE-2019-8271](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8271)
- [CVE-2019-8272](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8272)
- [CVE-2019-8273](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8273)
- [CVE-2019-8274](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8274)
- [CVE-2019-8275](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8275)
- [CVE-2019-8276](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8276)
- [CVE-2019-8277](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8277)
- [CVE-2019-8280](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8280)