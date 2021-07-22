> 原文链接: https://www.anquanke.com//post/id/184263 


# 分析asyncRAT远控的数据包格式及通讯建立过程


                                阅读量   
                                **421991**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01458836017fb39b6a.jpg)](https://p3.ssl.qhimg.com/t01458836017fb39b6a.jpg)



## 前言：

asyncRat远控不仅包括通讯、守护、隐藏、自启动等常见功能模块，而且还包含加密、反沙盒、反虚拟机、反分析、反调试等对抗模块，是一款相对比较成熟的异步通讯开源木马。本文主要目的是发现asyncRat木马的通讯建立过程及数据包格式。

被控端运行后，当被控端数据 穿透被控主机防护后，控制端将接收到被控端主机的IP地址、国家、ID、用户名、操作系统、net版本、权限、杀毒软件、系统性能等基本信息。

控制端效果图如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01792d6f444e5b9213.png)

当前木马控制端与被控端的连接几乎都是采用反向连接的方式，也就是被控端主动发送数据联系控制端。所以分析木马的通讯应该先从被控端开始。



## 一、被控端

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d5756f25ebd3a4ef.png)

分析先从木马建立连接后，被控端主动发送的基本信息数据开始，然后分析基本信息数据被嵌入了哪些数据（这些数据可能标识数据长度、数据类型等），最后分析被控端与控制端之间通讯建立过程。

1、从入口函数开始，找到发送函数位置

1.1 入口主函数

