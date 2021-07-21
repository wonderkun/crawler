> 原文链接: https://www.anquanke.com//post/id/201219 


# Android https过反抓包的一些总结


                                阅读量   
                                **918058**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



## [![](https://p2.ssl.qhimg.com/t01a7a0dd2a561578bf.jpg)](https://p2.ssl.qhimg.com/t01a7a0dd2a561578bf.jpg)

大家在分析app的协议时，经常会遇到一些app存在反抓包，增加逆向难度。下面小弟我就分情况讨论一下如何解决反抓包问题。



#### <a class="reference-link" name="%E6%83%85%E5%86%B51%EF%BC%9A%E6%8A%93%E5%8C%85%E5%B7%A5%E5%85%B7%E6%97%A0%E6%B3%95%E6%8A%93%E5%88%B0%E5%8C%85%EF%BC%8C%E4%BD%86app%E5%8F%AF%E4%BB%A5%E6%AD%A3%E5%B8%B8%E8%81%94%E7%BD%91%E4%BD%BF%E7%94%A8"></a>情况1：抓包工具无法抓到包，但app可以正常联网使用

可能原因：app内部使用的非http协议，可能是websocket或是tcp协议（qq，微信，百度贴吧等）

解决方案：对于这种情况，只能逆向app进一步去分析底层的二进制协议，暂无其他方法

可能原因：app内部设置了http协议不走代理流量（支付宝，美团等）

解决方案：可以使用一些第三方代理app（如Drony），通过使用vpn，来强制app的http协议走代理流量，从而实现抓包。但如果是需要翻墙的app，则该方法无效，因为翻墙本身需要海外vpn连接，无法再去使用这些代理软件来开启另一个vpn。



#### <a class="reference-link" name="%E6%83%85%E5%86%B52%EF%BC%9A%E6%8A%93%E5%8C%85%E5%B7%A5%E5%85%B7%E6%97%A0%E6%B3%95%E6%8A%93%E5%88%B0https%E5%8C%85%EF%BC%8C%E4%B8%94app%E6%97%A0%E6%B3%95%E8%81%94%E7%BD%91"></a>情况2：抓包工具无法抓到https包，且app无法联网

原因：大部分是app有对服务器证书的校验，因为我们使用的是抓包工具自己的证书，所以app证书校验不过去，也就自然拒绝发送请求，在外界看来app就相当于一个断网的状态。

解决方案1：逆向app，找到发包接口，动态调试下断点来获取https请求和返回的数据

解决方案2：逆向app，找到证书校验的位置，通过hook的方式来过掉校验。

下面我总结了android常用的一些网络框架的过证书校验的方法：



<a class="reference-link" name="HttpUrlConnection%EF%BC%88%E8%BE%83%E5%85%B6%E4%BB%96%E6%A1%86%E6%9E%B6%E7%9B%B8%E6%AF%94%E6%80%A7%E8%83%BD%E4%B8%8D%E9%AB%98%EF%BC%8C%E4%BD%BF%E7%94%A8%E7%9A%84app%E8%BE%83%E5%B0%91)%EF%BC%9A"></a>HttpUrlConnection（较其他框架相比性能不高，使用的app较少)：

```
TrustManager[] trustAllCerts = new TrustManager[]`{`new X509TrustManager() `{`
    public X509Certificate[] getAcceptedIssuers() `{`
        return null;
    `}`
    //重写校验方法，直接返回null通过证书校验
    public void checkClientTrusted(X509Certificate[] certs, String authType) `{`
    `}`
    public void checkServerTrusted(X509Certificate[] certs, String authType) `{`
    `}`
 `}``}`;
 HostnameVerifier hv = new HostnameVerifier() `{`
     @Override
    public boolean verify(String s, SSLSession sslSession) `{`
        //返回true，表示信任该主机名
        return true;
    `}`
`}`;
SSLContext sc = SSLContext.getInstance("TLS");
sc.init(null, trustAllCerts, new SecureRandom());
SSLSocketFactory ssf=sc.getSocketFactory();
//hook证书校验
XposedHelpers.findAndHookMethod(HttpsURLConnection.Class, "setDefaultSSLSocketFactory",
                SSLSocketFactory.class,
                new XC_MethodHook() `{`
                    @Override
                    protected Object beforeHookedMethod(MethodHookParam param) throws Throwable `{`
                        param.args[0]=ssf;
                    `}`
                `}`);
//hook域名校验
XposedHelpers.findAndHookMethod(HttpsURLConnection.Class, "setDefaultHostnameVerifier",
                HostnameVerifier.class,
                new XC_MethodHook() `{`
                    @Override
                    protected Object beforeHookedMethod(MethodHookParam param) throws Throwable `{`
                        param.args[0]=hv;
                    `}`
                `}`);
```

