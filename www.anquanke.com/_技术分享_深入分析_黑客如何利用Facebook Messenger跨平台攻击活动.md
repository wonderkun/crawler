> 原文链接: https://www.anquanke.com//post/id/86796 


# 【技术分享】深入分析：黑客如何利用Facebook Messenger跨平台攻击活动


                                阅读量   
                                **100205**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：detectify.com
                                <br>原文地址：[https://labs.detectify.com/2017/08/31/dissecting-the-chrome-extension-facebook-malware/](https://labs.detectify.com/2017/08/31/dissecting-the-chrome-extension-facebook-malware/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t012cd1b56233d519a3.jpg)](https://p5.ssl.qhimg.com/t012cd1b56233d519a3.jpg)

****

译者：[紫曦归来](http://bobao.360.cn/member/contribute?uid=2937531371)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

我们经常会使用 Facebook Messenger 与朋友分享有趣的影片或资讯链接，不过最近你要提高警惕了，因为黑客可能正通过这些链接传播恶意软件。日前，卡巴斯基实验室和Detectify实验室的研究人员发现，黑客正利用 Facebook Messenger 进行跨平台攻击活动， 即以目标用户好友身份发送经过处理的视频链接。一旦点击链接，则会根据用户浏览器与操作系统将其重新定向至虚假网站，并诱导用户下载恶意扩展程序，从而自动下载恶意广告软件至用户电脑设备。目前，卡巴斯基实验室针对此威胁进行评估。来自Detectify实验室的Frans Rosé也在对此进行分析研究。因此，卡巴斯基研究员David Jacoby和Detectify的研究员Frans Rosé决定共同撰写此次事件的研究报告。

**<br>**

**传播机制**

Frans Rosé花费了相当长的时间对JavaScript进行分析，并试图弄清楚恶意软件的传播方式。从表面上看，这貌似是一个简单的工作，但实际情况并非如此。这项工作涉及多个步骤，其中就包括确定Javascript的有效载荷。此外，由于是由脚本决定何时发起网络攻击，因此要实时关注攻击者何时发起攻击。

利用Chrome传播的恶意软件不仅仅是传播恶意的网络链接，还会收集和统计受害者的信息。我们尝试将此次恶意软件传播过程进行分解，总结下来主要分为以下几个步骤：

1、受害者从朋友那里收到Facebook Messenger的链接。

[![](https://p0.ssl.qhimg.com/t01d9a2e892a62cfa13.png)](https://p0.ssl.qhimg.com/t01d9a2e892a62cfa13.png)

2、一旦对方点入就会导引到一个Google Doc网页，其中现实的是一个朋友头像照片的虚假的视频播放器。

[![](https://p0.ssl.qhimg.com/t015a1d1132db96e41d.png)](https://p0.ssl.qhimg.com/t015a1d1132db96e41d.png)

3、点击这个链接并使用Chrome浏览器进行观看，就会被复位向至虚假的YouTube网站，同时该网站会诱导受害者从 Google 应用商店下载恶意 Chrome 扩展程序（实际上它是一个**Downloader**）。

[![](https://p5.ssl.qhimg.com/t017e3ff46d9d650629.png)](https://p5.ssl.qhimg.com/t017e3ff46d9d650629.png)

4、一旦安装了这个恶意的Chrome 扩展程序，受害者就会向其线上的朋友继续发送恶意链接。

Chrome 恶意扩展程序传播步骤值得我们深入研究——

**Facebook的消息框**

消息框中的信息包括用户的姓氏、“视频”（Video）一词和随机的emoji表情：

[![](https://p4.ssl.qhimg.com/t01dc7fdb264e35910c.png)](https://p4.ssl.qhimg.com/t01dc7fdb264e35910c.png)

以及使用URL缩短工具创建的链接。

**Google文档共享PDF预览**

点击链接后，用户就会被复位向到docs.google.com上的一个URL。此链接是通过使用共享PDF的预览链接制作的。这一可能性比较大，因为这是通过外部链接在合法的Google域上获取大型受控内容区域的最快方式。

<a></a>PDF本身是使用PHP中的**TCPDF 6.2.13**创建的，然后使用Google Cloud Services上传Google文档。

TCPDF 6.2.13的PHP创建的，然后使用Google Cloud Services上传到Google文档。点击[![](https://p0.ssl.qhimg.com/t013afbcaf3d36e5b40.png)](https://p0.ssl.qhimg.com/t013afbcaf3d36e5b40.png)就会转到一个正在预览的PDF文件的详细信息页面。

生成的链接的共享设置，其中包含一个有趣的细节：

[![](https://p3.ssl.qhimg.com/t01d941d502bf2f1fce.png)](https://p3.ssl.qhimg.com/t01d941d502bf2f1fce.png)

上图中显示“任何人都可以编辑”（Anyone can edit”），这就意味着任何拥有链接的人都可以对其进行编辑。让我们来看看这个链接是如何传播开来的——攻击对所有受害者facebook好友都发送了相同的链接。但任何一个好友改变链接访问权限，就会阻止攻击蔓延到受害者的其它朋友。

另一个有趣的细节是创建文档的用户。对大量的个案进行研究就会发现其中的规律：

[![](https://p2.ssl.qhimg.com/t0129db3a20c88d071a.png)](https://p2.ssl.qhimg.com/t0129db3a20c88d071a.png)

上图所示是发送给四个不同受害者的链接，但其中的三个链接都使用了一个相同的IAM用户名（ID-34234），即便这三个链接使用的是不同的Google Cloud项目创建的。

在黑客发起攻击时，这些发送给受害者的pdf预览页面的URL都不在Google的黑名单之列。

**重新定向**

在点击Google文档链接后，用户将被重新定向，最有可能出现的是指纹识别浏览器。以下我们将重点分析Chrome浏览器。

**Chrome扩展程序重新定向被重新定向至虚假的YouTube网页**

使用Chrome浏览器的用户将被重新定向至虚假的YouTube网页。我们注意到在攻击时使用了几个不同的域。

[![](https://p4.ssl.qhimg.com/t011e2f6a8a05c899c5.png)](https://p4.ssl.qhimg.com/t011e2f6a8a05c899c5.png)

被重新定向的页面还会要求您安装Chrome扩展程序。由于用户可以直接在页面上安装Chrome扩展程序，因此受害者唯一可以执行的操作就是单击“添加扩展名”。一旦受害者点击了“添加扩展名”，黑客的攻击行动就成功了。

**Chrome扩展程序**

这里使用了多种Chrome扩展程序。所有的扩展程序都是新创建的，代码是从名称相似的扩展名中盗来的。这些扩展程序主要是使用**background.js**和**manifest.json**的修改版。

显示进行了更改以控制tabs和所有的URL，并启用对background.js的支持：

[![](https://p4.ssl.qhimg.com/t0176f2b533e7857347.png)](https://p4.ssl.qhimg.com/t0176f2b533e7857347.png)

我们发现的所有Chrome扩展程序中的后台脚本都是模糊的，但基础的脚本如下图所示：

[![](https://p0.ssl.qhimg.com/t0102e8ad6152924660.png)](https://p0.ssl.qhimg.com/t0102e8ad6152924660.png)

**模糊后台脚本**

这个脚本非常值得深入推敲。首先，用户只有从Chrome Webstore上安装了扩展程序，background.js才能获取外部URL；如果使用未打包的从本地安装的扩展程序则不会触发网络攻击。

抓取的URL将包含另一个脚本的引用。这个脚本将使用URL.createObjectURL发送到一个Javascript的Blob对象，然后运行background.js。

Blob对象中新生成的脚本同样是模糊的，如下图所示：

[![](https://p1.ssl.qhimg.com/t01ec1dcebdfd943fb4.png)](https://p1.ssl.qhimg.com/t01ec1dcebdfd943fb4.png)

之后将出现这两种情况：

1、如果tab加载成功，就会为所有tab添加一个听众。

2、标签页面载入后，将向另一URL地址发起请求。如果该响应包含任何内容，将被发回标签页面，同时使用executeScript进行触发。该文件之后将在发出请求的标签页面上运行Javascript，从而及时实现XSS注入。

**获取所有脚本**

进行识别被注入文件的研究时，我注意到攻击者的C&amp;C服务器并非始终有代码返回。我开始猜测，当攻击发起时，攻击者能够控制是否传播攻击，以及是否采取手动或特定手段进行。

为了避免在这里白白坐等，我建立了伪扩展程序来模拟攻击者的行为。当然，我并没有激活相关代码，而是将其保存在本地。

一段时间后，我注意到自己已经获得许多点击量，点击者的终端均立即发回了回应码（back code）：

[![](https://p4.ssl.qhimg.com/t01cb4327f1bb48e97e.png)](https://p4.ssl.qhimg.com/t01cb4327f1bb48e97e.png)

返回的代码没有经过任何混淆处理，能够从中看清具体流程。该代码实际是专门针对Facebook而编写的。

该脚本将执行以下操作：

查看运行的域中是否包含Facebook.com。

提取CSRF凭证以访问Facebook，将其名为“fb_dtsg”。

查看是否已经获取访问凭证（获得访问权限是为了完成Facebook API的身份验证）。

将访问令牌（access token）和用户ID发送给攻击者的外部站点。

[![](https://p1.ssl.qhimg.com/t01ab1130aa1312d48c.png)](https://p1.ssl.qhimg.com/t01ab1130aa1312d48c.png)

确保平台功能已启用（禁用kill-switch）：

创建一个访问令牌。目前Facebook已经弃用了FQL API，Facebook此前一直使用FQL API：

[![](https://p4.ssl.qhimg.com/t0122d4204a14d6a03f.png)](https://p4.ssl.qhimg.com/t0122d4204a14d6a03f.png)

然而攻击者发现，如果目标使用iOS系统中的“Pages Manager”应用程序定制访问凭证，FQL API将继续保持可用。

让我们继续来看最有趣的部分，即这些脚本都干了什么：

**对攻击者点赞Facebook页面的剖析**

该脚本将根据硬编码内容为一个Facebook页面点赞。而攻击者很有可能是通过监控该页面的点赞数量来计算受感染用户的具体数量的。

在该攻击的某一阶段中，我们发现页面中的点赞数量激增，在短短数小时之中，从8900跃升到近32000：

[![](https://p2.ssl.qhimg.com/t01e274985d32755ff5.png)](https://p2.ssl.qhimg.com/t01e274985d32755ff5.png)

[![](https://p1.ssl.qhimg.com/t011e4f25d0bfedad37.png)](https://p1.ssl.qhimg.com/t011e4f25d0bfedad37.png)

同样明显的是，攻击者能够通过C&amp;C服务器中的脚本获取器来控制攻击时间。在攻击过程中，该网页点赞数量的增长速度呈现出巨大差异。

攻击者此外还数次更换了页面，很有可能是因为他们的页面遭到了Facebook封停。

**取得好友列表**

由于攻击者已经获得一个支持**FQL**的访问凭证，他们将能利用过时API取得受害者的朋友列表，并按上线日期进行划分，将一直保持在线的朋友选取出来。

他们通过一次选取50名好友将其打乱，只有当这些好友处于空闲或在线状态时，才开始发动攻击。

接着，他们将通过另一域名生成链接，专门用于接受用户ID信息。这一链接将在Google Docs上创建PDF文件，记录目前受害者的档案资料，再由一个短地址将其发回。

攻击者接收该链接后，会再次随即向所有好友发送信息，并使该链接再次运转。

**<br>**

**有趣的细节**

在前面的攻击中，植入代码的某些部分从未被使用过，或有所遗留。

其中一部分就是在合适条件下向每名好友发送消息的定位功能，在实际攻击中其被换成了随机的emoji表情：

[![](https://p2.ssl.qhimg.com/t0131ad3144d039eba8.png)](https://p2.ssl.qhimg.com/t0131ad3144d039eba8.png)

login.php

攻击者所使用的域中包含了一些文件，使我们猜测类似login.php在内的PHP文件应该存储其中。该文件将同时释放出一个Facebook登录脚本，以及一个硬编码电子邮箱地址：

[![](https://p2.ssl.qhimg.com/t0124d5813a61be1238.png)](https://p2.ssl.qhimg.com/t0124d5813a61be1238.png)

**<br>**

**版本**

我们发现攻击者使用了数种版本的Facebook注入脚本。在攻击的末尾阶段，该脚本仅仅点赞了Facebook页面，却并未发动攻击。另外，用于收集访问凭证的域名也从脚本中移除了。

**<br>**

**登录页**

正如我们所提到，脚本同样列举了你正在使用的浏览器类型。Chrome拓展部分仅对使用Google Chrome的用户有效。如果你使用的是另一种浏览器，相关代码也会执行其它命令。

有趣的是，攻击者虽然对大多数操作系统添加了支持，但我们并未收集到针对Linux操作系统的任何样本。

我们所收集的样本均为恶意广告程序，在受害者打开最后的登陆页时，将被复位向至数个

包含恶意邮件或广告的跟踪域。这也说明了攻击者想要通过点击量或分发恶意邮件或广告进行谋利。

**<br>**

**Safari浏览器**

MD5 (AdobeFlashPlayerInstaller.dmg) = d8bf71b7b524077d2469d9a2524d6d79

MD5 (FlashPlayer.dmg) = cfc58f532b16395e873840b03f173733

MD5 (MPlay.dmg) = 05163f148a01eb28f252de9ce1bd6978

这些均为虚假的Adobe Flash更新，但受害者每次都会关闭不同的网站。为此，攻击者似乎轮流使用了一组域名。

[![](https://p2.ssl.qhimg.com/t0174bf97566d5b6d8d.png)](https://p2.ssl.qhimg.com/t0174bf97566d5b6d8d.png)

[![](https://p2.ssl.qhimg.com/t01ec85e8e9a8b27c8a.png)](https://p2.ssl.qhimg.com/t01ec85e8e9a8b27c8a.png)

**<br>**

**火狐浏览器（Mozilla Firefox）**

MD5 (VideoPlayerSetup_2368681540.exe) = 93df484b00f1a81aeb9ccfdcf2dce481

MD5 (VideoPlayerSetup_3106177604.exe) = de4f41ede202f85c370476b731fb36eb

[![](https://p1.ssl.qhimg.com/t01e41948a6b6762240.png)](https://p1.ssl.qhimg.com/t01e41948a6b6762240.png)

“我感染了这个，我该怎么办？

目前，Google Chrome安全小组已禁用所有恶意扩展程序，但是当攻击者使用恶意软件盗取了你的Facebook个人资料的同时，也盗取了你Facebook账号的访问令牌（access-token）。这个访问令牌可能使有时间限制的，但是它的访问权限非常之大。Facebook账号的访问令牌主要是用于安卓系统的Facebook软件。一旦获得了你的访问令牌，攻击者就可以访问用户的个人资料，不论你是否更改了密码、注销Facebook账户或是关闭了Facebook上的的平台设置。

[![](https://p0.ssl.qhimg.com/t018a26b245cde935f9.png)](https://p0.ssl.qhimg.com/t018a26b245cde935f9.png)

我们目前正在与Facebook就这个问题进行探讨。但目前看来，受害者似乎并没有一个简单的方法废除被攻击者偷走的访问令牌。现在只能祈祷攻击者不要在令牌过期之前做任何事情。

我们强烈建议用户更新杀毒软件。

**<br>**

**结语**

攻击主要依赖现实的社交互动，动态用户内容和合法域名作为中间步骤。上述扩散机制的核心感染点是安装Chrome扩展程序。当你允许扩展过程控制浏览器活动时请格外注意。同时，也要弄清楚目前你的浏览器上运行了哪些扩展程序。如果你使用的是Chrome浏览器，可以在URL中输入chrome://extensions/，以获取正在运行的扩展程序列表。


