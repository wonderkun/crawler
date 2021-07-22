> 原文链接: https://www.anquanke.com//post/id/190080 


# 记一次APP双向认证抓包


                                阅读量   
                                **1132086**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t015f307557d0f8ce5d.png)](https://p5.ssl.qhimg.com/t015f307557d0f8ce5d.png)



## 前言

随着移动应用的发展和推广，APP应用安全越来越受到重视。APP中各类防抓包的机制的出现，让测试无法正常进行分析。

这篇文章算是总结一下我最近遇到的一款抓不到包的APP，给大家提供一个双向证书认证应该如何解决的思路。



## 判断证书双向认证

刚拿到此app时候常规方法一把梭，发现只要一开启手机代理，却提示网络异常，通过观察burpsuite的记录发现，只有请求包而没有响应包。

直觉告诉我应该是使用SSL Pinning防止中间人拦截攻击，然后我开启了ssl-kill-switch2后发现该APP所有的响应包返回 400 No required SSL certificate was sent的报错信息。

[![](https://p1.ssl.qhimg.com/t01e190fc713c587333.png)](https://p1.ssl.qhimg.com/t01e190fc713c587333.png)

根据报错提示，搜了一下发现该错误是指服务器端启用了证书双向认证。

> 当服务器启用了证书双向认证之后，除了客户端去验证服务器端的证书外，服务器也同时需要验证客户端的证书，也就是会要求客户端提供自己的证书，如果没有通过验证，则会拒绝连接，如果通过验证，服务器获得用户的公钥。

该app直接封装了客户端的证书，相比于单项认证，无非就是多了一个服务器端验证客户端证书的过程，而在以往的用代理工具如burp这类工具，抓取https的包时，除了浏览器获取的是代理工具的证书外，默认是不发送证书给服务器端的。burp在抓取https报文的过程中也提供了双向认证的证书发送，但是是使用了burp提供的证书文件，也就是CA证书。app的服务端不认证这个burp提供的CA证书，那么我们就需要拿到匹配的证书，以其对服务端进行匹配。



## 突破思路

确定该APP是证书双向认证，那么APP客户端一定会存一个证书文件。通过对该APP解压并进入payload目录，发现只有一个.p12结尾的证书文件。

[![](https://p5.ssl.qhimg.com/t01e184b2d0e098c9fa.png)](https://p5.ssl.qhimg.com/t01e184b2d0e098c9fa.png)

尝试点开发现需要安装密码。

[![](https://p4.ssl.qhimg.com/t017df067cd594280e8.png)](https://p4.ssl.qhimg.com/t017df067cd594280e8.png)



## app解密的代码逻辑

客户端发送数据包以后，需要去从app中读取这个证书文件，密码是以硬编码形式放在了代码中，利用这个代码中的密码字段去解密证书文件，从中读取以后，再进行解密并回传给服务器端进行确认。由此推断，寻找证书名称应该就可以拿到安装密码。



## 获取安装证书密码

首先对其APP进行砸壳，完成后我们解压缩然后使用IDA加载二进制文件。

然后在String窗口搜索证书的名称client，搜索后进入对应的类。

[![](https://p2.ssl.qhimg.com/t019b3e65634bb4f7e5.png)](https://p2.ssl.qhimg.com/t019b3e65634bb4f7e5.png)

通过跟踪发现了该证书密钥，如下：

[![](https://p5.ssl.qhimg.com/t017ee445c0a78031be.png)](https://p5.ssl.qhimg.com/t017ee445c0a78031be.png)

测试使用该密钥发现可以成功安装该证书：

[![](https://p1.ssl.qhimg.com/t018c37399c1ab48e41.png)](https://p1.ssl.qhimg.com/t018c37399c1ab48e41.png)



## burp添加客户端证书

host填写app服务端的主域名。

[![](https://p0.ssl.qhimg.com/t01c5f028114fe6d828.png)](https://p0.ssl.qhimg.com/t01c5f028114fe6d828.png)

随后选择app客户端内的client.p12证书文件，并输入安装密码。

[![](https://p5.ssl.qhimg.com/t01624f4a24cdcc7687.png)](https://p5.ssl.qhimg.com/t01624f4a24cdcc7687.png)

证书成功导入，勾选即可使用。

[![](https://p1.ssl.qhimg.com/t0188024ced1f73d0f4.png)](https://p1.ssl.qhimg.com/t0188024ced1f73d0f4.png)

ok~发现可以正常抓包，如下。

[![](https://p3.ssl.qhimg.com/t01098caa6c3f6623fc.png)](https://p3.ssl.qhimg.com/t01098caa6c3f6623fc.png)

参考文章,感谢各位大佬的倾情奉献

> [https://se8s0n.github.io/2018/09/11/HTTP系列(五)/](https://se8s0n.github.io/2018/09/11/HTTP%E7%B3%BB%E5%88%97(%E4%BA%94)/)<br>[https://xz.aliyun.com/t/6551#toc-14](https://xz.aliyun.com/t/6551#toc-14)<br>[https://juejin.im/post/5c9cbf1df265da60f6731f0a](https://juejin.im/post/5c9cbf1df265da60f6731f0a)<br>[https://www.secpulse.com/archives/54027.html](https://www.secpulse.com/archives/54027.html)



## 关注我们

Tide安全团队正式成立于2019年1月，是新潮信息旗下以互联网攻防技术研究为目标的安全团队，目前聚集了十多位专业的安全攻防技术研究人员，专注于网络攻防、Web安全、移动终端、安全开发、IoT/物联网/工控安全等方向。

想了解更多Tide安全团队，请关注团队官网: [http://www.TideSec.net](http://www.tidesec.net/) 或长按二维码关注公众号：

[![](https://image.3001.net/images/20191031/1572510422_5dba9ad6ba332.png!small)](https://image.3001.net/images/20191031/1572510422_5dba9ad6ba332.png!small)
