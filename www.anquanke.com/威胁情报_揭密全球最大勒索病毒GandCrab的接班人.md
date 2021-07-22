> 原文链接: https://www.anquanke.com//post/id/180470 


# 威胁情报：揭密全球最大勒索病毒GandCrab的接班人


                                阅读量   
                                **166600**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t018318fd3190913216.jpg)](https://p0.ssl.qhimg.com/t018318fd3190913216.jpg)



## 概述

前面文章讲述了[GandCrab勒索病毒狂赚20亿的故事](https://www.anquanke.com/post/id/179816)，从6月1号GandCrab勒索病毒运营团队宣布停止更新之后，过去了快半个月，确实没有再发现GandCrab新的版本出现，然而有一款跟GandCrab使用相同的传播渠道的勒索病毒却在最近一段时间非常活跃，那就是Sodinokibi

国内最早发现Sodinokibi是在4月份，勒索病毒运行之后中毒现象，如下所示：

[![](https://p1.ssl.qhimg.com/t014eb8d1d13dc32f52.png)](https://p1.ssl.qhimg.com/t014eb8d1d13dc32f52.png)



## 核心技术剖析

对样本进行详细分析，Sodinokibi的样本都使用了大量的代码混淆加密的方式，勒索病毒核心代码被一层外壳代码加密包裹，在内存中解密执行，如下所示：

[![](https://p4.ssl.qhimg.com/t014b2a4b73f690ad89.png)](https://p4.ssl.qhimg.com/t014b2a4b73f690ad89.png)

动态跟踪分析，我提取出样本中勒索加密的核心Payload代码，然后对核心的Payload代码进行调试，在调试的过程中，我发现这款勒索跟之前GandCrab勒索病毒部分功能比较相似，有一种似曾相似的感觉，该勒索病毒主要的功能函数，如下所示：

[![](https://p0.ssl.qhimg.com/t01f2185c3d7556216b.png)](https://p0.ssl.qhimg.com/t01f2185c3d7556216b.png)

该勒索病毒同样会将加密的一些密钥信息存储在注册表中，如下所示：

[![](https://p1.ssl.qhimg.com/t0194c3cdfe876dcb10.png)](https://p1.ssl.qhimg.com/t0194c3cdfe876dcb10.png)

获取主机的相关信息，如下所示：

[![](https://p0.ssl.qhimg.com/t01c2d8add2f4b2e8e6.png)](https://p0.ssl.qhimg.com/t01c2d8add2f4b2e8e6.png)

在内存中解密出大量的域名，我提取了几百个内存解密出来的域名信息，用这些域名拼接URL，与GandCrab勒索病毒使用的拼接技术一样，如下所示：

[![](https://p3.ssl.qhimg.com/t01c53beba06f2eef68.png)](https://p3.ssl.qhimg.com/t01c53beba06f2eef68.png)

从样本逆向分析的角度，可以找到与GandCrab勒索病毒的一些相似的关联信息，分析完这款勒索病毒，我的感觉就是这款勒索病毒作者应该是有GandCrab勒索病毒的一部分源码或借鉴了GandCrab勒索病毒的一些技术……

在分析样本的时候，我有一点预感，觉得这个样本后面应该会比较流行，可能是一种职业的嗅觉，之前我分析过很多勒索病毒家族，修改桌面背景的流行的勒索病毒家族并不多，像之前的GandCrab和Shade勒索病毒等



## 溯源关联分析

通过溯源，可以找了一个VBS脚本，如下所示：

[![](https://p5.ssl.qhimg.com/t01ad49d732680e3b56.png)](https://p5.ssl.qhimg.com/t01ad49d732680e3b56.png)

分析脚本中发现一个恶意服务器IP地址188.166.74.218，通过VT平台进行关联分析，该服务器从4月份，还在一直传播GandCrab勒索病毒，如下所示：

[![](https://p3.ssl.qhimg.com/t01fffc02e19a26c1af.png)](https://p3.ssl.qhimg.com/t01fffc02e19a26c1af.png)

通过病毒样本的HASH值，在VT上查询到样本的相关信息，如下所示：

[![](https://p4.ssl.qhimg.com/t013c0739e0f0ecfa41.png)](https://p4.ssl.qhimg.com/t013c0739e0f0ecfa41.png)

可以看到样本最早是4月26号被人上传到VT平台分析的，通过威胁情报IP地址关联，我还关联到了云安全服务提供商AlertLogic在4月23号发布的相关的分析报告，如下所示：

[![](https://p1.ssl.qhimg.com/t01485e703efe2f76e9.png)](https://p1.ssl.qhimg.com/t01485e703efe2f76e9.png)

该报告指出黑客利用Confluence的安全漏洞传播GandCrab勒索病毒，可以得出在4月23号之前这个恶意服务器还在传播GandCrab，然而到了4月26号就开始传播Sodinokibi勒索病毒，然后就有企业感染了Sodinokibi勒索病毒，并将样本上传到了VT上，可见黑产的更新速度之快



## 威胁情报追踪

4月26号，国外某社交网站，Cyber Security公布了一款新型的勒索病毒Sodinokibi，这也是这款勒索病毒首次公布出来，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016fb86922cde57cdd.png)

(猜测之前VT上的样本是不是也是Cyber Security上传上去的？哈哈哈哈)

4月27号，Cyber Security又在社交网站发布了这款勒索病毒的攻击感染视频，如下所示：

[![](https://p3.ssl.qhimg.com/t01b4267b8646a6fbdf.png)](https://p3.ssl.qhimg.com/t01b4267b8646a6fbdf.png)

4月28号，深信服千里目安全实验室在国内发布了第一篇关于Sodinokibi勒索病毒的相关详细分析报告，取名为GandCrab的“蓝屏”变种勒索病毒，如下所示：

[![](https://p3.ssl.qhimg.com/t0158013487dcdb1efd.png)](https://p3.ssl.qhimg.com/t0158013487dcdb1efd.png)

4月29号，Cyber Security在社交网站公布了VT样本的下载地址，如下所示：

[![](https://p0.ssl.qhimg.com/t01bea41216bb0609e3.png)](https://p0.ssl.qhimg.com/t01bea41216bb0609e3.png)

4月30号，思科全球威胁情报分析团队，发布了一篇Sodinokibi的安全分析文章，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0150a569b6119a4e90.png)

并在社交网站使用官方帐号发布了报告信息，如下所示：

[![](https://p2.ssl.qhimg.com/t01efbb250469ac578d.png)](https://p2.ssl.qhimg.com/t01efbb250469ac578d.png)

5月1号起，国外各大安全媒体网站和安全研究负责人争相在社交网站转发报道思科的分析报告，同时国外各大网站都开始发布这款勒索病毒的预警文章，如下所示：

[![](https://p1.ssl.qhimg.com/t0198a3d80f5573e88c.png)](https://p1.ssl.qhimg.com/t0198a3d80f5573e88c.png)

思科的报告中提到一款通过WebLogic服务器漏洞传播的新型的Sodinokibi勒索病毒，拿到样本之后，我做了相似性分析，发现里面介绍了勒索病毒样本跟我分析的勒索病毒非常相似，如下所示：

[![](https://p2.ssl.qhimg.com/t011dbdf1b403e7b601.png)](https://p2.ssl.qhimg.com/t011dbdf1b403e7b601.png)

样本代码相似度达到95%，加密勒索的核心主功能代码流程也基本相似，添加了一些无用函数分支，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01636c644f246156a4.png)

从而判定思科威胁分析团队报道的这个勒索病毒就是我之前分析过的勒索病毒，国外取了一个名字叫Sodinokibi勒索病毒

4月23号之前还在传播GandCrab勒索病毒的渠道，在4月27号就有国内有客户感染Sodinokibi，可见Sodinokibi勒索病毒传播速度有多快了，同时也证实之前GandCrab的传播渠道是多么的强大

从4月26号到4月30号，已经有多个客户感染不同的Sodinokibi勒索病毒变种，5月份，国内外开始相继出现在大量关于Sodinokibi勒索病毒的安全预警报告，从分析捕获到的各种Sodinokibi勒索病毒样本，可以看出这些变种样本代码上大体上没有变化，勒索桌面背景图片会显示不同的勒索文字信息，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0144fe5a829c1642d1.png)

这在一个半月的时间里，国内外已经有很多企业客户被这款勒索病毒感染，期间有一位搞工控安全的朋友曾咨询过我，它有一个客户也是中了这款勒索病毒，如下所示：

[![](https://p3.ssl.qhimg.com/t01a852c0db8e10c2b1.png)](https://p3.ssl.qhimg.com/t01a852c0db8e10c2b1.png)

从朋友那里得知这款勒索病毒已经在工控企业系统开始传播流行起来了，同时这款勒索病毒传播流行速度之快，国内其它各企业都需要做好相应的安全防护，因为很遗憾至今这款勒索病毒还不能解密，没有解密工具，如果企业主机被这款勒索病毒加密了，是无法解密的……

针对这款新型的勒索病毒，微步在线威胁情报关联的IP信息，如下所示：

[https://x.threatbook.cn/](https://x.threatbook.cn/)

[![](https://p5.ssl.qhimg.com/t0144238a681f34eeed.png)](https://p5.ssl.qhimg.com/t0144238a681f34eeed.png)

已经关联到相关的样本和国外一些分析报告信息，如下所示：

[![](https://p3.ssl.qhimg.com/t016baaecc65099983d.png)](https://p3.ssl.qhimg.com/t016baaecc65099983d.png)

可以看到这个恶意的IP地址，已经被微步的自动化工具，加入到了威胁情报库中，说明微步在威胁情报这方面做的还可以，如下所示：

[![](https://p4.ssl.qhimg.com/t011ff94d32352a6023.png)](https://p4.ssl.qhimg.com/t011ff94d32352a6023.png)



## 总结

今年针对企业的勒索病毒攻击越来越多，GandCrab仅仅是开始，每天都有新的勒索病毒出现，全球已经有多家企业和政府部分受到勒索病毒攻击，导致巨额的损失，前天国外报道世界最大飞机零件供应商ASCO惨遭勒索病毒攻击，导致四个工厂已经停产，数千人在家待业，如下所示：

[![](https://p3.ssl.qhimg.com/t017cc40f5c6237a0a1.png)](https://p3.ssl.qhimg.com/t017cc40f5c6237a0a1.png)

GandCrab勒索病毒不更新了，针对企业的勒索病毒攻击并没有停止，可以发现Sodinoki勒索病毒已经迅速流行传播，通过威胁情报的关联分析，我们可以得出Sodinokibi勒索病毒接管了GandCrab强大的传播渠道，成为了全球最大的勒索病毒GandCrab的接班人，开始继续作恶，Sodinokibi会不会成为下一个GandCrab？还需要持续追踪……

最后欢迎大家关注我的微信公众号：CyberThreatAnalyst,会不定期更新相关内容，一直感谢那些支持我的朋友，欢迎关注、转发、赞赏，安全的路，贵在坚持……

本文转载自: [CyberThreatAnalyst](https://mp.weixin.qq.com/s/5gTElAGq5v-hFWeq9uL9jg)

如若转载,请注明出处：[https://mp.weixin.qq.com/s/5gTElAGq5v-hFWeq9uL9jg](https://mp.weixin.qq.com/s/5gTElAGq5v-hFWeq9uL9jg)
