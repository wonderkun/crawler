
# Kerberos概述及常见攻击场景


                                阅读量   
                                **780924**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者specterops，文章来源：posts.specterops.io
                                <br>原文地址：[https://posts.specterops.io/kerberosity-killed-the-domain-an-offensive-kerberos-overview-eb04b1402c61](https://posts.specterops.io/kerberosity-killed-the-domain-an-offensive-kerberos-overview-eb04b1402c61)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/200680/t01d3707e82d7c340e8.jpg)](./img/200680/t01d3707e82d7c340e8.jpg)



## 0x00 前言

Kerberos是Windows域首选的一种认证协议，优于NTLM认证机制。虽然Kerberos认证机制较为复杂，但红队、渗透测试人员以及实际攻击者经常会用到该协议。理解Kerberos的工作原理非常重要，这样我们才能理解针对Kerberos的潜在攻击方式，澄清攻击者如何利用该协议攻击域环境。本文大概介绍了Kerberos的工作原理，也介绍了与之相关的一些常见攻击场景。



## 0x01 Kerberos概述

Kerberos认证协议围绕着“票据”（ticket）对象展开，这里涉及两类票据：

1、TGT：票据授予票据（Ticket-Granting-Ticket）；

2、TGS：票据授予服务（Ticket-Granting Service，也称为“服务票据”）。

当用户登录域主机Windows系统时，系统根据用户输入的密码生成哈希，并将哈希值作为密钥来加密时间戳，发送至KDC（Key-Distribution Center，密钥分发中心，位于域控制器上）。经过加密的时间戳以AS-REQ（Authentication Server Request）形式发送至KDC，KDC随后使用用户在AD中的密码哈希来解密该请求，验证用户凭据，确认时间戳是否在允许范围内，然后返回AS-REP（Authentication Server Reply）响应。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a4726bef06cabf9f.png)

图1. TGT请求/响应流程

AS-REP中包含使用KRBTGT密钥（即密码哈希）加密的TGT，也包含使用用户密钥加密的其他数据。KRBTGT账户为首次设置DC时创建的账户，用于Kerberos认证协议中。如果KRBTGT账户密码被攻击者获取，将造成严重的后果，稍后我们会介绍这方面内容。

现在用户已通过域的身份认证，但仍然需要访问已登录主机上的某些服务。此时就需要发送TGS-REQ请求，获取针对某个服务主体（service principal）的服务票据（TGS）。服务主体由SPN（service principal name，服务主体名称）来表示。Windows中有许多SPN，大家可以访问[此处](https://adsecurity.org/?page_id=183)了解大部分SPN。为了访问实际主机，这里客户端需要请求`HOST` SPN。`HOST`主体中包含Windows的所有[内置服务](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/ff649429(v=pandp.10)?redirectedfrom=MSDN)。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f01f1c8c09aeec00.png)

图2. 服务票据请求流程

TGS中包含PAC（Privileged Attribute Certificate，特权属性证书），而PAC中包含于用户及其成员身份的相关信息，如图3所示。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b81a417dc5e81cd8.png)

图3. TGS中的PAC

在上图中，`GroupIDs`为服务用来判断用户是否具备访问权限的一个元素。为了避免被篡改，TGS使用目标服务的密码哈希来加密。对于`HOST/ComputerName`，这里使用的是主机账户的密码哈希。之所以使用账户密码哈希来加密/解密票据，是因为这些哈希为账户及KDC/域控之间共享的唯一秘钥。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0158e2bc369f6844c3.png)

图4. TGS-REP交换过程

一旦通过TGS-REP收到TGS，目标服务就会使用自己的密码哈希（这里为主机账户的密码哈希）来解密票据，查看TGS中的PAC来判断其中是否存在匹配的组SID，以便确定访问权限。服务票据中比较特别的一点在于，KDC负责身份认证（TGT），而服务负责授权（TGS中的PAC）。确认权限后，用户就可以访问`HOST`服务主体，登录计算机。

我们可以使用Wireshark捕捉用户登录过程，查看整个登录流程。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b46c7bc2347a7be2.png)

图5. 登录域主机Windows系统时涉及到的Kerberos认证过程

