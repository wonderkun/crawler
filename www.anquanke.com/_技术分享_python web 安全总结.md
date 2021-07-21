> 原文链接: https://www.anquanke.com//post/id/87007 


# 【技术分享】python web 安全总结


                                阅读量   
                                **313996**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01363e77b4c46b016e.png)](https://p5.ssl.qhimg.com/t01363e77b4c46b016e.png)

**<br>**



作者：[mapl0](http://bobao.360.cn/member/contribute?uid=621946719)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**引言**

作者以前学习过php方面的安全知识，机缘巧合的情况下学习了django，在学习的过程中顺便收集总结了一下python安全方面的知识点以及近年来的相关漏洞，如果有需要修正或补充的地方，欢迎各位师傅的指出。

ps:特别感谢c1tas&amp;lucifaer两位师傅的指点。

常见web漏洞在python中的示例。

<br>

**xss**

python下的xss其原理跟php是一样的，django近年的例子如下：

**CVE-2017-12794**,此例中通过抛出异常造成xss。



**sql注入**

一般来说使用django自带的操作数据库api是不会造成sql注入的,如下：

```
Person.objects.filter(first_name=request.GET.get('user'))
```

不过django依然支持原生sql语法的使用方法,如下：



```
def index(request, *args, **kwargs):
        for e in Person.objects.raw('select * from FIRST_Person '):
            print(e.first_name,e.last_name)
        return render(request, 'home.html')
```

控制台结果如下：



```
asd sdf
    mapl0 ppp
    admin hahaha
```

如果代码如下：



```
def index(request, *args, **kwargs):
        for e in Person.objects.raw('select * from FIRST_Person WHERE first_name = ' + '"' + request.GET.get('user') + '"'):
            print(e.last_name)
        return render(request, 'home.html')
```

访问**http://127.0.0.1:8000/?user=admin**后控制台返回hahaha

而访问**http://127.0.0.1:8000/?user=qqq%22%20or%20%221**，控制台直接返回了



```
sdf
    ppp
    hahaha
```



**代码/命令执行**

除内建的模块，还有**os,commands,subprocess,multiprocessing,pty，Cpickle/pickle，PyYAML**等模块能代码/命令执行，详细可看下文。

<br>

**CSRF**

django这类的框架**自带csrf防护**，不过在去年依然爆出csrf漏洞[**CVE-2016-7401-Django**](http://blog.knownsec.com/2016/10/django-csrf-bypass_cve-2016-7401/)（知道创宇这篇分析很细致），如果django使用了Google Analytics则可能绕过django自带的csrf防护机制。

Django对于CSRF的防护就是**判断cookie中的csrftoken和提交的csrfmiddlewaretoken**的值是否相等，但是**Google Analytics可以通过referer帮我们设置用户的cookie**，cookie一般如下：

```
utmz=123456.123456789.11.2.utmcsr=[HOST]|utmccn=(referral)|utmcmd=referral|utmcct=[PATH]
```

其中[HOST]和[PATH]是由Referer确定的，也就是说当

```
Referer: http://x.com/helloworld
```

时，cookie如下：

```
z=123456.123456789.11.2.utmcsr=x.com|utmccn=(referral)|utmcmd=referral|utmcct=helloworld
```

django在当时的版本有cookie解析漏洞，当Cookie.SimpleCookie()解析a=hello]b=world这样的字符串时，就会取得a=hello和b=world，所以当Referer为http://x.com/hello]csrftoken=world，csrftoken就被成功赋值。

详细的[**代码分析**](http://blog.knownsec.com/2016/10/django-csrf-bypass_cve-2016-7401/)，值得一看。



**文件上传**

在php环境下如果不限制上传文件后缀会导致getshell，但在django下，如果上传的文件能覆盖类似url.py，__init__.py的文件，攻击者能顺利getshell。参考[https://www.secpulse.com/archives/36220.html](https://www.secpulse.com/archives/36220.html) 。还有django只有在development server的模式下才会修改了文件就立刻重启，否则修改了文件也暂时无法生效。

当然除此之外还有其他方法，例如写cron（前提是有权限），和模板文件。

简单说一下写模板文件的过程：

需要在templatetags和templates分别写入一个文件（可能也不叫templatetags，可自行定义），templatetags文件夹内存放自定义标签，上传文件rce.py，代码如下：



```
from django import template
    import os
    register = template.Library()
    @register.simple_tag
    def some_function(value):
        shell = os.system('touch mapl0')
        return shell
```

templates文件夹存放静态html文件，上传文件home.html如下：



```
&lt;!DOCTYPE html&gt;
    &lt;html&gt;
    &lt;head&gt;
        &lt;meta charset="UTF-8"&gt;
        &lt;title&gt;Title&lt;/title&gt;
    &lt;/head&gt;
    &lt;body&gt;
    `{`% load rce %`}`
    `{`% some_function "%s" as func %`}`
    &lt;p&gt; command is `{``{` func `}``}` &lt;/p&gt;
    &lt;/body&gt;
    &lt;/html&gt;
```

在view里，index会使用这个模板：



```
def index(request, *args, **kwargs):
        return render(request, 'home.html')
```

访问后，就在项目目录生成了mapl0文件。

可见使用限制很大，还需要一定的权限。首先，文件后缀没有限制，其次上传路径没有限制，templatetags目录已知，另外还需要有view使用这个模板。

另外xml和html文件的自由上传依然可以造成xxe和xss。



**文件包含**

[案例](http://bobao.360.cn/news/detail/1475.html)

相比之下文件包含比php少得多

<br>

**重定向**

****

django在今年爆出了两个重定向漏洞[CVE-2017-7233&amp;7234](https://paper.seebug.org/274/)其中的CVE-2017-7233与urlparse有关，漏洞的说明可查看下文。

<br>

**不安全模块及函数**

****

**内建函数**

**input():**

python input() 相等于 eval(raw_input(prompt)) ，用来获取控制台的输入,在python3.0以后的版本中取消raw_input,并用input代替.



```
value = input("hello ")
    print("welcome %s" % (value,))
```

python2命令行下：



```
hello dir()
    welcome ['__builtins__', '__doc__', '__file__', '__name__', '__package__']
```

python3命令行下:



```
hello dir()
    welcome dir()
```

**assert():**

assert断言是声明其布尔值必须为真的判定，如果发生异常就说明表达示为假。



```
Traceback (most recent call last):
      File "/Users/mapl0/Desktop/资料/sec.py", line 3, in &lt;module&gt;
        assert os.system('touch test')
    AssertionError
```

报了个错误，但test文件已被建立

**代码执行函数**

eval:计算字符串中的表达式

exec:执行字符串中的语句

execfile:用来执行一个文件#python3中已无此函数



```
a = "print('eval:hello')"
    b = "print('exec:hello')"
    eval(a)
    exec(b)
```

python2和python3下结果一样

eval:hello

exec:hello

execfile('temp.bin')#temp.bin内容为print('execfile:hello')

结果

execfile:hello

**os模块:**

os.system

os.popen#和os.system的区别在于popen会把命令的输出作为返回值

os.spawn

[os.exec家族](http://wangyongbin.blog.51cto.com/8964308/1672725)

**commands模块 :**

```
commands.getstatusoutput
```

**subprocess模块 :**

subprocess.Popen

subprocess.call通过子进程进行外壳注入



```
from subprocess import call
    unvalidated_input = '/bin/true'#true命令啥都不做,只设置退出码为0
    unvalidated_input += '; cut -d: -f1 /etc/passwd'
    call(unvalidated_input, shell=True)#当shell=true时，shell命令可被当做多句执行。
```

运行结果

    nobody

    root

    ……..

multiprocessing多进程模块 :



```
import multiprocessing
    p = multiprocessing.Process(target=print, args=("hello"))#target参数为函数名，args为函数所需参数
    p.start()
    p.join()
```

运行结果

h e l l o

**pty :**

只能在linuxmac下使用的**伪终端**



```
import pty
    pty.spawn('ls')
```

在python23下均可执行命令

其他有安全问题模块及函数

**codecs :**

codecs作用于各种编码之间的相互转换



```
import codecs
    import io
    b = b'x41xF5x42x43xF4'
    print("Correct-String %r") % ((repr(b.decode('utf8', 'replace'))))
    with open('temp.bin', 'wb') as fout:
        fout.write(b)
    with codecs.open('temp.bin', encoding='utf8', errors='replace') as fin:
        print("CODECS-String %r") % (repr(fin.read()))
    with io.open('temp.bin', 'rt', encoding='utf8', errors='replace') as fin:
        print("IO-String %r") % (repr(fin.read()))
```

当b以二进制方式写入文件后，用codecs在进行读取，如果errors='replace'且编码形式为utf-8时，则对于xF5和xF4这类不能编码的都会被替换为ufffd。

在python2下：



```
Correct-String "u'A\ufffdBC\ufffd'"
    CODECS-String "u'A\ufffdBC'"
    IO-String "u'A\ufffdBC\ufffd'"
```

在Python3下会报错：



```
print("Correct-String %r") % ((repr(b.decode('utf8', 'replace'))))
    TypeError: unsupported operand type(s) for %: 'NoneType' and 'str'
```

**ctypes :**

ctypes是一个**提供和C语言兼容的数据类型的外部库**，当出现x00的空字符就会出现截断



```
import ctypes
    buffer = ctypes.create_string_buffer(8)
    buffer.value='abx00c1234'
    print(buffer.value)
    print (buffer.raw)
```

在python2命令行下:

    ab

    abc1234

在python3下回报错：



```
buffer.value='abx00c1234'
    TypeError: bytes expected instead of str instance
```

**Python Interpreter :**



```
#!python
    try:
        if 0:
            yield 5
        print("T1-FAIL")
    except Exception as e:
        print("T1-PASS")
        pass
    try:
        if False:
            yield 5
        print("T2-FAIL")
    except Exception as e:
        print(repr(e))
        pass
```

对于类似if 0: if False: 的写法，python版本的不同，其测试结果也不同

[![](https://p5.ssl.qhimg.com/t012589bb06bdd991b8.png)](https://p5.ssl.qhimg.com/t012589bb06bdd991b8.png)

可重用整数 :



```
999+1 is 1000 #False
    1+1 is 2 #True
```

对此的解释是，Python 维护了一个对象连接池，其中保有前几百个整数，重用它们会节约内存和对象的创建。

浮点数比较 :

```
2.2 * 3.0 == 3.3 * 2.0 #False
```

由于固有受限精度，以及十进制与二进制小数表示所产生的差异导致的舍入错误。

无穷大 :

python支持无穷大的概念，但在python2下出现了这样的情况



```
Type "help", "copyright", "credits" or "license" for more information.
    10**1000000 &gt; float('infinity')
    False
    float &gt; float('infinity')
    True
```

python3下



```
10**1000000 &gt; float('infinity')
    False
     float &gt; float('infinity')
    Traceback (most recent call last):
      File "&lt;stdin&gt;", line 1, in &lt;module&gt;
    TypeError: unorderable types: type() &gt; float()
```

**builtins :**

此模块在python启动后首先加载到内存，此时还没有执行任何程序员写的代码，在Python2.X版本中，内建模块被命名为__builtin__，而到了Python3.X版本中更名为builtins。

在 Python 2中， 内置对象可以通过魔法 __builtins__ 模块进行访问。



```
__builtins__.False, __builtins__.True = True, False
      True
      False
      int(True)
      0
```

false被赋值成true，true被赋值成false

**urllib2:**

Python 的 urllib 库曾出过一个头注入的漏洞，[CVE-2016-5699](http://blog.neargle.com/SecNewsBak/drops/Python%20urllib%20HTTP%E5%A4%B4%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E.html)

如果请求头里出现了**%0A**则直接换行导致攻击者可以注入额外http头和请求方法，可在ssrf里攻击redis或者memcached。

Python2/Python3较新的版本均在出口处的putheader()函数里添加了一个检验，发现不合法URL会报一个error.

**tarfile/ZipFile:**

tarfile模块可以读取和写入tar文件，包括使用gzip或bz2压缩的压缩文件。

ZipFile模块提供了创建，读取，写入，附加和列出ZIP文件的函数。

TarFile.extractall使用此函数提取文件时，文件可能创建在其他路径，官方建议不要从不信任的来源提取文件。

ZipFile.extractall也有同样的问题，解压时文件可能创建在其他路径，但在2.7.4版本中，模块会试图阻止这种行为。

**urlparse :**

[CVE-2017-7233](https://paper.seebug.org/274/) urllib.parse.urlparse的特殊情况曾给django造成一个url跳转漏洞。

django的**is_safe_ur**l函数可用于检测url是或否安全，但整合各函数是基于urllib.parse.urlparse的，urlparse在当scheme不等于http，path为纯数字时不能正常分割使得is_safe_url为true，从而达到bypass的目的。

例如 https:1029415385，is_safe_url会直接判断为true。

**格式化字符串漏洞:**

起因是python的新方法format，示例如下：



```
class mapl0:
        user = 'mapl0'
        password = 'hahaha'
        key = '123456'
    print("This is `{`user.user`}` `{`user.password`}`".format(user = mapl0))
```

我们可以通过format将mapl0类中的属性输出出来，在这篇[paper](https://paper.seebug.org/175/)中(@phithon)就有类似的情况：



```
def view(request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.GET.get('uid'))
        template = 'This is `{`user`}`'s email: ' + request.GET.get('email')
        return HttpResponse(template.format(user=user))
```

由于request.GET.get('email')也就是用户通过get传入的email参数完全可控，我们就能让request.user里的任意属性输出出来，例如`{`user.password`}`。

通过debug查看了一下request.user里的内容,其中session_key,目录，secret_key等等敏感信息都能查看，其中SECRET_KEY如果泄露，则可能配合django反序列化漏洞实现rce。

[![](https://p4.ssl.qhimg.com/t0156734683638758a4.png)](https://p4.ssl.qhimg.com/t0156734683638758a4.png)

Jinja的沙盒绕过与此同理。顺便一说，在[paper](https://paper.seebug.org/175/)还提到的f修饰符很有意思，在python3.6版本会后，被f/F修饰的字符串将会被当做代码执行。



**反序列化**

****

**Cpickle/pickle 反序列化：**

python2 使用cPickle，python3 使用pickle，__reduce__函数会在被反序列化是执行，类似php里的__wakeup，当我们序列化了一个带有__reduce__的类时，将其反序列化即可执行__reduce__里的代码



```
import os
    import cPickle
    a = 1
    # Exploit that we want the target to unpickle
    class Exploit(object):
        def __reduce__(self):
            global a
            a = 10
            os.system("pwd")
            return (os.system, ('ls',))
    shellcode = cPickle.dumps(Exploit())#cPickle.dumps序列化操作
    cPickle.loads(shellcode)#cPickle.loads反序列化操作
    print a
```

pickle用法类似



```
import os
    import pickle
    # Exploit that we want the target to unpickle
    class Exploit(object):
        def __reduce__(self):
            return (os.system, ('ls',))
    shellcode = pickle.dumps(Exploit())
    pickle.loads(shellcode)
```

[Django任意代码](http://www.freebuf.com/vuls/77591.html)在django1.6版本前存在任意代码执行漏洞，其漏洞起因就是pickle。

在django1.6以下，session默认是采用pickle执行序列号操作，在1.6及以上版本默认采用json序列化，但还需要知道SECRET_KEY以及目标采用了signed_cookies。

[掌阅iReader某站Python漏洞挖掘](https://www.leavesongs.com/PENETRATION/zhangyue-python-web-code-execute.html)，通过redis写session从而反序列化getshell。

**PyYAML 对象类型解析导致的命令执行问题：**

[http://blog.knownsec.com/2016/03/pyyaml-tags-parse-to-command-execution/](http://blog.knownsec.com/2016/03/pyyaml-tags-parse-to-command-execution/) 



```
import yaml
    content = '''---
    !!python/object/apply:subprocess.check_output [[ls]]#subprocess.check_output父进程等待子进程完成 返回子进程向标准输出的输出结果
    ...'''
    print yaml.load(content)
```

python2下结果

1.py

__init__.py

__pycache__

……

python3下结果

```
b'1.pyn__init__.pyn__pycache__n................
```

**shelve：**

shelve用处是让对象持久化，但它在序列化与反序列化的过程中使用了pickle模块，因此我们可以利用shelve会调用的pickle在反序列化过程中执行代码。



```
import shelve
    import os
    class exp(object):
        def __reduce__(self):
            return (os.system('ls'))
    file = shelve.open("test")
    file['exp'] = exp()
    print(file['exp'])
```

一些在较新版本被弃用的函数和模块

**rexec:**

在python2.6后被弃用，相关[文档](https://docs.python.org/2/library/rexec.html).

**bastion:**

在python2.6后被弃用，相关[文档](https://docs.python.org/2/library/bastion.html).

**tempfile.mktemp:**

此函数自从2.3版本不推荐使用并使用mkstemp()代替，相关[文档](https://docs.python.org/3/library/tempfile.html?highlight=mktemp#tempfile.mktemp)



**总结**

****

python安全还远不止上文所述部分，随之python使用者的增多，其安全性必然也会不断地收到挑战，而我们也需要从中不断学习以应对随时袭来的威胁。



**参考文章**

****

[http://python.jobbole.com/82746/](http://python.jobbole.com/82746/) 

[http://www.freebuf.com/articles/web/73669.html](http://www.freebuf.com/articles/web/73669.html) 

[https://virusdefender.net/index.php/archives/576/](https://virusdefender.net/index.php/archives/576/) 

[https://paper.seebug.org/337/](https://paper.seebug.org/337/) 

[http://www.freebuf.com/articles/system/89165.html](http://www.freebuf.com/articles/system/89165.html) 
