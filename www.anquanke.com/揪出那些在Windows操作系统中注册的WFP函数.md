> 原文链接: https://www.anquanke.com//post/id/236134 


# 揪出那些在Windows操作系统中注册的WFP函数


                                阅读量   
                                **129534**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01ed521b88dacceafb.jpg)](https://p5.ssl.qhimg.com/t01ed521b88dacceafb.jpg)



首先，minifilter有!fltkd.的命令，ndis有!ndiskd.的命令，但是WFP却没有类似的命令。

尽管有netsh wfp的命令和类似的接口/API(FwpmEnum)，但是都没有获取到注册的函数的.

有些用户，包括自己，是尽量想获取到注册的函数，而不止是那些注册的信息。

所以，出现了本文。

分析的办法有二，<br>
一正向分析，分析注册的函数（FwpsCalloutRegister），步步跟踪。<br>
二逆向分析，在注册的函数上下断点，根据调用栈步步向上逆向跟踪。



## 上面是引子

下面是方案一的分析。

首先从带有注册函数的FwpsCalloutRegister开始：<br>
FWPKCLNT.SYS!FwpsCalloutRegister3-&gt;FWPKCLNT.SYS!FwppCalloutRegister-&gt;netio.sys!KfdAddCalloutEntry-&gt;netio.sys!FeAddCalloutEntry.

在netio.sys中见到了gWfpGlobal。<br>
gFwppCallouts是个GuardedMutex。

gFwppCallouts是一个指针，这个指针指向一个结构，结构如下：

```
00000000 ; size==0x680
00000000 WfpGlobal struc ; (sizeof=0x680, mappedto_461)
00000000 Lookaside dq ? ; offset
00000008 field_8 dq ?
00000010 field_10 dd ?
00000014 field_14 dd ?
00000018 field_18 dd ?
0000001C field_1C dd ?
00000020 field_20 dd ?
00000024 field_24 dd ?
00000028 field_28 dq ?
00000030 field_30 dq ?
00000038 field_38 dq ?
00000040 field_40 dq ?
00000048 field_48 dq ?
00000050 field_50 dq ?
00000058 field_58 dq ?
00000060 field_60 dq ?
00000068 field_68 dq ?
00000070 field_70 dq ?
00000078 field_78 dq ?
00000080 FastWriteLock dq ? ; offset
00000088 field_88 dd ?
0000008C field_8C dd ?
00000090 field_90 dd ?
00000094 field_94 dd ?
00000098 field_98 dd ?
0000009C field_9C dd ?
000000A0 field_A0 dq ?
000000A8 field_A8 dd ?
000000AC field_AC dd ?
000000B0 field_B0 dd ?
000000B4 field_B4 dd ?
000000B8 field_B8 dd ?
000000BC field_BC dd ?
000000C0 KfdFilterFreeNotify dq ?
000000C8 IndexListCreate dq ?
000000D0 field_D0 dq ?
000000D8 IndexListClassify dq ?
000000E0 IndexListEnum dq ?
000000E8 IndexListAdd dq ?
000000F0 IndexListDelete dq ?
000000F8 IndexListFree dq ?
00000100 IndexHashCreate dq ?
00000108 field_108 dq ?
00000110 IndexHashClassify dq ?
00000118 IndexHashEnum dq ?
00000120 IndexHashAdd dq ?
00000128 IndexHashDelete dq ?
00000130 IndexHashFree dq ?
00000138 IndexTrieCreate dq ?
00000140 IndexTriePreClassify dq ?
00000148 field_148 dq ?
00000150 IndexTrieEnum dq ?
00000158 IndexTrieAdd dq ?
00000160 IndexTrieDelete dq ?
00000168 IndexTrieFree dq ?
00000170 field_170 dq ?
00000178 field_178 dd ?
0000017C field_17C dd ?
00000180 HashTable dq ? ; offset
00000188 field_188 dd ?
0000018C field_18C dd ?
00000190 MaxCalloutId dd ? ; 数组的个数，亦是最大个数。
00000194 field_194 dd ?
00000198 CalloutTable dq ? ; 一个数组的指针，里面包含WFP注册的重要信息，如：函数等。
000001A0 RWLockRead dq ? ; offset
000001A8 field_1A8 dd ?
000001AC field_1AC dq ?
000001B4 field_1B4 dq ?
000001BC field_1BC dd ?
000001C0 field_1C0 dd ?
000001C4 field_1C4 dq ?
000001CC field_1CC dq ?
000001D4 field_1D4 dq ?
000001DC field_1DC dq ?
000001E4 field_1E4 dq ?
000001EC field_1EC dq ?
000001F4 field_1F4 dq ?
000001FC field_1FC dq ?
00000204 field_204 dq ?
0000020C field_20C dq ?
00000214 field_214 dq ?
0000021C field_21C dq ?
00000224 field_224 dq ?
0000022C field_22C dq ?
00000234 field_234 dq ?
0000023C field_23C dq ?
00000244 field_244 dq ?
0000024C field_24C dq ?
00000254 field_254 dq ?
0000025C field_25C dq ?
00000264 field_264 dq ?
0000026C field_26C dq ?
00000274 field_274 dq ?
0000027C field_27C dq ?
00000284 field_284 dq ?
0000028C field_28C dq ?
00000294 field_294 dq ?
0000029C field_29C dq ?
000002A4 field_2A4 dq ?
000002AC field_2AC dq ?
000002B4 field_2B4 dq ?
000002BC field_2BC dq ?
000002C4 field_2C4 dq ?
000002CC field_2CC dq ?
000002D4 field_2D4 dq ?
000002DC field_2DC dq ?
000002E4 field_2E4 dq ?
000002EC field_2EC dq ?
000002F4 field_2F4 dq ?
000002FC field_2FC dq ?
00000304 field_304 dq ?
0000030C field_30C dq ?
00000314 field_314 dq ?
0000031C field_31C dq ?
00000324 field_324 dq ?
0000032C field_32C dq ?
00000334 field_334 dq ?
0000033C field_33C dq ?
00000344 field_344 dq ?
0000034C field_34C dq ?
00000354 field_354 dq ?
0000035C field_35C dq ?
00000364 field_364 dq ?
0000036C field_36C dq ?
00000374 field_374 dq ?
0000037C field_37C dd ?
00000380 field_380 dd ?
00000384 field_384 dq ?
0000038C field_38C dq ?
00000394 field_394 dq ?
0000039C field_39C dq ?
000003A4 field_3A4 dq ?
000003AC field_3AC dq ?
000003B4 field_3B4 dq ?
000003BC field_3BC dq ?
000003C4 field_3C4 dq ?
000003CC field_3CC dq ?
000003D4 field_3D4 dq ?
000003DC field_3DC dq ?
000003E4 field_3E4 dq ?
000003EC field_3EC dq ?
000003F4 field_3F4 dq ?
000003FC field_3FC dq ?
00000404 field_404 dq ?
0000040C field_40C dq ?
00000414 field_414 dq ?
0000041C field_41C dq ?
00000424 field_424 dq ?
0000042C field_42C dq ?
00000434 field_434 dq ?
0000043C field_43C dq ?
00000444 field_444 dd ?
00000448 field_448 dd ?
0000044C field_44C dq ?
00000454 field_454 dd ?
00000458 field_458 dd ?
0000045C field_45C dd ?
00000460 field_460 dd ?
00000464 field_464 dq ?
0000046C field_46C dq ?
00000474 field_474 dq ?
0000047C field_47C dq ?
00000484 field_484 dd ?
00000488 field_488 dd ?
0000048C field_48C dd ?
00000490 field_490 dd ?
00000494 field_494 dd ?
00000498 field_498 dd ?
0000049C field_49C dq ?
000004A4 field_4A4 dd ?
000004A8 field_4A8 dd ?
000004AC field_4AC dd ?
000004B0 SpinLock dq ?
000004B8 field_4B8 dd ?
000004BC field_4BC dq ?
000004C4 field_4C4 dd ?
000004C8 SpinLock2 dq ?
000004D0 field_4D0 dd ?
000004D4 field_4D4 dd ?
000004D8 field_4D8 dd ?
000004DC field_4DC dd ?
000004E0 SpinLock3 dq ?
000004E8 field_4E8 dd ?
000004EC field_4EC dd ?
000004F0 field_4F0 dd ?
000004F4 field_4F4 dd ?
000004F8 field_4F8 dd ?
000004FC field_4FC dd ?
00000500 field_500 dd ?
00000504 field_504 dd ?
00000508 InStackQueuedSpinLock dq ?
00000510 field_510 dd ?
00000514 field_514 dq ?
0000051C field_51C dq ?
00000524 field_524 dq ?
0000052C field_52C dq ?
00000534 field_534 dd ?
00000538 WorkQueue dq ?
00000540 field_540 dd ?
00000544 field_544 dq ?
0000054C field_54C dq ?
00000554 field_554 dq ?
0000055C field_55C dq ?
00000564 field_564 dd ?
00000568 field_568 dd ?
0000056C field_56C dq ?
00000574 field_574 dq ?
0000057C field_57C dd ?
00000580 field_580 dd ?
00000584 field_584 dd ?
00000588 field_588 dd ?
0000058C field_58C dq ?
00000594 field_594 dq ?
0000059C field_59C dq ?
000005A4 field_5A4 dq ?
000005AC field_5AC dq ?
000005B4 field_5B4 dq ?
000005BC field_5BC dq ?
000005C4 field_5C4 dq ?
000005CC field_5CC dq ?
000005D4 field_5D4 dq ?
000005DC field_5DC dq ?
000005E4 field_5E4 dq ?
000005EC field_5EC dq ?
000005F4 field_5F4 dq ?
000005FC field_5FC dq ?
00000604 field_604 dq ?
0000060C field_60C dq ?
00000614 field_614 dq ?
0000061C field_61C dq ?
00000624 field_624 dq ?
0000062C field_62C dq ?
00000634 field_634 dd ?
00000638 RWLockRead2 dq ? ; offset
00000640 field_640 dd ?
00000644 field_644 dd ?
00000648 field_648 dd ?
0000064C field_64C dq ?
00000654 field_654 dq ?
0000065C field_65C dq ?
00000664 field_664 dq ?
0000066C field_66C dq ?
00000674 field_674 dq ?
0000067C field_67C dd ?
00000680 WfpGlobal ends
```

KfdAddCalloutEntry函数的原型和伪代码如下：

```
NTSTATUS fastcall KfdAddCalloutEntry(int64 a1, int64 classifyFn, int64 notifyFn, int64 flowDeleteFn, int flags, int a6, UINT32 id, void * deviceObject) `{`
    int v11; // er15
    int64 Status; // rax
    NTSTATUS NtStatus; // ebx
    int v15; // [rsp+28h] [rbp-40h]
    struct _LOCK_STATE_EX v16[5]; // [rsp+40h] [rbp-28h] BYREF
    (_WORD) &amp; v16[0].OldIrql = 0;
    v16[0].Flags = 0;
    v11 = a1;
    if (id &gt; 0x186A0) return WfpReportSysErrorAsNtStatus(a1, (int)”KfdAddCalloutEntry”, STATUS_INVALID_PARAMETER, 1);
    gWfpGlobal - &gt;field_BC = 1;
    KeGenericCallDpc(WfpSyncDpcCallback, 0i64);
    Status = FeAcquireWriteEngineLock(v16);
    NtStatus = Status;
    if (!Status) `{`
        LOBYTE(v15) = a6;
        NtStatus = FeAddCalloutEntry(v11, classifyFn, notifyFn, flowDeleteFn, flags, v15, id, deviceObject);
        WfpReleaseFastWriteLock( &amp; gWfpGlobal - &gt;FastWriteLock, v16);
        gWfpGlobal - &gt;field_BC = 0;
    `}`
    return NtStatus;
`}`
```

FeAddCalloutEntry函数的原型和伪代码如下：

```
NTSTATUS fastcall FeAddCalloutEntry(int a1, int64 classifyFn, int64 notifyFn, int64 flowDeleteFn, int flags, int a6, UINT32 calloutId, void deviceObject) `{`
    int64 v12; // rax
    int64 v13; // rcx
    __int64 NtStatus; // rdi
    CalloutEntry calloutInfo; // rbx
    __int64 Status; // rax
    LODWORD(v12) = WfpAllocateCalloutEntry(calloutId);
    NtStatus = v12;
    if (v12) goto LABEL_13;
    calloutInfo = (CalloutEntry)(gWfpGlobal - &gt;CalloutTable + 0x50i64 calloutId);
    if (calloutInfo - &gt;IsUsed || calloutInfo - &gt;field_8) `{`
        LODWORD(Status) = WfpReportSysErrorAsNtStatus(v13, “IsCalloutEntryAvailable”, STATUS_OBJECT_NAME_EXISTS, 1);
        NtStatus = Status;
        if (!Status) goto LABEL_5;
        WfpReportError(Status, “IsCalloutEntryAvailable”);
    `}`
    if (NtStatus) `{`
        LABEL_13: WfpReportError(NtStatus, “FeAddCalloutEntry”);
        return NtStatus;
    `}`
    LABEL_5: memset(calloutInfo, 0, sizeof(CalloutEntry));
    calloutInfo - &gt;char0 = a1;
    calloutInfo - &gt;IsUsed = 1;
    if (a1 == 3) calloutInfo - &gt;classifyFnFast = classifyFn;
    else calloutInfo - &gt;classifyFn = classifyFn;
    calloutInfo - &gt;word4A = 0;
    calloutInfo - &gt;dword4C = 0;
    calloutInfo - &gt;flags = flags;
    calloutInfo - &gt;byte49 = a6;
    calloutInfo - &gt;notifyFn = notifyFn;
    calloutInfo - &gt;flowDeleteFn = flowDeleteFn;
    calloutInfo - &gt;byte48 = 0;
    if (deviceObject) `{`
        ObfReferenceObject(deviceObject);
        calloutInfo - &gt;deviceObject = deviceObject;
    `}`
    return NtStatus;
`}`
```

FeAddCalloutEntry函数中用到的一个数据结构如下：

```
00000000 CalloutEntry struc ; (sizeof=0x50, align=0x10, mappedto_496)
00000000 char0 dd ?
00000004 IsUsed dd ?
00000008 field_8 dd ?
0000000C field_C dd ?
00000010 classifyFn dq ?
00000018 notifyFn dq ?
00000020 flowDeleteFn dq ?
00000028 classifyFnFast dq ?
00000030 flags dd ?
00000034 field_34 dd ?
00000038 field_38 dd ?
0000003C field_3C dd ?
00000040 deviceObject dq ?
00000048 byte48 db ?
00000049 byte49 db ?
0000004A word4A dw ?
0000004C dword4C dd ?
00000050 CalloutEntry ends
```

不得不说的一个函数是WfpAllocateCalloutEntry。

```
NTSTATUS __fastcall WfpAllocateCalloutEntry(UINT64 calloutId) `{`
    NTSTATUS NtStatus; // edi
    int NewMaxCalloutId; // esi
    unsigned int v4; // ebx
    size_t v5; // r8
    void v6; // rbx
    unsigned int MaxCalloutId; // [rsp+40h] [rbp+8h] BYREF
    size_t Size; // [rsp+48h] [rbp+10h] BYREF
    void Dst; // [rsp+50h] [rbp+18h] BYREF
    NtStatus = 0;
    Dst = 0i64;
    LODWORD(Size) = 0;
    MaxCalloutId = 0;
    if ((unsigned int) calloutId &gt; 0x186A0) `{` (_QWORD) &amp; NtStatus = WfpReportSysErrorAsNtStatus(calloutId, “WfpAllocateCalloutEntry”, STATUS_INVALID_PARAMETER, 1);
        goto LABEL_9;
    `}`
    if ((unsigned int) calloutId &gt;= gWfpGlobal - &gt;MaxCalloutId) `{` (_QWORD) &amp; NtStatus = WfpUINT32Add(calloutId, 0x400, &amp;MaxCalloutId);
        if ((_QWORD) &amp; NtStatus) goto LABEL_10;
        NewMaxCalloutId = MaxCalloutId; (_QWORD) &amp; NtStatus = WfpUINT32Multiply(MaxCalloutId, 0x50u, &amp;Size);
        if ((_QWORD) &amp; NtStatus) goto LABEL_10;
        v4 = Size; (_QWORD) &amp; NtStatus = WfpPoolAllocNonPaged((unsigned int) Size, ‘CpfW’, &amp;Dst);
        if ((_QWORD) &amp; NtStatus) goto LABEL_10;
        v5 = v4;
        v6 = Dst;
        memset(Dst, 0, v5);
        memmove(v6, (const void) gWfpGlobal - &gt;CalloutTable, (unsigned int)(0x50 gWfpGlobal - &gt;MaxCalloutId));
        WfpPoolFree((void * ) &amp; gWfpGlobal - &gt;CalloutTable);
        gWfpGlobal - &gt;CalloutTable = (__int64) v6;
        gWfpGlobal - &gt;MaxCalloutId = NewMaxCalloutId;
        LABEL_9: if (! (_QWORD) &amp; NtStatus) return NtStatus;
        LABEL_10: WfpReportError((__int64 * ) &amp; NtStatus, “WfpAllocateCalloutEntry”);
    `}`
    return NtStatus;
`}`
```

总结一下吧！<br>
gWfpGlobal结构有个成员叫CalloutTable(自己命名的)，这是个指针，这片内存的默认初始大小是0x14000字节。<br>
每次有WFP注册时，都会扩大/修改这个值的：重新申请内存，复制数据，然后删除原来的内存。

gWfpGlobal-&gt;CalloutTable里其实是一个数组，每个元素的大小是0x50，这个数组是自己定义的结构：CalloutEntry。

gWfpGlobal-&gt;MaxCalloutId(自己命名的)是数组的成员的个数。

值得一说的是calloutId都是这个注册的数据在这里的索引，同时，这个calloutId也是返回给用户(驱动开发者)使用的。



## 上面是IDA的分析

下面是windbg的验证

所以windbg输出也很简单：<br>
1.定位gWfpGlobal。<br>
2.定位那个成员(CalloutTable)的偏移。<br>
3.获取MaxCalloutId的大小<br>
4.dps XXX L(MaxCalloutId)。

那都动手吧！

```
0: kd&gt; vertarget
Windows 8 Kernel Version 9200 MP (8 procs) Free x64
Product: WinNt, suite: TerminalServer SingleUserTS
Built by: 19041.1.amd64fre.vb_release.191206-1406
Machine Name:
Kernel base = 0xfffff80618400000 PsLoadedModuleList = 0xfffff8061902a490
Debug session time: Fri Mar 26 08:36:03.775 2021 (UTC + 8:00)
System Uptime: 2 days 15:17:46.248
0: kd&gt; dp netio!gWfpGlobal L1
fffff8061bdea560 ffffa00a142028e0
0: kd&gt; uf netio!FeAddCalloutEntry
NETIO!FeAddCalloutEntry:
fffff8061bd95c10 48895c2408 mov qword ptr [rsp+8],rbx
fffff8061bd95c15 48896c2410 mov qword ptr [rsp+10h],rbp
fffff8061bd95c1a 4889742418 mov qword ptr [rsp+18h],rsi
fffff8061bd95c1f 57 push rdi
fffff8061bd95c20 4156 push r14
fffff8061bd95c22 4157 push r15
fffff8061bd95c24 4883ec20 sub rsp,20h
fffff8061bd95c28 8be9 mov ebp,ecx
fffff8061bd95c2a 4d8bf1 mov r14,r9
fffff8061bd95c2d 8b4c2470 mov ecx,dword ptr [rsp+70h]
fffff8061bd95c31 4d8bf8 mov r15,r8
fffff8061bd95c34 488bf2 mov rsi,rdx
fffff8061bd95c37 e88076ffff call NETIO!WfpAllocateCalloutEntry (fffff8061bd8d2bc)
fffff8061bd95c3c 488bf8 mov rdi,rax
fffff8061bd95c3f 4885c0 test rax,rax
fffff8061bd95c42 0f85cd430100 jne NETIO!FeAddCalloutEntry+0x14405 (fffff8061bdaa015) Branch

NETIO!FeAddCalloutEntry+0x38:
fffff8061bd95c48 8b442470 mov eax,dword ptr [rsp+70h]
fffff8061bd95c4c 488d1c80 lea rbx,[rax+rax*4]
fffff8061bd95c50 488b0509490500 mov rax,qword ptr [NETIO!gWfpGlobal (fffff8061bdea560)]
fffff8061bd95c57 48c1e304 shl rbx,4
fffff8061bd95c5b 48039898010000 add rbx,qword ptr [rax+198h]
fffff8061bd95c62 397b04 cmp dword ptr [rbx+4],edi
fffff8061bd95c65 0f8571430100 jne NETIO!FeAddCalloutEntry+0x143cc (fffff806 1bda9fdc) Branch

NETIO!FeAddCalloutEntry+0x5b:
fffff8061bd95c6b 397b08 cmp dword ptr [rbx+8],edi
fffff8061bd95c6e 0f8568430100 jne NETIO!FeAddCalloutEntry+0x143cc (fffff806 1bda9fdc) Branch

NETIO!FeAddCalloutEntry+0x64:
fffff8061bd95c74 4885ff test rdi,rdi
fffff8061bd95c77 0f8598430100 jne NETIO!FeAddCalloutEntry+0x14405 (fffff806 1bdaa015) Branch

NETIO!FeAddCalloutEntry+0x6d:
fffff8061bd95c7d 33d2 xor edx,edx
fffff8061bd95c7f 488bcb mov rcx,rbx
fffff8061bd95c82 448d4250 lea r8d,[rdx+50h]
fffff8061bd95c86 e8753d0000 call NETIO!memset (fffff8061bd99a00)
fffff8061bd95c8b 892b mov dword ptr [rbx],ebp
fffff8061bd95c8d c7430401000000 mov dword ptr [rbx+4],1
fffff8061bd95c94 83fd03 cmp ebp,3
fffff8061bd95c97 7463 je NETIO!FeAddCalloutEntry+0xec (fffff8061bd95cfc) Branch

NETIO!FeAddCalloutEntry+0x89:
fffff806 1bd95c99 48897310 mov qword ptr [rbx+10h],rsi

NETIO!FeAddCalloutEntry+0x8d:
fffff8061bd95c9d 8b442460 mov eax,dword ptr [rsp+60h]
fffff8061bd95ca1 6683634a00 and word ptr [rbx+4Ah],0
fffff8061bd95ca6 83634c00 and dword ptr [rbx+4Ch],0
fffff8061bd95caa 488b742478 mov rsi,qword ptr [rsp+78h]
fffff8061bd95caf 894330 mov dword ptr [rbx+30h],eax
fffff8061bd95cb2 8a442468 mov al,byte ptr [rsp+68h]
fffff8061bd95cb6 884349 mov byte ptr [rbx+49h],al
fffff8061bd95cb9 4c897b18 mov qword ptr [rbx+18h],r15
fffff8061bd95cbd 4c897320 mov qword ptr [rbx+20h],r14
fffff8061bd95cc1 c6434800 mov byte ptr [rbx+48h],0
fffff8061bd95cc5 4885f6 test rsi,rsi
fffff8061bd95cc8 751d jne NETIO!FeAddCalloutEntry+0xd7 (fffff806 1bd95ce7) Branch

NETIO!FeAddCalloutEntry+0xba:
fffff8061bd95cca 488b5c2440 mov rbx,qword ptr [rsp+40h]
fffff8061bd95ccf 488bc7 mov rax,rdi
fffff8061bd95cd2 488b6c2448 mov rbp,qword ptr [rsp+48h]
fffff8061bd95cd7 488b742450 mov rsi,qword ptr [rsp+50h]
fffff8061bd95cdc 4883c420 add rsp,20h
fffff8061bd95ce0 415f pop r15
fffff8061bd95ce2 415e pop r14
fffff8061bd95ce4 5f pop rdi
fffff806 1bd95ce5 c3 ret

NETIO!FeAddCalloutEntry+0xd7:
fffff8061bd95ce7 488bce mov rcx,rsi
fffff8061bd95cea 4c8b1507b90500 mov r10,qword ptr [NETIO!_imp_ObfReferenceObject (fffff8061bdf15f8)]
fffff8061bd95cf1 e8aab58cfc call nt!ObfReferenceObject (fffff806186612a0)
fffff8061bd95cf6 48897340 mov qword ptr [rbx+40h],rsi
fffff8061bd95cfa ebce jmp NETIO!FeAddCalloutEntry+0xba (fffff8061bd95cca) Branch

NETIO!FeAddCalloutEntry+0xec:
fffff8061bd95cfc 48897328 mov qword ptr [rbx+28h],rsi
fffff8061bd95d00 eb9b jmp NETIO!FeAddCalloutEntry+0x8d (fffff806 1bd95c9d) Branch

NETIO!FeAddCalloutEntry+0x143cc:
fffff8061bda9fdc 41b901000000 mov r9d,1
fffff8061bda9fe2 488d15d7770300 lea rdx,[NETIO!string' (fffff8061bde17c0)]
fffff8061bda9fe9 41b800000040 mov r8d,40000000h
fffff8061bda9fef e8d061feff call NETIO!WfpReportSysErrorAsNtStatus (fffff8061bd901c4)
fffff8061bda9ff4 488bf8 mov rdi,rax
fffff8061bda9ff7 4885c0 test rax,rax
fffff8061bda9ffa 0f847dbcfeff je NETIO!FeAddCalloutEntry+0x6d (fffff806 1bd95c7d) Branch

NETIO!FeAddCalloutEntry+0x143f0:
fffff8061bdaa000 488d15b9770300 lea rdx,[NETIO!string’ (fffff8061bde17c0)]
fffff8061bdaa007 488bc8 mov rcx,rax
fffff8061bdaa00a e8f561feff call NETIO!WfpReportError (fffff8061bd90204)
fffff8061bdaa00f 90 nop
fffff8061bdaa010 e95fbcfeff jmp NETIO!FeAddCalloutEntry+0x64 (fffff806 1bd95c74) Branch

NETIO!FeAddCalloutEntry+0x14405:
fffff8061bdaa015 488d15bc770300 lea rdx,[NETIO!string’ (fffff8061bde17d8)]
fffff8061bdaa01c 488bcf mov rcx,rdi
fffff8061bdaa01f e8e061feff call NETIO!WfpReportError (fffff8061bd90204)
fffff8061bdaa024 90 nop
fffff8061bdaa025 e9a0bcfeff jmp NETIO!FeAddCalloutEntry+0xba (fffff8061bd95cca) Branch
0: kd&gt; ? ffffa00a142028e0 + 198
Evaluate expression: -105509828941192 = ffffa00a14202a78
0: kd&gt; ? ffffa00a142028e0 + 190
Evaluate expression: -105509828941200 = ffffa00a14202a70
0: kd&gt; dq ffffa00a14202a78 L1
ffffa00a14202a78 ffffa00a14213000
0: kd&gt; dd ffffa00a14202a70 l1
ffffa00a14202a70 00000400
0: kd&gt; ? (00000400 0x50)/8 数组的个数数组的大小，再除以dps在x64上显示的大小。
Evaluate expression: 10240 = 0000000000002800
0: kd&gt; dps ffffa00a14213000 L2800
ffffa00a14213000 0000000000000000
……
ffffa00a14213058 0000000000000000
ffffa00a14213060 fffff8061c08fd40 tcpip!IPSecInboundTransportFilterCalloutClassifyV4
ffffa00a14213068 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213070 0000000000000000
……
ffffa00a142130a8 0000000000000000
ffffa00a142130b0 fffff8061c08fe90 tcpip!IPSecInboundTransportFilterCalloutClassifyV6
ffffa00a142130b8 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a142130c0 0000000000000000
……
ffffa00a142130f8 0000000000000000
ffffa00a14213100 fffff8061c090d80 tcpip!IPSecOutboundTransportFilterCalloutClassifyV4
ffffa00a14213108 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213110 0000000000000000
……
ffffa00a14213148 0000000000000000
ffffa00a14213150 fffff8061c090eb0 tcpip!IPSecOutboundTransportFilterCalloutClassifyV6
ffffa00a14213158 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213160 0000000000000000
……
ffffa00a14213198 0000000000000000
ffffa00a142131a0 fffff8061c0903e0 tcpip!IPSecInboundTunnelFilterCalloutClassifyV4
ffffa00a142131a8 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a142131b0 0000000000000000
……
ffffa00a142131e8 0000000000000000
ffffa00a142131f0 fffff8061c0904b0 tcpip!IPSecInboundTunnelFilterCalloutClassifyV6
ffffa00a142131f8 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213200 0000000000000000
……
ffffa00a14213238 0000000000000000
ffffa00a14213240 fffff8061c091390 tcpip!IPSecOutboundTunnelFilterCalloutClassifyV4
ffffa00a14213248 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213250 0000000000000000
……
ffffa00a14213288 0000000000000000
ffffa00a14213290 fffff8061c091460 tcpip!IPSecOutboundTunnelFilterCalloutClassifyV6
ffffa00a14213298 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a142132a0 0000000000000000
……
ffffa00a142132d8 0000000000000000
ffffa00a142132e0 fffff8061c08f1f0 tcpip!IPSecForwardInboundTunnelFilterCalloutClassifyV4
ffffa00a142132e8 fffff8061bfd2da0 tcpip!IPSecForwardInboundTunnelFilterCalloutNotifyV4
ffffa00a142132f0 0000000000000000
……
ffffa00a14213328 0000000000000000
ffffa00a14213330 fffff8061c08f360 tcpip!IPSecForwardInboundTunnelFilterCalloutClassifyV6
ffffa00a14213338 fffff8061bfd2e00 tcpip!IPSecForwardInboundTunnelFilterCalloutNotifyV6
ffffa00a14213340 0000000000000000
……
ffffa00a14213378 0000000000000000
ffffa00a14213380 fffff8061c08f4d0 tcpip!IPSecForwardOutboundTunnelFilterCalloutClassifyV4
ffffa00a14213388 fffff8061bfd2e60 tcpip!IPSecForwardOutboundTunnelFilterCalloutNotifyV4
ffffa00a14213390 0000000000000000
……
ffffa00a142133c8 0000000000000000
ffffa00a142133d0 fffff8061c08f630 tcpip!IPSecForwardOutboundTunnelFilterCalloutClassifyV6
ffffa00a142133d8 fffff8061bfd2f00 tcpip!IPSecForwardOutboundTunnelFilterCalloutNotifyV6
ffffa00a142133e0 0000000000000000
……
ffffa00a14213418 0000000000000000
ffffa00a14213420 fffff8061c08f7b0 tcpip!IPSecInboundAcceptAuthorizeCalloutClassify
ffffa00a14213428 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213430 0000000000000000
……
ffffa00a14213468 0000000000000000
ffffa00a14213470 fffff8061c08f7b0 tcpip!IPSecInboundAcceptAuthorizeCalloutClassify
ffffa00a14213478 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213480 0000000000000000
……
ffffa00a142134b8 0000000000000000
ffffa00a142134c0 fffff8061c08ec40 tcpip!IPSecAleConnectCalloutClassify
ffffa00a142134c8 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a142134d0 0000000000000000
……
ffffa00a14213508 0000000000000000
ffffa00a14213510 fffff8061c08ec40 tcpip!IPSecAleConnectCalloutClassify
ffffa00a14213518 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213520 0000000000000000
……
ffffa00a14213558 0000000000000000
ffffa00a14213560 fffff8061becba20 tcpip!WfpEnforceSilentDrop
ffffa00a14213568 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213570 0000000000000000
……
ffffa00a142135a8 0000000000000000
ffffa00a142135b0 fffff8061becba20 tcpip!WfpEnforceSilentDrop
ffffa00a142135b8 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a142135c0 0000000000000000
……
ffffa00a14213738 0000000000000000
ffffa00a14213740 fffff8061bf8f3b0 tcpip!WfpAlepSetOptionsCalloutClassify
ffffa00a14213748 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213750 0000000000000000
……
ffffa00a14213788 0000000000000000
ffffa00a14213790 fffff8061bf8f3b0 tcpip!WfpAlepSetOptionsCalloutClassify
ffffa00a14213798 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a142137a0 0000000000000000
……
ffffa00a142137d8 0000000000000000
ffffa00a142137e0 fffff8061c08ffe0 tcpip!IPSecInboundTunnelAcceptAuthorizeCalloutClassify
ffffa00a142137e8 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a142137f0 0000000000000000
……
ffffa00a14213828 0000000000000000
ffffa00a14213830 fffff8061c08ffe0 tcpip!IPSecInboundTunnelAcceptAuthorizeCalloutClassify
ffffa00a14213838 fffff8061bfd2bb0 tcpip!IPSecAleConnectCalloutNotify
ffffa00a14213840 0000000000000000
……
ffffa00a14213878 0000000000000000
ffffa00a14213880 fffff8061bec0bf0 tcpip!FlpEdgeTraversalCalloutClassify
ffffa00a14213888 fffff8061bed4dc0 tcpip!FlpEdgeTraversalCalloutNotify
ffffa00a14213890 0000000000000000
……
ffffa00a142138c8 0000000000000000
ffffa00a142138d0 fffff8061bec0bf0 tcpip!FlpEdgeTraversalCalloutClassify
ffffa00a142138d8 fffff8061bed4dc0 tcpip!FlpEdgeTraversalCalloutNotify
ffffa00a142138e0 0000000000000000
……
ffffa00a14213918 0000000000000000
ffffa00a14213920 fffff8061bec0bf0 tcpip!FlpEdgeTraversalCalloutClassify
ffffa00a14213928 fffff8061bed4dc0 tcpip!FlpEdgeTraversalCalloutNotify
ffffa00a14213930 0000000000000000
……
ffffa00a14213968 0000000000000000
ffffa00a14213970 fffff8061bec0bf0 tcpip!FlpEdgeTraversalCalloutClassify
ffffa00a14213978 fffff8061bed4dc0 tcpip!FlpEdgeTraversalCalloutNotify
ffffa00a14213980 0000000000000000
……
ffffa00a142139b8 0000000000000000
ffffa00a142139c0 fffff8061c0a47a0 tcpip!IdpCalloutClassifyV6
ffffa00a142139c8 fffff8061c0a4ae0 tcpip!IdpCalloutNotifyV6
ffffa00a142139d0 0000000000000000
……
ffffa00a14213a08 0000000000000000
ffffa00a14213a10 fffff8061c0a46a0 tcpip!IdpCalloutClassifyV4
ffffa00a14213a18 fffff8061c0a49e0 tcpip!IdpCalloutNotifyV4
ffffa00a14213a20 0000000000000000
……
ffffa00a14213a58 0000000000000000
ffffa00a14213a60 fffff8061bf6a130 tcpip!TcpTemplatesFilter
ffffa00a14213a68 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213a70 0000000000000000
……
ffffa00a14213aa8 0000000000000000
ffffa00a14213ab0 fffff8061bf6a130 tcpip!TcpTemplatesFilter
ffffa00a14213ab8 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213ac0 0000000000000000
……
ffffa00a14213af8 0000000000000000
ffffa00a14213b00 fffff8061bf6a130 tcpip!TcpTemplatesFilter
ffffa00a14213b08 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213b10 0000000000000000
……
ffffa00a14213b48 0000000000000000
ffffa00a14213b50 fffff8061bf6a130 tcpip!TcpTemplatesFilter
ffffa00a14213b58 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213b60 0000000000000000
……
ffffa00a14213b98 0000000000000000
ffffa00a14213ba0 fffff8061becc8c0 tcpip!WfpAlepDbgLowboxSetByPolicyLoopbackCalloutClassify
ffffa00a14213ba8 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213bb0 0000000000000000
……
ffffa00a14213be8 0000000000000000
ffffa00a14213bf0 fffff8061becc8c0 tcpip!WfpAlepDbgLowboxSetByPolicyLoopbackCalloutClassify
ffffa00a14213bf8 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213c00 0000000000000000
……
ffffa00a14213c38 0000000000000000
ffffa00a14213c40 fffff8061bf8f3b0 tcpip!WfpAlepSetOptionsCalloutClassify
ffffa00a14213c48 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213c50 0000000000000000
……
ffffa00a14213c88 0000000000000000
ffffa00a14213c90 fffff8061bf8f3b0 tcpip!WfpAlepSetOptionsCalloutClassify
ffffa00a14213c98 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213ca0 0000000000000000
……
ffffa00a14213cd8 0000000000000000
ffffa00a14213ce0 fffff8061bf8f100 tcpip!WfpAlepPolicySilentModeCalloutClassify
ffffa00a14213ce8 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213cf0 0000000000000000
……
ffffa00a14213d28 0000000000000000
ffffa00a14213d30 fffff8061bf8f100 tcpip!WfpAlepPolicySilentModeCalloutClassify
ffffa00a14213d38 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213d40 0000000000000000
……
ffffa00a14213d78 0000000000000000
ffffa00a14213d80 fffff8061bf8f100 tcpip!WfpAlepPolicySilentModeCalloutClassify
ffffa00a14213d88 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213d90 0000000000000000
……
ffffa00a14213dc8 0000000000000000
ffffa00a14213dd0 fffff8061bf8f100 tcpip!WfpAlepPolicySilentModeCalloutClassify
ffffa00a14213dd8 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14213de0 0000000000000000
……
ffffa00a14218008 0000000000000000
ffffa00a14218010 fffff8061bf8f1e0 tcpip!WfpAlepRioAppIdHelperCalloutClassify
ffffa00a14218018 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14218020 0000000000000000
……
ffffa00a14218058 0000000000000000
ffffa00a14218060 fffff8061bf8f1e0 tcpip!WfpAlepRioAppIdHelperCalloutClassify
ffffa00a14218068 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14218070 0000000000000000
……
ffffa00a142180a8 0000000000000000
ffffa00a142180b0 fffff8061bf8f230 tcpip!WfpAlepSetBindIfListCalloutClassify
ffffa00a142180b8 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a142180c0 0000000000000000
……
ffffa00a142180f8 0000000000000000
ffffa00a14218100 fffff8061bf8f230 tcpip!WfpAlepSetBindIfListCalloutClassify
ffffa00a14218108 fffff8061bed0120 tcpip!FllAddGroup
ffffa00a14218110 0000000000000000
……
ffffa00a14218148 0000000000000000
ffffa00a14218150 fffff8061bf8c0a0 tcpip!WfpVpnCalloutClassifyV4
ffffa00a14218158 fffff8061bf8c460 tcpip!WfpVpnCalloutNotifyV4
ffffa00a14218160 fffff8061bf8c310 tcpip!WfpVpnCalloutFlowDeleteV4
ffffa00a14218168 0000000000000000
……
ffffa00a14218198 0000000000000000
ffffa00a142181a0 fffff8061bf8c1d0 tcpip!WfpVpnCalloutClassifyV6
ffffa00a142181a8 fffff8061bf8c490 tcpip!WfpVpnCalloutNotifyV6
ffffa00a142181b0 fffff8061bf8c310 tcpip!WfpVpnCalloutFlowDeleteV4
ffffa00a142181b8 0000000000000000
……
ffffa00a142181e8 0000000000000000
ffffa00a142181f0 fffff8061e6213f0 pango_netfilter2+0x13f0
ffffa00a142181f8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218200 0000000000000000
……
ffffa00a14218238 0000000000000000
ffffa00a14218240 fffff8061e6213f0 pango_netfilter2+0x13f0
ffffa00a14218248 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218250 0000000000000000
……
ffffa00a14218288 0000000000000000
ffffa00a14218290 fffff8061e621640 pango_netfilter2+0x1640
ffffa00a14218298 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142182a0 fffff8061e621360 pango_netfilter2+0x1360
ffffa00a142182a8 0000000000000000
……
ffffa00a142182d8 0000000000000000
ffffa00a142182e0 fffff8061e621600 pango_netfilter2+0x1600
ffffa00a142182e8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142182f0 fffff8061e6213b0 pango_netfilter2+0x13b0
ffffa00a142182f8 0000000000000000
……
ffffa00a14218328 0000000000000000
ffffa00a14218330 fffff8061e622460 pango_netfilter2+0x2460
ffffa00a14218338 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218340 fffff8061e6213b0 pango_netfilter2+0x13b0
ffffa00a14218348 0000000000000000
……
ffffa00a14218378 0000000000000000
ffffa00a14218380 fffff8061e621640 pango_netfilter2+0x1640
ffffa00a14218388 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218390 fffff8061e621360 pango_netfilter2+0x1360
ffffa00a14218398 0000000000000000
……
ffffa00a142183c8 0000000000000000
ffffa00a142183d0 fffff8061e621600 pango_netfilter2+0x1600
ffffa00a142183d8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142183e0 fffff8061e6213b0 pango_netfilter2+0x13b0
ffffa00a142183e8 0000000000000000
……
ffffa00a14218418 0000000000000000
ffffa00a14218420 fffff8061e622460 pango_netfilter2+0x2460
ffffa00a14218428 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218430 fffff8061e6213b0 pango_netfilter2+0x13b0
ffffa00a14218438 0000000000000000
……
ffffa00a14218468 0000000000000000
ffffa00a14218470 fffff8061e621680 pango_netfilter2+0x1680
ffffa00a14218478 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218480 0000000000000000
……
ffffa00a142184b8 0000000000000000
ffffa00a142184c0 fffff8061e621680 pango_netfilter2+0x1680
ffffa00a142184c8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142184d0 0000000000000000
……
ffffa00a14218508 0000000000000000
ffffa00a14218510 fffff8061e621710 pango_netfilter2+0x1710
ffffa00a14218518 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218520 0000000000000000
……
ffffa00a14218558 0000000000000000
ffffa00a14218560 fffff8061e621710 pango_netfilter2+0x1710
ffffa00a14218568 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218570 0000000000000000
……
ffffa00a142185a8 0000000000000000
ffffa00a142185b0 fffff8061e621cc0 pango_netfilter2+0x1cc0
ffffa00a142185b8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142185c0 fffff8061e621cb0 pango_netfilter2+0x1cb0
ffffa00a142185c8 0000000000000000
……
ffffa00a142185f8 0000000000000000
ffffa00a14218600 fffff8061e621cc0 pango_netfilter2+0x1cc0
ffffa00a14218608 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218610 fffff8061e621cb0 pango_netfilter2+0x1cb0
ffffa00a14218618 0000000000000000
……
ffffa00a14218648 0000000000000000
ffffa00a14218650 fffff8061e621e20 pango_netfilter2+0x1e20
ffffa00a14218658 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218660 fffff8061e621cb0 pango_netfilter2+0x1cb0
ffffa00a14218668 0000000000000000
……
ffffa00a14218698 0000000000000000
ffffa00a142186a0 fffff8061e621e20 pango_netfilter2+0x1e20
ffffa00a142186a8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142186b0 fffff8061e621cb0 pango_netfilter2+0x1cb0
ffffa00a142186b8 0000000000000000
……
ffffa00a142186e8 0000000000000000
ffffa00a142186f0 fffff8061e621f60 pango_netfilter2+0x1f60
ffffa00a142186f8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218700 0000000000000000
……
ffffa00a14218738 0000000000000000
ffffa00a14218740 fffff8061e621f60 pango_netfilter2+0x1f60
ffffa00a14218748 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218750 0000000000000000
……
ffffa00a14218788 0000000000000000
ffffa00a14218790 fffff8061e622160 pango_netfilter2+0x2160
ffffa00a14218798 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142187a0 0000000000000000
……
ffffa00a142187d8 0000000000000000
ffffa00a142187e0 fffff8061e622160 pango_netfilter2+0x2160
ffffa00a142187e8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142187f0 0000000000000000
……
ffffa00a14218828 0000000000000000
ffffa00a14218830 fffff8061e6221e0 pango_netfilter2+0x21e0
ffffa00a14218838 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218840 0000000000000000
……
ffffa00a14218878 0000000000000000
ffffa00a14218880 fffff8061e6221e0 pango_netfilter2+0x21e0
ffffa00a14218888 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218890 0000000000000000
……
ffffa00a142188c8 0000000000000000
ffffa00a142188d0 fffff8061e6223f0 pango_netfilter2+0x23f0
ffffa00a142188d8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142188e0 0000000000000000
……
ffffa00a14218918 0000000000000000
ffffa00a14218920 fffff8061e6223f0 pango_netfilter2+0x23f0
ffffa00a14218928 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218930 0000000000000000
……
ffffa00a14218968 0000000000000000
ffffa00a14218970 fffff8061e622630 pango_netfilter2+0x2630
ffffa00a14218978 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218980 0000000000000000
……
ffffa00a142189b8 0000000000000000
ffffa00a142189c0 fffff8061e622630 pango_netfilter2+0x2630
ffffa00a142189c8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a142189d0 0000000000000000
……
ffffa00a14218a08 0000000000000000
ffffa00a14218a10 fffff8061e622630 pango_netfilter2+0x2630
ffffa00a14218a18 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218a20 0000000000000000
……
ffffa00a14218a58 0000000000000000
ffffa00a14218a60 fffff8061e622630 pango_netfilter2+0x2630
ffffa00a14218a68 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218a70 0000000000000000
……
ffffa00a14218be8 0000000000000000
ffffa00a14218bf0 fffff8061e622820 pango_netfilter2+0x2820
ffffa00a14218bf8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218c00 0000000000000000
……
ffffa00a14218c38 0000000000000000
ffffa00a14218c40 fffff8061e622820 pango_netfilter2+0x2820
ffffa00a14218c48 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218c50 0000000000000000
……
ffffa00a14218c88 0000000000000000
ffffa00a14218c90 fffff8061e622af0 pango_netfilter2+0x2af0
ffffa00a14218c98 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218ca0 0000000000000000
……
ffffa00a14218cd8 0000000000000000
ffffa00a14218ce0 fffff8061e622af0 pango_netfilter2+0x2af0
ffffa00a14218ce8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218cf0 0000000000000000
……
ffffa00a14218d28 0000000000000000
ffffa00a14218d30 fffff8061e622b80 pango_netfilter2+0x2b80
ffffa00a14218d38 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218d40 0000000000000000
……
ffffa00a14218d78 0000000000000000
ffffa00a14218d80 fffff8061e622b80 pango_netfilter2+0x2b80
ffffa00a14218d88 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218d90 0000000000000000
……
ffffa00a14218dc8 0000000000000000
ffffa00a14218dd0 fffff8061e622c00 pango_netfilter2+0x2c00
ffffa00a14218dd8 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218de0 0000000000000000
……
ffffa00a14218e18 0000000000000000
ffffa00a14218e20 fffff8061e622c00 pango_netfilter2+0x2c00
ffffa00a14218e28 fffff8061e621350 pango_netfilter2+0x1350
ffffa00a14218e30 0000000000000000
……
ffffa00a14218e68 0000000000000000
ffffa00a14218e70 fffff80613551040 mpsdrv!MpsQueryUserCallout
ffffa00a14218e78 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14218e80 0000000000000000
……
ffffa00a14218eb8 0000000000000000
ffffa00a14218ec0 fffff80613551040 mpsdrv!MpsQueryUserCallout
ffffa00a14218ec8 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14218ed0 0000000000000000
……
ffffa00a14218f08 0000000000000000
ffffa00a14218f10 fffff80613551040 mpsdrv!MpsQueryUserCallout
ffffa00a14218f18 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14218f20 0000000000000000
……
ffffa00a14218f58 0000000000000000
ffffa00a14218f60 fffff80613551040 mpsdrv!MpsQueryUserCallout
ffffa00a14218f68 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14218f70 0000000000000000
……
ffffa00a14218fa8 0000000000000000
ffffa00a14218fb0 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a14218fb8 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14218fc0 0000000000000000
……
ffffa00a14218ff8 0000000000000000
ffffa00a14219000 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a14219008 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219010 0000000000000000
……
ffffa00a14219048 0000000000000000
ffffa00a14219050 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a14219058 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219060 0000000000000000
……
ffffa00a14219098 0000000000000000
ffffa00a142190a0 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a142190a8 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a142190b0 0000000000000000
……
ffffa00a142190e8 0000000000000000
ffffa00a142190f0 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a142190f8 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219100 0000000000000000
……
ffffa00a14219138 0000000000000000
ffffa00a14219140 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a14219148 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219150 0000000000000000
……
ffffa00a14219188 0000000000000000
ffffa00a14219190 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a14219198 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a142191a0 0000000000000000
……
ffffa00a142191d8 0000000000000000
ffffa00a142191e0 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a142191e8 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a142191f0 0000000000000000
……
ffffa00a14219228 0000000000000000
ffffa00a14219230 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a14219238 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219240 0000000000000000
……
ffffa00a14219278 0000000000000000
ffffa00a14219280 fffff80613557790 mpsdrv!MpsLoggingCallout
ffffa00a14219288 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219290 0000000000000000
……
ffffa00a142192c8 0000000000000000
ffffa00a142192d0 fffff80613551460 mpsdrv!MpsSecondaryConnectionsCallout
ffffa00a142192d8 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a142192e0 0000000000000000
……
ffffa00a14219318 0000000000000000
ffffa00a14219320 fffff80613551460 mpsdrv!MpsSecondaryConnectionsCallout
ffffa00a14219328 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219330 0000000000000000
……
ffffa00a14219368 0000000000000000
ffffa00a14219370 fffff80613551460 mpsdrv!MpsSecondaryConnectionsCallout
ffffa00a14219378 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219380 0000000000000000
……
ffffa00a142193b8 0000000000000000
ffffa00a142193c0 fffff80613551460 mpsdrv!MpsSecondaryConnectionsCallout
ffffa00a142193c8 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a142193d0 0000000000000000
……
ffffa00a14219408 0000000000000000
ffffa00a14219410 fffff80613557420 mpsdrv!MpsFlowEstablishedCallout
ffffa00a14219418 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219420 0000000000000000
……
ffffa00a14219458 0000000000000000
ffffa00a14219460 fffff80613557420 mpsdrv!MpsFlowEstablishedCallout
ffffa00a14219468 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219470 0000000000000000
……
ffffa00a142194a8 0000000000000000
ffffa00a142194b0 fffff80613557e20 mpsdrv!MpsStreamFlowAnalysisCallout
ffffa00a142194b8 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a142194c0 fffff806135573d0 mpsdrv!MpsFlowAnalysisFlowDelete
ffffa00a142194c8 0000000000000000
……
ffffa00a142194f8 0000000000000000
ffffa00a14219500 fffff80613557e20 mpsdrv!MpsStreamFlowAnalysisCallout
ffffa00a14219508 fffff80613552710 mpsdrv!MpsDummyFilterNotify
ffffa00a14219510 fffff806135573d0 mpsdrv!MpsFlowAnalysisFlowDelete
ffffa00a14219518 0000000000000000
……
ffffa00a14219548 0000000000000000
ffffa00a14219550 fffff806132a1940 Ndu!NduFlowEstablishedClassify
ffffa00a14219558 fffff806132ab060 Ndu!NduCalloutNotify
ffffa00a14219560 0000000000000000
……
ffffa00a14219598 0000000000000000
ffffa00a142195a0 fffff806132a1940 Ndu!NduFlowEstablishedClassify
ffffa00a142195a8 fffff806132ab060 Ndu!NduCalloutNotify
ffffa00a142195b0 0000000000000000
……
ffffa00a142195f0 0000000000000000
ffffa00a142195f8 fffff806132ab0b0 Ndu!NduCalloutNotify2
ffffa00a14219600 ffff4fe4ded0d622
ffffa00a14219608 fffff806132a6ad0 Ndu!NduInboundTransportClassify
ffffa00a14219610 0000000000000362
……
ffffa00a14219640 0000000000000000
ffffa00a14219648 fffff806132ab0b0 Ndu!NduCalloutNotify2
ffffa00a14219650 ffff4fe4ded0d622
ffffa00a14219658 fffff806132a4170 Ndu!NduOutboundTransportClassify
ffffa00a14219660 0000000000000362
……
ffffa00a14219690 0000000000000000
ffffa00a14219698 fffff806132ab0b0 Ndu!NduCalloutNotify2
ffffa00a142196a0 ffff4fe4ded0d622
ffffa00a142196a8 fffff806132a4530 Ndu!NduInboundMacClassify
ffffa00a142196b0 00000000000003e2
……
ffffa00a142196e0 0000000000000000
ffffa00a142196e8 fffff806132ab0b0 Ndu!NduCalloutNotify2
ffffa00a142196f0 ffff4fe4ded0d622
ffffa00a142196f8 fffff806132a3100 Ndu!NduOutboundMacClassify
ffffa00a14219700 00000000000003e2
……
ffffa00a14219728 0000000000000000
ffffa00a14219730 fffff80613caf630 winnat!IPxlatOutboundIPv4Callout
ffffa00a14219738 fffff80613ca1b30 winnat!IPxlatNotifyCallout
ffffa00a14219740 0000000000000000
……
ffffa00a14219778 0000000000000000
ffffa00a14219780 fffff80613caf780 winnat!IPxlatInboundIPv6Callout
ffffa00a14219788 fffff80613ca1b30 winnat!IPxlatNotifyCallout
ffffa00a14219790 0000000000000000
……
ffffa00a142197c8 0000000000000000
ffffa00a142197d0 fffff80613caf930 winnat!IPxlatForwardIPv4Callout
ffffa00a142197d8 fffff80613ca1b30 winnat!IPxlatNotifyCallout
ffffa00a142197e0 0000000000000000
……
ffffa00a14226ff8 0000000000000000
```

至此分析完毕，可以和一款叫Windows-Kernel-Explorer的ARK做对比。

话外题：

这个变量（NETIO!gWfpGlobal）不用解析符号，因为有导出的NETIO!FeGetWfpGlobalPtr函数。

```
0: kd&gt; u NETIO!FeGetWfpGlobalPtr
NETIO!FeGetWfpGlobalPtr:
fffff8061bd99310 488b0549120500 mov rax,qword ptr [NETIO!gWfpGlobal (fffff8061bdea560)]
fffff8061bd99317 c3 ret
```

移除思路：<br>
主要知道了CallOutId直接调用FwpsCalloutUnregisterById函数即可。<br>
也无需<br>
1.设置CalloutEntry的那个成员的标志。<br>
2.设置CalloutEntry位默认的值。<br>
3.设置CalloutEntry（的所有成员）为空。<br>
4.移除这个CalloutEntry，或者inline hook那些函数。<br>
5.更无需调用未导出的FeMoveFilter等函数。ioctlKfdMoveFilter是导出的。

MaxCalloutId的最大值是0x186A0，最小值是0x400.

## 参考：

[https://www.codemachine.com/article_findwfpcallouts.html](https://www.codemachine.com/article_findwfpcallouts.html)

made by correy

[https://correy.webs.com](https://correy.webs.com)
