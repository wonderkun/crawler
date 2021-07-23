> 原文链接: https://www.anquanke.com//post/id/176884 


# JavaScript 原型链污染


                                阅读量   
                                **284096**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01c4169cb3c2780454.png)](https://p4.ssl.qhimg.com/t01c4169cb3c2780454.png)



## 0x01 前言

最近看到一篇原型链污染的文章，自己在这里总结一下



## 0x02 javascript 原型链

js在ECS6之前没有类的概念，之前的类都是用funtion来声明的。如下

[![](https://p1.ssl.qhimg.com/t019556fd16ba65eeb5.png)](https://p1.ssl.qhimg.com/t019556fd16ba65eeb5.png)

可以看到`b`在实例化为`test对象`以后，就可以输出test类中的`属性a`了。这是为什么呢？

原因在于js中的一个重要的概念：继承。

而继承的整个过程就称为该类的原型链。

`在javascript中,每个对象的都有一个指向他的原型(prototype)的内部链接，这个原型对象又有它自己的原型，直到null为止`

```
function i()`{`
    this.a = "test1";
    this.b = "test2";`}`
```

[![](https://p2.ssl.qhimg.com/t01cd3f549f7931af2b.png)](https://p2.ssl.qhimg.com/t01cd3f549f7931af2b.png)

可以看到其父类为object，且里面还有许多函数，这就解释了为什么许多变量可以调用某些方法。

在javascript中一切皆对象，因为所有的变量，函数，数组，对象 都始于object的原型即object.prototype。同时，在js中只有类才有prototype属性，而对象却没有，对象有的是`__proto__`和类的`prototype`对应。且二者是等价的

[![](https://p0.ssl.qhimg.com/t015c638a722c8647e9.png)](https://p0.ssl.qhimg.com/t015c638a722c8647e9.png)

**当我们创建一个类时**

[![](https://p4.ssl.qhimg.com/t01b128815e74731722.png)](https://p4.ssl.qhimg.com/t01b128815e74731722.png)

原型链为

> b -&gt; a.prototype -&gt; object.prototype-&gt;null

**创建一个数组时**

[![](https://p3.ssl.qhimg.com/t01fa7b79ff6a41fc0f.png)](https://p3.ssl.qhimg.com/t01fa7b79ff6a41fc0f.png)

原型链为

> c -&gt; array.prototype -&gt; object.prototype-&gt;null

**创建一个函数时**

[![](https://p4.ssl.qhimg.com/t01b78066761d72b215.png)](https://p4.ssl.qhimg.com/t01b78066761d72b215.png)

原型链为

> d -&gt; function.prototype -&gt; object.prototype-&gt;null

**创建一个日期**

[![](https://p1.ssl.qhimg.com/t0160fae0d096488fc5.png)](https://p1.ssl.qhimg.com/t0160fae0d096488fc5.png)

原型链为

> f -&gt; Data.prototype -&gt; object.prototype-&gt;null

所以，测试之后会发现：javascript 一切皆对象，一切皆始于 `object.prototype`

### <a class="reference-link" name="%E5%8E%9F%E5%9E%8B%E9%93%BE%E5%8F%98%E9%87%8F%E7%9A%84%E6%90%9C%E7%B4%A2"></a>原型链变量的搜索

下面先看一个例子：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e25362c66a17681a.png)

我们实例要先于在`i`中添加属性，但是在`j`中也有了c属性。这是为什么呢

答：

`当要使用或输出一个变量时：首先会在本层中搜索相应的变量，如果不存在的话，就会向上搜索，即在自己的父类中搜索，当父类中也没有时，就会向祖父类搜索，直到指向null，如果此时还没有搜索到，就会返回 undefined`

所以上面的过程就很好解释了，原型链为

> j -&gt; i.prototype -&gt; object.prototype -&gt; null

所以`对象j`调用`c属性`时，本层并没有，所以向上搜索，在上一层找到了我们添加的`test3`,所以可以输出。



## prototype 原型链污染

先看一个小例子：

```
mess.js

----

(function()
`{`
    var secret = ["aaa","bbb"];
    secret.forEach();
`}`)();
```

attach.html

[![](https://p4.ssl.qhimg.com/t0156fe7a23c815fcae.png)](https://p4.ssl.qhimg.com/t0156fe7a23c815fcae.png)

结果：

[![](https://p4.ssl.qhimg.com/t014e1e98074c233ab0.png)](https://p4.ssl.qhimg.com/t014e1e98074c233ab0.png)

在mess.js中我们声明了一个数组 `secret`,然后该数组调用了属于 `Array.protottype`的`foreach`方法,如下

[![](https://p3.ssl.qhimg.com/t01147f05bd2ee7576a.png)](https://p3.ssl.qhimg.com/t01147f05bd2ee7576a.png)

但是，在调用js文件之前，js代码中将`Array.prototype.foreach`方法进行了重写，而prototype链为`secret -&gt; Array.prototype -&gt;object.prototype`,secret中无 foreach 方法，所以就会向上检索，就找到了`Array.prototype` 而其`foreach`方法已经被重写过了，所以会执行输出。

这就是原型链污染。很明显，原型链污染就是：`在我们想要利用的代码之前的赋值语句如果可控的话，我们进行 ——__proto__ 赋值，之后就可以利用代码了`



## 如何应用？

在javascript中可以通过 `test.a` or `test['a']` 对数组的元素进行访问，如下：

[![](https://p1.ssl.qhimg.com/t019d1c37681bace558.png)](https://p1.ssl.qhimg.com/t019d1c37681bace558.png)

同时对对象来说说也是一样的

[![](https://p5.ssl.qhimg.com/t01ea20328008b48ee6.png)](https://p5.ssl.qhimg.com/t01ea20328008b48ee6.png)

所以我们上述说的prototype也是一样的

[![](https://p0.ssl.qhimg.com/t01cab56668ea99390f.png)](https://p0.ssl.qhimg.com/t01cab56668ea99390f.png)

那就很明显了，原型链污染一般会出现在对象、或数组的`键名或属性名`可控,而且是赋值语句的情况下。

### <a class="reference-link" name="%E4%B8%8B%E9%9D%A2%E6%88%91%E4%BB%AC%E5%85%88%E7%9C%8B%E4%B8%80%E9%81%93%E9%A2%98%EF%BC%9Ahackit%202018"></a>下面我们先看一道题：hackit 2018

```
const express = require('express')
var hbs = require('hbs');
var bodyParser = require('body-parser');
const md5 = require('md5');
var morganBody = require('morgan-body');
const app = express();
var user = []; //empty for now

var matrix = [];
for (var i = 0; i &lt; 3; i++)`{`
    matrix[i] = [null , null, null];
`}`

function draw(mat) `{`
    var count = 0;
    for (var i = 0; i &lt; 3; i++)`{`
        for (var j = 0; j &lt; 3; j++)`{`
            if (matrix[i][j] !== null)`{`
                count += 1;
            `}`
        `}`
    `}`
    return count === 9;
`}`

app.use(express.static('public'));
app.use(bodyParser.json());
app.set('view engine', 'html');
morganBody(app);
app.engine('html', require('hbs').__express);

app.get('/', (req, res) =&gt; `{`

    for (var i = 0; i &lt; 3; i++)`{`
        matrix[i] = [null , null, null];

    `}`
    res.render('index');
`}`)


app.get('/admin', (req, res) =&gt; `{` 
    /*this is under development I guess ??*/
    console.log(user.admintoken);
    if(user.admintoken &amp;&amp; req.query.querytoken &amp;&amp; md5(user.admintoken) === req.query.querytoken)`{`
        res.send('Hey admin your flag is &lt;b&gt;flag`{`prototype_pollution_is_very_dangerous`}`&lt;/b&gt;');
    `}` 
    else `{`
        res.status(403).send('Forbidden');
    `}`    
`}`
)


app.post('/api', (req, res) =&gt; `{`
    var client = req.body;
    var winner = null;

    if (client.row &gt; 3 || client.col &gt; 3)`{`
        client.row %= 3;
        client.col %= 3;
    `}`
    matrix[client.row][client.col] = client.data;
    for(var i = 0; i &lt; 3; i++)`{`
        if (matrix[i][0] === matrix[i][1] &amp;&amp; matrix[i][1] === matrix[i][2] )`{`
            if (matrix[i][0] === 'X') `{`
                winner = 1;
            `}`
            else if(matrix[i][0] === 'O') `{`
                winner = 2;
            `}`
        `}`
        if (matrix[0][i] === matrix[1][i] &amp;&amp; matrix[1][i] === matrix[2][i])`{`
            if (matrix[0][i] === 'X') `{`
                winner = 1;
            `}`
            else if(matrix[0][i] === 'O') `{`
                winner = 2;
            `}`
        `}`
    `}`

    if (matrix[0][0] === matrix[1][1] &amp;&amp; matrix[1][1] === matrix[2][2] &amp;&amp; matrix[0][0] === 'X')`{`
        winner = 1;
    `}`
    if (matrix[0][0] === matrix[1][1] &amp;&amp; matrix[1][1] === matrix[2][2] &amp;&amp; matrix[0][0] === 'O')`{`
        winner = 2;
    `}` 

    if (matrix[0][2] === matrix[1][1] &amp;&amp; matrix[1][1] === matrix[2][0] &amp;&amp; matrix[2][0] === 'X')`{`
        winner = 1;
    `}`
    if (matrix[0][2] === matrix[1][1] &amp;&amp; matrix[1][1] === matrix[2][0] &amp;&amp; matrix[2][0] === 'O')`{`
        winner = 2;
    `}`

    if (draw(matrix) &amp;&amp; winner === null)`{`
        res.send(JSON.stringify(`{`winner: 0`}`))
    `}`
    else if (winner !== null) `{`
        res.send(JSON.stringify(`{`winner: winner`}`))
    `}`
    else `{`
        res.send(JSON.stringify(`{`winner: -1`}`))
    `}`

`}`)
app.listen(3000, () =&gt; `{`
    console.log('app listening on port 3000!')
`}`)
```

获取flag的条件是 传入的querytoken要和user数组本身的admintoken的MD5值相等，且二者都要存在。

由代码可知，全文没有对user.admintokn 进行赋值，所以理论上这个值时不存在的，但是下面有一句赋值语句：

`matrix[client.row][client.col] = client.data`

`data`,`row`,`col`，都是我们post传入的值，都是可控的。所以可以构造原型链污染，下面我们先本地测试一下。

[![](https://p0.ssl.qhimg.com/t018f2c199bb1709bab.png)](https://p0.ssl.qhimg.com/t018f2c199bb1709bab.png)

下面我们给出payload和结果

[![](https://p1.ssl.qhimg.com/t01f1e38a0e7d6c40f8.png)](https://p1.ssl.qhimg.com/t01f1e38a0e7d6c40f8.png)

`注:要使用json传值，不然会出现错误`

### <a class="reference-link" name="%E4%B8%8B%E9%9D%A2%E5%86%8D%E7%9C%8B%E5%8F%A6%E4%B8%80%E9%81%93%E9%A2%98%EF%BC%9A"></a>下面再看另一道题：

```
'use strict';

const express = require('express');
const bodyParser = require('body-parser')
const cookieParser = require('cookie-parser');
const path = require('path');


const isObject = obj =&gt; obj &amp;&amp; obj.constructor &amp;&amp; obj.constructor === Object;

function merge(a, b) `{`
    for (var attr in b) `{`
        if (isObject(a[attr]) &amp;&amp; isObject(b[attr])) `{`
            merge(a[attr], b[attr]);
        `}` else `{`
            a[attr] = b[attr];
        `}`
    `}`
    return a
`}`

function clone(a) `{`
    return merge(`{``}`, a);
`}`

// Constants
const PORT = 8080;
const HOST = '0.0.0.0';
const admin = `{``}`;

// App
const app = express();
app.use(bodyParser.json())
app.use(cookieParser());

app.use('/', express.static(path.join(__dirname, 'views')));
app.post('/signup', (req, res) =&gt; `{`
    var body = JSON.parse(JSON.stringify(req.body));
    var copybody = clone(body)
    if (copybody.name) `{`
        res.cookie('name', copybody.name).json(`{`
            "done": "cookie set"
        `}`);
    `}` else `{`
        res.json(`{`
            "error": "cookie not set"
        `}`)
    `}`
`}`);
app.get('/getFlag', (req, res) =&gt; `{`
    var аdmin = JSON.parse(JSON.stringify(req.cookies))
    if (admin.аdmin == 1) `{`
        res.send("hackim19`{``}`");
    `}` else `{`
        res.send("You are not authorized");
    `}`
`}`);
app.listen(PORT, HOST);
console.log(`Running on http://$`{`HOST`}`:$`{`PORT`}``);
```

先分析一下题目，获取flag的条件是`admin.аdmin == 1`而admin 本身是一个object，其admin 属性本身并不存在，而且还有一个敏感函数 merg

```
function merge(a, b) `{`
    for (var attr in b) `{`
        if (isObject(a[attr]) &amp;&amp; isObject(b[attr])) `{`
            merge(a[attr], b[attr]);
        `}` else `{`
            a[attr] = b[attr];
        `}`
    `}`
    return a
`}`
```

merge 函数作用是进行对象的合并，其中涉及到了对象的赋值，且键值可控，这样就可以触发原形链污染了

下面我们本地测试一下

[![](https://p2.ssl.qhimg.com/t01ca40069c07f3bc16.png)](https://p2.ssl.qhimg.com/t01ca40069c07f3bc16.png)

是undefined，为什么呢？下面我们看下

[![](https://p3.ssl.qhimg.com/t015a99e81f7d6ed181.png)](https://p3.ssl.qhimg.com/t015a99e81f7d6ed181.png)

原来我们在创建字典的时候，`__proto__`,不是作为一个键名，而是已经作为`__proto__`给其父类进行赋值了，所以在`test.__proto__`中才有admin属性，但是我们是想让`__proto__`作为一个键值的.

那应该怎么办呢？可以使用 JSON.parse

[![](https://p1.ssl.qhimg.com/t0143621daff1e3c7b0.png)](https://p1.ssl.qhimg.com/t0143621daff1e3c7b0.png)

> JSON.parse 会把一个json字符串 转化为 javascript的object

这样就不会在创建类的时候直接给父类赋值了

而题目中也出现了`JSON.parse`

```
var body = JSON.parse(JSON.stringify(req.body));
```

这样我们就可以愉快地进行原型链污染了

payload：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0170b8adbc3097c720.png)
