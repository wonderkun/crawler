> 原文链接: https://www.anquanke.com//post/id/85381 


# 【木马分析】解密具有完善支付体系的新型勒索软件Spora


                                阅读量   
                                **100042**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：bleepingcomputer.com
                                <br>原文地址：[https://www.bleepingcomputer.com/news/security/spora-ransomware-works-offline-has-the-most-sophisticated-payment-site-as-of-yet/](https://www.bleepingcomputer.com/news/security/spora-ransomware-works-offline-has-the-most-sophisticated-payment-site-as-of-yet/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t010d8f7b8d43d2facc.png)](https://p5.ssl.qhimg.com/t010d8f7b8d43d2facc.png)

**翻译：**[**petale******](http://bobao.360.cn/member/contribute?uid=1431129546)

**预估稿费：200RMB**

**投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿**



**0x00 前言**

今天一个名为Spora的新勒索软件家族浮出水面，其在俄语中是孢子的意思。这款勒索软件最值得注意的是强健的加密机制，离线工作能力和一个非常完善的赎金支付网站。而这个赎金支付网站是我们目前看到的最复杂成熟的一个。

Spora勒索软件首次发现是在Bleeping Computer和卡巴斯基论坛。接下来的分析由Bleeping Computer的Lawrence Abrams提供，以及MalwareHunterTeam和Emsisoft的Fabian Wosar。

<br>

**0x01 Spora通过钓鱼邮件传播**

目前，Spora勒索软件通过钓鱼邮件伪装成发票信息传播。这些电子邮件附带了包含HTA文件的ZIP文件形式的附件。

[![](https://p2.ssl.qhimg.com/t01002dce0bc9ac6c49.png)](https://p2.ssl.qhimg.com/t01002dce0bc9ac6c49.png)

这些HTA（HTML应用程序）文件使用双扩展名，如PDF.HTA或DOC.HTA。在Windows计算机上文件扩展名被隐藏，用户仅能看到第一个扩展名，并且可能被诱骗打开文件。点击任何这些文件将启动Spora勒索软件的进程。

[![](https://p2.ssl.qhimg.com/t010c9804801eff4f43.png)](https://p2.ssl.qhimg.com/t010c9804801eff4f43.png)

当用户运行HTA文件时，它将释放出一个名为close.js的Javascript文件到％Temp％文件夹，该文件将进一步释放可执行文件到同一文件夹并执行。此可执行文件使用随机生成的名称。在我们的测试中是“81063163ded.exe”。此可执行文件是主加密器，并将加密计算机上的文件。

此外，该HTA文件还将提取并执行一个DOCX文件，告诉用户此文件已损坏，并将显示错误。其他恶意软件家族使用相同的伎俩，打开损坏的文件，以诱骗用户认为该文件已在电子邮件传输或下载期间损坏，这样用户就不会对打不开Word文件有异议。

[![](https://p3.ssl.qhimg.com/t019b0a06d2b1841e99.png)](https://p3.ssl.qhimg.com/t019b0a06d2b1841e99.png)

与如今大多数勒索软件不同，Spora可离线运行，不会产生任何网络流量。另一个不同是，Spora并不针对大量的文件格式。当前版本的Spora仅针对具有以下文件扩展名的文件：

```
.xls, .doc, .xlsx, .docx, .rtf, .odt, .pdf, .psd, .dwg, .cdr, .cd, .mdb, .1cd, .dbf, .sqlite, .accdb, .jpg, .jpeg, .tiff, .zip, .rar, .7z, .backup
```

该加密过程的目标为本地文件和网络共享，并且不在文件末尾附加任何额外的文件扩展名，保留文件名的完整性。

为了避免损坏计算机以至阻止重启和其他操作，Spora跳过位于某些文件夹中的文件。默认情况下，Spora不会加密其名称中包含以下字符串的的文件：



```
games
program files (x86)
program files
windows
```



**0x02 Spora具备一流加密**



根据Emisoft的首席技术官和恶意软件研究员Fabian Wosar的说法，Spora似乎在加密程序中没有任何漏洞。整个加密操作看起来非常复杂。Spora遵循这个复杂的过程来创建.KEY文件和创建用于锁定每个文件的加密密钥。

Wosar向Bleeping Computer解释了创建.KEY文件的过程： ”生成RSA密钥，生成AES密钥，使用AES密钥加密RSA密钥，使用可执行文件中的公钥加密AES密钥，将两个加密密钥保存到[.KEY ]文件。”

对于用户的数据文件，加密程序更简单快捷。“生成AES密钥，使用生成的RSA密钥加密AES密钥，使用AES密钥加密文件，将所有内容保存到文件中，”Wosar说。

“要解密，你必须向他们发送你的.KEY文件，”专家补充说。“然后他们可以使用他们的私钥，解密用于加密系统生成的RSA密钥的AES密钥。他们可能将RSA密钥嵌入到他们的解密器，然后发回你的解密器，解密器接着使用该RSA密钥解密文件中的AES密钥并用它解密。 [更新：在我们的文章发布后，Emsisoft发布了一篇博客文章详细介绍加密程序，对这个过程进行更深入的分析。（[http://blog.emsisoft.com/2017/01/10/from-darknet-with-love-meet-spora-ransomware/](http://blog.emsisoft.com/2017/01/10/from-darknet-with-love-meet-spora-ransomware/)）]

下面是硬编码在Spora的随机命名的可执行文件中的公有RSA密钥。



```
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC6COfj49E0yjEopSpP5kbeCRQp
WdpWvx5XJj5zThtBa7svs/RvX4ZPGyOG0DtbGNbLswOYKuRcRnWfW5897B8xWgD2
AMQd4KGIeTHjsbkcSt1DUye/Qsu0jn4ZB7yKTEzKWeSyon5XmYwoFsh34ueErnNL
LZQcL88hoRHo0TVqAwIDAQAB
-----END PUBLIC KEY-----
```

在加密过程结束时，Spora还会运行以下CLI命令，其中包括删除卷映射拷贝服务（shadow volume copies），禁用Windows启动修复（shadow volume copies）以及更改BootStatus策略。

```
process call create "cmd.exe /c vssadmin.exe delete shadows /all /quiet &amp; bcdedit.exe /set `{`default`}` recoveryenabled no &amp; bcdedit.exe /set `{`default`}` bootstatuspolicy ignoreallfailures"
```

加密过程完成后，勒索软件将向用户的桌面和其他文件夹添加赎金备注和.KEY文件。

[![](https://p2.ssl.qhimg.com/t01d80ae91422adc50a.png)](https://p2.ssl.qhimg.com/t01d80ae91422adc50a.png)

此赎金便笺包含简单的说明和感染ID，每个受害者唯一。此ID也用于[Infection-ID] .HTML格式的赎金备注文件名。

感染ID的格式为CCCXX-XXXXX-XXXXX-XXXXX-XXXXX或CCXXX-XXXXX-XXXXX-XXXXX-XXXXX，其中CCC和CC是三个和两个字母的国家代码，X是字母或数字字符。

<br>

**0x03 专业解密服务**

Spora的解密门户目前位于可公开访问的域名Spora.bz。这个域名实际上是一个用TOR网关来隐藏的TOR网站。

用户访问此网站后，须输入其赎金记录中显示的感染ID。 这是他们的Spora解密服务的登录ID。

[![](https://p3.ssl.qhimg.com/t011d896c3e0c2e273d.png)](https://p3.ssl.qhimg.com/t011d896c3e0c2e273d.png)

[![](https://p5.ssl.qhimg.com/t0192d44bf70a36a61f.png)](https://p5.ssl.qhimg.com/t0192d44bf70a36a61f.png)

Spora的解密服务是我们之前没有在任何其他勒索软件解密站点中所看到的。首先，在使用此网站之前，用户必须通过上传.KEY文件将其计算机与解密门户同步。

[![](https://p1.ssl.qhimg.com/t01e3cb32902523b380.png)](https://p1.ssl.qhimg.com/t01e3cb32902523b380.png)

通过同步密钥文件，有关计算机加密的唯一信息随后会上传到支付网站，并与唯一ID相关联。受害者现在可以使用网站上提供的其他选项。此门户网站上的所有内容都整齐排列，并在悬停在某些选项上时显示有用的工具提示。

[![](https://p5.ssl.qhimg.com/t01d701482aa7f22b29.png)](https://p5.ssl.qhimg.com/t01d701482aa7f22b29.png)

该勒索软件另一个独特的地方是可以根据受害者的需要购买不同的服务。这些选项在名为“MyPurchasings”的栏目下，允许用户：

解密他们的文件（目前$ 79）

以后免受Spora感染（目前$ 50）

支付赎金后，删除所有Spora相关文件（目前$ 20）

还原文件（目前为$ 30）

还原2个文件（免费）

这个整洁的设置让我们想起了电子商务网站的付款部分，为每个用户提供不同的付款选项。工具提示和这种模块化支付系统是我们迄今为止在任何其他勒索软件解密服务中都没有看到的。

Spora赎金支付网站似乎也在Twitter上通过其视觉效果给用户留下了深刻的印象。

[![](https://p5.ssl.qhimg.com/t01e53eba923ab4ccc1.png)](https://p5.ssl.qhimg.com/t01e53eba923ab4ccc1.png)

当前版本的解密门户还使用由Comodo颁发的SSL证书，通过HTTPS加密流量。

[![](https://p2.ssl.qhimg.com/t01ed2a59d01d079b1a.png)](https://p2.ssl.qhimg.com/t01ed2a59d01d079b1a.png)

所有Spora付款只能使用比特币。用户将比特币加载到他们的Spora帐户，然后他们可以使用它购买上面提供的任何服务。

根据Emisoft，Spora使用六层模型来组织不同类别的加密文件类型。然后，将有关每个类别的统计信息嵌入到.KEY文件和感染ID中。当受害者上传此文件并将其同步到解密门户时，Spora服务会根据受害者计算机中加密的数据量和类型显示不同的价格。

这使得开发者向商业公司或设计公司收取更多费用，通常计算机中的文件比计算机本身更为贵重。Bleeping Computer统计Spora赎金的费用从79美元到280美元不等。

解密门户还包括一个聊天小部件，允许受害者发送多达五条消息。根据MalwareHunterTeam，这个功能的开发者很有经验。

这个聊天服务让Bleeping Computer确认一旦受害者支付赎金便会收到解密器，可以运行在他们计算机上的任何地方，解密锁定的文件。

<br>

**0x04 Spora目前只针对俄罗斯用户**

根据MalwareHunterTeam，所有Spora上传的ID都是来自俄罗斯的用户。

此外，在我们的测试中发现赎金备注也只有俄语。Spora钓鱼邮件也都是俄语。

[![](https://p5.ssl.qhimg.com/t018411c75ed03fd901.png)](https://p5.ssl.qhimg.com/t018411c75ed03fd901.png)

从我们与不同的安全研究人员谈话中得知，新出现的Spora似乎是由一个专业的勒索软件团队组成，他们在勒索软件方面之前有经验。

去年的1月和2月，全世界都知道了勒索软件家族，如Locky和Cerber，这两个勒索软件在2016年困扰了世界各地的用户，安全公司也没有破解他们的加密。

Spora似乎和Cerber，Locky一样先进稳定，也许我们很快就会看到它从俄罗斯席卷全球。
