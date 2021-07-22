> 原文链接: https://www.anquanke.com//post/id/241109 


# 津门杯 Injected/Tunnel WP


                                阅读量   
                                **110829**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0148255d1e60944e97.jpg)](https://p1.ssl.qhimg.com/t0148255d1e60944e97.jpg)



周末的时候玩了一下津门杯，感觉遇到了几个比较有意思的题目，这边写一个wp用作记录。

## Injected

这个逆向题目比较有趣，考察了比较多的知识点。

### <a class="reference-link" name="%E5%AF%BB%E6%89%BE%E5%85%A5%E5%8F%A3%E7%82%B9"></a>寻找入口点

首先下载的文件叫做`Dbgview-Infected.exe`，并且整个icon就和Dbgview长得一样，结合题目来看，应该是**修改了一个真正的dbgview**。于是我们用ida打开检查一下，发现整个exe里面多了一个段:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0131f6623aa38225dc.png)

这个`.easyre`明显是外部注入的代码段。但是观察会发现，大部分的地方并不能被解析成代码，大部分的地方不知道如何解释

[![](https://p4.ssl.qhimg.com/t014ff76ab94acfd3b4.png)](https://p4.ssl.qhimg.com/t014ff76ab94acfd3b4.png)

单纯的逆向又会发现这部分的逻辑比较复杂，所以首先需要找到程序的入口点。考虑到这个程序是被静态注入的，那么**只要能够找到原先的程序，进行简单的比较，应该能找到作者修改的部分**<br>
我们这边检查一下文件的属性

[![](https://p0.ssl.qhimg.com/t01af5c4b433612aa68.png)](https://p0.ssl.qhimg.com/t01af5c4b433612aa68.png)

可以发现是4.76.0的dbgview，这个版本的英文版本在网上很难找到下载的软件。不过联想到这个程序打开之后是一个中文的dbgview界面，这个会不会是国内的人汉化之后的版本呢？找了一圈之后真的找到了一个汉化的版本，正好也是4.76.0。于是直接跑一个bindiff对比一下:

[![](https://p5.ssl.qhimg.com/t01508e3b4a1827f53b.png)](https://p5.ssl.qhimg.com/t01508e3b4a1827f53b.png)

对比后发现，确实有两个函数不一样，不过第一个函数`sub_0401a30`感觉可能是bindiff本身识别的问题，实际上代码非常相近。关键是第二个函数`sub_0040f8b0`

[![](https://p1.ssl.qhimg.com/t01ee358a0496dd1df7.png)](https://p1.ssl.qhimg.com/t01ee358a0496dd1df7.png)

可以看到，注入的dbgview中，多了一段强制跳转的逻辑，很显然这就是题目的入口，我们跟随提示找到相关的代码:

```
if ( a2 == 272 )
  `{`
    v23.hInstance = hInstance;
    v23.hwndOwner = dword_44F9E0;
    v23.lStructSize = 76;
    v23.lpstrFilter = "DebugView Dump (*.dmp)";
    v23.lpstrCustomFilter = 0;
    v23.nMaxCustFilter = 0;
    v23.nFilterIndex = 1;
    v23.lpstrFile = aMemoryDmp;
    v23.nMaxFile = 260;
    v23.lpstrFileTitle = 0;
    v23.nMaxFileTitle = 0;
    v23.lpstrInitialDir = 0;
    v23.lpstrTitle = "Open crash dump...";
    v23.nFileOffset = 0;
    v23.nFileExtension = 0;
    v23.lpstrDefExt = "*.dmp";
    v23.lpfnHook = 0;
    v23.Flags = 2103296;
    GetOpenFileNameA(&amp;v23);
    dword_487000 = 65765608;
    JUMPOUT(0x487000);
  `}`
```

这边会将`65765608`赋值给`dword_487000`，此时这个地址会变成:

```
.easyre:00487004 ; ---------------------------------------------------------------------------
.easyre:00487004                 call    loc_4C5B89
.easyre:00487004 ; ---------------------------------------------------------------------------
;---------------------
;---------------------
;---------------------
;---------------------
.easyre:004C5B89                 sub     esp, 2CCh
.easyre:004C5B8F                 push    ebx
.easyre:004C5B90                 push    ebp
.easyre:004C5B91                 push    esi
.easyre:004C5B92                 mov     esi, [esp+2DCh]
.easyre:004C5B99                 xor     ebx, ebx
.easyre:004C5B9B                 push    edi
.easyre:004C5B9C                 mov     edi, ebx
.easyre:004C5B9E                 mov     eax, [esi+238h]
.easyre:004C5BA4                 or      eax, [esi+23Ch
```

这边就是注入地址的真正入口。从代码可以看到，这一段应该是dbgview中解析dmp的时候的相关逻辑，然后我们打开dbgview，和dmp相关的功能只有一处:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d2c0aa736c6e66ed.png)

基本可以确认这边就是真正的程序入口。<br>
回看到题目名称叫做`injected`，出了段注入之外，很容易想到的是**可能存在远程线程注入**。于是这边使用procmon观测程序，并且尝试触发程序入口，会发现有一个子进程启动的过程:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016fa2945bf7933a6c.png)

可以猜测到，这个程序肯定会有一个启动子进程的逻辑。

### <a class="reference-link" name="%E6%B3%A8%E5%85%A5%E4%B8%8E%E5%8A%A8%E6%80%81%E8%B0%83%E8%AF%95"></a>注入与动态调试

由于这段代码会有一些IDA无法处理的异常（或者我配置出现问题），这边使用x32dbg进行调试。首先我们一直调试，会发现整个代码将**00487004+5，也就是我们的call指令之后的几个字节当作了数据段使用，将这个数据段存放在了esi中**。代码检查了当前的数据段，并且发现再偏移238出的qword==0，于是跳转到了`sub_4C6CA9`

[![](https://p4.ssl.qhimg.com/t0155c379e22106c814.png)](https://p4.ssl.qhimg.com/t0155c379e22106c814.png)

在这个函数，程序首先调用`sub_4C7C08`进行内存中的API加载，会加载如下的代码
- VirtualAlloc
- VirtualFree
- RtlExitUserProcess
那之后，程序会分配一个`[edi]`大小的内存堆块，分配一个可读写的内存块。之后会完成一个内存拷贝并且解密的过程。当完成了相关的check之后，便会尝试加载解密后内存中的指定的dll:

[![](https://p1.ssl.qhimg.com/t014eb73941bec5506b.png)](https://p1.ssl.qhimg.com/t014eb73941bec5506b.png)

```
LoadLibrary = LoadFunction(addr, addr[12], addr[13], addr[10], addr[11]);
    addr[12] = LoadLibrary;
    if ( !LoadLibrary )
      return -1;
    v11 = (char *)(addr + 145);
    while ( 1 )
    `{`
      v12 = *v11;
      v13 = 0;
      if ( !*v11 )
        break;
      v14 = v11;
      do
      `{`
        if ( v12 == 59 )
          break;
        if ( v13 &gt;= 0x104 )
          break;
        v14[v35 - v11] = v12;
        ++v13;
        v12 = *++v14;
      `}`
      while ( *v14 );
      if ( !v13 )
        break;
      v35[v13] = 0;
      v11 += v13 + 1;
      ((void (__stdcall *)(char *))addr[12])(v35);
```

之后，会根据edi中指向的edi，完成剩余所有dll中的API导出:

```
if ( addr[144] &gt; 1u )
    `{`
      v16 = addr + 13;
      v17 = addr + 14;
      do  // addr[144] -&gt; kernel32中的API个数
      `{`
        v18 = LoadFunction(addr, *v17, v17[1], addr[10], addr[11]);
        *v16 = v18;
        if ( !v18 )
          goto LABEL_56;
        ++v15;
        v17 += 2;
        ++v16;
      `}`
      while ( v15 &lt; addr[144] );
    `}`
```

之后，代码会比较`[edi+6e4]`处的flag，此时我们的flag为1，于是进入和1相关的处理逻辑:

```
.easyre:004C6E99                 push    edi
.easyre:004C6E9A                 call    sub_4C5FE0
.easyre:004C6E9F                 pop     ecx
.easyre:004C6EA0                 test    eax, eax
.easyre:004C6EA2                 jnz     short loc_4C6EB1
.easyre:004C6EA4                 cmp     dword ptr [edi+56Ch], 2
.easyre:004C6EAB                 jz      loc_4C6FF2
.easyre:004C6EB1
.easyre:004C6EB1 loc_4C6EB1:                             ; CODE XREF: sub_4C6CA9+1F9↑j
.easyre:004C6EB1                 push    edi
.easyre:004C6EB2                 call    sub_4C60C6
.easyre:004C6EB7                 pop     ecx
.easyre:004C6EB8                 test    eax, eax
.easyre:004C6EBA                 jnz     short loc_4C6EC9
.easyre:004C6EBC                 cmp     dword ptr [edi+56Ch], 2
.easyre:004C6EC3                 jz      loc_4C6FF2
```

第一个函数`sub_4C5FE0`内部首先load了`Amsi`的dll，并且将其中的
- AmsiScanString
- AmsiScanBuffer
这两个API进行了patch:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f79cdc4af9362285.png)

上述的两个API为微软提供的一个可以用于扫描缓冲区/字符串中的恶意软件的API

(patch后的相关函数)<br>
第二个函数`sub_4C60C6`则提供了关于wldp的load，并且将以下的函数进行了patch
- WldpQueryDynamicCodeTrust
- WldpIsClassInApprovedList
这两个函数是wldp提供的用于支持`DynmaicCodePolicy`策略的函数，详情可以参考[看雪的这篇文章](https://bbs.pediy.com/thread-230150.htm#msg_header_h2_9)，大致来讲就是，这两个API可以检查内存中的一些函数是否发生了hook，以及一些CLSID接口的函数是否是可信任的。通常来说，这两个函数可以用来检查前面提到的`AmsiScanString`，`AmsiScanBuffer`是否发生了hook，以及一些com对象是否被劫持。

完成了一些防御绕过之后，进入如下的逻辑:

```
switch ( *v20 )
          `{`
            case 3:
            case 4:
              sub_4C73B3(addr, v20);
              break;
            case 1:
            case 2:
              if ( sub_4C6AA9(addr, v20, v34) )
                sub_4C706E(addr, v20, v34);
              sub_4C6581(addr, v34);
              break;
            case 5:
            case 6:
              sub_4C77ED(addr, v20);
              break;
          `}`
```

初次运行到这边的时候，这边的值为4，于是进入`sub_4C73B3`。这边首先获取了当前程序的基地址，并且分配了一个大小为`44000`大的RWX空间。然后将一个之前从`.easyre`解密后的一个模块拷贝到了当前空间：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c9e30976c9e94433.png)

之后依然是读取Kernel32.dll，将相关的API填充到对应的位置上，最后跳转到指定的函数地址:

```
if ( *(_DWORD *)(a2 + 4) )
  `{`
    v35 = (*(int (__stdcall **)(_DWORD, _DWORD, void (__stdcall *)(_DWORD), _DWORD, _DWORD, _DWORD))(v2 + 92))(// CreateThread
            0,
            0,
            entry,
            0,
            0,
            0);
    if ( v35 )
      (*(void (__stdcall **)(int, int))(v2 + 88))(v35, -1);
  `}`
  else
  `{`
    entry(NtCurrentTeb()-&gt;ProcessEnvironmentBlock);
  `}`
```

进入这段逻辑之后，会发现这段逻辑非常熟悉，基本类似于**windows的main函数外部，用于准备各类全局变量和环境变量的加载部分**:

[![](https://p4.ssl.qhimg.com/t012e8b8f10c62c7fff.png)](https://p4.ssl.qhimg.com/t012e8b8f10c62c7fff.png)

于是我们将这一段内存进行dump，可以看到主要逻辑:

```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  char *v3; // edi
  struct _PROCESS_INFORMATION ProcessInformation; // [esp+8h] [ebp-324h] BYREF
  CONTEXT Context; // [esp+18h] [ebp-314h] BYREF
  struct _STARTUPINFOA StartupInfo; // [esp+2E4h] [ebp-48h] BYREF

  ((void (__cdecl *)(struct _STARTUPINFOA *, _DWORD, int))(&amp;byte_28F518C + 4117))(&amp;StartupInfo, 0, 68);
  ProcessInformation = 0i64;
  CreateProcessA(0, msiexec, 0, 0, 0, 4u, 0, 0, &amp;StartupInfo, &amp;ProcessInformation);
  Context.ContextFlags = 65537;
  GetThreadContext(ProcessInformation.hThread, &amp;Context);
  v3 = (char *)VirtualAllocEx(ProcessInformation.hProcess, 0, 0x278F0u, 0x1000u, 0x40u);
  WriteProcessMemory(ProcessInformation.hProcess, v3, dword_29061E8, 0xED80u, 0);
  WriteProcessMemory(ProcessInformation.hProcess, v3 + 60800, dword_2914F70, 0xED80u, 0);
  WriteProcessMemory(ProcessInformation.hProcess, v3 + 121600, dword_2923CF8, 0x9DEEu, 0);
  Context.Eip = (DWORD)v3;
  Context.ContextFlags = 65537;
  SetThreadContext(ProcessInformation.hThread, &amp;Context);
  ResumeThread(ProcessInformation.hThread);
  Sleep(0xEA60u);
  VirtualFreeEx(ProcessInformation.hProcess, v3, 0xED81u, 0x4000u);
  return 0;
`}`
```

上述代码做了如下的事情:
- 创建了一个msiexec的进程，并且将其挂起
- 往进程地址空间写入了三段内存空间，经过调试可以知道，其中有两段是加密的数据段，还有一个和之前injected的代码段一致
- 使用ThreadContext修改了主线程的地址，然后重新运行线程，让子进程运行注入的shellcode
### <a class="reference-link" name="%E5%AD%90%E8%BF%9B%E7%A8%8B%E8%B0%83%E8%AF%95%E4%BB%A5%E5%8F%8A%E6%9C%80%E7%BB%88%E8%A7%A3%E5%AF%86"></a>子进程调试以及最终解密

我们使用另一个x32dbg依附到子进程，并且根据我们父进程代码

```
Context.Eip = (DWORD)v3;
```

找到我们需要调试的函数地址:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0119b1a54378b0ef3b.png)

然后让父进程运行到`ResumeThread`之后，子进程这边开始活动。我们直接让其运行到断点处，发现这边的代码大致上和`.easyre`开头的代码一致

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fa721bd83441ae58.png)

之后的逻辑和之前很相似，也是进行了一些安全函数的Patch，然后解密一段逻辑，并且读取Kernel32中指定的API，最终跳转到一个被设置为RWX的内存空间上。最终我们用类似的方法找到对应的main函数地址:

```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  NumberOfBytesRead = 0;
  Buffer[0] = 0;
  sub_2E77100(&amp;Buffer[1], 0, 999);
  *(_DWORD *)v12 = 0x534B675B;
  *(_WORD *)&amp;v12[4] = 0x530F;
  v12[6] = 0x63;
  v3 = CreateFileA(aFlag, 0xC0000000, 0, 0, 3u, 0x80u, 0);
  if ( v3 == (HANDLE)-1 )
  `{`
    GetLastError();
    result = 0;
  `}`
  else
  `{`
    GetFileSizeEx(v3, &amp;FileSize);
    if ( FileSize.QuadPart &gt;= 0xFFFFFFFFFi64
      &amp;&amp; ReadFile(v3, Buffer, 0x19u, &amp;NumberOfBytesRead, 0)
      &amp;&amp; (!self_str_cmp((int)Buffer, aFlag_0, 5u) || Buffer[24] == '`}`') )
    `{`
      v5 = *(_DWORD *)&amp;Buffer[16];
      v6 = *(_DWORD *)&amp;Buffer[20];
      i = 0;
      v13 = *(_DWORD *)&amp;Buffer[12] + 0x6FC4108B;
      while ( 1 )
      `{`
        v8 = Buffer[i + 5];
        if ( v8 &lt;= 97 || v8 &gt;= 122 || sub_2E71CB0(v8, 2) != v12[i] )
          break;
        if ( (unsigned int)++i &gt; 6 )
        `{`
          if ( *(_DWORD *)&amp;Buffer[12] / 0x1DD7u == 0x18E82 )
          `{`
            v9 = 32;
            v10 = 0;
            do
            `{`
              v10 += v13;
              v5 += (v10 + v6) ^ (*(_DWORD *)Buffer + 16 * v6) ^ (*(_DWORD *)&amp;Buffer[4] + (v6 &gt;&gt; 5));
              v6 += (v10 + v5) ^ (*(_DWORD *)&amp;Buffer[12] + (v5 &gt;&gt; 5)) ^ (*(_DWORD *)&amp;Buffer[8] + 16 * v5);
              --v9;
            `}`
            while ( v9 );
            *(_DWORD *)&amp;Buffer[16] = v5;
            *(_DWORD *)&amp;Buffer[20] = v6;
            if ( v5 == 0xC0CEE32 &amp;&amp; v6 == 0xB7F3D728 )
            `{`
              v11 = sub_2E72A60();
              sub_2E72D20(v11);
            `}`
          `}`
          break;
        `}`
      `}`
    `}`
    result = 0;
  `}`
  return result;
`}`
```

于是可以分析出如下的逻辑:
- 代码首先会打开一个叫做flag的文件，并且其长度可以推测要为25
<li>读入的字符串前五个字节为`flag`{``，最后一个字母为``}``
</li>
<li>
`sub_2E71CB0`函数会决定flag中（出去前缀）的前七个字符为多少，这个函数为一个简单的递归函数。</li>
- 接下来的四个字符可通过运算得到
- 以前16个字符为密钥，剩下的内容为密文进行TEA加密
<li>最终检查加密结果是否为`0xC0CEE32`和`0xB7F3D728`
</li>
于是我们可以根据上述逻辑写出最终的解题:

```
#include&lt;iostream&gt;
#include&lt;string&gt;
#include&lt;Windows.h&gt;


unsigned int __fastcall sub_4541CB0(unsigned __int8 chr, int num)
`{`
    char v2; // al
    int v3; // edx
    unsigned int v4; // ebx
    char v6; // [esp+Ch] [ebp-4h]

    v2 = num;
    v3 = num - 1;
    v6 = v2;
    if (v3 &lt; 0)
    `{`
        v4 = chr;
    `}`
    else
    `{`
        v4 = sub_4541CB0(chr, v3);
        v2 = v6;
    `}`
    return ((v4 &amp; (1 &lt;&lt; (6 - v2))) &gt;&gt; (2 * (3 - v2))) | ((v4 &amp; (1 &lt;&lt; v2)) &lt;&lt; (2 * (3 - v2))) | v4 &amp; ~(1 &lt;&lt; v2) &amp; ~(1 &lt;&lt; (6 - v2));
`}`

void decrypt(uint32_t v[2], const uint32_t k[4]) `{`
    unsigned int boundary = 0x18E82* 0x1DD7;
    unsigned int delta = 0x9E3779B9;
    unsigned int sum = 0xC6EF3720;
    uint32_t v0 = v[0], v1 = v[1], i;  /* set up; sum is 32*delta */
    uint32_t k0 = k[0], k1 = k[1], k2 = k[2], k3 = k[3];   /* cache key */
    for (i = 0; i &lt; 32; i++) `{`                         /* basic cycle start */
        v1 -= ((v0 &lt;&lt; 4) + k2) ^ (v0 + sum) ^ ((v0 &gt;&gt; 5) + k3);
        v0 -= ((v1 &lt;&lt; 4) + k0) ^ (v1 + sum) ^ ((v1 &gt;&gt; 5) + k1);
        sum -= delta;
    `}`                                              /* end cycle */
    v[0] = v0; v[1] = v1;
`}`

void encrypt(uint32_t v[2], const uint32_t k[4]) `{`
    uint32_t v0 = v[0], v1 = v[1], sum = 0, i;           /* set up */
    uint32_t delta = 0x9E3779B9;                     /* a key schedule constant */
    uint32_t k0 = k[0], k1 = k[1], k2 = k[2], k3 = k[3];   /* cache key */
    for (i = 0; i &lt; 32; i++) `{`                         /* basic cycle start */
        sum += delta;
        v0 += ((v1 &lt;&lt; 4) + k0) ^ (v1 + sum) ^ ((v1 &gt;&gt; 5) + k1);
        v1 += ((v0 &lt;&lt; 4) + k2) ^ (v0 + sum) ^ ((v0 &gt;&gt; 5) + k3);
    `}`                                              /* end cycle */
    v[0] = v0; v[1] = v1;
`}`

int main()
`{`
    // msiex
    unsigned char table[] = `{` 0x5b,0x67,0x4b,0x53,0x0f,0x53,0x63`}`;
    for (int i = 0; i &lt; 7; i++)
    `{`
        for (unsigned char c = 0x61; c &lt;= 0x7a; c++)
        `{`
            if (sub_4541CB0(c, 2) == table[i])
            `{`
                printf("%c", c);
                break;
            `}`
        `}`
    `}`
    puts("----");
    // .si.
    unsigned int boundary = 0x2e73692e;
    unsigned int num = boundary + 0x6FC4108B;
    char buffer[10] = `{` 0 `}`;
    //unsigned int check[10] = `{` 0xC0CEE32 , 0xB7F3D728 `}`;
    unsigned char check[9] = "\x32\xee\x0c\x0c\x28\xd7\xf3\xb7";
    // unsigned int check[2] = `{`0xB7F3D728,0xC0CEE32 `}`;

    unsigned char input_string[] = "flag`{`msiexec.is.";
    decrypt((uint32_t*)check, (uint32_t*)input_string);
    printf("%s\n", check);
`}`
```

至此，整个解题流程结束



## misc tunnel

本题通过出题的方式介绍了一种基于DNS的攻击手段

### <a class="reference-link" name="%E6%B5%81%E9%87%8F%E6%A3%80%E6%9F%A5"></a>流量检查

从名字上看，本题应该是使用了某种通信的加密技术，打开流量包检查相关信息:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01735d2072f1276aeb.png)

可以看到这边请求的url非常有规律，都是**以evil.im作为后缀，并且前缀有类似base64后的字符串**。根据以前搞事情的了解，这里应该是使用了一种叫做**DNS tunnel**的技巧。

### <a class="reference-link" name="DNS%20tunnel"></a>DNS tunnel

这边简单介绍一下这种技巧。DNS(Domain Name System)，也就是域名解析系统，是一种能够将数字ip与域名形成映射的协议。DNS在解析的过程中，当本地没有缓存的时候，会尝试以 根服务器-&gt;顶级服务器-&gt;二级域名服务器 等递归的方式对url进行解析，最终找到url对应的真实IP

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01223ce6d863bf2af6.png)

如上图。假设`test.com`对应的就是我们的服务器，那么dns请求最终就会得到我们的服务器的ip。那么，如果在这个基础上，我们再增加一个子域名，类似于`c2VjcmV0.test.com`，那么根据dns递归查找的原理，此时dns会**尝试在我们的服务器上进行123的解析**，最终会变成如下的形式:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015b886a1afb18fb52.png)

于是，我们就通过dns请求，将我们想要传递的信息发送给了我们自己的服务器。<br>
这种多此一举的操作是为啥呢？其实就是为了隐蔽传输的信息，将某些特殊的信息藏在dns流量中，甚至绕过某些认证，进行网络通信，这边就不仔细展开

### <a class="reference-link" name="%E8%A7%A3%E6%9E%90dns"></a>解析dns

那么既然知道url中藏有重要的通信内容，这边就需要尝试分析流量。从图1可以知道，整个通信过程中似乎进行了A类和AAAA类两种请求方式，不过乍一看传输数据都是类似的，于是这边我们首先使用tshark将所有需要分析的dns解析的域名导出

```
tshark -r tunnel.pcap -T fields -e dns.qry.name -Y 'ip.src == 192.168.1.103 &amp;&amp; ip.dst == 8.8.8.8 &amp;&amp; dns.qry.type eq 1'
tshark -r tunnel.pcap -T fields -e dns.qry.name -Y 'ip.src == 192.168.1.103 &amp;&amp; ip.dst == 8.8.8.8 &amp;&amp; dns.qry.type eq 28'
```

这边1是A记录，28是AAAA记录。导出之后，我们比对一下两个导出结果的差异，会发现A记录比AAAA记录多了好几条，说明可能A才是我们要找的记录。然后我们将导出的dns tunnel的数据进行解密:

```
import base64
fd = open("dns2.txt",'r')
content = []
for eachline in fd:
    content.append(eachline)

fd.close()
print(content)
contents = b""
index = 0
passwd = []
for index in range(len(content)):
    if "evil.im" in content[index]:
    # if ("evil.im" in content[index] and 
    # (index ==0 or content[index-1] != content[index])):
        eachline = content[index].strip()
        print(eachline)
        cont = eachline.split(".")[0]
        if len(cont) % 4 != 0:
            cont += '='*(4-(len(cont) % 4))
        # contents += cont.encode("utf-8")
        cont_out = base64.standard_b64decode(cont)
        contents += cont_out

# out = base64.standard_b64decode(contents)
fd = open("out2",'wb')
fd.write(contents)
# fd.write(out)
fd.close()
```

解密完，会发现二进制文件经典PK头，所以又是一个zip包，打开后发现是一个加了密的图片。

### <a class="reference-link" name="%E5%AF%86%E9%92%A5%E4%B8%8Ebase64"></a>密钥与base64

最初我以为密钥藏在了流量中，不过剩余流量并没有分析的价值，直到队友提醒可能和base64隐写有关。关于base64隐写，其实最关键的点就在于，base64在加密过程中，发生了信息膨胀，这就意味着**这里进行了base64隐写**。详情可以参考[这边博客](https://www.tr0y.wang/2017/06/14/Base64steg/)<br>
这边尝试对第一条导出的base64进行了解码再编码，发现果然不相等，说明确实存在base64隐写的问题:

```
In [10]: test = b"UEsDBDMAAwBjAJ12k1KDFWibyjR="
In [11]: base64.standard_b64encode(base64.standard_b64decode(test))
Out[11]: b'UEsDBDMAAwBjAJ12k1KDFWibyjQ='
```

于是修改了一下导出脚本，将密钥导出也放在其中:

```
import base64
fd = open("dns2.txt",'r')
content = []
for eachline in fd:
    content.append(eachline)

fd.close()
print(content)
contents = b""
index = 0
passwd = []
for index in range(len(content)):
    if "evil.im" in content[index]:
    # if ("evil.im" in content[index] and 
    # (index ==0 or content[index-1] != content[index])):
        eachline = content[index].strip()
        print(eachline)
        cont = eachline.split(".")[0]
        if len(cont) % 4 != 0:
            cont += '='*(4-(len(cont) % 4))
        # contents += cont.encode("utf-8")
        passwd.append(cont)
        cont_out = base64.standard_b64decode(cont)
        contents += cont_out


# print(contents)
print(passwd)

# out = base64.standard_b64decode(contents)
fd = open("out2.zip",'wb')
fd.write(contents)
# fd.write(out)
fd.close()

# try to find password
b64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
bin_str = ''
result_offset = []
# fd = open("diff.txt",'r')
for eachline in passwd:
    # eachline = eachline.strip()

    # if len(eachline) % 4 != 0:
    #     eachline += '='*(4-(len(eachline) % 4))
    # print(eachline)
    out = base64.standard_b64encode(base64.standard_b64decode(eachline.encode('utf-8')))
    print("test:"+eachline)
    out = out.decode('utf-8')
    if out != eachline:
        print("encrypted!")
        print(out,eachline)
        offset = abs(b64chars.index(eachline.replace('=','')[-1])-b64chars.index(out.replace('=','')[-1]))
        equalnum = eachline.count('=') 
        print(offset)
        result_offset.append(offset)
        if offset != 0:
            # bin_str += bin(offset)[2:].zfill(equalnum * 2)
            bin_str += bin(offset)[2:].zfill(equalnum * 2)
            # bin_str += (4-equalnum*2)*'0'
        # else:
        #     bin_str += '0' * equalnum * 2
        print(bin_str)
    else:
        print("not encrypted!")
        equalnum = eachline.count('=') 
        bin_str += '0' * equalnum * 2
    print(''.join([chr(int(bin_str[i:i + 8], 2)) for i in range(0, len(bin_str), 8)]))

print(result_offset)
# for i in range(0, len(bin_str),8):
#     print(chr(int(bin_str[i:i+8],2)))
```

可以隐藏的内容为:

```
password: B@%MG"6FjbS8^c#r
```

于是最终能够解开压缩包，得到答案。



## 一点思考

这次津门杯虽然有一些题目也是原题修改，不过我觉得Injected和tunnel两个题目还是非常有趣的。Injected中感觉使用了一种真实攻击样例中使用的工具进行题目的封装，里面甚至还有一些关于WLDQ的一些非常新的防御绕过的机制。而tunnel则是以出题的方式介绍了DNS tunnel，这两个题目能作为引子，让人尝试了解DynamicCodePolicy以及DNS tunnel，个人感觉还是不错的。



## 参考链接

[https://www.tr0y.wang/2017/06/14/Base64steg/](https://www.tr0y.wang/2017/06/14/Base64steg/)
