> 原文链接: https://www.anquanke.com//post/id/224775 


# WAPDropper恶意软件-悄悄为你订阅高级服务


                                阅读量   
                                **92998**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01aaebd5cbe0b0577a.jpg)](https://p5.ssl.qhimg.com/t01aaebd5cbe0b0577a.jpg)



## 概述：

CheckPoint研究人员最近发现了一种新型恶意软件并将它命名为WAPDropper。该恶意软件包含两个不同的模块：恶意程序下载模块和高级拨号程序模块。恶意程序下载模块用于下载第二阶段恶意代码并执行其恶意功能，高级拨号程序模块用于在受害者不知情或未同意的情况下订阅由泰国和马来西亚的电信供应商提供的高级服务。

恒安嘉新App全景态势与情报溯源挖掘平台监测到一款名为“Email”，仿冒邮件标识的安装图标，安全研究人员发现该应用具有WAPDropper特征，在用户设备感染该恶意软件后，会执行隐藏图标，延迟执行，进程永久运行，强加密混淆，环境检测等一系列自身防护操作，一旦进入受害设备，便会连接C2服务器获取恶意代码并加载执行，然后利用反射调用机制执行高级服务订阅模块，打开一个小的Web视图，加载执行恶意JS代码，并使用第三方提供的图像验证代码识别绕过验证步骤，最终实现为用户订阅高级服务的目的，执行流程原理如图1所示，执行过程中，该恶意程序会删除所有HTTP请求中的“ X-Requested-With”标识，禁用对CSRF（跨站请求伪造）攻击的防护。

[![](https://p2.ssl.qhimg.com/t01670285d024914423.png)](https://p2.ssl.qhimg.com/t01670285d024914423.png)

**图1-1 恶意程序执行流程**



## 1. 样本信息
<td class="ql-align-justify" data-row="1">**应用名**</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">Email</td><td data-row="1"></td>
<td class="ql-align-justify" data-row="2">**报名**</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">com.android.ferugre</td><td data-row="2"></td>
<td class="ql-align-justify" data-row="3">MD5</td><td data-row="3"></td><td class="ql-align-justify" data-row="3">cb4e32705a64aca8329cab42e44047f5</td><td data-row="3"></td>
<td class="ql-align-justify" data-row="4">[![](https://p2.ssl.qhimg.com/t012eae93c9a8af76b3.png)](https://p2.ssl.qhimg.com/t012eae93c9a8af76b3.png)</td><td data-row="4"></td>



## 2. 技术分析

### **2.1 自身防护**

**2.1.1 隐藏图标、延迟执行**

（1）恶意软件一开始运行便隐藏其图标，以防止任何用户识别和卸载恶意软件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0150a15836fd1cce14.png)

**图2-1 隐藏图标**

（2）接着设置延迟60s执行其恶意功能：

[![](https://p1.ssl.qhimg.com/t01fe0c5a0f86a81703.png)](https://p1.ssl.qhimg.com/t01fe0c5a0f86a81703.png)

**图2-2 延迟启动服务**

**2.1.2 进程保活**

**（1）由于JobService的任务是由系统来维护的，通过设置每隔5000毫秒、最小延迟5000毫秒执行一次任务，能避免系统杀死后台进程，以达到进程保活的目的。**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019bb106fca3cd8da7.png)

**图2-3 启动JobService**

（2）通过添加Account使用同步机制来提高进程的存活率：

[![](https://p5.ssl.qhimg.com/t01bba29d52c8b039b1.png)](https://p5.ssl.qhimg.com/t01bba29d52c8b039b1.png)

**图2-4 添加Account**

该恶意软件在用户设备中添加账户：

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c2bd109f3299d6ad.png)**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017aaa7d23b12b320d.png)

**图2-5 添加账户**

**2.1.3 混淆加密代码**

** 该恶意软件严重的混淆加密了其字符串，所有字符串以及反射调用类名、函数名、参数都使用了复杂的自定义加密算法。**

**加密的字符串字节数组：**

[![](https://p4.ssl.qhimg.com/t01a4e4b4eaf49d2c19.png)](https://p4.ssl.qhimg.com/t01a4e4b4eaf49d2c19.png)

**图2-6 字符串字节码**

字符串解密函数调用：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015f664d9c12db1cbb.png)

**图2-7 解密函数调用**

**2.1.4 环境检测**

** 检查设备是否配置了代理或VPN，防止用户对应用通信数据进行抓包：**

[![](https://p1.ssl.qhimg.com/t01f49cf83cef1b0da1.png)](https://p1.ssl.qhimg.com/t01f49cf83cef1b0da1.png)

**图2-8 检测代理**

### **2.2 恶意模块**

** 恶意软件在执行完以上操作后便通过调用初始化函数执行恶意程序下载模块和高级服务订阅模块：**

[![](https://p3.ssl.qhimg.com/t01373fb0de2bf0ce87.png)](https://p3.ssl.qhimg.com/t01373fb0de2bf0ce87.png)

**图2-9 开始执行恶意模块**

**2.2.1 恶意程序下载模块**

** 应用程序首先收集有关受害者设备和系统的数据，包括：**

**设备编号**

**MAC地址**

**所有已安装应用程序的列表**

**正在运行的服务列表**

**最高活动包名称**

**屏幕是否打开**

**是否为此应用启用了通知**

**可用的存储空间大小**

[![](https://p2.ssl.qhimg.com/t015587829841721498.png)](https://p2.ssl.qhimg.com/t015587829841721498.png)

**图2-10 获取用户设备信息**

它将收集信息发送至服务器：https：//ks***r7.3q03on.com：12038。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f0c86f681ee34caa.png)

**图2-11与服务器通信**

收到来自C＆C服务器的响应后，WAPDropper解析JSON配置，其中包括有关Dropper模块下载的其他有效负载的说明和规范，包括：

有效负载的下载URL

下载文件的MD5验证

反射调用的类名称和方法名称

执行频率（分钟）

最大执行次数

[![](https://p0.ssl.qhimg.com/t018d59af4e463c1a7e.png)](https://p0.ssl.qhimg.com/t018d59af4e463c1a7e.png)

**图2-12 解析服务器数据**

完成下载每个有效负载后，WAPDropper会将下载的DEX文件解密为.jar文件，并将其本地存储在受感染的设备上。

WAPDropper加载解密的.jar文件，并立即将其从设备中删除，以避免留下痕迹。每个有效负载都具有在JSON配置中配置的执行频率。WAPDropper会针对每个不同的有效负载监视此频率。

[![](https://p4.ssl.qhimg.com/t01c192a06f59276692.png)](https://p4.ssl.qhimg.com/t01c192a06f59276692.png)

[![](https://p2.ssl.qhimg.com/t0131035654e526b8d7.png)](https://p2.ssl.qhimg.com/t0131035654e526b8d7.png)

**图2-13 动态加载dex文件**

**2.2.3 高级服务订阅模块**

** 高级访问订阅模块首先会解密存储在其代码中的文件字节码，并通过一系列反射调用将其写入名为“data.jar”、“libnav-6mdw2z.so”的本地文件中。**

[![](https://p2.ssl.qhimg.com/t0124ccf86110c5d871.png)](https://p2.ssl.qhimg.com/t0124ccf86110c5d871.png)

**图1-14 加密的DEX文件字节数组**

[![](https://p0.ssl.qhimg.com/t014c63eff7b9e0a734.png)](https://p0.ssl.qhimg.com/t014c63eff7b9e0a734.png)

**图1-15 解密写入本地文件**

[![](https://p4.ssl.qhimg.com/t01cb6047be95351d7f.png)](https://p4.ssl.qhimg.com/t01cb6047be95351d7f.png)

**图1-16 解密后存储在本地的文件**

接着WAPDropper反射加载本地data.jar文件，并调用其初始化方法以开始实施订阅高级服务的计划。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01749a4c1ce0d4c8ea.png)

**图1-17 加载高级服务订阅模块**

加载本机库.lib文件。

[![](https://p4.ssl.qhimg.com/t01bce8b4635b2c64ad.png)](https://p4.ssl.qhimg.com/t01bce8b4635b2c64ad.png)

**图1-18 加载本机库**

该库负责从所有HTTP请求中删除所有“X-Requested-With” HTTP标头。

“X-Requested-With”是一个HTTP标头，用于验证CSRF（跨站请求伪造），即是一种挟制用户在当前已登录的Web[应用程序](https://baike.baidu.com/item/%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F/5985445)上执行非本意的操作的攻击方法。WAPDropper将所有出现的“X-Requested-With”字符串替换为“Accept-Encoding”字符串，这导致禁用对CSRF攻击的防护。

[![](https://p0.ssl.qhimg.com/t01b2649645670dfab2.png)](https://p0.ssl.qhimg.com/t01b2649645670dfab2.png)

**图1-19 删除“X-Requested-With” HTTP标头**

WAPDropper接下来将启动一个计时器，该计时器定期将有关受感染设备的基本信息发送到服务器：https：//api .bi***rd.com / un，并从服务器获取广告报价。

[![](https://p1.ssl.qhimg.com/t012f8f23daf6121ed2.png)](https://p1.ssl.qhimg.com/t012f8f23daf6121ed2.png)

**图1-20 获取用户设备信息**

收到广告报价后，该恶意软件会构建一个1×1像素的对话框，该对话框几乎看不见，但实际上包含一个很小的Web视图：

[![](https://p2.ssl.qhimg.com/t01dcbeb7f6c7ebacfb.png)](https://p2.ssl.qhimg.com/t01dcbeb7f6c7ebacfb.png)

**图1-21 构建对话框**

下一步是将恶意JavaScript注入新的易受攻击的Web视图，此JavaScript是一个界面，提供了一个可以执行以下操作的远程网站：

获取受害者的电话号码。

获取短信列表。

发送短信至指定号码。

将POST请求发送到指定的URL。

[![](https://p2.ssl.qhimg.com/t016cf01200ef89bc4b.png)](https://p2.ssl.qhimg.com/t016cf01200ef89bc4b.png)

图1-22 加载JavaScript代码

该恶意软件另一个特殊的功能就是可识别CAPTCHA（验证码）功能以及它如何在Web视图中输入验证码结果。

WAPDropper选择下载图片并将其发送到服务器，或者解析图片的DOM树，提取图片，使用Base64对其进行编码，然后将其发送至服务器：https://upload.cha***ing.net/Upload/Processing.php。该服务器是由国内某公司提供的基于ML的图像验证代码识别和图像分类服务。当恶意软件将验证码图像提交给服务时，平台会在图片中返回识别结果的坐标位置，然后解析坐标模拟登陆。

[![](https://p1.ssl.qhimg.com/t015fd59fd7c6b34263.png)](https://p1.ssl.qhimg.com/t015fd59fd7c6b34263.png)

[![](https://p3.ssl.qhimg.com/t01d3e595ded25e00db.png)](https://p3.ssl.qhimg.com/t01d3e595ded25e00db.png)

图1-23 恶意软件的CAPTCHA识别功能

WAPDropper还具有解析HTML和识别其中的特定元素的功能，因此它可以模仿用户输入的行为：

[![](https://p5.ssl.qhimg.com/t014323563f9d8d5633.png)](https://p5.ssl.qhimg.com/t014323563f9d8d5633.png)

**图1-24 模仿用户输入行为**

通过查看软件包名称和相应的功能，可以很明显地看出该恶意软件是针对电信公司。

[![](https://p0.ssl.qhimg.com/t01764a30b5089b3e0b.png)](https://p0.ssl.qhimg.com/t01764a30b5089b3e0b.png)

[![](https://p0.ssl.qhimg.com/t010e90f7254d535688.png)](https://p0.ssl.qhimg.com/t010e90f7254d535688.png)

**图1-25 针对电信公司证据**

WAPDropper是一种新型的恶意软件病毒，软件开发者对其代码进行了强混淆加密保护，这不仅能够躲避防病毒工具的检测，躲避应用商店的检测，同时大大增加了逆向分析人员的分析难度。恶意程序的整个攻击过程分为两个模块，恶意程序下载模块使恶意软件能够随意从服务器获取更新恶意代码在本地执行。高级服务订阅模块会在用户不知情的情况下订阅高级服务造成用户资费消耗。如果用户设备不小心感染了该病毒，将会对用户的隐私安全以及财产安全造成极大威胁。

### **3. 服务器列表**
<td class="ql-align-justify" data-row="1">**服务器地址**</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">**IP**</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">**地址**</td><td data-row="1"></td>
<td class="ql-align-justify" data-row="2">http://104.250.***.170:6262</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">104.250.***.170</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">北美</td><td data-row="2"></td>
<td class="ql-align-justify" data-row="3">http://test.f***2o.com/</td><td data-row="3"></td><td class="ql-align-justify" data-row="3">104.250.***.114</td><td data-row="3"></td><td class="ql-align-justify" data-row="3">北美</td><td data-row="3"></td>
<td class="ql-align-justify" data-row="4">http://api.bi***rd.com/un</td><td data-row="4"></td><td class="ql-align-justify" data-row="4">104.250.***.35</td><td data-row="4"></td><td class="ql-align-justify" data-row="4">北美</td><td data-row="4"></td>
<td class="ql-align-justify" data-row="5">http://ss1.mo***elife.co.th/confirmOtp</td><td data-row="5"></td><td class="ql-align-justify" data-row="5">202.149.***.122</td><td data-row="5"></td><td class="ql-align-justify" data-row="5">泰国</td><td data-row="5"></td>
<td class="ql-align-justify" data-row="6">https：//ks***r7.3q03on.com</td><td data-row="6"></td><td class="ql-align-justify" data-row="6">161.117.***.93</td><td data-row="6"></td><td class="ql-align-justify" data-row="6">新加坡</td><td data-row="6"></td>



## 4. 扩展信息

恒安嘉新App全景态势与情报溯源挖掘平台监测到此次攻击事件的样本信息,标识为病毒高风险仿冒。



## 4. 安全建议
1. 用户安装所需软件，建议去正规的应用市场下载、去官方下载。
1. 在手机当中安装必要的安全软件，并保持安全软件更新。
1. 关注“暗影安全实验室”微信公众号，我们将持续关注安全事件。