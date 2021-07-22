> 原文链接: https://www.anquanke.com//post/id/231424 


# 内网渗透代理之frp的应用与改造（一）


                                阅读量   
                                **293546**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0156a9666ab32c52db.jpg)](https://p0.ssl.qhimg.com/t0156a9666ab32c52db.jpg)



## 0x0 前言

在内网渗透中,通常为了团队协作和代理的稳定性，我会选择一个合适且持久的沦陷主机来通过docker一键搭建OpenVPN，但是对于通过钓鱼等方式获取到window工作机器，用来搭建OpenVPN显然是不太方便(个人觉得过于笨重,安装麻烦且容易被发现),所以当时自己就在网上物色一些比较轻便、稳定、高速且支持socks代理的工具来满足自己的场景需求。



## 0x1 前置知识

### <a class="reference-link" name="0x1.1%20socks%20%E5%8D%8F%E8%AE%AE"></a>0x1.1 socks 协议

> socks是一种网络传输协议,主要用于客户端与外网服务器之间通讯的中间传递。SOCKS是”SOCKetS”的缩写。
当[防火墙](https://zh.wikipedia.org/wiki/%E9%98%B2%E7%81%AB%E5%A2%99_(%E7%BD%91%E7%BB%9C))后的客户端要访问外部的服务器时，就跟SOCKS[代理服务器](https://zh.wikipedia.org/wiki/%E4%BB%A3%E7%90%86%E6%9C%8D%E5%8A%A1%E5%99%A8)连接。这个代理服务器控制客户端访问外网的资格，允许的话，就将客户端的请求发往外部的服务器。
这个协议最初由David Koblas开发，而后由NEC的Ying-Da Lee将其扩展到SOCKS4。最新协议是SOCKS5，与前一版本相比，增加支持[UDP](https://zh.wikipedia.org/wiki/%E7%94%A8%E6%88%B7%E6%95%B0%E6%8D%AE%E6%8A%A5%E5%8D%8F%E8%AE%AE)、验证，以及[IPv6](https://zh.wikipedia.org/wiki/IPv6)。
根据[OSI模型](https://zh.wikipedia.org/wiki/OSI%E6%A8%A1%E5%9E%8B)，SOCKS是[会话层](https://zh.wikipedia.org/wiki/%E4%BC%9A%E8%AF%9D%E5%B1%82)的协议，位于[表示层](https://zh.wikipedia.org/wiki/%E8%A1%A8%E7%A4%BA%E5%B1%82)与[传输层](https://zh.wikipedia.org/wiki/%E4%BC%A0%E8%BE%93%E5%B1%82)之间。
SOCKS协议不提供[加密](https://zh.wikipedia.org/wiki/%E5%8A%A0%E5%AF%86)

可以简单理解为socks是一种代理协议，处于中介的角色，被大多数软件所支持，支持多种协议的数据转发。

### <a class="reference-link" name="0x1.2%20kcp%E5%8D%8F%E8%AE%AE"></a>0x1.2 kcp协议

> <p>KCP是一个快速可靠协议，能以比 TCP浪费10%-20%的带宽的代价，换取平均延迟降低 30%-40%，且最大延迟降低三倍的传输效果。纯算法实现，并不负责底层协议（如UDP）的收发，需要使用者自己定义下层数据的发送方式，以 callback的方式提供给 KCP。连时钟都需要外部传递进来，内部不会有任何一次系统调用。<br>
TCP是为流量设计的（每秒内可以传输多少KB的数据），讲究的是充分利用带宽。而 KCP是为流速设计的（单个数据从一端发送到一端需要多少时间），以10%-20%带宽浪费的代价换取了比 TCP快30%-40%的传输速度。</p>

可以简单理解为基于udp的KCP协议就是在保留UDP高传输速度的同时尽可能地提高了可靠性。



## 0x2 frp的使用

通过阅读frp的[说明文档](https://github.com/fatedier/frp/blob/master/README_zh.md),可以知道frp支持相当多的功能,有兴趣的可以自行挖掘一下。

这里只说明下自己在内网渗透中最常使用的配置,主要涉及到稳定性和加密两个点。

### <a class="reference-link" name="0x2.1%20kcp%E6%A8%A1%E5%BC%8F%E5%AF%B9%E6%AF%94"></a>0x2.1 kcp模式对比

在网络环境比较差的时候，使用kcp能够有效提高传输效率。

**(1) 没有开启kcp模式**

`frps.ini`

```
[common]
bind_addr = 0.0.0.0
bind_port = 7000

# IP 与 bind_addr 默认相同，可以不设置
# dashboard_addr = 0.0.0.0
# 端口必须设置，只有设置web页面才生效
dashboard_port = 7500
# 用户密码保平安
dashboard_user = xq17
dashboard_pwd = admin888

# 允许客户端绑定的端口
#allow_ports = 40000-50000
```

`frpc.ini`

```
[common]
server_addr = 101.200.157.195
server_port = 7000

[plugin_socks5]
type = tcp
remote_port = 6005
plugin = socks5
plugin_user = abc
plugin_passwd = abc
```

[![](https://p1.ssl.qhimg.com/t01baa0295e90280b19.png)](https://p1.ssl.qhimg.com/t01baa0295e90280b19.png)

**(2) 开启KCP**

`frps.ini` [common] 下添加 `kcp_bind_port`参数即可

```
[common]
bind_addr = 0.0.0.0
bind_port = 7000
# 开启kcp模式
kcp_bind_port = 7000

# IP 与 bind_addr 默认相同，可以不设置
# dashboard_addr = 0.0.0.0
# 端口必须设置，只有设置web页面才生效
dashboard_port = 7500
# 用户密码保平安
dashboard_user = xq17
dashboard_pwd = admin888

# 允许客户端绑定的端口
#allow_ports = 40000-50000
```

`frpc.ini` [common]下添加`protocol=kcp`即可

```
[common]
server_addr = 101.200.157.195
# kcp监听的端口
server_port = 7000
protocol = kcp

[plugin_socks5]
type = tcp
remote_port = 6005
plugin = socks5
plugin_user = abc
plugin_passwd = abc
```

[![](https://p0.ssl.qhimg.com/t0107bf7627f89ab729.png)](https://p0.ssl.qhimg.com/t0107bf7627f89ab729.png)

可以看到无论在下载还是延迟上都有了很大的优化,由于支持端口复用, 就算环境不支持kcp也不会出错，所以这个选项建议默认开启。

### <a class="reference-link" name="0x2.2%20TLS%20%E5%8A%A0%E5%AF%86%E6%A8%A1%E5%BC%8F%E5%AF%B9%E6%AF%94"></a>0x2.2 TLS 加密模式对比

从 v0.25.0 版本开始 frpc 和 frps 之间支持通过 TLS 协议加密传输。通过在 `frpc.ini` 的 `common` 中配置 `tls_enable = true` 来启用此功能，性更高。

为了端口复用，frp 建立 TLS 连接的第一个字节为 0x17。

通过将 frps.ini 的 `[common]` 中 `tls_only` 设置为 true，可以强制 frps 只接受 TLS 连接。

**注意: 启用此功能后除 xtcp 外，不需要再设置 use_encryption。**

**(1) 没有开启TLS加密**

当没有开启TLS加密的时候,我们可以用WireShark抓包分析一下流量。

规则: `ip.dst == 101.200.157.195 || tcp.port == 7000 || udp.port == 7000`

由于开启了KCP所以抓到的包走的是UDP协议。

[![](https://p4.ssl.qhimg.com/t0162c4dbb49667a147.png)](https://p4.ssl.qhimg.com/t0162c4dbb49667a147.png)

通过观测udp stream, 可以看到:

[![](https://p4.ssl.qhimg.com/t0139ca04e44e2d5eb1.png)](https://p4.ssl.qhimg.com/t0139ca04e44e2d5eb1.png)

前面4次udp数据报可以看到client和Server进行版本、任务信息的校鉴过程。

我们尝试使用socks5的插件请求[https://www.speedtest.cn/](https://www.speedtest.cn/) 这个网站进行测速,然后观察wireshark的流量情况。

查看Firefox 使用socks5的流量规则: `tcp.port == 6006`

[![](https://p1.ssl.qhimg.com/t01dcab44a4876f8df4.png)](https://p1.ssl.qhimg.com/t01dcab44a4876f8df4.png)

可以看到的确进行了socks的用户和密码检验，这里不知道是不是客户端的原因, wireshark没识别出socks5的协议，导致我们不能很直观地看出对应字段的表示的内容。

直接跟踪流

[![](https://p5.ssl.qhimg.com/t016a7b5508439eead0.png)](https://p5.ssl.qhimg.com/t016a7b5508439eead0.png)

可以看到信息发送和返回都是明文传输的,这个其实关系不大,因为这些信息是暴露在我们这边,我们再分析下client端的数据交互。

[![](https://p2.ssl.qhimg.com/t014ce87e6db0caa933.png)](https://p2.ssl.qhimg.com/t014ce87e6db0caa933.png)

可以看到前面几个包都是再进行一些数据交换，其中出现了很多特定特征,我们可以跟踪udp stream

[![](https://p5.ssl.qhimg.com/t01272a35d1215da944.png)](https://p5.ssl.qhimg.com/t01272a35d1215da944.png)

其中数据也没有进行加密

[![](https://p1.ssl.qhimg.com/t01f61a35d9a5f39dcc.png)](https://p1.ssl.qhimg.com/t01f61a35d9a5f39dcc.png)

在这种代理模式下，是很容易被拦截的，数据传输安全得不到保证。

**(2) 开启TLS加密**

只需在`frpc.ini` 的 [common] 中配置`tls_enable = true` 来启用此功能

```
[common]
server_addr = 101.200.157.195
server_port = 7000
protocol = kcp
tls_enable = true


[plugin_socks5]
type = tcp
remote_port = 6006
plugin = socks5
plugin_user = abc
plugin_passwd = abc
```

我们再通过wireshark看下流量的情况:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0112d3d73e5e4f653b.png)

可以看到整个流量过程都已经被加密了。

[![](https://p4.ssl.qhimg.com/t019e67d588ffe7ef5e.png)](https://p4.ssl.qhimg.com/t019e67d588ffe7ef5e.png)

网络传输的质量保持也良好,不过出现了比较多EOF的错误,不知道是否会对某些情况产生影响。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014c3cd79920b1b529.png)

### <a class="reference-link" name="0x2.3%20%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1"></a>0x2.3 负载均衡

如果我们同时拿到了多台内网机器,为了进一步提高代理的稳定性，同时也希望避免沦陷主机资源负载过高等异常情况。我们可以考虑使用frp的负载均衡的配置来分担流量,同时开启frp自带的健康检查，避免出现服务单点故障，从而实现高可用架构的稳定代理。

查阅相关文档，得知其用法:

[![](https://p1.ssl.qhimg.com/t01e358e2d02c0df5c8.png)](https://p1.ssl.qhimg.com/t01e358e2d02c0df5c8.png)

server: `frps.ini`

```
[common]
bind_addr = 0.0.0.0
bind_port = 7000
kcp_bind_port = 7000


# IP 与 bind_addr 默认相同，可以不设置
# dashboard_addr = 0.0.0.0
# ，只有设置web页面才生效
dashboard_port = 7500
# 用户密码保平安
dashboard_user = xq17
dashboard_pwd = admin888
```

client1: `frpc.ini`

```
[common]
server_addr = 101.200.157.195
# kcp监听的端口
server_port = 7000
protocol = kcp

[client_socks5_one]
type = tcp
remote_port = 6005
plugin = socks5
# 启用健康检查，类型为 tcp
health_check_type = tcp
# 建立连接超时时间为 3 秒
health_check_timeout_s = 3
# 连续 3 次检查失败，此 proxy 会被摘除
health_check_max_failed = 3
# 每隔 10 秒进行一次健康检查
health_check_interval_s = 10

# 负载均衡配置客户组
group = load_balance
group_key = 123
```

client2: `frpc.ini`

```
[common]
server_addr = 101.200.157.195
# kcp监听的端口
server_port = 7000
protocol = kcp

[client_socks5_two]
type = tcp
remote_port = 6005
plugin = socks5
# 启用健康检查，类型为 tcp
health_check_type = tcp
# 建立连接超时时间为 3 秒
health_check_timeout_s = 3
# 连续 3 次检查失败，此 proxy 会被摘除
health_check_max_failed = 3
# 每隔 10 秒进行一次健康检查
health_check_interval_s = 10

# 负载均衡配置客户组
group = load_balance
group_key = 123
```

[![](https://p0.ssl.qhimg.com/t011011581b0ae97c60.png)](https://p0.ssl.qhimg.com/t011011581b0ae97c60.png)

[![](https://p4.ssl.qhimg.com/t01191aa0ca8b1a426f.png)](https://p4.ssl.qhimg.com/t01191aa0ca8b1a426f.png)

可以看到流量被平均分配到了两个负载的机器上:

[![](https://p4.ssl.qhimg.com/t01ba531052963697db.png)](https://p4.ssl.qhimg.com/t01ba531052963697db.png)



## 0x3 frp client执行流程分析

这里主要分析客户端: `frp/cmd/frpc/main.go`

从入口开始跟起:

[![](https://p0.ssl.qhimg.com/t01463686e7207ba49a.png)](https://p0.ssl.qhimg.com/t01463686e7207ba49a.png)

可以发现处理参数使用的是 cobra库

[![](https://p4.ssl.qhimg.com/t015998f38510461e8a.png)](https://p4.ssl.qhimg.com/t015998f38510461e8a.png)

在这里定义了持久的参数,其中`cfgFile`默认值是`./frpc.ini`, 通过阅读文档,RunE 获取函数后对函数进行操作的函数

[![](https://p5.ssl.qhimg.com/t01ce0b340d45ed7019.png)](https://p5.ssl.qhimg.com/t01ce0b340d45ed7019.png)

跟进`runClient`

[![](https://p1.ssl.qhimg.com/t01ca6ce010d94a512e.png)](https://p1.ssl.qhimg.com/t01ca6ce010d94a512e.png)

首先加载配置文件内容给`content`,然后`parseClientCommonCfg`对配置文件内容进行解析,我们看下解析的规则

[![](https://p0.ssl.qhimg.com/t01de4aa30e65f1c65a.png)](https://p0.ssl.qhimg.com/t01de4aa30e65f1c65a.png)

跳过一些中间函数

[![](https://p3.ssl.qhimg.com/t010d671094b7e3f44f.png)](https://p3.ssl.qhimg.com/t010d671094b7e3f44f.png)

[![](https://p5.ssl.qhimg.com/t011eb8b593df310a18.png)](https://p5.ssl.qhimg.com/t011eb8b593df310a18.png)

可以看到配置文件中的内容安装key装进了`cfg`里面,后面这句就是加载自己定义配置

`pxyCfgs, visitorCfgs, err := config.LoadAllConfFromIni(cfg.User, content, cfg.Start)`

[![](https://p4.ssl.qhimg.com/t0128726b2b63bb2fa6.png)](https://p4.ssl.qhimg.com/t0128726b2b63bb2fa6.png)

原理差不多,也是只提取定义好的key然后装进`cfg`

[![](https://p3.ssl.qhimg.com/t01c5dd1cc598d835ab.png)](https://p3.ssl.qhimg.com/t01c5dd1cc598d835ab.png)

解析完所有配置文件到cfg,真正开始启动服务

`err = startService(cfg, pxyCfgs, visitorCfgs, cfgFilePath)`

其中`pxyCfgs`主要存放的内容就是我们添加的插件的配置,

[![](https://p1.ssl.qhimg.com/t01dbc016117d014b3b.png)](https://p1.ssl.qhimg.com/t01dbc016117d014b3b.png)

接着会尝试登陆到服务器,然后返回conn和session

[![](https://p5.ssl.qhimg.com/t01213d73628c1308f3.png)](https://p5.ssl.qhimg.com/t01213d73628c1308f3.png)

[![](https://p5.ssl.qhimg.com/t018942f42f758ffcb4.png)](https://p5.ssl.qhimg.com/t018942f42f758ffcb4.png)

然后开始进去`ConnectServerByProxyWithTLS`-&gt;`ConnectServerByProxy`

和服务器尝试建立连接:

[![](https://p0.ssl.qhimg.com/t016de1c66dbc64c164.png)](https://p0.ssl.qhimg.com/t016de1c66dbc64c164.png)

这里就开始建立tcp的连接:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0106a697ee81036f30.png)

然后用建立好的连接，发了个0x17的字符，代表等下要建立tls加密传输,然后进入了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e6c465c95f77bb71.png)

然后tls.client重新封装的net.conn为tls.conn,作为后续的tls交互使用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0150e9348678605ec8.png)

然后后面就是利用fmux继续封装，用来实现多路复用,返回conn=stream,用来后续的链接

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01704328c4a7b30a08.png)

…因为有链接时超时的限制，这里我们直接跟下一个关键断点.

[![](https://p5.ssl.qhimg.com/t0137ee164d1133ba9e.png)](https://p5.ssl.qhimg.com/t0137ee164d1133ba9e.png)

这里主要是yamux建立应用流通道时基于tcp的交互。

最后发送登录信息给服务端完成:

[![](https://p5.ssl.qhimg.com/t016a64252386da121a.png)](https://p5.ssl.qhimg.com/t016a64252386da121a.png)


