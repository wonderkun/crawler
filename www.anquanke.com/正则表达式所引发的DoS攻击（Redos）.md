> 原文链接: https://www.anquanke.com//post/id/177100 


# 正则表达式所引发的DoS攻击（Redos）


                                阅读量   
                                **280073**
                            
                        |
                        
                                                                                    



[![](https://nosec.org/avatar/uploads/attach/image/7ec1f75bf0bc1585b9d8aa1adbd6e37f/22.png)](https://nosec.org/avatar/uploads/attach/image/7ec1f75bf0bc1585b9d8aa1adbd6e37f/22.png)



正则表达式（或正则表达式）基本上是搜索模式。例如，表达式`[cb]at`将匹配`cat`和`bat`。这篇文章不是介绍一个正则表达式的教程，如果你对正则表达式了解不多，可在阅读之前点击[https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285](https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285)了解。

首先，让我们介绍一些重点知识。



## 重复运算符

`+`是重复运算符，可代表某个字符或某个模式的重复。

```
ca+t 将会匹配 caaaat
```

此外，还有另一个重复运算符`*`。它和`+`之间唯一的区别是：`+`代表重复一次多次，`*`代表重复零次或多次。

```
ca*t  将同时匹配      caaaat和ct
ca+t  将匹配caaaat   但不会匹配  ct
```



## 贪婪匹配和非贪婪匹配

如果我想匹配`X`和`y`之间所有的字符，我可以简单地用`x.*y`进行处理，注意，`.`代表任意字符。因此，该表达式将成功匹配`x)dw2rfy`字符串。

但是，默认情况下，重复运算符是很贪婪的。他们会尝试尽可能多的匹配。

让我们再考虑上面的例子，

`x.*y`表达式如果对字符串`axaayaaya`进行处理，就会返回`xaayaay`。但是使用者可能并不期待这种结果，他们也许只想要字符串`xaay`，这种`x&lt;anything here&gt;y`的模式就是贪婪匹配和非贪婪匹配发挥作用的地方。默认情况下，表达式将返回尽可能长的结果，但我们可以通过使用运算符`?`指定其进行非贪婪匹配，此时表达式为`x.*?y`



## 计算（回溯）

计算机在处理正则表达式的时候可以说是非常愚蠢，虽然看上去它们有很强的计算能力。当你需要用`x*y`表达式对字符串`xxxxxxxxxxxxxx`进行匹配时，任何人都可以迅速告诉你无匹配结果，因为这个字符串不包含字符y。但是计算机的正则表达式引擎并不知道！它将执行以下操作

```
xxxxxxxxxxxxxx # 不匹配
xxxxxxxxxxxxxx # 回溯
xxxxxxxxxxxxx  # 不匹配
xxxxxxxxxxxxx  # 回溯
xxxxxxxxxxxx   # 不匹配
xxxxxxxxxxxx   # 回溯
xxxxxxxxxxx    # 不匹配
xxxxxxxxxxx    # 回溯

&gt;&gt;很多很多步骤 

xx             # 不匹配
x              # 回溯
x              # 不匹配
               # 无匹配结果

你不会以为结束了吧？这只是第一步！

现在，正则表达式引擎将从第二个x开始匹配，然后是第三个，然后是第四个，依此类推到第14个x。

最终总步骤数为256。
```

它总共需要256步才能得出无匹配结果这一结论。计算机在这方面真的很蠢。

同样，如果你使用非贪婪匹配，`x*?y`表达式会从一个字母开始匹配，直到尝试过所有的可能，这和贪婪匹配一样愚蠢。



## 利用

正如之前所见，使用正则表达式进行匹配搜索可能需要计算执行大量计算步骤，但一般来说这并不是问题，因为计算机速度很快，并且可以在眨眼间完成数千个步骤。

但是，计算机也是有极限的，我们能否造出一个字符串让计算机长时间的超负荷运转？这很有趣，也许我们可以试试以下简单的步骤：
- 了解正则表达式的模式
- 查看它是否有可能回溯
- 查看它是否有重复符号
- 查看它是否有安全限制
- ？？？？？
- DoS！
那么，我们到底如何发现这些潜在的攻击点呢？



## 重复运算符嵌套

如果你看到一个重复运算符嵌套于另一个重复运算符，就可能存在问题。

```
表达式：  xxxxxxxxxx 17945(x+)*y
Motive: 会匹配任意数量的x加上一个y
匹配字符串: xxxxxxxxxx(10 chars)
计算步骤数: 17945
```

此时计算步骤数并不算多，但是，这个增长趋势是很惊人的。

```
字符串                  X的个数                步数
z                      0                      3 
xz                     1                      6 
xxz                    2                      19 
xxxz                   3                      49 
xxxxz                  4                      122 
xxxxxz                 5                      292 
xxxxxxz                6                      687 
xxxxxxxz               7                      1585 
xxxxxxxxz              8                      3604 
xxxxxxxxxz             9                      8086 
xxxxxxxxxxz            10                     17945 
xxxxxxxxxxxz           11                     39451 
xxxxxxxxxxxxz          12                     86046 
xxxxxxxxxxxxxz         13                     186400 
xxxxxxxxxxxxxxz        14                     401443 
xxxxxxxxxxxxxxxz       15                     860197
xxxxxxxxxxxxxxxxz      16                     1835048 
xxxxxxxxxxxxxxxxxz     17                     3899434 
xxxxxxxxxxxxxxxxxxz    18                     8257581 
xxxxxxxxxxxxxxxxxxxz   19                     17432623 
xxxxxxxxxxxxxxxxxxxxz  20                     36700210 
xxxxxxxxxxxxxxxxxxxxxz 21                     77070388
```

如上所见，计算步骤数随着输入字符串中X的数量呈指数增长。

我不是很擅长数学，但如果输入40个x，貌似需要的计算步骤数是：

计算步骤数 = 98516241848729725

如果计算机可以在1秒内完成100万个计算步骤，则需要3123年才能完成所有计算。

以上我们所展示的情况看起来很是糟糕，但是还存在其他糟糕的情况。



## 多个重复运算符1

如果两个重复运算符相邻，那么也有可能很脆弱。

```
表达式：  .*d+.jpg
Motive: 会匹配任意字符加上数字加上.jpg
匹配字符串: 1111111111111111111111111 (25 chars)
计算步骤数: 9187
```

它没有前一个那么严重，但如果程序没有控制输入的长度，它也足够致命。



## 多个重复运算符2

如果两个重复运算符较为相近，也有可能受到攻击。

```
表达式：  .*d+.*a
Motive: 会匹配任意字符串加上数字加上任意字符串加上a字符
匹配字符串: 1111111111111111111111111 (25 chars)
计算步骤数: 77600
```

## 多个重复运算符3

`|`符号加上`[]`符号再配上`+`也可能受到攻击。

```
表达式：  (d+|[1A])+z
Motive: 会匹配任意数字或任意（1或A）字符串加上字符z
匹配字符串: 111111111 (10 chars)
计算步骤数: 46342
```

以上就是我所知道一些利用场景情况。你还知道更多吗？欢迎和我交流。



## 如何寻找这样的漏洞？

你一定想知道在哪里寻找这样的漏洞。目前来说一般应用于白盒审计，或者网站代码处于开源的情况，你可以查看它是否使用了一些敏感的正则表达式。



## 其他

以上介绍的攻击场景并不适用于所有正则表达式引擎（同时受到开发语言的影响），且已有针对回溯攻击的防护。

## 资源
<li>
[rxxr](https://github.com/ConradIrwin/rxxr2/)：用于检查正则表达式是否容易受到回溯影响的工具。</li>
<li>
[Regex Buddy](https://www.regexbuddy.com/)（付费）：它可以帮助您分析正则表达式。它有很多功能，包括计算步骤数，使用各种正则表达式引擎等。如果正则表达式容易受到回溯的影响，它也会发出警告。</li>
<li>
[研究论文](http://www.cs.bham.ac.uk/~hxt/research/redos_full.pdf)： Static Analysis for Regular ex pression Exponential Runtime via Substructural Logics</li>
<li>
[文章：](https://www.regular-ex%20pressions.info/catastrophic.html)Vulnerability in a real world regex pattern</li>
感谢你的阅读！

```
本文由白帽汇整理并翻译，不代表白帽汇任何观点和立场：https://nosec.org/home/detail/2506.html
来源：https://medium.com/@somdevsangwan/exploiting-regular-ex pressions-2192dbbd6936
```
