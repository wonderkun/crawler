> 原文链接: https://www.anquanke.com//post/id/197086 


# Apereo CAS 反序列化漏洞分析及回显利用


                                阅读量   
                                **1176758**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://www.00theway.org/2020/01/04/apereo-cas-rce/banner.png)](https://www.00theway.org/2020/01/04/apereo-cas-rce/banner.png)



author: [00theway](https://www.00theway.org/)

## 背景介绍

Apereo CAS 是一个开源的企业级单点登录系统，很多统一认证系统都是基于此系统二次开发，官网对于漏洞的一个[通告](https://apereo.github.io/2016/04/08/commonsvulndisc/)，记录一下分析过程。



## 漏洞环境

直接使用docker运行了4.1.6的cas环境,将源代码拷贝出来以供分析。

```
# docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                                              NAMES
91ae98e6388d        apereo/cas:v4.1.6   "/cas-overlay/bin/ru…"   9 days ago          Up 20 seconds       0.0.0.0:32773-&gt;8080/tcp, 0.0.0.0:32772-&gt;8443/tcp
# docker cp 91ae98e6388d:/cas-overlay ~/worksation/cas_4_1_6
```



## 漏洞分析

### <a class="reference-link" name="1.%20CAS%E5%A6%82%E4%BD%95%E5%A4%84%E7%90%86%E8%AF%B7%E6%B1%82"></a>1. CAS如何处理请求

Apereo CAS 使用了spring webflow来处理登录、退出等请求，处理流程可以看一下这篇文章[CAS单点登录开源框架解读（三）—CAS单点登录服务端认证之loginFlowRegistry流程](https://blog.csdn.net/joeljx/article/details/88812944)。

### <a class="reference-link" name="2.%20%E6%BC%8F%E6%B4%9E%E8%A7%A6%E5%8F%91%E6%B5%81%E7%A8%8B"></a>2. 漏洞触发流程

cas中关于登录的配置文件如下

```
# /WEB-INF/cas-servlet.xml
  &lt;bean id="loginHandlerAdapter"
        class="org.jasig.cas.web.flow.SelectiveFlowHandlerAdapter"
        p:supportedFlowId="login"
        p:flowExecutor-ref="loginFlowExecutor"
        p:flowUrlHandler-ref="loginFlowUrlHandler" /&gt;
```

当新的登录请求到达时，Spring会调用 “org.jasig.cas.web.flow.SelectiveFlowHandlerAdapter”类 的handle函数来处理请求，这个类的handle函数实现在他的父类里边，关键代码如下

```
// org.springframework.webflow.mvc.servlet.FlowHandlerAdapter.class

public ModelAndView handle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception `{`
        FlowHandler flowHandler = (FlowHandler)handler;
        this.checkAndPrepare(request, response, false);

        // flowExecutionKey是POST的“execution”的参数值，其中的flowUrlHandler在登录相关的配置文件中有配置“p:flowUrlHandler-ref="loginFlowUrlHandler"”
        String flowExecutionKey = this.flowUrlHandler.getFlowExecutionKey(request);
        if (flowExecutionKey != null) `{`
            try `{`
                ServletExternalContext context = this.createServletExternalContext(request, response);

                //用来恢复execute中存储的当前状态，漏洞从这里开始，其中flowExecutor在登录相关的配置文件中可以找到
                             //p:flowExecutor-ref="loginFlowExecutor"，loginFlowExecutor对应的类为“org.springframework.webflow.executor.FlowExecutorImpl”
                FlowExecutionResult result = this.flowExecutor.resumeExecution(flowExecutionKey, context);
                this.handleFlowExecutionResult(result, context, request, response, flowHandler);
                ...
```

跟进看一下 “this.flowExecutor.resumeExecution(flowExecutionKey, context);”是如何恢复状态的

```
// org.springframework.webflow.executor.FlowExecutorImpl.class

public FlowExecutionResult resumeExecution(String flowExecutionKey, ExternalContext context) throws FlowException `{`
        FlowExecutionResult var6;
        try `{`
            if (logger.isDebugEnabled()) `{`
                logger.debug("Resuming flow execution with key '" + flowExecutionKey);
            `}`

            ExternalContextHolder.setExternalContext(context);

            // 简单解析flowExecutionKey的数据到FlowExecutionKey对象，供后续使用
            FlowExecutionKey key = this.executionRepository.parseFlowExecutionKey(flowExecutionKey);
            FlowExecutionLock lock = this.executionRepository.getLock(key);
            lock.lock();

            try `{`
            //通过FlowExecutionKey恢复状态，其中处理不当导致了反序列化漏洞
                FlowExecution flowExecution = this.executionRepository.getFlowExecution(key);
                flowExecution.resume(context);
    ...
```

继续跟进“this.executionRepository.getFlowExecution(key);”的处理流程

```
// org.jasig.spring.webflow.plugin.ClientFlowExecutionRepository.class

public FlowExecution getFlowExecution(FlowExecutionKey key) throws FlowExecutionRepositoryException `{`
        if (!(key instanceof ClientFlowExecutionKey)) `{`
            throw new IllegalArgumentException("Expected instance of ClientFlowExecutionKey but got " + key.getClass().getName());
        `}` else `{`
        // 从上一步解析出的key对象中获取序列化相关的数据
            byte[] encoded = ((ClientFlowExecutionKey)key).getData();

            try `{`
            //在this.transcoder.decode(encoded)代码解密中同时进行了反序列化恢复状态
                ClientFlowExecutionRepository.SerializedFlowExecutionState state = (ClientFlowExecutionRepository.SerializedFlowExecutionState)this.transcoder.decode(encoded);
                ...
```

简单看一下解密相关的代码，漏洞触发点

```
//org.jasig.spring.webflow.plugin.EncryptedTranscoder.class

public Object decode(byte[] encoded) throws IOException `{`
        byte[] data;
        try `{`
            data = this.cipherBean.decrypt(encoded);
        `}` catch (Exception var11) `{`
            throw new IOException("Decryption error", var11);
        `}`

        ByteArrayInputStream inBuffer = new ByteArrayInputStream(data);
        ObjectInputStream in = null;

        Object var5;
        try `{`
            if (this.compression) `{`
                in = new ObjectInputStream(new GZIPInputStream(inBuffer));
            `}` else `{`
                in = new ObjectInputStream(inBuffer);
            `}`
            // 触发反序列化漏洞
            var5 = in.readObject();
        ...
```

可以看到作者有意识的对序列化数据进行了加密，并使用配置的cipherBean进行解密

看一下cipherBean的相关配置

```
&lt;bean id="loginFlowStateTranscoder" class="org.jasig.spring.webflow.plugin.EncryptedTranscoder"
          c:cipherBean-ref="loginFlowCipherBean" /&gt;

    &lt;bean id="loginFlowCipherBean" class="org.cryptacular.bean.BufferedBlockCipherBean"
          p:keyAlias="$`{`cas.webflow.keyalias:aes128`}`"
          p:keyStore-ref="loginFlowCipherKeystore"
          p:keyPassword="$`{`cas.webflow.keypassword:changeit`}`"&gt;
        &lt;property name="nonce"&gt;
            &lt;bean class="org.cryptacular.generator.sp80038a.RBGNonce" /&gt;
        &lt;/property&gt;
        &lt;property name="blockCipherSpec"&gt;
            &lt;bean class="org.cryptacular.spec.BufferedBlockCipherSpec"
                  c:algName="$`{`cas.webflow.cipher.alg:AES`}`"
                  c:cipherMode="$`{`cas.webflow.cipher.mode:CBC`}`"
                  c:cipherPadding="$`{`cas.webflow.cipher.padding:PKCS7`}`" /&gt;
        &lt;/property&gt;
    &lt;/bean&gt;

    &lt;bean id="loginFlowCipherKeystore" class="java.security.KeyStore"
          factory-bean="loginFlowCipherKeystoreFactory" factory-method="newInstance" /&gt;

    &lt;bean id="loginFlowCipherKeystoreFactory" class="org.cryptacular.bean.KeyStoreFactoryBean"
          c:type="$`{`cas.webflow.keystore.type:JCEKS`}`"
          c:password="$`{`cas.webflow.keystore.password:changeit`}`"&gt;
        &lt;constructor-arg name="resource"&gt;
            &lt;bean class="org.cryptacular.io.URLResource"
                  c:url="$`{`cas.webflow.keystore:classpath:/etc/keystore.jceks`}`" /&gt;
        &lt;/constructor-arg&gt;
    &lt;/bean&gt;
```

加解密相关的配置会先去配置文件中获取，没有配置密钥信息的会使用jar包默认的密钥信息（默认keystore文件位于spring-webflow-client-repo-1.0.0.jar包当中）。

由于cas默认配置文件中没有对密钥进行配置，导致我们可以用spring-webflow-client-repo这个jar包中默认的密钥加密序列化数据进行攻击。

分析漏洞之余去看了一下导致漏洞的spring-webflow-client-repo这个jar包的github主页[spring-webflow-client-repo](https://github.com/serac/spring-webflow-client-repo)

在主页中作者对这个jar包存在的安全风险做了相关提示

[![](https://www.00theway.org/2020/01/04/apereo-cas-rce/security.png)](https://www.00theway.org/2020/01/04/apereo-cas-rce/security.png)

如果开发者在使用一个新的第三方包之前去了解一下作者的介绍完全可以避免这个漏洞的存在。



## 漏洞回显利用

对于反序列化漏洞单纯利用是比较简单的，这里不做过多介绍。这里重点介绍一下在web环境中有可以回显的exploit。

关于web回显方法
1. [报错回显](https://xz.aliyun.com/t/2272)
1. 获取response对象
1. 目前在研究一种新的通杀回显方法
> PS回显了解一下[![](https://www.00theway.org/2020/01/04/apereo-cas-rce/shiro-exp.png)](https://www.00theway.org/2020/01/04/apereo-cas-rce/shiro-exp.png)

之前在调试”Nexus Repository Manager 3”的表达式执行漏洞时候发现”Thread.currentThread()”的“threadLocals”变量中会保存当前线程相关的一些资源，其中就可能存在response对象。

[![](https://www.00theway.org/2020/01/04/apereo-cas-rce/threadLocals.png)](https://www.00theway.org/2020/01/04/apereo-cas-rce/threadLocals.png)

这种方法会相对麻烦，因为需要去遍历列表判断是否为目标对象。

此次回显使用常见的通过静态方法获取response对象，对整个项目进行搜索发现了一个静态方法满足我们的需求

```
org.springframework.webflow.context.ExternalContextHolder.getExternalContext()
```

通过这个方法可以获取到当前进行关联的上下文信息，然后通过“getNativeRequest()”方法获取request对象通过getNativeResponse()方法获取response对象。

> 可以通过 “org.springframework.cglib.core.ReflectUtils.defineClass().newInstance();”这个public方法来加载我们的payload。



## Enter-hacking

> 自己动手，丰衣足食。<br>[![](https://www.00theway.org/2020/01/04/apereo-cas-rce/exploit.png)](https://www.00theway.org/2020/01/04/apereo-cas-rce/exploit.png)

欢迎北京、武汉红队来撩 [liheng@qianxin.com](mailto:liheng@qianxin.com)
