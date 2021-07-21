> 原文链接: https://www.anquanke.com//post/id/172941 


# MachineAccountQuota在活动目录中的应用


                                阅读量   
                                **159206**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者netspi，文章来源：blog.netspi.com
                                <br>原文地址：[https://blog.netspi.com/machineaccountquota-is-useful-sometimes/](https://blog.netspi.com/machineaccountquota-is-useful-sometimes/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0156853e8d05b63135.jpg)](https://p1.ssl.qhimg.com/t0156853e8d05b63135.jpg)



## 一、前言

`MachineAccountQuota`（MAQ）是一个域级别的属性，默认情况下可以允许非特权用户将主机连接到活动目录（AD）域，能连接的主机数最多不超过10台。我与MAQ的缘分可以追溯到很早以前，当时我还是一名网络管理员，我的任务是将某个远程系统加入AD中。添加10台主机后，当我想再新加入一台主机时看到了如下错误信息：

[![](https://p1.ssl.qhimg.com/t0132b9d64fa2aec64a.png)](https://p1.ssl.qhimg.com/t0132b9d64fa2aec64a.png)

我发现这个错误信息与[ms-DS-MachineAccountQuota](https://docs.microsoft.com/en-us/windows/desktop/adschema/a-ms-ds-machineaccountquota)有关，错误信息表明我当前使用的AD访问权限并不满足要求。我联系了某个管理员解释当前遇到的情况，虽然他并不知道如何为我的账户增加配额，但却提供了一个域管账户，以便我继续工作。



## 二、Powermad

2017年年末我发布了[Powermad](https://github.com/Kevin-Robertson/Powermad)工具，这款工具集合了许多PowerShell函数，参考了[加入LDAP域](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-adod/87edaa57-425e-479d-b98c-a40116032463)过程中涉及到的许多数据包。深入分析这些数据包后，我找到了一段经过加密的LDAP add数据，可以用来创建主机账户对象（machine account object）。未经加密的LDAP add数据如下所示：

[![](https://p5.ssl.qhimg.com/t01b88ec66ac12ad729.png)](https://p5.ssl.qhimg.com/t01b88ec66ac12ad729.png)

在开发Powermad时，我最主要的目的是想在测试过程中更加方便地使用MAQ。之前我看到过测试人员利用MAQ将完整的Windows系统加入域。我不希望MAQ只限于这种使用场景，而是希望能够将某个主机账户加入域中。

[![](https://p4.ssl.qhimg.com/t016e187122acd49d26.png)](https://p4.ssl.qhimg.com/t016e187122acd49d26.png)



## 三、MachineAccountQuota的作用

在开发Powermad的过程中，除了知道默认情况下有10个系统数量限制外，我还学到了关于MAQ的许多知识。最近一段时间，[Elad Shamir](https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html)、[Harmj0y](https://posts.specterops.io/a-case-study-in-wagging-the-dog-computer-takeover-2bcb7f94c783)以及[Dirk-jan](https://dirkjanm.io/worst-of-both-worlds-ntlm-relaying-and-kerberos-delegation/)公布了一些非常好的研究文章，其中也涉及到MAQ相关内容，我从中汲取了更多信息。

总而言之，我得出一个结论：在某些情况下，`MachineAccountQuota`的确非常有用。

[![](https://p2.ssl.qhimg.com/t01f69fa8fcd07fcee6.png)](https://p2.ssl.qhimg.com/t01f69fa8fcd07fcee6.png)

在本文中，我将与大家分享作为攻击者在使用MAQ的过程中我们要遵循的10条规则。我们的应用场景是将某个主机账户加入AD中，而不是添加完整的Windows操作系统。随后，我会将其中某些规则应用到MAQ + Kerberos无约束委派使用场景中。最后，我会介绍如何防御与MAQ有关的攻击方法。



## 四、具体规则

我将自己掌握的MAQ知识总结成10条规则，希望大家可以使用这些规则来判断能否在实际环境中使用MAQ。

**1、MAQ可以让非特权用户将主机账户对象加入域中**

默认情况下，非特权用户可以创建10个主机账户。

[![](https://p1.ssl.qhimg.com/t0165db7465fe3bd099.png)](https://p1.ssl.qhimg.com/t0165db7465fe3bd099.png)

在调用MAQ时，我们并不需要做太多特别的操作，只需要使用尚未被直接授予域加入权限的账户即可。

**2、创建者账户的SID存储在主机账户的`ms-DS-CreatorSID`属性中**

只有当创建者不是管理员，或者尚未被委派添加主机账户的权限时，AD才会设置该属性。

[![](https://p2.ssl.qhimg.com/t01e96da8dc7cd357ff.png)](https://p2.ssl.qhimg.com/t01e96da8dc7cd357ff.png)

AD同样会使用`ms-DS-CreatorSID`来计算MAQ的当前数值。从测试角度来看，要记住该属性是指向创建者账户的一个指针，即使使用嵌套的MAQ也是如此。因此，使用MAQ创建主机账户并不能完全保护创建者账户。

[![](https://p0.ssl.qhimg.com/t0116ecdb32077b37bd.png)](https://p0.ssl.qhimg.com/t0116ecdb32077b37bd.png)

如果目标防护机制对`ms-DS-CreatorSID`属性比较敏感，那么很有可能已经禁用了MAQ。

**3、通过MAQ创建的主机账户位于Domain Computers（域主机）组中**

如果Domain Computers组被授予了额外权限，那么这些权限也会通过MAQ扩展到未授权的用户。比如，我们有可能在本地管理员组中找到Domain Computers:

[![](https://p0.ssl.qhimg.com/t01fa2b05235e4e10b8.png)](https://p0.ssl.qhimg.com/t01fa2b05235e4e10b8.png)

或者如果运气更好，我们有可能在Domain Administrators（域管理员）组成员中找到这个组。

[![](https://p5.ssl.qhimg.com/t0171cfd4ab35598566.png)](https://p5.ssl.qhimg.com/t0171cfd4ab35598566.png)

稍微扩展一下，如果我们发现目标环境会根据主机账户名特征，自动化将主机归入特定OU或者组中，此时我们可以通过MAQ来利用这种自动化策略。

**4、创建者账户会被授予某些主机账户对象属性的写入权限**

通常情况下包含如下属性：

```
AccountDisabled
description
displayName
DnsHostName
ServicePrincipalName
userParameters
userAccountControl
msDS-AdditionalDnsHostName
msDS-AllowedToActOnBehalfOfOtherIdentity
samAccountName
```

我们可以根据实际情况修改这些属性。

[![](https://p1.ssl.qhimg.com/t01083bc18b96c3e40a.png)](https://p1.ssl.qhimg.com/t01083bc18b96c3e40a.png)

然而，某些属性的取值仍被限定在一定范围内。

**5、主机账户具备自身某些属性的写入权限**

其中就包含[msDS-SupportedEncryptionTypes](https://www.harmj0y.net/blog/redteaming/kerberoasting-revisited/)属性，该属性可以影响Kerberos协商加密方法。现代Windows系统会在加入域的过程中将该属性值设置为28.

[![](https://p1.ssl.qhimg.com/t0122c540b9fd9a23ac.png)](https://p1.ssl.qhimg.com/t0122c540b9fd9a23ac.png)

**6、添加主机账户时对属性验证非常严格**

属性值需要匹配系统要求，如果不匹配，添加过程就会失败，如下图所示，其中`samAccountName`属性值不正确。

[![](https://p5.ssl.qhimg.com/t0123e37cd52371266c.png)](https://p5.ssl.qhimg.com/t0123e37cd52371266c.png)

奇怪的是，添加主机账户后系统会放宽某些验证规则。

**7、我们可以将`samAccountName`修改为与域内已有`samAccountName`属性不同的值**

修改这个属性可以帮我们在合法流量中隐藏攻击行为，比如我们可以删除其中的`$`字符，或者将其改成满足现有账户命名规范的值。有趣的是，`samAccountName`末尾甚至可以是空格符，这样就能仿冒现有的域账户。

[![](https://p1.ssl.qhimg.com/t011abaa1ddd3b15ee7.png)](https://p1.ssl.qhimg.com/t011abaa1ddd3b15ee7.png)

仿冒的`Administrator`账户在数据包中的特征如下：

[![](https://p0.ssl.qhimg.com/t01000890832a2cef0a.png)](https://p0.ssl.qhimg.com/t01000890832a2cef0a.png)

请注意，修改`samAccountName`并不会修改实际的主机账户对象名。因此，我们可以使用满足命名规范的计算机账户，同时使用一个完全不同的`samAccountName`。

**8、添加主机账户会创建4个SPN**

具体列表如下：

```
HOST/MachineAccountName
HOST/MachineAccountName.domain.name
RestrictedKrbHost/MachineAccountName
RestrictedKrbhost/MachineAccountName.domain.name
```

例如，`test.inveigh.net`主机账户的默认SPN列表如下图所示：

[![](https://p5.ssl.qhimg.com/t01991a091e0b8fdd4e.png)](https://p5.ssl.qhimg.com/t01991a091e0b8fdd4e.png)

添加主机账户后，我们可以使用符合规则的SPN来增加或者替换列表元素。

[![](https://p2.ssl.qhimg.com/t01ea3a60fc4c9f8474.png)](https://p2.ssl.qhimg.com/t01ea3a60fc4c9f8474.png)

如果我们修改`samAccountName`、`DnsHostname`或者`msDS-AdditionalDnsHostName`属性，SPN列表会自动更新为新的值。默认的SPN的确覆盖了许多使用场景，因此我们不一定要去修改这个列表。如果需要了解更多SPN知识，可以参考[Sean Metcalf](https://twitter.com/PyroTek3)在[AdSecurity](https://adsecurity.org/?page_id=183)上给出的清单，其中就包含`Host`和`RestrictedKrbHost`方面的具体设置。

**9、主机账户不具备本地登录权限**

然而，我们可以在命令行使用能够直接接受相应凭据的工具，或者使用`runas /netonly`命令来利用主机账户，可执行的操作包括[信息枚举](https://github.com/NetSPI/goddi)、[添加DNS记录](https://blog.netspi.com/adidns-revisited/)或者适用于用户账户的大多数命令。

[![](https://p4.ssl.qhimg.com/t01c6328b60b499a67a.png)](https://p4.ssl.qhimg.com/t01c6328b60b499a67a.png)

**10、无法使用非特权创建者账户删除通过MAQ添加的主机账户**

在使用MAQ后，为了完全清理AD记录，我们需要提升域内权限，或者将该任务交给客户端来完成。然而我们可以使用非特权创建者账户禁用主机账户。

[![](https://p2.ssl.qhimg.com/t015d5047aa1e69840b.png)](https://p2.ssl.qhimg.com/t015d5047aa1e69840b.png)



## 五、MachineAccountQuota的实际应用

我们可以将上述规则应用于已窃取的、具备[SeEnableDelegationPrivilege](https://www.harmj0y.net/blog/activedirectory/the-most-dangerous-user-right-you-probably-have-never-heard-of/)权限的AD账户。在规则4中我们提到过，即使账户具备某个属性的写入权限，系统也会对写入操作进行验证。

[![](https://p3.ssl.qhimg.com/t013b15aa8b3a9dd083.png)](https://p3.ssl.qhimg.com/t013b15aa8b3a9dd083.png)

然而，如果我们拿到了具备正确权限的账户（比如具备[SeEnableDelegationPrivilege](https://www.youtube.com/watch?v=ze1UcSLOypw)权限），那么事情就会变得有趣起来。

[![](https://p5.ssl.qhimg.com/t015ad9bfa0827b0d9d.png)](https://p5.ssl.qhimg.com/t015ad9bfa0827b0d9d.png)

在这种情况下，我们可以使用`INVEIGH\kevin`账户配合MAQ来创建并配置主机账户对象，以便执行Kerberos无约束委派（unconstrained delegation）攻击，这种方法可以让我们不用专门去寻找能够利用`SeEnableDelegationPrivilege`权限的AD对象，可以使用MAQ创建自己的对象。

请注意，这只是一种应用场景，实际情况下，如果我们能使用自己的Windows系统加入域，那操作起来会更加方便。如果我们选择使用这种方法，那么可以在主机账户上启动无约束委派，然后就可以执行正常的攻击操作。这里有个好消息，只使用主机账户的情况下，整个过程依然非常可控。



## 六、设置Kerberos无约束委派

想象一个攻击场景，比如我们已获得域内某个Windows系统上的非特权访问权限，也窃取了具备`SeEnableDelegationPrivilege`权限的账户。那么我们可以执行如下攻击操作：

1、使用`SeEnableDelegationPrivilege`账户，通过MAQ添加主机账户。

[![](https://p4.ssl.qhimg.com/t018e30b0aa60c4bd26.png)](https://p4.ssl.qhimg.com/t018e30b0aa60c4bd26.png)

2、将`userAccountControl`属性值设置为`528384`，启用无约束委派。

[![](https://p3.ssl.qhimg.com/t01a87ccb83f8a60570.png)](https://p3.ssl.qhimg.com/t01a87ccb83f8a60570.png)

3、（可选操作）使用主机账户凭据将`msDS-SupportedEncryptionTypes`属性值设置为所需的Kerberos加密类型。

[![](https://p0.ssl.qhimg.com/t018d59bcd24a3972b2.png)](https://p0.ssl.qhimg.com/t018d59bcd24a3972b2.png)

4、（可选操作）添加域SPN对应的DNS记录，将其指向我们已入侵的Windows系统。通常我们可以使用[动态更新或者LDAP](https://blog.netspi.com/exploiting-adidns/)完成该任务。这是一个可选项，因为在默认的SPN下，其他解析方法（如LLMNR/NBNS）也会触发Kerberos。

[![](https://p2.ssl.qhimg.com/t010ed3ff2500c7e600.png)](https://p2.ssl.qhimg.com/t010ed3ff2500c7e600.png)



## 七、Kerberos无约束委派攻击

环境设置完毕后，接下来我们需要澄清如何构造出正确的通信数据包。首先，我们可以使用tifkin的[打印机漏洞](https://www.slideshare.net/harmj0y/derbycon-the-unintended-risks-of-trusting-active-directory/39)让域控主机账户通过SMB协议连接到我们的系统。此外，我们还可以使用Dev分支的[Inveigh](https://github.com/Kevin-Robertson/Inveigh/tree/dev)，该工具可以通过数据包嗅探提取SMB Kerberos TGT流量，将结果输出为kirbi文件，以便与[Mimikatz](https://github.com/gentilkiwi/mimikatz)及[Rubeus](https://github.com/GhostPack/Rubeus)工具配合使用。

使用Inveigh时，我们需要提供无约束委派账户的AES256哈希值或者以Kerberos salt作为用户名的PSCredential对象。如下图所示，我们可以使用Powermad的`Get-KerberosAESKey`函数生成正确的AES256哈希值。

[![](https://p5.ssl.qhimg.com/t013e16947f5956adcc.png)](https://p5.ssl.qhimg.com/t013e16947f5956adcc.png)

请注意，目前Inveigh值仅支持AES256 Kerberos解密。

由于我们想使用无约束委派主机账户的SPN，因此我们需要让目标连接到正确的主机名。在这个测试案例中，我使用的是[Dirk-jan](https://twitter.com/_dirkjan)提供的`printerbug`脚本，该脚本来自于他最近公开的[Krbrelayx工具集](https://github.com/dirkjanm/krbrelayx/)。

[![](https://p2.ssl.qhimg.com/t015ea1d2f090a62a01.png)](https://p2.ssl.qhimg.com/t015ea1d2f090a62a01.png)

这里我们可以稍微放缓脚步，回顾一下涉及到的各种SPN。首先，我们入侵了以`SYSTEM`权限运行SMB服务器的某个系统，这意味着SMB服务器会使用系统的主机账户凭据来解密Kerberos票据。如果我们构造不匹配的SPN，在不同SPN下加密数据并发起Kerberos认证，那么SMB认证过程就会失败。然而，在客户端发送完AP-REQ之前，SMB服务器并不会拒绝认证请求。

[![](https://p1.ssl.qhimg.com/t01d1f70a4ac0ae95c3.png)](https://p1.ssl.qhimg.com/t01d1f70a4ac0ae95c3.png)

更加重要的是，在接收到TGT后，SMB服务器会拒绝连接。因此，如果我们能通过数据包嗅探抓取Kerberos流量，我们就可以使用已有的主机账户凭据解密出所需数据。

[![](https://p0.ssl.qhimg.com/t01c63c8bece5db1dfb.png)](https://p0.ssl.qhimg.com/t01c63c8bece5db1dfb.png)

请注意，这种SPN不匹配技巧可能会触发客户端执行多次Kerberos认证。对于每个用户，我设置Inveigh默认输出2个kirbi文件。Inveigh会将剩余信息存储在内存中，我们可以通过`Get-Inveigh`访问这些数据。

现在我们已经掌握域控制器的kirbi TGT，可以将其输入Mimikatz中，尝试执行dcsync攻击。

[![](https://p3.ssl.qhimg.com/t016b64d4e6a6fe860b.png)](https://p3.ssl.qhimg.com/t016b64d4e6a6fe860b.png)

再举一个简单例子，我们可以使用Inveigh捕捉基于SMB协议的域管理员（Domain Administrator）TGT。

[![](https://p5.ssl.qhimg.com/t0193e8ec10e85a434b.png)](https://p5.ssl.qhimg.com/t0193e8ec10e85a434b.png)

接下来使用Rubeus处理kirbi文件。

[![](https://p5.ssl.qhimg.com/t01930906878855d7ac.png)](https://p5.ssl.qhimg.com/t01930906878855d7ac.png)

最后一个例子，我们可以使用Inveigh捕捉基于HTTP协议的TGT。

[![](https://p5.ssl.qhimg.com/t01d6eba12f5d111d40.png)](https://p5.ssl.qhimg.com/t01d6eba12f5d111d40.png)

在理想情况下，使用HTTP协议时我们可能不需要本地管理员访问我们已入侵的系统。

新的krbrelayx工具集也能使用前面提到的Kerberos无约束委派技术。

关于`SeEnableDelegationPrivilege` + MAQ技术最后再提一点，由于我们通常不具备`msDS-AllowedToDelegateTo`写权限，因此想完整设置标准的约束委派基本上是不可能完成的任务。



## 八、防御MachineAccountQuota攻击技术

我相信目前系统中还有许多默认的设置我们没注意到，MAQ只是其中一个代表。正常情况下，我认为许多公司很少需要使用默认的MAQ设置，或者根本不需要启用该功能。要禁用MAQ，我们只需要将`ms-DS-MachineAccountQuota`属性值[设置为0](https://social.technet.microsoft.com/wiki/contents/articles/5446.active-directory-how-to-prevent-authenticated-users-from-joining-workstations-to-a-domain.aspx)即可。如果我们的确需要允许非特权用户在网络中添加系统，那么更好的方法是只将相应权限授予特定的组。此外，本文提到的大部分内容同样适用于已被委派域加入权限的账户。

防御方可以关注两个要点：
- 被修改的`ms-DS-CreatorSID`属性
- 未修改密码的主机账户


## 九、总结

`MachineAccountQuota`并非万能技术，也有一定的使用场景。对于测试人员来说，可以将其当成备用技术，最近[Elad Shamir](https://twitter.com/elad_shamir)公开的技术也表明这方面技巧有其价值所在。对于防御方而言，我建议直接禁用`MachineAccountQuota`即可。
