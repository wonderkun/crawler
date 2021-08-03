> 原文链接: https://www.anquanke.com//post/id/247813 


# 深入理解APC机制


                                阅读量   
                                **21460**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0178b919fb5c17d3b6.jpg)](https://p3.ssl.qhimg.com/t0178b919fb5c17d3b6.jpg)



## 0x00 前言

​ 在平常的渗透测试中，其中主要一项就是对抗杀软检测，需要对shellcode 免杀，而免杀中使用最多的就是APC 注入方式，第一次接触的时候感觉很NB，国内的杀软都能过（即使现在），我就在思考为什么杀软不能检测和拦截到此如此常见的方式，于是就有了此文对APC内部机制的探索。



## 0x01 APC 介绍

​ 1.APC（Asynchronous Procedure Call 异步过程调用）是一种可以在 Windows 中使用的机制，用于将要在特定线程上下文中完成的作业排队。这在几个方面很有用 – 主要用于异步回调 – 安全人员了解 APC 主要是因为恶意软件使用它来将代码注入不同的进程 – 这就是对该机制的滥用。

​ 在内核模式下，开发人员通常不使用 APC，因为 API 没有记录，但是安全人员（包括 rootkit 和 AV 开发人员）使用它从内核驱动程序将他们的代码注入到用户模式进程中。例如，当调用异步 RPC 方法时，您可以指定在 RPC 方法完成时将执行的 APC 队列。这只是一个例子，有很多使用 APC 的机制的例子，比如 NtWriteFile/NtReadFile、IRP 中的 IO 完成、Get/SetThreadContext、SuspendThread、TerminateThread 等等。此外，Windows 的调度程序也使用 APC。这就是为什么我认为理解 APC 对理解 Windows 内部结构很重要。

​ 2.Alertable 状态：要调用APC，线程必须是处于Alertable 状态。那怎么才能让线程处于这个状态呢？很简单，WaitForSingleObjectEx、[SleepEx](https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleepex)等且Alertable=TRUE，它就会变成“Alertable” 状态。执行此操作时，Windows 可能会在从这些函数返回之前将 APC 传送到该线程。这允许程序的开发人员控制可以在程序的哪些部分交付用户 APC。另一个可用于允许挂起 APC 执行的函数是 NtTestAlert。



## 0x02 APC 注入

​ 在实战攻防中如何利用此特性对抗杀软，其实有已经很多代码的例子了C++ 版本[APC-Inject](https://github.com/tomcarver16/APC-Injector/blob/master/apc-inject/apc-inject.cpp)，C# 版本 [APC-inject](https://github.com/pwndizzle/c-sharp-memory-injection/blob/master/apc-injection-new-process.cs)，函数原型：

```
DWORD QueueUserAPC(
  PAPCFUNC  pfnAPC,
  HANDLE    hThread,
  ULONG_PTR dwData
);
```

​ 最常用的一般都是：1.创建一个suspend状态的进程。2.将exp函数插入APC队列。3.resumexx 调用APC队列中的函数。这里第一步中的suspend状态的进程对应的就是Alertable 状态（第一次学习的时候，就在想为什么必须是suspend）。你注入的如果是正常进程的APC，是永远都不会执行的，这里其实是Microsoft 不希望在线程未处于Alertable状态时运行 APC。例如，假设一个线程正在使用LoadLibrary加载一个库，LoadLibrary 接触 PEB 中的加载程序结构并获取锁。假设 APC 的目标地址是 LoadLibrary，这可能会导致问题，因为同一个线程已经在 LoadLibrary 中。



## 0x03 深入APC 内核

​ 内核向队列 APC 公开了 3 个系统调用：NtQueueApcThread、NtQueueApcThreadEx 和 NtQueueApcThreadEx2。QueueUserAPC 是 kernelbase 中的一个封装函数，它调用 NtQueueApcThread。让我们看看此函数原型：

NtQueueApcThread：

```
NTSTATUS
NtQueueApcThread(  
    IN HANDLE ThreadHandle,
    IN PPS_APC_ROUTINE ApcRoutine,
    IN PVOID SystemArgument1 OPTIONAL,
    IN PVOID SystemArgument2 OPTIONAL,
    IN PVOID SystemArgument3 OPTIONAL
    );

typedef 
VOID 
(*PPS_APC_ROUTINE)(
    PVOID SystemArgument1,
    PVOID SystemArgument2,
    PVOID SystemArgument3,
    PCONTEXT ContextRecord
);
```

其中ApcRoutine就是指在目标进程中routine的地址，也就是函数地址。后面三个参数就是对应传入函数的参数值，常见的比如注入加载dll就可以采用如下方式：

```
NtQueueApcThread(
    ThreadHandle,
    GetProcAddress(GetModuleHandle("kernel32"), "LoadLibraryA"),
    RemoteLibraryAddress,
    NULL,
    NULL
);
```

NtQueueApcThreadEx:

​ 每次调用 NtQueueApcThread 时，都会在内核模式下分配一个新的 KAPC 对象来存储有关 APC 对象的数据。因为如果有一个组件将许多 APC排队。这可能会对性能产生影响，因为使用了大量非分页内存，并且分配内存也需要一些时间。所以，在 Windows 7 中，微软向内核模式添加了一个非常简单的对象，称为内存保留对象（memory reserve object.）。它允许在内核模式下为某些对象保留内存，稍后在释放对象时使用相同的内存区域来存储另一个对象，从而减少 ExAllocatePool/ExFreePool 调用的次数。NtQueueApcThreadEx 接收到此类对象的 HANDLE，从而允许调用者重用相同的内存。

```
NTSTATUS
NtQueueApcThreadEx(  
    IN HANDLE ThreadHandle,
    IN HANDLE MemoryReserveHandle,
    IN PPS_APC_ROUTINE ApcRoutine,
    IN PVOID SystemArgument1 OPTIONAL,
    IN PVOID SystemArgument2 OPTIONAL,
    IN PVOID SystemArgument3 OPTIONAL
    );
```

这跟NtQueueApcThread很相似，就是多了MemoryReserveHandle参数，此handle可以由NtAllocateReserveObject获得。

```
NTSTATUS
NtAllocateReserveObject(
    __out PHANDLE MemoryReserveHandle,
    __in_opt POBJECT_ATTRIBUTES ObjectAttributes,
    __in MEMORY_RESERVE_OBJECT_TYPE ObjectType
    );
```

例如示例代码会循环插入APC队列，并且执行会一直输出内容：

```
#include &lt;Windows.h&gt;
#include &lt;stdio.h&gt;
#include &lt;winternl.h&gt;


typedef
VOID
(*PPS_APC_ROUTINE)(
    PVOID SystemArgument1,
    PVOID SystemArgument2,
    PVOID SystemArgument3
    );

typedef
NTSTATUS
(NTAPI* PNT_QUEUE_APC_THREAD_EX)(
    IN HANDLE ThreadHandle,
    IN HANDLE MemoryReserveHandle,
    IN PPS_APC_ROUTINE ApcRoutine,
    IN PVOID SystemArgument1 OPTIONAL,
    IN PVOID SystemArgument2 OPTIONAL,
    IN PVOID SystemArgument3 OPTIONAL
    );

typedef enum _MEMORY_RESERVE_OBJECT_TYPE `{`
    MemoryReserveObjectTypeUserApc,
    MemoryReserveObjectTypeIoCompletion
`}` MEMORY_RESERVE_OBJECT_TYPE, PMEMORY_RESERVE_OBJECT_TYPE;

typedef
NTSTATUS
(NTAPI* PNT_ALLOCATE_RESERVE_OBJECT)(
    __out PHANDLE MemoryReserveHandle,
    __in_opt POBJECT_ATTRIBUTES ObjectAttributes,
    __in ULONG Type
    );

VOID
ExampleApcRoutine(
    PVOID arg1,
    PVOID arg2,
    PVOID arg3
);

PNT_ALLOCATE_RESERVE_OBJECT NtAllocateReserveObject;
PNT_QUEUE_APC_THREAD_EX NtQueueApcThreadEx;

int main(
    int argc,
    const char** argv
)
`{`
    NTSTATUS Status;
    HANDLE MemoryReserveHandle;

    NtQueueApcThreadEx = (PNT_QUEUE_APC_THREAD_EX)GetProcAddress(GetModuleHandle(L"ntdll.dll"), "NtQueueApcThreadEx");
    NtAllocateReserveObject = (PNT_ALLOCATE_RESERVE_OBJECT)GetProcAddress(GetModuleHandle(L"ntdll.dll"), "NtAllocateReserveObject");

    if (!NtQueueApcThreadEx || !NtAllocateReserveObject) `{`
        exit(0x1337);
    `}`

    Status = NtAllocateReserveObject(&amp;MemoryReserveHandle, NULL, MemoryReserveObjectTypeUserApc);

    if (!NT_SUCCESS(Status)) `{`
        printf("NtAllocateReserveObject Failed! 0x%08X\n", Status);
        return -1;
    `}`

    while (TRUE) `{`
        //
        // 添加APC队列到当前线程
        //
        Status = NtQueueApcThreadEx(
            GetCurrentThread(),
            MemoryReserveHandle,
            expfunc,//这里也可以换成LoadLibraryA加载dll
            NULL,
            NULL,
            NULL
        );

        if (!NT_SUCCESS(Status)) `{`
            printf("NtQueueApcThreadEx Failed! 0x%08X\n", Status);
            return -1;
        `}`

        //
        // 执行APC函数
        //
        SleepEx(0, TRUE);
    `}`

    return 0;
`}`

VOID
expfunc(
    PVOID arg1,
    PVOID arg2,
    PVOID arg3
)
`{`
    Sleep(300);

    printf("This is the weird loop!\n");
`}`
```



## 0x04 总结

​ 因为在第一次了解，发现这是一种很好的免杀方式，想知道其内部原理，可以调用内部过程函数，对后面的免杀有了更深的理解。在查找资料中，发现了很多很好的文章思路，总结其APC Windows内部结构，对想理解windows机制的人会有所帮助。
