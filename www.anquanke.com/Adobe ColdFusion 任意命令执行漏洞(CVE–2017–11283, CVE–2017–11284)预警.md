> 原文链接: https://www.anquanke.com//post/id/87047 


# Adobe ColdFusion 任意命令执行漏洞(CVE–2017–11283, CVE–2017–11284)预警


                                阅读量   
                                **199422**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t010669b7d0aafa7b56.png)](https://p4.ssl.qhimg.com/t010669b7d0aafa7b56.png)



**0x00 事件描述**



Adobe ColdFusion 在 2017 年 9 月 12 日发布的安全更新中提及到之前版本中存在严重的反序列化漏洞（**CVE-2017-11283, CVE-2017-11284**），可导致远程代码执行。当使用 Flex 集成服务开启 Remote Adobe LiveCycle Data Management access 的情况下可能受到该漏洞的影响，使用该功能会开启 RMI 服务，**监听的端口为 1099**。ColdFusion 自带的 Java 版本过低，不会在反序列化之前对 RMI 请求中的对象类型进行检验。

360CERT 经过分析验证，确认该漏洞确实存在，请相关用户尽快进行更新处理。



**0x01 影响版本**



1.ColdFusion (2016 release) Update 4 以及之前的版本

2.ColdFusion 11 Update 12 以及之前版本



**0x02 漏洞利用验证**



往 RMI 服务发送构造好的 payload 做一个简单的远程代码执行验证。

[![](https://p4.ssl.qhimg.com/t01fbc7277e7fa94bae.png)](https://p4.ssl.qhimg.com/t01fbc7277e7fa94bae.png)



**0x03 修复方案**



1.在管理页面关闭 Remote Adobe LiveCycle Data Management access

2.升级最新补丁 ColdFusion (2016 release) Update 5，ColdFusion 11 Update 13



**0x04 时间线**



2017-9-12 Adobe ColdFusion 发布安全更新

2017-10-19 360CERT 发布漏洞预警



**0x05 参考链接**



[https://helpx.adobe.com/security/products/coldfusion/apsb17-30.html](https://helpx.adobe.com/security/products/coldfusion/apsb17-30.html)

[https://nickbloor.co.uk/2017/10/13/adobe-coldfusion-deserialization-rce-cve-2017-11283-cve-2017-11238/](https://nickbloor.co.uk/2017/10/13/adobe-coldfusion-deserialization-rce-cve-2017-11283-cve-2017-11238/)
