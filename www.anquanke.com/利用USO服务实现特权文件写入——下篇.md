> 原文链接: https://www.anquanke.com//post/id/209910 


# 利用USO服务实现特权文件写入——下篇


                                阅读量   
                                **240427**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者itm4n，文章来源：itm4n.github.io
                                <br>原文地址：[https://itm4n.github.io/usodllloader-part2/](https://itm4n.github.io/usodllloader-part2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01d5dadea303fae572.png)](https://p4.ssl.qhimg.com/t01d5dadea303fae572.png)



在上一篇文章中，我展示了如何使用**USO客户端**与**USO服务**进行交互，并通过 `StartScan` 命令让其按需加载`windowscoredeviceinfo.dll`。不过这并没有达到我们最终的目的。所以，我对客户端和服务器的一部分进行了逆向工程，以便**通过代码模拟它的行为**，我实现了一个独立的项目，可以在漏洞利用中进行代码重用，简化漏洞利用的过程。



## USO客户端 – 静态分析

虽然我在研究过程中也使用了Ghidra，但为了保持一致性，我在这次演示中会使用IDA。

在IDA中打开`usoclient.exe`之前，我用下面的命令下载了相应的PDB文件。理论上，如果pdb在同一目录下，IDA会自动完成这个操作，但我发现它并不总是有效。然后可以用`File &gt; Load File &gt; PDB File...`加载PDB文件。

`symchk`工具与Windows SDK一起，一般位于`C:/Program Files (x86)Windows Kits10/Debuggersx64`中。我们使用它下载对应的pdb文件。

```
symchk /s "srv*c:symbols*https://msdl.microsoft.com/download/symbols" "c:windowssystem32usoclient.exe"
```

> **注：** PDB代表 “程序数据库”。程序数据库(PDB)是一种专有的文件格式(由微软开发)，用于存储程序(或通常是程序模块，如DLL或EXE)的调试信息。[维基百科](https://en.wikipedia.org/wiki/Program_database)

`usoclient.exe`现在已经在IDA中打开了，符号也加载完毕，我们从哪里开始呢？我们知道 `StartScan` 的命令是一个有效的 “触发器”，所以，我们自然会在二进制文件中寻找这个字符串的出现，并通过 “Xref” 来找出它的使用位置。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//21_IDA-StartScan-XrefsTo.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//21_IDA-StartScan-XrefsTo.png)

`StartScan`字符串在两个函数中被使用：`PerformOperationOnSession()`和`PerformOperationOnManager()`。我们来检查第一个函数，检查它对应的伪代码。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//22_IDA-PerformOperationOnSession.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//22_IDA-PerformOperationOnSession.png)

这似乎是一个 **Switch Case**。输入的内容与一系列硬编码命令进行比较：”StartScan”、”StartDownload”、”StartInstall “等。如果有匹配的命令，就会进入对应的分支。

例如，当使用 “StartScan “选项时，会运行以下代码。

```
v5 = *(_QWORD *)(*(_QWORD *)v3 + 168i64);
v6 = _guard_dispatch_icall_fptr(v3, 0i64);
if ( v6 &gt;= 0 )
  return 0i64;
```

这段代码没有什么意义。<br>
所以，我暂时认为这是一个死胡同，决定改用寻找这个函数的`Xrefs`来往上走。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//23_PerformOperationOnSession-Xrefs.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//23_PerformOperationOnSession-Xrefs.png)

这个函数只被调用一次。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//24_IDA-USOclient-CoSetProxyBlanket.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//24_IDA-USOclient-CoSetProxyBlanket.png)

然后，我快速查看了一下伪代码，我立刻发现了以下调用。`CoInitializeEx()`、`CoCreateInstance()`、`CoSetProxyBlanket()`等。因为之前已经玩过COM(Component Object Model)，所以我认出了API调用的顺序。<br>
我们来仔细看看下面的调用。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//25_IDA-USOclient-CoCreateInstance.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//25_IDA-USOclient-CoCreateInstance.png)

根据微软的文档，你可以调用`CoCreateInstance()`来**创建一个与指定的CLSID相关联的类的单个未初始化对象**([CoCreateInstance函数](https://docs.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance))

函数原型:

```
HRESULT CoCreateInstance(
  REFCLSID  rclsid,
  LPUNKNOWN pUnkOuter,
  DWORD     dwClsContext,
  REFIID    riid,
  LPVOID    *ppv
);
```
<li>
`rclsid`是与创建对象的数据和代码相关的CLSID。</li>
<li>
`riid`是与对象通信的接口标识符的引用。</li>
如果我们想要将此用于USO客户端的调用，则意味只需要创建CLSID为`b91d5831-bbbd-4608-8198-d72e155020f7`的对象，并使用IID为`07f3afac-7c8a-4ce7-a5e0-3d24ee8a77e0`的接口与其通信。

在读了[James Forshaw](https://twitter.com/tiraniddo)的文章[利用任意文件写入进行本地权限提升](https://googleprojectzero.blogspot.com/2018/04/windows-exploitation-tricks-exploiting.html)后，我知道接下来要做什么了。多亏了他的名为`OleViewDotNet`的工具，**对DCOM对象进行逆向**非常的容易。

如果你熟悉这个概念，可以跳过下一部分。此处了解[更多信息](https://docs.microsoft.com/en-us/windows/win32/com/inter-object-communication)。



## 关于(D)COM的简单介绍

正如我前面所说，COM是 **Component Object Model** 的缩写。它是微软定义的进程间通信标准。由于我自己对这个技术不是很了解，所以就不详细介绍了。

不过需要注意的关键点是客户端和服务器之间的**通信是如何完成的**。下面的图上有描述。客户端的调用经过一个****Proxy****，然后经过一个****Channel****，这个 **Channel** 是 **COM** 的一部分。经过marshaled的调用由于 **RPC Runtime** 传输到服务器的进程中，最后由****Stub****对参数进行unmarshaled，再转发给服务器。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//dcom-marshaling.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//dcom-marshaling.png)

后果是，我们只能找到客户端代理的定义，而且，我们可能会错过一些服务器端的关键信息。



## 对COM通信进行逆向

让我们开始COM对象的逆向工程。使用`OleViewDotNet`让我们知道**它的CLSID**，这一步比较的简单。

首先，我们可以通过 `Registry &gt; Local Services`，**列举主机上运行的服务所暴露的所有对象**。因为我们也知道服务的名称，所以我们可以通过关键字`orchestrator`缩小列表范围。**这将产生一些对象**，我们可以手动检查以找到我们要找的对象。`UpdateSessionOrchestrator`.这个**CLSID**与我们之前在逆向工程USO客户端时看到的**CLSID一致：`b91d5831-b1bd-4608-8198-d72e155020f7`。

下一步将是展开相应的节点，以便枚举对象的所有接口。然而，在这种情况下，有时它会失败，并产生以下错误：`Error querying COM interface - ClassFactory cannot supply requested class`。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//26_OleViewDotNet-Orchestrator-Failed.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//26_OleViewDotNet-Orchestrator-Failed.png)

我们只能手动操作了，对客户端进行动态分析，以了解RPC调用的工作情况。

为此，我使用了这三个工具：
<li>
**IDA**（配置了调试符号）。</li>
<li>
**IDA**的x86/64 Windows调试服务器-`C:Program Files (x86)IDA 6.8dbgsrvwin64_remotex64.exe`。</li>
<li>
**WinDbg**（配置了调试符号）。</li>
We already know that the `CoCreateInstance()` call is used to instantiate the remote COM object. As a result the variable `pInterface`, as its name implies, holds a pointer to the interface with the IID `07f3afac-7c8a-4ce7-a5e0-3d24ee8a77e0`, which will be used to communicate with the object. My goal now is to understand what happens next. Therefore, I put a breakpoint on the first `_guard_dispatch_icall_fptr` call that comes right after.<br>
我们已经知道，`CoCreateInstance()` 的调用是用来实例化远程COM对象的，因此变量 `pInterface` 如它的名字一样，有一个指向IID为 “07f3afac-7c8a-4ce7-a5e0-3d” 接口的指针，它将被用来与对象进行通信。我现在的目标是了解接下来会发生什么。因此，我在紧接着的第一个`_guard_dispatch_icall_fptr`调用上设置了一个断点。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//27_IDA-call-sequence.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//27_IDA-call-sequence.png)

以下是调用前程序的执行过程：
<li>
`RCX'寄存器保存着接口指针的位置（即`pInterface`）。</li>
<li>
`RCX`所指向的值被写入RAX，即`RAX=pInterface`。</li>
1. 储存在 “RSI “中的值被复制到 “RDX “中。
<li>
`RAX+0x28`指向的值被载入`RAX`，即`ProxyVTable[5]`。</li>
[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//28_IDA-break-1.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//28_IDA-break-1.png)

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//29_IDA-break-1-registers.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//29_IDA-break-1-registers.png)

`RCX`的值是`0x000002344FA53D68`。让我们看看用WinDbg能在这个地址找到什么。

```
0:000&gt; dqs 0x00002344FA53D68 L1
00000234`4fa53d68  00007ff8`e48fd560 usoapi!IUpdateSessionOrchestratorProxyVtbl+0x10
```

我们找到UpdateSessionOrchestrator的接口的Proxy VTable的起始地址。然后我们可以查看VTable中的所有指针。

```
0:000&gt; dqs 0x00007ff8e48fd560 LB
00007ff8`e48fd560  00007ff8`e48f8040 usoapi!IUnknown_QueryInterface_Proxy
00007ff8`e48fd568  00007ff8`e48f7d90 usoapi!IUnknown_AddRef_Proxy
00007ff8`e48fd570  00007ff8`e48f7ed0 usoapi!IUnknown_Release_Proxy
00007ff8`e48fd578  00007ff8`e48f7dc0 usoapi!ObjectStublessClient3
00007ff8`e48fd580  00007ff8`e48f8090 usoapi!ObjectStublessClient4
00007ff8`e48fd588  00007ff8`e48f7e80 usoapi!ObjectStublessClient5
00007ff8`e48fd590  00007ff8`e48f7ef0 usoapi!ObjectStublessClient6
00007ff8`e48fd598  00007ff8`e48f7e60 usoapi!ObjectStublessClient7
00007ff8`e48fd5a0  00007ff8`e49068b0 usoapi!IID_IMoUsoUpdate
00007ff8`e48fd5a8  00007ff8`e48fefb0 usoapi!CAutomaticUpdates::`vftable'+0x3b0
00007ff8`e48fd5b0  00000000`00000019

```

前三个函数是`QueryInterface`、`AddRef`和`Release`。这三个函数是COM接口从`IUnknown`继承的函数。然后，后面还有5个函数，但我们不知道它们的名字。

为了找到更多关于VTable的信息，我们必须检查服务端。我们知道COM对象的名字—“UpdateSessionOrchestrator”，我们也知道服务的名字—“USOsvc”，所以理论上，我们应该能在 “usosvc.dll” 中找到我们需要的所有信息。

```
.rdata:00000001800582F8 dq offset UpdateSessionOrchestrator::QueryInterface(void)
.rdata:0000000180058300 dq offset UpdateSessionOrchestrator::AddRef(void)
.rdata:0000000180058308 dq offset UpdateSessionOrchestrator::Release(void)
.rdata:0000000180058310 dq offset UpdateSessionOrchestrator::CreateUpdateSession(tagUpdateSessionType,_GUID const &amp;,void * *)
.rdata:0000000180058318 dq offset UpdateSessionOrchestrator::GetCurrentActiveUpdateSessions(IUsoSessionCollection * *)
.rdata:0000000180058320 dq offset UpdateSessionOrchestrator::LogTaskRunning(ushort const *)
.rdata:0000000180058328 dq offset UpdateSessionOrchestrator::CreateUxUpdateManager(IUxUpdateManager * *)
.rdata:0000000180058330 dq offset UpdateSessionOrchestrator::CreateUniversalOrchestrator(IUniversalOrchestrator * *)
```

这里是完整的VTable，我们可以看到偏移量5的函数是`UpdateSessionOrchestrator::LogTaskRunning(ush)`

最后，RDX的值是`0x000002344FA39450`。我们也来看看这个地址能找到什么，这次用IDA找找看

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//31_IDA-break-1-startscan-str.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//31_IDA-break-1-startscan-str.png)

这个地方只是一个指针，指向unicode字符串`L"StartScan"`。

所有这些信息可以归纳如下：

```
RAX = VTable[5] = `UpdateSessionOrchestrator::LogTaskRunning(ushort const *)`
RCX = argv[0]   = `UpdateSessionOrchestrator pInterface`
RDX = argv[1]   = L"StartScan"
```

如果我们考虑到Windows的x86_64调用惯例，可以用下面的伪代码来表示。

```
pInterface-&gt;LogTaskRunning(L"StartScan");
```

同样的过程可以应用于下一次调用。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//32_IDA-break-2.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//32_IDA-break-2.png)

这将产生以下结果：

```
RAX = VTable[0] = `UpdateSessionOrchestrator::QueryInterface()`
RCX = argv[0]   = `UpdateSessionOrchestrator pInterface`
RDX = argv[1]   = `*GUID(c57692f8-8f5f-47cb-9381-34329b40285a)`
R8  = argv[2]   = Output pointer location
```

这里，返回的值是 “NULL”，所以，”if”语句后面的所有代码都将被忽略。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//33_IDA-break-2-check.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//33_IDA-break-2-check.png)

因此，我们可以跳过它，直接跳转到这里。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//34_IDA-break-3.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//34_IDA-break-3.png)

不错，我们越来越接近目标`PerformOperationOnSession()`了。

在逆向工程过程中，我们发现如下的调用。

```
RAX = VTable[3] = `UpdateSessionOrchestrator::CreateUpdateSession(tagUpdateSessionType,_GUID const &amp;,void * *)`
RCX = argv[0]   = `UpdateSessionOrchestrator pInterface`
RDX = argv[1]   = 1
R8  = argv[2]   = `*GUID(fccc288d-b47e-41fa-970c-935ec952f4a4)`
R9  = argv[3]   = `void **param_3 (usoapi!IUsoSessionCommonProxyVtbl+0x10)` --&gt; IUsoSessionCommon pProxy
```

在这里，我们可以看到另一个接口被嵌入。`IUsoSessionCommon`.它的IID是`fccc288d-b47e-41fa-970c-935ec952f4a4`，它的VTable有68个条目，所以我在这里不列出所有的功能。

Next there is a `CoSetProxyBlanket()` call. This is a standard WinApi function that is used to **set the authentication information that will be used to make calls on the specified proxy** (Source: [CoSetProxyBlanket function](https://docs.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cosetproxyblanket)).<br>
接下来有一个`CoSetProxyBlanket()`的调用。这是一个标准的WinApi函数，用于 **设置在指定代理上进行调用的认证信息** ([CoSetProxyBlanket函数](https://docs.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cosetproxyblanket))。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//35_IDA-CoSetProxyBlanket.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//35_IDA-CoSetProxyBlanket.png)

如果我们将所有的十六进制值变成Win32常量，就会产生以下API调用。

```
IUsoSessionCommonPtr usoSessionCommon;
CoSetProxyBlanket(usoSessionCommon, RPC_C_AUTHN_DEFAULT, RPC_C_AUTHZ_DEFAULT, COLE_DEFAULT_PRINCIPAL, RPC_C_AUTHN_LEVEL_DEFAULT, RPC_C_IMP_LEVEL_IMPERSONATE, nullptr, NULL);
```

现在，我们可以进入 “PerformOperationOnSession() “函数查看，又回到了之前那段没有意义的代码。不过，由于我们刚刚的逆向，目标现在已经越来越清晰了。这是一个对`IUsoSessionCommon`代理的简单调用。我们只需要确定调用**哪个函数**，用**哪个参数**。

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//36_IDA-break-4.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//36_IDA-break-4.png)

[![](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//37_IDA-break-4-instructions.png)](https://itm4n.github.io/assets/posts/2019-08-19-usodllloader-part2//37_IDA-break-4-instructions.png)

有了这个最后的断点，函数的偏移量和参数就可以很容易地确定。

```
RAX = VTable[21] = combase_NdrProxyForwardingFunction21
RCX = argv[0]    = IUsoSessionCommon pProxy
RDX = argv[1]    = 0
R8  = argv[2]    = 0
R9  = argv[3]    = L"ScanTriggerUsoClient"
```

这就相当于执行了下面的伪代码。

```
pProxy-&gt;Proc21(0, 0, L"ScanTriggerUsoClient");
```

如果把所有的部分放在一起，USO客户端中的 “StartScan “操作可以用下面的代码来表示。

```
HRESULT hResult;
// Initialize the COM library
hResult = CoInitializeEx(0, COINIT_MULTITHREADED);
// Create the remote UpdateSessionOrchestrator object
GUID CLSID_UpdateSessionOrchestrator = `{` 0xb91d5831, 0xb1bd, 0x4608, `{` 0x81, 0x98, 0xd7, 0x2e, 0x15, 0x50, 0x20, 0xf7 `}` `}`;
IUpdateSessionOrchestratorPtr updateSessionOrchestrator;
hResult = CoCreateInstance(CLSID_UpdateSessionOrchestrator, nullptr, CLSCTX_LOCAL_SERVER, IID_PPV_ARGS(&amp;updateSessionOrchestrator));
// Invoke LogTaskRunning() 
updateSessionOrchestrator-&gt;LogTaskRunning(L"StartScan");
// Create an update session 
IUsoSessionCommonPtr usoSessionCommon;
GUID IID_IUsoSessionCommon = `{` 0xfccc288d, 0xb47e, 0x41fa, `{` 0x97, 0x0c, 0x93, 0x5e, 0xc9, 0x52, 0xf4, 0xa4 `}` `}`;
updateSessionOrchestrator-&gt;CreateUpdateSession(1, &amp;IID_IUsoSessionCommon, &amp;usoSessionCommon);
// Set the authentication information 
CoSetProxyBlanket(usoSessionCommon, RPC_C_AUTHN_DEFAULT, RPC_C_AUTHZ_DEFAULT, COLE_DEFAULT_PRINCIPAL, RPC_C_AUTHN_LEVEL_DEFAULT, RPC_C_IMP_LEVEL_IMPERSONATE, nullptr, NULL);
// Trigger the "StartScan" action
usoSessionCommon-&gt;Proc21(0, 0, L"ScanTriggerUsoClient")
// Close the COM library  
CoUninitialize();
```



## 结论

知道了USO客户端的工作原理以及它如何触发特权操作，现在就可以将这种行为复制为独立的应用程序。[UsoDllLoader](https://github.com/itm4n/UsoDllLoader)。当然，从这个逆向工程过程过渡到实际的C++代码需要更多的工作。

关于逆向工程部分，我不得不说这并不难，因为COM客户端已经存在，而且Windows默认提供。`OleViewDotNet`最后也确实帮了大忙。它能够生成第二个接口（UsoSessionCommon）的代码—你知道的，有68个函数的那个接口。

好了，这篇文章就到此为止。希望大家喜欢。



## 参考文献
<li>微软文档 – CoCreateInstance。<br>[https://docs.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance](https://docs.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance)
</li>
<li>微软文件 — — 对象间通信<br>[https://docs.microsoft.com/en-us/windows/win32/com/inter-object-communication](https://docs.microsoft.com/en-us/windows/win32/com/inter-object-communication)
</li>
<li>Microosft文件 — — x64调用惯例<br>[https://docs.microsoft.com/en-us/cpp/build/x64-calling-convention?view=vs-2019](https://docs.microsoft.com/en-us/cpp/build/x64-calling-convention?view=vs-2019)
</li>
<li>Windows开发技巧。利用任意文件写入来提升本地的权限。<br>[https://googleprojectzero.blogspot.com/2018/04/windows-exploitation-tricks-exploiting.html](https://googleprojectzero.blogspot.com/2018/04/windows-exploitation-tricks-exploiting.html)
</li>