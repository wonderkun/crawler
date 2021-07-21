> 原文链接: https://www.anquanke.com//post/id/185513 


# 工控安全入门（一）—— Modbus协议


                                阅读量   
                                **509126**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01269d5e4f1847c828.jpg)](https://p5.ssl.qhimg.com/t01269d5e4f1847c828.jpg)



最近参加了工控安全方面的比赛，也了解了一些工控安全方面的知识，这次就和大家分享一下工控领域常用的modbus协议的相关知识。

## modbus基础知识

modbus协议最初是由Modicon公司在1971年推出的全球第一款真正意义上用于工业现场的总线协议，最初是为了实现串行通信，运用在串口（如RS232、RS485等）传输上的，分为ModbusRTU、Modbus ASCII两种，后来施耐德电气将该公司收购，并在1997年推出了基于TCP/IP的Modbus TCP。现在使用最多的就是Modbus TCP了，我们今天的主角也是它。

Modbus作为一种通信协议，它和我们之前介绍的Zigbee有很大不同，Zigbee有自己完整的协议栈，而Modbus是一种应用层的报文传输协议，它既可以在物理层面上选择串口进行简单的串行通信，也可以使用TCP的方式进行传输。

[![](https://i.loli.net/2019/08/31/AFw67f9IvXn2VjN.png)](https://i.loli.net/2019/08/31/AFw67f9IvXn2VjN.png)

上图可以看到Modbus的协议栈仅仅是在传统ISO/OSI模型的基础上对数据链路层和应用层做了定义。也正是因为modbus是应用层的协议，所以它的安全漏洞并不只是它本身，TCP/IP的漏洞也可以利用在modbus上，最典型的就是18年工控比赛的题目，中间人。

modbus是一种主从协议，主设备的一方向从设备的一方下达指令，从设备的一方根据指令做出反应并回复主设备，主设备可以有多个从设备。具体来说，工作人员的计算机可认为是master，而PLC之类的具体设备就是slave了。每个设备有自己的“代号”，主设备通过“代号”来找到某一个对应的设备，当然也可以使用广播的方式，代号0即为广播。

[![](https://i.loli.net/2019/08/31/2T93iyNlp6k1nLQ.png)](https://i.loli.net/2019/08/31/2T93iyNlp6k1nLQ.png)

从协议栈还可以看到，Modbus有自己的数据链路层定义，其实主要是对于传输数据格式和校验等方面的规定。具体来说，modbus定义了自己的数据单元，功能码与具体的数据组成了PDU（协议数据单元 Protocol Data Unit），所谓的功能码也就是代表了主向从下达的指令是什么，这是很重要的一个知识，后面我们会具体讲功能码代指的功能，数据也就是这次指令要用到的“参数”。

[![](https://i.loli.net/2019/08/31/p8BlydqkEV1hbsC.png)](https://i.loli.net/2019/08/31/p8BlydqkEV1hbsC.png)

很显然，只有PDU并不够，我们还需要知道从设备的“代号”才能知道数据往哪发，还要想办法保证数据的完整性、一致性和可靠性。所以在PDU的基础上我们还需要添加一个地址，和一个差错校验，这就构成了ADU（Application Data Unit）。但要注意，由于三种Modbus在传输中存在差异，所以ADU，特别是校验部分会有不同。



## modbus功能码

前面说过通过功能码主设备能够对从设备下达指令，功能码有效范围在1~255之间。其中大部分都是保留的，如128-255为异常响应保留，举几个栗子：
- 01 读线圈状态
- 02 读离散输入状态
- 03 读保持寄存器
- 04 读输入寄存器
- 05 写单个线圈
可能看到这里大家就懵了，这都是啥啊。其实很简单，modbus可以说是将读写指令分为了两大类，一类是离散的，也就是位操作，非1即0；第二类是模拟的，也就是数字，可以叫做字操作。而每一类下面都有输出和输出之分，于是就有了下面四种说法：
- DO（digital output 数字量输出），所谓线圈就是离散的输出状态，01即读一个离散的输出状态，举个不恰当的栗子，你家灯泡接到某个控制器上（实际上并不会存在这种情况……），我们可以通过01加上数据，比如1，让他亮，加上0，让他灭。
- DI （digital input 数字量输入），所谓的离散输入就是它，还是上面的栗子，我们想知道灯的开关是咋样的呢？就用02指令看看，如果是1，哦，按下去了，如果是0就是没按。通过这个不恰当的栗子我们大概也可以猜到，这是不可写的（如果你随便一个指令把开关给按死了，那我这灯不是彻底开不了了？），可以理解为外部对工控系统所带来的“开关”影响。
- AO（AnalogOutput 模拟输出），保持寄存器的功能，和DO最大的不同就是它不再是0或1，可以是一个数值，比如，我们设定的PID运行参数，或者是温度的上下限等等
- AI（Analog Input 模拟输入），也就是输入寄存器，和DI一样，可读但不可写，可以理解为外部对于系统的多位输入
当然有写单个的就必然有写多个的，比如15就是写多个线圈，16是写多个保持寄存器。此外还有读文件记录的20，写文件记录的21，获取异常状态的08等等，这里就不在多说了，具体的大家可以自行查看手册。

当然，说到功能码就不得不提Modbus在施耐德设备上的一个重要漏洞了。这就是在defcon上展示过的fun with 0x5a，这个0x5a的功能码是由施耐德自己实现的非标准的功能码，该功能码实现了Modbus标准未允许的功能。在defcon中大佬为我们展示了以下几项

[![](https://i.loli.net/2019/08/27/TIcXLuQKjpUfGn2.png)](https://i.loli.net/2019/08/27/TIcXLuQKjpUfGn2.png)
- 获取项目和PLC信息
- 开启、停止PLC
- 下载程序
- 更改程序
这里先不做过多介绍，在之后我们再详细看一看0x5a攻击的流量包。



## Modbus TCP

上面说了我们这次的主角是Modbus TCP。我们可以通过wireshark对Modbus的流量包进行抓取进而观察Modbus TCP的数据格式

```
Transaction identifier ： 事务标识符
Protocol identifier ： 默认为0
Length : 数据的长度
Unit identifier ： 从机地址，因为使用了TCP/IP所以用ip地址来标识从机，所以该位可忽视，或者做进一步分发
Function code ： modbus的功能码
Data ：具体的数据
```

可以看到在遵从TCP/IP的基础上Modbus加了自己的修改，主要有以下三个部分：
- 由于TCP/IP本身具有数据校验部分，所以ADU的差错校验没有了
- 实用ip可以确定从机，ADU的附加地址也不再有效。但是目标可以继续是一个主机，再向其他从机发送数据，这时ADU的附加地址可以作为下一个主机分发数据包时的地址。
- 增加了TCP/IP的头部，比如length、协议标识符等
[![](https://i.loli.net/2019/08/31/ANi81zYqhUnRCjb.png)](https://i.loli.net/2019/08/31/ANi81zYqhUnRCjb.png)



## Modbus赛题及漏洞

### <a class="reference-link" name="2019%E5%B7%A5%E6%8E%A7%E5%AE%89%E5%85%A8%E6%AF%94%E8%B5%9B%20%E7%BA%BF%E4%B8%8A%E8%B5%9B%E7%AC%AC%E4%B8%80%E5%9C%BA%20Modbus%E9%A2%98%E7%9B%AE%EF%BC%88%E7%AC%AC%E4%B8%80%E7%89%88%EF%BC%89"></a>2019工控安全比赛 线上赛第一场 Modbus题目（第一版）

首先说明一下，这个题目就是前不久工控比赛的线上赛第一场的签到题，但貌似后来又换了个附件，因为也不知道题目是否正确，这里就不再追求flag了，看一下题目本身涉及的知识点。

首先wireshark打开pcap流量包

[![](https://i.loli.net/2019/08/31/cCuzZxNSPE7J1Q3.png)](https://i.loli.net/2019/08/31/cCuzZxNSPE7J1Q3.png)

可以看到在tcp握手后就是清一色的func 90。这就是上面我们提到过的施耐德高危功能码，它是施耐德自定义的非标准功能码，功能及其强大，就相当于root般强大。

这个高危功能码是通过Unity Pro与PLC通信时发送的，Unity Pro像其他开发工具一样提供了stop、读取项目信息、debug、修改代码等功能，这些功能并没有办法通过标准的指令码发送，所以就有了0x5a（也就是90）。后来，工控安全研究和顾问公司Digital Bond在metasploit上放出了0x5a的poc，再后来defcon上有人做了”fun with modbus 0x5a“的演讲，这个漏洞算是被熟知了。

首先看第一个Modbus的数据包，我们前面说过，Modbus作为主从协议，必然是主发从响应的，也就是说，在该环境下，100为主机，而253很显然就是从设备了。功能码是0x5a高危功能，携带数据为0002，此时，我们并不知道该功能到底做了什么。

[![](https://i.loli.net/2019/08/31/jcFyzkKDlbr6HvM.png)](https://i.loli.net/2019/08/31/jcFyzkKDlbr6HvM.png)

接着看返回的包

[![](https://i.loli.net/2019/08/31/Oq8E1JkBeQHSUtM.png)](https://i.loli.net/2019/08/31/Oq8E1JkBeQHSUtM.png)

可以看到它符合我们前面对于Modbus的说明，指令码同样是0x5a，同时带回来一部分数据，没有进行任何的加密，直接解码发现存在字符串140 CPU 311 10

```
&gt;&gt;&gt; str.decode("hex")
"x00xfex10xffZx01x01x00x00x00px02x00x00'x00tx00x08x00x00x00x00x00x0e140 CPU 311 10x01x01x01x00x00x00x00x11x00"
```

搜索后发现是施耐德家的一款产品，就是下面图上的家伙

[![](https://i.loli.net/2019/08/31/XUcxqfr58P2QBnw.png)](https://i.loli.net/2019/08/31/XUcxqfr58P2QBnw.png)

我们可以推测，上面的指令应该是在获取从机的设备信息。往下走还可以看到有这样一个数据包

[![](https://i.loli.net/2019/08/31/fTM3wIcRz62S9Pl.png)](https://i.loli.net/2019/08/31/fTM3wIcRz62S9Pl.png)

它的回复则是这样的

[![](https://i.loli.net/2019/08/31/xaXvGmDq9zQnrgc.png)](https://i.loli.net/2019/08/31/xaXvGmDq9zQnrgc.png)

Project字符串很明显，而x0cx3bx0cx0ex01xdex07是项目文件上次修改的日期，x08x00x00是项目的修订号，翻译成人话就是项目在2017年1月14日12时59分12秒进行了第8版的修改

继续向下探索还可以发现诸如”USER-714E74F21B“之类的字符串，可以看到它获得了大量的设备及项目相关信息。再往下就不在具体分析了，有兴趣的可以自行研究。（建议去利用unity Pro操作，抓取相应的流量包来分析具体0x5a的data功能）

我们可以利用主机的流量包还原出攻击者的脚本，实际上就是类似funwithmodbus0x5a的攻击脚本，大家去github下载，msf上也有相应的。

### <a class="reference-link" name="2019%E5%B7%A5%E6%8E%A7%E5%AE%89%E5%85%A8%E6%AF%94%E8%B5%9B%20%E7%BA%BF%E4%B8%8A%E8%B5%9B%E7%AC%AC%E4%B8%80%E5%9C%BA%20Modbus%E9%A2%98%E7%9B%AE%EF%BC%88%E7%AC%AC%E4%BA%8C%E7%89%88%EF%BC%89"></a>2019工控安全比赛 线上赛第一场 Modbus题目（第二版）

这个题目是真的签到题，非常简单……首先还是看一下流量包

[![](https://i.loli.net/2019/08/31/8TqFRAZecWNdXE7.png)](https://i.loli.net/2019/08/31/8TqFRAZecWNdXE7.png)

可以看到，比起上一个这个可太友善了……都是些正常的功能码。23是主机，33则是从机，没什么很明显的TCP/IP攻击的痕迹，整体看上去没啥问题。

接下来就该考虑是否有数据的写入，flag很有可能就是写入的数据。那么首先排除12345的功能码，因为flag既不可能是位操作，也不可能是字操作，都太短了，所以聚焦的就应该是包长度大的，或者是类似16功能码那样写多个字的指令。

这里给出我的脚本，是第二种思路，也就是筛选1234之外功能码的包并打印内容

```
import pyshark
func_code = [1,2,3,4]
def find_flag():
     pcap = pyshark.FileCapture("q1.pcap")
     for c in pcap:
         for pkt in c:
             if pkt.layer_name == "modbus":
                 temp = int(pkt.func_code)
                 if temp not in func_code:
                     payload = str(c["TCP"].payload).replace(":", "")
                     print("content[*] is " + payload)
```

也可以用[scu–igroup](https://github.com/scu-igroup/ctf_ics_traffic)老哥的脚本，用第一种思路，找长度最大的包提取数据，结果相同（速度还很快…自己写的脚本在遇到流量包很大的情况下速度很慢）

[![](https://i.loli.net/2019/08/31/AwQEU1chsHo4MPY.png)](https://i.loli.net/2019/08/31/AwQEU1chsHo4MPY.png)

转换为ascii码就得到了最终答案

[![](https://i.loli.net/2019/08/31/gSNczl6apGimv4C.png)](https://i.loli.net/2019/08/31/gSNczl6apGimv4C.png)

### <a class="reference-link" name="2018%E5%B7%A5%E6%8E%A7%E5%AE%89%E5%85%A8%E6%AF%94%E8%B5%9B%20%E7%BA%BF%E4%B8%8A%E8%B5%9B%E7%AC%AC%E4%B8%80%E5%9C%BA%20Modbus%E9%A2%98%E7%9B%AE"></a>2018工控安全比赛 线上赛第一场 Modbus题目

这个题目就涉及到了Modbus在TCP上的漏洞了，首先我们还是看看题目给的流量包

[![](https://i.loli.net/2019/08/31/gVcisrjWNvuIw9D.png)](https://i.loli.net/2019/08/31/gVcisrjWNvuIw9D.png)

说真的一看这包我当时就愣了，这啥玩意，一个modbus的包咋这么多tcp呢？定睛一看才发现都是TCP的重传，说明啥？说明有可能是中间人攻击啊。

但是，其实这个题目的中间人其实并没有什么关系……因为我们要的是流量，而modbus的长流量必然是在1234四个功能码之外的……当然这道题还有变数，因为存在S7comm，所以其中也有可能藏有flag，所以我们先手动检查S7comm，发现没有重要信息后，再来进行下一步

还是上一个题目的脚本，很容易找到相应的流量

[![](https://i.loli.net/2019/08/31/z7mPXER2rbCNKIp.png)](https://i.loli.net/2019/08/31/z7mPXER2rbCNKIp.png)

这段数据不是传统的data，进行了加密，所以我一时陷入了僵局，只能通过胡乱组合最终还真碰巧出来了…….因为我并没有参加18年的工控比赛，所以我不知道当时主办方给没给加密方法，但搜到的题目中有相应的解密脚本，如下：

```
#!/usr/bin/python
#coding:utf-8

coils_bytes = 'c29e46a64eeaf64e3626c2ae0ec2a22ac24c0c8c1c'.decode('hex')
print len(coils_bytes)
flag = ''
for data in coils_bytes:
        #print int('`{`:08b`}`'.format(ord(data)))
        #print int('`{`:08b`}`'.format(ord(data)), 2)
        #print int('`{`:08b`}`'.format(ord(data))[::-1])
        #print int('`{`:08b`}`'.format(ord(data))[::-1], 2)
    #print int('`{`:08b`}`'.format(ord(data)),2),int('`{`:08b`}`'.format(ord(data))[::-1], 2)
    flag += chr(int('`{`:08b`}`'.format(ord(data))[::-1], 2))
print flag
```

这里还有个坑，我跑脚本时没有过滤掉data外其他的数据，所以导致脚本跑不出来……因为19年那个题没加密直接转字符就成，所以我也没注意到这个问题（实际上就是截图中flag意外的奇怪字符），只能手动找到了相应的流量包提取了data……

最终flag为

[![](https://i.loli.net/2019/08/31/WsrhRPx95aDolVg.png)](https://i.loli.net/2019/08/31/WsrhRPx95aDolVg.png)



## 总结

通过上面几道题目可以看到modbus目前在ctf中还是以简单题目为主，基本上就是过滤出特殊功能码的流量包进行简单的转换即可，但实际上modbus的还存在许许多多的安全隐患，未来有很多可以出题的点。
- 传统TCP/IP存在的问题，比如18年的中间人攻击，虽然并没有涉及到过多的知识点，但毫无疑问这方面可以做文章
- 异常的功能码，比如19年的第一版，施耐德的高危功能码，这是非常难的，从之前的分析可以看到这些保留的功能码在厂商自定义后对于我们普通的参赛选手来说是很难真正读懂流量包的，需要配合相应的正向使用知识，和正向使用的流量包来进行学习
- 认证、授权、加密的一系列问题。从题目可以看到，该协议根本没有认证方面的定义，攻击者需要的仅仅是一个合适的ip地址而已，至于授权更是无从谈起，加密方面也是漏洞百出。
- 缓冲区溢出，未来没准会出现pwn？
这次参加工控比赛收获了不少新知识，也花了不少时间来消化，算是开启了一个新领域的学习，以后也会在这方面多下点功夫，希望能拿个好成绩。
