> 原文链接: https://www.anquanke.com//post/id/95746 


# NAT66的优点、缺点及不足


                                阅读量   
                                **397641**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者mcilloni，文章来源：mcilloni.ovh
                                <br>原文地址：[https://mcilloni.ovh/2018/01/20/oh-god-why-NAT66/](https://mcilloni.ovh/2018/01/20/oh-god-why-NAT66/)

译文仅供参考，具体内容表达以及含义原文为准



## 一、前言

很多人对一些技术持有强烈的看法，NAT（以及NAPT）技术正是其中之一。IPv4的地址空间非常小，只有32位。刚开始时计算机的数量非常少，但随着全世界计算机规模大幅增长，这个地址空间已经捉襟见肘。此时NAT及NAPT技术应运而生，可以避免IPv4地址继续分裂，是一种取巧但又非常实用的解决办法。

目前IPv4协议早已大大超出原先设想的范围，该协议已是现代互联网环境中的基本组成部分，这个网络规模极其庞大，是IPv4协议无法承受之重。是时候让IPv4退隐江湖，轮到尚存争议但能解决问题的IPv6上场了。IPv6具有128位的地址空间，足以应付这种规模的网络。

那么，在新的互联网中，端到端原则已经重新回归，成为主要原则之一，此时NAT应该扮演什么角色呢？



## 二、尴尬境地

然而似乎NAT很难有立足之地，IETF一直不推荐人们使用NAT66（NAT这个词在IPv6上已经被占用）。这么做并非无中生有，多年以来，由于NAT网关的存在，本来应该为无状态（stateless）、无连接（connectionless）的IP协议已经变成了一种临时的“有状态（stateful）”、面向连接（connection-oriented）的协议，这主要是因为大量的设备需要接入互联网而不得已为之。

这种地址转换能给我们带来一种虚假的安全感。我已经听过许多人表达过这样一种看法：“从内部网络安全角度来看，NAT是必不可少的一环（然而事实并非如此）”。

IPv6地址空间非常庞大，运营商可以给客户分配足够多的`/64`地址。我始终无法找到NAT66的价值所在：我觉得NAT66从技术上讲根本就是一潭死水，处于本末倒置状态，是先有了答案，再去寻找适配这个答案的问题，很容易被他人滥用。

当然，由于某些托管服务的存在，这种技术仍有发挥的空间。



## 三、应用场景

前一阵子我非常高兴，因为我的VPS提供商宣布他们开始支持IPv6网络，这样一来我就可以在这台VPS上为VPN用户提供IPv6接入方式，不必再去使用Hurrican Electric以及SixXS之类的隧道转换服务，避免产生不必要的延迟。

幸福的时光总是那么短暂，不久后我发现虽然这个运营商拿到了完整的`/32`地址空间（即2^`{`96`}`个IP），但他们还是决定只给VPS客户分配一个`/128`地址。

再强调一下：**只有1个地址**。

[![](https://p0.ssl.qhimg.com/t01ef4090578ef0dcf8.png)](https://p0.ssl.qhimg.com/t01ef4090578ef0dcf8.png)

由于IPv6的连接特性是我配置OpenVPN时迫切需要的一种特性，这让我感到万分悲伤。因此我基本上只剩下两种选择：

1、获取免费的`/64`Hurricane Electric隧道，为VPN用户分配IPv6地址。

2、不得已使用NAT66解决方案。

毫无疑问，Hurrican Electric是最正统的一种选择：这是一种免费服务，可以提供`/64`地址，并且设置起来也非常方便。

这里最主要的问题就是延迟问题，两层隧道的存在（VPN -&gt; 6to4 -&gt; IPv6互联网）会增加一些延迟，并且默认情况下IPv6源IP地址会比IPv4地址优先级更高，因此，如果你拥有一个IPv6公有地址反而会带来一些延迟，这有点令人难以接受。如果我们能找到对IPv6以及IPv4都可以接受的RTT（Round-Trip Time，往返时延）那再好不过。

出于这几方面考虑，我带着一丝愧疚，不得已选择了第二种方案。



## 四、如何配置

设置NAT的过程中通常需要选择一个保留的可路由的私有IP地址范围，以避免内部网络结构与其他网络路由规则相冲突（当然，如果出现多重错误配置依然可能发生冲突）。

IETF在2005年通过ULA（Unique Local Addresses，本地唯一地址）规范，定义了与`10.0.0.0/8`、`172.16.0.0/12`以及`192.168.0.0/16`对应的IPv6地址。这个RFC中定义了唯一的且不能在公网上路由的`fc00::/7`地址，用来定义本地子网，这类地址不需要使用`2000::/3`来保证地址唯一性（`2000::/3`为全球单播地址（Global Unicast Addresses，GUA），也是暂时为互联网分配的地址）。目前该地址范围内实际上只定义了`fd00::/8`，这足以应付私有网络所需要的所有地址。

下一步就是配置OpenVPN，使其能够按我们所需为客户端分配ULA地址，在配置文件末尾添加如下几行：

```
server-ipv6 fd00::1:8:0/112
push "route-ipv6 2000::/3"
```

由于OpenVPN只接受从`/64`到`/112`的掩码长度，因此我为UDP服务器挑选了`fd00::1:8:0/112`地址，为TCP服务器挑选了`fd00::1:9:0/112`地址。

我也希望能通过NAT转发访问互联网的流量，因此还需要指导服务器在客户端连接时向其推送默认路由。

```
$ ping fd00::1:8:1
PING fd00::1:8:1(fd00::1:8:1) 56 data bytes
64 bytes from fd00::1:8:1: icmp_seq=1 ttl=64 time=40.7 ms
```

现在客户端与服务器之间已经可以通过本地地址相互ping通对方，但依然无法访问外部网络。

因此，我需要继续配置内核，以转发IPv6报文。具体方法是使用`sysctl`或者在`sysctl.conf`中设置`net.ipv6.conf.all.forwarding = 1`选项（从这里开始，下文使用的都是Linux环境）。

```
# cat /etc/sysctl.d/30-ipforward.conf 
net.ipv4.ip_forward=1
net.ipv6.conf.default.forwarding=1
net.ipv6.conf.all.forwarding=1
# sysctl -p /etc/sysctl.d/30-ipforward.conf
```

现在，最后一个步骤就是设置NAT66，我们可以通过Linux的包过滤器（packet filter）提供的stateful防火墙来完成这个任务。

我个人比较喜欢使用新一点的`nftables`来取代``{`ip,ip6,arp,eth`}`tables`，因为这个工具更加灵活，更便于理解（但网上相关的文档比较少，这一点不是特别方便，我希望Linux能像OpenBSD那样提供完备的pf文档）。

如果你使用的是`ip6tables`，不妨继续使用这种方法，完全没必要勉强自己将现有的规则集迁移到`nft`中。

我在`nftables.conf`中添加了许多规则，以使NAT66能够正常工作，部分规则摘抄如下。出于完整性考虑，我同时也保留了IPv4规则。

**注意：记得将MY_EXTERNAL_IPV相关地址修改为你自己的IPv4/6地址。**

```
table inet filter `{`
  [...]
  chain forward `{`
    type filter hook forward priority 0;

    # allow established/related connections                                                                                                                                                                                                 
    ct state `{`established, related`}` accept

    # early drop of invalid connections                                                                                                                                                                                                     
    ct state invalid drop

    # Allow packets to be forwarded from the VPNs to the outer world
    ip saddr 10.0.0.0/8 iifname "tun*" oifname eth0 accept

    # Using fd00::1:0:0/96 allows to match for
    # every fd00::1:xxxx:0/112 I set up
    ip6 saddr fd00::1:0:0/96 iifname "tun*" oifname eth0 accept
  `}`
  [...]
`}`
# IPv4 NAT table
table ip nat `{`
  chain prerouting `{`
    type nat hook prerouting priority 0; policy accept;
  `}`
  chain postrouting `{`
    type nat hook postrouting priority 100; policy accept;
    ip saddr 10.0.0.0/8 oif "eth0" snat to MY_EXTERNAL_IPV4
  `}`
`}` 

# IPv6 NAT table
table ip6 nat `{`
  chain prerouting `{`
    type nat hook prerouting priority 0; policy accept;
  `}`
  chain postrouting `{`
    type nat hook postrouting priority 100; policy accept;

    # Creates a SNAT (source NAT) rule that changes the source 
    # address of the outbound IPs with the external IP of eth0
    ip6 saddr fd00::1:0:0/96 oif "eth0" snat to MY_EXTERNAL_IPV6
  `}`
`}`
```

这里需要着重注意的是`table ip6 nat`表以及`table inet filter`中的`chain forward`，它们可以配置包过滤器，执行NAT66方案以及将数据包从`tun*`接口转发到外部网络中。

使用`nft -f &lt;path/to/ruleset&gt;`命令应用新的规则集后，我们可以静静等待这些配置生效。剩下的就是通过某个客户端ping已知的一个IPv6地址，确保转发功能以及NAT功能都可以正常工作。我们可以使用Google提供的DNS服务器地址：

```
$ ping 2001:4860:4860::8888
PING 2001:4860:4860::8888(2001:4860:4860::8888) 56 data bytes
64 bytes from 2001:4860:4860::8888: icmp_seq=1 ttl=54 time=48.7 ms
64 bytes from 2001:4860:4860::8888: icmp_seq=2 ttl=54 time=47.5 ms
$ ping 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=55 time=49.1 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=55 time=50.8 ms
```

非常好，NAT66可以正常工作，客户端能够访问外部IPv6互联网，并且RTT值与IPv4网络不相上下。现在需要检查客户端是否能够解析AAAA记录。由于我在`/etc/resolv.conf`中使用的是Google的DNS服务器，因此检验起来也非常方便：

```
$ ping facebook.com
PING facebook.com (157.240.1.35) 56(84) bytes of data.
^C
$ ping -6 facebook.com
PING facebook.com(edge-star-mini6-shv-01-lht6.facebook.com (2a03:2880:f129:83:face:b00c:0:25de)) 56 data bytes
^C
```

这里有个问题，为什么默认情况下ping命令会先尝试Facebook的IPv4地址，而不会尝试IPv6地址呢？



## 五、解决另一个问题

Linux系统通常会使用Glibc的`getaddrinfo()`函数来解析DNS地址，事实证明该函数有优先级偏好，可以正确处理源-目的地址的优先级关系。

刚开始时，我怀疑默认情况下`getaddrinfo()`在面对本地地址（包括ULA地址）时，会使用与全球IPv6地址不一样的处理方式。因此，我检查了IPv6 DNS解析器的配置文件，即`gai.conf`：

```
label ::1/128       0  # Local IPv6 address
label ::/0          1  # Every IPv6
label 2002::/16     2 # 6to4 IPv6
label ::/96         3 # Deprecated IPv4-compatible IPv6 address prefix
label ::ffff:0:0/96 4  # Every IPv4 address
label fec0::/10     5 # Deprecated 
label fc00::/7      6 # ULA
label 2001:0::/32   7 # Teredo addresses
```

`getaddrinfo()`所使用的默认label表如上所示。

与我猜想的一致，ULA地址的标签（6）与全球单播地址的标签（1）不一样。根据RFC 3484的约定，默认情况下标签的顺序会影响源-地址对的选择，因此每次系统都会优先使用IPv4地址。

为了我们选择的方案最后能够正常工作，我不得已又做了些处理（NAT66中光有ULA并不足够），我需要修改`gai.conf`，如下所示：

```
label ::1/128       0  # Local IPv6 address
label ::/0          1  # Every IPv6
label 2002::/16     2 # 6to4 IPv6
label ::/96         3 # Deprecated IPv4-compatible IPv6 address
label ::ffff:0:0/96 4  # Every IPv4 address
label fec0::/10     5 # Deprecated 
label 2001:0::/32   7 # Teredo addresses
```

在原有的配置文件中删除`fc00::/7`的label后，ULA地址现在已经与GUA地址属于同一类地址，因此系统默认情况下就会使用经过NAT转化的IPv6地址发起连接。

```
$ ping google.com
PING google.com(par10s29-in-x0e.1e100.net (2a00:1450:4007:80f::200e)) 56 data bytes
```

## 

## 六、总结

从上文可知，我们的确可以配置NAT66并让它正常工作，但这个过程中还需要绕过不少坑。由于运营商拒绝给客户提供`/64`地址，因此我不得不放弃端到端的连接特性，稍微处理了一下ULA地址，但这违背了这些地址的设计初衷。

这么做是否值得？也许吧。接入VPN后，现在IPv6上的ping值与IPv4上的难分伯仲，并且其他一切都能正常工作，但这一切都建立在非常复杂的网络配置基础之上。如果每个人都能大致理解IPv6与IPv4的不同点，也明白给客户分配一个地址并不足以简单解决具体问题，那么这一切可能就会简单得多。

现在我们之所以使用NAT，主要是历史遗留问题，当时的地址空间非常狭小，我们不得不破坏互联网的完整性才能拯救整个互联网。为了修复这个难题，我们不得已犯了个错，现在我们有机会能够弥补这一切。从现在起，我们应以认真负责的态度来面对这个过渡期，避免再次陷入泥沼，犯下同一个错。
