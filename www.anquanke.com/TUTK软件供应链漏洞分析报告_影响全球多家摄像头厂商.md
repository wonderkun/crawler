> 原文链接: https://www.anquanke.com//post/id/247414 


# TUTK软件供应链漏洞分析报告：影响全球多家摄像头厂商


                                阅读量   
                                **182710**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t018472f66662ba8413.png)](https://p3.ssl.qhimg.com/t018472f66662ba8413.png)



## 漏洞背景

### 概述

近日，360安全大脑监测到 Nozomi 实验室披露了 ThroughTek 公司的 P2P 软件开发套件 (SDK) 中的一个严重漏洞(CVE-2021-32934)[1]，CVSS v3评分为9.1分。该 P2P SDK 用于支持通过 Internet 提供对音频/视频流的远程访问，目前被多个安全摄像头和智能设备厂商采用，是许多消费级安全摄像头和物联网设备原始设备制造商 (OEM) 供应链的一部分。

此后 ThroughTek 公司给出了漏洞影响的SDK版本、实现与修复建议[2]。但是同时 Nozomi 实验室表示：由于多年来，ThroughTek 的 P2P 库已被多个供应商集成到许多不同的设备中，因此第三方几乎不可能跟踪受影响的产品。

时至今日，该供应链漏洞到底影响了产业界哪些厂商，哪些设备型号，依然没有团队给出详细的分析报告，导致潜在受漏洞影响的诸多厂商依然浑然不知，大量的在网设备依然面临潜在的风险而无人知晓。为此，360未来安全研究院 / 工业互联网安全团队通过 FirmwareTotal 供应链安全分析平台，独家提供该软件供应链安全事件分析报告，以期提高业界对本次漏洞事件的关注度和风险认知程度。

### 背景

**网络摄像机的相关概念**

需要先明确漏洞场景中出现的如下几个概念名词：
<li id="u5e4ef49d">
**DVR**：Digital Video Recorder，数字硬盘录像机，主要功能是将视频信息数字化存储到如磁盘、USB、SD卡、SSD 或本地网络大容量存储的电子设备。其前端主要接入的是模拟摄像机，在 DVR 内部进行编码存储。如果 DVR 支持网络输出，也可以成为 NVR 的视频源提供者。 
</li>
<li id="ude68296c">
**IPC**：IP Camera，基于网络协议传输视频控制数据以及发送图像数据的摄像设备。与模拟型信号的 CCTV 摄像机不同，无需本地录像设备支持，仅需要局域网络即可。多数 IPC 都是 webcam，提供实时的监控视频图像。 
</li>
<li id="u5a47987b">
**NVR**：Network Video Recorder，网络视频录像机，基于专用的嵌入式系统提供视频录像功能，但无视频监控设备，往往和 IPC 等设备直接相连，NVR 通常不提供视频数据的编码功能，但提供数据流的存储和远程观看或压缩等功能。有些混合型的 NVR 设备集成了 NVR 和 DVR 的功能。 
</li>
**典型NVR架构**

典型的网络摄像机的架构如下图所示：

[![](https://p2.ssl.qhimg.com/t016d458cc6a0ce917b.png)](https://p2.ssl.qhimg.com/t016d458cc6a0ce917b.png)

在这种工作模式下，用户与其所拥有的 NVR 设备之间有诸如 LAN、P2P、Relay 等多种连接方式。对于 P2P 连接，其指的是允许客户端通过互联网透明地访问音频/视频流的连接功能。P2P 往往借助于隧道技术，而相应的隧道建立方案则因提供商的具体实现而异。

同时，在建立 P2P 连接之前，则需要一个公网上的服务器提供认证与连接服务。此服务器常由设备商或是上游供应商提供（对于此案例，对于使用了 IOTC 库的设备与客户端之间的连接，则是由 ThroughTek 提供），用以充当想要访问音频/视频流的客户端和提供数据的设备之间的中间人。

IOTC（物联网云）平台是 Throughtek (TUTK) 所开发的基于云平台的物联网解决方案。它利用 P2P 连接技术与云计算，加上跨平台API，使得不同的互联网设备之间可以建立跨平台的连接。使用 TUTK 提供的 SDK 所开发的网络摄像机客户端与服务端，会被嵌入 IOTC 库，用于与 TUTK 服务器通讯，并建立 P2P 连接。

由于 ThroughTek 软件组件被安全摄像头和智能设备供应商广泛使用，目前已被整合至数以百万计的连接设备中。作为多个消费级安全摄像头和物联网设备原始设备制造商供应链的组成部分，此次漏洞影响到了 IP 摄像机和婴儿和宠物监控摄像机，以及机器人和电池设备等多种设备。



## 漏洞分析

根据 nozomi 披露的信息，漏洞是由于客户端与设备端库中采用了硬编码加解密算法和密钥，因此第三方可以通过中间人或离线的方式，重建音频/视频流。

通过分析我们发现，问题组件可能以动态链接库文件（IOTCAPIs.dll、libIOTCAPIs.so）的形式打包进设备端固件或客户端程序（exe，apk）中，也可能被静态链接到厂商特定的二进制程序中，例如`goahead`,`tutk_tran`, `TutkTunnel`等，这反映出供应链安全问题的隐蔽性和复杂性。

### IOTC 库设备与客户端交互逻辑分析

为还原漏洞场景，首先我们需要的是一套包含了 IOTC 平台的设备固件，和与其交互的客户端。

无论是固件还是客户端，都会包含 IOTC 的版本信息。所以我们以 IOTC_Get_Version 函数作为搜索依据，在 FirmwareTotal 中搜索相应的固件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c62761a96b516699.png)

得到关联分析结果：

[![](https://p5.ssl.qhimg.com/t017d6a60a26463d0a0.png)](https://p5.ssl.qhimg.com/t017d6a60a26463d0a0.png)



筛选出与包含 IOTC_Get_Version 字符串的单文件相关的固件后，我们这里选取了某摄像头固件作为分析对象。



同时依据产品型号搜索，我们关联到了该摄像头的 Windows 版客户端（md5sum: 9990658d87a78d04186b869bb20a38be）。可以发现 Windows 客户端中的 IOTC 相关功能实现于 IOTCAPIs.dll 库中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01452144ff40d34d53.png)

同时，使用 FirmwareTotal 下载到该摄像头固件的文件系统，可以从中提取到固件端的 IOTC 库文件 libIOTCAPIs.so。

样本就绪后，就可以开始我们的分析任务了。经过对于客户端简单的反编译分析，定位到登录设备的函数 LoginDevice 后，可以初步确认，登录设备所用的设备标识为设备ID。继续进入 VideoPlayerTutk_LoginDev 函数：

可以发现，经由 TUTK 服务器进行认证登录一台设备，所需提供的参数项包含了：
- 设备ID：deviceID
- 访问账户：viewAccount
- 访问口令：viewPassword
继续跟踪执行流可以还原出客户端的如下执行流程信息：
<li id="u79a46154">
首先，客户端使用`IOTC_Get_SessionID`函数，请求到当前连接的一个 Session 并用 SessionID 唯一标识。
</li>
<li id="u3d195401">
此后使用`IOTC_Connect_ByUID_Parallel(_deviceID, SessionID)`连接设备，此处建立连接需要 uid+sid 来共同标识。
</li><li id="ud86d0c5a">
之后还有一步check操作，使用`IOTC_Session_Check(SessionID, &amp;buffer)`对于当前连接的 Session 进行检查，同时在检查成功的情况下，向 buffer 所在缓冲区中写入相应信息。
</li>
<li id="ua692b810">
以上步骤通过后，使用`avClientStart2(SessionID, account, password, 10, &amp;v22, 0, &amp;v20)`对设备进行连接，此时连接所用的 account 与 password，是用于在设备端进行认证的信息，而非与 TUTK 服务器进行交互认证的信息。
</li>- TUTK 服务器端，SessionID 的 check 通过且 UID 可用；设备端，account 与 password 检查通过，则客户端与设备成功建立 P2P 连接。
以上是初步的逆向分析与定位。同时，依据搜索到的 IOTC 文档与源码[3-5]，我们可以进一步还原更准确的设备与客户端连接流程。整体流程如下图所示：

[![](https://p3.ssl.qhimg.com/t0109eb056e0cd30d7d.jpg)](https://p3.ssl.qhimg.com/t0109eb056e0cd30d7d.jpg)
1. 设备注册到P2P服务器
1. 客户端向P2P服务器请求P2P连接服务1. P2P服务器为客户端提供隧道建立服务
1. P2P服务器为设备提供隧道建立服务1. 此后设备与客户端直连，不涉及 P2P 服务器
成功建立 P2P 连接后，设备与客户端便可以开始传输数据了。具体的通讯方式如下：

首先是设备端的流图：

[![](https://p1.ssl.qhimg.com/t01eed8e91d309e2170.png)](https://p1.ssl.qhimg.com/t01eed8e91d309e2170.png)
- 首先进行IOTC 的初始化：IOTC_Initialize(master_domain_name, port)。其中的参数标识了 Master 服务器的地址。Master 指的是一台由 TUTK 维持在 IOTC 平台的，用于检查内部关键信息来管理服务器和设备以及验证他们的身份的主机。
- 此后 Login 线程会被创建，此线程使用 IOTC_Divce_Login(device_UID) 尝试登陆 IOTC 云平台以获取服务。此处的 UID 是 TUTK 为每个服务器和设备提供的 20 字节的唯一标识，用于管理和连接目的。- 接下来便是建立客户端与服务端之间的连接。连接以 SessionID 标识。建立 Session 的前提则是由 TUTK 服务器告知客户端设备的 IP 与端口，以此让两者建立 P2P 通讯。
- 连接建立成功后的数据传输，则是以SessionID对应的连接为标识。
其次是客户端的流图：

[![](https://p2.ssl.qhimg.com/t01fd40f5dde7b6fe56.png)](https://p2.ssl.qhimg.com/t01fd40f5dde7b6fe56.png)
- 与设备端相同，客户端首先需要使用 IOTC_Initialize(master_domain_name, port) 连接到 Master 服务器。
- 其后，使用 IOTC_seession_ID = IOTC_Connect_ByUID(device_UID)，通过传入 UID 来连接自己想要的设备，并在连接成功建立后返回该连接的 Session_ID。- 此后同样以 Session_ID 标识的连接进行数据传输。
### 流量”解密”

由于client端与设备端通过UDP协议传输数据，数据仅进行简单混淆，因此很容易通过中间人方式窃取设备端传输的敏感信息，例如摄像头画面、用户凭据等。“解密”脚本如下

从 libIOTCAPIs.so 版本1.7.0.0开始，已经实现了“更安全”的IOTC_Listen2()和IOTC_Connect_ByUID2() 但是，建立 P2P 连接使用的libP2PTunnelAPIs.so仍然使用的旧版本的接口IOTC_Listen()和IOTC_Connect_ByUID()，意味着建立的 P2P 连接仍没有得到保护。

后续版本中对该“解密”函数的实现略有调整，但差别不大，此处不再赘述。

**虽然该漏洞出现在 TUTK 的 P2P 组件中，实际上，无论采用何种方式（P2P/LAN/RELAY），只要使用该组件进行设备连接，均存在音频/视频被截取的风险。**

### AES misused

通过分析 libIOTCAPIs.so 的加密通信接口，我们发现其中还存在AES加密算法的误用问题。

根据文档， `IOTC_Listen2()`接口的参数 `cszAESKey` 表示加密密钥

当设备端调用该接口启动监听时，将 `cszAESKey` 保存到 session的 `PrivateKey`字段中

[![](https://p3.ssl.qhimg.com/t019087d3b895b4babb.png)](https://p3.ssl.qhimg.com/t019087d3b895b4babb.png)

但是在调用 AES 加/解密时，却将`PrivateKey`字段作为初始向量IV使用，真正的 Ek/Dk 均为空

[![](https://p1.ssl.qhimg.com/t0129ffc6be331ff4ee.png)](https://p1.ssl.qhimg.com/t0129ffc6be331ff4ee.png)

其中，AesCtx结构定义如下

在 libIOTCAPIs.so 的 3.1.10.7 版本中，我们还看到采用ECB分组模式的AES实现，其中使用了硬编码的密钥

[![](https://p3.ssl.qhimg.com/t019ca627fa35aceb93.png)](https://p3.ssl.qhimg.com/t019ca627fa35aceb93.png)



## 影响范围评估

### 版本识别

根据 TUTK 的声明，所有版本低于 3.1.10 的 SDK 都会受到影响。通过提取库文件 libIOTCAPIs.so 或 IOTCAPIs.dll 中， `IOTC_Get_Version()` 函数的硬编码数值，可以识别设备端或客户端所使用到的 SDK 版本。

以某摄像头的客户端为例，将 `IOTC_Get_Version()` 函数的返回值由高位向低位逐字节读取即得结果，其版本为2.1.8.4。

我们采取这个方法对 FirmwareTotal 库中的 TUTK SDK 版本分布做出了评估，结果如下

### 厂商视角

厂商

受影响固件数量

美国 Shield Technology 

96

台湾威联通科技（QNAP）

55

台湾利凌（LiLin）

51

Tenvis

22

台湾广盈（KGuard）

11

Xiaomi

7

美国趋网（TRENDnet）

5

日本艾欧（IO DATA）

4

Tenda

4

Xiaoyi

4

英国Zxtech

3

台湾环名（HME）

1

韩国Hanwha Techwin

1

Relong

1

[![](https://p4.ssl.qhimg.com/t01f13372caac69a897.png)](https://p4.ssl.qhimg.com/t01f13372caac69a897.png)

### 固件视角

通过对 FirmwareTotal 中的固件进行关联分析发现，仅有 5 个固件包含了3.1.10以上版本（3.1.10.7）的SDK。对于低于该版本的SDK，统计包含其的固件数量分布如下：

SDK 版本

包含该版本SDK的固件数量

1.6.0.0

2

1.9.1.0

142

1.10.0.0

21

1.10.2.0

54

1.10.3.0

122

1.10.5.0

1

1.10.6.0

6

1.10.7.0

1

1.10.8.0

27

1.11.0.0

2

1.13.8.0

3

2.1.3.0

13

2.1.4.22

1

2.1.8.4

1

2.1.8.13

1

3.0.0.0

1

3.0.1.29

4

3.1.4.48

1

3.1.5.38

1

[![](https://p5.ssl.qhimg.com/t01c16ea8a1394508a4.png)](https://p5.ssl.qhimg.com/t01c16ea8a1394508a4.png)

### 厂商修复建议

参照TUTK官方给出的漏洞影响范围与修复措施：



**影响范围**
- 3.1.10及更早版本
- 带有nossl标签的SDK版本- 不使用AuthKey进行IOTC连接的设备固件
- 使用AVAPI模块而不启用DTLS机制的设备固件- 使用P2PTunnel或RDT模块的设备固件


**修复方案**
- 如果SDK是3.1.10及以上，请开启Authkey和DTLS
- 如果SDK低于3.1.10，请将库升级到3.3.1.0或3.4.2.0并开启Authkey/DTLS


## 写在最后

相对于CVSS 给出的 9.1 的威胁评分和需要抓取流量作为利用前提，摄像头类的设备面临的 RCE 漏洞往往更为致命，我们呼吁关注设备厂商关注摄像头设备的代码质量和供应链的风险。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0171407a0c54ef28cd.png)

在分析此漏洞的过程中，通过安全大脑在全网的持续监测，我们观测到该漏洞影响的厂商和产品型号范围依然在增长变动的过程：（完整的受影响设备固件和文件列表见文末附件）

此外，安全大脑还监测到mirai_ptea僵尸网络正在利用上述设备的其他漏洞进行DDos攻击和传播[6]，这引发了另一个角度的思考：

在供应链安全风险的问题上，过去业界主要聚焦于关键基础设施等个别领域，而在其他领域，特别是IoT等小型智能设备领域上，往往由于单个IoT设备安全问题影响较小而普遍被忽视。**但是，如今由智能家居、产业数字化升级、智慧城市建设、智能车联网、智能工业互联网等形成的超过百亿联网IoT设备聚集起来形成的设备网络，某种意义上讲已经形成了另一种形态的新型关键基础设施，并且可以触达城市/工厂/居民家庭的各个角落，一旦大规模的IoT设备被僵尸网络控制，将可能被用于窃取城市、国家方方面面的情报数据以及发动大规模的网络攻击。特别当再次出现类似由上游软件供应链问题导致的大规模安全事件时，将可能导致网络空间成千上万的联网设备同时出现安全风险，其可能导致的潜在威胁将足以比拟关键基础设施安全问题。**

产业的全球化进程导致了软件供应链问题更加错综复杂，全球各厂商生产制造过程彼此互相交织，网络空间安全已经是全球问题，需要全球合作，携手保障数字经济安全。

从近年来的国家立法层面以及激励政策方面，已经可以看到越来越多提及到供应链安全，例如《网络安全审查办法》（修订草案征求意见稿）[7]中的开篇第一条：

第一条 **为了确保关键信息基础设施供应链安全，维护国家安全**，依据《中华人民共和国国家安全法》《中华人民共和国网络安全法》《中华人民共和国数据安全法》，制定本办法。

以及在《网络安全产业高质量发展三年行动计划(2021-2023年）（征求意见稿）》[8]中**将软件供应链安全列为重点任务之一**：

6.**加强共性基础支撑**。持续建设高质量威胁信息、漏洞、恶意代码、恶意地址、攻击行为特征等网络安全基础知识库，强化网络安全知识支撑能力。加快发展恶意代码检测、高级威胁监测分析、信息处理、逆向分析、漏洞分析、密码安全性分析等底层引擎和工具，提升网络安全知识使用水平。**加快发展源代码分析、组件成分分析等软件供应链安全工具，提升网络安全产品安全开发水平。**积极推进网络靶场技术研究，建设结合虚拟环境和真实设备的安全孪生试验床，提升网络安全技术产品测试验证能力。



相信未来软件供应链安全问题的治理将会得到不断的改善，360安全大脑与安全专家团队也将持续为客户提供更好的软件供应链安全治理服务与基础设施建设服务。

在此也欢迎厂商和我们联系以获取更详细的信息，协手合作，共同提升安全防护能力。



另外，我们近期正在招聘，包括安全研究员、Web前端开发、Web服务端开发等岗位，校招社招都有，欢迎热爱技术的你加入我们，简历请投递：iot-fw-sec@360.cn。



## Reference

[1] [https://www.nozominetworks.com/blog/new-iot-security-risk-throughtek-p2p-supply-chain-vulnerability/](https://www.nozominetworks.com/blog/new-iot-security-risk-throughtek-p2p-supply-chain-vulnerability/)

[2] [https://www.throughtek.com/about-throughteks-kalay-platform-security-mechanism/](https://www.throughtek.com/about-throughteks-kalay-platform-security-mechanism/)

[3] [https://github.com/cnping/TUTK](https://github.com/cnping/TUTK)

[4] [https://download.csdn.net/download/u013852008/12797862](https://download.csdn.net/download/u013852008/12797862)

[5] [http://www.sunipcam.com/sdk/%E8%87%AA%E5%8A%A8%E8%B7%9F%E8%B8%AA%E7%90%83%E6%9C%BASDK%E5%BC%80%E5%8F%91%E5%8C%85.zip](http://www.sunipcam.com/sdk/%E8%87%AA%E5%8A%A8%E8%B7%9F%E8%B8%AA%E7%90%83%E6%9C%BASDK%E5%BC%80%E5%8F%91%E5%8C%85.zip)

[6] [https://blog.netlab.360.com/mirai_ptea-botnet-is-exploiting-undisclosed-kguard-dvr-vulnerability/](https://blog.netlab.360.com/mirai_ptea-botnet-is-exploiting-undisclosed-kguard-dvr-vulnerability/)

[7] [http://www.cac.gov.cn/2021-07/10/c_1627503724456684.htm](http://www.cac.gov.cn/2021-07/10/c_1627503724456684.htm)

[8] [https://wap.miit.gov.cn/gzcy/yjzj/art/2021/art_34f89fff961b4862bf0c393532e2bf63.html](https://wap.miit.gov.cn/gzcy/yjzj/art/2021/art_34f89fff961b4862bf0c393532e2bf63.html)



## 附件

### 受影响固件型号列表

厂商

固件名称

MD5

HanwhaTechwin

WisenetMobile.zip

92d6c709a941d44aa476b6736470c336

HME

HM-4LADVR264-205.01.09.XXX-v154.zip,HM-4AL.zip

e325a54bbd66cb9442344bcf92e892ad

HM-16LADVR264-32.03.12.XXX-v154.zip,HM-16AL.zip

88bfa641a374460ec84a5e994f19764d

HM-8LADVR264-211.02.39.XXX-v154.zip,HM-8AL.zip

8d6d09b89f505ec818993f1fdbde37a3

HM-45DVR264-214.01.08.XXX-v154.zip

bbdaad67344f93a52cef6e5a5d65f644

HM-4M16ADVR264-32.03.08.XXX-v154.zip

089581374bb8a1538c6fa81ebe038a10

HM-16ADVR264-32.03.09.XXX-v154.zip

711fcaf06bf1f5a95402749a20900fb4

HM-8HDVR264-211.02.42.XXX-v154.zip

d13c5c24014d961c722f066cfa21c02c

HM-3116AFHDLDVR264-31.03.07.XXX-v132.zip

61c2e2eed4d06d2a6b84c4e1474b7fd2

HM-8ADVR264-211.02.09.XXX-v154.zip

acb94b5846382a83634776a4b2014389

HM-4M8ADVR264-211.02.08.XXX-v154.zip

d224c59b1aca9d234bcfcb5fb6d5399f

HM-165DVR264-35.03.08.XXX-v165.zip

4bd5014ad4598b1763ed810730851215

HM-4M4ADVR264-211.01.08.XXX-v154.zip

22b18fc59e656d1f40b31006ef47991a

Aquila.zip

3add1a452d0544ec6d46fee94be3c554

HM-85DVR264-214.02.08.XXX-v85.zip

f02a265b656cd5d5693f9586fc4180a6

HM-16HDVR264-32.03.42.XXX-v154.zip

57e29ad61b11409ff6ffb29d0428b801

HM-4ADVR264-211.01.09.XXX-v154.zip

7445506d2d7eb699aed4c5909819a97f

IODATA

wfssr02_f111.exe

4d7ea755ddfd7c6002da284eb0a2a46a

wfssr02_f110.zip

f2911a80cc815ce22156c4c57b75cb16

wfssr02_f110.exe

6fd383b1eb1c12decf7dd911c93897af

wfssr02_f111.zip

9487aec3ccef0dcf156a2af2c6db3199

KGuard

How_to_upgrade_QRT601_FW6K_IPC_V4.00.00.80_20170426.zip

55e74555b5919a8d714cc34a03580c49

dvrupgrade.zip

60c1fec812eb21b2011e30ccf6585b43

UPG_ipc5955a-mw7-M20-hi3518e-20151201_171603.zip

405592d898e8f6956b77d3b7d7a94f72

UPG_ipc2564a-w7-M20-hi3518e-20160104_155726.ov

c5377798cd9740d9be066e824718c68b

CONSUMER_KGUARD_6K_IPC_V4.00.00.79_20170104.img.rom.zip

49313db90be3adb99aa4d5480c6324a7

V20160831.zip

3c23f77c568193e6cb5da5956c60ba87

UPG_ipc2564a60N-w7-M20-hi3518e-20160606_144704.ov

9b224d97849cdf242345d1b307ee6f18

CONSUMER_KGUARD_6K_IPC_V4.00.00.80_20170426.img.rom

56c35f4839080d4e242228d2a679f7a9

dvrupgrade.zip

36676808c7e51107fe1407e3240d85e6

V20160831.zip

ea99decbcd2d0843b1947a70f6bff967

UPG_ipc2564a60N-w7-M20-hi3518e-20160831_161521.ov

b33a7cff0cb3f860fa8fefa6c3f2e14c

LiLin

DHD204A–USBRecoveryTool.zip

f2dfc5a9bf894f76a5d15aee82799cf9

DHD216Firmwarev2.0b60_20200207.zip

a608295e6a0be3e9a925f0f14c020eae

DHD208Firmwarev2.0b60_20200207.zip

ec934cbcdc328a7c46aabde3827c29f8

Firmware-DHD504A-EN.zip

f38fc70b5fa8f45dcae9c6edb6e2f910

DHD216A–USBRecoveryTool.zip

d688cee5b0704aa6335502d483d428dc

DHD204AFirmwarev2.0b60_20161123.zip,Firmware-DHD204A-EN.zip

d0c31820e03f24df77f55b4b3cc6fedb

DHD208A–USBRecoveryTool.zip

8b3af5fc3b5cf45ccd25cb7379259c69

Firmware-DHD216-EN.zip

8dde05721ec30927c062e7e67556e0ec

DHD208AFirmwarev2.0b60_20200207.zip

0b335d7cab4e5ef460bb7df1607697bc

DHD204AFirmwarev2.0b60_20200207.zip

642aa28e3a36188e798b67901a6bb193

DHD208AFirmwarev2.0b60_20161123.zip,Firmware-DHD208A-EN.zip

59eb27fc1bb61f2c2c9c3e4da717ffd4

DHD216AFirmwarev2.0b60_20200207.zip

31328d3424c79895232c599941ef03dd

DHD308AFirmwarev2.0b1_20200122.zip

a8f2daf3b1d072e56bf6c09066edd0b1

Firmware-DHD316A-EN.zip

da4a90762aa1be0204b24ab4c6f9c098

Firmware-DHD516A-EN.zip

d3d70caf606648c5f682f4ee4b68be2b

Firmware-DHD208-EN.zip

7cbacba456dddc30ac490a2414af0d4b

Firmware-DHD304A-EN.zip

f8104380a8e4a606db575c70fe9228a6

Firmware-DHD216A-EN.zip

c0d3206baaf7740f30a63e6cb29670fc

Firmware-DHD508A-EN.zip

5bafd973bdcf0ad65c4faceef71804ac

DHD508AFirmwarev2.0b1_20200831.zip

1ee2c99601c974e4cffe2afc060e1c0f

DHD204AFirmware.zip

3bb95a6a11d6213fdc8a65752bf85091

Firmware-DHD308A-EN.zip

11bc95e2f178973eae61d069107803a2

DHD208Firmware.zip

e5220410a9b337eb77ada1e1c7faa05a

DHD516AFirmwarev2.0b1_20200122.zip

0f874ec282b07bb4f53dd937daea77c6

DHD516AFirmwarev2.0b1_20200831.zip

fac35e234798c162ea2338ae5375e35e

DHD304AFirmwarev2.0b1_20200122.zip

732933d0537fd8fbbc07066489f57909

DHD216AFirmware.zip

60b7cad13e980f0375c09a491d14fef7

DHD504AFirmwarev2.0b1_20200831.zip

7e13031205a2f2b6a12464608a18d2c2

DHD508AFirmwarev2.0b1_20200122.zip

1f6e90038859d338a5f2a571a68498c3

DHD308AFirmwarev2.0b1_20200122.zip

e4426c0afb65aa6a7170c4b308135ab2

DHD316AFirmwarev2.0b1_20200122.zip

7ed897f4379618cbc0f4a55ee6c4bbdd

DHD316AFirmwarev2.0b1_20200122.zip

dd5a032b9253b2ad033c5277e4e10a54

Firmware-DHD216A-EN.zip,DHD216AFirmwarev2.0b60_20161123.zip

c637b9257c4e32fc561268383d640680

DHD504AFirmwarev2.0b1_20200122.zip

2e9aa72f61745a0e41f6522e37ea107f

DHD216Firmware.zip

6b17da1367893e4cd37595cc00d40433

DHD304AFirmwarev2.0b1_20200122.zip

2b1c05d37361929d526f48ecdf7baa87

DHD504AFirmwarev2.0b1_20191202–JPEGC4panels.zip

bb0569fcd47f3d00e0682bc9084a7ffd

DHD216Firmwarev2.0b60_20160504.zip

9ec09b458d285581a1c1861cb86da1ff

DHD308AFirmwarev2.0b1_20180828.zip

36d12e7c6fb405eb1393c432c92b86d3

DHD316AFirmwarev2.0b1_20171128C4Panels.zip

25fcb06fb2cd16ce60c594588ecc9d3a

DHD504AFirmwarev2.0b1_20200122.zip

a952d245e24729ccd8cb8d38bf1c95f9

DHD316AFirmwarev2.0b1_20180828.zip

4733c821a9810400801fed85f8245f41

DHD304AFirmwarev2.0b1_20180828.zip

19253ec8c68584ebd3c48195a4f4ec0b

DHD208AFirmware.zip

eed926087506f148d232b8817aadbd74

DHD208Firmwarev2.0b60_20160504.zip

b31dde088b5fcceec35345c0161f8bb0

DHD508AFirmwarev2.0b1_20180828–RTSPworks.zip

8f0f811176d017725fe76276f44fcb63

DHD508AFirmwarev2.0b1_20200122.zip

089457119b634b5d30c9abbc3847a111

DHD516AFirmwarev2.0b1_20200122.zip

13e51689f210df16389cb4f163805a7d

DHD504AFirmwarev2.0b1_20190417–JPEGC4panels.zip

34b80e18c9f74fe71ccd2bfee28b656d

DHD516AFirmwarev2.0b1_20191202–JPEGC4panels.zip

d9a63812da9bd01d3cd58a74139d681c

DHD516AFirmwarev2.0b1_20180828–RTSPworks.zip

628a779bd203ae93fbba43d36230f3ab

Tenvis

IPC_V1.7_V1.7.25.zip

811276e2a53507e8f70157ff629829fe

IPC_V1.4_V1.7.25.zip

695f3de656d7ff8b2379f2a9c0e5bd49

V1.4_V.2.7.19.zip

e40225e1eff4bbee61513a0cfc45e5fe

V1.4_V.3.7.19.zip

c8cb59d9845ccd7df759473f80cf2fd6

QNAP

TS-659_20140927-4.1.1.zip

c0e6a2982c1254ad3896b5ef5d3ee1e5

TS-X80U_20160304-4.2.0.zip

3e6ca554bacf3e25279c323290f7c778

TS-X80_20160304-4.2.0.zip

1012f15d9a641622fc677a86a72b818a

TS-X53_20160304-4.2.0.zip

f7b43354df57c41f08e7013be83900f6

TVS-X63_20160130-4.2.0.zip

90f505e036462d5bd1e118d1a62e3197

TS-119_20160304-4.2.0.zip

2773bbc713de460f45309ac546c9fb44

TS-X53U_20160304-4.2.0.zip

03151f5fd462e8797c44fcecf9e44c69

TS-419U_20160304-4.2.0.zip

e4d6be4139c6a1552d1c09579afcc9bf

TS-459U_20160304-4.2.0.zip

c083e006937caf18a1576ae35e13c1af

TS-X51_20160304-4.2.0.zip

63a183afdfe3f0128a1826fc7bb91464

TVS-X63_20160304-4.2.0.zip

92770357df3a254db216cdcbab9ffc37

TS-469U_20160304-4.2.0.zip

2e071f187ec55396a2ff9901b5bfa155

TVS-X71_20160130-4.2.0.zip

6ac6be37b01d8cc1538f5362b04c4cea

TS-410U_20160304-4.2.0.zip

112d34e99b301fe070b0037079969332

TS-412U_20160304-4.2.0.zip

ae04469ce7ee1bbd8f76a2d7fd7869dc

TS-563_20160130-4.2.0.zip

0aaf048f2b6ea8ce2b67d5fe9a191694

TS-X51U_20160304-4.2.0.zip

bea3fc5b5ea45910107424c6803e7c4c

TS-669_20160304-4.2.0.zip

161ecb722f67651b9de060eb05509d85

TS-459U_20160119-4.2.0.zip

3d1fe6543417dd4c5b8db827ba9deeeb

TS-439PROII_20160119-4.2.0.zip

1babdd6f710c810bf046117459c04aff

TS-420U_20160304-4.2.0.zip

745120d158cd1543ef3fce53e54b9b2e

TS-410_20160304-4.2.0.zip

c9c6229ecfd39c545d18d9c3c71665da

TS-559_20160304-4.2.0.zip

47a1d2785c371daa28f5d7e12511dc65

TS-509_20160304-4.2.0.zip

6683fdd4d54d5d13691857c138bfa552

TS-419P_20160304-4.2.0.zip

ff50390ffaf4670e6907c07949c2bcd8

TS-269_20160304-4.2.0.zip

2524527e5cebbaabb89840aa41a2f726

TS-439PROII_20160304-4.2.0.zip

604d0f3f8692e0bb6c5505e4cd55c492

TS-X80_20160130-4.2.0.zip

c94cbb939db7cf19882858be21764ea4

TS-1269U_20160304-4.2.0.zip

6973f7caa676c9017ff830eb0848e4b6

TS-1079_20160119-4.2.0.zip

07878a5243dcd01dce027a67814c462f

SS-439_20160304-4.2.0.zip

f08fb240a13ea43b67110419f6ce8339

TS-421U_20160304-4.2.0.zip

8dd0eec2a461091ab8f8035c4f6b8a1f

HS-210_20160304-4.2.0.zip

8068d19a495092d751ef6992d58cd093

TS-219_20160304-4.2.0.zip

93c0bef32ebd932954e3bf57ed5dba3b

TS-870U_20160119-4.2.0.zip

9b25a699e26519563a13217d506960d2

TS-870_20160130-4.2.0.zip

cc506a7effed5a0df045839541513c05

CloudLink_2.2.21_20210518_arm_kw.zip

8c1e4424f912d7a461f6fbf0c034396f

TS-239H_20160304-4.2.0.zip

796e93f5a6c42f6352b8f0f711116e2b

TS-439_20160304-4.2.0.zip

9f84b0fc74f5150d5657687226acd85c

TS-869_20160304-4.2.0.zip

e43bf5adee98d1edcf866c72f6270aec

TS-239PROII_20160304-4.2.0.zip

b04399fdbb3f342919c08d65fb3b0921

TS-1679U_20160304-4.2.0.zip

6903b380db88df87767235294851dbde

SS-2479U_20160130-4.2.0.zip

b5e9560ad8553770fd2ffa5be82b2c98

TS-879_20160130-4.2.0.zip

cd155f21f8fd0c44bbc35b816996d2e2

TVS-X71_20160304-4.2.0.zip

c10398ffafcaf850cddc95c5e3d2a00f

TS-210_20160304-4.2.0.zip

e8050aab3d94f208d1fcdf38acedac95

TS-221_20160304-4.2.0.zip

a0cfdf15a0a21b541e0370909b85ce3b

TS-459_20160304-4.2.0.zip

042220a0f9cafa05f4f9ee470758b10b

TS-859U_20160304-4.2.0.zip

9d5ff226d49d8c44a061013aa489e083

TS-659_20160304-4.2.0.zip

fe22733957c90d5fe7a96c2207e299d3

TS-809_20160304-4.2.0.zip

3e5f27b4d0c72ede3418b104f49d3a22

HS-251_20160304-4.2.0.zip

80a1f0e5bde5859ff7f836b170d29a46

TS-1270U_20160304-4.2.0.zip

329abb891f03d1f78ab22d7cb1270a85

TS-870U_20160304-4.2.0.zip

c5d1bbd10b6fdc8420201472c6e1c5fd

TS-239_20160304-4.2.0.zip

05323ef7e6344430235fe23929300b4a

Relong

RL-HD-VR3908.zip

de844985d49fdad47a3ecae894958538

ShieldTechnology

shield_vi-2.0b1_20170119.fw

15acda940b3e649ab7c9199702fc016f

shield_vi-2.0b1_20161024.fw

e194d305634dcc2212e179aff6bd7066

shield_vii-2.0b1_20180628.fw,sh-shd-16a-recovery.fw

5e4fd97df0fb8c17f5f6f407da93a97f

shield_vi-2.0b1_20161020.fw

6eb77f08d73654113c48112dbc33879f

shield_vi-2.0b1_20160805.fw

0b2f930ef5c36f04b8ede764baa03e9d

shield_vi-2.0b1_20180223.fw

a017e37c44016c9112e23aa19602aa0d

shield_viii-2.0b1_20180706.fw,sh-shd-8a-recovery.fw

7283469b6f986e9e063ab7b2fda22148

shield_ix-2.0b1_20180628.fw,sh-shd-4a-recovery.fw

5b5e0e182155217c31ca76253fcc8c26

shield_ix-2.0b1_20170707.fw

0105c2a12429c795494e1dc61608e78d

shield_viii-2.0b1_20161110.fw

0e8d59aac44f529a5074d87a49500ef6

shield_viii-2.0b1_20161021.fw

87593f82d1e7d3363cc040c066dfbb64

shield_v-2.0b1_20150915.fw

acbc87e90913e810f54afaa464dd8c40

shield_ii-2.0b1_20170315.fw

ca1fd1dc7970b34575670b17748134e6

shield_i-2.0b1_20160816.fw

7cbea9490eb542306323b7b45782eceb

shield_xi-2.0b1_20170119.fw

a6f03b02106877bfc75117f9b78706ec

shield_v-2.0b1_20160913.fw

c0c9e23c65af28ba87574d739218acd9

shield_viii-2.0b1_20161121.fw

4bc93352e65dd2a5fdc90ac4537e2e43

shield_v-2.0b1_20160628.fw

35f1ab8451c0bc5fe68bd86033cd2a23

shield_shd-16ch-20181025.fw

5104cf9ab99fbed33cc6a52a40041dc0

shield_shd-8ch_20181025.fw

2cc982048955c2d5a09a54e605a10baf

shield-iv_2.0b1c_20170426.fw

4e082b9f86632e308cbed27105252a15

shield_ix-2.0b1_20161110.fw

4622adf5b63b1f7e6927470fb6fc34ed

shield_ii-2.0b1_20150827.fw

9e5051431a7e3fdbfeba3b0d5d9ac624

shield_ii-2.0b1_20150924.fw

2c8a43388bb009fb0b1ed184dea34e13

shield-ix_2.0b1_20161012.fw

89f5441996e3bab2b3b168024f539467

shield_vii-2.0b1_20160816.fw

44f073d5e701eedc767eda7bd102109b

shield_vii-2.0b1_20170707.fw

c2e0b02877b18fb782cd62970bf534ae

shield_vii-2.0b1_20170816.fw

17321c0aaf1515b44fba7505903919d5

shield_i-2.0b1_20170619.fw

0fa086c388500711fb71a46747c47447

shield_i-2.0b1_20160428.fw

9c6fa6df3969a798f205d782e6c8ece1

shield_ix-2.0b1_20161026.fw

b82076ff92a55bb24e55a70a3d8b757b

shield_vii-2.0b1_20161110.fw

8db7f849adfdc491f02e444a7797d8af

shield_viii-2.0b1_20180418.fw

883a320bf52c83a51d52666bb78d632e

shield_v-2.0b1_20160428.fw

97a4556158f76882a43c71b641dd748c

shield_iii-2.0b1_20160628.fw

2b15c5c951d8c39a0415ea73bcd9e209

shield_x-2.0b1_20170119.fw

219e6a04a4f9cf730fc601b21fe21b4f

shield_x-2.0b1_20161020.fw

f647cc20a87c99ec2b5905fd9c55ab56

shield_v-2.0b1_20150827.fw

0d4e401cc05fea86d83d4b2ba510d788

shield_ii-2.0b1_20160816.fw

5e8ceb9b92e1c08e91b4faf303cc502b

shield_ii-CN-2.0b1_20161027.fw

0afda3f4129134faf9353e4c9677759c

shield-vii_2.0b1_20161012.fw

60041a1d6b3e514a76f2f071247a6735

shield-viii_2.0b1_20161012.fw

17dbb3495434438b43412a989769ed88

shield_shd-4ch_20180628.fw

1b0230d0f83b274dba26155a01c498c4

shield_vii-2.0b1_20180518.fw

3d7d17ba4b35ee54b51a9bbe08b38f69

shield_v-2.0b1_20160420.fw

806faa8d74af75e47ef42d9c98b45376

shield_i-2.0b1_20150924.fw

75d5aab26396cb0f28a65aea58d40f19

shield_ix-2.0b1_20180418.fw

23f4b6db9c5712d3792c97310705c9e8

shield-viii_2.0b1c_20161102.fw

bfe2e917fabe26c15bdbeee9f998b508

shield_iv-1.1b9_20150107.fw

32ee533eaa4f75cb1e23f31e918f8155

shield_vi-2.0b1_20180925.fw

ab0f50bff8f694f9da2cd9535ead17a9

shield_iv-2.0b1_20160816.fw

c4cff1813eacac4849a6aecf9a55277e

sh-shd-16-recovery.fw,shield_shd-16ch_20180628.fw

e8110ff80ed3085970ff88276906d3c3

shield_vii-2.0b1_20181025.fw

a3177c7355e16e3b927e95d80755e215

shield_v-2.0b1_20160816.fw

e470872ff4caeeedafb208240bed5c52

shield_ii-2.0b1_20170420.fw

d32e323a93b8eae16260864fd8d31f70

shield-ix_2.0b1c_20161102.fw

b84a7a046e288d915e2079477935a410

shield_vii-2.0b1_20161121.fw

18e8a157d448ee78ea8e75ef31f17863

shield_v-2.0b1_20170420.fw

fadcd28d5930b8d7757cb6061a0f75eb

shield_vii-2.0b1_20170712.fw

c94d85e6c4d05953150d96bac73a3aad

shield_ix-2.0b1_20170712.fw

ca699dd906974e696585bb1472eafbe0

shield_v-2.0b1_20150924.fw

f073c59f8aa0917e0120fb0ed1005ed9

latest.zip

c3d71f73ce32ae174bac9db4f47292a2

shield_ix-2.0b1_20161121.fw

bc5f5cfeead62135c81e6a507ae63280

shield_ix-2.0b1_20171220.fw

51138820bcf9cd249bdd18b982579983

shield_viii-2.0b1_20170306.fw

b3b9e6687bb84c0a4bf68af8e88c1148

shield-vii_2.0b1c_20161102.fw

1896ed3dc98360bdac6e3733838f75db

shield_i-2.0b1_20170315.fw

9eece33e5f1928c1fed137d45404538a

shield_i-2.0b1_20161116.fw

54cb565d188093da423ad3c41773c1d1

shield_ix-2.0b1_20170306.fw

e9819adc4faa92731269ce73360f9733

shield_ii-2.0b1_20160420.fw

646b2e20453c16f6f61ad347276a3c9e

shield_ii-2.0b1_20160628.fw

50b273da4d0f3f9272441b48fe9f165d

shield_iv-2.0b1_20150827.fw

7165fdec748161c8b3793c8c00ca197d

shield_viii-2.0b1_20170707.fw

c83dad64259dad6f092cf23f278658e2

shield_viii-2.0b1_20171220.fw

ea8d80d13959624bf8786a092444a8e4

shield_v-2.0b1_20160819.fw

8f082c58336065df47fdb2b5ac6b32d4

shield_iv-2.0b1_20160428.fw

758d810d67c64b33933e5fc30e1985df

shield_vii-2.0b1_20161021.fw

78e58703fbce0c657a227fa313351753

shield_iii-2.0b1_20170420.fw

16a7443dd26b3eda306d3c4986141150

shield_shd-8ch_20180628.fw

8de87cd7f4a33e596a15780eeab2e0d0

shield_iv-2.0b1_20150924.fw

b52b9ccba69eb7901265f5930f5a67f1

shield_iii-CN-2.0b1_20161027.fw

845f2b1c283ff3f842690ecc7560815b

shield_iii-2.0b1_20150827.fw

ad6634bdc53061e29f2b33912ac297e2

shield_iii-2.0b1_20161027.fw

8093814fbae55921f270e0c05f35d7d5

shield_v-2.0b1_20161111.fw

258bef9781583bb17667922c3575daba

shield_v-2.0b1_20161007.fw

62fd3fa8e8f51804defe07945591353b

shield_ii-2.0b1_20160428.fw

124e54a078a3fca5a8d242dc64093b36

shield_x-2.0b1_20170427.fw

022f4ecda54ae7d22242a01435ab45ce

shield_vii-2.0b1_20171220.fw

23db82bc3300ac4c5f84e342aba9f86a

shield_ii-2.0b1_20161123.fw

cd709f3aacb94df00df04a570facf368

shield_ix-2.0b1_20170816.fw

a55b755d5686fe69104dedf6cf903915

shield-viii_2.0b1c_20170426.fw

d0fed619e7d3fd6455dafbb2f05bd3a0

shield_ii-2.0b1_20161027.fw

4c0f6d0185cc23840845bb1271b811dd

shield-ix_2.0b1c_20170504.fw

7bb20496333e6d4a4f62d8dcae3a5cc8

shield_ix-2.0b1_20161021.fw

036811da8594b13beb9695d2eadd2c63

shield_vii-2.0b1_20170310.fw

cb9066178638611c20d39b09d2d2d96c

shield_viii-2.0b1_20170712.fw

43a8abd37983d3e53ca9c9517593911b

Tenda

Android%20APPS.rar

ca8f6c9ef6d9ffc0f4a78e5f1dc63828

C50sV2.0%20system%20firmware.rar,C50sV2.0systemfirmware.rar

9caf0e5bdb263a99dc6d274336ad1909

TendaCamera.rar

99cf5a3a25d0c6f24596713715e8f60e

Android%20APPS.rar

e92df4c0aa6b6b8bb0a0f10f1159ebc1

Tenvis

IPC_V1.7_V3.7.25.zip

69cf4f164c59b9d3632cd72a17945f3a

IPC_V2.7.24_HW-V2.4_1129.zip

e17cbab3dcb816486efa62eeaa467697

IPC_V1.4_V3.7.25.zip

db42b58a39926ca2abe29ebf202a75fb

5.1.1.1.5.rar

c114c34b0e712a6b91bd55f98118532a

12.1.1.1.2.rar

bfc38783aaf8fc6f6c309317a5afe221

IPC_V2.7.24_HW-V2.7_1129.zip

35b14c2e251bfbc6cd317e3fbf63b1cc

3.1.1.1.4.rar

3a41ad52cddc5a9a66a59196a16320da

UPG_ipc5160a-w7-M20-hi3518-20160229_183313.ov

37e54ff6207db37e0059b4b82edcb3cf

V2.7.25_V1.7orV1.8.zip

07aa2af8d3ecde0127d88bae5922ea60

IPC_V1.8_V1.7.25.zip

3818eb7bb776c04cea217fc11ab7d664

7.1.1.1.1.2-20141129.rar

da44eee6e8a898b3a0d4bb30ab4850b3

UPG_ipc5360a-mw7-M20-hi3518-20160229_115440.ov

fe59952b36113ac4649a8b88bfe81c43

UPG_ipc3360a-w7-M20-hi3518-20160229_173554.ov

565b97d2550ad41fcfec30f79c755df0

update.bin

1013742fad39a062133fe79823467d7a

UPG_ipc5360a-mw7-M20-hi3518-20160229_115440.ov,1UPG_ipc5360a-mw7-M20-hi3518-20160229_115440.ov

2677e6b63430c353f389b74ffd89aae6

UPG_ipc2360a-w7-M20-hi3518-20160229_173606.ov

0e751df5b855e2a5fafc1c63b57a5ca3

TRENDnet

FW_THA-103AC_v11.00_F-20170120.zip,fw_tha-103ac_v11.00_f-20170120.zip,FW_THA-103AC_v1(1.00_F-20170120).zip

ec3a19c62e3c22ba84181644e4689128

fw_tha-1011.03.zip,FW_THA-1011.03.zip,FW_THA-101(1.03).zip

e5c3f7c46ef8a502344572593619a750

fw_tha-103ac1.00.zip

bbaa750e3d63e46a866802e382a07ea9

fw_tha-1011.02.zip

7ea42a34a32eff3a38b5629ec195222b

fw_tha-103ac1.00.zip

ab811e0765422dafde49ad4dc8423ec0

Xiaomi

小方摄像头fimware3.0.3.56.bin, 1533537292_FIRMWARE_660R.bin

12c424a07178dceedb4b05130f736757

update-xmen@T38.zip

1faf0be28092e086661335e32985c975

华来小方智能摄像机1s_iSC5_GD25Q127C@SOIC8.BIN

78e0b13a86c3f10aca3b1b9689a69702

update-entrapment.zip

51dd901e0fa74f9ae86a47651077677d

update-braveheart.zip

fd5d4454b4299340058921c46c8a53c0

update-xmen@T33.zip

b23fb48c6aa130895eef11b8b44da659

update-pulpfiction.zip

bd1c9697c7b5225091446acd4f76e184

Xiaoyi

1.8.6.1B_201604071151home

92ebae2e40e3429df20288428ed8a5bc

1.8.6.1C_201605191103home

58f3017c63a06c15c2bed1232320a8f4

1.8.6.1B_201604071154home

0f1cf844411a7ad6cb4e199948db6cad

1.8.7.0C_201705091058home.zip

8ddc0dc92df07d64d5c1ba5579a67ca0

Zxtech

4channel.zip

637a41dcd27826372fa9d123f67c50c1

16channel.zip

48582a7339e8c367abd56046ea0bc88b

8channel.zip

3db91fa3735f2425245bbd4717990a9c

### 受影响文件MD5列表

文件MD5

版本号

21a445ca4fb67ee62a2c1de054e726dd

1.6.0.0

feef9f0f58c059e0fdd37886fd1a224b

1.6.0.0

ffb9571e5a648f8e0a0216e4d72f14ba

1.9.1.0

005dacb895a1e1c41003caf54867c81a

1.10.0.0

01123b18eccc20d485a3725bbc80ec51

1.10.0.0

1583a039974e41e66af124d4e86355f3

1.10.0.0

181d9634e933eafb838493fe4b41f833

1.10.0.0

3e235b5abfccadfabdf30ce3f008a04f

1.10.0.0

451ee160faf7a124ba113562d69c3574

1.10.0.0

6256fce8895298c1cce831e9452b1fd0

1.10.0.0

6b66568f55cc2dbe710b9555cb1dce75

1.10.0.0

883028d9d49c0a250fc84dafb878b059

1.10.0.0

95e15985b06eb1061999e841f43efaaf

1.10.0.0

99fdc4e8bd04b34f2b38e42b31136811

1.10.0.0

b38f652b453d87555117222dc228ec74

1.10.0.0

b8de100e817dfb77f5f91574913a3ce0

1.10.0.0

fd981305abfbed96dc0cbfa8a8dd3426

1.10.0.0

a052b2f9fd6187be27832ddb8c0490be

1.10.2.0

de6bfe6ed7d39912e5c689421e0baa92

1.10.2.0

c01ca513705bbd528a4b4067cc083d20

1.10.3.0

50f241d14f729795a502504866cd8e0f

1.10.5.0

404f6654b3f4d0fdeb3ffad186edd52f

1.10.6.0

5fba51216c19cfb5ab1d39019c638f69

1.10.6.0

bfdb398b9345369704f4c76b3dde1253

1.10.6.0

f5a719a7d23dbc8d1d453264e96a65bc

1.10.7.0

0df39fe7e72f4d96a131d25036fa7a06

1.10.8.0

5ca2fac8051f50f8758cfbeee0658015

1.10.8.0

cd78bdb6f1ee8e8f847fe952213c8bb7

1.10.8.0

dbc2cf546e19a8ec16765a67f66c4767

1.10.8.0

eb39ac8ca7f5e6040f60c244add4fa86

1.10.8.0

ecd5499dda5d683f35793d3f8bc8c778

1.10.8.0

d973a70d1e56c5f71b3a276143736e80

1.11.0.0

f9280806c1d2ec32f0f6179308d9031a

1.11.0.0

1db7c71626eb3d1b733b49ebeadfa5ba

1.13.8.0

2e952f594cc8a281f48c554a24178508

1.13.8.0

0dce32ccc3762da8aa1a32ba16556bc4

2.1.3.0

2bcd8e2b01e87cafb39e6b410e11dbe2

2.1.3.0

5a9746a840e718b052daebf58d36c8fc

2.1.3.0

946c9ea3d27a27ca06aefcde7ef42aea

2.1.3.0

befada9cec84f7c40451aaf5837fff88

2.1.3.0

cbd1668205b8d1c75ab4347d93d16791

2.1.3.0

36187135bc585aee68db99b6945f302c

2.1.4.22

dcc0d8da5f469b0b2f18dd75ef02f138

2.1.8.4

32027d9a66a72aa36cc18426748a2705

2.1.8.13

5076bedc539a62ae86a57113ff756ba0

3.0.0.0

98301d359cafa8dfa917716193b30e29

3.0.0.0

bf5f47df9446eb839594582c4bbdf87b

3.0.0.0

f2d33e5215cbacf0a10edc8ce5e794ea

3.0.1.29

bf910c5a1e65db561624e6cdc34047c8

3.1.4.48

b793ceaa8a5995f50ebf2c81a4cfb08e

3.1.5.38

c89218297663c8f76b2bb14490bc2343

3.1.5.38

0d16aefd823b785a1a4ba0d3ff080d66

3.1.10.7

37918d69370eb2f13e222a7dbcec272c

3.1.10.7

3b6dd8f97a5490fe25bba917b2544243

3.1.10.7

4163449993d5b1067796368c5c61a320

3.1.10.7

8d50bc18b0a9e0618984367e6679b96a

3.1.10.7
