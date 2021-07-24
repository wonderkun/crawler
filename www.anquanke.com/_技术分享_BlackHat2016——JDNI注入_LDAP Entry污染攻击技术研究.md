> 原文链接: https://www.anquanke.com//post/id/84506 


# 【技术分享】BlackHat2016——JDNI注入/LDAP Entry污染攻击技术研究


                                阅读量   
                                **79684**
                            
                        |
                        
                                                                                    



**[![](https://p0.ssl.qhimg.com/t01a4c2280fa424ab56.png)](https://p0.ssl.qhimg.com/t01a4c2280fa424ab56.png)**

**(一)基本概念**

****

**1.1 JNDI**

JNDI（Java Naming and DirectoryInterface），直译为命名与目录接口。JNDI是一组客户端通过名称（Naming）来寻找和发现数据和对象的API。

JNDI的概念分为命名系统和目录系统：

（1）    命名系统（Naming Service）：将实体使用名称和值的方式联系起来，俗称绑定。

l  DNS：将机器的网络地址和域名进行映射；

l  文件系统：将文件名和存储在磁盘的数据进行映射。

（2）    目录系统（Directory Service）：是一种特殊的命名系统，目录系统中支持“目录对象”的存储和查询。LDAP就是一种目录系统，允许以树状的形式存储目录对象，并且可以对这些对象进行索引。

明确一下对象的概念，对象可以在本地，也可以部署在远程服务器。学习过RMI原理的同学应该对远程对象并不陌生，其实RMI就是JNDI的一种，类似的还有CORBA,LDAP以及众所周知的DNS服务。

<br>

**1.2 JNDI的代码片段**

[![](https://p1.ssl.qhimg.com/t0132bd65b81e47008d.png)](https://p1.ssl.qhimg.com/t0132bd65b81e47008d.png)

上图的代码片段是使用JNDI接口来创建RMI服务，这和sun.rmi.*包提供的创建方式有所不同，关键在于map对象env和上下文对象ctx，通过这两个对象来标识一些信息。这里有几个方法要说明一下：

（1）    bind方法：将服务名称和实体进行绑定，比如这里调用bind方法来使用foo字符串指定一个字符串”Sample String”。当然这个代码直接运行会出错，原因在于bind方法接收的对象必须是远程对象。源码如下：

[![](https://p5.ssl.qhimg.com/t0118731d483b542e72.png)](https://p5.ssl.qhimg.com/t0118731d483b542e72.png)

（2）lookup方法：从系统中寻找命名标识的对象。这里使用foo字符串来在命名与目录系统中寻找对应的对象（字符串对象）。

最后print出的是“Sample String”

<br>

**1.3 引用与地址**

在JNDI系统中，需要存储一些对象，存储对象的方式通常会采用存储该对象的引用的方式。对于学习过OOP概念的同学，对象的引用并不难理解。所谓引用（Reference）就是指在内存中定位对象的一个指针。通过对象的引用，我们可以在JNDI系统中操作对象或者获取对象的一些信息。

[![](https://p0.ssl.qhimg.com/t0128d3b99498863521.png)](https://p0.ssl.qhimg.com/t0128d3b99498863521.png)

比较有趣的是，使用Reference对象可以指定工厂来创建一个java对象，用户可以指定远程的对象工厂地址，当远程对象地址用户可控时，这也会带来不小的问题。

<br>

**1.4 远程代码与安全管理器**

**1.4.1 Java中的安全管理器**

Java中的对象分为本地对象和远程对象，本地对象是默认为可信任的，但是远程对象是不受信任的。比如，当我们的系统从远程服务器加载一个对象，为了安全起见，JVM就要限制该对象的能力，比如禁止该对象访问我们本地的文件系统等，这些在现有的JVM中是依赖安全管理器（SecurityManager）来实现的。

[![](https://p5.ssl.qhimg.com/t01cb04f89d62590267.png)](https://p5.ssl.qhimg.com/t01cb04f89d62590267.png)

JVM中采用的最新模型见上图，引入了“域”的概念，在不同的域中执行不同的权限。JVM会把所有代码加载到不同的系统域和应用域，系统域专门负责与关键资源进行交互，而应用域则通过系统域的部分代理来对各种需要的资源进行访问，存在于不同域的class文件就具有了当前域的全部权限。

关于安全管理机制，可以详细阅读：

[http://www.ibm.com/developerworks/cn/java/j-lo-javasecurity/](http://www.ibm.com/developerworks/cn/java/j-lo-javasecurity/)

**<br>**

**1.4.2 JNDI安全管理器架构**

[![](https://p5.ssl.qhimg.com/t01a0efca303bfc256e.png)](https://p5.ssl.qhimg.com/t01a0efca303bfc256e.png)

对于加载远程对象，JDNI有两种不同的安全控制方式，对于Naming Manager来说，相对的安全管理器的规则比较宽泛，但是对JNDI SPI层会按照下面表格中的规则进行控制：

[![](https://p5.ssl.qhimg.com/t019e7beb28d2b536e6.png)](https://p5.ssl.qhimg.com/t019e7beb28d2b536e6.png)

针对以上特性，黑客可能会找到一些特殊场景，利用两者的差异来执行恶意代码。

<br>

**（二）click-to-play绕过**

****

**2.1 点击运行保护**

有了以上的基础知识作为铺垫，我们来了解下“Click-to-play”的绕过（CVE-2015-4902），该0day是从趋势科技捕获的一个蠕虫病毒Pawn Storm中发现的。详细请参考趋势科技的具体blog：

[http://blog.trendmicro.com/trendlabs-security-intelligence/new-headaches-how-the-pawn-storm-zero-day-evaded-javas-click-to-play-protection/](http://blog.trendmicro.com/trendlabs-security-intelligence/new-headaches-how-the-pawn-storm-zero-day-evaded-javas-click-to-play-protection/)

要想真正理解这个CVE的原理，还需要一些基础知识的讲解。

**<br>**

**2.2 JNLP协议**

JNLP全称为Java Network Launch Protocol，这项技术被用来通过URL打开一个远程的Java可执行文件。通过这个技术，可以快速部署applet或者web应用。而在攻击场景下，攻击者用于部署applet应用。

**<br>**

**2.3 jndi.properties文件**

jndi.properties文件用来创建Context上下文对象。如果正常使用代码的方式，我们可以创建一个Properties对象来设置一些JNDI服务需要的一些配置，然后通过这个对象创建出相关的上下文对象：

Properties p = new Properties(); 

p.put(Cotnext.PROVIDER_URL, "localhost:1099 "）；//主机名和端口号 

//InitialContext的创建工厂类

p.put(Context.InitialContextFactroy, "com.sun.InitialContextFactory"); 

InitialContext ctx = new InitialContext(p); 

如果使用jndi.properties文件来创建上下文对象，我们可以将这些配置写入到properties文件中，从而使代码的可配置性更高：

java.naming.factory.initial=com.sun.NamingContextFactory 

java.naming.provider.url=localhost:1099 

如果直接创建初始上下文,如下： 

InitialContext   ctx   =   new  InitialContext(); 

InitialContext的构造器会在类路径中找jndi.properties文件，如果找到，通过里面的属性，创建初始上下文。 

两种方式是相同的效果。

**<br>**

**2.4 攻击思路**

**[![](https://p1.ssl.qhimg.com/t01fb18c035dbad780f.png)](https://p1.ssl.qhimg.com/t01fb18c035dbad780f.png)**

攻击发生前，攻击者做了这样三件事情：

（1）    配置一个恶意的web页面，该页面包含一个applet应用，具体代码如下：

[![](https://p1.ssl.qhimg.com/t011aaadd4379eb3a6c.png)](https://p1.ssl.qhimg.com/t011aaadd4379eb3a6c.png)

（1）    攻击者创建一个RMI服务（公网IP）

（2）    攻击者创建一个托管java恶意代码的服务器（公网IP）

接下来就是攻击发生的具体步骤了：

Ø  在受害者机器上，访问含有applet应用的html页面之后，浏览器进程会启动jp2launcher.exe，然后从恶意服务器请求init.jnlp文件。

Ø  恶意服务器上返回一个jnpl文件，文件内容如下：

[![](https://p3.ssl.qhimg.com/t01b5bb3d12690681c9.png)](https://p3.ssl.qhimg.com/t01b5bb3d12690681c9.png)

这里jnpl文件中，progress-class指定为javax.naming.InitialContext。通过官网文档，我们获知这个属性指定的类名需要实现DownloadServiceListener接口才行，但是jre似乎没有校验这个情况。

Ø  受害者主机会执行这个类的构造方法，InitialContext构造方法会从恶意服务器上请求jndi.properties文件，用于创建context对象，该文件如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011fa1e14e4a85b8b9.png)

可以看到指定了Context的工厂类为RMI服务的，并且指定rmi的URL。

Ø  然后受害者主机与RMI服务器建立了通讯，随后客户端发起查找Go对象

（其实就是个恶意的工厂类）的请求，相应地，RMI服务器返回一个恶意的Go.class。

Ø  这个恶意文件在受害者主机被执行，从而实现静默执行效果。

从上面的过程来看，攻击者用到了JNDI实现了静默执行applet的方法，从而执行了恶意代码，绕过click-to-play，过程非常巧妙和精彩。

**<br>**

**（三）JNDI注入漏洞**

**<br>**

**3.1 攻击条件**

漏洞利用的条件：

（1）    上下文对象必须通过InitialContext或者它的子类（InitialDirContextor InitialLdapContext）来实例化。

（2）    InitialContext的一些属性可以通过传入lookup方法的参数进行修改。

关于条件中的第二条，来解读一下，首先看下面的代码片段：

[![](https://p0.ssl.qhimg.com/t0116abed11d71372fa.png)](https://p0.ssl.qhimg.com/t0116abed11d71372fa.png)

如果攻击者对传入lookup的参数是可控的，那么无论context中配置过什么URL，比如这里指定了RMI的URL为rmi://sercure-server:1099，但是攻击者如果在lookup中指定一个绝对路径，如rmi://evil-server:1099/foo，那么会以lookup参数指定的URL为准。

**<br>**

**3.2 RMI攻击向量**

**<br>**

**3.2.1 RMI介绍**

**[![](https://p5.ssl.qhimg.com/t01ddf5db53946b98ef.png)](https://p5.ssl.qhimg.com/t01ddf5db53946b98ef.png)**

RMI全称为远程方法调用，上图描述了RMI的架构，可以看到，客户端和服务器的通讯运用了代理对象，分别是Stub和Skeleton对象，这两个代理对象负责实现客户端和服务器之间的通讯，提供远程对象的副本，返回远程对象调用的结果等功能，从而实现远程对象的调用。

**<br>**

**3.2.2 JNDI Ref payload**

Reference是JNDI中的对象引用，因为在JNDI中，对象传递要么是序列化方式存储（对象的拷贝，对应按值传递），要么是按照引用（对象的引用，对应按引用传递）来存储，当序列化不好用的时候，我们可以使用Reference将对象存储在JNDI系统中。

JNDI提供了一个Reference类来表示某个对象的引用，这个类中包含被引用对象的类信息和地址。地址属性是用RefAddr类表示。用Reference也可以创建对象：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fec74d6c22bbba60.png)

上面的代码片段是官方文档中的demo，通过Reference构造函数，传入要实例化类的全名、地址信息、工厂类的全名、工厂类的地址等信息，就能实例化一个类，值得注意的是，这里支持传入工厂类的URL地址，也就是支持远程工厂类的引入。

如果在RMI服务器端使用Reference创建远程对象后，绑定到rmi中：

[![](https://p0.ssl.qhimg.com/t01c028470da1533cda.png)](https://p0.ssl.qhimg.com/t01c028470da1533cda.png)

注意，这里的FactoryURL需要攻击者可控，因此攻击者可以自己写一个恶意的工厂类，然后在服务端执行恶意代码。

看两个Demo来说明一下：

**场景1：攻击者可控FactoryUrl**

首先是提供正常RMI服务的服务器，代码看上去是这样的：

[![](https://p2.ssl.qhimg.com/t016d38fde7e8ec15b6.png)](https://p2.ssl.qhimg.com/t016d38fde7e8ec15b6.png)

如果上面圈出来的地方是攻击者可控的话，那么攻击者通过这个URL可以构造一个工厂类来影响服务器端的逻辑。

这个工程类如果包含了恶意的代码，比如可以把工厂类构造成这样：

[![](https://p2.ssl.qhimg.com/t01423ebc901debff78.png)](https://p2.ssl.qhimg.com/t01423ebc901debff78.png)

这里demo中，恶意代码放在了getObjectInstance里，因为在执行lookup时，JNDI会调用工厂对象中的getObjectInstance方法：

[![](https://p5.ssl.qhimg.com/t01d917face305da756.png)](https://p5.ssl.qhimg.com/t01d917face305da756.png)

其实直接把恶意代码放在工厂类的构造函数中也行，因为lookup执行时会对其进行实例化，相关代码可以从RMI实现中找到。

当然我们还需要自己做一个RMI服务器，当然是恶意的服务器，代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c9f4b6e22e504cb1.png)

在恶意服务器上，我们将恶意的工厂类绑定在RMI服务上。

这样，服务器上bind的对象，实际上是我们工厂方法所提供的。一旦有客户端连接这个受到污染的RMI服务器，并且调用了lookup方法来寻找受污染的远程对象，恶意代码就会被执行。

写个客户端代码模拟一下：

[![](https://p5.ssl.qhimg.com/t010125f4f2f1417180.png)](https://p5.ssl.qhimg.com/t010125f4f2f1417180.png)

**<br>**

**3.2.3 直接注入lookup**

直接看代码：

[![](https://p1.ssl.qhimg.com/t0140e59ca4c94e0ef7.png)](https://p1.ssl.qhimg.com/t0140e59ca4c94e0ef7.png)

清晰明了，没啥可说的。而且原理实际上和ref注入差不多，为了好懂，还是举个栗子。

**场景2：利用恶意工厂类exploit**

上个场景有点蜜汁难懂，其实是我自己YY的，我们来看下议题的作者给出的姿势。

首先，我们在可控的服务器上搭建一个RMI服务，这个服务上绑定一个恶意的工厂类：

[![](https://p5.ssl.qhimg.com/t0179bfb12c1ce0cde7.png)](https://p5.ssl.qhimg.com/t0179bfb12c1ce0cde7.png)

恶意服务器开放了12345端口，并绑定了一个恶意的工厂类，这次我们将恶意代码放入到这个工厂类的构造函数中，比如：

[![](https://p3.ssl.qhimg.com/t016e247017465c1a2a.png)](https://p3.ssl.qhimg.com/t016e247017465c1a2a.png)

然后，如果某个应用的lookup方法的参数是我们可控的，就可以填入我们的恶意服务URL，类似下面这种。

[![](https://p1.ssl.qhimg.com/t019bde52000e8471c6.png)](https://p1.ssl.qhimg.com/t019bde52000e8471c6.png)

原理很简单，工厂类最终会在客户端进行实例化，实例化时就会调用构造函数中的代码，从而达到任意代码执行的效果，注意，实例化工厂类的是NamingManager，根据JNDI的架构，这个类是不受Java安全管理器约束的。

<br>

**3.2.4 恶意远程对象**

通过远程对象来进行JNDI注入，难度比较大，要求有权限修改codebase以及java.rmi.server.useCodebaseOnly必须为False（JDK 7u21后默认为true）。

由于运用难度大并且有很大的局限性，所以这里就不进行介绍了。

**<br>**

**3.2.5 攻击过程**

**[![](https://p2.ssl.qhimg.com/t013dc79f4f212e4e31.png)](https://p2.ssl.qhimg.com/t013dc79f4f212e4e31.png)**

配合Ref Payload的Demo，我们不难理解通过RMI进行JNDI注入的攻击流程：

（1）    首先攻击者将RMI绝对路径注入到lookup方法中。

（2）    受害者RMI服务器会请求攻击者事先搭建好的恶意RMI服务器

（3）    恶意服务器返回Payload（恶意远程对象）

（4）    恶意代码在受害者服务器执行。

值得注意的是，像InitialContext.rename()和InitialContext.lookupLink()方法也会受到影响，因为它们最终还是调用了lookup方法。

<br>

**3.2.6 Toplink/EclipseLink**

JPA（持久化技术）是ORM的统一标准，Toplink是JPA的一种实现，常用的hibernate也是。EclipseLink是以Toplink为基础的开源项目。来看看JNDI的真实场景：

[![](https://p5.ssl.qhimg.com/t01a2bdd0a3d3f797aa.png)](https://p5.ssl.qhimg.com/t01a2bdd0a3d3f797aa.png)

在基础操作中处理POST请求的过程中，调用了callSessionBeanInternal，跟进这个方法：

[![](https://p4.ssl.qhimg.com/t01ccfecdd902c37e15.png)](https://p4.ssl.qhimg.com/t01ccfecdd902c37e15.png)

Lookup传入的参数是可控的，通过http请求可以做到，标准的JNDI注入。攻击者可以利用JNDI注入漏洞来实现任意代码执行。

<br>

**3.2.7 与反序列化配合**

本质上原理相同，readObject方法中有可控的lookup参数。

[![](https://p3.ssl.qhimg.com/t011671fe5bd34cab82.png)](https://p3.ssl.qhimg.com/t011671fe5bd34cab82.png)

比如Spring框架爆出的这个反序列化漏洞，执行过程如下：

org.springframework.transaction.jta.JtaTransactionManager.readObject()方法中调用了IntinailContext.lookup方法，调用过程如下：

l  initUserTransactionAndTransactionManager()

l  initUserTransactionAndTransactionManager()

l  JndiTemplate.lookup()

l  InitialContext.lookup()

InitialContext.lookup()这个方法中的传入参数”userTransactionName”是用户可控的，所以造成了JNDI注入。BlackHat上的议题中还提到了其他的例子，这里就不一一介绍了。

**<br>**

**3.3 CORBA攻击向量**

CORBA的JNDI注入原理和RMI的差不多，但是有SecurityManager的限制，然而，议题的演讲者找到了一个绕过SecurityManager的方法，但是由于正在被修复中，所以在议题中并没有透漏这个方法。感兴趣的同学可以关注一下，在几个绕过中，已经有一个获得了CVE编号（CVE-2016-5018）。

**<br>**

**3.4 LDAP攻击向量**

**<br>**

**3.4.1 LDAP基础**

LDAP是轻量级目录访问协议，通过LDAP，用户可以连接，查询，更新远程服务器上的目录。

对象在LDAP上有两种存储方式：

（1）    利用Java序列化方式

（2）    利用JDNI的References对象引用

这两种方式都有可能造成命令执行。

<br>

**3.4.2 攻击流程**

**[![](https://p4.ssl.qhimg.com/t0102799da955a58cac.png)](https://p4.ssl.qhimg.com/t0102799da955a58cac.png)**

1.      攻击者提供一个LDAP的绝对路径URL注入到JNDI的lookup方法

2.      受害者服务器连接到攻击者的恶意LDAP服务，并返回一个恶意的远程对象引用。

3.      受害者服务器对JNDI远程对象引用Reference进行decode操作。

4.      受害者服务器获取到了恶意的工厂对象。

5.      受害者服务器实例化这个工厂对象。

6.      工厂对象中的恶意代码被触发执行。

LDAP的情境下，对于lookup方法的注入和漏洞触发原理本质上和RMI的一致。

<br>

**3.4.3 LDAP实体投毒**

实际上，lookup方法恶意注入的场景是非常少见的。大部分的操作都是在对象层面的操作，比如增删改查等。

LDAP编程中，通常会使用search方法来查询一个目录对象，单纯的一个查询是无法做到命令执行的，但是议题作者发现，当returnObjFlag设置为true时，攻击者可以控制LDAP的返回并引发任意命令执行的漏洞。

**对象返回查询**

LDAP编程中使用

SearchControls对象作为参数来标识查询范围以及查询返回值的形式。这个对象中有个方法是setReturningObjFlag(boolean)，当设置为true时（默认为false），使用search方法查询后会返回一个对象结构。

[![](https://p4.ssl.qhimg.com/t0175ff2469362cbfd1.png)](https://p4.ssl.qhimg.com/t0175ff2469362cbfd1.png)

当returnObjFlag设置为true时，查看源码，可以看到调用了decodeObject方法转化为对象。

Java对象表现协议

在RFC 2713中，详细的定义了不同的Java对象在LDAP目录系统中的表现和存储形式。

**1.      序列化对象**

序列化对象在LDAP中的表示如下：

l  javaClassName：类的全称

l  javaClassNames：类定义所继承的父类，接口的名称集合

l  javaCodebase：指向class定义的位置

l  javaSerializedData：包含序列化之后的对象数据

**2.      Marshalled Objects**

和序列化对象差不多，但是会记录javaCodebase.

**3.      JNDI References**

引用类型对象包含了javaClassName,javaClassNames, javaCodebase。除此之外，还有：

l  javaReferenceAddress：存储引用地址的列表。

l  javaFactory：存储工厂类的类名全称。

**<br>**

**攻击向量**

**1.      反序列化**

当JNDI中对象的javaSerializedData不为空时，decodeObject方法就会对这个字段的内容进行反序列化（Obj.decodeObject(Attributesattrs)）：

[![](https://p2.ssl.qhimg.com/t01742d50f4ce46d8f3.png)](https://p2.ssl.qhimg.com/t01742d50f4ce46d8f3.png)

这里javaCodebase可以指定远程的URL，黑客只需要在readObject方法中编写恶意代码就能执行，当然需要服务器端配置com.sun.jndi.object.trustURLCodebase=true

来避开JVM的安全管理器。

当LDAP服务器没有这种设置时，攻击者仍然可以使用一些存在于服务器端的有漏洞的类来执行代码。

LDAP投毒的代码如下，这里是指定了javaCodebase进行攻击：

[![](https://p4.ssl.qhimg.com/t01f2125c921a063c76.png)](https://p4.ssl.qhimg.com/t01f2125c921a063c76.png)

**2.      JNDIReference**

LDAP中，也是由Naming Manager来处理引用类型的对象，并做实例化的。Naming Manager会检查javaFactory和javaCodebase是否是存在的，如果存在，则从javaCodebase中获取javaFactory进行实例化。正如前面所说的，对于Naming Manager，JVM的安全管理机制太过于宽松。因此，攻击者就可以通过控制这些属性来执行恶意代码。

下面的代码是Obj.decodeObject(Attributesattrs)中实例化Reference的代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b8f33e5b19f02303.png)

这里的decodeReference方法中对Reference进行了组装：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014b2a4728db19d102.png)

可以看到这个代码和JNDI注入的代码是一致的。

攻击代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01521e659e856f0032.png)

<br>

**3.      RemoteLocation**

javaRemoteLocation属性在RFC中是被废除的，但是JNDI还是能支持这个属性的处理。相关代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01afa7d7cbec21b4d6.png)

可以看到，当指定javaRemoteLocation时，JNDI会根据URL获取到对应的Reference，实例化之后就会触发漏洞代码，和RMI的情景如出一辙。

[![](https://p0.ssl.qhimg.com/t01f249544564545ef2.png)](https://p0.ssl.qhimg.com/t01f249544564545ef2.png)

**<br>**

**3.4.4 攻击场景**

在LDAP中修改对应的Java属性，当LDAP中查询后实例化查询结果时，就会触发漏洞。具体来讲，是LdapSearchEnumeration类对LDAP查询响应进行实例化，本质上还是通过注入外部的工厂类来污染Reference。

对攻击过程进行总结，大致是两个方向：

**1.      针对LDAP条目**

（1）    攻击者污染一个LDAP条目，并且注入恶意的Java协议属性。

（2）    攻击者向LDAPserver发起一个查询（比如LDAP认证的时候）。

（3）    受害应用执行LDAP查询并获取受到污染的实体。

（4）    受害应用将条目转换为java对象。

（5）    受害应用从攻击者控制的服务器上获取恶意的工厂类。

（6）    受害应用在实例化工厂类的时候执行了恶意代码。

**2.      针对LDAP响应**

（1）    攻击者强制受害应用发起一个LDAP查询（比如认证的时候），或者等待该应用发起一次LDAP查询。

（2）    应用发起一次LDAP查询，并获取一个条目

（3）    攻击者拦截并修改LDAP查询的响应，将恶意的Java协议属性注入到响应中。

（4）    受害应用对该响应进行实例化时触发恶意代码

**<br>**

**3.4.5 返回对象的查询方式**

设置returnObjFlag为true的写法还是挺常见的，因为查询过后直接返回对象，操作起来非常方便。

**Spring Security案例**

Spring security是一个Java应用常见的认证和鉴别的框架。

这个库提供了一个查询指定用户名的方法：

FilterBasedLdapUserSearch.searchForUser(String username). 这个方法是Spring Security获取正在认证的用户信息的。这个方法用到了SpringSecurityLdapTemplate类：

[![](https://p4.ssl.qhimg.com/t01ff2d9fd8ee2ee7c2.png)](https://p4.ssl.qhimg.com/t01ff2d9fd8ee2ee7c2.png)

跟进这个方法：

继续跟进，可以看到查询的代码：

[![](https://p1.ssl.qhimg.com/t012a656f31dd5e751e.png)](https://p1.ssl.qhimg.com/t012a656f31dd5e751e.png)

在buildControls中，可以看到设置了RETURN_OBJECT为true：

[![](https://p2.ssl.qhimg.com/t015ea60200a66012c4.png)](https://p2.ssl.qhimg.com/t015ea60200a66012c4.png)

显然，这个漏洞是针对条目的一种形式，由于设置了查询结果返回为java对象，JNDI会自动将查询结果进行某种decode来转为Java对象，实例化过程中触发漏洞。通过修改java协议属性来复现：

1.      首先写一个恶意的工厂类，在构造函数中执行恶意代码。

[![](https://p1.ssl.qhimg.com/t017093c2d1007ef207.png)](https://p1.ssl.qhimg.com/t017093c2d1007ef207.png)

2.    污染条目

[![](https://p1.ssl.qhimg.com/t01992c58c8fac8f396.png)](https://p1.ssl.qhimg.com/t01992c58c8fac8f396.png)

重点是修改了javaFactory和javaCodebase，指向了我们的恶意工厂类。

3.      触发search方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f9944221396ecced.png)

只需要尝试登陆一下即可触发LDAP执行search操作，从而执行我们的恶意代码。

1.      执行恶意代码。

Spring LDAP案例

还是同样的原因，这里只分析下源码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0126db0fcfb2fc4e5e.png)

受影响的是authenticate方法，调用了search方法，跟进之后发现也同样设置了returnObjFlag，利用思路和前面一致。

<br>

**（四）总结**

****

议题中介绍了两种新型的攻击方式——JNDI攻击和LDAP条目污染。两种方式都是非常高危的漏洞，并且可以执行任意的代码。

为了防范这两种类型的漏洞，可以做以下措施：

1.      不要将不可信的数据传入InitialContext.lookup方法中。

如果必须这么做，那么要确保参数不是绝对路径的URL。

2.      使用安全管理器时，需要仔细审计安全策略。

3.      尽可能禁止远程的codebase
