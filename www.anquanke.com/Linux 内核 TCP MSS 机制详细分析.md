> 原文链接: https://www.anquanke.com//post/id/181278 


# Linux 内核 TCP MSS 机制详细分析


                                阅读量   
                                **197448**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01cb7c2f42e87a472b.jpg)](https://p3.ssl.qhimg.com/t01cb7c2f42e87a472b.jpg)



作者：Hcamael@知道创宇 404 实验室

## 前言

上周Linux内核修复了4个CVE漏洞[1]，其中的CVE-2019-11477感觉是一个很厉害的Dos漏洞，不过因为有其他事打断，所以进展的速度比较慢，这期间网上已经有相关的分析文章了。[2][3]

而我在尝试复现CVE-2019-11477漏洞的过程中，在第一步设置MSS的问题上就遇到问题了，无法达到预期效果，但是目前公开的分析文章却没对该部分内容进行详细分析。所以本文将通过Linux内核源码对TCP的MSS机制进行详细分析。



## 测试环境

**1. 存在漏洞的靶机**

操作系统版本：Ubuntu 18.04

内核版本：4.15.0-20-generic

地址：192.168.11.112

内核源码：

```
$ sudo apt install linux-source-4.15.0
$ ls /usr/src/linux-source-4.15.0.tar.bz2
```

带符号的内核：

```
$ cat /etc/apt/sources.list.d/ddebs.list
deb http://ddebs.ubuntu.com/ bionic main
deb http://ddebs.ubuntu.com/ bionic-updates main
$ sudo apt install linux-image-4.15.0-20-generic-dbgsym
$ ls /usr/lib/debug/boot/vmlinux-4.15.0-20-generic
```

关闭内核地址随机化（KALSR）：

```
# 内核是通过grup启动的，所以在grup配置文件中，内核启动参数里加上nokaslr 
$ cat /etc/default/grub |grep -v "#" | grep CMDLI
GRUB_CMDLINE_LINUX_DEFAULT="nokaslr"
GRUB_CMDLINE_LINUX=""
$ sudo update-grub
```

装一个nginx，供测试：

```
$ sudo apt install nginx
```

**2. 宿主机**

操作系统：MacOS

Wireshark：抓流量

虚拟机：VMware Fusion 11

调试Linux虚拟机：

```
$ cat ubuntu_18.04_server_test.vmx|grep debug
debugStub.listen.guest64 = "1"
```

编译gdb：

```
$ ./configure --build=x86_64-apple-darwin --target=x86_64-linux --with-python=/usr/local/bin/python3
$ make
$ sudo make install
$ cat .zshrc|grep gdb
alias gdb="~/Documents/gdb_8.3/gdb/gdb"
```

gdb进行远程调试：

```
$ gdb vmlinux-4.15.0-20-generic
$ cat ~/.gdbinit
define gef
source ~/.gdbinit-gef.py
end

define kernel
target remote :8864
end
```

**3. 攻击机器**

自己日常使用的Linux设备就好了

地址：192.168.11.111

日常习惯使用Python的，需要装个scapy构造自定义TCP包



## 自定义SYN的MSS选项

有三种方法可以设置TCP SYN包的MSS值

**1. iptable**

```
# 添加规则
$ sudo iptables -I OUTPUT -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 48
# 删除
$ sudo iptables -D OUTPUT -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 48
```

**2. route**

```
# 查看路由信息
$ route -ne
$ ip route show
192.168.11.0/24 dev ens33 proto kernel scope link src 192.168.11.111 metric 100
# 修改路由表
$ sudo ip route change 192.168.11.0/24 dev ens33 proto kernel scope link src 192.168.11.111 metric 100 advmss 48
# 修改路由表信息就是在上面show的结果后面加上 advmss 8
```

**3. 直接发包设置**

PS：使用scapy发送自定义TCP包需要ROOT权限

```
from scapy.all import *

ip = IP(dst="192.168.11.112")
tcp = TCP(dport=80, flags="S",options=[('MSS',48),('SAckOK', '')])
```

flags选项S表示SYN，A表示ACK，SA表示SYN, ACK

scapy中TCP可设置选项表：

```
TCPOptions = (
`{` 
    0 : ("EOL",None),
    1 : ("NOP",None),
    2 : ("MSS","!H"),
    3 : ("WScale","!B"),
    4 : ("SAckOK",None),
    5 : ("SAck","!"),
    8 : ("Timestamp","!II"),
    14 : ("AltChkSum","!BH"),
    15 : ("AltChkSumOpt",None),
    25 : ("Mood","!p"),
    254 : ("Experiment","!HHHH")
`}`,
`{` 
    "EOL":0,
    "NOP":1,
    "MSS":2,
    "WScale":3,
    "SAckOK":4,
    "SAck":5,
    "Timestamp":8,
    "AltChkSum":14,
    "AltChkSumOpt":15,
    "Mood":25,
    "Experiment":254
`}`)
```

但是这个会有一个问题，在使用Python发送了一个SYN包以后，内核会自动带上一个RST包，查过资料后，发现在新版系统中，对于用户发送的未完成的TCP握手包，内核会发送RST包终止该连接，应该是为了防止进行SYN Floor攻击。解决办法是使用iptable过滤RST包：

```
$ sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -s 192.168.11.111 -j DROP
```



## 对于MSS的深入研究

关于该漏洞的细节，别的文章中已经分析过了，这里简单的提一下，该漏洞为uint16溢出：

```
tcp_gso_segs 类型为uint16
tcp_set_skb_tso_segs:
tcp_skb_pcount_set(skb, DIV_ROUND_UP(skb-&gt;len, mss_now));
skb-&gt;len的最大值为17 * 32 * 1024
mss_now的最小值为8
&gt;&gt;&gt; hex(17*32*1024//8)
'0x11000'
&gt;&gt;&gt; hex(17*32*1024//9)
'0xf1c7'
```

所以在mss_now小于等于8时，才能发生整型溢出。

深入研究的原因是因为进行了如下的测试：

攻击机器通过iptables/iproute命令将MSS值为48后，使用curl请求靶机的http服务，然后使用wireshark抓流量，发现服务器返回的http数据包的确被分割成小块，但是只小到36，离预想的8有很大的差距

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2019/06/c3b72e38-1d34-4c99-9023-172085257af8.png-w331s)

