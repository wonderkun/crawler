> 原文链接: https://www.anquanke.com//post/id/173626 


# 利用 Windows I/O 实现本地提权


                                阅读量   
                                **264997**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者microsoft，文章来源：blogs.technet.microsoft.com
                                <br>原文地址：[https://blogs.technet.microsoft.com/srd/2019/03/14/local-privilege-escalation-via-the-windows-i-o-manager-a-variant-finding-collaboration/](https://blogs.technet.microsoft.com/srd/2019/03/14/local-privilege-escalation-via-the-windows-i-o-manager-a-variant-finding-collaboration/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p0.ssl.qhimg.com/dm/1024_576_/t01f9da61ce1cc9e9c5.gif)](https://p0.ssl.qhimg.com/dm/1024_576_/t01f9da61ce1cc9e9c5.gif)



微软应急响应中心（The Microsoft Security Response Center，MSRC）对所有影响微软产品和服务的漏洞报告进行调查研究，以确保客户和全球在线社区更加的安全。我们非常感谢安全社区定期向我们报告优秀漏洞研究成果，同时我们也认为，与这些研究进行合作将是一件极具意义的事情。

一直依赖，**Google Project Zero**的研究人员**James Forshaw**不断向我们报送高质量、有价值的漏洞。James大部分的工作集中在windows内部的复杂逻辑漏洞上，尤其是特权提升和沙箱逃逸领域。

本文介绍了James和MSRC团队之间的合作，双方在windows内核及其驱动程序中发现了新的漏洞类，并进一步阐述了微软的工程师团队是如何修复这些漏洞，以及第三方驱动开发者如何避免类似漏洞。



## 背景

在windows平台上，当用户模式线程进行系统调用时，系统调用处理程序通过将其**PreviousMode**字段设置为**UserMode**，将其记录在线程对象中。与之对应，如果是利用**Zw**前缀函数或者系统线程从内核模式发起的系统调用，其对应的**PreviousMode**字段则会设定为**KernelMode**。这种区分用户模式和内核模式调用的方法可用来判定调用的参数是否来自可信数据源，以此来确定其在内核中进行验证的程度。

当一个用户模式的应用程序创建或打开一个文件，会由`NtCreateFile`或`NtOpenFile`执行系统调用。内核模式的代码具有更加广泛的API函数集可供选择：`NtCreateFile/NtOpenFile`以及与其等价的**Zw**前缀函数，来自I/O管理器的`IoCreateFile*`系列函数以及来自Filter管理器的`FltCreateFile*`系列函数。

[![](https://p3.ssl.qhimg.com/t0184832cfcb1dfe32e.png)](https://p3.ssl.qhimg.com/t0184832cfcb1dfe32e.png)

如上图所示，所有这些调用均以I/O管理器内的`IopCreateFile`函数结束。线程的**PreviousMode**会被分配给变量**AccessMode**，该变量在`IopCreateFile`函数中决定是否对有效参数和缓冲区进行检查，然后在调用`ObOpenObjectByNameEx`函数时传递给对象管理器。之后在`IopParseDevice`中，**AccessMode**被用于访问检查。——如果是**UserMode**，则对设备对象执行权限检查。接下来，`IopParseDevice`构造一个I/O请求包（IRP），将其**RequestorMode**字段设置为**AccessMode**，并用`IofCallDriver`控制设备的`IRP_MJ_CREATE`调度功能。

`IopCreateFile`有一个**Options**参数，该参数并不向`NtCreateFile`和`NtOpenFile`函数的调用者公开，仅供来自内核模式的API函数调用。如果设置了`IO_NO_PARAMETER_CHECKING`标志，它将会覆盖**AccessMode**，使其设置为**KernelMode**而不是线程之前的模式，从而实现了绕过参数验证。这也将会导致后续在`IopParseDevice`函数中的权限检查。

需要注意的是，`IoCreateFileEx`会始终设置`IO_NO_PARAMETER_CHECKING`标志。由于`FltCreateFile、FltCreateFileEx、FltCreateFile2`会通过此函数调用I/O管理器，因此这些函数也会相应的设置有`IO_NO_PARAMETER_CHECKING`标志。

但是，有些情况下则必须覆写该参数来强制进行访问检查。比如，一个内核模式驱动程序打开一个由用户模式应用程序指定名称的对象。

如果`IopCreateFile`函数的`Options`参数设置了`IO_FORCE_ACCESS_CHECK`标志，将会产生两点影响：其一，会导致`IopParseDevice`中的I/O管理器执行访问检查，就相当于**AccessMode**是**UserMode**（实际没有将其设置为**UserMode**）。其二，在**IRP**堆栈位置中的`IRP_MJ_CREATE`，会导致`Flags`字段设置为`SL_FORCE_ACCESS_CHECK`。`IRP_MJ_CREATE`请求的处理程序将会在其访问检查中使用该标志，覆写**IRP**的**RequestorMode**。

在Windows XP的开发过程中，在对象命名空间（例如**Registry**的`ZwOpenKey`）的其他API函数调用需要一些方法，来强制进行访问检查，因此引入了`OBJ_FORCE_ACCESS_CHECK`标志。该标志设置在所请求对象的属性上，从而迫使对象管理器（而不是I/O管理器）来将请求的访问模式设置为**UserMode**。该设置的优先级高于已设置的任何访问模式——尤其是它会覆盖在**KernelMode**中设置`IO_NO_PARAMETER_CHECKING`所产生的作用，并返回`IopCreateFile`。

[![](https://p0.ssl.qhimg.com/t0168c3682966146ca1.png)](https://p0.ssl.qhimg.com/t0168c3682966146ca1.png)

综上所述：
- 在决定是否进行访问检查时，`IRP_MJ_CREATE`处理程序不仅要检查IRP的**RequestorMode**是否为**UserMode **，还需检查是否设置了`SL_FORCE_ACCESS_CHECK`标志
<li>
`IoCreateFile*`或`FltCreateFile*`的内核模式函数调用有两种方式来指定执行访问检查：
<ul>
- 利用I/O管理器，通过设置`IO_FORCE_ACCESS_CHECK`标志来最终设置IRP栈中的`SL_FORCE_ACCESS_CHECK`标志。
<li>利用对象管理器，通过设置`OBJ_FORCE_ACCESS_CHECK OptionAttributes-&gt;Attributes`标志，从而将IRP的**RequestorMode**设置为**UserMode**
</li>


## 漏洞分析

James的研究发现，windows附带了多种内核模式驱动程序，在处理`IRP_MJ_CREATE`请求时会检查IRP的**RequestorMode**，而不会检查`SL_FORCE_ACCESS_CHECK`。而且，这些都可能被内核模式代码所利用，但在表面上看，在创建或打开文件操作时设置`IO_FORCE_ACCESS_CHECK`似乎是正常操作。通过构造一些用户模式的请求，攻击者可以实现对创建/打开文件时参数的控制，并以此为基础发送`IRP_MJ_CREATE`请求，其**RequestorMode**为**KernelMode**。如果在安全决策中使用**RequestorMode**检查，则会导致本地提权漏洞。

更多细节，包括James如何发现该漏洞类以及windows内核驱动程序中此类代码出现位置的示例，可以参考其 [Google Project Zero的博客](https://googleprojectzero.blogspot.com/2019/03/windows-kernel-logic-bug-class-access.html)。

[![](https://p5.ssl.qhimg.com/t01c59f4ab081de1722.png)](https://p5.ssl.qhimg.com/t01c59f4ab081de1722.png)

James specified two kernel mode code patterns – the ‘initiator’, which makes a file create/open call, and the ‘receiver’, which handles IRP_MJ_CREATE requests. These are defined as follows:

James指定了两种内核代码模式——创建和打开文件的**initiator**，处理`IRP_MJ_CREATE`请求的**receiver**。具体内容如下：
<li>
**initiator**包括以下内容：
<ul>
<li>调用API函数（`IoCreateFile*`或`FltCreateFile*`）打开文件，其中：
<ul>
<li>设置了`IO_NO_PARAMETER_CHECKING`标志（或者，该函数调用来自系统线程）
<ul>
<li>这会将IRP的**RequestorMode**设置为**KernelMode**
</li>
<li>对于`IoCreateFileEx`和`FltCreateFile*`，将会隐式设置`IO_NO_PARAMETER_CHECKING`
</li>
</ul>
</li>
<li>
`IO_FORCE_ACCESS_CHECK`标志被设置，表示将进行访问检查</li>
<li>
**ObjectAttributes**中没有设置`OBJ_FORCE_ACCESS_CHECK`标志
<ul>
<li>如果设置了该标志，会覆盖IRP的**RequestorMode**，将其设定为**UserMode**
</li>
</ul>
</li>
1. 攻击者可以采取措施，控制调用过程
</ul>
</li>
</ul>
</li>
<li>
**receiver**包括一下内容：
<ul>
<li>针对`IRP_MJ_CREATE`请求的处理函数，其中：
<ul>
1. IRP的**RequestorMode**被用于设定安全策略
1. 处理过程中，IRP栈中对应位置的Flags没有做`SL_FORCE_ACCESS_CHECK`检测
</ul>
</li>
</ul>
</li><li>如果设置了该标志，会覆盖IRP的**RequestorMode**，将其设定为**UserMode**
</li>
攻击者需要能够指示**initiator**打开由**receiver**处理的设备对象。**receiver**中的安全检测会被绕过，因为`Irp-&gt;RequestorMode`将会被设置为**KernelMode**，但并没有检测`SL_FORCE_ACCESS_CHECK`标志。

James在研究中发现了**initiator**和**receiver**的实例，但并未发现两者链接在一起所导致的权限提升。我们选择与其合作进行深入研究，以期望共同有所发现。



## 合作中的发现

针对windows的官方驱动（由Microsoft编写）以及Windows内核，我们选用Semmle QL来对源代码进行搜索，找寻符合上述模式的漏洞代码。

为找到**initiator**代码模式，我们通过自定义的数据流分析的方法，对`Options`和`ObjectAttributes-&gt;Attributes`的标志组合当其传递给内部函数`IopCreateFile`时进行跟踪。正如前文提到的，各种打开文件的API函数最终都会执行到此函数。对结果进行过滤筛选，仅显示设置了`IO_FORCE_ACCESS_CHECK`和`IO_NO_PARAMETER_CHECKING`标志、但未设置`OBJ_FORCE_ACCESS_CHECK`标志的调用。而且我们并不关心那些攻击者无法控制的对象名称。

为找到**receiver**代码模式，我们对控制表达式（即控制流语句中的表达式，例如if 和 switch 语句）进行了检查，该表达式受IRP对象**RequestorMode**字段影响且可以通过`IRP_MJ_CREATE`调度或过滤函数访问。这些过滤函数筛除了一些表达式，主要是包含`SL_FORCE_ACCESS_CHECK`宏和对`IO_STACK_LOCATION`对象`Flags`字段访问。在手动跟踪的过程中，排除了少量**RequestorMode**的检查，因为它们本质上没有相应的安全影响（例如，它们被用于排除内核模式调用，而不是允许操作）。

经过初步分析，在Windows源码中，发现了11个潜在的**initiators**和16个潜在的**receivers**，包括James已经向我们报送的。

Windows还附带了一些“inbox drivers”——即第三方驱动程序，它们对于启动某些设备至关重要，或者它们能够实现开箱即用的全功能安装。我们对每个驱动程序的二进制文件筛选其导入表，得到一个子集以便下一步分析。对于**initiators**而言，这些是`IoCreateFile*`或`FltCreateFile*`的导入，而对于**receivers**而言，就是`oCreateDevice`或`FltRegisterFilter`，因为我们只关心那些通过设备对象或过滤器可访问的代码。使用IDA Pro分析余下部分的驱动文件，并没有发现**initiators**或是**receivers**。

利用这些潜在的漏洞需要更具兼容性的**initiators**和**receivers**。尤其是，**initiator**要为最终调用`IopCreateFile`的攻击者提供足够的控制权，以便可以进一步利用**receiver**。

我们可将**receiver**划分为两大类：
- 需要提供特定的扩展属性，要么进行**RequestorMode**检查，要么在实现绕过之后在利用方面做些有用的事情
- 要求将文件句柄传回给攻击者，以便获取其他可利用的IRP调度函数的代码
幸运的是，在我们的分析过程中，没有发现任何**initiators**能够为攻击者提供足够的能力来执行上述任何一个操作。

下一步的分析工作，我们扩大搜索内容的范围，囊括所有对内核模式文件创建/打开的API调用，包括`ZwCreateFile`和`ZwOpenFile`的调用，以及设置了`IO_NO_PARAMETER_CHECKING`标志（无论是否设置了`IO_FORCE_ACCESS_CHECK`）的`IoCreateFile*`和`FltCreateFile*`的调用。在排除所有设置了`OBJ_FORCE_ACCESS_CHECK`标志的调用之后，仍然剩下几百条内核和驱动代码的记录，因此我们聚焦上述两类**receiver**策略来进行过滤筛选。

首先，我们过滤掉`EaBuffer`参数为非空的函数调用，从而查看扩展属性的传入位置。其次，我们过滤掉没有设置`OBJ_KERNEL_HANDLE`标志的调用，查看一个可用对象具柄传回用户模式时可能的位置。上述操作可以有效将结果进行缩减，可进一步进行手动分析。但是，我们并没有在结果中发现任何代码可以来用作有效**initiator**。



## 纵深防御安全举措

综合James和MSRC的联合研究，在当前支持的windows版本中似乎并没有发现**initiator**和**receiver**的有效组合，能有用于实现本地权限提升操作。

尽管如此，我们仍计划在未来的windows版本中解决这些问题，作为深度防御举措。大多数补丁都在**Windows 10 19H1**中发布，还有一部分有待进一步的兼容性测试，因为在默认情况下并不推荐使用其组件。

在对API进行改进时，我们确确实实考虑扩大修复的范围来阻止**initiator**，这样依赖如果设置了`IO_FORCE_ACCESS_CHECK`选项，RIP的**RequestorMode**则会自动设置为**UserMode**，就如同设置了`OBJ_FORCE_ACCESS_CHECK`选项一样。但是，第三方驱动程序可能依赖于现有状态，破坏现有的这种兼容性依赖的风险还是太高。



## 给驱动开发者的建议

In IRP_MJ_CREATE dispatch handlers, don’t rely on the value of the IRP’s RequestorMode without also checking for the SL_FORCE_ACCESS_CHECK flag. For example, instead of:

存在一些第三方的驱动程序，容易遭受此类漏洞的影响，我们已经要求所有内核驱动开发者检查其代码，确保正确处理了IRP请求、防御性使用文件打开API。

建议改进的过程应相对简易。

在`IRP_MJ_CREATE`调度处理程序中，不依赖于IRP的**RequestorMode**的数值，也不检查`SL_FORCE_ACCESS_CHECK`标志。比如，下面的程序应当修改：

```
if (Irp-&gt;RequestorMode != KernelMode)
    `{`
        // reject user mode requestors
        Status = STATUS_ACCESS_DENIED;
    `}`
```

应使用以下片段：

```
PIO_STACK_LOCATION IrpSp = IoGetCurrentIrpStackLocation(Irp);

    if ((Irp-&gt;RequestorMode != KernelMode) || (IrpSp-&gt;Flags &amp; SL_FORCE_ACCESS_CHECK))
    `{`
        // reject user mode requestors
        Status = STATUS_ACCESS_DENIED;
    `}`
```

其次，如果已经在选项中设置了`IO_FORCE_ACCESS_CHECK`标志，我们强烈简易您在**ObjectAttributes**中设置`OBJ_FORCE_ACCESS_CHECK`标志。例如：

```
InitializeObjectAttributes(
        &amp;ObjectAttributes,
        FileName,
        (OBJ_CASE_INSENSITIVE | OBJ_FORCE_ACCESS_CHECK),
        NULL,
        NULL);
    Status = IoCreateFileEx(
        &amp;ObjectHandle,
        GENERIC_READ | SYNCHRONIZE,
        &amp;ObjectAttributes,
        &amp;IoStatusBlock,
        NULL,
        0,
        0,
        FILE_OPEN,
        0,
        NULL,
        0,
        CreateFileTypeNone,
        NULL,
        IO_FORCE_ACCESS_CHECK);
```

更一般的情况，在代表用户模式请求下创建/打开文件，不要盲目认为线程之前的模式是**UserMode**，这会被转发到IRP的**requestor**模式——通过在**ObjectAttributes**中设置`OBJ_FORCE_ACCESS_CHECK`标志可以显示出来。



## 声明

我们要再次感谢James Forshaw与我们合作进行漏洞研究，以及他与MSRC分享的其他高质量漏洞报告。

还要感谢Paul Brookes, Dileepa Kidambi Sudarsana, and Michelle Chen的帮助，将静态分析应用到整个windows代码库。
