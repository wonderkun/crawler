> 原文链接: https://www.anquanke.com//post/id/85753 


# 【APT报告】日本发布来自亚洲某国的APT样本分析


                                阅读量   
                                **120637**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：0day.jp
                                <br>原文地址：[http://blog.0day.jp/p/english-report-of-fhappi-freehosting.html](http://blog.0day.jp/p/english-report-of-fhappi-freehosting.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01df763a7bc6e99fcf.png)](https://p0.ssl.qhimg.com/t01df763a7bc6e99fcf.png)

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**0x00 背景**

VXRL联系我们，有关于一个APT钓鱼邮件，其包含了一个指向位于Geocities网站上的一个恶意软件的下载链接。

样本和证据。

[![](https://p4.ssl.qhimg.com/t0169ce2cb36cd8ade2.png)](https://p4.ssl.qhimg.com/t0169ce2cb36cd8ade2.png)

因为我们认为它是一个APT攻击，所以我们不能披露所有的邮件内容。

在讨论这个恶意软件之后，很多信息不清楚。我检查了特征检测率，结果没有检测到。没有明确的证据，Geocities就不会做任何事，我决定逆向这个APT。

这里是我分析的一些结果，请用它来移除这个恶意软件。

从URL看，这个恶意软件位于Geocities日本网站上，Geocities不是恶意软件或恶意网站，但是一个免费的博客网站。

[![](https://p4.ssl.qhimg.com/t01271c36a4c23dcf1b.png)](https://p4.ssl.qhimg.com/t01271c36a4c23dcf1b.png)

账户“vbiayay1”被用于托管真实的恶意样本。

恶意软件的文件内容是一个编码的VBScript脚本。

[![](https://p0.ssl.qhimg.com/t0139db4c9a9821ab01.png)](https://p0.ssl.qhimg.com/t0139db4c9a9821ab01.png)

这是一个惊讶的时刻，我第一次从Geocities.jp中看见这种类型，并且这个文件看起来非常可疑，因此我决定进一步分析。

VBScript是VisualBasic的一个子集，对于使用VB编程和VBA宏编程的人来说这个非常熟悉。然而VBScript被设计用于在浏览器内执行，且只能调用基本的函数（如文件访问和打印）。微软VBScript能在Windows Script Hsost或者PowerShell中执行。

<br>

**0x01 马拉松式的base64逆向分析**

首先，我手动解码了VBScript脚本，得到下面的代码：

[![](https://p3.ssl.qhimg.com/t01a7cb64e8b2ce353a.png)](https://p3.ssl.qhimg.com/t01a7cb64e8b2ce353a.png)

这段代码通过创建Windows Script Host VBScript对象并运行PowerShell.exe：

```
powershell.exe -w hidden -ep bypass -Enc etc etc.
```

继续解码，得到下面的脚本。

[![](https://p2.ssl.qhimg.com/t014873fb47fe82d36a.png)](https://p2.ssl.qhimg.com/t014873fb47fe82d36a.png)

再一次得到一个VBScript，这个脚本创建一个web客户端对象，且使用代理设置，并从URL下载执行一个文件。

这将打开一个.doc文档。

[![](https://p4.ssl.qhimg.com/t011d48febeb494df4c.png)](https://p4.ssl.qhimg.com/t011d48febeb494df4c.png)

然后，通过使用Invoke-Expression命令在Windows PowerShell下执行一个脚本，并从另一个URL下载执行一个.ps1文件。

让我们再深入ps1文件。

[![](https://p2.ssl.qhimg.com/t010c1cbd7f77178297.png)](https://p2.ssl.qhimg.com/t010c1cbd7f77178297.png)

还是一个base64编码的代码，它使用Invoke-Expression命令来解码。

看起来很像base64编码，因此我们继续手动解码base64.

[![](https://p0.ssl.qhimg.com/t01fdcb555bd8089d98.png)](https://p0.ssl.qhimg.com/t01fdcb555bd8089d98.png)

上面是解码的代码，但是它是另一个base64编码的代码。

然而，他最终揭示了一些感染代码，真实的payload在这个base64代码中。

这段代码揭示了32位和64位的感染向量，它通过一个假的安全更新服务进程隐藏自己，并使用powershell.exe来执行Invoke-Expression解码的base64代码。

好了，再次回到base64解码。

解码得到两个函数和一段shellcode。

[![](https://p1.ssl.qhimg.com/t0109124491b969639d.png)](https://p1.ssl.qhimg.com/t0109124491b969639d.png)

[![](https://p3.ssl.qhimg.com/t010b7e3f6bf9aa010b.png)](https://p3.ssl.qhimg.com/t010b7e3f6bf9aa010b.png)

[![](https://p5.ssl.qhimg.com/t01ab79b3a883546321.png)](https://p5.ssl.qhimg.com/t01ab79b3a883546321.png)

上面的代码很容易理解。它解释了powershell怎么被用来作为一个致命的攻击向量，以便进程注入，并且它都在一个脚本中完成。

<br>

**0x02 拷贝/粘帖 PowerSploit/CodeExecution PoC**

上部分看起来很熟悉，在搜索MalwareMustDie的推特后，发现了PowerSploit/CodeExecution PoC代码。

[![](https://p5.ssl.qhimg.com/t01af3a39a0b26b1980.png)](https://p5.ssl.qhimg.com/t01af3a39a0b26b1980.png)

<br>

**0x03 Shellcode**

这个样本主要的payload是PowerSploit/CodeExection的复制粘帖，shellcode和多层base64编码是这个样本的根本。

为了揭示真实的shellcode，我们已经解码了剩余的base64编码。

```
$Shellcode = [System.Convert]::FromBase64String($Shellcode32)
```

解码完成后，shellcode头分析如下：

[![](https://p5.ssl.qhimg.com/t01631c84ff2d71037e.png)](https://p5.ssl.qhimg.com/t01631c84ff2d71037e.png)

我们可以逆向它，然而需要花费一些时间。

[![](https://p5.ssl.qhimg.com/t01ff39f5388bb6c25b.png)](https://p5.ssl.qhimg.com/t01ff39f5388bb6c25b.png)

结果看起来像我们需要的，XOR，密钥0xe9和字节长度0x2183

[![](https://p0.ssl.qhimg.com/t0166a2be94c4afe7ab.png)](https://p0.ssl.qhimg.com/t0166a2be94c4afe7ab.png)

我用这个shellcode创建了一个PE文件。

将这段shellcode保存在.text节中，并调整入口点为shellcode，因此你能作为一个二进制PE文件执行shellcode。这个方法在分析shellcode时很常用。并且在Unix环境中创建PE文件，还免除感染的风险。

[![](https://p3.ssl.qhimg.com/t015c92f1f76f331a82.png)](https://p3.ssl.qhimg.com/t015c92f1f76f331a82.png)

通过使用gcc或者nasm，编译PE文件。

[![](https://p0.ssl.qhimg.com/t012ab4f81204110fc1.png)](https://p0.ssl.qhimg.com/t012ab4f81204110fc1.png)

因此我们现在能进一步分析代码和恶意行为。

事实证明，样本进行了很多恶意行为操作，shellcode提取受害者的信息并传回C&amp;C服务器。

Payload的详细行为完整成文需要花费很多的时间，在这里我贴出了手稿以展示payload的行为。

[![](https://p2.ssl.qhimg.com/t01e46f4227b8456b9c.png)](https://p2.ssl.qhimg.com/t01e46f4227b8456b9c.png)

<br>

**0x04 Poison Ivy**

Shellcode使用很多系统调用，因此shellcode有点大。

下图是我从列出的DLL调用。

[![](https://p5.ssl.qhimg.com/t012dbf7bdc9314da38.png)](https://p5.ssl.qhimg.com/t012dbf7bdc9314da38.png)

在跟踪分析shellcode的第一个阶段我注意到了这是一个“Poison Ivy”：

[![](https://p5.ssl.qhimg.com/t012140cc443f2d9a0e.png)](https://p5.ssl.qhimg.com/t012140cc443f2d9a0e.png)

如你所见，一个假的userinit.exe进程被创建，且在这个进程中注入恶意代码并执行。受害者将看到一个假的userinit.exe进程在做坏事。这是一个典型的Poison Ivy模式。而且，DLL的组合使用也显示了这种威胁的典型模式。在互斥量名字中时间戳也经常被Poison Ivy使用。

让我们破解更多信息：

[![](https://p5.ssl.qhimg.com/t0118622a81e9961d1a.png)](https://p5.ssl.qhimg.com/t0118622a81e9961d1a.png)

你能看到这个userinit.exe创建Plug1.cat文件。它通过socket做更多事，且通过HKEY_LOCAL_MACHINESYSTEMSetup  SystemSetupInProgress查询PC信息，稍后我们将看到设置的值。

到了这里，毫无疑问这是一个Poison Ivy。

<br>

**0x05 C&amp;C和网络流量**

因为时间限制，让我们忽略一些小细节，主要关注感兴趣的WS2_32.dll。它包含了socket(),gethostbyname(),和connect()调用。这些揭示了主机名和IP地址，及一些次要信息。

IP地址是韩国的拨号IP地址。

[![](https://p4.ssl.qhimg.com/t015ffe36ca1c5bde8f.png)](https://p4.ssl.qhimg.com/t015ffe36ca1c5bde8f.png)

网络/BGP信息：61.97.243.15||4766 | 61.97.243.0/24 | KIXS-AS | KR | kisa.or.kr | KRNIC

因此黑客利用另一个国家作为C&amp;C服务器，我们继续看：

主机名：web.outlooksysm.net

[![](https://p0.ssl.qhimg.com/t01e640902f8beb8a20.png)](https://p0.ssl.qhimg.com/t01e640902f8beb8a20.png)

下面是域名的WHOIS信息：



```
Domain Name: outlooksysm.net
Registry Domain ID: 10632213
Registrar WHOIS Server: grs-whois.cndns.com
Registrar URL: http://www.cndns.com
Updated Date: 2016-05-27T11:24:02Z
Create Date: 2016-05-27T11:19:45Z
Registrar Registration Expiration Date: 2017-05-27T11:19:45Z
Registrar: SHANGHAI MEICHENG TECHNOLOGY INFORMATION DEVELOPMENT CO., LTD.
Registrar IANA ID: 1621
Registrar Abuse Contact Email: domain@cndns.com
Registrar Abuse Contact Phone: +86.2151697771
Reseller: (null)
Domain Status: ok https://icann.org/epp#ok
Registry Registrant ID:
Registrant Name: Liu Ying
Registrant Organization: Liu Ying
Registrant Street: Nan An Shi Jing Hua Lu 88Hao
Registrant City: NanAnShi
Registrant State/Province: FuJian
Registrant Postal Code: 009810
Registrant Country: CN
Registrant Phone : +86.13276905963
Registrant Phone Ext:
Registrant Fax: +86.13276905963
Registrant Fax Ext:
Registrant Email: missliu6@sina.com
```

因此我们知道了黑客来自哪里。

只分析代码不够证据，我需要一种安全的方式来执行PE文件，以获得更多的行为分析。这样我就能捕获到C&amp;C流量。

[![](https://p2.ssl.qhimg.com/t01d63b6923e07cbe00.png)](https://p2.ssl.qhimg.com/t01d63b6923e07cbe00.png)

在流量中，发送了我的PC信息

[![](https://p4.ssl.qhimg.com/t012127653dcfb756e1.png)](https://p4.ssl.qhimg.com/t012127653dcfb756e1.png)

第一个传输的是256字节的数据，看起来很有趣。

[![](https://p0.ssl.qhimg.com/t0107d409a8aa549cd2.png)](https://p0.ssl.qhimg.com/t0107d409a8aa549cd2.png)

因此，通过一些参考发现这256字节的传输流量模式属于Poison Ivy远控。

[![](https://p4.ssl.qhimg.com/t014ac02d52563f2514.png)](https://p4.ssl.qhimg.com/t014ac02d52563f2514.png)

Poison Ivy，也被称为PIVY，是一个RAT，它是一个后门型恶意程序。很多间谍相关的恶意软件在APT中使用它。

<br>

**0x06 总结**

这个APT活动利用很多变种，来使得受害者下载一个恶意的VBScript，其会下载一个二级的.doc文件并打开它。在这之后它静默执行一个PowerSploit攻击以使用在进程内存中运行的Poison Ivy感染受害者电脑。这是个特别的实例，一个修改版的PowerSploit PoC代码被用在APT攻击中，显示了这种攻击的潜在威胁。

这个APT活动利用Geocities网站的多个帐号，使得进行大规模的APT活动成为可能。这种攻击首先在日本发现，且在和我朋友讨论过后，一些研究者把它命名为“Free Hosting（pivoted）APT PowerSploit Poison Ivy”（FHAPPI）。

<br>

**0x07 样本**

我一直都这么做，我将只分享一些样本的哈希值。

一旦我完成了，我将增加一些VT URLs。



```
1.MD5 (Meeting_summary.doc)  = 0011fb4f42ee9d68c0f2dc62562f53e0
2.MD5 (johnts0301.ps1)       = b862a2cfe8f79bdbb4e1d39e0cfcae3a
3.MD5 (Meeting_summary.doc)  = 0011fb4f42ee9d68c0f2dc62562f53e0
4.MD5 (johnts0301.ps1)       = b862a2cfe8f79bdbb4e1d39e0cfcae3a
5.MD5 (johnts0301.wsc)       = 7c9689e015563410d331af91e0a0be8c
6.MD5 (shellcode-bin)        = cb9a199fc68da233cec9d2f3d4deb081
7.MD5 (stupid-shellcode.exe) = 661d4e056c8c0f6804cac7e6b24a79ec
Other samples. (credit: Syota Shinogi)
MD5 (f0921.ps1)            = e798a7c33a58fc249965ac3de0fee67b
```



**0x08 更新**

**找到其他的Geocities账户**

感谢Syota Shinogi的帮助，他进一步研究发现了另一个Geocities账户。

它使用相同的PowerSploit shellcode和蒙古语的doc文件，可能目标是蒙古相关的。

[![](https://p2.ssl.qhimg.com/t01c3eeabc01a4dac0c.jpg)](https://p2.ssl.qhimg.com/t01c3eeabc01a4dac0c.jpg)

[![](https://p2.ssl.qhimg.com/t013785a686ff89449a.jpg)](https://p2.ssl.qhimg.com/t013785a686ff89449a.jpg)

**文件名包含APT信息**

URL和攻击活动相关的信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012e4956a6000febb3.png)

这表明了攻击日期，目标ID和一些版本信息。

**APT恶意文件的删除过程**

在雅虎应急响应组织、JP-CERT/CC和日本其他一些安全机构的帮助下文件被成功删除。

下面是删除的文件。

[![](https://p3.ssl.qhimg.com/t0132b21fed9bad125a.png)](https://p3.ssl.qhimg.com/t0132b21fed9bad125a.png)

**目标蒙古的APT活动**

用户gxpoy6包含了以蒙古为目标的APT攻击的数据。从它开始的时间为去年9月看，感染向量是相同的。许多工件和网络特征已经消失了，但是我们能分析下这个并作进一步对比。

第一个安装脚本没有使用base64混淆。

它使用VBScript但是不编码，且直接执行powershell.exe，然而执行进程自己和上面是相同的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018c123aec12ab7f41.png)

通过powershell.exe执行的编码的命令行有相同的格式。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01821d4c55e7c41111.png)

蒙古语的文档

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017027624bfbbac933.png)

还是使用PowerSploit注入恶意软件到内存中，没有改变。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01244f96c067e7eb7a.png)

Shellcode设计的有点不同

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fd1500df6326a634.png)

蒙古相关的活动也使用了XOR，但是密钥（“0xd4”）不同，字节长度还是0x2183.

[![](https://p2.ssl.qhimg.com/t012e05632cc53a4dce.png)](https://p2.ssl.qhimg.com/t012e05632cc53a4dce.png)

C&amp;C服务器还是在中国，主机名稍后公布。

[![](https://p0.ssl.qhimg.com/t017d906993cec92dcc.png)](https://p0.ssl.qhimg.com/t017d906993cec92dcc.png)

IP/BGP信息：116.193.154.28 | 116-193-154-28.pacswitch.net. | AS4766 | JIULINGQIHANG-CN | CN (Room 413, No.188, Dong Han Men Nan Lu, CHINA)
