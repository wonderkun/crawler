> 原文链接: https://www.anquanke.com//post/id/213528 


# APT-SpyMax间谍软件家族追踪


                                阅读量   
                                **111809**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01b6dfc65384f1f538.jpg)](https://p0.ssl.qhimg.com/t01b6dfc65384f1f538.jpg)



**概述：**坦桑尼亚大陆超级联赛足球赛季在即，该足球赛是非洲坦桑尼亚的顶级职业足球联赛。最近安全人员发现威胁行为者将攻击目标对准了正在进行的坦桑尼亚大陆超级联赛足球赛。他们分发了两个最著名足球俱乐部的Android应用安装包，分别是SimbaSC和Yanga（YoungAfricans）SC。经分析发现该两款恶意软件是通过SpyMax间谍软件框架打包的恶意程序。主要通过利用SimbaSC和Yanga（YoungAfricans）SC合法应用的图标吸引用户安装使用。且SpyMax间谍软件上半年行动活跃，疫情期间利用“新冠肺炎”热点锁定移动用户。SpyMax间谍软件框架打包的恶意软件具有强大的隐匿功能，其主要通过动态从服务器获取加载恶意代码来执行其恶意行为，一般病毒引擎无法检测到。



## 1. 程序运行流程图

恶意程序运行主要分为两个个阶段，首先间谍软件为了掩饰自己的恶意行为安装启动后便隐藏自身图标然后从资源文件中获取安装另一款安全的应用。接着恶意程序连接服务器，根据服务器下发的命令从服务器下载不同的恶意文件，并加载执行其恶意行为。

[![](https://p3.ssl.qhimg.com/t01e61378f61dcb3e03.png)](https://p3.ssl.qhimg.com/t01e61378f61dcb3e03.png)

图1-1 程序运行流程图



## 2. 技术原理分析

### **2.1 仿冒合法应用图标**

仿冒合法的SimbaSC和Yanga（YoungAfricans）SC应用。

[![](https://p4.ssl.qhimg.com/t015cb461fdbc26553d.png)](https://p4.ssl.qhimg.com/t015cb461fdbc26553d.png)

**图1-2仿冒合法应用图标**

允许将应用程序安装到外部存储空间中去，但是如果没有指定安装位置，则由系统自行决定应用程序安装位置。

[![](https://p0.ssl.qhimg.com/t01254f161ca1acfd9b.png)](https://p0.ssl.qhimg.com/t01254f161ca1acfd9b.png)

**图1-3 设置**安装到外部存储空间

应用安装启动后会隐藏自身图标，并从资源文件中获取安装一款具有实际功能的仿冒应用。这款应用没有恶意行为，主要用于显示广告。这样做的目的是为了防止用户发现其恶意行为。

[![](https://p5.ssl.qhimg.com/t01c532695cdf89d053.png)](https://p5.ssl.qhimg.com/t01c532695cdf89d053.png)

图1-4 获取安全应用写入外部存储路径

获取文件MIME类型（它设定某种扩展名的文件用一种应用程序来打开的方式类型，当该扩展名文件被访问的时候，浏览器会自动使用指定应用程序来打开），安装应用。

[![](https://p4.ssl.qhimg.com/t01a73555ce2252edbc.png)](https://p4.ssl.qhimg.com/t01a73555ce2252edbc.png)

**图1-5 安装安全应用**

该合法应用具有实际业务功能，主要用于显示一些google广告，目的是赚取广告费用。在该应用的掩饰下，用户很难发现间谍软件的恶意行为。

[![](https://p0.ssl.qhimg.com/t01d367e388d1a319d8.png)](https://p0.ssl.qhimg.com/t01d367e388d1a319d8.png)

**图1-6 合法应用界面、显示的广告**

### **2.2 获取敏感权限**

恶意程序将目标SDK设置低于23，不需要用户主动授权，就可获取所有敏感权限。

[![](https://p1.ssl.qhimg.com/t01e3eca0d81940f33a.png)](https://p1.ssl.qhimg.com/t01e3eca0d81940f33a.png)

**图1-7 targetSdk设置为22**

敏感权限列表：

[![](https://p1.ssl.qhimg.com/t0129ec75e0e0a7dd78.png)](https://p1.ssl.qhimg.com/t0129ec75e0e0a7dd78.png)

**图1-8 敏感权限列表**

### **2.3自我防护**

**（1）设置电源锁和wifi锁，保障应用在后台正常运行。**

[![](https://p0.ssl.qhimg.com/t01317cc1e10cecba22.png)](https://p0.ssl.qhimg.com/t01317cc1e10cecba22.png)

**图1-9 设置电源锁和wifi锁**

（2）设置wifi休眠策略，设置WIFI在休眠时不断开：

[![](https://p2.ssl.qhimg.com/t0137dc603b1c01f7a3.png)](https://p2.ssl.qhimg.com/t0137dc603b1c01f7a3.png)

**图1-10 设置wifi休眠策略**

（3）远程控制杀死自身进程：

[![](https://p3.ssl.qhimg.com/t01d38999219800d634.png)](https://p3.ssl.qhimg.com/t01d38999219800d634.png)

**图1-11 杀死自身进程**

### **2.4加载恶意代码**

（1）启动线程连接服务器，与服务器进行socket通信。

服务器地址：40.114.***.110

端口：7774

[![](https://p4.ssl.qhimg.com/t011092e5130ee1cbc2.png)](https://p4.ssl.qhimg.com/t011092e5130ee1cbc2.png)

**图1-12 连接服务器**

（2）获取用户设备、服务器地址、端口等信息压缩并作一定处理后发送至服务器，作为用户的唯一标识。

[![](https://p2.ssl.qhimg.com/t0106d48db7123a796a.png)](https://p2.ssl.qhimg.com/t0106d48db7123a796a.png)

**图1-13 发送用户设备信息至服务器**

[![](https://p1.ssl.qhimg.com/t01051c30d7c6f293c7.png)](https://p1.ssl.qhimg.com/t01051c30d7c6f293c7.png)

[![](https://p2.ssl.qhimg.com/t0180f67465e1e5c2ab.png)](https://p2.ssl.qhimg.com/t0180f67465e1e5c2ab.png)

**图1-14 对发送数据进行压缩处理**

（3）循环从服务器读取数据，并进行解压处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c6eaed4ce972cb7b.png)

**图1-15 从服务器获取数据**

[![](https://p4.ssl.qhimg.com/t012d383ad83725252b.png)](https://p4.ssl.qhimg.com/t012d383ad83725252b.png)

**图1-16 对数据进行解压**

(4)从服务器获取恶意代码写入外部存储目录并加载执行，每次加载完文件便将文件删除。

[![](https://p1.ssl.qhimg.com/t01521a9cd0c377863c.png)](https://p1.ssl.qhimg.com/t01521a9cd0c377863c.png)

**图1-17 从服务器下载恶意代码**

外部存储目录一共包含8个恶意apk文件，每个apk文件包含一个类进行一个功能管理。

[![](https://p1.ssl.qhimg.com/t013eeee2df4b11d9d8.png)](https://p1.ssl.qhimg.com/t013eeee2df4b11d9d8.png)

**图1-18加载的恶意文件**

[![](https://p2.ssl.qhimg.com/t01591e02c5d0492e08.png)](https://p2.ssl.qhimg.com/t01591e02c5d0492e08.png)

**图1-19 恶意文件结构**

加载各个恶意文件中的类：

[![](https://p1.ssl.qhimg.com/t01957e0da53d652525.png)](https://p1.ssl.qhimg.com/t01957e0da53d652525.png)

**图1-20加载类**

（5）反射调用恶意文件中的方法，执行恶意行为。

[![](https://p2.ssl.qhimg.com/t0154daafb4a053be49.png)](https://p2.ssl.qhimg.com/t0154daafb4a053be49.png)

**图1-21 反射调用方法**

服务器发送至客户端的命令包含需要加载的恶意文件内容、类名、方法名以及参数信息。当攻击者在服务器控制面板点击查看用户不同的信息时，服务器就会发送不同指令。

[![](https://p5.ssl.qhimg.com/t01979fabd583297fd4.png)](https://p5.ssl.qhimg.com/t01979fabd583297fd4.png)

**图1-22调用的方法名都为“method”**

### **2.5 程序恶意行为**

**应用程序具有以下恶意行为：**
1. 短信息管理
1. 联系人信息管理
1. 通话记录管理
1. 用户账户信息管理
1. 应用管理
1. 录制音频
1. 相机管理
1. 文件管理
1. 拨打电话、发送短信
1. **访问实时位置**
1. 执行shell命令
1. **键盘记录、剪切板记录**
（1）键盘记录需通过开启可服务性服务监控用户行为，应用主要监控用户的点击、长按、文本框聚焦、文本改变等行为。

[![](https://p0.ssl.qhimg.com/t01fe24dcc986da234d.png)](https://p0.ssl.qhimg.com/t01fe24dcc986da234d.png)

**图2-1 监控用户行为**

（2）获取用户通话记录信息:

[![](https://p0.ssl.qhimg.com/t017ef3f23823408c43.png)](https://p0.ssl.qhimg.com/t017ef3f23823408c43.png)

**图2-2 获取用户通话记录**

（3）获取用户设备联系人信息：

[![](https://p5.ssl.qhimg.com/t01c097efda809bec2c.png)](https://p5.ssl.qhimg.com/t01c097efda809bec2c.png)

**图2-3获取用户联系人信息**

（4）获取用户短信息：

[![](https://p2.ssl.qhimg.com/t012b9e7a0e8dbe2f92.png)](https://p2.ssl.qhimg.com/t012b9e7a0e8dbe2f92.png)

**图2-4 获取用户短信息**



## 3. SpyMax间谍软件框架

### **3.1 文件结构**

（1）Spymax间谍软件制作的应用文件结构中只有一个包，包内包含多个名称相似的类，类都经过了混淆。

[![](https://p1.ssl.qhimg.com/t01bf09217bc0bed37c.png)](https://p1.ssl.qhimg.com/t01bf09217bc0bed37c.png)

**图3-1 间谍软件类结构**

（2）资源文件的raw目录下包含一个apk文件，values目录下主要包含三项配置文件。配置文件中包含绑定的IP和端口信息。

[![](https://p5.ssl.qhimg.com/t01fb2b423317ee38a6.png)](https://p5.ssl.qhimg.com/t01fb2b423317ee38a6.png)

图3-2 间谍软件文件结构

### **3.2 框架介绍**

（1）国外网站对Spymax间谍软件框架进行推广。

[![](https://p0.ssl.qhimg.com/t01ad9cbd674c1e0555.png)](https://p0.ssl.qhimg.com/t01ad9cbd674c1e0555.png)

**图3-3 Spymax间谍软件框架网站推广tu**

（2）通过SpyMax间谍软件框架我们可以很轻松的打包一个间谍软件。可设置服务器IP、端口、恶意软件图标以及绑定一个安全的应用。

Spymax间谍软件信息管理窗口：

[![](https://p2.ssl.qhimg.com/t0141ebf1ad96db836f.png)](https://p2.ssl.qhimg.com/t0141ebf1ad96db836f.png)

**图3-4 Spymax间谍软件信息管理窗口**

（2）显示获取的用户信息：

[![](https://p1.ssl.qhimg.com/t018ffaeea20b2cf1f2.png)](https://p1.ssl.qhimg.com/t018ffaeea20b2cf1f2.png)

**图3-5 用户隐私数据显示窗口**



## 4. 样本信息
<td class="ql-align-justify" data-row="1">**Hash**</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">**包名**</td><td data-row="1"></td>
<td class="ql-align-justify" data-row="2">aa67921f19809edc87f1f79237e123e9c5c67019</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">yanga.com</td><td data-row="2"></td>
<td class="ql-align-justify" data-row="3">2ed2d804754d83aa5de32c27b4ca767d959bf3e8</td><td data-row="3"></td><td class="ql-align-justify" data-row="3">yonglowfans.yanga</td><td data-row="3"></td>
<td class="ql-align-justify" data-row="4">bea206cf83eea30bf5d0734d94764796d956c4f5</td><td data-row="4"></td><td class="ql-align-justify" data-row="4">com.livestream.livestream</td><td data-row="4"></td>
<td class="ql-align-justify" data-row="5">1cc01da09849e17f83940d9250318d248f7ab77d</td><td data-row="5"></td><td class="ql-align-justify" data-row="5">com.simba.simba</td><td data-row="5"></td>
<td class="ql-align-justify" data-row="6">4c7a41d7b0a225f0fa61fe7dc18695e03c2690c8</td><td data-row="6"></td><td class="ql-align-justify" data-row="6">yonglowfans.yanga</td><td data-row="6"></td>
<td class="ql-align-justify" data-row="7">aa67921f19809edc87f1f79237e123e9c5c67019</td><td data-row="7"></td><td class="ql-align-justify" data-row="7">yanga.com</td><td data-row="7"></td>



## 5. 安全建议
1. 让你的设备保持最新，最好将它们设置为自动补丁和更新，这样即使你不是最熟悉安全的用户，你也能得到保护。
1. 坚持去正规应用商店下载软件，避免从论坛等下载软件，可以有效的减少该类病毒的侵害。关注”暗影实验室”公众号，获取最新实时移动安全状态，避免给您造成损失和危害。
1. 安装好杀毒软件，能有效的识别已知的病毒。