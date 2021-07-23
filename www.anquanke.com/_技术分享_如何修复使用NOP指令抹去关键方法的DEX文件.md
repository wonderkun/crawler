> 原文链接: https://www.anquanke.com//post/id/85886 


# 【技术分享】如何修复使用NOP指令抹去关键方法的DEX文件


                                阅读量   
                                **180449**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fortinet.com
                                <br>原文地址：[http://blog.fortinet.com/2017/04/05/how-to-repair-a-dex-file-in-which-some-key-methods-are-erased-with-nops](http://blog.fortinet.com/2017/04/05/how-to-repair-a-dex-file-in-which-some-key-methods-are-erased-with-nops)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p4.ssl.qhimg.com/t01f5e3535440c51974.jpg)](https://p4.ssl.qhimg.com/t01f5e3535440c51974.jpg)

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：140RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

在分析Android恶意软件的过程中，我们经常会碰到某些APK样本对主逻辑代码进行了隐藏或加密处理，只有在某些时刻才会将真正的代码释放到内存中，因此我们需要找到正确的时机才能提取这些代码。本文中，我将举例说明，当一个DEX文件中的某些关键方法被NOP指令抹去后，我们如何去修复这个文件，并且在程序执行时动态解压其代码。

请注意，以下的分析基于Android 4.4.2_r1版本（KOT49H）。

<br>

**二、具体操作**

首先，我们使用某些反编译工具打开一个classes.dex文件，如下所示：

[![](https://p2.ssl.qhimg.com/t01a2a6dcd3834f0f22.png)](https://p2.ssl.qhimg.com/t01a2a6dcd3834f0f22.png)

图1. DEX文件的反编译结果

在图1中，我们可以看到每个函数的代码全部被抹去了。接下来，我们先使用010 Editor来解析这个Dex文件，如图2所示。

[![](https://p0.ssl.qhimg.com/t01941ed4900e477ce1.png)](https://p0.ssl.qhimg.com/t01941ed4900e477ce1.png)

图2. 010 Editor无法解析此Dex文件

看来010 Editor无法解析classes.dex文件，原因可能在于Dex文件中的某些字段已经被修改过。这些字段可能包含某些偏移量信息，用来标识文件内部的偏移量。如果偏移量的值超过了DEX文件的大小，会导致文件解析错误。

该Dex文件的大小为0x2B2DD8。

我写了一个C++程序来解析Dex文件，检查其中不正常的字段，部分输出结果如图3所示。

[![](https://p0.ssl.qhimg.com/t01dc104f50f53fcdc0.png)](https://p0.ssl.qhimg.com/t01dc104f50f53fcdc0.png)

图3. 使用C++程序解析Dex文件的输出结果

我们可以看到DexCode结构中，“debugInfoOff”字段的值不正常，超过了文件本身的0x2b2dd8大小。此例中，这些不正常的debugInfoOff字段取值范围在0x3ffff30到0x4000000之间。

[![](https://p3.ssl.qhimg.com/t01160af41ba88079d8.png)](https://p3.ssl.qhimg.com/t01160af41ba88079d8.png)

图4. DexCode结构体的定义

为使010 Editor能正确解析这个Dex文件，我修复了文件debugInfoOff字段的值。我以MainActivity类中的“OnCreate”方法为例，演示修复过后的Dex文件在010 Editor中的解析结果。

[![](https://p1.ssl.qhimg.com/t017d04e4b052783389.png)](https://p1.ssl.qhimg.com/t017d04e4b052783389.png)

图5. 修复过后的Dex文件在010 Editor中的解析结果

接下来我将debugInfoOff的值修改为0。insns_size字段代表了代码中指令的长度，每一条指令包括2个字节，因此代码的长度为0x76。“OnCreate”方法的具体代码以“0E 00”字节码开始，其余部分全部为NOP指令。“0E 00”字节码代表的是void返回类型。

现在的问题是，如何获取该方法的真正字节码？图5中，某些关键方法已经被NOP指令抹去了。程序准备调用某个方法前，会先对该方法中的字节码进行解密，调用完毕后程序会使用原始的NOP字节码重新替换填充。

在Dalvik虚拟机中，方法在调用时其字节码必须是正确的。换句话说，如果某个方法不处于调用状态，那么它的字节码可能是错误的。这个样本充分利用了这一点，实现了对方法的动态解密调用。

随后，我研究如何在方法调用前对其进行动态解密。通过某些逆向工程及分析工作，我发现该程序可以hook dalvik虚拟机中的dvmResolveClass方法。当某个类中的方法被调用时，整个类必须完成加载过程，dvmResolveClass方法正是在类的加载过程被调用。

下图是IDA Pro中dvmResolveClass方法的ARM指令：

[![](https://p3.ssl.qhimg.com/t01f3c91607d5408775.png)](https://p3.ssl.qhimg.com/t01f3c91607d5408775.png)

图6. IDA Pro中dvmResolveClass方法的ARM指令

接下来，我继续使用IDA Pro进行动态调试，分析hook后的dvmResolveClass方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01362899acd4e650bf.png)

图7. hook后的dvmResolveClass方法

当执行arm指令时，程序跳转到了sub_75485310子函数，图8显示了sub_75485310的执行流程。

[![](https://p5.ssl.qhimg.com/t013d00aed83ba6b51c.png)](https://p5.ssl.qhimg.com/t013d00aed83ba6b51c.png)

图8. sub_75485310的执行流程

图8中，ARM指令“BLX R3”用来调用真正的dvmResolveClass方法。之后程序执行位于0x75938000地址的指令。运行到0x75938014地址时，程序会跳转到0x414E468A地址，调用实际的dvmResolveClass方法，如图9所示。

[![](https://p1.ssl.qhimg.com/t01ddb2f6f84818ce61.png)](https://p1.ssl.qhimg.com/t01ddb2f6f84818ce61.png)

图9. 从0x75938000地址开始程序的执行流程

[![](https://p2.ssl.qhimg.com/t01aa6252cee30f3ff3.png)](https://p2.ssl.qhimg.com/t01aa6252cee30f3ff3.png)

图10. 返回到实际的dvmResolveClass方法

现在程序成功hook了dvmResolveClass方法，此时此刻，关键方法的正确字节码也已经加载到内存中，具体保存在Method结构的insns指针中。Method结构体的定义如图11所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f1473f1d067fcac7.png)

图11. Method结构体的定义

接下来，我们可以修改dvmResolveClass方法的源代码，提取真正的字节码。

部分关键代码如下图所示。

[![](https://p0.ssl.qhimg.com/t015d17898283e3a09e.png)](https://p0.ssl.qhimg.com/t015d17898283e3a09e.png)

图12. 在dvmResolveClass方法中添加关键代码以获取实际字节码

现在我们可以将真正的字节码保存为本地文件。

[![](https://p2.ssl.qhimg.com/t01e84f3528d87940a4.png)](https://p2.ssl.qhimg.com/t01e84f3528d87940a4.png)

图13. 保存为本地文件中的真正字节码

最后，结合图13与图3的输出结果，我研发了一个python脚本，用来修改原始的classes.dex文件，修改后的文件如下图所示。

[![](https://p1.ssl.qhimg.com/t0193f3d029a73601b1.png)](https://p1.ssl.qhimg.com/t0193f3d029a73601b1.png)

图14. dex文件修改前后的对比

[![](https://p0.ssl.qhimg.com/t01c3e3143364241804.png)](https://p0.ssl.qhimg.com/t01c3e3143364241804.png)

图15. 使用dex反编译工具处理修改后的dex文件

对比图1和图15的结果，我们可以看到原来那些经过特殊处理的指令已经恢复正常。

<br>

**三、总结**

Android系统是个开源系统，通过阅读AOSP（Android Open Source Project，Android开源项目）的源代码，我们可以深入分析理解dalvik虚拟机的具体实现。读者也可以自行修改dalvik虚拟机的源代码，开发工具来修复其他经过混淆加固的DEX文件。
