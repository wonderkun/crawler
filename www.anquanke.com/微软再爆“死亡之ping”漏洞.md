> 原文链接: https://www.anquanke.com//post/id/219503 


# 微软再爆“死亡之ping”漏洞


                                阅读量   
                                **179803**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01fd5a033cf0883806.jpg)](https://p1.ssl.qhimg.com/t01fd5a033cf0883806.jpg)



微软将在10月的补丁周二发布中再次发布大量安全修补程序，其中11个被微软评为”关键”。但是，在修补的漏洞中，有两个漏洞比这些漏洞更突出：CVE-2020-16898和 CVE-2020-16899。这些漏洞（由 Windows的 TCP/IP 驱动程序中的 Bug 引起）堪比2013 年 Windows 中修复的”死亡ping”漏洞。通过精心制作的数据包使拒绝服务和潜在的远程代码执行成为可能。

tcpip.sys 中的漏洞是驱动程序分析 ICMP 消息的逻辑错误，可以使用包含递归 DNS 服务器 （RDNSS） 选项的精心制作的 IPv6 路由器播发数据包远程触发。RDNSS 选项通常包含一个或多个递归 DNS 服务器的 IPv6 地址列表。

[![](https://p3.ssl.qhimg.com/t01f6227fb24de3bfcf.png)](https://p3.ssl.qhimg.com/t01f6227fb24de3bfcf.png)

tcpip.sys 存在逻辑缺陷，可以通过创建包含比预期更多的数据的路由器播发数据包来利用该缺陷，这会导致驱动程序在其内存堆栈上将数据字节数超过驱动程序代码中提供的数据字节数，从而导致缓冲区溢出。

POC 视频：.

<video style="width: 100%; height: auto;" src="https://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/MGI3OGVxYWFzYWFhY3FhaGVrNGdsYnB2YWpnZGJlc2FhY2lhLmYxMDAwMi5tcDQ=" controls="controls" width="300" height="150">﻿您的浏览器不支持video标签 </video>



开发一个”蓝屏死亡”的DoS攻击是可以的。但是实现远程代码执行（RCE）比较困难。

首先，TcpIp.sys 使用 GS 标志编译，这可以防止典型的堆栈溢出直接控制返回地址。

[![](https://p1.ssl.qhimg.com/t01d2baf8d5b0af94cc.png)](https://p1.ssl.qhimg.com/t01d2baf8d5b0af94cc.png)

Stack Cookie 也称为stackcanary，是加载时产生的随机值。其值是 XOR’d 与堆栈指针，使得它极难可靠地预测。

[![](https://p2.ssl.qhimg.com/t01aad4cbbed676d3eb.png)](https://p2.ssl.qhimg.com/t01aad4cbbed676d3eb.png)

RCE 漏洞利用的第二个困难是内核地址空间布局随机化 （kASLR）。即使有可能可以可靠地预测stack canary落在系统外壳在用户模式下还需要正确（并再次远程）确定Windows内核的基本地址。



## 针对此漏洞的防护

此处提供一个Lua脚本用于此漏洞的检测可以集成到IDS中。

```
function init(args)

   local needs = `{``}`

   needs["packet"] = tostring(true)

   return needs

end

 

function match(args)

   local packet = args["packet"]

   if packet == nil then

       print("Packet buffer empty! Aborting...")

       return 0

   end

 

   -- SCPacketPayload starts at byte 5 of the ICMPv6 header, so we use thepacket buffer instead.

   local buffer = SCPacketPayload()

   local search_str = string.sub(buffer, 1, 8)

   local s, _ = string.find(packet, search_str)

   local offset = s - 4

 

   -- Only inspect Router Advertisement (Type = 134) ICMPv6 packets.

   local type = tonumber(packet:byte(offset))

   if type ~= 134 then

       return 0

   end

 

   -- ICMPv6 Options start at byte 17 of the ICMPv6 payload.

   offset = offset + 16

 

   -- Continue looking for Options until we've run out of packet bytes.

   while offset &lt; string.len(packet) do

 

       -- We're only interested in RDNSS Options (Type = 25).

       local option_type = tonumber(packet:byte(offset))

 

       -- The Option's Length field counts in 8-byte increments, so Length = 2means the Option is 16 bytes long.

       offset = offset + 1

       local length = tonumber(packet:byte(offset))

 

       -- The vulnerability is exercised when an even length value is in anRDNSS Option.

       if option_type == 25 and length &gt; 3 and (length % 2) == 0 then

           return 1

 

       -- Otherwise, move to the start of the next Option, if present.

       else

           offset = offset + (length * 8) - 1

       end

   end

 

   return 0

end
```



## 如何防御：

1、如果不使用，请禁用 IPv6

2、netsh int ipv6set int int=*INTERFACENUMBER* rabaseddnsconfig=disable



## 参考链接：

[https://news.sophos.com/en-us/2020/10/13/top-reason-to-apply-october-2020s-microsoft-patches-ping-of-death-redux/](https://news.sophos.com/en-us/2020/10/13/top-reason-to-apply-october-2020s-microsoft-patches-ping-of-death-redux/)

[https://github.com/advanced-threat-research/CVE-2020-16898](https://github.com/advanced-threat-research/CVE-2020-16898)
