> 原文链接: https://www.anquanke.com//post/id/84824 


# 【技术分享】如何使用Nmap远程开启AppleTV


                                阅读量   
                                **143071**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://www.blackhillsinfosec.com/?p=5341](http://www.blackhillsinfosec.com/?p=5341)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01ccdb20588251ab0d.jpg)](https://p1.ssl.qhimg.com/t01ccdb20588251ab0d.jpg)



**作者：**[**secist******](http://bobao.360.cn/member/contribute?uid=1427345510)

**稿费：150RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版******](http://bobao.360.cn/contribute/index)**在线投稿**



**前言**

一天在我工作的时候，我妻子走到我办公桌前询问我，问我为什么我的电视是开着的？但是我也不知道是什么原因，虽然它就在我的办公桌旁，但我并没有去特意打开过它。我简单回顾了我当时的工作场景，当时我正在本地网络，运行着 Nmap ，进行一系列相关的扫描工作。你可能曾经听说过，使用 Nmap 扫描一定要格外小心，因为有时它们会刻意打印出它们接收到的包，这样就会导致打印机用光你的纸张。想到这里，我脑海中掠过一个大胆的猜想，会不会我的AppleTV也遭遇了类似的问题！？

通过简单的猜想，也让我找到了练习的借口和理由。我决定循着自己的想法，去探索及思考这个问题。我相信，相比起去读本书或其它什么方法，独立思考和自己发现问题并取尝试着解决，更能让我们学到东西！

<br>

**信息收集**

如果你有一台 AppleTV ，那么我们可以通过以下步骤找到它的 IP 地址：

Settings &gt; General &gt; About &gt; IP Address

这里我的 IP 地址为：192.168.10.110

还可以看到一些其它信息：

model A1625 （模型）

tvOS 9.2.2 （系统版本）

接着，我们在电脑上打开 Nmap 并使它们处在同一网段内。我们开始对其进行版本扫描：

```
nmap -sV 192.168.10.110
```

在经过了两三分钟的等待，我们可以看到扫描结果如下，共有 6 个端口处于开放状态。

[![](https://p2.ssl.qhimg.com/t018384160ca7c9655e.png)](https://p2.ssl.qhimg.com/t018384160ca7c9655e.png)

为了使结果更加可信准确，我进行了第二次同样的扫描，结果与第一次一致。因此，我可以肯定我的 AppleTV 所开放的端口信息。现在我想知道，是什么原因导致开头的那幕的？或许这里有些可以被利用的服务端口，能让我们控制 AppleTV？我能否关闭 AppleTV ？能否让它播放音乐？ 甚至说控制邻居家的 AppleTV？

<br>

**让我们看看，在扫描期间网络里都发生了些什么？**

下面我将打开两个 terminal 终端窗口，一个运行 tcpdump ,另一个运行 nmap 。利用 tcpdump 来追踪 nmap 的扫描过程，这是一个非常好的习惯！当你使用的某款工具不支持交互信息的输出时，它能让你看到其执行的过程。通过流量的可视化追踪，还能让我们避免一些错误的扫描行为。

如果你运行 tcpdump 不添加任何过滤参数，它将会返回所有标准的信息。为了使我们更加容易，区分和辨别出我们感兴趣的数据。我们可以使用过滤参数，进行数据筛选。例如：not arp 过滤 arp 数据包等。通过 -n 参数，可以关闭域名解析功能，减少我们的等待时间。如果你知道目标的 IP 地址，这将会帮我们一个大忙！

[![](https://p1.ssl.qhimg.com/t01ca233b1b325ed372.png)](https://p1.ssl.qhimg.com/t01ca233b1b325ed372.png)

以上我将抓到的数据包，进行了保存(-w appletv.pcap）。

我认为在这些数据包中肯定其中有一两个数据包是导致我 AppleTV 开启的原因。但是不幸的是，我们可以看到这里一共有将近三千个数据包，最坏的情况就是我们得从头来一一排除和查找。显然，这将浪费我们大量的时间！

[![](https://p0.ssl.qhimg.com/t01f5d37730ac4af919.png)](https://p0.ssl.qhimg.com/t01f5d37730ac4af919.png)

那么我们该如何缩小我们的范围呢？通过包的抓取我们大致可以猜到， Nmap 进行端口扫描时，也会将数据探测包，发送给那些处于关闭状态的端口。因此，我们会抓取到数量巨大的数据包。根据这个猜想，我们再来进行一次 tcpdump 的抓包，不过我们这次来指定我们所需数据包的端口，端口就使用我们最初使用 Nmap 获取的端口信息，3689, 5000, 7000, 7100, 49152, 62078。

[![](https://p4.ssl.qhimg.com/t01ce5af3791826dfbd.png)](https://p4.ssl.qhimg.com/t01ce5af3791826dfbd.png)

可以看到，数据包的数量大大减少了只有一百多个。我们用 wireshark 来打开抓取的数据包文件，并从底部最新的数据开始查找。我找到了一个看起来像是会话的连接数据：

[![](https://p3.ssl.qhimg.com/t01350d43b2a3d222db.png)](https://p3.ssl.qhimg.com/t01350d43b2a3d222db.png)

我们在该数据包上右键选择 “Follow…. TCP Stream”查看数据流内容：

[![](https://p0.ssl.qhimg.com/t01a4aee668672242d4.png)](https://p0.ssl.qhimg.com/t01a4aee668672242d4.png)

这里可以看到，它采用的是 RTSP 协议，而不是我们常见的 HTTP 协议。但是它们的语法非常相识，因此如果我知道了目标的 IP 和 端口，那么我就可以在命令行里模拟发送该数据包。在 wireshark 界面我们可以得知会话的端口为 5000。

我关闭了我的 AppleTV ，并利用 Netcat 通过 echo 命令，将数据包模拟发送给 192.168.10.110 5000 端口：

[![](https://p2.ssl.qhimg.com/t0115fddad0fb9bc3d3.png)](https://p2.ssl.qhimg.com/t0115fddad0fb9bc3d3.png)

我得到了相同的响应包，但是 AppleTV 仍处于关闭状态。因此，说明这并不是我要找的那个数据包。但有趣的是，我从一个处于关闭状态的系统那，竟能获取一个如此完整的响应包：

我们可以看到以上数据包，还发生了一次奇怪的 HTTP 请求。这看起来像是， nmap 对某些特定的系统所做出的特定响应。请求内容为：

```
GET /nice%20ports%2C/Tri%6Eity.txt%2ebak
```

 (“nice ports,/Trinity.txt.bak" 至于为什么会发送这样的一个请求，或许我们能从以下地址找到答案： [http://seclists.org/nmap-dev/2006/q2/207](http://seclists.org/nmap-dev/2006/q2/207)）。

同样我发送了以上数据请求，但结果依然令我失望，它同样不是我们想要找的请求包信息。我们接着往上找，在开头位置我们找到了两个 GET requests ，分别在两个不同的端口：

[![](https://p2.ssl.qhimg.com/t0184c8cc59e4b1a04f.png)](https://p2.ssl.qhimg.com/t0184c8cc59e4b1a04f.png)

那么我可以发送以下请求：

```
$ echo -en "GET / HTTP/1.0nn"| nc 192.168.10.110 3689
```

当我成功发送以上请求，发现我的 AppleTV 被成功的开启！就像扫描打印机导致它无限制的打印纸张一样，在某些时候扫描器总会给我们带来一些不好的影响，而不是我们所预期的结果。这并不只是一个，不起眼的数据包的简单处理。而是暴露出了 AppleTV 某些功能缺少身份验证机制，导致极易被人利用！

我在网上查询了有关此端口的信息，发现这个[[非官方的 Airplay 协议规范]](https://nto.github.io/AirPlay.html)，它解释了一些我所看到的，并提出了进一步研究思路。如果你感兴趣的话，可以去尝试阅读并学习它！

[![](https://p5.ssl.qhimg.com/t0104910999658838f6.jpg)](https://p5.ssl.qhimg.com/t0104910999658838f6.jpg)[![](https://p2.ssl.qhimg.com/t0114912868ee40ef88.jpg)](https://p2.ssl.qhimg.com/t0114912868ee40ef88.jpg)
