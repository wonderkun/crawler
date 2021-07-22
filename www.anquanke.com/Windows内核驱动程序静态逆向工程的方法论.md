> 原文链接: https://www.anquanke.com//post/id/203237 


# Windows内核驱动程序静态逆向工程的方法论


                                阅读量   
                                **353716**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者specterops，文章来源：posts.specterops.io
                                <br>原文地址：[https://posts.specterops.io/methodology-for-static-reverse-engineering-of-windows-kernel-drivers-3115b2efed83](https://posts.specterops.io/methodology-for-static-reverse-engineering-of-windows-kernel-drivers-3115b2efed83)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t016805c62de7943df7.png)](https://p1.ssl.qhimg.com/t016805c62de7943df7.png)



## 一、概述

多年来，许多恶意组织纷纷致力于针对Windows内核模式软件驱动程序进行攻击，特别是针对第三方发布的驱动程序开展攻击。在这些漏洞中，一个比较常见和有据可查的就是CAPCOM.sys任意函数执行、Win32k.sys本地特权提升以及EternalBlue池损坏漏洞。攻击者在驱动程序中得到了一些新的攻击维度，无论是通过传统的漏洞利用原语，还是滥用合法的驱动程序功能，这些都无法在用户模式中实现。

随着Windows安全性的不断发展，研究内核模式驱动程序中的漏洞利用对于我们的攻防技术而言变得越来越重要。为了辅助分析这些漏洞，我认为比较重要的一件事是，我们需要在研究中探寻内核漏洞，并找到一些值得关注并且可以滥用的功能。

在本文中，我将首先介绍驱动程序的工作原理，说明所需的先验知识，随后将进入反汇编领域，逐步查找潜在的易受攻击的内部函数。

我们的分析过程将尽量将复杂的问题简单化，因此在文章中可能会包含指向其他资源的一些链接，希望各位读者按需参考。



## 目标识别与选择

通常情况下，我们要首先分析的，就是基础工作站和服务器映像上到底加载了哪些驱动程序。如果我们能在这些核心驱动程序中发现漏洞，那么其影响将会比较广泛。同时，这也在对抗过程中带来了一个好处，也就是不需要再投放和加载新的驱动程序，从而降低被发现的概率。为此，我将手动查看注册表中的驱动程序（HKLMSystemControlSetServices，其中Type为0x1，ImagePath包含*.sys的条目），或使用类似于DriverQuery的工具通过C2来运行。

[![](https://p1.ssl.qhimg.com/t0122d58fa97b9158b4.png)](https://p1.ssl.qhimg.com/t0122d58fa97b9158b4.png)

在选择目标时，我们需要考虑综合因素，因为没有某一种特定类型的驱动程序是比较容易受到攻击的。尽管如此，但我们倾向于将目标放在由安全厂商发布的驱动程序、由主板厂商发布的任何内容以及性能监控软件。并且，我们倾向于忽略掉微软的驱动程序，因为我们通常没有太多的时间对其进行深入研究。



## 二、驱动内部原理分析

如果大家以前没有开发过内核模式软件驱动程序，那么可能会发现，它看起来要比实际复杂得多。在开始进行逆向之前，必须首先了解三个重要概念————DriverEntry、IRP Handler和IOCTL。

### <a class="reference-link" name="2.1%20DriverEntry"></a>2.1 DriverEntry

与C/C++语言中的main()函数非常相似，驱动程序必须指定入口点DriverEntry。

DriverEntry要负责很多工作，例如创建设备对象、创建用于与驱动程序和核心函数（IRP Handler、卸载函数、回调例程等）进行通信的符号链接。

DriverEntry首先使用到`IoCreateDevice()`或`IoCreateDeviceSecure()`的调用来创建设备对象，后者通常用于将安全描述符应用于设备对象，以限制对本地管理员和NT AUTHORITYSYSTEM的访问。

接下来，`DriveEntry`将`IoCreateSymbolicLink()`与先前创建的设备对象一起使用，以建立符号链接，该链接将允许用户模式进程与驱动程序进行通信。

其代码如下：

```
NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath) `{`
    UNREFERENCED_PARAMETER(RegistryPath);
    NTSTATUS status;

    // Create the device object
    UNICODE_STRING devName = RTL_CONSTANT_STRING(L"\Device\MyDevice");
    PDEVICE_OBJECT DeviceObject;
    NTSTATUS status = IoCreateDevice(DriverObject, 0, &amp;devName, FILE_DEVICE_UNKNOWN, 0, FALSE, &amp;DeviceObject);
    if (!NT_SUCCESS(status)) `{`
        KdPrint(("Failed to create device object");
        return status;
    `}`

    // Create the symbolic link
    UNICODE_STRING symLink = RTL_CONSTANT_STRING(L"\??\MySymlink");
    status = IoCreateSymbolicLink(&amp;symLink, &amp;devName);
    if (!NT_SUCCESS(status)) `{`
        KdPrint(("Failed to create symbolic link"));
        IoDeleteDevice(DeviceObject);
        return status;
    `}`

    return status;
`}`
```

最后，`DriverEntry`还定义了IRP Handler的函数。

### <a class="reference-link" name="2.2%20IRP%20Handler"></a>2.2 IRP Handler

中断请求包（IRP）本质上只是驱动程序的一条指令。这些数据包允许驱动程序通过提供函数所需的相关信息来执行特定的主要函数。主要函数的代码较多，但其中最常见的是`IRP_MJ_CREATE`、`IRP_MJ_CLOSE`和`IRP_MJ_DEVICE_CONTROL`。这些与用户模式函数相关：

IRP_MJ_CREATE → CreateFile<br>
IRP_MJ_CLOSE → CloseFile<br>
IRP_MJ_DEVICE_CONTROL → DeviceIoControl

在用户模式下执行以下代码时，驱动程序将收到具有主要函数代码`IRP_MJ_CREATE`的IRP，并将执行`MyCreateCloseFunction`函数：

```
hDevice = CreateFile(L"\\.\MyDevice", GENERIC_WRITE|GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
```

在几乎所有情况下，对我们来说最重要的主要函数是`IRP_MJ_DEVICE_CONTROL`，该函数用于发送请求，以从用户模式执行特定的内部函数。这些请求中包括一个IO控制代码，该代码负责通知驱动程序具体的操作，还包含一个向驱动程序发送数据和从驱动程序接收数据的缓冲区。

### <a class="reference-link" name="2.3%20IOCTL"></a>2.3 IOCTL

IO控制代码（IOCTL）是我们的主要搜寻目标，因为其中包含我们需要知道的很多重要细节。它是以DWORD表示，每一个32位都表示有关请求的详细信息，包括设备类型、需要的访问、函数代码和传输类型。微软提供了一个可视化的图表来分解这些字段：

[![](https://p5.ssl.qhimg.com/t01441ed0da8c8fb4ef.png)](https://p5.ssl.qhimg.com/t01441ed0da8c8fb4ef.png)

1、传输类型：定义将数据传递到驱动程序地方式，具体的类型可以是`METHOD_BUFFERED、METHOD_IN_DIRECT`、`METHOD_OUT_DIRECT`或`METHOD_NEITHER`。

2、函数代码：驱动程序要执行的内部函数。这部分应该是以0x800开始，但实际上我们会发现，很多都是从0x0开始的。其中的自定义位（Custom bit）用于定义厂商分配的值。

3、设备类型：在`IoCreateDevice(Secure)()`指定的驱动程序设备对象类型。在Wdm.h和Ntddk.h中，定义了许多设备类型，但对于软件驱动程序而言，最常见的一种就是`FILE_DEVICE_UNKNOWN (0x22)`。其中的通用位（Common bit）用于定义厂商分配的值。

驱动程序标头定义示例如下：

```
#define MYDRIVER_IOCTL_DOSOMETHING CTL_CODE(0x8000, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
```

我们完全可以自行对这些值进行解码，但如果大家觉得解码过程过于繁琐，可以使用OSR的在线解码器。并且，我们发现!ioctldecode Windbg扩展可能对这一过程非常有帮助。当我们编写与目标驱动程序接口的应用程序时，这些细节将尤为重要。在反汇编程序中，它们仍然会以十六进制表示。

### <a class="reference-link" name="2.4%20%E7%BB%84%E5%90%88"></a>2.4 组合

我知道，上述的过程可能太过复杂。但是，我们可以对其进行简化，并类比于发送网络数据包的过程来对其进行分析。我们可以使用所需的任何细节来构造数据包，然后将其发送到服务器进行处理，使用该数据包执行某些操作。而对于服务器端，要不然会忽略我们的数据包，要不然会返回一些结果。接下来，我们对IOCTL的发送和处理方式进行简化并说明：

[![](https://p3.ssl.qhimg.com/t01b50bc1808895fd67.png)](https://p3.ssl.qhimg.com/t01b50bc1808895fd67.png)

1、用户模式应用程序获取符号链接上的句柄。

2、用户模式应用程序使用`DeviceIoControl()`将所需的IOCTL和输入/输出缓冲区发送到符号链接。

3、符号链接指向驱动程序的设备对象，并允许驱动程序接收用户模式应用程序的数据包（IRP）。

4、驱动程序看到该数据包来自DeviceIoControl()，因此将其传递给已定义的内部函数`MyCtlFunction()`。

5、`MyCtlFunction()`将函数代码0x800映射到内部函数`SomeFunction()`。

6、`SomeFunction()`执行。

7、IRP已经完成，其状态以及驱动程序在用户模式应用程序中提供的输出缓冲区中包含的为用户提供的所有内容都将传回给用户。<br>
注意：在这里我们并不是说IRP已经完成，但需要关注的是，一旦`SomeFunction()`执行，上述时间就可以发生，并且将得到函数返回的状态代码，这表明操作的结束。



## 三、驱动程序反编译

现在，我们已经对需要探寻的关键结构有了一定了解，是时候开始深入研究目标驱动程序了。我们会清晰展现出如何在Ghidra中执行此操作，IDA中的方法与之完全相同。

一旦我们将要定位的驱动程序下载到我们的分析环境中，就应该开始寻找IRP Handler，该处理程序会使我们明确潜在的关键函数。

### <a class="reference-link" name="3.1%20%E8%AE%BE%E7%BD%AE"></a>3.1 设置

由于Ghidra中并没有包含太多分析驱动程序所需的符号，所以我们需要找到一种方法，以某种方式将其进行导入。幸运的是，感谢0x6d696368（Mich）此前所做的研究工作，帮助我们简化了这一过程。

Ghidra支持Ghidra数据类型存档（GDT）格式的数据类型，这些数据类型是打包的二进制文件，其中包含从所选标头衍生出的符号，这些符号可能是自定义的，也可能是微软提供的。有关这些文件的文档并不多，并且确实需要进行一些手工修改，但幸运的是，Mich已经完成了这部分工作。

我们在他的GitHub项目中找到了针对Ntddk.h和Wdm.h的预编译GDT，即ntddk_64.gdt。我们需要在运行Ghidra的系统上下载该文件。

要导入并开始使用GDT文件，我们需要打开要分析的驱动程序，单击“Data Type Manager”的下拉箭头，然后选择“Open File Archive”。

[![](https://p4.ssl.qhimg.com/t01476d0df10053ce20.png)](https://p4.ssl.qhimg.com/t01476d0df10053ce20.png)

然后，选择先前下载的ntddk_64.gdt文件并打开。

[![](https://p0.ssl.qhimg.com/t013f06b93223ffc783.png)](https://p0.ssl.qhimg.com/t013f06b93223ffc783.png)

在“Data Type Manager”窗口中，目前有一个新的条目“ntddk_64”。右键单击该条目，然后选择“Apply Function Data Types”，随后将会更新反编译器，并且可以看到许多函数签名的变化。

[![](https://p3.ssl.qhimg.com/t01ff3deea85dd3421e.png)](https://p3.ssl.qhimg.com/t01ff3deea85dd3421e.png)

### <a class="reference-link" name="3.2%20%E6%9F%A5%E6%89%BEDriverEntry"></a>3.2 查找DriverEntry

现在，我们已经对数据类型进行了排序，接下来需要确定驱动程序对象。这个过程相对简单，因为它是`DriverEntry`的第一个参数。首先，在Ghidra中打开驱动程序，并进行初始的自动分析。在“Symbol Tree”窗口下，展开“Exports”项目，就可以找到有一个名为entry的函数。

[![](https://p4.ssl.qhimg.com/t01043224a745895a19.png)](https://p4.ssl.qhimg.com/t01043224a745895a19.png)

注意：在某些情况下，可能还会有一个`GsDriverEntry`函数，看起来像是对两个未命名函数的调用。这是开发人员使用/GS编译器标志并设置栈Cookie的结果。其中的一个函数是真正的驱动程序入口，因此我们需要检查其中较长的一个函数。

### <a class="reference-link" name="3.3%20%E6%9F%A5%E6%89%BEIRP%20Handler"></a>3.3 查找IRP Handler

我们需要查找的第一个内容是驱动程序对象的一系列偏移量。这些都与`nt!_DRIVER_OBJECT`结构的属性有关。其中，我们最感兴趣的一个是MajorFunction表（+0x70）。

[![](https://p4.ssl.qhimg.com/t012bebdec6987196b8.png)](https://p4.ssl.qhimg.com/t012bebdec6987196b8.png)

使用我们新应用的符号，就变得容易很多。因为我们知道，`DriverEntry`的第一个参数是指向驱动程序对象的指针，所以我们可以在反编译器中单击该参数，然后按CTRL+L来调出数据类型选择器，搜索`PDRIVER_OBJECT`，然后单击“OK”，这样将更改参数的类型以对应其真实类型。

[![](https://p0.ssl.qhimg.com/t01d3b78ab4fb3ed53a.png)](https://p0.ssl.qhimg.com/t01d3b78ab4fb3ed53a.png)

注意：我希望将参数名称更改为`DriverObject`，以在执行该函数时为我提供一些帮助。要执行此操作，需要单击参数，然后按“L”，然后输入要使用的名称。

现在，我们就有了适当的类型，是时候开始寻找`MajorFunction`表的偏移量了。有时候，我们可能会在`DriverEntry`函数中看到这个权限，但有时可以看到驱动程序对象作为参数传递给另一个内部函数。

接下来，我们查找`DriverObject`变量的出现。使用鼠标可以轻松完成查找工作，只需要在变量上单击鼠标滚轮，反编译器中就可以突出显示该变量的所有实例。在我们使用的示例中，没有看到对驱动程序对象的偏移量的引用，但发现它被传递到另一个函数。

[![](https://p3.ssl.qhimg.com/t0128e07bd47d6c7b91.png)](https://p3.ssl.qhimg.com/t0128e07bd47d6c7b91.png)

我们跳到`FUN_00011060`这个函数，然后将第一个参数重新输入到`PDRIVER_OBJECT`中，因为我们知道`DriverEntry`将其作为唯一参数显示。

[![](https://p2.ssl.qhimg.com/t011ca57dcf8b3a88dc.png)](https://p2.ssl.qhimg.com/t011ca57dcf8b3a88dc.png)

然后，再次开始从`DriverObject`变量中搜索对偏移量的引用。我们正在寻找的是：

[![](https://p5.ssl.qhimg.com/t011467449a7595d089.png)](https://p5.ssl.qhimg.com/t011467449a7595d089.png)

在vanilla Ghidra中，我们将这些视图视为`DriverObject`的详细偏移量，但由于我们已经应用了NTDDK数据类型，因此现在它变得更为整洁。现在，我们已经找到了标记了`MajorFunction`表的`DriverObject`偏移量，索引的位置是(0, 2, 0xe)？这些偏移量都是在WDM标头（wdm.h）中定义，代表IRP主要函数代码。

[![](https://p3.ssl.qhimg.com/t01de38e1bd53487694.png)](https://p3.ssl.qhimg.com/t01de38e1bd53487694.png)

在我们的示例中，驱动程序处理3个主要函数代码————`IRP_MJ_CREATE`、`IRP_MJ_CLOSE`和`IRP_MJ_DEVICE_CONTROL`。其中，前两个我们并不关注，但第三个`IRP_MJ_DEVICE_CONTROL`非常关键，因为在该偏移量（0x104bc）处定义的函数使用了`DeviceIoControl`及其包含的I/O控制代码（IOCTL）来处理从用户模式发出的请求。

接下来，让我们深入研究该函数。我们查看`MajorFunction[0xe]`的偏移量，将会看到驱动程序中偏移量为0x104bc的函数。该函数的第二个参数以及所有设备I/O控制IRP Handler是指向IRP的指针。我们可以再次使用CTLR+L，将第二个参数重新命名为PIRP（或者其他自定义名称）。

[![](https://p1.ssl.qhimg.com/t01eb5a337afe680a31.png)](https://p1.ssl.qhimg.com/t01eb5a337afe680a31.png)

IRP结构非常复杂，即使有了我们新的类型定义，也无法弄清楚所有内容。在其中，我们首先要寻找的是IOCTL。这部分在反编译器中将以DWORD来表示，但我们需要知道它们将分配给哪个变量。为了弄明白这一点，我们要依靠我们的老朋友————WinDbg。

我们可以看到，IRP的第一个偏移量是`IRP-&gt;Tail + 0x40`。

[![](https://p5.ssl.qhimg.com/t01be67c4cda7416903.png)](https://p5.ssl.qhimg.com/t01be67c4cda7416903.png)

接下来，我们深入研究一下IRP结构。

[![](https://p3.ssl.qhimg.com/t015395276f4397a27e.png)](https://p3.ssl.qhimg.com/t015395276f4397a27e.png)

我们可以看到Tail是从偏移量+0x78开始，但是0x40字节又是什么呢？借助WinDbg，我们可以看到`CurrentStackLocation`是位于`Irp-&gt;Tail`偏移量+0x40的位置，但仅仅显示为一个指针。

[![](https://p5.ssl.qhimg.com/t0181bbf30d605fb002.png)](https://p5.ssl.qhimg.com/t0181bbf30d605fb002.png)

微软似乎暗示，这是指向`_IO_STACK_LOCATION`结构的指针。因此，在反编译器中，我们可以将lVar2重命名为CurrentStackLocation。

[![](https://p1.ssl.qhimg.com/t01b29f03ac7a56f9a4.png)](https://p1.ssl.qhimg.com/t01b29f03ac7a56f9a4.png)

在这个新变量之后，我们希望找到对偏移量+0x18（即IOCTL）的引用。

[![](https://p1.ssl.qhimg.com/t019b5121c18b5c9b52.png)](https://p1.ssl.qhimg.com/t019b5121c18b5c9b52.png)

如果希望，还可以将该变量重命名为便于识别的名称。

[![](https://p2.ssl.qhimg.com/t01bfcabaaf0c255422.png)](https://p2.ssl.qhimg.com/t01bfcabaaf0c255422.png)

现在，我们已经找到了包含IOCTL的变量，我们看到，它与一系列DWORD进行了比较。

[![](https://p3.ssl.qhimg.com/t0103f49b7ababef82e.png)](https://p3.ssl.qhimg.com/t0103f49b7ababef82e.png)

这些比较是驱动程序检查这些IOCTL是否属于其可以处理的范围。在每次比较之后，可能会发生内部函数调用。当特定的IOCTL从用户模式发送到驱动程序时，将会执行这些操作。在上面的示例中，驱动程序收到IOCTL 0x8000204c时，将执行`FUN_0000944c`（某些类型的打印函数）和`FUN_000100d0`。

### <a class="reference-link" name="3.4%20%E5%B0%8F%E7%BB%93"></a>3.4 小结

上面的信息量有点大，但实际上非常简单。我们将其总结为以下的工作流程：

1、跟随`DriverEntry`的第一个参数，即驱动程序对象，直至找到指示`MajorFunction`表的偏移量。

2、在`MajorFunction[0xe]`处查找偏移量，标记DeviceIoControl IRP Handler。

3、跟随这个函数的第二个参数PIRP，直至找到`PIRP-&gt;Tail +0x40`，将其标记为CurrentStackLocation。<br>
4、从`CurrentStackLocation`查找偏移量+0x18，这就是我们想寻找的IOCTL。

在很多情况下，我们会跳过第3步和第4步，并借助反编译器进行一连串的DWORD比较。如果为了方便，我们往往会寻找对`IofCompleteRequest`的调用，然后从调用向上滚动，以查找DWORD比较。



## 四、函数逆向

既然我们已经知道驱动程序收到IOCTL时哪些函数会在内部执行，我们就可以开始逆向这些函数，以找到有趣的功能。由于各个驱动程序之间的差异很大，因此我们的分析中就没有包含这部分内容。

在这里，我的常用思路是，在这些函数中查找有趣的API调用，确定输入所需的内容，然后使用简单的用户模式客户端（根据目标来复制并修改的通用模板）来发送IRP。在分析EDR驱动程序时，我还希望了解它们具体的功能，例如进程对象处理程序回调。在此过程中，我找到了一些不错的驱动程序漏洞，可以激发出我们的一些灵感。

需要注意的一件重要事情，特别是在使用Ghidra时，需要注意这个变量声明：

[![](https://p5.ssl.qhimg.com/t014407b1a29f78c557.png)](https://p5.ssl.qhimg.com/t014407b1a29f78c557.png)

如果我们在WinDbg中查看此内容，我们可以发现，在这个偏移量的位置是指向`MasterIrp`的指针。

[![](https://p3.ssl.qhimg.com/t0144d12b76935e0e5a.png)](https://p3.ssl.qhimg.com/t0144d12b76935e0e5a.png)

实际上，我们看到的是与`IRP-&gt;SystemBuffer`的并集，该变量实际上是`METHOD_BUFFERED`数据结构。这也就是为什么我们经常会看到它作为参数传递给内部函数的原因。在对内部函数进行逆向的过程中，请确保将其视为输入/输出缓冲区。<br>
祝大家好运，狩猎愉快！
