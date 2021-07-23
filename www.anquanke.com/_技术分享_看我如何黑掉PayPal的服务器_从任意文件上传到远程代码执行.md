> 原文链接: https://www.anquanke.com//post/id/86477 


# 【技术分享】看我如何黑掉PayPal的服务器：从任意文件上传到远程代码执行


                                阅读量   
                                **102893**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentestbegins.com
                                <br>原文地址：[http://blog.pentestbegins.com/2017/07/21/hacking-into-paypal-server-remote-code-execution-2017/](http://blog.pentestbegins.com/2017/07/21/hacking-into-paypal-server-remote-code-execution-2017/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01c4747922590177a2.jpg)](https://p2.ssl.qhimg.com/t01c4747922590177a2.jpg)

<br>

****

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：180RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**写在前面的话**

各位同学大家好，我知道大家在看到本文的标题之后肯定会忍不住点进来，在这篇文章中我将给大家描述我是怎样入侵PayPal服务器的，这是一个任意文件上传漏洞，而这个漏洞将允许我在PayPal的服务器上实现远程代码执行。

[![](https://p2.ssl.qhimg.com/t01936fcb00408cc97f.png)](https://p2.ssl.qhimg.com/t01936fcb00408cc97f.png)

相信我，设计这个漏洞的PoC其实并不是一件多么困难的事情，唯一一件让我感到幸运的事情就是我竟然真的可以找到无法抵御这种攻击的域名。

接下来，开始我们的正题！

<br>

**漏洞的发现过程**

在之前的一篇[文章](http://blog.pentestbegins.com/2017/07/05/my-oscp-certification-journey-2017/)中，我跟大家介绍了我是如何破解OSCP证书的，整个破解过程的确非常艰难，大概花了我四个多月的时间吧…但是你懂的，不去花时间花精力挖漏洞的话，口袋里可就没钱用了。

对于一个普通人来说，周末无非就是喝酒以及各种各样的Party。运气好的可能还有个女朋友可以约约会，运气不好的估计就只能在家看电视剧了（强推一波《权力的游戏》）。

[![](https://p0.ssl.qhimg.com/t0174b45ee29e528504.png)](https://p0.ssl.qhimg.com/t0174b45ee29e528504.png)

但对于我这样的人来说，我会在周末的时候看一些博客或者油管视频。有一次我找到了一些关于PayPal的文章，然后打开了Burp（关闭了拦截器）并访问了PayPal的漏洞奖励计划页面，于是我发现了如下图所示的内容：

[![](https://p3.ssl.qhimg.com/t012a38f98126dc0dac.png)](https://p3.ssl.qhimg.com/t012a38f98126dc0dac.png)

上图显示的是我访问http://paypal.com/bugbounty/时服务器所返回的响应信息，仔细分析之后我发现了网站返回信息的响应头"Content-Security Policy"中包含有一串PayPal的域名。其中有一个域名是https://*.paypalcorp.com，而这个域名吸引了我的注意。与之前一样，我在挖洞的时候喜欢找出目标站点尽可能多的可用子域名，因为这些子域名站点中很可能会存在一些被管理人员所忽略的安全问题。

如果要枚举目标站点的子域名，我推荐你使用Subbrute、Knockpy和enumall等工具，而且我平时也都会用到这些工具，但是我这一次偷了个懒，我直接使用了VirusTotal来枚举子域名，子域名列表信息请点击【[这里](https://www.virustotal.com/en/domain/paypalcorp.com/information/)】获取。

将子域名列表拷贝到本地文件中，然后运行命令"dig -f paypal +noall +answer"来查看每一个子域名最终所指向的服务器IP地址：

[![](https://p4.ssl.qhimg.com/t01a76b6387e1ac8bd6.png)](https://p4.ssl.qhimg.com/t01a76b6387e1ac8bd6.png)

其中有一个子域名为"brandpermission.paypalcorp.com" ，它指向的是站点 https://www.paypal-brandcentral.com/。这个站点是PayPal的品牌中心，其实也是PayPal提供给厂商、供应商以及合作伙伴的一个ticket在线支持系统，他们可以在这个网站上申请与PalPal合作，然后上传自己品牌的Logo、图片或其他一些相关资料。

我相信当任何一个Bug Hunter看到网站的文件上传功能之后，眼睛都会放光吧？

[![](https://p5.ssl.qhimg.com/t01c8a3ae6562dda4f9.jpg)](https://p5.ssl.qhimg.com/t01c8a3ae6562dda4f9.jpg)

于是乎，我创建了一张虚拟的ticket，然后上传了一个名叫“finished.jpg”的图片文件，系统将其以“finished__thumb.jpg”存储在了下面这个目录之中：

"/content/helpdesk/368/867/finishedthumb.jpg" 

“finishedthumb.jpg”是系统在目录"/867/"中新创建的文件，吓得我赶紧去查看这个文件还是不是我之前上传的那个原始文件。幸运的是，之前上传的原始文件“finished.jpg”同样也在这个目录中。

接下来，我对这个Web应用的上传文件处理流程以及文件/文件夹的命名规则进行了深入分析，我发现上述链接中的"368"目录其实就是我们所创建的ticket编号（ID），而"867"是文件夹ID，所有与这个ticket相关的模板文件和图片等资源都会保存在这个目录下。

了解到这些东西之后，我又用同样的方法创建了另一份ticket，我发现系统用按顺序递增的方式创建了ticket ID和文件ID。创建完成之后，这一次我选择上传一个".php"后缀名的文件，其中包含有一行命令执行脚本代码：

[![](https://p3.ssl.qhimg.com/t017a3b60856b995e21.png)](https://p3.ssl.qhimg.com/t017a3b60856b995e21.png)

这一次服务器返回的响应码为302（200意味着请求成功），根据Web应用的反应来看，这意味着服务器端并没有对用户所上传的文件类型和文件内容的有效性进行验证。非常好！看来漏洞唾手可得了！

[![](https://p5.ssl.qhimg.com/t01cb26265d81837e01.png)](https://p5.ssl.qhimg.com/t01cb26265d81837e01.png)

需要注意的是，如果你上传的是一个php文件，那么我们将无法查看到这个php文件在服务器端的保存路径，我们只能看到ticket编号。

<br>

**那接下来我们应该干什么呢？**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018c4492330dff2a39.png)

当我了解到ticket ID为"/366/"之后，也就知道了我们所上传的文件将会保存在哪一个文件目录下。但由于我们无法像查看图片文件一样去查看之前所上传的php文件的存储位置，所以我们没有办法得知具体的文件夹ID。

我们现在所知道的是，当我们上传一个名为"example.jpg"的文件之后，服务器会在相同目录下生成一个"example_thumb.jpg"文件。那么我们如果上传的php文件名叫"success.php"的话，那么服务器是否会在相同目录下生成一个名叫"success_thumb.php"的文件呢？实验证明我们的假设没有错！而且我们还发现，最近使用的文件夹ID跟我们之前上传图片文件的文件夹ID是一样的。因此，存储了我们PoC php命令执行代码的文件其ticket ID为"/386/"，文件ID为"867"。

为什么我不使用暴力破解攻击来获取文件夹ID呢？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010910e691dbf4102f.png)

于是我马上打开了我的爆破工具，并对下列请求地址进行暴力破解攻击（文件ID从500-1000）：

```
https://www.paypal-brandcentral.com/content/_helpdesk/366/$(爆破500-1000)$/success.php
```

最终文件夹ID为"865"的请求返回了200响应码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014971d5f90aebc111.png)

没错，我当时的感觉就像是这样:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019170cb6acf5432c9.png)

非常好！接下来，我们尝试一下用刚才得到的ticket ID和文件ID来运行我们的代码：

```
https://www.paypal-brandcentral.com/content/_helpdesk/366/865/success.php?cmd=uname-a;whoami
```

[![](https://p0.ssl.qhimg.com/t0188cbbc1c6f983bf7.png)](https://p0.ssl.qhimg.com/t0188cbbc1c6f983bf7.png)

是的，你没看错！我好像找到了一个远程代码执行漏洞！

服务器端还托管了一个PayPal员工专用的登录页面，也许你还可以登录进去看看里面有什么，哈哈。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019b6a59606e2404cd.png)

<br>

**漏洞披露时间轴**



2017年7月8日18时03分：提交漏洞信息

2017年7月11日18时03分：漏洞成功修复
