> 原文链接: https://www.anquanke.com//post/id/85503 


# 【技术分享】渗透测试中的LLMNR/NBT-NS欺骗攻击


                                阅读量   
                                **173283**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：aptive.co.uk
                                <br>原文地址：[https://www.aptive.co.uk/blog/llmnr-nbt-ns-spoofing/](https://www.aptive.co.uk/blog/llmnr-nbt-ns-spoofing/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t01ffbc378dc5552f50.jpg)](https://p1.ssl.qhimg.com/t01ffbc378dc5552f50.jpg)**

****

作者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：140RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**简介 **

LLMNR＆NBT-NS 欺骗攻击是一种经典的内部网络攻击，然而由于一方面了解它的人很少，另一方面在Windows中它们是默认启用的，所以该攻击到现在仍然是有效的。在本文中，我们首先为读者解释什么是LLMNR＆NBT-NS攻击，然后介绍如何通过该攻击进行渗透测试，最后，给出针对该漏洞的防御措施。

<br>

**什么是LLMNR和NetBIOS名称服务器广播？**

当DNS名称服务器请求失败时，Microsoft Windows系统就会通过链路本地多播名称解析（LLMNR）和Net-BIOS名称服务（NBT-NS）试图在本地进行名称解析。    

<br>

**LLMNR和Netbios NS广播有什么问题吗？**

当DNS名称无法解析的时候，客户端就会将未经认证的UDP广播到网络中，询问它是否为本地系统的名称。 事实上，该过程是未被认证的，并会广播到整个网络，从而允许网络上的任何机器响应并声称是目标机器。 

<br>

**什么是LLMNR / NBT-NS中毒攻击？**

通过侦听LLMNR和NetBIOS广播，攻击者可以伪装成受害者（客户端）要访问的目标机器，从而让受害者乖乖交出相应的登陆凭证。在接受连接后，攻击者可以使用Responder.py或Metasploit等工具将请求转发到执行身份验证过程的流氓服务（如SMB TCP：137）。 在身份验证过程中，受害者会向流氓服务器发送用于身份认证的NTLMv2哈希值，这个哈希值将被保存到磁盘中，之后就可以使用像Hashcat或John Ripper（TJR）这样的工具在线下破解，或直接用于 pass-the-hash攻击。

在Windows中，LLMNR和NBT-NS是默认启用的，并且了解这种攻击的人很少，所以我们可以在内部渗透测试中利用该攻击来收集凭据。为此，我们可以在使用其他攻击手段进行测试的过程中，可以让Responder.py一直运行着。 

<br>

**Linux和苹果用户是否受该攻击的影响？**

是的，Linux和苹果客户端也使用类似的协议，即多播DNS（mDNS），该协议会监听TCP：5353端口。有关mDSN的更多信息，请参阅mDNS的维基百科页面。

典型的LLMNR / NetBIOS名称服务器攻击

下图显示了用户因为无法解析服务器名称而遭受这种攻击的典型场景。

[![](https://p0.ssl.qhimg.com/t016b4e687342b7544c.png)](https://p0.ssl.qhimg.com/t016b4e687342b7544c.png)

<br>

**攻击过程详解**

1.	用户发送不正确的SMB共享地址\ SNARE01

2.	DNS服务器响应\SNARE01 – NOT FOUND

3.	客户端进行LLMNR / NBT-NS广播

4.	响应者告诉客户端它是SNARE01并接受NTLMv2哈希值

5.	响应者将错误发送回客户端，因此最终用户如果不是精于此道的话，通常不会引起警觉

<br>

**实例：使用Kali＆Responder.py**

下面，我们通过一个实际例子来演示此攻击的危害性：使用Kali Linux和Responder.py在内部渗透测试期间从网络捕获用户凭据。

从github安装最新版本的responder软件： 



```
root@kali:~# git clone https://github.com/SpiderLabs/Responder.git
Cloning into 'Responder'...
remote: Counting objects: 886, done.
remote: Total 886 (delta 0), reused 0 (delta 0), pack-reused 886
Receiving objects: 100% (886/886), 543.74 KiB | 0 bytes/s, done.
Resolving deltas: 100% (577/577), done.
```

运行Responder.py，使用您的本地接口和IP地址，具体如下所示： 



```
root@kali:~# cd Responder/
root@kali:~/Responder# python Responder.py -i 192.168.210.145 -I eth0
```

这样就可以启动Responder.py了:

[![](https://p0.ssl.qhimg.com/t011aeff268c044423f.png)](https://p0.ssl.qhimg.com/t011aeff268c044423f.png)

Responder.py运行后，我们模拟一个用户键入错误的SMB服务器名称，比如使用SNARE01而不是SHARE01。 

下面，从客户端计算机输入错误SMB服务器名称： 

[![](https://p3.ssl.qhimg.com/t01eb54fab03d847316.png)](https://p3.ssl.qhimg.com/t01eb54fab03d847316.png)

注意：实验室环境中的客户端计算机是Windows 2008 Server R2

在客户端广播不正确的服务器名称的几秒钟时间内，Responder.py就完成了对这个广播请求的应答，并将NTLMv2哈希值写入了硬盘。 

[![](https://p5.ssl.qhimg.com/t011abe6909a0379385.png)](https://p5.ssl.qhimg.com/t011abe6909a0379385.png)

最后一步是破解NTLMv2哈希值，这一步成功与否取决于目标环境中的密码策略的复杂性，这可能需要等待一些时间。 当密码策略是已知的，或者怀疑密码安全性较高的时候，ocl-hashcat将是离线破解的上上之选。由于在测试实验室环境中我们故意使用了不安全的密码，因此这里使用john来破解NTLMv2哈希值： 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0144a5df7ea81f4d62.png)

<br>

**如何保护网络免受LLMNR / NBT-NS中毒攻击**

好消息是：这种攻击是相当容易预防的。注意，为此需要禁用LLMNR和NetBIOS名称服务，如果您只禁用LLMNR的话，则Windows将无法解析的名称转移到NetBIOS名称服务器以进行解析。

<br>

**禁用NetBIOS名称服务**

似乎没有办法使用GPO来禁用NetBIOS名称服务（如果你知道的话，请在回复中告诉我们！），其手册说明如下所示。

1.	请依次打开：控制面板网络和Internet 网络连接

2.	右键单击网络接口，选择属性，双击“Internet Protocol Version 4 TCP/IPv4”

3.	在下一个屏幕上，单击高级，然后选择WINS选项卡

4.	单击“Disable NetBIOS over TCP/IP”旁边的单选按钮

具体操作，请参阅下面的屏幕截图： 

[![](https://p3.ssl.qhimg.com/t01ab7afd97785131f9.png)](https://p3.ssl.qhimg.com/t01ab7afd97785131f9.png)

<br>

**禁用LLMNR**

幸运的是，您可以使用GPO来禁用LLMNR，具体如下所示：

1.	Start =&gt; Run =&gt; gpedit.msc

     打开“Local Computer Policy”=&gt;“Computer Configuration”=&gt;“Administrative Templates”=&gt;“Network”=&gt;“DNS Client”

2.	单击“Turn Off Multicast Name Resolution”，并将其设置为“Enabled”

[![](https://p4.ssl.qhimg.com/t01d5898cd27275c06e.png)](https://p4.ssl.qhimg.com/t01d5898cd27275c06e.png)

<br>

**小结**

本文介绍了一种经典的内部网络攻击方法，虽然这种方法由来已久，但是由于了解这种攻击的人非常少，另外由于相关设置在Windows中是默认启用的，所以到目前为止，这种攻击手段仍然行之有效。 
