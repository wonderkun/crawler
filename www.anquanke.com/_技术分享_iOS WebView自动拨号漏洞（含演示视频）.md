> 原文链接: https://www.anquanke.com//post/id/84883 


# 【技术分享】iOS WebView自动拨号漏洞（含演示视频）


                                阅读量   
                                **79986**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：mulliner
                                <br>原文地址：[https://www.mulliner.org/blog/blosxom.cgi/security/ios_webview_auto_dialer.html](https://www.mulliner.org/blog/blosxom.cgi/security/ios_webview_auto_dialer.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0123d48d1758cdcac6.png)](https://p4.ssl.qhimg.com/t0123d48d1758cdcac6.png)

****

**翻译：**[**WisFree**](http://bobao.360.cn/member/contribute?uid=2606963099)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**漏洞概述**

安全研究专家发现，iOS的WebViews组件中存在漏洞，攻击者或可利用这个漏洞来控制目标手机进行自动拨号（号码可控制）。在这种攻击场景中，攻击者可以在短时间内屏蔽用户手机的图形操作界面（UI），并通过这种方法防止用户挂断通话。这是一个应用程序漏洞，该漏洞主要是由操作系统框架层的设计缺陷所导致的。需要注意的是，这个漏洞的利用方法非常简单，攻击者可以轻易地利用这个漏洞实施攻击，所以各位App开发人员应该尽快修复应用代码中存在的问题。安全研究人员目前已经确认，Twitter和LinkedIn的iOS端App存在这个漏洞，但是还有很多其他的App同样也会存在这个问题。

<br>

**针对911报警电话的拒绝服务攻击**

大约在一个星期之前，我看到了一篇文章，这篇文章大致描述的是：有一个人创建了一个恶意Web页面，当用户访问这个页面时，用户的iPhone手机将会自动拨打911报警号码，从而实现了对911报警电话的拒绝服务攻击。看到这篇报道之后，我立刻想到了我在2008年10月份提交给苹果公司的一个漏洞[[传送门](https://archive.cert.uni-stuttgart.de/bugtraq/2009/06/msg00190.html)]，攻击者所使用的这个漏洞肯定跟手机调用拨号功能的TEL URI有关。但是我并不认为攻击者利用的是我之前所报告过的那个漏洞，所以我打算深入调查一下。

<br>

**漏洞的严重性**

攻击者可以在App中嵌入一条恶意链接，当用户点击这条链接之后手机便会自动拨打某个电话号码。如果你觉得这并不是什么大问题的话，请你再考虑一下。针对911报警电话的拒绝服务攻击已经非常恐怖了，而攻击者甚至还可以通过让你的手机自动拨打付费电话来谋取巨额利益。除此之外，犯罪分子还可以控制目标手机拨打他的电话，这样一来犯罪分子便获取到了目标用户的手机号码。所有的这一切都是你不希望看到的。

于是我打算对iOS版的Twitter App进行分析。我在很短的时间内就制作出了一个可以正常工作的自动拨号程序，其简单程度令我感到震惊。我一开始还以为这是我之前提交给苹果公司的那个漏洞，但我在仔细研究过后发现，因为攻击者在攻击过程中使用了大量的JavaScript脚本和各种弹出窗口，所以这应该是另一个漏洞，至少这个漏洞的触发机理与之前的不同。在此之前，我只需要一行HTML代码（一个指向TEL URL的meta-refresh标签）就可以触发那个漏洞了，所以我打算通过Twitter的漏洞奖励计划将该漏洞上报给Twitter公司。我此前从未参与过任何的漏洞奖励计划，所以我觉得这也是一种不错的经历。当然了，Twitter在几天之后便确认了这个漏洞，然后也给我支付了漏洞奖金。

[![](https://p1.ssl.qhimg.com/t01d6fe2603a11a13bf.png)](https://p1.ssl.qhimg.com/t01d6fe2603a11a13bf.png)

在11月7日，我更新了提交给Twitter的漏洞报告，我在其中添加了关于UI屏蔽的问题，并且还上传了演示视频。但是Twitter却在没有提供任何其他评论的情况下直接关闭了我所提交的漏洞，因为他们认为这个问题与我之前提交的漏洞重复了。但我认为，Twitter应该表现得更加“绅士”一些，至少应该对我们这些利用业余休息时间帮他们挖漏洞的人要心存感激。所以我决定，出于他们对我的“无礼”，我打算将该漏洞的细节信息公布出来。

<br>

**漏洞分析**

我在进行了深入分析之后发现，使用WebViews来显示内容的iOS应用普遍都存在这个问题。为了验证我的想法，我对我手机中已经安装了的几款热门应用进行了测试。包含漏洞的应用首先要给用户提供一条Web链接，只有当目标Web页面在应用程序的WebView中打开时，用户才会受到攻击。如果恶意链接在类似Safari或Chrome之类的移动端浏览器中打开的话，用户是不会受该漏洞影响的。

考虑到LinkedIn是商业类的社交媒体软件，所以我一开始测试的是LinkedIn的iOS端App。用户可以用这款App发送信息或者更新状态，而更新中通常会包含文字和链接。我发布了一条链接，然后点击了这条链接。果然不出我所料，点击之后我的手机便开始拨打我的另外一个号码了。（演示视频在下方）

[![](https://p4.ssl.qhimg.com/t019170d7c854d0e8d8.png)](https://p4.ssl.qhimg.com/t019170d7c854d0e8d8.png)

于是我打算将该漏洞上报给LinkedIn，而且他们的确也有相应的漏洞奖励计划。但不幸的是，LinkedIn的漏洞奖励计划是不对外开放的，只有之前提交过漏洞的人才能参加这个计划。我努力了一阵之后，结果是徒劳无功。在我思考片刻之后，我决定不提交给LinkedIn了，我要公开这个漏洞。毕竟现在已经是2016年了，他们既然不打算将我列为漏洞奖励对象的话，我尊重他们的选择。不过通常情况下，我是不会直接将漏洞曝光的…

<br>

**漏洞触发机理**

我记得我在2008年提交那个漏洞的时候，附带了相应的PoC。而我发现，这个PoC现在竟然在Twitter和LinkedIn的App上仍然奏效。先回顾一下，当时我们可以通过访问一个网站（重定向至手机的TEL URL）来触发这个漏洞，并控制目标手机来拨打电话。实现TEL URL重定向的方法有很多，例如http-meta refresh、iframe、 设置document.location、window.location、或者HTTP重定向。这些方法都可以直接实现拨打电话。当然了，用户可以在屏幕中看到手机所拨打的电话号码，他们也可以直接按下“挂断”键来终止这通电话。但是能够实现自动拨打电话就已经非常糟糕了，不明真相的群众看到这种情况肯定也会一脸懵。

需要注意的是，在我利用2008年所提交的那个漏洞时，我可以屏蔽用户手机的UI界面，虽然只能屏蔽几秒钟，但这也足够防止用户挂断通话了。所以我打算将这个小技巧用到这个漏洞上来，而这个技巧确实可以让iOS操作系统在拨号的过程中打开另外一个应用程序。实现方法也很简单，你只需要通过打开一个URL地址就可以让iOS运行另外一个应用程序了。实际上，你只需要绑定一个URI，你就可以运行任何一个iOS应用程序了。

当时，我使用了一个SMS URL（带有一个非常长的电话号码）来屏蔽UI线程。在我看来，漏洞存在的主要原因是IPC子系统无法正常地将这些上千字节的URL数据转移至应用程序中，而应用程序也不希望接收到这样的URL。我的PoC代码如下图所示，我在攻击代码中使用了meta-refresh标签和window.location。我设置的延迟时间为1.3秒，这样就可以保证我的拨号器可以首先得到运行。这个延迟时间不能太长，否则WebView就不会通过URL来启动短信App了。所以时间必须设置得恰到好处。

[![](https://p4.ssl.qhimg.com/t01de465e8cf8f26f77.png)](https://p4.ssl.qhimg.com/t01de465e8cf8f26f77.png)

<br>

**漏洞触发演示**

我在下方给大家提供了两个攻击演示视频。你可以清楚地看到手机的UI界面在短时间内是无法响应用户操作的。在这段时间内，电话已经拨通了，尤其是某些付费电话。

**演示视频一：**



**演示视频二：**



<br>

**正常App的拨号操作**

通常情况下，一款合法的App在执行某个URL之前，首先会对其进行检测，然后再弹出对话框。当用户同意之后，相应的App才会被启动。如下图所示：

[![](https://p1.ssl.qhimg.com/t019b67ea0dd6cb10a1.png)](https://p1.ssl.qhimg.com/t019b67ea0dd6cb10a1.png)

移动端的Safari浏览器在拨打苹果服务电话之前，也会提醒用户。这才是一款合法App应有的表现！

[![](https://p3.ssl.qhimg.com/t013d7528087e7a4e59.png)](https://p3.ssl.qhimg.com/t013d7528087e7a4e59.png)

Dropbox也会在拨打电话之前给用户提示，但是并没有显示电话号码。不过，这也总好过什么也不提示吧！

[![](https://p3.ssl.qhimg.com/t019b268cf61aaffed6.png)](https://p3.ssl.qhimg.com/t019b268cf61aaffed6.png)

<br>

**总结**

苹果的开发者们应该立刻审查自己的App是否会受到这个漏洞的影响，如果有的话，请立刻修复相应的问题。

<br>

**参考资料**

1. [http://news.softpedia.com/news/bug-bounty-hunter-launches-accidental-ddos-on-911-systems-via-ios-bug-509738.shtml](http://news.softpedia.com/news/bug-bounty-hunter-launches-accidental-ddos-on-911-systems-via-ios-bug-509738.shtml)

2. [http://arstechnica.com/security/2016/10/teen-arrested-for-iphone-hack-that-threatened-emergency-911-system/](http://arstechnica.com/security/2016/10/teen-arrested-for-iphone-hack-that-threatened-emergency-911-system/)

3. [https://archive.cert.uni-stuttgart.de/bugtraq/2009/06/msg00190.html](https://archive.cert.uni-stuttgart.de/bugtraq/2009/06/msg00190.html)

4. [https://tools.ietf.org/html/rfc2806](https://tools.ietf.org/html/rfc2806)

5. [https://tools.ietf.org/html/rfc3966](https://tools.ietf.org/html/rfc3966)
