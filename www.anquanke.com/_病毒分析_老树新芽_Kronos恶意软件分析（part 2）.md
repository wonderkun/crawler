> 原文链接: https://www.anquanke.com//post/id/86755 


# 【病毒分析】老树新芽：Kronos恶意软件分析（part 2）


                                阅读量   
                                **77615**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：malwarebytes.com
                                <br>原文地址：[https://blog.malwarebytes.com/cybercrime/2017/08/inside-kronos-malware-p2/](https://blog.malwarebytes.com/cybercrime/2017/08/inside-kronos-malware-p2/)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p1.ssl.qhimg.com/t01313736019f1fbafa.jpg)](https://p1.ssl.qhimg.com/t01313736019f1fbafa.jpg)**

****

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

****

在[Kronos分析](https://blog.malwarebytes.com/cybercrime/2017/08/inside-kronos-malware/)的[第一部分](https://blog.malwarebytes.com/cybercrime/2017/08/inside-kronos-malware/)中，我们分析了Kronos恶意软件的安装过程，并详细解释了恶意软件为了保持隐蔽性而使用的各种技巧。现在我们将继续对Kronos的恶意行为进行分析。

<br>

**分析样本**

****

[ede01f7431543c1fef546f8e1d693a85](https://www.hybrid-analysis.com/sample/4dea938fc2ea6e3ffc5706a1e57b2e0f42caecd7ec0f166a141900158584e58b?environmentId=100)-downloader（一个包含恶意代码的word文档）

[2a550956263a22991c34f076f3160b49 ](https://www.hybrid-analysis.com/sample/8389dd850c991127f3b3402dce4201cb693ec0fb7b1e7663fcfa24ef30039851?environmentId=100)-bot恶意程序

特别感谢[@shotgunner101](https://twitter.com/chrisdoman)和[@chrisdoman](https://twitter.com/chrisdoman)分享恶意软件样本。

<br>

**配置和目标**

****

Kronos是一款银行木马，其bot程序需要首先从C&amp;C服务器上下载额外的配置文件，并以加密的形式存储在安装文件夹中。通过分析我们发现，当通过网络发送该配置文件时，它使用CBC模式的AES 加密算法对文件进行加密进行加密，但是当该配置文件存储在磁盘上时，将使用ECB模式的AES加密算法进行加密。从下图我们可以看到，Kronos恶意软件的安装目录是**%APPDATA%/Microsoft**，目录中的文件夹名称被用来表示BotId。而且，该文件夹中存储的文件，可执行文件以及配置文件都具有相同的名称，只是扩展名不同而已：

 [![](https://p1.ssl.qhimg.com/t01a6a379001e99ff97.png)](https://p1.ssl.qhimg.com/t01a6a379001e99ff97.png)

我们将捕获到配置文件进行了解密操作，你可以在如下的github地址上找到该解密文件：

[https://gist.github.com/malwarezone/d6de3d53395849123596f5d9e68fe3a3#file-config-txt](https://gist.github.com/malwarezone/d6de3d53395849123596f5d9e68fe3a3#file-config-txt)

配置文件的格式遵循了Zeus恶意软件中定义的标准，恶意软件在该文件中指定了要在目标网站中注入的外部脚本以及注入位置。下图是一个配置文件的片段：

 [![](https://p3.ssl.qhimg.com/t01e82da58bedbe30cf.png)](https://p3.ssl.qhimg.com/t01e82da58bedbe30cf.png)

上述例子中注入的外部脚本是[figrabber.js](https://gist.github.com/malwarezone/d6de3d53395849123596f5d9e68fe3a3#file-figrabber-js)，该脚本被托管在攻击者的服务器上：

 [![](https://p4.ssl.qhimg.com/t01e1fb17418d73b301.png)](https://p4.ssl.qhimg.com/t01e1fb17418d73b301.png)

该脚本当前的配置主要用来对几家银行实施网络攻击，不过该脚本还被用来窃取Google，Twitter和Facebook等网站的登录凭据。如果用户的机器上感染了Kronos恶意软件，那么配置文件中定义的代码片段会被植入到了合法网站的源代码中，一旦用户打开恶意软件所针对的目标网站，注入到合法网站上的脚本就会开始执行了，具体例子如下图所示：

Facebook的：

 [![](https://p1.ssl.qhimg.com/t0138dd1e32025b392b.png)](https://p1.ssl.qhimg.com/t0138dd1e32025b392b.png)

花旗银行：

 [![](https://p0.ssl.qhimg.com/t01e66b3d9a9814ddeb.png)](https://p0.ssl.qhimg.com/t01e66b3d9a9814ddeb.png)

注入的脚本负责打开额外的窗口，该窗口正在尝试欺骗用户并窃取他/她的个人数据：

 [![](https://p4.ssl.qhimg.com/t01cf174e3b78f3d358.png)](https://p4.ssl.qhimg.com/t01cf174e3b78f3d358.png)

富国银行：

 [![](https://p5.ssl.qhimg.com/t0113ca27dfe7d0b8d3.png)](https://p5.ssl.qhimg.com/t0113ca27dfe7d0b8d3.png)

[![](https://p0.ssl.qhimg.com/t01b5c79c1be9864561.png)](https://p0.ssl.qhimg.com/t01b5c79c1be9864561.png)

图片中的表单是都是恶意软件自定义的，以适应每个页面的主题。但是，其内容对于每个目标都是相同的。总的来说，该恶意软件针对银行的攻击操作并不十分复杂，稍微有些安全意识的用户都会对上述的攻击行为产生怀疑，毕竟该恶意软件试图说服用户输入与银行业务相关的所有个人数据：

 [![](https://p0.ssl.qhimg.com/t018361fe3b8eb8d934.png)](https://p0.ssl.qhimg.com/t018361fe3b8eb8d934.png)

<br>

**Downloader**

****

Kronos恶意软件除了感染浏览器和窃取数据外，它还具有下载功能。在我们的测试中，它下载了一个新的可执行文件，并将其保存在**%TEMP%**目录中，恶意软件的有效载荷存储在与主安装目录相同名称的其他目录中：

 [![](https://p5.ssl.qhimg.com/t01b7d9a50a9df6b381.png)](https://p5.ssl.qhimg.com/t01b7d9a50a9df6b381.png)

已下载的payload

[6f7f79dd2a2bf58ba08d03c64ead5ced ](https://virustotal.com/#/file/e675aac1fbb288eb16c1646a288eb8fe3e2c842f03db772f924b0d7c6b122f15/)-nCBngA.exe

从Kronos C&amp;C下载的payload：

 [![](https://p0.ssl.qhimg.com/t01743ec4dc165ffd3f.png)](https://p0.ssl.qhimg.com/t01743ec4dc165ffd3f.png)

下载的过程中发现payload未加密传输：

 [![](https://p5.ssl.qhimg.com/t01e5b4d6b2044e0888.png)](https://p5.ssl.qhimg.com/t01e5b4d6b2044e0888.png)

在上述案例中，下载的payload只是Kronos恶意软件bot组件的更新程序。但是，同样的功能也可用于获取和部署其他恶意软件系列。

<br>

**命令和控制（C&amp;C）服务器**

****

通过我们的分析发现，Kronos恶意软件在其C&amp;C服务器上使用了[Fast-Flux](https://en.wikipedia.org/wiki/Fast_flux)技术，域名每次都被解析成不同的IP。例如，针对hjbkjbhkjhbkjhl.info这个域名，每次从下面给出的IP地址池中随机选择一个作为域名的IP地址：



```
46.175.146.50
46.172.209.210
47.188.161.114
74.109.250.65
77.122.51.88
77.122.51.88
89.25.31.94
89.185.15.235
91.196.93.112
176.32.5.207
188.25.234.208
109.121.227.191
```

通过对C&amp;C服务器网络通信流量的分析，我们观察到恶意软件每次都通过connect.php这个php文件与C&amp;C服务器进行通信，并附带一个可选参数a：



```
connect.php-初始信标
connect.php?a = 0向C&amp;C发送数据
connect.php?a=1从C&amp;C下载配置文件
```





**C&amp;C管理后台**

****

在网上我们找到了泄漏的C&amp;C管理后台代码，这个发现可以让我们对Kronos恶意软件有更进一步的了解。像大多数恶意软件管理后台一样，Kronos管理后台使用PHP编写，并使用MySQL数据库，涉及到的文件如下图所示：

 [![](https://p5.ssl.qhimg.com/t0127647815e27b6a8c.png)](https://p5.ssl.qhimg.com/t0127647815e27b6a8c.png)

事实证明，bot程序总共有三个命令：

a=0 ：发送抓取的页面内容

a=1 ：获取配置文件

a=2 ：发送记录的窗口

下图是管理后台代码的一个代码片段（具体实现位于connect.php文件中），该php文件负责解析和存储相应命令上传的数据。

＃0命令（a=0）：

 [![](https://p2.ssl.qhimg.com/t012cd3fde2b9a0b69f.png)](https://p2.ssl.qhimg.com/t012cd3fde2b9a0b69f.png)

＃2命令（a=2）：

 [![](https://p5.ssl.qhimg.com/t014b61d689efb17442.png)](https://p5.ssl.qhimg.com/t014b61d689efb17442.png)

＃1命令（a=1）：

 [![](https://p0.ssl.qhimg.com/t01838a93d9936a5d81.png)](https://p0.ssl.qhimg.com/t01838a93d9936a5d81.png)

我们还可以非常清楚地看到C&amp;C服务器使用CBC模式的AES加密算法对配置文件进行加密，且加密密钥是BotId的md5值的前16个字节。

 [![](https://p1.ssl.qhimg.com/t01ab9aaed32944657a.png)](https://p1.ssl.qhimg.com/t01ab9aaed32944657a.png)

然而，AES并不是Kronos所使用的唯一加密算法。其他命令在ECB模式下使用BlowFish加密算法：

＃0命令（a=0）：

 [![](https://p0.ssl.qhimg.com/t01051aa6588fb89df1.png)](https://p0.ssl.qhimg.com/t01051aa6588fb89df1.png)

＃2命令（a=2）：

 [![](https://p3.ssl.qhimg.com/t01af036636dc1571c8.png)](https://p3.ssl.qhimg.com/t01af036636dc1571c8.png)

在所有情况下，都有一个名为UniqueId的变量用作加密算法的密钥。其实，UniqueId变量就是BotId，该变量值在每个POST请求中经过XOR编码后被发送出去。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016f0c11a30ef84b05.png)

你可以在这里找到相应的Python脚本来解码相应的请求和响应：

[https://github.com/hasherezade/malware_analysis/tree/master/kronos](https://github.com/hasherezade/malware_analysis/tree/master/kronos)

Kronos恶意软件还支持插件功能，以扩展其核心功能：

 [![](https://p2.ssl.qhimg.com/t01ed77489f93f2bc6a.png)](https://p2.ssl.qhimg.com/t01ed77489f93f2bc6a.png)

<br>

**解密通信流量**

****

在脚本程序（可以[在这里下载](https://github.com/hasherezade/malware_analysis/tree/master/kronos)）的帮助下，我们可以解密Kronos bot和C&amp;C服务器之间通信的网络流量，具体如下所述：

**1.BotId**

由于BotId被用作加密算法的加密，因此我们首先需要获取BotId变量的值，我们在bot程序发送给其C&amp;C服务器（74字节长）的请求中能够找到它：

 [![](https://p1.ssl.qhimg.com/t0132eb40d3958a14fa.png)](https://p1.ssl.qhimg.com/t0132eb40d3958a14fa.png)

转储请求后，我们可以使用以下脚本对其进行解码：

```
./kronos_beacon_decoder.py --infile dump1.bin
```

解码输出结果中包含了以下两个字段：

1.配置文件的哈希值（如果目前没有配置文件，这部分将填写“X”字符）

2.BotId

例如：

```
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX `{`117BB161-6479-4624-858B-4D2CE81593A2`}`
```

因此，上图中的BotId就是**`{`117BB161-6479-4624-858B-4D2CE81593A2`}`**。

**2.配置**

获取BotId之后，我们可以用它来解密配置文件，配置文件位于a=1请求的响应报文中：

 [![](https://p1.ssl.qhimg.com/t0104a7b40304846fae.png)](https://p1.ssl.qhimg.com/t0104a7b40304846fae.png)

下图是一个请求示例：

 [![](https://p1.ssl.qhimg.com/t0149668a76a48e764e.png)](https://p1.ssl.qhimg.com/t0149668a76a48e764e.png)

在转储响应之后，我们可以使用另一个脚本进行解码，给出BotId作为参数：

```
./kronos_a1_decoder.py --datafile dump2.bin --botid `{`117BB161-6479-4624-858B-4D2CE81593A2`}`
```

解码后的数据已经上传到github上了，详情参考：

[https://gist.github.com/malwarezone/a7fc13d4142da0c6a67b5e575156c720#file-config-txt](https://gist.github.com/malwarezone/a7fc13d4142da0c6a67b5e575156c720#file-config-txt)

**3.发送报告**

有时我们可以在请求中找到Kronos bot报告给C&amp;C服务器的加密数据：

 [![](https://p3.ssl.qhimg.com/t01cc435f422246b8f3.png)](https://p3.ssl.qhimg.com/t01cc435f422246b8f3.png)

下图是加密请求示例：

 [![](https://p1.ssl.qhimg.com/t01cce2b8bdee265b03.png)](https://p1.ssl.qhimg.com/t01cce2b8bdee265b03.png)

在转储请求提数据之后，我们可以使用一个脚本对数据进行解密：

```
./kronos_a02_decoder.py --datafile dump3.bin --botid `{`117BB161-6479-4624-858B-4D2CE81593A2`}`
```

解密后的数据已经上传到github上了，详情参考[https://gist.github.com/malwarezone/a03fa49de475dfbdb7c499ff2bbb3314#file-a0_req-txt](https://gist.github.com/malwarezone/a03fa49de475dfbdb7c499ff2bbb3314#file-a0_req-txt)

<br>

**结论**

****

Kronos 恶意软件的代码质量方面很高，但相较于其他恶意软件，其功能并没有什么“高明”之处。尽管[bot程序在黑市论坛上得到了很好的评价](https://blog.sensecy.com/2014/07/15/two-new-banking-trojans-offered-for-sale-on-the-russian-underground/)，但由于其定价太高，因此在受欢迎程度方面，它总是落后于其他恶意软件。
