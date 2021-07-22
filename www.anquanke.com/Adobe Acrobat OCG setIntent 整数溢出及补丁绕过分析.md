> 原文链接: https://www.anquanke.com//post/id/146797 


# Adobe Acrobat OCG setIntent 整数溢出及补丁绕过分析


                                阅读量   
                                **109669**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.zerodayinitiative.com/
                                <br>原文地址：[https://www.zerodayinitiative.com/blog/2018/5/29/malicious-intent-using-adobe-acrobats-ocg-setintent](https://www.zerodayinitiative.com/blog/2018/5/29/malicious-intent-using-adobe-acrobats-ocg-setintent)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01bbd0d7d2841ad1a1.png)](https://p5.ssl.qhimg.com/t01bbd0d7d2841ad1a1.png)



## 介绍

在过去的几年中，我们看到了关于Adobe的漏洞数量激增，可见Adobe Acrobat和Reader拥有相当大的关注度。虽然大多数这些漏洞都是些简单的文件分析问题，但也有不少`XML Forms Architecture（XFA）`和`JavaScript`漏洞。JavaScript漏洞对于攻击者来说是最有趣的，因为这给攻击者提供控制权`(allocations/frees/spraying 等)`。Acrobat中的JavaScript引擎存在许多漏洞，我们今年发布的关于Acrobat的80条建议就是明证。<br>
在这篇博文中，我将讨论我们通过程序[ZDI-18-173](https://www.zerodayinitiative.com/advisories/ZDI-18-173/)收到的一个漏洞，它影响了`setIntent`可选内容组`(OCG) JavaScript`函数。这个漏洞很有趣，不仅是因为Adobe试图修补它的方式。我们接下来一起来看看吧！



## 概观

[OCG](https://acrobatusers.com/tutorials/print/creating-and-using-layers-ocgs-with-acrobat-javascript)用于控制页面内容的可见性。在Acrobat中，可以通过JavaScript创建和控制这些图层。<br>
例如，我们可以通过`addWatermarkFromText`函数创建一个简单的`OCG` ：

```
this.addWatermarkFromText(“AAA”);
```

我们可以通过`getOCGs`函数检索`OCGs`:

```
this.getOCGs();
```

[![](https://p2.ssl.qhimg.com/t0104c6d6cda89e8c1f.png)](https://p2.ssl.qhimg.com/t0104c6d6cda89e8c1f.png)

`OCG`对象公开了允许我们在一定程度上控制图层的各种属性和方法。我比较感兴趣`setIntent`方法。该方法用于设置`OCG intent`数组。

[![](https://p4.ssl.qhimg.com/t017164c844e465d745.png)](https://p4.ssl.qhimg.com/t017164c844e465d745.png)<br>
根据`JavaScript API`参考，此函数将数组作为参数。我们可以从控制台验证这一点：

[![](https://p4.ssl.qhimg.com/t014e3b91a8bc884e39.png)](https://p4.ssl.qhimg.com/t014e3b91a8bc884e39.png)



## The Bug

`setIntent`在内部实现`Escript.api`，位于`Acrobat`中的`plug-ins`文件夹内。我不会深入研究如何在`Escript`中找到`setIntent`，我们将在以后的MindshaRE博客中讨论。

现在，让我们假设，我们设`setInten`在`Escript`：

[![](https://p4.ssl.qhimg.com/t01ae00f021dd817f3f.png)](https://p4.ssl.qhimg.com/t01ae00f021dd817f3f.png)<br>
我删除了`sub_238B9F62`函数的反编译代码的一部分，只保留了其相关部分：

[![](https://p1.ssl.qhimg.com/t015985b580a8bfec55.png)](https://p1.ssl.qhimg.com/t015985b580a8bfec55.png)

在上面的图2的[1]中，获取数组的长度属性并由攻击者完全控制。然后在上图中的[3]处，根据[2]计算的大小分配内存。最后，在[4]中，该长度用于溢出分配缓冲区的循环中：

[![](https://p0.ssl.qhimg.com/t0149ef8ecbfa242443.png)](https://p0.ssl.qhimg.com/t0149ef8ecbfa242443.png)



## POC

[![](https://p5.ssl.qhimg.com/t0110edf8498758de2e.png)](https://p5.ssl.qhimg.com/t0110edf8498758de2e.png)<br>
从逻辑上讲，任何导致`wrap（&gt; 0x7FFFFFFF）`的值都会带有易受攻击的代码路径。因此，在修正bug时应考虑到这个问题。然而，Adobe的开发人员决定采用修补程序快捷方式：

[![](https://p0.ssl.qhimg.com/t015fca581e234971d6.png)](https://p0.ssl.qhimg.com/t015fca581e234971d6.png)<br>
他们想确保大小不是完全 `0x7FFFFFFF`。显然，这是不够的，因为这不是触发错误的唯一值。

一旦补丁出来，研究人员不会浪费时间。几个小时后，他直接给我们发送了补丁。POC看起来与原来的POC完全一样，但有一点小改变：将数组长度设置为`0xFFFFFFFF`而不是`0x7FFFFFFF`。同样，任何大于`0x7FFFFFFF的`值都可以。下图是bypass：

[![](https://p0.ssl.qhimg.com/t0195c7c73bbcb5b0e9.png)](https://p0.ssl.qhimg.com/t0195c7c73bbcb5b0e9.png)<br>
这一次，Adobe的开发人员提出以下解决方案来避免整数换行：

[![](https://p5.ssl.qhimg.com/t01c684aed45d25ccb3.png)](https://p5.ssl.qhimg.com/t01c684aed45d25ccb3.png)



## 结论

Adobe Acrobat的攻击面之大令人惊讶。想想有多少系统安装了Acrobat。更严重的是缺乏高级的缓解措施，使得它比其他应用程序更容易定位。再加上一些不太合适的补丁，这就是为什么它仍然是研究人员的热门目标。与其他厂商相比，Acrobat追赶现代还有很长的路要走，我们将密切关注他们的改进。在此之前，Acrobat可能仍然是寻找bug的目标。
