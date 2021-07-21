> 原文链接: https://www.anquanke.com//post/id/151919 


# Google Play上的Android/FoulGoal.A间谍软件分析


                                阅读量   
                                **137841**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securingtomorrow.mcafee.com
                                <br>原文地址：[https://securingtomorrow.mcafee.com/mcafee-labs/google-play-users-risk-a-yellow-card-with-android-foulgoal-a/](https://securingtomorrow.mcafee.com/mcafee-labs/google-play-users-risk-a-yellow-card-with-android-foulgoal-a/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0145b73573fa572012.jpg)](https://p2.ssl.qhimg.com/t0145b73573fa572012.jpg)

目前英国球迷们正热情地享受着英国队在世界杯上的表现，伴随着[“Three Lions”](https://www.youtube.com/watch?v=RJqimlFcJsM)的旋律在脑中不断回响，他们热切地盼望着英国队52年的悲痛历史可以在今年终结。但与此同时，最近在Google Play上发布的间谍软件已经对精彩的世界杯的粉丝造成了不小的损害。使用重大事件进行社工并不是什么新鲜事，因为网络钓鱼的电子邮件经常利用灾难和体育赛事来吸引受害者。

“Golden Cup”是一个会在受害者设备上安装间谍软件的恶意应用程序。它通过Google Play发布，并“提供”直播和对所有世界杯记录的搜索功能。McAfee Mobile Security将此威胁识别为了Android/FoulGoal.A; 目前Google已将其从Google Play中删除。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/07/20180711-Cup-1.png)

用户一旦安装了Golden Cup，它就会伪装成一个典型的体育类应用程序，具有多媒体内容和有关世界杯的一些普通信息，大多数此类数据都来自没有恶意活动的Web服务。但是，在后台并且未经用户同意的情况下，应用程序会偷偷地将信息传输到另一台服务器。



## 捕获的数据

Golden Cup从受害者的设备中捕获大量的加密数据：
- 电话号码
- 已安装的包
- 设备型号、制造商、序列号
- 可用的内部存储容量
- 设备ID
- Android版本
- IMEI，IMSI
此间谍软件可能只是更大感染活动的第一阶段，因为它具有从远程源加载dex文件的能力，该应用程序会连接到其控制服务器，并尝试下载、解压缩和解密第二阶段。

Android/FoulGoal.A检测屏幕何时打开或关闭，并将其记录在其内部文件scrn.txt中，字符串“on”和“off”表示其被用来追踪用户查看屏幕的时间：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/07/20180711-Cup-2.png)

设备和恶意服务器之间的通信通道使用了消息队列遥测传输协议（MQTT）来发送和接收命令。



## 数据加密

用户数据在被发送到控制服务器之前使用了AES加密。Cryptor类提供加密和解密功能。doCrypto函数被定义为常用函数。作为函数的第一个参数，“1”表示加密，“2”表示解密模式：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/07/20180711-Cup-3.jpg)

加密密钥是使用SecureRandom函数动态生成的，SecureRandom函数会在设备上生成唯一值，以对数据进行混淆处理。addKey函数则将加密密钥嵌入到加密数据中，最后带密钥的数据再被上传到控制服务器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/07/20180711-Cup-4.jpg)

我们认为恶意软件作者使用了此AES加密技术来上传所有信息，这有助于躲避Google Bouncer和网络检测产品的检测。

我们的初步分析表明至少有300次感染，我们怀疑是在6月8日至12日之间，也就是在第一次世界杯比赛开始之前。



## 第二阶段

攻击的第二阶段利用加密的dex文件，该文件扩展名为.data，由第一阶段恶意软件下载并动态加载，它使用了与上传加密文件时相同的提取机制，可以从内容的大小和第一级恶意软件中的固定号码来识别解密密钥的位置。

解密过后，我们可以看到压缩格式的out.dex，而这个dex文件具有间谍功能，可以从受感染的设备窃取SMS消息、联系人、多媒体文件和设备位置。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/07/20180711-Cup-5.jpg)

第二阶段的控制服务器与第一阶段的控制服务器不同，而远程服务器上的加密方法和服务器文件夹结构则与第一阶段相同。

我们在控制服务器上的加密数据中找到了一个受害者的GPS位置信息和录制的音频文件（.3gp）。



## 变种

我们还发现了由此威胁的作者创建的另外两个同类型变种，它们被作为约会应用程序发布到Google Play上。虽然所有应用程序都已从Google Play中删除，但我们仍然可以看到我们的遥测数据感染的迹象，因此我们知道这些应用程序在某些用户的设备上仍处于活跃状态。

我们的遥测数据显示，虽然全球用户都下载了该应用程序，但大多数下载都发生在中东，很可能是因为一条希伯来语的世界杯主题的Twitter帖子诱导了用户下载该应用程序以关注世界杯的最新进展信息。

McAfee Mobile Security用户可以免受被检测为Android / FoulGoal.A的此威胁的所有变种的侵害。

审核人：yiwang   编辑：边边
