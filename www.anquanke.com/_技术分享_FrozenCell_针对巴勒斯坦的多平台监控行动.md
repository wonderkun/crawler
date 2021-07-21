> 原文链接: https://www.anquanke.com//post/id/86998 


# 【技术分享】FrozenCell：针对巴勒斯坦的多平台监控行动


                                阅读量   
                                **93146**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：lookout.com
                                <br>原文地址：[https://blog.lookout.com/frozencell-mobile-threat](https://blog.lookout.com/frozencell-mobile-threat)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01d81960d7d85110d1.png)](https://p0.ssl.qhimg.com/t01d81960d7d85110d1.png)

译者：[Janus情报局](http://bobao.360.cn/member/contribute?uid=2954465307)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**简介**

****

Lookout安全研究人员近期发现一款新型移动监控软件家族，FrozenCell。这一威胁很可能针对巴勒斯坦各政府机构、安全部门、巴勒斯坦学生以及与法塔赫政党有关的人员。

[![](https://p3.ssl.qhimg.com/t01f48830ccdbaa5982.png)](https://p3.ssl.qhimg.com/t01f48830ccdbaa5982.png)

图1  FrozenCell经常伪装成知名的社交媒体和聊天应用，以及一款在2016年普通中学考试中巴勒斯坦或约旦学生使用的应用

今年3月，360追日团队发现了[双尾蝎/APT-C-23](http://zhuiri.360.cn/report/index.php/2017/03/09/twotailedscorpion/)APT攻击，这个威胁利用受控的移动设备和桌面来监控受害者。本文中提到的FrozenCell正是双尾蝎多平台攻击的移动组件。而该APT攻击的桌面组件，在此之前[已被Palo Alto Network发现](https://researchcenter.paloaltonetworks.com/2017/04/unit42-targeted-attacks-middle-east-using-kasperagent-micropsia/)，并命名为KasperAgent和Micropsia。在调查这一攻击的过程中，我们对来自24个受控Android设备的561MB泄露数据进行了分析。在分析的过程中，我们发现，每天都会有新的数据出现，这表明，该活动仍在活跃期，我们也会对该攻击持续关注。

这个威胁，也是攻击者把移动设备作为主要攻击载体加入到监视活动的另外一个证据。政府机构和企业应该把这一威胁看做间谍行为的例子，因为现在在移动设备在工作场所随处可见。攻击者敏锐地意识到他们可以从这些设备中获取信息，并使用多阶段(钓鱼+可执行文件)，多平台(安卓+桌面)攻击来完成他们的间谍活动。

<br>

**它都做了什么？**

****

FrozenCell经常伪装成Facebook、hatsApp、Messenger、LINE和LoveChat等聊天应用的更新，诱使用户下载。此外，我们还在针对特定中东人的应用程序中发现了它的踪迹。例如文章开始所提到的，FrozenCell背后的攻击者使用了一款名为Tawjihi 2016的恶搞应用，这款应用是约旦或巴勒斯坦学生在普通中学考试中使用的应用程序。

一旦安装在设备上，FrozenCell能够进行如下操作：

**·  **通话录音

**·  **获取通用电话元数据(例如，基站定位，移动国家码和移动网络码)

**·  **定位设备

**·  **提取短信

**·  **获取受害者账户信息

**·  **泄露设备中的图片

**·  **下载中并安装其他应用程序

**·  **搜索并泄露pdf,doc,docx,ppt,pptx,xls及xlsx等类型文件

**· ** 获取通讯录

下图显示了从一个配置错误的C&amp;C服务器（超过37台服务器）上获取的数据类型。 当然，这些只是此威胁获取的数据的一小部分。



[![](https://p1.ssl.qhimg.com/t01c13c11f7da4e8454.png)](https://p1.ssl.qhimg.com/t01c13c11f7da4e8454.png)

图2  泄露数据类型

从这些受控设备中提取的内容有一些值得注意的文件，包括护照照片，通话录音，其他图片，以及存有484份个人数据的PDF文件。PDF中列出了这些人的出生日期、性别、护照号码和姓名。

<br>

**潜在目标**<br>



FrozenCell背后的攻击者使用了一个在线服务，利用附近的基站定位移动设备，追踪目标。数据表明受感染设备的明显集中于加沙到巴勒斯坦的区域。

[![](https://p1.ssl.qhimg.com/t017ba372d6317d0e6f.png)](https://p1.ssl.qhimg.com/t017ba372d6317d0e6f.png)

图3  FrozenCell的早期样本使用在线服务来存储受感染设备的地理位置信息。经过遥感技术分析，可以看到，受感染的设备主要位于巴基斯坦的加沙地带。目前还没有办法确定这些是测试设备还是受害者的设备。

我们也可以将FrozenCell的Android基础网络对象与许多桌面样本进行关联，这些样本是更大的多平台攻击的一部分。从种种迹象看来，攻击者通过仿冒巴基斯坦安全局，内政部民防总局，巴勒斯坦民族解放阵线第七次法庭会议(2016年举办)相关进行网络钓鱼活动，传播恶意可执行文件。而这些文件的标题和内容又表明，这些活动的目标群体是与政府机构和法塔赫政党相关的工作人员。

一些与这些恶意样本有关的恶意文件标题：

**·  **Council_of_ministres_decision

**·  **Minutes of the Geneva Meeting on Troops (محضر اجتماع جنيف الخاص بقوات ا_من)

**·  **Summary of today's meetings.doc.exe (ملخص إجتماعات اليوم)

**·  **The most important points of meeting the memory of the late President Abu Omar may Allah have mercy on him – Paper No. 1 (أهم نقاط إجتماع ذكرى الرئيس الراحل أبوعمار رحمه الله – ورقة رقم)

**·  **Fadi Alsalamin scandal with an Israeli officer – exclusive – watched before the deletion – Fadi Elsalameen (فضيحة فادي السلامين مع ضابط إسرائيلي- حصري-شاهد وقبل الحذف-Fadi Elsalameen)

**·  **The details of the assassination of President Arafat_06-12-2016_docx

**·  **Quds.rar

部分PDF内容截图：

[![](https://p0.ssl.qhimg.com/t010061de8775ca9e13.png)](https://p0.ssl.qhimg.com/t010061de8775ca9e13.png)

图4  PDF内容截图

[![](https://p0.ssl.qhimg.com/t01fae87834e0c032a4.png)](https://p0.ssl.qhimg.com/t01fae87834e0c032a4.png)



图5  PDF内容截图

[![](https://p3.ssl.qhimg.com/t01610206e7b2bd02e2.png)](https://p3.ssl.qhimg.com/t01610206e7b2bd02e2.png)

图6  PDF内容截图

这些可执行文件大多与使用Bit.ly创建的各种短域名相关联。在分析与这些短域名相关的流量后，我们确定每个短域名都与mail.mosa.pna.ps中引用的路径相关。MOSA是巴勒斯坦社会发展理事会，根据该部门的公开资料显示，其任务是实现巴勒斯坦家庭的全面发展、社会保障和经济增长。



**基础网络对象**<br>

在撰写本文时，以下域名已由该家族使用或处于活跃期。截止目前，该攻击团伙已多次改变其基础网络对象，我们预计以下列表还会扩增。

**·  **cecilia-gilbert[.]com    

**·  **gooogel[.]org

**·  **mary-crawley[.]com    

**·  **mydriveweb[.]com

**·  **rose-sturat[.]info    

**·  **kalisi[.]xyz

**·  **debra-morgan[.]com    

**·  **arnani[.]info

**·  **acount-manager[.]info    

**·  **gooogel-drive[.]com

**·  **mediauploader[.]me    

**·  **acount-manager[.]net

**·  **upload404[.]club    

**·  **upload999[.]info

**·  **al-amalhumandevelopment[.]com

**·  **margaery[.]co

**·  **upload202[.]com    

**·  **go-mail-accounts[.]com

**·  **upload101[.]net    

**·  **sybil-parks[.]info

**·  **davos-seaworth[.]info    

**·  **upload999[.]org

**·  **acount-manager[.]com    

**·  **lila-tournai[.]com

**·  **account-manager[.]org    

**·  **mediauploader[.]info

**·  **kalisi[.]org    

**·  **aryastark[.]info

**·  **mavis-dracula[.]com    

**·  **kalisi[.]info

**·  **google-support-team[.]com    

**·  **9oo91e[.]com

**·  **useraccount[.]website    

**·  **accounts-fb[.]com

**·  **akashipro[.]com    

**·  **feteh-asefa[.]com

**·  **lagertha-lothbrok[.]info



**OpSec失误以及加密**



在查看这些基础网络对象时，我们发现其中一个域名启动了目录索引。这个小的操作安全性的失误，使我们能够看到很多设备中泄露的内容。而镜像表明，它可能是一个定期清理的临时服务器。我们从这个域名获取了超过561M的泄露数据，经过查看，发现这些数据都经过7z压缩并进行了加密。

压缩文件的密码在客户端生成，大多数情况下每个设备的密钥都是唯一的。密钥的关键信息由设备Android ID的MD5，设备制造商和设备模型的MD5组成，并由下划线进行分隔。表示方式如下图所示：

[![](https://p5.ssl.qhimg.com/t01745a554b75ea75ec.png)](https://p5.ssl.qhimg.com/t01745a554b75ea75ec.png)

图7  密钥关键信息格式

结合我们在C2基础网络对象索引目录的分析，我们可以轻松反推出每个设备密码的产生过程，进而可以将被感染设备中泄露的内容解压。

[![](https://p2.ssl.qhimg.com/t01bb721df1817765eb.png)](https://p2.ssl.qhimg.com/t01bb721df1817765eb.png)

图8  索引目录

尽管泄露的内容已被加密，但是用于生成每个设备密码的信息在顶层目录是可见的。从目录列表获取此信息，可对所有内容进行解密操作。

FrozenCell是一个非常成功的多平台监控活动的一部分。攻击者对于如何利用多平台进行监控非常得心应手，擅长利用设备和一些服务进行定位。政府机构和企业应该从各个角度——云服务、移动设备、笔记本电脑，来建立全面的安全防护策略。



**IoCs(移动端)**

[![](https://p4.ssl.qhimg.com/t01cf84c286208289ed.png)](https://p4.ssl.qhimg.com/t01cf84c286208289ed.png)



**IoCs(PC端)**

[![](https://p4.ssl.qhimg.com/t01fa405009007a6fc1.png)](https://p4.ssl.qhimg.com/t01fa405009007a6fc1.png)
