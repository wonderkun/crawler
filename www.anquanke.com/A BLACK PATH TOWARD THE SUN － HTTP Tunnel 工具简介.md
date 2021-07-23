> 原文链接: https://www.anquanke.com//post/id/84384 


# A BLACK PATH TOWARD THE SUN － HTTP Tunnel 工具简介


                                阅读量   
                                **90861**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01729523f559cfe0c4.webp)](https://p5.ssl.qhimg.com/t01729523f559cfe0c4.webp)

**Part One － 简介**

NCC Group 作为老牌的代码安全审计机构，在 OpenSSL HeartBleed（心脏出血漏洞）爆发之后为 OpenSSL 提供代码安全性的审计服务。同时他们在 Github 上也提供很多开源的工具和解决方案，从 [NCC Group 主页](https://github.com/nccgroup)可以看到很多超过 100+ star 的项目，而在最近 Black Hat US 的 Arsenal 展区他们带来了新的开源项目 [A Black Path Toward The Sun](https://github.com/nccgroup/ABPTTS) （ABPTTS），一款用以在复杂网络环境下通过被控制的 Web 应用服务器打通 HTTP Tunnel 建立网络连接的工具。<br>

在 ABPTTS 出现之前，已经有了 [netcat](http://netcat.sourceforge.net/)（TCP 端口转发）、[httptunnel](http://http-tunnel.sourceforge.net/)（TCP – over – HTTP）、 [tunna](https://github.com/SECFORCE/Tunna) （HTTP Tunnel）、[reGeorg](https://github.com/sensepost/reGeorg)（Socks5）等类似的网络工具，而 NCC Group 开发 ABPTTS 的目的将这些工具各自的优秀之处结合起来并简化成一个工具。 ABPTTS 主要针对的使用情况有两种：
<li>
在渗透过程中渗透者（下文简称：A）不能和 Web 服务器建立除了 HTTP  之外的其他类型连接。举个例子：A 从应用层控制了 Web 服务器，可以访问 Web 服务器的 TCP 的 443 端口并建立连接，但是其他类型的连接不能通过防火墙。
</li>
<li>
A 虽然可以对被控制的 Web 服务器发起非 HTTP 协议之外的请求，并且这些请求或许可以通过防火墙抵达 Web 服务器， 但是 Web 服务器向外发起的只有 HTTP 连接可以直接通过防火墙。举个例子：A 想 SSH 登陆到 目标服务器，但是该 SSH 协议需要通过网络中部署的 TLS – Inspector，而 TLS – Inspector 会拒绝其他协议企图建立隧道的请求，因此 A 并没有办法直接建立起和 Web 服务器之间的 SSH 隧道。
</li>
**Part Two － 举个********[![](https://p5.ssl.qhimg.com/t01cf227489f9813807.webp)](https://p5.ssl.qhimg.com/t01cf227489f9813807.webp)**

**现在我们假设一个真实的场景如下：**
<li>
A 发现了一个可以直接 Getshell 任意文件上传，目标 Web 服务器使用的是 Apache Tomcat。
</li>
<li>
Web 服务器处于公网，A 可以直接访问，但是除了 HTTP 连接之外的其他连接都被防火墙、路由器 ACL 表、负载均衡等过滤。
</li>
<li>
Web 服务器所有协议的请求都需要经过上述防火墙、路由器 ACL 表等过滤，不能和外网建立任何直接连接。
</li>
<li>
Web 服务器不向外网的 DNS 服务器发起 DNS 查询。
</li>
第二点使 A 没办法向目标服务器建立任何直连 Shell，而第三点则让 A 没办法和目标服务器建立反向 Shell，第四点则使 A 没办法和目标服务器建立 DNS 隧道。

在这样的复杂网络环境下如果不建立 HTTP 隧道，那么 A 只能通过 Webshell 获得的非（半）交互式 Shell 来逐条地执行命令，这样极为不便并且很多需要交互的软件不能运行，更不用说将 Web 服务器作为跳板使用 RDP 连接内网其他主机了。

这个时候 A 就可以通过 ABPTTS 建立起一个 HTTP Tunnel，而通过这个 HTTP Tunnel 攻击者可以直接访问到目标服务器所能访问到的内容，因为 A 和目标服务器通信是通过 HTTP Tunnel 符合防火墙等策略，能够通过防火墙等的过滤。

使用 ABPTTS 建立 HTTP Tunnel 在客户端和服务端都需要进行特定操作：
<li>
A 在本机运行一个可以将发往目标服务器的 TCP 报文转换成特定格式 HTTP 请求的 Python 脚本，然后再将该 HTTP 请求发送给目标服务器。
</li>
<li>
A 在目标服务器上传一个 JSP 脚本文件（当前环境为 Tomcat），这个脚本文件可以将 A 发起的 HTTP 请求还原成原 TCP 报文，并根据报文建立连接，将连接产生的响应 TCP 报文又重新转换成 HTTP 响应并通过 Web 应用返回给 A。
</li>
**具体步骤如下：**

1.A 在本机执行

```
python abpttsfactory.py -o tomcat_walkthrough
```

将会看到如下输出：

```
[2016-08-10 10:53:34.839592] ---===[[[ A Black Path Toward The Sun ]]]===---[2016-08-10 10:53:34.839674]    --==[[        -  Factory  -        ]]==--[2016-08-10 10:53:34.839706]             Ben Lincoln, NCC Group[2016-08-10 10:53:34.839721]            Version 1.0 - 2016-07-30[2016-08-10 10:53:34.841099] Output files will be created in "~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough"[2016-08-10 10:53:34.841121] Client-side configuration file will be written as "~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough/config.txt"[2016-08-10 10:53:34.841137] Using "~/Desktop/Pentest/Python/ABPTTS/data/american-english-lowercase-4-64.txt" as a wordlist file[2016-08-10 10:53:34.849013] Created client configuration file "~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough/config.txt"[2016-08-10 10:53:34.851994] Created server file "~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough/abptts.jsp"[2016-08-10 10:53:34.853073] Created server file "~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough/abptts.aspx"[2016-08-10 10:53:34.853882] Created server file "~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough/war/WEB-INF/web.xml"[2016-08-10 10:53:34.854348] Created server file "~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough/war/META-INF/MANIFEST.MF"[2016-08-10 10:53:34.855520] Prebuilt JSP WAR file: ~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough/DroopyWhimsical.war[2016-08-10 10:53:34.855541] Unpacked WAR file contents: ~/Desktop/Pentest/Python/ABPTTS/tomcat_walthrough/war
```

可以看到在当前目录下生成了一个 tomcat_walkthrough 文件夹，而文件夹内有所有 ABPTTTS 支持的服务端脚本（JSP、AWAR、ASPX等，但是暂不支持 PHP）和对应的配置文件如下所示。



[![](https://p0.ssl.qhimg.com/t010325e28dad8a2548.webp)](https://p0.ssl.qhimg.com/t010325e28dad8a2548.webp)

2.根据 Web 服务器的类型选择对应的服务端脚本并上传到 Web 服务器上，本例中则使用 JSP 脚本，上传到服务器后直接访问会出现如下界面，类似一串随机的英文 ＋ 数字，这就是服务端脚本对信息进行加密之后的结果，加解密方法具体可以参考 abptts.jsp 和 abpttsclient.py 中的代码。因为每次通过 abpttsfactory.py 产生的通信密钥是随机的，所以访问不同的 abptts.jsp 得到的字符串也都会不同。



[![](https://p0.ssl.qhimg.com/t0122d40f548d35d0d7.webp)](https://p0.ssl.qhimg.com/t0122d40f548d35d0d7.webp)

3.看到上述字符串后可以确定服务端脚本正常工作，A 这时可以在本机运行



```
python abttsclient.py -c tomcat_walkthrough/config.txt -u http://x.x.x.x:8080/abptts.jsp -f 127.0.0.1:22222/127.0.0.1:22
```

这里 －u 指定对应服务端脚本的 URL；－f 指定对应的映射关系，可以抽象为 LOCAL_NETWORK_IP:LOCAL_PORT/REMOTE_NETWORK_IP:REMOTE_PORT。－c 指定的对应服务端脚本的配置，config.txt 里包含 HTTP Tunnel 各项配置内容，格式如下：



```
headerNameKey:::::::x-sourcing-unisex-extollingheaderValueKey:::::::6ivKbot3qLL4ATtoMWrS15T2pay5Q7bz/x3i8qA=encryptionKeyHex:::::::635587d56a6ecb687cc1b20f0aec4804.........
```

运行脚本后可以看到 HTTP Tunnel 已经打通，本地 22222 端口正在等待连接。

```
[2016-08-10 11:24:53.318090] ---===[[[ A Black Path Toward The Sun ]]]===---[2016-08-10 11:24:53.318125]    --==[[       -  Client  -          ]]==--[2016-08-10 11:24:53.318131]             Ben Lincoln, NCC Group[2016-08-10 11:24:53.318137]            Version 1.0 - 2016-07-30[2016-08-10 11:24:53.319952] Listener ready to forward connections from 127.0.0.1:22222 to 127.0.0.1:22 via http://x.x.x.x:8080/abptts.jsp[2016-08-10 11:24:53.319978] Waiting for client connection to 127.0.0.1:22222
```

4. 此时便可以直接通过 HTTP Tunnel 进行 TCP-Over-HTTP 通信，建立 SSH 连接如下。

```
ssh root@127.0.0.1 -p 22222 -i ~/.ssh/xxx/id_rsa
```

运行脚本后可以看到 HTTP Tunnel 已经打通，本地 22222 端口正在等待连接。

**<br>**

**Part Three － 讨论**

其实在 ABPTTS 出现之前就已经有不少类似且好用的工具，那么为什么还要重复造轮子呢？官方手册中指出，开发 ABPTTS 的主要目标有如下几个：
<li>
让工具的部署需要尽可能的简单 － 在服务器上增加部分依赖或服务代码即可部署，或者更简单的，直接上传一个文件即可。
</li>
<li>
HTTP Tunnel 流量需要能够抵抗指纹检测 － HTTP Tunnel 中的流量需要看上去够 “随机”，每次转换后的 HTTP 流量中不能有特征字符。
</li>
<li>
配置文件的生成需要尽可能的自动化 － 往往使用这类的软件，因为需要对转换后的 HTTP 流量进行加密，所以往往配置文件中需要配置各种各样的内容，如：AES 密钥、客户端 Token、伪造请求头等等，而且这些配置文件的内容往往是使用者并不真正关心的，也不会去对他们进行修改，所以配置文件需要可以自动生成。
</li>
<li>
HTTP Tunnel 流量需要进行加密 － 很多协议本身对传输的敏感数据不进行加密，如果不加密再流入 HTTP Tunnel 中那么很可能导致信息泄漏或者是指纹明显，ABPTTS 最后选择了对流量进行 AES－128 非对称方式进行加密。
</li>
<li>
可以多个客户端共用一个 HTTP Tunnel 服务端 － 前文有说到往往为了进入复杂网络环境需要占用一整个窗口来进行交互操作，而这种情况下往往需要多个客户端窗口，在可以共用一个 HTTP Tunnel 服务端的情况下，减少了使用者需要进行的操作。
</li>
顺道一提，由于 HTTP Tunnel 确实不是一项新的技术之前也有类似成形的项目，使用的比较多的有 Tunna 和 HTTPTunnel 这两个，试着了解了一下这两个项目，下面做出一些对比：

[Tunna](https://github.com/SECFORCE/Tunna)
<li>
优点：支持 aspx／jsp／php 三种类型的服务端脚本，部署方便；客户端脚本没有使用第三方库纯净 Python 可以运行。
</li>
<li>
缺点：（太）容易掉线，连接不稳定，更不用说多客户端共用一个 Tunnel 服务端；对流量没有加密，很容易被 IDS／IPS／WAF 等检测到或者是泄漏敏感信息；没有配置文件；不能自定义 HTTP Tunnel 返回页面模版。
</li>
[HTTPTunnel](http://http-tunnel.sourceforge.net/)
<li>
优点：可以多个 Client 共用一个 Server；配置简单，可以通过 Web GUI 进行配置；不仅支持 HTTP Tunnel 还支持 SOCKS4（5）；流量加密和压缩，提高传输效率；干扰检测。
</li>
<li>
缺点：服务端只支持 Perl 、PHP，客户端只支持 Perl，条件比较苛刻；年代过于久远。
</li>
上述这两个项目均已经停止更新，Tunna 上次更新在两年前而 HTTPTunnel 上次更新是 2010 年。ABPTTS 项目在 Github 开源之后初步了解体验了一下，基本上述的内容基本都已经实现，下面也进行相对应的总结。

[ABPTTS](https://github.com/nccgroup/abptts)
<li>
优点：目前是最新的，特征暂时没有进入各大杀软的指纹库，并且会持续更新；配置简单，会自动根据当前项目生成配置文件；服务端支持或将会支持大部分主流语言的脚本文件和部署包（ASPX／JSP／WAR／PHP／RoR／Node.js／）；流量加密传输；多个 Client 可以共用一个 Server；可以自定义 HTTP Tunnel 的响应模版进行伪装，降低被识别的可能。
</li>
<li>
缺点：配置文件修改时比较麻烦；暂不支持 PHP；客户端 Python 脚本使用了第三方库 httplib2 不能直接运行；连接有时仍然会存在不稳定的情况。
</li>
虽然 ABPTTS 在使用中仍有不足之处，但是相比之下已经有超越上述两个项目的实力，另外看了一眼他的 TODO 还是很有意思的，想深入了解的话可以在 ABPTTS 的 Git [文档](https://github.com/nccgroup/ABPTTS/blob/master/ABPTTS-Manual.pdf)查看。

文中内容如有错误，敬请斧正，欢迎交流。

最后YSRC送个福利，关注“同程安全应急响应中心”公众号，点击底部菜单，ISC含餐两日通票，仅售396元~

[![](https://p1.ssl.qhimg.com/t014dc80063dd138e40.jpg)](https://p1.ssl.qhimg.com/t014dc80063dd138e40.jpg)


