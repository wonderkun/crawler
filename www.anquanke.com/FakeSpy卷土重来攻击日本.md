> 原文链接: https://www.anquanke.com//post/id/161104 


# FakeSpy卷土重来攻击日本


                                阅读量   
                                **88791**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fortinet.com
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/fakespy-comes-back—new-wave-hits-japan.html](https://www.fortinet.com/blog/threat-research/fakespy-comes-back%E2%80%94new-wave-hits-japan.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01cb8f979efcac525e.jpg)](https://p0.ssl.qhimg.com/t01cb8f979efcac525e.jpg)

## 一、前言

FortiGuard实验室最近发现了一些恶意流量，其C2服务器位于中国境内。恶意链接所使用的域名与日本最知名的快递服务商非常相似。根据我们的分析，创建该链接的网站属于虚假网站，并且会传播Android恶意软件。

初步分析时，这个Android文件非常像趋势研究人员在2018年6月份发现的FakeSpy恶意软件，但根据我们分析平台的处理结果，虽然该样本在代码上基于FakeSpy，但这款新变种还包含新的功能，并且恶意活动势力不断增长。



## 二、网页分析

初步分析样本后，我们发现了一个域名：`hxxp://sagawa-ba[.]com`。

[![](https://p0.ssl.qhimg.com/t01c717d590d30f553d.jpg)](https://p0.ssl.qhimg.com/t01c717d590d30f553d.jpg)

图1. 伪造的日本快递官网

眼尖的读者可能会发现，该网站伪装的是日本的某家快递服务公司。然而仔细检查后，我们可以看到该网站并没有使用SSL证书，并且页面布局也不正确。

在分析页面源码时，我们首先注意到的是其中的Mark of the Web（MOTW）注释。MOTW是Windows XP SP2开始引入的一个安全机制，现在每一个浏览器都会部署该机制，在用户下载Web页面和脚本到本地磁盘时提高用户的安全性。

[![](https://p1.ssl.qhimg.com/t012b9554911bb4bee4.jpg)](https://p1.ssl.qhimg.com/t012b9554911bb4bee4.jpg)

图2. 主页面的MOTW标志

这行注释表明该页面最早下载自某个页面，然后再上传到其他页面中，以便添加一些新的“功能”。新增的一个主要功能是包含`kk`函数的一段脚本。我们还观察到页面中注释掉了一个弹出消息，可能表明攻击代码仍在研发中。`kk`函数很简单，会打开网站的`pp.html`页面，一旦终端用户点击网站时就会调用该函数。

[![](https://p4.ssl.qhimg.com/t01e76a393946ac4ad1.jpg)](https://p4.ssl.qhimg.com/t01e76a393946ac4ad1.jpg)

图3. 主页面中的重定向脚本

跟随重定向代码，我们可以看到如下错误信息，声称出于安全原因，用户需要输入手机号码。

[![](https://p3.ssl.qhimg.com/t01b4ec88c9565960ab.png)](https://p3.ssl.qhimg.com/t01b4ec88c9565960ab.png)

图4. 出于“安全”原因弹出来的手机号码页面

分析处理输入字段的脚本后，我们发现用户输入的数据会直接发送到恶意服务器，其中cookie字段用来发送用户输入的移动手机号码。之后浏览器会跳转到下一个页面，调用`pp2.html`。该页面中同样包含被注释的代码段，可能表明攻击代码仍在研发中。

[![](https://p3.ssl.qhimg.com/t01d3cb3abaf4880a94.png)](https://p3.ssl.qhimg.com/t01d3cb3abaf4880a94.png)

图5. 手机号码发送脚本

进入下一页，恶意网站会要求我们输入“确认”码：

[![](https://p5.ssl.qhimg.com/t018b66a34526c9b845.png)](https://p5.ssl.qhimg.com/t018b66a34526c9b845.png)

图6. 手机号的“确认”码

当我们检查输入字段的代码时，可以发现其中依然包含注释代码，但这次代码与之前的`pp.html` JavaScript代码非常相似。很有可能是开发者复制粘贴代码后，在投入实际环境中前忘了删掉其中的注释，也有可能将这些注释代码留在页面中用来测试。

[![](https://p5.ssl.qhimg.com/t012da9808cb00812fc.png)](https://p5.ssl.qhimg.com/t012da9808cb00812fc.png)

图7. 确认码的验证代码

分析该脚本，我们可以看到脚本会调用`validate()`函数，检查用户提供的代码是否包含4个数字。如果满足该条件，网站就会将代码发送到服务端，将用户重定向到`loding1.html`页面。不幸的是，我们没有从服务器那获取任何响应数据。但该元素可能用来帮用户订阅付费服务，或者用来验证用户提供的是真实的手机号，该页面只为用户“服务”一次。

除了该脚本外，该页面还包含一个定时器脚本。这里有趣的是，该页面的注释中包含一些中文字符。

[![](https://p5.ssl.qhimg.com/t01db8634cd404a1f66.png)](https://p5.ssl.qhimg.com/t01db8634cd404a1f66.png)

图8. 带有中文注释的自定义定时器代码

接下来，如果我们我们分析`loding1.html`源码，可以找到负责处理服务器返回数据的另一个脚本，脚本中我们还是可以找到中文注释，还有一条韩文注释。这可能表明攻击者存在代码复用，没有翻译中文字符，或者也有可能是中国攻击者和韩国攻击者合作的结果。

[![](https://p1.ssl.qhimg.com/t01096ed12bc76a23b0.jpg)](https://p1.ssl.qhimg.com/t01096ed12bc76a23b0.jpg)

图9. 带有中文和韩文注释的页面加载脚本

在搜索代码模式时，我们发现这些有趣的地方并不足以作为追踪钓鱼网站开发者的证据。虽然钓鱼页面中的`setInterval('newArticleCheck()', 2000);`代码与2015年韩国人`쥬리앙`（Juriang）在Q&amp;A PHP论坛上使用的代码样式、函数名以及语法相匹配，但我们无法肯定新的攻击代码由同一个人开发，有可能其他人直接复用了PHP论坛上的代码。

[![](https://p4.ssl.qhimg.com/t01c8c0f2c164c60b31.png)](https://p4.ssl.qhimg.com/t01c8c0f2c164c60b31.png)

图10. 论坛上发现的同样的代码特征

观察网站的主逻辑后，我们决定分析分析其他功能的页面代码，此时我们发现页面上存在安装`sagawa.apk` Android应用的代码：

[![](https://p1.ssl.qhimg.com/t018ec6191cc93a7bf7.png)](https://p1.ssl.qhimg.com/t018ec6191cc93a7bf7.png)

图11. Android应用安装链接

不幸的是，此时该链接已失效，会跳转到一个中文404页面：

[![](https://p5.ssl.qhimg.com/t01a3a03a9210b2cb6a.png)](https://p5.ssl.qhimg.com/t01a3a03a9210b2cb6a.png)

图12. 中文404页面

完成对该网站的初步检查后，我们分析了该域名的WHOIS信息。该服务器位于台湾地区，域名注册时间为2018年7月16日。

[![](https://p0.ssl.qhimg.com/t016863b49c6833c1cc.png)](https://p0.ssl.qhimg.com/t016863b49c6833c1cc.png)

图13. C2服务器位置信息

令人惊讶的是，我们发现恶意活动并不仅限于这个域名。我们可以找到347个域名，这些域名对快递官网域名的第一部分或者最后一部分域名做了修改。攻击者使用如下3个邮箱来注册这些域名。

```
mantianxing0111[at]yahoo.co.jp （注册104个域名）
2509677308[at]qq.com （注册55个域名）
21449497[at]qq.com （注册188个域名）
```

[![](https://p4.ssl.qhimg.com/t01d03f7d70d502a49f.png)](https://p4.ssl.qhimg.com/t01d03f7d70d502a49f.png)

图14. 伪造域名部分列表

我们决定检查该列表中的某些域名。这些网站大部分都已注册，但没被使用过。某些域名已连接到托管服务器（托管服务器主要位于台湾地区），但并不包含网页内容。然而，某些网站上的确包含同样的钓鱼页面。

我们针对性检查了结尾为`-iso.com`以及`-wow.com`的那些域名。在检查过程中，我们发现了另一个脚本，该脚本与`-ba.com`网站上的脚本非常相似，但并不会将用户重定向到电话号码页面，而是在用户点击网页时，下载`sagawa.apk`应用。以`-wow.com`结尾的域名并不会收集用户手机号码，也不像`-ba.com`的域名那样包含`pp.html`、`pp2.html`或者`loding1.html`页面。此外，该域名会使用英文的404页面。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0193a92e45c7c66757.jpg)

图15. 投放`sagawa.apk`应用的脚本



## 三、应用分析

我们分析的APK哈希值为`92cd2e43bf85703f92a493668be3d777c3d3cfab3f674b62bd334ddc082ac50d`。

### <a class="reference-link" name="%E9%87%8A%E6%94%BE%E5%99%A8"></a>释放器

首先我们分析的是APK文件的内容。

我们使用内部分析工具分析样本，分析报告部分内容如下图所示。应用的包名为`fang.tang.sha`，除了与正常APK文件一样包含`classes.dex`外，还包含适配不同架构的一个库（`libxxn.so`）、一个asset文件（`nini.dll`）。这已经是一个危险标志：正常Android应用不需要依赖MS Windows库。

[![](https://p5.ssl.qhimg.com/t01d2845b2a7369875f.png)](https://p5.ssl.qhimg.com/t01d2845b2a7369875f.png)

图16. APK报告摘抄

快速检查后，我们发现`nini.dll`其实是经过加密处理的一个文件，这引起了我们的好奇心，决定开始分析apk文件。

首先我们分析了`AndroidManifest.xml`文件，其中包含应用的大部分信息，比如权限信息、Activity和服务信息等。我们首先注意到应用会请求大量可疑权限：

[![](https://p1.ssl.qhimg.com/t01191487ded9ec1ce5.png)](https://p1.ssl.qhimg.com/t01191487ded9ec1ce5.png)

图17. APK过滤器

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017758b39b763d771d.png)

图18. APK权限

然而还有另一处重要细节，`classes.dex`文件中并不包含`AndroidManifest`中的类和函数。应用使用的所有Activity以及服务都需要提前在`Manifest`中提前声明，声明不存在的类并没有意义。这里可以推测出来，应用在执行期间会动态加载其他一些代码。

应用在执行时会启动一个`webview`，显示攻击者正在伪造的快递服务主页。应用会请求注册为处理SMS的默认应用并在后台运行，无视电池优化策略。与此同时，应用图标会从界面中消失，并在后台保持运行。

由于应用与用户的交互较少，因此我们来看一下应用代码。

应用的执行流程非常简单：应用首先加载`libxxn.so`，然后执行`run()`函数（位于`Java_taii_YANGG_run`共享对象中）。该函数会解密`nini.dll`文件，加载解密后的文件（在我的测试设备上该文件位于`/data/user/0/fang.tang.sha/app_cache`目录中）。应用会动态加载该文件，我们可以在`adb logcat`命令的输出中验证这一点：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01abfe6ee29d8103e3.png)

图19. adb logcat输出

该文件在加载后就会被立即删除，加大取证难度。幸运的是，我们可以使用FRIDA（非常方便灵活的一个开源套件）来停止执行流程，在文件被删除前保存该文件。

[FRIDA](https://www.frida.re/)是逆向Android应用的一款工具（并且功能不局限于此），也能适用于多个架构，可以在root和非root设备上使用（非root设备上需要进一步配置）。大家可以访问[Github页面](https://github.com/ddurando/frida-scripts)下载我所使用的脚本。

### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E8%BD%BD%E8%8D%B7"></a>攻击载荷

释放出来的`mycode.jar`文件中包含一个`classes.dex`文件，恶意软件使用`libxxn.so`库中的`DexClassLoader`函数来加载该文件。

载荷看起来像是FakeSpy（2018年6月份发现的一款恶意软件）的变种，包含前一代版本所具备的大部分功能，但同样包含一些新功能。

### <a class="reference-link" name="%E5%8A%9F%E8%83%BD%E5%88%86%E6%9E%90"></a>功能分析

[![](https://p0.ssl.qhimg.com/t01836a6bda63eb6550.png)](https://p0.ssl.qhimg.com/t01836a6bda63eb6550.png)

图20. SMS信息收集

恶意软件会请求成为默认的SMS应用，因此该应用具备拦截SMS消息的能力并不奇怪。当设备接收到消息时，应用会记录消息中的所有信息，并将其发送给C2服务器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014f3701d54f0c2c89.png)

图21. C2通信数据中包含目标号码

此外，这款恶意软件还可以创建SMS并发送至其他设备。实际上这也是恶意软件的传播方式。移动设备一旦被感染，就会开始与C2服务器通信，在SMS中嵌入指向攻击者控制域名的链接，尝试通过SMS感染其他手机号对应的设备。

在图22中，我们使用FRIDA控制`SMSmanager`这个Android类，然后修改其中的`sendTextMessage()`函数，只记录下恶意消息内容，并没有实际发送恶意消息。

[![](https://p5.ssl.qhimg.com/t01ccf1b519af71d220.png)](https://p5.ssl.qhimg.com/t01ccf1b519af71d220.png)

图22. 发送给目标的SMS

恶意软件还可以获取当前设备上已安装的所有应用列表以及其他信息（如IMEI以及手机号），将这些信息以JSON文件形式发送给C2服务器。利用这种方法，攻击者可以获取该设备的所有状态信息。

[![](https://p0.ssl.qhimg.com/t01f9e4a52199d0d29c.png)](https://p0.ssl.qhimg.com/t01f9e4a52199d0d29c.png)

图23. 发送至C2服务器的应用信息

最后，恶意软件还可以向服务器发送完整的崩溃报告。

### <a class="reference-link" name="%E5%BC%82%E5%B8%B8%E7%89%B9%E5%BE%81"></a>异常特征

该样本中包含一些奇怪的特征，因此我们认为恶意软件仍处于开发状态。

C2服务器地址以`URL`名称保存在`sharedPreferences`中，这个值最开始设置为`125.227.0.22`，但可以在应用执行过程中通过`ChangeIP()`函数动态修改，该函数会检查执行时间是否已超过1分钟，如果满足该条件，则从加密的字符串中解出新的C2服务器IP地址。该字符串指向一个推特账户，其用户名包含新的IP地址，可以使用简单的字符串操作进行解码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b0c6422979900e9d.png)

图24. 用于获取新C2地址的推特账户

然而，即便dex文件中存在解密代码，根据我们的分析，恶意软件似乎从来不会使用这段代码。相反，应用会在活动期间始终与第一个C2地址通信。我们尝试将HTTP流量重定向修改后的C2地址，但并没有收到任何响应。

恶意软件同样包含指向`/sdcard/new.apk`文件的多处引用，可以利用给定的URL下载文件，然后检查设备是否包含名为`ni.vb.bi`的一个应用，如果包含该应用，则不会安装下载的文件。然而，在执行期间恶意软件永远不会调用下载文件的函数。

[![](https://p1.ssl.qhimg.com/t018e8bdbbca8f2f448.png)](https://p1.ssl.qhimg.com/t018e8bdbbca8f2f448.png)

图25. 安装`new.apk`的函数

恶意软件的一个类中包含`main()`和`System.out.println()`函数，Android APK中并不需要这些函数，但在Java文件中很常见，这表明开发者可能想测试某些功能，或者只是从其他源中复制粘贴代码。

[![](https://p4.ssl.qhimg.com/t01032d5932ad6ec30f.png)](https://p4.ssl.qhimg.com/t01032d5932ad6ec30f.png)

图26. 测试main()函数

恶意软件还会请求Device Admin权限，并且包含一个`DeviceAdminReceiver`类，但从来没有请求权限来使用这个类，因此这个类永远无法发挥作用。

[![](https://p0.ssl.qhimg.com/t01dbd6ba061c8e6b09.png)](https://p0.ssl.qhimg.com/t01dbd6ba061c8e6b09.png)

图27. Device Admin函数

在分析过程中，我们发现恶意样本几乎每天都会更新证书，表明另一端至少有某些人在维护整个基础设施。



## 四、总结

总而言之，参与此次攻击活动的幕后黑手拥有大量域名，这些域名伪造的是日本快递服务商的真实域名，这意味着他们正在为攻击活动投入大量时间及域名，但可能仍在考虑从这些资源中获取丰厚利润的方法。利用攻击者邮箱注册的域名大多数处于非活跃状态，但这并不意味着这些域名永远不会被使用。网站上存在的脚本、注释以及无用的代码行可能表明攻击者仍在改进攻击方式，尝试使用不同的方法来实现他们的既定目标。

不幸的是，我们无法确定攻击者为什么要收集手机号，但可以猜测攻击者会利用这些信息来发起其他恶意攻击，或者将这些信息售卖给其他攻击者。

这款恶意软件以及此次攻击活动似乎仍处于早期研发阶段。恶意软件基于已有代码库开发而来，但攻击者尝试改进代码，添加其他功能，有些功能目前仍没有发挥作用，但可能在将来会有所变化。



## 五、解决方案

Fortinet产品可以防御此类攻击，已将释放器标识为`Android/Agent.CIJ!tr`，将攻击载荷标识为`Android/Fakespy.Z!tr`。



## 六、IOC

释放器哈希值：

```
24072be590bec0e1002aa8d6ef7270a3114e8fe89996837a8bc8f6a185d9690e 92cd2e43bf85703f92a493668be3d777c3d3cfab3f674b62bd334ddc082ac50d 01caceb86d3e2a383eeab4af98c55a2ec7b82ae0972594866b13fc0c62c93d74
```

攻击载荷哈希值：

```
b7f4850b243649cdba97fd3bb309aa76fe170af80fa9c6ee5edd623dac2ce4e2 00ce9ffe9cca59df86125747c3a2e548245bf1b0607bc8f080fd3c501d9fc3f0
```

C2服务器地址：

```
sagawa-ba[.]com
sagawa-wow[.]com
sagawa-iso[.]com
```

我们的Web Filter服务同样会过滤出其他344个域名。
