> 原文链接: https://www.anquanke.com//post/id/84363 


# 初探Windows Fuzzing神器----Winafl


                                阅读量   
                                **119752**
                            
                        |
                        
                                                                                    



**author:k0shl**

**转载自:同程安全应急响应中心**

**这是一篇客座文章,作者是乌云二进制漏洞挖掘白帽子 k0shl 。其实上个月17号,本文就已经写完了,但是我们一直“捂”到了今天。算是给二进制方向的白帽子的七夕礼物吧 : )**

<br>

**0x01 什么是winafl**

其实说的afl-fuzz大家都不会很陌生,afl-fuzz是Linux用于fuzz文件格式,协议等二进制漏洞的神器,而winafl则是afl-fuzz的Windows版,最近我对winafl进行了一些浅层研究,由于之前也进行过一段时间的二进制漏洞挖掘,但基本上都是停留在手工挖掘上,越发觉得自动化神器功能的强大,也为以后自己开发fuzz工具提供了很重要的指导依据。

Winafl到底是什么?

Winafl是windows下一种挖掘文件格式,协议漏洞的半自动化工具,为什么说半自动化呢,因为针对特定的软件,Winafl并没有提供一个全面的样本库,虽然winafl确实提供了一些测试样本,但实际上真正fuzz的过程中,很多文件需要自己手工构造。

其次比起自动fuzz,Winafl需要自己手动定位需要fuzz的函数地址偏移,来确定具体要进行fuzz的函数位置。

那么相比较来说winafl到底优势在哪呢?这里我要提一下我的理解,winafl的优势在于它采用的是代码扩展来确定输入输出,以此来判断漏洞是否存在,这么说可能大家比较晕乎。

这个原理有点像PIN插件,PIN插件是微软提供的一种类似用于汇编指令扩展的插件,我用一张图来简单描述一下这个过程。

