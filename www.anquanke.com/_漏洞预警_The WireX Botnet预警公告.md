> 原文链接: https://www.anquanke.com//post/id/86718 


# 【漏洞预警】The WireX Botnet预警公告


                                阅读量   
                                **85844**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0138e655b7d54c07c8.png)](https://p3.ssl.qhimg.com/t0138e655b7d54c07c8.png)



**0x00 事件公告**



2017年8月17日，名为WireX BotNet的僵尸网络通过伪装普通安卓应用的方式大量感染安卓设备并发动了较大规模的DDoS攻击，此举引起了部分CDN提供商的注意，此后来自Akamai, Cloudflare, Flashpoint, Google, Oracle Dyn, RiskIQ, Team Cymru等组织**联合**对该事件进行分析，并于8月28日发布了该事件的安全报告。

该安全报告分析表明，攻击者可能从7月中旬(可能更早)开始组建WireX BotNet，并通过小规模的攻击受害网络来牟利。8月7日左右，WireX BotNet开始进行流量更大持续时间更长的DDoS攻击。从8月15日开始，WireX引发的DDoS事件源自至少**7万个**独立IP地址。8月17日攻击数据的分析显示，来自**100多个国家**的设备感染了WireX BotNet。

[![](https://p4.ssl.qhimg.com/t019d6c8ef45d8ecd60.png)](https://p4.ssl.qhimg.com/t019d6c8ef45d8ecd60.png)

**WireX BotNet的源IP趋势**

WireX BotNet主要伪装成带有极大的诱惑性和隐蔽性的视频播放器、铃声、文件管理器等无害应用，此前已发现大约有300种不同的移动应用程序分散在Google Play商店中。目前Google删除了受影响的应用程序，并开始从所有设备中删除该恶意应用程序，但还不清楚具体有多少安卓设备被WireX感染。

目前，360手机卫士、360安全卫士和360手机助手在内的产品已经能准确地进行WireX BotNet查杀，技术层面（分析报告见参考3）确定了国内有100多个WireX BotNet相关的恶意安卓应用。请使用安卓设备的用户和相关的安卓应用市场尽快进行相关的查杀。



**0x01 影响面分析**



事件等级： 较大

感染了Google Play商店和部分安卓应用市场，可能有数万台安卓设备受影响。



**0x02 处理建议**



1、建议安卓用户安装360手机卫士等有效的终端防护应用进行防护；

2、建议各安卓应用市场对于存量和提交的应用进行安全扫描后再上架；



**0x03 时间线**



2017-8-28 事件披露

2017-8-29 360烽火实验室和360NetLab对WireX进行技术分析

2017-8-29 360CERT发布预警公告



**0x04 参考**



1、The WireX Botnet: How Industry Collaboration Disrupted a DDoS Attack

[https://blog.cloudflare.com/the-wirex-botnet/?utm_content=buffer9e1c5&amp;utm_medium=social&amp;utm_source=twitter.com&amp;utm_campaign=buffer](https://blog.cloudflare.com/the-wirex-botnet/?utm_content=buffer9e1c5&amp;utm_medium=social&amp;utm_source=twitter.com&amp;utm_campaign=buffer)

2、安卓DDOS僵尸网络：The WireX Botnet

[http://bobao.360.cn/learning/detail/4323.html](http://bobao.360.cn/learning/detail/4323.html)

3、关于“WireX Botnet”事件Android样本分析报告

[http://blogs.360.cn/blog/analysis_of_wirex_botnet](http://blogs.360.cn/blog/analysis_of_wirex_botnet)
