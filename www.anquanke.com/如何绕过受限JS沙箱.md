> 原文链接: https://www.anquanke.com//post/id/172322 


# 如何绕过受限JS沙箱


                                阅读量   
                                **198388**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者licenciaparahackear，文章来源：licenciaparahackear.github.io
                                <br>原文地址：[https://licenciaparahackear.github.io/en/posts/bypassing-a-restrictive-js-sandbox/](https://licenciaparahackear.github.io/en/posts/bypassing-a-restrictive-js-sandbox/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01d05affa1a631f839.jpg)](https://p1.ssl.qhimg.com/t01d05affa1a631f839.jpg)



## 一、前言

在参与某个漏洞赏金计划时，我发现某个站点的功能非常有趣：该站点允许用户使用可控的表达式来过滤数据。我可以使用类似`book.price &gt; 100`的表达式来显示价格高于100美元的书籍，使用`true`为过滤器则显示所有书籍，`false`为过滤器不显示任何内容。因此，我可以知道所使用的表达式结果为`true`还是`false`。

该功能成功吸引了我的注意，因此我尝试传入更为复杂的表达式，如`(1+1).toString()==="2"`（结果为真）以及`(1+1).toString()===5`（结果为假）。这显然是JavaScript代码，因此我猜测我使用的表达式会传入NodeJS服务器上类似`eval`的某个函数。此时貌似我找到了一个远程代码执行（RCE）漏洞。然而，当我使用更为复杂的表达式时，服务器返回错误，提示表达式无效。我猜测服务端并没有使用`eval`函数来解析表达式，而是使用了JavaScript的某种沙箱。

在受限环境中使用沙箱来执行不可信代码通常并不完美。在大多数情况下，我们已经有一些方法能够绕过这种保护措施，以普通权限来执行代码。如果目标环境尝试限制使用像JavaScript之类复杂功能的语言，那么防护起来更难面面俱到。发现这个问题后，我决定花些时间尝试突破这个沙箱系统。我需要了解JavaScript内部工作原理，这样才能有助于查找并利用RCE。

我首先需要确定网站使用哪个库来实现沙箱，因为整个NodeJS生态中有数十个库可以实现该功能，并且在许多情况下这些实现方案并不完美。也有可能目标网站使用了自定义的沙箱，但这种可能性较小，因为开发者需要较多精力才能做到这一点。

最后，我通过分析应用的错误信息发现目标站点使用的是[static-eval](https://github.com/substack/static-eval)，这个库没有那么知名（但开发者是[substack](https://twitter.com/substack)，是NodeJS社区的一个名人）。虽然这个库最初并不是针对沙箱场景而设计（其实我现在也不了解这个库最开始的使用场景），但文档中的确涉及相关内容。目前，我测试的这个站点的确将该库用于沙箱环境。



## 二、绕过static-eval

`static-eval`的原理是使用[esprima](https://github.com/jquery/esprima/)库来解析JS表达式，将其转化为[AST（抽象语法树）](https://en.wikipedia.org/wiki/Abstract_syntax_tree)。给定AST和我们输入的变量对象后，目标会尝试计算表达式。如果目标发现某一点存在异常，那么函数就会失败，不会执行我们输入的代码。因为这一点，最开始时我有点动力不足，因为我发现这个沙箱系统对能接收的数据非常严格。我甚至不能在表达式中使用`for`或者`while`语句，因此想执行需要迭代算法的操作几乎无法完成。无论如何，我一直在尝试寻找系统中是否存在任何bug。

粗略分析后我并没有找到任何bug，因此我查看了`static-eval` [GitHub](https://github.com/substack/static-eval)项目的`commits`和`pull`请求。我发现其中有个[pull请求](https://github.com/substack/static-eval/pull/18)修复了2个bug，这些bug可以规避沙箱环境，这正是我所寻找的答案。我也发现了pull请求作者发表过的一篇[文章](https://maustin.net/articles/2017-10/static_eval)，其中深入分析了这些漏洞。因此，我第一时间在目标站点上测试了这些技术，但不幸的是，目标站点使用的是新版的`static-eval`，已经修复了这些漏洞。然而，当发现有人曾成功绕过沙箱后，我对自己也更有信心，因此开始寻找能规避沙箱的新方法。

随后，我深入分析了这两个漏洞，希望这些漏洞能帮我找到思路，发现该库中的新漏洞。



## 三、分析第一个漏洞

第一个漏洞使用了[constructor](https://developer.mozilla.org/es/docs/Web/JavaScript/Referencia/Objetos_globales/Function)来构造恶意函数，攻击者经常使用这种技术来绕过沙箱。比如，在绕过angular.js沙箱以获得XSS攻击点的大多数[`vm2`](https://github.com/patriksimek/vm2/issues/32)。例如，我们可以通过如下表达式打印出系统环境变量，证实漏洞的确存在（因为沙箱的存在，该操作可能不会成功）：

```
"".sub.constructor("console.log(process.env)")()
```

在如上代码中，`"".sub`是获得函数的一个简单方法（`(function()`{``}`)`也能实现类似功能），随后再获取该函数的`constructor`。当调用该函数后会返回一个新函数，该函数具体代码为传入的字符串参数。这类似于`eval`函数，但并没有立即执行代码，而是返回可以执行代码的一个函数。这就可以解释payload结尾为什么会有`()`，我们可以通过这种方式来调用该函数。

[![](https://p1.ssl.qhimg.com/t019ca146a6431e5410.png)](https://p1.ssl.qhimg.com/t019ca146a6431e5410.png)

我们可以执行更多操作，而不单单是打印环境变量。比如，我们可以使用NodeJS `child_process`模块的`execSync`函数来执行操作系统命令并返回输出结果。如下payload会返回`id`命令的输出结果：

```
"".sub.constructor("console.log(global.process.mainModule.constructor._load("child_process").execSync("id").toString())")()
```

上面的payload与之前的payload类似，不同点在于所创建函数的具体代码。在该代码中，`global.process.mainModule.constructor._load`与NodeJS中`require`函数的功能一样。由于我没注意到的某些原因，函数`constructor`内部无法使用`require`，因此我只能使用这种不优雅的表达方式。

[![](https://p0.ssl.qhimg.com/t01f0c6ec0672ec8269.png)](https://p0.ssl.qhimg.com/t01f0c6ec0672ec8269.png)

开发者通过阻止对函数对象属性的访问（通过`typeof obj == 'function'`来判断对象是否是函数）来修复该漏洞：

```
else if (node.type === 'MemberExpression') `{`
    var obj = walk(node.object);
    // do not allow access to methods on Function 
    if((obj === FAIL) || (typeof obj == 'function'))`{`
        return FAIL;
    `}`
```

这种修复方式非常简单，但也非常有效。由于`constructor`只能在函数中使用，因此现在我已无法访问该接口。对象的`typeof`属性无法修改，因此只要是函数，那么`typeof`必定等于`function`。我没有找到绕过这种防护的办法，因此我接着分析第二个漏洞。



## 四、分析第二个漏洞

与第一个漏洞相比，这个漏洞更加简单，也更加容易发现：问题在于沙箱允许我们创建匿名函数，但并没有检查函数内容，没有禁用恶意代码。实际上，我们可以将函数体直接传递给构造函数。如下代码能够实现与前面第一个payload同样的效果：

```
(function()`{`console.log(process.env)`}`)()
```

我们可以修改匿名函数的函数体，使用`execSync`来显示系统命令的执行结果，这部分工作留给大家来完成。

对于该漏洞，一种可能的修复方式是禁用`static-eval`表达式内部的所有匿名函数声明语句。然而，这样可能会阻止匿名函数的正常使用（比如，正常情况下匿名函数可以用来映射数组）。因此，缓解措施必须允许正常匿名函数的使用，同时还要阻止恶意的使用方式。开发者可以分析已定义函数的函数体，检查该函数不会执行任何恶意操作，比如访问构造函数。

实际的修复措施比第一个漏洞的修复方式要更为复杂。与此同时，Matt Austin（提出缓解措施的开发者）表示自己并不确定这种方法是否能够完美解决问题。因此，我决定找到绕过这种修复措施的方法。



## 五、寻找新漏洞

我注意到一个细节，`static-eval`会在函数定义时判断目标是否为恶意函数，而不在函数被调用时进行判断。因此`static-eval`并不会去考虑函数参数的具体值，因此这样就需要在函数被调用时进行判断。

我常用的做法就是尝试访问构造函数，通过某种方式绕过第一种修复措施（因为我无法访问函数的属性）。然而，如果我尝试访问函数参数的`constructor`时会出现什么情况？由于函数定义时并不知道这个值，因此我们有可能借此绕过系统的限制机制。为了测试这一点，我使用了如下表达式：

```
(function(something)`{`return something.constructor`}`)("".sub)
```

如果上面语句返回了`cnostructor`，那么我们成功找到了绕过办法。不幸的是事实并非如此。如果某个函数在函数定义时访问某个未知类型的某个属性时，就会被`static-eval`阻止（这里即为`something`参数）。

`static-eval`有个非常有用的特性，基本可以适用于所有情况。我们可以指定在`static-eval`内部可用的一些变量。比如，在本文开头，我使用了`book.price &gt; 100`这个表达式。在这种情况下，调用`static-eval`的代码会向其传入`book`变量的值，以便在表达式中使用该变量。

这给了我另一个思路：如果我构造一个匿名函数，参数名与已定义的变量名相同会出现什么情况？由于目标无法在定义时知道参数的值，因此可能会使用变量的初始值，这对我来说非常有用。假如我又一个变量`book`，其初始值为一个对象，那么利用如下表达式：

```
(function(book)`{`return book.constructor`}`)("".sub)
```

将得到一个非常满意的结果：当定义函数时，`static-eval`会检查`book.constructor`是否为有效的表达式。由于`book`最开始时为对象（其`typeof`值为`object`），并非函数，因此我们可以访问其`constructor`，成功创建函数。然而，当我调用该函数时，`book`会将传入的值作为参数传递给另一个函数（即`"".sub`，另一个函数）。然后访问并返回其`constructor`，最终成功返回`constructor`。

不幸的是，这种方法依然无法成功，因为开发者也考虑到了这种情况。在分析函数体时，所有参数的值会被设置为`null`，覆盖变量的初始值。部分代码如下所示：

```
node.params.forEach(function(key) `{`
    if(key.type == 'Identifier')`{`
      vars[key.name] = null;
    `}`
`}`);
```

这段代码会处理定义该函数的AST节点，遍历类型为`Identifier`的每个参数，提取其名称并将对应的`vars`属性为`null`。即便上述代码看起来非常正确，但也犯下了一个非常常见的错误：并没有覆盖所有可能的情况。如果某个参数比较奇怪，其类型不等于`Identifier`会出现什么情况？修复代码并没有采用白名单机制，会忽略该参数，继续执行剩余代码（类似黑名单机制）。这意味着如果我构造的节点类型与`Identifier`不同，那么该变量的值就不会被覆盖，因此就可以使用初始值。此时我非常确定自己找到了非常关键的一点。我只需要想办法将`key.type`的值设置为与`Identifier`不同的其他值即可。

前面我们提到过，`static-eval`使用[`esprima`库](https://github.com/jquery/esprima/)来解析我们输入的代码。根据相关文档，`esprima`这个解析器完全支持[ECMAScript标准](https://www.ecma-international.org/ecma-262/7.0/)。ECMAScript类似于JavaScript的另一种表示法，但具备更多的功能，语法上对用户而言更加友好。

ECMAScript添加的一个功能就是[函数参数解构](https://simonsmith.io/destructuring-objects-as-function-parameters-in-es6/)功能。在该功能的帮助下，如下JS代码现在可以正常执行：

```
function fullName(`{`firstName, lastName`}`)`{`
    return firstName + " " + lastName;
`}`
console.log(fullName(`{`firstName: "John", lastName: "McCarthy"`}`))
```

函数参数定义中包含花括号，不代表该函数接受`firstName`和`lastName`两个参数，而是只接受一个参数，该参数是包含`firstName`和`lastName`属性的一个对象。上面代码等同于如下代码：

```
function fullName(person)`{`
    return person.firstName + " " + person.lastName;
`}`
console.log(fullName(`{`firstName: "John", lastName: "McCarthy"`}`))
```

如果我们检查esprima生成的AST（我使用的是[这款工具](http://esprima.org/demo/parse.html)），就能看到一个非常令人满意的结果：

[![](https://p2.ssl.qhimg.com/t0149cd601d3571050e.png)](https://p2.ssl.qhimg.com/t0149cd601d3571050e.png)

实际上，这种新的语法可以让函数参数的`key.type`值不等于`Identifier`，因此`static-eval`在覆盖变量时不会处理该参数。通过这种方法，当执行如下表达式时:

```
(function(`{`book`}`)`{`return book.constructor`}`)(`{`book:"".sub`}`)
```

`static-eval`会使用`book`的初始值（这是一个对象），然后我们也能创建函数。但当函数被调用时，`book`就会变成一个函数，因此就能返回函数的`constructor`。现在我的确找到了绕过方法！

之前的表达式会返回函数的`constructor`，因此我只需要调用`constructor`来创建恶意函数，然后再调用新创建的函数即可。

```
(function(`{`book`}`)`{`return book.constructor`}`)(`{`book:"".sub`}`)("console.log(global.process.mainModule.constructor._load("child_process").execSync("id").toString())")()
```

我在本地环境安装了最新版的`static-eval`，并测试了这个表达式，结果与我的预期相符：

[![](https://p3.ssl.qhimg.com/t0154b9342ae9211de4.png)](https://p3.ssl.qhimg.com/t0154b9342ae9211de4.png)

任务完成！我找到了绕过`static-eval`库的一种方法，能够在使用该库的目标主机上执行代码。唯一的条件是需要知道变量值不是函数的某个变量名，并且该变量包含`constructor`属性。字符串（strings）、数字（numbers）、数组（arrays）以及对象（objects）都满足这些条件，因此这对我们来说应该不难。我只需要在我测试的网站上使用这种技术，证实目标存在RCE利用点即可。但事情真的那么简单吗？



## 六、无法在目标环境中生效

不幸的是，即使我找到了优雅并且可用的绕过方法后，我发现我测试的目标站点上并不能使用这种技术。唯一的条件是我们要掌握变量值不为函数的某个变量名，因此大家可能觉得我找不到这个切入点，导致我无法利用漏洞。然而事实上我的确满足这个条件，之所以无法成功利用，原因有点复杂。

这里介绍一下相关背景，该网站并没有直接使用`static-eval`库，而是通过[jsonpath](https://github.com/dchester/jsonpath) npm库来使用目标库。JSONPath是与XPATH类似的一个查询语言，但处理的是JSON文档而非XML文档，该库最早于2007年问世（参考[此处文章](https://goessner.net/articles/JsonPath/)）。

阅读JSONPath文档后，我发现这个项目非常糟糕，没有明确的规范，所实现的大多数功能有点随性而为之的感觉，并不去考虑添加这些功能是否必要。可惜的是NodeJS生态系统中充斥着类似的库。

[![](https://p4.ssl.qhimg.com/t016cf5e22d60873d79.jpg)](https://p4.ssl.qhimg.com/t016cf5e22d60873d79.jpg)

JSONPath具有一个过滤器表达式功能，可以过滤匹配给定表达式的文档。比如，我们可以使用`$.store.book[?(@.price &lt; 10)].title`来筛选价格低于`$10`的书籍，然后获取书籍的标题。jsonpath npm库使用`static-eval`来计算括号之间的表达式。我测试的站点可以让我指定JSONPath表达式，然后使用该库来解析这个表达式，因此RCE也就顺手拈来。

如果我们仔细观察上面那个JSONPath表达式，可以看到传递给`static-eval`的表达式为`@.price &lt; 10`。根据文档描述，`@`是包含待过滤文档的一个变量（通常是一个对象）。不幸的是，JSONPath开发者采用的是`@`这个符号。根据ECMAScript规范，该符号并不是一个有效的变量名。因此为了让`static-eval`能够正常工作，开发者需要[修改esprima代码](https://github.com/dchester/jsonpath/blob/87f97be392870c469308dd4dc90d2067863ea02a/lib/aesprim.js#L8)。使其能够将`@`当成一个合法的变量名。

当我们在`static-eval`中创建匿名函数时，匿名函数会嵌入另一个函数中，后者将其当成已定义的变量参数来使用。因此如果我在JSONPath过滤器表达式中创建一个匿名函数，那么它将创建包含该函数的一个函数，并且接受名为`@`的一个参数。程序会直接调用`constructor`来完成该操作，因此并没有使用之前的esprima补丁。然后，当定义函数时，它会抛出我无法规避的一个错误。这是这个库的一个bug，导致我们无法在过滤器表达式中定义函数（不管是不是恶意函数）。因此，本文介绍的这种绕过技术无法适用于这个库。

由于开发者在目标库中使用了`@`来命名变量，而该符号又不是JS中的有效变量名，因此我无法在目标站点中利用RCE漏洞，也没法获得4位数的漏洞赏金。为什么开发者不使用`_`（这是一个有效的变量名）、`document`或者`joseph`！经过这次学习，我找到了某个库中很大的一个漏洞，也学到了关于JavaScript的不少知识。



## 七、总结

即使我没有拿到预期的赏金，在与这个库搏斗的过程中我也乐此不疲。我也利用学到的知识绕过了另一个受限JS环境，这一次我并没有空手而归，回头我希望能够尽快公布相关研究报告。

这里还得再次感谢Matt Austin之前关于[static-eval](https://maustin.net/articles/2017-10/static_eval)的研究成果，没有这些成果支撑，也许我不会发现这个新的漏洞。

在测试目标系统方面，我们可以考虑在本地环境中复现并控制系统的每个功能，这样我们测试起来可以更加自由。在本文中，我使用了部署`static-eval`库的一个Docker实例，在此基础上尝试绕过沙箱。我的问题在于，我在整个研究过程中只使用过这个实例，没有去验证这种技术在实际网站中是否可用。如果我先验证了这一点，很可能早就发现这一点，可以早点腾出手来。这里我们可以吸取教训，不要过于抽象整个环境，我们需要不断测试在实际系统中的发现，而不是埋头钻到实验环境中。

最后提一下，如果我们正在审计部署类似系统的站点，该站点会将用户可控的表达式在沙箱中执行，我建议大家可以好好用心分析这个环境。沙箱系统很难尽善尽美，如果沙箱能够执行动态、全功能的编程语言（如JavaScript、Python或者Ruby）的话更难面面俱到。当我们发现沙箱绕过漏洞时，这种漏洞往往能够对包含该系统的应用造成重大影响。



## 八、时间线
<li>01/02/19 – 将漏洞信息提交给NodeJS安全团队以及static-eval维护人员，大家可以参考[原始报告](https://licenciaparahackear.github.io/posts/static-eval-sandbox-escape-original-writeup/)
</li>
- 01/03/19 – NodeJS安全团队复现漏洞，告诉我他们将联系程序库维护人员，如果维护人员不响应报告，则会公布安全公告
<li>02/14/19 – [nmpjs网站上公布安全公告](https://www.npmjs.com/advisories/758)
</li>
- 02/15/19 – [漏洞已被修复](https://github.com/browserify/static-eval/pull/21) ，发布新版程序库
- 02/18/19 – 程序库的README文件已更新，提到该库[不应该](https://github.com/browserify/static-eval/pull/22/files)作为沙箱来使用
- 02/26/19 – 发布新的[补丁](https://github.com/browserify/static-eval/pull/23)，因为我最早的补丁有个bug，导致`static-eval`仍然存在漏洞