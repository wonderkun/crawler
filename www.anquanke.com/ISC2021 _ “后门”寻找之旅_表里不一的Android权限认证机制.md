> 原文链接: https://www.anquanke.com//post/id/249465 


# ISC2021 | “后门”寻找之旅：表里不一的Android权限认证机制


                                阅读量   
                                **27036**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t017bcb381194b1ea42.jpg)](https://p2.ssl.qhimg.com/t017bcb381194b1ea42.jpg)



7月29日，第九届互联网安全大会（ISC 2021）漏洞研究分论坛上，字节跳动无恒实验室安全研究员张清和夏光帅同学带来了《“后门”寻找之旅：表里不一的Android权限认证机制》的议题，该议题聚焦于Android权限管控机制的一些常见问题和设计缺陷，通过历史多个安全漏洞，提出了系统权限管控设计的4条基本原则，以此来提醒和帮助厂家提高系统权限认证模型的安全性。

[![](https://p2.ssl.qhimg.com/t0154b9acca15c5540d.jpg)](https://p2.ssl.qhimg.com/t0154b9acca15c5540d.jpg)



## 一、问题：

当用户在Android等多种移动操作系统中进行系统重置、密码重置等敏感操作时，系统需要多重权限认证来验证操作者身份，来确保操作行为的安全性。在这些身份验证的体系或模型中，同一行为在不同操作路径上进行的权限认证需要保持前后一致。例如，在系统中完成某一行为存在A/B两个接口，无论从A接口还是B接口接入操作，其授权机制都应该是完全相同，如果A接口的权限校验机制比B接口要轻松很多，那A接口对于这个系统而言就是一个后门或者是一个漏洞，A接口的存在严重破坏了这个系统的权限体系设计原则。

在我们过去几年对于Android系统的研究中，我们发现了诸多破坏Android权限模型的漏洞，这些漏洞严重破坏了Android权限体系的完整性，危害严重。在本次研究中，我们对相关问题进行了整理和场景分类，总结出一些通用性安全设计原则，以此来提醒和帮助厂家提高系统权限认证模型的安全性。



## 二、技术背景：

### <a class="reference-link" name="2.1%20%E6%9D%83%E9%99%90%E6%8E%A7%E5%88%B6%E4%BD%93%E7%B3%BB%EF%BC%9A"></a>2.1 权限控制体系：

从信息安全角度，权限的控制体系分为认证、授权、鉴权和权限控制四个方面。

认证：是指根据声明者所特有的识别信息，确认声明者的身份。最常见的认证实现方式是通过用户名和密码，此外：手机短信、手势密码、身份证、指纹、密保问题等。

授权：是指资源所有者委派执行者，赋予执行者指定范围的资源操作权限，以便执行者代理执行对资源的相关操作。

鉴权：主要是对声明者所声明的真实性进行校验。授权和鉴权是两个上下游相匹配的关系，先授权，后鉴权。

权限控制是指对可执行的各种操作组合配置为权限列表，然后根据执行者的权限，若其操作在权限范围内，则允许执行，否则禁止。

### <a class="reference-link" name="2.2%20Android%E6%9D%83%E9%99%90%E6%8E%A7%E5%88%B6%E4%BD%93%E7%B3%BB%EF%BC%9A"></a>2.2 Android权限控制体系：

Android权限授权体系分为用户和应用两个方面。

用户认证主要体现在系统用户识别、多用户管理，认证方式通常为密码（PIN、Pattern）、指纹、人脸等。

[![](https://p0.ssl.qhimg.com/t01057aaab50234027b.png)](https://p0.ssl.qhimg.com/t01057aaab50234027b.png)

应用认证在Android中有沙箱隔离、签名管理、权限（normal、dangerous、signature等级别）管理、selinux等。

[![](https://p0.ssl.qhimg.com/t0198e746ae7006000a.png)](https://p0.ssl.qhimg.com/t0198e746ae7006000a.png)

### <a class="reference-link" name="2.3%20Android%E6%9D%83%E9%99%90%E6%8E%A7%E5%88%B6%E6%BC%8F%E6%B4%9E%E5%9C%BA%E6%99%AF%EF%BC%9A"></a>2.3 Android权限控制漏洞场景：

**① API调用存在“后门”：**

[![](https://p4.ssl.qhimg.com/t01528815a5feb579d2.png)](https://p4.ssl.qhimg.com/t01528815a5feb579d2.png)

针对同一套数据访问，接口A调用有权限认证，接口B无权限认证，给普通用户的感知变成了一个“后门”。

**② 敏感界面被越权绕过**

[![](https://p4.ssl.qhimg.com/t01d5c357b89a2be5a4.png)](https://p4.ssl.qhimg.com/t01d5c357b89a2be5a4.png)

针对敏感界面S，应该通过C进行认证才能打开，但是由于逻辑漏洞导致可以越过中间认证操作，直接打开敏感界面。

### <a class="reference-link" name="2.4%20%E5%85%B8%E5%9E%8B%E6%BC%8F%E6%B4%9E%EF%BC%9A"></a>2.4 典型漏洞：

在Android系统中，常用的存在鉴权体系的模块有Recovery模式、工程模式、查找手机、锁屏密码、应用加密、文件保险箱等。如果鉴权不当，很容易造成越权漏洞，比如我们近期研究发现的Recovery模式或工程模式可越权格式化手机、锁屏密码hash存储不当导致可被爆破、自添加系统API未鉴权任意拨打电话、查找手机逻辑校验不当导致任意锁定及格式化手机等。轻则会未经用户同意窃取各种敏感数据、获取锁屏密码，严重则会导致用户手机重置，造成用户所有数据全部丢失。

[![](https://p4.ssl.qhimg.com/t01cefc555345c92b55.png)](https://p4.ssl.qhimg.com/t01cefc555345c92b55.png)

### <a class="reference-link" name="2.5%20Android%E6%9D%83%E9%99%90%E6%8E%A7%E5%88%B6%E7%9A%84%E5%AE%89%E5%85%A8%E5%8E%9F%E5%88%99%EF%BC%9A"></a>2.5 Android权限控制的安全原则：

根据上述漏洞成因，我们总结Android的权限控制安全原则如下：

[![](https://p3.ssl.qhimg.com/t0172a48c374513bff1.png)](https://p3.ssl.qhimg.com/t0172a48c374513bff1.png)

**粗细适中：**权限划分，权限颗粒度适中；

**表里如一：**使用同一套鉴权方法，不能公开接口有权限，“后门”接口无权限；

**一脉相承：**自添加的能力和服务保持与Android原生同等级的鉴权方式，不能私自无故降级；

**从一而终：**比如android security boot、TLS的证书链式验证，环环相扣；



## 三、漏洞研究：

最近几年我们对国内外主流Android手机厂商的各种鉴权场景的脆弱性进行了研究，他们均存在着各种形式的越权问题，严重影响用户的个人数据安全。详细情况如下表所示，为了保护手机厂商的隐私，不同的Android手机厂商以A~G代替，具体的漏洞细节不再展示。

[![](https://p2.ssl.qhimg.com/t018f23e8b3c2d6fa49.png)](https://p2.ssl.qhimg.com/t018f23e8b3c2d6fa49.png)

工程模式是手机中系统级别的硬件管理程序，一般工程师会在工程模式中对手机的蓝牙、wifi、屏幕、电池以及各种传感器直接进行测试和操作，甚至可以直接格式化手机等，如果此处出现漏洞，则会直接影响设备的正常使用。recovery模式是指的是一种可以对安卓手机内部的数据或系统进行修改的模式，在这个模式下可以对已有的系统进行备份或升级，也可以在此恢复出厂设置。而查找手机也具有对手机进行恢复出厂设置的能力，当查找手机功能开启后，用户可以在其他终端设备对手机进行远程操作，包括远程锁定、格式化等。

然而在工程模式、recovery模式和查找手机相关功能场景中，我们发现很多手机厂商存在严重的鉴权漏洞，导致无需任何用户身份验证即可越权执行恢复出厂设置、格式化手机，导致用户个人数据完全丢失。

在锁屏密码以及私密文件、应用锁等具有相关密码设定的模块中，我们也发现了部分手机厂商由于鉴权漏洞导致可以越权获取、修改或移除密码等问题等等。

这些漏洞严重破坏了Android权限体系的完整性，直接影响着用户的个人数据和财产安全，若被恶意利用，危害极大。



## 四、总结：

如何避免这类问题呢？根据我们前面提出的Android权限控制的4条基本安全原则以及历史相关漏洞研究， 在权限认证中应该注意以下几个方面：
- 敏感操作要进行身份验证：比如密码重置、手机重置、找回手机、私密文件等场景。
- 权限校验要“表里如一”：不要关了一扇门，又打开了一扇窗。
- 自添加的服务和能力要保持与原生同等级的权限控制。
- 权限颗粒度设置适中，防止被以一当十。
在Android权限体系的设计中，无论是用户认证和应用鉴权，只有从权限的认证、授权、鉴权和权限控制四个方面做好综合考量和安全防护，不弱化某一环节、不留“后门”，才能从根本上杜绝越权问题的产生，从而保护用户数据和隐私安全。



## 五、关于无恒实验室：

无恒实验室是由字节跳动资深安全研究人员组成的专业攻防研究实验室，实验室成员具备极强的实战攻防能力，通过渗透入侵演练，业务蓝军演练，漏洞挖掘、黑产打击、漏洞应急、APT应急等手段，不断提升公司基础安全、数据安全、业务安全水位，极力降低安全事件对业务和公司的影响程度。同时为公司和各大产品提供定期的渗透测试服务，产出渗透测试报告。全力确保字节跳动用户在使用旗下产品与服务时的安全。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eb79686538ad6d03.png)

参考：<br>[http://www.hyhblog.cn/2018/04/25/user_login_auth_terms/](http://www.hyhblog.cn/2018/04/25/user_login_auth_terms/)<br>[https://securityaffairs.co/wordpress/107010/breaking-news/samsung-find-my-mobile-flaws.html](https://securityaffairs.co/wordpress/107010/breaking-news/samsung-find-my-mobile-flaws.html)<br>[https://xlab.tencent.com/cn/2021/05/14/A-Mirage-of-Safety-Bug-Finding-and-Exploit-Techniques-of-Top-Android-Vendors-Privacy-Protection-Apps/](https://xlab.tencent.com/cn/2021/05/14/A-Mirage-of-Safety-Bug-Finding-and-Exploit-Techniques-of-Top-Android-Vendors-Privacy-Protection-Apps/)<br>[https://support.google.com/pixelphone/answer/4596836?hl=en#zippy=%2Cwith-your-phones-buttons-advanced](https://support.google.com/pixelphone/answer/4596836?hl=en#zippy=%2Cwith-your-phones-buttons-advanced)
