> 原文链接: https://www.anquanke.com//post/id/94072 


# 黄金鼠组织（APT-C-27）叙利亚地区的定向攻击活动


                                阅读量   
                                **565037**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01e628bbd9da503c8a.jpg)](https://p0.ssl.qhimg.com/t01e628bbd9da503c8a.jpg)



发布机构：360威胁情报中心
- 2014年11月起至今，黄金鼠组织（APT-C-27）对叙利亚地区展开了有组织、有计划、有针对性的长时间不间断攻击。
- 攻击平台主要包括Windows与Android，截至目前我们一共捕获了Android样本29个，Windows样本55个，涉及的C&amp;C域名9个。
- PC与Android端间谍软件主要伪装成Telegram等聊天软件，并通过水坑等攻击方式配合社会工程学手段进行渗透。
- 相关恶意可执行程序多为“.exe”和“.scr”扩展名，但是这些程序都伪装成Word、聊天工具图标，并通过多种诱导方式诱导用户中招。
- 攻击者在诱饵文档命名时也颇为讲究，如“حمص تلبيسة قصف بالهاون”（炮击霍姆斯），此类文件名容易诱惑用户点击。
- 攻击者针对PC平台使用了大量的攻击载荷，包括Multi-stage Dropper、njRAT、VBS脚本、JS脚本、Downloader等恶意程序，此类恶意程序多为远控，主要功能包括上传下载文件、执行shell等。
- Android端后门程序功能主要包括定位、短信拦截、电话录音等，并且还会收集文档、图片、联系人、短信等情报信息。
- 通过相关信息的分析，发现该组织极有可能来自阿拉伯国家。
关键词：黄金鼠、APT-C-27、叙利亚、Windows、Android、水坑、伪装、诱饵文档、RAT、后门



## 概述

从2014年11月起至今，黄金鼠组织（APT-C-27）对叙利亚地区展开了有组织、有计划、有针对性的长时间不间断攻击。攻击平台从开始的Windows平台逐渐扩展至Android平台，截至目前我们一共捕获了Android平台攻击样本29个，Windows平台攻击样本55个，涉及的C&amp;C域名9个。

2016年6月，我们首次注意到该攻击组织中涉及的PC端恶意代码，并展开关联分析，但通过大数据关联分析发现相关攻击行动最早可以追溯到 2014年11月，并关联出数十个恶意样本文件，包括PC和Android平台。此外，Android和PC平台的恶意样本主要伪装成聊天软件及一些特定领域常用软件，通过水坑攻击方式配合社会工程学手段进行渗透，向特定目标人群进行攻击，进一步结合恶意代码中诱饵文件的内容和其他情报数据，我们判定这是一次以窃取敏感信息为目的的针对性攻击，且目标熟悉阿拉伯语。

2015年7月，叙利亚哈马市新闻媒体在Facebook上发布了一则消息，该条消息称带有“土耳其对叙利亚边界部署反导弹系统进行干预，详细信息为[http://www.gulfup.com/?MCVlNX](http://www.gulfup.com/?MCVlNX)”的信息为恶意信息，并告诫大家不要打开信息中链接，该链接为黑客入侵链接，相关C&amp;C为31.9.48.183。哈马市揭露的这次攻击行动，就是我们在 2016年6月发现的针对叙利亚地区的APT攻击。从新闻中我们确定了该行动的攻击目标至少包括叙利亚地区，其载荷投递方式至少包括水坑式攻击。

360威胁情报中心将APT-C-27组织命名为黄金鼠，主要是考虑了以下几方面的因素：一是该组织在攻击过程中使用了大量的资源，说明该攻击组织资源丰富，而黄金鼠有长期在野外囤积粮食的习惯，字面上也有丰富的含义；二、该攻击组织通常是间隔一段时间出来攻击一次，这跟鼠有相通的地方；三是黄金仓鼠是叙利亚地区一种比较有代表性的动物。因此，根据360威胁情报中心对APT组织的命名规则（参见《2016年中国高级持续性威胁研究报告》），我们命名APT-C-27组织为“黄金鼠”。



## 攻击组织的三次攻击行动

[![](https://p3.ssl.qhimg.com/t016cb9f710eb8c8130.png)](https://p3.ssl.qhimg.com/t016cb9f710eb8c8130.png)

图1 该攻击组织相关重点事件时间轴

> 注：
圆形蓝色里程碑：相关典型后门首次出现时间
正方形灰色里程碑：相关典型后门再次出现时间
三角形深蓝色里程碑：相关C&amp;C出现时间
菱形黑色里程碑：重要事件出现的时间
<td width="15%">攻击行动</td><td width="24%">活跃时间</td><td width="30%">主要载荷</td><td width="30%">主要C&amp;C</td>
<td width="15%">第一次</td><td width="24%">2014.10 – 2015.7</td><td width="30%">njRAT、Downloader</td><td width="30%">bbbb4.noip.me31.9.48.183</td>
<td width="15%">第二次</td><td width="24%">2015.8 – 2016.11</td><td width="30%">DarkKomet、VBS Backdoor、AndroRAT</td><td width="30%">basharalassad1sea.noip.me31.9.48.183</td>
<td width="15%">第三次</td><td width="24%">2016.12 – 至今</td><td width="30%">Android RAT、定制RAT、JS Backdoor、JS后门</td><td width="30%">82.137.255.56telgram.strangled.netchatsecurelite.us.to</td>

chatsecurelite.us.to

表1  三波攻击行动

第一次攻击行动集中在2014年10月到2015年7月，该期间攻击组织主要使用开源远控njRAT和Downloader进行攻击，攻击载荷并不复杂，使用的C&amp;C主要为bbbb4.noip.me和31.9.48.183。但是2015年7月，该组织使用的C&amp;C（31.9.48.183）被叙利亚哈马市新闻媒体在Facebook曝光。

第二次攻击行动集中在2015年7月到2016年11月，在这期间攻击者使用了多种不同类型的攻击载荷。在2015年8月攻击者开始使用Delphi编写的DarkKomet远控，此外，在2015年11月针对Android操作系统的攻击开始出现，并使用了AndroRAT恶意程序，期间使用的C&amp;C主要是31.9.48.183，但是到了2016年1月，该组织开始使用新的域名basharalassad1sea.noip.me作为C&amp;C服务器。另外，本次攻击行动具有代表性的就是2016年10月开始使用Facebook进行水坑攻击，并使用全新的VBS后门作为攻击载荷。

第三次攻击行动集中在2016年12月到至今，该期间攻击组织表现尤为活跃，使用的攻击载荷变得更加丰富。在2017年4月使用了telgram.strangled.net钓鱼页面进行水坑攻击，并且根据telegram升级程序的步骤制作RAT进行攻击，攻击平台包括PC与Android，C&amp;C服务器也改变成82.137.255.56。此外，在2017年5月，首次出现了JS后门，并结合前期的VBS后门、RAT同时攻击。在这次攻击中需要引起重视的是，在2017年9月，攻击者开始使用域名chatsecurelite.us.to替代原有域名telgram.strangled.net进行水坑攻击，并着重针对Android平台进行攻击，开发了一系列不同伪装形式的RAT，最近两个月，攻击者基本上都只对Android平台进行攻击。



## 载荷投递

### 水坑攻击

APT 攻击中主流的水坑攻击主要分为以下三种：1、攻击者将被攻击目标关注的网站攻陷，并植入恶意代码（俗称挂马），当目标访问时可能会触发漏洞从而植入恶意代码；2、攻击者将被攻击目标关注的网站攻陷，并把网站上一些可信应用或链接替换为攻击者所持有的恶意下载链接，当目标访问被攻陷的网站并将恶意下载链接的文件下载并执行，则被植入恶意代码；3、攻击者搭建一些具有迷惑性的网站，通过诱导用户转向此网站进行恶意程序的下载，如鱼叉邮件正文中嵌入恶意网址或基于社交网络的诱导。在该事件中，攻击者选择的是第三种水坑攻击方式。

#### <a name="_Toc503261513"></a>（一）   钓鱼网站

PC端间谍软件主要伪装成Telegram、Chrome等升级软件，并通过挂载在具有迷惑性的下载网址上引诱目标下载安装。攻击者注册了一系列类似于[http://telgram.strangled.net/](http://telgram.strangled.net/)、http://chatsecurelite.us.to这种具有迷惑性的网址，并且上面都挂着部分正常样本用于干扰、迷惑。表2是PC端RAT程序具体下载链接和链接对应文件MD5。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018c6167d6493396d3.png)

表2  PC端RAT程序下载链接和链接对应文件MD5

Android端间谍软件主要伪装成“System Package Update”、“Telegram Update”、“ChatSecure Ultimate 2017”、“Ms Office Update 2017”、“WordActivation”、“تسريع_نت_مجاني”等软件，这些软件普遍为一些聊天软件更新程序，并通过挂载在具有迷惑性的下载网址上引诱目标下载安装。

图2为攻击者钓鱼页面（chatsecurelite.us.to/تحميل-البرنامج/）。

[![](https://p1.ssl.qhimg.com/t01a2e09081d997fd84.png)](https://p1.ssl.qhimg.com/t01a2e09081d997fd84.png)

图2 攻击者钓鱼页面

点击上图中的应用会跳转至真正后台进行应用下载，如图3所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fc9c26044196eec0.png)

图3 攻击者后台页面

目前该链接为正常状态，表3是某Android端RAT程序具体下载链接和链接对应的APK文件 MD5。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011a00e6b253421eff.png)

表3  Android端RAT程序下载链接和链接对应的APK文件MD5

通过分析我们发现telgram.strangled.net这个域名从2017年9月份停止使用，9月份之后，开始使用chatsecurelite.us.to这个域名。此外，通过链接下载的APK文件或EXE程序图标都会被修改成正常的软件更新程序欺骗用户，从而导致用户中招。

#### <a name="_Toc503261514"></a>（二）   社交网络

除了上述诱导用户到指定链接下载恶意程序外，攻击者还利用社交网络Facebook传播恶意程序，甚至将带有水坑链接的这些消息置顶，以更好的达到欺骗效果。图4、图5、图6都是攻击者在Facebook上诱导用户点击水坑链接的截图，用户点击该链接实际上会下载恶意载荷。

[![](https://p0.ssl.qhimg.com/t01ad0ccb19b8acf1de.png)](https://p0.ssl.qhimg.com/t01ad0ccb19b8acf1de.png)

图4  Facebook传播恶意载荷1

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0107ab0ff35f4b12b4.png)

图5  Facebook传播恶意载荷2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e70d60237010f31a.png)

图6  Facebook传播恶意载荷3

从上图可以知道，攻击者首先将部分恶意载荷上传至下载站，如[https://jumpshare.com/、http://www.mediafire.com/](https://jumpshare.com/%E3%80%81http:/www.mediafire.com/)，然后在Facebook上发送欺骗性消息，欺骗用户到指定网站下载恶意载荷。表4是某VBS载荷具体下载链接和链接对应的VBS文件 MD5。

[![](https://p5.ssl.qhimg.com/t012cf1db2f0f813250.png)](https://p5.ssl.qhimg.com/t012cf1db2f0f813250.png)<br>
表4  某VBS载荷下载链接和链接对应的VBS文件MD5

### <a name="_Toc503261515"></a>疑似鱼叉邮件

相关恶意可执行程序多为“.exe”和“.scr”扩展名，但是这些文件都伪装成doc、telegram、chrome图标，并且文件中还包含一些用以迷惑用户的文档，从以往此类事件的分析经验来看，一般这类可执行程序均进行压缩，以压缩包形态发送。压缩包和包内恶意代码文件名一般是针对目标进行精心构造的文件名，相关文件名一般与邮件主题、正文内容和恶意代码释放出的诱饵文档内容相符，因此这次攻击行动有可能也会以鱼叉邮件的方式进行投递。<a name="_Toc476214387"></a>



## 诱导方式

攻击组织在这次行动中主要使用以下几种诱导方式。

### <a name="_Toc503261517"></a> 文档诱导

文档诱导主要是指攻击者通过正常PDF、DOC文档，提醒用户到恶意URL处更新最新程序或诱导用户安装APK文件，从而导致用户中招。

图7为其中某诱饵文档，该文档指出用户所用版本为旧版本，提醒用户及时更新，但是实际上文档中URL为恶意URL，下载的程序为RAT。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01456731169345a206.png)

图7 诱饵文档1

下图为诱导用户安装APK的PDF文件，如用户按照此方式进行安装，APK会隐藏图标，在后台静默执行恶意程序。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fc4a3ba232a55c5e.png)

图8 诱饵文档2

### <a name="_Toc503261518"></a> 文件图标伪装

PC与Android端特洛伊木马通过图标进行伪装，涉及的图标主要包括聊天工具、WORD文档、人物头像等图标，其中Android平台涉及的伪装图标主要是聊天工具和Word图标，如图9所示。

[![](https://p3.ssl.qhimg.com/t01db56329fae573c23.png)](https://p3.ssl.qhimg.com/t01db56329fae573c23.png)

图9  Android端欺骗性软件图标

PC平台上涉及的伪装图标主要有人物头像、聊天工具升级图标等，如图10所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012a436aa71f5ccba2.png)

图10  PC端欺骗性软件图标

### <a name="_Toc503261519"></a> 使用特殊文件格式

攻击者使用的部分载荷采用scr后缀的文件名，scr文件格式是Windows系统中屏幕保护程序，为exe的衍生类型。此外，攻击者在使用这种文件格式时，通常会对文件命名一个诱饵名字，如“حمص تلبيسة قصف بالهاون.scr”（炮击霍姆斯），霍姆斯是叙利亚的一个城市，并且被大规模武装袭击过。攻击者利用此类文件名及文件格式容易引起用户好奇心，从而点击文件中招。

### <a name="_Toc503261520"></a> 正常软件更新伪装

攻击者不仅对恶意程序文件名、图标进行伪装，而且还会针对某些恶意更新程序（如telegram.exe，telegram是叙利亚一个比较流行的通讯软件）伪装其正常更新页面。当点击该恶意程序时，弹出正常的软件更新页面以迷惑用户，从而隐藏其层层释放恶意RAT的行为，普通用户很难辨别出此类软件恶意行为。图11为某一恶意程序运行的截图。

### [![](https://p2.ssl.qhimg.com/t013acb84392bb8c25a.png)](https://p2.ssl.qhimg.com/t013acb84392bb8c25a.png)

图11  软件更新伪装界面



## 后门分析

### <a name="_Toc503261522"></a><a name="_Toc476214388"></a> Android

1）Android平台的样本，伪装成“ChatSecure”、“WordActivation”、“whatsappupdate_2017”、“تسريع_نت_مج”等常用聊天办公软件，本质是一个RAT。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0158511c4b429c0fd8.png)

图12  “WordActivation”运行界面

2）Android设备管理器是Google提供的一套API，允许用户以system权限管理设备，一个APP激活设备管理器后，不能被轻易卸载（必须先取消激活）。这些RAT程序动后诱导用户激活设备管理器，然后隐藏图标在后台运行。



图13 激活设备管理器代码[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/300_50_/t011f993cf25cccd86a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ee510b56089795d3.png)

图14 诱导用户激活设备管理器

3）启动RAT监控模块。RAT模块默认与31.9.48.183这个C&amp;C建立连接，接收命令和参数。

[![](https://p0.ssl.qhimg.com/t019bac6cc179c0b85b.png)](https://p0.ssl.qhimg.com/t019bac6cc179c0b85b.png)

[![](https://p3.ssl.qhimg.com/t01856277404933afbf.png)](https://p3.ssl.qhimg.com/t01856277404933afbf.png)

图15 启动RAT监控模块

4）依据云端指令盗取用户手机中WhatsApp、Viber等软件的数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01998bdce15b1ed596.png)

图16 盗取用户WhatsApp、Viber的数据

5）样本具有录音、拍照、GPS定位、上传联系人/通话记录/短信/文件、执行云端命令等能力，除伪装的APP名字不一样，功能基本相同。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f7c8a62719fe3a83.png)

图17 样本核心代码的结构

6）样本主要以xml格式向云端发送数据和接收指令。

[![](https://p2.ssl.qhimg.com/t0188caf2d8b72caac0.png)](https://p2.ssl.qhimg.com/t0188caf2d8b72caac0.png)[![](https://p1.ssl.qhimg.com/t016299bc91912bef91.png)](https://p1.ssl.qhimg.com/t016299bc91912bef91.png)

图18 发送的数据和接收的指令

7）样本接收的指令如表5所示。经分析，这些指令都可以执行。
<td width="173">指令</td><td width="284">功能</td>
<td width="173">16</td><td width="284">心跳打点</td>
<td width="173">17</td><td width="284">connect</td>
<td width="173">18</td><td width="284">获取指定文件的基本信息</td>
<td width="173">19</td><td width="284">下载文件</td>
<td width="173">20</td><td width="284">上传文件</td>
<td width="173">21</td><td width="284">删除文件</td>
<td width="173">22</td><td width="284">按照云端指令复制文件</td>
<td width="173">23</td><td width="284">按照云端指令移动文件</td>
<td width="173">24</td><td width="284">按照云端指令重命名文件</td>
<td width="173">25</td><td width="284">运行文件</td>
<td width="173">28</td><td width="284">按照云端指令创建目录</td>
<td width="173">29</td><td width="284">执行云端命令</td>
<td width="173">30</td><td width="284">执行一次ping命令</td>
<td width="173">31</td><td width="284">获取并上传联系人信息</td>
<td width="173">32</td><td width="284">获取并上传短信</td>
<td width="173">33</td><td width="284">获取并上传通话记录</td>
<td width="173">34</td><td width="284">开始录音</td>
<td width="173">35</td><td width="284">停止并上传录音文件</td>
<td width="173">36</td><td width="284">拍照</td>
<td width="173">37</td><td width="284">开始GPS定位</td>
<td width="173">38</td><td width="284">停止GPS定位并上传位置信息</td>
<td width="173">39</td><td width="284">使用云端发来的ip/port</td>
<td width="173">40</td><td width="284">向云端报告当前使用的ip/port</td>
<td width="173">41</td><td width="284">获取已安装应用的信息</td>

表5  Android端RAT样本指令与功能对应关系

### <a name="_Toc503261523"></a> Windows

#### <a name="_Toc503261524"></a>（一）   Multi-stage Dropper

此类间谍软件伪装成聊天工具telegram的升级程序进行传播，为使用户中招和更好的隐藏自身，该恶意程序在多方面进行了伪装，不但使用具有诱惑性的名字和图标，而且还做了可以以假乱真的安装界面来迷惑用户。该恶意程序运行后会有一个伪装的telegram升级界面，在用户一步步点击进行升级的过程中，恶意程序通过层层释放，最终会将一个RAT程序释放到用户电脑并运行。下图是某恶意程序执行流程图。

[![](https://p1.ssl.qhimg.com/t0186825f8fd46b1c78.png)](https://p1.ssl.qhimg.com/t0186825f8fd46b1c78.png)

图19 执行流程图

该RAT程序使用.net框架编写，通过接受控制端命令对用户计算机进行控制，如文件修改执行，杀进程等操作。通过对比发现该RAT与Android平台的RAT样本的命令除个别外其余编号对应的功能基本一致。对应关系如表6所示。
<td width="173">指令</td><td width="284">功能</td>
<td width="173">18</td><td width="284">获取磁盘信息</td>
<td width="173">19</td><td width="284">上传文件</td>
<td width="173">20</td><td width="284">下载文件</td>
<td width="173">21</td><td width="284">删除文件</td>
<td width="173">22</td><td width="284">复制文件</td>
<td width="173">23</td><td width="284">移动文件</td>
<td width="173">24</td><td width="284">重命名文件</td>
<td width="173">25</td><td width="284">运行文件</td>
<td width="173">26</td><td width="284">压缩文件</td>
<td width="173">27</td><td width="284">解压文件</td>
<td width="173">28</td><td width="284">创建目录</td>
<td width="173">31</td><td width="284">上传屏幕截图</td>
<td width="173">32</td><td width="284">停止屏幕截图</td>
<td width="173">33</td><td width="284">获取进程列表</td>
<td width="173">34</td><td width="284">结束进程</td>
<td width="173">35</td><td width="284">执行命令</td>

表6  PC端RAT样本指令与功能对应关系

#### <a name="_Toc503261525"></a>（二）   njRAT

该组织除了自己开发Multi-stage Dropper程序外，也使用近年来最为活跃的木马家族之一的远控njRAT。在使用njRAT时并不是直接使用，而是对在njRAT的基础上进行了二次封装，使用C#为njRAT加了一层壳，并对壳的代码进行了大量的混淆。该壳的作用是在内存中加载njRAT运行，防止njRAT被杀毒软件检测。

njRAT又称Bladabindi，是通过.net框架编写的RAT程序，通过控制端可以操作受控端的注册表，进程，文件等，还可以对被控端的键盘进行记录。同时njRAT采用了插件机制，可以通过不同的插件来扩展njRAT的功能。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016ce84d12682dc08c.png)

图20 配置信息

[![](https://p4.ssl.qhimg.com/t01e506f01b7a19e10e.png)](https://p4.ssl.qhimg.com/t01e506f01b7a19e10e.png)

图21 键盘记录

#### <a name="_Toc503261526"></a>（三）   C# Downloader

在进行关联分析中还发现该组织也使用Downloader进行二次下次，该Downloader使用具有诱惑力的名字，后缀也使用scr来诱导用户点击，如حمص تلبيسة قصف بالهاون.scr，شام الحرة.scr（炮击霍姆斯）。

Downloader主要是从pastebin.com去下载文件执行，在通过下载的文件执行核心功能，如backdoor，RAT等。

[![](https://p0.ssl.qhimg.com/t0198aea0fc8d2e54b3.png)](https://p0.ssl.qhimg.com/t0198aea0fc8d2e54b3.png)

图22 下载功能1

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018a0eddf892f28a32.png)

图23 下载功能2

#### <a name="_Toc503261527"></a>（四）   VBS Backdoor

该组织在进行攻击时使用大量的VBS脚本，并且该脚本经过大量混淆，下图为其中一个VBS脚本的部分代码。除此之外，使用的VBS脚本不再是简单的下载文件，而且完整的一个后门程序。

[![](https://p1.ssl.qhimg.com/t0137106821ae7b5ea9.png)](https://p1.ssl.qhimg.com/t0137106821ae7b5ea9.png)

图24 部分VBS代码

将代码去混淆后，得到主要代码。

[![](https://p0.ssl.qhimg.com/t0157d1c854a4ad5cbb.png)](https://p0.ssl.qhimg.com/t0157d1c854a4ad5cbb.png)

图25 主要功能代码

该VBS主要功能是与C&amp;C(31.9.48.183:1984)进行通信，表7是主要指令对用的功能。
<td width="173">指令</td><td width="284">功能</td>
<td width="173">excecute</td><td width="284">执行远端命令</td>
<td width="173">update</td><td width="284">更新载荷</td>
<td width="173">uninstall</td><td width="284">卸载自身</td>
<td width="173">send</td><td width="284">下载文件</td>
<td width="173">site-send</td><td width="284">指定网站下载文件</td>
<td width="173">recv</td><td width="284">上传数据</td>
<td width="173">enum-driver</td><td width="284">枚举驱动</td>
<td width="173">enum-faf</td><td width="284">枚举指定目录下的文件</td>
<td width="173">enum-process</td><td width="284">枚举进程</td>
<td width="173">cmd-shell</td><td width="284">执行shell</td>
<td width="173">delete</td><td width="284">删除文件</td>
<td width="173">exit-process</td><td width="284">结束进程</td>
<td width="173">sleep</td><td width="284">设置脚本的睡眠时间</td>

表7  VBS样本指令与功能对应关系

#### <a name="_Toc503261528"></a>（五）   JS Backdoor<a name="_Toc476214390"></a>

在此次行动中攻击者还使用了JavaScript脚本，脚本为完整后门程序。部分代码如图26所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c2357f073f2fd4fc.png)

图26  JS脚本部分功能代码

该样本功能是与82.137.255.56:1933进行通信，主要指令如表8所示。
<td width="173">指令</td><td width="284">功能</td>
<td width="173">Sc</td><td width="284">在临时目录创建文件并运行</td>
<td width="173">Ex</td><td width="284">获取指定的环境变量</td>
<td width="173">Rn</td><td width="284">更新脚本程序并运行</td>
<td width="173">Up</td><td width="284">在临时目录创建脚本并运行</td>
<td width="173">Un</td><td width="284">执行命令</td>

表8  JS样本指令与功能对应关系

综上所述，可以看出攻击者在攻击过程中使用了大量不同类型的攻击载荷。另外，需要特别说明的是，除上述攻击载荷外，该组织在攻击过程中还使用了Delphi开发的远控程序DarkKomet和XtremeRAT，使用C&amp;C为31.9.48.183，但该类型远控占比较低且为公开远控，所以这里不再单独进行分析。



## C&amp;C分析

本章就攻击者使用的C&amp;C进行分析，发现C&amp;C使用的都是子域名（如telgram.strangled.net）或硬编码IP地址，攻击使用此类方式来隐藏自己的真实身份，安全研究机构或人员很难找到相关线索信息进行关联回溯，这说明了该组织对自己的真实身份有较强的保护意识。

### <a name="_Toc476214392"></a><a name="_Toc503261530"></a> C&amp;C时间分布
<td width="39%">C&amp;C使用时间</td><td width="60%">主要C&amp;C</td>
<td width="39%">2014年</td><td width="60%">bbbb4.noip.me</td>
<td width="39%">2015年~2016年</td><td width="60%">basharalassad1sea.noip.me、31.9.48.183</td>
<td width="39%">2017年</td><td width="60%">telgram.strangled.net、chatsecurelite.us.to82.137.255.56</td>

表9  域名时间分布

从上表中可以看出该组织攻击行动使用的C&amp;C并不多，2014年第一次攻击行动使用的域名为bbbb4.noip.me，在2015到2016年期间，使用的主要C&amp;C是basharalassad1sea.noip.me和31.9.48.183。不过2017年开始，以前使用的C&amp;C基本都不再用了，而是使用telgram.strangled.net、chatsecurelite.us.to、82.137.255.56这三个C&amp;C，通过分析发现2017年9月份之前攻击者水坑攻击使用的是telgram.strangled.net，9月份之后，开始使用chatsecurelite.us.to这个域名，而攻击载荷主要使用82.137.255.56这个C&amp;C。

### <a name="_Toc503261531"></a> C&amp;C服务器端口分布

攻击者使用的C&amp;C服务器虽说较少，但是不同攻击载荷使用了不同的端口，下图为C&amp;C服务器端口分布。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d9e0ace9eba50d6e.png)

图27  C&amp;C服务器端口分布

从上图C&amp;C服务器端口分布来看，攻击者偏向于使用1177、1740、5552端口，其占比居前三位，分别为33.9%、19.4%、8.1%。其中1177和5552端口主要用于njRAT远控，1740端口多用于移动端RAT样本。紧随其后的有1940、1933端口，其占比分别为6.5%、4.8%，此二类端口多用于VBS后门中。另外其他类别主要包括3000、1990、1610、1984、4010、1920等端口。

### <a name="_Toc503261532"></a><a name="_Toc476214393"></a> C&amp;C、IP及部分样本对应关系

### [![](https://p0.ssl.qhimg.com/t01e4ac2447c5ff006f.png)](https://p0.ssl.qhimg.com/t01e4ac2447c5ff006f.png)

图28  C&amp;C、 IP及部分样本对应关系

通过图28中的C&amp;C、IP及部分样本对应关系，很明确说明了PC端样本与Android平台样本存在强关联。此外IP 82.137.255.56与31.9.48.183都是攻击者所持有，后面第八章会重点分析两IP之间的关系。通过分析所有样本，发现早期PC端样本主要使用31.9.48.183作为C&amp;C服务器，而后期PC与Android端则主要使用C&amp;C服务器为82.137.255.56<a name="_Toc476214394"></a>。



## PC与Android关联分析

本章主要就该攻击组织使用的恶意代码、文件名、C&amp;C服务器等层面进行关联分析。

### <a name="_Toc503261534"></a> 共用C&amp;C
<td width="30%">针对操作系统</td><td width="69%">PC</td>
<td width="30%">MD5</td><td width="69%">d84a553f9f272c8e2e6db525fa4f9977</td>
<td width="30%">C&amp;C</td><td width="69%">82.137.255.56:5601</td>

表10  PC样本基本信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ca3129fe2cb3f002.png)

图29  PC样本代码截图（C&amp;C地址）
<td width="29%">针对操作系统</td><td width="70%">Android</td>
<td width="29%">MD5</td><td width="70%">cf507aa156fe856e74f22b80e83055fd</td>
<td width="29%">C&amp;C</td><td width="70%">82.137.255.56:1740</td>

表11  Android样本基本信息

[![](https://p5.ssl.qhimg.com/t01e57d7ef933696af5.png)](https://p5.ssl.qhimg.com/t01e57d7ef933696af5.png)

图30  Android样本代码截图（C&amp;C地址）

从掌握的样本信息发现，近期Android与PC端样本使用C&amp;C都是 82.137.255.56，只是端口不一样。

### <a name="_Toc503261535"></a> 共用远控指令
<td width="30%">针对操作系统</td><td width="69%">PC</td>
<td width="30%">MD5</td><td width="69%">ad9c09bb6b22cb970706b5e3ffdf7621</td>
<td width="30%">C&amp;C</td><td width="69%">82.137.255.56</td>

表12  PC样本基本信息

[![](https://p3.ssl.qhimg.com/t0109c13cf59a16e05b.png)](https://p3.ssl.qhimg.com/t0109c13cf59a16e05b.png)

图31  PC样本代码截图（远控指令）
<td width="29%">针对操作系统</td><td width="70%">Android</td>
<td width="29%">MD5</td><td width="70%">cf507aa156fe856e74f22b80e83055fd</td>
<td width="29%">C&amp;C</td><td width="70%">82.137.255.56</td>

表13  Android样本基本信息

[![](https://p5.ssl.qhimg.com/t010f14ab7652da9bd4.png)](https://p5.ssl.qhimg.com/t010f14ab7652da9bd4.png)

图32  Android样本代码截图（远控指令）

从上述对比信息知道，PC与Android端的RAT远端指令20、21、22都一致，分别是下载文件、删除文件、复制文件。实际攻击在PC与Android端RAT样本使用的是同一套远控指令，都从数字17开始，这间接说明了攻击方都是同一伙人。

### <a name="_Toc503261536"></a> 共用水坑链接
<td width="22%">针对操作系统</td><td width="77%">PC</td>
<td width="22%">MD5</td><td width="77%">ad9c09bb6b22cb970706b5e3ffdf7621</td>
<td width="22%">下载链接</td><td width="77%">[http://telgram.strangled.net/wp-content/uploads/2017/](http://telgram.strangled.net/wp-content/uploads/2017/)telegram.exe</td>

表14  PC样本基本信息
<td width="21%">针对操作系统</td><td width="78%">Android</td>
<td width="21%">MD5</td><td width="78%">090ba0eef20b8fdcefd619ddc634b440</td>
<td width="21%">下载链接</td><td width="78%">[http://chatsecurelite.us.to/wp-content/uploads/2017/](http://chatsecurelite.us.to/wp-content/uploads/2017/)ChatSecurePro.apk</td>

表15  Android样本基本信息

通过表14和表15我们知道PC与Android端使用的水坑链接目录结构一致。实际上telgram.strangled.net、chatsecurelite.us.to这两个域名都是攻击者持有，且对应的IP都是82.137.255.56，只是攻击者从2017年9月开始使用chatsecurelite.us.to这个域名，并在11月将对应IP改为82.137.255.57。

### <a name="_Toc503261537"></a> 共用文件名

攻击行动中PC与Android平台上的间谍软件使用的文件名大多是一些聊天软件名，如telegram.exe。
<td width="64">平台</td><td width="236">Md5</td><td width="174">文件名</td>
<td width="64">PC</td><td width="236">ad9c09bb6b22cb970706b5e3ffdf7621</td><td width="174">telegram.exe</td>
<td width="64">Android</td><td width="236">a5a7ad37a06d0beac8da7ae1663db001</td><td width="174">telegramupdate_2017.apk</td>

表16  样本文件名

从上表可以看出该组织针对这两种平台都喜欢使用聊天软件名。

### <a name="_Toc503261538"></a> 共用字符串

攻击行动中PC与Android平台间谍软件代码中都包含“HAMZA_DELIMITER_STOP”等字符串, 此字符串是xml格式数据的结尾标志。此外发现PC与Android端样本代码中都使用了大量阿拉伯语，如 “لايمكن ضفط、 “فشل التحميل”等字符串。
<td width="64">平台</td><td width="236">Md5</td><td width="174">字符串</td>
<td width="64">PC</td><td width="236">ad9c09bb6b22cb970706b5e3ffdf7621</td><td width="174">HAMZA_DELIMITER_STOP、وصول غير مسموح（不允许访问）</td>
<td width="64">Android</td><td width="236">a5a7ad37a06d0beac8da7ae1663db001</td><td width="174">HAMZA_DELIMITER_STOP、فشل التحميل（加载失败）</td>

表17  样本中涉及的字符串

通过上述所有的关联分析，可以明确知道PC与Android端样本来自同一组织开发，并且该组织熟悉阿拉伯语。

## 特殊线索信息

### <a name="_Toc503261540"></a> PDB路径

PDB路径有一定地域特征。
<td width="51%">样本MD5</td><td width="48%">pdb路径</td>
<td width="51%">871e4e5036c7909d6fd9f23285ff39b5</td><td width="48%">aboomar3laqat.pdb</td>
<td width="51%">11b61b531a7bbc7668d7d346e4a17d5e</td><td width="48%">C:\Users\Th3ProSyria\Desktop\cleanPROs\cleanPROs\obj\Debug\NJ.pdb</td>

表18  PC样本PDB路径

上表是PC平台中部分PE文件的PDB路径，这个路径就是恶意代码作者本机的文件路径，从相关用户名“Th3ProSyria”、“aboomar”来看，这些用户名更多出现在阿拉伯国家。

### <a name="_Toc503261541"></a> 特殊文件名
<td width="51%">样本MD5</td><td width="48%">文件名</td>
<td width="51%">a4e6c15984a86f2a102ad67fa870a844</td><td width="48%">حمص تلبيسة قصف بالهاون.scr</td>
<td width="51%">3f00799368f029c38cea4a1a56389ab7</td><td width="48%">صفقة جيش الاسلام مع النظام المتضمنة تبادل 75 اسير للنظام من عدرا العمالية مقابل 15 معتقل لجيش الاسلام image.vbs</td>
<td width="51%">ea79617ba045e118ca26a0e39683700d</td><td width="48%">وثيقة رقم 1 العميد مناف طلاس يترأس هيئة الاركان العليا.vbs</td>

表19  PC样本PDB路径

上表是部分攻击样本的文件名，其中文件名“وثيقة رقم 1 العميد مناف طلاس يترأس هيئة الاركان العليا”是关于Manaf Tlass的信息，而Manaf Tlass是叙利亚前国防部长之子马纳夫・塔拉斯。文件名“حمص تلبيسة قصف بالهاون”直译是“炮击霍姆斯”，而霍姆斯是叙利亚的一个城市，通过上述文件名可以侧面看出攻击者针对地区为叙利亚。文件名“صفقة جيش الاسلام مع النظام المتضمنة تبادل 75 اسير للنظام من عدرا العمالية مقابل 15 معتقل لجيش الاسلام”是关于囚犯交换的。因此从这些文件名可以看出，攻击者在诱饵文档命名时也颇为讲究，此类文件名容易诱惑用户点击。

### <a name="_Toc503261542"></a> 文档作者

通过在攻击者后台[http://chatsecurelite.us.to/wp-content/uploads/2016/12/目录下发现文件1.docx](http://chatsecurelite.us.to/wp-content/uploads/2016/12/%E7%9B%AE%E5%BD%95%E4%B8%8B%E5%8F%91%E7%8E%B0%E6%96%87%E4%BB%B61.docx)文件，如下图。

[![](https://p3.ssl.qhimg.com/t010326df247b4f64c2.png)](https://p3.ssl.qhimg.com/t010326df247b4f64c2.png)

图33  1.docx存放位置

查看1.docx的属性发现该文件有作者信息Raddex。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01be10a4f324fcb188.png)

图34  1.docx属性

进一步关联分析发现，发现PC端样本SystemUI.exe(bdaaf37d1982a7221733c4cae17eccf8)也使用Raddex字符命名类，此样本C&amp;C为31.9.48.183。这与叙利亚哈马市新闻网发布的攻击者IP信息一致。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019e67c113d207e84a.png)

图35 叙利亚哈马市新闻网发布的消息

因此，推断Raddex属于攻击者组织的用户名。

### <a name="_Toc503261543"></a> 计算机名

[![](https://p4.ssl.qhimg.com/t01cae7ed9eaab2d9b5.png)](https://p4.ssl.qhimg.com/t01cae7ed9eaab2d9b5.png)

图36  IP 31.9.48.183信息<a name="_Toc476214395"></a>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c5b12549927365f5.png)

图37  IP 82.137.255.56信息

图36、37分别是IP 31.9.48.183、82.137.255.56的相关信息，这两个IP都是攻击者所持有。通过对这两个IP关联分析，并结合前面的pdb路径，可以清楚知道aboomar、abo moaaz属于攻击组织的计算机名。aboomar、abo moaaz此名字常出现在阿拉伯地区。



## 总结

通过对该组织相关TTPs（Tools、Techniques、Procedures）的研究分析，以及结合以往跟进或披露的 APT 组织或攻击行动，总结出以下几点：

### 移动端APT事件逐渐增多

以往披露的APT事件主要是针对Windows系统进行攻击，现今由于Android系统、APP的普及与发展，带动了Android手机等智能终端用户量的持续攀升，从而导致黑客组织的攻击目标也逐渐转向移动端。从我们捕获的样本也可以知道，攻击者显示从Windows平台逐渐过度到Android平台，并且在近期攻击者主要使用Android样本进行攻击，且更新速率很快，从而变相说明该组织后期主要会基于Android系统进行攻击。

因此，针对移动端的APT攻击不容忽略。

### 攻击技术由浅入深。

技术分析显示，该组织初期使用的特种木马技术并不复杂，主要使用开源的njRAT。但后期版本中，攻击者开始使用定制RAT，此种RAT需要通过层层释放执行恶意功能，于此同时，攻击者也开始使用VBS、JS脚本、Android RAT进行全方位攻击。综合来看，该组织的攻击周期较长攻击目标之明确，并且攻击过程中使用了大量资源，都表明这不是一个人或一般组织能承受的攻击成本。

因此该组织行动背后组织应该不是普通的民间黑客组织，很有可能是具有高度组织化的、专业化的黑客组织。

### 攻击组织极可能来自阿拉伯国家。

通过前面分析我们知道PDB路径有“Th3Pro”、“aboomar”等字符串，文档作者Raddex，IP信息获取的“aboomar”、“abo moaaz”计算机名，这些名字（“aboomar”、“abo moaaz”）常常出现在阿拉伯地区。并且通过部分样本中使用的字符串及文件名（如“حمص تلبيسة قصف بالهاون”）可以知道攻击者熟悉阿拉伯语。

因此，综合来看该攻击行动极可能来自阿拉伯国家。<a name="_Toc476214396"></a>



## 附录A：样本MD5
<td width="49%">PC端样本MD5</td><td width="50%">移动端样本MD5</td>
<td width="49%">dc09543850d109fbb78f7c91badcda0d</td><td width="50%">090ba0eef20b8fdcefd619ddc634b440</td>
<td width="49%">571afc1fe6ec2deef5099435c3b112f7</td><td width="50%">21cae0f8b41d5094c88858135a2bafc6</td>
<td width="49%">d84a553f9f272c8e2e6db525fa4f9977</td><td width="50%">3b8050b44700dec5cc7b2875549a3460</td>
<td width="49%">29e33220e37afd6c3a22543f2dad4486</td><td width="50%">405d28c207096120b92bf8338d2ed9f6</td>
<td width="49%">d38bd978afca411e8e4fc10861485834</td><td width="50%">5fe4361fbe0f96f521b7ad08cf4fa5c2</td>
<td width="49%">d774a45b9f865f2d3d045ead7d27d871</td><td width="50%">604035f7470a0de7b6169b218b30fe1e</td>
<td width="49%">ad9c09bb6b22cb970706b5e3ffdf7621</td><td width="50%">62d8a29ecae6bea296b2aeefa69814f7</td>
<td width="49%">55971412602747a98c3477b289ef2c9a</td><td width="50%">74f9549afd7ba8e25f0dfbd735ed2130</td>
<td width="49%">b7d1e20f814e9300a5b104f0a6f0c6f6</td><td width="50%">9f6a99a4bfddbf1efc72264252f691ef</td>
<td width="49%">3f00799368f029c38cea4a1a56389ab7</td><td width="50%">a5a7ad37a06d0beac8da7ae1663db001</td>
<td width="49%">a4e6c15984a86f2a102ad67fa870a844</td><td width="50%">cb9759054dee65621ecf9c91018e4322</td>
<td width="49%">b5d9b03020fff512934e2001805f9c0b</td><td width="50%">ccf4a5d0f441c0e55fd871ebd229ccd7</td>
<td width="49%">b89e0d5a7329ee61fba7279dca14edf3</td><td width="50%">cf507aa156fe856e74f22b80e83055fd</td>
<td width="49%">bdaaf37d1982a7221733c4cae17eccf8</td><td width="50%">de83e22c323a3382fde98e4b7e6ddc3e</td>
<td width="49%">11b61b531a7bbc7668d7d346e4a17d5e</td><td width="50%">def07be7cd3584bd565b808f9d9103b5</td>
<td width="49%">d06f0950f2f3a0b069fa9cedfcbc7d43</td><td width="50%">e022aa83908625ca356782480881dd8d</td>
<td width="49%">871e4e5036c7909d6fd9f23285ff39b5</td><td width="50%">e53e4db569e2886b960f8f5a7d9069ff</td>
<td width="49%">6cde6e81f8bc05339d2dd50feadbc31f</td><td width="50%">39dd3d9e2a276d4d341ef01b21964d05</td>
<td width="49%">612cb35dbab698b11a63a8c93df1cf6b</td><td width="50%">59cc514938fa30b14f7d1d46f5fb493a</td>
<td width="49%">5232f720be177310c72ac004ed84f026</td><td width="50%">819cac2e71e2ed346a9b5e48077e786c</td>
<td width="49%">99977cb5eafe40b9672c75010ae74398</td><td width="50%">8ab2a456d8c0cdd5f541c53f925158f8</td>
<td width="49%">1403bbaa9e0fcb5c9d9e8efeca95efa3</td><td width="50%">d94244732a762d9414587cce8d9836f8</td>
<td width="49%">eb8cce73a5f983b94d5bf6a389ea09f0</td><td width="50%">b4f1cd4bbf1be5c4ed4d84de941f4cc1</td>
<td width="49%">0d5a49d9be130d238c0a9ce2bf3115a5</td><td width="50%">45c45e1afdd6232b08041576da590f12</td>
<td width="49%">e3f9694b264bdb667bfefb09c209a118</td><td width="50%">e4197ea4e6fa6c1b7b053805cfa48b69</td>
<td width="49%">93ca8ea43d7af65875973adb2fcc80a3</td><td width="50%">b010230cd1846226aae1b3b9b4a16ac7</td>
<td width="49%">382788bb234b75a35b80ac69cb7ba306</td><td width="50%">9dbda4346efae4daceac1e3ce6c23994</td>
<td width="49%">69a35e8c9cfe20edeeed96241d66dac7</td><td width="50%">e448e46dd39b9398467e382128e538e4</td>
<td width="49%">fdedf688e4ac5fb4df059052883cd90b</td><td width="50%">7eacdf48061a5aa075e81e69e151a767</td>
<td width="49%">bf1dd2bd62e34c467ac1bb3363c2a98b</td><td width="50%">d9b1e46a08cc5a5d4844193fffec4489</td>
<td width="49%">4ef5bd5f1cc6758a765b4ef6a270e527</td><td width="50%">7bd1e63ac84e4cf511e54ac85b7af6fe</td>
<td width="49%">cc0db787872eac747c75d7bea6e75bf1</td><td width="50%">d6aa10393135f4a77191533d3422403b</td>
<td width="49%">ea79617ba045e118ca26a0e39683700d</td><td width="50%"></td>
<td width="49%">c9adaec7775c19c06b91b3d45ff4687e</td><td width="50%"></td>
<td width="49%">73dc99693709a12881681659292103e7</td><td width="50%"></td>
<td width="49%">9231882b47475e327adc23f3b1f716f0</td><td width="50%"></td>
<td width="49%">17cc1c907ac19139a98fab34d78f7323</td><td width="50%"></td>
<td width="49%">6b2136a9ae899588769e9c0513be410e</td><td width="50%"></td>
<td width="49%">b29f50770355a8a165dff87f4aede6f0</td><td width="50%"></td>
<td width="49%">af73ca52a77402a178ee3594020e88c1</td><td width="50%"></td>
<td width="49%">1b09ce9b782e56131103aad73016e329</td><td width="50%"></td>
<td width="49%">cf8ffe7f560b4d19aaaf93439101ef16</td><td width="50%"></td>
<td width="49%">558a6afb2353bd25da76d17b0f80193b</td><td width="50%"></td>
<td width="49%">75e8aeb6314ced58a0c40e0b88a969a6</td><td width="50%"></td>
<td width="49%">f519e5b04bd9cbf76875c0d8dbbbc8b4</td><td width="50%"></td>
<td width="49%">8848631aeaf33a166c9e623d430cb1bf</td><td width="50%"></td>
<td width="49%">f739170918c50bea803b313d5cb0f470</td><td width="50%"></td>
<td width="49%">ea73fa4f83a40cbb11ee04106414fe7a</td><td width="50%"></td>
<td width="49%">2ea0298b94b8fadb49ed35aece28cb14</td><td width="50%"></td>
<td width="49%">6fcadad1af1894f6678a4f46c2e168c2</td><td width="50%"></td>
<td width="49%">32ea9d96b6278f8040bf0bb4bbfa4418</td><td width="50%"></td>
<td width="49%">b134dc4c1f69dd734417ac5125995bdb</td><td width="50%"></td>



## 附录B：C&amp;C列表
<td width="198">82.137.255.56</td>
<td width="198">82.137.255.57</td>
<td width="198">31.9.48.183</td>
<td width="198">82.137.249.204</td>
<td width="198">chatsecurelite.us.to</td>
<td width="198">telgram.strangled.net</td>
<td width="198">basharalassad1sea.noip.me</td>
<td width="198">bbbb4.noip.me</td>
<td width="198">android.nard.ca</td>


