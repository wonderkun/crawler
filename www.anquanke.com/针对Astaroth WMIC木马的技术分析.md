> 原文链接: https://www.anquanke.com//post/id/159610 


# 针对Astaroth WMIC木马的技术分析


                                阅读量   
                                **120051**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：cofense.com
                                <br>原文地址：[https://cofense.com/seeing-resurgence-demonic-astaroth-wmic-trojan/](https://cofense.com/seeing-resurgence-demonic-astaroth-wmic-trojan/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01a6aac3fc5e6e8fdd.jpg)](https://p5.ssl.qhimg.com/t01a6aac3fc5e6e8fdd.jpg)

## 概述

最近，Cofense网络钓鱼防御中心（PDC）监测到Astaroth木马再次活跃。上周，我们的客户共计有数十台资产感染该木马。根据估算，在短短一周内，有约8000台机器可能遭到入侵。<br>
Astaroth木马因其使用撒旦的变量名称（古代传说中的“大公爵”）而得名，自2017年底以来，一直通过伪造的发票钓鱼邮件感染受害用户，大部分发件人使用的是cam.br域名，以此来模拟合法的发件人。<br>
下图为冒充TicketLog的钓鱼邮件：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture1-1.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture1-1.jpg)<br>
此次木马的再次活跃，显然事先做了充足的谋划，将此次攻击的目标放在了南美洲。所有恶意域名都是由Cloudflare托管，并用于将Payload传送到IP地址位于南美洲的主机上。<br>
成功下载Payload的抓包截图：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture2-480x92.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture2-480x92.jpg)Astaroth的原始Payload是恶意.lnk文件，这也是攻击者比较常见的一种传递Payload的方法。恶意.lnk中包含指向URL的链接，受害用户跳转到该链接便能获取下一个Payload。



## 利用现有Windows服务承载恶意软件

