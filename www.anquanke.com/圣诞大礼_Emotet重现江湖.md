> 原文链接: https://www.anquanke.com//post/id/94022 


# 圣诞大礼：Emotet重现江湖


                                阅读量   
                                **165092**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Minerva Labs，文章来源：minerva-labs.com
                                <br>原文地址：[https://blog.minerva-labs.com/the-emotet-grinch-is-back](https://blog.minerva-labs.com/the-emotet-grinch-is-back)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t016a51783f1267ed7e.png)](https://p1.ssl.qhimg.com/t016a51783f1267ed7e.png)



## 一、前言

如果大家读过minerva实验室之前发表的文章，那么应该对Emotet有所了解。最近minerva又阻挡了Emotet新发起的一波攻击，这波攻击以圣诞节主题，我们将其称之为“Emotet Grinch”（Emotet圣诞怪杰）。



## 二、技术分析

网络犯罪分子最近正在紧锣密鼓推广这款恶意软件，想方设法绕过基本防线，突破目标系统。在十二月底时，Minerva阻止了Emotet新发起的一波攻击浪潮，这次攻击与时俱进，以圣诞节为主题。与之前的攻击类似，“Emotet Grinch”同样以钓鱼邮件为攻击起点，该邮件中包含指向恶意文档的一条链接，文档名为“Your Holidays eCard.doc”（你专属的假日电子贺卡.doc）。这份文档同样会想方设法诱使用户启动文档中内置的恶意宏，如下图所示：

[![](https://p1.ssl.qhimg.com/t01dc328708e724b9bd.png)](https://p1.ssl.qhimg.com/t01dc328708e724b9bd.png)

接下来，攻击行为与之前的Emotet攻击活动类似：恶意宏会使用如下字符串作为参数，运行`cmd.exe`：

[![](https://p4.ssl.qhimg.com/t01284bea5ddfc2af88.png)](https://p4.ssl.qhimg.com/t01284bea5ddfc2af88.png)

这个脚本中有一些冗余信息，使用多个变量用来掩盖“powershell”这个字符串，可以看出攻击者精心伪造了下一阶段的攻击载荷，下一阶段使用的是PowerShell无文件攻击载荷。在之前的攻击活动中，Emotet所使用的攻击载荷开头部分为经过混淆的[Invoke-Expression](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-expression?view=powershell-5.1)调用语句，后面跟着字符串形式的一段PowerShell脚本：

[![](https://p3.ssl.qhimg.com/t012bcce265aa3f6c4d.png)](https://p3.ssl.qhimg.com/t012bcce265aa3f6c4d.png)

如上图所示，老版的Emotet样本在内嵌的PowerShell载荷之前，会对“iex”字符串进行混淆处理。

其中，“comspec”这个环境变量对应的是`cmd.exe`的具体路径，攻击者精心选择该路径中的几个字符，最终组成了“iex”这个字符串，该字符串也是[Invoke-Expression](http://ilovepowershell.com/2011/11/03/list-of-top-powershell-alias/)的别名（alias）。

[![](https://p4.ssl.qhimg.com/t01e0d7a62c76e8792f.png)](https://p4.ssl.qhimg.com/t01e0d7a62c76e8792f.png)

与之前的攻击活动不同，这一次Emotet Grinch使用了三重“Invoke-Expression”混淆来给受害者送份“大礼”。每一层混淆都会使用一条命令返回预定的一个值，再以这个值为输入来构造最终的“iex”字符串：

第一层，使用“MaximumDriveCount”：

[![](https://p3.ssl.qhimg.com/t010e0fb58a68ea4ba1.png)](https://p3.ssl.qhimg.com/t010e0fb58a68ea4ba1.png)

第二层，使用“$Shellid”变量：

[![](https://p2.ssl.qhimg.com/t0128424f18de5079f0.png)](https://p2.ssl.qhimg.com/t0128424f18de5079f0.png)

第三层，使用“$VerbosePreference”：

[![](https://p3.ssl.qhimg.com/t01afd844cca4609dba.png)](https://p3.ssl.qhimg.com/t01afd844cca4609dba.png)

攻击者将这种“iex套娃”混淆技术与字符串替换方法（如将“garBaGe”替换为“c”）结合在一起，这样就能绕过静态扫描技术，许多安全产品难以揭开足够多的掩护层，无法触摸到最里面的恶意功能。

去混淆处理完成后，恶意软件会在受害者系统上执行如下脚本：

[![](https://p0.ssl.qhimg.com/t01f31fffaebad9a649.png)](https://p0.ssl.qhimg.com/t01f31fffaebad9a649.png)

经过去混淆处理后，我们可以看到最终的PowerShell脚本结构比较清晰，该脚本可以从5个域名下载Emotet的可执行载荷，这些域名已经硬编码到脚本中，下载的可执行文件被重命名为随机数字名，然后再加以执行。

值得注意的是，与早期的Emotet可执行载荷类似，用户可以使用Minerva出品的DIY Emotet防护方法来对抗此次Emotet攻击浪潮：

[![](https://p5.ssl.qhimg.com/t015f615f38db471511.png)](https://p5.ssl.qhimg.com/t015f615f38db471511.png)

此外，Minerva的Anti-Evasion Platform包含各种安防功能，可以防止用户被Emotet感染。该平台中位于最前线的为[Malicious Document Prevention](https://minerva-labs.com/malicious-document-prevention)（恶意文档预防）模块，该模块可以在攻击活动的初始阶段打破整个感染链，使攻击者无法通过恶意文档执行第一阶段的攻击，因此能保护用户安全。



## 三、IoC

**恶意文档SHA256哈希：**

```
abd5d939438d963e05e59e137e7679e1408e0f9c7f4b0690287aecb807cd2909
```

**托管可执行载荷的URL：**

```
hxxp://metricinvestmentsgroup[.]com/bAtOQlC/
hxxp://dopplmeister[.]com/897zkkf/
hxxp://starklogic[.]com/xr5e/
hxxp://archersdelathur[.]org/Zw1Db/
hxxp://lephamtech[.]com/gIhZm/
```

此外，[Pastebin页面](https://pastebin.com/u/Spacing)，该页面每天会更新相关URL地址。

**托管恶意文档的URL：**

```
hxxp://roberthempsall[.]co[.]uk/Your-Holidays-eCard/
hxxp://www.printit[.]com[.]pk/Your-holidays-Gift-Card/
```
