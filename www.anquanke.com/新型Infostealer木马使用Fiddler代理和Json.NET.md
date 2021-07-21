> 原文链接: https://www.anquanke.com//post/id/83877 


# 新型Infostealer木马使用Fiddler代理和Json.NET


                                阅读量   
                                **95410**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.zscaler.com/blogs/research/new-infostealer-trojan-uses-fiddler-proxy-jsonnet](https://www.zscaler.com/blogs/research/new-infostealer-trojan-uses-fiddler-proxy-jsonnet)

译文仅供参考，具体内容表达以及含义原文为准

简介

Zscaler ThreatLabZ安全实验室找到了一个用.NET写的新型Infostealer木马,该Infostealer木马病毒利用一些流行的工具比如Fiddler 和 Json.NET来运行 。4月时,这种来自西班牙的Infostealer首次被发现用于攻击美国和墨西哥的用户。

该恶意软件的制作者的目标是墨西哥第二大银行Banamex的用户,但是它其实能够更新配置文件从而威胁到更多的金融机构。

发送机制及安装过程

感染过程开始于一个安装程序,这个安装程序使用双扩展名curp.pdf.exe”,目的是伪装成PDF文档在受害者的机器上安装恶意程序。该恶意软件没有嵌入在其中的PDF文件的图标,因此用户看到的是一个通用的应用程序图标,该文件图标如下图所示:

[![](https://p5.ssl.qhimg.com/t0142f9db7b87986064.png)](https://p5.ssl.qhimg.com/t0142f9db7b87986064.png)

在过去的两周中,我们已经发现的安装程序负载的URL如下:

“cigm[.]co/js/slick/curp.pdf.exe

saysa[.]com.co/js/rfc.pdf.exe

saysa[.]com.co/js/curp.pdf.exe

bestdentalimplants[.]co.in/js/curp.pdf.exe

denticenter[.]com.co/js/slick/curp.pdf.exe

 “

一旦被执行,这些安装程序就会在受害者的机器上执行以下三个部分:
<li>
syswow.exe—— 这是一个窃取银行凭证的主要 Infostealer的有效负载;
</li>
<li>
FiddlerCore3dot5.dll ——.NET应用程序的Fiddler代理引擎 ,这是恶意软件制作者在主要Infostealer功能中需要的相关.NET类库文件;
</li>
<li>
Newtonsoft.Json.dll ——.NET应用程序的开源JSON框架 。这是恶意软件制作者用来从句法上分析指令与控制(C&amp;C)服务器响应数据,并将其转换成XML格式的有关.NET类库文件。
</li>
上述文件下载到Windows系统目录中的代码如下图所示:

[![](https://p0.ssl.qhimg.com/t01fc4a0fdfb6afe0ea.png)](https://p0.ssl.qhimg.com/t01fc4a0fdfb6afe0ea.png)

Infostealer安装程序下载组件

然后,安装程序将执行 Infostealer主程序,并自行终止。

<br>

Infostealer程序分析

首先,该Infostealer程序在受害者的机器上检查FiddlerCore3dot5.dll和Newtonsoft.Json.dll是否存在。如果没有找到这些DLL文件,那么该恶意软件将试图从一个新的位置下载这些硬编码在程序中的文件。一旦确认了这些DLL文件,恶意软件将检查受害者的操作系统版本,如下图所示:

 

[![](https://p5.ssl.qhimg.com/t010f9a8f6bfd11731c.png)](https://p5.ssl.qhimg.com/t010f9a8f6bfd11731c.png)

<br>

 Infostealer检查操作系统版本

对于Windows XP(32位和64位)和Windows Server 2003系统,恶意软件将创建一个能够自启动的注册表密码项,以确保能够在系统中持久地重新启动 。然后,恶意软件会下载一个配置文件,并启动Fiddler代理引擎。

对于其他版本的Windows系统,恶意软件不会创建一个自启动注册表项。然而,为了使Fiddler代理引擎正常工作,恶意软件将在开始启动代理引擎之前先安装一个Fiddler生成的root凭证。

<br>

C&amp;C配置文件

在成功安装后,该Infostealer木马将收集例如“MachineName”, “UserName”, “systeminfo” 和 “hostip””这样的信息,并将其以Base64编码格式发送到远程C&amp;C服务器,如下图所示:

 

[![](https://p4.ssl.qhimg.com/t012cf7e869ca7191c3.png)](https://p4.ssl.qhimg.com/t012cf7e869ca7191c3.png)

<br>

Infostealer发送信息

C&amp;C服务器会响应Infostealer所发送的消息,响应内容是一个配置文件,其中包含指向替换C&amp;C位置以及其他指令的URL列表 。该恶意软件使用Json.NET库来解析服务器响应,并将其以XML的格式保存,文件名为registro.xml 。下面是我们的分析中得到的一个示例配置文件:

 

[![](https://p4.ssl.qhimg.com/t01acc77889babee14d.png)](https://p4.ssl.qhimg.com/t01acc77889babee14d.png)

<br>

Infostealer XML配置文件

该配置文件还包含域到IP元组的一个列表,这主要用于Infostealer木马劫持用户到那些域的请求,并将其重定向到托管目标域的假冒钓鱼网站的恶意服务器上。

该恶意软件初始化了一个计时器组件,该组件每隔10分钟将触发一个RefreshInfo函数调用 。这将导致每隔10分钟就从列表中的下一个URL下载一个新的配置文件。

<br>

Fiddler拦截HTTP和HTTPS流量

有趣的是, 该恶意软件利用Fiddler代理引擎拦截了HTTP / HTTPS连接,并将用户重定向到攻击者所控制的托管虚假网站的服务器上。

如果域名是C&amp;C的配置文件中的目标名单上的,该恶意软件就添加包含攻击者服务器IP地址的X-overrideHost flag,从而实现了他们的目的 。这将导致Fiddler代理引擎解析所提供的IP地址的域名并将受害者引到一个虚假的网站。

被感染的系统中得到的虚假Banamex截图如下图所示:

 

[![](https://p5.ssl.qhimg.com/t01601e674ea8aa164f.png)](https://p5.ssl.qhimg.com/t01601e674ea8aa164f.png)

虚假Banamex银行网址托管在攻击者所控制的服务器上

结论

我们经常看到多个基于.NET的恶意软件程序,但这个特殊的Infostealer木马引起了我们的特别关注,因为这个木马中使用了诸如Fiddler还有Json.NET等流行的应用程序库。

墨西哥第二大银行Banamex,似乎是这个Infostealer木马的凭据盗窃和金融诈骗的主要对象。然而,创造这个木马的人可以很轻松地每隔10分钟就向不停更新的列表中添加更多的目标。 Zscaler的ThreatLabZ实验室已经确认了初始下载和Infostealer程序,确保向使用Zscaler的互联网安全平台的组织提供保护。

IOCs

Infostealer安装程序MD5SUM:

123f4c1d2d3d691c2427aca42289fe85

070ab6aa63e658ff8a56ea05426a71b4

ac6027d316070dc6d2fd3b273162f2ee

98bbc1917613c4a73b1fe35e3ba9a8d9

070ab6aa63e658ff8a56ea05426a71b4

06f3da0adf8a18679d51c6adaa100bd4

123f4c1d2d3d691c2427aca42289fe85

8c9896440fb0c8f2d36aff0382c9c2e4

作者:Deepen Desai, Avinash Kumar
