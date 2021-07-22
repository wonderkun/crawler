> 原文链接: https://www.anquanke.com//post/id/149010 


# 反序列化漏洞：在JS中利用反序列化漏洞


                                阅读量   
                                **117973**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：acunetix.com
                                <br>原文地址：[https://www.acunetix.com/blog/web-security-zone/deserialization-vulnerabilities-attacking-deserialization-in-js/](https://www.acunetix.com/blog/web-security-zone/deserialization-vulnerabilities-attacking-deserialization-in-js/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01f39e73f6d9887944.png)](https://p2.ssl.qhimg.com/t01f39e73f6d9887944.png)

在2017年的ZeroNights会议上，我做了一个关于“各种语言的反序列化漏洞”的演讲。关于我的演讲，我引用了一篇关于两个Node.js序列化包的文章。我将它们作为一个例子来展示反序列化l漏洞被攻击的过程。在这篇文章中，我将展示一下我自己的研究成果以及在JS中反序列化漏洞攻击的新方法。



## 之前的研究

上面的文章中提到的两个软件包node-serialize和serialize-to-js。它们都可以把对象序列化为JSON格式，但与标准函数（JSON.parse，JSON.stringify）不同，它们几乎允许任何类型的对象序列化，例如函数。(在JavaScript中，函数是一个对象)。所以，下面的代码是一个有用的对象。

```
var obj = `{`
field1: "value1",
field2: function()`{`
return 1;
`}`
`}`
```

但是如果我使用JSON.stringify序列化，会得到。

```
`{` field1: "value1" `}`
```

为了实现对各种对象的支持，node-serialize，内部使用eval

```
`{`"anything_here":"_$$ND_FUNC$$_function ()`{`сonsole.log(1)`}`"`}`
```

这是带有函数的序列化对象的样子。在反序列化的过程中，特殊标记ND_FUNC之后的任何内容都直接进入eval函数。因此，我们可以使用 IIFE(如文章中所述)或者直接 编写代码(如文章评论所述)。

使用IIFE(立即调用函数表达式)，我们所要做的是添加一个函数到序列化中,比如下面的第一行代码，在反序列化过程中将被定义，然后自动被调用。

```
`{`"anything_here":"$$ND_FUNC$$function ()`{`сonsole.log(1)`}`()"`}` `{`"anything_here":"$$ND_FUNC$$console.log(1)"`}`
```

下一个例子是serialize-to-js。虽然它不支持函数作为一种类型，但由于它在反序列化过程中使用了下一个构造，因此它的实现仍然不安全。

```
return (new Function('"use strict"; return ' + str))()

```

上面代码中的str可以被攻击者控制。

实际上，这只是eval的变体。我们可以使用下面的payload来实现远程命令执行，如下：

```
console.log(`exploited`)
(function ()`{`сonsole.log(1)`}`())
```



## 更安全的方式？

在ZeroNights演讲之后，我发现一个来自雅虎的序列化包。它也支持函数的序列化。但是，这个包不包含任何反序列化的功能，需要你自己去实现。它们的例子是直接使用eval。所以我感兴趣看看是否有其他软件包支持函数序列化，并且没有使用eval或者类似函数。

实际上，有很多序列化库(大约40或60)。我查看了其中一些，发现反序列化的一种更安全的方法是根据对象类型使用不同的构造函数。例如，一个包为函数返回新的Function（params，body），其中params和body从特定的JSON字段中获取。在这种情况下，函数被重建，但攻击者不能强制执行代码。

我还发现另一个含有漏洞的软件包funcster,它的利用方式和前面提到的IIFE相同。所以攻击者可以在反序列化过程中执行恶意代码。下面是一个有效的攻击payload

```
`{` __js_function: 'function testa()`{`var pr = this.constructor.constructor("return process")(); pr.stdout.write("param-pam-pam") `}`()' `}`
```

该包使用另外一种方法进行序列化/反序列化。在反序列化过程中，通过JSON文件创建一个带有导出函数的新模块。以下是一部分代码：

```
return "module.exports=(function(module,exports)`{`return`{`" + entries + "`}`;`}`)();";
```

这里一个有趣的不同点是标准的内置对象不可以访问，因为它们超出了范围。这意味着我们可以执行自己的代码，但是不能调用内置对象的方法。如果我们使用console.log()或require(something)，Node将返回一个异常，例如“ReferenceError：console is not defined”。

由于我们可以访问全局上下文，因此仍然可以轻松获取所有的内容。

```
var pr = this.constructor.constructor("console.log(1111)")();
```

这里this.constructor.constructor为我们提供了Function对象，我们将代码设置为一个参数并使用IIFE调用它。



## 用Prototype更深入一步

当我研究软件包的时候，我也发现了其他语言使用的反序列化攻击方法。为了实现代码执行，攻击者利用控制数据的函数，这些数据在反序列化过程中自动调用，或者在应用程序与新创建的对象进行交互之后调用。类似于其他语言中的“魔术方法”。

实际上，有很多软件包的工作方式完全不同，在经过一些实验之后，我发现了一个有趣的(semi-universal)半通用攻击。它基于两个条件。

首先，许多软件包在反序列化过程中使用下一种方法。它们创建一个空对象，然后使用方括号表示法设置其属性：

```
obj[key]=value
```

其中的key和value取自JSON 。

因此，作为攻击者，实际上我们可以控制新对象的任何属性。如果查看属性列表，并将注意力集中在cool **proto** property。这个属性用于修改和访问对象的原型，这意味着我们可以改变这个对象的行为和添加/修改它的方法。

其次，调用某个函数会导致调用函数参数的方法。例如，当一个对象转换为一个字符串时，该对象的方法valueOf，toString会自动调用（这里有更多细节)。所以，console.log（obj）导致调用obj.toString（）。另一个例子，JSON.stringify（obj）在内部调用obj.toJSON()。

