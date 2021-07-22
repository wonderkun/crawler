> 原文链接: https://www.anquanke.com//post/id/222214 


# 微软轻量级系统监控工具sysmon原理与实现完全分析——ProcessGuid的生成


                                阅读量   
                                **206987**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01f85cacd3d6547ad0.jpg)](https://p3.ssl.qhimg.com/t01f85cacd3d6547ad0.jpg)



Sysmon的众多事件看起来都是独立存在的，但是它们确实都是由每个进程的产生的，而关联这些信息的东西正是ProcessGuid，这个对进程是唯一的。如下图

Event 23

[![](https://p1.ssl.qhimg.com/t01650043d8bb415be6.png)](https://p1.ssl.qhimg.com/t01650043d8bb415be6.png)

[![](https://p2.ssl.qhimg.com/t01cfcaf6f1fd1e0ca2.png)](https://p2.ssl.qhimg.com/t01cfcaf6f1fd1e0ca2.png)

都会有个ProcessGuid 字段，今天的这篇文章主要就是讲解Sysmo是如何生成事件的ProcessGuid的。<br>
Sysmon有两个地方会调用ProcessGuid创建的函数，第一个是初始化的时候，在服务启动的时候会初始化一次当前机器里 已经打开进程的ProcessGuid

[![](https://p4.ssl.qhimg.com/t017602690d6732817f.png)](https://p4.ssl.qhimg.com/t017602690d6732817f.png)

查看这个红色框的函数Sysmon_InitProcessCache

[![](https://p4.ssl.qhimg.com/t0151df3626208f019d.png)](https://p4.ssl.qhimg.com/t0151df3626208f019d.png)

首先会枚举当前机器所有进程，然后下面就会调用Guid的创建的函数

[![](https://p5.ssl.qhimg.com/t0186626c8a923f50d9.png)](https://p5.ssl.qhimg.com/t0186626c8a923f50d9.png)

传入ProcessPid，进程的pid

[![](https://p0.ssl.qhimg.com/t01cab67b7b4bb80333.png)](https://p0.ssl.qhimg.com/t01cab67b7b4bb80333.png)

然后像Sysmon的驱动发送IoControl码去获取该进程的相关信息，获取哪些信息呢？接下来我们看内核驱动。<br>
Sysmom内核驱动处理Io的函数SysmonDispatchIrpDeviceIO

[![](https://p3.ssl.qhimg.com/t01644ddff7cb063649.png)](https://p3.ssl.qhimg.com/t01644ddff7cb063649.png)

找到对应的IoControl

[![](https://p0.ssl.qhimg.com/t01273e077a1f00f27f.png)](https://p0.ssl.qhimg.com/t01273e077a1f00f27f.png)

这里就是处理的地方，可以发现会先检验传入参数的大小是不是正确的，然后会调用<br>
SysmonInsertCreateThreadProcess(pUserBuffer-&gt;ProcessId, 1u, pUserBuffer-&gt;NewAdd, pIrp);去获取该进程pid的进程相关的信息。

首选会获取进程的Token相关的信息

[![](https://p4.ssl.qhimg.com/t0143405764e6ac12f1.png)](https://p4.ssl.qhimg.com/t0143405764e6ac12f1.png)

在这里函数里使用了ZwOpenProcessToken(ProcessHandle, 0x20008u, &amp;TokenHandle);去获取进程token句柄

[![](https://p2.ssl.qhimg.com/t014fbe18890b379575.png)](https://p2.ssl.qhimg.com/t014fbe18890b379575.png)

然后Query句柄，使用ZwQueryInformationToken函数去获取，TokenInfomationClass分别是TokenUser、TokenGroups、TokenStatistics、TokenIntegrityLevel。最后会把这些信息输出到传输的缓冲区结构体里

[![](https://p0.ssl.qhimg.com/t01413ea93af9c0c275.png)](https://p0.ssl.qhimg.com/t01413ea93af9c0c275.png)

[![](https://p4.ssl.qhimg.com/t01babe32204d7905e8.png)](https://p4.ssl.qhimg.com/t01babe32204d7905e8.png)

获取了以上信息后，还会继续获取进程的全路径和参数

[![](https://p3.ssl.qhimg.com/t0171300224cc029e67.png)](https://p3.ssl.qhimg.com/t0171300224cc029e67.png)

AttackProcess进程后去获取进程的参数的获取，是通过PEB—&gt;ProcessParameter获取

[![](https://p2.ssl.qhimg.com/t012f345977fa800d2f.png)](https://p2.ssl.qhimg.com/t012f345977fa800d2f.png)

[![](https://p3.ssl.qhimg.com/t0161ef8f6535b168b5.png)](https://p3.ssl.qhimg.com/t0161ef8f6535b168b5.png)

接下来就是获取进程创建时间

```
ZwQueryInformationProcess(ProcessHandlev9, ProcessTimes, &amp;KernelUserTime, 0x20u, 0);
if (!KernelUserTime.CreateTime.QuadPart) `{`
    ResultLength = 48;
    if (ZwQuerySystemInformation(SystemTimeOfDayInformation, &amp;SystemTimeDelayInformation, 0x30u, &amp;ResultLength) &gt;= 0) KernelUserTime.CreateTime.QuadPart = SystemTimeDelayInformation.BootTime.QuadPart

    - SystemTimeDelayInformation.BootTimeBias;
`}`
```

[![](https://p2.ssl.qhimg.com/t013f12450ce89305e2.png)](https://p2.ssl.qhimg.com/t013f12450ce89305e2.png)

继续还会计算改进程的hash

[![](https://p3.ssl.qhimg.com/t015df0b26fda1a1388.png)](https://p3.ssl.qhimg.com/t015df0b26fda1a1388.png)

最后把这些信息输出到ring3输入的缓冲区里

[![](https://p5.ssl.qhimg.com/t01617d179e650024e7.png)](https://p5.ssl.qhimg.com/t01617d179e650024e7.png)

[![](https://p0.ssl.qhimg.com/t01aa908430481d3c32.png)](https://p0.ssl.qhimg.com/t01aa908430481d3c32.png)

结构体是：

```
struct _Report_Process `{`
    Report_Common_Header Header;
    CHAR data[16];
    ULONG ProcessPid;
    ULONG ParentPid;
    ULONG SessionId;
    ULONG UserSid;
    LARGE_INTEGER CreateTime;
    LUID AuthenticationId;
    ULONG TokenIsAppContainer;
    LUID TokenId;
    ULONG HashingalgorithmRule;
    DWORD DataChunkLength[6];
    CHAR Data[1];
`}`;
```

后面的数据data 有

<strong>SID<br>
TokenIntegrityLevel<br>
ImageFileName<br>
HASH<br>
CommandLine<br>
DirectoryPath</strong>

驱动过程结束后继续回到应用层调用的地方，应用层获取了以上数据后就是对数据进程组装来生成ProcessGuid。

[![](https://p1.ssl.qhimg.com/t01591844b9b6eb33a0.png)](https://p1.ssl.qhimg.com/t01591844b9b6eb33a0.png)

可以看到函数v7 = (const __m128i *)SysmonCreateGuid(&amp;OutBuffer.TokenId, (int)&amp;OutBuffer.CreateTime, &amp;Guid, 0x10000000);传入的参数是TokenId、CreateTime<br>
继续分析该函数内部实现

[![](https://p1.ssl.qhimg.com/t017a0799727ad17a52.png)](https://p1.ssl.qhimg.com/t017a0799727ad17a52.png)

OutGuid的参数是v6

V6的data1 赋值为g_Guid_Data1，这个从哪里来的呢，答案很简单。

在另外一个函数里有个给g_Guid_Data1赋值的地方

[![](https://p1.ssl.qhimg.com/t01084b391344b9dd3c.png)](https://p1.ssl.qhimg.com/t01084b391344b9dd3c.png)

可以看到读取注册表键值为MachineGuid的键值获取这个键值Guid的第一个Data1给g_Guid_Data1，网上翻阅，会看到

[![](https://p5.ssl.qhimg.com/t011f394e3b8789f101.png)](https://p5.ssl.qhimg.com/t011f394e3b8789f101.png)

哦，答案一目了然了，是<br>
v2 = RegOpenKeyW(HKEY_LOCAL_MACHINE, L”SOFTWARE\Microsoft\Cryptography”, &amp;phkResult);

我们看下自己机器的注册表里

[![](https://p5.ssl.qhimg.com/t01f7f507c66a6a2ec3.png)](https://p5.ssl.qhimg.com/t01f7f507c66a6a2ec3.png)

确实存在一个Guid，sysmon只去了第一个data1.

接着看**(_DWORD **)&amp;v6-&gt;Data2 = v8;

V8 就是 进程的CreateTime，只是经过了

RtlTimeToSecondsSince1970(Time, &amp;v8);的时间格式化

最后就是8个字节的数据

**(_DWORD **)v6-&gt;Data4 = GudingValue | TokenIdv5-&gt;HighPart;<br>**(_DWORD **)&amp;v6-&gt;Data4[4] = TokenIdv5-&gt;LowPart;

GudingValue是哥固定值0x10000000

填充Tokenid的高位与低位

现在我们大概清楚ProcessGuid的算法就是

**MachineIdData1-进程创建时间-TokenId组合而成的**

以上是初始化的时候ProcessGuid过程，第二个部分是实时从内核获取进程线程事件后，Sleep(500u);每500毫秒从驱动内获得事件缓冲数据

[![](https://p0.ssl.qhimg.com/t012b7879cfe7d724bf.png)](https://p0.ssl.qhimg.com/t012b7879cfe7d724bf.png)

然后调用SysmonDisplayEvent(lpOutBuffer);去解析事件

[![](https://p5.ssl.qhimg.com/t013267cdda65b80b01.png)](https://p5.ssl.qhimg.com/t013267cdda65b80b01.png)

[![](https://p4.ssl.qhimg.com/t014a4ed4db183c7d06.png)](https://p4.ssl.qhimg.com/t014a4ed4db183c7d06.png)

事件类型为7的时候，同样会调用以上函数Sysmon_DeviceIo_Process_Pid_Guid(**(_DWORD **)v22, (GUID *)&amp;v67, 4, SizeInWords);去生成ProcessGuid，事件类型7 就是我们上一篇文章讲的进程线程事件。

最后就是实验我们的结果，写代码

```
if (SUCCEEDED(StringCchPrintf(szDriverKey, MAX_PATH, _T(“\\.\ % s”), _T(“SysmonDrv”)))) `{`
    HANDLE hObjectDrv = CreateFile(szDriverKey, GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);

    if (hObjectDrv != INVALID_HANDLE_VALUE) `{`
        LARGE_INTEGER Request;
        Request.LowPart = GetCurrentProcessId();
        Request.HighPart = FALSE;
        BYTE OutBuffer[4002] = `{`
            0
        `}`;
        ULONG BytesReturned = 0;
        if (SUCCEEDED(DeviceIoControl(hObjectDrv, SYSMON_REQUEST_PROCESS_INFO, &amp;Request, 8, OutBuffer, sizeof(OutBuffer), &amp;BytesReturned, 0))) `{`

            if (BytesReturned) `{`
                Sysmon_Report_Process * pSysmon_Report_Process = (Sysmon_Report_Process * ) &amp; OutBuffer[0];

                if (pSysmon_Report_Process - &gt;Header.ReportSize) `{`

                    typedef void(__stdcall * pRtlTimeToSecondsSince1970)(LARGE_INTEGER * , LUID * );
                    LUID CreateTime;
                    GUID ProcessGuid = `{`
                        0
                    `}`;
                    ProcessGuid.Data1 = 0x118a010c;
                    pRtlTimeToSecondsSince1970 RtlTimeToSecondsSince1970 = (pRtlTimeToSecondsSince1970) GetProcAddress(GetModuleHandle(_T("ntdll.dll")), "RtlTimeToSecondsSince1970");
                    if (RtlTimeToSecondsSince1970) `{`

                        RtlTimeToSecondsSince1970( &amp; pSysmon_Report_Process - &gt;CreateTime, &amp;CreateTime); * (DWORD * ) &amp; ProcessGuid.Data2 = CreateTime.LowPart; * (DWORD * ) ProcessGuid.Data4 = pSysmon_Report_Process - &gt;TokenId.HighPart; * (DWORD * ) &amp; ProcessGuid.Data4[4] = pSysmon_Report_Process - &gt;TokenId.LowPart;
                    `}`
                    CheckServiceOk = TRUE;
                `}`
            `}`
        `}`
        CloseHandle(hObjectDrv);
        hObjectDrv = NULL;
    `}`
`}`
```

[![](https://p2.ssl.qhimg.com/t012943fe9eada7df6c.png)](https://p2.ssl.qhimg.com/t012943fe9eada7df6c.png)

我们计算自己进程的结果是

[![](https://p0.ssl.qhimg.com/t01f1778b64714f82d5.png)](https://p0.ssl.qhimg.com/t01f1778b64714f82d5.png)

**ProcessGuid = `{`118A010C-7A53-5FAB-0000-0010B1AED716`}`**

再看看sysmon里记录的记过是

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015929c9e24073602f.png)

是一样的，算法结果没问题

这篇文章就到此结束，希望能对读者有些帮助，当然我这个是v8的sysmon的版本对应的算法，最新版v11有点小的变动，但变化是在内核里的数据，其他变化不大，读者可以自己去研究。