在图5中，第一个AS-REQ对应的响应信息为“KRB Error: KRB5KDC_ERR_PREAUTH_REQUIRED”。在Kerberos 5之前，Kerberos允许不使用密码进行身份认证，而在Kerberos 5中，密码信息不可或缺，这种过程称之为“预认证”。可能出于向后兼容考虑，Kerberos在执行预认证之前，首先会尝试不使用密码进行身份认证，因此在登录期间，发送初始AS-REQ后我们总是能看到一个错误信息。在这种情况下，攻击者有可能利用AS-REP Roasting攻击。



## 0x02 AS-REP Roasting

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01587cfa707f7ab8f7.png)

图6. 不需要进行Kerberos预认证的用户属性

上图为AD中用户的账户选项设置，其中有个选项可以设定不需要进行Kerberos预认证。

由于AS-REQ使用用户的密码哈希作为秘钥来加密时间戳，如果KDC使用用户的密码哈希成功读取时间戳，并且时间戳落在KDC允许的时间窗口内（几分钟内），KDC就会通过AS-REP发送TGT。当不需要预认证时，攻击者可以发送伪造的AS-REQ，此时由于认证过程不需要密码，KDC会立即授予TGT。由于AS-REP中的部分数据（除TGT之外）包含使用用户秘钥（即密码哈希）加密的数据（会话秘钥、TGT到期时间以及nounce），因此攻击者可以从中提取密码哈希，离线破解。大家可以访问[此处](https://www.harmj0y.net/blog/activedirectory/roasting-as-reps/)了解详细信息。

我们可以使用Rubeus中的`asreproast`函数完成攻击过程，参考[此处视频](https://vimeo.com/396724788)。



## 0x03 Kerberoasting

当发送TGS时，KDC会使用时间戳+服务账户的密码哈希来加密TGS。由于目标服务通常为计算机控制的某个服务（比如`HOST`或者`CIFS`），因此这里会使用主机账户密码哈希。在某些情况下，用户账户也会被创建为“服务账户”，注册为SPN。由于KDC不负责服务的授权工作（该工作由服务自己负责），因此任何用户都可以请求任何服务的TGS。这意味着如果某个用户“服务账户”被注册为SPN，那么任何用户都可以请求该用户对应的TGS，而该TGS使用用户账户密码哈希加密，攻击者可以从票据中提取哈希，离线破解。

我们可以使用Rubeus中的`kerberoast`函数完成攻击过程，参考[此处视频](https://vimeo.com/396724808)。



## 0x04 黄金票据

前面提到过，当发送TGT时，该票据会使用KRBTGT的账户密码哈希来加密。KRBTGT的密码默认情况下不会被手动设置，因此与主机账户密码一样复杂。当攻击者成功获取KRBTGT密码，伪造TGT时，这种攻击技术称为黄金票据攻击。Mimikatz可以使用KRBTGT密码的RC4哈希来伪造任何用户的票据，并且该过程不需要知道用户密码。攻击过程参考[此处视频](https://vimeo.com/396724835)。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01748a3603e2cf6db6.png)

图7. 通过Mimikatz命令发起黄金票据攻击



## 0x05 白银票据

黄金票据对应的是TGT伪造，而白银票据则是TGS伪造。攻击者使用黄金票据时会有安全上的考虑：攻击过程涉及KDC，KDC会发布一个TGT，因此防御方可能会收到警报，捕捉到黄金票据攻击。白银票据更为隐蔽，攻击过程不涉及到KDC。由于这里伪造的是服务票据，因为攻击者需要知道目标服务的密码哈希，而大多数情况下，该哈希对应的是主机账户的密码哈希。对于设置了SPN的服务账户，攻击者也可以针对该SPN生成白银票据。

举个例子，如果用户名`MSSQLServiceAcct`创建了一个服务账户，注册了`MSSQLSVC`主体，那么对应的SPN则为`MSSQLSVC/MSSQLServiceAcct`。如果攻击者获取了账户的密码哈希（通过Kerberoasting或者其他方法），就可以利用该哈希来伪造针对该SPN的TGS，访问对应的服务（这里为`MSSQLSVC`）。

对于某些服务（如`CIFS`），如果使用了用户账户来创建SPN（如`CIFS/Alice`），此时攻击者无法使用该用户的密码来构造`CIFS`对应的白银票据，这是因为用户并不控制该服务的访问权限，这是主机账户负责的工作。

在典型的攻击场景中（参考[此处视频](https://vimeo.com/396724942)），攻击者已知域控主机账户的哈希，然后可以利用该哈希生成针对`CIFS`的白银票据，访问目标文件系统。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e6167a0008a66c0b.png)

图8. 通过Mimikatz命令发起白银票据攻击

白银票据存在的安全风险在于，如果设置了PAC验证功能，票据就会发送到KDC进行验证，此时攻击将以失败告终。



## 0x06 委派攻击

Kerberos中有个委派（delegation）概念，其中账户可以复用票据，或者将票据“转发”至另一个主机或者应用程序。

比如在下图中，用户登录到某个Web应用，该应用使用了另一台服务器上的SQL DB。这里Web应用的服务账户可以不具备SQL DB所在服务器的完整访问权限，管理员只需要配置委派策略，使Web应用服务器上的服务账户只能访问SQL服务器上的SQL服务。此外，服务账户可以用于委派，意味着服务账户将代表用户、以用户的票据来访问SQL服务器。这种方式既能使服务账户不具备SQL服务器的完整访问权限，也能确保只有已授权的用户能够通过Web应用访问SQL DB。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01749c0ad4a4cf6adb.png)

图9. 常见的域委派场景

Windows中主要有3类委派，每类委派都有对应的攻击场景：

1、非约束（unconstrained）委派；

2、约束（constrained）委派；

3、基于资源的约束（Resource-Based Constrained，RBCD）委派

### <a class="reference-link" name="%E9%9D%9E%E7%BA%A6%E6%9D%9F%E5%A7%94%E6%B4%BE"></a>非约束委派

微软在Windows 2000中实现了非约束委派，这是执行委派的一种非常古老的方法。我们可以在AD的某个主机对象的“委派”选项卡中进行设置。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e0d48c301fe8a5b9.png)

图10. AD中主机对象属性表明该对象支持非约束委派

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014ec3e468fb7f171d.png)

图11. 非约束委派示例

将计算机配置为非约束委派时，发送至主机且包含SPN的任何TGS都将带有一个TGT，且TGT将被缓存在内存中，以便后续的身份模拟。这里的安全问题在于，如果攻击者正在监控内存中的Kerberos票据活动，当TGS发送到主机时，攻击者就能提取TGT并复用该票据。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01277bd8ee8074c9b4.png)

图12. 主机使用用户的TGT，通过非约束委派请求TGS

如果攻击者能通过打印机漏洞，将域中任何主机的认证强制转接到非约束主机，那么就能进一步利用这种攻击技术。打印机漏洞是Windows Print System Remote Protocol中的一个“功能”，允许主机查询另一台主机，请求更新打印作业，目标主机随后会通过TGS（在非约束委派场景中包含TGT）响应发起请求的主机。

这意味着，如果攻击者控制了具有非约束委派的主机，就可以使用打印机漏洞，强制域控向攻击者控制的主机进行身份认证，然后就能提取域控的计算机账户TGT。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013fb255d77e48d540.png)

