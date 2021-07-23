> 原文链接: https://www.anquanke.com//post/id/210324 


# NTLM认证协议与SSP（下）——NTLM中高级进阶


                                阅读量   
                                **179873**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01da0b6cd153e1bc69.jpg)](https://p0.ssl.qhimg.com/t01da0b6cd153e1bc69.jpg)

上篇：[https://www.anquanke.com/post/id/210323](https://www.anquanke.com/post/id/210323)

内容参考原文链接：[http://davenport.sourceforge.net/ntlm.html](http://davenport.sourceforge.net/ntlm.html)

翻译人：rootclay（香山）[https://github.com/rootclay](https://github.com/rootclay)

Gitbook：[https://rootclay.gitbook.io/ntlm/](https://rootclay.gitbook.io/ntlm/)



## 说明

本文是一篇NTLM中高级进阶文章，文中大部分参考来自于[Sourceforge](http://davenport.sourceforge.net/ntlm.html)，原文中已经对NTLM讲解非常详细，在学习的过程中思考为何不翻译之，做为学习和后续回顾的文档，并在此基础上添加自己的思考，因此出现了这篇文章，在翻译的过程中会有部分注解与新加入的元素，后续我也会在Github对此文进行持续性的更新NTLM以及常见的协议中高级进阶并计划开源部分协议调试工具，望各位issue勘误。



## 摘要

本文旨在以中级到高级的详细级别描述NTLM身份验证协议(authentication protocol)和相关的安全支持提供程序功能(security support provider functionality)，作为参考。希望该文档能发展成为对NTLM的全面描述。目前，无论是在作者的知识还是在文档方面，都存在遗漏，而且几乎可以肯定的说本文是不准确的。但是，该文档至少应能够为进一步研究提供坚实的基础。本文提供的信息用作在开放源代码jCIFS库中实现NTLM身份验证的基础，该库可从 http://jcifs.samba.org获得。本文档基于作者的独立研究，并分析了[Samba](http://www.samba.org/)软件套件。



## NTLM版本2(NTLM Version 2)

NTLM版本2包含三种新的响应算法（NTLMv2，LMv2和NTLM2会话响应，如前所述）和新的签名和Sealing方案（NTLM2会话安全性）。NTLM2会话安全性是通过”Negotiate NTLM2 Key”FlagsNegotiate的；但是，可以通过修改注册表来启用NTLMv2身份验证。此外，客户端和域控制器上的注册表设置必须兼容才能成功进行身份验证（尽管NTLMv2身份验证有可能通过较旧的服务器传递到NTLMv2域控制器）。部署NTLMv2所需的配置和计划的结果是，许多主机仅使用默认设置（NTLMv1），而不怎么使用NTLMv2进行身份验证。

Microsoft知识库文章239869 中详细介绍了启用NTLM版本2的说明 。简要地，对注册表值进行了修改：<br>`HKEY_LOCAL_MACHINESystemCurrentControlSetControlLSALMCompatibilityLevel`<br>
（基于Win9x的系统上的LMCompatibility）。这是一个 REG_DWORD条目，可以设置为以下值之一：

<th style="text-align: left;">Level</th><th style="text-align: left;">Sent by Client</th><th style="text-align: left;">Accepted by Server</th>
|------
<td style="text-align: left;">0</td><td style="text-align: left;">LM&lt;br&gt;NTLM</td><td style="text-align: left;">LM&lt;br&gt;NTLM&lt;br&gt;LMv2&lt;br&gt;NTLMv2</td>
<td style="text-align: left;">1</td><td style="text-align: left;">LM&lt;br&gt;NTLM</td><td style="text-align: left;">LM&lt;br&gt;NTLM&lt;br&gt;LMv2&lt;br&gt;NTLMv2</td>
<td style="text-align: left;">2</td><td style="text-align: left;">NTLM</td><td style="text-align: left;">LM&lt;br&gt;NTLM&lt;br&gt;LMv2&lt;br&gt;NTLMv2</td>
<td style="text-align: left;">3</td><td style="text-align: left;">LMv2&lt;br&gt;NTLMv2</td><td style="text-align: left;">LM&lt;br&gt;NTLM&lt;br&gt;LMv2&lt;br&gt;NTLMv2</td>
<td style="text-align: left;">4</td><td style="text-align: left;">LMv2&lt;br&gt;NTLMv2</td><td style="text-align: left;">NTLM&lt;br&gt;LMv2&lt;br&gt;NTLMv2</td>
<td style="text-align: left;">5</td><td style="text-align: left;">LMv2&lt;br&gt;NTLMv2</td><td style="text-align: left;">LMv2&lt;br&gt;NTLMv2</td>

在所有级别中，都支持NTLM2会话安全性并在可用时进行Negotiate（大多数可用文档表明NTLM2会话安全性仅在级别1和更高级别上启用，但实际上在级别0上也可以看到）。默认情况下，在Windows 95和Windows 98平台上仅支持LM响应。安装Directory Services之后的客户端使NTLMv2也可以在这些主机上使用（并启用LMCompatibility 设置，尽管仅级别0和3可用）。

在级别2中，客户端两次发送NTLM响应（在LM和NTLM响应字段中）。在级别3和更高级别，LMv2和NTLMv2响应分别替换LM和NTLM响应。

协商了NTLM2会话安全性后（由”Negotiate NTLM2 Key”Flags指示），可以在级别0、1和2中使用NTLM2会话响应来代替较弱的LM和NTLM响应。与NTLMv1相比，这可以提供针对基于服务器的预先计算的字典攻击的增强保护。通过向计算中添加随机的客户随机数，可以使客户对给定challenge的响应变得可变。

NTLM2 session response很有趣，因为它可以在支持较新方案的客户端和服务器之间进行Negotiate，即使存在不支持较旧域控制器的情况也是如此。在通常情况下，身份验证事务中的服务器实际上并不拥有用户的密码哈希；而是保留在域控制器中。将计算机加入使用NT风格认证的域时，它会建立到域控制器（俗称” NetLogon pipe”）的经过加密，相互认证的通道。当客户端使用”原始” NTLMv1握手向服务器进行身份验证时，在后台进行以下事务：
1. 客户端发送Type 1消息，其中包含Flags和其他信息，如前所述。
1. 服务器为客户端生成一个质询，并发送包含Negotiate Flags集的Type 2消息。
1. 客户响应challenge，提供LM / NTLM响应。
1. 服务器通过NetLogon管道将质询和客户端响应发送到域控制器。
1. 域控制器使用存储的哈希值和服务器给出的质询来重现身份验证计算。如果它们与响应匹配，则认证成功。
1. 域控制器计算Session Key并将其发送到服务器，该Session Key可用于服务器和客户端之间的后续签名和Sealing操作。
在NTLM2会话响应的情况下，可能已升级了客户端和服务器以允许较新的协议，而域控制器却没有。为了考虑到这种情况，对上述握手进行了如下修改：
1. 客户端发送Type 1消息，在这种情况下，该消息指示”Negotiate NTLM2 Key”Flags。
1. 服务器为客户端生成质询，并发送包含NegotiateFlags集（还包括”Negotiate NTLM2 Key”Flags）的Type 2消息。
1. 客户端响应challenge，在LM字段中提供client nonce，并在NTLM字段中提供NTLM2会话响应（NTLM2 Session Response）。请注意，后者的计算与NTLM响应完全相同，只是客户端没有对服务器质询进行加密，而是对与client nonce连接的服务器质询的MD5哈希进行了加密。
1. 服务器不是将服务器质询直接通过NetLogon管道直接发送到域控制器，而是将服务器质询的MD5哈希与client nonce连接在一起（从LM响应字段中提取）。此外，它还发送客户端响应（照常）。
1. 域控制器使用存储的哈希作为Key对服务器发送的质询字段进行加密，并验证它与NTLM响应字段匹配；因此，客户端已成功通过身份验证。
<li>域控制器计算正常的NTLM用户Session Key并将其发送到服务器；服务器在次要计算中使用它来获取NTLM2会话响应用户Session Key（在后续部分中讨论 ）<br>
本质上，这允许已升级的客户端和服务器在尚未将域控制器升级到NTLMv2（或者网络管理员尚未将LMCompatibilityLevel注册表设置配置为使用NTLMv2）的网络中使用NTLM2会话响应。</li>
与LMCompatibilityLevel设置相关的是 NtlmMinClientSec和NtlmMinServerSec设置。这些规定了由NTLMSSP建立的NTLM上下文的最低要求。两者都是 REG_WORD条目，并且是指定以下NTLMFlags组合的位域：
1. Negotiate Sign（0x00000010）-指示必须在支持消息完整性（签名）的情况下建立上下文。
1. Negotiate Seal（0x00000020）-指示必须在支持消息机密性（Sealing）的情况下建立上下文。
1. Negotiate NTLM2 Key（0x00080000）-指示必须使用NTLM2会话安全性来建立上下文。
1. Negotiate 128（0x20000000）-指示上下文必须至少支持128位签名/SealingKey。
1. Negotiate 56（0x80000000）-指示上下文必须至少支持56位签名/SealingKey。
尽管其中大多数都更适用于NTLM2签名和Sealing，但”Negotiate NTLM2 Key”对于身份验证很重要，因为它可以防止与无法NegotiateNTLM2会话安全性的主机建立会话。这用于确保不发送LM和NTLM响应（要求认证在所有情况下至少将使用NTLM2会话响应）。



## NTLMSSP和SSPI

在这一点上，我们将开始研究NTLM如何适应”大局”（big picture）。关于SSPI内容也可以查看本链接中的简单说明[SSPI](https://daiker.gitbook.io/windows-protocol/ntlm-pian/4#0x04-ssp-and-sspi)

Windows提供了一个称为SSPI的安全框架-安全支持提供程序接口。这与GSS-API（通用安全服务应用程序接口，RFC 2743 ）在Microsoft中等效。 ），并允许应用认证，完整性和机密性原语的非常高级的机制无关的方法。SSPI支持多个基础提供程序（Kerberos、Cred SSP、Digest SSP、Negotiate SSP、Schannel SSP、Negotiate Extensions SSP、PKU2U SSP）。其中之一就是NTLMSSP（NTLM安全支持提供程序），它提供了到目前为止我们一直在讨论的NTLM身份验证机制。SSPI提供了一个灵活的API，用于处理不透明的，特定于提供程序的身份验证令牌。NTLM Type 1，Type 2和Type 3消息就是此类令牌，专用于NTLMSSP并由其处理。SSPI提供的API几乎抽象了NTLM的所有细节。应用程序开发人员甚至不必知道正在使用NTLM，并且可以交换另一种身份验证机制（例如Kerberos），而在应用程序级别进行的更改很少或没有更改。

在系统层面，SSP就是一个dll，来实现身份验证等安全功能，实现的身份验证机制是不一样的。比如 NTLM SSP 实现的就是一种 Challenge/Response 验证机制。而 Kerberos 实现的就是基于 ticket 的身份验证机制。我们可以编写自己的 SSP，然后注册到操作系统中，让操作系统支持更多的自定义的身份验证方法。

我们不会对SSPI框架进行深入研究，但这是研究应用于NTLM的SSPI身份验证握手的好方法：
1. 客户端通过SSPI AcquireCredentialsHandle函数为用户获取证书集的表示。
1. 客户端调用SSPI InitializeSecurityContext函数以获得身份验证请求令牌（在我们的示例中为Type 1消息）。客户端将此令牌发送到服务器。该函数的返回值表明身份验证将需要多个步骤。
1. 服务器从客户端接收令牌，并将其用作AcceptSecurityContext SSPI函数的输入 。这将在服务器上创建一个表示客户端的本地安全上下文，并生成一个身份验证响应令牌（Type 2消息），该令牌将发送到客户端。该函数的返回值指示需要客户端提供更多信息。
1. 客户端从服务器接收响应令牌，然后再次调用 InitializeSecurityContext，并将服务器的令牌作为输入传递。这为我们提供了另一个身份验证请求令牌（Type 3消息）。返回值指示安全上下文已成功初始化；令牌已发送到服务器。
1. 服务器从客户端接收令牌，并使用Type 3消息作为输入再次调用 AcceptSecurityContext。返回值指示上下文已成功接受；没有令牌产生，并且认证完成。
### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E8%AE%A4%E8%AF%81%EF%BC%88Local%20Authentication%EF%BC%89"></a>本地认证（Local Authentication）

我们在讨论的各个阶段都提到了本地身份验证序列。对SSPI有基本的了解后，我们可以更详细地研究这种情况。

基于NTLM消息中的信息，客户端和服务器通过一系列决策来协商本地身份验证。其工作方式如下：
1. 客户端调用AcquireCredentialsHandle函数，通过将null传递给”pAuthData”参数来指定默认凭据。这将获得用于单点登录的登录用户凭据的句柄。
1. 客户端调用SSPI InitializeSecurityContext函数来创建Type 1消息。提供默认凭据句柄时，Type 1消息包含客户端的工作站和域名。这由”Negotiate Domain Supplied”和”Negotiate Workstation Supplied”Flags的存在以及消息中包含已填充的”已提供的域（Supplied Domain）”和”工作站的安全性（Supplied Workstation security）”标记来表明。
1. 服务器从客户端接收Type 1消息，并调用 AcceptSecurityContext。这将在服务器上创建一个代表客户端的本地安全上下文。服务器检查客户端发送的域和工作站信息，以确定客户端和服务器是否在同一台计算机上。如果是这样，则服务器通过在结果2类消息中设置”Negotiate Local Call”Flags来启动本地身份验证。Type 2消息的Context字段中的第一个long填充了新获得的SSPI上下文句柄的”upper”部分（特别是SSPI CtxtHandle结构的” dwUpper”字段）。第二个long在所有情况下，”上下文”字段中的”空白”都为空。（尽管从逻辑上讲，它会假定它应包含上下文句柄的”下部”部分）。
1. 客户端从服务器接收Type 2消息，并将其传递给 InitializeSecurityContext。注意了”Negotiate Local Call”Flags的存在之后，客户端检查服务器上下文句柄以确定它是否代表有效的本地安全上下文。如果无法验证上下文，则身份验证将照常进行-计算适当的响应，并将其包含在Type 3消息中的域，工作站和用户名中。如果来自Type 2消息的安全上下文句柄可以验证，但是，没有准备任何答复。而是，默认凭据在内部与服务器上下文相关联。生成的Type 3消息完全为空，其中包含响应长度为零的安全缓冲区以及用户名，域和工作站。
1. 服务器收到Type 3消息，并将其用作AcceptSecurityContext函数的输入 。服务器验证安全上下文已与用户关联；如果是这样，则认证已成功完成。如果上下文尚未绑定到用户，则身份验证失败。
### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E6%8A%A5%E8%AE%A4%E8%AF%81%EF%BC%88Datagram%20Authentication%EF%BC%89%EF%BC%88%E9%9D%A2%E5%90%91%E6%97%A0%E8%BF%9E%E6%8E%A5%EF%BC%89"></a>数据报认证（Datagram Authentication）（面向无连接）

数据报样式验证用于通过无连接传输Negotiate NTLM。尽管消息周围的许多语义保持不变，但仍存在一些重大差异：
1. 在第一次调用InitializeSecurityContext的过程中，SSPI不会创建Type 1消息 。
1. 身份验证选项由服务器提供，而不是由客户端请求。
1. Type 3消息中的Flags将会有用（如在面向连接的身份验证中）。
在”normal”（面向连接）身份验证期间，在交换Type 1和Type 2消息期间，所有选项都在客户端和服务器之间的第一个事务中Negotiate。Negotiate的设置由服务器”remembered”，并应用于客户端的Type 3消息。尽管大多数客户端发送带有Type 3消息的Negotiate一致的Flags，但它们未用于连接身份验证。（注：也就是Type3消息的Flag是没有用的）

但是，在数据报身份验证中，规则发生了一些变化。为了减轻服务器跟踪Negotiate选项的需要（如果没有持久连接，这将变得困难），将Type 1消息完全删除。服务器生成包含所有受支持Flags的Type 2消息（当然还有质询）。然后，客户端决定它将支持哪些选项，并以Type 3消息进行答复，其中包含对质询的响应和一组选定Flags。数据报认证的SSPI握手序列如下：
1. 客户端调用AcquireCredentialsHandle以获得用户证书集的表示。
1. 客户端调用InitializeSecurityContext，并通过fContextReq参数将 ISC_REQ_DATAGRAMFlags作为上下文要求传递。这将启动客户端的安全上下文的建设，但并没有产生令牌的请求（Type 1的消息）。
1. 服务器调用AcceptSecurityContext函数，指定 ASC_REQ_DATAGRAM上下文要求Flags并传入空输入令牌。这将创建本地安全上下文，并生成身份验证响应令牌（Type 2消息）。此Type 2消息将包含”Negotiate数据报样式”Flags，以及服务器支持的所有Flags。照常发送给客户端。
1. 客户端收到Type 2消息，并将其传递给 InitializeSecurityContext。客户端从服务器提供的选项中选择适当的选项（包括必须设置的”Negotiate数据报样式”），创建对质询的响应，并填充Type 3消息。然后，该消息将中继到服务器。
1. 服务器将Type 3消息传递到AcceptSecurityContext 函数中。根据客户端选择的Flags来处理消息，并且上下文被成功接受。
与SSPI一起使用时，显然无法产生数据报样式的Type 1消息。但是，有趣的是，我们可以通过巧妙地操纵NTLMSSP令牌来产生我们自己的数据报Type 1令牌，从而在较低级别上”诱导”数据报语义。

这可以通过在将令牌传递到服务器之前，在面向连接的SSPI握手中在第一个InitializeSecurityContext调用产生的Type 1消息上设置”NegotiateNegotiate Datagram Style”Flags来实现。当将修改后的Type 1消息传递到 AcceptSecurityContext函数中时，服务器将采用数据报语义（即使未指定ASC_REQ_DATAGRAM）。这将产生设置了”Negotiate Datagram Style”Flags的2类消息，但与通常会生成的面向连接的消息相同；也就是说，在构造Type 2消息时会考虑客户端发送的Type 1Flags，而不是简单地提供所有受支持的选项。

然后，客户端可以使用此Type 2令牌调用InitializeSecurityContext。请注意，客户端仍处于面向连接的模式。生成的Type 3消息将忽略应用于Type 2消息的”Negotiate Datagram Style”Flags。但是，服务器正在执行数据报语义，并且现在将要求正确设置Type 3Flags。在将”Negotiate Datagram Style”Flags添加到Type 3消息之前，将其手动发送到服务器之前，可以使服务器使用修改后的令牌成功调用 AcceptSecurityContext。

这样可以成功进行身份验证；”篡改”Type 1消息有效地将服务器切换到数据报式身份验证，其中将观察并强制使用Type 3Flags。目前没有已知的实际用途，但是它确实演示了可以通过策略性地处理NTLM消息来观察到的一些有趣和意外的行为。



## 会话安全性-签名和盖章概念（Session Security – Signing &amp; Sealing Concepts）

除了SSPI身份验证服务，还提供了消息完整性和机密性功能。这也由NTLM安全支持提供程序实现。”签名”由SSPI MakeSignature函数执行，该函数将消息验证码（MAC）应用于消息（message）。收件人可以对此进行验证，并且可以强有力地确保消息在传输过程中没有被修改。签名是使用发送方和接收方已知的Key生成的；MAC只能由拥有Key的一方来验证（这反过来可以确保签名是由发送方创建的）。”Sealing”由SSPI EncryptMessage执行功能。这会对消息应用加密，以防止传输中的第三方查看它（类似HTPPS）；NTLMSSP使用多种对称加密机制（使用相同的Key进行解密和加密）。

NTLM身份验证过程的同时会建立用于签名和Sealing的Key。除了验证客户端的身份外，身份验证握手还在客户端和服务器之间建立了一个上下文，其中包括在各方之间签名和Sealing消息所需的Key。我们将讨论这些Key的产生以及NTLMSSP用于签名和Sealing的机制。

在签名和盖章过程中采用了许多关键方案。我们将首先概述不同Type的Key和核心会话安全性概念。

### <a class="reference-link" name="The%20User%20Session%20Key"></a>The User Session Key

这是会话安全中使用的基本Key Type。有很多变体：
- LM User Session Key
- NTLM User Session Key
- LMv2 User Session Key
- NTLMv2 User Session Key
- NTLM2 Session Response User Session Key
所使用的推导方法取决于Type 3消息中发送的响应。这些变体及其计算概述如下。

**<a class="reference-link" name="LM%20User%20Session%20Key"></a>LM User Session Key**

仅在提供LM响应时（即，对于Win9x客户端）使用。LM用户Session Key的得出如下：
1. 16字节LM哈希（先前计算）被截断为8字节。
1. 将其空填充为16个字节。该值是LM用户Session Key。
与LM哈希本身一样，此Key仅响应于用户更改密码而更改。还要注意，只有前7个密码字符输入了Key（请参阅LM响应的计算过程 ； LM用户Session Key是LM哈希的前半部分）。此外，Key空间实际上要小得多，因为LM哈希本身基于大写密码。所有这些因素加在一起使得LM用户Session Key非常难以抵抗攻击。

<a class="reference-link" name="NTLM%20User%20Session%20Key"></a>**NTLM User Session Key**

客户端发送NTLM响应时，将使用此变体。Key的计算非常简单：
1. 获得NTLM哈希（Unicode大小写混合的密码的MD4摘要，先前已计算）。
1. MD4消息摘要算法应用于NTLM哈希，结果为16字节。这是NTLM用户Session Key。
NTLM用户Session Key比LM用户Session Key有了很大的改进。密码空间更大（区分大小写，而不是将密码转换为大写）；此外，所有密码字符都已输入到Key生成中。但是，它仍然仅在用户更改其密码时才更改。这使得离线攻击变得更加容易。

<a class="reference-link" name="LMv2%20User%20Session%20Key"></a>**LMv2 User Session Key**

发送LMv2响应（但不发送NTLMv2响应）时使用。派生此Key有点复杂，但并不十分复杂：
1. 获得NTLMv2哈希（如先前计算的那样）。
1. 获得LMv2client nonce（用于LMv2响应）。
1. 来自Type 2消息的质询与client nonce串联在一起。使用NTLMv2哈希作为Key，将HMAC-MD5消息认证代码算法应用于此值，从而得到16字节的输出值。
1. 再次使用NTLMv2哈希作为Key，将HMAC-MD5算法应用于该值。结果为16个字节的值是LMv2 User Session Key。
LMv2 User Session Key相对于基于NTLMv1的Key提供了一些改进。它是从NTLMv2哈希派生而来的（它本身是从NTLM哈希派生的），它特定于用户名和域/服务器。此外，服务器质询和client nonce都为Key计算提供输入。Key计算也可以简单地表示为LMv2响应的前16个字节的HMAC-MD5摘要（使用NTLMv2哈希作为Key）。

<a class="reference-link" name="NTLMv2%20User%20Session%20Key"></a>**NTLMv2 User Session Key**

发送NTLMv2响应时使用。该Key的计算与LMv2用户Session Key非常相似：
1. 获得NTLMv2哈希（如先前计算的那样）。
1. 获得NTLMv2”blob”（与NTLMv2响应中使用的一样）。
1. 来自Type 2消息的challenge与Blob连接在一起作为待加密值。使用NTLMv2哈希作为Keykey，将HMAC-MD5消息认证代码算法应用于此值，从而得到16字节的输出值。
1. 再次使用NTLMv2哈希作为Key，将HMAC-MD5算法应用于第三步的值。结果为16个字节的值是NTLMv2用户Session Key。
NTLMv2 User Session Key在密码上与LMv2 User Session Key非常相似。可以说是NTLMv2响应的前16个字节的HMAC-MD5摘要（使用NTLMv2哈希作为关键字）。

<a class="reference-link" name="NTLM2%20Session%20Response%20User%20Session%20Key"></a>**NTLM2 Session Response User Session Key**

当NTLMv1身份验证与NTLM2会话安全性一起使用时使用。该Key是从NTLM2会话响应信息中派生的，如下所示：
1. 如前所述，将获得NTLM User Session Key。
1. 获得session nonce（先前已讨论过，这是Type 2质询和NTLM2会话响应中的随机数的串联）。
1. 使用NTLM User Session Key作为Key，将HMAC-MD5算法应用于session nonce。结果为16个字节的值是NTLM2会话响应用户Session Key。
NTLM2会话响应用户Session Key的显着之处在于它是在客户端和服务器之间而不是在域控制器上计算的。域控制器像以前一样导出NTLM用户Session Key，并将其提供给服务器。如果已经与客户端Negotiate了NTLM2会话安全性，则服务器将使用NTLM用户Session Key作为MACKey来获取session nonce的HMAC-MD5摘要。

<a class="reference-link" name="%E7%A9%BA%E7%94%A8%E6%88%B7Session%20Key%EF%BC%88The%20Null%20User%20Session%20Key%EF%BC%89"></a>**空用户Session Key（The Null User Session Key）**

当执行匿名身份验证时，将使用Null用户Session Key。这很简单；它只有16个空字节（” 0x000000000000000000000000000000000000 “）。

### <a class="reference-link" name="Lan%20Manager%20Session%20Key"></a>Lan Manager Session Key

Lan Manager Session Key是User Session Key的替代方法，用于在设置”Negotiate Lan Manager Key” NTLM Flags时派生NTLM1签名和Sealing中的Key。Lan ManagerSession Key的计算如下：
1. 16字节LM哈希（先前计算）被截断为8字节。
1. 这将填充为14个字节，其值为”0xbdbdbdbdbdbdbd “。
1. 该值分为两个7字节的一半。
1. 这些值用于创建两个DESKey（每个7字节的一半为一个）。
1. 这些Key中的每一个都用于对LM响应的前8个字节进行DES加密（导致两个8字节密文值）。
1. 这两个密文值连接在一起形成一个16字节的值-Lan ManagerSession Key。
请注意，Lan ManagerSession Key基于LM响应（而不是简单的LM哈希），这意味着它将响应于不同的服务器challenge而更改。与仅基于密码哈希的LM和NTLM用户Session Key相比，这是一个优势。Lan ManagerSession Key会针对每个身份验证操作进行更改，而LM / NTLM用户Session Key将保持不变，直到用户更改其密码为止。因此，Lan ManagerSession Key比LM用户Session Key（两者具有相似的Key强度，但Lan ManagerSession Key可以防止重放攻击）要强得多。NTLM用户Session Key具有完整的128位Key空间，但与LM用户Session Key一样，在每次身份验证时也不相同。

### <a class="reference-link" name="Key%20Exchange%EF%BC%88%E5%AF%86%E9%92%A5%E4%BA%A4%E6%8D%A2%EF%BC%89"></a>Key Exchange（密钥交换）

当设置”Negotiate Key Exchange”Flags时，客户端和服务器将会就”secondary”Key达成共识，该Key用于代替Session Key进行签名和Sealing。这样做如下：
1. 客户端选择一个随机的16字节Key（辅助Key，也就是py-ntlm中的exported_session_key）。
1. Session Key（User Session Key或Lan Manager Session Key，取决于”Negotiate Lan ManagerKey”Flags的状态）用于RC4加密辅助Key。结果是一个16字节的密文值（注：也就是py-ntlm中的encrypted_random_session_key）。
1. 此值在Type 3消息的”Session Key”字段中发送到服务器。
1. 服务器接收Type 3消息并解密客户端发送的值（使用带有用户Session Key或Lan ManagerSession Key的RC4）。
1. 结果值是恢复的辅助Key，并代替Session Key进行签名和Sealing。
此外，密钥交换过程巧妙地更改了NTLM2会话安全性中的签名协议（在后续部分中讨论）。

### <a class="reference-link" name="%E5%BC%B1%E5%8C%96Key%EF%BC%88Key%20Weakening%EF%BC%89"></a>弱化Key（Key Weakening）

根据加密输出限制，用于签名和Sealing的Key已被弱化（”weakened”）（注：可能是由于加密性能原因）。Key强度由”Negotiate128”和”Negotiate56”Flags确定。使用的最终Key的强度是客户端和服务器都支持的最大强度。如果两个Flags都未设置，则使用默认的Key长度40位。NTLM1签名和Sealing支持40位和56位Key；NTLM2会话安全性支持40位，56位和不变的128位Key。



## NTLM1会话安全

NTLM1是”原始” NTLMSSP签名和Sealing方案，在未协商”Negotiate NTLM2 Key”Flags时使用。此方案中的Key派生由以下NTLM的Flags驱动：

|Flag|说明
|------
|Negotiate Lan Manager Key|设置后，Lan Manager会话密钥将用作签名和密封密钥（而不是用户会话密钥）的基础。 如果未建立，则用户会话密钥将用于密钥派生。（When set, the Lan Manager Session Key is used as the basis for the signing and sealing keys (rather than the User Session Key). If not established, the User Session Key will be used for key derivation. ）
|Negotiate 56|表示支持56位密钥。 如果未协商，将使用40位密钥。 这仅适用于与“协商Lan Manager密钥”结合使用； 在NTLM1下，用户会话密钥不会减弱（因为它们已经很弱）。（Indicates support for 56-bit keys. If not negotiated, 40-bit keys will be used. This is only applicable in combination with “Negotiate Lan Manager Key”; User Session Keys are not weakened under NTLM1 (as they are already weak).）
|Negotiate Key Exchange|表示将执行密钥交换以协商用于签名和密封的辅助密钥。（Indicates that key exchange will be performed to negotiate a secondary key for signing and sealing.）

### <a class="reference-link" name="NTLM1Key%E6%B4%BE%E7%94%9F"></a>NTLM1Key派生

要产生或是派生NTLM1Key本质上是一个三步过程：
1. Master key negotiation
1. Key exchange
1. Key weakening
<a class="reference-link" name="Master%20key%20negotiation"></a>**Master key negotiation**

第一步是Negotiate128位”Master Key”，从中将得出最终的签名和Sealing的Key。这是由NTLMFlags”Negotiate Lan Manager Key”驱动的；如果设置，则Lan ManagerSession Key将用作Master Key。否则，将使用适当的用户Session Key。

例如，考虑我们的示例用户，其密码为” SecREt01”。如果未设置”Negotiate Lan Manager”Key，并且在Type 3消息中提供了NTLM响应，则将选择NTLM用户Session Key作为Master Key。这是通过获取NTLM哈希的MD4摘要（本身就是Unicode密码的MD4哈希）来计算的：

0x3f373ea8e4af954f14faa506f8eebdc4

**<a class="reference-link" name="%E5%AF%86%E9%92%A5%E4%BA%A4%E6%8D%A2%EF%BC%88Key%20exchange%EF%BC%89"></a>密钥交换（Key exchange）**

如果设置了”Negotiate Key exchange”Flags，则客户端将使用新的Master Key（使用先前选择的Master Key进行RC4加密）填充Type 3消息中的”Session Key”字段。服务器将解密该值以接收新的Master Key。

例如，假定客户端选择随机Master Key” 0xf0f0aabb00112233445566778899aabb “。客户端将使用先前Negotiate的Master Key（” 0x3f373ea8e4af954f14faa506f8eebdc4 “）做为Key使用RC4加密此随机Master Key，以获取该值：

0x1d3355eb71c82850a9a2d65c2952e6f3

它在Type 3消息的”Session Key”字段中发送到服务器。服务器RC4-使用旧的Master Key对该值解密，以恢复客户端选择的新的Master Key（” 0xf0f0aabb00112233445566778899aabb “）。

<a class="reference-link" name="%E5%BC%B1%E5%8C%96Key%EF%BC%88Key%20Weakening%EF%BC%89"></a>**弱化Key（Key Weakening）**

最后，关键是要弱化以遵守出口限制。NTLM1支持40位和56位Key。如果设置了” Negotiate 56” NTLMFlags，则128位Master Key将减弱为56位；如果不设置，它将被削弱到40位。请注意，仅在使用Lan Manager Session Key（设置了”NegotiateLan ManagerKey”）时，才在NTLM1下采用Key弱化功能。LM和NTLM 的 User Session Key基于密码散列，而不是响应。给定的密码将始终导致NTLM1下具有相同的用户Session Key。显然不需要弱化，因为给定用户的密码哈希可以轻松恢复User Session Key。

NTLM1下的Key弱化过程如下：
- 要生成56位Key，Master Key将被截断为7个字节（56位），并附加字节值” 0xa0 “。
- 要生成40位Key，Master Key将被截断为5个字节（40位），并附加三个字节的值” 0xe538b0 “。
以Master Key” 0x0102030405060708090a0b0c0d0e0f00 “为例，用于签名和Sealing的40位Key为” 0x0102030405e538b0 “。如果Negotiate了56位Key，则最终Key将为” 0x01020304050607a0 “。

### <a class="reference-link" name="%E7%AD%BE%E5%90%8D"></a>签名

一旦协商了Key，就可以使用它来生成数字签名，从而提供消息完整性。通过存在”Negotiate Flags” NTLMFlags来指示对签名的支持。

NTLM1签名（由SSPI MakeSignature函数完成）如下：
1. 使用先前Negotiate的Key初始化RC4密码。只需执行一次（在第一次签名操作之前），并且Key流永远不会重置。
1. 计算消息的CRC32校验和；它表示为长整数（32位Little-Endian值）。
1. 获得序列号；它从零开始，并在每条消息签名后递增。该数字表示为长号。
1. 将四个零字节与CRC32值和序列号连接起来，以获得一个12字节的值（” 0x00000000 “ + CRC32（message）+ sequenceNumber）。
1. 使用先前初始化的RC4密码对该值进行加密。
1. 密文结果的前四个字节被伪随机计数器值覆盖（使用的实际值无关紧要）。
1. 将版本号（” 0x01000000 “）与上一步的结果并置以形成签名。
例如，假设我们使用上一个示例中的40位Key对消息” jCIFS “（十六进制” 0x6a43494653 “）进行签名：
1. 计算CRC32校验和（使用小端十六进制” 0xa0310宝宝7 “）。
1. 获得序列号。由于这是我们签名的第一条消息，因此序列号为零（” 0x00000000 “）。
1. 将四个零字节与CRC32值和序列号连接起来，以获得一个12字节的值（” 0x00000000a0310宝宝700000000 “）。
1. 使用我们的Key（” 0x0102030405e538b0 “）对这个值进行RC4加密；这将产生密文” 0xecbf1ced397420fe0e5a0f89 “。
1. 前四个字节被计数器值覆盖；使用” 0x78010900 “给出” 0x78010900397420fe0e5a0f89 “。
<li>将版本图章与结果连接起来以形成最终签名：<br>
0x0100000078010900397420fe0e5a0f89</li>
下一条签名的消息将接收序列号1；同样，再次注意，用第一个签名初始化的RC4Key流不会为后续签名重置。

### <a class="reference-link" name="Sealing"></a>Sealing

除了消息完整性之外，还通过Sealing来提供消息机密性。”Negotiate Sealing” NTLMFlags表示支持Sealing。在具有NTLM提供程序的SSPI下，Sealing总是与签名结合进行（Sealing消息会同时生成签名）。相同的RC4Key流用于签名和Sealing。

NTLM1Sealing（由SSPI EncryptMessage函数完成）如下：
1. 使用先前Negotiate的Key初始化RC4密码。只需执行一次（在第一次Sealing操作之前），并且Key流永远不会重置。
1. 使用RC4密码对消息进行加密；这将产生Sealing的密文。
1. 如前所述，将生成消息的签名，并将其放置在安全尾部缓冲区中。
例如，考虑使用40位Key” 0x0102030405e538b0 “ 对消息” jCIFS “（” 0x6a43494653 “）进行Sealing：
1. 使用我们的Key（” 0x0102030405e538b0 “）初始化RC4密码。
1. 我们的消息通过RC4密码传递，并产生密文” 0x86fc55abca “。这是Sealing消息。
1. 我们计算出消息的CRC32校验和（使用小尾数十六进制” 0xa0310宝宝7 “）。
1. 获得序列号。由于这是第一个签名，因此序列号为零（” 0x00000000 “）。
1. 将四个零字节与CRC32值和序列号连接起来，以获得一个12字节的值（” 0x00000000a0310宝宝700000000 “）。
1. 该值是使用来自密码的Key流进行RC4加密的；这将产生密文” 0x452b490efa3e828bcc8affc3 “。
1. 前四个字节被计数器值覆盖；使用” 0x78010900 “给出” 0x78010900fa3e828bcc8affc3 “。
<li>版本标记与结果串联在一起，以形成最终签名，并将其放置在安全尾部缓冲区中：<br>
0x0100000078010900fa3e828bcc8affc3整个Sealing结构的十六进制转储为：0x86fc55abca0100000078010900fa3e828bcc8affc3</li>


## NTLM2会话安全

NTLM2是更新的签名和Sealing方案，在建立”NegotiateNTLM2Key”Flags时使用。此方案中的Key派生由以下NTLMFlags驱动：

|Flags|说明
|------
|Negotiate NTLM2 Key|表示支持NTLM2会话安全性。
|Negotiate56|表示支持56位Key。如果既未指定此Flags也未指定”Negotiate128”，则将使用40位Key。
|Negotiate128|表示支持128位Key。如果既未指定此Flags也未指定”Negotiate56”，则将使用40位Key。
|NegotiateKey交换|表示将执行Key交换以Negotiate用于签名和Sealing的辅助基本Key。

### <a class="reference-link" name="NTLM2Key%E6%B4%BE%E7%94%9F"></a>NTLM2Key派生

NTLM2中的Key派生分为四个步骤：
1. Master Key Negotiate
1. Key exchange
1. Key weakening
1. Subkey generation
**<a class="reference-link" name="Master%20Key%20Negotiate"></a>Master Key Negotiate**

用户Session Key在NTLM2签名和Sealing中始终用作基本Master Key。使用NTLMv2身份验证时，LMv2或NTLMv2用户Session Key将用作Master Key。当NTLMv1身份验证与NTLM2会话安全一起使用时，NTLM2会话响应用户Session Key将用作Master Key。请注意，NTLM2中使用的用户Session Key比NTLM1对应的用户Session Key或Lan Manager Session Key要强得多，因为它们同时包含服务器质询和client nonce。

<a class="reference-link" name="Key%E4%BA%A4%E6%8D%A2"></a>**Key交换**

如先前针对NTLM1所讨论的那样执行Key交换。客户端选择一个辅助Master Key，RC4用基本Master Key对其进行加密，然后在Type 3”Session Key”字段中将密文值发送到服务器。这由”Negotiate Key exchange”Flags的存在指示。

<a class="reference-link" name="%E5%BC%B1%E5%8C%96Key"></a>**弱化Key**

NTLM2中的Key弱化仅通过将Master Key（或辅助Master Key，如果执行了Key交换）截短到适当的长度即可完成；例如，Master Key” 0xf0f0aabb00112233445566778899aabb “将减弱为40位，如” 0xf0f0aabb00 “和56位为” 0xf0f0aabb001122 “。请注意，NTLM2支持128位Key。在这种情况下，Master Key直接用于生成子Key（不执行弱化操作）。

仅当生成Sealing子Key时，Master Key才会在NTLM2下减弱。完整的128位Master Key始终用于生成签名Key。

**<a class="reference-link" name="%E5%AD%90%E9%A1%B9%E7%94%9F%E6%88%90"></a>子项生成**

在NTLM2下，最多可以建立四个子项。Master Key实际上从未用于Signing或Sealing消息。子项生成如下：
<li>128位（无弱点）Master Key与以空值终止的ASCII常量字符串连接：<br>
客户端到服务器签名的Session Key魔术常数以十六进制表示，此常数是：0x73657373696f6e206b657920746f2063<br>
6c69656e742d746f2d73657276657220<br>
7369676e696e67206b6579206d616769<br>
6320636f6e7374616e7400<br>
上面的换行符仅用于显示目的。将MD5消息摘要算法应用于此算法，从而得到一个16字节的值。这是客户端Signing Key，客户端使用它来为消息创建签名。</li>
<li>原生的128位Master Key与以空值终止的ASCII常量字符串连接：<br>
服务器到客户端签名的Session Key魔术常数以十六进制表示，此常数是：0x73657373696f6e206b657920746f2073<br>
65727665722d746f2d636c69656e7420<br>
7369676e696e67206b6579206d616769<br>
6320636f6e7374616e7400<br>
将使用此内容的MD5摘要，从而获得16字节的服务器Signing Key。服务器使用它来创建消息的签名。</li>
<li>弱化的Master Key（取决于Negotiate的是40位，56位还是128位加密）与以空值结尾的ASCII常量字符串连接：<br>
客户端到服务器的Session KeySealingKey魔术常数以十六进制表示，此常数是：0x73657373696f6e206b657920746f2063<br>
6c69656e742d746f2d73657276657220<br>
7365616c696e67206b6579206d616769<br>
6320636f6e7374616e7400<br>
使用MD5摘要来获取16字节的客户端Sealing Key。客户端使用它来加密消息。</li>
<li>弱化的主键与以空值终止的ASCII常量字符串连接：<br>
服务器到客户端的Session KeySealingKey魔术常数以十六进制表示，此常数是：0x73657373696f6e206b657920746f2073<br>
65727665722d746f2d636c69656e7420<br>
7365616c696e67206b6579206d616769<br>
6320636f6e7374616e7400<br>
应用MD5摘要算法，产生16字节的服务器Sealing Key。服务器使用此Key来加密消息。</li>
<a class="reference-link" name="%E7%AD%BE%E5%90%8D%EF%BC%88Signing%EF%BC%89"></a>**签名（Signing）**

签名支持再次由”Negotiate Signing” NTLMFlags指示。客户端签名是使用客户端签名Key完成的；服务器使用服务器签名Key对消息进行签名。签名Key是从无损的Master Key生成的（如前所述）。

NTLM2签名（由SSPI MakeSignature函数完成）如下：
1. 获得序列号；它从零开始，并在每条消息签名后递增。该数字表示为长整数（32位Little-endian值）。
1. 序列号与消息串联在一起。HMAC-MD5消息认证代码算法使用适当的签名Key应用于此值。这将产生一个16字节的值。
1. 如果已NegotiateKey交换，则使用适当的SealingKey初始化RC4密码。这一次完成（在第一次操作期间），并且Key流永远不会重置。HMAC结果的前八个字节使用此RC4密码加密。如果Key交换还没有经过谈判，省略这个Sealing操作。
1. 将版本号（” 0x01000000 “）与上一步的结果和序列号连接起来以形成签名。
例如，假设我们使用Master Key” 0x0102030405060708090a0b0c0d0e0f00 “ 在客户端上对消息” jCIFS “（十六进制” 0x6a43494653 “）进行签名。这与客户端到服务器的签名常量连接在一起，并应用MD5生成客户端签名Key（” 0xf7f97a82ec390f9c903dac4f6aceb132 “）和客户端SealingKey（” 0x2785f595293f3e2813439d73a223810d “）；这些用于签名消息如下：
1. 获得序列号。由于这是我们签名的第一条消息，因此序列号为零（” 0x00000000 “）。
<li>序列号与消息串联在一起：<br>
0x000000006a43494653使用客户端签名Key（” 0xf7f97a82ec390f9c903dac4f6aceb132 “）应用HMAC-MD5 。结果是16字节的值” 0x0a003602317a759a720dc9c7a2a95257 “。</li>
1. 使用我们的SealingKey（” 0x2785f595293f3e2813439d73a223810d “）初始化RC4密码。先前结果的前八个字节通过密码传递，产生密文” 0xe37f97f2544f4d7e “。
<li>将版本标记与上一步的结果和序列号连接起来，以形成最终签名：<br>
0x01000000e37f97f2544f4d7e00000000</li>
<a class="reference-link" name="Sealing"></a>**Sealing**

“Negotiate Sealing” NTLMFlags再次表明支持NTLM2中的消息机密性。NTLM2Sealing（由SSPI EncryptMessage函数完成）如下：
1. RC4密码使用适当的SealingKey初始化（取决于客户端还是服务器正在执行Sealing）。只需执行一次（在第一次Sealing操作之前），并且Key流永远不会重置。
1. 使用RC4密码对消息进行加密；这将产生Sealing的密文。
1. 如前所述，将生成消息的签名，并将其放置在安全尾部缓冲区中。请注意，签名操作中使用的RC4密码已经初始化（在前面的步骤中）；它不会为签名操作重置。
例如，假设我们使用Master Key” 0x0102030405060060090090a0b0c0d0e0f00 “ 在客户端上Sealing消息” jCIFS “（十六进制” 0x6a43494653 “）。与前面的示例一样，我们使用未减弱的Master Key生成客户端签名Key（” 0xf7f97a82ec390f9c903dac4f6aceb132 “）。我们还需要生成客户SealingKey；我们将假定已经Negotiate了40位弱化。我们将弱化的Master Key（” 0x0102030405 “）与客户端到服务器的Sealing常数连接起来，并应用MD5产生客户端SealingKey（” 0x6f0d9953503333cbe499cd1914fe9ee “）。以下过程用于Sealing消息：
1. RC4密码使用我们的客户SealingKey（” 0x6f0d99535033951cbe499cd1914fe9ee “）初始化。
1. 我们的消息通过RC4密码传递，并产生密文” 0xcf0eb0a939 “。这是Sealing消息。
1. 获得序列号。由于这是第一个签名，因此序列号为零（” 0x00000000 “）。
<li>序列号与消息串联在一起：<br>
0x000000006a43494653使用客户端签名Key（” 0xf7f97a82ec390f9c903dac4f6aceb132 “）应用HMAC-MD5 。结果是16字节的值” 0x0a003602317a759a720dc9c7a2a95257 “。</li>
1. 该值的前八个字节通过Sealing密码，得到的密文为” 0x884b14809e53bfe7 “。
<li>将版本标记与结果和序列号连接起来以形成最终签名，该最终签名被放置在安全性尾部缓冲区中：<br>
0x01000000884b14809e53bfe700000000整个Sealing结构的十六进制转储为：0xcf0eb0a93901000000884b14809e53bfe700000000</li>


## 会话安全主题（Miscellaneous Session Security Topics）

还有其他几个会话安全性主题，这些主题实际上并不适合其他任何地方：
- 数据报的签名和Sealing
- “虚拟”的签名
### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E6%8A%A5%E7%AD%BE%E5%90%8D%E5%92%8CSealing"></a>数据报签名和Sealing

在建立数据报上下文时使用此方法（由数据报身份验证握手和”Negotiate Datagram Style”Flags的存在指示）。关于数据报会话安全性的语义有些不同；首次调用SSPI InitializeSecurityContext函数之后（即，在与服务器进行任何通信之前），签名可以立即在客户端上开始。这意味着需要预先安排的签名和Sealing方案（因为可以在与服务器Negotiate任何选项之前创建签名）。数据报会话安全性基于具有密钥交换的40位Lan Manager Session Key NTLM1（尽管可能有一些方法可以通过注册表预先确定更强大的方案）。

在数据报模式下，序列号不递增；它固定为零，每个签名都反映了这一点。同样，每次签名或Sealing操作都会重置RC4Key流。这很重要，因为消息可能容易受到已知的明文攻击。

### <a class="reference-link" name="%E2%80%9C%E8%99%9A%E6%8B%9F%E2%80%9D%E7%AD%BE%E5%90%8D"></a>“虚拟”签名

如果初始化SSPI上下文而未指定对消息完整性的支持，则使用此方法。如果建立了”始终NegotiateNegotiate” NTLMFlags，则对MakeSignature的调用将成功，并返回常量” signature”：

0x01000000000000000000000000000000

对EncryptMessage的调用通常会成功（包括安全性尾部缓冲区中的”真实”签名）。如果未Negotiate”Negotiate始终签名”，则签名和Sealing均将失败。



## 附录A：链接和参考

请注意，由于Web具有高度动态性和瞬态性，因此这些功能可能可用或可能不可用。

jCIFS项目主页<br>[http://jcifs.samba.org/](http://jcifs.samba.org/)<br>
jCIFS是CIFS / SMB的开源Java实现。本文中提供的信息用作jCIFS NTLM身份验证实现的基础。jCIFS为NTLM HTTP身份验证方案的客户端和服务器端以及非协议特定的NTLM实用程序类提供支持。<br>
Samba主页<br>[http://www.samba.org/](http://www.samba.org/)<br>
Samba是一个开源CIFS / SMB服务器和客户端。实现NTLM身份验证和会话安全性，以及本文档大部分内容的参考。<br>
实施CIFS：通用Internet文件系统<br>[http://ubiqx.org/cifs/](http://ubiqx.org/cifs/)<br>
Christopher R. Hertel撰写的，内容丰富的在线图书。与该讨论特别相关的是有关 身份验证的部分。<br>
Open Group ActiveX核心技术参考（第11章，” NTLM”）<br>[http://www.opengroup.org/comsource/techref2/NCH1222X.HTM](http://www.opengroup.org/comsource/techref2/NCH1222X.HTM)<br>
与NTLM上”官方”参考最接近的东西。不幸的是，它还很旧并且不够准确。<br>
安全支持提供者界面<br>[http://www.microsoft.com/windows2000/techinfo/howitworks/security/sspi2000.asp](http://www.microsoft.com/windows2000/techinfo/howitworks/security/sspi2000.asp)<br>
白皮书，讨论使用SSPI进行应用程序开发。<br>
HTTP的NTLM身份验证方案<br>[http://www.innovation.ch/java/ntlm.html](http://www.innovation.ch/java/ntlm.html)<br>
有关NTLM HTTP身份验证机制的内容丰富的讨论。<br>
Squid NTLM认证项目<br>[http://squid.sourceforge.net/ntlm/](http://squid.sourceforge.net/ntlm/)<br>
为Squid代理服务器提供NTLM HTTP身份验证的项目。<br>
Jakarta Commons HttpClient<br>[http://jakarta.apache.org/commons/httpclient/](http://jakarta.apache.org/commons/httpclient/)<br>
一个开放源Java HTTP客户端，它提供对NTLM HTTP身份验证方案的支持。<br>
GNU加密项目<br>[http://www.gnu.org/software/gnu-crypto/](http://www.gnu.org/software/gnu-crypto/)<br>
一个开放源代码的Java密码学扩展提供程序，提供了MD4消息摘要算法的实现。<br>
RFC 1320-MD4消息摘要算法<br>[http://www.ietf.org/rfc/rfc1320.txt](http://www.ietf.org/rfc/rfc1320.txt)<br>
MD4摘要的规范和参考实现（用于计算NTLM密码哈希）。<br>
RFC 1321-MD5消息摘要算法<br>[http://www.ietf.org/rfc/rfc1321.txt](http://www.ietf.org/rfc/rfc1321.txt)<br>
MD5摘要的规范和参考实现（用于计算NTLM2会话响应）。<br>
RFC 2104-HMAC：消息身份验证的键哈希<br>[http://www.ietf.org/rfc/rfc2104.txt](http://www.ietf.org/rfc/rfc2104.txt)<br>
HMAC-MD5算法的规范和参考实现（用于NTLMv2 / LMv2响应的计算）。<br>
如何启用NTLM 2身份验证<br>[http://support.microsoft.com/default.aspx?scid=KB;zh-cn;239869](http://support.microsoft.com/default.aspx?scid=KB;zh-cn;239869)<br>
描述了如何启用NTLMv2身份验证的Negotiate并强制执行NTLM安全Flags。<br>
Microsoft SSPI功能文档<br>[http://windowssdk.msdn.microsoft.com/en-us/library/ms717571.aspx#sspi_functions](http://windowssdk.msdn.microsoft.com/en-us/library/ms717571.aspx#sspi_functions)<br>
概述了安全支持提供程序接口（SSPI）和相关功能。



## 附录B：NTLM的应用协议用法

本节研究了Microsoft的某些网络协议实现中NTLM身份验证的使用。

### <a class="reference-link" name="NTLM%20HTTP%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81"></a>NTLM HTTP身份验证

Microsoft已经为HTTP建立了专有的” NTLM”身份验证方案，以向IIS Web服务器提供集成身份验证。此身份验证机制允许客户端使用其Windows凭据访问资源，通常用于公司环境中，以向Intranet站点提供单点登录功能。从历史上看，Internet Explorer仅支持NTLM身份验证。但是，最近，已经向其他各种用户代理添加了支持。

NTLM HTTP身份验证机制的工作方式如下：
<li>客户端从服务器请求受保护的资源：<br>
GET /index.html HTTP / 1.1</li>
<li>服务器以401状态响应，指示客户端必须进行身份验证。通过” WWW-Authenticate “标头将” NTLM”表示为受支持的身份验证机制。通常，服务器此时会关闭连接：<br>
HTTP / 1.1 401未经授权的<br>
WWW身份验证：NTLM<br>
连接：关闭<br>
请注意，如果Internet Explorer是第一个提供的机制，它将仅选择NTLM。这与RFC 2616不一致，RFC 2616指出客户端必须选择支持最强的身份验证方案。</li>
<li>客户端使用包含Type 1消息参数的” Authorization “标头重新提交请求。Type 1消息经过Base-64编码以进行传输。从这一点开始，连接保持打开状态。关闭连接需要重新验证后续请求。这意味着服务器和客户端必须通过HTTP 1.0样式的” Keep-Alive”标头或HTTP 1.1（默认情况下采用持久连接）来支持持久连接。相关的请求标头显示如下（下面的” Authorization “标头中的换行符仅用于显示目的，在实际消息中不存在）：<br>
GET /index.html HTTP / 1.1<br>
授权：NTLM TlRMTVNTUAABAAAABzIAAAYABgArAAAACwALACAAAABXT1<br>
JLU1RBVElPTkRPTUFJTg ==</li>
<li>服务器以401状态答复，该状态在” WWW-Authenticate “标头中包含Type 2消息（再次，以Base-64编码）。如下所示（” WWW-Authenticate “标头中的换行符仅出于编辑目的，在实际标头中不存在）。<br>
HTTP / 1.1 401未授权<br>
WWW验证：NTLM TlRMTVNTUAACAAAADAAMADAAAAABAoEAASNFZ4mrze8<br>
AAAAAAAAAAGIAYgA8AAAARABPAE0AQQBJAE4AAgAMAEQATwBNAEEASQBOAAEADABTA<br>
EUAUgBWAEUAUgAEABQAZABvAG0AYQBpAG4ALgBjAG8AbQADACIAcwBlAHIAdgBlAHI<br>
ALgBkAG8AbQBhAGkAbgAuAGMAbwBtAAAAAAA =</li>
<li>客户端通过使用包含包含Base-64编码的Type 3消息的” Authorization “标头重新提交请求来响应Type 2消息（同样，下面的” Authorization “标头中的换行符仅用于显示目的）：<br>
GET /index.html HTTP / 1.1<br>
授权：NTLM TlRMTVNTUAADAAAAGAAYAGoAAAAYABgAggAAAAwADABAAA<br>
AACAAIAEwAAAAWABYAVAAAAAAAAACaAAAAAQIAAEQATwBNAEEASQBOAHUAcwBlAHIA<br>
VwBPAFIASwBTAFQAQQBUAEkATwBOAMM3zVy9RPyXgqZnr21CfG3mfCDC0 + d8ViWpjB<br>
wx6BhHRmspst9GgPOZWPuMITqcxg ==</li>
<li>最后，服务器验证客户端的Type 3消息中的响应，并允许访问资源。<br>
HTTP / 1.1 200 OK</li>
此方案与大多数”常规” HTTP身份验证机制不同，因为通过身份验证的连接发出的后续请求本身不会被身份验证；NTLM是面向连接的，而不是面向请求的。因此，对” /index.html “ 的第二个请求将不携带任何身份验证信息，并且服务器将不请求任何身份验证信息。如果服务器检测到与客户端的连接已断开，则对” /index.html “ 的请求将导致服务器重新启动NTLM握手。

上面的一个显着例外是客户端在提交POST请求时的行为（通常在客户端向服务器发送表单数据时使用）。如果客户端确定服务器不是本地主机，则客户端将通过活动连接启动POST请求的重新认证。客户端将首先提交一个空的POST请求，并在” Authorization “标头中带有Type 1消息。服务器以Type 2消息作为响应（如上所示，在” WWW-Authenticate “标头中）。然后，客户端使用Type 3消息重新提交POST，并随请求发送表单数据。

NTLM HTTP机制也可以用于HTTP代理身份验证。该过程类似，除了：
- 服务器使用407响应代码（指示需要进行代理身份验证）而不是401。
- 客户端的1类和3类消息是在” 代理授权 “请求标头中发送的，而不是在” 授权 “标头中发送的。
- 服务器的Type 2质询在” Proxy-Authenticate “响应头中发送（而不是” WWW-Authenticate “）。
在Windows 2000中，Microsoft引入了”Negotiate” HTTP身份验证机制。虽然其主要目的是提供一种通过Kerberos通过Active Directory验证用户身份的方法，但它与NTLM方案向后兼容。当在”传统”模式下使用Negotiate机制时，在客户端和服务器之间传递的标头是相同的，只是将”Negotiate”（而不是” NTLM”）指定为机制名称。

### <a class="reference-link" name="NTLM%20POP3%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81"></a>NTLM POP3身份验证

Microsoft的Exchange服务器为POP3协议提供了NTLM身份验证机制。这是RFC 1734中记录的与POP3 AUTH命令 一起使用的专有扩展 。在客户端，Outlook和Outlook Express支持此机制，称为”安全密码身份验证”。

POP3 NTLM身份验证握手在POP3”授权”状态期间发生，其工作方式如下：
<li>客户端可以通过发送不带参数的AUTH命令来请求支持的身份验证机制的列表：<br>
AUTH</li>
<li>服务器以成功消息响应，然后是受支持机制的列表；此列表应包含” NTLM “，并以包含单个句点（” 。 “）的行结尾。<br>
+OK The operation completed successfully.<br>
NTLM<br>
.</li>
<li>客户端通过发送一个将NTLM指定为身份验证机制的AUTH命令来启动NTLM身份验证：<br>
AUTH NTLM</li>
<li>服务器将显示一条成功消息，如下所示。注意，” + “和” OK “ 之间有一个空格；RFC 1734指出服务器应以质询进行答复，但是NTLM要求来自客户端的Type 1消息。因此，服务器发送”非challenge”消息，基本上是消息” OK “。<br>
+OK</li>
<li>然后，客户端发送Type 1消息，以Base-64编码进行传输：<br>
TlRMTVNTUAABAAAABzIAAAYABgArAAAACwALACAAAABXT1JLU1RBVElPTkRPTUFJTg ==</li>
<li>服务器回复Type 2质询消息（再次，以Base-64编码）。它以RFC 1734指定的质询格式发送（” + “，后跟一个空格，后跟质询消息）。如下所示；换行符是出于编辑目的，不出现在服务器的答复中：
<ul>
<li>TlRMTVNTUAACAAAADAAMADAAAAABAoEAASNFZ4mrze8AAAAAAAAAAGIAYgA8AAAA<br>
RABPAE0AQQBJAE4AAgAMAEQATwBNAEEASQBOAAEADABTAEUAUgBWAEUAUgAEABQAZA<br>
BvAG0AYQBpAG4ALgBjAG8AbQADACIAcwBlAHIAdgBlAHIALgBkAG8AbQBhAGkAbgAu<br>
AGMAbwBtAAAAAAA =</li>
</ul>
</li>
<li>客户端计算并发送Base-64编码的Type 3响应（下面的换行符仅用于显示目的）：<br>
TlRMTVNTUAADAAAAGAAYAGoAAAAYABgAggAAAAwADABAAAAACAAIAEwAAAAWABYAVA<br>
AAAAAAAACaAAAAAQIAAEQATwBNAEEASQBOAHUAcwBlAHIAVwBPAFIASwBTAFQAQQBU<br>
AEkATwBOAMM3zVy9RPyXgqZnr21CfG3mfCDC0 + d8ViWpjBwx6BhHRmspst9GgPOZWP<br>
uMITqcxg ==</li>
<li>服务器验证响应并指示认证结果：<br>
+OK User successfully logged on</li>
成功进行身份验证后，POP3会话进入”事务”状态，从而允许客户端检索消息。

### <a class="reference-link" name="NTLM%20IMAP%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81"></a>NTLM IMAP身份验证

Exchange提供了一种IMAP身份验证机制，其形式类似于前面讨论的POP3机制。RFC 1730中记录了IMAP身份验证 ；NTLM机制是Exchange提供的专有扩展，并由Outlook客户端家族支持。

握手序列类似于POP3机制：
<li>服务器可以在能力响应中指示对NTLM身份验证机制的支持。连接到IMAP服务器后，客户端将请求服务器功能列表：<br>
0000 CAPABILITY</li>
<li>服务器以支持的功能列表作为响应；服务器回复中字符串” AUTH = NTLM “ 的存在指示了NTLM身份验证扩展名：
<ul>
<li>CAPABILITY IMAP4 IMAP4rev1 IDLE LITERAL+ AUTH=NTLM<br>
0000 OK CAPABILITY completed.</li>
</ul>
</li>
<li>客户端通过发送 将NTLM指定为身份验证机制的AUTHENTICATE命令来启动NTLM身份验证：<br>
0001授权NTLM</li>
<li>服务器以一个空的质询作为响应，该质询仅由” + “组成：<br>
+</li>
<li>然后，客户端发送Type 1消息，以Base-64编码进行传输：<br>
TlRMTVNTUAABAAAABzIAAAYABgArAAAACwALACAAAABXT1JLU1RBVElPTkRPTUFJTg ==</li>
<li>服务器回复Type 2质询消息（再次，以Base-64编码）。它以RFC 1730指定的质询格式发送（” + “，后跟一个空格，后跟质询消息）。如下所示；换行符是出于编辑目的，不出现在服务器的答复中：
<ul>
<li>TlRMTVNTUAACAAAADAAMADAAAAABAoEAASNFZ4mrze8AAAAAAAAAAGIAYgA8AAAA<br>
RABPAE0AQQBJAE4AAgAMAEQATwBNAEEASQBOAAEADABTAEUAUgBWAEUAUgAEABQAZA<br>
BvAG0AYQBpAG4ALgBjAG8AbQADACIAcwBlAHIAdgBlAHIALgBkAG8AbQBhAGkAbgAu<br>
AGMAbwBtAAAAAAA =</li>
</ul>
</li>
<li>客户端计算并发送Base-64编码的Type 3响应（下面的换行符仅用于显示目的）：<br>
TlRMTVNTUAADAAAAGAAYAGoAAAAYABgAggAAAAwADABAAAAACAAIAEwAAAAWABYAVA<br>
AAAAAAAACaAAAAAQIAAEQATwBNAEEASQBOAHUAcwBlAHIAVwBPAFIASwBTAFQAQQBU<br>
AEkATwBOAMM3zVy9RPyXgqZnr21CfG3mfCDC0 + d8ViWpjBwx6BhHRmspst9GgPOZWP<br>
uMITqcxg ==</li>
<li>服务器验证响应并指示认证结果：<br>
0001 OK AUTHENTICATE NTLM completed.</li><li>TlRMTVNTUAACAAAADAAMADAAAAABAoEAASNFZ4mrze8AAAAAAAAAAGIAYgA8AAAA<br>
RABPAE0AQQBJAE4AAgAMAEQATwBNAEEASQBOAAEADABTAEUAUgBWAEUAUgAEABQAZA<br>
BvAG0AYQBpAG4ALgBjAG8AbQADACIAcwBlAHIAdgBlAHIALgBkAG8AbQBhAGkAbgAu<br>
AGMAbwBtAAAAAAA =</li>
身份验证完成后，IMAP会话将进入身份验证状态。

### <a class="reference-link" name="NTLM%20SMTP%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81"></a>NTLM SMTP身份验证

除了为POP3和IMAP提供的NTLM身份验证机制外，Exchange还为SMTP协议提供了类似的功能。这样可以对发送外发邮件的用户进行NTLM身份验证。这是与SMTP AUTH命令一起使用的专有扩展（在 RFC 2554中记录）。

SMTP NTLM身份验证握手的操作如下：
<li>服务器可以在EHLO答复中指示支持NTLM作为身份验证机制。连接到SMTP服务器后，客户端将发送初始EHLO消息：<br>
EHLO client.example.com</li>
<li>服务器以支持的扩展列表进行响应。NTLM身份验证扩展由其在AUTH机制列表中的存在指示，如下所示。请注意，AUTH 列表发送了两次（一次带有” = “，一次没有）。显然在RFC草案中指定了” AUTH = “形式。发送两种表格都可以确保支持针对该草案实施的客户。<br>
250-server.example.com Hello [10.10.2.20]<br>
250-HELP<br>
250-AUTH LOGIN NTLM<br>
250-AUTH=LOGIN NTLM<br>
250 SIZE 10240000</li>
1. 客户端通过发送一个AUTH 命令来启动NTLM身份验证，该命令将NTLM指定为身份验证机制，并提供Base-64编码的Type 1消息作为参数：AUTH NTLM TlRMTVNTUAABAAAABzIAAAYABgArAAAACwALACAAAABXT1JLU1RBVElPTkRPTUFJTg ==
根据RFC 2554，客户端可以选择不发送初始响应参数（而是仅发送” AUTH NTLM “并等待空服务器质询，然后以Type 1消息答复）。但是，在针对Exchange测试时，这似乎无法正常工作。
<li>服务器回复334响应，其中包含Type 2质询消息（同样是Base-64编码）。如下所示；换行符是出于编辑目的，不出现在服务器的答复中：<br>
334 TlRMTVNTUAACAAAADAAMADAAAAABAoEAASNFZ4mrze8AAAAAAAAAAGIAYgA8AAAA<br>
RABPAE0AQQBJAE4AAgAMAEQATwBNAEEASQBOAAEADABTAEUAUgBWAEUAUgAEABQAZA<br>
BvAG0AYQBpAG4ALgBjAG8AbQADACIAcwBlAHIAdgBlAHIALgBkAG8AbQBhAGkAbgAu<br>
AGMAbwBtAAAAAAA =</li>
<li>客户端计算并发送Base-64编码的Type 3响应（下面的换行符仅用于显示目的）：<br>
TlRMTVNTUAADAAAAGAAYAGoAAAAYABgAggAAAAwADABAAAAACAAIAEwAAAAWABYAVA<br>
AAAAAAAACaAAAAAQIAAEQATwBNAEEASQBOAHUAcwBlAHIAVwBPAFIASwBTAFQAQQBU<br>
AEkATwBOAMM3zVy9RPyXgqZnr21CfG3mfCDC0 + d8ViWpjBwx6BhHRmspst9GgPOZWP<br>
uMITqcxg ==</li>
1. 服务器验证响应并指示认证结果：235 NTLM authentication successful.
验证后，客户端可以正常发送消息。



## 附录C：NTLMSSP操作分解示例

此部分内容较多，后续持续更新于Github。
