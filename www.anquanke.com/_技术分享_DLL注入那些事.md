> 原文链接: https://www.anquanke.com//post/id/86671 


# 【技术分享】DLL注入那些事


                                阅读量   
                                **220423**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.deniable.org
                                <br>原文地址：[http://blog.deniable.org/blog/2017/07/16/inject-all-the-things](http://blog.deniable.org/blog/2017/07/16/inject-all-the-things)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t011b2047aa5101086b.jpg)](https://p0.ssl.qhimg.com/t011b2047aa5101086b.jpg)

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：260RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>





在本文中，我们将向读者全面介绍各种DLL注入技术。所谓DLL注入，本来是软件用于向其他程序添加/扩展功能、调试或逆向工程的一种合法技术。不过，后来恶意软件也常用这种方式来干坏事。因此，这意味着从安全的角度来看，我们必须知道DLL注入是如何工作的。

之前，当我开始开发Red Team的定制工具（为了模拟不同类型的攻击者）时，我完成了这个小项目的大部分代码，并将该项目命名为“injectAllTheThings”。如果你想看一些使用DLL注入的具体示例，请访问[这里](https://attack.mitre.org/wiki/Technique/T1055)。如果你想了解DLL注入，该项目也会很有帮助。实际上，我已经在一个单一的Visual Studio项目中组合了多种DLL注入技术（实际上是7种不同的技术），它们都有32位和64位版本，并且非常便于阅读和理解：每种技术都有自己单独的源文件。

以下是该工具的输出，给出了所有已经实现的方法。

[![](https://p0.ssl.qhimg.com/t016765af01a0fe6140.png)](https://p0.ssl.qhimg.com/t016765af01a0fe6140.png)

根据[@SubTee](https://twitter.com/subtee)的说法，DLL注入是“没什么大不了”的。我同意这种观点，但是，DLL注入远不止加载DLL这么简单。

[![](https://p5.ssl.qhimg.com/t0169943eff8fbfaf86.png)](https://p5.ssl.qhimg.com/t0169943eff8fbfaf86.png)

你虽然可以使用经过Microsoft签名的二进制代码来加载DLL，但是却无法附加到某个进程来利用其内存。大多数渗透测试人员实际上不知道什么是DLL注入以及它是如何工作的，主要是因为[Metasploit](https://www.metasploit.com/)可以代劳的事情太多了。他们一直在盲目地使用它。我相信，学习这个“怪异的”内存操纵技术的最佳地点，不是安全论坛，而是黑客论坛。如果你加入了红队，你可能需要鼓捣这种东西，除非你安于使用他人提供的工具。

大多时候，我们首先会使用一项高度复杂的技术展开攻击，如果我们没有被发现，才会开始降低复杂程度。这就是说，我们会先将二进制文件丢到磁盘上，然后使用DLL注入。

这篇文章将全面介绍DLL注入，同时也是[GitHub](https://github.com/fdiskyou/injectAllTheThings)托管的该项目的“帮助文档”。

<br>

**概述**

****

DLL注入简单来说就是将代码插入/注入到正在运行的进程中的过程。我们注入的代码是动态链接库（DLL）的形式。为什么可以做到这一点？因为DLL（如UNIX中的共享库）是在运行时根据需要来进行加载。在这个项目中，我将只使用DLL，但是实际上还可以使用其他各种形式（任何PE文件、shellcode / assembly等）来“注入”代码，这些在恶意软件中非常常见。

此外，请记住，您需要具有适当级别的权限才能鼓捣其他进程的内存。但是，这里不会探讨受和[保护的进程](https://www.microsoftpressstore.com/articles/article.aspx?p=2233328&amp;seqNum=2)、[Windows特权级别](https://msdn.microsoft.com/en-gb/library/windows/desktop/bb648648(v=vs.85).aspx)（由Vista引入）有关的内容——这是一个完全不同的主题。

如上所述，DLL注入可以用于合法目的。例如，防病毒和终端安全解决方案就需要使用这些技术将自己的软件代码/挂钩放置到系统上的“所有”运行的进程中。这使他们能够在运行过程中监视每个进程的行为，从而更好地保护我们。但是，该技术也可以用于恶意的目的。一般来说，常用技术是注入“lsass”进程以获取密码哈希值。恶意软件也广泛使用代码注入技术，例如，运行shellcode、运行PE文件或将DLL加载到另一个进程的内存中以隐藏自身，等等。

<br>

**基础知识**

我们将使用MS Windows API完成各种注入，因为这个API提供了非常丰富的功能，允许我们连接和操纵其他进程。自从微软第一个版本的操作系统以来，DLL一直是MS Windows的基石。事实上，MS Windows 所有API都涉及DLL。最重要的一些DLL有“Kernel32.dll”（其中包含用于管理内存、进程和线程的函数）、“User32.dll”（主要是用户界面函数）和“GDI32.dll”（用于绘制图形和文字显示）。

您可能奇怪为什么会提供这样的API，为什么微软给我们这么好的一套函数来操作进程的内存？实际上，它们的最初用途是扩展应用程序的功能。例如，一家公司创建一个了应用程序，并希望允许其他公司扩展或增强应用程序。所以，DLL最初是用于合法的目的。此外，DLL还可用于项目管理，节省内存，实现资源共享等。

下图讲解DLL注入技术的流程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ff4691c9837d2983.png)

就像上面看到的那样，DLL注入分为四个步骤：

1.附加到目标/远程进程

2.在目标/远程进程内分配内存

3.将DLL路径或DLL复制到目标/远程进程内存中

4.让进程执行DLL

所有这些步骤都是通过调用一组API函数来实现的。每种技术都需要一定的设置和选项才能完成。实际上，每种技术都有自己的优点和缺点。

<br>

**技术详解**

****

我们有多种方法来让进程执行我们的DLL。最常见的方法就是使用“CreateRemoteThread()”和“NtCreateThreadEx()”。但是，我们无法将DLL作为参数传递给这些函数。我们必须提供一个保存执行起始点的内存地址。为此，我们需要完成内存分配，使用“LoadLibrary()”加载我们的DLL，复制内存等等。

这个项目我称之为'injectAllTheThings'（取这个名字，只是因为我讨厌‘injector’的名字，加上GitHub上已经有太多的‘injector’了），它有7种不同的技术。当然，这些技术都不是我发明的。我只是使用了这七种技术（是的，还有更多）。一些API具有详细的文档说明（如“CreateRemoteThread()”），有些API则没有相关的文档说明（如'NtCreateThreadEx()'）。以下是已经实现的技术的完整列表，它们全部适用于32位和64位。

CreateRemoteThread()

NtCreateThreadEx()

QueueUserAPC

SetWindowsHookEx()

RtlCreateUserThread()

通过SetThreadContext()获取代码洞

反射型DLL

其中，可能有一些是你早就接触过的技术。当然，这不是所有DLL注入技术的完整列表。如我所说，还有更多的技术，但是并没有包括在这里。这里给出的，是到目前为止，我在一些项目中使用过的技术。有些是稳定的，有些是不稳定的——当然，之所以不稳定，可能是由于我的代码的原因，而不是这些技术本身的原因。

<br>

**LoadLibrary()**

如[MSDN](https://msdn.microsoft.com/en-us/library/windows/desktop/ms684175(v=vs.85).aspx)所述，“LoadLibrary（）”函数的作用是将指定的模块加载到调用进程的地址空间中。而指定的模块可能会导致加载其他模块。



```
HMODULE WINAPI LoadLibrary(
  _In_ LPCTSTR lpFileName
);
```

lpFileName [in]

The name of the module. This can be either a library module (a .dll file) or an executable module (an .exe file). (…)

If the string specifies a full path, the function searches only that path for the module.

If the string specifies a relative path or a module name without a path, the function uses a standard search strategy to find the module (…) 

If the function cannot find the module, the function fails. When specifying a path, be sure to use backslashes (), not forward slashes (/). (…)

If the string specifies a module name without a path and the file name extension is omitted, the function appends the default library extension .dll to the module name. (…)

换句话说，它只需要一个文件名作为其唯一的参数。也就是说，我们只需要为DLL的路径分配一些内存，并将执行起始点设置为“LoadLibrary()”函数的地址，将路径的内存地址作为参数传递就行了。

实际上，这里最大的问题是“LoadLibrary()”使用程序来将加载的DLL添加到注册表中。意思是它可以轻松被检测到，但是实际上许多终端安全解决方案仍然无法检测到它们。无论如何，正如我之前所说，DLL注入也有合法的使用情况，所以…另外，请注意，如果DLL已经加载了'LoadLibrary()'，它将不会被再次执行。如果使用反射型DLL注入，当然没有这个问题，因为DLL没有被注册。如果使用反射DLL注入技术而不是使用“LoadLibrary()”，会将整个DLL加载到内存中。然后找到DLL的入口点的偏移量来加载它。如果你愿意，还可以设法将其隐藏起来。取证人员仍然可以在内存中找到你的DLL，只是这不会那么容易而已。Metasploit使用了大量的DLL注入，但是大多数终端解决方案都能搞定这一切。如果你喜欢狩猎，或者你属于“蓝队”，可以看看[这里](https://www.defcon.org/html/defcon-20/dc-20-speakers.html#King)和[这里](https://www.defcon.org/html/defcon-20/dc-20-speakers.html#King)。

顺便说一句，如果你的终端安全软件无法搞定所有这一切…你可尝试使用一些[游戏反欺骗引擎](https://www.nostarch.com/gamehacking)。一些反欺诈游戏的反rootkit功能比某些AV更加先进。

<br>

**连接到目标/远程进程**

首先，我们需要得到要与之进行交互的进程的句柄。为此，我们可以使用API调用[OpenProcess()](https://msdn.microsoft.com/en-gb/library/windows/desktop/ms684320(v=vs.85).aspx)。



```
HANDLE WINAPI OpenProcess(
  _In_ DWORD dwDesiredAccess,
  _In_ BOOL  bInheritHandle,
  _In_ DWORD dwProcessId
);
```

如果您阅读MSDN上的文档，就会明白，为此需要具备一定的访问权限。访问权限的完整列表可以在[这里](https://msdn.microsoft.com/en-gb/library/windows/desktop/ms684880(v=vs.85).aspx)找到。

这些可能因MS Windows版本而异，不过几乎所有技术都需要用到以下内容。



```
HANDLE hProcess = OpenProcess(
    PROCESS_QUERY_INFORMATION |
    PROCESS_CREATE_THREAD |
    PROCESS_VM_OPERATION |
    PROCESS_VM_WRITE,
    FALSE, dwProcessId);
```

<br>

**在目标/远程进程内分配内存**

为了给DLL路径分配内存，我们需要使用[VirtualAllocEx()](https://msdn.microsoft.com/en-us/library/windows/desktop/aa366890%28v=vs.85%29.aspx)。如MSDN所述，VirtualAllocEx()可以用来预留、提交或更改指定进程的虚拟地址空间内的内存区域的状态。该函数将其分配的内存初始化为零。



```
LPVOID WINAPI VirtualAllocEx(
  _In_     HANDLE hProcess,
  _In_opt_ LPVOID lpAddress,
  _In_     SIZE_T dwSize,
  _In_     DWORD  flAllocationType,
  _In_     DWORD  flProtect
);
```

我们需要完成类似下面的工作：



```
// calculate the number of bytes needed for the DLL's pathname
DWORD dwSize = (lstrlenW(pszLibFile) + 1) * sizeof(wchar_t);
// allocate space in the target/remote process for the pathname
LPVOID pszLibFileRemote = (PWSTR)VirtualAllocEx(hProcess, NULL, dwSize, MEM_COMMIT, PAGE_READWRITE);
```

此外，您还可以使用“[GetFullPathName()](https://msdn.microsoft.com/en-us/library/windows/desktop/aa364963%28v=vs.85%29.aspx)”API调用。但是，我不会在整个项目中使用这个API调用。不过，这只是个人偏好的问题。

如果要为整个DLL分配空间，则必须执行以下操作：



```
hFile = CreateFileW(pszLibFile, GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
dwSize, = GetFileSize(hFile, NULL);
PVOID pszLibFileRemote = (PWSTR)VirtualAllocEx(hProcess, NULL, dwSize, MEM_COMMIT, PAGE_READWRITE);
```

**<br>**

**将DLL路径或DLL复制到目标/远程进程的内存中**

现在只需要使用[WriteProcessMemory()](https://msdn.microsoft.com/en-us/library/windows/desktop/ms681674%28v=vs.85%29.aspx)API调用将DLL路径或完整的DLL复制到目标/远程进程。



```
BOOL WINAPI WriteProcessMemory(
  _In_  HANDLE  hProcess,
  _In_  LPVOID  lpBaseAddress,
  _In_  LPCVOID lpBuffer,
  _In_  SIZE_T  nSize,
  _Out_ SIZE_T  *lpNumberOfBytesWritten
);
```

这就像：

```
DWORD n = WriteProcessMemory(hProcess, pszLibFileRemote, (PVOID)pszLibFile, dwSize, NULL);
```

如果我们要复制完整的DLL，就像在反射DLL注入技术中那样，则还需要另外一些代码，因为这需要将其读入内存，然后再将其复制到目标/远程进程。



```
lpBuffer = HeapAlloc(GetProcessHeap(), 0, dwLength);
ReadFile(hFile, lpBuffer, dwLength, &amp;dwBytesRead, NULL);
WriteProcessMemory(hProcess, pszLibFileRemote, (PVOID)pszLibFile, dwSize, NULL);
```

如前所述，通过使用反射DLL注入技术，并将DLL复制到内存中，DLL就不会被注册到进程中。

这稍微有点复杂，因为需要在内存中加载DLL时取得它的入口点。作为反射DLL项目用到的“LoadRemoteLibraryR()”函数可以为我们完成这些工作。如果你想查看源码的话，可以访问这里。

需要注意的一点是，我们要注入的DLL需要使用适当的include和options进行编译，使其与ReflectiveDLLInjection方法相适应。'injectAllTheThings'项目包括名为'rdll_32.dll / rdll_64.dll'的DLL，您可以使用它来完成这些工作。

** **

**让进程执行DLL**

**CreateRemoteThread()**

CreateRemoteThread()是一种经典和最受欢迎的DLL注入技术。另外，它的说明文档也是最全面的。

它包括以下步骤：

1.用OpenProcess()打开目标进程

2.通过GetProcAddress()找到LoadLibrary()的地址

3.通过VirtualAllocEx()为目标/远程进程地址空间中的DLL路径预留内存

4.使用WriteProcessMemory()将DLL路径写入前面预留的内存空间中

5.使用CreateRemoteThread()创建一个新线程，该线程将调用LoadLibrary()函数，以DLL路径名称作为参数

如果浏览MSDN上的[CreateRemoteThread()](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682437%28v=vs.85%29.aspx)文档，会发现我们需要一个指向由线程执行的、类型为LPTHREAD_START_ROUTINE的应用程序定义函数的指针，它实际上是远程进程中线程的起始地址。

这意味着为了执行我们的DLL，只需要给我们的进程发出指示，让它来完成就行了。这样就简单了。

完整的步骤如下所示。



```
HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION | PROCESS_VM_WRITE, FALSE, dwProcessId);
// Allocate space in the remote process for the pathname
LPVOID pszLibFileRemote = (PWSTR)VirtualAllocEx(hProcess, NULL, dwSize, MEM_COMMIT, PAGE_READWRITE);
// Copy the DLL's pathname to the remote process address space
DWORD n = WriteProcessMemory(hProcess, pszLibFileRemote, (PVOID)pszLibFile, dwSize, NULL);
// Get the real address of LoadLibraryW in Kernel32.dll
PTHREAD_START_ROUTINE pfnThreadRtn = (PTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle(TEXT("Kernel32")), "LoadLibraryW");
// Create a remote thread that calls LoadLibraryW(DLLPathname)
HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, pfnThreadRtn, pszLibFileRemote, 0, NULL);
```

完整的源代码，请参阅CreateRemoteThread.cpp文件。

**NtCreateThreadEx()**

另一个选择是使用[NtCreateThreadEx()](https://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FNT%20Objects%2FThread%2FNtCreateThread.html)。这是一个未公开的ntdll.dll函数，在将来它可能会消失或发生变化。这种技术实现起来有点复杂，因为我们需要使用一个结构体（见下文）作为参数传递给它，而使用另一个结构体接收来自它的数据。



```
struct NtCreateThreadExBuffer `{`
  ULONG Size;
  ULONG Unknown1;
  ULONG Unknown2;
  PULONG Unknown3;
  ULONG Unknown4;
  ULONG Unknown5;
  ULONG Unknown6;
  PULONG Unknown7;
  ULONG Unknown8;
`}`;
```

[这里](http://securityxploded.com/ntcreatethreadex.php)有一篇对该调用的详细说明。这种方法与CreateRemoteThread()方法比较接近。



```
PTHREAD_START_ROUTINE ntCreateThreadExAddr = (PTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle(TEXT("ntdll.dll")), "NtCreateThreadEx"); 
LPFUN_NtCreateThreadEx funNtCreateThreadEx = (LPFUN_NtCreateThreadEx)ntCreateThreadExAddr;
NTSTATUS status = funNtCreateThreadEx(
  &amp;hRemoteThread,
  0x1FFFFF,
  NULL,
  hProcess,
  pfnThreadRtn,
  (LPVOID)pszLibFileRemote,
  FALSE,
  NULL,
  NULL,
  NULL,
  NULL
  );
```

完整的源代码，请参阅t_NtCreateThreadEx.cpp文件。

**QueueUserAPC()**

对于前面的方法，有一个替代：使用[QueueUserAPC()](https://msdn.microsoft.com/en-us/library/windows/desktop/ms684954%28v=vs.85%29.aspx)函数。

如MSDN所述，这个调用“将用户模式异步过程调用（APC）对象添加到指定线程的APC队列。”

下面是具体定义。



```
DWORD WINAPI QueueUserAPC(
  _In_ PAPCFUNC  pfnAPC,
  _In_ HANDLE    hThread,
  _In_ ULONG_PTR dwData
);
```

pfnAPC [in]

A pointer to the application-supplied APC function to be called when the specified thread performs an alertable wait operation. (…)

hThread [in]

A handle to the thread. The handle must have the THREAD_SET_CONTEXT access right. (…)

dwData [in]

A single value that is passed to the APC function pointed to by the pfnAPC parameter.

所以，如果我们不想创建自己的线程，那么可以使用QueueUserAPC()来劫持目标/远程进程中的现有线程。也就是说，调用此函数将在指定的线程上对异步过程调用进行排队。

我们可以使用真正的APC回调函数代替LoadLibrary()。这里的参数实际上可以指向注入的DLL文件名的指针。

```
DWORD dwResult = QueueUserAPC((PAPCFUNC)pfnThreadRtn, hThread, (ULONG_PTR)pszLibFileRemote);
```

当你尝试这种技术的时候，你可能会注意到，这与MS Windows执行APC的方式有关。但是，这里没有查看APC队列的调度器，这意味着，只有当线程变为可警示状态时，队列才会被检查。

这样，我们就可以劫持每一个线程了，具体如下。

```
BOOL bResult = Thread32First(hSnapshot, &amp;threadEntry);
  while (bResult)
  `{`
    bResult = Thread32Next(hSnapshot, &amp;threadEntry);
    if (bResult)
    `{`
      if (threadEntry.th32OwnerProcessID == dwProcessId)
      `{`
        threadId = threadEntry.th32ThreadID;
 
        wprintf(TEXT("[+] Using thread: %in"), threadId);
        HANDLE hThread = OpenThread(THREAD_SET_CONTEXT, FALSE, threadId);
        if (hThread == NULL)
          wprintf(TEXT("[-] Error: Can't open thread. Continuing to try other threads...n"));
        else
        `{`
          DWORD dwResult = QueueUserAPC((PAPCFUNC)pfnThreadRtn, hThread, (ULONG_PTR)pszLibFileRemote);
          if (!dwResult)
            wprintf(TEXT("[-] Error: Couldn't call QueueUserAPC on thread&gt; Continuing to try othrt threads...n"));
          else
            wprintf(TEXT("[+] Success: DLL injected via CreateRemoteThread().n"));
          CloseHandle(hThread);
        `}`
      `}`
    `}`
  `}`
```

我们这样做，主要是想让一个线程变为可警示状态。

顺便说一句，很高兴看到这种技术被[DOUBLEPULSAR](https://countercept.com/our-thinking/doublepulsar-usermode-analysis-generic-reflective-dll-loader/)应用。

完整的源代码，请参见“t_QueueUserAPC.cpp”文件。

**SetWindowsHookEx()**

为了使用这种技术，我们首先需要了解一下MS Windows钩子的工作原理。简单来说，钩子就是一种拦截事件并采取行动的方式。

你可能会猜到，会有很多不同类型的钩子。其中，最常见的是WH_KEYBOARD和WH_MOUSE。是的，你可能已经猜到了，它们可以用来监控键盘和鼠标的输入。

[SetWindowsHookEx()](https://msdn.microsoft.com/en-us/library/windows/desktop/ms644990%28v=vs.85%29.aspx)的作用是“将应用程序定义的钩子装到钩子链中。”



```
HHOOK WINAPI SetWindowsHookEx(
  _In_ int       idHook,
  _In_ HOOKPROC  lpfn,
  _In_ HINSTANCE hMod,
  _In_ DWORD     dwThreadId
);
```

idHook [in]

Type: int

The type of hook procedure to be installed. (…)

lpfn [in]

Type: HOOKPROC

A pointer to the hook procedure. (…)

hMod [in]

Type: HINSTANCE

A handle to the DLL containing the hook procedure pointed to by the lpfn parameter. (…)

dwThreadId [in]

Type: DWORD

The identifier of the thread with which the hook procedure is to be associated. (…)

MSDN上一个有趣的评论指出：

“SetWindowsHookEx可以用于将DLL注入到另一个进程中。32位DLL不能被注入到64位进程中，同时，64位DLL也不能被注入到32位进程中。如果应用程序需要在其他进程中使用钩子，则需要使用一个32位应用程序调用SetWindowsHookEx将32位DLL注入32位进程中，或者使用64位应用程序调用SetWindowsHookEx来把64位DLL注入64位进程。32位和64位DLL必须具有不同的名称。”

请大家务必记住这一点。

下面是取自具体实现中的一段代码。



```
GetWindowThreadProcessId(targetWnd, &amp;dwProcessId);
HHOOK handle = SetWindowsHookEx(WH_KEYBOARD, addr, dll, threadID);
```

我们需要知道，发生的每个事件都将通过一个钩子链，这是一系列可以在事件中运行的过程。SetWindowsHookExe()要做的基本上就是如何将自己的钩子放入钩子链中。

上面的代码需要用到要安装的钩子类型（WH_KEYBOARD）、指向过程的指针、具有该过程的DLL的句柄以及将要挂钩的线程的ID。

为了获得指向程序的指针，我们需要首先使用LoadLibrary()调用加载DLL。然后，调用[SetWindowsHookEx()](https://wikileaks.org/ciav7p1/cms/page_6062133.html)，并等待我们想要的事件发生（这里而言就是按一个键）。一旦相应的事件发生，我们的DLL就会被执行。

完整的源代码，请参阅t_SetWindowsHookEx.cpp文件。

**RtlCreateUserThread()**

[RtlCreateUserThread()](https://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FExecutable%20Images%2FRtlCreateUserThread.html)是一个未公开的API调用。它的设置几乎与CreateRemoteThread()以及后面介绍的NtCreateThreadE()完全相同。

实际上，RtlCreateUserThread()会调用NtCreateThreadEx()，这意味着RtlCreateUserThread()是NtCreateThreadEx()的封装。所以，这里没有什么新玩意。但是，我们可能只想使用RtlCreateUserThread()，而不是NtCreateThreadEx()。即使后者发生了变动，我们的RtlCreateUserThread()仍然可以正常工作。

我们知道，[mimikatz](http://blog.gentilkiwi.com/mimikatz)和Metasploit都使用[RtlCreateUserThread()](http://blog.gentilkiwi.com/mimikatz)。如果你有兴趣的话，可以看看[这里](https://github.com/gentilkiwi/mimikatz/blob/d5676aa66cb3f01afc373b0a2f8fcc1a2822fd27/modules/kull_m_remotelib.c#L59)和[这里](https://github.com/rapid7/meterpreter/blob/6d43284689240f4261cae44a47f0fb557c1dde27/source/common/arch/win/remote_thread.c)。

所以，如果mimikatz和Metasploit正在使用RtlCreateUserThread()…是的，那些家伙都了解自己的代码…按照他们的“建议”，使用RtlCreateUserThread()——特别是，如果你打算鼓捣一些比简单的“injectAllTheThings”程序更复杂的事情的时候。

完整的源代码，请参阅t_RtlCreateUserThread.cpp。

**SetThreadContext()**

这实际上是一个很酷的方法。通过在目标/远程进程中分配一大块内存，以便将特制代码注入目标/远程进程。而该代码是负责加载DLL的。

下面给出的是32位的代码。



```
0x68, 0xCC, 0xCC, 0xCC, 0xCC,   // push 0xDEADBEEF (placeholder for return address)
0x9c,                           // pushfd (save flags and registers)
0x60,                           // pushad
0x68, 0xCC, 0xCC, 0xCC, 0xCC,   // push 0xDEADBEEF (placeholder for DLL path name)
0xb8, 0xCC, 0xCC, 0xCC, 0xCC,   // mov eax, 0xDEADBEEF (placeholder for LoadLibrary)
0xff, 0xd0,                     // call eax (call LoadLibrary)
0x61,                           // popad (restore flags and registers)
0x9d,                           // popfd
0xc3                            // ret
```

对于64位代码，没有找到任何可用的代码，只好自己动手了，具体如下。



```
0x50,                                                       // push rax (save rax)
0x48, 0xB8, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, // mov rax, 0CCCCCCCCCCCCCCCCh (placeholder for return address)
0x9c,                                                       // pushfq
0x51,                                                       // push rcx
0x52,                                                       // push rdx
0x53,                                                       // push rbx
0x55,                                                       // push rbp
0x56,                                                       // push rsi
0x57,                                                       // push rdi
0x41, 0x50,                                                 // push r8
0x41, 0x51,                                                 // push r9
0x41, 0x52,                                                 // push r10
0x41, 0x53,                                                 // push r11
0x41, 0x54,                                                 // push r12
0x41, 0x55,                                                 // push r13
0x41, 0x56,                                                 // push r14
0x41, 0x57,                                                 // push r15
0x68,0xef,0xbe,0xad,0xde,                                   // fastcall convention
0x48, 0xB9, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, // mov rcx, 0CCCCCCCCCCCCCCCCh (placeholder for DLL path name)
0x48, 0xB8, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, // mov rax, 0CCCCCCCCCCCCCCCCh (placeholder for LoadLibrary)
0xFF, 0xD0,                                                 // call rax (call LoadLibrary)
0x58,                                                       // pop dummy
0x41, 0x5F,                                                 // pop r15
0x41, 0x5E,                                                 // pop r14
0x41, 0x5D,                                                 // pop r13
0x41, 0x5C,                                                 // pop r12
0x41, 0x5B,                                                 // pop r11
0x41, 0x5A,                                                 // pop r10
0x41, 0x59,                                                 // pop r9
0x41, 0x58,                                                 // pop r8
0x5F,                                                       // pop rdi
0x5E,                                                       // pop rsi
0x5D,                                                       // pop rbp
0x5B,                                                       // pop rbx
0x5A,                                                       // pop rdx
0x59,                                                       // pop rcx
0x9D,                                                       // popfq
0x58,                                                       // pop rax
0xC3                                                        // ret
```

在将这个代码注入目标进程之前，需要填充/修补一些占位符： 

返回地址（代码完成执行后线程应该恢复的地址）。

DLL路径名。

LoadLibrary()的地址。

接下来就是劫持、暂停、注入和恢复线程发挥作用的时候。

我们首先需要连接到目标/远程进程，并将内存分配到目标/远程进程中。请注意，我们需要分配具有读取和写入权限的内存来保存DLL路径名，以及存放加载DLL的汇编代码。



```
LPVOID lpDllAddr = VirtualAllocEx(hProcess, NULL, dwSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
stub = VirtualAllocEx(hProcess, NULL, stubLen, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
```

接下来，我们需要获得在目标/远程进程上运行的一个线程的上下文（将要注入我们的汇编代码的线程）。

为找到线程，我们可以使用函数getThreadID()，它位于‘auxiliary.cpp’中。

一旦我们获得了线程id，就可以设置线程上下文了。

```
hThread = OpenThread((THREAD_GET_CONTEXT | THREAD_SET_CONTEXT | THREAD_SUSPEND_RESUME), false, threadID);
```

接下来，我们需要暂停线程来捕获其上下文。线程的上下文实际上就是其寄存器的状态。我们特别感兴趣的寄存器是EIP / RIP（有时称为IP指令指针）。

由于线程被暂停，所以我们可以更改EIP / RIP的值，并强制它继续在不同的路径（我们的代码洞）中执行。



```
ctx.ContextFlags = CONTEXT_CONTROL;
GetThreadContext(hThread, &amp;ctx);
DWORD64 oldIP = ctx.Rip;
ctx.Rip = (DWORD64)stub;
ctx.ContextFlags = CONTEXT_CONTROL;
WriteProcessMemory(hProcess, (void *)stub, &amp;sc, stubLen, NULL); // write code cave
SetThreadContext(hThread, &amp;ctx);
ResumeThread(hThread);
```

所以，我们暂停线程，捕获上下文，从中提取EIP / RIP。当我们注入的代码运行完成时，保存的这些数据将用来恢复现场。新的EIP / RIP设置为我们注入的代码位置。

然后我们使用返回地址、DLL路径名地址和LoadLibrary()地址对所有占位符进行填补。

一旦线程开始执行，我们的DLL将被加载，它一旦运行完成，将返回到被挂起的位置，并在那里恢复执行。

如果你想练习调试的话，这里有具体的操作指南。启动要注入的应用程序，如notepad.exe。运行injectAllTheThings_64.exe与x64dbg，如下所示。

[![](https://p2.ssl.qhimg.com/t016f430e3e32eafac3.png)](https://p2.ssl.qhimg.com/t016f430e3e32eafac3.png)

也就是说，我们可以使用以下命令行（具体视您的环境而定）：

```
"C:UsersruiDocumentsVisual Studio 2013ProjectsinjectAllTheThingsbininjectAllTheThings_64.exe" -t 6 notepad.exe "c:UsersruiDocumentsVisual Studio 2013ProjectsinjectAllTheThingsbindllmain_64.dll"
```

在调用WriteProcessMemory()处设置断点，如下所示。

[![](https://p0.ssl.qhimg.com/t01211a0986f8be0fe4.png)](https://p0.ssl.qhimg.com/t01211a0986f8be0fe4.png)

         

当代码运行时，断点触发，这时要注意寄存器RDX的内存地址。至于为什么要关注RDX，可以阅读x64调用约定方面的资料。

[![](https://p1.ssl.qhimg.com/t01cb123f3f25a95e8c.png)](https://p1.ssl.qhimg.com/t01cb123f3f25a95e8c.png)

利用单步方式（F8）调用WriteProcessMemory()，启动x64dbg的另一个实例，并连接到'notepad.exe'。转到以前复制的地址（RDX中的地址），按“Ctrl + g”，您将看到我们的代码，如下所示。

[![](https://p0.ssl.qhimg.com/t01515e1bf77a7c9c28.png)](https://p0.ssl.qhimg.com/t01515e1bf77a7c9c28.png)

太棒了！ 现在，请在这个shellcode的开头设置一个断点。转到被调试进程的injectAllTheThings，让它运行。正如在下面看到的，我们的断点触发，现在可以单步调试代码，进行仔细研究了。

[![](https://p0.ssl.qhimg.com/t012b550b4dc04de29f.png)](https://p0.ssl.qhimg.com/t012b550b4dc04de29f.png)

一旦调用LoadLibrary()了函数，就可以加载我们的DLL了。

[![](https://p5.ssl.qhimg.com/t01549dce113bb97186.png)](https://p5.ssl.qhimg.com/t01549dce113bb97186.png)

这真是太好了。

我们的shellcode将返回到之前保存的RIP的地址处，notepad.exe将恢复执行。

完整的源代码，请参阅t_suspendInjectResume.cpp。

**反射型DLL注射**

我还将Stephen Fewer（这种技术的先驱）代码引入了这个“injectAllTheThings”项目，此外，我还构建了一个反射型DLL项目使用这种技术。请注意，我们正在注入的DLL必须使用适当的include和options进行编译。

由于反射型DLL注入会将整个DLL复制到内存中，因此避免了使用进程注册DLL。我们已经完成了一切繁重的工作。要在DLL中加载内存时获取入口点，只需使用Stephen Fewer的代码即可。他的项目中包含的“LoadRemoteLibraryR（）”函数为我们完成了这些工作。我们使用GetReflectiveLoaderOffset（）来确定我们进程内存中的偏移量，然后使用该偏移加上目标/远程进程（我们写入DLL的位置）中的内存的基地址作为执行起始点。

有点太复杂了？是的，确实如此。下面是实现这一目标的4个主要步骤。

1.将DLL头写入内存

2.将每个节写入内存（通过解析节表）

3.检测import并加载所有其他已导入的DLL

4.调用DllMain入口点

与其他方法相比，这种技术提供了强大的隐蔽性，并在Metasploit中大量应用。

如果你想了解更多详情，请访问官方的[GitHub信息库](https://github.com/stephenfewer/ReflectiveDLLInjection)。此外，请务必阅读[Stephen Fewer的文章](http://www.harmonysecurity.com/files/HS-P005_ReflectiveDllInjection.pdf)。

另外，最好读一下[MemoryModule](https://github.com/fancycode/MemoryModule/)的作者Joachim Bauch写的一篇[文章](https://www.joachim-bauch.de/tutorials/loading-a-dll-from-memory/)，讲述了如何从内存加载一个DLL，同时，这也是在没有LoadLibrary（）的情况下[手动加载Win32 / 64 DLL的好方法](https://www.codeproject.com/Tips/430684/Loading-Win-DLLs-manually-without-LoadLibrary)。

<br>

**代码**

当然，还有一些复杂的注入方法，所以后面还会更新injectAllTheThings项目。我最近看到的最有趣的一些是：

[DOUBLEPULSAR](https://countercept.com/our-thinking/doublepulsar-usermode-analysis-generic-reflective-dll-loader/)使用的一种方法

由[@zerosum0x0](https://twitter.com/zerosum0x0)编写的，使用SetThreadContext()和[NtContinue()](https://zerosum0x0.blogspot.co.uk/2017/07/threadcontinue-reflective-injection.html)的反射型DLL注入技术，此处提供了可用的[代码](https://github.com/zerosum0x0/ThreadContinue)。

我上面描述的所有技术都是我在[GitHub](https://github.com/fdiskyou/injectAllTheThings/)上提供的一个项目中已经实现的。此外，我还提供了每种技术所需的DLL。下表可以了解实际实现的内容以及使用方法。

[![](https://p5.ssl.qhimg.com/t01d602d0cc9db1fbf2.png)](https://p5.ssl.qhimg.com/t01d602d0cc9db1fbf2.png)

不用说，为了安全起见，最好始终使用injectAllTheThings_32.exe注入32位进程或使用AllTheThings_64.exe注入64位进程。当然，您也可以使用injectAllTheThings_64.exe注入32位进程。其实我还没有实现这一点，但是我可能稍后会再试一次，你可以试着用[WoW64](http://blog.rewolf.pl/blog/?p=102)鼓捣一下64位进程。Metasploit的smart_migrate基本上就是这种情况，具体请看[这里](https://github.com/rapid7/meterpreter/blob/5e24206d510a48db284d5f399a6951cd1b4c754b/source/common/arch/win/i386/base_inject.c)。

本文涉及的整个项目的所有代码，包括DLL，都可从[GitHub](https://github.com/fdiskyou/injectAllTheThings/)下载。当然，如果您有兴致的话，也可以自己试着编译32位和64位代码。
