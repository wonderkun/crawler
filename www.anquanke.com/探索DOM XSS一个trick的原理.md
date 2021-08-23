> 原文链接: https://www.anquanke.com//post/id/250538 


# 探索DOM XSS一个trick的原理


                                阅读量   
                                **56917**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t013c826c06c3c07bb5.png)](https://p2.ssl.qhimg.com/t013c826c06c3c07bb5.png)



前段时间P牛在他的星球发了一个XSS的小挑战（关于挑战的更多细节和解法见P牛的[博客](https://www.leavesongs.com)或者星球），我用的是DOM clobbering的方式完成。事后P牛给出了另一个trick，我看不懂但大受震撼，所以本文就来探讨一下这个trick的原理。

以下测试的步骤都是Win10 &amp; Chrome 最新版(92.0.4515.131) 下进行的；作者水平有限，如有错漏，还请各位师傅指正。



## 挑战

小挑战的代码如下

```
&lt;script&gt;
 const data = decodeURIComponent(location.hash.substr(1));;
 const root = document.createElement('div');
 root.innerHTML = data;

 // 这里模拟了XSS过滤的过程，方法是移除所有属性，sanitizer
 for (let el of root.querySelectorAll('*')) `{`
  let attrs = [];
  for (let attr of el.attributes) `{`
   attrs.push(attr.name);
  `}`
  for (let name of attrs) `{`
   el.removeAttribute(name);
  `}`
 `}`    
  document.body.appendChild(root); 

&lt;/script&gt;
```

可以看到这是个明显的DOM XSS，用户的输入会构成一个新div元素的子结点，但在插入body之前会被移除所有的属性。



## 解法

这里有两种解法，一种是绕过过滤的代码，另一种则是在过滤前就执行的代码

### <a class="reference-link" name="%E5%A4%B1%E8%B4%A5%E8%A7%A3%E6%B3%95"></a>失败解法

有一些常见的payload在这个挑战里是无法成功，例如`&lt;img src=x onerror=alert(1)&gt;`，原因也很明显，`onerror`在触发前被过滤掉了。

### <a class="reference-link" name="%E7%BB%95%E8%BF%87%E8%BF%87%E6%BB%A4"></a>绕过过滤

绕过过滤主要是为了使得Payload里面的属性不被清除，最终触发事件执行JS。具体做法正是DOM clobbering，但不是本文重点就不展开了，感兴趣的师傅可以看下Zedd师傅的[文章](https://blog.zeddyu.info/2020/03/04/Dom-Clobbering/)，P牛的[文章](https://www.leavesongs.com/PENETRATION/a-tour-of-tui-editor-xss.html)也有其他Payload，这里给出一个我的解法以供参考：

```
&lt;form tabindex=1 onfocus="alert(1);this.removeAttribute('onfocus');" autofocus=true&gt; &lt;img id=attributes&gt;&lt;img id=attributes name=z&gt;&lt;/form&gt;
```

### <a class="reference-link" name="%E8%BF%87%E6%BB%A4%E5%89%8D%E6%89%A7%E8%A1%8C%E4%BB%A3%E7%A0%81"></a>过滤前执行代码

另一种正确解法就是`&lt;svg&gt;&lt;svg onload=alert(1)&gt;`。看起来平平无奇，但是它可以在过滤代码执行以前，提前执行恶意代码。那为什么这个payload可以，上面img标签的payload却不能执行代码？而且如果只有单独一个svg标签也是不能正常执行的，像是`&lt;svg onload=alert(1)&gt;`。为更好地理解这个问题，需要稍微了解一下浏览器的渲染过程。



## DOM树的构建

我们知道JS是通过DOM接口来操作文档的，而HTML文档也是用DOM树来表示。所以在浏览器的渲染过程中，我们最关注的就是DOM树是如何构建的。

解析一份文档时，先由标记生成器做词法分析，将读入的字符转化为不同类型的Token，然后将Token传递给树构造器处理；接着标识识别器继续接收字符转换为Token，如此循环。实际上对于很多其他语言，词法分析全部完成后才会进行语法分析（树构造器完成的内容），但由于HTML的特殊性，树构造器工作的时候有可能会修改文档的内容，因此这个过程需要循环处理。

[![](https://p3.ssl.qhimg.com/t01d2d29f7a691529ed.png)](https://p3.ssl.qhimg.com/t01d2d29f7a691529ed.png)

（图源参考链接3）

在树构建过程中，遇到不同的Token有不同的处理方式。具体的判断是在`HTMLTreeBuilder::ProcessToken(AtomicHTMLToken* token)`中进行的。`AtomicHTMLToken`是代表Token的数据结构，包含了确定Token类型的字段，确定Token名字的字段等等。Token类型共有7种，`kStartTag`代表开标签，`kEndTag`代表闭标签，`kCharacter`代表标签内的文本。所以一个`&lt;script&gt;alert(1)&lt;/script&gt;`会被解析成3个不同种类的Token，分别是`kStartTag`、`kCharacter`和`kEndTag`。在处理Token的过程中，还有一个`InsertionMode`的概念，用于判断和辅助处理一些异常情况。

在处理Token的时候，还会用到`HTMLElementStack`，一个栈的结构。当解析器遇到开标签时，会创建相应元素并附加到其父节点，然后将token和元素构成的Item压入该栈。遇到一个闭标签的时候，就会一直弹出栈直到遇到对应元素构成的item为止，这也是一个处理文档异常的办法。比如`&lt;div&gt;&lt;p&gt;1&lt;/div&gt;`会被浏览器正确识别成`&lt;div&gt;&lt;p&gt;1&lt;/p&gt;&lt;/div&gt;`正是借助了栈的能力。

而当处理script的闭标签时，除了弹出相应item，还会暂停当前的DOM树构建，进入JS的执行环境。换句话说，在文档中的script标签会阻塞DOM的构造。JS环境里对DOM操作又会导致回流，为DOM树构造造成额外影响。



## svg标签

了解完上述内容后，回过头来看是什么导致了svg的成功，img的失败。

### <a class="reference-link" name="img%E5%A4%B1%E8%B4%A5%E5%8E%9F%E5%9B%A0"></a>img失败原因

先来找一下失败案例的原因，看看是在哪里触发了img payload中的事件代码。将过滤的代码注释以后，注入payload并打断点调试一下。

[![](https://p2.ssl.qhimg.com/t012a9ca434fd233675.png)](https://p2.ssl.qhimg.com/t012a9ca434fd233675.png)

可以发现即使代码已经执行到最后一步，但在没有退出JS环境以前依然还没有弹窗。

[![](https://p1.ssl.qhimg.com/t01381207e59fcba6d2.png)](https://p1.ssl.qhimg.com/t01381207e59fcba6d2.png)

此时再点击单步调试就会来到我们的代码的执行环境了。此外，这里还有一个细节就是`appendChild`被注释并不影响代码的执行，证明即使img元素没有被添加到DOM树也不影响相关资源的加载和事件的触发。

那么很明显，`alert(1)`是在页面上script标签中的代码全部执行完毕以后才被调用的。这里涉及到浏览器渲染的另外一部分内容： **在DOM树构建完成以后，就会触发`DOMContentLoaded`事件，接着加载脚本、图片等外部文件，全部加载完成之后触发`load`事件**。

同时，上文已经提到了，页面的JS执行是会阻塞DOM树构建的。所以总的来说，在script标签内的JS执行完毕以后，DOM树才会构建完成，接着才会加载图片，然后发现加载内容出错才会触发`error`事件。

可以在页面上添加以下代码来测试这一点。

```
window.addEventListener("DOMContentLoaded", (event) =&gt; `{`
    console.log('DOMContentLoaded')
  `}`);
  window.addEventListener("load", (event) =&gt; `{`
    console.log('load')
  `}`);
```

测试结果：

[![](https://p2.ssl.qhimg.com/t013e4f592110d8f875.png)](https://p2.ssl.qhimg.com/t013e4f592110d8f875.png)

那么失败的原因也很明显了，在DOM树构建以前，img的属性已经被sanitizer清除了，自然也不可能执行事件代码了。

### <a class="reference-link" name="svg%E6%88%90%E5%8A%9F%E5%8E%9F%E5%9B%A0"></a>svg成功原因

继续用断点调试svg payload为何成功。

在`root.innerHtml = data`断下来后，点击单步调试。

[![](https://p5.ssl.qhimg.com/t0187f843d63508b408.png)](https://p5.ssl.qhimg.com/t0187f843d63508b408.png)

神奇的事情发生了，直接弹出了窗口，点击确定以后，调试器才会走到下一行代码。而且，这个地方如果只有一个`&lt;svg onload=alert(1)&gt;`，那么结果将同img一样，直到script标签结束以后才能执行相关的代码，这样的代码放到挑战里也将失败（测试单个svg时要注意，不能像img一样注释掉`appendChild`那一行）。那为什么多了一个svg套嵌就可以提前执行呢？带着这个疑问，我们来看一下浏览器是怎么处理的。

<a class="reference-link" name="%E8%A7%A6%E5%8F%91%E6%B5%81%E7%A8%8B"></a>**触发流程**

上文提到了一个叫`HTMLElementStack`的结构用来帮助构建DOM树，它有多个出栈函数。其中，除了`PopAll`以外，大部分出栈函数最终会调用到`PopCommon`函数。这两个函数代码如下：

```
void HTMLElementStack::PopAll() `{`
  root_node_ = nullptr;
  head_element_ = nullptr;
  body_element_ = nullptr;
  stack_depth_ = 0;
  while (top_) `{`
    Node&amp; node = *TopNode();
    auto* element = DynamicTo&lt;Element&gt;(node);
    if (element) `{`
      element-&gt;FinishParsingChildren();
      if (auto* select = DynamicTo&lt;HTMLSelectElement&gt;(node))
        select-&gt;SetBlocksFormSubmission(true);
    `}`
    top_ = top_-&gt;ReleaseNext();
  `}`
`}`

void HTMLElementStack::PopCommon() `{`
  DCHECK(!TopStackItem()-&gt;HasTagName(html_names::kHTMLTag));
  DCHECK(!TopStackItem()-&gt;HasTagName(html_names::kHeadTag) || !head_element_);
  DCHECK(!TopStackItem()-&gt;HasTagName(html_names::kBodyTag) || !body_element_);
  Top()-&gt;FinishParsingChildren();
  top_ = top_-&gt;ReleaseNext();

  stack_depth_--;
`}`
```

当我们没有正确闭合标签的时候，如`&lt;svg&gt;&lt;svg&gt;`，就可能调用到`PopAll`来清理；而正确闭合的标签就可能调用到其他出栈函数并调用到`PopCommon`。这两个函数有一个共同点，都会调用栈中元素的`FinishParsingChildren`函数。这个函数用于处理子节点解析完毕以后的工作。因此，我们可以查看svg标签对应的元素类的这个函数。

```
void SVGSVGElement::FinishParsingChildren() `{`
  SVGGraphicsElement::FinishParsingChildren();

  // The outermost SVGSVGElement SVGLoad event is fired through
  // LocalDOMWindow::dispatchWindowLoadEvent.
  if (IsOutermostSVGSVGElement())
    return;

  // finishParsingChildren() is called when the close tag is reached for an
  // element (e.g. &lt;/svg&gt;) we send SVGLoad events here if we can, otherwise
  // they'll be sent when any required loads finish
  SendSVGLoadEventIfPossible();
`}`
```

这里有一个非常明显的判断`IsOutermostSVGSVGElement`，如果是最外层的svg则直接返回。注释也告诉我们了，最外层svg的`load`事件由`LocalDOMWindow::dispatchWindowLoadEvent`触发；而其他svg的`load`事件则在达到结束标记的时候触发。所以我们跟进`SendSVGLoadEventIfPossible`进一步查看。

```
bool SVGElement::SendSVGLoadEventIfPossible() `{`
  if (!HaveLoadedRequiredResources())
    return false;
  if ((IsStructurallyExternal() || IsA&lt;SVGSVGElement&gt;(*this)) &amp;&amp;
      HasLoadListener(this))
    DispatchEvent(*Event::Create(event_type_names::kLoad));
  return true;
`}`
```

这个函数是继承自父类`SVGElement`的，可以看到代码中的`DispatchEvent(*Event::Create(event_type_names::kLoad));`确实触发了load事件，而前面的判断只要满足是svg元素以及对`load`事件编写了相关代码即可，也就是说在这里执行了我们写的`onload=alert(1)`的代码。

<a class="reference-link" name="%E5%AE%9E%E9%AA%8C"></a>**实验**

我们可以将过滤的代码注释，并添加相关代码来验证这个事件的触发时间。

```
window.addEventListener("DOMContentLoaded", (event) =&gt; `{`
    console.log('DOMContentLoaded')
  `}`);
  window.addEventListener("load", (event) =&gt; `{`
    console.log('load')
  `}`);
```

同时，我们将注入代码也再套嵌一层`&lt;svg onload=console.log("svg0")&gt;&lt;svg onload=console.log("svg1")&gt;&lt;svg onload=console.log("svg2")&gt;`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d71d2582971cf3e7.png)

可以看到结果不出所料，最内层的svg先触发，然后再到下一层，而且是在DOM树构建完成以前就触发了相关事件；最外层的svg则得等到DOM树构建完成才能触发。

### <a class="reference-link" name="%E5%B0%8F%E7%BB%93"></a>小结

img和其他payload的失败原因在于sanitizer执行的时间早于事件代码的执行时间，sanitizer将恶意代码清除了。

套嵌的svg之所以成功，是因为当页面为`root.innerHtml`赋值的时候浏览器进入DOM树构建过程；在这个过程中**会触发非最外层svg标签的`load`事件，最终成功执行代码**。所以，sanitizer执行的时间点在这之后，无法影响我们的payload。



## details标签

在P牛的文章里还简单提到了一个跟svg标签类似的，可以在Tui Editor里使用的payload，也就是`&lt;details open ontoggle=alert(1)&gt;`；但我用小挑战的代码进行测试的时候却发现并不可行。所以，这里也值得探讨一下。

### <a class="reference-link" name="%E4%BA%8B%E4%BB%B6%E8%A7%A6%E5%8F%91%E6%B5%81%E7%A8%8B"></a>事件触发流程

首先触发代码的点是在`DispatchPendingEvent`函数里

```
void HTMLDetailsElement::DispatchPendingEvent(
    const AttributeModificationReason reason) `{`
  if (reason == AttributeModificationReason::kByParser)
    GetDocument().SetToggleDuringParsing(true);
  DispatchEvent(*Event::Create(event_type_names::kToggle));
  if (reason == AttributeModificationReason::kByParser)
    GetDocument().SetToggleDuringParsing(false);
`}`
```

而这个函数是在`ParseAttribute`被调用的

```
void HTMLDetailsElement::ParseAttribute(
    const AttributeModificationParams&amp; params) `{`
  if (params.name == html_names::kOpenAttr) `{`
    bool old_value = is_open_;
    is_open_ = !params.new_value.IsNull();
    if (is_open_ == old_value)
      return;

    // Dispatch toggle event asynchronously.
    pending_event_ = PostCancellableTask(
        *GetDocument().GetTaskRunner(TaskType::kDOMManipulation), FROM_HERE,
        WTF::Bind(&amp;HTMLDetailsElement::DispatchPendingEvent,
                  WrapPersistent(this), params.reason));

    ....

    return;
  `}`
  HTMLElement::ParseAttribute(params);
`}`
```

`ParseAttribute`正是在解析文档处理标签属性的时候被调用的。注释也写到了，分发toggle事件的操作是异步的。可以看到下面的代码是通过`PostCancellableTask`来进行回调触发的，并且传递了一个`TaskRunner`。

```
TaskHandle PostCancellableTask(base::SequencedTaskRunner&amp; task_runner,
                               const base::Location&amp; location,
                               base::OnceClosure task) `{`
  DCHECK(task_runner.RunsTasksInCurrentSequence());
  scoped_refptr&lt;TaskHandle::Runner&gt; runner =
      base::AdoptRef(new TaskHandle::Runner(std::move(task)));
  task_runner.PostTask(location,
                       WTF::Bind(&amp;TaskHandle::Runner::Run, runner-&gt;AsWeakPtr(),
                                 TaskHandle(runner)));
  return TaskHandle(runner);
`}`
```

跟进`PostCancellableTask`的代码则会发现，回调函数（被封装成task）正是通过传递的`TaskRunner`去派遣执行。

清楚调用流程以后，就可以思考，为什么无法触发这个事件呢？最大的可能性，就是在任务交给`TaskRunner`以后又被取消了。因为是异步调用，而且`PostCancellableTask`这个函数名也暗示了这一点。

### <a class="reference-link" name="%E5%AE%9E%E9%AA%8C%E9%AA%8C%E8%AF%81"></a>实验验证

可以做一个实验来验证，修改小挑战代码，将sanitizer部分延时执行。

```
const data = decodeURIComponent(location.hash.substr(1));;
 const root = document.createElement('div');
 root.innerHTML = data;
 setTimeout( () =&gt; `{`
     for (let el of root.querySelectorAll('*')) `{`
      let attrs = [];
      for (let attr of el.attributes) `{`
       attrs.push(attr.name);
      `}`
      for (let name of attrs) `{`
       el.removeAttribute(name);
      `}`
     `}`    
     document.body.appendChild(root)
 `}` , 2000)
```

**代码修改前：**

[![](https://p5.ssl.qhimg.com/t0130889a4929691e83.png)](https://p5.ssl.qhimg.com/t0130889a4929691e83.png)

执行失败。

**代码修改后：**

[![](https://p2.ssl.qhimg.com/t017e2c3c133ef779c0.png)](https://p2.ssl.qhimg.com/t017e2c3c133ef779c0.png)

可以看到，确实成功执行了事件代码。

那么回过头来想一下，为什么P牛测试Tui的时候直接成功，我却在修改前的挑战代码中失败？看一下Tui的处理这部分内容的相关代码。[https://github.com/nhn/tui.editor/blob/48a01f5/apps/editor/src/sanitizer/htmlSanitizer.ts](https://github.com/nhn/tui.editor/blob/48a01f5/apps/editor/src/sanitizer/htmlSanitizer.ts)

```
export function sanitizeHTML(html: string) `{`
  const root = document.createElement('div');

  if (isString(html)) `{`
    html = html.replace(reComment, '').replace(reXSSOnload, '$1');
    root.innerHTML = html;
  `}`

  removeUnnecessaryTags(root);
  leaveOnlyWhitelistAttribute(root);

  return finalizeHtml(root, true) as string;
`}`
```

`sanitizeHTML`函数是处理用户输入的部分。比起挑战的代码，这里多了正则过滤，移除黑名单标签(removeUnnecessaryTags)，不过不会移除所有标签而是留下了部分白名单标签(leaveOnlyWhitelistAttribute)。最神奇的地方来了，**details标签也是黑名单的一员**，这也是我一开始无法理解为何这个payload能成功执行的原因。但现在我们理清楚调用流程以后，可以有一个大胆的猜测：**正是因为details在黑名单里，所以被移除以后其属性没有被直接修改，所以事件依然在队列中没有被取消。**

再进行一个实验来验证，对挑战的代码做一些修改，增加移除标签的代码。

```
const data = decodeURIComponent(location.hash.substr(1));;
 const root = document.createElement('div');
 root.innerHTML = data;

 let details = root.querySelector("details")
 root.removeChild(details)

 for (let el of root.querySelectorAll('*')) `{`
  let attrs = [];
  for (let attr of el.attributes) `{`
   attrs.push(attr.name);
  `}`
  for (let name of attrs) `{`
   el.removeAttribute(name);
  `}`
 `}`
```

[![](https://p4.ssl.qhimg.com/t016f28894abf1abd7d.png)](https://p4.ssl.qhimg.com/t016f28894abf1abd7d.png)

成功执行了代码！

### <a class="reference-link" name="%E5%B0%8F%E7%BB%93"></a>小结

所以我们可以得到结论，**details标签的toggle事件是异步触发的，并且直接对details标签的移除不会清除原先通过属性设置的异步任务**。



## 思考

对于DOM XSS，我们是通过操作DOM来引入代码，但由于浏览器的限制，我们无法像这样`root.innerHTML = "&lt;script&gt;..&lt;/script&gt;"` 直接执行插入的代码，因此，一般需要通过事件触发。通过上面的例子，可以发现依据事件触发的时机能进一步区分DOM XSS：
1. 立即型，操作DOM时触发。套嵌的svg可以实现
1. 异步型，操作DOM后，异步触发。details可以实现
1. 滞后型，操作DOM后，由其他代码触发。img等常见payload可以实现
从危害来看，明显是1&gt;2&gt;3，特别是1，可以直接无视后续的sanitizer操作。因此，师傅们可以研究浏览器的相关代码，通过这个方向来找到杀伤力更大的第一种或第二种类型的payload。



## 参考链接
1. [一次对 Tui Editor XSS 的挖掘与分析](https://www.leavesongs.com/PENETRATION/a-tour-of-tui-editor-xss.html)
1. [从Chrome源码看JavaScript的执行（上）](https://xz.aliyun.com/t/2480)
1. [浏览器的工作原理：新式网络浏览器幕后揭秘](https://www.html5rocks.com/zh/tutorials/internals/howbrowserswork)
1. [浏览器内核原理—Chromium Blink Html解析(2)](https://zhuanlan.zhihu.com/p/50628909)
1. [从Chrome源码看事件循环](https://www.yinchengli.com/2018/11/04/chrome-event-loop/comment-page-1/)