> 原文链接: https://www.anquanke.com//post/id/249441 


# 医疗气动管道(PTS)系统中的PwnedPiper漏洞使美国80%以上医院受到影响


                                阅读量   
                                **20505**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[]()

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0197adf11d1c0089eb.jpg)](https://p3.ssl.qhimg.com/t0197adf11d1c0089eb.jpg)



网络安全部门Armis的研究人员披露了一组名为PwnedPiper的九个漏洞，这些漏洞可能会使医院的气动管道系统（PTS）遭受恶意攻击。

瑞仕格医疗公司制造的气动管道(PTS)系统能够通过气动管道实现医院内物资的自动化运输，北美百分之八十以上医院及全球范围内数千家医院均使用了该系统。而这些系统存在着名为PwnedPiper的漏洞，这些漏洞可以使攻击者控制PTS传输系统，进行中间人攻击等网络攻击并部署勒索软件等。

[![](https://p0.ssl.qhimg.com/t018c96cbfd71dbb960.png)](https://p0.ssl.qhimg.com/t018c96cbfd71dbb960.png)

Armis的研究人员在报告（[https://www.armis.com/research/pwnedpiper）](https://www.armis.com/research/pwnedpiper%EF%BC%89) 中指出这些漏洞可以让攻击者不需要进行身份验证的情况下控制 Translogic PTS 站点，从而掌控医院的整个 PTS 网络，同时，该攻击也可能会引发勒索或信息泄露等后续行为。

此外，漏洞还可能引发权限升级、内存损坏、远程控制和拒绝服务等一系列问题和通过固件升级导致的系统崩溃。

研究人员披露的九个漏洞信息分别为：<br>
• CVE-2021-37161 udpRXThread中的下溢<br>
• CVE-2021-37162 sccProcessMsg中的溢出<br>
• CVE-2021-37163 Telnet服务器默认密码<br>
• CVE-2021-37164 tcpTxThread堆栈溢出<br>
• CVE-2021-37165 hmiProcessMsg溢出<br>
• CVE-2021-37166 GUI套接字拒绝服务<br>
• CVE-2021-37167 root用户脚本可用于PE<br>
• CVE-2021-37160 固件升级可不经验证（未经授权、未加密、未签名）

Swisslog新发布的7.2.5.7版本修复了绝大多数漏洞，但其中的 CVE-2021-37160尚未被修复。
