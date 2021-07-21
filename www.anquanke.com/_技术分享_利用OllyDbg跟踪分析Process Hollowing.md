> 原文链接: https://www.anquanke.com//post/id/85124 


# 【技术分享】利用OllyDbg跟踪分析Process Hollowing


                                阅读量   
                                **168298**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.airbuscybersecurity.com
                                <br>原文地址：[http://blog.airbuscybersecurity.com/post/2016/06/Following-Process-Hollowing-in-OllyDbg](http://blog.airbuscybersecurity.com/post/2016/06/Following-Process-Hollowing-in-OllyDbg)

译文仅供参考，具体内容表达以及含义原文为准

 

[![](https://p1.ssl.qhimg.com/t018d747606f4dfc2cd.jpg)](https://p1.ssl.qhimg.com/t018d747606f4dfc2cd.jpg)

翻译：[m6aa8k](http://bobao.360.cn/member/contribute?uid=2799685960)

预估稿费：160RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**概述**



Process Hollowing是现代恶意软件常用的一种进程创建技术，虽然在使用任务管理器之类的工具查看时，这些进程看起来是合法的，但是该进程的代码实际上已被恶意内容所替代。

这篇文章将介绍Process Hollowing技术常用的API调用，并将解释如何利用OllyDbg中的相应机制，赶在恶意代码执行之前附加到新进程上面。



**调试Hollowing进程**



我们看到的第一个API调用将是CreateProcess。通常来说，其命令行参数与用于创建初始进程的参数是相同的。Creation Flag将设置为CREATE_SUSPENDED，具体如下所示。这个调用的返回值是进程的句柄，它将作为参数传递给下文介绍的各个函数调用。

[![](https://p3.ssl.qhimg.com/t01717d022d6e9beebb.png)](https://p3.ssl.qhimg.com/t01717d022d6e9beebb.png)

一旦进程创建完成，接下来将调用NtUnmapViewOfSection，以便从新创建的进程中掏空代码。在此之后，将调用VirtualAllocEx，在新进程中创建可写内存区域。这里有几个重要的参数，包括新建内存区的地址和保护标志。

[![](https://p1.ssl.qhimg.com/t0168f528b70208b688.png)](https://p1.ssl.qhimg.com/t0168f528b70208b688.png)

下一个调用将是WriteProcessMemory。通过它可以查看从父进程的内存中的哪些地方复制代码，这在逆向投递程序和加壳的恶意软件时帮助很大。这个API函数有可能被调用许多次，因为代码可能会位于父进程不同的内存区中。在本示例中，这里的代码会循环遍历PE的各个部分，并将它们分别写入新进程中。

写入代码后，必须告诉进程新的入口点在哪里。为此，可以使用GetThreadContext和SetThreadContext API调用。首先，调用GetThreadContext，将信息读入到可编辑的缓冲区中。进行相应的修改后，使用SetThreadContext将其写回到新进程中。如下图所示，SetThreadContext其中的一个参数是指向存放新的Context结构的缓冲区的指针。

[![](https://p3.ssl.qhimg.com/t01a4ec2fa7a17d9aa5.png)](https://p3.ssl.qhimg.com/t01a4ec2fa7a17d9aa5.png)

右键单击pContext参数旁边的值，选择“Decode as Pointer to Structure”，然后从可用结构列表中选择CONTEXT，这样就可以检查正在写入新进程的数据了。通过在解码后的结构中查找EAX寄存器的值，就能找到新的入口点。在这个例子中，入口点将是0x45E8C0。

[![](https://p1.ssl.qhimg.com/t01515b2c6d852a7191.png)](https://p1.ssl.qhimg.com/t01515b2c6d852a7191.png)

最后一个API调用将是ResumeThread。一旦调用了这个函数，新进程将从前面提到的上下文结构中定义的入口点开始恢复运行。为了能够从头开始跟踪这个新进程，必须在调用ResumeThread之前给它打好补丁。

为此，您可以使用http://processhacker.sourceforge.net/提供的Process Hacker工具，我在监控恶意软件活动时就是使用的这款任务管理器。在这里，进程以树状显示，所以很容易辨别出你感兴趣的进程。你可能已经注意到了，我们的目标进程是灰色的，因为它目前处于挂起状态。我们可以通过右键菜单或通过双击该进程来打开属性对话框。然后，选中内存选项卡，显示虚拟内存的完整映射。在大多数情况下，您感兴趣的内存区域将位于0x400000处，但是，如果不在这里的话，可以在Protect列标记为executable并且名称显示为“Private（Commit）”的区域中查找。

[![](https://p2.ssl.qhimg.com/t0123dfafdcd2349e7f.png)](https://p2.ssl.qhimg.com/t0123dfafdcd2349e7f.png)

双击对话框中的条目，就会在十六进制编辑器中打开相应的内存区域。我们可以单击对话框底部的Goto …按钮，并输入十六进制地址。这里需要用到偏移量，就本例来说，入口点为0x45E8C0，偏移量为0x5E8C0。您必须输入前缀0x，否则Goto函数将失败。

[![](https://p5.ssl.qhimg.com/t015d853485ca44473c.png)](https://p5.ssl.qhimg.com/t015d853485ca44473c.png)

找到入口点后，需要进行相应的修改，否则无法使用调试器。一个方法是用CC替换第一个字节，这跟设置INT 3软件断点的效果是相同的。但是，只有将OllyDbg设置为Just-In-Time调试器时，这种方法才能奏效。我最喜欢的方法是用EB FE替换前两个字节，这会导致进程在恢复运行时进入无限循环。需要注意的是，无论使用哪种方法，都要保存好原始值，以便将来改回为初始值。这里我用EB FE替换前两个字节，以便将来进入无限循环。最后，单击Write按钮，将修改内容写入内存。



[![](https://p1.ssl.qhimg.com/t0156f6873b07194afb.png)](https://p1.ssl.qhimg.com/t0156f6873b07194afb.png)

完成上述修改后，继续遍历原始进程，直到达到ResumeProcess API调用，并允许它运行。现在 ，这个进程将从您的修改的代码开始执行。如果选择了断点选项，那么该进程会在即时调试程序中自动打开。如果像我一样，你也选择使用无限循环方法的话，那么你需要手动将OllyDbg附加到新进程上面。正如下面显示的那样，调试器已成功附加到新进程上面，并在修改的代码处停了下来。

[![](https://p5.ssl.qhimg.com/t0172b7d1b37e3398f7.png)](https://p5.ssl.qhimg.com/t0172b7d1b37e3398f7.png)

最后一步是用原始值替换修改后的代码。在assembly视图中右键单击第一条指令的地址，然后选择Follow in Dump选项。这样就能使得hex视图与assembly视图同步。然后，选择修改后的值，具体如下图所示。

[![](https://p1.ssl.qhimg.com/t01b738a07465d6347d.png)](https://p1.ssl.qhimg.com/t01b738a07465d6347d.png)

然后，用之前记录下来的原始值覆盖这里选中的十六进制数值即可。

[![](https://p4.ssl.qhimg.com/t010a4f5d1fa00729fd.png)](https://p4.ssl.qhimg.com/t010a4f5d1fa00729fd.png)

如此一来，上面的代码将会变成下面的样子。

[![](https://p0.ssl.qhimg.com/t01d60c6bc4c744cdf8.png)](https://p0.ssl.qhimg.com/t01d60c6bc4c744cdf8.png)

完成上述工作后，就可以继续调试新进程了。如果你是在VM中完成这些工作的话，明智的做法是在这里建立一个快照，因为使用OllyDbg中的“rewind”按钮重新启动进程将导致它从磁盘加载原始映像，所以最好还是还原VM为妙。

<br style="text-align: left">
