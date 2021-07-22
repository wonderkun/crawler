> 原文链接: https://www.anquanke.com//post/id/169646 


# 2018年Windows服务器挖矿木马总结报告


                                阅读量   
                                **265937**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t017d51dce3ed68f5ac.jpg)](https://p1.ssl.qhimg.com/t017d51dce3ed68f5ac.jpg)



## 摘要

2018年，挖矿木马已经成为Windows服务器遭遇的最严重的安全威胁之一。这一年，在挖矿木马攻击趋势由爆发式增长逐渐转为平稳发展的同时，挖矿木马攻击技术提升明显，恶意挖矿产业也趋于成熟，恶意挖矿家族通过相互之间的合作使受害计算机和网络设备的价值被更大程度压榨，合作带来的技术升级也给安全从业者带来更大挑战。2019年，挖矿木马攻击将继续保持平稳，但黑产家族间的合作将更加普遍，“闷声发大财”可能是新一年挖矿木马的主要目标。



## 前言

挖矿木马是一类通过入侵计算机系统并植入挖矿机赚取加密数字货币获利的木马，被植入挖矿木马的计算机会出现CPU使用率飙升、系统卡顿、部分服务无法正常使用等情况。挖矿木马最早在2012年出现，并在2017年开始大量传播。

2018年，挖矿木马已经成为服务器遭遇的最严重的安全威胁之一。360互联网安全中心对挖矿木马进行了深入研究分析和长期攻防对抗，在这一年，360安全卫士平均每日拦截针对Windows服务器的挖矿木马攻击超过十万次，时刻守卫Windows服务器安全。本文将依据我们掌握的数据，总结2018年Windows服务器遭遇的挖矿木马威胁，并对2019年Windows服务器下挖矿木马发展趋势进行分析评估（注：下文提到的“挖矿木马”均指针对Windows服务器的挖矿木马）。

## 第一章 2018年攻击趋势概览

2018年，Windows服务器遭到的挖矿木马攻击呈现先扬后抑再扬的趋势。2018年上半年，针对Windows服务器的挖矿木马呈现稳步上升趋势，并在2018年7月左右达到顶峰。之后挖矿木马攻击强度减弱，部分挖矿木马家族更新停滞，直到2018年12月，WannaMine、Mykings等大型挖矿僵尸网络再次发起大规模攻击，针对Windows服务器的挖矿木马攻击才再次出现上升趋势。2018年针对Windows服务器的挖矿木马攻击趋势如图1所示。

[![](https://p3.ssl.qhimg.com/t013a6834d6ca1b4e6e.png)](https://p3.ssl.qhimg.com/t013a6834d6ca1b4e6e.png)

图1 2018年针对Windows服务器的挖矿木马攻击趋势

在2018年初，挖矿木马攻击的上升趋势是2017年末挖矿木马爆发的延续。2017年12月，“8220”组织使用当时还是0day状态的Weblogic反序列化漏洞（CVE-2017-10271）入侵服务器并植入挖矿木马[[1]](#%E6%B3%A8%E9%87%8A1)，引起一波不小的轰动。之后，更多黑产从业者将目光投向服务器挖矿领域。据360互联网安全中心统计，2018年上半年针对Windows服务器的挖矿木马家族呈逐月上升趋势，最高时每月有20余个成规模的挖矿木马家族。

[![](https://p2.ssl.qhimg.com/t01348eabf446386c7f.png)](https://p2.ssl.qhimg.com/t01348eabf446386c7f.png)

图2 2018年针对Windows服务器的挖矿木马家族数量变化

不过到了2018年下半年，挖矿攻击趋势有所下降，挖矿木马家族数量也仅仅保持稳定，不再呈现类似于上半年的增长趋势。出现这种情况的原因之一，在于2018年下半年披露的Web应用远程代码执行漏洞相比较上半年要少得多，挖矿木马缺少新的攻击入口；另外由于虚拟货币的波动，下半年针对服务器的挖矿木马家族格局基本定型，没有新的大家族产生。从图2可以看出2018年下半年成规模挖矿木马家族数量一直保持30个左右的，并未出现太大增长。

直到2018年年底，各大挖矿木马家族才再次活跃，挖矿木马攻击在沉寂将近半年之后再次呈现上升趋势。其中，“Mykings”家族、“8220”组织与“WannaMine”家族无疑是攻击趋势上升的“主力”。2018年，这三个家族攻击计算机数量占据所有家族攻击计算机总量的87%，到了12月，这个数值上升到了可怕的92%。图4展示了2018年这三个家族攻击计算机数量与其他家族攻击计算机数量总和的比较。关于这几个活跃挖矿家族的细节将在第三章提及。

[![](https://p1.ssl.qhimg.com/t01da5ec0e6fb824de2.png)](https://p1.ssl.qhimg.com/t01da5ec0e6fb824de2.png)

图3 2018年“Mykings”、“8220”组织与“WannaMine”三个家族攻击计算机数量与其他家族对比

因此，2018年成为针对Windows服务器挖矿木马最为鼎盛的一年，进入2019年，如果加密数字货币继续保持目前下滑状态，挖矿木马可能也将随之降温，攻击者也会在更多盈获利方式中寻求平衡。



## 第二章 2018年挖矿木马详解

### <a name="_Toc535015275"></a>一、挖矿木马攻击目标分布

针对Windows服务器的挖矿木马除少部分利用Windows自身漏洞外，更多的是利用搭建在Windows平台上的Web应用或数据库的漏洞入侵服务器。图5展示了2018年针对Windows服务器的挖矿木马攻击目标分布。其中，MsSQL是挖矿木马的最大攻击目标，Weblogic、JBoss、Drupal、Tomcat等Web应用也是挖矿木马重灾区。

[![](https://p4.ssl.qhimg.com/t018e7f6293c925d9ce.png)](https://p4.ssl.qhimg.com/t018e7f6293c925d9ce.png)

图4 2018年针对Windows服务器挖矿木马攻击目标分布

### <a name="_Toc535015276"></a>二、挖矿木马使用漏洞一览

正所谓“工欲善其事，必先利其器”——利用成功率高、操作简便、适用于大规模攻击的漏洞往往受到攻击者青睐。表1展示了2018年挖矿木马入侵Windows服务器所使用的漏洞。攻击者手里往往持有一个能够针对多个平台的漏洞武器库和一个保存有存在漏洞计算机的IP地址的列表，具有僵尸网络性质的挖矿木马会将这个漏洞武器库集成到挖矿木马中，使挖矿木马实现“自力更生”，不具有僵尸网络性质的挖矿木马则会定期对列表中的IP地址发起攻击。一些频繁更新的挖矿木马更是在漏洞POC公开后的极短时间内将其运用在实际攻击中。
<td width="189">攻击平台</td><td width="189">漏洞编号</td><td valign="top" width="189">POC公开与首次出现利用时间差</td>

漏洞编号
<td rowspan="4" width="189">Weblogic</td><td valign="top" width="189">CVE-2017-3248</td><td valign="top" width="189">6个月</td>

CVE-2017-3248
<td valign="top" width="189">CVE-2017-10271</td><td valign="top" width="189">0 天（0day）</td>

0 天（0day）
<td valign="top" width="189">CVE-2018-2628</td><td valign="top" width="189">10天-20天</td>

10天-20天
<td valign="top" width="189">CVE-2018-2894</td><td valign="top" width="189">5个月</td>

5个月
<td rowspan="2" width="189">JBoss</td><td valign="top" width="189">CVE-2010-0738</td><td valign="top" width="189">未知</td>

CVE-2010-0738
<td valign="top" width="189">CVE-2017-12149</td><td valign="top" width="189">20天-30天</td>

20天-30天
<td rowspan="3" width="189">Struts2</td><td valign="top" width="189">CVE-2017-5638</td><td valign="top" width="189">&lt;1个月</td>

CVE-2017-5638
<td valign="top" width="189">CVE-2017-9805</td><td valign="top" width="189">未知</td>

未知
<td valign="top" width="189">CVE-2018-11776</td><td valign="top" width="189">4个月</td>

4个月
<td rowspan="2" width="189">Drupal</td><td valign="top" width="189">CVE-2018-7600</td><td valign="top" width="189">2个月</td>

CVE-2018-7600
<td valign="top" width="189">CVE-2018-7602</td><td valign="top" width="189">2个月</td>

2个月
<td valign="top" width="189">ThinkPHP</td><td valign="top" width="189">-( ThinkPHPv5 GetShell)</td><td valign="top" width="189">10天-15天</td>

-( ThinkPHPv5 GetShell)
<td valign="top" width="189">PHPMyAdmin</td><td valign="top" width="189">-(弱口令爆破)</td><td valign="top" width="189">–</td>

-(弱口令爆破)
<td valign="top" width="189">PHPStudy</td><td valign="top" width="189">-(弱口令爆破)</td><td valign="top" width="189">–</td>

-(弱口令爆破)
<td valign="top" width="189">Spring Data Commons</td><td valign="top" width="189">CVE-2018-1273</td><td valign="top" width="189">未知</td>

CVE-2018-1273
<td rowspan="2" width="189">Tomcat</td><td valign="top" width="189">-(弱口令爆破)</td><td valign="top" width="189">–</td>

-(弱口令爆破)
<td valign="top" width="189">CVE-2017-12615</td><td valign="top" width="189">未知</td>

未知
<td valign="top" width="189">MsSQL</td><td valign="top" width="189">-(弱口令爆破)</td><td valign="top" width="189">–</td>

-(弱口令爆破)
<td valign="top" width="189">MySQL</td><td valign="top" width="189">-(弱口令爆破)</td><td valign="top" width="189">–</td>

-(弱口令爆破)
<td rowspan="2" width="189">Windows Server</td><td valign="top" width="189">-(弱口令爆破)</td><td valign="top" width="189">–</td>

-(弱口令爆破)
<td valign="top" width="189">CVE-2017-0143</td><td valign="top" width="189">&lt;1个月</td>

&lt;1个月

表1 2018年挖矿木马入侵Windows服务器所使用的漏洞

### <a name="_Toc535015277"></a>三、挖矿木马使用的攻击技术

<a name="_Toc535015278"></a>**（一）横向移动**

横向移动指的是：木马在入侵计算机之后，以该计算机作为傀儡机，攻击局域网中的其他机器并控制这些机器。具有僵尸网络性质的挖矿木马家族常会利用Windows系统自身漏洞攻击局域网中的其他机器，并在其他机器中植入挖矿木马。在横向移动攻击武器的选择上，“永恒之蓝”漏洞攻击武器是大部分挖矿木马家族的首选，而横向渗透神器Mimikatz也被WannaMine等挖矿木马家族所使用。在这些家族的横向渗透中，Mimikatz只是作为“永恒之蓝”漏洞攻击武器的备选方案，可见攻击者更追求稳定性和使用上的简便，而不愿将上手难度高的Mimikatz放在首位。

[![](https://p3.ssl.qhimg.com/t01cd8ed4ffb2c852e9.png)](https://p3.ssl.qhimg.com/t01cd8ed4ffb2c852e9.png)

图5 使用“永恒之蓝”漏洞攻击武器与使用Mimikatz的挖矿木马家族数量对比

<a name="_Toc535015279"></a>**（二）Living off the land**

Living off the land直译是“靠山吃山，靠水吃水”，在恶意攻击中指的是借助系统中已存在的应用程序或工具完成攻击。上文提到针对Windows服务器的挖矿木马大多数通过Web应用或系统的缺陷入侵计算机，而这些缺陷大多数只允许在远程计算机上执行任意命令而非任意代码，因此攻击者需要借助系统中已存在的应用程序或工具下载载荷，实现挖矿木马的植入。表2展示了被挖矿木马借力的合法应用程序。
<td valign="top" width="284">应用程序名称</td><td valign="top" width="284">被挖矿木马滥用的功能</td>

被挖矿木马滥用的功能
<td valign="top" width="284">cmd.exe</td><td valign="top" width="284">执行载荷</td>

执行载荷
<td valign="top" width="284">PowerShell.exe</td><td valign="top" width="284">下载载荷，执行载荷</td>

下载载荷，执行载荷
<td valign="top" width="284">Regsvr32.exe</td><td valign="top" width="284">执行载荷</td>

执行载荷
<td valign="top" width="284">Certutil.exe</td><td valign="top" width="284">下载载荷，解码载荷</td>

下载载荷，解码载荷
<td valign="top" width="284">bitsadmin.exe</td><td valign="top" width="284">下载载荷，执行载荷，持续驻留</td>

下载载荷，执行载荷，持续驻留
<td valign="top" width="284">wscript.exe</td><td valign="top" width="284">下载载荷，执行载荷</td>

下载载荷，执行载荷
<td valign="top" width="284">cscript.exe</td><td valign="top" width="284">下载载荷，执行载荷</td>

下载载荷，执行载荷
<td valign="top" width="284">mshta.exe</td><td valign="top" width="284">执行载荷</td>

执行载荷
<td valign="top" width="284">wmic.exe</td><td valign="top" width="284">执行载荷</td>

执行载荷

表2 被挖矿木马借力的合法应用程序

图7则展示了针对Windows平台挖矿木马家族对这些合法应用程序的使用情况。Powershell这个功能强大的工具是攻击者最青睐的，而诸如Regsvr32.exe、mshta.exe这类能够执行存放在攻击者服务器的恶意代码的应用程序也被大量挖矿木马所使用。

[![](https://p4.ssl.qhimg.com/t017e38af8e8367cb75.png)](https://p4.ssl.qhimg.com/t017e38af8e8367cb75.png)

图6 针对Windows平台挖矿木马家族滥用合法应用程序的情况

<a name="_Toc535015280"></a>**（三）Fileless**

Fileless也叫“无文件攻击”技术，即攻击者在不释放文件的情况下实施攻击。攻击者一般通过在内存中加载恶意代码实现“无文件攻击”。Fileless本身是在Living off the land的范畴中，由于针对Windows服务器的挖矿木马频繁使用该技术，故此在文章中将其提取出来另外讨论。

在针对Windows服务器的挖矿木马家族中，WannaMine是“无文件攻击”技术的集大成者。WannaMine利用漏洞入侵服务器后，会借助PowerShell应用程序在内存中完成挖矿木马运行、横向渗透、更新自身等多项工作。图8是WannaMine家族所使用的无文件攻击技术图解[[2]](#%E6%B3%A8%E9%87%8A2)。

[![](https://p5.ssl.qhimg.com/t01293f0bfb1ad0cf27.png)](https://p5.ssl.qhimg.com/t01293f0bfb1ad0cf27.png)

图7 WannaMine家族所使用的无文件攻击技术图解

2018年11月，Mykings僵尸网络使用CVE-2015-7768攻击KONICA MINOLTA FTP时也使用了“无文件”攻击技术。Mykings将加密后的载荷隐藏在PowerShell内存中，当扫描到存在漏洞的KONICA MINOLTA FTP时就解密载荷并向其发送带有载荷的漏洞利用代码。

[![](https://p1.ssl.qhimg.com/t0148d3d63bf3e2edf8.png)](https://p1.ssl.qhimg.com/t0148d3d63bf3e2edf8.png)

图8 Mykings家族攻击KONICA MINOLTA FTP时所使用的无文件攻击技术图解

“无文件攻击”技术的优势在于能够躲避杀毒软件的静态扫描，劣势在于现阶段过分依赖PowerShell强大的功能，一旦PowerShell被封锁，攻击者将很难找到替代品。

<a name="_Toc535015281"></a>**（四）代码混淆技术**

代码混淆的目的是为了逃避杀毒软件的静态扫描，并增加样本分析人员的分析难度。对PE文件格式的木马加上诸如VMP这类的强壳已经是老生常谈了。2018年挖矿木马将混淆魔爪伸向了PowerShell脚本、JS脚本、hta文件等非PE文件，这些文件不一定会在受害机器上出现，更多的是在内存中执行，攻击者此举纯粹是为了给样本分析人员增加难度。

Invoke-DOSfuscation项目[[3]](#%E6%B3%A8%E9%87%8A3)最受挖矿木马青睐，图10和图11分别是WannaMine家族和Mykings家族使用Invoke-DOSfuscation对PowerShell代码进行混淆的例子。这类连编辑器都无法正常高亮的混淆代码给样本分析人员带来极大的挑战。

[![](https://p4.ssl.qhimg.com/t014f4ed69f6aa2d127.png)](https://p4.ssl.qhimg.com/t014f4ed69f6aa2d127.png)

图9 WannaMine家族使用Invoke-DOSfuscation进行混淆的例子

[![](https://p1.ssl.qhimg.com/t0162b1294c3bb4df83.png)](https://p1.ssl.qhimg.com/t0162b1294c3bb4df83.png)

图10 Mykings家族使用Invoke-DOSfuscation进行混淆的例子

### <a name="_Toc535015282"></a>四、挖矿木马收益分析及未来获利方式预测

2018年全球加密数字货币价格呈现走跌的趋势，大部分挖矿木马选择的币种——门罗币，在2018年缩水了超过九成。从最高时的1个门罗币兑3500元人民币降到现在的1个门罗币兑300元人民币。

[![](https://p4.ssl.qhimg.com/t016fb10e01e9fb3015.png)](https://p4.ssl.qhimg.com/t016fb10e01e9fb3015.png)

图11 门罗币价格走势，红框中为2018年门罗币价格走势[[4]](#%E6%B3%A8%E9%87%8A4)

挖矿是一种几乎零成本的获利方式，因此门罗币价格的大幅缩水对挖矿木马攻击趋势的影响有限。表3展示了各个针对Windows服务器的成规模挖矿家族钱包地址和获利情况。可以看出，即使加密数字货币价格狂跌，一些大型挖矿家族仍然能够获得不错的收益。以WannaMine家族为例，若该家族以当前价格将持有的门罗币兑换成人民币，依然可以收益将近150万人民币，而实际收益必然大于150万人民币。
<td valign="top" width="357">钱包地址</td><td valign="top" width="132">加密数字货币数量</td><td valign="top" width="80">家族</td>

家族
<td valign="top" width="357">43Qof2iF1QV8NuGEDhxU3vBapovcxGVrYaNu35oMA58JXx1wx5nwEdZMe2DEsRVM1DV3vj5prS9moK8hAebH4ewgV7JDmDb</td><td width="132">2879XMR</td><td rowspan="6" width="80">WannaMine</td>

2879XMR


<td valign="top" width="357">44XYTPbEG7pg17grFsFdd3KdPaiJzNBNCZX1RqkvDuBmKwcLq1QVwhaCzrZctw15zrDPGFhQWVAWsi47g3p5dyNY21jUCj1</td><td width="132">2015XMR</td>

2015XMR
<td valign="top" width="357">4B9oDLDgeLnWnE9y2snHC3N2fX5CnBFMvQw1hgyZkhd8Vfg3nVAzJ2mVND9eryd5ZmauBredcbxtLMU35t346K6cPPQt7Bt</td><td width="132">157XMR</td>
<td valign="top" width="357">41mmoPVT1EFTaq3R4RpWEWiFJufAqJk8bAHBheSDVSGLgorjJHTNemdNg3kocA2Hj66Cve8B9fVEuYY6ztctk1bAETqsnNk</td><td width="132">31XMR</td>
<td valign="top" width="357">49kWWHdZd5NFHXveGPPAnX8irX7grcNLHN2anNKhBAinVFLd26n8gX2EisdakRV6h1HkXaa1YJ7iz3AHtJNK5MD93z6tV9H</td><td width="132">53XMR</td>
<td valign="top" width="357">4836J714oRpM9zdt7PZGmpChufqSEAFW8RgEMhu4tpGZKiFtogAiPY85GW9tWD9zKEi9XmB4Prw55M5fjjTgrhVhSDLLkFZ</td><td width="132">12XMR</td>
<td valign="top" width="357">44FaSvDWdKAB2R3n1XUZnjavNWwXEvyixVP8FhmccbNC6TGuCs4R937YWuoewbbSmMEsEJuYzqUwucVHhW73DwXo4ttSdNS</td><td width="132">3XMR</td><td width="80">Zombieboy</td>

Zombieboy
<td valign="top" width="357">41e2vPcVux9NNeTfWe8TLK2UWxCXJvNyCQtNb69YEexdNs711jEaDRXWbwaVe4vUMveKAzAiA4j8xgUi29TpKXpm3zKTUYo</td><td width="132">545XMR</td><td rowspan="3" width="80">“8220”组织</td>

“8220”组织
<td valign="top" width="357">4AB31XZu3bKeUWtwGQ43ZadTKCfCzq3wra6yNbKdsucpRfgofJP3YwqDiTutrufk8D17D7xw1zPGyMspv8Lqwwg36V5chYg</td><td width="132">203XMR</td>
<td valign="top" width="357">46E9UkTFqALXNh2mSbA7WGDoa2i6h4WVgUgPVdT9ZdtweLRvAhWmbvuY1dhEmfjHbsavKXo3eGf5ZRb4qJzFXLVHGYH4moQ</td><td width="132">11XMR</td>
<td valign="top" width="357">48ojQAPbQCY5j75Hshe1mXKSAe3db6NVRAxsiMxS7rMNcEGE1mKGW1eETRamd1cKgRHCtqdTnEUu6NEKKSGXVugN9q2WVM8</td><td width="132">43XMR</td><td rowspan="4" width="80">KoiMiner</td>

KoiMiner
<td valign="top" width="357">463tGbooc85VubSo9TjhjLegtVvBQD6qPVJ3LxDoNrtKexAqcyDkoqm9p32MrDoMWcSmWz41EKbxL3AKPJyCjCmcTPZ96XQ</td><td width="132">16XMR</td>
<td valign="top" width="357">47Uvt85TgZzHkveaTed69jhY4CSN8334BUufUtmaoLSNJadf2BoTtroHm5evYqQy4NJeyVBYYtGK8SHSAtFSiW6aDztDs9j</td><td width="132">46XMR</td>
<td valign="top" width="357">44873Xameckc4wR21AdrM5fnoFHKZJSVj6cBADTgFTrEEN94jP2XfQZ74PMRiqoYHnBu2cCe32wLx7gKHnQpfFqCLb6Ryn2</td><td width="132">19XMR</td>
<td valign="top" width="357">43BEKp4t8km3wEBasxmPMcV5n5XPPjRN4VcicaSwKZkTHxKzc4hTYwd3tyqR8SLZahfuSsTeJEG3fcEMnX3jA1F86iao1GU</td><td width="132">0.32XMR</td><td width="80">NSASrvanyMinner</td>

NSASrvanyMinner
<td valign="top" width="357">4AN9zC5PGgQWtg1mTNZDySHSS79nG1qd4FWA1rVjEGZV84R8BqoLN9wU1UCnmvu1rj89bjY4Fat1XgEiKks6FoeiRi1EHhh</td><td width="132">157XMR</td><td width="80">bulehero</td>

bulehero
<td valign="top" width="357">49bjBwYN1YVcn6iJv7pTboVUPKT7Se1cZVqWKd7axs2zJoai68dYg8uWoapnxLNDyWNGTvsMbgvesbBctw1SW2czSBGB6R3</td><td width="132">13XMR</td><td width="80">JavaeMiner（未披露）</td>

JavaeMiner（未披露）
<td valign="top" width="357">45UGVCbZAtzePzujSn2GYHPrciq8ZoBH1MXaA7nNiQa5GrvvomXuinGHnXTBgv21NmXUrNDxKXJwZb8hTQK4Hj1VCkCvCsH</td><td width="132">3XMR</td><td width="80">WmicMiner（未披露）</td>

WmicMiner（未披露）
<td valign="top" width="357">44qLwCLcifP4KZfkqwNJj4fTbQ8rkLCxJc3TW4UBwciZ95yWFuQD6mD4QeDusREBXMhHX9DzT5LBaWdVbsjStfjR9PXaV9L</td><td width="132">58XMR</td><td rowspan="2" width="80">MassMiner</td>

MassMiner
<td valign="top" width="357">49Rocc2niuCTyVMakjq7zU7njgZq3deBwba3pTcGFjLnB2Gvxt8z6PsfEn4sc8WPPedTkGjQVHk2RLk7btk6Js8gKv9iLCi</td><td width="132">928XMR</td>
<td valign="top" width="357">47Tscy1QuJn1fxHiBRjWFtgHmvqkW71YZCQL33LeunfH4rsGEHx5UGTPdfXNJtMMATMz8bmaykGVuDFGWP3KyufBSdzxBb2</td><td width="132">&gt;2000XMR（矿池已禁止查询该钱包）</td><td rowspan="3" width="80">Mykings</td>

Mykings
<td valign="top" width="357">41xDYg86Zug9dwbJ3ysuyWMF7R6Un2Ko84TNfiCW7xghhbKZV6jh8Q7hJoncnLayLVDwpzbPQPi62bvPqe6jJouHAsGNkg2</td><td width="132">11MXR</td>
<td valign="top" width="357">47Tscy1QuJn1fxHiBRjWFtgHmvqkW71YZCQL33LeunfH4rsGEHx5UGTPdfXNJtMMATMz8bmaykGVuDFGWP3KyufBSdzxBb2</td><td width="132">&gt;6000XMR（矿池已禁止查询该钱包）</td>

表3 各挖矿家族钱包地址的获利情况

不过某些规模较大的挖矿家族依然在寻求其他的获利方式以最大化利用其控制的僵尸机器的价值。比如2018年6月，WannaMine家族在一次更新中增加了DDoS模块。该DDoS模块代码风格、攻击手法与WannaMine家族之前的情况大不相同，DDoS模块的载荷下载地址在2018年6月之前曾经被其他家族所使用[[5]](#%E6%B3%A8%E9%87%8A5)。不难推测，WannaMine可能与其他黑产家族进行合作，摇身一变成为“军火商”为其他黑产家族定制化恶意程序。

[![](https://p1.ssl.qhimg.com/t01aef029d4b46800fd.png)](https://p1.ssl.qhimg.com/t01aef029d4b46800fd.png)

图12 WannaMine的DDoS模块中所连接的载荷下载地址d4uk.7h4uk.com曾被其他家族使用

无独有偶，另一大挖矿家族Mykings也在2018年实现了身份的转换。2018年11月，Mykings与“暗云”木马家族合作，向受控计算机中植入“暗云”木马，功能包括但不限于挖矿、锁首页、暗刷和DDoS[[6]](#%E6%B3%A8%E9%87%8A6)。图14展示了Mykings僵尸网络与“暗云”木马合作后的攻击流程。

[![](https://p5.ssl.qhimg.com/t012b9b9ec60196c439.png)](https://p5.ssl.qhimg.com/t012b9b9ec60196c439.png)

图13 Mykings僵尸网络与“暗云”木马合作后的攻击流程

可以预测，2019年将涌现更多这类的合作。挖矿木马家族除了往僵尸机中植入挖矿木马获利外，还会向其他黑产家族提供成熟的漏洞攻击武器与战术，或者将已控制的僵尸机出售给其他黑产家族。而类似“暗云”木马家族这类对黑产获利方式、获利渠道较为熟悉的家族则购买挖矿木马家族出售的僵尸机，或者与挖矿木马家族共同开发定制木马，谋求挖矿以外的利益最大化。



## 第三章 2018年挖矿木马家族典型

### [[7]](#%E6%B3%A8%E9%87%8A7)、PowerGhost[[8]](#%E6%B3%A8%E9%87%8A8)）

[![](https://p5.ssl.qhimg.com/t018f617b69160ca8cf.png)](https://p5.ssl.qhimg.com/t018f617b69160ca8cf.png)

图14 WannaMine家族典型的攻击流程

WannaMine是2018年最活跃的挖矿木马家族之一，该家族主要针对搭建Weblogic的服务器，也攻击PHPMyadmin、Drupal等Web应用。当WannaMine入侵服务器之后，使用“永恒之蓝”漏洞攻击武器或Mimikatz进行横向渗透，将挖矿木马植入位于同一局域网的其他计算机中。WannaMine是“无文件”攻击技术的集大成者，在其绝大多数版本中都通过PowerShell应用程序将挖矿木马加载到内存中执行，未有文件“落地”。

WannaMine更新频繁，不仅定期更换载荷下载URL，且一旦有新的Web应用漏洞POC公开，WannaMine就会在第一时间将POC武器化。图16展示了2018年WannaMine家族的攻击趋势，年初的上涨来源于WannaMine家族第一次使用Weblogic反序列化漏洞（CVE-2017-10271）对服务器进行攻击[[9]](#%E6%B3%A8%E9%87%8A9)，而2018年底的突然上涨是WannaMine在更新停滞数月之后再次活跃所造成的。不难推测，WannaMine攻击者手中保存有存在漏洞的机器列表，以实现在短时间内控制大量机器的目的。

[![](https://p5.ssl.qhimg.com/t01de324367769c1003.png)](https://p5.ssl.qhimg.com/t01de324367769c1003.png)

图15 WannaMine家族2018年攻击趋势

### [[10]](#%E6%B3%A8%E9%87%8A10)（隐匿者[[11]](#%E6%B3%A8%E9%87%8A11)）

[![](https://p3.ssl.qhimg.com/t0179f7f156e445adae.png)](https://p3.ssl.qhimg.com/t0179f7f156e445adae.png)

图16 Mykings家族典型的攻击流程

Mykings家族最早可以追溯到2014年，在2017年被多家安全厂商披露，至今仍然处在活跃状态中。Mykings家族拥有一套成熟的弱口令扫描与爆破体系，能够爆破MsSQL、Telnet、RDP、CCTV等系统组件或设备，其爆破模块除了复用Mirai僵尸网络和Masscan扫描器的部分代码外，还集成了内容丰富的弱口令字典以及针对MsSQL的多种命令执行方式。在获利方式上，Mykings家族不仅仅局限于通过挖矿获利，也通过与其他黑产家族合作完成锁首页、DDoS等工作。

2018年，Mykings家族攻击趋势较为稳定。2018年上半年Mykings家族呈平稳上升趋势，年中时曾经对MsSQL发起一次大规模的爆破攻击，在这次攻击中Mykings家族使用新的载荷下载地址，并尝试使用“白利用”技术对抗杀毒软件，也是在这一波攻击之后，Mykings家族控制的僵尸机数量大幅上涨[[12]](#%E6%B3%A8%E9%87%8A12)。与WannaMine家族相似，Mykings家族在2018年下半年稍显沉寂，直到2018年11月与“暗云”家族合作后才有所改观。

[![](https://p2.ssl.qhimg.com/t013410ac1e3642985d.png)](https://p2.ssl.qhimg.com/t013410ac1e3642985d.png)

图17 Mykings家族2018年攻击趋势

### [[13]](#%E6%B3%A8%E9%87%8A13)

[![](https://p1.ssl.qhimg.com/t01f63e9784a5448fad.png)](https://p1.ssl.qhimg.com/t01f63e9784a5448fad.png)

图18 “8220”组织典型的攻击流程

2017年11月，一攻击组织使用当时还是0day状态的Weblogic反序列化漏洞（CVE-2017-10271）入侵服务器植入挖矿木马，这是第一次被公开披露的使用0day漏洞入侵服务器植入挖矿木马的案例，而这个攻击组织就是“8220”组织。

“8220”组织传播的挖矿木马攻击流程十分简单，即通过Web应用漏洞入侵Windows服务器之后通过PowerShell下载挖矿木马执行，再通过计划任务在计算机中持续驻留。不同于WannaMine家族和Mykings家族，“8220”组织传播的挖矿木马并不具有蠕虫传播的功能，但是该组织活跃时依然能够成功入侵大量Windows服务器。可以断定，“8220”组织手中必然保存着一个存在漏洞的服务器IP地址的列表，使该组织能够定期对大量服务器实施打击。

“8220”组织在2018年年初较为活跃，主要原因在于2018年年初披露的Web应用漏洞POC数量相比较其他时候要多得多。之后随着披露的Web应用漏洞POC数量的减少，“8220”组织也相对沉寂，不过到了2018年12月末，“8220“组织使用包括Github、bitbucket在内的代码托管平台存储载荷，开启新一波服务器入侵攻势。

[![](https://p4.ssl.qhimg.com/t01e5dc7c2758180df3.png)](https://p4.ssl.qhimg.com/t01e5dc7c2758180df3.png)

图19 “8220”组织2018年攻击趋势

### [[14]](#%E6%B3%A8%E9%87%8A14)

[![](https://p5.ssl.qhimg.com/t01eb22aae6fa9c6cda.png)](https://p5.ssl.qhimg.com/t01eb22aae6fa9c6cda.png)

图20 bulehero家族典型的攻击流程

bulehero家族最早出现于2018年初，该家族最初并非使用bulehero.in这个域名作为载荷下载URL，而是直接使用IP地址173.208.202.234。诞生初期的bulehero家族规模并不大，直到2018年7月，该家族所构建的僵尸网络才逐渐成型。2018年12月，ThinkPHP v5被曝存在远程代码执行漏洞，bulehero是第一个使用该漏洞入侵服务器的家族，而这次入侵也使bulehero家族控制的僵尸机器数量暴涨[[15]](#%E6%B3%A8%E9%87%8A15)。

[![](https://p0.ssl.qhimg.com/t01abbd29528632797f.png)](https://p0.ssl.qhimg.com/t01abbd29528632797f.png)

图21 bulehero家族2018年攻击趋势

### [[16]](#%E6%B3%A8%E9%87%8A16)

[![](https://p4.ssl.qhimg.com/t011e7e365be6e771ef.png)](https://p4.ssl.qhimg.com/t011e7e365be6e771ef.png)

图22 MassMiner家族典型的攻击流程

MassMiner家族以其使用Masscan扫描器得名。该家族主要活跃于2018年上半年，通过Web应用漏洞和MsSQL弱口令爆破入侵Windows服务器，并将受害机器转化为傀儡机对互联网中的计算机进行扫描和入侵，构建僵尸网络。

进入2018年下半年，MassMiner几乎消失。有趣的是，MassMiner所使用的门罗币钱包地址共收入将近1000个门罗币，这明显与MassMiner家族构建的僵尸网络规模不符。可见MassMiner家族必然还存在一个尚未被披露的分支，这个分支为该家族带来绝大多数的收益。

[![](https://p0.ssl.qhimg.com/t01574d39eca9ff8bb2.png)](https://p0.ssl.qhimg.com/t01574d39eca9ff8bb2.png)

图23 MassMiner家族2018年攻击趋势

### <a name="_Toc535015289"></a>六、ArcGISMiner

[![](https://p5.ssl.qhimg.com/t01399c2868147406e7.png)](https://p5.ssl.qhimg.com/t01399c2868147406e7.png)

图24 ArcGISMiner家族典型的攻击流程

这是一个尚未有专门报告披露的挖矿木马家族，也是挖矿木马中的“异类”——ArcGISMiner只在几个时间段攻击服务器，每次攻击持续不会超过2个小时，并且两次攻击间隔最少为6天。ArcGISMiner主要针对提供位置服务的ArcGIS、exLive等Web应用，入侵服务器后通过反射dll注入执行挖矿。
<td valign="top" width="284">攻击时间</td><td valign="top" width="284">载荷下载地址</td>

载荷下载地址
<td valign="top" width="284">2018年5月17日</td><td valign="top" width="284">hxxp://121.41.33.131:8000</td>

hxxp://121.41.33.131:8000
<td valign="top" width="284">2018年6月6日</td><td valign="top" width="284">hxxp://121.41.33.131:8000</td>

hxxp://121.41.33.131:8000
<td valign="top" width="284">2018年8月23日</td><td valign="top" width="284">hxxp://121.41.33.131:8000</td>

hxxp://121.41.33.131:8000
<td valign="top" width="284">2018年8月28日</td><td valign="top" width="284">hxxp://120.27.244.75:53</td>

hxxp://120.27.244.75:53
<td valign="top" width="284">2018年10月19日</td><td valign="top" width="284">hxxp://121.41.33.131:8000</td>

hxxp://121.41.33.131:8000
<td valign="top" width="284">2018年11月1日</td><td valign="top" width="284">hxxp://status.chalive.cn</td>

hxxp://status.chalive.cn

表4 ArcGISMiner攻击时间点与载荷下载地址



## 第四章 总结

2018年是挖矿木马由兴起到稳定发展的一年，这一年中有许多新家族涌现，也有许多家族在竞争中消亡，整体攻击趋势转向平稳。毫无疑问的是，在这一年挖矿木马变得更加成熟，幕后操纵者也不再是“野路子”黑客，而是商业化程度极高的黑产组织。黑产家族间的相互合作、各取所需，使受害计算机和网络设备的价值被更大程度压榨，合作带来的技术升级也给安全从业者带来更大挑战。不难预测，未来挖矿木马攻击将保持平稳，但黑产家族间的合作将更加普遍，“闷声发大财”可能是新一年挖矿木马的主要目标。



## 参考文章

[https://www.freebuf.com/news/158007.html](https://www.freebuf.com/news/158007.html)

[https://www.freebuf.com/articles/web/166066.html](https://www.freebuf.com/articles/web/166066.html)

[https://github.com/danielbohannon/Invoke-DOSfuscation](https://github.com/danielbohannon/Invoke-DOSfuscation)

[https://www.coingecko.com/zh/%E4%BB%B7%E6%A0%BC%E5%9B%BE/%E9%97%A8%E7%BD%97%E5%B8%81/cny](https://www.coingecko.com/zh/%E4%BB%B7%E6%A0%BC%E5%9B%BE/%E9%97%A8%E7%BD%97%E5%B8%81/cny)

[https://www.freebuf.com/articles/web/175626.html](https://www.freebuf.com/articles/web/175626.html)

[http://www.360.cn/n/10470.html](http://www.360.cn/n/10470.html)

[https://blog.minerva-labs.com/ghostminer-cryptomining-malware-goes-fileless](https://blog.minerva-labs.com/ghostminer-cryptomining-malware-goes-fileless)

[https://www.kaspersky.com/blog/powerghost-fileless-miner/23310/](https://www.kaspersky.com/blog/powerghost-fileless-miner/23310/)

[https://www.freebuf.com/articles/web/166066.html](https://www.freebuf.com/articles/web/166066.html)

[https://blog.netlab.360.com/mykings-the-botnet-behind-multiple-active-spreading-botnets/](https://blog.netlab.360.com/mykings-the-botnet-behind-multiple-active-spreading-botnets/)

[https://www.huorong.cn/info/150097083373.html](https://www.huorong.cn/info/150097083373.html)

[https://s.tencent.com/research/report/504.html](https://s.tencent.com/research/report/504.html)

[https://ti.360.net/blog/articles/8220-mining-gang-in-china/](https://ti.360.net/blog/articles/8220-mining-gang-in-china/)

[https://www.freebuf.com/column/180544.html](https://www.freebuf.com/column/180544.html)

[http://www.360.cn/n/10542.html](http://www.360.cn/n/10542.html)

[https://www.alienvault.com/blogs/labs-research/massminer-malware-targeting-web-servers](https://www.alienvault.com/blogs/labs-research/massminer-malware-targeting-web-servers)
