> 原文链接: https://www.anquanke.com//post/id/179748 


# 《Dive into Windbg系列》Explorer无法启动排查


                                阅读量   
                                **180811**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_576_/t01046f75101c73b87d.jpg)](https://p3.ssl.qhimg.com/dm/1024_576_/t01046f75101c73b87d.jpg)


- 作者：BlackINT3
<li>联系：[blackint3@gmail.com](mailto:blackint3@gmail.com)
</li>
<li>网站：[https://github.com/BlackINT3](https://github.com/BlackINT3)
</li>
> 《Dive into Windbg》是一系列关于如何理解和使用Windbg的文章，主要涵盖三个方面：
<ul>
- 1、Windbg实战运用，排查资源占用、死锁、崩溃、蓝屏等，以解决各种实际问题为导向。
- 2、Windbg原理剖析，插件、脚本开发，剖析调试原理，便于较更好理解Windbg的工作机制。
- 3、Windbg后续思考，站在开发和逆向角度，谈谈软件开发，分享作者使用Windbg的一些经历。
</ul>



## 第三篇 《Explorer无法启动排查》

> 涉及知识点：消息机制、进程退出过程、MUI、国际化等。



## 起因

一台Windows服务器迁移后，发现资源管理器explorer启动不了。手动运行依然无法启动，在任务管理器能看到进程启动后消失，服务器是Server2008 R2，64位。



## 初步排查

关于进程退出，能想到其大致流程：

exit =&gt; ExitProcess =&gt; TerminateProcess =&gt; NtTerminateProcess =&gt; PspTerminateThreadByPointer =&gt; 线程内 PspExitNormalApc =&gt; PspExitThread =&gt;<br>
释放各种资源、通知调试器等 =&gt; KeTerminateThread =&gt; 交出调度权

_ExitProcess伪代码流程如下：

```
//from: https://bbs.pediy.com/thread-188064-1.htm#1287019
int __stdcall _ExitProcess(UINT ExitCode)
`{`
  int result; // eax@1
  char v2; // [sp+10h] [bp-DCh]@2
  UINT v3; // [sp+38h] [bp-B4h]@2
  CPPEH_RECORD ms_exc; // [sp+D4h] [bp-18h]@2

  result = __security_cookie;
  if ( !BaseRunningInServerProcess )
  `{`
    RtlAcquirePebLock();
    ms_exc.disabled = 0;
    NtTerminateProcess(0, ExitCode);
    LdrShutdownProcess();
    v3 = ExitCode;
    CsrClientCallServer(&amp;v2, 0, 65539, 4);
    NtTerminateProcess(-1, ExitCode);
    ms_exc.disabled = -1;
    result = RtlReleasePebLock();
  `}`
  return result;
`}`
```

因为是在迁移机器，需要开关机，猜测是explorer产生已知异常导致的正常退出，可能是什么东西被破坏了，常见的像注册表配置、文件等，这种在关机时最可能会出现。

对于这种稳定复现的问题，先挂个调试器看看再说，因为此时资源管理器不在，用热键调出任务管理器，运行windbg，下面是具体调试过程：

[![](https://p1.ssl.qhimg.com/t01773894041a3b9548.png)](https://p1.ssl.qhimg.com/t01773894041a3b9548.png)

直接g调试运行，发现进程直接退出，调试器中断在NtTerminateProcess，通过栈回溯可知是从main函数中的正常退出，跟之前猜想一样，说明这是程序内部已知的错误。

[![](https://p4.ssl.qhimg.com/t01bac54879f0b73fa9.png)](https://p4.ssl.qhimg.com/t01bac54879f0b73fa9.png)

仔细观察发现，调试器捕获到一处异常：

```
(ae4.284): Unknown exception - code 000006ba (first chance)
```

难道跟这个异常有关？调试器没断下来，只在first chance，说明异常被内部SEH捕获了，没有到达second chance，还是看下异常是什么。使用sx命令查看当前windbg调试事件设置：

[![](https://p1.ssl.qhimg.com/t019583defe8bbad9e9.png)](https://p1.ssl.qhimg.com/t019583defe8bbad9e9.png)

这里也说明了未知异常只在调试器收到second chance（即SEH不处理）时才break下来，输入sxe *，让其直接中断，重新调试运行。

[![](https://p5.ssl.qhimg.com/t0148fa762fe00f54e7.png)](https://p5.ssl.qhimg.com/t0148fa762fe00f54e7.png)

观察异常堆栈，原来是音频服务RPC Server端抛了异常，不过这跟explorer无法启动应该没有关联。

输入!teb，看看LastError有没有什么线索：

[![](https://p0.ssl.qhimg.com/t01eb21f973885d0d64.png)](https://p0.ssl.qhimg.com/t01eb21f973885d0d64.png)

LastStatusValue是c0000034，这里使用一款开源工具：OpenArk<br>[https://github.com/BlackINT3/OpenArk](https://github.com/BlackINT3/OpenArk)

使用.err命令或者直接查看NTSTATUS。

[![](https://p1.ssl.qhimg.com/t0105f7e850684e46f3.png)](https://p1.ssl.qhimg.com/t0105f7e850684e46f3.png)

找不到文件？还是先跟进explorer去看看，至少目前有一点线索。



## 步步追踪

在main函数中直接退出，想到WinProc的各种switch，很多应该都被折腾过。不过有符号已经能省很多事了，想想那些没符号全是各种条件断点的crack日子….

通过栈回溯找到调用ExitProcess的地方，ub查看上面的代码，观察哪个点最接近，也可在靠近GetCommandLineW等附近下断点，这样就不用从OEP去跟了。

对于这种必现问题，有两种方法：

1、反汇编代码，可尝试多次下断点、单步跟踪，找到可疑的地方，尤其是要检查一些返回值和LastError。

2、wt直接跟踪，有符号的话，根据函数名找到可疑的地方，结合方法1。

Tips：用bu命令下断点，然后保存到workspace，下次调试继续生效，注意windbg根据符号偏移下断点可能会有bug，以后有机会再来探讨，若有需要可以关掉ASLR。

跟踪发现是CreateDesktopAndTray函数返回NULL，导致退出。

[![](https://p1.ssl.qhimg.com/t0116e7371c9acbceb8.png)](https://p1.ssl.qhimg.com/t0116e7371c9acbceb8.png)

这是第一个关键点，进入函数，发现是因为explorer!c_tray+0x8为NULL导致，一般情况我们可能会考虑内存访问断点来找，不过这种情况下，执行失败后explorer!c_tray可能不会赋值。

[![](https://p2.ssl.qhimg.com/t01fd1b8c4b47c79347.png)](https://p2.ssl.qhimg.com/t01fd1b8c4b47c79347.png)

观察explorer!CTray::SyncThreadProc线程，c_tray是该线程的一个参数，那么线程应该在初始化c_tray信息，继续跟踪。

最后发现SyncThreadProc调用SHFusionCreateWindowEx函数创建窗口失败了，窗口句柄是NULL，调用之前和调用之后，LastStatusValue都是c0000034，说明开始发现的这个值有误。

[![](https://p1.ssl.qhimg.com/t0162635650ba0005fc.png)](https://p1.ssl.qhimg.com/t0162635650ba0005fc.png)

跟进SHFusionCreateWindowEx，单步走过CreateWindowEx。有意思的事发生了，得到的窗口句柄rax却不是0，为什么？

[![](https://p5.ssl.qhimg.com/t01029344a3fcf66db1.png)](https://p5.ssl.qhimg.com/t01029344a3fcf66db1.png)

说明这个函数内部递归调用，查看栈回溯如下：

[![](https://p1.ssl.qhimg.com/t01ee013c8e61203a8d.png)](https://p1.ssl.qhimg.com/t01ee013c8e61203a8d.png)

说到Windows消息机制，就想到了KeUserModeCallback、KiUserCallbackDispatcher、KernelCallbackTable、LoadLibrary注入、消息钩子等等。<br>
感兴趣的可以看看《KeUserModeCallback用法详解》[https://bbs.pediy.com/thread-104918.htm。](https://bbs.pediy.com/thread-104918.htm%E3%80%82)<br>
NT6之后虽有些不同，但实现思路是一致的。

看到这个_fnINLPCREATESTRUCT蛋疼的命名，我便想起了David Culter看到GUI部门的表情，还是ntoskrnl内部颇有美感。

_fnINLPCREATESTRUCT这个函数便在分发WM_CREATE消息，具体可以看看KernelCallbackTable表，在这个点可以做一些拦截，什么消息钩子、窗口子类化。

接下来思路就清晰了，肯定是某个窗口创建失败了，在调用CreateWindowExW处下条件断点。

```
bu *** ".if(rax == 0)`{``}`.else`{`gc`}`"
```

断下来后，继续查看TEB LastStatus，最后发现是c00b0006错误。

[![](https://p1.ssl.qhimg.com/t01f2420a41e9d680dc.png)](https://p1.ssl.qhimg.com/t01f2420a41e9d680dc.png)

```
15105 ERROR_MUI_FILE_NOT_LOADED &lt;--&gt; c00b0006 STATUS_MUI_FILE_NOT_LOADED
```

提示MUI文件不存在，到系统Windows目录查看，explorer.exe.mui果然不在，拷贝之，再次验证，explorer启动成功。。。

MUI文件本身也是PE文件，里面含有语言资源，为了解决国际化，动态分离程序和语言文件，这个和”大名鼎鼎”的LPK有关联。

MUI可以参考：[https://docs.microsoft.com/en-us/windows/desktop/intl/overview-of-mui](https://docs.microsoft.com/en-us/windows/desktop/intl/overview-of-mui)



## 结束

很多时候，看似一些难缠的问题背后往往原因很简单。积累经验，总结反思，培养测量意识，善用调试跟踪工具，自动化去解决问题。

比如这次我可以在TEB的LastError用内存访问断点，也可以用Procmon监视文件访问，解决问题的方法基本是：猜想 + 论证 =&gt;…=&gt; 解决。

Thanks for reading。

```
参考资料：
Google
MSDN
Windbg Help
WRK
```
