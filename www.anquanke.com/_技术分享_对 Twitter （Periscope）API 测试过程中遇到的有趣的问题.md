> 原文链接: https://www.anquanke.com//post/id/86573 


# 【技术分享】对 Twitter （Periscope）API 测试过程中遇到的有趣的问题


                                阅读量   
                                **75055**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：innerht.ml
                                <br>原文地址：[http://blog.innerht.ml/testing-new-features/](http://blog.innerht.ml/testing-new-features/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01d2dbe1f81516f772.jpg)](https://p2.ssl.qhimg.com/t01d2dbe1f81516f772.jpg)



译者：[bottlecolor](http://bobao.360.cn/member/contribute?uid=2938038026)

预估稿费：130RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

距离我发上一篇博客已经将近一年了，所以我想我要写一些有趣的东西：我在 Twitter (Periscope) 上发现了一个 bug。这个 bug（CSRF）本身并没有什么吸引人的地方，不过我觉得我发现它的方法和我的思考过程应该是值得分享的。

几天前我注意到 Twitter，或者说是 Periscope 发布了一个 Producer API([https://blog.twitter.com/developer/en_us/topics/tools/2017/introducing-the-periscope-producer-api.html](https://blog.twitter.com/developer/en_us/topics/tools/2017/introducing-the-periscope-producer-api.html))，这个 API 只对其一些合作伙伴开放，它的用处是可以在一个 Periscope 账户上直接播放由第三方应用（比如一些外部相机设备）拍摄的直播视频。

[![](https://p3.ssl.qhimg.com/t0133d60ebdbeb99607.png)](https://p3.ssl.qhimg.com/t0133d60ebdbeb99607.png)

这听起来和OAuth有关，根据我以往的经验，OAuth的使用通常是存在问题的，所以我打算仔细研究一下。

我遇到的第一个问题是这个API甚至没有公开的使用文档，因为在这篇博客([https://blog.twitter.com/developer/en_us/topics/tools/2017/introducing-the-periscope-producer-api.html](https://blog.twitter.com/developer/en_us/topics/tools/2017/introducing-the-periscope-producer-api.html))中提到了一些正在使用这个API的合作伙伴，所以我想尝试着去了解他们是如何做API交互的。然而不幸的是为了使用他们在 Periscope 上的功能必须对他们进行付费订阅，即使我愿意付费的话也无济于事，因为他们是一些Web应用程序，利用API进行交互的工作是由服务器完成的。

接下来我注意到一个手机应用也在使用这个API（Mevo on iOS），在手机应用中，OAuth请求一般是由客户端直接发起的，并且可以通过劫持流量来理解API的调用。在OAuth 1.0a 中使用签名机制来防止流量劫持，而OAuth 2.0仅仅依赖HTTPS来保证传输的安全性。因此，除非应用程序使用了一些严格的证书钉扎技术（其中大部分可以通过SSL Kill Switch 2解决），那么应该不会有问题。

[![](https://p2.ssl.qhimg.com/t011cf5f0c88a9391ab.jpg)](https://p2.ssl.qhimg.com/t011cf5f0c88a9391ab.jpg)

下一个遇到的问题是为了开始使用APP，你必须有一个Mevo相机。这个相机在Amazon上的价格是399.99美元，所以我也不愿意为了测试一个可能不存在漏洞的东西而去买这么一个相机。

所以我尝试了我并不熟悉的领域：逆向工程。我准备了一个已越狱的并安装了Clutch([https://github.com/KJCracks/Clutch](https://github.com/KJCracks/Clutch)) 的iPhone来解密IPA文件，用class-dump([https://github.com/nygard/class-dump](https://github.com/nygard/class-dump))生成Objective-C头文件，还用Hopper([https://www.hopperapp.com/index.html](https://www.hopperapp.com/index.html) )来反汇编代码。

 开始的时候我从头文件中搜索“Periscope”这个词，因为很可能他们用这个名字的类来处理与Periscope交互的逻辑。

[![](https://p0.ssl.qhimg.com/t01dd77efd2e4aa923e.png)](https://p0.ssl.qhimg.com/t01dd77efd2e4aa923e.png)

像PeriscopeBroadcastCreateOperation.h和PeriscopeBroadcastPublishAPIOperation.h这样的文件名引起了我的注意，因为它们与Periscope的API调用相关。 通过观察这些文件，我注意到他们都扩展了PeriscopeAPIOperation类，所以这个类是下一个需要关注的地方。



```
//
//     Generated by class-dump 3.5 (64 bit).
//
//     class-dump is Copyright (C) 1997-1998, 2000-2001, 2004-2013 by Steve Nygard.
//
#import "GroupOperation.h"
@class NSDictionary, NSMutableURLRequest, PeriscopeOAuthOperation, PeriscopeRefreshTokenAPIOperation, URLSessionTaskOperation;
@interface PeriscopeAPIOperation : GroupOperation
`{`
    NSDictionary *_JSON;
    URLSessionTaskOperation *_taskOperation;
    PeriscopeRefreshTokenAPIOperation *_refreshTokenOperation;
    PeriscopeOAuthOperation *_oauthOperation;
    NSMutableURLRequest *_request;
`}`
+ (void)removeCookies;
+ (void)logout;
+ (id)userID;
+ (id)refreshToken;
+ (id)accessToken;
+ (void)updateAccessToken:(id)arg1;
+ (void)setAccessToken:(id)arg1 refreshToken:(id)arg2 forAccount:(id)arg3;
+ (_Bool)isUserAuthorized;
+ (id)buildRequestForPath:(id)arg1 params:(id)arg2 query:(id)arg3 queryItems:(id)arg4 HTTPMethod:(id)arg5 accessToken:(id)arg6;
@property(retain, nonatomic) NSMutableURLRequest *request; // @synthesize request=_request;
@property(retain, nonatomic) PeriscopeOAuthOperation *oauthOperation; // @synthesize oauthOperation=_oauthOperation;
@property(retain, nonatomic) PeriscopeRefreshTokenAPIOperation *refreshTokenOperation; // @synthesize refreshTokenOperation=_refreshTokenOperation;
@property(retain, nonatomic) URLSessionTaskOperation *taskOperation; // @synthesize taskOperation=_taskOperation;
@property(retain) NSDictionary *JSON; // @synthesize JSON=_JSON;
- (void).cxx_destruct;
- (void)repeatOperation;
- (_Bool)operationHas401Code;
- (_Bool)shouldHandle401Code;
- (void)operationDidFinish:(id)arg1 withErrors:(id)arg2;
- (void)finishWithError:(id)arg1;
- (id)initWitMethod:(id)arg1 params:(id)arg2;
- (id)initWitMethod:(id)arg1 params:(id)arg2 HTTPMethod:(id)arg3;
- (id)initWitMethod:(id)arg1 queryItems:(id)arg2;
- (id)initWitMethod:(id)arg1 params:(id)arg2 HTTPMethod:(id)arg3 queryItems:(id)arg4;
@end
```

哇，这是相当多的属性和方法。 看这些方法名称，这个类应该负责处理对Periscope的API调用。

我打开Hopper来测试我的理论，确定的是，他们调用`initWitMethod`方法来发起一个带有参数的API调用。

[![](https://p4.ssl.qhimg.com/t013d30c7990fcfe972.png)](https://p4.ssl.qhimg.com/t013d30c7990fcfe972.png)

从那里开始，我只需要找出还有其他哪些地方调用了这个方法，这样我可以有一个Periscope API调用列表和参数名。 通过之后的分析，我还从静态字符串中提取了Mevo的API root，`client_id`和`client_secret`。

在经历所有这些麻烦之后，我终于可以开始检查Periscope的OAuth实现的安全性。 我很快发现初始授权端点没有CSRF保护。 第三方的Periscope应用程序可以请求对用户的Periscope帐户的完全权限，攻击者可能会准备恶意的第三方应用程序，并让用户在不知不觉中对其进行授权，以代表用户执行操作。

关于该漏洞的具体细节可以在下面的报告中找到，虽然相对来说可能不那么有趣。

<br>

**结论**

我关注Twitter的更新，因为我相信这可以确保我可以在任何人之前测试新的功能。

此外，仅向某些方开放的功能并不意味着您无法在公开之前进行测试，您只需要找到一种访问它们的方法。 底线的做法是可以请求程序允许您访问测试的功能（尽管Twitter尚未响应我的请求）。

最后但并非最不重要的是，当有些事情需要你支付时，不要马上退出。 即使你像我一样找不到绕过付款的方式。无论如何这是一个很好的机会，因为人们一般不想投资于不确定性，这就意味着一个探索没有人看到的地方的机会。 我见识过有人这样做之后获得了成功。

<br>

**引用**

HackerOne上的原始报告([https://hackerone.com/reports/215381](https://hackerone.com/reports/215381))
