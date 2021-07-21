> 原文链接: https://www.anquanke.com//post/id/169072 


# Windows内核扩展机制研究


                                阅读量   
                                **188718**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者yarden-shafir，文章来源：medium.com
                                <br>原文地址：[https://medium.com/yarden-shafir/yes-more-callbacks-the-kernel-extension-mechanism-c7300119a37a](https://medium.com/yarden-shafir/yes-more-callbacks-the-kernel-extension-mechanism-c7300119a37a)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t019a831a35c180a05f.jpg)](https://p5.ssl.qhimg.com/t019a831a35c180a05f.jpg)



## 一、前言

最近我需要写一个内核模式驱动，这种工作通常会让许多人恼怒不堪，无法从容处理（转述自Douglas Adams）。

与我之前写过的代码一样，这个驱动也存在几个主要的bug，会导致一些有趣的副作用。具体而言，该驱动会阻止其他驱动正确加载，导致系统崩溃。

事实证明，许多驱动会默认自己的初始化例程（`DriverEntry`）始终能够成功执行，当意外情况发生时并不具备相应的处置办法。[j00ru](https://twitter.com/j00ru)在几年前的一篇[博客](https://j00ru.vexillium.org/2012/11/defeating-windows-driver-signature-enforcement-part-1-default-drivers/)中讨论了其中一些案例，并且其中许多案例仍可以在当前的Windows版本中找到关联线索。然而，这些bug驱动并不是我遇到的那个问题，并且j00ru对这些bug驱动的分析也比我更加全面。我关注的是其中一个驱动，进一步分析后，我开始研究“windows kernel host extensions”（Windows内核宿主扩展）机制。



## 二、初步分析

我们的目标是`Bam.sys`（Background Activity Moderator），这是Windows 10 1709（RS3）版新引入的一个驱动。当该驱动的`DriverEntry`中途失败时，系统会出现崩溃，相关调用栈情况如下所示：

[![](https://p2.ssl.qhimg.com/t01f2cb35fd31d00f64.png)](https://p2.ssl.qhimg.com/t01f2cb35fd31d00f64.png)

从崩溃转储信息中，我们可知`Bam.sys`注册了一个进程创建回调函数，并且在卸载前忘记取消注册该回调。因此，当进程被创建/终止时，系统会尝试调用该回调函数，结果就碰到无效指针，发生崩溃。

[![](https://p2.ssl.qhimg.com/t01a73f036b842ea66b.png)](https://p2.ssl.qhimg.com/t01a73f036b842ea66b.png)

这里有趣的并不是系统崩溃这件事，而是`Bam.sys`注册该回调的过程。通常情况下，驱动会通过`nt!PsSetCreateProcessNotifyRoutine(Ex)`来注册进程创建回调函数，将回调函数加入`nt!PspCreateProcessNotifyRoutine`数组中。然后，当进程被创建或者终止时，`nt!PspCallProcessNotifyRoutines`会遍历该数组，调用已注册的所有回调。然而，如果我们在WindDbg中运行`!wdbgark.wa_systemcb /type process`命令（参考[wdbgark](https://github.com/swwwolf/wdbgark)），会看到数组中并不存在`Bam.sys`所使用的回调。

[![](https://p3.ssl.qhimg.com/t01df7ae5c62efec75e.png)](https://p3.ssl.qhimg.com/t01df7ae5c62efec75e.png)

相反，`Bam.sys`使用了另一种机制来注册回调函数。

[![](https://p0.ssl.qhimg.com/t01612c99b66ba9c8bd.png)](https://p0.ssl.qhimg.com/t01612c99b66ba9c8bd.png)

如果我们去分析`nt!PspCallProcessNotifyRoutines`，就会看到其中显式引用了名为`nt!PspBamExtensionHost`的一些变量（`Dam.sys`驱动中也存在另一个类似变量）。通过这种“extension host”机制，`nt!PspCallProcessNotifyRoutines`就可以得到一张“extension table”（扩展表），然后调用extension table中的第一个函数，也就是`bam!BampCreateProcessCallback`。



## 三、扩展机制分析

如果我们在IDA中打开`Bam.sys`，很容易就能找到`bam!BampCreateProcessCallback`，进一步搜索相关的交叉引用（xref）。幸运的是，这里只有一处交叉引用，位于`bam!BampRegisterKernelExtension`中：

[![](https://p4.ssl.qhimg.com/t01367c82cc90d2fe60.png)](https://p4.ssl.qhimg.com/t01367c82cc90d2fe60.png)

正如我们猜想的那样，驱动并没有通过正常的回调注册机制来注册`Bam!BampCreateProcessCallback`，实际上该函数存放在名为`Bam!BampKernelCalloutTable`的一张函数表中，该表随后会与其他一些参数传递给未公开的`nt!ExRegisterExtension`函数（稍后我们再讨论这些参数）。

我尝试搜索相关文档或者线索，想知道这个函数具体负责的工作，或者澄清这究竟是什么扩展，但找到的线索寥寥无几。我找到最有用的一个资源就是公开泄露的[ntosifs.h](https://github.com/room/winsdk10/blob/d1acc505c51b11a6ceafb0f93c9dc584b8b4a9d3/Include/10.0.10240.0/um/minwin/ntosifs.h)头文件，头文件中包含`nt!ExRegisterExtension`的原型以及`_EX_EXTENSION_REGISTRATION_1`结构的布局信息。

`ntosifs.h`中关于`nt!ExRegisterExtension`原型以及`_EX_EXTENSION_REGISTRATION_1`结构的内容如下：

```
NTKERNELAPI NTSTATUS ExRegisterExtension (
    _Outptr_ PEX_EXTENSION *Extension,
    _In_ ULONG RegistrationVersion,
    _In_ PVOID RegistrationInfo
);

typedef struct _EX_EXTENSION_REGISTRATION_1 `{`
    USHORT ExtensionId;
    USHORT ExtensionVersion;
    USHORT FunctionCount;
    VOID *FunctionTable;
    PVOID *HostInterface;
    PVOID DriverObject;
`}` EX_EXTENSION_REGISTRATION_1, *PEX_EXTENSION_REGISTRATION_1;
```

经过一番逆向分析后，我发现`PVOID RegistrationInfo`这个输入参数实际上为`PEX_EXTENSION_REGISTRATION_1`类型。

`nt!ExRegisterExtension`的伪代码请参考附录B，这里给出该函数的主要工作流程，如下所示：

1、`nt!ExRegisterExtension`提取`RegistrationInfo`结构中`ExtensionId`和`ExtensionVersion`成员的值，然后通过`nt!ExpFindHost`函数（参考附录B）使用这些值来查找`nt!ExpHostList`中与之匹配的host；

2、然后，该函数验证`RegistrationInfo-&gt;FunctionCount`所提供的函数数量是否与host结构中设置的预期数量值相匹配。函数还会确保host的`FunctionTable`字段尚未被初始化。从这点来看，该检查机制意味着一个内核扩展无法多次注册；

3、如果一切正常，那么host的`FunctionTable`就会指向`RegistrationInfo`中的`FunctionTable`；

4、此外，`RegistrationInfo-&gt;HostInterface`会指向host结构中的一些数据。这一点比较有趣，后面我们会回头讨论这些数据；

5、最终，经过完整初始化的host会通过输出参数返回给调用方。

可以看到`nt!ExRegisterExtension`会搜索与`RegistrationInfo`匹配的host。现在的问题在于，这些host来源于何处？

在初始化阶段，NTOS会多次调用`nt!ExRegisterHost`。在每次调用时，NTOS都会传递一个结构体，用来标识预定的驱动列表（完整列表请参考附录A）中的某个驱动。比如，用来初始化`Bam.sys` host的调用代码如下：

[![](https://p2.ssl.qhimg.com/t01e27923024cfa2409.png)](https://p2.ssl.qhimg.com/t01e27923024cfa2409.png)

`nt!ExRegisterHost`会分配类型为`_HOST_LIST_ENTRY`（我起的一个非官方名称）的一个结构体，使用调用方提供的数据来初始化该结构体，然后将其附加到`nt!ExpHostList`的末尾。`_HOST_LIST_ENTRY`结构没有公开文档，其布局如下：

```
struct _HOST_LIST_ENTRY
`{`
    _LIST_ENTRY List;
    DWORD RefCount;
    USHORT ExtensionId;
    USHORT ExtensionVersion;
    USHORT FunctionCount; // number of callbacks that the extension 
                          // contains
    POOL_TYPE PoolType;   // where this host is allocated
    PVOID HostInterface; // table of unexported nt functions, 
                         // to be used by the driver to which 
                         // this extension belongs
    PVOID FunctionAddress; // optional, rarely used. 
                           // This callback is called before 
                           // and after an extension for this 
                           // host is registered / unregistered
    PVOID ArgForFunction; // will be sent to the function saved here
    _EX_RUNDOWN_REF RundownRef;
    _EX_PUSH_LOCK Lock;
    PVOID FunctionTable; // a table of the callbacks that the 
                         // driver “registers”
    DWORD Flags;         // Only uses one bit. 
                         // Not sure about its meaning.
`}` HOST_LIST_ENTRY, *PHOST_LIST_ENTRY;
```

当某个预定的驱动加载时，会使用`nt!ExRegisterExtension`注册一个扩展，并会提供一个`RegistrationInfo`结构，结构中包含一个函数表（如`Bam.sys`的工作流程一样），该函数表会存放于对应host的`FunctionTable`成员中。在某些情况下，NTOS会调用这些函数，因而这些函数的角色也类似于某种回调函数。

前文提到过，`nt!ExRegisterExtension`会设置`RegistrationInfo-&gt;HostInterface`（其中包含调用驱动的一个全局变量），将其指向host结构中发现的某些数据。现在我们回头来分析这一点。

注册扩展的每个驱动都对应由NTOS初始化的一个host。该host中包括许多信息，其中包含一个`HostInterface`指针，该指针指向包含**未导出**的NTOS函数的一张预定表。不同驱动会收到不同的`HostInterface`，而有些驱动得不到该信息。

比如，`Bam.sys`收到的`HostInterface`如下：

[![](https://p1.ssl.qhimg.com/t0117533f32e553917d.png)](https://p1.ssl.qhimg.com/t0117533f32e553917d.png)

因此，“内核扩展”机制实际上是一个双向通信端口：驱动提供一个“回调”列表，以便在不同场合下调用，然后会收到在驱动内部可以使用的一组函数。

还是回到`Bam.sys`这个例子，该驱动提供的回调函数如下：

```
BampCreateProcessCallback
BampSetThrottleStateCallback
BampGetThrottleStateCallback
BampSetUserSettings
BampGetUserSettingsHandle
```

与`Bam.sys`对应的host事先“知道”会收到包含5个函数的一张表，由于函数通过索引来调用，因此这些函数必须按照上面的顺序排列。在这个例子中，系统会调用`nt!PspBamExtensionHost-&gt;FunctionTable[4]`这个函数：

[![](https://p4.ssl.qhimg.com/t0161e1b15a43d73ac5.png)](https://p4.ssl.qhimg.com/t0161e1b15a43d73ac5.png)



## 四、总结

总而言之，Windows中存在一种机制，可以用来“扩展”NTOS，具体过程是先注册某些回调函数，然后接收驱动可以使用的未导出函数。

我并不清楚这个知识点是否能发挥实际作用，但觉得这方面内容比较有趣，值得与大家分享。关于该机制如果大家有其他有用或者有趣的想法，欢迎随时与我分享。



## 五、附录

### <a class="reference-link" name="%E9%99%84%E5%BD%95A%EF%BC%9A%E7%94%B1NTOS%E5%88%9D%E5%A7%8B%E5%8C%96%E7%9A%84ExtensionHost"></a>附录A：由NTOS初始化的ExtensionHost

[![](https://p2.ssl.qhimg.com/t011e5b5a548dc9d0b1.png)](https://p2.ssl.qhimg.com/t011e5b5a548dc9d0b1.png)

### <a class="reference-link" name="%E9%99%84%E5%BD%95B%EF%BC%9A%E9%83%A8%E5%88%86%E5%87%BD%E6%95%B0%E4%BC%AA%E4%BB%A3%E7%A0%81"></a>附录B：部分函数伪代码

`ExRegisterExtension.c`：

```
NTSTATUS ExRegisterExtension(_Outptr_ PEX_EXTENSION *Extension, _In_ ULONG RegistrationVersion, _In_ PREGISTRATION_INFO RegistrationInfo)
`{`
    // Validate that version is ok and that FunctionTable is not sent without FunctionCount or vise-versa.
    if ( (RegistrationVersion &amp; 0xFFFF0000 != 0x10000) || (RegistrationInfo-&gt;FunctionTable == nullptr &amp;&amp; RegistrationInfo-&gt;FunctionCount != 0) ) 
    `{` 
        return STATUS_INVALID_PARAMETER; 
    `}`

    // Skipping over some lock-related stuff,

    // Find the host with the matching version and id.
    PHOST_LIST_ENTRY pHostListEntry;
    pHostListEntry = ExpFindHost(RegistrationInfo-&gt;ExtensionId, RegistrationInfo-&gt;ExtensionVersion);

    // More lock-related stuff.    

    if (!pHostListEntry)
    `{`
        return STATUS_NOT_FOUND;
    `}`

    // Verify that the FunctionCount in the host doesn't exceed the FunctionCount supplied by the caller.
    if (RegistrationInfo-&gt;FunctionCount &lt; pHostListEntry-&gt;FunctionCount)
    `{`
        ExpDereferenceHost(pHostListEntry);
        return STATUS_INVALID_PARAMETER;
    `}`

    // Check that the number of functions in FunctionTable matches the amount in FunctionCount.
    PVOID FunctionTable = RegistrationInfo-&gt;FunctionTable;
    for (int i = 0; i &lt; RegistrationInfo-&gt;FunctionCount; i++)
    `{`    
        if ( RegistrationInfo-&gt;FunctionTable[i] == nullptr ) 
        `{` 
            ExpDereferenceHost(pHostListEntry);
            return STATUS_ACCESS_DENIED; 
        `}`
    `}`

    // skipping over some more lock-related stuff

    // Check if there is already an extension registered for this host.
    if (pHostListEntry-&gt;FunctionTable != nullptr || FlagOn(pHostListEntry-&gt;Flags, 1) )
    `{`
        // There is something related to locks here
        ExpDereferenceHost(pHostListEntry);
        return STATUS_OBJECT_NAME_COLLISION;
    `}`

    // If there is a callback function for this host, call it before registering the extension, with 0 as the first parameter.
    if (pHostListEntry-&gt;FunctionAddress) 
    `{` 
        pHostListEntry-&gt;FunctionAddress(0, pHostListEntry-&gt;ArgForFunction); 
    `}`

    // Set the FunctionTable in the host to the table supplied by the caller, or to MmBadPointer if a table wasn't supplied.
    if (RegistrationInfo-&gt;FunctionTable == nullptr)
    `{`
        pHostListEntry-&gt;FunctionTable = nt!MmBadPointer;
    `}`
    else
    `{`
        pHostListEntry-&gt;FunctionTable = RegistrationInfo-&gt;FunctionTable;
    `}`

    pHostListEntry-&gt;RundownRef = 0;

    // If there is a callback function for this host, call it after registering the extension, with 1 as the first parameter.
    if (pHostListEntry-&gt;FunctionAddress)
    `{`
        pHostListEntry-&gt;FunctionAddress(1, pHostListEntry-&gt;ArgForFunction);
    `}`

    // Here there is some more lock-related stuff

    // Set the HostTable of the calling driver to the table of functions listed in the host.
    if (RegistrationInfo-&gt;HostTable != nullptr)
    `{`
        *(PVOID)RegistrationInfo-&gt;HostTable = pHostListEntry-&gt;hostInterface;
    `}`

    // Return the initialized host to the caller in the output Extension parameter.
    *Extension = pHostListEntry;
    return STATUS_SUCCESS;
`}`
```

`ExRegisterHost.c`：

```
NTSTATUS ExRegisterHost(_Out_ PHOST_LIST_ENTRY ExtensionHost, _In_ ULONG Unused, _In_ PHOST_INFORMATION HostInformation)
`{`
    NTSTATUS Status = STATUS_SUCCESS;

    // Allocate memory for a new HOST_LIST_ENTRY
    PHOST_LIST_ENTRY p = ExAllocatePoolWithTag(HostInformation-&gt;PoolType, 0x60, 'HExE');
    if (p == nullptr)
    `{`
        return STATUS_INSUFFICIENT_RESOURCES;
    `}`

    //
    // Initialize a new HOST_LIST_ENTRY 
    //
    p-&gt;Flags &amp;= 0xFE;
    p-&gt;RefCount = 1;
    p-&gt;FunctionTable = 0;
    p-&gt;ExtensionId = HostInformation-&gt;ExtensionId;
    p-&gt;ExtensionVersion = HostInformation-&gt;ExtensionVersion;
    p-&gt;hostInterface = HostInformation-&gt;hostInterface;
    p-&gt;FunctionAddress = HostInformation-&gt;FunctionAddress;
    p-&gt;ArgForFunction = HostInformation-&gt;ArgForFunction;            
    p-&gt;Lock = 0;             
    p-&gt;RundownRef = 0;        

    // Search for an existing listEntry with the same version and id.
    PHOST_LIST_ENTRY listEntry = ExpFindHost(HostInformation-&gt;ExtensionId, HostInformation-&gt;ExtensionVersion);
    if (listEntry)
    `{`
        Status = STATUS_OBJECT_NAME_COLLISION;
        ExpDereferenceHost(p);
        ExpDereferenceHost(listEntry);
    `}`
    else
    `{`
        // Insert the new HOST_LIST_ENTRY to the end of ExpHostList.
        if ( *lastHostListEntry != &amp;firstHostListEntry )
        `{`
                  __fastfail();
        `}`

        firstHostListEntry-&gt;Prev = &amp;p;
        p-&gt;Next = firstHostListEntry;
        lastHostListEntry = p;

        ExtensionHost = p;
    `}`

    return Status;
`}`
```

`ExpFindHost.c`：

```
PHOST_LIST_ENTRY ExpFindHost(USHORT ExtensionId, USHORT ExtensionVersion)
`{`
    PHOST_LIST_ENTRY entry;
    for (entry == ExpHostList; ; entry = entry-&gt;Next)
    `{`
        if (entry == &amp;ExpHostList) 
        `{` 
            return 0; 
        `}`

        if ( *(entry-&gt;ExtensionId) == ExtensionId &amp;&amp; *(entry-&gt;ExtensionVersion) == ExtensionVersion ) 
        `{` 
            break; 
        `}`
    `}`
    InterlockedIncrement(entry-&gt;RefCount);
    return entry;
`}`
```

`ExpDereferenceHost.c`：

```
void ExpDereferenceHost(PHOST_LIST_ENTRY Host)
`{`
      if ( InterlockedExchangeAdd(Host.RefCount, 0xFFFFFFFF) == 1 )
    `{`
            ExFreePoolWithTag(Host, 0);
    `}`
`}`
```

### <a class="reference-link" name="%E9%99%84%E5%BD%95C%EF%BC%9A%E7%BB%93%E6%9E%84%E5%AE%9A%E4%B9%89"></a>附录C：结构定义

```
struct _HOST_INFORMATION
`{`
    USHORT ExtensionId;
    USHORT ExtensionVersion;
    DWORD FunctionCount;
    POOL_TYPE PoolType;
    PVOID HostInterface;
    PVOID FunctionAddress;
    PVOID ArgForFunction;
    PVOID unk;
`}` HOST_INFORMATION, *PHOST_INFORMATION;

struct _HOST_LIST_ENTRY
`{`
    _LIST_ENTRY List;
    DWORD RefCount;
    USHORT ExtensionId;
    USHORT ExtensionVersion;
    USHORT FunctionCount; // number of callbacks that the 
                          // extension contains
    POOL_TYPE PoolType;   // where this host is allocated
    PVOID HostInterface;  // table of unexported nt functions, 
                          // to be used by the driver to which 
                          // this extension belongs
    PVOID FunctionAddress; // optional, rarely used. 
                           // This callback is called before and    
                           // after an extension for this host 
                           // is registered / unregistered
    PVOID ArgForFunction; // will be sent to the function saved here
    _EX_RUNDOWN_REF RundownRef;
    _EX_PUSH_LOCK Lock;
    PVOID FunctionTable;    // a table of the callbacks that 
                            // the driver “registers”
DWORD Flags;                // Only uses one flag. 
                            // Not sure about its meaning.
`}` HOST_LIST_ENTRY, *PHOST_LIST_ENTRY;;

struct _EX_EXTENSION_REGISTRATION_1
`{`
    USHORT ExtensionId;
    USHORT ExtensionVersion;
    USHORT FunctionCount;
    PVOID FunctionTable;
    PVOID *HostTable;
    PVOID DriverObject;
`}`EX_EXTENSION_REGISTRATION_1, *PEX_EXTENSION_REGISTRATION_1;
```
