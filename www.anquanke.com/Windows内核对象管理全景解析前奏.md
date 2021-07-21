> 原文链接: https://www.anquanke.com//post/id/219839 


# Windows内核对象管理全景解析前奏


                                阅读量   
                                **157238**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01a07625d9571da527.jpg)](https://p5.ssl.qhimg.com/t01a07625d9571da527.jpg)



## 0、引言

学习过Windows内核的或者从事过内核安全开发再或者从事过驱动开发的同事，必然都遇到过或者听说过这样一个概念——“内核对象管理”，然而对于这个问题，潘爱民老师的那本《Windows内核原理与实现》对齐提及甚少，但毛德操老师的《Windows内核情景分析》又不是基于Windows的源码进行分析的。对于这个问题，我曾深入研究分析过，处理通常的理论说教外，更多的是在Windbg调试器中带着大家亲自走一遍分析的过程，知其然又知其所以然。学完会发现Windows内核实现了一个小型的类似文件系统的结构来管理内核对象。

涉及到的知识：

1、Windows内核对象；<br>
2、Windows内核对象管理；<br>
3、Windbg内核调试；<br>
4、Windbg的常规使用；



## 1、内核对象简介

首先大家别被这个名字唬住了，内核对象=内核+对象；先解释“对象”这个名字，这个与CPP中的类的实例是一个道理，即类的实例化便是一个到底，再往底层了说就是按照类这个模板，为其分配一块内存，并作相应的初始化，就这么简单，可别忘了，操作系统也是用代码写成的，只不过不同于CPP中的类，而是用的C中的结构体。在一个概念就是“内核”，可别被这玩意整蒙了，这里所谓的内核无非就是跑在系统空间里的实例对象，即对象的内存地址分配在系统空间中的对象即为内核对象。好了，名字的事情搞明白了，下边接着分析。



## 2、内核对象的构成

我们都知道，像CPP，JAVA，C#等等，这类面向对象的编程语言有一个很重要的特性就是“继承”。所谓的继承一句话总结下就是：拿来主义，子承父业。无非是实现代码复用，而这种复用的语法很 简单，就是通过”继承”来实现了，简化了复用的整个过程。除了复用之外，还有一个好处便是能够实现多态，通过基类指针就能够访问子类中该写过的虚函数，这种基于同一个接口实现不同功能的方式便是多态的核心了。通过一套统一的接口就能够达到统一管理的目的，不得不说，CPP的成功本质是编程思想的成功。然而C语言中，没有继承这个概念，那么多态啥的就跟他没一丁点关系了。难道伟大的C语言真就被这么个小玩意难住了吗？显然没有，诺，这里的内核对象管理就另辟蹊径，把C玩出了CPP的味道，不得不说，C就是这么伟大。微软的解决方案是：

对象头+对象体<br>
对象头便是相当于CPP中的基类，负责管理一些简单的，所有对象共有的属性；诸如进程对象头，线程对象头，文件对象头，调试对象头等等；<br>
对象体相当于CPP中的继承的子类，代表着具体的某个对象；诸如进程对象，线程对象，文件对象，调试对象等等；<br>
具体的内存布局如下图所示：

[![](https://p5.ssl.qhimg.com/t01be99d24674d59de1.png)](https://p5.ssl.qhimg.com/t01be99d24674d59de1.png)

但别觉得对象头就很简单，类似于CPP中的一个类中有很多字段属性一样，Windows内核中实现的对象头又是有很多个不同的组成部分组成的，这些独立的组成部分是否存在则由一个总的字段来进行管理的，具体的简化图如下图所示：

[![](https://p5.ssl.qhimg.com/t0121ed5bc5265048cb.png)](https://p5.ssl.qhimg.com/t0121ed5bc5265048cb.png)



## 3、Windows内核对象头的内存结构

这里以Win7为例来讲解下Windows内核中具体的实现，第一个结构体当然是nt!_OBJECT_HEADER，具体实现如下图：

[![](https://p0.ssl.qhimg.com/t013783d890c57209a5.png)](https://p0.ssl.qhimg.com/t013783d890c57209a5.png)

字段稍微解释下：

```
+0x000 PointerCount     : 以指针访问该对象的次数，内核里诸如ObReferenceObjectByHandle()函数根据句柄访问该对象时,会加1操作此字段
   +0x004 HandleCount      : 以句柄访问该对象的次数
   +0x004 NextToFree       : 对象管理相关，用于记录链表中下一个空闲状态的对象，可忽略之
   +0x008 Lock             : 推锁，用于同步访问当前该对象
   +0x00c TypeIndex        : 该对象的索引号，此索引号是对象类型对象的数组索引号，后边会讲解
   +0x00d TraceFlags       : UChar
   +0x00e InfoMask         : 用以记录该对象头其他部分，即补充的对象头有哪些
   +0x00f Flags            : 一些标志位
   +0x010 ObjectCreateInfo : Ptr32 _OBJECT_CREATE_INFORMATION,对象的创建信息
   +0x010 QuotaBlockCharged : Ptr32 Void,对象的配额信息
   +0x014 SecurityDescriptor : Ptr32 Void,对象的安全描述符信息
   +0x018 Body             : _QUAD,对象体,这个是对象相关的部分
```

与我们当前强相关的两个字段是InfoMask和Body。对于InfoMask需要详细的分析下，因为这个字段直接关系在对象头的可变部分到底是怎么定位的。可变对象头在Win7中共分为5类，如下：

```
nt!_OBJECT_HEADER_CREATOR_INFO //对象的创建者信息
nt!_OBJECT_HEADER_NAME_INFO    //对象的名字信息
nt!_OBJECT_HEADER_HANDLE_INFO  //对象的句柄信息
nt!_OBJECT_HEADER_QUOTA_INFO   //对象的配额信息
nt!_OBJECT_HEADER_PROCESS_INFO //对象的进程信息
```

后边我们会来手动找数据对比分析这些结构体的数据。那另一个问题来了，如何确认这些可变对象头存在与否呢？那就是InfoMask的作用了，且看InfoMask的具体bit的含义：

```
#define OB_INFOMASK_CREATOR_INFO  0x01
#define OB_INFOMASK_NAME          0x02
#define OB_INFOMASK_HANDLE        0x04
#define OB_INFOMASK_QUOTA         0x08
#define OB_INFOMASK_PROCESS_INFO  0x10
```

正好对应着每一个可变对象头的结构体，ok，下一个关键问题就是，即使指导某个可变对象头是存在的，那又如何定位到该可变对象头的具体位置呢？这个简单，以nt!_OBJECT_HEADER为基准，往前减去对应可变对象头的偏移就ok，现在整个对象头可以整理如下：

[![](https://p3.ssl.qhimg.com/t01d2251d7e9929d17f.png)](https://p3.ssl.qhimg.com/t01d2251d7e9929d17f.png)



## 4、以进程对象来观察对象头和可变对象头

下边我们以具体的实例来讲解这些字段的具体函数以及其他相关的信息。在系统中运行notepad.exe这个记事本进程，然后产看其具体的对象头信息，如下:

```
2: kd&gt; !process 0 0 notepad.exe
PROCESS a20f4d40  SessionId: 1  Cid: 0f1c    Peb: 7ffdd000  ParentCid: 0524
    DirBase: be6e2540  ObjectTable: 00000000  HandleCount:   0.
    Image: notepad.exe
```

PROCESS这个字段信息表征的就是nt!_OBJECT_HEADER中的Body部分，现在根据他来找到对象头的起始地址，nt!_OBJECT_HEADER.Body的偏移是0x18，那么nt!_OBJECT_HEADER的位置自然就是Body往前倒推0x18了，即:

```
2: kd&gt; ?a20f4d40-0x18
Evaluate expression: -1576055512 = a20f4d28
```

ok，得到了nt!_OBJECT_HEADER在内存中的虚拟地址，下边就开始解析，如下：

[![](https://p2.ssl.qhimg.com/t016e097f96c2ca90e8.png)](https://p2.ssl.qhimg.com/t016e097f96c2ca90e8.png)

由上图可知，InfoMask为0x08，等于OB_INFOMASK_QUOTA，即在之前存在nt!_OBJECT_HEADER_QUOTA_INFO，下边先来看一下nt!_OBJECT_HEADER_QUOTA_INFO这个结构体的大小：

```
2: kd&gt; ??sizeof(nt!_OBJECT_HEADER_QUOTA_INFO)
unsigned int 0x10
```

[![](https://p4.ssl.qhimg.com/t013f8133e050f3dfcf.png)](https://p4.ssl.qhimg.com/t013f8133e050f3dfcf.png)



## 5、nt!_OBJECT_HEADER之PointerCount分析

除此

[![](https://p4.ssl.qhimg.com/t016de62b2aa8578c44.png)](https://p4.ssl.qhimg.com/t016de62b2aa8578c44.png)

之外，我们还能知道，通过PointerCount引用这个对象的次数为1，通过句柄应用这个对象的次数也为1。这两个字段的作用又是什么呢？当然是管理对象的生存周期了，CPP中或者JAVA中，智能指针不就这么干的嘛。下边通过内核代码来分析下，系统是如何使用这个字段的，如下：

[![](https://p2.ssl.qhimg.com/t0188e052c25f176e68.png)](https://p2.ssl.qhimg.com/t0188e052c25f176e68.png)

[![](https://p3.ssl.qhimg.com/t01dc4cbb32b0430bb0.png)](https://p3.ssl.qhimg.com/t01dc4cbb32b0430bb0.png)

由上图可知，ObReferenceObjectByPointerWithTag()内部通过传入的对象的Body地址计算出对象头的内存地址，然后调用InterlockedExchangeAdd()对其进程加1操作，而这个被加1的字段正式_OBJECT_HEADER.PointerCount。类似的，我们再分析下另一个函数，看看是如何减1操作的。

[![](https://p5.ssl.qhimg.com/t012ff480a15aa20b7f.png)](https://p5.ssl.qhimg.com/t012ff480a15aa20b7f.png)

[![](https://p3.ssl.qhimg.com/t0190961ab0aa7608fc.png)](https://p3.ssl.qhimg.com/t0190961ab0aa7608fc.png)



## 6、nt!_OBJECT_HEADER之HandleCount分析

现在分析下HandleCount这个字段，但现在换一个思路，因为很多初学者并不知道系统的哪个函数来读写此字段，或者即使找到了也不知道如何定位到关键的代码点。现在我们用调试的方式来查找读写此处的关键API。随便选一个进程，如下：

```
0: kd&gt; !process WmiPrvSE.exe 0
PROCESS a3f0ed40  SessionId: 0  Cid: 0b70    Peb: 7ffdf000  ParentCid: 02c0
    DirBase: be6e2480  ObjectTable: b3bf0758  HandleCount: 250.
    Image: WmiPrvSE.exe

0: kd&gt; dt nt!_OBJECT_HEADER a3f0ed40-18
   +0x000 PointerCount     : 0n73
   +0x004 HandleCount      : 0n6
   +0x004 NextToFree       : 0x00000006 Void
   +0x008 Lock             : _EX_PUSH_LOCK
   +0x00c TypeIndex        : 0x7 ''
   +0x00d TraceFlags       : 0 ''
   +0x00e InfoMask         : 0x8 ''
   +0x00f Flags            : 0 ''
   +0x010 ObjectCreateInfo : 0x83f74c40 _OBJECT_CREATE_INFORMATION
   +0x010 QuotaBlockCharged : 0x83f74c40 Void
   +0x014 SecurityDescriptor : 0xb3bf415f Void
   +0x018 Body             : _QUAD
```

然后下一个内存写断点：

```
0: kd&gt; ba w4 a3f0ed40-18+4
```

调用栈如下：

```
0: kd&gt; k
# ChildEBP RetAddr  
00 b2e47934 8406278c nt!ObpIncrementHandleCountEx+0x1df
01 b2e479a0 840bafde nt!ObpCreateHandle+0xff
02 b2e47b20 840bb043 nt!ObOpenObjectByPointerWithTag+0xc1
03 b2e47b48 840b8e02 nt!ObOpenObjectByPointer+0x24
04 b2e47cfc 840c155e nt!PsOpenProcess+0x231
05 b2e47d1c 83e8342a nt!NtOpenProcess+0x2d
06 b2e47d1c 76f664f4 nt!KiFastCallEntry+0x12a
07 02a3f680 76f651dc ntdll!KiFastSystemCallRet
08 02a3f684 751291b6 ntdll!NtOpenProcess+0xc
09 02a3f6c0 6ec4ac13 KERNELBASE!OpenProcess+0x49
WARNING: Stack unwind information not available. Following frames may be wrong.
0a 02a3f728 6ec56294 wmiprvsd!DllGetClassObject+0x11159
0b 02a3f750 6ec3071d wmiprvsd!DllGetClassObject+0x1c7da
0c 02a3f7ac 6ec303d8 wmiprvsd!DllCanUnloadNow+0xbd37
0d 02a3f820 6ec301f9 wmiprvsd!DllCanUnloadNow+0xb9f2
0e 02a3f8b4 6ec2ff5e wmiprvsd!DllCanUnloadNow+0xb813
0f 02a3f988 6ec37f68 wmiprvsd!DllCanUnloadNow+0xb578
10 02a3f9f4 6ec2b471 wmiprvsd!DllCanUnloadNow+0x13582
11 02a3fa3c 6ec2b1e0 wmiprvsd!DllCanUnloadNow+0x6a8b
12 02a3fac0 6f1b7502 wmiprvsd!DllCanUnloadNow+0x67fa
13 02a3fb34 6f1b6899 wbemcore!DllCanUnloadNow+0x4399
14 02a3fb80 6f1bceca wbemcore!DllCanUnloadNow+0x3730
15 02a3fbb0 6f1bfd5c wbemcore!DllGetClassObject+0x1d42
16 02a3fcf4 6f1bdf2c wbemcore!DllGetClassObject+0x4bd4
17 02a3fe0c 6f1bdd80 wbemcore!DllGetClassObject+0x2da4
18 02a3fe5c 6f1bfc6e wbemcore!DllGetClassObject+0x2bf8
19 02a3feb4 6f1b37a2 wbemcore!DllGetClassObject+0x4ae6
1a 02a3fee8 6f1b3747 wbemcore!DllCanUnloadNow+0x639
1b 02a3ff34 6f1b2326 wbemcore!DllCanUnloadNow+0x5de
1c 02a3ff6c 6f1b23f4 wbemcore+0x2326
1d 02a3ff84 76d51174 wbemcore+0x23f4
1e 02a3ff90 76f7b3f5 kernel32!BaseThreadInitThunk+0xe
1f 02a3ffd0 76f7b3c8 ntdll!__RtlUserThreadStart+0x70
20 02a3ffe8 00000000 ntdll!_RtlUserThreadStart+0x1b
```

根据调用栈可知，关键的API是nt!ObOpenObjectByPointer，现在来逆向分析下该API，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012ebfa735bdfbb177.png)

[![](https://p2.ssl.qhimg.com/t0156a904a252588898.png)](https://p2.ssl.qhimg.com/t0156a904a252588898.png)

[![](https://p3.ssl.qhimg.com/t01be8294377e97baad.png)](https://p3.ssl.qhimg.com/t01be8294377e97baad.png)

[![](https://p1.ssl.qhimg.com/t01c3725d7f0114ac23.png)](https://p1.ssl.qhimg.com/t01c3725d7f0114ac23.png)

从整个调用链的分析过程可知，是用户态进程调用了KERNELBASE!OpenProcess()，然后引发的一系列的调用操作，从这里也可以推出来，nt!_OBJECT_HEADER.HandleCount这个字段主要用户记录用户态通过句柄访问该对象的次数。当然，对齐做的减1操作的分析过程就留给大家了。



## 7、内核对象类型对象分析

大家读到这个词可能有点拗口，啥意思呢。这个句子可以这么断开来，内核对象 类型 对象，即内核对象的类型也是个对象，我们现在对这个类型对象进行分析。玩过Python的人都知道一句话，Python中一切皆对象，其实Windows中又何尝不是呢。此外，Python的内核实现与我们这边分析的Windows内核对象管理的相似度99.999%，这个有机会后边给大家对比分析下两者实现的源码。扯远了，现在回来看一下这个类型对象所谓何物。nt!_OBJECT_HEADER.TypeIndex这个字段代表着当前的这个对象再对象类型数组中的索引号，那么这个数组的起始地址在哪呢？类型对象自身的类型又是什么呢？下边一一来回答这两个问题。<br>
第一个问题：这个数组的起始地址为nt!ObpObjectTypes；<br>
第二个问题：类型对象的结构体为dt nt!_OBJECT_TYPE；

我们先来分析下dt nt!_OBJECT_TYPE，如下：

```
0: kd&gt; dt nt!_OBJECT_TYPE
   +0x000 TypeList         : _LIST_ENTRY            //隶属于同一个类型对象的实例
   +0x008 Name             : _UNICODE_STRING        //该对象的名字
   +0x010 DefaultObject    : Ptr32 Void
   +0x014 Index            : UChar                  //该对象在对象类型对象数组中的索引号
   +0x018 TotalNumberOfObjects : Uint4B             //以指针形式引用该对象的次数
   +0x01c TotalNumberOfHandles : Uint4B             //以句柄形式应用该对象的次数
   +0x020 HighWaterNumberOfObjects : Uint4B         //用于记录以指针形式引用该对象的最高次数，该字段一般用于统计，性能优化
   +0x024 HighWaterNumberOfHandles : Uint4B         //用于记录以句柄形式应用该对象的最高次数，该字段一般用于统计，性能优化
   +0x028 TypeInfo         : _OBJECT_TYPE_INITIALIZER // 具体的对象类型初始化字段
   +0x078 TypeLock         : _EX_PUSH_LOCK          // 互斥访问锁
   +0x07c Key              : Uint4B
   +0x080 CallbackList     : _LIST_ENTRY

0: kd&gt; dt nt!_OBJECT_TYPE_INITIALIZER
   +0x000 Length           : Uint2B
   +0x002 ObjectTypeFlags  : UChar
   +0x002 CaseInsensitive  : Pos 0, 1 Bit
   +0x002 UnnamedObjectsOnly : Pos 1, 1 Bit
   +0x002 UseDefaultObject : Pos 2, 1 Bit
   +0x002 SecurityRequired : Pos 3, 1 Bit
   +0x002 MaintainHandleCount : Pos 4, 1 Bit
   +0x002 MaintainTypeList : Pos 5, 1 Bit
   +0x002 SupportsObjectCallbacks : Pos 6, 1 Bit
   +0x004 ObjectTypeCode   : Uint4B
   +0x008 InvalidAttributes : Uint4B
   +0x00c GenericMapping   : _GENERIC_MAPPING
   +0x01c ValidAccessMask  : Uint4B
   +0x020 RetainAccess     : Uint4B
   +0x024 PoolType         : _POOL_TYPE
   +0x028 DefaultPagedPoolCharge : Uint4B
   +0x02c DefaultNonPagedPoolCharge : Uint4B
   +0x030 DumpProcedure    : Ptr32     void
   +0x034 OpenProcedure    : Ptr32     long
   +0x038 CloseProcedure   : Ptr32     void
   +0x03c DeleteProcedure  : Ptr32     void
   +0x040 ParseProcedure   : Ptr32     long
   +0x044 SecurityProcedure : Ptr32     long
   +0x048 QueryNameProcedure : Ptr32     long
   +0x04c OkayToCloseProcedure : Ptr32     unsigned char
```

nt!_OBJECT_TYPE_INITIALIZER结构体主要是存储一些属性信息，特别是一些权限校验和默认的函数过程。特别有意思的是SupportsObjectCallbacks字段，修改该字段可以绕过系统提供的安全保护措施。现在来看下这个系统全局的对象类型对象数组，如下：

```
0: kd&gt; dd nt!ObpObjectTypes
83f81aa0  a19378e0 a1937818 a1937750 a1937508
83f81ab0  a19c2040 a19c2f78 a19c2eb0 a19c2de8
83f81ac0  a19c2d20 a19c2668 a19e2330 a19ea418
83f81ad0  a19ea350 a19e9418 a19e9350 a19e89b8
83f81ae0  a19e88f0 a19e8828 a19e8760 a19e8698
83f81af0  a19e85d0 a19e8508 a19e8440 a19e8378
83f81b00  a19e7040 a19e7f78 a19e7eb0 a19e7160
83f81b10  a19f3f78 a19f3eb0 a19f3de8 a19f3930
```

notepad进程对象的TypeIndex为0x07，那么是否意味着是nt!ObpObjectTypes[7]呢？假设是的话，我们来看下数据：

[![](https://p0.ssl.qhimg.com/t01e4d4a17260218bee.png)](https://p0.ssl.qhimg.com/t01e4d4a17260218bee.png)

[![](https://p2.ssl.qhimg.com/t01fc7c0517a0de9e49.png)](https://p2.ssl.qhimg.com/t01fc7c0517a0de9e49.png)

显然是有问题的，因为我们看的这个明明是notepad这个进程对象，但这里的名字却是“UserApcReserve”，如果这个还不足以打消你的疑虑，那TotalNumberOfObjects和TotalNumberOfHandles总归最好的证明了吧。既然TypeIndex不是这么简单的映射到nt!ObpObjectTypes数组的下标，那么这里的映射关系又是怎样的呢？最好的办法当然是去内核中寻找答案。



## 8、TypeIndex与nt!ObpObjectTypes数组的映射关系

与这个索引映射关系最为直接的是ObCreateObjectTypeEx()函数，该函数的关键代码整理如下：

[![](https://p2.ssl.qhimg.com/t01daf49987878949f0.png)](https://p2.ssl.qhimg.com/t01daf49987878949f0.png)

[![](https://p1.ssl.qhimg.com/t01da206a3054d875bb.png)](https://p1.ssl.qhimg.com/t01da206a3054d875bb.png)

[![](https://p1.ssl.qhimg.com/t01e129550d1d4e629e.png)](https://p1.ssl.qhimg.com/t01e129550d1d4e629e.png)

由此可见，nt!_OBJECT_TYPE.Index这个是从2开始的，且2一定是分配给ObpTypeObjectType的，好的，现在来查看下是不是我们分析的这个结果。

```
0: kd&gt; dd nt!ObpTypeObjectType l1
83f81a94  a19378e0
0: kd&gt; dt nt!_OBJECT_TYPE a19378e0
   +0x000 TypeList         : _LIST_ENTRY [ 0xa19378b8 - 0xa240b610 ]
   +0x008 Name             : _UNICODE_STRING "Type"
   +0x010 DefaultObject    : 0x83f81ba0 Void
   +0x014 Index            : 0x2 ''
   +0x018 TotalNumberOfObjects : 0x2a
   +0x01c TotalNumberOfHandles : 0
   +0x020 HighWaterNumberOfObjects : 0x2a
   +0x024 HighWaterNumberOfHandles : 0
   +0x028 TypeInfo         : _OBJECT_TYPE_INITIALIZER
   +0x078 TypeLock         : _EX_PUSH_LOCK
   +0x07c Key              : 0x546a624f
   +0x080 CallbackList     : _LIST_ENTRY [ 0xa1937960 - 0xa1937960 ]
```

再看看nt!ObpObjectTypes数组的第一项也正是a19378e0<br>
OK，验证正确，现在就看下我们所需要核验的notepad进程的类型对象。7-2=5，所以我们就应该分析nt!ObpObjectTypesp[5]，如下：

[![](https://p1.ssl.qhimg.com/t01429fa30cff865cf4.png)](https://p1.ssl.qhimg.com/t01429fa30cff865cf4.png)



## 9、总结

ok，暂且先到这，这篇文章讲述的主要是内核对象的比较细节的知识点，大家需要自己亲自做个实验分析一下，文中是以Win7 32为例分析的，其他版本的Windows内核实现可能有差异，但基本原理是一致的。文章中给大家留的那个分析的作业也希望大家做一下。下一篇将会再这篇的基础上构建出一副完整的内核对象管理全景图，你会发现，Windows其实是实现了一个小型的类似文件系统的东西来管理内核对象的。
