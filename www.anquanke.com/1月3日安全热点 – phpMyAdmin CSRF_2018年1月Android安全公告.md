> 原文链接: https://www.anquanke.com//post/id/93210 


# 1月3日安全热点 – phpMyAdmin CSRF/2018年1月Android安全公告


                                阅读量   
                                **103685**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)

## 资讯类

Google发布2018年1月的Android安全公告（包括运行时的提权漏洞CVE-2017-13176、Media framework的代码执行漏洞和提权漏洞等）

[https://source.android.com/security/bulletin/2018-01-01](https://source.android.com/security/bulletin/2018-01-01)



两名安全研究人员发布了一系列叫作“Trackmageddon”的漏洞的报告，这些漏洞会影响一些GPS和定位跟踪服务

[https://www.bleepingcomputer.com/news/security/-trackmageddon-vulnerabilities-discovered-in-gps-location-tracking-services/](https://www.bleepingcomputer.com/news/security/-trackmageddon-vulnerabilities-discovered-in-gps-location-tracking-services/)

报告：[https://0x0.li/trackmageddon/](https://0x0.li/trackmageddon/)



## 技术类

三星Android设备通过MTP(Media Transfer Protocol )任意文件读写漏洞PoC(SVE-2017-10086)

[https://github.com/smeso/MTPwn](https://github.com/smeso/MTPwn)



浏览器里运行的C语言环境：可将C++编译为WebAssembly格式在浏览器运行

[https://tbfleming.github.io/cib/](https://tbfleming.github.io/cib/)

[https://github.com/tbfleming/cib](https://github.com/tbfleming/cib)



从微信小程序看前端代码安全

[https://share.whuboy.com/weapp.html](https://share.whuboy.com/weapp.html)



34c3 Web部分Writeup<br>[https://lorexxar.cn/2018/01/02/34c3-writeup/](https://lorexxar.cn/2018/01/02/34c3-writeup/)



“Inside Intel Management Engine” about activation JTAG for IntelME

[https://github.com/ptresearch/IntelME-JTAG/blob/master/Inside_Intel_Management_Engine.pdf](https://github.com/ptresearch/IntelME-JTAG/blob/master/Inside_Intel_Management_Engine.pdf)



用Golang写的域名信息搜集工具

[https://github.com/tomsteele/blacksheepwall](https://github.com/tomsteele/blacksheepwall)



facebook移动站(m.facebook.com)上的DOM型XSS writeup，官方确认后给了$7500作为奖励

[https://thesecurityexperts.wordpress.com/2017/12/20/dom-xss-in-facebook-mobile-siteapp-login/](https://thesecurityexperts.wordpress.com/2017/12/20/dom-xss-in-facebook-mobile-siteapp-login/)

[![](https://p4.ssl.qhimg.com/t01961d59d82578c9c5.png)](https://p4.ssl.qhimg.com/t01961d59d82578c9c5.png)[![](https://p1.ssl.qhimg.com/t01c0c2b8410d4d43e6.png)](https://p1.ssl.qhimg.com/t01c0c2b8410d4d43e6.png)



phpMyAdmin &lt; 4.7.7 CSRF漏洞

[https://thehackernews.com/2018/01/phpmyadmin-hack.html](https://thehackernews.com/2018/01/phpmyadmin-hack.html)

[http://securityaffairs.co/wordpress/67243/hacking/phpmyadmin-csrf-vulnerability.html](http://securityaffairs.co/wordpress/67243/hacking/phpmyadmin-csrf-vulnerability.html)<br><video src="http://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/Q1NSRiBpbiBwaHBNeUFkbWluIF8gRFJPUCBUQUJMRSB3aXRoIGEgc2luZ2xlIGNsaWNrIS5tcDQ=" controls="controls" width="728" height="440" style="width: 728; height: 440;">﻿<br>
您的浏览器不支持video标签<br></video>

phpMyAdmin 官方公告

[https://www.phpmyadmin.net/security/PMASA-2017-9/](https://www.phpmyadmin.net/security/PMASA-2017-9/)



gron：使JSON greppable的工具

```
▶ gron "https://api.github.com/repos/tomnomnom/gron/commits?per_page=1" | fgrep "commit.author"
json[0].commit.author = `{``}`;
json[0].commit.author.date = "2016-07-02T10:51:21Z";
json[0].commit.author.email = "mail@tomnomnom.com";
json[0].commit.author.name = "Tom Hudson";
```

[https://github.com/tomnomnom/gron](https://github.com/tomnomnom/gron)



脱壳反编译PyInstaller恶意软件

[https://www.youtube.com/watch?v=x8OtmBoCyw4](https://www.youtube.com/watch?v=x8OtmBoCyw4)



免root使用frida

[https://koz.io/using-frida-on-android-without-root/](https://koz.io/using-frida-on-android-without-root/)



CVE-2017-5129：Google Chrome “ScriptProcessorHandler::FireProcessEvent()” Use-after-free 漏洞

[https://bugs.chromium.org/p/chromium/issues/detail?id=765495](https://bugs.chromium.org/p/chromium/issues/detail?id=765495)
