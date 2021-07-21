> 原文链接: https://www.anquanke.com//post/id/186099 


# 工控安全入门（二）—— S7comm协议


                                阅读量   
                                **434107**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01269d5e4f1847c828.jpg)](https://p5.ssl.qhimg.com/t01269d5e4f1847c828.jpg)



在上一次的文章中我们介绍了施耐德公司的协议modbus，这次我们把目标转向私有协议，来看看另一家巨头西门子的S7comm。首先要说明，这篇文章中的内容有笔者自己的探索，有大佬们的成果，但由于S7comm是私有协议，一些结论和看法不可能完全正确，希望各位有认为不对的地方或是更好的看法可以评论告诉我。

ps：有些专业名词可能不对，因为没找到准确的翻译或者是根本没找到官方定义（毕竟是私有协议），笔者就自己起了名……

建议阅读本篇前首先阅读：[工控安全入门（一）—— Modbus协议](https://www.anquanke.com/post/id/185513)



## S7comm简介

西门子是德国的一家超大型企业，在能源、工业、医疗、基建等等方面都有它的身影，同时它也位列全球500强第66名。作为一个以电报起家的大型企业，它对于通信更是重视，S7comm就是西门子为了它生产的PLC之间、SCADA与PLC之间的通信而设计的专属协议。

和Modbus的应用层协议不同，S7comm的协议栈修改程度更高，在应用层组织的数据经过COTP协议、TPKT协议的进一步处理后，最终通过TCP进行传输，下面是wireshark wiki给出的S7comm的协议栈：

|OSI layer|Protocol
|------
|Application Layer|S7 communication
|Presentation Layer|S7 communication(COTP)
|Session Layer|S7 communication(TPKT)
|Transport Layer|ISO-on-TCP (RFC 1006)
|Network Layer|IP
|Data Link Layer|Ethernet
|Physical Layer|Ethernet

我们说的题目虽然是对S7comm的分析，实际上是对整个协议栈的探索。鉴于数据包逻辑上是由高层进行封装再一步步的转递给较低层，但我们接收到包后是低层一层层拆卸交给上层，基于逆向思维，我们之后的分析应该是由低向高展开的



## TPKT协议

我相信大家对于传输层往下的内容应该比较熟悉了，都是TCP/IP的基本内容，我就不再赘述，直接从会话层来看。

TPKT协议是一个传输服务协议，它为上层的COPT和下层TCP进行了过渡。我们常用的RDP协议（remote desktop protocol，windows的远程桌面协议）也是基于TPKT的，TPKT的默认TCP端口为102（RDP为3389），其实它本身为payload增加的数据并不多，主要就是以下几个：

[![](https://i.loli.net/2019/09/06/8JeRab3nNxZBkDg.png)](https://i.loli.net/2019/09/06/8JeRab3nNxZBkDg.png)
- version，1byte，表明版本信息
- reserved，1byte，看到这个名字就知道是保留的了
- length，2byte，包括payload和这三部分在内的总长度
下面我们就用之前分析过的2018工控比赛的流量包来实际看一下

[![](https://i.loli.net/2019/09/06/ewQv9mufKVtsiaP.png)](https://i.loli.net/2019/09/06/ewQv9mufKVtsiaP.png)

可以看到，版本号是3号，长度为31，除此之外该层并没有什么有用信息了



## COPT协议

COPT协议的全称是Connection-Oriented Transport Protocol，即面向连接的传输协议，从这个名字就可以看出，它的传输必然是依赖于连接的，所以在传输数据前必然有类似TCP握手建立链接的操作。

让我们先来看看具体的流量包

[![](https://i.loli.net/2019/09/06/VQWDfcE4jth3Z6S.png)](https://i.loli.net/2019/09/06/VQWDfcE4jth3Z6S.png)

首先是TCP的三次握手，在192.168.25.146与192.168.25.139间建立了TCP连接，之后是两个COTP的包，注意，这里wireshark为我们标注出了CR和CC，后面的COTP包都是DT，这里的CR和CC其实分别是connect request和connet confirm的，也就是建立连接的过程，之后连接建立成功后，发送DT包，也就是data ，是在发送数据。

我们接着再看看他们携带的数据

[![](https://i.loli.net/2019/09/06/YPRnDuLtzZ1E7GN.png)](https://i.loli.net/2019/09/06/YPRnDuLtzZ1E7GN.png)

可以看到，DT包和连接包有着明显的不同，连接包明显多了一堆内容，这其实是COPT包的两种形态，COTP连接包（COTP Connection Packet）和COTP功能包（COTP Fuction Packet）

首先来看COPT连接包，通过上面的wireshark的分析我们可以看到，主要有以下几个字段：
- length，1byte，数据的长度，但并不包含length这个字段（个人感觉很奇怪……）
<li>PDU type，1 byte，标识类型，图中的0x0d即为连接确认的类型，常有的还有
<ul>
- 0xe，连接请求
- 0x0d，连接确认
- 0x08，断开请求
- 0x0c，断开确认
- 0x05，拒绝- 前四位标识class，也就是标识类别
- 倒数第二位对应Extended formats，是否使用拓展样式
- 倒数第一位对应No explicit flow control，是否有明确的指定流控制<li>code，1byte，标识类型，主要有：
<ul>
- 0xc0，tpdu的size，tpdu即传送协议数据单元，也就是传输的数据的大小（是否和前面的length有重复之处？）
<li>0xc1，src-tsap，翻译过来应该叫源的端到端传输（在完整的TCP/IP协议栈中，这个字段代表的是应用与应用之间的通信，我这里猜测可能是为了），但从西门子给的手册来看，它标记的应该是机架号，可是不管我怎么查，也没有找到wireshark解析出的字符串。那么逆向我们找不到答案，就只能正向来了，在parameter字段的最后我们再来详细说这到底是个啥。
[![](https://i.loli.net/2019/09/04/IiUVYODBqEW9y6F.png)](https://i.loli.net/2019/09/04/IiUVYODBqEW9y6F.png)
</li>
- 0xc2，dst-tsap，同上，之后我们再探索
接着COPT功能包，其实个人感觉这两种包可以归为一种，但是看到文献都是分为两种的，那我们也就划分为两种吧
- length，1byte，长度
- PDU type，1 byte，图中为0x0f，即为数据传输，此外的type都不太常用，这里不再提了（其实是我没找到相关的流量包……有这方面流量的大佬希望补全以下）
<li>option，1byte，以位为单位划分：
<ul>
- 第一位，标识是否为最后一个数据包（从这可以看出，COPT协议当数据较多时，会分为几个单元传输
- 后七位，标识TPDU的number
到这COPT包我们就算是分析的彻彻底底了，当然，上面还留了个小问题，parameter里的tsap到底是个什么东西？一些我们看上去整不明白的参数到底是干啥的呢？既然逆向不行了，我们就通过正向开发来看看，这到底是个啥，以下使用Simatic NET 软件（做的时候忘记截图了……图片来自[http://www.ad.siemens.com.cn](http://www.ad.siemens.com.cn/)）。

[![](https://i.loli.net/2019/09/07/6aXV7sCz8bnl4YD.png)](https://i.loli.net/2019/09/07/6aXV7sCz8bnl4YD.png)

我们配置了一台local的OPC服务器（OPC服务器可以理解为转换协议的一种设备），目标是实现它和PLC的通信。我们选择使用Ethernet，并分别配置了机器的ip地址和子网。

[![](https://i.loli.net/2019/09/07/hbW2RVgcLUe8JB3.png)](https://i.loli.net/2019/09/07/hbW2RVgcLUe8JB3.png)

接着我们进入地址的细节，发现了TSAP和RACK/SLOT两个重要的选择项，实际操作我们才发现，RACK是指CPU的机架号，而SLOT是指是CPU的槽位号，通过这两个参数我们就可以唯一指定一个CPU。

那说明手册有错？那怎么可能，人家好歹也是个大厂，玄机就在这个TSAP上。其实它有三部分组成：
- 连接号（我瞎起的名，确实是没找到这玩意叫啥），指的是连接方式，03就是单向通信，单向的可以连接多个设备，10以上的就是双向的，双向的就没法多个设备了。
- 机架号，就是RACK
- 槽位号，就是SLOT
如图所示，我们为OPC服务器配置的是12.11，也就是双向通信，1号架1号槽位，而PLC则是03.02，单向通信，0号架2号槽位。那么问题又来了，这和我们流量里的数据包完全不一样啊！

[![](https://i.loli.net/2019/09/07/ZEslVFD6rkmTRKN.png)](https://i.loli.net/2019/09/07/ZEslVFD6rkmTRKN.png)

数据包里是SNOPCCxxxx，咋解释？这可一点也不符合我们上面的说明，这其实是另外一种连接方式，叫做S7优化连接，比起之前的连接方式，这种连接可以以符号的形式访问数据块。

它规定了src-tsap为SNOPCC000x000xxx，第一个x笔者没有搞明白代表了什么，第二个是连接数，图中即为有一个连接，而在dst-tsap必须为SIMATIC-ROOT-OTH 。刚好也和我们的数据包对应。所以我们分析的数据包应该是一个单向连接，连接的数目是一个。

到这里，我们对于COPT可以说是精确到每一位了，虽然还有一些地方有瑕疵，但总体来说是没什么问题了。



## S7comm协议

总算是来到了最后的S7comm协议，它的结构很简单，主要分为三部分：
- Header，主要是数据的描述性信息，最重要的是要表明PDU的类型
- Parameter，参数，随着不同类型的PDU会有不同的参数
- Data，具体的数据
[![](https://i.loli.net/2019/09/08/r9K4bcyzP3A6YhC.png)](https://i.loli.net/2019/09/08/r9K4bcyzP3A6YhC.png)

首先我们就具体来看看这个Header有什么玄机

[![](https://i.loli.net/2019/09/08/vwHyeXRjTg1Sm6I.png)](https://i.loli.net/2019/09/08/vwHyeXRjTg1Sm6I.png)
- Protocol id，1 byte，即协议的id，为0x32
<li>ROSCTR，1byte，pdu的类型，一般由以下几种：
<ul>
- 0x01，job，就是开工干活的意思，主设备通过job向从设备发出“干活”的命令，具体是读取数据还是写数据由parameter决定
- 0x02，ack，0x02，确认
- 0x03，ack data，从设备回应主设备的job
- Reserved，2byte，保留
- PDU reference，pdu的参考
- parameter length，参数的长度
- error class，错误类型，像是图中的0x00就是没有错误的意思，而常见的请求错误则是0x85
- error code，错误码，结合错误类型来确定错误，图中的0x00同样是没有错误的意思
关于具体的错误类型和错误码的信息大家可以自行搜索，因为太多了这里就不再展开说明了。而parameter取决于不同的pdu类型，所以这里也不再说了，下面来看看具体的流量包

[![](https://i.loli.net/2019/09/08/WK2X5Jg1EvLyimM.png)](https://i.loli.net/2019/09/08/WK2X5Jg1EvLyimM.png)

可以看到该pdu为job，也就是主设备在发号施令，而通过parameter可以看到，function是0x04的read，也就是读取数据，item count意思是后续跟了几个item，该pdu就一个，所以为1。而这个item的结构就有要单独说说了：
- variable specification，1byte，一般就是0x12（我没见过别的……）
- 长度，Length of following address specification，数据的长度
- Syntax Id，符号id，一个标志，决定了一些格式性问题，这里是0x10是Address data S7-Any pointer-like DBx.DBXx.x的意思，具体啥意思我们在看完下面几条后再提，详细的大家还是可以去自己看看，主要就是对于后续的寻址起到了一定的限定
- 传输大小，也可以认为是传输类型，在这是4，也就是WORD
- DB number，就是数据块编号的意思，0就代表要找的东西不在数据块里
- area，要操作的“东西”，比如0x82，就是读设备的输出，通过这一位也可以看到，我们要读的数据不在DB里，所以DB number为0，如果为DB的话，这1byte应该为0x84
- address，具体的地址，如下图所示，前五位没用到，第六位到第二十一位是Byte地址，最后三位是Bit的地址
[![](https://i.loli.net/2019/09/08/kYZjMtDx4ouhWnq.png)](https://i.loli.net/2019/09/08/kYZjMtDx4ouhWnq.png)

首先，它定义了格式为Address data S7-Any pointer-like DBx.DBXx.x，然后指定了读取的”东西“为设备的输出，读取的大小为word，其实到这里这个pdu的全部信息就已经分析完了，但是为了让大家更好的理解上面定义的格式，我们还是继续看一下。

它读的DB number是0那么根据格式就是DB0.DBXx.x，而读取的address是Byte为0，Bit为0，也就是DB0.DBX0.0，如果我们指定的”东西“为数据块的话，就按照这种格式读取。这就是格式的意思，再比如说0xb2，描述为Symbolic address mode of S7-1200，实际上格式就是符号地址，就不再是这样的组织形式了。

[![](https://i.loli.net/2019/09/08/I2EgPS84JHtzOid.png)](https://i.loli.net/2019/09/08/I2EgPS84JHtzOid.png)

再来看看上个pdu的相应，这里截图没截到header，header最值得关注的是pdu的类型，这里是0x03，也就是我们之前提到过的对于job的相应

而paramter部分可以看到，function是与job pdu的相同的。Data部分就是传回来的具体数据了，return code是返回码，用来标识job让干活的结果，这里是0xff，代表的是成功的意思，除了这个，还有以下几种：
- 0x01，硬件错误
- 0x03，想访问的东西不让访问
- 0x05，地址越界了
- 0x06，你请求的数据类型和请求的”东西“的数据类型不一致
接着是data的长度（是真的data的长度，不包含前面），最后就是具体的data了，可以看到，这里读到的是0x0000。

到此，S7comm协议我们也认识的差不多了，下面就让题目了。



## 2018年工业信息安全技能大赛（东北赛区）工业协议数据分析

因为19年的题目涉及到S7comm的上次我们已经做了一个了，所以这次就找了个别的题目，首先来看流量包

[![](https://i.loli.net/2019/09/08/rDkAKENV9fBJ7iI.png)](https://i.loli.net/2019/09/08/rDkAKENV9fBJ7iI.png)

可以看到一大堆的协议，不过整体思路还是刚才清晰的，首先是ARP协议去找mac地址（不知道arp的，补一下计算机网络的知识吧……），接着是标准的TCP三次握手，接着是COPT的建立连接（要不以后我叫他两次握手？），接着就到了S7comm和modbus来具体干活了。

我们可以看到这个job和我们之前的并不一样，打开仔细瞧瞧

[![](https://i.loli.net/2019/09/08/pBNOQMYa5CZ7us3.png)](https://i.loli.net/2019/09/08/pBNOQMYa5CZ7us3.png)

可以看到parameter中的funtion为0xf0，是建立通信的意思，这其实是和上面的TCP、COPT有些相似的，都是在两个设备之间建立通信，而参数的主要信息是MAX AMQ calling和MAX AMQ called。

下面一个ack_data的pdu自然是相应建立通信的意思了，经过TCP握手、COPT建立连接、S7comm建立通信，这样设备间的通信才正式建立完毕了。

往后的S7comm可以看到是read，也就是在读数据，数据包和上面提到的一样，不再赘述。经过查找，并没有flag。

这时候就要考虑modbus协议中是否存在flag了，这时候就要用到之前modbus的技巧了，1、2、3、4的function code没有大规模取数据的能力，flag一般都在他们之外，进行下简单的过滤，打印出相应的数据就ok了

脚本还是用上一篇文章的就可以，这里就不在放了，需要的去上一篇取即可（不水字数了）。

最终flag为modbusICSsecurityWin



## 总结

S7comm作为一个私有协议，它的可出题点其实更多，而且由于是私有协议，很多地方都还有挖掘的空间，这篇文章只是带大家按照我的思路，从无到有的分析了S7comm的各个部分，肯定有不完全正确的地方，也肯定有细节没有考虑到，希望大家能更进一步，探索更多的秘密。
