> 原文链接: https://www.anquanke.com//post/id/82758 


# 使用PYTHON测试HTTP验证服务的OCSP协议


                                阅读量   
                                **115118**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.insinuator.net/2015/10/ocsp-over-http-testing-with-python/](https://www.insinuator.net/2015/10/ocsp-over-http-testing-with-python/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0135018254f661acc8.jpg)](https://p0.ssl.qhimg.com/t0135018254f661acc8.jpg)

今天我们想分享一下如何使用渗透测试神器Burp和一些Python技巧测试HTTP验证服务的 OCSP 协议。首先介绍一点OCSP在线证书状态协议的背景OCSP的首要作用是验证 X.509证书的状态。

OCSP响应器是系统的重要组成部分。它由权威认证机构运营并会响应三种不同的可能结果之一。第一种是好“good”表示该证书不会被禁止撤销“revoked”表示证书会被禁止而未知“unknown”表示状态不能被确定因为证书的颁发CA对响应器是未知的。

想要获取更多细节你可以看看RFC 2560。在最近的渗透测试中我们开发了一个python脚本可以生成有效的X.509证书并连接一个OCSP服务。在这一系列测试期间不同于每次都自己做一遍的麻烦如果有一个脚本将会非常得心应手这能生成有效的响应。

为了使用这个脚本必须要安装一些必需的python包 “PyASN”包用来存储和交换客户端和OCSP程序之间的数据 “requests”包用来在应用程序和Burp Proxy之间处理和创建 http POST请求。所有这些扩展包可以通过easy_install python package manager进行安装。脚本的设置部分取决于你自己的配置url部分是你想测试的OCSP应用程序服务器的地址而Proxy部分是默认 Proxy Burp听新来的请求。一旦你已经设置好正确的变量你就准备就绪了。你需要做的第一件事就是开启Burp Proxy并拦截所有来自端口8080的请求。如果你的设置都正确了你会接收到类似下面所示的响应

```
POST http://yourhost.tld/ocsp HTTP/1.1
 Host: yourhost.tld
 Content-Length: 105
 Accept-Encoding: gzip, deflate
 Accept: */*
 User-Agent: python-requests/2.7.0 CPython/2.7.6 Windows/7
 Connection: keep-alive
 Content-Type: application/ocsp-request
 0g0e0&gt;0&lt;0:0 +
```



你所看到的是OCSP 服务的二进制证书请求。如果将请求传递给OCSP服务它会验证证书并发送一个回复例如



```
HTTP/1.1 200 OK
Content-Type: application/ocsp-response
Date: Mon, 29 Jun 2015 18:22:10 GMT
X-Cache: MISS from
Via: 1.1
Connection: keep-alive
Content-Length: 5779
0Â‚Â
```



想要弄清楚回复的含义是什么并不简单所以我们已经在脚本中实现了一个解码器。如果你看一下终端你会看到位于解码有效载荷的高位和中位的响应。

certStatus=CertStatus:

unknown=

如以上所示程序的响应是 RFC2560中的 “未知“。“未知”状态是指响应器不知道有关证书是否被请求的任何信息。如果OCSP服务正确处理了所有的请求你应该能够修改脚本并植入自己的恶意证书来检查一下。如果你想要进一步查看OCSP Service的安全验证的步骤你应该查看验证证书的具体机制。比如试试使用一个revoked认证然后看看 OCSP service是否仍然接受它这当然就是漏洞了。你需要查看的另外一个就是所谓的OCSP stapling。OCSP stapling功能是标准OCSP协议的增强版可以使用证书从服务器发送OCSP响应无需web用户一方每次检查OCSP响应与颁发CA。这会降低带宽显著提高网站性能并提高安全性因为人人都参与了建立安全会话。使用stapling改善服务也将减少拒绝服务的风险Denial-of-Service。而且考虑到了OCSP服运行着一个在每次你认证时提供给它的加密签名哈希。因此有足够的计算能力的服务运营商也可能受到DoS攻击。如果你正在用burp测试服务器试试评估一下有多少OCSP请求可以同时进行。同时如果可能的话查看一下OCSP服务器看看服务器平均负载是如何增加的或没有变化。

作为总结当你操纵这样一个服务器时还有一些针对OCSP服务器的攻击源需要留心。

以下是我们测试使用的Python脚本

[**OCSP Python Script**](https://github.com/ernw/insinuator-snippets/blob/master/OCSP/ocsp.py)
