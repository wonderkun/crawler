> 原文链接: https://www.anquanke.com//post/id/235227 


# 从TemplatesImpl类Gadget中提取bytecode


                                阅读量   
                                **189136**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0189d079c55f0f6c12.png)](https://p1.ssl.qhimg.com/t0189d079c55f0f6c12.png)



作者：fnmsd[@360](https://github.com/360)云安全

大半年前开的头，扔那就给忘了，终于想起来给写完了(*/ω＼*)



## 前言

在Java反序列化的gadget中，有很多使用可反序列化TemplatesImpl类进行命令执行（比如CommonsCollections2-4、CommonsBeanutils1、Jdk7u21以及变种JRE8u20等等）。

实际上这类Gadget的反序列化过程中是直接或间接调用newTransformer或getOutputProperties方法，最终进入defineTransletClasses方法，将_bytecodes字段中存储的类的bytecode重新在JVM中定义为类，最终在对其调用newInstance方法时，触发写在该类static块或者无参构造方法中的代码块，从而达到代码执行的效果。

由于ysoserial中默认用于创建TemplatesImpl对象的createTemplatesImpl函数中，是在bytecode对应的类的静态代码块中加入执行java.lang.Runtime.exec的代码段，所以效果上来说，ysoserial创建的这类gadget是用于触发命令执行的，但实际上是可以进行任意代码执行的。

[![](https://p0.ssl.qhimg.com/t01b042858ac9a155ca.png)](https://p0.ssl.qhimg.com/t01b042858ac9a155ca.png)

（修改yso令其支持任意代码执行可以参考这两篇文章:

[https://blog.csdn.net/fnmsd/article/details/79534877](https://blog.csdn.net/fnmsd/article/details/79534877)

[https://gv7.me/articles/2019/enable-ysoserial-to-support-execution-of-custom-code/）](https://gv7.me/articles/2019/enable-ysoserial-to-support-execution-of-custom-code/%EF%BC%89)

所以，当我们抓取到一些TemplatesImpl类的Gadget时，为了了解其具体的目的、执行的代码，我们需要提取出其中的bytecode进行反编译。



## idea调试反序列化过程

以提取Xray Shiro的Shiro扫描中的bytecodes为例（此处膜一下长亭的Koalr师傅）

**准备环境：**

idea

shiro的samples-web.war

xray高级版（高级版才有Shiro Scan功能）

**开始：**

idea中下断点下到TemplatesImpl类的内部类TransletClassLoaderdefineClass中defineClass方法上：

[![](https://p3.ssl.qhimg.com/t01a3f46dbd251436ef.png)](https://p3.ssl.qhimg.com/t01a3f46dbd251436ef.png)

启动调试，并使用xray开始扫描shiro站点：

```
xray webscan --plugins shiro --url http://127.0.0.1:8080/samples_web_war/
```

（注意url一定要加结尾的斜杠，否则会导致响应302扫描失败）

然后idea中会触发断点，这时可以看到进入defineClass方法的bytecode

[![](https://p5.ssl.qhimg.com/t0145898dd42af4f029.png)](https://p5.ssl.qhimg.com/t0145898dd42af4f029.png)

接着使用idea的调试的表达式执行功能将它保存出来，使用如下代码,并点击evaluate：

```
var f = new FileOutputStream("d:/test.class");//这里路径改成需要保存的位置
f.write(b);
f.close();
```

此时就将byteCode的内容保存了下来。

[![](https://p5.ssl.qhimg.com/t0161eac70dc824cb3e.png)](https://p5.ssl.qhimg.com/t0161eac70dc824cb3e.png)

接着上jd-gui或者luyten就可以看到详细的逻辑了：

[![](https://p0.ssl.qhimg.com/t017413358315a2ae72.png)](https://p0.ssl.qhimg.com/t017413358315a2ae72.png)



## 使用Java Agent

使用Agent修改TemplatesImpl$TransletClassLoader类的defineClass方法，将_bytecodes进行保存。

[![](https://p2.ssl.qhimg.com/t011984981485f86917.png)](https://p2.ssl.qhimg.com/t011984981485f86917.png)

基于javassist写了一个简单的premain模式的Agent，修改defineClass方法，增加字节码的输出，此处感谢同部门的jweny师傅给的支持~

```
package org.fnmsd;

import javassist.*;

import java.io.ByteArrayInputStream;
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;

public class DumperAgent `{`
    public static void premain(String args, Instrumentation instrumentation) `{`
        DumperTransformer transformer = new DumperTransformer();
        instrumentation.addTransformer(transformer);
    `}`

    public static class DumperTransformer implements ClassFileTransformer `{`
        public byte[] transform(ClassLoader loader, String className, Class&lt;?&gt; classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException `{`

            if(className.equals("com/sun/org/apache/xalan/internal/xsltc/trax/TemplatesImpl$TransletClassLoader"))`{`
                ClassPool classPool = ClassPool.getDefault();
                classPool.appendClassPath(new LoaderClassPath(loader));
                try `{`
                    CtClass ctClass = classPool.makeClass(new ByteArrayInputStream(classfileBuffer));
                    CtMethod defineClass = ctClass.getDeclaredMethod("defineClass");
                    //利用JavaAssist增加代码
                    defineClass.insertBefore("long l = new java.util.Random().nextLong();System.out.println(\"Output Class:\"+l);new java.io.FileOutputStream(l+\".class\").write($1);");
                    return ctClass.toBytecode();
                `}` catch (Exception e) `{`
                    System.err.println("Agent:Patch Method Error");
                    e.printStackTrace();
                `}`
            `}`
            return classfileBuffer;
        `}`
    `}`
`}`
```

在defineClass方法最前面加入了：

```
long l = new java.util.Random().nextLong();
System.out.println("Output Class:"+l);
new java.io.FileOutputStream(l+".class").write($1);//$1是一个参数，即bytecodes的数组b
```

会将加载的通过defineClass加载字节码，写入到当前工作目录下，具体位置可根据实际需要进行修改。

LoadObject是我自己加的一个用来测试生成好的序列化数据的伪gadget,作用就是用ObjectInputStream加载输出的序列化文件。

当然同样可以挂到Weblogic\Tomcat等中间件上来导出bytecodes。

可以正常弹出计算，此处我就不截计算器图了。

[![](https://p4.ssl.qhimg.com/t0191a9714bfb32551a.png)](https://p4.ssl.qhimg.com/t0191a9714bfb32551a.png)

查看输出的class文件：

[![](https://p5.ssl.qhimg.com/t01e0b1aff8ae433cb5.png)](https://p5.ssl.qhimg.com/t01e0b1aff8ae433cb5.png)

会输出两次是因为原版的ysoserial除了代码执行用的bytecode以外，还带一个迷之Foo.class，有关yso的bytecodes相关问题可以看下这篇文章：[https://xz.aliyun.com/t/6227](https://xz.aliyun.com/t/6227)



## 直接分析Java序列化数据

这个只对未加密的序列化数据进行解析，除了shiro反序列化以外，大部分利用应该都是这种。

具体的序列化数据结构，可以参考Java文档中[对象序列化流协议](https://docs.oracle.com/javase/8/docs/platform/serialization/spec/protocol.html)部分。

这里选择修改NickstaDB大佬（膜）实现的Java序列化数据解析工具SerializationDumper来进行bytecodes的导出。

[https://github.com/fnmsd/SerializationDumper/](https://github.com/fnmsd/SerializationDumper/)

(上段用的Agent也传到了这里)

在SerializationDumper类里面加了几个字段，用来确定是解析到了TemplatesImpl类的bytecodes字段以及存储解析出来的byte。

最后效果：

[![](https://p4.ssl.qhimg.com/t0149afe592e2160e8c.png)](https://p4.ssl.qhimg.com/t0149afe592e2160e8c.png)

[![](https://p4.ssl.qhimg.com/t01f0dac7b95285e68c.png)](https://p4.ssl.qhimg.com/t01f0dac7b95285e68c.png)



## 总结

以上是想到的三种导出bytecodes的方法，我用的最多的是第一种，调试的时候就顺手导出了。

已经有师傅写过第三种方法了，可以参考一下：

[https://github.com/r00tuser111/SerializationDumper-Shiro](https://github.com/r00tuser111/SerializationDumper-Shiro)

[https://mp.weixin.qq.com/s/EBH3pfFKx4vwCy1Z7h_DcQ](https://mp.weixin.qq.com/s/EBH3pfFKx4vwCy1Z7h_DcQ)



## 引用

[https://blog.csdn.net/u011040537/article/details/107176880/](https://blog.csdn.net/u011040537/article/details/107176880/)

[https://docs.oracle.com/javase/8/docs/platform/serialization/spec/protocol.html](https://docs.oracle.com/javase/8/docs/platform/serialization/spec/protocol.html)

[https://github.com/NickstaDB/SerializationDumper](https://github.com/NickstaDB/SerializationDumper)
