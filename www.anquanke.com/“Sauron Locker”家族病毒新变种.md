> 原文链接: https://www.anquanke.com//post/id/204763 


# “Sauron Locker”家族病毒新变种


                                阅读量   
                                **239573**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01631a28ce8bc4e913.jpg)](https://p1.ssl.qhimg.com/t01631a28ce8bc4e913.jpg)



**背景：**《地母经》里说：“鼠耗出头年，高低多偏颇。”庚子年，似乎都伴随着重大灾难或历史转折，新冠肺炎的出现，使人们在这一年的开头感到了一丝沉重，一些人总会挺身而出，悬壶济世，成为最美逆行者；一些人总会趁着乱世，利用人性的弱点，扰乱社会秩序，从而达到不法的目的。

自2020年初以来，恒安嘉新暗影安全实验室持续针对“新冠肺炎”相关的病毒样本进行监测，近期，我们发现了一款名为“Covid19”的病毒软件，其代码结构与“SauronLocker”家族病毒及其相似，我们怀疑是该病毒家族的新变种，用户设备中毒后，导致用户手机的通讯录和外存储文件被加密，要求用户支付比特币解密，另外，该版本采用AES的加密算法，而加解密的密钥是从远程服务器动态获取，增加了破解勒索软件加密算法的难度。



## 1.基本信息

**样本名称：**Covid19

**样本MD5：**362DAC3F2838D2BF60C5C54CC6D34C80

**样本包名：**com.ins.fortnite

**签名信息：**CN=KhumarAjit, OU=App Dev, O=App Dev, L=Bangladesh, ST=Balgadesh, C=ID

[![](https://p4.ssl.qhimg.com/t01994d4eae975893c8.png)](https://p4.ssl.qhimg.com/t01994d4eae975893c8.png)

图1“Covid19”安装图标



## 2.运行原理

该程序是一款名为“Covid19”的勒索软件，程序运行后将自身界面置顶，妨碍用户正常退出。首先，获取设备的基本信息（UID）作为参数上传到远程服务器，用于识别设备并下发加密密钥，然后，加密用户手机的外部存储文件，加密文件后缀为“.encrypted”，同时将用户通讯录文件利用AES算法加密后，再通过BASE64编码进行存储，并删除原通讯录信息，最后，弹出勒索界面信息，要求用户需要支付0.028比特币。

用户点击“CHECKPAYMENT ANDUNBLOCK”按钮时，程序访问服务器判断是否付款和获取解密密钥，当返回信息为“true”，密钥正确时会自动进行解密并提示用户重启手机解除锁定。

**病毒运行流程示意图：**

[![](https://p1.ssl.qhimg.com/t01d5acfc56c6a9d590.png)](https://p1.ssl.qhimg.com/t01d5acfc56c6a9d590.png)

图2 病毒运行流程示意图



## 3.代码分析

该软件的代码框架相对简洁，主要由开机启动广播、恶意服务、勒索界面、加密解密四部分组成，其中加密解密密钥是从远程服务器远程获取，相对比较复杂。

[![](https://p3.ssl.qhimg.com/t0155db4e2d528197d1.png)](https://p3.ssl.qhimg.com/t0155db4e2d528197d1.png)

图3 代码框架

**（1）实施勒索**

程序运行后将自身界面置顶，注册开机广播，实现开机自启，妨碍用户正常退出，获取设备的基本信息(如：UID)作为参数上传到远程服务器，用于设备识别并下发加密密钥，之后程序会对用户外部存储的文件以及通讯录文件利用AES算法进行加密。

自身界面置顶:

[![](https://p2.ssl.qhimg.com/t01d242fcc65b42eca1.png)](https://p2.ssl.qhimg.com/t01d242fcc65b42eca1.png)

图4 窗口置顶

开机自启:

[![](https://p5.ssl.qhimg.com/t014d1120dbeeef628b.png)](https://p5.ssl.qhimg.com/t014d1120dbeeef628b.png)

图5 开机自启

生成设备唯一识别码:

[![](https://p0.ssl.qhimg.com/t01d051d3466b3996cc.png)](https://p0.ssl.qhimg.com/t01d051d3466b3996cc.png)

图6 生成设备UID

加密通讯录和外部存储文件：

url：http://ex***pooo.xyz/wp-content/gateway/attach.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01084e3157473893ba.png)

图7 加密通讯录和文件

获取勒索信息进行展示：

url：http://ex***pooo.xyz/wp-content/gateway/settings.php

[![](https://p1.ssl.qhimg.com/dm/1024_389_/t01cb578d90ac48131b.png)](https://p1.ssl.qhimg.com/dm/1024_389_/t01cb578d90ac48131b.png)

[![](https://p2.ssl.qhimg.com/t0150f2f21eab4ab3da.png)](https://p2.ssl.qhimg.com/t0150f2f21eab4ab3da.png)

图8 获取勒索信息

[![](https://p2.ssl.qhimg.com/t0189d455341cca9327.png)](https://p2.ssl.qhimg.com/t0189d455341cca9327.png)

图9 展示勒索信息

**（2）加解密算法**

通过代码分析可知，加解密的密钥通过服务器下发，经过AES算法对通讯录和文件进行加密操作，由于AES算法属于对称加密算法，所以加解密的密钥相同，只要知道加密时的密钥就能进行解密，而加密的密钥可以在首次启动该软件时进行抓包获取到。

获取加密密钥:

[![](https://p3.ssl.qhimg.com/t0189fa79088ae85478.png)](https://p3.ssl.qhimg.com/t0189fa79088ae85478.png)

图10 获取加密密钥

将密钥转换成比特数组:

[![](https://p5.ssl.qhimg.com/t015a8b8bc3bd184169.png)](https://p5.ssl.qhimg.com/t015a8b8bc3bd184169.png)

图11 密钥转换

将转换后的比特数组作为KEY值，利用AES/CBC/PKCS5Padding算法类型进行加密:

[![](https://p5.ssl.qhimg.com/t011714a1b5f4e09638.png)](https://p5.ssl.qhimg.com/t011714a1b5f4e09638.png)

图12 AES算法

加密通讯录：

将通讯录利用AES算法加密后，再通过BASE64编码进行存储，并删除原信息:

[![](https://p4.ssl.qhimg.com/t0112212f7f7653d5a4.png)](https://p4.ssl.qhimg.com/t0112212f7f7653d5a4.png)

图13 加密通讯录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010d5e1cc1e1b2c3a3.png)

图14 通讯录加密前后对比

加密文件

将文件经过AES加密后，并在文件名后面添加“.encrypted”字符串，最后删除原文件

[![](https://p1.ssl.qhimg.com/t017a722c17a4b1573e.png)](https://p1.ssl.qhimg.com/t017a722c17a4b1573e.png)

[![](https://p0.ssl.qhimg.com/t01f7dcdcc901979c12.png)](https://p0.ssl.qhimg.com/t01f7dcdcc901979c12.png)

图15 文件加密前后对比

**（3）解除勒索**

当点击“CHECKPAYMENT ANDUNBLOCK”按钮时，程序访问服务器判断是否付款和获取解密密钥，当返回信息为“true”，密钥正确时会自动进行解密并提示用户重启手机解除锁定。

与后台确认是否付款和解除锁定:

url：http://ex***pooo.xyz/wp-content/gateway/check.php

[![](https://p0.ssl.qhimg.com/t01a8a281616ec81133.png)](https://p0.ssl.qhimg.com/t01a8a281616ec81133.png)

图16 与后台确认是否付款和解除锁定

[![](https://p4.ssl.qhimg.com/t01620a8c3bd556e29b.png)](https://p4.ssl.qhimg.com/t01620a8c3bd556e29b.png)

[![](https://p1.ssl.qhimg.com/t01bdbf3ddd504fe4cc.png)](https://p1.ssl.qhimg.com/t01bdbf3ddd504fe4cc.png)

图17 解析返回的信息

[![](https://p4.ssl.qhimg.com/t01054d16d4135e3ff9.png)](https://p4.ssl.qhimg.com/t01054d16d4135e3ff9.png)

图18 解除锁定的界面

**溯源分析**

**（1）域名溯源**

通过域名信息进行溯源，发现该域名注册日期为2020年3月，存有后台管理地址，服务器开启了列目录功能，可以看到部分文件，通过文件的编辑日期可以看出该作者早在2018年就开始进行该软件的制作，最后修改日期为2020年4月22日，可以看出是针对目前的热点新闻进行了针对性修改，更容易欺骗用户。

Whois信息：

[![](https://p2.ssl.qhimg.com/t017b9b00dbae3edbba.png)](https://p2.ssl.qhimg.com/t017b9b00dbae3edbba.png)

图19 域名备案信息

后台地址：

url：http://ex***pooo.xyz/wp-content/admin/login.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01879fa0566d0b4341.png)

图20 后台地址

服务器目录结构：

[![](https://p2.ssl.qhimg.com/t0115911d5aa5ca3ff7.png)](https://p2.ssl.qhimg.com/t0115911d5aa5ca3ff7.png)

图21 服务器文件目录

用于勒索的主要文件：

[![](https://p4.ssl.qhimg.com/t01dd3def55d83ddf7b.png)](https://p4.ssl.qhimg.com/t01dd3def55d83ddf7b.png)

图22 用于勒索的文件

域名对应IP地址为104.18.47.130 美国。

**（2）数字钱包溯源**

要求支付比特币的钱包地址：3DEdThknF1sRr57djd47ii2uKa1SWDG8c5

[![](https://p3.ssl.qhimg.com/dm/1024_402_/t01d3757375cb6ca434.png)](https://p3.ssl.qhimg.com/dm/1024_402_/t01d3757375cb6ca434.png)

图23 比特币交易信息

**（3）同源性分析**

2019年8月，首次出现“SauronLocker”家族勒索软件，根据同源性分析，我们本次发现的样本在界面、包名、代码结构、逻辑功能等方面，都与“SauronLocker”家族病毒极度相似，我们归属于同一家族病毒。

界面对比：

[![](https://p3.ssl.qhimg.com/t01eccdc078ed760dcf.png)](https://p3.ssl.qhimg.com/t01eccdc078ed760dcf.png)

图24 界面对比

代码结构对比：

[![](https://p0.ssl.qhimg.com/t017d33ff0d5d08cae3.png)](https://p0.ssl.qhimg.com/t017d33ff0d5d08cae3.png)

图25 文件对比

签名对比，发现本次软件的作者使用了带有孟加拉国命名的签名信息：

[![](https://p5.ssl.qhimg.com/dm/1024_512_/t0144184f2e65bf2d18.png)](https://p5.ssl.qhimg.com/dm/1024_512_/t0144184f2e65bf2d18.png)

图26 样本签名信息



## 5.总结

此类勒索软件具有代码结构相似，二次开发容易的特点，利用对文件和通讯录加密的方式进行勒索，由于密钥采用远程下发的方式，破解难度大，最终迫使用户交纳赎金，危害极大，该软件源代码已经泄露，使得二次开发和代码复用变得极其容易，对用户的威胁将会更大。

在此，暗影实验室提醒大家，不轻易相信陌生人，不轻易点击陌生人发送的链接，不轻易下载不安全应用。
1. 安全从自身做起，建议用户在下载软件时，到正规的应用商店进行下载正版软件，避免从论坛等下载软件，可以有效的减少该类病毒的侵害；
1. 很多用户受骗正是因为钓鱼短信的发件人显示为10086、95588等正常号码而放松安全警惕导致中招，运营商需要加强对伪基站的监控打击力度，减少遭受伪基站干扰的几率；
1. 各大银行、各支付平台需要加强对各自支付转账渠道的监管，完善对用户资金转移等敏感操作的风控机制，防止被不法分子利用窃取用户网银财产;
1. 警惕各种借贷软件的套路，不要轻易使用借贷类App。