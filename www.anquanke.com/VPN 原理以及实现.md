> 原文链接: https://www.anquanke.com//post/id/248136 


# VPN 原理以及实现


                                阅读量   
                                **37404**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t0170e5f118297e191c.jpg)](https://p1.ssl.qhimg.com/t0170e5f118297e191c.jpg)



作者：0x7F@知道创宇404实验室**<br>**

### <a class="reference-link" name="0x00%20%E5%89%8D%E8%A8%80"></a>0x00 前言

最近在工作中遇到 VPN 的相关问题，之前一直对 VPN 的原理存在一些疑惑，借此机会学习一下 VPN 的原理以及进行实现验证。

由于 VPN 在不同系统下的实现方式不同，为了便于学习和理解，这里我们选择 `Linux` 环境，我本地测试环境使用的是 `Ubuntu 18.04 x64`。

本文从 TUN/TAP 出发，逐步理解 VPN 中的技术细节；并结合 [simpletun](https://github.com/gregnietsky/simpletun) 源码，进行 VPN 的原理验证。

### <a class="reference-link" name="0x01%20VPN%E6%98%AF%E4%BB%80%E4%B9%88"></a>0x01 VPN是什么

VPN 全称为虚拟私人网络(Virtual Private Network)，常用于连接中、大型企业或团体间私人网络的通讯方法，利用隧道协议（Tunneling Protocol）来达到发送端认证、消息保密与准确性等功能。

比如多地办公的公司，可以使用 VPN 将不同地区连接在同一内网下；或者在家办公的时候也可以通过 VPN 接入公司内网中。

VPN 以 CS 架构运行，工作流程如下：

[![](https://p0.ssl.qhimg.com/t01e5f45317f16d05bb.png)](https://p0.ssl.qhimg.com/t01e5f45317f16d05bb.png)

1.VPN工作流程

在外网的用户可以使用 `vpn client` 连接组织搭建的 `vpn server` 以建立通信隧道，随后便建立了虚拟的私人网络，处于外网的 `worker` 和内网中的 `server` 可以相互通信。

那么我们可以简单理解 VPN，由 `VPN client` 捕获用户发出的报文，封装报文后通过物理网络通信链路将报文发给 `VPN server`，`VPN server` 接收到报文后进行解包，再将其转发给实际的目标，反之同理； VPN 在逻辑层面构建了虚拟网络。

### <a class="reference-link" name="0x02%20TUN/TAP"></a>0x02 TUN/TAP

那么在代码层面 VPN 是如何实现的呢？我们可以先来看看 TUN/TAP。

TUN/TAP 是操作系统内核中的虚拟网络设备，由软件进行实现，向操作系统和应用程序提供与硬件网络设备完全相同的功能。其中 TAP 是以太网设备(二层设备)，操作和封装以太网数据帧，TUN 则是网络层设备(三层设备)，操作和封装网络层数据帧。

当应用程序发出报文后，报文将通过操作系统协议栈处理，到达网络设备，硬件网络设备将收到的报文转化为电信号发出，而虚拟网络设备(TUN/TAP)不具备实际的物理功能，报文需要上层应用进行处理，如下：

[![](https://p4.ssl.qhimg.com/t01c7a4921e091e6273.png)](https://p4.ssl.qhimg.com/t01c7a4921e091e6273.png)

2.硬件/虚拟网络设备

我们直接使用命令创建 TUN/TAP 设备，并进行测试：

```
# ip tuntap 创建名为 tun0 的 tun 设备
sudo ip tuntap add dev tun0 mod tun
# 为 tun0 配置 ip
sudo ifconfig tun0 192.168.0.10 netmask 255.255.255.0
# 查看 tun0 网卡
ifconfig tun0
```

如下：

[![](https://p1.ssl.qhimg.com/t01f2b77992d78bba20.png)](https://p1.ssl.qhimg.com/t01f2b77992d78bba20.png)

3.通过命令创建TUN设备

在 VPN 中我们可以借助 TUN/TAP 来捕获用户发出的报文。

### <a class="reference-link" name="0x03%20%E8%99%9A%E6%8B%9F%E9%80%9A%E4%BF%A1%E9%93%BE%E8%B7%AF"></a>0x03 虚拟通信链路

按照 TUN/TAP 的工作特性，我们可以编写程序直接读写虚拟网卡(也就是物理网卡实际收发报文的过程)，来实现捕获用户数据以及传递用户数据。(TUN 和 TAP 有不同的应用场景，下文我们将以更简单的 TUN 作为例子)

随后，位于不同主机上的程序通过 socket 进行通信，将从虚拟网卡的接收的数据通过 socket 发送给对端，这就是一个 VPN 的雏形了，如下：

[![](https://p5.ssl.qhimg.com/t01310bd64cb7e2e4b3.png)](https://p5.ssl.qhimg.com/t01310bd64cb7e2e4b3.png)

4.虚拟通信链路工作流程

`simpletun` 是这种方案的最小实现(源码仅 300+ 行，感兴趣的小伙伴可以自行学习)，在源码中实现了创建虚拟网络设备以及 socket 通信，借助 `simpletun` 可以帮助我们快速进行验证。

需要注意一点，`simpletun` 启动后需要我们手动配置虚拟网卡的 ip 地址，当 ip 地址未配置时，两端相互发送数据(部分操作系统会自动发送)会造成程序异常退出，所以在代码中添加一个 `sleep(30)` 便于我们配置 ip 地址：

[![](https://p4.ssl.qhimg.com/t014eb6b452d0d6e456.png)](https://p4.ssl.qhimg.com/t014eb6b452d0d6e456.png)

5.在simpletun中添加sleep

在两台 `Ubuntu` 测试环境下配置并进行验证：

```
# A主机
# 编译 simpletun
gcc simpletun.c -Wall -o vpn
# 作为 vpn server 启动，并开启 debug，默认监听 55555
sudo ./vpn -i tun0 -s -d
# 配置 tun 网卡地址
sudo ifconfig tun0 192.168.0.10 netmask 255.255.255.0

# B主机
# 编译 simpletun
gcc simpletun.c -Wall -o vpn
# 作为 vpn client 启动，连接 server，并开启 debug
sudo ./vpn -i tun0 -c 10.11.33.50 -d
# 配置 tun 网卡地址
sudo ifconfig tun0 192.168.0.11 netmask 255.255.255.0
```

此时两台主机位于 `192.168.0.0/24` 虚拟网络网段下，可以相互通信，如下：

[![](https://p1.ssl.qhimg.com/t01a1a00ffbba85caa2.png)](https://p1.ssl.qhimg.com/t01a1a00ffbba85caa2.png)

6.虚拟通信链路两端通信

### <a class="reference-link" name="0x04%20%E8%AE%BF%E9%97%AE%E5%86%85%E7%BD%91%E7%BD%91%E6%AE%B5"></a>0x04 访问内网网段

在上文的验证中，我们可以实现两端的虚拟网络搭建和通信，但实际 VPN 的使用场景是需要通过 VPN 访问整个内网网段，在这种使用场景下，VPN server 至少配置有两张物理网卡，其中一张接入内网网段，另一张则连接到互联网。

按照 `0x03 虚拟通信链路` 的链路，VPN client 发送报文到内网主机，VPN server 接收到该报文后，将其写入到虚拟网卡中，随后报文进入 TCP/IP 协议栈，但是由于 IP 地址不是 VPN server 自己，该报文会被丢弃，无法正常进行通信；这里我们需要借助「报文转发」，将内网报文从虚拟网卡转发到内网网卡上。其新的工作流程如下：

[![](https://p1.ssl.qhimg.com/t019c296c72b1451b16.png)](https://p1.ssl.qhimg.com/t019c296c72b1451b16.png)

7.VPN访问内网网段

> VPN server 一般会作为内网网关，内网主机无需任何额外配置就可以在虚拟网段下正常工作。

我们按照该流程配置测试环境，复用 `0x03 虚拟通信链路` 中的环境，在 VPN server 上我们使用 docker 模拟内网网段和主机，其环境搭建如下：

[![](https://p5.ssl.qhimg.com/t01a9baf8b40f8544ec.png)](https://p5.ssl.qhimg.com/t01a9baf8b40f8544ec.png)

8.VPN测试环境搭建

然后按照 `0x03 虚拟通信链路` 中的方式，启动 `simpletun` 并使用 `ifconfig` 配置 ip 地址，创建虚拟通信链路；使用如下命令开启报文转发：

```
# 临时开启报文转发
echo "1" &gt; /proc/sys/net/ipv4/ip_forward
```

> 实际上在该测试环境下，docker 会自动开启报文转发

再通过 `iptables` 配置转发策略，如下：

```
# 将入口网卡、来源ip为 192.168.0.0/24 转发至 docker0
sudo iptables -A FORWARD -i tun0 -s 192.168.0.0/24 -o docker0 -j ACCEPT
# 将入口网卡、目的ip为 192.168.0.0/24 转发至 tun0
sudo iptables -A FORWARD -i docker0 -d 192.168.0.0/24 -o tun0 -j ACCEPT
```

> 实际上在该测试环境下，第二条可以不用配置，因为 docker 会自动配置转发策略，会覆盖这条策略

除此之外，为了在 VPN client 可以访问到内网主机，需要手动添加路由：

```
# VPN client 添加内网网段路由，设置为虚拟网络设备 tun0
sudo route add -net 172.17.0.0/24 tun0
```

此时 VPN 配置完成，内网主机和 VPN client 相互连通：

[![](https://p4.ssl.qhimg.com/t01a529cb2802bce2fb.png)](https://p4.ssl.qhimg.com/t01a529cb2802bce2fb.png)

9.内网主机访问以及验证

### <a class="reference-link" name="0x05%20%E6%8B%93%E5%B1%95"></a>0x05 拓展

上文中我们使用最小实现验证了 VPN 的工作原理，但是实际场景却比这个复杂很多，这里我们简单抛出一些问题作为拓展学习。

**1.VPN作为网关？**<br>
VPN server 一般作为网关进行配置，内网主机不用进行额外配置，也可以把报文发送给 VPN server。

**2.UDP通信链路？**<br>
在 `simpletun` 中 VPN server 和 client 之间使用 TCP 进行通信，但是在实际场景一般使用 UDP 进行通信。

当使用 TCP 作为通信隧道时，并且上层应用也使用 TCP，也就是 `tcp in tcp`，当出现丢包时，上层应用的 TCP 和 VPN 通信隧道的 TCP 都会进行重传，从而通信中出现大量的重传报文，降低通信效率；如果在这种情况下，以 UDP 作为通信隧道，`tcp in udp`，丢包后将只由上层应用的 TCP 进行重传。

**3.etc**

### <a class="reference-link" name="0x06%20%E6%80%BB%E7%BB%93"></a>0x06 总结

最后感谢 rook1e@知道创宇404实验室 小伙伴同我一起学习和研究，解决了诸多问题。

本文从 VPN 原理出发，介绍了关键作用的 TUN/TAP 虚拟网络设备，并结合 `simpletun` 创建了两端的虚拟通信链路，最后配合报文转发，实现并验证了 VPN 的通信工作原理。

VPN 的实现较为简单，但涉及到各种细枝末节的网络知识；这里的最小验证，可以为我们实现更为复杂的 VPN 或基于 VPN 技术的其他项目提供参考。

References:<br>[https://zh.wikipedia.org/wiki/%E8%99%9B%E6%93%AC%E7%A7%81%E4%BA%BA%E7%B6%B2%E8%B7%AF](https://zh.wikipedia.org/wiki/%E8%99%9B%E6%93%AC%E7%A7%81%E4%BA%BA%E7%B6%B2%E8%B7%AF)<br>[https://zhaohuabing.com/post/2020-02-24-linux-taptun/](https://zhaohuabing.com/post/2020-02-24-linux-taptun/)<br>[https://www.cnblogs.com/sparkdev/p/9262825.html](https://www.cnblogs.com/sparkdev/p/9262825.html)<br>[https://serverfault.com/questions/39307/linux-ip-forwarding-for-openvpn-correct-firewall-setup](https://serverfault.com/questions/39307/linux-ip-forwarding-for-openvpn-correct-firewall-setup)<br>[https://liuyehcf.github.io/2019/08/25/OpenVPN-%E8%BD%AC%E8%BD%BD/](https://liuyehcf.github.io/2019/08/25/OpenVPN-%E8%BD%AC%E8%BD%BD/)<br>[https://yunfwe.cn/2018/05/24/2018/%E4%B8%80%E8%B5%B7%E5%8A%A8%E6%89%8B%E5%86%99%E4%B8%80%E4%B8%AAVPN/](https://yunfwe.cn/2018/05/24/2018/%E4%B8%80%E8%B5%B7%E5%8A%A8%E6%89%8B%E5%86%99%E4%B8%80%E4%B8%AAVPN/)<br>[https://github.com/gregnietsky/simpletun](https://github.com/gregnietsky/simpletun)
