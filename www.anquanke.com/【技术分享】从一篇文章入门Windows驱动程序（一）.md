
# 【技术分享】从一篇文章入门Windows驱动程序（一）


                                阅读量   
                                **211115**
                            
                        |
                        
                                                                                                                                    ![](./img/85972/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/85972/t01e44470b18b8ac913.png)](./img/85972/t01e44470b18b8ac913.png)

作者：[**Kr0net**](http://bobao.360.cn/member/contribute?uid=2874666548)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**<font face="微软雅黑, Microsoft YaHei">传送门</font>**

[**<font face="微软雅黑, Microsoft YaHei">【技术分享】从一篇文章入门Windows驱动程序（二）</font>**](http://bobao.360.cn/learning/detail/3785.html)

<br>

**0x1 背景**

笔者在学习中发现，关于Windows驱动编程的文章多不胜数，但是其中很多文章的内容繁杂不便于了解与学习，缺少对内容精准的概括与总结，所以本篇文章将对Windows驱动编程进行一次总结性介绍。文章将分为两个部分，分别是对NT驱动和WDM驱动的介绍，同时为了读者能够更好地学习Windows驱动编程，在文章开头将先介绍在内核模式下编程的基础知识。

<br>

**0x2 相关基础**

**（内核相关）**

**a.内核模式和用户模式**

内核模式和用户模式是操作系统的两种运行级别。内核模式：操作系统的核心代码运行在特权模式下。与之相对应的，应用程序运行在非特权模式下为用户模式。

我们都知道在用户模式下，一个进程拥有windows专供的句柄表和虚拟地址空间，形象一点来说就是windows为进程提供了一个密闭的个人房间（这个房间位于低32位的内存空间里，用户空间），进程可以在房间里自行其是二不会干扰到其他的进程。在内核模式下，所有的代码都共享一个房间（位于高32位的内存空间里，内核空间），这个房间受到硬件的保护，ring0层的代码才可以访问这个内存空间，ring3层的代码想访问这个内存空间时，一般都需要操作系统提供的入口（int 0x2e、iret组合或者sysenter、sysexit组合）来让CPU进入内核。

学习这部分内容的时候，可能可能会有一个疑问，那么什么是实模式、保护模式？（笔者一开始的时候将这四种模式混淆）实际上与用户模式和内核模式不同，实模式和保护模式是另外一种概念了。实模式和保护模式是内存的两种形式，二者最大的区别是寻址范围，保护模式是32位内存寻址，可以访问4G的内存空间，实模式是20位寻址，只能访问1M的内存空间，另外保护模式保证进程间的地址空间不会冲突，也就是一个进程没有办法访问另外一个进程地址空间的数据。

**b.系统调用**

我们来看一下应用程序和内核之间的联系：

[![](./img/85972/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ac5aed8dcd93bf0f.png)

这幅图的中央是Win32子系统，子系统的概念可以理解为Windows为兼容其他操作系统的程序所服务的。而Win32子系统是最纯正的Windows子系统，它为Windwos提供了大量的API。

从图上可以看到在用户模式里，程序员通过调用NativeAPI操作Windows内核，实现系统调用。Native API 是指以二进制方式，函式库 (DLL) 直接开放的应用程式开发接口 (API,Application Programming Interface)可以直接由 C/C++ 来呼叫存取使用，一般的Native API的函数都是在Win32API上加上Nt两个字母。所有的NativeAPI都是在Ntdll.dll中实现的。下面我们通过ReadFile函数来详细说明系统调用（详细的可以参考《Windows内核情景分析——采用开源代码ReactOS》）。

在用户模式下，应用程序调用了ReadFile()函数，实际上在ReadFile()(根据ReactOS所提供的代码)内部有一个函数NTReadFile()。



```
ReadFile()
{
   ...
   Status = NTReadFile();
   ...
}
```

NTReadFile是一个系统调用（操作系统的内核所提供的可供应用程序调用的函数），NTReadFile实现在ntoskrnl.exe。其实ReadFile函数内部并不是只是单单调用了NTReadFile()，在用户空间的函数库中还有一个叫做NTReadFile的函数，这个函数内部的内容与其函数的实际的意义有所不同，大体上这个函数通过sysenter指令进入内核，并将NTReadFile的系统调用号压入堆栈，让内核调用此函数。

**（驱动相关）**

**a.驱动对象和设备对象**

首先解释一下对象的概念，虽然说Windows内核采用面向对象的编程模式，实际上这里的对象并不等同与面向对象编程里的对象，在Windows内核中，确切的来说对象实际上就是带了很多”附加信息“数据结构。

驱动对象：一个驱动对象就对应一个驱动程序，在Windows中加载这样一个结构，实际上时告诉系统需要提供哪些东西。

```
typedef struct _DRIVER_OBJECT {  
 //  结构的类型和大小。  
      CSHORT Type;  
      CSHORT Size;  
 
  /* 设备对象的指针，注意这里实际上是一个设备对象的链表的开始。
一个驱动程序可以拥有多个设备对象，并且这些对象用链表的形式连接起来。*/
      PDEVICE_OBJECT DeviceObject;  
  ……  
  //  驱动的名字  
      UNICODE_STRING DriverName;  
  ……  
  //  快速 IO分发函数  
      PFAST_IO_DISPATCH FastIoDispatch;  
   ……  
 //  驱动的卸载函数  
      PDRIVER_UNLOAD DriverUnload;  
  //  普通分发函数  
    PDRIVER_DISPATCH MajorFunction[IRP_MJ_MAXIMUM_FUNCTION + 1];  
} DRIVER_OBJECT;
```

 设备对象：这里我们可以类比为windowsGUI编程中的窗口,任何消息都发送给窗口，窗口也是唯一用来消息的东西，而设备对象也是唯一用来接收设备请求的实体。

```
typedef struct DECLSPEC_ALIGN(MEMORY_ALLOCATION_ALIGNMENT) _DEVICE_OBJECT  
{
  CSHORT Type;  
  USHORT Size;     
  //  引用计数，当引用计数为0的时候此对象被销毁  
  ULONG ReferenceCount;     
  //  这个设备所属的驱动对象  
   struct _DRIVER_OBJECT *DriverObject;  
  //  下一个设备对象。在一个驱动对象中有n 个设备，这些设备用这个指针连接  
  //  起来作为一个单向的链表。  
    struct _DEVICE_OBJECT *NextDevice;   
  //  设备类型  
  DEVICE_TYPE DeviceType;     
  // IRP栈大小  
  HAR StackSize;       
  ……  
}DEVICE_OBJECT;
```

** b.IRP：**

首先先介绍一下IO管理器，I/O管理器通过一系列内核模式下的例程发起I/O请求，并且为用户模式下的进程提供了统一的接口。IRP是一种请求的形式。

IRP（I/O Request Pcaket）。驱动与驱动之间，驱动与用户层之间都是直接或者间接通过IRP进行通讯的。IRP的结构相当复杂（限于篇幅的原因，本文章只介绍几个常用的关键成员），具体由两部分组成：头部区域和I/O堆栈（IO_STACK_LOCATIONS）。

头部区域是一个IRP结构。I/O堆栈则是一个IO_STACK_LOCATIONS的结构体数组，这个数组的大小由IoAllocateIrp创建IRP时所决定。

```
PIRP IoAllocateIrp(
  _In_ CCHAR   StackSize,  //决定IO_STACK_LOCATION的大小
  _In_ BOOLEAN ChargeQuota
);
```

通过前面介绍，我们知道驱动对象会创建一个又一个的设备对象，这些设备对象通过链表的数据结构堆叠成一个垂直的结构，这个结构被称为设备栈。IRP会被操作系统送到栈顶。然后通过设备堆栈一层一层向下转发处理，直至这次I/O请求结束。

IRP结构中有一个IoStatus成员，驱动程序在最终完成请求时设置这个结构。IoStatus中还包含了两个域：Status、Information。前者的作用会收到一个NTSTATUS，后者的信息值取决于具体的IRP类型和请求完成的状态。

<br>

**0x3 驱动编程。**

驱动程序分为两类：NT驱动程序，WDM驱动程序（支持即插即用）（在Vista之后微软推出了WDF驱动模型，它理解为是对WDM模型的一种升级，相比较与WDM,WDF模型中关于电源，PnP等相关的复杂操作都由微软实现，在《寒江独钓——Windows内核安全编程》中有对驱动程序做了很好的分类，将NT、WDM归类于传统型驱动，而使用WDF相关内核函数的驱动为WDF驱动）。

驱动程序的编程其实并不难，简单来说就是API的调用，类似于windows编程。提醒一点虽然驱动程序的编写用的也是C/C++，但是在编程中不能使用C的运行时函数（内核模式下是不能调用用户模式的API的）。对应不同的设备，驱动的编写人员可能还需要知道一些设备的协议。另外由于驱动程序是在Ring0权限下执行的，所以编程中出现的差错可能会直接影响到操作系统导致系统的崩溃（蓝屏），所以在编写Windows驱动程序的时候，需要WinDbg的联机调试，具体的方法网上有很多的教程可供参考，这里就不再赘述。

驱动程序的编写流程(以下的代码是使用《Windows驱动开发技术详解》内的改动后的代码、部分函数的说明来自MSDN)：

驱动程序和普通的win32程序一样都有一个程序的入口点（win32程序是WINMAIN），驱动程序的入口是DriverEtry，在C++编译的时候要加上extern “C”，extern "C"的用处是让C++可以和其他语言混合使用。

```
NTSTATUS DriverEntry(
   IN PDRIVER_OBJECT DriverObject,
   IN PUNICODE_STRING RegistryPath
   )
{}
```

DriverEntry主要作用是对驱动程序进行初始化工作，它是由系统进程所调用的。DriverEntry的返回值是NTSTATUS，这是一个是被定义为32位的无符号长整形。不同的值对应不同的返回状态。DriverObject是一个驱动对象的指针，RegistryPath是一个指向设备服务器键键名的字符串指针；在DriverEntry函数中，一般设置卸载例程数和IRP的派遣函数，另外还有一部分代码负责创建设备对象。设置卸载例程和设置派遣函数都是对驱动对象的的设置。

```
extern "C" NTSTATUS DriverEntry (IN PDRIVER_OBJECT pDriverObject,
                    IN PUNICODE_STRING pRegistryPath)
{
NTSTATUS status;
DbgPrint(("Wlcome to A Driver!n"));
pDriverObject-&gt;MajorFunction[IRP_MJ_CREATE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFunction[IRP_MJ_CLOSE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFun8ction[IRP_MJ_WRITE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFunction[IRP_MJ_READ] = FirstDriverRoutine;
pDriverObject-&gt;DriverUnload = FirstDriverUnload;
//创建驱动设备对象
status = DriverCreateDevice(pDriverObject);
DbgPrint(("See you Again!I'm Kr0netn"));
return status;
}
```

DriverEntry内部有一个函数DriverCreateDevice()，这是实际是一个自定义的函数，在其内部实现了相关功能，它传入驱动对象的指针。

来看DriverCreateDevice函数，实际上可以直接将这个函数的内容放在DriveEntry函数里。

```
NTSTATUS DriverCreateDevice (IN PDRIVER_OBJECTpDriverObject)
{
NTSTATUS status;
PDEVICE_OBJECT pDevObj;
PDEVICE_EXTENSION pDevExt;
//创建设备名称
UNICODE_STRING devName;
RtlInitUnicodeString(&amp;devName,L"\Device\MyFirstDevice");
//创建设备
status = IoCreateDevice( pDriverObject,
sizeof(DEVICE_EXTENSION),
&amp;(UNICODE_STRING)devName,
FILE_DEVICE_UNKNOWN,
0, TRUE,
&amp;pDevObj );
if (!NT_SUCCESS(status)
    {
       DbgPrint(("CreateDevice Unsuccess!"));
       return status;
    }
pDevObj-&gt;Flags |= DO_BUFFERED_IO;
pDevExt = (PDEVICE_EXTENSION)pDevObj-&gt;DeviceExtension;
pDevExt-&gt;pDevice = pDevObj;
pDevExt-&gt;ustrDeviceName = devName;
//创建符号链接
UNICODE_STRING symLinkName;
RtlInitUnicodeString(&amp;symLinkName,L"\??\FirstDriver");
pDevExt-&gt;ustrSymLinkName = symLinkName;
status = IoCreateSymbolicLink( &amp;symLinkName,&amp;devName );
if (!NT_SUCCESS(status))
{
IoDeleteDevice( pDevObj );
return status;
}
return STATUS_SUCCESS;
}
```

CreateDevice函数看起来还算很大，我们分开来看

首先：

创建设备名称，这里要注意的是字符串必须是“Device[设备名]”的形式。RtlnitUnicodeString()函数是对一个Unicode字符的初始化。

接下来：

IoCreateDevice()创建设备

```
NTSTATUS IoCreateDevice
(
IN PDRIVER_OBJECT DriverObject,    //一个指向调用该函数的驱动程序对象.每一个驱动程序在它的DriverEntry过程里接收一个指向它的驱动程序对象
IN ULONG DeviceExtensionSize,
IN PUNICODE_STRING DeviceNameOPTIONAL,
IN DEVICE_TYPE DeviceType,         //设备类型
IN ULONG DeviceCharacteristics,    //设备特征
IN BOOLEAN Exclusive,
OUT PDEVICE_OBJECT *DeviceObject   //一个指向DEVICE_OBJECT结构体指针的指针,这是一个指针的指针,指向的指针用来接收DEVICE_OBJECT结构体的指针
);
~：
```

我们会注意到这个函数开头所定义的一个指针pDevExt,这是一个DVICE_EXTENSION结构的指针，也就是设备扩展。

什么是设备扩展？

设备扩展主要用来维护设备状态信息、存储驱动程序使用的内核对象或系统资源（如自旋锁）、保存驱动程序需要的数据等。由于大多数的总线驱动、功能驱动和过滤 器驱动都要工作在任意线程上下文，即任意线程都可能成为当前线程，所以，设备扩展是保存设备状态信息和数据的主要空间。（实际上设备扩展就是用来保存一些设备其他的信息的，这个结构的内容根据每个驱动程序的需要，由程序员自己定义）

```
typedef struct _DEVICE_EXTENSION {
PDEVICE_OBJECT pDevice;
UNICODE_STRING ustrDeviceName;    //设备名称
UNICODE_STRING ustrSymLinkName;    //符号链接名
} DEVICE_EXTENSION, *PDEVICE_EXTENSION;
```



最后

IoCreateSysbolicLink()创建符号链接，这里可能会有疑问，之前创建了设备名为什么这里还要创建符号链接。原因是这样，设备名只能被内核模式下的其他驱动识别，用户模式下的应用程序就无法识别这个设备。符号链接的作用就是让用户空间的应用程序也能够识别。

在应用程序中使用符号链接打开设备:CreateFile()、OpenFile()的系统调用时NTCreateFile()和NTOpenFile()，为内核创建新的对象类型时上述的函数就是通用方法。应用程序在打开和关闭一个设备的时候，操作系统就会发出IRP，并将个IRP送到指定的派遣函数当中。



```
// ConsoleApplication2.cpp : 定义控制台应用程序的入口点。
//
#include&lt;windows.h&gt;
#include&lt;stdio.h&gt;
int main()
{
HANDLE hDevice = CreateFile("\\.\FistDriver",
GENERIC_READ | GENERIC_WRITE,
0,
NULL,
OPEN_EXISTING,
FILE_ATTRIBUTE_NORMAL,
NULL
);
if (hDevice == INVALID_HANDLE_VALUE)
{
printf("Failed To Open A Driver.ERROR:%d", GetLastError());
return -1;
}
CloseHandle(hDevice);
return 0;
}
```

再次回到DriverEntry函数，实际上这个函数最明显的就是这一段：



```
pDriverObject-&gt;MajorFunction[IRP_MJ_CREATE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFunction[IRP_MJ_CLOSE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFunction[IRP_MJ_WRITE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFunction[IRP_MJ_READ] = FirstDriverRoutine;
```

这一段就是对IRP派遣函数的设置，MajorFunction[]这个是一个函数指针数组，这个数组最多有0x1b个成员，相对应有27个不同派遣例程的函数，IRP_MJ_CREATE这些数组下标表示的是IRP的主功能号，用来标识IRP的功能大类。



```
#define IRP_MJ_CREATE                   0x00  
#define IRP_MJ_CLOSE                    0x02  
#define IRP_MJ_READ                     0x03  
#define IRP_MJ_WRITE                    0x04
```

为了方便理解，这里所有派遣函数都设置为FirstDriverRoutine。

```
NTSTATUS FirstDriverRoutine(IN PDEVICE_OBJECT pDevObj,IN PIRP pIrp) 
{
KdPrint(("Welcome to FirstDriverRoutinen"));
NTSTATUS status = STATUS_SUCCESS;
// 完成IRP
pIrp-&gt;IoStatus.Status = status;
pIrp-&gt;IoStatus.Information = 0;
IoCompleteRequest( pIrp, IO_NO_INCREMENT );
DbgPrint(("Leave FirstDriverRoutinen"));
return status;
}
```

FirstDriverRoutine的作用是：打印一些log，设置irp完成状态，调用IoCompleteRequest函数来完成这个IRP。

至此一个简单的驱动程序完成。

<br>



**传送门**

**[【技术分享】从一篇文章入门Windows驱动程序（二）](http://bobao.360.cn/learning/detail/3785.html)**


