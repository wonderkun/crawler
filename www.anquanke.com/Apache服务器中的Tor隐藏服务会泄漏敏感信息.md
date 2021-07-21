> 原文链接: https://www.anquanke.com//post/id/83416 


# Apache服务器中的Tor隐藏服务会泄漏敏感信息


                                阅读量   
                                **80029**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://www.dailydot.com/politics/apache-server-status-tor/](http://www.dailydot.com/politics/apache-server-status-tor/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/t01880212a26cd92210.jpg)](https://p5.ssl.qhimg.com/t01880212a26cd92210.jpg)

Tor或许不是网络匿名访问的唯一手段，但毫无疑问它是目前最流行、最受开发者欢迎的。这个免费、开源的程序可以给网络流量进行三重加密，并将用户流量在世界各地的电脑终端里跳跃传递，这样就很难去追踪它的来源。大部分的Tor用户只把它作为一个匿名浏览网页的工具，不过实际上它潜力十足：Tor软件可以在操作系统后台运行，创建一个代理链接将用户连接到Tor网络。随着越来越多的软件甚至操作系统都开始允许用户选择通过Tor链接发送所有流量，这使得你几乎可以用任何类型的在线服务来掩盖自己的身份。

按理来说，隐匿在[Tor](http://www.dailydot.com/tags/tor/)匿名网络中的网站是不应该被发现的，因为Tor网络采用了非常复杂和安全的技术来保证这一点。但是无论技术多么的强大，人类的错误操作几乎可以抵消技术所带来的所有强大功能。

Apache是世界使用排名第一的Web服务器软件。它可以运行在几乎所有广泛使用的计算机平台上，由于其跨平台和安全性被广泛使用，是最流行的Web服务器端软件之一。它快速、可靠并且可通过简单的API扩充，将Perl/Python等解释器编译到服务器中。

研究人员发现，在Apache服务器中存在一个非常常见的错误配置方式，几乎当前全世界所有热门的Web服务器软件都存在这一问题。如果网络服务器中存在这种错误的配置，那么任何人都可以查看到网络中的隐藏服务器，并且还可以查看到服务器中的实时HTTP请求信息以及所有的通信流量数据。

当一个隐藏服务泄漏了HTTP请求信息之后，也就泄漏了服务器中的所有文件－例如Web页面，图片，视频，zip压缩文件等等，这些文件都是服务器页面需要获取的文件。

早在去年时，Tor的开发人员就已经发现了这个问题，但是他们却没有发表任何有关这一问题的公告和声明。这种类型的问题是很常见的，即便是Tor项目的开发人员自己也会犯这样的错误。但是在2015年10月，有一名Tor用户发现，他在对服务器中的软件进行更新检测时发现，这个问题将允许任何人查看你服务器中的所有请求信息以及通信流量数据。

[![](https://p0.ssl.qhimg.com/t01fc5e7c5dc29aabb7.png)](https://p0.ssl.qhimg.com/t01fc5e7c5dc29aabb7.png)

对于使用了Tor网络的设备而言，这样的问题对于用户而言并不会给他们带来任何的安全问题。因为我们可以从上面所给出的这个状态页面中看到大量的服务器信息，但是并没有泄漏任何的敏感的用户数据。

Alec Muffet是Facebook的一名软件工程师，他也在使用Tor匿名网络服务。他在上周周六表示，这个问题已经[存在了六个月之久了](https://wireflaw.net/blog/apache-hidden-service-vuln.html)，但是却没人来修复这个问题。去年，他在一个热门的隐藏服务搜索引擎中发现了同样的问题，这个问题同样会将服务器当前的HTTP请求泄漏出来，这也就意味着你可以查看到该搜索引擎的实时搜索信息。

Muffet在研究之后得到了下图所示的结果，其中搜索量最多的就是－“How to get rid of 2 bodys.”

[![](https://p1.ssl.qhimg.com/t016be5f7dc9169b6e2.png)](https://p1.ssl.qhimg.com/t016be5f7dc9169b6e2.png)

当Tor的开发者在去年得到了关于这个问题的信息之后，他们就决定不发布任何相关的公告和通知。实际上，Apache服务器中的配置问题[在很久之前](https://www.reddit.com/r/TOR/comments/1xgya7/apache_serverstatus_and_tor_hidden_services/)就已经曝光了。

如果你需要修复这个存在于Apache服务器隐藏服务之中的问题，Muffet建议用户可以在服务器中的shell输入下面的这一行命令，运行之后所有问题也都没有了（全都禁用了…..）：

$ sudo a2dismod status
