> 原文链接: https://www.anquanke.com//post/id/83205 


# ​FLARE脚本系列：自动解码混淆字符串


                                阅读量   
                                **87211**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2015/12/flare_script_series.html](https://www.fireeye.com/blog/threat-research/2015/12/flare_script_series.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01a7b23425d0322967.png)](https://p0.ssl.qhimg.com/t01a7b23425d0322967.png)

**介绍**

我们的脚本系列已经不仅限于IDA Pro了。这篇文章将会给大家介绍有关FireEye实验室高级逆向工程(FLARE)脚本的内容，该脚本可用于逆向工程调试器（这是一个非常棒的调试器）。与IDA Pro类似，调试器debugger也有脚本接口。比如说，OllyDbg使用的是类asm的脚本语言，其Immunity调试器包含有Python接口，而且Windbg也有其自身的脚本编程语言。但是所有的这些选项并不适合快速创建字符串解码的调试脚本。对于Immunity和OllyDbg而言，这两者仅仅支持32位的程序，而Windbg的脚本编程语言是专用于Windbg的。[pykd](https://pykd.codeplex.com/)项目所提供的接口支持Python和Windbg，它可以允许开发者使用Python语言来编写调试器的脚本程序，因为恶意软件的逆向工程师大多都喜欢Python。

我们公布了一个代码库，在此我们称其为flare-dbg。这个库所提供的几个实用的类和功能函数可以允许开发者快速编写能够使Windbg自动进行调试任务的脚本。如果你对此感兴趣的话，请持续关注我们的博客，我们将会提供更多有关debugger脚本的信息。

**字符串解码**

恶意软件的编写人员需要通过混淆代码中的字符串以达到隐藏恶意软件意图的目的。因此，如果你能够快速地对字符串进行反混淆，那么你就可以快速地发现那些恶意软件的真正目的了。

正如我们在《[恶意软件分析实践](http://practicalmalwareanalysis.com/)》一文中提到的，通常有两种反混淆字符串的方法：自解码以及手工编程。自解码方法可以让恶意软件自己解码其代码中的字符串。手工编程需要逆向工程师重新对解码函数进行编程。自解码方式的其中一种就是模拟（仿真），程序会对程序指令集合进行模拟运行。不幸的是，我们还需要模拟代码库的调用，但模拟每一个代码库的调用过程是非常困难的，而且还会导致分析结果不准确。相反，debugger能够对代码的实际运行过程进行分析，这样一来，所有的库函数都可以正常运行。上述的这些方式都有其用武之地，但这篇文章的重点是告诉大家如何使用编译器脚本来对所有经过混淆的字符串进行自动解码。

**当前的挑战**

为了解码所有的混淆字符串，我们需要找到下列信息：字符串解码函数，每次调用它的时间，以及每个实例的所有参数。然后我们还需要运行这个函数，并且记录所有的运行结果。难度和挑战就在于，我们必须采用半自动化的方法来完成这些操作。

**方法**

当前，我们的首要任务就是找到字符串解码函数，并且对该函数进行基本的了解，例如其输入和输出参数等。下一个任务就是验证这个字符串解码函数的调用时间，以及每次调用所需要的全部参数。在不使用IDA的情况下，最实用的工具就是[Vivisect](https://github.com/vivisect/vivisect)（一个Python项目，可用于二进制代码的分析）。Vivisect包含几种启发式算法，可用于验证函数和交叉引用。除此之外，Vivisect还可以进行模拟和分解一系列操作码，这将有助于我们对函数参数进行分析和验证。如果你还没有做好准备，那么我建议你查看一下FLARE脚本系列教程的[相关文章](https://www.fireeye.com/blog/threat-research/2015/11/flare_ida_pro_script.html)，文章中同样会使用到Vivisect。

**flare-dbg介绍**

这次，FLARE团队给大家带来的是一个Python项目，即基于pykd的flare-dbg。该项目的目标就是让Windbg脚本编程变得更加简单。flare-dbg项目的精髓就是DebugUtils类，这个类包含有几个非常重要的功能：

l   内存和寄存器操作

l   堆栈操作

l   调试执行

l   断点

l   函数调用

除了调试器所需的基本功能函数之外，DebugUtils类还可以利用Vivisect来操作二进制代码的分析部分。

**举例说明**

我编写了一小段简单的恶意软件，并且通过编码来隐藏了其中的字符串。在图片1中，我使用了一个名为string_decoder的函数来解码HTTP用户代理程序中的字符串。

[![](https://p0.ssl.qhimg.com/t01aeacc7cfa9a63605.png)](https://p0.ssl.qhimg.com/t01aeacc7cfa9a63605.png)

图片1:字符串加码函数

在粗略地看了一下string_decoder函数之后，可以发现其中有下列几个参数：编码字符串的字节偏移量，输出地址，以及长度等信息。这个函数用C语言可以表示成下图所示的函数形式：

[![](https://p4.ssl.qhimg.com/t01c1ba2a4f59060c84.png)](https://p4.ssl.qhimg.com/t01c1ba2a4f59060c84.png)

既然我们已经对string_decoder函数有了一个大致的了解了，那么我们就可以开始使用Windbg和flare-dbg来测试解码功能了。首先，我们需要运行Windbg，然后在Windbg中开启Python的交互接口（shell），然后导入flaredbg。此时，你应该得到类似下图的界面：

[![](https://p5.ssl.qhimg.com/t01d2849f0c94d24ca5.png)](https://p5.ssl.qhimg.com/t01d2849f0c94d24ca5.png)

接下来，我们创建一个DebugUtils对象，该对象包含有一个函数，我们在控制调试器的时候将会用到它。

[![](https://p4.ssl.qhimg.com/t0152293852b13bfd02.png)](https://p4.ssl.qhimg.com/t0152293852b13bfd02.png)

当然了，我们还需要为输出字符串分配一个大小为0x3A字节的内存空间。然后使用新分配的内存来进行参数配置。

[![](https://p4.ssl.qhimg.com/t01d3e78937565b9bc4.png)](https://p4.ssl.qhimg.com/t01d3e78937565b9bc4.png)

最后，我们调用string_decoder函数，其虚拟地址为0x401000，然后读取输出字符串的缓冲区数据。

[![](https://p1.ssl.qhimg.com/t01a4d6556e2955504a.png)](https://p1.ssl.qhimg.com/t01a4d6556e2955504a.png)

上述操作完成之后，我们就可以用flare-dbg来对字符串进行解码了。图片2显示的就是调试器脚本的一个实例。完整的脚本代码可以在我们的Github代码库中获取到。

[![](https://p2.ssl.qhimg.com/t010e7c26310dab7c7a.png)](https://p2.ssl.qhimg.com/t010e7c26310dab7c7a.png)

图片2:调试器脚本的实例

接下来，让我们对脚本代码进行详细的分析。

首先，我们得确定字符串解码函数的虚拟地址，然后创建DebugUtils对象。接下来，我们使用DebugUtils类的函数get_call_list来得到string_decoder函数在每次调用时所需要的参数。

当call_list生成之后，我们就可以对所有的调用地址和进行迭代并组合参数。比如说，输出字符串将会被解码至堆栈。因为我们只执行了字符串解码函数，但恶意软件中并没有配置同样的堆栈，所以我们必须为输出字符串分配内存。我们所需要的第三个参数为length（长度），用于制定内存分配的大小。当我们成功为输出字符串分配了内存之后，我们就可以将最新分配的内存地址作为第二个参数传入函数中。

最后，我们可以通过DebugUtils类的调用函数来调用string_decoder函数。当所有的字符串成功解码之后，最后一步就是读取这些字符串。

运行调试器脚本，便能够得到下列输出结果：

[![](https://p2.ssl.qhimg.com/t0126831a43687744a7.png)](https://p2.ssl.qhimg.com/t0126831a43687744a7.png)

所有的解码字符串以及地址下图片3所示：

[![](https://p0.ssl.qhimg.com/t018a1ec82fa8227d92.png)](https://p0.ssl.qhimg.com/t018a1ec82fa8227d92.png)

图片3：解码字符串

**总结**

请持续关注我们有关调试器脚本的文章，我们还会对相关的功能插件进行介绍！现在，你就可以访问Github主页，并访问[flare-dbg页面](https://github.com/fireeye/flare-dbg)来开始你的实践。该项目将会用到[pykd](https://pykd.codeplex.com/),[winappdbg](http://winappdbg.sourceforge.net/)，以及[vivisect](https://github.com/vivisect/vivisect)。
