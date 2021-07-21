> 原文链接: https://www.anquanke.com//post/id/86507 


# 【技术分享】使用Frida绕过Android SSL Re-Pinning


                                阅读量   
                                **299435**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：techblog.mediaservice.net
                                <br>原文地址：[https://techblog.mediaservice.net/2017/07/universal-android-ssl-pinning-bypass-with-frida/](https://techblog.mediaservice.net/2017/07/universal-android-ssl-pinning-bypass-with-frida/)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p0.ssl.qhimg.com/t01eacc7d9f484916ec.jpg)](https://p0.ssl.qhimg.com/t01eacc7d9f484916ec.jpg)**



作者：for_while

预估稿费：40RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**Android SSL Re-Pinning**



在Android应用中可以找到两种SSL Pinning的实现：自己实现的和官方推荐的。前者通常使用单个方法，执行所有证书检查（可能使用自定义库），返回一个布尔值来判断是否正常。这意味着我们可以通过识别进行判断的关键函数，然后hook它的返回值来轻松地绕过此方法。针对这种检测方法，可以使用类似以下的Frida JavaScript脚本：

[![](https://p5.ssl.qhimg.com/t014e6be8bfe0f6e9e8.png)](https://p5.ssl.qhimg.com/t014e6be8bfe0f6e9e8.png)

hook关键函数，使他永远返回True, 绕过检查。

不过当SSL Pinning是根据Android的[官方文档](https://developer.android.com/training/articles/security-ssl.html)实现时，事情变得更加艰难。不过现在还是有很多优秀的解决方案，比如定制的Android图像，底层框架，使socket.relaxsslcheck = yes等等。几乎每个尝试绕过SSL Pinning的方案都是基于操纵SSLContext。我们可以用Frida操纵SSLContext吗？我们想要的是一个通用的方法，我们想用Frida JavaScript脚本来实现这个目的。

这里的想法是根据官方文档的建议来实现的，所以我们将SSL Pinning Java代码移植到了Frida JavaScript。

它是这样工作的：

1. 从设备加载我们的 CA证书；

2. 创建包含我们信任的CA证书的KeyStore；

3. 创建一个TrustManager，使它信任我们的KeyStore中的CA证书。

当应用程序初始化其SSLContext时，我们会劫持SSLContext.init()方法，当它被调用时，我们使用我们之前准备的TrustManager , 把它设置为第二个参数。( SSLContext.init(KeyManager，TrustManager，SecuRandom) )。

这样我们就使应用程序信任我们的CA了。<br>

[![](https://p0.ssl.qhimg.com/t0122d520a65935c452.png)](https://p0.ssl.qhimg.com/t0122d520a65935c452.png)



**执行示例：**<br>

****

```
$ adb push burpca-cert-der.crt /data/local/tmp/cert-der.crt
$ adb shell "/data/local/tmp/frida-server &amp;"

$ frida -U -f it.app.mobile -l frida-android-repinning.js --no-pause

[…]
[USB::Samsung GT-31337::['it.app.mobile']]-&gt;
[.] Cert Pinning Bypass/Re-Pinning
[+] Loading our CA...
[o] Our CA Info: CN=PortSwigger CA, OU=PortSwigger CA, O=PortSwigger, L=PortSwigger, ST=PortSwigger, C=PortSwigger
[+] Creating a KeyStore for our CA...
[+] Creating a TrustManager that trusts the CA in our KeyStore...
[+] Our TrustManager is ready...
[+] Hijacking SSLContext methods now...
[-] Waiting for the app to invoke SSLContext.init()...
[o] App invoked javax.net.ssl.SSLContext.init...
[+] SSLContext initialized with our custom TrustManager!
[o] App invoked javax.net.ssl.SSLContext.init...
[+] SSLContext initialized with our custom TrustManager!
[o] App invoked javax.net.ssl.SSLContext.init...
[+] SSLContext initialized with our custom TrustManager!
[o] App invoked javax.net.ssl.SSLContext.init...
[+] SSLContext initialized with our custom TrustManager!
```

上述示例，应用程序调用了四次SSLContext.init，这意味着它验证了四个不同的证书（其中两个被第三方跟踪库使用）。

frida脚本： 在[这里](https://techblog.mediaservice.net/wp-content/uploads/2017/07/frida-android-repinning_sa-1.js)下载，或者[这里](https://codeshare.frida.re/@pcipolloni/universal-android-ssl-pinning-bypass-with-frida/)

Frida＆Android： [https://www.frida.re/docs/android/](https://www.frida.re/docs/android/)

```
/* 
   Android SSL Re-pinning frida script v0.2 030417-pier 

   $ adb push burpca-cert-der.crt /data/local/tmp/cert-der.crt
   $ frida -U -f it.app.mobile -l frida-android-repinning.js --no-pause

   https://techblog.mediaservice.net/2017/07/universal-android-ssl-pinning-bypass-with-frida/
*/

setTimeout(function()`{`
    Java.perform(function ()`{`
    	console.log("");
	    console.log("[.] Cert Pinning Bypass/Re-Pinning");

	    var CertificateFactory = Java.use("java.security.cert.CertificateFactory");
	    var FileInputStream = Java.use("java.io.FileInputStream");
	    var BufferedInputStream = Java.use("java.io.BufferedInputStream");
	    var X509Certificate = Java.use("java.security.cert.X509Certificate");
	    var KeyStore = Java.use("java.security.KeyStore");
	    var TrustManagerFactory = Java.use("javax.net.ssl.TrustManagerFactory");
	    var SSLContext = Java.use("javax.net.ssl.SSLContext");

	    // Load CAs from an InputStream
	    console.log("[+] Loading our CA...")
	    cf = CertificateFactory.getInstance("X.509");
	    
	    try `{`
	    	var fileInputStream = FileInputStream.$new("/data/local/tmp/cert-der.crt");
	    `}`
	    catch(err) `{`
	    	console.log("[o] " + err);
	    `}`
	    var bufferedInputStream = BufferedInputStream.$new(fileInputStream);
	  	var ca = cf.generateCertificate(bufferedInputStream);
	    bufferedInputStream.close();

		var certInfo = Java.cast(ca, X509Certificate);
	    console.log("[o] Our CA Info: " + certInfo.getSubjectDN());

	    // Create a KeyStore containing our trusted CAs
	    console.log("[+] Creating a KeyStore for our CA...");
	    var keyStoreType = KeyStore.getDefaultType();
	    var keyStore = KeyStore.getInstance(keyStoreType);
	    keyStore.load(null, null);
	    keyStore.setCertificateEntry("ca", ca);
	    
	    // Create a TrustManager that trusts the CAs in our KeyStore
	    console.log("[+] Creating a TrustManager that trusts the CA in our KeyStore...");
	    var tmfAlgorithm = TrustManagerFactory.getDefaultAlgorithm();
	    var tmf = TrustManagerFactory.getInstance(tmfAlgorithm);
	    tmf.init(keyStore);
	    console.log("[+] Our TrustManager is ready...");

	    console.log("[+] Hijacking SSLContext methods now...")
	    console.log("[-] Waiting for the app to invoke SSLContext.init()...")

	   	SSLContext.init.overload("[Ljavax.net.ssl.KeyManager;", "[Ljavax.net.ssl.TrustManager;", "java.security.SecureRandom").implementation = function(a,b,c) `{`
	   		console.log("[o] App invoked javax.net.ssl.SSLContext.init...");
	   		SSLContext.init.overload("[Ljavax.net.ssl.KeyManager;", "[Ljavax.net.ssl.TrustManager;", "java.security.SecureRandom").call(this, a, tmf.getTrustManagers(), c);
	   		console.log("[+] SSLContext initialized with our custom TrustManager!");
	   	`}`
    `}`);
`}`,0);
```


