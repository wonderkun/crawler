> 原文链接: https://www.anquanke.com//post/id/95244 


# 安卓间谍软件Skygofree：跟随HackingTeam的脚步


                                阅读量   
                                **172578**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者Nikita Buchka, Alexey Firsh，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/skygofree-following-in-the-footsteps-of-hackingteam/83603/](https://securelist.com/skygofree-following-in-the-footsteps-of-hackingteam/83603/)

译文仅供参考，具体内容表达以及含义原文为准

## 背景

在2017年10月初，卡巴斯基研究人员发现了一些新的Android间谍软件，其中包含以前未曾见过的功能。在进一步的研究过程中，他们发现了一些相关的样本指向了一个长期的进化过程。这个恶意软件的最初版本至少是在2014年底创建的。从那时起，植入物（间谍软件）的功能已经得到改善，并且实现了显著的新功能，例如，**当被感染的设备到达指定的位置时麦克风就会进行自动录音；通过无障碍服务窃取WhatsApp消息；以及具备将受感染设备连接到由网络犯罪分子控制的Wi-Fi网络的能力**。（这些新功能是大部分的间谍软件所没有的）

他们观测到许多模仿移动运营商登陆页面的网站，这些网页主要用于传播Android植入物。攻击者自2015年就已经注册了这些域名。根据遥测数据，这是传播最为活跃的一年。传播活动仍然在继续：最近观察到的域名于2017年10月31日登记。根据我们的KSN统计数据，受感染的用户主要位于意大利境内。

此外，当我们深入研究调查时，我们发现了几种Windows间谍软件工具，它们构成了一个用于在目标机器上扫描敏感数据的植入物。我们发现的版本是在2017年初建立的，目前我们还不确定这种植入物是否已经在野外使用。

将此恶意软件命名为Skygofree，是因为我们在其中一个域名中找到了这个词。

## 恶意软件新特征

这部分分别介绍了Android系统和Windows系统下此类家族的间谍软件新特征。

### 1、Android系统

根据观察到的样本及其签名，推断该Android恶意软件的早期版本是在2014年底开发的，并且该活动一直保持活跃。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0169e83b3f1ffd6fbd.png)

最早版本的签名

恶意软件代码和功能已经改变了很多次，从简单的未混淆的恶意软件到复杂的多阶段间谍软件，攻击者可以完全远程控制被感染设备。该类间谍软件可以获取设备的通话记录，文本消息，地理定位，周围音频，日历事件和设备上的其他存储数据（如社交软件WhatsApp，Facebook等信息）。

当恶意软件启动后，它会显示一个假的欢迎通知，同时，它会隐藏桌面图标并启动后台服务，以达到持久隐蔽运行的目的（恶意软件常用手法）。

