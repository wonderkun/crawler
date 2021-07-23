> 原文链接: https://www.anquanke.com//post/id/85441 


# 【技术分享】使用Netzob逆向未知协议


                                阅读量   
                                **154735**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：amossys.fr
                                <br>原文地址：[http://blog.amossys.fr/How_to_reverse_unknown_protocols_using_Netzob.html](http://blog.amossys.fr/How_to_reverse_unknown_protocols_using_Netzob.html)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p4.ssl.qhimg.com/t01875941bd7cead853.jpg)](https://p4.ssl.qhimg.com/t01875941bd7cead853.jpg)

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**0x00 前言**

本文主要介绍如何使用Netzob来逆向未知协议。通过简单学习协议的消息格式及其状态机，并且给出一些关于实际通信中如何产生流量的观点。最后，我们说明如何针对服务器的实现使用基本的模糊测试。

<br>

**0x01 Netzob简介**

Netzob是一个用于逆向工程、生成流量和模糊测试通信协议的开源工具。它允许通过被动和主动的过程来推断协议的消息格式和状态机。该模型可以用于模拟现实和可控流量以及模糊测试目标实现。

通过这个教程，我们将介绍Netzob的主要功能，推断消息格式和简单协议的语法，并且在最后介绍些基本实现的模糊测试。被介绍的功能覆盖以下能力：

**导入一个我们想逆向的包含痕迹的文件**

**推断消息格式**

    区分特定分隔符的消息

    重组特定关键字字段消息

    区分序列对齐的每个消息的子集

    查找每组消息的关联性

    修改消息格式，应用发现的关系

**推断语法**

    根据捕获的消息序列，生成一个主状态机

    根据捕获的消息序列，生成一个序列的状态机

    根据捕获的消息序列，生成一个Prefix Tree Acceptor (PTA)

**生成流量和fuzz服务器**

    生成遵循推断的每组消息格式的消息

    通过不同的消息格式fuzzing服务器

<br>

**0x02 安装Netzob和下载教程**

首先，得到Netzob的源代码，安装依赖库和编译底层库。如果需要，有关安装过程的更多详细信息，请参见README文件。

[![](https://p5.ssl.qhimg.com/t010038534e03d9164c.png)](https://p5.ssl.qhimg.com/t010038534e03d9164c.png)

然后，你能获得教程中使用的协议实现的源代码，和一些消息序列的PCAP文件：

[测试协议实现](https://dev.netzob.org/attachments/download/179/tutorial_netzob_v1.tar.gz)

[序列1的PCAP文件](https://dev.netzob.org/attachments/download/182/target_src_v1_session1.pcap)

[序列2的PCAP文件](https://dev.netzob.org/attachments/download/181/target_src_v1_session2.pcap)

[序列3的PCAP文件](https://dev.netzob.org/attachments/download/180/target_src_v1_session3.pcap)

下节通过几步来逆向这个测试协议。在深入Netzob功能前，你能先看一下它的文档，尤其是API的描述。

<br>

**0x03 消息格式接口**

**从一个PCAP文件中导入消息**

大部分逆向协议的第一步是收集重要的通信实例。在这个教程中，例子来自PCAP文件。可以通过PCAPImporter.readfile()函数从PCAP文件中读取数据包。这个函数有可选参数来指定[BPF](https://en.wikipedia.org/wiki/Berkeley_Packet_Filter)过滤，导入层或者捕获到的数据包如下：

[![](https://p2.ssl.qhimg.com/t012767fb6f793d1027.png)](https://p2.ssl.qhimg.com/t012767fb6f793d1027.png)

这个函数能用来从模拟我们测试协议实现的PCAP文件中导出消息。例如，下面的代码创建了一个基于从PCAP导出的消息的symbol。这个symbol代表了共享相同语法和语义的所有消息。换句话说，symbol是一组相似消息的抽象，这组消息从协议的角度看有相同的影响。首先，从PCAP文件导入的消息以symbol的形式分组了。对于这个symbol我们使用不同的方法来确定协议的消息格式。

[![](https://p1.ssl.qhimg.com/t017e5beccec24c7613.png)](https://p1.ssl.qhimg.com/t017e5beccec24c7613.png)

[![](https://p5.ssl.qhimg.com/t010d3382e68c0c0757.png)](https://p5.ssl.qhimg.com/t010d3382e68c0c0757.png)

**使用分隔符做格式区分**

根据快速浏览消息，字符#出现在每个消息中间。因此，第一步根据字符#分割每条消息。根据文档描述，函数splitDelimiter()有这个功能：

[![](https://p5.ssl.qhimg.com/t0111a9f0640e6b0f84.png)](https://p5.ssl.qhimg.com/t0111a9f0640e6b0f84.png)

让我们使用分隔符#来调用splitDelimiter函数。我们能使用_str_debug()方法结构化输出获得的字段。这个方法显示了symbol结构的ASCII的展示，因此显示了每个字段的定义。

[![](https://p3.ssl.qhimg.com/t017da108512413ed8f.png)](https://p3.ssl.qhimg.com/t017da108512413ed8f.png)

[![](https://p3.ssl.qhimg.com/t014bca26dbdcbbfb4c.png)](https://p3.ssl.qhimg.com/t014bca26dbdcbbfb4c.png)

关于分割的消息，显示如下：

[![](https://p5.ssl.qhimg.com/t01847a4d5cd7a00d0f.png)](https://p5.ssl.qhimg.com/t01847a4d5cd7a00d0f.png)

**根据关键字段分簇**

现在我们有了symbol的不同字段的分解，让我们试下重组一些消息：这是Netzob中分簇方法的目的。

在这个例子中，第一个字段是有用的，因为它包含了几种命令行（CMDencrypt, CMDidentify等）。让我们根据第一个字段分簇（如有相同第一个字段的消息分为一组）。我们使用clusterByKeyField()函数：

[![](https://p0.ssl.qhimg.com/t0181a275c762aa6fe3.png)](https://p0.ssl.qhimg.com/t0181a275c762aa6fe3.png)

这里，使用该函数生成捕捉到的消息的symbol列表：

[![](https://p3.ssl.qhimg.com/t0179a3ad4e9c43f2e4.png)](https://p3.ssl.qhimg.com/t0179a3ad4e9c43f2e4.png)

分簇算法生成了14个不同的symbol，每个symbol都有一个唯一的第一个字段。

[![](https://p3.ssl.qhimg.com/t01897cd2e1095863d3.png)](https://p3.ssl.qhimg.com/t01897cd2e1095863d3.png)

**在每个symbol中以序列对齐来区分格式**

在这步，我们重组了消息，并且有每个消息的3个字段的基本分解：命令字段，分割字段和不定长内容。让我们关注下最后一个字段。具有动态大小的字段是我们在Netzob中序列对齐的良好选择。这个功能让我们对齐静态和动态的子字段。为了做到这个，使用splitAligned()函数：

[![](https://p4.ssl.qhimg.com/t0188cefecfbfe9883e.png)](https://p4.ssl.qhimg.com/t0188cefecfbfe9883e.png)

在接下来的文中，我们想通过序列对齐算法来对齐每个symbol的最后一个字段：

[![](https://p3.ssl.qhimg.com/t01525af8b969cf316c.png)](https://p3.ssl.qhimg.com/t01525af8b969cf316c.png)

对于symbol CMDencrypt，序列对齐后的最后一个字段编程如下格式，我们能看到两个可变字段的包裹一个静态字段x00x00x00。最后一个字段似乎是我们想加密的缓冲区，因为字段关键字的暗示（如CMDencrypt）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b1dd90268e79d90e.png)

**找到每个symbol的关系**

现在让哦我们试着找出这些消息的关系。Netzob的API提供了静态函数RelationFinder.findOnSymbol()，让我们确定潜在的消息字段之间的关系：

[![](https://p4.ssl.qhimg.com/t01bc161fd60e0cea5a.png)](https://p4.ssl.qhimg.com/t01bc161fd60e0cea5a.png)

下文显示了如何在我们未知的协议中找到关系，并且如何处理结果：

[![](https://p5.ssl.qhimg.com/t01b8672a9bff0155e7.png)](https://p5.ssl.qhimg.com/t01b8672a9bff0155e7.png)

导出结果如下，我们已经找到了symbol CMDencrypt在内容字段（第三个字段）和另一个字段程度的的关系（最后一个，假设包含我们想加密的缓冲区的字段）

[![](https://p4.ssl.qhimg.com/t0160e1e205c5205c83.png)](https://p4.ssl.qhimg.com/t0160e1e205c5205c83.png)

**应用找到symbol结构之间的关系**

因此我们刚刚发现了一个与下个字段大小相关的字段。关于这个结果，我们修改消息格式来应用我们找到的关系。我们通过创建一个Size字段来做这个，这个字段的值依赖目标字段的内容。我们也指定一个事实是Size字段的大小应该是缓冲区字段的八分之一（因为每个字段默认按位描述）。

[![](https://p3.ssl.qhimg.com/t01ef7de8861900cbdf.png)](https://p3.ssl.qhimg.com/t01ef7de8861900cbdf.png)

CMDencrypt的结果如下：

[![](https://p0.ssl.qhimg.com/t01bcac042f8f082ad7.png)](https://p0.ssl.qhimg.com/t01bcac042f8f082ad7.png)

我们已经显示了CMDencrypt的结果，但是我们协议的其他symbol需要做相同的工作。结果，我么能得到每个symbol的完整定义。

好了，消息格式的推断结束了。按照现在我们对于每个symbol的理解，我们来逆向协议的状态机。

<br>

**0x04 推断状态机**

**生成一个状态机链**

教程的第一部分我们着重逆向协议的消息格式。我们现在开始逆向状态机，如说明授权的消息序列的语法。在这个部分，通过学习观察消息序列我们生成3种antomata。在Netzob中对象Session表示消息序列。而且当和symbols一起时（一组相似消息的组合的抽象），抽象消息的序列用abstract session表示。这个对象被用来推测状态机。

在这个部分，我们将介绍3种方法来生成基于我们的PCAP文件的automata。

基于我们学习的symbols，我们我们将首先生成一个基本的automaton，来描述从PCAP文件中导出的命令和响应的序列。对于每个消息的发送，将创建一个新的状态，因此命名为chained states automaton。

[![](https://p3.ssl.qhimg.com/t01aa7de7c68df842b5.png)](https://p3.ssl.qhimg.com/t01aa7de7c68df842b5.png)

获取到的automaton最终能转化为dotcode，图形展示如下。

[![](https://p0.ssl.qhimg.com/t0144220770c4ebce76.png)](https://p0.ssl.qhimg.com/t0144220770c4ebce76.png)

**生成一个状态机**

这时，代替将PCAP转化为我们观察到的每个消息的序列的状态，我们生成一个唯一的状态来接收任何发送消息触发的状态转变。每个发送消息的响应（如CMDencrypt），我们需要一个指定的响应（如REDencrypt）。

[![](https://p0.ssl.qhimg.com/t014f740b652439d091.png)](https://p0.ssl.qhimg.com/t014f740b652439d091.png)

获得的automaton转化为dotcode，图形展示如下。

[![](https://p2.ssl.qhimg.com/t01e8796442a5e93546.png)](https://p2.ssl.qhimg.com/t01e8796442a5e93546.png)

**生成一个基于PTA的automaton**

最后，我们将不同的PCAP文件导出的消息序列转化为生成一个我们已经合并相同路径的automaton。底层合并策略被称为Prefix-Tree Acceptor。

[![](https://p1.ssl.qhimg.com/t01542a71a16703e98a.png)](https://p1.ssl.qhimg.com/t01542a71a16703e98a.png)

获得的automaton转化为dotcode，图形显示如下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010a06912b3f5efe06.png)

<br>

**0x04 流量生成和fuzzing**

**根据推断的模型产生消息**

我们现在已经理解了消息格式和目标协议的语法。让我们测试下这个模型，通过尝试和真实的服务器通信。

首先，启动服务器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019e8b4d4a3f4676f3.png)

然后我们创建一个UDP客户端，交互推断出的消息与服务器通信（127.0.0.1:4242）。 在Netzob中，这个角色表示了通信的远端端口。这个角色可以收发遵循推测的状态机和消息格式的数据。为了转化symbols为具体的消息，或者为了将收到的具体的消息转化为symbols，一个抽象层被使用。这个组件确保了发送的symbols和接收的消息抽象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017f7b8356fe37b29c.png)

在automaton中我们有8个迭代。

[![](https://p3.ssl.qhimg.com/t01a815e5a7d83053ac.png)](https://p3.ssl.qhimg.com/t01a815e5a7d83053ac.png)

关于真实的服务器，我们能看见接收到的消息格式正确，因为服务器能解析他们并正确响应。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0157ed84b06c4c6d75.png)

**Fuzzing一个指定的symbol**

最终，我们选择CMDencrypt的消息格式。修改的格式与缓冲区字段的大小的扩展一致。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011e705cfdbb4d0947.png)

我们能看见Netzob仅仅发送了包含长的最后一个字段的CMDencrypt消息。

```
[+] Sending: 'CMDencrypt#6x00x00x00&amp;xe0*xb3xa8A(x0bxd2yAxb5xb8rwx0fGixeexb3xd6xb0&lt;xfcxc0xa7mxbdxbcxde2~xceExe5xda@xd4xedxedxf2xb4xe7txfbCxbfx05xc6xcexfbx83xf2x00'
(...)
```

在服务端，我们会得到错误消息，由于解析最后一个字段的bug导致的。

[![](https://p2.ssl.qhimg.com/t01f2d6cdce17d9f264.png)](https://p2.ssl.qhimg.com/t01f2d6cdce17d9f264.png)

教程到此就结束了。现在你们应该能用Netzob来推断消息格式，甚至必要的语法。

关于这个教程，整个脚本可以在这找到：[https://dev.netzob.org/attachments/download/183/inference_target_src_v1.py](https://dev.netzob.org/attachments/download/183/inference_target_src_v1.py)

同时，不要忘了读[API文档](https://netzob.readthedocs.org/en/latest/)，如果过有任何问题可以和netzob开发团队交流。
