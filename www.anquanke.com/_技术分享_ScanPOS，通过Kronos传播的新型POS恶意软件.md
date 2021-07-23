> 原文链接: https://www.anquanke.com//post/id/85194 


# 【技术分享】ScanPOS，通过Kronos传播的新型POS恶意软件


                                阅读量   
                                **79277**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：morphick.com
                                <br>原文地址：[http://www.morphick.com/resources/lab-blog/scanpos-new-pos-malware-being-distributed-kronos](http://www.morphick.com/resources/lab-blog/scanpos-new-pos-malware-being-distributed-kronos)

译文仅供参考，具体内容表达以及含义原文为准

 **[![](https://p0.ssl.qhimg.com/t0131afcf92497ba2c2.jpg)](https://p0.ssl.qhimg.com/t0131afcf92497ba2c2.jpg)**

****

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：100RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**



不久前，安全研究人员又发现了一个全新POS恶意软件家族——ScanPOS。

安全研究人员在分析Kronos网络钓鱼活动过程中，发现了一个含有下载银行恶意软件Kronos的恶意宏指令的相关文档。当Kronos运行时，它的payload将进一步下载另外几种恶意软件，但是引起他们注意的是一种新型的信用卡转储软件，该软件的检测难度非常大。根据在这款恶意软件中发现的字符串，安全研究人员将其正式命名为ScanPOS，以便于进行持续的跟踪和研究。

```
C:Usersexampledocumentsvisual studio 2010Projectsscan3Releasescan3.pdb
```

在写这篇文章的时候，ScanPOS在Virustotal网站上的检出率只有1/55：               

[![](https://p4.ssl.qhimg.com/t011718344dfa5b6302.png)](https://p4.ssl.qhimg.com/t011718344dfa5b6302.png)

ScanPOS是一个新的银行恶意软件家族。虽然它的基本功能与其他POS恶意软件基本相同，但它的隐身功能却是非常出色的。为了逃避杀毒软件的检测，ScanPOS软件做的非常小，这可以帮助轻松混入生产环境中。当代码被过度加壳后，反而容易被通用的启发式算法所捕获。

**<br>**

**网络钓鱼： **

****

实际上，Kronos是通过非常简单的网络钓鱼邮件来传播这款新型恶意软件的，电子邮件的内容如下所示：



```
An Employee has just been terminated.
Name: Tanner Williamson
Employee profile: EmployeeID-6283.doc
Emplid: 2965385
Rcd#: 0
Termination Date: 11/17/2016
```

相关的邮件头部如下所示：



```
TIME-STAMP: "16-11-14_13.44.23"
CONTENT-DISPOSITION: "attachment; filename='EmployeeID-6283.doc'"
X-VIRUS-SCANNED: "Debian amavisd-new at hosting5.skyinet.pl"
Subject : An Employee has just been terminated.
From: HR &lt;johns.brueggemann@banctec.com&gt;
Mail-From: web1@hosting5.skyinet.pl
1st rec: hosting23.skyinet.pl
2nd rec:hosting23.skyinet.pl
```

当EmployeID-6283.doc启用宏时，那么将下载Kronos的Payload： 

```
profile.excel-sharepoint[.]com/doc/office.exe
```

下载完成后，就会执行它。之后，Kronos将通过下面的地址来下载并执行ScanPOS



```
http://networkupdate[.]online/kbps/upload/a8b05325.exe.
```

 

**转储信用卡信息：**

在执行时，该恶意软件将获取有关当前进程的信息并让用户调用GetUserNameA。同时，它还会通过SeDebugPrivilege（见下文）来进行权限检查，以确保该恶意软件有权查看其他进程的内存空间。

[![](https://p1.ssl.qhimg.com/t017e1cc7cae3c400eb.png)](https://p1.ssl.qhimg.com/t017e1cc7cae3c400eb.png)

然后，该恶意软件将进入无限循环，来转储计算机上面的进程内存，搜索信用卡轨道数据。在此循环过程中，该恶意软件将使用Process32FirstW / Process32Next来遍历通过CreateToolhelp32Snapshot获取的进程列表中的所有进程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ec65148af1178912.png)

迭代器通过使用OpenProcess获取进程的句柄，然后通过检查一个简单的白名单来过滤掉不必要的系统进程： 

[![](https://p1.ssl.qhimg.com/t01519e1b166b3acee5.png)](https://p1.ssl.qhimg.com/t01519e1b166b3acee5.png) 

如果进程的名称通过了白名单，那么该恶意软件将进一步通过调用VirtualQueryEx以及ReadProcessMemory函数来获取该进程的内存信息。

  [![](https://p1.ssl.qhimg.com/t01ab24743fefcf186d.png)](https://p1.ssl.qhimg.com/t01ab24743fefcf186d.png)

一旦取得了进程内存，就可以开始扫描信用卡轨道数据了，其背后的主要逻辑是由函数0x4026C0实现的。

这段代码首先检查相应的标记符号（sentinel checks），并且从3,4,5或6开始下手。

[![](https://p2.ssl.qhimg.com/t0125193f7e1ca81811.png)](https://p2.ssl.qhimg.com/t0125193f7e1ca81811.png)

然后，该恶意软件将使用自定义的搜索程序（而不是规则表达式）来查找潜在的候选数字。

[![](https://p4.ssl.qhimg.com/t019e732fe0ac8a5a86.png)](https://p4.ssl.qhimg.com/t019e732fe0ac8a5a86.png)

该恶意软件对信用卡信息进行多次检查后，它会利用Luhn算法对潜在卡号进行基本验证。

 [![](https://p3.ssl.qhimg.com/t015ca95d832e2b411f.png)](https://p3.ssl.qhimg.com/t015ca95d832e2b411f.png) 

当它找到了通过Luhn算法验证的潜在候选号码时，它将继续搜索数字（介于0到9之间的任意值），直到它命中轨道数据的结束标记“？”为止。

[![](https://p3.ssl.qhimg.com/t01639c6f82e631c780.png)](https://p3.ssl.qhimg.com/t01639c6f82e631c780.png)

**<br>**

**网络连接：**



一旦找到潜在的卡号，就会通过HTTP POST将其发送到invoicesharepoint [。] com。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010a0f0f49d1939b60.png) 

**<br>**

**结束语**



ScanPOS是一款最近发现的银行恶意软件，当前只有一个反病毒引擎将这个可执行文件标记为恶意代码。在本文中，我们对该恶意软件进行了全面的分析，希望对大家有所帮助。

<br style="text-align: left">
