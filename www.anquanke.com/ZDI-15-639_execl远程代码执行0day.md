> 原文链接: https://www.anquanke.com//post/id/83139 


# ZDI-15-639：execl远程代码执行0day


                                阅读量   
                                **77177**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://sourceincite.com/2015/12/15/microsoft-office-excel-users-vulnerable-to-zdi-15-639-a-remote-code-execution-zeroday/](http://sourceincite.com/2015/12/15/microsoft-office-excel-users-vulnerable-to-zdi-15-639-a-remote-code-execution-zeroday/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01b74f6b059c441a86.jpg)](https://p3.ssl.qhimg.com/t01b74f6b059c441a86.jpg)

最近我发现了一个Use-After-Free漏洞,它影响所有版本的Microsoft’s Excel应用程序,只需要构造一个恶意的Excel二进制文件就可以利用该漏洞。这个漏洞可以导致远程代码执行,而微软拒绝对它提供补丁,只是弹出一个警告框作为提醒。让我们看一下弹出的框是什么样子。<br>

[![](https://p5.ssl.qhimg.com/t0138f873bb5491ca71.png)](https://p5.ssl.qhimg.com/t0138f873bb5491ca71.png)

试问,如果这份文件是你从电子邮件中收到的“可信”文件,你当然会点YES吧?毕竟它是一份来自于你认为的“可信”来源发来的“可信”文件。一旦你点击了YES,让我们来看一下会发生什么。

一旦我们点击了YES,我们就在Excel的二进制exe程序中启用了页面堆和用户模式栈追踪,你可能会看到这个:



```
(868.15c4): Access violation - code c0000005 (first chance)
First chance exceptions are reported before any exception handling.
This exception may be expected and handled.
eax=221beff0 ebx=001c2602 ecx=08a1dff0 edx=00000001 esi=00000000 edi=00000001
eip=2fed37f1 esp=001c2264 ebp=001c2294 iopl=0         nv up ei pl zr na pe nc
cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00210246
EXCEL!Ordinal40+0x7737f1:
2fed37f1 663b5004        cmp     dx,word ptr [eax+4]      ds:0023:221beff4=????
0:000&gt; !heap -p -a @eax
    address 221beff0 found in
    _DPH_HEAP_ROOT @ 11d1000
    in free-ed allocation (  DPH_HEAP_BLOCK:         VirtAddr         VirtSize)
                                   22d31a5c:         221be000             2000
    716690b2 verifier!AVrfDebugPageHeapFree+0x000000c2
    773a6dbc ntdll!RtlDebugFreeHeap+0x0000002f
    7736a4c7 ntdll!RtlpFreeHeap+0x0000005d
    77336896 ntdll!RtlFreeHeap+0x00000142
    75b6c4d4 kernel32!HeapFree+0x00000014
    62296f1b mso!Ordinal9770+0x00007bef
    2f98cde3 EXCEL!Ordinal40+0x0022cde3
    2f9e2e82 EXCEL!Ordinal40+0x00282e82
    2f9e2b35 EXCEL!Ordinal40+0x00282b35
    2fa26427 EXCEL!Ordinal40+0x002c6427
    2fa260b6 EXCEL!Ordinal40+0x002c60b6
    2fa24e39 EXCEL!Ordinal40+0x002c4e39
    2fa21994 EXCEL!Ordinal40+0x002c1994
    2fa24a26 EXCEL!Ordinal40+0x002c4a26
    2fa1f82c EXCEL!Ordinal40+0x002bf82c
    2fa1e336 EXCEL!Ordinal40+0x002be336
    2fa1d992 EXCEL!Ordinal40+0x002bd992
    2fa1ced6 EXCEL!Ordinal40+0x002bced6
    2fff23cd EXCEL!Ordinal40+0x008923cd
    3002c86e EXCEL!Ordinal40+0x008cc86e
    300316f1 EXCEL!Ordinal40+0x008d16f1
    30032050 EXCEL!Ordinal40+0x008d2050
    30042046 EXCEL!Ordinal40+0x008e2046
    62076292 mso!Ordinal9994+0x000024c7
    620766cb mso!Ordinal4158+0x000001d8
    6205992d mso!Ordinal9839+0x00000ff0
    6205a0df mso!Ordinal143+0x00000415
    61b50593 mso!Ordinal6326+0x00003b30
    6207621f mso!Ordinal9994+0x00002454
    6175882e mso!Ordinal53+0x0000083b
    617585bc mso!Ordinal53+0x000005c9
    6175744a mso!Ordinal7509+0x00000060
```

很明显,这是一个Use-After-Free漏洞,你可能会认为这个问题并没有那么严重,下面是一份录径示例代码,它并没有启用页面堆和用户模式栈追踪。如果攻击者能够迫使内存分配在某一块特定位置(是的,他们有能力做到),那么攻击者就可以控制代码代码执行。



```
(1614.1a24): Access violation - code c0000005 (first chance)
First chance exceptions are reported before any exception handling.
This exception may be expected and handled.
eax=5ca5f546 ebx=00000000 ecx=5c991ed8 edx=00266794 esi=5c991ed8 edi=00000000
eip=8bec8b55 esp=002667a8 ebp=002667e0 iopl=0         nv up ei pl nz na pe nc
cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00210206
8bec8b55 ??              ???
0:000&gt; k
*** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:Program FilesCommon FilesMicrosoft Sharedoffice14mso.dll - 
ChildEBP RetAddr  
WARNING: Frame IP not in any known module. Following frames may be wrong.
002667a4 5cdec71b 0x8bec8b55
002667e0 5ca40b78 mso!Ordinal8883+0xa15
00266810 5ca40b20 mso!Ordinal9662+0xdb2
00266838 5ca40a84 mso!Ordinal9662+0xd5a
00266844 5ca5f015 mso!Ordinal9662+0xcbe
00266858 5d67e54f mso!Ordinal10511+0x3de
002668cc 5d67e614 mso!Ordinal2804+0x45a
002668f0 5d3a5c3c mso!Ordinal2804+0x51f
*** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:Program FilesMicrosoft OfficeOffice14EXCEL.EXE - 
00266b3c 2fafdf1c mso!Ordinal7674+0x265
00267230 2fafd9e1 EXCEL!Ordinal40+0x23df1c
00267280 3018c1da EXCEL!Ordinal40+0x23d9e1
0026d184 301916f1 EXCEL!Ordinal40+0x8cc1da
0026f798 30192050 EXCEL!Ordinal40+0x8d16f1
0026fa74 301a2046 EXCEL!Ordinal40+0x8d2050
0026fa94 5d166292 EXCEL!Ordinal40+0x8e2046
0026fab4 5d1666cb mso!Ordinal9994+0x24c7
0026facc 5d14992d mso!Ordinal4158+0x1d8
0026faf4 5d14a0df mso!Ordinal9839+0xff0
0026fb0c 5cc40593 mso!Ordinal143+0x415
0026fb30 5d16621f mso!Ordinal6326+0x3b30
0:000&gt; u 5ca40b78 
mso!Ordinal9662+0xdb2:
5ca40b78 8bce            mov     ecx,esi
5ca40b7a e84f000000      call    mso!Ordinal9662+0xe08 (5ca40bce)
5ca40b7f 8b4e2c          mov     ecx,dword ptr [esi+2Ch]
5ca40b82 3bcf            cmp     ecx,edi
5ca40b84 7409            je      mso!Ordinal9662+0xdc9 (5ca40b8f)
5ca40b86 8b01            mov     eax,dword ptr [ecx]
5ca40b88 6a01            push    1
5ca40b8a ff10            call    dword ptr [eax]
```

这里是在IDA中显示的sub_39270b26()的位置。

[![](https://p3.ssl.qhimg.com/t015c96c59cd5336d57.png)](https://p3.ssl.qhimg.com/t015c96c59cd5336d57.png)

我不会涉及漏洞的发现已经关键代码路径,因为目前该漏洞还未被修复,POC攻击实例也在上面列出了。此外,如果利用最近的ALSR绕过技术来利用这次的Excel漏洞,漏洞影响无疑将会扩大。

所以那些版本受到影响呢?所有2007和2010版本,新版本也可能受影响(未进行测试)。测试环境使用的是完全补丁的Office 2010专业版。

[![](https://p4.ssl.qhimg.com/t01d455a19755126bab.png)](https://p4.ssl.qhimg.com/t01d455a19755126bab.png)

总结

我们希望微软能够意识到该问题的严重性,并及时推出相应补丁。这是一个严重的漏洞,而且类似的还不少。
