> 原文链接: https://www.anquanke.com//post/id/161903 


# 攻击者如何使用虚假浏览器更新攻击MikroTik路由器


                                阅读量   
                                **133655**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Malwarebytes，文章来源：blog.malwarebytes.com
                                <br>原文地址：[https://blog.malwarebytes.com/threat-analysis/2018/10/fake-browser-update-seeks-to-compromise-more-mikrotik-routers/](https://blog.malwarebytes.com/threat-analysis/2018/10/fake-browser-update-seeks-to-compromise-more-mikrotik-routers/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01685cc77cab2b8239.jpg)](https://p3.ssl.qhimg.com/t01685cc77cab2b8239.jpg)

## 概述

MikroTik是一家拉脱维亚公司生产的路由器和ISP无线系统，在过去几个月中，该产品一直在应对其操作系统存在的数个安全漏洞。自2018年4月下旬研究人员发现RouteOS中存在一个严重漏洞（ [https://forum.mikrotik.com/viewtopic.php?t=133533](https://forum.mikrotik.com/viewtopic.php?t=133533) ）以来，针对该产品的攻击一直在以惊人的增长速度发生。更糟糕的是，随着CVE-2018-14847漏洞利用方法（ [https://www.exploit-db.com/exploits/45578/](https://www.exploit-db.com/exploits/45578/) ）的出现，产品遭受到了更为猛烈的攻击。

尽管厂商已经发布了安全补丁程序，但目前仍有大量MikroTik路由器没有更新补丁，并且被攻击者成功攻陷，这样一来就产生了严重的安全问题。攻击者根据概念证明（PoC）代码，在短时间内迅速攻陷了数十万台设备。在去年夏天，SpiderLabs的研究人员通过被入侵后的MikroTik设备，发现了可能是迄今为止最大规模的Coinhive恶意活动（ [https://www.trustwave.com/Resources/SpiderLabs-Blog/Mass-MikroTik-Router-Infection-%E2%80%93-First-we-cryptojack-Brazil,-then-we-take-the-World-/](https://www.trustwave.com/Resources/SpiderLabs-Blog/Mass-MikroTik-Router-Infection-%E2%80%93-First-we-cryptojack-Brazil,-then-we-take-the-World-/) ），现在这一恶意活动的覆盖范围可能更加广泛。

通过最新的攻击方法，被感染的路由器可以向用户展示一个虚假的浏览器更新页面。当用户运行此恶意更新时，会将恶意代码解压缩到计算机上。随后，被感染计算机将在网络上执行扫描，发现其他存在漏洞的路由器，并尝试对它们进行漏洞利用。



## 可疑的浏览器更新

安全研究员[@VriesHd](https://github.com/VriesHd)率先发现了一种新的恶意活动（ [https://twitter.com/VriesHd/status/1049775664235208706](https://twitter.com/VriesHd/status/1049775664235208706) ），攻击者试图利用典型的社会工程学技术，尝试进一步攻陷存在漏洞的路由器。假如网络供应商存在受感染的MikroTik路由器，那么就会将终端用户的合法请求跳转到一个写着“旧版浏览器”的重定向页面：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/fake_update.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/fake_update.png)

根据Censys的调查结果（ [https://censys.io/ipv4?q=%22During+the+opening+of+the+site%22+AND+%22MikroTik+Device%22](https://censys.io/ipv4?q=%22During+the+opening+of+the+site%22+AND+%22MikroTik+Device%22) ），现在有大约11000个被感染的MikroTik设备上托管了这一假冒的下载页面：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/censys_results.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/censys_results.png)

可疑浏览器更新文件将会从指定FTP服务器下载，如下所示：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/sourcecode.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/sourcecode.png)

有意思的是，这一IP地址也作为免费公开的Web代理在网络上发布。一些希望绕过某些国家或地区网络限制的用户（例如，不在美国的用户想要观看美国版的Netflix），或者是希望隐藏自己真实IP地址的用户，通常会使用代理。

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/free_proxy.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/free_proxy.png)



## Payload分析

### <a name="%E8%A1%8C%E4%B8%BA%E5%88%86%E6%9E%90"></a>行为分析

Payload将自己伪装成一个名为updbrowser的安装程序。

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/upd_browser.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/upd_browser.png)

当我们运行恶意安装程序时，会弹出一个错误提示。

![]( [https://blog.malwarebytes.com/wp-content/uploads/2018/10/error_popup](https://blog.malwarebytes.com/wp-content/uploads/2018/10/error_popup).png)

然而，如果我们在这时对网络流量进行捕获，可以看到它实际上在后台扫描各种IP地址，并尝试连接8291端口（通过Winbox应用程序管理MicroTik路由器的默认端口）：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/probing.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/probing.png)

### <a name="%E8%84%B1%E5%A3%B3%E8%BF%87%E7%A8%8B"></a>脱壳过程

投放的Payload是一个相对较大的可执行文件（文件大小为7.25MB）。经过分析，其头部内容及可视化视图如下：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/sections_.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/sections_.png)

我们通过其名称上的特征，发现该恶意软件使用了一个流行且简单的加壳工具UPX（ [https://upx.github.io/](https://upx.github.io/) ）进行加壳。根据其叠加的大小判断，该文件中还包含更多需要提取的内容。经过进一步分析，发现该恶意软件会将Python DLL和其他相关文件解压到%TEMP%文件夹中，然后对它们进行加载。由此，很容易猜测这个EXE实际上是一个经过包装后的Python脚本。我们可以参考这里的步骤对其进行脱壳： [https://hshrzd.wordpress.com/2018/01/26/solving-a-pyinstaller-compiled-crackme/](https://hshrzd.wordpress.com/2018/01/26/solving-a-pyinstaller-compiled-crackme/) 。

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/extracted_.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/extracted_.png)

入口点位于名为upd_browser的脚本中。在对脚本进行反编译和跟踪之后，我们有两个Python脚本是该恶意软件的核心，分别是upd_browser.py和ups.py。

### <a name="%E6%B7%B1%E5%85%A5%E5%88%86%E6%9E%90%E8%84%9A%E6%9C%AC"></a>深入分析脚本

该脚本模块中的main函数（ [https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-upd_browser-py-L95](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-upd_browser-py-L95) ）比较简单：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/main_func_.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/main_func_.png)

如我们所见，弹出的错误提示是硬编码的（ [https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-upd_browser-py-L97](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-upd_browser-py-L97) ）。也就是说，它并不是一个实际发生的错误，而是一个掩人耳目的手段。

在弹出错误提示之后，恶意软件通过查询跟踪器的硬编码地址，来记录被感染设备的IP地址，这一跟踪器实际上利用了合法服务IP Logger。该跟踪器使用了一个像素大小的图像形式进行记录：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/iplogger_.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/iplogger_.png)

