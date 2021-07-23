> 原文链接: https://www.anquanke.com//post/id/87231 


# 【病毒分析】Ordinypt恶意软件分析报告


                                阅读量   
                                **102107**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：29wspy.ru
                                <br>原文地址：[http://29wspy.ru/reversing/Ordinypt/Ordinypt.pdf](http://29wspy.ru/reversing/Ordinypt/Ordinypt.pdf)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t0175c2bab5b2ba28eb.png)](https://p4.ssl.qhimg.com/t0175c2bab5b2ba28eb.png)**

译者：[eridanus96](http://bobao.360.cn/member/contribute?uid=2857535356)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**



近期，出现了一个新的勒索病毒，被称为“Ordinypt”，其目标主要针对于德国用户。我们对这个恶意软件进行了分析，并进行了逆向工作，以研究该病毒的工作原理。

Ordinypt表面上是一个勒索病毒，会向受感染的用户勒索金钱，以解密文件。但我们发现，它实际上是一个清扫器（Wiper）类型的病毒，被它加密的文件会直接被销毁，并且没有任何通过支付赎金给恶意软件作者以恢复文件的机制。

用于本次分析之中的病毒样本Hash值为**3ba3272977dfe0d1a0c48ef6cb9a06b2**。接下来让我们开始分析该样本。



**恶意软件分析<br>**

****

第一步，我们使用**ExeInfo**查看该恶意软件是否加壳，当然也可以使用**PeID**等工具来进行。

[![](https://p2.ssl.qhimg.com/t0129de2af6b4d4532d.png)](https://p2.ssl.qhimg.com/t0129de2af6b4d4532d.png)

根据ExeInfo的结果，**该恶意软件使用MPRESS 2.12进行加壳**，因此我们可以借助工具来进行脱壳，或者也可以尝试着手动脱壳。

为了更好地了解这个壳，我们接下来就进行手动脱壳。查看相应的Section，我们可以看到：

[![](https://p2.ssl.qhimg.com/t018bdf8f8ffe5c421a.png)](https://p2.ssl.qhimg.com/t018bdf8f8ffe5c421a.png)

第一个Section名称为“.MPRESS1”，大小为142KB；第二个Section名称为“.MPRESS2”，大小为3.5KB，最后一个Section名称为“.rsrc”，大小为100.5KB。

最后一个Section没有可执行标志（Executable flag），也就意味着它没有程序的入口点。根据ExeInfo显示的结果，入口点是在内存“0x8225D”偏移量的位置，因此我们发现，入口点是在第二个Section之中。

接下来，让我们使用Olly，对第二个Section做进一步的分析。

[![](https://p4.ssl.qhimg.com/t01fc702ea9513f5b2d.png)](https://p4.ssl.qhimg.com/t01fc702ea9513f5b2d.png)

我们接下来调试第二个Section中的代码。在调试后，全部的壳代码最终到达偏移量0x455B30。

[![](https://p1.ssl.qhimg.com/t015740b145a0cb41ec.png)](https://p1.ssl.qhimg.com/t015740b145a0cb41ec.png)

**该点即为恶意软件的起始点。**在调试过程中，我们可以使用下面这些技巧，以快速有效地对壳进行分析：

**1. ****使用硬件断点（Hardware Breakpoint）避免循环****：**

在本文的分析过程中，我们可以使用正常的断点。但是，一些程序可以使用其自身代码进行脱壳、生成密钥等操作，因此，学习使用硬件断点就变得非常重要。

在使用常规断点时，会将汇编指令“INT3”即0xCC放置在想要中断的未知的第一个字节处，随后软件执行到相应位置时，会检测到错误，并触发异常。

**2. ****注意其中的跳转，确保所有的Track都被注意到，并在这些地址中适当放置一些硬件断点，以结束循环。**

**3. ****壳往往会使用大量的调用，才能跳转到下一条指令，因此借助Track是非常必要的。**

4. 壳会从kernel32.dll中获取到一些Export，例如DeleteCriticalSection等。**如果能在GetModuleHandleA或GetProcAddress放置一个BP寄存器，可能会很有帮助。**

**5. ****在最后，壳会使用一个无条件跳转指令（JMP）来实现原始二进制在内存中的还原。**

至此，我们已经有了在内存中还原后的恶意软件，就可以对其进行dump。在偏移量0x455B30的位置，使用OllyDump（或其他）插件即可。但要注意，在dump的时候不要选择“重建IAT”（Rebuild Import）这个选项。

现在，我们就有了一个628KB的二进制文件，但还有一个问题，就是其中的IAT是错误的，我们要利用ImportREC来进行修复。

[![](https://p5.ssl.qhimg.com/t01ab3f6d04d6d552f6.png)](https://p5.ssl.qhimg.com/t01ab3f6d04d6d552f6.png)

在修复dump后，最终得到的恶意软件大小为632KB（或636KB），并且已经完成了IAT的恢复，也就意味着可以在无壳的情况下运行。

我们注意到，其中的Section依然保持着原来的名字，但这并没有关系。现在，使用IDA打开恶意软件，发现这个清扫器病毒是使用Delphi 7语言编写而成。

[![](https://p2.ssl.qhimg.com/t0100937c84dbe4f675.png)](https://p2.ssl.qhimg.com/t0100937c84dbe4f675.png)

尽管IDA可以帮助我们逆向Delphi，但建议最好还是使用**IDR（Interactive Delphi Reconstructor）**。我们使用IDR打开恶意软件，并等待代码分析的完成。

当完成后，选择“Tools -&gt; Map Generator”或者“Tools -&gt; IDC Generator”。在这里，我选择了映射文件，并且借助Olly中“加载映射（Load Map）”的插件对其进行加载，并将所有调试的内容都保存到UDD文件中，以备将来需要时使用。

**恶意软件的有效载荷是在unit1.pas文件的代码中，所以，接下来要针对名为“_Unit2.InitUnits”的函数进行调试。**在这个函数中，代码在一次大循环中调用了一个寄存器。我们需要等待进入的函数是“Unit1.Initialization”，也就是开始执行恶意代码的函数。另一个调用则属于Delphi，用于启动自己的库和单元。

[![](https://p1.ssl.qhimg.com/t01131e2fd0487a5dcc.png)](https://p1.ssl.qhimg.com/t01131e2fd0487a5dcc.png)

终于，我们到达了位于偏移量0x455194的启动恶意代码的函数。

[![](https://p0.ssl.qhimg.com/t0174e6f42f5d5df8b8.png)](https://p0.ssl.qhimg.com/t0174e6f42f5d5df8b8.png)

恶意软件的第一个动作，是使用API“**GetDiskFreeSpaceExA**”从“A:”到“Z:”检查所有的逻辑分区中是否有可用空间。

如果发现分区存在，它将在该分区的可用空间中，以全局变量的方式保存。

随后，恶意软件访问从“C:”到“P:”的分区。

从“C:”开始，恶意软件会使用concat查询分区中带有“*”的字符串，以搜索该分区中的所有文件和目录。

[![](https://p3.ssl.qhimg.com/t01bc9d8675d8b26946.png)](https://p3.ssl.qhimg.com/t01bc9d8675d8b26946.png)

**恶意软件使用Delphi中SysUtils库的“FindFirst”和“FindNext”进行查找。**对于每个找到的文件或目录，它会使用“.”和“..”检查名称，以避免获取到的是当前目录或前一个目录。

[![](https://p5.ssl.qhimg.com/t01e3cc11dbe7abfb3f.png)](https://p5.ssl.qhimg.com/t01e3cc11dbe7abfb3f.png)

此外，还会**检查其查找到的是否为目录**，如果是目录，就会调用相同的函数，以递归的方式进入全部目录树中的所有子文件夹中。

恶意软件还会再**检查各个文件是否在黑名单列出的目录下**。为了实现这项检查，它**调用了SysUtils库中的“ExtractFileDir”函数**。

黑名单中的目录如下：

windows 

Windows 

program files 

Program Files 

Program Files (x86) 

Programme 

Programme (x86) 

program files (x86) 

programme 

programme (x86) 

programdata

在这个地方，恶意软件存在一个BUG。检查黑名单的本意是避免其对Windows目录造成破坏，**然而，它针对同一个目录，仅仅检查了首字母大小写的两种名称，而没有检查全部大写的名称（例如WINDOWS）**。因此，Windows系统目录有可能会受到恶意软件的影响。

恶意软件**使用SysUtils库的“ExtractFileName”函数来检查文件名**，以确保操作的文件不是以德文命名的“Wo_sind_meine_Datein.html”支付赎金通知。

[![](https://p3.ssl.qhimg.com/t01f951270c413dbd8c.png)](https://p3.ssl.qhimg.com/t01f951270c413dbd8c.png)

如上所述，它仅会避免对系统目录下的文件及支付赎金通知文件的操作。如果文件不属于上述二者，恶意软件会**使用SysUtils库的“ExtractFileExt”函数获取文件的扩展名**。若扩展名属于指定列表之中的任何一个，则会破坏该文件，如果不属于该列表之中，就不会对该文件进行操作。

[![](https://p3.ssl.qhimg.com/t01fe18069b131d7d22.png)](https://p3.ssl.qhimg.com/t01fe18069b131d7d22.png)

我们发现，该病毒的代码质量很差，在检查每个文件的扩展名并与列表进行比较时，都是同一段代码的单纯重复。

受影响的扩展名如下：

[![](https://p0.ssl.qhimg.com/t01850dd950193ac696.png)](https://p0.ssl.qhimg.com/t01850dd950193ac696.png)

如果某个文件的扩展名与上表匹配，**恶意软件首先会生成一个随机值，并随机更改文件名**：

[![](https://p0.ssl.qhimg.com/t015b18f9a12c68df87.png)](https://p0.ssl.qhimg.com/t015b18f9a12c68df87.png)

通常该名称有13个字符。之后，**恶意软件将在0到0x3E80的范围内生成另一个随机值，并将其添加到0x1F40，以产生一个大小不同的新“垃圾文件”，并作为所谓的“加密”文件使用。**

它将使用随机字符填充相应大小的缓冲区，后续会将其储存在文件中。

下一步操作，就是获取没有路径的文件，并进行删除：

[![](https://p0.ssl.qhimg.com/t01345e6707f20712c1.png)](https://p0.ssl.qhimg.com/t01345e6707f20712c1.png)

重要的是，恶意软件删除文件，但并不会覆盖垃圾文件。因此，文件仍然会保留在硬盘中。**如果感染病毒，可以通过使用例如Recuva的恢复软件尝试恢复，有一定概率能成功。**

在删除后，它会将路径与新的随机名称的文件相连接，创建文件，并且用缓冲区中的“垃圾文件”内容进行填充。在最后，它会关闭新文件的句柄，并在同一个文件夹中创建“Wo_sind_meine_Datein. html”的赎金通知。

[![](https://p3.ssl.qhimg.com/t015cc2a9ca30152df1.png)](https://p3.ssl.qhimg.com/t015cc2a9ca30152df1.png)

正如我之前所说，这段病毒代码非常糟糕，因为它默认会为每一个销毁的文件都创建一个赎金通知，然后再进行检查文件夹中有没有之前创建过的赎金通知。

在完成上面的所有过程后，**恶意软件会创建一个名为“HSDFSD-HFSD-3241-91E7-ASDGSDGHH”的互斥锁（mutex），并检查是否存在GetLastError API。如果存在，恶意软件将保持运行。如果不存在，恶意软件将会以另一种不可见的方式在内存中保持运行。**

 

**文件恢复方法**

恶意软件留下的支付赎金通知如下：

[![](https://p5.ssl.qhimg.com/t01ab086002ac0d5343.png)](https://p5.ssl.qhimg.com/t01ab086002ac0d5343.png)

在通知中说，他们使用了AES算法来加密用户的文件，需要支付0.12比特币（约600欧元/4800人民币）。

但实际上，并不像通知所说的那样，**恶意软件在一开始就破坏了文件，根本无法通过支付赎金来实现恢复文件。**

然而，**恶意软件不会对系统中的任何卷影副本（Shadow Volume）或还原点（Restore Point）进行破坏。**

因此，我们可以使用一些软件来管理卷影副本，比如ShadowExplorer：

[https://www.bleepingcomputer.com/download/shadowexplorer/](https://www.bleepingcomputer.com/download/shadowexplorer/)

或者按照以下步骤操作：

[https://www.bleepingcomputer.com/tutorials/how-to-recover-files-and-folders-using-shadow-volume-copies/](https://www.bleepingcomputer.com/tutorials/how-to-recover-files-and-folders-using-shadow-volume-copies/)

另外一个选择，就是使用Recuva这样的恢复程序从原始磁盘中进行恢复，但并不能确保所有的文件都会被恢复：

[https://www.piriform.com/recuva](https://ssl.microsofttranslator.com/bv.aspx?from=&amp;to=zh-CHS&amp;a=https%3A%2F%2Fwww.piriform.com%2Frecuva)

<br>

**总结**

****

通过我们的分析，发现这是一个愚蠢的恶意软件，该恶意软件会破坏企业及个人的信息，尝试诈骗钱财，代码风格挺糟糕的，加的壳也挺简单，以至于我只需要1小时就能完成对它的逆向，顺便写完了这一篇报告。
