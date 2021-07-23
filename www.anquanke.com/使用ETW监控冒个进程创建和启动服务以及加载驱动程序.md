> 原文链接: https://www.anquanke.com//post/id/241806 


# 使用ETW监控冒个进程创建和启动服务以及加载驱动程序


                                阅读量   
                                **111442**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01c6971b8ac1959a0b.jpg)](https://p4.ssl.qhimg.com/t01c6971b8ac1959a0b.jpg)



做edr的同学大概都晓得edr中经常需要监控windows服务以及windows驱动模块的加载的监控，windows驱动的加载的监控的方法通常使用和windows模块加载监控的方法一样，在内核驱动里使用PsSetLoadImageNotifyRoutine设置模块加载回调例程来监控ring3模块以及ring0模块的加载，回调函数 PsSetLoadImageNotifyRoutine的第二个参数判断，如果 Process Id是0 ，则表示加载驱动，如果Process Id非零，则表示加载DLL。但是这种方法监控驱动加载通常的进程Id是0，因为驱动加载的时候使用的是APC线程，当前上下文在系统线程内，所以得不到具体的进程id.

堆栈如下

[![](https://p3.ssl.qhimg.com/t015745c5e36b5a9fc2.png)](https://p3.ssl.qhimg.com/t015745c5e36b5a9fc2.png)



## RetAddr : Args to Child : Call Site

```
00 fffff80004b1748d : fffff8800456b8a0 fffff880031ac0d0 0000000000000001 fffff80004b74dfe : nt!DebugService2+0x5
01 fffff80004b74ecb : fffff880031ac000 fffffa80016de070 fffff8800456b9b8 0000000000000007 : nt!DbgLoadImageSymbols+0x4d
02 fffff80004e47bfd : fffffa8000eeee20 fffff8a00000001c fffff80004d84a30 fffff8800456b888 : nt!DbgLoadImageSymbolsUnicode+0x2b
03 fffff80004e6286b : fffff880031ac000 fffff8800456b8f8 0000000000000000 fffff8800456b8d8 : nt!MiDriverLoadSucceeded+0x2bd
04 fffff80004e64ebd : fffff8800456b9b8 0000000000000000 0000000000000000 0000000000000000 : nt!MmLoadSystemImage+0x80b
05 fffff80004e65875 : 0000000000000001 0000000000000000 0000000000000000 fffffa800231c1e0 : nt!IopLoadDriver+0x44d
06 fffff80004a8b161 : fffff80000000000 ffffffff8000077c fffff80004e65820 fffffa80006db040 : nt!IopLoadUnloadDriver+0x55
07 fffff80004d21166 : 0000000000000000 fffffa80006db040 0000000000000080 fffffa80006b71d0 : nt!ExpWorkerThread+0x111
08 fffff80004a5c486 : fffff80004bf6e80 fffffa80006db040 fffffa80006da680 0000000000000000 : nt!PspSystemThreadStartup+0x5a
09 0000000000000000 : fffff8800456c000 fffff88004566000 fffff8800456ae60 0000000000000000 : nt!KiStartSystemThread+0x16
```

所以在当到达PsSetLoadImageNotifyRoutine的时候加载驱动模块的加载的时候pid就是0了，是否有其他方法可以监控到具体的进程？答案是肯定的， 那就是ETW。

ETW是个windows日志事件Trace，每个Trace日志都有他自己的Guid，要监控服务以及驱动加载的日志就得找到对应的GUID,这个GUID是多少呢，下面我们就来具体分析。<br>
最好的方式就是逆向调试分析，打开一个安装驱动服务的软件，比如我们这次使用的是

[![](https://p2.ssl.qhimg.com/t016a9858db57aae192.png)](https://p2.ssl.qhimg.com/t016a9858db57aae192.png)

[![](https://p0.ssl.qhimg.com/t012371d2bb3a0ddde2.png)](https://p0.ssl.qhimg.com/t012371d2bb3a0ddde2.png)

接下来就是上调试器附加这个进程

[![](https://p3.ssl.qhimg.com/t0120d46c30bd1438bf.png)](https://p3.ssl.qhimg.com/t0120d46c30bd1438bf.png)

在调试器里找到**CreateServiceW**函数，发现这个函数会调用**sechost.dll**的**sechost.CreateServiceW**的函数

[![](https://p1.ssl.qhimg.com/t0140348e3541ef0613.png)](https://p1.ssl.qhimg.com/t0140348e3541ef0613.png)

发现最终的实现是在这个sechost模块的**CreateServiceW**,在**windows/system32**的目录下找到对应的模块，在IDA下以及调试器看到，在运行到最后会调用**NdrClientCall4**

[![](https://p0.ssl.qhimg.com/t0165b94aff0c768d3e.png)](https://p0.ssl.qhimg.com/t0165b94aff0c768d3e.png)

[![](https://p1.ssl.qhimg.com/t01242d19dce66ac4df.png)](https://p1.ssl.qhimg.com/t01242d19dce66ac4df.png)

[![](https://p2.ssl.qhimg.com/t01992f7f4400613aad.png)](https://p2.ssl.qhimg.com/t01992f7f4400613aad.png)

注意该函数的第一个参数是**pStubDescriptor**，它的类型是**PMIDL_STUB_DESC pStubDescriptor**，是一个结构体

<code>typedef struct _MIDL_STUB_DESC `{`<br>
void                                 *RpcInterfaceInformation;<br>
void * )(size_t)                                 *(pfnAllocate;<br>
void()(void *)                                * pfnFree;<br>
union `{`<br>
handle_t              *pAutoHandle;<br>
handle_t              *pPrimitiveHandle;<br>
PGENERIC_BINDING_INFO pGenericBindingInfo;<br>
`}` IMPLICIT_HANDLE_INFO;<br>
const NDR_RUNDOWN                    *apfnNdrRundownRoutines;<br>
const GENERIC_BINDING_ROUTINE_PAIR   *aGenericBindingRoutinePairs;<br>
const EXPR_EVAL                      *apfnExprEval;<br>
const XMIT_ROUTINE_QUINTUPLE         *aXmitQuintuple;<br>
const unsigned char                  *pFormatTypes;<br>
int                                  fCheckBounds;<br>
unsigned long                        Version;<br>
MALLOC_FREE_STRUCT                   *pMallocFreeStruct;<br>
long                                 MIDLVersion;<br>
const COMM_FAULT_OFFSETS             *CommFaultOffsets;<br>
const USER_MARSHAL_ROUTINE_QUADRUPLE *aUserMarshalQuadruple;<br>
const NDR_NOTIFY_ROUTINE             *NotifyRoutineTable;<br>
ULONG_PTR                            mFlags;<br>
const NDR_CS_ROUTINES                *CsRoutineTables;<br>
void                                 *ProxyServerInfo;<br>
const NDR_EXPR_DESC                  *pExprInfo;<br>
`}` MIDL_STUB_DESC;</code>

[![](https://p2.ssl.qhimg.com/t01b787dd56a8a6f1b9.png)](https://p2.ssl.qhimg.com/t01b787dd56a8a6f1b9.png)

最主要的是结构体中的第一个字段**RpcInterfaceInformation**，这个结构是RPC接口的信息，定义这RPC的GUID，当前对应的是全局内存是dword_10008F38，所以它对应的是RPC的GUIID

[![](https://p0.ssl.qhimg.com/t014ec1a9981f8a29c5.png)](https://p0.ssl.qhimg.com/t014ec1a9981f8a29c5.png)

可以看出GUID是 **367ABB81-9844-35F1-AD32-98F038001003**

```
这个RPC  的GUID我们可以在微软的官方网页里找到
```

[https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/4c8b7701-b043-400c-9350-dc29cfaa5e7a](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/4c8b7701-b043-400c-9350-dc29cfaa5e7a)

```
The server interface is identified by UUID 367ABB81-9844-35F1-AD32-98F038001003, version 2.0, using the RPC well-known endpoint "\PIPE\svcctl". The server MUST use RPC over SMB, ncacn_np or RPC over TCP, or ncacn_ip_tcp as the RPC protocol sequence to the RPC implementation, as specified in [MS-RPCE]. The server MUST specify the Simple and Protected GSS-API Negotiation Mechanism (SPNEGO) (0x9) or NT LAN Manager (NTLM) (0xA), or both, as the RPC Authentication Service (as specified in [MS-RPCE]). See [MS-RPCE] section 3.3.1.5.2.2 and [C706] section 13.
```

意思就是说说这个GUID的RPC对应的名字是**\PIPE\svcctl**，而且它是在**server.exe**的这个服务进程里创建的。

接下来的工作就是去逆向**service.exe**这个进程。<br>
在server.exe的程序里我们可以找到对应的RPC 接口函数是RCreateServiceW

[![](https://p3.ssl.qhimg.com/t012d3339c1f3280531.png)](https://p3.ssl.qhimg.com/t012d3339c1f3280531.png)

接着会调用ScCreateServiceRpc

[![](https://p0.ssl.qhimg.com/t018833afc7650bd78b.png)](https://p0.ssl.qhimg.com/t018833afc7650bd78b.png)

在下面的地方我们会看到一个函数<br>**I_RpcBindingInqLocalClientPID(0i64, &amp;Pid);**，这个函数会获取当前RPC的客户端进程id

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0175a8ed9c2b09801f.png)

接着就是输出日志，当然前提是这个日志已经开启并且有人去接收它，

[![](https://p4.ssl.qhimg.com/t0195dadcfe3f8f30b5.png)](https://p4.ssl.qhimg.com/t0195dadcfe3f8f30b5.png)

V22 就是pid，0x28是当前输出的KeyId，a17是模块名，a2是路径

注意此处的**WPP_410463680eaf3577d867156ad5450ae6_Traceguids**并非Etw的事件GUID，需要从**WPP_GLOBAL_Control**对应的结构体去找，在服务的进程的初始化会填充初始化这个GUID

在服务启动入口函数Main里

[![](https://p5.ssl.qhimg.com/t01f799780cff2376a3.png)](https://p5.ssl.qhimg.com/t01f799780cff2376a3.png)

会开启StarttraceSession

[![](https://p3.ssl.qhimg.com/t01fdd995dc99f9b4fc.png)](https://p3.ssl.qhimg.com/t01fdd995dc99f9b4fc.png)

[![](https://p1.ssl.qhimg.com/t01164a19fa0348fe8b.png)](https://p1.ssl.qhimg.com/t01164a19fa0348fe8b.png)

ScStartTracingSession开函数里启动EnableTrace Etw日志

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a4517fa1b889dd25.png)

对应的GUID就是ScmWppLoggingGuid ：**`{`EBCCA1C2-AB46-4A1D-8C2A-906C2FF25F39`}`**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0105c7d4fa5596d2eb.png)

其实**ScmWppLoggingGuid**对应的微软官方Trace名是**Service Control Manager Trace**<br>
最终我们获取的就是这个GUID，当有了这个名字后我们就可以写demo去获取相应的信息来验证我们研究的结果<br>
伪代码如下

`GUID RegistryProvGuid = `{` 0xEBCCA1C2, 0xAB46, 0x4A1D, 0x8c, 0x2a, 0x90, 0x6c, 0x2f, 0xf2, 0x5f, 0x39 `}`;`

………….（注意中间略去ETW的创建开启代码，网络上很多这种代码。）

**最关键的是Monitor的地方对**PEVENT_RECORD**值的判断要判断key id 是否是0x28,因为之前我们逆向时发现输出的key id是0x28**

`Void  Monitor(PEVENT_RECORD pEvent)`<br>``{``<br>`if (pEvent-&gt;EventHeader.EventDescriptor.Id == 0x28)`<br>``{``<br>`int i = 0;`<br>`i++;`<br>``}``<br>`else if (pEvent-&gt;EventHeader.EventDescriptor.Id == 0x2A)`<br><code>`{`<br>
`}`<br>
`}`</code>

写好之后我们就可以调试。使用之前的程序去创建服务。

[![](https://p3.ssl.qhimg.com/t01966a792a751b3f57.png)](https://p3.ssl.qhimg.com/t01966a792a751b3f57.png)

[![](https://p4.ssl.qhimg.com/t01007f7050d427af8e.png)](https://p4.ssl.qhimg.com/t01007f7050d427af8e.png)

他对应的**Pid** 是 **3356**

当点击安装的时候demo断点断捕获下来了

[![](https://p5.ssl.qhimg.com/t012880847802439c9e.png)](https://p5.ssl.qhimg.com/t012880847802439c9e.png)

可以在内存里查看

[![](https://p0.ssl.qhimg.com/t01a06d956debf32f24.png)](https://p0.ssl.qhimg.com/t01a06d956debf32f24.png)

UserData

[![](https://p3.ssl.qhimg.com/t01b0c199bc8083ad81.png)](https://p3.ssl.qhimg.com/t01b0c199bc8083ad81.png)

可以看到前面就是创建的服务名，那个**e4 0d 00 00** 就是进程Pid，内存颠倒过来就是**00000de4 == 3356** , 后面还有一块区域是要创建的服务对应的模块地址。<br>
到此验证ok，还有其他一些**OpenService、StartService**都可以找出来对应的key id，这个读者可以自行去研究发现。
