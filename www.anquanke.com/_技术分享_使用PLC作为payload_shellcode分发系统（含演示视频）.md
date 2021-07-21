> 原文链接: https://www.anquanke.com//post/id/85159 


# 【技术分享】使用PLC作为payload/shellcode分发系统（含演示视频）


                                阅读量   
                                **78485**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：shelliscoming.com
                                <br>原文地址：[http://www.shelliscoming.com/2016/12/modbus-stager-using-plcs-as.html](http://www.shelliscoming.com/2016/12/modbus-stager-using-plcs-as.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t0199116b4121d1f04e.jpg)](https://p5.ssl.qhimg.com/t0199116b4121d1f04e.jpg)**

**翻译：**[**shan66 ******](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：180RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

这个周末，我一直在鼓捣Modbus，并利用汇编语言开发了一个[stager](https://github.com/BorjaMerino/PlcInjector/blob/master/stager/block_recv_modbus.asm)，它可以从PLC的保持寄存器中下载payload。由于有大量的PLC都暴露在互联网上，我情不自禁地想到，是否可以利用它们提供的处理能力和内存来存储某些payload，以便以后（从stager）下载它们。

所以，我们不妨考虑下面的场景： 

1.	攻击者从互联网上寻找一个具有足够的空间来存储payload的PLC。实际上，带有几十KB内存的Modbus设备是很容易找到的。

2.	攻击者将payload上传到PLC的内存。

3.	攻击者用dropper感染一个主机，然后利用stager与Modbus进行“交流”，从PLC中下载并执行该stage。

[![](https://p3.ssl.qhimg.com/t01a90da32c459e1010.png)](https://p3.ssl.qhimg.com/t01a90da32c459e1010.png)

<br>

**采用PLC保持寄存器存储Payload的优点**

由于使用了第三方PLC，所以具有很好的匿名性，跟踪的难度非常大。无需将payload上传到服务器。

由于payload存放在PLC的内存中，所以加大了取证分析的难度。此外，一旦payload被取出，其内容可以被容易地覆盖（甚至stager自身就能做到这一点）。

此外，我认为Modbus Stager在某些ICS环境中也是非常有用的，因为这些环境下Modbus之外的协议会引起人们的警觉，并且[WinHTTP / WinInet](https://github.com/rapid7/metasploit-framework/wiki/The-ins-and-outs-of-HTTP-and-HTTPS-communications-in-Meterpreter-and-Metasploit-Stagers) stager也不是最适用的。所以，在这种情况下，你只需要一个Modbus处理程序或者只是使用一个仿真器，在stager连接它时，由其提供stage即可。此外我们还发现，许多网络上都有可以远程管理的Modbus设备，所以它们也是这种stager的用武之地。

重要说明：请不要对任何第三方PLC执行这些操作。PLC寄存器上的任何写操作都可能毁坏原来的过程控制策略。

<br>

**活跃在互联网上采用Modbus协议的PLC数量**

为了弄清楚暴露在互联网中、使用Modbus协议的PLC的数量，我使用[Censys API](https://censys.io/)写了一个[小脚本](https://github.com/BorjaMerino/PlcInjector/blob/master/plcModbusDownload.py)。如果你的网卡性能不错的话，你可以利用[masscan](https://github.com/robertdavidgraham/masscan)或[Zmap](https://github.com/zmap/zmap)等工具来扫描互联网，寻找在502端口上运行Modbus协议的设备。

从以下输出可以看出，至少有5500个PLC可供利用。

[![](https://p2.ssl.qhimg.com/t01a9d8a16ccf5f07b9.png)](https://p2.ssl.qhimg.com/t01a9d8a16ccf5f07b9.png)

在这些IP中，许多只是些蜜罐，[这很容易看出来](https://www.youtube.com/watch?v=HiZdkBAFp7Q)；例如，Conpot以及托管在云服务中的其他服务。就本文来说，即使蜜罐也无所谓，只要它们的内存足够大就行了。

<br>

**如何将Payload上传至PLC保持寄存器**

好了，为了将payload上传到PLC中，我编写了一个名为[plcInjectPayload.py](https://github.com/BorjaMerino/PlcInjector/blob/master/plcInjectPayload.py)的python脚本。根据加载的控制策略的不同，对PLC可用内存大小的要求也有所变化，因此该脚本首先检查它们是否有足够的内存空间来存放相应的payload。为了检测内存的大小，可以发送操作ID为03（读取保持寄存器）的Modbus请求，尝试从某个地址读取特定记录（每个记录长度为16比特）。如果收到一个0x83异常，那么说明这个PLC对于我们来说是无法使用的。

要上传payload，请使用-upload选项，具体如下所示。该选项允许使用参数-addr规定起始地址，也就是说，从这个保持寄存器编号（如果未指定，则为地址0）开始加载payload。

[![](https://p2.ssl.qhimg.com/t0183484e84a1f2e04b.png)](https://p2.ssl.qhimg.com/t0183484e84a1f2e04b.png)

如果payload的字节数为奇数，就需要用“0x90”来进行填充，以避免在读取时出现一些问题。在前面的示例中，大小为1536字节; 为了检查加载操作是否成功，我们可以利用选项-download从地址0处下载同样数量的字节。



[![](https://p1.ssl.qhimg.com/t01dab75e28833d7f73.png)](https://p1.ssl.qhimg.com/t01dab75e28833d7f73.png)

很明显，该脚本不仅可以上传payload，实际上还可以上传任何类型的文件。所以，我们觉得这是一个泄露和共享信息的有趣方法。设想一下，有谁会怀疑某个公共PLC的保存寄存器会存有.docx或.zip文件呢？ 

需要格外注意的是，存放payload的记录可能会被PLC所改变。由于我们不清楚PLC I / O及其过程控制策略，所以需要寻找一个通常不会被修改到的内存范围。为此，我们可以将payload加载到某个范围，然后在一段时间内，payload经多次检查未发现任何变化的话，这就是我们要找的内存区域。为了达到这个目的，我们可以借助于plcInjectPayload.py以及另外几个bash指令即可。

<br>

**在受控主机中读取PLC中存储的Payload**

payload上传到PLC之后，还必须从受害者的计算机中读取它。为此，我建立了一个基于Modbus协议的stager;它的大小还不到500字节（我会设法让它变得更小）。其中，它的reverse_tcp和block_api代码取自Metasploit（[https://github.com/rapid7/metasploit-framework/tree/master/external/source/shellcode/windows/x86/src/block](https://github.com/rapid7/metasploit-framework/tree/master/external/source/shellcode/windows/x86/src/block)）。下图展示的是[block_recv_modbus.asm](https://github.com/BorjaMerino/PlcInjector/blob/master/stager/block_recv_modbus.asm)的asm代码，它的一部分职责是通过Modbus协议获取payload。因此，这段代码需要通过Modbus协议与PLC通信，以下相应的payload。这里的代码会利用前4个字节来了解该stage大小，并通过VirtualAlloc分配必要的内存。然后，通过不断发送“read holding”请求（功能代码03）来获取payload。根据协议规定，对于每个读请求，PLC最多可以返回250个字节（125个保持寄存器），因此，stager可以以它为单位，逐步下载payload。

[![](https://p1.ssl.qhimg.com/t01f810f0c475cd0d0a.png)](https://p1.ssl.qhimg.com/t01f810f0c475cd0d0a.png)

<br>

**实例解析**

下面我们来看一个实际的例子。最近，我在[www.exploit-db.com](http://www.exploit-db.com)网站上发现一个[用于Windows系统的键盘记录shellcode](https://www.exploit-db.com/exploits/39794/)，大小只有600字节；虽然它的尺寸很小，但是对于一个只有几个MODBUS请求（记住，每个请求的最大字节数为250字节）的POC来说已经足够了。shellcode在执行后，会把按键敲击动作写入到用户的％TEMP％目录下的“log.bin”文件中。

因此，我们首先把该payload放到一个二进制文件中，并在它的前面放上其长度，这里是以小端字节表示的长度（4字节）。

[![](https://p2.ssl.qhimg.com/t01b7ef605a377a31c1.png)](https://p2.ssl.qhimg.com/t01b7ef605a377a31c1.png)

现在，让我们从地址0开始将其上传到PLC： 

[![](https://p3.ssl.qhimg.com/t0128beda58cac85ce8.png)](https://p3.ssl.qhimg.com/t0128beda58cac85ce8.png)

这个stager一旦运行，就会通过3个请求下载该payload：250 + 250 + 102 = 602字节。下图详细描述了Modbus通信过程。

[![](https://p4.ssl.qhimg.com/t018a9a821fbedc64d3.png)](https://p4.ssl.qhimg.com/t018a9a821fbedc64d3.png)

下图展示了Wireshark对上述通信过程的跟踪情况。进程监视器窗口表明，该stage在成功运行（检查log.bin文件就能看到保存的击键）

[![](https://p1.ssl.qhimg.com/t015062087edcd0a3c6.png)](https://p1.ssl.qhimg.com/t015062087edcd0a3c6.png)

我已经通过[Modbus仿真器](http://modbuspal.sourceforge.net/)和实际PLC对这个代码进行了验证，结果一切正常，但是如前所述，我认为该shellcode还可以进一步优化。为了进行第一个测试，我在python（[plcModbusHandler.py](https://github.com/BorjaMerino/PlcInjector/blob/master/plcModbusHandler.py)）中创建了一个Modbus处理程序，用来把该payload发送给stager。

[![](https://p1.ssl.qhimg.com/t017506686427839e41.png)](https://p1.ssl.qhimg.com/t017506686427839e41.png)

我正在设法把这个处理程序移植到Metasploit。更多详情，请观看下面的视频。

<br>

**演示视频**



****
