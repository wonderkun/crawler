> 原文链接: https://www.anquanke.com//post/id/245539 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 - 服务端请求伪造(SSRF)专题


                                阅读量   
                                **48830**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01e13074572d213276.png)](https://p3.ssl.qhimg.com/t01e13074572d213276.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 服务器端漏洞篇介绍

> burp官方说他们建议初学者先看服务器漏洞篇，因为初学者只需要了解服务器端发生了什么就可以了



## 服务器端漏洞篇 – 服务端请求伪造(SSRF)专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFSSRF%EF%BC%9F"></a>什么是SSRF？

SSRF全称是Server-Side Request Forgery，它就是攻击者诱使服务器向攻击者指定的域发送HTTP请求，可以用来建立恶意的连接

### <a class="reference-link" name="%E5%B8%B8%E8%A7%84SSRF%E6%94%BB%E5%87%BB"></a>常规SSRF攻击

SSRF攻击主要是基于服务器对输入的绝对信任，因为绝对信任所以服务器无条件地执行输入中的指令，导致即使其中包含恶意命令也会执行

### <a class="reference-link" name="%E9%92%88%E5%AF%B9%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%9C%AC%E8%BA%AB%E7%9A%84SSRF%E6%94%BB%E5%87%BB"></a>针对服务器本身的SSRF攻击

这种攻击方式就是攻击者诱使服务器向本地地址(127.0.0.1或localhost)的某些服务发送HTTP请求。<br>
例如考虑这样一个应用程序，通过在HTTP请求中指定API的URL查询库存，例如这样的HTTP请求

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://stock.weliketoshop.net:8080/product/stock/check%3FproductId%3D6%26storeId%3D1

```

然后我们可以将stockApi修改为本地地址的管理界面

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://localhost/admin

```

由于服务器会无条件信任stockApi指定的URL并跳转到该URL，所以此时可以触发垂直越权进入管理界面。危害还是很大的。<br>
为什么服务器会默认信任来自本地地址的请求呢，大概有如下原因
- 访问控制策略可能编写于前端，我们修改请求包的时候是已经通过了前端的，所以很容易就被绕过了
- 有的应用程序为了方便灾难恢复将服务器设置为任意用户都可访问，这就导致也会默认信任本地地址
### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%92%88%E5%AF%B9%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%9C%AC%E8%BA%AB%E7%9A%84%E5%9F%BA%E7%A1%80SSRF%E6%94%BB%E5%87%BB"></a>配套靶场：针对服务器本身的基础SSRF攻击

刚讲过的知识点，我们随便将一个查询库存的请求发到repeater中，发现同样有stockApi参数

[![](https://p0.ssl.qhimg.com/t0189a95425b2d97e8f.png)](https://p0.ssl.qhimg.com/t0189a95425b2d97e8f.png)

图中我们看到可以直接通过修改该参数访问管理页面，于是我们就可以利用这个漏洞删除指定用户了

[![](https://p3.ssl.qhimg.com/t012a4ea13d94eef4c4.png)](https://p3.ssl.qhimg.com/t012a4ea13d94eef4c4.png)

我们成功解决这道题

### <a class="reference-link" name="%E9%92%88%E5%AF%B9%E5%85%B6%E4%BB%96%E5%90%8E%E7%AB%AF%E7%B3%BB%E7%BB%9F%E7%9A%84SSRF%E6%94%BB%E5%87%BB"></a>针对其他后端系统的SSRF攻击

有的后端系统用户是无法直接访问的，但是服务器可以成功向其发送请求，所以如果利用ssrf同样可以向这些本不对用户开放的后端系统发出恶意请求。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%92%88%E5%AF%B9%E5%85%B6%E4%BB%96%E5%90%8E%E7%AB%AF%E7%B3%BB%E7%BB%9F%E7%9A%84%E5%9F%BA%E7%A1%80SSRF%E6%94%BB%E5%87%BB"></a>配套靶场：针对其他后端系统的基础SSRF攻击

热乎的知识点，因为不知道具体是哪个IP，所以我们放到Intruder跑一下

[![](https://p1.ssl.qhimg.com/t01f36cb6136dadadfb.png)](https://p1.ssl.qhimg.com/t01f36cb6136dadadfb.png)

[![](https://p5.ssl.qhimg.com/t01b16e967f15360d8b.png)](https://p5.ssl.qhimg.com/t01b16e967f15360d8b.png)

[![](https://p1.ssl.qhimg.com/t0177b4c122fc5cb48f.png)](https://p1.ssl.qhimg.com/t0177b4c122fc5cb48f.png)

从爆破结果得知目标后端系统了，然后将响应发到浏览器就可以进入管理面板删除指定用户了

### <a class="reference-link" name="%E7%BB%95%E8%BF%87%E5%B8%B8%E8%A7%84SSRF%E9%98%B2%E6%8A%A4%E7%9A%84%E6%89%8B%E6%AE%B5"></a>绕过常规SSRF防护的手段

为了缓解SSRF攻击，有的应用程序会采取一些防护手段，但是针对常规的防护手段还是可以通过一些绕过方法绕过的

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E9%BB%91%E5%90%8D%E5%8D%95%E7%9A%84%E8%BE%93%E5%85%A5%E8%BF%87%E6%BB%A4%E7%9A%84SSRF"></a>基于黑名单的输入过滤的SSRF

有的应用程序会在后端系统设置黑名单限制向本地地址发出的请求，但是我们可以通过其他形式的本地地址进行绕过，因为并不是所有形式的写法都在黑名单中，例如2130706433，017700000001和127.1，还有dns解析记录为本地地址的域名，如burp内置的域名spoofed.burpcollaborator.net，或者利用URL编码、大小写混用之类的混淆方法进行绕过

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%9F%BA%E4%BA%8E%E9%BB%91%E5%90%8D%E5%8D%95%E7%9A%84%E8%BE%93%E5%85%A5%E8%BF%87%E6%BB%A4%E7%9A%84SSRF"></a>配套靶场：基于黑名单的输入过滤的SSRF

根据知识点我们对地址进行混淆

[![](https://p0.ssl.qhimg.com/t01d62af18a90ce3665.png)](https://p0.ssl.qhimg.com/t01d62af18a90ce3665.png)

混淆以后就可以绕过防护机制进入管理面板删除指定用户了

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E7%99%BD%E5%90%8D%E5%8D%95%E7%9A%84%E8%BE%93%E5%85%A5%E8%BF%87%E6%BB%A4%E7%9A%84SSRF"></a>基于白名单的输入过滤的SSRF

区别于黑名单，白名单就是只允许名单上的地址连接，但是有的应用程序的过滤机制匹配方法导致可以通过在不同位置夹带恶意目标地址进行绕过，例如

```
https://expected-host@evil-host
https://evil-host#expected-host
https://expected-host.evil-host
```

还可以利用与应用程序URL解码规则有差异的URL编码进行绕过，比如双重URL编码之类的

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%9F%BA%E4%BA%8E%E7%99%BD%E5%90%8D%E5%8D%95%E7%9A%84%E8%BE%93%E5%85%A5%E8%BF%87%E6%BB%A4%E7%9A%84SSRF"></a>配套靶场：基于白名单的输入过滤的SSRF

因为不知道应用程序会对哪些连接符拦截，所以我们做一下fuzz测试

[![](https://p4.ssl.qhimg.com/t01dcf781b0a0f4af91.png)](https://p4.ssl.qhimg.com/t01dcf781b0a0f4af91.png)

[![](https://p3.ssl.qhimg.com/t016fa1363a78df54d9.png)](https://p3.ssl.qhimg.com/t016fa1363a78df54d9.png)

[![](https://p3.ssl.qhimg.com/t0104bfe9ab1c1d8b79.png)](https://p3.ssl.qhimg.com/t0104bfe9ab1c1d8b79.png)

我们现在得知@是可用的连接符，因为这仅仅突破了第一道防线，下面我们要突破第二道防线即对本地地址的过滤

[![](https://p3.ssl.qhimg.com/t011643a0c52997c1e0.png)](https://p3.ssl.qhimg.com/t011643a0c52997c1e0.png)

[![](https://p2.ssl.qhimg.com/t0136e72ed766c27df0.png)](https://p2.ssl.qhimg.com/t0136e72ed766c27df0.png)

发现%2523，是对#的双重URL编码处理的，我们就可以成功删除指定用户了

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E5%BC%80%E6%94%BE%E9%87%8D%E5%AE%9A%E5%90%91%E7%BB%95%E8%BF%87SSRF%E8%BF%87%E6%BB%A4"></a>通过开放重定向绕过SSRF过滤

有的应用程序请求的API支持添加一个可以指定重定向URL的参数，这就给了攻击者可乘之机，如果API URL的过滤机制比较脆弱就会导致开放重定向漏洞进入本不允许访问的URL，比如攻击者可以构造这样的请求包

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://weliketoshop.net/product/nextProduct?currentProductId=6&amp;path=http://192.168.0.68/admin

```

因为API URL为应用程序允许请求的域名，并且支持设置重定向地址，所以我们可以利用这个漏洞向目标地址请求

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87%E5%BC%80%E6%94%BE%E9%87%8D%E5%AE%9A%E5%90%91%E6%BC%8F%E6%B4%9E%E7%BB%95%E8%BF%87%E6%9C%89%E8%BF%87%E6%BB%A4%E7%9A%84SSRF"></a>配套靶场：通过开放重定向漏洞绕过有过滤的SSRF

我们先试一下常规的SSRF攻击手段能不能成功

[![](https://p5.ssl.qhimg.com/t010f56bf22a1c3ea40.png)](https://p5.ssl.qhimg.com/t010f56bf22a1c3ea40.png)

发现并不能通过过滤器，但是我们发现有一个展示下一个产品的功能点，会触发重定向

[![](https://p4.ssl.qhimg.com/t010a7e19aa6fcbfd43.png)](https://p4.ssl.qhimg.com/t010a7e19aa6fcbfd43.png)

所以我们可以将目标地址附在重定向参数中

[![](https://p1.ssl.qhimg.com/t01fcff3b35766bfcd0.png)](https://p1.ssl.qhimg.com/t01fcff3b35766bfcd0.png)

然后会跳转到管理面板

[![](https://p0.ssl.qhimg.com/t015023fb9c65cda9f8.png)](https://p0.ssl.qhimg.com/t015023fb9c65cda9f8.png)

我们成功删除指定用户了

### <a class="reference-link" name="SSRF%E7%9B%B2%E6%89%93"></a>SSRF盲打

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFSSRF%E7%9B%B2%E6%89%93%EF%BC%9F"></a>什么是SSRF盲打？

和sql盲注一样，就是不会在响应中得到SSRF攻击的反馈

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%AF%BB%E6%89%BE%E5%92%8C%E5%88%A9%E7%94%A8SSRF%E7%9B%B2%E6%89%93%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>如何寻找和利用SSRF盲打漏洞？

与sql盲注相同，ssrf盲打最佳利用方式就是通过带外技术接收响应结果。也是同样使用burp自带的简易带外平台collaborator。即使有一些HTTP流量会被拦截，也会因为不怎么拦截DNS流量而获取我们想要的结果。<br>
有的情况还可以利用SSRF盲打对目标后端系统进行探测，比如探测目标网络中开放的主机及端口之类的，这些同样也可以通过带外通道接收到。<br>
还有一种情况就是所谓的反弹shell了，burp在这里没有进行过多的讲解，有兴趣的小伙伴可以自行了解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%B8%A6%E6%9C%89%E5%B8%A6%E5%A4%96%E6%A3%80%E6%B5%8B%E7%9A%84SSRF%E7%9B%B2%E6%89%93"></a>配套靶场1：带有带外检测的SSRF盲打

题目中直接告诉我们Referer头存在SSRF盲打漏洞，于是我们把临时collaborator地址贴上去

[![](https://p5.ssl.qhimg.com/t01f67f7616c7762f66.png)](https://p5.ssl.qhimg.com/t01f67f7616c7762f66.png)

然后我们在客户端接收到了发过来的DNS请求

[![](https://p0.ssl.qhimg.com/t012c5a7df2dcd3e9e6.png)](https://p0.ssl.qhimg.com/t012c5a7df2dcd3e9e6.png)

我们看到只收到了DNS请求，说明是前面介绍的那种情况，仅会拦截HTTP流量

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%B8%A6%E6%9C%89shellshock%E5%88%A9%E7%94%A8%E7%9A%84SSRF%E7%9B%B2%E6%89%93"></a>配套靶场2：带有shellshock利用的SSRF盲打

首先我们到burp插件市场装一个这个插件

[![](https://p3.ssl.qhimg.com/t012db3117f2b034773.png)](https://p3.ssl.qhimg.com/t012db3117f2b034773.png)

从名字就能看出来这个插件可以对每一个点都进行collaborator测试以发现可以使用带外技术发送请求的点，为了方便插件进行测试，我们将靶场地址添加到scope中

[![](https://p4.ssl.qhimg.com/t01f990460a00eaa400.png)](https://p4.ssl.qhimg.com/t01f990460a00eaa400.png)

然后在浏览器中随意访问靶场里的一些页面，插件就会自动开始探测了

[![](https://p1.ssl.qhimg.com/t01ae8b1125f885760b.png)](https://p1.ssl.qhimg.com/t01ae8b1125f885760b.png)

从结果得知Referer和User-Agent两个位置可以使用带外技术发送请求，于是我们构造这样的payload

[![](https://p3.ssl.qhimg.com/t0121f7a8bf49da5645.png)](https://p3.ssl.qhimg.com/t0121f7a8bf49da5645.png)

这样我们就能在客户端接收到结果了

[![](https://p0.ssl.qhimg.com/t0144e88ffbdaeee295.png)](https://p0.ssl.qhimg.com/t0144e88ffbdaeee295.png)

我们知道了当前用户名是peter了，说明whoami不仅执行成功了，还把执行结果附加在URL中向指定的collaborator客户端发送请求了

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%AF%BB%E6%89%BESSRF%E9%9A%90%E8%97%8F%E7%9A%84%E6%94%BB%E5%87%BB%E9%9D%A2%EF%BC%9F"></a>如何寻找SSRF隐藏的攻击面？

burp总结了一些不太常发现SSRF的攻击面

### <a class="reference-link" name="%E8%AF%B7%E6%B1%82%E4%B8%AD%E7%9A%84%E9%83%A8%E5%88%86URL"></a>请求中的部分URL

有的应用程序仅在请求中获取部分URL，然后在后端系统中再将其与剩余部分拼接成完整的URL，这就导致我们无法控制整个URL而很难利用SSRF攻击成功

### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F%E5%86%85%E7%9A%84URL"></a>数据格式内的URL

有的应用程序允许在某种数据格式中插入URL，这就涉及到我们下一个要讲的专题了，就是xxe注入漏洞专题，通过xxe注入可以发动ssrf攻击，我们会在下一专题中进行讲解

### <a class="reference-link" name="%E9%80%9A%E8%BF%87Referer%E5%A4%B4%E7%9A%84SSRF"></a>通过Referer头的SSRF

有的应用程序为了跟踪分析用户的浏览记录会总是访问Referer指定的URL中的内容，此时是最容易引发SSRF攻击的



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 – 服务端请 求伪造(SSRF)专题的全部内容啦，本专题主要讲了如何寻找和利用SSRF漏洞，发现这类漏洞往往危害很大，可以利用服务器的信任关系执行高危的命令，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
