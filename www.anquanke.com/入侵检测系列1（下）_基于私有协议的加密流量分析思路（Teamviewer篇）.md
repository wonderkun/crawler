> 原文链接: https://www.anquanke.com//post/id/226531 


# 入侵检测系列1（下）：基于私有协议的加密流量分析思路（Teamviewer篇）


                                阅读量   
                                **234764**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01ae72fe8389206899.jpg)](https://p2.ssl.qhimg.com/t01ae72fe8389206899.jpg)



## 写在前面

在1(上)篇，我主要从私有协议的分析方式开始，通过抓取TeamViewer包观察其流量行为，从日志中获取协议的各个行为入手，对协议各个流程进行分解。而在1(中)篇，我继续对协议流程进行分解，包括对登陆行为分析(这里指本机连接至Server)，发出连接请求，成功连接，两台机器间的通讯和一些其他操作进行解析，并在最后附上协议流程的时序图。

详情见：

入侵检测系列1(上):基于私有协议的加密流量分析思路(Teamviewer篇)

[https://www.anquanke.com/post/id/223106](https://www.anquanke.com/post/id/223106)

入侵检测系列1(中):基于私有协议的加密流量分析思路(Teamviewer篇)

[https://www.anquanke.com/post/id/225394](https://www.anquanke.com/post/id/225394)

本文为入侵检测系列1的最后一篇文章，在此，我将详细叙述TeamViewer的加密与身份验证内容模块。



## 3 TeamViewer 的加密与身份认证

首先我们来看看他的整个加密与身份认证流程：

[![](https://p1.ssl.qhimg.com/t0173c94c0e6829784d.png)](https://p1.ssl.qhimg.com/t0173c94c0e6829784d.png)

### <a class="reference-link" name="3.1%20%E5%8A%A0%E5%AF%86%E6%B5%81%E9%87%8F"></a>3.1 加密流量

TeamViewer流量使用RSA公钥/私钥交换和AES（256位）会话进行加密保护。这项技术在https/SSL中有着可比性，在当今的安全标准中被认为是最安全的。由于私钥永远不会离开客户端计算机，所以整个过程可以确保互连的PC（包括TeamViewer路由服务器）都无法解密流量。

### <a class="reference-link" name="3.2%20%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81"></a>3.2 身份验证

每台TeamViewer客户端都使用了主集群(master cluster )的公钥，因此可以对主集群的消息进行加密，并检查由它签名的消息。PKI（Public Key Infrastructure，公钥基础设施）有效地防止了中间人攻击，尽管加密了密码，但密码从不直接发送，而是通过响应返回，并且只保存在本地计算机上。在身份验证过程中，由于使用了安全远程密码（SRP）协议，因此不会直接传输密码。本地计算机上只存储一个密码验证器。在身份验证过程中，由于使用了安全远程密码（SRP）协议，因此不会直接传输密码，而是在本地PC上存储了码验证器。

### <a class="reference-link" name="3.3%20%E8%BF%9E%E6%8E%A5%E8%BF%87%E7%A8%8B"></a>3.3 连接过程

完整连接过程如下：

[![](https://p1.ssl.qhimg.com/t01b9c19155b91d7e54.png)](https://p1.ssl.qhimg.com/t01b9c19155b91d7e54.png)

**CMD_RequestEncryption**

默认情况下双方会使用master server在**RequestRoute2** 响应中发出的公钥来发起对对方的加密信息邀请 。这个加密连接的过程会使用 **CMD_RequestEncryption**，两端路由都是对等连接的。这个连接中包含了1个加密过的session key(AES/RC4，算法基于使用版本而定)还有对方的公钥匙，本机用于身份认证的私钥。在 **RequestRoute2** 响应里，包含一个对方TeamViewer传过来的公钥，这个对方的公钥还包含本机TeamViewer的地址信息，但却不做任何身份验证，没有使用加密签名验证之类的。在这种情况下，攻击者可以选择自己的密钥去替换RSA密钥由此发起中间人攻击。所以，在每个新的连接上执行一个新的**RequestRoute2**请求，会使得攻击者轻易使用中间人攻击Master的响应，轻而易举的替换掉公钥。

**CMD_RequestNoEncryption**

在端对端协商失败的情况下，协商双方的其中一个客户端（通常是无法解密对等流量的客户端）将发送一个**CMD_RequestNoEncryption**，该命令将关闭会话的所有对等加密。关闭加密这项操作是没有任何提示的，用户通讯过程不会受到明显的影响。攻击者也可能会插入这样的命令来禁用会话的加密。

我还注意到整个加密过程是通过异步协商和确认的——加密前被确认的发生过的任何通信数据会被自动清除，加密后发生的通讯内容都被自动加密。在确认加密之前，通常会有多个对等数据包进行通信，在此我大胆猜测：无限期地延迟**RequestEncryption**命令会导致连接和身份验证成功，而无需任何加密步骤。有兴趣的小伙伴可以自行测试。

### <a class="reference-link" name="3.4%20%E8%BA%AB%E4%BB%BD%E8%AE%A4%E8%AF%81%E6%96%B9%E5%BC%8F"></a>3.4 身份认证方式

身份验证是端对端进行的，默认情况下使用6位数字字母密码，在16年版本中为4位数字密码。基于TeamViewer的密码保护机制（TeamViewer QuickSupport），它会生成会话密码（一次性密码）。在本机重新启动TeamViewer后，将生成一个新的会话密码，也就是说对方只能在接到邀请的情况下连接到客户的计算机。无人值守远程支持模式时，则需要设置一个单独的固定密码，以确保对计算机的访问安全。

**Brute-Force Protection**

Teamviewer采用了一种叫做暴力保护的方式(**Brute-Force Protection**)，即采用回退计时器(back-off timer)的方法，该计时器在后续的错误身份验证后会增加等待的时间。这么做是防止攻击者通过暴力猜解的方式获取密码。根据官方数据，24次尝试最多可以延迟达到17小时(图和数据源自官网)。只有在成功输入正确的密码后才会重置延迟时长。

[![](https://p4.ssl.qhimg.com/t0148c2975920cc1c38.png)](https://p4.ssl.qhimg.com/t0148c2975920cc1c38.png)

### <a class="reference-link" name="3.5%20%E8%BA%AB%E4%BB%BD%E8%AE%A4%E8%AF%81%E8%BF%87%E7%A8%8B"></a>3.5 身份认证过程

理想状态下的认证过程：

[![](https://p2.ssl.qhimg.com/t014720b067feaefa91.png)](https://p2.ssl.qhimg.com/t014720b067feaefa91.png)

该流程的Pcap截图：

[![](https://p0.ssl.qhimg.com/t01426d61c82a3e0849.png)](https://p0.ssl.qhimg.com/t01426d61c82a3e0849.png)

**Data4**

如图所示，端对端发送的**Data4**包在发送**ConfirmEncryption** 之后被加密，但加密过程是异步的，而且很有可能在几个**Data4**包交换之后还未完成加密。除了**Data4**以外，少部分情况下还能见到**Data3**。4和3的区别是**Data4**支持加密和明文的负载，**Data3**还区分**Data3** 和**Data3_Encrypted**。

如果由于过多的身份验证尝试而激活暴力保护，远程客户端将用错误代码响应身份验证消息，并且可以重试另一个指示身份验证前秒数的参数，否则，将返回一个代码，指示身份验证是否成功。最后，**Data4**消息也使用zlib流进行压缩（在加密之前），但只在初始版本握手之后从消息开始，并且第一个**握手**（ID 49）对等消息已经发送。



## 4 暴力猜解

用户激活**Brute-Force Protection**时，远程客户端会返回一个身份验证消息的错误代码，并且可以重试另一个验证码，然后返回结果。**Data4**只在初始版本握手之后从消息开始使用zlib流进行压缩（在加密之前），并且完成发送第一个握手(ID49).

在传输密码的过程中，对Teamviewer进行中间人攻击和对其密码进行暴力破解其实是不难做到的，因为密码中可能会包含弱口令或者其它什么意想不到的缺陷/漏洞。在研究过程中，我发现了这么个Exp([https://github.com/AleWong/teamviewerExp/blob/main/tv3.py),它通过使用ipfwipfw](https://github.com/AleWong/teamviewerExp/blob/main/tv3.py),%E5%AE%83%E9%80%9A%E8%BF%87%E4%BD%BF%E7%94%A8ipfwipfw) divert套接字转移TCP通信量，修改并重新注入它。利用该漏洞可以处理来自Mac电脑或通过Mac电脑路由的任何流量(该Exp的编写者如是说)。该漏洞攻击通过执行此处描述的两种攻击来工作。它通过修改**MasterResponse**修改交换目标的公钥。我最初这样做的目的是限制加密的流量，在运行中解密和重新加密，但是我注意到加密被放弃使用了**CMD_RequestNoEncryption**，当**CMD_RequestEncryption**的会话密钥无法解密时不需要这样做。由于端对端之间的通信是完全透明的，在加密被悄悄地放弃之后，很容易找到身份验证消息，并根据MD5（challenge | passcode）快速强行将9999个可能的密码离线从而输出明文密码。

在爆破次数到达一定数量时，我收到一个以前从未见过的错误：**NOROUTE_ExcessiveUse**（请注意，拼写与**NOROUTE_excessive usd**略有不同，后者表示来自单个ID的请求过多）。假设这个黑名单是基于相同源IP地址。但在使用Tor路由请求之后，我发现黑名单实际上是基于受害者的客户机ID。这种行为本身就是一种DDOS。只需反复请求一个到系统的路由，最终会将其打崩。我观察到，目的地黑名单只能坚持大概15到30分钟，因此攻击者可以在不到24小时内成功执行在线暴力。



## 5 TeamViewer漏洞:CVE-2019-18988

在3 加密与身份认证中，我提到TeamViewer存储用AES-128-CBC加密的用户密码，它们在Windows注册表中的键为`0602000000a400005253413100040000`和`0100010067244F436E6762F25EA8D704`。如果密码在任何地方都可以重复使用，则存在提权。如果PC的RDP权限但已安装TeamViewer，则可以使用TeamViewer进行远程访问。TeamViewer还允许复制数据或计划任务以通过其服务运行，该服务的运行方式为`NT AUTHORITY\SYSTEM`，因此低特权用户可以立即转到`SYSTEM`一个`.bat`文件。这个漏洞被分配了CVE，编号为CVE-2019-18988。

TeamViewer注册表项是有备份的。它在备份中有类似OptionsPasswordAES或SecurityPasswordAES。如果导入注册表设置或将它部署在.msi中，那么这么做的公司他们所安装使用的所有TeamViewer都可以使用相同的密码。也就是说，所有TeamViewer之间都有一个共享密钥，该密钥可以通过涉及AES的注册密钥来备份声明。但事实证明，OptionsPasswordAESreg会防止未经授权的人员进入菜单，不过这里又可以更改设置。在不知道密码的的情况下，挖到这个漏洞的作者从nirsoft下载BulletPassView并运行它，它以纯文本形式返回了一个密码。这时返回“选项”页面并查看菜单的“安全性”部分，然而预定义的无人参与访问密码显示在BulletPassView中为星号。后来作者通过作弊引擎发现选项密码以明文形式存储在内存中的字节080088和之间000000000000。并且这段内存中的明文凭证已经被分配了CVE-2018-14333。

```
=================================================
"ServerPasswordAES"=hex:88,44,d7,0a,b2,96,2a,3d,63,16,3c,ff,e4,15,04,fb
=================================================
Takes 8844d70ab2962a3d63163cffe41504fb into xmm0
Takes 5B659253E5E873D26723B7D5EAC06E3B into xmm1
pxor xmm0, xmm1
movdqa xmmword ptr ds:[eax],xmm0
[eax] = D3214559577E59EF04358B2A0ED56AC0

movdqa xmm1,xmmword ptr ds:[esi]     | [esi] = 25C8C8BD4298BB32A57EECBDBD045BBB
movdqa xmm0,xmmword ptr ds:[eax]     | [eax] = D3214559577E59EF04358B2A0ED56AC0
aesdec xmm0,xmm1                     | One round of an AES decryption, using Equivalent Inverse Cipher, 128-bit data (state) from xmm1 with 128-bit round key from xmm2/m128; store the result in xmm1.
movdqa xmmword ptr ds:[eax],xmm0     | [eax] = 6F AA 98 76 DE 11 7D 8D 7E B6 EE 61 2D 3D 15 52
movdqa xmm1,xmmword ptr ds:[esi+10]  | [esi+10]=[008FDE10]=79 DC 78 A6 67 50 73 8F E7 E6 57 8F 18 7A B7 06
add esi,20                           |
dec ecx                              | ecx = 3
aesdec xmm0,xmm1                     | do the actual decryption
movdqa xmmword ptr ds:[eax],xmm0     | [eax]=[008FDC90]=E3 58 26 46 A7 37 12 40 85 1C C0 43 7D 1F 1E 30

Three more rounds of aesdec then
aesdeclast xmm0, xmm1 .| Last round of AES decryption, using Equivalent Inverse Cipher, 128-bit data (state) from xmm2 with a 128-bit round key from xmm3/m128; store the result in xmm1. 

008FDC90  01 00 01 00 67 24 4F 43 6E 67 62 F2 5E A8 D7 04  ....g$OCngbò^¨×.
```

这部分代码从注册表中获取字节ServerPasswordAES，进入xmm2的动作是它们的关键0602000000a400005253413100040000。IV是ServerPasswordAES，也就是密钥和空IV的解密字节。在这种情况下，对于IVSecurityPasswordAES是0100010067244F436E6762F25EA8D704。只要SecurityPasswordExported有可用的密钥，即可立即使用TeamViewer版本7和最新版本的Teamviewer 14 。



## 6 总结

出于安全性考虑，我在此建议大家不要在公用网络或者默认密码设置下使用TeamViewer。TeamViewer确实支持将密码强度增加到可配置的长度，并使用字母数字密码，但是临时用户不太可能会更改此设置。另外，TeamViewer中存在严重的攻击面，需要进行更多分析，例如客户端与服务器之间未经身份验证的纯文本通信（在客户端支持并解析了100多个命令），以及许多对等命令是通过网关服务器的路由的。在不知道是TeamViewer的情况下这些流量很容易被当成噪音被忽略；如果不进行仔细分析，几乎不可能发现通信中出现的专用IP地址的含义，因为不知道其与TeamViewer的关系。

关于TeamViewer的私有协议分析至此告一段落，谢谢安全客平台和各位读者的支持！



## 7 参考资料

[https://whynotsecurity.com/blog/teamviewer/](https://whynotsecurity.com/blog/teamviewer/)

[https://www.teamviewer.com/en/features/end-to-end-security/](https://www.teamviewer.com/en/features/end-to-end-security/)

[https://www.easemob.com/news/3983](https://www.easemob.com/news/3983)
