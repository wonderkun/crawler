> 原文链接: https://www.anquanke.com//post/id/176343 


# 《Dive into Windbg系列》AudioSrv音频服务故障


                                阅读量   
                                **1190090**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_576_/t01046f75101c73b87d.jpg)](https://p3.ssl.qhimg.com/dm/1024_576_/t01046f75101c73b87d.jpg)



作者：BlackINT3

联系：[blackint3@gmail.com](mailto:blackint3@gmail.com)

网站：[https://github.com/BlackINT3](https://github.com/BlackINT3)

> 《Dive into Windbg》是一系列关于如何理解和使用Windbg的文章，主要涵盖三个方面：
<ul>
- 1、Windbg实战运用，排查资源占用、死锁、崩溃、蓝屏等，以解决各种实际问题为导向。
- 2、Windbg原理剖析，插件、脚本开发，剖析调试原理，便于较更好理解Windbg的工作机制。
- 3、Windbg后续思考，站在开发和逆向角度，谈谈软件开发，分享作者使用Windbg的一些经历。
</ul>



## 第二篇 《AudioSrv音频服务故障》

> 涉及知识点：控制面板、AudioSrv服务、COM、RPC、ALPC、ACL、Token、本地内核调试等。



## 起因

最近换了HDMI显示器后，提示正在寻找音频设备，随后系统没声音了。右下角喇叭出现红叉，自动修复提示音频服务未响应，重装音频驱动也没用，系统是Windows 10 1803 64位。

[![](https://p0.ssl.qhimg.com/t01cddfcdc3a85ec06e.png)](https://p0.ssl.qhimg.com/t01cddfcdc3a85ec06e.png)

多次尝试修复无果，于是打开调试器一探究竟。



## 寻找突破口

从何处入手？这不由得让我想起《How to solve it》一书：问题是什么？之间的关联？有哪些已知线索？

系统的音频面板中列出了本机所有接口，操作一番发现设置为默认的功能不生效。

[![](https://p0.ssl.qhimg.com/t0123d4f03c3bac3b8e.png)](https://p0.ssl.qhimg.com/t0123d4f03c3bac3b8e.png)

我意识到这可能跟音频服务无响应有关，于是决定从这个点入手。

可以看到设置默认选项是一个PopMenu，因此打算先找到该菜单的响应函数，进而分析后续的代码实现。打开procexp，查找该窗口对应的进程，发现是rundll32，如下：

```
"C:windowssystem32rundll32.exe" Shell32.dll,Control_RunDLL mmsys.cpl,,sounds
```

mmsys.cpl是一个控制面板程序，CPL是PE文件，导出了CPlApplet函数，该函数是程序的逻辑入口，原型如下：

```
__declspec(dllexport) long __stdcall CPlApplet(HWND hwndCPL,UINT uMsg,LPARAM lParam1,LPARAM lParam2);
```

为了找到PopMenu窗口的消息处理过程(WndProc)，首先通过spy++找到菜单所属窗口的句柄wnd，接着写一段代码注入到rundll32进程中获取：

```
LONG_PTR ptr = NULL;
HWND wnd = ***;
//https://blogs.msdn.microsoft.com/oldnewthing/20031201-00/?p=41673
if (IsWindowUnicode(wnd))
  ptr = GetWindowLongPtrW((HWND)wnd, GWLP_WNDPROC);
else
  ptr = GetWindowLongPtrA((HWND)wnd, GWLP_WNDPROC);
```

找到WndProc是ntdll!NtdllDialogWndProc_W，接着就需要条件断点，PopMenu的菜单响应是WM_COMMAND（0x0111）消息，WndProc原型如下：

```
LRESULT CALLBACK WindowProc(HWND hwnd,
    UINT uMsg,
    WPARAM wParam,
    LPARAM lParam
);
```

可知rcx是窗口句柄，rdx是消息ID，因此设置条件断点如下：

```
bp ntdll!NtdllDialogWndProc_W ".if(@rcx==句柄 and @rdx==0x0111)`{`.printf "%x %xn",@rcx,@rdx;.echo`}`.else`{`gc`}`"
```

[![](https://p1.ssl.qhimg.com/t01f4c662b078894ec3.png)](https://p1.ssl.qhimg.com/t01f4c662b078894ec3.png)

中断下来之后使用pc命令找到对应的调用，根据符号名能大致知道函数的功能，最后找到PolicyConfigHelper::SetDefaultEndpoint函数，调用栈如下所示：

```
00 audioses!PolicyConfigHelper::SetDefaultEndpoint
01 audioses!CPolicyConfigClient::SetDefaultEndpointForPolicy
02 mmsys!CEndpoint::MakeDefault
03 mmsys!CPageDevices::ProcessWindowMessage
04 mmsys!CDevicesPageRender::ProcessWindowMessage
05 mmsys!ATL::CDialogImplBaseT&lt;ATL::CWindow&gt;::DialogProc
06 atlthunk!AtlThunk_0x01
07 USER32!UserCallDlgProcCheckWow
08 USER32!DefDlgProcWorker
09 USER32!DefDlgProcW
10 ntdll!NtdllDialogWndProc_W
```

uf /c 查看audioses!PolicyConfigHelper::SetDefaultEndpoint调用函数如下：

```
0:000&gt; uf /c audioses!PolicyConfigHelper::SetDefaultEndpoint
audioses!PolicyConfigHelper::SetDefaultEndpoint (00007ffc`6c3adc7c)
    call to audioses!GetAudioServerBindingHandle (00007ffc`6c387be4)
    call to RPCRT4!NdrClientCall3 (00007ffc`94e706f0)
    call to audioses!FreeAudioServerBindingHandle (00007ffc`6c387b78)
    call to audioses!WPP_SF_D (00007ffc`6c3643d4)

```



## RPC调试方法

查看GetAudioServerBindingHandle函数：

```
audioses!GetAudioServerBindingHandle (00007fff`d2c07be4)
    call to RPCRT4!RpcStringBindingComposeW (00007ff8`07882e60)
    call to RPCRT4!RpcBindingFromStringBindingW (00007ff8`0788d8b0)
    call to RPCRT4!RpcStringFreeW (00007ff8`0787ab40)

```

可知在连接RPC服务端，得到端口句柄。接下来的NdrClientCall3便是执行RPC客户端调用。

RPC全称Remote Procedure Call（远程过程调用），主要是实现客户端的函数在服务端上下文调用，对客户端来说像在调用本地函数一样，为此这里会涉及几个点：

```
函数原型一致
序列化/反序列化
同步异步
数据交换
内存分配
异常处理
注册发现
传输方式
...
```

关于RPC，可以讲很多东西，因篇幅有限，我将重心放在Windows的RPC，同时讲一些调试技巧。对RPC感兴趣的可以去看看gRPC、brpc（有很多研究资料）、Thrift，以及一些序列化协议（pb、json、mp）等。

Windows对RPC使用无处不在，COM的跨进程通信便是用的RPC，还有许多服务都提供了RPC调用接口，例如LSA、NetLogon等等。

读者需要理清COM、RPC、LPC/ALPC之间的关联，这里可以分三个层次：

```
COM -- ole*.dll、combase.dll
RPC -- rpcrt4.dll
LPC/ALPC -- ntdll!Zw*Port/ntdll!ZwAlpc*
```

COM在垮进程通信时会调用到RPC，RPC在本地调用时会用到LPC（本地过程调用Local Procedure Call）（也有可能是Socket/NamedPipe，大部分应该都是LPC，因为效率最高），LPC是NT旧时代的产物，Vista之后LPC升级成了ALPC，A是Advanced高级的意思，ALPC通信速度、安全性、代码规范，可伸缩性都有提升，这些概念可以参考Windows Internals。

大致了解这些概念之后，我们来通过调试讲解，这些调用关系从栈回溯能很清晰看到。

回到文中的问题，我们执行到RPC运行时这一层，RpcStringBindingComposeW函数，原型如下：

```
RPC_STATUS RPC_ENTRY RpcStringBindingCompose(
  TCHAR* ObjUuid,
  TCHAR* ProtSeq,
  TCHAR* NetworkAddr,
  TCHAR* EndPoint,
  TCHAR* Options,
  TCHAR** StringBinding
);
```

关于调试RPC运行时这一层（RPC有文档、ALPC没文档化），建议参看MSDN

[https://docs.microsoft.com/en-us/windows/desktop/rpc/rpc-start-page](https://docs.microsoft.com/en-us/windows/desktop/rpc/rpc-start-page)

，写点代码，使用MIDL生成stub，然后查看NDR是如何序列化接口、参数等信息，也就是Marshall部分，以及RPC如何实现同步异步、内存分配、异常处理，理清各个结构，这对调试大有裨益。

接下来使用du rdx查看ProtSeq值是”ncalrpc”，说明使用的LPC，后续的NdrClientCall3会调入ALPC，因此来到ntdll!NtAlpcSendWaitReceivePort，查看栈如下：

[![](https://p2.ssl.qhimg.com/t01f70f6a09f2f5b4ef.png)](https://p2.ssl.qhimg.com/t01f70f6a09f2f5b4ef.png)

NtAlpcSendWaitReceivePort调入内核，然而在应用层仅通过这个函数提供的信息，我们并不能很快定位到服务端的调用。当然可以调试RPC运行时层（rpcrt4）来定位，不过走到这一步，我们接下来的重点是调试ALPC，因此不作考虑。

PrcessHacker里有不少逆向过的代码，直接查看NtAlpcSendWaitReceivePort原型下：

```
NTSTATUS
NtAlpcSendWaitReceivePort(
    __in HANDLE PortHandle,
    __in ULONG Flags,
    __in_opt PPORT_MESSAGE SendMessage,
    __in_opt PALPC_MESSAGE_ATTRIBUTES SendMessageAttributes,
    __inout_opt PPORT_MESSAGE ReceiveMessage,
    __inout_opt PULONG BufferLength,
    __inout_opt PALPC_MESSAGE_ATTRIBUTES ReceiveMessageAttributes,
    __in_opt PLARGE_INTEGER Timeout
    );
```

找到PortHandle，用livekd来查看ALPC Port信息：

```
//启动livekd查看内核信息
livekd -k windbg路径

//根据进程ID找到rundll32的EPROCESS
!process `{`进程ID`}` 0

//找到PortHandle对应的ALPC端口对象
!handle `{`PortHandle`}` 3 `{`EPROCESS`}`

//查看ALPC对象信息
!alpc /p `{`AlpcPortObject`}`
```

通过ALPC信息可知ConnectionPort是AudioClientRpc。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d8a7c3bb11590800.png)

继续查看ConnectionPort，可知Server端是svchost，并且开了两个IOCP Worker线程在处理ALPC通信，正处于Wait状态，同时能得到进程线程ID。

[![](https://p5.ssl.qhimg.com/t016b6212a2ca8ff6d7.png)](https://p5.ssl.qhimg.com/t016b6212a2ca8ff6d7.png)

```
//切换到svchost进程地址空间
.process `{`svchost EPROCESS`}`

//重新加载符号和模块
.reload

//查看两个IOCP线程信息
!thread `{`ETHREAD`}`

//正在等待IOCP，线程栈如下：
nt!KiSwapContext+0x76
nt!KiSwapThread+0x501
nt!KiCommitThreadWait+0x13b
nt!KeRemoveQueueEx+0x262
nt!IoRemoveIoCompletion+0x99
nt!NtWaitForWorkViaWorkerFactory+0x334
nt!KiSystemServiceCopyEnd+0x13 (TrapFrame @ ffffca89`c2661b00)
ntdll!NtWaitForWorkViaWorkerFactory+0x14
ntdll!TppWorkerThread+0x536
KERNEL32!BaseThreadInitThunk+0x14
ntdll!RtlUserThreadStart+0x21
```

另开windbg挂起对应的svchost.exe，在上述线程的ntdll!NtWaitForWorkViaWorkerFactory+0x14返回处下断点：

```
~~[1118] bp 7ff8`07dd6866
```

断下来后，使用wt跟踪，可大致知道调用关系，继续在NtAlpcSendWaitReceivePort下断点：

```
~~[1118] bp ntdll!NtAlpcSendWaitReceivePort
```

查看栈回溯，可知IOCP的Callback在处理ALPC调用：

[![](https://p1.ssl.qhimg.com/t01849b289413da3090.png)](https://p1.ssl.qhimg.com/t01849b289413da3090.png)

面对频繁的ALPC调用，如何才能定位是我们的Client发过来的？

必然要找到Client和Server之间的关联，然后设置条件断点，那么关联在哪里？

NtAlpcSendWaitReceivePort函数的参数ReceiveMessage是PPORT_MESSAGE，其包含MessageId和对端的进程线程ID，结构如下：

```
//from: https://github.com/processhacker/processhacker/blob/master/phnt/include/ntlpcapi.h
typedef struct _PORT_MESSAGE
`{`
    union
    `{`
        struct
        `{`
            CSHORT DataLength;
            CSHORT TotalLength;
        `}` s1;
        ULONG Length;
    `}` u1;
    union
    `{`
        struct
        `{`
            CSHORT Type;
            CSHORT DataInfoOffset;
        `}` s2;
        ULONG ZeroInit;
    `}` u2;
    union
    `{`
        CLIENT_ID ClientId;
        double DoNotUseThisField;
    `}`;
    ULONG MessageId;
    union
    `{`
        SIZE_T ClientViewSize; // only valid for LPC_CONNECTION_REQUEST messages
        ULONG CallbackId; // only valid for LPC_REQUEST messages
    `}`;
`}` PORT_MESSAGE, *PPORT_MESSAGE;
```

通过结构体推算ClientId结构偏移是+0x08，ReceiveMessage是第5个参数（上一篇讲过如何获取x64的参数值）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cffd059025e9c5dc.png)

可知rdi是ReceiveMessage，rdi是non volatile寄存器，因此设置条件断点：

```
//Tips：先让Client执行到NdrClientCall时再启用断点，防止中断到其它RPC函数。
bp `{`NtAlpcSendWaitReceivePort调用后`}` ".if(poi(@rdi+8)==`{`Client进程ID`}` and poi(@rdi+10)==`{`Client线程ID`}`)`{``}`.else`{`gc`}`"
```

此时Client单步走过NdrClientCall，svchost会中断下来，由于这个RPC接口是阻塞的，因此Client会等到Server端的返回。

接下里就是进入rpcrt4运行时，执行各种反序列化、内存分配拷贝等操作，最后通过rpcrt4!Invoke进入真正的接口函数，通过调用栈一目了然。

[![](https://p1.ssl.qhimg.com/t01e0ac3e537863841d.png)](https://p1.ssl.qhimg.com/t01e0ac3e537863841d.png)



## 调试音频服务

找到Server端函数audiosrv!PolicyConfigSetDefaultEndpoint：

```
RPCRT4!Invoke+0x70:
00007ff8`078e4410 41ffd2          call    r10 `{`audiosrv!PolicyConfigSetDefaultEndpoint (00007fff`f81d2d10)`}`
```

取消Client所有断点，开始跟踪audiosrv!PolicyConfigSetDefaultEndpoint，该函数调用失败返回80070005h（拒绝访问）。

通过调试不难发现MMDevAPI!CSubEndpointDevice::SetRegValue调用失败（CFG导致截图看到的函数不直观，查看rax即可）。

[![](https://p1.ssl.qhimg.com/t012c1a1d548ea9cfbb.png)](https://p1.ssl.qhimg.com/t012c1a1d548ea9cfbb.png)

然而根本原因是因为操作注册表失败，如下图所示：

[![](https://p1.ssl.qhimg.com/t01416a3880fa13a1ac.png)](https://p1.ssl.qhimg.com/t01416a3880fa13a1ac.png)

参数信息如下：<br>
HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionMMDevicesAudioRender`{`34bb9f66-ad6b-4d17-b74b-7aace4320530`}`<br>
samDesired=0x20106(KEY_WRITE(0x20006) | KEY_WOW64_64KEY (0x0100))

!token查看当前token信息，使用Sysinternals的PsGetsid查看GroupOwner的sid对应NT ServiceAudiosrv。

```
NT ServiceAudiosrv
NT ServiceAudioEndpointBuilder
```

查看注册表键值，上面两个服务虚拟用户只有读取权限，删除自有权限，启用继承父键权限。Render键下还有几个设备也按同样的方式处理。

关于MMDev可参考：<br>[https://docs.microsoft.com/en-us/windows/desktop/coreaudio/audio-endpoint-devices](https://docs.microsoft.com/en-us/windows/desktop/coreaudio/audio-endpoint-devices)

再次调试，注册表操作成功，audiosrv!PolicyConfigSetDefaultEndpoint返回S_OK，重启AudioService服务，问题解决。



## 结束

最后，每次解决问题后，应该反思每一个细节，目标是否明确，思路是否清晰，是否有更好的方式，不断总结优化。

例如对于这类问题，可从符号入手定位问题，可从RPC运行时（rpcrt4）这一层去分析，亦可在rpcrt4!Invoke的监视，等等。。。

Thanks for reading。

```
参考资料：
Google
MSDN
ProcessHacker
Windows Internals
Windbg Help
WRK
```
