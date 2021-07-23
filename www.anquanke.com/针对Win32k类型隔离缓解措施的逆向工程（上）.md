> 原文链接: https://www.anquanke.com//post/id/97498 


# 针对Win32k类型隔离缓解措施的逆向工程（上）


                                阅读量   
                                **132783**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Francisco Falcon，文章来源：blog.quarkslab.com
                                <br>原文地址：[https://blog.quarkslab.com/reverse-engineering-the-win32k-type-isolation-mitigation.html](https://blog.quarkslab.com/reverse-engineering-the-win32k-type-isolation-mitigation.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t010193eea70ce1c5e2.jpg)](https://p5.ssl.qhimg.com/t010193eea70ce1c5e2.jpg)



## 一、前言

目前，越来越多人开始借助GDI Bitmaps对象来实现内核漏洞利用。几乎任何形式的内核损坏漏洞（除NULL写入外），都可以借助于对Bitmaps的滥用，来可靠地获得内核内存的任意R/W原语。基于这一点，微软正在努力防御基于Bitmaps的漏洞利用。为此，在Windows 10秋季创意者更新（Windows 10 1709）中，引入了类型隔离（Type Isolation）功能，该功能是Win32k子系统中的一项漏洞利用缓解措施，会对SURFACE对象的内存布局（即内核端Bitmap的内部表示）进行拆分。本文深入介绍了类型隔离的相关细节，并通过逆向工程帮助大家理解其原理。受篇幅所限，本文将分为上下两篇。



## 二、分析样本

本次分析所采用的样本是Windows 10秋季创意者更新（x64）上的win32kbase.sys，文件版本号为10.0.16288.1，这是2017年10月Windows 10 1709公开发布前的最后一个内部预览版本。在撰写本文（2018年1月底）之前，我们将其与最新的win32kbase.sys（版本号为10.0.16299.125）进行了对比，结果表明类型隔离的相关功能无任何变化。



## 三、技术背景

自2015年年中起，一类GDI对象，即Bitmaps便成为了漏洞利用开发者在进行Windows上内核漏洞利用时的首选。在Windows内核中，这种类型的数据结构包含一些非常危险的成员，只要借助于内存损坏的安全漏洞，攻击者就可以对内核地址空间拥有完整的读/写权限。从内核的角度来看，Bitmap是由一个SURFACE对象使用以下结构来表示的：

```
typedef struct _SURFACE `{`
    BASEOBJECT BaseObject;
    SURFOBJ surfobj;
    [...]
`}`
```

BASEOBJECT是一个常见的对象类型，其定义如下：

```
typedef struct _BASEOBJECT `{`
    HANDLE hHmgr;
    ULONG  ulShareCount;
    USHORT cExclusiveLock;
    USHORT BaseFlags;
    PVOID  Tid;
`}` BASEOBJECT, *PBASEOBJECT;
```

我们重点关注的是SURFACE的特定结构——SURFOBJ，其定义如下：

```
typedef struct _SURFOBJ `{`
    DHSURF dhsurf;
    HSURF  hsurf;
    DHPDEV dhpdev;
    HDEV   hdev;
    SIZEL  sizlBitmap;
    ULONG  cjBits;
    PVOID  pvBits;
    PVOID  pvScan0;
    LONG   lDelta;
    ULONG  iUniq;
    ULONG  iBitmapFormat;
    USHORT iType;
    USHORT fjBitmap;
`}` SURFOBJ, *PSURFOBJ;
```

在该结构中，有两个值得关注的成员，分别是pvScan0和sizlBitmap。pvScan0指向保存Bitmap像素数据的缓冲区，sizlBitmap保存Bitmap的尺寸（宽度及高度）。我们主要有两种方式，可以通过破坏前面提到的成员，来实现针对SURFACE对象的利用：
1. GetBitmapBits和SetBitmapBits的GDI API都能对SURFOBJ结构的pvScan0成员所指向的像素数据缓冲区进行操作。因此，覆盖这个指针，可以实现以用户模式对内核内存的任意读/写。
1. SURFOB结构的sizlBitmap成员保存了Bitmap的宽度和高度属性。通过覆盖sizlBitmap.cx或sizlBitmap.cy，可以对像素数据缓冲区进行“放大”。这样就可以实现对像素缓冲区之后内核内存的读/写访问。
这两种方法涉及到两个不同的Bitmap对象，如果你想深入研究上述内容，我建议你阅读2016年Ekoparty会议上发表的题为“Abusing GDI for ring0 exploit primitives: Reloaded”的演讲（ [https://www.coresecurity.com/system/files/publications/2016/10/Abusing-GDI-Reloaded-ekoparty-2016_0.pdf](https://www.coresecurity.com/system/files/publications/2016/10/Abusing-GDI-Reloaded-ekoparty-2016_0.pdf) ），该演讲由Diego Juárez和Nicolás Economou发表。<br>
第一种方式，向攻击者提供了完整的读/写功能。但其不足之处在于，需要借助于一个好用的漏洞（比如对某处的写入）才能实现，这一漏洞应该允许用任意值覆盖pvScan0指针。<br>
第二种技术虽然看起来没有那么强大，但由于它能够提供对于像素数据缓冲区结束之后的内存读/写权限，因此不需要借助于非常严重的漏洞即可轻松实现，此外可以轻松进行递增或递减，非常方便操作。要覆盖SURFOBJ结构的sizlBitmap成员，需要在内存中创建两个相邻的SURFACE对象（我们在这里称为SURFACE1和SURFACE2），通过破坏SURFACE1的sizlBitmap，使其像素缓冲区被“放大”，从而与相邻的SURFACE2对象重叠。此后，经过放大的SURFACE1就可以覆盖SURFACE2头部的成员。针对超出SURFACE1像素缓冲区范围的部分，本来只拥有有限的读/写权限，经过放大之后，我们便拥有了完全任意读/写的权限。<br>
大家可能会注意到，第二种利用方式的可行性非常高。因为，Bitmap的像素缓冲区通常与SURFACE头部相邻，整个SURFACE对象都是通过一个单独的内存分配创建的，其大小足够容纳SURFACE头部和像素数据缓冲区。这样一来，漏洞利用者就能够得到一个非常有用的内存布局，其中哪个一个SURFACE对象的像素数据缓冲区可以紧跟着另一SURFACE对象的头部。<br>
考虑到第二种方式允许通过对GDI Bitmap对象的滥用，将几乎任何类型的内存损坏漏洞（除NULL写入外）转化为内核内存任意读写漏洞，微软决定要对该方式进行防范。为此，在Windows 10秋季创意者更新（Windows 10 1709）中引入了类型隔离（Type Isolation）功能，该功能是Win32k子系统中的一项漏洞利用缓解措施，会对SURFACE对象的内存布局（即内核端Bitmap的内部表示）进行拆分。



## 四、类型隔离的详细分析

### <a class="reference-link" name="4.1%20%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84"></a>4.1 数据结构

类型隔离是通过许多链式结构实现的。具体主要有4种数据结构与之相关，分别是：<br>
CTypeIsolation<br>
CSectionEntry<br>
CSectionBitmapAllocator<br>
RTL_BITMAP<br>
尽管第四个RTL_BITMAP结构不仅仅用于类型隔离，但这一著名的Windows内核不透明结构在这里起着重要的作用。<br>
所有这些，都是从使用ExAllocatePoolWithTag的PagedPoolSession pool中分配的。它们共享一个新的4字节池标记（Pool Tag）Uiso，并且用于SURFACE对象的像素数据缓冲区的池标记也会由“Gh?5”变为“Gpbm”。<br>
静态变量win32kbase!gpTypeIsolation是一个指针，它指向另一个指向全局CTypeIsolation结构的指针。CTypeIsolation是CSectionEntry对象的循环双向链表的头部，而CSectionEntry负责管理0xF0 SURFACE头部。每个CSectionEntry都具有一个CSectionBitmapAllocator对象，该对象负责维护两个主要对象的同步：一个段的0x28视图（View）数组，其中每个视图可以包含6个SURFACE头部；以及一个比特位图（map of bits，即RTL_BITMAP），用于跟踪每个0x28 * 6 == 0xF0可用位置的忙/闲状态。CSectionEntry对象的双向链表可以根据需要进行扩增。<br>
通过逆向工程，我们掌握了这4种数据结构的定义，并知道了它们的大小及各自成员的偏移量，具体如下：<br>
1、CTypeIsolation（大小为0x20字节）

```
typedef struct _CTYPEISOLATION `{`
    PCSECTIONENTRY  next;           // + 0x00
    PCSECTIONENTRY  previous;       // + 0x08
    PVOID           pushlock;       // + 0x10
    ULONG64         size;           // + 0x18
`}` CTYPEISOLATION, *PCTYPEISOLATION;
```

2、CSectionEntry（大小为0x28字节）

```
typedef struct _CSECTIONENTRY CSECTIONENTRY, *PCSECTIONENTRY;

struct _CSECTIONENTRY `{`
    CSECTIONENTRY   *next;          // + 0x00
    CSECTIONENTRY   *previous;      // + 0x08
    PVOID           section;        // + 0x10
    PVOID           view;           // + 0x18
    PCSECTIONBITMAPALLOCATOR bitmap_allocator;  // + 0x20
`}`;
```

3、CSectionBitmapAllocator（大小为0x28字节）

```
typedef struct _CSECTIONBITMAPALLOCATOR `{`
    PVOID           pushlock;           // + 0x00
    ULONG64         xored_view;         // + 0x08
    ULONG64         xor_key;            // + 0x10
    ULONG64         xored_rtl_bitmap;   // + 0x18
    ULONG           bitmap_hint_index;  // + 0x20
    ULONG           num_commited_views; // + 0x24
`}` CSECTIONBITMAPALLOCATOR, *PCSECTIONBITMAPALLOCATOR;
```

4、RTL_BITMAP（大小为0x10字节）

```
typedef struct _RTL_BITMAP `{`
    ULONG64         size;               // + 0x00
    PVOID           bitmap_buffer;      // + 0x08
`}` RTL_BITMAP, *PRTL_BITMAP;
```

下图展现了所有相关数据结构之间的关系：<br>[![](https://blog.quarkslab.com/resources/2018-01-26-win32k-type-isolation/images/data-structures.png)](https://blog.quarkslab.com/resources/2018-01-26-win32k-type-isolation/images/data-structures.png)<br>
上图展现了具有3个CSectionEntry实例的Type Isolation结构的假想状态，其中的每个实例都有相关联的CSectionBitmapAllocator和RTL_BITMAP实例。由于CSectionEntry的各实例管理0xF0 SURFACE标头，因此CTypeIsolation对象的成员大小设定为0xF0 * 3 == 0x2D0。<br>
此外，图中还标出了支持第一个CSectionEntry的0x28视图。在所有的0x28视图中，只有两个被使用，其余都处于未映射状态。第一个视图已满：SURFACE头部使用了大小为0x280的全部6个位置（页尾部的0x100备用字节未在图中体现）。第二个视图只使用了一半：3个0x280字节的位置正在使用中，而另外3个未被使用。同时，每个位置的忙/闲状态会与相同CSectionEntry的RTL_BITMAP中的比特位图（map of bits）保持同步。在这一假设的前提下，前9个位置会被使用，其余均为被使用，比特位图将如下所示：11111111 00000001 00000000 00000000…<br>
此外，由于所有访问均是通过视图来完成，并没有直接访问相应段，为简单起见，上图没有绘制支持视图对象的Section对象。<br>
还有，win32kbase!SURFACE::tSize静态变量的大小为0x278。然而通过我们对代码的分析，计算出每个SURFACE头部的大小为280字节，这可能是由于考虑了对齐的因素。

```
.data:00000001C0196110 ; Exported entry 387. ?tSize@SURFACE@@0_KA
.data:00000001C0196110                 public private: static unsigned __int64 SURFACE::tSize
.data:00000001C0196110 private: static unsigned __int64 SURFACE::tSize dq 278h
```

### <a class="reference-link" name="4.2%20%E5%88%9D%E5%A7%8B%E5%8C%96"></a>4.2 初始化

类型隔离结构的初始化，发生在win32kbase!HmgCreate()中，并在win32kbase.sys驱动的初始化过程中被调用。初始化过程首先会分配一个指向后面头部NSInstrumentation::CTypeIsolation结构的指针，并将其保存到win32kbase!gpTypeIsolation全局变量中。然后，会调用CTypeIsolation::Create()方法，分配头部CTypeIsolation结构。

```
HmgCreate+397                  mov     edx, 'osiU'
HmgCreate+39C                  mov     rcx, r14        ; size = 8 (ptr to CTypeIsolation)
HmgCreate+39F                  call    Win32AllocPool
HmgCreate+3A4                  mov     cs:uchar * * gpTypeIsolation, rax
HmgCreate+3AB                  test    rax, rax
HmgCreate+3AE                  jz      short loc_1C0012561
HmgCreate+3B0                  xor     ecx, ecx
HmgCreate+3B2                  mov     [rax], rcx
HmgCreate+3B5                  call    TypeIsolationFactory&lt;NSInstrumentation::CTypeIsolation&lt;163840,640&gt;&gt;::Create(uchar * *)
```

CTypeIsolation::Create()为CTypeIsolation对象分配0x20字节，随后调用CTypeIsolation::Initialize()对其进行初始化。如果一切正常，则CTypeIsolation对象的地址将会保存到win32kbase!gpTypeIsolation所引用的指针的位置。

```
.text:00000001C001263C public: static bool TypeIsolationFactory&lt;class NSInstrumentation::CTypeIsolation&lt;163840, 640&gt;&gt;::Create(unsigned char * *) proc near
[...]
.text:00000001C001264D                 mov     edx, 20h        ; NumberOfBytes
.text:00000001C0012652                 mov     r8d, 'osiU'     ; Tag
.text:00000001C0012658                 lea     ecx, [rdx+1]    ; PoolType
.text:00000001C001265B                 call    cs:__imp_ExAllocatePoolWithTag ; allocates a NSInstrumentation::CTypeIsolation object
.text:00000001C0012661                 mov     rbx, rax        ; rbx = CTypeIsolation object
.text:00000001C0012664                 test    rax, rax
.text:00000001C0012667                 jz      short loc_1C0012699
.text:00000001C0012669                 and     qword ptr [rax+10h], 0 ; CTypeIsolation-&gt;pushlock = NULL
.text:00000001C001266E                 mov     rcx, rax
.text:00000001C0012671                 and     dword ptr [rax+18h], 0 ; CTypeIsolation-&gt;size = 0
.text:00000001C0012675                 mov     [rax+8], rax    ; CTypeIsolation-&gt;previous = this
.text:00000001C0012679                 mov     [rax], rax      ; CTypeIsolation-&gt;next = this
.text:00000001C001267C                 call    NSInstrumentation::CTypeIsolation&lt;163840,640&gt;::Initialize(void)
.text:00000001C0012681                 test    al, al
.text:00000001C0012683                 jz      loc_1C00BA344
.text:00000001C0012689                 mov     [rdi], rbx      ; *win32kbase!gpTypeIsolation = CTypeIsolation
```

非常值得注意的是，CTypeIsolation::Initialize()通过调用CSectionEntry::Create()来创建一个CSectionEntry结构，并将其分配给CTypeIsolation对象的下一个和上一个成员：

```
.text:00000001C0039A34 private: bool NSInstrumentation::CTypeIsolation&lt;163840, 640&gt;::Initialize(void) proc near
[...]
.text:00000001C0039A5E                 call    NSInstrumentation::CSectionEntry&lt;163840,640&gt;::Create(void)
.text:00000001C0039A63                 test    rax, rax        ; rax == CSectionEntry object
.text:00000001C0039A66                 jz      short loc_1C0039A92
.text:00000001C0039A68                 mov     rcx, [rbx+8]    ; rcx = CTypeIsolation-&gt;previous
.text:00000001C0039A6C                 mov     dword ptr [rbx+18h], 0F0h ; CTypeIsolation-&gt;size = 0xF0
.text:00000001C0039A73                 cmp     [rcx], rbx      ; CTypeIsolation-&gt;previous-&gt;next == CTypeIsolation?
.text:00000001C0039A76                 jnz     FatalListEntryError_10
.text:00000001C0039A7C                 mov     [rax], rbx      ; CSectionEntry-&gt;next= CTypeIsolation
.text:00000001C0039A7F                 mov     [rax+8], rcx    ; CSectionEntry-&gt;previous = CTypeIsolation-&gt;previous
.text:00000001C0039A83                 mov     [rcx], rax      ; *CTypeIsolation-&gt;previous-&gt;next = CSectionEntry
.text:00000001C0039A86                 mov     [rbx+8], rax    ; CTypeIsolation-&gt;previous = CSectionEntry
```

接下来，CSectionEntry::Create()调用CSectionEntry::Initialize()，后者通过调用nt!MmCreateSection()来创建一个Section对象。这里Section的大小是0x28000字节，Section将会通过0x28视图被访问，每一个大小为0x1000字节。指向此Section对象的指针存储在CSectionEntry结构中。

```
.text:00000001C0099E5C                 lea     r9, [rbp+arg_0] ; MaximumSize
.text:00000001C0099E60                 xor     eax, eax
.text:00000001C0099E62                 mov     rdi, rcx        ; rdi = CSectionEntry object
.text:00000001C0099E65                 and     [r11-10h], rax
.text:00000001C0099E69                 lea     rcx, [rbp+SectionHandle] ; SectionHandle
.text:00000001C0099E6D                 and     [r11-18h], rax
.text:00000001C0099E71                 xor     r8d, r8d        ; ObjectAttributes
.text:00000001C0099E74                 mov     [rbp+arg_0], rax
.text:00000001C0099E78                 mov     edx, 0F001Fh    ; DesiredAccess = SECTION_ALL_ACCESS
.text:00000001C0099E7D                 mov     [rsp+40h+var_18], SEC_RESERVE ; AllocationAttributes
.text:00000001C0099E85                 mov     [rsp+40h+var_20], PAGE_READWRITE ; SectionPageProtection
.text:00000001C0099E8D                 mov     dword ptr [rbp+arg_0], 28000h ; size for the Section
.text:00000001C0099E94                 call    cs:__imp_MmCreateSection
```

然后，将会映射该Section的视图。指向视图的指针同样保存在CSectionEntry结构中。

```
.text:00000001C0099EB8                 mov     [rdi+10h], rcx  ; CSectionEntry-&gt;section = section
.text:00000001C0099EBC                 test    rcx, rcx
.text:00000001C0099EBF                 jz      short loc_1C0099F0F
.text:00000001C0099EC1                 and     [rbp+arg_0], 0
.text:00000001C0099EC6                 lea     rbx, [rdi+18h]  ; rbx = ptr to output view
.text:00000001C0099ECA                 mov     rdx, rbx
.text:00000001C0099ECD                 lea     r8, [rbp+arg_0]
.text:00000001C0099ED1                 call    cs:__imp_MmMapViewInSessionSpace ; populates CSectionEntry-&gt;view
```

最后，CSectionEntry::Initialize()通过调用CSectionBitmapAllocator::Create()来创建一个CSectionBitmapAllocator对象。指向此对象的指针，存储在CSectionEntry结构中。

```
.text:00000001C0099EED                 mov     rcx, [rbx]      ; rcx = CSectionEntry-&gt;view
.text:00000001C0099EF0                 call    NSInstrumentation::CSectionBitmapAllocator&lt;163840,640&gt;::Create(uchar * const)
.text:00000001C0099EF5                 test    rax, rax        ; rax = CSectionBitmapAllocator
.text:00000001C0099EF8                 mov     [rdi+20h], rax  ; CSectionEntry-&gt;bitmap_allocator = CSectionBitmapAllocator
```

正如我们猜想的那样，CSectionBitmapAllocator::Create()将会调用CSectionBitmapAllocator::Initialize()。该方法会分配一个0x30大小的缓冲池，用于保存RTL_BITMAP结构。请注意，在这里我们并不讨论GDI Bitmap对象，而是讨论通用的位图，通常适用于跟踪一组可重用项。该池缓冲区的第一个0x10字节用于保存位图的头部，其余的0x20字节用于保存位本身的映射。0x20字节的缓冲区可以保存0x100位，但只有在调用nt!RtlInitializeBitMap的时候才会将位数定义为0xF0，这样就能匹配由CSectionEntry处理的SURFACE数量。然后，通过调用nt!RtlClearAllBits将位图中所有位初始化为0。

```
.text:00000001C009E324 allocate_rtl_bitmap proc near
[...]
.text:00000001C009E333                 mov     ecx, 21h        ; PoolType = PagedPoolSession
.text:00000001C009E338                 cmp     edx, edi
.text:00000001C009E33A                 mov     r8d, 'osiU'     ; Tag = 'Uiso'
.text:00000001C009E340                 cmovnb  edi, edx        ; edi = 0xF0
.text:00000001C009E343                 mov     edx, edi
.text:00000001C009E345                 shr     edx, 3          ; edx = 0x1e
.text:00000001C009E348                 add     edx, 7          ; edx = 0x25
.text:00000001C009E34B                 and     edx, 0FFFFFFF8h ; edx = 0x20
.text:00000001C009E34E                 add     edx, 10h        ; NumberOfBytes = 0x30
.text:00000001C009E351                 call    cs:__imp_ExAllocatePoolWithTag ; allocs 0x30 bytes for a RTL_BITMAP
.text:00000001C009E357                 mov     rbx, rax
.text:00000001C009E35A                 test    rax, rax
.text:00000001C009E35D                 jz      short loc_1C009E386
.text:00000001C009E35F                 lea     rdx, [rax+10h]  ; BitMapBuffer (0x30 - 0x10 bytes)
.text:00000001C009E363                 mov     r8d, edi        ; SizeOfBitMap (number of bits) = 0xF0
.text:00000001C009E366                 mov     rcx, rax        ; BitMapHeader
.text:00000001C009E369                 call    cs:__imp_RtlInitializeBitMap
.text:00000001C009E36F                 mov     rcx, rbx        ; BitMapHeader
.text:00000001C009E372                 call    cs:__imp_RtlClearAllBits
```

除了分配RTL_BITMAP结构外，CSectionBitmapAllocator::Initialize()还会生成一个64位的随机数，提供给XOR键用来对先前分配给视图和RTL_BITMAP对象的指针进行编码：

```
.text:00000001C002DE38 private: bool NSInstrumentation::CSectionBitmapAllocator&lt;163840, 640&gt;::Initialize(unsigned char *) proc near
[...]
.text:00000001C002DE48                 rdtsc                   ; source for RtlRandomEx
.text:00000001C002DE4A                 shl     rdx, 20h
.text:00000001C002DE4E                 lea     rcx, [rsp+28h+arg_0]
.text:00000001C002DE53                 or      rax, rdx
.text:00000001C002DE56                 mov     [rsp+28h+arg_0], eax
.text:00000001C002DE5A                 call    cs:__imp_RtlRandomEx ; get a 32-bit random number
.text:00000001C002DE60                 mov     eax, eax
.text:00000001C002DE62                 lea     rcx, [rsp+28h+arg_0]
.text:00000001C002DE67                 shl     rax, 20h        ; shift eax to the higher part of RAX
.text:00000001C002DE6B                 mov     [rbx+10h], rax  ; CSectionBitmapAllocator-&gt;xor_key = random
.text:00000001C002DE6F                 call    cs:__imp_RtlRandomEx ; get another 32-bit random number
.text:00000001C002DE75                 mov     eax, eax
.text:00000001C002DE77                 or      [rbx+10h], rax  ; CSectionBitmapAllocator-&gt;xor_key |= another_random
```

指向视图和RTL_BITMAP对象的XOR后指针存储在CSectionBitmapAllocator结构中。

```
.text:00000001C002DEB8                 mov     rdx, [rbx+10h]  ; rdx = CSectionBitmapAllocator-&gt;xor_key
.text:00000001C002DEBC                 mov     rcx, rdx
.text:00000001C002DEBF                 xor     rcx, rax        ; rcx = CSectionBitmapAllocator-&gt;xor_key ^ RTL_BITMAP
.text:00000001C002DEC2                 mov     al, 1
.text:00000001C002DEC4                 xor     rdx, rdi        ; rdx = CSectionBitmapAllocator-&gt;xor_key ^ CSectionEntry-&gt;view
.text:00000001C002DEC7                 mov     [rbx+18h], rcx  ; CSectionBitmapAllocator-&gt;xored_rtl_bitmap = CSectionBitmapAllocator-&gt;xor_key ^ RTL_BITMAP
.text:00000001C002DECB                 mov     [rbx+8], rdx    ; CSectionBitmapAllocator-&gt;xored_view = CSectionBitmapAllocator-&gt;xor_key ^ CSectionEntry-&gt;view
```

以上，我们对类型隔离的数据结构和初始化过程进行了详细分析。在下篇文章中，我们将会详细讲解类型隔离的分配和释放过程，并提供WinDBG的扩展，请大家继续关注。
