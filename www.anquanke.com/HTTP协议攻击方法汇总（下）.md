> 原文链接: https://www.anquanke.com//post/id/225955 


# HTTP协议攻击方法汇总（下）


                                阅读量   
                                **197745**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t01dcef6e71e348eda4.png)](https://p5.ssl.qhimg.com/t01dcef6e71e348eda4.png)



最近一段时间,部门的小伙伴们看了一些HTTP协议相关的攻击方法，现做一个汇总。

由于内容比较多，分上下两部分进行发布。

上半部分：[https://www.anquanke.com/post/id/224321](https://www.anquanke.com/post/id/224321)<br>
下半部分内容：<br>
《Web Cache Attack》作者：donky16<br>
《RangeAMP放大攻击》 作者: fnmsd



## Web Cache Attack

Web缓存欺骗和Web缓存投毒攻击方式<br>
作者:donky16[@360](https://github.com/360)云安全

### <a class="reference-link" name="%E5%85%B3%E4%BA%8E%E7%BC%93%E5%AD%98"></a>关于缓存

由于现在网站应用的复杂性，通常一个首页就会进行大量资源的加载，为了使用户更快的加载网页，几乎都会使用缓存，即将一些常用的静态文件，存储起来，当之后再需要这些静态资源的时候，直接就可以拿出来使用。浏览器缓存就是将缓存文件存储在本地，从而减少重复的请求，服务端缓存就是将缓存文件存储在客户端与服务端之间的CDN或者一些代理服务器中。

目前针对Web缓存的攻击方式有很多，以CDN为例，通俗来说，如果CDN会将一些攻击者构造的有害数据或者这些有害数据造成的Web应用异常的响应缓存起来，然后其他用户可以获取，那么将造成用户被攻击，即缓存投毒，如果CDN会将用户的敏感信息缓存起来，然后攻击者可以获取，那么将造成用户数据泄露，即Web缓存欺骗。

### <a class="reference-link" name="Web%E7%BC%93%E5%AD%98%E6%AC%BA%E9%AA%97"></a>Web缓存欺骗
<li>
<h5 id="h5-u73AFu5883u642Du5EFA">
<a class="reference-link" name="%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>环境搭建</h5>
以CDN为例，为了更好的搞清楚这种攻击方式的原理，简单地使用Apache2+php搭建了一个网站应用，功能十分简单，`index.php`可以输入用户名用于登录
</li>
[![](https://p5.ssl.qhimg.com/t011e525c45160c6623.png)](https://p5.ssl.qhimg.com/t011e525c45160c6623.png)

​ `info.php`可以获取用户名并展示

[![](https://p5.ssl.qhimg.com/t01e9045cc56f90f109.png)](https://p5.ssl.qhimg.com/t01e9045cc56f90f109.png)

​ 接着将网站接入了CloudFlare CDN。而最终目的就是攻击者获取正常用户的用户名，真实环境中可以获取更多敏感信息。
<li>
<h5 id="h5-u653Bu51FBu65B9u6CD5">
<a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%96%B9%E6%B3%95"></a>攻击方法</h5>
<ul>
1. 用户正常访问网站并登录获取info.php
1. 攻击者构造`http://donky.cn/test/info.php/cache-attack.css`链接并诱导用户访问
1. 用户访问`http://donky.cn/test/info.php/cache-attack.css`，请求到达CDN，CDN第一次接收到此请求，直接转发到源站
1. 源站返回带有`usernmae`的`info.php`的内容
1. CDN获取到`info.php`的内容并转发给用户，此时CDN缓存机制发现此请求路径文件拓展名为`css`，缓存此文件
1. 攻击者访问`http://donky.cn/test/info.php/cache-attack.css`，CDN发现此请求可以命中缓存，返回`info.php`内容给攻击者
1. 攻击者获取用户的`info.php`内容
</ul>
</li><li>
<h5 id="h5-u653Bu51FBu5206u6790">
<a class="reference-link" name="%E6%94%BB%E5%87%BB%E5%88%86%E6%9E%90"></a>攻击分析</h5>
上述是一个理想的攻击链，但是实际情况并不如此
当访问用户`http://donky.cn/test/info.php/cache-attack.css`
</li>
[![](https://p4.ssl.qhimg.com/t01fec5b90883d0549a.png)](https://p4.ssl.qhimg.com/t01fec5b90883d0549a.png)

由于环境是一个简单的php程序，并没有使用任何框架，没有进行相关路由配置，php忽略了url中`info.php`后面的`cache-attack.css`直接返回了`info.php`的内容，这是攻击成功的第一个条件。

接着我们用攻击者的角度去访问这个url

[![](https://p0.ssl.qhimg.com/t01cd26c36bb6763b00.png)](https://p0.ssl.qhimg.com/t01cd26c36bb6763b00.png)

发现并没有获取到用户的`username`

[![](https://p4.ssl.qhimg.com/t01b7b9bc325e902453.png)](https://p4.ssl.qhimg.com/t01b7b9bc325e902453.png)

从响应可以看到，`CF-Cache-Status: BYPASS;Cache-Control: no-store, no-cache, must-revalidate`，`CF-Cache-Status`是CloudFlare对与此请求缓存的状态记录，可以在[CloudFlare-Doc](https://support.cloudflare.com/hc/en-us/articles/200172516-Understanding-Cloudflare-s-CDN)查询

[![](https://p1.ssl.qhimg.com/t0143ccd02c96613599.png)](https://p1.ssl.qhimg.com/t0143ccd02c96613599.png)

对于源站来说，很明显`http://donky.cn/test/info.php/cache-attack.css`这个请求返回的并不是静态资源是不允许缓存的，所以在返回包内设置了`Cache-Control: no-store, no-cache, must-revalidate`，当CloudFlare获取到这种`no-store`时，自然不会进行缓存

[![](https://p4.ssl.qhimg.com/t012c5cd9073c13daf1.png)](https://p4.ssl.qhimg.com/t012c5cd9073c13daf1.png)

所以要想Web缓存欺骗攻击成功，必须保证缓存服务器会把`info.php/cache-attack.css`的内容当作`css`静态资源来进行缓存，这是攻击成功最重要的条件，想到达到这条件有两种方法，源站返回可以进行缓存的`Cache-Control`或者缓存服务器忽略源站返回的`Cache-Control`从而进行缓存。

显然第一种方式很难出现，但是对于第二种方式却在很多情况下都可以进行配置，由于网站的复杂性，很多缓存服务器可以自定义缓存策略，以测试的CloudFlare为例，可以通过Page Rule来进行配置，下图可以通过正则的方式实现在`test`目录下的所有`css`文件都可以进行缓存

[![](https://p0.ssl.qhimg.com/t013f87d2f874e4eb65.png)](https://p0.ssl.qhimg.com/t013f87d2f874e4eb65.png)

因为`http://donky.cn/test/info.php/cache-attack.css`正好匹配中`http://donky.cn/test/*.css`，所以CloudFlare会直接将`info.php`的内容缓存起来

再次测试上述攻击利用链，当用户访问`http://donky.cn/test/info.php/cache-attack.css`时，响应包中出现`Cache-Control: max-age=14400, must-revalidate; CF-Cache-Status: MISS`，此时源站返回的`Cache-Control`已经被CloudFlare忽略，并设置了缓存信息，由于第一次请求这个url，所以在缓存中是`MISS`状态，当攻击者再次访问时，会返回缓存的`info.php`内容，响应包中含有`Cache-Control: max-age=14400, must-revalidate; CF-Cache-Status: HIT; Age: 281`，命中缓存，达到攻击效果。

[![](https://p3.ssl.qhimg.com/t0166cb9ffff995c37c.png)](https://p3.ssl.qhimg.com/t0166cb9ffff995c37c.png)

### <a class="reference-link" name="Web%E7%BC%93%E5%AD%98%E6%AC%BA%E9%AA%97%E6%80%BB%E7%BB%93"></a>Web缓存欺骗总结
<li>
<h5 id="h5-u653Bu51FBu6761u4EF6">
<a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%9D%A1%E4%BB%B6"></a>攻击条件</h5>
<ul>
1. 源站应用能够忽略url中正常请求路径后面的静态文件名
1. 缓存服务器能够忽略源站返回的`Cache-Control`，并把请求获取的内容当作静态文件一样缓存
</ul>
</li>
<li>
<h5 id="h5-u5BF9u5E94u9632u5FA1u63AAu65BD">
<a class="reference-link" name="%E5%AF%B9%E5%BA%94%E9%98%B2%E5%BE%A1%E6%8E%AA%E6%96%BD"></a>对应防御措施</h5>
<ul>
1. 源站对于`http://donky.cn/test/info.php/cache-attack.css`这种请求，应该做相应的正确处理，而不是仅仅忽略后面的静态文件名
1. 缓存服务器对于源站返回的含有不能进行缓存指令的HTTP头的数据不进行缓存
</ul>
</li>
##### <a class="reference-link" name="%E5%AF%B9%E5%BA%94%E9%98%B2%E5%BE%A1%E6%8E%AA%E6%96%BD"></a>对应防御措施
- 源站对于`http://donky.cn/test/info.php/cache-attack.css`这种请求，应该做相应的正确处理，而不是仅仅忽略后面的静态文件名
- 缓存服务器对于源站返回的含有不能进行缓存指令的HTTP头的数据不进行缓存
### <a class="reference-link" name="Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>Web缓存投毒
<li>
<h5 id="h5-u7F13u5B58u952E">
<a class="reference-link" name="%E7%BC%93%E5%AD%98%E9%94%AE"></a>缓存键</h5>
由于缓存服务器会缓存一些请求返回的内容，然后当再次接收到相同的请求时，便可以直接取出缓存中的内容返回给客户端。但是如何辨别一个请求是否和缓存中的请求等效，是一件复杂的事情。http头部字段冗杂，通过设置某些字段为缓存键，当缓存键相同时，就认为可以从缓存中取文件资源。
</li>
<li>
<h5 id="h5-u653Bu51FBu573Au666F">
<a class="reference-link" name="%E6%94%BB%E5%87%BB%E5%9C%BA%E6%99%AF"></a>攻击场景</h5>
请求中一些非缓存键，会影响Web应用返回的响应内容（如把值拼接到返回内容中），并且如果这种请求获取的响应可以被缓存，那么之后的正常用户就会受到攻击。
unity3d.com就出现过这种问题
<blockquote>
<p>GET / HTTP/1.1<br>
Host: unity3d.com<br>
X-Host: portswigger-labs.net</p>
<p>HTTP/1.1 200 OK<br>
Via: 1.1 varnish-v4<br>
Age: 174<br>
Cache-Control: public, max-age=1800<br>
…</p>
\&lt;script src=”https://portswigger-labs.net/sites/files/foo.js”&gt;\&lt;/script&gt;
</blockquote>
Web应用把`X-Host`的值拼接到了返回内容的`script`标签中，这样可以直接造成XSS，`Age: 174`和`Cache-Control: public, max-age=1800`可以确认这个请求的响应是会进行缓存的，下一次更新缓存的时间可以通过`Age`和`max-age`来确定，这样就能将自己的XSS payload精准地注入到缓存中，达到攻击其他用户的效果。在很多场景下，当我们获取到非缓存键影响的响应内容时，应该搞清楚输入的非缓存键到底影响了什么内容，我们能控制哪些内容，这样才能为之后的攻击创造条件。
</li>
##### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E5%9C%BA%E6%99%AF"></a>攻击场景

#### <a class="reference-link" name="%E5%BC%95%E7%94%A8"></a>引用

[https://www.4hou.com/posts/MQkO](https://www.4hou.com/posts/MQkO)

[https://support.cloudflare.com/hc/en-us/articles/200172516-Understanding-Cloudflare-s-CDN](https://support.cloudflare.com/hc/en-us/articles/200172516-Understanding-Cloudflare-s-CDN)

[https://support.cloudflare.com/hc/zh-cn/articles/115003206852](https://support.cloudflare.com/hc/zh-cn/articles/115003206852)

[https://www.anquanke.com/post/id/156356](https://www.anquanke.com/post/id/156356)



## RangeAMP放大攻击

作者：fnmsd[@360](https://github.com/360)云安全

最近拜读了《CDN Backfired: Amplification Attacks Based on HTTP Range Requests》这篇由清华大学主导的DSN2020最佳论文，做一个简单的笔记。

**论文下载地址：**

[https://netsec.ccert.edu.cn/files/papers/cdn-backfire-dsn2020.pdf](https://netsec.ccert.edu.cn/files/papers/cdn-backfire-dsn2020.pdf)

此处先膜一下各位论文作者，tql~

### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E6%A6%82%E5%BF%B5"></a>基本概念

首先是两个概念，了解的可以直接跳过：

#### <a class="reference-link" name="CDN(%E8%BF%99%E9%87%8C%E4%B8%BB%E8%A6%81%E6%8C%87%E7%9A%84%E6%98%AFHTTP%E5%8D%8F%E8%AE%AE%E7%9A%84CDN)%EF%BC%9A"></a>CDN(这里主要指的是HTTP协议的CDN)：

> CDN的全称是Content Delivery Network，即[内容分发网络](https://baike.baidu.com/item/%E5%86%85%E5%AE%B9%E5%88%86%E5%8F%91%E7%BD%91%E7%BB%9C/4034265)。CDN是构建在现有网络基础之上的智能虚拟网络，依靠部署在各地的边缘服务器，通过中心平台的负载均衡、内容分发、调度等功能模块，使用户就近获取所需内容，降低网络拥塞，提高用户访问响应速度和命中率。CDN的关键技术主要有内容存储和分发技术。

目前主要形式还是以反向代理，产品有很多CloudFlare、AWS的CloudFront；阿里云、腾讯云的CDN产品；云WAF也基本上都带有CDN功能。

单独说一下**CDN缓存：**

> 当服务接入了 CDN 之后，浏览器本地缓存的资源过期之后，浏览器不是直接向源服务器请求资源，而是转而向 CDN 边缘节点请求资源。CDN 边缘节点中将用户的数据缓存起来，如果 CDN 中的缓存也过期了，CDN 边缘节点会向源服务器发出回源请求，从而来获取最新资源。

一些CDN的缓存可以通过加请求参数、更改请求头等等方法，令已缓存的资源资源被认为未缓存，进而令CDN回源站进行读取。

#### <a class="reference-link" name="HTTP%20Range%E8%AF%B7%E6%B1%82%EF%BC%88HTTP%E8%8C%83%E5%9B%B4%E8%AF%B7%E6%B1%82%EF%BC%89%EF%BC%9A"></a>HTTP Range请求（HTTP范围请求）：

> HTTP 协议范围请求允许服务器只发送 HTTP 消息的一部分到客户端。范围请求在传送大的媒体文件，或者与文件下载的断点续传功能搭配使用时非常有用。

所以，Range请求主要用途：大文件分块下载、断点续传、多线程下载

可以使用HEAD请求（GET也可以，只是会返回响应内容），确认所请求资源是否支持Range，如下图所示，包含Accept-Ranges为bytes为支持：

[![](https://p0.ssl.qhimg.com/t019f5b240f36f07f27.png)](https://p0.ssl.qhimg.com/t019f5b240f36f07f27.png)

不包含Accept-Ranges头，或Accept-Ranges值为none则不可用（不排除有别的值，目前看是只有bytes和none）。

使用Range请求时，需要在HTTP请求头中加入Range头，Range头的形式有两种：
<li>单一范围：
<pre><code class="lang-html hljs xml">Range: bytes=0-1023
</code></pre>
带上述请求头的请求返回0-1023个字节，服务器端会返回状态码为 [`206`](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/206) `Partial Content` 的响应，响应内容为我们所请求的1024字节的内容。
</li>
[![](https://p1.ssl.qhimg.com/t01aa9b4732ccb81ecb.png)](https://p1.ssl.qhimg.com/t01aa9b4732ccb81ecb.png)
<li>多重范围，用于请求多个数据块(范围可重叠，后面的ORB手法就是利用重叠的范围进行攻击)
<pre><code class="lang-html hljs xml">Range: bytes=0-50, 100-150
</code></pre>
带有多重范围Range请求的请求，服务器会返回 [`206`](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/206) `Partial Content`状态码，同时使用类似文件上传时的multipart多重分块作为响应（Content-Type为multipart/byteranges）,下面使用boundary进行分割多块内容。
</li>
[![](https://p2.ssl.qhimg.com/t01050c27800395e5f1.png)](https://p2.ssl.qhimg.com/t01050c27800395e5f1.png)

### <a class="reference-link" name="%E6%95%B4%E4%BD%93%E6%80%9D%E8%B7%AF"></a>整体思路

论文中整理了CDN在处理Range请求时回源策略有如下三种（详见原论文中Table I/Table II）：
<li>
**懒惰型：**不做任何改变，直接转发带Range头的请求</li>
<li>
**删除型：**直接删除Range头再转发</li>
<li>
**扩展型：**将Range头扩展到一个比较大范围</li>
其中`删除型`及`扩展型`是CDN缓存为了增加缓存命中率而做的优化，对于Range请求的资源（文件）尽量的多请求，以便客户端向CDN请求后续分块时无需再向源站请求数据。

根据CDN处理Range的方式以及CDN数量、前后顺序提出了两种攻击方式：

[![](https://p3.ssl.qhimg.com/t01a5c48adaa9b93444.png)](https://p3.ssl.qhimg.com/t01a5c48adaa9b93444.png)

### <a class="reference-link" name="Small%20Byte%20Range(SBR)Attack%EF%BC%88%E5%B0%8F%E5%AD%97%E8%8A%82%E8%8C%83%E5%9B%B4%E6%94%BB%E5%87%BB%EF%BC%89"></a>Small Byte Range(SBR)Attack（小字节范围攻击）

该方法的主旨是利用CDN进行Range放大攻击打目标源站，无需一般UDP类反射放大攻击需要源地址伪造。

[![](https://p5.ssl.qhimg.com/t01a001d8d400f7636a.png)](https://p5.ssl.qhimg.com/t01a001d8d400f7636a.png)

（论文原图，以访问test.jpg为例）

简单来说就是使用了**删除型**、**扩展型**回源策略的CDN，向源站请求尽量大的内容，且响应给客户端的内容依然为Range头预期的小内容。

放大倍数约等于**所访问的文件大小**/**Range请求+响应包大小**，论文中统计了test.jpg为1MB的情况，根据不同CDN放大倍数从724倍~1707倍不等（除了KeyCDN为724倍，其余CDN都在1000倍以上）。

(举个例子：上图1+4也就是攻击者与CDN间的交互报文大小为600字节，而请求test.jpg文件大小为1MB，那么此时2+3也就是CDN与源站交互的报文大小约等于1MB，1MB/600B,放大倍数接近1700倍)

理论上，使用**删除型**策略的CDN的放大倍数可以随着test.jpg大小**无限制增大**，论文中25MB时最大放大倍数可达4W+倍（Memcached的反射放大攻击最大在5W倍左右）。

而使用**扩展型**策略的CDN，可能会存在一个Range请求大小的上限，令放大倍数存在一定的限制，不过最次的情况下最大放大倍数也接近了万倍。

此时配合一些手法，令每次对test.jpg访问都不命中缓存并回源进行数据读取，从而造成稳定的放大攻击,持续消耗源站的带宽资源。

**论文中的攻击测试结果：**目标资源10MB，客户端消耗带宽小于500Kbps，可使目前源站1000Mbps的带宽接近占满。

**我自己的测试：**通过国外某CDN打我的阿里云ECS主机（上限带宽100Mbps），资源文件10MB(实际上用不到这么大的资源文件),20线程直接打满

[![](https://p1.ssl.qhimg.com/t018e1f035072cddc3e.png)](https://p1.ssl.qhimg.com/t018e1f035072cddc3e.png)

iftop信息，消耗了大量的流量，以及打满的带宽：

[![](https://p1.ssl.qhimg.com/t01bcb9e3e204e73e9d.png)](https://p1.ssl.qhimg.com/t01bcb9e3e204e73e9d.png)

**题外话：**这种攻击方式配合目前家用的千兆宽带，多线程多CDN节点多个代理进行Range请求，轻轻松松的放大到上T流量，理论上。。。理论上。。。

### <a class="reference-link" name="Overlapping%20Byte%20Ranges(ORB)%20Attack(%E9%87%8D%E5%8F%A0%E5%AD%97%E8%8A%82%E8%8C%83%E5%9B%B4%E6%94%BB%E5%87%BB)"></a>Overlapping Byte Ranges(ORB) Attack(重叠字节范围攻击)

该方法的主旨是利用Range放大攻击，消耗CDN内部的网络资源。

[![](https://p4.ssl.qhimg.com/t01cb625c4a132d6c6f.png)](https://p4.ssl.qhimg.com/t01cb625c4a132d6c6f.png)

（继续论文原图）

该方法使用多重范围的Range头，堆叠Range范围数量（bytes=0-,0-,…,0-）(n个0-，CDN支持的n的数量越大放大倍数越大，CDN间消耗的流量等于n倍的访问文件大小)，适用于前置CDN（FCDN）采取**懒惰型**策略，并且后置CDN（BCDN）不检查Range范围是否重叠，就返回分块的Range响应；的CDN组合情况。

同时在客户端处，设置较小的**TCP接收窗口**，并及时断开连接，使得接收的数据尽量小。

该方法可获得源站文件大小50-6500的流量放大，大量消耗FCDN、BCDN的网络资源。

论文中给了6个CDN结合，一共11种组合的可利用情况，相对SRB来说利用难度较大，一般很少有使用多层CDN的情况。

该方法无法直接威胁到源站。



## 解决方案

论文中最后给出了针对不同角色的解决方案：

**服务器侧：**1. 增强本地DDOS防御能力 2.如果接入了CDN，判断是否存在上述问题。

**CDN侧：**修改Range请求的回源策略，从删除型的扩展型，并且扩展较小的范围（比如在原范围基础上扩展8KB，这样不会浪费太多资源）。

**协议侧：**修改相关RFC标准，将RangeAMP纳入到考虑范围中。

我们还发现:在静态资源后面加参数，使CDN的缓存MISS是一种常见的Cache MISS手法。（在这种情况下，访问`/test.jpg`和访问`/test.jpg?xx`,会被当做访问了不同的静态资源文件）

所以，如果确认不需要参数，可直接在CDN上开启忽略参数进行缓存，避免静态资源重复回源，造成RangeAMP放大攻击。

[![](https://p5.ssl.qhimg.com/t01bfc6a37c08c4534d.png)](https://p5.ssl.qhimg.com/t01bfc6a37c08c4534d.png)



## 总结

SRB、ORB攻击方法利用了CDN的缓存策略、Range请求进行了放大攻击。

利用本应该用于抗D的CDN来对源站进行流量攻击，以及无意义的消耗CDN网络内部的资源，保护者变成了破坏者。



## 引用内容
1. [https://netsec.ccert.edu.cn/files/papers/cdn-backfire-dsn2020.pdf](https://netsec.ccert.edu.cn/files/papers/cdn-backfire-dsn2020.pdf)
1. [https://baike.baidu.com/item/CDN/420951](https://baike.baidu.com/item/CDN/420951)
1. [https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Range_requests](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Range_requests)
1. [https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Accept-Ranges](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Accept-Ranges)
1. [https://www.jianshu.com/p/baf12d367fe7](https://www.jianshu.com/p/baf12d367fe7)