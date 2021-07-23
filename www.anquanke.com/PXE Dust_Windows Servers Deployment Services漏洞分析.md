> 原文链接: https://www.anquanke.com//post/id/172888 


# PXE Dust：Windows Servers Deployment Services漏洞分析


                                阅读量   
                                **192976**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者checkpoint，文章来源：research.checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/pxe-dust-finding-a-vulnerability-in-windows-servers-deployment-services/](https://research.checkpoint.com/pxe-dust-finding-a-vulnerability-in-windows-servers-deployment-services/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0155d314420fc83508.png)](https://p2.ssl.qhimg.com/t0155d314420fc83508.png)



## 一、前言

许多大型组织会使用Windows Deployment Services（WDS，Windows部署服务）在新主机上安装自定义操作系统。用户可以通过LAN访问Windows Deployment Services，获取相关软件。WDS可以针对每个新的网络单元确定操作系统以及相关的程序及服务。

在这种场景下，如果攻击者可以破坏WDS服务器，修改服务器以便控制每台新主机的内容，然后在主机上部署自己的恶意软件，显然会造成非常严重的后果。

本文分析了我们在WDS架构上的一些研究成果，介绍了我们利用该漏洞的一些探索过程。



## 二、Windows Deployment Services

WDS是微软针对基于网络安装的Windows操作系统提出的一个解决方案。WDS使用了Windows Imaging （WIM）格式的磁盘映像，微软从Windows Server 2008（32位及64位）开始正式引入WDS角色。

WDS是一个复杂的系统，目前我们还没有完全理解其整体架构。在本次研究中，我们主要分析了WDS在新安装环境中的具体行为，因为这种预认证协商过程一直以来都是比较吸引攻击者目光的一种攻击方式。

在部署完整的Windows映像之前，WDS必须提供一些网络启动策略。为了完成该任务，WDS使用了PXE（Preboot eXecution Environment，预引导执行环境）服务器。PXE是Intel创建的一个标准，用来在引导固件中建立一套通用的预引导（pre-boot）服务，最终目标是使客户端能够执行网络引导操作，接收来自网络启动服务器的NBP（Network Boot Program，网络启动程序）。PXE服务器会使用TFTP（Trivial File Transfer Protocol，简单文件传输协议）来传输NBP。

TFTP是基于UDP/IP协议上的一个简单文件传输协议，端口号为69。由于TFTP架构比较简单，代码量也比较小，因此是各种网络启动策略（如BOOTP、BSDP以及PXE）在初始阶段的首选协议。然而，TFTP缺乏FTP协议所具备的许多高级功能，比如无法列出、删除或者重命名文件或目录，也不支持用户认证，该协议只支持读写功能。目前，TFTP已经很少用于互联网传输场景，主要用于LAN使用场景。基于这些因素，我们将研究目标转向这个协议。



## 三、模糊测试

我们首先要做的就是使用[Boofuzz](https://github.com/jtpereyda/boofuzz)来创建一个TFTP dumb fuzzer。

Boofuzz是[Sulley](https://github.com/OpenRCE/sulley)模糊测试框架的继任者，安装起来非常简单，相关文档也非常丰富，并且由于Boofuzz语法简单，因此将相关的RFC转换成[模糊测试脚本](https://github.com/CheckPointSW/Cyber-Research/blob/master/Vulnerability/PXE_Dust/tftp-sulley-fuzzer.py)也不是一件难事。

`Tftp.py`定义了协议语义以及待模糊测试的字段。由于这个fuzzer非常通用，我们可以改造代码以适配任何TFTP的具体实现，我们也鼓励其他研究人员采用这种方式，避免重复造轮子。

当fuzzer在运行时，我们手动逆向了`wdstftp.dll`中服务端实现代码，这两种办法往往能相互补充。



## 四、wdstftp.dll

逆向分析完成后，我们开始检查`CTftp::ParseRequest`中实现的文件读取机制。前面提到过，这种协议并没有实现太多复杂的功能，因此这是个非常好的切入点。

服务端会在`CTftpPacket::ParseRequest`中处理TFTP Read Requests（RRQ，TFTP读取请求）。验证客户端所请求的文件的确存在于PXE根目录中后，服务端会将其读入一个`CTptReadFile::CacheBlock`结构中。

[![](https://p2.ssl.qhimg.com/t01fd4fe7a71e077742.png)](https://p2.ssl.qhimg.com/t01fd4fe7a71e077742.png)

图1. CacheBlock结构

服务端通过一个链表来管理这些`CacheBlocks`，以异步方式调用[ReadFile](https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-readfile)，并将`CTptReadFile::_IOCompletionCallback`设置为回调函数。

[![](https://p4.ssl.qhimg.com/t01ff9af5f8164a2958.png)](https://p4.ssl.qhimg.com/t01ff9af5f8164a2958.png)

图2. ReadFile对应的回调函数

目前为止一切正常。然而，接下来我们注意到一个非常奇怪的行为：似乎`CacheBlocks`链表的大小有限，只有2个节点？

[![](https://p3.ssl.qhimg.com/t0112fe9101229cbad1.png)](https://p3.ssl.qhimg.com/t0112fe9101229cbad1.png)

图3. maxCacheBlocks = 2

在下图中我们可以看到，当cache blocks的数量超过2时，最后一个节点会被删除。

[![](https://p5.ssl.qhimg.com/t01ccfa28d6ee22e5d6.png)](https://p5.ssl.qhimg.com/t01ccfa28d6ee22e5d6.png)

图4. 释放尾部节点

了解TFTP协议的这个特征后，再配合`blksize`和`windowsize`选项的使用，我们应该可以构造一个请求，在收到确认（acknowledgement）数据包前生成两个以上cache blocks。如果一切顺利并且把握好时机，某个cacheblock在被`CTptReadFile::_IOCompletionCallback`回调函数使用前就会被释放掉。

[![](https://p0.ssl.qhimg.com/t01238146df228cd3f2.png)](https://p0.ssl.qhimg.com/t01238146df228cd3f2.png)

图5. windbg中出现异常

可以看到`RAX`现在指向的是已释放的内存，这样我们就在Windows Deployment Services中找到了一个UAC（释放后重用）漏洞。

这个bug看起来非常普通，为什么我们的fuzzer没有找到呢？

原因在于Sulley框架每次只能fuzz一个字段，而我们的请求永远不会延伸到如此深的路径。这对未来fuzzer的开发也有借鉴意义：一方面我们希望构造的报文尽可能有效，不会被解析器拒绝；另一方面，如果报文过于正确，我们可能不会发现潜在的bug。



## 五、利用方法

由于这是一个可远程触发、无需身份认证并且高权限的Windows服务端bug，因此我们可以将其标记为严重漏洞。

通常情况下，在利用UAF漏洞时，我们会去尝试分配一个不同的对象（大小类似）或者处于不同状态的一个类似的对象，然后在两者之间造成某种混乱。

我们检查了进程堆以便寻找能在已释放空间分配对象的方法。

事实证明，WDS使用了若干个堆，并且我们的堆会被`wdstftp.dll`、`wdssrv.dll`以及`wdsmc.dll`共享使用。

虽然`wdstftp.dll`支持某些非常灵活的分配方式（如[TFTP Error](https://tools.ietf.org/html/rfc1350#page-8)报文中的分配方式），但会将ASCII转换为Unicode。

[![](https://p5.ssl.qhimg.com/t019558b96e71bda438.png)](https://p5.ssl.qhimg.com/t019558b96e71bda438.png)

图6. Unicode POC

这对POC来说已经是非常好的利用原语，但为了构造可用的payload，我们还需要dereference某些指针。

`wdssrv.dll`也提供了一个分配原语机制，该dll公开了一个RPC接口，可以用来远程调用WDS服务器所提供的服务。

根据该协议的程序特征以及非常丰富的[官方文档](https://msdn.microsoft.com/en-us/library/dd541214.aspx)，我们似乎很有希望能成功利用漏洞。

在寻找攻击者可控的分配空间时，我们找到了`CRpcHandler::OnRecvRequest`。顾名思义，这个RPC处理程序会先对RPC请求执行初始解析操作，然后再将这些请求插入队列中，以便后续函数处理。不幸的是，后续函数并没有共享我们的堆，因此我们的操作范围仅限于这个处理函数。

为了使用被释放后的内存，我们需要使用相同的堆bucket（size = 0x5c-0x78）。

在这个处理函数中，唯一的分配操作位于`CMemoryBuffer::Initialize`中。

[![](https://p1.ssl.qhimg.com/t013a7b9f663523979d.png)](https://p1.ssl.qhimg.com/t013a7b9f663523979d.png)

图7. RPC分配原语

我们可以使用如下脚本执行成功的分配操作，命中目标bucket。

[![](https://p0.ssl.qhimg.com/t014892d74f19103642.png)](https://p0.ssl.qhimg.com/t014892d74f19103642.png)

图8. RPC POC

然而，显然结构中某些字段（最重要的是`CacheBlocks`的`callbackCtx`指针）会保持不变（没有初始化）。

[![](https://p4.ssl.qhimg.com/t0125a2e2b78053ac67.png)](https://p4.ssl.qhimg.com/t0125a2e2b78053ac67.png)

图9. 使用RPC POC时的内存布局

如果我们进一步扩大PRC payload，由于`CMemoryBuffer::Initialize`中会计算size，因此我们会被分配到错误的bucket中。

我们的思路是判断是否可以使用能够控制的`CacheBlocks`字段来做些改变。

不幸的是，经过进一步逆向分析后，我们发现`CTftpReader`实际上并没有使用这些字段，这不是个好消息。

为了利用这个bug，我们尝试了另一个方法。我们尝试重新利用这个bug，利用该bug使服务器泄露重要的信息。在正常场景中，服务端会在`CacheBlock`上调用`IOCompletionCallback`（`CacheBlock`中包含文件的内容），并将相应内容返回给我们。通过植入“全新的” `CacheBlock`后（`CacheBlock`尚未包含文件内容），我们希望服务端能将新的`CacheBlock`的未初始化内容发送给我们，这样就能构造信息泄露场景。

在这种竞争条件下，经过多次尝试，我们还是会收到部分文件内容，并没有看到未初始化的内存信息。我们猜测如果服务端较为繁忙，需要处理大量的文件读写请求，那么读取我们的TFTP映像速度会更慢，因此可能会提高我们成功的概率。



## 六、总结

WDS是一个非常流行的Windows服务器服务，广泛用于镜像的安装部署。该服务的底层PXE服务器存在一个严重的UAF漏洞，可以被远程触发，有可能会被未经身份认证的攻击者使用。

我们向微软报告了该漏洞，微软为该漏洞分配的编号为CVE-2018-8476，标为严重漏洞，声明Windows Server 2008 SP2以上操作系统可能存在代码执行风险。

由于时间限制，我们没有继续寻找漏洞利用方法，但Check Point Research和微软都认为该漏洞很有可能会被攻击者成功利用。

Check Point IPS解决方案可以防护该威胁：Microsoft Windows Deployment Services TFTP Server Code Execution (CVE-2018-8476)。