<a class="reference-link" name="okhttp3%EF%BC%88%E5%A4%A7%E5%A4%9A%E6%95%B0%E5%B0%8F%E4%BC%97app%E4%BD%BF%E7%94%A8%E7%9A%84%E7%BD%91%E7%BB%9C%E6%A1%86%E6%9E%B6)%EF%BC%9A"></a>okhttp3（大多数小众app使用的网络框架)：

```
TrustManager[] trustAllCerts = new TrustManager[]`{`new X509TrustManager() `{`
    public X509Certificate[] getAcceptedIssuers() `{`
        return null;
    `}`
    //重写校验方法，直接返回null通过证书校验
    public void checkClientTrusted(X509Certificate[] certs, String authType) `{`
    `}`
    public void checkServerTrusted(X509Certificate[] certs, String authType) `{`
    `}`
 `}``}`;
 HostnameVerifier hv = new HostnameVerifier() `{`
     @Override
    public boolean verify(String s, SSLSession sslSession) `{`
        //返回true，表示信任该主机名
        return true;
    `}`
`}`;
SSLContext sc = SSLContext.getInstance("TLS");
sc.init(null, trustAllCerts, new SecureRandom());
SSLSocketFactory ssf=sc.getSocketFactory();
//Hook
Class&lt;?&gt; okc_builder=XposedHelpers.findClass("okhttp3.OkHttpClient$Builder",classLoader);
Class&lt;?&gt; pinner=XposedHelpers.findClass("okhttp3.CertificatePinner",classLoader);
//hook证书校验
XposedHelpers.findAndHookMethod(okc_builder, "sslSocketFactory",SSLSocketFactory.class,
                new XC_MethodHook() `{`
                    @Override
                    protected Object beforeHookedMethod(MethodHookParam param) throws Throwable `{`
                        param.args[0]=ssf;
                    `}`
                `}`);
//hook域名校验
XposedHelpers.findAndHookMethod(okc_builder, "hostnameVerifier",HostnameVerifier.class,
                new XC_MethodHook() `{`
                    @Override
                    protected Object beforeHookedMethod(MethodHookParam param) throws Throwable `{`
                        param.args[0]=hv;
                    `}`
                `}`);
//hook证书锁定
XposedHelpers.findAndHookMethod(okc_builder, "certificatePinner",pinner,
                 new XC_MethodReplacement() `{`
                    @Override
                    protected Object replaceHookedMethod(MethodHookParam param) throws Throwable `{`
                        return param.thisObject;
                    `}`
                `}`);
```



<a class="reference-link" name="Cronet:"></a>Cronet:

