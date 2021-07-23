> 原文链接: https://www.anquanke.com//post/id/84341 


# BlackHat2016第一天部分精彩议题分享（含PPT下载）


                                阅读量   
                                **90751**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01d3a36c3ed350173b.png)](https://p0.ssl.qhimg.com/t01d3a36c3ed350173b.png)

**想下载PPT的来这里**

**官方地址：**[**https://www.blackhat.com/us-16/briefings.html**](https://www.blackhat.com/us-16/briefings.html)

**国内网盘镜像：**[**https://yunpan.cn/c6kigEevIGK9w**](https://yunpan.cn/c6kigEevIGK9w) **（提取码：9419）**



<br>

**议题:**

**$HELL ON EARTH: FROM BROWSER TO SYSTEM COMPROMISE (从浏览器漏洞利用到SYSTEM权限）**

演讲者的照片和介绍

[![](https://p2.ssl.qhimg.com/t018eb0ec31b7a535c5.jpg)](https://p2.ssl.qhimg.com/t018eb0ec31b7a535c5.jpg)

[![](https://p1.ssl.qhimg.com/t013057fb22d745d2c9.jpg)](https://p1.ssl.qhimg.com/t013057fb22d745d2c9.jpg)

[![](https://p3.ssl.qhimg.com/t01fb687c72fac3e0ff.jpg)](https://p3.ssl.qhimg.com/t01fb687c72fac3e0ff.jpg)

[![](https://p4.ssl.qhimg.com/t0132c0ebd0c8c52f1e.jpg)](https://p4.ssl.qhimg.com/t0132c0ebd0c8c52f1e.jpg)

<br>

**演讲内容:**

通过浏览器或者默认浏览器插件来获得远程系统的SYSTEM/root权限,这在以前的pwn2own比赛中是很少见的,这个议题将会讲解今年Pwn2Own比赛中的Exploition chains(总共21个漏洞),议题会覆盖针对当代流行浏览器的利用,内核UAF漏洞的利用,以及内核中的目录递归漏洞和逻辑漏洞利用。议题中会详细分析所有的攻击面,利用技术,以及缓解措施(比如通过应用沙盒)。

<br>

**议题:**

**A JOURNEY FROM JNDI/LDAP MANIPULATION TO REMOTE CODE EXECUTION DREAM LAND （从历险<strong>JNDI/LDAP到远程代码执行的梦想大陆） **</strong>

演讲者的照片和介绍

[![](https://p3.ssl.qhimg.com/t01bb1d8f2d55793595.jpg)](https://p3.ssl.qhimg.com/t01bb1d8f2d55793595.jpg)

[![](https://p2.ssl.qhimg.com/t01344fab246f8e3456.jpg)](https://p2.ssl.qhimg.com/t01344fab246f8e3456.jpg)

<br>

**演讲内容:**

JNDI(Java Naming and Directory Interface,Java命名和目录接口)是一种标准的Java命名系统接口,JNDI提供统一的客户端API,通过不同的访问提供者接口JNDI服务供应接口(SPI)的实现,由管理者将JNDI API映射为特定的命名服务和目录系统,使得Java应用程序可以和这些命名服务和目录服务之间进行交互。JNDI可访问的现有的目录及服务有RMI, CORBA, LDAP, or DNS等等。

这个议题将会讲解一种叫做"JNDI Reference Injection(JNDI参考注入)” 的新漏洞类型,起初发现于攻击Java Applets (CVE-2015-4902)的恶意样本中,但是同样的概念也能用于攻击运行了JNDI查找的Web应用程序,如果攻击者能控制JNDI查找参数的话。在议题的演示中将会演示攻击者可以使用不同的技术运行任意代码在服务器执行JNDI查找时。议题会聚焦在RMI,LDAP和CORBA服务,因为这些服务几乎存在于每个企业的应用程序中

如果攻击者不能够修改LDAP的地址时,LDAP提供其他的攻击面,仍然可以修改LDAP目录,以及存储对象在LDAP执行搜索操作时来执行任意代码。

<br>

**议题:**

**A LIGHTBULB WORM? （编写LIGHTBULB蠕虫？）**

演讲者的照片和介绍

[![](https://p5.ssl.qhimg.com/t011abf8db34cdfded4.jpg)](https://p5.ssl.qhimg.com/t011abf8db34cdfded4.jpg)

**<br>**

**演讲内容:**

可否想过通过蠕虫感染智能灯泡网络?这个议题会演示针对飞利浦Hue智能灯系统搭建的网络进行演示,黑进bridge,接着访问内部网络。也会讲到如何绕过加密的bootloader读取敏感信息,并对多个飞利浦hue智能灯泡固件的进行讨论。

<br>

**议题:**

**AMSI: HOW WINDOWS 10 PLANS TO STOP SCRIPT-BASED ATTACKS AND HOW WELL IT DOES IT （Windows 10 如何阻止基于脚本的攻击，我们如何绕过他们）**

演讲者的照片和介绍

[![](https://p0.ssl.qhimg.com/t010d86ebfb7c475002.jpg)](https://p0.ssl.qhimg.com/t010d86ebfb7c475002.jpg)

<br>

**演讲内容:**

在windows10系统中,微软推出了AntiMalware扫描接口 (AMSI) 用于阻止基于恶意脚本的对系统的攻击,基于脚本的攻击方法,尤其是利用powershell编写的恶意脚本,在近年来对企业网络的威胁日益增加,AMSI的目标就是检测用Powershell,Vbscript,Jscript等脚本编写的恶意程序,当恶意代码发到脚本主机执行的时候,AMSI会检测和扫描脚本的恶意内容。AMSI也提供了开放接口可以被其他程序调用,微软能否因此阻止掉基于恶意脚本的攻击吗?

这个议题伴随着大量的演示,比如使用AMSI检测恶意脚本常见的执行方式,恶意脚本的存储方式已经由传统的存于硬盘的脚本转向可以从WMI命名空间/注册表/系统日志导入,那么AMSI默认情况下能检测出来吗?

利用installUtil/regsrv32/rundll32绕过白名单来执行脚本,AMSI能检测出来吗?

最后是给攻击者的福利,演示使用客户端攻击绕过AMSI,其中[https://github.com/Cn33liz/p0wnedShell已经实现了绕过AMSI](https://github.com/Cn33liz/p0wnedShell%E5%B7%B2%E7%BB%8F%E5%AE%9E%E7%8E%B0%E4%BA%86%E7%BB%95%E8%BF%87AMSI)的方法,感兴趣的同学可以去看看代码实现。

<br>

**议题:**

**ANALYSIS OF THE ATTACK SURFACE OF WINDOWS 10 VIRTUALIZATION-BASED SECURITY （分析windows 10 基于虚拟化的安全的攻击面）**

演讲者的照片和介绍

[![](https://p2.ssl.qhimg.com/t011a0cfed7510dc0db.jpg)](https://p2.ssl.qhimg.com/t011a0cfed7510dc0db.jpg)

**演讲内容:**

在windows 10,微软引进了基于虚拟化的安全特性(VBS),该特性是基于hypervisor的安全解决方案,在这个议题,将讨论VBS的实现细节以及可能遭受到的攻击面,VBS的虚拟化解决不同于其他,议题会专注底层平台的复杂性导致的潜在问题(UEFI固件是主要的一个例子)

除了大量的理论介绍,议题还会演示一个真正的漏洞利用,一个是对VBS自身的,一个是对漏洞固件的,前者不是很严重的漏洞(主要是绕过VBS的功能),后者是严重漏洞。

<br>

**议题:**

**APPLIED MACHINE LEARNING FOR DATA EXFIL AND OTHER FUN TOPICS**

演讲者的照片和介绍

[![](https://p4.ssl.qhimg.com/t01ff93200d7303981e.jpg)](https://p4.ssl.qhimg.com/t01ff93200d7303981e.jpg)

[![](https://p4.ssl.qhimg.com/t011114536fdd5e58d9.jpg)](https://www.blackhat.com/us-16/speakers/Xuan-Zhao.html)

[![](https://p3.ssl.qhimg.com/t010ccce4827b00e69d.jpg)](https://p3.ssl.qhimg.com/t010ccce4827b00e69d.jpg)

**演讲内容:**

机器学习这个概念在这几年在各个领域都很热门了,在安全产业更不例外,只要技术应用的恰当,就能够辅助分析许多以数据驱动的业务以及决策分析。机器学习这么技术是强大的,这个议题会讲一些实际的应用

首先这个议题会帮助研究人员,分析人员,安全爱好者讲解如何通过机器学习来处理一些脏活累活,我们会从想法到代码实现再到实际应用,其中在实现的时候遇到的坑,也会在议题中告诉你。一些实际的机器学习应用比如在数据提取过程中高级的混淆技术,大型网络映射,在海量URL中识别CC控制页面等。在会议结束后,研究人员会放出相应的代码供学习

<br>

**议题:**

**BADWPAD**

演讲者的照片和介绍

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0193550489170bdcc1.jpg)

<br>

**演讲内容:**

WPAD(web代理自动发现)协议允许计算机自动发现网络代理配置,主要用于网络客户端中仅能通过代理上网时的自动化解决方案,这是一个很古老的协议了,大概有20年了(RFC draft 1999-07-28),但是有很多的安全风险被忽略了,这个议题会演示几个由于WPAD糟糕的设计导致的安全问题,我们将这个议题取名为“BADWPAD"也是为了给你演示在不同情景下(比如在免费的WIFI环境网络中的攻击,在企业网络中的攻击)的恶意利用方式(泄露客户端的DNS,识别出到外网的HTTP请求),我们保证观众听后会对我们的实验结果表示惊讶,比如在机场贵宾室,在会议室,在酒店和技术上利用WIFI的攻击面,最后当然还会讲讲防御方法

<br>

**议题:**

**BEYOND THE MCSE: ACTIVE DIRECTORY FOR THE SECURITY PROFESSIONAL （活动目录的安全专业渗透）**

演讲者的照片和介绍

[![](https://p1.ssl.qhimg.com/t01fceb12f8c4410661.jpg)](https://p1.ssl.qhimg.com/t01fceb12f8c4410661.jpg)

**演讲内容:**

你毕业后是不是为了找工作,背题考过MCSE?,微软的活动目录在财富1000强的公司中,有95%都在使用。主要用于管理,认证。这意味着不管是对红队还是蓝队,熟悉活动目录的安全将会是自己一方的制胜武器之一,这个议题会讲解 (MS14-068)漏洞,也就是经典的kerberos一键通杀漏洞。组策略中间人漏洞 (MS15-011 &amp; MS15-014) ,以及在域入侵时,高级列举技术。

议题会覆盖:

从管理员,攻击者,信息安全人员眼中看活动目录的视角

森林和域名两者的区别,包括在多域的AD中的安全问题

描述域之间的信任关系给攻击者带来的机会

活动目录数据库的数据格式,文件,对象存储方式

RODC(只读域控)的安全概念以及潜在的安全风险

windows的认证协议在这些年中被发现的弱点,包括微软的下一代认证系统 Microsoft Passport

讲解在AD部署时微软云Azure AD 和 Office 365在安全方面的差异

讲解活动目录的安全功能以及最新的windows操作系统新增的安全功能实现

相信看完这个议题,你才是真的MCSE

**想下载PPT的来这里**

**官方下载地址：****[https://www.blackhat.com/us-16/briefings.html](https://www.blackhat.com/us-16/briefings.html)**

**<strong>国内网盘镜像：**</strong>**********[<strong>https://yunpan.cn/c6kigEevIGK9w**](https://yunpan.cn/c6kigEevIGK9w) **（提取码：9419）**</strong>


