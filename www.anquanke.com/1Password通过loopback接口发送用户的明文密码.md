> 原文链接: https://www.anquanke.com//post/id/83572 


# 1Password通过loopback接口发送用户的明文密码


                                阅读量   
                                **115911**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://medium.com/@rosshosman/1password-sends-your-password-across-the-loopback-interface-in-clear-text-307cefca6389#.jv3w5c63s](https://medium.com/@rosshosman/1password-sends-your-password-across-the-loopback-interface-in-clear-text-307cefca6389#.jv3w5c63s)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0155ae85d0ed013a89.png)](https://p2.ssl.qhimg.com/t0155ae85d0ed013a89.png)

        如果你使用浏览器扩展功能，1Password会通过loopback接口，将你的密码以清晰的文本形式发送出去。

        注：运行Mac OSX 10.11.3，1Password Mac Store 6.0.1，扩展版本的4.5.3.90（谷歌浏览器）

        昨晚我花了一些时间，来查看我的系统上都在运行着什么，以及端口都和什么连接着。这个时候，我看到1Password在loopback的环回接口连接着。



```
mango:~ ross$ lsof -n -iTCP
COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
2BUA8C4S2 631 ross 12u IPv4 0x507c280b7bcfe03d 0t0 TCP 127.0.0.1:6258 (LISTEN)
2BUA8C4S2 631 ross 13u IPv6 0x507c280b75c30955 0t0 TCP [::1]:6258 (LISTEN)
2BUA8C4S2 631 ross 14u IPv4 0x507c280b7bcfd735 0t0 TCP 127.0.0.1:6263 (LISTEN)
2BUA8C4S2 631 ross 15u IPv6 0x507c280b75c2e3b5 0t0 TCP [::1]:6263 (LISTEN)
2BUA8C4S2 631 ross 18u IPv4 0x507c280b7fd6603d 0t0 TCP 127.0.0.1:6263-&gt;127.0.0.1:49303 (ESTABLISHED)
2BUA8C4S2 631 ross 25u IPv4 0x507c280b9e36b24d 0t0 TCP 127.0.0.1:6263-&gt;127.0.0.1:56141 (ESTABLISHED)
```

<br>

        这勾起了我的兴趣，因为我没有运行任何的服务器功能（除了Wi-Fi的服务器功能），或者任何类似的东西。所以我决定用1Password看看到底发生了什么：

```
tcpdump -i lo0 -s 65535 -w info.pcap
```

        我把原来的一部分数据传输到Wireshark上，然后我就看到了如下的东西：

[![](https://p0.ssl.qhimg.com/t01f754d8fef1ee4c7c.png)](https://p0.ssl.qhimg.com/t01f754d8fef1ee4c7c.png)

        而且如果你填写了网站用户名，或者用1Password登录的话，你可以从中很清楚的看到这些信息：

```
~..`{`“action”:”executeFillScript”,”payload”:`{`“script”:[[“click_on_opid”,”__1"],[“fill_by_opid”,”__1",”&lt;username&gt;”],[“click_on_opid”,”__2"],[“fill_by_opid”,”__2",”&lt;password&gt;”]],”nakedDomains”:[“ycombinator.com”],”documentUUID”:”9983220DB43B058611F22F8542E8D72C”,”autosubmit”:`{`“focusOpid”:”__2",”helper-capable-of-press-enter-key”:true,”submit”:true`}`,”properties”:`{``}`,”fillContextIdentifier”:”`{`”itemUUID”:”D21FD2D7D188424CA2FDDB137F59AFCE”,”profileUUID”:”FF2D2B2B4B904F28A4B891EE35B9903E”,”uuid”:”BD67065A938647C3AE7108F6C11032B9”`}`”,”options”:`{`“animate”:true`}`,”savedUrl”:”https://news.ycombinator.com/x?fnid=xxxxxxxxxxx”,”url”:”https://news.ycombinator.com/x?fnid=xxxxxxxxxxx”`}`,”version”:”01"`}`
```

        据此，我认为1Password正在通过loopback接口向浏览器传输数据，并且不仅仅是传输密码，还有信用卡数据以及其中的购买记录。所以，如果有人嗅探你的loopback，他就可以获取你的密码。信用卡数据或购买记录的信息。

        我同样也关注着[Dashlane](http://www.dashlane.com/)，看他们是如何处理这类通讯联系的，在[Dashlane](http://www.dashlane.com/)上，一切都是加密过的。但我现在还没有去检查Safe-in-Cloud和Enpass是否也是这样处理。

        作者注：我通过邮件向agilebits说明了这个情况，他们没有一个安全邮箱，但是有一个标准的电子邮件支持，[support+kb@agilebits.com](mailto:support+kb@agilebits.com)，你可以这样发送电子邮件来报告一些紧急情况：[support+urgent@agilebits.com](mailto:support+urgent@agilebits.com)。我在不久之前给两个地址都发过邮件，但是他们隐藏了域名注册信息，而且在网站上也不提供。他们是真的很想让你去使用他们的支持论坛。

        因为这涉及到人们的密码，是一个本地设备的问题，而且这很容易解决。所以我觉得我把这些问题尽快公布出来对大家来说是个好事，你们可以据此决定是否要继续使用浏览器扩展功能。
