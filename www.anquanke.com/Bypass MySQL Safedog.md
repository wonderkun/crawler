> 原文链接: https://www.anquanke.com//post/id/188465 


# Bypass MySQL Safedog


                                阅读量   
                                **778867**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t0136a9bfa315469964.jpg)](https://p3.ssl.qhimg.com/t0136a9bfa315469964.jpg)



跟团队小伙伴一起日狗



## 判断注入

安全狗不让基本运算符后跟数字字符串

特殊运算符绕

16进制绕

BINARY绕

conv()函数绕

concat()函数绕



## 判断字段数

绕order by

内联

注释换行



## 联合查询

关键在于打乱union select

内联

注释后跟垃圾字符换行

union distinct | distinctrow | all

接下来是查数据，我在这使用注释垃圾字符换行也就是%23a%0a的方法来绕，你可以用上面说的/*!14440*/内联

查当前数据库名

查其他库名 安全狗4.0默认没开information_schema防护的时候可以过，开了information_schema防护之后绕不过去，哭唧唧😭

查表名

查列名，首先是没开information_schema防护时

开information_schema防护有两种姿势，不过需要知道表名

一、子查询

二、用join和using爆列名，前提是页面可以报错，需要已知表名

[![](https://p4.ssl.qhimg.com/dm/1024_549_/t01944e8970418e8b83.png)](https://p4.ssl.qhimg.com/dm/1024_549_/t01944e8970418e8b83.png)

然后通过using来继续爆

[![](https://p3.ssl.qhimg.com/dm/1024_549_/t011ec2e75861741f68.png)](https://p3.ssl.qhimg.com/dm/1024_549_/t011ec2e75861741f68.png)

查数据

其实配合MySQL5.7的特性可以使用sys这个库来绕过，具体看chabug发的文章吧 [注入bypass之捶狗开锁破盾](https://www.chabug.org/web/1019.html)

> 在下文中不再提及开启information_schema防护的绕过姿势，自行举一反三。



## 报错注入

报错注入只提及updatexml报错

关键在于updatexml()结构打乱

不让updatexml匹配到两个括号就行了

用户名 库名

库名

表名

列名

查数据



## 盲注

分布尔盲注和时间盲注来说吧

### 布尔盲注

不让他匹配完整括号对

使用left()或者right()

使用substring() substr()

查表名

列名字段名同理，略

### 时间盲注

不匹配成对括号

sleep()绕过

查用户

查数据 limit过不了



## 其他

length()长度

count()



## 参考

[https://github.com/aleenzz/MYSQL_SQL_BYPASS_WIKI](https://github.com/aleenzz/MYSQL_SQL_BYPASS_WIKI)

[https://www.chabug.org/web/1019.html](https://www.chabug.org/web/1019.html)

文笔垃圾，措辞轻浮，内容浅显，操作生疏。不足之处欢迎大师傅们指点和纠正，感激不尽。
