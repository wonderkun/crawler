
# 【技术分享】从一篇文章入门Windows驱动程序（二）


                                阅读量   
                                **103523**
                            
                        |
                        
                                                                                                                                    ![](./img/85975/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85975/t014a7cdecf35613ed4.png)](./img/85975/t014a7cdecf35613ed4.png)**

****

作者：[**Kr0net**](http://bobao.360.cn/member/contribute?uid=2874666548)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**传送门**

[**【技术分享】从一篇文章入门Windows驱动程序（一）**](http://bobao.360.cn/learning/detail/3781.html)



**0x1 前言**

在文章的上一份部分：[《从一篇文章入门Windows驱动（一）》](http://bobao.360.cn/learning/detail/3781.html)笔者介绍了Windows驱动编程相关的基础知识，并对NT式的驱动编写给了详细的介绍，下面笔者开始介绍WDM。

<br>

**0x2 WDM**

WDM模型是建立在NT式驱动程序的模型之上的，从功能上来看，WDN和NT明显的区别是WDN支持即插即用（热拔插），从结构上来看，WDM一般是基于分层的驱动程序（实际上NT驱动程序也可以分层，WDM可以说是NT驱动程序的一种延伸，另外驱动程序的层次结构的内容相对较多，这里也不一一概述），也就是说它完成一个设备的操作，至少需要两个驱动设备共同来完成，一个是物理设备对象（PDO），一个是功能设备对象（FDO）。

当一个设备插入PC的时候，PDO就会自动创建，接下来一个FDO附加在PDO上，后系统会检测到新设备并提示是否要安装驱动程序（WDM）。

WDM的驱动程序的入口也和NT式驱动程序一样是DriverEntry，不同的是WDM不在DriverEntry中创建设备对象，而是放在了AddDevice例程中，这个例程是WDM所独有的。另外，DriverEntry设置了一个的对IRP_MJ_PNP（在系统产生即插即用活动时由PnP管理器发送IRP给WDM驱动程序，具体的实现内容取决于其功能代码）处理的派遣函数



```
extern "C" NTSTATUS DriverEntry (IN PDRIVER_OBJECT pDriverObject,
                    IN PUNICODE_STRING pRegistryPath) 
{
NTSTATUS status;
DbgPrint(("Wlcome to A Driver!n"));
//设置AddDevice例程
pDriverObject-&gt;DriverExtension-&gt;AddDevice = FirstDriverAddDevice;
pDriverObject-&gt;MajorFunction[IRP_MJ_CREATE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFunction[IRP_MJ_CLOSE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFun8ction[IRP_MJ_WRITE] = FirstDriverRoutine;
pDriverObject-&gt;MajorFunction[IRP_MJ_READ] = FirstDriverRoutine;
//设置IRP_MJ_PNP派遣函数
pDriverObject-&gt;MajorFunction[IRP_MI_PNP] = FirstDriverPNP;
pDriverObject-&gt;DriverUnload = FirstDriverUnload;
//创建驱动设备对象
status = DriverCreateDevice(pDriverObject);
DbgPrint(("See you Again!I'm Kr0netn"));
return status;
}
```

下面来看一下FirstDriverAddDevice



```
NTSTATUS FirstDriverAddDevice(IN PDRIVER_OBJECT DriverObject,
                         IN PDEVICE_OBJECT PhysicalDeviceObject)
{ 
PAGED_CODE();
DbgPrint(("Enter FirstDriverAddDevicen"));
NTSTATUS status;
PDEVICE_OBJECT fdo;
status = IoCreateDevice(
DriverObject,
sizeof(DEVICE_EXTENSION),
NULL,//没有指定设备名
FILE_DEVICE_UNKNOWN,
0,
FALSE,
&amp;fdo);
if( !NT_SUCCESS(status))
return status;
PDEVICE_EXTENSION pdx = (PDEVICE_EXTENSION)fdo-&gt;DeviceExtension;
pdx-&gt;fdo = fdo;
pdx-&gt;NextStackDevice = IoAttachDeviceToDeviceStack(fdo, PhysicalDeviceObject);
//创建设备接口
status = IoRegisterDeviceInterface(PhysicalDeviceObject, &amp;MY_WDM_DEVICE, NULL, &amp;pdx-&gt;interfaceName);
if( !NT_SUCCESS(status))
{
IoDeleteDevice(fdo);
return status;
}
DbgPrint(("%wZn",&amp;pdx-&gt;interfaceName));
IoSetDeviceInterfaceState(&amp;pdx-&gt;interfaceName, TRUE);
if( !NT_SUCCESS(status))
{
return status;
}
fdo-&gt;Flags |= DO_BUFFERED_IO | DO_POWER_PAGABLE;
fdo-&gt;Flags &amp;= ~DO_DEVICE_INITIALIZING;
KdPrint(("Leave FirstDriverAddDevicen"));
return STATUS_SUCCESS;
 }
```

这个例程首先和NT驱动一样，创建一个设备对象FDO。

接着调用IoAttachDeviceToDeviceStack例程（把调用者的设备对象附加到链中的最高设备对象，并返回指向先前最高设备对象的指针）将FDO附加在PDO上。当FDO附加到PDO时，PDO通过AttachDevice子域知道他上边的设备时FDO，而FDO要通过设备扩展来得知它的下方是什么设备。

```
pdx-&gt;NextStackDevice = IoAttachDeviceToDeviceStack(fdo, PhysicalDeviceObject);
```

WDM驱动程序一般不会命名设备对象，因此不应使用IoCreateSymbolicLink例程来创建符号链接。WDM驱动程序中，是通过设备接口来定位驱动程序的。WDM驱动程序调用IoRegisterDeviceInterface注册一个设备接口类（如果以前没有注册过）或者称作设备接口，并创建一个接口类的新实例（驱动程序可以为给定的设备多次调用此例程来注册几个接口类并创建类的实例）。创建成功后调用IoSetDeviceIntefaceState例程来打开或者关闭设备接口。应用程序通过Setup系列函数得到设备接口（以下对函数的解释来自MSDN）



```
HANDLE GetTheDeviceSymbolicLink(CUID *Guid, DWORD InterfaceData)
{
//获得类信息 DeviceInfo是指向设备信息集的指针，包含了所要接收信息的接口      
HDEVINFO DeviceInfo = SetupDiGetClassDevs(&amp;Guid, NULL, NULL, DIGCF_PRESENT | DIGCF_INTERFACEDEVICE);   
if(DeviceInfo ==INVALID_HANDLE_VALUE)    
{     
         printf("ERROR : %dn", GetLastError() );    
         return -1;     
     }  
   
// Get interface data for the requested instance    
SP_INTERFACE_DEVICE_DATA CatchData;   //该结构用于指定接口的信息 
catchdata.cbSize = sizeof(CatchData);     
if(!SetupDiEnumDeviceInterfaces(DevInfo, NULL, &amp;Guid, 0, &amp;InterfaceData))    
{     
    printf("ERROR : %dn", GetLastError());       
    SetupDiDestroyDeviceInfoList(DeviceInfo);     
    return 1;     
     }       
 
   // 得到符号链接名 
     DWORD ReqLen;     
     SetupDiGetDeviceInterfaceDetail(DeviceInfo , &amp;CatchData, NULL, 0, &amp;ReqLen, NULL);    
     PSP_INTERFACE_DEVICE_DETAIL_DATA CatchDataDetial= (PSP_INTERFACE_DEVICE_DETAIL_DATA)(new char[ReqLen]);     
     if( InterfaceDetail==NULL)    
   {     
      SetupDiDestroyDeviceInfoList(DeviceInfo);     
      return 1;     
 }       
  CatchDataDetial-&gt;cbSize = sizeof(SP_INTERFACE_DEVICE_DETAIL_DATA);   //cbSize成员总是包含数据结构的固定部分长度  
 if( !SetupDiGetDeviceInterfaceDetail(DevInfo, &amp;InterfaceData, CatchDataDetial, ReqLen, NULL, NULL))    
   {     
       SetupDiDestroyDeviceInfoList(DeviceInfo);     
      delete InterfaceDetail;     
     return 1;     
  }      
 printf("Symbolic link is %sn",CatchDataDetial-&gt;DevicePath);     
 
     HANDLE hDevice =   
       CreateFile(InterfaceDetail-&gt;DevicePath,  //通过符号链接名打开设备
                 GENERIC_READ | GENERIC_WRITE,  
                   FILE_SHARE_WRITE|FILE_SHARE_READ,       // share mode none  
                   NULL,   // no security  
                 OPEN_EXISTING,  
                 FILE_ATTRIBUTE_NORMAL,  
                     NULL );     // no template  
     if (hDevice == INVALID_HANDLE_VALUE)  
     {  
       printf("ERROR : %dn", GetLastError() );  
      return -1;  
     }  
    delete CatchDataDetial;
  SetupDiDestroyDeviceInfoList(info);
     return hDeice;
}
```

SetupDiEnumDeviceInterfaces 该函数枚举设备信息中的全部接口

SetupDiGetDeviceInterfaceDetail 该函数返回设备接口信息

使用这个函数来获得接口的细节，通常需要以下两个步骤：

1、获得请求的缓冲区大小

2、分配一个合适的缓冲去再次调用函数来获得接口的细节。

下面就是最核心的WDM的IRP_MJ_PNP派遣函数。IRP_MJ_PNP是这个IRP的主功能代码，不同的即插即用事件会有不同的子功能代码。IRP_MJ_PNP的派遣函数中需要针对子功能代码的不同需要做出相应的操作。（《Windows驱动开发技术详解》使用一个函数指针的办法，每次都将便利一个数组来查找对应的函数指针，笔者使用switch看起来更有条理性一些）

```
NTSTATUS FirstDevicePnP(PDRIVER_OBJECT DeviceObject, IN PIRP Irp)
{
FirstDev_Ext DevExt;
PIO_STACK_LOCATION IrpStack;
KIRQL OldIrql;
KEVENT event;
NTSTATUS status = STATUS_SUCCESS;
DevExt = (FirstDev_Ext)(DeviceObject-&gt;DriverExtension);
IrpStack = IoGetCurrentIrpStackLocation(Irp);
switch (IrpStack-&gt;MinorFunction)
{
case IRP_MN_START_DEVICE:
   ...
case IRP_MN_...:
   ...
default:
...;
}
return status;
}
```

最后是WDM程序的卸载例程.

WDM的卸载例程主要是在IRP_MN_REMOVE_DEVICE中处理，DriverUnload例程的处理就相对简单了，在MSDN对IRP_REMOVE_DEVICE的说明中得知，在Windows2000以及更高的版本的系统上，在IRP_REMOVE_DEVICE到达之前发送一个IRP_MN_SURPPRISE_REMOVAL来通知注册的应用程序和驱动程序，该设备已经删除（实际上并没有），这样来确保删除设备的时候并没有在使用这个驱动程序。

好的，至此一个简单WDM驱动的编写也到此结束。

<br>

**参考文献**

《天书夜读——从汇编语言到Windows内核编程》

《寒江独钓——Windows内核安全编程》

《Windows驱动开发技术详解》

《Windows内核情景分析——采用开源代码ReactOS》

<br>



**传送门**

**[【技术分享】从一篇文章入门Windows驱动程序（一）](http://bobao.360.cn/learning/detail/3781.html)**
