> 原文链接: https://www.anquanke.com//post/id/147352 


# 分析安卓恶意软件RuMMS新变种


                                阅读量   
                                **119668**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.zscaler.com/
                                <br>原文地址：[https://www.zscaler.com/blogs/research/rumms-malware-back-enhancements](https://www.zscaler.com/blogs/research/rumms-malware-back-enhancements)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t010d622f99b7cd81af.png)](https://p1.ssl.qhimg.com/t010d622f99b7cd81af.png)

## 概述

近期，Zscaler ThreatLabZ团队发现了一个恶意软件，该恶意软件源自于名为mmsprivate[.]site的虚假MMS网站上。该网站诱导用户点击查看私人分享的照片，在用户点击后，将会在手机上下载一个恶意Android软件包（APK）。该恶意软件将自身伪装成“Сooбщениe”，翻译为中文是“信息”的意思，并通过利用Android AccessibilityService来执行其恶意功能，被利用的这一功能可帮助残障人士使用Android设备和应用程序。在恶意软件运行后，它会隐藏自身，并暗中监视被感染用户。<br>
FireEye的研究人员在2016年对RuMMS恶意软件进行过一次分析（ [https://www.fireeye.com/blog/threat-research/2016/04/rumms-android-malware.html](https://www.fireeye.com/blog/threat-research/2016/04/rumms-android-malware.html) ），而我们此次所分析的恶意软件变种具有一些与原始样本相似的特征，同时也进行了部分修改，包含了一些新的功能，因此我们将本次分析的新变种称为RuMMS v2.0。



## 样本详情

APP名称：Сooбщениe<br>
Hash值：c1f80e88a0470711cac720a66747665e<br>
包名称：ru.row.glass



## 详细分析

### <a class="reference-link" name="%E4%B8%8B%E8%BD%BD%E5%92%8C%E5%AE%89%E8%A3%85"></a>下载和安装

恶意软件通过网站mmsprivate[.]site/feel/ 实现传播，并且很可能会通过短信和电子邮件实现进一步扩散。一旦用户点击该链接访问，恶意页面就会诱导用户点击一个按钮，在点击这个按钮之后便可以下载恶意APK文件。该恶意页面所使用的语言为俄文，下图为截图及相应翻译：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-2.zscaler.com/cdn/farfuture/0Oxy3AZlaPN8LyfHPvcm5pC5gPlQxVZtye9iFDxvSec/mtime:1527149553/sites/default/files/images/blogs/downloads/edited_initial_url.png)<br>
该APK来自未知来源，因此Android系统默认不允许安装，需要用户点击“允许安装未知来源的APP”才可以成功安装恶意应用程序。具体步骤如下。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-3.zscaler.com/cdn/farfuture/eFoJjGy9NE0iMnfJ9KKOrK3lH_tgAtFafqC-AM8PhqQ/mtime:1527149554/sites/default/files/images/blogs/downloads/edited_unknow_source_install.png)

### <a class="reference-link" name="%E5%90%AF%E7%94%A8AccessibilityService"></a>启用AccessibilityService

在安装完成后，该应用程序会将自己伪装为一个消息应用程序（可以从下图中的图标看出）。在第一次运行时，应用程序会询问用户是否启用Android AccessibilityService。在用户允许启用后，应用程序将从主屏幕上消失。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-3.zscaler.com/cdn/farfuture/8MD53kRpvdh1_dhXcXYCpy5aWqXTmGt_bqqWpUhnheo/mtime:1527149554/sites/default/files/images/blogs/downloads/edited_enabling_accessibility_serives.png)<br>
如果被感染用户没有启用AccessibilityService，那么诱导界面将持续出现在屏幕上（请参见上述图片中的第二个屏幕截图），从而继续引导用户启用该服务。<br>
一旦启用AccessibilityService，间谍软件就会启动，会将Сooбщениe APP修改为默认的消息APP。该间谍软件通过使用AccessibilityService的功能，在提示要求确认修改此应用程序为默认消息应用程序时，自动选择“是”，这一过程中用户将无法看到这一提示信息。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-5.zscaler.com/cdn/farfuture/RoIfz0WvuTqN5GPaYJX-udYmsin83gRegcOdDzeBAZo/mtime:1527149554/sites/default/files/images/blogs/downloads/message_popup.png)

