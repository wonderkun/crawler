> 原文链接: https://www.anquanke.com//post/id/205079 


# “BankerBR” 家族银行木马


                                阅读量   
                                **181830**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01dfcc483b5a62a4a3.jpg)](https://p2.ssl.qhimg.com/t01dfcc483b5a62a4a3.jpg)



**背景：** IBMX-Force研究人员发现新的Android木马Banker.BR家族，其利用屏幕覆盖攻击针对使用西班牙语或葡萄牙语（包括西班牙、葡萄牙、巴西和拉丁美洲其他地区）的银行客户，企图窃取用户凭证并盗取其账户。研究发现，该恶意软件的早期版本仅具有基本的SMS窃取功能，但是Banker.BR更为精细，具有覆盖攻击的功能并且有全新的代码，不依赖于先前泄漏的代码或现有的移动恶意软件。

近期，恒安嘉新暗影安全实验室在日常监控中，发现一批“Banker.BR”家族银行木马新变种，这些木马程序主要针对桑坦德、玻利维亚、法希尔、西班牙等13家银行客户端实施网络钓鱼攻击，绕过银行双因子验证。程序运行后，通过网络钓鱼手段窃取用户银行相关的账号和密码，再上传用户手机短信验证码，盗取用户的资金。



## 1. 样本概况

**程序名称：** 2020NovoeBan

**程序包名：** pt.bn2020.ptz

**样本签名** ：CN=AnywhereSoftware,O=Anywhere Software,C=US

**证书MD5** ：0D304D8EB39B8494962603CDE0CD9052

[![](https://p2.ssl.qhimg.com/t011c60052fb44e31a2.png)](https://p2.ssl.qhimg.com/t011c60052fb44e31a2.png)

图1 程序安装图标



## 2. 样本分析

该样本运行后，会采用界面劫持，网络钓鱼的手段骗取用户的账号和密码，然后监听手机短信，屏蔽短信广播，使用户接收不到短信提醒，最后，上传用户短信内容、银行账户，密码等个人隐私到远程服务器，还有程序会通过后台服务、电源锁等保证进程不被系统杀掉；通过对手机静音、屏蔽短信广播等方式防止被用户察觉；通过设置定时任务发送心跳包监控程序运行状态，达到持久化监测用户手机。

**行为示意图如下：**

[![](https://p5.ssl.qhimg.com/t019ae9abd6acc0e2b4.png)](https://p5.ssl.qhimg.com/t019ae9abd6acc0e2b4.png)

图2 行为示意图

### **2.1恶意行为持久化**

程序通过后台服务、电源锁等保证进程不被系统杀掉；通过对手机静音、屏蔽短信广播等方式防止被用户察觉；通过设置定时任务发送心跳包监控程序运行状态，达到持久化利用用户手机的目的。

[![](https://p0.ssl.qhimg.com/dm/1024_459_/t01a9d67dbaea7d890b.png)](https://p0.ssl.qhimg.com/dm/1024_459_/t01a9d67dbaea7d890b.png)

图3 恶意行为持久化

**设置电源锁**

程序通过设置电源锁，使程序在CPU中能持续运行。

[![](https://p2.ssl.qhimg.com/dm/1024_520_/t01117003f96b2bc8f4.png)](https://p2.ssl.qhimg.com/dm/1024_520_/t01117003f96b2bc8f4.png)

图4 设置电源锁

**定时发送心跳包**

程序设置了定时任务，任务内容为每分钟访问指定链接，该链接参数中带有用户设备的ID，可用于识别。

[![](https://p5.ssl.qhimg.com/dm/1024_188_/t01e7e33cf1c210386f.png)](https://p5.ssl.qhimg.com/dm/1024_188_/t01e7e33cf1c210386f.png)

图5 设置定时任务

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_368_/t014d94d03bd095ca00.png)

图6 上传用户设备ID

心跳包截图：

[![](https://p0.ssl.qhimg.com/t01f88e61b9d05b90e5.png)](https://p0.ssl.qhimg.com/t01f88e61b9d05b90e5.png)

图7 心跳包

### **2.2窃取用户短信**

程序注册监听器，监听手机短信，当来短信后屏蔽短信广播，使用户接收不到短信提醒，同时上传短信内容到服务器。

[![](https://p5.ssl.qhimg.com/dm/1024_463_/t016c80893ecda82e8e.png)](https://p5.ssl.qhimg.com/dm/1024_463_/t016c80893ecda82e8e.png)

图8 获取并上传用户短信息

读取最新收到的短信：

[![](https://p2.ssl.qhimg.com/dm/1024_211_/t018bfb586e1fe34a2d.png)](https://p2.ssl.qhimg.com/dm/1024_211_/t018bfb586e1fe34a2d.png)

[![](https://p0.ssl.qhimg.com/dm/1024_455_/t0113d95df22acb167a.png)](https://p0.ssl.qhimg.com/dm/1024_455_/t0113d95df22acb167a.png)

图9 接收用户短信

上传短信内容到服务器：

url：http://186.***.91.100/controls/nb/sms.php?apelido=

[![](https://p3.ssl.qhimg.com/dm/1024_194_/t01d216ff152ec2241a.png)](https://p3.ssl.qhimg.com/dm/1024_194_/t01d216ff152ec2241a.png)

图10 上传接收的短信息

### **2.3获取钓鱼网页**

程序通过访问硬编码url的方式，获取钓鱼网页地址。通过这种方式，控制者可以随时更换钓鱼页面：

http://186.***.91.100/extras/nb_link_lyly.txt

[![](https://p0.ssl.qhimg.com/dm/1024_427_/t01658ce7b3d1cdd133.png)](https://p0.ssl.qhimg.com/dm/1024_427_/t01658ce7b3d1cdd133.png)

图11 获取钓鱼页面

### **2.4启动钓鱼页面**

程序加载从服务器获取的钓鱼链接，启动网络钓鱼，程序可以从钓鱼页面获取用户账号及密码等信息。

[![](https://p2.ssl.qhimg.com/dm/1024_181_/t01f8750647d9d47b2f.png)](https://p2.ssl.qhimg.com/dm/1024_181_/t01f8750647d9d47b2f.png)

图12 加载钓鱼页面



## 3. 溯源分析

### **3.1服务器分析**

通过样本分析，我们得到了一个IP地址186.***.91.100，归属地位于巴西，通过反查IP域名，获取到19个曾经绑定过的子域名，同时发现多个后台地址，从后台界面中可以看到多个金融机构的标签，表明攻击者对接收到的数据进行了相应归类。

**子域名：**

[![](https://p5.ssl.qhimg.com/t0110be91dcad831f3b.png)](https://p5.ssl.qhimg.com/t0110be91dcad831f3b.png)

**后台地址**

**http://186.***.91.100/index.php**

**http://186.***.91.101/index.php**

**http://ns1.glad***ijoux.com.br/**

[![](https://p3.ssl.qhimg.com/dm/1024_599_/t018d7c1971986e854c.png)](https://p3.ssl.qhimg.com/dm/1024_599_/t018d7c1971986e854c.png)

图13 服务器后台

后台界面各金融机构的标签：

[![](https://p0.ssl.qhimg.com/dm/1024_55_/t011a9f075d83d13e5c.png)](https://p0.ssl.qhimg.com/dm/1024_55_/t011a9f075d83d13e5c.png)

**图14 服务器后台**

**相关的服务器信息列表**

[![](https://p5.ssl.qhimg.com/t013f157d34126b09e1.png)](https://p5.ssl.qhimg.com/t013f157d34126b09e1.png)

### **3.2传播链接分析**

通过恒安嘉新 App全景态势与案件情报溯源挖掘平台分析，发现一条传播链接和疑似后台服务器日志，通过时间点分析，发现攻击者可能来自巴西。

传播链接：https://sis-ptc***stro.com/app/BPI_Security.apk

查看域名信息，注册时间为2020年4月14日：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0196def047b2dfc663.png)

图15 传播地址域名信息查询

查看该地址的登录日志发现，第一条访问时间为2020年4月14日，由此推测第一条访问ip可能来自攻击者：

[![](https://p2.ssl.qhimg.com/t015b11d42bc893cbb6.png)](https://p2.ssl.qhimg.com/t015b11d42bc893cbb6.png)

图16 登录日志信息

[![](https://p2.ssl.qhimg.com/t012acb31398c2664fd.png)](https://p2.ssl.qhimg.com/t012acb31398c2664fd.png)

图17 IP归属地

### **3.3同源性分析**

在恒安嘉新 App全景态势与案件情报溯源挖掘平台上，通过应用名称、包名等特征关联搜索相关样本，发现平台上存在一批与当前样本同源的样本，总体上可以分为两类，一类与本文阐述的行为相同，另一类样本对功能进行了改进。该类恶意程序代码结构、包名及其类似，极有可能是同一批人在持续开发传播。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e5d6eeae7a975366.png)

图18 同源样本信息

**新增的功能**

（1）增加了无障碍服务权限，诱导用户授予该权限，程序可以监控手机界面。

[![](https://p5.ssl.qhimg.com/t0147dba7c8f3623550.png)](https://p5.ssl.qhimg.com/t0147dba7c8f3623550.png)

图19 请求无障碍服务

（2）将从网络获取指定的钓鱼页面改进为自带钓鱼界面，根据不同的应用，启动相对应的钓鱼界面。

根据不同的应用，展示对应的仿冒界面：

[![](https://p4.ssl.qhimg.com/t017e5cd5c529e5d763.png)](https://p4.ssl.qhimg.com/t017e5cd5c529e5d763.png)

图20钓鱼页面列表

（3）界面劫持验证

以BBVA应用为例进行测试，恶意程序能够成功覆盖原APP界面，效果如下所示：

[![](https://p2.ssl.qhimg.com/t01e1adecd20f7118e2.png)](https://p2.ssl.qhimg.com/t01e1adecd20f7118e2.png)

图21 界面劫持



## 4.“BankerBR”家族银行木马

**总结**

从这类样本的行为特征来看，主要针对桑坦德、玻利维亚、法希尔、西班牙等13家银行客户端实施网络钓鱼攻击，绕过银行双因子验证。通过网络钓鱼手段窃取用户银行相关的账号和密码，再上传用户手机短信验证码，最终目的是盗取用户的资金。是一种具有针对性钓鱼攻击行为，后续暗影实验室会持续关注此类样本的新进展

在此，暗影实验室提醒大家，不轻易相信陌生人，不轻易点击陌生人发送的链接，不轻易下载不安全应用。
1. 安全从自身做起，建议用户在下载软件时，到正规的应用商店进行下载正版软件，避免从论坛等下载软件，可以有效的减少该类病毒的侵害；
1. 很多用户受骗正是因为钓鱼短信的发件人显示为10086、95588等正常号码而放松安全警惕导致中招，运营商需要加强对伪基站的监控打击力度，减少遭受伪基站干扰的几率；
1. 各大银行、各支付平台需要加强对各自支付转账渠道的监管，完善对用户资金转移等敏感操作的风控机制，防止被不法分子利用窃取用户网银财产;
1. 警惕各种借贷软件的套路，不要轻易使用借贷类App。