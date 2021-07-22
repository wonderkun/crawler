> 原文链接: https://www.anquanke.com//post/id/86369 


# 【技术分享】如何代码实现给fastboot发消息? 逆向aftool工具纪实


                                阅读量   
                                **161900**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01a632b1c8230acb3c.jpg)](https://p5.ssl.qhimg.com/t01a632b1c8230acb3c.jpg)

作者：[Yan_1_20](http://bobao.360.cn/member/contribute?uid=2785437033)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**0x00 起因**



学习android安全的朋友都应该熟悉adb,fastboot这两个工具，但是其实现方式网上却没有多少资料，在下对这些知识也非好奇,一次机会对某手机的售后刷机工具aftool进行对手机刷机时，发现了它的软件包里没有fastboot.exe,但是却执行了fastboot命令，猜测他可能自己实现了fastboot.exe的功能，就想对其进行逆向分析执行fastboot的命令的核心代码。



**0x01 调试环境配置**

工具：IDA ,Ollydbg,Wireshark,Source Insight3    

Aftool download link：

[http://pan.baidu.com/s/1c0AVz9I](http://pan.baidu.com/s/1c0AVz9I)

Adb source code download link:

[http://pan.baidu.com/s/1hrVZFxU](http://pan.baidu.com/s/1hrVZFxU)

安装AF_UPGRADE_PKG.exe后,aftool.exe为目标文件

 

**0x02 fastboot.exe 和fastboot 模式通信的数据包**



我们手机进入fastboot， 使用wireshark 抓取usb数据包，观察数据包数量以及格式

进入fastboot的方法:

[1](命令)使用 adb reboot-bootloader

[2](按键)音量减键+电源键

[![](https://p2.ssl.qhimg.com/t019827f61da9dd6590.png)](https://p2.ssl.qhimg.com/t019827f61da9dd6590.png)

使用wireshark 捕获usb包

选择接口  android Bootloader interface

[![](https://p1.ssl.qhimg.com/t0195f91faa1f4e58d4.png)](https://p1.ssl.qhimg.com/t0195f91faa1f4e58d4.png)

使用fastboot.exe 发送命令 fastboot reboot-bootloader

[![](https://p4.ssl.qhimg.com/t01fbe688295a81c7a4.png)](https://p4.ssl.qhimg.com/t01fbe688295a81c7a4.png)

同时wireshark捕获到的数据包为:

[![](https://p2.ssl.qhimg.com/t01e5bd59aeff987503.png)](https://p2.ssl.qhimg.com/t01e5bd59aeff987503.png)

URB_BULK out 的数据为:

[![](https://p3.ssl.qhimg.com/t0108f4cc4343694bf0.png)](https://p3.ssl.qhimg.com/t0108f4cc4343694bf0.png)

URB_BULK  in 的数据为:

[![](https://p5.ssl.qhimg.com/t01cc547290ee75c6ae.png)](https://p5.ssl.qhimg.com/t01cc547290ee75c6ae.png)

可以大胆猜测  URB_BULK out 就是我们使用的fastboot的命令 fastboot reboot-bootloaderURB_BULK int 就是手机端给的回应

但是上面三个特殊的数据包  和我们发的数据没有任何关系,但是看其名称”Request,Response,Status”猜测可能是fastboot的通信协议的 建立协议的数据包

 

**0x03 aftool.exe 和fastboot 模式通信的数据包**

Aftool的使用方法:

[1]切换成高通手机

[2]点击选择按钮 加X520_recovery目录下的fastboot_flash_all.bat

[3]点击下载按钮 开始执行fastboot_flash_all.bat里面的命令

对wireshark的处理方式和上面类型

捕获的数据包如下图

[![](https://p4.ssl.qhimg.com/t018fdc0c40438d71f8.png)](https://p4.ssl.qhimg.com/t018fdc0c40438d71f8.png)

看来和fastboot的数据包格式一致，只是多发送了一条命令

现在的思路就是 Ollydbg 调试aftool ,假如执行了某个函数同时wireshark上有数据包产生那么这个函数就是通信使用的函数

 

**0x04 逆向aftool.exe**



这个工具是使用Qt编写,没有加壳子,没有加混淆，对我这种小白来说，最大的难题可能就是怎么在Qt的架构里找到”下载”按钮的处理函数了。 

一开始我是没有思路的，由于不知道这个下载按钮里进行了操作，我给它下断点都不知道用什么函数下什么断点。但是想到了旁边还有一个”选择”按钮，加载bat文件肯定有文件读取的操作 于是对ReadFile 下了断点。果然断了下，然后通过回溯。找到了它的UI消息处理函数sub_4E22C0。

最后确定了sub_4E22C0 中调用的sub_4BFD30就是”下载”按钮响应事件，

在sub_4BFD30里分支比较多 但是ollydbg跟了几次之后 发现其执行的分支稳定执行

sub_4BBAF0

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010da2f003a965e62d.png)

但是sub_4BBAF0的代码逻辑看起来很简单并没有多少值得注意的代码，但是在OD里跟着sub_4BBAF0 按F9就会跑起来，看来是这个函数没错，但是应该是错过了什么

在sub_4BBAF0里的下层函数sub_4B7DB0，以及sub_4B7DB0的下层函数sub_4A3F30找到了如下代码

[![](https://p4.ssl.qhimg.com/t011ad54d44dd26547e.png)](https://p4.ssl.qhimg.com/t011ad54d44dd26547e.png)

可以的它开了一个线程

但是参考Qt  QThread::start()的用法 这里传入的参数可能是ida的没有使用类的方式调用吧

直接用ollydbg动态调到他这里来。得到了v2[18]的值742D345e(742D345e不是定值)

接着有两个函数需要F7



```
742D34C2    E8 51FFFFFF     call msvcr90.742D3418
742D3430    FF50 54         call dword ptr ds:[eax+0x54]
```

恭喜最后来到了



```
004A411A   .  E8 914B0000   call AFTool.004A8CB0
```

sub_4A8CB0就是真正处理函数 

接着在ollydbg IDA里跟了跟这个函数观察 



```
//reboot-bootloader
004A908C  |.  E8 3F190000   call AFTool.004AA9D0
```

发现AFTool.004AA9D0 这个函数就是给手机发数据的函数

004AA9D0 里最重要的就是下面的函数



```
004AAA58  |.  52            |push edx
004AAA59  |.  8B5424 34     |mov edx,dword ptr ss:[esp+0x34]         ;  AFTool.0052D4B8
004AAA5D  |.  8D4C24 18     |lea ecx,dword ptr ss:[esp+0x18]
004AAA61  |.  51            |push ecx
004AAA62  |.  50            |push eax
004AAA63  |.  8B42 08       |mov eax,dword ptr ds:[edx+0x8]
004AAA66  |.  55            |push ebp
004AAA67  |.  50            |push eax
004AAA68  |.  FF15 1CC05000 |call dword ptr ds:[&lt;&amp;AdbWinApi.AdbWrite&gt;;  AdbWinAp.AdbWriteEndpointSync
```

堆栈如图：



```
esp-&gt;  09A2F978   00000008
       09A2F97C   09A2FD1C  ASCII "reboot-bootloader"
       09A2F980   00000011
       09A2F984   09A2F9A0
       09A2F988   0000027C
```

&lt;注意:这个函数执行之前Wireshark里已经有了那三条特殊的数据包了，这个函数执行之后Wireshark会增加 URB_BULK out  &gt; 

所以发送命令API函数就是 AdbWinAPi.dll里的导出函数 AdbWriteEndpointSync

类似的找到了发出别的4条数据包的具体函数(其实三条特殊数据包的是一个函数发的)



```
AdbGetSerialNumber            ------&gt;GET DESCRIPTOR Request STRING
------&gt;GET DESCRIPTOR Response STRING
------&gt;GET DESCRIPTOR Status
 
AdbReadEndpointSync           ------&gt;URB_BULK in
```



**0x05 API调用分析**

现在找到了API接下来就是参考源码对这些API传入正确参数并调用了。

我们一开始假设的是前三条数据包是建立协议链接 类似socket编程accept函数返回的sock

然后AdbWriteEndpointSync 类似 send函数 使用这个sock进行通信

在源码里找了AdbWriteEndpointSync 声明(使用dll里的导出函数)，调用

声明：

[![](https://p2.ssl.qhimg.com/t016e8bb1c4eaca847b.png)](https://p2.ssl.qhimg.com/t016e8bb1c4eaca847b.png)

调用：

[![](https://p3.ssl.qhimg.com/t01d82539ec291f1be1.png)](https://p3.ssl.qhimg.com/t01d82539ec291f1be1.png)

在usb_write 下面就是 usb_read的定义

[![](https://p0.ssl.qhimg.com/t01f871c982e2c2c5d7.png)](https://p0.ssl.qhimg.com/t01f871c982e2c2c5d7.png)

通过上面的代码可以看出AdbWriteEndpointSync,AdbReadEndpointSync使用的第一个参数都是同一个结构体里的不同成员变量

这个结构体的声明如下

[![](https://p5.ssl.qhimg.com/t01cb24cfb00d052d61.png)](https://p5.ssl.qhimg.com/t01cb24cfb00d052d61.png)

接着关于adb_write_pipe和adb_read_pipe变量的赋值

但是搜索无果，搜索调用函数usb_write的函数时，能搜索到，但是没有找到他的参数传递

[![](https://p4.ssl.qhimg.com/t013d657443d966a797.png)](https://p4.ssl.qhimg.com/t013d657443d966a797.png)

换了一个思路对AdbGetSerialNumber调用进行了寻找 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0158202f30059d8b25.png)

比起这个调用，上面的do_usb_open函数返回的handle则是引起了我的兴趣，其定义如下。

[![](https://p0.ssl.qhimg.com/t010f5da994beef9d9a.png)](https://p0.ssl.qhimg.com/t010f5da994beef9d9a.png)

通过其定义可以看出，do_usb_open 里完成了对结构体usb_handle的分配已经赋值。

通过do_usb_open 返回的关键性结构体，我们就可以对AdbWriteEndpointSync 进行调用。

至于do_usb_open的参数来源 则是 上面的API AdbNextInterface进行的赋值

[![](https://p0.ssl.qhimg.com/t01c7596d1001033b09.png)](https://p0.ssl.qhimg.com/t01c7596d1001033b09.png)

所以我们已经在源码里找到了我们需要的API的调用参数的来源。

 

**0x06 整合代码**



通过整合。得了如下的代码

&lt;注意:一定要把AdbWinApi.dll AdbWinUsbApi.dll放到这个项目里编译&gt;



```
// adb_test.cpp : 定义控制台应用程序的入口点。
//
 
#include "stdafx.h"
#include&lt;windows.h&gt;
#define  ADB_MUTEX_INITIALIZER    PTHREAD_MUTEX_INITIALIZER
typedef void* ADBAPIHANDLE;
 
typedef struct _AdbInterfaceInfo `{`
    /// Inteface's class id (see SP_DEVICE_INTERFACE_DATA for details)
    GUID          class_id;
 
    /// Interface flags (see SP_DEVICE_INTERFACE_DATA for details)
    unsigned long flags;
 
    /// Device name for the interface (see SP_DEVICE_INTERFACE_DETAIL_DATA
    /// for details)
    wchar_t       device_name[1];
`}` AdbInterfaceInfo;
 
 
 
struct usb_handle `{`
    /// Previous entry in the list of opened usb handles
    usb_handle *prev;
 
    /// Next entry in the list of opened usb handles
    usb_handle *next;
 
    /// Handle to USB interface
    ADBAPIHANDLE  adb_interface;
 
    /// Handle to USB read pipe (endpoint)
    ADBAPIHANDLE  adb_read_pipe;
 
    /// Handle to USB write pipe (endpoint)
    ADBAPIHANDLE  adb_write_pipe;
 
    /// Interface name
    char*         interface_name;
 
    /// Mask for determining when to use zero length packets
    unsigned zero_mask;
`}`;
 
typedef enum _AdbOpenAccessType `{`
    /// Opens for read and write access.
    AdbOpenAccessTypeReadWrite,
 
    /// Opens for read only access.
    AdbOpenAccessTypeRead,
 
    /// Opens for write only access.
    AdbOpenAccessTypeWrite,
 
    /// Opens for querying information.
    AdbOpenAccessTypeQueryInfo,
`}` AdbOpenAccessType;
 
typedef enum _AdbOpenSharingMode `{`
    /// Shares read and write.
    AdbOpenSharingModeReadWrite,
 
    /// Shares only read.
    AdbOpenSharingModeRead,
 
    /// Shares only write.
    AdbOpenSharingModeWrite,
 
    /// Opens exclusive.
    AdbOpenSharingModeExclusive,
`}` AdbOpenSharingMode;
 
 
 
#define ANDROID_USB_CLASS_ID 
`{`0xf72fe0d4, 0xcbcb, 0x407d, `{`0x88, 0x14, 0x9e, 0xd6, 0x73, 0xd0, 0xdd, 0x6b`}``}`;
 
 
struct  usb_ifc_info
`{`
    unsigned __int16 dev_vendor;
    unsigned __int16 dev_product;
    unsigned __int8 dev_class;
    unsigned __int8 dev_subclass;
    unsigned __int8 dev_protocol;
    unsigned __int8 ifc_class;
    unsigned __int8 ifc_subclass;
    unsigned __int8 ifc_protocol;
    unsigned __int8 has_bulk_in;
    unsigned __int8 has_bulk_out;
    unsigned __int8 writable;
    char serial_number[256];
    char device_path[256];
`}`;
 
typedef struct _USB_DEVICE_DESCRIPTOR `{`
    UCHAR bLength;
    UCHAR bDescriptorType;
    USHORT bcdUSB;
    UCHAR bDeviceClass;
    UCHAR bDeviceSubClass;
    UCHAR bDeviceProtocol;
    UCHAR bMaxPacketSize0;
    USHORT idVendor;
    USHORT idProduct;
    USHORT bcdDevice;
    UCHAR iManufacturer;
    UCHAR iProduct;
    UCHAR iSerialNumber;
    UCHAR bNumConfigurations;
`}` USB_DEVICE_DESCRIPTOR, *PUSB_DEVICE_DESCRIPTOR;
 
 
typedef struct _USB_INTERFACE_DESCRIPTOR `{`
    UCHAR bLength;
    UCHAR bDescriptorType;
    UCHAR bInterfaceNumber;
    UCHAR bAlternateSetting;
    UCHAR bNumEndpoints;
    UCHAR bInterfaceClass;
    UCHAR bInterfaceSubClass;
    UCHAR bInterfaceProtocol;
    UCHAR iInterface;
`}` USB_INTERFACE_DESCRIPTOR, *PUSB_INTERFACE_DESCRIPTOR;
 
typedef int(*AdbWriteEndpointSync_)(ADBAPIHANDLE, char*, int, int *, int);
typedef void* (*AdbCreateInterfaceByName_)(const wchar_t*);
typedef void* (*AdbOpenDefaultBulkWriteEndpoint_)(ADBAPIHANDLE, AdbOpenAccessType, AdbOpenSharingMode);
typedef bool(*AdbNextInterface_)(ADBAPIHANDLE, AdbInterfaceInfo*, unsigned long* size);
typedef void* (*AdbEnumInterfaces_)(GUID, bool, bool, bool);
typedef ADBAPIHANDLE(*AdbOpenDefaultBulkReadEndpoint_)(ADBAPIHANDLE, AdbOpenAccessType, AdbOpenSharingMode);
 
typedef bool(*AdbGetInterfaceName_)(ADBAPIHANDLE adb_interface,
    void* buffer,
    unsigned long* buffer_char_size,
    bool ansi);
 
 
typedef bool(*AdbCloseHandle_)(ADBAPIHANDLE adb_handle);
 
typedef bool(*AdbGetUsbDeviceDescriptor_)(ADBAPIHANDLE, USB_DEVICE_DESCRIPTOR*);
 
typedef bool(*AdbGetUsbInterfaceDescriptor_)(ADBAPIHANDLE, USB_INTERFACE_DESCRIPTOR*);
 
 
typedef bool(*AdbGetSerialNumber_)(ADBAPIHANDLE, void*, unsigned long*, bool);
 
typedef bool(*AdbReadEndpointSync_) (ADBAPIHANDLE,
    void*,
    unsigned long,
    unsigned long*,
    unsigned long);
 
AdbWriteEndpointSync_ AdbWriteEndpointSync;
AdbCreateInterfaceByName_ AdbCreateInterfaceByName;
AdbOpenDefaultBulkWriteEndpoint_ AdbOpenDefaultBulkWriteEndpoint;
AdbNextInterface_ AdbNextInterface;
AdbEnumInterfaces_ AdbEnumInterfaces;
AdbOpenDefaultBulkReadEndpoint_ AdbOpenDefaultBulkReadEndpoint;
AdbGetInterfaceName_ AdbGetInterfaceName;
AdbCloseHandle_ AdbCloseHandle;
AdbGetUsbDeviceDescriptor_ AdbGetUsbDeviceDescriptor;
AdbGetUsbInterfaceDescriptor_ AdbGetUsbInterfaceDescriptor;
AdbGetSerialNumber_ AdbGetSerialNumber;
AdbReadEndpointSync_ AdbReadEndpointSync;
 
usb_handle* do_usb_open(const wchar_t* interface_name);
void usb_cleanup_handle(usb_handle* handle);
int recognized_device(usb_handle* handle);
int main()
`{`
    int d;
    char getvar[] = "getvar:product";   
    char rebootbl[] = "reboot-bootloader";
    HMODULE a = LoadLibrary(L"AdbWinApi.dll");
 
    AdbWriteEndpointSync = (AdbWriteEndpointSync_)GetProcAddress(a, "AdbWriteEndpointSync");
    AdbCreateInterfaceByName = (AdbCreateInterfaceByName_)GetProcAddress(a, "AdbCreateInterfaceByName");
    AdbOpenDefaultBulkWriteEndpoint = (AdbOpenDefaultBulkWriteEndpoint_)GetProcAddress(a, "AdbOpenDefaultBulkWriteEndpoint");
    AdbNextInterface = (AdbNextInterface_)GetProcAddress(a, "AdbNextInterface");
    AdbEnumInterfaces = (AdbEnumInterfaces_)GetProcAddress(a, "AdbEnumInterfaces");
    AdbOpenDefaultBulkReadEndpoint = (AdbOpenDefaultBulkReadEndpoint_)GetProcAddress(a, "AdbOpenDefaultBulkReadEndpoint");
    AdbGetInterfaceName = (AdbGetInterfaceName_)GetProcAddress(a, "AdbGetInterfaceName");
    AdbCloseHandle = (AdbCloseHandle_)GetProcAddress(a, "AdbCloseHandle");
 
    AdbGetUsbDeviceDescriptor = (AdbGetUsbDeviceDescriptor_)GetProcAddress(a, "AdbGetUsbDeviceDescriptor");
    AdbGetUsbInterfaceDescriptor = (AdbGetUsbInterfaceDescriptor_)GetProcAddress(a, "AdbGetUsbInterfaceDescriptor");
    AdbGetSerialNumber = (AdbGetSerialNumber_)GetProcAddress(a, "AdbGetSerialNumber");
    AdbReadEndpointSync = (AdbReadEndpointSync_)GetProcAddress(a, "AdbReadEndpointSync");
 
    usb_handle* handle = NULL;
    char entry_buffer[2048];
    char interf_name[2048];
    char read[2048];
    int ArgList;
    AdbInterfaceInfo* next_interface = (AdbInterfaceInfo*)(&amp;entry_buffer[0]);
    unsigned long entry_buffer_size = sizeof(entry_buffer);
    char* copy_name;
    static const GUID usb_class_id = ANDROID_USB_CLASS_ID;
    // Enumerate all present and active interfaces.
    ADBAPIHANDLE enum_handle =
        AdbEnumInterfaces(usb_class_id, true, true, true);
 
    while (AdbNextInterface(enum_handle, next_interface, &amp;entry_buffer_size)) `{`
 
        const wchar_t* wchar_name = next_interface-&gt;device_name;
        for (copy_name = interf_name;
        L'' != *wchar_name;
            wchar_name++, copy_name++) `{`
            *copy_name = (char)(*wchar_name);
        `}`
        *copy_name = '';
        handle = do_usb_open(next_interface-&gt;device_name);
        if (recognized_device(handle)) `{`
            printf("adding a new device %sn", interf_name);
            char serial_number[512];
            unsigned long serial_number_len = sizeof(serial_number);
            if (AdbGetSerialNumber(handle-&gt;adb_interface, serial_number, &amp;serial_number_len, true))
            `{`
            
                memset(read, 0, sizeof(read));
                AdbWriteEndpointSync(handle-&gt;adb_write_pipe, getvar, strlen(rebootbl), &amp;d, 0x26c);
 
                Sleep(3000);
 
                AdbReadEndpointSync(handle-&gt;adb_read_pipe, read, 4096, (unsigned long*)&amp;ArgList, 0x26c);
 
                read[strlen(read)]='';
                printf("%s:n",read);
 
 
                memset(read, 0, sizeof(read));
                AdbWriteEndpointSync(handle-&gt;adb_write_pipe, rebootbl, strlen(rebootbl), &amp;d, 0x26c);
 
                Sleep(3000);
 
                AdbReadEndpointSync(handle-&gt;adb_read_pipe, read, 4096, (unsigned long*)&amp;ArgList, 0x26c);
                read[strlen(read)] = '';
                printf("%s:n", read);
 
            
 
            `}`
        `}`
    `}`
    //AdbWriteEndpointSync(ret-&gt;adb_write_pipe, rebootbl, strlen(rebootbl), &amp;d, 0x26c);
    return 0;
`}`
 
 
int recognized_device(usb_handle* handle) `{`
    if (NULL == handle)
        return 0;
 
    // Check vendor and product id first
    USB_DEVICE_DESCRIPTOR device_desc;
 
    if (!AdbGetUsbDeviceDescriptor(handle-&gt;adb_interface,
        &amp;device_desc)) `{`
        return 0;
    `}`
 
    // Then check interface properties
    USB_INTERFACE_DESCRIPTOR interf_desc;
 
    if (!AdbGetUsbInterfaceDescriptor(handle-&gt;adb_interface,
        &amp;interf_desc)) `{`
        return 0;
    `}`
 
    // Must have two endpoints
    if (2 != interf_desc.bNumEndpoints) `{`
        return 0;
    `}`
 
    //if (is_adb_interface(device_desc.idVendor, device_desc.idProduct,
    //  interf_desc.bInterfaceClass, interf_desc.bInterfaceSubClass, interf_desc.bInterfaceProtocol)) `{`
 
    //  if (interf_desc.bInterfaceProtocol == 0x01) `{`
    //      AdbEndpointInformation endpoint_info;
    //      // assuming zero is a valid bulk endpoint ID
    //      if (AdbGetEndpointInformation(handle-&gt;adb_interface, 0, &amp;endpoint_info)) `{`
    //          handle-&gt;zero_mask = endpoint_info.max_packet_size - 1;
    //      `}`
    //  `}`
 
    return 1;
`}`
 
 
void usb_cleanup_handle(usb_handle* handle) `{`
    if (NULL != handle) `{`
        if (NULL != handle-&gt;interface_name)
            free(handle-&gt;interface_name);
        if (NULL != handle-&gt;adb_write_pipe)
            AdbCloseHandle(handle-&gt;adb_write_pipe);
        if (NULL != handle-&gt;adb_read_pipe)
            AdbCloseHandle(handle-&gt;adb_read_pipe);
        if (NULL != handle-&gt;adb_interface)
            AdbCloseHandle(handle-&gt;adb_interface);
 
        handle-&gt;interface_name = NULL;
        handle-&gt;adb_write_pipe = NULL;
        handle-&gt;adb_read_pipe = NULL;
        handle-&gt;adb_interface = NULL;
    `}`
`}`
 
usb_handle* do_usb_open(const wchar_t* interface_name) `{`
    // Allocate our handle
    usb_handle* ret = (usb_handle*)malloc(sizeof(usb_handle));
    if (NULL == ret)
        return NULL;
 
    // Set linkers back to the handle
    ret-&gt;next = ret;
    ret-&gt;prev = ret;
 
    // Create interface.
    ret-&gt;adb_interface = AdbCreateInterfaceByName(interface_name);
 
    //if (NULL == ret-&gt;adb_interface) `{`
    //  free(ret);
    //  errno = GetLastError();
    //  return NULL;
    //`}`
 
    // Open read pipe (endpoint)
 
 
 
    ret-&gt;adb_read_pipe =
        AdbOpenDefaultBulkReadEndpoint(ret-&gt;adb_interface,
            AdbOpenAccessTypeReadWrite,
            AdbOpenSharingModeReadWrite);
 
    // Open write pipe (endpoint)
    ret-&gt;adb_write_pipe =
        AdbOpenDefaultBulkWriteEndpoint(ret-&gt;adb_interface,
            AdbOpenAccessTypeReadWrite,
            AdbOpenSharingModeReadWrite);
 
    // Save interface name
    unsigned long name_len = 0;
 
    // First get expected name length
    AdbGetInterfaceName(ret-&gt;adb_interface,
        NULL,
        &amp;name_len,
        true);
    if (0 != name_len) `{`
        ret-&gt;interface_name = (char*)malloc(name_len);
 
        if (NULL != ret-&gt;interface_name) `{`
            // Now save the name
            if (AdbGetInterfaceName(ret-&gt;adb_interface,
                ret-&gt;interface_name,
                &amp;name_len,
                true)) `{`
                // We're done at this point
                return ret;
            `}`
        `}`
        else `{`
            SetLastError(ERROR_OUTOFMEMORY);
        `}`
    `}`
 
 
 
    // Something went wrong.
    int saved_errno = GetLastError();
    usb_cleanup_handle(ret);
    free(ret);
    SetLastError(saved_errno);
 
    return NULL;
`}`
```



**0x07 代码运行结果**

[![](https://p3.ssl.qhimg.com/t01879b9fc0fc7aa39e.png)](https://p3.ssl.qhimg.com/t01879b9fc0fc7aa39e.png)

其中 OKAYMSM8916是其CUP型号，为fastboot命令 getvar product的返回，OKAY是reboot-bootloader的返回，并且手机重启进入fastboot模式。说明得到的代码是完全能执行命令的核心API。

 
