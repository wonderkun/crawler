> 原文链接: https://www.anquanke.com//post/id/167568 


# MuddyWater感染链剖析


                                阅读量   
                                **375233**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者yore，文章来源：blog.yoroi.company
                                <br>原文地址：[https://blog.yoroi.company/research/dissecting-the-muddywater-infection-chain/](https://blog.yoroi.company/research/dissecting-the-muddywater-infection-chain/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/dm/1024_683_/t016634cf10300e97b2.gif)](https://p1.ssl.qhimg.com/dm/1024_683_/t016634cf10300e97b2.gif)



## 一、前言

在11月末，我们发现有关MuddyWater（污水，APT组织）的新一轮攻击，其攻击目标是中东相关国家。该组织是在2017年被[Unit42](https://researchcenter.paloaltonetworks.com/2017/11/unit42-muddying-the-water-targeted-attacks-in-the-middle-east/)的研究人员首次披露，在很长的一段时间里，MuddyWater（污水，APT组织）的TTP基本不变：他们通过鱼叉式网络钓鱼的手段进行传播，电子邮件中包含模糊的邮件附件，他们会诱使收件人打开附件并启用宏来运行，然后通过POWERSTAT（该程序是MuddyWater组织使用的基于powershell的第一阶段后门）恶意程序感染收件人主机。下图是恶意文档实例。

[![](https://p5.ssl.qhimg.com/dm/1024_452_/t0141cccdc9615428d1.png)](https://p5.ssl.qhimg.com/dm/1024_452_/t0141cccdc9615428d1.png)

根据ClearSky研究小组和TrendMicro研究人员的分析，在11月底，MuddyWater（污水，APT组织）组织先后攻击了土耳其，黎巴嫩和阿曼的相关机构，其采用的手段和释放的载荷相同，都是利用文档中的宏和POWERSTAT后门进行攻击。



## 二、技术分析

当受害者启用文档中的宏并执行时，恶意代码会创建一个Excel文档，该文档包含一段代码，这段代码的功能是下载下一阶段所需的恶意载荷，同时，会弹出一个错误窗口，并显示“office版本不兼容”，如下图所示。

[![](https://p3.ssl.qhimg.com/t01886f504a450dbea3.png)](https://p3.ssl.qhimg.com/t01886f504a450dbea3.png)

恶意代码会开启一个用户例程来解密被加密的宏代码。如下图所示：

[![](https://p2.ssl.qhimg.com/t013b7cdf9554436eb8.png)](https://p2.ssl.qhimg.com/t013b7cdf9554436eb8.png)

下图所示为解密后的代码，代码中的“x1”变量代表一个函数，该函数功能是创建一个隐藏的Excel文档。

[![](https://p1.ssl.qhimg.com/dm/1024_312_/t01d4738e3dc8c6b1e4.png)](https://p1.ssl.qhimg.com/dm/1024_312_/t01d4738e3dc8c6b1e4.png)

创建出来的Excel文档也包含宏，该宏执行后，会连接指定URL并下载powershell代码，该URL指向了一个图片链接：”[http://pazazta[.]com/app/icon.png](http://pazazta%5B.%5Dcom/app/icon.png)“

该powershell会创建3个本地文件。其存放的路径如下：

1.C:\Windows\Temp\temp.jpg（该文件包含一段Javascript代码）<br>
2.C:\Windows\Temp\Windows.vbe（该文件包含一段被编码后的VB脚本）<br>
3.C:\Program\Data\Microsoft.db（该文件包含一段被加密的有效载荷，该载荷是最后阶段释放执行）

下图为下载的powershell代码：

[![](https://p4.ssl.qhimg.com/dm/1024_289_/t010fbb02e27a0e29e9.png)](https://p4.ssl.qhimg.com/dm/1024_289_/t010fbb02e27a0e29e9.png)

从上图中我们可以看到，第一个被执行的文件是“Windows.vbe”文件，该文件通过Cscript（Windows脚本宿主的一个版本，可以用来从命令行运行脚本）来执行temp.jpg中的Javascript代码，该Javascript代码被加密，解密后可以看到其功能是延迟执行另一段powershell。下图是解密后的temp.jpg中的Javascript代码：

[![](https://p0.ssl.qhimg.com/dm/1024_166_/t01ba59f977098f1fd7.png)](https://p0.ssl.qhimg.com/dm/1024_166_/t01ba59f977098f1fd7.png)

由上图我们可以看到，这段代码只有满足“Math.round(ss) % 20 == 19”条件才会继续执行下一个恶意阶段，否则会不断的重复此过程。代码中的“ss”变量是getTime()函数的返回值，表示当前时间距 1970 年 1 月 1 日之间的毫秒数。

当条件满足后，会执行“Microsoft.db”文件，该文件中包含POWERSTATS后门程序。该后门连接的域名如下：

1.hxxp://amphira[.]com<br>
2.hxxps://amorenvena[.]com

这些域名都指向同一个IP地址：139.162.245.200（该IP所在地为英国）。

[![](https://p3.ssl.qhimg.com/t018d8688575d4bb1f5.png)](https://p3.ssl.qhimg.com/t018d8688575d4bb1f5.png)

如上图所示，POWERSTATS后门程序会进行HTTP和POST请求，该请求会连接远程服务器，并上传受害者机器的通用信息，下图为发送的受害者信息：

[![](https://p5.ssl.qhimg.com/t014b9ea02ce61d864e.png)](https://p5.ssl.qhimg.com/t014b9ea02ce61d864e.png)

然后，该后门与C2进行通信，并请求操作指令。我们在分析中发现HTTP的参数“type”有以下数值，分别代表执行不同功能：

1.info：在POST请求中使用，会发送受害者机器的相关信息。<br>
2.live：在POST请求中使用，进行ping操作。<br>
3.cmd：POST和GET请求中使用，在POST请求中，其功能是发送最后执行的命令。在GET请求中，其功能是检索服务器中的新命令。<br>
4.res：在POST请求中使用，功能是当恶意软件已执行后，发送该消息。

参数“id”是受害者机器的唯一标识，通过系统信息计算得出，此标识被用于创建文件，文件路径为：C:ProgramData，创建出的文件用来存储临时信息。下图是相关代码：

[![](https://p3.ssl.qhimg.com/dm/1024_236_/t01932f0eeb909d0142.png)](https://p3.ssl.qhimg.com/dm/1024_236_/t01932f0eeb909d0142.png)

我们分析了Microsoft.db文件中的代码，该代码被混淆，反混淆后我们识别出POWERSTATS后门具备以下指令功能：

1.upload：恶意软件会从指定的URL下载新的文件<br>
2.cmd：恶意软件会执行指定的命令<br>
3.b64：恶意软件通过base64解码Powershell脚本并执行<br>
4.muddy:恶意软件新建一个加密文件并执行，文件路径在C:ProgramDataLSASS目录下，该文件包含powershell脚本。下图是反混淆后的POWERSTATS后门代码：

[![](https://p0.ssl.qhimg.com/t018cae51055eadca01.png)](https://p0.ssl.qhimg.com/t018cae51055eadca01.png)

**持久性**

为了保证自己拥有持久化的能力，该恶意软件采用了多个技术手段，比如把自己添加到注册表项：“MicrosoftWindowsCurrentVerisonRun” 下以保持开机自启动。如下图所示：

[![](https://p1.ssl.qhimg.com/t0133db3fc9a97295e9.png)](https://p1.ssl.qhimg.com/t0133db3fc9a97295e9.png)

[![](https://p3.ssl.qhimg.com/t01f34e061b1f86dd1a.png)](https://p3.ssl.qhimg.com/t01f34e061b1f86dd1a.png)

创建一个名为“MicrosoftEdge”的计划任务，该计划任务设置为每天12点开始执行。如下图所示：

[![](https://p3.ssl.qhimg.com/t0189484fb4f0160919.png)](https://p3.ssl.qhimg.com/t0189484fb4f0160919.png)



## 三、总结

通过对MuddyWater（污水，伊朗的APT组织）组织最近的活动进行分析，我们发现了其攻击的方式和流程。包括：如何利用系统工具和脚本来实现特定目标，如何保持自身持久性，如何利用嵌入宏的文档进行攻击，并通过一些方式引诱受害者执行恶意载荷等。其整个攻击流程图如下：

[![](https://p4.ssl.qhimg.com/dm/1024_737_/t01028d1974aea852e1.png)](https://p4.ssl.qhimg.com/dm/1024_737_/t01028d1974aea852e1.png)



## 四、IOC

Dropurl:

```
hxxp://pazazta[.com/app/icon.png
```

C2:

```
hxxp://amphira[.com
hxxps://amorenvena[.com
139.162.245.200
```

Hash:

```
294a907c27d622380727496cd7c53bf908af7a88657302ebd0a9ecdd30d2ec9d
79f2d06834a75981af8784c2542e286f1ee757f7a3281d3462590a89e8e86b5a
ae2c0de026d0df8093f4a4e2e2e4d297405f943c42e86d3fdd0ddea656c5483d
077bff76abc54edabda6b7b86aa1258fca73db041c53f4ec9c699c55a0913424
ccfdfcee9f073430cd288522383ee30a7d6d3373b968f040f89ae81d4772a7d0
```
