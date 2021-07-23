> 原文链接: https://www.anquanke.com//post/id/84789 


# 【技术分享】从白帽子角度谈Flash安全


                                阅读量   
                                **116025**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0182241c11338ec545.jpg)](https://p5.ssl.qhimg.com/t0182241c11338ec545.jpg)

**作者：**[**阻圣**********](http://bobao.360.cn/member/contribute?uid=134615136)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**********](http://bobao.360.cn/contribute/index)**在线投稿**

**<br>**

**前言**

Flash攻击技术一直以它的不为人知性而深受黑客追捧，本文从白帽子角度介绍Flash安全，从Flash漏洞产生的原因到漏洞的挖掘之路，希望能帮助到大家，水平有限，如有不足还请指出。

<br>

**配置不当出CSRF**

Flash跨域唯一的限制就在crossdomain.xml这个文件，它限制了flash是否可以跨域读写数据以及允许从什么地方跨域读取数据，如果配置不当就会产生CSRF漏洞。

下图展示了网易博客的crossdomain.xml

[![](https://p5.ssl.qhimg.com/t013f5aab24464ee447.png)](https://p5.ssl.qhimg.com/t013f5aab24464ee447.png)

<br>

**挖掘Flash CSRF思路**

既然形成Flash CSRF的原因在于crossdomain.xml，我们首先就来打开crossdomain.xml，查看是否允许跨域，允许了哪些站点跨域。

allow-access-from选项就是用来限制哪些域可以进行跨域请求数据。

经典的漏洞配置：

```
&lt;allow-access-from domain="*"/&gt;
```

允许所有域进行跨域请求数据。

<br>

**Flash CSRF漏洞利用**

发现漏洞后，可以要测试一些是否有危害了，要是影响不大肯定又要忽略了。所以我们肯定先要证明一下漏洞确实存在并且有危害的。

首先找到一个存在csrf的页面：

[![](https://p5.ssl.qhimg.com/t01fa511a76bfd7e287.png)](https://p5.ssl.qhimg.com/t01fa511a76bfd7e287.png)

我们找到一个地方插入flash，管理访问我们的页面就会执行我们写的脚本了。下面看演示，我们来写一个管理访问我们的页面时，就修改用户admin的密码为test123。

利用代码：



```
var url:String = "http://www.test.com/csrfdemo.php";
var datapost:String = "username=admin&amp;password=test";
var _request:URLRequest = new URLRequest();
_request.url = url;
_request.method = URLRequestMethod.POST;
_request.data = datapost;
sendToURL(_request);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0160c1d6c732a32608.png)

这里我们为了演示清楚，flash显示的就是一个长方形框。

然后我们看一下数据库情况：

[![](https://p3.ssl.qhimg.com/t0172c6761987002fbf.png)](https://p3.ssl.qhimg.com/t0172c6761987002fbf.png)

可以看见访问前密码是123456，访问后密码变成test123，利用成功。

<br>

**Flash CSRF防御**

很多小伙伴提交漏洞的时候，在漏洞修复建议的地方往往就填个你懂的，其实我们描述清楚，肯定会减少审核人员的工作量，让他们更容易理解，这样绝对有加分滴。

其实Flash CSRF修复建议也很简单，配置好crossdomain.xml文件，将权限限制到子域。

<br>

**Flash XSS**

挖掘flash xss其实就像代码审计一样悠闲，我们将网站上flash文件下载下来，然后进行逆向分析。下面介绍存在漏洞的函数。

**1、	getURL()**

getURL函数存在问题的地方有两处，第一处是clickTAG变量，clickTAG变量主要被用来跟踪广告的被单击的时间、次数还有显示的位置。但没有对这个变量进行检查的话，就可以注入我们的恶意脚本。

```
getURL(clickTag,"window");
```

[![](https://p5.ssl.qhimg.com/t017388a01f82c562db.png)](https://p5.ssl.qhimg.com/t017388a01f82c562db.png)

同样道理，不管第一个变量叫什么名字，我们都可以用来执行javascript伪协议来执行任意代码。

另一处存在的问题是重定向，只要将函数内参数设置一个url就可以了。

[![](https://p3.ssl.qhimg.com/t0152bc2a34d80a2db4.png)](https://p3.ssl.qhimg.com/t0152bc2a34d80a2db4.png)

ActionScript 3.0已经不支持这个函数，不过代码都是兼容的，可以用ActionScript 2.0来写。

**2、	navigateToURL()**

在ActionScript 3.0中舍弃了getURL()而使用navigateToURL()，其实navigateToURL()也存在安全问题。

[![](https://p1.ssl.qhimg.com/t01e35788d65f1336cc.png)](https://p1.ssl.qhimg.com/t01e35788d65f1336cc.png)

问题产生原因在于调用外部资源文件可被控制导致的。

[![](https://p3.ssl.qhimg.com/t01fbac33c377c9eefc.png)](https://p3.ssl.qhimg.com/t01fbac33c377c9eefc.png)

类型注入函数：



```
loadVariables();
loadMovie();
loadMovieNum();
XML.load();
LoadVars.load();
Sound.loadSound();
NetStream.play();
```

大家注意大小写。

**3、ExternalInterface.call()**

ExternalInterface.call()是一个执行js的接口函数

参数：

```
ExternalInterface.call("sendToJavaScript", input.text);
```

最终执行的js：

```
try `{`
    __flash__toXML(sendToJavaScript,"value of input.text"));
  `}` catch (e) `{`
    "&lt;undefined/&gt;";
  `}`
```

[![](https://p2.ssl.qhimg.com/t010a641a8ecf4fa290.png)](https://p2.ssl.qhimg.com/t010a641a8ecf4fa290.png)

[![](https://p1.ssl.qhimg.com/t016015cca8f4b8bd54.png)](https://p1.ssl.qhimg.com/t016015cca8f4b8bd54.png)

可控第一个参数的时候

[![](https://p1.ssl.qhimg.com/t016d4af98426022926.png)](https://p1.ssl.qhimg.com/t016d4af98426022926.png)

[![](https://p4.ssl.qhimg.com/t0118e5b6de4e773ec0.png)](https://p4.ssl.qhimg.com/t0118e5b6de4e773ec0.png)

可控第二个参数的时候

[![](https://p3.ssl.qhimg.com/t01fe7dd7de7d53032d.png)](https://p3.ssl.qhimg.com/t01fe7dd7de7d53032d.png)

<br>

**Flash XSS漏洞修复建议**

只要找到问题点进行说明就很容易进行修复了。

<br>

**总结**

本文介绍应该比较详细了，本文事例如出现与文章不符现象，并非文章有错误，浏览器本身是有保护机制的，关于如何绕过浏览器保护机制不是本文所介绍的内容，技术有限，如有不足还请指出。

<br>

**参考文章**

[https://lcamtuf.blogspot.hk/2011/03/other-reason-to-beware-of.html](https://lcamtuf.blogspot.hk/2011/03/other-reason-to-beware-of.html)
