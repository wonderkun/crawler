> 原文链接: https://www.anquanke.com//post/id/157149 


# Hangouts Chat聊天工具从任意跳转到代码执行漏洞


                                阅读量   
                                **111182**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Michał Bentkowski，文章来源：bentkowski.info
                                <br>原文地址：[https://blog.bentkowski.info/2018/07/vulnerability-in-hangouts-chat-aka-how.html?view=sidebar](https://blog.bentkowski.info/2018/07/vulnerability-in-hangouts-chat-aka-how.html?view=sidebar)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0179fdef19ec63f564.jpg)](https://p3.ssl.qhimg.com/t0179fdef19ec63f564.jpg)

几个月前谷歌发布了一个叫做Hangouts Chat的对标Slack的聊天工具。Hangouts既可以在浏览器用，也可以下载桌面版或者手机版。

我做了一些调研，决定还是把重心放在桌面应用上。



## Hangout Chat桌面版

安装完以后，我发现Hangouts的桌面版其实就是一个[Electron](https://sites.google.com/site/bughunteruniversity/nonvuln/open-redirect)桌面应用，就是把`https://chat.google.com.web`应用的web版嵌入一个桌面应用。<br>[![](https://p4.ssl.qhimg.com/t0175196b76d5526803.png)](https://p4.ssl.qhimg.com/t0175196b76d5526803.png)

所以在Electron应用上测试安全问题就和web测试差不多了，两者最大的区别是，web版本的应用在显示时会有一个地址栏，地址栏会告诉用户当前访问的网站是不是可以网站，这有几句Michał Zalewski 写的关于web的话：

**从本质上来说，地址栏中的域名URL是web应用中最重要的标识，用户可以很直观迅速的区分他们信任的网站和其他网站。**

然而在Electron应用这种以浏览器为底层的应用中并没有地址栏，也就是说用户必须完全相信应用本身提供的是来自`https://chat.google.com`的服务，因为没有地址栏，就无法标识服务是官方的还是第三方的。

因此，我想我应该先在应用中找到一个可以跳转到外站的接口，这样就可以造成一个可信度比较高的钓鱼。用户会被攻击者重定向到一个外部网站，可以制作一个和谷歌登录很相似的登录面板，因为没有地址栏，很难分辨登录框是假的。



## 寻找重定向

所以我从最简单的地方开始，先找到一个可以重定向到其他域的地方，先试试在聊天内容中加一个外部域名，点击之后发现只是打开了默认浏览器。

[![](https://p2.ssl.qhimg.com/t013d8973d303f2af84.gif)](https://p2.ssl.qhimg.com/t013d8973d303f2af84.gif)

恩，先不要放弃，经过研究，我发现如果链接是到`chat.google.com`官网的URL，在Electron应用中是直接打开的。另外，如果返回状态码不是200，当用户单击链接(例如：`https：//chat.google.com/webChannel/Events`)时，必须重新启动应用程序，因为没有“回退”按钮；)<br>[![](https://p3.ssl.qhimg.com/t013609004fbc626c27.gif)](https://p3.ssl.qhimg.com/t013609004fbc626c27.gif)

一个绕过URL访问规则的常见方法是强制使用重定向，即把请求的响应码手动改为3XX。我发现当导航到一个不存在的URL时(比如`https://chat.google.com/test123`)，`chat.google.com`会被302重定向到`https://chat.google.com/u/0/?hasBeenRedirected=true`这个链接，所以我在Burp里自定义了一个替换规则，响应头中包含`hasBeenRedirected=true`的URL，都替换为sekurak.pl 这个地址。<br>[![](https://p1.ssl.qhimg.com/t0132b52694083332e3.png)](https://p1.ssl.qhimg.com/t0132b52694083332e3.png)

Hangouts响应如下：<br>[![](https://p2.ssl.qhimg.com/t01fbe255ed7a656624.gif)](https://p2.ssl.qhimg.com/t01fbe255ed7a656624.gif)

神奇的事情发生了！这证明了在Hangouts的桌面版应用聊天窗口中，可以利用302跳转到任意外部网站。

现在万事俱备，只缺一个在`chat.google.com`网站上真实存在的任意重定向了。



## 任意重定向

在我看来，任意重定向大部分情况下是一种被高估了的漏洞，引用一下在Google的[Bug Hunter University](https://sites.google.com/site/bughunteruniversity/nonvuln/open-redirect)中的定义：

**任意重定向是可以从Google链接跳转到由攻击者构造的任意站点，一些安全论坛的成员认为，任意重定向容易被用来钓鱼，因为用户比较相信鼠标悬停时展示的地址栏地址，跳转发生后的链接往往不会被再次检查。**

我也同意这种观点，用户一般来说只能根据地址栏判断安全指标。但这一点在Electron应用中就完全没用了，Electron应用是没有地址栏的，因此用户没办法确认正在访问的网站的真实性，在这种场景下这显然是个脆弱点。

在`https://chat.google.com`查找任意重定向漏洞比我预想中要更容易一些。我发现`https://chat.google.com/accounts`路径下的所有URL都会跳转到`accounts.google.com`，比如`https://chat.google.com/accounts/random-url`这个，点击之后会跳转到`https://accounts.google.com/random-url`这个链接。

重定向到accounts.google.com只是第一步，但实际上更重要的是在accounts.google.com有一个公开的重定向(twitter账号 [博客文章](https://vagmour.eu/google-open-url-redirection/)中的细节，我基本确定可以重定向到我自己的域名，只需要在主机名后加上/_ah/conflogin的路径。

最后组合好的任意跳转链接如下：

```
https://chat.google.com/accounts/ServiceLogin?continue=https://appengine.google.com/_ah/conflogin?continue=http://bentkowski.info/&amp;service=ah
```

然后我准备了一个和谷歌登录基本一样的登录框，这就是一个让用户非常容易上钩的钓鱼页面了。<br>[![](https://p3.ssl.qhimg.com/t01570f98a761a7e419.gif)](https://p3.ssl.qhimg.com/t01570f98a761a7e419.gif)

因为没有地址栏，用户不会知道这是一个假的登录页面，当然同样的情况在浏览器中就没有这样的效果了：<br>[![](https://p4.ssl.qhimg.com/t016f060fef63f7329f.png)](https://p4.ssl.qhimg.com/t016f060fef63f7329f.png)



## 总结

Electron应用因为没有浏览器地址栏，很容易引发由任意重定向造成的钓鱼问题，如果你要开发一个Electron的应用，务必要确保在窗口中不能被重定向到外部站点。

如果你正在使用谷歌的Hangouts Chat聊天工具，务必要升级到最新版本，几天前官方已经发布了新的补丁。

谷歌对这个bug也是很大方，我最终拿到了$7500，主要是因为引起了代码执行。一开始我无法证明可以命令执行，多亏了[Matt Austin](https://twitter.com/mattaustin)在推特中的一篇[推文](https://twitter.com/mattaustin/status/1022648925902200832)证明了确实可以代码执行，感谢Matt!

后续更新：一开始的标题是“Hangouts Chat中的漏洞也说明了Enectron应用使任意重定向问题再次爆发”，这引发了一些媒体的点击量，为避免争议所以还是改成了比较中立的标题。
