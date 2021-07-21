> 原文链接: https://www.anquanke.com//post/id/169872 


# 对某HWP漏洞样本的shellcode分析


                                阅读量   
                                **210449**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01e2d9d00ef4b19de2.png)](https://p5.ssl.qhimg.com/t01e2d9d00ef4b19de2.png)



## 前言

最近拿到一个新的HWP样本，样本本身利用的是一个老漏洞，这个样本吸引我们的是shellcode部分。相关漏洞的细节我们在[之前的文章](https://www.anquanke.com/post/id/163085)中已有描述。需要注意的是，这次的样本和上次的样本在最终的执行流切换方面有一些差异。前一段时间我们曾审计过一些HWP样本，发现不同HWP样本在触发该漏洞后具体的执行流切换上存在4种不同的情况。上次的漏洞分析文章是第1种情况，本次的样本是第2种情况，此外还有2种其他情况，相关的MD5示例如下：

```
第1种情况：
33874577bf54d3c209925c9def880eb9

第2种情况：
660b607e74c41b032a63e3af8f32e9f5
e488c2d80d8c33208e2957d884d1e918 (本次调试样本)

第3种情况：
f58e86638a26eb1f11dd1d18c47fa592

第4种情况：
14b985d7ae9b3024da487f851439dc04
```

```
本次调试环境为 windows7_sp1_x86 + HWP2010英文版 (hwpapp.dll 8.0.0.466) + windbg x86
```

这个样本在漏洞触发成功后执行的shellcode让我们眼前一亮，样本在漏洞触发后先执行第1阶段shellcode去解密第2阶段的shellcode。在第2阶段的shellcode中，通过hash比对的方式从kernel32.dll中获取功能函数，然后创建 `C:Windowssystem32userinit.exe` 进程并且在创建时挂起，接着从文档内容中查找标志头，定位到被加密的PE文件数据，随后通过两轮解密解出PE文件，将其写入userinit.exe进程的`0x400000`处，随后修改userinit.exe进程的`Peb.ImageBaseAddress`为新写入的PE文件，并且修改userinit.exe的主线程的线程上下背景文的`Context.eax`为新写入PE文件的`AddressOfEntryPoint`，然后恢复userinit.exe的主线程，从而将执行流切换到注入的PE文件的入口地址，这是一种`Process Hollowing`技术，相关原理在[这个网页](https://cysinfo.com/detecting-deceptive-hollowing-techniques/)中有描述。这种方法让分析人员较难提取到注入的PE文件，在沙箱中跑时也不会显式drop出PE文件，可以说有效躲避了检测。注入的PE文件启动后，会收集系统信息保存到`%appdata%MicrosoftNetworkxyz`,随后发给远程C2(`online[-]business.atwebpages[.]com`)，然后在一个while循环中进行等待，如果收集的信息显示当前目标存在价值，远程C2会下发一个动态库保存到`%appdata%MicrosoftNetworkzyx.dll`并使之加载。比较遗憾的是，我们在调试时并没有得到`zyx.dll`。



## 文档信息

用`HwpScan2`工具打开该文档，先看一下基本属性部分。可以看到原始文档在2016年就已经生成。

[![](https://p2.ssl.qhimg.com/t01399901a63b19f5ba.png)](https://p2.ssl.qhimg.com/t01399901a63b19f5ba.png)

原文档是限制编辑的，打开后文档内容无法复制，实际的段落内容被存储在”ViewText”流下，而不是常规的”BodyText”流下：

[![](https://p3.ssl.qhimg.com/t016fbfab3575462cec.png)](https://p3.ssl.qhimg.com/t016fbfab3575462cec.png)

关于这一点，VB2018的一个[PPT](https://www.virusbulletin.com/uploads/pdf/conference_slides/2018/KimKwakJang-VB2018-Dokkaebi.pdf)上有详细的介绍：

[![](https://p2.ssl.qhimg.com/t01906588b4c2ec565e.png)](https://p2.ssl.qhimg.com/t01906588b4c2ec565e.png)

Section1和Section2这两个Section里面含有被压缩后的堆喷射数据，在文档打开期间解压后的数据会被喷射到指定的内存。



## 内存布局

这个样本用到了堆喷射来布局内存，我们在调试器里面看一下堆喷射的具体细节：

```
sxe ld:hwpapp.dll
...
ModLoad: 046f0000 04ad1000   C:Program FilesHncHwp80HwpApp.dll
eax=0012ee68 ebx=00000000 ecx=00000006 edx=00000000 esi=7ffdf000 edi=0012eff4
eip=772270b4 esp=0012ef0c ebp=0012ef60 iopl=0         nv up ei pl zr na pe nc
cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
ntdll!KiFastSystemCallRet:
772270b4 c3              ret

0:000&gt; bp hwpapp+1122f3 ".if(edx == hwpapp+bded0)`{`g;`}`.else`{``}`"

0:000&gt; g
DllMain() : DLL_PROCESS_ATTACH -  ABase Start!
(d8c.468): C++ EH exception - code e06d7363 (first chance)
eax=20142014 ebx=0012f6bc ecx=20142014 edx=20142014 esi=02c86d18 edi=00000098
eip=048022f3 esp=0012ed90 ebp=02d881a8 iopl=0         nv up ei pl nz na pe nc
cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
HwpApp!HwpCreateParameterArray+0x8c433:
048022f3 ffd2            call    edx `{`20142014`}`

0:000&gt; !heap
NtGlobalFlag enables following debugging aids for new heaps:    stack back traces
Index   Address  Name      Debugging options enabled
  1:   00230000                
  2:   00010000                
  3:   01980000                
  4:   02650000                
  5:   02770000                
  6:   02950000                
  7:   025d0000                
  8:   028f0000                
  9:   03250000                
 10:   028d0000                
 11:   04e20000                
 12:   06720000                
 13:   07440000                
 14:   07590000                

// 可以看到5号堆块几乎被完全用完
0:000&gt; !heap -stat -h 02770000
 heap @ 02770000
group-by: TOTSIZE max-display: 20
    size     #blocks     total     ( %) (percent of total busy bytes)
    42003b0 2 - 8400760  (49.47)
    420035c 2 - 84006b8  (49.47)
    e4 926 - 825d8  (0.19)
    f0 38a - 35160  (0.08)
    194 1cf - 2daac  (0.07)
    24000 1 - 24000  (0.05)
    18 15d9 - 20c58  (0.05)
    20000 1 - 20000  (0.05)
    100 190 - 19000  (0.04)
    aa00 2 - 15400  (0.03)
    28 6e1 - 11328  (0.03)
    10bc0 1 - 10bc0  (0.02)
    10000 1 - 10000  (0.02)
    fda0 1 - fda0  (0.02)
    fb50 1 - fb50  (0.02)
    a8 158 - e1c0  (0.02)
    4400 3 - cc00  (0.02)
    2200 6 - cc00  (0.02)
    800 17 - b800  (0.02)
    82 13b - 9ff6  (0.01)

0:000&gt; !heap -flt s 420035c 
    _HEAP @ 230000
    _HEAP @ 10000
    _HEAP @ 1980000
    _HEAP @ 2650000
    _HEAP @ 2770000
      HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
invalid allocation size, possible heap corruption
        121b0018 84006d 0000  [00]   121b0030    420035c - (busy VirtualAlloc)
invalid allocation size, possible heap corruption
        242d0018 84006d 006d  [00]   242d0030    420035c - (busy VirtualAlloc)
    _HEAP @ 2950000
    _HEAP @ 25d0000
    _HEAP @ 28f0000
    _HEAP @ 3250000
    _HEAP @ 28d0000
    _HEAP @ 4e20000
    _HEAP @ 6720000
    _HEAP @ 7440000
    _HEAP @ 7590000

0:000&gt; !heap -flt s 42003b0 
    _HEAP @ 230000
    _HEAP @ 10000
    _HEAP @ 1980000
    _HEAP @ 2650000
    _HEAP @ 2770000
      HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
        0a6d0018 840078 0000  [00]   0a6d0030    42003b0 - (busy VirtualAlloc)
        200c0018 840078 0078  [00]   200c0030    42003b0 - (busy VirtualAlloc)
    _HEAP @ 2950000
    _HEAP @ 25d0000
    _HEAP @ 28f0000
    _HEAP @ 3250000
    _HEAP @ 28d0000
    _HEAP @ 4e20000
    _HEAP @ 6720000
    _HEAP @ 7440000
    _HEAP @ 7590000

// 推测Section1和Section2分别被映射了两次，我们来看一下堆喷射的总大小
0:000&gt; ? 42003b0 / 400 / 400
Evaluate expression: 66 = 00000042

// 可以看到堆喷射的大小总大小为264MB，单个堆块大小为66MB，0x20142014地址稳定位于0x200c0030左右开始的喷射区域，所以可以很方便地劫持控制流。
0:000&gt; ? 42 * 4
Evaluate expression: 264 = 00000108
```



## 第1阶段shellcode

漏洞触发成功之后，首先跳转到`0x20142014`这个地址，由于前面已经通过堆喷射布局内存，所以执行流可以一路滑行到`0x242bf714`(这里再强调一下，HWP2010并未开启DEP，所以可以直接在堆上执行shellcode)以执行第1阶段的shellcode。下面来看一下shellcode部分。

```
0:000&gt; u 242bf714
242bf714 52              push    edx
242bf715 53              push    ebx
242bf716 56              push    esi
242bf717 50              push    eax
242bf718 57              push    edi
242bf719 ba14201420      mov     edx,20142014h
...
```

第1阶段的shellcode的主要目的是定位并解密第2阶段的shellcode。从下图可以看到，第1阶段shellcode通过第1轮循环(loc_A)定位到第2阶段shellcode地址，然后通过第2轮循环(loc_22)去解密第2阶段的shellcode。

[![](https://p3.ssl.qhimg.com/t01bdec160042581721.png)](https://p3.ssl.qhimg.com/t01bdec160042581721.png)

我们用python模拟了一下上述shellcode的解密过程：

```
# -*- coding: utf-8 -*-
import os
import binascii

cur_dir = os.path.dirname(__file__)

path_encode = os.path.join(cur_dir, "sc_encode.bin")
with open(path_encode, "rb") as f:
    bin_data = f.read()
    bin_data = binascii.b2a_hex(bin_data)

i = 0
j = 0
k = 0
while k &lt; 0x60D:
    a = ((int(bin_data[i:i+2], 16) &amp; 0x0F) &lt;&lt; 4) &amp; 0xF0
    b = int(bin_data[i+2:i+4], 16) &amp; 0x0F
    c = '`{`:02x`}`'.format(a + b)
    bin_data = bin_data[:j] + c[0] + c[1] + bin_data[j+2:]
    i += 2 * 2
    j += 2 * 1
    k += 1

path_decode = os.path.join(cur_dir, "sc_decode.bin")
with open(path_decode, "wb") as f:
    f.write(binascii.a2b_hex(bin_data))
```

实际解密时从下述数据开始：

[![](https://p2.ssl.qhimg.com/t01c1d3f4cc6d0d9d52.png)](https://p2.ssl.qhimg.com/t01c1d3f4cc6d0d9d52.png)

解密完成后，我们可以得到如下数据：

[![](https://p1.ssl.qhimg.com/t01546e2d4b07083606.png)](https://p1.ssl.qhimg.com/t01546e2d4b07083606.png)



## 第2阶段shellcode

### <a class="reference-link" name="%E8%8E%B7%E5%8F%96%E5%8A%9F%E8%83%BD%E5%87%BD%E6%95%B0"></a>获取功能函数

得到解密后的第2阶段shellcode后，就可以愉快地在IDA里进行后续分析了。

第2阶段shellcode上来就是一系列hash，看起来貌似是要通过hash比对搜索功能函数。

[![](https://p1.ssl.qhimg.com/t01d0bb515df8dcb466.png)](https://p1.ssl.qhimg.com/t01d0bb515df8dcb466.png)

一番调试和逆向后，我们明白shellcode封装了一个辅助函数用来查找所需的功能函数：

[![](https://p1.ssl.qhimg.com/t01b1dac54a0605473e.png)](https://p1.ssl.qhimg.com/t01b1dac54a0605473e.png)

在`GetFuncAddrFromEATByHash`函数内部，作者用循环右移13位的方式计算hash，并查找满足指定hash的动态库(kernel32.dll)内的满足指定hash的函数，然后将它们的地址保存到栈的指定位置，如上图所示。我们这里用C语言还原一下dll的hash的计算过程和api的hash的计算过程：

```
// 部分代码借鉴自网络，此处表示致谢
#include &lt;stdio.h&gt;
#include &lt;windows.h&gt;

#define ROTATE_RIGHT(x, s, n) ((x) &gt;&gt; (n)) | ((x) &lt;&lt; ((s) - (n)))

DWORD GetHashHWPUnicode(WCHAR *wszName)
`{`
    printf("%S", wszName);
    DWORD dwRet = 0;
    WCHAR* wszCur = 0;
    do 
    `{`
        dwRet = ROTATE_RIGHT(dwRet, 32, 0x0D);
        dwRet += *wszName;
        wszCur = wszName;
        wszName++;
    `}` while (*wszCur);
    printf(" function's hash is 0x%.8xn", dwRet);
    return dwRet;
`}`

DWORD GetHashHWPAscii(CHAR *szName)
`{`
    printf("%s", szName);
    DWORD dwRet = 0;
    CHAR* szCur = 0;
    do 
    `{`
        dwRet = ROTATE_RIGHT(dwRet, 32, 0x0D);
        dwRet += *szName;
        szCur = szName;
        szName++;
    `}` while (*szCur);
    printf(" function's hash is 0x%.8xn", dwRet);
    return dwRet;
`}`

int main(int argc, char* argv[])
`{`
    GetHashHWPUnicode(L"KERNEL32.dll");
    GetHashHWPUnicode(L"KERNEL32.DLL");
    GetHashHWPUnicode(L"kernel32.DLL");
    GetHashHWPUnicode(L"kernel32.dll");

    GetHashHWPAscii("ResumeThread");
    GetHashHWPAscii("SetThreadContext");
    GetHashHWPAscii("VirtualProtectEx");
    GetHashHWPAscii("WriteProcessMemory");
    GetHashHWPAscii("GetVersionExA");
    GetHashHWPAscii("ReadProcessMemory");
    GetHashHWPAscii("TerminateProcess");
    GetHashHWPAscii("GetThreadContext");
    GetHashHWPAscii("GetLastError");
    GetHashHWPAscii("GetProcAddress");
    GetHashHWPAscii("GetSystemDirectoryA");
    GetHashHWPAscii("GetModuleHandleA");
    GetHashHWPAscii("CreateProcessA");
    GetHashHWPAscii("GlobalAlloc");
    GetHashHWPAscii("GetFileSize");
    GetHashHWPAscii("SetFilePointer");
    GetHashHWPAscii("CloseHandle");
    GetHashHWPAscii("VirtualAllocEx");
    GetHashHWPAscii("ReadFile");
    return 0;
`}`
```

### <a class="reference-link" name="%E5%AE%9A%E4%BD%8DPE%E6%96%87%E4%BB%B6%E5%B9%B6%E8%A7%A3%E5%AF%86"></a>定位PE文件并解密

获得需要的功能函数后，shellcode首先通过`GlobalAlloc`函数申请一段内存，用来存储后面将要读入的PE数据。随后，从4开始，遍历句柄，暴力搜索文件大小等于当前hwp文件大小的文件句柄并保存，然后将文件指针移动到`0x9DE1`偏移处，并将大小为`3E40A Bytes`的内容读入之前申请的内存处。

[![](https://p2.ssl.qhimg.com/t01ed4cfceeb899b48c.png)](https://p2.ssl.qhimg.com/t01ed4cfceeb899b48c.png)

然后，shellcode从读入的文档内容开始搜索两个连续的标志`0x42594F4A`，`0x4D545245`，并将第2个标志结束`+2`的地址处作为PE数据的首地址保存到[ebp-18]处。

[![](https://p4.ssl.qhimg.com/t013adb11284881d1ad.png)](https://p4.ssl.qhimg.com/t013adb11284881d1ad.png)

可以在HWP文档中定位到相应数据区域：

[![](https://p3.ssl.qhimg.com/t0117fbfbf88654805b.png)](https://p3.ssl.qhimg.com/t0117fbfbf88654805b.png)

不过此时的PE文件数据仍为被加密的状态，shellcode随后用两轮解密将解密的PE文件进行解密，相关汇编代码如下：

[![](https://p4.ssl.qhimg.com/t013e59aa07bf066378.png)](https://p4.ssl.qhimg.com/t013e59aa07bf066378.png)

在理解上述代码的基础上一样可以用python写出解密程序，如下：

```
# -*- coding: utf-8 -*-
import os
import binascii

cur_dir = os.path.dirname(__file__)

path_encode = os.path.join(cur_dir, "pe_encode.bin")
with open(path_encode, "rb") as f:
    bin_data = f.read()
    bin_data = binascii.b2a_hex(bin_data)

i = 2 * 2
while (i / 2) &lt; 0x18400:
    a = int(bin_data[i-4:i-4+2], 16)
    b = int(bin_data[i-2:i], 16)
    c = int(bin_data[i:i+2], 16)
    c = '`{`:02x`}`'.format((a ^ b ^ c) &amp; 0xFF)
    bin_data = bin_data[:i] + c[0] + c[1] + bin_data[i+2:]
    i += 2 * 1

i = 2 * 2
while (i / 2) &lt; 0x18400:
    c = int(bin_data[i:i+2], 16)
    c = ((c &lt;&lt; ((i / 2) &amp; 7)) &amp; 0xFF) + ((c &gt;&gt; (8 - ((i / 2) &amp; 7))) &amp; 0xFF) ^ (i / 2)
    c = '`{`:02x`}`'.format(c &amp; 0xFF)
    bin_data = bin_data[:i] + c[0] + c[1] + bin_data[i+2:]
    i += 2 * 1

path_decode = os.path.join(cur_dir, "pe_decode.bin")
with open(path_decode, "wb") as f:
    f.write(binascii.a2b_hex(bin_data[4:]))

```

解密前的PE数据如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0150347967b84c4920.png)

解密后的PE数据如下：

[![](https://p1.ssl.qhimg.com/t01fa6ae898754f4768.png)](https://p1.ssl.qhimg.com/t01fa6ae898754f4768.png)

### <a class="reference-link" name="%E5%88%9B%E5%BB%BAuserinit.exe%E8%BF%9B%E7%A8%8B%E5%B9%B6%E6%8C%82%E8%B5%B7"></a>创建userinit.exe进程并挂起

得到解密的PE文件后，shellcode做了一系列准备并最终去启动userinit.exe进程，启动时传入`CREATE_SUSPENDED`标志，指明将userinit.exe启动后挂起：

[![](https://p5.ssl.qhimg.com/t0130fe66bd8e214039.png)](https://p5.ssl.qhimg.com/t0130fe66bd8e214039.png)

[![](https://p5.ssl.qhimg.com/t0109bdef22e9ce7f71.png)](https://p5.ssl.qhimg.com/t0109bdef22e9ce7f71.png)

### <a class="reference-link" name="%E6%9B%BF%E6%8D%A2userinit.exe%E4%B8%BB%E6%A8%A1%E5%9D%97"></a>替换userinit.exe主模块

随后shellcode调用`GetThreadContext`获取userinit.exe主线程的线程上下文并保存到栈的指定位置：

[![](https://p5.ssl.qhimg.com/t0195c04c7a3fba63cf.png)](https://p5.ssl.qhimg.com/t0195c04c7a3fba63cf.png)

接着读取userinit.exe的`Peb.ImageBaseAddress`：

[![](https://p0.ssl.qhimg.com/t01709fa867e0865373.png)](https://p0.ssl.qhimg.com/t01709fa867e0865373.png)

然后动态获取`ntdll!ZwUnmapViewOfSection`，并判断操作系统版本，如果操作系统主版本小于6(相关原理可以参考[这篇文章](https://cysinfo.com/detecting-deceptive-hollowing-techniques/))，则调用该API对主模块基地址的内存进行解映射，否则直接跳到后续步骤：

[![](https://p5.ssl.qhimg.com/t019f2a981120defb99.png)](https://p5.ssl.qhimg.com/t019f2a981120defb99.png)

接着shellcode在userinit.exe进程内`0x400000`地址处(即PE文件中写入的进程默认加载基址)申请一片内存，内存大小等于解密出来的PE文件，并先将PE文件的头部写入所申请的内存(`0x400000`)：

[![](https://p0.ssl.qhimg.com/t01a6a74b33a5690348.png)](https://p0.ssl.qhimg.com/t01a6a74b33a5690348.png)

随后往上述内存区域循环写入PE文件的各个节区：

[![](https://p0.ssl.qhimg.com/t01283f8c4dd08fbe82.png)](https://p0.ssl.qhimg.com/t01283f8c4dd08fbe82.png)

每写完一个节区后，shellcode获取PE文件中该节区的原始读写属性(通过`Characteristics`字段)，并在内存中相应更新这些节区对应的内存属性：

[![](https://p4.ssl.qhimg.com/t011f66972d47da6293.png)](https://p4.ssl.qhimg.com/t011f66972d47da6293.png)

完成上述步骤后，shellcode将userinit.exe进程的`Peb.ImageBaseAddress`域改写为`0x400000`(即注入后的PE基地址)，并将线程上下文中`Context.eax`更新为所注入PE的`AddressOfEntryPoint`，这部分的原理可以参考[这篇文章](https://blog.csdn.net/lixiangminghate/article/details/42121929)。

[![](https://p3.ssl.qhimg.com/t015998d8eef3a3f059.png)](https://p3.ssl.qhimg.com/t015998d8eef3a3f059.png)

最后恢复userinit.exe的主线程，并关闭刚才打开的userinit.exe进程句柄，从而使主线程去执行`Process Hollowing`后的PE文件，达到偷天换日的目的。相关代码可以参考[这里](https://github.com/m0n0ph1/Process-Hollowing)。

[![](https://p2.ssl.qhimg.com/t016492a41dbc0aa7cf.png)](https://p2.ssl.qhimg.com/t016492a41dbc0aa7cf.png)



## 注入的PE文件

前面我们已经静态解密出了PE文件，我们现在来看一下解密出的PE文件的基本信息，用`pestudio`打开该PE文件，看一下这个PE文件的基本信息：

可以看到该PE文件的编译时间是`2017.12.26 10:13:17`，此外还可以知道该PE文件的链接器版本是9.0。

[![](https://p0.ssl.qhimg.com/t01c2907d32aeab32ad.png)](https://p0.ssl.qhimg.com/t01c2907d32aeab32ad.png)

### <a class="reference-link" name="%E9%80%86%E5%90%91PE%E6%96%87%E4%BB%B6"></a>逆向PE文件

整个PE文件既没有加壳，也没有加花指令，整体逻辑非常清晰明了，拖进IDA基本上就原形毕露了。

PE文件主入口函数如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0182f91c5cb0d6f958.png)

正如函数名所示，它首先调用`AdjustTokenPrivileges`提升自己的权限，然后分别从`Kernel32.dll/Wininet.dll/Advapi32.dll`获取所需的功能函数并保存到全局变量，最后启动一个新的线程，并在10秒后退出当前函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0122fd3cba0c19442b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e93499b7880fccea.png)

(以下几个函数貌似并没有被用到)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014b9ff1337b2b3958.png)

来看一下启动的线程干了哪些事情，如下图所示，这个线程的主要目的就是先收集系统信息，并保存到`%appdata%MicrosoftNetworkxyz`，随后将这些信息发送给远程C2，传完之后删除xyz文件。随后进入一个循环，每隔30分钟从远程服务器尝试下载一个`zyx.dll`并保存到`%appdata%MicrosoftNetworkzyx.dll`并尝试加载之。这里推测是C2端需要先判断目标用户是否有价值，然后才决定是否将下一阶段的载荷发送给目标用户。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011e077293d9a0f5d6.png)

收集信息部分的代码也很直接，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011e0f12153224eda3.png)

随后将收集的信息发送给远程C2：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017c6f819596cc07bb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0127f204cf68703499.png)

[![](https://p0.ssl.qhimg.com/t0155a08f6edcf97bcd.png)](https://p0.ssl.qhimg.com/t0155a08f6edcf97bcd.png)

最后，一旦远程dll被下发到目标机器，PE文件会立即加载之，并在3分钟后卸载对应的dll并删除文件。由于我们调试期间并没有获得下发的dll，所以dll里面具体执行了什么逻辑不得而知。

[![](https://p2.ssl.qhimg.com/t01261f1f33cbbb48a1.png)](https://p2.ssl.qhimg.com/t01261f1f33cbbb48a1.png)



## IOC

```
HWP: e488c2d80d8c33208e2957d884d1e918
PE: 72d44546ca6526cdc0f6e21ba8a0f25d
Domain: online[-]business.atwebpages[.]com
IP: 185[.]176.43.82
```



## 参考链接

[https://github.com/m0n0ph1/Process-Hollowing](https://github.com/m0n0ph1/Process-Hollowing)

[https://cysinfo.com/detecting-deceptive-hollowing-techniques/](https://cysinfo.com/detecting-deceptive-hollowing-techniques/)

[https://blog.csdn.net/lixiangminghate/article/details/42121929](https://blog.csdn.net/lixiangminghate/article/details/42121929)

[https://www.virusbulletin.com/uploads/pdf/conference_slides/2018/KimKwakJang-VB2018-Dokkaebi.pdf](https://www.virusbulletin.com/uploads/pdf/conference_slides/2018/KimKwakJang-VB2018-Dokkaebi.pdf)
