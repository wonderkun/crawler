> 原文链接: https://www.anquanke.com//post/id/85241 


# 【技术分享】Python新型字符串格式漏洞分析


                                阅读量   
                                **85539**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/](http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01008a424a4c5fd53e.jpg)](https://p4.ssl.qhimg.com/t01008a424a4c5fd53e.jpg) 



翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：100RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

<br>

**前言**



本文对Python引入的一种格式化字符串的新型语法的安全漏洞进行了深入的分析，并提供了相应的安全解决方案。

当我们对不可信的用户输入使用str.format的时候，将会带来安全隐患——对于这个问题，其实我早就知道了，但是直到今天我才真正意识到它的严重性。因为攻击者可以利用它来绕过Jinja2沙盒，这会造成严重的信息泄露问题。同时，我在本文最后部分为str.format提供了一个新的安全版本。

需要提醒的是，这是一个相当严重的安全隐患，这里之所以撰文介绍，是因为大多数人很可能不知道它是多么容易被利用。

<br>

**核心问题**

从Python 2.6开始，Python受.NET启发而引入了一种格式化字符串的新型语法。当然，除了Python之外，Rust及其他一些编程语言也支持这种语法。借助于.format（）方法，该语法可以应用到字节和unicode字符串（在Python 3中，只能用于unicode字符串）上面，此外，它还能映射为更加具有可定制性的string.Formatter API。

 该语法的一个特点是，人们可以通过它确定出字符串格式的位置和关键字参数，并且随时可以显式对数据项重新排序。此外，它甚至可以访问对象的属性和数据项——这是导致这里的安全问题的根本原因。

 总的来说，人们可以利用它来进行以下事情： 



```
&gt;&gt;&gt; 'class of `{`0`}` is `{`0.__class__`}`'.format(42)
"class of 42 is &lt;class 'int'&gt;"
```

实质上，任何能够控制格式字符串的人都有可能访问对象的各种内部属性。

<br>

**问题出在哪里？**



第一个问题是，如何控制格式字符串。可以从下列地方下手：

1.字符串文件中不可信的翻译器。我们很可能通过它们得手，因为许多被翻译成多种语言的应用程序都会用到这种新式Python字符串格式化方法，但是并非所有人都会对输入的所有字符串进行全面的审查。

2.用户暴露的配置。 由于一些系统用户可以对某些行为进行配置，而这些配置有可能以格式字符串的形式被暴露出来。需要特别提示的是，我就见过某些用户可以通过Web应用程序来配置通知邮件、日志消息格式或其他基本模板。

 

**危险等级**

如果只是向该格式字符串传递C解释器对象的话，倒是不会有太大的危险，因为这样的话，你最多会暴露一些整数类之类的东西。

然而，一旦Python对象被传递给这种格式字符串的话，那就麻烦了。这是因为，能够从Python函数暴露的东西的数量是相当惊人的。 下面是假想的Web应用程序的情形，这种情况下能够泄露密钥：

 



```
CONFIG = `{`
    'SECRET_KEY': 'super secret key'
`}`
 
class Event(object):
    def __init__(self, id, level, message):
        self.id = id
        self.level = level
        self.message = message
 
def format_event(format_string, event):
    return format_string.format(event=event)
```

如果用户可以在这里注入format_string，那么他们就能发现下面这样的秘密字符串： 

```
`{`event.__init__.__globals__[CONFIG][SECRET_KEY]`}`
```

将格式化作沙箱化处理

那么，如果需要让其他人提供格式化字符串，那该怎么办呢？ 其实，可以利用某些未公开的内部机制来改变字符串格式化行为。



```
from string import Formatter
from collections import Mapping
 
class MagicFormatMapping(Mapping):
    """This class implements a dummy wrapper to fix a bug in the Python
    standard library for string formatting.
 
    See http://bugs.python.org/issue13598 for information about why
    this is necessary.
    """
 
    def __init__(self, args, kwargs):
        self._args = args
        self._kwargs = kwargs
        self._last_index = 0
 
    def __getitem__(self, key):
        if key == '':
            idx = self._last_index
            self._last_index += 1
            try:
                return self._args[idx]
            except LookupError:
                pass
            key = str(idx)
        return self._kwargs[key]
 
    def __iter__(self):
        return iter(self._kwargs)
 
    def __len__(self):
        return len(self._kwargs)
 
# This is a necessary API but it's undocumented and moved around
# between Python releases
try:
    from _string import formatter_field_name_split
except ImportError:
    formatter_field_name_split = lambda 
        x: x._formatter_field_name_split()
 
class SafeFormatter(Formatter):
 
    def get_field(self, field_name, args, kwargs):
        first, rest = formatter_field_name_split(field_name)
        obj = self.get_value(first, args, kwargs)
        for is_attr, i in rest:
            if is_attr:
                obj = safe_getattr(obj, i)
            else:
                obj = obj[i]
        return obj, first
 
def safe_getattr(obj, attr):
    # Expand the logic here.  For instance on 2.x you will also need
    # to disallow func_globals, on 3.x you will also need to hide
    # things like cr_frame and others.  So ideally have a list of
    # objects that are entirely unsafe to access.
    if attr[:1] == '_':
        raise AttributeError(attr)
    return getattr(obj, attr)
 
def safe_format(_string, *args, **kwargs):
    formatter = SafeFormatter()
    kwargs = MagicFormatMapping(args, kwargs)
    return formatter.vformat(_string, args, kwargs)
```

现在，我们就可以使用safe_format方法来替代str.format了：



```
&gt;&gt;&gt; '`{`0.__class__`}`'.format(42)
"&lt;type 'int'&gt;"
&gt;&gt;&gt; safe_format('`{`0.__class__`}`', 42)
Traceback (most recent call last):
  File "&lt;stdin&gt;", line 1, in &lt;module&gt;
AttributeError: __class__
```

**<br>**

**小结**

在本文中，我们对Python引入的一种格式化字符串的新型语法的安全漏洞进行了深入的分析，并提供了相应的安全解决方案，希望对读者能够有所帮助。


