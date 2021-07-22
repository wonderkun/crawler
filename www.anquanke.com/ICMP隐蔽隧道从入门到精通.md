> 原文链接: https://www.anquanke.com//post/id/152046 


# ICMP隐蔽隧道从入门到精通


                                阅读量   
                                **226028**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t017bf5a93c878e5dbd.jpg)](https://p3.ssl.qhimg.com/t017bf5a93c878e5dbd.jpg)

## 概述

众所周知传统socket隧道已极少，tcp、upd大量被防御系统拦截，dns、icmp、http/https等难于禁止的协议（当然还有各种xx over dns/icmp/http，后续再讲）已成为黑客控制隧道的主流。<br>
本文从技术原理、实现方式、检测防御等多个维度解释隐蔽性最强的icmp隧道的相关知识，但不深入探讨编程实现，仅作为一篇科普文章，所以用了“从入门到精通”这个标题，本来就是科普(〃’▽’〃)，请大神绕过！谢谢！！



## 起源

说起icmp其实要从最早的免费上网说起。<br>
当年互联网刚刚兴起的时候，上网费是很贵的，难说一不小心上个网就能我们穷学生倾家荡产！后来聪明的同学开始研究技术，虽然我们的网络断了（不是拨号那种无法获得ip的，需要有ip），但是ping ip还是可以的，于是就利用icmp隧道将访问转发到自己的一台放置在公网代理，利用代理中转访问公网，实现免费上网，虽然速率不高，但是免费嘛。<br>[![](https://p1.ssl.qhimg.com/t014e74f4b4974b7655.png)](https://p1.ssl.qhimg.com/t014e74f4b4974b7655.png)<br>
了解了起源，知道他的由来了，我们就好奇了，这技术是怎么回事？最后为啥又成了黑客用的隐蔽隧道呢，其实正所谓技术本无罪，只是看被什么人用罢了。我们主要关注技术原理即可。



## 技术原理

怎么可以实现这种神奇的通信呢，这就要从协议这个东西的基本原理说起，打开rfc（[https://www.rfc-editor.org/search/rfc_search_detail.php）查询ping使用的icmp协议](https://www.rfc-editor.org/search/rfc_search_detail.php%EF%BC%89%E6%9F%A5%E8%AF%A2ping%E4%BD%BF%E7%94%A8%E7%9A%84icmp%E5%8D%8F%E8%AE%AE)<br>[![](https://p5.ssl.qhimg.com/t013fa9712128977d56.png)](https://p5.ssl.qhimg.com/t013fa9712128977d56.png)查看详情RFC792<br>[https://www.rfc-editor.org/info/rfc792](https://www.rfc-editor.org/info/rfc792)<br>[https://www.rfc-editor.org/rfc/rfc792.txt](https://www.rfc-editor.org/rfc/rfc792.txt)<br>
你会发现icmp协议的结构如下：<br>[![](https://p2.ssl.qhimg.com/t012750ea1bdf1f4141.png)](https://p2.ssl.qhimg.com/t012750ea1bdf1f4141.png)<br>
其中0~31是各种协议头部，那剩下的呢？当然就是data了！原本默认ping传输的是：<br>
windows系统，默认传输32bytes，内容是abcdefghijklmnopqrstuvwabcdefghi，共32bytes<br>[![](https://p0.ssl.qhimg.com/t01b1d9acbfc2e63ba5.jpg)](https://p0.ssl.qhimg.com/t01b1d9acbfc2e63ba5.jpg)linux系统，稍显复杂，默认Data传输的是48bytes，在Date之前多了一个Timestamp from icmp data头，占用8bytes,如e5 0d 44 5b 00 00 00 00（Jul 10, 2018 09:37:41.000000000 CST），详情如下：<br>
1、%%%%，4个%在0~f间变化，发送和返回相同，不同发送返回不同（笔者未深入研究规律和代表内容），占用2个bytes<br>
2、090000000000，前两位%%在变动，同一次ping操作，无论发送接收多少包，此数值不变，下一次ping则此值会变动（笔者未深入研究规律和代表内容），占用6bytes<br>
3、101112131415161718191a1b1c1d1e1f20（规律是从10开始的16进制递增，一直到20），占用17bytes<br>
4、!”#$%&amp;’()**+,-./01234567,占用23bytes<br>[![](https://p4.ssl.qhimg.com/t012502f828b2b68de0.jpg)](https://p4.ssl.qhimg.com/t012502f828b2b68de0.jpg)**经过简单的分析确认，windows固定传输的是abcdefghijklmnopqrstuvwabcdefghi，linux固定传输的是!”#$%&amp;’()+,-./01234567，那我们能否改变这些data填充我们自己的数据呢？ 答案是当然是可以！<br>
这就是icmp隐蔽隧道的原理：替换Data部分。windows简单，替换后解决checksum即可，linux稍复杂，替换后要还要满足原有的其他规律（笔者主要领域是windows，有兴趣的读者可以研究下），防止链路上的设备对错误包进行抛弃处理。<br>
此外，还有一点需要补充，ping的包大小，也就是data大小是可以修改的，如修改为1024bytes，以windows为例：<br>[![](https://p3.ssl.qhimg.com/t0184d43e700e80cbdc.png)](https://p3.ssl.qhimg.com/t0184d43e700e80cbdc.png)则，从包体看效果如下，可见规律还是一样，重复罢了。<br>[![](https://p3.ssl.qhimg.com/t01a583c2d9c6eaa4a7.jpg)](https://p3.ssl.qhimg.com/t01a583c2d9c6eaa4a7.jpg)最后，还有一个关键问题！<br>
你发送了修改了data的数据，对方的系统能否正常处理你的畸形ping数据呢？还有对方回包的畸形ping应答数据，你自身能否处理呢？很明显，标准的windows系统和linux系统是无法处理畸形data的数据的，所以我们还需自己的ping发送和应答程序替代系统的本身的ping。那么接下来，我们就来看看各种畸形ping处理工具，也即是icmp隧道工具。



## 工具实现

这里我们不用虚拟机演示，避免只是演示不能实践的窘境！<br>
笔者一开始接触icmp shell时，参考各种用虚拟机演示的文章，发现用虚拟机ok但是真实环境不行，所以踩坑后为了让大家不踩，我们采用真实的公网vps+内网终端演示，环境：<br>
1、vps为linux，内网终端为windows；<br>
2、vps无法ping通内网终端的内网ip；<br>
3、内网终端可以ping通公网独立ip的vps.<br>
好，说明完，我们看看怎么实现:

### <a name="icmp.sh%EF%BC%9A"></a>icmp.sh

先说这个，是因为这个包括一个通用的icmp server端(前面说过，这个是必须的)，可以被其他方式的被控端复用，下载在github找即可，操作如下

<a class="reference-link" name="server%E7%AB%AF%EF%BC%9A"></a>**server端**

正如前面说的，我们的server端要替代系统本身的ping的应答程序，要不shell不稳定（现象是一直提刷屏，无法交互输入），先关闭系统的ping应答，方法如下（恢复系统应答则=0）：<br>[![](https://p4.ssl.qhimg.com/t0120677b68e111c968.png)](https://p4.ssl.qhimg.com/t0120677b68e111c968.png)<br>
然后就可以启动我们自己的icmp应答程序了<br>[![](https://p2.ssl.qhimg.com/t01bd40665d7b92a9b1.png)](https://p2.ssl.qhimg.com/t01bd40665d7b92a9b1.png)<br>
第一个ip为vps的ip，是独立的公网ip，建议用搬瓦工即可<br>
第二个ip是agent的公网ip，但这个所谓的公网ip有玄机，严格说这个ip应该是server端看到的ip，为了得到这个ip可以从内网终端ping这个vps，在vps用tcpdump icmp获取这个ip，然后填写。如下：<br>[![](https://p2.ssl.qhimg.com/t01d28227df27de6a2e.png)](https://p2.ssl.qhimg.com/t01d28227df27de6a2e.png)<br>
如果您要用这个server作为您自己的木马组件则要自动判定，建议anget木马程序弹shell之前，先ping一下server（调整独特ping大小，次数等，防止server误判），server根据ping自动启动server配置。

<a name="agent%E7%AB%AF%EF%BC%9A"></a>**agent端**

按照github上这个工具作者的文章，如下：<br>[![](https://p3.ssl.qhimg.com/t0166116aaff5950b52.png)](https://p3.ssl.qhimg.com/t0166116aaff5950b52.png)<br>
这个ip就是公网的vps的ip了。这样在server端就可以获取到shell了<br>[![](https://p4.ssl.qhimg.com/t014a2cd8f606a07eaf.png)](https://p4.ssl.qhimg.com/t014a2cd8f606a07eaf.png)<br>
数据包分析,课件windows替换了data，大小增大到113<br>[![](https://p1.ssl.qhimg.com/t0109ad1b00a6d128d3.png)](https://p1.ssl.qhimg.com/t0109ad1b00a6d128d3.png)

### <a class="reference-link" name="powershell%20icmp%EF%BC%9A"></a>powershell icmp

**<a name="server%E7%AB%AF%EF%BC%9A%E5%90%8C%E4%B8%8A"></a>server端**

同上

<a class="reference-link" name="agent%E7%AB%AF%EF%BC%9A"></a>**agent端**

这个就不多说了，都是玩这个的，如下<br>[![](https://p5.ssl.qhimg.com/t018c50b991ea77ddee.png)](https://p5.ssl.qhimg.com/t018c50b991ea77ddee.png)

[![](https://p1.ssl.qhimg.com/t01513646b70f8180d7.png)](https://p1.ssl.qhimg.com/t01513646b70f8180d7.png)<br>
ip还是sever的ip，咱们的vps的ip，获取shell，没有乱码，所以笔者还是喜欢powershell这个神器！<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010dd159bcc43a5bd1.png)

### <a class="reference-link" name="meterpreter"></a>meterpreter

虽然写了这个，是因为笔者认为它应该有icmp的反弹shell，但是竟然没找到，也许是寻找方法不对，有知道的同学麻烦留言，感谢！

### <a class="reference-link" name="icmptunnel%E3%80%81ptunnel%E7%AD%89"></a>icmptunnel、ptunnel等

主要用作xx over icmp使用，相对复杂，但是可以让传统的tcp、udp木马再次有用武之地，后续探讨。<br>
当然除了以上还有很多其他工具，如linux下的PRISM（也支持mac、安卓）等等，还有很多人自己的写的python实现，可以说是现有工具已经遍地开花，那就更别说专业黑客在自己的代码中直接实现的了，所以对抗icmp隧道迫在眉睫！



## 检测和防御

明白了原理，也模拟了工具的使用，那么防御和检测就简单，只需要禁止ping就可以完全屏蔽此类隐蔽隧道风险，但如果要考虑用户体验，那就只有解析包体了，然后做否定判定，也就是说只要ping的data不是标准的windows、linux的data包体（标准大包为合法）内容，则判定非法，报警拦截即可。<br>
不过笔者没研究除了windows、linux以外系统ping的实现，如macos、安卓各个版本、各个网络设备等，建议安全防御者先解析包体，然后分析合法data，形成白data清单，最终再做“否”判定。



## 最后的思考

我们这里只探讨最常见的ping（ICMP类型为0和8），那icmp的其他类型是否可以外传、交互shell？继续研究！

审核人：yiwang   编辑：边边
