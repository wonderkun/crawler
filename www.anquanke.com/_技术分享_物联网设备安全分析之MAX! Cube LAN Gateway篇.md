> 原文链接: https://www.anquanke.com//post/id/85353 


# 【技术分享】物联网设备安全分析之MAX! Cube LAN Gateway篇


                                阅读量   
                                **73374**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：insinuator.net
                                <br>原文地址：[https://insinuator.net/2016/04/discover-the-unknown-analyzing-an-iot-device/](https://insinuator.net/2016/04/discover-the-unknown-analyzing-an-iot-device/)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p1.ssl.qhimg.com/t01c817a24325a6a39d.jpg)](https://p1.ssl.qhimg.com/t01c817a24325a6a39d.jpg)**

**翻译：**[**shan66 ******](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：200RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

在这篇文章中，我们将为读者介绍如何对物联网设备进行安全评估。这里将会详细介绍进行评估所需的基本方法：对于不同的任务需要使用哪些工具，以及如何解决在分析过程中可能出现的问题。本文的目标读者对为对物联网设备安全分析感兴趣的朋友，对逆向工程感兴趣的读者，或者只想了解如何通过技术手段来处理未知设备的读者。

本文的重点不在于揭示某种设备的某种漏洞，而在于阐释影响各种IoT设备的安全弱点，因此，本文介绍的内容同样适用于其他的设备和场景。 

<br>

**分析对象**

本文的分析对象是来自eQ-3公司的 MAX! Cube LAN Gateway （以下称为“Cube”）。实际上，许多产品都捆绑了该设备，比如我的加热控制系统中就带有该设备。通过该设备名称中的“Cube”不难猜出，它只是一个LAN网关，通过RF技术实现真正的“物联网设备”或“智能设备”之间的通信。在本文中，我们将重点介绍以太网通信，因为它是管理软件的主要通信方式。 

<br>

**搭建中间人攻击场景 **

为了全面地了解该设备的通信状况，我搭建了一个简单的中间人攻击场景。我在自己的系统上使用了一个USB网卡，并将其直接连接到Cube。首先，打开Cube，但是不要使用任何管理客户端或其他需要通信的软件，这样就能了解Cube自身发送了什么数据包。我们发现，它只是试图通过DHCP获得IP，然后开始解析ntp.homematic.com。 

为了让Cube可以访问互联网，我已将自己的USB网卡配置为Cube的路由器。为了在不使用DHCP的时候可以通过192.168.0.222访问Cube，我把设备的IP地址设为192.168.0.1/24，并进行了如下所示的配置，以允许通过USB网卡的NAT访问互联网： 



```
sysctl net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -o enp0s25 -j MASQUERADE
iptables -A FORWARD -i enp0s20u9u3 -o enp0s25 -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
```

注意：设备enp0s20u9u3是连接到Cube的USB网卡，enp0s25是系统上的另一个网卡，该网卡连接到具有互联网连接的路由器上。

因为Cube会向默认的路由器发送DNS查询，所以，我们可以在机器上设置一个DNS服务器，或者直接将DNS查询转发给相应的域名服务器（例如OpenDNS服务器）： 



```
iptables -t nat -A PREROUTING -i enp0s20u9u3 -p udp --dport 53 -j DNAT --to 208.67.222.222:53
iptables -t nat -A PREROUTING -i enp0s20u9u3 -p tcp --dport 53 -j DNAT --to 208.67.222.222:53
```

这样一来，我们就能设法观察Cube发送的所有的数据了，例如使用Wireshark或tcpdump等工具来嗅探连接到Cube的NIC上通信数据。 

<br>

**发现网络中的Cube设备 **

为了方便管理员自动识别本地网络上的Cube设备，Cube提供了相应的网络发现功能。下面的Wireshark屏幕截图展示了由本地管理软件发送的数据包： 

[![](https://p5.ssl.qhimg.com/t011d80165618f47d41.png)](https://p5.ssl.qhimg.com/t011d80165618f47d41.png)

该软件会向23272端口上的多播组地址224.0.01发送UDP数据包。在右下方，标记出来的hexdump部分是有效载荷（eQ3Max *  x00 ********** I）。这是一个所谓的身份消息，用来命令Cube向数据包的源主机报告其序列号。下面的截图显示了Cube的响应： 

[![](https://p3.ssl.qhimg.com/t01ee10296320245502.png)](https://p3.ssl.qhimg.com/t01ee10296320245502.png)

同样，这里响应的有效载荷也在右下侧（eQ3MaxApKMD1016788&gt; I）做了标记。 我的设备的序列号是KMD1016788，所以一切正常。现在，我们只要发送这样的UDP数据包，就能轻松找出本地网络上所有的Cube设备。同时，我们也可以检查某个主机是否是使用单播数据包的Cube设备。 

我们自己也可以发送所有这些数据包，甚至单播数据包。对于这些任务，我更喜欢使用Scapy来完成。因为有了它，我们就可以在交互式Python shell中创建、发送/接收和操作数据包，这样做是很方便的，因为这样可以同时进行其他任务，如进行计算或数据转换。Cube使用的UDP端口是23272。我们可以从前面的示例中获取相应字符串（这是一个“身份消息（identity message）”，由有效载荷末尾的“I”表示），并将其发送到目标主机： 



```
&gt;&gt;&gt; p = Ether()/IP(src="192.168.0.1", dst="192.168.0.222")/UDP(sport=23272, dport=23272)/Raw("eQ3Max*x00**********I")
&gt;&gt;&gt; sendp(p, iface="enp0s20u9u3")
```

响应的有效载荷的内容如下所示： 



```
00000000  65 51 33 4d 61 78 41 70  4b 4d 44 31 30 31 36 37 eQ3MaxAp KMD10167
00000010  38 38 3e 49 00 09 9c 3e  01 13                   88&gt;I...&gt; ..
```

注意：Cube发送的响应数据包的源和目标端口总是23272。所以，你要么一直使用23272作为源端口来获得响应，要么使用pcap进行带外捕获——如果你使用随机源端口的话。

实际上身份消息是非常有用的：所有其他UDP消息都需要该Cube的序列号，它将被放入请求的响应中。有了这个序列号，我们就可以发送其他消息类型了，例如 “重新启动消息（reboot message）”（在有效载荷末尾用“R”进行标识）： 



```
&gt;&gt;&gt; p = Ether()/IP(src="192.168.0.1", dst="192.168.0.10")/UDP(sport=23272, dport=23272)/Raw("eQ3Max*x00KMD1016788R")
&gt;&gt;&gt; sendp(p, iface="enp0s20u9u3")
```

就像该消息的名称所示，它会重新启动该设备。这种消息可以从本地网络上的任何设备发出，无需任何身份验证。 

<br>

**如何管理Cube**

Cube的管理方式有三种：

**本地管理软件：**这是一个可安装在Windows上的EXE程序，它会在一个较大的随机端口上启动一个本地Web服务器，用于java applet…

**远程管理软件：**功能与登录界面基本相同，只不过是托管在云中而已。

**移动应用：**我还没有见过。

本地和远程管理软件的主要区别是远程软件的通信是加密的，这一点将在下文详细介绍。 

本地管理软件非常有助于深入了解Cube的内部工作原理，因为通过触发不同的功能，我们就可以观察发送给Cube的相应请求了。为此，我们可以每次执行一个功能，然后捕获相应的流量，从而大概了解哪些事情是可以通过Cube的远程管理来执行的。 

与“远程代理”进行交互 

为了使用远程管理软件，您必须在本地管理软件中配置远程管理所需的用户名和密码。请注意，对于Cube来说，每次只能通过一个客户端进行管理。 因此，当本地管理软件运行时，移动应用程序或远程管理将无法工作。 只要在端口62910上有一个打开的TCP会话，那么其他客户端就无法与此端口通信了。所以，本地网络中可以到达Cube的62910端口的每个客户端，都可以通过连接到Cube的这个端口来阻止其他客户端登陆。 

Cube和远程管理工具之间的通信是加密形式的，但不是SSL / TLS …它们的通信是借助HTTP POST请求来完成的，但是只对POST主体进行了加密。HTTP的头部如下所示： 



```
POST /cube HTTP/1.1
Host: smarthome.md.de
connection: close
Content-Length: 32
Opt: "http://www.eq-3.com/MAX", ns=MAX
MAX-Serial: KMD1016788
```

这些请求将发送到http://smarthome.md.de:8080。其中，一个相当重要的头部是MAX-Serial。它必须包括有效的序列号，否则服务器将只是返回500 Internal Server Errors。 

<br>

**AES密码 **

AES密码用于加密发送到远程管理工具的POST主体。Cube能够支持"e"消息和"d"消息，这两类消息分别实现了“加密”和“解密”功能。这样的话，我们不仅可以对任意字符串进行加密，还能对Cube加密的任何字符串进行解密。下面有一个简单的例子： 



```
~ » ncat 192.168.0.222 62910
[...]
e:TEST^M
E:kvJcZ8bVAoyXaE7gK+q2Ug==
d:kvJcZ8bVAoyXaE7gK+q2Ug==^M
D:TESTAAAAAAAAAAAAAAAAAA==
```

注意：Cube要求命令必须以“ r  n”结尾，否则它不会给予响应。为此，在netcat / ncat这样的工具中发送命令时，不要直接按下RETURN，而应该先按CTRL + v，然后再按RETURN（由行末尾的“^ M”表示）。 

该示例展示了Cube是如何对字符串TEST进行加密的，返回的密文是以Base64编码的字符串kvJcZ8bVAoyXaE7gK + q2Ug ==。 为了对这个字符串进行解密，您可以使用它的解密功能，这样就可以得到明文字符串TEST了。字符串的其余部分只是经过编码的空字节（0x00），用于填充密文，使其符合AES块大小的要求。 

加密的字符串通常使用Base64编码。下面，让我们看一个真实的例子：为了使用远程登录，我们需要设置用户名和密码。从Cube发送到远程系统的明文请求如下所示： 



```
H:KMD1016788,099c3e,0113
B:FOOBAR1,5a8a4a5d3c1bd612b8bf1e2fecf609f7,1,SuperSecret
```

第一行包括的内容是序列号、RF地址和固件版本。 第二行包括用户名（FOOBAR1）、MD5哈希值，数字（1）和实际密码（SuperSecret）。MD5哈希值是 password||serial_number的哈希值： 



```
~ » echo -n "SuperSecretKMD1016788"|openssl md5
(stdin)= 5a8a4a5d3c1bd612b8bf1e2fecf609f7
```

为了将这个有效载荷发送到远程系统，我们必须进行Base64编码： 



```
~ » echo -n "H:KMD1016788,099c3e,0113
B:FOOBAR1,5a8a4a5d3c1bd612b8bf1e2fecf609f7,1,SuperSecret"|base64 -w0
SDpLTUQxMDE2Nzg4LDA5OWMzZSwwMTEzCkI6Rk9PQkFSMSw1YThhNGE1ZDNjMWJkNjEyYjhiZjFlMmZlY2Y2MDlmNywxLFN1cGVyU2VjcmV0
```

然后进行加密： 



```
e:SDpLTUQxMDE2Nzg4LDA5OWMzZSwwMTEzCkI6Rk9PQkFSMSw1YThhNGE1ZDNjMWJkNjEyYjhiZjFlMmZlY2Y2MDlmNywxLFN1cGVyU2VjcmV0^M
E:kGxTXPZVm8CQGcurInyvX3z4C+6zKKKcuS8Wp259XC1yKUfN8tFIfRt0s3qRliIcUGSAcuhuDzl7fpT6fWOnyysSxk9TG1cXtrcVkeNWUzgeO5poXjS5tJlXWgV64ibG
```

我们现在可以将该Base64字符串复制到Burpsuite的中继器中，进行Base64解码（选中它，然后按CTRL + Shift + b），并将其发送到服务器，具体如下图所示： 

[![](https://p0.ssl.qhimg.com/t016b540ca13aa1ef4d.png)](https://p0.ssl.qhimg.com/t016b540ca13aa1ef4d.png)

如图所示，服务器返回了一个200 OK响应，说明我们的请求成功了。之后，我们就可以使用用户名FOOBAR1和密码SuperSecret登录到http://smarthome.md.de/的Web界面了。 为了给响应消息进行解密，我们可以对响应的主体进行Base64编码（只选中响应的主体，并按CTRL + b），然后将其发送到Cube，利用其解密功能进行处理： 



```
d:QAINuzPCglmG1nNNI/ylrbV6AXKdtBQbkNXT/pMobpXSeuP6/tZtCIq8GD5YSHjK^M
D:aTowMDAwNTFiMSwwMDAwMDAwMCxmZmZmZmZmZg0KYjpPSw0KAAAAAAAAAAAAAAAA
```

然后，对得到的Base64字符串进行解码： 



```
~ » echo -n "aTowMDAwNTFiMSwwMDAwMDAwMCxmZmZmZmZmZg0KYjpPSw0KAAAAAAAAAAAAAAAA"|base64 -d
i:000051b1,00000000,ffffffff
b:OK
```

这里的重要问题是：该设备是如何加密该字符串的，加密密钥是什么？ 当谈论AES加密时，你必须弄清楚：

使用的密钥大小是多少？ AES支持128、192和256位密钥。

使用什么操作模式？

根据操作模式：初始化向量（IV）是什么？

第一个问题很容易回答：在供应商页面上，他们说它使用的是AES-128。 那么操作模式是什么呢？ 知道了它，我们就可以加密任意字符串。 最基本的操作模式是ECB：每个16字节块都被独立加密，对于它来说，如果对明文加密两次后会得到相同的密文。 我已经通过字符串（ 16 * “xff”的Base64编码）进行了测试，这个字符串的大小正好等于AES密码的块大小： 



```
e://///////////////////w==^M
E:XQfNd8PcLZgnJbwGTuTx5A==
e://///////////////////w==^M
E:XQfNd8PcLZgnJbwGTuTx5A==
```

我们可以看到，对相同的明文（///////////////////// w ==）加密两次，得到的密文是一致的，那么这可能意味着使用的是ECB 。 但是，让我们看看多个块是否是单独进行加密的。 以下示例将会加密32 *“ xff”（两个块）： 



```
e://///////////////////w==^M
E:XQfNd8PcLZgnJbwGTuTx5A==
e://////////////////////////////////////////8=^M
E:XQfNd8PcLZgnJbwGTuTx5LM36fXWGGUjgVLWxtzwCgo=
```

如果它使用了ECB模式，那么密文应包含两份先前看到的字节序列： 



```
cryptotest » echo -n "XQfNd8PcLZgnJbwGTuTx5A=="|base64 -d |xxd
00000000: 5d07 cd77 c3dc 2d98 2725 bc06 4ee4 f1e4 ]..w..-.'%..N...
cryptotest » echo -n "XQfNd8PcLZgnJbwGTuTx5LM36fXWGGUjgVLWxtzwCgo="|base64 -d |xxd
00000000: 5d07 cd77 c3dc 2d98 2725 bc06 4ee4 f1e4 ]..w..-.'%..N...
00000010: b337 e9f5 d618 6523 8152 d6c6 dcf0 0a0a .7....e#.R......
```

我们可以在hexdump中看到，第一个16字节的确与以前的加密结果一致，但是第二个块是完全不同的。 实际上，ECB加密结果应该是这样的： 



```
cryptotest » xxd plain_16
00000000: ffff ffff ffff ffff ffff ffff ffff ffff ................
cryptotest » xxd plain_32
00000000: ffff ffff ffff ffff ffff ffff ffff ffff ................
00000010: ffff ffff ffff ffff ffff ffff ffff ffff ................
cryptotest » openssl enc -aes-128-ecb -in plain_16 -nosalt -nopad -k TEST |xxd
00000000: cb30 66d5 3db8 89f6 da4b 5831 d29c 6b9f .0f.=....KX1..k.
cryptotest » openssl enc -aes-128-ecb -in plain_32 -nosalt -nopad -k TEST |xxd
00000000: cb30 66d5 3db8 89f6 da4b 5831 d29c 6b9f .0f.=....KX1..k.
00000010: cb30 66d5 3db8 89f6 da4b 5831 d29c 6b9f .0f.=....KX1..k.
```

我们现在知道，它不是ECB。第二种猜测是使用CBC模式进行的加密。CBC在进行AES加密之前，先对第一个块用初始向量IV进行XOR运算，而所有后续块将与前一块的密文进行XOR运算。这样做的好处是防止相同的明文加密两次，会产生两份相同的密文。对于这个IV来说，就是每次加密时生成的一个随机数字。所以这里合理的猜测是，这个Cube使用的是静态IV的CBC。 

但是，要想解密密文的话，我们首先需要获得相应的加密密钥。我这里的猜测是，密钥可能是基于序列号的，因为如果MAX-serial头部中包含的是另一个序列号（即使有效）的话，那么远程服务器就不会接受密文。然而，密钥从未露面，同时Cube和远程服务器在磋商加密参数的时候也没有进行握手。所以，我猜测这个密钥可能是通过序列号计算得到的。 

除了软件方面之外，我还还考察了Cube的硬件。结果是，电路板本身是很小，正面除了序列号之外，好像也没有其他有用的信息。但是，我把它翻过来的时候，有趣的东西出现了…… 

[![](https://p2.ssl.qhimg.com/t014a54633413eb185b.jpg)](https://p2.ssl.qhimg.com/t014a54633413eb185b.jpg)

背面有几个QR码，包括MAC地址，RF地址，序列号，以及一个…KEY …？

标识为KEY的QR码包含以“k”（可能是"key"的意思）为前缀的MD5哈希值，所以，我们不妨尝试用这个密钥来解密密文： 



```
~ » echo -n "XQfNd8PcLZgnJbwGTuTx5LM36fXWGGUjgVLWxtzwCgo="|base64 -d |openssl enc -aes-128-cbc -d -nopad -nosalt -K 98bbce3f1b25df8e6894b779456d330e -iv 00 |xxd
00000000: c975 1589 ed36 536c c975 1589 ed36 536c  .u...6Sl.u...6Sl
00000010: ffff ffff ffff ffff ffff ffff ffff ffff  ................
```

棒极了！您可以看到，第二个块已正确解密了。 实际上，第一个块应该是相同的，但它看起来却是完全随机的。 在上一个命令中，我使用了空字节来作为IV（-iv 00）。但是，不要忘了，在解密CBC模式中的最后一个块之后，需要将最后一个块与IV进行XOR。这样就好理解了：由于第一个块（在解密期间将被最后处理）与一个错误的值进行了异或运算，所以才导致了不同的明文。 

然而，在这种情况下获得IV是相当容易的，因为我们知道明文。我们只要将前面得到的第一个块与明文（即16 *“ xff”）进行异或运算，就能得到正确的IV了。现在，请打开一个Python shell，只需要进行如下所示的操作即可： 



```
&gt;&gt;&gt; hex(0xc9751589ed36536cc9751589ed36536c^0xffffffffffffffffffffffffffffffff)
'0x368aea7612c9ac93368aea7612c9ac93L'
```

现在，让我们用这里的IV再次对密文进行解密： 



```
~ » echo -n "XQfNd8PcLZgnJbwGTuTx5LM36fXWGGUjgVLWxtzwCgo="|base64 -d |openssl enc -aes-128-cbc -d -nopad -nosalt -K 98bbce3f1b25df8e6894b779456d330e -iv 368aea7612c9ac93368aea7612c9ac93 |xxd
00000000: ffff ffff ffff ffff ffff ffff ffff ffff  ................
00000010: ffff ffff ffff ffff ffff ffff ffff ffff  ................
```

如你所见，我们的明文已经完全恢复了！我们还可以解密远程服务器的响应： 



```
~ » echo -n "QAINuzPCglmG1nNNI/ylrbV6AXKdtBQbkNXT/pMobpXSeuP6/tZtCIq8GD5YSHjK"|base64 -d |openssl enc -aes-128-cbc -d -nopad -nosalt -K 98bbce3f1b25df8e6894b779456d330e -iv 368aea7612c9ac93368aea7612c9ac93    
i:000051b1,00000000,ffffffff
b:OK
```

现在，我们已经掌握了在Cube和远程服务器上对字符串进行加密和解密的所有秘密。同时，我还实现了一个小的Python脚本，不仅使得加密/解密字符串变得更加简单，同时还能完成适当的填充操作。 

<br>

****

**网络发现的自动化 **

在我看来，分析未知设备的一个重要部分，就是让其他人也能使用已获得的信息，以支持他人的进一步研究，或能够让人们用通用工具来发现这样的设备。当涉及到发现网络上的设备时，我选择的通用工具是Nmap。除了纯端口扫描之外，它还提供了大量已知服务的签名，同时，我们还可以通过NSE脚本来对其功能进行扩展。

NSE脚本是用Lua语言编写的，而Lua又是一种相当简单和易于理解的脚本语言。 开始编写自己的脚本时，最简单的方法是就是学习现有的脚本（脚本通常位于/usr/share/nmap/scripts目录中，或者在线查找）。例如，对于身份请求来说，我们只需要发送一个UDP包，然后检索响应的有效载荷即可。一个浅显易懂例子是daytime.nse脚本，具体如下所示： 



```
portrule = shortport.port_or_service(13, "daytime", `{`"tcp", "udp"`}`)
action = function(host, port)
  local status, result = comm.exchange(host, port, "dummy", `{`lines=1`}`)
  if status then
    return result
  end
end
```

在开头部分，只是定义了一些元数据，实际上对于每个NSE脚本来说，真正的起始位置都是从portrule这里开始的。它定义了该脚本的运行时机。就本例来说，如果13端口已经打开了，并且与端口13或TCP或UDP服务匹配的时候，就会运行该脚本。 NSE脚本中的第二个重要的事情是action，它可以被看作是NSE脚本的main（）函数。action总是需要两个参数：主机和端口。应当指出，这些不仅仅是一个包含主机名或IP地址和端口号的字符串，每个都是一个保存了诸如主机表（host.mac_addr）中的MAC地址或端口表（port.protocol）中的协议（TCP或UDP）之类附加信息的表。

这个脚本使用了comm模块中的exchange（）函数，而该模块是Nmap提供的诸多LUA模块之一。这个函数的作用，只是发送一个有效载荷并返回响应。如果脚本需要向用户返回信息的话，可以通过纯字符串或LUA表的形式来返回。 

作为Nmap脚本的第一个例子，这里只是在TCP端口62910连接Cube设备，并解析该设备返回的第一行内容，从而输出该Cube设备的序列号、RF地址和固件版本 。 



```
H:KMD1016788,099c3e,0113,00000000,7ee2b5d7,00,32,100408,002c,03,0000
[...]
```

所以，我们的脚本只需要连接到该端口，获得响应并解析值KMD1016788（序列号）、099c3e（RF地址）和0113（固件版本），代码具体如下所示： 



```
local shortport = require "shortport"
local stdnse = require "stdnse"
description = [[
]]
author = "CHANGEME"
license = "Same as Nmap--See https://nmap.org/book/man-legal.html"
categories = `{`"discovery", "safe"`}`
portrule = shortport.portnumber(0, "tcp")
action = function(host, port)
end
```

在上面的代码的基础之上，可以继续添加所需的功能。 因为我们只需要连接到一个端口来获取响应而不发送任何东西，所以最简单的方法是使用一个简单的套接字。有了Nmap后，利用NSE脚本进行socket通信变得异常轻松： 



```
local sock = nmap.new_socket()
local status, err = sock:connect(host, port, "tcp")
if not status then
  stdnse.debug1("%s", err)
  return
end
local status, data = sock:receive()
if not status or not data then
  stdnse.debug1("%s", "Could not receive any data")
  return
end
```

这样就可以在变量ret中接收响应了，然后解析该变量，就能提取所需的信息了： 



```
local output = stdnse.output_table()
local serial, rf_address, firmware
for serial,rf_address,firmware in data:gmatch("H:(%u%u%u%d%d%d%d%d%d%d),(%x%x%x%x%x%x),(%d%d%d%d),") do
    output["MAX Serial:"] = serial
    output["RF Address"] = rf_address
    output["Firmware Version"] = firmware
end
```

现在，我们就有了一个输出表，其中包含了需要返回给用户的所有信息。正如前面说过的一样，为此只需在action的末尾放上一个“return output”即可。 完整的脚本可以在这里下载。

我们可以测试该脚本，检查是否能够正常工作： 



```
max-cube/nse » nmap --script maxcube-info.nse -Pn -p 62910 192.168.0.222
Starting Nmap 7.12SVN ( https://nmap.org ) at 2016-04-08 01:11 CEST
Nmap scan report for 192.168.0.222
Host is up (0.0051s latency).
PORT      STATE SERVICE
62910/tcp open  unknown
| maxcube-info: 
|   MAX Serial:: KMD1016788
|   RF Address: 099c3e
|_  Firmware Version: 0113
```

从上面的结果来看，我们的脚本工作正常。但它可能是非常不可靠的：就像我前面提到的，当端口62910上有一个开放的TCP连接（例如管理软件正在运行或有人通过netcat连接该端口）的时候，Nmap将无法与该端口进行通信，那么这个脚本自然就无法正常工作了。 

一些有用的提示： 

stdnse模块提供了debug()函数，可以用来在脚本中打印所有的调试输出。为此，至少需要提供一个-d命令行参数。

命令行参数-script-trace能够提供调试NSE脚本所需的更详细的输出结果。

为了在已标识为打开的所有端口上运行该脚本，请在脚本名称前面加上前缀+，例如不要用“-script myscript.nse”，而是使用“-script + myscript.nse” 

 

**接下来要做什么？ **

还有两个大问题需要解决： 

**加密密钥来自哪里？ **

我认为加密密钥（看起来像一个MD5哈希值）是只有供应商知道的密码串与序列号的哈希值。由于供应商可以区分密文，这意味着每个设备都可能有一个自己的密钥（我只有一个设备可以测试）。

一个不同的论点：我在电路板上的QR码中发现的密钥。这可能表示，密钥在设备的制造期间就已经确定下来了。 加密密钥可以是完全随机的，并且甚至可能不是包括序列号的任何明文的散列值。但这意味着供应商将需要建立一个列表，以便在制造期间将所有的序列号都映射为相应的密钥。 

**文件firmware.enc是如何加密的？ **

Cube提供了更新功能，也就是可以通过UDP数据包发送一些新版本的固件（记住，这是未经验证的）。 然而，固件文件是不可读的，并且需要在该设备上进行解密，因为管理软件只能解析文件，但无法解密它们。我已经编写了一个简单的解析代码（地址[https://github.com/ernw/insinuator-snippets/tree/master/maxcube/firmware/parser](https://github.com/ernw/insinuator-snippets/tree/master/maxcube/firmware/parser)），但固件本身似乎是加密的。

不过，我猜修改固件是一件很酷的事情。

<br>

**编写其他Nmap脚本 **

正如在文章开头所看到的那样，至少有两种方法可以识别网络上的Cube：多播或单播UDP数据包。然而，这些方法还是需要一点技巧的，因为响应的源端口是静态的（总是23272）。所以，如果你打算在脚本中使用Nmap的comm.exchange()函数的话，那么是无法在函数中获得任何响应的，因为它会使用随机的源端口。 

这个问题的解决方案是发送组播数据包，然后使用pcap捕获响应。实际上，Nmap的一些脚本已经可以做到这一点了，例如我就写过一个脚本，专门利用类似的技术来寻找KNX设备。  

<br>

**结束语**

根据我们分析IoT设备的经验，大部分物联网设备都存在许多常见的安全漏洞，如缺乏身份验证或验证不足等。 此外，在网络上识别这样的设备通常是轻而易举的事情，因为它们具有一些“奇异”的属性，例如响应分组中的固定源端口或者仅允许单个TCP连接等。所以，我希望分析未知设备的研究人员也开始共享他们的研究成果，例如向Nmap等项目贡献代码，以便帮助更多的人。 
