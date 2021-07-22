> 原文链接: https://www.anquanke.com//post/id/86675 


# 【技术分享】如何使用C#加密攻击载荷来绕过杀毒软件


                                阅读量   
                                **107535**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：linkedin.com
                                <br>原文地址：[https://www.linkedin.com/pulse/bypass-all-anti-viruses-encrypted-payloads-c-damon-mohammadbagher](https://www.linkedin.com/pulse/bypass-all-anti-viruses-encrypted-payloads-c-damon-mohammadbagher)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p1.ssl.qhimg.com/t01d22841b03baf8143.jpg)](https://p1.ssl.qhimg.com/t01d22841b03baf8143.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：130RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

曾经有人问过我，如何绕过所有的杀毒软件？

我的回答是：非常简单。但这是一种秘密技术，大多数渗透测试者或黑客永远都不会与他人共享。他们与我一样有各种各样的理由，但最大的原因在于，一旦技术公开，杀软公司很快就会检测并封杀这种技术。在本文中，我想跟大家分享一种C#编程及加密方法，可以绕过所有杀软。

在介绍具体细节之前，我想先提供一下本文用到的C#源代码。

[http://github.com/DamonMohammadbagher/NativePayloadReversetcp](http://github.com/DamonMohammadbagher/NativePayload_Reverse_tcp)

如果你对渗透测试、Kali Linux以及Metasploit后门载荷比较熟悉，你也掌握一定的编程技术，那么阅读本文后，你可以在互联网上找到更多源代码完成这一任务。

首先：你需要了解反病毒软件以及基于特征的应用（如反病毒软件）。

其次：你需要了解基于Linux的系统以及用于渗透测试的Kali Linux或其他Linux操作系统。

最后：你需要了解Windows编程技术，本文中为C# .Net编程技术。

在本文中，我主要介绍的是C#编程技术，受篇幅所限，我无法在一篇文章里面面面俱到。

请记住：想要绕过安全防御工具（如反病毒软件或者防火墙）的每个渗透测试团队或者红队都需要了解如何在Layer 7层（即应用层）绕过这些应用，这一点在Whitehat或者渗透测试项目、黑帽攻击中非常重要，如果你的团队或者你个人掌握多种杀软绕过技术，显然就掌握足够的先机。另外我想强调的是，这一点实现起来并不困难。

**<br>**

**二、技术细节**

这一部分我会向大家介绍如何一步一步使用C#加密载荷绕过反病毒软件。

**步骤1：**

我在Kali Linux里面制作了一个C类型的后门载荷，其十六进制格式如下图所示。之所以使用“reverse_tcp（反弹型tcp）”载荷，原因在于这种载荷最容易绕过禁止入站连接的防火墙。

[![](https://p0.ssl.qhimg.com/t01603e4c7be34de40f.png)](https://p0.ssl.qhimg.com/t01603e4c7be34de40f.png)

**步骤2：**

你应该使用“异或（XOR）”算法或其他加密算法，至少完成一次载荷加密。

比如，我写了个简单的C#应用，使用加密算法来完成加密，类似的源码还有非常多，我们不用担心代码源。

[![](https://p0.ssl.qhimg.com/t0123f5d45291cb8c1c.png)](https://p0.ssl.qhimg.com/t0123f5d45291cb8c1c.png)

如上图所示，我使用VS.NET 2015来开发C#代码，但所有版本的VS.NET都支持这一代码。

上图中，你会发现一个名为payload.txt的文本文件，这个文件就是我在步骤1中使用msfvenom工具生成的载荷。

在步骤2中，你应该使用payload.txt文件中的内容替换代码中的载荷变量`{`0xfc , ….`}`。

**步骤3：**

程序的输出如下图所示，加密后的载荷也会一同输出。

[![](https://p2.ssl.qhimg.com/t011fd5d168c1ace7b2.png)](https://p2.ssl.qhimg.com/t011fd5d168c1ace7b2.png)

如上图所示，我们的加密载荷开头为“217,119,88….,82,12,210”。现在我们手头上已经有一个加密载荷，你可以在backdoor.exe文件中放心使用这个载荷，因为反病毒软件无法检测这种载荷，只有你掌握了加密或解密载荷的密钥。

**步骤4：**

现在我们需要一段C#代码来在目标主机上执行这段加密载荷。

如下图所示，我使用这一段C#代码来执行加密后的载荷，在源码中，我们需要将Payload_Encrypted变量替换为步骤3中生成的加密后的载荷，此外，我们需要将KEY值替换为步骤2中使用的那个密钥值。

请注意：你在步骤2以及步骤4中使用的KEY值应该一致，因为加密密钥以及解密密钥是同一个密钥。

[![](https://p4.ssl.qhimg.com/t016ea0107d542f8ce9.png)](https://p4.ssl.qhimg.com/t016ea0107d542f8ce9.png)

在这段源码中，我会根据命令行中的参数来生成加密载荷，所以我可以在命令行中输入字符串形式的加密载荷，执行这个exe程序，如下图所示。

执行程序的命令如下：

```
dos C:&gt; backdoor.exe “217,119,88,…….,82,12,210”
```

此时，加密后的载荷会解密并在目标主机的内存中运行，如果上述步骤均顺利完成，那么你就可以在攻击端的Kali Linux系统中收到一个meterpreter会话，如下图所示：

[![](https://p1.ssl.qhimg.com/t01317dc08e1f1af269.png)](https://p1.ssl.qhimg.com/t01317dc08e1f1af269.png)

如下图所示，我的反病毒软件没有检测到这个使用了加密载荷的后门：

[![](https://p3.ssl.qhimg.com/t01df7de57216ef3d99.png)](https://p3.ssl.qhimg.com/t01df7de57216ef3d99.png)

事实上所有的反病毒软件都无法检测这种后门，检测结果如下图所示：

[![](https://p5.ssl.qhimg.com/t01605e6eec6ed02f3d.png)](https://p5.ssl.qhimg.com/t01605e6eec6ed02f3d.png)

其实我开发了一个取证工具，可以实时检测内存中的Meterpreter载荷。使用这种实时扫描工具，你可以在内存中发现这个后门，工具下载链接如下：

[http://github.com/DamonMohammadbagher/MeterpreterPayloadDetection](http://github.com/DamonMohammadbagher/Meterpreter_Payload_Detection)

**<br>**

**三、参考资料**

[1] 使用DNS传输后门绕过反病毒软件。[http://www.linkedin.com/pulse/bypassing-anti-viruses-transfer-backdoor-payloads-dns-mohammadbagher](http://www.linkedin.com/pulse/bypassing-anti-viruses-transfer-backdoor-payloads-dns-mohammadbagher)

[2] 反病毒软件以及基于特征的检测方法的不足（使用NativePayloadReversetcp 2.0版再次绕过反病毒软件）。[http://www.linkedin.com/pulse/antivirus-signature-based-detection-methods-doesnt-mohammadbagher?trk=pulse_spock-articles](http://www.linkedin.com/pulse/antivirus-signature-based-detection-methods-doesnt-mohammadbagher?trk=pulse_spock-articles)

[3] 如何通过扫描内存发现无法检测到的Meterpreter载荷。[http://www.linkedin.com/pulse/detecting-meterpreter-undetectable-payloads-scanning-mohammadbagher?published=t](http://www.linkedin.com/pulse/detecting-meterpreter-undetectable-payloads-scanning-mohammadbagher?published=t)