Windows Management Instrumentation Console（WMIC）是WMI的命令行界面。WMIC是一个管理Windows主机的优秀工具，受到管理员的广泛青睐。使用get命令，可以以多种方式来检索机器的信息，但是该木马会滥用os get /format:命令，从以.xsl扩展名的非本地资源下载Payload。同时，下载的样式表允许从其中运行经篡改的JavaScript和VBS，这样一来就能够轻松在被感染系统中运行任何类型的恶意软件。Astaroth木马的.lnk文件中包含WMIC.exe的参数，用于指定WMIC以非交互模式运行，这样一来被感染用户就不会看到任何窗口，木马可以悄悄地下载.lnk中的硬编码URL，并自行退出。<br>[![](https://cofense.com/wp-content/uploads/2018/09/Untitled-1-1-768x76.jpg)](https://cofense.com/wp-content/uploads/2018/09/Untitled-1-1-768x76.jpg)<br>
Astaroth从URL中检索包含带有嵌入式JavaScript样式表的.php文件。我们访问该网页，并手动进到view:source即可看到其代码。截至撰写本文时，这部分代码还没有以任何方法进行混淆。<br>
下图为.xsl中的嵌入式JS：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture4-341x480.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture4-341x480.jpg)其中一些变量包含用于文件执行和操作的ActiveX对象，在定义了几个变量之后，该脚本使用一个函数“roll”来生成随机数。<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture5.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture5.jpg)然后，使用生成的随机数，从列表中选择Payload的URL。<br>
域名列表如下：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture6.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture6.jpg)<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture6a.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture6a.jpg)在代码中，经常会重复使用“xVRxastaroth”变量，这一变量可以作为指纹，有助于我们识别该木马。其中，列出的154个域名都托管在CloudFlare上，木马编写者现在大多倾向于借助Google Cloud或CloudFlare等合法托管服务来托管其Payload或C&amp;C基础架构，从而使得安全人员阻止IP的行动变得更加困难。<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture7-480x79.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture7-480x79.jpg)<br>[![](https://cofense.com/wp-content/uploads/2018/09/Screen-Shot-2018-09-07-at-9.16.52-AM-480x179.jpg)](https://cofense.com/wp-content/uploads/2018/09/Screen-Shot-2018-09-07-at-9.16.52-AM-480x179.jpg)在选择域名之后，木马会再次使用WMIC加载到另一个样式表的Payload URL。选择的域名将会以硬编码值的形式存储到/Seu7v130a.xsl?，并在后面附加1111111到9999999之间随机选择的数字。<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture8-480x56.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture8-480x56.jpg)例如：<br>
hxxp://ta4dcmj[.]proxy6x-server[.]website/09//Seu7v130a[.]xsl?3314468[.]xsl<br>
该Payload包含更多嵌入式的JavaScript，并且是恶意软件核心功能的一部分。在这里，重复使用了与原始样式表中声明变量相同的变量，包括用于Payload域名的RNG Roller。在选择Payload URL之后，该脚本将会创建certutil和regsvr32的副本并保存到临时目录中，以备之后使用。<br>
恶意软件产生certutil和regsvr32的副本：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture88-480x136.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture88-480x136.jpg)Certutil.exe（其副本被木马重命名为certis.exe）在Windows环境中通常用于管理证书。但在被感染主机上，第二个样式表借助该可执行文件来下载恶意软件Payload。该脚本创建一个函数，函数使用-urlcache参数和-f、-split选项在temp文件夹中运行复制的certutil。这样一来，可以将获取到的URL保存在文件中。<br>
缓存URL并下载Payload：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture9-480x222.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture9-480x222.jpg)该函数将重复使用，以检索其余的恶意软件Payload。此外，还会执行检查，在继续下一步之前确保已经将每个文件都下载到正确的文件夹中。<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture10-480x146.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture10-480x146.jpg)在下载恶意软件并验证文件后，脚本会在C:Program Files目录下检查是否已经安装Avast防病毒产品，这是全球最流行的防病毒产品之一。<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture11-480x107.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture11-480x107.jpg)如果被感染主机上没有安装Avast，那么脚本将使用regsvr32继续执行最终的.dll，并退出。<br>
如下图所示，木马已经大功告成：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture12-480x144.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture12-480x144.jpg)



## 被感染主机的数据库

