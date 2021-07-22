> 原文链接: https://www.anquanke.com//post/id/187517 


# 放假之前EvaRichter勒索病毒来袭


                                阅读量   
                                **501685**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t015e339673b1f507be.jpg)](https://p5.ssl.qhimg.com/t015e339673b1f507be.jpg)



目前勒索病毒仍然是全球最大的威胁，最近一年针对企业的勒索病毒攻击越来越多，大部分勒索病毒是无法解密的，并且不断有新型的勒索病毒出现，各企业一定要保持高度的重视，马上放假了，一款新型勒索病毒来袭……

近日国外某独立恶意软件安全研究人员曝光了一个新型的勒索病毒，如下所示：

[![](https://p2.ssl.qhimg.com/t012b23de611c642693.png)](https://p2.ssl.qhimg.com/t012b23de611c642693.png)

然后有人回复说是EvaRichter勒索病毒，并给出了id-ransomware博客地址，如下所示：

[![](https://p5.ssl.qhimg.com/t01428f4c197611eee0.png)](https://p5.ssl.qhimg.com/t01428f4c197611eee0.png)

这款勒索病毒之所以勾起我的兴趣，主要是它与之前的GandCrab、Sodinokibi、GermanWiper、NEMTY等勒索有某些类似之处，都将桌面壁纸修改成蓝色了，笔者通过MD5在app.any.run上找到了相应的样本，如下：

[![](https://p2.ssl.qhimg.com/t01729617fbf852d4db.png)](https://p2.ssl.qhimg.com/t01729617fbf852d4db.png)

样本被人在24号上传到了VT上，依据上传的时间判断可能就是国外那个独立恶意软件研究员上传的，从app.any.run上下载样本，图标使用了类似微信的图标，如下所示：

[![](https://p0.ssl.qhimg.com/t01619c00fd3a903dca.png)](https://p0.ssl.qhimg.com/t01619c00fd3a903dca.png)

运行之后，加密的文件后缀为随机文件，如下所示：

[![](https://p3.ssl.qhimg.com/t01e6d77152fbaf3cc2.png)](https://p3.ssl.qhimg.com/t01e6d77152fbaf3cc2.png)

勒索病毒会修改桌面壁纸为蓝色，如下所示：

[![](https://p0.ssl.qhimg.com/t01f8f83e8e0908af49.png)](https://p0.ssl.qhimg.com/t01f8f83e8e0908af49.png)

勒索提示信息文本文件[加密后缀随机名]_how_to_decrypt.txt，内容如下所示：

[![](https://p3.ssl.qhimg.com/t018e9100100323fb08.png)](https://p3.ssl.qhimg.com/t018e9100100323fb08.png)

访问勒索病毒解密网址，如下所示：

[![](https://p0.ssl.qhimg.com/t012b3a6b0be5224a43.png)](https://p0.ssl.qhimg.com/t012b3a6b0be5224a43.png)

输入勒索提示信息中的Access Code码之后，如下所示：

[![](https://p2.ssl.qhimg.com/t0111a17bef11009c3e.png)](https://p2.ssl.qhimg.com/t0111a17bef11009c3e.png)

黑客的BTC钱包地址：14Biqrf2fryuGNDrMDPchPCQeEjzZkqaLi，勒索赎金七天之内为：0.1521163 BTC，如下所示：

[![](https://p4.ssl.qhimg.com/t01ecbadf503f51e96b.png)](https://p4.ssl.qhimg.com/t01ecbadf503f51e96b.png)

最近BTC降了一点，我们按今天BTC的市价来算，如下：

[![](https://p0.ssl.qhimg.com/t01ac498d619fefa6b9.png)](https://p0.ssl.qhimg.com/t01ac498d619fefa6b9.png)

等于0.1521163 X 8405.59 = 1278美元(七天之内解密的价格)

此勒索病毒同样采用了高强度的代码混淆技术，简单的反调试技术，核心的勒索病毒代码被多层封装起来了，通过动态调试，解密出外壳的封装代码，如下所示：

[![](https://p3.ssl.qhimg.com/t01e997ce2a3d2dc848.png)](https://p3.ssl.qhimg.com/t01e997ce2a3d2dc848.png)

继续跟踪调试，最后解密出核心的勒索病毒代码，如下所示：

[![](https://p2.ssl.qhimg.com/t0143e4a02f5ff9dd45.png)](https://p2.ssl.qhimg.com/t0143e4a02f5ff9dd45.png)

解密出完整的勒索病毒核心是一个PE文件，采用Delphi语言进行编写，如下所示：

[![](https://p0.ssl.qhimg.com/t01b40b21f752eb8fcf.png)](https://p0.ssl.qhimg.com/t01b40b21f752eb8fcf.png)

查看入口代码，如下所示：

[![](https://p5.ssl.qhimg.com/t010ed65eabb960d8e3.png)](https://p5.ssl.qhimg.com/t010ed65eabb960d8e3.png)

使用IDA查看字符串信息，里面包含勒索相关信息，如下所示：

[![](https://p1.ssl.qhimg.com/t01d16743d8f3592677.png)](https://p1.ssl.qhimg.com/t01d16743d8f3592677.png)

此勒索病毒最后还会删除磁盘卷影副本等操作，如下所示：

[![](https://p3.ssl.qhimg.com/t014a2cc576dbb8ff2a.png)](https://p3.ssl.qhimg.com/t014a2cc576dbb8ff2a.png)

从勒索病毒的核心代码，我发现这款勒索病毒与之前我分析过的一款新型的勒索病毒GermanWiper创建的互斥变量一模一样，都是HSDFSD-HFSD-3241-91E7-ASDGSDGHH，GermanWiper勒索病毒的核心代码同样是使用Delphi语言编写的，于是我将两款勒索病毒的核心Payload代码进行对比，如下所示：

[![](https://p0.ssl.qhimg.com/t01d6a7272f752a8373.png)](https://p0.ssl.qhimg.com/t01d6a7272f752a8373.png)

代码相似度也高达82%，所以我觉得这款勒索病毒应该是GermanWiper最新变种，国外安全研究人员又取了一个名字叫：EvaRichter勒索病毒，还是按国外安全研究人员的名字命名吧

自从GandCrab勒索病毒于今年6月1 号，宣布停止运营之后，虽然后面再也没有见到过GandCrab的最新版本出现，然后它的影子似乎一直都在，比如现在比较流行的Sodinokibi勒索病毒，国外很多报道直指Sodinokibi与GandCrab有千丝万缕的关系，前面我就说过GandCrab勒索病毒虽然结束了，背后的运营团队只是宣布停止GandCrab勒索病毒的运营，它会不会继续运营其他勒索病毒家族呢？也许只是GandCrab勒索病毒的开发者不想开发了，它背后的运营团队会不会接着运营其它病毒呢？勒索病毒已经成为了黑产来钱最快的方式之一，大部分做黑产的不就是为了赚大钱吗？难怪会放弃这么好赚钱的机会？

GermanWiper勒索病毒上个月流行过一段时间，这款勒索病毒后面会不会大面积传播，需要持续的关注与跟踪，以前做黑产的都喜欢在放假的时候搞点事情，因为对于做黑产是没有休息日，而且越是放假，越容易搞一些活动，捆绑一些木马让用户主动下载，做黑产的为了搞钱，每天都在寻找不同的攻击目标，通过各种漏洞+恶意软件对目标进行攻击，获取暴利

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/n0RAki0zw6AeBqANHQOptA)
