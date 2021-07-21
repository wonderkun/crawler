> 原文链接: https://www.anquanke.com//post/id/186587 


# 工控安全入门（三）—— 再解S7comm


                                阅读量   
                                **479035**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01269d5e4f1847c828.jpg)](https://p5.ssl.qhimg.com/t01269d5e4f1847c828.jpg)



之前的文章我们都是在ctf的基础上学习工控协议知识的，显然这样对于S7comm的认识还不够深刻，这次就做一个实战补全，看看S7comm还有哪些值得我们深挖的地方。

本篇是对S7comm的补全和实战，阅读本篇之前一定要先阅读以下文章，掌握基本的S7comm知识：

[工控安全入门（二）—— S7comm协议](https://www.anquanke.com/post/id/186099)

本篇文章依然有很多笔者自己摸索的内容，可能存在错误，同时也发现了wireshark对于s7comm解析的几个模糊之处，希望大家能帮忙指正。本次选用的流量包来自于github的w3h，有兴趣的同学可以下载下来仔细研究。

[https://github.com/w3h/icsmaster/tree/master/pcap](https://github.com/w3h/icsmaster/tree/master/pcap)



## s7comm_reading_setting_plc_time

首先来大体上看一下流量包

[![](https://i.loli.net/2019/09/13/sio59F2T8ylwu6L.png)](https://i.loli.net/2019/09/13/sio59F2T8ylwu6L.png)

可以看到，主机是192.168.1.10，设备为192.168.1.40，首先是tcp包，但传输失败了，之后调用arp解析到了40的mac地址，接下来通过tcp的三次握手来建立连接，通过COPT的CR和CC建立了通信，最后再利用S7comm的job建立了通信。这是s7comm在两个设备建立通信的一般流程，到此为止，利用我们上一篇文章的知识都可以完美解决，可是再往下就出了问题，这个userdata的包是个啥？

我们打开看看具体的细节

[![](https://i.loli.net/2019/09/13/xograbtWGs5MqAy.png)](https://i.loli.net/2019/09/13/xograbtWGs5MqAy.png)

可以看到大体结构和我们上一篇文章所讲的无异，最主要的就是PDU的类型不一样导致后面的跟的参数我们看不明白了。不要慌，这个时候就要慢慢来分析了。

首先ROSCTR变为了0x07，wireshark给出的是Userdata，翻译过来是用户数据？那就不对了，如果我们把设备比作电脑的话，我们之前用的job更像是一般用户的操作，而这个Userdata嘛更像是程序员的操作，比如说它可以用来读取SZL（后面会说这是个啥）、调试、安全等等方面。（是不是感觉有点像modbus的0x5a操作？）

也正因为它包含了复杂的功能，所以Parameter比起job更为复杂，这里主要要关注两项。
<li>function，1byte，wireshark已经帮我们解析为了8位
<ul>
- 前四位，标识pdu的状态或者说是类型，比如说图中的0100对应request，说明该pdu是主机请求设备的。而作为回应的有0000，对应push，推迟了请求；或者是10
- 00，对应response，对于该请求的返回
- 后四位，标识方法所属的类型，这里是0100，对应的是cpu功能
那么szl到底是个啥呢？其实它是系统状态列表的缩写，本来标准缩写应该是SSL（system status list官方手册上也是这么写的），但因为西门子是德国的，在德语中”状态“是z开头的，于是就成了szl。简单说就是当前设备的状态信息，包括很多重要的信息。可以看到Data中有SZL-ID和Index两个字段，这俩就用来指示要读取的内容

[![](https://i.loli.net/2019/09/13/8OrSUNw2nGtu7HF.png)](https://i.loli.net/2019/09/13/8OrSUNw2nGtu7HF.png)

ID占两个字节，意思分别如下：

[![](https://i.loli.net/2019/09/13/jU1SqAO6vYmXxWF.png)](https://i.loli.net/2019/09/13/jU1SqAO6vYmXxWF.png)
<li>前四位，diagnosit type，直译是诊断类型，实际上就是说明要操作的对象是啥| Bit | Type |<br>
| —— | —— |<br>
| 0000 | Cpu |<br>
| 1100 | cp |<br>
| 1000 | Fm |<br>
| 0100 | im |</li>- 中间4位，这个应该是wireshark解析错误了，可以看到官方文档给出的是4位，而wireshark给出的是16位，显然是不对的。这里的数字是要提取的局部列表的值，简单说就是这表东西有点多，你当然可以全输出，但更多时候我们还是只需要其中的一部分。
<li>后八位表明表明局部列表的序号，这里是0x32wireshark为我们说明这个局部列表是通信状态数据，具体的各类局部列表的序号如下（我们关注的是最后两个字节）：[![](https://i.loli.net/2019/09/13/dJguZIjc3xTniGa.png)](https://i.loli.net/2019/09/13/dJguZIjc3xTniGa.png)
</li>
这里SZL-ID的完整意思就是，从编号为0x32的局部列表（写作W#16#xy32）中提取0x01的内容（写作W#160132），0x01意思是通用通信数据，index是0x04，即对象管理系统（写作W#16#0004，这个index旧版的手册上没有），这就组成了完整的请求。根据我们写作的格式查找手册即可查询具体作用。

再看看这个pdu的回复，可以看到data tree就是读取到的信息

[![](https://i.loli.net/2019/09/13/jLTzpQP3D6h7rFO.png)](https://i.loli.net/2019/09/13/jLTzpQP3D6h7rFO.png)
- key，关键交换机的保护等级
- param，分配的保护等级
- real，合法的cpu保护等级
- bart_sch，这是当前的状态，图中为RUN_P，此外还有RUN、STOP等等
- crst-wrst，这是wireshark给的解释，我认为此处应该是anl_sch，即初始的设定，这里是0，也就是没有出事设定
- res，看到reserved就是保留的（但这里保留的字节是不是太多了……）
接着看下一个PDU，对应的包是第16个

[![](https://i.loli.net/2019/09/13/4gorTIuk9GEtwWO.png)](https://i.loli.net/2019/09/13/4gorTIuk9GEtwWO.png)

还是和上面一个套路，不过这次的SZL-ID和index都是0，这可怪了，按照上面我们给出的分析方法，似乎找不到这个特殊的家伙，这时候我们就需要结合response来进行逆推了

[![](https://i.loli.net/2019/09/13/mlaSZkyQwTIJDze.png)](https://i.loli.net/2019/09/13/mlaSZkyQwTIJDze.png)

可以看到返回了一大堆数据，而这些很眼熟啊，正好就是SZL-ID啊，所以我们就可以推断出，上面一个request的作用是检查所有存在的局部列表。

后面的pdu就不再展开分析了，都是在读取cpu类的相关信息，只不过是指定的局部列表不同、index不同罢了，大家有兴趣的可以自行往下看。



## step7_s300_stop.pcapng &amp;&amp; snap7_s300_stop.pcapng

stop绝对是对工控设备最重要也是最容易出事的指令了，一个不小心就会酿成大祸。这里给大家分析两种stop的包，首先简单说一下背景：
- step 7，这是个用于管理和组态项目中所有设备的工具，界面非常友好，使用也很简单
- snap7，是个开源的西门子s7系列的通信库，支持多种编程语言
首先来看snap7的吧，流量包就两个pdu，是我们已经熟悉的job和ack_data，我们打开job来详细看一下

[![](https://i.loli.net/2019/09/13/Ai9y7laH1zBx8YE.png)](https://i.loli.net/2019/09/13/Ai9y7laH1zBx8YE.png)

这里可以看到整体十分简单，唯一一个有疑惑的地方就是PI Service，这个PI Service是程序调用服务的意思，它标识包括启动、停止等等的服务，它本身最常用在0x28的function中，0x28标识PI service包，再通过PI service这个字段来标识具体的功能。因为stop的重要性，所以在s7comm中把它从PI service包中单独拿了出来，作为stop包，并将PI service字段置为P_PROGRAM。

再看step 7的stop

[![](https://i.loli.net/2019/09/13/vRPNdnmce3Cip2a.png)](https://i.loli.net/2019/09/13/vRPNdnmce3Cip2a.png)

比起snap 7的stop，step 7在其基础上又额外有两个pdu，都是userdata，我们一个一个看

[![](https://i.loli.net/2019/09/13/AuH4axs8fMKSvpq.png)](https://i.loli.net/2019/09/13/AuH4axs8fMKSvpq.png)

结合上面的知识我们知道：直接看function，0000标识push，0100标识是cpu类的方法，子方法说明这是诊断信息。而下面data中的cpu diagnostic message也就是诊断信息的具体内容，给了俩理由，一个是stop操作导致停止；一个是SFB 20停止。SFB的全称是system function block，系统功能块，这是为用户提供的程序集合，可以理解为设备系统的一部分，它是不能被修改删除的。

[![](https://i.loli.net/2019/09/14/NVaLoQt7h6mk8w1.png)](https://i.loli.net/2019/09/14/NVaLoQt7h6mk8w1.png)

第二个包就有意思了，首先和上面一样是一个push，但这次的类是mode-transition，这个可是个新东西。

该类的方法用来切换设备的工作状态，在该类的包中没有Data段了，仅仅靠Current mode来决定要做什么。图中为stop，即停止运行的意思。除此之外，常用到的还有Warm Restart（暖启动，重启程序，但数据不变）、Hot Restart（完全从停止的状态开始运行）、Cold Restart（重启，并重置数据）、RUN（运行）等等。



## step7_s300_AuthPassword.pcapng

该流量包是step 7 软件对plc进行密码修改，如下：

[![](https://i.loli.net/2019/09/14/ga1ZIkR97ezvpmh.png)](https://i.loli.net/2019/09/14/ga1ZIkR97ezvpmh.png)

前两个包是读取CPU状态的，和上面分析的相同，不再废话，直接从第三个开始看

[![](https://i.loli.net/2019/09/14/8jGPKTtarXLMz7i.png)](https://i.loli.net/2019/09/14/8jGPKTtarXLMz7i.png)

这次的类又变了，成了security，这个类实现的功能非常少，就是一个设置密码，一个清除密码，如图这里subfunction标识了是设置密码，data就是加密后的新密码。

加密过程非常的简单：

首先对前两个数与0x55进行异或操作0x21^0x55 = t ，0x3a^0x55 = o

接着对剩下的数操作，操作为与自己距离为-2的数进行异或，再与0x55异或，如：0x1b^t = o

脚本如下：

```
list = [0x21,0x3a,0x1b,0x1d,0x6e,0x68,0x1b,0x1d]
passwd = []
for i in range(0,len(list)):
    if i==0 or i==1:
        passwd.append(chr(list[i]^0x55))
    else:
        passwd.append(chr(list[i]^0x55^list[i-2]))
print passwd
```

解得新设置的密码为toor 。第四个包为回应，没有特别之处，剩下两个同样是查询信息。



## s7comm_downloading_block_db1

大体看一下流量包

[![](https://i.loli.net/2019/09/14/sMZCr6AGvyDH7dl.png)](https://i.loli.net/2019/09/14/sMZCr6AGvyDH7dl.png)

一开始是建立通信的操作，之后对设备信息进行了查询，关键是后面，出现了block function和resquest download，我们一点点看

[![](https://i.loli.net/2019/09/14/TZMsxfFaohIiv4z.png)](https://i.loli.net/2019/09/14/TZMsxfFaohIiv4z.png)

可与看到为块方法类，这就需要详细解释一下西门子设备里的块到底是怎么样一个概念了。西门子的plc程序采用的是结构化设计，就像是我们的c语言，我们会分成很多模块进行编写（包括程序、数据），最后在main函数里调用，而块这个概念就是对应着我们c语言里的不同模块。
- OB，object block，相当于main函数，由它去调用其他块
- SFB、SFC，前面提到过，就相当于是系统给你写好的函数，直接调用就完事了
- FB、FC，自己写的函数，可以在OB中调用
- DB，数据块，放数据的
可以看到系统函数和自己写的函数都有C和B的区分，最开始接触时，就简单的理解为，C的就是没有全局变量的函数，没有存下来什么；而B就是带全局变量的函数，它修改了全局变量。

当然，上面的理解有些简单粗暴，但却很有道理。B就是block，而这个block是指DB，B不光是有函数，它还有自己的数据块用来存放数据，这个数据块也叫做背景数据块；而C呢则是使用的共享的数据块，调用时临时分配给他一块数据块，用完就收回来，它不会对数据进行持续性的保留。

举个栗子，如果你设备上有1、2两个器件，他们各自有各自的运行状态和收集到的数据，如果你执行的操作并没有涉及到数据，那可以用B，但如果你要将各自的数据收集，那就要用有背景数据块的C了。

聊完了什么是块之后我们继续看这个包，子方法是1，意思是列出所有的块，除了该方法外，该类还有：
- 列举块类型（List blocks of type）
- 读取块的信息（Get block info）
我们之后还会看到，先看看这包的回复

[![](https://i.loli.net/2019/09/15/9QnTup3OqBgb16L.png)](https://i.loli.net/2019/09/15/9QnTup3OqBgb16L.png)

可以看到和上一篇文章中的read var同样使用了item来组织内容，item包含块的类型和数量，OB作为s7的main，必然是1个，FC、FB数量则取决于用户的定义，而SFC、SFB的数量则和系统挂钩。

之后几组（一个request和一个response组成）包都是重复操作，直到37，使用了Get block info的方法

[![](https://i.loli.net/2019/09/15/ruwqN5h3zpPMJ8b.png)](https://i.loli.net/2019/09/15/ruwqN5h3zpPMJ8b.png)

很显然block type指定了块的类型，而number则是块的编号，这里涉及到了一个新的概念，文件系统
- P（Passive module)：被动文件系统
- A (Active module)：主动文件系统
- B (Active as well as passive module)：主被文件系统
这里的意思就是读取第一个DB块

[![](https://i.loli.net/2019/09/15/GzQNMc6WOULnPgy.png)](https://i.loli.net/2019/09/15/GzQNMc6WOULnPgy.png)

接着看response，可以看到最关键的字段为Error code，根据上面item我们知道DB块实际上是0，根本没有number=1的情况，所以不能回复相应的数据，这时就会回应error code，这里的error code即没有对应的块。data中的内容也是”对象不存在“。

相应的如果数据块存在的话，回复的数据就应该是DB的数据。

[![](https://i.loli.net/2019/09/15/6W4FMeDHkjxOdTZ.png)](https://i.loli.net/2019/09/15/6W4FMeDHkjxOdTZ.png)

往下走看到了request download，它是job包的一种，所以一定是（job，ack_data）这样的组合。主要关注的是

filename，由几个字段共同组成，用来唯一指定一个块
- file identifier，文件标识符一般由_ (Complete Module)、$ (Module header for up-loading)两种
- block type，块的类型，这里是0A
- block number也就数块的编号
- 文件系统，上面有说过。
response很简单，这里就不再看了。接着往下走download block包

[![](https://i.loli.net/2019/09/15/V4WM19roY6H2npe.png)](https://i.loli.net/2019/09/15/V4WM19roY6H2npe.png)

可以看到和request download差不多，主要看看response的包

[![](https://i.loli.net/2019/09/15/e1H9QciAS6rp3qX.png)](https://i.loli.net/2019/09/15/e1H9QciAS6rp3qX.png)

可以见到，这次带回了数据，还有个关键地方，Function status，它提示我们，还有更多的数据在后面。所以我们可以看到，后续的流量中一直再重复job、ack_data直到出现ended标识才算是真正的完成了一组数据的下载。

[![](https://i.loli.net/2019/09/15/jClFnVHfQgBiL5D.png)](https://i.loli.net/2019/09/15/jClFnVHfQgBiL5D.png)

在之后，会调用PI-Service的_INSE来激活下载的块，这样才算是真正完成了下载的任务。

[![](https://i.loli.net/2019/09/15/BXKSenD4zR69r7F.png)](https://i.loli.net/2019/09/15/BXKSenD4zR69r7F.png)

总结一下，当要对一个块进行下载操作时，往往需要如下几步：

查看块是否存在（Block类中的Get block info） —&gt; 请求下载（request download） —&gt; 下载（由于数据过多可能重复多次） —&gt; 激活块（PI-Service的_INSE）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2019/09/15/J9QnYWVHSN8Ac5O.png)

除此之外我们还可以看到，在激活块后主机10发起来一个RST的请求与设备断开了连接，然后又重新连接，我们并不清楚流量包抓取过程中的实际情况，只能推测有可能是因为更新了数据，所以主机与设备重新建立了通信。



## 总结

某大佬说过，安全不是ctf。我们可以看到比赛题目中的S7comm并没有涉及到文章中的很多知识，但是这些东西我认为也十分重要，实际过程中我们接触的更多也是这样的流量包，只有掌握好这些最基础的知识，才能更进一步。

这次实际分析了三个流量包，实际上我给的链接中还有很多，只不过我认为这几个最有代表性，有了这几个的基础，相信剩下的也不是问题。
