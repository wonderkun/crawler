> 原文链接: https://www.anquanke.com//post/id/86896 


# 【技术分享】Windows内核池喷射的乐趣


                                阅读量   
                                **102990**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：theevilbit.blogspot.com
                                <br>原文地址：[https://theevilbit.blogspot.com/2017/09/pool-spraying-fun-part-1.html](https://theevilbit.blogspot.com/2017/09/pool-spraying-fun-part-1.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01db18f45a7cfed465.jpg)](https://p3.ssl.qhimg.com/t01db18f45a7cfed465.jpg)



译者：[**天鸽**](http://bobao.360.cn/member/contribute?uid=145812086)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言——Windows内核池喷射**

我计划写这一系列文章已经有一年了，我对这些东西做过一些研究，但是常常会忘记，也没有正确地写下笔记。我想探索的是什么样的对象可以用于内核池喷射，主要关注于它们消耗多少空间，它们拥有什么属性，并且到最后写了一段代码，将池孔大小（**pool hole size**）作为输入，然后动态地告诉我们在这里使用什么样的对象能够控制池分配以达到溢出的目的。我思考这一问题已经有段时间了，让我再一次感到兴奋的是当我看到了来自 @steventseeley 的一条推特（[https://twitter.com/steventseeley/status/904443608216031233](https://twitter.com/steventseeley/status/904443608216031233)），我决定把它写出来，另一方面也是我自己的兴趣使然。

微软有一个很棒的内核对象列表，我们可以通过调用用户模式功能来创建内核对象，尽管它不是很完整，但仍然是一个很好的开始：[https://msdn.microsoft.com/library/windows/desktop/ms724485(v=vs.85).aspx](https://msdn.microsoft.com/library/windows/desktop/ms724485%28v=vs.85%29.aspx)

另一个重要的链接，是一个我们能够找到 **pool tag**（译者注：poll tag是调试时用于识别块的字符）的列表，当查看池分配时也是十分方便的：[https://blogs.technet.microsoft.com/yongrhee/2009/06/23/pool-tag-list/](https://blogs.technet.microsoft.com/yongrhee/2009/06/23/pool-tag-list/)

在这篇文章中，我想探讨的是 Mutex 对象，由于笔记不完整它让我很头疼，我会讲到如何找到并查看对象在池空间中的实际分配以及对象本身的一些基本信息。<br>

<br>

**第一部分——环境配置及对象大小**

在设置环境的部分，我们并不需要进行远程内核调试，进行本地内核调试就足够了，因为我们只探索内核内存，目前也就不需要设置任何断点。所以本地调试足以满足我们的需求。为此，我们需要在 Windows 中启用调试：

```
bcdedit -debug ON
```

之后，需要重启机器。一旦完成，我们就可以启动 WinDBG，转到内核调试，然后选择本地调试。我建议使用下面的命令来加载符号：

```
.symfix
.reload
```

此时我们就可以探索内核内存空间了。我将使用 Win7 SP1 x86 进行演示。

首先，如果我们希望获得更全面的对象列表，可以使用下面的命令：



```
!object ObjectTypes
```

我们会得到这样的东西：



```
lkd&gt; !object ObjectTypes
Object: 8be05880  Type: (851466d8) Directory
    ObjectHeader: 8be05868 (new version)
    HandleCount: 0  PointerCount: 44
    Directory Object: 8be05ed0  Name: ObjectTypes
    Hash Address  Type                      Name
    ---- -------  ----                      ----
     00  851d6900 Type                      TpWorkerFactory
         851466d8 Type                      Directory
     01  8521a838 Type                      Mutant
         851cddb0 Type                      Thread
     03  857c7c40 Type                      FilterCommunicationPort
     04  8522a360 Type                      TmTx
     05  851d29c8 Type                      Controller
     06  8521d0b8 Type                      EtwRegistration
     07  851fe9c8 Type                      Profile
         8521a9c8 Type                      Event
         851467a0 Type                      Type
     09  8521cce0 Type                      Section
         8521a900 Type                      EventPair
         85146610 Type                      SymbolicLink
     10  851d69c8 Type                      Desktop
         851cdce8 Type                      UserApcReserve
     11  85221040 Type                      EtwConsumer
         8520e838 Type                      Timer
     12  8522a8f0 Type                      File
         851fe838 Type                      WindowStation
     14  860a6f78 Type                      PcwObject
     15  8521ceb0 Type                      TmEn
     16  851d2838 Type                      Driver
     18  8521db70 Type                      WmiGuid
         851fe900 Type                      KeyedEvent
     19  851d2900 Type                      Device
         851cd040 Type                      Token
     20  85214690 Type                      ALPC Port
         851cd568 Type                      DebugObject
     21  8522a9b8 Type                      IoCompletion
     22  851cde78 Type                      Process
     23  8521cf78 Type                      TmRm
     24  851d6838 Type                      Adapter
     26  852139a8 Type                      PowerRequest
         85218448 Type                      Key
     28  851cdf40 Type                      Job
     30  8521c940 Type                      Session
         8522a428 Type                      TmTm
     31  851cdc20 Type                      IoCompletionReserve
     32  8520e9c8 Type                      Callback
     33  85894328 Type                      FilterConnectionPort
     34  8520e900 Type                      Semaphore
```

这是一个可以在内核空间中分配的对象的列表。我们可以通过查看更多的细节来探索几个关于它们的重要属性。使用命令 dt nt!_OBJECT_TYPE &lt;object&gt; 我们可以得到关于某对象（object）的更多细节，比如句柄总数等。但是最重要的是 _OBJECT_TYPE_INITIALIZER 结构的偏移量，它将给我们带来极大的方便。让我们看看它为我们提供了 Mutant 对象的哪些我想要的信息：



```
lkd&gt; dt nt!_OBJECT_TYPE 8521a838
   +0x000 TypeList         : _LIST_ENTRY [ 0x8521a838 - 0x8521a838 ]
   +0x008 Name             : _UNICODE_STRING "Mutant"
   +0x010 DefaultObject    : (null) 
   +0x014 Index            : 0xe ''
   +0x018 TotalNumberOfObjects : 0x15f
   +0x01c TotalNumberOfHandles : 0x167
   +0x020 HighWaterNumberOfObjects : 0xc4d7
   +0x024 HighWaterNumberOfHandles : 0xc4ed
   +0x028 TypeInfo         : _OBJECT_TYPE_INITIALIZER
   +0x078 TypeLock         : _EX_PUSH_LOCK
   +0x07c Key              : 0x6174754d
   +0x080 CallbackList     : _LIST_ENTRY [ 0x8521a8b8 - 0x8521a8b8 ]
```

然后阅读下 _OBJECT_TYPE_INITIALIZER：



```
lkd&gt; dt nt!_OBJECT_TYPE_INITIALIZER 8521a838+28
   +0x000 Length           : 0x50
   +0x002 ObjectTypeFlags  : 0 ''
   +0x002 CaseInsensitive  : 0y0
   +0x002 UnnamedObjectsOnly : 0y0
   +0x002 UseDefaultObject : 0y0
   +0x002 SecurityRequired : 0y0
   +0x002 MaintainHandleCount : 0y0
   +0x002 MaintainTypeList : 0y0
   +0x002 SupportsObjectCallbacks : 0y0
   +0x002 CacheAligned     : 0y0
   +0x004 ObjectTypeCode   : 2
   +0x008 InvalidAttributes : 0x100
   +0x00c GenericMapping   : _GENERIC_MAPPING
   +0x01c ValidAccessMask  : 0x1f0001
   +0x020 RetainAccess     : 0
   +0x024 PoolType         : 0 ( NonPagedPool )
   +0x028 DefaultPagedPoolCharge : 0
   +0x02c DefaultNonPagedPoolCharge : 0x50
   +0x030 DumpProcedure    : (null) 
   +0x034 OpenProcedure    : (null) 
   +0x038 CloseProcedure   : (null) 
   +0x03c DeleteProcedure  : 0x82afe453     void  nt!ExpDeleteMutant+0
   +0x040 ParseProcedure   : (null) 
   +0x044 SecurityProcedure : 0x82ca2936     long  nt!SeDefaultObjectMethod+0
   +0x048 QueryNameProcedure : (null) 
   +0x04c OkayToCloseProcedure : (null)
```

这里告诉了我们两个重要的事情：

**此对象被分配给的池类型 – 在这里是非分页池（NonPagedPool）**

**功能偏移（这在实际的漏洞利用部分十分重要）**

之后，我们来分配一个 Mutant 对象，然后在内核池中找到它。我写了一段简短的 Python 代码来实现它：



```
from ctypes import *
from ctypes.wintypes import *
import os, sys
kernel32 = windll.kernel32
def alloc_not_named_mutex():
        hHandle = HANDLE(0)
hHandle = kernel32.CreateMutexA(None, False, None)
if hHandle == None:
                print "[-] Error while creating mutex"
  sys.exit()
print hex(hHandle)
if __name__ == '__main__':
        alloc_not_named_mutex()
variable = raw_input('Press any key to exit...')
```

这段代码将为我们分配一个未命名的 mutex，打印出它的句柄并等待退出。我们需要等待着，所以我们可以在 WinDBG 中探索内核池，如果进程退出，则mutex 将被破坏。这里我得到了一个 0x70 的句柄，我们来看看怎样在 WinDBG 中找到它。首先我需要找到 Python 进程并切换上下文，可以这样做：



```
lkd&gt; !process 0 0 python.exe
PROCESS 86e80930  SessionId: 1  Cid: 0240    Peb: 7ffd4000  ParentCid: 0f80
    DirBase: bf3fd2e0  ObjectTable: a8282b30  HandleCount:  41.
    Image: python.exe
lkd&gt; .process 86e80930  
Implicit process is now 86e80930
```

第一条命令将为我们找到进程，第二条命令将切换上下文。然后我们查询句柄，就能得到内存中对象的地址：



```
lkd&gt; !handle 70
PROCESS 86e80930  SessionId: 1  Cid: 0240    Peb: 7ffd4000  ParentCid: 0f80
    DirBase: bf3fd2e0  ObjectTable: a8282b30  HandleCount:  41.
    Image: python.exe
Handle table at a8282b30 with 41 entries in use
0070: Object: 86e031a8  GrantedAccess: 001f0001 Entry: 8c0d80e0
Object: 86e031a8  Type: (8521a838) Mutant
    ObjectHeader: 86e03190 (new version)
        HandleCount: 1  PointerCount: 1
```

这样我们就可以找到池的位置，细节如下：



```
lkd&gt; !pool 86e031a8  
Pool page 86e031a8 region is Nonpaged pool
 86e03000 size:   98 previous size:    0  (Allocated)  IoCo (Protected)
 86e03098 size:   90 previous size:   98  (Allocated)  MmCa
 86e03128 size:   40 previous size:   90  (Allocated)  Even (Protected)
 86e03168 size:   10 previous size:   40  (Free)       Icp 
*86e03178 size:   50 previous size:   10  (Allocated) *Muta (Protected)
  Pooltag Muta : Mutant objects
 86e031c8 size:   40 previous size:   50  (Allocated)  Even (Protected)
 86e03208 size:   40 previous size:   40  (Allocated)  Even (Protected)
```

它显示在非分页池中需要 0x50 字节大小的位置。无论我们重复多少次，都是 0x50。看起来确实如此。如果我们将之前的代码放在一个循环中，我们可以看到它能够工作，并且可以进行很棒的堆喷射：



```
851ef118 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef168 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef1b8 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef208 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef258 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef2a8 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef2f8 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef348 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef398 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef3e8 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef438 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef488 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef4d8 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef528 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef578 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef5c8 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef618 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef668 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef6b8 size:   50 previous size:   50  (Allocated)  Muta (Protected)
 851ef708 size:   50 previous size:   50  (Allocated)  Muta (Protected)
```

那么如果我们给 Mutex 取一个名字，会有什么样的变化？这是另一段 Python 代码：



```
def alloc_named_mutex(i):
        hHandle = HANDLE(0)
hHandle = kernel32.CreateMutexA(None, False, "Pool spraying is cool " + str(i))
if hHandle == None:
                print "[-] Error while creating mutex"
  sys.exit()
print hex(hHandle)
```

我给它传递了一个参数，因为如果我们要使用它来进行喷射，这将是很重要的，因为我们不能创建两个具有相同命名的 mutex。

一旦我们创建了 mutex，并且我们遵循与之前一样的逻辑，就可以看到其中有点不同：



```
*871d39e8 size:   60 previous size:   30  (Allocated) *Muta (Protected)
  Pooltag Muta : Mutant objects
```

这一次它需要 0x60 字节，这也是一致的。我们也可以做同样的喷射，但具有不同的大小。这里有一些重要的东西。如果我们看一看池分配，就可以看到这是一个从 pool chunk 的头位置偏移 0x20 的指针，指向 Mutex 的名字：<br>

```
lkd&gt; dd 871d39e8 
871d39e8  040c0006 e174754d 00000000 00000050
871d39f8  00000000 00000000 9a06fb38 002e002e
871d3a08  aab50528 00000000 00000002 00000001
871d3a18  00000000 000a000e 86e0bd80 99a4fc07
871d3a28  0008bb02 00000001 871d3a30 871d3a30
871d3a38  00000001 00000000 00000000 01d10000
871d3a48  040b000c 6d4d6956 b299b8c8 9a087020
871d3a58  a8246340 00000000 00000000 85d4f0b0
lkd&gt; dd aab50528
aab50528  006f0050 006c006f 00730020 00720070
aab50538  00790061 006e0069 00200067 00730069
aab50548  00630020 006f006f 0020006c 006f0031
lkd&gt; dS aab50528
006c006f  "????????????????????????????????"
006c00af  "????????"
```

我的 WinDBG 看起来是不想打印出对象的名字，但是如果你以十六进制格式查看它的 UNICODE，它就是我们给 Mutex 的命名。如果我们检查这个字符串的存储位置：



```
lkd&gt; !pool aab50528
Pool page aab50528 region is Paged pool
 aab50000 size:   a8 previous size:    0  (Allocated)  CMDa
 aab500a8 size:   28 previous size:   a8  (Free)       3.7.
 aab500d0 size:   28 previous size:   28  (Allocated)  NtFs
 aab500f8 size:   28 previous size:   28  (Allocated)  MmSm
 aab50120 size:   38 previous size:   28  (Allocated)  CMnb Process: 86ef6760
 aab50158 size:  100 previous size:   38  (Allocated)  IoNm
 aab50258 size:   38 previous size:  100  (Allocated)  CMDa
 aab50290 size:   38 previous size:   38  (Allocated)  CMNb (Protected)
 aab502c8 size:   28 previous size:   38  (Allocated)  MmSm
 aab502f0 size:   20 previous size:   28  (Allocated)  CMNb (Protected)
 aab50310 size:   60 previous size:   20  (Allocated)  Key  (Protected)
 aab50370 size:   20 previous size:   60  (Allocated)  SeAt
 aab50390 size:   d8 previous size:   20  (Allocated)  FMfn
 aab50468 size:   28 previous size:   d8  (Allocated)  CMVa
 aab50490 size:   30 previous size:   28  (Allocated)  CMVa
 aab504c0 size:   60 previous size:   30  (Allocated)  Key  (Protected)
*aab50520 size:   38 previous size:   60  (Allocated) *ObNm
  Pooltag ObNm : object names, Binary : nt!ob
```

可以看到它在分页池中！之后我们还会回顾这里，但在这里先透露一些东西：我们可以使用命名的 Mutex 在分页池区域（paged pool area）中创建自定义大小的分配，大小取决于我们给出的名称。这对于在分页池中进行喷射是非常有用的。

<br>

**第二部分——使用pykd编写脚本**

正如上一部分中讲到的，获得对象实际大小的过程是相当简单的，但是如果我们需要获得很多对象大小的时候，这将是一个繁重的手工作业，因此为了避免浪费太多时间，此过程应该被自动化执行。手动操作几次当然是有好处的，特别是对初学者而言，但是更多的重复就没有意义了。那么我们如何编写 WinDBG 脚本？用 pykd！pykd 是 WinDBG 的一个很棒的 Python 扩展，它甚至允许在没有手动启动 WinDBG 的情况下编写脚本。

第一件事就是安装 pykd，这有时很让人头疼。它并不总是像听起来那么简单。如果我们下载预编译的版本，并将 pykd.pyd 文件放在 WinDBG 的 winext 目录下，可能是最简单的方法。请让 WinDBG、Python、VCRedict 和 pykd 的架构相同（x86 或 x64），这一点很重要。你也可以通过 PIP 来安装 pykd，但是我在尝试导入它的时候并没有成功。另外一定要使用最新版本的 Python （2.7.13），当启动 pykd 时，一些较旧的版本（如 2.7.9）会使 WinDBG 退出。至于那些更老版本的 Python（2.7.1），它曾经是可以工作的。但是你一旦这么做，它将成为一个非常强大的扩展。

于是我写了一个简单的函数来获取对象名称和句柄，并且会查找对象的大小。也许还有其他更优雅的解决方案，但下面的脚本已经可以满足我的需求：



```
def find_object_size(handle,name):
#find windbg.exe process
wp = dbgCommand('!process 0 0 windbg.exe')
#print wp
#extract process "address"
process_tuples = re.findall( r'(PROCESS )([0-9a-f]*)(  SessionId)', wp)
if process_tuples:
  process = process_tuples[0][1]
  print "Process: " + process
  #switch to process context
  dbgCommand(".process " + process)
  #find object "address"
  object_ref = dbgCommand("!handle " + h)
  object_tuples = re.findall( r'(Object: )([0-9a-f]*)(  GrantedAccess)', object_ref)
  if object_tuples:
   obj = object_tuples[0][1]
   print "Object: " + obj
   #find pool
   pools = dbgCommand("!pool " + obj)
   #print pools
   #find size
   size_re = re.findall(r'(*[0-9a-f]`{`8`}` size:[ ]*)([0-9a-f]*)( previous)',pools)
   if size_re:
    print name + " objects's size in kernel: " + size_re[0][1]
#close handle
kernel32.CloseHandle(handle)
```

<br>

**第三部分——研究分析**

脚本将会减轻我们寻找池大小分配的工作。有了这个我会查看下面的对象：

**Event**

**IoCompletionPort**

**IoCompletionReserve**

**Job（已命名的和未命名的）<br>**

**Semaphore（已命名的和未命名的）**

从这一点来讲，过程是非常简单的，我们只需要调用相关的用户模式函数，创建一个对象，然后检查大小。我为 WinDBG 创建了一个简短的脚本，它能够自动化创建上述的对象，并检查大小，最后把它们打印出来。我把脚本上传到了这里：

[https://github.com/theevilbit/kex/blob/master/kernel_objects.py](https://github.com/theevilbit/kex/blob/master/kernel_objects.py)

使用方法：

1.    启动 WinDBG

2.    依次点击 Kernel debug -&gt; Local

3.    执行命令：.load pykd

4.    命令：!py path_to_the_script

结果如下：



```
Not Named Mutex objects's size in kernel: 0x50
Named Mutex objects's size in kernel: 0x60
Job objects's size in kernel: 0x168
Job objects's size in kernel: 0x178
IoCompletionPort objects's size in kernel: 0x98
Event objects's size in kernel: 0x40
IoCompletionReserve objects's size in kernel: 0x60
Not named Semaphore objects's size in kernel: 0x48
Named Semaphore objects's size in kernel: 0x58
```

这样我们就得到了一套不错的可用于内核池喷射的对象。那么什么是“kex”，它在期望什么呢？在后面的文章中你将看到内核中更酷的东西。

也许我应该在这个系列的开始做一些解释。我想写一些脚本，让我们在进行 Windows 内核利用开发的时候更快，我的第一个脚本是用于内核池喷射的。另外，如果你从来没有看过关于内核池溢出的东西，也没有用过内核池喷射技术。那么可以阅读：

[http://trackwatch.com/windows-kernel-pool-spraying/](http://trackwatch.com/windows-kernel-pool-spraying/)

[http://www.fuzzysecurity.com/tutorials/expDev/20.html](http://www.fuzzysecurity.com/tutorials/expDev/20.html)

现在我们已经有了一个包含内核对象大小的列表（该脚本也可以在其他平台上运行，尽管可能需要针对 x64 架构做一些修改），我们可以进行自动化的喷射和制造空隙（hole）了。如果我们知道需要多大的空隙的话。

基本上：

**1.    一旦我们分析了漏洞，就会知道驱动程序将在内核池中分配的对象或缓冲器的大小是多少。**

**2.    我们需要控制该分配的位置，所以我们需要在池中准备一个给定大小的空隙，以便内核在那儿分配新对象。**

**3.    如果我们知道大小，就可以简单地计算出什么类型的对象利于喷射，还有我们需要释放掉多少个该对象。**

**4.    如果我们知道这些所有的东西，就可以进行内核喷射并制造空隙了。**

我们需要知道该对象的信息和我们使用溢出覆盖的池头部的信息，之后我会回来再讲的，因为在制造空隙时并不需要这些。我可能会失败，也做了一些准备，我希望覆盖数据也可以自动生成。现在，我只想根据给定的大小去制造空隙。所以我写了一个脚本，可以用于这个目的（请注意，这里是为 Win7 SP1 x86 硬编码的）：

[https://github.com/theevilbit/kex/blob/master/spray_helper.py](https://github.com/theevilbit/kex/blob/master/spray_helper.py)

它会让你输入想要的空隙的大小，然后进行喷射，释放空间并在 WinDBG 中显示该区域。还要注意的是，它仍是使用本地内核调试器，我们无法设置断点，所以存在竞争条件的问题，当我们使用 !pool 命令时，可以像其他内核进程一样在可用空间中分配。我仍然使用本地内核调试器的原因是对于目前阶段的演示来说更简单。当我做真实的利用演示时，就需要进行远程调试了，但在这里我可以直接进行演示。下面是输出：

```
lkd&gt; !py c:userscsabydesktopspray_helper.py
Give me the size of the hole in hex: 440
Process: 8572bd40
Object location: 857e15f0
Pool page 857e15f0 region is Nonpaged pool
 857e1000 size:   40 previous size:    0  (Allocated)  Even (Protected)
 857e1040 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e1080 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e10c0 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e1100 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e1140 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e1180 size:   40 previous size:   40  (Free )  Even (Protected)
 857e11c0 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1200 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1240 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1280 size:   40 previous size:   40  (Free )  Even (Protected)
 857e12c0 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1300 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1340 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1380 size:   40 previous size:   40  (Free )  Even (Protected)
 857e13c0 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1400 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1440 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1480 size:   40 previous size:   40  (Free )  Even (Protected)
 857e14c0 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1500 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1540 size:   40 previous size:   40  (Free )  Even (Protected)
 857e1580 size:   40 previous size:   40  (Free )  Even (Protected)
*857e15c0 size:   40 previous size:   40  (Allocated) *Even (Protected)
  Pooltag Even : Event objects
 857e1600 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e1640 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e1680 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e16c0 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e1700 size:   40 previous size:   40  (Allocated)  Even (Protected)
 857e1740 size:   40 previous size:   40  (Allocated)  Even (Protected)
```

你可以看到我们有 17 x 0x40，也就是 0x440 的空闲空间，没有必要去处理更多细节。我可以给出任何其他的大小，例如：



```
lkd&gt; !py c:userscsabydesktopspray_helper.py
Give me the size of the hole in hex: 260
Process: 8572bd40
Object location: 87b2fe00
Pool page 87b2fe00 region is Nonpaged pool
 87b2f000 size:   98 previous size:    0  (Allocated)  IoCo (Protected)
 87b2f098 size:   90 previous size:   98  (Free)       ....
 87b2f128 size:   98 previous size:   90  (Allocated)  IoCo (Protected)
 87b2f1c0 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f258 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f2f0 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f388 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f420 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f4b8 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f550 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f5e8 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f680 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f718 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f7b0 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f848 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f8e0 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2f978 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2fa10 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2faa8 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2fb40 size:   98 previous size:   98  (Free )  IoCo (Protected)
 87b2fbd8 size:   98 previous size:   98  (Free )  IoCo (Protected)
 87b2fc70 size:   98 previous size:   98  (Free )  IoCo (Protected)
 87b2fd08 size:   98 previous size:   98  (Free )  IoCo (Protected)
*87b2fda0 size:   98 previous size:   98  (Allocated) *IoCo (Protected)
  Owning component : Unknown (update pooltag.txt)
 87b2fe38 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2fed0 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
 87b2ff68 size:   98 previous size:   98  (Allocated)  IoCo (Protected)
```

可以看到这个喷射正是我们想要的。请注意，这一次使用了不同的对象。如果你测试很多次，请尝试着使用一个会导致不同对象分配的数字，那样你就可以得到更整洁的输出。

另一个值得注意的事情是，这里制造的空隙不是 100% 可靠的，但我相信已经非常接近了。我做了如下几点：我使用 100000 个对象对内核进行喷射，然后释放掉中间的 X 个。这很可能会让它们一个接着一个，并在我释放掉它们的时候提供给我们需要的空间，为了演示自动化过程，这是最简单的。但如果像下面这样的话会更可靠：

我尝试制造多个空隙，并释放多个 X，它们可能是彼此相邻的。

有一种方法可以从内核中泄露对象的地址，并计算它们是否相邻，从而释放空间。这是最可靠的方法。

随着我的进步，我会在将来实现它，但是现在我采用了第一种方法。

是的，我使用 Python 编码，而不是 Powershell，仅仅是因为我不能在 PS 中写代码，但是我完全同意人们说的，在 PS 中实现会更有意义。
