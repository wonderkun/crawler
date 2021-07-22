> 原文链接: https://www.anquanke.com//post/id/105840 


# Windows利用技巧：利用任意文件写入漏洞实现本地权限提升


                                阅读量   
                                **184231**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://googleprojectzero.blogspot.com/
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2018/04/windows-exploitation-tricks-exploiting.html](https://googleprojectzero.blogspot.com/2018/04/windows-exploitation-tricks-exploiting.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0145ad1d8ba034907a.jpg)](https://p2.ssl.qhimg.com/t0145ad1d8ba034907a.jpg)



## 一、前言

之前我曾在一篇[文章](https://googleprojectzero.blogspot.com/2017/08/windows-exploitation-tricks-arbitrary.html)中介绍过一种技术，可以利用Windows系统上的任意目录创建漏洞来获得系统上任意文件的访问权限。在即将推出的Spring Creators Update（RS4）系统上，前面提到过的这种漏洞（滥用挂载点链接到文件）已经被修复。这是非常典型的一个良性例子，通过对漏洞利用方法的详细分析，开发者就能具有充足的动力，寻找修复漏洞利用方法的各种途径。

在本文中，我将介绍一种新的技术来利用Windows 10系统上更为常见的任意文件写入漏洞。微软也许会进一步加固操作系统，使这类漏洞利用起来更加困难。最近微软修复了Project Zero报告的一个漏洞（issue [1428](https://bugs.chromium.org/p/project-zero/issues/detail?id=1428)），这里我会详细漏洞细节，向大家演示该漏洞的利用方法。

所谓的任意文件写入漏洞，指的是用户可以在正常情况下无法访问的某个目录中创建或者修改文件。之所以会出现这种情况，原因可能是某个特权服务没有正确过滤用户传递进来的信息，符号链接植入攻击也有可能导致这种后果（用户将链接写入某个目录中，随后被特权服务所使用）。如果攻击者不仅能够控制文件的写入位置，也能控制文件内容，那么这是最为理想的一种漏洞场景，本文针对的正是这种场景。

任意文件写入漏洞常见的一种利用方法就是执行[DLL劫持](https://cwe.mitre.org/data/definitions/427.html)攻击。当Windows可执行文件开始执行时，NTDLL中的初始化loader会尝试查找所有导入的DLL。loader对DLL的检查过程比我们想象中的还要复杂一些，简而言之，该过程包含如下几个步骤：

1、检查[Known DLLs](https://blogs.msdn.microsoft.com/larryosterman/2004/07/19/what-are-known-dlls-anyway/)，也就是操作系统预先缓存的一些已知DLL的列表。如果找到对应的DLL，则将DLL从预加载的section对象映射到内存中。

2、检查应用目录。比如如果程序正在导入`TEST.DLL`，并且程序所处目录为`C:APP`，那么loader就会检查`C:APPTEST.DLL`这个文件。

3、检查系统目录，比如`C:WINDOWSSYSTEM32`以及`C:WINDOWS`。

4、如果以上查找过程全部失败，则搜索当前的`PATH`环境变量。

DLL劫持的目标是找到处于高权限运行下的某个可执行程序，该程序会从某个目录加载某个DLL文件，而攻击者刚好可以往该目录中写入数据。只有当loader无法从前几个检查步骤中找到对应的DLL，这种劫持攻击才能奏效。

如果想成功执行DLL劫持攻击，有两个问题比较棘手，需要解决：

1、我们通常需要创建特权进程的一个新实例，因为当该进程首次执行时，待导入的大多数DLL已经被解析过。

2、大多数以特权用户身份运行的系统二进制文件、可执行程序以及DLL基本都位于`SYSTEM32`目录中。

第二个问题意味着在步骤2以及步骤3中，loader始终会去搜索`SYSTEM32`目录中的DLL文件。如果我们无法在目标环境中覆盖DLL文件（如果DLL已处于载入状态，则无法写入该文件），就很难找到合适的DLL来劫持。为了绕过这些问题，一种典型的方法就是挑选不在`SYSTEM32`中的某个可执行文件，并且该文件很容易被激活（比如通过加载COM服务器或者运行计划任务）。

即使我们找到了合适的目标程序来进行DLL劫持，但劫持过程看起来可能略显丑陋。某些情况下我们需要实现原始DLL的导出函数，否则DLL无法被成功加载。在其他情况下，运行代码的最佳位置就是DllMain，但这会引入其他问题（比如在[loader lock](https://msdn.microsoft.com/en-us/library/windows/desktop/dn633971%28v=vs.85%29.aspx)中运行代码）。对于我们来说，最好的一种场景就是找到一个特权服务，该服务可以加载任意DLL，不需要劫持，也不需要生成“正确”的特权进程。那么问题来了，这种服务是否真的存在？

事实证明的确存在这样一个服务，并且该服务之前已经被滥用过两次，一次是被Lokihardt用来实现沙箱逃逸，另一次是被我用来实现用户权限到系统权限的[提升](https://bugs.chromium.org/p/project-zero/issues/detail?id=887)。这个服务的名称为“Microsoft (R) Diagnostics Hub Standard Collector Service”，我们可以简称为DiagHub。

DiagHub是Windows 10引入的一种服务，Windows 7以及8.1上也有执行类似任务的服务：IE ETW Collector。该服务的目的是通过ETW（Event Tracing for Windows）为沙箱应用（特别是Edge以及Internet Explorer）收集诊断信息。该服务有一个有趣的功能，可以配置为从`SYSTEM32`目录中加载任意一个DLL，这正是Lokihardt和我利用的功能，最终借此实现了权限提升（EoP）。该服务的所有功能均通过已注册的一个DCOM对象对外公开，因此为了加载我们自己的DLL，我们需要弄清楚如何调用这个DCOM对象上的方法。现在你可以直接跳到本文尾部，但如果你想知道我如何发现DCOM对象的具体实现方式，可以继续阅读以下内容。



## 二、逆向分析DCOM对象

接下来请跟随我的脚步，一步步探索如何发现某个未知DCOM对象所支持的接口，找到该接口的实现方式，以便对其进行逆向分析。为了完成任务，一般我会使用两种方法，要么使用IDA Pro或者类似工具进行逆向分析，要么先在系统上做些调研工作，以缩小调查范围。这里我们可以使用第二种方法，因为该方法能够提供更加丰富的信息。我并不了解Lokihardt解决问题的方法，这里我们以自己的方式解决这个问题。

选择这种方法，我们需要用到一些工具，比如github上的[OleViewDotNet](https://github.com/tyranid/oleviewdotnet/releases) v1.4+（OVDN）以及[SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk)中的WinDBG工具。第一步是找到DCOM对象的注册信息，查找那些接口可以访问。我们知道DCOM对象托管在某个服务中，所以启动OVDN工具后，我们可以使用**Registry ⇒ Local Services**菜单，这样就能导入对外开放COM对象的已注册的系统服务。如果此时你搜索“Microsoft (R) Diagnostics Hub Standard Collector Service”这个服务（建议使用过滤器，查找起来更加方便），那么应该能在服务列表中找到它的身影。打开该服务的树形结构后，我们可以看到“Diagnostics Hub Standard Collector Service”这个子节点，这就是托管的DCOM对象。如果我们打开这个节点，该工具就会创建该对象，然后查询可以远程访问的所有COM接口，这样我们就能知道该对象支持的所有接口，如下图所示：

[![](https://p5.ssl.qhimg.com/t010ba35e993715366c.png)](https://p5.ssl.qhimg.com/t010ba35e993715366c.png)

这里我们需要检查一下访问这个DCOM对象所需的安全等级。右键单击class节点，选择**View Access Permissions**或者**View Launch Permissions**，这样就能显示权限信息。在本例中，我们可以从IE Protected Mode或者Edge的AppContainer沙箱（包括LPAC）来访问这个DCOM对象。

[![](https://p5.ssl.qhimg.com/t010a51540ddc892745.png)](https://p5.ssl.qhimg.com/t010a51540ddc892745.png)

在这些接口中我们只关心标准的接口。有些时候目标中可能存在比较有趣的一些接口，但本例中我们并没有找到这些接口。在这些标准接口中有两个我们比较关心：**IStandardCollectorAuthorizationService**以及**IStandardCollectorService**。其实我可以告诉大家**IStandardCollectorService**服务比较有趣，但由于下面的操作过程对每个接口来说都适用，因此我们可以随便挑一个接口来处理。如果我们右键单击接口节点，选择**Properties**，就可以查看该注册接口的详细信息。

[![](https://p4.ssl.qhimg.com/t01e94f60d4b5941004.png)](https://p4.ssl.qhimg.com/t01e94f60d4b5941004.png)

这里没有太多的信息可以帮助我们，不过我们可以发现这个接口上对应有8个方法。与其他许多COM注册信息一样，这个值也有可能是一个错误值，不过这里我们选择信任这个信息。为了理解这些方法具体是什么，我们需要跟踪COM服务器中`IStandardCollectorService`的实现方式。掌握这个信息后，我们就能集中逆向分析精力来分析正确的二进制程序以及正确的方法。对于进程内COM对象而言，想完成这个任务相对来说比较容易，因为我们可以通过dereference部分指针（即*操作）来直接查询某个对象的VTable指针。然而，对于进程外（OOP）的情况来说就比较复杂一些，这是因为我们所调用的进程内对象实际上是远程对象的代理，如下图所示：

[![](https://p0.ssl.qhimg.com/t01a77abf56f3ab5a5f.png)](https://p0.ssl.qhimg.com/t01a77abf56f3ab5a5f.png)

即便如此，我们依然可以通过提取保存在服务器进程中的对象信息来查找OOP对象的VTable。在之前的界面中右键点击“Diagnostics Hub Standard Collector Service”节点，选择**Create Instance**，这样可以创建COM对象的一个新实例，如下图所示：

[![](https://p3.ssl.qhimg.com/t018ee27ebea30bdaa5.png)](https://p3.ssl.qhimg.com/t018ee27ebea30bdaa5.png)

这个实例可以告诉我们许多基本信息，比如该对象的CLSID（这里这个值为``{`42CBFAA7-A4A7-47BB-B422-BD10E9D02700`}``，后面我们会用到这个值）以及支持的接口信息。现在需要确保的是我们已连接至我们感兴趣的那个接口。我们可以先选择窗口下半部分的`IStandardCollectorService`服务，然后在**Operations**菜单的底部，选择**Marshal ⇒ View Properties**。如果操作成功，我们可以看到如下界面：

[![](https://p4.ssl.qhimg.com/t01f1c8020926840d4d.png)](https://p4.ssl.qhimg.com/t01f1c8020926840d4d.png)

这个界面包含很多信息，但最重要的两个信息是托管服务的Process ID以及IPID（Interface Pointer Identifier）。本例中由于该服务运行在自己的进程中，因此Process ID是显而易见的一个值，但这并不适用于所有情况：有时候当我们创建一个COM对象时，我们并不知道哪个进程在托管COM服务器，此时这个信息就非常有用。IPID是DCOM对象服务器端托管进程中的唯一标识，我们可以使用Process ID以及IPID值来查找这个服务器，然后从中找出实现COM方法的VTable的具体位置。需要注意的是，与IPID对应的Process ID的大小最大为16个比特，但现在Windows中可能存在更大的PID，因此我们有时候需要手动查找目标进程，或者多次重启服务，直到得到合适的PID值为止。

现在我们可以利用OVDN的一个功能，访问服务器进程的内存空间，查找对应的IPID信息。当然你可以通过主菜单的**Object ⇒ Processes**来获取所有进程中对应的这个信息，但我们已经知道待处理的是哪个进程，因此只需要点击上图中Process ID旁边的**View**按钮即可。对了，我们需要以管理员权限运行OVDN，否则无法打开服务进程。如果前面我们没有以管理员权限运行，那么此时该工具会要求我们配置符号支持（symbol support）选项，因为OVDN需要公共符号（public symbol）来查找COM DLL中待解析的正确位置。我们需要使用WinDBG自带的DBGHELP.DLL，因为该DLL支持远程符号服务器。符号选项的配置信息如下图所示：

[![](https://p3.ssl.qhimg.com/t01a2a699888590d19d.png)](https://p3.ssl.qhimg.com/t01a2a699888590d19d.png)

如果所有选项配置正确，并且我们也以管理员权限来运行该工具，那么我们应该能够获得关于IPID的更多信息，如下图所示：

[![](https://p1.ssl.qhimg.com/t01745513482ff12af2.png)](https://p1.ssl.qhimg.com/t01745513482ff12af2.png)

这里最有用的两条信息就是Interface指针（堆分配对象的地址，以便我们查看该对象状态）以及接口对应的VTable指针。VTable地址可以告诉我们COM服务器实现的具体位置。在上图中，我们可知VTable位于与主可执行文（DiagnosticsHub.StandardCollector.Server）不同的另一个模块中（DiagnosticsHub.StandardCollector.Runtime）。我们可以使用WinDBG attach到服务进程上，导出VTable地址处的符号，验证这个VTable地址是否正确。前文提到过这里有8个方法，为了找到这8个方法，我们可以使用如下命令：

```
dqs DiagnosticsHub_StandardCollector_Runtime+0x36C78 L8
```

需要注意的是，WinDBG会将模块名中的点转化为下划线。如果这条命令执行成功，我们可以得到如下结果：

[![](https://p1.ssl.qhimg.com/t019bf440b0cf6f0508.png)](https://p1.ssl.qhimg.com/t019bf440b0cf6f0508.png)

提取出这些信息后，我们就可以知道这些方法的名称（如下所示）以及方法在二进制中的具体地址。我们可以设置断点，查看正常操作期间有哪些方法被调用，或者可以根据这些信息开始我们的逆向分析之旅。

```
ATL::CComObject&lt;StandardCollectorService&gt;::QueryInterface
ATL::CComObjectCached&lt;StandardCollectorService&gt;::AddRef
ATL::CComObjectCached&lt;StandardCollectorService&gt;::Release
StandardCollectorService::CreateSession
StandardCollectorService::GetSession
StandardCollectorService::DestroySession
StandardCollectorService::DestroySessionAsync
StandardCollectorService::AddLifetimeMonitorProcessIdForSession
```

我们得到的方法貌似是正确的：最开头的3个方法为COM对象的标准方法，由ATL库实现，后面跟着5个方法，由`StandardCollectorService`类实现。作为公共符号，我们无法从中了解需要往COM服务器传递哪些参数。由于C++名称中包含某些类型信息，IDA Pro有可能提取出我们所需的参数信息，但不一定能告诉我们传递给函数的任何结构体的具体格式。幸运的是，COM代理在具体实现中使用了NDR（Network Data Representation）解释器来对数据进行编码，我们有可能将NDR字节码还原成我们可以理解的格式。对于本文的这个案例，我们可以回到最初的服务信息窗口，右键点击**IStandardCollectorService**节点，选择**View Proxy Definition**。这样OVDN就能解析NDR代理信息，如下所示：

[![](https://p2.ssl.qhimg.com/t0130ea9d4d0eae8bab.png)](https://p2.ssl.qhimg.com/t0130ea9d4d0eae8bab.png)

查看代理的定义后，我们也能解析出该代理库实现的其他任何接口，这些信息可能对我们后面的逆向分析来说有点用。经过反编译的代理定义代码类似于C#形式的伪代码，我们可以根据需要转化为能够正常工作的C#或者C++代码。需要注意的是代理定义中并不包含方法的名称，但我们之前已经提取过这些信息。因此，稍作处理后，我们就能得到如下定义代码：

```
[uuid("0d8af6b7-efd5-4f6d-a834-314740ab8caa")]
struct IStandardCollectorService : IUnknown `{`
   HRESULT CreateSession(_In_ struct Struct_24* p0, 
                         _In_ IStandardCollectorClientDelegate* p1,
                         _Out_ ICollectionSession** p2);
   HRESULT GetSession(_In_ GUID* p0, _Out_ ICollectionSession** p1);
   HRESULT DestroySession(_In_ GUID* p0);
   HRESULT DestroySessionAsync(_In_ GUID* p0);
   HRESULT AddLifetimeMonitorProcessIdForSession(_In_ GUID* p0, [In] int p1);
`}`
```

目前我们还缺失最后一块拼图：我们并不知道`Struct_24`结构体的具体定义。这个信息有可能通过逆向分析得到，但幸运的是这里我们不需要那么麻烦。NDR字节码知道如何编解码这个结构，因此OVDN可以自动地提取出这个结构的定义：我们可以选择**Structures**标签页，找到`Struct_24`即可：

[![](https://p1.ssl.qhimg.com/t0120ecd57a1e0c692b.png)](https://p1.ssl.qhimg.com/t0120ecd57a1e0c692b.png)

在后面的逆向分析过程中，我们可以根据实际需要重复这个过程，直到解开所有谜题。现在我们准备开始利用DiagHub服务，通过一个实际可用的例子给大家演示该服务的利用方法。



## 三、利用方法

根据前面的逆向分析结果，为了从`SYSTEM32`目录中加载DLL，我们需要做如下操作：

1、使用`IStandardCollectorService::CreateSession`创建一个新的Diagnostics Session。

2、在新会话上调用`ICollectionSession::AddAgent`方法，传入待加载的DLL名称（不需要包含任何路径信息）。

`ICollectionSession::AddAgent`加载代码的简化版如下所示：

```
void EtwCollectionSession::AddAgent(LPWCSTR dll_path, 
                                   REFGUID guid) `{`
 WCHAR valid_path[MAX_PATH];
 if ( !GetValidAgentPath(dll_path, valid_path)) `{`
   return E_INVALID_AGENT_PATH;
 HMODULE mod = LoadLibraryExW(valid_path, 
       nullptr, LOAD_WITH_ALTERED_SEARCH_PATH);
 dll_get_class_obj = GetProcAddress(hModule, "DllGetClassObject");
 return dll_get_class_obj(guid);
`}`
```

从中可知，代码会检查agent path是否有效，然后返回一个完整路径（这正是之前存在EoP漏洞的地方，没有经过足够的校验）。代码使用`LoadLibraryEx`加载这个路径，然后获取DLL中的`DllGetClassObject`导出函数，然后再调用这个函数。因此为了得到代码执行机会，我们只需要实现这个方法，然后将文件放入`SYSTEM32`目录即可。`DllGetClassObject`会在loader lock之外被调用，所以基本上我们可以为所欲为。我们可以采用如下代码（移除了其中的错误处理代码）来加载名为`dummy.dll`的一个DLL文件：

```
IStandardCollectorService* service;
CoCreateInstance(CLSID_CollectorService, nullptr, CLSCTX_LOCAL_SERVER, IID_PPV_ARGS(&amp;service));

SessionConfiguration config = `{``}`;
config.version = 1;
config.monitor_pid = ::GetCurrentProcessId();
CoCreateGuid(&amp;config.guid);
config.path = ::SysAllocString(L"C:Dummy");
ICollectionSession* session;
service-&gt;CreateSession(&amp;config, nullptr, &amp;session);

GUID agent_guid;
CoCreateGuid(&amp;agent_guid);
session-&gt;AddAgent(L"dummy.dll", agent_guid);
```

现在我们只需要实现任意文件写入目标，将任意DLL放入`SYSTEM32`目录中，得到加载机会，提升权限。为了完成这个任务，我决定使用我在`Storage Service`的`SvcMoveFileInheritSecurity` RPC方法中找到的一个漏洞。这个函数之所以引起我的注意，原因是[Clément Rouault](https://twitter.com/hakril)和[Thomas Imbert](https://twitter.com/masthoon)在[PACSEC 2017](https://pacsec.jp/psj17/PSJ2017_Rouault_Imbert_alpc_rpc_pacsec.pdf)上曾发现并演示过的一个漏洞（ALPC漏洞），漏洞利用过程中用到了这个函数。虽然这种方法的确是利用该漏洞的一条途径，但我发现其实这里潜伏着两个漏洞（至少包含普通用户权限提升漏洞）。未经修补前的`SvcMoveFileInheritSecurity`的代码如下所示：

```
void SvcMoveFileInheritSecurity(LPCWSTR lpExistingFileName, 
                               LPCWSTR lpNewFileName, 
                               DWORD dwFlags) `{`
 PACL pAcl;
 if (!RpcImpersonateClient()) `{`
   // Move file while impersonating.
   if (MoveFileEx(lpExistingFileName, lpNewFileName, dwFlags)) `{`
     RpcRevertToSelf();
     // Copy inherited DACL while not.
     InitializeAcl(&amp;pAcl, 8, ACL_REVISION);
     DWORD status = SetNamedSecurityInfo(lpNewFileName, SE_FILE_OBJECT, 
         UNPROTECTED_DACL_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION,
         nullptr, nullptr, &amp;pAcl, nullptr);
       if (status != ERROR_SUCCESS)
         MoveFileEx(lpNewFileName, lpExistingFileName, dwFlags);
   `}`
   else `{`
     // Copy file instead...
     RpcRevertToSelf();
   `}`
 `}`
`}`
```

这个方法的功能应该是移动文件到一个新的位置，然后将继承的所有ACE（Access Control Entry）应用于新目录中的DACL（Discretionary Access Control List）。这对移动处于同一卷上的文件来说是有必要的，这样老的文件名链接被取消，新的文件被链接到新的位置。然而，新文件仍然将保留从原位置那分配的安全属性。继承的ACE只有在目录中创建新文件时才会应用，或者就像这种情况一样，调用`SetNamedSecurityInfo`之类的函数来显式应用ACE。

为了确保这种方法不会让以服务用户身份（这里为Local System）运行的用户移动任意文件，需要模拟一个RPC调用者（caller）。问题就在于此，当第一次调用`MoveFileEx`时，代码会终止模拟，恢复到自己的安全标识，然后调用`SetNamedSecurityInfo`。如果调用失败，代码则会再次调用`MoveFileEx`，尝试恢复原来的文件移动操作。这里是第一个漏洞，有可能原来文件名的所处的位置现在指向了别的地方（比如通过滥用符号链接来实现这种效果）。我们很容易就能让`SetNamedSecurityInfo`调用失败，只需要在文件的ACE中，为WRITE_DAC添加针对Local System的一个Deny ACL，这样将返回一个错误代码，导致恢复操作失败，因此我们就能拥有任意文件创建能力。这个问题已经之前已经给微软提交过（issue [1427](https://bugs.chromium.org/p/project-zero/issues/detail?id=1427)）。

这并不是我们想利用的漏洞，因为这样没有什么挑战性。相反，我们可以利用这段代码中的第二个漏洞：当以Local System身份运行时，我们可以让服务在任何文件上调用`SetNamedSecurityInfo`。为了做到这一点，我们可以在第一次`MoveFileEx`时，滥用模拟设备映射，重定向本地驱动器盘符（如`C:`），将`lpNewFileName`指向任意位置，或者也可以通过滥用硬链接（hard link）来实现。这个问题之前也提交过（issue [1428](https://bugs.chromium.org/p/project-zero/issues/detail?id=1428)），我们可以通过硬链接来利用这个漏洞，如下所示：

[![](https://p2.ssl.qhimg.com/t016acc7601c339600e.png)](https://p2.ssl.qhimg.com/t016acc7601c339600e.png)

1、创建指向`SYSTEM32`目录中我们希望覆盖的某个文件的硬链接。由于创建硬链接时，我们不需要拥有目标文件的写入权限（至少沙箱外面时适用这种情况），因此我们可以完成这个步骤。

2、创建一个新的目录，该目录具有某个组（如Everyone或者Authenticated Users）可以继承的ACE，以允许这些组用户修改新文件。其实我们根本不需要刻意去做这件事情，比如`C:`盘根目录下创建的任何目录都具有Authenticated Users能够继承的ACE。然后我们可以向RPC服务请求将硬链接文件移动到新的目录中。在模拟状态下，只要我们拥有原始位置的`FILE_DELETE_CHILD`访问权限，同时具有新位置的`FILE_ADD_FILE`权限，移动操作就能顺利完成，而这两个条件都是我们可控的条件。

3、服务现在会在移动后的硬链接文件上调用`SetNamedSecurityInfo`。`SetNamedSecurityInfo`会从新目录中提取继承的ACE，然后将ACE应用到硬链接的文件上。ACE之所以会应用到硬链接的文件上，原因在于从`SetNamedSecurityInfo`的视角来看，虽然原始的目标文件位于`SYSTEM32`目录中，但硬链接的文件位于新的目录中。

利用这一点，我们可以修改Local System具备`WRITE_DAC`访问权限的任意文件的安全属性。因此我们可以修改`SYSTEM32`目录中的某个文件，然后使用DiagHub服务来加载该文件。然而这个问题并不是特别严重。`SYSTEM32`目录下文件的所有者大部分属于`TrustedInstaller`组，因此我们无法修改（即便是Local System）。我们需要找到所有者不是TrustedInstaller且又能被我们修改的文件，同时也要保证这样不会导致系统安装被损坏。我们不用去管具体的文件扩展名，因为`AddAgent`只会检查文件是否存在，然后使用`LoadLibraryEx`来加载该文件。我们可以使用各种方法查找这类文件，比如通过SysInternals的[AccessChk](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk)工具，但为了百分百确认Storage Service的token能够修改目标文件，我决定使用我的[NtObjectManager](https://www.powershellgallery.com/packages/NtObjectManager) PowerShell模块（更确切一点是`Get-AccessibleFile`这个cmdlet，可以接受某个进程为参数来检查条件是否满足）。这个模块可以用来检查从沙箱中能够访问哪些文件，也能够用来检查特权服务能够访问哪些文件。安装该模块后，如果我们以管理员权限运行如下脚本，那么Storage Service具备`WRITE_DAC`访问权限的文件列表将存放在`$files`变量中。

```
Import-Module NtObjectManager

Start-Service -Name "StorSvc"
Set-NtTokenPrivilege SeDebugPrivilege | Out-Null
$files = Use-NtObject($p = Get-NtProcess -ServiceName "StorSvc") `{`
   Get-AccessibleFile -Win32Path C:Windowssystem32 -Recurse `
    -MaxDepth 1 -FormatWin32Path -AccessRights WriteDac -CheckMode FilesOnly
`}`
```

查看这些文件后，我决定选择`license.rtf`这个文件，该文件包含Windows系统的简要许可声明。这个文件的优势在于它对操作系统而言不是特别关键，因此覆盖这个文件不大可能出现系统安装被破坏问题。

[![](https://p1.ssl.qhimg.com/t019101c24ad4fa3d40.png)](https://p1.ssl.qhimg.com/t019101c24ad4fa3d40.png)

因此利用过程分为以下几步：

1、使用`Storage Service`漏洞修改`SYSTEM32`目录中`license.rtf`文件的安全属性。

2、将某个DLL覆盖`license.rtf`，该文件实现了`DllGetClassObject`方法。

3、使用DiagHub服务将经过我们修改的许可声明文件以DLL形式载入，这样我们就能以Local System身份获得代码执行机会，为所欲为。

如果你想查看完整的利用过程，我也上传了一份完整代码，大家可以访问[此处](https://bugs.chromium.org/p/project-zero/issues/detail?id=1428#c9)下载分析。



## 四、总结

在本文中，我介绍了针对Windows 10的一种漏洞利用方法，我们也可以在某些沙箱环境（如Edge LPAC）中利用这种方法。找到这类方法后，漏洞利用过程可以更加简单，不容易出现错误。此外，本文也介绍了如何在类似的DCOM实现方法中去寻找可能存在的一些错误。
