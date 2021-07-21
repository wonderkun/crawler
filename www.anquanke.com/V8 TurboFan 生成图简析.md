> 原文链接: https://www.anquanke.com//post/id/240011 


# V8 TurboFan 生成图简析


                                阅读量   
                                **131996**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01b51b7a9507020836.png)](https://p5.ssl.qhimg.com/t01b51b7a9507020836.png)



## 一、简介

v8 turbolizer 有助于我们分析 JIT turbofan 的优化方式以及优化过程。但我们常常对于 turbolizer 生成的 IR 图一知半解，不清楚具体符号所代表的意思。以下为笔者阅读相关代码后所做的笔记。



## 二、TurboFan Json 格式
<li>
`--trace-turbo` 参数将会生成一个 JSON 格式的数据。通过在 turbolizer 上加载该 JSON，可以得到一个这样的IR图：<br>[![](https://p2.ssl.qhimg.com/t01ca12342d60aa8fd9.png)](https://p2.ssl.qhimg.com/t01ca12342d60aa8fd9.png)
</li>
<li>其中，该 JSON 的格式如下：
<pre><code class="lang-json hljs">`{`
    "function": "opt_me",
    "sourcePosition": 109,
    "source": [js source],
    "phases": [
        `{`
            "name": "Typed",
            "type": "graph",
            "data": `{`
                "nodes": [
                    [...],
                    `{`
                        "id": 20,
                        "label": "FrameState[INTERPRETED_FRAME, 11, Ignore, 0x1a5acd4aa5e9 &lt;SharedFunctionInfo opt_me&gt;]",
                        "title": "FrameState[INTERPRETED_FRAME, 11, Ignore, 0x1a5acd4aa5e9 &lt;SharedFunctionInfo opt_me&gt;]",
                        "live": true,
                        "properties": "Idempotent, NoRead, NoWrite, NoThrow, NoDeopt",
                        "pos": 178,
                        "opcode": "FrameState",
                        "control": false,
                        "opinfo": "5 v 0 eff 0 ctrl in, 1 v 0 eff 0 ctrl out",
                        "type": "Internal"
                    `}`,
                    [...]
                ],
                "edges": [
                    `{`
                        "source": 100,
                        "target": 101,
                        "index": 0,
                        "type": "control"
                    `}`,
                    [...]
                ]
            `}`
        `}`,
        [...]
    ],
    "nodePositions": `{`
        [...]
    `}`
`}`
</code></pre>
简单的概括一下，就是：
<ul>
- function： 函数名称
- sourcePosition：代码的起始位置。
- source： 当前 turboFan 优化的 JS 代码
<li>phases： turboFan 的各个优化阶段
<ul>
<li>优化阶段1
<ul>
- name： 当前优化阶段的名称
- type：显示的形式，是 `graph` IR 图还是 文本。
<li>data： 当前阶段真正存放的结点与边的数据。
<ul>
<li>nodes： 结点数据
<ul>
<li>结点1
<ul>
- id: 结点ID，通常是一个数字
- label：结点标签
- title：结点主题
- live： 当前结点是否是活结点，为 true / false
- properties：当前结点的属性
- pos：暂且不说
<li>opcode：当前结点的操作码，例如`End`
</li>
- control：当前是否是控制结点，为 true / false
<li>opinfo：具体的结点信息，通常表示当前结点的**ValueInputCount、EffectInputCount、ControlInputCount、ValueOutputCount、EffectOutputCount、ControlOutputCount**。<br><blockquote>
表示方式如下：
“\&lt;ValueInputCount\&gt; v
<pre><code class="hljs xml">\&lt;EffectInputCount\&gt;    eff
\&lt;ControlInputCount\&gt;   ctrl in,
\&lt;ValueOutputCount\&gt;    v
\&lt;EffectOutputCount\&gt;   eff
\&lt;ControlOutputCount\&gt;  ctrl out"
</code></pre>
例如：”0 v 1 eff 1 ctrl in, 0 v 1 eff 0 ctrl out”
</blockquote>
</li><li>边1
<ul>
- source：边的源节点 ID
- target：边的目标节点ID
- index：当前边连接到目标节点的哪个输入
- type：当前边的类型，例如 control、value、effect等等


## 三、Node

### <a class="reference-link" name="a.%20%E5%B1%9E%E6%80%A7%E8%AF%B4%E6%98%8E"></a>a. 属性说明

以下是截取出的一个 Node 示例：

```
`{`
    "id": 128,
    "label": "LoadField[+16]",
    "title": "LoadField[tagged base, 16, Internal, kRepTaggedPointer|kTypeAny, PointerWriteBarrier]",
    "live": true,
    "properties": "NoWrite, NoThrow, NoDeopt",
    "pos": 388,
    "opcode": "LoadField",
    "control": false,
    "opinfo": "1 v 1 eff 1 ctrl in, 1 v 1 eff 0 ctrl out",
    "type": "Internal"
`}`
```

对应的结点如下：

[![](https://p5.ssl.qhimg.com/t0116763f57116d5dea.png)](https://p5.ssl.qhimg.com/t0116763f57116d5dea.png)

一一对应以下便可以看出，其中的 id、label、title、properties、opinfo 以及 type 均显现在图中。

而 live、pos、opcode 以及 control 字段则是给 turbolizer.js 使用的。

> 注意到上图中的 “Inplace update in phase: Typed”，其中的 phase 则是 turbolizer.js 动态分析出的，不在 JSON 中记录。

### <a class="reference-link" name="b.%20%E9%A2%9C%E8%89%B2"></a>b. 颜色

我们可以注意到，IR图中的结点都有颜色，其中颜色貌似符合某种规律。

通过查阅 turbolizer.js 以及 在线 turbolizer 的 css 代码，turbolizer 将结点分为了以下几种结点，并设置了不同的颜色加以区分：
<li>Control 结点：对于那些控制结点， 即 JSON 数据中 control 字段为 true 的结点，其颜色为**黄色**。[![](https://p0.ssl.qhimg.com/t01feab6eb5527f3451.png)](https://p0.ssl.qhimg.com/t01feab6eb5527f3451.png)
</li>
<li>Input 结点：那些 opcode 为 Parameter 或 Constant 结点，其颜色为**浅蓝色**。[![](https://p0.ssl.qhimg.com/t011a5232f23eff7c77.png)](https://p0.ssl.qhimg.com/t011a5232f23eff7c77.png)
</li>
<li>Live 结点（**这其实不能算一类结点**）：即 live 字段为 true 的结点。其反向结点——DeadNode——的颜色会在原先颜色的基础上进行浅色化处理，例如以下图片。图片中的两个结点其类型相同，所不同的是左边的结点是 Dead，右边结点是 Live。[![](https://p5.ssl.qhimg.com/t010d136faec91a4712.png)](https://p5.ssl.qhimg.com/t010d136faec91a4712.png)
</li>
<li>JavaScript结点：那些 opcode 以 **JS** 开头的结点，其颜色为**橙红色**。[![](https://p3.ssl.qhimg.com/t01bb3630fc2483e782.png)](https://p3.ssl.qhimg.com/t01bb3630fc2483e782.png)
</li>
<li>Simplified 结点：那些 opcode 包含 **Phi、Boolean、Number、String、Change、Object、Reference、Any、ToNumber、AnyToBoolean、Load、Store**，但**不是 JavaScript类型**的结点。其颜色如下所示：[![](https://p0.ssl.qhimg.com/t01ca703850da3a4082.png)](https://p0.ssl.qhimg.com/t01ca703850da3a4082.png)
</li>
<li>Machine 结点：除了上述四种结点以外，剩余的结点。颜色如下所示：[![](https://p1.ssl.qhimg.com/t013b48eed09e81323f.png)](https://p1.ssl.qhimg.com/t013b48eed09e81323f.png)
</li>


## 四、Edge

Edge 中的 Type 共有五种，分别是 **value**、**context**、**frame-state**、**effect**、**control** 以及最后一个 unknown。

以下是这些边的一些例子：

### <a class="reference-link" name="a.%20value%20%E8%BE%B9"></a>a. value 边

对于该边：

```
`{`
    "source": 80,
    "target": 83,
    "index": 4,
    "type": "value"
`}`
```

其边的视觉效果如下：

[![](https://p2.ssl.qhimg.com/t010246f36d3f1a1aa9.png)](https://p2.ssl.qhimg.com/t010246f36d3f1a1aa9.png)

可以看到，对于 **Value 边**来说，是一条**实线**。

### <a class="reference-link" name="b.%20context%20%E8%BE%B9"></a>b. context 边

对于该边：

```
`{`
    "source": 4,
    "target": 49,
    "index": 3,
    "type": "context"
`}`
```

视觉效果如下：

[![](https://p4.ssl.qhimg.com/t013584fbd62cfe222c.png)](https://p4.ssl.qhimg.com/t013584fbd62cfe222c.png)

可以看到，**Context边**也是一条**实线**。但在当前这个例子中，由于 Context 边只会由 `Parameter[%context#4]`结点发出，因此**不会与 Value 边混淆**。

这里需要注意一下，Context 边只会存在于某个 Context 结点发出的所有边，即不会出现结点既发出 Context 边又发出 Value 边的情况。

> 如果有还请指正。

### <a class="reference-link" name="c.%20frame-state%20%E8%BE%B9"></a>c. frame-state 边

例子：

```
`{`
    "source": 50,
    "target": 49,
    "index": 4,
    "type": "frame-state"
`}`
```

视觉效果：

[![](https://p1.ssl.qhimg.com/t01bf5e5c5eeaf4a97d.png)](https://p1.ssl.qhimg.com/t01bf5e5c5eeaf4a97d.png)

可以看到，对于一条 **frame-state 边**，其视觉效果是一条 **疏虚线**。

frame-state 边一定是由一个 FrameState 结点发出的。

> 上图的另一条虚线是**密虚线**，所不同的是虚线的**疏密程度**。

### <a class="reference-link" name="d.%20effect%20%E8%BE%B9"></a>d. effect 边

例子：

```
`{`
    "source": 114,
    "target": 49,
    "index": 5,
    "type": "effect"
`}`
```

视觉效果：

[![](https://p0.ssl.qhimg.com/t0139c5a37edf79045f.png)](https://p0.ssl.qhimg.com/t0139c5a37edf79045f.png)

即 **effect 边**的显示效果是 **密虚线**。

### <a class="reference-link" name="e.%20control%20%E8%BE%B9"></a>e. control 边

例子：

```
`{`
    "source": 31,
    "target": 49,
    "index": 6,
    "type": "control"
`}`
```

视觉效果：

[![](https://p5.ssl.qhimg.com/t0173893e8bebfc82b3.png)](https://p5.ssl.qhimg.com/t0173893e8bebfc82b3.png)

注意：与 value 边相同，**control 边**的显示效果也是一条**实线**。这意味着单单只看 IR 图的话，是无法将 Control 边和 Value 边区分开的。



## 五、参考的源码
- v8/tools/turbolizer/build/turbolizer.js
- v8/src/compiler/graph-visualizer.cc