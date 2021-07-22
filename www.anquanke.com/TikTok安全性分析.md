> 原文链接: https://www.anquanke.com//post/id/197004 


# TikTok安全性分析


                                阅读量   
                                **1216559**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者checkpoint，文章来源：research.checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/2020/tik-or-tok-is-tiktok-secure-enough/](https://research.checkpoint.com/2020/tik-or-tok-is-tiktok-secure-enough/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t019b1399fd8b49dfb9.jpg)](https://p3.ssl.qhimg.com/t019b1399fd8b49dfb9.jpg)



## 0x00 前言

TikTok（抖音国际版）覆盖全球150多个国家和地区，提供**75**种服务语言，拥有超过10亿用户，在全球拥有极高的热度。截至2019年10月份，TikTok是世界上下载次数最多的应用程序之一。

该应用主要面向青少年群体，可以用来创建音乐小视频（通常配合3~5秒音乐），或者循环小视频（3~60秒）。用户可以通过该应用分享、保存自己以及亲人的私密视频。

在过去几个月中，我们发现TikTok应用中存在一些潜在安全风险，并且得到了业内其他小伙伴的确认。根据[USA Today](https://www.usatoday.com/story/tech/2019/12/23/us-navy-bans-personnel-using-tiktok-government-issued-phones/2732203001/)报道，美国海军已禁止所属人员使用该应用。另据[The Guardian](https://www.theguardian.com/technology/2019/oct/24/tiktok-foreign-interference-chuck-schumer-tom-cotton)报道，资深民主党人Chuck Schumer表示：“TikTok会对国家安全带来潜在风险”。此外，[New York Times](https://www.nytimes.com/2019/11/01/technology/tiktok-national-security-review.html)报道称TikTok应用正在接受国家安全审查。最近[CNet.com](https://www.cnet.com/google-amp/news/us-army-bans-tiktok-app-from-government-phones/)报道美陆军禁止相关人员在政府手机上使用TikTok，一改其在娱乐应用上的政策（最近官方曾使用该应用来招募人员）。

Check Point Research团队最近在TikTok应用中发现了多个漏洞，攻击者可以使用这些漏洞完成如下操作：

1、控制TikTok账户，篡改用户内容；

2、删除视频；

3、未授权上传视频；

4、公开“私密”视频；

5、获取账户中保存的个人信息，比如私人邮件地址等。

Check Point Research团队已向TikTok开发者提交了此次研究中找到的漏洞，官方已发布解决方案，确保用户能安全使用TikTok应用。

请访问[此处](https://research.checkpoint.com/wp-content/uploads/2020/01/tiktok_video.mp4)观看攻击演示视频。



## 0x01 技术细节

### <a class="reference-link" name="SMS%E9%93%BE%E6%8E%A5%E6%AC%BA%E8%AF%88"></a>SMS链接欺诈

在研究过程中，我们发现攻击者有可能以TikTok的身份向任意手机号码发送SMS消息。

TikTok[主页](http://www.tiktok.com/)上提供了一个功能，允许用户向自己发送一条SMS，以便下载该应用。

[![](https://p2.ssl.qhimg.com/t016e3238dbb7ce57a5.jpg)](https://p2.ssl.qhimg.com/t016e3238dbb7ce57a5.jpg)

如果攻击者希望向目标用户发送SMS消息，可以使用代理工具（如Burp Suite）抓取HTTP请求。请求中的`Mobile`参数包含待发送SMS消息的手机号码，`download_url`参数为SMS消息中显示的下载链接。

[![](https://p3.ssl.qhimg.com/t017e200bb87852258b.png)](https://p3.ssl.qhimg.com/t017e200bb87852258b.png)

官方正常的SMS消息如下：

[![](https://p3.ssl.qhimg.com/t01547a26d6f159b303.jpg)](https://p3.ssl.qhimg.com/t01547a26d6f159b303.jpg)

修改`download_url`参数后，攻击者可以构造出一个欺诈型SMS消息，其中包含攻击者选择的恶意链接。

包含恶意链接的欺诈型SMS消息如下图所示，这里我们使用`https://attacker.com`作为恶意链接来演示：

[![](https://p3.ssl.qhimg.com/t01493d3b733d628172.png)](https://p3.ssl.qhimg.com/t01493d3b733d628172.png)

可以看到伪造的SMS消息中包含`https://attacker.com`：

[![](https://p2.ssl.qhimg.com/t01744c8853281403a0.jpg)](https://p2.ssl.qhimg.com/t01744c8853281403a0.jpg)

### <a class="reference-link" name="%E6%B7%B1%E5%BA%A6%E9%93%BE%E6%8E%A5"></a>深度链接

在逆向分析Android版TikTok应用时，我们发现该应用包含一个“deep links”（深度链接）功能，可以通过浏览器链接调用应用中的`intent`。

该应用监听的`intent`所对应的url schema为`https://m.tiktok.com`及`musically://`。

[![](https://p2.ssl.qhimg.com/t012ad54aa61143278e.png)](https://p2.ssl.qhimg.com/t012ad54aa61143278e.png)

通过SMS链接伪造漏洞，攻击者可以发送包含上述schema的自定义链接。由于自定义链接中包含`url`参数，因此移动应用会打开一个`webview`（浏览器）窗口，通过移动应用访问`parameter`参数中指定的页面，并且发送的任何请求中都会带有用户的cookie。

这里我们以如下链接为例：

[![](https://p1.ssl.qhimg.com/t01e1bbe91bf9be483c.jpg)](https://p1.ssl.qhimg.com/t01e1bbe91bf9be483c.jpg)

解析深度链接的代码如下所示：

[![](https://p3.ssl.qhimg.com/t0102bba9d946338d68.jpg)](https://p3.ssl.qhimg.com/t0102bba9d946338d68.jpg)

该应用会打开一个webview（浏览器）窗口，访问`http://10.10.10.113:8000`，也就是攻击者控制的一个web服务器。

因此，攻击者有可能以用户身份发送请求。

### <a class="reference-link" name="%E5%9F%9F%E5%90%8D%E6%AD%A3%E5%88%99%E9%AA%8C%E8%AF%81"></a>域名正则验证

在研究过程中，我们发现攻击者有可能向受害者发送恶意链接，将受害者重定向到恶意网站。这种重定向攻击使攻击者有可能在未经用户许可的情况下发起[XSS](https://research.checkpoint.com/2020/tik-or-tok-is-tiktok-secure-enough/#XSS)、[CSRF](https://research.checkpoint.com/2020/tik-or-tok-is-tiktok-secure-enough/#CSRF)攻击，或者获取敏感数据。

当攻击者发送的登录链接派生自TikTok的域名（`https://login.tiktok.com`）时，就可能诱发重定向。

我们发现登录请求中可以包含HTTP GET参数`redirect_url`，比如在用户成功登录后，可以通过如下请求实现重定向：

```
https://login.tiktok.com/?redirect_url=https://www.tiktok.com
```

`redirection`参数会将用户重定向到TikTok所属域名的网页，TikTok采用如下正则表达式来验证域名是否满足要求（只在客户端验证）：

[![](https://p1.ssl.qhimg.com/t0123bbd76bed47f0f7.png)](https://p1.ssl.qhimg.com/t0123bbd76bed47f0f7.png)

[![](https://p4.ssl.qhimg.com/t01007d90cc6f33a95a.png)](https://p4.ssl.qhimg.com/t01007d90cc6f33a95a.png)

由于该正则表达式并没有正确验证`redirect_url`参数的值，因此重定向过程可能存在漏洞。如上所示，正则表达式会验证参数值是否以`tiktok.com`结尾，因此攻击者有很大的重定向空间。

比如，攻击者可以将用户重定向至`http://www.attacker-tiktok.com`网站，从而进一步利用前面提到的攻击方式。

[![](https://p3.ssl.qhimg.com/t0118fdb64a391cde8b.png)](https://p3.ssl.qhimg.com/t0118fdb64a391cde8b.png)

### <a class="reference-link" name="XSS"></a>XSS

进一步研究后，我们发现TikTok的某个子域名（`https://ads.tiktok.com`）存在XSS漏洞，攻击者可以将恶意脚本注入可信站点。

`ads`子域名包含一个帮助中心，用户可以了解如何在TikTok中创建并发布广告。帮助中心地址为`https://ads.tiktok.com/help/`，其中包含一个搜索漏洞。

XSS注入点位于搜索功能中。当攻击者执行搜索操作时，就会向web应用服务器发起HTTP GET请求，其中包含一个`q`参数，参数值为搜索的字符串。

正常的搜索过程如下所示，攻击者搜索`pwned`字符串：

```
https://ads.tiktok.com/help/search?q=pwned
```

[![](https://p2.ssl.qhimg.com/t0151cc118c5715eb08.png)](https://p2.ssl.qhimg.com/t0151cc118c5715eb08.png)

攻击者可以将JavaScript代码注入`q`参数中（注入的值经过URL编码）。

这里为了方便演示，我们可以弹出一个alert窗口，内容为`xss`：

```
https://ads.tiktok.com/help/search?q=%22%3Cscript%20src%20%3Djavascript%3Aalert%28%29%3E
```

[![](https://p1.ssl.qhimg.com/t0197721be4724cc9dc.png)](https://p1.ssl.qhimg.com/t0197721be4724cc9dc.png)



## 0x02 攻击场景

此时我们已经掌握了2个不同的缺陷：如果受害者点击了我们发送的链接，就能以该受害者身份执行JavaScript代码（参考前文的“SMS链接欺诈”）；以及重定向攻击（参考前文的“域名正则验证”），将用户重定向到恶意站点，执行JavaScript代码，使用受害者cookie向TikTok发送请求。

由于缺乏防御CSRF攻击的机制，因此我们可以执行JavaScript代码，未经受害者许可以其身份执行各种操作。

### <a class="reference-link" name="%E5%88%A0%E9%99%A4%E8%A7%86%E9%A2%91"></a>删除视频

我们可以向`https://api-t.tiktok.com/aweme/v1/aweme/delete/?aweme_id=video_id`发送HTTP GET请求，删除视频。

通过前文描述的JavaScript执行方式，我们可以指定`aweme_id`参数值（即视频id），发送HTTP GET请求，删除攻击者指定的视频。

例如，删除编号为`6755373615039991045`视频的请求如下图所示：

[![](https://p4.ssl.qhimg.com/t0184244774e111b816.png)](https://p4.ssl.qhimg.com/t0184244774e111b816.png)

服务端返回响应，表明视频已成功删除：

[![](https://p2.ssl.qhimg.com/t015ad7e7afcacdef25.png)](https://p2.ssl.qhimg.com/t015ad7e7afcacdef25.png)

### <a class="reference-link" name="%E5%88%9B%E5%BB%BA%E8%A7%86%E9%A2%91"></a>创建视频

为了在受害者feed流上创建视频，攻击者首先需要发送一个请求，在自己feed流上创建视频。视频创建请求会生成一个新的视频id，此时攻击者可以复制视频创建请求，然后使用前面描述的执行JavaScript的方法，配合上一步复制的视频创建请求，以受害者身份发送HTTP POST请求。

在受害者feed流上创建视频的请求如下所示：

[![](https://p1.ssl.qhimg.com/t017b706e7e5d776062.png)](https://p1.ssl.qhimg.com/t017b706e7e5d776062.png)

服务端返回响应，表示视频已成功创建。

[![](https://p3.ssl.qhimg.com/t0109632b96f04890dd.png)](https://p3.ssl.qhimg.com/t0109632b96f04890dd.png)

### <a class="reference-link" name="%E6%88%90%E4%B8%BA%E7%B2%89%E4%B8%9D"></a>成为粉丝

攻击者需要向受害者发送请求，等受害者同意后才能成为受害者的粉丝（follower）。

为了同意粉丝请求，攻击者可以使用前面提到的JavaScript执行方法，以受害者身份发送同意请求。

此时需要往如下路径发送一个HTTP POST请求：

```
https://api-m.tiktok.com/aweme/v1/commit/follow/request/approve
```

POST请求中包含一个`from_user_id`参数，该参数中包含希望成为粉丝的用户id。

攻击者可以将`from_user_id`参数值修改为自己的id，然后向TikTok服务器发送请求：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01340094bd18715141.png)

此时攻击者已成功成为受害者的粉丝：

[![](https://p2.ssl.qhimg.com/t017dae02c338dc3daf.png)](https://p2.ssl.qhimg.com/t017dae02c338dc3daf.png)

### <a class="reference-link" name="%E5%BC%80%E6%94%BE%E7%A7%81%E5%AF%86%E8%A7%86%E9%A2%91"></a>开放私密视频

为了将视频从私密模式变成公开模式，攻击者需要获取到视频id。当攻击者成为受害者粉丝后，就可以成功获取视频id。

一旦拿到私密视频的id，攻击者就能以受害者身份，发送HTTP GET请求来修改视频的隐私设置（通过前面提到的JavaScript执行方式）：

```
https://api-m.tiktok.com/aweme/v1/aweme/modify/visibility/?aweme_id=video_id&amp;type=1&amp;aid=1233&amp;mcc_mnc=42503
```

需要注意的是，`type=1`会将视频变成公共模式，而`type=2`会将视频变成私密模式。

如下图所示，攻击者可以通过HTTP GET请求，将id为`6755813399445261573`的视频从私密模式变成公共模式：

[![](https://p2.ssl.qhimg.com/t01a1cf6bbeb32c9108.png)](https://p2.ssl.qhimg.com/t01a1cf6bbeb32c9108.png)

服务端返回响应，表明视频模式已修改成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01436e3f1e5b731e7d.png)

### <a class="reference-link" name="%E8%8E%B7%E5%8F%96%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF"></a>获取敏感信息

继续研究后，我们发现可以通过XSS或者前面提到的方法来执行JavaScript代码，获取敏感信息。我们在`https://api-t.tiktok.com`及`https://api-m.tiktok.com`子域名中找到了几个API接口。

向这些API接口发送请求后，我们可以看到关于用户的一些敏感信息，包括邮箱地址、付款信息、生日等。

在尝试使用前面提到的JavaScript代码执行方法后，我们遇到了一个问题：CORS（Cross Origin Resource Sharing）机制以及SOP（Same Origin Policy）安全限制。

API子域名似乎只允许特定源（比如`www.tiktok.com`）来发送请求。例如，源自`https://cpr.checkpoint.com`的API请求如下：

[![](https://p1.ssl.qhimg.com/t01a1562af0e15aa5e8.png)](https://p1.ssl.qhimg.com/t01a1562af0e15aa5e8.png)

由于安全限制，服务端的响应如下：

[![](https://p0.ssl.qhimg.com/t0140610111cb40ac4f.png)](https://p0.ssl.qhimg.com/t0140610111cb40ac4f.png)

因此我们必须以某种方式绕过CORS及SOP安全机制，才能获取所需的敏感信息。

我们发现TikTok实现了一个非常规的JSONP回调，提供了从API服务器请求数据的方法，并且没有CORS及SOP限制！

绕过这些安全机制后，我们就可以向JSONP回调发送AJAX请求，窃取所有敏感信息，拿到经过JavaScript函数封装的JSON数据。

如下图所示，我们可以通过AJAX请求，获取与受害者钱包有关的所有敏感信息。请求中包含一个`callback`参数，参数值为待执行的JavaScript函数（`myCallBackMethod`）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016b3033bc1be8fda6.png)

从API获取到的数据如下所示，其中包含所有敏感信息。敏感信息可以进一步提取，发送到攻击者的服务器：

[![](https://p0.ssl.qhimg.com/t01eb6b14ca19f2893f.png)](https://p0.ssl.qhimg.com/t01eb6b14ca19f2893f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c48d6d51b90344de.png)



## 0x03 总结

本文分析了目前全世界最流行、最广泛使用的一款社交应用所存在的安全风险，这类风险的存在更加凸显我们对网络世界中隐私和数据安全的迫切需求。我们生活在数据之中，而数据泄露目前愈演愈烈，因此这是全球各家单位共同面对的一个难题。我们的数据存储在多个网络中，其中包含对自己而言最有价值的私密信息，因此保护数据不受侵害是我们共同的责任。
