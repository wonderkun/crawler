> 原文链接: https://www.anquanke.com//post/id/190472 


# Java反序列化利用链分析之CommonsCollections2,4,8


                                阅读量   
                                **1036614**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t014e810d5cd76cb132.jpg)](https://p4.ssl.qhimg.com/t014e810d5cd76cb132.jpg)



## 0x00 前言

前面几篇文章，分析了CommonsCollections:3.2.1版本以下存在的反序列化链。今天将继续分析CommonsCollections:4.0版本，主要讲述CommonsCollections2，4，8的利用链构造。



## 0x01 前景回顾

commons-collections:4.0版本其实并没有像3.2.2版本的修复方式一样做拉黑处理，所以在3.2.1及以下的利用链改改还是可以用的。<br>
例如CommonsCollections5

```
final Map&lt;String, String&gt; innerMap = new HashMap();
final Map lazyMap = LazyMap.lazyMap(innerMap, transformerChain);
```

将innerMap改成键值对的申明方式即可，但是大家是不是还记得，除了用LazyMap的方式，CommonsCollections3曾提到过使用`TrAXFilter`类初始化的方式来载入任意的class bytes数组。

这里commons-collections:4.0版本下的利用链，用的都是TemplatesImpl作为最终的命令执行的代码调用，由于前面分析过这个利用方式，后文不再复述。



## 0x02 利用链分析

### <a class="reference-link" name="1.%20CommonsCollections2,4"></a>1. CommonsCollections2,4

CommonsCollections2,4都用到了一个新的类`PriorityQueue`的`Comparator`来触发`transform`函数，两者的区别在于中间的桥接用的不同的Transformer对象。先来看一下`PriorityQueue.readObject`

[![](https://p3.ssl.qhimg.com/t014fedd6edd0aadbdb.png)](https://p3.ssl.qhimg.com/t014fedd6edd0aadbdb.png)

框框里的主要工作为反序列化恢复该对象的数据，我们重点关注`heapify()`

[![](https://p4.ssl.qhimg.com/t01a656698ab5932df2.png)](https://p4.ssl.qhimg.com/t01a656698ab5932df2.png)

继续跟进`siftDown`

[![](https://p0.ssl.qhimg.com/t017aa78f3f99bddf0a.png)](https://p0.ssl.qhimg.com/t017aa78f3f99bddf0a.png)

当我们在实例化对象时提供了`comparator`，将会来到我们最终触发compare的位置，看一下`siftDownUsingComparator`

[![](https://p0.ssl.qhimg.com/t019945708dd2ecd620.png)](https://p0.ssl.qhimg.com/t019945708dd2ecd620.png)

这里调用了我们传入的comparator，并调用其compare，利用链中使用了`TransformingComparator`,来看一下它的compare函数

[![](https://p0.ssl.qhimg.com/t01d46c8875a48f9cc5.png)](https://p0.ssl.qhimg.com/t01d46c8875a48f9cc5.png)

调用了当前的transformer的transform函数，看到这里，其实已经很熟了，前面分析的很多利用链都跟transform有关，并且4.0版本并没有拉黑相关的transformer。所以接下来，我们就可以用前面的一些思路了。

1.CommonsCollections2<br>
CommonsCollections2利用了InvokerTransformer类的任意类函数调用的transform，传入构造好的templates gadget并调用 `TemplatesImpl.newTransformer`

2.CommonsCollections4<br>
CommonsCollections4后续用的方法同CommonsCollections3一样，用`InstantiateTransformer`来触发`TrAXFilter`的初始化，最终也将调用`TemplatesImpl.newTransformer`

整理一下利用链

```
CommonsCollection2:
PriorityQueue.readObject
    -&gt; PriorityQueue.heapify()
    -&gt; PriorityQueue.siftDown()
    -&gt; PriorityQueue.siftDownUsingComparator()
    -&gt; TransformingComparator.compare()
    -&gt; InvokerTransformer.transform()
    -&gt; TemplatesImpl.newTransformer()
    ... templates Gadgets ...
    -&gt; Runtime.getRuntime().exec()

CommonsCollection4:
PriorityQueue.readObject
    -&gt; PriorityQueue.heapify()
    -&gt; PriorityQueue.siftDown()
    -&gt; PriorityQueue.siftDownUsingComparator()
    -&gt; TransformingComparator.compare()
    -&gt; ChainedTransformer.transform()
    -&gt; InstantiateTransformer.transform()
    -&gt; TemplatesImpl.newTransformer()
    ... templates Gadgets ...
    -&gt; Runtime.getRuntime().exec()
```

### <a class="reference-link" name="2.CommonsCollections8"></a>2.CommonsCollections8

CommonsCollections8是今年**[navalorenzo](https://github.com/navalorenzo)**推送到ysoserial上的，8与2，4的区别在于使用了新的readObject触发点`TreeBag`

来看一下`TreeBag.readObject`

[![](https://p2.ssl.qhimg.com/t011eafec398f6fa00f.png)](https://p2.ssl.qhimg.com/t011eafec398f6fa00f.png)

这里的两个关键点`TreeBag`的父类的`doReadObject`函数和`TreeMap`.

看一下`doReadObject`

[![](https://p0.ssl.qhimg.com/t012ce06471167f2a10.png)](https://p0.ssl.qhimg.com/t012ce06471167f2a10.png)

这里对传入的TreeMap调用了`put`函数

[![](https://p0.ssl.qhimg.com/t016a9c43f5a3f04782.png)](https://p0.ssl.qhimg.com/t016a9c43f5a3f04782.png)

继续跟进`compare`函数

[![](https://p4.ssl.qhimg.com/t014e90d7f35bd46d9f.png)](https://p4.ssl.qhimg.com/t014e90d7f35bd46d9f.png)

这里又回到了熟悉的`comparator.compare`函数，其中`comparator`就是我们构造的`TransformingComparator`

后续跟CommonsCollections2相同，就不复述了。

整理一下利用链

```
TreeBag.readObject()
    -&gt; AbstractMapBag.doReadObject()
    -&gt; TreeMap.put()
    -&gt; TransformingComparator.compare()
    -&gt; InvokerTransformer.transform()
    -&gt; TemplatesImpl.newTransformer()
    ... templates Gadgets ...
    -&gt; Runtime.getRuntime().exec()
```

### <a class="reference-link" name="3.%20commons-collections:4.1%E5%8F%8A%E4%BB%A5%E4%B8%8A%E7%9A%84%E6%94%B9%E5%8F%98"></a>3. commons-collections:4.1及以上的改变

前面提到的CommonsCollections2,4,8，都是在commons-collections:4.0版本下才可以使用的。这里我们来看看为什么在4.1及以上版本无法利用！

前面我们用到了InvokerTransformer和InstantiateTransformer作为中转，很真实，4.1版本这两个类都没有实现Serializable接口，导致我们在序列化时就无法利用这两个类。emmmmm，直接干掉了上面的2，4，8。

[![](https://p5.ssl.qhimg.com/t014225082fd54a801d.png)](https://p5.ssl.qhimg.com/t014225082fd54a801d.png)

[![](https://p2.ssl.qhimg.com/t016a2d21114b5b7b9b.png)](https://p2.ssl.qhimg.com/t016a2d21114b5b7b9b.png)

这个改变意味着我们需要从其他可操作危险方法的对象了。



## 0x03 总结

分析完ysoserial里的commons-collections系列的payloads，我们可以简单总结一下Java的反序列化挖掘思路（不涉及技术点，个人的一些想法，如果有错误的地方，希望师傅们指正）。

### <a class="reference-link" name="1.%20%E6%9C%80%E7%BB%88%E7%9A%84%E5%88%A9%E7%94%A8%E6%95%88%E6%9E%9C"></a>1. 最终的利用效果

在利用链构造中，我们肯定希望最终可以达到任意命令执行或者是任意代码执行的效果，这样会使得反序列化漏洞的威力最大化。所以我们很开心能看到InvokerTransformer的transform函数，他利用反射机制来调用任意的代码，也意味着我们能控制任意类的调用执行。但是在实际的挖掘中，除了对反射机制的挖掘和defineClass类型的挖掘，我们也应该注意到其他可能会存在的危险利用，如任意文件写入，任意文件删除等等。

### <a class="reference-link" name="2.%20%E5%88%A9%E7%94%A8%E9%93%BE%E6%80%BB%E4%BD%93%E7%9A%84%E4%B8%80%E4%B8%AA%E6%8C%96%E6%8E%98%E6%80%9D%E8%B7%AF"></a>2. 利用链总体的一个挖掘思路

我们在分析完所有的CommonsCollections的payloads很容易发现的一点是很多payloads“杂交”组合了多个可利用的节点。那么我们在实际的挖掘中，我们需要首先能获知哪些库文件里有哪些可利用的节点，然后根据一定的规则来进行一个链条的连接。

那么来看一下，可利用的节点是什么？

1.实现了`Serializable`接口，枚举出所有可以被序列化的类。<br>
2.该类的类属性做了函数调用或函数的返回值，如`TreeMap.map.put()`和`ConstantTransformer.transform`直接返回`iConstant`类属性。如果不存在上述的情况，我们可以忽略。<br>
3.实现了`readObject`函数，这种情况可作为起始点，也可以作为桥接点，需要具体判断其代码的实现。<br>
4.实现了`invoke`函数，这种情况可作为桥接点，利用了代理机制。<br>
5.从`readObject`函数和`invoke`函数，衍生出来的类属性函数调用，这边可能会引向其他的类函数，如`TreeBag.readObject`的实现，将引向下一步的父类函数`doReadObject`函数。这里就需要做一个人工或者是静态的代码分析。

接下来，关于可利用节点的串联，其实主要依赖于第5点的挖掘，我们需要根据经验或者是静态的代码分析来做。

根据上面的一个分析，其实我们可以做到一个自动化的利用链发掘，[https://github.com/JackOfMostTrades/gadgetinspector这个工具就是一个很好的实现，后续将对其进行一个分析。](https://github.com/JackOfMostTrades/gadgetinspector%E8%BF%99%E4%B8%AA%E5%B7%A5%E5%85%B7%E5%B0%B1%E6%98%AF%E4%B8%80%E4%B8%AA%E5%BE%88%E5%A5%BD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%8C%E5%90%8E%E7%BB%AD%E5%B0%86%E5%AF%B9%E5%85%B6%E8%BF%9B%E8%A1%8C%E4%B8%80%E4%B8%AA%E5%88%86%E6%9E%90%E3%80%82)

从commons-collections的防护来看，我们越来越无法在单个库里面实现一个可利用的利用链，这也意味着我们需要对不同的项目做针对性的分析，所以gadetinspector这个工具的重要性就不言而喻了。下一步将重点分析一下该工具的实现。

[![](https://p0.ssl.qhimg.com/t014651eec75e98d5a4.jpg)](https://p0.ssl.qhimg.com/t014651eec75e98d5a4.jpg)