### <a class="reference-link" name="%E9%80%9A%E4%BF%A1"></a>通信

根据我们的分析，在初始化设置完成后，恶意软件就开始向命令和控制（C&amp;C）服务器发送详细信息，C&amp;C服务器的信息以硬编码的方式保存。向C&amp;C服务器发送的请求及其回复的响应都采用Base64编码，下图展现了解码后的内容：<br>[![](https://4.bp.blogspot.com/-J4P2UJ5iBs8/WwUVC4E6F3I/AAAAAAAABMo/rhZIlME60HsgxRGzswmCgDy9Mhx8EwW_ACLcBGAs/s1600/mms_device_details_encoded_request.png)](https://4.bp.blogspot.com/-J4P2UJ5iBs8/WwUVC4E6F3I/AAAAAAAABMo/rhZIlME60HsgxRGzswmCgDy9Mhx8EwW_ACLcBGAs/s1600/mms_device_details_encoded_request.png)在上图中，我们可以看到被感染设备发送给C&amp;C服务器的详细信息。C&amp;C服务器回复了命令“40”和APP的名称。我们注意到，命令“40”代表禁用应用程序。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-4.zscaler.com/cdn/farfuture/Gh4TxztMiXYGNGHol-ze_DeyANgg7jN3f49GoB737-c/mtime:1527149555/sites/default/files/images/blogs/downloads/mms_initial_response.png)在要禁用的应用程序列表中，包含许多知名的反病毒应用，其中包括：Trend Micro、Dr. Web、AhnLab、Avira、Sophos、McAfee、F-Secure。<br>
恶意软件会确保这些反病毒应用程序无法使用。一旦被感染用户试图打开其中的一个应用，恶意软件会立即将其关闭。这一行为类似于针对俄罗斯银行Sber Bank的恶意程序，该恶意程序不允许任何Sber Bank应用启动。

### <a class="reference-link" name="%E5%8F%91%E9%80%81%E7%9F%AD%E4%BF%A1%E4%B8%8E%E7%AA%83%E5%8F%96%E7%9F%AD%E4%BF%A1%E5%86%85%E5%AE%B9"></a>发送短信与窃取短信内容

恶意软件等待来自C&amp;C服务器的命令，并根据该命令执行相应的功能。分析过程中我们发现，命令“11”用于发送SMS消息到任意指定的号码，而C&amp;C服务器还可以指定短信的正文内容。<br>[![](https://2.bp.blogspot.com/-PM5UBG8DdcY/WwU2hcBIh_I/AAAAAAAABNc/aL3ck07dEkot-xXBOciG44xcJtgMjWKfwCLcBGAs/s1600/mms_sms_response.png)](https://2.bp.blogspot.com/-PM5UBG8DdcY/WwU2hcBIh_I/AAAAAAAABNc/aL3ck07dEkot-xXBOciG44xcJtgMjWKfwCLcBGAs/s1600/mms_sms_response.png)经过进一步分析，我们还发现恶意软件可以窃取被感染设备上的短信内容。该功能可以用于窃取银行相关的验证码和其他信息。下图展示了这一功能的相关代码：<br>[![](https://2.bp.blogspot.com/-XmBFOhsSNnI/WwVDyiHe_pI/AAAAAAAABN0/N2d3xupiLYAL9g_Fsz_Kx-CmLUZ-Ds0KACLcBGAs/s1600/mms_steal_sms.png)](https://2.bp.blogspot.com/-XmBFOhsSNnI/WwVDyiHe_pI/AAAAAAAABN0/N2d3xupiLYAL9g_Fsz_Kx-CmLUZ-Ds0KACLcBGAs/s1600/mms_steal_sms.png)

### <a class="reference-link" name="%E7%AA%83%E5%8F%96%E9%80%9A%E8%AE%AF%E5%BD%95"></a>窃取通讯录

该恶意软件还能够窃取被感染设备上的联系人信息。我们相信这一功能可能会被用于借助SMS-Phishing（SMiShing）技术来进一步传播恶意软件。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-4.zscaler.com/cdn/farfuture/utMKwE7sDTCa-ML5gpNMXC1C8S_fdkL0dVshFDoGyu0/mtime:1527149556/sites/default/files/images/blogs/downloads/mms_steal_contacts.png)

### <a class="reference-link" name="%E5%91%BC%E5%8F%AB%E7%89%B9%E5%AE%9A%E5%8F%B7%E7%A0%81"></a>呼叫特定号码

该恶意软件还具有呼叫号码功能。在下图中的例子中，需要被呼叫的号码是由C&amp;C服务器发送编码后的信息来指定的。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-5.zscaler.com/cdn/farfuture/um19RZT6ALHlghDrU00KQFBzpcJSeTX34sGWJyjDCfc/mtime:1527149556/sites/default/files/images/blogs/downloads/mms_call.png)



## 分发方式

我们注意到另外一个更有趣的事情，就是恶意软件的分发方式。每次我们访问恶意链接时，都能够看到一个新的恶意应用程序，这些应用程序尽管具有相同的功能，但它们的应用程序名称、软件包名称甚至Android证书签名都不相同。我们还发现，应用程序使用不同的C&amp;C服务器，其格式为：http[:]//&lt;域名&gt;[.]com/&lt;随机字符&gt;/index.php。我们注意到目前存在如下与C&amp;C服务器相关联的域名：

```
Sr #     Domain Name     # of apps contacted
1     sisirplus[.]com         172
2     vietusprotus[.]com          50
3     glowbobget[.]com         45
4     hellowopung[.]com         102
5     quostpeopls[.]com         24
6     bannerincbest[.]com         102
7     campuphome[.]com         9
8     wewelowertick[.]com         3
9     bigslogous[.]com         25
10     zavannerweb[.]com         55
```



## 总结

RuMMS v2.0在原有版本的基础上，对一些功能进行了增强，对部分功能进行了修改和更新。在经过一段休眠期之后，目前的新变种又重新活跃在网络中。在2018年5月末，Zscaler ThreatlabZ团队共在野外发现了580多款类似的应用程序。我们建议广大用户始终避免点击未知的链接，永远不要相信通过短信或电子邮件方式收到的可疑网址，并坚持从官方应用商店下载应用。



## IoC

下面列举了近期发现样本的SHA256哈希值，包含580个以上应用的更完整列表请参阅： [https://pastebin.com/7tfmsjmb](https://pastebin.com/7tfmsjmb) 。<br>
2cc08d98b2bc11047791e722c2f0e7639f4c5772cda0fb5ecabec1b55914a3c2<br>
6ec7fba253b76d3b8090a98c6e87c662af8bcda1694a617cce7db59feb08e6f1<br>
96a8393e583ff1a12df458534790dfd2551861a4fd600f741e36023682d9d9be<br>
1092d809488da433c5d5433a4a1efdc2e32445637e44b6dc77b7fa0e4d536c43<br>
762c5d1b1b95c46aa6727a49ae27e2b19863d406da2091e50ffe13c79211ffac<br>
af6773b1dcec3c3a1d05964ed9d245c2271e96835ffbe3fc543912dc602a64f9<br>
cfc50b2e3da760a2369dbb5bf45fc8d3cdc37a2ad020084aafe2acb53d8603d6<br>
707456abf552e13ba4ece378d0a7a672bd8fbc22185a478478c81fc7e5c96ce9<br>
a8352f93f7c23953a6deeace67205216c1d37d7f8f6207147d7b93cf272fca9c<br>
751f1ed896639b62e433fcbce5d87b1baeb7a5a82c3a855d30fa4c4c8dddfd81<br>
a1ff7ca12de6cbf36a67aa10ee95202f0c37b8b953f916e9f1780a10042e36af<br>
4a429aae275be2e06ce751537deae327ba377e2e96fc040611f910957b64fcf5<br>
83728b3d17974df0ac424845668496a2bbf6eaa166e899ef2bf842dae2359bf6<br>
be4ceb20c9ddf2ddba90988a41ee68f43f205860d9a66d5ac8da500f55fb9d21<br>
09aefb181d949be189a580e5415b74f372d61a13edd86930e6aa0046231813fe<br>
b5a7683172d38220c4d179c525b9dd8ffaa28b6b5cb9c1b45bac7a72327b7da6<br>
383ddecdcdbe2e43035e34307a026e66f79e0b5556f231684db876b3104f0e10<br>
d6f172b04d2e4d1eb7d5e58b16d9768cfe59c32d987ca9b4534e9cf859cce8f4<br>
f18f523d581acb3136e85cb7b2a056f88e48f2d1dfe21f003ef3f12269e470e1<br>
47e105ef7874e30903d6edadeaa5c2731280663f48c7fb5004cc7668a3ac2a81<br>
d3ca7e61067f527f7cefdddabb0b770ae8ad6d38a89b0f0bccbed995893cea19<br>
1c66a552c0090f81f7b2ce11c8974bbd2aea75afc1092ad5e8d6f8a1ccf416f3<br>
21569d8d302180098231efa76482c5a673f344cba8b4654130fada58aad7e62f<br>
f2c1b8bd0777cd69329fe22fec8519d810e41b000b92ee13de5629dcd3e875ad<br>
98ab7f612c7a1dc3fd44fbd045a6cf21d8c9240dbad08f847423df5f22d7b460<br>
758fbbd8a142933f9c5a9866ea7b7c26789da293c93ec3223f5661f62939325c<br>
0b246a1ba24761fb4d6f105d210af9e9c2507b475f13084780a7f9e8145a91a6<br>
eb607863d2e6a56a53893d4c6253896f3e7ab229a75ad29b32762f27bbd398e5<br>
642be174b9ad9d14b4079472d0a641b9c73f6eb3d8a40152025d438619e22ad5<br>
bd800b6cc3ea900aa111c88adcffca2b31f8c47e00928df985d62bf4cc0daf2d<br>
6858491a04ba906f912d0baf86b37e8ef42c63c505e0db3ffffdf5b543e0c829<br>
2518d9deb54ed0fa373b0b22a16da5b7a8f02502470987aeeba34398e083c15c<br>
f0dabdc7f4364e810e1870afccfd6af14f844f494cd9026879dc2b3becdba8a7<br>
5e4f663d867ab14c7a2ad6e5f35aa315e34ea0e01c50dbb8d63667c405437e1c<br>
389393e8642e61e8f884ae288be53b71aa9ff5846c5760d013e57c6843e14440<br>
2dfa3d51b031976f8418d8f7d05f8fa803b937cfc6711f9d4ffeca45ca3db0a5<br>
b4dd995909b8f99d2b519d347c27386b0bfa434332eb7b0c7483a10f0d1d864c<br>
f260bb6965405aac4a79de75650f184911185c34e27cc43d27c88efca86ab712<br>
bf170d05c2ae2738ae298b851390eca2bed6fb6db729e3150d3809179c02bec7<br>
e191bc75a21a613232cf5cff2f4874106f3cd64f867b5096b193a7fcf9dc74c4<br>
88b1fc39c3e89e790fa7fdba78516ac52b489209e9fb38c39aac416f53fdde90<br>
64647593a8cdfba26a39441cdf49216fbb687652f490cbed230ebc2061aa6b17<br>
027c3f91df5b5f413c4ce117d4e1a4eb33c050a4be96a0385e8a4cc1c445c027<br>
ee996791fcabcc88d1bc082060a9989fdb1b7079c2e66583002443ac43da87ec<br>
a97e2e39a29ebd7ace2895621a6cf2f4a53990d55752816957034b916a149a31<br>
c170ee01c009f4d1a960f6dca3edd2d96fd4e31fad29b7bac248314947d09d1d<br>
b0d4b92653518def16f6b08739cf47ba463a6a18f6c7c85ace7be9d6f4145084<br>
7cffccf41385f1c82c5383a68d79999a1ff506b403cbb00879351bb247a09371<br>
59746db01df4c33edebf4b4b6cfb44d297cde45f23ec6678ef0f2ca15b40d6e9<br>
b2a940600d50d862f539eead80d636b556d32aabc462156fe8b29d44c3337ab8<br>
8e839d560f08ae14d5ca457ace9735419e8d5e06f8c30febb48d2997145ff1b6<br>
5bbecc8c2eaea918ce06e37fa8fda338861662d682cfa43e26ebca6c1075114d<br>
d186eaaf72c80289e755ab20a604e4ff20dc98349dfb56206848a4ec79d9388f<br>
cc978d00329bbb2c2bf60055d5762dd7b407f44b8df2a31f0d1e54a0958271d8<br>
d507332483bb124158b2b02bf0f3d7b07977bf7fa1c34df5a1b001979a2e2a66<br>
65d34b945cccd91ce48eb77458768aba34be86be9372f36162e6d42198416775<br>
bce3428913c048d7f8114d07fffacecb7273d65a41e0c7b8bff3f63abb1913b1<br>
a801e38fb832b7f4f9713fb4fbb35f4c5de156c5787718d7fdbe636499e99cf0<br>
048e3bc98ae1d8ac57eb5e55c5b2cbc6661a77992650a10e35a5d0fbbc1227cf<br>
cbb5b11f0e934e8e13c1590c5868dce72f1a364ab32e7ba408f2ad9fa8d5145b<br>
d1259c1461d71e238ac9984baf96b94c2c145a820ea44d487b6f2fc4e196ef70<br>
09ead1fcde087a14da07d58b8db8bed1b18e08701ee4ee300d2af3dbe1a6bd55<br>
a36e780153fb6c26e28ab5cb4c51ebfeb6dd1e04ec6f4489d9ea67c710015b74<br>
71567ed7c3c0b14a09b5cbd712fcdc777a6bb5d0685c24cccc82e1d1ac3d5d3f<br>
319246f91aff8b444037474ce845cc51785b160a2b650a54cfbe402621598de5<br>
c14c22ddb3d492ef6b40afb3918a97a4b9a8def4dfb6dc944bcdb476e347f1a5<br>
790654bcb118cf14a6ffcb82a73d18620ab1a993f570d6186f3a1571b6d2b2e8<br>
04ae5d0126670a8a1eab95373e39db662c921ee468ea7d842d9f894e3d1270c6<br>
f7cb9474374badcc8881bd5c48ff9d0ac3149de053d93abc9a1cad45c319ad04<br>
bb58e7eb3aa7f212c4d8a4bab1dbd086b8d5621441f50b774d6550b811978897<br>
2202684f0ff5b627baa8473f2068ee3b1d976d7d860f9c188a9178253d356cb3<br>
d130b94a85a8ded1f52469b68977f601617bd536df34c279d37674b03119eb9c<br>
359f8c5ced61249c52655de6ff263c76878c15be12577a920d667f4dcf52e033<br>
b51a6a66778db92878578f3e45cba90fcdb64ca8ece738053b399430bde9e94c<br>
0da9e58ce9b435726f691e869e3efa8f331a8fc2c877c0cee48430837685ec0e<br>
f2176c17ee41cb242db184db275d782293e1a71b7d19fd160d56872b17c75096<br>
c9bfea7a58aa8a3b60198832d891622da61d48ace0d97d42aa5616c76382
