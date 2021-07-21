> 原文链接: https://www.anquanke.com//post/id/187221 


# 工控安全入门（四）—— DNP3协议


                                阅读量   
                                **584695**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01269d5e4f1847c828.jpg)](https://p5.ssl.qhimg.com/t01269d5e4f1847c828.jpg)



我们之前看过了法国施耐德的Modbus、德国西门子的S7comm，这次就让我们把目光投到美洲，看看加拿大的HARRIS的DNP3有什么特别之处。

这次选用的流量包部分来自w3h的gitbub：

[https://github.com/w3h/icsmaster/tree/master/pcap/dnp3](https://github.com/w3h/icsmaster/tree/master/pcap/dnp3)

分析借助到的可执行文件和代码来自：

[https://code.google.com/archive/p/dnp3/](https://code.google.com/archive/p/dnp3/)



## 基础知识

DNP3全称是Distributed Network Protocol 3，分布式网络协议3，这个协议在各种工业系统中都应用很多。它比起s7comm大刀阔斧做的协议栈要简单的多，是完全基于TCP/IP的，只是修改了应用层（但比modbus的应用层要复杂得多），在应用层实现了对传输数据的分片、校验、控制等诸多功能。

DNP借助TCP在以太网上运行，使用的端口是20000端口，

我们首先来看看最基本的结构，再去进行实际的流量包分析。这一部分可能会很枯燥，但只有彻底理清一遍DNP3的结构，才能帮我们更好的分析DNP3的相关流量包

[![](https://i.loli.net/2019/09/18/LcEjT3X7z5feZ2h.png)](https://i.loli.net/2019/09/18/LcEjT3X7z5feZ2h.png)

可以看到，在应用层DNP3分为了几个部分来处理，就像是在应用层是又搭建了一个协议栈一般。下面就让我们细致的探索一下

[![](https://i.loli.net/2019/09/18/JkOWEifzwsbKcaC.png)](https://i.loli.net/2019/09/18/JkOWEifzwsbKcaC.png)

首先是数据链路层，这个名字听着有点出戏（OSI第二层的链路层一脸懵逼）……它主要是规定了传输的规则，在官方文档上将这部分的数据单元称为LPDU。

它的组成很简单，主要就是以下几部分：
- start bytes，表明数据开始的起始字节，固定为0x0564
- length，长度
<li>control，控制字，这是最重要的一个字段，用一个字节来进行标记
<ul>
- 第一位，direction，听着很高端，但其实就是表明发送的方向
- 第二位，primary，表示发送设备是主设备还是从设备
- 第三位，FCB，翻译过来是“帧的计数位”，但实际上不是用来计数而是用来纠错的。如果是response的话则为保留位
- 第四位，FCV，这一位说明FCB是否有效，在上图中为0，就表示FCB未开启。如果是response的话则为DFC，数据链路层是否发生缓冲区溢出
<li>后四位，控制方法码，这个码可没有S7comm的功能码那么“变态”，它并不直接指示功能，只是对包进行分类而已，更像是Type，对于主设备来说
<ul>
- 0，链路重置
- 1，进程重置
- 3，请求发送数据
- 4，直接发送数据
- 9，查询当前链路的状态
对于从设备来说
- 0，同意
- 1，拒绝
- 11，回应当前链路状态
到此数据链路层结束，接下来又冒出来个TC（Transport control），看这个名字就知道是要仿照OSI的传输层，不过这个比起上面可要简单很多，实现的功能主要就是标注当前的包是第几个包。

[![](https://i.loli.net/2019/09/19/f3Pq7cLSwABrlRW.png)](https://i.loli.net/2019/09/19/f3Pq7cLSwABrlRW.png)
- 第一位是final，标识是否为最后一个包
- 第二位是first，标识是否为最后一个包
- 后六位为seq，表明当前是第几个包
这里可以注意到一个小细节，本来六位标识的话，包的数量为2的6次方，也就是0到63，乍一看好像是一次最多拆分成这么多包，但是因为有first位、final位，只要final位不为1，那就可以一直传啊！事实上也是如此，在真实情况中，传到63后，下一个包会从0再继续。所以这个设计可太巧妙了，乍一看是“浪费”了两位，实际上反倒是彻底解除了位数的限制。

接下来到了DNP3的应用层的应用层，别觉得很怪，人家就是这么起的名字……

[![](https://i.loli.net/2019/09/20/eyP1VpRz5b6KhYi.png)](https://i.loli.net/2019/09/20/eyP1VpRz5b6KhYi.png)

可以看到应用层结构还是比较清晰的，

主要有以下几部分组成：
<li>control 控制字，按位分为以下：
<ul>
- 第一位，first，表明是否为第一个
- 第二位，final，表明是否为最后一个
- 第三位，confirm，表明是否需要回复，图中即表示不需要回复
- 第四位，unsolicited，表明是否为主动提出的
- 后四位，seq，为队列号，这里的设计和上面传输层的类似，同样可以支持大于2的四次方的包的数量- Obj，即图中的0x3c，这里是数据的基本类型，比如离散还是模拟
- var，即图中的0x02，进一步说明数据的类型，比如是模拟的话，那你是32位还是64位
这里给大家一份可以查询的表格，有需要时查表即可

[![](https://i.loli.net/2019/09/20/lFN1TV7afuHO46n.png)](https://i.loli.net/2019/09/20/lFN1TV7afuHO46n.png)

[![](https://i.loli.net/2019/09/20/gI8sC2NXmv9YnpB.png)](https://i.loli.net/2019/09/20/gI8sC2NXmv9YnpB.png)

[![](https://i.loli.net/2019/09/20/rQF8EphN1CLHcyv.png)](https://i.loli.net/2019/09/20/rQF8EphN1CLHcyv.png)

到这就可以完整的说明数据的类型了，接下来就是限定词，给出了一系列的限制。
- 第一位，保留，wireshark同样没有给出解析信息
- 三位，限定码，这个不太好理解，简单点说是表明一个数据对象的索引的字节数
- 后四位，range，也就是指定的范围的意思，图中6即为读取所需类型的全部数据。往后就是最后的对象了，这个包中并没有，之后会看到。
到这里我们就把DNP3的细节过了一遍，可以看到，DNP3在自己的应用层又搭建一个简易的协议栈用来传输数据，让他有了自己的数据检测、数据分段功能，虽然有很多巧妙的设计带来了传输的帮助，但是其略显繁琐的设计必定要也会导致性能的下降，同时我们也可以看到，它在安全性方面，实在是没什么保障。



## file_read

那么就开始看流量包吧，简单的read write之类的就不再赘述，相信看了上面的描述之后你们绝对是没问题的，让我们来看几个稍稍复杂一点点的。

[![](https://i.loli.net/2019/09/20/Nj4ZGMqiF8AU7pO.png)](https://i.loli.net/2019/09/20/Nj4ZGMqiF8AU7pO.png)

不知道大家看到这种流量会不会觉得亲切，我之前有门课是《网络管理与服务设计》，配置CIFS和NFS时抓到的包都和这种类似，看着包多，但是逻辑很简单，就像是小学生对话一样……

[![](https://i.loli.net/2019/09/20/XtERbLUModkWI4y.png)](https://i.loli.net/2019/09/20/XtERbLUModkWI4y.png)

最重要的参数显然就是object了，这里指定了一堆东西，实际上咱们大部分都可以不管了，注意file control mode为read，也就是读，而文件的最大块的size为1024，最后的filename是重点，也就是说主设备发送了一个请求，想要打开testfile.txt文件

[![](https://i.loli.net/2019/09/20/ycOIPUoCdHqvjiY.png)](https://i.loli.net/2019/09/20/ycOIPUoCdHqvjiY.png)

回应包的内容告诉主设备：“ok，我知道了，你可以打开，它的句柄是0x12345678”，句柄是啥相信不用我再提了吧。

[![](https://i.loli.net/2019/09/20/md6TXacwUD4Zs5n.png)](https://i.loli.net/2019/09/20/md6TXacwUD4Zs5n.png)

主设备告诉从设备：“我要读句柄为0x12345678的文件，而且从第一个block开始读，我要读到最后”，这里的file block即表明开始的位置，而last block就是是不是最后的块，不设置的话就是一口气读到底。

[![](https://i.loli.net/2019/09/20/GJIukOq8vfPDT4W.png)](https://i.loli.net/2019/09/20/GJIukOq8vfPDT4W.png)

从设备回复：“ok，最后的块为第一个块，文件的数据为XXXX”，这里从设备帮我们确定了文件的块数，并将数据返回给我们，数据即为：This is a test file

[![](https://i.loli.net/2019/09/20/ypWq6tE9usAJPLv.png)](https://i.loli.net/2019/09/20/ypWq6tE9usAJPLv.png)

主设备：“我想要关闭0x12345678句柄的文件”

[![](https://i.loli.net/2019/09/20/HUe3WB1p65JAdc7.png)](https://i.loli.net/2019/09/20/HUe3WB1p65JAdc7.png)

从设备：“ok，已关闭”

到此读文件的过程完毕，可以看到虽然看上去很繁琐，但整体就是简单的“对话”，比起s7comm来说相当容易分析了。write的过程类似，我们就只看write包吧

[![](https://i.loli.net/2019/09/20/WidcrTLkSN6QFJg.png)](https://i.loli.net/2019/09/20/WidcrTLkSN6QFJg.png)

主设备：“我想往0x12345678句柄的文件里写东西，开始的块是0，就一个块，内容是hi there”



## file_list_directory

[![](https://i.loli.net/2019/09/22/lkgSqHxoL9ZQs7f.png)](https://i.loli.net/2019/09/22/lkgSqHxoL9ZQs7f.png)

总体流量包很清晰，基本和read file一样，都是打开文件、读文件、关闭文件三部曲，但中间穿插了一些奇奇怪怪的东西，实际上就是DNP3对数据的分段处理，让我们具体看看

[![](https://i.loli.net/2019/09/22/8YMnhxvZKO3cEy5.png)](https://i.loli.net/2019/09/22/8YMnhxvZKO3cEy5.png)

主设备：“我想打开name为.的文件”，有Linux基础的同学应该都知道这个name就是文件夹。

从设备：“ok，句柄为0x12345678”

[![](https://i.loli.net/2019/09/22/s2KHqCbUWDnFXIp.png)](https://i.loli.net/2019/09/22/s2KHqCbUWDnFXIp.png)

主设备：“我要读取句柄0x12345678的内容”

从设备：“有点多。。。你等等”

由于目录的所包含的内容过多，所以并不能一次传输完成，所以这时就要借助传输层的机制来实现分段了

[![](https://i.loli.net/2019/09/22/TzFrneAWSbm87qa.png)](https://i.loli.net/2019/09/22/TzFrneAWSbm87qa.png)

我们上面说过，传输层通过控制字对每一段进行划分，第一个包即为01XXXXXX

[![](https://i.loli.net/2019/09/22/NIgQCRjLma3q4vh.png)](https://i.loli.net/2019/09/22/NIgQCRjLma3q4vh.png)

第二个包为00xxxxxx+1，如此就是实现了分段，而最后一个包变为10xxxxxx，那么主设备也知道了，哦，数据传输完了。



## freeze

其实这样的流量包特别特别简单，但是主要是想提一下freeze这个操作的含义，request如下

[![](https://i.loli.net/2019/09/20/Wwx5cT98UBoFDS2.png)](https://i.loli.net/2019/09/20/Wwx5cT98UBoFDS2.png)

可以看到没什么特别的地方，还是简单的指定了数据对象而已，再看看response就要复杂得多

[![](https://i.loli.net/2019/09/20/JBYjhyaR3vLoVpb.png)](https://i.loli.net/2019/09/20/JBYjhyaR3vLoVpb.png)

里面有一堆参数，我们先不着急看，先搞明白什么是freeze

freeze翻译成中文有冻结的意思，具体的操作是将指定的数据对象放到一个缓冲区（称其为冻结缓冲区）中，但根据他的功能，我觉得叫做shotsnap或许更为合适，它有以下几种类型：
- immediate Freeze，0x7，冻结，需要从设备给予回应
- immediate Freeze no ack，0x8，冻结，不需要回应
- Freeze&amp;Clear ，0x9，冻结，删除原来的数据（这才是真正的冻结吧，打入冷宫），需要从设备回应
- Freeze&amp;Clear no ack，0x10，同上，但无需回应
- Freeze with Time，0x11，指定时间冻结
我们这里用的显然是0x7的，所以不会对原来的数据造成损失，可以看到回复包中一堆的参数，表明的是从设备的“状态”问题，包括像是设备是否重启、设备是否有问题、时间同步等等，这里就不在一一说明了。



## full_exchange

下面来看看这个流量包，开头是TCP的三次握手，不再说了

[![](https://i.loli.net/2019/09/20/7dTHbvaJMlO6jRw.png)](https://i.loli.net/2019/09/20/7dTHbvaJMlO6jRw.png)

第一个DNP就是个让人懵圈的包，从下面很容易看出来1为主设备，130为从设备，怎么上来130就response了呢？其实这是一种特殊情况，我们可以打开包来具体

[![](https://i.loli.net/2019/09/22/XPgnsDMTAHCrqI1.png)](https://i.loli.net/2019/09/22/XPgnsDMTAHCrqI1.png)

我们发现它自发的向主设备发送了一系列的状态信息，而在这之中只有1位是1，重启。那我们可以推测，设备应该是刚刚经历了一次重启，所以它在与主设备重新获得联系后赶紧发送了当前的状态，虽然违背了request-response的规则，但是也不无道理，毕竟主设备在从设备重启后的第一时间就需要知道从设备的相关信息。那我们同样也可以猜测，这个function code很有可能就是从设备在特殊情况下自发传输某些数据。再结合官方文档，我们就可以真正理解这个function，确实是自发上送数据。

接着就是正常的请求包了

[![](https://i.loli.net/2019/09/22/iDPx8l4IjhpbWtw.png)](https://i.loli.net/2019/09/22/iDPx8l4IjhpbWtw.png)

function code为0x15，其实恰好上面，是禁止自发上送某些信息，这个也很好理解，毕竟从设备也不可能说是把数据都自主上传吧，主设备肯定要做一些限制，所以这里就开始对class1 class2 class3进行限制，不允许对这些进行自发的上送。

从设备对该function进行了标准的response，接着主设备又发送了confirm表示确认（该function也是一种特殊情况，不需要从设备进行回复），接下是一个write的function

[![](https://i.loli.net/2019/09/22/IgZ34hKqlovVXDF.png)](https://i.loli.net/2019/09/22/IgZ34hKqlovVXDF.png)

write是看明白了，写的是0也看明白了，但是他写了个啥？intenal indication？上网一搜，啥也没有；谷歌翻译，内部指示，一脸懵逼。

实际上这可不是什么内部指示，只不过是wireshark给的一个名词而已，我们仔细向上翻，其实是能在response里找到的，就是我们之前说得很简单的“状态”，wireshark给的这个名字让我们产生了误解而已。

所以write就是在改写从设备的“状态”信息，看看response有什么变化

[![](https://i.loli.net/2019/09/22/D3J4wFXzOWLIAvm.png)](https://i.loli.net/2019/09/22/D3J4wFXzOWLIAvm.png)

这次全都是0了，可以看到算是恢复了初始状态。

接着进行read操作，读取了相应的信息。最后使用0x15的相反功能，允许自发上送数据，允许从设备对class1、2、3进行上送操作，tcp四次挥手，该包完毕。



## lan_time_sync

先看看整体的流量包

[![](https://i.loli.net/2019/09/22/B5EhJIok913sH8C.png)](https://i.loli.net/2019/09/22/B5EhJIok913sH8C.png)

[![](https://i.loli.net/2019/09/22/TlUSnCGh3d8IkHu.png)](https://i.loli.net/2019/09/22/TlUSnCGh3d8IkHu.png)

大家要是去查现成的资料的话可能会找不到这个Record Current Time的function说明，如果按照它的function code去查的话找到的可能是“未使用”三个大字。

实际上这是因为2017年DNP3进行了一次更新，加入了部分新的function，其中就有这个，实际上就是功能就是记录当前的时间，response倒没什么特别的，接下来是个write操作

[![](https://i.loli.net/2019/09/22/d3iGceN7Ay9WzoZ.png)](https://i.loli.net/2019/09/22/d3iGceN7Ay9WzoZ.png)

它去写的是时间和日期，传送的方式是时间戳，非常简单。



## 总结

这次总结了DNP3的相关细节，并分析了几种实际的数据包来加强理解，当然作为一个协议，他还是很多很多没有提到的地方，大家有兴趣的可以继续尝试下去。
