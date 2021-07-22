> 原文链接: https://www.anquanke.com//post/id/85539 


# 【技术分享】我的MITRE物联网挑战赛之旅


                                阅读量   
                                **118596**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p5.ssl.qhimg.com/t016d7458684b08e97d.jpg)](https://p5.ssl.qhimg.com/t016d7458684b08e97d.jpg)**

****

作者：[Selfighter](http://bobao.360.cn/member/contribute?uid=1437811105)

预估稿费：500RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**前言**

前一段时间我在推特上无意中看到MITRE公司在举行一个比赛（MITRE是一家成立59年拥有7613名雇员的公司，管理着联邦资助的研究与开发中心（FFRDC），为美国国防部、国安局等重要单位提供服务）。

[![](https://p2.ssl.qhimg.com/t01046e3ad090c3d153.jpg)](https://p2.ssl.qhimg.com/t01046e3ad090c3d153.jpg)

IoT和$50k 奖金这两个关键词立即引起了我的注意，我跟着链接点进去后看到了比赛详情

官方的比赛介绍：[https://www.mitre.org/research/mitre-challenge/mitre-challenge-iot](https://www.mitre.org/research/mitre-challenge/mitre-challenge-iot)    



****

**竞赛概述**

物联网（IoT Internet of Things）设备的普及势必会改变人们的生活、工作方式。IoT设备的互通互联将带给我们极大地便利。美好的愿景往往带来巨大的挑战，物联网设备的广泛应用带来了更多的攻击面，如何保护我们的汽车、智能家居、工厂等不被攻击？从企业到军方都在寻求管理IoT设备的解决方案。

网络管理员需要清楚的知道IoT网络环境中到底存在什么设备，当攻击者对其中一个设备进行替换后，有什么方法对其进行区分。我们需要一个唯一的识别符（或者”指纹”）使得只需要管理员对网络进行被动监听就能识别物联网设备。

MITRE公司以此为主题举办了此次竞赛，在不需要对现有产品进行改造的情况下，寻求革命性的IoT设备识别方案，同时为成绩优异的参赛者提供了丰厚的奖励。

**<br>**

**背景**

从家到医院、电网、高速公路甚至是战场，物联网（IoT Internet of Things）势必会改变人们的生活方式、商业活动的进行方式、政府的工作方式等等。

IoT设备之间广泛的相互连接将带来新的效率和能力。想象一下一套智能医疗系统将病人监护设备与药物注射泵连接起来从而防止注射泵过量用药及减少监护设备的误报，或者一座智能城市智能地制定维护工作计划从而将可能造成的交通拥堵影响减少到最小。

但是伴随这些美好的前景的是巨大的挑战，由于物联网提供了如此多的可能被利用的攻击入口，我们如何才能保护我们的汽车、家、工厂等等不被攻击？从企事业单位到军队都在寻求如何来管理IoT以在他们各自的操作系统和环境下保证安全和隐私。

网络管理员需要清楚的知道网络环境中到底有什么设备，包括当攻击者用一台设替换另一台设备情况下，换句话说，我们今天看到的这个智能温控器还是昨天我们看到的那个吗？我们需要一个唯一识别符（或者”指纹”）来使得管理员只需要对网络进行被动监听就能识别物联网设备。

MITRE挑战赛——物联网设备的唯一识别，就是为了寻求应对这种潜在威胁的方案，我们的赞助方希望借此比赛在风险最小化的同时收获技术革新的成果。

我们寻求的是非传统的方法来识别IoT设备，在将来，设备厂商可能为其每一台设备嵌入唯一数字签名，但是在当下我们需要能够监控已经投入使用的设备。

我们寻求的革命性的设备识别方案，方案不需要对现有产品进行改造（如改变通信协议或者生产过程）。

<br>

**为什么要参加比赛**

本比赛为世界各地的参赛者提供：

赢取5万美金的机会

对参赛者发明的创新的解决方案进行推广和认可

与寻求IoT解决方案的政府机构建立联系的机会

与MITRE专家一起经更好地理解政府的需求的机会（注：所有的知识产权归发明者所有）

<br>

**比赛详情**

本比赛面向各种背景的参赛者开放，我们欢迎想展示才能的个人企业家、学校团队以及想在IoT领域创造影响力的各种规模的企业。

我们寻求的是简单、可承受的物联网设备识别方案以实现在物联网环境中来发现那些伪造的恶意设备。MITRE 物联网团队搭建了一个家庭物联网络来作为比赛的测试环境，这个健壮的智能家居系统包含了一系列价格适中、运行特性各异的物联网设备。我们相信在智能家庭网络环境下被证明有效的设备识别方案可以用于工业、医疗、军队、智慧城市以及其他物联网络。

<br>

**比赛时间表**

9月——10月 注册网站开放，我们需要你提供参赛队伍名称、联系方式以及其他数据来完成注册流程，所以开始想一个好的团队名吧。

11月——12月 比赛会于11月中旬开始，持续时间约为8周（准确时间会在最后注册后提供）。分数将基于团队回答对了多少问题，以及提交答案的速度。

1月——我们计划在1月17日结束比赛。如果没有团队提交完全正确的方案，那么得分最高的团队获胜，但是要想拿到5万美金的奖金必须要至少答对80%

<br>

**比赛注册**

看完比赛介绍后发现我已经来晚了，这个为期两个月的比赛还有一周不到就要结束了，WTF！

不过看完比赛简介后我觉得这比赛还挺有意思，于是就想尝试一下，至少看一看MITRE这个美国政府支持的公司也是CVE背后的公司会出什么样的难题。于是我就开始了注册过程，注册流程还是比较麻烦的，首先你得在MITRE 的网站上去注册，然后收到一封注册确认邮件告诉我会再联系我

[![](https://p2.ssl.qhimg.com/t01b7bdecea2cb9a79c.png)](https://p2.ssl.qhimg.com/t01b7bdecea2cb9a79c.png)

一天后我收到了另一封邮件

[![](https://p2.ssl.qhimg.com/t01359badd4bebc96f4.png)](https://p2.ssl.qhimg.com/t01359badd4bebc96f4.png)

邮件让我先去注册一个他们的在线协作系统帐号，让后他们会通过这个系统给我分享一个参赛协议书，我需要下载这个协议书打印出来然后手写填完并签字后再扫描上传到他们的在线协作系统中。他们然后对协议书进行审核，如果通过审核就会为我开放比赛数据下载渠道。

[![](https://p5.ssl.qhimg.com/t01ce65ca70ad8a3a21.png)](https://p5.ssl.qhimg.com/t01ce65ca70ad8a3a21.png)

等到审核通过后已经是12号了，17号比赛就结束了。

[![](https://p0.ssl.qhimg.com/t014bef2f7b101ebbf1.png)](https://p0.ssl.qhimg.com/t014bef2f7b101ebbf1.png)

<br>

**比赛数据分析**

我通过审核并获得数据下载权限后在线协作系统就长下面这样子的：

[![](https://p4.ssl.qhimg.com/t0100b885c415271ef5.png)](https://p4.ssl.qhimg.com/t0100b885c415271ef5.png)

可以看到比赛数据集主要有5个文件近30G，其中4个文件为比赛数据大小分别都是7.2G，有一个txt文件是这些数据的Hash值，用于验证下载后的文件完整性。紧接着我就开始下载数据了，近30G的数据花了我好几个小时才下完，还是我大360的网速，汗！

数据下载完成后我发现并不知道数据是干嘛的，于是又去协作系统里找线索，在另一个文件夹下有个名为『IoT Challenge answer submission form-11-16-2016-final.pdf』文件，看名字像是答题卡，于是下载下来看看，结果这个文件里有数据的相关说明和题目

[![](https://p3.ssl.qhimg.com/t016bf769365618cdc8.png)](https://p3.ssl.qhimg.com/t016bf769365618cdc8.png)

从给出的说明可以看出原来比赛的数据分别是以16MS/s(sample per second即每秒1600万次采样)的速率并分别以2.42GHz和908MHz为中心频率录制的无线信号，数据保存的格式是16位的有符号IQ值，到这里我也不懂IQ值格式，于是就谷歌了一下，我在国家仪器公司网站上找到了一篇比较详细的介绍文章，详细内容就不啰嗦了，请看原文

来源：[http://www.ni.com/tutorial/4805/en/](http://www.ni.com/tutorial/4805/en/) 

如下面这个信号有幅度、相位、频率几个参数

[![](https://p0.ssl.qhimg.com/t01159701d7c23b75b3.jpg)](https://p0.ssl.qhimg.com/t01159701d7c23b75b3.jpg)

简单来说IQ值是保存无线信号的一种数据格式，分为I和Q两路数据，从下图的最后一个等式可以看出只需要IQ数据就可以得到信号的幅度和相位等信息。

[![](https://p0.ssl.qhimg.com/t01233c743ab2c06028.jpg)](https://p0.ssl.qhimg.com/t01233c743ab2c06028.jpg)

有了IQ数据再加上载波频率就可以还原出无线信号了，对应的硬件也较简单如下图

[![](https://p0.ssl.qhimg.com/t01cb77899876aa533a.jpg)](https://p0.ssl.qhimg.com/t01cb77899876aa533a.jpg)

图 IQ数据对应硬件简图（图片来自网络）

<br>

**题目分析**

比赛的题目要求是要在这原始的无线数据中找出物理设备（注意这里说的物理设备，一个设备的网络地址等可能改变，但无论怎么变，它还只是一个物理设备，例如你一部手机断开WIFI后再连接前后的IP地址可能变了，但是你还只是一台物理设备,你的MAC地址一般也不会变），并且在网络环境变化（如移除某些设备，添加某些设备，设备的网络地址或者通信协议改变等等）后还要分辨出那些新增或者消失的物理设备。一共8道题目，要求找出B1和B2文件中每个独立物理设备的网络ID和设备ID，列出在B1中出现而在C1中未出现（比如设备已关闭或者断电）的物理设备的网络ID和设备ID，其他问题也是类似



[![](https://p3.ssl.qhimg.com/t011bdbf9cd734f1551.png)](https://p3.ssl.qhimg.com/t011bdbf9cd734f1551.png)

B2和C2对应的问题也是类似，一共有8道题，其中B1和C1相关的有4道题，B2和C2相关的有4道题。

答题的时候需要给出设备的网络ID和设备ID，如下的示例答案

[![](https://p0.ssl.qhimg.com/t01552494dc08dfc974.png)](https://p0.ssl.qhimg.com/t01552494dc08dfc974.png)

注意，这里网络ID和设备ID并不能标识一个物理设备，因为网络ID和设备ID有可能会变，后面会讲。

看看这题目感觉还是非常有挑战性的，首先工作在2.42GHz和908MHz这两个频率点的设备可能有很多，如蓝牙，WIFI，ZigBee，Z-Wave等等，那么如何在才能唯一的物理的识别这些采用不同协议的设备呢？

进一步阅读发现主办方还是比较仁慈的，做了一些限定。

主办方只要求我们分析802.15.4（ZigBee）和ITU-T G.9959（Z-Wave https://en.wikipedia.org/wiki/Z-Wave）流量，排除其他流量，如802.11（WIFI）和802.15.1（蓝牙）。ZigBee和Z-Wave是物联网领域广泛采用的协议，常用于智能家居等，这与本次比赛的目的（IoT）还是比较契合的，因为蓝牙和WIFI的安全是比较成熟的研究领域，ZigBee和Z-Wave相对而言就算是比较新的领域了，后面我会再讲详细一点。

分析到这里我发现分数排行榜已经更新了，已经有人做到了75分。（比赛可以提交3次答案，最后会根据时间戳和最高分来确定最后成绩）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0101768baa209d0804.png)

虽然我知道拿奖金的可能性比较低，但是既然参赛了还是想尽量早点提交结果期待拿个名次，所以还是有点开始着急了。

<br>

**继续分析题目**

至此已经知道题目要求和给的数据格式了，下一步就是如何根据给的数据来完成题目了

如下图所示，ZigBee通信一共有26个信道。

[![](https://p3.ssl.qhimg.com/t01abbc056595e2082a.png)](https://p3.ssl.qhimg.com/t01abbc056595e2082a.png)

[![](https://p1.ssl.qhimg.com/t01c35eb9f57dc5d634.png)](https://p1.ssl.qhimg.com/t01c35eb9f57dc5d634.png)

图 ZigBee的信道分布（图片来自网络）

主办方给出的B1和C1两个文件的采样中心频率是2.42GHz，和ZigBee的第14信道吻合。

下图是Z-Wave 的工作频率分布图

[![](https://p4.ssl.qhimg.com/t01dfd2fe7fd48155a9.png)](https://p4.ssl.qhimg.com/t01dfd2fe7fd48155a9.png)

图 Z-Wave 的工频率（图片来自网络）

从图中可以看出，Z-Wave根据地区的不同而采用不同的频率，主办方给出的B2和C2两个文件的采样中心频率是908MHz，与Z-Wave在北美和南美采用的908.42MHz非常接近，虽然ZigBee在908MHz附近也有信道，但是可能性不大。题目只要求列出采用ZigBee和Z-Wave设备，所以可以确定B1和C1两个文件是要求参赛者找出ZigBee设备，而B2和C2则是要求参赛者找出Z-Wave设备。

至此数据格式及题目要求都已经搞清楚了，接下来就该下手做题了。

<br>

**IEEE802.15.4（ZigBee）**

ZigBee的协议栈我比较熟悉，因为我曾经研究过一段时间的ZigBee 安全性,所以拿ZigBee开刀进行分析（关于ZigBee的安全感兴趣的可以看看我和独角兽团队老大杨卿一起发表到DEFCON黑客大会的研究成果[《I am a newbie yet I can hack ZigBee—take unauthorized control over ZigBee devices》](https://www.defcon.org/html/defcon-23/dc-23-speakers.html#Li)）。

ZigBee是一种自组织网络，广泛用于智能家居、环境监测、远程控制等领域

[![](https://p4.ssl.qhimg.com/t015f02cce36c8164d5.png)](https://p4.ssl.qhimg.com/t015f02cce36c8164d5.png)

图 ZigBee应用场景（图片来自网络）

ZigBee网络中的设备安功能不同分为3种：

协调器（Co-ordinator）：起核心协调作用，负责组网，分配网络地址等等

路由器（Router）：负责转发数据（也可以兼具设备功能，例如一个智能开关）

终端节点（End Device）：即设备，像传感器、智能家居里的开关等等

类似电脑一样，每个ZigBee设备在通信的时候主要由网络地址（NetworkID 又称为PANID）和设备地址（DeviceID，又称为短地址）来寻址。

[![](https://p5.ssl.qhimg.com/t01c3c5a0e48b08f2b7.png)](https://p5.ssl.qhimg.com/t01c3c5a0e48b08f2b7.png)

图 ZigBee的网络拓扑（图片来自网络）

但是无论是网络地址还是设备地址都不能唯一的标记一个物理设备，因为NetworkID是由协调器在建立网络的时候设定的，所以同一个协调器物理设备可能建立不同NetworkID的网络，DeviceID是终端设备在入网时由协调器分配的，当这个终端设备再次入网的时候可能会得到另一个网络地址。也就是说，同一个设备，两次入网地址可能就变了，所以DeviceID也不能作为唯一标记物理设备的ID。

每一台ZigBee设备在出厂时都会有一个64位IEEE地址或者叫扩展地址，这个地址类似与电脑网卡的MAC地址，一般是不会变的，所以可以用来唯一标记一台物理设备，而这个IEEE地址在ZigBee通信过程中一般不使用（ZigBee通信过程一般使用网络地址和设备地址），只在特殊的时候使用，如设备申请入网时，网络广播时等等。只要能找到这些IEEE地址对应的物理设备，则无论这个设备的NetworkID和DeviceID怎么变都能够唯一地确定这些物理设备，所以参赛者的目标就是要找这些唯一的IEEE地址代表的物理设备，并在不同场景（及B1和C1两个场景）中找出其对应的网络地址和设备地址。

那么如何才能从IQ数据中找到IEEE地址呢？我最初的的几个想法是：

1.把数据用Python或者matlab进行处理，参考协议栈的文档一步一步从原始数据（Raw data）解析到网络层，即下图的NWK Frame那层

[![](https://p3.ssl.qhimg.com/t010d1a59228280c1f2.png)](https://p3.ssl.qhimg.com/t010d1a59228280c1f2.png)

图 ZigBee帧结构（图片来自网络）

这种方法肯定费时费力，相当于要自己实现ZigBee协议栈，虽然有一些开源的协议栈可以修改和参考但总归比较麻烦。

开源的协议栈举例[http://zboss.dsr-wireless.com/](http://zboss.dsr-wireless.com/) 

2.对数据进行最简单的底层处理，然后用wireshark进行解析，也比较麻烦。

3.正在抓耳挠腮之际突然想到了软件无线电（SDR software defined radio）设备可以录制信号及重放信号，而IQ数据正是一种很常用的信号保存格式，无线电安全研究部内的独角兽团队有很多同事是软件无线电专家，包括中国第一本软件无线电书籍的作者黄琳也是我们团队的。能不能用SDR把IQ数据重新发送出来，这样就好像是把主办方采集数据的环境从美国搬到了我这里，那么下一步就可以利用我之前做ZigBee安全研究积累的数据分析经验、软件和硬件了。

经过以上分析我决定采用第三种方法，下图是第三种方法的所需步骤的示意图：

[![](https://p4.ssl.qhimg.com/t01b368933013d5b1b8.png)](https://p4.ssl.qhimg.com/t01b368933013d5b1b8.png)

我们已经下载了比赛数据，所以接下来我们要进行图中的第二步，把数据发送出来进行分析

发送数据：可以采用的设备有HackRF，USRP等等SDR硬件，我们团队都有（炫富ing），我们最终用的USRP来进行的发送信号。

分析数据：分析ZigBee数据可以用的软件硬件组合有也有很多，有付费版的软件如Ubiqua protocol analyzer，Perytons protocol analyzer等等，免费的软件如TI packet sniffer，killerbee等等， 至于接收数据的硬件大部分分析软件都支持德州仪器的USB Dongle，而我们手头也有现成的。我最终选择了TI的免费软件+USB Dongle来分析数据。

下图为搭建好的环境，左边是USRP硬件+GNU Radio Companion软件用来发送数据，右边是ZigBee USB Dongle硬件+TI Packet Sniffer软件用来接收和分析数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0151d538eb2e818710.jpg)

下图即为用用GNU Radio发送数据的流图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015dca030c9eb0a2f1.jpg)

现在可以发送数据了，但是还有一个问题需要解决，MITRE要求我们中无线信号中定位识别出发送信号的物理设备，日常环境中与现在我们要定位识别的ZigBee设备同样工作在2.4GHz频段的还有很多其他设备，如蓝牙、WIFI甚至其他ZigBee设备，我们肯定不希望受到其他设备的干扰或者错误地将其他ZigBee设备识别为比赛让我们识别的设备，所以我们需要解决干扰问题。

应对这个问题一般有多种方法，比如直接将信号发送方和信号接收方用屏蔽线（类似天线的馈线）连接起来，这样发送的信号只有接收方能收到，由于我采用的硬件是印制板天线，所以无法采用这一种方法。另一种方法就是在电磁屏蔽空间中进行，好在我们团队有电磁屏蔽实验室（炫富ing x 2），下图即为屏蔽实验室的”铜墙铁壁” ；）

[![](https://p3.ssl.qhimg.com/t01e1937611e92397c5.jpg)](https://p3.ssl.qhimg.com/t01e1937611e92397c5.jpg)

好了，发送数据、接收数据、抗干扰等问题都解决了，接下来看看如何分析数据，如前面所说，主办方要我们在不同环境下列出每个物理设备的网络ID和设备ID。

（解释一下这里所说的不同环境，主办方给出了4个文件，2.42GHz和908MHz的文件各两个，这里每个文件代表一个环境，例如B1代表的一个环境是有N个物理设备在工作的环境，C1却可能代表B1改变后的环境，改变可以是添加或者移除了一些物理设备或者系统重置了，重置的结果可能造成物理设备的网络ID和设备ID发生改变，所以网络ID和设备ID并不能唯一定位标识一个设备）

例如下图中，我们在B1环境中发现了28个物理设备，这其中某些物理设备可能在C1中采用不同的网络ID和设备ID进行通信。

[![](https://p1.ssl.qhimg.com/t0103ac562cda5f47a4.png)](https://p1.ssl.qhimg.com/t0103ac562cda5f47a4.png)

所以我们需要寻找并进行统计的是包含网络ID与设备ID与IEEE地址对应关系的数据包，就像下图这种：

将B1和C1中的所有的IEEE地址（唯一识别物理设备的地址）及对应的网络ID和设备ID关系统计出来就能够回答ZigBee相关的题目了。如下图中的统计结果可以看出红色IEEE标记的物理设备在两个不同环境中的网络ID和设备ID都不同，但其实就是同一个物理设备。

[![](https://p5.ssl.qhimg.com/t019b0f0b4ac2fb12c5.png)](https://p5.ssl.qhimg.com/t019b0f0b4ac2fb12c5.png)

好了，ZigBee部分讲完了接下来我们讲一讲Z-Wave,虽然我还没有时间来得及做，但是在这里还是可以和大家分享一下我的思路和一些相关资料。

对于Z-Wave我们可以发送主办方给的数据，然后用Z-Wave分析工具进行分析。

<br>

**Z-Wave简介**

Z-Wave是由丹麦公司Zensys所一手主导的无线组网规格，Z-wave联盟(Z-wave Alliance)虽然没有ZigBee联盟强大，但是Z-wave联盟的成员均是已经在智能家居领域有现行产品的厂商，该联盟已经具有160多家国际知名公司，范围基本覆盖全球各个国家和地区。

Z-Wave技术设计用于住宅、照明商业控制以及状态读取应用，例如抄表、照明及家电控制、HVAC、防盗及火灾检测等。Z-Wave可将任何独立的设备转换为智能网络设备，从而可以实现控制和无线监测。如下图中是一些采用Z-Wave的产品。

[![](https://p2.ssl.qhimg.com/t0112bcc6b82886ac52.png)](https://p2.ssl.qhimg.com/t0112bcc6b82886ac52.png)

每一个Z-Wave网络都拥有自己独立的网络地址(HomeID);网络内每个节点有其地址(NodeID)，由控制节点(Controller)分配在节点入网时分配。如下图：

[![](https://p5.ssl.qhimg.com/t0142d65a06e79a9d88.png)](https://p5.ssl.qhimg.com/t0142d65a06e79a9d88.png)

图片 Z-Wave设备入网过程图 （来源[http://zwavepublic.com/sites/default/files/APL13031-2%20-%20Z-Wave%20Networking%20Basics.pdf](http://zwavepublic.com/sites/default/files/APL13031-2%20-%20Z-Wave%20Networking%20Basics.pdf) ）

ZWave网络中有两种节点主控设备（Primary Controller）、从设备（Slave）。主控设备的HomeID是出厂就已经设定好的，并且NodeID通常都是0x01，用户无法改变。从设备的HomeID和NodeID在入网前都未初始化，如下表：

[![](https://p5.ssl.qhimg.com/t0110436bf85600dea8.png)](https://p5.ssl.qhimg.com/t0110436bf85600dea8.png)

举个例，注意下图中的从设备（slave）在加入网络之前homeID和nodeID均为0

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0176578c1eb16e67be.png)

下图是当从设备加入网络后Slave已经获得了homeID和nodeID

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01603130ad3ea91f99.png)

所以不难想象除了主控设备例外，Z-Wave设备的HomeID和NodeID不能用于唯一识别一个物理设备，因为一个从设备可以加入不同的网络（入网在ZWave术语中叫inclusion ）从而得到不同的homeID和nodeID。

一篇非常有参考价值的文章：[http://www.vesternet.com/resources/technology-indepth/understanding-z-wave-networks](http://www.vesternet.com/resources/technology-indepth/understanding-z-wave-networks) 

Z-Wave每个网络最多容纳232个节点(Slave)，包括控制节点在内。控制节点可以有多个，但只有一个主控制节点，即所有网络内节点的分配，都由主控制节点负责，其他控制节点只是转发主控制节点的命令。已入网的普通节点，所有控制节点都可以控制。超出通信距离的节点，可以通过控制器与受控节点之间的其他节点，即路由(Routing)的方式完成控制。

Z-Wave 有一种命令可以用来请求节点信息帧NIF（Node Information Frame 参考http://blog.csdn.net/junglefly/article/details/53184484），或许可以用来识别设备。

最重要的一点是Z-Wave和ZigBee设备一样在实际的应用场景中经常会通过一个网关来接入互联网，实现远程控制，这就引起了物联网设备被远程控制或者被作为攻击入口的可能性！

可以用于Z-Wave抓包分析或者发送Z-Wave包的一些工具

OpenZWave[https://github.com/OpenZWave/open-zwave](https://github.com/OpenZWave/open-zwave) 

[https://github.com/selfighter/EZ-Wave](https://github.com/selfighter/EZ-Wave) 

[https://sensepost.com/cms/resources/conferences/2013/bh_zwave/Security%20Evaluation%20of%20Z-Wave_WP.pdf](https://sensepost.com/cms/resources/conferences/2013/bh_zwave/Security%20Evaluation%20of%20Z-Wave_WP.pdf) 

<br>

**最后比赛结果**

大年初一收到一封邮件说比赛结果公布了，如下

[![](https://p5.ssl.qhimg.com/t016b7e07ea9e122f9b.jpg)](https://p5.ssl.qhimg.com/t016b7e07ea9e122f9b.jpg)

激动地发现我居然不出所料地没有拿第一名，不过值得庆幸的是没有白做，上了Leaderboard排行榜。

[![](https://p1.ssl.qhimg.com/t01dd20bbf2099cd0d9.jpg)](https://p1.ssl.qhimg.com/t01dd20bbf2099cd0d9.jpg)

全球130个参赛队，得了第六名，而且由于报名时间晚，为期2个月大比赛我只有6天，所以当在榜单上看见Selfighter的ID时还是非常满意的。

看到Selfighter这个ID只是我个人的ID，其实是由于对比赛背景不了解，所以我们部门就先派我去当小白鼠试试水。



**往届比赛简介**

**MITRE反无人机挑战赛**

官网信息：[https://www.mitre.org/research/mitre-challenge/mitre-challenge-uas](https://www.mitre.org/research/mitre-challenge/mitre-challenge-uas) 

关于比赛的一片中文报道

[http://www.yuchen360.com/news/8205-1-0.html](http://www.yuchen360.com/news/8205-1-0.html) 

个人认为比较有意思的几个比赛入围成果介绍

**Skywall 100**

官网： [http://openworksengineering.com/skywall](http://openworksengineering.com/skywall)     

视频：[http://www.iqiyi.com/w_19rsxqlleh.html](http://www.iqiyi.com/w_19rsxqlleh.html) 

**DroneTracker**

官网： [http://www.dedrone.com/en/dronetracker/drone-protection-software](http://www.dedrone.com/en/dronetracker/drone-protection-software) 

视频： [https://www.youtube.com/watch?v=ti2KtGG4adc](https://www.youtube.com/watch?v=ti2KtGG4adc) 

中文介绍：[http://www.sirenji.com/article/201602/79642.html](http://www.sirenji.com/article/201602/79642.html) 

**MESMER**

官网及视频

[http://www.department13.com](http://www.department13.com) 

<br>

**总结&amp;展望**

在我写这篇文章的时候RSA大会正在美国举行，对于企业安全产品厂商来说这可以说是全球最重要逼格最高的行业大会了，所以很多安全企业漂洋过海去参展/参会，RSA大会能够一定程度反映安全行业的动态。独角兽团队的会棍老大杨卿也去参会了，还写了一篇参(liao)会(mei)经历，（感兴趣的童鞋可以看看http://mp.weixin.qq.com/s/Bc0cGblm7Vl0n-r60y4K6Q ）

在他这篇文章中我看到2张图片

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018c3e98d976a8275c.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019a683ef38c466bfd.jpg)

可以看到这家企业展示的方案不正是IoT设备的检测识别方案吗！

MITRE去年的比赛题目是对抗无人机，比赛过程涌现出的那些idea可能早已应用于美国国防，而过去的这一年我们看到了很多无人机造成的安全事件相关新闻，有用无人机扔炸弹的、偷拍的、造成航班延误的、甚至用无人机作为中继进行渗透测试的，所以无人机已经作为一种安全隐患受到全球关注。我们团队的无线入侵检测产品天巡也将会加入无人机检测及对抗功能，下图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01adae87194d43b659.jpg)

综上所述，MITRE作为一个与美国政府有合作的巨型企业，提出的比赛题目都是和国防有关的具有前瞻性的课题，虽然参赛者们的研究出的方案IP归研究者所有，但是这并不能阻止他们将这些研究成果应用于美国的国防等领域，或者从参赛者的方案中寻求灵感，一场比赛结束或许就意味着他们的某个技术难题被解决。

<br>

**致谢**

感谢独角兽团队提供地研究环境，祝我的团队越来越强大。

特别感谢团队同事杨卿、黄琳、曾颖涛、张婉桥等怪人的帮助。

<br>

**作者**

李均(selfighter)，360独角兽安全团队安全研究员。

[![](https://p5.ssl.qhimg.com/t018c0ebb0077926e88.png)](https://p5.ssl.qhimg.com/t018c0ebb0077926e88.png)
