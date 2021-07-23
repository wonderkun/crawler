> 原文链接: https://www.anquanke.com//post/id/166576 


# Rotexy银行勒索软件的演变


                                阅读量   
                                **149890**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者securelist，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/the-rotexy-mobile-trojan-banker-and-ransomware/88893/](https://securelist.com/the-rotexy-mobile-trojan-banker-and-ransomware/88893/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/dm/1024_672_/t01c4aa34ae04550cfd.jpg)](https://p5.ssl.qhimg.com/dm/1024_672_/t01c4aa34ae04550cfd.jpg)



Rotexy家族的移动木马在2018年8月至10月的三个月内，针对位于俄罗斯的用户发起了70,000多起攻击。

这个银行特洛伊木马家族的一个特征是可以同时接收三个不同来源发起的指令：

1.Google Cloud Messaging（GCM）服务 – 该服务用于通过Google服务器将 JSON格式的信息发送到移动设备；

2.恶意C＆C服务器；

3.远程控制短信。

这种“多功能性”出现在Rotexy的最初版本中，并且被该家族持续使用。通过研究发现，这个木马是由2014年10月首次发现的短信间谍软件发展而来的。当时它被检测恶意类型为Trojan-Spy.AndroidOS.SmsThief，但后来变更为另一类型 – Trojan-Banker.AndroidOS.Rotexy。

Rotexy的当前版本结合了银行特洛伊木马和勒索软件的功能。它通过youla9d6h.tk，prodam8n9.tk，prodamfkz.ml，avitoe0ys.tk等网站传播恶意载荷，载荷名称为AvitoPay.apk或其他类似命名。这些网站域名是根据明确的算法生成的：前几个字母暗示热门的分类广告服务，其次是随机字符串，最后是两个字母的顶级域名。在详细介绍Rotexy的最新版本以及它的独特之处之前，先简要介绍自2014年以来该家族木马的演变过程。



## Rotexy的演变过程

### <a name="2014%E5%B9%B4-2015%E5%B9%B4"></a>2014年-2015年

自2014年检测到该家族的恶意程序以来，其主要功能和传播方法没有改变：通过钓鱼短信中的恶意链接进行载荷投递，提示用户安装应用程序。在启动时，它会请求设备管理员权限，随后与恶意C＆C服务器进行通信。DEX文件中的典型类型列表为：

[![](https://p0.ssl.qhimg.com/t01a8a0f56b35cdb55d.png)](https://p0.ssl.qhimg.com/t01a8a0f56b35cdb55d.png)

直到2015年中期，Rotexy使用纯文本JSON格式与其C＆C进行通信。C＆C地址在代码中以明文显示，未进行加密：

[![](https://p4.ssl.qhimg.com/t017218410976f29f00.png)](https://p4.ssl.qhimg.com/t017218410976f29f00.png)

在某些版本的代码中会动态生成低级域名用作C＆C地址：

[![](https://p2.ssl.qhimg.com/t0163d949d6c0706a23.png)](https://p2.ssl.qhimg.com/t0163d949d6c0706a23.png)

在恶意软件被用户安装后，该木马将受感染设备的IMEI信息发送到C＆C服务器，随后它会以短信形式收到一套用于检测受害者所接收短信是否可利用的规则（包含电话号码，关键字和正则表达式），这些规则主要可以识别来自银行，支付系统和移动网络运营商发来的短信。例如，该木马可以根据短信内容自动回复并立即将其删除。

[![](https://p3.ssl.qhimg.com/t010833f6bde58fd514.png)](https://p3.ssl.qhimg.com/t010833f6bde58fd514.png)

接着，Rotexy将受害者手机的信息发送给C＆C，内容包括手机型号，号码，移动网络运营商名称，操作系统版本和IMEI。

[![](https://p0.ssl.qhimg.com/t01243eb3286111a966.png)](https://p0.ssl.qhimg.com/t01243eb3286111a966.png)

该木马每发起一个请求，就会生成一个新的子域名进行通信，生成该域名的算法被硬编在代码中。

Rotexy木马还在Google云消息传递服务中进行了注册，这意味着它可以通过该服务接收命令。Rotexy木马的命令列表在这些年里几乎保持不变，具体命令语句会在文章后面进行详解。

木马的assets文件夹包含文件data.db，文件包含PAGE命令的User-Agent字段的可能值列表（下载指定的网页的地址）。如果该字段的值未能从C＆C获取，则使用伪随机算法从文件data.db中选择它。

data.db的内容为：

[![](https://p1.ssl.qhimg.com/t013a06dd15aa1ac301.png)](https://p1.ssl.qhimg.com/t013a06dd15aa1ac301.png)

### <a name="2015%E5%B9%B4-2016%E5%B9%B4"></a>2015年-2016年

从2015年年中开始，Rotexy木马开始使用AES算法加密受感染设备与C＆C之间通信的数据：

[![](https://p2.ssl.qhimg.com/t01dd38bc37616618f7.png)](https://p2.ssl.qhimg.com/t01dd38bc37616618f7.png)

数据在POST请求中被发送到格式为“/ [number]”的相对地址（伪随机生成的数字，范围为0-9999）。

在某些样本中，从2016年1月开始，已经实现了一种用于从资源文件夹中解压加密的DEX文件的算法。但在此版本的Rotexy中，未使用动态生成最低级域名的办法。

### <a name="2016%E5%B9%B4"></a>2016年

从2016年中期开始，攻击者重新开始使用动态生成的最低级域名的办法。

[![](https://p3.ssl.qhimg.com/t01ed401babc36c339b.png)](https://p3.ssl.qhimg.com/t01ed401babc36c339b.png)

在2016年末，出现了包含在assets / www文件夹中的card.html网络钓鱼页面。该页面旨在窃取用户的银行卡详细信息：

[![](https://p4.ssl.qhimg.com/t01a6fe86284bba6290.png)](https://p4.ssl.qhimg.com/t01a6fe86284bba6290.png)

### <a name="2017%E5%B9%B4-2018%E5%B9%B4"></a>2017年-2018年

从2017年初开始，钓鱼页面bank.html，update.html和extortionist.html开始出现在assets文件夹中。此外，在某些版本的特洛伊木马中，文件名是随机字符串。<br>
在2018年，Rotexy的新版本中出现由随机字符串和数字组成的“一次性”域名，这些随机域名的一级域名为.cf，.ga，.gq，.ml或.tk。

这时，Rotexy木马也开始积极使用了不同的混淆方法。例如，DEX文件包含垃圾字符串的简单and/or操作，并包含用于从APK解密可执行文件的密钥。



## 最新版本分析

以SHA256：ba4beb97f5d4ba33162f769f43ec8e7d1ae501acdade792a4a577cd6449e1a84样本为例进行分析。

### <a name="%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E5%90%AF%E5%8A%A8"></a>应用程序启动

Rotexy通过短信传播，其中包含应用程序下载链接和一些引人注目的文本，这些内容会提示用户点击链接并下载应用程序。在某些情况下，这些消息是从朋友的电话号码发过来的，这就让受害者毫无防备并点击链接。

感染设备后， Rotexy会检查它已经登录的设备，检测内容包括查它是否在仿真环境中启动，以及它在哪个国家/地区启动。如果恶意软件检测到它是在仿真器中运行而不是在真正的智能手机上运行，它就会无限循环应用程序初始化。

[![](https://p5.ssl.qhimg.com/t017a3c2aca8b942b2c.png)](https://p5.ssl.qhimg.com/t017a3c2aca8b942b2c.png)

在这种情况下，特洛伊木马的日志进行俄语记录，内容包括语法错误和拼写错误：

[![](https://p3.ssl.qhimg.com/t01e34c077c65c35a98.png)](https://p3.ssl.qhimg.com/t01e34c077c65c35a98.png)

如果检查成功，Rotexy则将向GCM进行注册并启动SuperService，以跟踪特洛伊木马是否具有设备管理员权限。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e42b59406b9f9114.png)

如果未允许管理员状态，SuperService还会跟踪自己的状态和重新启动。它每秒执行一次特权检查; 如果管理员权限不可用，特洛伊木马会在无限循环中开始向用户请求它们。如果用户同意并向应用程序提供所请求的权限，则会隐藏其图标并显示该页面：

[![](https://p2.ssl.qhimg.com/t01d3f0a7bd56a7c4a7.png)](https://p2.ssl.qhimg.com/t01d3f0a7bd56a7c4a7.png)

如果木马检测到用户试图撤销其管理员权限，则会立即开始关闭电话屏幕，尝试停止用户操作。如果成功撤销权限，则特洛伊木马会重新启动请求管理员权限的周期。如果由于某种原因，当试图撤销设备管理员权限时，SuperService不能关闭屏幕，则特洛伊木马会试图威胁用户。

在运行时，Rotexy会跟踪以下内容：

1.打开并重启手机;

2.终止其运作 – 在这种情况下，它重新启动;

3.应用程序发送短信 – 在这种情况下，手机将切换到静音模式。

### <a name="C%EF%BC%86C%E9%80%9A%E8%AE%AF"></a>C＆C通讯

默认的C＆C地址在Rotexy代码中是硬编的：

[![](https://p3.ssl.qhimg.com/t017bf3bee3a13dbe27.png)](https://p3.ssl.qhimg.com/t017bf3bee3a13dbe27.png)

木马将从设备发送信息的地址以伪随机方式生成。

[![](https://p2.ssl.qhimg.com/t01fb70d8443c1ab6f8.png)](https://p2.ssl.qhimg.com/t01fb70d8443c1ab6f8.png)<br>
木马将有关C＆C服务器的信息以及从受感染设备收集的数据存储在本地SQLite数据库中。

首先，特洛伊木马在管理面板中注册，并从C＆C接收操作所需的信息（SMS拦截模板和将在HTML页面上显示的文本）：

[![](https://p2.ssl.qhimg.com/t01946d522ce3919672.png)](https://p2.ssl.qhimg.com/t01946d522ce3919672.png)

Rotexy拦截所有传入的SMS，并根据从C＆C收到的模板处理它们。此外，当短信到达时，特洛伊木马会将手机置于静音模式并关闭屏幕，以便用户不会注意到新短信已到达。在需要时，特洛伊木马会将SMS发送到指定的电话号码，并使用从截获的消息中收到的信息。（在拦截模板中指定是否必须发送回复，以及应将哪个文本发送到哪个地址。）如果应用程序未收到有关处理传入SMS的规则的说明，则只会将所有SMS保存到本地数据库并将它们上传到C＆C。

除了有关设备的一般信息外，木马还会将所有正在运行的进程和已安装的应用程序列表发送给C＆C。

Rotexy收到相应的命令后会执行进一步的操作：

START，STOP，RESTART – 启动，停止，重启SuperService。

URL – 更新C＆C地址。

MESSAGE – 将包含指定文本的SMS发送到指定的号码。

UPDATE_PATTERNS – 在管理面板中重新注册。

UNBLOCK – 取消阻止电话（撤消应用程序的设备管理员权限）。

UPDATE- 从C＆C下载APK文件并安装它。此命令不仅可用于更新应用程序，还可用于在受感染设备上安装任何其他软件。

CONTACTS – 将从C＆C收到的文本发送给所有用户联系人。这很可能是应用程序的传播方式。

CONTACTS_PRO – 从地址簿中请求联系人的唯一消息文本。

PAGE – 使用也从C＆C或本地数据库收到的User-Agent值从C＆C收到的联系URL。

ALLMSG – 发送C＆C用户收到和发送的所有短信，存储在手机内存中。

ALLCONTACTS – 将所有联系人从手机记忆库发送到C＆C。

ONLINE – 将有关特洛伊木马当前状态的信息发送给C＆C：是否具有设备管理员权限，当前显示的HTML页面，屏幕是打开还是关闭等。

NEWMSG – 将SMS写入设备存储器，其中包含从C＆C发送的文本和发件人编号。

CHANGE_GCM_ID – 更改GSM ID。

BLOCKER_BANKING_START – 显示用于输入银行卡详细信息的网络钓鱼HTML页面。

BLOCKER_EXTORTIONIST_START – 显示勒索软件的HTML页面。

BLOCKER_UPDATE_START – 显示虚假的HTML页面以进行更新。

BLOCKER_STOP – 阻止显示所有HTML页面。

该木马会拦截攻击者传入的SMS，并可以从它们接收以下命令：

“3458” – 撤消应用中的设备管理员权限;

“hi”，“ask” – 启用和禁用移动互联网;

“privet”，“ru” – 启用和禁用Wi-Fi;

“check” – 将文本“install：[device IMEI] ”发送到发送短信的电话号码;

“stop_blocker” – 停止显示所有阻止的HTML页面;

“393838” – 将C＆C地址更改为SMS中指定的地址。



## 如何解锁感染了Rotexy的智能手机

Rotexy没有对SMS的命令产生号码校验。这意味着任何手机发来的指令都会被执行。如果手机被该病毒感染，用户可以：

1.发送“393838”到被感染的手机。Rotexy会将此解释为将C＆C服务器的地址更改为空，并且将停止接收网络犯罪分子指令。

2.然后发送“3458”。这将取消管理员权限。

3.最后，发送“stop_blocker”。此命令将强制Rotexy删除挡住屏幕的网站或页面。

如果在此之后，Rotexy还请求管理员权限，只需以安全模式重启设备，转到应用程序管理器或应用程序和通知，并从设备中删除恶意软件。



## Rotexy攻击的地理位置

98％的Rotexy攻击都针对俄罗斯的用户。该特洛伊木马明确针对使用俄语的用户群体，因此实际上，乌克兰，德国，土耳其和其他几个国家的用户也受到影响。



## IOC

SHA256

```
0ca09d4fde9e00c0987de44ae2ad51a01b3c4c2c11606fe8308a083805760ee7
4378f3680ff070a1316663880f47eba54510beaeb2d897e7bbb8d6b45de63f96
76c9d8226ce558c87c81236a9b95112b83c7b546863e29b88fec4dba5c720c0b
7cc2d8d43093c3767c7c73dc2b4daeb96f70a7c455299e0c7824b4210edd6386
9b2fd7189395b2f34781b499f5cae10ec86aa7ab373fbdc2a14ec4597d4799ba
ac216d502233ca0fe51ac2bb64cfaf553d906dc19b7da4c023fec39b000bc0d7
b1ccb5618925c8f0dda8d13efe4a1e1a93d1ceed9e26ec4a388229a28d1f8d5b
ba4beb97f5d4ba33162f769f43ec8e7d1ae501acdade792a4a577cd6449e1a84
ba9f4d3f4eba3fa7dce726150fe402e37359a7f36c07f3932a92bd711436f88c
e194268bf682d81fc7dc1e437c53c952ffae55a9d15a1fc020f0219527b7c2ec
```

С&amp;C

```
2014–2015:
secondby.ru
darkclub.net
holerole.org
googleapis.link
2015–2016:
test2016.ru
blackstar.pro
synchronize.pw
lineout.pw
sync-weather.pw
2016
freedns.website
streamout.space
2017–2018:
streamout.space
sky-sync.pw
gms-service.info
```
