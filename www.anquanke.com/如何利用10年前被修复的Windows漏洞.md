> 原文链接: https://www.anquanke.com//post/id/207601 


# 如何利用10年前被修复的Windows漏洞


                                阅读量   
                                **200929**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者itm4n，文章来源：itm4n.github.io
                                <br>原文地址：[https://itm4n.github.io/chimichurri-reloaded/](https://itm4n.github.io/chimichurri-reloaded/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t011ed72dd26eb91c3a.jpg)](https://p2.ssl.qhimg.com/t011ed72dd26eb91c3a.jpg)



## 0x00 前言

在上一篇文章中，我介绍了如何在具备模拟（impersonation）特权的情况下，将权限提升至`SYSTEM`。此外我们也以微软10年前对Service Tracing漏洞的修复措施为例，演示了如何修复这类漏洞。然而这种安全机制实际上可以被绕过，在本文中，我们将研究如何让有10年历史的漏洞焕发生机。



## 0x01 背景

大约10年之前，Cesar Cerrudo（[CVE-2010-2554](https://www.cvedetails.com/cve/CVE-2010-2554/)。

这里我们以`RASMAN`服务对应的Service Tracing键值为例。操作过程非常简单，我们首先需要启动一个本地命名管道服务器，然后在注册表中将目标日志文件目录的路径设为该命名管道的路径。

[![](https://p4.ssl.qhimg.com/t01a0b85c63a0d602e9.png)](https://p4.ssl.qhimg.com/t01a0b85c63a0d602e9.png)

如上图所示，目标目录为`\\localhost\pipe\tracing`。随后，一旦`EnableFileTracing`值被设置为`1`，服务就会使用`\\localhost\pipe\tracing\RASMAN.LOG`作为路径来尝试打开日志文件。因此，如果我们创建名为`\\.\pipe\tracing\RASMAN.LOG`的命名管道，就可以收到连接请求，调用`ImpersonateNamedPipeClient`函数来模拟服务账户。由于`RASMAN`以`NT AUTHORITY\SYSTEM`权限运行，因此我们最终能够拿到`SYSTEM`模拟令牌。

> **注意：**在不同版本的Windows系统上，将`EnableFileTracing`设置为`1`后系统可能不会立即打开日志文件。由于低权限用户可以通过服务控制管理器（SCM）来启动`RASMAN`，因此为了稳定触发该事件，我们可以手动启动该服务。

[![](https://p4.ssl.qhimg.com/t0127d298189167777c.png)](https://p4.ssl.qhimg.com/t0127d298189167777c.png)

当然，如果我们尝试在较新版本的Windows上（发布年限不到10年）执行该操作，我们就会看到上图所示的问题。如果我们想在被模拟用户的安全上下文中执行任意代码，我们将会收到`1346`错误，也就是“指定的模拟级别无 效, 或所提供的模拟级别无效”错误。此外我们还会看到错误代码`5`，也就是“访问被拒绝”错误，这是因为微软在Windows系统中部署了相应的防护机制。

我在前一篇文章中详细描述了这种安全更新机制。简而言之，系统现在会在`CreateFile`函数调用中指定`SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION`标志，而该函数负责获取目标日志文件的初始句柄。在这些标志的影响下，我们现在获取的令牌的模拟级别为`SecurityIdentification`（等级2/4）。然而为了完整模拟目标用户，我们必须获取的模拟级别为`SecurityImpersonation`（等级3/4）或者`SecurityDelegation`（等级4/4）。

> 备注：在上述命令提示符中，我们看到的打印信息为`Unknown error 0x80070542`，而不是实际的Win32错误。这是因为我在模拟用户时想获取错误代码对应的错误信息。由于模拟级别受限，因此我们无法查找代码与消息的对应关系。

那么这是否意味着我们将无功而返呢？我们获得的令牌的确用处不大，但我们可以继续阅读下文，寻找一线生机。



## 0x02 UNC路径

根据前文描述，如果我们将日志文件目录设为命名管道名称，就能拿到模拟令牌，但无法利用该令牌创建新进程。然而这里我其实隐藏了一个重要的细节：我们如何设置命名管道名称？

首先我们需要了解最终使用的日志文件路径的计算方式。这是非常简单的字符串拼接操作：`&lt;DIRECTORY&gt;\&lt;SERVICE_NAME&gt;.LOG`，其中`&lt;DIRECTORY&gt;`读取自注册表（`FileDirectory`键值）。因此，如果我们为名为`Bar`的服务设置输出的目录为`C:\Temp`，那么该服务就会使用`C:\Temp\BAR.LOG`作为日志文件的路径。

在漏洞利用过程中，我们通过UNC路径来指定管道名称，而不是常规的目录。在Windows系统上我们有许多方法来设置路径，UNC路径是其中一种（这里我们就不展开讲）。为了成功利用漏洞，我们的确需要用到UNC（通用命名约定），但需要稍加改动。

UNC路径通常用来访问本地网络中的远程共享。比如，如果我们想访问`DUMMY`主机`FOO`卷上的`BAR`文件，那么可以使用UNC路径`\\DUMMY\FOO\BAR`。在这种情况下，客户端主机会连接目标服务器的TCP 445端口，使用SMB协议来交换数据。

然而我们也可以使用`\\DUMMY[@4444](https://github.com/4444)\FOO\BAR`，通过任意端口（而不是默认的TCP 445端口）来访问远程共享（这里为`4444`端口）。尽管这种路径与默认路径差别很小，但带来的影响非常巨大。效果上最明显的区别在于，这种情况下系统不再使用SMB协议，客户端会使用HTTP协议的扩展版本，也就是WebDAV（Web Distributed Authoring and Versioning）。

在Windows系统上，WebDAV由`WebClient`服务负责处理。如果我们查看该服务的描述，可以找到如下信息：

> （该服务）使基于Windows的程序可以创建、访问并修改基于Internet的文件。如果停止该服务，这些功能将不再可用。如果该服务被禁用，那么以来该服务的其他服务将无法启动。

虽然WebDAV使用的是完全不同的协议，但有个因素始终不变：身份认证。因此，如果我们创建一个本地WebDAV服务器，然后使用该路径作为输出目录时会出现什么情况？



## 0x03 拿到模拟令牌

首先我们需要编辑注册表，修改`FileDirectory`的值。这里我们不再使用命名管道路径，而是使用`\\127.0.0.1[@4444](https://github.com/4444)\tracing`。

[![](https://p0.ssl.qhimg.com/t015e5bd162b69d3dbf.png)](https://p0.ssl.qhimg.com/t015e5bd162b69d3dbf.png)

我们可以使用`netcat`打开socket，在本地TCP 4444端口上监听。启用服务跟踪功能后，我们可以收到如下信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0113beadefcca1d2fb.png)

非常有趣！我们收到了一个HTTP `OPTIONS`请求。根据`User-Agent`头部字段，我们可知这是一个WebDAV请求，但目前我们得不到更多信息。基于这些现象，我们知道该服务可以使用WebDAV来通信，因此我们应该回复并发送身份认证请求。

为了完成该任务，我创建了一个简单的PowerShell脚本，使用`System.Net.Sockets.TcpListener`对象在任意端口上监听，然后向连接该socket的第一个客户端发送一个硬编码的HTTP响应。我们准备发送给客户端的HTTP响应数据如下：

```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: NTLM
```

如果大家非常熟悉Web应用渗透测试，那么应该经常会遇到带有`Basic`值的`WWW-Authenticate`头（比如Apache `htpasswd`），但不一定经常碰到带有`NTLM`的值。通过这个值，我们能够要求客户端使用3次NTLM认证方案来进行身份认证。这里顺便提一下，如果大家想了解关于NTLM的背景知识，可以参考[NTLM中继](https://en.hackndo.com/ntlm-relay/)的研究文章。

脚本运行后，我们能看到如下结果：

[![](https://p4.ssl.qhimg.com/t019f90931f2d8b855d.png)](https://p4.ssl.qhimg.com/t019f90931f2d8b855d.png)

初步分析，目标服务似乎同意发起NTLM认证过程，向我们发送NTLM NEGOTIATE请求。我们可以通过Wireshark来确认这一点：

[![](https://p0.ssl.qhimg.com/t01d5ac8032b65846ea.png)](https://p0.ssl.qhimg.com/t01d5ac8032b65846ea.png)

这是个不错的开头，表示我们的研究方向没有偏差，但我们还需要确认最后一个因素：“协商身份”标志。

关于NTLM认证协议的文档非常详细，我们可以看到该协议中使用的每条信息的详细结构。其中有个[文档](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/99d90ff4-957f-4c8a-80e4-5bfe5a9a9832)解释了`NEGOTIATE`消息中`NegotiateFlags`值的计算方式。在官方文档中，我们可以找到关于`Identify`标志的一段话：

[![](https://p2.ssl.qhimg.com/t018d035f596aaf6d9c.png)](https://p2.ssl.qhimg.com/t018d035f596aaf6d9c.png)

因此，如果设置了该标志位，客户端会通知服务端，表示自己只能请求模拟级别为`SecurityIdentification`的令牌。也就是说，如果设置了该标志位，我们将无功而返，无法拿到合适的模拟令牌。

在Wireshark中我们可以检查该标志位的设置情况：

[![](https://p2.ssl.qhimg.com/t01740475e9107b10ee.png)](https://p2.ssl.qhimg.com/t01740475e9107b10ee.png)

事实证明，`Identify`标志位并没有被设置！

这意味着我们可以绕过补丁，拿到模拟令牌，使用该令牌在`NT AUTHORITY\SYSTEM`上下文执行任意代码。接下来我们只需要完成NTLM认证过程即可，以便将原始的NTLM数据转换成可以使用的令牌。这里我就不展开分析，相关内容可以参考各种Potato漏洞利用工具的原理。

我开发了一个PoC，运行结果如下图所示：

[![](https://p0.ssl.qhimg.com/t018bb9b4e09a1a5f19.png)](https://p0.ssl.qhimg.com/t018bb9b4e09a1a5f19.png)



## 0x04 一些小细节

为了完整理解漏洞原理，我们还需要做一些工作，详细分析不再赘述，这里我想与大家分享一些小细节。

首先大家可能会注意到一点：服务正在请求的资源为`/tracing`，而不是`/tracing/RASMAN.LOG`，那么为什么会出现这种情况？

由于我们将`\\127.0.0.1[@4444](https://github.com/4444)\tracing`设置为目录路径，因此可能会认为目标服务会使用`\\127.0.0.1[@4444](https://github.com/4444)\tracing\RASMAN.LOG`路径，并且会请求`/tracing/RASMAN.LOG`。如果我们分析`rtutils.dll`中的`TraceCreateClientFile`函数，可以看到在打开日志文件前，该函数会检查`TraceCreateClientFile`值中指定的目录是否存在。

如下图所示，如果`CreateDirectory`成功执行（即目标目录不存在，且被成功创建），那么该函数会立即返回。在这种情况下，日志文件永远不会被打开，我们需要禁用跟踪功能，重新启用服务。也就是说，如果想让`TraceCreateClientFile`成功完成，`CreateDirectory`必须返回失败值。

[![](https://p1.ssl.qhimg.com/t01929ac6d7585593ec.png)](https://p1.ssl.qhimg.com/t01929ac6d7585593ec.png)

我们WebDAV服务器收到的第一个HTTP请求实际上对应的正是这个初始化检查过程。此外，`CreateDirectory`实际上只是`NtCreateFile`函数的一个封装函数（在Windows上同样所有对象都是文件）。

`CreateDirectory`函数使用起来非常方便，但有一个问题：该函数并不能设置自定义标志，比如用来限制令牌模拟级别的标志，这也解释了为什么我们能够通过这种技巧拿到可用的模拟令牌。

```
BOOL CreateDirectoryW(
  LPCWSTR               lpPathName,
  LPSECURITY_ATTRIBUTES lpSecurityAttributes
);
```

那么如果服务端通过强化版的`CreateFile`文件来请求`/tracing/RASMAN.LOG`时会出现什么情况？为了回答该问题，我编译了如下代码：

```
HANDLE hFile = CreateFile(
    argv[1], 
    GENERIC_READ | GENERIC_WRITE, 
    0, 
    NULL, 
    OPEN_EXISTING, 
    SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION, // &lt;- Limited token
    NULL);
if (hFile)
`{`
    wprintf(L"CreateFile OK\n");
    CloseHandle(hFile);
`}`
else
`{`
    PrintLastErrorAsText(L"CreateFile");
`}`
```

然后我们可以不必等待`RASMAN`服务连接，而是以低权限用户身份，通过该测试应用来触发WebDAV访问行为。测试结果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c6ffcc10a4f2d371.png)

尽管我们在`CreateFile`函数调用中设置了`SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION`标志，我们还是能够拿到带有`SecurityImpersonation`模拟级别的令牌！因此我们可以得出结论：`WebClient`服务同样存在缺陷。



## 0x05 总结

微软在早期部署的安全补丁可以阻止恶意服务器应用程序利用Service Tracing功能获取可用的模拟令牌，在本文中，我们介绍了如何轻松绕过这种安全机制。这里我还得感谢另一个小伙伴，他几年前写的[MS16-075](https://github.com/NotGlop/SysExec)利用代码给了我不少启发。

后续我不一定发布利用工具，由于许多Service Tracing键值可以被触发，因此想开发出一款可用的工具还需要一些工作要处理。此外如果我们想利用这种方式，还需满足一个前提条件：目标系统上必须安装并启用`WebClient`服务。尽管这是Workstation版系统上的默认设置，但并不适用于Server版系统。在Server系统上，我们需要通过附加功能来安装/启用WebDAV组件。

这里我们还可以继续研究，比如我们可以去分析为什么来自`WebClient`的请求并没有在调用`CreateFile`时考虑到`SECURITY_IDENTIFICATION`标志。在我看来这应该算是一个漏洞，但官方不一定也这么认为。



## 0x06 参考资料
<li>CVE-2010-2554<br>[https://www.cvedetails.com/cve/CVE-2010-2554/](https://www.cvedetails.com/cve/CVE-2010-2554/)
</li>
<li>MS10-059 – Vulnerabilities in the Tracing Feature for Services Could Allow Elevation of Privilege<br>[https://docs.microsoft.com/en-us/security-updates/securitybulletins/2010/ms10-059](https://docs.microsoft.com/en-us/security-updates/securitybulletins/2010/ms10-059)
</li>
<li>GitHub – Chimichurri exploit<br>[https://github.com/Re4son/Chimichurri/](https://github.com/Re4son/Chimichurri/)
</li>
<li>Hackndo – NTLM Relay<br>[https://en.hackndo.com/ntlm-relay/](https://en.hackndo.com/ntlm-relay/)
</li>
<li>MS16-075 exploit leveraging the WebClient service<br>[https://github.com/NotGlop/SysExec](https://github.com/NotGlop/SysExec)
</li>