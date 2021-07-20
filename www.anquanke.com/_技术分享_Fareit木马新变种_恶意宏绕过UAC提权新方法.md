> 原文链接: https://www.anquanke.com//post/id/85174 


# 【技术分享】Fareit木马新变种：恶意宏绕过UAC提权新方法


                                阅读量   
                                **87569**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.fortinet.com
                                <br>原文地址：[http://blog.fortinet.com/2016/12/16/malicious-macro-bypasses-uac-to-elevate-privilege-for-fareit-malware](http://blog.fortinet.com/2016/12/16/malicious-macro-bypasses-uac-to-elevate-privilege-for-fareit-malware)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p2.ssl.qhimg.com/t01420b37f724e275e6.png)](https://p2.ssl.qhimg.com/t01420b37f724e275e6.png)



**翻译：**[**pwn_361******](http://bobao.360.cn/member/contribute?uid=2798962642)

**预估稿费：150RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

为了生存下来，基于宏的下载者需要不断开发新的技术，用于规避沙箱环境和对抗杀毒软件。近日，研究人员发现[Fareit](https://blog.fortinet.com/2016/05/06/new-fareit-variant-analysis)设计了一个恶意的宏文档，用于绕过Windows UAC，并执行Fareit。

根据2015年4月统计, 由Fareit感染的肉鸡组成的僵尸网络，每天可以发送77亿封垃圾邮件, 并通过邮件传播恶意软件盗取网银, 比特币等用户信息。

[![](https://p3.ssl.qhimg.com/t01c0b6da24ff10e667.jpg)](https://p3.ssl.qhimg.com/t01c0b6da24ff10e667.jpg)

Fareit木马感染全球态势—-根据2015年数据统计

[![](https://p0.ssl.qhimg.com/t013f81cf8462bb25c3.jpg)](https://p0.ssl.qhimg.com/t013f81cf8462bb25c3.jpg)

Fareit木马感染国内情况—-根据2015年数据统计

<br>

**垃圾邮件**

这个恶意文档用垃圾邮件来传播，在社会工程学策略的引诱下，可能会有很多感兴趣的人。

[![](https://p4.ssl.qhimg.com/t017094fa41e76e8764.png)](https://p4.ssl.qhimg.com/t017094fa41e76e8764.png)

<br>

**带恶意文档的垃圾邮件**

通常，当文档打开时，目标受害者被鼓励开启宏执行。当用户开启宏时，恶意宏会在后台执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e1b48b20eee1f44e.png)

<br>

**恶意文档鼓励用户开启宏**

这个宏通过向真实字符串中插入乱码的方法，进行了简单的混淆。

[![](https://p5.ssl.qhimg.com/t01020a02e90bccec01.png)](https://p5.ssl.qhimg.com/t01020a02e90bccec01.png)

删除乱码的函数

下面是一个例子：

[![](https://p0.ssl.qhimg.com/t0112040e1719069a8e.png)](https://p0.ssl.qhimg.com/t0112040e1719069a8e.png)

真实的字符串是”cmd.exe/c powershell”。

下面是这个宏里执行的完整SHELL命令：

[![](https://p1.ssl.qhimg.com/t019ac25918434a0f85.png)](https://p1.ssl.qhimg.com/t019ac25918434a0f85.png)

里面包含了恶意宏文件下载和执行恶意软件的常见行为。然而，让我们感兴趣的是，这个宏会以高权限执行Fareit木马(sick.exe)，而它本身是以低权限运行的。根据默认的UAC设置，在没有UAC权限提示弹出的情况下，它做到这些应该是不可能的。但是实际上，它绕过UAC设置。并执行Windows本地应用，eventvwr.exe(事件查看器)。

[![](https://p5.ssl.qhimg.com/t011c368e072295c2d0.png)](https://p5.ssl.qhimg.com/t011c368e072295c2d0.png)

宏执行了事件查看器和Fareit(sick.exe)

<br>

**绕过UAC并提权**

一个程序在系统中以高权限运行，意味着它能有更多资源的访问权，这对于一个低权限的程序是达不到的。就恶意软件而言，这意味着它有偷取更多数据的能力、做更多事的机会。

UAC安全机制用于阻止应用程序在没有用户允许的情况下以高权限运行。这也是一个方便的功能，可以允许用户在不切换用户的情况下，执行管理员和非管理员任务。

为了能更好理解这个SHELL命令，我们将它分成四部分。

第一部分仅仅是下载Fareit恶意软件，并存储为%TEMP%sick.exe。

命令是：

[![](https://p0.ssl.qhimg.com/t01769920033c35da9a.png)](https://p0.ssl.qhimg.com/t01769920033c35da9a.png)

[![](https://p3.ssl.qhimg.com/t0194b2f71425c8d095.png)](https://p3.ssl.qhimg.com/t0194b2f71425c8d095.png)

第二部分是我们开始感兴趣的地方，这个恶意宏向注册表中添加了下面的一项：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0195c6fd553de2a24f.png)

命令是:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0182fbf3edee2d9037.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014a9dab14c5ba3acd.png)

HKCUSoftwareClasses 包含打开指定文件类型时使用默认软件的注册表项。将恶意软件添加到这个注册表项，意味着每次打开一个mscfile(.msc)文件时，这个恶意软件都会被执行。但其实重点不在这，添加这个注册表项还有更重要的原因。

来看一下第三部分的命令。在改变注册表后，它执行了windows的事件查看器程序，这是一个为监视和排除故障的工具，可以查看程序和系统记录。

命令是：

[![](https://p2.ssl.qhimg.com/t01a48590f279fce40a.png)](https://p2.ssl.qhimg.com/t01a48590f279fce40a.png)

默认情况下，打开事件查看器时，会先执行mmc.exe(windows管理员控制台)，但是，事件查看器并不是直接打开mmc.exe，会首先按顺序在两个注册表地址中执行一个查询，分别是：



```
HKCUSoftwareClassesmscfileshellopencommand；
HKCRmscfileshellopencommand；
```

在上面一个注册表项中已经写入了我们的恶意软件的地址(写入时不需要高权限)，下面的一个注册表项里面是什么呢，如下图，是mmc.exe在系统中的地址：

[![](https://p5.ssl.qhimg.com/t01cb178350317b03dd.png)](https://p5.ssl.qhimg.com/t01cb178350317b03dd.png)

最后恶意软件被先执行了。

现在，非常重要的是：事件查看器启动一个程序时会有一个[自动提权](https://technet.microsoft.com/en-us/library/2009.07.uac.aspx#id0560031)的参数。意味着它能在没有UAC提示的情况下以高权限执行一个程序。从而由它启动的任何一个子进程，都会以高权限运行，在这个安例中，Fareit就以高权限运行了。

在这个案例中，存在的漏洞是：一个高权限的Windows本地应用程序（eventvwr .exe）的参数、或依赖的系统构件，可以很容易的被较低权限的程序修改。

这个UAC绕过技术是enigma0x3几个月前发现的，漏洞的详细分析可以从[这里看到](https://enigma0x3.net/2016/08/15/fileless-uac-bypass-using-eventvwr-exe-and-registry-hijacking/)。

SHELL命令的第四部分是“%tmp%sick.exe”，试图再次执行Fareit木马，这可能仅仅是以高权限启动失败后的一个故障安全机制。

<br>

**结论**

基于宏的恶意软件攻击已经出现了很长时间了，大部分是因为这是非常有效的社会工程学方案。随着时间的过去，它们为了规避探测，变得更加积极并富有创建性，这个例子就很好的体现了它的进步和发展，今后，我们肯定会看到其他的变种。

不久前，安全研究人员发布绕过这种UAC绕过技术的POC代码。向公众分享这样的信息总是有好处也有坏处。对于安全人员，它可以作为一个好的启发，用来规划和减轻其不良影响。但是，这也给了坏人一个好机会。

总之，这里有一些简单的安全措施，可以减轻这些类型的攻击：

如果不使用宏，则禁用宏的执行；

将UAC设置为“总是通知”；

警惕那些来历不明的电子邮件和文件；

<br>

**参考文章**

[http://www.freebuf.com/news/85568.html](http://www.freebuf.com/news/85568.html)

[http://blog.fortinet.com/2016/12/16/malicious-macro-bypasses-uac-to-elevate-privilege-for-fareit-malware](http://blog.fortinet.com/2016/12/16/malicious-macro-bypasses-uac-to-elevate-privilege-for-fareit-malware)

[https://technet.microsoft.com/en-us/library/2009.07.uac.aspx#id0560031](https://technet.microsoft.com/en-us/library/2009.07.uac.aspx#id0560031)