此后，会在预先定义好的指定时间间隔后，重复查询该地址。

最关键的操作是在名为scan的函数（ [https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-upd_browser-py-L75](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-upd_browser-py-L75) ）中执行的，该函数部署在多个并行线程中（最大线程数定义为thmax=600）。函数scan会生成伪随机IP地址，并尝试通过上文所述的8291端口连接这些地址。如果连接成功，那么就会在56778-56887端口范围内随机尝试进行另一个连接。如果失败，那么就继续漏洞利用过程：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/scan_addrs_.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/scan_addrs_.png)

函数poc（ [https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-upd_browser-py-L5](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-upd_browser-py-L5) ）的作用是利用已知漏洞感染路由器。该函数首先尝试利用路径遍历漏洞（CVE-2018-14847）来检索被感染主机上的凭据：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/get_user_pass_.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/get_user_pass_.png)

user.dat文件应为M2格式，因此脚本附带一个内置的解析器（也就是loadfile函数， [https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-ups-py-L117](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-ups-py-L117) ）：

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/m2_parser_fragment-1.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/m2_parser_fragment-1.png)

如果从user.dat文件中成功检索到密码，就会解密凭据，并使用该凭据来创建后门：一个管理员账户，其密码是随机生成的。此外，还设置了路由器执行的计划任务。

调度程序中设置的脚本，是根据硬编码的模板（ [https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-ups-py-L30](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-ups-py-L30) ）生成的。在这里，我们提供了整理后的版本： [https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-script_template-txt](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-script_template-txt) 。该脚本的作用是，修改路由器的配置，并且设置能加载CoinHive挖矿程序的错误页面。

错误页面可能位于以下两个位置：webproxy/error.html或flash/webproxy/error.html。

[![](https://blog.malwarebytes.com/wp-content/uploads/2018/10/proxy_view.png)](https://blog.malwarebytes.com/wp-content/uploads/2018/10/proxy_view.png)

两个错误页面的内容如下：

[https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-script_template-txt-L42](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-script_template-txt-L42)

[https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-script_template-txt-L43](https://gist.github.com/malwarezone/e437bb06d0d19a2d02ffd98cffe2b2c4#file-script_template-txt-L43)

只要用户访问了拒绝访问的URL，就会向用户显示这样的错误页面。但是，经过对路由器中配置的恶意脚本进行分析，我们发现基本上任何HTTP请求都会产生错误。然而，由于这一错误页面的目的是针对原始流量实现欺骗，因此请求的页面会显示为iframe。因此，用户依然可以正常浏览大部分网页，而不会注意到有异常之处。例如：

![]( [https://blog.malwarebytes.com/wp-content/uploads/2018/10/coinhive](https://blog.malwarebytes.com/wp-content/uploads/2018/10/coinhive).png)

CoinHive挖矿程序是嵌入式的，因此在这段时间内，被感染主机将被用于挖矿。



## 缓解措施

针对MikroTik用户，建议尽快在路由器上运行更新补丁。如果目前运行的仍为受漏洞影响版本，那么应该假设系统上的身份验证凭据已经发生泄漏。在MikroTik的下载页面（ [https://mikrotik.com/download](https://mikrotik.com/download) ）上，介绍了如何升级RouterOS。

由于很多用户不会习惯性地升级路由器，因此这些用户应该清楚这一漏洞的存在，并且了解漏洞利用的难度。然而，许多终端用户无法进行路由器的更新，还需要他们的网络供应商在上游来执行这一操作。

从这次攻击的案例中，我们可以看到，攻击者如何感染普通用户，并使用他们的计算机扫描互联网上其他存在漏洞的路由器。这种技术非常聪明，因为扫描行为需要大量的时间和资源，而将这一任务分布到每一台被感染主机，无疑效率是更高的。



## IoC

样本哈希值：

57EB8C673FC6A351B8C15310E507233860876BA813ED6AC633E9AF329A0BBAA0

ConHive站点密钥：

oiKAGEslcNfjfgxTMrxKGMJvh436ypIM

5zHUikiwJT4MLzQ9PLbU11gEz8TLCcYx

5ROof564mEBQsYzCqee0M2LplLBEApCv

qKoXV8jXlcUaIt0LGcMJIHw7yLJEyyVO

ZsyeL0FvutbhhdLTVEYe3WOnyd3BU1fK

ByMzv397Mzjcm4Tvr3dOzD6toK0LOqg

joy1MQSiGgGHos78FarfEGIuM5Ig7l8h

ryZ1Dl4QYuDlQBMchMFviBXPL1E1bbGs

jh0GD0ZETDOfypDbwjTNWXWIuvUlwtsF

BcdFFhSoV7WkHiz9nLmIbHgil0BHI0Ma
