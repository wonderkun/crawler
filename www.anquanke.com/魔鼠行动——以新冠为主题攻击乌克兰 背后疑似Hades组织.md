
# 魔鼠行动——以新冠为主题攻击乌克兰 背后疑似Hades组织


                                阅读量   
                                **791887**
                            
                        |
                        
                                                                                    



[![](./img/199621/t013760cfbf121be685.jpg)](./img/199621/t013760cfbf121be685.jpg)

> 威胁情报中心 猎影实验室

Hades组织至今没有一个非常明确的定论，根据已有披露的信息，一种被认为可能来自朝鲜，又有一种说法认为和俄罗斯组织APT28有关。该组织最早发现并披露是因为2017年12月22日对韩国平昌冬奥会的攻击，使用了命名为“Olympic Destroyer”的恶意软件。

后续国外友商又发现了几起Hades的攻击活动。攻击目标包括俄罗斯、乌克兰和其他几个欧洲国家，俄罗斯金融部门、欧洲和乌克兰的生物和化学威胁预防实验室等都是其瞄准的对象。



## 分析

近期，在安恒文件威胁分析平台监测到一起以“COVID-19”（新型冠状病毒肺炎）为主题的恶意攻击，攻击目标指向乌克兰。

这次攻击采用了带有恶意宏代码的伪装文档。标题为“Коронавірусна інфекція COVID-19.doc”（冠状病毒感染COVID-19.doc）。

未启用宏，打开该文档为一个提示页面，

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01218d08a67911af54.png)

启用宏后，显示出文档内容。

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d5ef2ab93f331ea5.png)

恶意宏代码最终会在用户目录下释放“conhost.exe”恶意程序并执行。

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01376578edf225ba71.png)

恶意程序conhost.exe由C#编写，并硬编码了一个回连地址

l  https://cloud-security.ggpht[.]ml

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f4f3aec7cc12af92.png)

这个程序看上去是个远控程序，包含了一些功能如下：

l  收集用户名、机器名、网络适配器等信息

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f262eeeeb10c4843.png)

l  获取进程信息

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01909c67bd71e22ac7.png)

l  键盘记录

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010f957b53bf772d53.png)

l  屏幕信息

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01114e6f02cea4223c.png)

其它行为还有如注册表操作

l  “cmd.exe” /c REG ADD HKCUConsole%SystemRoot^%_system32_cmd.exe /v CodePage /t REG_DWORD /d 65001 /f

似为解决编码问题

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014bb83f363279cd03.png)

l  Socks5指令，似使用socks5

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b6db3c80910230e1.png)

l  Klg指令，似键盘记录功能的启动、停止和更新

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0184ae9041be15afbd.png)

另外还发现了一串比较有意思的字符串

“**Trick: TrickyMouse**”

猜测可能为行动代号。

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e63de9a8764c75c6.png)



## 组织分析

经过一定的分析发现本次活动可能和Hades有一定的关联。具体分析如下。

**宏的相似与关联**

本次攻击的诱饵文档使用了恶意宏代码，

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013ed3141e7dec84ef.png)

通过相似性分析可以发掘出一些相关样本，
<td style="width: 426.1pt; border: 1pt solid black; padding: 0cm 5.4pt;" valign="top" width="568">MD5</td>
<td style="width: 426.1pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="568">e2e102291d259f054625cc85318b7ef5</td>
<td style="width: 426.1pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="568">cd15a7c3cb1725dc9d21160c26ab9c2e</td>
<td style="width: 426.1pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="568">0e7b32d23fbd6d62a593c234bafa2311</td>
<td style="width: 426.1pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="568">4247901eca6d87f5f3af7df8249ea825</td>
<td style="width: 426.1pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="568">e3487e2725f8c79d04ffda6de9612e25</td>
<td style="width: 426.1pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="568">1d0cf431e623b21aeae8f2b8414d2a73</td>
<td style="width: 426.1pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="568">e160ca75a0e8c4bc9177f412b09e7a29</td>
<td style="width: 426.1pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="568">7f327ae9b70d6a2bd48e20c897f7f726</td>

这几个样本都归属于Hades组织，并且使用的宏代码大同小异，基本一致。

以e2e102291d259f054625cc85318b7ef5样本为例，将该样本暂时命名为“Hades样本1”，来和本次攻击样本的宏代码进行比较。

在初步观察下可以发现本次攻击和Hades样本都使用了结构相似的随机的变量名，并且一些字符串都转成了十六进制字符串的形式。

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0173a9a5e217ce39f0.png)

再看上图中，两个样本使用的函数，本次样本为

l  “documenT_oPen”

而Hades样本1中显示的为

l  “MultiPage1_Layout”

表现出明显的结构相似性，这一点也曾被作为Hades的一个重要指标之一。

并且宏的内容和函数行为表现出极大相似性。

再细看一点，Hades样本中将该函数的一部分单独提取出作为一个独立函数，而这次样本连续在了一起，并且使用了一些相同的特性，如使用了相同的Font Color。

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014c47da4493851af5.png)

