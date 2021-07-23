> 原文链接: https://www.anquanke.com//post/id/216999 


# 某办公软件PDF阅读器漏洞挖掘及Crash分析


                                阅读量   
                                **224754**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01f4a9b3c4f9ce5f88.png)](https://p5.ssl.qhimg.com/t01f4a9b3c4f9ce5f88.png)



作者：维阵漏洞研究员 lawhack

## 摘要：

本文主要讲述如何利用winafl对***pdf阅读器程序进行漏洞挖掘的过程。



## 准备:

• winafl、DynamoRIO

• ***pdf（11.6.0.8537）32位

• 测试环境：win7 32位、4G内存、4核cpu



## 寻找合适的偏移函数

我在看***pdf的程序目录时，找到和pdf相关的dll仅有pdfmain.dll，大致分析，应该是将开源的pdf库pdfium打包了进去，但无法确定库的版本，同时也无法确定是否经过该办公软件官方修改，因此无法找到独立的库文件进行fuzz。所以最终我选择对***pdf.exe主程序进行fuzz。
1. 利用winafl对windows程序进行漏洞挖掘，关键是找到合适的函数位置进行插桩，便于winafl进行可重复的fuzz测试。根据winafl的官方说明，函数偏移需要满足以下条件：
1. 打开输入文件。打开文件操作必须在选定的函数内部执行，这样当winafl迭代测试时可以重写输入文件，程序每次读取的都是经过变异后的文件。
1. 解析输入文件。（这样便于衡量程序的覆盖率）
1. 关闭输入文件。这点非常重要，如果没有关闭文件，winafl将无法重写文件。
1. 函数能够在无交互的情况下运行到返回处。
在没有源码的情况下，我们可以通过逆向分析的手段来找到一个恰当的函数位置进行插桩。

首先通过process monitor，来大致确认***pdf打开和读取pdf文件时大致的函数位置，如下图所示：

[![](https://p4.ssl.qhimg.com/t0199e9df734db62ffe.png)](https://p4.ssl.qhimg.com/t0199e9df734db62ffe.png)

查看调用栈如下：

[![](https://p1.ssl.qhimg.com/t019f8092edad6e6cf0.png)](https://p1.ssl.qhimg.com/t019f8092edad6e6cf0.png)

查看模块基址如下：

[![](https://p4.ssl.qhimg.com/t01e9ee68693fdf3b95.png)](https://p4.ssl.qhimg.com/t01e9ee68693fdf3b95.png)

因此可以确定调用CreateFileW时的函数调用地址为0x104bcb9c，关键位置处于pdfmain.dll中，利用ida打开，代码如下：

[![](https://p3.ssl.qhimg.com/t0156e895328d9a6201.png)](https://p3.ssl.qhimg.com/t0156e895328d9a6201.png)

接着看下ReadFile的函数操作：

[![](https://p4.ssl.qhimg.com/t01dc86df78992b8df3.jpg)](https://p4.ssl.qhimg.com/t01dc86df78992b8df3.jpg)

[![](https://p0.ssl.qhimg.com/t012febc37ef61b4211.png)](https://p0.ssl.qhimg.com/t012febc37ef61b4211.png)

[![](https://p5.ssl.qhimg.com/t011977e15fe0d10f00.png)](https://p5.ssl.qhimg.com/t011977e15fe0d10f00.png)

我们看到从偏移0x389130处下面的函数调用都相同，能够判断出在该函数内部进行了对文件的打开和读取操作，因此可以考虑在该函数以及后面的函数作为选取的函数偏移。



## 进行debug模式测试

这里考虑将0x765F93处的函数头部

0x765f00作为选定的函数偏移，利用以下命令进行测试：

效果如下：

[![](https://p5.ssl.qhimg.com/t01f820e61d05f8b879.jpg)](https://p5.ssl.qhimg.com/t01f820e61d05f8b879.jpg)



## 利用winafl-cmin精简样本

我们接下来利用winafl-cmin.py对样本进行精简，命令如下：

结果如下，200多个文件最终保留了15个。

[![](https://p4.ssl.qhimg.com/t01b34c2db6b5e23491.png)](https://p4.ssl.qhimg.com/t01b34c2db6b5e23491.png)



## 利用winafl进行fuzz测试

命令如下：

但是出现了一些问题，如下图：

[![](https://p0.ssl.qhimg.com/t01c1a48af4589c607b.png)](https://p0.ssl.qhimg.com/t01c1a48af4589c607b.png)

为什么程序被处理掉呢，深入分析后，我发现winafl无法重写测试文件即.cur_input，原因是在我们选择的函数内部并没有主动关闭文件导致没有释放句柄，所以winafl就无法重写文件，这导致winafl必须主动关闭掉程序来进行新样本的测试。

那么***pdf在什么时候会关闭文件呢，通过分析发现只有用户主动点击X图标时***pdf才会关闭文件，因此在***pdf打开的文件中，是不允许对文件进行修改的。这给fuzz带来一些困扰，根据winafl的说明，如果发现fuzz效率低下，则可能需要修改winafl源码或者对程序进行patch来提高不关闭文件句柄时的fuzz效率。

当然，目前还有其它的方法，比如发现有的人会通过一些autoit脚本来主动识别打开文件时的窗口，并立即关闭，这样似乎也可以，相当于通过脚本自动化的关闭窗口。但是在实际过程发现，在我们选择的函数中还并没有对窗口进行绘制，因此就无法获取窗口句柄，关闭窗口了。因此为了提高效率，我们可以从以下两方面入手：
1. patch系统调用，对CreateFile、ReadFile、WriteFile等和文件读写的系统调用进行patch，比如说，CreateFile判断读取的文件名称，是否是fuzz时的输入文件名称，如果是，则保留句柄，在ReadFile、WriteFile时判断传入的句柄是否为输入文件的句柄，如果是，则将特定数据内容返回，而不走系统自身调用。这样避免了已经打开的文件无法重写的问题。
1. patch目标程序，在选择的函数偏移内部找一块可读、可执行的区域添加保存句柄、释放句柄的代码。这样实现了在函数内部自动关闭文件的操作。
这里仅仅修改winafl源码是无法解决问题的，不过可以修改代码来进行配合以提高fuzz效率，比如每次生成变异的文件无需写入磁盘，而是直接向特定的区域写入，这样少了系统api的调用，应该可以快上不少。

为了防止修改系统调用后影响过大而造成其他问题，我选择patch***pdf目标程序。在调试时找到一块可利用的地址，但是发现是系统出于内存对齐而申请的，文件中并不存在，因此只能通过添加区段的方式来添加新的利用代码了。

我通过studype这个软件来添加区段，并且设置区段属性为可读、可写、可执行，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01538928bab98523bb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ca8086fc3029b860.png)

一般来说，在CreateFile函数后添加代码将输入文件的句柄进行保存，那么就需要解决另外一个问题：在哪里关闭句柄是恰当的。我通过不断的测试发现在特定的函数后关闭句柄，并不会影响整个pdf文件的读取和解析，pdf文件内容可以正常输出到显示器上。添加的代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f833de4a2dc00f14.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f199ec5f6b71bed0.png)

由于执行CreateFile的操作不只一次，因此需要提前进行判断，只保留输入文件的句柄。对patch后的程序进行fuzz，效率果然提升了不少，测试效果如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d556eae3fb93100d.png)

但是在fuzz过程中，由于winafl变异样本导致pdf格式不正确，因此***pdf会弹窗说明：

[![](https://p3.ssl.qhimg.com/t01588681be86724bcf.jpg)](https://p3.ssl.qhimg.com/t01588681be86724bcf.jpg)

此时winafl会卡住，这会极大地降低fuzz的速率，一般来说通过post library的方式修改pdf文件头部为%PDF-1.4，可以解决一部分的文件格式问题，还有一部分是不符合整个pdf的文件结构导致的，这时只修改头部是没什么用的。不过要解决这个问题，其实只要让它不弹窗就好了。我们可以利用调试器调试***pdf打开文件的过程，当弹窗messagebox后，中断程序，切换到0号线程，即可观察到弹框时的函数调用栈，如下：

[![](https://p1.ssl.qhimg.com/t015946eb98723946e3.png)](https://p1.ssl.qhimg.com/t015946eb98723946e3.png)

查看函数rva如下：

[![](https://p1.ssl.qhimg.com/t011fa3e58e3882f01d.png)](https://p1.ssl.qhimg.com/t011fa3e58e3882f01d.png)

因此将该处的代码patch即可，尽量不要修改程序的逻辑，如下：

[![](https://p3.ssl.qhimg.com/t0120c167f327cf1d8c.png)](https://p3.ssl.qhimg.com/t0120c167f327cf1d8c.png)

这样的话即使程序检测到文件格式不正确时也不会弹窗，进而影响fuzz速度了。但是这里遇到另外一个问题涉及到了数据重定位，由于patch的地方保存着重定位的数据，因此必须手动修复。首先通过studype查看程序的重定位表，定位到具体的代码段的rva处，查看对应重定位数据的索引，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01844252861e1507ab.png)

接着通过010editor打开pdfmain.dll，利用pe的模板对文件进行解析，如下：

[![](https://p1.ssl.qhimg.com/t019dda733594dd1c73.png)](https://p1.ssl.qhimg.com/t019dda733594dd1c73.png)

将对应块的内容改为其它地址或者0，就不会对原有的数据进行重定位了，不然nop后的汇编代码会被修改为重定位后的值，导致程序执行异常。但是这里有一个隐患，为了提高漏洞的检测能力，通过gflags开启page heap，这样就能够检测堆的漏洞了。后面确实触发了一个uaf漏洞，经过深入调试分析发现，是因为程序在检测到文件格式错误后，会主动关闭文件句柄，而我们自身又关闭了一次，这就导致程序的逻辑出现了一些问题，最终触发了uaf。

因此为了修复这个问题，定位到了程序在检测到文件格式不正确后主动关闭文件句柄处的函数地址，再次patch，添加代码，让程序不会多次关闭句柄，进而让程序能够正常运行。

经过一段时间的fuzz后，出现了一些crash，我们接下来针对crash进行分析。

[![](https://p3.ssl.qhimg.com/t01d72b9bd81a2dfd7d.png)](https://p3.ssl.qhimg.com/t01d72b9bd81a2dfd7d.png)



## crash分析

经过粗略的分析发现这次的漏洞是一个uaf漏洞，崩溃现场如下：

[![](https://p1.ssl.qhimg.com/t01ff28c97e64473e17.png)](https://p1.ssl.qhimg.com/t01ff28c97e64473e17.png)

可以看到ecx指向的内存地址是不可访问的，由于开启了page heap，可以查看该内存块的释放位置，利用命令!heap -p -a ecx，显示如下：

[![](https://p0.ssl.qhimg.com/t0145b7334faac13719.png)](https://p0.ssl.qhimg.com/t0145b7334faac13719.png)

虽然知道了释放堆的地址，但我们无法获取堆块的内容，同样也不清楚申请该堆的作用是什么，在什么地方申请的。虽然可以通过调试时在free的地方下断点进行分析，但实际分析时发现该处释放堆块的次数非常多，难以确认具体的释放触发uaf漏洞的堆块的时机，因此我们可以通过简单的windbg脚本来获取释放堆块时的具体数据，以方便进行对照。脚本命令如下：

搜索找到了free前的堆块数据，如下所示：

[![](https://p3.ssl.qhimg.com/t01b6562169e8900bbc.png)](https://p3.ssl.qhimg.com/t01b6562169e8900bbc.png)

跟踪下malloc后的程序行为，发现是将pdf obj中的数据保存在该堆块中，如上图中的数据0x2068，其实是pdf obj的length数据，如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0124983c72ba8f8db2.png)

将8296字符串转换为16进制数据保存到该堆中，申请以及数据存储函数如下：

[![](https://p2.ssl.qhimg.com/t01baa659e347fb8e31.png)](https://p2.ssl.qhimg.com/t01baa659e347fb8e31.png)

[![](https://p1.ssl.qhimg.com/t018ef8b3c9120ae0fd.png)](https://p1.ssl.qhimg.com/t018ef8b3c9120ae0fd.png)

[![](https://p0.ssl.qhimg.com/t012778ee135c988ad2.png)](https://p0.ssl.qhimg.com/t012778ee135c988ad2.png)

随后，又将该指针保存在多处，函数如下：

[![](https://p3.ssl.qhimg.com/t0171c63a185aa2bc50.png)](https://p3.ssl.qhimg.com/t0171c63a185aa2bc50.png)

整个程序的执行流程如下：

首先在函数0x10479DF0中处理对pdf内容的解析，申请堆内存保存相关数据；

[![](https://p4.ssl.qhimg.com/t015e42e57b4c2bdd34.png)](https://p4.ssl.qhimg.com/t015e42e57b4c2bdd34.png)

接着在函数0x1043a7b0中释放资源；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01009cee7646e7148c.png)

而保存length内容的指针在多个地方均有引用，首次释放在这里：

[![](https://p3.ssl.qhimg.com/t01bc598e4e76638a5a.png)](https://p3.ssl.qhimg.com/t01bc598e4e76638a5a.png)

接下来释放保存有uaf指针的多个指针，结构如下：

[![](https://p4.ssl.qhimg.com/t01b8e010abbebfc28a.png)](https://p4.ssl.qhimg.com/t01b8e010abbebfc28a.png)

随后会对释放后指针的首4字节内容进行判断，就触发了uaf漏洞。

[![](https://p4.ssl.qhimg.com/t016af9a6d683282092.png)](https://p4.ssl.qhimg.com/t016af9a6d683282092.png)



## 修复建议

该漏洞产生的原因是将多个指针指向同一块内存区域，但是在释放内存后，并没将所有指向该内存的指针指向null，产生了野指针，在后面对野指针的访问造成程序异常。因此建议在开发阶段排查野指针问题，或者使用更加安全的智能指针进行代替。



## 改进

后续在fuzz过程中，我发现很难产生新的路径，虽然说整个程序的运行速度很快，但是每次都是在一次完整的迭代测试后，kill掉进程重新测试时才会产生新的路径。这种情况有可能是由于patch程序造成的，为了了解产生这种情况的原因，我们需要再次对程序进行分析。

通过drrun.exe监控下patch后程序的运行状况，结果如下：

[![](https://p5.ssl.qhimg.com/t01c1da771ba218c09a.png)](https://p5.ssl.qhimg.com/t01c1da771ba218c09a.png)

可以看出，除了第一次外，***pdf会读取输入文件，后面的迭代测试中并没有对输入进行读取和解析，因此此时的fuzz效率本质上还是非常低的，虽然它的速度非常快，但是***pdf并没有对后续的输入进行解析，这就导致发现新路径的速度非常的慢。

在解决这个问题之前，我们必须了解清楚***pdf对后续的输入没有读取的原因。

通过测试发现，***pdf程序无法打开同一个位置的同名文件，由于patch了pdfmain.dll，这让我们可以在***pdf加载输入文件后随意修改输入文件名称和内容，在将文件名称修改后，***pdf就可以继续打开输入文件了，本质上它们是同一个文件。我们可以确定两点，第一点是***pdf内部有判断机制，即不会重复打开相同的文件路径；第二点是该判断机制的代码的大概区间，就在我们patch代码的函数地址到读文件的函数地址之间。

通过动态调试，找到该判断处位于函数0x107b0e90，如下：

[![](https://p5.ssl.qhimg.com/t0101ee1559c4167ddf.png)](https://p5.ssl.qhimg.com/t0101ee1559c4167ddf.png)

当该函数返回值非0时，说明此时的文件已经在***pdf中被打开，***pdf就不会第二次打开该pdf，因此让该函数直接返回0后退出即可。patch过后再次利用drrun.exe查看程序的执行效果，如下：

[![](https://p2.ssl.qhimg.com/t01c7d58ae8dcc2eb22.png)](https://p2.ssl.qhimg.com/t01c7d58ae8dcc2eb22.png)

可以看出，在每次迭代测试中均会对输入文件进行打开和解析，这样就可以进一步的fuzz了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f10909119404fff4.png)

如上所示，虽然程序fuzz速度变慢，但是发现新路径的速度反而快了很多。后续我将继续思考如何提高fuzz效率的相关问题，详细内容敬请期待。
