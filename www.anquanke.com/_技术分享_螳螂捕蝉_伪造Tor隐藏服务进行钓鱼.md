> 原文链接: https://www.anquanke.com//post/id/87024 


# 【技术分享】螳螂捕蝉：伪造Tor隐藏服务进行钓鱼


                                阅读量   
                                **99816**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：incoherency.co.uk
                                <br>原文地址：[http://incoherency.co.uk/blog/stories/hidden-service-phishing.html](http://incoherency.co.uk/blog/stories/hidden-service-phishing.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01208aaa3d5f7faf6c.png)](https://p2.ssl.qhimg.com/t01208aaa3d5f7faf6c.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

****

[****](https://smsprivacy.org/)**[<strong>SMS Privacy**](https://smsprivacy.org/)</strong>是我创建的一个隐私短信服务，可以作为Tor隐藏服务来使用，事实上的确有约10%的用户以这种方式来使用该服务。然而，我发现有些人伪造了我的Tor隐藏服务来创建一个钓鱼网站，在本文中，我会与读者分享我发现的一些细节。



**二、概述**

某一天，[Charlie](https://charlie.ht/)正在网上随便逛逛，突然，他发现使用谷歌搜索“site:*.onion.to smsprivacy”会得到一些意想不到的结果。

**smspriv6fynj23u6.onion**是合法的隐藏服务名，然而，搜索页面中出现了另一个结果：**smsprivyevs6xn6z.onion**，对应的站点看起来一模一样。

经过简单调研后，我们发现这个网站是一个简单的代理网站，即：所有发往该钓鱼站点的页面请求都会被转发到真实的隐藏服务上，并会返回收到的响应数据，只有几个特殊之处除外：

**1、头部中缺失Content-Length字段。**

HTTP客户端可以根据Content-Length头了解待传输内容的字节数。如果代理服务器不对响应数据进行修改，那么它可以保持Content-Length头不变，直接传递这个字段，因为代理服务器知道如果内容不发生改变的话，其数据长度也不会发生变化。

然而，这个代理服务器认为响应内容会发生改变，这意味着**服务器准备在某些情况下修改响应内容**。

既然如此，它为什么不修改Content-Length字段，使其对应修改后的内容长度呢？

可能是代理服务器想减少页面加载时间：如果代理服务器不需要预先了解长度值，那么它就可以在收到响应内容后以数据流方式直接发送给客户端，在发送过程中修改数据。如果代理服务器需要读取所有内容，再进行修改，然后再发送所有数据，那么有可能会增加页面加载时间，引起用户怀疑。

可能代理服务器作者无法接受存储所有内容所需的高内存负载。如果同一个服务器正在代理数十个至数百个其他隐藏服务，那么采用这种方案也是可以理解的。

**2、头部中Connection字段错误。**

合法站点与钓鱼站点的响应头对比如下所示。

合法站点：



```
$ torsocks curl -I http://smspriv6fynj23u6.onion/
HTTP/1.1 200 OK
Server: nginx/1.10.2
Date: Fri, 13 Oct 2017 05:37:49 GMT
Content-Type: text/html;charset=UTF-8
Content-Length: 7387
Connection: keep-alive
Set-Cookie: [...]
X-Frame-Options: DENY
```

钓鱼站点：



```
$ torsocks curl -I http://smsprivyevs6xn6z.onion/
HTTP/1.1 200 OK
Server: nginx/1.10.2
Date: Fri, 13 Oct 2017 05:37:57 GMT
Content-Type: text/html;charset=UTF-8
Connection: [object Object]
Set-Cookie: [...]
X-Frame-Options: DENY
```

头部中Connection字段由keep-alive变成了[object Object]。**当你使用javascript语言，将某个对象转化为字符串时，如果该对象没有实现toString()方法，就会得到这个结果。这个线索非常重要，可以告诉我们代理服务器正在运行的软件类型。**

代理服务器很有可能使用的是NodeJS。我无法在node-http-proxy或者Harmon上复现这个bug（Harmon是node-http-proxy的中间件，用来修改响应数据）。很有可能代理服务器使用了自定义的解决方案。如果有人知道什么软件会有bug导致Connection头变为[object Object]，请及时告诉我。

**3、代理服务器会缓存某些非预期的javascript文件（可能会有其他文件被缓存下来）。**

我添加了一些Javascript，以检测页面是否运行在某个流氓域名上，如果的确如此，脚本会把**document.referrer**信息POST给我，以便后续分析。我发现使用合法网站时，浏览器会修改我使用的脚本，然而，使用钓鱼网站时，我会得到一个过时的版本，据此，我判断钓鱼站点使用了某些额外的缓存机制。这样做可能也是为了减少页面加载时间。

在写这篇文章时，我尝试着调查这种缓存机制，然后发现了更为有趣的一些信息。代理服务器会丢弃掉跟踪脚本获得的所有内容，因此我无法获取这些信息。重命名脚本并稍加修改内容后，我解决了这个问题，但我实在不想玩这种猫捉老鼠的游戏。这种情况至少意味着有人正在积极维护这个代理服务，及时采取措施保持服务正常运行。

**4、隐藏服务地址被修改。**

代理服务器似乎会重写**smspriv6fynj23u6.onion**的所有实例，将其改为**smsprivyevs6xn6z.onion**。尽管如此，它对大写的地址不会采用相同操作。

**5、比特币地址被修改。**

这是钓鱼站点的真正目的。通常情况下，钓鱼网站会窃取用户凭据，以便后续使用或者出售这些信息，但这个站点采用的方法更加直接，它将原始的比特币地址修改成攻击者可以控制的地址。

当首次重定向到支付页面时，在页面加载之前用户能感受到一段延迟，大概是因为代理服务器后台正在生成一个新的比特币地址（这个操作需要一段时间，意味着该地址正被插入一个缺少索引的规模巨大的数据库，或者该地址由速度较慢的机器生成而得，或者攻击者使用速度较慢的代码语言来生成这个地址。如果是后面这种情况，这有可能表明RNG（随机数生成器）本身也不安全）。所有以文本形式表示的比特币地址都会被重写为攻击者可控的地址，合法地址与伪造地址之间实现了一一映射关系。值得注意的是，二维码（QR）保持不变，仍然对应原始的合法地址。

我向伪造的地址（**1GM6Awv28kSfzak2Y7Pj1NRdWiXshMwdGW**）发起了一条支付请求，想看看会发生什么事情。这个信息并不会出现在网站上，更加确定了这是个静默代理站点。目前这笔钱还没被使用，但一旦被使用，我们可能会观察到一些有趣的信息。

<br>

**三、伪造站点如何分发给用户**

当用户在未知域上查看站点时，Javascript会把referrer信息POST到服务器上，我看到了一些不同的返回结果。大多数情况下，这些信息都源自于人们使用web代理（如onion.link）来查看隐藏服务，然而，我发现了两个比较特殊的隐藏服务：

7cbqhjnpcgixggts.onion：“The onion crate”：这是Tor隐藏服务的列表。与远古的“Web网站清单”类似，但专为Tor设计，其上钓鱼站点被突出标记为“钓鱼链接”（然而reddit上有人指出"The onion crate"这个服务本身就是钓鱼链接）

hss3uro2hsxfogfq.onion：“not Evil”：这是个搜索引擎服务，用来搜索Tor隐藏服务。搜索“sms privacy”时，合法站点排在第一位，钓鱼站点排在第二位。我点击了钓鱼站点旁的“滥用情况报告（report abuse）”按钮，然而目前搜索结果还没有将其删除。

这并没有给出我想要的结果。我希望找到某人仿造的推特、博客或者类似信息。“The onion crate”的后台负责人不太可能负责维护这个钓鱼站点。因为如果我希望人们使用我的钓鱼站点，那么该站点就不会被标记为“钓鱼链接”。负责维护“not Evil”搜索引擎的人有可能是肇事者，虽然这种情况也不大符合实际。如果我正在维护某个搜索引擎，目的是向用户推送钓鱼链接，那么我根本不会将正常链接包括在搜索结果中，更何况将其排在第一位。

很有可能真正的钓鱼攻击正准备实施，“The onion crate”于2017-05-17将钓鱼链接标记出来，表明这个钓鱼网站已经存活了一段时间。



**四、谁是肇事者**

最有可能的结果是，某个普普通通的网络犯罪分子写了个代理服务器，将比特币地址替换为自己的地址，为各种合法的隐藏服务生成了许多伪造的隐藏服务，然后坐等金钱滚滚流入他的钱包。

起初我认为是情报部门希望监控隐私短信用户，然而，如果是这种情况，他们不会修改比特币地址，导致站点失效，而是希望悄悄进行监视。我猜想情报部门会将该站点设计成只监听特定的用户子集，对其他人呈现普通的钓鱼站点，但我还是认为“普普通通的网络犯罪分子”这种可能性最大。

与传统网站的钓鱼相比，伪造隐藏服务进行钓鱼要容易得多，这是因为想要定位隐藏服务的服务器本身就不是件容易的事（这也是隐藏服务的设计理念），隐藏服务没有集中管控的命名系统，这意味着即便是合法的站点，其地址中也会包含随机字符。想要获得伪造的地址也比较容易。随后，即便伪造的钓鱼网站被发现，也没有人能够撤销攻击者的域名或者关闭掉托管的页面。这是完美的犯罪行为，唯一的缺点就是，与普通站点相比，隐藏服务站点的目标用户群体的技术水平往往更高，因此不是那么好欺骗。



**五、用户如何保护自己**

****

SMS Privacy的客户应该确保他们使用HTTPS方式浏览smsprivacy.org，如果使用Tor的话，请核实使用的隐藏服务名为唯一正确的smspriv6fynj23u6.onion。除此之外，其他访问方式几乎肯定会带来安全风险。



**六、是否有用户受到影响**

我尚未收到用户发来的电子邮件，抱怨他们的支付情况出现异常（当然实际情况并非如此，然而每种出错情况最终都归根于我自己犯的错误，与用户不小心浏览钓鱼网站无关）。因此，我想说的是目前没有用户受到影响，或者至少没有大量用户受到影响。



**七、后续调查**

我猜测运行这个代理的软件也同时正在代理其他许多隐藏服务。如果你想写些代码来代理隐藏服务，你只需要将域名改成自己的域名，将比特币地址改成自己的地址，整个过程差不多就搞定了。你可以将代理服务放置在许多上游隐藏服务的前端，这几乎不需要消耗额外的精力及资源，所以，如果攻击者没有这么做我反而会感到奇怪。

事实上，如果我们能找到另一个Tor隐藏服务钓鱼站点，他们共享相同的特征（即Connection: [object Object]、缺失Content-Length字段、重写小写的隐藏服务地址、首次呈现比特币地址时会有延迟以及访问未知主机名时返回500响应代码），那么我们也能发现一些有趣的结论。

此外，如果我们探测该网站的漏洞，看看是否能找到所代理的隐藏服务的完整列表，那么也会非常有趣。攻击者很有可能在代理代码中实现主机名选择功能，也就是说请求不同的钓鱼站点可能会返回其他钓鱼站点的内容。如果出现这种结果，就可以更加确信这些代理站点运行在同一台主机上。



**八、总结**

发现有人正在积极从事这项活动是非常有趣的一件事情，只要稍作思考，我们可知大范围部署这种方案非常容易：只需一个周末的时间，攻击者就能搭建起基本的工作环境。如果未来有大量隐藏服务的钓鱼网站出现，我并不会感到惊讶。



**九、2017-10-13更新**

在这篇文章发表之后，我根据“后续调查”中的建议做了些调研。我在“The onion crate”中查找其他钓鱼链接，发现某个网站会在响应头中包含Connection: [object Object]信息，也会传递伪造的SMS Privacy隐藏服务地址。调查结果表明，这个毫不相关的隐藏服务同样给出了伪造的SMS Privacy内容！这表明这两个站点很有可能托管在同一台主机上，由同一个操作者（或者组织）进行维护，这一切证实了这个系统的规模非常庞大：



```
$ torsocks curl -I -H 'Host: smsprivyevs6xn6z.onion' http://cboc66yz75virnj7.onion
HTTP/1.1 200 OK
Server: nginx/1.10.2
Date: Fri, 13 Oct 2017 16:26:10 GMT
Content-Type: text/html;charset=UTF-8
Connection: [object Object]
Set-Cookie: mojolicious=eyJsYW5kaW5nX3VybCI6Ii8iLCJhYnRlc3RzIjp7ImxhbmRpbmdfdXJsIjoiLyIsInNpZ251cGxpbmsiOiJvcmlnaW5hbCIsInJlZmVyX3NyYyI6Im5vbmUiLCJoaWRkZW5fc2VydmljZSI6ImhpZGRlbiJ9LCJleHBpcmVzIjoxNTA3OTE1NzE1LCJjc3JmX3Rva2VuIjoiZmQzNjc4NzcyMjRiNDZkZWZhYjNhM2ViZDIwMDY0ZmRmMDliZmQ0NCIsImFidGVzdHNfc2Vzc2lvbmlkIjoiOGM4NWQxMTZjMmE1MTBkOSJ9--785fbe83dce1217e74543ed831eb4c18c1cd6105; expires=Fri, 13 Oct 2017 17:28:35 GMT; path=/; HttpOnly
X-Frame-Options: DENY
```


