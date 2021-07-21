> 原文链接: https://www.anquanke.com//post/id/86232 


# 【技术分享】从JS文件中发现『认证绕过』漏洞


                                阅读量   
                                **107459**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blogspot.com
                                <br>原文地址：[http://c0rni3sm.blogspot.com/2017/06/from-js-to-another-js-files-lead-to.html](http://c0rni3sm.blogspot.com/2017/06/from-js-to-another-js-files-lead-to.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01aa2c2ebe5c3a41af.jpg)](https://p4.ssl.qhimg.com/t01aa2c2ebe5c3a41af.jpg)



翻译：[**h4d35**](http://bobao.360.cn/member/contribute?uid=1630860495)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

本篇文章主要介绍了在一次漏洞悬赏项目中如何利用配置错误挖到一个认证绕过漏洞。

<br>

**从JS文件中发现认证绕过漏洞**

本文内容源自一个私有漏洞赏金计划。在这个漏洞计划中，接受的漏洞范围限于目标网站少数几个公开的功能。基于前期发现的问题（当我被邀请进这个计划时，其他人一共提交了5个漏洞），似乎很难再挖到新的漏洞。同时，在赏金详情中提到了这样一句话：

如果你成功进入管理页面，请立即报告，请勿在/admin中进行进一步的测试。

然而，目标网站中存在一个仅限于未认证和未经授权的用户访问的管理页面。当我们访问/login或/admin时会跳转到https://bountysite.com/admin/dashboard?redirect=/。

对登录页面进行暴力破解也许是一个可行方案，但是我并不喜欢这种方式。看一下网页源码，没什么有用的内容。于是我开始查看目标网站的结构。似乎目标网站的JS文件都放在少数几个文件夹中，如/lib、/js、/application等。

有意思！

祭出神器BurpSuite，使用Intruder跑一下看能否在上述文件夹中找到任何可访问的JS文件。将攻击点设置为https://bountysite.com/admin/dashboard/js/*attack*.js。注意，不要忘记.js扩展名，这样如果文件能够访问则返回200响应。确实有意思！因为我找到了一些可访问的JS文件，其中一个文件是/login.js。

访问这个JS文件https://bountysite.com/admin/dashboard/js/login.js，请求被重定向至管理页面:) 。但是，我并没有查看该文件的权限，只能看到部分接口信息。

[![](https://p3.ssl.qhimg.com/t016d458b9db740a087.png)](https://p3.ssl.qhimg.com/t016d458b9db740a087.png)

但是我并没有就此止步。这看起来很奇怪，为什么我访问一个.js文件却被作为HTML加载了呢？经过一番探查，终于发现，我能够访问管理页面的原因在于*login*。是的，只要在请求路径/dashboard/后的字符串中含有*login*（除了'login'，这只会使我回到登录页面），请求就会跳转到这个管理接口，但是却没有正确的授权。

我继续对这个受限的管理接口进行了进一步的测试。再一次查看了页面源码，试着搞清楚网站结构。在这个管理接口中，有其他一些JS文件能够帮助我理解管理员是如何执行操作的。一些管理操作需要一个有效的令牌。我试着使用从一个JS文件中泄露的令牌执行相关管理操作，然并卵。请求还是被重定向到了登录页面。我发现另外一个真实存在的路径中也部署了一些内容，那就是/dashboard/controllers/*.php。

再一次祭出BurpSuite，使用Intruder检查一下是否存在可以从此处访问的其他任何路径。第二次Intruder的结果是，我发现几乎不存在其他无需授权即可访问的路径。这是基于服务器返回的500或者200响应得出的结论。

[![](https://p3.ssl.qhimg.com/t01931977b0917ea7bd.png)](https://p3.ssl.qhimg.com/t01931977b0917ea7bd.png)

回到我在上一步侦察中了解到的网站结构中，我发现这些路径是在/controllers中定义的，通过/dashboard/*here*/进行访问。但是直接访问这些路径会跳转到登录页面，似乎网站对Session检查得还挺严格。此时我又累又困，几乎都打算放弃了，但是我想最后再试一把。如果我利用与访问管理页面相同的方法去执行这些管理操作会怎么样呢？很有趣，高潮来了:) 我能够做到这一点。

通过访问/dashboard/photography/loginx，请求跳转到了Admin Photography页面，并且拥有完整的权限！

[![](https://p2.ssl.qhimg.com/t01ad5f6ca498ba80d8.png)](https://p2.ssl.qhimg.com/t01ad5f6ca498ba80d8.png)

从这里开始，我能够执行和访问/dashboard/*路径下的所有操作和目录，这些地方充满了诸如SQL注入、XSS、文件上传、公开重定向等漏洞。但是，我没有继续深入测试，因为这些都不在赏金计划之内，根据计划要求，一旦突破管理授权限制，应立即报告问题。此外，根据管理页面显示的调试错误信息可知，我之所以能够访问到管理页面，是因为应用程序在/dashboard/controllers/*文件中存在错误配置。期望达到的效果是：只要请求链接中出现*login*，就重定向至主登录页面，然而，实际情况并不如人所愿。

<br>

**后记**

总之，这是有趣的一天！我拿到了这个漏洞赏金计划最大金额的奖励。
