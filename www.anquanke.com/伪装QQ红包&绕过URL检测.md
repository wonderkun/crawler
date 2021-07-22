> 原文链接: https://www.anquanke.com//post/id/82466 


# 伪装QQ红包&amp;绕过URL检测


                                阅读量   
                                **147326**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0149cd4dc670946d8c.png)](https://p5.ssl.qhimg.com/t0149cd4dc670946d8c.png)

**一、绕过PC端恶意URL提示**

“腾讯外部漏洞报告处理流程”中提到了一个越权的url检测网址[http://www.qq.com_521_qq_diao_yu_wangzhan_789.com/ ](http://www.qq.com_521_qq_diao_yu_wangzhan_789.com/)直接发出来的话肯定是提示恶意链接的。

[![](http://p4.qhimg.com/t014bb7e42d0b08b3e8.png)](http://p4.qhimg.com/t014bb7e42d0b08b3e8.png)

(其实可以手机QQ是无法正常识别出这个url的,所以希望能够改进一下手机客户端的URL识别。)

并且是无法直接打开的,只能复制url。

直接用QQ浏览器的手机采用打开,刚开始是提示恶意链接,不用管,然后点击分享

[![](http://p4.qhimg.com/t017beff92e8ae1594e.png)](http://p4.qhimg.com/t017beff92e8ae1594e.png)

[![](http://p0.qhimg.com/t01c146bda767f17858.png)](http://p0.qhimg.com/t01c146bda767f17858.png)

分享给QQ好友以后,手机还有PC上分别显示为

PC:

[![](http://p0.qhimg.com/t01197333bb112a8b27.png)](http://p0.qhimg.com/t01197333bb112a8b27.png)

手机QQ:

[![](http://p5.qhimg.com/t015f15be227614c2ca.png)](http://p5.qhimg.com/t015f15be227614c2ca.png)

PC端已经不再红色恶意链接提示了。可直接打开url。

此时测试结果:

PC端QQ URL检测:绕过

手端QQ URL检测:提示

欺骗性:弱

<br>

**二、伪装“红包”**

只是这种绕过恶意url检测,是没有多大意义的,毕竟很多用户又不傻,不会去点击类似这种:

[![](http://p8.qhimg.com/t01197333bb112a8b27.png)](http://p8.qhimg.com/t01197333bb112a8b27.png)

的链接的。下面就去改进一下,首先我们需要一个被腾讯报恶意链接并且可控的网站。(毕竟钓鱼网站都是可控的):

[http://www.bzxlcj.com/](http://www.bzxlcj.com/)

添加一个test.html

```
&lt;html&gt;
&lt;head&gt;
&lt;meta itemprop="name" content="发红包啦!"&gt;
&lt;meta itemprop="image"   content="https://mqq-imgcache.gtimg.cn/res/mqq/hongbao/img/message_logo_100.png"&gt;  
&lt;meta name="description"   itemprop="description" content="赶紧点击拆开吧!"&gt;
&lt;meta http-equiv="Content-Language"   content="zh-CN"&gt;
&lt;meta HTTP-EQUIV="Content-Type"   CONTENT="text/html; charset=gb2312"&gt;
&lt;title&gt;&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
钓鱼网站
&lt;/body&gt;
&lt;/html&gt;
```

这时候发出来还是会报恶意url

还是用手机QQ打开(会有恶意提示)

[![](http://p0.qhimg.com/t01c728de2ad56889f6.png)](http://p0.qhimg.com/t01c728de2ad56889f6.png)

,并且分享给QQ好友。

[![](http://p7.qhimg.com/t0120183215ee09af67.png)](http://p7.qhimg.com/t0120183215ee09af67.png)

[![](http://p1.qhimg.com/t01ce2f8296a67d237e.png)](http://p1.qhimg.com/t01ce2f8296a67d237e.png)

(经过测试,发现这个拉取摘要的过程并不是在本地进行的。)

PC端还有手机QQ端分别显示为

PC:

[![](http://p2.qhimg.com/t01a8ed808496d6520b.png)](http://p2.qhimg.com/t01a8ed808496d6520b.png)

手机QQ:

[![](http://p5.qhimg.com/t01be3ecd2b53a11168.png)](http://p5.qhimg.com/t01be3ecd2b53a11168.png)

这样就可以达到欺骗用户的目的了。

此时测试结果:

PC端QQ URL检测:绕过

手端QQ URL检测:提示

欺骗性:中

<br>

**三、绕过手机端QQ恶意url检测**

其实一二两种情况只能绕过PC端,局限性非常大!下面来绕过手机端的恶意url检测。

当手机QQ打开一个连接的时候

[http://111.161.83.162/cgi-bin/httpconn?htcmd=0x6ff0080&amp;u=http%3A%2F%2Fwww.bzxlcj.com%2Ftest.html](http://111.161.83.162/cgi-bin/httpconn?htcmd=0x6ff0080&amp;u=http%3A%2F%2Fwww.bzxlcj.com%2Ftest.html)

[![](http://p1.qhimg.com/t01ee52f3fdab4aaa71.png)](http://p1.qhimg.com/t01ee52f3fdab4aaa71.png)

这是一个url跳转链接,类似的还有很多,之前有人在wooyun上报过此类的url跳转,腾讯之所以不认为是漏洞,是因为这种跳转会对url进行恶意url检测,一旦发现是恶意的url,那么将会自动进行屏蔽!

所以我们想要绕过就很简单,就是绕过这个url检测机制即可。

首先把[http://www.bzxlcj.com/test.html](http://www.bzxlcj.com/test.html)转换成短域名

[http://t.cn/RyGbYXw](http://t.cn/RyGbYXw)

当我直接给好友发送短域名的时候,是这么显示的

PC:

[![](http://p0.qhimg.com/t01fa01e3383ee91e7a.png)](http://p0.qhimg.com/t01fa01e3383ee91e7a.png)

手机QQ:

[![](http://p8.qhimg.com/t013321146f901d6719.png)](http://p8.qhimg.com/t013321146f901d6719.png)

这个时候打开已经无提示了。

有人说,这不就是一个普通的跳转么?怎么能算一个漏洞?可以看到手机是直接解析短域名的302跳转,去读取概要的。既然已经可以进行跳转了,并且读取出概要解析成链接形式了,为什么不再进行一次检测呢?漏洞的关键就出在这里!

当然这样有一个弊端,就是电脑是不显示红包效果的。只是一个跳转链接。

我们可以这么解决,

1.随便找个好友发送信息[http://t.cn/RyGbYXw](http://t.cn/RyGbYXw)

2.断网,打开网址,并且稍等知道出现无法连接。此时网站是不进行跳转的。

3.连网,点击分享给好友。

这个时候转发出来,就是完美的过手机+PC恶意url检测机制,并且伪装红包。

手机端:

[![](http://p1.qhimg.com/t01888172c7f88619d6.png)](http://p1.qhimg.com/t01888172c7f88619d6.png)

[![](http://p0.qhimg.com/t0116262c2a6362cc02.png)](http://p0.qhimg.com/t0116262c2a6362cc02.png)

PC端:

[![](http://p2.qhimg.com/t0100b6890f8504d8e7.png)](http://p2.qhimg.com/t0100b6890f8504d8e7.png)

[![](http://p1.qhimg.com/t013d828d383928c81e.png)](http://p1.qhimg.com/t013d828d383928c81e.png)

PC端QQ URL检测:绕过

手端QQ URL检测:绕过

欺骗性:中

最终版:修改PC端角标&amp;一键生成

还有两个问题:

1.右下角有QQ浏览器字样

2.太TM麻烦了!

有没有简单一键生成的!,并且左下角显示QQ红包的啊!?

有!

一键生成版:

[http://connect.qq.com/widget/shareqq/index.html?url=http%3A%2F%2Fmtfly.net&amp;desc=&amp;title=%E5%8F%91%E7%BA%A2%E5%8C%85%E5%95%A6%EF%BC%81&amp;summary=%E8%B5%B6%E7%B4%A7%E7%82%B9%E5%87%BB%E6%8B%86%E5%BC%80%E5%90%A7%EF%BC%81&amp;pics=http%3A%2F%2Fmqq-imgcache.gtimg.cn%2Fres%2Fmqq%2Fhongbao%2Fimg%2Fmessage_logo_100.png&amp;flash=&amp;site=QQ%E7%BA%A2%E5%8C%85&amp;style=101&amp;width=96&amp;height=24&amp;showcount=](http://connect.qq.com/widget/shareqq/index.html?url=http%3A%2F%2Fmtfly.net&amp;desc=&amp;title=%E5%8F%91%E7%BA%A2%E5%8C%85%E5%95%A6%EF%BC%81&amp;summary=%E8%B5%B6%E7%B4%A7%E7%82%B9%E5%87%BB%E6%8B%86%E5%BC%80%E5%90%A7%EF%BC%81&amp;pics=http%3A%2F%2Fmqq-imgcache.gtimg.cn%2Fres%2Fmqq%2Fhongbao%2Fimg%2Fmessage_logo_100.png&amp;flash=&amp;site=QQ%E7%BA%A2%E5%8C%85&amp;style=101&amp;width=96&amp;height=24&amp;showcount=)

web版:

```
&lt;script type="text/javascript"&gt;
(function()`{`
var p = `{`
url:'http://mtfly.net',
desc:'',
title:'发红包啦!',
summary:'赶紧点击拆开吧!',
pics:'https://mqq-imgcache.gtimg.cn/res/mqq/hongbao/img/message_logo_100.png',
flash: '',
site:'QQ红包',
style:'101',
width:96,
height:24
`}`;
var s = [];
for(var i in p)`{`
s.push(i + '=' + encodeURIComponent(p[i]||''));
`}`
document.write(['&lt;a href="http://connect.qq.com/widget/shareqq/index.html?',s.join('&amp;'),'" target="_blank"&gt;分享到QQ&lt;/a&gt;'].join(''));
`}`)();
&lt;/script&gt;
&lt;script src="http://connect.qq.com/widget/loader/loader.js" widget="shareqq" charset="utf-8"&gt;&lt;/script&gt;
```

其实这就是腾讯的分享组件修改的。[http://connect.qq.com/intro/sharetoqq/](http://connect.qq.com/intro/sharetoqq/)

PC:

[![](http://p6.qhimg.com/t0100b6890f8504d8e7.png)](http://p6.qhimg.com/t0100b6890f8504d8e7.png)

手机:

[![](http://p9.qhimg.com/t01e3595ab95959b22b.png)](http://p9.qhimg.com/t01e3595ab95959b22b.png)

完美!

[![](http://p7.qhimg.com/t0173e176d242f4a1af.png)](http://p7.qhimg.com/t0173e176d242f4a1af.png)

PS:其实腾讯的恶意url跳转是指网站url跳转的时候的恶意url判断,比如http://111.161.83.162/cgi-bin/httpconn?htcmd=0x6ff0080&amp;u=http%3A%2F%2Fwww.bzxlcj.com%2Ftest.html

我上面的理解有些偏差吧。
