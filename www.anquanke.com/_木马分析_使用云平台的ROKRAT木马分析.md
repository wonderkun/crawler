> 原文链接: https://www.anquanke.com//post/id/85847 


# 【木马分析】使用云平台的ROKRAT木马分析


                                阅读量   
                                **133822**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/04/introducing-rokrat.html](http://blog.talosintelligence.com/2017/04/introducing-rokrat.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t011bddff1a310f49cf.jpg)](https://p4.ssl.qhimg.com/t011bddff1a310f49cf.jpg)**

****

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

几周前，Talos实验室发表了一篇韩国恶意文档的[研究报告](http://blog.talosintelligence.com/2017/02/korean-maldoc.html)。正如我们之前讨论的一样，这个攻击者反应很快，及时调整了攻击轨迹，抹掉了受害主机上的痕迹。我们认为攻击者在任何一次攻击活动中使用的控制服务器活动时长不超过几个小时。最近我们又捕获了一个新的攻击活动，使用了是韩国常用的恶意Word文档（HWP文档），文档的攻击载荷是一款远控工具，我们称之为ROKRAT。

与之前的文章类似，攻击活动以钓鱼邮件开始，包含一个HWP文档的恶意附件。其中一个样本邮件是从首尔延世私立大学邮件服务器发出的，邮件地址是“kgf2016@yonsei.ac.kr”，为韩国全球论坛的联系邮箱，“2016”可能指的是“朝鲜半岛的和平统一”，这些字符是想增加该电子邮件地址的合理性和信誉度。

这个HWP文档包含一个嵌入式EPS对象（Embedded Encapsulated PostScript，EPS是用PostScript语言封装的一种文件格式），也是一种zlib压缩文件。攻击者使用EPS是为了利用已知漏洞（CVE-2013-0808）下载伪装为jpg图片的二进制文件。二进制文件解码后为ROKRAT远控工具，这个工具以合法的网站作为其命令控制服务器以增加复杂性。这些网站包括Twitter以及Yandex、Mediafire这两个云平台，不幸的是这些平台的使用一般不会被阻拦，因为它们在大多数情况下都是用于合法用途。此外，这三个平台使用的都是HTTPS协议，这样安全人员更加难以识别攻击行为中的特征模式和特征令牌。

<br>

**二、钓鱼邮件**

下图是针对韩国发送的钓鱼邮件样本：

[![](https://p5.ssl.qhimg.com/t01e58b5bb07c9ac022.png)](https://p5.ssl.qhimg.com/t01e58b5bb07c9ac022.png)

我们所捕获的第一封邮件最为有趣。在这个样本中，我们观察到攻击者在邮件中感谢用户接受加入“韩国统一与朝鲜问题会议”这个小组，邮件表示用户应该填写文档内容并提交反馈。然而，这个会议是个冒牌会议，与之最为贴近的是2017年1月份举办的[NYDA统一会议](https://nkleadershipwatch.wordpress.com/2017/01/19/nyda-reunification-joint-conference-held/)。邮件发送者是“kgf2016@yonsei.ac.kr”，这是[韩国全球论坛](http://www.kgforum.kr/)的联系邮箱。

查看邮件头部，我们发现邮件发送者IP是“165.132.10.103”，通过“nslookup”命令可知该IP属于延世大学的一个SMTP服务器。我们认为该邮箱被攻击者盗用，借此发送钓鱼邮件。

样本文件名翻译过来就是“统一北韩会议_调查问卷”，邮件内容又再次强调了统一会议这个主题。此外，攻击者暗示收件人在填写文档并反馈后将会获得一些“小费”，也许恶意软件就是那个“小费”。

[![](https://p1.ssl.qhimg.com/t01951e940df9d80843.png)](https://p1.ssl.qhimg.com/t01951e940df9d80843.png)

我们捕获的第二封邮件就没那么用心了。该邮件使用了Daum（Hanmail的前身）邮件服务商提供的免费邮件，与之前的相比，该邮件并没有试图伪装成来自官方机构或个人的邮件，而是使用了简单的“请求帮助”主题，文档附件名为“我是一名来自朝鲜江原道文川市的人”。我们怀疑攻击者想借此博得受害者的同情，因为江原道以前曾是韩国领土的一部分。附件内容讲述了一个名为“Ewing Kim”的人正在寻求帮助的故事。

邮件的附件使用了两个不同的HWP文档，但利用都是CVE-2013-0808这个漏洞。

<br>

**三、恶意HWP文档**

这个HWP文档由OLE对象组成。在本文样例中，该文档包含一个名为BIN0001.eps的EPS对象。由于HWP文档的信息使用了zlib压缩，因此你需要解压“.eps”对象来获得真正的shellcode。

[![](https://p4.ssl.qhimg.com/t01369a73eae96b9c6a.png)](https://p4.ssl.qhimg.com/t01369a73eae96b9c6a.png)

我们可以从EPS对象中找到利用CVE-2013-0808漏洞的shellcode：

[![](https://p0.ssl.qhimg.com/t01b6d35d769b0810a8.png)](https://p0.ssl.qhimg.com/t01b6d35d769b0810a8.png)

shellcode以0x0404开始，而不是以标准的NOP指令（0x90）开始：



```
user@lnx$ rasm2 -d 0404040404040404040490909090909090909090E8000000005E
add al, 0x4
add al, 0x4
add al, 0x4
add al, 0x4
add al, 0x4
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
call 0x19
pop esi
```

这两个HWP文档中的shellcode目的是下载并解码互联网上的一个载荷。载荷为二进制可执行文件。以下是文档所使用的一些样本信息：



```
SHA256: 7d163e36f47ec56c9fe08d758a0770f1778fa30af68f39aac80441a3f037761e
文件名: 통일북한학술대회_심사서류.hwp ("朝鲜会议_调查问卷")
URL: http://discgolfglow[.]com:/wp-content/plugins/maintenance/images/worker.jpg
```

[![](https://p5.ssl.qhimg.com/t0187c028ff5784f5bb.png)](https://p5.ssl.qhimg.com/t0187c028ff5784f5bb.png)



```
SHA256: 5441f45df22af63498c63a49aae82065086964f9067cfa75987951831017bd4f 
文件名: 저는요 북조선 강원도 문천 사람이에요.hwp (“我是一名来自朝鲜江原道文川市的人”)
URL: http://acddesigns[.]com[.]au/clients/ACPRCM/kingstone.jpg
```

[![](https://p1.ssl.qhimg.com/t0164ac4b2752822d76.png)](https://p1.ssl.qhimg.com/t0164ac4b2752822d76.png)

<br>

**四、木马分析**

这两个文档所下载的木马都属于同一族群，主要区别是所使用的命令与控制服务器，其中一个使用了Twitter作为C2服务器，另一个使用了Yandex和Mediafire这两个云平台，两个样本都包含同一个Twitter令牌。

**（一）反分析策略**

ROKRAT作者使用了常见的几种技术来对抗人工分析和避免在沙箱内执行。

首先，恶意软件不在Windows XP系统上运行，它使用GetVersion() API判断操作系统版本，如果主版本号为5，就执行无限循环sleep：

[![](https://p5.ssl.qhimg.com/t0128144fd21ff47471.png)](https://p5.ssl.qhimg.com/t0128144fd21ff47471.png)

此外，恶意软件检查当前运行进程，以便识别安全软件或沙箱环境，如以下代码：

[![](https://p2.ssl.qhimg.com/t01621b8903a109c956.png)](https://p2.ssl.qhimg.com/t01621b8903a109c956.png)

恶意软件检查受害者主机上的进程名，查看是否包含包含关键词，关键词列表如下：



```
"mtool"代表VMWare Tools
"llyd"代表OllyDBG
"ython"代表Python (Cuckoo等沙箱使用这个工具)
"ilemo"代表File Monitor
"egmon"代表Registry Monitor
"peid"代表PEiD
"rocex"代表Process Explorer
"vbox"代表VirtualBox
"iddler"代表Fiddler
"ortmo"代表Portmon
"iresha"代表Wireshark
"rocmo"代表Process Monitor
"utoru"代表Autoruns
"cpvie"代表TCPView
```

如果执行中发现上述任一进程，恶意软件则会跳转到虚假函数中，产生虚假的HTTP流量。另外，如果恶意软件发现自己正被调试、不是通过HWP文档运行（比如使用双击运行）或者在父进程上成功使用OpenProcess()函数，那么恶意软件也会进入虚假处理流程。

恶意软件这么做似乎是为了产生网络流量以提供某种反馈机制，虚假处理流程使用了以下两个URL：



```
https://www[.]amazon[.]com/Men-War-PC/dp/B001QZGVEC/EsoftTeam/watchcom.jpg
http://www[.]hulu[.]com/watch/559035/episode3.mp4
```

[![](https://p4.ssl.qhimg.com/t01508a43d592299688.png)](https://p4.ssl.qhimg.com/t01508a43d592299688.png)

第一个URL是一张“Men of War”的WII游戏图片，第二个URL是一部名为“Golden Time”的日本动漫视频。

[![](https://p1.ssl.qhimg.com/t0174b80e889bd6e9a3.png)](https://p1.ssl.qhimg.com/t0174b80e889bd6e9a3.png)

这两个URL都没有恶意，作者使用这些URL来试图欺骗对其的安全分析。

**（二）C2架构**

ROKRAT使用合法平台作为C2服务器并接收指令。我们总共发现了12个硬编码令牌，通过这些平台的公共API进行通讯。

**1、使用Twitter作为C2服务器**

我们在样本中发现了7个不同的Twitter API令牌（包含Consumer Key、Consumer Secret、Token以及Token Secret）。恶意软件检查Twitter时间线上的最后一条信息来接收指令，指令包括执行命令、移动文件、删除文件、终止进程、下载并执行文件。恶意软件也可以发布推文，推文以下面字符串中的随机三个字符开始：

```
SHA-TOM-BRN-JMS-ROC-JAN-PED-JHN-KIM-LEE-
```

恶意软件使用的是官方的Twitter API：

[![](https://p5.ssl.qhimg.com/t01c2e27831e4da9dd8.png)](https://p5.ssl.qhimg.com/t01c2e27831e4da9dd8.png)

**2、使用Yandex作为C2服务器**

Yandex云平台允许用户在Yandex云中创建磁盘。对于这个C2服务器，我们在样本中找到了4个Yandex令牌。样本使用API来下载和执行文件，或者上传用户文档。文档上传地址为：

```
disk:/12ABCDEF/Document/Doc20170330120000.tfs
```

其中“12ABCDEF”是一个随机ID，用来标识受害主机，而“Doc20170330120000”则包含了时间信息。

[![](https://p0.ssl.qhimg.com/t01499c79ca6a72f830.png)](https://p0.ssl.qhimg.com/t01499c79ca6a72f830.png)

**3、使用Mediafire作为C2服务器**

这个网站的使用方法与Yandex类似，目的在于使用Mediafire提供的文件存储功能，以便下载执行文件或上传用户文档：

[![](https://p5.ssl.qhimg.com/t012db6eb609af0d24a.png)](https://p5.ssl.qhimg.com/t012db6eb609af0d24a.png)

样本中内置了一个Mediafire账户（邮箱、密码和应用ID）。

**（三）其他功能：屏幕截图和键盘记录**

此外，某个样本可以截取受害主机的屏幕，攻击者使用了GDI API来实现这一功能：

[![](https://p1.ssl.qhimg.com/t01762c9ce8581c5f4a.png)](https://p1.ssl.qhimg.com/t01762c9ce8581c5f4a.png)

键盘记录中，恶意软件使用了SetWindowsHookEx()这个API拦截用户键盘输入，使用GetKeyNameText() API来获取按键代表的字符，恶意软件同时提取了前台窗口的标题信息以便了解用户当前所处的输入窗口（使用GetForegroundWindow()以及GetWindowText() API）。

[![](https://p1.ssl.qhimg.com/t018ddb41e573aeb63b.png)](https://p1.ssl.qhimg.com/t018ddb41e573aeb63b.png)

<br>

**五、总结**

这次攻击活动中所使用了HWP（用户主要集中在韩国）文档，邮件和文档完全使用韩文撰写，这表明攻击者以韩语作为母语。

木马使用了新颖的通信渠道，包括Twitter和Yandex、Mediafire这两个云平台来发送命令、获取文件以及上传文件。这种通信渠道难以防范，因为这些平台基本都用于合法用途。恶意软件具备异常处理功能，例如它可以检测自身是否在沙箱中运行或者目标环境中是否存在安全分析工具，检测成功则会进入虚假处理流程并访问合法网站（Amazon和Hulu）。

这次攻击活动再次表明韩国仍是攻击者热衷的目标。本文案例中，攻击者使用了首尔某大学合法论坛的邮箱来发送钓鱼邮件，以提升攻击成功率。

<br>

**六、样本特征**

**（一）文件哈希**

HWP文档：



```
7d163e36f47ec56c9fe08d758a0770f1778fa30af68f39aac80441a3f037761e
5441f45df22af63498c63a49aae82065086964f9067cfa75987951831017bd4f
```

ROKRAT文件：



```
cd166565ce09ef410c5bba40bad0b49441af6cfb48772e7e4a9de3d646b4851c
051463a14767c6477b6dacd639f30a8a5b9e126ff31532b58fc29c8364604d00
```

**（二）网络特征**

恶意URL：



```
http://discgolfglow[.]com/wp-content/plugins/maintenance/images/worker.jpg
http://acddesigns[.]com[.]au/clients/ACPRCM/kingstone.jpg
```

非恶意URL：



```
https://www[.]amazon[.]com/Men-War-PC/dp/B001QZGVEC/EsoftTeam/watchcom.jpg
http://www[.]hulu[.]com/watch/559035/episode3.mp4
```

**（三）令牌特征**

MEDIAFIRE：



```
Account #1
Username: ksy182824@gmail.com
Application ID: 81342
```

TWITTER：



```
Account #1
Consumer key: sOPcUKjJteYrg8klXC4XUlk9l
Token: 722226174008315904-u6P1FlI7IDg8VIYe720X0gqDYcAMQAR
Account #2
Consumer key: sgpalyF1KukVKaPAePb3EGeMT
Token: 759577633630593029-CQzXMfvsQ2RztFYawUPeVbAzcSnwllX
Account #3
Consumer key: XVvauoXKfnAUm2qdR1nNEZqkN
Token: 752302142474051585-r2TH1Dk8tU5TetUyfnw9c5OgA1popTj
Account #4
Consumer key: U1AoCSLLHxfeDbtxRXVgj7y00
Token: 779546496603561984-Qm8CknTvS4nKxWOB4tJvbtBUMBfNCKE
Account #5
Consumer key: 9ndXAB6UcxhQVoBAkEKnwzt4C
Token: 777852155245080576-H0kXYcQCpV6qiFER38h3wS1tBFdROcQ
Account #6
Consumer key: QCDXTaOCPBQM4VZigrRj2CnJi
Token: 775849572124307457-4ICTjYmOfAy5MX2FxUHVdUfqeNTYYqj
Account #7
Consumer key: 2DQ8GqKhDWp55XIl77Es9oFRV
Token: 778855419785154560-0YUVZtZjKblo2gTGWKiNF67ROwS9MMq
```

YANDEX：



```
Token #1: AQAAAAAYm4qtAANss-XFfX3FjU8VmVR76k4aMA0
Token #2: AQAAAAAA8uDKAANxExojbqps-UOIi8kc8EAhcq8
Token #3: AQAAAAAY9j8KAANyULDuYU1240rjvpNXcRdF5Tw
Token #4: AQAAAAAZDPB1AAN6l1Ht3ctALU1flix57TvuMa4
```
