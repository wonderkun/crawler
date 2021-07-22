> 原文链接: https://www.anquanke.com//post/id/231884 


# 浅析UMAS协议


                                阅读量   
                                **99167**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0177b5f4003a25eec6.png)](https://p2.ssl.qhimg.com/t0177b5f4003a25eec6.png)



作者：Nonattack

## 1、概述

UMAS (Unified Messaging Application Services) 统一消息传递应用程序服务，它是用于交换应用程序数据的平台独立协议，通信数据使用标准的Modbus协议。Modbus是Modicon公司在1979年开发的基于消息结构的协议，最早是为Modicon公司的PLC中使用，后为施耐德电气公司所有。Modbus协议是现今使用的最早和应用最广泛的工业控制系统协议之一，主要是用于和现场控制器通信的应用层协议，共有三种工作模式：Modbus/ASCII，Modbus/RTU，和Modbus/TCP。

Modbus协议标准是公开的，其众多功能码早已广为人知，在此不做赘述。但其标准文档中也提到了一些未公开、且为占用状态的功能码，90功能码（0x5A）即为其中一个，UMAS协议即为90功能码的Modbus。

[![](https://p4.ssl.qhimg.com/t01c7beafbb66e0cbba.png)](https://p4.ssl.qhimg.com/t01c7beafbb66e0cbba.png)

 UMAS协议为施耐德电气私有的、用于对其PLC产品进行配置和监控等操作，通过查阅，发现未有相关详细描述文档，因此，本文的主要目的即是对UMAS进行基本研究和归纳，不当之处望指正。UMAS协议的基本结构如下图所示：

[![](https://p0.ssl.qhimg.com/t01eaeecc46863c85db.png)](https://p0.ssl.qhimg.com/t01eaeecc46863c85db.png)

## 2、UMAS协议功能码

UMAS协议即为0x5A功能码的Modbus协议，其通信数据在Wireshark中的识别情况如下图：

[![](https://p1.ssl.qhimg.com/t0115af2e3c28f14052.png)](https://p1.ssl.qhimg.com/t0115af2e3c28f14052.png)

功能码全部显示为Unity(Schneider)(90)，那么，UMAS有功能码吗？进一步观察Data部分，在Wireshark中其隶属于Modbus部分且未能被详细解析，而恰好此部分即为UMAS所特有的，本节内容所讨论的UMAS功能码并非Modbus协议中的功能码，而是指UMAS特有部分中的功能码，其与PLC的各种配置，包括：PLC读、写、运行/停止、数据上传/下载等操作密切相关。

UMAS协议功能码的梳理与总结，源于对相关DLL文件的分析和对与PLC通信数据分析总结而来，测试中使用了Schneider M340 PLC，在没有PLC的情况下，可使用上位机软件Unity Pro XL(后来软件更名为EcoStruxure Control Expert)自带的仿真器代替PLC进行通信。

安装Unity Pro软件后，通过对特定DLL文件进行分析，可以发现逆向源码中即对协议的名称描述即为UMAS，相关的对PLC特定操作亦可以快速定位到：

[![](https://p5.ssl.qhimg.com/t01e14d0ae5940e18e9.png)](https://p5.ssl.qhimg.com/t01e14d0ae5940e18e9.png)

[![](https://p1.ssl.qhimg.com/t018acd713a0fa47a2b.png)](https://p1.ssl.qhimg.com/t018acd713a0fa47a2b.png)

[![](https://p4.ssl.qhimg.com/t01568828a918d9d423.png)](https://p4.ssl.qhimg.com/t01568828a918d9d423.png)

结合代码分析和通信数据，UMAS相关功能码和基本含义总结如下：
<td colspan="4" valign="bottom" nowrap width="614">UMAS功能码</td>
<td valign="bottom" nowrap width="47">序号</td><td valign="bottom" nowrap width="66">功能码</td><td colspan="2" valign="bottom" nowrap width="501">含义</td>

功能码
<td valign="bottom" nowrap width="47">1</td><td valign="bottom" nowrap width="66">0x01</td><td valign="bottom" nowrap width="236">INIT_COMM</td><td valign="bottom" nowrap width="265">建立UMAS通信</td>

0x01

建立UMAS通信
<td valign="bottom" nowrap width="47">2</td><td valign="bottom" nowrap width="66">0x02</td><td valign="bottom" nowrap width="236">READ_ID</td><td valign="bottom" nowrap width="265">请求PLC ID</td>

0x02

请求PLC ID
<td valign="bottom" nowrap width="47">3</td><td valign="bottom" nowrap width="66">0x03</td><td valign="bottom" nowrap width="236">READ_PROJECT_INFO</td><td valign="bottom" nowrap width="265">读取PLC中工程信息</td>

0x03

读取PLC中工程信息
<td valign="bottom" nowrap width="47">4</td><td valign="bottom" nowrap width="66">0x04</td><td valign="bottom" nowrap width="236">READ_PLC_INFO</td><td valign="bottom" nowrap width="265">读取PLC内部信息</td>

0x04

读取PLC内部信息
<td valign="bottom" nowrap width="47">5</td><td valign="bottom" nowrap width="66">0x06</td><td valign="bottom" nowrap width="236">READ_CARD_INFO</td><td valign="bottom" nowrap width="265">读取PLC SD卡信息</td>

0x06

读取PLC SD卡信息
<td valign="bottom" nowrap width="47">6</td><td valign="bottom" nowrap width="66">0x0A</td><td valign="bottom" nowrap width="236">REPEAT</td><td valign="bottom" nowrap width="265">回传发送给PLC的数据</td>

0x0A

回传发送给PLC的数据
<td valign="bottom" nowrap width="47">7</td><td valign="bottom" nowrap width="66">0x10</td><td valign="bottom" nowrap width="236">TAKE_PLC_RESERVATION</td><td valign="bottom" nowrap width="265">独占PLC</td>

0x10

独占PLC
<td valign="bottom" nowrap width="47">8</td><td valign="bottom" nowrap width="66">0x11</td><td valign="bottom" nowrap width="236">RELEASE_PLC_RESERVATION</td><td valign="bottom" nowrap width="265">释放PLC</td>

0x11

释放PLC
<td valign="bottom" nowrap width="47">9</td><td valign="bottom" nowrap width="66">0x12</td><td valign="bottom" nowrap width="236">KEEP_ALIVE</td><td valign="bottom" nowrap width="265">保持连接</td>

0x12

保持连接
<td valign="bottom" nowrap width="47">10</td><td valign="bottom" nowrap width="66">0x20</td><td valign="bottom" nowrap width="236">READ_MEMORY_BLOCK</td><td valign="bottom" nowrap width="265">准备读取PLC内存块</td>

0x20

准备读取PLC内存块
<td valign="bottom" nowrap width="47">11</td><td valign="bottom" nowrap width="66">0x22</td><td valign="bottom" nowrap width="236">READ_VARIABLES</td><td valign="bottom" nowrap width="265">以bit/word方式读系统变量</td>

0x22

以bit/word方式读系统变量
<td valign="bottom" nowrap width="47">12</td><td valign="bottom" nowrap width="66">0x23</td><td valign="bottom" nowrap width="236">WRITE_VARIABLES</td><td valign="bottom" nowrap width="265">以bit/word方式写系统变量</td>

0x23

以bit/word方式写系统变量
<td valign="bottom" nowrap width="47">13</td><td valign="bottom" nowrap width="66">0x24</td><td valign="bottom" nowrap width="236">READ_COILS_REGISTERS</td><td valign="bottom" nowrap width="265">读PLC的线圈/寄存器值</td>

0x24

读PLC的线圈/寄存器值
<td valign="bottom" nowrap width="47">14</td><td valign="bottom" nowrap width="66">0x25</td><td valign="bottom" nowrap width="236">WRITE_COILS_REGISTERS</td><td valign="bottom" nowrap width="265">写PLC的线圈/寄存器值</td>

0x25

写PLC的线圈/寄存器值
<td valign="bottom" nowrap width="47">15</td><td valign="bottom" nowrap width="66">0x26</td><td valign="bottom" nowrap width="236">ENABLE/DISABLE DATA DICTIONARY</td><td valign="bottom" nowrap width="265">启用/关闭数据字典功能</td>

0x26

启用/关闭数据字典功能
<td valign="bottom" nowrap width="47">16</td><td valign="bottom" nowrap width="66">0x30</td><td valign="bottom" nowrap width="236">INITIALIZE_UPLOAD</td><td valign="bottom" nowrap width="265">初始化数据上传（From PLC）</td>

0x30

初始化数据上传（From PLC）
<td valign="bottom" nowrap width="47">17</td><td valign="bottom" nowrap width="66">0x31</td><td valign="bottom" nowrap width="236">UPLOAD_BLOCK</td><td valign="bottom" nowrap width="265">上传PLC数据</td>

0x31

上传PLC数据
<td valign="bottom" nowrap width="47">18</td><td valign="bottom" nowrap width="66">0x32</td><td valign="bottom" nowrap width="236">END_STRATEGY_UPLOAD</td><td valign="bottom" nowrap width="265">完成数据上传</td>

0x32

完成数据上传
<td valign="bottom" nowrap width="47">19</td><td valign="bottom" nowrap width="66">0x33</td><td valign="bottom" nowrap width="236">INITIALIZE_DOWNLOAD</td><td valign="bottom" nowrap width="265">初始化数据下装（To PLC）</td>

0x33

初始化数据下装（To PLC）
<td valign="bottom" nowrap width="47">20</td><td valign="bottom" nowrap width="66">0x34</td><td valign="bottom" nowrap width="236">DOWNLOAD_BLOCK</td><td valign="bottom" nowrap width="265">下载数据到PLC</td>

0x34

下载数据到PLC
<td valign="bottom" nowrap width="47">21</td><td valign="bottom" nowrap width="66">0x35</td><td valign="bottom" nowrap width="236">END_DOWNLOAD</td><td valign="bottom" nowrap width="265">完成数据下载</td>

0x35

完成数据下载
<td valign="bottom" nowrap width="47">22</td><td valign="bottom" nowrap width="66">0x36</td><td valign="bottom" nowrap width="236">CREATE/RESTORE/REMOVE BACKUP</td><td valign="bottom" nowrap width="265">创建/恢复/删除内存卡中的数据备份</td>

0x36

创建/恢复/删除内存卡中的数据备份
<td valign="bottom" nowrap width="47">23</td><td valign="bottom" nowrap width="66">0x39</td><td valign="bottom" nowrap width="236">READ_ETH_MASTER_DATA</td><td valign="bottom" nowrap width="265">Read Ethernet Master Data</td>

0x39

Read Ethernet Master Data
<td valign="bottom" nowrap width="47">24</td><td valign="bottom" nowrap width="66">0x40</td><td valign="bottom" nowrap width="236">START_PLC</td><td valign="bottom" nowrap width="265">运行PLC</td>

0x40

运行PLC
<td valign="bottom" nowrap width="47">25</td><td valign="bottom" nowrap width="66">0x41</td><td valign="bottom" nowrap width="236">STOP_PLC</td><td valign="bottom" nowrap width="265">停止PLC</td>

0x41

停止PLC
<td valign="bottom" nowrap width="47">26</td><td valign="bottom" nowrap width="66">0x50</td><td valign="bottom" nowrap width="236">MONITOR_PLC</td><td valign="bottom" nowrap width="265">监视PLC变量</td>

0x50

监视PLC变量
<td valign="bottom" nowrap width="47">27</td><td valign="bottom" nowrap width="66">0x58</td><td valign="bottom" nowrap width="236">CHECK_PLC</td><td valign="bottom" nowrap width="265">检查PLC连接状态</td>

0x58

检查PLC连接状态
<td valign="bottom" nowrap width="47">28</td><td valign="bottom" nowrap width="66">0x70</td><td valign="bottom" nowrap width="236">READ_IO_OBJECT</td><td valign="bottom" nowrap width="265">读IO目标</td>

0x70

读IO目标
<td valign="bottom" nowrap width="47">29</td><td valign="bottom" nowrap width="66">0x71</td><td valign="bottom" nowrap width="236">WRITE_IO_OBJECT</td><td valign="bottom" nowrap width="265">写IO目标</td>

0x71

写IO目标
<td valign="bottom" nowrap width="47">30</td><td valign="bottom" nowrap width="66">0x73</td><td valign="bottom" nowrap width="236">GET_STATUS_MODULE</td><td valign="bottom" nowrap width="265">获取状态模块</td>

0x73

获取状态模块



## 3、UMAS协议数据分析

使用Unity Pro连接M340 PLC进行一些列操作，抓取通信过程数据，可对功能码进行对照分析。对于UMAS协议，有一点需要明确的是它是一种应/答式的通信协议：包含某种功能码的数据发送到PLC，PLC对请求解析后按照固定格式回应数据。UMAS的请求与响应数据基本格式如下所示：

请求：

[ TCP Packet ] – [ Modbus Header ] – [5A] – [ UMAS CODE (16 bit) ] [ UMAS PAYLOAD (Variable) ]

响应：

[ TCP Packet ] – [ Modbus Header ] – [5A] – [ RETURN CODE (16 bit) ] [ UMAS PAYLOAD (Variable) ]

[RETURN CODE]即为状态码部分，存在两种可能性：0x01 0xFE–意味着OK；

0x01 0xFD–意味着Error。

功能码0x01：建立通信，抓取的实际建立通信的数据将为：

[![](https://p2.ssl.qhimg.com/t0134d207ed893344f9.png)](https://p2.ssl.qhimg.com/t0134d207ed893344f9.png)

响应数据包为：

[![](https://p4.ssl.qhimg.com/t0126487b27f4d0741d.jpg)](https://p4.ssl.qhimg.com/t0126487b27f4d0741d.jpg)

功能码0x03：读取PLC中工程信息，抓取的实际建立通信的数据将为：

[![](https://p3.ssl.qhimg.com/t01df708580b0709d0a.png)](https://p3.ssl.qhimg.com/t01df708580b0709d0a.png)

响应数据包为：

[![](https://p3.ssl.qhimg.com/t0104cf94a601d2eac3.jpg)](https://p3.ssl.qhimg.com/t0104cf94a601d2eac3.jpg)

响应数据包的基本格式为：

[ TCP Packet ] – [ Modbus Header ] – [5A] – [ Response Code (16) ] –  [ Unknown (9 bytes) ] –  [ Unknown 2 (9 bytes) ] – 

[ Modification date (8 bytes) ] – [ Modification date Rep (8 bytes) ] – [ Project Version (16) ] – [ Unknown (16) ] – 

[ Project Name length (8) – [ Project name (variable) ] 

状态码之后连续两个9字节数据意义不明确，df 07按照小端数据换算过来即为2015，即工程修改时间为2015年；工程版本为0.0.01

功能码0x40/0x41：启动/停止PLC

启动PLC的请求数据为：

[![](https://p5.ssl.qhimg.com/t01080f32e9345a77ff.png)](https://p5.ssl.qhimg.com/t01080f32e9345a77ff.png)

UMAS CODE部分为00 40，不同情况下使用01 40亦可以启动PLC运行（与PLC固件版本相关）。

[![](https://p4.ssl.qhimg.com/t012a214d74bdbf4caf.png)](https://p4.ssl.qhimg.com/t012a214d74bdbf4caf.png)

相应的停止PLC的UMAS CODE部分为00 41或01 41均可。尝试对Schneider M340 PLC发送启/停数据包，验证数据格式及功能的可行性，如下所示:PLC被停止后，其run灯变为闪烁状态（并非熄灭）：

<video style="width: 100%; height: auto;" src="https://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke1/bTM0MC5tcDQ=" controls="controls" width="300" height="150">﻿您的浏览器不支持video标签 </video>



结合对UMAS功能码的理解，尝试编写数据解析插件并对数据包解析，可得到如下效果：

请求数据包：

[![](https://p0.ssl.qhimg.com/t01db9c6bd0f86753c2.png)](https://p0.ssl.qhimg.com/t01db9c6bd0f86753c2.png)

回复数据包：

[![](https://p0.ssl.qhimg.com/t014f20be824f0ff1ae.png)](https://p0.ssl.qhimg.com/t014f20be824f0ff1ae.png)

## 4、总结

本文基于对施耐德组态软件Unity Pro的关键DLL分析和对上位机与PLC通信数据分析，梳理总结了UMAS协议基本功能码，同时尝试编写Wireshark解析插件以方便数据包分析，验证了插件的可用性和数据的正确性。



## 参考资料：

[1] https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf 

[2] [https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/vulnerabilities-in-schneider-electric-somachine-and-m221-plc/](https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/vulnerabilities-in-schneider-electric-somachine-and-m221-plc/) 

[3] [https://www.lshack.cn/827/](https://www.lshack.cn/827/)

[4] https://www.cnblogs.com/zzqcn/p/4840589.html