图13. 打印机漏洞攻击示意图

攻击者可以使用Rubeus及SpoolSample发起此类攻击，参考[此处视频](https://vimeo.com/396724959)。

需要注意的是，域控制器默认情况下会启用非约束委派选项。

### <a class="reference-link" name="%E7%BA%A6%E6%9D%9F%E5%A7%94%E6%B4%BE"></a>约束委派

微软在Windows 2003中引入了约束委派，以改进非约束委派的不足。约束委派最大的变化在于，系统将限制指定服务器可以代表用户执行的服务。约束委派相关设置位于活动目录用户和计算机对象的“委派”选项卡中。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f7faaaa85eb5ee5b.png)

图14. AD中主机对象属性，表明其可以被委派访问PRIMARY.LAB主机上的HTTP服务

我们可以使用PowerView中的函数，查看账户/计算机中的`msDS-AllowedToDelegateTo`属性，在整个域中检查委派信息：

```
Get-DomainUser USERNAME -Properties msds-allowedtodelegateto,useraccountcontrol
```

在发起攻击之前，我们首先需要了解约束委派的工作机制。约束委派使用了两个Kerberos扩展：S4U2Self以及S4U2Proxy。[文章](http://www.harmj0y.net/blog/activedirectory/s4u2pwnage/)中详细介绍了技术细节，简而言之，S4U2Self允许某个账户代表其他任意用户（无需知道这些用户的密码）请求适用于自己的服务票据。如果设置了`TRUSTED_TO_AUTH_FOR_DELEGATION`位，那么TGS将会被标记为可转发状态。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019eacc67616521f77.png)

图15. S4U2Self工作流程示意图

接下来轮到S4U2Proxy上场，委派账户使用可转发TGS请求针对特定SPN的TGS。该过程通过[MS-SFU](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/3bff5864-8135-400e-bdd9-33b552051d94) Kerberos扩展来完成，该扩展允许通过TGS请求TGS。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a04922a795960ab8.png)

