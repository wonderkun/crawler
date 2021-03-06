> 原文链接: https://www.anquanke.com//post/id/181951 


# Zigbee安全入门（一）—— 技术介绍和安全策略


                                阅读量   
                                **220737**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t012fd2f2e00794ba38.jpg)](https://p3.ssl.qhimg.com/t012fd2f2e00794ba38.jpg)



最近忙着考试，《Windows调试艺术》鸽了好久没更新（在写了，在写了），而考完试又是紧张刺激的小学期，需要完成的是一个基于Zigbee的温湿度调控系统，这一刻，我终于想起了自己还是个物联网专业的学生……于是就有了这个系列的文章，主要是给大家分享一些Zigbee的基础知识以及Zigbee安全性上的探讨。

选用的硬件是TI（德州仪器）的CC2530，需要的软件主要是IAR和串口调试工具。



## 什么是Zigbee？

Zigbee说白了就是类似wifi、蓝牙的一种交换数据的方式，学术点说就是低成本、用于低功耗嵌入式设备（无线电系统），用以促进机器与机器之间高效且有效通信（通常相距10-100米）的无线技术。它建立在IEEE802.15.4的基础上，比起蓝牙，它能建立更大的网络（蓝牙的piconet最多支持7个设备），比起wifi，它虽然速度差很多，但功耗相应的也要低不少，因此它非常适合家庭、工厂等应用场景。小米近期推出的家庭网关设备也正是因为Zigbee的这些优势才选择了这项技术。

上面提到的IEEE的802.15.4主要是定义了协议栈的PHY层和MAC层，而Zigbee则是在其基础上建立了完整的协议栈。之后我们会对Zigbee的每一层再进行详细的说明。

[![](https://p5.ssl.qhimg.com/t010767b215f23387fb.jpg)](https://p5.ssl.qhimg.com/t010767b215f23387fb.jpg)

Zigbee将设备划分成了三类，协调器（Coordinator）、路由器（Router）、终端（EndPoint或是EndDevice）。
- 协调器是整个Zigbee网络的发起者、管理者，功能包括：对网络进行初始化，包括制定网络的信道、PANID（网络的标识符，比如一个信道内可以存在多个Zigbee网络，每个网络就由PANID来区分）；配置网络的安全级别和配置信任中心的地址（默认是协调器自己，且每个Zigbee网络只能有一个信任中心），信任中心用来分发网络和端到端应用程序配置管理的密钥，当一个路由器想要加入网络，也需要信任中心的许可；维护当前关联的设备信息。如图，可以在给的Sample中Tools目录下的f8wConfig.cfg中修改信道和PANID
[![](https://p1.ssl.qhimg.com/t01b0c9c456d0baf341.jpg)](https://p1.ssl.qhimg.com/t01b0c9c456d0baf341.jpg)
- 路由器负责在终端设备之间或终端设备与协调器之间路由数据包，同样需要维护当前关联的设备的信息，而且它作为网络的连接点，是不能休眠的。
- 终端负责感知信息，它不允许其他设备关联自己，相当于树的叶子
Zigbee常见的网络拓扑结构主要有一下几种

[![](https://p5.ssl.qhimg.com/t017d561f703970d13b.jpg)](https://p5.ssl.qhimg.com/t017d561f703970d13b.jpg)

图中提到的PAN协调点也就是协调器的意思，FFD（FFD-Full Function Device全功能设备）即可以当做三类设备中任一一类使用的设备，而RFD（RFD-Reduced Function Device精简功能设备）则只可以当做终端使用。实际上我们一般买到的都是FFD，只是在将代码导入设备时，根据选择的不同编译器会做不同的处理，最终生成三类不同的设备，如图，在IAR中可以直接修改

[![](https://p3.ssl.qhimg.com/t0138a4b1ed5cf40392.jpg)](https://p3.ssl.qhimg.com/t0138a4b1ed5cf40392.jpg)

Zigbee采用short地址方式标识网络内的设备，short地址是16位的，是由所属的网络分配的，类似我们网卡的ip地址，要注意因为short地址只有16位，所以Zigbee的最大接入设备数是65535。



## Zigbee的协议栈

上面说了Zigbee的协议栈是在IEEE802.15.4的基础上建立的，那么要搞懂Zigbee的协议栈就要首先把15.4给搞明白，这就要涉及到无线网络的知识了。

首先是802协议的相关内容，15实际上是WPAN（wireless personal area network无线个域网），也就是为了实现近距离通信而设置的，其中15.1就是我们熟悉的蓝牙，15.4是zigbee，而我们最了解的wifi其实是802.11，也就是WLAN（Wireless Local Area Network 无线局域网）。

由于这部分内容居多无比，所以本文只概括性的进行一下解释，具体的各层分析会放在以后的文章中

[![](https://p3.ssl.qhimg.com/dm/1024_780_/t01392f4066a9ed613f.jpg)](https://p3.ssl.qhimg.com/dm/1024_780_/t01392f4066a9ed613f.jpg)

### <a class="reference-link" name="%E7%89%A9%E7%90%86%E5%B1%82%EF%BC%88PHY%EF%BC%89"></a>物理层（PHY）

它指定了Zigbee使用的是2.4GHz物理层和868、915MHz物理层，均基于直接序列扩频（DSSS）技术。而DSSS技术有如下两个特点：
- DSSS使用一串连续的伪随机码(pseudonoise， PN)串行，用相位偏移调制的方法来调制信息。这一串连续的伪随机码称为码片(chips)，其每个码的持续时间远小于要调制的信息位。即每个信息位都被频率更高的码片所调制。因此，码片速率远大于信息位速率。
- DSSS通讯架构中，发送端产生的码片在发送前已经被接收端所获知。接收端可以使用相同的码片来解码接收到的信号，解调用此码片调制过的信号，还原为原来的信息。
该层最主要的任务就是在两个对等MAC实体间提供可靠链路，它提供PHY数据服务和PHY管理服务两种服务，PHY数据服务使PHY能通过物理无线信道传输和接收PHY协议数据单元(PPDU)；PHY管理服务为PLME（这是一个管理该层的实体，可以通过调用它提供的接口对该层进行管理）提供的接口。

### <a class="reference-link" name="MAC%E5%B1%82"></a>MAC层

在《计算机网络》这门课中我们学过非常经典的CSMA/CD（也就是多点接入、载波监听、碰撞检测）来避免线缆传输信息时造成的碰撞，实际上这是定义在802.3的内容，它定义了MAC通过这种方式来避免冲突。但上面提到了“线缆”二字，也就是说这玩意是针对有线网络而言的，实际上它是通过电压变化检测来冲突，那么问题来了，我现在是无线网络，这上哪检测电缆电压去？所以这里我们换了一种想法，我们不再去检测它是不是冲突了，而是尽可能避免冲突，这也就是CSMA/CA（多点接入、载波监听、碰撞避免）。Zigbee的802.15.4和wifi的802.11都是在MAC层通过这种办法来避免冲突的。

我们需要关注的还有安全性的问题。上层会将MAC层的默认密钥设置为网络的密钥，而MAC层则会将上层的链接密钥设置为自己的链接密钥。此外，MAC层采用cbc-mac来进行加密。（关于各类密钥的说明见下文）

同样，MAC也提供了MAC数据服务和管理服务，也有管理实体，叫做MLME

以上是对802.15.4规定的层的简单说明，以下便是Zigbee建立的上层

### <a class="reference-link" name="%E7%BD%91%E7%BB%9C%E5%B1%82%EF%BC%88NWK%EF%BC%89"></a>网络层（NWK）

网络层向上通过NLDE实体与应用层联系，通过NLME管理该层，主要包括了配置新设备，启动网络，执行加入网络，重新加入网络和离开网络的功能，提供寻址功能，邻居发现，路由发现，接收控制和路由等功能。安全性方面主要是AES-CCM*

### <a class="reference-link" name="%E5%BA%94%E7%94%A8%E5%B1%82%EF%BC%88APL%EF%BC%89"></a>应用层（APL）

由上面的图可以看出该层主要分为两部分，一是APS，也就是应用支持子层，二是一堆的object。

APS目的是为了提供NWK和APL之间的接口。和其他层一样，同样提供了两项服务，一是APSDE在应用实体之间提供数据传输服务，二是APS管理实体APMSE，主要是提供安全服务，设备绑定和组管理。APS层基于链接密钥或网络密钥的帧安全性。APS层负责安全的传输向外传出的帧和安全的接收传入的帧以及安全的建立和管理加密密钥所需的处理步骤。上层通过向APS层发布原语来控制加密密钥的管理。

一堆的object则又可以分为两部分，一部分是254个用户可以自己选用的应用object，他们通过绑定端号实现，实际上就和我们在计算机上常说的端口类似，应用间的通信也是基于端号实现的；另一部分是ZDO（Zigbee Device Object，Zigbee设备对象），ZDO负责初始化APS，NWK和安全服务提供商。它组装了来自末端应用程序的配置信息，来确定和实现设备和服务发现，安全管理（密钥加载，密钥建立，密钥传输和身份验证），网络管理（网络发现，离开/加入网络，重置网络连接和创建），绑定，节点和组管理，负责管理设备的安全策略和安全配置。



## Zigbee安全策略

### <a class="reference-link" name="Zigbee%E5%AE%89%E5%85%A8%E5%AF%86%E9%92%A5"></a>Zigbee安全密钥

上文中我们提到了链接密钥和网络密钥，但并没有具体解释到底是什么，这里我们就来详细说明一下。
- 主密钥：构成两个设备之间长期安全性的基础，仅由APS使用。
- 网络密钥，主要用在广播通信，每个节点都要有网络密钥才能与其他节点安全通信。可以是通过密钥传输（网络设备向信任中心发出请求，要求将密钥发送给它）获得，或者是预安装（制造商将密钥安装到设备本身，用户进行选择）获得，由NWK和ZigBee的APL应用该密钥
- 链接密钥，主要用在单播通信，当节点与节点应用通信时，信任中心会生成一个链接密钥并通过网络密钥加密发送至节点，也被叫做唯一密钥；而节点在加入网络时信任中心会给它分配与信任中心通信的链接密钥，这叫做全局密钥。当然，也可以用过与安装的方式获得。链接密钥比起网络密钥多了一种获得方式——密钥构造。所谓构造就是通过主密钥和其他参数算出来一个链接密钥出来，这样就可以避免了服务之间可能存在的冲突和安全隐患（毕竟算出来，你是你，我是我，井水不犯河水）默认的全局信任中心链路密钥由ZigBee联盟定义。如果应用程序在加入时未指定其他链接密钥，则默认值为5A 69 67 42 65 65 41 6C 6C 69 61 6E 63 65 30 39
### <a class="reference-link" name="Zigbee%E5%AE%89%E5%85%A8%E6%A8%A1%E5%9E%8B"></a>Zigbee安全模型

Zigbee支持两种不同的网络安全管理方式，主要区别就是新设备的处理方式和信息的保护，我看大佬们将它翻译为安全模型，那我也就这样用了……

[![](https://p3.ssl.qhimg.com/t01b6a9406791beef47.jpg)](https://p3.ssl.qhimg.com/t01b6a9406791beef47.jpg)

如图为集中式安全模型，这种模型需要我们上面提到过的信任中心来负责安全事务。我们可以通过协调器来指定信任中心或默认使用协调器作为信任中心。当有一个新设备要加入网络时，首先在配置信息添加新设备的信息，然后为该设备建立唯一的信任中心链接密钥（也就是在MAC层我们提到过的链接密钥），以实现与信任中心的通信。

建立的过程主要是根据安装码，安装码说白了就是一串通过16位循环冗余校验的128位随机数字，信任中心会通过Matyas-Meyer-Oseas（MMO）哈希函数从安装码派生唯一的128位信任中心链接密钥

信任中心会维护一个网络密钥用来加密信息，并且定期或根据需要切换，来保证网络信息的安全性。

另外，在集中式模型中，可以使用基于证书的密钥建立协议（CBKE）来分发密钥。可以根据制造时存储在两个设备中并由证书颁发机构（CA）签名的证书与信任中心协商对称密钥。

我们提到的大多数技术也是在此模型上建立的。

[![](https://p5.ssl.qhimg.com/t018f453994d1e5460b.jpg)](https://p5.ssl.qhimg.com/t018f453994d1e5460b.jpg)

如图为分布式安全模型，最主要的就是信任中心被“分散”了，负责安全的成了路由器，路由器来注册接入网络的设备，链接密钥在加入网络时各设备预先配置，而网络密钥由路由器分发给接入的设备，并且同一网络使用同一密钥。

### <a class="reference-link" name="Zigbee%E5%AE%89%E5%85%A8%E6%8E%AA%E6%96%BD"></a>Zigbee安全措施

上文提到了Zigbee采用了AES-CCM*的来保证数据的完整性、可靠性、安全性。
- 发送端，将要发送的数据组织为128位的数据块，然后进行AES-CCM*的处理，得到的是加密的128位数据和一个生成的MIC（消息完整性代码，它是通过使用128位密钥加密IEEE MAC帧的部分而创建的）
- 接收端将收到的数据去除掉MIC，然后进行AES-CCM*处理，得到解密的128位数据，并且有生成了一个MIC，检查这个MIC和接收的MIC是否一致即可判断数据是否完整、正确。
[![](https://p1.ssl.qhimg.com/dm/1024_400_/t0166fad8b57476f647.jpg)](https://p1.ssl.qhimg.com/dm/1024_400_/t0166fad8b57476f647.jpg)

上文讲述了设备加入集中式安全模型的网络时信任中心会给予其一个链接密钥，Zigbee通过住宅模式和商业模式进行不同的处理
- 住宅模式，新加入的设备有可能没有网络密钥，没有受保护的链路，但是还是要接收信任中心的链接密钥，这时候就是不安全的发送了；当然，如果有网络密钥的话，会等待信任中心的消息，通过这条特殊的消息确认信任中心的地址，然后在进行相应的设置。
- 商业模式，信任中心通过不安全的方式向加入设备发送一个主密钥，然后双方通过密钥建立协议（SKKE），然后建立链接密钥。
Zigbee还在预防重放攻击（啥是重放攻击这里就不再展开了）上做了很多工作。Zigbee的每个节点维护了一个32位的帧计数器，数据包每次传递时它就会自增，同时它也会跟踪自己连接设备的帧计数器，当发过来数据包，上一个的帧计数器还是和自己相同或者甚至还比自己小，那就说明有问题了，于是就把这个包丢掉。

上文我们还说到了Zigbee会更新自己的网络密钥。当信任中心认为该更新网络密钥时，它先生成一个新的密钥，然后借助旧的密钥加密分发给其他节点，并将节点的帧计数器清0。注意，新网络密钥建立存在延时，节点仍旧会保持旧的密钥一段时间。

这一篇文章仅仅是大体上对Zigbee进行了分析，之后会进入具体的协议栈实现、代码分析等的内容。建议大家去买俩节点试试，还是挺有意思的。
