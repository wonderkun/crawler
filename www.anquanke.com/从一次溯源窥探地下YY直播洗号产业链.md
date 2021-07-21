> 原文链接: https://www.anquanke.com//post/id/105043 


# 从一次溯源窥探地下YY直播洗号产业链


                                阅读量   
                                **133019**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">27</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t0170a72fb045d23e48.jpg)](https://p5.ssl.qhimg.com/t0170a72fb045d23e48.jpg)

本文将揭露地下黑产中最常见的扫号产业链，包括从账号收集、代理抓取、扫号、洗号、变现的完整过程。本次主要讲述针对YY直播的扫号产业链

作者：路人甲@360云影实验室



## 0x00 偶然发现的扫号黑客

近日在蜜罐中发现了一个特别的腾讯云的ip，这个ip通过我们蜜罐的匿名代理端口对几个特定的ip频繁发包，但是数据包内容看着并无异常，就是些常规tcp链接。

在这这个ip的80端口部着一个hfs，奇怪的是它这个hfs中存的不是木马远控样本，也不是挖矿样本，而是一堆ip和端口组合

[![](https://p0.ssl.qhimg.com/t01d8069a002da8fe08.png)](https://p0.ssl.qhimg.com/t01d8069a002da8fe08.png)

[![](https://p3.ssl.qhimg.com/t01e13988496834ec0a.png)](https://p3.ssl.qhimg.com/t01e13988496834ec0a.png)



这些勾起了我们的好奇心。正好他的hfs是有漏洞的版本，于是就有了下面漫长的文章

**   1****、控制黑客机器   **

利用hfs的代码执行直接打下黑客的vps，直接去到管理员的桌面，第一眼看着机器似乎一切正常

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d6130887cb9fa5db.png)

打开前面名字为“保存数据xxx”的文件夹，呈现在面前是大量的已经分好类型的账号和密码文件。

[![](https://p2.ssl.qhimg.com/t016afaa51930649f78.png)](https://p2.ssl.qhimg.com/t016afaa51930649f78.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c4e2342a1a8bc085.png)

[![](https://p1.ssl.qhimg.com/t01ec9ebba1ef449d3f.png)](https://p1.ssl.qhimg.com/t01ec9ebba1ef449d3f.png)

根据分类名，猜测这些应该都是YY直播的账号密码。

于是为了验证这些账户的真实性，我们尝试登陆了几个账号。成功率几乎百分之百。

如下图:

[![](https://p5.ssl.qhimg.com/t019755fdfe50b7fe0b.png)](https://p5.ssl.qhimg.com/t019755fdfe50b7fe0b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ddce7925e020d41d.png)

[![](https://p3.ssl.qhimg.com/t014f811dc243d818fb.png)](https://p3.ssl.qhimg.com/t014f811dc243d818fb.png)

这些分类文件里面的账号，都是能登陆的，而且有些账号里面的还剩余有Y币或者钻等。粗略的计算了下，就在这一个文件夹中的账密就有15000多条。然后在机器上发现了好几款YY直播的扫号器。

[![](https://p5.ssl.qhimg.com/t015293815e6d4e5610.png)](https://p5.ssl.qhimg.com/t015293815e6d4e5610.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eda02ec3a827240e.png)

用mimikatz抓取了管理员密码，切换到他的桌面，扫号的程序正在疯狂工作

[![](https://p1.ssl.qhimg.com/t013fef05e30cf3fba8.png)](https://p1.ssl.qhimg.com/t013fef05e30cf3fba8.png)

[![](https://p4.ssl.qhimg.com/t014b3a7350f710cf6e.png)](https://p4.ssl.qhimg.com/t014b3a7350f710cf6e.png)



尝试运行其中的一款扫号工具，导入他vps已经扫出来的账号，发现全部等能登录， 这个扫号工具效率还是极其高的。

[![](https://p2.ssl.qhimg.com/t01eb9f659a7cc73b9b.png)](https://p2.ssl.qhimg.com/t01eb9f659a7cc73b9b.png)

有意思的是，从数据包来看，这些扫号软件并不是直接通过web的接口来进行扫号的，从他们的文件命名来看他们的扫号都是通过YY直播客户端的通信协议来完成的，猜测这样做的目的是增加扫号的速度，因为初步来看给予YY直播协议的登陆是直接通过tcp协议完成的。不用再走一层http。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018d16adf48bf9ca62.png)



在同目录发现了config配置文件，这个文件配置的就是前面黑客的hfs地址，这就解开了之前的疑问，其实他hfs里面的ip列表都是他收集的一些免费的匿名代理ip，用来批量导入扫号软件中软件开始扫号。

**2****、意外收获**

在这位黑客的vps上面发现了“百度云盘的软件”，打开他的百度云软件，他居然记住了密码，我们也就顺着这条路深挖了一下。

[![](https://p0.ssl.qhimg.com/t0125fa9deef58ce90a.png)](https://p0.ssl.qhimg.com/t0125fa9deef58ce90a.png)

他的百度运账号里面存放着大量的外挂、账号数据、以及一些扫号的源码。

在一个文件夹为400万的文件夹中发现了存放着380多万的YY账号和密码的文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d670c99b61f4c1f8.png)

初步怀疑这些账号密码是之前YY泄露过的一部分

这些账密都是十分整齐的排列,随机挑选其中的账号也是有能够登陆的,这些应该就是扫号的的基础数据来源了。后来也证实了这的确是是之前yy泄漏的老数据（这部分后面会写）

到此已经找到这个黑客的扫号的数据源、扫号工具、扫号方式。但是，我们依然对他这380万的账号来源和他后续这些账号怎么变现非常感兴趣，于是就有了后续一系列的操纵。

** **

## 0x02 溯源+社工

**1****、****轻松的溯源****                  **

为了了解他们整个产业链我决定加他的qq。加他之前对他进行了深入了解，前面说这个黑客确实大意了，在他的vps百度云是记住密码的，于是乎我们的溯源就容易多了。

[![](https://p1.ssl.qhimg.com/t01e5fd83600f726633.png)](https://p1.ssl.qhimg.com/t01e5fd83600f726633.png)

看到炫酷的OPPO r7s 这个明显是他的手机传上来的，

[![](https://p0.ssl.qhimg.com/t0180ea26e73fdec908.png)](https://p0.ssl.qhimg.com/t0180ea26e73fdec908.png)

这就是小黑客的样子，还是个萌萌哒的小鲜肉，他是在山东潍坊某学校上学

最后在他的自己的定位图发现了他读的学校，某某科技学院

[![](https://p1.ssl.qhimg.com/t01af1da2884f092a0d.png)](https://p1.ssl.qhimg.com/t01af1da2884f092a0d.png)

这个黑客可真大意，继续翻他的相册

[![](https://p5.ssl.qhimg.com/t0149c96783821e9fe1.png)](https://p5.ssl.qhimg.com/t0149c96783821e9fe1.png)

发现了他的两个qq号，分别是281********、3338*******

然后通过他的从百度云账号，我们能够辅助的判断他最常用的qq大号，就是这个2开头的qq号

[![](https://p2.ssl.qhimg.com/t0144d760f5e28d62b2.png)](https://p2.ssl.qhimg.com/t0144d760f5e28d62b2.png)[![](https://p3.ssl.qhimg.com/t01498a4d08453017a7.png)](https://p3.ssl.qhimg.com/t01498a4d08453017a7.png)

这位黑客自己还成立一个叫“凉心科技的”公司（然而经过查询并没有注册在案），还在做免流的生意

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a661ddbdfdb8bbdd.png)

顺带在他的qq空间暴露了他的年龄，还是个多愁善感的小伙。

在他使用校园上网软件中么也发现了他的姓名，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0172d0203c90d737e5.png)

通过和他的vps的3389密码对比，发现他vps的密码的开头就是姓名的缩写

侧面也印证这个叫张某涛的人就是那个扫号黑客

[![](https://p4.ssl.qhimg.com/t0174e058e765214089.png)](https://p4.ssl.qhimg.com/t0174e058e765214089.png)

**汇总后，信息总结如下**：

姓名：张*涛

年龄：18

常用QQ：281*******、333*******

学校：****科技学院

主要产业：扫号、免流、游戏外挂





**2、强行社工**

掌握了这些信息后，我觉得足以吓唬到他了，于是以合作的名义加他。

我直接表明了我就是之前黑掉他服务器的人，想找他合作搞YY直播账号。

[![](https://p4.ssl.qhimg.com/t01e82385d0e20eced4.png)](https://p4.ssl.qhimg.com/t01e82385d0e20eced4.png)

开始他还很有防备半信半疑，我然后抖了关于他的很多的个人信息。[![](https://p5.ssl.qhimg.com/t016b1fcc23f48b72de.png)](https://p5.ssl.qhimg.com/t016b1fcc23f48b72de.png)

[![](https://p1.ssl.qhimg.com/t01515109f73247782f.png)](https://p1.ssl.qhimg.com/t01515109f73247782f.png)

他立马态度大变，还要拜师学习黑客技术，于是就在他面前强行吹了波逼，加强了他对我的信任。（他始终都没反应过来他的人信息我是从他百度云扒下来的 ：） ）



## 0x02 基础数据的来源

得到他的信任之后，我就和他交流了一些问题，首先，就是他那380万的账号的来源，果然就是之前泄露过的那一批之中的

[![](https://p1.ssl.qhimg.com/t011b581a0d8e6ac54f.png)](https://p1.ssl.qhimg.com/t011b581a0d8e6ac54f.png)



## 0x03 洗号变现

从他这里也了解到YY直播怎么洗号变现的，他其实不是整个链条的最后一环节，他只是其中一环，他只把扫出来的账号，卖给下家，自己就不管了。行情大概是100元1万个普通的yy账号

[![](https://p3.ssl.qhimg.com/t01d8a1f0deae682470.png)](https://p3.ssl.qhimg.com/t01d8a1f0deae682470.png)

有YY币的账号另算。大概是按10：4卖给下家，下家就直接给主播刷礼物，然后主播从YY的官方把礼物按比列体现成钱，到此yy币就变百花花银子了。

[![](https://p3.ssl.qhimg.com/t01d4b37addbf165f5f.png)](https://p3.ssl.qhimg.com/t01d4b37addbf165f5f.png)

而那些没有钱的YY账号，这些人就会用批量挂号软件，批量进入主播濒道，为主播增加观看人数从而达到刷人气的目的。（有些主播可能是洗号的人自己开的，也可能是和一些主播合作然后分成）

通过这位黑客介绍，找到了洗号的下家，有序是熟人介绍，这个人对我很是信任，从他那里也证实了这位黑客之前说的，我说我有大量的YY账号找他合作。

[![](https://p1.ssl.qhimg.com/t0160364e2fc7f28364.png)](https://p1.ssl.qhimg.com/t0160364e2fc7f28364.png)

他直接仍给我一个批量刷礼物的软件，说是测试版本，证明他的实力。

[![](https://p1.ssl.qhimg.com/t016e7bd38433fc881b.png)](https://p1.ssl.qhimg.com/t016e7bd38433fc881b.png)

[![](https://p4.ssl.qhimg.com/t01f798992a265c6789.png)](https://p4.ssl.qhimg.com/t01f798992a265c6789.png)

从这个软件数据包来看，当要查询币数量和批量送礼物的时候就需要走http协议了。

至此整个产业链，也就完整的呈现出来了

[![](https://p4.ssl.qhimg.com/t013933f49c29065a90.jpg)](https://p4.ssl.qhimg.com/t013933f49c29065a90.jpg)





## 0x04 总结

1、人在做天在看，干坏事总会留下痕迹的，当然这肯定只是扫号产业中很小的一部分。

2、扫号这种产业一直都是伴随着整个互联网的，针对这些扫号的黑客，甲方的风控压力确实不小，要和这些黑产对抗，甲方的要走的路还很长

3、顺带说一句现在各大的云计算平台真的是成了各种黑客的保护地，上面什么样的黑产都有，也许要打击这些黑产，这些云平台也许应该负点责任了
