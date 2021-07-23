> 原文链接: https://www.anquanke.com//post/id/85784 


# 【漏洞分析】Firefox一个整数溢出导致的mmap区域越界写利用


                                阅读量   
                                **117321**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：saelo.github.io
                                <br>原文地址：[https://saelo.github.io/posts/firefox-script-loader-overflow.html](https://saelo.github.io/posts/firefox-script-loader-overflow.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t019fac03cd351c1232.jpg)](https://p1.ssl.qhimg.com/t019fac03cd351c1232.jpg)**

****

翻译：[beswing](http://bobao.360.cn/member/contribute?uid=820455891)

稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**TL;DR**



这个文章将探讨一个很有趣的漏洞—CVE-2016-9066 ，一个很简单但是很有趣的可以导致代码执行的Firefox漏洞。

中的代码中存在一个整数溢出漏洞，导致加载的mmap区域越界。有一种利用这一点的方法是，将JavaScrip的堆放在缓冲器后面，随后溢出到其元数据中以创建假空闲单元。然后可以将ArrayBuffer创建的实例放在另一个ArrayBuffer的内联数据中。然后可以任意修改内部ArrayBuffer，产生任意的读和写。并可以很容易的实现代码的执行。完整的漏洞报告可以在[这里](https://github.com/saelo/foxpwn)找到，这对MacOS 10.11.6上的Firefox 48.0.1进行了测试。Bugzilla的漏洞报告可以在[这里](https://github.com/saelo/foxpwn)找到。

**<br>**

**The Vulnerability**



下面的代码用于加载脚本标记的数据:

```
result
nsScriptLoadHandler::TryDecodeRawData(const uint8_t* aData,
                                      uint32_t aDataLength,
                                      bool aEndOfStream)
`{`
  int32_t srcLen = aDataLength;
  const char* src = reinterpret_cast&lt;const char *&gt;(aData);
  int32_t dstLen;
  nsresult rv =
    mDecoder-&gt;GetMaxLength(src, srcLen, &amp;dstLen);
  NS_ENSURE_SUCCESS(rv, rv);
  uint32_t haveRead = mBuffer.length();
  uint32_t capacity = haveRead + dstLen;
  if (!mBuffer.reserve(capacity)) `{`
    return NS_ERROR_OUT_OF_MEMORY;
  `}`
  rv = mDecoder-&gt;Convert(src,
                         &amp;srcLen,
                         mBuffer.begin() + haveRead,
                         &amp;dstLen);
  NS_ENSURE_SUCCESS(rv, rv);
  haveRead += dstLen;
  MOZ_ASSERT(haveRead &lt;= capacity, "mDecoder produced more data than expected");
  MOZ_ALWAYS_TRUE(mBuffer.resizeUninitialized(haveRead));
  return NS_OK;
`}`
```

当新数据从服务器到达时，代码将由OnIncrementalData调用。 这里的bug是一个简单的整数溢出，发生在服务器发送超过4GB的数据时。 在这种情况下， capacity将wrap around，并且调用mBuffer.reserve，但并不会以任何方式修改缓冲区。 mDecode-&gt;Convert然后在缓冲区的结尾写超过8GB的数据（数据在浏览器中存储为char16_t），这将由一个mmap块（一个普通的，很大的mmap 区块）支持下完成。

补丁也很简单：

```
uint32_t haveRead = mBuffer.length();
-  uint32_t capacity = haveRead + dstLen;
-  if (!mBuffer.reserve(capacity)) `{`
+
+  CheckedInt&lt;uint32_t&gt; capacity = haveRead;
+  capacity += dstLen;
+
+  if (!capacity.isValid() || !mBuffer.reserve(capacity.value())) `{`
     return NS_ERROR_OUT_OF_MEMORY;
   `}`
```

首先，看起来没有那么可靠。 例如，它需要发送和分配多个千兆字节的内存。 但是，我们会看到，该bug事实上可以被很可靠的利用的，并且在我的2015年版本的MacBook Pro上打开页面后大约一分钟内就能完成漏洞的触发。 我们现在将首先探讨如何利用这个bug在macOS上弹出一个计算器，然后提高漏洞利用的可靠性，并使用较少的带宽（我们将使用HTTP压缩数据）。

**<br>**

**漏洞利用**



```
#include &lt;sys/mman.h&gt;
#include &lt;stdio.h&gt;
const size_t MAP_SIZE = 0x100000;       // 1 MB
int main()
`{`
    char* chunk1 = mmap(NULL, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    char* chunk2 = mmap(NULL, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    printf("chunk1: %p - %pn", chunk1, chunk1 + MAP_SIZE);
    printf("chunk2: %p - %pn", chunk2, chunk2 + MAP_SIZE);
    return 0;
`}`
```

上面的程序的打印结果，能告诉我们能通过简单的mmap ，映射内存直到存有的空间都被填充，然后通过mmap分配一个内存块，来分配溢出缓冲区后面的东西。 要验证这一点，我们将执行以下操作：

加载脚本(包含payload.js,将导致溢出的代码) 和一些异步执行的JavaScrip代码(code.js，用来执行下面的步骤3和步骤5)

当浏览器请求payload.js时，让服务器回复Content-Length为0x100000001，但只发送数据的第一个0xffffffff字节

然后，让JavaScript代码分配多个足够大的（1GB）ArrayBuffers（内存不一定会使用，直到实际写入缓冲区）

让webserver发送payload.js的剩余两个字节

检查每个ArrayBuffer的前几个字节， 有一个应该包含由webserver发送数据

为了实现这一点，我们将需要在浏览器中运行的JavaScript代码和web服务器之间的某种同步原语。 为此，我在python的asyncio库上面写了一个小的[web服务器](https://github.com/saelo/foxpwn/blob/master/server.py) ，它包含一个方便的[事件对象](https://docs.python.org/3/library/asyncio-sync.html#event) ，用于同步协同。 创建两个全局事件可以向服务器发信号通知客户端代码已完成其当前任务，并且现在正在等待服务器执行下一步骤。 /sync的处理程序如下所示：



```
async def sync(request, response):
    script_ready_event.set()
    await server_done_event.wait()
    server_done_event.clear()
    response.send_header(200, `{`
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Length': '2'
    `}`)
    response.write(b'OK')
    await response.drain()
```



**获取目标 Hunting for Target Objects**

因为malloc （以及C ++中的new操作符）在某些时候将使用mmap请求更多的内存，所以分配给它们的任何内容都可能对我们的漏洞利用有帮助。 我走了一条不同的路线。 我最初想检查是否可能溢出到JavaScript对象，例如损坏数组的长度或类似的东西。 因此，我开始探索JavaScript分配器以查看JSObject存储在哪里。 Spidermonkey（Firefox中的JavaScript引擎）将JSObjects存储在两个独立的区域中：

终止堆。 更长的活动中的对象以及几个选定的对象类型在这里分配。 这是一个相当经典的堆，跟踪自由点，然后重新用于之后的分配。

The Nursery。 这是一个包含短暂对象的内存区域。 大多数JSObject在这里首先被分配，然后在下一个GC循环期间被移动到永久堆中（这包括更新它们的所有指针，因此需要gargabe收集器知道它的对象的所有指针）。 Nursery不需要自由列表或类似的：在GC循环之后，Nursery简单地被声明为自由的，因为所有活动的对象已经被移出它的区域。

有关Spidermonkey内部的更深入的讨论，请参阅[这篇文章](http://phrack.com/issues/69/14.html#article)。

堆中的对象存储在名为Arenas的容器中：



```
/*
* Arenas are the allocation units of the tenured heap in the GC. An arena
* is 4kiB in size and 4kiB-aligned. It starts with several header fields
* followed by some bytes of padding. The remainder of the arena is filled
* with GC things of a particular AllocKind. The padding ensures that the
* GC thing array ends exactly at the end of the arena:
*
* &lt;----------------------------------------------&gt; = ArenaSize bytes
* +---------------+---------+----+----+-----+----+
* | header fields | padding | T0 | T1 | ... | Tn |
* +---------------+---------+----+----+-----+----+
* &lt;-------------------------&gt; = first thing offset
*/
class Arena
`{`
 static JS_FRIEND_DATA(const uint32_t) ThingSizes[];
 static JS_FRIEND_DATA(const uint32_t) FirstThingOffsets[];
 static JS_FRIEND_DATA(const uint32_t) ThingsPerArena[];
 /*
  * The first span of free things in the arena. Most of these spans are
  * stored as offsets in free regions of the data array, and most operations
  * on FreeSpans take an Arena pointer for safety. However, the FreeSpans
  * used for allocation are stored here, at the start of an Arena, and use
  * their own address to grab the next span within the same Arena.
  */
 FreeSpan firstFreeSpan;
 // ...
```

注释已经给出了一个相当好的概括： [Arenas](https://github.com/mozilla/gecko-dev/blob/40ae52a2c349f978a462a38f770e4e35d49f6563/js/src/gc/Heap.h#L450)只是容器对象，其中分配了[相同大小](https://github.com/mozilla/gecko-dev/blob/40ae52a2c349f978a462a38f770e4e35d49f6563/js/src/gc/Heap.h#L83)的JavaScript对象。 它们位于容器对象（ Chunk结构）内部 ，该结构本身通过mmap直接分配。 有趣的部分是Arena类的firstFreeSpan成员：它是Arena对象的第一个成员（并且因此位于mmap-ed区域的开始），并且基本上指示该Arena内的第一个自由单元的索引。 这是FreeSpan实例的样子：



```
class FreeSpan
`{`
 uint16_t first;
 uint16_t last;
 // methods following
`}`
```

first和last是到Arena的字节索引，指示freelist的头部。 这打开了一个有趣的方式来利用这个bug：通过溢出到Arena的firstFreeSpan字段，我们可以分配一个对象在另一个对象内，最好在某种类型的可访问的内联数据内。 然后我们可以任意修改“内部”对象。

这种技术有几个好处：

能够在Arena内部的选定偏移处分配JavaScript对象直接产生存储器读/写，正如我们将看到的

我们只需要溢出以下块的4个字节，因此不会损坏任何指针或其他敏感数据

Arenas / Chunks可以通过分配大量的JavaScript对象

事实证明，大小为96字节的ArrayBuffer对象将把它们的数据存储在对象header之后。 他们也将跳过nursery ，因此位于Arena内。 这使得它们是我们的漏洞利用的理想选择。 我们会这样

分配大量的ArrayBuffer与96字节的存储

溢出并创建一个假的自由单元格内的竞技场下面我们的缓冲区

分配更多的相同大小的ArrayBuffer对象，看看它们中的一个是否放在另一个ArrayBuffer的数据内（只是扫描所有“old”ArrayBuffers为非零内容）

<br>

**对GC的需要**

不幸的是，这不是那么容易：为了让Spidermonkey在我们的目标（损坏） Arena中分配一个对象， Arena必须以前被标记为（部分）free。 这意味着我们需要在每个竞技场至少释放一个slot。 我们可以通过删除每25个ArrayBuffer（因为每个Arena有25个），然后强制垃圾收集机制。

Spidermonkey由于各种 原因触发垃圾收集。 似乎最容易触发的是TOO_MUCH_MALLOC ：它只是在通过malloc分配了一定数量的字节时被触发。 因此，以下代码足以触发垃圾回收：



```
function gc() `{`
    const maxMallocBytes = 128 * MB;
    for (var i = 0; i &lt; 3; i++) `{`
        var x = new ArrayBuffer(maxMallocBytes);
    `}`
`}`
```

然后，我们的目标竞技场将被放到自由列表，我们随后的覆盖将损坏它。 从损坏的竞技场的下一个分配将返回ArrayBuffer对象的内联数据内的（假的）单元格。

<br>

**（可选读数）压缩GC**

其实，这有点复杂。 存在称为压缩GC的GC模式，其将从多个部分填充的arenas移动对象以填充其他arenas。 这减少了内部碎片，并帮助释放整个块，以便它们可以返回到操作系统。 然而，对于我们来说，压缩GC会很麻烦，因为它可能填补我们在目标arenas上创建的洞。 以下代码用于确定是否应运行压缩GC：



```
bool
GCRuntime::shouldCompact()
`{`
    // Compact on shrinking GC if enabled, but skip compacting in incremental
    // GCs if we are currently animating.
    return invocationKind == GC_SHRINK &amp;&amp; isCompactingGCEnabled() &amp;&amp;
        (!isIncremental || rt-&gt;lastAnimationTime + PRMJ_USEC_PER_SEC &lt; PRMJ_Now());
`}`
```

看看代码应该有办法防止压缩GC发生（例如通过执行一些animations）。 看起来我们很幸运：我们的gc函数从上面将触发Spidermonkey中的下面的代码路径，从而阻止压缩GC，因为invocationKind将是GC_NORMAL而不是GC_SHRINK 。



```
bool
GCRuntime::gcIfRequested()
`{`
    // This method returns whether a major GC was performed.
    if (minorGCRequested())
        minorGC(minorGCTriggerReason);
    if (majorGCRequested()) `{`
        if (!isIncrementalGCInProgress())
            startGC(GC_NORMAL, majorGCTriggerReason);       // &lt;-- we trigger this code path
        else
            gcSlice(majorGCTriggerReason);
        return true;
    `}`
    return false;
`}`
```



**Writing an Exploit 完成攻击脚本的编写**

这一点上，我们所有的部分在一起，实际上可以写一个利用。 一旦我们创建了假的空闲单元并在其中分配了一个ArrayBuffer，我们将看到之前分配的ArrayBuffer之一现在包含数据。 Spidermonkey中的ArrayBuffer对象大致如下：



```
// From JSObject
GCPtrObjectGroup group_;
// From ShapedObject
GCPtrShape shape_;
// From NativeObject
HeapSlots* slots_;
HeapSlots* elements_;
// Slot offsets from ArrayBufferObject
static const uint8_t DATA_SLOT = 0;
static const uint8_t BYTE_LENGTH_SLOT = 1;
static const uint8_t FIRST_VIEW_SLOT = 2;
static const uint8_t FLAGS_SLOT = 3;
```

XXX_SLOT常数确定对象从对象开始的偏移量。 因此，数据指针（ DATA_SLOT ）将存储在addrof(ArrayBuffer) + sizeof(ArrayBuffer) 。

我们现在可以构造以下exploit

从绝对内存地址读取：我们将DATA_SLOT设置为所需的地址，并从内部ArrayBuffer读取

写入绝对内存地址：与上面相同，但这次我们写入内部ArrayBuffer

泄漏JavaScript对象的地址：为此，我们设置其地址我们想知道作为内部ArrayBuffer的属性的对象，然后通过我们现有的读基元从slots_指针读取地址

<br>

**进一步**

为了避免在下一个GC循环期间崩溃浏览器进程，我们必须修复几件事：

ArrayBuffer在我们的exploit中的外部 ArrayBuffer之后，因为它将被内部 ArrayBuffer的数据损坏。 要解决这个问题，我们可以简单地将另一个ArrayBuffer对象复制到该位置

最初在我们的Arena中释放的Cell现在看起来像一个使用的Cell，并且将被收集器处理，导致崩溃，因为它已被其他数据覆盖（例如FreeSpan实例）。 我们可以通过恢复我们的Arena的原始firstFreeSpan字段来修复这个问题，将该Cell标记为空闲。

<br>

**小结**

将所有内容放在一起，以下步骤将给我们一个任意的读/写 ：

插入脚本标记以加载有效负载，最终触发错误。

等待服务器发送高达2GB + 1字节的数据。 浏览器现在将分配最终的块，我们以后会溢出。 我们尝试使用ArrayBuffer对象填充现有的mmap孔，就像我们对第一个PoC所做的那样。

分配包含大小为96（最大大小的ArrayBuffers）的JavaScript Arenas（内存区域），因此数据仍然分配在对象后面，并希望其中一个放在我们即将溢出的缓冲区之后。 Mmap分配连续区域，所以这只能失败，如果我们没有分配足够的内存或如果别的东西分配那里。

让服务器总共发送所有内容到0xffffffff字节，完全填充当前块

在每个竞技场中释放一个ArrayBuffer，并尝试触发gargabe集合，以便将arenas插入到空闲列表中。

让服务器发送剩余的数据。 这将触发溢出并损坏其中一个场的内部自由列表（指示哪些单元未使用）。 修改freelist，使得第一自由单元位于竞技场中包含的ArrayBuffer之一的内联数据内。

分配更多ArrayBuffers。 如果一切工作到目前为止，其中一个将被分配在另一个ArrayBuffer的内联数据内部。 搜索该ArrayBuffer。

如果找到，则构造任意的存储器读/写原语。 我们现在可以修改内部ArrayBuffer的数据指针，所以这很容易。

修复损坏的对象，以便在我们的漏洞利用完成后保持进程的活动。

<br>

**现在我们可以弹出计算器了**

行自定义代码的一个简单方法是滥用JIT区域 ，但是，这种技术（部分） 在Firefox中减轻 。 给定我们的开发原语（例如通过编写一个小ROP链并在那里传送控制），这可以被绕过，但是对于简单的PoC来说这似乎很复杂。

还有其他Firefox特有的技术，通过滥用特权JavaScript来获取代码执行，但这些需要对浏览器状态进行非常小的修改（例如，添加turn_off_all_security_so_that_viruses_can_take_over_this_computer首选项）。

我结束了使用一些标准的CTF技巧来完成漏洞：寻找交叉引用libc函数接受一个字符串作为第一个参数（在这种情况下strcmp），我发现Date.toLocalFormat的Date.toLocalFormat ，并注意到它转换其第一参数从JSString到C字符串 ，然后它用作strcmp的第一个参数 。 因此，我们可以简单地用system的地址替换strcmp的GOT条目，并执行data_obj.toLocaleFormat("open -a /Applications/Calculator.app");. Done 🙂

<br>

**改进 Exploit**

在这一点上，基本的攻击已经完成。 本节现在将描述如何使其更可靠和更少的带宽资源。

**Adding Robustness**

目前为止，我们的漏洞利用只是分配了一些非常大的ArrayBuffer实例（每个1GB）来填充现有的mmap空间，然后再分配大约另一个GB的js :: Arena实例来溢出。 因此，它假定浏览器堆操作在利用期间或多或少是确定性的。 由于这不一定是这种情况，我们希望使我们的漏洞更加健壮。

快速查看然后实现mozilla :: Vector类（用于保存脚本缓冲区）向我们展示了它在需要时使用realloc将其缓冲区的大小增加一倍。 由于jemalloc直接将mmap用于较大的块，这使我们有以下分配模式:



```
mmap 1MB
mmap 2MB，munmap previous chunk
mmap 4MB，munmap previous chunk
... ...
mmap 8GB，munmap previous chunk
```

因为当前块大小将总是大于所有先前块大小的总和，这将导致在我们的最终缓冲器之前有大量的可用空间。 理论上，我们可以简单地计算空闲空间的总和，然后再分配一个大的ArrayBuffer。 在实践中，这不工作，因为在服务器开始发送数据之后和在浏览器完成解压缩最后一个块之前将有其他分配。 jemalloc保留释放的内存的一部分以备后用。 相反，我们会尝试在浏览器释放后立即分配一个块。 这里是我们要做的事情：

JavaScript代码使用sync等待服务器

服务器将所有数据发送到下一次方的二（以MB为单位），因此在结束时只触发一次对realloc的调用。 浏览器现在将释放一个已知大小的块

服务器设置server_done_event ，导致JavaScript代码执行

JavaScript代码分配与上一个缓冲区大小相同的ArrayBuffer实例，填充可用空间

这被重复，直到我们发送0x80000001字节（因此强制最终缓冲区的分配）

个简单的算法在服务器端和客户端在步骤1中实现 。 使用这种算法，我们可以相当可靠地获得一个分配在我们的目标缓冲区后面，只喷洒几个兆字节的ArrayBuffer实例，而不是多个千兆字节。

<br>

**减少网路负载**

我们当前的漏洞需要通过网络发送4GB的数据。 这很容易解决：我们将使用HTTP压缩。 这里的好处是例如zlip 支持 “流式”压缩，这使得可以递增地压缩有效载荷。 这样，我们只需要将有效负载的每个部分添加到zlib流中，然后调用flush以获取有效负载的下一个压缩块，并将其发送到服务器。 服务器将在接收到该块时对该块进行解压缩并执行所需的动作（例如执行一个重分配步骤）。

这是在poc.py中的construct_payload方法中实现的 ，并设法将有效负载的大小减小到大约18MB。。

<br>

**关于资源的使用**

至少在理论上，漏洞需要相当多的内存：

一个8GB缓冲区，保存我们的“JavaScript”有效负载。 实际上，它更像是12 GB，因为在最后的realloc期间，4GB缓冲区的内容必须复制到一个新的8GB缓冲区

多个（大约6GB）缓冲区，由JavaScript分配以填充由realloc创建的空洞

大约256 MB的ArrayBuffers

然而，由于许多缓冲器从未被写入，它们不一定消耗任何物理存储器。 此外，在最后的realloc期间，只有4GB的新缓冲区将被写入到旧的缓冲区被释放之前，所以真正的“只”8 GB是必需的。

这仍然是很大的内存。 然而，有一些技术，如果物理内存变低，将有助于减少该数量：

内存压缩（macOS）：大内存区域可以压缩和交换出来。 这是我们的用例的完美，因为8GB缓冲区将完全填充零。 这种效果可以在Activity Monitor.app中观察到，在某些时候显示超过6 GB的内存被“压缩”在利用期间。

页重复数据删除（Windows，Linux）：包含相同内容的页面被映射为写时复制（COW），并指向同一物理页面（实质上将内存使用减少到4KB）。

CPU使用率也将在（解压缩）时被使用得相当高。 然而，CPU压力可以进一步减少通过发送有效载荷在较小的块之间的延迟（这将明显增加漏洞利用所需的时间）。 这也将给予OS更多的时间来压缩和/或去重复大的存储器缓冲器。

<br>

**进一步改进的可能性**

在当前的漏洞中有一些不可靠的来源，主要是处理时序：

在发送有效载荷数据期间，如果JavaScript在浏览器完全处理下一个块之前运行分配，则分配将“去同步”。 这可能导致失败的攻击。 理想情况下，一旦下一个块被接收和处理，JavaScript就会执行分配。 这可能通过观察CPU使用情况来确定。

如果垃圾收集循环在我们已经破坏FreeSpan之后但在我们修复它之前运行，我们就崩溃了

如果在我们释放了一些ArrayBuffer之后但是在触发溢出之前运行了一个可压缩的gargabe收集循环，则攻击将失败，因为Arena将再次被填满。

如果假的空闲单元恰好放置在释放的ArrayBuffer的单元格内，那么我们的漏洞将会失败，并且浏览器会在下一个gargabe收集周期中崩溃。 每个arena 有25个cells per，这给我们理论上的1/25失败的机会。 然而，在我的实验中，空闲单元总是位于相同的偏移量（到 Arena中的1216个字节），指示在开发开始时的引擎的状态是相当确定的（至少关于 Arena持有的状态大小为160字节的对象）。

从我的经验，如果浏览器没有大量使用，漏洞运行相当可靠（&gt; 95％）。 如果10+个其他选项卡已打开，漏洞利用仍然有效，但如果目前正在加载大型Web应用程序，则可能会失败。

<br>

**结论**

虽然从攻击者的角度来看，这个漏洞并不理想，但它仍然可以被相当可靠地利用并且没有太多的带宽使用。 有趣的是看到各种技术（压缩，相同的页面合并，…）可以使一个更容易利用的bug。

想想如何防止这样的bug的可利用性，一些事情想起来了。 一个相当通用的缓解是保护页（每当以某种方式访问时，导致segfault的页）。 这些将必须在每个mmap分配区域之前或之后分配，并且因此将防止利用诸如这一个的线性溢出。 然而，它们不能防止非线性溢出，例如这个错误 。 另一种可能性是引入内部mmap随机化以分散遍及地址空间的分配区域（可能仅在64位系统上有效）。 这最好由内核执行，但也可以在用户空间中执行。
