> 原文链接: https://www.anquanke.com//post/id/179816 


# 赚了20亿美元GandCrab勒索病毒家族的故事


                                阅读量   
                                **229022**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t0129fb49f01523a06a.jpg)](https://p5.ssl.qhimg.com/t0129fb49f01523a06a.jpg)





2019年6月1日，GandCrab勒索病毒团队在相关论坛发表俄语官方声明，将停止更新，这款2018年最流行的勒索病毒，在2019年6月终于结束了……然后它的故事完了，钱赚够了，却打开了潘多拉魔盒，后面会有越来越多的GandCrab团队涌现出来……对这款勒索病毒，我跟踪了一年半，一年半之后GandCrab运营团队赚够了，退休了，我却仍坚持着.跟踪各种恶意家族样本…..

[![](https://p1.ssl.qhimg.com/t01c6c3c256fa5f2a7a.png)](https://p1.ssl.qhimg.com/t01c6c3c256fa5f2a7a.png)

翻译之后，大概的意思，如下所示：

在与我们合作的那一年里，人们已经赚了20多亿美元，我们已经成为地下市场中勒索软件制造者方向的代表者。 我们每周的收入平均为250万美元。我们每人每年赚得超过1.5亿美元。我们成功兑现了这笔钱，并在现实生活和互联网上的将收获的钱成功合法化。

我们很高兴与你合作，但是，如上所述，所有的好事都会结束。

我们要离开这个当之无愧的退休生活。

我们已经证明，通过做恶行为，报复不会到来。我们证明，在一年内你可以终生赚钱。 我们已经证明，有可能成为一个不是我们自己的话，而是为了表彰其他人。

1、停止代理商活动;

2、我们要求代理商暂停流量

3、从这个日期起的20天内，我们要求代理商以任何方式通过他们的僵尸主机从而将赎金货币化

4、受害者 – 如果您现在购买密钥，但您的数据将无法恢复，因为密钥将被删除

大概意思就是上面，运营团队做的很绝，在赚了那么多钱的情况下，仍没有想着公布密钥，然后删除所有的密钥，之前有团队称他们为“侠盗勒索病毒”，是因为他们在后期的版本中避开了叙利亚地区，但他们并没有“仁慈”放出所有的密钥，而且选择销毁…….



## 开端

### GandCrab1.0初出茅庐

GandCrab勒索病毒，我第一次接触它是在一个国外安全研究人员的论坛上，相关的论坛网站：https://secrary.com/ReversingMalware/UnpackingGandCrab/，如下所示：

[![](https://p4.ssl.qhimg.com/t01e28c859ab1c734a8.png)](https://p4.ssl.qhimg.com/t01e28c859ab1c734a8.png)

当时我觉得这个勒索比较有意思，于是有从app.any.run网站下载到了相关的样本，如下所示：

[![](https://p0.ssl.qhimg.com/t0103b7df09ab523166.png)](https://p0.ssl.qhimg.com/t0103b7df09ab523166.png)

2019年1月26号，我第一次分析了GandCrab1.0版本的样本，它的第一代，使用了代码自解密技术，在内存中解密出勒索病毒的核心代码，然后替换到相应的内存空间中执行,当时它只向用户勒索达世币，加密后缀为:GDCB，分析完之后GandCrab运营团队在2019年1月28号，在论坛上发布了相关的出售贴子，如下所示：

[![](https://p2.ssl.qhimg.com/t01e1d9ec49348e7cc1.png)](https://p2.ssl.qhimg.com/t01e1d9ec49348e7cc1.png)

当时我还没加入现在的公司，也没发现这款勒索在后面一年半的时候会变的如此火爆……



## 演变

### GandCrab2.0

2018年2月份，我加入了新的公司，负责勒索病毒这块的业务，GandCrab在2018年3月份的时候演变出了GandCrab2.0版本，主要是因为3月初GandCrab勒索病毒的服务器被罗马尼亚一家安全公司和警方攻破，可以成功恢复GandCrab加密的文件。病毒开发人员迅速升级了版本V2，并将服务器主机命名为politiaromana.bit，挑衅罗马尼亚警方，之前服务器的主机为gandcrab.bit…..

分析GandCrab2.0版本的，使用了代码混淆，花指令，反调试等技术，同时它使用了反射式注入技术，将解密出来的勒索病毒核心Payload代码，注入到相关的进程当中，然后执行相应的勒索加密操作，加密后缀为：CRAB……

### GandCrab2.1

2018年4月，我接到客户应急处理，发现了第一例GandCrab勒索案例，通过分析，发现它就是之前我分析过的GandCrab2.0版本的升级，该版本号为GandCrab2.1，然后我们发布了相关的分析预警报告，如下所示：

[![](https://p3.ssl.qhimg.com/t0132d2fd5e458167c8.png)](https://p3.ssl.qhimg.com/t0132d2fd5e458167c8.png)

### GandCrab3.0

在发布预警之后，我监控到了一款新的GandCrab新的变种，命名为GandCrab3.0，这款勒索病毒主要通过邮件附件的方式，在一个DOC文档中执行VBS脚本，然后下载GandCrab3.0勒索病毒并执行，加密后缀与之前2.0版本一样为:CRAB，如下所示：

[![](https://p4.ssl.qhimg.com/t01d3ad73a6dc744778.png)](https://p4.ssl.qhimg.com/t01d3ad73a6dc744778.png)

### GandCrab4.0

2018年7月，再次接到客户应急响应，通过分析发现它属于GandCrab家族，这次加密后缀为:KRAB，同时勒索运营团队在勒索信息中首次使用了TOR支付站点的方式，让受害者联系，然后解密，我们也在第一时间发布了相关的预警，如下所示：

[![](https://p2.ssl.qhimg.com/t01ca43bf93cadc804a.png)](https://p2.ssl.qhimg.com/t01ca43bf93cadc804a.png)

### GandCarb4.3

GandCrab4.0之后，2018年8月底，我捕获到了GandCrab的一个新版本GandCrab4.3版本，可见这款勒索更新是如此之快，对样本进行了详细分析，并发布了相关的详细分析报告，如下所示：

[![](https://p4.ssl.qhimg.com/t01784332d127bf5c5b.png)](https://p4.ssl.qhimg.com/t01784332d127bf5c5b.png)

### GandCrab5.0

在2018年9月份的时候，我发现这款勒索病毒又更新了，而且使用了更多的方式传播，不仅仅通过VBS脚本执行下载，还会使用PowerShell脚本，JS脚本的方式下载传播执行，捕获取了它的相关样本，并解密出相应的脚本，如下所示：

[![](https://p1.ssl.qhimg.com/t01134f913685b6c139.png)](https://p1.ssl.qhimg.com/t01134f913685b6c139.png)

同时我们也在第一时间更新了GandCrab5.0版本的预警报告，如下所示：

[![](https://p1.ssl.qhimg.com/t01dca401f2638e8f51.png)](https://p1.ssl.qhimg.com/t01dca401f2638e8f51.png)

GandCrab5.0勒索病毒加密的后缀，不在使用之前的加密后缀，开始使用随机的加密后缀……

在GandCrab5.0之后，出现了两个小版本更新GandCrab5.0.3和GandCrab5.0.4，尤其是GandCrab5.0.4这个版本非常流行，很多客户中招……

### GandCrab5.0.3

在2018年10月，我捕获到了最新的GandCrab5.0.3的传播JS脚本，同时做了详细分析，如下所示：

[![](https://p3.ssl.qhimg.com/t01f22e0c1db9d9724f.png)](https://p3.ssl.qhimg.com/t01f22e0c1db9d9724f.png)

在我发布GandCrab5.0.3分析报告不久之后，GandCrab5.0.4开始非常活跃，大量客户中招，我们马上发布了相应的预警报告，如下所示：

[![](https://p1.ssl.qhimg.com/t01907b908e839c1824.png)](https://p1.ssl.qhimg.com/t01907b908e839c1824.png)

GandCrab5.0.4这个版本一直活跃了很长一段时间，导致大量客户中招……

### GandCrab5.0.5

在GandCrab5.0.4版本活跃了一段时间之后，全球多家企业以及个人用户中招，这里有一个小插曲，在10月16日，一位叙利亚用户在twitter上表示GandCrab勒索病毒加密了他的电脑文件，因为无力支付高达600美元的“赎金”，他再也无法看到因为战争丧生的小儿子的照片，如下所示:

[![](https://p5.ssl.qhimg.com/t0197751b91649d73bf.png)](https://p5.ssl.qhimg.com/t0197751b91649d73bf.png)

GandCrab勒索病毒运营团队看到后就发布了一条道歉声明，并放出了所有叙利亚感染者的解密密匙，GandCrab也随之进行了V5.0.5更新，将叙利亚加进感染区域的“白名单”，这也是为什么后面有一些安全团队称GandCrab为“侠盗勒索病毒”的原因……

后面安全公司Bitdefender与欧州型警组织和罗马尼亚警方合作开发了GandCrab勒索软件解密工具,解密工具适用于所有已知版本的勒索软件,该努力是No More Ransom项目的最新成果，这大该也预示着GandCrab勒索病毒快走到了尽头……

解密工具，如下所示：

[![](https://p0.ssl.qhimg.com/t0141624f0484d8fe4e.png)](https://p0.ssl.qhimg.com/t0141624f0484d8fe4e.png)

可解密的版本，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010426842bbfd58466.png)

[![](https://p0.ssl.qhimg.com/t01f13683123737b2a9.png)](https://p0.ssl.qhimg.com/t01f13683123737b2a9.png)

2018年年底，GandCrab勒索病毒，被我“誉为”2018年四大勒索病毒之首，2018年四大勒索病毒：GandCrab、Satan、CrySiS、Globelmpster，也是我最先提出来的，后面各大安全厂商也相应在报告中提到……

在年底的时候，我们发布了一个相关的GandCrab预警的总结报告，总结了一下GandCrab在2018年的故事，如下所示：

[![](https://p1.ssl.qhimg.com/t0161ef197415724ab4.png)](https://p1.ssl.qhimg.com/t0161ef197415724ab4.png)

2018年GandCrab就这样活跃了一整年，赚了多少钱，只有他们自己知道……

### GandCrab5.1

2019年1月，再次接到客户应急响应，发现GandCrab5.1版本的勒索病毒，通过分析之后，我们也在第一时间发布了相关的预警报告，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014fd57fc9a0cbf6fc.png)

GandCrab5.1勒索病毒与GandCrab5.0.5版本同样避开了叙利亚地区，对叙利亚地区的主机不进行加密……

GandCrab5.1版本之后不久，2019年2月安全公司Bitdefender再次更新了GandCrab解密工具，可以解密GandCrab5.1版本的勒索病毒，如下所示：

[![](https://p5.ssl.qhimg.com/t01b04edbc1d02877cc.png)](https://p5.ssl.qhimg.com/t01b04edbc1d02877cc.png)

经过测试，这款解密工具可以解密GandCrab5.1版本之前的多个版本GandCrab勒索病毒……



## 衰落

### GandCrab5.2

GandCrab5.1火了一段时间，然后随着GandCrab5.1版本的解密工具的放出，2019年3月，GandCrab运营团队再次发布了GandCrab5.2版本的勒索病毒，同时国内又有多家企业中招，我们第一时间捕获到了相应的样本，然后发布了相应的预警报告，如下所示：

[![](https://p3.ssl.qhimg.com/t017dfdef1c8da6ce9f.png)](https://p3.ssl.qhimg.com/t017dfdef1c8da6ce9f.png)

### GandCrab5.3

2019年4月，捕获到了GandCarb最新的也是最后的一个变种版本样本GandCrab5.3版本，如下所示：

[![](https://p4.ssl.qhimg.com/t017e024fbe55961c8c.png)](https://p4.ssl.qhimg.com/t017e024fbe55961c8c.png)

在GandCrab爆发的一年半时间里，接到过N起客户应急响应事件，直到近期，我发现它的传播渠道开始传播其他勒索病毒样本(Sodinokibi、GetCrypt、EZDZ)，我心里在想GandCrab换人了？

没想到2019年6月1日，GandCrab运营团队就在国外论坛上官方宣布了，停止GandCrab勒索病毒的更新……

这款勒索病毒，我跟踪了一年半的时间，从GandCrab1.0到GandCrab5.3，期间有多个大小版本的更新，更新速度之快，传播方式之多，使用了各种方式进行传播，相关的报告中也都有所提到，GandCrab运营团队声称已经赚够了养老钱，不会更新了，然后它并没有放出所有的解密密钥……

GandCrab运营团队研究赚了多少，我们不知道，不过肯定不会少，勒索现在成了黑产来钱最快，也是最暴力的方式，每年全球的勒索运营团队都会有几百亿的黑产收入，很多大型企业中了勒索而不敢申张，偷偷交赎金解决，相关政企事业单会找安全公司进行应急响应处理……

从GandCrab1.0出来到GandCrab5.3版本，我敢说除了GandCrab运营团队，全球没有人比我更了解GandCrab勒索病毒，我一直持续不断在跟进，追踪，捕获最新的样本，这款勒索病毒更新速度也是真的很快……

我写过的相关的分析报告(大部分报告已发表到深信服千里目安全实验室微信公众号，大家可以关注)

[![](https://p3.ssl.qhimg.com/t016d8cf953c776aac6.png)](https://p3.ssl.qhimg.com/t016d8cf953c776aac6.png)

抓到的相关样本

[![](https://p0.ssl.qhimg.com/t01943533a4250e5507.png)](https://p0.ssl.qhimg.com/t01943533a4250e5507.png)

然后一年半之后，GandCrab运营团队已经赚够了钱，可以退休了，我却还在坚守着岗位，赚着微薄的薪水，作为一名安全分析师继续跟踪着一个又一个勒索病毒，挖矿病毒，以及各种恶意软件……

有时候我在想，要不要去做黑产?各种安全技术我有，黑产运作我也懂，做安全的这帮人怎么在玩，我也了解，为啥不去做黑产?赚一票了走人?

这么多年做安全，我一直保持着两点：1.坚持安全研究  2.不做黑产

至少现在我能坚守这两点……

GandCrab勒索虽然结束了，然仍安全并没有结束，而且在后面一定会越来越多的黑产团队加入，GandCrab也算是打开了潘多拉之盒，会有多少像GandCrab的黑产团队出来作恶就不知道了，这些年做勒索和挖矿的黑产，基本都发财了，闷声发着大财……

就这样吧，赚了20亿美元GandCrab勒索病毒家族的故事已经结束，但我的故事还在继续，还有更多各种不同的恶意样本家族需要我去跟踪分析，勒索、挖矿，银行木马、僵尸网络、APT间谍远控等等……

最后欢迎大家关注我的微信公众号：CyberThreatAnalyst，我会不定期更新相关内容!


