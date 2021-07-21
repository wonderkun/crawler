> 原文链接: https://www.anquanke.com//post/id/147090 


# 如何编写Swift代码拦截SSL Pinning的HTTPS请求


                                阅读量   
                                **137909**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0146efb22636a657aa.png)](https://p0.ssl.qhimg.com/t0146efb22636a657aa.png)



## 一、前言

如果想检查iOS Apps中的HTTPS请求，最常用的方法就是中间人（MITM）攻击。这种技术需要使用某台主机作为代理服务器，为客户端提供服务。为了保证攻击成功，客户端需要将代理服务器的证书安装到设备的全局信任存储区中。这样处理后，客户端就会将证书添加到白名单中，允许与代理服务器之间的HTTPS通信。

如下图所示，我们可以通过[mitmproxy](https://mitmproxy.org/)来查看CNN这款iOS应用的流量。在查看流量之前，我已经将代理服务器的证书安装到设备上，大家可以参考[mitmproxy](https://docs.mitmproxy.org/stable/concepts-certificates/)官网了解具体操作步骤。

[![](https://p4.ssl.qhimg.com/t012d530c19871ea541.gif)](https://p4.ssl.qhimg.com/t012d530c19871ea541.gif)



## 二、SSL证书Pinning

如果想保护应用免受MITM攻击影响，一种方法就是使用SSL校验证书绑定（SSL certificate pinning）。此时受信服务器的证书副本会打包到iOS应用中，还有一些附加代码可以确保应用只与使用特定证书的服务器通信。当SSL证书绑定处于激活状态时，应用不会将任何请求发送到不受信任的任何服务器上。因此，MITM代理服务器无法提取这些请求数据，因为此时请求并没有通过足够安全的网络通道来发送。

Twitter iOS应用采用了SSL证书绑定这种安全机制，适用于发往[https://api.twitter.com](https://api.twitter.com./)的请求，因此类似[mitmproxy](https://mitmproxy.org/)以及[Charles Proxy](https://www.charlesproxy.com/)之类的MITM工具无法查看与Twitter api有关的任何请求。

[![](https://p0.ssl.qhimg.com/t01b858b7c55aa65243.png)](https://p0.ssl.qhimg.com/t01b858b7c55aa65243.png)

有一种方法可以绕过SSL证书绑定，那就是在具体请求通过受保护的HTTPS通道发送之前，尝试拦截这个请求。这种技术需要我们将代码植入到应用中，这样就能直接访问我们要查看的`URLRequest`对象。因此我们可以先来看一下Apple的URL加载系统。



## 三、URLProtocol

Apple的URL加载系统会定义不同的URLProtocol来处理不同类型的URL。如果要创建我们自定义的URLProtocol子类，可以采用如下步骤：

1、每个URLProtocol子类最基本的框架如下：

```
class CustomUrlProtocol: URLProtocol `{`

    open override class func canInit(with request: URLRequest) -&gt; Bool `{`
        //Logic to determine whether this URLProtocol class knows how to handle the request
        return true
    `}`

    open override class func canonicalRequest(for request: URLRequest) -&gt; URLRequest `{`
        return request
    `}`

    override func startLoading() `{`
        //Implementation logic to process the request
    `}`
    override func stopLoading() `{``}`


`}`
```

2、使用加载系统注册新的URLProtocol子类。

```
URLProtocol.registerClass(CustomUrlProtocol.self)
```

3、在`canInit`函数中添加自定义的记录函数。

```
class CustormUrlProtocol: URLProtocol `{`

    var connection: NSURLConnection?
    var response: URLResponse?
    var data: NSMutableData?


    static var requestCount = 0

    open override class func canInit(with request: URLRequest) -&gt; Bool `{`

        guard let url = request.url, let scheme = url.scheme else `{`
            return false
        `}`
        guard ["http", "https"].contains(scheme) else `{`
            return false
        `}`
        if let _ = URLProtocol.property(forKey: "CustormUrlProtocol", in: request) `{`
            return false
        `}`

        if NetworkInterceptor.shared.shouldIgnoreLogging(url: url)`{`
            return false
        `}`

        requestCount = requestCount + 1
        NSLog("Request #(requestCount): CURL =&gt; (request.cURL)")
        NetworkInterceptor.shared.logRequest(urlRequest: request)

        return false
    `}`


`}`
```

我们将以cURL命令格式，将URLRequest实例按照字符串表示方式输出到控制台以及Slack通道中（参考第28行代码）。



## 四、技术点汇总

因此，为了查看所有的网络请求，我们需要执行如下步骤：

1、创建一个新的Xcode Dynamic Framework工程，可以参考Github上[源码](https://github.com/depoon/NetworkInterceptor)。

2、创建自定义的URLProtocol，比如CustormUrlProtocol。添加自定义代码以生成cURL命令字符串。此外我们还可以将cURL字符串打印到设备控制台，或者发送到Slack通道上（参考[此处](https://github.com/depoon/NetworkInterceptor/blob/master/NetworkInterceptor/Source/RequestInterceptor/CustomUrlProtocolRequestInterceptor.swift#L51-L155)代码）。

3、将新的URLProtocol子类注册到加载系统中，调整方法以确保我们的协议类能先于任何已有的Apple协议类执行（参考[此处](https://github.com/depoon/NetworkInterceptor/blob/master/NetworkInterceptor/Source/RequestInterceptor/CustomUrlProtocolRequestInterceptor.swift#L11-L49)代码）。

4、在工程中创建一个Slack通道请求记录类（参考[此处](https://github.com/depoon/NetworkInterceptor/blob/master/NetworkInterceptor/Source/RequestLogger/SlackRequestLogger.swift)代码）。

5、编译整个框架。

6、我们可以将该框架拖拽到其他Xcode工程中，开始使用我们新增的功能。记得检查控制台以及slack通道中的cURL命令。

7、对于iOS设备的`.ipa`文件，我们需要将该框架（匹配iphone架构）注入到ipa文件中。



## 五、代码注入

大家可以参考我前面发表的&lt;a href=”https://medium.com/[@kennethpoon](https://github.com/kennethpoon)/how-to-perform-ios-code-injection-on-ipa-files-1ba91d9438db”&gt;文章了解Dynamic Library框架代码注入技术，好消息是我们不需要越狱就能完成这个任务。

需要注意的是，我们的确无法对AppStore上的iOS应用执行代码注入，因为这些应用受到数字版权管理（DRM）保护。幸运的是，我们可以在[这个网站](https://www.iphonecake.com)上找到被破解的AppStore应用。然而，由于我们并不知道这些破解应用有没有被篡改过，是否添加了恶意代码，因此需要自己承担风险。



## 六、Tinder API请求

当我将动态框架应用于Tinder iOS应用时，我可以看到一些请求数据，如下图所示：

[![](https://p0.ssl.qhimg.com/t0107fb2b8299a304a1.jpg)](https://p0.ssl.qhimg.com/t0107fb2b8299a304a1.jpg)



[![](https://p1.ssl.qhimg.com/t01405c7cbdcbd29d55.png)](https://p1.ssl.qhimg.com/t01405c7cbdcbd29d55.png)

现在比如说我不喜欢某人的Tinder账户，那么也能看到“Pass”掉某人的Api请求。

此外，我们还可以注意到Tinder也会往Facebook Api上发送请求，如下图所示。这是因为Tinder应用中也集成了FacebookSDK，用到了登录之类的功能。

[![](https://p0.ssl.qhimg.com/t013b3605ac3d3548d5.png)](https://p0.ssl.qhimg.com/t013b3605ac3d3548d5.png)

遗憾的是，Tinder应用上并没有启用SSL证书绑定，任何人都可以使用MITM工具来检查所有请求。因此我们来找一下另一款应用。



## 七、Twitter API请求

前文提到过，由于SSL证书绑定机制，因此MITM工具无法查看针对[api.twitter.com](https://api.twitter.com/)的任何请求数据。尝试登录Twitter时，应用会抛出认证错误信息，不允许相关请求通过网络发送给服务端。

[![](https://p5.ssl.qhimg.com/t01542cc496a5f5c13d.png)](https://p5.ssl.qhimg.com/t01542cc496a5f5c13d.png)

将我们的框架注入并禁用代理后，我们可以观察到“/auth/1/xauth_password.json ”这个api请求，请求参数中包含我们的ID以及密码值（可以观察Slack通道第二条消息中的最后一行）。

同时还需要注意到，成功登录Twitter后，应用就会崩溃，因为应用检测到我正在使用自己的开发配置信息来签名这个应用，而应用的签名与KeyChain的安全性有冲突。这个问题解决起来并不麻烦，但为了节省文章篇幅，这里我不会去介绍如何具体解决这个特定问题。



## 八、相关演讲

2018年5月30日，我在新加坡举办的iOS Dev Scout Meetup会议上作了一次[演讲](https://engineers.sg/video/intercepting-network-requests-ios-dev-scout--2639)，会上我演示了即使在SSL pinning处于激活状态，我也能探测Twitter应用的HTTPS请求。

大家可以参考Github上的[NetworkInterceptor](https://github.com/depoon/NetworkInterceptor)以及[iOSDylibInjectionDemo](https://github.com/depoon/iOSDylibInjectionDemo)代码。



## 九、总结

希望本文对大家有所帮助。大家可以尝试相关代码，观察自己最喜欢的iOS应用的请求。如果实验成功或者遇到什么问题，欢迎大家通过[de_poon@hotmail.com](mailto:de_poon@hotmail.com)邮箱联系我。
