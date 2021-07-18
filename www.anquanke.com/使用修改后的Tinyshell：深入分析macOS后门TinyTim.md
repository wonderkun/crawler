
# 使用修改后的Tinyshell：深入分析macOS后门TinyTim


                                阅读量   
                                **333816**
                            
                        |
                        
                                                                                                                                    ![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者themittenmac，文章来源：themittenmac.com
                                <br>原文地址：[https://themittenmac.com/tinyshell-under-the-microscope/](https://themittenmac.com/tinyshell-under-the-microscope/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/203643/t018033be064faf3621.png)](./img/203643/t018033be064faf3621.png)



## 前言

早在2018年的时候，我就在一些小型会议上发表了名为Macdoored的演讲。在演讲中，我针对Mac遇到的各种APT攻击进行了分享。在分享过程中，我用了一些时间来说明攻击者目前正在使用的后门，它是Tinyshell的修改版本。Tinyshell是一个开源工具，其运行方式类似于修改后的SSH。从遇到这个新版本开始已经有一段时间了，但是我完全有理由相信，攻击者仍然在使用这个后门。如果大家观看了名为Macdoored的主题演讲，就会了解到，攻击者目前正在使用这个工具发动攻击。但是，目前还没有人研究过该恶意软件本身的技术细节。可能原因在于，恶意软件与开源版本相比，其代码的变化比较小。然而，这些修改可以让我们通过多种方式对其进行有效检测。由于该恶意软件已经被恶意行为者修改，因此现在将其继续称为Tinyshell似乎并不准确。因此，我将这个特定的修改版本称为TinyTim。

我们可以在VirusTotal上找到这篇文章中涉及到的示例。

SHA256：8029e7b12742d67fe13fcd53953e6b03ca4fa09b1d5755f8f8289eac08366efc

最后，在我们开始深入分析之前，我想向Objective-See的Patrick Wardle表示感谢，感谢他对于Hooper反汇编过程中的指导。在他的网站上，有大量免费的Mac安全工具，欢迎大家使用。



## 初步分析

经过我们的初步观察表明，该恶意软件是由开发者进行签名的。我们目前还不清楚这是被窃取的合法签名证书，还是由攻击者创建并持有的证书。这非常值得关注，因为恶意软件通常都是为了防止被Gatekeeper拦截而进行的签名。正如我再Macdoored演讲中提到的那样，这个恶意软件使用了获取到的凭据，通过SSH方式连接到受害者系统上并投放其自身。还有一种可能，也许攻击者故意使用经过签名的二进制文件，以便降低其被发现的概率。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017c96b1fe43c48179.png)

恶意行为者对Tinyshell源代码所做的主要更改之一，就是添加了一个名为`MyDecode()`的函数。该函数使攻击者可以对二进制文件中的某些公开字符串进行编码。如果我们想要更加具体地了解这里发生的事情，就需要在Hooper等反汇编程序中打开它。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f7f628269a4b89c0.png)

在主函数中，我们首先发现，TinyTim已经添加了一些基本的反调试功能。在开始时，我们看到`ptrace`与`ptrace_deny_attach`参数共同使用，如果是连接调试器执行该程序，则程序会立即关闭。我们必须要注意这一点。

在检查调试器是否存在后，该函数将继续运行`getuid()`，它将返回执行程序用户的用户ID。在这里，恶意软件主要检查是否存在属于root用户的UID 0。在这两种情况下，`MyDecode`函数最终都会在看起来像是乱码的字符串上运行。如果我们在左侧的标签中选择`_MyDecode`并按“X”按键，就可以看到所有引用这一函数的位置。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01649263aa610fa7f7.webp)

我们发现，有11个调用是来自主函数，有2个调用来自`tshd_runshell`。显然，这个恶意软件经常依赖于这个函数。如果我们将Hooper视图切换为伪代码，可以发现这个函数实际上是非常基础的。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ba65f4bf24e142a1.png)

在这里，需要重点关注的一项是`r14 ^ r15`。这是恶意软件经常会用到的，用于对两个字节进行简单的异或运算。我们看到，`r14`和`r15`的值是传递给该函数的第二和第三个参数值。而传递的第一个参数，施工记者想要取消屏蔽的字符串。回到主代码，我们可以去寻找攻击者在调用`MyDecode`时传递的值。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013a5f6bff90a99d6a.webp)

在前面的几个调用中，我们看到`MyDecode`使用了XOR方式`0x4 ^ 0x2`对每个字符串进行编码。在这里，有一些方法，可以将这些字符串转换回可读文本。我们可以调试程序，也可以编写简单的脚本来解码字符串。或者，也可以结合这两种方式。我们首先从调试开始。