另外还使用了相同的解码函数

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bee70de29cccd297.png)

可以看到结构基本是一致的。

**文档特性的关联**

Hades的历史样本文档有一些会嵌入Hyperlinks（超链接）形式的文档内容，使诱饵文件更加真实，如
<td style="width: 136.7pt; border: 1pt solid black; padding: 0cm 5.4pt;" valign="top" width="182">MD5</td><td style="width: 289.4pt; border-color: black black black currentcolor; border-style: solid solid solid none; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt;" valign="top" width="386">Hyperlinks</td>

Hyperlinks
<td style="width: 136.7pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="182">0e7b32d23fbd6d62a593c234bafa2311</td><td style="width: 289.4pt; border-color: currentcolor black black currentcolor; border-style: none solid solid none; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt;" valign="top" width="386">lisa.brueggemann@babs.admin[.]ch, https://www.labor-spiez[.]ch/pdf/en/rue/LaborSpiezConvergence2016_02_FINAL.pdf, https://www.labor-spiez[.]ch/pdf/de/rue/Spiez_Convergence_2014_web.pdf</td>

lisa.brueggemann@babs.admin[.]ch, https://www.labor-spiez[.]ch/pdf/en/rue/LaborSpiezConvergence2016_02_FINAL.pdf, https://www.labor-spiez[.]ch/pdf/de/rue/Spiez_Convergence_2014_web.pdf
<td style="width: 136.7pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="182">cd15a7c3cb1725dc9d21160c26ab9c2e</td><td style="width: 289.4pt; border-color: currentcolor black black currentcolor; border-style: none solid solid none; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt;" valign="top" width="386">http://shopster[.]ua/</td>

http://shopster[.]ua/
<td style="width: 136.7pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="182">4247901eca6d87f5f3af7df8249ea825</td><td style="width: 289.4pt; border-color: currentcolor black black currentcolor; border-style: none solid solid none; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt;" valign="top" width="386">http://moz.gov.ua/uploads/1/5534-dn_20180611_1103_dod.pdf</td>

http://moz.gov.ua/uploads/1/5534-dn_20180611_1103_dod.pdf

而本次攻击样本也嵌入了Hyperlinks，
<td style="width: 213.05pt; border: 1pt solid black; padding: 0cm 5.4pt;" valign="top" width="284">MD5</td><td style="width: 213.05pt; border-color: black black black currentcolor; border-style: solid solid solid none; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt;" valign="top" width="284">Hyperlinks</td>

Hyperlinks
<td style="width: 213.05pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="284">74572fba26f5e988b297ec5ea5c8ac1c</td><td style="width: 213.05pt; border-color: currentcolor black black currentcolor; border-style: none solid solid none; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt;" rowspan="2" valign="top" width="284">https://hub.jhu[.]edu/2020/01/23/coronavirus-outbreak-mapping-tool-649-em1-art1-dtd-health/, https://www.ecdc.europa[.]eu/en/novel-coronavirus-china, https://www.who[.]int/emergencies/diseases/novel-coronavirus-2019, https://www.who[.]int/emergencies/diseases/novel-coronavirus-2019, https://www.kmu.gov[.]ua/npas/pro-zahodi-shchodo-zapobigannya-zanesennyu-i-poshirennyu-na-teritoriyi-ukrayini-gostroyi-t030220, https://phc.org[.]ua/kontrol-zakhvoryuvan/inshi-infekciyni-zakhvoryuvannya/koronavirusna-infekciya-covid-19</td>

https://hub.jhu[.]edu/2020/01/23/coronavirus-outbreak-mapping-tool-649-em1-art1-dtd-health/, https://www.ecdc.europa[.]eu/en/novel-coronavirus-china, https://www.who[.]int/emergencies/diseases/novel-coronavirus-2019, https://www.who[.]int/emergencies/diseases/novel-coronavirus-2019, https://www.kmu.gov[.]ua/npas/pro-zahodi-shchodo-zapobigannya-zanesennyu-i-poshirennyu-na-teritoriyi-ukrayini-gostroyi-t030220, https://phc.org[.]ua/kontrol-zakhvoryuvan/inshi-infekciyni-zakhvoryuvannya/koronavirusna-infekciya-covid-19
<td style="width: 213.05pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="284">8d8e5a09fe6878f133b3b81799d84e27</td>

在文档展现方面，Hades的一些样本也会进行一定的伪装，在宏代码未被执行前，文档内容

为带有提示性质的内容或空白文档，在宏代码执行后更多的伪装信息被表露出来。

如Hades的0e7b32d23fbd6d62a593c234bafa2311样本，

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01284cb8bd1a489d00.png)

本次攻击也表现出这种形式。

**进化的****User-Agent****？**

回到释放的载荷来进行观察。

在Olympics攻击活动中发现的第二阶段有效载荷命名为“Gold Dragon”，还有几个样本braveprince、Ghost419和“Gold Dragon”有关联。

