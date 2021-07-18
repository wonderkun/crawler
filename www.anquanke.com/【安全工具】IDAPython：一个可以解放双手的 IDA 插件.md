
# 【安全工具】IDAPython：一个可以解放双手的 IDA 插件


                                阅读量   
                                **233914**
                            
                        |
                        
                                                                                                                                    ![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/saving-time-effort-idapython/](http://resources.infosecinstitute.com/saving-time-effort-idapython/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85890/t0189742651524d0f4e.png)](./img/85890/t0189742651524d0f4e.png)



翻译：[村雨其实没有雨](http://bobao.360.cn/member/contribute?uid=2671379114)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



对于那些熟悉CTF比赛的人来说，时间分配是非常重要的一个问题，我们需要合理安排好时间，尽可能多的得分。你看到的大多数题目的write-up都使用了自动化的脚本来自动完成一些繁琐的或者不可能手工完成的任务。这不仅节省了时间，更节省了精力，因为解题人只需要一次性搞清楚需要重复执行的内容，剩下的就可以交给脚本去做了。这就是我们面临的挑战。

我们现在需要解决的题目来自[Nuit Du Hack Quals 2017](https://quals.nuitduhack.com/)，题名是"[Matrioshka: Step 4(I did it again)"](https://goo.gl/MhVl0g)，一道逆向工程题。我们会看到，如果手工处理的话，不仅会花费逆向手几个小时时间，还会让触及用于检查输入是否正确的代码更加困难。

本文的目标是编写一个Python解析器脚本，它将会自动化的完成题目，然后在末尾输出flag。

我们先来看看我们正在处理的是什么样的二进制文件

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c667b450e1d18cfa.png)

我们现在需要做的是设置远程CDB调试器，然后从IDA64连接到文件

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014e159d3d67c4b476.png)

该程序期望我们输入334个字符，我们照做就好

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e56f443152587661.png)

检查长度后，crackme会用memalign分配内存对齐的内存块。它将随后使用mprotect来修改页面对RWX的权限。

复制到该块的数据从sub_40089D开始到sub_422C0C(不包括sub_422C0C)。这两个地址之间的一些内容表明可能这里会有一些即时的代码解密过程。

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016f6f22be97a5bc94.png)

接下来，使用以下参数调用分配页面中的“sub_40089D”副本。

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0147cc4f096fe364ef.png)

如果输入的参数是正确的，返回值为0x1。

到现在为止还挺好。现在我们来看看sub_40089D做了什么。

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01920fc235bb6d3f56.png)

我们看到它遍历提供的输入的每个字符，并执行以下操作：

读取字符两次

将其保存在局部变量中

再次读取字符并将其加1。例如，A变为B等等

用增加的值替换内存中的原始字符

从局部变量恢复它

也许有人会把它看作垃圾代码，因为它实际上做的只是修改了一个字符，然后将其还原到之前的内容。但实际上，它是通过使用硬件断点机制进行对flag算法探测行为进行防护。如果只使用一次的话，这种保护会非常弱，但事实上，它在程序的整个执行过程中被使用了几十次，这将大大增加手动检查flag算法的时间。

现在让我们看看代码加密的部分，我们不会深入到太细节地方，简单来讲每个函数都进行了以下操作：

执行我们之前看过的反硬件断点技巧

使用简单的XOR算法加密相同功能的最后三条指令（在LEAVE; RETN之前）

用简单的XOR算法解密下一个被调用的函数

调用解密函数

返回后解密最后三条指令，然后继续执行，从而返回给调用者（我们直到输入正确才会返回）

同样的过程在0x40089D到0x40C305被执行（分配区块中的等效地址），因此我们大概有47kb的代码是除了解密自身和访问（读写）用户输入之外什么都不做。

你可能想知道我是如何知道这段功能是在0x40089D到0x40C305被执行的，当然我没有狂按F9打几百次断点，这里就是IDAPython发挥作用的地方了。

在开始编写脚本之前，我们需要做一些假设：

调试二进制文件前，我们只能执行所有操作中的四个函数。所以我的第一个假设是除了最后检查输出的功能以外，所有后续功能是一样的。

第二个假设是关于HW断点保护的，这也是最重要的假设。我认为检查输入的函数是在所有其他函数执行完之后才会执行的，也就是最后才会被调用。如果检查输入是在中期执行的，那么也就意味着我们会在输入被检查完之后还会再做很多无用的硬件断点，我采用的方法就不会起作用，那时候我们就需要更多的标准来判定。

幸运的是我们所有的假设都是正确的，下面的脚本能够帮我们找到第一个被确认的字符的位置

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01673874eb170e02c4.png)

我们首先创建一个空列表来保存所有地址（RIP），其中调试器将由于读/写硬件断点而暂停进程。接下来，在prepare函数中，可以看到在CALL指令中修改提供给mprotect的地址参数和RAX寄存器（图4）。我这样做是因为IDA在后面阶段尝试处理硬件断点时（第二个脚本）会崩溃。我不知道为什么会这样。

从函数返回时，调试器仍然挂起在CALL RAX，我们可以通过在RDX上引用指针来将指针提取到我们的字符串。

随后，我们在字符串的第一个字符上设置了一个读/写硬件断点。在此之后，我们输入一个循环，继续将地址（RIP）附加到列表中。循环继续，直到进程退出(event！= BREAKPOINT)。最后，我们删除读/写硬件断点，并打印硬件断点的最后一个地址。也就是代码检查提供的输入的有效性的位置。

这是我们从IDA得到的输出：

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01237995cc375aa1cf.png)

我们现在要做的就是去看看包含在0x40c336里的函数的功能是什么。为了搞清楚这一点，我们还需要在该地址设置一个执行硬件断点（设置软件断点是不可行的）。

一旦我们触发了断点，我们需要做的就是让IDA将其周围的字节解析成指令，然后查看函数的作用。

以下是python等效于算法，用于检查两个字符是否匹配flag：

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d0017648163c131b.png)

正如我们所见，该算法通过使用两个硬编码的双字词（我们成为dword1和dword2）来检查每两个字节是否有效。每个函数检查十个字符，但最后一个仅检查4个字符。换言之每个函数将会把后面的代码执行五次，最后一个执行2次。这就意味着，如果你想手动调试，就需要反复执行复制粘贴双字词到爆破脚本多达167次; 在CTF大赛中，这并不是一个明智的选择。

现在我们需要修改Python函数，让它能够使用i和j变量来遍历result变量，它们分别是dword1和dword2。

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c71fb88b0e0c0ba6.png)

在这之后，我们需要执行第二个Python脚本，将flag输出到一个文件中：

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01aaa37cc1b4ca60aa.png)

脚本的功能显而易见，唯一需要说明的是添加到RIP和RBP中的两个偏移变量：

第一个Dword始终储存在局部变量[RBP-3Ch]中

第二个Dword被硬编码为指令操作数，但是始终位于RIP+0x54。RIP是HW断点触发后调试器挂起进程的地方

作为脚本执行的结果，我们会得到一个包含标志的文件

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cf02aa3b50ebb06e.png)

[![](./img/85890/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012dda27313cdebb61.png)

我们可以轻松将两个脚本结合在一起，最终在IDA只运行一次

更多资料可以参考IDAPython文档：[https://www.hex-rays.com/products/ida/support/idapython_docs/](https://www.hex-rays.com/products/ida/support/idapython_docs/) 