## 准备工作

在开始之前，我们需要通过执行以下步骤来准备可执行文件，以便使其可以运行。

1、使用`chmod +x`赋予TinyTim可执行文件权限。

2、使用`codesign --remove-signature`删除已经撤销的签名。

3、使用`xattr -d com.apple.quarantine`删除隔离位（假设该恶意软件是从下载的来源）。

4、删除前面讨论过的`ptrace()`调用，这是一种防调试技术，如果检测到调试器的存在，则会关闭该程序。我们可以通过在`ptrace`调用上放置一个断点，然后跳过的方式来实现。或者，我们可以简单地对其NOP，这样一来就不必在每次运行时都产生一个额外的断点。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ca312b06439dfa98.png)

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01888666f3cec2a4d2.png)



## 调试

现在，我们已经完成了所有准备工作，可以在调试器中打开TinyTim，并开始分析`MyDecode()`函数。我们在函数末尾的返回值上放置一个断点，然后启动调试器。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015d2138c61c35f5b7.png)

当在调试器中命中断点时，就表明`MyDecode`函数已经运行完成。如果使用`x/s $rdx`命令打印RDX寄存器，我们就可以看到已经解码的字符串。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01295042736a12c2a2.png)

在这种情况下，我们看到解码后的字符串是`/Users/%@/Library/Fonts/.cache`。请注意，我们在这里是以基本用户身份运行的，从主函数中可以看到，如果是以root身份运行，将会执行不同的分支（请参阅第一个截图中的if/else语句）。我们可以继续调到下一个断点，并打印每个字符串，从而得到结果。

```
0x10000c260: “/Users/%@/Library/Fonts/.cache”
0x7ffeefbffa40: “PROG_INFO”
0x7ffeefbffa50: “name_masq”
0x7ffeefbffa60: “CONN_INFO”
0x7ffeefbffb28: “domain”
0x7ffeefbffa70: “”
0x7ffeefbffa70: “next_time”
```

大多数安全分析人员都会将上面的字符串视为是后门配置选项。我们猜测，这些选项可能是从`/Users/%@/Library/Fonts/.cache`文件中进行读取的。但是，由于没有在指定位置创建配置文件，所以我们没有成功读取这些配置。另外有一点需要关注，其中有一个解码后的字符串为空，这稍微有一些奇怪，但我们可以在后面再进行讨论。现在，我们来整理一些快速的Python代码，这些代码也可以取消屏蔽这些字符串，因为它们并没有实际的影响。在这里，似乎没有更快速的方式，我们只需要跳过提供的字符串中的每个字符，然后对其执行XOR操作，就可以得到解码后的字符。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c411112983684f86.png)

现在，我们在无需调试器的情况下，就可以轻松实现解码。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01de8fa73bc38c2577.png)

太棒了！现在，我们就可以获取存储在可执行文件中的各种字符串，并以纯文本格式查看它们。接下来，我们可以尝试创建一个配置文件，并看看会发生什么。但是，我们现在还并不清楚配置文件的格式，因此首先需要看看能否解决这一问题。

我们发现，配置文件格式的关键，实际在于`getProfileString()`函数。该函数仅仅会引用`fopen()`、`fgets()`、`fseek()`和`fclose()`函数，而后面的几个函数通常用于打开文件、关闭文件和移动文件。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ce48c969698cba97.png)

如我们所见，`fopen`将打开指定为arg0的文件，在我们的示例中，就是恶意软件的配置文件。随后，开始对配置文件进行解析。在文件的最后，我们看到`sscanf()`正在使用某些特定的格式。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c874a50f191b08bc.png)

如果大家不熟悉这个函数，可以在Google上查询`sscanf`函数，以弄清楚这里发生的事情。随后，我们需要将视线转移到`GetProfileString()`函数上面来。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017bc88d535c0cbcc9.png)

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fef8cfca2ebc9def.png)

在这里，我们得到了一个函数，它是Windows的某种端口，允许用户读取.ini格式的配置文件。我们这时回顾之前由`myDecode()`函数产生的值，发现这里很有意义。这意味着，所有大写字母的条目均为`lpAppName`的值，小写字母的条目均为`lpKeyName`的值。在Mac上，这显然有些不自然，因为它是Windows .ini格式的一部分，但实际上，其本质是文本文件，并不是复杂的格式。这意味着，我们的配置文件应该类似于以下的示例：

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016efa939adb047213.png)

