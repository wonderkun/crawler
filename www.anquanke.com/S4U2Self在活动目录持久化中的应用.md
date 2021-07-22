> 原文链接: https://www.anquanke.com//post/id/170535 


# S4U2Self在活动目录持久化中的应用


                                阅读量   
                                **195110**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者alsid，文章来源：alsid.com
                                <br>原文地址：[https://alsid.com/company/news/abusing-s4u2self-another-sneaky-active-directory-persistence](https://alsid.com/company/news/abusing-s4u2self-another-sneaky-active-directory-persistence)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t014f4c6fdd671aa4c1.png)](https://p1.ssl.qhimg.com/t014f4c6fdd671aa4c1.png)



## 一、前言

[Elad Shamir](https://twitter.com/elad_shamir)最近在Kerberos委派上做了不少研究（参考这篇[文章](https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html)），在这基础上，我们准备发表一系列文章，深入分析之前未发现的攻击方法，也会帮蓝队提出实用的解决方案，可以衡量这种攻击方法对活动目录（Active Directory）基础设施的影响。

这是我们发布的第二篇文章，重点介绍的是Kerberos的`S4U2Self`扩展。Shamir在那篇文章中介绍了基于该功能的一种新型AD后门。本文会介绍攻击者如何部署并使用这种后门，并将这种技术拓展到不同类型的AD账户。这里我们还将调整委派方向，描述可能存在的另一种漏洞。在文末我们也会提出一些建议，帮助安全团队防御此类攻击场景。



## 二、理解S4U2Self后门

在之前的研究文章中，Shamir提出攻击者可以通过某种方式利用`msDS-AllowedToActOnBehalfOfOtherIdentity`属性，以便在AD基础设施中隐藏特权访问权限。

如果在`krbtgt`账户的`msDS-AllowedToActOnBehalfOfOtherIdentity`属性中设置某个用户账户的SID（下文将详细介绍操作过程），那么任意账户就可以获取KDC（Key Distribution Centre）服务的TGS（Ticket Granting Service），最终获得一个有效的TGT（Ticket-Granting Ticket），这也意味着攻击者成功获得了黄金票据（Golden Ticket）。拥有黄金票据后，攻击者可以完全控制整个AD域。



## 三、部署S4U2Self后门

来回顾一下攻击者如何利用公开工具来植入S2USelf后门，然后使用该后门来获取管理员权限。

### <a class="reference-link" name="%E5%B8%83%E7%BD%AE%E5%90%8E%E9%97%A8"></a>布置后门

假设攻击者已经可以利用`adm-compromised`账户临时获得域管（Domain Admins）权限（这种场景下，后门只能在后渗透阶段中使用），并且想利用Shamir介绍的后门技术实现目标环境的持久化访问。利用该账户，攻击者可以执行如下步骤：

1、寻找具备SPN并且密码永不过期的用户账户。在企业环境中这种情况非常常见，比如许多服务账户就会满足这种条件。

[![](https://p1.ssl.qhimg.com/t01b5156f2292c2a7d3.png)](https://p1.ssl.qhimg.com/t01b5156f2292c2a7d3.png)

图1. 使用PS命令获取满足条件的服务账户

2、使用许多攻击型安全工具（如Mimikatz）中的“DCSync”功能提取该账户对应的哈希。

[![](https://p0.ssl.qhimg.com/t018cb4048fc1fc49db.png)](https://p0.ssl.qhimg.com/t018cb4048fc1fc49db.png)

图2. 使用Mimikatz提取服务账户哈希

3、在`krbtgt`账户上设置`S4U2Self`后门。在本例中，攻击者使用的服务账户为`svc-backdoor`，并且对该账户具备完整控制权限。我们会在下文中介绍如何选择这类账户。

[![](https://p3.ssl.qhimg.com/t01f52d8f548ed31f78.png)](https://p3.ssl.qhimg.com/t01f52d8f548ed31f78.png)

图3. 设置S4U2Self后门

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%90%8E%E9%97%A8%E9%87%8D%E6%96%B0%E8%8E%B7%E5%8F%96%E7%AE%A1%E7%90%86%E5%91%98%E6%9D%83%E9%99%90"></a>利用后门重新获取管理员权限

这里我们要介绍攻击者如何利用先前植入的后门重新获取“Domain Admin”权限。为了重新获取管理员权限，攻击者会利用`svc-backdoor`账户执行如下3个步骤：

1、触发后门，为任意账户申请TGT，这里我们以`administrator`账户为例。

[![](https://p1.ssl.qhimg.com/t01ae70c56246f6404a.png)](https://p1.ssl.qhimg.com/t01ae70c56246f6404a.png)

图4. 利用Rubeus及`svc-backdoor`账户的Kerberos AES秘钥获取该账户的TGT

[![](https://p5.ssl.qhimg.com/t01ce3680dbad9b9af5.png)](https://p5.ssl.qhimg.com/t01ce3680dbad9b9af5.png)

图5. `S4U2Self`仿冒`administrator`账户身份，使用该TGT获取只适用于该服务账户的TGS

[![](https://p2.ssl.qhimg.com/t01f4a6e7a01779d2c2.png)](https://p2.ssl.qhimg.com/t01f4a6e7a01779d2c2.png)

图6. S4U2Proxy成功获取`administrator`账户的TGS

> 重要事项：由于我们针对的是Krbtgt服务的TGS，因此从原理上讲，获取到是适用于`administrator`账户的TGT。

2、获得TGT后，攻击者可以为所仿冒的账户（这里为`administrator`）在域控上获取CIFS及LDAP服务的TGS，然后将这些TGS注入当前会话中。

[![](https://p3.ssl.qhimg.com/t019a107ddc7efe70af.png)](https://p3.ssl.qhimg.com/t019a107ddc7efe70af.png)

图7. 利用之前获取的TGT来请求有效的TGS

3、最后，攻击者已经成功恢复高权限，可以执行各种恶意操作，如转储其他用户的凭据等。

[![](https://p4.ssl.qhimg.com/t0190dc3852f510635c.png)](https://p4.ssl.qhimg.com/t0190dc3852f510635c.png)

图8. 使用已恢复的TGT再次提取管理员凭据

## 四、对S4U2Self后门持久化应用的分析

根据Shamir在文中的介绍，攻击者必须在`msDS-AllowedToActOnBehalfOfOtherIdentity`属性中设置某个用户的SID值，才能使后门具备可用性。由于该账户是唯一能够触发后门的账户，因此攻击者必须谨慎选择目标账户。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e5af96aaac61da80.png)

图9. 在`krbtgt`账户中设置John Doe为后门账户

目标账户不一定是特权账户，可以是用户账户或者主机账户，但必须设置SPN属性才能保证S4U2Self攻击过程顺利进行。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E8%AE%A1%E7%AE%97%E6%9C%BA%E8%B4%A6%E6%88%B7"></a>使用计算机账户

计算机账户对攻击者来说非常具有吸引力，因为这些账户天然就具备SPN属性，可以作为较为隐蔽的攻击目标。

这种方法有唯一一个限制条件：计算机账户密码的自动更新问题。（默认情况下）每隔30天，计算机账户密码就会自动更新，对应的凭据也会发生变化，使后门失去作用。攻击者可以有两种方法绕过这种限制：
- 要么每隔30天重新连接至已入侵的主机，然后再次转储Kerberos秘钥
- 或者修改主机本地配置，使用`DisablePasswordChange`这个注册表项禁用密码自动更新机制（参考[此处](https://blogs.technet.microsoft.com/askds/2009/02/15/machine-account-password-process-2/)资料）
[![](https://p0.ssl.qhimg.com/t01fc1180cc336e0a30.png)](https://p0.ssl.qhimg.com/t01fc1180cc336e0a30.png)

图10. 禁用计算机账户密码更新机制

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E6%9C%8D%E5%8A%A1%E8%B4%A6%E6%88%B7"></a>使用服务账户

根据具体的目标环境，服务账户可能是隐藏`S4U2Self`后门的更好的选择。实际上，使用Kerberos身份认证的服务账户必须设置SPN属性，根据我们的经验，这些服务也会使用不过期的密码。这样一来该服务就是我们后门的绝佳目标，原因如下：
- 由于没有额外添加SPN，因此这种方式更加隐蔽，避免攻击过程意外暴露。
- 由于Kerberos密钥不会改变，因此这种方式更具备持久性
当然，即使管理员对服务账户做了防护，避免账户委派（即服务账户隶属于“Protected Users”或者被标记为敏感账户），也不会对这种AD持久化技术造成影响。



## 五、利用约束委派

需要注意的是还有一类后门与这种技术类似，此时采用的是基于协议转换的约束委派（constrained delegation），这种方法可以实现相同目标。

这种方法并没有用到`krbtgt`账户的某个属性，而是直接在目标账户上进行配置，具体用到了`userAccountControl`属性以及`AllowedToDelegateTo`属性的`TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`标志。需要注意的是，只有属于“Domain Admins”组的用户能够设置后面一个属性。

### <a class="reference-link" name="%E5%B8%83%E7%BD%AE%E5%90%8E%E9%97%A8"></a>布置后门

为了布置这种后门，我们可以稍微修改前面提到过的`S4U2Self`后门的布置过程。
- 识别出密码不过期且带有SPN的用户账户（与之前的命令相同）
- 提取该账户的哈希值（可以使用Mimikatz，与之前的命令相同）
- 配置该账户，以便通过协议转换进行委派（如下图1处红框），然后选择域控制器及LDAP协议（如下图2处红框）
[![](https://p0.ssl.qhimg.com/t01ce533bfe4b765827.png)](https://p0.ssl.qhimg.com/t01ce533bfe4b765827.png)

图11. 设置约束委派后门

### <a class="reference-link" name="%E5%86%8D%E6%AC%A1%E8%8E%B7%E5%BE%97%E7%AE%A1%E7%90%86%E5%91%98%E6%9D%83%E9%99%90"></a>再次获得管理员权限

同样我们可以使用`svc-backdoor`账户再次触发后门。

1、使用该后门账户为任意用户获取LDAP服务的TGS，这里我们使用的是`administrator`账户。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013ae773542e96f82d.png)

图12. 利用Rubeus及`svc-backdoor`账户的Kerberos AES秘钥获取该账户的TGT

[![](https://p5.ssl.qhimg.com/t013addcd1903785213.png)](https://p5.ssl.qhimg.com/t013addcd1903785213.png)

图13. `S4U2Self`仿冒`administrator`账户身份，使用该TGT获取只适用于该服务账户的TGS

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b2b0bce17590eefc.png)

图14. S4U2Proxy成功获得`administrator`账户在DC上LDAP服务的TGS

2、现在该TGS已经成功注入当前进程，同样我们可以使用经典的pass-the-hash（哈希传递）攻击获得管理员凭据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018c2b60cfd3ea17e0.png)

图15. 成功入侵AD域

如上文所示，这两种方法都非常相似，唯一的区别在于后门所使用的属性（是我们想要访问的资源的属性，还是能够访问该资源的服务账户的属性）。



## 六、如何检测S4U2Self后门

既然我们已经知道S4U2Self后门的工作过程，也能够找到相应的检测机制。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8Alsid%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88"></a>使用Alsid解决方案

Alsid提供的解决方案能够实时检测对AD对象属性的修改操作，因此可以在后门安装的早期攻击过程中检测到攻击行为，如下图所示：

[![](https://p5.ssl.qhimg.com/t01a370940af99d6bcc.png)](https://p5.ssl.qhimg.com/t01a370940af99d6bcc.png)

图16. 使用Alsid for AD检测S4U2Self

我们知道`krbtgt`账户是非常关键的资源，必须得到妥善保护。在正常配置情况下，这个账户不应该被委派。因此，一旦有人在`msDS-AllowedToActOnBehalfOfOtherIdentity`中添加了其他属性，Alsid就会向SOC团队报警，解释问题所在。

这同样适用于`msDS-AllowedToDelegateTo`属性。一旦该属性设置了使用协议转换进行约束委派，就表明配置出现了某些问题。如果线索指向的是域控制器，那么安全团队应该好好评估相关风险。

监控`krbtgt`账户并不是万全之策。如果某个管理员账户设置了SPN，那么攻击者还有可能选择该账户作为攻击目标，此时攻击者可以使用Kerberoast攻击以及适用于`krbtgt`账户的所有攻击方法。由于Alsid产品已经能够全面检测Kerberoast攻击，因此可以防御这种攻击场景。此外，如果攻击者想使用另一个特权账户来设置后门，就需要在该账户上设置SPN，该操作也会触发警报。

### <a class="reference-link" name="%E5%85%B6%E4%BB%96%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88"></a>其他解决方案

我们还可以使用其他方案来检测这类攻击。

比如，我们可以使用非特权AD账户、[RSAT](https://www.microsoft.com/en-US/download/details.aspx?id=45520)工具包，配合如下PowerShell命令来检测基于`krbtgt`账户的后门：

```
PS C:\ &gt; Import-Module ActiveDirectory
PS C:\ &gt; Get-ADUser krbtgt -Properties PrincipalsAllowedToDelegateToAccount
```

不幸的是，虽然这种方法对安全审计来说非常有用，但不适用于实时检测。我们还可以使用另一种方法，在`krbtgt`账户上设置SACL，这样该账户有任何修改时我们就能得到通知，分析具体改动，检测`msDS-AllowedToActOnBehalfOfOtherIdentity`属性的具体值。大家可以参考我们之前的一篇[文章](https://alsid.com/company/news/kerberos-resource-based-constrained-delegation-new-control-path)了解更多细节。

为了检测基于其他特权账户的S4U2Self后门，我们首先应该分析AD环境中带有敏感权限的每个内置组。除了较为知名的“Domain Admins”组之外，还有其他许多组也具备特权性质。这些组的每个成员都不应该带有SPN属性，否则攻击者就可以利用Kerberoast以及本文介绍的后门技术发起攻击。

比如，我们应该重点保护如下几个特权组：

```
Domain Admins
Enterprise Admins
Administrators
Schema Admins
Domain Controllers
Group Policy Creator Owners
Server Operators
Account Operators
Cert Publishers
Key Admins
Enterprise Key Admins
Print Operators
Backup Operators
DnsAdmins
```

在实际环境中，我们应该递归查询这些组，获取所有成员，检查这些账户是否设置了SPN。

如前文所述，S4U2Self后门需要设置SPN，并且要求目标账户永远不更新密码。因此，我们可以使用如下PowerShell命令，寻找适用于`msDS-AllowedToActOnBehalfOfOtherIdentity`属性的目标账户：

```
PS C:\ &gt; Get-ADUser -Filter * -Properties ServicePrincipalName, PasswordNeverExpires | ? `{`($_.ServicePrincipalName -ne "") -and ($_.PasswordNeverExpires -eq $true)`}`
```
