> 原文链接: https://www.anquanke.com//post/id/91627 


# Trojan.AndroidOS.Loapi：Android端恶意软件中的多面手


                                阅读量   
                                **137577**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Nikita Buchka, Anton Kivva, Dmitry Galov，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/jack-of-all-trades/83470/](https://securelist.com/jack-of-all-trades/83470/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01fb05749dff2c34b7.jpg)](https://p0.ssl.qhimg.com/t01fb05749dff2c34b7.jpg)



## 写在前面的话

其实大家都知道，我们的智能手机一不小心就会感染恶意软件，哪怕你只从Google的官方应用商店（Google Play）下载软件也一样救不了你。但如果你喜欢从其他地方（除官方应用商店之外）下载软件的话，那你估计够呛了，因为这些第三方商店中充斥着大量伪造的以及未进行安全检测的应用程序。<br>
话虽如此，但针对安卓操作系统的恶意软件可不仅仅会在非官方应用商城中传播，它们还会利用恶意广告、SMS垃圾短信以及其他各种技术来进行传播。在各种针对安卓平台的恶意软件威胁中，我们发现了一个有趣的样本实例-Trojan.AndroidOS.Loapi。这个木马拥有十分复杂的模块化结构，这意味着它可以进行各种恶意活动，例如挖矿、给用户不断弹出烦人的广告、以及利用受感染设备发动DDoS（分布式拒绝服务）攻击等等。而在此之前，我们从未见过功能如此之多的移动端恶意软件，它足以配得上“多面手”这个称号了。



## 传播与感染

Loapi木马家族的样本主要通过恶意广告活动来进行传播，当用户被重定向到攻击者所控制的恶意Web资源后，恶意文件将会被下载到目标用户的安卓手机上。我们目前已经发现了超过20个这样的恶意资源，它们有些指向的是热门的反病毒厂商官网，有些则指向的是著名的色情网站。如下图所示，Loapi会用很多反病毒产品或者成人内容App来伪装自己：<br>[![](https://p0.ssl.qhimg.com/t018f647267e3508f39.png)](https://p0.ssl.qhimg.com/t018f647267e3508f39.png)安装完成之后，恶意应用会尝试获取设备的管理员权限，并不停地申请权限直到用户点击“同意”为止。Trojan.AndroidOS.Loapi还会检测设备是否已经root过，但它并不会使用root权限。毫无疑问，它肯定会在将来的某些新模块中使用root权限。<br>[![](https://p4.ssl.qhimg.com/t0189a5da4d4203c7b6.png)](https://p4.ssl.qhimg.com/t0189a5da4d4203c7b6.png)获取到设备的管理员权限之后，恶意软件将会在菜单中隐藏自己的图标，或使用各种反病毒产品来伪装自己：<br>[![](https://p3.ssl.qhimg.com/t018b122971b83a86a9.png)](https://p3.ssl.qhimg.com/t018b122971b83a86a9.png)



## 自我保护

Loapi会使用各种方法来防止用户调用设备管理器权限，如果用户尝试移除恶意软件的相关权限，恶意将会锁定屏幕并关闭设备管理器的设置窗口，然后执行以下代码：<br>[![](https://p0.ssl.qhimg.com/t01520c157f136a17ce.png)](https://p0.ssl.qhimg.com/t01520c157f136a17ce.png)除了这种较为常见的保护技术之外，我们还在其自我保护机制中发现了一个非常有趣的功能。该木马可以从远程C&amp;C服务器接收一个恶意应用程序列表，它会使用这个列表来监控这些恶意软件的安装、启动和运行过程。如果其中一个App安装并启动之后，该木马便会显示一条伪造的信息并告知用户它成功检测到了一个恶意软件，并提示用户将其删除：<br>[![](https://p0.ssl.qhimg.com/t01a36af9d6d17891ea.png)](https://p0.ssl.qhimg.com/t01a36af9d6d17891ea.png)这条信息会不断地循环显示，所以如果用户点击“取消”之后，这条信息将会不断地重复弹出，直到用户同意删除应用程序为止。



## 层级架构

[![](https://p4.ssl.qhimg.com/t01ac00f7c069f254f7.png)](https://p4.ssl.qhimg.com/t01ac00f7c069f254f7.png)下面给出的是该木马的架构详情：
1. 在初始阶段，恶意应用会从“assets”目录中加载一个文件，并使用Base64对其进行解码，最后使用异或操作将其解密。App签名哈希将作为密钥使用，并得到一个DEX文件（Payload），然后木马会使用ClassLoader来加载这个Payload。
<li>在第二阶段，恶意应用会将目标设备信息以JSON格式数据发送至中央C&amp;C服务器（hxxps://api-profit.com）：<br>[![](https://p0.ssl.qhimg.com/t018081798f0858bd9e.png)](https://p0.ssl.qhimg.com/t018081798f0858bd9e.png)<br>
服务器所返回的响应命令格式如下所示：<br>[![](https://p1.ssl.qhimg.com/t017da807df2175d0ad.png)](https://p1.ssl.qhimg.com/t017da807df2175d0ad.png)<br>
其中，列表installs中包含的是需要下载并执行的模块ID；列表removes中包含的是需要删除的模块ID；列表domains中包含的是C&amp;C服务器的域名；而reservedDomains则是一个包含了后备域名的列表；hic标记代表的是是否会给用户显示应用程序图标；列表dangerousPackages中包含的是该木马需要阻止安装和运行的应用程序（自我保护机制）。</li>
在第三阶段，该木马的功能模块会被下载并初始化，接下来我们一起来看一看我们从攻击者的服务器中获取到了哪些攻击模块。



## 恶意广告模块

[![](https://p0.ssl.qhimg.com/t01f498e115f7061c86.png)](https://p0.ssl.qhimg.com/t01f498e115f7061c86.png)目的和功能：这个模块可以用来在目标设备上强制显示广告，其大致功能如下。<br>
-显示视频广告和标语；<br>
-打开指定的URL；<br>
-在目标设备上创建快捷图标；<br>
-显示通知；<br>
-在热门社交网络中打开页面，例如Facebook和Instagram等；<br>
-下载并安装其他应用程序；<br>
我们从攻击者服务器中接收到的广告信息如下所示：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01824c0e8747b4fff4.png)在处理这项任务时，应用程序会发送一个隐藏请求，其中包含了特殊的User-Agent以及指向Web页面hxxps://ronesio.xyz/advert/api/interim的引用，而这个地址将会重定向到一个包含了恶意广告的页面。



## SMS短信模块

目的和功能：这个模块用来隐藏Web页面所要执行的JavaScript代码，并强制用户订阅各种付费服务。大多数情况下，移动运营商会给用户发送短信以确认付费服务的订阅，但是这个木马的SMS短信模块会自动给这种确认短信发送回复确认。除此之外，这个模块还可以用来进行Web页面爬取。比如说，下面给出的就是其中一个Web页面爬取示例：<br>[![](https://p5.ssl.qhimg.com/t016a477e6ad32e460a.png)](https://p5.ssl.qhimg.com/t016a477e6ad32e460a.png)<br>
在我们的测试过程中（24小时），这个模块在目标设备上总共尝试打开了28000多个不同的URL地址。



## 代理模块

目的和功能：这个模块用来实现一个HTTP代理服务器，它允许攻击者给目标设备发送HTTP请求。这也就意味着，攻击者将能够利用目标设备来发动DDoS攻击。除此之外，该模块还能改变目标设备的网络连接类型，例如将移动数据修改成Wi-Fi。



## 挖矿模块（门罗币）

目的和功能：这个模块可以利用目标设备来挖门罗币，部分挖矿代码如下所示：<br>[![](https://p5.ssl.qhimg.com/t013ca37cefcd4c7ab4.png)](https://p5.ssl.qhimg.com/t013ca37cefcd4c7ab4.png)<br>
上述代码使用了下列参数：

```
-url：矿池地址，“stratum+tcp://xmr.pool.minergate.com:45560”
-this.user：用户名、以及从列表中选出的随机值（“lukasjeromemi@gmail.com”, “jjopajopaa@gmail.com”, “grishaobskyy@mail.ru”, “kimzheng@yandex.ru”, “hirt.brown@gmx.de”, “swiftjobs@rambler.ru”, “highboot1@mail333.com”, “jahram.abdi@yandex.com”, “goodearglen@inbox.ru”, girlfool@bk.ru）
-password：常量值“qwe”
```



## 总结

Loapi是目前一种极具代表性的安卓端恶意软件，它的开发者几乎已经将目前所有的攻击技术都融入在里面了。比如说，该木马会强制用户订阅付费服务、发送短信至任何号码、生成流量并通过恶意广告来赚钱、使用目标设备的计算能力进行挖矿、以及执行各种互联网攻击行为等等。不过，该木马唯一缺失的功能就是“网络间谍”功能，但这种木马所采用的模块化设计允许开发人员随时向其添加这种功能。



## P.S.

在分析这款恶意软件的过程中，我们在一台测试设备上对其进行了动态分析，而下图显示的是两天之后的实验设备：<br>[![](https://p1.ssl.qhimg.com/t01c17b496a37ea82f8.png)](https://p1.ssl.qhimg.com/t01c17b496a37ea82f8.png)由于恶意软件的挖矿模块会不断生成流量并消耗计算资源，手机电池已经澎胀变形并撑破了手机后盖。



## C&amp;C服务器

```
ronesio.xyz (恶意广告模块)
api-profit.com:5210 (SMS短信模块和挖矿模块)
mnfioew.info (网络爬虫)
mp-app.info (代理模块)
```



## 域名

该木马用于下载恶意软件/Payload的Web资源列表如下所示：<br>[![](https://p3.ssl.qhimg.com/t01c0c913d95991cca3.png)](https://p3.ssl.qhimg.com/t01c0c913d95991cca3.png)
