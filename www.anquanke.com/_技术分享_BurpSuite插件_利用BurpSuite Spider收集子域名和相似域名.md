> 原文链接: https://www.anquanke.com//post/id/86512 


# 【技术分享】BurpSuite插件：利用BurpSuite Spider收集子域名和相似域名


                                阅读量   
                                **136647**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    





[![](https://p0.ssl.qhimg.com/t011001fd08e623a96e.png)](https://p0.ssl.qhimg.com/t011001fd08e623a96e.png)

**作者：bit4@polaris-lab.com**

**<br>**

**前言**



在我的域名收集知识体系中，利用爬虫来获取域名是其中的一部分（见文末思维导图，其他部分的实现请访问我的另外一个项目：[https://github.com/bit4woo/Teemo](https://github.com/bit4woo/Teemo) ），由于使用频率，使用习惯等问题，而我最终决定使用BurpSuite的Spider来实现爬虫部分的自动化收集。所以有了这个BurpSuite插件：Domain Hunter。

<br>

**原理**

****

当使用了BurpSuite作为代理，或者使用它进行了安全测试，会就会记录相关的域名。其中，某个目标的子域名和相似域名很有价值，尤其是相似域名，往往有惊喜！插件的主要原理就是从BurpSuite的Sitemap中搜索出子域名和相似域名。也可以对已经发现的子域名进行主动爬取，以发现更多的相关域名，这个动作可以自己重复递归下去，直到没有新的域名发现为止。

<br>

**项目地址**

****

[https://github.com/bit4woo/domain_hunter](https://github.com/bit4woo/domain_hunter)



**截图**

****

[![](https://p3.ssl.qhimg.com/t0172dc18b9ecd38bbf.png)](https://p3.ssl.qhimg.com/t0172dc18b9ecd38bbf.png)



**Change Log**

****

2017-07-28: Add a function to crawl all known subdomains; fix some bug.

<br>

**Xmind Of Domain Collection**

****

[![](https://p4.ssl.qhimg.com/t0155ef853cd37d5424.png)](https://p4.ssl.qhimg.com/t0155ef853cd37d5424.png)


