> 原文链接: https://www.anquanke.com//post/id/151514 


# Intel Active Management Technology（AMT）漏洞预警


                                阅读量   
                                **158104**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t011f73ccb8f9a00d9d.jpg)](https://p2.ssl.qhimg.com/t011f73ccb8f9a00d9d.jpg)

报告编号： B6-2018-071101

报告来源： 360CERT

报告作者： 360CERT

更新日期： 2018-07-11



## 0x00 事件概述

近日英特尔公司对Intel Active Management Technology（intel AMT）进行更新，修补3个补丁，编号为：CVE-2018-3628 ， CVE-2018-3629， CVE-2018-3632。 在使用英特尔处理器的PC设备上启用AMT技术，AMT固件版本在 3.x至11.x 之间的物联网设备，工作站，服务器会受到该漏洞影响。

360-CERT团队经过评估，认为漏洞风险等级重要，建议用户参照相关修复建议进行防御。



## 0x01 技术背景

Intel AMT其全称为INTEL Active Management Technology(英特尔主动管理技术)，它是一种集成在芯片中的系统，不依赖特定的操作系统，这也是Intel AMT与远程控制软件最大的不同。 即使计算机属于关闭状态，或者操作系统故障，通过此技术都可以进行远程管理。



## 0x02 漏洞描述

CVE-2018-3628：在英特尔Converged Security Manageability Engine（CSME）固件中的AMT模块的Http处理程序中存在缓冲区溢出漏洞，攻击者可以通过构造恶意的HTTP请求来发起攻击，从而控制局域网中存在漏洞的机器，来执行恶意代码。

严重性：高

受影响固件版本：3.x至11.x

CVE-2018-3629：在英特尔Converged Security Manageability Engine（CSME）固件中的AMT模块的Event处理程序中存在缓冲区溢出漏洞，攻击者可以构造恶意代码来使目标机造成拒绝服务。

严重性：高

受影响固件版本：3.x至11.x

CVE-2018-3632：在英特尔Converged Security Manageability Engine（CSME）固件中上的AMT模块中存在内存破坏漏洞，攻击者可以构造恶意代码来进行本地代码提权。

严重性：中

受影响固件版本：6.x/7.x/8.x/9.x/10.x/11.0/11.5/11.6/11.7/11.10/11.20



## 0x03 影响范围

在使用英特尔处理器的PC设备上启用AMT技术，AMT固件版本在 3.x至11.x 之间的物联网设备，工作站，服务器会受到影响。

受影响CPU型号如下：

•英特尔®酷睿™2双核vPro™和英特尔®迅驰™2博锐™

•1至8代英特尔睿™处理器家族

•英特尔®至强®处理器E3-1200 v5和v6产品系列（Greenlow）

•英特尔®至强®处理器可扩展系列（Purley）

•英特尔®至强®处理器W系列（Basin Falls）



## 0x04 修复建议

建议用户尽快更细固件到最新版本。

|受影响CPU系列|已修复漏洞的固件版本或更高版本
|------
|4th Generation Intel® Core™ 处理器系列|Intel® CSME 9.1.43 Intel® CSME 9.5.63
|5th Generation Intel® Core™ 处理器系列|Intel® CSME 10.0.57
|6th Generation Intel® Core™ 处理器系列|Intel® CSME 11.8.50
|7th Generation Intel® Core™ 处理器系列|Intel® CSME 11.8.50
|8th Generation Intel® Core™ 处理器系列|Intel® CSME 11.8.50
|Intel® Xeon® Processor E3-1200 v5 &amp; v6 产品系列|Intel® CSME 11.8.50
|Intel® Xeon® 处理器可扩展系列|Intel® CSME 11.21.51
|Intel® Xeon® 处理器W系列|Intel® CSME 11.11.50

英特尔表示不再支持以下产品的英特尔®CSME固件。没有对以下系列CPU提供固件更新：

英特尔®酷睿™2双核vPro™

英特尔®迅驰™2博锐™

第一代英特尔®酷睿™

第二代英特尔®酷睿™

第三代英特尔®酷睿™



## 0x05 时间线

2018-07-10 英特尔发布相关公告

2018-07-11 360CERT发布预警



## 0x06 参考链接

[https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00112.html](https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00112.html)
