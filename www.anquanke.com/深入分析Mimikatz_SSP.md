> 原文链接: https://www.anquanke.com//post/id/180001 


# 深入分析Mimikatz：SSP


                                阅读量   
                                **299086**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者xpnsec，文章来源：blog.xpnsec.com
                                <br>原文地址：[https://blog.xpnsec.com/exploring-mimikatz-part-2/](https://blog.xpnsec.com/exploring-mimikatz-part-2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01abe248a20b28bf57.jpg)](https://p5.ssl.qhimg.com/t01abe248a20b28bf57.jpg)



## 0x00 前言

在前一篇[文章](https://blog.xpnsec.com/exploring-mimikatz-part-1/)中，我们开始深入分析Mimikatz。我们的想法很简单，就是想澄清Mimikatz内部的工作原理，以便开发自定义和有针对性的payload。微软引入了一些安全控制机制（如Credential Guard），避免攻击者转储凭据信息。在本文中，我们将回顾一下绕过这种机制的巧妙方法，然后提取我们所需的凭据。这里我们想要分析的是Mimikatz所支持的SSP功能。

SSP（Security Support Provider）是一个DLL，允许开发者提供一些回调函数，以便在特定认证和授权事件期间调用。在前一篇文章中，我们可以了解到WDigest正是使用这个接口来缓存凭据。

Mimikatz为我们提供了利用SSP的其他一些不同技术。首先是“Mimilib”，这是具备各种功能的一个DLL，其中一个功能就是实现了SSP接口。其次是“memssp”，这是完成相同任务的另一种有趣方式，但这种方法需要patch内存，而不是单单加载DLL那么简单。

首先试一下以传统方式来加载SSP：Mimilib。

> 备注：与前一篇文章相同，本文大量用到了Mimikatz源代码，Mimikatz开发人员在这上面花了大量精力。感谢Mimikatz、[Benjamin Delpy](https://twitter.com/gentilkiwi)以及[Vincent Le Toux](https://twitter.com/mysmartlogon)的杰出工作。



## 0x01 Mimilib

Mimilib就像变色龙一样，支持利用`ServerLevelPluginDll`来通过RPC进行横向移动、DHCP Server Callout，甚至也可以作为WinDBG扩展。在本文中，我们主要关注的是这个库如何充当SSP角色，使攻击者能在受害者输入凭据时提取到目标信息。

系统在调用SSP时，会通过SSP接口传递明文凭据，这意味着我们可以提取到明文凭据，这也是Mimilib的理论基础。Mimilib SSP功能的入口点位于[kssp.c](https://github.com/gentilkiwi/mimikatz/blob/master/mimilib/kssp.c)中的`kssp_SpLsaModeInitialize`函数。DLL通过`mimilib.def`定义文件，将该函数导出为`SpLsaModeInitialize`，`lsass`会使用该函数来初始化包含多个回调的一个结构体。

Mimilib注册的回调函数包括：
<li>
`SpInitialize`：用来初始化SSP，提供一个函数指针列表。</li>
<li>
`SpShutDown`：卸载SSP时就会被调用，以便释放资源。</li>
<li>
`SpGetInfoFn`：提供SSP相关信息，包括版本、名称以及描述。</li>
<li>
`SpAcceptCredentials`：接收LSA传递的明文凭据，以便SSP缓存。</li>
如果大家看过上一篇文章，就知道WDigest会使用`SpAcceptCredentials`来缓存凭据，这也是多年来我们一直能成功提取凭据的切入点。

了解这些背景后，Mimilib所需要做的就是在`SpAcceptCredentials`被调用后保存传入的明文凭据，这正是`kssp_SpAcceptCredentials`的代码逻辑，如下所示：

```
NTSTATUS NTAPI kssp_SpAcceptCredentials(SECURITY_LOGON_TYPE LogonType, PUNICODE_STRING AccountName, PSECPKG_PRIMARY_CRED PrimaryCredentials, PSECPKG_SUPPLEMENTAL_CRED SupplementalCredentials)
`{`
    FILE *kssp_logfile;
#pragma warning(push)
#pragma warning(disable:4996)
    if(kssp_logfile = _wfopen(L"kiwissp.log", L"a"))
#pragma warning(pop)
    `{`    
        klog(kssp_logfile, L"[%08x:%08x] [%08x] %wZ\%wZ (%wZ)t", PrimaryCredentials-&gt;LogonId.HighPart, PrimaryCredentials-&gt;LogonId.LowPart, LogonType, &amp;PrimaryCredentials-&gt;DomainName, &amp;PrimaryCredentials-&gt;DownlevelName, AccountName);
        klog_password(kssp_logfile, &amp;PrimaryCredentials-&gt;Password);
        klog(kssp_logfile, L"n");
        fclose(kssp_logfile);
    `}`
    return STATUS_SUCCESS;
`}`
```

现在我不相信`mimikatz.exe`能够直接加载Mimilib，但根据微软的官方文档，我们可以添加[注册表项](https://docs.microsoft.com/en-us/windows/desktop/secauthn/restrictions-around-registering-and-installing-a-security-package)、重启系统就能添加SSP。

然而经过一番搜索后，我找到了一则推文：

[![](https://p2.ssl.qhimg.com/t01f00e6db21e41035a.png)](https://p2.ssl.qhimg.com/t01f00e6db21e41035a.png)

这里直接提到了[AddSecurityPackage](https://docs.microsoft.com/en-us/windows/desktop/api/sspi/nf-sspi-addsecuritypackagea)这个API，[Install-SSP.ps1](https://github.com/PowerShellMafia/PowerSploit/blob/master/Persistence/Persistence.psm1)脚本中利用这个API来加载SSP。这意味着实际上我们可以在不重启的情况下添加Mimilib。当添加成功后，我们发现每次进行身份认证时，凭据信息都会被写入[kiwissp.log](https://github.com/gentilkiwi/mimikatz/blob/master/mimilib/kssp.c#L43)文件中。

[![](https://p0.ssl.qhimg.com/t017ae2a93d97ecc762.png)](https://p0.ssl.qhimg.com/t017ae2a93d97ecc762.png)

现在在目标环境中使用SSP有一个缺点，那就是我们必须在`lsass`中注册SSP，这样我们就不得不留下一些踪迹，比如创建与SSP有关的注册表、或者在`lsass`进程中留下异常的DLL，防御方可以有针对性地跟踪我们的恶意行为。此外，SSP还会对外公开名称以及注释，可以使用`EnumerateSecurityPackages`来枚举这些信息，如下所示：

```
#define SECURITY_WIN32

#include &lt;stdio.h&gt;
#include &lt;Windows.h&gt;
#include &lt;Security.h&gt;

int main(int argc, char **argv) `{`
    ULONG packageCount = 0;
    PSecPkgInfoA packages;

    if (EnumerateSecurityPackagesA(&amp;packageCount, &amp;packages) == SEC_E_OK) `{`
        for (int i = 0; i &lt; packageCount; i++) `{`
            printf("Name: %snComment: %snn", packages[i].Name, packages[i].Comment);
        `}`
    `}`
`}`
```

如下图所示，输出结果中包含已加载每个SSP的相关信息，其中大家可能会注意到有Mimilib的身影：

[![](https://p2.ssl.qhimg.com/t01eed6fa88178370a8.png)](https://p2.ssl.qhimg.com/t01eed6fa88178370a8.png)

那么我们是否可以采取一些隐蔽措施呢？最明显的应该就是修改Mimilib中`SpGetInfo`回调函数所返回的描述信息，这些信息被硬编码在代码中，如下所示：

```
NTSTATUS NTAPI kssp_SpGetInfo(PSecPkgInfoW PackageInfo)
`{`
    PackageInfo-&gt;fCapabilities = SECPKG_FLAG_ACCEPT_WIN32_NAME | SECPKG_FLAG_CONNECTION;
    PackageInfo-&gt;wVersion   = 1;
    PackageInfo-&gt;wRPCID     = SECPKG_ID_NONE;
    PackageInfo-&gt;cbMaxToken = 0;
    PackageInfo-&gt;Name       = L"KiwiSSP";
    PackageInfo-&gt;Comment    = L"Kiwi Security Support Provider";
    return STATUS_SUCCESS;
`}`
```

这里我们可以修改`Name`以及`Comment`字段，结果如下所示：

[![](https://p2.ssl.qhimg.com/t018bbc9577f343621b.png)](https://p2.ssl.qhimg.com/t018bbc9577f343621b.png)

好吧，显然这还远远不够（即使我们修改了名称以及注释字段）。要注意一点，在没有充分剥离并重新编译之前，Mimilib中还包含大量功能，而不单单是充当SSP角色那么简单。

那么我们应该如何绕过这一点呢？这里要感谢Mimikatz还支持`misc::memssp`，这是我们可以使用的另一个较好的候选方案。



## 0x02 MemSSP

MemSSP回到了处理`lsass`内存的老路上，这一次MemSSP会识别并patch一些函数，重定向执行逻辑。

来看一下源头函数：[kuhl_m_misc_memssp](https://github.com/gentilkiwi/mimikatz/blob/72b83acb297f50758b0ce1de33f722e70f476250/mimikatz/modules/kuhl_m_misc.c#L508)。这里我们可以看到代码会打开`lsass`进程，开始搜索`msv1_0.dll`，这个DLL是支持交互式身份认证的一个认证程序包：

```
NTSTATUS kuhl_m_misc_memssp(int argc, wchar_t * argv[])
`{`
...
if(kull_m_process_getProcessIdForName(L"lsass.exe", &amp;processId))
  `{`
    if(hProcess = OpenProcess(PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_QUERY_INFORMATION, FALSE, processId))
    `{`
    if(kull_m_memory_open(KULL_M_MEMORY_TYPE_PROCESS, hProcess, &amp;aLsass.hMemory))
      `{`            if(kull_m_process_getVeryBasicModuleInformationsForName(aLsass.hMemory, L"msv1_0.dll", &amp;iMSV))
        `{`
...
```

接下来是在内存中搜索匹配模式，这类似于我们在WDigest中看到的处理逻辑：

```
...
sSearch.kull_m_memoryRange.kull_m_memoryAdress = iMSV.DllBase;
sSearch.kull_m_memoryRange.size = iMSV.SizeOfImage;
if(pGeneric = kull_m_patch_getGenericFromBuild(MSV1_0AcceptReferences, ARRAYSIZE(MSV1_0AcceptReferences), MIMIKATZ_NT_BUILD_NUMBER))
`{`
  aLocal.address = pGeneric-&gt;Search.Pattern;
  if(kull_m_memory_search(&amp;aLocal, pGeneric-&gt;Search.Length, &amp;sSearch, TRUE))
  `{`
...
```

如果我们暂停代码审计，投入Ghidra怀抱，就可以搜索代码正在使用的匹配模式，然后找到如下位置：

[![](https://p3.ssl.qhimg.com/t0131bc6c5fdb72ea1f.png)](https://p3.ssl.qhimg.com/t0131bc6c5fdb72ea1f.png)

这里我们来看看代码实际上在执行哪些操作。memssp正被用来hook `msv1_0.dll`的`SpAcceptCredentials`函数，以便恢复凭据信息。让我们使用调试器看一下添加后的hook长啥样子。

首先我们确认`SpAcceptCredentials`中包含一个hook：

[![](https://p0.ssl.qhimg.com/t0119a3406a5fcac133.png)](https://p0.ssl.qhimg.com/t0119a3406a5fcac133.png)

接下来当我们逐步执行时，会进入一段代码逻辑，其中会在栈上创建一个文件名，将其传递给`fopen`，以便创建一个log文件：

[![](https://p3.ssl.qhimg.com/t012504d874ed981d80.png)](https://p3.ssl.qhimg.com/t012504d874ed981d80.png)

[![](https://p0.ssl.qhimg.com/t01b1c64bfbafaa11af.png)](https://p0.ssl.qhimg.com/t01b1c64bfbafaa11af.png)

一旦打开该文件，传递给`SpAcceptCredentials`的凭据就会被写入该文件中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0130c273877bbc2a04.png)

最后，执行流程会被重定向回`msv1_0.dll`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017e3d5cb85fc46287.png)

如果大家想查看负责这个hook的代码，可以在`kuhl_m_misc.c`源文件的[misc_msv1_0_SpAcceptCredentials](https://github.com/gentilkiwi/mimikatz/blob/72b83acb297f50758b0ce1de33f722e70f476250/mimikatz/modules/kuhl_m_misc.c#L462)函数中找到相应代码。

那么我们使用这种技术的风险在哪呢？从前面分析中，我们可以看到hook会通过`kull_m_memory_copy`被拷贝到`lsass`中，该函数实际上使用的是`WriteProcessMemory`。根据目标具体环境，调用`WriteProcessMemory`插入另一个进程可能会被检测到，或者被标记为可疑行为，等等。特别当目标进程是`lsass`时，这种行为更加可疑。

现在对我们来说，深入分析Mimikatz使用的具体技术可以帮我们修改与`lsass`的交互行为，使蓝队更难发现我们的踪迹。接下来让我们看一下如何增加整个过程的复杂度。



## 0x03 不使用WriteProcessMemory重构memssp

回顾前面分析的技术后，我们能找到各自的优点以及缺点。

第一种方法（Mimilib）需要注册SSP，而这种行为可以通过`EnumerateSecurityPackages`枚举已注册的SSP列表来定位。此外，如果Mimilib库没有经过修改，那么DLL中还包含大量其他功能。另外一方面，当使用`AddSecurityProvider`来加载时，注册表键值会被修改，以便系统重启时还能保持SSP驻留。也就是说，这种方法最大的优点在于不需要调用有潜在风险的`WriteProcessMemory` API就能完成任务。

第二种方法（memssp）需要依赖容易被监控的API（如`WriteProcessMemory`），利用这些API来hook到`lsass`中。这种方法的最大优点就是不会存在于已注册的SSP列表中，也不会存在于已加载的DLL中。

那么我们可以做些什么呢？我们可以将这两种方法结合起来，使用`AddSecurityProvider`来加载我们的代码，同时避免自己出现在已注册的SSP列表中。我们需要找到方法避免直接调用`AddSecurityProvider` API，如果成功的话，这样就能绕过各种烦人的AV或者EDR（这些解决方法可能会hook这个函数）。

让我们先来看看`AddSecurityPackage`注册SSP的具体过程，这意味我们需要做一些逆向分析。我们先观察导出该API的DLL：`Secur32.dll`。

在Ghidra中打开这个DLL，就可以看到这实际上是个封装库，会调用`sspcli.dll`：

[![](https://p1.ssl.qhimg.com/t01571d602070959216.png)](https://p1.ssl.qhimg.com/t01571d602070959216.png)

反汇编`sspcli.dll`中的`AddSecurityPackage`（特别是该函数所使用的外部API调用），我们可以找到`NdrClientCall3`，这意味着该函数正在使用RPC。这一点很正常，因为这个调用需要向`lsass`发送信号，通知`lsass`应当加载一个新的SSP：

[![](https://p5.ssl.qhimg.com/t01d79e429a9caadf5d.png)](https://p5.ssl.qhimg.com/t01d79e429a9caadf5d.png)

跟踪`NdrClientCall3`，我们可以找到传入的如下参数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010618d9b34cf9946c.png)

其中`nProcNum`参数值为`3`，如果我们深入分析`sspirpc_ProxyInfo`结构，可以看到RPC接口的UUID值为`4f32adc8-6052-4a04-8701-293ccf2096f0`：

[![](https://p3.ssl.qhimg.com/t01358bed86b30e0502.png)](https://p3.ssl.qhimg.com/t01358bed86b30e0502.png)

现在我们已经掌握足够多的信息，可以通过RpcView来观察通过`sspisrv.dll`公开的`SspirCallRpc` RPC调用：

[![](https://p0.ssl.qhimg.com/t016466f89c4b84b2bf.png)](https://p0.ssl.qhimg.com/t016466f89c4b84b2bf.png)

为了使用这个调用，我们需要知道传入的参数。我们可以通过RpcView来获取这些信息，如下所示：

```
long Proc3_SspirCallRpc(
  [in][context_handle] void* arg_0,
  [in]long arg_1,
  [in][size_is(arg_1)]/*[range(0,0)]*/ char* arg_2,
  [out]long* arg_3,
  [out][ref][size_is(, *arg_3)]/*[range(0,0)]*/ char** arg_4,
  [out]struct Struct_144_t* arg_5);
```

然而在实现这个调用之前，我们需要知道`arg_2`参数传入的具体值（`arg_1`为`arg_2`的大小，`arg_3`、`arg_4`以及`arg_5`都标记为`out`）。我发现完成该任务最简单的方法就是启动调试器，然后在`AddSecurityPackage`调用`NdrClientCall3`之前插入断点：

[![](https://p3.ssl.qhimg.com/t01bfe9c1f203415e5a.png)](https://p3.ssl.qhimg.com/t01bfe9c1f203415e5a.png)

暂停执行后，我们可以dump出传入的每个参数的值。我们可以使用`dq rsp+0x20 L1`来获取`arg_1`参数中传递的缓冲区大小值。

[![](https://p2.ssl.qhimg.com/t01d172e88cf9c216bc.png)](https://p2.ssl.qhimg.com/t01d172e88cf9c216bc.png)

因此，我们知道在这种情况下，传入的缓冲区大小为`0xEC`字节。现在我们可以使用如下命令来dump出`arg_2`：

[![](https://p4.ssl.qhimg.com/t0104d2468c070f428e.png)](https://p4.ssl.qhimg.com/t0104d2468c070f428e.png)

经过一番挖掘后，我成功将大多数值关联起来。让我们以`QWORD`来重新格式化输出，这样能较为清晰地梳理我们正在处理的数据：

[![](https://p3.ssl.qhimg.com/t01bc9ae0f2d5a7cb02.png)](https://p3.ssl.qhimg.com/t01bc9ae0f2d5a7cb02.png)

现在我们已经映射出传入的大部分数据，我们可以尝试在不直接使用`AddSecurityPackage` API的情况下发起RPC调用。大家可以访问[Gist](https://gist.github.com/xpn/c7f6d15bf15750eae3ec349e7ec2380e)下载我构造的代码。

在不直接调用`AddSecurityPackage`下我们已经能够加载包，接下来我们看看能否进一步使这个过程更加隐蔽。

让我们使用Ghidra载入`sspisrv.dll`，观察服务端如何处理RPC调用。反汇编`SspirCallRpc`后，我们很快就发现执行流程会通过`gLsapSspiExtension`来传递：

[![](https://p4.ssl.qhimg.com/t01656ff299cbd6e27d.png)](https://p4.ssl.qhimg.com/t01656ff299cbd6e27d.png)

这实际上使指向函数数组的一个指针，通过`lsasrv.dll`提供，会指向`LsapSspiExtensionFunctions`：

[![](https://p4.ssl.qhimg.com/t01647e91b0f0d2f61e.png)](https://p4.ssl.qhimg.com/t01647e91b0f0d2f61e.png)

我们对`SspiExCallRpc`比较感兴趣，这与我们在RPCView中观察到的非常相似。该函数会验证参数值，并将执行流程传递给`LpcHandler`：

[![](https://p2.ssl.qhimg.com/t01414672e3c624991f.png)](https://p2.ssl.qhimg.com/t01414672e3c624991f.png)

`LpcHandler`在将执行权交给`DispatchApi`之前，会进一步检查所提供的参数：

[![](https://p1.ssl.qhimg.com/t01087c2b51aa0b6280.png)](https://p1.ssl.qhimg.com/t01087c2b51aa0b6280.png)

同样，这里会使用另一个函数数组指针来调度`LpcDispatchTable`所指向的函数调用：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01945a60960caf26bd.png)

现在我们应该对这个数组比较感兴趣，因为我们可能会根据函数名，找到其中的`s_AddPackage`，并且这个函数的索引值与我们在请求中找到的`0xb` “Function ID”索引值相匹配。

沿着线索进一步走下去，我们找到了`WLsaAddPackage`，该函数首先会检查我们是否具备足够的权限来调用RPC方法，具体操作就是模拟（impersonate）客户端，然后尝试以Read/Write权限打开`HKLM\System\CurrentControlSet\Control\Lsa`注册表项：

[![](https://p5.ssl.qhimg.com/t01c9dbe3d4f586d939.png)](https://p5.ssl.qhimg.com/t01c9dbe3d4f586d939.png)

如果操作成功（请注意这是可用于权限提升的一个较新颖的后门技术），那么执行权就会继续交给`SpmpLoadDll`，后者会通过`LoadLibraryExW`将我们提供的SSP加载到`lsass`中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0161efcaa9cd4e3f82.png)

如果SSP成功加载，那么DLL就会被添加到注册表中，以实现自动加载：

[![](https://p3.ssl.qhimg.com/t018bd77f13fce88202.png)](https://p3.ssl.qhimg.com/t018bd77f13fce88202.png)

这里我们可能希望跳过这个操作，因为我们不希望使用这种方法实现本地驻留，并且如果没有必要，我们也不希望涉及到注册表操作。理想状态下，如果引起怀疑（比如防御方通过ProcessExplorer来分析时），我们还希望这个DLL不会出现在`lsass`载入列表中。因此我们可以使用RPC调用来传递我们的DLL，在SSP的`DllMain`中返回`FALSE`，强制SSP加载失败。这样就会跳过注册表修改操作，也意味着我们的DLL会从进程中卸载。

我以Mimikatz的memssp作为模板构造了一个DLL，可以通过我们的RPC调用来加载，使用Mimikatz所用的相同hook来patch `SpAddCredentials`。大家可以访问[Gist](https://gist.github.com/xpn/93f2b75bf086baf2c388b2ddd50fb5d0)下载源代码。

使用我们的`AddSecurityPackage` RPC调用来加载DLL的整个过程参考[此处视频](https://youtu.be/EtIah5mL80E)。

使用这种方法时，我们也不一定需要在本地系统中才能加载DLL，如果通过RPC调用，我们也可以使用UNC路径（但我们需要确保EDR并不会将这种操作标记为可疑行为）。

当然，我们也不一定要使用`AddSecurityPackage`来加载这个DLL。我们构造了一个独立版的DLL，可以实现memssp patch。我们可以使用前一篇文章中的SAMR RPC脚本，利用该脚本通过`LoadLibrary`来加载我们的DLL，获取使用SMB共享的登录操作信息，整个过程可以参考[此处视频](https://youtu.be/aMdkMOvdUTw)。

此外，还有很多方法能够改进这些方法的有效性。但与前一篇文章一样，我希望本文能给大家提供一个思路，让大家了解如何构造自己的SSP，以便在行动中更加得心应手。本文只提供了能够隐蔽将SSP载入`lsass`过程的一些参考方法，澄清Mimikatz实现该过程的具体原理。大家可以根据这些信息，在实际环境中定制自己的payload，以便绕过AV或者EDR，或者可以用来测试蓝队在Mimilib和memssp之外是否存在其他检测能力。
