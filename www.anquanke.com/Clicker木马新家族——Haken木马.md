
# Clicker木马新家族——Haken木马


                                阅读量   
                                **649752**
                            
                        |
                        
                                                                                    



[![](./img/200955/t01bfa961d0c3cf3271.jpg)](./img/200955/t01bfa961d0c3cf3271.jpg)



概述：Clicker木马是广泛的恶意程序，旨在提高网站访问率在线赚钱。它们通过单击链接和其他交互式元素来模拟网页上的用户操作，实现无声地模拟与广告网站的交互，自动订阅付费服务。该木马是一个恶意模块，它内置于普通应用程序中，例如字典，在线地图，音频播放器，条形码扫描仪和其他软件。

Clicker木马报告：[“A.I.type”虚拟键盘”的风险提示](https://www.anquanke.com/post/id/193421)。

最近暗影实验室在GooglePlay上发现了一个新的Clicker恶意软件家族Haken木马。该应用是一款提供位置方向服务的应用。与利用不可见Web视图的创建和加载来执行恶意点击功能的Clicker木马和Joker木马不同,Haken木马通过将本机代码注入Facebook和Google广告SDK的库中来实现模拟用户点击广告功能。通过点击广告来提高网站访问量赚取钱财。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0187098d85a7085bfa.png)

图1-1GooglePlay上应用信息

用户抱怨该应用会弹广告，建议谨慎下载。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ea1acf88b73c5458.png)

图1-2用户对该应用的评论



## 技术分析：

该程序的第一个入口是BaseReceiver广播接收器。其中注册了许多action，使该广播很容易被触发。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_500_/t0198352681cb45f320.png)

图2-1注册BaseReceiver广播

在该接收器内加载了lib库文件。通过在native层的startTicks函数调用本地com/ google / android / gms / internal / JHandler ”类中的“ clm”方式。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0128e4187c5003d771.png)

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013dce71db94996df3.png)

图2-2加载库文件反射调用本地方法

此方法中注册了两个工作线程和一个计时器。其中wdt线程与C＆C服务器通信获取最新配置信息。而w线程由定时器触发用于检查配置信息并将代码注入到广告SDK（如Google的AdMob和Facebook）的与广告相关的Activity类中。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_435_/t017c9f11ac270e3454.png)

图2-3注册两个工作线程

**工作线程一：**

在wdt线程中与服务器交互获取最新配置信息。服务器地址被编码：[http://13.***.34.16](http://13.250.34.16)。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_558_/t0120ffe512a45b67a4.png)

图2-4服务器交互

服务器下发的配置信息，其中包括用于更新服务器交互的地址。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01aa4b7032a6a11e9f.png)

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017bcd4e1f657d99ae.png)

图2-5从服务器获取配置信息

**工作线程二：**

w线程在设备已联网且应用已定时启动60000ms的情况下，启动活动。通过生成在1-4间的随机数匹配到启动哪个活动，这四个活动用于将代码注入到Facebook和Google广告类中，实现加载广告并模拟点击广告。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c206b19327435fb7.png)

图2-6注入Facebook和Google



[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_661_/t012efbc5bdf0ca1091.png)

图2-7加载广告

模拟用户点击，点击从广告SDK中接收到的广告，这些功能都是通过反射机制实现的。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ccd5585e61f688d9.png)

图2-8点击从广告SDK中接收到的广告

**服务器后台：**

我们通过于应用与服务器交互的地址进入到该应用的服务器后台，发现该应用的开发者使用XAMPP平台搭建了个人网站和服务器。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_530_/t019ec68849ee425c49.png)

图2-9Haken木马个人网站

服务器后台包含2个js文件。Js文件用于代码的注入实现模拟点击功能。

[![](./img/200955/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0110c1f4110b989d2d.png)

图2-10Haken木马服务器后台



## 样本信息：
<td class="ql-align-justify">**应用名**</td>|<td class="ql-align-justify">**包名**</td>|<td class="ql-align-justify">**Sha256**</td>|
<td class="ql-align-justify">Compass</td>|<td class="ql-align-justify">com.haken.compass</td>|<td class="ql-align-justify">30bf493c79824a255f9b56db74a04e711a59257802f215187faffae9c6c2f8dc</td>|
<td class="ql-align-justify">Qrcode</td>|<td class="ql-align-justify">com.haken.qrcode</td>|<td class="ql-align-justify">62d192ff53a851855ac349ee9e6b71c1dee8fb6ed00502ff3bf00b3d367f9f38</td>|
<td class="ql-align-justify">Coloring Book</td>|<td class="ql-align-justify">com.faber.kids.coloring</td>|<td class="ql-align-justify">381620b5fc7c3a2d73e0135c6b4ebd91e117882f804a4794f3a583b3b0c19bc5</td>|
<td class="ql-align-justify">Fruits Coloring Book</td>|<td class="ql-align-justify">com.vimotech.fruits.coloring.book</td>|<td class="ql-align-justify">f4da643b2b9a310fdc1cc7a3cbaee83e106a0d654119fddc608a4b587c5552a3</td>|
<td class="ql-align-justify">Soccer Coloring Book</td>|<td class="ql-align-justify">com.vimotech.soccer.coloring.book</td>|<td class="ql-align-justify">a4295a2120fc6b75b6a86a55e8c6b380f0dfede3b9824fe5323e139d3bee6f5c</td>|
<td class="ql-align-justify">Fruit Helix Jump</td>|<td class="ql-align-justify">mobi.game.fruit.jump.tower</td>|<td class="ql-align-justify">e811f04491b9a7859602f8fad9165d1df7127696cc03418ffb5c8ca0914c64da</td>|
<td class="ql-align-justify">Number Shooter</td>|<td class="ql-align-justify">mobi.game.ball.number.shooter</td>|<td class="ql-align-justify">d3f13dd1d35c604f26fecf7cb8b871a28aa8dab343c2488d748a35b0fa28349a</td>|



## 情报扩展：

“Joker”恶意软件家族最早于2019年9月在GooglePlay上被发现，暗影实验室在2019年9月28号通过[反间谍之旅—模拟订阅高级服务](https://www.anquanke.com/post/id/187621)一文向用户发出风险预示。该恶意软件被用来向用户订阅高级服务，无声地模拟与广告网站的自动交互包括模拟点击和输入高级服务订阅的授权代码。在过去几个月中Joker不断出现在GooglePlay商店中。

我们最近在GooglePlay上发现了另外四个Joker样本，已下载130,000+次。以下为样本信息。
<td class="ql-align-justify">**应用名**</td>|<td class="ql-align-justify">**Sha256**</td>|
<td class="ql-align-justify">com.app.reyflow.phote</td>|<td class="ql-align-justify">08f53bbb959132d4769c4cb7ea6023bae557dd841786643ae3d297e280c2ae08</td>|
<td class="ql-align-justify">com.race.mely.wpaper</td>|<td class="ql-align-justify">44102fc646501f1785dcadd591092a81365b86de5c83949c75c380ab8111e4e8</td>|
<td class="ql-align-justify">com.landscape.camera.plus</td>|<td class="ql-align-justify">9c713db272ee6cc507863ed73d8017d07bea5f1414d231cf0c9788e6ca4ff769</td>|
<td class="ql-align-justify">com.vailsmsplus</td>|<td class="ql-align-justify">1194433043679ef2f324592220dcd6a146b28689c15582f2d3f5f38ce950d2a8</td>|


