> 原文链接: https://www.anquanke.com//post/id/223817 


# 钱包黑洞：Lazarus 组织近期在加密货币方面的隐蔽攻击活动


                                阅读量   
                                **180981**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t012fa651572a71cba7.jpg)](https://p5.ssl.qhimg.com/t012fa651572a71cba7.jpg)



## 概述

Lazarus 组织是一个长期活跃的 APT 组织，因为 2014 年攻击索尼影业而开始受到广泛关注，该组织早期主要针对韩国、日本、美国等国家的政府机构进行攻击活动，以窃取情报等信息为目的。自 2014 年后，该组织开始将全球金融机构，加密交易机构等为目标，进行敛财活动。今年 7 月，我们发布了一篇《泡菜的味道：Lazarus 组织在 MacOS 平台上的攻击活动分析》揭露了 Lazarus 组织在 2019 下半年至 2020 上半年在加密货币方面的攻击活动。近期，通过对该组织的持续监控，微步情报局通过威胁狩猎系统捕获到 Lazarus 组织在加密货币方面近期使用的样本，包含 Windows 和 MacOS 平台的版本，与之前的样本有显著变化。近期攻击活动使用的攻击样本对加密货币的用户有针对性，而且更加隐蔽，不易被发现。
1. Lazarus 组织在加密货币方面的攻击活动持续活跃，使用的样本在不断演化中。
1. Lazarus 组织在 Windows 和 MacOS 平台上对加密货币方面的用户进行针对性的攻击，而且更加隐蔽。
1. Lazarus 组织使用失陷机器作为临时 C&amp;C 服务器来隐藏活动痕迹。
1. 微步在线通过对相关样本、IP 和域名的溯源分析，共提取 29 条相关 IOC，可用于威胁情报检测。


## 详情

Lazarus Group 是一个网络犯罪组织，至少从 2009 年以来一直活跃，据报道是 2014 年 11 月索尼影视娱乐的攻击主要主导者。 它发起了一个被称为“Operation Blockbuster”的网络攻击活动。Lazarus Group 还发起了 Operation Flame, Operation 1Mission, Operation Troy, DarkSeoul 和 Ten Days of /Rain 网络攻击活动。Lazarus 组织是一个长期活跃的 APT 组织，因为 2014 年攻击索尼影业而开始受到广泛关注，该组织早期主要针对韩国、日本、美国等国家的政府机构进行攻击活动，以窃取情报等信息为目的。自 2014 年后，该组织开始将全球金融机构，加密交易机构等为目标，进行敛财活动。尤其是 2018 年以来，Lazarus 组织在 MacOS 平台上的攻击活动日渐活跃。该组织曾于 2018 年 8 月被曝光制作加密货币交易网站 “Celas LLC”，以推广交易软件为名推广恶意代码盗取密币，此后又不断被曝光使用相似手法搭建了“Worldbit-bot”、“JMT Trading”、“Union Crypto Trader”等伪装平台，用于推广 Windows 和 macOS 两种平台下带有后门的交易软件，继续对加密货币生态相关公司发起定向攻击。

微步情报局通过威胁狩猎系统捕获到 Lazarus 组织在加密货币方面近期使用的样本，包含 Windows 和 MacOS 平台的版本，与之前的样本有显著变化。近期攻击活动使用的攻击样本在运行后会检查运行环境再释放恶意代码文件，恶意代码运行后会修改配置实现自启动，之后连接 Lazarus 组织控制的失陷机器，接受攻击者的命令并进行下一阶段的攻击活动，对加密货币的用户有针对性，而且更加隐蔽，不易被发现。

本文从下列角度对 Lazarus 组织近期在加密货币方面的攻击活动进行分析：

1. 攻击过程分析

2. MacOS 平台样本详细分析

3. Windows 平台样本详细分析

4. 加密网络流量特征

5. Lazarus 在加密货币方面攻击的 TTPs（MITRE ATT&amp;CK Framework）

### **1. 攻击过程分析**

分析近期 Lazarus 组织在加密货币方面的攻击活动，Lazarus 组织依旧采用钓鱼的手法，首先制造虚假的加密货币交易网站，然后诱导用户下载含有恶意代码的加密货币交易客户端并安装运行。通过对客户端的分析，我们发现其在杀毒引擎的检出率很低（图1），并且使用失陷网站来作为 C&amp;C 服务器，然后再进行下一阶段的攻击活动。相比于之前的攻击活动，近期的攻击活动更有针对性，更加隐蔽，不易被发现。

以 esilet.com（Lazarus 组织制造的虚假加密货币交易网站）为例。搜索引擎的记录（图2）的关键词 blockchain technology，Top Cryptocurrencies by Market 等均与加密货币相关。esilet.com 页面上有多种加密货币交易价格等信息（图3）。该虚假加密货币交易网站的目标是用户去下载攻击者精心制造的含有恶意代码的客户端 APP（图4）。

[![](https://p3.ssl.qhimg.com/t01c20586a1fd535225.png)](https://p3.ssl.qhimg.com/t01c20586a1fd535225.png)

图 1 – 多款杀毒引擎的检出结果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0188604c1f8cf7c1e2.png)

图 2 – esilet.com的搜索引擎记录

[![](https://p4.ssl.qhimg.com/t016770a7638f237100.png)](https://p4.ssl.qhimg.com/t016770a7638f237100.png)

图 3 – esilet.com的部分内容

[![](https://p1.ssl.qhimg.com/t012d15ddc916859f96.png)](https://p1.ssl.qhimg.com/t012d15ddc916859f96.png)

图 4 – 含恶意代码的客户端下载页面

### **2. MacOS 平台样本分析**

以样本 MD5: 53d9af8829a9c7f6f177178885901c01（MacOS 版本）为例。该样本的主程序 /MacOS/Esilet 会加载运行 /Contents/Frameworks/Esilet Helper (Renderer) 应用，释放恶意代码到 /var/folders/7d/7skpstwd7qnctfwpwp7225xw0000gn/T/Esilet-tmpg7lpp ，然后加载运行 (/bin/sh -c) 该恶意程序 Esilet-tmpg7lpp。

[![](https://p0.ssl.qhimg.com/t013d913eef2860b1d3.png)](https://p0.ssl.qhimg.com/t013d913eef2860b1d3.png)

Esilet-tmpg7lpp 会在 /Library/LaunchDaemons/ 目录下添加配置文件，RunAtLoad 设为 true，来实现开机自启动。

[![](https://p2.ssl.qhimg.com/t0109a3e6e5ed278ae0.png)](https://p2.ssl.qhimg.com/t0109a3e6e5ed278ae0.png)

Esilet-tmpg7lpp 连接到攻击者控制的失陷机器获取下一步指令，目前相关链接已无正常响应。

[![](https://p5.ssl.qhimg.com/t01c57e809cb1c2e80f.png)](https://p5.ssl.qhimg.com/t01c57e809cb1c2e80f.png)

解密 C&amp;C 服务器返回指令的函数。

[![](https://p2.ssl.qhimg.com/t01503878d18df8dba9.png)](https://p2.ssl.qhimg.com/t01503878d18df8dba9.png)

指令执行模块。

[![](https://p0.ssl.qhimg.com/t01f20deaa800499f1f.png)](https://p0.ssl.qhimg.com/t01f20deaa800499f1f.png)

以 sub_100002920 函数为例，该函数具备的功能是运行命令 sh -c sw_vers 来收集设备信息，然后返回给攻击者控制的失陷机器。

[![](https://p4.ssl.qhimg.com/t01c03a0eea2349012a.png)](https://p4.ssl.qhimg.com/t01c03a0eea2349012a.png)

sub_1000036A0 函数具备的功能是执行攻击者返回的 shell 命令。

[![](https://p2.ssl.qhimg.com/t010022ff4d035c453f.png)](https://p2.ssl.qhimg.com/t010022ff4d035c453f.png)

### **3. Windows 平台样本分析**

样本 MD5: 40858748e03a544f6b562a687777397a（Windows 版本）是 Lazarus 组织在 Windows 平台使用的组件，在函数 iAppleCloud 中使用反射式注入手法在内存中加载自身。

[![](https://p2.ssl.qhimg.com/t0186614debb5cbdde0.png)](https://p2.ssl.qhimg.com/t0186614debb5cbdde0.png)

其使用字符串以加密形式存储，使用的时候动态解密，且使用的相关 API 也以动态获取形式使用，首先创建一个挂起的系统进程 mspaint.exe。

[![](https://p0.ssl.qhimg.com/t01317bc806c5c90e1a.png)](https://p0.ssl.qhimg.com/t01317bc806c5c90e1a.png)

然后将自身注入到 mspaint.exe 进程中执行。

[![](https://p0.ssl.qhimg.com/t01b27de5afacfaf02d.png)](https://p0.ssl.qhimg.com/t01b27de5afacfaf02d.png)

成功注入执行后，首先将自身 dll 删除。

[![](https://p0.ssl.qhimg.com/t0171c2b948921951df.png)](https://p0.ssl.qhimg.com/t0171c2b948921951df.png)

然后创建互斥体，确保只有一个木马实例运行。

[![](https://p2.ssl.qhimg.com/t01c0020f4775f0a6ad.png)](https://p2.ssl.qhimg.com/t01c0020f4775f0a6ad.png)

收集主机信息，包括系统版本、系统架构、systeminfo、杀软信息、网卡信息、磁盘信息、进程列表、CPU 信息的等等并加密。

[![](https://p5.ssl.qhimg.com/t011bd270e4c2305013.png)](https://p5.ssl.qhimg.com/t011bd270e4c2305013.png)

尝试循环连接 5 个URL，将收集到的主机信息以 POST 方法发送至服务器，而这 5 个链接均为 Lazarus 组织所控制的失陷机器，目前链接已无正常响应。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018cad4026f8fb464b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010fa49c9235fd06bf.png)

然后将服务器返回数据保存到指定目录下，并为其创建进程执行。

[![](https://p4.ssl.qhimg.com/t012a6952b0e6e48f38.png)](https://p4.ssl.qhimg.com/t012a6952b0e6e48f38.png)

[![](https://p3.ssl.qhimg.com/t01deb7488c8397e14e.png)](https://p3.ssl.qhimg.com/t01deb7488c8397e14e.png)

### **4. 加密网络流量的特征**

[![](https://p0.ssl.qhimg.com/t01cdbedbb791d3ae77.png)](https://p0.ssl.qhimg.com/t01cdbedbb791d3ae77.png)

### **5. MITRE ATT&amp;CK Framework (Lazarus, TTPs)**

[![](https://p0.ssl.qhimg.com/t0154f9f7053e04cbf8.png)](https://p0.ssl.qhimg.com/t0154f9f7053e04cbf8.png)



## 结论

Lazarus 组织在加密货币方面的攻击虽然已被曝光多次，但是相关攻击活动依旧持续活跃。通过对该组织的持续监控，微步情报局通过威胁狩猎系统捕获到 Lazarus 组织在加密货币方面近期使用的样本，包含 Windows 和 MacOS 平台的版本，与之前的样本有显著变化，对加密货币的用户更有针对性，更加隐蔽，不易被发现。

为了保护系统免受此类威胁，用户应仅从官方和合法市场下载应用程序，不打开和安装未知来源的程序。对于此类伪装为加密货币交易平台来传播木马的攻击手法，加密货币公司及相关从业人员应该提高警惕。



## 附录 – IOC

### Hash

SHA256

25bed4be8c78f9728ad9b6cc86a38ee95bdf8d91e2635a0cf785bc603140163c

ec84802bb2bb33c52c1f02e7a7b74c6ea6247611c410bf386a95dc1eb45e2347

9ba02f8a985ec1a99ab7b78fa678f26c0273d91ae7cbe45b814e6775ec477598

dced1acbbe11db2b9e7ae44a617f3c12d6613a8188f6a1ece0451e4cd4205156

ee72f31f961f8fb703d6613686d7ba4370dfee10e78591c506b84d087d025b77

917b4075b47f5e8004cc6915bb5481080ef77bb048a0139aefdf4990e5ef9c50

08051b859367ab3c85522dd751755ee881464afa2fd89a955c2c8aad49d1e81c

c97bce0037078a7fc7738087fd12b7052e2cdb2bfdb6e3509d0a84adea81a16e

### C2

torrytrade.com

skord.me

dorusio.com

esilet.com

### URL

https://admforte.com.br/wp-content/plugins/top.php

https://shahrtdc.com/wp-content/plugins/top.php

[https://justholdfast.com/doodle/wp-content/plugins/top.php](https://justholdfast.com/doodle/wp-content/plugins/top.php)

https://infodigitalnew.com/wp-content/plugins/top.php

https://sche-eg.org/plugins/top.php

https://www.vinoymas.ch/wp-content/plugins/top.php

[http://torrytrade.com/info.php?truefalsefalse](http://torrytrade.com/info.php?truefalsefalse)

[http://torrytrade.com/info.php?04](https://www.virustotal.com/gui/search/http:/torrytrade.com/info.php?04)

http://drei-schneeballen.de/wp-content/plugins/nextgen-gallery/view.php

https://qwerty.creativehonduras.com/wp-includes/class-wp-redirect.php

http://www.urbankizomba.se/wp-content/plugins/photo-gallery/filemanager/upload.php

http://tag-cloud-photo.freeware.filetransit.com/login.php

http://funny-pictures.picphotos.net/saint-louis-senior-photos-senior-pictures-seniors-st-louis-st-louis/upload.php

https://www.charcuterie-a-la-ferme.com/wp-content/plugins/ckeditor-for-wordpress/ckeditor/plugins/image/images/get.php?ts=5F7912FF_D899390

http://tipslonim.by/wp-content/plugins/ckeditor-for-wordpress/ckeditor/plugins/image/every.php?ts=5F7912B0_103BAC80

http://nurture.com.sg/wp-content/plugins/ckeditor-for-wordpress/ckeditor/plugins/image/upgrade.php?ts=5F791207_1ABFC40

https://australia-express.com/wp-includes/image-list.php?ts=5F79125F_1E22F78B

### 关于微步情报局

微步情报局，即微步在线研究响应团队，负责微步在线安全分析与安全服务业务，主要研究内容包括威胁情报自动化研发、高级APT组织&amp;黑产研究与追踪、恶意代码与自动化分析技术、重大事件应急响应等。
