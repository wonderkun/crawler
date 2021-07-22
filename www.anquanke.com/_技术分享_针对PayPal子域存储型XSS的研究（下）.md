> 原文链接: https://www.anquanke.com//post/id/87264 


# 【技术分享】针对PayPal子域存储型XSS的研究（下）


                                阅读量   
                                **93194**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：firstsight.me
                                <br>原文地址：[http://firstsight.me/fia07a53c4ec63d2b0d47fe27ea2645d82f8c98648/[ENG]%20PayPal%20-%20Turning%20Self-XSS%20into%20non-Self%20Stored-XSS%20via%20Authorization%20Issue.pdf](http://firstsight.me/fia07a53c4ec63d2b0d47fe27ea2645d82f8c98648/%5BENG%5D%20PayPal%20-%20Turning%20Self-XSS%20into%20non-Self%20Stored-XSS%20via%20Authorization%20Issue.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t012413a32f56afaa62.png)](https://p1.ssl.qhimg.com/t012413a32f56afaa62.png)

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**传送门**

****

[**【技术分享】针对PayPal子域存储型XSS的研究（上）**](http://bobao.360.cn/learning/detail/4706.html)

**<br>**

**写在前面的话**

在本系列文章的上集中，我们给大家介绍了PayPal品牌中心以及PayPal技术支持门户中存在的存储型跨站脚本漏洞。接下来，我们将会给大家介绍如何利用PayPal品牌中心站点中的XSS（跨站脚本）漏洞。在这个过程中，我们需要利用该站点所使用的身份验证机制中存在的安全问题，并利用“文件名注入”技术将Self-XSS转换为non-Self型的存储型XSS。<br>

如果你想了解更多相关内容，请访问作者的Twitter主页或通过电子邮箱与他联系。

Twitter：@YoKoAcc 电子邮箱：[yk@firstsight.me](mailto:yk@firstsight.me)



**PoC**

由于PayPal所存在的这个跨站脚本实际上是一种self-XSS，因此我们的PoC可能会跟其他类型的XSS有所不同。为了给大家进行比较完整的解释，我们会尝试使用一些简单的流程图来解释攻击的过程以及方法。

**针对PayPal技术支持门户的PoC**

现在，我们已经知道了这个门户网站中的验证机制存在安全问题。简单来说，这个问题将允许任意的匿名用户伪装成网站的已注册用户来提交内容，而攻击者只需要知道一个“已注册”的电子邮箱ID就可以了。

接下来，攻击者可以利用验证机制的漏洞来创建新的任务单，并上传恶意.svg文件来触发XSS漏洞。由于这里存在的是存储型跨站脚本漏洞，因此攻击者需要目标用户打开他们所创建的任务单才能够成功发动攻击。有趣的是，该网站的任务单提交功能并没有部署任何的验证码机制，因此攻击者就可以通过暴力破解的方式来自动化地测试邮件ID列表了。

注意：这种方法也许是PayPal经过深思熟虑之后所设计出来的一种企业业务流程，所以他们目前还没有对这种任务单提交方法进行修改和优化，他们目前只修复了其中的跨站脚本漏洞。

在直接介绍攻击PoC之前，我们需要简单了解一下攻击的整个流程。下面这张图片显示的是攻击者用于欺骗目标用户所使用的方法。在这种场景中，攻击者可以利用“无需登录即可提交任务单”的方法并绕过网站的文件上传保护来上传恶意的.svg文件（SVG是一种用XML定义的语言，用来描述二维矢量及矢量/栅格图形。SVG可以算是目前最最火热的图像文件格式了，它的英文全称为Scalable Vector Graphics，意思为可缩放的矢量图形。）。

攻击流程图如下所示：

[![](https://p0.ssl.qhimg.com/t019f70b3574d07daf9.png)](https://p0.ssl.qhimg.com/t019f70b3574d07daf9.png)

需要注意的是，在这种场景下的攻击过程中，攻击者所填入的电子邮箱地址必须是真实存在的目标用户PayPal技术支持账号（电子邮箱，可通过暴力破解攻击获取）。

填写完所有的内容之后，接下来攻击者需要上传包含了客户端脚本的恶意.svg文件，下面给出的是客户端脚本代码PoC：



```
&lt;?xml        version="1.0"  encoding="UTF-8"         standalone="yes"?&gt;
&lt;svg onload="window.location='http://www.google.com'"
xmlns="http://www.w3.org/2000/svg"&gt;&lt;/svg&gt;
```

需要注意的是，由于网站不允许用户上传后缀为.svg的文件，因此我们在上传之前还需要绕过客户端的保护机制，此时攻击者可以将.svg修改为.png之类的网站所允许的后缀来实现绕过：<br>

[![](https://p4.ssl.qhimg.com/t019c0ad141dff2bcca.png)](https://p4.ssl.qhimg.com/t019c0ad141dff2bcca.png)

[![](https://p5.ssl.qhimg.com/t01ebd9dac411d4121a.png)](https://p5.ssl.qhimg.com/t01ebd9dac411d4121a.png)

当我们选择了包含客户端脚本代码的恶意.png文件之后，接下来我们要做的就是在将其发送给服务器之前拦截网站请求。在拦截下来的请求信息中，我们可以修改content-type的内容，并将后缀名以及文件格式修改为.svg。

[![](https://p5.ssl.qhimg.com/t0167d14164aaa9dab0.png)](https://p5.ssl.qhimg.com/t0167d14164aaa9dab0.png)

修改完成之后，我们就可以将拦截下来的请求转发出去了。当请求转发成功之后，如果.svg文件上传成功，那么我们就可以得到网站所返回的“上传成功”提示。具体如下图所示：

[![](https://p0.ssl.qhimg.com/t0168ee6f4a047d2068.png)](https://p0.ssl.qhimg.com/t0168ee6f4a047d2068.png)

最后，攻击者只需要等待目标用户打开任务单以及之前所上传的恶意.svg文件即可。当.svg文件被打开之后，网站中的跨站脚本漏洞（存储型XSS）将会被触发。

**针对PayPal品牌中心的PoC**

与之前介绍的一样，PayPal品牌中心的网页中存在一个验证问题。换句话来说，任何一位匿名用户都可以向另一名已注册的PayPal用户发送任务单，而他们只需要知道目标用户的已注册邮箱ID就可以了。

PayPal品牌中心门户的注册流程以及任务单提交流程：

[![](https://p3.ssl.qhimg.com/t019f535bc1509c6b83.png)](https://p3.ssl.qhimg.com/t019f535bc1509c6b83.png)

上图所示的流程可以主要分为以下两种场景，即“账号不存在”和“账号存在”这两种情况。

1.       如果账号存在，则注册流程将会跳转到“在不知道用户密码的情况下提交任务单”功能。

2.       如果账号不存在，则注册流程将会按照正常规则进行处理（完成注册）。

在这一步骤中，我们将要使用的攻击流程与之前针对PayPal技术支持门户的攻击流程一样。下图所示的就是攻击者用于欺骗目标用户的方法。在这种场景下，攻击者需要利用“无需登录提交任务单”的方法以及“先上传任意文件之后再修改文件名”来触发网站中存在的跨站脚本漏洞。

针对PayPal品牌中心门户的攻击流程图：

[![](https://p3.ssl.qhimg.com/t01e7513562872d9c28.png)](https://p3.ssl.qhimg.com/t01e7513562872d9c28.png)

跟之前“无需登录提交任务单”的方法一样，攻击者所填写的邮箱地址必须是真实存在的目标用户PayPal品牌中心账号。

网页表单中的信息全部填写完成之后，攻击者需要拦截网站给服务器发送的请求信息，并将上传的文件名修改为恶意脚本文件，这样才能在客户端触发漏洞。为了演示方便，我们可以使用下面给出的Payload来触发一次警告弹窗：

```
&gt;&lt;img       src=x         onerror=prompt(1)&gt;
```

但是，由于这种弹窗式的Payload还不足以证明这种安全问题的严重等级，因此我们还需要尝试修改Payload，至少要实现URL重定向或下载一个程序才够。但是在这种场景中，我们又发现了另一个问题，即该门户网站中的文件名中不允许出现以下特殊字符：“. " / =”（点号、双引号、反斜杠和等号）。

所以，我们需要将Payload修改成以下形式并尝试绕过这种特殊字符限制：

```
&lt;img src=a onerror=document.location="http://google.com"&gt;
```

下面给出的就是我们拦截下请求之后最终的修改情况：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01562d787c5e103b67.png)

在攻击的最后阶段中，攻击者只需要等待目标用户打开任务单即可。当任务单打开之后，网页将会执行注入在文件名中的恶意脚本代码。

[![](https://p0.ssl.qhimg.com/t0132f57dcde0121265.png)](https://p0.ssl.qhimg.com/t0132f57dcde0121265.png)



**后话**

其实，对于PayPal这种商业支付领域的领军企业来说，用户的信息安全以及资金安全肯定是首要的。我个人认为，对于某些大规模的网站而言，需要保护的东西实在是太多了，而安全团队也并不能百分之百地清楚网站中每一个应用程序的具体运行流程。

与此同时，像Facebook和Twitter这样的门户网站一样，PayPal的安全团队每天都会接收到来自全世界各个地区的研究人员所发过来的漏洞报告，因此这也给企业的安全团队带来了巨大的工作量。因此，当各位想要提交漏洞报告的时候，请一定要保证报告内容的完整性，并提供可行的PoC以及漏洞利用细节，最好还可以附带演示视频。
