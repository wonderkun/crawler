> 原文链接: https://www.anquanke.com//post/id/148660 


# 拆解一个经多层打包的Betabot木马新变种


                                阅读量   
                                **91816**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@woj_ciech/betabot-still-alive-with-multi-stage-packing-fbe8ef211d39](https://medium.com/@woj_ciech/betabot-still-alive-with-multi-stage-packing-fbe8ef211d39)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01afd6666d704ec2ca.jpg)](https://p0.ssl.qhimg.com/t01afd6666d704ec2ca.jpg)

安全研究员Wojciech在上周发表的一篇文章中指出，他在偶然间得到了一个Betabot木马的新变种样本，经过了多层的伪装和隐藏。作为初始向量的恶意Office文档试图利用一个17年前的漏洞。

Betabot可以说是一个多变的木马程序，从银行木马演变成密码窃取者，然后演变成一个僵尸网络，能够传播勒索软件和其他恶意程序。虽然在地下市场上你可能只需要花费大约120美元就可以购买到这款木马，但在2017年初也发现了一个[破解版本](https://www.securityweek.com/cybercriminals-use-cracked-builder-spawn-betabot-variants)。



## Word文档作为初始向量

正如通常发生的那样，文档（PDF、Word、Excel）会是攻击者的切入点，在这种情况下，CVE-2017-11882被用于交付下一阶段的有效载荷。由于这种利用，攻击者可以将OLE对象嵌入到特制的RTF文件中，这允许他在受害者系统上执行命令。在下面，你可以找到嵌入在恶意word文档中的对象。

[![](https://p0.ssl.qhimg.com/t01c103729a5a16bcaa.png)](https://p0.ssl.qhimg.com/t01c103729a5a16bcaa.png)在word文件中嵌入的对象

所有对象都试图伪装成合法的软件（英特尔）来获得用户的信任。

<!-- [if !supportLists]-->l  <!--[endif]-->Inteldriverupd1.sct允许攻击者利用Windows脚本组件创建新对象，用于在之后运行task.bat脚本。 [![](https://p0.ssl.qhimg.com/t0142d512b7066c71c0.png)](https://p0.ssl.qhimg.com/t0142d512b7066c71c0.png)

inteldriverupd1.sct

<!-- [if !supportLists]-->l  <!--[endif]-->Task.bat检查临时目录中“block.txt”文件的存在，如果文件不存在，脚本会创建它。最后它会启动“2nd.bat”并删除自身。 [![](https://p0.ssl.qhimg.com/t01653a8dc4768e6104.png)](https://p0.ssl.qhimg.com/t01653a8dc4768e6104.png)

task.bat

<!-- [if !supportLists]-->l  <!--[endif]-->最后阶段是执行2nd.bat脚本。一开始它会启动主exe文件并杀死文字处理程序（winword.exe）进程。之后，它会从注册表中删除Resiliency目录（对于每个版本）以隐藏它自己的痕迹并阻止文档的恢复。由于MRU（最近使用）功能，下一行很有趣。这些键保留最后打开文档的路径。通过这种方式，攻击者能够知道文件的执行位置，并可以轻易地将decoy.doc复制到临时文件夹。最后两条命令删除其他存在痕迹。 [![](https://p3.ssl.qhimg.com/t019244fca7aa24844e.png)](https://p3.ssl.qhimg.com/t019244fca7aa24844e.png)

2nd.bat

<!-- [if !supportLists]-->l  <!--[endif]-->就如同它的命名一样，“Decoy.doc”被用作诱饵，这意味着该文件将在感染后显示给最终用户。

[![](https://p3.ssl.qhimg.com/t0182c73430737d0779.png)](https://p3.ssl.qhimg.com/t0182c73430737d0779.png)decoy.doc

整个文件权重为1,4 MB。

另外值得一提的是，在执行时，它连接到hxxp://goog[.]com/newbuild/t.php?stats=send&amp;thread=0，稍后会详细介绍这一点。下面展示了一个截图： [![](https://p2.ssl.qhimg.com/t01ae2446e02507dedd.png)](https://p2.ssl.qhimg.com/t01ae2446e02507dedd.png)

在word文件中嵌入的地址

## 第一层

丢弃的文件（exe.exe）是用C＃编写的，并且使用DeepSea算法进行了混淆处理，但是De4dot做得很好，立即对文件进行去混淆处理。

[![](https://p4.ssl.qhimg.com/t01aec01cf9c82e5d6b.png)](https://p4.ssl.qhimg.com/t01aec01cf9c82e5d6b.png) 用de4dot进行去混淆

在这个操作之后，我们可以清楚地看到类和函数的名称，这可以让我们了解它的运作方式。事实证明，这只是第一层的混淆。我们必须确定下一个有效载荷的位置，以及可能的混淆算法，然后将其转储为二进制。 [![](https://p1.ssl.qhimg.com/t0157549d2ec319ccdb.png)](https://p1.ssl.qhimg.com/t0157549d2ec319ccdb.png)

左边是去混淆之前，右边是去混淆之后

## 第二层

函数负责解码，它是简单的xor和modulo操作。现在，我们可以轻松地转储下一个文件。 [![](https://p1.ssl.qhimg.com/t011d9007109a45dd54.png)](https://p1.ssl.qhimg.com/t011d9007109a45dd54.png)

解码算法

一种方法是在“while”操作之后设置断点，并将其变量直接保存到磁盘。也可以将整个项目导入到Visual Studio中，然后调用该函数，但Wojciech决定将此函数重写为python并解码。

“Byte3”和“Byte2”是字节数组的名称。                  

 int0 = len（byte3） – 1

这是如何检索下一个文件的方法，另一种方法可以是调试代码并检查已加载的模块。新文件在执行之前被加载到内存中，因此可以将它从“modules”选项卡转储到DnSpy中。 [![](https://p5.ssl.qhimg.com/t01181ff2ced072d124.png)](https://p5.ssl.qhimg.com/t01181ff2ced072d124.png)

未知的模块

另外有趣的是，在文件的资源中有许多被嵌入的图片。所有图片都包含有噪声像素，其中有一张图片是个例外，它看起来像布加勒斯特电影之夜的合法海报，名称为“Key0”。含有噪声像素的图片将在下一阶段中使用，但这张海报的目的仍然未知。 [![](https://p1.ssl.qhimg.com/t01de83d405fbd122c7.png)](https://p1.ssl.qhimg.com/t01de83d405fbd122c7.png)

在资源中的嵌入的海报

## 第三层

下一个文件也是用.Net编写的，采用的一些技巧使得它更加难以阅读。例如，字符串是用硬编码的密钥加密的。不过，解密它并不困难，因为我们有一个源代码，你可以在代码中的每一个创建的字符串上调用此函数。 [![](https://p2.ssl.qhimg.com/t010476cf2d36f45eba.png)](https://p2.ssl.qhimg.com/t010476cf2d36f45eba.png)

加密的字符串

一些有趣的字符串：

Notify

Software\Microsoft\Windows\CurrentVersion\Run

.exe

InstallUtil.exe

RegAsm.exe

vbc.exe

AppLaunch.exe

svchost.exe

-boot

/c select,

explorer.exe

.lnk

Save

shell32.dll,

conLocation

TargetPath

CreateShortcut

b070b0ef-fb2c-415b-9f41-b32551b5d91f

vmacthlp

vmtools

vboxservice

事实证明，大多数类和函数名称仍然不够易读，不便于分析。Wojciech表示，他没有找到任何自动去混淆这个层的方法，但经过一段时间，他得出了一些结论。

[![](https://p5.ssl.qhimg.com/t01fbd1fd4fba60d9d8.png)](https://p5.ssl.qhimg.com/t01fbd1fd4fba60d9d8.png)第三层的主要功能

文件所做的第一件事是解密另一个文件，并将其与其他与恶意软件配置相关的信息存储在字典中。它创建另一个文件的方式非常有创意，其工作原理如下：

<!-- [if !supportLists]-->l  <!--[endif]-->从资源获取图片（来自前一阶段的含有噪声像素的图片），并将其作为“image”类型存储在数组中；

<!-- [if !supportLists]-->l  <!--[endif]-->将每个图片转换成内存流；

<!-- [if !supportLists]-->l  <!--[endif]-->解密它。；

<!-- [if !supportLists]-->l  <!--[endif]-->将它添加到字典中。 [![](https://p3.ssl.qhimg.com/t01c0cf08185940b813.png)](https://p3.ssl.qhimg.com/t01c0cf08185940b813.png)

配置字典

在执行过程中，它检查字典中的配置（在这个样本中没有打开任何附加功能），并调用相应的函数。例如，如果将值Options.CheckVM设置为false，恶意软件则不会调用负责检查其是否在虚拟环境中运行的功能。

其中一个功能检查进程（vmacthlp、vmtools、vboxservice），如果其中任意一个正在运行，它会自动终止。

在下面我们可以看到它是如何将自己复制到C:users[username]AppDataRoamingMicrosoftWindowsStart MenuPrograms并在之后启动的。 [![](https://p1.ssl.qhimg.com/t0183ffb55b70d5c071.png)](https://p1.ssl.qhimg.com/t0183ffb55b70d5c071.png)



## 第四层——Betabot

在从前面提到的数组中转储文件之后，我们就得到了Betabot变种。目前在野外很多不同版本的Betabot，作为原因之一，很可能是因为破解版本的出现。样本包含一些反调试和反虚拟环境技巧。

首先是检查PEB进程中的BeingDebugged标志。想要绕过它，我们必须将EBX值设置为与EAX中的值相同。关于这项技术的更多信息在[这里](https://www.aldeid.com/wiki/PEB-Process-Environment-Block/BeingDebugged)。

[![](https://p5.ssl.qhimg.com/t019c749bb8c26e9bc8.png)](https://p5.ssl.qhimg.com/t019c749bb8c26e9bc8.png) 它在SYSTEMCurrentControlSet中检查以下键的存在：VboxGuest、VmTools和Vmware.inc。

[![](https://p3.ssl.qhimg.com/t01ee49dff04226a859.png)](https://p3.ssl.qhimg.com/t01ee49dff04226a859.png)检查过程

执行的其余部分与[此处](https://resources.infosecinstitute.com/beta-bot-analysis-part-1/)分析的样本相同。不过，Wojciech在从内存中打开恶意软件时遇到了一些麻烦。在整个文件被完全解压缩之前，Wojciech遇到了堆栈溢出错误，这也许是无法绕过的下一个反调试机制。

在这种情况下，Wojciech决定使用SysAnalyzer之类的自动工具，它可以检测和转储适当的内存部分以供进一步分析。它确实完成了自己的工作，但是header仍然被破坏或加密，因此无法分析文件，但是从字符串中可以推断出一些功能。 [![](https://p1.ssl.qhimg.com/t01dc199b7780d17f7c.png)](https://p1.ssl.qhimg.com/t01dc199b7780d17f7c.png)

转储文件中的字符串

## 网络流量

如前所述，首先连接到的是hxxp://goog[.]com/newbuild/t.php?stats=send&amp;thread=0，在重定向之后，它会分配随机值作为响应。 [![](https://p0.ssl.qhimg.com/t01d7a577ae119d1abd.png)](https://p0.ssl.qhimg.com/t01d7a577ae119d1abd.png)

第一个请求和响应

重定向导致联署服务hxxp://sharesale[.]com，并带有一些跟踪值。 [![](https://p3.ssl.qhimg.com/t015e5acef4f3e041bf.png)](https://p3.ssl.qhimg.com/t015e5acef4f3e041bf.png)

第二个请求和响应

最后，我们登陆到hxxp://shirtbattle[.]com。

Wojciech的猜测是，bot首先会注册自身用于跟踪目的，然后去shirtbattle从联署项目赚取一些额外的钱。

Wojciech还观察到，主要的C2服务器位于hxxp://onedriveservice[.]com上，它不是真正的微软域，它与[其他恶意活动相关联](https://www.malwareurl.com/listing.php?domain=onedriveservice.com)。

也许这项活动已经结束，CnC已经关闭。我们可以更改我们的DNS设置，以充当C＆C服务器。以下是对Betabot标准的要求、随机参数名称和RC4编码。更多关于提取RC4密钥以及如何获取配置的信息在[这里](https://www.sophos.com/en-us/medialibrary/PDFs/technical-papers/BetaBot.pdf?la=en)。

[![](https://p3.ssl.qhimg.com/t01a79cc41e43c22840.png)](https://p3.ssl.qhimg.com/t01a79cc41e43c22840.png) 对Betabot的标准要求

网络流量的准备非常谨慎，一些合法的全球服务可能会因为域名的相似性而显得无辜，类似于goog[.]com和onedriveservice[.]com。



## 结论

有时即使是已知的样本也会因为各种打包、加密或编码方式而带来一些麻烦，这使得我们需要花更多时间来了解它的运作方式以及它可以做什么。



## IOCs

Purchase_order.doc 20FC1511A310ECE324E40381E49F49C2

Decoy.doc B5F34D2752EC82ACA1DD544DA7990448

2nd.bat 76C94647524188152C6488600CC438B0

Exe.exe 13AE5AF773E63F65D5B0748676FCFF75

Mndgrhsz.exe BFDD283E6135AC06284AC8A221990DA9

Multi.exe B01137B556E968582730F9FE4186DE08

Betabot.exe 005551A827C77BCECBA7B65F5B7A95AF

goog.com

onedriveservice.com



审核人：yiwang   编辑：边边
