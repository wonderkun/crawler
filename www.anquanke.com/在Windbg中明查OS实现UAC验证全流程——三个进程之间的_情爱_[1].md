> 原文链接: https://www.anquanke.com//post/id/231403 


# 在Windbg中明查OS实现UAC验证全流程——三个进程之间的"情爱"[1]


                                阅读量   
                                **194211**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0133435a43ae81bd1e.png)](https://p2.ssl.qhimg.com/t0133435a43ae81bd1e.png)



## 0、引言

讲解UAC提权的文章有很多，其提权方法更是数不胜数，目前不完全统计大概有65种方法，但很少或者说几乎没有文章谈及OS是如何完成UAC验证的，本文基于作者之前的一些小小调试分析，记录下有关的细节，与大家共同学习交流。整个系列涉及到的知识：

0、Windbg调试及相关技巧；

1、OS中的白名单及白名单列表的窥探；

2、OS中的受信目录及受信目录列表的查询；

3、窗口绘制[对,你没看错,提权窗口就涉及到绘制]；

4、程序内嵌的程序的Manifest；

5、服务程序的调试；



## 1、进程之间的父子关系图

首先必须明确下接下来要涉及到的几个进程的关系，大致会涉及到四个进程，但待创建的目标进程对于我们这里分析的内部验证机制不太重要，只需要它的一些静态信息，所以着重分析三个进程之间的关系，但为了不失一般性，还是把他挂到图谱上去。

场景1是这样的，在任务栏右键，启动任务管理器，直至Taskmgr进程起来，期间涉及的进程如下：

explorer.exe——&gt;这个进程只负责调用CreateProcess()发起一个创建进程的请求出去； AIS———————&gt;负责完成各种校验，校验通过了，它负责创建指定的进程；

有两个问题请读者思考下：

1)通过procexp.exe或者自己code可知，待创建的进程的父进程是explorer，而我这里说是AIS创建的，是不是说错了，如果没说错，原因是什么？<br>
2)explorer明明是meduim完整性级别，为什么被创建的进程就是High完整性级别了？

场景2是这样的，双击桌面上的应用程序[这个应用程序需要管理员权限才能启动的那种，通常带个盾牌]，直至弹出框框出来，这一些列的操作涉及：

explorer.exe—&gt;这个进程只负责调用CreateProcess()发起一个创建进程的请求出去；<br>
AIS—————&gt;负责完成各种校验，校验通过了，它负责创建指定的进程；<br>
consent.exe—&gt;仅仅是画一个界面，谈一个框，跟用户确认是否要提权，然后把结果通知给AIS；

有一个问题请读者思考下：

1)既然consent.exe弹出一个框，让用户确认是否提权，那我们是否可以通过模拟鼠标或键盘操作的方式，来模拟点击进行提权呢？

场景3是这样的，右键桌面上的应用程序，以管理员程序执行，直至弹出框框来，这一系列的操作涉及：

explorer.exe—&gt;这个进程只负责调用CreateProcess()发起一个创建进程的请求出去；<br>
AIS—————&gt;负责完成各种校验，校验通过了，它负责创建指定的进程；<br>
consent.exe—&gt;仅仅是画一个界面，谈一个框，跟用户确认是否要提权，然后把结果通知给AIS；

好了，下边给出图谱，如下：

