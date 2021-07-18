
# 【技术分享】使用Web流量代理的GootKit木马变种分析


                                阅读量   
                                **84415**
                            
                        |
                        
                                                                                                                                    ![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securityintelligence.com
                                <br>原文地址：[https://securityintelligence.com/gootkit-developers-dress-it-up-with-web-traffic-proxy](https://securityintelligence.com/gootkit-developers-dress-it-up-with-web-traffic-proxy)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85655/t01a7248f7e5aaa6aa6.jpg)](./img/85655/t01a7248f7e5aaa6aa6.jpg)**

****

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：190RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**一、前言**

自2014年夏天问世以来，[GootKit木马](https://exchange.xforce.ibmcloud.com/collection/GootKit-Ongoing-Research-Collection-422ab7991b937f35b89923f928b79702)就被人们广泛认为是现今活跃的最复杂的银行木马之一，该木马针对网上银行的消费者和商业账户，主要在英国及欧洲其他地区活动。

本文将对我们于2017年1月在IBM X-Force研究工作中发现的GootKit的最新一个样本（MD5: 60e079ec28d47ef85e93039c21afd19c）进行分析。之所以注意到这个样本，主要是因为我们发现GootKit开发者已经修改了木马架构，并改变了木马在被感染终端的运行方式。

通过对GootKit内部工作的深入研究，我发现它使用了新的网络拦截方法，木马利用自身对网络流量提供代理服务，而不是之前使用的对浏览器进行hook方法。GootKit同时通过hook其他相关API绕过了浏览器的证书验证，使其攻击行为畅通无阻。

<br>

**二、木马架构的革新**

在GootKit最新变种中，我首先注意到的一个变化（也是最重要的变化）就是其最新架构的拓展，在这之前，GootKit主要使用两大模块：

1、加载模块，负责持久化、软件更新、对浏览器及Windows系统进程进行恶意代码注入。

2、主模块，负责恶意软件主要功能。该模块基于node.js引擎研发，与恶意代码绑定。

主模块可以注入到svchost进程中，此时它充当master角色，也可以注入到浏览器进程中，此时充当的是slave角色。充当slave角色时，主模块通过hook系统NtDeviceIoControlFile API函数，拦截通过浏览器的所有网络通信流量。NtDeviceIoControlFile服务是一个设备相关接口，可以扩展应用程序对系统中各种设备的控制。该API提供了对系统输入和输出的一致性视图，同时在指定通信接口条件下，也可以向应用和驱动提供设备相关方法。

2017年以来，在我们收集到的GootKit变种中，这两大功能模块变成了三大功能模块：

1、加载模块，与之前类似。

2、主模块（GootKit开发者称之为node32.dll），用来提供处理恶意软件的主要功能，基于同一个的node.js引擎，主要功能在JavaScript代码中实现。

3、浏览器注入模块，这是GootKit最新变种添加的一个功能模块，负责网络流量拦截以及控制浏览器。

GootKit变种现在使用第三个模块配合主功能模块重定向互联网流量，而不是像之前那样让流量直接通过浏览器。

<br>

**三、部署流程的改动**

GootKit变种对它在受感染终端的感染流程和内在工作流程进行了改动。在本文分析的样本中，GootKit利用某个下载器进行分发下载，通过下载器的持久化技术得到运行机会。

GootKit变种使用Windows注册表中的组策略对象（Group Policy Object，GPO）实现本地持久化目的。组策略可以控制用户的工作环境，GootKit利用此功能实现重启后的运行。大多数金融恶意软件族群会在注册表中设置启动表项，GootKit摒弃了此类方法，以规避自动检测规则（https://securityintelligence.com/gootkit-bobbing-and-weaving-to-avoid-prying-eyes/）。

接下来，GootKit创建一个挂起状态的mstsc.exe进程，将加载模块注入其中。该进程就是远程桌面连接（Remote Desktop Connection，RDC）进程，是远程桌面服务的客户端程序，允许用户远程登陆到开放此服务的互联网计算机。

mstsc进程下一步会启动一个svchost.exe进程，将加载模块注入到svchost中。接下来，主模块会通过svchost进程进行加载。

恶意软件的二进制文件存放在以下注册表中：

```
HKCUSoftwareAppDataLowbinaryImage32_0 to HKCUSoftwareAppDataLowbinaryImage32_7
```

<br>

**四、流量代理机制**

恶意软件启动后，主模块开始利用GootKit的新型模块，在受感染主机上架设代理服务器。

这里用到了GootKit内部node.js引擎实现的两个函数：SpInitializeStandaloneMitm函数以及RandomListenPortBase函数。SpInitializeStandaloneMitm使用JavaScript实现，为终端主机的HTTP及HTTPS流量提供代理服务。

GootKit使用RandomListenPortBase函数为这些流量指定通连端口。HTTP流量路由使用的是80端口，HTTPS流量路由使用的是443端口。至于本地监听端口，通常的选择是1024到5000之间的随机一个端口，在这里GootKit使用的是6000端口。

[![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e36dfcdbb8de4e55.png)

注意上图中最后调用的函数是InitializeCertificateFaker()。

<br>

**五、绕过浏览器的证书验证提示标识**

在受感染终端创建新的浏览器进程后，加载模块会将浏览器模块注入到相应进程中。浏览器模块会依次hook两类API：

1、负责连接创建的网络API：

1）mswsock.dll中的MSAFD_ConnectEx API。mswsock.dll为Winsock的扩展模块，所提供的服务不是Winsock的一部分。

2）mswsock.dll中的WSPConnect API。

2、负责证书验证的API：

1）crypt32.dll中的CertVerifyCertificateChainPolicy API。

2）crypt32.dll中的CertGetCertificateChain API。

这些hook使得GootKit能够通过自身模块重定向互联网流量，并将无效证书中的OS标志替换为有效证书中的标志，从而避免浏览器弹出任何证书错误警报。

<br>

**六、利用GootKit代理进行流量重定向**

当浏览器初始化新连接时，GootKit将连接的IP地址及端口号改为上文提到的地址及端口。GootKit对MSAFD_ConnectEx及WSPConnect进行hook，检查流量类型是否为TCP/IP流量，同时对头部进行检查，以确保sockaddr结构大小为16字节，这也是IPv4地址中非混合结构的最大长度。

[![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e90515d35dd5fb1b.png)

[![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01dc15dcc485dad27d.png)

接下来的过程涉及到终端外部IP地址与本地IP地址的修改转化。GootKit检查sa_family值是否为AF_INET，也就是互联网协议地址格式。

[![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0155ea100c045f00be.png)

GootKit将终端的远程IP地址修改为本地IP地址（127.0.0.1），将前文提到的端口值与原始TCP端口相加作为新的端口值。

[![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c2dfc4476e9c027a.png)

本地TCP监听端口也做了相应修改：

[![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b94ce9bf0158681c.png)

十六进制1770h端口对应的即为十进制的6000端口。

<br>

**七、伪造证书标识**

此时用户到网上银行的流量都会经过GootKit代理，GootKit开发者必须确保浏览器不会弹出SSL错误信息，以免引起受害者怀疑。为了伪造有效证书标识，GootKit木马hook了几个API。

第一个API是CertGetCertificateChain。hook这个API可以确保带有pPolicyStatus参数的PCERT_CHAIN_CONTEXT的返回值每次都会显示一个有效证书信息（将dwUnfoStatus设为0即可）。

[![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0198d489a15ff94492.png)

第二个API是CertVerifyCertificateChainPolicy。GootKit同样将PCERT_CHAIN_POLICY_STATUS的值设为0以显示证书有效。

[![](./img/85655/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0141c92990a2c92294.png)

<br>

**八、总结**

GootKit开发者显然仍在对其进行不断改进，增强其反检测规避技术，提高其在受害主机浏览器上的控制能力。此次GootKit变种所做的功能性改进也与它始终贯彻的的高级技术路线相符。

过去一年里，在IBM X-Force团队捕获的所有攻击中，GootKit是2016年欧洲区活动最频繁的恶意木马，主要针对英国、法国及意大利开展攻击活动。在全球最活跃的金融类恶意软件中，GootKit排名第八。虽然GootKit非常复杂，它始终保持较小的感染和攻击范围，以避免因过度暴露而被重点检测。
