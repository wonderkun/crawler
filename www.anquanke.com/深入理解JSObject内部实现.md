> 原文链接: https://www.anquanke.com//post/id/179780 


# 深入理解JSObject内部实现


                                阅读量   
                                **186969**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者liveoverflow，文章来源：liveoverflow.com
                                <br>原文地址：[https://liveoverflow.com/setup-and-debug-javascriptcore-webkit-browser-0x01/](https://liveoverflow.com/setup-and-debug-javascriptcore-webkit-browser-0x01/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0135921be760afe911.png)](https://p4.ssl.qhimg.com/t0135921be760afe911.png)



## 0x00 前言

在本文中，我们来分析JavaScript在内存中的基本结构，同时了解一下其中涉及到的butterfly（蝶式）结构。

我们可以通过内存中的`JSObject`结构来了解`JavaScriptCore`内部实现。之前saelo已经在[phrack](http://phrack.org/papers/attacking_javascript_engines.html)的一篇文章中讨论过这方面内容，但我希望能利用[上篇文章](https://liveoverflow.com/setup-and-debug-javascriptcore-webkit-browser-0x01/)中介绍的调试器技术来分析这些知识点。在上篇文章中，我们快速过了一遍`[1, 2, 3, 4]`数组的内存结构，找到了这些数值，但我们还发现这些数值的高位全都被设置为`0xffff`，这里我们来了解一下为什么会出现这种情况。

[![](https://p1.ssl.qhimg.com/t013b157842eb4fc356.gif)](https://p1.ssl.qhimg.com/t013b157842eb4fc356.gif)



## 0x01 JSValue源代码

JavaScript中有个非常重要的类，可以用来处理各种数值：`JSValue`类。我们可以在[JSCJSValue.h](https://github.com/WebKit/webkit/blob/master/Source/JavaScriptCore/runtime/JSCJSValue.h)源文件中看到类定义，根据类定义，该类应该可以处理各种类型值，如`Integer`、`Double`或者`Boolean`。

```
//[...]
    bool isInt32() const;
    bool isUInt32() const;
    bool isDouble() const;
    bool isTrue() const;
    bool isFalse() const;

    int32_t asInt32() const;
    uint32_t asUInt32() const;
    int64_t asAnyInt() const;
    uint32_t asUInt32AsAnyInt() const;
    int32_t asInt32AsAnyInt() const;
    double asDouble() const;
    bool asBoolean() const;
    double asNumber() const;
//[...]
```

这个类中包含一个编译器开关，针对32位及64位架构可以使用不同的实现。但现在大部分都是64位架构，因此我们主要关注这方面实现。代码中还有一大段注释，解释了什么是`JSValue`。仔细阅读注释，后面我们将多次回顾其中内容。

```
//[...]
#elif USE(JSVALUE64)
    /*
     * On 64-bit platforms USE(JSVALUE64) should be defined, and we use a NaN-encoded
     * form for immediates.
     *
     * The encoding makes use of unused NaN space in the IEEE754 representation.  Any value
     * with the top 13 bits set represents a QNaN (with the sign bit set).  QNaN values
     * can encode a 51-bit payload.  Hardware produced and C-library payloads typically
     * have a payload of zero.  We assume that non-zero payloads are available to encode
     * pointer and integer values.  Since any 64-bit bit pattern where the top 15 bits are
     * all set represents a NaN with a non-zero payload, we can use this space in the NaN
     * ranges to encode other values (however there are also other ranges of NaN space that
     * could have been selected).
     *
     * This range of NaN space is represented by 64-bit numbers begining with the 16-bit
     * hex patterns 0xFFFE and 0xFFFF - we rely on the fact that no valid double-precision
     * numbers will fall in these ranges.
     *
     * The top 16-bits denote the type of the encoded JSValue:
     *
     *     Pointer `{`  0000:PPPP:PPPP:PPPP
     *              / 0001:****:****:****
     *     Double  `{`         ...
     *               FFFE:****:****:****
     *     Integer `{`  FFFF:0000:IIII:IIII
     *          *
     * The scheme we have implemented encodes double precision values by performing a
     * 64-bit integer addition of the value 2^48 to the number. After this manipulation
     * no encoded double-precision value will begin with the pattern 0x0000 or 0xFFFF.
     * Values must be decoded by reversing this operation before subsequent floating point
     * operations may be peformed.
     *
     * 32-bit signed integers are marked with the 16-bit tag 0xFFFF.
     *
     * The tag 0x0000 denotes a pointer, or another form of tagged immediate. Boolean,
     * null and undefined values are represented by specific, invalid pointer values:
     *
     *     False:     0x06
     *     True:      0x07
     *     Undefined: 0x0a
     *     Null:      0x02
     *
     * These values have the following properties:
     * - Bit 1 (TagBitTypeOther) is set for all four values, allowing real pointers to be
     *   quickly distinguished from all immediate values, including these invalid pointers.
     * - With bit 3 is masked out (TagBitUndefined) Undefined and Null share the
     *   same value, allowing null &amp; undefined to be quickly detected.
     *
     * No valid JSValue will have the bit pattern 0x0, this is used to represent array
     * holes, and as a C++ 'no value' result (e.g. JSValue() has an internal value of 0).
     */
```

仔细阅读注释后，大家可以注意到其中涉及到`JSValue`的编码表，其中解释了我们在数组中看到的`0xffff`。`JSValue`可以包含不同类型，通过高位来定义具体是什么类型。注释中也提到了为什么JavaScript即使在64位架构上也只处理32位整数，这是因为`JSValue`通过将顶部32位设置为`0xffff0000`来编码整数。如果顶部比特位为`0x0000`则代表指针，如果是其他比特位则都为`float`/`double`。

```
Pointer `{`  0000:PPPP:PPPP:PPPP
         / 0001:****:****:****
Double  `{`         ...
          FFFE:****:****:****
Integer `{`  FFFF:0000:IIII:IIII
```

此外其中还包含我们经常在JavaScript中看到的一些常量，这些常量可以编码成`JSValue`。比如`False`为`0x06`，`Null`为`0x02`。

```
False:     0x06
True:      0x07
Undefined: 0x0a
Null:      0x02
```

但我们还是在内存中观察一下。



## 0x02 使用调试器

首先我们可以创建包含各种不同类型的一个奇怪数组，然后在内存中观察该数组。很快我们就会发现奇怪的地方，第一个元素应该是一个整数，然而当在内存中观察时，我们发现其实它是一个`float`。为什么会出现这种情况？

```
[0x1337,13.37,false,undefined,ture,null,`{``}`,0x41424344]
```

[![](https://p0.ssl.qhimg.com/t01f692c46480641ab2.gif)](https://p0.ssl.qhimg.com/t01f692c46480641ab2.gif)

让我们慢慢分析，逐个元素来构造数组。通过这种方法，我们可以观察到整个数组的内部类型在不断变化，并且第一个元素有时候也会被转换成`float`。

[![](https://p4.ssl.qhimg.com/t019ed8535b747c043c.gif)](https://p4.ssl.qhimg.com/t019ed8535b747c043c.gif)

这表明JavaScriptCore在后台会有各种操作，我们来仔细分析一下。



## 0x03 在内存中识别JSValue

将内存中数组的值与关于JSValue的信息进行对比，我们可以很容易识别出各种常量，如`undefined`或者`false`。

[![](https://p0.ssl.qhimg.com/t019615ab203caaaa82.png)](https://p0.ssl.qhimg.com/t019615ab203caaaa82.png)

上图中JSValue常量分别为`false`、`undefined`、`true`以及`null`。

我们创建的空JavaScript对象显示为一个指针，因此这是一个地址，实际的对象存储在其他地方。

[![](https://p1.ssl.qhimg.com/t013aca8e96d438be9d.png)](https://p1.ssl.qhimg.com/t013aca8e96d438be9d.png)

图. JSValue：对象/指针

当然，这里我们还可以通过`0xffff0000`前缀来识别`Integer`。

[![](https://p5.ssl.qhimg.com/t0157980967a8434027.png)](https://p5.ssl.qhimg.com/t0157980967a8434027.png)

图. JSValue：Integer



## 0x04 Butterfly

当观察`describe()`函数的输出时，我们可以看到所谓的“butterfly”（蝶式）地址。根据前面的内存分析结果，我们已经知道其中包含数组元素，但为什么会跟蝴蝶关联在一起呢？

当我们观察该地址所指向的具体位置时，原因就不言而喻。通常情况下地址/指针指向的是某个结构的起始处，但这里指向的是中间位置。指针的右侧为数组元素，指针的左侧为数组长度以及其他对象属性值。

[![](https://p1.ssl.qhimg.com/t0179065d1bd7b3fea0.gif)](https://p1.ssl.qhimg.com/t0179065d1bd7b3fea0.gif)



## 0x05 Structure ID

除了蝶式地址，我们还可以在内存中看到作为对象一部分的其他值。前8个字节包含描述某些内部属性的一些标志以及非常重要的`StructureID`。这个值定义了该偏移地址的具体结构。

[![](https://p0.ssl.qhimg.com/t01320b75db7f303d37.png)](https://p0.ssl.qhimg.com/t01320b75db7f303d37.png)

图. 内存中的`StructureID`

我们可以修改各种内容来分析相关对象，然后观察`StructureID`是否发生改变。比如，当我们往某个对象中添加了一些属性（如`a.x = 1`），可以看到`StructureID`会发生改变。实际上如果对象中没有包含该结构，那么就会创建新的`StructureID`，并且我们可以看到相应的值只是简单地递增。



## 0x06 总结

在这个[视频](https://www.youtube.com/watch?v=KVpHouVMTgY)中，我们可以找到关于内存中分析对象的其他文章，但我个人更建议大家使用调试器，自己操作一下试试。通过这个过程，我们应该能更深入理解基本的JavaScript对象和类型的内部结构，后续我们将以此为基础开展研究。

最后提一下，我们当然可以使用lldb的打印功能来使用调试版本的符号信息。如下图所示，我们可以看到属于`JSCell`头的`StructureID`及标志，并且可以看到蝶式地址是`JSObject`类的一部分。

[![](https://p3.ssl.qhimg.com/t0145abac05db8154fc.png)](https://p3.ssl.qhimg.com/t0145abac05db8154fc.png)



## 0x07 参考资料
- [Attacking JavaScript Engines by saelo](http://phrack.org/papers/attacking_javascript_engines.html)