[![](https://p3.ssl.qhimg.com/t019c0943624e5f041e.png)](https://p3.ssl.qhimg.com/t019c0943624e5f041e.png)

欢迎通知

下表是各个服务对应的主要功能：
<td width="284">服务名称</td><td width="284">功能</td>
<td width="284">AndroidAlarmManager</td><td width="284">上传最近的录音音频(.amr格式)</td>
<td width="284">AndroidSystemService</td><td width="284">录音</td>
<td width="284">AndroidSystemQueues</td><td width="284">运动检测的位置跟踪</td>
<td width="284">ClearSystems</td><td width="284">GSM跟踪（CID，LAC，PSC）</td>
<td width="284">ClipService</td><td width="284">窃取剪贴板内容</td>
<td width="284">AndroidFileManager</td><td width="284">上传所有已获取的数据</td>
<td width="284">AndroidPush</td><td width="284">XMPPС&amp;C协议（url.plus:5223）</td>
<td width="284">RegistrationService</td><td width="284">通过HTTP在C&amp;C进行注册（url.plus/app/pro/）</td>

几乎所有的服务都实现了自我保护功能。由于在Android 8.0（SDK API 26）系统能够杀死空闲的服务，这段代码生成了一个假的更新通知，以防被杀死：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011bfa4aedc41c4fe1.png)

假的更新通知

远控方式更加多样化：**攻击者具备通过HTTP，XMPP（基于XML的协议），二进制SMS和FirebaseCloudMessaging（流行的推送服务）（或旧版本的GoogleCloudMessaging）协议来远程控制受控端的能力**。这种协议的多样性给攻击者更加灵活的控制。在最新的版本中有48个不同的命令。下面是一些最值得注意的命令：
- Geofence：这个命令将一个指定的位置添加到间谍软件的内部数据库，当它匹配设备的当前位置时，恶意软件会触发并开始记录周围的音频。
- Social：启动“AndroidMDMSupport”服务的命令 – 这允许抓取任何其他安装的应用程序的文件。服务名称清楚地表明，攻击者通过应用程序将MDM解决方案作为业务特定工具。控制者可以使用任何目标应用程序的数据库和服务器端PHP脚本名称来指定路径上传。
[![](https://p1.ssl.qhimg.com/t013b64fe93d60290d3.png)](https://p1.ssl.qhimg.com/t013b64fe93d60290d3.png)

**由****MDM-grabbing** **命令定位的几个硬编码应用程序**
- Wifi：通过命令创建一个具有指定配置的新Wi-Fi连接，如果Wi-Fi被禁用，则启用Wi-Fi连接。所以，当设备连接到已建立的网络时，这个过程将是静默和自动的。该命令用于将受害者连接到由网络犯罪分子控制的Wi-Fi网络，以执行流量嗅探和中间人（MitM）攻击。
[![](https://p0.ssl.qhimg.com/t019a8a421aee38157e.png)](https://p0.ssl.qhimg.com/t019a8a421aee38157e.png)

**addWifiConfig****方法代码片段**
- Camera：此命令用于在下次解锁设备时使用前置摄像头记录视频/捕获照片。
Skygofree的某些版本具有专门针对华为设备的自我保护能力。这个品牌的智能手机中有一个“受保护的应用程序”列表，与节省电池的概念相关。未选择作为受保护应用程序的应用程序将在屏幕关闭并等待重新激活时停止工作。因此，为了确保其能够在华为设备上运行，恶意程序将其自身添加到此列表中。显然开发者特别关注华为设备上植入的工作。

此外，我们还发现了一个调试版本的样本（70a937b2504b3ad6c623581424c7e53d），其中包含特别的常量，包括间谍软件的版本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0136b9c928994b15a0.png)

调试版本的版本号

在对所有发现的Skygofree版本进行了深入的分析之后，我们对恶意软件的进化做了大致的时间表。

第一阶段：该阶段是进化的初始阶段，开始于2014年，此阶段初期的恶意软件并没有使用root，窃取社交软件数据库等功能。后期增加了使用root权限的功能。

第二阶段：该阶段为进化中期，原始的包中会有利用漏洞进行提权的功能，并且会下载释放恶意子包。子包类型有elf和apk两种。

第三阶段：此阶段为最新阶段，它能通过第二阶段释放的apk子包继续释放第三层恶意子包。

[![](https://p2.ssl.qhimg.com/t01e66c3191f83b7530.png)](https://p2.ssl.qhimg.com/t01e66c3191f83b7530.png)

恶意软件进化表

但是，有些事实表明，第二阶段的APK样本也可以作为感染的第一步单独使用。以下是Skygofree在第二和第三阶段使用的有效载荷列表。
- 反向的有效载荷
反向shell模块是由攻击者编译的在Android上运行的外部ELF文件。软件的版本决定了特定有效载荷的选择，并且可以在植入开始后或者在特定命令之后立即从命令和控制（C&amp;C）服务器下载。在最近的情况下，有效载荷压缩文件的选择取决于设备处理器架构。目前我们只发现了一个适用于ARM处理器（arm64-v8a, armeabi, armeabi-v7a）的载荷版本。

在几乎所有情况下，zip压缩文件中的这个有效载荷文件都被命名为“setting”或“setting.o”。

该模块的主要目的是通过连接C&amp;C服务器的套接字来提供设备上的反向shell功能。

[![](https://p0.ssl.qhimg.com/t01ac6cebcf8bd77b8a.png)](https://p0.ssl.qhimg.com/t01ac6cebcf8bd77b8a.png)

反向的有效载荷

有效载荷由主模块启动，指定的主机和端口作为一个参数，在某些版本中硬编码为’54 .67.109.199’和’30010’：

[![](https://p3.ssl.qhimg.com/t01649c0e68b9096dce.png)](https://p3.ssl.qhimg.com/t01649c0e68b9096dce.png)

有的直接硬编码到了有效载荷代码中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c37da15a6094526a.png)

我们还观察到在主APK的/ lib /路径中直接安装了类似反向shell有效载荷的变体。

[![](https://p3.ssl.qhimg.com/t01ade9f443c155e339.png)](https://p3.ssl.qhimg.com/t01ade9f443c155e339.png)

配备特定字符串的反向shell载荷

经过深入的研究，我们发现反向shell有效载荷代码的一些版本与PRISM有相似之处（Github上的反向shell后门程序[https://github.com/andreafabrizi/prism/](https://github.com/andreafabrizi/prism/)）。

[![](https://p5.ssl.qhimg.com/t01d681038453b6719d.png)](https://p5.ssl.qhimg.com/t01d681038453b6719d.png)

update_dev.zip里面的反向有效载荷
- 漏洞利用的有效载荷
我们发现了一个重要的有效载荷二进制文件，它试图利用几个已知的漏洞和升级权限。根据几个时间戳，这个有效载荷被自2016年以来创建的版本使用。它也可以通过特定命令下载。攻击负载包含以下文件组件：
<td width="329">组件名称</td><td width="274">描述</td>
<td width="329">run_root_shell/arrs_put_user.o/arrs_put_user/poc</td><td width="274">漏洞利用ELF</td>
<td width="329">db</td><td width="274">Sqlite3工具ELF</td>
<td width="329">device.db</td><td width="274">提权所依据的Sqlite3数据库与支持设备及其常量</td>

‘device.db’是exploit使用的数据库。它包含两个表’supported_devices’和’device_address’。第一个表包含205个设备以及部分Linux属性的信息;；第二个包含与成功利用所需的特定内存地址相关联的地址。如果受感染设备未在此数据库中列出，则漏洞利用程序尝试发现这些地址。

[![](https://p2.ssl.qhimg.com/t0112f64ab5184a4563.png)](https://p2.ssl.qhimg.com/t0112f64ab5184a4563.png)

**目标设备和特殊内存地址的截图**

下载和解包后，主模块执行漏洞利用二进制文件。一旦执行，模块将尝试通过利用以下漏洞获得设备的root权限：

CVE-2013-2094<br>
CVE-2013-2595<br>
CVE-2013-6282<br>
CVE-2014-3153(TowelRoot [https://threatpost.com/android-root-access-vulnerability-affecting-most-devices/106683/](https://threatpost.com/android-root-access-vulnerability-affecting-most-devices/106683/))<br>
CVE-2015-3636

[![](https://p2.ssl.qhimg.com/t01e253eaf33b65d1a5.png)](https://p2.ssl.qhimg.com/t01e253eaf33b65d1a5.png)

漏洞利用过程

经过深入的研究，我们发现攻击负载代码与公共项目android-rooting-tools（[https://github.com/android-rooting-tools](https://github.com/android-rooting-tools)）有许多相似之处。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01876774f550389ae6.png)

反编译的漏洞利用代码

[![](https://p0.ssl.qhimg.com/t011f2db153a94686dd.png)](https://p0.ssl.qhimg.com/t011f2db153a94686dd.png)

android-rooting-tools项目中的run_with_mmap函数

比较两个方法可以看出攻击者所开发的漏洞利用模块是基于android-rooting-tools开源项目的。
- Busybox有效载荷
Busybox是公共软件，在单个ELF文件中提供多个Linux工具。在早期版本中，它使用如下的shell命令进行操作：

[![](https://p1.ssl.qhimg.com/t011ad1daeb37424e85.png)](https://p1.ssl.qhimg.com/t011ad1daeb37424e85.png)

用Busybox窃取WhatsApp加密密钥
- 社工载荷
实际上，这不是一个独立的有效载荷文件。在所有观察到的版本中，它的代码是在一个文件（’poc_perm’，’arrs_put_user’，’arrs_put_user.o’）中利用有效载荷进行编译的。这是由于在执行社交载荷操作之前，恶意软件需要提升权限。该有效载荷也被早期版本使用。它具有与当前版本中的“AndroidMDMSupport”命令类似的功能（窃取属于其他已安装应用程序的数据）。有效载荷将执行shell代码来窃取来自各种应用程序的数据。下面的例子窃取Facebook数据：

[![](https://p4.ssl.qhimg.com/t01b149f8653783ecf3.png)](https://p4.ssl.qhimg.com/t01b149f8653783ecf3.png)

载荷针对的其他应用信息如下：
<td width="284">包名</td><td width="284">应用名</td>
<td width="284">jp.naver.line.android</td><td width="284">LINE: Free Calls &amp; Messages</td>
<td width="284">com.facebook.orca</td><td width="284">Facebook messenger</td>
<td width="284">com.facebook.katana</td><td width="284">Facebook</td>
<td width="284">com.whatsapp</td><td width="284">WhatsApp</td>
<td width="284">com.viber.voip</td><td width="284">Viber</td>
- Parser载荷
在接收到特定的命令后，恶意软件可以下载特殊的有效载荷以从外部应用获取敏感信息。我们观察到的情况涉及WhatsApp。

在审查的版本中，它是从以下地址下载的：**hxxp://url[.]plus/Updates/tt/parser.apk**

负载可以是一个.dex或.apk文件，这是一个Java编译的Android可执行文件。下载之后，它将通过DexClassLoader api由主模块加载：

[![](https://p2.ssl.qhimg.com/t01d964f161579595ce.png)](https://p2.ssl.qhimg.com/t01d964f161579595ce.png)

我们观察到专门针对WhatsApp Messenger的有效载荷。有效载荷使用Android Accessibility Service从屏幕上显示的元素直接获取信息，因此它等待目标应用程序启动，然后解析所有节点以查找文本消息：

[![](https://p3.ssl.qhimg.com/t0159381779b6829b9d.png)](https://p3.ssl.qhimg.com/t0159381779b6829b9d.png)

##### 2、Windows系统

我们发现多个组件构成Windows平台的整个间谍软件系统。
<td width="122">名称</td><td width="264">Md5</td><td width="155">作用</td>
<td width="122">msconf.exe</td><td width="264">55fb01048b6287eadcbd9a0f86d21adf</td><td width="155">主要模块，反向外壳</td>
<td width="122">network.exe</td><td width="264">f673bb1d519138ced7659484c0b66c5b</td><td width="155">发送获取数据</td>
<td width="122">system.exe</td><td width="264">d3baa45ed342fbc5a56d974d36d5f73f</td><td width="155">麦克风录音</td>
<td width="122">update.exe</td><td width="264">395f9f87df728134b5e3c1ca4d48e9fa</td><td width="155">键盘记录</td>
<td width="122">wow.exe</td><td width="264">16311b16fd48c1c87c6476a455093e7a</td><td width="155">截屏</td>
<td width="122">skype_sync2.exe</td><td width="264">6bcc3559d7405f25ea403317353d905f</td><td width="155">Skype通话录音到MP3</td>

所有的模块，除了skype_sync2.exe，都是用Python编写的，并通过Py2exe工具打包成二进制文件。这种转换允许Python代码在Windows环境下运行，无需预先安装Python二进制文件。

msconf.exe是提供恶意软件和反向壳体功能控制的主要模块。它会在受害者的机器上打开一个套接字，并与位于”54.67.109.199:6500”的服务器端组件连接。在与套接字连接之前，它会在“APPDATA / myupd”中创建一个恶意软件环境，并在那里创建一个sqlite3数据库(myupd_tmp\\mng.db)。

[![](https://p2.ssl.qhimg.com/t018d1858b01bb464cf.png)](https://p2.ssl.qhimg.com/t018d1858b01bb464cf.png)

最后，恶意软件会修改“Software \ Microsoft \ Windows \ CurrentVersion \ Run”注册表项创建一个开机启动项。

代码中存在部分意大利语的注释，如下图所示。

[![](https://p2.ssl.qhimg.com/t0115a18a8ca21bd24b.png)](https://p2.ssl.qhimg.com/t0115a18a8ca21bd24b.png)

****释义：********“Receive commands from the remote server, here you can set the key commands to command the virus”****

以下是可用的控制命令：

[![](https://p3.ssl.qhimg.com/t0165ea4fab0bf46d4e.png)](https://p3.ssl.qhimg.com/t0165ea4fab0bf46d4e.png)

所有模块都将其文件设置为隐藏属性：

[![](https://p1.ssl.qhimg.com/t0186072e53ea38ac5c.png)](https://p1.ssl.qhimg.com/t0186072e53ea38ac5c.png)

而且，我们发现了一个用.Net写的模块（skype_sync2.exe）。这个模块的主要目的是获取Skype通话记录。启动后，它直接从C&amp;C服务器下载用于MP3编码的编解码器：[http://54.67.109.199/skype_resource/libmp3lame.dll](http://54.67.109.199/skype_resource/libmp3lame.dll)

skype_sync2.exe模块编译时间戳为2018年2月6日，PDB信息如下：

** [![](https://p4.ssl.qhimg.com/t01034d2c384c972c4d.png)](https://p4.ssl.qhimg.com/t01034d2c384c972c4d.png)**

network.exe是一个提交所有获取数据到服务器的模块。在样本的观察版本中，它没有与skype_sync2.exe模块一起使用的接口。

[![](https://p0.ssl.qhimg.com/t011a0e5e9ad2936a18.png)](https://p0.ssl.qhimg.com/t011a0e5e9ad2936a18.png)

network.exe 向服务器提交数据

3、代码相似性

Windows下间谍软件的一些代码和某些开源项目的代码有很多相似之处。（[https://github.com/El3ct71k/Keylogger/](https://github.com/El3ct71k/Keylogger/)）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c3ee29a161ccb5a1.png)

**Update.exe****和****’El3ct71k’****的键盘记录器的代码对比**

Xenotix Python键盘记录包括指定的“mutex_var_xboz”

[![](https://p3.ssl.qhimg.com/t01edf4876324d78653.png)](https://p3.ssl.qhimg.com/t01edf4876324d78653.png)

**update.exe****模块和****Xenotix Python Keylogger****代码比较**

[![](https://p0.ssl.qhimg.com/t01300a45d2ab2c9cc2.png)](https://p0.ssl.qhimg.com/t01300a45d2ab2c9cc2.png)

**msconf.exe****模块的****‘addStartup’****方法**

[![](https://p1.ssl.qhimg.com/t0102c4702cfb74dc7f.png)](https://p1.ssl.qhimg.com/t0102c4702cfb74dc7f.png)

**Xenotix Python Keylogger****的****‘addStartup’****方法**

## 传播

下面是传播软件的登录页：

[![](https://p0.ssl.qhimg.com/t01655f84812ef5f8ce.png)](https://p0.ssl.qhimg.com/t01655f84812ef5f8ce.png)

这些域中有许多是过时的，但是几乎所有（除了一个appPro_AC.apk）样本都位于217.194.13.133服务器上。

所有观察到的登陆页面都通过他们的域名和网页内容来模拟移动运营商的网页。

[![](https://p4.ssl.qhimg.com/t01eccd117f1fa05b9b.png)](https://p4.ssl.qhimg.com/t01eccd117f1fa05b9b.png)

模仿登录页

[![](https://p2.ssl.qhimg.com/t01402bc3d75326f15f.png)](https://p2.ssl.qhimg.com/t01402bc3d75326f15f.png)

[![](https://p5.ssl.qhimg.com/t015e93fedf08dfd73f.png)](https://p5.ssl.qhimg.com/t015e93fedf08dfd73f.png)

现在不能确定这些登陆页面在什么环境下被广泛使用，但是根据数据中的所有信息，可以认为它们是利用恶意重定向或者“在线”中间人攻击。例如，这可能是受害者的设备连接到受到攻击者感染或控制的Wi-Fi接入点。

## 痕迹

在研究过程中，我们发现了很多开发者和维护者的痕迹。

[![](https://p5.ssl.qhimg.com/t0108fe08307e2ef271.png)](https://p5.ssl.qhimg.com/t0108fe08307e2ef271.png)

特别的证书信息

Whois记录和IP关系也提供了许多有趣的信息。Whois记录中还有很多涉及“Negg”。

[![](https://p0.ssl.qhimg.com/t0144ac8553bf58494e.png)](https://p0.ssl.qhimg.com/t0144ac8553bf58494e.png)

## 结论

Skygofree Android间谍软件是最强大的间谍软件工具之一。在其长期发展的过程中，有多种特殊功能：使用多种漏洞获取root权限，复杂的有效负载结构，以前从未见过的监视功能，如在特定位置录制周围的音频。

通过在恶意软件代码中发现的许多痕迹，我们坚信，Skygofree的开发商是一家意大利IT公司，就像HackingTeam一样致力于监控解决方案。

IOC：[skygofree木马IOC.pdf](https://cdn.securelist.com/files/2018/01/Skygofree_appendix_eng.pdf)
