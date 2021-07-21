> 原文链接: https://www.anquanke.com//post/id/87261 


# 【技术分享】针对新型POS机恶意软件Trojan.Win32.Alinaos的分析


                                阅读量   
                                **89839**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pandasecurity.com
                                <br>原文地址：[https://www.pandasecurity.com/mediacenter/pandalabs/alina-pos-malware/](https://www.pandasecurity.com/mediacenter/pandalabs/alina-pos-malware/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01a37ac9acf3522e06.jpg)](https://p5.ssl.qhimg.com/t01a37ac9acf3522e06.jpg)

****

译者：[eridanus96](http://bobao.360.cn/member/contribute?uid=2857535356)

预估稿费：110RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

****

日常生活中，当我们刷卡后，POS机通常会保存我们的消费记录，其中就包含信用卡的信息。因此，POS机已经成为了一个关键的系统，同时也日益成为网络犯罪者的重要攻击目标。

如今在黑市上，有不少人都在通过售卖信用卡信息来赚取非法盈利。而在网络中，针对POS终端进行攻击也相对简单。正因如此，我们需要关注POS机的安全。

近期，我们在美国的大量酒吧和餐厅都发现了POS机恶意软件。经过分析，他们的POS终端是被信用卡信息窃取恶意软件的两个变种所感染。

本文中，我们要分析的恶意软件如下：

[![](https://p3.ssl.qhimg.com/t01cf62a1f9ee925fd4.png)](https://p3.ssl.qhimg.com/t01cf62a1f9ee925fd4.png)



**分析过程**

其中，Epson使用了一个无效的证书：

[![](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/1-1100x433.png)](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/1-1100x433.png)

这两个样本都是使用Microsoft Visual C++ 8 编译而成的，**并且没有经过加壳或者加密。一旦恶意软件在系统中运行，它会自动分析系统中不同的进程，以搜索信用卡信息。**

在这里，我们重点关注恶意软件是通过哪些不同的方法，在内存中寻找到包含信用卡信息的程序：

[![](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/2.png)](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/2.png)

在“Epson.exe”样本中，它会按照以下步骤搜索信用卡信息：

[![](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/3.png)](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/3.png)

[![](https://p4.ssl.qhimg.com/t0109f541acbc72cd4a.png)](https://p4.ssl.qhimg.com/t0109f541acbc72cd4a.png)

而另一个变种，“Wnhelp.exe”样本中包含一个不进行分析的进程清单。如果进程名称符合表格中的任意一项，在搜索信用卡信息时就不会分析该进程：

[![](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/4.png)](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/4.png)

**Wnhelp.exe不分析的进程：**

[![](https://p3.ssl.qhimg.com/t0192c5a24e4469d995.png)](https://p3.ssl.qhimg.com/t0192c5a24e4469d995.png)

在这两个样本中，一旦发现需要对某个进程进行分析，将会创建一个新线程：

[![](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/5.png)](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/5.png)

然后，恶意软件将会使用专门设计的算法来分析内存，以检查所找到的数据是否属于信用卡信息：

[![](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/6.png)](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/6.png)

Wnhelp.exe样本是由攻击者通过“install”命令执行的，该病毒会创建一个服务，以确保其在系统中能持续存在：

[![](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/7.png)](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/7.png)

该服务的名称为“Windows错误报告服务日志”（Windows Error Reporting Service Log）。

[![](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/8.png)](https://www.pandasecurity.com/mediacenter/src/uploads/2017/11/8.png)

样本Epson.exe的工作方式与Wnhelp大体相同，但不同的是，攻击者可以通过修改参数来配置服务的名称：

**install [服务名称] [服务描述] [第三个参数]**

这两个变种，分别会连接到不同的C&amp;C服务器：

**Epson.exe：<strong>dropalien[.]com/wp-admin/gate1.php**</strong>

**Wnhelp.exe：www[.]rdvaer[.]com/wp-admin/gate1.php**

****

在连接之后，它们可以接收到攻击者的不同指令：

**update = [URL] —— 通过指定URL，对恶意软件进行更新**

**dlex = [URL] —— 通过指定URL，下载并运行程序**

**chk = [CRC校验值] —— 提供更新文件的CRC校验值**

上述恶意软件会使用如下代理：

“Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.152 Safari/537.22”

恶意软件与C&amp;C主机的通信会通过SSL传输。并且，恶意软件通过修改网络连接配置，以避免产生“未知的证书颁发机构”（Unknown CAs）安全警告，从而确保它能够使用自己的证书。

首先，它通过InternetQueryOptionA API获得网络安全连接的标志，并将第三个参数的值设置为“**INTERNET_OPTION_SECURITY_FLAGS**(31)”。一旦成功，它将会带有“**SECURITY_FLAG_IGNORE_UNKNOWN_CA **(100h)”的标志，就可以继续执行下一步操作。



**如何防范POS攻击**

****

目前，针对POS的攻击已经十分流行，特别是在美国这样没有强制使用带有芯片的信用卡和刷卡密码的国家。并且，许多POS机的使用者并不掌握安全方面的技能，甚至对计算机都知之甚少，这便无形中提高了攻击的成功几率。

POS终端是处理关键数据的计算机，因此必须重视对于其安全的加强，从而保护客户的数据免受泄露的风险。针对用户，建议大家更换并使用带有芯片的银行卡，并且开启密码验证功能。除此之外，使用一些自适应防御的解决方案，也能有助于确保在终端中不会有恶意进程运行。
