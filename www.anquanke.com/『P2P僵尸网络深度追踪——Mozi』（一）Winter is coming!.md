> 原文链接: https://www.anquanke.com//post/id/240195 


# 『P2P僵尸网络深度追踪——Mozi』（一）Winter is coming!


                                阅读量   
                                **148167**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01c8900df08ba9c17d.jpg)](https://p3.ssl.qhimg.com/t01c8900df08ba9c17d.jpg)



Winter Is Coming（凛冬将至） ——《冰与火之歌》

你是否曾经疑惑过：

Mozi僵尸网络现在的感染规模有多大？

全球有多少台设备已经被感染？

是否有手段可以完全触摸到Mozi的边界？

……

自Mozi僵尸网络（以下简称Mozi）2019年被首次发现以来，它的受关注度日益提升。知微实验室自2020年9月份开始持续追踪Mozi僵尸网络，通过对Mozi通信原理和DHT协议的深度分析，提出了多种主动式探测方法，运用多种探测手段进行数据交叉验证，不断触及Mozi网络边界。我们基于已收集的探测数据，在Mozi的节点规模、全球及国内的地域分布、24小时全球活跃态势等方面给出自己的统计结论。

针对以上疑问，我们即将推出一系列Mozi专题文章详细介绍。作为该专题的首发之作，本文将概述我们目前对Mozi的研究成果。此外，我们还会在后续文章中分享对此类涉及物联网安全的P2P僵尸网络的主动探测技术，希望与各位追踪和研究新型P2P僵尸网络的同行一起交流合作！



## 一、Mozi的前世今生

新冠疫情加速了企业数字化转型趋势，据GSMA预测，2025年全球物联网设备（包括蜂窝及非蜂窝）联网数量将达到约246亿个。庞大的数量、快速的增长趋势必然牵动了巨大的利益链条，也吸引了大量不法分子试图从中谋取暴利——IBM发现，2019年10月至2020年6月间的物联网攻击比前两年增加了400%。

2019年360发布报告命名了新的P2P僵尸网络Mozi，绿盟、知道创宇等公司也随后发布观测结果，IBM更是指出2019年10月至 2020年6月Mozi 僵尸网络占了 IoT 网络流量的 90％，但都还处于初期观测阶段，捕获到的Mozi样本数量远远不够。

360的分析报告根据Mozi传播样本文件名为“Mozi.m”、“Mozi.a”等特征将它命名为“Mozi botnet”，其发音很容易联想到中文的“墨子”，因此也有人称其为“墨子”僵尸网络。截止目前已公布的分析报告，业内部分安全研究团队怀疑此僵尸网络的幕后黑手是国人，推测的蛛丝马迹如下：
1. “Mozi”一词未发现在西方有实际含义；
<li>被感染节点基于Mozi.v2版本更新得到的config信息解密后显示免费通信量统计平台由www.51.la变为[http://ia.51.la/go1?id=17675125&amp;pu=http%3a%2f%2fv.baidu.com，变化前后皆是国内域名；](http://ia.51.la/go1?id=17675125&amp;pu=http%3a%2f%2fv.baidu.com%EF%BC%8C%E5%8F%98%E5%8C%96%E5%89%8D%E5%90%8E%E7%9A%86%E6%98%AF%E5%9B%BD%E5%86%85%E5%9F%9F%E5%90%8D%EF%BC%9B)
</li>
<li>目前已知Mozi节点hash的前缀为88888888，表明Mozi节点具有群聚性，并且IBM 研究人员称Mozi 僵尸网络使用的基础设施主要位于中国（宣称占 84％，我们对数据的精确度存疑，下文会详细阐述）。<br>
于是我们大开脑洞将“Mozi”与历史上的“墨子”联系起来对比，发现了很有意思的巧合：<br>[![](https://p0.ssl.qhimg.com/t0161cd33f5e6481360.png)](https://p0.ssl.qhimg.com/t0161cd33f5e6481360.png)
</li>
言归正传！寄生于正常P2P网络的Mozi僵尸网络已经感染海量物联网节点，对全球网络基础设施而言威胁极高，因此开展对此类新型P2P型僵尸网络的深度追踪迫在眉睫。



## 二、感染节点走势

不同于通过被动式流量特征匹配的僵尸网络节点追踪方法，我们结合Mozi僵尸网络和P2P网络的特点，采用了两种更加激进的主动式探测方法，实现了对整个Mozi僵尸网络的边界探测，并交叉比对2种探测方法的结果验证了边界有效性（后续将有一篇文章对此详细介绍）。

截止4月25日，我们探测到135万个历史感染节点，其中有73万个节点来自中国，占比约为54%，（但是在去年IBM公布的数据中，中国感染节点数量占比84%。是IBM并未精确统计，还是其他国家的被感染节点在这一年中迅猛增长，我们尚对此存疑）。图1和图2展示了我们统计数据中感染排名前十位的国家，可以看到中国受感染的物联网设备数量最多，其次是印度、俄罗斯，这三个国家感染数量占总量的92%。

[![](https://p1.ssl.qhimg.com/t01dbec4d09da28c846.png)](https://p1.ssl.qhimg.com/t01dbec4d09da28c846.png)

图1. 感染国家排名前十分布

[![](https://p5.ssl.qhimg.com/t018eadd9bc0c5e6ea6.png)](https://p5.ssl.qhimg.com/t018eadd9bc0c5e6ea6.png)

图2. 感染国家排名前十位

我们绘制了感染节点每天的增量统计图（见图3），可以清晰看到每天新增的增量感染节点都是数千的量级（以千为单位，甚至达到万级），这表明Mozi的感染速度和范围扩张极快。

[![](https://p1.ssl.qhimg.com/t0125950f10d64d30fc.png)](https://p1.ssl.qhimg.com/t0125950f10d64d30fc.png)

图3. 日感染增量走势

自去年9月份至今，以国家为单位的每日活跃的感染节点的ip分布走势见图4。印度在观测初期数量最多，随后中国跃居第一。

[![](https://p1.ssl.qhimg.com/t016ac9c61153c50b46.png)](https://p1.ssl.qhimg.com/t016ac9c61153c50b46.png)

图4. 去年9月份至今以国家为单位的每日活跃的感染IP走势

截止4月25日的前七日中活跃24小时与活跃72小时的Mozi总数走势见图5，可以看到活跃的节点总数大致呈上升趋势，与图3展示的日感染增量增长趋势一致。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0134a3eaae0869a88f.png)

图5. 24小时和72小时活跃感染节点走势

如果IBM的数据准确，由此看来，经过不到一年时间，Mozi僵尸网络已在世界飞速蔓延，形势严峻。Winter is coming！



## 三、感染节点分布

截至4月25日，根据我们观测所得的数据绘制深浅图（我们统计了所有被感染Mozi节点所在ip的地理位置并绘制了地图）（见图6），可以看到，除非洲等互联网发展较落后的地区外，其余各洲都或多或少曾感染过Mozi，再一次表明，Mozi已席卷全球。

[![](https://p3.ssl.qhimg.com/t01c0ebdaefd85353ba.png)](https://p3.ssl.qhimg.com/t01c0ebdaefd85353ba.png)

图6. 存量Mozi节点世界分布

针对被感染数量最多的中国，我们绘制了热力图（见图7）以便于更加直观地展示国内各省市感染设备分布情况。通过对感染数量排序，可以看到前十个省份（见图8）的被感染数量差距明显，排名第一的河南尤为突出，接近全国总量的50%。这引起了我们的注意，后续将会针对此问题的展开详细分析。

[![](https://p3.ssl.qhimg.com/t017751c8a09c77876c.png)](https://p3.ssl.qhimg.com/t017751c8a09c77876c.png)

图7. 中国存量Mozi节点分布热力图

[![](https://p2.ssl.qhimg.com/t0106760bd77225aa5c.png)](https://p2.ssl.qhimg.com/t0106760bd77225aa5c.png)

图8. 国内感染省份排名前十位分布

由于Mozi节点并不是固定不变的，而是不断有新节点加入、旧节点退出的状态，因此我们对最近24小时活跃的Mozi样本进行分析，并绘制世界态势热力图（见图9）及国内省份的分布图（见图10），可以发现与存量（所有被感染过的）Mozi分布类似，这说明Mozi在全球范围内同步扩张，极具威胁。

[![](https://p0.ssl.qhimg.com/t01c602a22e5ade5f0c.png)](https://p0.ssl.qhimg.com/t01c602a22e5ade5f0c.png)

图9. 24小时活跃感染节点全球态势

[![](https://p3.ssl.qhimg.com/t017967ecab465410a2.png)](https://p3.ssl.qhimg.com/t017967ecab465410a2.png)

图10. 24小时国内感染省份分布

从世界范围看，被感染Mozi的物联网设备主要分布在亚欧，而国内的被感染物联网设备主要分布在经济发达的东部及南部沿海地区。而根据2020年GDP排行，排名前十的广东、江苏、山东、浙江、河南、四川、福建、湖北、湖南、上海等省市，与Mozi感染排行，呈现出惊人的相似 。相关数据显示，广东省5G基站建站需求最多，江苏、山东紧随其后。同时，在绿盟2019年发布的物联网安全年报中对暴露的物联网资产地区分布的分析中，大陆地区排名前三的是河南、山东和江苏，这也具有一定的参考价值。由此推断，越是经济发达、互联网发展迅速的地区，物联网设备越多，使不法分子能够趁虚而入。



## 四、样本统计

在我们抓取的Mozi样本中，Mips架构占比最高,其次是Mipsel，Arm6/Arm7，占比最低的是Arm4/Arm5。具体数据见表1和图11。

[![](https://p3.ssl.qhimg.com/t018fad4356feb2c2a0.png)](https://p3.ssl.qhimg.com/t018fad4356feb2c2a0.png)

表1. Mozi样本各架构数量及占比

[![](https://p1.ssl.qhimg.com/t01deb27294523cd36e.png)](https://p1.ssl.qhimg.com/t01deb27294523cd36e.png)

图11. Mozi样本架构种类统计

Mozi每感染一个节点会自动下载样本以便自己继续扩张感染更多节点。表2展示了被下载的次数排名前十的样本及下载节点历史总量。图12展示了下载样本种类排名前十的ip及其下载数量。后续会有系列文章对样本进行详细分析。

样本MD5

样本下载节点历史总量

a73ddd6ec22462db955439f665cad4e6

163096

fbe51695e97a45dc61967dc3241a37dc

154958

dbc520ea1518748fec9fcfcf29755c30

92317

eec5c6c219535fba3a0492ea8118b397

67887

4dde761681684d7edad4e5e1ffdb940b

26210

59ce0baba11893f90527fc951ac69912

21388

9a111588a7db15b796421bd13a949cd4

18024

3849f30b51a5c49e8d1546960cc206c7

11839

635d926cace851bef7df910d8cb5f647

8029

3313e9cc72e7cf75851dc62b84ca932c

7418

[![](https://p1.ssl.qhimg.com/t01a25a61738824efe4.png)](https://p1.ssl.qhimg.com/t01a25a61738824efe4.png)

表2. 被下载样本数量排名前十

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e4183c90ff9a8733.png)

图12. 下载样本种类最多的IP排名前十
