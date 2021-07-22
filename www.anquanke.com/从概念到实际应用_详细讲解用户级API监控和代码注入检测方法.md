> 原文链接: https://www.anquanke.com//post/id/98770 


# 从概念到实际应用：详细讲解用户级API监控和代码注入检测方法


                                阅读量   
                                **714568**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者dtm，文章来源：0x00sec.org
                                <br>原文地址：[https://0x00sec.org/t/userland-api-monitoring-and-code-injection-detection/5565](https://0x00sec.org/t/userland-api-monitoring-and-code-injection-detection/5565)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01d12fb20dc32ea9bb.png)](https://p2.ssl.qhimg.com/t01d12fb20dc32ea9bb.png)



## 一、前言

在当今，网络犯罪分子致力于开发恶意软件，并用于感染主机以执行特定的活动。考虑到目前反病毒软件能力的不断提升，这些恶意软件也必须保持较强的存活能力，必须要在暗中进行操作，以避免被反病毒软件和系统管理员觉察。在众多方法之中，代码注入是一个保证隐蔽性的较好方法。<br>
本文主要描述恶意软件及其与Windows应用程序编程接口（WinAPI）交互的相关研究成果，详细介绍恶意软件是如何将恶意Payload植入其他进程，以及如何通过监控Windows操作系统的通信来检测此类行为。关于监控API调用的这一概念，在本文中也将会通过对特定函数进行Hook的过程来向大家展现，并且该概念将用于实现代码注入。<br>
由于时间有限，我们以非常快的速度完成了该项目的研究，因此如果本文中有任何疏漏或错误之处，希望大家能够谅解，并期待各位的指正。此外，本文附带的代码可能会存在一些未知的设计缺陷，请各位自行参考。



## 二、相关概念

### <a class="reference-link" name="2.1%20Inline%20Hooking"></a>2.1 Inline Hooking

内联挂钩（Inline Hooking）是通过热补丁（Hotpatching）的方式绕开代码流的行为。在这里，热补丁是指在可执行映像运行期间对代码进行修改。之所以使用内联挂钩的方式，是为了能够捕获程序在何时调用函数的实例，以进行监控或实现调用。以下是一次函数调用正常执行的过程：

```
Normal Execution of a Function Call

+---------+                                                                       +----------+
| Program | ----------------------- calls function -----------------------------&gt; | Function |  | execution
+---------+                                                                       |    .     |  | of
                                                                                  |    .     |  | function
                                                                                  |    .     |  |
                                                                                  |          |  v
                                                                                  +----------+
```

与执行一个挂钩后的函数相比：

```
Execution of a Hooked Function Call

+---------+                       +--------------+                    + -------&gt;  +----------+
| Program | -- calls function --&gt; | Intermediate | | execution        |           | Function |  | execution
+---------+                       |   Function   | | of             calls         |    .     |  | of
                                  |       .      | | intermediate   normal        |    .     |  | function
                                  |       .      | | function      function       |    .     |  |
                                  |       .      | v                  |           |          |  v
                                  +--------------+  ------------------+           +----------+
```

该过程可以分为三个步骤。我们在这里，以WinAPI函数MessageBox为例，演示此过程。<br>
(1) 对函数进行挂钩<br>
想要挂钩（Hook）函数，我们首先需要一个中间函数，它必须能够复制目标函数的参数。在MSDN中对MessageBox的定义如下：

```
int WINAPI MessageBox(
    _In_opt_ HWND    hWnd,
    _In_opt_ LPCTSTR lpText,
    _In_opt_ LPCTSTR lpCaption,
    _In_     UINT    uType
);
```

所以，我们的中间函数可以这样定义：

```
int WINAPI HookedMessageBox(HWND hWnd, LPCTSTR lpText, LPCTSTR lpCaption, UINT uType) `{`
    // our code in here
`}`
```

一旦存在，执行流就会重定向到代码中的特定位置。如果想要真正对MessageBox函数进行挂钩，我们可以修补代码的前几个字节（请注意，必须要对原始字节进行记录，以便在中间函数完成时能够恢复该函数）。以下是该函数的原始汇编指令，如该函数的相应模块user32.dll中所示：

```
; MessageBox
8B FF   mov edi, edi
55      push ebp
8B EC   mov ebp, esp
```

与挂钩后的函数相比：

```
; MessageBox
68 xx xx xx xx  push &lt;HookedMessageBox&gt; ; our intermediate function
C3              ret
```

在这里，我选择了PUSH和RET的组合，而没有选择JMP，这是基于我之前的经验，前者会有更强的隐蔽性。其中的xx xx xx xx表示HookedMessageBox的小字节序顺序地址（Little-Endian Byte-Order Address）。<br>
(2) 捕获函数调用<br>
当程序调用MessageBox时，它将执行PUSH-RET并会成功跳入HookedMessageBox函数。一旦完成，程序就会完全控制参数和调用本身。如果想替换在消息对话框中所显示的文本，可以在HookedMessageBox中定义如下内容：

```
int WINAPI HookedMessageBox(HWND hWnd, LPCTSTR lpText, LPCTSTR lpCaption, UINT uType) `{`
    TCHAR szMyText[] = TEXT("This function has been hooked!");
`}`
```

其中，szMyText可以用来替换MessageBox的LPCTSTR lpText参数。<br>
(3) 恢复正常执行<br>
要转发此参数，执行过程需要回到原始的MessageBox，以让操作系统可以显示该对话框。如果现在再次调用MessageBox，会导致无限递归（死循环），因此我们必须要恢复原始字节（如前所述）。

```
int WINAPI HookedMessageBox(HWND hWnd, LPCTSTR lpText, LPCTSTR lpCaption, UINT uType) `{`
    TCHAR szMyText[] = TEXT("This function has been hooked!");

    // restore the original bytes of MessageBox
    // ...

    // continue to MessageBox with the replaced parameter and return the return value to the program
    return MessageBox(hWnd, szMyText, lpCaption, uType);
`}`
```

如果需要拒绝调用MessageBox，方法也非常简单，就像返回一个值一样，但这个值最好是在文档中定义过的。例如，想要从”是/否”对话框中返回”否”选项的值，其中间函数可以是：

```
int WINAPI HookedMessageBox(HWND hWnd, LPCTSTR lpText, LPCTSTR lpCaption, UINT uType) `{`
    return IDNO;  // IDNO defined as 7
`}`
```

### <a class="reference-link" name="2.2%20API%E7%9B%91%E6%8E%A7"></a>2.2 API监控

在了解函数挂钩以后，我们紧接着讲解API监控的概念。我们有能力获得对函数调用的控制，同时也可以对所有参数进行监控，也就是标题所说的API监控。但是，还存在一个小问题，是由不同级别的API调用可用性导致的，尽管这些调用是唯一的，但在较低级别会使用相同的一组API。这就称为函数包装（Function Wrapping），定义为用于调用次级子程序的子程序。让我们回到MessageBox的示例，其中有两个定义的函数：MessageBoxA用于包含ASCII字符的参数，MessageBoxW用于包含宽字符的参数。实际上，如果我们要对MessageBox进行挂钩，就必须要同时修补MessageBoxA和MessageBoxW。要解决这一问题，我们需要尽可能在函数调用层次（Call Hierarchy）结构的最低公共点位置进行挂钩。

```
+---------+
                                                      | Program |
                                                      +---------+
                                                     /           
                                                    |             |
                                            +------------+   +------------+
                                            | Function A |   | Function B |
                                            +------------+   +------------+
                                                    |             |
                                           +-------------------------------+
                                           | user32.dll, kernel32.dll, ... |
                                           +-------------------------------+
       +---------+       +-------- hook -----------------&gt; |
       |   API   | &lt;---- +              +-------------------------------------+
       | Monitor | &lt;-----+              |              ntdll.dll              |
       +---------+       |              +-------------------------------------+
                         +-------- hook -----------------&gt; |                           User mode
                                 -----------------------------------------------------
                                                                                       Kernel mode

```

以下是MessageBox调用层次结构：

```
MessageBoxA：
user32!MessageBoxA -&gt; user32!MessageBoxExA -&gt; user32!MessageBoxTimeoutA -&gt; user32!MessageBoxTimeoutW
MessageBoxW：
user32!MessageBoxW -&gt; user32!MessageBoxExW -&gt; user32!MessageBoxTimeoutW
```

上述的调用层次，都将汇入MessageBoxTimeoutW，这是一个挂钩的绝佳位置。在这里要特别指出，对于具有更深层次结构的函数，由于函数参数的复杂程度有所增加，对较低位置的值进行挂钩可能会产生一些问题。MessageBoxTimeoutW是一个没有出现在文档中的WinAPI函数（Undocumented WinAPI Function），其定义如下：

```
int WINAPI MessageBoxTimeoutW(
    HWND hWnd, 
    LPCWSTR lpText, 
    LPCWSTR lpCaption, 
    UINT uType, 
    WORD wLanguageId, 
    DWORD dwMilliseconds
);
```

其用法如下：

```
int WINAPI MessageBoxTimeoutW(HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType, WORD wLanguageId, DWORD dwMilliseconds) `{`
    std::wofstream logfile;     // declare wide stream because of wide parameters
    logfile.open(L"log.txt", std::ios::out | std::ios::app);

    logfile &lt;&lt; L"Caption: " &lt;&lt; lpCaption &lt;&lt; L"n";
    logfile &lt;&lt; L"Text: " &lt;&lt; lpText &lt;&lt; L"n";
    logfile &lt;&lt; L"Type: " &lt;&lt; uType &lt;&lt; :"n";

    logfile.close();

    // restore the original bytes
    // ...

    // pass execution to the normal function and save the return value
    int ret = MessageBoxTimeoutW(hWnd, lpText, lpCaption, uType, wLanguageId, dwMilliseconds);

    // rehook the function for next calls
    // ...

    return ret;   // return the value of the original function
`}`
```

当挂钩被放入MessageBoxTimeoutW中之后，MessageBoxA和MessageBoxW就都可以被捕获了。

### <a class="reference-link" name="2.3%20%E4%BB%A3%E7%A0%81%E6%B3%A8%E5%85%A5%E5%85%A5%E9%97%A8"></a>2.3 代码注入入门

就本文而言，我们所讲解的”代码注入”是指将可执行代码插入到外部进程中。在WinAPI中，允许了一些功能，从而让代码注入成为了可能。在某些函数的共同作用下，我们可以访问现有进程，向其中写入数据，并且在其上下文中进行远程执行。在本节中，我们将介绍研究中涉及到的相关代码注入技术。

#### <a class="reference-link" name="2.3.1%20DLL%E6%B3%A8%E5%85%A5"></a>2.3.1 DLL注入

关于代码注入，代码可以是各种形式，其中之一就是动态链接库（DLL）。DLL是用来为可执行程序提供扩展功能的库，通过导出子程序的方式我们就可以使用该程序。下面是一个DLL示例，下文中都将以此为例：

```
extern "C" void __declspec(dllexport) Demo() `{`
    ::MessageBox(nullptr, TEXT("This is a demo!"), TEXT("Demo"), MB_OK);
`}`

bool APIENTRY DllMain(HINSTANCE hInstDll, DWORD fdwReason, LPVOID lpvReserved) `{`
    if (fdwReason == DLL_PROCESS_ATTACH)
        ::CreateThread(nullptr, 0, (LPTHREAD_START_ROUTINE)Demo, nullptr, 0, nullptr);
    return true;
`}`
```

当一个DLL被加载到进程并初始化时，加载程序将会调用Dllmain，并将fdwReason设置为DLL_PROCESS_ATTACH。在这个例子中，当它被加载到进程中时，会通过Demo子例程来显示一个消息框，其标题为”Demo”，文本内容为”This is a demo!”。要正确完成DLL的初始化，它必须返回True，否则就会被卸载。<br>
2.3.1.1 CreateRemoteThread<br>
通过CreateRemoteThread函数的DLL注入会利用此函数在另一个进程的虚拟空间中执行远程线程（Remote Thread）。如上所述，我们要执行DLL，只需要通过强制执行LoadLibrary函数来将其加载到进程中。以下代码可以完成此操作：

```
void injectDll(const HANDLE hProcess, const std::string dllPath) `{`
    LPVOID lpBaseAddress = ::VirtualAllocEx(hProcess, nullptr, dllPath.length(), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    ::WriteProcessMemory(hProcess, lpBaseAddress, dllPath.c_str(), dllPath.length(), &amp;dwWritten);

    HMODULE hModule = ::GetModuleHandle(TEXT("kernel32.dll"));

    LPVOID lpStartAddress = ::GetProcAddress(hModule, "LoadLibraryA");      // LoadLibraryA for ASCII string

    ::CreateRemoteThread(hProcess, nullptr, 0, (LPTHREAD_START_ROUTINE)lpStartAddress, lpBaseAddress, 0, nullptr);
`}`
```

在MSDN中，对LoadLibrary的定义如下：

```
HMODULE WINAPI LoadLibrary(
    _In_ LPCTSTR lpFileName
);
```

该定义使用了一个参数，即要加载的所需库的路径名称。CreateRemoteThread函数允许将一个参数传递到与LoadLibrary的函数定义完全匹配的线程例程。其目标是在目标进程的虚拟地址空间中分配字符串参数，然后将分配的空间地址传递给CreateRemoteThread的参数中，以便调用LoadLibrary来加载DLL。<br>
(1) 在目标进程中分配虚拟内存<br>
使用VirtualAllocEx可以允许在选定的进程哪分配空间，一旦成功，会返回分配内存的起始地址。

```
Virtual Address Space of Target Process
                                              +--------------------+
                                              |                    |
                        VirtualAllocEx        +--------------------+
                        Allocated memory ---&gt; |     Empty space    |
                                              +--------------------+
                                              |                    |
                                              +--------------------+
                                              |     Executable     |
                                              |       Image        |
                                              +--------------------+
                                              |                    |
                                              |                    |
                                              +--------------------+
                                              |    kernel32.dll    |
                                              +--------------------+
                                              |                    |
                                              +--------------------+
```

(2) 将DLL路径写入分配的内存<br>
一旦内存被初始化，DLL的路径可以被注入到VirtualAllocEx使用WriteProcessMemory返回的分配内存中。

```
Virtual Address Space of Target Process
                                              +--------------------+
                                              |                    |
                        WriteProcessMemory    +--------------------+
                        Inject DLL path ----&gt; | "....myDll.dll"  |
                                              +--------------------+
                                              |                    |
                                              +--------------------+
                                              |     Executable     |
                                              |       Image        |
                                              +--------------------+
                                              |                    |
                                              |                    |
                                              +--------------------+
                                              |    kernel32.dll    |
                                              +--------------------+
                                              |                    |
                                              +--------------------+
```

(3) 获取LoadLibrary的地址<br>
由于所有系统DLL都映射到所有进程的相同地址空间，因此LoadLibrary的地址不必直接从目标进程中检索，只需调用GetModuleHandle(TEXT(“kernel32.dll”))和GetProcAddress(hModule, “LoadLibraryA”)即可完成这项工作。<br>
(4) 加载DLL<br>
如果要加载DLL，就需要LoadLibrary的地址和DLL的路径。此时使用CreateRemoteThread函数，LoadLibrary会在目标进程的上下文中以DLL路径作为参数执行。

```
Virtual Address Space of Target Process
                                              +--------------------+
                                              |                    |
                                              +--------------------+
                                   +--------- | "....myDll.dll"  |
                                   |          +--------------------+
                                   |          |                    |
                                   |          +--------------------+ &lt;---+
                                   |          |     myDll.dll      |     |
                                   |          +--------------------+     |
                                   |          |                    |     | LoadLibrary
                                   |          +--------------------+     | loads
                                   |          |     Executable     |     | and
                                   |          |       Image        |     | initialises
                                   |          +--------------------+     | myDll.dll
                                   |          |                    |     |
                                   |          |                    |     |
          CreateRemoteThread       v          +--------------------+     |
          LoadLibraryA("....myDll.dll") --&gt; |    kernel32.dll    | ----+
                                              +--------------------+
                                              |                    |
                                              +--------------------+
```

2.3.1.2 SetWindowsHookEx<br>
在Windows中，通过SetWindowsHookEx函数为开发人员提供了通过安装钩子来监视某些事件的功能。虽然这一功能经常被用于监控键盘输入并记录，但它其实也能用于注入DLL。以下代码演示了如何向其自身注入DLL：

```
int main() `{`
    HMODULE hMod = ::LoadLibrary(DLL_PATH);
    HOOKPROC lpfn = (HOOKPROC)::GetProcAddress(hMod, "Demo");
    HHOOK hHook = ::SetWindowsHookEx(WH_GETMESSAGE, lpfn, hMod, ::GetCurrentThreadId());
    ::PostThreadMessageW(::GetCurrentThreadId(), WM_RBUTTONDOWN, (WPARAM)0, (LPARAM)0);

    // message queue to capture events
    MSG msg;
    while (::GetMessage(&amp;msg, nullptr, 0, 0) &gt; 0) `{`
        ::TranslateMessage(&amp;msg);
        ::DispatchMessage(&amp;msg);
    `}`

    return 0;
`}`
```

MSDN中定义的SetWindowsHookEx如下：

```
HHOOK WINAPI SetWindowsHookEx(
    _In_ int       idHook,
    _In_ HOOKPROC  lpfn,
    _In_ HINSTANCE hMod,
    _In_ DWORD     dwThreadId
);
```

在这里，需要一个HOOKPROC参数，该参数是触发特定挂钩事件时执行的用户定义的回调子例程。在这种情况下，事件是WH_GETMESSAGE，它负责处理消息队列中的消息。该代码最初将DLL加载到其自身的虚拟进程空间中，并且导出的Demo函数的地址将被获取并定义为调用SetWindowsHookEx中的回调函数。为了强制回调函数执行，使用了消息WM_RBUTTONDOWN调用PostThreadMessage，这样就能触发WH_GETMESSAGE钩子，从而显示消息框。<br>
2.3.1.3 QueueUserAPC<br>
使用QueueUserAPC的DLL注入与CreateRemoteThread类似，都是分配DLL路径并注入到目标进程的虚拟地址空间，然后在其上下文中强制调用LoadLibrary。

```
int injectDll(const std::string dllPath, const DWORD dwProcessId, const DWORD dwThreadId) `{`
    HANDLE hProcess = ::OpenProcess(PROCESS_ALL_ACCESS, false, dwProcessId);

    HANDLE hThread = ::OpenThread(THREAD_ALL_ACCESS, false, dwThreadId);

    LPVOID lpLoadLibraryParam = ::VirtualAllocEx(hProcess, nullptr, dllPath.length(), MEM_COMMIT, PAGE_READWRITE);

    ::WriteProcessMemory(hProcess, lpLoadLibraryParam, dllPath.data(), dllPath.length(), &amp;dwWritten);

    ::QueueUserAPC((PAPCFUNC)::GetProcAddress(::GetModuleHandle(TEXT("kernel32.dll")), "LoadLibraryA"), hThread, (ULONG_PTR)lpLoadLibraryParam);

    return 0;
`}`
```

其与CreateRemoteThread之间的一个主要区别是，QueueUserAPC能在可报警状态（Alertable State）下运行。由QueueUserAPC进行排队的异步过程仅在线程进入此状态时才进行处理。

#### <a class="reference-link" name="2.3.2%20Process%20Hollowing"></a>2.3.2 Process Hollowing

Process Hollowing，也称RunPE，适用于逃避反病毒检测的一种常用方式。该方式允许将整个可执行文件的注入部分加载到目标进程中，并在其上下文中执行。通常我们可以在加密的应用程序中看到，与Payload相兼容的磁盘上文件会被选为主文件，并创建为进程，其主要可执行模块会被替换。该过程可以分为下述四个阶段。<br>
(1) 创建主进程<br>
为了注入Payload，引导程序必须会首先找到合适的主文件。如果Payload是.NET应用程序，那么主文件也必须是.NET应用程序。如果Payload是定义为使用控制台子系统的本地可执行文件，那么主文件也必须有相同的属性。这一原则在x86和x64程序时都要满足。一旦选择了主文件，随后便会使用CreateProcess(PATH_TO_HOST_EXE, …, CREATE_SUSPENDED, …)将其作为挂起的进程创建。

```
Executable Image of Host Process
                                        +---  +--------------------+
                                        |     |         PE         |
                                        |     |       Headers      |
                                        |     +--------------------+
                                        |     |       .text        |
                                        |     +--------------------+
                          CreateProcess +     |       .data        |
                                        |     +--------------------+
                                        |     |         ...        |
                                        |     +--------------------+
                                        |     |         ...        |
                                        |     +--------------------+
                                        |     |         ...        |
                                        +---  +--------------------+

```

(2) 对主进程的Hollowing<br>
为了让Payload能在注入后正常工作，必须要将其映射到虚拟地址空间，该虚拟地址空间要与在Payload PE头部的可选头中找到的ImageBase值相匹配。

```
typedef struct _IMAGE_OPTIONAL_HEADER `{`
  WORD                 Magic;
  BYTE                 MajorLinkerVersion;
  BYTE                 MinorLinkerVersion;
  DWORD                SizeOfCode;
  DWORD                SizeOfInitializedData;
  DWORD                SizeOfUninitializedData;
  DWORD                AddressOfEntryPoint;          // &lt;---- this is required later
  DWORD                BaseOfCode;
  DWORD                BaseOfData;
  DWORD                ImageBase;                    // &lt;---- 
  DWORD                SectionAlignment;
  DWORD                FileAlignment;
  WORD                 MajorOperatingSystemVersion;
  WORD                 MinorOperatingSystemVersion;
  WORD                 MajorImageVersion;
  WORD                 MinorImageVersion;
  WORD                 MajorSubsystemVersion;
  WORD                 MinorSubsystemVersion;
  DWORD                Win32VersionValue;
  DWORD                SizeOfImage;                  // &lt;---- size of the PE file as an image
  DWORD                SizeOfHeaders;
  DWORD                CheckSum;
  WORD                 Subsystem;
  WORD                 DllCharacteristics;
  DWORD                SizeOfStackReserve;
  DWORD                SizeOfStackCommit;
  DWORD                SizeOfHeapReserve;
  DWORD                SizeOfHeapCommit;
  DWORD                LoaderFlags;
  DWORD                NumberOfRvaAndSizes;
  IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
`}` IMAGE_OPTIONAL_HEADER, *PIMAGE_OPTIONAL_HEADER;
```

这一点非常重要，因为绝对地址很可能完全依赖于其内存位置的代码。为了安全地映射可执行映像，必须从描述的ImageBase值开始的虚拟内存空间取消映射。由于许多可执行文件都会使用公共的基地址（通常是0x400000），因此主进程自己的可执行映像未映射的情况并不罕见。这一过程是通过NtUnmapViewOfSection(IMAGE_BASE, SIZE_OF_IMAGE)来完成的。

```
Executable Image of Host Process
                                        +---  +--------------------+
                                        |     |                    |
                                        |     |                    |
                                        |     |                    |
                                        |     |                    |
                                        |     |                    |
                   NtUnmapViewOfSection +     |                    |
                                        |     |                    |
                                        |     |                    |
                                        |     |                    |
                                        |     |                    |
                                        |     |                    |
                                        |     |                    |
                                        +---  +--------------------+

```

(3) 注入Payload<br>
要注入Payload，必须手动解析PE文件，以将其从磁盘形式转换为映像形式。在使用VirtualAllocEx分配虚拟内存之后，要将PE头部直接复制到该基地址。

```
Executable Image of Host Process
                                        +---  +--------------------+
                                        |     |         PE         |
                                        |     |       Headers      |
                                        +---  +--------------------+
                                        |     |                    |
                                        |     |                    |
                     WriteProcessMemory +     |                    |
                                              |                    |
                                              |                    |
                                              |                    |
                                              |                    |
                                              |                    |
                                              |                    |
                                              +--------------------+
```

要将PE文件转换为映像，必须单独从文件偏移量中读取所有部分，然后使用WriteProcessMemory将其正确放置到相应的虚拟偏移量中。这一点在本文每一节中都有详细的讲解。

```
typedef struct _IMAGE_SECTION_HEADER `{`
  BYTE  Name[IMAGE_SIZEOF_SHORT_NAME];
  union `{`
    DWORD PhysicalAddress;
    DWORD VirtualSize;
  `}` Misc;
  DWORD VirtualAddress;               // &lt;---- virtual offset
  DWORD SizeOfRawData;
  DWORD PointerToRawData;             // &lt;---- file offset
  DWORD PointerToRelocations;
  DWORD PointerToLinenumbers;
  WORD  NumberOfRelocations;
  WORD  NumberOfLinenumbers;
  DWORD Characteristics;
`}` IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;
Executable Image of Host Process
                                              +--------------------+
                                              |         PE         |
                                              |       Headers      |
                                        +---  +--------------------+
                                        |     |       .text        |
                                        +---  +--------------------+
                     WriteProcessMemory +     |       .data        |
                                        +---  +--------------------+
                                        |     |         ...        |
                                        +---- +--------------------+
                                        |     |         ...        |
                                        +---- +--------------------+
                                        |     |         ...        |
                                        +---- +--------------------+
```

(4) 执行Payload<br>
最后一步，就是将执行的起始地址指向Payload的AddressOfEntryPoint。由于进程的主线程已经被挂起，所以可以使用GetThreadContext来检索相关信息。其上下文结构被定义为：

```
typedef struct _CONTEXT
`{`
     ULONG ContextFlags;
     ULONG Dr0;
     ULONG Dr1;
     ULONG Dr2;
     ULONG Dr3;
     ULONG Dr6;
     ULONG Dr7;
     FLOATING_SAVE_AREA FloatSave;
     ULONG SegGs;
     ULONG SegFs;
     ULONG SegEs;
     ULONG SegDs;
     ULONG Edi;
     ULONG Esi;
     ULONG Ebx;
     ULONG Edx;
     ULONG Ecx;
     ULONG Eax;                        // &lt;----
     ULONG Ebp;
     ULONG Eip;
     ULONG SegCs;
     ULONG EFlags;
     ULONG Esp;
     ULONG SegSs;
     UCHAR ExtendedRegisters[512];
`}` CONTEXT, *PCONTEXT;
```

要修改起始地址，必须将Eax成员更改为Payload的AddressOfEntryPoint的虚拟地址。简单来说，context.Eax = ImageBase + AddressOfEntryPoint。通过调用SetThreadContext，将修改的部分传入CONTEXT结构，即可将上述更改应用到进程的线程。接下来，我们只需调用ResumeThread，就可以使Payload执行。

#### <a class="reference-link" name="2.3.3%20Atom%20Bombing"></a>2.3.3 Atom Bombing

Atom Bombing是一种代码注入技术，它利用Windows全局原子表（Windows’s Global Atom Table）进行全局数据存储。全局原子表的数据可以通过所有进程访问，这样就使我们的代码注入成为了可能。存储在表中的数据是以空字符结尾的C字符串类型，使用一个名为atom的16位整数键表示，类似于map数据结构。在MSDN中提供了一个用于添加数据的GlobalAddAtom函数，其定义如下：

```
ATOM WINAPI GlobalAddAtom(
    _In_ LPCTSTR lpString
);
```

其中，lpString是要存储的数据。在成功调用时，会返回16位整数的原子。为了检索存储在全局原子表中的数据，MSDN提供了一个GlobalGetAtomName，其定义如下：

```
UINT WINAPI GlobalGetAtomName(
    _In_  ATOM   nAtom,
    _Out_ LPTSTR lpBuffer,
    _In_  int    nSize
);
```

其功能是传入从GlobalAddAtom返回的标识原子，会将数据放入lpBuffer并返回不包含空终止符的字符串长度。<br>
Atom Bombing通过迫使目标进程加载并执行放置在全局原子表中的代码来实现，该过程依赖于另一个至关重要的函数NtQueueApcThread，它是QueueUserAPC的最低级用户空间调用。我们之所以使用NtQueueApcThread而不是QueueUserAPC的原因在于，与GlobalGetAtomName相比，QueueUserAPC的APCProc只能接收一个不匹配的参数。

```
VOID CALLBACK APCProc(               UINT WINAPI GlobalGetAtomName(
                                         _In_  ATOM   nAtom,
    _In_ ULONG_PTR dwParam     -&gt;        _Out_ LPTSTR lpBuffer,
                                         _In_  int    nSize
);                                   );
```

然而，在NtQueueApcThread的底层实现中，实际上是允许三个参数的：

```
NTSTATUS NTAPI NtQueueApcThread(                      UINT WINAPI GlobalGetAtomName(
    _In_     HANDLE           ThreadHandle,               // target process's thread
    _In_     PIO_APC_ROUTINE  ApcRoutine,                 // APCProc (GlobalGetAtomName)
    _In_opt_ PVOID            ApcRoutineContext,  -&gt;      _In_  ATOM   nAtom,
    _In_opt_ PIO_STATUS_BLOCK ApcStatusBlock,             _Out_ LPTSTR lpBuffer,
    _In_opt_ ULONG            ApcReserved                 _In_  int    nSize
);                                                    );
```

这是代码注入过程的可视化表示：

```
Atom bombing code injection
                                              +--------------------+
                                              |                    |
                                              +--------------------+
                                              |      lpBuffer      | &lt;-+
                                              |                    |   |
                                              +--------------------+   |
     +---------+                              |                    |   | Calls
     |  Atom   |                              +--------------------+   | GlobalGetAtomName
     | Bombing |                              |     Executable     |   | specifying
     | Process |                              |       Image        |   | arbitrary
     +---------+                              +--------------------+   | address space
          |                                   |                    |   | and loads shellcode
          |                                   |                    |   |
          |           NtQueueApcThread        +--------------------+   |
          +---------- GlobalGetAtomName ----&gt; |      ntdll.dll     | --+
                                              +--------------------+
                                              |                    |
                                              +--------------------+

```

以上，我们以简洁的方式介绍了Atom Bombing，但这些基础知识对于本文的研究已经足够了。如果你想了解更多关于Atom Bombing的只是，请参考enSilo的文章：[https://blog.ensilo.com/atombombing-brand-new-code-injection-for-windows](https://blog.ensilo.com/atombombing-brand-new-code-injection-for-windows) 。



## 三、UnRunPE

UnRunPE是我们的概念验证（PoC）工具，是为了将API监控的理论应用于实践之中而写的。该工具目的在于选定一个可执行文件，并创建挂起的进程，随后将DLL注入到该进程中，利用Process Hollowing技术来实现特定的功能。

### <a class="reference-link" name="3.1%20%E4%BB%A3%E7%A0%81%E6%B3%A8%E5%85%A5%E6%A3%80%E6%B5%8B"></a>3.1 代码注入检测

读完了我们代码注入的基础知识，Hollowing方法可以用下面的WinAPI调用链来描述：

```
CreateProcess
NtUnmapViewOfSection
VirtualAllocEx
WriteProcessMemory
GetThreadContext
SetThreadContext
ResumeThread
```

这些调用过程，不必按照特定顺序进行调用。例如，也可以在VirtualAllocEx之前调用GetThreadContext。然而，一些调用需要依赖之前的API调用，也不能将这些调用完全颠倒先后顺序。例如，SetThreadContext必须要在GetThreadContext或CreateProcess之前调用，否则目标进程就不会有Payload注入。该工具以上述内容为运行的基础，试图检测潜在的Process Hollowing过程。<br>
根据API监控的理论，我们最好对较低的位置进行挂钩，但如果考虑到对恶意软件检测的场景，那么我们最理想的是在最低的位置挂钩。最厉害的恶意软件可能会尝试跳过更高级别的WinAPI函数，直接调用通常在ntdll.dll模块中所找到的调用层次结构中最低的函数。以下WinAPI函数是Process Hollowing的调用层次结构最低的函数：

```
NtCreateUserProcess
NtUnmapViewOfSection
NtAllocateVirtualMemory
NtWriteVirtualMemory
NtGetContextThread
NtSetContextThread
NtResumeThread
```

### <a class="reference-link" name="3.2%20%E4%BB%A3%E7%A0%81%E6%B3%A8%E5%85%A5%E8%BD%AC%E5%82%A8"></a>3.2 代码注入转储

当我们对必要的函数进行挂钩之后，就会执行目标进程，并记录每个已挂钩函数的参数，这样能跟踪Process Hollowing以及主进程的当前状态。最重要的两个钩子是NtWriteVirtualMemory和NtResumeThread，前者负责在代码注入后进行应用，后者负责执行。除了记录参数之外，UnRunPE还会尝试转储使用NtWriteVirtualMemory写入的字节，然后当到达NtResumeThread时，会尝试转储已经注入主进程的全部Payload。为了完成上述任务，它使用NtCreateUserProcess中记录的进程和线程句柄参数，以及NtUnmapViewOfSection记录的基地址和大小。在这里，如果使用NtAllocateVirtualMemory提供的参数可能更为合适，但实际过程中，由于某些暂不清楚的原因，如果挂钩该函数会在运行过程中出现一些错误。当Payload从NtResumeThread中转储出来后，它将会终止目标进程及其宿主进程，以防止注入的代码被真正执行。

### <a class="reference-link" name="3.3%20UnRunPE%E7%A4%BA%E4%BE%8B"></a>3.3 UnRunPE示例

为了演示，我使用了之前创建的二进制木马文件，它包含主要可执行文件PEview.exe，同时隐藏了可执行文件PuTTY.exe。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-20%2018-35-29.png)



## 四、实战：Dreadnought工具

Dreadnought是基于UnRunPE构建的PoC工具，用于更广泛的代码注入检测，也就是我们在本文2.3中讲解的全部代码注入。我们要实现全面的代码注入检测，就需要对工具进行一些强化。

### <a class="reference-link" name="4.1%20%E4%BB%A3%E7%A0%81%E6%B3%A8%E5%85%A5%E6%A3%80%E6%B5%8B%E6%96%B9%E6%B3%95"></a>4.1 代码注入检测方法

考虑到当前有很多种代码注入方法，因此必须对不同的代码注入技术进行区分。第一种方法是识别”触发”API调用，即负责远程执行Payload的API调用。共有四种类型：<br>
段（Section）：代码作为段被注入/代码被注入到段中。<br>
进程：代码被注入到进程中。<br>
代码：通用代码注入或Shellcode。<br>
DLL：代码作为DLL被注入。<br>[![](https://4.bp.blogspot.com/-ixv5E0LMZCw/WWi5yRjL-_I/AAAAAAAAAnk/WO99S4Yrd8w6lfg6tITwUV02CGDFYAORACLcBGAs/s1600/Process%2BInjection%25281%2529.png)](https://4.bp.blogspot.com/-ixv5E0LMZCw/WWi5yRjL-_I/AAAAAAAAAnk/WO99S4Yrd8w6lfg6tITwUV02CGDFYAORACLcBGAs/s1600/Process%2BInjection%25281%2529.png)<br>
每一个触发API都列在相应的执行下面。当符合这些API中的任何一个时，Dreadought将会执行相应的代码转储方法，该方法与假设的注入类型相匹配，就类似于UnRunPE中Porcess Hollowing的方式。但是，这还远远不够，因为API调用仍然与可能会被混合，实现如箭头所示的功能。

### <a class="reference-link" name="4.2%20%E5%90%AF%E5%8F%91%E5%BC%8F%E6%A3%80%E6%B5%8B"></a>4.2 启发式检测

为了让Dreadnought更准确地确定代码注入的方法，我们应该使用启发式检测。在开发过程中，我们应用了非常简单的启发式方法。在进程注入后，每次对API进行挂钩时，都会增加一个或多个存储在map数据结构中的相关代码注入类型的权重。由于它会跟踪每一个API调用，因此从一开始就有一个最高可能性的注入类型。一旦触发API被输入，它将识别并比较相关类型的权重，并进行调整。

### <a class="reference-link" name="4.3%20Dreadnought%E5%AE%9E%E6%88%98"></a>4.3 Dreadnought实战

#### <a class="reference-link" name="4.3.1%20%E8%BF%9B%E7%A8%8B%E6%B3%A8%E5%85%A5%20-%20Process%20Hollowing"></a>4.3.1 进程注入 – Process Hollowing

[![](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-14-46.png)](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-14-46.png)

#### <a class="reference-link" name="4.3.2%20DLL%E6%B3%A8%E5%85%A5%20-%20SetWindowsHookEx"></a>4.3.2 DLL注入 – SetWindowsHookEx

[![](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-15-35.png)](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-15-35.png)

#### <a class="reference-link" name="4.3.3%20DLL%E6%B3%A8%E5%85%A5%20-%20QueueUserAPC"></a>4.3.3 DLL注入 – QueueUserAPC

[![](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-16-17.png)](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-16-17.png)

#### <a class="reference-link" name="4.3.4%20%E4%BB%A3%E7%A0%81%E6%B3%A8%E5%85%A5%20-%20Atom%20Bombing"></a>4.3.4 代码注入 – Atom Bombing

[![](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-24-43.png)](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-24-43.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-25-09.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/NtRaiseHardError/NtRaiseHardError.github.io/master/images/2018-02-21-Userland-API-Monitoring-and-Code-Injection-Detection/Screenshot%20from%202018-02-21%2020-29-30.png)



## 五、结论

本文对代码注入的技术进行了讲解，并帮助大家理解了其与WinAPI的交互过程。恶意软件利用注入的方式来绕过反病毒检测，我们可以使用Dreadnought来有效对这种行为进行检测。<br>
然而，Dreadnought仍然存在一些局限性，它的启发式检测设计尚不完善，目前只能用于理论演示的目的，在实际使用中效果可能并不理想。因此，在操作系统正常运行期间，其可能会出现误报与漏报的情况。



## 六、PoC与相关源代码

[https://github.com/NtRaiseHardError/UnRunPE](https://github.com/NtRaiseHardError/UnRunPE)<br>[https://github.com/NtRaiseHardError/Dreadnought](https://github.com/NtRaiseHardError/Dreadnought)



## 七、参考

[1] [https://www.blackhat.com/presentations/bh-usa-06/BH-US-06-Sotirov.pdf](https://www.blackhat.com/presentations/bh-usa-06/BH-US-06-Sotirov.pdf)<br>
[2] [https://www.codeproject.com/Articles/7914/MessageBoxTimeout-API](https://www.codeproject.com/Articles/7914/MessageBoxTimeout-API)<br>
[3] [https://blog.ensilo.com/atombombing-brand-new-code-injection-for-windows](https://blog.ensilo.com/atombombing-brand-new-code-injection-for-windows)<br>
[4] [http://struppigel.blogspot.com.au/2017/07/process-injection-info-graphic.html](http://struppigel.blogspot.com.au/2017/07/process-injection-info-graphic.html)<br>
[5] [https://www.reactos.org/](https://www.reactos.org/)<br>
[6] [https://undocumented.ntinternals.net/](https://undocumented.ntinternals.net/)<br>
[7] [http://ntcoder.com/category/undocumented-winapi/](http://ntcoder.com/category/undocumented-winapi/)<br>
[8] [https://github.com/processhacker/processhacker](https://github.com/processhacker/processhacker)<br>
[9] [https://www.youtube.com/channel/UCVFXrUwuWxNlm6UNZtBLJ-A](https://www.youtube.com/channel/UCVFXrUwuWxNlm6UNZtBLJ-A)<br>
[10] [https://www.youtube.com/channel/UC–DwaiMV-jtO-6EvmKOnqg](https://www.youtube.com/channel/UC--DwaiMV-jtO-6EvmKOnqg)