图16. S4U2Proxy工作流程示意图

经过上述操作后，现在服务1（`HTTP/WebServiceAcct`）拥有服务2（`MSSQLSvc/SQLSA`）的票据，服务1将票据提供给服务2，服务2随后会验证TGS PAC中的SID，确认客户端是否有权访问该服务。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f6b6811eeab48fe8.png)

图17. 服务1通过约束委派向服务2发起身份认证

攻击者可以滥用S4U2Self及S4U2Proxy扩展。如果某个账户`AllowedToDelegateTo`属性中设置了某个SPN，并且`userAccountControl`属性中包含`TRUSTED_TO_AUTH_FOR_DELEGATION`值，那么该账户就能模拟任何用户请求该SPN中的任何服务。虽然S4U2Self扩展允许服务以任何用户身份请求适用于自己的TGS，但（第2个）TGS的SPN中的`sname`（服务名）字段并没有受到保护，因此攻击者可以将其修改成所需的任何服务。

完整的攻击路径如下：

1、攻击者通过Kerberoast方式攻击某个账户（`WebSA`），该账户的`AllowedToDelegateTo`属性设置了`MSSQLSvc/LABWIN10.LAB.local` SPN，这意味着`WebSA`能够委派其他账户访问`LABWIN10.LAB.local`上的`MSSQLSvc`。

2、攻击者使用`Rubeus`，自动化利用S4U2Self扩展，代表用户`Admin`请求当前用户（即`WebSA`）的TGS。返回的TGS被标记为“可转发”状态。

3、随后Rubeus可以自动化使用S4U2Proxy扩展来利用MS-SFU扩展，请求委派SPN的TGS，但将其中的服务字段修改为用户指定的值。比如原始值为`MSSSQLSvc/LABWIN10.LAB.local`，攻击者可以请求`HOST/LABWIN10.LAB.local`的TGS。由于服务部分不会被校验，因此返回的TGS将使用`Admin`用户身份，SPN为`HOST/LABWIN10.LAB.local`.

4、该票据被缓存到内存中，用户现在可以使用`Admin`用户身份访问`HOST/LABWIN10`。

整个流程图如下所示：

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0128fd836cfcac4a17.png)

图18. 约束委派攻击典型场景

