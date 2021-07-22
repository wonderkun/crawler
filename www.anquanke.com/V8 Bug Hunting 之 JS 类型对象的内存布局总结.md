> 原文链接: https://www.anquanke.com//post/id/185339 


# V8 Bug Hunting 之 JS 类型对象的内存布局总结


                                阅读量   
                                **352745**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者stankoja，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@stankoja/v8-bug-hunting-part-2-memory-representation-of-js-types-ea37571276b8](https://medium.com/@stankoja/v8-bug-hunting-part-2-memory-representation-of-js-types-ea37571276b8)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p1.ssl.qhimg.com/t0159a091d7d2766a0a.jpg)](https://p1.ssl.qhimg.com/t0159a091d7d2766a0a.jpg)



## 相关介绍

在设置好JS调试环境后，现在就可以使用V8了。我想要看的第一件事是各种JS类型在内存中的表现方式，JS类型分为两大类：基本类型（即数字，字符串，布尔…）和对象，我们来看看这两个类别。



## Number

在JavaScript中，所有数字都是双精度数（64位浮点数），这是数字的原始类型。但是V8如何实现它们呢？在大多数情况下，在代码中使用数字时，我们只使用整数。

先来看看我之前博客文章中的截图：

[![](https://p5.ssl.qhimg.com/t01831048e94e88e310.png)](https://p5.ssl.qhimg.com/t01831048e94e88e310.png)

在那里，我创建了一个像= [1,2,3,4,5,6,7,8,9]的数组，并在内存中识别出来。我选择了我认为是数组中的整数2。考虑到在64位系统上并且内存是小端的，我认为这是有意义的。

虽然在C语言中可能有意义，但这并不是像JavaScript这样的高级语言的工作方式。JavaScript是一种动态类型语言，这意味着变量可以包含任何类型，并且为了能够做到这一点，JavaScript需要使用变量存储一些类型信息。

JavaScript Core（WebKit JS引擎）使用**NaN-boxing**将类型信息和变量值存储在64位浮点内。V8使用**标记指针**来做到这一点。由于内存的对齐方式，指针通常指向4或8字节倍数的内存位置。这意味着指针的最后2-3位将始终为0并且永远不会被使用。V8将使用它并将在最后一位内编码某些类型信息。将会是这样的：

**对于指针：**

```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 1
```

对于指针，V8将始终将最后一位设置为1，如果该位为1，则表示我们正在处理指针。这也意味着在使用该指针之前，需要清除最后一位（将其设置为0），因为它被设置为1只是为了将该变量标记为指针。

**对于小整数（SMI）：**

```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 0
```

对于小整数（SMI），最后一位将设置为0，这意味着32位系统上的小整数为31位长。

在64位系统上，它的工作略有不同 – SMI为32位，低32位始终设为0：

```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 00000000000000000000000000000000
```

但原理是一样的：如果一个内存位置的最后一位是1，正在处理一个指针，如果它是0，正在处理一个SMI。

通过创建以下数组并在D8中对其执行调试打印来尝试：

```
A = [5， “test”]
```

[![](https://p3.ssl.qhimg.com/t01f8a71874880216dc.png)](https://p3.ssl.qhimg.com/t01f8a71874880216dc.png)

注意这里调试输出中的所有指针是如何将最后一位设置为1的，如果想要使用其中一些指针，必须清除它的最后一位，即该数组的元素地址将变为02ae456d6e98（而不是02ae456d6e99）。

让我们转到WinDbg中的那个地址并查看元素：

[![](https://p0.ssl.qhimg.com/t0119ae5c56e50f90b6.png)](https://p0.ssl.qhimg.com/t0119ae5c56e50f90b6.png)

在那里将找到SMI 5，并在它下面是指向我们的字符串“test”的指针。如果记住内存是little-endian，SMI看起来像是十六进制：

```
00 00 00 05 00 00 00 00
```

这意味着，低32位设置为0，高32位用作SMI值。

现在让我们尝试添加一个大于32位的整数和一个浮点到数组，看看会发生什么：

[![](https://p4.ssl.qhimg.com/t014eea3c5b861b8f54.png)](https://p4.ssl.qhimg.com/t014eea3c5b861b8f54.png)

看到这两个数字都存储在堆上。如果跟踪其中一个指针，将看到两件事：指向map的指针，以及[IEEE 754](https://en.wikipedia.org/wiki/IEEE_754)编码形式的数字/浮点数的值：

[![](https://p5.ssl.qhimg.com/t017cc7fd30b407cd1b.png)](https://p5.ssl.qhimg.com/t017cc7fd30b407cd1b.png)

可以使用任何IEEE 754转换器将这些值转换回十进制格式。



## 字符串和其他原始类型

与浮点数类似，字符串将以类似的方式存储：指向内存位置的指针：1）描述变量的映射 2）变量本身的值。一些不包含任何值的原始数据（如null或undefined）将仅表示为指向map的指针。

值得一提的是，尽管讨论了一些类型如字符串和数字作为基本类型，但也可以将它们创建为对象：

```
var a =“test”; //原始类型
var o = new String（“test”）;
```

那么现在让我们谈个对象吧:)。



## 对象

创建一个对象并为它执行调试打印：

```
var o = `{`color：“yellow”，shape：“round”`}`;
```

[![](https://p0.ssl.qhimg.com/t017871fcaee4f12ef8.png)](https://p0.ssl.qhimg.com/t017871fcaee4f12ef8.png)

尝试在WinDbg中加载该对象的内存地址，因为现在唯一的目标是了解它在内存中的布局：

[![](https://p5.ssl.qhimg.com/t01b07824f603644302.png)](https://p5.ssl.qhimg.com/t01b07824f603644302.png)

为了理解这一点，首先理解JS对象在内存中应该是什么样子：

```
++++++++++++++++++++++++
+      JS OBJECT       +
++++++++++++++++++++++++
|         Map          |
------------------------
|      Properties      |
------------------------
|       Elements       |
------------------------
| In-Object Property 1 |
------------------------
| In-Object Property 2 |
------------------------
|         ...          |
------------------------
```

对象的内存位置的第一个指针是指向该对象的Map的指针。Map类似于隐藏类，它描述了对象的布局，属性名称到偏移的映射，以及其他一些东西，比如指向对象原型的指针。

第二个指针是指向该对象属性的指针。V8中有三种类型的对象属性：
1. Very fast properites
1. Fast properties
1. Slow properties
如果一个对象只有几个属性，V8将直接将它们放在对象本身内。如果属性太多，V8将使用Object中的第二个指针指向包含其他属性的数组，在这种情况下可能是Fast或Slow。[https://v8.dev/blog/fast-properties](https://v8.dev/blog/fast-properties))

Object中的第三个指针是指向对象元素的指针。元素就像属性，但有数字名称，即`{`1：“green”，2：“red”`}`，它们将在数组中使用。

在指针到达所有非常快的属性之后，如果你从上面的截图比较WinDbg内存布局中的第四个内存位置/行，你会看到它包含我们第一个属性的字符串值的地址/指针。

接下来还有更多内容要探索:)



## 参考资料

[https://github.com/thlorenz/v8-perf/blob/master/data-types.md](https://github.com/thlorenz/v8-perf/blob/master/data-types.md)

[https://stackoverflow.com/questions/7413168/how-does-v8-manage-the-memory-of-object-instances](https://stackoverflow.com/questions/7413168/how-does-v8-manage-the-memory-of-object-instances)

[https://v8.dev/blog/fast-properties](https://v8.dev/blog/fast-properties)

[https://javascript.info/primitives-methods](https://javascript.info/primitives-methods)

[https://www.youtube.com/watch?v=5nmpokoRaZI](https://www.youtube.com/watch?v=5nmpokoRaZI)
