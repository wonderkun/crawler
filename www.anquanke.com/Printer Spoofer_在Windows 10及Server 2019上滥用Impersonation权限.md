> 原文链接: https://www.anquanke.com//post/id/204399 


# Printer Spoofer：在Windows 10及Server 2019上滥用Impersonation权限


                                阅读量   
                                **281109**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者itm4n，文章来源：itm4n.github.io
                                <br>原文地址：[https://itm4n.github.io/printspoofer-abusing-impersonate-privileges/](https://itm4n.github.io/printspoofer-abusing-impersonate-privileges/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01487e3877fcadc528.jpg)](https://p0.ssl.qhimg.com/t01487e3877fcadc528.jpg)



## 0x00 前言

过去几年中诞生了不少工具，如[RottenPotato](https://github.com/foxglovesec/RottenPotato)、[RottenPotatoNG](https://github.com/breenmachine/RottenPotatoNG)或者[Juicy Potato](https://github.com/ohpe/juicy-potato)等，这些工具能够利用Windows系统中的模拟（Impersonation）权限，因此广受攻击者欢迎。然而Windows操作系统最近进行了不少改动，有意或者无意地降低了这些技术在Windows 10及Server 2016/2019上的威力。在本文中，我想与大家分享一款新工具，可以帮助渗透测试人员再次利用这种权限提升技术。

需要注意的是，这里我使用了“新工具”（而非“新技术”）这个词。如果大家希望通过本文掌握一种全新的提权技术，可能会大失所望。这里我想讨论的是如何结合非常知名的两种技术，将权限从`LOCAL SERVICE`或者`NETWORK SERVICE`提升至`SYSTEM`。据我所知，目前网上并没有直接分析过如何在该上下文中使用该技巧（可能是我没有找到）。

> 注意：之前James Forshaw发表过一篇文章（[Sharing a Logon Session a Little Too Much](https://www.tiraniddo.dev/2020/04/sharing-logon-session-little-too-much.html)），但我的工具当时已经开发完成，只是文章还没发表。我本来想取消文章发布，但认为还是可以与大家分享我的心得。



## 0x01 Impersonation权限

<a>@decoder_it</a>曾提到过“如果我们拿到了`SeAssignPrimaryToken`或者`SeImpersonate`权限，那么我们就能拿到`SYSTEM`权限”。这显然是非常兴奋的一件事，但实际上并非如此。

这两个权限威力的确非常大，允许我们运行代码，甚至可以在另一个用户的上下文中创建新的进程。为了完成该任务，如果我们具备`SeImpersonatePrivilege`权限，那么可以调用`CreateProcessWithToken()`；如果我们具备`SeAssignPrimaryTokenPrivilege`权限，可以调用`CreateProcessAsUser()`。

在讨论这2个函数之前，我想与大家快速过一遍标准的`CreateProcess()`函数：

[![](https://p2.ssl.qhimg.com/t01bf1a186ecc0e0e42.png)](https://p2.ssl.qhimg.com/t01bf1a186ecc0e0e42.png)

前2个参数可以让我们指定希望运行的应用程序或者命令行，然后我们可以设置其他选项，自定义子进程的运行环境以及安全上下文。最后1个参数为指向`PROCESS_INFORMATION`结构的引用，该结构将在函数执行成功后返回，其中包含目标进程及线程的句柄。

现在来观察一下`CreateProcessWithToken()`及`CreateProcessAsUser()`：

[![](https://p1.ssl.qhimg.com/t0179c4cdd2f70eb231.png)](https://p1.ssl.qhimg.com/t0179c4cdd2f70eb231.png)

如上图所示，这两个函数与标准的`CreateProcess()`函数并没有太多差别。然而，这两个函数都需要指向令牌（token）的一个句柄。根据官方文档，`hToken`必须为“指向用户主令牌（primary token）的句柄”。此外，文档中还有如下一段话：

> 为了获取代表特定用户的primary token，……我们可以调用`DuplicateTokenEx`函数，将impersonation token（模拟令牌）转换为primary token。这样模拟客户端的服务端应用程序就可以使用客户端的安全上下文来创建进程。

当然，官方文档并没有告诉我们如何获取该令牌，因为这并不是这两个函数的职责，但官方文档中给出了这些函数的适用场景。这些函数允许服务端应用程序在客户端的安全上下文中创建进程，对于提供RPC/COM接口的Windows服务而言，这是非常常见的一种做法。当我们调用以高权限账户运行的服务所提供的RPC函数时，该服务可能会调用`RpcImpersonateClient()`，以便在我们的安全上下文中运行某些代码，降低权限提升风险。

总结一下，如果我们具备`SeImpersonatePrivilege`或者`SeAssignPrimaryTokenPrivilege`权限，就可以在其他用户安全上下文中创建进程，我们只需要拿到该用户的令牌即可。现在问题是：如何使用自定义服务端应用来获取这类令牌？



## 0x02 通过命名管道模拟用户

Potato系列工具背后的思路都一样：将网络认证从环回TCP端点中继至NTLM协商程序。为了完成该任务，这些工具利用了`IStorage` COM接口的某些特殊功能，诱导`NT AUTHORITY\SYSTEM`账户连接攻击者控制的RPC服务器并进行身份认证。

在身份认证过程中，所有消息都会在客户端（这里为`SYSTEM`账户）和本地NTLM协商程序之间中继。这里的中继程序只是几个Windows API调用的组合（如`AcquireCredentialsHandle()`以及`AcceptSecurityContext()`），通过ALPC与`lsass`进程交互。如果一切顺利，我们将能拿到所需的`SYSTEM`令牌。

不幸的是，由于某些核心改动，这种技术无法适用于Windows 10，该系统中从目标服务到`Storage`的底层COM连接只能通过`TCP/135`端口。

> 注意：[文章](https://decoder.cloud/2019/12/06/we-thought-they-were-potatoes-but-they-were-beans/)中提到过，这种限制机制其实可以绕过，但拿到的令牌无法用于身份模拟。

现在我们是否还有其他选择？RPC并不是在这种中继场景中唯一可用的一种协议，这里我想与大家谈到使用管道的一种古老技术。

根据官方[文档](https://docs.microsoft.com/en-us/windows/win32/ipc/pipes)：“管道是一种共享内存，进程可以使用管道来通信。创建管道的进程为管道服务器，连接到管道的进程为管道客户端。进程可以向管道中写入信息，其他进程可以从管道中读取信息”。换而言之，管道是Windows上实现进程间通信（IPC）的一种方式，与RPC、COM或者socket类似。

管道有两种类型：
- 匿名管道：匿名管道是父进程和子进程之间传输数据的一种典型方式，通常用来在子进程与父进程之间重定向标准输入及输出。
- 命名管道：不相关进程间可以使用命名管道来传输数据，前提是管道赋予客户端进程适当的访问权限。
前面我提到过`RpcImpersonateClient()`函数，RPC服务器可以使用该函数来模拟RPC客户端。命名管道似乎具备`ImpersonateNamedPipeClient()`函数相同的功能，所以我们可以考虑使用命名管道完成模拟。

前面都是理论知识，现在给出一些示例代码，如下所示：

```
HANDLE hPipe = INVALID_HANDLE_VALUE;
LPWSTR pwszPipeName = argv[1];
SECURITY_DESCRIPTOR sd = `{` 0 `}`;
SECURITY_ATTRIBUTES sa = `{` 0 `}`;
HANDLE hToken = INVALID_HANDLE_VALUE;

if (!InitializeSecurityDescriptor(&amp;sd, SECURITY_DESCRIPTOR_REVISION))
`{`
    wprintf(L"InitializeSecurityDescriptor() failed. Error: %d - ", GetLastError());
    PrintLastErrorAsText(GetLastError());
    return -1;
`}`

if (!ConvertStringSecurityDescriptorToSecurityDescriptor(L"D:(A;OICI;GA;;;WD)", SDDL_REVISION_1, &amp;((&amp;sa)-&gt;lpSecurityDescriptor), NULL))
`{`
    wprintf(L"ConvertStringSecurityDescriptorToSecurityDescriptor() failed. Error: %d - ", GetLastError());
    PrintLastErrorAsText(GetLastError());
    return -1;
`}`

if ((hPipe = CreateNamedPipe(pwszPipeName, PIPE_ACCESS_DUPLEX, PIPE_TYPE_BYTE | PIPE_WAIT, 10, 2048, 2048, 0, &amp;sa)) != INVALID_HANDLE_VALUE)
`{`
    wprintf(L"[*] Named pipe '%ls' listening...\n", pwszPipeName);
    ConnectNamedPipe(hPipe, NULL);
    wprintf(L"[+] A client connected!\n");

    if (ImpersonateNamedPipeClient(hPipe)) `{`

        if (OpenThreadToken(GetCurrentThread(), TOKEN_ALL_ACCESS, FALSE, &amp;hToken)) `{`

            PrintTokenUserSidAndName(hToken);
            PrintTokenImpersonationLevel(hToken);
            PrintTokenType(hToken);

            DoSomethingAsImpersonatedUser();

            CloseHandle(hToken);
        `}`
        else
        `{`
            wprintf(L"OpenThreadToken() failed. Error = %d - ", GetLastError());
            PrintLastErrorAsText(GetLastError());
        `}`
    `}`
    else
    `{`
        wprintf(L"ImpersonateNamedPipeClient() failed. Error = %d - ", GetLastError());
        PrintLastErrorAsText(GetLastError());
    `}`

    CloseHandle(hPipe);
`}`
else
`{`
    wprintf(L"CreateNamedPipe() failed. Error: %d - ", GetLastError());
    PrintLastErrorAsText(GetLastError());
`}`
```

前2个函数用来创建一个自定义安全描述符，以便后续应用于管道。这些函数不单单局限于命名管道，因此没有在模拟中发挥作用。命名管道的确是可保护的对象，与文件或者注册表一样。这意味着如果我们没有在创建的命名管道上设置适当的权限，那么使用不同身份运行的客户端可能无法访问该管道。这里我选择最简单的场景，赋予`Everyone`组对该管道的通用访问权限。

通过命名管道模拟客户端时，我们需要如下函数：

1、`CreateNamedPipe()`：作为服务端应用，我们可以使用该函数创建格式为`\\.\pipe\PIPE_NAME`的命名管道。

2、`ConnectNamedPipe()`：创建命名管道后，该函数用来接受客户端连接。如果没有明确指定，该调用默认情况下使用同步方式，因此线程处于暂停状态，直到客户端连接。

3、`ImpersonateNamedPipeClient()`：这正是我们研究的重点。

当然，使用最后一个函数时我们要遵守一些规则。根据[官方文档](https://docs.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient#remarks)，这里有4种可模拟的场景，其中2种场景为：

1、经过认证后的身份与调用方相同。也就是说，我们可以模拟我们自己。奇怪的是，在某些利用场景中这的确是非常有用的一种场景。

2、调用方具备`SeImpersonatePrivilege`权限。这也是我们所处的场景。

在给出代码之前，我先实现了某些函数，用来打印客户端令牌的相关信息。此外我还实现了一个`DoSomethingAsImpersonatedUser()`函数，该函数的功能是检查我们是否能在客户端的上下文种执行代码。

```
PrintTokenUserSidAndName(hToken);
PrintTokenImpersonationLevel(hToken);
PrintTokenType(hToken);
DoSomethingAsImpersonatedUser();
```

下面开始进入正题。以本地管理员权限启动我们的服务端应用后（本地管理员默认情况下具备`SeImpersonatePrivilege`权限），我使用普通用户账户，尝试向命名管道写入数据。

[![](https://itm4n.github.io/assets/posts/2020-05-02-printspoofer-abusing-impersonate-privileges/03_simple-impersonation.gif)](https://itm4n.github.io/assets/posts/2020-05-02-printspoofer-abusing-impersonate-privileges/03_simple-impersonation.gif)

客户端连接后，我们拿到模拟级别为`2`（即`SecurityImpersonation`）的一个模拟令牌。此外，`DoSomethingAsImpersonatedUser()`会成功返回，这意味着我们可以在该户端的安全上下文种运行任意代码。

> 可能大家会注意到我使用的路径为`\\localhost\pipe\foo123`，而不是`\\.\pipe\foo123`（这是管道的实际名称）。为了成功模拟，服务端首先需要从管道种读取数据。如果客户端使用`\\.\pipe\foo123`作为路径来打开管道，将不会写入数据，导致`ImpersonateNamedPipeClient()`失败。另一方面，如果客户端使用`\\HOSTNAME\pipe\foo123`来打开管道，`ImpersonateNamedPipeClient()`则会成功执行。不要问我为什么，我也不知道……

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015076504cc0d76375.png)

总结一下，我们知道为了在另一个用户的上下文中创建进程，我们需要拿到令牌。然后，由于服务端应用采用命名管道模拟，因此我们能如愿获取到令牌。到目前为止，这些都是大家知道的知识，现在问题是：我们如何诱导`NT AUTHORITY\SYSTEM`账户连接我们的命名管道？



## 0x03 获取SYSTEM令牌

去年年底（2019-12-06），[文章](https://decoder.cloud/2019/12/06/we-thought-they-were-potatoes-but-they-were-beans/)，其中演示了如何在本地NTLM中继场景中，利用Background Intelligent Transfer Service（BITS）获取`SYSTEM`令牌，这与Potato工具所用到的技术非常相似。[此处](https://github.com/antonioCoco/RogueWinRM)下载源码。

虽然这种方法非常有效，但缺点也很明显。该技术需要使用WinRM请求，由BITS在本地`TCP/5985`端口发起。如果该端口可用，我们可以创建一个恶意WinRM服务器，响应该请求，从而捕获到`SYSTEM`账户凭据。尽管WinRM服务通常在工作站系统上处于停止状态，但在服务器上并非如此，因此无法利用。

当完成PoC开发后，我还查找了是否存在更为通用的方法能实现相同目标的：通过本地NTLM中继捕捉`SYSTEM`令牌。尽管这不是我的首要任务，我还是找到了类似的技巧，但最终该方法还是有相同的局限性，无法适用于大多数Windows Server系统。几个月之后，在某次闲聊中，<a>@jonaslyk</a>提供了答案：打印机漏洞（略微修改版）。

打印机漏洞最早由Lee Christensen（[GitHub](https://github.com/leechristensen/SpoolSample)上的描述，该工具的功能是“强制Windows主机通过MS-RPRN RPC接口向其他计算机发起身份认证”。该工具背后的原理通过诱导域控制器回连非约束委派的某个系统，从而实现了在活动目录环境中的一种简单且有效的利用机制。基于这个原理，攻击者可以突破双向认证的另一个森林。

该工具会调用Print Spooler服务提供的一个RPC函数：

```
DWORD RpcRemoteFindFirstPrinterChangeNotificationEx( 
    /* [in] */ PRINTER_HANDLE hPrinter,
    /* [in] */ DWORD fdwFlags,
    /* [in] */ DWORD fdwOptions,
    /* [unique][string][in] */ wchar_t *pszLocalMachine,
    /* [in] */ DWORD dwPrinterLocal,
    /* [unique][in] */ RPC_V2_NOTIFY_OPTIONS *pOptions)

```

根据官方文档，该函数会创建一个远程更改通知对象，监控对打印机对象的更改，使用`RpcRouterReplyPrinter`或者`RpcRouterReplyPrinterEx`向打印客户端发送更改通知。

那么这些通知如何发送到客户端呢？答案是“在命名管道上……通过RPC”。Print Spooler服务的RPC接口通过命名管道`\\.\pipe\spoolss`对外提供服务，现在是不是真相快水落石出了？

[![](https://p1.ssl.qhimg.com/t016fe1f18e7fd3364d.png)](https://p1.ssl.qhimg.com/t016fe1f18e7fd3364d.png)

下面使用Lee Christensen提供的PoC来测试一下。

[![](https://p1.ssl.qhimg.com/t011ba9432cb7f6bf26.png)](https://p1.ssl.qhimg.com/t011ba9432cb7f6bf26.png)

我们可以通过该工具指定两个服务器：用于连接的服务器（域控制器）以及我们控制的服务器（用来捕捉认证凭据）。这里我们想连接本地主机，也想在本地主机上收到通知。这里的问题是，如果我们想这么做，那么通知将会发送给`\\DESKTOP-RTFONKM\pipe\spoolss`。该管道由`NT AUTHORITY\SYSTEM`控制，我们无法使用相同的名称创建自己的管道。另一方面，如果我们指定其他路径，在路径上附加一个任意字符串，由于路径有效性问题，我们将无法调用成功。

然而前面提到过，这里我们可以用一个小技巧，这也是<a>@jonaslyk</a>与我分享的第二个技巧。如果主机名中包含`/`字符，那么就能绕过路径有效性检查。但在计算待连接的命名管道路径时，系统的规范化操作会将该字符转换为`\`。通过这种方式，我们可以部分控制服务器所使用的路径！

[![](https://itm4n.github.io/assets/posts/2020-05-02-printspoofer-abusing-impersonate-privileges/07_spoolsample-second-try.gif)](https://itm4n.github.io/assets/posts/2020-05-02-printspoofer-abusing-impersonate-privileges/07_spoolsample-second-try.gif)

从上图可知，服务所使用的最终路径现在为`\\DESKTOP-RTFONKM\foo123\pipe\spoolss`。当然，这也不是适用于命名管道的有效路径，但稍加调整后，我们可以将其变成一个有效值。如果我们在RPC调用中指定的值为`\\DESKTOP-RTFONKM/pipe/foo123`，那么服务会将其转换为`\\DESKTOP-RTFONKM\pipe\foo123\pipe\spoolss`，这正是一个有效值。

在服务端应用的帮助下，现在我们快速测试这种利用场景。如下图所示，我们的确收到了一个连接，可以成功模拟`NT AUTHORITY\SYSTEM`。

[![](https://p0.ssl.qhimg.com/t015af247203c106256.png)](https://p0.ssl.qhimg.com/t015af247203c106256.png)

我在[PrintSpoofer](https://github.com/itm4n/PrintSpoofer)中实现了这种技巧，利用该工具的前提条件是，我们需要具备`SeImpersonatePrivilege`权限。我在默认安装的**Windows 8.1**、**Windows Server 2012 R2**、**Windows 10**以及**Windows Server 2019**上成功测试了该工具的功能，在某些条件下，该工具应该也适用于更早版本的Windows系统。

该工具在实际环境中的执行效果如下图所示，在Windows Server 2019上，我们拿到了以`CDPSvc`服务子进程形式生成的一个shell。这个案例特别有趣，因为该服务运行在`NT AUTHORITY\LOCAL SERVICE`全下辖，并且只有两个特权：`SeChangeNotifyPrivilege`和`SeImpersonatePrivilege`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01733741485b5f33be.png)



## 0x04 如何避免命名管道模拟

命名管道模拟可以被阻止。作为客户端，我们可以指定自己不希望被模拟，或者至少不希望服务器在我们的安全上下文中运行代码。实际上，我在之前一篇文章中曾讨论过该技术，微软通过补丁形式实现了这种保护机制。

在继续分析前，我们需要一个客户端应用来与我们的命名管道服务器通信，以便更好地演示缓解过程。命名管道是文件系统的一部分，那么我们如何连接命名管道呢？只需要“使用简单的`CreateFile()`函数即可”。

```
HANDLE hFile = CreateFile(
    argv[1],                        // pipe name
    GENERIC_READ | GENERIC_WRITE,   // read and write access 
    0,                              // no sharing 
    NULL,                           // default security attributes
    OPEN_EXISTING,                  // opens existing pipe 
    0,                              // default attributes 
    NULL                            // no template file 
);

if (hFile != INVALID_HANDLE_VALUE) `{`
    wprintf(L"[+] CreateFile() OK\n");
    CloseHandle(hFile);
`}` else `{`
    wprintf(L"[-] CreateFile() failed. Error: %d - ", GetLastError());
`}`
```

运行代码后，我们可以在命名管道上收到一个连接，成功模拟客户端。这一点很正常，因为我使用了**默认**参数来调用`CreateFile()`。

[![](https://p2.ssl.qhimg.com/t01578e05093e0702b2.png)](https://p2.ssl.qhimg.com/t01578e05093e0702b2.png)

参考[官方文档](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)，我们发现可以在`CreateFile()`函数中指定很多属性。如果我们设置了`SECURITY_SQOS_PRESENT`标志，就可以控制我们令牌的模拟级别。

[![](https://p4.ssl.qhimg.com/t01e429f5cf5155c8b4.png)](https://p4.ssl.qhimg.com/t01e429f5cf5155c8b4.png)

因此，在客户端应用源代码中，我修改了`CreateFile()`函数调用语句，如下所示，现在`dwFlagsAndAttributes`参数的值被设定为`SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION`。

```
HANDLE hFile = CreateFile(
    argv[1],                        // pipe name
    GENERIC_READ | GENERIC_WRITE,   // read and write access 
    0,                              // no sharing 
    NULL,                           // default security attributes
    OPEN_EXISTING,                  // opens existing pipe 
    SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION, // impersonation level: SecurityIdentification
    NULL                            // no template file 
);
```

[![](https://p1.ssl.qhimg.com/t018f541a031ca5ed78.png)](https://p1.ssl.qhimg.com/t018f541a031ca5ed78.png)

我们仍然能拿到关于令牌的某些信息，但当我们尝试在客户端安全上下文中执行代码时，会看到一个错误信息：“未提供所需的模拟级别，或者提供的模拟级别无效“。如上图所示，现在令牌的模拟级别为`SecurityIdentification`，导致我们的恶意服务端应用无法完整模拟客户端。

前面我提到过，微软通过补丁方式实现了这种防护。在前一篇文章中，我与大家讨论了Service Tracing功能中的一个漏洞。该功能允许我们收集特定服务的某些调试信息，只需要简单修改`HKLM` hive中的某个注册表键值即可。经过身份认证的用户可以在注册表的`FileDirectory`值中指定日志文件的目的文件夹。比如，如果我们指定了`C:\test`，那么被调试的程序就会将调试信息写入`C:\test\MODULE.log`，并且该操作会在目标应用或服务的安全上下文中执行。

由于我们可以控制文件路径，因此可以将管道名称作为目标文件夹的路径。这也是[CVE-2010-2554](https://www.cvedetails.com/cve/CVE-2010-2554/)（即[MS10-059](https://docs.microsoft.com/en-us/security-updates/securitybulletins/2010/ms10-059)）安全公告解决的问题。

该漏洞由[此处](https://github.com/Re4son/Chimichurri)下载修改版代码。该工具的原理是诱导以`NT AUTHORITY\SYSTEM`权限运行的服务连接到恶意命名管道，从而捕获高权限令牌。由于我们具备`SeImpersonatePrivilege`特权，因此利用起来没有问题。

如果我们在Windows 10上测试，会出现什么情况呢？如下所示：

[![](https://p3.ssl.qhimg.com/t01f8ef2874fc2294aa.png)](https://p3.ssl.qhimg.com/t01f8ef2874fc2294aa.png)

尽管我们具备`SeImpersonatePrivilege`特权，但当尝试在`SYSTEM`账户上下文中执行代码时，还是会看到一样的错误。`rtutils.dll`中使用了`CreateFile()`来打开日志文件，分析相关代码，如下所示：

[![](https://p2.ssl.qhimg.com/t011842b4591051eda3.png)](https://p2.ssl.qhimg.com/t011842b4591051eda3.png)

十六进制的值`0x110080`实际上为`SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION | FILE_ATTRIBUTE_NORMAL`。

> 注意：这种防护措施并不是无懈可击，只是让攻击者操作时变得更加困难。

微软将这种情况当成常规漏洞处理，分配了CVE编号，公布了详细的安全公告。然而随着时间的推移，现在情况有所不同。现在如果我们尝试报告此类漏洞，官方会反馈称利用模拟特权实现权限提升是系统的预期行为，官方可能已经意识到这是一场无法取得的战斗。[James Forshaw](https://twitter.com/tiraniddo)曾在[Twitter](https://twitter.com/tiraniddo/status/1203069035983720449)上提到过：“官方认为如果攻击者拿到了模拟特权，那么可能已经具备了`SYSTEM`权限。官方当然可以让攻击者更难拿到合适的令牌，但这只是一场无尽的猫鼠游戏，攻击者总能找到其他可利用的点”。



## 0x05 总结

在本文中，我介绍了如何在Windows 10上利用模拟特权，在`SYSTEM`账户上下文中执行代码。许多以`LOCAL/NETWORK SERVICE`身份运行的Windows服务都具备这些条件。在某些场景中，有些服务并不满足条件，此时我们可以使用[FullPowers](https://github.com/itm4n/FullPowers)或者James Forshaw在某篇[文章](https://www.tiraniddo.dev/2020/04/sharing-logon-session-little-too-much.html)中介绍的方法来拿到模拟特权。



## 0x06 参考资料
<li>GitHub – itm4n / PrintSpoofer<br>[https://github.com/itm4n/PrintSpoofer](https://github.com/itm4n/PrintSpoofer)
</li>
<li>Decoder’s Blog – We thought they were potatoes but they were beans (from Service Account to SYSTEM again)<br>[https://decoder.cloud/2019/12/06/we-thought-they-were-potatoes-but-they-were-beans/](https://decoder.cloud/2019/12/06/we-thought-they-were-potatoes-but-they-were-beans/)
</li>
<li>GitHub – antonioCoco / RogueWinRM (Windows Local Privilege Escalation from Service Account to System) [https://github.com/antonioCoco/RogueWinRM](https://github.com/antonioCoco/RogueWinRM)
</li>
<li>GitHub – leechristensen / SpoolSample<br>[https://github.com/leechristensen/SpoolSample](https://github.com/leechristensen/SpoolSample)
</li>
<li>Tyranid’s Lair – Sharing a Logon Session a Little Too Much<br>[https://www.tiraniddo.dev/2020/04/sharing-logon-session-little-too-much.html](https://www.tiraniddo.dev/2020/04/sharing-logon-session-little-too-much.html)
</li>