网上关于这个框架的介绍比较少，但是有很多知名app使用了该框架，如今日头条，抖音，微博，youtube等等，官方文档（[https://developer.android.com/guide/topics/connectivity/cronet）](https://developer.android.com/guide/topics/connectivity/cronet%EF%BC%89)

cronet设置证书校验的方式：

```
CronetEngine.Builder builder = new CronetEngine.Builder(AppContext);
String hostname="xxx.com";
//服务器证书
Set&lt;byte[]&gt; pinsSha256=new HashSet&lt;byte[]&gt;();
//将信任的服务器证书的公钥导入
pinsSha256.add(publicKey1);
pinsSha256.add(publicKey2);
...
pinsSha256.add(publicKeyn);
//添加公钥验证，如果服务器的公钥证书不在pinsSha256集合中，则客户端拒绝连接该服务器
Builder.addPublicKeyPins(hostname,pinsSha256,includeSubdomains,expirationDate)
    .enablePublicKeyPinningBypassForLocalTrustAnchors(false);  //设置不允许绕过本地证书校验
CronetEngine cronetEngine = builder.build();
```

解决方案就是hook addPublicKeyPins方法直接让其返回原对象，跳过证书校验：

```
Class&lt;?&gt; okc_builder=XposedHelpers.findClass("org.chromium.net.CronetEngine$Builder",classLoader);
//hook证书锁定
XposedHelpers.findAndHookMethod(cronet_class, "addPublicKeyPins",
                String.class, Set.class, boolean.class, Date.class,
                new XC_MethodReplacement() `{`
                    @Override
                    protected Object replaceHookedMethod(MethodHookParam param) throws Throwable `{`
                        return param.thisObject;
                    `}`
                `}`);
//hook绕过证书校验返回true,允许绕过本地证书校验
XposedHelpers.findAndHookMethod(cronet_class,"enablePublicKeyPinningBypassForLocalTrustAnchors",boolean.class,new XC_MethodHook() `{`
                    @Override
                    protected Object beforeHookedMethod(MethodHookParam param) throws Throwable `{`    
                        param.arg[0]=true;            
                    `}`
                `}`);
```

遗憾的是，大多数app可能会对上述代码做混淆处理，所以对我们快速定位这些代码增加了难度，但依然可以通过参数来匹配这些地方，大多数android或java系统类参数是无法混淆的。网上有个plus版的JustTrustMe就是运用了这种方法来对抗代码混淆（[https://github.com/langgithub/JustTrustMePlus）](https://github.com/langgithub/JustTrustMePlus%EF%BC%89) ，大家可以使用一下。



<a class="reference-link" name="%E6%83%85%E5%86%B5%E4%B8%89%EF%BC%9A%E5%8F%AF%E4%BB%A5%E6%8A%93%E5%88%B0%E5%8C%85%EF%BC%8C%E4%BD%86app%E6%97%A0%E6%B3%95%E8%81%94%E7%BD%91%EF%BC%8C%E8%AF%B7%E6%B1%82%E5%8C%85%E4%B8%AD%E6%B2%A1%E6%9C%89%E6%9C%89%E6%95%88%E6%95%B0%E6%8D%AE%E8%BF%94%E5%9B%9E"></a>情况三：可以抓到包，但app无法联网，请求包中没有有效数据返回

很可能的原因是服务器端有对app客户端的证书校验，所以app虽然可以发送请求，但是服务器因为验证客户端证书不通过，拒绝返回数据。

如soul这个app，其中有客户端，服务端双向验证，在通过服务器证书校验后用fidder抓包会出现如下提示，表示需要客户端证书来验证客户端身份：

[![](https://s1.ax1x.com/2020/03/18/8BjmEq.png)](https://s1.ax1x.com/2020/03/18/8BjmEq.png)

解决方案：一般客户端的证书随app一起打包，如果没有对证书文件进行加密操作，可能存放的位置会在assets目录下，但也可能是加密的形式保存，但具体还是需要逆向分析app，找到设置证书的位置。

证书存放的格式有多种，详情可参考该篇文章：[https://www.cnblogs.com/xq1314/archive/2017/12/05/7987216.html，下面说说各个抓包工具如何导入证书](https://www.cnblogs.com/xq1314/archive/2017/12/05/7987216.html%EF%BC%8C%E4%B8%8B%E9%9D%A2%E8%AF%B4%E8%AF%B4%E5%90%84%E4%B8%AA%E6%8A%93%E5%8C%85%E5%B7%A5%E5%85%B7%E5%A6%82%E4%BD%95%E5%AF%BC%E5%85%A5%E8%AF%81%E4%B9%A6)



<a class="reference-link" name="Fidder:"></a>Fidder:

fidder只支持.cer格式证书，大部分apk中只存放了.p12格式的客户端证书，或是密钥和证书分开存储，这需要我们对证书格式进行转换，这里我们使用openssl：

```
# 将.p12证书转换成.pem格式
$ openssl pkcs12 -in client.p12 -out ClientCertificate.pem -nodes
Enter Import Password:
# 将.pem证书转换成.cer格式
$ openssl x509 -outform der -in ClientCertificate.pem -out ClientCertificate.cer
```

需要注意的是这里使用p12格式的证书是需要密码的，密码需要逆向app获取到。

生成.cer证书后，放入到fidder客户端证书指定路径（上图C:UsersFear1essDocumentsFiddler2ClientCertificate.cer），就可以愉快地抓包啦。。



<a class="reference-link" name="Charles:"></a>Charles:

而charles是支持导入.p12格式的证书，所以就不用进行证书转换：

[![](https://s1.ax1x.com/2020/03/18/8Bju5V.png)](https://s1.ax1x.com/2020/03/18/8Bju5V.png)

[![](https://s1.ax1x.com/2020/03/18/8Bjl2F.png)](https://s1.ax1x.com/2020/03/18/8Bjl2F.png)

[![](https://s1.ax1x.com/2020/03/18/8Bj8KJ.png)](https://s1.ax1x.com/2020/03/18/8Bj8KJ.png)

直接导入p12或pem证书即可。。导入p12证书时同样需要输入密钥，从app中逆向获取，之后就可以抓包了。
