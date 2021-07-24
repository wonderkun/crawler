> 原文链接: https://www.anquanke.com//post/id/86719 


# 【病毒分析】360烽火实验室：“WireX Botnet”事件Android样本分析报告


                                阅读量   
                                **122491**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01d5d7a90982e36eee.jpg)](https://p5.ssl.qhimg.com/t01d5d7a90982e36eee.jpg)

**<br>**

**C&amp;C服务器地址**

****

WireX家族病毒基本上都会在内部硬编码存放两个URL地址（部分变种的URL经过加密），变种A在内部硬编码了如下两个URL



```
http://u.*******.store/?utm_source=tfikztteuic
http://g.*******.store/?utm_source=tfikztteuic
```

这些URL地址是病毒的C&amp;C Server的地址，用于返回要攻击的网站的信息，不同之处在于，对这两个URL返回的信息，处理方式不同，执行的恶意行为也不同。

<br>

**UDP Flood攻击**

****

对于以u开头的URL地址，比如

```
http://u.*******.store/?utm_source=tfikztteuic
```

（实际测试不能正常返回数据，以下是根据代码逻辑进行描述的），返回数据分为两部分，一个要攻击的主机地址，一个是端口，中间使用字符串“snewxwri”分割，代码中对返回数据处理如下：

 [![](https://p0.ssl.qhimg.com/t01d6664dfc7c8c8669.jpg)](https://p0.ssl.qhimg.com/t01d6664dfc7c8c8669.jpg)

获得主机地址和端口号之后，会创建50个线程，每个线程中都会连接该主机和端口，开启socket之后，使用udp协议发送随机数据，每次回发送512个字节的数据，一个线程中一共会发送 10000000 (一千万)次，也就是 10000000512=5120000000 字节的数据，因为一共实现了创建了50个线程，所以，理论上会发送10000000512*50=256000000000（2560亿）字节，实现代码如下所示：

 [![](https://p0.ssl.qhimg.com/t01f27fe21929793d47.png)](https://p0.ssl.qhimg.com/t01f27fe21929793d47.png)

[![](https://p4.ssl.qhimg.com/t016d48046c29ae31ca.png)](https://p4.ssl.qhimg.com/t016d48046c29ae31ca.png)

<br>

**Deceptive Access Attack**

****

对于以g开头的URL地址， 比如 

```
http://g.*******.store/?utm_source=tfikztteuic
```

，返回数据分为3部分，分别是访问要攻击的网站的URL、UserAgent和Referer，使用硬编码的字符串（比如**snewxwri** ）进行分割，代码中对返回数据处理如下：

 [![](https://p2.ssl.qhimg.com/t01238dc42668d687a9.jpg)](https://p2.ssl.qhimg.com/t01238dc42668d687a9.jpg)

获得要攻击网站用到的**URL**、**UserAgent**和**Referer**后，会创建20个Webview，然后使用每个WebView访问要攻击的网站，代码实现如下：

 [![](https://p5.ssl.qhimg.com/t01611aa77bff39fde9.png)](https://p5.ssl.qhimg.com/t01611aa77bff39fde9.png)

**<br>**

**Deceptive Click Attack**

****

变种B内置了2个URL地址，如下：



```
http://ww68.c.********.us/?utm_source=tfikztteuic
http://ww68.d.********.us/?utm_source=tfikztteuic
```

请求这两个URL返回的数据是类似的，都是在HTML的**title**中设置了一段内容，这段内容使用一个硬编码的字符串（比如**”eindoejy”**）分隔成3或者4部分，前3部分都是一样的，一个**URL**，一段**JS代码**，一个**UserAgent**，后面可能还有一个字段，猜测为国家名字缩写，该样本中为**CN**（代表中国？）。请求你的地址和返回的数据，类似下图：

 [![](https://p0.ssl.qhimg.com/t013cb2db25e537e6ec.jpg)](https://p0.ssl.qhimg.com/t013cb2db25e537e6ec.jpg)

该病毒对这些数据的处理方式是，使用WebView加载返回URL，然后在页面加载完成后，执行那段JS代码，JS代码的功能是从页面中所有的URL link（通过查找html的a标签获得）中，随机挑选一个，模拟鼠标事件进行点击，实现代码如下：

 [![](https://p5.ssl.qhimg.com/t0152969275c01084b0.jpg)](https://p5.ssl.qhimg.com/t0152969275c01084b0.jpg)

实现模拟鼠标点击JS代码如下：

 [![](https://p4.ssl.qhimg.com/t011f59dadb68114eb4.png)](https://p4.ssl.qhimg.com/t011f59dadb68114eb4.png)

**<br>**

**Attack Controller**

****

上述几种攻击的实现都是位于某个Android Service中，那么这几种攻击是怎么启动的呢？通过逆向分析APK得知, 该APK注册了监听某些事件的**Broadcast Receiver**，比如network connectivity change、device admin enabled等，在这些Receiver中，会启动Attack Controller这个Service， Attack Controller负责启动各种Attack，代码实现如下：

 [![](https://p4.ssl.qhimg.com/t012875db5f4f7ecb55.png)](https://p4.ssl.qhimg.com/t012875db5f4f7ecb55.png)

不同的变种，实现方式有些差别，攻击的强度也又有所差别，这个变种中，每隔**55秒**都会重启一次攻击。

<br>

**受影响app列表(部分)**

****

[![](https://p1.ssl.qhimg.com/t01a9a52f85527528fe.png)](https://p1.ssl.qhimg.com/t01a9a52f85527528fe.png)

详细内容请看：

[https://appscan.io/monitor.html?id=59a4ddf60272383df95153ea](https://appscan.io/monitor.html?id=59a4ddf60272383df95153ea)

<br>

**360烽火实验室**

****

360烽火实验室，致力于Android病毒分析、移动黑产研究、移动威胁预警以及Android漏洞挖掘等移动安全领域及Android安全生态的深度研究。作为全球顶级移动安全生态研究实验室，360烽火实验室在全球范围内首发了多篇具备国际影响力的Android木马分析报告和Android木马黑色产业链研究报告。实验室在为360手机卫士、360手机急救箱、360手机助手等提供核心安全数据和顽固木马清除解决方案的同时，也为上百家国内外厂商、应用商店等合作伙伴提供了移动应用安全检测服务，全方位守护移动安全。

[![](https://blogs.360.cn/360mobile/files/2016/09/image1-1.png)](https://blogs.360.cn/360mobile/files/2016/09/image1-1.png)
