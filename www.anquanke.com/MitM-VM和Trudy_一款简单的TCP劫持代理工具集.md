> 原文链接: https://www.anquanke.com//post/id/83436 


# MitM-VM和Trudy：一款简单的TCP劫持代理工具集


                                阅读量   
                                **152188**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.praetorian.com/blog/trudy-a-dead-simple-tcp-intercepting-proxy-mitm-vm](https://www.praetorian.com/blog/trudy-a-dead-simple-tcp-intercepting-proxy-mitm-vm)

译文仅供参考，具体内容表达以及含义原文为准

中间人攻击(MitM)指的是,通过各种技术手段将受入侵者控制的一台计算机虚拟放置在网络连接中的两台通信计算机之间,这台计算机就称为“中间人”。在安全评估中,MitM模式能够给安全审计人员提供非常大的帮助。

不幸的是,在某些情况下,想要利用MitM模式来进行安全检测是十分困难的。现在有一些代理从某种程度上来说是可以解决这些问题的,但是这些代理似乎又存在各种各样的问题和漏洞,导致这些工具无法正常的使用。[MitM-VM](https://github.com/praetorian-inc/mitm-vm)和[Trudy](https://github.com/praetorian-inc/trudy)是一套能够在功能上互补的工具集,这套工具集能够解决目前各个代理中所存在的问题。这套工具的安装过程非常的简单,而且功能也非常的强大,它们能够给安全审计人员提供行之有效的解决方案。

为什么要开发这样的一套工具呢?通常情况下,如果需要对嵌入式设备与服务器之间正在使用的自定义二进制协议进行修改,其处理过程是非常麻烦的。因为这不仅会涉及到嗅探合法的通信数据,而且还需要开发人员重新编程来对数据包进行封装。Trudy可以让这一切变得更加的简单和快捷,因为Trudy能够像Burp Suite一样来对TCP通信数据进行解析。

[![](https://p3.ssl.qhimg.com/t013b16a2e7de382224.png)](https://p3.ssl.qhimg.com/t013b16a2e7de382224.png)

**MitM-VM**

MitM-VM是一款[Vagrant](https://www.vagrantup.com/)虚拟机,它可以给我们提供透明代理服务。在此我需要给大家介绍一下Vagrant,Vagrant是一个基于Ruby的工具,用于创建和部署虚拟化开发环境。它使用Oracle的开源VirtualBox虚拟化系统,使用Chef创建自动化虚拟环境。这款虚拟机的安装十分简单,而且在经过了适当的配置之后,它可以处理大多数情况下的代理问题。我给大家举一个简单的例子:在我接触到MitM-VM之前,我习惯使用配置了[tcpdump](http://www.tcpdump.org/)(或者类似软件)的虚拟路由器([OpenWRT](https://openwrt.org/))来对目标设备的通信数据进行监视和分析。在大多数情况下,我都能够完成这部分的操作。但是我在操作过程中也面临着两个主要的问题:首先,与我的笔记本电脑相比,我所使用的路由器硬件性能比较差;其次,我将需要管理两部分硬件设备。在对MitM-VM进行了适当的设置之后,它可以作为一个多硬件的集合来供我使用,而且它也能提供同样的功能。除了硬件数量的减少,更加重要的是,在使用了MitM-VM之后,我将能够使用Debian系统来处理我的通信数据了。(我需要注明的是,我仍然非常喜欢OpenWRT!)

当然了,MitM-VM也安装并配置了其他的一些实用工具,这些工具也能够帮助我们监视或修改通信数据。MitM-VM的使用文档均对这些工具进行了详细介绍,感兴趣的朋友可以阅读使用文档来获取更多的信息。

**Trudy**

Trudy采用Go语言进行开发,它可以配合MitM-VM使用。Trudy是一款透明代理,它适用于所有的TCP通信连接,并且允许开发人员对TCP数据包进行手动编程或修改。Trudy的安装过程非常的简单,而且配置选项也十分精简,它能够适用于绝大多数的特殊情况。

它能够为其所代理的每一条通信链接创建一个双向“管道(pipe)”。你所需要设置代理的设备会与Trudy(但是Trudy不会察觉连接的建立)建立连接,而Trudy会与客户端的目的地址(即服务器)进行连接。这样一来,通信数据就会在这个双向管道中进行传输了。用户可以自己创建相应的Go函数来管理和修改管道中的通信数据。

在为TLS连接设置代理时,Trudy会使用合法证书来架设一个TLS服务器。很明显,你肯定会需要使用这个证书,否则客户端是无法通过认证的。

Trudy的功能就是监视和修使用了非HTTP协议的未知代理设备。如果你想要截取或修改HTTP(S)通信数据,[Burp Suite](https://portswigger.net/burp/)可能是你更好的选择。

**实践出真知**

我们Praetorian的技术人员准备对一款联网的家庭智能设备进行一次安全评估。这款设备在其与网络进行通信的TCP协议上又使用了一层自定义的二进制协议,这也带来了很多安全问题。值得一提的是,该协议头部的信息中包含数据包的长度信息,而且也没有对数据包头进行验证。设备不会对数据包的长度进行检测,而且会在设备对数据包进行正常处理时使用到这个值。介于设备之间的一个活跃中间人可以利用这个漏洞来造成目标设备的缓冲区溢出。在此,我们需要去修改非HTTP协议的通信数据,但修改之后Burp就无法正常工作了。除此之外,我们还要修改数据包中的一些其他信息,但是这将导致netsed无法正常工作。最后,我们还希望最大程度地减少我们在安装和配置过程中所花费的时间,不出所料,[Mallory](https://github.com/intrepidusgroup/mallory)和[Squid](http://wiki.squid-cache.org/Features/SslBump)都无法运行了。但是正如我们所说的,MitM-VM加上Trudy,这些问题都迎刃而解了。

**赶紧动手吧!**

如果你对[MitM-VM](mailto:https://github.com/praetorian-inc/mitm-vm)和[Trudy](https://github.com/praetorian-inc/trudy)感兴趣的话,请移步至相应的Github页面来了解更多有关的信息,Github代码库给大家提供了相应的README文档。在这篇文章中,我已经给大家介绍了有关这两个项目的相关信息,如果大家还有什么不明白的地方,或者说在安装过程中遇到了困难,都可以在Github中留言和提问。除此之外,也欢迎大家直接通过电子邮件来与我进行交流:[mailto:kelby.ludwig@praetorian.com](mailto:kelby.ludwig@praetorian.com)
