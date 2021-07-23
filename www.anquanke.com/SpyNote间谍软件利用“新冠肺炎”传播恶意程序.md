> 原文链接: https://www.anquanke.com//post/id/203264 


# SpyNote间谍软件利用“新冠肺炎”传播恶意程序


                                阅读量   
                                **450167**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01830e572ddb0b21ee.png)](https://p2.ssl.qhimg.com/t01830e572ddb0b21ee.png)



PaloaltoNetworks团队最早于2016年发现了一款新的AndroidRAT（远程管理工具）-SpyNote，该间谍软件允许恶意软件所有者获得对Android设备的远程管理控制。

随着COVID-19的传播，人们时刻关注着该病毒的准确信息以及迫切寻求政府提供的有关该病毒物资、工具等方面的帮助。威胁行为者利用围绕该主题的一切可利用信息传播大量恶意程序。

SpyNote间谍木马最早于今年2月份就开始利用“新冠肺炎”传播应用名为“Corona1”的恶意软件。而最近暗影安全实验室再次发现SpyNote在一个仿冒世界卫生组织的网站上分发间谍软件，该网站打着世界卫生组织的名号诱导用户下载自我检测新冠状病毒的程序。

[![](https://p0.ssl.qhimg.com/dm/1024_610_/t01aeaaa0aaeb4e86b3.png)](https://p0.ssl.qhimg.com/dm/1024_610_/t01aeaaa0aaeb4e86b3.png)

图1-1 分发恶意软件



## 1.样本信息

**MD5**：F83D7F4D5A6BFF93F2E39CC0064DEEB8

**包名：**com.android.tester

**应用名：**COVID19

**图标：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c3b78c010ed693e6.png)



## 2.技术分析

该应用安装后将会从受害者的设备中删除该应用程序的图标。这是恶意软件开发人员常用的技巧，使用户认为该应用程序可能已被删除，在后台，该恶意软件尚未删除。相反，它开始准备对其进行攻击

该应用程序targetsdk为22，低版本的系统默认全部授权，无需用户主动授权。以下程序获取了用户设备大量敏感权限。

[![](https://p3.ssl.qhimg.com/dm/576_1024_/t0145bbd04ed2c5cab7.png)](https://p3.ssl.qhimg.com/dm/576_1024_/t0145bbd04ed2c5cab7.png)

图2-1 应用权限列表

该应用程序通过注册开机启动、电源连接等广播启动主服务来保证主服务的安全运行，且会在服务、广播、活动等组件执行结束时通过判断主服务是否正在运行来决定是否启动主服务。

[![](https://p3.ssl.qhimg.com/t01c97c07f0ae3500f6.png)](https://p3.ssl.qhimg.com/t01c97c07f0ae3500f6.png)

图2-2 注册广播用于启动主

应用程序启动后在主服务中通过Socket连接服务器进行通信，每次执行完获取用户数据的操作后会将获取的用户数据写入到输出流中传送到服务端。且该应用程序还可通过下发指令远程控制手机端。IP:144.76.30.213，端口：443。

[![](https://p1.ssl.qhimg.com/dm/1024_531_/t0134025195e61758df.png)](https://p1.ssl.qhimg.com/dm/1024_531_/t0134025195e61758df.png)

图2-3 与服务器通信

**指令列表：**
<td class="ql-align-justify">**指令**</td>|<td class="ql-align-justify">**功能**</td>|
<td class="ql-align-justify">10254</td>|<td class="ql-align-justify">停止录音</td>|
<td class="ql-align-justify">10255</td>|<td class="ql-align-justify">获取壁纸信息</td>|
<td class="ql-align-justify">10256</td>|<td class="ql-align-justify">开始录音</td>|
<td class="ql-align-justify">10257</td>|<td class="ql-align-justify">获取照相机配置信息</td>|
<td class="ql-align-justify">10258</td>|<td class="ql-align-justify">启动设置照相机配置服务</td>|
<td class="ql-align-justify">10259</td>|<td class="ql-align-justify">停止设置照相机配置服务</td>|
<td class="ql-align-justify">10260</td>|<td class="ql-align-justify">设置照相机配置</td>|
<td class="ql-align-justify">10261</td>|<td class="ql-align-justify">遍历文件获取文件名、路径、长度等信息</td>|
<td class="ql-align-justify">10262</td>|<td class="ql-align-justify">捕获了设备的屏幕活动</td>|
<td class="ql-align-justify">10263</td>|<td class="ql-align-justify">捕获了设备的音频</td>|
<td class="ql-align-justify">10264</td>|<td class="ql-align-justify">设置参数</td>|
<td class="ql-align-justify">10265</td>|<td class="ql-align-justify">获取指定文件路径</td>|
<td class="ql-align-justify">10266</td>|<td class="ql-align-justify">获取指定文件内容</td>|
<td class="ql-align-justify">10267</td>|<td class="ql-align-justify">读取文件每行内容</td>|
<td class="ql-align-justify">10268</td>|<td class="ql-align-justify">对文件进行写操作</td>|
<td class="ql-align-justify">10269</td>|<td class="ql-align-justify">获取位置信息</td>|
<td class="ql-align-justify">10270</td>|<td class="ql-align-justify">监控位置变化</td>|
<td class="ql-align-justify">10271</td>|<td class="ql-align-justify">获取通话记录</td>|
<td class="ql-align-justify">10272</td>|<td class="ql-align-justify">获取用户账户信息</td>|
<td class="ql-align-justify">10273</td>|<td class="ql-align-justify">获取联系人信息</td>|
<td class="ql-align-justify">10274</td>|<td class="ql-align-justify">获取通讯录列表中其它信息如邮件、地址</td>|
<td class="ql-align-justify">10275</td>|<td class="ql-align-justify">获取已安装应用信息</td>|
<td class="ql-align-justify">10276</td>|<td class="ql-align-justify">启动其它应用</td>|
<td class="ql-align-justify">10278</td>|<td class="ql-align-justify">传递配置信息到服务器</td>|
<td class="ql-align-justify">10279</td>|<td class="ql-align-justify">拨打指定号码电话</td>|
<td class="ql-align-justify">10281</td>|<td class="ql-align-justify">重新连接服务器</td>|
<td class="ql-align-justify">10282</td>|<td class="ql-align-justify">停止连接服务器</td>|
<td class="ql-align-justify">10283</td>|<td class="ql-align-justify">对指定文件写入指定内容</td>|
<td class="ql-align-justify">10284</td>|<td class="ql-align-justify">执行cmd命令</td>|
<td class="ql-align-justify">10285</td>|<td class="ql-align-justify">判断指定文件是否存在，不存在就创建</td>|
<td class="ql-align-justify">10286</td>|<td class="ql-align-justify">重命名文件</td>|
<td class="ql-align-justify">10287</td>|<td class="ql-align-justify">删除文件</td>|
<td class="ql-align-justify">10288</td>|<td class="ql-align-justify">执行cmd命令删除文件</td>|
<td class="ql-align-justify">10289</td>|<td class="ql-align-justify">设置壁纸</td>|
<td class="ql-align-justify">10290</td>|<td class="ql-align-justify">将一个文件内容写入另一文件</td>|
<td class="ql-align-justify">10291</td>|<td class="ql-align-justify">开启播放媒体文件</td>|
<td class="ql-align-justify">10292</td>|<td class="ql-align-justify">停止播放媒体文件</td>|
<td class="ql-align-justify">10293</td>|<td class="ql-align-justify">压缩文件</td>|
<td class="ql-align-justify">10295</td>|<td class="ql-align-justify">获取设备详细信息</td>|
<td class="ql-align-justify">10296</td>|<td class="ql-align-justify">获取手机、wifi、音频等设置信息</td>|
<td class="ql-align-justify">10297</td>|<td class="ql-align-justify">获取外部存储指定文件名称、长度信息</td>|
<td class="ql-align-justify">10298</td>|<td class="ql-align-justify">读取外部存储指定文件内容</td>|
<td class="ql-align-justify">10299</td>|<td class="ql-align-justify">删除外部存储指定文件</td>|
<td class="ql-align-justify">10303</td>|<td class="ql-align-justify">对通话记录数据库做删除操作</td>|
<td class="ql-align-justify">10304</td>|<td class="ql-align-justify">对联系人数据库做删除操作</td>|
<td class="ql-align-justify">10305</td>|<td class="ql-align-justify">对联系人数据库做插入操作</td>|
<td class="ql-align-justify">10306</td>|<td class="ql-align-justify">锁定屏幕重设密码</td>|
<td class="ql-align-justify">10307</td>|<td class="ql-align-justify">打开网页</td>|
<td class="ql-align-justify">10308</td>|<td class="ql-align-justify">获取已安装应用activity信息</td>|
<td class="ql-align-justify">10311</td>|<td class="ql-align-justify">删除振动设置</td>|
<td class="ql-align-justify">10312</td>|<td class="ql-align-justify">设置振动模式</td>|

（1）该应用程序可在远程执行命令行操作：

[![](https://p5.ssl.qhimg.com/dm/1024_614_/t0111edaab09da71c5d.png)](https://p5.ssl.qhimg.com/dm/1024_614_/t0111edaab09da71c5d.png)

图2-4 远程执行命令行

（2）监听用户短信：

[![](https://p4.ssl.qhimg.com/dm/1024_538_/t016f5e6f4ace952ace.png)](https://p4.ssl.qhimg.com/dm/1024_538_/t016f5e6f4ace952ace.png)

图2-5 监听用户短信

（3）获取联系人信息：包括联系人电话、姓名、住址、email等信息。

[![](https://p0.ssl.qhimg.com/t0194b29b0efe5af400.png)](https://p0.ssl.qhimg.com/t0194b29b0efe5af400.png)

图2-6 获取用户联系人信息

联系人数据库操作：

[![](https://p0.ssl.qhimg.com/dm/1024_187_/t01f7778e5051571905.png)](https://p0.ssl.qhimg.com/dm/1024_187_/t01f7778e5051571905.png)

图2-7 对联系人数据库执行插入操作

（4）获取用户通讯录信息。

[![](https://p0.ssl.qhimg.com/dm/1024_629_/t016819414e124cde45.png)](https://p0.ssl.qhimg.com/dm/1024_629_/t016819414e124cde45.png)

图2-8 获取通讯录信息

（5）监听用户电话状态：

[![](https://p4.ssl.qhimg.com/t01705cf779ae4bbacb.png)](https://p4.ssl.qhimg.com/t01705cf779ae4bbacb.png)

图2-9 监听用户电话

（6）使用麦克风、摄像头麦克风、语音识别、语音通信等设备录音。

[![](https://p3.ssl.qhimg.com/dm/1024_640_/t0109129f36a2ad6b3a.png)](https://p3.ssl.qhimg.com/dm/1024_640_/t0109129f36a2ad6b3a.png)

图2-10 使用麦克风录音

（7）监听用户位置变化：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_382_/t012379493bdf5e1caa.png)

图2-11 监听用户位置变化

（8）该应用还具有开启设备管理器、重设锁屏密码功能。

[![](https://p0.ssl.qhimg.com/dm/1024_600_/t014003fae564900de0.png)](https://p0.ssl.qhimg.com/dm/1024_600_/t014003fae564900de0.png)

图2-12 重设用户锁屏密码



## 3.SpyNote平台

经由SpyNote生成的APK都有类似的配置文件，指定了服务端ip、端口、App名称等信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015ecb5c00d1497ff4.png)

图3-1 SpyNote 样本配置

我们也通过V5.0版本的SpyNote平台打包了一个APK应用，通过文件以及代码对比我们发现该应用程序也是通过SpyNote平台打包的间谍软件。由于打包应用的SpyNote平台版本不同，所以结构和代码会有点差异，但他们的代码运行逻辑却相同。

[![](https://p1.ssl.qhimg.com/t01b3603bc2d0a26fd6.png)](https://p1.ssl.qhimg.com/t01b3603bc2d0a26fd6.png)

图3-2 程序文件结构对比

[![](https://p5.ssl.qhimg.com/t01c64229f0a2e51573.png)](https://p5.ssl.qhimg.com/t01c64229f0a2e51573.png)

图3-3 程序代码结构

SpyNote平台的官网上显示该平台已更新到V6.5版本，且用户需要购买才可以使用。

[![](https://p5.ssl.qhimg.com/t014d9d5415eb6c7c06.png)](https://p5.ssl.qhimg.com/t014d9d5415eb6c7c06.png)

图3-4 SpyNote官网

（1）SpyNote平台集成了大量监控用户手机设备的功能，其中包括以下功能：
1. 短信管理：可进行SMS短信收发和查看功能
1. 联系人管理：联系人数据库插入、删除操作
1. 通话记录管理：通话记录数据库删除操作
1. 位置监听：GPS定位
1. 文件管理：文件的浏览、传输、删除等操作
1. 查看手机系统信息、更改手机设置。
1. 麦克风监听、屏幕捕获
1. APP管理
1. 远程执行cmd命令
[![](https://p0.ssl.qhimg.com/t01f5a6ae2209c07118.png)](https://p0.ssl.qhimg.com/t01f5a6ae2209c07118.png)

图3-5 SpyNote控制面板

（2）利用SpyNote平台创建APK应用。创建应用时可设置服务器IP、端口、以及应用图标、包名等信息。将apk文件安装到手机端，便可对手机实施监控。

[![](https://p3.ssl.qhimg.com/t016bf3479b294a8257.png)](https://p3.ssl.qhimg.com/t016bf3479b294a8257.png)

图3-6 创建被控端应用

（3）以下显示我们通过SpyNote平台打包的应用已与控制端连接成功。

[![](https://p4.ssl.qhimg.com/t011ce91823a6cdd74e.png)](https://p4.ssl.qhimg.com/t011ce91823a6cdd74e.png)

图3-7 服务端与控制端连接成功

（4）SpyNote间谍软件具有强大的命令行执行功能。

[![](https://p4.ssl.qhimg.com/dm/1024_399_/t01558965275230f7e1.png)](https://p4.ssl.qhimg.com/dm/1024_399_/t01558965275230f7e1.png)

图3-8 执行命令行操作

（5）以及管理用户设备文件、应用、查看用户通话记录、联系人列表等功能。

[![](https://p0.ssl.qhimg.com/t01b024aa46b403ae49.png)](https://p0.ssl.qhimg.com/t01b024aa46b403ae49.png)

图3-9 文件、应用、通讯录、联系人管理

SpyNote生成的间谍软件具有强大的监控手机设备功能，包含且不限于查看短信、查看通讯录、拨打电话、发送短信、查看位置、震动、向手机发消息等，安装应用后，服务端的一条命令即可让个人的隐私暴露无遗，造成信息的严重泄露、个人日常行为被监控、手机系统被破坏、个人财产被盗取等危害。



## 4.扩展分析

通过关联分析在恒安嘉新App全景平台态势平台上，我们发现多款SpyNote平台打包的恶意应用。这些恶意程序都是通过早期SpyNote平台打包的应用。

[![](https://p2.ssl.qhimg.com/dm/1024_651_/t01a49b0c0b327e32ea.png)](https://p2.ssl.qhimg.com/dm/1024_651_/t01a49b0c0b327e32ea.png)



## 5.总结

“新型冠状病毒肺炎”的爆发掀起了威胁行为者传播移动恶意程序的热潮。Anubis、Cerberus、Joker等臭名远昭木马利用该热点大量分发恶意程序。“新型冠状病毒肺炎”相关的广告木马、短信蠕虫、勒索病毒也相继出现。

威胁行为者利用“新型冠状病毒肺炎”传播SpyNote间谍软件目的在于窃取用户隐私数据、监控用户行为并达到完全控制受害者手机的目的。SpyNote工具使用门槛极低，经过简单配置即可生成一款间谍软件，不管该间谍软件是针对哪类人群又或者是带有什么样的个人目的、政治目的，用户手机一旦被感染，将完全受他人监控。用户应提高自身网络安全意识，保护设备安全，留意手机上的异常行为和未知软件。

关注”暗影安全实验室”，我们将会持续关注移动安全事件，为用户提供更多移动安全知识。
