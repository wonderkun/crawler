
# 【技术分享】WebAssembly入门：将字节码带入Web世界


                                阅读量   
                                **183190**
                            
                        |
                        
                                                                                                                                    ![](./img/85934/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fortinet.com
                                <br>原文地址：[http://blog.fortinet.com/2017/04/13/webassembly-101-bringing-bytecode-to-the-web](http://blog.fortinet.com/2017/04/13/webassembly-101-bringing-bytecode-to-the-web)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85934/t018e4ee994f45efc52.jpg)](./img/85934/t018e4ee994f45efc52.jpg)



翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

WebAssembly（WA）是一种新兴技术，FortiGuard实验室在这篇文章里汇总了与之相关的一些常见问题。

<br>

**一、何为WebAssembly**

WebAssembly是针对Web设计的一种低级语言，这种可移植的二进制格式旨在提高Web应用的运行速度。这种语言的设计初衷是获得比JavaScript（JS）更快的解析速度（最高提高20倍）和执行速度。

<br>

**二、WebAssembly的公布时间**

WebAssembly社区小组于2015年4月成立，其使命是“为Web设计一种全新的、可移植的、能够高效加载及易于编辑的轻量级格式，以促进跨浏览器协作”。

<br>

**三、从何处入手**

首先你必须使用[**Binaryen**](https://github.com/WebAssembly/binaryen)设置[**Emscripten SDK**](http://kripken.github.io/emscripten-site/)，将C/C++代码或Rust代码转化为WA的“.wasm”二进制文件，或者使用与Lisp类似的[**S-表达式**](https://webassembly.github.io/spec/)将代码转化为“.wast”（或“.wat”）文本格式，如图1所示。

[![](./img/85934/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0157fbf6ef79cd9aaa.png)

图1. 从源代码到Web的处理过程

你可以从这个[**在线工具**](https://cdn.rawgit.com/WebAssembly/sexpr-wasm-prototype/2bb13aa785be9908b95d0e2e09950b39a26004fa/demo/index.html)开始学习，快速查看代码片段。

在页面右侧的反汇编输出中，你可以看到头两行代码如下所示：



```
0000000: 0061 736d                                  ; WASM_BINARY_MAGIC
0000004: 0b00 0000                                  ; WASM_BINARY_VERSION
```

第一行与魔术数字“0x6d736100”有关，这个数字代表的是“asm”。第二行显示的是版本号，这里版本号为“0xb”。由于当前WA的版本号是0xd，因此这个在线工具生成的字节码不能用于当前版本的Web浏览器，不过这段代码还是值得一看的。当WebAssembly最终发布时，其版本号会被设定为0x1。

<br>

**四、WebAssembly如何工作**

目前WebAssembly需要通过JavaScript加载和编译。主要包括以下四个步骤：

1、加载wasm字节码。

2、将wasm字节码编译为模块。

3、实例化模块。

4、运行函数。

翻译过来就是：



```
fetch('your_code.wasm').then(response =&gt; response.arrayBuffer()
).then(bytes =&gt; WebAssembly.instantiate(bytes, {})
).then(instance =&gt; instance.exports.your_exported_function ()
```

从上述代码可知，“WebAssembly.instantiate”可以同时用于编译和实例化模块。

<br>

**五、WebAssembly的使用场景**

作为asm.js的下一代改进版，WebAssembly使用了JavaScript中一个非常受限的指令子集，该子集最适合作为C编译器的编译目标。WebAssembly不包含JavaScript对象，也不直接访问文档对象模型（Document Object Model，DOM）。从本质上来讲，WebAssembly只允许对类型数组进行算术运算和操作。

一些初步样例表明，使用wasm实现的斐波那契数生成算法比对应的JS实现性能上更优，有超过350%的性能提升。

目前，WebAssembly只是在简单模仿JS的功能，但人们计划扩展WebAssembly的使用场景，以处理JS中难以处理的事情，同时不增加语言的复杂度。比如，人们计划使WebAssembly默认支持SIMD（Single Instruction，Multiple Data，单指令流多数据流）、线程、共享内存等等功能。

许多流行视频游戏编辑器已经准备就绪，开始将WebAssembly技术与WebGL 2.0相结合，将部分3D功能引擎移植到这个全新平台上。你可以试一下Epic出品的[**Zen Garden**](https://s3.amazonaws.com/mozilla-games/ZenGarden/EpicZenGarden.html)，体验这种全新技术。

<br>

**六、这是否就是JavaScript的末日**

WebAssembly会促进JavaScript的发展，而不是导致其灭亡，它可以为Web中的关键功能带来语言上的多样性并提高性能。WebAssembly不单单给JS带来性能上的提升，同时也造福了Web浏览器。

可以预想的是，五年后，我们使用JS的方式将大大不同。目前，我们在很多场景中都难以使用JS代码完成任务，大部分功能都需要借助复杂库来实现。

由于WebAssembly的易用性和简单性，我们预测会有越来越多的代码从C++或Python转化为JS，甚至直接转化为WebAssembly。这意味着你不需要去学习一门全新的语言。JS虚拟机还是会存在，但对应工具会不断发展，以获取更优的性能。

<br>

**七、WebAssembly与基于MS ActiveX/Adobe Flash/Orcale Java Applet/MS Silverlight/Google NaCl构建的富因特网应用之间有何区别**

由于不同的公司各自推出了不同的标准，因此富因特网应用（Rich Internet Application, RIA）无法形成标准的开放格式。

比如，微软在自家的IE浏览器中推广ActiveX技术。该技术让开发者能够通过COM组件将打包功能重新集成到Web页面中。

Google推出了Native Client，让开发者将一些C/C++代码打包集成到浏览器中，然而，只有Chrome支持这项技术，达不到广义上的可移植要求。

几年前，Mozilla发布了asm.js，打开了性能优化的大门。他们最早提出了使用JS中的严格子集。通过限制语言的功能性，他们能够预测虚拟机的下一步反应，从而通过移除某些不必要的检查操作以提高性能。但这种技术也会影响语言的动态行为。

所有的这些技术构成了今天WA诞生的基础。WebAssembly运行在JS虚拟机内部，使用了JS的部分功能，这意味着它不仅能够与运行最新Web浏览器的设备兼容，也能做到向前兼容。为了实现这一点，设计人员正在开发一个polyfill，核心思想是将每个函数转换为语义上等效的JS代码，虽然这样做会影响运行性能，但至少能解决代码的运行问题。

<br>

**八、WebAssembly长什么样**

顾名思义，WebAssembly的最终形式是一种低级字节码，可以转换为汇编代码，但与通常的CPU汇编代码不同。

我们来看看“Hello world”这个例子（值得一提的是，虽然“Hello world”是大多数程序员相当熟悉的一个程序，但这个程序并不是特别适合这门语言，因为WA默认情况下没有集成打印功能，这也是为什么以下代码必须通过JS从标准库中导入该功能，然后传递所需的参数）。

size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)这个C语言库函数可以从ptr指向的数组中读取数据，并将数据写入到stream文件流中。

紧跟在wasp代码之后的是wasm字节码的版本号，如上文所述。



```
;; WebAssembly WASM AST Hello World! program
(module
  (memory 1 
   (segment 8 "hello world!n")
  )
  (import $__fwrite "env" "_fwrite" (param i32 i32 i32 i32) (result i32))
  (import $_get__stdout "env" "get__stdout" (param) (result i32))
  (export "main" $main)
  (func $main (result i32)
    (local $stdout i32)
    (set_local $stdout (call_import $_get__stdout))
    (return (call_import $__fwrite
       (i32.const 8)         ;; void *ptr    =&gt; Address of our string
       (i32.const 1)         ;; size_t size  =&gt; Data size
       (i32.const 13)        ;; size_t nmemb =&gt; Length of our string
       (get_local $stdout))  ;; stream
    )
  )
)
```

代码1：wast版的Hello World程序（参考自[github](https://gist.github.com/icefox/e58d23e860a0b525e0044cac120f667b#file-helloworld-wast)）

[![](./img/85934/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017af2785c8f821014.png)

代码2：wasm字节码形式的Hello World程序

虽然我们可以手动编写字节码，但我想没有哪个程序员会这么做。相反，他们会选择使用wasp的[S-表达式](https://webassembly.github.io/spec/)，或者其他更为人性化的高级语言，这样能够生成等价的编译器优化的代码。

<br>

**九、WA的安全性如何，对网络威胁方面的意义**

在浏览器中运行时，WebAssembly运行在一个安全的沙箱化环境中，这意味着WebAssembly与其他Web语言一样，遵守相同的同源策略和权限策略。根据维基百科的定义，[**同源策略**](https://en.wikipedia.org/wiki/Same-origin_policy)可以“防止某个页面中的恶意脚本通过该页面的文档对象模型（DOM）获取其他Web页面上敏感信息的访问权限”。

这听起来是一个非常完美的解决方案。

然而，过去的很多案例表明，攻击者出于个人利益，总是能够找到一种方法来滥用或转移新技术的使用场景。比如，攻击者已经使用某些流行的开源项目或某些自制代码中的JS混淆代码，实现恶意代码隐藏并绕过杀毒软件的检测。

因此我们很容易就能预测到，WA可能会被攻击者用来实现高级混淆或加密。这个问题对训练有素的分析师来说并不是不能克服的，但对攻击工具的调试和挖掘将变得更加困难，也更加耗时。

目前，如果你在浏览器界面点击右键，查看wasm模块，你所看到的结果会与当前所使用的浏览器有关。你可能会在开发者调试器窗口看到某个函数的“原生代码”引用，也可能看到Firefox中的一个警告信息（如图2所示），还有可能看到Chrome中文本形式的WA代码（如图3所示）。

[![](./img/85934/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ba0285984bf1b6b9.png)

图2. Firefox浏览器的WA调试界面

[![](./img/85934/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fb289d9646ab712b.png)

图3. Chrome浏览器的WA开发者工具

我们需要改进Web浏览器以支持更加智能的WA调试工具。在任何情况下，浏览器都应该支持某个恶意模块的下载（因为模块需要在用户主机上运行）及反汇编，以帮助逆向研究人员分析模块的目的。否则，就像.NET一样，会有某些代码混淆器阻止人们将字节码还原为初始代码。但后者可能不是出于恶意目的，有时候是合法的，比如源代码作者希望通过这种方法保护他们的知识产权。

<br>

**十、WA何时发布**

Mozilla Firefox 52版（3月7日发布）、Google Chrome 57版（3月9日发布）以及Opera 44版（3月21日发布）已经默认支持并启用了WA。其他主流浏览器厂商，比如微软和Apple也正在推进浏览器支持WA。你可以在线跟踪相关的研发状态。

<br>

**十一、如何禁用**

禁用WA的方法取决与你正在使用的具体浏览器。

对于Chrome，你可以访问“chrome://flags/#enable-webassembly”这个URL，在组合框中选择“Disabled”即可。需要注意的是，你还需要重新启动浏览器使更改生效。

对于Firefox，你可以访问“about:config”这个URL，找到名为“javascript.options.wasm”的首选项，双击将该布尔值改为“False”，就可以禁用WA。
