
# 【技术分享】Windows8.1中的沙箱逃逸问题


                                阅读量   
                                **122541**
                            
                        |
                        
                                                                                                                                    ![](./img/85633/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2015_05_01_archive.html?m=0](https://googleprojectzero.blogspot.com/2015_05_01_archive.html?m=0)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85633/t016d45aed4b75920db.jpg)](./img/85633/t016d45aed4b75920db.jpg)

翻译：[Ox9A82](http://bobao.360.cn/member/contribute?uid=2676915949)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**

这篇文章要讲解一个Windows 8.1系统中的未被修补的漏洞，这个漏洞可以允许你对作业（job object）的限制进行逃逸。从而可以有助于开发Chrome浏览器中的沙盒逃逸利用程序，也适用于类似的其它沙盒保护机制。

如果你正试图开发一个款用户模式的安全沙盒程序，那么你是在依赖于系统底层机制的“施舍”。因为，就算你使尽了浑身解数用上了各种安全机制，有时操作系统本身的编写人员就会断送掉你的努力。这本来是我在Shmoocon and Nullcon上面的演讲话题，主题是在Windows系统上保证一个用户态沙盒安全可靠的困难性。

<br>

**Windows 作业对象**

我们首先讲解一下Windows里的Job object到底是什么和Chrome利用它干什么。严格上来说作业其实跟安全没什么关系。job object是一种把进程分组起来管理，然后限制访问通用资源的数量和种类的方式。如果你熟悉Unix，那么它很类似ulimit而且功能更强大一些。一个很明确的作用，就是用它来限制一个进程能做的事情。举例来说，Chrome渲染器进程属于以下的job object。

[![](./img/85633/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bb4cb406cd4f174f.png)

这个作业对象限制了进程访问一些UI的功能，比如剪贴板。但是它同时还限制了作业中的活动进程只能有一个。这意味着如果你想在作业中新建一个子进程将会被拒绝，并且这项措施是在内核中实现的。当你使用一个受限的token运行时，这只是一个障碍而已。然而，当使用一个普通的用户时你可以使用系统服务例如：WMI或者计划任务来逃逸。

存在一些漏洞会受益于创建子进程，所以打破作业的限制对于构造利用链是很有用的。接下来，我们来看一下可以让我们打破作业对象限制的漏洞。

<br>

**控制台驱动的漏洞**

在早期版本的Windows系统中（XP及之前），控制台窗口由客户端-服务器运行时子系统负责处理，比如广为人知的CSRSS。这个子系统实现Win32窗口系统的用户态部分。但是这样就有一个不利条件，你不能正确应用主题到窗口上，这就是为什么控制台窗口看起来与XP系统不协调。因此在Windows的更高版本中，引入了一个新进程，conhost.exe，它将在用户的桌面上生成以处理控制台窗口。然而，CSRSS仍然参与到创建conhost进程的新实例中。

所有在Windows 8.1中改变。代替CSRSS负责，引入了一个新的内核驱动程序condrv.sys。驱动程序公开设备对象 Device  ConDrv，可以从任何用户上下文访问，即使一个严重锁定作为Chrome渲染器。事实上，没有已知的方法来删除访问驱动程序。使用设备IO控制代码将命令发送到驱动程序。感兴趣的命令是CdpLaunchServerProcess，负责创建conhost可执行文件。直接调用它是有点涉及，特别是在64位版本的Windows，所以我们可以只调用Windows API AllocConsole，它会为我们做。

让我们看看CdpLaunchServerProcess调用的创建conhost.exe进程新实例的代码。



```
NTSTATUS CdpCreateProcess(PHANDLE handle, 
                          HANDLE token_handle, 
                          PRTL_USER_PROCESS_PARAMETERS pp) {  
  HANDLE thread_handle;
  NTSTATUS result;    
  PROCESS_ATTRIBUTE_LIST attrib_list;
  SetProcessExecutable(&amp;attrib_list, L"\SystemRoot\System32\Conhost.exe");
  SetProcessToken(&amp;attrib_list, token_handle);
  result = ZwCreateUserProcess(
             handle,
             &amp;thread_handle,
             ...,
             PROCESS_BREAKAWAY_JOB,  // Process Flags
             CREATE_SUSPENDED,       // Thread Flags
      ...,                         
             &amp;attrib_list);
  if ( result &lt; 0 ) 
    *handle = NULL;
  else
    ObCloseHandle(thread_handle, 0);    
  return result;
}
```

在这段与漏洞直接相关的代码中有两个非常重要的事情需要注意。首先，它调用一个Zw形式的系统调用NtCreateUserProcess。这个前缀表示将调用系统调用，就像它是来自内核模式而不是用户模式的系统调用。这是很重要的，因为它意味着任何安全检查都会在进程创建过程中被绕过。如果驱动程序调用正常的Nt形式函数，它将不可能从像Chrome渲染器那样的环境中进行逃逸，如果没有它conhost.exe文件就无法打开（试图打开会返回拒绝访问），使这个函数很快失效。

第二个重要的事情是传递PROCESS_BREAKAWAY_JOB标志作为进程标志。虽然这个函数没有文档，但是通过逆向工程的内核代码，你会发现这个标志的意思是新进程不应该与父进程处于一个作业中。这意味着一个受限的作业对象可以被逃逸。当在内核中处理这个标志期间，会检查SeTcbPrivilege;然而，当从内核模式调用时，不管调用者是谁这个检查都会被绕过。

最终结果是：

文件安全检查被绕过，导致conhost进程被创建。

因为PROCESS_BREAKAWAY_JOB标记已通过，因此具有限制性的作业对象将会被逃逸。

对于受限的作业对象（如Chrome GPU进程或Adobe Reader）的某些用户，你想利用这个问题的所需的全部操作就是调用AllocConsole。但是，我们将看到对于Chrome渲染器来说它不是那么简单的。

在Chrome渲染器中利用这个问题

我们想去尝试利用一下Chrome渲染器，Chrome渲染器是Chrome中使用最多的锁定沙箱进程。我们碰到的第一个挑战是让代码在渲染器的上下文中运行以测试这个漏洞。

渲染器中的通用测试代码

最显而易见的想法就是使用DLL注入，不幸的是这是说起来容易做起来难的事情。渲染器进程的主令牌限制严格，以至于几乎不可能在磁盘上打开一个文件，所以当你注入一个新的线程来加载DLL文件时，将会打开失败。

现在，你可以重新编译Chromium然后调整一下沙箱的策略，就可以访问磁盘的任意位置。但从M37以后，有一种方法使得我们可以欺骗并利用一个release版程序。M37增加了对DirectWrite字体渲染的支持，为了实现这一点，沙盒策略中添加了一条允许读取Windows字体目录。因此，如果我们将我们的DLL放入％windir％ Fonts我们就可以让它加载。当然，为了实现这一点，你需要在系统上以管理员身份执行代码，因此它不会对Chrome的安全造成威胁。我们还需要调整一些DLL的构建设置，假设你使用Visual Studio，具体来说：

删除manifest，因为它不能在限制性的沙箱中使用。

静态链接DLL，因为一旦初始化你就不能轻易的打开其他DLL了。

<br>

**测试Exploit**

当一个dll文件可由Chrome的渲染器进程打开时，我们就可以注入一个线程，然后调用LoadLibrary以在进程中执行代码。作为我们的第一次测尝试，我们先试着调用AllocConsole，看看会发生什么。如果我们使用进程监视器进行监视，我们会发现正在创建的conhost进程，但它永远不会执行，事实上，它几乎是以负的状态码立即退出的。

[![](./img/85633/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0184380d8d82dcd35c.png)

如果我们把退出状态码转换成一个无符号整数，我们得到了0xC0000022相当于STATUS_ACCESS_DENIED。 显然，很一些什么东西很不高兴，然后杀死了这个过程。为了理解到底发什么了什么，让我们再看一些进程创建后的代码。



```
NTSTATUS CdpLaunchServerProcess(
            FILE_OBJECT* ConsoleFile, 
            PRTL_USER_PROCESS_PARAMETERS pp) {
    HANDLE hToken;
    HANDLE hProcess;
    NTSTATUS status;
    PACCESS_TOKEN tokenobj = PsReferencePrimaryToken();
    ObOpenObjectByPointer(tokenobj, ..., &amp;hToken);
    status = CdpCreateProcess(&amp;hProcess, &amp;hToken, pp);
    if (status &gt;= STATUS_SUCCESS) {
        HANDLE hConsoleFile;
        status = ObOpenObjectByPointer(ConsoleFile, 
                0, 0, GENERIC_ALL, IoFileObjectType,
                UserMode, &amp;hConsoleFile);   
        if (status &gt;= STATUS_SUCCESS) {
            // Modify process command line...
            ZwResumeProcess(hProcess);
        }
    }
    if (status &lt; STATUS_SUCCESS) {
        ZwTerminateProcess(hProcess, status);
    }
    return status;
}
```

这个代码做的是创建进程，然后它创建一个新的句柄到当前控制台设备对象，所以它可以将它在命令行上传递到conhost进程。观察执行流程可以发现，进程被杀死（使用ZwTerminateProcess）的唯一方式是，如果ObOpenObjectByPointer在尝试创建新的句柄时返回STATUS_ACCESS_DENIED。但是这怎么可能发生？我们最初就是这么打开设备文件的，不应该也能够用相同的访问权限再次打开？事实却不是这样的，因为FILE_OBJECT有一个相关的安全描述符，DACL没有给我们受限令牌的GENERIC_ALL访问权限。正如我们在下面的截图中可以看到的，我们缺少一个渲染器的令牌限制SID（S-1-0-0）的条目，它允许限制令牌成功检查。

[![](./img/85633/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019de1c93e8021f46e.png)

不要被RESTRICTED组条目欺骗。RESTRICTED组只是在使用受限令牌时的约定，除非令牌是作为受限制的SID创建的，否则它不会起任何作用。那么这意味着我们永远都不能在Chrome中利用这个bug？当然不是，我们只需要了解FILE_OBJECT的DACL是如何设置的。

与通常从父容器继承其DACL的文件和注册表键不同，内核对象从当前访问令牌中的特殊字段获取其默认的DACL。我们可以通过使用TokenDefaultDacl作为信息类来传递适当的结构到SetTokenInformation来修改当前令牌的默认DACL。我们可以做到这一点，而不需要任何特殊权限。但是要把DACL设置为什么呢？如果我们查看访问令牌的已启用组，会发现我们只有当前用户SID和登录SID。然而，由于令牌也是受限令牌，我们需要授予对受限SID（S-1-0-0，NULL SID）的访问权限，否则访问检查仍会失败。因此，让我们更改默认DACL以指定对登录SID和NULL SID的完全访问权限。



```
void SetCurrentDacl()
{
    HANDLE hToken;
    if (OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &amp;hToken))
    {       
        WCHAR sddl[256];
        PSECURITY_DESCRIPTOR psd = nullptr;
        StringCchPrintf(sddl, _countof(sddl), 
                    L"D:(A;;GA;;;%ls)(A;;GA;;;S-1-0-0)", GetLogonSid());
        if (ConvertStringSecurityDescriptorToSecurityDescriptor(sddl, 
                    SDDL_REVISION_1, &amp;psd, nullptr))
        {
            BOOL present;
            BOOL defaulted;
            PACL dacl;
            GetSecurityDescriptorDacl(psd, &amp;present, &amp;dacl, &amp;defaulted);
            TOKEN_DEFAULT_DACL default_dacl;
            default_dacl.DefaultDacl = dacl;
            SetTokenInformation(hToken, TokenDefaultDacl, 
                    &amp;default_dacl, sizeof(default_dacl));               
            LocalFree(psd);
        }       
    }
}
```

现在在设置当前DACL后，我们可以再试一次，但AllocConsole仍然失败。然而，看看错误代码，我们至少已经解决了最初的问题。进程监视器显示进程的退出代码为STATUS_DLL_NOT_FOUND，它告诉我们发生了什么。

当进程的第一个线程运行时，它实际上并不直接在进程入口点开始。相反，它在NTDLL中运行一段特殊的代码（LdrInitializeThunk）来初始化当前进程。正如Ldr前缀表明的（它是Loader的简称），该函数负责扫描进程的导入DLL，将它们加载到内存并调用它们的初始化函数。在这种情况下，进程令牌是受限制的，我们甚至打不开典型的DLL文件。幸运的是，在创建的进程和用ZwResumeProcess恢复初始线程之间有一个时间窗口。如果我们可以在这个窗口中捕获进程，我们就可以把进程初始化为一个空的shell。但我们怎么做呢？

<br>

**捕获新进程**

一个显而易见的利用方法是在时间窗口期间打开新进程，然后使用这个句柄调用NtSuspendProcess。这可以实现，因为挂起/恢复操作引用引用计数。该进程以暂停计数——1开始，因为内核驱动程序使用CREATE_SUSPENDED标志创建了初始线程，因此，如果我们快速调用NtSuspendProcess，我们可以将其增加到2。然后，驱动程序通过调用ZwResumeProcess减少计数，但这只会将计数降低到1，内核将挂起线程。然后，我们可以操作新进程以删除初始化代码并在作业对象外部运行。

但这个计划有一个比较大的问题。通常，当创建一个新进程时，将返回该进程的句柄，但这里不是这样的情况，因为内核驱动程序在返回到调用者之前会关闭内核模式句柄。因此，我们需要通过其PID打开进程，但估计这可能会是很难办的。因为现代的Windows系统并不是简单的依次递增PID值，而是会在一段时间后回收重新使用旧的PID值。我们可以通过猜测，但每一次错误的猜测都是在浪费时间。你会发现，暴力的方法是几乎不可能奏效的。

所以我们被卡在这里了吗？当然不是，我们只需要使用进一步的未文档化的功能。内核暴露了一个系统调用，NtGetNextProcess，顾名思义，它用来获得下一个进程。但下一个是什么呢？如果你已经对Windows内部原理有所了解，你会知道进程对象在内核中的一个链表被链接到一起。这个系统调用将句柄放入一个进程对象中，并找到链表中可由当前用户打开的下一个进程。

[![](./img/85633/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018291ebf1d8eff961.png)

在默认情况下，是没有其他进程可以被当前进程在列表中打开的，甚至它本身，这是由于那个讨厌的默认DACL。这意味着正常的NtGetNextProcess调用总会失败。当新的conhost进程创建时，它继承了我们可以访问的新的修改了的默认DACL，这意味着我们可以使用一个非常小的循环调用NtGetNextProcess直到成功。返回的句柄几乎肯定是conhost，所以我们可以快速暂停进程，现在可以争取尽可能多的时间，这是我们喜欢的。 我们需要在一个线程中这样做，因为AllocConsole将阻塞，但这不是一个问题。 例如：



```
HANDLE GetConhostProcess()
{       
    HANDLE hCurr = nullptr;
    while (!hCurr)
    {
        hCurr = nullptr;
        if (NtGetNextProcess(hCurr, MAXIMUM_ALLOWED,
                             0, 0, &amp;hCurr) == 0)
        {
            NtSuspendProcess(hCurr);
            return hCurr;
        }
    }
    return 0;
}
```

因此，通过处理conhost进程，我们可以修改LdrInitializeThunk方法来防止它失败并注入一些shellcode。你只有NTDLL服务，因为没有其他DLL会被映射。我们仍然达成了目标，你现在可以对一个受限的Job对象进行逃逸了，即使是在这样一个锁定的进程中。你现在要用这种力量去做什么完全取决于你自己。

<br>

**结论**

那么这有什么用呢？好吧，我是开玩笑的，至少从沙箱里面直接逃逸是不行的。它只是削弱了一些防御，并且扩展了攻击面，以便利用其他问题。我可以理解为什么微软不想修复它，因为它的行为以这种方式实现向后兼容性，所以改变它将是很困难的。这说明我相信它可以在当前进程调用API的安全上下文中工作，因为很少有应用程序使用这种限制性令牌作为应用程序沙箱。

此外，Chrome还在努力进一步减少安全方面的问题。例如，当作业中断删除强制的作业UI限制时，Chrome现在在所有受影响的平台上使用win32k锁定，据我所知，即使在子进程中也不能进行禁用。安全缓解措施在继续发展，利用了平台的各种新特性，然而安全问题的回归是不可避免的。开发良好的沙箱不应依赖于任何一个平台功能的安全性，因为该功能可能随时中断掉。
