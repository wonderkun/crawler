> 原文链接: https://www.anquanke.com//post/id/87058 


# 【技术分享】Chrome浏览器安全之沙盒逃逸（下）


                                阅读量   
                                **105021**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：technet.microsoft.com
                                <br>原文地址：[https://blogs.technet.microsoft.com/mmpc/2017/10/18/browser-security-beyond-sandboxing/](https://blogs.technet.microsoft.com/mmpc/2017/10/18/browser-security-beyond-sandboxing/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t017e5493f3f8d9c68c.jpg)](https://p3.ssl.qhimg.com/t017e5493f3f8d9c68c.jpg)



译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**传送门**

[](http://bobao.360.cn/learning/detail/4580.html)[****](http://bobao.360.cn/learning/detail/4580.html)**[<strong>【技术分享】Chrome浏览器安全之沙盒逃逸（上）**](http://bobao.360.cn/learning/detail/4580.html)</strong>



**引发信息泄漏**

现在，对于这个bug，要想知道我们可以用它做什么或不能做什么的最简单的方法，就是直接使用测试用例。例如，我们可以考察通过未初始化的指针来改变我们要加载的字段的类型的效果：

[![](https://p4.ssl.qhimg.com/t019312406a7d185c22.png)](https://p4.ssl.qhimg.com/t019312406a7d185c22.png)

结果是，现在该字段直接作为float加载，而不是一个对象指针或SMI加载：

[![](https://p3.ssl.qhimg.com/t0199915617b3bc4f20.png)](https://p3.ssl.qhimg.com/t0199915617b3bc4f20.png)

类似地，我们可以尝试向对象添加更多的字段：

[![](https://p2.ssl.qhimg.com/t0163df3a377994acc2.png)](https://p2.ssl.qhimg.com/t0163df3a377994acc2.png)

运行后将出现以下崩溃：

 [![](https://p5.ssl.qhimg.com/t015468640410bb8931.png)](https://p5.ssl.qhimg.com/t015468640410bb8931.png)

这非常有趣，因为它看起来像是通过为对象添加字段而改变了加载字段的偏移量。事实上，我们计算一下，就会发现（0x67 – 0x1f）/ 8 = 9，这正是我们从o.b.ba.bab添加的字段数。这同样适用于rbx加载有关的新偏移量。

经过多次测试后，我们可以确认，我们对加载未初始化指针的偏移量实现了绝对的控制，即使这些字段都没有被初始化。这时，了解是否可以将任意数据放入这个内存区域是非常有用的。结合前面对0xbadc0de的测试来看，我们好像是可以做到这一点的，但每次运行测试用例时，这个偏移量好像都会发生变化。通常，利用值喷射可以解决这个问题。原因是，如果我们无法准确地将目标陷入某一特定的地点，我们可以改变目标，让它变得更大一些。实际上，我们可以通过使用内联数组来喷射值： 

 [![](https://p4.ssl.qhimg.com/t015b66ca25dc0ac738.png)](https://p4.ssl.qhimg.com/t015b66ca25dc0ac738.png)

查看crash dump，我们发现：

 [![](https://p4.ssl.qhimg.com/t0142c790402b752c32.png)](https://p4.ssl.qhimg.com/t0142c790402b752c32.png)

这里的崩溃情况与以前基本相同，但如果我们查看未初始化数据所来自的内存区域的话，我们会发现：

 [![](https://p5.ssl.qhimg.com/t019b3a88af1db14d9d.png)](https://p5.ssl.qhimg.com/t019b3a88af1db14d9d.png)

我们现在找到了一大片完全由脚本控制的值，其偏移量位于r11中。将这个观察结果与以前的观点结合起来：

 [![](https://p2.ssl.qhimg.com/t01c9268e1478a36755.png)](https://p2.ssl.qhimg.com/t01c9268e1478a36755.png)

结果是我们现在可以对来自任意地址的任意浮点值解引用了：

 [![](https://p5.ssl.qhimg.com/t0150dce5bcfbb1227f.png)](https://p5.ssl.qhimg.com/t0150dce5bcfbb1227f.png)

这当然是非常强大的：它直接带来了一个任意的读取原语。不幸的是，没有初始信息泄漏的任意读取原语并不那么有用：**我们需要知道要读取哪些地址才能使用它**。

由于变量v可以是我们想要的任何东西，所以可以用一个对象替换它，然后读取它的内部字段。例如，我们可以使用自定义回调函数的调用来替换对**Object.toString()**的调用，并将V替换为DataView对象，读回该对象的后备存储器的地址。这为我们寻找完全受脚本控制的数据提供了一种方法：

 [![](https://p3.ssl.qhimg.com/t014d4f110a0ef77a83.png)](https://p3.ssl.qhimg.com/t014d4f110a0ef77a83.png)

以上代码返回： 

 [![](https://p4.ssl.qhimg.com/t016fe50726b5fedc69.png)](https://p4.ssl.qhimg.com/t016fe50726b5fedc69.png)

使用WinDbg，我们可以证实这的确是缓冲区的后备dump：

 [![](https://p2.ssl.qhimg.com/t01cd7b46d1db312b1e.png)](https://p2.ssl.qhimg.com/t01cd7b46d1db312b1e.png)

这同样是一个非常强大的原语，我们可以使用它来泄漏对象的任何字段以及任何JavaScript对象的地址，因为这些对象有时被存储为其他对象中的字段。



**构建任意的读/写原语**

能够以已知地址放置任意数据意味着我们可以解锁更强大的原语：创建任意JavaScript对象的能力。 只需将从float读取的字段的类型更改为对象，就可以从内存中的任何位置读取一个对象指针，包括我们已经知道地址的缓冲区。 为了进行相应的测试，可以使用WinDbg通过以下命令将受控数据放置到已知地址中： 

 [![](https://p4.ssl.qhimg.com/t013042a1ff6656ec95.png)](https://p4.ssl.qhimg.com/t013042a1ff6656ec95.png)

这将在我们的任意对象指针的加载位置放置一个表示整数0xbadc0de的SMI。由于我们没有设置最低有效位，所以它将被V8解释为内联整数：

 [![](https://p1.ssl.qhimg.com/t01be238670458c41fd.png)](https://p1.ssl.qhimg.com/t01be238670458c41fd.png)

如预期的那样，V8将打印以下输出：

 [![](https://p2.ssl.qhimg.com/t019399fb9a4d808f86.png)](https://p2.ssl.qhimg.com/t019399fb9a4d808f86.png)

这样的话，说明我们能够创建任意对象。因此，我们可以通过创建伪造的DataView和ArrayBuffer对象来形成任意的读/写原语。我们再次通过WinDbg将我们伪造的对象数据放入已知位置：

 [![](https://p3.ssl.qhimg.com/t0103b478e372e64611.png)](https://p3.ssl.qhimg.com/t0103b478e372e64611.png)

然后我们用以下JavaScript进行测试：

 [![](https://p3.ssl.qhimg.com/t016fd75003d56c351d.png)](https://p3.ssl.qhimg.com/t016fd75003d56c351d.png)

如预期的那样，调用DataView.prototype.setUint32会触发崩溃，并尝试将值0xdeadcafe写入0x00000badbeefc0de：

 [![](https://p5.ssl.qhimg.com/t019786164c89d94897.png)](https://p5.ssl.qhimg.com/t019786164c89d94897.png)

为了控制数据的写入或读取地址，只需修改一下通过WinDbg填充的obj.arraybuffer.backing_store内存即可。因为在真正的exploit中，待修改的内存将成为实际的ArrayBuffer对象的后备存储的一部分，对其进行修改并非难事。例如，下面便是一个写入原语：

 [![](https://p2.ssl.qhimg.com/t019f2b934c77d2239c.png)](https://p2.ssl.qhimg.com/t019f2b934c77d2239c.png)

在这种情况下，我们可以通过JavaScript对Chrome渲染器进程中的任意内存位置进行可靠地读写操作。 

<br>

**执行任意代码 **

获得任意的读/写原语后，在渲染器进程中实现代码执行是比较容易的。在执行写入操作时，V8会赋予JIT代码页read-write-execute（RWX）权限，这意味着可以通过定位JIT代码页，对其进行覆盖，然后调用它来完成代码的执行。在实践中，可以通过信息泄漏来定位JavaScript函数对象的地址并读取其函数的entrypoint字段来达到这个目的。一旦将代码放入这个入口点后，我们便可以调用JavaScript函数来执行代码。对于JavaScript来说，代码如下所示：

 [![](https://p5.ssl.qhimg.com/t0152fbaf7dae0c6cbc.png)](https://p5.ssl.qhimg.com/t0152fbaf7dae0c6cbc.png)

值得注意的是，即使V8没有使用带有RWX权限的页面，由于缺乏控制流完整性检查，仍然很容易触发ROP链。在这种情况下，我们可以覆盖JavaScript函数对象的entrypoint字段，使其指向所需的gadget，然后进行函数调用。

这些技术都无法直接用于具有CFG和ACG功能的Microsoft Edge。在Windows 10 Creators Update中引入的ACG，会执行严格的DEP检测，并将JIT编译器移到外部进程。这样做可以确保攻击者无法覆盖可执行代码，除非他们已经攻陷了JIT进程，但是这需要发现并利用其他漏洞。

另一方面，CFG可以确保间接调用方只能跳转到某一组函数，这意味着它们无法直接执行ROP。Creators Update还引入了CFG禁止导出特性，通过从有效的目标集中删除大多数导出的函数，大大减少了有效的CFG间接调用目标。所有这些缓解措施和其他保护措施结合在一起，使得利用Microsoft Edge中的RCE漏洞变得更加困难。 

<br>

**RCE的危险性 **

Chrome是一款现代化的网络浏览器，采用了多进程模式。所以，它涉及到多种进程类型：浏览器进程、GPU进程和渲染器进程。正如其名称所示，GPU进程用来处理GPU与需要使用它的所有进程之间的交互，而浏览器进程则是一个用来处理访问从文件系统到网络的所有过程的全局管理器进程。

渲染器是一个或多个选项卡背后的大脑——它负责解析和解释HTML、JavaScript等。沙箱模型使得这些进程只能访问其需要的功能。因此，如果无法找到一个辅助漏洞从沙箱溢出的话，攻击者很难通过渲染器彻底拿下受害者的机器。

鉴于此，我们很想知道攻击者是否可以在不借助辅助漏洞的情况下拿下机器。虽然大多数选项卡在个别进程中都是隔离的，但情况并不总是如此。例如，如果您在bing.com上使用JavaScript开发者控制台（可以通过按F12打开该控制台）来运行window.open('https://microsoft.com')的话，则会打开一个新的选项卡，但是它通常将与原始标签位于同一个进程中。为此，可以通过Chrome的内部任务管理器进行检查。要想打开这个管理器，可以使用Shift + Escape组合键： 

 [![](https://p5.ssl.qhimg.com/t0131945554859356a0.png)](https://p5.ssl.qhimg.com/t0131945554859356a0.png)

如果您仔细观察的话，会发现非常有趣，因为它表明渲染器进程没有被锁定到任何一个源。这意味着，如果在渲染器进程中实现任意代码执行的话，使攻击者可以访问其他源。虽然攻击者以这种方式获得的绕过SOP策略的能力看上去无关痛痒，但后果却非常严重：

攻击者可以通过劫持PasswordAutofillAgent界面窃取为任何网站保存的密码。

攻击者可以将任意JavaScript注入到任意的页面（称为通用跨站点脚本或UXSS），例如劫持**blink::ClassicScript::RunScript**方法。

攻击者可以在后台中导航到任意的网站，而不会引起用户的察觉，例如，创建隐藏的弹出式窗口。这完全是可能的，因为许多用户交互检查是在渲染器进程中，而非浏览器进程中完成的。结果就是，攻击者可以在无需人工交互的情况下劫持像**ChromeContentRendererClient::AllowPopup**这样的东西，也就是说，攻击者就可以隐藏新建窗口了。他们还可以在弹出式窗口被关闭时弹出一个新的窗口，例如，通过hooking onbeforeunload窗口事件就能达到这个目的。

为了更好地实施这种攻击，需要研究渲染器和浏览器进程的通信方式，然后直接模拟相关消息，不过对于这种攻击来说，只需付出有限的努力就可以实现。虽然双因子身份验证的普及能够降低密码被窃的风险，但是由于攻击者可以在用户已经登录的网站中骗取其身份凭证，所以他们仍然能够以用户的身份横冲直撞。 



**小结**

****

在本文中，我们深入分析了Google的Chrome浏览器中的沙盒逃逸的漏洞根源，以及具体的利用方法，希望本文对读者能够有所帮助。
