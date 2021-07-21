> 原文链接: https://www.anquanke.com//post/id/219731 


# Fastjson &lt; 1.2.68版本反序列化漏洞分析篇


                                阅读量   
                                **164349**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01f4745e0a7bdb320d.jpg)](https://p0.ssl.qhimg.com/t01f4745e0a7bdb320d.jpg)



作者：ale_wong@云影实验室

## 前言

迟到的Fastjson反序列化漏洞分析，按照国际惯例这次依旧没有放poc。道理还是那个道理，但利用方式多种多样。除了之前放出来用于文件读写的利用方式以外其实还可以用于SSRF。



## 一、漏洞概述

在之前其他大佬文章中，我们可以看到的利用方式为通过清空指定文件向指定文件写入指定内容(用到第三方库)。当gadget是继承的第一个类的子类的时候，满足攻击fastjson的条件。此时寻找到的需要gadget满足能利用期望类绕过checkAutoType。

本文分析了一种利用反序列化指向fastjson自带类进行攻击利用，可实现文件读取、SSRF攻击等。



## 二、调试分析

### <a class="reference-link" name="1.%20%E6%BC%8F%E6%B4%9E%E8%B0%83%E8%AF%95"></a>1. 漏洞调试

从更新的补丁中可以看到expectClass类新增了三个方法分别为：

java.lang.Runnable、java.lang.Readable、java.lang.AutoCloseable

首先，parseObject方法对传入的数据进行处理。通过词法解析得到类型名称，如果不是数字则开始checkAutoType检查。

```
if (!allDigits) `{`
                            clazz = config.checkAutoType(typeName, null, lexer.getFeatures());
                        `}`
```

当传入的数据不是数字的时候，默认设置期望类为空，进入checkAutoType进行检查传入的类。

```
final boolean expectClassFlag;
if (expectClass == null) `{`
    expectClassFlag = false;
`}` else `{`
    if (expectClass == Object.class
            || expectClass == Serializable.class
            || expectClass == Cloneable.class
            || expectClass == Closeable.class
            || expectClass == EventListener.class
            || expectClass == Iterable.class
            || expectClass == Collection.class
            ) `{`
        expectClassFlag = false;
    `}` else `{`
        expectClassFlag = true;
    `}`
`}`
```

判断期望类，此时期望类为null。往下走的代码中，autoCloseable 满足不在白名单内,不在黑名单内，autoTypeSupport没有开启，expectClassFlag为false。

其中：

A.计算哈希值进行内部白名单匹配

B.计算哈希值进行内部黑名单匹配

C.非内部白名单且开启autoTypeSupport或者是期望类的，进行hash校验白名单acceptHashCodes、黑名单denyHashCodes。如果在acceptHashCodes内则进行加载( defaultClassLoader),在黑名单内则抛出 autoType is not support。

```
clazz = TypeUtils.getClassFromMapping(typeName);
```

满足条件C后来到clazz的赋值，解析来的代码中对clazz进行了各种判断

```
clazz = TypeUtils.getClassFromMapping(typeName);
```

从明文缓存中取出autoCloseable赋值给 clazz

[![](https://p4.ssl.qhimg.com/t011719f91b02b6b331.png)](https://p4.ssl.qhimg.com/t011719f91b02b6b331.png)

```
clazz = TypeUtils.getClassFromMapping(typeName);

if (clazz == null) `{`
    clazz = deserializers.findClass(typeName);
`}`

if (clazz == null) `{`
    clazz = typeMapping.get(typeName);
`}`

if (internalWhite) `{`
    clazz = TypeUtils.loadClass(typeName, defaultClassLoader, true);
`}`

if (clazz != null) `{`
    if (expectClass != null
            &amp;&amp; clazz != java.util.HashMap.class
            &amp;&amp; !expectClass.isAssignableFrom(clazz)) `{`
        throw new JSONException("type not match. " + typeName + " -&gt; " + expectClass.getName());
    `}`

    return clazz;
```

当clazz不为空时，expectClassFlag为空不满足条件，返回clazz,至此，第一次的checkAutoType检查完毕。

```
ObjectDeserializer deserializer = config.getDeserializer(clazz);
Class deserClass = deserializer.getClass();
if (JavaBeanDeserializer.class.isAssignableFrom(deserClass)
        &amp;&amp; deserClass != JavaBeanDeserializer.class
        &amp;&amp; deserClass != ThrowableDeserializer.class) `{`
    this.setResolveStatus(NONE);
`}` else if (deserializer instanceof MapDeserializer) `{`
    this.setResolveStatus(NONE);
`}`
Object obj = deserializer.deserialze(this, clazz, fieldName);
return obj;
```

将检查完毕的autoCloseable进行反序列化，该类使用的是JavaBeanDeserializer反序列化器，从MapDeserializer中继承

```
public &lt;T&gt; T deserialze(DefaultJSONParser parser, Type type, Object fieldName) `{`
    return deserialze(parser, type, fieldName, 0);
`}`

public &lt;T&gt; T deserialze(DefaultJSONParser parser, Type type, Object fieldName, int features) `{`
    return deserialze(parser, type, fieldName, null, features, null);
`}`//进入后代码如下
```

```
if ((typeKey != null &amp;&amp; typeKey.equals(key))
        || JSON.DEFAULT_TYPE_KEY == key) `{`
    lexer.nextTokenWithColon(JSONToken.LITERAL_STRING);
    if (lexer.token() == JSONToken.LITERAL_STRING) `{`
        String typeName = lexer.stringVal();
        lexer.nextToken(JSONToken.COMMA);

        if (typeName.equals(beanInfo.typeName)|| parser.isEnabled(Feature.IgnoreAutoType)) `{`
        // beanInfo.typeName是autoCloseable ，但IgnoreAutoType没有开启   
          if (lexer.token() == JSONToken.RBRACE) `{`
                lexer.nextToken();
                break;
            `}`
            continue;
        `}`//不满足条件所以这块代码被跳过了
```

JSON.DEFAULT_TYPE_KEY 为[@type](https://github.com/type) ,并给它赋值传入的key [@type](https://github.com/type) ,将第二个类也就是这次 的gadget传入

```
if (deserializer == null) `{`
    Class&lt;?&gt; expectClass = TypeUtils.getClass(type);
    userType = config.checkAutoType(typeName, expectClass, lexer.getFeatures());
    deserializer = parser.getConfig().getDeserializer(userType);
`}`
```

期望类在这里发生了变化，expectClass的值变为java.lang.AutoCloseable，typeName为gadget，

```
boolean jsonType = false;
        InputStream is = null;
        try `{`
            String resource = typeName.replace('.', '/') + ".class";
            if (defaultClassLoader != null) `{`
                is = defaultClassLoader.getResourceAsStream(resource);
            `}` else `{`
                is = ParserConfig.class.getClassLoader().getResourceAsStream(resource);
              //开了一个class文件的输入流
            `}`
            if (is != null) `{`
                ClassReader classReader = new ClassReader(is, true);//new reader工具
                TypeCollector visitor = new TypeCollector("&lt;clinit&gt;", new Class[0]);
                classReader.accept(visitor);
                jsonType = visitor.hasJsonType();
            `}`
        `}` catch (Exception e) `{`
            // skip
        `}` finally `{`
            IOUtils.close(is);//关闭流 JarURLConnection$JarURLInputStream
        `}`
```

来到JSONType注解，取typename gadget转换变为路径，resource通过将 “.” 替换为”/“得到路径 。其实已经开始读取gadget了，它本意应该是加载AutoCloseable。

```
public ClassReader(InputStream is, boolean readAnnotations) throws IOException `{`
    this.readAnnotations = readAnnotations;

    `{`
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[1024];
        for (; ; ) `{`
            int len = is.read(buf);
            if (len == -1) `{`
                break;
            `}`

            if (len &gt; 0) `{`
                out.write(buf, 0, len);
            `}`
        `}`
        is.close();
        this.b = out.toByteArray();
    `}`
```

可以看到这里有读取文件的功能。所以之前网传的POC可能是利用这里这个特性(?)留意一下以后研究…

```
if (autoTypeSupport || jsonType || expectClassFlag) `{`
    boolean cacheClass = autoTypeSupport || jsonType;
    clazz = TypeUtils.loadClass(typeName, defaultClassLoader, cacheClass);
  //开始加载gadget
`}`
```

```
if (expectClass != null) `{`
    if (expectClass.isAssignableFrom(clazz)) `{`//判断里面的类是否为继承类
        TypeUtils.addMapping(typeName, clazz);
        return clazz;
    `}` else `{`
        throw new JSONException("type not match. " + typeName + " -&gt; " + expectClass.getName());
    `}`
`}`
```

isAssignableFrom()这个方法用于判断里面的类是否为继承类，当利用了java.lang.AutoCloseable这个方法去攻击fastjson，那么后续反序列化的链路需要是继承于该类的子类。

TypeUtils.addMapping(typeName, clazz)这一步成功把gadget加入缓存中并返回被赋值gadget的clazz.

[![](https://p2.ssl.qhimg.com/t019aff13ede1e72ffd.png)](https://p2.ssl.qhimg.com/t019aff13ede1e72ffd.png)

checkAutoType正式检查完毕，此时用deserializer = parser.getConfig().getDeserializer(userType); userType既gadget进行反序列化。

```
private void xxTryOnly(boolean isXXXXeconnect, Properties mergedProps) throws 
  XXXException `{`
    Exception connectionNotEstablishedBecause = null;

    try `{`

        coreConnect(mergedProps);
        this.connectionId = this.io.getThreadId();
        this.isClosed = false;
```

进入coreConnect()

[![](https://p1.ssl.qhimg.com/t010896053bc80a2e61.png)](https://p1.ssl.qhimg.com/t010896053bc80a2e61.png)

[![](https://p0.ssl.qhimg.com/t01f74980019c0b255c.png)](https://p0.ssl.qhimg.com/t01f74980019c0b255c.png)

在这里进行连接。至此漏洞利用完结。



### <a class="reference-link" name="2.%20%E6%80%BB%E7%BB%93%EF%BC%9A"></a>2. 总结：

在本次反序列化漏洞中，笔者认为关键点在于找到合适并且可利用的常用jar包中的gadget。gadget在被反序列化后即可执行类里的恶意的功能(不仅限于RCE还包括任意文件读取/创建,SSRF等)。也可以使本漏洞得到最大化的利用。



## 三、参考考链接

[https://b1ue.cn/archives/348.html](https://b1ue.cn/archives/348.html)

[https://daybr4ak.github.io/2020/07/20/fastjson%201.6.68%20autotype%20bypass/](https://daybr4ak.github.io/2020/07/20/fastjson%201.6.68%20autotype%20bypass/)
