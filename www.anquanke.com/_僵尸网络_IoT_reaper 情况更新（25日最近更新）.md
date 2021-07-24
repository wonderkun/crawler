> 原文链接: https://www.anquanke.com//post/id/87083 


# 【僵尸网络】IoT_reaper 情况更新（25日最近更新）


                                阅读量   
                                **96281**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01ee3213dd2622e1dd.png)](https://p3.ssl.qhimg.com/t01ee3213dd2622e1dd.png)

**传送门**

****

[**【僵尸网络】IoT_reaper : 一个正在快速扩张的新 IoT僵尸网络**](http://bobao.360.cn/learning/detail/4582.html)



**前言**

****

在周五晚上披露了**IoT_reaper**之后，我们收到了来自安全社区和各方很多问题。这里给出一个快速的更新，以澄清各方可能的疑问。



**IoT_reaper样本投递历史情况**

****

我们通过蜜罐观察到的 **IoT_reaper **样本历史投递情况如下：

[![](https://p2.ssl.qhimg.com/t01653d88ec1d14f9c7.png)](https://p2.ssl.qhimg.com/t01653d88ec1d14f9c7.png)

可以看出，IoT_reaper 最主要传播的恶意代码位于下面这个URL上：

下载地址：**hxxp://162.211.183.192/sa**

投递者：119.82.26.157

起止时间：10-04～10-17

样本md5：7 个,详细见文末IoC

这个URL上的样本之间内聚关系比较强，我们称为S簇。

后来进一步的分析，认为S簇还包括其他一些样本；而在S簇之外，还有一个LUA簇，以及其他更小一些的未知簇。



**S簇的样本构成**

****

我们认为S簇包含下面这些URL上的样本：

hxxp://162.211.183.192/sa

hxxp://162.211.183.192/sa5

hxxp://162.211.183.192/sm

hxxp://162.211.183.192/sml

簇内的命名策略可能是这样的，头部的s代表S簇：

sa: arm

sa5：arm5

sm：mips

sml：mips 小端

S簇的C2 布局、感染机制和数字疑问

[![](https://p5.ssl.qhimg.com/t01a5d7cb545ee6176c.png)](https://p5.ssl.qhimg.com/t01a5d7cb545ee6176c.png)

如上图：

**loader **: 负责通过漏洞植入恶意代码

**downloader **: 提供恶意代码下载

**reporter **: 接收bot扫描到的易感染设备信息

**controller **: 控制bot、发送控制指令

我们猜测，在reporter 和 loader 之间有一个队列，reporter会将收集到的易感染设备信息推入队列，等待loader处理

与 S 簇感染相关的有一组不同的数字，近日来容易引起安全社区的混淆。我们看到的数字如下：

**已经汇报到单台 reporter 的易感染设备数：超过2m，到 2017-10-18 为止；**

**单台 controller 累积控制设备数：超过28k，到 2017-10-24 为止；**

这两个数字之间有 显著差距，原因尚不明确。这可能是因为攻击者的实现导致在队列中加入了大量的不存在相应漏洞的设备, 或者是攻击者的 loader 处理能力不足而被动积压，也有可能是攻击者主动抑制了感染速度以减少暴露风险，或者是因为其他我们不得而知的原因。



**S 簇单台 C2 感染情况统计（2017-10-13 ～ 2017-10-23）**

****

时间分布：

[![](https://p5.ssl.qhimg.com/t01fdef6765ecd3063a.png)](https://p5.ssl.qhimg.com/t01fdef6765ecd3063a.png)

国家分布:

[![](https://p4.ssl.qhimg.com/t01d568da8bfd7bf9fc.png)](https://p4.ssl.qhimg.com/t01d568da8bfd7bf9fc.png)

被感染的前十国家:

[![](https://p3.ssl.qhimg.com/t01bfdf5b249b5bd622.png)](https://p3.ssl.qhimg.com/t01bfdf5b249b5bd622.png)

与 mirai 初期感染情况对比

[![](https://p1.ssl.qhimg.com/t01c1d43ba211928b55.png)](https://p1.ssl.qhimg.com/t01c1d43ba211928b55.png)

<br>

**S簇的近期样本变化情况**

****

我们会监控视野范围内样本变化情况。在10月23日，我们检测到S簇的如下URL内容发生变化：

**hxxp://162.211.183.192/sa**

变化情况如下表所示：

[![](https://p4.ssl.qhimg.com/t0144eb0a150b427b77.png)](https://p4.ssl.qhimg.com/t0144eb0a150b427b77.png)

在原始报告的“样本的投入、C2 的布局和流量变化”一节已经提及：这是一个恶意代码样本，被控制者放置在downloader服务器上，被loader服务器投递，投递成功后会向controller报告心跳，启动扫描并将扫描到的易感染设备信息报告给reporter。

我们仔细观察更新后的样本发现：

新集成了一个**新的漏洞利用** :[http://roberto.greyhats.it/advisories/20130227-dlink-dir.txt](http://roberto.greyhats.it/advisories/20130227-dlink-dir.txt) 

心跳会指向 **e.hl852.com/e.hl859.com**

样本中内置了**9个硬编码的IP地址**，扫描时，扫描目标地址会包含；

上述9个IP地址上有共计 34个端口会被频繁扫描：其中**17个端口是硬编码的**，样本会随机扫描其中的部分；**另外17个端口**虽然会被频繁扫描，但是并未被直接硬编码到样本中。我们推测样本中隐藏了某段逻辑来扫描后面17个端口。

这第十个漏洞利用在样本中的调用过程：

[![](https://p3.ssl.qhimg.com/t016f5016223da6fcd2.png)](https://p3.ssl.qhimg.com/t016f5016223da6fcd2.png)

上述9个硬编码的IP地址是：

217.155.58.226  

85.229.43.75  

213.185.228.42  

218.186.0.186  

103.56.233.78  

103.245.77.113  

116.58.254.40  

201.242.171.137  

36.85.177.3  

对应的，我们可以观察到大网上这9个IP地址的流量在上述时间点以后开始增加：

[![](https://p5.ssl.qhimg.com/t018d5cc1d2e7bc1bca.png)](https://p5.ssl.qhimg.com/t018d5cc1d2e7bc1bca.png)

34 个硬编码、没有硬编码但是会被扫描的端口号：

[![](https://p3.ssl.qhimg.com/t0167a1b5302155f3f9.png)](https://p3.ssl.qhimg.com/t0167a1b5302155f3f9.png)

<br>

**S 簇的 C2 DNS流量变化**

****

S 簇先后使用了下面一组C2，对应的 DNS 流量图见后

**e.hi8520.com**：对应图中最上方蓝色曲线；

**e.hl852.com**：对应图中中间绿色曲线；

**e.ha859.com**：对应途中底部黄色曲线；



**IoC **

****

hxxp://162.211.183.192/sa 41ef6a5c5b2fde1b367685c7b8b3c154 

hxxp://162.211.183.192/sa f9ec2427377cbc6afb4a7ff011e0de77 

hxxp://162.211.183.192/sa 76be3db77c7eb56825fe60009de2a8f2 

hxxp://162.211.183.192/sa5 95b448bdf6b6c97a33e1d1dbe41678eb 

hxxp://162.211.183.192/sa e9a03dbde09c6b0a83eefc9c295711d7 

hxxp://162.211.183.192/sa 3d680273377b67e6491051abe17759db 

hxxp://162.211.183.192/sa 726d0626f66d5cacfeff36ed954dad70

<br>



**传送门**

****

**[【僵尸网络】IoT_reaper : 一个正在快速扩张的新 IoT僵尸网络](http://bobao.360.cn/learning/detail/4582.html)**
