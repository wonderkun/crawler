> 原文链接: https://www.anquanke.com//post/id/156106 


# 利用内核分配内存时的 PoolTags 标记识别主机指纹


                                阅读量   
                                **133095**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01fa841b6c896d550c.jpg)](https://p4.ssl.qhimg.com/t01fa841b6c896d550c.jpg)

通常，恶意软件会识别其执行主机的指纹，以尝试发现主机环境的更多信息, 并采取相应措施。

指纹识别的一种方式是分析专用的、特定的数据，以便确定恶意软件是否在虚拟机中运行，比如蜜罐或恶意代码分析环境，还用于检测其他软件的存在。例如，恶意软件经常会试图找出系统监控工具是否正在运行（procmon，sysmon等）以及安装了哪个AV软件。

在本文中，我们将介绍另一种可能被恶意软件滥用的主机指纹识别方法。



## 主持指纹识别的常用方法

在本节中，我们提供了一个简短列表, 包含一些众所周知的检测虚拟机环境的方法，这些方法也通常用于检测其他安全软件是否存在。请注意，以下列表并未包含所有的指纹识别方式。
- 进程枚举
- 加载的模块枚举
- 文件枚举
- 从Windows注册表中提取的数据（硬盘，BIOS等）
- 加载的驱动程序枚举
- 打开特定命名设备对象的句柄
- 系统资源枚举（CPU内核，RAM，屏幕分辨率等）


## PoolTag方式

如果你对Windows内核驱动程序开发和分析有一些经验，那么你应该熟悉 `ExAllocatePoolWithTag[1]` 函数，该函数用于在内核层分配内存块。这里的关键部分是’Tag’参数，用于为特定的内存分配提供某种标识。

如果出现问题，例如内存损坏，我们可以使用指定的Tag（最多四个字符）将损坏的内存地址与分配该内存块的内核驱动程序中的代码路径相关联。这种方法足以检测内核驱动程序的存在，进而检测到那些加载内核模块以绕过以上列表所述指纹识别方法的软件，因为以上列表中的方法依赖于驱动程序提供的信息, 而驱动提供的信息是可以篡改的。换句话说，从恶意软件作者的角度来看, 使用PoolTag检测真正关键的内容是非常理想的。

例如，安全/监控软件可能会通过在内核级别注册回调过滤器来隐藏其进程和文件。恶意代码分析人员通常会从注册表中删除恶意软件通常搜索的内容来加固虚拟机环境, 降低恶意代码检测到真实执行环境的风险。

但是，安全软件供应商和/或恶意代码分析人员可能不会做的是：修改他们自己的程序和/或系统/虚拟机环境使用的特定内核驱动程序，以不断更改其内核池分配的标记。



## 获取PoolTag信息

可以通过调用 `NtQuerySystemInformation[2]` 函数并将参数 `SysteminformationClass` 设置为 `SystemPoolTagInformation（0x16 ）[3]` 来获取此信息。

上述功能和相关的 `SysteminformationClass` 可取值在MSDN上只有部分记录，但幸运的是，我们找到了一些研究人员编写的文档。特别是，[Alex Ionescu](https://twitter.com/aionescu) 在他的 `NDK[3]` 项目中记录了许多Windows内部没有文档化的内容。

为了验证此方式的有效性，我们自己编写了获取和解析PoolTag信息的代码，但是如果你想用GUI方式来检验结果，那么 `PoolMonEx[4]` 是一个非常好的工具。

例如，以下是我们工具输出的屏幕截图。源代码在下面。

[![](https://labs.nettitude.com/wp-content/uploads/2018/08/word-image.png)](https://labs.nettitude.com/wp-content/uploads/2018/08/word-image.png)

你可以与PoolMonEx显示中的`Nbtk`标记的内存分配结果进行比较，如下所示。

[![](https://labs.nettitude.com/wp-content/uploads/2018/08/word-image-1.png)](https://labs.nettitude.com/wp-content/uploads/2018/08/word-image-1.png)



## QueryPoolTagInfo.cpp

```
#include "Defs.h"
#include &lt;iostream&gt;

using namespace std;

int main()
`{`
    NTSTATUS NtStatus = STATUS_SUCCESS;
    BYTE * InfoBuf = nullptr;
    ULONG ReturnLength = 0;

    _ZwQuerySystemInformation ZwQuerySystemInformation = (_ZwQuerySystemInformation)GetProcAddress(GetModuleHandleA("ntdll.dll"), "ZwQuerySystemInformation");

    do`{`
        NtStatus = ZwQuerySystemInformation(SystemPoolTagInformation, InfoBuf, ReturnLength, &amp;ReturnLength);

        if (NtStatus == STATUS_INFO_LENGTH_MISMATCH)
        `{`
            if (InfoBuf != nullptr)
            `{`
                delete[] InfoBuf;
                InfoBuf = nullptr;
            `}`

            InfoBuf = new (nothrow) BYTE[ReturnLength];

            if (InfoBuf != nullptr)
                memset(InfoBuf, 0, ReturnLength);
            else
                goto Exit;
        `}`

    `}` while (NtStatus != STATUS_SUCCESS);


    PSYSTEM_POOLTAG_INFORMATION pSysPoolTagInfo = (PSYSTEM_POOLTAG_INFORMATION)InfoBuf;
    PSYSTEM_POOLTAG psysPoolTag = (PSYSTEM_POOLTAG)&amp;pSysPoolTagInfo-&gt;TagInfo-&gt;Tag;

    ULONG count = pSysPoolTagInfo-&gt;Count;
    cout &lt;&lt; "Count: " &lt;&lt; count &lt;&lt; endl &lt;&lt; endl;

    for (ULONG i = 0; i &lt; count; i++)
    `{`
        cout &lt;&lt; "PoolTag: ";

        for (int k = 0; k &lt; sizeof(ULONG); k++)
            cout &lt;&lt; psysPoolTag-&gt;Tag[k];

        cout &lt;&lt; endl;

        if (psysPoolTag-&gt;NonPagedAllocs != 0)
        `{`
            cout &lt;&lt; "NonPaged Allocs: " &lt;&lt; psysPoolTag-&gt;NonPagedAllocs &lt;&lt; endl;
            cout &lt;&lt; "NonPaged Frees: " &lt;&lt; psysPoolTag-&gt;NonPagedFrees &lt;&lt; endl;
            cout &lt;&lt; "NonPaged Pool Bytes Used: " &lt;&lt; psysPoolTag-&gt;NonPagedUsed &lt;&lt; endl;
        `}`
        else
        `{`
            cout &lt;&lt; "Paged Allocs: " &lt;&lt; psysPoolTag-&gt;PagedAllocs &lt;&lt; endl;
            cout &lt;&lt; "Paged Frees: " &lt;&lt; psysPoolTag-&gt;PagedFrees &lt;&lt; endl;
            cout &lt;&lt; "Paged Pool Bytes Used: " &lt;&lt; psysPoolTag-&gt;PagedUsed &lt;&lt; endl;
        `}`

        psysPoolTag++;
        cout &lt;&lt; endl &lt;&lt; "-------------------------------" &lt;&lt; endl;
        cout &lt;&lt; endl &lt;&lt; "-------------------------------" &lt;&lt; endl &lt;&lt; endl;

    `}`

    if (InfoBuf != nullptr)
        delete[] InfoBuf;

Exit:
    cin.get();
    return 0;
`}`
```



## Defs.h

```
#include &lt;Windows.h&gt;

#define SystemPoolTagInformation (DWORD)0x16

#define STATUS_SUCCESS 0
#define STATUS_INFO_LENGTH_MISMATCH 0xC0000004

typedef DWORD SYSTEM_INFORMATION_CLASS;

typedef struct _SYSTEM_POOLTAG
`{`
    union
    `{`
        UCHAR Tag[4];
        ULONG TagUlong;
    `}`;
    ULONG PagedAllocs;
    ULONG PagedFrees;
    SIZE_T PagedUsed;
    ULONG NonPagedAllocs;
    ULONG NonPagedFrees;
    SIZE_T NonPagedUsed;

`}`SYSTEM_POOLTAG, *PSYSTEM_POOLTAG;

typedef struct _SYSTEM_POOLTAG_INFORMATION
`{`
    ULONG Count;
    SYSTEM_POOLTAG TagInfo[ANYSIZE_ARRAY];

`}`SYSTEM_POOLTAG_INFORMATION, *PSYSTEM_POOLTAG_INFORMATION;


typedef NTSTATUS(WINAPI *_ZwQuerySystemInformation)(
    _In_      SYSTEM_INFORMATION_CLASS SystemInformationClass,
    _Inout_   PVOID                    SystemInformation,
    _In_      ULONG                    SystemInformationLength,
    _Out_opt_ PULONG                   ReturnLength
    );
```



## 目标PoolTag信息

为了理解获取的 PoolTag 信息，有必要分析我们感兴趣的那些驱动程序。通过搜索对 `ExAllocatePoolWithTag` 的调用， 我们可以记录这些驱动程序使用的特定标记并将它们保存在我们的列表中。

此时，你应该知道任何驱动程序都可以随意使用任何标记，因此，尝试查找一些看起来不太常见但标准Windows内核驱动程序和/或对象没有使用的标记是有意义的。

话虽如此，如果使用时不多多小心谨慎，这种检测特定驱动的方法也可能会产生误报。



## PoolTag示例列表

为了证明以上PoC，我们从特定的驱动程序中收集了一些PoolTag信息。
<li>VMWare（Guest操作系统）
<ul>
- vm3dmp.sys（标签：VM3D）
- vmci.sys（标签：CTGC，CTMM，QPMM等……）
- vmhgfs.sys（标签：HGCC，HGAC，HGVS，HGCD等……）
- vmmemctl.sys（标签：VMBL）
- vsock.sys（标签：vskg，vskd，vsks等…）- procexp152.sys（标签：PEOT，PrcX等…）- procmon23.sys（标签：Pmn）- sysmondrv.sys（标签：Sys1，Sys2，Sys3，SysA，SysD，SysE等…）- aswsnx.sys（标签：’Snx ‘，Aw++）（我们在第一个中使用单引号，因为它以空格字符结尾）
- aswsp.sys（标签：pSsA，AsDr）


## 结论

与其他方法一样，这个方法有其优点和缺点。

这种方法不容易被规避，特别是在64位Windows中，内核补丁保护（Patch Guard）不允许我们修改内核函数，因此直接 Hook `NtQuerySystemInformation` 等函数的解决方案对于安全和监控工具就不再可用。

此外，此方法不受某些驱动程序的影响, 例如试图阻止来自用户层进程访问特定进程、文件和注册表项的驱动(或向用户层进程隐藏这些信息)。

此外，该方法可能用于进一步识别主机指纹。

通过搜索操作系统中引入的Windows对象的特定标记，我们可以确定其主要版本。

例如，通过比较不同版本的Windbg附带的poolTag信息（pooltag.txt），（在本例中为Windows 8.1 x64和Windows 10 x64 Build 10.0.15063），我们能够能够发现，Windows 10中 `netio.sys` 内核驱动使用的 `PoolTags`，如 `Nrsd`， `Nrtr`， `Nrtw`，在Windows 8.1中都不存在。

我们后来使用两个虚拟机进行了快速验证，确实可以在Windows 10中找到至少有两个上述标签的内存分配，而Windows 8.1虚拟机中并没有这些。

话虽这么说，内核驱动程序开发中使用Tag关联内存块和分配内存块的驱动模块, 依然是一种常见且良好的做法。

另一方面，如前所述，`PoolTags` 可以随意使用，因此我们必须小心选择我们要对付的驱动。

最后要提到的是，`PoolTag` 信息一直在变化，换句话说，内存块一直在被分配和释放，因此我们在选择要搜索的`PoolTag`时应该牢记这一点。

尽管这种方法看起来实验性超过实际使用，但实际上当恶意软件搜索特定的监控和安全软件时，PoolTag信息可能非常可靠。

**参考**
1. [https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/wdm/nf-wdm-exallocatepoolwithtag](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/wdm/nf-wdm-exallocatepoolwithtag)
1. [https://msdn.microsoft.com/en-us/library/windows/desktop/ms724509(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms724509(v=vs.85).aspx)
1. [https://github.com/arizvisa/ndk](https://github.com/arizvisa/ndk)
1. [http://blogs.microsoft.co.il/pavely/2016/09/14/kernel-pool-monitor-the-gui-version/](http://blogs.microsoft.co.il/pavely/2016/09/14/kernel-pool-monitor-the-gui-version/)