这里使用的值是我在测试过程生成的，但是这样的格式应该是有效的。我们有一种简单的确认方法，可以在`getProfileString()`函数底部附近的`strcpy()`函数上放置一个断点，因为我们猜测该函数用于保存从配置文件中获取的字符串。在到达断点后，我们可以使用`x/s $RDI`（在调用函数时，RDI几乎总是保持在arg0）来打印`$RDI`寄存器，以显示出在继续下一个断点之前传递给`strcpy`函数的第一个参数，并依此重复。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d562a2a5a5050807.png)

在使用正确的配置文件格式之后，我们就离这个恶意软件的底层原理越来越近了。但是，仍然存在一些问题。我们重新看一下放置在`myDecode`函数上的断点，然后再次打印出每个解码后的值。大家可能还记得，我们尝试打印出的第六个字符串是一个空字符串。我们现在来看看这个位置是否有变化。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016b6ffe985c6acc59.png)

这时，解码后的字符串现在显示为“749060607”。需要注意的是，这个字符串在“domain”字符串解码后立即被解码。只需简单观察即可发现，它与我们提供的localhost IP地址（127.0.0.1）长度相同。

如果我们使用自行编写的myDecode.py脚本，并在127.0.0.1上面运行，是否有可能得到“749060607”呢？

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01528f9f13f1fd6b73.png)

果然！似乎是这样。事实证明，我们在配置文件中使用的IP地址必须使用XOR方式进行编码。对于攻击者来说，这无疑是明智的。这样就可以确保研究人员即使找到配置文件，也无法直接看到纯文本形式的命令和控制IP/域名。如果攻击者使用的是已知的恶意IP地址，通过这样的方式，比较不容易通过简单的YARA规则来提取其C2。因此，如果我们希望看到与该恶意软件的成功连接，必须确保首先对存储在配置文件中的IP或域名进行了相应的编码。由于XOR是双向加密/解密的，并且我们已经知道了使用的方式，因此这一过程就变得非常简单。我们可以在Python的myDecode脚本中实现：

ascii = (ord(x) + 0x4) ^ 0x2<br>
ascii = (ord(x) – 0x4) ^ 0x2

这样，我们就得到了所需的编码后的127.0.0.1，在我们更新配置文件后，恶意软件就可以对其进行正确解码。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012bbaedc4249e5ca1.png)

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01be27bda8f049eda7.png)

现在，我们已经准备好重新建立与C2服务器的连接。但是，TinyTim还包含另外一种反调试技巧。如果我们再次查看伪代码版本的`main()`函数，我们会注意到，被调用的`connect()`函数取决于不匹配的字符串比较。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fe7783fb812e88c4.png)

我们现在可以在`strcmp`函数上添加一个断点，并通过打印寄存器RDI和RSI（即传递给`strcmp`的第一个和第二个参数）来查看正在比较的内容。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0103724867bafc8571.png)

当然，在连接到指定的C2之前，我们需要进行检查，以确保没有尝试连接到运行恶意软件的同一台计算机。有很多方法可以解决这个问题，为简单起见，我在虚拟机中启动了Tinyshell服务器，获取虚拟机的本地IP地址，使用XOR对IP地址进行编码，然后将其添加到配置文件中。于是，问题解决。现在，运行TinyTim后，在我的虚拟机上将会创建返回到Tinyshell服务器的连接。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0168ddea4aa3b897e9.png)

TinyTim需要密码，这也是意料之中的，因为原本的Tinyshell就要求用户输入密码。但是，我们此前并没有在配置文件中看到指定的密码选项，所以判断它一定是存储在可执行文件中。开源的Tinyshell中，将密码命名为“secret”。因此，我们可以使用Hopper来简单地搜索“secret”。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0182083881bd2f7958.webp)

在这里，我们看到有一个XREF指向了一个值得关注的字符串“`lcc ,./3”。我们可以尝试使用这个密码作为密码。但是，与这个可执行文件中的其他所有字符串一样，这个字符串被编码的概率非常大。因此，我们首先使用Python脚本，对其进行解码。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b4c8156ec511314d.png)

得到的密码是：free&amp;2015。

[![](./img/203643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0163216b4599e81b20.png)

最后，我们终于可以按照原计划进行尝试。我们最开始的目标就是希望让恶意软件连接到我们的C2服务器，以确认是否可以通过任何方式对其进行进一步修改。事实证明，在此之后，恶意软件的行为就如同开源的Tinyshell一样。因此，我们判断，攻击者主要就是增加了编码字符串、用于快速修改的配置文件和部分反调试技术。


