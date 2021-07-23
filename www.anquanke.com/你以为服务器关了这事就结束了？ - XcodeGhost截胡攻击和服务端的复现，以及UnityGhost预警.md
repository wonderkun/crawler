> 原文链接: https://www.anquanke.com//post/id/82451 


# 你以为服务器关了这事就结束了？ - XcodeGhost截胡攻击和服务端的复现，以及UnityGhost预警


                                阅读量   
                                **83654**
                            
                        |
                        
                                                                                    





[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.tianjimedia.com/uploadImages/2015/264/41/D3M6U1D1M7RX_144256467352181481_600.jpg)

作者:没羽,蒸米,阿刻,迅迪 @ 阿里移动安全<br>

**0x00 序**

截胡,麻将术语,指的是某一位玩家打出一张牌后,此时如果多人要胡这张牌,那么按照逆时针顺序只有最近的人算胡,其他的不能算胡。现也引申意为断别人财路,在别人快成功的时候抢走了别人的胜利果实。

虽然XcodeGhost作者的服务器关闭了,但是受感染的app的行为还在,这些app依然孜孜不倦的向服务器(比如init.icloud-analysis.com,init.icloud-diagnostics.com等)发送着请求。这时候黑客只要使用DNS劫持或者污染技术,声称自己的服务器就是”init.icloud-analysis.com”,就可以成功的控制这些受感染的app。具体能干什么能,请看我们的详细分析。

另外,有证据表明unity 4.6.4 – unity 5.1.1的开发工具也受到了污染,并且行为与XcodeGhost一致,更恐怖的是,还有证据证明XcodeGhost作者依然逍遥法外,具体内容请查看第三节。

PS:虽然涅槃团队已经发出过攻击的demo了2,但很多细节并没有公布。所以我们打算在这篇文章中给出更加详细的分析过程供大家参考。

<br>

**0x01通信协议分析**

在受感染的客户端App代码中,有个Response方法用于接收和处理远程服务器指令。

