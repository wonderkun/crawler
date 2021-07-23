> 原文链接: https://www.anquanke.com//post/id/180327 


# Evernote Chrome扩展漏洞分析


                                阅读量   
                                **183039**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者guard，文章来源：guard.io
                                <br>原文地址：[https://guard.io/blog/evernote-universal-xss-vulnerability](https://guard.io/blog/evernote-universal-xss-vulnerability)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01f97232f9cbb64004.png)](https://p4.ssl.qhimg.com/t01f97232f9cbb64004.png)



## 0x00 前言

2019年5月，Guardio研究团队发现了Evernote Web Clipper Chrome插件中的一个严重漏洞。这是一个逻辑缺陷，攻击者可以借此破坏域名隔离机制，以用户身份来执行代码，最终访问敏感用户信息（不局限于Evernote自己的域名）。金融、社交媒体、个人邮件等其他信息都是攻击者潜在的目标。这个通用型XSS漏洞编号为CVE-2019-12592。

成功利用漏洞后，如果用户访问攻击者控制的网站，第三方网站就可以窃取访问者的私密数据。在PoC中，Guardio演示了如何利用该漏洞访问社交媒体（读取并发表社交内容）、金融交易历史、个人购物清单等。

由于Guardio及时反馈，Evernote已经修复该漏洞，并在几天内推出了新版本。



## 0x01 背景

现在大多数互联网用户已经不需要下载可执行文件或者安装专用软件。对于社交账户、购物以及金融领域，用户们已经越来越倾向于直接使用浏览器提供的软件及工具。

这种场景也给app开发者带来了不小挑战。某些工具需要更多访问权限，才能更出色地完成任务，此时就轮到浏览器扩展（extension）派上用场。虽然app开发者的初衷是提供更好的用户体验，但扩展通常具备访问大量敏感资源的权限，因此与传统网站相比可能会带来更大的安全风险。

在Guardio安全研究工作中，我们的研究人员发现了Evernote Web Clipper Chrome扩展中的一个严重漏洞。由于Evernote现在使用范围特别广泛，这个问题影响范围较大，在本文撰写时大概有超过4,600,000用户受到影响。

与之前扩展中的严重漏洞相比（比如大家熟悉的Grammarly安全漏洞），这个漏洞会直接影响第三方服务，因此攻击范围不局限于用户的Evernote账户。



## 0x02 PoC

为了演示攻击者如何利用这个漏洞，Guardio发布了一个PoC，可以悄无声息窃取用户的敏感信息。将几个攻击步骤结合在一起后，我们能看到令人惊讶的攻击效果。

PoC攻击步骤：

1、用户浏览攻击者控制的恶意网站（比如社交媒体、邮件或者恶意博客评论等）；

2、恶意网站悄悄加载隐藏的、合法的目标站点`iframe`标签（链接）；

3、恶意网站触发漏洞，导致Evernote内部架构将攻击者控制的payload注入所有`iframe`上下文中；

4、注入的payload为每个目标网站专门定制，可以窃取cookie、凭据、私密信息、以用户身份操作等。

[![](https://p3.ssl.qhimg.com/t01ad01e9b58c158d04.png)](https://p3.ssl.qhimg.com/t01ad01e9b58c158d04.png)



## 0x03 漏洞细节

为了理解漏洞细节，我们首先需要大概了解Evernote Web Clipper Chrome插件如何与站点及frame交互。

Evernote的代码注入链可以追溯到扩展的`manifest`文件（`manifest.json`），其中`BrowserFrameLoader.js`内容脚本会以声明方式被注入到所有网页及frame中。需要注意的是，由于注入frame的行为比较敏感，因此这似乎是使用`all_frames`指令注入的唯一脚本，这样可以减少可能存在的攻击面。这个脚本的主要目标是承担小型的命令及控制服务器角色，以便根据需要将其他代码载入页面中。

[![](https://p2.ssl.qhimg.com/t011b4a07d652b49259.png)](https://p2.ssl.qhimg.com/t011b4a07d652b49259.png)

在通信渠道方面，该脚本通过`postMessage` API来实现窗口消息传递。作为小型注入脚本，该脚本只为几种消息类型提供处理接口（handler），其中就包含`installAndSerializeAll`命令，该命令可以注入第二阶段的`FrameSerializer.js`，执行序列化操作。这种机制采用了弱认证方案，本身并不是一个漏洞，但可以作为后续漏洞利用链的支撑点，在网站沙盒上下文中运行的脚本可以触发后续命令。这个消息处理接口涉及到的参数（这里为`resourcePath`及`target`）可以作为命令请求消息中的payload字段进行传递。

[![](https://p4.ssl.qhimg.com/t01795ff41377879eb9.png)](https://p4.ssl.qhimg.com/t01795ff41377879eb9.png)

`_getBundleUrl`函数本来的功能是向该扩展的命令空间（`chrome-extension://...`）提供有效的URL，但由于代码逻辑疏忽，并且没有对输入进行清洗过滤，因此我们可以使用前面接口的`resourcePath`输入参数来篡改URL的第一部分数据。

[![](https://p0.ssl.qhimg.com/t01265e98ee495762e3.png)](https://p0.ssl.qhimg.com/t01265e98ee495762e3.png)

将这些细节组合成完整的利用链，该漏洞可以允许远程攻击者通过简单的一条`window.postMessage`命令，将自己可控的脚本载入其他网站的上下文中。通过滥用Evernote的注入框架，恶意脚本可以被注入到页面的所有目标frame中，无视跨域策略约束。

[![](https://p2.ssl.qhimg.com/t01a3a2113eca3b1c7b.png)](https://p2.ssl.qhimg.com/t01a3a2113eca3b1c7b.png)

攻击者可以通过这种方法，通过可控的任何网站实现通用型XSS注入。漏洞利用成功后，攻击者还可以执行各种操作，Guardio在向Evernote提供的PoC中只给出了一些攻击场景，实际上利用场景要广泛得多。



## 0x04 缓解措施

Evernote已经发布了补丁，向用户推出了新版本。大家可以访问Evernote Chrome扩展页面（`chrome://extensions/?id=pioclpoplcdbaefihamjohnefbikjilc`，出于安全原因，需要手动将该地址拷贝到浏览器地址栏），查看是否安装了最新版本，确保当前版本号不低于7.11.1。

这个漏洞表明，我们需要重视浏览器扩展的安全性，只安装来自于可信源的扩展，毕竟攻击者只需要一个不安全的扩展就能对用户的在线数据造成威胁（如金融、社交媒体、个人邮件等数据）。



## 0x05 时间线

Evernote安全团队高度负责，及时修复了这个漏洞，具体时间线如下：
- 2019年5月27日 – 提交漏洞反馈
- 2019年5月28日 – 官方回复邮件
- 2019年5月28日 – 确认问题，并归到漏洞类别
<li>2019年5月29日 – Evernote安全页面上提到[相关内容](https://evernote.com/security/report-issue/)
</li>
- 2019年5月31日 – 发布Evernote Web Clipper 7.11.1版
- 2019年6月4日 – 确认问题已修复