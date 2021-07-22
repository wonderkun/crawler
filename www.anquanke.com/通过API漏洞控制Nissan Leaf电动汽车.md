> 原文链接: https://www.anquanke.com//post/id/83534 


# 通过API漏洞控制Nissan Leaf电动汽车


                                阅读量   
                                **81192**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://www.troyhunt.com/2016/02/controlling-vehicle-features-of-nissan.html](http://www.troyhunt.com/2016/02/controlling-vehicle-features-of-nissan.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t015366dbb0f612961c.png)](https://p0.ssl.qhimg.com/t015366dbb0f612961c.png)

**在我曝光了Nissan Leaf车载应用程序的漏洞之后，安全研究人员还发现，攻击者不仅可以通过网络连接Nissan Leaf电动汽车，而且还可以在不受尼桑所设计的应用程序限制的情况下控制人们的Nissan Leaf电动汽车。**

后来我发现，我的朋友[Scott Helme](https://scotthelme.co.uk/)（他也是一名安全研究人员）也有一台Nissan Leaf电动汽车，所以我们记录下了下面的这个视频，并在视频中进行了相应的演示操作。我之所以要将这个视频放在文章的开头，是因为我想让大家知道这个问题的严重程度，任何人都可以对你的Nissan Leaf电动汽车做这些事情。别着急，我会在文章中对相关的技术细节进行详细地讨论：



大家可以看到，我选择了一个阳光明媚的地方来进行操作，而与此同时，Scott却在寒风中颤抖，但他的“牺牲”是为了给大家演示：即使你在非常遥远的地方，你也可以控制别人的汽车。没错，遥远的地方指的就是地球的另一端。接下来，我将给大家讲解我们是如何一步一步地获取到这台Nissan Leaf电动汽车的控制权，并且还会解释为何其他国家的电动汽车也有可能会被远程控制。

下图即为[目前全世界销量最高的电动汽车](https://en.wikipedia.org/wiki/Nissan_Leaf)－Nissan Leaf电动汽车：

[![](https://p0.ssl.qhimg.com/t017b802e92b39bac7c.png)](https://p0.ssl.qhimg.com/t017b802e92b39bac7c.png)

**连接Nissan Leaf电动汽车**

在挪威等国家，Nissan Leaf电动汽车是非常受欢迎的，因为挪威政府向民众提供了大量的财政补贴，目的就是为了鼓励大家使用清洁能源，远离汽油和柴油等化石燃料。你所期待电动汽车应该具有的功能，Nissan Leaf电动汽车都一应具全，因为它诞生于这个物联网时代，而且它还配备有一个内置的车载应用程序：

[![](https://p2.ssl.qhimg.com/t01044f01226c729ee6.png)](https://p2.ssl.qhimg.com/t01044f01226c729ee6.png)

在好奇心的驱使之下，我在我的手机中安装了[NissanConnect EV应用程序](https://itunes.apple.com/us/app/nissanconnectsm-ev/id407814405?mt=8)，整个安装过程需要几分钟的时间，在对这款应用程序进行了使用体验之后，我便立刻卸载了这个程序：

[![](https://p5.ssl.qhimg.com/t01b632658fbd3f31d1.png)](https://p5.ssl.qhimg.com/t01b632658fbd3f31d1.png)

上图显示的是该程序的主界面，这个界面并不会泄漏我的个人信息。当我打开这个程序之后，我观察到了下列请求信息（我对网络主机名以及车辆识别码的最后五位数进行了混淆处理）：

```
GET https://[redacted].com/orchestration_1111/gdc/BatteryStatusRecordsRequest.php?RegionCode=NE&amp;lg=no-NO&amp;DCMID=&amp;VIN=SJNFAAZE0U60XXXXX&amp;tz=Europe/Paris&amp;TimeFrom=2014-09-27T09:15:21
```

而这个请求信息将会返回下图所示的JSON响应信息：

[![](https://p4.ssl.qhimg.com/t01fd49d8d8b1ce761f.png)](https://p4.ssl.qhimg.com/t01fd49d8d8b1ce761f.png)

如果你能看懂这些响应信息，那么一切都会不解自明：我们可以从上面这段响应信息中了解到汽车的电池电量状态。但是，真正引起我注意力的事情并不是我能接收到有关汽车当前电池电量的信息，而是在我手机所发送的请求信息中，并没有包含任何有关身份验证的信息。换句话来说，我莫名其妙地实现了匿名访问API。这是一个GET请求，所以该请求并没有传递任何有关身份验证的内容，而且也没有在请求的header中添加任何的令牌信息。实际上，唯一能够识别出目标车辆的根据就是其车辆识别码，而这一信息也可以从上述的URL地址中看到。

[车辆识别码](https://en.wikipedia.org/wiki/Vehicle_identification_number)可以唯一标识一架Nissan Leaf电动汽车的底盘，也就是说，每一架Nissan Leaf电动汽车只能唯一对应一个车辆识别码。所以这个识别码肯定不应该作为身份验证过程中的秘密数据来使用。

从表面上看，似乎任何人只要能够知道Nissan Leaf电动汽车的车辆识别码，他都可以得到该汽车的电池电量信息。但实际上，这个问题并没有大家想象中的那么严重，因为这是一个被动查询请求（它其实并不能够修改汽车的相关配置信息），而且在该请求的响应信息中并不会包含多少用户的个人敏感信息。但值得注意的是，他人可以通过OperationDateAndTime的数据来了解到目标车辆的车主最后的一次驾驶该汽车的时间。于是，我继续进行分析。

我发现，我还可以使用下列请求信息来检测车辆温度控制系统的当前状态：

```
GET https://[redacted].com/orchestration_1111/gdc/RemoteACRecordsRequest.php?RegionCode=NE&amp;lg=no-NO&amp;DCMID=&amp;VIN=SJNFAAZE0U60XXXXX
```

上面这个请求信息将会返回与之前类似的响应信息，具体如下图所示：

[![](https://p0.ssl.qhimg.com/t016a9770df8a2b01b3.png)](https://p0.ssl.qhimg.com/t016a9770df8a2b01b3.png)

实际上，我们也可以从NissanConnect应用程序中看到这些信息：

[![](https://p2.ssl.qhimg.com/t01a3d6a173a6aa4a03.png)](https://p2.ssl.qhimg.com/t01a3d6a173a6aa4a03.png)

同样的，这也是一个被动请求信息，温度控制系统要么开启，要么关闭，这只是一个开关，你也不可能从中获取到什么有价值的信息。但是当我尝试开启它时，我观察到了下列的请求信息：

```
GET https://[redacted].com/orchestration_1111/gdc/ACRemoteRequest.php?RegionCode=NE&amp;lg=no-NO&amp;DCMID=&amp;VIN=SJNFAAZE0U60XXXXX&amp;tz=Europe/Paris
```

该请求信息将会接收到下图所示的响应信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e0b5ed0035d64b2a.png)

但是这一次，系统却返回了用户的个人信息，例如userID，用户的userID很有可能使用的是其真实姓名。除此之外，响应信息中还包含有目标汽车的车辆识别码和请求的resultKey。

然后，我将汽车的温度控制系统关闭，并且发现这个应用程序还发出了下列请求信息：

```
GET https://[redacted].com/orchestration_1111/gdc/ACRemoteOffRequest.php?RegionCode=NE&amp;lg=no-NO&amp;DCMID=&amp;VIN=SJNFAAZE0U60XXXXX&amp;tz=Europe/Paris
```

在该应用程序所发出的所有请求信息中，没有附带有任何形式的身份认证信息，所以这些请求都是匿名发送的。与此同时，我还将这些请求信息加载进了Chrome浏览器中，我同样能够接收到相应的返回信息。所以现在我可以断定，这个应用程序的API绝对没有提供任何的访问权限控制。

**与其他的汽车进行连接**

我在网上进行了一番搜索之后，我发现了这样的一张图片：

[![](https://p2.ssl.qhimg.com/t01ab9f254a82cb1ee1.png)](https://p2.ssl.qhimg.com/t01ab9f254a82cb1ee1.png)

很明显，这就是汽车的车辆识别码，我对识别码进行了混淆处理，但是网站上的这张图片却是清晰完整的。

在我进行更加深入地讨论之前，我需要说明一下，而这也是我经常挂在嘴边的事情：当一个潜在的安全漏洞被发现之后，你就必须仔细考虑如何去进行身份验证处理。而且我想澄清的一点就是，我们并不会去对他人的车辆进行恶意操作，即开启汽车的温度控制系统，而且我们也不会去从汽车中获取到有关车主的个人信息。

不同车辆的车辆识别码只在其最后五位数有所区别。我们提取出了这个识别码，并将其插入到了请求信息之中（这个请求信息并不会改变汽车的配置，也不会获取到用户的个人信息），看看是否能够接收到车辆的电池信息，在片刻过后，我们接收到了下图所示的响应信息：

[![](https://p5.ssl.qhimg.com/t01b7df575bc3f3b4f2.png)](https://p5.ssl.qhimg.com/t01b7df575bc3f3b4f2.png)

这似乎意味着系统无法对我们所发送的这个请求信息进行处理，但我们尚不清楚其原因。在经过思考之后，我认为很有可能是因为这个车辆识别码并没有在NissanConnect应用程序中进行过注册，而且也有可能是因为上面这个URL地址中的某些参数有误。比如说，车辆识别码中有一段数据是用于标明产地信息的，也许是因为这一信息与汽车当前的位置有出入。

但是，我们也可以很容易地枚举出车辆识别码。这也就意味着，我们可以利用Burp Suite这样的工具来对枚举出的车辆识别码进行测试。

**总结**

我希望尼桑公司尽快修复这个问题。现在唯一的好消息就是，这个问题并不会影响车辆的驾驶控制系统。现在，大量的汽车制造商都想要往各自生产的汽车中添加物联网智能部件，而安全方面的问题也就浮出了水面。所以我希望各大厂商在推出某一款新产品之前，请确保这款产品的安全性。如果产品中存在严重的安全漏洞，受影响的不仅是消费者，企业辛辛苦苦建立的声誉也会分崩瓦解。
