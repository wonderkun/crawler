
# Java JMX-RMI


                                阅读量   
                                **377390**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/202686/t0125f83f55202607b1.jpg)](./img/202686/t0125f83f55202607b1.jpg)



## 0x00 前言

RMI的一个重要应用是JMX(Java Management Extentions)，本文介绍JMX的几个攻击面：）



## 0x01 基础

在写一半的时候，发现了这篇文章，感觉写的很好，可以看看：[https://mogwailabs.de/blog/2019/04/attacking-rmi-based-jmx-services/](https://mogwailabs.de/blog/2019/04/attacking-rmi-based-jmx-services/)

JMX

> Java Management Extensions (JMX) is a Java technology that supplies tools for managing and monitoring applications, system objects, devices (such as printers) and service-oriented networks.

MBean

> JMX allows you to manage resources as managed beans. A managed bean (MBean) is a Java Bean class that follows certain design rules of the JMX standard. An MBean can represent a device, an application, or any resource that needs to be managed over JMX. You can access these MBeans via JMX, query attributes and invoke Bean methods.
The JMX standard differs between various MBean types however, we will only deal with the standard MBeans here. To be a valid MBean, a Java class must:
<ul>
- Implement an interface
- Provide a default constructor (without any arguments)
- Follow certain naming conventions, for example implement getter/setter methods to read/write attributes
</ul>

这里提一下，当MBean的名字为`Hello`时，其相应的interface名必须为`HelloMBean`，不然算不合法的MBean

MBean Server

> A MBean server is a service that manages the MBeans of a system. Developers can register their MBeans in the server following a specific naming pattern. The MBean server will forward incoming messages to the registered MBeans. The service is also responsible to forward messages from MBeans to external components.

DEMO用参考里的，用`jconsole`看看结果

[![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01303da1ffd4c0b63e.png)

在JConsole里可以对当前注册的MBean进行操作，如上图调用`sayHello`函数

当前我们连的是本地的MBean Server(每个java进程在本地都会有一个MBean Server)，我们也可以将MBean Server挂载到某一端口上，提供远程的MBean管理。

运行jar时带上`-Dcom.sun.management.jmxremote.port=2222 -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false`

直接通过JConsole来连接，会提示你有两种方法1:`host:port`;2:`service:jmx:&lt;protocol&gt;:&lt;sap&gt;`

这里我们重点要讲的就是第二种方法，首先我们先来看一下jmx建立起2222端口后，用nmap来获取其内容是怎么样的

[![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a8e0f16a224ec31b.png)

从结果来看，JMX的MBean Server是建立在RMI的基础上的，并且其RMI Registy注册的名字叫`jmxrmi`。

第二种方法中，我们可以通过指定具体的协议来跟Server端进行连接，参考[JMX RMI connector API](https://docs.oracle.com/javase/8/docs/api/index.html?javax/management/remote/rmi/package-summary.html)

> There are two forms for RMI connector addresses:
<ul>
- In the **JNDI form**, the URL indicates **where to find an RMI stub for the connector**. This RMI stub is a Java object of type [`RMIServer`](https://docs.oracle.com/javase/8/docs/api/javax/management/remote/rmi/RMIServer.html) that gives remote access to the connector server. With this address form, the RMI stub is obtained from an external directory entry included in the URL. An external directory is any directory recognized by [`JNDI`](https://docs.oracle.com/javase/8/docs/api/javax/naming/package-summary.html), typically the RMI registry, LDAP, or COS Naming.
- In the **encoded form**, the URL directly includes the information needed to connect to the connector server. When using RMI/JRMP, the encoded form is the serialized RMI stub for the server object, encoded using BASE64 without embedded newlines. When using RMI/IIOP, the encoded form is the CORBA IOR for the server object.
</ul>

这里的encoded form的反序列化过程实在发起端进行的，所以这里不考虑第二种形式。

对于JNDI的形式，有以下几种方法跟JMX Server去连接：

Connector支持JRMP和iiop作为连接层的协议，所以对应的有两种方式

```
1. service:jmx:rmi://host:port/
2. service:jmx:iiop://host:port/
```

此外，还有基于目录条目的connectors

```
1. service:jmx:rmi://host:port/jndi/jndi-name
2. service:jmx:iiop://host:port/jndi/jndi-name
比如
serivce:jmx:rmi://&lt;可忽略的host&gt;/jndi/rmi://host:port/jmxrmi
```

这种方式就可以使用jndi下的所有spi来进行连接



## 0x02 攻击JMX

### <a class="reference-link" name="1.%20%E6%94%BB%E5%87%BBJMX-RMI"></a>1. 攻击JMX-RMI

**CVE-2016-3427** 由于JMX认证时传递的是HashMap数据结构，而以HashMap可以直接构造一个反序列化利用链来攻击本地ClassPath，这里已经修复了不细讲了XD

**主动攻击1**：利用RMI Registy收到远程bind时产生的反序列化漏洞 jdk&lt;8u141_b10(并且check host的顺序变了，详细可以看[这里](http://blog.0kami.cn/2020/02/06/rmi-registry-security-problem/))，[8u141_b10修改后](http://hg.openjdk.java.net/jdk8u/jdk8u/jdk/rev/c92d704420d7#l2.32)SingleEntryRegistry增加了filter

[![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01149637a0bba3f7c1.png)

限制了接受到的不能是序列化后的对象，也就意味着不能利用registry这种方式来达成利用了。

**主动攻击2**:利用RMI DGC实现存在反序列化漏洞，可在JEP 290之前的版本攻击成功(使用ysoserial的JRMPClient，分析也见[这里](http://blog.0kami.cn/2020/02/06/rmi-registry-security-problem/)0x08部分)

前面两种方式，在最新版的JDK8中均早已失效。除了直接攻击RMI层，我们也还可以利用MBean Server挂载的对象函数，来传递构造好的序列化数据。这里有点像RMI中利用RMI Server挂载的对象函数参数中存在相关可利用的对象，如Object类型就可以装载所有的序列化数据。

### <a class="reference-link" name="2.%20%E6%94%BB%E5%87%BB%E5%AD%98%E5%9C%A8%E5%87%BD%E6%95%B0%E5%8F%82%E6%95%B0%E7%9A%84%E5%AF%B9%E8%B1%A1"></a>2. 攻击存在函数参数的对象

利用MBean Server挂载的对象函数参数，来传递构造好的序列化数据。MBean Server接收到数据后，会对获取到的参数数据进行`object[]`转换，在转换前，需要将RMI交互过程中的序列化数据进行反序列化

`javax/management/remote/rmi/RMIConnectionImpl.java#unwrap`

[![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0188d65326eddd7f5b.png)

1583行进行类型转化，但首先需要先进行反序列化`mo.get()`

`java/rmi/MarshalledObject.java#get`

[![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01be5bb719b3057445.png)

这里就到了常规的反序列化操作

所以只要MBean Server里存在MBean的函数存在参数，我们通过构造相关的invoke传递过去就可以触发反序列化

[![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0109504afb31714dbf.png)

如`java.util.logging.Logging#getLoggerLevel(String)`有一个String类型的函数参数，这里我们直接将payload塞进invoke的第二个参数即可。

其他的MBean也同样可以这样操作，这里如果需要认证的话，就需要在连接时将认证信息带上，后续的还是可以利用成功的。

### <a class="reference-link" name="3.%20%E5%88%A9%E7%94%A8MLET%E6%96%B9%E5%BC%8F%E5%8A%A8%E6%80%81%E5%8A%A0%E8%BD%BDMBean"></a>3. 利用MLET方式动态加载MBean

这里先说利用方式：

**利用条件**：
1. 无security manager
1. 无认证
**利用原理**：
1. 在一HTTP Server挂载mlet文件和包含MBean的jar文件
1. 用`createMBean("javax.management.loading.MLet", null);`的方式在远程JMX创建MLet对象
1. 使用`getMBeansFromURL`从远程HTTP Server加载mlet文件
1. 解析mlet文件，由于存在codebase，从远程加载jar文件，并载入该MBean
1. 调用该MBean的方法，这个方法可以是自定义的执行命令等操作
**简单分析**：

来简单说一下MLet的原理，JMX除了加载本地的MBean，也可以加载远程的MLet文件(包含了MLet标签)来动态加载codebase里的Jar文件。后者就是通过MLet对象的getMBeansFromURL函数来完成的。

有兴趣的可以翻一翻`javax/management/loading/MLet.java#getMBeansFromURL`，这里直接说一下流程
1. 从远程服务器加载MLet文件并解析该文件
1. 根据MLet文件中指定的codebase和archive字段，拼接成最后要请求的jar文件URL地址
1. 最后由URLClassLoader来完成请求载入操作
这里需要注意的是，第2步中，如果当前的URL地址已经存在将不再重新发起载入请求，意味着一次载入成功之后，我们就可以直接调用该MBean（Server不重启的状态下）。

而对于前面提到的两个利用条件：

在文档里[https://docs.oracle.com/javase/7/docs/technotes/guides/management/agent.html提到](https://docs.oracle.com/javase/7/docs/technotes/guides/management/agent.html%E6%8F%90%E5%88%B0)

> **Caution –** This configuration is insecure: any remote user who knows (or guesses) your port number and host name will be able to monitor and control your Java applications and platform. Furthermore, possible harm is not limited to the operations you define in your MBeans. A remote client could create a `javax.management.loading.MLet` MBean and use it to create new MBeans from arbitrary URLs, at least if there is **no security manager**. In other words, a rogue remote client could make your Java application execute arbitrary code.
Consequently, while disabling security might be acceptable for development, it is strongly recommended that you **do not disable security for production systems**.

首先对于有认证的情况下，调用MLet将会进行权当前用户的权限验证，默认情况下都是不允许的。

`com/sun/jmx/remote/security/MBeanServerFileAccessController.java#checkAccess`会检查当前登陆的用户是否有Create的权限(这里的权限是下面的createPatterns，它允许创建指定正则的类型，而我们默认是为空的)，这里默认会返回false，也就意味着它不允许以MLet对象创建新的MBean

[![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0184a50fab5191e1ae.png)

其次对于security manager的限制，在远程载入前会判断是否存在载入的权限（这里我没看到其他的地方做了判断，可能不止当前这个位置的验证）

[![](./img/202686/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018a5286ac6c5a5db3.png)

当前方法比较方便的是可以载入任意的代码来执行，但是利用条件比较苛刻。



## 0x03 总结

对于JMX的利用主要利用的是本地存在的Gadget，如果本地不存在Gadget的话就无法利用成功。除非满足JMX MLet的利用条件，通过加载codebase上的Jar文件来执行任意代码。

除此之外，由于本身JMX用的RMI那一套东西，所以如果在合适的JDK版本下，我们可以直接攻击RMI，不过前提仍然是本地存在相关的利用链。

最后，前文提到的攻击方法我已经同步到[github](https://github.com/wh1t3p1g/ysomap)上了
