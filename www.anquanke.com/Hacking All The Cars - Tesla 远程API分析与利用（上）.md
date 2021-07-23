> 原文链接: https://www.anquanke.com//post/id/218396 


# Hacking All The Cars - Tesla 远程API分析与利用（上）


                                阅读量   
                                **269914**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01b401bb18f9d132f1.jpg)](https://p3.ssl.qhimg.com/t01b401bb18f9d132f1.jpg)



大家好，我是银基Tiger Team的BaCde。该系列文章将通过逆向的方式分析Tesla远程api，并自己编写代码实现远程控制Tesla汽车。



## 0x00 简介

Tesla自身的app具备控车的一些功能，如解锁、温度控制、充电、行车轨迹、召唤功能等。那么可能有朋友要问了，分析app自己实现的意义是什么呢？为什么不用官方提供的app呢？而且Github也有大量开源项目。

最开始我也有同样的疑问，但是，当我去尝试了解后，发现分析api，自己可以拓展多种玩法：

1、挖掘潜在的隐藏功能。在漏洞挖掘过程中，总会有一些未在界面显示，被开发者隐藏起来的一些功能。这些功能一旦被我们发现，对漏洞挖掘或者实现额外的功能都有帮助。

2、实现批量控车功能。官方的APP同时只能控制一台汽车，无法控制多台。我们熟悉API后，我们则可以实现批量控制汽车，实现速度与激情中的控车场景，这想想都觉得很酷；

3、熟悉Tesla业务流程，可以深入去挖掘漏洞；

4、尽管目前网络上有很多Tesla的API代码或库，但是其他的车还没有。我们以Tesla为典型例子，可以将其思路和方法拓展到其他同类的汽车厂商中；

5、个性化定制，通过API可以按照自己习惯定制流程，控制更加灵活。还可以拓展功能，如雨天自动关闭天窗，根据情况自动制热/冷却等。甚至可以做成一个商业产品；

6、通过api调用，配合代理跳板实现隐藏自身，同时不会暴漏自己的imei、设备等，减少APP信息收集导致的隐私泄漏。

7、记录下所有关于车的数据，进行数据分析。



## 0x01 制定控制功能

在开始分析前，先来列一个功能清单，在后续分析过程中防止浪费时间。

1、获取车辆列表；<br>
2、获取车辆详细信息；<br>
3、实现远程操作，包括温度控制、开启后备箱、开车锁；<br>
4、通过召唤功能实现控制车前进后退；<br>
5、批量控制汽车。



## 0x02 APP分析

在分析之前，通过查看、搜索Tesla官方内容未发现存在官方的API文档。最终决定通过其官方提供的APP来进行分析。尽管有人发布Tesla API的文档，根据文档或Github的公开库会更快。但是我们本着探寻原理的态度以来使自己得到提升。

### <a class="reference-link" name="%E8%8E%B7%E5%8F%96APP"></a>获取APP

Tesla官方的Android app是需要在Google play上下载的，通过[https://apps.evozi.com/apk-downloader/?id=com.teslamotors.tesla](https://apps.evozi.com/apk-downloader/?id=com.teslamotors.tesla) 地址下载即可。

### <a class="reference-link" name="%E6%8F%90%E5%8F%96api%E5%9C%B0%E5%9D%80"></a>提取api地址

这里个人习惯不同，我通常会先使用apkurlgrep来获取APK文件中的url地址。apkurlgrep为golang语言编写的提取APK文件中输入点的程序。Github地址:[https://github.com/ndelphit/apkurlgrep](https://github.com/ndelphit/apkurlgrep)。按照Github文档安装即可。

安装完成后，执行`apkurlgrep -a com.teslamotors.tesla.apk` 等待显示结果即可。也可以将结果重定向到文件中。结果里有一些是多余的，找到一些我们关注的点即可。这里关注到有api的地址`owner-api.teslamotors.com`的地址，和带有api关键字的路径内容。

[![](https://p2.ssl.qhimg.com/t0156642dea071362c8.png)](https://p2.ssl.qhimg.com/t0156642dea071362c8.png)

[![](https://p0.ssl.qhimg.com/t0144a5791be05fd28a.png)](https://p0.ssl.qhimg.com/t0144a5791be05fd28a.png)

接下来使用jadx反编译源码，将上述发现的关键字在源码中搜索，可以发现这些内容在两个json的文件中。具体内容如下：

[![](https://p2.ssl.qhimg.com/t01abf0691121759362.png)](https://p2.ssl.qhimg.com/t01abf0691121759362.png)

根据定义的常量，在去进行搜索，可以看到其代码的位置。当然这里可以看出Tesla做了混淆，尽管可以分析，但是分析起来很耗精力。这个先暂停，先抓包分析来看看。

### <a class="reference-link" name="%E6%8A%93%E5%8C%85%E5%88%86%E6%9E%90"></a>抓包分析

直接使用抓包工具即可。根据个人习惯选择，本文使用的是Burpsuite。在抓包的过程中会遇到有一些post data的内容是乱码格式，观察其请求头就可以得知使用了gzip压缩，解码可以通过burp的decode即可查看。对于重放，则可以直接去掉其请求头中`content-encoding:gzip`和`Accept-Encoding: gzip, deflate`即可。另外为了方便分析，可以设置scope过滤掉除tesla之外的记录显示。

### <a class="reference-link" name="%E7%99%BB%E5%BD%95%E8%AF%B7%E6%B1%82%E5%88%86%E6%9E%90"></a>登录请求分析

开启拦截，我们使用打开手机中的Tesla APP。按照提示进行正常登录，截获到的请求我们可以先查看下，然后通过。操作完登录的整个流程，可以了解到这里涉及到4个域名，分别为auth-global.tesla.com、auth.tesla.cn、auth.tesla.com、owner-api.teslamotors.com。

其大致过程为先请求auth-global.tesla.com获取其地区，然后跳转到所属区域的服务，这里跳转到auth.tesla.cn，先显示的输入用户名，下一步后，跳转到auth.tesla.com域，显示用户名密码信息，输入用户名密码后也是经过auth.tesla.com。用户名密码正确，APP进行到程序主界面。 这里有两步，第一个先请求auth.tesla.com域获取jwt的token，第二将获取的jwt token带入请求owner-api.teslamotors.com。接下来的获取数据均请求到owner-api.teslamotors.com，由此也可以看出这个地址为api服务的地址，也就是最终我们只需要获取最后的那个token，就可以实现获取其他信息的操作。

大致流程图如下：

[![](https://p0.ssl.qhimg.com/t01ca914639ff9a3490.png)](https://p0.ssl.qhimg.com/t01ca914639ff9a3490.png)

这里实现思路有如下几个：

1、完全自己根据流程构造请求来获取。在实现过程中不仅有多个流程，还需要分析其请求中的参数，非常的麻烦。<br>
2、可以采用headless的方式，一些过程由浏览器来完成，只需要填入参数，点击按钮等操作即可。当然这里需要调用浏览器。

上面的方式都比较麻烦，有没有更简单的方法呢？仔细思考下，既然owner-api.teslamotors.com是提供api服务的，那么Tesla也会有其他的调用方式，如web等，那么其登录可能会更简单。这里我还去分析了下web登录。但是其登录后并未去请求owner-api.teslamotors.com。

而之前看网络上的api，只要发起一次请求就可以获取token，他们是如何获取的呢？

第一种尝试，通过Tesla官方的其他登录点来分析，收集了tesla几个域的子域名，通过寻找登录地来分析，最终没有收获。

第二种尝试，通过反编译的APK代码中搜索，通过查看可以确定tesla 采用了标准的oauth来实现，这里到发现对于owner-api.teslamotors.com的几种类型(grant_type)，分别有authorization_code、refresh_token、urn:ietf:params:oauth:grant-type:jwt-bearer。最后一种是app中登录用到的；refresh_token是用来刷新token的；authorization_code授权码模式(即先登录获取code,再获取token)。

查了下资料，oauth支持5类 grant_type 。除上述用到的外，还有password模式。而公开的api就是这种模式。那么既然支持这种模式，请求的参数字段和内容又怎么来的呢？新版本的APP里没有这种模式，陷入沉思中。片刻后，决定尝试下载老版本APP去分析下，通过搜索引擎找了3.8.5的老版本。反编译，搜索`grant_type`，结果眼前一亮，老版本的只有password模式。而且参数也写的非常明显了。

[![](https://p1.ssl.qhimg.com/t0161f5ff7df2b07887.png)](https://p1.ssl.qhimg.com/t0161f5ff7df2b07887.png)

至于这里的参数client_id和client_secret参数在上文中发现的json文件中有。email和password就是我们的用户名和密码。

至此，登录就分析完成了。我们可以直接构造一次请求，即可获取token了。后续在分析app的时候可以优先选择老版本入手。

### <a class="reference-link" name="%E6%8E%A7%E5%88%B6%E5%8A%9F%E8%83%BD%E8%AF%B7%E6%B1%82%E5%88%86%E6%9E%90"></a>控制功能请求分析

登录后，要控制特斯拉汽车，先会获取账户所属的车辆。在APP中如果只有一辆车则直接现实车辆信息和控制界面，如果有两辆及以上，则会先选择要控制的车辆。

我们登录成功后，只要我们在当前APP界面中，在Burp中会收到多次请求。这里还可以看到关于发送log的请求，这在自己实现api时则可以跳过这个记录。

1、**车辆列表**

根据burp的历史记录，或者在拦截的时候拦截其相应内容来进行分析。通过分析可以看到获取vin，id号的请求是`/api/1/products`，因为返回的格式为json，其信息都在因为返回内容在键，返回的内容中包含id号（id）、用户id（user_id）、vin、显示名字（display_name）、状态（state）等信息。这里id号后面会用到，对汽车进行的操作都是通过这里的id号。如果有两辆车以上，则遍历即可。

2、**车辆详细信息**

通过记录可以看到获取车辆详细信息的api地址为`/api/1/vehicles/`{`vehicle_id`}`/vehicle_data` ，通过抓取停止状态和行驶状态下的数据，可以看到由`endpoints`参数控制，值分别为`drive_state`(行驶中)、`climate_state%3Bgui_settings`、`climate_state%3Bcharge_state%3Bdrive_state%3Bgui_settings%3Bvehicle_state`。

对于行驶中的状态，通过api可以获取当前驾驶速度。

这里根据返回的json进行分析即可。这里不做详细描述。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01565a2c2d6e3f3988.png)

3、 **温度控制**

采用同样的方式，在app中操作，在burp中进行拦截或者从sitemap，历史记录里去分析。

要先调整温度，需要先开启，然后设置温度。也可以关闭温度控制。

api地址为：

```
/api/1/vehicles/`{`vehicle_id`}`/command/auto_conditioning_start //开启温度控制
   /api/1/vehicles/`{`vehicle_id`}`/command/auto_conditioning_stop  //关闭温度控制
   /api/1/vehicles/`{`vehicle_id`}`/command/set_temps                    //设置温度
```

开启和关闭使用空的json即可，或者去掉Content-Type头。

设置温度的请求如下：

```
POST /api/1/vehicles/`{`vehicle_id`}`/command/set_temps HTTP/1.1
   user-agent: Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5 Build/MOB31E; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/44.0.2403.117 Mobile Safari/537.36
   x-tesla-user-agent: TeslaApp/3.10.8-421/adff2e065/android/6.0.1
   authorization: Bearer *****
   Content-Type: application/json; charset=utf-8
   Content-Length: 42
   Host: owner-api.teslamotors.com
   Connection: close

   `{`"driver_temp":22.5,"passenger_temp":22.5`}`
```

[![](https://p1.ssl.qhimg.com/t014f2134dd9a61ecd9.png)](https://p1.ssl.qhimg.com/t014f2134dd9a61ecd9.png)

在分析过程中还会出现响应头尾304的情况，一般出现在GET请求中，我们只需要去掉If-None-Match请求头即可。

4、 **其他**

对于其他功能，分析方法都大致类似，了解了方法后，可以去分析其他的部分，然后对比已经公布的api文档来确认。

### <a class="reference-link" name="%E5%8F%AC%E5%94%A4%E5%8A%9F%E8%83%BD%E6%8E%A7%E8%BD%A6"></a>召唤功能控车

特斯拉在2016年推出了召唤功能，2019年推出了智能召唤功能。智能召唤功能支持车辆自主行驶避让障碍物，并能到达车主面前或者车主指定的位置，无需驾驶员在车内控制。当然这项功能对场地有一定要求，仅限于在“私家停车区域和行车道”使用，无法在公路上使用该功能。

召唤功能不是使用的`owner-api.teslamotors.com`，而是websocket通信，通信服务器为`streaming.vn.teslamotors.com`。由于特殊原因，此次召唤功能将在下篇内容中介绍。

### <a class="reference-link" name="%E5%88%86%E6%9E%90%E7%BB%93%E6%9E%9C"></a>分析结果

根据截获的流量信息，总结一下Telsa api的几个技术点：

1、Tesla的大多数功能调用的是`owner-api.teslamotors.com`的api接口；

2、使用了oAuth 2 标准；APP采用jwt方式来获取api接口的token信息，其jwt加密方式为RS256；

3、发起的请求除登录、找回密码功能外需要`Authorization: Bearer` 请求头，后面内容为token，token具有有效期；

4、召唤功能使用的是websocket的方式，其服务器地址`wss://streaming.vn.teslamotors.com/`。



## 0x03 编程实现

这里开发语言选择Python3，其版本使用的是3.8。为了实现高效的群控，采用异步编程，这里会选择使用aiohttp库。编程实现将在下篇内容中来详细说明。

对于大多数人来说，没有车是分析的最大问题？

我也面临同样的问题，每天上下班路上看着从自己身边路过的特斯拉，彷佛它在无情的嘲笑着我，心中不免泛起淡淡的忧伤。

[![](https://p5.ssl.qhimg.com/t01d13298ef112cecd7.png)](https://p5.ssl.qhimg.com/t01d13298ef112cecd7.png)

抱怨改变不了现实，于是借助搜索大法，几分钟后，成功获取到一个韩国人的账号，此刻我露出了久违的微笑。

[![](https://p4.ssl.qhimg.com/t01ec12335811b16913.png)](https://p4.ssl.qhimg.com/t01ec12335811b16913.png)

[![](https://p3.ssl.qhimg.com/t01192b17fde5d6eead.png)](https://p3.ssl.qhimg.com/t01192b17fde5d6eead.png)

本着负责任的态度，Tiger Team第一时间向泄漏账号的人发送了邮件。截止到目前，Tiger Team仍未收到回复的邮件。Tiger Team会持续跟进该事情进展，并会及时更新至本文。注：本文分析是利用自己的账号进行，意外获取他人账号只是一个小惊喜。

[![](https://p4.ssl.qhimg.com/t01182b5266cd860c06.png)](https://p4.ssl.qhimg.com/t01182b5266cd860c06.png)



## 0x04 总结

本文通过对Tesla app逆向、抓包的方式分析出其api接口。通过本文的研究可以发现，汽车越来越智能化、方便的同时，却也引入了新的安全风险。尽管运用了很多复杂的技术来提高和保证其安全性。但是一旦黑客获取到用户名密码，就可以把Tesla开走。而获取用户名和密码的手段还是可以通过传统的方式来获得。在下一篇的文章中将尝试通过python编程实现利用API来批量控制特斯拉。



## 0x05 参考

[https://apps.evozi.com/apk-downloader/?id=com.teslamotors.tesla](https://apps.evozi.com/apk-downloader/?id=com.teslamotors.tesla)

[https://github.com/ndelphit/apkurlgrep](https://github.com/ndelphit/apkurlgrep)

[https://tesla-api.timdorr.com/](https://tesla-api.timdorr.com/)