在恶意软件成功感染主机后，会生成一个纯文本日志（r1.log）并保存在tempwl目录下。这一日志中包含公网IP、地理位置、计算机名称、计算机受感染的时间以及需要提供给木马开发者的一些字段。<br>
被感染主机的日志如下图所示：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Screen-Shot-2018-09-07-at-9.32.02-AM-480x61.jpg)](https://cofense.com/wp-content/uploads/2018/09/Screen-Shot-2018-09-07-at-9.32.02-AM-480x61.jpg)然后，该信息会被发送到位于第一个Payload URL根目录中的SQLite数据库，如下面的代码段所示。~/9/中有多个打开的目录，如果将数字减少到0，就可以打开其他几个包含可下载的SQLite数据库的目录，这些目录很可能来自之前的木马活动。经过统计，被感染用户高达数千人，一周大约就能感染8000人左右。<br>
目录截图如下：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture14.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture14.jpg)下面为在SQLite Browser中查看的数据库，其中每个字段都经过了Base64编码。<br>[![](https://cofense.com/wp-content/uploads/2018/09/picture15-480x139.jpg)](https://cofense.com/wp-content/uploads/2018/09/picture15-480x139.jpg)解码后，该数据库中的内容包含每台受感染计算机的详细日志。请注意加拿大VPS上托管计算机的第一个条目，与其他南美主机（也就是此次恶意活动的主要针对目标）有所不同。但我们并不能确定，这也可能是木马开发者在测试他们的基础架构。<br>[![](https://cofense.com/wp-content/uploads/2018/09/picture16-880x311.jpg)](https://cofense.com/wp-content/uploads/2018/09/picture16-880x311.jpg)



## 详细分析

Astaroth木马在验证所有核心文件和二进制文件已经运行后，将执行恶意软件Payload。需要注意的是，任何Payload都可以通过滥用WMIC样式表来实现传递，Astaroth支持通过多种方式来传递Payload。然而，根据最近我们监测到的活动，该木马最近一直用于传递键盘记录器。在下载的文件中，伪装的.gif和.jpg文件似乎是恶意软件的依赖项。然而，根据其Magic Byte来看，并不是任何已知的文件类型，并且没有.text或其他PE部分，这就表明它们是不可执行的。然而，其中确实存在函数名称，包括PeekMessageA，这一函数在其他的键盘记录类恶意软件中也曾经发现过。除此之外，还有几个日志文件，以及一个名为vri的文件夹。当恶意软件运行时，该文件夹中也会保存日志。<br>
恶意软件文件列表：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture17-413x480.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture17-413x480.jpg)<br>
伪装成“.jpg”的文件的Magic Byte：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture18.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture18.jpg)函数名称：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture19-480x203.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture19-480x203.jpg)<br>
为了让木马更有针对性，在其他地区运行Astaroth恶意软件的尝试都会失败，具体而言，无法成功下载Payload，并且无法运行.dll文件。我们对其中一个.dll文件进行了简要分析，目前发现它是使用Delphi语言编写而成，其中使用了GetLocaleInfoA函数，以允许木马获取被感染主机的语言环境信息。<br>
以Delphi语言编写：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture20.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture20.jpg)获取语言环境信息：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture21.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture21.jpg)通过更改注册表中HKEY_CURRENT_USER&gt;Control Panel&gt;International项，我们将主机调整为巴西，并启用葡萄牙语键盘，即可解决这一问题。.dll首先在静默模式下使用regsrv32注册并运行，随后会创建启动项，以保证其持久性。<br>
运行.dll的regsvr32：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture22.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture22.jpg)创建启动项保证持久性：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture23-480x310.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture23-480x310.jpg)该恶意软件从regsvr32同时运行2个dll文件，并产生userinit、ctfmon和svchost进程。<br>
新产生的进程如下：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture24-480x86.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture24-480x86.jpg)恶意的svchost使用CLSID dc30c1661-cdaf-11D0-8A3E-00c04fc9e26e不断查询ieframe.dll以及IWebBrowser2接口，这两个组件都是与Internet Explorer交互的关键组件。<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture25-480x468.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture25-480x468.jpg)这一点至关重要，因为恶意软件专门针对Internet Explorer浏览器。为了确保被感染用户能够使用IE，恶意软件将终止其他浏览器的相关进程，例如Chrome和Firefox，并希望被感染用户能觉得这些浏览器出现了故障。当被感染用户使用IE浏览特定的巴西银行网站或商务网站时，恶意软件就会开始记录键盘键入的内容。<br>
下图为键盘记录和外传的数据：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture26-480x111.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture26-480x111.jpg)外传的数据采用Base64编码，经过解码后得到了一系列自定义编码的字符串，这些字符串看起来是以“/”分隔的。这些字符串可能必须要与特定字符串进行异或操作运算，因此解码可能会非常困难。<br>
下图为外传数据：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture27-644x439.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture27-644x439.jpg)下图为自定义编码的字符串：<br>[![](https://cofense.com/wp-content/uploads/2018/09/Picture28-768x313.jpg)](https://cofense.com/wp-content/uploads/2018/09/Picture28-768x313.jpg)



## 总结

Astaroth对于南美的企业来说，存在着较大的威胁。这一木马也向网络管理员提出了一大挑战，对于许多网络管理员来说，他们似乎无法阻止或限制WMIC的使用。<br>
和恶意Office宏一样，要防范这种基于社会工程的攻击形式，最好的方法就是加强用户的安全意识培训。
