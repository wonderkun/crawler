> 原文链接: https://www.anquanke.com//post/id/181652 


# 【缺陷周话】第42期：Cookie: 未经过 SSL 加密


                                阅读量   
                                **265922**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01649690fcb193fd32.jpg)](https://p4.ssl.qhimg.com/t01649690fcb193fd32.jpg)

## 1、Cookie: 未经过 SSL 加密

“Cookie: 未经过SSL加密”是指在创建 Cookie 时未将 secure 标记设置为 true，那么从通过未加密的通道发送 Cookie 将使其受到网络截取攻击。如果设置了该标记，那么浏览器只会通过 HTTPS 发送 Cookie，可以确保Cookie的保密性。本文以JAVA语言源代码为例，分析“Cookie：未经过SSL加密”缺陷产生的原因以及修复方法。

该缺陷的详细介绍请参见CWE ID 614: Sensitive Cookie in HTTPS Session Without ‘Secure’Attribute（http://cwe.mitre.org/data/definitions/614.html）。



## 2、”Cookie：未经过 SSL 加密”的危害

攻击者可以利用 “Cookie：未经过SSL加密”缺陷窃取或操纵客户会话和 Cookie，它们可能被用于模仿合法用户，从而使攻击者能够以该用户身份查看或变更用户记录以及执行事务。

从2018年1月至2019年7月，CVE中共有202条漏洞信息与其相关。部分漏洞如下：

<th width="154">CVE 编号</th><th width="398">概述</th>
|------
<td width="146">CVE-2018-5482</td><td width="397">NetApp SnapCenter 4.1 之前版本的服务器没有在HTTPS会话中为敏感 cookie 设置 secure 标志，这可以允许通过未加密的通道以纯文本形式传输cookie。</td>
<td width="146">CVE-2018-1948</td><td width="397">IBM Security Identity Governance and Intelligence 5.2 到5.2.4.1 虚拟设备未在授权令牌或cookie上设置安全属性。攻击者可以通过向用户发送 http 链接或通过在用户访问的站点中植入此链接来获取 cookie 值。cookie 将被发送到不安全的链接，然后攻击者可以通过窥探流量来获取 cookie 值。</td>
<td width="146">CVE-2018-1340</td><td width="397">Apache Guacamole 1.0.0 之前的版本使用 cookie 来存储用户会话令牌的客户端。此 cookie 缺少 secure 标志，如果对同一域发出未加密的 HTTP 请求，则可能允许攻击者窃听网络以拦截用户的会话令牌。</td>



## 3、示例代码

示例源于 WebGoat-8.0.0.M25 (https://www.owasp.org/index.php/Category:OWASP_WebGoat_Project)，源文件名：JWTVotesEndpoint.java。

### 3.1 缺陷代码

[![](https://p3.ssl.qhimg.com/t0108c6832069341bef.png)](https://p3.ssl.qhimg.com/t0108c6832069341bef.png)

上述示例代码是判断登录用户是否为指定用户，如果是指定用户，生成一个加密的Token 作为 Cookie 的值。在代码行第69行判断用户是否为指定用户: 如果是，在第70~72行声明了一个指定签发时间的自定义属性claims，并在 claims 中设置属性，user 的属性值为变量 user，admin 属性值为 false。第73行~76行JWT使用 SHA-512HMAC 算法生成一个 Token，并赋值给 token。第77行创建一个名称为access_token，值为 token 的 Cookie 对象。第78行将该 Cookie 对象放入response 中。如果不是指定用户，则创建一个名称为 access_token，值为空字符串的 Cookie 对象。如果应用程序同时使用 HTTPS 和 HTTP，但没有设置 secure 标记，那么在 HTTPS 请求过程中发送的 Cookie 也会在随后的 HTTP 请求过程中被发送。通过未加密的连接网络传输敏感信息可能会危及应用程序安全。

使用代码卫士对上述示例代码进行检测，可以检出“Cookie：未经过SSL加密”缺陷，显示等级为中。在代码行第78行和第83行报出缺陷如图1、图2所示：

[![](https://p2.ssl.qhimg.com/t011fbd9816317851ca.png)](https://p2.ssl.qhimg.com/t011fbd9816317851ca.png)

图1：“Cookie: 未经过 SSL 加密”检测示例

[![](https://p1.ssl.qhimg.com/t0141c6ae490133f59e.png)](https://p1.ssl.qhimg.com/t0141c6ae490133f59e.png)

图2：“Cookie: 未经过 SSL 加密”检测示例

### 3.2 修复代码

在上述修复代码中，将 Cookie 的 secure 标记设置为 true，保证通过 HTTPS 发送 Cookie。

使用代码卫士对修复后的代码进行检测，可以看到已不存在“Cookie：未经过SSL加密”缺陷。如图3：

[![](https://p5.ssl.qhimg.com/t01be7506519ce36327.png)](https://p5.ssl.qhimg.com/t01be7506519ce36327.png)

图3：修复后检测结果



## 4、如何避免“Cookie: 未经过SSL 加密”

为 Cookie 设置 secure 标记，要求浏览器通过 HTTPS 发送 Cookie，将有助于保护Cookie 值的保密性。
