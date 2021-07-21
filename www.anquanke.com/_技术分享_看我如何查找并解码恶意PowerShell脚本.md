> 原文链接: https://www.anquanke.com//post/id/87039 


# 【技术分享】看我如何查找并解码恶意PowerShell脚本


                                阅读量   
                                **167101**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：az4n6.blogspot.com
                                <br>原文地址：[http://az4n6.blogspot.com/2017/10/finding-and-decoding-malicious.html](http://az4n6.blogspot.com/2017/10/finding-and-decoding-malicious.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01ed7604d38a70d6ae.png)](https://p4.ssl.qhimg.com/t01ed7604d38a70d6ae.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

****

PowerShell的身影无所不在，我最近也遇到过越来越多的恶意PowerShell脚本。为什么攻击者热衷于使用PowserShell？因为许多Windows版本中都会自带这个工具，并且该工具可以访问WMI以及.Net Framework的全部功能，也能在内存中执行恶意代码以逃避反病毒软件的查杀，对了，与PowerShell相关的日志记录也没有那么完备。

在对这类案例的分析过程中，我发现了多条线索可以证明某位攻击者已经利用PowerShell实施过攻击。这些线索包括已安装的服务、注册表条目以及磁盘上的PowerShell文件。如果启用了日志记录功能，我也能找到许多有用的信息。本文的目的是为那些对PowerShell不是特别熟悉的安全分析人员提供一份参考。在本文中，我会向大家介绍如何定位恶意PowerShell程序的一些经验，同时也会介绍解码经过混淆的PowerShell脚本的一些方法。这一系列文章共有三篇，本文是第一篇，未来几周我会陆续推出后续文章。

<br>

**二、Part 1：以服务形式安装的PowerShell脚本**

****

首先我想介绍我最喜欢的一个例子：如何通过System事件日志发现攻击者将PowerShell脚本安装成本机服务。为了定位这类程序，我所做的第一件事情就是查找ID为7045的那些事件（Event ID 7045）。当系统中安装某个服务时，日志中就会出现这类事件。以服务形式安装的某个PowerShell脚本如下所示：

[![](https://p1.ssl.qhimg.com/t011af9a0e5771c7418.png)](https://p1.ssl.qhimg.com/t011af9a0e5771c7418.png)

上图中我用红框标出了一些值得注意的信息：

1、服务名（Service Name）为随机的字符串。

2、服务文件名（Service File Name）为%COMSPEC%，这个字符串为cmd.exe所对应的环境变量。

3、引用了powershell可执行文件。

4、包含经过Base64编码的数据。

那么，这类事件为什么会出现在日志中？有多种方法可以做到这一点，其中一种方法就是使用内置的Windows服务控制管理器（Service Control Manager）来创建服务，命令如下所示：



```
sc.exe create MyService binPath=%COMSPEC% powershell.exe -nop -w hidden -encodedcommand
sc start MyService
```

上述命令会创建名为“MyService”的一个服务，“binPath=”选项用来启动cmd.exe，后者会执行PowerShell代码。

有个有趣的信息需要引起我们的注意：以这种方式创建服务后，我们可能会得到一些错误信息。然而，这些错误信息并不意味着服务安装失败，原因在于Windows希望安装“真实”的二进制程序，因此在等待这个“服务”时会出现“超时”，最终呈现错误信息。我也是经过测试才知道这一点。在测试过程中，我使用该方法成功安装了一个反弹shell，操作过程中Windows主机上会产生服务错误信息。如下图中，左图为我在攻击虚拟机上启动的一个Metasploit会话，右图为安装了Windows 7系统的虚拟机。虽然Windows 7主机会提示“服务没有及时响应启动或控制请求（The service did not respond to the start or control request in a timely fashion）”，但并不影响Metasploit会话中成功打开反弹shell：

[![](https://p2.ssl.qhimg.com/t014611d656c72e3392.png)](https://p2.ssl.qhimg.com/t014611d656c72e3392.png)

如下两图分别对应System事件日志中的7000以及7009事件。虽然7009事件提示说“FakeDriver服务启动失败（The FakeDriver service failed to start）”，但这并不代表binPath变量中包含的命令执行失败。所以，如果根据这些信息判断PowerShell没有执行，我们可能会得到错误结论：

[![](https://p2.ssl.qhimg.com/t0165dc9b24e4c82bb5.png)](https://p2.ssl.qhimg.com/t0165dc9b24e4c82bb5.png)

[![](https://p2.ssl.qhimg.com/t015f72e9295ca9b32f.png)](https://p2.ssl.qhimg.com/t015f72e9295ca9b32f.png)

我们可以使用python来解码System日志中7045事件所包含的经过base64编码的PowerShell命令。有趣的一点是，这是一段Unicode编码的base64代码，因此在解压时我们需要指定额外的参数。（为了便于展示，我没有全部呈现所有base64文本，你需要在解码程序中包含所有的base64文本）：

```
import 
base64 code="JABjACAAPQAgAEAAIgAKAFsARABsAGwASQBtAHAA...." 
base64.b64decode(code).decode('UTF16')
```

解码后的PowerShell命令如下所示。快速查看代码后，我们可以找到一些有趣的线索，比如，我们可以在其中找到与Net Socket有关的TCP协议以及IP地址信息：

[![](https://p1.ssl.qhimg.com/t01b2d152245a27f8f0.png)](https://p1.ssl.qhimg.com/t01b2d152245a27f8f0.png)

这段代码在功能上与使用Meterpreter用来创建反弹shell类似。上述PowerShell代码解码起来非常容易，然而，许多场景下，我们面临的情况并没有那么简单。

接下来是另一个例子，这一次我们面对的是“普通”的base64代码。其中我们需要再次注意%COMSPEC%变量以及其中包含的powershell.exe字符串：

[![](https://p4.ssl.qhimg.com/t012b1e6d13ddc0e0e6.png)](https://p4.ssl.qhimg.com/t012b1e6d13ddc0e0e6.png)

我们还是使用Python来解码这段base64编码的PowerShell代码：

[![](https://p0.ssl.qhimg.com/t0173c440e63b6c0349.png)](https://p0.ssl.qhimg.com/t0173c440e63b6c0349.png)

这一次，解码后的结果没有那么直观。如果我们回过头好好观察一下System中的事件记录，我们可以发现其中包含有关“Gzip”以及“Decompress”相关信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0118535051165017cd.png)

根据这些信息，我们可以逆向思考，这段数据可能先经过Gzip的压缩，然后再使用base64进行编码。因此，我决定使用python将base64的解码结果写入到文件中，以便进一步解压缩处理：

```
import base64 
code="H4sICCSPh1kCADEAT..." 
decoded=base64.b64decode(code) 
f=open("decoded.gzip",'wb') 
f.write(decoded) 
f.close
```

通过7zip，我成功解压了这个gzip文件！操作过程中没有出现任何错误信息，因此我使用的可能是正确的方法：

[![](https://p2.ssl.qhimg.com/t01eac69002d290669c.png)](https://p2.ssl.qhimg.com/t01eac69002d290669c.png)

然后，我通过文本编辑器打开解压后的文件，希望能看到一些PowerShell代码：

[![](https://p5.ssl.qhimg.com/t0196cceb2bb3cf6b60.png)](https://p5.ssl.qhimg.com/t0196cceb2bb3cf6b60.png)

什么情况？好吧，是时候祭出十六进制编辑器了：

[![](https://p0.ssl.qhimg.com/t01e7ab5b3b566668cc.png)](https://p0.ssl.qhimg.com/t01e7ab5b3b566668cc.png)

依然没有太大帮助。我猜测这应该是一段shellcode代码。下一步，我想通过**PDF Stream Dumpe**r的shellcode分析工具，即scdbg.exe来分析这段数据：

[![](https://p2.ssl.qhimg.com/t0143c4ca80f3681983.png)](https://p2.ssl.qhimg.com/t0143c4ca80f3681983.png)

正中靶心！scdbg.exe可以从shellcode中提取出某些IOC特征。

总结一下，为了解码这段PowerShell代码，我用到了如下方法：

1、解码base64编码的PowerShell字符串。

2、将解码后的base64内容写入zip文件。

3、使用7zip解压Gzip文件。

4、通过scdbg.exe分析所得的二进制输出结果。

如上所述，在取得最终成果前，我们需要通过若干个挑战关卡。

最后一个例子：

[![](https://p1.ssl.qhimg.com/t012c2c3ad5b4234944.png)](https://p1.ssl.qhimg.com/t012c2c3ad5b4234944.png)

这个画面看起来似曾相识。第一步，我们需要解码这段Unicode形式的base64字符串，结果如下所示，我们可以看到base64代码中竟然还包括其他base64代码！：

[![](https://p1.ssl.qhimg.com/t01ce085f2a334df5a1.png)](https://p1.ssl.qhimg.com/t01ce085f2a334df5a1.png)

显然，代码先经过混淆，然后使用压缩方法再次进行混淆。这种情况之前我经常见到。这一次压缩文本中没有显示包含“gzip”字符串，因此我决定将第二轮base64结果保存到常规zip文件中，然后使用7zip再次打开这个文件：



```
decoded2="nVPvT9swEP2ev+IUR...." 
f=open("decoded2.zip,"wb") 
f.write(base64.b64decode(decoded2) 
f.close()
```

使用7zip打开这个文件时，我看到了如下错误：

[![](https://p5.ssl.qhimg.com/t01aec9217655810fd3.png)](https://p5.ssl.qhimg.com/t01aec9217655810fd3.png)

使用Windows自带的工具打开时也会提示错误信息：

[![](https://p2.ssl.qhimg.com/t019543862e0e7212c4.png)](https://p2.ssl.qhimg.com/t019543862e0e7212c4.png)

我也试过使用各种python库来解压这个压缩文件。经过一番调研后，我发现这种压缩方式与某些.Net库有关。由于我自己非常喜欢Python，我想知道如何使用Python来解压这个文件，这样我就能将解压代码写到自己的脚本中。Python是门跨平台语言，在Linux、Windows以及Mac都可以使用，而.Net由于核心机制原因无法做到这一点。因此，我选择使用Iron Python来解决这个问题（当然，你可以使用PowerShell来解压这段数据，然而我前面说过，我还是想用Python来完成这个任务）。

根据Iron Python官网的说法，“IronPython是Python编程语言的开源实现方案，与.NET Framework密切相关。IronPython可以使用.NET Framework和Python库，并且其他.NET代码想要使用Python代码也非常简单”。在Windows上安装IronPython非常简单，只需要一个MSI文件即可。安装完毕后，你就可以使用ipy.exe来运行脚本（稍后我会给出具体例子）。

有了这个工具后，我就可以开发python代码（io_decompress.py），使用python IO压缩库来解压zip文件：



```
import required .Net libraries
from System.IO import BinaryReader, StreamReader, MemoryStream from System.IO.Compression import CompressionMode, DeflateStream from System import Array, Byte from System.IO import FileStream, FileMode from System.Text import Encoding from System.IO import File
functions to decompress the data
def decompress(data): iozip = DeflateStream(MemoryStream(data), CompressionMode.Decompress) str = StreamReader(iozip).ReadToEnd() io_zip.Close() return str
print "Decompressing stream..." compressedBytes = File.ReadAllBytes("decoded2.zip") decompressedString = decompress(compressedBytes)
f = open("decompressed.txt", "wb") f.write(decompressedString) f.close()
```

通过IronPython来运行这段脚本也非常简单，命令为**ipy.exe io_decompress.py**，如下所示：

[![](https://p5.ssl.qhimg.com/t01604dc2c4d8d75a9e.png)](https://p5.ssl.qhimg.com/t01604dc2c4d8d75a9e.png)

这段脚本生成了decompressed.txt文件，其中包含明文版的PowerShell脚本，如下图所示。我们需要注意其中包含的IP地址信息：

[![](https://p1.ssl.qhimg.com/t010d76eb805558c18c.png)](https://p1.ssl.qhimg.com/t010d76eb805558c18c.png)

总结一下，为了从事件日志中得到正确结果，我经过了如下步骤：

1、解码Unicode base64代码。

2、解码嵌套的base64代码。

3、解压解码后的base64代码。

<br>

**三、总结**

****

从上面这三个例子中，我们可以看到，攻击者可能会使用各种技术来混淆他们的PowerShell攻击代码。这些技术可以组合使用，其中一些用法我已经在上面例子中介绍过。对于每种情况，所采取的步骤往往也各不相同。我经常会看到每种案例会对应2到3种变化，并且会在几个月的时间内蔓延到数百个系统中。某些情况下，我们所需要使用的步骤可能为：base64、base64、解压、shellcode，也有可能是base64、解压、base64、明文代码、base64、shellcode。这种情况是不是与俄罗斯套娃非常类似？在完成这一系列文章后，我会介绍如何自动化处理这个过程。如果你使用过类似Harlan Carvy的时间线脚本来获取文本输出结果，那么整个过程处理起来会非常简单。

[![](https://p2.ssl.qhimg.com/t018ede61dc5f4b4a1a.png)](https://p2.ssl.qhimg.com/t018ede61dc5f4b4a1a.png)

因此，我们如何在自己的环境中定位并解码这些脚本？可以使用如下步骤：

1、查找带有%COMSPEC%、powershell.exe、-encodedcommand、-w hidden、"From Base64String"之类特征的7045事件。

2、查找诸如Gzipstream或者[IO.Compression.CompressionMode]::Decompress之类的特征字符串，可以帮助我们了解代码所使用的压缩方法。

3、尝试使用sdbg.exe、shellcode2exe或其他恶意软件分析工具来分析得到的二进制文件。

在Part 2中，我会介绍注册表中的PowerShell代码，在Part 3中，我会介绍如何记录PowerShell日志，以及如何从内存中提取相关信息。