[![](https://p4.ssl.qhimg.com/t0177835c33d8422872.png)](https://p4.ssl.qhimg.com/t0177835c33d8422872.png)

如何理解这个过程,可以想象钩子,插桩等过程,在函数进入和函数返回时,检查程序输入输出是否符合预期等等,通过插入一些“额外”的指令来进行检查,这样,对崩溃位置定位更加精准,误报率极低等等。

刚开始如何学习fuzz?

有很多刚开始接触二进制,或者学过一段时间二进制的小伙伴会问我如何去挖掘,或者刚开始如何学习挖掘二进制漏洞的方法,其实我想说二进制漏洞挖掘是一个很难的过程,随着现在一些类似于strcpy_s,或者说软件安全性越来越好,fuzz的难度越来越高,想要挖掘高级漏洞,需要一些入门的知识,我的水平不高,在这里跟大家分享一些我做fuzz的心得,也是为之后利用winafl进行fuzz做一些铺垫。

在入门的漏洞挖掘中,最重要的是关注程序可能存在的脆弱点,其实和web很像,在二进制中,用户输入也应该是不可信的,而这里所谓的脆弱点,就是存在于用户输入和程序交互的过程中,比较有趣的函数有:strcpy,memcpy,sprintf,read等函数,指针传递,指针赋值等操作中。

下面我来举一个简单的例子,通过IDA分析一个软件,发现有一处比较有趣的调用。

[![](https://p1.ssl.qhimg.com/t012f33c40b9a772139.jpg)](https://p1.ssl.qhimg.com/t012f33c40b9a772139.jpg)

这里我们关注到调用了一处strcpy的调用,我们可以通过windbg附加调试,在j_strcpy位置下断点,这样,程序执行中,如果调用了这处函数,就会命中这处断点(当然,这里用OllyDBG也是可以的)。

[![](https://p4.ssl.qhimg.com/t01fc1b64c20fc1655a.jpg)](https://p4.ssl.qhimg.com/t01fc1b64c20fc1655a.jpg)

在敏感函数位置下断点,通过对样本的附加执行等等方法,直到命中断点,再对函数执行前后的输入输出进行判断,来确定样本是否可以造成程序崩溃,是否可控,是否是一处可造成拒绝服务或者代码执行的漏洞。

[![](https://p2.ssl.qhimg.com/t0179290cca433b129d.png)](https://p2.ssl.qhimg.com/t0179290cca433b129d.png)

通过后续执行情况,判断栈空间的覆盖情况,来确定这里是否是一处可利用的漏洞,可以看到,此时栈回溯已经被畸形字符串冲垮,这个畸形字符串是构造样本中,用户可控的字符串部分。

这里只是简单的讲述了一下最简单的二进制漏洞挖掘过程,其实仔细回想我描述的这个过程,对函数进入推出时输入输出的检查,也就是增加一个类似于指令扩展的过程,那么其实就是自动化fuzz一个简单的模型。

<br>

**0x02 Winafl fuzz前的准备**

这里,我们使用一个名为VUPlayer的软件来利用Winafl fuzz进行一次简单的漏洞挖掘,看过网上afl-fuzz教程的小伙伴可能会发现其实这个挖掘过程耗时很长,指令扩展一定意义上加大了代码冗余,增加了执行时间,这里我提供一个可以触发VUPlayer缓冲区溢出漏洞的PoC,只是为了讲解Winafl fuzz的使用和简单原理。

寻找一个可能存在的脆弱点

之前我提到了Winafl fuzz使用时需要提供一个函数偏移,而在上面的简单漏洞挖掘中,我提到了对敏感函数的寻找,那么我们就来看一下VUPlayer的函数结构,利用IDA分析一下VUPlayer的函数部分。

[![](https://p1.ssl.qhimg.com/t01166b46912d511a31.png)](https://p1.ssl.qhimg.com/t01166b46912d511a31.png)

发现函数调用了一个系统dll的函数lstrcpyA,这样回溯这个lstrcpyA,发现了一处函数。

[![](https://p0.ssl.qhimg.com/t01fa2eb6de58bd9f13.jpg)](https://p0.ssl.qhimg.com/t01fa2eb6de58bd9f13.jpg)

那么我们就选择这个函数进行fuzz,函数入口偏移就是0x532a0,接下来要开始准备fuzz了。

DynamoRIO是什么?

在fuzz前,不得不提到winafl fuzz必须要用到的DynamoRIO,这个软件我也是第一次听说,可能很多二进制的老司机对它都不陌生,其实粗略看过winafl的源码之后,我发现其实winafl很多的实现上,都借用了DynamoRIO,在这两者之间建立了通信管道从而实现两者之间的调用。

而DynamoRIO应该算是winafl的核心部分,它主要实现的是指令动态插桩,其实就是之前我提到的指令扩展,对函数输入输出进行一定的检查。关于DynamoRIO的原理以及介绍在网上有很多描述,这里不做过多介绍了。

用DynamoRIO测试过程

这里我们要用到的是DynamoRIO的ddrun.exe工具,代码如下

&lt;code&gt;

pathtoDynamoRIObin64drrun.exe-c winafl.dll -debug -target_module [target exe or dll]VUPlyaer.exe -target_offset0x532a0 -fuzz_iterations 10  —  [target exe]VUPlayer.exe &lt;/code&gt;

这里需要进行一些简单的解释,首先是-D,用于和afl fuzz进行链接,主要是调用winafl.dll,target_module是测试目标模块,target_offset是偏移,这样的话会打开目标程序。

[![](https://p2.ssl.qhimg.com/t015f97970d7884bf66.jpg)](https://p2.ssl.qhimg.com/t015f97970d7884bf66.jpg)

接下来附加一个样本,发现程序崩溃了,其实这时候,在目标目录下会生成一个log文件。

[![](https://p4.ssl.qhimg.com/t01e90f78502ab8b8c4.jpg)](https://p4.ssl.qhimg.com/t01e90f78502ab8b8c4.jpg)

这个log文件实际上记录了测试VUPlayer过程中,加载的模块,以及记录了偏移函数位置的变化情况,可以对这个崩溃场景进行一个简单的分析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0153a0b2d6633a93fc.jpg)

[![](https://p5.ssl.qhimg.com/t01980ef5635cf40bb7.png)](https://p5.ssl.qhimg.com/t01980ef5635cf40bb7.png)

**0x03 Winafl fuzz与核心源码浅析**

使用Winafl进行fuzz

了解了Dynamoafl fuzz的基本工作流程之后,我们可以使用winafl进行漏洞挖掘,实际上,winafl需要提供多个样本才能对目标程序进行挖掘。

这里为了介绍winafl,我们仍然使用能对目标程序造成崩溃的样本文件。

&lt;code&gt;

C:ProgramFilesVUPlayer&gt;afl-fuzz.exe -i in -o out -D C:UsersAdministratorDe

sktopDynamoRIO-Windows-6.1.1-3DynamoRIO-Windows-6.1.1-3bin32-t 20000 — -fuz

z_iterations 5000-target_module VUPlayer.exe -target_offset 0x532a0 -nargs 2 — VUPlayer.exe @@

&lt;/code&gt;

这里仍然需要对参数进行一些简单说明,首先afl-fuzz需要和winafl.dll同时处于目标文件夹下,-i参数是用于记录输入样本,-o参数用于保存输出数据,-D则是DynamoRIO的路径,-t是样本测试延时,-target_offset是要测试函数的偏移。

[![](https://p4.ssl.qhimg.com/t01d09f5595bd1345d0.png)](https://p4.ssl.qhimg.com/t01d09f5595bd1345d0.png)

当接触到崩溃的时候。

[![](https://p3.ssl.qhimg.com/t01ca88efe6add83389.png)](https://p3.ssl.qhimg.com/t01ca88efe6add83389.png)

结果分析

当winafl碰到崩溃场景的时候,会在-o设定的文件夹下生成一系列文件,会详细记录指令扩展中产生的各种信息。

[![](https://p1.ssl.qhimg.com/t01b74bcb46948537b5.png)](https://p1.ssl.qhimg.com/t01b74bcb46948537b5.png)

Crashes文件记录了崩溃样本,queue记录了指令扩展中的各种信息,cur_input是当前输入信息。

[![](https://p3.ssl.qhimg.com/t01c7f40a91eb7518a3.jpg)](https://p3.ssl.qhimg.com/t01c7f40a91eb7518a3.jpg)

只需要产生crash之后对指令进行分析就可以很清晰的分析到这个函数输入输出发生了什么。或者说,获取了可以崩溃的样本之后,直接附加windbg复现这个漏洞,也能很快的分析出漏洞的成因。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018132e7de4362ff97.png)

源代码中的关键点

之前提到了DynamoRIO在winafl fuzz中的重要性,其实在源码中有很多部分都有体现,下面从源码的角度来看一些在fuzz中的关键点。

[![](https://p0.ssl.qhimg.com/t01b82b3382fda2f8d4.png)](https://p0.ssl.qhimg.com/t01b82b3382fda2f8d4.png)

这个位置会定义dynamorio的路径,以便后续会调用到dynamorio中的工具。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f9c1d911654e601a.jpg)

构造指令插桩的关键语句,可以看到这里调用了ddrun,是DynamoRIO动态插桩的核心工具。

[![](https://p4.ssl.qhimg.com/t018b510e5cb50a3dfe.png)](https://p4.ssl.qhimg.com/t018b510e5cb50a3dfe.png)

目标进程崩溃的进程信息。其实还有很多,比如进程重启机制,指令扩展后记录输入输出,关键函数地址等信息的部分等等。

我才接触二进制的时间不长,文章中有很多描述不当或遗漏的地方希望大牛们多多指正,一起交流进步,这次我只是对winafl进行了一些粗浅分析,源码有上万行,有很多命令的具体功能,插桩的实现原理等等都没有进行更深入的研究,如果感兴趣一起研究的朋友欢迎和我联系,一起学习进步,也希望我以后能够带来对winafl本身更为深入的研究分享,谢谢大家!
