
# 儿童游戏软件中隐藏着Tekya木马风险预警


                                阅读量   
                                **468631**
                            
                        |
                        
                                                                                    



[![](./img/202640/t016f6ebd1115c653d7.jpg)](./img/202640/t016f6ebd1115c653d7.jpg)



**概述：**广告软件通常通过弹出式窗口、横幅广告、内文链接等广告方式来呈献广告内容，主要是为了提高相关网站、产品知名度。这能为软件开发商带来一定的广告收入。而广告木马软件则通常通过单击链接和其他交互式元素来模拟网页上的用户操作，实现无声地模拟与广告网站的交互如点击广告提高网站访问率或自动订阅付费服务，从而增加广告带来的收入。

继2020年2月，[Clicker木马新家族-Haken木马](#rd)通过在GooglePlay分发8种不同的恶意应用来感染用户设备。最近暗影安全实验室在GooglePlay上发现了一个新木马家族—Tekya木马。该木马是一款模拟用户点击来自GoogleAdMob，Facebook等机构的广告进行移动广告欺诈的木马软件。它通过混淆原生代码来躲避Google的检测机制使其能成功的通过GooglePlay平台分发。并利用Android中的“MotionEvent”机制模仿用户的点击行为。



## 1.样本信息

**MD5：**2D3B6BDBBDF0AD12E935B97D565B891A

**包名：**com.pantanal.stickman.warrior

**应用名：**StickmanFighter

**图标：**

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01558e633416015e95.png)



## 2.技术分析

该程序在安装时会在receiver注册多条广播，比如开机自运行，读取网络状态，手机屏幕关闭后台仍然运行，这样使该广播很容易被触发。

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01367c2cf328a6d7bc.png)

**图2-1 注册Receiver广播**

接收到开机以及运行广播后，利用反射机制来调用apk文件中的libego.so文件

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013240453db1c42ce4.png)

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b3af8c596b910c15.png)

图2-2加载libego库文件反射调用本地方法

之后在ego库中创建validators对象列表，可以看到该对象列表中存在了许多混淆的对象

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01334367db188c7336.png)

**图2-3创建validators对象列表**

在这些validators对象中，每个调用的方法会从本地的libego.so中运行对应的函数，函数会调用C函数，运行到Y函数，最后调用xxcrl函数。

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0156e826cd2e973f51.png)

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015518aff5d726ebc3.png)

**图2-4xxcrl函数调用**

我们可以在本地的libego.so中找到对应的函数，该函数大多经过了混淆。

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ca0dd5e66644f38e.png)

**图2-5libego.so对应的函数**

我们在文件中的java_uk_nema_Ego_xxcrl函数中可以看到该函数负责多个动作，其中fflwejp方法负责分析配置文件，getWindow和getDecorView负责获取所需要的handle。

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e1f70322c0935431.png)

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0189661af8ae90e966.png)

**图2-6xxcrl函数中的方法作用**

接下来在子函数sub_AAF0处理对应的touch事件来进行模拟点击。

**[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-04-08/202004081519019278381920_html_m7bc5cbed.png)**

**[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-04-08/202004081519019278381920_html_9148c73.png)**

**图2-7进行模拟点击事件**



## 3.服务器后台

接下来我们对Tekya木马家族进行真机模拟抓包测试，通过实际运行我们可以看到此类软件在后台运行多种广告并进行对应的服务器访问。

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010b9073c8b5728630.png)

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_803_/t0188944ee276824c2e.png)

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016cf6067d7fea5899.png)

[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a0ba8f69d0a81237.png)

**图2-8多次访问广告**



## 4.情报扩展

我们在GooglePlay上共获取到29个该木马家族应用，下载量超过100万次，其中大部分软件是针对儿童的游戏软件，模拟点击的广告也多为游戏类广告。

**部分样本信息：**

**[![](./img/202640/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b43784b57914c45e.png)**



## 5.安全建议
1. 如果用户已经感染此类木马病毒，建议用户及时卸载此类应用。
1. 及时更新系统并下载安全软件，养成良好习惯。
1. 关注暗影实验室的微信公众号，我们会及时发布木马病毒的最新动态。