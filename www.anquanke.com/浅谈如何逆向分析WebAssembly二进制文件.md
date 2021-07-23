> 原文链接: https://www.anquanke.com//post/id/150923 


# 浅谈如何逆向分析WebAssembly二进制文件


                                阅读量   
                                **176186**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：forcepoint.com
                                <br>原文地址：[https://www.forcepoint.com/blog/security-labs/analyzing-webassembly-binaries](https://www.forcepoint.com/blog/security-labs/analyzing-webassembly-binaries)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t011b5ceac683c12d8c.png)](https://p4.ssl.qhimg.com/t011b5ceac683c12d8c.png)

我们最近发表了一篇关于[WebAssembly](https://www.forcepoint.com/blog/security-labs/webassembly-potentials-and-pitfalls)（Wasm）基本概念及其安全问题的博文。作为后续，本文将对Wasm应用程序的逆向工程方法进行介绍。考虑这样一个场景：当你遇到一个未知的Wasm应用程序，并想要弄清楚它是怎么构成的时候。你如何去分析它？目前关于这个主题几乎没有任何有用的文献，所以我们决定在一定程度上填补这个空白。

对于一个Wasm应用程序，我们可以用不同的方法进行分析。今天，我们将通过一个非常简单的应用程序来介绍Chrome内置的Wasm调试功能。随着我们的进展，一些相关概念将会被引入。

如果有按耐不住想要直接了解相关的技术内容的读者，可以先从附录部分获取HTML文件test.html，然后直接跳转到“调试我们的示例应用程序”部分。



## 为什么要分析W​​asm？

首先，为什么我们会对分析Wasm应用程序感兴趣呢？让我们先来回答这个问题，然后再深入研究实际的技术问题。

对于Forcepoint公司来说，我们对恶意软件开发者如何利用新兴技术和技巧非常感兴趣。每当出现新的威胁，比如一个新的勒索软件家族、一个物联网蠕虫或其他更不寻常的东西，安全研究人员都希望深入分析恶意代码的所有功能。当我们弄清楚一个恶意软件是如何工作的以及了解它的特性之后，我们可以通过编写签名来提供相应的保护。

这里有许多可用于分析传统恶意软件的工具，无论是经混淆过的JavaScript、恶意Flash对象、可移植可执行文件（PE）还是其他东西，总有一种行之有效的方法来分析这些威胁。

正如我们在本系列的第一篇文章中提到的那样，而Wasm的情况却有所不同。几乎没有任何关于如何分析Wasm应用程序的文献，大多数用于逆向工程的常用工具也都不适用于Wasm。因此，写这篇博文的一个目的也是试图为如何逆向分析Wasm二进制文件提供一些启发。



## 创建一个 “Hello World”Wasm示例应用程序

让我们从创建一个简单的Wasm应用程序开始，我们稍后将对其进行逆向分析。我们将在浏览器中运行该应用程序，并使用Chrome的开发人员工具对其进行逆向分析。

要在浏览器中运行Wasm应用程序，我们需要一个HTML文件来加载和执行Wasm二进制文件。让我们来看看创建这个HTML文件的过程。（如前所述，完整的文件可以在本文的附录中找到。）

从构建下面的框架开始（我们将进一步修改），并将其保存到test.html文件：

```
&lt;html&gt;
&lt;script&gt;
  function test() `{`
  `}`
&lt;/script&gt;
&lt;body onLoad="test()"&gt;
&lt;/body&gt;
&lt;/html&gt;
```

为了便于配置，并避免安装任何工具，让我们使用一个名为[WasmFiddler](https://wasdk.github.io/WasmFiddle/?wvzhb)的在线Web应用程序来生成我们的Wasm。在WasmFiddler中，输入以下简单程序：

```
void hello()
`{`
  printf("Hello Worldn");
`}`
```

然后，点击“Build”，如下面的屏幕截图所示： [![](https://p2.ssl.qhimg.com/t01b35acf1c439ccd33.png)](https://p2.ssl.qhimg.com/t01b35acf1c439ccd33.png)

图1：使用WasmFiddler编译Wasm应用程序

在上面的屏幕截图的右侧，我们可以看到一个名为utf8ToString()的函数。将该函数复制并粘贴到HTML页面的JavaScript部分，并将其置于test()函数之上。

仍然是在屏幕截图的右侧，我们可以在函数utf8ToString()之后看到几行JavaScript，如下所示：

```
let m = new WebAssembly.Instance(new WebAssembly.Module(buffer));
let h = new Uint8Array(m.exports.memory.buffer);
let p = m.exports.hello();
```

复制这几行代码，并将它们粘贴到test()函数中。这几行代码将实例化我们的Wasm，根据定义在名为“buffer”的数组中的代码，然后执行我们的hello()函数。

那么，我们如何定义这个缓冲区的内容（Wasm代码）呢？在WasmFiddler中，单击源代码下面的下拉菜单（图1中的“Text Format”），然后选择“Code Buffer”。

[![](https://p2.ssl.qhimg.com/t019026c093b378047f.png)](https://p2.ssl.qhimg.com/t019026c093b378047f.png)图2：在WasmFiddler中查看代码缓冲区

现在，WasmFiddler将生成二进制Wasm代码并将其放入JavaScript缓冲区中。你应该会得到如下内容（这里为了简洁，展示的是删减的结果）：

var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,…,108,100,0]);

注意：如果你只是得到一个空数组（“var wasmCode = new Uint8Array([null]);”），那么你应该是忘记了先编译源代码。在这种情况下，点击Build，再试一次。

复制这个缓冲区的内容，并将其粘贴到我们的test()函数的开始部分。将数组从“wasmCode”重命名为“buffer”，以匹配由WasmFiddler生成的其他代码的命名。

如果你还记得我们在本系列的第一篇文章所介绍的内容的话，那么你应该知道Wasm应用程序本身无法将文本打印到屏幕上。我们需要定义一个JavaScript函数，在我们的Wasm代码中调用printf()函数。回到WasmFiddler，在下拉菜单中选择Text Format格式，以查看编译后的Wasm应用程序的文本表示形式：

[![](https://p2.ssl.qhimg.com/t01fa3a15453383c45c.png)](https://p2.ssl.qhimg.com/t01fa3a15453383c45c.png)图3：puts()函数的Imports模板

复制上面看到的“wasmImports”的定义，并将其粘贴到我们的test()函数的开头部分。然后，我们需要将这个Imports的定义提供给Wasm的实例，如下所示：

var m = new WebAssembly.Instance(new WebAssembly.Module(buffer),wasmImports);

最后，让我们来定义puts()函数在被调用时应该做些什么。将其更改为以下内容：

```
puts: function puts (index)
`{`
alert(utf8ToString(h, index));
`}`
```

现在，我们已经完成了构建示例应用程序所需的所有步骤。在Chrome中加载我们的test.html文件，我们会看到这样一个弹出窗口： [![](https://p1.ssl.qhimg.com/t01573d3ff65469b544.png)](https://p1.ssl.qhimg.com/t01573d3ff65469b544.png)

图4：Chrome中的通知

我们可以看到，Wasm代码成功地调用了我们的外部函数。

注意：如果你没有看到弹出窗口，那么问题很可能是你的浏览器不支持Wasm。在这种情况下，请尝试使用最新版本的浏览器，因为目前所有主流浏览器的最新版本都应该支持Wasm。



## 调试我们的示例应用程序

现在，我们终于可以使用Chrome开发人员工具来调试我们的示例应用程序了。

在Chrome中打开test.html文件后，启动Chrome开发人员工具（通过按F12键），并选择顶部的Sources选项卡。然后，按Ctrl+R重新加载页面。现在，会出现一个带有文字“wasm”的小云朵图标。展开它以及它下面的项目，选择wasm子树下的叶子项目。具体如下所示： [![](https://p5.ssl.qhimg.com/t018b801d71b452c594.png)](https://p5.ssl.qhimg.com/t018b801d71b452c594.png)

图5：Chrome开发人员工具

让我们单步执行这个函数，以便更好地理解它的功能。单击左侧以“i32”开头的代码行，为其设置断点。一个蓝条将显示出来，表明断点已设置好。接下来，按Ctrl+R重新加载页面。现在，执行将停止在断点处。此时，Wasm堆栈是空的。然后，在调试器中按下Step Over按钮（F10或带有弯曲箭头的图标）以执行指令“i32.const 16”，以将值“16”压入堆栈： [![](https://p2.ssl.qhimg.com/t01d3e23443e026cc02.png)](https://p2.ssl.qhimg.com/t01d3e23443e026cc02.png)

图6：将值“16”压入堆栈

Wasm中的所有函数都被编号，编号为0的函数对应于Wasm从JavaScript导入的函数“puts”（编号为1的函数对应于“hello”函数）。因此，下一条调用0的指令实际上调用的是printf/puts函数，而堆栈中的值“16”就是它的参数。

值“16”如何与字符串‘Hello World’对应呢？该值实际上是一个指向Wasm应用程序内存空间中的地址的指针。让我们利用Chrome的调试器展开全局树，以查看Wasm应用程序的内存：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fb7c928df6d2da50.png)图7：查看Wasm应用程序的内存

让我们来看看内存中的位置编号为16处的内容：[![](https://p4.ssl.qhimg.com/t01376c9492882ac612.png)](https://p4.ssl.qhimg.com/t01376c9492882ac612.png)

图8：Wasm应用程序内存中的“Hello World”

运行状态下的Wasm应用程序的内存空间实际上是作为JavaScript数组实现的。该数组的定义位于负责加载Wasm应用程序的HTML文件中。在我们上面的示例中，变量“h”的定义如下所示，它包含了应用程序的内存空间：

let h = new Uint8Array(m.exports.memory.buffer);

现在，再次按下Step Over按钮来执行调用。如此这样，我们应该就能够看到JavaScript警报了。



## 结论

我们现在已经成功地逆向分析了我们的第一个简单的Wasm程序。尽管这个示例非常简单，但请记住，很多事情我们都需要从零开始。

在逆向分析过程中，我们是通过调用JavaScript声明的导入函数来了解Wasm如何与外部环境进行交互的。此外，我们还介绍了如何在JavaScript和Wasm之间共享内存。

Forcepoint安全实验室将继续观察Wasm的发展，并在适当的时候对我们的文章进行更新。



## 参考资料

WasmFiddle，在线编译Wasm：[https://wasdk.github.io/WasmFiddle/?wvzhb](https://wasdk.github.io/WasmFiddle/?wvzhb)

关于如何在浏览器调试器中调试Wasm的视频：[https://www.youtube.com/watch?v=R1WtBkMeGds](https://www.youtube.com/watch?v=R1WtBkMeGds)

在JavaScript和Wasm之间传递值：[https://hacks.mozilla.org/2017/07/memory-in-webassembly-and-why-its-safer-than-you-think/](https://hacks.mozilla.org/2017/07/memory-in-webassembly-and-why-its-safer-than-you-think/)



## 附录：test.html

为了便于参考，以下是我们创建并分析的完整test.html文件：

```
&lt;html&gt;
&lt;script&gt;
function utf8ToString(h, p) `{`
  let s = "";
  for (i = p; h[i]; i++) `{`
    s += String.fromCharCode(h[i]);
  `}`
  return s;
`}`
function test() `{`
  var wasmImports = `{`
    env: `{`
      puts: function puts (index) `{`
        alert(utf8ToString(h, index));
      `}`
    `}`
  `}`;

  var buffer = new Uint8Array([0,97,115,109,1,0,0,0,1,137,128,128,128,0,2,
    96,1,127,1,127,96,0,0,2,140,128,128,128,0,1,3,101,110,118,4,112,117,
    116,115,0,0,3,130,128,128,128,0,1,1,4,132,128,128,128,0,1,112,0,0,5,
    131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,146,128,128,128,0,2,6,
    109,101,109,111,114,121,2,0,5,104,101,108,108,111,0,1,10,141,128,128,
    128,0,1,135,128,128,128,0,0,65,16,16,0,26,11,11,146,128,128,128,0,1,0,
    65,16,11,12,72,101,108,108,111,32,87,111,114,108,100,0]);
  let m = new WebAssembly.Instance(new WebAssembly.Module(buffer),wasmImports);
  let h = new Uint8Array(m.exports.memory.buffer);
  m.exports.hello();
`}`
&lt;/script&gt;
&lt;body onLoad="test()"&gt;
&lt;/body&gt;
&lt;/html&gt;
```

审核人：yiwang 编辑：边边
