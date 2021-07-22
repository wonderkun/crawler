> 原文链接: https://www.anquanke.com//post/id/237096 


# Win10下一个有意思的驱动引起可能性的拒绝服务攻击


                                阅读量   
                                **81132**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01c6971b8ac1959a0b.jpg)](https://p4.ssl.qhimg.com/t01c6971b8ac1959a0b.jpg)



在一次排查系统的驱动的目录system32/driver目录文件时，看到一个名字为ProcLaunchMon.sys的驱动

数字签名微软官方的

[![](https://p5.ssl.qhimg.com/t01b97217863bddeb6b.png)](https://p5.ssl.qhimg.com/t01b97217863bddeb6b.png)

[![](https://p2.ssl.qhimg.com/t01f067a93453a5acef.png)](https://p2.ssl.qhimg.com/t01f067a93453a5acef.png)

该驱动带入的时间是2019‎年‎12‎月‎7‎日，‏‎17:08:33，文件描述是Time Travel Debugging Process Launch Monitor大致明白了就是一个调试工具实事记录进程活动的驱动。微软的这个官方页面有讲述了什么是Time Travel Debugging，<br>[https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/time-travel-debugging-overview](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/time-travel-debugging-overview)

本篇的文章的目的是主要研究这个驱动到底做了什么？<br>
接下来就祭出逆向工具ida<br>
微软对这个模块是有部分符号文件的，左侧的Function windows可以看到他是用c++写的驱动有一些类名显示

[![](https://p1.ssl.qhimg.com/t013852d91cf05475ab.png)](https://p1.ssl.qhimg.com/t013852d91cf05475ab.png)

主要的类名就是ProcessLaunchMonitorClient 、ProcessLaunchMonitorDevice、LegacyDevice<br>
然后再看看导入表有哪些函数，函数并不多主要就两类： 进程函数和事件函数<br>
PsSetCreateProcessNotifyRoutine<br>
ZwCreateEvent<br>
PsSuspendProcess<br>
PsResumeProcess<br>
ZwDuplicateObject<br>
等等

[![](https://p0.ssl.qhimg.com/t0123648e4ed8afdcb8.png)](https://p0.ssl.qhimg.com/t0123648e4ed8afdcb8.png)

[![](https://p0.ssl.qhimg.com/t012cffd92f15c9d1f2.png)](https://p0.ssl.qhimg.com/t012cffd92f15c9d1f2.png)

分析完表面这些明显的地方，下面就从驱动的入口点分析<br>
最开始的时候会构建一个device 类 **LegacyDevice::LegacyDevice**

[![](https://p4.ssl.qhimg.com/t01f1602bc23ede6695.png)](https://p4.ssl.qhimg.com/t01f1602bc23ede6695.png)

**LegacyDevice::LegacyDevice**类的大小是0x38，因为驱动，所以一般用c++写驱动的时候都会用动态内存分配全局结构，**ProcessLaunchMonitorDevice::`vftable** 是该类的基类，在驱动的虚表rdata节里可以看到该基类的定义

[![](https://p1.ssl.qhimg.com/t01f0793031edd26e86.png)](https://p1.ssl.qhimg.com/t01f0793031edd26e86.png)

[![](https://p0.ssl.qhimg.com/t0102b9b81369a3d4b8.png)](https://p0.ssl.qhimg.com/t0102b9b81369a3d4b8.png)

前面第一个是构造与析构函数，后面四个是IO 例程函数DispatchRoutine、DispatchCreate、DispatchClose、DispatchBufferedIoctl

内存构造结束了，就直接调用LegacyDevice::LegacyDevice的构造函数

[![](https://p0.ssl.qhimg.com/t01c09501394ac0f400.png)](https://p0.ssl.qhimg.com/t01c09501394ac0f400.png)

首先会构造设备名字的字符串

[![](https://p4.ssl.qhimg.com/t01efce0708d73967c2.png)](https://p4.ssl.qhimg.com/t01efce0708d73967c2.png)

[![](https://p2.ssl.qhimg.com/t01ee3e7f3b4c424432.png)](https://p2.ssl.qhimg.com/t01ee3e7f3b4c424432.png)

然后创建设备和设备连接

[![](https://p1.ssl.qhimg.com/t01bce8c57fba37164b.png)](https://p1.ssl.qhimg.com/t01bce8c57fba37164b.png)

注意该驱动使用的是<br>
WdmlibIoCreateDeviceSecure来创建设备，该函数创建的设备是管理权限才能打开设备。

最后构造函数里会填充MajorFunction结构体，用StaticDispatchRoutine函数覆盖。

```
memset64(a2-&gt;MajorFunction, (unsigned __int64)LegacyDevice::StaticDispatchRoutine, 0x1Cui64);
```

[![](https://p0.ssl.qhimg.com/t01c571c141138b770d.png)](https://p0.ssl.qhimg.com/t01c571c141138b770d.png)

自此这个构造类结束。

构造了这个全局类LegacyDevice::LegacyDevice，后接下来就是调用注册进程回调通知

[![](https://p5.ssl.qhimg.com/t0106c0469dd6b1b6bc.png)](https://p5.ssl.qhimg.com/t0106c0469dd6b1b6bc.png)

回调函数是ProcessCreationNotifyRoutine

到这里入口函数就结束，其实过程很简单，但是精华却在例程函数里。

要控制利用驱动，首先我们必须CreateFile一个驱动，这是会进入驱动的IRP_MJ_CREATE例程，接下来看上面的提到的StaticDispatchRoutine函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019765dec56650b024.png)

这个函数很简单，可能很多人一下子看不懂，从设备信息中获得DeviceExtension结构然后call v4 + 8的函数，这到底是什么呢，<br>
秘密在刚才那个构造函数里。<br>
在之前的LegacyDevice::LegacyDevice的构造函数里有这么句代码

```
(_QWORD )(*DeviceObject)-&gt;DeviceExtension = this;
```

[![](https://p0.ssl.qhimg.com/t011bcea12d342e3fcf.png)](https://p0.ssl.qhimg.com/t011bcea12d342e3fcf.png)

就是把LegacyDevice::LegacyDevice这个全局类的this指针赋值给DeviceObject)-&gt;DeviceExtension的结构中，现在明白了这个DeviceExtension里的值是什么了把，对他就是LegacyDevice::LegacyDevice的地址值，那么

```
((void (fastcall **)(int64, _QWORD ))((_QWORD )v4 + 8i64))(v4, v7);
```

的代码的意思就是调用LegacyDevice::LegacyDevice的基类的第二个函数DispatchRoutine

[![](https://p1.ssl.qhimg.com/t0190aaf302d5e0099a.png)](https://p1.ssl.qhimg.com/t0190aaf302d5e0099a.png)

继续分析进入DispatchRoutine 函数

[![](https://p1.ssl.qhimg.com/t014009811ec7e02f4a.png)](https://p1.ssl.qhimg.com/t014009811ec7e02f4a.png)

IRP_MJ_CREATE 会进入第一个函数

```
ProcessLaunchMonitorDevice::DispatchCreate(this, ((struct _FILE_OBJECT *)iocode + 6));
```

[![](https://p4.ssl.qhimg.com/t01a3881684db32efb9.png)](https://p4.ssl.qhimg.com/t01a3881684db32efb9.png)

ProcessLaunchMonitorDevice::DispatchCreate函数里会为每一个Client创建该设备的对象生成一个ProcessLaunchMonitorClient::ProcessLaunchMonitorClient(v6, v7, &amp;v15)，该类的内存大小为0x70.

[![](https://p4.ssl.qhimg.com/t011ae1afd9b1a631b2.png)](https://p4.ssl.qhimg.com/t011ae1afd9b1a631b2.png)

这个类的构造函数一个最主要的功能就是生成一个进程间通讯的Event，赋值给了<br>
v3 = (PVOID **)((char **)this + 56);的便宜的位置。<br>
最后会把这个Process<br>
赋值给了

[![](https://p0.ssl.qhimg.com/t01c3e1e286215f25ad.png)](https://p0.ssl.qhimg.com/t01c3e1e286215f25ad.png)

[![](https://p1.ssl.qhimg.com/t018e3ccd587726ed5f.png)](https://p1.ssl.qhimg.com/t018e3ccd587726ed5f.png)

ProcessLaunchMonitorDevice这个全局类的v10 = **((_QWORD **)this + 6);的位置的LIST_ENTRY的链表里。以及当前设备的文件对象的FsContext的上下文里。

打开了设备之后，我们就要通过IRP_MJ_DEVICE_CONTROL IO控制码是14的之类的去给驱动发IO命令，那么就会经过驱动的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e8d84dd4c9206b98.png)

然后再进入ProcessLaunchMonitorDevice::DispatchBufferedIoctl函数

[![](https://p5.ssl.qhimg.com/t01a2ab2ce718d56994.png)](https://p5.ssl.qhimg.com/t01a2ab2ce718d56994.png)

首先该函数会先从之前的我们讲的文件对象的FsContext结构中取出之前创建的ProcessLaunchMonitorClient的指针。

接下来会看到里面有一个IO code

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010acfb28d28223cf6.png)

Case : 0x224040 恢复进程<br>
Case 0x224044 关闭 ProcessLaunchMonitorClient 并且清楚恢复所有被悬挂的进程<br>
Case 0x2240048 获取之前ProcessLaunchMonitorClient里创建的进程间通讯的事件。<br>
等等

这些主要的IRP例程的函数大致的逻辑就分析完毕，那该驱动的进程回调函数有什么用呢？这个问题很好，下面就来分析回调通知里的逻辑

当一个进程启动后就会进入该驱动回调通知

[![](https://p4.ssl.qhimg.com/t01e379951942704e80.png)](https://p4.ssl.qhimg.com/t01e379951942704e80.png)

然后就会进入

```
ProcessLaunchMonitorDevice::HandleProcessCreatedOrDestroyed(gLegacyDevice::gLegacyDevice, Create != 0, v4, v6);
```

这个函数是主要的处理逻辑<br>
然后就会进入

[![](https://p0.ssl.qhimg.com/t012f704a7d3ef7202e.png)](https://p0.ssl.qhimg.com/t012f704a7d3ef7202e.png)

进入这个函数SuspendResumeProcessById(a4, v13)后就会把进程悬挂起来

[![](https://p3.ssl.qhimg.com/t0145893b729236aff0.png)](https://p3.ssl.qhimg.com/t0145893b729236aff0.png)

可以看到

```
If（a2）
`{`
v5 = PsSuspendProcess(Object);
`}`
```

如果a2这个参数是1的话，直接就悬挂了，然后外面给的参数就是1，那就是只要驱动功能起来了，就直接悬挂了新起来的进程(这个驱动太霸道了)， 如果你不发之前我们看到那个IO： 0x224040的控制码的话，它就一直被悬挂，起不来了，或者这个驱动被关闭也能自动恢复所有被悬挂的进程。<br>
其他一些小的附加的结构体的处理不在具体分析，以上就是该驱动的最主要的功能，当然分析完毕就是验证我们的分析结果。

主要代码如下：(具体的iocode 我模糊处理了，避免被恶意乱用)

```
int main()
`{`

TCHAR szDriverKey[MAX_PATH] = `{` 0 `}`;
GetSystemDirectory(szDriverKey,MAX_PATH);
StringCchCat(szDriverKey, MAX_PATH, _T("\\dirver\\ProcLaunchMon.sys"));

if (TRUE)
`{`
    //install driver
    LoadDriver(szDriverKey);
`}`
BOOL CheckServiceOk = FALSE;

if (SUCCEEDED(StringCchPrintf(
    szDriverKey,
    MAX_PATH,
    _T("\\\\.\\%s"),
    _T("com_microsoft_xxxxx_ProcLaunchMon")))) //


`{`
    HANDLE hObjectDrv = CreateFile(
        szDriverKey,
        GENERIC_READ |
        GENERIC_WRITE,
        0,
        0,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        0);

    if (hObjectDrv != INVALID_HANDLE_VALUE)
    `{`

        DWORD dwProcessId = -1;
        BYTE OutBuffer[4002] = `{` 0 `}`;
        ULONG BytesReturned = 0;

        DWORD sendrequest = 0xxabsdd;
        if (DeviceIoControl(
            hObjectDrv,
            sendrequest,//,
            &amp;dwProcessId,
            4,
            &amp;dwProcessId,
            4,
            &amp;BytesReturned, 0))
        `{`
            ULONG64 Request = 0;
            sendrequest = 0xa2XXXX;
            ULONG64 KeyHandle = 0;
            if (DeviceIoControl(
                hObjectDrv,
                sendrequest,//
                &amp;Request,
                8,
                &amp;KeyHandle,
                8,
                &amp;BytesReturned, 0))
            `{`
                //Get the kernel process event and wait for the kernel setting event

                if (WaitForSingleObject((HANDLE)KeyHandle, INFINITE) == WAIT_OBJECT_0)
                `{`
                    //                         int nI = 0;
                    //                         nI++;
                `}`

                while (TRUE)
                `{`
                    sendrequest = 0x125a3X;

                    typedef struct _GetPidBuffer
                    `{`
                        LARGE_INTEGER Pid;
                        ULONG32 Other;
                    `}`GetPidBuffer;
                    GetPidBuffer ProcessPid = `{`0`}`;
                    if (DeviceIoControl(
                        hObjectDrv,
                        sendrequest,
                        &amp;Request,
                        8,
                        &amp;ProcessPid,
                        12,
                        &amp;BytesReturned,
                        0))
                    `{`
                        if (BytesReturned &amp;&amp; ProcessPid.Pid.LowPart &gt; 0)
                        `{`

                            printf("curent run pid:%d", ProcessPid.Pid.HighPart);
                            //If the process is not recovered, it will cause denial of service attack. For example,
                            //if it is security software, it will cause security software failure
                            sendrequest = 0x224040;

                            if (DeviceIoControl(
                                hObjectDrv,
                                sendrequest,
                                &amp;ProcessPid.Pid.HighPart,
                                8,
                                &amp;ProcessPid.Pid.HighPart,
                                8,
                                &amp;BytesReturned, 0))
                            `{`
                            `}`
                            Sleep(100);
                            BytesReturned = 0;
                        `}`
                        else
                        `{`
                            if (WaitForSingleObject((HANDLE)KeyHandle, INFINITE) == WAIT_OBJECT_0)
                            `{`

                            `}`
                        `}`
                    `}`        
                `}`

            `}`
        `}`

        CloseHandle(hObjectDrv);
        hObjectDrv = NULL;
    `}`
`}`
return 0;
`}`
```

**1. 加载驱动成功**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017b0e5579bac8908b.png)

** 2. 打开设备成功**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0155921a0e3050c59b.png)

** 3. 开启功能**

[![](https://p4.ssl.qhimg.com/t01ec21bc495d0d2d7d.png)](https://p4.ssl.qhimg.com/t01ec21bc495d0d2d7d.png)

后记： 这个曾经上报给微软的msrc，对方承认是个有待改进的问题的驱动，但是并非是个漏洞，至今已经过去了四个月了，可以到了公布的时间了，如果一个恶意进程已经攻击进入一个系统后，，并且已经有了管理员权限，他就可以利用这个驱动去控制安全软件的启动，甚至失效，这也是很危险的驱动。
