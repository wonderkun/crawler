> 原文链接: https://www.anquanke.com//post/id/86140 


# 【技术分享】OpenSSL握手重协商过程中存在漏洞可导致拒绝服务


                                阅读量   
                                **133625**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：mcafee.com
                                <br>原文地址：[https://securingtomorrow.mcafee.com/mcafee-labs/vulnerable-openssl-handshake-renegotiation-can-trigger-denial-service/](https://securingtomorrow.mcafee.com/mcafee-labs/vulnerable-openssl-handshake-renegotiation-can-trigger-denial-service/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p0.ssl.qhimg.com/t01cd2278e81edf92b5.jpg)](https://p0.ssl.qhimg.com/t01cd2278e81edf92b5.jpg)

翻译：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**预估稿费：100RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

OpenSSL是一个非常流行的通用加密库，可为Web认证服务提供SSL/TLS协议的具体实现。最近以来，人们发现OpenSSL中存在几个漏洞。我们写过几篇文章分析这些漏洞，包括“[**CVE-2017-3731：截断数据包可导致OpenSSL拒绝服务**](https://securingtomorrow.mcafee.com/mcafee-labs/analyzing-cve-2017-3731-truncated-packets-can-cause-denial-service-openssl/)”、“[**SSL死亡警告（CVE-2016-8610）可导致OpenSSL服务器拒绝服务**](https://securingtomorrow.mcafee.com/mcafee-labs/ssl-death-alert-cve-2016-8610-can-cause-denial-of-service-to-openssl-servers/)”等。今天，我们将要分析的是CVE-2017-3733这个高危级漏洞，即Encrypt-Then-MAC（加密后消息认证码）重新协商崩溃漏洞，可导致OpenSSL拒绝服务。

在使用SSL/TLS协议加密数据之前，OpenSSL会先发起Handshake协议（握手）以及ChangeCipherSpec协议（更改密钥规格）的处理流程。

在Handshake阶段，客户端和服务器共同协商使用哪种加密算法。一旦协商完成，客户端和服务器会各自向对方发送一个ChangedCipherSpec消息，之后通信流量会使用协商好的算法进行加密。

在SSL/TLS中，加密数据会与MAC（Message Authentication Code，消息认证码）一起，使用以下两种方式进行发送：

1、MAC-then-encrypt（消息认证码后加密）：这种方式会先计算纯文本的MAC，并将其与纯文本连接，再使用加密算法生成最终的密文。

2、Encrypt-then-MAC（加密后消息认证码）：这种方式会先加密纯文本，并将已加密纯文本的MAC附加在尾部，形成最终的密文。

如果ClientHello消息没有包含Encrypt-Then-Mac扩展，那么默认情况下使用的是MAC-then-encrypt模式。如果ClientHello消息包含Encrypt-Then-Mac扩展，那么服务器就会在加密数据后计算MAC。

如果客户端或服务器希望更改加密算法，它们可以重新协商之前已确认的密码套件（Cipher Suites）。重新协商过程可以发生在数据传输的任何阶段中，只需要在已有的SSL连接中发起一个初始化Handshake即可。

<br>

**二、漏洞触发**

关于这个漏洞，OpenSSL的官方解释如下：

“在handshake重新协商中，如果协商过程中包含Encrypt-Then-Mac扩展，而原始的handshake中不包含该扩展（反之亦然），那么OpenSSL就会崩溃（取决于所使用的密码套件）。客户端和服务器都会受到影响”。

假设客户端使用默认的MAC-then-encrypt模式发起与服务器的TLS握手流程。如果客户端使用Encrypt-then-MAC扩展发起重新协商流程，并在ChangeCipherSpec消息之前以该模式发送加密数据，那么服务器就会崩溃，导致拒绝服务。

当客户端触发这个漏洞时，服务器的崩溃点位于“ssl3_get_record”函数中，该函数位于“ssl3_record.c”文件中，如下所示：

[![](https://p3.ssl.qhimg.com/t01b143579ac973fc0a.png)](https://p3.ssl.qhimg.com/t01b143579ac973fc0a.png)

崩溃点位于352行，此时程序正在检查mac_size变量值是否小于EVP_MAX_MD_SIZE的值（64字节）：

[![](https://p0.ssl.qhimg.com/t0141edb72c7a95572a.png)](https://p0.ssl.qhimg.com/t0141edb72c7a95572a.png)

if语句判断断言（assertion）语句是否成立，即判断服务器中是否设置了Encypt-then-MAC标识。if语句中的宏如下：

[![](https://p0.ssl.qhimg.com/t019358d248cebc636a.png)](https://p0.ssl.qhimg.com/t019358d248cebc636a.png)

在重新协商过程中，当使用Encrypt-then-MAC扩展发送ClientHello报文时，TLS1_FLAGS_ECRYPT_THEN_MAC标识已经被设置。因此if条件满足，程序会进入if内部的处理流程。但是由于ChangeCipherSpec消息还没有传递给服务器，服务器并不知道它必须使用Encrypt-then-MAC扩展。

在352行设置断点，检查mac_size变量的值，我们发现该至为0xffffffff，这个值比EVP_MAX_MD_SIZE的值（64字节）大。因此断言错误，导致服务器崩溃。

[![](https://p2.ssl.qhimg.com/t01933d9b643a905c73.png)](https://p2.ssl.qhimg.com/t01933d9b643a905c73.png)

让我们好好分析一下源码，看看为什么mac_size的值会是0xffffffff。我们发现EVP_MD_CTX_size函数负责计算mac_size变量的值：

[![](https://p0.ssl.qhimg.com/t01b303d397f35ff41f.png)](https://p0.ssl.qhimg.com/t01b303d397f35ff41f.png)

上述代码中，如果md（message digest，消息摘要）的值为null，函数就会返回-1，而0xffffffff刚好是-1的[**二进制补码形式**](https://en.wikipedia.org/wiki/Two's_complement)。这意味着“s-&gt;read_hash”语句会返回null，因为此时服务器会尝试使用MAC-then-encrypt模式计算哈希值。

以上就是OpenSSL漏洞的分析过程。
