> 原文链接: https://www.anquanke.com//post/id/245527 


# 如何将二进制数据隐藏到VB6可执行代码中


                                阅读量   
                                **48284**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者avast，文章来源：decoded.avast.io
                                <br>原文地址：[https://decoded.avast.io/davidzimmer/binary-data-hiding-in-vb6-executables/](https://decoded.avast.io/davidzimmer/binary-data-hiding-in-vb6-executables/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01859b2447455851d7.png)](https://p1.ssl.qhimg.com/t01859b2447455851d7.png)



本文是这个系列文章的第一篇，这里的重点是理解Visual Basic 6.0 (VB6)代码，以及恶意软件作者和研究人员针对VB6所用的常见策略和技术。 



## 摘要

本文涵盖了VB6恶意软件在可执行文件中嵌入二进制数据的常见方式，它们大体可以分为4个主要类别：
1. 基于字符串的编码技术； 
1. 将数据隐藏在程序的实际操作码中； 
1. 将数据隐藏在VB6文件格式中；
1. 将数据隐藏在正常PE结构内或周围。 
最初，我只打算讨论如何将数据隐藏在文件格式本身中，但出于文档完备性的考虑，我认为有必要介绍所有数据隐藏方式。

在我看来，在文件格式中隐藏数据是一种特别有趣的方式。这是因为，它可以将数据穿插在一组复杂的、未公开的结构体中，因此，要想检测这些数据，就要求相关人员掌握先进的知识和复杂的解析方法。在这种情况下，很难确定数据来自何处，甚至很难确认这些缓冲区是否存在。 



## 资源数据

第一种技术利用了语言本身内置的标准技术，即从资源段加载数据。实际上，VB6还附带了一个外接程序，用户可以通过它向项目中添加一个.res文件。该文件被编译到可执行文件的资源段，同时，该文件还可以轻松加载二进制数据。

[![](https://p5.ssl.qhimg.com/t019e51de4fbe1f40df.png)](https://p5.ssl.qhimg.com/t019e51de4fbe1f40df.png)

实际上，这是一种众所周知的标准技术。 



## 附加数据

这种技术是非常古老的，已经被各种编程语言所采用。我们将再次提及该技术，以使其更加全面，并链接到一个允许简化使用的公共实现[1]。

[![](https://p3.ssl.qhimg.com/t01ae24a7e646f31a83.png)](https://p3.ssl.qhimg.com/t01ae24a7e646f31a83.png)



## 十六进制字符串缓冲区

恶意软件通常会构建一串十六进制字符，然后将其转换回二进制数据。这里的转换过程通常包括各种文本操作，例如解密或剥离垃圾字符序列。这些额外的字符序列通常用于阻止AV将数据自动识别为十六进制字符串。

在VB6的背景下，这里存在多种限制。首先，IDE只允许在一行最多出现1023个字符。另外，VB的续行语法&amp;_也只限于25行。由于这些原因，您通常会看到以以下格式嵌入的大块数据：

[![](https://p1.ssl.qhimg.com/t014312fbc20e48dfa5.png)](https://p1.ssl.qhimg.com/t014312fbc20e48dfa5.png)

在一个已编译的二进制文件中，每个字符串片段都是作为一个单独的块来保存的，这很容易识别。一个更快的变体可以将每个元素保存在一个字符串数组中，这种方式的好处是，聚合操作只执行一次即可。 

这是一种众所周知的标准技术，常见于使用VBA、VB6以及其他语言编写的恶意软件中。需要注意的是，行长限制无法通过命令行编译绕过。



## 隐藏在图像中的二进制数据

我们知道，有多种方法可以将数据无损嵌入到图像格式中。其中，最常见的方法，就是将数据直接嵌入位图图像的结构中。位图可以直接保存在VB6的图像和Picture控件中。需要注意的是，以这种方式嵌入的数据，在编译前将被保存在.FRX表格资源文件中。一旦编译完成，这些数据将被保存到目标窗体元素的二进制属性字段中。像这样的图像可以用一个特殊的工具生成，然后用IDE直接嵌入到表单中。

下面是一个从这种位图中提取数据的公开样本[2]。

[![](https://p0.ssl.qhimg.com/t0172b178cb8a2a8640.png)](https://p0.ssl.qhimg.com/t0172b178cb8a2a8640.png)

提取的图像将显示为一系列的彩色块和各种颜色的像素。请注意，这不是隐写术。

许多工具到知道如何从二进制文件中提取嵌入的图像。由于图像数据仍然包含BITMAP头，因此不需要解析VB6文件格式本身。需要说明的是，这种技术是公开的，而且已经得到了普遍使用。数据在提取后，通常还需要进行解密。



## Chr字符串

与C语言恶意软件中的混淆方法类似，字符串可以在运行时根据单个字节值生成，具体如下例所示：

[![](https://p3.ssl.qhimg.com/t01285be6e8ae455f3d.png)](https://p3.ssl.qhimg.com/t01285be6e8ae455f3d.png)

在asm语言级别，这有助于拆分字节值，并将其与操作码放在一起，防止自动检测或显示为字符串。对于本地VB6代码来说，它看起来像下面这样：

[![](https://p5.ssl.qhimg.com/t0107b3fad609cba6e0.png)](https://p5.ssl.qhimg.com/t0107b3fad609cba6e0.png)

在P-Code中，它看起来像下面这样：

[![](https://p4.ssl.qhimg.com/t01b2c10d6557ea12d9.png)](https://p4.ssl.qhimg.com/t01b2c10d6557ea12d9.png)

这是一种众所周知的标准技术，常见于使用VBA和VB6语言编写的恶意软件中。 



## 数值数组

数值数组是恶意软件中的一种相当标准的技术，用于拆分程序操作码中的二进制数据。它类似于Chr技术，不同之处在于，它能够以更紧凑的格式保存数据。这种技术最常用的数据类型是4字节的long类型，和8个字节的currency类型。这种技术的主要优点是，数据易于通过数学方法进行处理，从而实现即时解码。

[![](https://p3.ssl.qhimg.com/t01988dacb97c418159.png)](https://p3.ssl.qhimg.com/t01988dacb97c418159.png)

本地代码：

[![](https://p0.ssl.qhimg.com/t011a14bddbe09d1435.png)](https://p0.ssl.qhimg.com/t011a14bddbe09d1435.png)

P-Code：

[![](https://p3.ssl.qhimg.com/t01c9728267f0b6befa.png)](https://p3.ssl.qhimg.com/t01c9728267f0b6befa.png)

[![](https://p1.ssl.qhimg.com/t015b3f408d404316b0.png)](https://p1.ssl.qhimg.com/t015b3f408d404316b0.png)

本地代码：

[![](https://p4.ssl.qhimg.com/t01549f187c2da0f7eb.png)](https://p4.ssl.qhimg.com/t01549f187c2da0f7eb.png)

P-Code： 

[![](https://p2.ssl.qhimg.com/t010efb5193d73e7b05.png)](https://p2.ssl.qhimg.com/t010efb5193d73e7b05.png)

尽管这种技术不像其他技术那样流行，但应用历史也很长了。就我而言，第一次看到它是在Flash ActionScript的漏洞中。



## 表单属性

表单和嵌入式GUI元素可以将编译后的数据保存到其属性中。其中，最常用的属性是Form.Caption、Textbox.Text以及各种元素的.Tag属性。

由于所有这些属性通常都是通过IDE输入的，因此，我们通常会发现其中仅包含ASCII数据，这些数据后来会解码为二进制形式。

然而，开发人员也可以通过各种技术将二进制数据直接嵌入到这些属性中。 

虽然可以直接对.FRX表单资源文件中的原始数据进行十六进制编辑，但这会面临许多限制，例如无法处理嵌入的空值。另一种解决方案是在编译后插入数据。通过这种技术，将预留一个由ASCII文本组成的大缓冲区，该缓冲区具有相应的起始和结束标记。然后，我们可以在编译后的可执行文件上运行嵌入工具，用真正的二进制数据填充缓冲区。 

使用表单元素属性来存放基于文本的数据也是一种常见的做法，在VBA、VB6、甚至PDF脚本中都可以看到这种用法。目前，研究人员已在野外观察到嵌入了后处理步骤的二进制数据。在P-Code和本地代码中，对这些属性的访问可以通过COM对象VTable完成。 

在Semi-VBDecompiler的源码中，每种不同的控件类型（包括ActiveX）都有自己的解析器，用于解析这些编译后的属性字段。如果所使用的工具能够显示数据，其结果会有所不同。此外，Semi-Vbdecompiler还提供了一个选项，可以将属性Blobs转储到磁盘上供人工探索。有时候，人工分析是揭示这种类型的嵌入式二进制数据所必需的。 



## 用户控件属性

在上述技术中，有一个特例，那就是内置的UserControl类型。这个控件用于托管可重用的视觉元素和创建OCX。该控件有两个事件，它们被传递给一个包含其内部二进制设置的PropertyBag对象。这种二进制数据可以在IDE中通过属性页轻松设置。这种机制可以用来存储任何种类的二进制数据，包括整个文件系统。关于这种技术的公开样本，请参阅[3]。需要注意的是，嵌入的数据将保存在宿主表单UserControl的每个实例的属性中。

[![](https://p1.ssl.qhimg.com/t01e0b54b5161e39e04.png)](https://p1.ssl.qhimg.com/t01e0b54b5161e39e04.png)



## 二进制字符串

编译后的VB6可执行文件会保存带有长度前缀的内部字符串。与表单属性的技巧类似，这些条目可以在编译后进行修改，以包含任意的二进制数据。为了将这些数据块与其他二进制数据区分开来，必须对VB6文件格式具有深入的理解并进行复杂的解析。 

用这种技术可以嵌入的最长字符串受限于IDE中的行长，即2042字节。

基于VB6的恶意软件可以正常访问这些字符串，并且无需使用特殊的加载程序：相关的源代码就是str = “binary data”。 

IDE可以处理大量unicode字符，而这些字符可以被嵌入到源代码并进行编译。另外，完整的二进制数据可以使用后处理技术（post processing technique）来嵌入。



## 错误行号

VB6允许开发人员嵌入行号，这样的好处是：在发生错误时，可以通过这些行号帮助确定出错的位置。这个错误行号信息被存储在字节码流之外的一个单独的表中。 

错误行号可以通过Erl()函数进行访问。VB6对每个函数的行号限制为0xFFFF，行号值必须在0-0xFFFF范围内。由于使用这种技术时，嵌入数据的大小受到限制，因此，这种方法仅适用于短字符串，如密码和网址等。

当运行下面的代码时，它将输出“secret”：

[![](https://p0.ssl.qhimg.com/t01df36bb092ee88c1f.png)](https://p0.ssl.qhimg.com/t01df36bb092ee88c1f.png)

需要注意的是，只有具备VB6文件格式的高级知识，才能将这种数据与文件的其他部分区分开来。如果不进行其他方式的编码处理的话，嵌入的数据将是连续的和可读的。 



## 函数体

利用AddressOf操作符，VB6可以在运行时轻松访问模块中公共函数的地址。我们可以在可执行文件的.text段中加入一个仅含占位符指令的dummy函数，以创建一个空白缓冲区。这个缓冲区可以通过调用CopyMemory轻松加载到一个字节数组中。之后，我们可以使用简单的后期编译嵌入技术来填充任意数据。

[![](https://p0.ssl.qhimg.com/t0141feb321cb7ccc26.png)](https://p0.ssl.qhimg.com/t0141feb321cb7ccc26.png)

对于P-Code编译，AddressOf会返回一个带有结构体偏移量的加载器存根的偏移位置。尽管P-Code编译还需要几个额外的步骤，但仍然是可以实现的。 



## 参考资料

[1] Embedded files appended to executable – theTrik:

https://github.com/thetrik/CEmbeddedFiles

[2] Embedding binary data in Bitmap images – theTrik:

http://www.vbforums.com/showthread.php?885395-RESOLVED-Store-binary-data-in UserControl&amp;p=5466661&amp;viewfull=1#post5466661

[3] UserControl binary data embedding – theTrik:

https://github.com/thetrik/ctlBinData
