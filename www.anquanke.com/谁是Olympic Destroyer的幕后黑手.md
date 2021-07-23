> 原文链接: https://www.anquanke.com//post/id/99176 


# 谁是Olympic Destroyer的幕后黑手


                                阅读量   
                                **128354**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者 Paul Rascagneres and Martin Lee，文章来源：blog.talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2018/02/who-wasnt-responsible-for-olympic.html](http://blog.talosintelligence.com/2018/02/who-wasnt-responsible-for-olympic.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01eac79fbea2afe06b.jpg)](https://p0.ssl.qhimg.com/t01eac79fbea2afe06b.jpg)



## 一、概要

前阶段出现了一款Olympic Destroyer恶意软件，但指向这款恶意软件幕后黑手的证据自相矛盾，研究人员无法借此追踪溯源。此次攻击活动的幕后黑手有目的性地引入一些蛛丝马迹，以阻扰分析人员，通过虚假的归因标志让研究人员误入歧途。错误地追踪溯源可能让幕后黑手逍遥法外，让他们公开引用不明真相的第三方组织所提供的证据来反对犯罪指控。成功追踪溯源虽然是爆炸性新闻，但难度很大，并且不是一门非常精确的科学。这样一来，人们不得不质疑单纯的基于软件的归因方法的准确性。



## 二、简介

在本月早些时候，在韩国平昌举行的冬奥会受到了网络攻击的干扰。据报道，这起袭击导致奥运官网中断服务，因此人们无法正常在线打印门票。由于现场记者无法使用WiFi，因而开幕会相关报道的数量也有所下降。2月12日，Talos发布了一篇博客，详细介绍了[Olympic Destroyer](http://blog.talosintelligence.com/2018/02/olympic-destroyer.html)恶意软件的功能，我们有证据认为这次攻击中用到了这款恶意软件。

[![](https://p2.ssl.qhimg.com/t0115eb56e9b25c33cd.gif)](https://p2.ssl.qhimg.com/t0115eb56e9b25c33cd.gif)

恶意软件并不会凭空出现，攻击事件也并非偶然发生，那么谁应为此负责？想追踪溯源特定恶意软件开发者或者攻击组织并非易事，也不是一门精确的科学。研究人员必须考虑各种参数、与之前的攻击进行分析以及对比，才能识别出相似性。与任何犯罪行为一样，犯罪分子也有惯用的技术，往往会留下痕迹，类似于数字指纹，这些指纹可以用来发现并关联其他犯罪行为。

在网络安全事件方面，分析人员会寻找相似之处以便追踪溯源，这些因素包括：

1、战术策略、技术以及过程（Tactics, Techniques and Procedures，TPP），即攻击者如何发起攻击；

2、受害者学（Victimology），即关于受害者的研究，研究受害者的各种信息；

3、基础设施，即攻击中用到的平台；

4、攻击指示器（Indicators of Compromise， IoC），即攻击过程中遗留的可以被识别的信息；

5、恶意软件样本（攻击中使用的恶意软件）。

软件工程的优势之一就是能够共享代码，在别人已编写好的库上构建应用程序，并且可以从其他软件工程师的成功以及失败经验中汲取教训。攻击者也是如此，两个不同的攻击者可能会在攻击活动中使用出自同一个来源的代码，这意味着他们的攻击活动存在相关性，尽管这些活动由不同的攻击团体发起。有时候攻击者可能会选择主动包含来自其他攻击组织的特征，以干扰分析人员，让他们误入歧途。

对于Olympic Destroyer，什么才是有效的证据，关于追踪溯源我们可以得出什么结论呢？



## 三、各种嫌犯

### <a class="reference-link" name="Lazarus%E7%BB%84%E7%BB%87"></a>Lazarus组织

拉撒路组织（Lazarus Group，也称为Group 77）是一个复杂的犯罪团伙，与许多攻击活动有关。值得注意的是，Lazarus的某个分支（即Bluenoroff组织）袭击了某个银行位于孟加拉国的SWIFT基础设施。

根据[BAE Systems](https://baesystemsai.blogspot.com/2016/04/two-bytes-to-951m.html)的说法，SWIFT恶意软件中所使用的文件名规范为`evtdiag.exe`、`evtsys.exe`以及`evtchk.bat`。

而Olympic Destroyer恶意软件会检查`%programdata%evtchk.txt`这个文件是否存在。

这两种案例有明显的相似之处。虽然这不是足够强大的证据，但可以当成一个线索来使用（尽管说服力并不强）。

[BAE Systems](https://baesystemsai.blogspot.com/2016/05/cyber-heist-attribution.html)又介绍了Olympic Destroyer以及Bluenoroff组织所使用的wiper恶意软件的相似之处。如下图所示，左侧为Bluenoroff的wiper恶意软件，右侧为Olympic Destroyer的wiper函数：

[![](https://p0.ssl.qhimg.com/t0153c8829561e97c92.png)](https://p0.ssl.qhimg.com/t0153c8829561e97c92.png)

显然，这两份代码并不完全相同，然而这两种情况下，恶意软件只会擦除大文件的前0x1000个字节，两款恶意软件都会采用这种独特的逻辑，辨识度非常高。这是另一个线索，比单纯的文件名检查特征更加令人信服。

然而，Bluenoroff所使用的文件名以及wiper函数均已公之于众，任何人都可以自由使用。这次攻击的幕后黑手可能会在代码中添加文件名检查特征，模仿wiper函数，想让研究人员将其与Lazarus组织关联起来，尽可能隐藏自己的真实身份。

Olympic Destroyer样本的哈希值为：`23e5bb2369080a47df8284e666cac7cafc207f3472474a9149f88c1a4fd7a9b0`。

Bluenoroff样本1的哈希值为：`ae086350239380f56470c19d6a200f7d251c7422c7bc5ce74730ee8bab8e6283`。

Bluenoroff样本2的哈希值为：`5b7c970fee7ebe08d50665f278d47d0e34c04acc19a91838de6a3fc63a8e5630`。

### <a class="reference-link" name="APT3%20&amp;%20APT10"></a>APT3 &amp; APT10

[Intezer Labs](http://www.intezer.com/2018-winter-cyber-olympics-code-similarities-cyber-attacks-pyeongchang/)发现了Olympic Destroyer与APT3以及APT10组织所使用的恶意软件存在共享代码情况。

Intezer Labs发现，Olympic Destroyer与APT3所使用的一款内存凭据窃取工具存在18.5%的代码相似度，这可能是一个非常强有力的线索。然而，APT3工具实际上是基于开源的Mimikatz开发而成。由于任何人都可以下载Mimikatz，因此在得知其他人已经使用过Mimikatz的代码后，Olympic Destroyer开发者完全有可能在他们的恶意软件中使用源自Mimikatz的代码。

Intezer Labs还发现Olympic Destroyer与APT10在生成AES密钥的函数中存在相似之处。根据Intezer Labs的分析结果，之前只有APT10用过这个特殊函数。可能恶意软件开发者无意中泄露了与自己身份有关的重要线索。

### <a class="reference-link" name="Nyetya"></a>Nyetya

2017年6月份出现了一款[Neytya](http://blog.talosintelligence.com/2017/06/worldwide-ransomware-variant.html) （NotPetya）恶意软件，这款恶意软件中也用到了来自Mimikatz的代码，以窃取凭据信息。与Nyetya一样，Olympic Destroyer也滥用了PsExec以及WMI之类的合法功能来实现横向拓展，并且Olympic Destroyer同样使用了命名管道（named pipe）将窃取的凭据发送到主模块。

与Nyetya不同的是，Olympic Destroyer在传播过程中并没有使用EternalBlue以及EternalRomance这两种漏洞利用技术。然而，肇事者在Olympic Destroyer源码中留下了一些马脚，暗示恶意软件存在SMB漏洞利用功能。

Olympic Destroyer定义了如下四种结构：

[![](https://p0.ssl.qhimg.com/t0167c2db12d6ed7059.png)](https://p0.ssl.qhimg.com/t0167c2db12d6ed7059.png)

在公开的EternalBlue [PoC](https://github.com/worawit/MS17-010/blob/master/zzz_exploit.py)代码中，我们也能看到这四种结构体：

[![](https://p4.ssl.qhimg.com/t01ef6f4e4769cb336b.png)](https://p4.ssl.qhimg.com/t01ef6f4e4769cb336b.png)

当运行Olympic Destroyer时，恶意软件会在运行时加载这些结构体，但并没有使用它们。显然，开发者听说过EternalBlue PoC，但为什么留下这些结构仍然原因不明。可能开发者想为安全分析师制造一个陷阱，将他们引入错误的方向。或者这是某些未完成的功能所遗留的痕迹，没有衍化为最终版本的恶意软件。



## 四、总结

追踪溯源并非易事，很少有分析人员能够达到类似法庭判决之类的水平。很多人容易很快得出结论，将Olympic Destroyer指向特定的攻击组织，然而这种结论的基础往往并不牢固。现在我们看到恶意软件开发者可能放置了多个虚假标志，使单纯基于恶意软件样本的追踪溯源变得更加困难。

目前我们并没有在案发现场明确看到枪口冒烟的凶器，不能直接将现有的证据直接指向某个罪恶团伙。其他安全分析人员以及研究机构可能拥有我们手头未掌握的进一步证据。如果某些组织拥有其他证据（比如可能为追踪溯源提供重要线索的信号情报（SIGINT）或者人力情报来源），很有可能不会共享情报，这是他们情报收集行动的天然特性。

可以肯定的是，Olympic Destroyer攻击事件是一次非常大胆的攻击活动，极有可能由具备水准的攻击者发起，他们非常自信，认为自己不可能被轻易识别出来，也不会被追究法律责任。

不同攻击者之间存在代码共享情况非常正常。开源工具是提供各种功能的聚宝盆，攻击者可以采用其他团伙之前攻击中用过的技术，误导分析人员，将他们引入错误的分析方向。

同样，我们认为水平较高的攻击者会利用这一点，整合其他证据以误导分析人员，将攻击活动归因到其他的工具团伙。攻击者很有可能以戏谑的态度阅读安全分析人员公布的错误信息。极端情况下，由于不明真相的第三方发布了错误的追踪溯源报告，国家层面会根据公布的证据否认这些指控。每次出现错误的追踪溯源情况时，都会让幕后黑手隐藏起来。在这个虚假新闻满天飞的时代，追踪溯源是非常敏感的一个问题。

随着攻击者不断改变他们的技巧以及技术，我们很有可能会看到攻击者挖空心思，使情况进一步复杂化，加大追踪溯源难度。追踪溯源并非易事，也不大会变得更加简单。
