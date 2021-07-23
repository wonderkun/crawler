> 原文链接: https://www.anquanke.com//post/id/162606 


# Rubeus - 现在拥有更多的Kekeo功能


                                阅读量   
                                **170614**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者harmj0y，文章来源：harmj0y.net
                                <br>原文地址：[http://www.harmj0y.net/blog/redteaming/rubeus-now-with-more-kekeo/](http://www.harmj0y.net/blog/redteaming/rubeus-now-with-more-kekeo/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t018c6639581f758f52.jpg)](https://p3.ssl.qhimg.com/t018c6639581f758f52.jpg)

译者摘要： 本文是[从 Kekeo 到 Rubeus](https://www.anquanke.com/post/id/161781) 的后续，作者继续更新了 Rubeus 项目，实现了更多的 Kekeo 功能。主要介绍了虚假代理 TGT 和 基于 Kerberos 的口令更改等新功能及其原理。

[Rubeus](https://github.com/GhostPack/Rubeus), 是我将 [Kekeo](https://github.com/gentilkiwi/kekeo/) 工具集的部分功能用 C# 重新实现的一个项目。目前已经发布了更新的 1.1.0 版本，并在在 1.2.0 版本中实现了新的功能。此篇文章将会介绍主要的新功能和其他的一些修改，并将深入探讨最酷的新功能 – 虚假代理TGT和基于Kerberos的口令更改。

像以前一样，我想强调 [Kekeo](https://github.com/gentilkiwi/kekeo/) ，我是永远也想不出这些攻击技术的。我发现除非我亲自去实现，否则我无法真正理解某个原理，因此我将继续重新实现 Kekeo 的功能。我将尽量去解释清楚 tgt::deleg/tgtdeleg 和 misc::changepw/changepw 函数（Kekeo 和 Rubeus 都有使用）的底层原理，这样大家都能对 Benjamin 实现的内容有所了解。

[![](https://p1.ssl.qhimg.com/t0131f622a72c77c33a.png)](https://p1.ssl.qhimg.com/t0131f622a72c77c33a.png)

[![](https://p0.ssl.qhimg.com/t0194e56e299480afc1.png)](https://p0.ssl.qhimg.com/t0194e56e299480afc1.png)

但是首先，为了便于讲解我将先介绍一些背景知识。



## 从 TGT 到 .kirbis

正如我们传统上所理解的那样，在 Kerberos 交换中使用一个 hash （ntlm/rc4_hmac, aes128_cts_hmac, aes256_cts_hmac. .等）从域控（也称为KDC，即密钥分发中心）获取票证授予票证（TGT）。在 Kerberos 语言中，这个交换过程涉及到向 KDC/DC 发送 AS-REQ（身份认证服务请求）进行身份认证，如果成功则将会生成一个 AS-REP （身份认证服务回复），其中包含一个TGT。但其实它还包含着其他内容。

Big note： TGT 本身是没用的。TGT 是用 Kerberos 服务（krbtgt）哈希加密/签名的不透明 blob 数据，所以普通用户无法将其解码。那么，TGT 实际上是如何使用的呢？

在成功认证用户后返回的 AS-REQ 中，TGT不是唯一的数据块，还有一个”加密的部分”，它是一个被标记的 [EncKDCRepPart 结构](https://github.com/gentilkiwi/kekeo/blob/fd852374dfcfae4ddf5e19e4d8eeb03833f08963/modules/asn1/KerberosV5Spec2.asn#L209-L227) ，使用用户的 hash 进行加密。使用的哈希格式（rc4_hmac, aes256_cts_hmac_sha1, 等）会在初始交换过程中进行协商。当这个 blob 被解密时，它会包含一组元数据，包括启动时间，结束时间，票据的更新期限等，但最重要的是它还会包含一个会话密钥，该密钥同时存在于不透明的 TGT blob 中（也是被用户的 krbtgt hash 进行加密的）。

那么用户/主机是如何“使用”TGT的呢？它会提供 TGT 和使用会话密钥加密的认证器 —— 这就证明客户端是知道在初始认证交换过程中所返回的会话密钥的（因此也会包含在 TGT 中）。TGT 续订，服务票据请求和 S4U 请求都会需要这个会话密钥。

那么这就说得通了;)

所有这些数据都会包含在一个 KRB-CRED 结构中。这就是 Mimikatz 语言中的 .kirbi 文件，代表通过已建立的 LSA API 提交的完整的 Kerberos 凭证的编码结构。因此，当我们谈论 “TGT” 时，我们实际上指的是可用的 TGT .kirbi 文件（其中包含有明文的会话密钥），而不仅仅是 TGT blob。我们将更深入的介绍一下这个重要区别。

此外，我还想快速地介绍一下从管理员权限和非管理员权限的条件下提取 Kerberos 票据的差异。Rubeus 的 dump 命令将根据 Rubeus 运行时所处的完整性级别来自动采取合适的方法。

如果是管理员权限，则一般的执行方法是：
1. 提取至系统权限。
1. 使用 [LsaRegisterLogonProcess()](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/nf-ntsecapi-lsaregisterlogonprocess) （需要SYSTEM权限）注册一个虚假的登录进程。这将向 LSA 服务器返回一个特权句柄。
1. 使用 [LsaEnumerateLogonSessions()](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/nf-ntsecapi-lsaenumeratelogonsessions) 枚举当前登陆会话。
1. 对于每个登录会话，构建一个 [KERB_QUERY_TKT_CACHE_REQUEST](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/ns-ntsecapi-_kerb_query_tkt_cache_request) 结构，用来表示此登录会话的 logon session ID ，和一个 [KerbQueryTicketCacheMessage](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/ne-ntsecapi-_kerb_protocol_message_type) 类型的消息类型。这将返回指定用户的登录会话中所缓存的所有 Kerberos 票据的相关信息。
1. 使用 KERB_QUERY_TKT_CACHE_REQUEST 调用 [LsaCallAuthenticationPackage()](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/nf-ntsecapi-lsacallauthenticationpackage) ，并解析返回的票据缓存信息。
<li>对于缓存中的每个票据信息位，构建一个 [KERB_RETRIEVE_TKT_REQUEST](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/ns-ntsecapi-_kerb_retrieve_tkt_request) 结构，此结构包含的内容为：[KerbRetrieveEncodedTicketMessage](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/ne-ntsecapi-_kerb_protocol_message_type) 的消息类型，当前正在迭代的登录会话ID，以及当前正在迭代的缓存中的票据所包含的目标服务器（即SPN）。这表明我们需要缓存中指定的服务票据的编码 KRB-CRED (.kirbi) blob 数据。PS – [用C#实现这个的过程比较令人讨厌 😉](https://github.com/GhostPack/Rubeus/blob/4c9145752395d48a73faf326c4ae57d2c565be7f/Rubeus/lib/LSA.cs#L506-L524)
</li>
1. 使用 KERB_RETRIEVE_TKT_REQUEST 调用 [LsaCallAuthenticationPackage()](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/nf-ntsecapi-lsacallauthenticationpackage) 并解析返回的 .kirbi 票据信息。
以上操作将返回当前系统上的登录的所有用户的所有 TGT 和 服务票据的完整 .kirbi blob 数据，无无须打开 LSASS 的读取句柄。当然你也可以选择使用 Mimikatz 的 sekurlsa::tickets /export 命令直接从 LSASS 进程的内存中导出所有的 Kerberos 票据，但是记住，那不是唯一的方法：）

[![](https://p5.ssl.qhimg.com/t01aaf868e093587801.png)](https://p5.ssl.qhimg.com/t01aaf868e093587801.png)

如果你处于非管理员权限，[则与上述的方法略有不同](https://github.com/GhostPack/Rubeus/blob/4c9145752395d48a73faf326c4ae57d2c565be7f/Rubeus/lib/LSA.cs#L685-L935):
1. 使用 [LsaConnectUntrusted()](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/nf-ntsecapi-lsaconnectuntrusted) 打开一个与 LSA 的不可信连接；
1. 使用 [KerbQueryTicketCacheMessage](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/ne-ntsecapi-_kerb_protocol_message_type) 消息类型构建一个 [KERB_QUERY_TKT_CACHE_REQUEST](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/ns-ntsecapi-_kerb_query_tkt_cache_request)，将返回当前用户的登录会话中缓存的所有 Kerberos 票据信息；
1. 使用 KERB_QUERY_TKT_CACHE_REQUEST 调用 [LsaCallAuthenticationPackage()](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/nf-ntsecapi-lsacallauthenticationpackage)，并解析返回的缓存票据信息；
1. 对于缓存中的每个票据信息位，构建一个消息类型为 [KerbRetrieveEncodedTicketMessage](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/ne-ntsecapi-_kerb_protocol_message_type) 的 [KERB_RETRIEVE_TKT_REQUEST](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/ns-ntsecapi-_kerb_retrieve_tkt_request) 结构，和缓存中我们正在迭代的票据的目标服务器（即SPN）。这表明我们需要缓存中指定的服务票据的编码 KRB-CRED (.kirbi) blob 数据；
1. 使用 KERB_RETRIEVE_TKT_REQUEST 调用 [LsaCallAuthenticationPackage()](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/nf-ntsecapi-lsacallauthenticationpackage) 并解析返回的 .kirbi 票据信息。
如果不是管理员权限，逻辑上只能请求当前登录会话的票据。并且，在 win7 以上系统，Windows 限制了从用户空间对 TGT 会话密钥的提取，所以当转储 TGT 时，你会得到如下结果：

[![](https://p3.ssl.qhimg.com/t015e5619e084d74417.png)](https://p3.ssl.qhimg.com/t015e5619e084d74417.png)

[![](https://p1.ssl.qhimg.com/t013fe782c500dce7f1.png)](https://p1.ssl.qhimg.com/t013fe782c500dce7f1.png)

这说明如果没有管理员权限，则无法为当前用户提取到可用 TGT .kirbis，请求到的会话密钥为空。图中 Mimikatz 的输出显示， [Microsoft 使用一个注册表项(allowtgtsessionkey)](https://support.microsoft.com/en-us/help/308339/registry-key-to-allow-session-keys-to-be-sent-in-kerberos-ticket-grant) 来允许返回 TGT 会话密钥。但是，默认情况下不启用此键值，并且需要管理员权限才能修改。

下文中的 tgtdeleg 章节将解释 Benjamin 绕过此限制的技巧。

返回会话密钥是为了制作服务票据。后面我们将看到其重要性。



## asktgs

第一个“重大的”新功能是通用服务票据请求：

asktgs 功能和 asktgt 功能一样，接受 /dc:X /ptt 参数。/ticket:X 参数一样是接受 .kirbi 文件的 base64 编码或 .kirbi 文件在磁盘上的路径。这票据是一个以 .kirbi 文件格式表示的 TGT （如前所述，完整的会话密钥），因此我们能够在一个 TGS-REQ/TGS-REP 交换中正确的请求一个服务票据。

/service:SPN 参数是必须的，用于指定要请求的服务票据的服务主体名称（SPN）。这个参数指定一个或多个以逗号分隔的 SPN 。如下所示：

操作上来讲，如果不是管理员权限，并且不想用 [上一篇文章描述的方法](http://www.harmj0y.net/blog/redteaming/from-kekeo-to-rubeus/) 将一个新的TGT覆盖当前登录会话中现有的TGT，你可以为指定账户请求一个TGT，并使用其 blob 和 asktgs 功能来请求/应用需要的服务票据。

有关服务票据接管原语的更多信息，请参考 [Sean Metcalf](https://twitter.com/PyroTek3/) 的博文 “[How Attackers Use Kerberos Silver Tickets to Exploit Systems](https://adsecurity.org/?p=2011)”中 “Service to Silver Ticket Reference” 部分。



## tgtdeleg

tgtdeleg 功能是对 Kekeo 的 tgt::deleg 函数的重新编码版本，允许你在非管理员权限下提取系统的当前登录用户的可用 TGT .kirbi文件。这利用了 Benjamin 发明的一个很酷的技巧，我将尝试详细解释一下，最后再介绍一些操作实例。

通用安全服务应用程序接口（GSS-API）是应用程序用来与安全服务交互的一个通用 API。虽然微软没有 [正式 支持 GSS-API](https://msdn.microsoft.com/en-us/library/ms995352.aspx), 但是它确实实现了 Kerberos 安全服务提供程序接口（SSPI），此接口与 Kerberos GSS-API 相兼容，意味着它支持所有常见的 Kerberos GSS-API 结构/方法。本文中将多次引用 [RFC4121](https://tools.ietf.org/html/rfc4121) 作为参考。

基本上，简单来说，你可以使用 Windows API 来请求通过 SSPI/GSS-API 发送到远程 host/SPN 的委托 TGT。这些结构中的一个包含着 KRBCRED（.kirbi）格式的当前用户的转发TGT，该 KRBCRED 被加密包含在 AP-REQ 中，以用于发送到目标服务器。用于加密 Authenticator / KRB-CRED 的会话密钥包含在目标 SPN 的服务票据中，此票据缓存于一个可访问的位置。将这些结合在一起，我们就可以在非管理员权限下提取当前用户的可用 TGT 了！

首先，使用 [AcquireCredentialsHandle()](https://msdn.microsoft.com/en-us/library/windows/desktop/aa374713(v=vs.85).aspx) 来获取当前用户现有 Kerberos 凭据的句柄。我们要为 fCredentialUse 参数指定 SECPKG_CRED_OUTBOUND，这将 “允许本地客户端凭证准备一个传出令牌”。

然后，使用 AcquireCredentialsHandle() 返回的凭据句柄和 [InitializeSecurityContext()](https://msdn.microsoft.com/en-us/library/windows/desktop/aa375507(v=vs.85).aspx) 建立一个“客户端的，出站安全上下文 ”。这里的技巧是为 fContextReq 参数指定 ISC_REQ_DELEGATE 和 ISC_REQ_MUTUAL_AUTH 标志。这将请求一个委派 TGT，意思是“服务器可以使用这个上下文来作为客户端向其他服务器进行认证。 ” 我们还为 pszTargetName 参数指定一个 SPN，此 SPN 代表的服务器应为无约束委派的（默认为 HOST/DC.domain.com）。这就是我们假装要进行委派请求的 SPN/服务器。

当触发这个 API 调用时将发生什么？

首先，将发生 TGS-REQ/TGS-REP 交换来请求我们假装要委派的 SPN 的服务票据。这样就将在目标服务器和我们发起连接的主机之间建立一个共享会话密钥。服务票据存储在本地的 Kerberos 缓存中，意味着我们稍后可以提取这个共享会话密钥。

接下来，将为当前用户请求一个转发TGT。转发票据的更多信息，请参考“什么是转发票据”的[章节](https://technet.microsoft.com/pt-pt/library/cc772815(v=ws.10).aspx)。KDC将使用当前TGT的单独会话密钥返回一个新的 TGT。系统将使用这个转发TGT为目标服务器建立一个 AP-REQ 请求，此请求中的认证器包含着转发TGT的可用 KRB-CRED 编码。这在 RFC4121 的 “4.1.1. Authenticator Checksum” 章节有说明。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0165bf615ffd6efe14.png)

最终的结果是什么呢？如果所有步骤都成功，我们将得到以SSPI[ SecBuffer](https://docs.microsoft.com/en-us/windows/desktop/api/sspi/ns-sspi-_secbuffer) 结构编码的 AP-ERQ(包含新TGT的.kirbi)，被传递给 InitializeSecurityContext() 的 pOutput 指针所指向。我们可以在输出流中搜索 [ KerberosV5 OID](https://github.com/gentilkiwi/kekeo/blob/fd852374dfcfae4ddf5e19e4d8eeb03833f08963/kekeo/modules/kuhl_m_tgt.c#L329-L345)，并从 GSS-API 输出中提取 AP-REQ。

然后就可以 [从缓存中](https://github.com/GhostPack/Rubeus/blob/4c9145752395d48a73faf326c4ae57d2c565be7f/Rubeus/lib/LSA.cs#L1247-L1248) 提取服务票据会话密钥并使用此密钥解密从 AP-REQ 中提取的 [认证器](https://github.com/GhostPack/Rubeus/blob/4c9145752395d48a73faf326c4ae57d2c565be7f/Rubeus/lib/LSA.cs#L1468-L1469)。最后我们可以从认证器校验和中提取编码的 KRB-CRED，并输出为可用的 TGT .kirbi:

[![](https://p0.ssl.qhimg.com/t01cc7dab0bf5e557bd.png)](https://p0.ssl.qhimg.com/t01cc7dab0bf5e557bd.png)

成功！m/

从操作的角度来看，这是一个比较小众的功能。我能想到的主要应用场景是，在一个环境中你已经控制了多个客户端，并且至少有一台主机你没有获取管理员权限。从这台主机上，你可以用Rubeus的 tgtdeleg 功能提取当前用户的 TGT，并将其和 /autorenew 标志一起传递给运行在另一台主机上的 Rubeus 的 renew 函数。这将允许你在不提权的情况下提取当前用户的凭证，并在另一台主机上进行最多7天（默认）的续订。

无论这个 TTP 是否有实际用处，理解和重新编码的过程给我带来了很多乐趣:)



## changepw

changepw 操作（即Kekeo中的 misc::changepw）是 <a>@Aorato POC</a> 的一个实现版本，允许攻击者利用一个 TGT .kirbi 修改用户的明文口令（无须知道口令的当前值）。将此与 asktgt 和用户的 rc4_hmac/aes128_cts_hmac_sha1/aes256_cts_hmac_sha1 哈希结合起来，意味着攻击者可以在已知用户口令hash的情况下轻松地强制重置一个用户的明文口令。或者，如果使用 Rubeus 的 dump 命令（管理员权限下）的话，攻击者只需用LSA API提取票据就能强制重置一个用户的口令。

在 [RFC3244](https://tools.ietf.org/html/rfc3244.html) (Microsoft Windows 2000 Kerberos Change Password and Set Password Protocols.) 中解释了这个过程。以下是发送到域控的464端口（kpasswd）的数据格式：

[![](https://p5.ssl.qhimg.com/t016b6965e7ce93e203.png)](https://p5.ssl.qhimg.com/t016b6965e7ce93e203.png)

有两个主要的部分：一个 AP-REQ 和一个特殊构造的 [KRB-PRIV](https://github.com/gentilkiwi/kekeo/blob/fd852374dfcfae4ddf5e19e4d8eeb03833f08963/modules/asn1/KerberosV5Spec2.asn#L289-L294) ASN.1 结构。AP-REQ 消息包含用户的 TGT blob，以及使用TGT .kribi中包含的TGT会话密钥加密的 [验证器](https://github.com/gentilkiwi/kekeo/blob/fd852374dfcfae4ddf5e19e4d8eeb03833f08963/modules/asn1/KerberosV5Spec2.asn#L248-L258) 。验证器必须具有随机 [子会话密钥](https://github.com/gentilkiwi/kekeo/blob/fd852374dfcfae4ddf5e19e4d8eeb03833f08963/modules/asn1/KerberosV5Spec2.asn#L255)集，用于加密后面的 KRB-PRIV 结构。KRB-PRIV 包含新的明文口令，[序列/随机数](https://github.com/gentilkiwi/kekeo/blob/fd852374dfcfae4ddf5e19e4d8eeb03833f08963/inc/globals.h#L34), 和 [发送者的主机地址](https://github.com/gentilkiwi/kekeo/blob/fd852374dfcfae4ddf5e19e4d8eeb03833f08963/modules/asn1/KerberosV5Spec2.asn#L301) （可任意指定）。

如果口令设置成功，则将返回一个 KRB-PRIV 结构，结构代码为0（KRB5_KPASSWD_SUCCESS）。错误代码为 KRB-ERROR 或其他错误代码。（在 [RFC3244](https://tools.ietf.org/html/rfc3244.html) 的第二部分末尾处定义）

[![](https://p0.ssl.qhimg.com/t01df7f513a009a2141.png)](https://p0.ssl.qhimg.com/t01df7f513a009a2141.png)

注意： 我不确定具体原因，使用 tgtdeleg 技巧提取的票据无法与此 changepw 方法一起使用，会返回一个 KRB5_KPASSWD_MALFORMED 错误。我用 Rubeus 和 Kekeo 都测试了，都是一样的结果。



## 其他变化

[其他更改/修复](https://github.com/GhostPack/Rubeus/blob/master/CHANGELOG.md#110---2018-09-31)
<li>s4u 操作现在接受多个可选 snames (/altservice:X,Y,… )
<ul>
1. 仅执行一次 S4U2self/S4U2proxy 过程，并将多个可选服务名称替换到最终返回的服务票据结果中，以获得尽可能多的 snames。
</ul>
</li>
1. 修正了 kerberoast 操作的哈希输出的encType提取，并将 KerberosRequestorSecurityToken.GetRequest 方法归功于 <a>@machosec</a>。
1. 修正了 asreproast hash的salt分界线，并添加了 Hashcat 的哈希输出格式。
1. 修正了 dump 操作中的一个bug——现在可以正确提取完整的 ServiceName/TargetName 字符串。
1. 我添加了一个基于 [CHANGELOG.md](https://github.com/GhostPack/Rubeus/blob/master/CHANGELOG.md) 的 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) 来记录当前和将来的一些修改。