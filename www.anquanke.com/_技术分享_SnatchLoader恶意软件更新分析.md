> 原文链接: https://www.anquanke.com//post/id/87157 


# 【技术分享】SnatchLoader恶意软件更新分析


                                阅读量   
                                **107893**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：arbornetworks.com
                                <br>原文地址：[https://www.arbornetworks.com/blog/asert/snatchloader-reloaded/](https://www.arbornetworks.com/blog/asert/snatchloader-reloaded/)

译文仅供参考，具体内容表达以及含义原文为准

  [![](https://p1.ssl.qhimg.com/t0131f0ece83a95ccfb.jpg)](https://p1.ssl.qhimg.com/t0131f0ece83a95ccfb.jpg)

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**摘要**

****

SnatchLoader是一种“downloader”类型的恶意软件专门用于将恶意软件分发（或加载）到受感染的计算机系统上。 我们在2017年1月左右发现了该恶意软件的网络攻击活动，该攻击活动一直持续了几个月的时间才慢慢消失。最近，我们的研究人员发现该恶意软件又开始发起新一轮的网络攻击活动了，在此次网络攻击活动中我们捕获到了该恶意软件的更新，并发现该恶意软件正被用于加载Ramnit银行特洛伊木马。此外，该恶意软件还使用了一个称为“地理IP阻止”的有趣功能，以使得只有某些地理区域的计算机才会被感染。到目前为止，我们已经能够确定，至少英国和意大利是该恶意软件攻击的目标，但美国，法国和香港目前还不是。



[![](https://p3.ssl.qhimg.com/t01e2b2d7399b11464b.png)](https://p3.ssl.qhimg.com/t01e2b2d7399b11464b.png)

SnatchLoader命令和控制面板的登录页面

<br>

**介绍**

****

几个月前，有一个关于关于垃圾邮件广告的Twitter ，当时是一个未知的“downloader”恶意软件，该恶意软件专门用于将恶意软件分发（或加载）到受感染的计算机系统上。根据我们的分析，该“downloader”恶意软件是“SnatchLoader”恶意软件的更新程序，KernelMode.info论坛在2017年1月期间有对SnatchLoader进行简要讨论的相关帖子的。正如论坛上该帖子所述，尽管没有进行详细的代码比较，但SnatchLoader和H1N1 Loader的恶意软件家族似乎有一些相似之处。除此之外，目前我们还没有看到任何关于SnatchLoader恶意软件的进一步讨论，因此本文我们将对SnatchLoader最新版本更新进行分析。

<br>

**样本**

****

Twitter 中引用的示例在[VirusTotal](https://www.virustotal.com/en/file/41e698c7f1febdb53b9b7eae0f48fd93949602d0631d6f6b7dc0768958f7107a/analysis/68958f7107a/analysis/&amp;usg=ALkJrhg06bcQgCG-)上可以找到。 然而，我们的大多数静态分析工作是在更新版本的“核心DLL”上执行的，该更新程序的最新编译日期为2017-10-04，该DLL在2017年10月11日首次被上传到了[VirusTotal](https://www.virustotal.com/en/file/075420f10a1b4fc7302c5e95e578e8397b93019acc0f7f018dc7453a9266e17e/analysis/)上。

<br>

**Windows API调用**

****

通过我们的分析发现，该恶意软件对Windows API的调用都是在运行时通过函数名哈希的方式进行的，散列算法是ROL和XOR运算的组合，在[GitHub](https://github.com/tildedennis/malware/blob/master/snatch_loader/api_hash.py)上可以找到该散列算法的一个Python代码实现。以下是一些API函数名称及其对应的哈希表：

**RtlZeroMemory** – &gt; 0x6b6c652b

**CreateMutexW** – &gt; 0x43725043

**InternetConnectA** – &gt; 0x1d0c0b3e

<br>

**静态配置**

****

一个静态配置被加密存储在DLL的PE Section中，目前我们已经看到该Section的两个名称：.idata和.xdata .，具体如下图所示：

 [![](https://p4.ssl.qhimg.com/t01942dcdf583ecf021.png)](https://p4.ssl.qhimg.com/t01942dcdf583ecf021.png)

Section的第一个DWORD（上图中的0x99a8）用作密钥生成函数的种子，此功能的Python实现在GitHub上可以找到 ，使用RC4算法和生成的密钥可以解密剩余的数据。解密的配置可以分成两个块：第一个块是XML结构的配置数据，具体如下图所示（为了可读性添加了空格）：

 [![](https://p4.ssl.qhimg.com/t01e1691f705c8ff561.png)](https://p4.ssl.qhimg.com/t01e1691f705c8ff561.png)

SRV是命令和控制（C2）服务器的URL，TIME是回连的轮询间隔（单位时间为分钟），NAME是一个活动标识符（02.10可能意味着10月2日），KEY用于加密回连通信。

第二个配置块是一个RSA证书，用于对下载的数据的执行签名检查。

<br>

**命令与控制**

****

到目前为止，我们观察到的所有C2 URL都是HTTPS的。 但是通过使用调试器，我们可以使用HTTP与服务器进行通信，并以明文方式查看回连的通信网络流量，具体如下图所示：

 [![](https://p1.ssl.qhimg.com/t01300bdcf35b95c03e.png)](https://p1.ssl.qhimg.com/t01300bdcf35b95c03e.png)

恶意软件对POST数据进行了四次加密操作：

1.RC4加密，KEY来源于配置文件

2.Base64编码

3.字符替换

4.使用“ r  n”分隔符把数据拆分成64字节的数据块

有三个字符被替换了，并且它们都是可逆的：

+ 到 –

/ 至 _

. 到 =

响应数据好像也被加密处理了，但并没有经过4次加密处理。

通信分为四种请求类型：

1.获取动态配置

2.发送系统信息

3.命令轮询

4.发送命令结果

<br>

**获取动态配置请求**

****

以下是“获取动态配置”请求的纯文本请求数据：

```
req=0&amp;guid=FCD08AEE3C0E9409&amp;name=02.10&amp;trash=ulbncmamlxwjakbnbmaklvvhamathrgsfrpbsfrfqeqpatisgsfrqbtfrgqfrpbuithtisrctisgsfrqbujtiuistduith
```

各个请求字段的含义分别是：

**req：请求类型**

**guid：bot ID**

**name：来自静态配置的NAME**

**trash： 随机长度的随机字符**

响应如下所示：

```
SUCCESS|&lt;CFG&gt;&lt;SRV&gt;https://lookmans[.]eu/css/order.php|https://vertasikupper[.]eu/css/order.php&lt;/SRV&gt;&lt;TIME&gt;120&lt;/TIME&gt;&lt;NAME&gt;02.10&lt;/NAME&gt;&lt;KEY&gt;547bnw47drtsb78d3&lt;/KEY&gt;&lt;/CFG&gt;|
```

该响应可以分为两个字段：状态字段和数据部分。这里的状态字段是“SUCCESS”，数据部分被封装在“&lt;CFG&gt;块”中，这个配置在代码中称为DYNAMIC配置。

<br>

**发送系统信息请求**

****

第二个回连请求发送一堆系统信息，如下所示：

```
req=1&amp;guid=FCD08AEE3C0E9409&amp;name=02.10&amp;win=9&amp;x64=1&amp;adm=1&amp;det=0&amp;def=0&amp;nat=1&amp;usrn=SYSTEM&amp;cmpn=JOHN-PC&amp;uagn=Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)&amp;sftl=AddressBook|Connection Manager|DirectDrawEx|Fontcore|IE40|IE4Data|IE5BAKEX|IEData|MobileOptionPack|SchedulingAgent|WIC|&amp;prcl=[System Process]rnSystemrnsmss.exerncsrss.exernwininit.exerncsrss.exernwinlogon.exernservices.exernlsass.exernlsm.exernsvchost.exernVBoxService.exernsvchost.exernsvchost.exernsvchost.exernsvchost.exernaudiodg.exernsvchost.exernsvchost.exernspoolsv.exernsvchost.exerntaskhost.exernsvchost.exerndwm.exernexplorer.exernVBoxTray.exernSearchIndexer.exernwmpnetwk.exernsvchost.exernsppsvc.exernsvchost.exernmscorsvw.exernmscorsvw.exernSearchProtocolHost.exernmsiexec.exernsvchost.exernTrustedInstaller.exerntaskhost.exernSearchFilterHost.exernmsiexec.exerndllhost.exerndllhost.exernmsiexec.exernsvchost.exern&amp;trash=ilnyyiittddnoyyiblambllvwgblalakjvufynamblcmambllwugxlwkwjvurn
```

各个请求字段的含义分别是：

req – 请求类型

guid – bot ID

name – 来自配置的NAME

win – Windows版本

x64 – 是64位架构

adm – 是管理员

det – 与反分析相关

def – 检测反分析过程名称

nat – 具有RFC1918 IP地址

usrn – 用户名

cmpn – 电脑名称

uagn – 用户代理

sftl – 从注册表中的Uninstall 键值中列举软件

prcl – 进程列表

垃圾 – 随机长度的随机字符

**响应如下所示：**

SUCCESS|

**命令轮询请求**

除了请求号是2之外，命令轮询请求看起来类似于“获取动态配置”请求，一个示例响应如下所示：

  SUCCESS | &lt;TASK&gt; 20 | 1 | 2 || MZ …  X00  X00 &lt;/ TASK&gt; | 

该响应具有两个字段，第一个字段是状态字段，第二个字段是数据部分。这里的数据可以是零个或多个以下字段的TASK块：

**任务ID**

命令类型

命令arg1（例如文件类型）

命令arg2（例如哈希值）

命令数据（例如可执行文件或URL）

SnatchLoader的主要功能是下载并加载其他恶意软件系列，因此大多数命令类型和参数都支持以各种方式执行。在这个例子中，命令是首先提取嵌入的可执行文件然后执行提取到的可执行文件。其他一些支持的命令是：

插件功能

更新配置

更新程序

发送命令结果

最后一个回连类型用于发送命令的结果：

```
req=3&amp;guid=FCD08AEE3C0E9409&amp;name=02.10&amp;results=&amp;trash=pffebxmawlawigdawkifcymbxmawlgebxlawkifcymbxmhebymbxlawkifcy
```

除了请求号是3之外，该请求类似于“命令轮询”的请求，并且添加了一个附加参数（results）。 对于此请求，C2没有任何的响应内容。

<br>

**地理阻止和当前有效载荷**

****

到目前为止，我们发现了该C2服务器的一个有趣的特征，它们似乎正在基于源IP地址执行某种地理阻塞操作。当我们尝试通过美国，法国或香港的TOR或VPN节点与C2服务器进行互动时，服务器会响应“404 Not found”错误。但是，如果我们尝试使用英国和意大利的VPN节点，C2服务器则会对请求进行回应。一般来说，地理阻挡不是一个新的特征，但并不是特别常见的。

在撰写本文时，SnatchLoader僵尸网络正在分发Ramnit恶意软件（一个银行恶意软件），该银行恶意软件的编译日期为2017年10月13日，该样本可在[VirusTotal上](https://www.virustotal.com/en/file/789c129a7d5815d81e324a065a8a50091b25f6e9d9f24d4a34cd2f0e2abdaa8d/analysis/)获得 。

<br>

**结论**

****

在这篇文章里，我们对SnatchLoader下载器恶意软件进行了研究和分析，该恶意软件最早我们可以追溯到2017年1月，并且在上周我们发现了该恶意软件的更新。目前，该恶意软件正在通过垃圾邮件广告进行传播，并根据地理位置封锁功能对某些特定的地理区域发起网络攻击。在撰写本文时，SnatchLoader正在将Ramnit恶意软件在英国和意大利这两个国家内进行传播。
