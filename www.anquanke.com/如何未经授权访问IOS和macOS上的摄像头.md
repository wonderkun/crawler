
# 如何未经授权访问IOS和macOS上的摄像头


                                阅读量   
                                **472830**
                            
                        |
                        
                                                                                                                                    ![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Ryan Pickren，文章来源：
                                <br>原文地址：[Webcam Hacking-The story of how I gained unauthorized Camera access on iOS and macOS](Webcam%20Hacking-The%20story%20of%20how%20I%20gained%20unauthorized%20Camera%20access%20on%20iOS%20and%20macOS)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/202511/t011feb4eb7f89bf4e7.png)](./img/202511/t011feb4eb7f89bf4e7.png)

这篇文章介绍了我在攻破IOS/MacOS网络摄像头的过程中发现的多个Safari中的0-day漏洞，通过此项目，我可以在未授权的情况下访问以下资源：

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015b6b95b4bdad0da7.png)

文中包含我用来向Apple报告漏洞的[BugPoC](https://bugpoc.com/)地址，如果你想要查看PoC的执行效果，可以下载**Safari 13.0.4**。



## 一、背景

**注：此项目的目标是劫持iOS/macOS的网络摄像头，在此过程中发现的其他漏洞只是一些额外收获。**

在开始之前，我想先引用以前同事的一句话，“漏洞挖掘其实就是在软件中寻找并破坏假设的过程”，这也正是我们今天要做的事情。我们要深入探索Safari浏览器中的模糊区域，测试一些不常见案例，发现其中的奇怪表现，将多个奇怪表现组合在一起，就可以形成一个强大的利用链。

iOS和macOS中的[摄像头安全模型](https://developer.apple.com/documentation/avfoundation/cameras_and_media_capture/requesting_authorization_for_media_capture_on_ios)十分严格，简而言之，应用程序必须明确地获取摄像头/麦克风权限，该操作由系统通过一个标准的警示框实现：

但是这个规则也有一个例外，苹果自己的应用程序可以直接使用摄像头，所以说从技术上来讲，Mobile Safari无需询问即可访问摄像头。此外，一些新的网络技术，例如[MediaDevices](https://w3c.github.io/mediacapture-main/#mediadevices) Web API(通常用于[WebRTC](https://webrtc.org/)传输)，允许**网站**利用Safari的权限直接访问摄像头，这一点方便了Skype或者Zoom这样基于Web的视频会议软件的使用，但是却破坏了系统本身的摄像头安全模型。[这篇](https://webrtc-security.github.io/)论文“A Study of WebRTC Security”中提出了该问题：

> 如果用户选择了一款他们认为可以信任的浏览器，那么可以认为所有的WebRTC通信都是“安全”的……换句话来说，WebRTC提供给用户的信任等级直接受到用户对浏览器信任程度的影响。

所以每个iOS/macOS的用户都应该问自己——你有多信任Safari浏览器呢？

**注：加密是WebRTC的一个强制功能，只有在你的网站处于“[安全上下文](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts)”的情况下，才会显示出[mediaDevices](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices) API。这就意味着即使是像[这样](https://alf.nu/SafariReaderUXSS)，[这样](https://twitter.com/fransrosen/status/1009727379659468801?lang=en)，或是[这样](https://www.ryanpickren.com/browser-hacking)的通用跨站脚本攻击(UXSS)漏洞也无法获取摄像头的访问权限。摄像头权限在Safari中受到了很好的保护。**

有研究表明，Safari会跟踪每个网站的权限设置，这样网站在访问类似GPS或者摄像头这样的敏感信息时，就可以“无需总是请求权限”，也就是说，如果你信任Skype，你就可以允许Skype在任何时候访问你的摄像头。你可以在Safari-&gt;偏好设置-&gt;网站中查看你当前信任的网站。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019bfe5afd580d3f14.png)

这项功能需要Safari在浏览器⟺网站上下文中重新实现系统⟺应用程序的安全模型，这也就自然而然带出一个问题——Safari对网站的跟踪情况有多好？

现在可以开始制定攻击计划了，如果可以以某种方式诱使Safari认为我们的恶意网站处于一个受信任网站的“安全上下文”中，我们就可以利用Safari的摄像头权限通过mediaDevices API访问网络摄像头。



## 二、跟踪网站

为了让Safari使用你的网站设置，它首先要知道你正在浏览哪些网站，这实际上也是所有浏览器最基本的责任，并且是维护同源策略的核心要求。如果想要实现任何UXSS或者绕过同源策略，关键就是要让浏览器无法正确识别你正在浏览的网站。

在做了一些实验之后，我注意到了一个奇怪的现象——Safari好像并没有使用[源](https://html.spec.whatwg.org/multipage/origin.html#origin)来跟踪“当前打开的网站”，事实上，Safari在这里用来跟踪网站的方法十分奇怪。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019ffff093462db330.png)

如上图所示，这四个窗口有不同的源，但是Safari认为只打开了一个网站。经过更多的实验后，我推测Safari可能是对所有打开窗口使用了[通用URI语法解析](https://tools.ietf.org/html/rfc3986#section-3.2)来获取URI的主机名，之后再做进一步的解析，具体来说，Safari移除了主机名开头的”www.”。我对这种方法很感兴趣，众所周知，解析URL并[不容易](https://www.youtube.com/watch?v=0uejy9aCNbI)。

在用一些简单的主机名进行fuzzing时，我注意到了一个奇怪的现象，如果主机名中存在连在一起的连接号”-“和点号”.”(即“.-”或者”-.”)，Safari的“当前打开网站”功能就无法发现这样的主机名，我无法立刻将这种奇怪的现象和摄像头联系在一起，但这仍旧是一个有趣的发现，因为类似`https://foo-.evil.com`这样的URL就不会出现在菜单中。这是第一个漏洞，CVE-2020-9787，BugPoC上的演示：[bugpoc.com/poc#bp-Ay2ea1QE](https://bugpoc.com/poc#bp-Ay2ea1QE)，密码：laidMouse24，注意该演示只在Safari 13.0.4下有效。用[BugPoC](https://bugpoc.com/)这个平台做演示很方便，因为你可以直接在这里创建自定义的子域名来托管HTML代码。

除此之外,还有一个重要的发现就是Safari**完全忽略**了URL协议，这可能会存在一些问题。因为有一些协议根本不包含有意义的主机名，例如`file:`，`javascript:`或者`data:`， 还有一些协议在嵌入的URI中包含主机名（[《Web之困》](https://books.google.com/books?id=NU3wOk2jzWsC&amp;pg=PA37&amp;lpg=PA37&amp;dq=encapsulating+pseudo+protocols&amp;source=bl&amp;ots=fqnDcca6Qc&amp;sig=ACfU3U2DDzX9qe3YryKVhDBZeeBzOiTHlA&amp;hl=en&amp;sa=X&amp;ved=2ahUKEwjQsfXStprmAhUSMH0KHSm8BpUQ6AEwA3oECAoQAQ#v=onepage&amp;q=encapsulating%20pseudo%20protocols&amp;f=false)称之为“封装伪协议”），例如`blob:`或者`view-source:`。像Safari这样只是简单地提取`://`和`/`之间的字符串作为有效主机名是错误的，它应该保留一份可以这样进行解析的协议白名单，例如`http:`，`https:`，`ws:`，等等。这是第二个漏洞，CVE-2020-3852。

下面我想要找到一种方法利用该漏洞，首先尝试一些伪协议。



## 三、一些常见的协议

这里，我们的目标是要创建一个URI，在使用RFC3986中定义的[通用URI语法](https://tools.ietf.org/html/rfc3986#section-3.2)解析该URI后，会生成一个受害者信任的任意主机名，看起来好像挺简单的，是吧？

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01674fa912573f135a.png)

所以我打算从一些常见的协议开始实验——[`javascript:`](https://tools.ietf.org/html/draft-hoehrmann-javascript-scheme-03)，[`data:`](https://tools.ietf.org/html/rfc2397)以及[`about:`](https://tools.ietf.org/html/rfc6694)。

**注：事实上一个都没有成功，所以如果你不想看失败案例的话，可以直接跳到下一小节。**

### <a class="reference-link" name="3.1.%20javascript:"></a>3.1. javascript:

我一开始真的对这个协议充满希望的，我认为`javascript://skype.com`应该能够成功，因为这种情况下Safari看到的主机名应该是`skype.com`。事实证明并不是，在尝试打开这个URL时，Safari实际加载的是`about:blank`，而内容在进入URL栏前就直接发送给了JavaScript引擎。换句话说，在你浏览页面的时候，`window.location.href`并不会等于`javascript://skype.com`，我用了几种方法暂停页面加载，让Safari返回这个href，但是都没成功。下一个……

### <a class="reference-link" name="3.2.%20data:"></a>3.2. data:

下一个实验的是`data:`，目标是创建一个经过RFC2397(`data:`)和RFC3986(旧式的授权URI)解析后仍然有效的URI，如果需要的话，也可以是多语言的URI。经过一些测试后，我想到了这个：`data://,[@skype](https://github.com/skype).com`，我使用标准的`window.open()`打开这个页面，并检查了Safari的偏好设置，成功了，Safari认为打开的是`skykpe.com`！

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01495c7d29688c425f.png)

但还是有个问题，尽管从技术上来讲，这是一个有效的`data:` URI，但是Safari或者其他浏览器并不能识别媒体类型`//`，而且[规范](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs)规定默认的媒体类型是`text/plain`，这就意味着`data://,[@skype](https://github.com/skype).com?&lt;script&gt;alert(1)&lt;/script&gt;`只会生成一个无害的TXT文件，尽管Safari可能会对其内容感到奇怪，但是如果不执行Javascript，文件本身并不会造成任何破坏。而且由于Safari会给每个`data:` URI一个唯一的源，所以我们也不能使用Javascript后期渲染来动态填充文档。

```
w = open('data://,@skype.com');
w.document.write('&lt;script&gt;alert(1)&lt;/script&gt;');
&gt; SecurityError
```

这种隔离源保护策略实际上是为了防止新建文档[与其父文档混淆](https://blog.mozilla.org/security/2017/10/04/treating-data-urls-unique-origins-firefox-57/)，但技术上也可以阻止上述类型的攻击。我尝试了多种方法，想要让Safari把`data:` URI当作HTML进行渲染，但是都没有成功（或许有一天能够实现锚标签的[type](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a)属性……）。

在对Safari内部如何解析这类URL进行了仔细地研究后，我决定试一下`window.history`。先创建一个HTML属性的`data:` URI，然后把`pathname`修改为`//skype.com`，但是不进行真正的页面加载或导航（因此不会更新媒体类型）。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01862bb215fd410003.png)

但是很遗憾，RFC编写者已经考虑过这种情况，并且[明确禁止](https://www.w3.org/TR/html52/browsers.html#the-history-interface)使用`history.pushState`或者`history.replaceState`改变[源](https://url.spec.whatwg.org/#concept-url-origin)。注意，该规范引用了源的实际算法定义，而不是经典的协议/主机/端口组合。在这种情况下(`data:` URI)，使用`history.replaceState`会将源从不透明源(opaque origin)A改为不透明源B，没有任何意义。

```
history.replaceState('','','data://skype.com')
&gt; SecurityError
```

### <a class="reference-link" name="3.3.%20about:"></a>3.3. about:

现在只剩下最后一个了：`about:`，看起来这个协议是可以工作的，Safari接受了`about://skype.com`（在Chrome里这么做会报错），但是我仍旧无法对文档进行动态填充：

```
w = open('about://skype.com');
w.document.write('&lt;script&gt;alert(1)&lt;/script&gt;');
&gt; SecurityError
```

Safari似乎只允许`about:blank`和`about:srcdoc`[继承原网站的源](https://books.google.com/books?id=NU3wOk2jzWsC&amp;pg=PA167&amp;lpg=PA167&amp;dq=%22about:blank%22+origin+scheme+inherit&amp;source=bl&amp;ots=fqnDbe20Kf&amp;sig=ACfU3U3sRHu24XTuoXYfpyQngZKksRrVvQ&amp;hl=en&amp;sa=X&amp;ved=2ahUKEwjgkuuv7JfmAhXsJzQIHQXbA3MQ6AEwCXoECAoQAQ#v=onepage&amp;q=%22about%3Ablank%22%20origin%20scheme%20inherit&amp;f=false)。我找到了一个旧的[WebKit漏洞报告](https://bugs.webkit.org/show_bug.cgi?id=199933)，其中提到利用该漏洞可以放宽此限制，但是他们并没有进行实验。所以现在`about://skype.com`只有一个唯一的不透明源，就和`data:`一样，这也就意味着我们同样无法使用`history.pushState`修改源。



## 四、拯救者file:

我考虑的下一个协议是`file:`，看起来这个协议中不包含有意义的主机名，对吗？但是在我深入阅读RFC文档时，我发现了[一个`file:` URI的奇怪格式](https://tools.ietf.org/html/rfc8089#appendix-E.3.1)，这个格式可以包含主机名。此类型的URI指定了一个远程服务器，类似FTP协议，但是规范中并没有定义对存储在远程服务器上的文件的检索机制。进一步的搜索后，我没找到任何支持这类URI的用户代理。

```
file://host.example.com/Share/path/to/file.txt
```

出于好奇，我测试了一下Safari内部是如何解析正常的`file:` URI的。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0158ae02d6db419167.png)

和预期一样，`hostname`是空的，我决定使用Javascript指定一个主机名，看看会发生什么。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://static.wixstatic.com/media/149864_a02d1396f7fc4fec9022c90e40769d57~mv2.gif)

Safari竟然接受了这个URI并且重新加载了该内容，我竟然用一个很简单的技巧就修改了`document.domain`。这是第三个漏洞，CVE-2020-3885。

果然，Safari认为我们现在在浏览`skype.com`，所以我可以在这里加载一些有害的Javascript脚本。如果你打开我的本地HTML文件，摄像头、麦克风、屏幕共享都会被劫持。除此之外，还有一个额外收获，Safari似乎也使用这种主机名解析方式实现密码的自动填充功能，所以如果你使用了此功能，我就可以窃取到你的密码了。

```
&lt;!--  file://exploit.html  --&gt;
&lt;script&gt;
if (location.host != 'google.com'){
    location.host = 'google.com';
}
else {
    alert(document.domain);
}
&lt;/script&gt;
```

所以说攻击完成了吗？并没有。到目前为止，攻击仍需要受害者打开一个本地HTML文件，此外，这样的攻击方式在iOS上也不起作用，因为通过Mobile Safari下载的文件会以预览模式显示在一个嵌入式的视图中，该视图不存在Javascript引擎。所以我们还需要进一步研究。



## 五、一个意外发现的漏洞：auto-downloads

为了让上面的`file:`攻击更具有可行性，我想要让Safari从我们的网站自动下载有害的HTML文件（当然，下载文件只是成功的一半，受害者仍旧需要打开它）。

我记得之前在[Broken Browser](https://www.brokenbrowser.com/referer-spoofing-patch-bypass/)上看到过一个Edge上的referer头部欺骗漏洞，事实证明，可以用类似的技术绕过Safari对auto-download的限制，只需要在弹出窗口中打开一个受信任的网站，然后用该弹出窗口打开下载链接。这是第四个和第五个漏洞，CVE-2020-9784以及CVE-2020-3887。

```
open('https://dropbox.com','foo');
setTimeout(function(){open('/file.exe','foo');},1000)
```

我用BugPoC的[BugPoC Mock Endpoint](https://bugpoc.com/testers/other)功能创建了一个URL，该URL带有Content-Disposition响应头并包含了一个用于演示的文本文件。BugPoC演示地址：[bugpoc.com/poc#bp-t9C660OJ](https://bugpoc.com/poc#bp-t9C660OJ)，密码calmOkapi20，注意该演示只在Safari 13.0.4下有效。

下面让我们继续进行摄像头的攻击。



## 六、一个奇怪的协议 blob:

封装伪协议[`blob:`](https://developer.mozilla.org/en-US/docs/Web/API/Blob)是一个很有意思的工具，有了这个协议，你可以使用随机标识符直接访问隐藏在浏览器内存中的文件，这样你就可以很轻松地引用动态创建的文件了。虽然这种类型的URI通常用于图像和视频，但是它允许你自己指定媒体类型，Safari甚至会尽其所能的渲染所有内容，所以你可以创建一个HTML文档，并在新标签页中打开它。

```
blob = new Blob(['&lt;h1&gt;hello, world!&lt;/h1&gt;'], {type: 'text/html'});
url = URL.createObjectURL(blob);
open(url,'_blank');
```

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e28b7a7371aaa28c.png)

`blob:`[规范](https://www.w3.org/TR/FileAPI/#url)中规定了用于生成这类URI的算法，浏览器必须使用此算法生成此类URI。

```
blob: [origin of creating document] / [random UUID]
```

该算法中仍有一些细节值得研究，注意源被[序列化](https://html.spec.whatwg.org/multipage/origin.html#ascii-serialisation-of-an-origin)为了一个字符串，但是如果构成blob URI的源并没有有意义的序列化结果呢？就像是[有效域](https://html.spec.whatwg.org/multipage/origin.html#concept-origin-effective-domain)(effective domain)为空的文档，它的源是不透明的，而[不透明源](https://html.spec.whatwg.org/multipage/origin.html#concept-origin-opaque)（还记得我们上面提到的`data:text/html,foo`或是`about://foo`的源吗？）的序列化结果是字符串”null“，并且这个序列化结果无法还原。这就意味着，即使序列化后的字符串都是”null“，在Safari内部，它会认为`data:text/html,foo`和`data:text/html,bar`具有不同的不透明源。规范中规定，这种情况下由浏览器自行处理：

> 如果序列化结果为”null“，将其设置为浏览器定义的值。

那么就让我们看一下Safari是如何处理这种情况的，可以用`data:` URI获得一个不透明源：`data:text/html,foobar`，然后创建一个`blob:` URI。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019a3a34a27cd062b2.png)

从控制台的输出结果可以看出，`blob:` URI中序列化后的源是”null“，因为这样的序列化是无法还原的，我想知道Safari是怎么知道应该允许哪个不透明源打开该URI的。

经过一些实验后，我确定Safari在这里强制使用了同源策略，所以就必须使用随机UUID值找到真正创建了该URI的源。我们可以在创建该URI的文档中使用Javascript打开该`blob:` URI，而且这个新打开的文档会按照RFC编写者的要求，继承父文档的不透明源，但是在另一个不透明源中打开该URI，则会报错。

之后我注意到了一个奇怪的现象……在Safari地址栏中手动输入这个URL，返回的源是`://`。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01337f86bd23614a74.png)

Safari认为在这种情况下应该返回”空的(blank)“源，但是这并不是创建此文档的不透明源，事实上，根据[源序列化标准](https://html.spec.whatwg.org/multipage/origin.html#ascii-serialisation-of-an-origin)，这根本不是一个不透明源，而是空白协议、空白主机、空白端口在算法上的运行结果，这是第六个漏洞，CVE-2020-3864。在本文的剩余内容中，我会把这种奇怪的源叫做”空白“源。经过更多的实验，我发现源为null的`blob:` URI会继承任何打开文档的源！当然，Safari会先检查打开文档是否有权限打开该URL（同源策略）。但是如果打开文档不是一个普通文档时，事情就变得复杂了。可以查看BugPoC上的演示文件：[bugpoc.com/poc#bp-wkIedjRe](https://bugpoc.com/poc#bp-wkIedjRe)，密码是laidFrog49，注意该演示只在Safari 13.0.4下有效。

从书签访问该URI会导致一些十分奇怪的行为：

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://static.wixstatic.com/media/149864_81d23113568145b0bbbe60de3f5aaeb0~mv2.gif)

从上图中可以发现，Safari想要把这个源为null的`blob:` URI的源设置为`https://example.com`，但是失败了，因为在该内存位置并没有存储任何文档（所以出现的错误类型是WebKitBlobResource）。

但是如果打开文档是”空白”源`://`，Safari就可以找到该文档。所以说”空白“源是一种很奇怪的源，在某些情境下它等于null，但是又不是不透明源。只要在地址栏手动输入源为null的`blob:` URI就可以到达”空白“源。

现在需要找到一种方法，用代码到达”空白“源页面，也就是说要模拟手动输入地址栏的行为。Javascript中有一个API [`location.replace`](https://developer.mozilla.org/en-US/docs/Web/API/Location/replace)可以实现该目的，`location.replace`会替换当前资源，就好像我们最初访问的就是这个URL一样。但是有一点要注意，Safari会检查你是否有权限查看这个URL，因此location的替换以及URL的创建应该发生在同一文档中。

```
// 不透明源中：
blob = new Blob(['&lt;h1&gt;hello, world!&lt;/h1&gt;'], {type: 'text/html'});
url = URL.createObjectURL(blob);
location.replace(url);
```

现在我们成功地将一个具有不透明源的`data:` URI变成了一个具有”空白“源的`blob:` URI。接下来要做什么呢？



## 七、重返History

在3.2小结中我们想要用[`window.history`](https://developer.mozilla.org/en-US/docs/Web/API/Window/history)修改`data:` URI，但是没有成功，因为改变`pathname`会同时改变不透明源（history规范中明确禁止该行为）。

回顾一下我们目前的状况：

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0150a79793c4ade923.png)

现在试一下下面的代码：

```
history.pushState('','','blob://skype.com');
&gt; SecurityError
```

没有成功，看起来Safari识别出上面的`pushState`会发送一个新的源。但是我很快发现一个奇怪的现象，下面的`pushState`是可以通过的：

```
history.pushState('','','blob://');
history.pushState('','','skype.com'); 
location.href
&gt; blob://skype.com
```

所以说到底发生了什么？为什么使用一行代码失败了，但是把代码分成两行就成功了？你可以在[这里](https://url.spec.whatwg.org/#concept-url-origin)查看如何确定`blob:` URI的源，我的猜测是，Safari可以成功识别`blob://skype.com`的源是一个新的不透明源（规范中的第三步），但是出于某些原因，Safari认为`blob://`的源是”空白“源`://`（规范中的第二步）。此漏洞已经作为第六个漏洞CVE-2020-3864的一部分被修复。

因为现在的源也是`://`，所以允许`pushState`的执行，而下一个`pushState`只更改了`pathname`，所以Safari认为这步操作没有问题，这样`location.href`就被修改为了`blob://skype.com`。查看Safari的偏好设置，会发现当前打开网站已经变成了`skype.com`，所以攻击完成了吗？

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019e10acb16c1f23f7.png)

还不算完成。尽管Safari已经将文档识别为`skype.com`，而且我们已经可以在该文档上执行Javascript了，但是它仍旧不处于”安全上下文“中，因此我们仍旧[无法使用类似`mediaDevices`这样的API](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014b793edeb2b24283.png)

所以……

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010ca2ba16abbe74f3.png)

到目前为止，我们已经可以实现自动下载，自动弹出窗口以及自动填充密码了，但是仍旧没能控制摄像头，下面我们继续实验。



## 八、不需要TLS的安全上下文

我们先看一下”[安全上下文](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts)“是什么意思：

> 安全上下文指一个窗口或是工作器，我们有足够的理由相信其中的内容得到了安全的传输（通过HTTPS/TLS），并且与非安全上下文的通信也受到了限制。许多Web API和功能只能在安全上下文中访问。安全上下文的主要目标是为了防止中间人攻击访问功能强大的API，从而彻底攻破受害者的防御。

对于WebRTC来说，这确实是一个合理的要求。如果WiFi上的任何人都可以访问你的网络摄像头，那也太可怕了（假设你在访问信任的HTTP网站）。现在我们需要找到一个新的漏洞来绕过这项要求。

在深入研究”安全上下文“[规范](https://w3c.github.io/webappsec-secure-contexts/)后，我发现了一个问题——安全上下文允许浏览器信任`file:` URL，因为这样“方便开发人员在公开部署之前构建应用程序”。

我想知道Safari如何实现这个例外情况，所以我开始搜索究竟是什么让`file:` URL如此特殊。围绕该协议的同源策略规则已经引起的[激烈的争论](https://books.google.com/books?id=NU3wOk2jzWsC&amp;pg=PA160)，而且这类URL的源是[由浏览器决定](https://developer.mozilla.org/en-US/docs/Web/API/URL/origin)的，Safari为[每个文件提供了不同的不透明源](https://groups.google.com/a/chromium.org/forum/#!topic/blink-dev/0w5mxLMkrNM)。经过实验，我发现Safari认为**所有**具有不透明源的文件都具有安全上下文（这是第七个漏洞，CVE-2020-3865）。这是个很大的问题，因为HTTP站点可以很容易就创建一个具有不透明源的文档，例如使用[具有sandbox属性的iframe标签](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe)：

```
&lt;iframe src="/" sandbox&gt;&lt;/iframe&gt;
```

唯一的问题就是，规范中规定，“要使网页具有安全上下文，必须确保安全传输该页面及其**父页面和创建页面链**中的所有页面“。这就意味着嵌入HTTP网站中的具有不透明源的文档总是被认为是不安全的。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fd0fd42da104db66.png)

幸运的是，Safari好像忽略了规范中关于”创建页面链“的部分，而只检查了父页面的安全性，这样我们只需从沙箱化的iframe中打开一个弹窗，即可创建一个具有安全上下文的窗口。

```
&lt;iframe srcdoc="&lt;script&gt;open('/')&lt;/script&gt;" sandbox="allow-scripts allow-popups"&gt;&lt;/iframe&gt;
```

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015dbf0c78b1aa35f8.png)

**注：对于中间人攻击者来说，还有一种更简单的方法让HTTP网站具有不透明源，只需要在响应的CSP中加入[sandbox选项](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/sandbox)即可。**

但是这项技术对于我们上面创建的`blob:skype.com`页面有什么帮助呢？事实上，没什么帮助。这个URL是伪造的，无法通过网络进行传输，它只是我们使用`history.pushState`和”空白“源创造的一个弗兰肯斯坦式怪兽。从沙箱化iframe中弹窗的技巧并不适用于这个怪兽，因为在执行`window.open('/')`后，Safari会试图加载`blob://skype.com`，但我们都知道，这个页面并不存在。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014a3257700885d06a.png)

所以我们要使用其他方法打开弹窗，该弹窗1）URI为`blob://skype.com`，2）具有不透明源，3）可以执行任意Javascript，而且该方法不会让Safari真正加载任何内容。

我记得在阅读[Broken Browser](http://www.brokenbrowser.com/sop-bypass-abusing-read-protocol/)时，其中提到，如果在会[继承源](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)(inherited origin)的文档中执行`document.write()`，Edge会不知道如何处理。我在Safari中试验了这一技巧。

事实证明，在Safari中，如果文档在其继承源的文档中执行了`document.write()`的话，该文档的`location.href`会发生扩散。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0113a941ff5b88af09.png)

这样的话就实现了我们上面对弹窗的第一点和第三点要求：URI为`blob://skype.com`以及任意Javascript执行。现在我们只需要让弹窗具有不透明源。

回顾一下我们目前的状况：

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0172d35e090446fecd.png)

问题在于，只有当弹窗具有相同源(同源策略)时才可以执行`document.write()`，所以我们需要找到一种方法，在执行完`document.write()`后，再将源设置为null。

我的计划是这样的：从具有”空白“源的`blob://skype.com`开始，创建一个包含`about:blank`的常规iframe，之后执行`document.write()`，使得该iframe的`href`变为`blob://skype.com`，然后将sandbox属性**动态**加到iframe上，最后使用上面提到的沙箱化iframe弹窗技巧，如果过程正确，`href`的`blob://skype.com`值应该会从父页面传递到iframe，再传递到弹窗中。

但是这个计划还有一个问题，iframe[规范](https://html.spec.whatwg.org/multipage/iframe-embed-object.html)中说，只有在iframe中的页面重新导航后，动态添加的sandbox属性才会生效。

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018d53aac19c92a236.png)

这个问题很难处理，因为我们的URL是伪造的，任何的框架导航操作都会让Safari重新抓取并加载资源，即使像是`location.reload()`这样的操作都会让Safari意识到当前页面的URL是伪造的，并返回错误信息。

所以我们需要想到一种方法，在不用Safari改变URL或网页内容的情况下，强制框架进行导航。

然后我想到了一种情况，如果导航因为某些不可控的原因失败了呢？如果Safari确实尝试进行了抓取和加载，但就是无法完成呢？我们是不是可以将iframe导航到一个真实的URL上，但是在响应中包含[`X-Frame-Options`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options)头，使导航失败。

```
document.getElementById('theiframe').contentWindow.location = 'https://google.com';

&gt; Refused to display 'https://www.google.com/' in a  frame because it set 'X-Frame-Options' to 'SAMEORIGIN'.
```

果然，这样也算是一次真实的框架导航。动态添加的sandbox属性生效了，但是iframe的URL和内容都没有变化。

```
document.getElementById('theiframe').contentDocument

&gt; Sandbox access violation: Blocked a frame at "://" from accessing a frame at "null".
```

现在我们有了一个沙箱化的iframe，其`href`值为`blob://skype.com`，且可以执行任意Javascript，现在只剩下最后一步，用`window.open()`弹出一个窗口。BugPoC上的演示文件：[bugpoc.com/poc#bp-2ONzjAW6](https://bugpoc.com/poc#bp-2ONzjAW6)，密码是blatantAnt90，注意该演示只在Safari 13.0.4下有效。

**注：可以在这里使用[BugPoC Mock Endpoint](https://bugpoc.com/testers/other)功能，模拟`X-Frame-Options`端点的功能。**

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018aa45ea4b031c03c.png)



## 九、技术总结及演示

至此，漏洞挖掘结束，我们从一个普通的HTTP网站开始，最终拥有了一个在安全上下文中的blob URI。下面对攻击发生过程进行一个总结：
1. 打开有害的**HTTP网站**；
<li>
**HTTP网站**变成一个`data:` URI;</li>
1. 使用”空白“源将`data:` URI变成`blob:` URI；
1. 修改`window.history`（分两个步骤）；
1. 创建一个包含`about:blank`的iframe，向其中执行`document.write`;
1. 为iframe动态添加sandbox标签；
1. 使用`X-Frame-Options`进行一次失败的框架导航；
1. 在iframe中执行`window.open`，打开一个弹窗，向其中执行`document.write`。
1. 结束
我们可以在第8步的弹窗中使用[`mediaDevices`](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices) Web API访问（前/后）摄像头、麦克风、屏幕共享（仅限于macOS）等资源。下面是最终的流程图：

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0190c23b39a0c03877.png)

下面是在现实中执行该攻击的录屏：

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://static.wixstatic.com/media/149864_b6a9268cffe34047a4797c88068e7669~mv2_d_1736_1380_s_2.gif)

[![](./img/202511/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://static.wixstatic.com/media/149864_f088f74e64334c199a9dd4738555ffbc~mv2.gif)

BugPoC上的演示文件：[bugpoc.com/poc#bp-HHAQuUYC](https://bugpoc.com/poc#bp-HHAQuUYC)，密码是blahWrasse59，注意该演示只在Safari 13.0.4下有效。
