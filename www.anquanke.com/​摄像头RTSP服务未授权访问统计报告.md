> 原文链接: https://www.anquanke.com//post/id/83500 


# ​摄像头RTSP服务未授权访问统计报告


                                阅读量   
                                **216345**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0155e7aa3f69dc94bd.jpg)](https://p4.ssl.qhimg.com/t0155e7aa3f69dc94bd.jpg)

        网络摄像机作为安防设备，被广泛的用于交通、学校、企业、商场等公共场所。网络摄像机为方便管理员远程监控，一般会有公网IP（或端口映射），接入互联网。因此许多暴露在公网的网络摄像机也成了黑客眼中的目标。

        在去年年初国内某知名摄像头厂商因被曝漏洞而遭遇“黑天鹅”后，网络摄像机的安全风险开始被公众所认识。去年一年国内多款摄像头也接二连三的被爆出存在安全漏洞。

近日，国外多篇关于通过RTSP未授权访问来获取摄像头内容的报道引起了我们的关注，360攻防实验室对其进行了研究统计。

**<br>**

**关于RTSP协议**

        RTSP（Real Time Streaming Protocol），实时流传输协议，是TCP/IP协议体系中的一个应用层协议，该协议定义了一对多应用程序如何有效地通过IP网络传送多媒体数据，被广泛用于视频直播领域。RTSP协议的默认端口是554，默认的承载协议为TCP。

        rtsp地址格式为：rtsp://[username]:[password]@[ip]:[port]/[codec]/[channel]/[subtype]/av_stream

**<br>**

**漏洞分析**

        为方便用户远程监控摄像头内容，许多摄像头厂商会在摄像头或NVR中开启RTSP服务器，用户可通过VLC等视频播放软件打开rtsp地址进行摄像头画面的实时查看。

        但是由于设计上考虑不周，许多厂商并没有给rtsp地址做身份认证，导致任何人都可以在未经授权的情况下直接通过地址观看到摄像头的实时内容。

        在shadon搜索port:554 has_screenshot:true，我们可以看到有大量的摄像头存在此类安全问题。

        其中有公共场所：

[![](https://p4.ssl.qhimg.com/t01db37131b6dfb31b4.png)](https://p4.ssl.qhimg.com/t01db37131b6dfb31b4.png)

        有办公场所：

[![](https://p0.ssl.qhimg.com/t01948336af80a9e58f.png)](https://p0.ssl.qhimg.com/t01948336af80a9e58f.png)

        甚至还有客厅、卧室等私人场所

[![](https://p5.ssl.qhimg.com/t01ae9d597c0084adf3.png)](https://p5.ssl.qhimg.com/t01ae9d597c0084adf3.png)

[![](https://p4.ssl.qhimg.com/t01e658d4290ab36d08.png)](https://p4.ssl.qhimg.com/t01e658d4290ab36d08.png)

**<br>**

**漏洞统计**

        360攻防实验室针对该安全问题对全网进行了扫描统计，发现公网可访问的RTSP服务器（554端口）有131万，无需认证可直接获取到视频内容的为45488个。

        排名前十的国家和地区如下：

[![](https://p2.ssl.qhimg.com/t010beea5831251fbb1.png)](https://p2.ssl.qhimg.com/t010beea5831251fbb1.png)

        值得一提的是，在中国的18230个无需认证的即可访问的RTSP服务中，有11227个是位于我国台湾地区的，由此可见台湾是受影响最大的地区。 

[![](https://p2.ssl.qhimg.com/t01b9055e891f4fc1e7.png)](https://p2.ssl.qhimg.com/t01b9055e891f4fc1e7.png)

**<br>**

**安全建议**

        对于开启了RTSP服务的摄像头，用户可自行检查在连接RTSP服务器时是否需要身份认证信息。对于无需认证即可连接的摄像头请不要将其暴露在公网上，并做相关的访问策略。

        及时升级固件，修复摄像头存在的漏洞。
