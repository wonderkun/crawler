> 原文链接: https://www.anquanke.com//post/id/93680 


# 1月5日安全热点–Intel CEO卖股票/Intel承诺下周末CPU固件更新


                                阅读量   
                                **128000**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)

## 资讯类

对于昨天Google的Project Zero发布的关于现代CPU的speculative execution漏洞的缓解措施

[https://security.googleblog.com/2018/01/more-details-about-mitigations-for-cpu_4.html](https://security.googleblog.com/2018/01/more-details-about-mitigations-for-cpu_4.html)

Google发布防御Spectre攻击的缓解措施：Retpoline

[https://support.google.com/faqs/answer/7625886](https://support.google.com/faqs/answer/7625886)



Intel CEO Brian Krzanich在去年11月卖掉其在公司价值2400万美元的股票和期权，而这个时间恰好在Google告知其处理器严重的安全漏洞之后，而在此漏洞本周公开披露之前。

[![](https://p5.ssl.qhimg.com/t01c1e9e4a3e780c037.jpg)](https://p5.ssl.qhimg.com/t01c1e9e4a3e780c037.jpg)

[http://www.businessinsider.com/intel-ceo-krzanich-sold-shares-after-company-was-informed-of-chip-flaw-2018-1](http://www.businessinsider.com/intel-ceo-krzanich-sold-shares-after-company-was-informed-of-chip-flaw-2018-1)

[http://thehill.com/policy/technology/367432-intel-ceo-sold-24-million-in-stock-while-firm-knew-about-cyber](http://thehill.com/policy/technology/367432-intel-ceo-sold-24-million-in-stock-while-firm-knew-about-cyber)



Intel承诺下周末发布CPU固件更新

（Intel说已经开始给合作伙伴发布一些CPU的固件升级，各委托制造商以及其他硬件厂商需要将这些固件更新加入到自己产品的更新中；Intel承诺会缓解性能上的影响；但是补丁会很复杂，因为修复这两个漏洞需CPU固件的升级，操作系统层的补丁，以及要应用层面的缓解措施。）

[https://www.bleepingcomputer.com/news/hardware/intel-promises-firmware-updates-for-most-modern-cpus-by-the-end-of-next-week/](https://www.bleepingcomputer.com/news/hardware/intel-promises-firmware-updates-for-most-modern-cpus-by-the-end-of-next-week/)



苹果发布公告称所有Mac系统和iOS设备都受Meltdown/Spectre漏洞影响，但目前还未发现针对用户的漏洞利用出现<br>
（“由于利用这些漏洞中的需要在您的Mac或iOS设备上加载恶意app，因此我们建议您仅从可信来源（如App Store）下载软件。 苹果已经在iOS 11.2，macOS 10.13.2和tvOS 11.2上发布了缓解措施，以帮助防御Meltdown漏洞。 Apple Watch不会受到Meltdown的影响。 在接下来的日子里，我们计划在Safari中发布缓解措施，以帮助防御Spectre。 我们将继续开发和测试这些问题的进一步缓解措施，并将在即将到来的iOS，macOS，tvOS和watchOS更新中发布。”）

[https://support.apple.com/en-us/HT208394](https://support.apple.com/en-us/HT208394)

[Apple says Meltdown and Spectre flaws affect ‘all Mac systems and iOS devices,’ but not for long](https://techcrunch.com/2018/01/04/apple-says-meltdown-and-spectre-flaws-affect-all-mac-systems-and-ios-devices-but-not-for-long/)



YouTube移除掉了关于Meltdown/Spectre PoC的视频

[![](https://p1.ssl.qhimg.com/t01992a4084b024bb5c.jpg)](https://p1.ssl.qhimg.com/t01992a4084b024bb5c.jpg)

[https://twitter.com/campuscodi/status/948989406332862464](https://twitter.com/campuscodi/status/948989406332862464)



## 技术类

CPU Spectre信息泄露漏洞PoC

[https://www.exploit-db.com/exploits/43427/](https://www.exploit-db.com/exploits/43427/)

CPU meltdown漏洞PoC

[https://github.com/paboldin/meltdown-exploit](https://github.com/paboldin/meltdown-exploit)



性能VS安全？CPU芯片漏洞攻击实战(1) – 破解macOS KASLR篇

[https://weibo.com/ttarticle/p/show?id=2309404192549521743410](https://weibo.com/ttarticle/p/show?id=2309404192549521743410)



Meltdown/Spectre漏洞的一些笔记

[http://blog.erratasec.com/2018/01/some-notes-on-meltdownspectre.html](http://blog.erratasec.com/2018/01/some-notes-on-meltdownspectre.html)



Android恶意软件偷取Uber凭证

[https://www.symantec.com/blogs/threat-intelligence/android-malware-uber-credentials-deep-links](https://www.symantec.com/blogs/threat-intelligence/android-malware-uber-credentials-deep-links)



Facebook CSRF

[https://www.youtube.com/watch?v=3KwGmKucayg](https://www.youtube.com/watch?v=3KwGmKucayg)

<video style="width: 100%; height: auto;" src="http://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/Q1NSRiBCeXBhc3MubXA0" controls="controls" width="100" height="100"><br>
您的浏览器不支持video标签<br></video>



Linksys WVBR0-25 – User-Agent命令执行

[https://www.exploit-db.com/exploits/43429/](https://www.exploit-db.com/exploits/43429/)



CVE-2017-17867: Iopsys路由器远程代码执行漏洞

[https://neonsea.uk/blog/2017/12/23/rce-inteno-iopsys.html](https://neonsea.uk/blog/2017/12/23/rce-inteno-iopsys.html)



Snort 2.9.11.1发布

[http://blog.snort.org/2018/01/snort-29111-has-been-released.html](http://blog.snort.org/2018/01/snort-29111-has-been-released.html)
