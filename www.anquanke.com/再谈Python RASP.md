> 原文链接: https://www.anquanke.com//post/id/204723 


# 再谈Python RASP


                                阅读量   
                                **269286**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01fce200a9cb70f028.jpg)](https://p5.ssl.qhimg.com/t01fce200a9cb70f028.jpg)



前几天看了腾讯小哥七夜发的关于python rasp的文章，想到之前也做过类似的研究，也来谈谈我知道的几种解决方案吧



## 概述

RASP（Runtime application self-protection）运行时应用自我保护，在红方中的应用一般有以下几种：<br>
1、配合实现IAST，在SDL中使用作为精准的检测方案<br>
2、应用层agent，用来弥补系统层agent难以还原原始攻击手法的缺陷<br>
3、动态解密，对于变形和动态执行的恶意代码或者webshell来说，rasp是最清晰的解密



## 几种实现方案概述

1、PEP 578 — python runtime audit hook<br>
python新版本中对标powershell模块记录等功能实现的审计方案<br>
优点:官方提供的审计方案，非侵入方案，且实现起来极其简单<br>
缺点:依赖版本过高(&gt;3.8)，只能作为记录方案，不能实现阻断能力

2、USDT<br>
感觉usdt dtrace的这些方案好像聊得比较少，文献也不太多，dtrace是一种动态追踪技术，最早是solaris上面提供，慢慢移植到了linux osx 最近连windows上都开始部分支持了，各类主流的语言其实也都有支持做了埋点(但是需要添加编译选项)，而python在3.6版本开始添加支持<br>
优点：也是官方的解决方案，侵入性小<br>
缺点：对操作系统版本和python版本的依赖都比较高，而且需要重新编译，默认显示的内容也不算特别丰富

3、import hook<br>
在load_module的过程中做的一种劫持方案<br>
触发点不太一样，其实跟方案4差不多

4、monkey patch<br>
这个是聊得最多的方案了，也是那个经典问题”如何让2+2=5”的一个解法<br>
优点：能够实现的功能最为全面，可劫持可以记录，且客观支持的python版本最广<br>
缺点：侵入式的解决方案，可能会影响业务稳定性，而且对于statement的语法(exec print等)劫持不到



## 具体实现

### <a class="reference-link" name="PEP%20578%20%E2%80%94%20python%20runtime%20audit%20hook"></a>PEP 578 — python runtime audit hook

在python3.8+中，sys模块新增了addaudithook方法，用于记录模块的执行过程，实现起来也极其方便，是四种方案中最简单的，效果也是最好的

```
import sys
def audit_hook(event,args):
    print("event is " + str(event) + " args is " + str(args))
sys.addaudithook(audit_hook)
```

[![](https://p3.ssl.qhimg.com/t01701ce7e8d8555393.png)](https://p3.ssl.qhimg.com/t01701ce7e8d8555393.png)

### <a class="reference-link" name="USDT"></a>USDT

最早看到python usdt是在bcc中（ [https://github.com/iovisor/bcc](https://github.com/iovisor/bcc) ）<br>
他的实现其实可以作为一套完整的主机安全agent了，在tools/pythonflow.sh中提供了显示python执行流的能力。<br>
而单独使用systemtap的调用过程：<br>
yum install systemtap kernel-devel systemtap-sdt-devel<br>
然后重新编译python<br>
./configure —prefix=/usr/local/python3 —with-dtrace

安装完成后可通过stap查看python提供的埋点

[![](https://p0.ssl.qhimg.com/t012e9091b009a5e3b7.png)](https://p0.ssl.qhimg.com/t012e9091b009a5e3b7.png)

详情可参考<br>[https://docs.python.org/zh-cn/3.8/howto/instrumentation.html](https://docs.python.org/zh-cn/3.8/howto/instrumentation.html)<br>
常用：<br>
function__entry(str filename, str funcname, int lineno) #函数执行<br>
import__find__load__start(str modulename) #模块加载

```
cat rasp.stp
#!/usr/bin/stap
probe begin `{`
        printf("beginn");
`}`
 probe process("/root/Python-3.9.0a6/python").mark("function__entry") `{`
     filename = user_string($arg1);
     funcname = user_string($arg2);
     lineno = $arg3;
     printf("filename:%s funcname:%s lineno:%d n",filename,funcname,lineno)

 `}`
probe process("/root/Python-3.9.0a6/python").end `{`
         exit()
`}`
```

执行效果

[![](https://p3.ssl.qhimg.com/t013d78a5c91e1952cb.png)](https://p3.ssl.qhimg.com/t013d78a5c91e1952cb.png)

### <a class="reference-link" name="import%20hook"></a>import hook

<a class="reference-link" name="%E8%83%8C%E6%99%AF%EF%BC%9A"></a>**背景：**

```
在import的模块加载过程中有以下几个重要过程
1、在sys.modules中寻找缓存避免重复加载
2、如果找不到则调用python的import协议来寻找和加载模块，包含
 a) 查找器
     使用sys.meta_path中的finder来寻找对应模块的spec
 b) 加载器
     使用上面找到的spec生成module object
实现了查找器和加载器接口的就是导入器，将其插入到sys.modules的最前面就可以劫持导入的过程
另外在site-packages目录下可创建sitecustomize.py或usercustomize.py，属于python自启动脚本
```

<a class="reference-link" name="hook:"></a>**hook:**

以劫持requests.get 为例，在site-packages目录下创建sitecustomize.py

```
import sys
import importlib
import functools
class MetaPathFinder:
    def find_module(self, fullname, path=None):
        hook_modules = ['requests']
        if fullname in hook_modules:
            return MetaPathLoader()
class MetaPathLoader:
    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        finder = sys.meta_path.pop(0)
        module = importlib.import_module(fullname)
        hook_module(fullname, module)
        sys.meta_path.insert(0, finder)
        return module
def my_waper(func):
    @functools.wraps(func)
    def get_args(*args,**kwargs):
        print("nFCN HOOK: %s %s (args=%s,kwargs=%s)" % (str(func),__name__,args,kwargs))
        return func(*args,**kwargs)
    return get_args
def hook_module(fullname,module):
    if fullname == 'requests':
        module.get = my_waper(module.get)
        frame = sys._getframe(2)
        code = frame.f_code
        file_path = code.co_filename
sys.meta_path.insert(0, MetaPathFinder())
```

### <a class="reference-link" name="monkey%20patch"></a>monkey patch

<a class="reference-link" name="%E6%8A%80%E6%9C%AF%E8%83%8C%E6%99%AF"></a>**技术背景**

python需要hook的函数类型分为以下几种<br>
1、exec 表面是函数，实际是statement（python2），在一切皆对象的python里面很罕见的非对象的东西了，所以在python3中就被改过去了。。<br>
暂时还没看到有hook的解决方案，但问题不大，对于动态解密来说甚至可以直接正则替换<br>
2、bound/unbound method<br>
区别就是是否绑定方法对象，在hook的写法方面会有一些区别<br>
3、builtin method<br>
builtin method是_builtins_模块下面的函数，从函数地址上就能看的出来

```
&gt;&gt;&gt; id(__builtins__.eval)
140568811177024
&gt;&gt;&gt; id(eval)
140568811177024
&gt;&gt;&gt;
```

但是直接替换_builtins_下方法时，在另一个namespace中不会生效，之前一直以为是有什么特殊的安全机制，后来发现_builtins_是__builtin的引用，所以直接替换是不会生效的，那直接修改__builtin就行了<br>
4、builtin 模块中的方法<br>
内置模块中的方法不支持修改

```
&gt;&gt;&gt; str.decode = mydecode
Traceback (most recent call last):
  File "&lt;stdin&gt;", line 1, in &lt;module&gt;
TypeError: can't set attributes of built-in/extension type 'str'
&gt;&gt;&gt;

```

这个的解决方案最早应该是来自于”如何在python中实现让2+2=5”这个经典问题的一个解，git地址 [https://github.com/fdintino/python-doublescript](https://github.com/fdintino/python-doublescript)<br>
具体涉及到的python c api的知识点简单说下<br>
1、PyObject是cpython中的对象基石，其中包含obrefcnt的引用计数器和ob_type，ob_type则指向PyTypeObject<br>
在ctypes中如果需要使用Structures，需要显示声明_fields，对于PyObject来说fields就是obrefcnt和obtype<br>
2、from_address(id(target)) 直接使用地址作为线索，把python下的变量转成了c下的变量了<br>
3、ctypes.pythonapi.PyDict_SetItem 将第二个变量作为key，第三个变量作为value，插入字典第一个变量，作为原始函数的保留，插入到原来对象的__dic中，后续方便保持原有逻辑的引用

```
Py_ssize_t = hasattr(ctypes.pythonapi, 'Py_InitModule4_64') and ctypes.c_int64 or ctypes.c_int
class PyObject(ctypes.Structure):
    pass
PyObject._fields_ = [('ob_refcnt',Py_ssize_t),('ob_type',ctypes.POINTER(PyObject))]
class DictProxy(PyObject):
    _fields_ = [('dict',ctypes.POINTER(PyObject))]
def patch_builtin(klass):
    name = klass.__name__
    target = klass.__dict__
    proxy_dict = DictProxy.from_address(id(target))
    namespace = `{``}`
    ctypes.pythonapi.PyDict_SetItem(
        ctypes.py_object(namespace),
        ctypes.py_object(name),
        proxy_dict.dict,
    )
    return namespace[name]
def patch_innerfunction(klass,attr,value):
    dikt = patch_builtin(klass)
    old_value = dikt.get(attr,None)
    old_name = '_c_%s' % attr
    if old_value:
        dikt[old_name] = old_value
    if old_value:
        dikt[attr] = value
        try:
            dikt[attr].__name__ = old_value.__name__
        except:
            pass
        try:
            dikt[attr].__qualname__ = old_value.__qualname__
        except:
            pass
    else:
        dikt[attr] = value
```



## 后记

从现状来看高版本python和linux内核的使用率都很低，方案一、二都难以作为大规模rasp部署的方案，但是方案一对于快速解密python脚本来说是最好的方案，方案二对于想以bcc类方案构建主机agent来说整体性很好，方案四作为最经常被讨论的方案整体的通用性还是最好的
