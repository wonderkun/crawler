> 原文链接: https://www.anquanke.com//post/id/105540 


# Steam新型盗号木马及产业链分析报告


                                阅读量   
                                **159764**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t010ecd7f3e24bb746e.jpg)](https://p0.ssl.qhimg.com/t010ecd7f3e24bb746e.jpg)

Poner@360Cert



## 0x00 前言

《绝地求生：大逃杀》自Steam上线以来就一直占据销量榜榜首，可见该款游戏的热门程度。用户纷纷加入“吃鸡大军”，而《绝地求生：大逃杀》需要用户在Steam商城花费98元购买才能够开始“吃鸡”。黑产从业者也发现这里面“商机”并盯上了用户手里的Steam账号，他们试图通过盗取Steam账号数据并售卖，进而牟利。

[![](https://p4.ssl.qhimg.com/t01d121bafe0d1410c9.png)](https://p4.ssl.qhimg.com/t01d121bafe0d1410c9.png)

“邮箱数据”贴吧



而我们也发现这些黑产从业者正试图在贴吧、QQ群里售卖手里的非法Steam数据，其中的“邮箱数据”贴吧里发布了大量的非法Steam数据交易内容。并且，我们360云安全系统监测近期也有曝光过一些不法分子借助变声器、外挂、加速器等进行盗号木马传播，该木马一旦运行，即可成功盗取得用户的QQ号和动态Skey。

腾讯为了方便用户，在登录的QQ电脑中，可以使用“快速登录”的方式，在使用此种登录方式的过程中，会产生一个密钥，是QQ登录的另一种身份证，盗号者可以通过这个key来识别用户的QQ，登录邮箱，QQ空间、看相册、日记，发布说说，微博，财付通，QB查询……

[![](https://p0.ssl.qhimg.com/t0113d2ed00704be396.png)](https://p0.ssl.qhimg.com/t0113d2ed00704be396.png)

使用QQkey登录邮箱工具

通过伪装steam外挂传播的不法分子通过快速登录QQ邮箱，将盗取与QQ邮箱有绑定关系的Steam账号以及相关财产。



## 0x01 产业链分析

我们尝试跟贴吧中一个“贩子”进行沟通，试图还原整个盗号产业链的情况。

[![](https://p5.ssl.qhimg.com/t0147b4c36049029ac4.jpg)](https://p5.ssl.qhimg.com/t0147b4c36049029ac4.jpg)[![](https://p2.ssl.qhimg.com/t01ef00ef5ee3a087d1.png)](https://p2.ssl.qhimg.com/t01ef00ef5ee3a087d1.png)



聊天记录、盗号工具列表

沟通的过程“贩子”向我们展示了盗取Steam账号过程中需要的工具以及测试数据，从工具来看，我们发现他们用于窃取QQKey的收信方式主要有腾讯企业邮箱收信、ASP收信。

[![](https://p3.ssl.qhimg.com/t01d9beaf67fc8a7f32.jpg)](https://p3.ssl.qhimg.com/t01d9beaf67fc8a7f32.jpg)

盗号木马生成器、QQKEY登录器

[![](https://p1.ssl.qhimg.com/t01b3636d0015d3f284.jpg)](https://p1.ssl.qhimg.com/t01b3636d0015d3f284.jpg)

邮件收信

“贩子”还告诉了我们这些工具、源码在圈内的价位，整套盗号木马生成器的易语言源码一套售价1500，而对于一些不懂的加工易语言源码的工作室主要是通过购买价位在800左右的QQKey盗号木马生成器，就连用于登录QQKey的登录器也要400。

[![](https://p2.ssl.qhimg.com/t017b4f043afb0d6020.png)](https://p2.ssl.qhimg.com/t017b4f043afb0d6020.png)

[![](https://p3.ssl.qhimg.com/t01ea71f3e320cafc09.png)](https://p3.ssl.qhimg.com/t01ea71f3e320cafc09.png)

我们以需要测试盗号木马是否能够免杀360向“贩子”要了一个测试木马，“贩子”称它的木马能够过360，然而文件刚下载下来就被QVM查杀了。其实，该木马本身技术门槛并不高。而整个盗号流程中至关重要的就是账号数据量，而在后续沟通的过程中，我们也“贩子”那了解到他们的手法主要为引流传播，并再次向我们展示了他们行业“撸号宝典”。

[![](https://p0.ssl.qhimg.com/t01621c438e0a873f23.jpg)](https://p0.ssl.qhimg.com/t01621c438e0a873f23.jpg)

最终我们还原出关于这类黑色产业链的情况如下图：

[![](https://p2.ssl.qhimg.com/t01dbfc4a9ee067ca29.jpg)](https://p2.ssl.qhimg.com/t01dbfc4a9ee067ca29.jpg)



## 0x02 窃取QQkey

我们根据近期捕获的样本中发现，此类盗号木马的窃取QQkey的攻击手法主要有两种。

### <a name="_Toc511896108"></a>利用QQ快速登录窃取QQKey

[![](https://p5.ssl.qhimg.com/t01563a8545629ba3c0.png)](https://p5.ssl.qhimg.com/t01563a8545629ba3c0.png)

通过访问[http://localhost.ptlogin2.qq.com:4300/[url](http://localhost.ptlogin2.qq.com:4300/%5burl)]获取用户登录qq的key ,将Set-Cookie中的clientKey发送到牧马人的服务器（464690486.blkj.tk）中。

[![](https://p4.ssl.qhimg.com/t01db4daefa5cecccb8.png)](https://p4.ssl.qhimg.com/t01db4daefa5cecccb8.png)

牧马人的服务器通过qqkey.php以Get的方式接收QQkey进程存储，传输的数据主要有：qq号码、QQ名称、QQkey。

[![](https://p1.ssl.qhimg.com/t01218c0eb2230157ed.jpg)](https://p1.ssl.qhimg.com/t01218c0eb2230157ed.jpg)

将qq号和qq登录的key发送到指定服务器

[![](https://p4.ssl.qhimg.com/t0161e71b85b027f656.jpg)](https://p4.ssl.qhimg.com/t0161e71b85b027f656.jpg)

还将信息发送到指定邮箱

其中某木马分发者的收信网站流量：

[![](https://p0.ssl.qhimg.com/t010f1702bc7aa396e2.png)](https://p0.ssl.qhimg.com/t010f1702bc7aa396e2.png)

注：该图来自360网络安全研究院

根据网站流量来看从2018年3月30日开始网站流量突然飙升，在上面我们也贴出了该站的访问日志。

另外一个木马分发者的收信邮箱：

[![](https://p1.ssl.qhimg.com/t017fafbda3d69f4fc4.png)](https://p1.ssl.qhimg.com/t017fafbda3d69f4fc4.png)

由此可见收获不菲。

### <a name="_Toc511896109"></a>暴力搜索内存提取QQkey，上传服务器或者邮箱

[![](https://p2.ssl.qhimg.com/t0185fdade027f5ae43.png)](https://p2.ssl.qhimg.com/t0185fdade027f5ae43.png)

读取QQ.exe内存

[![](https://p5.ssl.qhimg.com/t0132ba3fa09742f0c8.png)](https://p5.ssl.qhimg.com/t0132ba3fa09742f0c8.png)

发送QQKey到服务器

登录到一个盗号者的服务器上，可以看到半小时左右就有2000多个QQ账号和密码被盗取。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0120769a3351376800.png)

服务器上QQKey记录

### <a name="_Toc511896110"></a>新型变种

关于这个新型变种，我们发现他获取QQkey使用的方法并没有改变(这种方法目前在国内目前只有360可以查杀)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010d9cc4dec971d5be.png)

依旧还是通过QQ快速登录的接口获取的QQkey，如下图：

[![](https://p3.ssl.qhimg.com/t01b871d422f4263120.png)](https://p3.ssl.qhimg.com/t01b871d422f4263120.png)

不过我们发现他上传QQkey的方法发生了改变，由以前的通过邮箱收信、ASP收信变成了socket通信，如下图木马正在连接C&amp;C服务器：

[![](https://p2.ssl.qhimg.com/t0152d54ec7c98348d2.png)](https://p2.ssl.qhimg.com/t0152d54ec7c98348d2.png)

我们通过技术手段获得了该变种的木马生成器，该生成器中包含：全自动进入QQ邮箱盗号、管理获取的QQkey、自动生成木马等等，可见功能非常齐全。

其中，我们得知该服务器在4月11日至4月12日之间流量飙升，由此可见该变种应该是在4月11日的时候放出的，事后我们对此变种进行了拦截，该C&amp;C服务器的流量图如下：

[![](https://p1.ssl.qhimg.com/t012f7c11bfa5796ecf.png)](https://p1.ssl.qhimg.com/t012f7c11bfa5796ecf.png)

注：该图来自360网络安全研究院



## 0x03 IOC

12e13e.exe  55AC18FB660F726EB801B8F03F9EBC37

wrqdfq.exe   37575D21B8CD16ABA4C3E1B3013B1E31

QQPass.exe 6CB90F793DB09FEF0077E599C6FF6F20



## 0x04 防范建议
- 立即下载安装“360安全卫士”对此类木马进行防范。
- 不要因为使用辅助软件而关闭安全软件的防护功能。


## 0x05 总结

360云安全大数据显示该类型木马数量一直在不断的增加，不单单是可能影响到用户的Steam账号安全，也影响了用户QQ其他业务的安全性，有可能促使用户遭受较大的经济损失等。

建议广大用户立即下载安装目前国内唯一能查杀此类样本的“360安全卫士”进行查杀。
