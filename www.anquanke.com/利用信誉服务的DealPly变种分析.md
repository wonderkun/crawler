> 原文链接: https://www.anquanke.com//post/id/183372 


# 利用信誉服务的DealPly变种分析


                                阅读量   
                                **139483**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者ensilo，文章来源：blog.ensilo.com
                                <br>原文地址：[https://blog.ensilo.com/leveraging-reputation-services](https://blog.ensilo.com/leveraging-reputation-services)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t011800632bda302b60.jpg)](https://p5.ssl.qhimg.com/t011800632bda302b60.jpg)



## 0x00 前言

通常情况下，Adware（广告软件）并不是特别有趣的一个研究内容。然而某次我们遇到了某个DealPly变种，可以规避AV检测，因此我们决定深入研究一下。

除了模块化代码、机器指纹识别、VM（虚拟机）检测技术以及强大的C&amp;C架构之外，我们最有趣的发现是DealPly 会滥用微软以及McAfee的信誉服务来规避安全检测。微软的SmartScreen服务以及McAfee的WebAdvisor服务可以提供关于文件以及URL的威胁情报信息，并且可以免费使用。利用这些服务数据，这款广告软件可以延长安装程序以及组件的使用周期，只有发现自身被列入黑名单中才会进行修改。这类技术并不局限于广告软件，也可能被恶意软件开发者所采用。

在本文中，我们将简单介绍这款软件的执行流程、指纹识别、VM检测功能，重点关注该软件如何利用信誉服务获取所需信息。



## 0x01 技术分析

### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E6%84%9F%E6%9F%93%E8%BF%87%E7%A8%8B"></a>基本感染过程

DealPly攻击者最长使用的一种感染方式就是诱使用户通过免费软件下载网站来下载已捆绑这款Adware的合法软件安装包。

我们分析的样本名为Fotor（照片裁剪软件）,这本来是一款合法软件安装程序。这款安装程序会在执行时秘密运行DealPly，然后将自身副本拷贝到用户的`%AppData%`目录，执行如下命令完成本地驻留：

```
C:\Windows\system32\schtasks.exe /create /F /tn "`{`5D055606-F35B-577B-8F40-5DE1E36423A2`}`" /xml "C:\Users\JONNYB~1\AppData\Local\Temp\475671.xml"
```

计划任务会每隔一小时执行DealPly，每次执行时，DealPly都会联系`cwnpu.com`这个C&amp;C服务器，通过HTTP发送经过加密的一个请求，如图1所示。

[![](https://p5.ssl.qhimg.com/t015b98d5ea7d8f83f8.png)](https://p5.ssl.qhimg.com/t015b98d5ea7d8f83f8.png)

图1. 加密请求

经过解密后，我们能看到真正的请求消息，如图2所示：

[![](https://p1.ssl.qhimg.com/t01c0af690a981174fa.png)](https://p1.ssl.qhimg.com/t01c0af690a981174fa.png)

图2. 解密后的请求

DealPly会在请求中，通过`bty`以及`lptp`之类的参数来标识被感染的主机是否为VM，后面我们会进一步讨论这一点。

一旦服务器收到有效的请求，就会发送响应，将客户端重定向至`d1oz9ywjzmvfb5.cloudfront.net`。这个域名指向的是某台Amazon S3服务器。响应数据中包含相关指令以及待执行的主模块，主模块名为`WB_CH33.dll`。

### <a class="reference-link" name="%E6%A8%A1%E5%9D%97%E5%8C%96%E4%BB%A3%E7%A0%81%E6%9E%B6%E6%9E%84"></a>模块化代码架构

DealPly可以分成不同模块，这些模块互相配合以实现攻击目标。虽然每个模块承担不同的角色，但所有模块都采用类似的结构，并且包含某些类似的功能，比如字符串解密功能。

[![](https://p4.ssl.qhimg.com/t01abadecc6bc21b3df.png)](https://p4.ssl.qhimg.com/t01abadecc6bc21b3df.png)

图3. DealPly架构

开发者采用这种架构的目的是规避检测，在特定目标中只部署必要组件，尽可能减少蛛丝马迹。

根据我们的分析，`WB_CH33.dll`模块中包含主要功能。值得一提的是，所有模块都采用反射式加载方式，可以通过主模块或者其他命令行工具（如`wscript`、`powershell`等）运行。

`WB_CH33.dll`模块会使用`http://www.geoplugin.net/json.gp`服务来检测地理位置信息，保存国家代码以便后续使用。

`WB_CH33.dll`会使用`sbrg.dll`以及`WebAdvisorDll.dll`模块来查询信誉服务，后续我们会详细介绍这方面内容。

### <a class="reference-link" name="VM%E6%A3%80%E6%B5%8B%E5%8F%8A%E6%8C%87%E7%BA%B9%E6%94%B6%E9%9B%86"></a>VM检测及指纹收集

如图2所示，DealPly会将相关信息发送回C&amp;C服务器，其中包含当前主机是否为虚拟机的相关特征以及主机上的其他信息，这里我们来讨论其中某些特征。

#### <a class="reference-link" name="%E4%B8%BB%E6%9C%BA%E6%8C%87%E7%BA%B9"></a>主机指纹

如图2所示，发往C&amp;C服务端的解密信息中包含`UID`参数及`UID2`参数，这些参数包含关于主机的指纹信息。

`UID`的值包含主机MAC地址以及主机主驱动器序列号的后半部分。

`UID2`的值包含卷序列号以及代表主机名的一个值。

#### <a class="reference-link" name="%E7%9D%A1%E7%9C%A0%E6%8C%89%E9%92%AE"></a>睡眠按钮

虚拟机中没有物理睡眠按钮，该变种会使用`GetPwrCapabilities`函数来判断当前主机是否存在物理的睡眠按钮。该函数的原型如下：

[![](https://p1.ssl.qhimg.com/t01cf9eea861f7d68db.png)](https://p1.ssl.qhimg.com/t01cf9eea861f7d68db.png)

图4. `GetPwrCapabilities` API

该函数会返回一个`PSYSTEM_POWER_CAPABILITIES`结构，DealPly会检查该结构，判断`SleepButtonPresent`变量值为`true`还是`false`。

如果该值为`true`，则代表主机存在物理睡眠按钮，很可能不是虚拟机。

#### <a class="reference-link" name="%E7%94%B5%E6%B1%A0%E7%89%B9%E5%BE%81"></a>电池特征

该变种会调用`GetSystemPowerStatus`函数，检查主机是否连接到物理的AC电源。该函数的定义如下：

[![](https://p1.ssl.qhimg.com/t01e4802996a6e2577b.png)](https://p1.ssl.qhimg.com/t01e4802996a6e2577b.png)

图5. `GetSystemPowerStatus` API

函数返回的`SYSTEM_POWER_STATUS`结构中包含`ACLineStatus`标志，可以用来判断AC电源状态，而AC电源状态可以用来判断电源是否连接到当前主机。

如果当前主机没有连接电源，则很可能是笔记本电脑，因此不大可能是虚拟机。

[![](https://p0.ssl.qhimg.com/t01578e01a7d971fe6d.png)](https://p0.ssl.qhimg.com/t01578e01a7d971fe6d.png)

图6. `SYSTEM_POWER_STATUS`结构

#### <a class="reference-link" name="MAC%E5%9C%B0%E5%9D%80"></a>MAC地址

为了判断当前主机的MAC地址是否为虚拟机MAC地址，该变种会检查主机MAC地址是否属于以下厂商：Microsoft Azure、VMware、Parallels、Oracle Virtualbox、Amazon以及Xensource。

这里有趣的一点在于DealPly会检查主机是否运行在常见的云服务平台上（如Amazon EC2以及Microsoft Azure），背后的原因可能是运行在这些平台上的Windows操作系统会采用云相关的网络适配器，很可能是沙箱环境。

[![](https://p5.ssl.qhimg.com/t0171f0b39b0a2c23f0.png)](https://p5.ssl.qhimg.com/t0171f0b39b0a2c23f0.png)

图7. 基于Mac地址的VM检测过程



## 0x02 利用信誉服务

我们猜测DealPly之所以使用信誉服务，原因在于想检测哪个变种以及下载的网站已经失效，无法用于后续的感染过程。如果从多个服务器或者通过知名代理方案（如Tor）来发起查询，那么很容易就会被官方检测到、加入黑名单，很可能暴露DealPly行踪，因此这种情况下使用分布式主机网络来收集这些信息显然更为有效。这款软件中某些信誉模块只在某些国家中使用。这些国家代码可以分成两组，每组使用不同的模块。SmartScreen信誉模块只在位于A组国家中（参考附录）的主机使用，而McAfee WebAdvisor信誉模块只在位于B组的国家中使用。值得注意的是，某些国家同时属于这两个组。

我们并不清楚攻击者为什么会采用这种行为，这可能与McAfee在某些国家的流行程度有关。

### <a class="reference-link" name="SmartScreen%E6%A8%A1%E5%9D%97"></a>SmartScreen模块

SmartScreen是微软Windows的一项服务，从Windows 8开始集成到Windows系统中，主要功能是提供另一个防护层。

微软官方有如下一段[描述](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-smartscreen/windows-defender-smartscreen-overview)：

> 在您的员工访问已被标记为钓鱼网站或者恶意软件网站、或者尝试下载可能恶意的文件时，Windows Defender SmartScreen都可以给您的员工提供安全的环境。

在执行`Sbrg.dll`模块时，恶意软件就会向C&amp;C发送一个空白请求，服务器会返回一个XML格式的响应，其中包含一些信息，比如哈希值或者准备使用SmartScreen信誉服务器查询的Url。

[![](https://p0.ssl.qhimg.com/t010849b767055b6f60.png)](https://p0.ssl.qhimg.com/t010849b767055b6f60.png)

图8. 与C&amp;C的初始通信数据

接下来，DealPly会使用来自C&amp;C的指令向SmartScreen API发起请求。在图9中，我们可以看到发往`https://urs.smartscreen.microsoft.com/windows/browser/edge/service/navigate`的JSON数据：

[![](https://p2.ssl.qhimg.com/t018d9c73a23cbc77ab.png)](https://p2.ssl.qhimg.com/t018d9c73a23cbc77ab.png)

图9. SmartScreen：查询URL

为了让SmartScreen服务器能够处理请求，DealPly必须提供一个Authorization头，这个头的作用是刷掉其他无效的请求操作。Authorization数据格式如下所示：

[![](https://p0.ssl.qhimg.com/t01f56fa54352e72747.png)](https://p0.ssl.qhimg.com/t01f56fa54352e72747.png)

图10. SmartScreen Authorization

Authorization是经过Base64编码的json数据，如图11所示，其中包含3个变量：`hash`为经过Base64编码的二进制MD5值；`key`是另一个校验值，会计算MD5值以及请求body的校验值；`authId`是一个常量值，很有可能来自于原始的SmartScreen代理。

[![](https://p4.ssl.qhimg.com/t01b452e0b1f7ee6c8f.png)](https://p4.ssl.qhimg.com/t01b452e0b1f7ee6c8f.png)

图11. SmartScreen Authorization参数

来自SmartScreen服务端的响应如图12所示：

[![](https://p0.ssl.qhimg.com/t01b8a73c53d17c29cb.png)](https://p0.ssl.qhimg.com/t01b8a73c53d17c29cb.png)

图12. SmartScreen信誉服务响应

DealPly会尝试匹配如下值：

|字符串|含义
|------
|UNKN|未知URL/F文件
|MLWR|恶意软件相关URL/文件
|PHSH|钓鱼相关URL/文件

接下来，DealPly会向另一个API发送另一个请求，判断信誉服务是否检测到了文件哈希特征。

最终，DealPly会向C&amp;C反馈来自SmartScreen的检测数据。

### <a class="reference-link" name="SmartScreen%E7%89%88%E6%9C%AC"></a>SmartScreen版本

在图13中，我们可以看到某个对象的初始化过程，该对象负责与SmartScreen API的通信。该函数会根据具体的Windows版本选择一个类来处理查询请求。比如，调用`redstone_only`时，会调用名为`_7SmscUtils2ndEd`的一个类，该类中包含用于Windows 10 redstone 1以及2版本（版本号分别为14393及15063）的匹配函数。

[![](https://p5.ssl.qhimg.com/t01e2aee68ad54cbcf4.png)](https://p5.ssl.qhimg.com/t01e2aee68ad54cbcf4.png)

图13. 支持不同版本的SmartScreen API

在新版的SmartScreen服务中，最重要的区别在于查询结构的不同。老版本Windows会使用XML来生成SmartScreen查询，而随后在第一版redstone系统中，Windows已经换成JSON格式的查询请求。

需要注意的是，微软并没有官方公开SmartScreen API文档，这意味着开发者在逆向分析SmartScreen机制/功能方面下了不少功夫。

### <a class="reference-link" name="WebAdvisor%E6%A8%A1%E5%9D%97"></a>WebAdvisor模块

WebAdvisor是针对浏览器的一种防护工具，当用户可能下载或者访问包含恶意内容的站点时可以提醒用户相关风险。

该服务之前名为SiteAdvisor，最近才改名为WebAdvisor，这里我们分析的DealPly变种只针对了新版的WebAdvisor。

McAfee官方的定义如下：

> （WebAdvisor可以）阻止危险网站、检查活动的反病毒及防火墙防护状态、扫描下载内容、监控密码、帮助用户在使用互联网时做出更明智的决策。作为McAfee的高级Web防护软件，McAfee WebAdvisor会将颜色图标放置在搜索结果旁边，在用户点击链接前，帮助用户了解哪些是安全站点、哪些站点可能安装恶意代码、进行钓鱼攻击或者发送垃圾邮件。

该变种首先会检查主机是否安装了特定版本的WebAdvisor，如果满足条件，则会查询WebAdvisor的信誉服务。

样本会将所有请求发送到McAfee信誉服务的如下URL：

```
https://webadvisorc.rest.gti.mcafee.com/1
```

发往信誉服务的某个请求如图14所示，其中包含待查询的URL。该请求中包含一个`op`参数，代表查询的类型。此外还包含一个`cliid`参数，该参数值使用WebAdvisor的某个注册表键值计算所得。我们认为这个值用于身份认证/授权场景，每次查询API时都需要使用该值。

[![](https://p3.ssl.qhimg.com/t01c684bc4546a108ba.png)](https://p3.ssl.qhimg.com/t01c684bc4546a108ba.png)

图14. WebAdvisor URL请求

如图15所示，来自信誉服务的响应报文中包含请求id以及该URL的信誉值。

[![](https://p0.ssl.qhimg.com/t0117e567a63bb997c3.png)](https://p0.ssl.qhimg.com/t0117e567a63bb997c3.png)

图15. WebAdvisor URL响应

每个信誉值的具体含义如图16所示。前面提到过，McAfee WebAdvisor会“将颜色图标放置在搜索结果旁边”。`rep`参数对应的返回值可以归为如下几类：“red”（红色）、“yellow”（黄色）以及“default”（默认）。红色代表恶意、黄色代表风险或者垃圾邮件站点，默认代表未知或者安全。

[![](https://p0.ssl.qhimg.com/t01fe3b452325d56de2.png)](https://p0.ssl.qhimg.com/t01fe3b452325d56de2.png)

图16. WebAdvisor信誉度检查

最后，当模块完成查询请求后，会将结果反馈至DealPly的C&amp;C。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fca71a446171d6c5.png)

图17. 将结果反馈至C&amp;C



## 0x03 总结

在本文中，我们分析了DealPly所采用的一种新型技术，可以用来自动化规避AV产品。通过不断查询信誉服务，攻击者可以自动化评估样本的AV检测率，在需要的时候开发新的样本。这种技术使得DealPly始终能够在与安全解决方案的斗争过程中占得先机。

虽然我们在分析DealPly广告软件时首先观察到这种技术，但我们相信高级恶意软件开发者采用这种技术也只是时间问题。



## 0x04 IoC

### <a class="reference-link" name="%E6%A0%B7%E6%9C%AC%E5%93%88%E5%B8%8C"></a>样本哈希

```
2540E4D34C4D8F494FC4EDDA67737B7209EE6CEFB0EC74028B6ABCD3911EC338 (Fotor3_3.4.1 - official.exe )
B7030B145D4B61655E694441BFE43E8C2BF1BB4D7FF96811F1DC3FCE774C5E70  (Updater.exe)
FC2352A81FEDAD3CBB86DCB0E6B97AD023FE318D468FBB94602FB95F11EB8040  (SBRG.dll)
25CE28FBF32026FCC8DB23A1B3F6C9D78A10CED8D0D32126C044CBEF6AE4E9C9  (WebAdvisorDll.dll)
DF536CA20E421E2E5F4643870355BD39ADC6FB29C96A715BF3CC94B4C371FAB1 (Palikan)
```

### <a class="reference-link" name="%E5%9F%9F%E5%90%8D"></a>域名

```
tuwoqol.com
wugulaf.com
cwnpu.com
bdubnium.com
pydac.com
dabfd.com
fodfr.com
codfs.com
qaofd.com
ziuet.com
pocxc.com
uyvsa.com
bxvdc.com
adofd.com
```

### <a class="reference-link" name="URL"></a>URL

```
https://im-mf.s3.amazonaws.com/WA_WrUp.dat
http://pxl-nw-svr-981333793.us-east-1.elb.amazonaws.com/pxl/
http://dwrfiab3y6c09.cloudfront.net/sbrg.dat
```



## 0x05 附录

### <a class="reference-link" name="A%E7%BB%84%E5%9B%BD%E5%AE%B6"></a>A组国家

```
Algeria
Argentina
Bangladesh
Chile
Colombia
Ecuador
Egypt
India
Indonesia
Iran
Malaysia
Mexico
Morocco
Pakistan
Peru
Philippines
Saudi Arabia
Serbia
South Africa
Taiwan
Thailand
Tunisia
Turkey
Ukraine
United Arab Emirates
Venezuela
Vietnam
```

### <a class="reference-link" name="B%E7%BB%84%E5%9B%BD%E5%AE%B6"></a>B组国家

```
Argentina
Australia
Austria
Belgium
Brazil
Canada
Chile
Colombia
Denmark
Finland
France
Germany
Hong Kong
India
Indonesia
Ireland
Italy
Japan
Luxembourg
Malaysia
Mexico
Netherlands
New Zealand
Norway
Peru
Philippines
Singapore
Spain
Sweden
Switzerland
Taiwan
Thailand
United Kingdom
United States
Venezuela
Viet Nam
```
