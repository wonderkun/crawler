> 原文链接: https://www.anquanke.com//post/id/169829 


# 高中生，一年，从 0 到 0day 的秘密


                                阅读量   
                                **443261**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">13</a>
                                </b>
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者ccc，文章来源：media.ccc.de
                                <br>原文地址：[https://media.ccc.de/v/35c3-9657-from_zero_to_zero_day](https://media.ccc.de/v/35c3-9657-from_zero_to_zero_day)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01bb7d8e3e093b4c2c.png)](https://p1.ssl.qhimg.com/t01bb7d8e3e093b4c2c.png)



编译：360代码卫士团队

演讲稍长，但绝对有料好看，甚至值得一读再读~



## 我是谁？

[![](https://p2.ssl.qhimg.com/t01ee2e83a90dce5f61.png)](https://p2.ssl.qhimg.com/t01ee2e83a90dce5f61.png)

大家好，我叫 Jonathan，现在18岁，是一名计算机科学和数学专业的学生，对漏洞研究感兴趣，也是微软 MSRC-IL 的一名安全研究员。我也打 CTF 比赛，所在团队是 Perfect Blue。

我在去年才开始接触安全研究，这次演讲的第一部分主要说一下我在一年中都学了什么以及是如何学的；第二部分说一下我是如何从 ChakraCore 中找到第一个 0day 漏洞（JIT类型混淆漏洞）的。可能你刚刚接触安全领域，只知道一些基础的编程知识，但可能你也能听懂。虽然我会讲很多代码，但还好，不是太复杂。最后，我们看下演示。好的，我们开始吧。



## 知识和实践准备

我为什么要研究漏洞？对我而言，漏洞就像是一个谜，非常具有挑战性的东西。我们必须找到开发人员未考虑到的一些缺陷。至少对我而言这很具有挑战性，也非常有意思。我觉得挖漏洞是个很棒的事情。

那么，什么是漏洞呢？关于漏洞的定义很多。当你想了解某件事的时候，你就会去维基百科上搜索。上面有很多不同的解释，而且有一些看起来很古怪，比如有一个解释是这么说的，“某资产无法抵御威胁攻击动作的可能性”。我不懂它到底说的是什么。我的理解是，漏洞就是程序中出现的各种缺陷，你可以用来改变程序的控制流。这就是我对漏洞的理解，但定义没有告诉我如何找到一个漏洞。

那么，我们怎么才能找到漏洞呢？我当时开始找漏洞时有一些编程基础，我不是写程序最优秀的开发，也就是“还行”的水平，知道C语言、汇编语言，学了一些操作系统内部知识，了解操作系统是会如何运作的，能读一些 python 代码。所以我虽然并不是最优秀的开发，但我具备一些相关知识。比如，我从一本很不错的希伯来语书中了解了一些 C++ 语言的知识，以便我真正地开展漏洞研究。

下一步，我了解了一些漏洞的基础知识，如一些基础的漏洞类型像典型的堆缓冲溢出问题、整数溢出等。之后我就开始通过模拟演习开始实践自己所学的知识。模拟演习是可以在线下解决的安全挑战，这些挑战问题包括找到漏洞并利用它。最开始的时候我败得一塌糊涂，但随着时间的推移，我认为失败了也没关系，因为我看了解决方案、write-up，我知道了如何写解决方案，如何解决问题。所以最开始失败没关系，因为我们每个人都是这样过来的。之后我开始参加 CTF 比赛。

> CTF 比赛要求团队作战，这就是我找到团队成员的方式，我们通过 CTF 相识，然后一起打比赛。有时候我们输得很惨，有时候我们打得不错进了决赛，还一起周游世界，因为有时候赛事主办方会支付差旅费，哈哈。我们去了很多很酷的地方，真的很爽。

我认为 CTF 比赛是进入安全领域的一个很好的方式。

之后我决定“潜入深水区”。一旦你了解了基础知识之后，不要在“浅水区”停留太长的时间，这一点很重要，我们要给自己一些挑战。刚开始我害怕失败，但是随着时间的流逝，我想明白了，失败也没什么可怕的。失败后我能找到解决问题的技术。所以我认为这一点很重要：不要害怕失败，即使失败了，我们也能从别人的解决方案中学到东西。

> LiveOverflow 发的一条推文说得很好：学到基础后，尽快去做自己不懂的更难的事；不断地接触自己不懂的事情，然后重新来看自以为懂但实际上不懂的事情；然后从各种资源了解信息，学习从多个角度和方向一步步解决问题。

我认为这样做很重要。LiveOverFlow 也有 YouTube 频道，我也在看，讲的是漏洞和安全问题。推荐大家也可以关注他。

我具备一些知识后，通过 CTF 比赛、模拟演示等不断实践、实践、再实践。不断实践、自己解决问题很重要，因为这样你才能知道解决问题的技巧，然后再自己解决遇到的问题。一些漏洞是有特定模式的，要了解这些模式，你就需要多看几次。发现这些模式的一种好方法就是不断解决问题。这也是我为什么喜欢解决真实漏洞问题的原因，很多网站提供不少这样的途径，比如 Project Zero 的 0day 项目，你可以读取一些漏洞信息等。

我还发现CTF 和真实环境中的漏洞之间存在很大的关联，它们同时存在于 CTF 和真实世界中。漏洞实际上就是由 bug引起的。你在真正着手开始进行研究时遇到的最大问题就是代码库过于庞大（因此你可能会头大）。但实际上即使代码框架很庞大，但漏洞还是在具体某处。所以，不要发愁看代码库，因为漏洞很可能就恰好在你开始查看具体的某些代码时出现。之后你可以开始尝试解决问题，即开始了解真正的代码库。

经过一些实践后，我在想我们如何发现漏洞呢？当我们开始真正重复解决问题、实践的过程后，我发现漏洞研究就是关于找到 bug，而我们是通过读代码实现这个目标的。因此，审计代码很重要，因为我们想从中找到漏洞，对吧？而这需要我们真正审计代码，需要实践。因此实践在漏洞研究中起着非常重要的作用。因此我们搞砸了的时候可能就是更接近找到漏洞的时候。因此我认为实践很重要。

那我是如何发现漏洞的？我之前说过漏洞存在模式，而模式是通过时间的积累发现的。但我并没有研究很长的时间，只有短短的一年，那么我是如何发现漏洞的？实际上就是通过不断实践发现的。像我之前说过的那样，多实践能弥补开始晚的问题。我发现漏洞里面有一些模式，比如编程错误像整数溢出或类型混淆问题，这些问题实际上是存在的，因为人总是会犯错的。人类会犯错，我们并不是完美的。下面的代码就是一个很好的例子。

[![](https://p3.ssl.qhimg.com/t01210c4477aaf4b579.png)](https://p3.ssl.qhimg.com/t01210c4477aaf4b579.png)

第3行有一个整数溢出漏洞。很多开发人员都了解这些漏洞，但仍然可能会犯错。就像我之前说过的，人总会犯错。所以不要惧怕在繁杂的代码框架中去审计代码。这种类型的漏洞实际上是真实的存在于代码框架中，而不仅仅局限于 CTF 比赛，所以，只要不惧怕找漏洞的难度，你就能发现这类简单的漏洞。

CTF 和真实环境中的漏洞之间存在一个很大的不同之处。在 CTF 比赛中，通常当你发现问题时，你就大概知道该怎么处理它、如何去利用它等。比如，遇到溢出问题时，你需要去覆写变量或返回地址等。所以当你在 CTF 比赛中遇到漏洞时，大多数时候你知道怎么处理它，而在真实环境中，你有的只是像 “state（状态）”这样的词，以及一些原语 (premitives)，而原语是攻击者具备的一些能力，因此我们需要链接 (chain) 这些原语，做一些影响更大的事情，从而触发更大的漏洞。我在 Chakra 中找到的就是这种漏洞。这些就是我在开始查看 Chakra 之前所了解到的漏洞研究和安全研究知识。



## Chakra 0day 相关背景知识

我们说说 JavaScript。先说 JavaScript 引擎。有人会说你之前没说你学过 JavaScript 啊。我确实没说，因为我真的没学过。JS 是一种非常可靠的语言，当你学会一些编程语言后，学习 JavaScript 的过程可能会更顺畅一些。因此，做到这一点应该不会太难。

JavaScript 引擎负责运行开发编写的 JS 代码。它由很多部分组成，对我们而言最重要的是 JIT 编译器，它的作用是当有些函数变得很热门被调用很多次时，它会把这个函数编译成机器代码来改进它的性能。JIT 编译器还负责优化代码。它具有很多针对代码的假设，它不希望这些假设崩溃。我们随后会讲讲 JIT 编译器中出现的相关漏洞问题。

来了解下 JavaScript 的基础知识，它是一种动态输入语言，可读性尚可。JS 对象具有“原型”，用于从其它对象中继承各种功能，它在漏洞发现过程中很重要。它可通过 _proto_ 属性更改对象的原型进行修改。 Proxy 是可用于重新定义基础操作的对象。我们可以通过这些基础操作，将调用限制在 getter 和 setter 等函数中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011b3132162c147687.png)

来看下 ChakraCore。JavaScript 具有数组，而 ChakraCore 具有类型数组。我们来看看第一种类型 JavascriptNativeIntArray。它用于存储整数，每个元素具有四个字节。（举例： varint_arr=[1]）另外一种类型是 JavascriptNativeFloatArray，它用于存储浮点数，和C语言不同，它的每个元素具有8个字节（举例 varfloat_arr=[13.37]）。 JavascriptArray 用于存储对象（主要是指针），每个元素具有8个字节（举例： varobject_arr=[`{``}`]）。

我们来看下如何转换这些类型。

[![](https://p4.ssl.qhimg.com/t01da6adb2eb9aa1d43.png)](https://p4.ssl.qhimg.com/t01da6adb2eb9aa1d43.png)

[![](https://p3.ssl.qhimg.com/t01c6c80f7a934f83bf.png)](https://p3.ssl.qhimg.com/t01c6c80f7a934f83bf.png)

其中最后一种 (也就是 aray2._proto_=array1 中的 array1 直接转换为 JavascriptArray) 转换在 JavaScript 引擎很少见，但对于我们今天讲的主题很重要。当我们有两个数组，并将其中一个设置为另外一个的原型，那么充当原型的这个数组就会被直接转换为 JavascriptArray。这一点我们稍后再着重讲。

我们再来看看这些数组在内存中是什么样的。举个例子：

[![](https://p2.ssl.qhimg.com/t01e5fc44e89ad2a47d.png)](https://p2.ssl.qhimg.com/t01e5fc44e89ad2a47d.png)

我们来看看实际在内存中，当调试如下样本代码时，可以看到我们刚才提到的字段状态 (vararr=[0xaaaaaa,0x31377];)。

[![](https://p1.ssl.qhimg.com/t017125ba51bbe805f6.png)](https://p1.ssl.qhimg.com/t017125ba51bbe805f6.png)

红框部分是 JavascriptArray 属性，我们能看到数组的初始值，也就是 ArrayFlags 的值。绿框部分是实际的片段属性，它有长度、大小。蓝框是片段的内存布局（包括元素，下图的地址是 pArr-&gt;head）。图中右下角我们定义了两个片段。那么什么是 ArrayFlags ？它们是提示数组的某些东西的一些 flag。在这个案例中，它被定义为一个枚举类型。我们感兴趣的字段是 JavascriptArray 的 arrayFlags 字段 HasNoMissingValues（如下图）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ae12707cd05d4f03.png)

在我们的例子中，被我们定义为 ArrayFlags 的 InitialArrayValue 实际上由两个不同的 flag 组成：一个是 ObjectArrayFlagsTag flag，它和我们讲的内容不重要就不讲了；我们将重点看第二个 HasNoMissingValues flag，它说明数组并不存在缺失的值，也就是说数组中不存在任何洞 (holes)。那么，“洞”是什么意思？我们创建一个数组，元素之间有一些值。在 ChakraCore 案例中，它有三个元素，但中间的一个元素是缺失的。

[![](https://p4.ssl.qhimg.com/t01c5c99655c64adaed.png)](https://p4.ssl.qhimg.com/t01c5c99655c64adaed.png)

放在这里的值，它们在内存中表示为这些常数。我举这个例子是因为这样我们更容易地能在内存布局中发现它们。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0122c5e25a41be4d30.png)

像这里（如上图）就存在一个“洞”，它并没有开启 HasNoMissingValues，也就是说数组中存在洞，数组中确实存在缺失的值。这看似很合理，但当我们查看内存布局时，我们会发现一些奇怪之处。我们来看下这些所谓的“缺失的值”是如何在内存中表示的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013165a81cc6c7b16d.png)

这（上图）是片段的内存转储，红色部分是数组的元素。我们看到 deadbeef deadbeef ，但在中间即“缺失的值”（“洞”）的位置，我们看到了一些 Magic 常数。 0xfff80002fff80002是从哪里来的？这些常数代表的是“缺失的值”或者说数组中的“洞”似乎能说得通。但如之前所述，我们已经知道有一些东西能代表“缺失的值”，就是没有 HasNoMissingValues flag。而现在我们似乎发现了另外一种表示方法，就是数组的内容（上面提到的 Magic 常量）。

这很奇怪，也引发了很多问题：数组的 flag 和数组的内容不匹配怎么办？ HasNoMissingValues 设为真，那么就意味着不存在任何“洞”；但是 数组中实际上存在一个“缺失的值”。另外，我们在某种程度上把“数据”和“元数据”混为一谈了，因为如果把常量当作控制流，那么我们如果能够伪造它的话就很有意思了。

[![](https://p5.ssl.qhimg.com/t0195ffd2f4b69a3b6a.png)](https://p5.ssl.qhimg.com/t0195ffd2f4b69a3b6a.png)

事实证明，我们真的能够伪造这个“缺失的值”。这是由 @s0rryMybad 和 @lokihardt 发现的漏洞（如上图），获得了CVE 编号 CVE-2018-8505。他们就是把我们之前看到的常量转换为浮点数数组，从而伪造了“缺失的值”，进而发现了漏洞。缓解这个漏洞的方法有很多，可以通过不断更改这个Magic值常量或增加更多的检查加固安全性。

我们上面讲的是如何能将这些奇怪的状态转变为我们实际上能利用的漏洞。首先我们先来看看一些有意思的东西。之前@s0rryMybad 和 @lokihardt 发现的漏洞是原生的浮点数数组。显然，JavascriptArray 并不直接将浮点数组存储为真正的浮点数，而是这些值被 “boxed”，然后以常量进行 XORed （下图）。

[![](https://p2.ssl.qhimg.com/t0159cf14b6cd6fe342.png)](https://p2.ssl.qhimg.com/t0159cf14b6cd6fe342.png)

那么问题就变成，我们能否在 JavascriptArray 中使用同样的“缺失的值”技巧？如果能的话，那么常数会改变吗？因为我们从上面的例子看到，我们更改了值的代表方式，我们才能表示新的值。从理论上来讲，引擎应当能改变常量，否则我们就可能表示它。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f6aadfd39dd95350.png)

而事实上，常量并没有改变，因此我们就能表示它。首先对其进行 boxing，然后通过之前的常量值（ 0xfff80002fff80002）对常量进行 XORed（ xor(magic,FlatTag_Value)）。这样，我们得到的常量还是原始值，因此值就是原始值。当你 XORed 三个元素，其中两个元素是相同的，这样做是不允许的，它会给你原始的值。但如果我们让其中的一个的值是 0xFFFcull&lt;&lt;48，那么我们就能返回 Magic 值表示值。

而正是在这里，我找到了漏洞。我们依靠的是 JavaScript 引擎的基础知识，而boxing 就是我们最先会学到的东西。我们使用 boxing 的想法，利用这种应该不会被利用的状态找到了漏洞。

那么我们是如何把这种奇怪的状态转变为漏洞的？先来看看什么是 JIT 类型混淆漏洞。我们现在常见的 JIT 漏洞是类型混淆。JIT 类型混淆实际上是两种类型的混淆，是指因 JIT 做出了错误的假设而发生的漏洞，最常见的是发生“Side-Effect”，也就是发生了一些 JIT 并未意识到的事情。例如，JITed 函数调用函数 foo()，更改了某些对象比如是数组的类型，而 JITed 函数并不知道转换已发生，使用了数组之前的类型，从而导致 JITed 代码中出现类型混淆情况，从而可能导致 RCE 漏洞的发生。举个例子：（如下图）

[![](https://p4.ssl.qhimg.com/t01ba3325b52a785b31.png)](https://p4.ssl.qhimg.com/t01ba3325b52a785b31.png)



## 我如何发现 Chakra 0day？

Loki 和 S0rryMybad 发现 Array.prototype.concat 具有一个有意思的代码路径，它同时考虑了 HasNoMissingValues 和数组元素的值，而两人成功让 HasNoMissingValues 和数组值不匹配。他们成功在数组中伪造一个“缺失的值（以下称为 buggy）”后，以下代码就会触发一个有意思的流：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a369993dcccf1191.png)

之后，我们看到如下 if 语句：

[![](https://p5.ssl.qhimg.com/t0135de125f8d85c5db.png)](https://p5.ssl.qhimg.com/t0135de125f8d85c5db.png)

首先我们来看函数 ConcatArgs。这里的 aItem 就是伪造的数组，也就是 buggy。我们想让 isFillFromPrototypes 返回假值，如果 HasNoMissingVlues 已设置如下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d47f10c17a9b6822.png)

isFillFromPrototyps 检查数组只有一个片段，也就是通过检查下一个头部片段是否为空，没有“缺失的值”。它确保长度匹配，也就是数组的长度和片段的长度相等。因此这个片段就是数组中的唯一一个片段。这是它做的第一个检查。它做的第二个检查是 flag 将 HasNoMissingValues 设为真，这一点可被轻松绕过。这样我们就能让 isFillFromPrototypes() 返回假值，然后进入 if 语句。

通过 isFillFromPrototypes() 检查后，我们看到如下的 else 语句，因为我们的数组并非原生数组。

[![](https://p3.ssl.qhimg.com/t01d13ff185fffb2bff.png)](https://p3.ssl.qhimg.com/t01d13ff185fffb2bff.png)

如下图， srcArray 就是我们创建的虚假的“缺失的值”数组（也就是我们说的 buggy）。首先让数组本身进行迭代，当且只当没有找到所有的元素时，才在数组的原型上进行迭代。 Enumerator 会枚举数组中的所有的元素。

[![](https://p4.ssl.qhimg.com/t01bfafff8262a61861.png)](https://p4.ssl.qhimg.com/t01bfafff8262a61861.png)

我们看下它是如何实现的。

[![](https://p5.ssl.qhimg.com/t013072c5df89b755ac.png)](https://p5.ssl.qhimg.com/t013072c5df89b755ac.png)

通过 ArrayElementEnumerator 迭代源数组，如果值是“缺失的值（ ==0xfff80002fff80002）”，则会跳过该元素。这里发生了什么呢？就是我们每次进入 while 循环时，如果发现是“缺失的值”，则会跳过它。迭代器会跳过缺失的值，所以它的计数和数组中的元素数目不一致。

[![](https://p0.ssl.qhimg.com/t01074b96a45375fd4c.png)](https://p0.ssl.qhimg.com/t01074b96a45375fd4c.png)

还有一个函数也很有意思。

[![](https://p0.ssl.qhimg.com/t0187c6baddedb86561.png)](https://p0.ssl.qhimg.com/t0187c6baddedb86561.png)

它做的第一件事就是在原型 (prototype) 链之间循环。我们之前说过，原型可以是继承功能的对象。那么我们可以自己创建一个原型、另外一个原型，从而伪造一个原型链。这个函数首先进行循环原型链，然后调用带有 prototype 参数的这个具有很长名字的函数。这个原型是一个 JavaScriptArray，然后我们对其进行循环。

[![](https://p5.ssl.qhimg.com/t01513aba41b21a1f42.png)](https://p5.ssl.qhimg.com/t01513aba41b21a1f42.png)

所以， ForEachOwnMissingArrayIndexOfObject 为原型链中的每个原型调用了 EnsureNonNativeArray。

[![](https://p3.ssl.qhimg.com/t0162ca091b993dc2ab.png)](https://p3.ssl.qhimg.com/t0162ca091b993dc2ab.png)

我们来快速回顾一下。如果我们创建一个带有伪造的 MissingValue 的数字，但设置了 HasNoMissingValue flag，那么我们就能得到来自 Array.prototype.concat() 的有意思的代码流。它会循环伪造数组的原型链，并保证这个链中的每个原型都是一个 Non-native 数组（也就是 JavascriptArray）。记住，如果某些对象是另外一个对象的直接原型，那么这个原型就被转换为一个 JavascriptArray。所以，从理论上来讲，如果我们的原型是一个原生数组，那么我们就能将其转换为 JavascriptArray，而 JIT 并不知道这一点，这和我们之前解释过的“平常的” Side-Effect JIT 漏洞类似。

幸运的是，已经存在造成这一后果的技术了！我们可以使用代理限制 GetPrototype() 调用，但如果我们编写函数的话，它会被检测为 side-effect。 Object.prototype.valueOf 不会产生 Side-Effect，这是 Lokihardt 使用的已知的技术。我们来看个例子。

[![](https://p3.ssl.qhimg.com/t015d840120b89114ce.png)](https://p3.ssl.qhimg.com/t015d840120b89114ce.png)

[![](https://p2.ssl.qhimg.com/t010c22506a6f7cd804.png)](https://p2.ssl.qhimg.com/t010c22506a6f7cd804.png)

[![](https://p2.ssl.qhimg.com/t015f9bb5a8827c4769.png)](https://p2.ssl.qhimg.com/t015f9bb5a8827c4769.png)

[![](https://p0.ssl.qhimg.com/t01a2d495b97662cae9.png)](https://p0.ssl.qhimg.com/t01a2d495b97662cae9.png)

[![](https://p3.ssl.qhimg.com/t019c660d3ab6c6476c.png)](https://p3.ssl.qhimg.com/t019c660d3ab6c6476c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01336c06a3580f5e63.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01001afa312989e864.png)

[![](https://p3.ssl.qhimg.com/t0183638a1c848d5b2a.png)](https://p3.ssl.qhimg.com/t0183638a1c848d5b2a.png)

要利用这个漏洞，我们首先伪造了一个 DataView 对象，从而能让我们任意读/写。我们的利用代码基于 Pwn.js 库，这是一个很好的库，但我们需要修复一下才能使用。我们通过一种已知技术泄漏了一个栈地址，因而能够通过从 ThreadContext 读取一些数据而获取栈指针。之后，我们 ROP 并恢复我们的覆写，就能获得合法的进程继续。

我们本来打算在 Edge 浏览器上实际执行我们的代码，我们在沙箱环境下执行了代码，它不允许我们弹出计算器等东西。我们无法进行演示。于是我们编译了 Linux 版本的 Chakra，在 Linux 上进行了演示。在 Linux 上利用该漏洞也是类似的。

(注：最后, Jonathan 成功地在 Linux 版本的 Chakra 上进行了演示。接着掌声雷动。）

希望我的演讲能给想进入安全领域的人带来一些帮助，同时也给只想听技术部分的观众带来一些帮助。

谢谢大家。



## 大家怎么说

1.Magic Value是什么？

2.这是一个新的类型混淆漏洞的转化点。

3.为什么引擎中要定义一个Magic Value？

研究过patch之后，发现对StElem指令这块做了检查。也就是(作者提到的使用原生浮点数组)无法直接通过赋值的这种方式在Array中生成Magic Value。

Jacobi 的演讲中也是这样的思路，他举了一个例子说明Magic Value在内存中的样子。初步认识了Magic Value，然后通过其他的方式去伪造一个Magic Value绕过之前补丁的检查，作者通过concat的方式进行了一种实现，发现了一个新的0day。

但我大胆猜测concat是他多次尝试成功的一个方法，这个问题可以抽象成如何生成一个新的包含Magic Value的数组，且不通过直接赋值的方式。类似copywithin，concat,push…等等方法。作者在构造PoC时提到比较多的技巧，比如Object.prototype.valueOf 不会产生 Side-Effect。这都建立在他长期第一时间对这个领域知识的积累上。

这其中的严谨踏实的求真、勤于思考的积累、和清晰完善的思路，都值得去学习。

## 死磕到底。

欢迎在留言区分享你的看法~



## 原文链接

<iframe class="wp-embedded-content" sandbox="allow-scripts" security="restricted" src="https://media.ccc.de/v/35c3-9657-from_zero_to_zero_day/oembed#?secret=ljGxgJdHZh" data-secret="ljGxgJdHZh" width="500" height="720" frameborder="0" title="From Zero to Zero Day" scrolling="no"></iframe>
