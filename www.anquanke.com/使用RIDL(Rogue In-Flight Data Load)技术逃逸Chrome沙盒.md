
# 使用RIDL(Rogue In-Flight Data Load)技术逃逸Chrome沙盒


                                阅读量   
                                **631933**
                            
                        |
                        
                                                                                                                                    ![](./img/199792/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者googleprojectzero，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2020/02/escaping-chrome-sandbox-with-ridl.html](https://googleprojectzero.blogspot.com/2020/02/escaping-chrome-sandbox-with-ridl.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/199792/t019d3ed86d3bd316b9.jpg)](./img/199792/t019d3ed86d3bd316b9.jpg)



可以利用跨进程内存泄漏的漏洞逃逸Chrome沙箱。在发起此攻击之前，仍然需要攻击者攻击Renderer。为了防止对受影响的CPU进行攻击，请确保您的[微代码](https://zhuanlan.zhihu.com/p/86432216)（microcode）是最新的，并禁用超线程（HT）。

在我的上一个博客文章“[破坏数据流](https://googleprojectzero.blogspot.com/2019/05/trashing-flow-of-data.html)”中，我描述了如何利用Chrome的JavaScript引擎V8中的漏洞在Renderer进程中执行代码。为了使这种利用有效，您通常需要将其与第二个漏洞链接在一起使用，因为Chrome的沙箱会限制您对操作系统的访问，并且网站隔离技术（site-isolation）将不同网站隔离到单独的进程中，以防止您绕过Web平台的限制。

在本文中，我们将研究沙箱，尤其是当从被攻击的Renderer进程中使用RIDL和类似的硬件漏洞时所产生的影响。Chrome的IPC机制Mojo基于消息发送关键数据，泄漏的这些关键数据使我们能够将消息发送到特权接口，并执行Renderer进程不应允许执行的操作。我们将使用它来读取任意本地文件，以及在Windows上的沙箱外部执行.bat文件。在撰写本文时，Apple和Microsoft都在与Chrome安全团队合作积极致力于修复此漏洞，以防止这种攻击。



## 背景

以下是有关Chrome流程模型的简化概述：

[![](./img/199792/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2020/02/25/N65dJbpesh2DCjB.png)

Renderer进程位于单独的沙箱中，并且对内核的访问受到限制，例如，通过Linux上的seccomp过滤器或Windows上的[win32k lockdown](https://googleprojectzero.blogspot.com/2016/11/breaking-chain.html)机制。但是，为了使Renderer进程执行任何有用的操作，它需要与其他进程通信以执行各种操作。例如，要加载图像，将需要使用网络服务来完成加载。

Chrome中用于进程间通信的默认机制称为Mojo，它支持消息/数据管道和共享内存。通常您会使用C++，Java或JavaScript中的高级语言之一。也就是说，您使用自定义接口定义语言（IDL）的方法创建一个接口，Mojo用您选择的语言为您生成存根(stubs)，而您实现 功能。想要看代码是如何实现的，可以查看 [.mojom IDL](https://cs.chromium.org/chromium/src/services/network/public/mojom/url_loader_factory.mojom?l=32&amp;rcl=85c4d882d30b93f615011b036176cd0ce5b791df)，[C++实现](https://cs.chromium.org/chromium/src/services/network/url_loader_factory.h?l=43&amp;rcl=5fa80058135430d5253d4f2912a3bb11c6ecbfa9)，[在Renderer中使用](https://cs.chromium.org/chromium/src/services/network/cors/cors_url_loader.cc?l=513&amp;rcl=5fa80058135430d5253d4f2912a3bb11c6ecbfa9)中的URLLoaderFactory类。

Mojo的一项显著功能是允许您通过现有通道转发IPC端点。该代码在Chrome代码库中得到了广泛使用，即，每当您在.mojom文件中看到pending_receiver或未pending_remote参数时。

[![](./img/199792/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2020/02/25/cfmJxTovQqkLKD4.png)

在幕后，Mojo在进程之间或更具体地在Mojo的节点之间使用特定于平台的消息管道。由于Mojo支持消息发送机制,所以两个节点不需要彼此连接。网络中的一个节点称为代理节点(broker)，该代理节点(broker)需要设置节点通道并执行沙箱所限制的某些操作。

IPC端点本身称为端口（ports）。在上面的URLLoaderFactory示例中，客户端和实现方都由端口标识。在代码中，端口如下所示：

```
class Port : public base::RefCountedThreadSafe&lt;Port&gt; {
 public:
  // [...]
  // The current State of the Port.
  State state;
  // The Node and Port address to which events should be routed FROM this Port.
  // Note that this is NOT necessarily the address of the Port currently sending
  // events TO this Port.
  NodeName peer_node_name;
  PortName peer_port_name;
  // The next available sequence number to use for outgoing user message events
  // originating from this port.
  uint64_t next_sequence_num_to_send;
  // [...]
}
```

上面的peer_node_name 和peer_port_name 都是用于寻址的128位随机整数。如果将消息发送到端口(port)，它将首先将其转发到正确的节点，接收节点将在本地端口映射中查找端口名称，并将消息放入正确的消息队列。

当然，这意味着，如果浏览器进程中存在信息泄漏漏洞，则可以泄漏端口名称，并使用它们将消息注入特权IPC通道。实际上，这在Mojo核心文档的安全性部分中已提到：

> “ […]任何节点只要知道端口和节点名称，就可以将任何消息发送到任何其他节点的任何端口。[…]因此，重要的是不要将端口名称泄漏到不应被授予相应功能的节点中。”

利用泄漏的端口号的的一个很好的例子是[crbug.com/779314](http://crbug.com/779314)通过[@NedWilliamson](https://twitter.com/NedWilliamson)。这是[blob](https://developer.mozilla.org/en-US/docs/Web/API/Blob)实现中的整数溢出，它使您可以在浏览器进程中读取blob结构前面的任意数量的堆内存。该漏洞将大致如下所示：
1. 攻击Renderer进程。
1. 使用Blob 泄漏的堆内存。
1. 在内存中搜索端口（有效状态+ 16个高熵字节）。
<li>使用泄漏的端口将消息注入特权IPC连接。<br>
接下来，我们来看两件事。如何用CPU漏洞替换上面的第2步和第3步，以及如何通过特权IPC连接获得什么样的[原语](https://baike.baidu.com/item/%E5%8E%9F%E8%AF%AD)。</li>


## RIDL

为了通过硬件漏洞利用这种行为，需要找到一个跨进程边界的泄漏内存漏洞。来自[MDS攻击](http://mdsattacks.com/)的 RIDL 似乎是最理想的选择：它使您能够从受影响的CPU上的各种内部缓冲区泄漏数据。有关其工作原理的详细信息，请查看[论文](https://mdsattacks.com/files/ridl.pdf)或[幻灯片](https://mdsattacks.com/slides/slides.html)，因为它们比我能解释的要好得多。

已经发布了[微码（microcode）](https://zhuanlan.zhihu.com/p/86432216)和操作系统更新来解决MDS攻击。但是，如果您阅读了[英特尔对该主题的深入研究](https://software.intel.com/security-software-guidance/insights/deep-dive-intel-analysis-microarchitectural-data-sampling)，您会注意到，缓解措施在切换到特权较低的执行上下文时清除了受影响的缓冲区。如果您的CPU支持超线程，您仍然可以从物理内核上运行的第二个线程中读取泄漏数据。解决此问题的[建议](https://software.intel.com/security-software-guidance/insights/deep-dive-intel-analysis-microarchitectural-data-sampling#SMT-mitigations)是禁用超线程或实现组调度程序。

你可以找到多个从2019年五月的公开的MDS漏洞的POCs在网上[1](https://github.com/pietroborrello/RIDL-and-ZombieLoad),[2](https://github.com/vusec/ridl/),[3](https://github.com/IAIK/ZombieLoad)，这些POCs都具有如下属性：
- 它们总会加载或存储数据。
- 有些要求从L1缓存中清除数据。
- 您可以控制64字节高速缓存行中的索引读取到先前的访问的数据，一个64位的值。
- 速度因漏洞利用的不同会有差异。我看到的最高速度的报告是Brandon Falk的MLPDS [Exploit](https://gamozolabs.github.io/metrology/2019/12/30/load-port-monitor.html#an-mlpds-exploit)达到了228kB/s的。为了进行比较，我的机器上的漏洞利用仅达到25kB/s。
所有变体共享的一个属性是，它们在泄漏的内容上具有概率。尽管[RIDL论文](https://mdsattacks.com/files/ridl.pdf)描述了一些针对特定值的同步原语，但通常需要触发对关键数据的重复访问才能将其完全获取。

我最终使用不同的MDS变体为Chrome编写了两个漏洞，一个针对Xeon Gold 6154上的Linux构建，另一个针对Core i7-7600U上的Windows。我将描述这两种方法，因为它们在实践中最终面临不同的挑战。

### <a class="reference-link" name="%E5%BE%AE%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84%E5%A1%AB%E5%85%85%E7%BC%93%E5%86%B2%E5%8C%BA%E6%95%B0%E6%8D%AE%E9%87%87%E6%A0%B7%EF%BC%88MFBDS%EF%BC%89"></a>微体系结构填充缓冲区数据采样（MFBDS）

我的第一个exploit使用的技术为MFBDS。PoC非常简单：

```
xbegin out            ; start TSX to catch segfault
mov   rax, [0]        ; read from page 0 =&gt; leaks a value from line fill buffer
; the rest will only execute speculatively
and   rax, 0xff       ; mask out one byte
shl   rax, 0xc        ; use as page index
add   rax, 0x13370000 ; add address of probe array
prefetchnta [rax]     ; access into probe array
xend
out: nop
```

此后，您将定时访问指针数组以查看已缓存了哪个索引。<br>
你可以改变[0]中的数值去获取泄露数据。此外，您还希望按照[论文](https://mdsattacks.com/files/ridl.pdf)所述在泄漏值上实现前缀或后缀过滤器。请注意，这只会泄漏不在L1高速缓存中的值，因此您希望有一种方法可以在两次访问之间从高速缓存中擦除关键数据。

对于我的第一个泄漏目标，我选择了一个特权URLLoaderFactory。如上所述，Renderer进程使用URLLoaderFactory来获取网络资源。它将对Renderer进程强制执行同源策略（实际上是相同站点），以确保您不会破坏Web平台的限制。但是，浏览器进程还将URLLoaderFactories用于不同的目的，并且它们具有其他特权。除了忽略同源策略外，还允许它们上传本地文件。因此，如果我们可以泄漏其端口名之一，则可以使用它将/etc/passwd 上传到[https://evil.website。](https://evil.website%E3%80%82)

下一步将触发对特权加载程序的端口名的重复访问。让浏览器进程发出网络请求可能是一种选择，但似乎开销太大。我决定改为在节点中定位端口查找。

```
class COMPONENT_EXPORT(MOJO_CORE_PORTS) Node {
  // [...]
  std::unordered_map&lt;LocalPortName, scoped_refptr&lt;Port&gt;&gt; ports_;
  // [...]
}
```

每个节点都有一个存储[所有本地端口](https://cs.chromium.org/chromium/src/mojo/core/ports/node.h?l=298&amp;rcl=3fa5edd2bbabbc33627dffd5f0d1c99f9e18d109)的hashmap。如果我们将消息发送到不存在的端口，则目标节点将在映射中[查找它](https://cs.chromium.org/chromium/src/mojo/core/ports/node.cc?l=156&amp;rcl=3d901c43e94344919690ef36c843fa58e182ad50)，发现它不存在并丢弃消息。如果我们的端口名与另一个端口名位于同一哈希桶中，它将读取未知端口的完整哈希值以与之进行比较。由于端口名通常与散列存储在同一高速缓存行中，因此这还将端口名本身加载到高速缓存中。MFBDS允许我们泄漏整个缓存行，即使未直接访问值也是如此。

该map在一个新的Chrome实例上以大约700的存储桶大小开始，并且主要随着Renderer进程数量的增加而增长。这使攻击变得不可行，因为我们将不得不对存储桶索引和缓存行偏移量都进行暴力破解（由于对齐，所以四分之一）。但是，我注意到一个代码路径，该路径使您可以使用服务工作者创建大量特权URLLoaderFactories。如果您创建启用了[导航预加载](https://developers.google.com/web/updates/2017/02/navigation-preload)的服务，则每个顶级导航都将创建此类[loader](https://cs.chromium.org/chromium/src/content/browser/service_worker/service_worker_fetch_dispatcher.cc?l=334&amp;rcl=a129610c20b22dd77f65f137d88fc37dd1eb064f)。通过简单地创建多个iframe并在服务器端停止请求，您可以同时使数千个loader保持活动状态，并使暴力破解变得更加容易。

唯一缺少的是从L1缓存中擦除目标值。在实践中，简单地用32KB数据填充我们的消息似乎可以解决问题，因为我认为数据将被加载到受害者的L1缓存中并擦除其他所有内容。<br>
总结完整的利用：
1. 攻击Renderer进程。
1. 在$ NUM_CPU-1进程中以不同的缓存行偏移量运行RIDL漏洞。
1. 安装具导航预加载的服务。
1. 创建许多iframe并暂停其请求。
1. 使用随机端口名称将消息发送到网络进程。
1. 如果我们在存储桶索引上发生冲突，则2.中的过程可能会泄漏端口名称。
<li>假冒消息给URLLoaderFactory类，将本地文件上传到[https://evil.website。](https://evil.website%E3%80%82)
</li>
### <a class="reference-link" name="TSX%E5%BC%82%E6%AD%A5%E4%B8%AD%E6%AD%A2%EF%BC%88TAA%EF%BC%89"></a>TSX异步中止（TAA）

在2019年11月发布了MDS攻击的新变种，并且由于TAA PoC似乎比我的MFBDS攻击要快，因此我决定将其改编为Chrome攻击。此外，VUSec还发布了一项针对[存储操作的漏洞利用程序](https://github.com/vusec/ridl/blob/master/pocs/taa_basic.c)，如果我们能够将关键数据写入到内存中的不同地址，则该漏洞将使我们摆脱缓存刷新要求。如果我们可以触发浏览器将消息发送到特权端口，则应该发生这种情况。在这种情况下，关键数据的端口名称也将以节点名称作为前缀，并且我们可以使用RIDL论文中的技术轻松对其进行过滤。

我还开始寻找更好的原语，发现如果可以与NetworkService进行通信，它将允许我创建一个新的NetworkContext，从而选择存储cookie的sqlite3数据库的文件路径。

为了找出如何触发从浏览器进程到NetworkService的消息，我查看了界面中的IPC方法，以找到一种看起来可以从Renderer进程影响它的方法。NetworkService.OnPeerToPeerConnectionsCountChange引起了我的注意，实际上，每次更新WebRTC连接时都会调用此方法。您只需要创建一个伪造的WebRTC连接，每次将其标记为已连接/断开连接时，都会触发一条新消息给NetworkService。

[![](./img/199792/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2020/02/25/aMElI6LwVrd9xys.png)

一旦从被攻击的Renderer进程中泄漏了端口名称，我们就获得了编写具有完全受控路径的sqlite3数据库的原语。

虽然起初听起来并不是很有用，但是您实际上可以滥用它来获得代码执行。我注意到Windows批处理文件是一种非常宽容的文件格式。如果文件的开头有垃圾数据，它将跳过它直到下一个“rn”，然后从那里执行下一个命令。在我的攻击中，我使用它在用户的自动运行目录中创建一个cookies.bat文件，添加带有“rn”的cookie和其中的命令，它将在下次登录时执行。

最终，该exploit在我的机器上平均运行时间为1-2分钟，并持续不到5分钟。而且我敢肯定，由于我看到微小的变化和不同的技术可以大大提高速度，因此可以大大改善这一点。例如，实际上MLPDS似乎比我使用的变体更快。

Exploit总结：
1. 攻击Renderer进程。
1. 在$ NUM_CPU-1进程中以不同的缓存行偏移量运行RIDL漏洞。
1. 创建伪造的WebRTC连接，并在已连接和已断开连接之间切换。
1. 泄漏NetworkService端口名称。
1. 使用cpathtouserautoruncookies.bat中的cookie文件创建一个新的NetworkContext
1. 插入cookie“rncalc.exern”。
1. 等待下一次登录。


## 摘要

当我开始研究此问题时，我感到惊讶的是，即使漏洞已经公开了一段时间，它仍然可以被利用。如果您阅读了有关该主题的指南，则他们通常会在您的操作系统为最新的情况下谈论如何缓解这些漏洞，并应注意您应禁用超线程以完全保护自己。专注于缓解措施无疑给我一种错误的感觉，那就是漏洞已得到解决，我认为这些文章对于启用超线程的影响可能会更加清楚。

话虽如此，我希望您从这篇文章中收货两件事。首先，信息泄漏错误不仅仅可以绕过ASLR。即使不是依赖关键数据端口名，也可能会有其他有趣的数据泄漏，例如Chrome的UnguessableTokens，Gmail cookie或计算机其他进程中的敏感数据。如果您对如何大规模查找信息泄漏有所了解，Chrome可能是不错的选择。

其次，由于硬件漏洞一听就很难的样子，所以我长时间都不太关注他们。但是，我希望我可以通过此博客文章为您提供有关其影响的另一个观点，以帮助您做出是否应该禁用超线程的决定。关于可以用类似的方式破坏其他软件的方法，还有很多探索的余地，我很乐意看到更多应用硬件错误突破软件安全性边界的示例。



## 参考资料

Chrome Site Isolation 简介<br>[https://zhuanlan.zhihu.com/p/37861033](https://zhuanlan.zhihu.com/p/37861033)

Microcode是什么？它为什么能修正CPU硬件错误？<br>[https://zhuanlan.zhihu.com/p/86432216](https://zhuanlan.zhihu.com/p/86432216)

Mojo<br>[https://zhuanlan.zhihu.com/p/40774312](https://zhuanlan.zhihu.com/p/40774312)
