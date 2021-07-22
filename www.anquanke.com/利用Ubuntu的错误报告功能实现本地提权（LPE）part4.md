> 原文链接: https://www.anquanke.com//post/id/195952 


# 利用Ubuntu的错误报告功能实现本地提权（LPE）part4


                                阅读量   
                                **1186836**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者github，文章来源：securitylab.github.com
                                <br>原文地址：[https://securitylab.github.com/research/ubuntu-whoopsie-CVE-2019-11484](https://securitylab.github.com/research/ubuntu-whoopsie-CVE-2019-11484)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01cd34f92ae310e7ca.jpg)](https://p4.ssl.qhimg.com/t01cd34f92ae310e7ca.jpg)



这篇文章中，我将重点介绍whoopsie CVE-2019-11484，一个导致堆溢出的整数溢出漏洞。为了成功实现exploit ，我需要使用之前文章中介绍过的漏洞，用来获取whoopsie的ASLR偏移量。通过这两个漏洞，我可以用whoopsie用户获得一个shell，如[视频](https://v.youku.com/v_show/id_XNDQ4MzE0NDY4NA==.html?spm=a2hzp.8244740.0.0)中所演示。

## 简介

我需要一个whoopsie中的漏洞来完成CVE-2019-7307的漏洞攻击链，我发现了两个堆溢出漏洞，但是我只能成功利用第二个。我无法利用的第一个漏洞（CVE-2019-11476）在 whoopsie.c，第425行：

```
/* The length of this value string */
value_length = token_p - p;
if (value) `{`
    /* Space for the leading newline too. */
    value_pos = value_p - value;
    if (INT_MAX - (1 + value_length + 1) &lt; value_pos) `{`
        g_set_error (error,
                     g_quark_from_static_string ("whoopsie-quark"),
                     0, "Report value too long.");
        goto error;
    `}`
    value = g_realloc (value, value_pos + 1 + value_length + 1);
    value_p = value + value_pos;
    *value_p = 'n';
    value_p++;
`}` else `{`
```

这段代码在[parse_report](https://bazaar.launchpad.net/~daisy-pluckers/whoopsie/trunk/view/698/src/whoopsie.c#L354)中，当有新的错误报告写入`/var/crash`时调用它。问题是`value_length`和`value_pos`有int类型，我的PoC通过创建一个长度小于4GB的“字符串值”的错误报告。这将绕过[426行](https://bazaar.launchpad.net/~daisy-pluckers/whoopsie/trunk/view/698/src/whoopsie.c#L426)的边界检查，从而导致堆溢出。但我发现堆溢出的总是覆盖一个未映射的内存区域，导致立即发生`SIGSEGV`，所以我的结论是，这只是一个拒绝服务漏洞。

第二个漏洞是可利用的，它也存在于将新的错误报告写入`/var/crash`时调用的代码中，它在代码中的隐藏的比较深。错误报告在第656行被解析之后，在[第669行](https://bazaar.launchpad.net/~daisy-pluckers/whoopsie/trunk/view/698/src/whoopsie.c#L669)被转换为BSON格式。从漏洞报告的[讨论](https://bugs.launchpad.net/ubuntu/+source/whoopsie/+bug/1830865/comments/5)中可以看出，whoopsie正在使用一个非常老的libbson来进行转换。在`bson_ensure_space`有一个整数溢出漏洞:

```
int bson_ensure_space( bson *b, const int bytesNeeded ) `{`
    int pos = b-&gt;cur - b-&gt;data;
    char *orig = b-&gt;data;
    int new_size;

    if ( pos + bytesNeeded &lt;= b-&gt;dataSize )
        return BSON_OK;
```

`pos + bytesNeeded`可能溢出变为负数，这导致`bson_ensure_space`立即返回而没有分配更多的内存。更糟糕的是它返回了`BSON_OK`，因此调用者会认为内存分配成功。就像在我的PoC中那样，通过向BSON对象写入超过2GB的数据来触发这个漏洞，获得`SIGSEGV`是非常容易的。



## exploit

获取代码执行比较复杂，但实际上，这个漏洞是可以利用的。因为我无法控制缓冲区的大小，所以我无法控制它在内存中的位置。所以被分配到一个mmaped区域，这就排除了大部分常见的malloc利用技巧。

这个漏洞之所以可以被利用，是因为我能够破坏的内存区域包含一个内存分配器，称为[GSlice allocator](https://github.com/GNOME/glib/blob/2812219adb2d3e1208943f4bddf54b3a1c1e1ed3/glib/gslice.c)。GSlice allocator使用独立的“magazines”来提高分配效率。例如，它有一个16字节的块和一个32字节的块。magazine将大小一样未分配的块存储成单向链表，而内存开销为零。（大多数内存分配器会为元数据使用额外的存储空间，例如块的大小和prev / next指针。）我能够破坏的内存区域包含16字节的magazines，我的exploit是覆盖其中一个16字节块的下一个指针，这样分配器将在我选择的地址分配一个16字节块。在可利用性方面，有一些好消息和一些坏消息。让我们先从好消息开始：
1. 1.由于CVE-2019-15790，知道了whoopsie的ASLR偏移量，因此可以准确的计算目标地址应该在什么位置。
1. 2.我可以通过在/var/crash中创建一个文件来触发一个16字节的分配，这样我就可以控制何时将块分配到我选择的地址。
1. 3.mmap-ed区域中magazines的偏移量在每次运行时都是一致的，因此我知道需要破坏哪个偏移量。
坏消息是：
1. 1.堆溢出字符串不能包含任何小于0x20（空格字符）的字节。它还必须是一个有效的UTF8字符串。所以我只能用有效字符串的地址覆盖下一个指针。
1. 2.我分配的fake块将不包含有效的“next”指针，分配器肯定会在下次分配时崩溃。所以我只有一次机会去做一些事情。
1. 3.触发堆溢出需要在`/var/crash`中创建一个文件，该文件触发16字节的分配并从单向链表中取出一个块。所以我只能在所有块都被分配之前触发少量的溢出，并且不会留下任何损坏。
在某种程度上，我可以通过暴力破解的方法解决UTF8问题:只需多次运行exploit，直到ASLR生成一个有效的UTF8字符串地址。这种方法的问题是，我在上一篇文章中描述的exploit，但PID回收非常慢。它必须使用`bson_ensure_space`中的堆溢出来重新启动whoopsie，每次大约消耗15秒，而且由于whoopsie分配的PID存在不稳定性，它也只有大约1/3的正确率。因此，通常至少需要一分钟才能获得一组新的ASLR偏移量。一个代码地址的28位受ASLR影响。例如，在我的漏视频中，可以看到system函数被分配的一些地址是0x7ffad145c440、0x7f54e2d08440和0x7feeed303440。这些地址中有一个UTF8是有效的，并且不包含任何小于0x20字节的概率只有3.8%。如果我需要写多个地址，情况会变得很糟。代码地址的ASLR偏移量与堆偏移量无关，因此在同时运行中，两者都有效的机会太小了，导致exploit无法在合理的时间内完成。当我第一次开始研究这个exploit时，它需要几个小时才能完成，因为这种可能性很低。但是我发现了一个更好的解决方案，它将ASLR选择合适偏移量的概率提高到了32.6%，这意味着exploit通常在5分钟内完成。

### <a class="reference-link" name="%E5%86%85%E5%AD%98%E5%B8%83%E5%B1%80"></a>内存布局

下图显示了在处理新的错误报告时两个阶段中的内存布局：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securitylab.github.com/static/67eea23a72e725c5b64d514f5820d74f/whoopsie_memory_layout1.svg)

在第一阶段(parse_report)中，错误报告被mmap-ed（映射）到进程中。它包含一个2GB的字符串值，这个字符串被memcpy保存到一个malloced缓冲区中。然后对错误报告进行munmap-ed，在内存中留下一个缺口。在第二阶段(bsonify)，当2GB字符串被复制到bson对象时，这个缺口就被填补了。这就是我很幸运的地方，因为bson对象映射的内存区域的末尾与16字节GSlice magazines映射的区域的头部没有间隙。所以我可以使用堆溢出来破坏magazines。

### <a class="reference-link" name="16%E5%AD%97%E8%8A%82GSlice%20magazine%E5%B8%83%E5%B1%80"></a>16字节GSlice magazine布局

我的exploit中包含了16字节GSlice magazines占用空间的一些memory dumps演示。比如我前面提到的，magazines是一个单向链表，随时可以使用。以下是一个memory dumps的部分信息：

```
0x7f6f48006f40: 0x48006f50  0x00007f6f  0x00000000  0x00000000
0x7f6f48006f50: 0x48006f60  0x00007f6f  0x00000000  0x00000000
0x7f6f48006f60: 0x48006f80  0x00007f6f  0x00000000  0x00000000
0x7f6f48006f70: 0x6f8347c0  0x000055af  0x00000000  0x00000000
0x7f6f48006f80: 0x48006fa0  0x00007f6f  0x00000000  0x00000000
0x7f6f48006f90: 0x48006f70  0x00007f6f  0x00000000  0x00000000
0x7f6f48006fa0: 0x48006f90  0x00007f6f  0x00000000  0x00000000
0x7f6f48006fb0: 0x48006fc0  0x00007f6f  0x00000000  0x00000000
0x7f6f48006fc0: 0x48007200  0x00007f6f  0x00000000  0x00000000
```

如上所示，这些块在内存中并不总是连续的。比如上面的代码包括0x7f6f48006f80-&gt;0x7f6f48006fa0-&gt;0x7f6f48006f90-&gt;0x7f6f48006f70。源代码中的一条注释似乎表明这是一个经过深思熟虑的优化，称为“cache colorization”。好消息是，尽管块偏移看起来是随机的，但它们在每次运行时都是一致的。特别是地址最低的块始终位于偏移量0x6f40处。所以我的目标是覆盖偏移量0x6f40处的下一个指针，以便下一个要分配的块是fake。

### <a class="reference-link" name="mmap-ed%E5%8C%BA%E5%9F%9F%E7%9A%84ASLR%20entropy"></a>mmap-ed区域的ASLR entropy

我之前说过，代码地址（比如系统函数的地址）上的ASLR entropy是28位，这让地址成为有效UTF8字符串的概率非常低。但是mmap-ed地址的entropy更有用，可以在上面部分的内存信息中看到，在地址0x7f6f48006f40中，只有6f48受到ASLR的影响。因此，这些地址中有一个是有效字符串的几率要高很多。我计算出概率是32.6%。唯一需要注意的是，地址中间有一个零字节，所以我需要运行两次堆溢出来写一个地址。<br>
（第一个pass写入一个类似0x7F6F482121的地址，第二个pass写入一个稍短的字符串，用NULL成为地址中间的零字节。）因此，在GSlice分配器占用的mmap-ed区域内创建fake magazine块比较容易。

### <a class="reference-link" name="GSlice%20magazine%E5%88%97%E8%A1%A8%E9%80%86%E8%BD%AC%E8%A1%8C%E4%B8%BA"></a>GSlice magazine列表逆转行为

GSlice分配器的特性之一是，当magazine块被释放时，它不会被回收到分配时所在的列表中。可以在gslice.c的841行看到`thread_memory_magazine1_alloc`从弹出新块magazine1，在853行看到`thread_memory_magazine2_free`将它们回收到magazine2。这样做的结果是，单向链表被颠倒了。我可以使用这种行为来覆盖几乎任意地址的指针：通过覆盖magazine块的next指针，我可以获取下一个分配在我选择的地址处返回（fake）的块,当这个fake块被释放时，它的next指针将被前一个magazine块的地址覆盖。



## Exploit方案

到目前为止，这个漏洞让我有机会用指向我控制的内存的指针覆盖任意位置的内存。可以确定的是，这个程序很快就会崩溃，所以这个操作需要给我一个shell,我应该覆盖哪个指针?经过一些搜索之后，我发现了一个名为glib_worker_context的全局变量它包含一个名为source_lists的字段，这个字段通过间接引用指向一个名为GSourceFuncs的结构体:

```
struct _GSourceFuncs
`{`
  gboolean (*prepare)  (GSource    *source,
                        gint       *timeout_);
  gboolean (*check)    (GSource    *source);
  gboolean (*dispatch) (GSource    *source,
                        GSourceFunc callback,
                        gpointer    user_data);
  void     (*finalize) (GSource    *source); /* Can be NULL */

  /*&lt; private &gt;*/
  /* For use by g_source_set_closure */
  GSourceFunc     closure_callback;
  GSourceDummyMarshal closure_marshal; /* Really is of type GClosureMarshal */
`}`;
```

它包含函数指针!当一个事件发生时，这些指针就会被调用，比如在`/var/ crash`中写入一个新文件。因此，我需要做的就是使用该漏洞将`glib_worker_context-&gt;source_lists`替换为一个指向内存的指针，并用指向系统的指针填充fake GSourceFuncs。

这个方案的主要问题与之前一样:堆溢出只允许我编写有效的UTF8字符串，这将使我很难创建所有需要替换`sources_list`的fake堆对象。

### <a class="reference-link" name="memcpy"></a>memcpy

解决方法很简单，但我花了很长时间才弄明白！我已经多次说过，字符串必须是有效的UTF8，并且不能包含任何小于0x20的字节。0x20限制是有由`parse_report`检查：

```
value = g_malloc ((token_p - p) + 1);
memcpy (value, p, (token_p - p));
value[(token_p - p)] = '';
for (char *c = value; c &lt; value + (token_p - p); c++)
  if (*c &gt;= '' &amp;&amp; *c &lt; ' ')
    *c = '?';

```

首先，将2GB字符串memcpy到内存中。然后，在此bsonify阶段中小于0x20的任何字节都将替换为问号字符，直到后面才进行UTF8检查。当我第一次读到这段代码时，我立即得出结论，小于0x20的字符是不可能的。但我最终意识到，memcpy 2GB需要很长时间。因此，有一个时间窗，大概是半秒左右，在此期间，我可以完全控制字符串中的字节（内存布局图中左侧的框）。所以解决方案是将所有的fake堆对象放到malloced字符串中,在那里我可以完全控制所有字节,只需要我的fake magazine块重定向到它。而且malloced字符串的基地址正好位于内存中GSlice magazine下面(0x101000000)，所以如果GSlice地址满足UTF8要求，那么我也能够构造一个有效的指针到malloced区域。

### <a class="reference-link" name="%E9%87%8D%E5%AE%9A%E5%90%91%E5%88%B0fake%20heap"></a>重定向到fake heap

下图显示了如何在内存中创建fake对象：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securitylab.github.com/static/738b6e27f05dca12367304ae5dc037e6/whoopsie_memory_layout2.svg)

步骤如下：
1. 多次使用堆溢出在GSlice magazine中创建一个fake块，并使next指针指向将分配2GB字符串的内存区域。
1. 触发堆溢出，覆盖GSlice magazine中的fake块中的next指针。因为触发堆溢出的过程也会触发一个16字节的magazine分配，这也会导致fake块被分配和释放，所以下一个要分配的块将是malloced字符串中的第二个fake块。
1. 最后一次触发parse_report ，这样我的fake堆对象就被memcpy到malloc-ed字符串中。
1. 在`/var/crash`中快速触发一些文件事件，以便GSlice分配器在sources_list地址分配并释放一个块，这意味着它现在指向我的fake堆对象。这些事件是由一个单独的线程处理的，因此我可以memcpys时在无效字节没有被问号字符替换时触发它们。
1. 覆盖sources_list之后的下一个事件将会导致调用我的fake GSourceFuncs对象中的一个函数指针，并将我的fake GSource对象作为其第一个参数。我已经用指向系统函数指针填充了GSourceFuncs对象，并将字符串“/tmp/kev.sh”放在GSource对象中，所以接下来发生的事情就是调用我的脚本！
本文翻译自GitHub Security Lab
