> 原文链接: https://www.anquanke.com//post/id/94632 


# 1月13日安全热点–Intel的AMT安全问题/DNS篡改恶软OSX/MaMi


                                阅读量   
                                **114097**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)

## 资讯类

2018年才过去两周，就迎来了macOS平台的DNS篡改恶意软件OSX/MaMi

[https://www.bleepingcomputer.com/news/apple/the-first-mac-malware-of-2018-is-a-dns-hijacker-called-mami/](https://www.bleepingcomputer.com/news/apple/the-first-mac-malware-of-2018-is-a-dns-hijacker-called-mami/)

[https://www.tomsguide.com/us/mami-mac-malware,news-26451.html](https://www.tomsguide.com/us/mami-mac-malware,news-26451.html)

这个恶意软件的信息最早出现在malwarebytes的论坛上（一个网友不小心安装了什么然后他的DNS就被篡改了）

[![](https://p0.ssl.qhimg.com/dm/1024_278_/t01e39a80b82021d02a.png)](https://p0.ssl.qhimg.com/dm/1024_278_/t01e39a80b82021d02a.png)

[https://forums.malwarebytes.com/topic/218198-dns-hijacked/](https://forums.malwarebytes.com/topic/218198-dns-hijacked/)

该恶意软件以未签名的Mach-O 64位二进制文件的形式分发，现在VirusTotal上可已经可以检测到（16/59）

[https://www.virustotal.com/#/file/5586be30d505216bdc912605481f9c8c7bfd52748f66c5e212160f6b31fd8571/detection](https://www.virustotal.com/#/file/5586be30d505216bdc912605481f9c8c7bfd52748f66c5e212160f6b31fd8571/detection)

[![](https://p1.ssl.qhimg.com/dm/1024_525_/t01b8ac939db8ad3609.png)](https://p1.ssl.qhimg.com/dm/1024_525_/t01b8ac939db8ad3609.png)

样本下载：[https://objective-see.com/downloads/malware/MaMi.zip](https://objective-see.com/downloads/malware/MaMi.zip)

解压密码：infect3d

objective-see对macOS平台的DNS篡改恶意软件OSX/MaMi的分析

[https://objective-see.com/blog/blog_0x26.html](https://objective-see.com/blog/blog_0x26.html)



F-Secure的Harry Sintonen发现了Intel的AMT中一个安全问题，该问题可导致攻击者在几秒钟内完全控制用户的设备，影响全球数百万台企业笔记本电脑。Harry解释了这个问题，并建议了应该如何缓解。<br>[https://thehackernews.com/2018/01/intel-amt-vulnerability.html](https://thehackernews.com/2018/01/intel-amt-vulnerability.html)

[https://business.f-secure.com/intel-amt-security-issue](https://business.f-secure.com/intel-amt-security-issue)

演示视频：<br><video style="width: 100%; height: auto;" src="http://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/QSBTZWN1cml0eSBJc3N1ZSBpbiBJbnRlbOKAmXMgQWN0aXZlIE1hbmFnZW1lbnQgVGVjaG5vbG9neSAoQU1UKS5tcDQ=" controls="controls" width="100" height="100"><br>
您的浏览器不支持video标签<br></video>



本周勒索软件盘点

[https://www.bleepingcomputer.com/news/security/the-week-in-ransomware-january-12th-2018-ethereum-and-small-variants/](https://www.bleepingcomputer.com/news/security/the-week-in-ransomware-january-12th-2018-ethereum-and-small-variants/)



Google Play的游戏应用中发现了投放色情广告的恶意软件<br>[https://blog.checkpoint.com/2018/01/12/childrens-apps-google-play-display-porn-ads/](https://blog.checkpoint.com/2018/01/12/childrens-apps-google-play-display-porn-ads/)

[![](https://p3.ssl.qhimg.com/t01b83c394879b0a97b.jpg)](https://p3.ssl.qhimg.com/t01b83c394879b0a97b.jpg)



## 技术类

CVE-2018-0802的PoC

[https://github.com/zldww2011/CVE-2018-0802_POC](https://github.com/zldww2011/CVE-2018-0802_POC)



How I exploited ACME TLS-SNI-01 issuing Let’s Encrypt SSL-certs for any domain using shared hosting

[https://labs.detectify.com/2018/01/12/how-i-exploited-acme-tls-sni-01-issuing-lets-encrypt-ssl-certs-for-any-domain-using-shared-hosting/](https://labs.detectify.com/2018/01/12/how-i-exploited-acme-tls-sni-01-issuing-lets-encrypt-ssl-certs-for-any-domain-using-shared-hosting/)



IDACyber：一款IDA Pro数据可视化插件

[https://github.com/patois/IDACyber](https://github.com/patois/IDACyber)



CVE-2018-1000001：libc的realpath()  buffer underflow

[https://www.halfdog.net/Security/2017/LibcRealpathBufferUnderflow/](https://www.halfdog.net/Security/2017/LibcRealpathBufferUnderflow/)

邮件列表：

[http://seclists.org/oss-sec/2018/q1/38](http://seclists.org/oss-sec/2018/q1/38)

[http://seclists.org/oss-sec/2018/q1/42](http://seclists.org/oss-sec/2018/q1/42)



看我如何结合两个漏洞拿到雅虎账号的通讯录

[http://www.sxcurity.pro/2018/01/11/chaining-yahoo-bugs/](http://www.sxcurity.pro/2018/01/11/chaining-yahoo-bugs/)

演示视频：

<video style="width: 100%; height: auto;" src="http://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/WWFob28hIENvbnRhY3QgVGhlZnQgdmlhIENPUlMgKyBYU1MubXA0" controls="controls" width="100" height="100"><br>
您的浏览器不支持video标签<br></video>



2017 SANS Holiday Hack Challenge Writeup

[https://0xd13a.github.io//2017-SANS-Holiday-Hack-Challenge-Writeup/](https://0xd13a.github.io//2017-SANS-Holiday-Hack-Challenge-Writeup/)



Zone transfers in The Netherlands

[https://binaryfigments.com/2018/01/12/zone-transfers-in-the-netherlands/](https://binaryfigments.com/2018/01/12/zone-transfers-in-the-netherlands/)
