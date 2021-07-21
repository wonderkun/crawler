> 原文链接: https://www.anquanke.com//post/id/152955 


# Jenkins 任意文件读取漏洞分析


                                阅读量   
                                **270106**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t019ee406e80dc197d2.jpg)](https://p5.ssl.qhimg.com/t019ee406e80dc197d2.jpg)

## 一、漏洞背景

漏洞编号：CVE-2018-1999002<br>
漏洞等级：高危

Jenkins 7 月 18 日的安全通告修复了多个漏洞，其中 SECURITY-914 是由 Orange （博客链接：[http://blog.orange.tw/](http://blog.orange.tw/) ） 挖出的 Jenkins 未授权任意文件读取漏洞。

腾讯安全云鼎实验室安全研究人员对该漏洞进行分析发现，利用这个漏洞，攻击者可以读取 Windows 服务器上的任意文件，对于 Linux，在特定条件下也可以进行文件读取。利用文件读取漏洞，攻击者可以获取到 Jenkins 的凭证信息，从而造成敏感信息泄露。另外，在很多时候，Jenkins 的部分凭证和其内用户的帐号密码相同，获取到凭证信息后也可以直接登录 Jenkins 进行命令执行操作等。



## 二、漏洞分析

Jenkins 在处理请求的时候是通过 Stapler 进行处理的，Stapler 是一个 Java Web 框架。查看 web.xml 可知，Stapler 拦截了所有请求：

[![](https://p4.ssl.qhimg.com/t016d903f40e2320d7d.png)](https://p4.ssl.qhimg.com/t016d903f40e2320d7d.png)

单步跟入 hudson.util.PluginServletFilter，最后会跟到 jenkinscoresrcmainjavahudsonPlugin.java 的 doDynamic 方法：

[![](https://p0.ssl.qhimg.com/t019144d526064e91a4.png)](https://p0.ssl.qhimg.com/t019144d526064e91a4.png)

可以发现，Jenkins 在 serve /plugin/SHORTNAME 这个 URL 的时候，调用的是 StaplerResponse 的 serveLocalizedFile 方法处理静态文件的，继续跟入这个方法：

[![](https://p1.ssl.qhimg.com/t010335d655e2c3b254.png)](https://p1.ssl.qhimg.com/t010335d655e2c3b254.png)

其中 request.getLocale() 是 jetty-server-9.4.5.v20170502-sources.jar!orgeclipsejettyserverRequest.java 内的，其实现为：

[![](https://p4.ssl.qhimg.com/t01239b23e3b2d028b3.png)](https://p4.ssl.qhimg.com/t01239b23e3b2d028b3.png)

非常明显，Jetty 在获取 Locale 的时候直接从 HTTP Headers 里取出 Accept-Language 头，用 – 分割后返回了一个 Locale 对象。也就是我传入Accept-Language: ../../../aaaa-bbbbbb 时，那么我将会得到一个 Locale(“../../../aaaa”, “BBBBBB”)对象。

最后到跟入 stapler-1.254-sources.jar!orgkohsukestaplerStapler.java：

[![](https://p0.ssl.qhimg.com/t017cfef2575072cabf.png)](https://p0.ssl.qhimg.com/t017cfef2575072cabf.png)

我们可以发现，Stapler 首先将后缀名单独取出，接着将 Jenkins 目录和传入的 locale 的 language 以及后缀名拼接，然后打开这个路径。那么攻击者只需要构造出如下 HTTP 请求即可造成文件读取：

[![](https://p4.ssl.qhimg.com/t019d04dce7c4c5dfc6.png)](https://p4.ssl.qhimg.com/t019d04dce7c4c5dfc6.png)

最后 URL 拼接的现场为：

[![](https://p2.ssl.qhimg.com/t01f39660df122e6c70.png)](https://p2.ssl.qhimg.com/t01f39660df122e6c70.png)

在 Windows 下，不存在的目录可以通过 ../ 遍历过去的，而对于 Linux 则不行。那么这个漏洞在 Windows 下是可以任意文件读取的，而在 Linux 下则需要在 Jenkins plugins 目录下存在一个名字中存在 _ 的目录才可以。

[![](https://p4.ssl.qhimg.com/t019b92e7ebc5a6e049.png)](https://p4.ssl.qhimg.com/t019b92e7ebc5a6e049.png)



## 三、利用方式

一般来说，文件读取漏洞很难转化为命令执行，对于 Jenkins 也是如此。不过 Jenkins 有一个 Credentials 模块，这个模块储存了 Jenkins 的一些凭证信息，很多时候，其凭证的帐号密码是和 Jenkins 的帐号密码相同的。无论如何，在成功利用文件读取漏洞后，都要将凭证信息读取并解密，以收集更多的信息。

如果我们想获取 Jenkins 的凭证信息的话，需要以下几个文件：

· credentials.xml<br>
· secrets/hudson.util.Secret<br>
· secrets/master.key

很幸运的是这几个文件我们都可以利用文件读取漏洞读取出来。在 Shodan 上尝试获取国外 real world 的 Jenkins 的帐号密码：

[![](https://p1.ssl.qhimg.com/t01507313ce00b35f6c.png)](https://p1.ssl.qhimg.com/t01507313ce00b35f6c.png)

当然，获取到的帐号密码是不能直接登录的，但是稍微修改一下用户名就可以成功的登录进去了：

[![](https://p0.ssl.qhimg.com/t01acf068a3a558e811.png)](https://p0.ssl.qhimg.com/t01acf068a3a558e811.png)



## 四、修复方案

虽然这个漏洞危害较大，但是不必太过担心，因为默认安装 Jenkins 的时候匿名用户是没有可读权限的。并且此漏洞在 Linux 上被利用的可能性较小。以下为推荐的修复方案：

➢针对此高危漏洞利用，腾讯云网站管家 WAF AI 引擎可检测并拦截，如果需要，可在腾讯云官网进一步了解

➢在全局安全配置中将匿名用户的可读权限去掉

[![](https://p4.ssl.qhimg.com/t0105f7505e343a04d5.png)](https://p4.ssl.qhimg.com/t0105f7505e343a04d5.png)

➢升级到最新版本的 Jenkins（2.121.2）

➢使用 Linux
