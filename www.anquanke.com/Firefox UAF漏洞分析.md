> 原文链接: https://www.anquanke.com//post/id/181345 


# Firefox UAF漏洞分析


                                阅读量   
                                **196069**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者zerodayinitiative，文章来源：zerodayinitiative.com
                                <br>原文地址：[www.zerodayinitiative.com/blog/2019/7/1/the-left-branch-less-travelled-a-story-of-a-mozilla-firefox-use-after-free-vulnerability](www.zerodayinitiative.com/blog/2019/7/1/the-left-branch-less-travelled-a-story-of-a-mozilla-firefox-use-after-free-vulnerability)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t016e0a143d8b185f4a.png)](https://p4.ssl.qhimg.com/t016e0a143d8b185f4a.png)



## 0x00 前言

2018年12月，Mozila通过[mfsa2018-29](https://www.mozilla.org/en-US/security/advisories/mfsa2018-29/#CVE-2018-18492)发布了Firefox 64，修复了多个安全问题，其中就包含CVE-2018-18492，这是一个与`select`元素有关的UAF（use-after-free，释放后重用）漏洞，最早由Nils发现并报告。[之前](https://www.zerodayinitiative.com/blog/2017/6/26/use-after-silence-exploiting-a-quietly-patched-uaf-in-vmware)我们已经讨论过UAF问题，也看到厂商采取了多种[保护措施](https://www.blackhat.com/docs/us-15/materials/us-15-Gorenc-Abusing-Silent-Mitigations-Understanding-Weaknesses-Within-Internet-Explorers-Isolated-Heap-And-MemoryProtection-wp.pdf)想消除这些问题。但直到目前为止，我们还是经常能在web浏览器中发现与UAF相关的漏洞，因此理解这些问题对查找及修复漏洞来说至关重要。在本文中，我们将与大家分享这个UAF漏洞以及相关补丁的具体细节。



## 0x01 触发漏洞

我们可以使用如下PoC触发该漏洞：

[![](https://p4.ssl.qhimg.com/t018094bf52ca2daf31.png)](https://p4.ssl.qhimg.com/t018094bf52ca2daf31.png)

图1. PoC

在存在漏洞Firefox版本中运行该PoC，我们可以看到crash时的栈跟踪状态如下：

[![](https://p0.ssl.qhimg.com/t0132d7f806fb9f657d.png)](https://p0.ssl.qhimg.com/t0132d7f806fb9f657d.png)

图2. 崩溃时的栈跟踪状态

从图中可知，当解析填充`0xe5e5e5e5`的某个内存地址时，会出现read access violation（读取访问冲突）。`0xe5e5e5e5`是`jemalloc`用来“污染”已释放内存的一个值。这里的“污染”指的是以一种可识别模式来填充已被释放的内存，这样便于分析。正常情况下，我们选择的填充模式不要对应于可访问的地址，这样任何尝试从已填充内存中解析值的操作（比如UAF）都会导致crash。



## 0x02 漏洞分析

PoC包含6行代码，让我们来逐行分析：
- 创建一个`div`元素
- 创建一个`option`元素
- 将`option`元素附加到`div`元素，现在这个`div`元素是`option`元素的父节点
- 将`DOMNodeRemoved`事件监听器添加到`div`元素中。这意味着如果`option`节点被移除，就会调用我们在这里添加的函数
- 创建一个`select`元素
这里再深入分析一下：

当使用JavaScript创建`select`元素时，`xul.dll!NS_NewHTMLSelectElement`函数就会获得控制权，该函数会为这个`select`元素分配大小为`0x188`字节的一个对象：

[![](https://p0.ssl.qhimg.com/t01dc0e976f214420cd.png)](https://p0.ssl.qhimg.com/t01dc0e976f214420cd.png)

图3. `xul.dll!NS_NewHTMLSelectElement`函数

如上所示，在代码底部会跳转至`mozilla::dom::HTMLSelectElement::HTMLSelectElement`函数。

[![](https://p3.ssl.qhimg.com/t0137a696e43cee6798.png)](https://p3.ssl.qhimg.com/t0137a696e43cee6798.png)

图4. `mozilla::dom::HTMLSelectElement::HTMLSelectElement`函数

在该函数中会初始化新分配对象的各种字段。需要注意的是，这里也会分配大小为`0x38`字节的另一个对象，将其初始化为`HTMLOptionsCollection`对象。因此，每个`Select`元素默认情况下都会对应一个options collection（选项集合）。让我们看一下PoC的最后一行。
- 将第二行创建的`option`元素移动到`select`元素的options collection中
在JavaScript中执行该操作将导致`mozilla::dom::HTMLOptionsCollection::IndexedSetter`函数被调用（大家可以在图2的栈跟踪状态中看到该函数被调用）。

[![](https://p1.ssl.qhimg.com/t01bbfe83d4069e601b.png)](https://p1.ssl.qhimg.com/t01bbfe83d4069e601b.png)

图5. IDA中观察到的程序逻辑

这里浏览器会执行一些检查操作。比如，如果选项索引值大于当前options collection的长度值，那么就会调用`mozilla::dom::HTMLSelectElement::SetLength`函数来扩充options collection容量。在PoC中，这个长度值为为`0`（参考图1第6行的`[0]`）。然后浏览器会进入图5的红色方框处的检测逻辑。如果待设置的索引值不等于options collection的选项数，那么就会进入右分支。在PoC中，我们使用的索引值为`0`，而选项数也为0，因此会执行左分支。因此浏览器会调用`nsINode::ReplaceOrInsertBefore`函数，如下红框所示：

[![](https://p1.ssl.qhimg.com/t0179aa1df1c9fcabbe.png)](https://p1.ssl.qhimg.com/t0179aa1df1c9fcabbe.png)

图6. 调用`nsINode::ReplaceOrInsertBefore`函数

在`nsINode::ReplaceOrInsertBefore`函数中，浏览器会调用`nsContentUtils::MaybeFireNodeRemoved`函数，通知父节点关于子节点移除的相关事件（如果父节点在监听这类事件）。

[![](https://p3.ssl.qhimg.com/t018a9cd5db28294d35.png)](https://p3.ssl.qhimg.com/t018a9cd5db28294d35.png)

图7. 调用`nsContentUtils::MaybeFireNodeRemoved`函数

由于我们在PoC第4行（参考图1）中，在`div`元素上设置了`DOMNodeRemoved`事件监听器，因此这里浏览器就会触发我们设置的函数。在这个函数中，第一个`sel`变量会被设置为`0`，该操作会移除对`select`元素的最后一个引用。接下来，函数会创建一个巨大的数组缓冲区，这会给内存带来较大负担，触发垃圾回收机制（garbage collector）。此时会释放`select`元素对象，因为已经没有关于该对象的任何引用。现在被释放的内存已被`0xe5e5e5e5`填充。最后，函数会调用`alert`来[flush挂起的异步任务](https://developer.mozilla.org/en-US/docs/Web/JavaScript/EventLoop#Never_blocking)。从`nsContentUtils::MaybeFireNodeRemoved`函数返回后，被释放的`select`对象会被用来读取指针，触发read access violation：

[![](https://p2.ssl.qhimg.com/t01490061e2181f19a8.png)](https://p2.ssl.qhimg.com/t01490061e2181f19a8.png)

图8. 触发Read Access Violation

这里需要注意的是，如果浏览器执行的是右分支，那么还是会调用同一个函数（`nsINode::ReplaceOrInsertBefore`），但在调用该函数之前，会使用`AddRef`函数来增加`select`对象的引用计数。如果是这样操作，就不会出现UAF问题：

[![](https://p1.ssl.qhimg.com/t0107c7e79fc2eaef9b.png)](https://p1.ssl.qhimg.com/t0107c7e79fc2eaef9b.png)

图9. 通过`AddRef`函数避免出现UAF问题



## 0x03 补丁分析

Mozilla通过[d4f3e119ae841008c1be59e72ee0a058e3803cf3](https://hg.mozilla.org/mozilla-central/rev/d4f3e119ae841008c1be59e72ee0a058e3803cf3)改动修复了这个漏洞。这里最主要的改动是修改options collection中对`select`元素的弱引用逻辑，替换成强引用：

[![](https://p0.ssl.qhimg.com/t01f1db78fa2e113ac4.png)](https://p0.ssl.qhimg.com/t01f1db78fa2e113ac4.png)

图10. 补丁细节



## 0x04 总结

虽然UAF是大家都比较熟悉的一个问题，但在许多浏览器中依然存在。在几个月之前，有攻击者成功利用了Google Chrome浏览器中的[UAF漏洞](https://security.googleblog.com/2019/03/disclosing-vulnerabilities-to-protect.html)。UAF漏洞也不局限于浏览器，Linux内核之前也推出过一个[补丁](https://bit-tech.net/news/tech/software/linux-hit-by-use-after-free-vulnerability/1/)，用来修复由UAF导致的拒绝服务问题。澄清UAF触发原理是检测这类漏洞的关键所在。与缓冲区溢出问题一样，我们认为软件中无法完全避免UAF。然而，通过正确的编程以及安全的开发实践，在未来我们可以进一步消除、或者缓解UAF所带来的影响。

大家可以关注[推特](https://twitter.com/thezdi)了解最新的漏洞利用技术及安全补丁情况。
