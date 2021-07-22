> 原文链接: https://www.anquanke.com//post/id/86527 


# 【Blackhat】SSRF的新纪元：在编程语言中利用URL解析器


                                阅读量   
                                **183220**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blackhat.com
                                <br>原文地址：[https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01bc60335eb6586877.png)](https://p3.ssl.qhimg.com/t01bc60335eb6586877.png)



作者：[Orange Tsai ](http://blog.orange.tw/)  译者：[**math1as**](http://bobao.360.cn/member/contribute?uid=1336370560)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

并非完全翻译,掺杂了一点自己的私货和见解。



**<br>**

**什么是SSRF**

****

[1] 服务器端请求伪造

[2] 穿透防火墙,直达内网

[3] 让如下的内网服务陷入危险当中

Structs2

Redis

Elastic



**<br>**

**SSRF中的协议'走私'**

[1] 让SSRF的利用更加有效

本质上说,是利用原本的协议夹带信息,攻击到目标的应用

[2] 用来'走私'的协议必须是适合的,比如

基于HTTP的各类协议=&gt;Elastic,CouchDB,Mongodb,Docker

基于Text的各类协议=&gt;FTP,SMTP,Redis,Memcached



**<br>**

**一个有趣的例子**

****

像这样的一个协议

[![](https://p2.ssl.qhimg.com/t012da6fc6483859e74.png)](https://p2.ssl.qhimg.com/t012da6fc6483859e74.png)

我们来分析一下,各个不同的python库,分别请求到的是哪个域名呢？

[![](https://p2.ssl.qhimg.com/t0140b50133fc83aae3.png)](https://p2.ssl.qhimg.com/t0140b50133fc83aae3.png)

可以看到,Python真是个矛盾的语言呢。

<br>

**另一个有趣的例子**

[1] HTTP协议中的CRLF(换行符)注入

[2] 使用HTTP协议'走私'信息来攻击SMTP协议

我们尝试构造CRLF注入,来进行如下的攻击

[![](https://p1.ssl.qhimg.com/t01de444a27af7e3c55.png)](https://p1.ssl.qhimg.com/t01de444a27af7e3c55.png)

STMP '讨厌' HTTP协议

这似乎是不可利用的,可是,真的如此么?

我们在传统的SSRF利用中都使用gopher协议来进行相关攻击

可是事实上,如果真实的利用场景中不支持gopher协议呢?



**利用HTTPS协议:SSL握手中,什么信息不会被加密?**

[1] HTTPS协议中的CRLF(换行符)注入

[2] 化腐朽为神奇 – 利用TLS SNI(Server Name Indication),它是用来改善SSL和TLS的一项特性

允许客户端在服务器端向其发送证书之前请求服务器的域名。

https://tools.ietf.org/html/rfc4366RFC文档 

简单的说,原本的访问,是将域名解析后,向目标ip直接发送client hello,不包含域名

而现在包含了域名,给我们的CRLF攻击提供了利用空间

我们尝试构造CRLF注入,来进行如下的攻击

[![](https://p3.ssl.qhimg.com/t01e40451cbff15cd28.png)](https://p3.ssl.qhimg.com/t01e40451cbff15cd28.png)

监听25端口

[![](https://p2.ssl.qhimg.com/t01433aa98521613722.png)](https://p2.ssl.qhimg.com/t01433aa98521613722.png)

分析发现,127.0.0.1被作为域名信息附加在了client hello之后

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c56cd7acfa314de8.png)

由此我们成功的向STMP'走私'了信息,实施了一次攻击



**URL解析中的问题**

[1] 所有的问题,几乎都是由URL解析器和请求函数的不一致造成的。

[2] 为什么验证一个URL的合法性是很困难的?

1.在 RFC2396/RFC3986 中进行了说明,但是也只是停留在说明书的层面。

2.WHATWG(网页超文本应用技术工作小组)定义了一个基于RFC的具体实现

但是不同的编程语言仍然使用他们自己的实现



**RFC 3986中定义的URL组成部分**

大致用这张图片来说明

[![](https://p4.ssl.qhimg.com/t019f5f6a6200b14ceb.png)](https://p4.ssl.qhimg.com/t019f5f6a6200b14ceb.png)

其中的协议部分,在真实场景中一般都为http或https

而查询字符串和fragment,也就是#号后的部分,我们实际上是不关心的,因为这和我们的利用无关

所以,我们着重看的也就是authority和path部分

那么,在这几个部分中,能不能进行CRLF注入?

各个语言以及他们对应的库的情况如下图所示

[![](https://p2.ssl.qhimg.com/t012b9bca3ec00d5ba2.png)](https://p2.ssl.qhimg.com/t012b9bca3ec00d5ba2.png)

可以看到支持CRLF注入的部分还是很多的,但是除了在实际的请求中能利用CRLF注入外

还要能通过URL解析器的检查,而这个图也列出来了对应的情况。



**关于URL解析器**

[1] 让我们思考如下的php代码

[![](https://p3.ssl.qhimg.com/t0132d296b8025ae9a8.png)](https://p3.ssl.qhimg.com/t0132d296b8025ae9a8.png)

在这段代码中,我们最后使用readfile函数来实施我们的SSRF攻击

但是,我们构造出的URL需要经过parse_url的相应检查



**误用URL解析器的后果**

当我们对上述的php脚本传入这样的一个URL

[![](https://p1.ssl.qhimg.com/t01b6b99253d3671734.png)](https://p1.ssl.qhimg.com/t01b6b99253d3671734.png)

对于我们的请求函数readfile来说,它所请求的端口是11211

而相反的,对于parse_url来说,它则认为这个url的端口号是80,符合规定

[![](https://p0.ssl.qhimg.com/t01af94d76d66fe999d.png)](https://p0.ssl.qhimg.com/t01af94d76d66fe999d.png)

这就产生了一个差异化的问题,从而造成了SSRF的成功利用

让我们来看看,在RFC3986中,相关的定义

[![](https://p1.ssl.qhimg.com/t012c9b49c995f4f0dd.png)](https://p1.ssl.qhimg.com/t012c9b49c995f4f0dd.png)

那么,按照这个标准,当我们传入如下URL的时候,会发生什么呢

[![](https://p0.ssl.qhimg.com/t0198914d4cb8173803.png)](https://p0.ssl.qhimg.com/t0198914d4cb8173803.png)

对比我们的两个函数

[![](https://p1.ssl.qhimg.com/t01d2ab51ab659277ca.png)](https://p1.ssl.qhimg.com/t01d2ab51ab659277ca.png)

可以看到,parse_url最终得到的部分实际上是google.com

而readfile则忠实的执行了RFC的定义,将链接指向了evil.com

进行一下简单的分析

[1] 这样的问题同样影响了如下的编程语言

cURL,Python

[2] RFC3962的进一步分析

在3.2小节中有如下的定义:authority(基础认证)部分应该由//作为开始而由接下来的一个/号,或者问号

以及 #号作为一个结束,当然,如果都没有,这个部分将延续到URL的结尾。



**cURL的利用**

参照我们刚才所得到的结论

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01630d234ddc142e7b.png)

对这样的一个URL进行分析和测试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011618cb3b93c2e05b.png)

可以发现,在cURL作为请求的实施者时,它最终将evil.com:80作为了目标

而其他的几种URL解析器则得到了不一样的结果,产生了不一致。

当他们被一起使用时,可以被利用的有如下的几种组合

[![](https://p0.ssl.qhimg.com/t0159bce0a767db25eb.png)](https://p0.ssl.qhimg.com/t0159bce0a767db25eb.png)

于是我向cURL团队报告了这个问题,很快的我得到了一个补丁

但是这个补丁又可以被添加一个空格的方式绕过

[![](https://p5.ssl.qhimg.com/t013ed5337e5043980d.png)](https://p5.ssl.qhimg.com/t013ed5337e5043980d.png)

但是,当我再次向cURL报告这个情况的时候,他们认为,cURL并不能100%的验证URL的合法性

它本来就是要让你来传给他正确的URL参数的

并且他们表示,这个漏洞不会修复,但是上一个补丁仍然在7.54.0版本中被使用了



**NodeJS的Unicode解析问题**

让我们来看如下的一段nodeJS代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011b45e2c8a03d1d05.png)

可以看到,阻止了我们使用..来读取上层目录的内容

当对其传入如下的URL时,会发生什么呢

[![](https://p4.ssl.qhimg.com/t01f7ec5e8d1bfa9d89.png)](https://p4.ssl.qhimg.com/t01f7ec5e8d1bfa9d89.png)

注意,这里的N是 U+FF2E,也就是拉丁文中的N,其unicode编码为 /xFF/x2E

[![](https://p5.ssl.qhimg.com/t016fe07fd8c14673e4.png)](https://p5.ssl.qhimg.com/t016fe07fd8c14673e4.png)

最终,由于nodeJS的处理问题 xFF 被丢弃了,剩下的x2E被解析为.

于是我们得到了如下的结论

[![](https://p5.ssl.qhimg.com/t010ae2e6e8e48f7110.png)](https://p5.ssl.qhimg.com/t010ae2e6e8e48f7110.png)

在NodeJS的http模块中, NN/ 可以起到../ 的作用,绕过特定的过滤

那么,nodeJS对于之前我们所研究的CRLF注入,又能不能够加以防御呢?

[1] HTTP模块可以避免直接的CRLF注入

[2] 那么,当我们将换行符编码时,会如何呢?

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01615a34a714bf5b77.png)

很明显,这时候它并不会进行自动的解码操作

如何打破这个僵局呢? 使用U+FF0D和U+FF0A

[![](https://p3.ssl.qhimg.com/t0120385d1cb5273f57.png)](https://p3.ssl.qhimg.com/t0120385d1cb5273f57.png)

我们成功的往请求中注入了新的一行



**Glibc中的NSS特性**

在Glibc的源代码文件 resolv/ns_name.c中,有一个叫ns_name_pton的函数

[![](https://p2.ssl.qhimg.com/t015b1007e578c309c1.png)](https://p2.ssl.qhimg.com/t015b1007e578c309c1.png)

它遵循RFC1035标准,把一个ascii字符串转化成一个编码后的域名

这有什么可利用的呢?

让我们来看下面的代码

[![](https://p1.ssl.qhimg.com/t01ee33633d258f8351.png)](https://p1.ssl.qhimg.com/t01ee33633d258f8351.png)

通过gethostbyname函数来解析一个域名

在字符串中,代表转义符号,因此用\097来代表ascii码为97,也就是字母a

成功的解析到了orange.tw的ip地址

那么我们看看python的gethostbyname

[![](https://p5.ssl.qhimg.com/t01924acb116679b307.png)](https://p5.ssl.qhimg.com/t01924acb116679b307.png)

更让我们惊奇的是,它忽略了这些号 而解析到了orange.tw

同样的,一些类似的特性存在于linux的getaddrinfo()函数中,它会自动过滤掉空格后的垃圾信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eab354b18dba2c01.png)

python socket中的gethostbyname是依赖于getaddrinfo()函数的

因此出现了类似的问题,当传入CRLF时,后面的部分被丢弃了

[![](https://p3.ssl.qhimg.com/t0187842c9e2b3d72e0.png)](https://p3.ssl.qhimg.com/t0187842c9e2b3d72e0.png)

说了这么多,这些特性有什么可以利用的地方呢?

让我们来看如下的几种payload

[![](https://p2.ssl.qhimg.com/t016e2af036380b7c89.png)](https://p2.ssl.qhimg.com/t016e2af036380b7c89.png)

可以想到的是,如果利用Glibc的NSS特性,当检查URL时,gethostbyname将其识别为127.0.0.1

为什么%2509能够生效呢?部分的函数实现可能会解码两次,甚至循环解码到不含URL编码

那么接下来,实际发起访问时,我们就可以使用CRLF注入了

[![](https://p0.ssl.qhimg.com/t01063d523ba0e82a9d.png)](https://p0.ssl.qhimg.com/t01063d523ba0e82a9d.png)

由此注入了一条redis语句

同样的,当HTTPS开启了之前我们提到的TLS SNI(Server Name Indication)时

它会把我们传入的域名放到握手包的client hello后面

[![](https://p5.ssl.qhimg.com/t0171a14bab8bfb92a1.png)](https://p5.ssl.qhimg.com/t0171a14bab8bfb92a1.png)

这样我们就成功的注入了一条语句

[![](https://p5.ssl.qhimg.com/t015198d1feec8b3e4e.png)](https://p5.ssl.qhimg.com/t015198d1feec8b3e4e.png)

而我们还可以进一步延伸,比如曾经的python CRLF注入漏洞,CVE-2016-5699

可以看到,这里其实允许CRLF后紧跟一个空格

[![](https://p1.ssl.qhimg.com/t013e276f81b3d50450.png)](https://p1.ssl.qhimg.com/t013e276f81b3d50450.png)

由此绕过了_is_illegal_header_value()函数的正则表达式

但是,相应的应用会接受在行开头的空格么?

[![](https://p2.ssl.qhimg.com/t0132c7e8fd1a608637.png)](https://p2.ssl.qhimg.com/t0132c7e8fd1a608637.png)

可以看到,redis和memcached都是允许的,也就产生了利用。



**利用IDNA标准**

IDNA是,Internationalizing Domain Names in Applications的缩写,也就是'让域名变得国际化'

[![](https://p2.ssl.qhimg.com/t01e03097ff9fb55427.png)](https://p2.ssl.qhimg.com/t01e03097ff9fb55427.png)

上图是IDNA各个版本的标准,这个问题依赖于URL解析器和实际的请求器之间所用的IDNA标准不同

可以说,仍然是差异性的攻击。

[![](https://p1.ssl.qhimg.com/t017c98254a6dfc170d.png)](https://p1.ssl.qhimg.com/t017c98254a6dfc170d.png)

比如,我们来看这个例子,将这个希腊字母转化为大写时,得到了SS

其实,这个技巧在之前的xss挑战赛 prompt 1 to win当中也有用到

这里我们面对的的是Wordpress

1.它其实很注重保护自己不被SSRF攻击

2.但是仍然被我们发现了3种不同的方法来绕过它的SSRF保护;

3.在2017年2月25日就已经向它报告了这几个漏洞,但是仍然没有被修复

4.为了遵守漏洞披露机制,我选择使用MyBB作为接下来的案例分析

实际上,我们仍然是追寻'差异性'来达到攻击的目的

这次要分析的,是URL解析器,dns检查器,以及URL请求器之间的差异性

[![](https://p1.ssl.qhimg.com/t01cb754253e0708d6b.png)](https://p1.ssl.qhimg.com/t01cb754253e0708d6b.png)

上表列出了三种不同的web应用分别使用的URL解析器,dns检查器,以及URL请求器

[1] 第一种绕过方法

其实就是之前大家所普遍了解的dns-rebinding攻击

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dbfa60493964ce85.png)

在dns解析和最终请求之间有一个时间差,可以通过重新解析dns的方法进行绕过

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d1facdd56fbf97e2.png)

1.gethostbyname()函数得到了ip地址1.2.3.4

2.检查发现,1.2.3.4不在黑名单列表中

3.用curl_init()来获得一个ip地址,这时候cURL会再次发出一次DNS请求

4.最终我们重新解析foo.orange.tw到127.0.0.1 产生了一个dns攻击

[2] 第二种绕过方法

利用DNS解析器和URL请求器之间的差异性攻击

[![](https://p2.ssl.qhimg.com/t011089abd3b138eeaf.png)](https://p2.ssl.qhimg.com/t011089abd3b138eeaf.png)

对于gethostbynamel()这个DNS解析器所用的函数来说

它没有使用IDNA标准的转换,但是cURL却使用了

于是最终产生的后果是,gethostbynamel()解析不到对应的ip,返回了false

也就绕过了这里的检查。

[3] 第三种绕过方法

利用URL解析器和URL请求器之间的差异性攻击

这个漏洞已经在PHP 7.0.13中得到了修复

[![](https://p5.ssl.qhimg.com/t016da0176d110316f4.png)](https://p5.ssl.qhimg.com/t016da0176d110316f4.png)

有趣的是,这里最终请求到的是127.0.0.1:11211

而下一个payload则显示了curl的问题,最终也被解析到本地ip

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0150b45264fe1d90d1.png)

而这个漏洞也在cURL 7.54中被修复

可惜的是,ubuntu 17.04中自带的libcurl的版本仍然是7.52.1

但是,即使是这样进行了修复,参照之前的方法,添加空格仍然继续可以绕过

[![](https://p2.ssl.qhimg.com/t01990188ff014a793b.png)](https://p2.ssl.qhimg.com/t01990188ff014a793b.png)

而且cURL明确表示不会修复



**协议'走私' 案例分析**

这次我们分析的是github企业版

它使用ruby on rails框架编写,而且代码已经被做了混淆处理

关于github企业版的远程代码执行漏洞

是github三周年报告的最好漏洞

它把4个漏洞结合为一个攻击链,实现了远程代码执行的攻击

[1] 第一个漏洞:在webhooks上的SSRF绕过

webhooks是什么?

[![](https://p0.ssl.qhimg.com/t0162890bd0173d144f.png)](https://p0.ssl.qhimg.com/t0162890bd0173d144f.png)

这就很明显了,它含有发送POST数据包的功能

而它是如何实现的呢?

请求器使用了rubygem-faraday是一个HTTP/REST 客户端库

而黑名单则由其内部的faraday-restrict-ip-addresses所定义

它过滤了localhost,127.0.0.1等地址

但是仅仅用一个简单的 0 就可以加以绕过,像这样

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019e3104cfefa421a3.png)

但是,这个漏洞里有好几个限制,比如

不允许302重定向

不允许http,https之外的协议

不允许CRLF注入

只允许POST方式发送数据包

[2] 第二个漏洞:github企业版使用Graphite来绘制图标,它运行在本地的8000端口

[![](https://p4.ssl.qhimg.com/t010f13db9ef27c6ab8.png)](https://p4.ssl.qhimg.com/t010f13db9ef27c6ab8.png)

这里也是存在SSRF的

[3] 第三个漏洞 Graphite 中的CRLF注入

Graphite是由python编写的

于是,分析可知,这第二个SSRF的实现是httplib.HTTPConnection

很明显的,httplib是存在CRLF注入问题的

于是,我们可以构造下面的URL,产生一个'走私'漏洞

[![](https://p1.ssl.qhimg.com/t0188aa7e93321bea9a.png)](https://p1.ssl.qhimg.com/t0188aa7e93321bea9a.png)

[4] 第四个漏洞 Memcached gem中不安全的编排问题

Github企业版使用Memcached gem来作为它的缓存客户端

所有缓存的ruby对象都会被编排

最终的攻击链如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010f0325b053150823.png)

这个漏洞最终获得了12500美金的奖励

在github企业版&lt;2.8.7中可以使用



**缓解措施**

[1] 应用层

使用唯一的ip地址和URL,而不是对输入的URL进行复用

简单的说,拒绝对输入的URL进行二次解析,只使用第一次的结果

[2] 网络层

使用防火墙或者协议来阻断内网的通行

[3] 相关的项目

由 @fin1te 编写的SafeCurl

它也被 @JordanMilne 所提倡



**总结**

SSRF中的新攻击面

[1] URL解析器的问题

[2] 滥用IDNA标准

协议'走私'中的新攻击向量

[1] 利用linux Glibc中的新特性

[2] 利用NodeJS对Unicode字符的处理问题

以及相关的具体案例分析



**未来展望**

[1] OAuth中的URL解析器

[2] 现代浏览器中的URL解析器

[3] 代理服务器中的URL解析器

以及.. 更多


