> 原文链接: https://www.anquanke.com//post/id/213775 


# Adobe Reader沙箱逆向分析：探寻IPC内部结构


                                阅读量   
                                **132564**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者dronesec，文章来源：dronesec.pw
                                <br>原文地址：[http://dronesec.pw/blog/2020/08/07/digging-the-adobe-sandbox-internals/](http://dronesec.pw/blog/2020/08/07/digging-the-adobe-sandbox-internals/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t019787e774741c8954.png)](https://p0.ssl.qhimg.com/t019787e774741c8954.png)



## 0x00 概述

在这一系列文章中，我将介绍如何逆向Adobe Reader沙箱。这是我从去年年初开始的研究，直到目前一直在持续进行。这一系列文章将记录Reader沙箱的内部结构，介绍一些可以对其进行逆向或与其进行交互的工具，并对这一系列研究的结果进行描述。在这里，我详细记录了研究的过程和遇到的问题，希望能让研究人员收获到比纯技术成果更多的内容。

我的这一系列研究将会分为两篇文章。其中，第一篇文章将详细介绍沙箱的内部结构，并介绍一系列开发的工具，而第二篇文章会将重点放在模糊测试和研究成果上面。

这篇文章主要侧重于分析沙箱进程与代理（Broker）之间进行通信的IPC通道。我们不会过于深入地研究策略引擎的工作原理或已经启用的一些限制。



## 0x01 介绍

这并不是第一次对Adobe Reader沙箱进行深入研究。下面回顾了此前针对Adobe Reader沙箱进行过的一些出色研究工作：

2011年 – A Castle Made of Sand （Richard Johnson）

[https://talos-intelligence-site.s3.amazonaws.com/production/document_files/files/000/000/058/original/A_Castle_Made_of_Sand-HES_final.pdf](https://talos-intelligence-site.s3.amazonaws.com/production/document_files/files/000/000/058/original/A_Castle_Made_of_Sand-HES_final.pdf)

2011年 – 分析Reader X沙箱（Paul Sabanal和Mark Yason）

[https://docs.huihoo.com/blackhat/usa-2011/BH_US_11_SabanalYason_Readerx_Slides.pdf](https://docs.huihoo.com/blackhat/usa-2011/BH_US_11_SabanalYason_Readerx_Slides.pdf)

2012年 – 制作沙箱蠕虫（Zhenhua Liu和Guillaume Lovet）

[https://media.blackhat.com/bh-eu-12/Liu_Lovet/bh-eu-12-Liu_Lovet-Sandworms-WP.pdf](https://media.blackhat.com/bh-eu-12/Liu_Lovet/bh-eu-12-Liu_Lovet-Sandworms-WP.pdf)

2013年 – 当代理被攻破（Peter Vreugdenhil）

[https://cansecwest.com/slides/2013/Adobe%20Sandbox.pdf](https://cansecwest.com/slides/2013/Adobe%20Sandbox.pdf)

在《制作沙箱蠕虫》这篇文章中，详细描述了transaction的内部原理以及如何对沙箱进行模糊测试。我会在本系列的第二篇文章中详细描述我的方法和改进。

此外，ZDI团队的Abdul-Aziz Hariri等成员始终在研究JavaScript的攻击面，试图滥用Adobe Reader的JavaScript API，并且在这一方面取得了比较好的成果。

但是，在评估现有研究之后，似乎还有更多的工作需要以更加开源的形式进行。如今，Reader中的大多数沙箱逃逸漏洞都选择通过win32k/dxdiag/etc来攻击Windows自身，而不再选择沙箱代理。这是有道理的，但是也随之留下了许多没有开发的攻击面。

请注意，所有研究都是在Windows 10计算机的Acrobat Reader DC 20.6.20034上完成的。大家可以在这里（[https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html）获取Adobe](https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html%EF%BC%89%E8%8E%B7%E5%8F%96Adobe) Reader旧版本的安装程序。我强烈建议收藏这个旧版本记录。在针对一个新目标进行分析之前，我最喜欢做的就是了解历史漏洞和受影响版本，分析其根本原因，并进行漏洞利用尝试。



## 0x02 沙箱内部概览

Adobe Reader的沙箱称为“保护模式”，默认情况下处于启用状态，但可以通过选项设置或注册表来启用和关闭。在启动Reader后，会在较低的完整性下生成一个子进程，并在其中映射一部分共享内存。进程间通信（IPC）将通过该通道进行，其父进程作为代理（Broker）。

实际上，在7年之前，Adobe实际上已经在Github上发布了一些沙箱的源代码，但是其中不包含任何策略或现代的标记接口（Tag Interface）。这对于我们在逆向过程中寻找变量和函数名来说很有帮助，并且，源代码的编码习惯非常好，其中包含了清晰的注释，因此我建议大家可以参考。

Reader使用Chromium沙箱（Mojo之前的版本），我推荐大家可以关注以下资源：

1、官方文档（[https://chromium.googlesource.com/chromium/src/+/master/docs/design/sandbox.md）](https://chromium.googlesource.com/chromium/src/+/master/docs/design/sandbox.md%EF%BC%89)

2、白皮书（[https://seclab.stanford.edu/websec/chromium/chromium-security-architecture.pdf）](https://seclab.stanford.edu/websec/chromium/chromium-security-architecture.pdf%EF%BC%89)

3、源代码（[https://github.com/chromium/chromium/tree/master/sandbox/win/src）](https://github.com/chromium/chromium/tree/master/sandbox/win/src%EF%BC%89)

4、allpaca沙箱逃逸的Github项目（[https://github.com/allpaca/chrome-sbx-db）](https://github.com/allpaca/chrome-sbx-db%EF%BC%89)

如今，它已经被称为“旧版IPC”，在Chrome中已经被Mojo取代。Reader实际上是使用Mojo在其RdrCEF（Chromium嵌入式框架）进程之间进行通信，该进程处理云连接、同步等等。Adobe可能计划在某个时间节点使用Mojo替换Broker旧版API，但目前尚未宣布或发布。

首先，我们将简要介绍目标进程是如何派生的，但这篇文章将重点放在了起到实际作用的IPC机制。子进程的执行过程首先从`BrokerServicesBase::SpawnTarget`开始。这个函数可以生成目标进程及其限制。我们对其中的一部分进行了详细分析，具体如下：

1、创建受限Token
<li>通过`CreateRestrictedToken`
</li>
- 低完整性或AppContainer（如果可用）
2、创建受限Job对象
- 没有到剪贴板的读取/写入
- 在其他进程中无法访问用户句柄
- 没有消息广播
- 没有全局挂钩
- 没有全局原子表访问
- 无需更改显示设置
- 无需桌面切换/创建
- 没有ExitWindows调用
- 没有SystemParamtersInfo
- 一个活跃进程
- 在发生异常情况或存在未处理的异常时会终止
从这里开始，策略管理器将强制执行由`InterceptionManager`处理的拦截，该拦截将处理通过目标进程到代理的各种Win32函数的Hooking和重连。根据文档，这不是为了安全，而是因为：

“…用于在无法修改沙箱中的代码以应对沙箱限制时提供兼容性。为了节省不必要的IPC，在进行IPC调用之前，还会在目标进程中评估策略，这并不是用于安全性保证，而仅仅是用于速度上的优化。”

现在，我们可以从这里了解目标进程和代理进程之间的IPC机制是如何工作的。

代理进程负责生成目标进程、创建共享内存映射以及初始化必要的数据结构。这个共享内存映射是代理与目标之间进行通信和交换数据的媒介。如果目标需要进行IPC调用，则会发生以下情况：

1、目标找到处于空闲状态的通道。

2、目标将IPC调用参数序列化到通道。

3、随后，目标向该通道发出事件对象的信号（ping事件）。

4、目标等待，直到发出pong事件信号。

此时，代理将执行ThreadPingEventReady（IPC处理器入口点），会发生以下情况：

1、代理对通道中的调用参数进行反序列化。

2、对参数和调用进行完整性检查。

3、执行回调。

4、将返回结构写回到通道。

5、发出信号表示调用已经完成（pong事件）。

一共有16个可以使用的通道，这意味着代理一次可以服务多达16个并发的IPC请求。下图是描述这个体系结构的更高级别视图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0196489069e9f0310e.png)

从代理的角度来看，通道的结构如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eca52b7c25fbac3e.png)

总体来说，上述内容描述了Borker和目标之间的IPC通信通道原理。在以下的各小节中，我们将更加深入地介绍这些内容。



## 0x03 IPC内部结构

IPC是通过`TargetProcess::Init`建立的，而这正是我们想要研究的内容。下面代码描述了如何在代理和目标之间创建和建立共享内存映射：

```
DWORD shared_mem_size = static_cast&lt;DWORD&gt;(shared_IPC_size +
                                             shared_policy_size);
  shared_section_.Set(::CreateFileMappingW(INVALID_HANDLE_VALUE, NULL,
                                           PAGE_READWRITE | SEC_COMMIT,
                                           0, shared_mem_size, NULL));
  if (!shared_section_.IsValid()) `{`
    return ::GetLastError();
  `}`

  DWORD access = FILE_MAP_READ | FILE_MAP_WRITE;
  base::win::ScopedHandle target_shared_section;
  if (!::DuplicateHandle(::GetCurrentProcess(), shared_section_,
                         sandbox_process_info_.process_handle(),
                         target_shared_section.Receive(), access, FALSE, 0)) `{`
    return ::GetLastError();
  `}`

  void* shared_memory = ::MapViewOfFile(shared_section_,
                                        FILE_MAP_WRITE|FILE_MAP_READ,
                                        0, 0, 0);
```

源代码中，计算出的`shared_mem_size`为65536字节，这是不正确的。在现代Reader二进制文件中，共享字节实际上是0x20000字节。

一旦建立了映射，并复制了策略，接下来就要初始化`SharedMemIPCServer`，在这里事情会变得有趣。

`SharedMemIPCServer`会对用于通信的ping/pong事件进行初始化，创建通道并注册回调。

先前的架构图描述了在运行时这部分的结构和布局。简而言之，`ServerControl`是IPC通道的代理侧视图。它包含服务器端事件句柄、指向通道及其缓冲区的指针，以及有关连接IPC终端的通用信息。该结构对目标进程不可见，仅存在于代理中。

`ChannelControl`是目标进程版本的`ServerControl`。它包含目标的事件句柄、通道的状态，以及有关在哪里查找通道缓冲区的信息。在成功分配IPC后，可以在这个通道缓冲区中找到`CrossCallParams`以及调用返回信息。

让我们来看一下实际的请求。发出IPC请求，需要目标首先准备一个`CrossCallParams`结构。它被定义为一个类，但是我们可以将其模型化为一个结构：

```
const size_t kExtendedReturnCount = 8;

struct CrossCallParams `{`
  uint32 tag_;
  uint32 is_in_out_;
  CrossCallReturn call_return;
  size_t params_count_;
`}`;

struct CrossCallReturn `{`
  uint32 tag_;
  uint32 call_outcome;
  union `{`
    NTSTATUS nt_status;
    DWORD win32_result;
  `}`;

  HANDLE handle;
  uint32 extended_count;
  MultiType extended[kExtendedReturnCount];
`}`;

union MultiType `{`
  uint32 unsigned_int;
  void* pointer;
  HANDLE handle;
  ULONG_PTR ulong_ptr;
`}`;
```

我们还继续定义了所需的其他一些结构。请注意，返回结构`CrossCallReturn`是嵌入在`CrossCallParams`的主体内。

在沙箱源代码中，提供了一个很棒的ASCII图，它很有启发性，我把它复制到这里：

```
// [ tag                4 bytes]
// [ IsOnOut            4 bytes]
// [ call return       52 bytes]
// [ params count       4 bytes]
// [ parameter 0 type   4 bytes]
// [ parameter 0 offset 4 bytes] ---delta to ---\
// [ parameter 0 size   4 bytes]                |
// [ parameter 1 type   4 bytes]                |
// [ parameter 1 offset 4 bytes] ---------------|--\
// [ parameter 1 size   4 bytes]                |  |
// [ parameter 2 type   4 bytes]                |  |
// [ parameter 2 offset 4 bytes] ----------------------\
// [ parameter 2 size   4 bytes]                |  |   |
// |---------------------------|                |  |   |
// | value 0     (x bytes)     | &lt;--------------/  |   |
// | value 1     (y bytes)     | &lt;-----------------/   |
// |                           |                       |
// | end of buffer             | &lt;---------------------/
// |---------------------------|
```

标记是一个dword，表示我们正在调用哪个功能。取决于不同版本，这个数字介于1-255之间。这是在服务器端动态处理的，我们将在后面进一步探讨。

每个参数由`ParamInfo`结构依次表示：

```
struct ParamInfo `{`
  ArgType type_;
  ptrdiff_t offset_;
  size_t size_;
`}`;
```

这里的偏移量是`CrossCallParams`结构下方某处内存区域的增量值（delta value）。在Chromium源代码中，通过`ptrdiff_t`类型对其进行了处理。

我们从目标的角度来分析内存中的调用。假设通道缓冲区位于0x2a10134：

```
0:009&gt; dd 2a10000+0x134
02a10134  00000003 00000000 00000000 00000000
02a10144  00000000 00000000 000002cc 00000001
02a10154  00000000 00000000 00000000 00000000
02a10164  00000000 00000000 00000000 00000007
02a10174  00000001 000000a0 00000086 00000002
02a10184  00000128 00000004 00000002 00000130
02a10194  00000004 00000002 00000138 00000004
02a101a4  00000002 00000140 00000004 00000002
```

0x2a10134表示我们正在调用标记3，其中包含7个参数（0x2a10170）。第一个参数的类型是0x1（我们将在后面介绍类型），其增量偏移量是0xa0，大小为0x86字节。因此：

```
0:009&gt; dd 2a10000+0x134+0xa0
02a101d4  003f005c 005c003f 003a0043 0055005c
02a101e4  00650073 00730072 0062005c 0061006a
02a101f4  006a0066 0041005c 00700070 00610044
02a10204  00610074 004c005c 0063006f 006c0061
02a10214  006f004c 005c0077 00640041 0062006f
02a10224  005c0065 00630041 006f0072 00610062
02a10234  005c0074 00430044 0052005c 00610065
02a10244  00650064 004d0072 00730065 00610073
0:009&gt; du 2a10000+0x134+0xa0
02a101d4  "\??\C:\Users\bjaff\AppData\Local"
02a10214  "Low\Adobe\Acrobat\DC\ReaderMessa"
02a10254  "ges"
```

这里显示了参数数据的增量，并且根据参数类型，我们可以得知它是一个unicode字符串。

有了这些信息，我们就可以设计一个针对IPC标记3的缓冲区，然后继续发送。为此，我们需要`IPCControl`结构。这是在IPC共享内存段的开头定义的一个简单结构：

```
struct IPCControl `{`
    size_t channels_count;
    HANDLE server_alive;
    ChannelControl channels[1];
`}`;
```

在IPC共享内存段中：

```
0:009&gt; dd 2a10000
02a10000  0000000f 00000088 00000134 00000001
02a10010  00000010 00000014 00000003 00020134
```

因此，我们就有了16个通道、`server_alive`的句柄以及`ChannelControl`数组的开始。

`server_alive`句柄是一个互斥量，用于指示服务器是否崩溃。它在`SharedmemIPCClient::DoCall`的代码调用期间使用，我们将在后面做详细介绍。现在，假如我们在这里`WaitForSingleObject`，并得到返回`WAIT_ABANDONED`，则证明服务器已经崩溃。

`ChannelControl`是描述通道的结构，再次被定义为：

```
struct ChannelControl `{`
  size_t channel_base;
  volatile LONG state;
  HANDLE ping_event;
  HANDLE pong_event;
  uint32 ipc_tag;
`}`;
```

`channel_base`描述了通道的缓冲区，可以在其中找到`CrossCallParams`结构。这是以共享内存段作为基址开始的偏移量。

`state`是一个描述通道状态的枚举（enum）：

```
enum ChannelState `{`
  kFreeChannel = 1,
  kBusyChannel,
  kAckChannel,
  kReadyChannel,
  kAbandonnedChannel
`}`;
```

如前所述，ping事件和pong事件用于向相反的终端发出信号，表明数据已经准备好消耗。例如，当客户端写出其CrossCallParams并准备好用于服务器时，它将会发出如下信号：

```
DWORD wait = ::SignalObjectAndWait(channel[num].ping_event,
                                     channel[num].pong_event,
                                     kIPCWaitTimeOut1,
                                     FALSE);
```

服务器完成对请求的处理后，会发出`pong_event`信号，并且客户端会读取回调用结果。

通道是通过`SharedMemIPCClient::LockFreeChannel`获取到的，在调用`GetBuffer`时调用该通道。通过在`IPCControl`数组中设置`state == kFreeChannel`，可以标识该通道，并将其设置为`kBusyChannel`。借助其中的一个通道，我们现在可以将`CrossCallParams`结构写入到共享内存缓冲区中。我们的目标缓冲区是从`channel-&gt;channel_base`开始。

写入`CrossCallParams`的过程与之前有一些细微差别。首先，实际参数的数量是`NUMBER_PARAMS+1`。根据源代码：

```
// Note that the actual number of params is NUMBER_PARAMS + 1
// so that the size of each actual param can be computed from the difference
// between one parameter and the next down. The offset of the last param
// points to the end of the buffer and the type and size are undefined.
```

我们可以在`CopyParamIn`函数中看到：

```
param_info_[index + 1].offset_ = Align(param_info_[index].offset_ +
                                            size);
param_info_[index].size_ = size;
param_info_[index].type_ = type;
```

请注意，写入的偏移量是`index+1`的偏移量。此外，这个偏移量是对齐的。这是一个非常简单的函数，将通道缓冲区内增量进行字节对齐：

```
// Increases |value| until there is no need for padding given the 2*pointer
// alignment on the platform. Returns the increased value.
// NOTE: This might not be good enough for some buffer. The OS might want the
// structure inside the buffer to be aligned also.
size_t Align(size_t value) `{`
  size_t alignment = sizeof(ULONG_PTR) * 2;
    return ((value + alignment - 1) / alignment) * alignment;
    `}`
```

因为Reader进程是x86的，因此对齐永远是8。

用于写入`CrossCallParams`的代码可以简化为如下伪代码：

```
write_uint(buffer,     tag);
write_uint(buffer+0x4, is_in_out);

// reserve 52 bytes for CrossCallReturn
write_crosscall_return(buffer+0x8);

write_uint(buffer+0x3c, param_count);

// calculate initial delta 
delta = ((param_count + 1) * 12) + 12 + 52;

// write out the first argument's offset 
write_uint(buffer + (0x4 * (3 * 0 + 0x11)), delta);

for idx in range(param_count):

    write_uint(buffer + (0x4 * (3 * idx + 0x10)), type);
    write_uint(buffer + (0x4 * (3 * idx + 0x12)), size);

    // ...write out argument data. This varies based on the type

    // calculate new delta
    delta = Align(delta + size)
    write_uint(buffer + (0x4 * (3 * (idx+1) + 0x11)), delta);

// finally, write the tag out to the ChannelControl struct
write_uint(channel_control-&gt;tag, tag);
```

在写入`CrossCallParams`结构后，沙箱进程将发出`ping_event`信号，并触发代理。

代理侧的处理非常简单。服务器在`SharedMemIPCServer::Init`期间注册`ping_event`处理程序：

```
thread_provider_-&gt;RegisterWait(this, service_context-&gt;ping_event,
                                ThreadPingEventReady, service_context);
```

`RegisterWait`只是一个对`RegisterWaitForSingleObject`进行调用的线程池包装器。

`ThreadPingEventReady`函数将通道标记为`kAckChannel`，获取指向提供的缓冲区的指针，然后调用`InvokeCallback`。一旦返回，它将`CrossCallReturn`结构复制回该通道，并发出`pong_event`互斥信号。

`InvokeCallback`解析缓冲区，并以较高级别处理数据验证（确保字符串、缓冲区和大小符合要求）。这里是一个记录支持的参数类型的好机会。一共有10种类型，其中的两种属于占位符：

```
ArgType = `{`
    0: "INVALID_TYPE",
    1: "WCHAR_TYPE", 
    2: "ULONG_TYPE",
    3: "UNISTR_TYPE", # treated same as WCHAR_TYPE
    4: "VOIDPTR_TYPE",
    5: "INPTR_TYPE",
    6: "INOUTPTR_TYPE",
    7: "ASCII_TYPE",
    8: "MEM_TYPE", 
    9: "LAST_TYPE" 
`}`
```

这些来源于`internal_types`，但是我们注意到，其中还有两种附加的类型，分别是`ASCII_TYPE`和`MEM_TYPE`，它们对于Reader来说是唯一的。`ASCII_TYPE`是一个简单的7位ASCII字符串。`MEM_TYPE`是代理用于从沙箱进程中读取数据的内存结构，适用于无法通过API轻松传递的更复杂类型。此外，它还用于数据blob，例如PNG图片、增强格式的数据文件等。

其中一些类型应该顾名思义，比如`WCHAR_TYPE`是宽字符，`ASCII_TYPE`是ASCII字符串，`ULONG_TYPE`是ulong。还有一些类型不太容易看出，比如`VOIDPTR_TYPE`、`INPTR_TYPE`、`INOUTPTR_TYPE`和`MEM_TYPE`。

从`VOIDPTR_TYPE`开始，这是Chromium沙箱中的标准类型，因此我们可以参考源代码。

`SharedMemIPCServer::GetArgs`调用`GetParameterVoidPtr`。只需要将值本身提取出来，然后将其转换为无效的ptr：

```
*param = *(reinterpret_cast&lt;void**&gt;(start));
```

这里，允许标记引用代理进程本身内部的对象和数据。其中的一个例子可能是`NtOpenProcessToken`，它的第一个参数是目标进程的句柄。首先会通过调用`OpenProcess`来检索，然后交还给子进程，并在后续可能需要使用该句柄作为`VOIDPTR_TYPE`的任何后续调用中提供。

在Chromium源代码中，通过`GetRawParameter`将`INPTR_TYPE`提取为原始值，并且不执行任何其他处理。但是，在Adobe Reader中，它实际上是以与`INOUTPTR_TYPE`相同的方式提取的。

`INOUTPTR_TYPE`包装为`CountedBuffer`，可以在IPC调用期间写入。例如，如果调用`CreateProcessW`，则`PROCESS_INFORMATION`指针的类型为`INOUTPTR_TYPE`。

最后的一个类型是`MEM_TYPE`，这是在Adobe Reader中唯一的类型。我们可以将结构定义为：

```
struct MEM_TYPE `{`
  HANDLE hProcess;
  DWORD lpBaseAddress;
  SIZE_T nSize;
`}`;
```

如前所述，这个类型主要用于与代理进程之间传输数据缓冲区。听上去似乎很疯狂。每个标记都需要对提供的值进行自行验证，然后再将其用于任何`ReadProcessMemory`/`WriteProcessMemory`调用中。

在代理解析出传递的参数后，它将获取上下文分配器，并标识我们的标记处理程序：

```
ContextDispatcher = *(int (__thiscall ****)(_DWORD, int *, int *))(Context + 24);// fetch dispatcher function from Server control
target_info = Context + 28;
handler = (**ContextDispatcher)(ContextDispatcher, &amp;ipc_params, &amp;callback_generic);// PolicyBase::OnMessageReady
```

该处理程序是从`PolicyBase::OnMessageReady`获取的，它最终将调用`Dispatcher::OnMessageReady`。这是一个非常简单的功能，可以为正确的处理程序搜寻已经注册的IPC标志列表。最后，我们找到了Reader独有的`InvokeCallbackArgs`，它会以适当的参数对调用处理程序进行计数：

```
switch ( ParamCount )
  `{`
    case 0:
      v7 = callback_generic(_this, CrossCallParamsEx);
      goto LABEL_20;
    case 1:
      v7 = ((int (__thiscall *)(void *, int, _DWORD))callback_generic)(_this, CrossCallParamsEx, *args);
      goto LABEL_20;
    case 2:
      v7 = ((int (__thiscall *)(void *, int, _DWORD, _DWORD))callback_generic)(_this, CrossCallParamsEx, *args, args[1]);
      goto LABEL_20;
    case 3:
      v7 = ((int (__thiscall *)(void *, int, _DWORD, _DWORD, _DWORD))callback_generic)(
             _this,
             CrossCallParamsEx,
             *args,
             args[1],
             args[2]);
      goto LABEL_20;

[...]
```

Reader总计支持多达17个参数的标记函数。我并不知道这些是否都是必须的，但事实确实如此。另外，可以关注每个标记处理程序的前两个参数：上下文处理程序（分配器）和`CrossCallParamsEx`。最后一个结构实际上是代理版本的`CrossCallParams`。

单个函数用于注册IPC标记，该函数由单个初始化函数调用，这就使得我们可以更轻松地在运行时发现它们。可以静态或动态地提取所有IPC标记。使用静态方法会比较容易，但使用动态方法会更加准确。我已经使用IDAPython实现了静态生成器，该生成器可以在项目的存储库（ida_find_tags.py）中使用，并可以用于将所有受支持的IPC标签及其参数列出。但是，这并不能完全涵盖所有的调用。在沙箱初始化期间，将会执行许多功能检查，以确认某些功能的可用性。如果检查未通过，就不会注册标记。

标记被赋予`CrossCallParamsEx`的句柄，该句柄使其可以访问`CrossCallReturn`结构。其定义如下：

```
struct CrossCallReturn `{`
  uint32 tag_;
  uint32 call_outcome;
  union `{`
    NTSTATUS nt_status;
    DWORD win32_result;
  `}`;

  HANDLE handle;
  uint32 extended_count;
  MultiType extended[kExtendedReturnCount];
`}`;
```

这个52字节的结构嵌入在由沙箱进程传输的`CrossCallParams`之中。一旦标记从执行中返回，就会发生以下情况：

```
if (error) `{`
    if (handler)
      SetCallError(SBOX_ERROR_FAILED_IPC, call_result);
  `}` else `{`
    memcpy(call_result, &amp;ipc_info.return_info, sizeof(*call_result));
    SetCallSuccess(call_result);
    if (params-&gt;IsInOut()) `{`
      // Maybe the params got changed by the broker. We need to upadte the
      // memory section.
      memcpy(ipc_buffer, params.get(), output_size);
    `}`
  `}`
```

沙箱进程最终可以读出结果。请注意，这个机制不允许交换更复杂的类型，因此无法使用`MEM_TYPE`。最后一步是向`pong_event`发出信号，完成调用并释放通道。



## 0x04 标记Tag

现在，我们已经了解了IPC机制本身的工作原理，接下来可以检查一下沙箱中已经实现的标记。在初始化期间，我们通过一个称为`InitializeSandboxCallback`的函数来注册代码。这是一个比较大的函数，用于处理分配沙箱标记对象并调用各自的初始化器。每个初始化器都是用一个`RegisterTag`函数来构造和注册各个标记。标记是由`SandTag`结构定义的：

```
typedef struct SandTag `{`
  DWORD IPCTag;
  ArgType Arguments[17];
  LPVOID Handler;
`}`;
```

`Arguments`数组初始化为`INVALID_TYPE`，如果标记未使用全部17个slot，那么会将其忽略。下面是标记结构的示例：

```
.rdata:00DD49A8 IpcTag3         dd 3                    ; IPCTag
.rdata:00DD49A8                                         ; DATA XREF: 000190FA↑r
.rdata:00DD49A8                                         ; 00019140↑o ...
.rdata:00DD49A8                 dd 1, 6 dup(2), 0Ah dup(0); Arguments
.rdata:00DD49A8                 dd offset FilesystemDispatcher__NtCreateFile; Handler
```

在这里，我们看到标记3包含7个参数，其中第一个是`WCHAR_TYPE`，其余6个是`ULONG_TYPE`。这与`NtCreateFile`标记处理程序一致。

将这些标签组合起来，就形成了表示其行为的一个组。一共有20个组：

```
SandboxFilesystemDispatcher
SandboxNamedPipeDispatcher
SandboxProcessThreadDispatcher
SandboxSyncDispatcher
SandboxRegistryDispatcher
SandboxBrokerServerDispatcher
SandboxMutantDispatcher
SandboxSectionDispatcher
SandboxMAPIDispatcher
SandboxClipboardDispatcher
SandboxCryptDispatcher
SandboxKerberosDispatcher
SandboxExecProcessDispatcher
SandboxWininetDispatcher
SandboxSelfhealDispatcher
SandboxPrintDispatcher
SandboxPreviewDispatcher
SandboxDDEDispatcher
SandboxAtomDispatcher
SandboxTaskbarManagerDispatcher
```

这里的名称，是从Reader二进制文件，或与Chromium的关联中提取的。每个分配器实现一个初始化例程，该例程为每个标记调用`RegisterDispatchFunction`。根据Reader进程的安装、版本、功能等，注册标记的数量将有所不同。例如，`SandboxBrokerServerDispatcher`可以拥有大约25个标志。

我在这篇文章中并没有对每个分配器进行详细分析，而是将其放在了另一个单独的页面上，在[这里](http://dronesec.pw/other/adobe-reader-tags.html)可以找到。这个页面可以用于标志参考，也包含关于每个分配器的一些通用信息。此外，我还推送了用于从Reader二进制文件中提取标记信息，并将其生成表格的脚本，位于下文提及的sander存储库中。



## 0x05 libread

在研究过程中，我开发了一个库和一组工具，来检查和分析Reader沙箱。这里的libread库可以实现与代理的实时交互，从而允许对代理的组件进行快速调试，支持动态地逆向各种功能。此外，在进行模糊测试时，这个库非常重要。所有模糊测试工具和数据会在下篇文章中提到。

libread相当灵活且易于使用，但仍然比较基础，需要依赖于我的逆向工程来工作。它并不包含完整的功能，甚至目前还不太准确，欢迎大家提出问题。

这个库实现了所有值得关注的结构，并提供了一些帮助程序函数，用于从代理进程中定位`ServerControl`。如我们所见，`ServerControl`是代理对通道的预览，仅由代理持有。这意味着，它在共享内存中是无法预测的，我们只能通过扫描代理的内存来寻找它。从沙箱端开始，还有一个`find_memory_map`帮助程序，用于查找共享内存映射的基址。<br>
除了这个库，我还将发布sander。这是一个命令行工具，使用libread来提供一些用于检查沙箱的实用功能。

```
$ sander.exe -h
[-] sander: [action] &lt;pid&gt;
          -m   -  Monitor mode
          -d   -  Dump channels
          -t   -  Trigger test call (tag 62)
          -c   -  Capture IPC traffic and log to disk
          -h   -  Print this menu
```

这里最有用的功能是`-m`标志，可以实时监视IPC调用及其参数：

```
$ sander.exe -m 6132
[5184] ESP: 02e1f764    Buffer 029f0134 Tag 266 1 Parameters
      WCHAR_TYPE: _WVWT*&amp;^$
[5184] ESP: 02e1f764    Buffer 029f0134 Tag 34  1 Parameters
      WCHAR_TYPE: C:\Users\bja\desktop\test.pdf
[5184] ESP: 02e1f764    Buffer 029f0134 Tag 247 2 Parameters
      WCHAR_TYPE: C:\Users\bja\desktop\test.pdf
      ULONG_TYPE: 00000000
[5184] ESP: 02e1f764    Buffer 029f0134 Tag 16  6 Parameters
      WCHAR_TYPE: Software\Adobe\Acrobat Reader\DC\SessionManagement
      ULONG_TYPE: 00000040
      VOIDPTR_TYPE: 00000434
      ULONG_TYPE: 000f003f
      ULONG_TYPE: 00000000
      ULONG_TYPE: 00000000
[6020] ESP: 037dfca4    Buffer 029f0134 Tag 16  6 Parameters
      WCHAR_TYPE: cWindowsCurrent
      ULONG_TYPE: 00000040
      VOIDPTR_TYPE: 0000043c
      ULONG_TYPE: 000f003f
      ULONG_TYPE: 00000000
      ULONG_TYPE: 00000000
[5184] ESP: 02e1f764    Buffer 029f0134 Tag 16  6 Parameters
      WCHAR_TYPE: cWin0
      ULONG_TYPE: 00000040
      VOIDPTR_TYPE: 00000434
      ULONG_TYPE: 000f003f
      ULONG_TYPE: 00000000
      ULONG_TYPE: 00000000
[5184] ESP: 02e1f764    Buffer 029f0134 Tag 17  4 Parameters
      WCHAR_TYPE: cTab0
      ULONG_TYPE: 00000040
      VOIDPTR_TYPE: 00000298
      ULONG_TYPE: 000f003f
[2572] ESP: 0335fd5c    Buffer 029f0134 Tag 17  4 Parameters
      WCHAR_TYPE: cPathInfo
      ULONG_TYPE: 00000040
      VOIDPTR_TYPE: 000003cc
      ULONG_TYPE: 000f003f
```

我们还可以将所有IPC调用转储到代理的通道中（`-d`），这将有助于我们在进行模糊测试时调试线程出现的问题。同时，可以使用`-t`参数触发测试IPC调用。这个函数展示了如何通过libread发送自定义IPC调用，并允许我们测试其他工具。

最后一个可以使用的功能是`-c`标志，该标志将捕获所有IPC通信，并将通道缓冲区记录到磁盘上的文件中。我主要用它在模糊测试过程中积累数据，以对一些逆向过程提供帮助。重放请求并收集实际流量的过程对我们的研究非常有帮助，我也会在后续文章中对此进行进一步讨论。

到这里，本篇文章的内容就告一段落。接下来，我将会重点讨论使用的各种模糊测试策略、遇到的失败情况以及解决的问题。



## 0x06 资源

[1] Sander [https://github.com/hatRiot/sander](https://github.com/hatRiot/sander)<br>
[2] libread [https://github.com/hatRiot/libread](https://github.com/hatRiot/libread)<br>
[3] 沙箱标记列表 [http://dronesec.pw/other/adobe-reader-tags.html](http://dronesec.pw/other/adobe-reader-tags.html)