这个时候我选择通过审计源码和调试来深入研究为啥MSS无法达到我的预期值，SYN包中设置的MSS值到代码中的mss_now的过程中发生了啥？

随机进行源码审计，对发生溢出的函数tcp_set_skb_tso_segs进行回溯：

```
tcp_set_skb_tso_segs &lt;- tcp_fragment &lt;- tso_fragment &lt;- tcp_write_xmit
最后发现，传入tcp_write_xmit函数的mss_now都是通过tcp_current_mss函数进行计算的
```

随后对tcp_current_mss函数进行分析，关键代码如下：

```
# tcp_output.c
tcp_current_mss -&gt; tcp_sync_mss:
mss_now = tcp_mtu_to_mss(sk, pmtu);

tcp_mtu_to_mss:
/* Subtract TCP options size, not including SACKs */
return __tcp_mtu_to_mss(sk, pmtu) -
           (tcp_sk(sk)-&gt;tcp_header_len - sizeof(struct tcphdr));

__tcp_mtu_to_mss:
if (mss_now &lt; 48)
    mss_now = 48;
return mss_now;
```

看完这部分源码后，我们对MSS的含义就有一个深刻的理解，首先说一说TCP协议：

TCP协议包括了协议头和数据，协议头包括了固定长度的20字节和40字节的可选参数，也就是说TCP头部的最大长度为60字节，最小长度为20字节。

在__tcp_mtu_to_mss函数中的mss_now为我们SYN包中设置的MSS，从这里我们能看出MSS最小值是48，通过对TCP协议的理解和对代码的理解，可以知道SYN包中MSS的最小值48字节表示的是：TCP头可选参数最大长度40字节 + 数据最小长度8字节。

