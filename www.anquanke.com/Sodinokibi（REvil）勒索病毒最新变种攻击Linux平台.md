> 原文链接: https://www.anquanke.com//post/id/245797 


# Sodinokibi（REvil）勒索病毒最新变种攻击Linux平台


                                阅读量   
                                **305703**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01808abb660e086c0e.jpg)](https://p2.ssl.qhimg.com/t01808abb660e086c0e.jpg)



## 前言

近日，国外安全研究人员爆光了一个Linux平台上疑似Sodinokibi勒索病毒家族最新样本，如下所示：

[![](https://p3.ssl.qhimg.com/t01cf359852afb7279e.png)](https://p3.ssl.qhimg.com/t01cf359852afb7279e.png)

Sodinokibi(REvil)勒索病毒的详细分析以及资料可以参考笔者之前的一些文章，这款勒索病毒黑客组织此前一直以Windows平台为主要的攻击目标，目前首次发现这款勒索病毒Linux平台上的最新变种样本，未来会不会有相关的安全事件爆发，需要持续关注。



## 分析

笔者从一个恶意软件平台上下载到病毒样本，病毒运行之后，如下所示：

[![](https://p1.ssl.qhimg.com/t01769d7a18cb555063.png)](https://p1.ssl.qhimg.com/t01769d7a18cb555063.png)

样本的基础结构如下所示：

[![](https://p3.ssl.qhimg.com/t01bc2153695c83d2ff.png)](https://p3.ssl.qhimg.com/t01bc2153695c83d2ff.png)

获取勒索病毒中内置的配置文件信息，如下所示：

[![](https://p0.ssl.qhimg.com/t0195263c889eb2b86e.png)](https://p0.ssl.qhimg.com/t0195263c889eb2b86e.png)

可以发现这个配置文件信息内容与此前Sodinokibi勒索病毒的非常相似，获取到的配置信息，如下所示：

[![](https://p0.ssl.qhimg.com/t01775d424c973bfcad.png)](https://p0.ssl.qhimg.com/t01775d424c973bfcad.png)

生成文件加密后缀名qoxaq，如下所示：

[![](https://p2.ssl.qhimg.com/t010e65f0b84e905498.png)](https://p2.ssl.qhimg.com/t010e65f0b84e905498.png)

生成勒索提示信息文件内容，如下所示：

[![](https://p1.ssl.qhimg.com/t010a85428e8b2b8d31.png)](https://p1.ssl.qhimg.com/t010a85428e8b2b8d31.png)

调用esxcli命令关闭虚拟机进程，如下所示：

[![](https://p5.ssl.qhimg.com/t01182c7a2294568493.png)](https://p5.ssl.qhimg.com/t01182c7a2294568493.png)

相关的命令行，如下：

esxcli —formatter=csv —format-<br>
param=fields==”WorldID,DisplayName” vm<br>
process list | awk -F “\”**,\”**“ ‘,27h,’`{`system(“esxcli vm process kill —type=force —world-id=” $1)`}`

遍历目录，加密文件，如下所示：

[![](https://p5.ssl.qhimg.com/t01237525508c1a1533.png)](https://p5.ssl.qhimg.com/t01237525508c1a1533.png)

加密文件的过程，如下所示：

[![](https://p0.ssl.qhimg.com/t01a372438976b36cfe.png)](https://p0.ssl.qhimg.com/t01a372438976b36cfe.png)

生成的勒索提示信息文件，如下所示：

[![](https://p2.ssl.qhimg.com/t01a2c5c1eec0d4f2c7.png)](https://p2.ssl.qhimg.com/t01a2c5c1eec0d4f2c7.png)

加密完成之后，生成加密完成提示信息，显示一共有多少个文件被加密了，如下所示：

[![](https://p5.ssl.qhimg.com/t0157d342396d92e991.png)](https://p5.ssl.qhimg.com/t0157d342396d92e991.png)

通过勒索病毒的代码特征和行为特征，国外安全研究人员将这款勒索病毒归因为Sodinokibi勒索病毒的家族，笔者在访问这款勒索病毒解密网站的时候出现在问题，可能是这勒索病毒黑客组织正在维护解密网站服务器的后台。

笔者之前发现DarkSide这款勒索病毒针对Linux平台VMware ESXI的攻击，最近一款新型的勒索病毒DarkRadiation也是专门针对各种Linux平台进行攻击，笔者后面会给大家进行详细分析介绍，现在Sodinokibi勒索病毒也开始针对Linux平台进行攻击了，可以预测未来可能会有更多的勒索病毒黑客组织将目标转向Linux平台，扩大攻击平台的范围，获取更多的利益。



# <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

勒索病毒黑客组织一直在更新，从来没有停止过发起新的攻击，寻找新的目标，未来几年勒索攻击仍然是全球最大的安全威胁，笔者总结出一些勒索攻击发展的几个趋势，供大家参考：

(1)”双重”、”三重”勒索模式逐渐变多，也许会有其他更多的模式出现。<br>
(2)定向攻击勒索，采用APT攻击方式，为了利益最大化，会选择性的攻击行业“头部”大企业。<br>
(3)基于RAAS模式的新型勒索病毒组织会越来越多，同时核心运营团队会逐步形成“小圈子”模式，降低风险，黑客团队会向“精英化”团伙运营模式发展。<br>
(4)通过各种不同的恶意软件分发传播勒索病毒的形式会越来越多。<br>
(5)勒索攻击针对的平台会越来越多，未来针对Linux类系统的云计算平台勒索攻击会增多。<br>
(6)勒索攻击的支付方式可能会变化，除了BTC，黑客还会选择各多其他虚拟货币或其他方式支付。<br>
(7)勒索攻击，企业数据是关键，窃取企业的数据，已经成了勒索攻击一个环节。
