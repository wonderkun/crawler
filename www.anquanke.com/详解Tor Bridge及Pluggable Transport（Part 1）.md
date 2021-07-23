> 原文链接: https://www.anquanke.com//post/id/194480 


# 详解Tor Bridge及Pluggable Transport（Part 1）


                                阅读量   
                                **1390310**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者fortinet，文章来源：fortinet.com
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/dissecting-tor-bridges-pluggable-transport.html](https://www.fortinet.com/blog/threat-research/dissecting-tor-bridges-pluggable-transport.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01788207b46cbd5cfe.jpg)](https://p1.ssl.qhimg.com/t01788207b46cbd5cfe.jpg)



## 0x00 前言

在西弗吉尼亚州查尔斯顿举行的[SecureWV 2019](https://securewv.org/)网络安全会议上，我和Peixue做了名为“详解Tor Bridge及Pluggable Transport”的[主题演讲](https://fortiguard.com/events/3274/securewv-2019-dissect-tor-bridge-and-pluggable-transport)。这里我们将通过两篇文章与大家分享更多细节，在第一篇文章中，我将介绍如何通过逆向工程找到Tor内置的Bridge（网桥），以及在启用Bridge时Tor浏览器的工作方式。



## 0x01 Tor浏览器及Tor网络

[Tor浏览器](https://www.torproject.org/)是用来提供匿名Internet连接的一款工具，可以通过Tor网络实现多层加密。当用户使用Tor浏览器浏览网站时，真实IP地址会被Tor网络隐藏，因此目的网站永远不知道真实源IP地址。用户可以在Tor网络上自己创建站点，域名后缀为`.onion`。通过这种方式，只有Tor浏览器能够访问该站点，并且没有人知道站点的真实IP地址。这也是勒索软件犯罪分子要求受害者通过Tor浏览器访问`.onion`网站上付款页面的原因之一。Tor项目团队也知道这一点，在项目博客中明确指出“Tor已经被滥用于犯罪场景中”。

Tor浏览器是基于[Mozilla Firefox](https://www.mozilla.org/en-US/firefox/)的一个开源项目，我们可以从官网下载源代码。Tor网络是一个全球overlay网络，由数千个自愿加入的中继节点所组成。该网络有两种中继节点：普通中继节点以及bridge中继节点。普通中继节点可以通过Tor主目录查看，网络传感器可以轻松识别并阻止到普通中继节点的连接。

bridge的信息在Firefox的配置文件中定义，因此我们可以在Tor浏览器的地址栏中输入`about:config`中显示该信息，如图1所示：

[![](https://p3.ssl.qhimg.com/t015935de21ceb783fa.png)](https://p3.ssl.qhimg.com/t015935de21ceb783fa.png)

图1. 在Tor浏览器中显示配置信息

然而，bridge中继节点并没有在Tor主目录中显示，这意味着传感器无法轻松阻止到这类节点的连接。在本文中，我将介绍如何利用Tor浏览器的内置功能来寻找这类bridge及中继节点。

为了在Tor浏览器中使用bridge中继，我们可以采用两种方式。Tor浏览器内置了一些bridge供用户选择。如果内置的bridge无法正常工作，用户可以从Tor网络设置中获取更多bridge。用户可以访问`https://bridges.torproject.org/`，或者向`[bridges@bridges.torproject.org](mailto:bridges@bridges.torproject.org)`发送邮件来获取该信息。



## 0x02 实验环境

我们的实验环境如下所示：
- Windows 7 32-bit SP1
- Tor浏览器8.0
- TorLauncher 0.2.16.3（扩展）
- Torbutton 2.0.6（扩展）
所使用的Tor浏览器版本信息如下：

[![](https://p2.ssl.qhimg.com/t01d55e1b0989c8261e.png)](https://p2.ssl.qhimg.com/t01d55e1b0989c8261e.png)

图2. Tor浏览器版本信息

在分析过程中，Tor浏览器推出了一个新版本（2019年10月22日）：Tor浏览器9.0版，大家可以阅读本文附录了解更多信息。



## 0x03 使用内置Bridge运行Tor浏览器

我分析的Tor浏览器提供了4种bridge：`obfs4`、`fte`、`meek-azure`以及`obfs3`，这些bridge称为“Pluggable Transpoort”（可插拔传输器），具体设置如图3所示：

[![](https://p5.ssl.qhimg.com/t01e2f2cefdfa6d5cdb.png)](https://p5.ssl.qhimg.com/t01e2f2cefdfa6d5cdb.png)

图3. 在Tor网络设置页面选择使用内置bridge

Tor官网强烈推荐使用`Obfs4` Bridge，下文所有分析工作都基于这种bridge开展。当Tor浏览器建立`obfs4`连接时，我分析了通信流量，发现TCP会话由`obfs4proxy.exe`创建，该进程是bridge客户端进程。

使用`obfs4`启动Tor浏览器时的进程依赖情况如图4所示，其中`firefox.ex`启动`tor.exe`，后者随后启动`obfs4proxy.exe`。`obfs4proxy.exe`进程位于`Tor_installation_folder\Browser\TorBrowser\Tor\PluggableTransports`路径中，一开始我认为内置的`obfs4` bridge应该硬编码在`obfs4proxy.exe`进程中。

[![](https://p1.ssl.qhimg.com/t0153e829dc9da74a92.png)](https://p1.ssl.qhimg.com/t0153e829dc9da74a92.png)

图4. 使用`obfs4` bridge的进程树



## 0x04 分析obfs4proxy.exe进程

启动调试器，attach到`obfs4proxy.exe`，然后在`connect` API上设置断点，该API通常用来创建TCP连接。通常情况下，通过逆向工程我们可以通过该API快速找到IP地址及端口。然而当连接到我们创建的`obfs4` bridge时，断点从来没被触发过。进一步分析`obfs4proxy.exe`进程后，我发现该进程实际使用的是来自`mswsock.dll`的另一个API：`MSAFD_ConnectEx`。

[![](https://p4.ssl.qhimg.com/t01e3422c98319a85f0.png)](https://p4.ssl.qhimg.com/t01e3422c98319a85f0.png)

图5. 调用`MSAFD_ConnectEx` API

如图5所示，`obfs4proxy.exe`即将调用`mswsock.MSAFD_ConnectEx()`来与内置`obfs4` bridge建立TCP连接，使用的IP地址及端口为`192.95.36.142:443`。该函数的第二个参数为指向`sockaddr_in`结构变体的一个指针，其中包含待连接的IP地址及端口信息。随后，该函数会调用`WSASend`及`WSARecv`来与`obfs4` bridge通信。大家可能会注意到OllyDbg调试器无法正确识别该API，因为该API不属于`mswsock.dll`的导出函数。在IDA Pro对`mswsock.dll`的分析中，我们可以看到`750A7842`地址处为`MSAFD_ConnectEx()` API。此外，`call dword ptr [ebx]`指令用来调用`obfs4proxy.exe`所需的几乎所有系统API，这也是对抗API分析的一种方式。

根据我的分析，Tor使用的大多数PE文件（exe及dll文件，如`obfs4proxy.exe`）似乎使用`GCC MINGW-64w`编译器变异，该编译器始终使用`mov [esp], …`指令将参数传递给函数（而不是使用`push ...`指令）。不断跟踪从`MSAFD_ConnectEx()`开始的调用栈后，我发现一开始我并没有猜对，内置的IP地址及端口并没有硬编码在`obfs4proxy.exe`中，而是通过本地环回TCP连接来自于`tor.exe`父进程。

[![](https://p5.ssl.qhimg.com/t01dc98b0d8f2d391ce.png)](https://p5.ssl.qhimg.com/t01dc98b0d8f2d391ce.png)

图6. `obfs4proxy.exe`接收某个`obfs4` bridge的IP地址及端口

通常情况下，从`tor.exe`发往`obfs4proxy.exe`的第3个数据包中包含内置`obfs4` bridge二进制格式的IP地址及端口，如图6所示。这是一个Socks5报文，大小为`0xA`字节。`05 01 00 01`为Socks5协议头，其余数据为IP地址及端口信息。该数据包用来指导`obfs4proxy.exe`使用二进制IP地址及端口与bridge建立连接。`obfs4proxy.exe`随后将解析数据包，将二进制的IP地址及端口转化为字符串格式，这里为`154.35.22.13:16815`。



## 0x05 分析Tor.exe

`tor.exe`使用了名为`libevent.dll`的第三方模块，该模块来自于[libevent](https://libevent.org/)库（一个事件通知库），用来驱动Tor执行各种任务。Tor的大多数socket任务（`connect()`、`send()`、`recv()`等）依赖于事件，由`libevent`自动调用。当在`Tor.exe`中跟踪包含bridge IP地址及端口的数据包时，可以在调用栈上下文中看到许多返回地址位于`libevent.dll`模块中。在图7中，`Tor.exe`正在调用`ws2_32.send()` API来发送包含bridge IP地址及端口的数据包，这与图6中收到的数据包类似。

[![](https://p0.ssl.qhimg.com/t0151da57025d48781f.png)](https://p0.ssl.qhimg.com/t0151da57025d48781f.png)

图7. `tor.exe`使用`libevnet`模块将bridge的IP及端口发送到bridge进程

通过不断跟踪`tor.exe`发送的bridge IP地址及端口，我找到了某个地址，该地址用来启动新的事件，配合回调函数来发送bridge的IP地址及端口。如下所示的ASM代码片段为`tor.exe`中调用`libevent.event_new()`的上下文，该函数的第2个参数为socket句柄，第3参数为事件操作（这里为`14H`，代表`EV_WRITE`及`EV_PERSIST`），第4个参数为回调函数（这里为`sub_2833EE`），第5个参数包含bridge的IP地址及端口，当`libevent`调用该函数时就会将地址及端口传递给回调函数（`sub_2833EE`）。

以下ASM代码片段来自于`tor.exe`，其中基址为`00280000h`：

```
[…]   
.text:00281C84                 mov     edx, eax
.text:00281C86                 mov     eax, [ebp+var_2C] ; 
.text:00281C89                 mov     [eax+14h], edx
.text:00281C8C                 mov     eax, [ebp+var_2C] ; 
.text:00281C8F                 mov     ebx, [eax+0Ch]
.text:00281C92                 call    sub_5133E0
.text:00281C97                 mov     edx, eax
.text:00281C99                 mov     eax, [ebp+var_2C] 
.text:00281C9C                 mov     [esp+10h], eax       ; argument for callback function
.text:00281CA0                 mov     [esp+0Ch], offset sub_2833EE    ; the callback function
.text:00281CA8                 mov     [esp+8], 14h  ; #define EV_WRITE 0x04|#define EV_PERSIST 0x10
.text:00281CB0                 mov     [esp+4], ebx       ; socket
.text:00281CB4                 mov     [esp], edx
.text:00281CB7                 call    event_new    ; event_new(event_base, socket, event EV_READ/EV_WRITE, callback_fn, callback_args);
.text:00281CBC                 mov     edx, eax
.text:00281CBE                 mov     eax, [ebp+var_2C] 
.text:00281CC1                 mov     [eax+18h], edx
[…]
```

继续逆向分析`tor.exe`，我发现了一堆`Obfs4` bridge，这些bridge位于`SETCONF`命令的数据结构中，如图8所示：

[![](https://p1.ssl.qhimg.com/t015a78b521c334cd41.png)](https://p1.ssl.qhimg.com/t015a78b521c334cd41.png)

图8. 部分`SETCONF`命令数据

图8为`SETCONF`命令的部分片段，其中`SETCONF`为命令名，位于结构起始处，后面是内置的bridge信息。红框中标出的数据为一个`Obfs4` bridge数据块，也就是bridge配置行。每个bridge节点都必须保存在一条bridge配置行中，这里总共有27个bridge配置行。大家可以看到，`obfs4`类型的bridge以及对应的IP地址及端口采用字符串格式。

bridge信息也没有硬编码在`tor.exe`进程中，现在我们遇到另一个问题：整个`SETCONF`数据源自何处？实际上该数据来自`firefox.exe`收到的某个TCP数据包，该进程是`tor.exe`的父进程。当`tor.exe`启动时，会打开`9151/TCP`控制端口接收来自`firefox.exe`的命令，也会打开`9151/TCP`代理端口。稍后我会介绍`firefox.exe`如何将命令发送给`tor.exe`。

继续分析`tor.exe`，我注意到除了`SETCONF`命令之外，该进程还支持其他命令，如`GETCONF`、`SAVECONF`、`GETINFO`、`AUTHENTICATE`、`LOADCONF`以及`QUIT`等。`tor.exe`有一个函数用来处理这些命令，会根据命令执行不同的代码分支。

`tor.exe`会根据命令执行不同的任务。比如，`SAVECONF`命令告诉`tor.exe`将bridge信息保存到`Tor_installation_folder\Browser\TorBrowser\Tor\Data\torrc`中的某个文件，而`SETCONF`命令告诉`tor.exe`具体的bridge信息，该信息随后会传递给bridge进程，以便创建bridge连接。



## 0x06 在Firefox.exe中寻找内置Bridge

Tor使用许多环回TCP连接来在进程间传递命令，以便执行具体任务。Wireshark从`3.0.1`版开始支持本地环回适配器，因此我们可以使用该工具在环回接口上捕捉通信流量，其中就包括`firefox.exe`通过本地环回接口上的TCP `9151`控制端口向`tor.exe`发送的`SETCONF`数据包。[RawCap](https://www.netresec.com/?page=RawCap)是可以完成相同任务的另一款工具。`firefox.exe`采用一种特殊的方式向`tor.exe`发送命令数据包：每个数据包1个字节。如图9所示，其中有长度为1的许多数据包，重组这些数据包后，我们就可以还原出完整的`SETCONF`命令。

[![](https://p0.ssl.qhimg.com/t013932a84e8fdb69e6.png)](https://p0.ssl.qhimg.com/t013932a84e8fdb69e6.png)

图9. `firefox.exe`发送命令数据包

Firefox浏览器可以通过第三方开发者开发的[extensions](https://addons.mozilla.org/en-US/firefox/)扩展来执行更多功能。由于Tor浏览器基于Mozilla Firefox开发，因此也具备相同的能力。

在9.0版之前，Tor浏览器带有两个扩展：`Torbutton`以及`TorLauncher`。这些扩展位于`Tor_installation_folder\Browser\TorBrowser\Data\Browser\profile.default\extensions`目录中，对应的扩展文件分别为`[torbutton@torproject.org.xpi](mailto:torbutton@torproject.org.xpi)`及`tor-[launcher@torproject.org.xpi](mailto:launcher@torproject.org.xpi)`，如图10所示，这些文件都为Zip归档文件，包含JS文件及模块。

[![](https://p4.ssl.qhimg.com/t01c9b8f98d8e492cd9.png)](https://p4.ssl.qhimg.com/t01c9b8f98d8e492cd9.png)

图10. Tor扩展文件

然而从9.0版开始，Tor浏览器移除了这两个扩展，对应的代码及功能已经集成到Tor浏览器中。如果大家想了解更多细节，可参考本文附录。

`Torbutton`用来设置并显示Tor设置，也可以显示Tor信息（比如“关于Tor”）。我们可以点击Tor浏览器工具栏上的Tor图标来查看（如图3所示）。

`TorLauncher`负责根据`Torbutton`的具体设置来控制Tor进程。

`TorLauncher`在Firefox的`xul.dll`中加载，相关JS代码也会在该模块的上下文中执行。`xul.dll`是Mozilla Firefox的核心模块，也是向`tor.exe`发送命令的实际模块，这些命令包括`SETCONF`（在`network-setting.js`中实现）、`GETCONF`（`tl-protocol.js`）以及`GETINFO`（`tl-protocol.js`、`torbutton.js`）。`xul.dll`模块是一种JS引擎，可以用来解析并执行这些命令对应的JS代码。

现在来看一下当bridge启用时Tor浏览器的内部工作机制。一旦Tor浏览器中启用了bridge，就会执行如下操作：

1、`firefox.exe`加载基本配置、首选定义以及扩展（涉及到`firefox.exe`及`xul.dll`模块）；

2、`TorLauncher`扩展使用命令行中的设置运行`tor.exe`（涉及到`xul.dll`模块）；

3、用户可以使用`Torbutton`随时修改Tor设置（涉及到`xul.dll`模块）；

4、Firefox通过本地环回TCP连接向`tor.exe`发送命令，告诉`tor.exe`如何根据具体设置来工作（涉及到`xul.dll`、`tor.exe`模块）；

5、随后`tor.exe`运行对应的一个bridge进程（`obfs3`及`obfs4`对应`obfs4proxy.exe`，`fte`对应`fteproxy.exe`，`meek-azure`对应`terminateprocess-buffer.exe`），以便创建bridge通信（涉及到`tor.exe`及对应的bridge进程）；

6、`tor.exe`通过本地环回TCP连接与这些bridge进程通信（涉及到`tor.exe`及对应的bridge进程）；

7、bridge进程连接到bridge中继节点（涉及到bridge进程）。

Tor浏览器通过本地环回接口来发送命令，控制Tor客户端的工作模式，然后再接收并解析来自Tor客户端的处理结果。根据我的分析，`obfs4` bridge的所有信息都定义在一些全局命名变量中（也就是Firefox首选项），存放在本地文件中。当`firefox.exe`启动时会初始化这些信息，然后`TorLauncher`会读取首选项，根据对应的名称（取自`xul.dll`）来访问并使用这些信息。

出于安全原因，我在这里隐去了包含所有bridge完整信息的文件名。在我分析的Tor浏览器版本中，包含27个`obfs4` bridge、4个`obfs3` bridge、1个`meek-azure` bridge以及4个`fte` bridge。



## 0x07 Pluggable Transport

在前文分析中，我们提到了4种bridge类型：`obfs4`、`obfs3`、`meek-azure`以及`fte`。这些bridge都称之为[Pluggable Transport](https://2019.www.torproject.org/docs/pluggable-transports.html.en)（可插拔传输，PT），其主要任务就是转换并在客户端及第一跳（Tor中继节点）之间传输流量。因此，使用PT可以让传感器更加难以识别并阻止Tor流量。

`Obfs4`是更强大且更常用的PT。第一跳`Obfs4`节点通常是bridge中继点，并没有在Tor主目录中列出。`Obfs4`混淆器由Yawning Angel开发及维护，这是采用Go语言开发的开源项目，代码托管于[GitHub](https://github.com/Yawning/obfs4)。`Obfs` Bridge之前有多个版本，比如`Obfs2`及`Obfs3`。`Obfs4`与之前版本不大类似，更接近于ScrambleSuit，因为`Obfs4`的概念来自于Philipp Winter的[ScrambleSuit](https://www.cs.kau.se/philwint/scramblesuit/)协议，这也是为什么`Obfs4`客户端进程同样能够承担ScrambleSuit客户端功能的原因所在。

`Obfs4`的所有功能都由`obfs4proxy.exe`提供，后者是适用于Tor用户的`Obfs4`客户端进程。

前面提到过，Tor浏览器基于Firefox浏览器，使用Firefox扩展为用户提供匿名Internet访问服务。一旦Tor浏览器运行，就会启动`firefox.exe`，加载两个Tor扩展（`TorLauncher`及`Torbutton`）。随后，其中一个Tor扩展启动`tor.exe`（Tor客户端进程）。当在“Tor网络设置”中设置Tor浏览器启用`Obfs4` Bridge时，`tor.exe`就会运行`obfs4proxy.exe`。

在下文中，我们将详细介绍这3个组件（`firefox.exe`、`tor.exe`及`obfs4proxy.exe`）的交互过程。



## 0x08 Tor浏览器与Tor客户端通信

`firefox.exe`进程（Tor浏览器）及`tor.exe`（Tor客户端）会通过Tor的TCP端口（监听在本地环回接口）相互通信。

从图4可知，`firefox.exe`会运行`tor.exe`，更具体一点，`tor.exe`由Firefox扩展`TorLauncher`启动，该扩展由`xul.dll`加载并解析。当浏览器调用Windows原生API `ShellExecuteExW()`来运行`tor.exe`时，许多命令行参数会被传递给`tor.exe`。当`firefox.exe`准备启动`tor.exe`时，传递给`tor.exe`的命令行参数如图11所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d6af986af74ae342.png)

图11. `tor.exe`使用的命令行参数

传递给`tor.exe`的参数总共有10个，这里我们将其拆分，逐行分析。在表1中，`...\`是Tor浏览器安装路径的缩写。

[![](https://p4.ssl.qhimg.com/t0171baa6a2b2318a10.png)](https://p4.ssl.qhimg.com/t0171baa6a2b2318a10.png)

表1. `tor.exe`命令行参数中包含2个TCP端口

这里设置了2个端口，如表1中高亮部分文本所示，分别为`+__ControlPort 9151`以及`+__SocksPort "127.0.0.1:9150 IPv6Traffic PreferIPv6 KeepAliveIsolateSOCKSAuth"`。`tor.exe`会在环回接口（`127.0.0.1`）的`9151`及`9150`两个TCP端口上监听，这也是`tor.exe`默认使用的端口号。

用户可以修改这两个端口的默认值，默认值位于几个本地文件中。其中一个本地文件的示例代码如下：

```
// Proxy and proxy security
pref("network.proxy.socks", "127.0.0.1");
pref("network.proxy.socks_port", 9150);
```

TCP端口`9151`是控制端口，用来交换`firefox.exe`及`tor.exe`之间的控制命令及结果。Tor在TCP端口`9150`上提供SOCKS5代理服务，用来在`firefox.exe`及`tor.exe`之间传递SOCKS5数据包。

典型的控制命令如下所示。`firefox.exe`通过TCP端口`9151`将`GETINFO`命令发送给`tor.exe`，请求某些信息，随后`tor.exe`解析命令，通过TCP端口`9151`将结果发送回`firefox.exe`。

```
GETINFO status/bootstrap-phase

250-status/bootstrap-phase=NOTICE BOOTSTRAP PROGRESS=0 TAG=starting SUMMARY="Starting"
250 OK
```

Tor在`127.0.0.1:9150`上提供代理功能，用来在`firefox.exe`及`tor.exe`之间传输普通数据包（未经加密）。WireShark的抓包结果如图12所示，我将其分成两部分：上半部分为Tor SOCKS5握手过程，下半部分传输的数据包。

[![](https://p2.ssl.qhimg.com/t0142a358280c4f0fad.png)](https://p2.ssl.qhimg.com/t0142a358280c4f0fad.png)

图12. Tor通过TCP端口`9150`在`firefox.exe`及`tor.exe`之间传输的SOCKS5代理数据

使用Tor浏览器访问`https://www.google.com`的数据包如图12所示。在握手过程中，`firefox.exe`在SOCKS5报文中告诉`tor.exe`待访问的目的地址为`www.google.com`。握手结束后，`firefox.exe`开始向`tor.exe`发送Google TLS客户端Hello报文，Tor客户端会加密该报文，然后发送回Google TLS服务端Hello报文。随后，`firefox.exe`开始通过TCP端口`9150`向`tor.exe`发送请求报文及接收响应报文。

Tor客户端通过TCP端口`9150`接收数据包，完成SOCKS5握手。随后，客户端接收来自`firefox.exe`的正常报文，然后执行加密操作。经过Tor加密的数据包传递给选定的Tor电路（circuit）中的Tor入口中继节点。最终，Tor出口中继节点解密收到的数据包，还原正常报文，发送到目的服务器（如`www.google.com`）。

在相反路径上，当`tor.exe`从Tor入口中继节点收到加密报文后，会将报文解密获取明文报文，最终`tor.exe`通过TCP端口`9150` 将明文报文发送给`firefox.exe`（如图7所示）。



## 0x09 Tor客户端与Obfs4客户端通信

当Tor客户端（`tor.exe`）从Tor浏览器收到`SETCONF`命令后，就会启动`Obfs4`客户端`obfs4proxy.exe`。`obfs4proxy.exe`会在环回接口上打开一个随机TCP端口，为Tor提供`Obfs4` Bridge服务，通过进程间管道将TCP端口号通知父进程`tor.exe`。

当`obfs4proxy.exe`准备将TCP端口号通知`tor.exe`时，在`WriteFile()` Windows API上设置的断点就会被触发，参考图13中OllyDbg的输出结果。在图13所示的内存数据中，`CMETHOD obfs4 socks5 127.0.0.1:49496`为待发送给Tor客户端的数据，其中就包含TCP端口。我在测试时看到的TCP端口号为`49496`。`WriteFile()`的第1个参数为进程间管道的文件句柄，此时为`00000100`。

[![](https://p4.ssl.qhimg.com/t0158f354de47081334.png)](https://p4.ssl.qhimg.com/t0158f354de47081334.png)

图13. `obfs4proxy.exe`通过进程间管道将TCP端口发送给`tor.exe`

随后，`tor.exe`与该TCP端口建连，以便与`Obfs4`客户端通信。Tor分别将Bridge节点信息发送至该端口，每次发送一个Bridge信息。在图14的TCPView结果中，我们可以看到`tor.exe`如何将bridge信息分别发送给`obfs4proxy.exe`。

[![](https://p5.ssl.qhimg.com/t0143fc411be98eed22.png)](https://p5.ssl.qhimg.com/t0143fc411be98eed22.png)

图14. TCPView显示Tor将Obfs4 bridge信息发送至Obfs4Proxy

以上就是Tor浏览器（`firefox.exe`）与`Obfs4`客户端（`obfs4proxy.exe`）通过Tor客户端（`tor.exe`）的完整通信过程。在下文中，我们将介绍`Obfs4`客户端（`obfs4proxy.exe`）如何与`Obfs4` Bridge建连，以及`Obfs4`如何传输数据包以绕过网络传感器。



## 0x0A 附录

2019年10月份下旬，Tor浏览器发布了9.0版，该版本中移除了两个扩展（`TorLauncher`及`Torbutton`）。在该版本中，Tor浏览器将执行这两个扩展先前的任务。实际上，根据我的分析，我发现新版本并没有移除这两个扩展的代码，而是将代码集成到名为`omin.ja`的Firefox JAR文件中。当Firefox启动时会加载并解析该文件，随后，用户可以依次通过“Options”、“Tor”菜单找到Tor网络设置选项，如图15所示。

[![](https://p4.ssl.qhimg.com/t01349656a00fbf61cb.png)](https://p4.ssl.qhimg.com/t01349656a00fbf61cb.png)

图15. 两个扩展的功能已集成到Tor浏览器中

新版修改并没有影响Tor浏览器的工作机制，因此本文针对8.0版的分析结论依然有效。
