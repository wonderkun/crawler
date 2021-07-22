> 原文链接: https://www.anquanke.com//post/id/87283 


# 【漏洞预警】Intel Q3'17 ME 11.x, SPS 4.0, TXE 3.0 重要安全更新


                                阅读量   
                                **119064**
                            
                        |
                        
                                                                                    



**[![](https://p4.ssl.qhimg.com/t01e961348e97deec0f.png)](https://p4.ssl.qhimg.com/t01e961348e97deec0f.png)**

** **

**0x00 事件背景**





2017年11月20日，Intel官方发布了一则Intel多款固件安全更新公告(编号Intel-SA-00086)。此公告提供了包括Intel® Management Engine (ME), Intel® Server Platform Services (SPS), and Intel® Trusted Execution Engine (TXE)的安全漏洞情况和更新补丁。

据悉，相关固件产品一共有10个CVE漏洞编号，**其中8个被评级为高危，2个中危。**

360CERT建议广大使用Intel相关固件的用户尽快进行排查升级处理,目前官方已经提供了相关检测工具。



**0x01 事件影响面**



**影响面**

**攻击者可以在目标操作系统不可直接访问的区域进行加载/执行任意代码，具备极高的隐蔽性，常规方法无法检测到。**

**影响产品**

6th, 7th &amp; 8th Generation Intel® Core™ Processor Family

Intel® Xeon® Processor E3-1200 v5 &amp; v6 Product Family

Intel® Xeon® Processor Scalable Family

Intel® Xeon® Processor W Family

Intel® Atom® C3000 Processor Family

Apollo Lake Intel® Atom Processor E3900 series

Apollo Lake Intel® Pentium™

Celeron™ N and J series Processors

**漏洞详情**

针对相关产品漏洞一共有10个CVE介绍

[![](https://p2.ssl.qhimg.com/t01f3f94aa5f066a410.png)](https://p2.ssl.qhimg.com/t01f3f94aa5f066a410.png)



**0x02 安全建议**



厂商Intel已经推出了相应的安全细节通告，漏洞检测工具。360CERT建议广大用户尽快进行更新。

Linux和Windows 漏洞检测工具官方下载地址：[http://www.intel.com/sa-00086-support](http://www.intel.com/sa-00086-support)

针对某款普通家庭笔记本检测结果

[![](https://p4.ssl.qhimg.com/t01c04b7880864541b1.png)](https://p4.ssl.qhimg.com/t01c04b7880864541b1.png)



**0x03 时间线**



2017-11-20 Intel发布固件更新公告

2017-11-21 360CERT发布漏洞预警



**0x04 参考链接**



官方公告:[https://www.intel.com/content/www/us/en/support/articles/000025619/software.html](https://www.intel.com/content/www/us/en/support/articles/000025619/software.html)

官方披露技术细节:[https://security-center.intel.com/advisory.aspx?intelid=INTEL-SA-00086&amp;languageid=en-fr](https://security-center.intel.com/advisory.aspx?intelid=INTEL-SA-00086&amp;languageid=en-fr)
