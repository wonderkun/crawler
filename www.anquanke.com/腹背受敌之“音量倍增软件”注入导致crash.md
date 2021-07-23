> 原文链接: https://www.anquanke.com//post/id/208808 


# 腹背受敌之“音量倍增软件”注入导致crash


                                阅读量   
                                **276281**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t015cb7c02cce6b8f70.png)](https://p0.ssl.qhimg.com/t015cb7c02cce6b8f70.png)



0、为了避免具体公司及相关项目信息的泄漏，本文中隐去了所有名称信息，代之以A、B之类的标识符；



## 1、今天拿到一个比较有意思的dmp，分析之余觉得有趣，撰文以分享。



## 2、分析过程：

2.1、step1：Windbg打开，.exr -1看了下异常记录里所呈现的信息，如下：

```
ExceptionAddress: 5d38a57f
   ExceptionCode: c0000005 (Access violation)
  ExceptionFlags: 00000000
NumberParameters: 2
   Parameter[0]: 00000008
   Parameter[1]: 5d38a57f
Attempt to execute non-executable address 5d38a57f
```

上边标红的两行，第一行的意思是说“访问异常”，基本就是访问了不该访问的内存，比如处于Free状态的内存；或者是该内存是只读的，却往里边写数据了；第二行的意思是说，代码执行了不可执行的部分，换句话说就是EIP跑飞了；当然这个第二行的提示文本是Windbg善解人意的自动推导出来辅助你分析的，可能对也可能不对；且看下边继续分析；

2.2、step2：看一下5d38a57f附近的代码：

```
0:045&gt; u 5d38a57f
5d38a57f ??              ???
                ^ Memory access error in 'u 5d38a57f'
```

咋回事，咋都是些’??’，嗯，正常的，一种情况是这块内存没有被dmp下来，所以Windbg去反汇编这块内存的时候，找不到数据；另一种情况是这块内存本身就是Free的；来看下这块内存的属性如下：

```
0:045&gt; !address 5d38a57f
Usage:                  Free
Base Address:           5d0a6000
End Address:            62670000
Region Size:            055ca000 (  85.789 MB)
State:                  00010000          MEM_FREE
Protect:                00000001          PAGE_NOACCESS
Type:                   &lt;info not present at the target&gt;
```

看来是第二种情况了；线索断了，不急再看看其他的地方，说不定山重水复疑无路，柳暗花明又一村嘞；

2.3、step3：下面就是将上下文恢复到出现问题[异常]时的那会了；执行.ecxr即可；

```
0:045&gt; .ecxr
eax=00001000 ebx=04f015a8 ecx=9a27e8a0 edx=00000000 esi=04f015c6 edi=04f015b0
eip=5d38a57f esp=18a3fe1c ebp=18a3fe64 iopl=0         nv up ei pl nz na po nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010202
5d38a57f ??              ???
```

简单分析下上边所给出的信息；触发异常的显然就是这句汇编代码了，触发的原因也自然是5d38a57f这块内存是PAGE_NOACCESS，而你却Execute了，不挂才怪？这块内存属于谁？看下内存分布，如下：

```
5c8d0000 5c8e8000   dxva2      (deferred)             
5d0a0000 5d0a6000   d3d8thk    (deferred)             
62670000 626b7000   Qt5OpenGL   (deferred)             
64150000 6458e000   Qt5Widgets   (deferred)             
68bb0000 68bc4000   msacm32_68bb0000   (deferred)             
6a690000 6a697000   midimap    (deferred)             
6a6a0000 6a6a8000   msacm32    (deferred)             
6bbc0000 6bbf1000   EhStorShell   (deferred)
```

上图标蓝的两行最接近5d38a57f了，接近归接近，终究还是不属于任何模块，这就奇怪了。好好的EIP咋就跑的乱七八糟的了。看下调用栈吧，如下：

```
0:045&gt; k
# ChildEBP RetAddr  
00 18a3fe18 013e5c4e 0x5d38a57f
01 18a3fe64 013e5d5b aaaa!bbbb::waveOut+0x1fe
02 18a3fe6c 74bb343d aaaa!bbbb::waveOutRoutine+0xb
03 18a3fe78 77179812 kernel32!BaseThreadInitThunk+0xe
04 18a3feb8 771797e5 ntdll!__RtlUserThreadStart+0x70
05 18a3fed0 00000000 ntdll!_RtlUserThreadStart+0x1b

0:045&gt; ub 013e5c4e
aaaa!bbbb::waveOut+0x1e1
013e5c31 ff30            push    dword ptr [eax]
013e5c33 ffb3a4000000    push    dword ptr [ebx+0A4h]
013e5c39 e8d2020000      call    start_for_wegame!fifo_read (013e5f10)
013e5c3e 83c410          add     esp,10h
013e5c41 6a20            push    20h
013e5c43 ff75f8          push    dword ptr [ebp-8]
013e5c46 ff37            push    dword ptr [edi]
013e5c48 ff15fc914101    call    dword ptr [aaaa!_imp__waveOutWrite (014191fc)]
```

逻辑很清晰，是我们的exe调用了waveOutWrite()；这个API是 Winmm.dll中的，是系统的API，难道这个系统的API不够健壮，有bug？传入的错误的参数，其又没有很严格的校验？确实有这可能，但可能性微乎其微，你要学会相信微软啊；好了来看下传入的参数都是啥：

```
00 18a3fe18 013e5c4e 0bd84180 04f015e6 00000020 0x5d38a57f
01 18a3fe64 013e5d5b 18a3fe78 74bb343d 0bd83ed0 aaaa!bbbb::waveOut+0x1fe
02 18a3fe6c 74bb343d 0bd83ed0 18a3feb8 77179812 aaaa!bbbb::waveOutRoutine+0xb

0:045&gt; dd 04f015e6
04f015e6  04808e88 00001000 00000000 00000000
04f015f6  00000003 00000000 00000000 0000007b
```

整理如下：

```
typedef struct wavehdr_tag
`{`
  LPSTR              lpData;            04808e88
  DWORD              dwBufferLength;    00001000
  DWORD              dwBytesRecorded;   00000000
  DWORD_PTR          dwUser;            00000000
  DWORD              dwFlags;           00000003  #define WHDR_DONE | WHDR_PREPARED   
  DWORD              dwLoops;           00000000
  struct wavehdr_tag  *lpNext;          00000000
  DWORD_PTR          reserved;          0000007b
`}` WAVEHDR, *LPWAVEHDR;
```

参数都很正常，那咋回事呢？不妨到这个API里边去看下，看看总归还是可以的；<br>
2.4、step4：核心分析

```
0:045&gt; u Winmm!waveOutWrite
winmm!waveOutWrite:
70ad4f7b e990d5c892      jmp     SBH+0x2510 (03762510)
70ad4f80 56              push    esi
70ad4f81 8b750c          mov     esi,dword ptr [ebp+0Ch]
70ad4f84 6a01            push    1
70ad4f86 ff7510          push    dword ptr [ebp+10h]
70ad4f89 56              push    esi
70ad4f8a e8c2f9ffff      call    winmm!ValidateHeader (70ad4951)
70ad4f8f 85c0            test    eax,eax
```

有意思了，很有意思；正常的API的开头几个字节的反汇编代码通常是：

```
mov edi，edi ；hot patch会用到
```

而这里居然是一个jmp指令,那就说明这里有鬼了，根据给出的跳转目的地址可知，是跑到SBH这个模块里去了； 不妨看一下跳转的那块内存的汇编代码，简单看下他在干啥：

```
0:045&gt; u 03762510
SBH+0x2510:
03762510 ??              ???
                ^ Memory access error in 'u 03762510'
```

没有数据，这是个minidmp，里边的数据有限；那没办法了，只能归因于该crash是由于第三方软件的bug导致的了；但是，我们还有另一条路可走，来看看这个模块是啥，有哪些信息可获取到，如下：

```
0:045&gt; lmvm SBH
start    end        module name
03760000 0379d000   SBH      T (no symbols)           
    Loaded symbol image file: SBH.dll
    Image path: E:迅雷下载Letasoft Sound BoosterSBH.dll
    Image name: SBH.dll
    Browse all global symbols  functions  data
    Timestamp:        Fri Oct 19 00:43:47 2012 (508031C3)
    CheckSum:         0004A8A2
    ImageSize:        0003D000
    File version:     1.1.0.88
    Product version:  1.1.0.88
    File flags:       0 (Mask 3F)
    File OS:          40004 NT Win32
    File type:        2.0 Dll
    File date:        00000000.00000000
    Translations:     0000.04b0 0000.04e4 0409.04b0 0409.04e4
    Information from resource tables:
```

比较有用的信息，已经标红示出；根据经验，软件安装时，安装的目录名都一定程度上代表了这个软件自身的功能或者软件的名字；那从路径中提取出来的文件名就差不多是”Letasoft Sound Booster”，此外，还可以获取到该模块的创建时间戳为”2012-10-19 00:43:47”，下边百度下该软件的名字，看看能捞到哪些信息，如下，这个软件还是个正规的软件，官网为 https://www.letasoft.com/；从搜索到的

[![](https://p2.ssl.qhimg.com/t0115ffdf86005c7665.png)](https://p2.ssl.qhimg.com/t0115ffdf86005c7665.png)

[![](https://p3.ssl.qhimg.com/t011917f2d304ba04b8.png)](https://p3.ssl.qhimg.com/t011917f2d304ba04b8.png)

信息来看，这个软件的功能是增大音量的，其与dmp中所牵扯进来的waveOutWrite()也是对的上的，该软件还有官网，说明该软件确实是正规软件。要再继续往下边查原因的话，就需要去下载这个版本的，做下逆向分析了，但所得并不会太多，因为既然是正规软件且还是收费的，值来应该是可靠的，这里导致的crash，可能是极端情况下的某个bug，也必然不太容易复线。



## 3、dmp分析之外的探究——SBH.dll是怎么注入到进程里去的？

通常Ring3的注入方法无怪乎以下几种，

```
导入表注入：直接修改PE头，手动构造一项IAT表；
挂起线程注入：修改CONTEXT.Eip；
挂起进程注入：分为ShellCode法和Shim法，其中Shim法不太稳定，严重依赖系统版本；
注册表注入：AppInit_DLLs键值
钩子注入：利用SetWindowsHookEx拦截消息进行注入
APC注入：往用户态Apc队列中丢一项；
远程线程注入：CreateRemoteThread即可
输入法注入：构造自己的Ime文件
DLL劫持：利用Dll搜索的路径顺序加载我们自己构造好的Dll，然后再转发至真正的Dll；
```

但考虑到，这个软件是正规军，不可能用一些“猥琐的”跨平台特性较差的方法来进行SBH.dll的注入；猜测它用到的方法大概率为：

SetWindowsHookEx &gt; CreateRemoteThread&gt;其他<br>
为了研究这个问题，我下载了一个下来测试下，下载的版本如下：

[![](https://p5.ssl.qhimg.com/t014341cc9d1bbfed09.png)](https://p5.ssl.qhimg.com/t014341cc9d1bbfed09.png)

[![](https://p1.ssl.qhimg.com/t017717eac349f81c82.png)](https://p1.ssl.qhimg.com/t017717eac349f81c82.png)

[![](https://p5.ssl.qhimg.com/t016e87df20b81d5447.png)](https://p5.ssl.qhimg.com/t016e87df20b81d5447.png)

运行起来之后，是上边右图所示。此时我可怜的QQMusic已经被注入了该Dll；一点点防备都没有；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ac2ea9e9df816528.png)

来吧，开始干吧，祭出我们的核武器——Windbg；一顿操作之后挂到SoundBooster.exe上；继而操作如下：

```
0:008&gt; x User32!SetWindowsHookEx*
76a6f190          USER32!SetWindowsHookExA (&lt;no parameter info&gt;)
76a7f8e0          USER32!SetWindowsHookExAW (&lt;no parameter info&gt;)
76a7b610          USER32!SetWindowsHookExW (&lt;no parameter info&gt;)

0:009&gt; bm User32!SetWindowsHookEx*
  1: 76a6f190          @!"USER32!SetWindowsHookExA"
  2: 76a7f8e0          @!"USER32!SetWindowsHookExAW"
  3: 76a7b610          @!"USER32!SetWindowsHookExW"

0:009&gt; bl
     1 e Disable Clear  76a6f190     0001 (0001)  0:**** USER32!SetWindowsHookExA
     2 e Disable Clear  76a7f8e0     0001 (0001)  0:**** USER32!SetWindowsHookExAW
     3 e Disable Clear  76a7b610     0001 (0001)  0:**** USER32!SetWindowsHookExW
```

顷刻之间，相干API都已经被我们安插了眼线，然后选中”启用”复选框；一切如所料，命中了，如下：

```
0:009&gt; g
Breakpoint 1 hit
eax=00000000 ebx=00000001 ecx=10000000 edx=10007be0 esi=10072be8 edi=010a0000
eip=76a6f190 esp=0019ef0c ebp=0019f1b0 iopl=0         nv up ei pl zr na pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00200246
USER32!SetWindowsHookExA:
76a6f190 8bff            mov     edi,edi
0:000&gt; k
# ChildEBP RetAddr  
00 0019ef08 100073e2 USER32!SetWindowsHookExA
WARNING: Stack unwind information not available. Following frames may be wrong.
01 0019f1b0 0048d1f5 SBH+0x73e2
02 0019f1e0 0048c7b3 SoundBooster+0x8d1f5
03 0019f204 00492f71 SoundBooster+0x8c7b3
04 0019f254 00493985 SoundBooster+0x92f71
05 0019f2f0 0049034e SoundBooster+0x93985
06 0019f310 0049243d SoundBooster+0x9034e
07 0019f378 004924ca SoundBooster+0x9243d
08 0019f398 76a7bafb SoundBooster+0x924ca
09 0019f3c4 76a77e7a USER32!_InternalCallWinProc+0x2b
0a 0019f4ac 76a5c21a USER32!UserCallWinProcCheckWow+0x3aa
0b 0019f518 76a5bfa7 USER32!SendMessageWorker+0x20a
0c 0019f558 7163e96f USER32!SendMessageW+0x137
0d 0019f578 7163e92f COMCTL32!Button_NotifyParent+0x39
0e 0019f590 716697f1 COMCTL32!Button_ReleaseCapture+0x88
0f 0019f5e4 76a7bafb COMCTL32!Button_WndProc+0x3b1
10 0019f610 76a77e7a USER32!_InternalCallWinProc+0x2b
11 0019f6f8 76a57e4d USER32!UserCallWinProcCheckWow+0x3aa
12 0019f734 00490254 USER32!CallWindowProcW+0x8d
13 0019f754 00490365 SoundBooster+0x90254
14 0019f770 0049243d SoundBooster+0x90365
15 0019f7d8 004924ca SoundBooster+0x9243d
16 0019f7f8 76a7bafb SoundBooster+0x924ca
17 0019f824 76a77e7a USER32!_InternalCallWinProc+0x2b
18 0019f90c 76a7772e USER32!UserCallWinProcCheckWow+0x3aa
19 0019f988 76a5a613 USER32!DispatchMessageWorker+0x20e
1a 0019f9c8 004906d2 USER32!IsDialogMessageW+0x103
1b 0019fac8 00000000 SoundBooster+0x906d2
SetWindowsHookExA的原型以及传入的参数如下：

0:000&gt; dd 0019ef08+8 l4
0019ef10  00000003 10007350 10000000 00000000
```

```
HHOOK SetWindowsHookExA( 
int idHook,              00000003   ----&gt; WH_GETMESSAGE
HOOKPROC lpfn,           10007350
HINSTANCE hmod,          10000000   ----&gt;SBH.dll
DWORD dwThreadId         00000000   ----&gt;全局钩子
);

0:000&gt; !inmodule 10000000
0x10000000: SBH
```

那基本实锤了，这个软件就是通过的消息钩子安装的全局钩子注入到其他进程的；钩子的过程为0x10007350；看下反汇编代码，简单分析下：

```
SBH+0x7350:
10007350 56              push    esi
10007351 8b742408        mov     esi,dword ptr [esp+8]    ;code
10007355 85f6            test    esi,esi
10007357 57              push    edi
10007358 8b7c2414        mov     edi,dword ptr [esp+14h]  ;PMGS
1000735c 7516            jne     SBH+0x7374 (10007374)
1000735e 803df84a071000  cmp     byte ptr [SBH!KLHGetManager+0x6d078 (10074af8)],0
10007365 750d            jne     SBH+0x7374 (10007374)
10007367 8b07            mov     eax,dword ptr [edi]
10007369 50              push    eax                      ;hwnd
1000736a b9dc450710      mov     ecx,offset SBH!KLHGetManager+0x6cb5c (100745dc)
1000736f e8bcf8ffff      call    SBH+0x6c30 (10006c30)
10007374 8b4c2410        mov     ecx,dword ptr [esp+10h]
10007378 8b152c430710    mov     edx,dword ptr [SBH!KLHGetManager+0x6c8ac (1007432c)]
1000737e 8b4218          mov     eax,dword ptr [edx+18h]
10007381 57              push    edi
10007382 51              push    ecx
10007383 56              push    esi
10007384 50              push    eax
10007385 ff1518120410    call    dword ptr [SBH!KLHGetManager+0x39798 (10041218)];USER32!CallNextHookEx
1000738b 5f              pop     edi
1000738c 5e              pop     esi
1000738d c20c00          ret     0Ch

0:000&gt; ln poi(10041218)
(76a7a470)   USER32!CallNextHookEx   |  (76a7a530)   USER32!GetThreadDpiAwarenessContext
Exact matches:
    USER32!CallNextHookEx (void)
```

适可而止吧，再分析下去就是逆向这个软件的具体行为了，那就侵权了。
