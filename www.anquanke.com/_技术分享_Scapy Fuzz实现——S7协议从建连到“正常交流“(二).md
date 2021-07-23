> 原文链接: https://www.anquanke.com//post/id/86569 


# 【技术分享】Scapy Fuzz实现——S7协议从建连到“正常交流“(二)


                                阅读量   
                                **125930**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t017bd3737979dc6b93.png)](https://p0.ssl.qhimg.com/t017bd3737979dc6b93.png)

作者：[DropsAm4zing](http://bobao.360.cn/member/contribute?uid=2914824807)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**传送门：**[http://bobao.360.cn/learning/detail/4120.html](http://bobao.360.cn/learning/detail/4120.html) 

[![](https://p3.ssl.qhimg.com/t01996893625a4dd9ec.png)](https://p3.ssl.qhimg.com/t01996893625a4dd9ec.png)

上次酝酿了"三秒钟"，这次还是酝酿的久一点。这次继续上次的点和思路，把这个很low的小程序跑起来，先放一张运行截图做封面，自己总会认为我这个小屁孩这就是在班门弄斧，所以也就尽量的把自己的东西总结好，希望做好。

 

**0x01 关于Set Communication**

****

上次写到建立三次握手、S7协议握手数据包的重放，在文章的最后贴了自己写的建立连接的hello_plc()函数，其中通过Scapy发送数据并接收返回的响应数据包，Scapy接收到的数据格式是元组格式，我们只需要通过诸如“a[1][1]”这样的方式来访问取值，但还可能遇到问题，具体问题只能根据具体情况解决了。

 

**0x02 数据格式**

****

我们通过Wireshark可以看到，交互中的数据基本是“00 01 02 03 ……”这样的方式，如果我们通过TCP调试工具发送数据的当然是可以成功发送并接收数据，但是放到脚本里发送这样的格式会成功么？

答案很明显，肯定是会失败的，怎么搞?

**姿势一：**

```
hello='x03x00x00x16x11xe0x00x00x00x05x00xc1x02x01x01xc2x02x01x01xc0x01x0a'  
 
hello_respon="x03x00x00x16x11xd0x00x05x00x01x00xc0x01x0axc1x02x01x01xc2x02x01x01"
 
set_comm="x03x00x00x19x02xf0x80x32x01x00x00xccxc1x00x08x00x00xf0x00x00x01x00x01x03xc0"
```

上面的姿势可以通过脚本直接发送到设备并建立连接是没有问题的，需要你将“00 01 02 03 ……”通过处理变为上面的变量格式发送交互数据。

针对于建立连接过程，数据内容基本是固定的，所以直接转换格式固定发送即可，但是Fuzz测试的时候，可能需要准备专门的函数来转换格式发送，自认为比较麻烦，所以弃用。

**姿势二：**

测试的时候我们通过Wireshark来获取数据包的内容进行修改重放，所以我们看到的实际是十六进制的ASCII显示，我们需要转换到可直接传输的格式。

[![](https://p3.ssl.qhimg.com/t016b4e53d69f3b2c7f.png)](https://p3.ssl.qhimg.com/t016b4e53d69f3b2c7f.png)

```
def  str2byte(data):
    base = '0123456789ABCDEF'
    i = 0
    data = data.upper()
    result = ''
    while i &lt; len(data):
        beg = data[i]
        end = data[i+1]
        i += 2
        b1 = base.find(beg)
        b2 = base.find(end)
        if b1 == -1 or b2 == -1:
            return None
        result += chr((b1 &lt;&lt; 4) + b2)
    return result
```

相比较上一种方法自觉比较简单粗暴，选用。为什么自己愿意选用这个方式，因为发送的数据遵循固定的报文格式，所以Fuzz可以针对一个特定部分或者几个特定部分进行，随机产生Fuzz数据后，直接拼接为原始数据，然后经过转换直接发送即可。

```
hello   = 010203040506070809 Fuzz原始数据(假设此处为四位整数) 0504030201
fuzz原始数据 = random.randint(1000.9999)
fuzz_data   = str2byte(hello + fuzz原始数据)
```

上面对fuzz数据的产生过程做一个简单的解释，我们可以看到fuzz数据通过随机生成，通过拼接，再转换格式即可发送交互。实际情况是每个部分的数据进行拼接之后进行处理并发送。

 

**0x03 模糊数据**

****

那么模糊数据怎么产生并处理呢？

```
def random_String(n):
   random_string = (''.join(map(lambda xx:   (hex(ord(xx))[2:]), os.urandom(n))))
   return random_string
```

通过上面的函数产生指定长度的模糊数据，这里仍然存在问题，一些功能对应的数据报文是如“000a”这样的格式，而上面的函数只能生成如“a”、“2012”，不能生成前面为0的格式的数据(如“0001 001a”)，当时被坑惨了，然后一步步输出调试的时候才发现使这里除了问题。

zfill()函数: 这个函数解决了上面的问题，str.zfill(width)通过width指定字符串的长度，原字符串右对齐，在前面补0.

```
Protocol_ID   = '32'
ROSCTR   = ROSCTR_dict[random.randint(0, 1)]
Redundancy_Identification   = '0000'
Protocol_Data_Unit_Reference   = random_String(2).zfill(4)
Parameter_Length   = '0008'
Head_Data_Length   = (
    hex(
        ((int(TPKT_Length, 16))*2 - 14 -   36)/2
    )[2:]).zfill(4)
Header   = Protocol_ID + ROSCTR + Redundancy_Identification +   Protocol_Data_Unit_Reference
         + Parameter_Length +   Head_Data_Length
```

上面这是一段自己定义的通过Wireshark识别之后，数据报对应的各个部分的数据内容，有些部分是固定的格式，那么暂时不做Fuzz，那些保留字段或者可变字段，进行随机生成处理。Wireshark内置了对S7协议的分析代码，可以下载源码进行查找分析。下面就来看看S7协议相关的一些点。

[![](https://p2.ssl.qhimg.com/t01ee0a4e264f1dbb68.png)](https://p2.ssl.qhimg.com/t01ee0a4e264f1dbb68.png)

Wireshark已经针对数据中的每个部分做了解析，所以在学习了解S7协议的时候，Wireshark是必不可少的工具之一，通过Wireshark的解析，我们清楚的看到包括TPKT、COTP、S7 Communication这三个大的部分。大概结构如下:

TPKT包含了Version、Length和一个保留参数

COTP包含了Length、PDU类型和一个我不知道含义的参数(PS:为自己的无知捏一把冷汗)

S7 Communication包含了Header、Parameter、Data

我们的Fuzz目标针对于S7 Communication部分，前两部分的参数相对固定，我们一定要注意的是每部分中的“Length“对应的含义。

[![](https://p5.ssl.qhimg.com/t01760638aa0c7c33c1.png)](https://p5.ssl.qhimg.com/t01760638aa0c7c33c1.png)

TPKT: 含有Length参数，表示整个数据的长度

COTP: 含有Length参数，表示COTP除Length参数之外的长度

Header: S7协议的Header部分，含有Parameter Length和Data Length参数，分别表示Parameter和Data的长度

Parameter: S7协议的Parameter部分，含有Parameter Length参数，表示这部分此参数之后的数据长度。

Data: S7协议的Data部分，含有Length参数，表示Data部分data的长度

<br>

**0x03 运行日志**

****

通过上一部分对数据格式的了解，Fuzz脚本已经可以实现出来，我们继续讨论完善，如何判断Fuzz数据是否对设备造成了影响(比如: 设备状态异常)？如何实时的保存造成设备异常的报文呢？

```
def   fuzz_analysis(data):
    if len(data[0]) == 0:
        fuzzlog.write("%sn" %   binascii.hexlify(data[1]))
    else:
        errorlog.write("%s n" %   binascii.hexlify((data[0][1][2].load)[-2:]))
    rst = TCP(sport=sport, dport=dport,   flags='R', seq=data[2].ack)
    send(ip / rst)
```

我是通过上面的代码来处理的，发送Fuzz数据之后，判断返回的数据，并分别记录在不同的日志当中，判断数据的方法还是通过Scapy返回的数据格式，以元组的方式取值判断。

为什么要在记录日志之后发送一个RST数据包？

```
rst   = TCP(sport=sport, dport=dport, flags='R', seq=data[2].ack)
```

在Fuzz数据发送之后，我无法判断发送的数据是否生效，所以自己用了最笨的办法，发送一个RST数据报，重置断开连接。下面的流程展示了整个脚本的运行过程和实现流程。

[![](https://p0.ssl.qhimg.com/t01f20b0d2ee78802df.png)](https://p0.ssl.qhimg.com/t01f20b0d2ee78802df.png)

到此为止，可以自己将这个小脚本完成出来了，具体的小问题在自己写的过程中具体解决。

 

**0x04 几个问题**

****

 异常处理

异常的情况可能比较多，先罗列一种情况，当然异常情况不仅仅包含连接过程中，还可能是在交互过程中，数据报格式不正确，返回数据不正确等等问题。

**1)    设备不在线，三次握手会抛出异常，对异常进行处理**

**2)    设备在线，但S7建立连接出现错误不能连接(如: ip冲突引发的异常)**

所以异常要怎么处理呢？可以通过返回数据中的flag值来判断是否为Rst。

**如何判断设备是否可达?**

有别人的小程序是通过先发送一个Ping包来确定设备是否可达，但是Ping不通不一定是确定设备不可连接的唯一方式，自己选择直接发送S7握手包，如果返回异常，那么设备应该是不可达的。当然，也有可能是默认的102端口号被改掉了，所以最好能先扫描一下，然后针对端口多次尝试也是一个不错的方式?

 **发送Fuzz数据后如何判断设备是否异常?**

因为自己当时是在测试环境，所以需要判断当前设备是否发生了异常状况，所以在一个流程走完之后执行“ping 10.0.0.1 –c 4”,通过能否Ping通设备判断是否异常。

**如何提高效率，多线程还是多进程(自己编程渣的很)?**

这个问题暂时没有想的太明白。希望自己学到了然后就通了。

**是否需要一个单独的脚本一直监听并处理记录异常?**

这个自己考虑之后觉得可能没有必要在单独的开一个脚本去监听记录信息，因为通过Scapy已经可以将返回的数据进行判断处理，所以把上面的问题解决，在一定程度上已经可以很大的优化了这个Low的小脚本。

 

**0x05 可能有用**

****

```
Nmap S7-info Script: https://nmap.org/nsedoc/scripts/s7-info.html
```

这个是Nmap采集S7设备信息的脚本，挺好，看源码可以获取很多有用的信息，比如你可能没有握手的数据报文等等。其他的工具plcscan、S7client等工具别人都已经介绍过好多，可以自行找到很多。

OK，暂且告一段落，有错误欢迎指正。我是个菜鸡，路过的各路大神多多照顾包含。

**传送门：**[http://bobao.360.cn/learning/detail/4120.html](http://bobao.360.cn/learning/detail/4120.html) 
