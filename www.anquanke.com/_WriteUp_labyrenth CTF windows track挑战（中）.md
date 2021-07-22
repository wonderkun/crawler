> 原文链接: https://www.anquanke.com//post/id/84540 


# 【WriteUp】labyrenth CTF windows track挑战（中）


                                阅读量   
                                **70619**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0126a05cb6036cec89.jpg)](https://p2.ssl.qhimg.com/t0126a05cb6036cec89.jpg)

**文件： SquirtleChallenge.exe**

**SHA256:**360BB1FF6D129C99BC7B361A7B52C4CBDE04E5710101C866893DBB7236815E15

**加壳：**无

**体系结构:** 32Bit

**使用工具:** exeinfo, IDA Pro

**代码与二进制文件：**[https://github.com/jmprsp/labyrenth/tree/master/Window-Challenge-3](https://github.com/jmprsp/labyrenth/tree/master/Window-Challenge-3)

**说明：**这种挑战是用 C语言编写的，并且完全没有进行加壳。绕过标记需要很多反调试器的技巧。

[![](https://p0.ssl.qhimg.com/t01497994b7506018a9.png)](https://p0.ssl.qhimg.com/t01497994b7506018a9.png)

 

  我们可以从上述的数字导出没有进行加壳的文件。

  让我们尝试运行程序。

[![](https://p1.ssl.qhimg.com/t019a81fc4b2a847a49.png)](https://p1.ssl.qhimg.com/t019a81fc4b2a847a49.png)

 

  我们估计需要加载 IDA Pro ，并且开始查找字符串。

  我们首先需要知道密码是什么，每次输入错误都会导致 Squirtle出现问题。

[![](https://p1.ssl.qhimg.com/t0176bd67066cbeb376.png)](https://p1.ssl.qhimg.com/t0176bd67066cbeb376.png)

 

  从上图我们不难发现主函数调用的是密码检查。

[![](https://p4.ssl.qhimg.com/t01c524b78dd0bcdbc5.png)](https://p4.ssl.qhimg.com/t01c524b78dd0bcdbc5.png)

 

   所以我们定位了 squirtle 杀手，通过阅读装配说明我们可以看到，密码是"incorrect"。

[![](https://p0.ssl.qhimg.com/t01f429f40fdd37beb5.png)](https://p0.ssl.qhimg.com/t01f429f40fdd37beb5.png)

 

  让我们再来看一下是否有squirtle出现问题。

 

[![](https://p5.ssl.qhimg.com/t012bb4e19e8d6ad800.png)](https://p5.ssl.qhimg.com/t012bb4e19e8d6ad800.png)



  然而，answer.jpg 还是没有标记。

  看起来像是存在很多反调试器检查防止我们生成正确的 answer.jpg。让我们简单修补一下二进制文件。

[![](https://p2.ssl.qhimg.com/t017ffd8af7f03913b4.png)](https://p2.ssl.qhimg.com/t017ffd8af7f03913b4.png)

 

  一个简单的方法就是将mov eax，0 修补成 0x00401062；或者当它试验 eax 时修补程序调用方。下图所示就是Squirtle的活跃状态。

[![](https://p4.ssl.qhimg.com/t012792b325ed9ea8d8.png)](https://p4.ssl.qhimg.com/t012792b325ed9ea8d8.png)

 

  上图演示的是一种非常常见的技术，用于检查是否存在调试器标记附加调试器。如果你一直在关注我的博客，这对你来说一定很熟悉了。对于这一种挑战来说似乎还是要调试。我仅仅是将jz 修补称 jnz @ 0x401684。如下图所示，Squirtle 也一切正常。

[![](https://p1.ssl.qhimg.com/t011c4a0922b93c9603.png)](https://p1.ssl.qhimg.com/t011c4a0922b93c9603.png)

 

  只是修补 @ 0x401a45 （从 jbe 到ja） 指令，看一下是否可行。

  我们成功了！Squirtle 不再出现问题了！

[![](https://p0.ssl.qhimg.com/t010e4dd8e2c6176062.png)](https://p0.ssl.qhimg.com/t010e4dd8e2c6176062.png)

 

  让我们来看一下answer.jpg，接下来只需要解码。

[![](https://p2.ssl.qhimg.com/t01a022b791a4cb00ec.png)](https://p2.ssl.qhimg.com/t01a022b791a4cb00ec.png)

 

[![](https://p1.ssl.qhimg.com/t011496b3a618f48bd7.png)](https://p1.ssl.qhimg.com/t011496b3a618f48bd7.png)

 

标记: PAN`{`Th3_$quirtL3_$qu@d_w@z_bLuffiNg`}`



**文件: JugsOfBeer.exe**

**SHA256**：59E71EE7A6C110D77CB19337EF2E7DA26C9E367D44588C09C6A4635D91318D0A

**加壳**：无

**体系结构: **64Bit

**使用工具: **exeinfo, IDA Pro

**代码与二进制文件：**[https://github.com/jmprsp/labyrenth/tree/master/Window-Challenge-4](https://github.com/jmprsp/labyrenth/tree/master/Window-Challenge-4)

**说明：**这种挑战是用 c 语言编写的，并且使用64 位二进制编译。它是Water pouring puzzle修改后的版本。要解决这一挑战，需要找到最简洁的步骤达到指定的结束状态。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014709f277a90db9bd.png)

 

  所面临的挑战是来自用户的输入，这是否是典型的串行插件挑战？让我们检查看看它是否是通过 exeinfo 和 IDA Pro.进行加壳的。从以下的数据可以看出该二进制文件没有进行加壳。

[![](https://p5.ssl.qhimg.com/t018b76f746e406d28f.png)](https://p5.ssl.qhimg.com/t018b76f746e406d28f.png)

 

[![](https://p3.ssl.qhimg.com/t01175cd3e9a2d9563b.png)](https://p3.ssl.qhimg.com/t01175cd3e9a2d9563b.png)

 

  让我们开始分析。上图标出的是背跟踪字符串，其中遇到了 @ 0x0140001280 函数。

  如果你要分析函数，首先会遇到一个检查。

[![](https://p3.ssl.qhimg.com/t01636f533fed4d6a3f.png)](https://p3.ssl.qhimg.com/t01636f533fed4d6a3f.png)

 

 从上图中我们可以看出，输入的字符串必须是 32 个字符长。进一步深入之后我们会遇到检查，以确保输入的字符必须是 &gt; = 0x31 并且&lt; = 33。

  若要手动检查，假设我们输入 0，相当于 0x30。添加 0x30 到 0xFFFFFFCF 会返回 0xFFFFFFFF ，这样的检查测试就是失败的。

  如果我们输入值是4，总和将会是 0x100000003。现在的检查只需要最后4 个字节，因此我们再比较 3和2。因为 3 大于 2，所以测试再次失败。

  能够通过测试的唯一值就是在1 和 3 之间。



[![](https://p5.ssl.qhimg.com/t01e7f55709d60a3fe8.png)](https://p5.ssl.qhimg.com/t01e7f55709d60a3fe8.png)

 

 如果我们设法清除所有验证测试，我们将会在(0x140001750)函数中到达该地址 0x14000151C 。如果此函数返回 0，我们会得到一个"再试一次"的消息。这么看来，我们需要确保此函数返回值是 1。

[![](https://p4.ssl.qhimg.com/t017af79f3296dd7d37.png)](https://p4.ssl.qhimg.com/t017af79f3296dd7d37.png)

 

  缩放到 @ 0x140001750 函数中，我们可以看到它为 0x0，0x0，0xD 0x7 设置了一个变量的初始状态。

[![](https://p2.ssl.qhimg.com/t019c2b1e1bbc6d62b5.png)](https://p2.ssl.qhimg.com/t019c2b1e1bbc6d62b5.png)



进一步深入函数，我们会看到 0 x 的最终状态概览，（也可能是0xA，0xA或是0 x），代码将会设置检查值为 1！

可以观察到的是给定的输入数据以及相应的变量状态变化。换句话说，我们必须正确输入结束状态变量。

我们知道输入应该是32 个字符，这相当于 16 个组合。每个组合都可以是 0x11，0x12，0x13、 0x21、 0x22，0x23，0x31，0x32，0x33这些形式。但是状态不会改变，如果输入的值是 0x11，0x22，0x33，这将可能的输入减少到了只有 0x12，0x13，0x21，0x23，0x31，0x32这几种形式。

因此暴力破解永远不可能是一个明智的选择。

SMT Solver会做这项工作，但是让我们试试更容易的手动处理。我将0x140001750 的代码反编译到 php 脚本中。你可以在本文提供的 github 链接中找到脚本。现在让我们进一步观察。

如上图所示有一些有趣的东西。我们测试了 6种 不同可能的组合作为第一个输入，我们最终只得到了3种不同的结果。第一个输入结果返回到初始状态，所以我们只有 2种不同结果。从下图中，我们只是需要顺着路径继续观察。

 

[![](https://p2.ssl.qhimg.com/t01088349405d2ac137.png)](https://p2.ssl.qhimg.com/t01088349405d2ac137.png)

 

  假设我们只有这一条路径，我们可能永远达不到最终状态！

[![](https://p3.ssl.qhimg.com/t01d3c83f0fe6ba0b42.png)](https://p3.ssl.qhimg.com/t01d3c83f0fe6ba0b42.png)

 

[![](https://p2.ssl.qhimg.com/t0108700b735845a319.png)](https://p2.ssl.qhimg.com/t0108700b735845a319.png)

标记： PAN`{`C0ngr47ulaT1ons_buddy_y0Uv3_solved_the_re4l__prObL3M`}`



<br style="text-indent:2em;text-align:left">
