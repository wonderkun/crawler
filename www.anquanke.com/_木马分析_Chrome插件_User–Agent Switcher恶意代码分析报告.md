> 原文链接: https://www.anquanke.com//post/id/86892 


# 【木马分析】Chrome插件：User–Agent Switcher恶意代码分析报告


                                阅读量   
                                **197791**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t013e9257c44cd5d983.png)](https://p0.ssl.qhimg.com/t013e9257c44cd5d983.png)

**作者：c1tas@360CERT**



**0x00 背景介绍**



2017年9月9日，在v2ex论坛有用户表示Chrome中名为**User-Agent Switcher**的扩展可能存在未授权侵犯用户隐私的恶意行为。因为用户量大，此事引起了广泛关注，360CERT在第一时间对插件进行了分析，并发布了预警[https://cert.360.cn/warning/detail?id=866e27f5a3dd221b506a9bb99e817889](https://cert.360.cn/warning/detail?id=866e27f5a3dd221b506a9bb99e817889)



**0x01 行为概述**



360CERT经过跟踪分析，确认该插件将恶意代码隐写在正常图片中绕过Google Chrome市场的安全检查，并在没有征得用户同意的情况下，主动记录并上传用户的网页浏览地址并通过广告推广获利。



**0x02 攻击面影响**



**影响面**

经过360CERT研判后确认，**漏洞风险等级高，影响范围广**。

**影响版本**

Version 1.8.26

**DNS请求态势**

**uaswitcher.org**

[![](https://p3.ssl.qhimg.com/t016eaceb1f670e560b.png)](https://p3.ssl.qhimg.com/t016eaceb1f670e560b.png)

通过查看两个**User-Agent Switcher**的接受数据域名(**uaswitcher.org**)一个月内的记录，在2017年8月22日高点日活请求达到5万左右，在9月9日事件披露后至今依旧有4万左右的日活请求。

**the-extension.com &amp; api.data-monitor.info**

[![](https://p0.ssl.qhimg.com/t01eaacebc233c56cf4.png)](https://p0.ssl.qhimg.com/t01eaacebc233c56cf4.png)

通过查看两个**User-Agent Switcher**的payload推送域名和广告推广域名(**the-extension.com**;**api.data-monitor.info**)的记录，从2017年8约22日前访问曲线才开始上升，其中对payload推送的域名访问高点大概达到日活1.3万左右，对广告推广获取的域名访问高点大概达到日活1.1万左右，并于9月19日访问曲线开始下降。

注:该数据来自于:360网络安全研究院([http://netlab.360.com/](http://netlab.360.com/) )

**修复版本**

暂无



**0x03 详情**



**技术细节**

首先安装了该插件后,linux会在该目录下得到相应的**crx**文件解包出来的插件配置以及相关功能**js**文件目录

```
/home/r7/.config/google-chrome/Default/Extensions/ffhkkpnppgnfaobgihpdblnhmmbodake
```

[![](https://p2.ssl.qhimg.com/t0119aed7012441358d.png)](https://p2.ssl.qhimg.com/t0119aed7012441358d.png)

该目录的结构如下



```
1.8.26_0
├── css
│   ├── bootstrap.min.css
│   ├── options.css
│   └── popup.css
├── img
│   ├── active.png
│   ├── glyphicons-halflings.png
│   ├── glyphicons-halflings-white.png
│   ├── icon128.png
│   ├── icon16.png
│   ├── icon19.png
│   ├── icon38.png
│   └── icon48.png
├── js
│   ├── analytics.js
│   ├── background.js
│   ├── bootstrap.min.js
│   ├── content.js
│   ├── jquery.min.js
│   ├── JsonValues.js
│   ├── options.js
│   └── popup.js
├── manifest.json
├── _metadata
│   ├── computed_hashes.json
│   └── verified_contents.json
├── options.html
├── popup.html
└── promo.jpg

4 directories, 25 files
```

根据chrome插件编写原则**manifest.json**这个文件为核心配置文件

**canvas图片js代码隐藏**



那么现在直接从background.js看起 在background.js的70行处有一行经过js压缩的代码,进行beautify后

可以比较清楚的看到执行了这个promo函数,这里大部分代码的功能都是对promo.jpg这个图片文件的读取处理

**0x01**

[![](https://p2.ssl.qhimg.com/t01b9437c67e33af3b9.png)](https://p2.ssl.qhimg.com/t01b9437c67e33af3b9.png)

先看到**e.Vh**

[![](https://p5.ssl.qhimg.com/t016828872ba27b160a.png)](https://p5.ssl.qhimg.com/t016828872ba27b160a.png)

其中第一部分还原出的值为

[![](https://p0.ssl.qhimg.com/t0142d0d65b83d8c564.png)](https://p0.ssl.qhimg.com/t0142d0d65b83d8c564.png)

满足条件的地方是在**181787**这个值的地方**181787//4=45446**正好满足还原出的**list**长度 而值的内容都小于**10**,所以这就是为什么要放在A分量上,A分量的值255是完全不透明,而这部分值附加在245上.所以对图片的观感完全无影响

第二部分还原出的值为

[![](https://p1.ssl.qhimg.com/t01445b40ec1a9dea40.png)](https://p1.ssl.qhimg.com/t01445b40ec1a9dea40.png)

这一部分就稍微复杂一点

[![](https://p2.ssl.qhimg.com/t0180bf10a504526271.png)](https://p2.ssl.qhimg.com/t0180bf10a504526271.png)



```
in Vh for, y: 3
in Vh for, y: 6
in Vh for, y: 9
in Vh for, y: 12
in Vh for, y: 15
in Vh for, y: 18
in Vh for, y: 5
in Vh for, y: 8
in Vh for, y: 11
in Vh for, y: 14
in Vh for, y: 17
in Vh for, y: 4
in Vh for, y: 7
in Vh for, y: 10
in Vh for, y: 13
in Vh for, y: 16
```

可以看到**y**从**0**开始.当大于16的时候进行一次处理,而**y**有恒定的变化顺序**3,6,9,12,15,18,5,8,11,14,17,4,7,10,13,16**

而触发处理的是在**&gt;=16**这一条件下,构成(6,5,5)这样一个循环

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a9d524ce4c55e0aa.png)

再结合w的变换,只需要再安排好一个合适的数列，就能把大数拆分成(6,5,5)这样一组一组的由**0-9**组成的数

这就是为什么能以小于**10**的值将期望的值隐藏在**A**分量里

[![](https://p1.ssl.qhimg.com/t018c71f3f38f9ab81e.png)](https://p1.ssl.qhimg.com/t018c71f3f38f9ab81e.png)

这就达到了将js代码隐藏于图片的效果，并且对图片本身几乎无任何显示效果以及大小上的影响

而根据js中,**document.dafaultView[“Function”](n)()**这个方式,可以直接执行n中的js代码,所以直接尝试增加**document.write(n) **直接输出n的内容至页面

[![](https://p5.ssl.qhimg.com/t01e5bc1cc8ae1fdb91.png)](https://p5.ssl.qhimg.com/t01e5bc1cc8ae1fdb91.png)

[![](https://p4.ssl.qhimg.com/t011663cdbe18b983cd.png)](https://p4.ssl.qhimg.com/t011663cdbe18b983cd.png)

可以看到这确实是一段js代码

**隐藏JS代码执行**



可以看到,原本的代码是执行**i()**函数,而**i()**函数的内容是**setTimeout**这一定时执行函数,为了测试 直接提取出其中的执行函数进行执行

这些代码的功能按流程来说如下

1.首先**e(`{`‘act’: func1(‘0x2d’)`}`);**进行一个时间戳校验,满足一定时间后,从**https://the-extension.com**上下载js的payload

2.调用**chrome.storage.local.set**方法将这段js代码保存至本地缓存

```
Log/home/r7/.config/google-chrome/Default/Local Extension Settings/ffhkkpnppgnfaobgihpdblnhmmbodake/000003.log
```

这一文件中

3.再通过**r()[func1(‘0x1’)](a);**调用**r()**函数后再调用**a()**函数,执行了第二部保存下来的恶意js代码,进行的用户信息上传

**0x01**



首先是第一个技术,代码里的英文字符串90%都转换成了16进制的表示形式

例如

```
var _0x2126 = ['x63x6fx64x65', 'x76x65x72x73x69x6fx6e', 'x65x72x72x6fx72', 'x64x6fx77x6ex6cx6fx61x64', 'x69x6ex76x61x6cx69x64x4dx6fx6ex65x74x69x7ax61x74x69x6fx6ex43x6fx64x65', 'x54x6ax50x7ax6cx38x63x61x49x34x31', 'x4bx49x31x30x77x54x77x77x76x46x37', 'x46x75x6ex63x74x69x6fx6e', 'x72x75x6e', 'x69x64x6cx65', 'x70x79x57x35x46x31x55x34x33x56x49', 'x69x6ex69x74', 'x68x74x74x70x73x3ax2fx2fx74x68x65x2dx65x78x74x65x6ex73x69x6fx6ex2ex63x6fx6d', 'x6cx6fx63x61x6c', 'x73x74x6fx72x61x67x65', 'x65x76x61x6c', 'x74x68x65x6e', 'x67x65x74', 'x67x65x74x54x69x6dx65', 'x73x65x74x55x54x43x48x6fx75x72x73', 'x75x72x6c', 'x6fx72x69x67x69x6e', 'x73x65x74', 'x47x45x54', 'x6cx6fx61x64x69x6ex67', 'x73x74x61x74x75x73', 'x72x65x6dx6fx76x65x4cx69x73x74x65x6ex65x72', 'x6fx6ex55x70x64x61x74x65x64', 'x74x61x62x73', 'x63x61x6cx6cx65x65', 'x61x64x64x4cx69x73x74x65x6ex65x72', 'x6fx6ex4dx65x73x73x61x67x65', 'x72x75x6ex74x69x6dx65', 'x65x78x65x63x75x74x65x53x63x72x69x70x74', 'x72x65x70x6cx61x63x65', 'x64x61x74x61', 'x74x65x73x74', 'x69x6ex63x6cx75x64x65x73', 'x68x74x74x70x3ax2fx2f', 'x6cx65x6ex67x74x68', 'x55x72x6cx20x65x72x72x6fx72', 'x71x75x65x72x79', 'x66x69x6cx74x65x72', 'x61x63x74x69x76x65', 'x66x6cx6fx6fx72', 'x72x61x6ex64x6fx6d', 'x63x68x61x72x43x6fx64x65x41x74', 'x66x72x6fx6dx43x68x61x72x43x6fx64x65', 'x70x61x72x73x65'];
```

这是一个列表,里面存了很多字符串,因为js有个特性,在形如**chrome.storage.local**这种调用的时候 完全可以使用**chrome[“storage”][“local”]**这种方式

然后这个列表的顺序其实不准确,还存在一个复原列表的操作

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01815351509d5c930a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0166bd87e558885a3d.png)

这个才是复原后的顺序

**0x02**

针对上面的列表取值,特地用了一个函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017097bd875cc40bd3.png)

该函数作用就是把传入的16进制值转换为10进制,再在这个列表里作**index**,返回对应字符串

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0131aa1f768d6ca747.png)

可以看到大量采用这种形式的调用

**0x03**

可以看出代码中拥有大量的**Promise**对象

并且通过使用大量的箭头函数,是代码可读性并不如顺序执行那种思维出来的那么简单

[![](https://p3.ssl.qhimg.com/t01a86268a44bd0480d.png)](https://p3.ssl.qhimg.com/t01a86268a44bd0480d.png)

**下载恶意payload**

**[![](https://p5.ssl.qhimg.com/t01b6724243d6e3c2ee.png)](https://p5.ssl.qhimg.com/t01b6724243d6e3c2ee.png)**

[https://the-extension.com/?hash=jwtmv6kavksy5cazdf4leg66r](https://the-extension.com/?hash=jwtmv6kavksy5cazdf4leg66r)  为payload地址

[![](https://p0.ssl.qhimg.com/t01657ab325a5f7cb6e.png)](https://p0.ssl.qhimg.com/t01657ab325a5f7cb6e.png)

**第二部分恶意代码**

**用户信息上传**

很容易读到

[![](https://p0.ssl.qhimg.com/t01f85b0c6bdf553f3e.png)](https://p0.ssl.qhimg.com/t01f85b0c6bdf553f3e.png)

这个地方post了数据并且是往https://uaswitcher.org/logic/page/data 这个链接

这里可以看到，调用到.request方法的地方

[![](https://p4.ssl.qhimg.com/t01df90bdace9ca8f82.png)](https://p4.ssl.qhimg.com/t01df90bdace9ca8f82.png)

[![](https://p3.ssl.qhimg.com/t012ff0164b90be8ede.png)](https://p3.ssl.qhimg.com/t012ff0164b90be8ede.png)

然后调用了**fetchOverlayPattern**

可以看到其中的内容就是要传输出去的用户信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015d8b335c21b9f61f.png)

**广告推广部分**

代码部分

[![](https://p4.ssl.qhimg.com/t015714acc0a2a71ecc.png)](https://p4.ssl.qhimg.com/t015714acc0a2a71ecc.png) [![](https://p5.ssl.qhimg.com/t01140f9d12bfcf96b0.png)](https://p5.ssl.qhimg.com/t01140f9d12bfcf96b0.png)

这部分比较简单，就不过多赘述

获取到的推广跳转链接

[![](https://p2.ssl.qhimg.com/t01a8d81a9f7e9ccb0b.png)](https://p2.ssl.qhimg.com/t01a8d81a9f7e9ccb0b.png)

经过多次跳转后的页面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01339f3c1d8c5aba34.png)

**补充说明**

**RGBA**

红绿蓝透明 R – 红色 (0-255) G – 绿色 (0-255) B – 蓝色 (0-255) A – alpha 通道 (0-255; 0 是透明的，255 是完全可见的)0

**总结**

该插件通过隐藏在图片中的恶意js代码向控制者服务器请求新的恶意payload,恶意payload可以在用户不知情被控制者随时修改更新

建议用户尽快卸载该插件，或使用其他插件代替



**0x04 利用验证**

[![](https://p3.ssl.qhimg.com/t01dbd143f0679687b1.png)](https://p3.ssl.qhimg.com/t01dbd143f0679687b1.png)

可以看到当前的页面数据已经被获取了



**0x05 修复建议**



建议用户尽快卸载该插件，或使用其他插件代替



**0x06 时间线**



2017-09-09　事件披露

2017-09-10　360CERT发布预警通告

2017-09-20　360CERT完成全部细节分析



**0x07 参考文档**



Promise MDN web docs

[https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Promise](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Promise)

Arrow functions MDN web docs

[https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Functions/Arrow_functions](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Functions/Arrow_functions)

Pixel manipulation with canvas MDN web docs

[https://developer.mozilla.org/zh-CN/docs/Web/API/Canvas_API/Tutorial/Pixel_manipulation_with_canvas](https://developer.mozilla.org/zh-CN/docs/Web/API/Canvas_API/Tutorial/Pixel_manipulation_with_canvas)

js中||的作用

[https://www.zhihu.com/question/23720136?nr=1](https://www.zhihu.com/question/23720136?nr=1)

不能说的秘密——前端也能玩的图片隐写术 | AlloyTeam

[http://www.alloyteam.com/2016/03/image-steganography/](http://www.alloyteam.com/2016/03/image-steganography/)