使用这两个功能，我们可以在应用程序（node.js）和对象之间的交互过程中获得远程代码执行。

我发现了一个很好的例子 – 包Cryo，它支持函数序列化和用于对象重构的方括号表示法，但不易受IIFE影响，因为它可以正确管理对象（不使用eval＆co)。

以下是一个对象的序列化和反序列化的代码：

```
cvar Cryo = require('cryo');
var obj = `{`
testFunc : function() `{`return 1111;`}`
`}`;

var frozen = Cryo.stringify(obj);
console.log(frozen)

var hydrated = Cryo.parse(frozen);
console.log(hydrated);
```

序列化的JSON看起来像以下：

```
`{`"root":"_CRYO_REF_1","references":[`{`"contents":`{``}`,"value":"_CRYO_FUNCTION_function () `{`return 1111;`}`"`}`,`{`"contents":`{`"testFunc":"_CRYO_REF_0"`}`,"value":"_CRYO_OBJECT_"`}`]`}`
```

作为攻击者，我们可以用自定义**proto**创建一个序列化的JSON对象。我们可以用我们自己的方法创建对象原型的对象。一个小技巧，我们可以为**proto**设置一个不正确的名称（因为我们不想在应用程序中重写对象的原型）并将其序列化。

```
var obj = `{`
    __proto: `{`
        toString: function() `{`console.log("defconrussia"); return 1111;`}`,
        valueOf: function() `{`console.log("defconrussia"); return 2222;`}`
    `}`
`}`;
```

所以我们得到序列化的对象，并将其从**proto重命名为**proto__：

```
`{`"root":"CRYO_REF_3","references":[`{`"contents":`{``}`,"value":"_CRYO_FUNCTION_function () `{`console.log("defconrussia"); return 1111;`}`"`}`,`{`"contents":`{``}`,"value":"_CRYO_FUNCTION_function () `{`return 2222;`}`"`}`,`{`"contents":`{`"toString":"_CRYO_REF_0","valueOf":"_CRYO_REF_1"`}`,"value":"_CRYO_OBJECT"`}`,`{`"contents":`{`"proto":"CRYO_REF_2"`}`,"value":"_CRYO_OBJECT"`}`]`}`
```

当我们将JSON有效载荷发送给应用程序时，Cryo包反序列化有效载荷为一个对象，但也会将对象的原型更改为我们的值。因此，如果应用程序以某种方式与对象交互，例如将其转换为sting，那么原型的方法将被调用并且我们的代码将被执行。这就是代码执行。

我试图找到具有类似问题的包，但其中大多数不支持函数的序列化。我没有找到其他方法来重建**proto**中的函数。尽管如此，许多软件包使用方括号表示，我们也可以为它们重写**proto**，并破坏新创建对象的原型。当应用程序调用这些对象的任何原型方法时会发生什么？由于未处理的TypeError异常，它可能会崩溃。

另外，我提到整个想法可能适用于任何格式的反序列化,不仅是JSON格式。一旦两个功能同时使用，一个软件包就有可能受到攻击。另一件事是JSON.parse对**proto**重写不会造成攻击。

函数stringify == eval

我又发现一种序列化对象的方法。这个方法是先对函数进行字符串化，然后对整个对象进行JSON字符串化。“反序列化”由相同的步骤且相反的顺序组成。函数字符串化的例子包含cardigan, nor-function等其他的一些包。它们都是不安全的，由于eval＆co函数，并允许在无字符串转换过程中使用IIFE执行代码。



## 结论

对于测试者来说，仔细查看方括号表示并且访问**proto**,在某些情况下会有惊奇的发现。

对于开发人员：我在这里写一些软件包是含有漏洞的，但是当用户输入测试到易受攻击的功能时，您的应用程序才会受到攻击。一些软件包是以这种“不安全”的方式创建的，不会被修复。但是不要惊慌，只要检查一下你是否依赖于非标准的序列化包，以及如何处理用户的输入。

我使用HackerOne的程序与他们的维护者共享有关这两个漏洞的信息。funcster软件包的描述中增加了一条警告消息。但是我们无法联系到cryo的开发人员。

PS：感谢HackerOne的[@lirantal](https://github.com/lirantal)对上述漏洞的支持。



## 参考

Exploiting Node.js deserialization bug for Remote Code Execution



审核人：yiwang   编辑：边边
