> 原文链接: https://www.anquanke.com//post/id/246062 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 - 点击劫持专题


                                阅读量   
                                **32832**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01ac9859879ed7bbf1.png)](https://p4.ssl.qhimg.com/t01ac9859879ed7bbf1.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 客户端漏洞篇介绍

> 相对于服务器端漏洞篇，客户端漏洞篇会更加复杂，需要在我们之前学过的服务器篇的基础上去利用。



## 客户端漏洞篇 – 点击劫持专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%EF%BC%9F"></a>什么是点击劫持？

点击劫持，就是诱导受害者点击页面上透明的按钮或链接以发送一些恶意的请求。我们生活中就会遇到很多点击劫持，比如弹窗广告之类的。这是通过iframe技术在页面的最上层设置一个透明的按钮或链接，当用户误以为是点击页面上的按钮或链接时其实是点击的透明的按钮或链接，就神不知鬼不觉地触发了某些恶意请求。它和CSRF的区别就是，点击劫持是一定要受害者点击才会触发的。而且CSRF Token不能用于抵御点击劫持攻击，因为毕竟是受害者主动点击导致发送的请求。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%9E%84%E9%80%A0%E5%9F%BA%E7%A1%80%E7%9A%84%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何构造基础的点击劫持攻击？

点击劫持利用css去创建和操作图层，然后再利用iframe将恶意链接或按钮覆盖在页面最上层。例如

```
&lt;head&gt;
  &lt;style&gt;
    #target_website `{`
      position:relative;
      width:128px;
      height:128px;
      opacity:0.00001;
      z-index:2;
      `}`
    #decoy_website `{`
      position:absolute;
      width:300px;
      height:400px;
      z-index:1;
      `}`
  &lt;/style&gt;
&lt;/head&gt;
...
&lt;body&gt;
  &lt;div id="decoy_website"&gt;
  ...decoy web content here...
  &lt;/div&gt;
  &lt;iframe id="target_website" src="https://vulnerable-website.com"&gt;
  &lt;/iframe&gt;
&lt;/body&gt;
```

我们通过css让iframe层在原本页面层的上面，然后调整位置与页面中的诱导物重合，为了避免透明度检测，所以透明度设置了尽可能地最低。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8CSRF%20Token%E9%98%B2%E6%8A%A4%E7%9A%84%E5%9F%BA%E7%A1%80%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81"></a>配套靶场：使用CSRF Token防护的基础点击劫持

因为点击劫持不管怎么看都是由用户真实发出的请求，所以CSRF Token对于点击劫持是没有防护效果的。点击劫持的重点就是要对准，因为梨子使用的是Firefox Deleoper版，有一个标尺工具可以让我们精准地获取按钮的位置。

[![](https://p4.ssl.qhimg.com/t018e104773617ad3f4.png)](https://p4.ssl.qhimg.com/t018e104773617ad3f4.png)

得到准确的尺寸以后我们就可以构造payload了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018fb472096ade59a7.png)

然后将其存储到Exploit Server，当受害者接收到投放的页面以后就会因为点击劫持删除指定用户，这里要注意的是，千万不要自己点，因为删除操作只能执行一次，如果误删了，要等当前的靶场环境过期了才能再次开启靶场，而且靶场过期的时间是大约20分钟，burp并没有给出具体过期时间，这将是非常漫长的等待。

[![](https://p4.ssl.qhimg.com/t017b484896dc9520c5.png)](https://p4.ssl.qhimg.com/t017b484896dc9520c5.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E9%A2%84%E5%A1%AB%E5%85%85%E8%A1%A8%E5%8D%95%E8%BE%93%E5%85%A5%E7%9A%84%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81"></a>使用预填充表单输入的点击劫持

有的站点允许通过GET参数的方式预填充表单，而不需要用户再手动输入，搭配上点击劫持就会当用户提交表单时提交预填充的表单。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E4%BB%8EURL%E5%8F%82%E6%95%B0%E9%A2%84%E5%A1%AB%E5%85%85%E7%9A%84%E8%A1%A8%E5%8D%95%E8%BE%93%E5%85%A5%E6%95%B0%E6%8D%AE%E7%9A%84%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81"></a>配套靶场：使用从URL参数预填充的表单输入数据的点击劫持

这道靶场的利用方式与上面类似，只需要将iframe的src替换成带有参数值的URL即可

[![](https://p3.ssl.qhimg.com/t01f69e968f33051be4.png)](https://p3.ssl.qhimg.com/t01f69e968f33051be4.png)

这个位置和标准答案肯定会有出入的，需要不断调，切记不要真的点击，看看位置就好了

[![](https://p0.ssl.qhimg.com/t01a220f5d8cf3c1e4d.png)](https://p0.ssl.qhimg.com/t01a220f5d8cf3c1e4d.png)

### <a class="reference-link" name="%E7%A0%B4%E5%9D%8F%E6%A1%86%E6%9E%B6%E8%84%9A%E6%9C%AC"></a>破坏框架脚本

从前面我们了解到，只要可以框架化的站点都可能遭受点击劫持攻击。所以我们需要编写脚本去打破这些框架。可以通过JS附加组件或者扩展程序(如NoScript)实现。这些脚本需要实现下面功能。
- 检查并强制将当前应用程序窗口设置为主窗口或顶级窗口
- 让所有框架不透明化
- 阻止点击透明的框架
- 拦截并标记潜在的点击劫持攻击位置
但是这种技术是特定于浏览器和平台的，而且因为HTML比较灵活，攻击者有很多方法来绕过。并且有的浏览器阻止运行破坏框架脚本或者不支持运行JS脚本。攻击者采用HTML5的iframe沙箱属性来绕过破坏框架脚本。

```
&lt;iframe id="victim_website" src="https://victim-website.com" sandbox="allow-forms"&gt;&lt;/iframe&gt;
```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%9C%89%E7%A0%B4%E5%9D%8F%E6%A1%86%E6%9E%B6%E8%84%9A%E6%9C%AC%E7%9A%84%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81"></a>配套靶场：有破坏框架脚本的点击劫持

我们在页面中发现了一个破坏框架脚本

[![](https://p4.ssl.qhimg.com/t01f54454e6d407592f.png)](https://p4.ssl.qhimg.com/t01f54454e6d407592f.png)

这个脚本会检查该页面是不是最顶层，如果不是就返回false。所以我们要利用前面提到的方法绕过这个脚本的检测。

[![](https://p5.ssl.qhimg.com/t01723a2707baacebea.png)](https://p5.ssl.qhimg.com/t01723a2707baacebea.png)

这样我们又可以发动点击劫持攻击了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f10a66c11df8e488.png)

### <a class="reference-link" name="%E7%BB%93%E5%90%88%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%E5%92%8CDOM%20XSS%E7%9A%84%E6%94%BB%E5%87%BB"></a>结合点击劫持和DOM XSS的攻击

这是一种利用DOM XSS和iframe技术结合起来的攻击方式。在iframe的点击劫持中附加DOM XSS的payload，当受害者点击时即可同时触发DOM XSS。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%E6%BC%8F%E6%B4%9E%E8%A7%A6%E5%8F%91DOM%20XSS"></a>配套靶场：利用点击劫持漏洞触发DOM XSS

我们要找一下有没有相关DOM的操作，发现一个JS脚本(/resources/js/submitFeedback.js)，我们看看里面有什么有价值的东西。

[![](https://p5.ssl.qhimg.com/t01f64a3a24b004bbd4.png)](https://p5.ssl.qhimg.com/t01f64a3a24b004bbd4.png)

发现这里存在DOM XSS漏洞点，于是我们利用点击劫持将DOM XSS payload预填充到name框中

[![](https://p5.ssl.qhimg.com/t01b5efc089a4e6df85.png)](https://p5.ssl.qhimg.com/t01b5efc089a4e6df85.png)

这样就可以利用点击劫持触发DOM XSS了

[![](https://p0.ssl.qhimg.com/t0123397f8956411a73.png)](https://p0.ssl.qhimg.com/t0123397f8956411a73.png)

### <a class="reference-link" name="%E5%A4%9A%E9%87%8D%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81"></a>多重点击劫持

有的时候，需要诱导用户点击多处隐藏的按钮或者链接才能成功实现恶意的目的。下面我们通过一道靶场来讲解。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%A4%9A%E9%87%8D%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81"></a>配套靶场：多重点击劫持

因为要点击两个地方才可以，所以我们的payload也是要设置两个透明的按钮

[![](https://p1.ssl.qhimg.com/t016bffbd1ceae9c03e.png)](https://p1.ssl.qhimg.com/t016bffbd1ceae9c03e.png)

这两个按钮的位置也是要自己开启标尺以后调的，非常方便。

[![](https://p0.ssl.qhimg.com/t0140e7c5dd6a0e895e.png)](https://p0.ssl.qhimg.com/t0140e7c5dd6a0e895e.png)

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何缓解点击劫持攻击？

burp介绍了两种从服务器端缓解点击劫持攻击的方法，具体能不能有效实施还要看浏览器层面。

### <a class="reference-link" name="X-Frame-Options"></a>X-Frame-Options

一开始这个标头被用于IE8的非官方响应头使用的，后面被各浏览器采用。我们通过设置值来限制框架化操作。例如<br>`X-Frame-Options: deny`<br>
上面这条表示拒绝任何框架化操作，但是也可以限制框架化的来源为同源。<br>`X-Frame-Options: sameorigin`<br>
也可以设置为指定源<br>`X-Frame-Options: allow-from https://normal-website.com`<br>
如果将该响应头与CSP结合使用，效果更佳。

### <a class="reference-link" name="%E5%86%85%E5%AE%B9%E5%AE%89%E5%85%A8%E7%AD%96%E7%95%A5(CSP)"></a>内容安全策略(CSP)

XSS篇我们介绍过CSP，我们也可以使用CSP来缓解点击劫持攻击。例如<br>`Content-Security-Policy: frame-ancestors 'self';`<br>
这条与X-Frame-Options: sameorigin效果类似，也可以设置为指定源。<br>`Content-Security-Policy: frame-ancestors normal-website.com;`



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 – 点击劫持专题的全部内容啦，本专题主要讲了点击劫持漏洞的形成原理、利用、防护、绕过防护等，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