[![](https://p4.ssl.qhimg.com/t012e45ee5cb257649f.png)](https://p4.ssl.qhimg.com/t012e45ee5cb257649f.png)

Response方法中根据服务器下发的不同数据,解析成不同的命令执行,根据我们分析,此样本大致支持4种远程命令,分别是:设置sleep时长、窗口消息、url scheme、appStore窗口。

通过4种远程命令的单独或组合使用可以产生多种攻击方式:比如下载安装企业证书的App;弹AppStore的应用进行应用推广;弹钓鱼页面进一步窃取用户信息;如果用户手机中存在某url scheme漏洞,还可以进行url scheme攻击等。

[![](https://p2.ssl.qhimg.com/t01b2facd403a1ff02f.png)](https://p2.ssl.qhimg.com/t01b2facd403a1ff02f.png)

其通信协议是基于http协议的,在传输前用DES算法加密http body。Response方法拿到服务器下发送的数据后,调用Decrypt方法进行解密:

[![](https://p5.ssl.qhimg.com/t01b6fea26654821e9e.png)](https://p5.ssl.qhimg.com/t01b6fea26654821e9e.png)

如果解密成功,将解密后的数据转换成JSON格式数据:



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://static.wooyun.org//drops/20150921/2015092119175086338.png)

然后判断服务器端下发的数据,执行不同的操作。如下面截图是设置客户端请求服务端器sleep时长的操作:

[![](https://p0.ssl.qhimg.com/t01ef17daee75de3335.png)](https://p0.ssl.qhimg.com/t01ef17daee75de3335.png)

<br>

**0x2恶意行为分析及还原**

在逆向了该样本的远程控制代码后,我们还原了其服务端代码,进一步分析其潜在的危害。

首先我们在服务端可以打印出Request的数据,如下图:

[![](https://p2.ssl.qhimg.com/t0150d885aae180c5ee.png)](https://p2.ssl.qhimg.com/t0150d885aae180c5ee.png)

红色框标记的协议的头部部分,前4字节为报文长度,第二个2字节为命令长度,最后一个2字节为版本信息,紧跟着头部的为DES的加密数据。我们在服务端将数据解密后显示为:

[![](https://p5.ssl.qhimg.com/t0130bd38e713f2e8c3.png)](https://p5.ssl.qhimg.com/t0130bd38e713f2e8c3.png)

这里有收集客户端信息上传到控制服务器。

同样我们返回加密数据给客户端:

[![](https://p3.ssl.qhimg.com/t0144329cf2668cb7d0.png)](https://p3.ssl.qhimg.com/t0144329cf2668cb7d0.png)

明文信息为:

[![](https://p5.ssl.qhimg.com/t01bea0f7a7e53a74d2.png)](https://p5.ssl.qhimg.com/t01bea0f7a7e53a74d2.png)

客户端根据App的运行状态向服务端提供用户信息,然后控制服务器根据不同的状态返回控制数据:

[![](https://p3.ssl.qhimg.com/t0111b5518483fbf81c.png)](https://p3.ssl.qhimg.com/t0111b5518483fbf81c.png)

**恶意行为一 定向在客户端弹(诈骗)消息**

该样本先判断服务端下发的数据,如果同时在在“alertHeader”、“alertBody”、“appID”、“cancelTitle”、“confirmTitle”、“scheme”字段,则调用UIAlertView在客户端弹框显示消息窗口:

[![](https://p4.ssl.qhimg.com/t018460d7320e8b7bb5.png)](https://p4.ssl.qhimg.com/t018460d7320e8b7bb5.png)

消息的标题、内容由服务端控制

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01336a5c3cae4e811e.png)

客户端启动受感染的App后,弹出如下页面:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014b8ffc59299b1540.jpg)

**恶意行为二 下载企业证书签名的App**

当服务端下发的数据同时包含“configUrl”、“scheme”字段时,客户端调用Show()方法,Show()方法中调用UIApplication.openURL()方法访问configUrl:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a10c24acdbb5a015.png)

通过在服务端配置configUrl,达到下载安装企业证书App的目的:

[![](https://p1.ssl.qhimg.com/t019b1de0eff84dcd2a.png)](https://p1.ssl.qhimg.com/t019b1de0eff84dcd2a.png)

客户端启动受感染的App后,目标App将被安装:

[![](https://p3.ssl.qhimg.com/t01776df29d36c81e83.png)](https://p3.ssl.qhimg.com/t01776df29d36c81e83.png)

[![](https://p2.ssl.qhimg.com/t01a78dbbecc004de41.png)](https://p2.ssl.qhimg.com/t01a78dbbecc004de41.png)



**恶意行为三 推送钓鱼页面**

通过在服务端配置configUrl,达到推送钓鱼页面的目的:

[![](https://p2.ssl.qhimg.com/t01d4315eb89ad5ea3f.png)](https://p2.ssl.qhimg.com/t01d4315eb89ad5ea3f.png)

客户端启动受感染的App后,钓鱼页面被显示:

[![](https://p4.ssl.qhimg.com/t01a44423e541e21ddd.png)](https://p4.ssl.qhimg.com/t01a44423e541e21ddd.png)



**恶意行为四 推广AppStore中的应用**

通过在服务端配置configUrl,达到推广AppStore中的某些应用的目的:

[![](https://p0.ssl.qhimg.com/t012fb8b79b20093a3f.png)](https://p0.ssl.qhimg.com/t012fb8b79b20093a3f.png)

phishing1.html页面内容:

[![](https://p3.ssl.qhimg.com/t01b6b12da952091cab.png)](https://p3.ssl.qhimg.com/t01b6b12da952091cab.png)

客户端启动受感染的App后,自动启动AppStore,并显示目标App的下载页面:

[![](https://p3.ssl.qhimg.com/t01ffee622d0a6cc12b.png)](https://p3.ssl.qhimg.com/t01ffee622d0a6cc12b.png)



<br>

**0x03 UnityGhost?**

在大家以为一切都完结的时候,百度安全实验室称已经确认”Unity-4.X的感染样本”。并且逻辑行为和XcodeGhost一致,只是上线域名变成了init.icloud-diagnostics.com。这意味,凡是用过被感染的Unity的app都有窃取隐私和推送广告等恶意行为。

[![](https://p1.ssl.qhimg.com/t018594ded589b258ae.png)](https://p1.ssl.qhimg.com/t018594ded589b258ae.png)

Unity是由Unity Technologies开发的一个让玩家创建诸如三维视频游戏、实时三维动画等类型互动内容的多平台的综合型游戏开发工具,是一个全面整合的专业游戏引擎。很多有名的手机游戏比如神庙逃亡,纪念碑谷,炉石传说都是用unity进行开发的。

更令人恐怖的是,在百度安全实验室确认后没多久,大家就开始在网上寻找被感染的Unity工具,结果在我搜到一个Unity3D下载帖子的时候发现”codeFun与2015-09-22 01:18编辑了帖子”!?要知道codeFun就是那个自称XcodeGhost作者的人啊。他竟然也一直没睡,大半夜里一直在看大家发微博观察动静?随后发现大家知道了Unity也中毒的事情,赶紧去把自己曾经投毒的帖子删了?

[![](https://p1.ssl.qhimg.com/t015a6e4433bcd3d0c6.jpg)](https://p1.ssl.qhimg.com/t015a6e4433bcd3d0c6.jpg)

现在再去看那个帖子已经被作者删的没有任何内容了。。。 http://game.ceeger.com/forum/read.php?tid=21630&amp;fid=8

[![](https://p1.ssl.qhimg.com/t019b64ae5102a2d7ce.png)](https://p1.ssl.qhimg.com/t019b64ae5102a2d7ce.png)

但根据XcodeGhost作者没删之前的截图表明,从unity 4.6.4 – unity 5.1.1的开发工具都有可能被投毒了!

**0x04 总结**

虽然病毒作者声称并没有进行任何广告或者欺诈行为,但不代表别人不会代替病毒作者进行这些恶意行为。并且作者依然还在逍遥法外!所以立刻!马上!删掉那些中毒的app吧!

<br>

**0x05 参考资料**

涅槃团队:Xcode幽灵病毒存在恶意下发木马行为 [http://drops.wooyun.org/papers/8973](http://drops.wooyun.org/papers/8973)

XcodeGhost 源码 [https://github.com/XcodeGhostSource/XcodeGhost](https://github.com/XcodeGhostSource/XcodeGhost)
