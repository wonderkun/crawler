> 原文链接: https://www.anquanke.com//post/id/251220 


# Java反序列化和集合之间的渊源


                                阅读量   
                                **26372**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0148d3f9f405b3b108.jpg)](https://p3.ssl.qhimg.com/t0148d3f9f405b3b108.jpg)



## 0x01 前言

从一开始接触Java序列化漏洞就经常看到以Java集合作为反序列化入口，但是也没有仔细思考过原因。分析的Gadget多了觉得很多东西有必要总结一下，所以有了本篇文章。

分析过ysoserial的同学应该经常会遇到将HashMap、HashSet、PriorityQueue等Java集合作为反序列化入口的情况，总结了下大致如下：

|反序列化载体|Gadget
|------
|HashMap|Clojure、Hibernate1、Hibernate2、JSON1、Myfaces1、Myfaces2、ROME、URLDNS
|HashSet|AspectJWeaver、CommonsCollections6
|PriorityQueue|BeanShell1、Click1、CommonsCollections2、CommonsCollections4、Jython1
|LinkedHashSet|Jdk7u21
|Hashtable|CommonsCollections7



## 0x02 Gadget总结

### <a class="reference-link" name="1%E3%80%81HashMap"></a>1、HashMap

先来看下各个Gadget中涉及HashMap的部分：

Clojure

```
HashMap.readObject() -&gt; HashMap.hash() -&gt; AbstractTableModel$ff19274a.hashCode() -&gt; ...
```

Hibernate1和Hibernate2

```
HashMap.readObject() -&gt; HashMap.hash() -&gt; org.hibernate.engine.spi.TypedValue.hashCode() -&gt; ...
```

JSON1

```
HashMap.readObject() -&gt; HashMap.putVal() -&gt; javax.management.openmbean.TabularDataSupport.equals() -&gt; ...
```

Myfaces1和Myfaces2

```
HashMap.readObject() -&gt; HashMap.hash() -&gt; org.apache.myfaces.view.facelets.el.ValueExpressionMethodExpression.hashCode() -&gt; ...
```

ROME

```
HashMap.readObject() -&gt; HashMap.hash() -&gt; com.sun.syndication.feed.impl.ObjectBean.hashCode() -&gt; com.sun.syndication.feed.impl.EqualsBean.beanHashCode() -&gt; ...
```

URLDNS

```
HashMap.readObject() -&gt; HashMap.hash() -&gt; java.net.URL.hashCode() -&gt; ...
```

无外乎两种：

```
HashMap.readObject() -&gt; HashMap.hash() -&gt; XXX.hashCode()
HashMap.readObject() -&gt; HashMap.putVal() -&gt; XXX.equals()
```

那我们看看这几个方法，HashMap.readObject()中恢复HashMap时调用HashMap.putVal()插入键值对，并且调用HashMap.hash()将返回值作为参数。

```
private void readObject(java.io.ObjectInputStream s) throws IOException, ClassNotFoundException `{`
    s.defaultReadObject();
    reinitialize();
    ......
    Node&lt;K,V&gt;[] tab = (Node&lt;K,V&gt;[])new Node[cap];
    table = tab;
        for (int i = 0; i &lt; mappings; i++) `{`
                K key = (K) s.readObject();
                V value = (V) s.readObject();
            // 调用HashMap.putVal()
            putVal(hash(key), key, value, false, false);
        `}`
    `}`
`}`
```

HashMap.hash()用于计算key的hash值，会先**获取key.hashCode的值**，再对 hashcode 进行无符号右移操作，再和 hashCode 进行异或 ^ 操作。

```
static final int hash(Object key) `{`
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h &gt;&gt;&gt; 16);
`}`
```

在HashMap.putVal()中多次调用key.equals(k)进行比较，保证HashMap的键唯一的特点。

```
final V putVal(int hash, K key, V value, boolean onlyIfAbsent, boolean evict) `{`
    Node&lt;K,V&gt;[] tab; Node&lt;K,V&gt; p; int n, i;
    ......
    else `{`
        Node&lt;K,V&gt; e; K k;
        if (p.hash == hash &amp;&amp; ((k = p.key) == key || (key != null &amp;&amp; key.equals(k))))
            e = p;
        else if (p instanceof TreeNode)
            e = ((TreeNode&lt;K,V&gt;)p).putTreeVal(this, tab, hash, key, value);
        else `{`
            for (int binCount = 0; ; ++binCount) `{`
                ......
                if (e.hash == hash &amp;&amp; ((k = e.key) == key || (key != null &amp;&amp; key.equals(k))))
                    break;
                p = e;
            `}`
        `}`
        ......
    `}`
    ++modCount;
    if (++size &gt; threshold)
        resize();
    afterNodeInsertion(evict);
    return null;
`}`
```

### <a class="reference-link" name="2%E3%80%81HashSet"></a>2、HashSet

ysoserial中以HashSet为入口的是AspectJWeaver 和CommonsCollections6，这两个都是通过HashSet.readObject()调用TiedMapEntry.hashCode()：

```
HashSet.readObject() -&gt; HashMap.put() -&gt; HashMap.hash() -&gt; org.apache.commons.collections.keyvalue.TiedMapEntry.hashCode() -&gt; ...
```

HashSet底层是HashMap，readObject()反序列化恢复HashSet实例时需要创建HashMap，将其元素恢复并调用HashMap.put()插入元素，因为HashSet是Object的集合，而HashMap是键值对的集合，put插入时统一以e作为key，`PRESENT`作为value。HashMap.put是用HashMap.putVal()实现的，所以后续的调用和HashMap的一样。

