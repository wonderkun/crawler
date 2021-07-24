> 原文链接: https://www.anquanke.com//post/id/221706 


# NAT Slipstreaming攻击使防火墙形同虚设


                                阅读量   
                                **213969**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01d8216d5d0ade810f.jpg)](https://p3.ssl.qhimg.com/t01d8216d5d0ade810f.jpg)



2020年10月31日安全研究员Samy Kamka发布了一种被称为NAT Slipstreaming的攻击颠覆了人们对防火墙中NAT安全性认知。

NAT Slipstreaming，利用诱骗了受害人访问可能受到黑客控制的网站后，则允许攻击者绕过受害人的网络地址转换（NAT）或防火墙安全控制，远程访问绑定到受害者计算机的任何TCP/UDP服务。

[![](https://p5.ssl.qhimg.com/t01cf83f80403f1f6b2.png)](https://p5.ssl.qhimg.com/t01cf83f80403f1f6b2.png)

NAT Slipstreaming结合了通过定时攻击或WebRTC链接内部IP提取，自动远程MTU和IP碎片发现，TCP数据包大小按摩的内部IP提取，结合了内置在NAT，路由器和防火墙中的应用层网关（ALG）连接跟踪机制，利用了用户浏览器，TURN身份验证滥用，精确的数据包边界控制以及浏览器滥用造成的协议混乱。由于是打开目标端口的NAT或防火墙，因此绕过了任何基于浏览器的端口限制。

这种攻击利用了对某些TCP和UDP数据包的数据部分的任意控制的优势，而没有包括HTTP或其他标头。该攻击会在所有主要的现代（和较旧）浏览器上执行这项新的数据包注入技术，并且是我自2010年起使用的原始NAT Pinning技术（在DEFCON 18 + Black Hat 2010上提出的）的现代化版本。此外，还包括用于本地IP地址发现的新技术。

此攻击需要NAT /防火墙来支持ALG（应用级网关），这对于可以使用多个端口（控制通道+数据通道）的协议是必需的，例如SIP和H323（VoIP协议），FTP，IRC DCC等。

NAT Slipstreaming的工作方式如下：

1.受害者访问恶意网站（或带有恶意广告的网站）

2.首先必须通过浏览器提取受害者的内部IP并将其发送到服务器
1. 尝试通过WebRTC数据通道通过https提取内部IP
1. 有些浏览器（Chrome）仅通过HTTPS通过WebRTC泄露本地IP，但我们的某些攻击需要HTTP，因此我们首先重定向到攻击软件的HTTPS版本以提取本地IP
1. 如果我们能够绕过其他跨域保护机制，则将其重定向到URL中包含本地IP的HTTP版本（显示的.local mDNS / Bonjour地址对攻击没有帮助）
1. 如果内部IP未通过WebRTC（Safari）泄露或未通过WebRTC（&lt;= IE11）泄露，则将执行基于Web的TCP定时攻击
1. 隐藏到所有通用网关（例如192.168.0.1）的img标签在后台加载
1. 附加到img标签的onerror /成功事件
1. 如果网关（或SYN + HTTP响应）返回了任何TCP RST，则表明我们检测到有效子网
1. 在检测到的子网（/ 24）上的所有IP上重新执行定时攻击，以衡量发生错误/成功触发的时间
1. 最快的响应可能是内部IP，尽管所有响应都被视为内部IP候选者并受到攻击
3.大型TCP信标通过隐藏形式和自动HTTP POST发送给绑定到非标准端口的攻击者“ HTTP服务器”，以强制TCP分段和受害者IP堆栈的最大MTU大小发现
1. 攻击者TCP服务器发送“最大段大小TCP选项”以按摩受害者出站数据包大小（RFC 793 x3.1），从而可以控制将多大的浏览器TCP数据包
4.浏览器通过WebRTC TURN身份验证机制从浏览器发送到攻击者服务器的非标准端口的大型UDP信标，以强制填充TURN用户名字段的IP碎片
1. 我们会执行与TCP分段类似的攻击，但是会通过UDP进行IP分段，并提供与TCP分段不同的值
1. 服务器检测到并发送回受害者浏览器的受害者MTU大小，IP标头大小，IP数据包大小，TCP报头大小，TCP段大小，稍后用于数据包填充
5.以新的隐藏形式生成的“ SIP数据包”，包含用于触发应用程序级别网关连接跟踪的内部IP
1. 已启动到TCP端口5060（SIP端口）上的服务器的“ HTTP POST”，避免了受限制的浏览器端口
1. 将POST数据“填充”到确切的TCP段大小/数据包边界，然后通过Web表单附加和发布“ SIP数据包”
1. 受害IP堆栈将POST分解为多个TCP数据包，将“ SIP数据包”（作为POST数据的一部分）保留在其自己的TCP数据包中，而没有任何随附的HTTP标头
1. 如果浏览器由于任何其他原因更改了多部分/表单边界（Firefox）的大小或数据包大小更改，则大小更改会传达回客户端，并且客户端会以新大小自动重新发送
1. 当打开UDP端口时，在特制的用户名字段内通过TURN协议发送SIP数据包，从而强制IP分段和精确的边界控制
6.受害者NAT在SIP端口上看到正确的SIP REGISTER数据包（没有HTTP数据），从而触发ALG将数据包中定义的任何TCP / UDP端口打开回受害者
1. 受害者NAT重写SIP数据包，用公共IP替换内部IP，暗示攻击者利用成功
1. 即使受害人NAT通常重写源端口，ALG仍然会被迫转发到攻击者选择的端口，因为它认为受害机器打开了该端口，并且攻击者在到达的SIP数据包中看到了新的源端口。
1. 攻击者现在可以绕过受害者NAT，并直接连接回受害者计算机上的任何端口，从而暴露以前受保护/隐藏的服务。
1. 非恶意使用：此技术实质上为浏览器提供了完整的TCP和UDP套接字功能，可以与系统上本地的任何协议进行通信；可以通过连接回去的云服务器来抽象连接，但浏览器只是与云服务器对话，就好像它是套接字一样，使浏览器更强大，可以通过非Web友好协议进行通信
1. 如果在使用共享网络的虚拟机（VM）中进行测试（用于通过将主机路由到主机，而不是直接将主机路由到网络上来保护主机免受攻击），如果数据包将其识别出来，则父主机就是端口最终被打开，而不是虚拟机
1. IP分段可以完全控制IP数据部分中的所有数据，这意味着可以完全控制UDP报头，包括溢出数据包中的源/目标端口
[![](https://p3.ssl.qhimg.com/t019502a93fc38ed28e.png)](https://p3.ssl.qhimg.com/t019502a93fc38ed28e.png)

参考链接：

https://samy.pl/slipstream/

https://github.com/samyk/slipstream
