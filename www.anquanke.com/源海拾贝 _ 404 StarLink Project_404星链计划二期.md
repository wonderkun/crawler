> 原文链接: https://www.anquanke.com//post/id/218236 


# 源海拾贝 | 404 StarLink Project：404星链计划二期


                                阅读量   
                                **231677**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01e10a3e3b9705bb41.png)](https://p3.ssl.qhimg.com/t01e10a3e3b9705bb41.png)



“404星链计划”是知道创宇404实验室于2020年8月开始的计划，旨在通过开源或者开放的方式，长期维护并推进涉及安全研究各个领域不同环节的工具化，就像星链一样，将立足于不同安全领域、不同安全环节的研究人员链接起来。

其中不仅限于突破安全壁垒的大型工具，也会包括涉及到优化日常使用体验的各种小工具，除了404自研的工具开放以外，也会不断收集安全研究、渗透测试过程中的痛点，希望能通过“404星链计划”改善安全圈内工具庞杂、水平层次不齐、开源无人维护的多种问题，营造一个更好更开放的安全工具促进与交流的技术氛围。

项目地址:
- [https://github.com/knownsec/404StarLink-Project](https://github.com/knownsec/404StarLink-Project)


## Contents
<li>
[Project](#project)
<ul>
<li>
[KunLun-M](https://github.com/knownsec/404StarLink-Project/blob/master/TOOLS_README.md#kunlun-m)
<ul>
- Kunlun-Mirror. Focus on white box tools used by security researchers- A simple xss bot template- the fastest subdomain enumeration tool- the Chrome extension with Zoomeye- pocsuite3 is an open-sourced remote vulnerability testing framework developed by the Knownsec 404 Team.- ZoomEye API SDK- WAM is a platform powered by Python to monitor “Web App”<li>
[bin_extractor](https://github.com/knownsec/404StarLink-Project/blob/master/TOOLS_README.md#bin_extractor)
<ul>
- A simple script for quickly mining sensitive information in binary files.- A script used to quickly test APIs or required parameters and cookies for a certain request.- ipstatistics is a script based on the ipip library that is used to quickly filter the ip list.- cidrgen is based on cidr’s subnet IP list generator


## Project

该分类下主要聚合各类安全工具，偏向于可用性较高的完整项目。

### <a class="reference-link" name="KunLun-M"></a>KunLun-M

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E9%93%BE%E6%8E%A5%EF%BC%9A"></a>**项目链接：**

[https://github.com/LoRexxar/Kunlun-M](https://github.com/LoRexxar/Kunlun-M)

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E7%AE%80%E8%BF%B0%EF%BC%9A"></a>**项目简述：**

Kunlun-Mirror是从Cobra-W2.0发展而来，在经历了痛苦的维护改进原工具之后，昆仑镜将工具的发展重心放在安全研究员的使用上，将会围绕工具化使用不断改进使用体验。

目前工具主要支持php、javascript的语义分析，以及chrome ext, solidity的基础扫描.

KunLun-M可能是市面上唯一的开源并长期维护的自动化代码审计工具，希望开源工具可以推动白盒审计的发展:&gt;.

### <a class="reference-link" name="LBot"></a>LBot

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E9%93%BE%E6%8E%A5%EF%BC%9A"></a>**项目链接：**

[https://github.com/knownsec/LBot](https://github.com/knownsec/LBot)

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E7%AE%80%E8%BF%B0%EF%BC%9A"></a>**项目简述：**

XSS Bot是CTF比赛中出XSS的一大门槛，后端性能不够，环境处理不完善各种都会影响到Bot的每一环。

LBot是脱胎于爬虫的简单模板，配合相应的功能，可以方便快捷的完成一个成熟的Bot。



## Minitools

该分类下主要聚合各类安全研究过程中涉及到的小工具、脚本，旨在优化日常安全自动化的使用体验。

### <a class="reference-link" name="bin_extractor"></a>bin_extractor

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E9%93%BE%E6%8E%A5%EF%BC%9A"></a>**项目链接：**

[https://github.com/knownsec/Minitools-bin_extractor](https://github.com/knownsec/Minitools-bin_extractor)

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E7%AE%80%E8%BF%B0%EF%BC%9A"></a>**项目简述：**

一个简单的用于快速挖掘二进制文件中敏感信息的脚本。可以用来快速挖掘并验证二进制文件中的url链接等敏感信息。

### <a class="reference-link" name="CookieTest"></a>CookieTest

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E9%93%BE%E6%8E%A5%EF%BC%9A"></a>**项目链接：**

[https://github.com/knownsec/Minitools-CookieTest](https://github.com/knownsec/Minitools-CookieTest)

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E7%AE%80%E8%BF%B0%EF%BC%9A"></a>**项目简述：**

用于快速测试api或某个请求的必选参数、cookie的脚本。可以用来快速确认某个api的必选参数以便进一步测试渗透等.