攻击过程可参考[此处视频](https://vimeo.com/396724982)。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f26be1dd2976464a.png)

图19. 滥用约束委派的Rubeus命令

这里要注意一点：S4U2Self需要`TRUSTED_TO_AUTH_FOR_DELEGATION`，但在账户委派添加SPN时并不会自动添加这个值。如果攻击者在域控上具备`SeEnableDelegationPrivilege`权限，可以修改/添加这个值。

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E8%B5%84%E6%BA%90%E7%9A%84%E7%BA%A6%E6%9D%9F%E5%A7%94%E6%B4%BE"></a>基于资源的约束委派

基于资源的约束委派（RBCD）是对约束委派的一种改进版，从Windows Server 2012起引入。这里最大的不同点在于：我们不需要在某个账户的“委派”选项卡中指定SPN，现在委派设置可以交由“资源”本身来控制。以前面的约束委派案例为例，这意味着委派设置在后端SQL服务上完成，而不在Web服务账户上完成。

传统的约束委派需要在`msDS-AllowedToDelegateto`属性中设置SPN，而RBCD会使用计算机对象的`msDS-AllowedToActOnBehalfOfOtherIdentity`属性。[Elad Shamir](https://twitter.com/elad_shamir)之前写过一篇[文章](https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html)，详细介绍了如何滥用该功能。简而言之，如果不存在`TRUSTED_TO_AUTH_FOR_DELEGATION` `userAccountControl`标记，S4U2Self依然能工作，但返回的服务票据将被标记为“不可转发”状态。在传统的约束委派上下文中，这意味着该票据无法在S4U2Self扩展中使用。然而在RBCD场景下，即使该票据为“不可转发”状态，依然能被使用。

这里的攻击场景在于，如果攻击者已控制设置了SPN的账户，并且有个计算机账户设置了`AllowedToActOnBehalfOfOtherIdentity`属性，那么该计算机就会被攻击者控制。此外，如果攻击者具备该计算机账户的`GenericWrite`权限，由于能够修改`AllowedToAct`，将其设置为攻击者可控的SPN，因此就能控制目标计算机。

如果攻击者未控制带有SPN的账户，可以通过创建计算机对象来创建该账户。默认情况下，AD中的标准用户最多可以创建10个计算机对象，我们可以通过Kevin Robertson开发的[PowerMad](https://github.com/Kevin-Robertson/Powermad)项目来完成该任务。

整个攻击路径如下所示：

1、攻击者发现自己具备某个计算机的`GenericWrite`权限；

2.1、如果攻击者未控制带有SPN的账户，可以使用PowerMad来创建一个计算机账户，现在攻击者拿到了带有SPN的一个账户；

2.2、或者攻击者发现某个计算机对象的`msDS-AllowedToActOnBehalfOfOtherIdentity`属性设置了已被控制的账户SPN；

3、攻击者使用Rubeus的`S4U`函数，通过S4U2Self以任意用户身份请求设置SPN账户的票据（例如，为`Administrator`申请`newmachine$`的TGS）；

4、Rubeus的`S4U`函数随后通过S4U2Proxy，以`Administrator`身份（使用来自S4U2Self的TGS）请求目标计算机的TGS。该票据没有被标记为可转发状态，在传统的约束委派场景中，该操作将以失败告终，但在RBCD场景中，这种操作能顺利完成；

5、现在攻击者可以访问目标计算机。

典型攻击过程可参考[此处视频](https://vimeo.com/396724747)，其中攻击者已经控制了`Bob`，该用户账户设置了SPN。

[![](./img/200680/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0145e86191f6ec4d1d.png)

图20. 滥用RBCD的Rubeus命令

关于上述命令的详细说明，大家可以参考[@harmj0y](https://github.com/harmj0y)的[gist](https://gist.github.com/HarmJ0y/224dbfef83febdaf885a8451e40d52ff#file-rbcd_demo-ps1-L16)，这里我稍微修改了一些命令，以便使用用户SPN。



## 0x07 参考资料
- [https://labs.f-secure.com/archive/trust-years-to-earn-seconds-to-break/](https://labs.f-secure.com/archive/trust-years-to-earn-seconds-to-break/)
- [https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html#a-misunderstood-feature-1](https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html#a-misunderstood-feature-1)
- [http://www.harmj0y.net/blog/activedirectory/s4u2pwnage/](http://www.harmj0y.net/blog/activedirectory/s4u2pwnage/)
- [http://www.harmj0y.net/blog/activedirectory/the-most-dangerous-user-right-you-probably-have-never-heard-of/](http://www.harmj0y.net/blog/activedirectory/the-most-dangerous-user-right-you-probably-have-never-heard-of/)
- [https://www.harmj0y.net/blog/redteaming/another-word-on-delegation/](https://www.harmj0y.net/blog/redteaming/another-word-on-delegation/)
- [https://blogs.uw.edu/kool/2016/10/26/kerberos-delegation-in-active-directory/](https://blogs.uw.edu/kool/2016/10/26/kerberos-delegation-in-active-directory/)
- [https://github.com/GhostPack/Rubeus](https://github.com/GhostPack/Rubeus)
- [https://github.com/gentilkiwi/mimikatz](https://github.com/gentilkiwi/mimikatz)
- [https://adsecurity.org/?page_id=183](https://adsecurity.org/?page_id=183)