[![](https://p3.ssl.qhimg.com/t016afba53506ae9d33.png)](https://p3.ssl.qhimg.com/t016afba53506ae9d33.png)

1.1.1  初始化函数InitializeSetting（），初始化设置函数功能：主要是获取回连IP、端口、SSL通讯证书、解密秘钥、证书签名等基本信息，并对证书进行验证

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0174ccfcb22c4f2c5e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013535dd389f395185.png)

1.1.2   CreateMutex()函数:保证进程的唯一的

[![](https://p0.ssl.qhimg.com/t012f5d967405cde720.png)](https://p0.ssl.qhimg.com/t012f5d967405cde720.png)

1.1.3 RunAntiAnalysis()函数:对抗杀软、反沙盒、反虚拟机和逆向软件等

[![](https://p4.ssl.qhimg.com/t01448c544befc714b0.png)](https://p4.ssl.qhimg.com/t01448c544befc714b0.png)

1.1.4  Install()函数:添加自启动,非管理员权限添加到注册表，否则添加到任务计划

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0188c187fe1eeb553e.png)

1.1.5 ProcessCritical()函数：进程保护

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b1196923b2d27e7c.png)

1.1.6 Reconnect()函数：重新连接

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01781d339d5c3789fe.png)

1.1.7 初始化连接函数 InitializeClient()：获取控制端IP和端口后，建立SSL协议连接

[![](https://p5.ssl.qhimg.com/t01a79f2ba7d1d0ce71.png)](https://p5.ssl.qhimg.com/t01a79f2ba7d1d0ce71.png)

1.1.8 找到发送基本数据函数位置，在InitializeClient()函数中的如下位置：发送基本信息数据包的Send(Methods.SendInfo())和发送随机数据包的Tick = new Timer(new TimerCallback(CheckServer)）都是主动向控制端发送数据包的调用语句，我们的分析就先从Send(Methods.SendInfo())语句开始

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01dcd9e1a0d93a9f87.png)

2、分析基本信息数据包

2.1 我们在Send(Methods.SendInfo())处设置断点，逐过程执行找到发送的401个字节的数据包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012bb770206910cdc0.png)

2.2  试着将这些值换算成ascii码，部分如下

[![](https://p3.ssl.qhimg.com/t0144841b8ae61a4376.png)](https://p3.ssl.qhimg.com/t0144841b8ae61a4376.png)

但有一些特殊数值无法成功换算，共计24个，后面数据包格式的分析也就是分析这24个特殊数值，找到它们所代表的意义

[![](https://p0.ssl.qhimg.com/t017dd2697589a4337f.png)](https://p0.ssl.qhimg.com/t017dd2697589a4337f.png)

2.3 进入SendInfo()函数， 这里就是需要发送的基本信息数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ea030a66cedc2e7e.png)

3 分析基本信息数据包的封装过程

3.1 进入Encode2Bytes（）函数，继续进入Encode2Stream(ms)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f789279278ebf0e4.png)

3.2 Encode2Stream(ms)中，获取包类型，并根据不同的类型而采取不同的处理方式

[![](https://p2.ssl.qhimg.com/t016d9d5577e91113e7.png)](https://p2.ssl.qhimg.com/t016d9d5577e91113e7.png)

3.3 我们返回到sendinfo()函数，并在msgpack.Encode2Bytes()位置处设置一个断点，运行后，我们获取到包类型是Map

[![](https://p3.ssl.qhimg.com/t012afe049a9a351be7.png)](https://p3.ssl.qhimg.com/t012afe049a9a351be7.png)

3.4 重新回到Encode2Stream()函数中，我们知道了valueType的值是Map,那就会执行Writemap()函数，进入Writemap()函数，发现它会根据len=children.Count值得不同，写入不同的值到输出缓存。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01476c587af49b65a2.png)

3.5 依旧在前面断点的位置，获得len=children.Count=10

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01698d61acecd1e48f.png)

3.6 根据len=10，Writemap()中执行的位置如下，写入了第一个字节 b=0x80+0x0A=0x8A=138，我们在在ms.WriteByte()处设置断点进行验证，结果证明判断正确

[![](https://p2.ssl.qhimg.com/t013157972a22a43b2f.png)](https://p2.ssl.qhimg.com/t013157972a22a43b2f.png)

3.7 第一个特殊值138分析完成，它代表了子包的数量

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017649fedb0c9e3c73.png)

10个子包分别代表如下：

第一个子包：name=”Packet”     value=”ClientInfo”<br>
第二个子包：name=”HWID”      value=”AC35DE8E98BDA0B”<br>
第三个子包：name=”User”      value=”t…l”<br>
第四个子包：name=”OS”        value=” Windows 10 家庭中文版 64bit”<br>
第五个子包：name=”Path”      value=”E:…………………Stub.exe”<br>
第六个子包：name=”Version”    value=”0.5.2″<br>
第七个子包：name=”Admin”     value=”User”<br>
第八个子包：name=”Performance” value=”CPU 0%   RAM 76%”<br>
第九个子包：name=”Pastebin”   value=”null”<br>
第十个子包：name=”Antivirus”  value=”Lenovo Anti-Virus powered by Huorong Security, Windows Defender”<br>
3.8 继续查看WriteMap()函数，在for循环中，处理了子包的name属性值和Value属性值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0183318589cfbe3204.png)

处理name属性值，因为name属性值一定是字符串类型，所以调用了WriteTools.WriteString()函数

[![](https://p2.ssl.qhimg.com/t0125454c95f1b17123.png)](https://p2.ssl.qhimg.com/t0125454c95f1b17123.png)

处理value属性值 ，根据value值的类型不同，调用不同的函数，基本信息数据里面value也是字符串类型，所以调用了WriteTools.WriteString()函数

[![](https://p0.ssl.qhimg.com/t012a9879b7dd041fbb.png)](https://p0.ssl.qhimg.com/t012a9879b7dd041fbb.png)

3.9 分析WriteString()函数

观察WriteTools.WriteString()函数代码，能得到下面几个结果：

[![](https://p0.ssl.qhimg.com/t011833c19a1ead3506.png)](https://p0.ssl.qhimg.com/t011833c19a1ead3506.png)

我们在b值发生变化的位置全部设置断点， 这里有一个注意点，最好把发送随机信息数据的这段代码注释掉，因为这段代码会每个15到30秒之间随机的发送数据包，会影响我们对基本数据信息包的分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a9aefbabcc05132b.png)

3.10  追踪b值的变化 b值就是特殊值

[![](https://p4.ssl.qhimg.com/t017bb9f24182118042.png)](https://p4.ssl.qhimg.com/t017bb9f24182118042.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ecb722cb332a2926.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f00be505b39ce1b8.png)

[![](https://p4.ssl.qhimg.com/t011c17eff947da9969.png)](https://p4.ssl.qhimg.com/t011c17eff947da9969.png)

4  基本信息数据包总结

4.1 到此为止我们24个特殊值全部分析完了，为了更清楚，我们将这401个字节写到一个表格中

[![](https://p0.ssl.qhimg.com/t01588b03a112c71e75.png)](https://p0.ssl.qhimg.com/t01588b03a112c71e75.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f7778510ebd990d1.png)

4.2  138 表示子包数量，它的赋值流程如下：

[![](https://p5.ssl.qhimg.com/t01061640744d9cb0ed.png)](https://p5.ssl.qhimg.com/t01061640744d9cb0ed.png)

4.3        217、166、170、164、175、164、165、162、33等特殊值表示字符串长度，赋值流程如下

[![](https://p2.ssl.qhimg.com/t01ba4eb1c48e239dc3.png)](https://p2.ssl.qhimg.com/t01ba4eb1c48e239dc3.png)

4.4  基本信息数据包格式如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01569dadaecf5a1425.png)

4.5 基本信息数据包中子包格式如下

[![](https://p1.ssl.qhimg.com/t01abcc47281271107f.png)](https://p1.ssl.qhimg.com/t01abcc47281271107f.png)

5  分析被控端发送数据顺序

5.1 发送函数send（）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01343988b6e3d1e4c0.png)

5.2  被控端发送数据包顺序如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c283ccf90c71fd91.png)

[![](https://p4.ssl.qhimg.com/t0163a929c7915adc6a.png)](https://p4.ssl.qhimg.com/t0163a929c7915adc6a.png)

5.3 注意

基本信息数据包长和随机信息数据包包长是不固定的，原因是涉及到 CPU和RAM使用的百分比的数据信息是不断发生变化的。



## 二、控制端

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0158894ae809c15d6d.png)

1、从入口函数开始，找到接收函数位置

1.1 入口主函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e0a2dd3fb5db0f0c.png)

1.2 控制端监听端口

[![](https://p1.ssl.qhimg.com/t0183539ed2220f0060.png)](https://p1.ssl.qhimg.com/t0183539ed2220f0060.png)

1.3  异步方式等待被控端连接

[![](https://p3.ssl.qhimg.com/t01540de30c360fab09.png)](https://p3.ssl.qhimg.com/t01540de30c360fab09.png)

1.4 创建连接对象

[![](https://p1.ssl.qhimg.com/t01991d6781d4ee28a4.png)](https://p1.ssl.qhimg.com/t01991d6781d4ee28a4.png)

2、建立SSL连接

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0101063b102b930622.png)

发现异步的接收数据函数

[![](https://p0.ssl.qhimg.com/t01a00c542fb4e4bf1f.png)](https://p0.ssl.qhimg.com/t01a00c542fb4e4bf1f.png)

3 寻找数据包处理函数

[![](https://p1.ssl.qhimg.com/t013eadfabeefcce04d.png)](https://p1.ssl.qhimg.com/t013eadfabeefcce04d.png)

Packet.Read()函数内调用DecodeFromeBytes()函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b00a06fb6027aea7.png)

4、处理接收到的数据包

4.1  处理基本信息数据包

DecodeFromStream()函数

[![](https://p1.ssl.qhimg.com/t01f8e8a60bb3592675.png)](https://p1.ssl.qhimg.com/t01f8e8a60bb3592675.png)

基本信息数据包格式如下

[![](https://p2.ssl.qhimg.com/t0136e255115154517e.png)](https://p2.ssl.qhimg.com/t0136e255115154517e.png)

4.2 获取第一个字节值138

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b9dc35fc28509955.png)

4.3 设置name数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01950d62b9534fd848.png)

4.4 设置value数据

[![](https://p0.ssl.qhimg.com/t01baee724b4ec1d8cd.png)](https://p0.ssl.qhimg.com/t01baee724b4ec1d8cd.png)

5 基本信息数据包内子包中的其它数据处理同上

6  显示基本信息数据包中数据

[![](https://p5.ssl.qhimg.com/t015350571ff2da980d.png)](https://p5.ssl.qhimg.com/t015350571ff2da980d.png)



## 三、总结

1 调试设置断点时，需要将发送随机信息数据包注释掉，因为这个包是被控端每隔15到30秒随机发出的，如果不注释掉，会影响我们对基本信息数据包的分析结果

[![](https://p4.ssl.qhimg.com/t01c0aa5462ad5b496d.png)](https://p4.ssl.qhimg.com/t01c0aa5462ad5b496d.png)

2 所有数据包的第一个子包name值都是packet，不同的数据包对应不同的value值。控制端根据value值对不同的数据包采取不同的处理方式。

[![](https://p2.ssl.qhimg.com/t01cae7bf7448ce06bb.png)](https://p2.ssl.qhimg.com/t01cae7bf7448ce06bb.png)

3  基本信息数据包的子包结构如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a8984707b20cc795.png)

4 被控端组装数据包过程如下

1）计算子包数量

[![](https://p0.ssl.qhimg.com/t01e82d90155c5f24a3.png)](https://p0.ssl.qhimg.com/t01e82d90155c5f24a3.png)

2）计算子包的数据长度

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011073a9fa05346002.png)

3）构建子包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dd06271418e02279.png)

4）组装数据包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cf26f233204528ad.png)

5 控制端拆包提取数据过程如下

[![](https://p4.ssl.qhimg.com/t01d1671510995495d2.png)](https://p4.ssl.qhimg.com/t01d1671510995495d2.png)

6 被控端与控制端通讯建立过程如下

[![](https://p3.ssl.qhimg.com/t01c2fe91fc74376125.png)](https://p3.ssl.qhimg.com/t01c2fe91fc74376125.png)
