> 原文链接: https://www.anquanke.com//post/id/188293 


# 协议层的攻击——HTTP请求走私


                                阅读量   
                                **589711**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01265e60c3a1809fc2.png)](https://p1.ssl.qhimg.com/t01265e60c3a1809fc2.png)



作者：mengchen@知道创宇404实验室

## 1. 前言

最近在学习研究BlackHat的议题，其中有一篇议题——”HTTP Desync Attacks: Smashing into the Cell Next Door”引起了我极大地兴趣，在其中，作者讲述了HTTP走私攻击这一攻击手段，并且分享了他的一些攻击案例。我之前从未听说过这一攻击方式，决定对这一攻击方式进行一个完整的学习梳理，于是就有了这一篇文章。

当然了，作为这一攻击方式的初学者，难免会有一些错误，还请诸位斧正。



## 2. 发展时间线

最早在2005年，由Chaim Linhart，Amit Klein，Ronen Heled和Steve Orrin共同完成了一篇关于HTTP Request Smuggling这一攻击方式的报告。通过对整个RFC文档的分析以及丰富的实例，证明了这一攻击方式的危害性。

> [https://www.cgisecurity.com/lib/HTTP-Request-Smuggling.pdf](https://www.cgisecurity.com/lib/HTTP-Request-Smuggling.pdf)

在2016年的DEFCON 24 上，@regilero在他的议题——Hiding Wookiees in HTTP中对前面报告中的攻击方式进行了丰富和扩充。

> [https://media.defcon.org/DEF%20CON%2024/DEF%20CON%2024%20presentations/DEF%20CON%2024%20-%20Regilero-Hiding-Wookiees-In-Http.pdf](https://media.defcon.org/DEF%20CON%2024/DEF%20CON%2024%20presentations/DEF%20CON%2024%20-%20Regilero-Hiding-Wookiees-In-Http.pdf)

在2019年的BlackHat USA 2019上，PortSwigger的James Kettle在他的议题——HTTP Desync Attacks: Smashing into the Cell Next Door中针对当前的网络环境，展示了使用分块编码来进行攻击的攻击方式，扩展了攻击面，并且提出了完整的一套检测利用流程。

> [https://www.blackhat.com/us-19/briefings/schedule/#http-desync-attacks-smashing-into-the-cell-next-door-15153](https://www.blackhat.com/us-19/briefings/schedule/#http-desync-attacks-smashing-into-the-cell-next-door-15153)



## 3. 产生原因

HTTP请求走私这一攻击方式很特殊，它不像其他的Web攻击方式那样比较直观，它更多的是在复杂网络环境下，不同的服务器对RFC标准实现的方式不同，程度不同。这样一来，对同一个HTTP请求，不同的服务器可能会产生不同的处理结果，这样就产生了了安全风险。

在进行后续的学习研究前，我们先来认识一下如今使用最为广泛的HTTP 1.1的协议特性——Keep-Alive&amp;Pipeline。

在HTTP1.0之前的协议设计中，客户端每进行一次HTTP请求，就需要同服务器建立一个TCP链接。而现代的Web网站页面是由多种资源组成的，我们要获取一个网页的内容，不仅要请求HTML文档，还有JS、CSS、图片等各种各样的资源，这样如果按照之前的协议设计，就会导致HTTP服务器的负载开销增大。于是在HTTP1.1中，增加了Keep-Alive和Pipeline这两个特性。

所谓Keep-Alive，就是在HTTP请求中增加一个特殊的请求头Connection: Keep-Alive，告诉服务器，接收完这次HTTP请求后，不要关闭TCP链接，后面对相同目标服务器的HTTP请求，重用这一个TCP链接，这样只需要进行一次TCP握手的过程，可以减少服务器的开销，节约资源，还能加快访问速度。当然，这个特性在HTTP1.1中是默认开启的。

有了Keep-Alive之后，后续就有了Pipeline，在这里呢，客户端可以像流水线一样发送自己的HTTP请求，而不需要等待服务器的响应，服务器那边接收到请求后，需要遵循先入先出机制，将请求和响应严格对应起来，再将响应发送给客户端。

现如今，浏览器默认是不启用Pipeline的，但是一般的服务器都提供了对Pipleline的支持。

为了提升用户的浏览速度，提高使用体验，减轻服务器的负担，很多网站都用上了CDN加速服务，最简单的加速服务，就是在源站的前面加上一个具有缓存功能的反向代理服务器，用户在请求某些静态资源时，直接从代理服务器中就可以获取到，不用再从源站所在服务器获取。这就有了一个很典型的拓扑结构。

[![](https://p4.ssl.qhimg.com/t01944fdcd9da8866fe.png)](https://p4.ssl.qhimg.com/t01944fdcd9da8866fe.png)

一般来说，反向代理服务器与后端的源站服务器之间，会重用TCP链接。这也很容易理解，用户的分布范围是十分广泛，建立连接的时间也是不确定的，这样TCP链接就很难重用，而代理服务器与后端的源站服务器的IP地址是相对固定，不同用户的请求通过代理服务器与源站服务器建立链接，这两者之间的TCP链接进行重用，也就顺理成章了。

当我们向代理服务器发送一个比较模糊的HTTP请求时，由于两者服务器的实现方式不同，可能代理服务器认为这是一个HTTP请求，然后将其转发给了后端的源站服务器，但源站服务器经过解析处理后，只认为其中的一部分为正常请求，剩下的那一部分，就算是走私的请求，当该部分对正常用户的请求造成了影响之后，就实现了HTTP走私攻击。

### 3.1 CL不为0的GET请求

其实在这里，影响到的并不仅仅是GET请求，所有不携带请求体的HTTP请求都有可能受此影响，只因为GET比较典型，我们把它作为一个例子。

在RFC2616中，没有对GET请求像POST请求那样携带请求体做出规定，在最新的RFC7231的4.3.1节中也仅仅提了一句。

> [https://tools.ietf.org/html/rfc7231#section-4.3.1](https://tools.ietf.org/html/rfc7231#section-4.3.1)
sending a payload body on a GET request might cause some existing implementations to reject the request

假设前端代理服务器允许GET请求携带请求体，而后端服务器不允许GET请求携带请求体，它会直接忽略掉GET请求中的Content-Length头，不进行处理。这就有可能导致请求走私。

比如我们构造请求

前端服务器收到该请求，通过读取Content-Length，判断这是一个完整的请求，然后转发给后端服务器，而后端服务器收到后，因为它不对Content-Length进行处理，由于Pipeline的存在，它就认为这是收到了两个请求，分别是

这就导致了请求走私。在本文的4.3.1小节有一个类似于这一攻击方式的实例，推荐结合起来看下。

### 3.2 CL-CL

在RFC7230的第3.3.3节中的第四条中，规定当服务器收到的请求中包含两个Content-Length，而且两者的值不同时，需要返回400错误。

> [https://tools.ietf.org/html/rfc7230#section-3.3.3](https://tools.ietf.org/html/rfc7230#section-3.3.3)

但是总有服务器不会严格的实现该规范，假设中间的代理服务器和后端的源站服务器在收到类似的请求时，都不会返回400错误，但是中间代理服务器按照第一个Content-Length的值对请求进行处理，而后端源站服务器按照第二个Content-Length的值进行处理。

此时恶意攻击者可以构造一个特殊的请求

中间代理服务器获取到的数据包的长度为8，将上述整个数据包原封不动的转发给后端的源站服务器，而后端服务器获取到的数据包长度为7。当读取完前7个字符后，后端服务器认为已经读取完毕，然后生成对应的响应，发送出去。而此时的缓冲区去还剩余一个字母a，对于后端服务器来说，这个a是下一个请求的一部分，但是还没有传输完毕。此时恰巧有一个其他的正常用户对服务器进行了请求，假设请求如图所示。

从前面我们也知道了，代理服务器与源站服务器之间一般会重用TCP连接。

这时候正常用户的请求就拼接到了字母a的后面，当后端服务器接收完毕后，它实际处理的请求其实是

这时候用户就会收到一个类似于aGET request method not found的报错。这样就实现了一次HTTP走私攻击，而且还对正常用户的行为造成了影响，而且后续可以扩展成类似于CSRF的攻击方式。

但是两个Content-Length这种请求包还是太过于理想化了，一般的服务器都不会接受这种存在两个请求头的请求包。但是在RFC2616的第4.4节中，规定:如果收到同时存在Content-Length和Transfer-Encoding这两个请求头的请求包时，在处理的时候必须忽略Content-Length，这其实也就意味着请求包中同时包含这两个请求头并不算违规，服务器也不需要返回400错误。服务器在这里的实现更容易出问题。

> [https://tools.ietf.org/html/rfc2616#section-4.4](https://tools.ietf.org/html/rfc2616#section-4.4)

### 3.3 CL-TE

所谓CL-TE，就是当收到存在两个请求头的请求包时，前端代理服务器只处理Content-Length这一请求头，而后端服务器会遵守RFC2616的规定，忽略掉Content-Length，处理Transfer-Encoding这一请求头。

chunk传输数据格式如下，其中size的值由16进制表示。

Lab 地址：[https://portswigger.net/web-security/request-smuggling/lab-basic-cl-te](https://portswigger.net/web-security/request-smuggling/lab-basic-cl-te)

构造数据包

连续发送几次请求就可以获得该响应。

[![](https://p5.ssl.qhimg.com/dm/1024_376_/t0154d15c6a23d91a66.png)](https://p5.ssl.qhimg.com/dm/1024_376_/t0154d15c6a23d91a66.png)

由于前端服务器处理Content-Length，所以这个请求对于它来说是一个完整的请求，请求体的长度为6，也就是

当请求包经过代理服务器转发给后端服务器时，后端服务器处理Transfer-Encoding，当它读取到0rnrn时，认为已经读取到结尾了，但是剩下的字母G就被留在了缓冲区中，等待后续请求的到来。当我们重复发送请求后，发送的请求在后端服务器拼接成了类似下面这种请求。

服务器在解析时当然会产生报错了。

### 3.4 TE-CL

所谓TE-CL，就是当收到存在两个请求头的请求包时，前端代理服务器处理Transfer-Encoding这一请求头，而后端服务器处理Content-Length请求头。

Lab地址：[https://portswigger.net/web-security/request-smuggling/lab-basic-te-cl](https://portswigger.net/web-security/request-smuggling/lab-basic-te-cl)

构造数据包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_387_/t01ff6b6252ddadda17.png)

由于前端服务器处理Transfer-Encoding，当其读取到0rnrn时，认为是读取完毕了，此时这个请求对代理服务器来说是一个完整的请求，然后转发给后端服务器，后端服务器处理Content-Length请求头，当它读取完12rn之后，就认为这个请求已经结束了，后面的数据就认为是另一个请求了，也就是

成功报错。

### 3.5 TE-TE

TE-TE，也很容易理解，当收到存在两个请求头的请求包时，前后端服务器都处理Transfer-Encoding请求头，这确实是实现了RFC的标准。不过前后端服务器毕竟不是同一种，这就有了一种方法，我们可以对发送的请求包中的Transfer-Encoding进行某种混淆操作，从而使其中一个服务器不处理Transfer-Encoding请求头。从某种意义上还是CL-TE或者TE-CL。

Lab地址：[https://portswigger.net/web-security/request-smuggling/lab-ofuscating-te-header](https://portswigger.net/web-security/request-smuggling/lab-ofuscating-te-header)

构造数据包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_442_/t01d986e8431f7f34ab.png)



## 4. HTTP走私攻击实例——CVE-2018-8004

### 4.1 漏洞概述

Apache Traffic Server（ATS）是美国阿帕奇（Apache）软件基金会的一款高效、可扩展的HTTP代理和缓存服务器。

Apache ATS 6.0.0版本至6.2.2版本和7.0.0版本至7.1.3版本中存在安全漏洞。攻击者可利用该漏洞实施HTTP请求走私攻击或造成缓存中毒。

在美国国家信息安全漏洞库中，我们可以找到关于该漏洞的四个补丁，接下来我们详细看一下。

CVE-2018-8004 补丁列表
- [https://github.com/apache/trafficserver/pull/3192](https://github.com/apache/trafficserver/pull/3192)
- [https://github.com/apache/trafficserver/pull/3201](https://github.com/apache/trafficserver/pull/3201)
- [https://github.com/apache/trafficserver/pull/3231](https://github.com/apache/trafficserver/pull/3231)
- [https://github.com/apache/trafficserver/pull/3251](https://github.com/apache/trafficserver/pull/3251)
注：虽然漏洞通告中描述该漏洞影响范围到7.1.3版本，但从github上补丁归档的版本中看，在7.1.3版本中已经修复了大部分的漏洞。

### 4.2 测试环境

#### 4.2.1 简介

在这里，我们以ATS 7.1.2为例，搭建一个简单的测试环境。

环境组件介绍

环境拓扑图

[![](https://p0.ssl.qhimg.com/t01c886cfbd14efd469.png)](https://p0.ssl.qhimg.com/t01c886cfbd14efd469.png)

Apache Traffic Server 一般用作HTTP代理和缓存服务器，在这个测试环境中，我将其运行在了本地的Ubuntu虚拟机中，把它配置为后端服务器LAMP&amp;LNMP的反向代理，然后修改本机HOST文件，将域名ats.mengsec.com和lnmp.mengsec,com解析到这个IP，然后在ATS上配置映射，最终实现的效果就是，我们在本机访问域名ats.mengsec.com通过中间的代理服务器，获得LAMP的响应，在本机访问域名lnmp.mengsec,com，获得LNMP的响应。

为了方便查看请求的数据包，我在LNMP和LAMP的Web目录下都放置了输出请求头的脚本。

LNMP:

LAMP:

#### 4.2.2 搭建过程

在GIthub上下载源码编译安装ATS。

安装依赖&amp;常用工具。

然后解压源码，进行编译&amp;安装。

安装完毕后，配置反向代理和映射。

编辑records.config配置文件，在这里暂时把ATS的缓存功能关闭。

编辑remap.config配置文件，在末尾添加要映射的规则表。

配置完毕后重启一下服务器使配置生效，我们可以正常访问来测试一下。

为了准确获得服务器的响应，我们使用管道符和nc来与服务器建立链接。

[![](https://p1.ssl.qhimg.com/dm/1024_503_/t014de83f2ec2932296.png)](https://p1.ssl.qhimg.com/dm/1024_503_/t014de83f2ec2932296.png)

可以看到我们成功的访问到了后端的LAMP服务器。

同样的可以测试，代理服务器与后端LNMP服务器的连通性。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_598_/t012569f6bff816522d.png)

### 4.3 漏洞测试

来看下四个补丁以及它的描述

> [https://github.com/apache/trafficserver/pull/3192](https://github.com/apache/trafficserver/pull/3192) # 3192 如果字段名称后面和冒号前面有空格，则返回400 [https://github.com/apache/trafficserver/pull/3201](https://github.com/apache/trafficserver/pull/3201) # 3201 当返回400错误时，关闭链接[https://github.com/apache/trafficserver/pull/3231](https://github.com/apache/trafficserver/pull/3231) # 3231 验证请求中的Content-Length头[https://github.com/apache/trafficserver/pull/3251](https://github.com/apache/trafficserver/pull/3251) # 3251 当缓存命中时，清空请求体

#### 4.3.1 第一个补丁

> [https://github.com/apache/trafficserver/pull/3192](https://github.com/apache/trafficserver/pull/3192) # 3192 如果字段名称后面和冒号前面有空格，则返回400

看介绍是给ATS增加了RFC7230第3.2.4章的实现，

> [https://tools.ietf.org/html/rfc7230#section-3.2.4](https://tools.ietf.org/html/rfc7230#section-3.2.4)

在其中，规定了HTTP的请求包中，请求头字段与后续的冒号之间不能有空白字符，如果存在空白字符的话，服务器必须返回400，从补丁中来看的话，在ATS 7.1.2中，并没有对该标准进行一个详细的实现。当ATS服务器接收到的请求中存在请求字段与:之间存在空格的字段时，并不会对其进行修改，也不会按照RFC标准所描述的那样返回400错误，而是直接将其转发给后端服务器。

而当后端服务器也没有对该标准进行严格的实现时，就有可能导致HTTP走私攻击。比如Nginx服务器，在收到请求头字段与冒号之间存在空格的请求时，会忽略该请求头，而不是返回400错误。

在这时，我们可以构造一个特殊的HTTP请求，进行走私。

[![](https://p4.ssl.qhimg.com/dm/1024_405_/t01b1506d08af14d5c9.png)](https://p4.ssl.qhimg.com/dm/1024_405_/t01b1506d08af14d5c9.png)

很明显，请求包中下面的数据部分在传输过程中被后端服务器解析成了请求头。

来看下Wireshark中的数据包，ATS在与后端Nginx服务器进行数据传输的过程中，重用了TCP连接。

[![](https://p2.ssl.qhimg.com/dm/798_1024_/t01696d17c5574917a4.png)](https://p2.ssl.qhimg.com/dm/798_1024_/t01696d17c5574917a4.png)

只看一下请求，如图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_496_/t0133f9f576312131f3.png)

阴影部分为第一个请求，剩下的部分为第二个请求。

在我们发送的请求中，存在特殊构造的请求头Content-Length : 56，56就是后续数据的长度。

在数据的末尾，不存在rn这个结尾。

当我们的请求到达ATS服务器时，因为ATS服务器可以解析Content-Length : 56这个中间存在空格的请求头，它认为这个请求头是有效的。这样一来，后续的数据也被当做这个请求的一部分。总的来看，对于ATS服务器，这个请求就是完整的一个请求。

ATS收到这个请求之后，根据Host字段的值，将这个请求包转发给对应的后端服务器。在这里是转发到了Nginx服务器上。

而Nginx服务器在遇到类似于这种Content-Length : 56的请求头时，会认为其是无效的，然后将其忽略掉。但并不会返回400错误，对于Nginx来说，收到的请求为

因为最后的末尾没有rn，这就相当于收到了一个完整的GET请求和一个不完整的GET请求。

完整的：

不完整的：

在这时，Nginx就会将第一个请求包对应的响应发送给ATS服务器，然后等待后续的第二个请求传输完毕再进行响应。

当ATS转发的下一个请求到达时，对于Nginx来说，就直接拼接到了刚刚收到的那个不完整的请求包的后面。也就相当于

然后Nginx将这个请求包的响应发送给ATS服务器，我们收到的响应中就存在了attack: 1和foo: GET / HTTP/1.1这两个键值对了。

那这会造成什么危害呢？可以想一下，如果ATS转发的第二个请求不是我们发送的呢？让我们试一下。

假设在Nginx服务器下存在一个admin.php，代码内容如下：

由于HTTP协议本身是无状态的，很多网站都是使用Cookie来判断用户的身份信息。通过这个漏洞，我们可以盗用管理员的身份信息。在这个例子中，管理员的请求中会携带这个一个Cookie的键值对admin=1，当拥有管理员身份时，就能通过GET方式传入要删除的用户名称，然后删除对应的用户。

在前面我们也知道了，通过构造特殊的请求包，可以使Nginx服务器把收到的某个请求作为上一个请求的一部分。这样一来，我们就能盗用管理员的Cookie了。

构造数据包

然后是管理员的正常请求

让我们看一下效果如何。

[![](https://p2.ssl.qhimg.com/dm/1024_257_/t0180103aedb64d5d17.png)](https://p2.ssl.qhimg.com/dm/1024_257_/t0180103aedb64d5d17.png)

在Wireshark的数据包中看的很直观，阴影部分为管理员发送的正常请求。

[![](https://p3.ssl.qhimg.com/dm/1024_392_/t017ccf616af405e676.png)](https://p3.ssl.qhimg.com/dm/1024_392_/t017ccf616af405e676.png)

在Nginx服务器上拼接到了上一个请求中， 成功删除了用户mengchen。

#### 4.3.2 第二个补丁

> [https://github.com/apache/trafficserver/pull/3201](https://github.com/apache/trafficserver/pull/3201) # 3201 当返回400错误时，关闭连接

这个补丁说明了，在ATS 7.1.2中，如果请求导致了400错误，建立的TCP链接也不会关闭。在regilero的对CVE-2018-8004的分析[文章](https://regilero.github.io/english/security/2019/10/17/security_apache_traffic_server_http_smuggling/)中，说明了如何利用这个漏洞进行攻击。

一共能够获得2个响应，都是400错误。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/830_1024_/t0103aa6bdab1e77786.png)

ATS在解析HTTP请求时，如果遇到NULL，会导致一个截断操作，我们发送的这一个请求，对于ATS服务器来说，算是两个请求。

第一个

第二个

第一个请求在解析的时候遇到了NULL，ATS服务器响应了第一个400错误，后面的bbrn成了后面请求的开头，不符合HTTP请求的规范，这就响应了第二个400错误。

再进行修改下进行测试

[![](https://p1.ssl.qhimg.com/dm/748_1024_/t012004c15330b14970.png)](https://p1.ssl.qhimg.com/dm/748_1024_/t012004c15330b14970.png)

一个400响应，一个200响应，在Wireshark中也能看到，ATS把第二个请求转发给了后端Apache服务器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_672_/t01325ab42c208d2e8b.png)

那么由此就已经算是一个HTTP请求拆分攻击了，

但是这个请求包，怎么看都是两个请求，中间的GET /1.html HTTP/1.1rn不符合HTTP数据包中请求头Name:Value的格式。在这里我们可以使用absoluteURI，在RFC2616中第5.1.2节中规定了它的详细格式。

> [https://tools.ietf.org/html/rfc2616#section-5.1.2](https://tools.ietf.org/html/rfc2616#section-5.1.2)

我们可以使用类似GET http://www.w3.org/pub/WWW/TheProject.html HTTP/1.1的请求头进行请求。

构造数据包

本质上来说，这是两个HTTP请求，第一个为

其中GET http://ats.mengsec.com/1.html HTTP/1.1为名为GET http，值为//ats.mengsec.com/1.html HTTP/1.1的请求头。

第二个为

当该请求发送给ATS服务器之后，我们可以获取到三个HTTP响应，第一个为400，第二个为200，第三个为404。多出来的那个响应就是ATS中间对服务器1.html的请求的响应。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/786_1024_/t01e41772ca4901cca0.png)

根据HTTP Pipepline的先入先出规则，假设攻击者向ATS服务器发送了第一个恶意请求，然后受害者向ATS服务器发送了一个正常的请求，受害者获取到的响应，就会是攻击者发送的恶意请求中的GET http://evil.mengsec.com/evil.html HTTP/1.1中的内容。这种攻击方式理论上是可以成功的，但是利用条件还是太苛刻了。

对于该漏洞的修复方式，ATS服务器选择了，当遇到400错误时，关闭TCP链接，这样无论后续有什么请求，都不会对其他用户造成影响了。

#### 4.3.3 第三个补丁

> [https://github.com/apache/trafficserver/pull/3231](https://github.com/apache/trafficserver/pull/3231) # 3231 验证请求中的Content-Length头

在该补丁中，bryancall 的描述是

从这里我们可以知道，ATS 7.1.2版本中，并没有对RFC2616的标准进行完全实现，我们或许可以进行CL-TE走私攻击。

构造请求

多次发送后就能获得405 Not Allowed响应。

[![](https://p4.ssl.qhimg.com/dm/1024_387_/t01037ead694bd6dcf0.png)](https://p4.ssl.qhimg.com/dm/1024_387_/t01037ead694bd6dcf0.png)

我们可以认为，后续的多个请求在Nginx服务器上被组合成了类似如下所示的请求。

对于Nginx来说，GGET这种请求方法是不存在的，当然会返回405报错了。

接下来尝试攻击下admin.php，构造请求

多次请求后获得了响应You are not Admin，说明服务器对admin.php进行了请求。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_254_/t0105ae22eff62e5868.png)

如果此时管理员已经登录了，然后想要访问一下网站的主页。他的请求为

效果如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_344_/t013371070f3f1720cc.png)

我们可以看一下Wireshark的流量，其实还是很好理解的。

[![](https://p4.ssl.qhimg.com/dm/1024_514_/t013bed72287733852b.png)](https://p4.ssl.qhimg.com/dm/1024_514_/t013bed72287733852b.png)

阴影所示部分就是管理员发送的请求，在Nginx服务器中组合进入了上一个请求中，就相当于

携带着管理员的Cookie进行了删除用户的操作。这个与前面4.3.1中的利用方式在某种意义上其实是相同的。

#### 4.3.3 第四个补丁

> [https://github.com/apache/trafficserver/pull/3251](https://github.com/apache/trafficserver/pull/3251) # 3251 当缓存命中时，清空请求体

当时看这个补丁时，感觉是一脸懵逼，只知道应该和缓存有关，但一直想不到哪里会出问题。看代码也没找到，在9月17号的时候regilero的分析文章出来才知道问题在哪。

当缓存命中之后，ATS服务器会忽略请求中的Content-Length请求头，此时请求体中的数据会被ATS当做另外的HTTP请求来处理，这就导致了一个非常容易利用的请求走私漏洞。

在进行测试之前，把测试环境中ATS服务器的缓存功能打开，对默认配置进行一下修改，方便我们进行测试。

然后重启服务器即可生效。

为了方便测试，我在Nginx网站目录下写了一个生成随机字符串的脚本random_str.php

构造请求包

第一次请求

[![](https://p5.ssl.qhimg.com/dm/1024_294_/t0103267034b841e4a8.png)](https://p5.ssl.qhimg.com/dm/1024_294_/t0103267034b841e4a8.png)

第二次请求

[![](https://p4.ssl.qhimg.com/dm/1024_425_/t017c3edd4602393e2e.png)](https://p4.ssl.qhimg.com/dm/1024_425_/t017c3edd4602393e2e.png)

可以看到，当缓存命中时，请求体中的数据变成了下一个请求，并且成功的获得了响应。

而且在整个请求中，所有的请求头都是符合RFC规范的，这就意味着，在ATS前方的代理服务器，哪怕严格实现了RFC标准，也无法避免该攻击行为对其他用户造成影响。

ATS的修复措施也是简单粗暴，当缓存命中时，把整个请求体清空就好了。



## 5. 其他攻击实例

在前面，我们已经看到了不同种代理服务器组合所产生的HTTP请求走私漏洞，也成功模拟了使用HTTP请求走私这一攻击手段来进行会话劫持，但它能做的不仅仅是这些，在PortSwigger中提供了利用HTTP请求走私攻击的[实验](https://portswigger.net/web-security/request-smuggling/exploiting)，可以说是很典型了。

### 5.1 绕过前端服务器的安全控制

在这个网络环境中，前端服务器负责实现安全控制，只有被允许的请求才能转发给后端服务器，而后端服务器无条件的相信前端服务器转发过来的全部请求，对每个请求都进行响应。因此我们可以利用HTTP请求走私，将无法访问的请求走私给后端服务器并获得响应。在这里有两个实验，分别是使用CL-TE和TE-CL绕过前端的访问控制。

#### 5.1.1 使用CL-TE绕过前端服务器安全控制

Lab地址：[https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-cl-te](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-cl-te)

实验的最终目的是获取admin权限并删除用户carlos

我们直接访问/admin，会返回提示Path /admin is blocked，看样子是被前端服务器阻止了，根据题目的提示CL-TE，我们可以尝试构造数据包

进行多次请求之后，我们可以获得走私过去的请求的响应。

[![](https://p3.ssl.qhimg.com/dm/1024_661_/t011a7de538023b58ea.png)](https://p3.ssl.qhimg.com/dm/1024_661_/t011a7de538023b58ea.png)

提示只有是以管理员身份访问或者在本地登录才可以访问/admin接口。

在下方走私的请求中，添加一个Host: localhost请求头，然后重新进行请求，一次不成功多试几次。

如图所示，我们成功访问了admin界面。也知道了如何删除一个用户，也就是对/admin/delete?username=carlos进行请求。

[![](https://p5.ssl.qhimg.com/dm/1024_666_/t01bcf98c1d94c9fe24.png)](https://p5.ssl.qhimg.com/dm/1024_666_/t01bcf98c1d94c9fe24.png)

修改下走私的请求包再发送几次即可成功删除用户carlos。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_395_/t0117f8002476468b35.png)

需要注意的一点是在这里，不需要我们对其他用户造成影响，因此走私过去的请求也必须是一个完整的请求，最后的两个rn不能丢弃。

#### 5.1.1 使用TE-CL绕过前端服务器安全控制

Lab地址：[https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-te-cl](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-te-cl)

这个实验与上一个就十分类似了，具体攻击过程就不在赘述了。

[![](https://p4.ssl.qhimg.com/dm/1024_352_/t01f9c5d1e5cbc2f0a8.png)](https://p4.ssl.qhimg.com/dm/1024_352_/t01f9c5d1e5cbc2f0a8.png)

### 5.2 获取前端服务器重写请求字段

在有的网络环境下，前端代理服务器在收到请求后，不会直接转发给后端服务器，而是先添加一些必要的字段，然后再转发给后端服务器。这些字段是后端服务器对请求进行处理所必须的，比如：
- 描述TLS连接所使用的协议和密码
- 包含用户IP地址的XFF头
- 用户的会话令牌ID
总之，如果不能获取到代理服务器添加或者重写的字段，我们走私过去的请求就不能被后端服务器进行正确的处理。那么我们该如何获取这些值呢。PortSwigger提供了一个很简单的方法，主要是三大步骤：
- 找一个能够将请求参数的值输出到响应中的POST请求
- 把该POST请求中，找到的这个特殊的参数放在消息的最后面
- 然后走私这一个请求，然后直接发送一个普通的请求，前端服务器对这个请求重写的一些字段就会显示出来。
怎么理解呢，还是做一下实验来一起来学习下吧。

Lab地址：[https://portswigger.net/web-security/request-smuggling/exploiting/lab-reveal-front-end-request-rewriting](https://portswigger.net/web-security/request-smuggling/exploiting/lab-reveal-front-end-request-rewriting)

实验的最终目的还是删除用户 carlos。

我们首先进行第一步骤，找一个能够将请求参数的值输出到响应中的POST请求。

在网页上方的搜索功能就符合要求

[![](https://p0.ssl.qhimg.com/dm/1024_349_/t0151e0d36820b82868.png)](https://p0.ssl.qhimg.com/dm/1024_349_/t0151e0d36820b82868.png)

构造数据包

多次请求之后就可以获得前端服务器添加的请求头

[![](https://p0.ssl.qhimg.com/dm/1024_695_/t019bddd028f6587912.png)](https://p0.ssl.qhimg.com/dm/1024_695_/t019bddd028f6587912.png)

这是如何获取的呢，可以从我们构造的数据包来入手，可以看到，我们走私过去的请求为

其中Content-Length的值为70，显然下面携带的数据的长度是不够70的，因此后端服务器在接收到这个走私的请求之后，会认为这个请求还没传输完毕，继续等待传输。

接着我们又继续发送相同的数据包，后端服务器接收到的是前端代理服务器已经处理好的请求，当接收的数据的总长度到达70时，后端服务器认为这个请求已经传输完毕了，然后进行响应。这样一来，后来的请求的一部分被作为了走私的请求的参数的一部分，然后从响应中表示了出来，我们就能获取到了前端服务器重写的字段。

在走私的请求上添加这个字段，然后走私一个删除用户的请求就好了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_394_/t01436188ea259ef72a.png)

### 5.3 获取其他用户的请求

在上一个实验中，我们通过走私一个不完整的请求来获取前端服务器添加的字段，而字段来自于我们后续发送的请求。换句话说，我们通过请求走私获取到了我们走私请求之后的请求。如果在我们的恶意请求之后，其他用户也进行了请求呢？我们寻找的这个POST请求会将获得的数据存储并展示出来呢？这样一来，我们可以走私一个恶意请求，将其他用户的请求的信息拼接到走私请求之后，并存储到网站中，我们再查看这些数据，就能获取用户的请求了。这可以用来偷取用户的敏感信息，比如账号密码等信息。

Lab地址：[https://portswigger.net/web-security/request-smuggling/exploiting/lab-capture-other-users-requests](https://portswigger.net/web-security/request-smuggling/exploiting/lab-capture-other-users-requests)

实验的最终目的是获取其他用户的Cookie用来访问其他账号。

我们首先去寻找一个能够将传入的信息存储到网站中的POST请求表单，很容易就能发现网站中有一个用户评论的地方。

抓取POST请求并构造数据包

这样其实就足够了，但是有可能是实验环境的问题，我无论怎么等都不会获取到其他用户的请求，反而抓了一堆我自己的请求信息。不过原理就是这样，还是比较容易理解的，最重要的一点是，走私的请求是不完整的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_752_/t01d99b3369b427665a.png)

### 5.4 利用反射型XSS

我们可以使用HTTP走私请求搭配反射型XSS进行攻击，这样不需要与受害者进行交互，还能利用漏洞点在请求头中的XSS漏洞。

Lab地址：[https://portswigger.net/web-security/request-smuggling/exploiting/lab-deliver-reflected-xss](https://portswigger.net/web-security/request-smuggling/exploiting/lab-deliver-reflected-xss)

在实验介绍中已经告诉了前端服务器不支持分块编码，目标是执行alert(1)

首先根据UA出现的位置构造Payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_667_/t015eacd462a5bf6563.png)

然后构造数据包

此时在浏览器中访问，就会触发弹框

[![](https://p1.ssl.qhimg.com/dm/1024_215_/t01d99a03661d67403b.png)](https://p1.ssl.qhimg.com/dm/1024_215_/t01d99a03661d67403b.png)

再重新发一下，等一会刷新，可以看到这个实验已经解决了。

### 5.5 进行缓存投毒

一般来说，前端服务器出于性能原因，会对后端服务器的一些资源进行缓存，如果存在HTTP请求走私漏洞，则有可能使用重定向来进行缓存投毒，从而影响后续访问的所有用户。

Lab地址：[https://portswigger.net/web-security/request-smuggling/exploiting/lab-perform-web-cache-poisoning](https://portswigger.net/web-security/request-smuggling/exploiting/lab-perform-web-cache-poisoning)

实验环境中提供了漏洞利用的辅助服务器。

需要添加两个请求包，一个POST，携带要走私的请求包，另一个是正常的对JS文件发起的GET请求。

以下面这个JS文件为例

编辑响应服务器

[![](https://p5.ssl.qhimg.com/dm/955_1024_/t018f4994dd099e8138.png)](https://p5.ssl.qhimg.com/dm/955_1024_/t018f4994dd099e8138.png)

构造POST走私数据包

然后构造GET数据包

POST请求和GET请求交替进行，多进行几次，然后访问js文件，响应为缓存的漏洞利用服务器上的文件。

[![](https://p5.ssl.qhimg.com/dm/1024_162_/t01045087c8edd90ece.png)](https://p5.ssl.qhimg.com/dm/1024_162_/t01045087c8edd90ece.png)

访问主页，成功弹窗，可以知道，js文件成功的被前端服务器进行了缓存。

[![](https://p4.ssl.qhimg.com/dm/1024_245_/t016e76d0b9f29279bd.png)](https://p4.ssl.qhimg.com/dm/1024_245_/t016e76d0b9f29279bd.png)



## 6. 如何防御

从前面的大量案例中，我们已经知道了HTTP请求走私的危害性，那么该如何防御呢？不针对特定的服务器，通用的防御措施大概有三种。
- 禁用代理服务器与后端服务器之间的TCP连接重用。
- 使用HTTP/2协议。
- 前后端使用相同的服务器。
以上的措施有的不能从根本上解决问题，而且有着很多不足，就比如禁用代理服务器和后端服务器之间的TCP连接重用，会增大后端服务器的压力。使用HTTP/2在现在的网络条件下根本无法推广使用，哪怕支持HTTP/2协议的服务器也会兼容HTTP/1.1。从本质上来说，HTTP请求走私出现的原因并不是协议设计的问题，而是不同服务器实现的问题，个人认为最好的解决方案就是严格的实现RFC7230-7235中所规定的的标准，但这也是最难做到的。



## 参考链接
- [https://regilero.github.io/english/security/2019/10/17/security_apache_traffic_server_http_smuggling/](https://regilero.github.io/english/security/2019/10/17/security_apache_traffic_server_http_smuggling/)
- [https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn)
- [https://www.cgisecurity.com/lib/HTTP-Request-Smuggling.pdf](https://www.cgisecurity.com/lib/HTTP-Request-Smuggling.pdf)
- [https://media.defcon.org/DEF%20CON%2024/DEF%20CON%2024%20presentations/DEF%20CON%2024%20-%20Regilero-Hiding-Wookiees-In-Http.pdf](https://media.defcon.org/DEF%20CON%2024/DEF%20CON%2024%20presentations/DEF%20CON%2024%20-%20Regilero-Hiding-Wookiees-In-Http.pdf)

