> 原文链接: https://www.anquanke.com//post/id/86271 


# 【重大漏洞预警】Windows两个关键远程代码执行漏洞


                                阅读量   
                                **251702**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0171236ed84dbe6b33.jpg)](https://p0.ssl.qhimg.com/t0171236ed84dbe6b33.jpg)

**微软6月补丁日披露两个正在被利用的远程代码执行漏洞(CVE-2017-8543)Windows Search远程代码执行漏洞和(CVE-2017-8464)LNK文件（快捷方式）远程代码执行漏洞。**



****

**漏洞名称：Windows Search远程代码执行漏洞**

**漏洞编号：**CVE-2017-8543

**漏洞等级：****严重**

**漏洞概要：**Windows搜索服务（WSS）是windows的一项默认启用的基本服务。允许用户在多个Windows服务和客户端之间进行搜索。当Windows搜索处理内存中的对象时，存在远程执行代码漏洞。成功利用此漏洞的攻击者可以控制受影响的系统。

为了利用此漏洞，攻击者可以向Windows Search服务发送精心构造的SMB消息。从而利用此漏洞提升权限并控制计算机。此外，在企业场景中，未经身份验证的攻击者可以通过SMB服务连接远程触发漏洞，然后控制目标计算机。

**受影响版本**

桌面系统：Windows 10, 7, 8, 8.1, Vista, Xp和Windows RT 8.1

服务器系统：Windows Server 2016，2012，2008, 2003



**修复方案：**

桌面系统Windows 10, 7, 8.1和Windows RT 8.1；服务器系统：Windows Server 2016，2012，2008，可以通过Windows Update自动更新微软补丁的方式进行修复。

Windows 8, Vista, Xp和Windows Server 2003 可以通过选择对应版本然后手动更新补丁的方式进行更新

（补丁下载地址参考）[https://support.microsoft.com/zh-cn/help/4025687/microsoft-security-advisory-4025685-guidance-for-older-platforms](https://support.microsoft.com/zh-cn/help/4025687/microsoft-security-advisory-4025685-guidance-for-older-platforms) 





**漏洞名称：LNK文件（快捷方式）远程代码执行漏洞**

**漏洞编号：**CVE-2017-8464

**漏洞等级：****严重**

**漏洞概要：**如果用户打开攻击者精心构造的恶意LNK文件，则会造成远程代码执行。成功利用此漏洞的攻击者可以获得与本地用户相同的用户权限。

攻击者可以通过可移动驱动器（U盘）或远程共享等方式将包含恶意LNK文件和与之相关的恶意二进制文件传播给用户。当用户通过Windows资源管理器或任何能够解析LNK文件的程序打开恶意的LNK文件时，与之关联的恶意二进制代码将在目标系统上执行。

**受影响版本**

桌面系统：Windows 10, 7, 8.1, 8, Vista和Windows RT 8.1

服务器系统：Windows Server 2016，2012，2008

**修复方案：**

桌面系统Windows 10,7,8.1和Windows RT 8.1；服务器系统：Windows Server 2016，2012，2008，可以通过Windows Update自动更新微软补丁的方式进行修复。

Windows 8, Vista可以通过选择对应版本然后手动更新补丁的方式进行更新

（补丁下载地址参考）[https://support.microsoft.com/zh-cn/help/4025687/microsoft-security-advisory-4025685-guidance-for-older-platforms](https://support.microsoft.com/zh-cn/help/4025687/microsoft-security-advisory-4025685-guidance-for-older-platforms) 



**参考**



[https://threatpost.com/microsoft-patches-two-critical-vulnerabilities-under-attack/126239/](https://threatpost.com/microsoft-patches-two-critical-vulnerabilities-under-attack/126239/)  

[https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8543](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8543) 

[https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8464](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8464) 

[https://support.microsoft.com/zh-cn/help/4025687/microsoft-security-advisory-4025685-guidance-for-older-platforms](https://support.microsoft.com/zh-cn/help/4025687/microsoft-security-advisory-4025685-guidance-for-older-platforms) 


