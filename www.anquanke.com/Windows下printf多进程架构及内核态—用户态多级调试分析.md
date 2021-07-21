> 原文链接: https://www.anquanke.com//post/id/213429 


# Windows下printf多进程架构及内核态—用户态多级调试分析


                                阅读量   
                                **188135**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t010db17558cfd462b2.jpg)](https://p1.ssl.qhimg.com/t010db17558cfd462b2.jpg)



## 0、主要内容

全文围绕着微软底层是如何实现printf的这个宗旨，从应用程序开始着手分析，一直到内核层，进行双机调试，顺藤摸瓜，追寻数据的流向，又从内核回到用户态程序，接着又依据内核态调试时获知的信息，对用户态另一个进程进行分析，抓出了一系列的信息，使得这个问题越来越清楚，完完全全将printf的实现过程大白于天下。

涉及到的内容如下：

1、内核对象及内核对象管理；<br>
2、设备驱动程序及驱动程序对象；<br>
3、MDL；<br>
4、用户态程序与内核驱动通信DeviceIoControl；<br>
5、Windbg调试；<br>
6、C运行时库代码分析；



## 1、背景

作为程序员，printf这个函数肯定是不陌生的，刚学C语言那会，第一个程序基本也都是经典的printf(“hello world\n”)吧，一用十几年了，但重来都没有深究过背后的实现原理，只知道他是C语言标准库规定的，用起来很爽。最近几天恰好得闲，于是花了点时间把这个问题给搞清楚了；整个过程非常有意思，本以为简单分析下微软随IDE一起公布的C运行时库代码就能搞清楚的，可越分析越发现仅仅依靠这点源码压根解不开谜团，或者说，C运行时库关于printf的部分仅仅只有一个核心的API，遂搭建双机调试，进行内核分析；



## 2、分析过程之源码部分分析

### <a class="reference-link" name="2.1%E5%AE%9E%E4%BE%8B%E4%BB%A3%E7%A0%81%E5%A6%82%E4%B8%8B%EF%BC%8C%E5%BE%88%E7%AE%80%E5%8D%95%EF%BC%9BIDE%E6%98%AFVS2017%EF%BC%9B%E8%BF%99%E9%83%A8%E5%88%86%E6%BA%90%E7%A0%81%E8%BE%83%E5%A4%9A%EF%BC%8C%E5%A4%A7%E5%AE%B6%E8%80%90%E5%BF%83%E7%9C%8B%E5%AE%8C"></a>2.1实例代码如下，很简单；IDE是VS2017；这部分源码较多，大家耐心看完

```
#include &lt;stdio.h&gt;
#include &lt;Windows.h&gt;

int _tmain(int argc, _TCHAR* argv[])
`{`
    while(1)
    `{`
        printf("hello world\n");
        Sleep(500);
    `}`

    return 0;
`}`
```

每隔500ms就打印一下字符串“hello world\n”；下边来跟一下VC运行时库的源码；源码步骤比较繁琐，如果不感兴趣可直接略过，看后边的结论；总结起来就是一句话printf——-&gt;WriteFile();

### <a class="reference-link" name="2.2%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90"></a>2.2源码分析

[![](https://p4.ssl.qhimg.com/t01f51d324ac54aa54c.png)](https://p4.ssl.qhimg.com/t01f51d324ac54aa54c.png)

[![](https://p1.ssl.qhimg.com/t018237b5ad7d6af155.png)](https://p1.ssl.qhimg.com/t018237b5ad7d6af155.png)

[![](https://p5.ssl.qhimg.com/t01a25a05440f1db0bc.png)](https://p5.ssl.qhimg.com/t01a25a05440f1db0bc.png)

[![](https://p4.ssl.qhimg.com/t01eceda7c2d9da816b.png)](https://p4.ssl.qhimg.com/t01eceda7c2d9da816b.png)

[![](https://p1.ssl.qhimg.com/t01e1feaaf86fc030bb.png)](https://p1.ssl.qhimg.com/t01e1feaaf86fc030bb.png)

[![](https://p3.ssl.qhimg.com/t01d95a3c0a3f804255.png)](https://p3.ssl.qhimg.com/t01d95a3c0a3f804255.png)

[![](https://p1.ssl.qhimg.com/t01f38cbebaf93484a6.png)](https://p1.ssl.qhimg.com/t01f38cbebaf93484a6.png)

[![](https://p5.ssl.qhimg.com/t01ddc50ee6d45f1e31.png)](https://p5.ssl.qhimg.com/t01ddc50ee6d45f1e31.png)

[![](https://p0.ssl.qhimg.com/t01074a5b6d336bb2d1.png)](https://p0.ssl.qhimg.com/t01074a5b6d336bb2d1.png)

[![](https://p2.ssl.qhimg.com/t01e0b51cc886977299.png)](https://p2.ssl.qhimg.com/t01e0b51cc886977299.png)

经过千山万水，终于看到曙光了，总结起来就是一句话printf——-&gt;WriteFile();源码面前，了无密码，**现在最关心的是这个WriteFile()写入的文件到底是个什么神仙文件？**



## 3、分析部分之内核调试分析——写

```
根据最后一幅图的os_handle这个数据可知，句柄值为0x0C，现在来看下这个句柄到底是个啥。借助Procexp.exe工具，如下：
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01274af3f020cc750c.png)

光看这名字就不想普通的文件，如果是普通的文件的话，应该是有磁盘路径的，这显然是内核驱动创建的一个设备对象，那这玩意到底是啥呢？这才是今天的重点，且往下看；这时我们需要双机调试了，这玩意在内核里；把这程序拷贝到虚拟机，运行，然后用Windbg查数据；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019726828f6292ffcf.png)

查看下该对象的具体信息，如下所示：

```
1: kd&gt; !object 0xFFFFCC8BDCEA4EF0
Object: ffffcc8bdcea4ef0  Type: (ffffcc8bd88cdb20) File
    ObjectHeader: ffffcc8bdcea4ec0 (new version)
    HandleCount: 2  PointerCount: 64696
    Directory Object: 00000000  Name: \Output `{`ConDrv`}`
1: kd&gt; dt _OBJECT_HEADER ffffcc8bdcea4ec0
nt!_OBJECT_HEADER
   +0x000 PointerCount     : 0n64696
   +0x008 HandleCount      : 0n2
   +0x008 NextToFree       : 0x00000000`00000002 Void
   +0x010 Lock             : _EX_PUSH_LOCK
   +0x018 TypeIndex        : 0x50 'P'
   +0x019 TraceFlags       : 0 ''
   +0x019 DbgRefTrace      : 0y0
   +0x019 DbgTracePermanent : 0y0
   +0x01a InfoMask         : 0x4c 'L'
   +0x01b Flags            : 0 ''
   +0x01b NewObject        : 0y0
   +0x01b KernelObject     : 0y0
   +0x01b KernelOnlyAccess : 0y0
   +0x01b ExclusiveObject  : 0y0
   +0x01b PermanentObject  : 0y0
   +0x01b DefaultSecurityQuota : 0y0
   +0x01b SingleHandleEntry : 0y0
   +0x01b DeletedInline    : 0y0
   +0x01c Reserved         : 0xffffb68d
   +0x020 ObjectCreateInfo : 0xffffcc8b`db7aed80 _OBJECT_CREATE_INFORMATION
   +0x020 QuotaBlockCharged : 0xffffcc8b`db7aed80 Void
   +0x028 SecurityDescriptor : (null)
   +0x030 Body             : _QUAD

```

里边的很多字段暂时不用管，后边会专门撰文写Windows内核里对象管理的实现原理，但有一个信息是值得我们关注的，就是这个对象的类型是File，即文件；简单说明下，在Windows内核里，对象都是有类型的，就像应用层一样，每个对象都有其所对应的类类型，进程的对象类型为Process，线程的对象类型为Thread，等等，自然的文件对象的类型即为File了；那下边具体看下这个文件有什么特别的，且看下边的操作：

```
1: kd&gt; dt _FILE_OBJECT ffffcc8bdcea4ef0
nt!_FILE_OBJECT
   +0x000 Type             : 0n5
   +0x002 Size             : 0n216
   +0x008 DeviceObject     : 0xffffcc8b`dbee7b20 _DEVICE_OBJECT
   +0x010 Vpb              : (null)
   +0x018 FsContext        : 0xffffb68d`59de5b30 Void
   +0x020 FsContext2       : 0xffffcc8b`dacca230 Void
   +0x028 SectionObjectPointer : (null)
   +0x030 PrivateCacheMap  : (null)
   +0x038 FinalStatus      : 0n0
   +0x040 RelatedFileObject : 0xffffcc8b`dd122550 _FILE_OBJECT
   +0x048 LockOperation    : 0 ''
   +0x049 DeletePending    : 0 ''
   +0x04a ReadAccess       : 0 ''
   +0x04b WriteAccess      : 0 ''
   +0x04c DeleteAccess     : 0 ''
   +0x04d SharedRead       : 0 ''
   +0x04e SharedWrite      : 0 ''
   +0x04f SharedDelete     : 0 ''
   +0x050 Flags            : 0x10040002
   +0x058 FileName         : _UNICODE_STRING "\Output"
   +0x068 CurrentByteOffset : _LARGE_INTEGER 0x0
   +0x070 Waiters          : 0
   +0x074 Busy             : 0
   +0x078 LastLock         : (null)
   +0x080 Lock             : _KEVENT
   +0x098 Event            : _KEVENT
   +0x0b0 CompletionContext : (null)
   +0x0b8 IrpListLock      : 0
   +0x0c0 IrpList          : _LIST_ENTRY [ 0xffffcc8b`dcea4fb0 - 0xffffcc8b`dcea4fb0 ]
   +0x0d0 FileObjectExtension : (null)
```

确实挺特殊的，绝大部分字段都没有数据；但与该文件相关联的设备对象值得我们去探究下，如下：

```
1: kd&gt; dt 0xffffcc8b`dbee7b20 _DEVICE_OBJECT
nt!_DEVICE_OBJECT
   +0x000 Type             : 0n3
   +0x002 Size             : 0x150
   +0x004 ReferenceCount   : 0n10
   +0x008 DriverObject     : 0xffffcc8b`dc4fa200 _DRIVER_OBJECT
   +0x010 NextDevice       : (null)
   +0x018 AttachedDevice   : (null)
   +0x020 CurrentIrp       : (null)
   +0x028 Timer            : (null)
   +0x030 Flags            : 0x50
   +0x034 Characteristics  : 0x20000
   +0x038 Vpb              : (null)
   +0x040 DeviceExtension  : (null)
   +0x048 DeviceType       : 0x50
   +0x04c StackSize        : 2 ''
   +0x050 Queue            : &lt;unnamed-tag&gt;
   +0x098 AlignmentRequirement : 0
   +0x0a0 DeviceQueue      : _KDEVICE_QUEUE
   +0x0c8 Dpc              : _KDPC
   +0x108 ActiveThreadCount : 0
   +0x110 SecurityDescriptor : 0xffffb68d`575f0380 Void
   +0x118 DeviceLock       : _KEVENT
   +0x130 SectorSize       : 0
   +0x132 Spare1           : 0
   +0x138 DeviceObjectExtension : 0xffffcc8b`dbee7c70 _DEVOBJ_EXTENSION
   +0x140 Reserved         : (null)
```

设备对象在Windows内核里即可以表征一个实实在在的硬件设备，也可以是虚拟出来的一个假的设备，这就是Windows内核分层设计的妙处所在，好了设备仅仅是指代硬件，而该硬件具有哪些功能，则是由其关联的驱动对象所表征的，下边我们再看下其关联的驱动对象：

```
1: kd&gt; dt 0xffffcc8b`dc4fa200 _DRIVER_OBJECT
nt!_DRIVER_OBJECT
   +0x000 Type             : 0n4
   +0x002 Size             : 0n336
   +0x008 DeviceObject     : 0xffffcc8b`dbee7b20 _DEVICE_OBJECT
   +0x010 Flags            : 0x12
   +0x018 DriverStart      : 0xfffff802`14530000 Void
   +0x020 DriverSize       : 0x12000
   +0x028 DriverSection    : 0xffffcc8b`dc472cf0 Void
   +0x030 DriverExtension  : 0xffffcc8b`dc4fa350 _DRIVER_EXTENSION
   +0x038 DriverName       : _UNICODE_STRING "\Driver\condrv"
   +0x048 HardwareDatabase : 0xfffff802`151f4e38 _UNICODE_STRING "\REGISTRY\MACHINE\HARDWARE\DESCRIPTION\SYSTEM"
   +0x050 FastIoDispatch   : 0xfffff802`14534020 _FAST_IO_DISPATCH
   +0x058 DriverInit       : 0xfffff802`1453e010     long  +fffff8021453e010
   +0x060 DriverStartIo    : (null)
   +0x068 DriverUnload     : 0xfffff802`1453c8e0     void  +fffff8021453c8e0
   +0x070 MajorFunction    : [28] 0xfffff802`14537e10     long  +fffff80214537e10
```

该驱动对象的名字叫”\Driver\condrv”，跟之前的设备对象的名字还挺呼应的；对于驱动对象来说，最重要的要说MajorFunction数组里放着的那些个例程了；我们来看下这些历程中比较重要的一个

[![](https://p5.ssl.qhimg.com/t013f0cdb1efb08f968.png)](https://p5.ssl.qhimg.com/t013f0cdb1efb08f968.png)

回调例程的函数原型如下：

```
typedef NTSTATUS DRIVER_DISPATCH (__in struct _DEVICE_OBJECT *DeviceObject, __inout struct _IRP *Irp);
```

下一个断点看看，命中之后能获取哪些有用的信息；

```
1: kd&gt; bp 0xfffff802145382a0
1: kd&gt; g
1: kd&gt; k
# Child-SP          RetAddr           Call Site
00 ffffcb80`4ec07808 fffff802`14a428d9 0xfffff802`145382a0
01 ffffcb80`4ec07810 fffff802`14ed755e nt!IofCallDriver+0x59
02 ffffcb80`4ec07850 fffff802`14ed8ca0 nt!IopSynchronousServiceTail+0x19e
03 ffffcb80`4ec07900 fffff802`14b79553 nt!NtWriteFile+0x8b0
04 ffffcb80`4ec07a10 00000000`6e5e1e5c nt!KiSystemServiceCopyEnd+0x13
05 00000000`00aeead8 00000000`6e5e1b3a 0x6e5e1e5c
06 00000000`00aeeae0 00000023`774de7bc 0x6e5e1b3a
07 00000000`00aeeae8 00000000`6e580023 0x00000023`774de7bc
08 00000000`00aeeaf0 00000000`00000000 0x6e580023
```

断下来了，也确实看到nt!NtWriteFile了，但这个是内核态的并不是用户态的，我这里pdb路径没有设，设置正确的话，栈是完美的，不过这不影响我们的分析过程；要想直接看nt!NtWriteFile的参数比较麻烦，因为x64架构下的内核是通过寄存器传递参数的，这样需要手动去分析参数，比较麻烦，不过没关系，数据还在，回头看下回调函数的例程原型，第二个参数为IRP*，这个里边有我们想要的东西；来看下：

```
1: kd&gt; !irp ffffcc8bdc6addc0
Irp is active with 2 stacks 2 is current (= 0xffffcc8bdc6aded8)
Mdl=ffffcc8bdd351330: No System Buffer: Thread ffffcc8bd9c4f2c0:  Irp stack trace.  
     cmd  flg cl Device   File     Completion-Context
[N/A(0), N/A(0)]
            0  0 00000000 00000000 00000000-00000000    
            Args: 00000000 00000000 00000000 00000000
&gt;[IRP_MJ_WRITE(4), N/A(0)]
            0  0 ffffcc8bdbee7b20 ffffcc8bdcea4ef0 00000000-00000000    
           \Driver\condrv
            Args: 0000000d 00000000 00000000 00000000
```

重点关注其中的Mdl=ffffcc8bdd351330这行，来继续追踪下数据，这里稍微拓展下，MDL的全称是Memory Descriptor List，即内存 描述链表，是内核里常用来维护缓冲区内存用的一种结构，是个单项链表，借此我们正好来看下数据：

```
1: kd&gt; dt _mdl ffffcc8bdd351330
nt!_MDL
   +0x000 Next             : (null)
   +0x008 Size             : 0n56
   +0x00a MdlFlags         : 0n266
   +0x00c AllocationProcessorNumber : 1
   +0x00e Reserved         : 0
   +0x010 Process          : 0xffffcc8b`dacf9200 _EPROCESS
   +0x018 MappedSystemVa   : 0xffff9401`ce12f940 Void
   +0x020 StartVa          : 0x00000000`00bee000 Void
   +0x028 ByteCount        : 0xd
   +0x02c ByteOffset       : 0x3a4

```

各个字段的解释如下：

Next： 指向下一个MDL结构，从而构成链表，有时一个IRP会包含多个MDL；<br>
Size： MDL本身的大小，注意包含了定长部分和变长两部分的size；<br>
MdlFlags：属性标记，如所描述的物理页有没有被lock住等；<br>
Process： 顾名思义，指向该包含该虚拟地址的地址空间的对应进程结构；<br>
MappedSystemVa：内核态空间中的对应地址；<br>
StartVa： 用户或者内核地址空间中的虚拟地址，取决于在哪allocate的，该值是页对齐的；<br>
ByteCount：MDL所描述的虚拟地址段的大小，byte为单位；<br>
ByteOffset：起始地址的页内偏移，因为MDL所描述的地址段不一定是页对齐的；<br>
MdlFlags标志取值如下图，而这里的取值是0n266=0x10a；

参照下图可知，内核虚拟地址空间还没有分配，没关系，先看下用户态的数据是啥，先弥补下前边查看nt!NtWriteFile不方便而导致的没能查看数据的不快；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0144ae9f3fd473807e.png)

```
1: kd&gt; db 0x00000000`00bee000+0x3a4 ld
00000000`00bee3a4  68 65 6c 6c 6f 20 77 6f-72 6c 64 0d 0a           hello world..
```

正好是我们printf输出的字符串，“hello world\n”,到目前为止一切还在掌控中；那内核总会不一直不分配内核空间吧，因为只要进程切换了，CR3就换了，页表就换了，用户态的数据就有可能访问不到了，所以下一步我们就看下内核合适给MDL.MappedSystemVa 字段挂上数据；指向合适的内核内存空间；方法如下：

```
1: kd&gt; ba r8 ffffcc8bdd351330+18
1: kd&gt; g
Breakpoint 1 hit
nt!MmMapLockedPagesSpecifyCache+0x16a:
fffff802`14a58fea 83e601          and     esi,1
1: kd&gt; dt _mdl ffffcc8bdd351330
nt!_MDL
   +0x000 Next             : (null)
   +0x008 Size             : 0n56
   +0x00a MdlFlags         : 0n267
   +0x00c AllocationProcessorNumber : 1
   +0x00e Reserved         : 0
   +0x010 Process          : 0xffffcc8b`dacf9200 _EPROCESS
   +0x018 MappedSystemVa   : 0xffff9401`cea433a4 Void
   +0x020 StartVa          : 0x00000000`00bee000 Void
   +0x028 ByteCount        : 0xd
   +0x02c ByteOffset       : 0x3a4
```

数据设置好了，除了MappedSystemVa 字段被安排了合适的值，MdlFlags 字段也发生了改变；即多了项MDL_MAPPED_TO_SYSTEM_VA；赶紧来看下数据对不对：

```
1: kd&gt; db 0xffff9401`cea433a4
ffff9401`cea433a4  68 65 6c 6c 6f 20 77 6f-72 6c 64 0d 0a ea be 00  hello world.....
ffff9401`cea433b4  c0 ea be 00 50 00 00 00-d4 e3 be 00 cc 30 11 03  ....P........0..
```

顺便提一下，大家看下下图，最后一级的pfn居然一样，奇不奇怪？一点都不奇怪，本来就是两个虚拟地址映射到同一份物理页：

[![](https://p5.ssl.qhimg.com/t01c0ab3db9432f8d44.png)](https://p5.ssl.qhimg.com/t01c0ab3db9432f8d44.png)

OK了，到目前为止，我们知道了printf———&gt;WriteFile——-&gt;NtWriteFile———&gt;DriverObject.Write例程；下边我们需要知道，谁来读取这个数据呢？



## 4、分析部分之内核调试分析——读

```
接着上边的，在MappedSystemVa所指向的虚拟内存地址设置一个访问断点，看看谁来处理该数据的，如下：
```

```
1: kd&gt; ba r4 0xffff9401`cea433a4
1: kd&gt; g
Breakpoint 2 hit
fffff802`14531424 48ffc9          dec     rcx
1: kd&gt; kb
# RetAddr           : Args to Child                                                           : Call Site
00 fffff802`1453991d : 00000000`00000000 fffff802`14aac8e9 ffffcc8b`00000000 ffffcb80`4ec076f8 : 0xfffff802`14531424
01 00000000`00000000 : fffff802`14aac8e9 ffffcc8b`00000000 ffffcb80`4ec076f8 ffffb68d`6aa157c0 : 0xfffff802`1453991d
```

栈不完美，没关系，我们来看看当前的进程是哪个。要查看当前的进程是哪个，方法有很多，下边就给出两种方法，看官自取：

方法1：

```
1: kd&gt; dt _EPROCESS @$proc -yn ImageF
nt!_EPROCESS
   +0x448 ImageFilePointer : 0xffffcc8b`dea4ad10 _FILE_OBJECT
   +0x450 ImageFileName : [15]  "work.exe"
```

方法2：

```
1: kd&gt; !pcr
KPCR for Processor 1 at ffff9401cdcc0000:
    Major 1 Minor 1
    NtTib.ExceptionList: ffff9401cdcd0fb0
        NtTib.StackBase: ffff9401cdccf000
       NtTib.StackLimit: 0000000000aeead8
     NtTib.SubSystemTib: ffff9401cdcc0000
          NtTib.Version: 00000000cdcc0180
      NtTib.UserPointer: ffff9401cdcc0870
          NtTib.SelfTib: 0000000000cac000
                SelfPcr: 0000000000000000
                   Prcb: ffff9401cdcc0180
                   Irql: 0000000000000000
                    IRR: 0000000000000000
                    IDR: 0000000000000000
          InterruptMode: 0000000000000000
                    IDT: 0000000000000000
                    GDT: 0000000000000000
                    TSS: 0000000000000000
          CurrentThread: ffffcc8bd9c4f2c0
             NextThread: ffffcc8bdb76d380
             IdleThread: ffff9401cdcccb40
              DpcQueue: Unable to read nt!_KDPC_DATA.DpcListHead.Flink @ ffff9401cdcc2f80

1: kd&gt; !thread ffffcc8bd9c4f2c0
THREAD ffffcc8bd9c4f2c0  Cid 2744.1ea8  Teb: 0000000000cac000 Win32Thread: 0000000000000000 RUNNING on processor 1
IRP List:
    ffffcc8bdc6addc0: (0006,0238) Flags: 00060a00  Mdl: ffffcc8bdd351330
Not impersonating
DeviceMap                 ffffb68d596246e0
Owning Process            ffffcc8bdacf9200       Image:         work.exe
Attached Process          N/A            Image:         N/A
Wait Start TickCount      146715         Ticks: 3 (0:00:00:00.046)
Context Switch Count      1518           IdealProcessor: 1             
UserTime                  00:00:00.046
KernelTime                00:00:00.640
Win32 Start Address work!ILT+110(_wmainCRTStartup) (0x0000000000841073)
Stack Init ffffcb804ec07c10 Current ffffcb804ec069a0
Base ffffcb804ec08000 Limit ffffcb804ec01000 Call 0000000000000000
Priority 8 BasePriority 8 PriorityDecrement 0 IoPriority 2 PagePriority 5
Child-SP          RetAddr           : Args to Child                                                           : Call Site
ffffcb80`4ec07698 fffff802`1453991d : 00000000`00000000 fffff802`14aac8e9 ffffcc8b`00000000 ffffcb80`4ec076f8 : 0xfffff802`14531424
ffffcb80`4ec076a0 00000000`00000000 : fffff802`14aac8e9 ffffcc8b`00000000 ffffcb80`4ec076f8 ffffb68d`6aa157c0 : 0xfffff802`1453991d
```

嗯，还是work.exe自己，看看是不是复制之类的操作；看汇编下附近的代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ef329a4fc89ae87a.png)

```
1: kd&gt; ?rdx+rcx-1
Evaluate expression: -118739493964889 = ffff9401`cea433a7
1: kd&gt; db ffff9401`cea433a7
ffff9401`cea433a7  6c 6f 20 77 6f 72 6c 64-0d 0a ea be 00 c0 ea be  lo world........
1: kd&gt; db rcx
ffff9401`cea44d54  6f 20 77 6f 72 6c 64 0d-0a 00 00 00 9c eb be 00  o world.........
```

确实是在复制字符串，这个不管，多几次g，断下来之后，看下进程名，调整断点如下：

```
1: kd&gt; ba r4 0xffff9401`cdf953a4 "dt @$proc _EPROCESS -yn Image"
```

多执行机制g命令之后，如下图所示，出现了另一个进程也来读取这个数据：

[![](https://p1.ssl.qhimg.com/t0112f9576a20aa15d7.png)](https://p1.ssl.qhimg.com/t0112f9576a20aa15d7.png)

简单看下这个进程当前的线程信息，如下：

[![](https://p4.ssl.qhimg.com/t01b8746857616ffd48.png)](https://p4.ssl.qhimg.com/t01b8746857616ffd48.png)

可以知道的信息有线程的ID，线程的Teb信息，有了这些，直接用用户态调试器直接调试即可，但已经用到了内核调试器，那就简单看下当前的线程在干啥吧，看下他的用户态栈；大致浏览下信息，看看有没有什么特别的API调用；

[![](https://p2.ssl.qhimg.com/t01a9de68a062ae6184.png)](https://p2.ssl.qhimg.com/t01a9de68a062ae6184.png)

好，接下来转战用户态调试器；如果大家对内核调试熟悉的话，完全可以直接用内核态调试器直接调试用户态程序，也没多麻烦；



## 5、分析部分之用户态conhost.exe进程行为分析

先来看下DeviceIoControl()函数原型：

```
BOOL DeviceIoControl(
  HANDLE       hDevice,
  DWORD        dwIoControlCode,
  LPVOID       lpInBuffer,
  DWORD        nInBufferSize,
  LPVOID       lpOutBuffer,
  DWORD        nOutBufferSize,
  LPDWORD      lpBytesReturned,
  LPOVERLAPPED lpOverlapped
);

参数解释请见https://docs.microsoft.com/zh-cn/windows/win32/api/ioapiset/nf-ioapiset-deviceiocontrol
```

[![](https://p4.ssl.qhimg.com/t01d094a8abd63b888e.png)](https://p4.ssl.qhimg.com/t01d094a8abd63b888e.png)

x64下，函数参数传递前4个参数是通过cd89寄存器传递的，剩余的通过栈传递，下边来找一下这几个参数：

[![](https://p2.ssl.qhimg.com/t01f02f0ceb8f57c346.png)](https://p2.ssl.qhimg.com/t01f02f0ceb8f57c346.png)

下边来简单看下传输的缓冲区数据，看不出啥，这个需要去逆向分析通信协议了，不是我们关注的重点，那就让这个函数执行完，我们看看输出的内容吧：

```
0:000&gt; dd 000000cbe9a7fcd0
000000cb`e9a7fcd0  011c5524 00000000 00000000 00000000
000000cb`e9a7fce0  00000000 00000000 e9a7fd58 000000cb
000000cb`e9a7fcf0  00000004 00000000

```

[![](https://p3.ssl.qhimg.com/t013af70441e129aa23.png)](https://p3.ssl.qhimg.com/t013af70441e129aa23.png)<br>
原来conhost.exe是通过这个DeviceIoControl()API通过500006这个控制码跟驱动要的数据；<br>
至此整够过程全部分析完毕；



## 6、总结

本文从printf的源码层层深入分析，到驱动的调试逆向分析，再到conhost.exe进程的数据获取过程的详细分析；本文涉及到的知识点比较多；总结起来有以下几点：

1、printf源码的调试跟踪，如何定位观点点；<br>
2、内核对象管理，设备对象，驱动对象及主要的例程；<br>
3、MDL；<br>
4、内核调试；<br>
5、用户态调试；<br>
6、用户态程序通过DeviceIoControl()与内核驱动交互，获取特定数据；<br>
7、printf实现的多进程架构；涉及的内容比较多，希望读者花点时间好<br>
6、用户态程序通过DeviceIoControl()与内核驱动交互，获取特定数据；<br>
7、printf实现的多进程架构；

好整理总结；
