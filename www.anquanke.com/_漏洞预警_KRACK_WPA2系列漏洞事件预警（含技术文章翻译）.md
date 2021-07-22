> 原文链接: https://www.anquanke.com//post/id/87028 


# 【漏洞预警】KRACK：WPA2系列漏洞事件预警（含技术文章翻译）


                                阅读量   
                                **135216**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01a46052b0aa110fcc.png)](https://p1.ssl.qhimg.com/t01a46052b0aa110fcc.png)



**0x00 事件描述**



2017年10月16日, 名为KRACK的漏洞攻击方式被披露，针对WiFi+WPA2网络的攻击。

KRACK主要是利用802.11i中4次握手中的漏洞来最终实现解密和伪造加密的WiFi流量，该漏洞由来自imec-DistriNet的Mathy Vanhoef和 KU Leuven发现。本次漏洞事件有多种攻击型态，AP热点端，中继端，和客户端均受到影响。

根据krackattacks.com和部分厂商发布的安全公告综合分析，包括Linux,Android, Cisco wireless products, OpenBSD, MacOS, Windows, iOS等产品或平台, 影响面广泛。

360CERT建议客户端产品用户，IoT, 路由器厂商尽快进行相关漏洞评估调查。

附:技术翻译[《密钥重载攻击：强制WPA2重用Nonce》](http://bobao.360.cn/learning/detail/4561.html)一文。



**0x01 事件影响面**



**影响面**

KRACK漏洞的范围广泛，影响面大。

KRACK漏洞可造成WiFi+WPA2的加密网络流量可被攻击者解密或注入恶意攻击包，可能会泄露包括密码等在内的隐私信息，但是使用HTTPS等应用层加密层的流量不受影响。

360CERT综合分析，此次漏洞事件影响面大，漏洞等级重要，暂无规模性实际攻击案例发生，暂评定为较大网络安全事件。

**漏洞信息**

CVE-2017-13077: 4次握手时配对密钥(PTK-TK)重载漏洞

CVE-2017-13078: 4次握手时GTK重载漏洞

CVE-2017-13079: 4次握手时IGTK重载漏洞

CVE-2017-13080: group key握手时GTK重载漏洞

CVE-2017-13081: group key握手时IGTK重载漏洞

CVE-2017-13082: 接收FT重连请求，配对密钥(PTK-TK)重载漏洞

CVE-2017-13084: PeerKey握手时STK key重载漏洞

CVE-2017-13086: TDLS握手时TDLS,TPK重载漏洞

CVE-2017-13087: 处理WNM休眠模式响应帧GTK重载漏洞

CVE-2017-13088: 处理WNM休眠模式响应帧IGTK重载漏洞

**影响版本**

注:部分信息来源[参考3]

Arch Linux

Arista

Aruba

Broadcom

Cisco

DD-WRT

Debian

Extreme Networks

Fedora

FreeBSD

Lenovo

Juniper

Intel Corporation

LineageOS

LXDE

Marvell

Meraki

Microsoft

MikroTik

Mojo Networks

Synology

Turris Omnia

Ubiquiti

Ubuntu

UniFi

VMware

Watchguard Cloud

Windows 10

WPA_supplicant



**0x02 部分技术信息**



**注:部分信息来自[参考1]和[参考4]**

802.11i协议（即：WPA2协议）通过两种独立的机制来保证数据传输的机密性。第一个是在记录层通过加密WiFi帧的方式，保证无法被明文读取或嗅探。该加密机制通常是通过AES-CCM的方式，当然也有部分启动GCM模式，还有部分老的RC4-TKIP方式。

需要认真考虑的是AES-CCM(还包括GCM, TKIP)是一种流加密，这意味着在重用加密参数key和nonce(即:初始向量)的情况下是可以被攻击的。802.11i是基于包计数(packet number number)的方式，其在会话建立后的初始值为0，且会不停递增（当然到了2^48的时候，会触发更新key操作）。这样一来，假设在包计数不被重置的情况下，就可以成功防范key+nonce的重用攻击。

第二个机制是AP和客户端（supplicant）之间的4次握手流程，主要用于协商加密key。KRACK漏洞会直接利用到4次握手中的#3包，#3包可作用于客户端新key安装使用。

[![](https://p3.ssl.qhimg.com/t0120502d4069c33ffb.png)](https://p3.ssl.qhimg.com/t0120502d4069c33ffb.png)

KRACK的主要漏洞在于 #3包 可以被恶意阻断。当这个情况发生时，AP端会重发这个消息，会导致同样的一个key在客户端中被重装。带来的副作用是也会导致包计数会被重置为0（部分客户端，如Android6，会把key重置为0)，最终，就会触发key+nonce的重用攻击了。攻击者可以利用它来全流量解密，TCP劫持等。

此外，还有如下2种攻击:

包括针对客户端的基于GTK的攻击；

针对AP端的802.11 RFT握手攻击；

更详细技术细节可参阅360CERT翻译的《[密钥重载攻击：强制WPA2重用Nonce](http://bobao.360.cn/learning/detail/4561.html)》一文。



**Q &amp; A**



注:部分信息来自[参考1]

**我需要更换WiFi密码吗？**

更改WiFi密码并无助于防御和解决该漏洞，你不需要更改。相反的，你应该关注你使用的客户端（Android, IoT产品）是否更新，路由器固件是否更新了。当然如果你都这么做了，那你可以借此更新下你的WiFi密码了。

**只支持AES套件的WPA2也受该漏洞影响吗？**

是的，也受。

**我的设备是否也受影响？**

如果你的设备支持WiFi+WPA2连接的话(如手机，笔记本电脑等)，很可能也受到影响，请咨询相关厂商。

**如果我的路由器没有发布更新怎么办？**

虽然攻击者的利用可能是针对客户端的，但是路由器等也是有风险的。建议您首先联系下您的厂商确定下是否有安全更新，当然您也可以选择有安全更新的360安全路由器。

**我应该暂时切换到WEP，直到我的设备被更新了？**

别，这绝对不是个好选择。

**这个攻击看起来很难吗？**

其实实践起来并没有那么难，甚至挺普通简单的。千万别认为这个攻击很难。



**0x03 安全建议**



建议用户尽快评估自身的客户端,并安装对应安全更新



**0x04 时间线**



2017-10-16 事件披露

2017-10-17 360CERT发布预警通告



**0x05 参考链接**



Key Reinstallation Attacks Breaking WPA2 by forcing nonce reuse

[https://www.krackattacks.com](https://www.krackattacks.com)

Key Reinstallation Attacks: Forcing Nonce Reuse in WPA2

[https://papers.mathyvanhoef.com/ccs2017.pdf](https://papers.mathyvanhoef.com/ccs2017.pdf)

KRACK: (K)ey (R)einstallation (A)tta(ck)

[https://github.com/kristate/krackinfo](https://github.com/kristate/krackinfo)

Falling through the KRACKs

[https://blog.cryptographyengineering.com/2017/10/16/falling-through-the-kracks/](https://blog.cryptographyengineering.com/2017/10/16/falling-through-the-kracks/)

Arch Linux: wpa_supplicant

[https://git.archlinux.org/svntogit/packages.git/commit/trunk?h=packages/wpa_supplicant&amp;id=9c1bda00a846ff3b60e7c4b4f60b28ff4a8f7768](https://git.archlinux.org/svntogit/packages.git/commit/trunk?h=packages/wpa_supplicant&amp;id=9c1bda00a846ff3b60e7c4b4f60b28ff4a8f7768)

Arch Linux: hostapd

[https://git.archlinux.org/svntogit/community.git/commit/trunk?h=packages/hostapd&amp;id=d31735a09b4c25eaa69fb13b1031910ca3c29ee5](https://git.archlinux.org/svntogit/community.git/commit/trunk?h=packages/hostapd&amp;id=d31735a09b4c25eaa69fb13b1031910ca3c29ee5)

DD-WRT

[http://svn.dd-wrt.com/changeset/33525](http://svn.dd-wrt.com/changeset/33525)

MicroSoft

[https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-13080](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-13080)

Redhat:CVE-2017-13087

[https://access.redhat.com/security/cve/cve-2017-13087](https://access.redhat.com/security/cve/cve-2017-13087)

密钥重载攻击：强制WPA2重用Nonce

[https://cert.360.cn/static/files/%E5%AF%86%E9%92%A5%E9%87%8D%E8%BD%BD%E6%94%BB%E5%87%BB%EF%BC%9A%E5%BC%BA%E5%88%B6WPA2%E9%87%8D%E7%94%A8Nonce.pdf](https://cert.360.cn/static/files/%E5%AF%86%E9%92%A5%E9%87%8D%E8%BD%BD%E6%94%BB%E5%87%BB%EF%BC%9A%E5%BC%BA%E5%88%B6WPA2%E9%87%8D%E7%94%A8Nonce.pdf)
