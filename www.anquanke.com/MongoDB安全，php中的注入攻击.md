> 原文链接: https://www.anquanke.com//post/id/84009 


# MongoDB安全，php中的注入攻击


                                阅读量   
                                **120254**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://blog.securelayer7.net/mongodb-security-injection-attacks-with-php/](http://blog.securelayer7.net/mongodb-security-injection-attacks-with-php/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01111c65a0aff32653.jpg)](https://p4.ssl.qhimg.com/t01111c65a0aff32653.jpg)

在讨论MongoDB注入之前,我们必须要了解它到底是什么,以及我们之所以相较于其他数据库更偏爱它的原因。因为MongoDB不使用SQL,所以人们就假想它不容易受到任何形式的注入攻击。但是相信我,没有什么东西生来就内置安全防护。我们还是要设置一些逻辑代码来防止攻击。

MongoDB是什么?

简单来说,MongoDB是MongoDB公司开发的一个开源数据库,可以以不同结构的类似于JSCON文档的形式存储文件。相关的信息会被存储在一起,这样有利于使用MongoDB查询语言进行快速查找。

为什么要使用MongoDB?

因为大家都想要快速查询,所以MongoDB非常受欢迎。它的性能非常好(1000millionsquries/秒)。它更受欢迎的另一个原因就是它擅长在很多相关数据库不能很好适应的案例中发挥作用。例如,非结构化的应用程序、半结构化和多态数据或是可伸缩性要求高并且拥有多个数据中心的应用程序。

到此为止吧!如果在运行任何开源式应用程序的话,为了防止糟糕的情况发生,还是到此为止吧。我们为开源项目提供一种免费的渗透测试。在这里提交应用程序吧,我们会进行评价。

让我们来看一下注入攻击

第一种情况下,我们有一个PHP脚本,该脚本可以显示一个特定ID的用户名和对应密码。

[![](https://p4.ssl.qhimg.com/t01ab018e80faffde55.png)](https://p4.ssl.qhimg.com/t01ab018e80faffde55.png)

  

[![](https://p4.ssl.qhimg.com/t012fe5968fee02f9f1.png)](https://p4.ssl.qhimg.com/t012fe5968fee02f9f1.png)

在上面的脚本中可以看到数据库名称是安全,集合名称是用户。U-id参数会由GET算法获得,然后将其传递到数组,之后就会给出相关结果。听上去很好?我们试着放入一些比较运算符和数组。

[![](https://p3.ssl.qhimg.com/t013ee7db93f82e62ef.png)](https://p3.ssl.qhimg.com/t013ee7db93f82e62ef.png)

糟糕!!它得出的结果是整个数据库。问题到底出在哪呢?这是因为输入了http://localhost/mongo/show.php?u_id[$ne]=2,创建了下面这种MongoDB查询,$qry= array(“id” =&gt; array(“$ne” =&gt; 2))。所以它显示了除id=2之外的所有结果,可以从截屏1中看到。

让我们来考虑一下另一种情况,在前期脚本的工作内容是一样的,但是我们会用findOne方法来创建MongoDB查询。

首先我们来看一下findOne的工作原理。此方法有下列语法:

db.collection.findOne(查询、投影)

这将返回到满足指定查询条件的文档。例如,我们需要找到与id=2相关的结果,就会出现下列命令:

[![](https://p4.ssl.qhimg.com/t0129e92a13034f0d21.png)](https://p4.ssl.qhimg.com/t0129e92a13034f0d21.png)

现在让我们看一下源代码:

[![](https://p0.ssl.qhimg.com/t015c01200be83868c3.png)](https://p0.ssl.qhimg.com/t015c01200be83868c3.png)

这里的关键点就是在某种程度上打破查询,然后再修复它。那如果我们键入以下查询,又会发生什么呢?

http://localhost/mongo/inject.php?u_name=dummy’`}`);return`{`something:1,something:2`}``}`//&amp;u_pass=dummy

这会打破查询并返回所需参数。让我们来检查一下输出:

[![](https://p1.ssl.qhimg.com/t01c5460d9b680b577a.png)](https://p1.ssl.qhimg.com/t01c5460d9b680b577a.png)

这带来了两个错误,但是这只是因为我们想要访问两个不存在的参数吗?这种错误间接地表明,用户名和密码在数据库中是一种参数,而这就是我们想要的结果。

只要我们键入正确的参数,错误就会消除。

[![](https://p5.ssl.qhimg.com/t01ce5d07f295fbc5be.png)](https://p5.ssl.qhimg.com/t01ce5d07f295fbc5be.png)

现在我们想要找出数据库名称。在MongoDB中,用于查找数据库名称的方法是db.getName() 。因此查询就变成了:

[![](https://p3.ssl.qhimg.com/t015069aaf0408063e8.png)](https://p3.ssl.qhimg.com/t015069aaf0408063e8.png)

为了将此数据库转储,我们首先要找出集合的名称。在MongoDb中,用于查找集合名称的方法是db.getCollectionNames()。

[![](https://p2.ssl.qhimg.com/t019feab005764b6a5c.png)](https://p2.ssl.qhimg.com/t019feab005764b6a5c.png)

所以到现在为止,我们已经得到了数据库和集合的名称。剩下的就是要找到用户名集合,做法如下:

[![](https://p5.ssl.qhimg.com/t01541ffa92e0ee2aad.png)](https://p5.ssl.qhimg.com/t01541ffa92e0ee2aad.png)

同样的,我们可以通过改变内部函数db.users.find()[2]来获得其他的用户名和密码,比如说:

[![](https://p5.ssl.qhimg.com/t01be8836e5e4e35ba7.png)](https://p5.ssl.qhimg.com/t01be8836e5e4e35ba7.png)

既然大家都对MongoDb很熟悉,那么大家可能会想要了解相关的预防措施。

让我们考虑一下第一种情况,参数在数组中传递。要想防止这种注入,我们可能需要停止执行数组中的比较运算符。因此,其解决方案之一就是用下列方式使用implode()函数:

[![](https://p4.ssl.qhimg.com/t01800c46cea58c8164.png)](https://p4.ssl.qhimg.com/t01800c46cea58c8164.png)

implode()函数返回值是一个字符串数组。因此我们得到的只会是一个对应特定ID的结果,而不是所有结果。

[![](https://p2.ssl.qhimg.com/t014aa2e2d7f2957954.png)](https://p2.ssl.qhimg.com/t014aa2e2d7f2957954.png)

在第二种情况中,我们可以使用 addslashes() 方法来保证查询不被攻击者打破。使用正则表达式来替换特殊符号是一个好主意。可以使用下列的正则表达式:

$u_name =preg_replace(‘/[^a-z0-9]/i’, ‘’, $_GET[‘u_name’]);

[![](https://p5.ssl.qhimg.com/t01fca34e1a7b58c1a4.png)](https://p5.ssl.qhimg.com/t01fca34e1a7b58c1a4.png)

这样之后,如果我们试图打破查询,它就不会再重蹈覆辙。

[![](https://p2.ssl.qhimg.com/t018f5f8c3f3e696484.png)](https://p2.ssl.qhimg.com/t018f5f8c3f3e696484.png)