但是在代码中的mss_now表示的是数据的长度，接下来我们再看该值的计算公式。

tcphdr结构：

```
struct tcphdr `{`
    __be16  source;
    __be16  dest;
    __be32  seq;
    __be32  ack_seq;
#if defined(__LITTLE_ENDIAN_BITFIELD)
    __u16   res1:4,
        doff:4,
        fin:1,
        syn:1,
        rst:1,
        psh:1,
        ack:1,
        urg:1,
        ece:1,
        cwr:1;
#elif defined(__BIG_ENDIAN_BITFIELD)
    __u16   doff:4,
        res1:4,
        cwr:1,
        ece:1,
        urg:1,
        ack:1,
        psh:1,
        rst:1,
        syn:1,
        fin:1;
#else
#error  "Adjust your &lt;asm/byteorder.h&gt; defines"
#endif  
    __be16  window;
    __sum16 check;
    __be16  urg_ptr;
`}`;
```

该结构体为TCP头固定结构的结构体，大小为20bytes

变量tcp_sk(sk)-&gt;tcp_header_len表示的是本机发出的TCP包头部的长度。

因此我们得到的计算mss_now的公式为：SYN包设置的MSS值 – (本机发出的TCP包头部长度 – TCP头部固定的20字节长度)

所以，如果tcp_header_len的值能达到最大值60，那么mss_now就能被设置为8。那么内核代码中，有办法让tcp_header_len达到最大值长度吗？随后我们回溯该变量：

```
# tcp_output.c
tcp_connect_init:
tp-&gt;tcp_header_len = sizeof(struct tcphdr);
    if (sock_net(sk)-&gt;ipv4.sysctl_tcp_timestamps)
        tp-&gt;tcp_header_len += TCPOLEN_TSTAMP_ALIGNED;

#ifdef CONFIG_TCP_MD5SIG
    if (tp-&gt;af_specific-&gt;md5_lookup(sk, sk))
        tp-&gt;tcp_header_len += TCPOLEN_MD5SIG_ALIGNED;
#endif
```

所以在Linux 4.15内核中，在用户不干预的情况下，内核是不会发出头部大小为60字节的TCP包。这就导致了MSS无法被设置为最小值8，最终导致该漏洞无法利用。



## 总结

我们来总结一下整个流程：
1. 攻击者构造SYN包，自定义TCP头部可选参数MSS的值为48
1. 靶机（受到攻击的机器）接收到SYN请求后，把SYN包中的数据保存在内存中，返回SYN，ACK包。
1. 攻击者返回ACK包
三次握手完成

随后根据不同的服务，靶机主动向攻击者发送数据或者接收到攻击者的请求后向攻击者发送数据，这里就假设是一个nginx http服务。
1. 攻击者向靶机发送请求：GET / HTTP/1.1。
1. 靶机接收到请求后，首先计算出tcp_header_len，默认等于20字节，在内核配置sysctl_tcp_timestamps开启的情况下，增加12字节，如果编译内核的时候选择了CONFIG_TCP_MD5SIG，会再增加18字节，也就是说tcp_header_len的最大长度为50字节。
1. 随后需要计算出mss_now = 48 – 50 + 20 = 18
这里假设一下该漏洞可能利用成功的场景：有一个TCP服务，自己设定了TCP可选参数，并且设置满了40字节，那么攻击者才有可能通过构造SYN包中的MSS值来对该服务进行Dos攻击。

随后我对Linux 2.6.29至今的内核进行审计，mss_now的计算公式都一样，tcp_header_len长度也只会加上时间戳的12字节和md5值的18字节。



## 参考
1. [https://github.com/Netflix/security-bulletins/blob/master/advisories/third-party/2019-001.md](https://github.com/Netflix/security-bulletins/blob/master/advisories/third-party/2019-001.md)
1. [https://paper.seebug.org/959/](https://paper.seebug.org/959/)
1. [https://paper.seebug.org/960/](https://paper.seebug.org/960/)
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)

本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：[https://paper.seebug.org/966/](https://paper.seebug.org/966/)
