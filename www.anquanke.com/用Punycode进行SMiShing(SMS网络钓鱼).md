> 原文链接: https://www.anquanke.com//post/id/147104 


# 用Punycode进行SMiShing(SMS网络钓鱼)


                                阅读量   
                                **108732**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.zscaler.com/
                                <br>原文地址：[https://www.zscaler.com/blogs/research/smishing-punycode](https://www.zscaler.com/blogs/research/smishing-punycode)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0103d8e200cf2b15d2.jpg)](https://p4.ssl.qhimg.com/t0103d8e200cf2b15d2.jpg)

网络犯罪分子想出提出新的方法来窃取用户隐私数据并从中获利。由于移动设备的流行和其功能的强大，使之正成为各种网络攻击的目标，而此前这些攻击行为的对象仅限于计算机。

其中一种攻击技术就是SMS网络钓鱼——SMiShing，其通过短信来发送攻击。在SMiShing中，移动用户会在短信或聊天应用程序中接收到钓鱼网站的链接，攻击者会通过这些短信来引诱用户点击链接并输入其个人信息。

Zscaler ThreatlabZ观察到很多这种SMiShing攻击都使用“Punycode”来使钓鱼网址看起来更像是一个合法的网站URL，这种技术被称为[同形异义词（Homograph）攻击](https://en.wikipedia.org/wiki/IDN_homograph_attack)，攻击者试图通过将URL中的一个或多个字符替换为其他字符脚本中类似外观的字符来达到欺骗用户的目的。

以下的是我们在过去三个月内观测到的在移动设备上用Punycode进行网络钓鱼活动的URL的点击率。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-4.zscaler.com/cdn/farfuture/htPkG8vpTTtsBcekOtiwviBkWL9KnRLywx37lKgHIGc/mtime:1527626875/sites/default/files/images/blogs/smishing/ZDF.png?_ga=2.24719226.1507816898.1528117840-2133850840.1528117840)**图1. 从2018年3月1日到5月28日针对移动设备的SMiShing活动中的Punycode URL的点击率**

让我们来看看最近的一个示例，该示例显示了一个假装成Jet Airways免费机票供给链接的WhatsApp消息。该链接的设计看起来像实际的jetairways.com网站，但它使用的是同形异义词攻击，其中使用了相似的字符来欺骗受害者。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-5.zscaler.com/cdn/farfuture/YNv_gtFUe4WTHsjfCsW1X5e3MFYaYqFPDTfNPUV9VFw/mtime:1527190287/sites/default/files/images/blogs/smishing/whatsapp_message.png)**图2. 攻击示例**

如果仔细查看URL域名中的字符“i”，可以看到它是一个来自拉丁字符集的同形异义词。更确切地说，它是一个Unicode字符“Latin small letter dotless I”（U + 0131），代替了“airways”中的字母“i”。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-5.zscaler.com/cdn/farfuture/3gKx5_9DMLmXn83uBx16IlwyRc6kCM-1QdjejU6ZEdE/mtime:1527190359/sites/default/files/images/blogs/smishing/UTF.png?_ga=2.234563806.1507816898.1528117840-2133850840.1528117840)**图3. 对同形异义域标签进行解码后的结果**

如果用户在iPhone上点击了此链接，就会打开Safari Web浏览器并尝试加载钓鱼网站。注意这个URL看起来很像jetairways.com，因此对于用户来说很难察觉它并不是真正的网站。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-4.zscaler.com/cdn/farfuture/wlvfePzZUiKndp9B7rxUR43mY0G2gKZmykTBg1tN5n0/mtime:1527190328/sites/default/files/images/blogs/smishing/WhatsApp%20Image%202018-05-23%20at%2012.37.34%20PM.jpeg?_ga=2.238635072.1507816898.1528117840-2133850840.1528117840)**图4. Safari浏览器打开钓鱼网站后的效果**

并非所有浏览器都平等对待IDN URL，在下面的图片中，我们看到Android手机上的Google Chrome向用户显示的Punycode格式的URL。

