> 原文链接: https://www.anquanke.com//post/id/86565 


# 【漏洞预警】CVE–2017–8543 Windows Search远程代码执行漏洞预警(含演示)


                                阅读量   
                                **113555**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t018731f5b33a269799.png)](https://p1.ssl.qhimg.com/t018731f5b33a269799.png)

作者：Shi Lei @360CERT &amp;&amp; 360 GearTeam



**描述**



日前，360CERT确认了编号**CVE-2017-8543**的微软Windows Search严重漏洞存在被远程攻击的可行性，该漏洞被成功利用会对Windows用户产生严重的安全威胁，在此再次预警使用Windows平台的用户立即进行微软的2017年6月的安全补丁更新操作或安装“360安全卫士”进行有效防御。

微软在今年6月中旬发布的补丁包中包含了一个关于Windows Search的远程代码执行漏洞，CVE编号为:CVE-2017-8543。当 Windows Search 处理内存中的对象时，存在远程执行代码漏洞。成功利用此漏洞的攻击者可以控制受影响的目标系统。

为了利用此漏洞，攻击者会向 Windows Search 服务发送经特殊设计的消息。有权访问目标计算机的攻击者可以利用此漏洞提升特权并控制目标计算机。此外，在企业情形中，未经过身份验证的远程攻击者可能会通过 SMB 连接远程触发此漏洞，然后控制目标计算机。



**漏洞演示**



[![](https://p1.ssl.qhimg.com/t01b8f7bc5190fc3971.gif)](https://p1.ssl.qhimg.com/t01b8f7bc5190fc3971.gif)



** **

**危害等级**



**[+]严重**

** **

**影响版本**



**Microsoft Windows 10 3**

**Microsoft Windows 7 1**

**Microsoft Windows 8 1**

**Microsoft Windows Server 2008 2**

**Microsoft Windows Server 2012 2**

**Microsoft Windows Server 2016**

** **

**修复方案**



**1．强烈建议所有受影响用户，及时更新官方补丁。**

[https://portal.msrc.microsoft.com/zh-cn/security-guidance/advisory/CVE-2017-8543](https://portal.msrc.microsoft.com/zh-cn/security-guidance/advisory/CVE-2017-8543)

**2.下载安装“360安全卫士”进行防御**

[https://www.360.cn/](https://www.360.cn/)

**技术支持**

邮件至**g-cert-report@360.cn**
