> 原文链接: https://www.anquanke.com//post/id/86852 


# 【技术分享】利用威胁情报数据平台拓展APT攻击线索一例


                                阅读量   
                                **97736**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01a0e0e1a446fdcfce.jpg)](https://p3.ssl.qhimg.com/t01a0e0e1a446fdcfce.jpg)

<br>

**简介**

****

当我们说起APT攻击线索的发现，似乎是一个挺神秘的事，安全厂商往往说得云山雾罩，如果现在你问如何知道某件事情的时侯，得到的回答往往是：”嗯，我们用了机器学习”，行业外的人除了觉得高端以外基本得不到有用的信息。然而，发现高级的定向攻击是否一定需要高级的分析手段？答案是：未必。今天我们就举一个简单的例子，分析对象还是我们的老朋友：**海莲花APT团伙**。



**线索**

****

2017年5月14日FireEye公司发了一个揭露**APT32（海莲花）团伙**新近活动的分析，描述了攻击过程的细节和一些工具及网络相关的IOC。文章的链接如下：

[https://www.fireeye.com/blog/threat-research/2017/05/cyber-espionage-apt32.html](https://www.fireeye.com/blog/threat-research/2017/05/cyber-espionage-apt32.html) 

这些信息当然已经收录到360威胁情报中心数据平台里，搜索一下其中一个C&amp;C域名：**high.vphelp.net**，我们得到如下的输出页面：

[![](https://p4.ssl.qhimg.com/t0116389f657bfed5e7.png)](https://p4.ssl.qhimg.com/t0116389f657bfed5e7.png)

右下角的可视化分析已经把FireEye报告中涉及的所有IOC都做了关联展示。在左边的相关安全报告，也理所当然地提供了FireEye文章的原始链接，除此以外我们还发现了另外一个指向到著名沙箱Payload Security上的某个样本执行沙箱结果信息链接，相应的文件SHA256为**e56905579c84941dcdb2b2088d68d28108b1350a4e407fb3d5c901f8e16f5ebc**。点击过去看一下细节：

[![](https://p0.ssl.qhimg.com/t01efe030ce500af79e.png)](https://p0.ssl.qhimg.com/t01efe030ce500af79e.png)

嗯，一个越南语文件名的样本，这很海莲花。看一下它的网络行为：

[![](https://p0.ssl.qhimg.com/t017b3a9879529f9b1a.png)](https://p0.ssl.qhimg.com/t017b3a9879529f9b1a.png)

可以看到样本涉及一组4个的C&amp;C域名：



```
push.relasign.org
seri.volveri.net
high.vphelp.net
24.datatimes.org
```

这也是海莲花相关样本的风格，一般会在同一天注册4-5个域名用于C&amp;C通信。我们知道Payload Security上存储了大量样本的沙箱行为日志数据，那么我们是不是可以在上面找找更多类似的样本呢？这个值得一试。怎么做呢？试试最简单的关键字匹配。



**拓展**

****

注意到上面那个已知样本连接C&amp;C IP的进程名了吗？多年从事恶意代码分析的经验告诉我们，这个**sigverif.exe**进程在恶意代码的活动中并不常见。所以我们可以用sigverif.exe作为关键词尝试搜索，**不必用Payload Security网站自己的搜索选项，其实Google提供的全文搜索功能更为强大**，用”site:”指定目标网站并指定关键字” sigverif.exe”，Google给我们的结果只有2页，下面是第1页的结果：

[![](https://p5.ssl.qhimg.com/t01f6b90c6561caaf66.png)](https://p5.ssl.qhimg.com/t01f6b90c6561caaf66.png)

这里输出的命中列表中最后一项就是我们已知会连接**high.vphelp.net **C&amp;C域名的海莲花样本。由于条目总命中数并不多，所以我们可以逐一检查每个命中样本与已知样本的相似度。查看列表中的第一个样本，文件SHA256为**2bbffbc72a59efaf74028ef52f5b637aada59650d65735773cc9ff3a9edffca5**，相应的恶意行为判定如下：

[![](https://p4.ssl.qhimg.com/t0128937246ec8bf35d.png)](https://p4.ssl.qhimg.com/t0128937246ec8bf35d.png)

往前翻一下我们线索样本的行为判定（**进程调用关系和字符串**），可以确认两者几乎是完全相同的，这应该就是另一个相同功能的海莲花样本。接下来检查这个样本连接的C&amp;C域名和IP：

[![](https://p2.ssl.qhimg.com/t01baec34bc6494bef6.png)](https://p2.ssl.qhimg.com/t01baec34bc6494bef6.png)

在这里我们发现了另外4个**从前未知的**C&amp;C域名：



```
news.sitecontents.org
cdn.mediastatics.net
image.lastapi.org
time.synzone.org
```

域名注册于2016年8月10日，并做了隐私保护，海莲花团伙的惯用操作，在各种威胁情报平台上还查不到这些域名的标签信息。它们都曾解析到IP **81.95.7.12**，域名与IP与已知的其他海莲花的攻击活动没有关联，在基础设施方面隔离比较彻底，这也是近期海莲花活动的趋势。根据360威胁情报中心对这几个域名的监控，国内没有发现连接的迹象，所以相关的样本极有可能被用于针对中国以外目标的攻击。如此，我们就从一个已知的域名出发，通过关联的样本，提取其静态特征搜索到同类样本，最终挖掘到以前我们所未知的样本和C&amp;C基础设施。



**启示**



APT活动事件层面的分析本质上寻找关联点并利用关联点基于数据进行拓展的游戏，下面是360威胁情报中心整理的基于洛马Cyber Kill Chain模型关联点：

[![](https://p4.ssl.qhimg.com/t01e0ee337a8cab25a7.png)](https://p4.ssl.qhimg.com/t01e0ee337a8cab25a7.png)

APT的攻防最终会落到人和数据的对抗，很多时候数据就在那儿，在了解对手TTP类的攻防细节并且对数据敏感度高的分析人员手里，通过层层剖析就能得到拓展视野获取更多的威胁情报。360威胁情报中心基于自己的判定对大量的数据打了标签，部分标签是对外输出的，这些标签其实就是威胁情报，用户所要做的就是问对的问题。

<br>

**IOC**

****

**海莲花团伙新挖掘到的威胁情报******

[![](https://p2.ssl.qhimg.com/t01d882eb375593c0de.png)](https://p2.ssl.qhimg.com/t01d882eb375593c0de.png)

**文件HASH**

2bbffbc72a59efaf74028ef52f5b637aada59650d65735773cc9ff3a9edffca5