[![](https://p5.ssl.qhimg.com/t0170ce872b509c6cc3.png)](https://p5.ssl.qhimg.com/t0170ce872b509c6cc3.png)



## 2、Manifest与盾牌的恩怨

### <a class="reference-link" name="2.1%20%E5%AE%8C%E6%95%B4%E6%80%A7%E7%BA%A7%E5%88%AB"></a>2.1 完整性级别

关于Manifest是何方神圣，请自行百度解决，今天要讨论的是其与”提权“相关的部分，当Windows在桌面上绘图exe的图标时，它怎么知道哪些需要加一个盾牌，哪些不需要加的呢？一种常规的做法便是查看他的Manifest文件，并探查关键字段；当然不常规的做发就是看看它的导入表，是否调用了哪些特权API，诸如此类；下边来看一下这个Manifset文件，以两个exe举例说明，一个是Taskmgr.exe，另一个是一个普通的exe文件；查看exe中Manifest文件的方法有多个，这里列举两种方法：<br>
方法1 ：mt.exe工具，演示如下：

```
mt.exe -inputresource:C:\Users\Administrator\Desktop\Taskmgr.exe
-out:C:\Users\Administrator\Desktop\Taskmgr.manifest
```

会在指定的目录下生成一个Taskmgr.manifest文件，打开内容如下：

[![](https://p4.ssl.qhimg.com/t01581dd479f6b58ec7.png)](https://p4.ssl.qhimg.com/t01581dd479f6b58ec7.png)

比较重要的两个已经红框框出，简单解释如下：

1)requestedExecutionLevel表明你的程序需要怎样的权限，通常设置的值如下：

```
asInvoker
requireAdministrator
highestAvailable
```

asInvoker：父进程是什么权限级别，那么此应用程序作为子进程运行时就是什么权限级别。<br>
requireAdministrator：此程序需要以管理员权限运行。在资源管理器中可以看到这样的程序图标的右下角会有一个盾牌图标。<br>
highestAvailable：此程序将以当前用户能获取的最高权限来运行。

如果你指定为 highestAvailable：

1、当你在管理员账户下运行此程序，就会要求权限提升。资源管理器上会出现盾牌图标，双击启动此程序会弹出 UAC 提示框。<br>
2、当你在标准账户下运行此程序，此账户的最高权限就是标准账户。受限访问令牌（Limited Access Token）就是当前账户下的最高令牌了，于是 highestAvailable 已经达到了要求。资源管理器上不会出现盾牌图标，双击启动此程序也不会出现 UAC 提示框，此程序将以受限权限执行。显然这里看见的是 highestAvailable，而我当前的账户是管理员账户，如下：

[![](https://p3.ssl.qhimg.com/t0133ea354c0f1cd344.png)](https://p3.ssl.qhimg.com/t0133ea354c0f1cd344.png)

### <a class="reference-link" name="2.2%20autoElevate"></a>2.2 autoElevate

autoElevate字段用以表明该EXE是一个自动提权的程序，所谓的自动提权就是不需要弹出框让用户进行确认的提权操作。这往往出现在OS自带的需要提权的那些EXE中。需要说明的是，并不是有了autoElevate就能自动提权，他只是第一步，告知创建进程的API，待创建的子进程有这个意愿，至于能不能成，另说。



## 3、看看带头大哥explorer的动作——场景1

借助于调试利器——Windbg，来走一遍大哥是如何将创建的动作一步一步派发的。思路是这样的，在进程创建的关键API处下断点，拦截关键点。如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01589a7472913b2188.png)

这么多，一个一个来bp的话也行，但有快速的“批量”下断的方法，即模糊匹配，如下：

```
0:256&gt; bm ntdll!*Create*Process*  1: 00007ffc`f25a6ed0 
@!"ntdll!RtlCreateUserProcessEx"  2: 00007ffc`f256b3f0 
@!"ntdll!RtlCreateProcessParametersEx"  3: 00007ffc`f25a6f90 
@!"ntdll!RtlpCreateUserProcess"  4: 00007ffc`f25bb330 @!"ntdll!NtCreateProcessEx"  5: 
00007ffc`f25fbb50 @!"ntdll!RtlCreateUserProcess"breakpoint 4 redefined  4: 
00007ffc`f25bb330 @!"ntdll!ZwCreateProcessEx"  6: 00007ffc`f25f0b60 
@!"ntdll!RtlCreateProcessReflection"  7: 00007ffc`f25bc1c0 
@!"ntdll!ZwCreateUserProcess"breakpoint 7 redefined  7: 00007ffc`f25bc1c0 
@!"ntdll!NtCreateUserProcess"  8: 00007ffc`f2554d10 
@!"ntdll!RtlpCreateProcessRegistryInfo"  9: 00007ffc`f25f1860 
@!"ntdll!RtlCreateProcessParameters"  10: 00007ffc`f25bc000 
@!"ntdll!ZwCreateProcess"breakpoint 10 redefined  10: 00007ffc`f25bc000 
@!"ntdll!NtCreateProcess"

```

ok了，下边坐看钓鱼台，愿者上钩吧。任务栏右键启动任务管理器。断点命中，如下：

```
Breakpoint 8 hit
ntdll!RtlpCreateProcessRegistryInfo:
00007ffc`f2554d10 48895c2408      mov     qword ptr [rsp+8],rbx 
ss:00000000`036fdbc0=0000000000000001
0:003&gt; k# Child-SP          RetAddr           Call Site00 00000000`036fdbb8 
00007ffc`f2554b78 ntdll!RtlpCreateProcessRegistryInfo01 00000000`036fdbc0 
00007ffc`f2553f89 ntdll!LdrpSetThreadPreferredLangList+0x4c02 00000000`036fdbf0 
00007ffc`f2552f24 ntdll!LdrpLoadResourceFromAlternativeModule+0xd103 
00000000`036fdd50 00007ffc`f2552d7e ntdll!LdrpSearchResourceSection_U+0x17004 
00000000`036fde90 00007ffc`ee970e39 ntdll!LdrFindResource_U+0x5e05 
00000000`036fdee0 00007ffc`f05725a0 KERNELBASE!FindResourceExW+0x8906 
00000000`036fdf50 00007ffc`f09f9d35 user32!LoadMenuW+0x2007 
00000000`036fdf90 00007ffc`cc5c964b shlwapi!SHLoadMenuPopup+0x1508 
00000000`036fdfc0 00007ffc`cc5a2741 explorerframe!CBandSite::_OnContextMenu+0xcb09 00000000`036fe350 
00007ff6`340e67d5 explorerframe!CBandSite::OnWinEvent+0x635710a 
00000000`036fe3b0 00007ff6`340896db Explorer!CTrayBandSite::HandleMessage+0x890b 00000000`036fe420 
00007ff6`340c9c9e Explorer!BandSite_HandleMessage+0x730c 00000000`036fe460 
00007ff6`340c689f Explorer!TrayUI::WndProc+0x7de0d 00000000`036fe860 
00007ff6`340c47a2 Explorer!CTray::v_WndProc+0xccf0e 00000000`036fedb0 
00007ffc`f0566d41 Explorer!CImpWndProc::s_WndProc+0xf20f 00000000`036fee00 
00007ffc`f056634e user32!UserCallWinProcCheckWow+0x2c110 00000000`036fef90 
00007ffc`f0564ec8 user32!SendMessageWorker+0x21e11 00000000`036ff020 
00007ffc`f05643e8 user32!RealDefWindowProcWorker+0x98812 00000000`036ff120 
00007ff6`340c68db user32!DefWindowProcW+0x19813 00000000`036ff190 
00007ff6`340c47a2 Explorer!CTray::v_WndProc+0xd0b14 00000000`036ff6e0 
00007ffc`f0566d41 Explorer!CImpWndProc::s_WndProc+0xf215 00000000`036ff730 
00007ffc`f0566713 user32!UserCallWinProcCheckWow+0x2c116 00000000`036ff8c0 
00007ff6`340c8e52 user32!DispatchMessageWorker+0x1c317 00000000`036ff950 
00007ff6`34090253 Explorer!CTray::_MessageLoop+0x1b218 00000000`036ffa20 
00007ffc`f0733fb5 Explorer!CTray::MainThreadProc+0x4319 00000000`036ffa50 
00007ffc`eff14034 shcore!_WrapperThreadProc+0xf51a 00000000`036ffb30 
00007ffc`f2593691 KERNEL32!BaseThreadInitThunk+0x141b 00000000`036ffb60 
00000000`00000000 ntdll!RtlUserThreadStart+0x21

```

栈很完美，但这个不是我们关注的重点，取消掉这个断点：

```
bc 8
```

紧接着

```
Breakpoint 2 hit
ntdll!RtlCreateProcessParametersEx:00007ffc`f256b3f0 48895c2418      mov     qword ptr [rsp+18h],rbx ss:00000000`5624d6a0=0000000028289e40
# Child-SP          RetAddr           Call Site
00 00000000`56a4d5f8 00007ffc`ee98e7c9 ntdll!RtlCreateProcessParametersEx
01 00000000`56a4d600 00007ffc`ee98b4db KERNELBASE!BasepCreateProcessParameters+0x199
02 00000000`56a4d710 00007ffc`ee9b91b6 KERNELBASE!CreateProcessInternalW+0xc2b
03 00000000`56a4e3a0 00007ffc`eff1b9e3 KERNELBASE!CreateProcessW+0x66
04 00000000`56a4e410 00007ffc`eeed879e KERNEL32!CreateProcessWStub+0x53
05 00000000`56a4e470 00007ffc`eeed8396 windows_storage!CInvokeCreateProcessVerb::CallCreateProcess+0x2d2
06 00000000`56a4e720 00007ffc`eeed804c windows_storage!CInvokeCreateProcessVerb::_PrepareAndCallCreateProcess+0x1ee
07 00000000`56a4e7b0 00007ffc`eeed9517 windows_storage!CInvokeCreateProcessVerb::_TryCreateProcess+0x78
08 00000000`56a4e7e0 00007ffc`eeed7dee windows_storage!CInvokeCreateProcessVerb::Launch+0xfb
09 00000000`56a4e880 00007ffc`eeeda7f7 windows_storage!CInvokeCreateProcessVerb::Execute+0x3e
0a 00000000`56a4e8b0 00007ffc`eeedb010 windows_storage!CBindAndInvokeStaticVerb::InitAndCallExecute+0x163
0b 00000000`56a4e930 00007ffc`eeedab74 windows_storage!CBindAndInvokeStaticVerb::TryCreateProcessDdeHandler+0x68
0c 00000000`56a4e9b0 00007ffc`eeed3c03 windows_storage!CBindAndInvokeStaticVerb::Execute+0x1b4
0d 00000000`56a4ecc0 00007ffc`eeed395d windows_storage!RegDataDrivenCommand::_TryInvokeAssociation+0xaf
0e 00000000`56a4ed30 00007ffc`f0a96e25 windows_storage!RegDataDrivenCommand::_Invoke+0x13d
0f 00000000`56a4eda0 00007ffc`f0a95bba SHELL32!CRegistryVerbsContextMenu::_Execute+0xc9
10 00000000`56a4ee10 00007ffc`f0ad29c0 SHELL32!CRegistryVerbsContextMenu::InvokeCommand+0xaa
11 00000000`56a4f110 00007ffc`f0a7ee1d SHELL32!HDXA_LetHandlerProcessCommandEx+0x118
12 00000000`56a4f220 00007ffc`f0a6cfcf SHELL32!CDefFolderMenu::InvokeCommand+0x13d
13 00000000`56a4f580 00007ffc`f0a6cea9 SHELL32!CShellExecute::_InvokeInProcExec+0xff
14 00000000`56a4f680 00007ffc`f0a6c3e6 SHELL32!CShellExecute::_InvokeCtxMenu+0x59
15 00000000`56a4f6c0 00007ffc`f0ad830e SHELL32!CShellExecute::_DoExecute+0x156
16 00000000`56a4f720 00007ffc`f0733fb5 SHELL32!&lt;lambda_4b6122ab997c3c85ec9dfce089ab4a05&gt;::&lt;lambda_invoker_cdecl&gt;+0x1e
17 00000000`56a4f750 00007ffc`eff14034 shcore!_WrapperThreadProc+0xf5
18 00000000`56a4f830 00007ffc`f2593691 KERNEL32!BaseThreadInitThunk+0x14
19 00000000`56a4f860 00000000`00000000 ntdll!RtlUserThreadStart+0x21
```

简单看下CreateProcessW的几个参数，需要做一点分析，原因是x64上前4个参数是通过寄存器传递的，而现在我们断在了靠后的地方，所以需要手工解析下。但这里不需要解析，原因是内部大概率的会把相关的指针保存到栈中，只要解引用下栈的数据即可，一个指令搞定，如下：

```
0:241&gt; dpu 00000000`56a4d5f8 l30
00000000`56a4d5f8  00007ffc`ee98e7c9 ".诿藘.떈Գ䠀䖋䆇º.謀⁏喋襷袈"
00000000`56a4d600  00000000`00000002
00000000`56a4d608  00000000`00000000
00000000`56a4d610  00000000`1b6f17c0 "塚ե"
00000000`56a4d618  00000000`223b4a20 "C:\WINDOWS\system32"
00000000`56a4d620  00000000`56a4d6d0 "HJӃ"
00000000`56a4d628  00000000`00000000
00000000`56a4d630  00000000`56a4d6b0 "&gt;@"
00000000`56a4d638  00000000`56a4d6a0 ". "
00000000`56a4d640  00000000`56a4d690 ""
00000000`56a4d648  00000000`56a4d680 ""
00000000`56a4d650  00000000`00000001
00000000`56a4d658  00000000`223b4a20 "C:\WINDOWS\system32"
00000000`56a4d660  00000000`00000000
00000000`56a4d668  00007ffc`ee97ea00 "赈.འ쁗襈.䡀䲍〤䓇〤0"
00000000`56a4d670  00000000`00000000
00000000`56a4d678  00000000`00000000
00000000`56a4d680  00000000`00000000
00000000`56a4d688  00000000`00000000
00000000`56a4d690  00000000`00020000 "......................................................."
00000000`56a4d698  00007ffc`eead7414 ""
00000000`56a4d6a0  00000000`0020001e "ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ"
00000000`56a4d6a8  00000000`00f22f38 "Winsta0\Default"
00000000`56a4d6b0  00000000`0040003e ""
00000000`56a4d6b8  00000000`2be9a1e0 "C:\WINDOWS\system32\taskmgr.exe"
00000000`56a4d6c0  00000000`00280026 "ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ.ÿ"
00000000`56a4d6c8  00000000`223b4a20 "C:\WINDOWS\system32"
00000000`56a4d6d0  000004c3`004a0048
00000000`56a4d6d8  00000000`2bac04b0 ""C:\WINDOWS\system32\taskmgr.exe" /4"
00000000`56a4d6e0  00000000`00000004
00000000`56a4d6e8  00000000`00c05000 ""

```

基本无误了，下一步需要确认一件事情，即这个创建taskmgr.exe的动作是在explorer体内还是在AIS体内，这个简单。将AIS挂起，然后在创建taskmgr看看是否能成功拉起。



## 4、挂起AIS

AIS的全称是AppInfo Server，它是一个服务，内嵌在SvcHost体内，可通过任务管理器找到，如下图所示，他负责校验该EXE是否能够以管理员权限启动。他才是核心。

[![](https://p2.ssl.qhimg.com/t01a9d21411aa1925fe.png)](https://p2.ssl.qhimg.com/t01a9d21411aa1925fe.png)

通过任务管理器去停止这个服务，我这没能成功，索性就直接用Procexp吧。如下图：

[![](https://p5.ssl.qhimg.com/t013734970d47ef3fac.png)](https://p5.ssl.qhimg.com/t013734970d47ef3fac.png)

取消掉所有断点，然后 右键——-&gt;启动任务管理器 没有任何反应，Taskmgr也没有被创建出来，如下图：

[![](https://p3.ssl.qhimg.com/t0158d382f4ae8beb9f.png)](https://p3.ssl.qhimg.com/t0158d382f4ae8beb9f.png)

通过这种“粗暴”的手段，至少能证明，explorer顶多算个始作俑者却算不算真正的大佬。那谁才是背后推动着这个成功创建的幕后黑手呢？方法只有一个，继续调试，不过这次的断点稍微往上来一点。放在kernelbase中。【中途有点事情，耽搁了下，回来重启了下电脑，PID发生了变化】

```
0:151&gt; bp KERNELBASE!CreateProcessWBreakpoint 0 hit KERNELBASE!CreateProcessW:00007ffd`d9cc9150 4c8bdc          mov     r11,rsp
0:004&gt; k
Child-SP          RetAddr           Call Site
00 00000000`34f0e878 00007ffd`dc26b9e3 KERNELBASE!CreateProcessW
01 00000000`34f0e880 00007ffd`da55879e KERNEL32!CreateProcessWStub+0x53
02 00000000`34f0e8e0 00007ffd`da558396 windows_storage!CInvokeCreateProcessVerb::CallCreateProcess+0x2d2
03 00000000`34f0eb90 00007ffd`da55804c windows_storage!CInvokeCreateProcessVerb::_PrepareAndCallCreateProcess+0x1ee
04 00000000`34f0ec20 00007ffd`da559517 windows_storage!CInvokeCreateProcessVerb::_TryCreateProcess+0x78
05 00000000`34f0ec50 00007ffd`da557dee windows_storage!CInvokeCreateProcessVerb::Launch+0xfb
06 00000000`34f0ecf0 00007ffd`da55a7f7 windows_storage!CInvokeCreateProcessVerb::Execute+0x3e
07 00000000`34f0ed20 00007ffd`da55b010 windows_storage!CBindAndInvokeStaticVerb::InitAndCallExecute+0x163
08 00000000`34f0eda0 00007ffd`da55ab74 windows_storage!CBindAndInvokeStaticVerb::TryCreateProcessDdeHandler+0x68
09 00000000`34f0ee20 00007ffd`da553c03 windows_storage!CBindAndInvokeStaticVerb::Execute+0x1b4
0a 00000000`34f0f130 00007ffd`da55395d windows_storage!RegDataDrivenCommand::_TryInvokeAssociation+0xaf
0b 00000000`34f0f1a0 00007ffd`dab86e25 windows_storage!RegDataDrivenCommand::_Invoke+0x13d
0c 00000000`34f0f210 00007ffd`dab85bba SHELL32!CRegistryVerbsContextMenu::_Execute+0xc9
0d 00000000`34f0f280 00007ffd`dabc29c0 SHELL32!CRegistryVerbsContextMenu::InvokeCommand+0xaa
0e 00000000`34f0f580 00007ffd`dab6ee1d SHELL32!HDXA_LetHandlerProcessCommandEx+0x118
0f 00000000`34f0f690 00007ffd`dab5cfcf SHELL32!CDefFolderMenu::InvokeCommand+0x13d
10 00000000`34f0f9f0 00007ffd`dab5cea9 SHELL32!CShellExecute::_InvokeInProcExec+0xff
11 00000000`34f0faf0 00007ffd`dab5c3e6 SHELL32!CShellExecute::_InvokeCtxMenu+0x59
12 00000000`34f0fb30 00007ffd`dabc830e SHELL32!CShellExecute::_DoExecute+0x156
13 00000000`34f0fb90 00007ffd`dd3f3fb5 SHELL32!&lt;lambda_4b6122ab997c3c85ec9dfce089ab4a05&gt;::&lt;lambda_invoker_cdecl&gt;+0x1e
14 00000000`34f0fbc0 00007ffd`dc264034 shcore!_WrapperThreadProc+0xf5
15 00000000`34f0fca0 00007ffd`dd713691 KERNEL32!BaseThreadInitThunk+0x14
16 00000000`34f0fcd0 00000000`00000000 ntdll!RtlUserThreadStart+0x21

```

[![](https://p2.ssl.qhimg.com/t0164b9e9811907c69c.png)](https://p2.ssl.qhimg.com/t0164b9e9811907c69c.png)

紧接着看这个API的执行结果，如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0194d55f2ee578e522.png)

这个结果是可以预见的，原因是“如果通过CreateProcess能创建成功，那么俺也可以模仿者它的参数来创建玩玩，哪里还有啥UAC的事情”。好，接下来就是接着找，到底是咋创建的，反正是跟AIS有关。



## 5、探寻提权的骚操作——大哥开始派活了

好了，上边的线索断了，也该断了，不然在错误的道路上越走越远，万劫不复。现在仅有的线索就是上边那个栈回溯，那就再多瞅一眼呗。截取了一段有意思的如下：

[![](https://p1.ssl.qhimg.com/t01cb5153adc3fb24ab.png)](https://p1.ssl.qhimg.com/t01cb5153adc3fb24ab.png)

这个Try是啥意思？不是“尝试，试一下”的意思吗？它为何要尝试一下？难道不成功便成仁，有二手准备？

以上全部是鄙人猜测，那就在这几个Try处下断点，看看到底在干啥。

[![](https://p1.ssl.qhimg.com/t0158c504d32e01923f.png)](https://p1.ssl.qhimg.com/t0158c504d32e01923f.png)

很不幸的是，一个断点都没有断下来，那就有可能是我猜错了，还有种可能就是“重试”的操作在上边进行了，那就试试后者吧。

【下边的很多线程号对不上，是因为调试explorer不方便操作，为了写文章截图，只能重复演示】

[![](https://p3.ssl.qhimg.com/t014161e9d72069a649.png)](https://p3.ssl.qhimg.com/t014161e9d72069a649.png)

[![](https://p0.ssl.qhimg.com/t014a15a7a325f100cb.png)](https://p0.ssl.qhimg.com/t014a15a7a325f100cb.png)

继续分析如下：

[![](https://p3.ssl.qhimg.com/t01c6ff36e85d1e49e5.png)](https://p3.ssl.qhimg.com/t01c6ff36e85d1e49e5.png)

来简单看下传进去的参数

[![](https://p5.ssl.qhimg.com/t01d9296d7816257696.png)](https://p5.ssl.qhimg.com/t01d9296d7816257696.png)

跟进去，一步一步看看，如下：

[![](https://p2.ssl.qhimg.com/t01357fdf09165a0a3b.png)](https://p2.ssl.qhimg.com/t01357fdf09165a0a3b.png)

原来用的是RPC，现在具体分析下这个RPC的过程。

Ndr64AsyncClientCall的原型如下：

```
CLIENT_CALL_RETURN RPC_VAR_ENTRY Ndr64AsyncClientCall( MIDL_STUBLESS_PROXY_INFO *pProxyInfo, unsigned long nProcNum, void *pReturnValue, ... );

typedef struct _MIDL_STUBLESS_PROXY_INFO
`{`
    PMIDL_STUB_DESC                     pStubDesc;
    PFORMAT_STRING                      ProcFormatString;
    const unsigned short            *   FormatStringOffset;
    PRPC_SYNTAX_IDENTIFIER              pTransferSyntax;
    ULONG_PTR                           nCount;
    PMIDL_SYNTAX_INFO                   pSyntaxInfo;
`}` MIDL_STUBLESS_PROXY_INFO;

typedef struct _MIDL_STUB_DESC
`{`
    void  *    RpcInterfaceInformation;
    void  *    ( __RPC_API * pfnAllocate)(size_t);
    void       ( __RPC_API * pfnFree)(void  *);
    union
    `{`
        handle_t  *             pAutoHandle;
        handle_t  *             pPrimitiveHandle;
        PGENERIC_BINDING_INFO   pGenericBindingInfo;
    `}` IMPLICIT_HANDLE_INFO;
    const NDR_RUNDOWN  *                    apfnNdrRundownRoutines;
    const GENERIC_BINDING_ROUTINE_PAIR  *   aGenericBindingRoutinePairs;
    const EXPR_EVAL  *                      apfnExprEval;
    const XMIT_ROUTINE_QUINTUPLE  *         aXmitQuintuple;
    const unsigned char  *                  pFormatTypes;
    int                                     fCheckBounds;
    /* Ndr library version. */
    unsigned long                           Version;
    MALLOC_FREE_STRUCT  *                   pMallocFreeStruct;
    long                                    MIDLVersion;
    const COMM_FAULT_OFFSETS  *             CommFaultOffsets;
    // New fields for version 3.0+
    const USER_MARSHAL_ROUTINE_QUADRUPLE  * aUserMarshalQuadruple;
    // Notify routines - added for NT5, MIDL 5.0
    const NDR_NOTIFY_ROUTINE  *             NotifyRoutineTable;
    // Reserved for future use.
    ULONG_PTR                               mFlags;
    // International support routines - added for 64bit post NT5
    const NDR_CS_ROUTINES *                 CsRoutineTables;
    void *                                  ProxyServerInfo;
    const NDR_EXPR_DESC *               pExprInfo;
    // Fields up to now present in win2000 release.
`}` MIDL_STUB_DESC;

typedef struct _MIDL_SYNTAX_INFO
`{`
    RPC_SYNTAX_IDENTIFIER               TransferSyntax;
    RPC_DISPATCH_TABLE *                DispatchTable;
    PFORMAT_STRING                      ProcString;
    const unsigned short *              FmtStringOffset;
    PFORMAT_STRING                      TypeString;
    const void           *              aUserMarshalQuadruple;
    const MIDL_INTERFACE_METHOD_PROPERTIES *pMethodProperties;
    ULONG_PTR                           pReserved2;
`}` MIDL_SYNTAX_INFO, *PMIDL_SYNTAX_INFO;

typedef const MIDL_STUB_DESC  * PMIDL_STUB_DESC;
typedef const unsigned char  * PFORMAT_STRING;
typedef MIDL_SYNTAX_INFO, *PMIDL_SYNTAX_INFO;
```

简单整理下Ndr64AsyncClientCall的函数参数，跟一下数据，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01059a18f871af1f6e.png)

gAppinfoRPCBandHandle是Appinfo的RPC的UUID，如下：

[![](https://p2.ssl.qhimg.com/t01dc1564848826850b.png)](https://p2.ssl.qhimg.com/t01dc1564848826850b.png)

[![](https://p3.ssl.qhimg.com/t01b57625f614eabd2c.png)](https://p3.ssl.qhimg.com/t01b57625f614eabd2c.png)

这把全清楚了，原来explorer把创建进程的骚操作通过RPC推给了AppInfo。

dwCreationFlags == 0x4080404，解释如下：

```
#define CREATE_SUSPENDED                      0x00000004
#define CREATE_UNICODE_ENVIRONMENT            0x00000400
#define EXTENDED_STARTUPINFO_PRESENT          0x00080000
#define CREATE_DEFAULT_ERROR_MODE             0x04000000
```



## 6、寂寞等待的大哥

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0163665992065527ce.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01682bb93c9a03f842.png)

[![](https://p1.ssl.qhimg.com/t01ba00a9bbb43808ed.png)](https://p1.ssl.qhimg.com/t01ba00a9bbb43808ed.png)

多么淳朴的做法，地道！



## 7、总结

本篇主要讲解了explorer拉起需要提权的进程的第一步，涉及到好些个进程的调试，后续的还有深入分析，敬请期待！
