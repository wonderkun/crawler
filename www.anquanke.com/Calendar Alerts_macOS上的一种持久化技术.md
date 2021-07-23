> 原文链接: https://www.anquanke.com//post/id/219829 


# Calendar Alerts：macOS上的一种持久化技术


                                阅读量   
                                **67611**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者f-secure，文章来源：labs.f-secure.com
                                <br>原文地址：[https://labs.f-secure.com/blog/operationalising-calendar-alerts-persistence-on-macos/](https://labs.f-secure.com/blog/operationalising-calendar-alerts-persistence-on-macos/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t015e5185134cb770ec.jpg)](https://p3.ssl.qhimg.com/t015e5185134cb770ec.jpg)



## 0x00 前言

在本文中，我们详细分析了如何利用日历警报实现macOS上的持久化。本文以Andy Grant在NCC上发表的一篇[文章](https://research.nccgroup.com/2020/05/05/exploring-macos-calendar-alerts-part-1-attempting-to-execute-code/)为基础，深入分析了如何从攻击者角度来实现该技术的武器化应用。我们进行了多项研究，包括逆向分析`Automator.app`，发现了一个未公开的API来实现该技术，也公布了用来实现持久化的JavaScript for Automation（JXA）[代码](https://github.com/FSecureLABS/CalendarPersist)。



## 0x01 Calendar.app

Andy在之前的文章中曾提到过，macOS内置的Calendar应用中包含许多功能，其中一个功能是可以针对某个事件，以警报方式来执行应用。用户可以通过GUI来配置该功能，创建新事件时的操作界面如下图所示：

[![](https://p2.ssl.qhimg.com/t01defd1acb6747bf56.png)](https://p2.ssl.qhimg.com/t01defd1acb6747bf56.png)

Andy已经详细分析过这方面内容，包括研究代码的执行方式以及数据窃取方式（强烈建议大家先看一下那篇文章，写的非常精彩），然而我比较关注的是其中提到的持久化内细节。Andy提到他在实现持久化方面遇到一些困难，比如难以通过编程方式、使用AppleScript来插入事件，另外Calendar应用也会直接忽视他的请求等。我们也可以采用其他方法，比如修改支撑该应用的SQLite数据库。这种方法很好，我们可以为所有后续事件设置默认的告警行为，然而在实际环境中，这种技术很难应用。



## 0x02 技术分析

在测试该技术的过程中，我顺带研究了一下`Automator.app`，这是Apple提供的一种拖放式（drag-and-drop）应用构建解决方案，可以用来执行重复任务。Automator中就包含构建日历警报的模板。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e0c295d3fa6e73c2.png)

逐步通过GUI操作，保存workflow（工作流）后，我们可以看到日历中添加了一个新的事件，并且附带了能够以新应用来执行我们workflow的警报。这是个不错的开头，我们有可能通过编程来自动完成该任务。

我开始深入研究Apple Developer文档中的[EventKit](https://developer.apple.com/documentation/eventkit/ekalarm?language=objc)，这是负责与日历事件交互的一个框架。然而在官方文档中，我并没有找到允许用户添加警报、执行应用的API。因此，我决定深入分析Automator，了解实现该过程的原理。

首先我使用Objective See的[FileMonitor](https://objective-see.com/products/utilities.html)和[ProcessMonitor](https://objective-see.com/products/utilities.html)分析工具，初步了解了Automator的处理流程。该应用并没有修改Calendar的数据库，也没有修改其他感兴趣的文件。因此，我使用了LLVM调试器`lldb`来分析。在剔除一些EventKit函数后，最后我找到了一个函数：`[AMICalPluginWorkflowPersonality finishSavingWorkflow:forOperation:atURL:error:]`。观察该函数的反汇编代码后，我们可以看到一系列EventKit函数，这些函数与Apple官方文档中提供的函数非常类似。

```
&lt;+735&gt;:  movq   0x58d6ff62(%rip), %rdi    ; (void *)0x00007fff90b872b0: AMEventKitSoftLinking
&lt;+742&gt;:  movq   0x58d6eb8b(%rip), %rsi    ; "EKEvent"
&lt;+749&gt;:  callq  *%r14
&lt;+752&gt;:  movq   0x58d6ec69(%rip), %rsi    ; "eventWithEventStore:"
&lt;+759&gt;:  movq   %rax, %rdi
&lt;+762&gt;:  movq   %r12, %rdx
&lt;+765&gt;:  callq  *%r14
&lt;+768&gt;:  movq   %rax, %rdi
&lt;+771&gt;:  callq  0x7fff37e3e744            ; symbol stub for: objc_retainAutoreleasedReturnValue
&lt;+776&gt;:  movq   %rax, %rbx
&lt;+779&gt;:  movq   0x58d6898e(%rip), %rsi    ; "setTitle:"
&lt;+786&gt;:  movq   %rax, %rdi
&lt;+789&gt;:  movq   -0x98(%rbp), %rdx
&lt;+796&gt;:  callq  *%r14
&lt;+799&gt;:  movq   0x58d6ec42(%rip), %rsi    ; "setStartDate:"
&lt;+806&gt;:  movq   %rbx, %rdi
&lt;+809&gt;:  movq   %r15, %rdx
&lt;+812&gt;:  callq  *%r14
&lt;+815&gt;:  movq   0x58d6ec3a(%rip), %rsi    ; "setEndDate:"
&lt;+822&gt;:  movq   %rbx, %rdi
&lt;+825&gt;:  movq   %r15, -0xd0(%rbp)
&lt;+832&gt;:  movq   %r15, %rdx
&lt;+835&gt;:  callq  *%r14
```

如上所示，这段反汇编代码会使用`EKEvent`类来创建一个新的事件，设置事件标题、开始以及结束日期。然而有一部分我不是特别熟悉，其中包含一个有趣的函数：`[EKAlarm procedureAlarmWithBookmark]`，该函数无法在Apple的官方文档中找到。涉及这个未公开函数的部分反汇编代码如下所示：

```
&lt;+876&gt;:  movq   0x58d6ec05(%rip), %rsi    ; "bookmarkDataWithOptions:includingResourceValuesForKeys:relativeToURL:error:"
&lt;+883&gt;:  xorl   %r12d, %r12d
&lt;+886&gt;:  movl   $0x200, %edx              ; imm = 0x200 
&lt;+891&gt;:  xorl   %ecx, %ecx
&lt;+893&gt;:  xorl   %r8d, %r8d
&lt;+896&gt;:  movq   %r13, %r9
&lt;+899&gt;:  callq  *0x58cd7f17(%rip)         ; (void *)0x00007fff723f3800: objc_msgSend
&lt;+905&gt;:  movq   %rax, %rdi
&lt;+908&gt;:  callq  0x7fff37e3e744            ; symbol stub for: objc_retainAutoreleasedReturnValue
&lt;+913&gt;:  movq   %rax, %r15
&lt;+916&gt;:  movq   (%r13), %rdi
&lt;+920&gt;:  callq  *0x58cd7f12(%rip)         ; (void *)0x00007fff723f36d0: objc_retain
&lt;+926&gt;:  movq   %rax, %r13
&lt;+929&gt;:  testq  %r15, %r15
&lt;+932&gt;:  je     0x7fff37e1138a            ; &lt;+1034&gt;
&lt;+934&gt;:  movq   0x58d6fe9b(%rip), %rdi    ; (void *)0x00007fff90b872b0: AMEventKitSoftLinking
&lt;+941&gt;:  movq   0x58d6ebcc(%rip), %rsi    ; "EKAlarm"
&lt;+948&gt;:  callq  *%r14
&lt;+951&gt;:  movq   0x58d6ebca(%rip), %rsi    ; "procedureAlarmWithBookmark:"
&lt;+958&gt;:  movq   %rax, %rdi
&lt;+961&gt;:  movq   %r15, %rdx
&lt;+964&gt;:  callq  *%r14
```

可以看到，Automator会创建一个新的书签，该书签是指向磁盘上特定文件的一个数据结构。随后，Automator会创建`EKAlarm`类的一个新实例，调用该类中的`procedureAlarmWithBookmark`函数，传入书签数据作为参数。太棒了，这正是我们寻找的目标。



## 0x03 具体实现

此时我们已经找到了所有线索，可以通过编程方式实现持久化目标。我将这些要点都融入JXA代码中，方便通过Mythic（也就是Apfell）来执行攻击代码。下面我将举个例子，通过这种攻击方式，最终将新的日历事件添加到特定的日历中。这并不是实现该技术的唯一方式（或者不是最隐蔽的方式），此外我的JXA代码还可以通过已有的事件来植入后门，或者修改用户的日历。大家可以查看[GitHUb](https://github.com/FSecureLABS/CalendarPersist)了解更多细节。

在开始操作前，我们先要设置Mythic，准备好Apfell载荷。Mythic提供了很好的官方文档，大家可以根据[文档](https://docs.mythic-c2.net/installation)步骤来操作。接下来，我们需要使用`jsimport`命令，将我们的功能导入到Apfell中。

[![](https://p0.ssl.qhimg.com/t012b08b0f37937fdb5.png)](https://p0.ssl.qhimg.com/t012b08b0f37937fdb5.png)

此时，我们的脚本已经载入Apfell载荷中，然后开始调用其中的函数。首先我们需要枚举用户的日历，可以使用`list_calendars`函数完成该任务，这个操作需要用户授予日历（有时候是联系人）的进程执行代码[权限](https://developer.apple.com/documentation/eventkit/ekeventstore/1507547-requestaccesstoentitytype)。

[![](https://p2.ssl.qhimg.com/t01e1547d46690441a5.png)](https://p2.ssl.qhimg.com/t01e1547d46690441a5.png)

这里我们选择Automator日历，记录下对应的UID。接下来，我们使用JXA中的`persist_calalert`函数来创建新的事件。该函数调用方式如下所示：

```
persist_calalert(
    "My Event",                            // Title
    "/Users/rookuu/Library/Apfell.app",    // Target App
    60,                                    // Delay in seconds
    "daily",                               // Frequency of recurrence
    1,                                     // Interval of recurrence
    3,                                     // Number of events
    "711CE045-7778-4633-A6FA-27E18ADD0C17" // UID of the calendar
)
```

现在进程会创建新的事件，将其插入日历中。函数调用中的`Delay in seconds`参数用来指定第一个事件的发生时间，后续参数分别为持久化操作触发的频率、间隔以及事件数。在本例中，我们将每天创建一个新的事件，持续3天，当事件触发时，将会启动我们的恶意应用。

[![](https://p4.ssl.qhimg.com/t01966823f88762fcb6.png)](https://p4.ssl.qhimg.com/t01966823f88762fcb6.png)

在Apfell中开始攻击后，我们可以在日历中看到操作结果。首次事件将在2020年10月9日 18:53触发，执行指定的app。在这个测试用例中，我们最终将执行Apfell载荷，并且在指定的时间段内，我们可以拿到回连shell，完成持久化任务。



## 0x04 macOS沙箱

在本文撰写过程中，Calum Hall（[@_chall](https://github.com/_chall)）曾提醒到，我没有考虑到系统上的沙箱机制，这样即使应用被成功执行，效果也不完美，除非我们能在Calendar沙箱外执行代码。

[![](https://p3.ssl.qhimg.com/t01c2d8ee098b69ce89.png)](https://p3.ssl.qhimg.com/t01c2d8ee098b69ce89.png)

出乎我意料的是，事实证明我们并不需要关心沙箱逃逸问题，因为我们一开始就没有在沙箱中。虽然Calendar是一个沙箱化进程，但通过警报方式执行的应用并没有被沙箱化处理。如上图所示，我们执行的应用`CalendarAlarmSandboxTest`并没有在沙箱中。



## 0x05 检测机制

对这种攻击技术的检测方式很大程度上取决于具体的环境、可用的感知技术以及攻击技术的具体实现或者执行方式。

### <a class="reference-link" name="%E5%BC%82%E5%B8%B8%E6%96%87%E4%BB%B6%E8%AE%BF%E9%97%AE%E4%BA%8B%E4%BB%B6"></a>异常文件访问事件

对于这种攻击技术，我们可以重点关注在`/Users/`{`USER`}`/Library/Calendars/`路径下创建或修改日历事件文件的异常应用是关键的检测指标。更具体一些，我们需要关注是否有脚本进程（比如Python、osascrit、ruby等）发起了这类文件创建或者修改操作。当使用脚本来创建或者修改事件时，就会在该路径下创建或者编辑ICS文件。

### <a class="reference-link" name="%E8%BF%9B%E7%A8%8B%E5%85%B3%E7%B3%BB"></a>进程关系

除了文件访问事件之外，防御方还可以考虑借助可以进程关系来检测。通常情况下，与日历事件有关的进程可以提供Calendar应用本身与被执行的程序或者payload之间的关系。然而，受限于macOS上进程间通信的工作方式，`launchd`进程通常是大多数执行进程的父进程，导致防御方无法准确绘制出父子进程关系以及进程树。Jaron Bradley之前在[The Truetree Concept](https://themittenmac.com/the-truetree-concept/)中已经详细讨论过这方面内容，也分析了如何利用未公开的API和XPC服务来获取“Responsible”及“Submitted by”进程标识符。在本例中，我们最终执行的“payload”应用由`CoreServicesUIA`提交。

### <a class="reference-link" name="%E5%8F%AF%E7%96%91%E7%9A%84osascript%E8%BF%9B%E7%A8%8B"></a>可疑的osascript进程

持久化技术的检测并不一定很简单，防御方最好将检测重点集中在攻击链的早期阶段。我们在本文中讨论的PoC使用了Apfell的JXA payload，因此可以通过ESF监控osascript进程来检测。此外，osascript的执行在macOS系统以及整个环境中非常常见的一种行为。为了提高检测准确率，防御方需要收集丰富的数据，比如可以在命令行参数或者系统功能上查找是否存在如下特征：
- 执行JavaScript
<li>执行shel脚本，如`do shell sciprt`
</li>
- 脚本尝试以提升的权限运行，以及/或者使用对话框提示用户输入。


## 0x06 总结

Calendar Alerts是在macOS设备上实现持久化的一种技巧，大家可以试一下`CalendarPersist.js` JXA以及Mythic/Apfell。找到未公开的API是不错的一个切入点，这方面还值得进一步研究。