在攻击活动中“Gold Dragon”使用的User-Agent为

l  Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0;

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0117c09fc655917d36.png)

本次攻击活动使用的conhost.exe使用的User-Agent为

l  Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; Win64; x64; Trident/6.0; .NET4.0E; .NET4.0C; Microsoft Outlook 15.0.5023; ms-office; MSOffice 15)

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013ce3b0647e5d7299.png)

看上去像是一种版本升级和进化。

综上有一定的理由怀疑这次攻击的背后组织为Hades。



## 更进一步

在关联分析中发现了另外一些样本，如
<td style="width: 266.45pt; border: 1pt solid black; padding: 0cm 5.4pt;" valign="top" width="355">MD5</td><td style="width: 159.65pt; border-color: black black black currentcolor; border-style: solid solid solid none; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt;" valign="top" width="213">载荷远程下载地址</td>

载荷远程下载地址
<td style="width: 266.45pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="355">047a0c1e472ec2f557a84676982465c9</td><td style="width: 159.65pt; border-color: currentcolor black black currentcolor; border-style: none solid solid none; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt;" valign="top" width="213">http://www.momplet[.]com/eco/Pablo/bin.exe</td>

http://www.momplet[.]com/eco/Pablo/bin.exe
<td style="width: 266.45pt; border-color: currentcolor black black; border-style: none solid solid; border-width: medium 1pt 1pt; padding: 0cm 5.4pt;" valign="top" width="355">73874b9b5019f2224b4506f892482760</td><td style="width: 159.65pt; border-color: currentcolor black black currentcolor; border-style: none solid solid none; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt;" valign="top" width="213">http://comproorosilver[.]es/js/bin.exe</td>

http://comproorosilver[.]es/js/bin.exe

也是带有恶意宏代码的伪装文档。这两个样本存在的时间比较早，为2014年10月份。

并且这两个文件的宏代码结构是一致的。

观察发现样本的宏和前面分析的宏代码有一定相似性，以样本

047a0c1e472ec2f557a84676982465c9为例，

使用“Auto_Open”、“Workbook_Open”函数名，当然非常比较常见。

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01edf15e989b8542cd.png)

使用随机的变量名和十六进制处理的字符串，

[![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01210493750100d33e.png)

使用和前面分析的有相同结构的解码函数。

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0103ef3b9b952015ce.png)

不得不怀疑和Hades是否有一定联系。

并且这两个样本还会远程下载恶意载荷并执行。

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01816c90285251d930.png)

下载链接为

l  http://www.momplet[.]com/eco/Pablo/bin.exe

l  http://comproorosilver[.]es/js/bin.exe

这两个网站似为合法的网站，被攻击者利用。在Hades的多个攻击活动中也是利用攻入的合法网站作为C2或分发中转。

这两个文档的作者，都是“facepa1m@live[.]ru”，LanguageCode为Russian。充分说明Id为“facepa1m”的作者来自俄罗斯。

并在Github上发现了一个同ID的用户，仅在2016年创建过一个仓储，内容是空的，不过仓储名称calc引发了一定的联想。

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0173957464fb9542ab.png)

当然并没有充分证据证明这两者是确定关联的。

另外这个ID还出现在了一些比特币相关的网站或论坛，如

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01369b0cbfa11f9d0d.png)

有意思的是，在国外友商卡巴斯基在对OlympicDestroyer攻击活动进行披露时提到Hades组织疑似使用NordVPN和MonoVM的主机服务，NordVPN提供VPN服务，并且是为比特币提供受隐私保护的服务，MonoVM是比特币提供商的VPS。这两个服务都可用于比特币。那么这会是一个巧合么？

根据“facepa1m@live[.]ru”这个作者名称，还可以关联到一个名为Informazioni10221419.doc

的样本（MD5:b86526bed4bf9cb034baff0403617856），根据文件属性，可以看到它的Company属性为“SPecialiST RePack”，

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011f3462e2c33bdf3b.png)

SPecialiST RePack是俄罗斯的数字出版商，用于重新包装软件。据悉以该软件商包装的软件是大量感染文件和产品的来源。这里或许仅是使用了SPecialiST RePack重新包装的Office软件。

另一个值得关注的点，文档的创建时间和最后修改时间是一样的，并且最后修改者为“durdom”，

 [![](./img/199621/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d9c2fe32fa9a78d1.png)

这可能是一个有故事的名字。



## 小结

由于本次攻击载荷中出现的特殊字符串“Trick: TrickyMouse”，我们将这次攻击命名Operation TrickyMouse，即魔鼠行动。

**IOC**

Hash:

53b31f65bb6ced61c5bafa8e4c98e9e8

74572fba26f5e988b297ec5ea5c8ac1c

8d8e5a09fe6878f133b3b81799d84e27

0acecad57c4015e14d9b3bb02b433d3e

2dfb086bc73c259cac18a9cb1f9dbbc8

C2:

cloud-security.ggpht[.]ml
