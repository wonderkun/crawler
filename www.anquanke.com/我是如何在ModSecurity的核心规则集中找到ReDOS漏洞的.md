> 原文链接: https://www.anquanke.com//post/id/177101 


# 我是如何在ModSecurity的核心规则集中找到ReDOS漏洞的


                                阅读量   
                                **176116**
                            
                        |
                        
                                                                                    



[![](https://nosec.org/avatar/uploads/attach/image/c6e4f86c36eae49a6b0bf0a10f1047af/33.png)](https://nosec.org/avatar/uploads/attach/image/c6e4f86c36eae49a6b0bf0a10f1047af/33.png)



本文将会讲述我是如何在世界知名WAF的规则集中找到ReDOS漏洞的，如果你还不是很熟悉正则表达式和ReDOS漏洞，可以阅读我的前一篇文章：[https://nosec.org/home/detail/2506.html](https://nosec.org/home/detail/2506.html)。简单来说，ReDOS漏洞由于某些正则表达式在编写时忽略了安全性，导致在匹配搜索某些特殊的字符串时会消耗大量计算资源，产生DOS攻击的效果。而现在不少WAF产品都是依赖正则表达式对流量进行过滤，一旦哪个正则表达式存在安全问题，就有可能使WAF受到ReDOS漏洞的攻击。

最近，我花了很多时间去研究WAF中的ReDOS漏洞。而我的目标则是世界知名的WAF产品ModSecurity的核心规则集[CRS](https://github.com/SpiderLabs/owasp-modsecurity-crs)，因为它有大量的正则表达式，正好锻炼我的绕WAF能力，一石二鸟！

CRS有29个配置文件，其中包含大量正则表达式，我不可能全部手动测试，所以我编写了一个脚本自动化处理。遗憾的是脚本还处于alpha阶段，我还不能公开它，不过我已想好了发布时间，相信不久后就能和大家见面。

在利用脚本得到一些可疑的正则表达式后，我使用[regex101.com](http://regex101.com/)来去除表达式中的无用部分，例如把`((fine)|(vulnerable))`中的`(fine)`删除

我还使用了[RegexBuddy](https://www.regexbuddy.com/)来分析不同漏洞的利用方式，最后用Python解释器来确认利用有效。

现在，让我们谈谈我所发现的漏洞点以及它们的利用方式。



## Case#1

```
表达式: (?:(?:^["'`\\]*?[^"'`]+["'`])+|(?:^["'`\\]*?[d"'`]+)+)s

利用: """""""""""""" (大约1000个")
```

为什么是漏洞？

这个表达式是由`|`符连接两个子表达式而成的，而且两个子表达式都是以`^[”’`\\]*?`开头，然后末尾再接上一两个特殊字符。正则表达式引擎在处理时会遍历两种子表达式的所有可能，大大消耗计算资源。

而且在第二子表达式中，`^[”’`\\]*?`和`[d”’`]+`都会匹配`“`, `‘` 和反引号有明显的竞争关系。

这种`((pattern 1)+|(pattern 2)+)+`重复运算符加嵌套的模式很明显在处理特殊字符串时会消耗大量计算资源。



## Case#2

```
表达式: for(?:/[dflr].*)* %+[^ ]+ in(.*)s?do

弱点: for(?:/[dflr].*)* %

利用: for/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r
```

为什么是漏洞？

让我们一步步看看这个表达式对特殊字符串的匹配步骤

```
f
fo
for
for/
for/r
for/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r
```

我所给出的字符串后半部分会被`.*`所匹配，但由于字符串的末尾不是`%`，最终会导致匹配失败。

此时，为了成功匹配，此时匹配逻辑会放过最后的字符`r`，看看其余字符串是否符合：

```
for/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/r/
```

当然，匹配依旧失败。一般来说，匹配逻辑会不断后退，直到退无可退，彻底匹配失败。但是，由于这里是两个重复运算符的叠加应用，事情变得更加复杂。而且`/r`既可以被`.*`匹配，又会被`/[dflr]`匹配……

我不确定如果运行完需要多少次计算，我使用的`RegexBuddy4`的上限为10,00,000，很显然真实的数字远超这个值。



## Case#3

```
Pattern: (?:s|/*.**/|//.*|#.*)*(.*)
Exploit: ################################################
```

为什么是漏洞？

`(?:s|/*.**/|//.*|#.*)*`可以看作由`|`符连接四个子表达式，其中3个具有`.*`这种可以匹配一切的敏感符号。当正则表达式引擎将表达式与字符串进行匹配搜索时，只有最后的子表达式才匹配，但因为缺少表达式所需的`()`，匹配失败，此时正则表达式引擎会变得很疯狂，而且这里也存在重复运算符的嵌套问题。最终，每增加一个`#`字符，所需的计算步骤数就会疯狂增长。

最后这个case我在3个不同的规则中都有找到。

在我上报了以上漏洞后，得到了如下CVE：
- [CVE-2019-11387](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-11387)
- [CVE-2019-11388](https://nvd.nist.gov/vuln/detail/CVE-2019-11388)
- [CVE-2019-11389](https://nvd.nist.gov/vuln/detail/CVE-2019-11389)
- [CVE-2019-11390](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-11390)
- [CVE-2019-11391](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-11391)
感谢你的阅读，今后我将继续分享更多关于ReDOS的研究。

```
本文由白帽汇整理并翻译，不代表白帽汇任何观点和立场：https://nosec.org/home/detail/2508.html
来源：https://medium.com/@somdevsangwan/how-i-found-5-redos-vulnerabilities-in-mod-security-crs-ce8474877e6e
```
