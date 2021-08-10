> 原文链接: https://www.anquanke.com//post/id/249863 


# 从mimikatz学习Windows安全之访问控制模型（一）


                                阅读量   
                                **22951**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t019dd4de7932e4e563.jpg)](https://p0.ssl.qhimg.com/t019dd4de7932e4e563.jpg)



作者：Loong716@[Amulab](https://github.com/Amulab)

## 0x00 前言

[Mimikatz](https://github.com/gentilkiwi/mimikatz)是法国安全研究员Benjamin Delpy开发的一款安全工具。渗透测试人员对mimikatz印象最深的肯定就是抓取Windows凭证，但作者对它的描述是**“a tool I’ve made to learn C and make somes experiments with Windows security.”**，其实它的功能不仅仅是抓取凭证，还包含了很多Windows安全相关的技术和知识

这里借用**[@daiker](https://github.com/daiker)**师傅的思维导图，mimikatz的模块大致可分为几个部分：

[![](https://p1.ssl.qhimg.com/t0186dd583b07f40429.png)](https://p1.ssl.qhimg.com/t0186dd583b07f40429.png)

因此文章也会大致分为windows 访问控制模型，windows 凭据以及加解密，windows AD 安全，windows 进程以及服务，mimikatz 其他模块五个小系列。之前自己一直想分析mimikatz的相关功能，主要是出于以下原因：
- mimikatz中有许多功能利用了Windows的一些机制和特性，以changentlm为例，其利用MS-SAMR协议修改用户的密码，我们再根据MS-SAMR或RPC进行知识延伸，肯定也有不少收获
- mimikatz中涉及大量内存的操作，其中运用的内存Patch技术也被经常应用于一些安全机制的绕过（如绕过AMSI、Credential Guard等），于是自己想在分析过程中通过windbg学到一些调试的技巧
- mimikatz在实战中被杀的很厉害，了解相应原理可以自己实现相应功能
- 学习/练习C语言 😀
mimikatz中与Windows访问控制模型相关的有privilege、token、sid三个模块，其分别对应特权、访问令牌、安全标识符三个知识，本文主要分析token模块，并简要介绍Windows访问控制模型

由于mimikatz代码逻辑较为复杂，涉及大量回调，因此文中代码都是经过简化的。文章可能也会有一些技术上或者逻辑上的错误，还请师傅们指正



## 0x01 访问控制模型简介

Windows访问控制模型有两个基本组成部分：
- 访问令牌(Access Token)：包含有关登录用户的信息
- 安全描述符(Security Descriptor)：包含用于保护安全对象的安全信息
### <a class="reference-link" name="1.%20%E8%AE%BF%E9%97%AE%E4%BB%A4%E7%89%8C(Access%20Token)"></a>1. 访问令牌(Access Token)

访问令牌(Access Token)被用来描述一个进程或线程的安全上下文，用户每次登录成功后，系统会为其创建访问令牌，该用户的所有进程也将拥有此访问令牌的副本

当线程与安全对象进行交互或尝试执行需要特权的系统任务时，系统使用访问令牌来标识用户。使用windbg查看进程的token，其包含信息如下图所示：

[![](https://p0.ssl.qhimg.com/t017902d523dd3cb449.png)](https://p0.ssl.qhimg.com/t017902d523dd3cb449.png)

[![](https://p2.ssl.qhimg.com/t01fb6af58326a08cbe.png)](https://p2.ssl.qhimg.com/t01fb6af58326a08cbe.png)

[![](https://p0.ssl.qhimg.com/t017f2c765ea8634b98.png)](https://p0.ssl.qhimg.com/t017f2c765ea8634b98.png)

### <a class="reference-link" name="2.%20%E5%AE%89%E5%85%A8%E6%8F%8F%E8%BF%B0%E7%AC%A6(Security%20Descriptor)"></a>2. 安全描述符(Security Descriptor)

安全描述符(Security Descriptor)包含与安全对象有关的安全信息，这些信息规定了哪些用户/组可以对这个对象执行哪些操作，安全描述符主要由以下部分构成：
- 所有者的SID
- 组SID
- 自主访问控制列表（DACL），规定哪些用户/组可以对这个对象执行哪些操作
- 系统访问控制列表（SACL），规定哪些用户/组的哪些操作将被记录到安全审计日志中
在windbg中查看一个安全对象的安全描述符，可以清晰的看到安全描述符的组成：

[![](https://p4.ssl.qhimg.com/t0132cd1a48d4a0ad75.png)](https://p4.ssl.qhimg.com/t0132cd1a48d4a0ad75.png)

可以看到该安全描述符的DACL中有三条ACE，ACE的类型都是`ACCESS_ALLOWED_ACE_TYPE`，`Mask`是权限掩码，用来指定对应的权限。以第一条ACE为例，其表示允许SID为S-1-5-32-544的对象能够对该安全对象做0x001fffff对应的操作

### <a class="reference-link" name="3.%20%E6%9D%83%E9%99%90%E6%A3%80%E6%9F%A5%E7%9A%84%E8%BF%87%E7%A8%8B"></a>3. 权限检查的过程

当某个线程尝试访问一个安全对象时，系统根据安全对象的ACE对照线程的访问令牌来判断该线程是否能够对该安全对象进行访问。通常，系统使用请求访问的线程的主访问令牌。但是，如果线程正在模拟其他用户，则系统会使用线程的模拟令牌

此时将在该安全对象的DACL中按顺序检查ACE，直到发生以下事件：
- 某一条拒绝类型的ACE显式拒绝令牌中某个受信者的所有访问权限
- 一条或多条允许类型的ACE允许令牌中列出的受信者的所有访问权限
- 检查完所有ACE但没有一个权限显式允许，那么系统会隐式拒绝该访问
我们以微软文档中的图片为例，描述一下整个过程：

[![](https://p3.ssl.qhimg.com/t01f75e5403d293c694.png)](https://p3.ssl.qhimg.com/t01f75e5403d293c694.png)
1. 线程A请求访问安全对象，系统读取ACE1，发现拒绝Andrew用户的所有访问权限，而线程A的访问令牌是Andrew，因此拒绝访问，并不再检查ACE2、ACE3
1. 线程A请求访问，系统按顺序读取ACE，ACE1不适用，读取到ACE2发现适用，再读取到ACE3也适用，因此最终该用户拥有对该安全对象的读、写、执行权限


## 0x02 Mimikatz的Token模块

Mimikatz的token模块共有5个功能：
<li>
**token::whoami**：列出当前进程/线程的token信息</li>
<li>
**token::list**：列出当前系统中存在的token</li>
<li>
**token::elevate**：窃取其他用户的token</li>
<li>
**token::run**：利用某用户权限运行指定程序</li>
<li>
**token::revert**：恢复为原来的token</li>
### <a class="reference-link" name="1.%20token::whoami"></a>1. token::whoami

该功能用于列出当前进程/线程的token信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011698e25f81c60ece.png)

只有一个可选参数`/full`，当指定该参数时会打印出当前token的组信息和特权信息：

[![](https://p1.ssl.qhimg.com/t01e09059d09111178a.png)](https://p1.ssl.qhimg.com/t01e09059d09111178a.png)

该功能的原理大致如下：
1. 通过`OpenProcess()`获取当前进程/线程的句柄
1. 调用`GetTokenInformation()`获取token的各种信息并输出
其核心为调用`GetTokenInformation()`来获取token的各种信息，我们先来看这个API定义

```
BOOL GetTokenInformation(
  HANDLE                  TokenHandle,
  TOKEN_INFORMATION_CLASS TokenInformationClass,
  LPVOID                  TokenInformation,
  DWORD                   TokenInformationLength,
  PDWORD                  ReturnLength
);
```

其中第二个参数是一个`TOKEN_INFORMATION_CLASS`枚举类型，我们可以通过指定它的值来获取token指定的信息

```
typedef enum _TOKEN_INFORMATION_CLASS `{`
  TokenUser,
  TokenGroups,
  TokenPrivileges,
  TokenOwner,
  TokenPrimaryGroup,
  TokenDefaultDacl,
  TokenSource,
  ...
`}` TOKEN_INFORMATION_CLASS, *PTOKEN_INFORMATION_CLASS;
```

例如获取token的SessionID并输出，可以使用以下代码：

```
if (!GetTokenInformation(hToken, TokenSessionId, &amp;sessionId, sizeof(TokenSessionId), &amp;dwSize))
`{`
    wprintf(L"[!] GetTokenInformation error: %u\n", GetLastError());
`}`

wprintf(L"\t%-21s: %u\n", L"Session ID", sessionId);
```

### <a class="reference-link" name="2.%20token::list"></a>2. token::list

该功能是获取当前系统中所有的token，注意使用前需要先获取`SeDebugPrivilege`，否则列出的token不全

[![](https://p3.ssl.qhimg.com/t011017fbc86b52fc1c.png)](https://p3.ssl.qhimg.com/t011017fbc86b52fc1c.png)

该功能原理大致如下：
1. 调用`NtQuerySystemInformation()`获取系统进程信息（如进程PID等）
1. 循环遍历所有进程的PID，使用`token::whoami`功能中的方法对指定token信息进行输出
`NtQuerySystemInformation()`用来检索指定的系统信息：

```
__kernel_entry NTSTATUS NtQuerySystemInformation(
  SYSTEM_INFORMATION_CLASS SystemInformationClass,
  PVOID                    SystemInformation,
  ULONG                    SystemInformationLength,
  PULONG                   ReturnLength
);
```

其第一个参数是一个`SYSTEM_INFORMATION_CLASS`枚举类型，我们同样可以指定不同参数来获取不同的系统信息

[![](https://p4.ssl.qhimg.com/t01e87545db2f0c951d.png)](https://p4.ssl.qhimg.com/t01e87545db2f0c951d.png)

以获取系统进程名和PID为例，代码如下：

```
PSYSTEM_PROCESS_INFORMATION pProcessInfo = NULL;
DWORD flag = TRUE;

pProcessInfo = (PSYSTEM_PROCESS_INFORMATION)malloc(dwSize);
ntReturn = NtQuerySystemInformation(SystemProcessInformation, pProcessInfo, dwSize, &amp;dwSize);

while (ntReturn == STATUS_INFO_LENGTH_MISMATCH) `{`
    free(pProcessInfo);
    pProcessInfo = (PSYSTEM_PROCESS_INFORMATION)malloc(dwSize);
    ntReturn = NtQuerySystemInformation(SystemProcessInformation, pProcessInfo, dwSize, &amp;dwSize);
`}`

while (flag)
`{`
    if (pProcessInfo-&gt;NextEntryOffset == 0)
        flag = FALSE;

    wprintf(L"%-15d", (DWORD)pProcessInfo-&gt;UniqueProcessId);
    wprintf(L"%-50s", (wchar_t*)pProcessInfo-&gt;ImageName.Buffer);

    pProcessInfo = (PSYSTEM_PROCESS_INFORMATION)((BYTE*)pProcessInfo + pProcessInfo-&gt;NextEntryOffset);
`}`
```

**PS：**按照该思路，理论上利用`CreateToolhelp32Snapshot()` + `Process32First()`遍历进程PID也可以实现该功能

### <a class="reference-link" name="3.%20token::elevate"></a>3. token::elevate

该模块用于窃取指定用户的token，共有7个可选参数，这些参数主要用来指定要窃取的token，如果不指定参数则默认窃取`NT AUTHORITY\SYSTEM`的token
<li>
**/id**：指定目标token的TokenID</li>
<li>
**/domainadmin**：窃取域管的token</li>
<li>
**/enterpriseadmin**：窃取企业管理员的token</li>
<li>
**/admin**：窃取本地管理员的token</li>
<li>
**/localservice**：窃取Local Service权限的token</li>
<li>
**/networkservice**：窃取Network Service权限的token</li>
<li>
**/system**：窃取SYSTEM权限的token</li>
假设我们现在在目标机器上发现的域管权限的token

[![](https://p2.ssl.qhimg.com/t01f3b136ab52bfecdd.png)](https://p2.ssl.qhimg.com/t01f3b136ab52bfecdd.png)

我们可以指定目标TokenID，或者使用`/domainadmin`来窃取域管的token，执行成功后可以看到当前线程已经拥有域管的模拟令牌：

[![](https://p2.ssl.qhimg.com/t016fc5700dd10f9d46.png)](https://p2.ssl.qhimg.com/t016fc5700dd10f9d46.png)

然后我们就可以在当前mimikatz上下文中使用域管身份执行操作了，如DCSync

[![](https://p4.ssl.qhimg.com/t0160a6cc8dd8da89c8.png)](https://p4.ssl.qhimg.com/t0160a6cc8dd8da89c8.png)

该功能大致过程如下：
1. 通过`OpenProcess()`获取当前进程/线程的句柄
1. 调用`OpenProcessToken()`打开与进程相关的token句柄
1. 使用`DuplicateTokenEx()`使用目标进程token创建一个新的模拟token
1. 调用`SetThreadToken()`设置当前线程的token为上一步创建的新的模拟token
由于窃取token是Access Token利用的重点，该过程放在本文后面分析

### <a class="reference-link" name="4.%20token::run"></a>4. token::run

该功能是使用指定的token来运行程序，也可以使用`token::elevate`中的几个参数来指定运行程序的token，除此之外还有一个参数：
<li>
**/process**：指定要运行的程序，默认值为whoami.exe</li>
[![](https://p1.ssl.qhimg.com/t01b0eaf7251ee4780e.png)](https://p1.ssl.qhimg.com/t01b0eaf7251ee4780e.png)

其原理前三步与`token::elevate`大致相同，区别在于使用`DuplicateTokenEx()`窃取token后，该功能使用`CreateProcessAsUser()`来使用新的primary token创建一个进程

```
BOOL CreateProcessAsUserA(
  HANDLE                hToken,
  LPCSTR                lpApplicationName,
  LPSTR                 lpCommandLine,
  LPSECURITY_ATTRIBUTES lpProcessAttributes,
  LPSECURITY_ATTRIBUTES lpThreadAttributes,
  BOOL                  bInheritHandles,
  DWORD                 dwCreationFlags,
  LPVOID                lpEnvironment,
  LPCSTR                lpCurrentDirectory,
  LPSTARTUPINFOA        lpStartupInfo,
  LPPROCESS_INFORMATION lpProcessInformation
);
```

创建进程后，利用匿名管道做进程间通信，将新创建进程的标准输出写入到匿名管道的write端，从管道read端读取数据进行回显（在webshell等非交互场景下很有用）

```
if (CreatePipe(&amp;hStdoutR, &amp;hStdoutW, &amp;saAttr, 0))
`{`
    SetHandleInformation(hStdoutR, HANDLE_FLAG_INHERIT, 0);
    si.cb = sizeof(STARTUPINFO);
    si.hStdOutput = hStdoutW;
    si.hStdError = si.hStdOutput;
    si.dwFlags |= STARTF_USESTDHANDLES;

    if (CreateProcessWithTokenW(hDupToken, LOGON_WITH_PROFILE, NULL, cmd, CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT, NULL, NULL, &amp;si, &amp;pi))
    `{`
        CloseHandle(si.hStdOutput);
        si.hStdOutput = si.hStdError = NULL;
        while (ReadFile(hStdoutR, resultBuf, sizeof(resultBuf), &amp;dwRead, NULL) &amp;&amp; dwRead)
        `{`
            for (i = 0; i &lt; dwRead; i++)
                wprintf(L"%c", resultBuf[i]);
        `}`

        WaitForSingleObject(pi.hProcess, INFINITE);
        CloseHandle(pi.hThread);
        CloseHandle(pi.hProcess);
    `}`
    else wprintf(L"CreateProcessWithTokenW error 0x%08X\n", GetLastError());

`}`
else wprintf(L"CreatePipe error! 0x%08X\n", GetLastError());
```

### <a class="reference-link" name="5.%20token::revert"></a>5. token::revert

该模块用来清除线程的模拟令牌：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014cc55a99a8be91c1.png)

原理很简单，直接使用`SetThreadToken(NULL, NULL)`即可将当前线程的token清除



## 0x03 令牌窃取

在渗透测试中，窃取token是administrator -&gt; system的常见手法之一，还经常被用于降权等用户切换操作

### <a class="reference-link" name="1.%20%E5%8E%9F%E7%90%86"></a>1. 原理

窃取token主要涉及以下几个API：
1. **OpenProcess**
```
HANDLE OpenProcess(
  DWORD dwDesiredAccess,
  BOOL  bInheritHandle,
  DWORD dwProcessId
);
```

该函数打开指定PID的进程的句柄，需要注意的是第一个参数**dwDesiredAccess**，主要会用到的是以下三个权限
- PROCESS_ALL_ACCESS
- PROCESS_QUERY_INFORMATION (0x0400)
- PROCESS_QUERY_LIMITED_INFORMATION (0x1000)
我在编写窃取Token的代码时，发现对部分进程（如smss.exe、csrss.exe等）调用OpenProcess会出现拒绝访问的情况，查阅网上资料后发现这些进程存在保护，需要使用`PROCESS_QUERY_LIMITED_INFORMATION`权限打开句柄，详情请参考[这篇文章](https://posts.specterops.io/understanding-and-defending-against-access-token-theft-finding-alternatives-to-winlogon-exe-80696c8a73b)
1. **OpenProcessToken**
```
BOOL OpenProcessToken(
  HANDLE  ProcessHandle,
  DWORD   DesiredAccess,
  PHANDLE TokenHandle
);
```

该函数打开与进程相关联的令牌的句柄，其中第二个参数**DesiredAccess**同样用来指定令牌的访问权限，需要以下几个：
- TOKEN_DUPLICATE：复制令牌需要的权限
- TOKEN_QUERY：查询令牌需要的权限
如果要调用`DuplicateTokenEx`需要指定TOKEN_DUPLICATE，如果调用`ImpersonatedLoggedOnUser`则需要指定TOKEN_DUPLICATE和TOKEN_QUERY
1. **DuplicateTokenEx**
```
BOOL DuplicateTokenEx(
  HANDLE                       hExistingToken,
  DWORD                        dwDesiredAccess,
  LPSECURITY_ATTRIBUTES        lpTokenAttributes,
  SECURITY_IMPERSONATION_LEVEL ImpersonationLevel,
  TOKEN_TYPE                   TokenType,
  PHANDLE                      phNewToken
);
```

`DuplicateTokenEx`用来复制现有的令牌来生成一张新令牌，该函数可以选择生成主令牌还是模拟令牌
<li>
**hExistingToken**：指定现有的令牌句柄，可以使用`OpenProcessToken`获得</li>
<li>
**dwDesiredAccess**：用来指定令牌访问权限，需要指定以下几个来支持后面调用`CreateProcessWithToken`：
<ul>
- TOKEN_DUPLICATE：需要复制访问令牌
- TOKEN_QUERY：需要查询访问令牌
- TOKEN_ASSIGN_PRIMARY：将令牌附加到主进程的权限
- TOKEN_ADJUST_DEFAULT：需要更改访问令牌的默认所有者、主要组或 DACL
- TOKEN_ADJUST_SESSIONID：需要调整访问令牌的会话 ID，需要 SE_TCB_NAME 权限
复制完一张新令牌后，我们就可以利用这张新令牌来运行我们指定的进程了
1. **CreateProcessWithTokenW**
```
BOOL CreateProcessWithTokenW(
  HANDLE                hToken,
  DWORD                 dwLogonFlags,
  LPCWSTR               lpApplicationName,
  LPWSTR                lpCommandLine,
  DWORD                 dwCreationFlags,
  LPVOID                lpEnvironment,
  LPCWSTR               lpCurrentDirectory,
  LPSTARTUPINFOW        lpStartupInfo,
  LPPROCESS_INFORMATION lpProcessInformation
);
```

该函数创建一个新进程及其主线程，新进程在指定令牌的安全上下文中运行。我们直接指定前面复制出来的新令牌，使用该令牌创建我们指定的进程即可

### <a class="reference-link" name="2.%20%E5%88%A9%E7%94%A8"></a>2. 利用

根据mimikatz的token模块的原理，简单实现了一个[demo](https://github.com/loong716/CPPPractice/tree/master/TokenTest)，也有许多token相关的工具如incognito等

当获取管理员权限后，我们可以列出系统中进程对应的token：

[![](https://p5.ssl.qhimg.com/t01310d44bcf093df0f.png)](https://p5.ssl.qhimg.com/t01310d44bcf093df0f.png)

然后窃取指定进程的token来运行我们的程序，如直接运行上线马

[![](https://p2.ssl.qhimg.com/t01939f38218ead9903.png)](https://p2.ssl.qhimg.com/t01939f38218ead9903.png)

如果想要拿回程序输出的话，则可以通过管道等进程间通信的方法来回显输出

[![](https://p4.ssl.qhimg.com/t01c9a80a08a856bec2.png)](https://p4.ssl.qhimg.com/t01c9a80a08a856bec2.png)

如果拿到一台机器有域管的进程，那么我们可以直接窃取域管进程的token来进行DCSync攻击

[![](https://p4.ssl.qhimg.com/t01a149e20390a434cf.png)](https://p4.ssl.qhimg.com/t01a149e20390a434cf.png)



## 0x04 参考链接

[https://docs.microsoft.com/](https://docs.microsoft.com/)

[https://github.com/gentilkiwi/mimikatz/](https://github.com/gentilkiwi/mimikatz/)

[https://www.ired.team/offensive-security/privilege-escalation/t1134-access-token-manipulation](https://www.ired.team/offensive-security/privilege-escalation/t1134-access-token-manipulation)

[https://www.slideshare.net/JustinBui5/understanding-windows-access-token-manipulation](https://www.slideshare.net/JustinBui5/understanding-windows-access-token-manipulation)

[https://posts.specterops.io/understanding-and-defending-against-access-token-theft-finding-alternatives-to-winlogon-exe-80696c8a73b](https://posts.specterops.io/understanding-and-defending-against-access-token-theft-finding-alternatives-to-winlogon-exe-80696c8a73b)