[![](https://cdn.zscaler.com/cdn/farfuture/Lhv1D2B8kSbQpDuABtIFFb0_ElkbKg6j8HDZ2SNy14k/mtime:1527627085/sites/default/files/images/blogs/smishing/Android_Updated.png)](https://cdn.zscaler.com/cdn/farfuture/Lhv1D2B8kSbQpDuABtIFFb0_ElkbKg6j8HDZ2SNy14k/mtime:1527627085/sites/default/files/images/blogs/smishing/Android_Updated.png)**图5. 安卓手机上的Google Chrome浏览器显示Punycode的URL，而不是IDN格式**

Web浏览器根据不同情况来决定显示IDN格式还是Punycode格式，例如URL中存在可能会欺骗分隔符的特定字符比如“.”或者“/”，则需要确定所有字符是否来自于同一种语言，是否属于允许的组合，或着直接检查该域名是否存在于白名单TLD之中。[这里](https://wiki.mozilla.org/IDN_Display_Algorithm#Algorithm)详细介绍了这个算法，谷歌浏览器也采用了一套类似的规则，其次是Mozilla Firefox浏览器（详情见[这里](https://www.chromium.org/developers/design-documents/idn-in-google-chrome)）。浏览器可以根据分类的[限制级别](http://www.unicode.org/reports/tr39/#Restriction_Level_Detection)来进行抉择 。

以下是常见Web浏览器对IDN域标签的不同反应。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-5.zscaler.com/cdn/farfuture/mc77caOezcrySsNCnClxo1HtNIzD2sQkkf2_jfWKAGo/mtime:1527627190/sites/default/files/images/blogs/smishing/Browser_Behavior.png?_ga=2.24667002.1507816898.1528117840-2133850840.1528117840)**图6. 常见Web浏览器对IDN域标签的不同反应**

回到我们之前的示例，如果我们在Domaintools上检查这个域名的域名历史记录，它会显示该域名是在前两周内新注册的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-2.zscaler.com/cdn/farfuture/TYMP4oiji3vACSG18My33vsB_Fy63c30kZMFmSxflRk/mtime:1527190432/sites/default/files/images/blogs/smishing/2018-05-23%2012_43_54-Jeta%C4%B1rways.com%20WHOIS%2C%20DNS%2C%20%26%20Domain%20Info%20-%20DomainTools.png?_ga=2.238708160.1507816898.1528117840-2133850840.1528117840)**图7. 域名注册信息**

这次钓鱼攻击的完整生命周期展示在以下的截图中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-2.zscaler.com/cdn/farfuture/MwO08OgYQR_bmWMgjUyF3ocsoDk_kyjg146kQM4Z5iM/mtime:1527190464/sites/default/files/images/blogs/smishing/Fiddler.png?_ga=2.3228528.1507816898.1528117840-2133850840.1528117840)**图8. 网络钓鱼网页截图**

我们可以看到，在受到钓鱼页面的攻击后，受害者被重定向到了另一个域名：newuewfarben [.] com，该域被用来为恶意软件提供服务。在测试时，并未发现这个URL的活动。

## 

## 结论

SMiShing在2018年一直呈上升趋势，同形异义技术的加入也将使其对不知情的移动用户造成更大的危害。网页浏览器已经采取了对同形异义攻击的保护措施，但由于Punycode字符的合法性，开发人员想要设计一个万无一失的解决方案会非常困难，而攻击者则可以利用这一点来解决规则并创建同形异义文档，尽管本质上它们是恶意的，但它们仍可以IDN的格式显示。<br>
Zscaler ThreatLabZ正在积极监控此类攻击，以确保Zscaler客户受到保护。

### **用户如何保护自己？**

用户在点击任何通过短信或IM应用程序共享的链接之前应保持警惕，即使它们来自于一位可信的联系人。IDN格式显示由浏览器设计控制，最终用户在控制如何显示URL有局限性。主要和最有效的方法是利用密码管理器在输入密码之前检查URL，这可有效降低用户向同形异义网址钓鱼网站输入凭证的机会。辅助检查将有效检测URL以查看是否有任何明显的字符切换。