```
// HashSet.readObject()
private void readObject(java.io.ObjectInputStream s) throws java.io.IOException, ClassNotFoundException `{`
    // Read in any hidden serialization magic
    s.defaultReadObject();
    ......
    // Create backing HashMap
    map = (((HashSet&lt;?&gt;)this) instanceof LinkedHashSet ?
           new LinkedHashMap&lt;E,Object&gt;(capacity, loadFactor) :
           new HashMap&lt;E,Object&gt;(capacity, loadFactor));
    // Read in all elements in the proper order.
    for (int i=0; i&lt;size; i++) `{`
        @SuppressWarnings("unchecked")
            E e = (E) s.readObject();
        map.put(e, PRESENT);
    `}`
`}`

//HashMap.put()
public V put(K key, V value) `{`
    return putVal(hash(key), key, value, false, true);
`}`
```

### <a class="reference-link" name="3%E3%80%81LinkedHashSet"></a>3、LinkedHashSet

ysoserial中仅Jdk7u21用到了LinkedHashSet：

```
LinkedHashSet.readObject() -&gt; (HashSet)LinkedHashSet.add() -&gt; HashMap.put() -&gt; HashMap.hash() -&gt; TemplatesImpl.hashCode() -&gt; ...
```

LinkedHashSet继承了HashSet，底层也是HashMap，内部没有直接定义readObject方法，但是可以调用HashSet.readObject()，跟HashSet的调用一样。

### <a class="reference-link" name="4%E3%80%81PriorityQueue"></a>4、PriorityQueue

[之前的文章](https://www.anquanke.com/post/id/250800)里分析过了，详细不再赘述。

```
PriorityQueue.readObject() -&gt; java.util.PriorityQueue.heapify() -&gt; java.util.PriorityQueue.siftDown() -&gt; PriorityQueue.siftDownUsingComparator() -&gt; XXXComparator.compare()
```

### <a class="reference-link" name="5%E3%80%81Hashtable"></a>5、Hashtable

ysoserial中CommonsCollections7用到了Hashtable，Hashtable和HashMap类似，不过Hashtable是支持同步的。

```
Hashtable.readObject() -&gt; Hashtable.reconstitutionPut()-&gt; org.apache.commons.collections.map.AbstractMapDecorator.equals() -&gt; ...
```

Hashtable反序列化时创建Entry数组，将key和value通过Hashtable.reconstitutionPut()插入数组。

```
private void readObject(java.io.ObjectInputStream s)
     throws IOException, ClassNotFoundException
`{`
    // Read in the threshold and loadFactor
    s.defaultReadObject();
    ......
    table = new Entry&lt;?,?&gt;[length];
    threshold = (int)Math.min(length * loadFactor, MAX_ARRAY_SIZE + 1);
    count = 0;
    // Read the number of elements and then all the key/value objects
    for (; elements &gt; 0; elements--) `{`
            K key = (K)s.readObject();
            V value = (V)s.readObject();
        // sync is eliminated for performance
        reconstitutionPut(table, key, value);
    `}`
`}`
```

Hashtable.reconstitutionPut()为了计算hash和保证键唯一，也调用了hashCode和equals()，CommonsCollections7中用到的是equals()动态加载。

```
private void reconstitutionPut(Entry&lt;?,?&gt;[] tab, K key, V value) throws StreamCorruptedException
`{`
    if (value == null) `{`
        throw new java.io.StreamCorruptedException();
    `}`
    // Makes sure the key is not already in the hashtable.
    // This should not happen in deserialized version.
    int hash = key.hashCode();
    int index = (hash &amp; 0x7FFFFFFF) % tab.length;
    for (Entry&lt;?,?&gt; e = tab[index] ; e != null ; e = e.next) `{`
        if ((e.hash == hash) &amp;&amp; e.key.equals(key)) `{`
            throw new java.io.StreamCorruptedException();
        `}`
    `}`
    // Creates the new entry.
    @SuppressWarnings("unchecked")
        Entry&lt;K,V&gt; e = (Entry&lt;K,V&gt;)tab[index];
    tab[index] = new Entry&lt;&gt;(hash, key, value, e);
    count++;
`}`
```



## 0x03 Java集合为什么备受青睐?

**Java所有类都继承于Object**。既然都继承于Object，那么所有的类都是有共性的，只要是java对象都可以调用或者重写父类Object的方法。<br>
集合可以理解为一个容器，**可以储存任意类型的对象**。在集合中经常会有比较或者计算Hash的操作，会频繁使用equals()和hashCode()方法，而**equals()和hashCode()都是Object中定义的方法**，在不同的类中也可能进行了重写。为了实现Gadget的动态加载，自然会用到这些方法进行连接。<br>
这就能解释为什么Java集合会备受Gadget青睐。

此时我们可以拓展下，在PriorityQueue中比较时用的是Comparator或Comparable，Comparator是Java中一个重要的接口，被应用于比较或者排序，Comparator也在很多类中实现了。

除了equals()和hashCode()，上文没有提到的toString也是Object中定义的方法，在Gadget中也常被用到，道理都一样。

```
public boolean equals(Object obj) `{`
    return (this == obj);
`}`

public native int hashCode(); 

public String toString() `{`
    return getClass().getName() + "@" + Integer.toHexString(hashCode());
`}`
```

在挖掘漏洞时可以作为反序列化入口可以总结如下：

```
HashMap.readObject() -&gt; ... -&gt; XXX.hashCode() -&gt; ...
HashMap.readObject() -&gt; ... -&gt; XXX.equals() -&gt; ...
... -&gt; XXX.toString() -&gt; ...
PriorityQueue.readObject() -&gt; ... -&gt; Comparator.compare() -&gt; ...
```



## 0x04 参考链接

[https://github.com/frohoff/ysoserial](https://github.com/frohoff/ysoserial)
