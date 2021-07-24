> 原文链接: https://www.anquanke.com//post/id/197614 


# 一道有趣的XSS-Challenge


                                阅读量   
                                **910717**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01dde367b428ce05ae.png)](https://p1.ssl.qhimg.com/t01dde367b428ce05ae.png)



早上刷某特时推送了三上悠ya的动态，猛点双击后却发现是pwnfunction更新了一道xss-challenge的wp(上当了上当了)。看了下题目难度是hard，质量很高，考点也很有趣。官方wp的payload和解题思路看起来不是很复杂，实际上还是隐藏了很多知识点，如果大家复现这个题目，希望这篇文章能够对你有帮助。



## 题目信息

题目名称:WW<br>
题目难度:Hard<br>
题目地址:[https://xss.pwnfunction.com/challenges/ww3/](https://xss.pwnfunction.com/challenges/ww3/)<br>
思路:bypass DOMPurify+DOM clobbering

可控的输入的点有两个`text`，`img`

```
let text = new URL(location).searchParams.get('text')
let img = new URL(location).searchParams.get('img')
```

`img`作为img标签的src属性被写入，且被过滤了关键符号。

```
&lt;img class="circle" src="$`{`escape(img)`}`" onload="memeGen(this, notify)"&gt;

const escape = (dirty) =&gt; unescape(dirty).replace(/[&lt;&gt;'"=]/g, '');
```

`text`作为文本被渲染，渲染前都经过一次DOMPurify.sanitize处理

```
//part1
document.write(
...
Creating meme... ($`{`DOMPurify.sanitize(text)`}`)
)

//part2 
html = (`&lt;div class="alert alert-warning" role="alert"&gt;&lt;b&gt;Meme&lt;/b&gt; created from $`{`DOMPurify.sanitize(text)`}`&lt;/div&gt;`)

notify ? ($('#notify').html(html)) : ''
```



## DOMpurify bypass via Jquery.html()

乍一看经过`DOMPurify`后的这些交互点都很安全，但是使用`html()`解析会存在标签逃逸问题。

题目作者在wp中提到了两种解析html的方式:**jquery.html&amp;innerhtml**。`innerHTML`是原生js的写法，`Jqury.html()`也是调用原生的innerHTML方法，但是加了自己的解析规则(后文介绍)。

关于两种方式:`Jquery.html()`和`innerHTMl`的区别我们用示例来看。

对于innerHTML：模拟浏览器自动补全标签，不处理非法标签。同时，`&lt;style&gt;`标签中不允许存在子标签(style标签最初的设计理念就不能用来放子标签)，如果存在会被当作text解析。因此`&lt;style&gt;&lt;style/&gt;&lt;script&gt;alert(1337)//`会被渲染如下

```
&lt;style&gt;
    &lt;style/&gt;&lt;script&gt;alert(1337)//
&lt;/style&gt;
```

对于`Jqury.html()`，最终对标签的处理是在`htmlPrefilter()`中实现:[jquery-src](https://github.com/jquery/jquery/blob/d0ce00cdfa680f1f0c38460bc51ea14079ae8b07/src/manipulation.js)，其后再进行原生innerHTML的调用来加载到页面。

```
rxhtmlTag = /&lt;(?!area|br|col|embed|hr|img|input|link|meta|param)(([a-z][^/&gt;x20trnf]*)[^&gt;]*)/&gt;/gi
/&lt;(?!area|br|col|embed|hr|img|input|link|meta|param)(([a-z][^/&gt;x20trnf]*)[^&gt;]*)/&gt;/gi


jQuery.extend( `{`
    htmlPrefilter: function( html ) `{`
        return html.replace( rxhtmlTag, "&lt;$1&gt;&lt;/$2&gt;" );
    `}`
    ...
`}`)

tmp.innerHTML = wrap[ 1 ] + jQuery.htmlPrefilter( elem ) + wrap[ 2 ];
```

有意思的是，这个正则表达式在匹配`&lt;*/&gt;`之后会重新生成一对标签(区别于直接调用innerHTML)

[![](https://p0.ssl.qhimg.com/t0161eda8a9349f255c.png)](https://p0.ssl.qhimg.com/t0161eda8a9349f255c.png)

所以相同的语句`&lt;style&gt;&lt;style/&gt;&lt;script&gt;alert(1337)//`则会被解析成如下形式，成功逃逸`&lt;script&gt;`标签。

```
&lt;style&gt;
    &lt;style&gt;
&lt;/style&gt;
&lt;script&gt;alert(1337)//

```

[![](https://p3.ssl.qhimg.com/t012d8eb81dab70637c.png)](https://p3.ssl.qhimg.com/t012d8eb81dab70637c.png)

我们知道DOMPurify的工作机制是将传入的payload分配给元素的innerHtml属性，让浏览器解释它(但不执行)，然后对潜在的XSS进行清理。由于DOMPurify在对其进行`innerHtml`处理时，`script`标签被当作`style`标签的text处理了，所以DOMPurify不会进行清洗(因为认为这是无害的payload)，但在其后进入html()时，这个无害payload就能逃逸出来一个有害的`script`标签从而xss。



## DOM-clobbering

第二个考点是要覆盖变量`notify`，只有在notify不为false的时候才能顺利进入html()方法

```
let notify = false;

document.write(`&lt;img class="circle" src="$`{`escape(img)`}`" onload="memeGen(this, notify)"&gt;`)

const memeGen = (that, notify) =&gt; `{`
        if (notify) `{`
                html = (`$`{`DOMPurify.sanitize(text)`}``)
            `}`
        ...
        $('#notify').html(html)
`}`
```

首先尝试用DOM-clobbering创造一个id为`notify`的变量，但是这种方式不允许覆盖已经存在的变量。

```
&lt;html&gt;
&lt;img id=notify&gt;
&lt;img src="" onerror="memeGen(notify)"&gt;

&lt;script&gt;
const memeGen = (notify) =&gt;`{`
    consol.log(notify);  //false
`}`

let notify = false;
&lt;/script&gt;
&lt;/html&gt;
```

不过我们依然可以借助标签的name属性值，为document对象创造一个变量`document.notify`，熟悉dom-clobbing的都很了解这种方式也常用来覆盖`document`的各种属性/方法。然而这道题不需要覆盖什么，我们就先把它当作一种创造变量的手段，后文再讲。我们先看简单了解一下JS的作用域



## JS作用域&amp;作用域链

在JS的函数中，一个变量是否可访问要看它的作用域(scope)，变量的作用域有全局作用域和局部作用域(函数作用域)两种，关于详细的介绍可以移步之前博客的小记：[深入Javascript-作用域&amp;Scope Chain](https://hpdoger.cn/2020/01/20/%E6%B7%B1%E5%85%A5Javascript-%E4%BD%9C%E7%94%A8%E5%9F%9F&amp;Scope%20Chain/)，这里举个最简单的例子如下

```
function init() `{`
    var inVariable = "local";
`}`
init();
console.log(inVariable); //Uncaught ReferenceError: inVariable is not defined
```

这就是因为函数内部用`var`声明的`inVariaiable`属于局部作用域范畴，在全局作用域没有声明。我们可以这样理解：作用域就是一个独立的地盘，让变量不会外泄、暴露出去。也就是说作用域最大的用处就是隔离变量，不同作用域下同名变量不会有冲突

在寻找一个变量可访问性时根据作用域链来查找的，作用域链中的下一个变量对象来自包含（外部）环境，而再下一个变量对象则来自下一个包含环境。这样，一直延续到全局执行环境；全局执行环境的变量对象始终都是作用域链中的最后一个对象。

而在Javascript event handler(时间处理程序)中，也就是onxx事件中(这块地盘)，scope chain的调用就比较有意思了。它会先去判断当前的scope是否有局部变量`notify`，若不存在向上查找`window.document.notify`，仍不存在继续向上到全局执行环境即`window.notify`为止。

这样说起来可能有点绕，我们来看下面这个例子就明白了

```
&lt;img src="" onerror="console.log(nickname)"&gt; //pig
&lt;img src="" onerror="var nickname='dog';console.log(nickname)"&gt; //dog

&lt;script&gt;
window.document.nickname = 'pig';
window.nickname = 'cat';
&lt;script&gt;

```

打印的结果分别为`pig`和`dog`。原因就是在第二个img标签中，onerror的上下文存在局部作用域的nickname变量，不用再向上查找了。

同时注意到题目触发`memeGen`函数的方式也恰好是写在event handler中—即`onload`内。所以污染了`document.notify`就相当于污染了将要传递的实参`notify`，这也就是为什么需要之前的dom-clobbing。

```
&lt;img class="circle" src=url onload="memeGen(this, notify)"&gt;
```



## 思路线&amp;题外话

**dom clobbing新建一个document.notify-&gt;onload-&gt;bypass D0MPurify via html()=&gt;XSS**

另外，我们前文提到在event handler的作用域中scope chain是:局部变量-&gt;document-&gt;global。

但是在普通的局部作用域内，scope chain **没有** document这一链，而是`局部作用域变量-&gt;global`，示例如下

```
&lt;script&gt;
window.document.nickname = 'pig';
window.nickname = 'cat';
let nickname = 'dog';

function echoNameA(nickname)`{`
    console.log(nickname); // dog
`}`

window.realname = 'me';
window.document.realname = 'hpdoger';

function echoNameB()`{`
    console.log(realname); //me
`}`

echoNameA(nickname);
echoNameB(realname);
&lt;/script&gt;
```
