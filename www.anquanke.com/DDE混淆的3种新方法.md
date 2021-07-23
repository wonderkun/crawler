> 原文链接: https://www.anquanke.com//post/id/161041 


# DDE混淆的3种新方法


                                阅读量   
                                **222362**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：reversinglabs.com
                                <br>原文地址：[https://blog.reversinglabs.com/blog/cvs-dde-exploits-and-obfuscation](https://blog.reversinglabs.com/blog/cvs-dde-exploits-and-obfuscation)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t011733f7381386cd49.jpg)](https://p2.ssl.qhimg.com/t011733f7381386cd49.jpg)

## 一、前言

最近一段时间，微软的Office产品已经成为滋养新型攻击方法的沃土，从相对比较简单的数据注入方法（如[DDE注入](https://sensepost.com/blog/2017/macro-less-code-exec-in-msword/)以及[CSV注入](http://blog.securelayer7.net/how-to-perform-csv-excel-macro-injection/)）到更加复杂的基于[嵌入公式对象](https://research.checkpoint.com/another-office-equation-rce-vulnerability/)的攻击技术，不一而足。反病毒行业很快吸收了这些技术，有许多厂商可以正确检测并识别大多数攻击方法。然而万物都处于演化之中，因此攻击场景中出现攻击手段的混淆及变种也只是时间问题。思科Talos以及ReversingLabs曾发表过一篇联合[文章](https://blog.talosintelligence.com/2018/09/adwind-dodgesav-dde.html)，介绍与CSV DDE注入有关的两种新技术（一种混淆技术以及一个变种）。本文的目的是为大家解释这些技术背后的一些“原理”，也会介绍3种新的混淆技术。



## 二、CSV/DDE代码注入

尽管网上关于DDE代码注入技术已经有许多参考资料，但这里我们还可以简单过一下这种技术的原理。CSV（使用逗号作为分隔符）是一种简单的数据格式，可以用来存储结构化数据，也可以作为Excel的数据源（Excel会解析该数据，然后将被分隔符切分的数据填充到单元格中）。实际上，如果文件格式与文件扩展名不匹配，但该文件扩展名可以使用Excel来打开，那么Excel似乎会采用CSV模式来导入数据。

根据微软的描述，DDE（Dynamic Data Exchange，动态数据交换）是应用之间传输数据的一种方法。Excel可以使用这种机制，根据外部应用的处理结果来更新单元格的内容。因此，如果我们制作包含DDE公式的CSV文件，那么在打开该文件时，Excel就会尝试执行外部应用，这个过程听起来非常简单。



## 三、DDE解析

虽然听起来简单，但工作过程却稍微复杂一些。当打开文件时，Excel会逐个检查文件的每一行。将该行的的内容分隔并拷贝到对应的单元格之前，Excel会检查当前行是否以某些命令字符开头。这些字符可能是内部函数所需的字符，如`=`、`+`、`-`以及`@`。根据命令的前缀，可能会出现以下两种情况：

1、如果前缀为为`=`、`+`或者`-`，那么后续数据就会被当成表达式来处理；

2、如果前缀为`@`，那么Excel会搜索内部函数（比如`SUM()`），将参数解析成表达式。

到目前为止，前面都是大家可以从网上找到的公开资料，但状态机如何处理表达式可能参考资料就相对较少。说到DDE时，相应的表达式大致可以表示为：

```
command|’arguments’!cell
```

命令本身也是一种表达式。如果表达式中仅包含可打印字符（甚至包含一些不可打印字符，如`0xAA`，具体取决于代码页），那么缓冲区大小就为256字节。由于命令前缀或者操作符占了1个字符，因此实际上表达式只有255个字节可用。表达式可以是名称、数字、字符串或者文件名。

即便缓冲区中有足够大的空间，内部程序的最大文件名长度为8个字符。这可能是MS-DOS文件名的历史遗留问题，当时系统最大只支持8字节长文件名（不包括扩展名）。

然而，表达式通常采用递归定义，可以采用算术及逻辑运算符（如`&amp;`、`^`、`/`、`+`等等）链接起来，甚至还可以使用左括号（表示函数参数的开始）或者冒号（用作单元格分隔符）。虽然命令不应该被当成表达式来处理，但由于null字节会被全部忽略掉，而空格有时候后会被忽略（比如位于命令之前的空格），因此出现这种情况也不足为奇。

换句话说，表达式中可以包含数量不限的null字节。Excel会忽视参数以及单元格中的null字节。重要的是，单元格引用根本不必为有效值。一旦表达式被成功解析及转换，命令和参数就会传递给`WinExec()` API执行。



## 四、更多细节

思科Talos在[文中](https://blog.talosintelligence.com/2018/09/adwind-dodgesav-dde.html)提到，攻击样本会使用简单的混淆技术，比如在DDE公式之前或者之后附加文本或者二进制数据。这似乎只是冰山一角，这是因为数据解析规则不仅可以处理前缀（prefix）或后缀（suffix）形式的混淆命令，也能处理中缀（infix）形式的混淆数据。

表达式可以串联使用，我们也可以在实际命令之前注入任意数量的表达式（每个子表达式最多可以使用255个字符），命令甚至也可以串联起来使用，这也是命令可以使用混淆前缀的基础，如下所示：

```
=AAAA+BBBB-CCCC&amp;"Hello"/12345&amp;cmd|'/c calc.exe'!A
=cmd|'/c calc.exe'!A*cmd|'/c calc.exe'!A
+thespanishinquisition(cmd|'/c calc.exe'!A
=         cmd|'/c calc.exe'!A
```

目前在实际攻击中看到的载荷会选择`cmd`、`msexcel`或者`msiexec`作为可执行目标文件，，但我们可以任意选择其他外部应用，只要文件名少于8字符即可，而这个条件在实际环境中很容满足。比如，`regsvr32`、`certutil`以及`rundll32`都满足文件名长度要求，这为我们打开了后缀混淆攻击的新世界：

```
=rundll32|'URL.dll,OpenURL calc.exe'!A
=rundll321234567890abcdefghijklmnopqrstuvwxyz|'URL.dll,OpenURL calc.exe'!A
```

最后，我们可以在各处添加null字节或者空格，达到中缀混淆目的。空格不能嵌入到命令名称中，一旦嵌入就将拆分命令名，导致命令无法执行。但是命令名之前以及或者参数中的空间还可以为我们所用。当然，命令名不区分大小写，因此我们可以使用不同的大小写方案来进行混淆。大家可以访问[此处](https://cdn2.hubspot.net/hubfs/3375217/proof_of_concept.zip?t=1538160223600)下载前面我们描述的所有混淆样例（密码为`infected`）。

[![](https://p1.ssl.qhimg.com/t01f665dae6f8e0bb50.jpg)](https://p1.ssl.qhimg.com/t01f665dae6f8e0bb50.jpg)

图1. A1000十六进制数据中的中缀混淆示例

这些混淆技术当然可以单独使用，或者可以组合使用。我们已经使用Excel 2013以及Excel 2017测试过本文提到的所有混淆技术，在本文撰写时没有任何杀毒软件厂商能够检测到这些技术。为了帮大家防御这类简单的混淆攻击，我们同样发布了匹配的YARA规则，大家可以访问[此链接](https://cdn2.hubspot.net/hubfs/3375217/obfuscated_dde.yara?t=1538160223600)下载。



## 五、总结

在本文中，我们介绍了混淆DDE载荷的3种新技术：前缀、中缀以及后缀混淆技术。由于Office产品在过去27年中一直在不断完善，丰富的功能同样给正常用户和恶意用户带来广阔的表演舞台。在接下来的几年时间内，可以预见的是新的攻击方法及混淆技术将不断演化，我们也希望能看到推陈出新的技术用来投递攻击载荷。
