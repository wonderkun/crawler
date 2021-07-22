> 原文链接: https://www.anquanke.com//post/id/155294 


# Black Hat USA 2018 Arsenal | GhostTunnel解读


                                阅读量   
                                **183990**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01594c0e9f77303456.png)](https://p3.ssl.qhimg.com/t01594c0e9f77303456.png)

作者：360无线电安全研究院



## 1. 前言

今年是360无线电安全研究院第四次登上世界顶级的安全会议Black Hat，继4月份的HITB阿姆斯特丹站后，来自天马安全团队的柴坤哲、曹鸿健，王永涛带来的GhostTunnel再次入选了以“议题审核严苛”著名的 Black Hat USA 2018，据悉，该会议议题接受率不足20%。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012852f52a64f4fcba.jpg)

Ghost Tunnel是一种可适用于隔离环境下的后门传输方式。一旦payload在目标设备释放后，可在用户无感知情况下对目标进行控制及信息回传。相比于现有的其他类似研究（如WHID，一种通过 Wi-Fi 进行控制的 HID 设备），

Ghost Tunnel不创建或依赖于任何有线、无线网络，甚至不需要外插任何硬件模块。

在BlackHat的演讲中，我们对之前的Ghost Tunnel版本进行了更新，并将源码进行了开源。为了便于新来的读者，我依然会在第2，3小节中进行基础的介绍，便于理解Ghost Tunnel的使用场景及技术原理。在第3小节的末尾部分（3.3，3.4），我将会补充之前未详细介绍的实现部分及本次更新内容。

[![](https://p0.ssl.qhimg.com/t01e40604b7591628f4.png)](https://p0.ssl.qhimg.com/t01e40604b7591628f4.png)

## 2. 背景

在本节中将会介绍“远控木马上线方式”、“网络隔离”、“HID攻击”等相关知识，部分内容引用自其他文章，在小节末将给出原文以便于大家扩展阅读。

### 2.1 远控木马上线方式

说起远控木马，大家可能会想到一大堆耳熟能详的名称，如灰鸽子、冰河、PCshare、Gh0st、白金、凤凰ABC以及Poison Ivy等，在此我们以上线方式的角度对远控木马进行一个简单分类。

– 主动连接型

被控端开启特定端口，主控端通过该主机IP及端口连接到被控端，如3389远程桌面、VNC远程桌面等。

– 反弹连接型

由于主动连接的方式不适用于攻击目标处在内网的环境，许多木马采用反弹型进行上线。与主动连接的方式相反，由主控端监听特定端口，被控端执行木马后反连回主控端。由于该种方式的适用性更广，大部分的木马都采用该方式上线，如利用FTP上线、DNS域名解析上线等。

[![](https://p0.ssl.qhimg.com/t0161ff4cbc65105e9f.png)](https://p0.ssl.qhimg.com/t0161ff4cbc65105e9f.png)

– 通过第三方域名型

出于隐蔽性或者反追踪的目的，有些新型的木马采用第三方网站来进行上线。比如通过知名博客类网站的文章内容及评论区，利用QQ空间、微博、推特的推送内容，甚至笔者还见过利用QQ个性签名来作为上线地址。八仙过海各显神通，利用知名网站的好处是可以绕过某些防火墙的白名单限制。

[![](https://p3.ssl.qhimg.com/t01d4b549d3f4db8fca.png)](https://p3.ssl.qhimg.com/t01d4b549d3f4db8fca.png)

&gt;《木马的前世今生：上线方式的发展及新型上线方式的实现》 http://www.freebuf.com/articles/terminal/77412.html

其实，Ghost Tunnel也可以理解为一种木马的上线方式，只是它更针对于攻击目标处在隔离网络中的场景。

### 2.2 什么是Air Grapping

&gt; Wikipedia: “An air gap, air wall or air gapping is a network security measure employed on one or more computers to ensure that a secure computer network is physically isolated from unsecured networks, such as the public Internet or an unsecured local area network.”

简单来说，Air Grapping是一种用于保护特定网络，采用物理隔离的安全措施，通常被用来防止利用网络连接途径造成的入侵及信息泄漏事件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a08c112e42af0826.png)

隔离网闸是常见的一种形态，其原理为：切断网络之间的通用协议连接；将数据包进行分解或重组为静态数据；对静态数据进行安全审查，包括网络协议检查和代码扫描等；确认后的安全数据流入内部单元；内部用户通过严格的身份认证机制获取所需数据。其经常被使用在涉密网与非涉密网间。

攻击者无论是想利用操作系统、应用软件、通信协议的漏洞，都需要通过网络触碰目标机器，而网络隔离环境中就将这条路给封住了。不过凡事没有绝对，一些大新闻告诉我们利用恶意USB就是一种具有可操作性的攻击方式，以下就是几个针对隔离网攻击的案例。

**震网病毒 Stuxnet Worm**

[![](https://p3.ssl.qhimg.com/t012b40bf4ad50e8dc5.png)](https://p3.ssl.qhimg.com/t012b40bf4ad50e8dc5.png)

著名的震网病毒便利用了USB的方式将病毒传入隔离网络，随后将病毒传播到网络中的其他设备。在适当的时候给工控机器下发错误指令，导致机器异常直至报废。最终震网病毒导致伊朗的核计划被迫延迟至少两年。

**水蝮蛇一号 COTTONMOUTH-I**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01565d9c50ea2a137b.png)

在斯诺登披露的NSA秘密武器中包含了该工具，其内部包含了一套 ARMv7 芯片和无线收发装置。当它插入目标主机后，植入恶意程序并创建一个无线网桥，配套的设备可通过RF信号与其进行交互，传输命令及数据。同样，它被NSA用于攻击伊朗的秘密机构，从物理隔离的设备中窃取数据长达数年。

### 2.3 HID攻击

HID是Human Interface Device的缩写，由其名称可以了解HID设备是直接与人交互的设备，例如键盘、鼠标与游戏杆等。不过HID设备并不一定要有人机接口，只要符合HID类别规范的设备都是HID设备。一般来讲针对HID的攻击主要集中在键盘鼠标上，因为只要控制了用户键盘，基本上就等于控制了用户的电脑。攻击者会把攻击隐藏在一个正常的鼠标键盘中，当用户将含有攻击向量的鼠标或键盘，插入电脑时，恶意代码会被加载并执行。

**Teensy**

攻击者在定制攻击设备时，会向USB设备中置入一个攻击芯片，此攻击芯片是一个非常小而且功能完整的单片机开发系统，它的名字叫TEENSY。通过TEENSY你可以模拟出一个键盘和鼠标，当你插入这个定制的USB设备时，电脑会识别为一个键盘，利用设备中的微处理器与存储空间和编程进去的攻击代码，就可以向主机发送控制命令，从而完全控制主机，无论自动播放是否开启，都可以成功。

[![](https://p1.ssl.qhimg.com/t0187c22708708b9bff.png)](https://p1.ssl.qhimg.com/t0187c22708708b9bff.png)

**USB Rubber Ducker**

简称USB橡皮鸭，是最早的按键注入工具，通过嵌入式开发板实现，后来发展成为一个完全成熟的商业化按键注入攻击平台。它的原理同样是将USB设备模拟成为键盘，让电脑识别成为键盘，然后进行脚本模拟按键进行攻击。

[![](https://p0.ssl.qhimg.com/t01ccaadd56216be746.png)](https://p0.ssl.qhimg.com/t01ccaadd56216be746.png)

**BadUSB**

Teensy和橡皮鸭的缺陷在于要定制硬件设备，通用性比较差。但是BadUSB就不一样了，它是在“USB RUBBER DUCKY”和“Teensy”攻击方式的基础上用通用的USB设备（比如U盘）。BadUSB就是通过对U盘的固件进行逆向重新编程，相当于改写了U盘的操作系统而进行攻击的。

**BashBunny**

[![](https://p0.ssl.qhimg.com/t0158ab03d75944018f.png)](https://p0.ssl.qhimg.com/t0158ab03d75944018f.png)

可以发动多种payload是这款设备的一大特色。将开关切换到相应payload选择（上图中的Switch Position 1/2），将Bash Bunny插入目标设备，观察LED灯的变化就能了解攻击状态。在硬件方面，设备中包含1颗四核CPU和桌面级SSD，Hak5介绍说此设备从插入到攻击发动只需要7秒。此外，这款Bash Bunny设备实际上拥有Linux设备的各种功能，通过特定串口可访问shell。绝大部分渗透测试工具的功能都能在其中找到。

**DuckHunter**

在Kali Linux NetHunter中提供了该工具。它可以将USB Rubber Ducky的脚本转化为NetHunter 自有的HID Attacks格式，由此我们将刷有Nethunter的Android设备通过数据线与电脑相连便能模拟键盘进行输入。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010039287dd0cde16c.png)

**WHID**

WHID就是WiFi +HID的组合，WHID注入器顾名思义就是对HID攻击进行无线化攻击时的一种注入工具，通过在USB设备上提供WiFi功能以供远程控制。

[![](https://p2.ssl.qhimg.com/t016ff254ce2e8a1f9a.png)](https://p2.ssl.qhimg.com/t016ff254ce2e8a1f9a.png)

&gt;《HID攻击之TEENSY实战》

[http://blog.topsec.com.cn/ad_lab/hid%E6%94%BB%E5%87%BB%E4%B9%8Bteensy%E5%AE%9E%E6%88%98/](http://blog.topsec.com.cn/ad_lab/hid%E6%94%BB%E5%87%BB%E4%B9%8Bteensy%E5%AE%9E%E6%88%98/)

&gt;《新的U盘自动运行——BadUSB原理与实现》

[https://security.tencent.com/index.php/blog/msg/74](https://security.tencent.com/index.php/blog/msg/74)

&gt;《据说是“最先进的USB攻击平台”》

[http://www.freebuf.com/news/128788.html](http://www.freebuf.com/news/128788.html)

&gt; 《DuckHunterHID for mac》

[http://www.ggsec.cn/DuckHunterHID.html](http://www.ggsec.cn/DuckHunterHID.html)

&gt; 《WHID注入器：在无线环境下实现HID攻击的最新利器》

[http://www.4hou.com/technology/4565.html](http://www.4hou.com/technology/4565.html)

## 3. Ghost Tunnel

对于隔离网络的攻击一般有两个步骤：

1. 在目标系统植入恶意软件

2. 建立数据通道，(infiltrate &amp; exfiltrate)，以便执行命令和窃取数据。

根据之前的案例可以看到，任何可以承载数据的媒介都是可以用来建立数据通信的通道。Ghost Tunnel便是一个利用WiFi信号的隐蔽传输通道。

[![](https://p1.ssl.qhimg.com/t011abd3f13bcf49c28.png)](https://p1.ssl.qhimg.com/t011abd3f13bcf49c28.png)

首先，以HID攻击为例：我们使用BashBunny或者DuckHunter等HID工具将恶意程序植入受害者设备，比如一台Windows笔记本。随后恶意程序将使用受害者设备的**内置无线通信模块**与另一台由攻击者控制的设备建立端到端的WiFi传输通道。此时，攻击者就可以远程执行命令并窃取数据。

演示效果如下：

[https://v.qq.com/x/page/a0647p75qrp.html](https://v.qq.com/x/page/a0647p75qrp.html)

值得注意的是，Ghost Tunnel指的是通过利用受害者设备自身的无线模块来建立传输通道的一种方式，其并不仅局限于使用HID攻击来植入恶意程序，实际上以其他方式植入也是可行的。

### 3.1 优势

Ghost Tunnel的实现方式具有这几个优势：

– HID设备只用于植入攻击代码，当植入完成就可以移除了。（HID攻击外的其他植入方式也是可以的）

– 没有正常的网络流量，可以绕过防火墙检测。

– 不会对现有的网络通信及连接状态造成影响。

– 跨平台支持。该攻击可用于任何拥有WiFi模块的设备，我们在Win7、Win10、Mac OSX、Linux上进行了测试。

– 可支持最高256个受控端.

– 可在50米内工作，配合信号桥接设备理论上可做到无限远。

### 3.2 原理

在正常的Wi-Fi通信中，一个站点必须经历Beacon，Probe，Authentication，Association等过程后才能建立与接入点的连接，其整个流程如下图。

[![](https://p3.ssl.qhimg.com/t01479f08ce9dd4f6b2.png)](https://p3.ssl.qhimg.com/t01479f08ce9dd4f6b2.png)

而Ghost Tunnel并没有使用正常的Wi-Fi连接，而只用到了Beacon、Probe 帧，如下图。

[![](https://p5.ssl.qhimg.com/t01d57544e64848cf93.png)](https://p5.ssl.qhimg.com/t01d57544e64848cf93.png)

为什么用这三个帧呢？在802.11的状态机中，取决于认证和关联的状态，一共有三个阶段。

[![](https://p0.ssl.qhimg.com/t01c92eb2915da7f510.png)](https://p0.ssl.qhimg.com/t01c92eb2915da7f510.png)

在State 1时，客户端处于Unauthenticated、Unassociated状态。而该阶段可以使用的802.11帧有以下具体几种，其中就包含了Probe Request，Probe Response，Beacon帧。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d9d12cc18a3c65e8.png)

原本它们被使用在无线网络扫描阶段。当802.11客户端在扫描可用无线网络时，有两种扫描方式：

– 主动扫描，客户端主动发送Probe Request，接收由接入点返回的Probe Response。

– 被动扫描，客户端在每个频道监听AP周期性发送的Beacon。

[![](https://p1.ssl.qhimg.com/t016b50ea9fc46c4086.png)](https://p1.ssl.qhimg.com/t016b50ea9fc46c4086.png)

总而言之，Ghost Tunnel通过Probe，Beacon帧来进行通信，并不建立完整的WiFi连接。

首先攻击者创建一个具有特殊SSID的AP，攻击者和受害设备都使用它作为通信的标识符（而不是常规WiFi通信中的MAC）。此时，攻击者通过解析受害者设备发出的Probe帧得到数据；受害者设备上的恶意程序将解析攻击者发出的Beacon帧来执行命令并返回数据。这便是Ghost Tunnel WiFi隐蔽传输通道的秘密。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010c494f599c165cb5.png)

### 3.3 更新及开源

配合着本次在Black Hat上的分享，我们对Ghost Tunnel进行了以下更新：

– 除了远程shell外，还添加了文件下载功能

– 优化了传输效率

– 可自行添加其他需要的功能

同时，我们将Ghost Tunnel的服务端与Windows受控端部分进行了开源：

[https://github.com/360PegasusTeam/GhostTunnel](https://github.com/360PegasusTeam/GhostTunnel)，读者可自行下载编译安装，搭建实验环境。

[![](https://p4.ssl.qhimg.com/t0190552293857903d2.png)](https://p4.ssl.qhimg.com/t0190552293857903d2.png)

[![](https://p3.ssl.qhimg.com/t0110c495381f5ee270.png)](https://p3.ssl.qhimg.com/t0110c495381f5ee270.png)

[![](https://p0.ssl.qhimg.com/t019ea5d516675d5f1a.png)](https://p0.ssl.qhimg.com/t019ea5d516675d5f1a.png)

### 3.4 实现

前面提到，控制端与被控端采用Beacon和Probe Request帧进行通信，通信数据嵌入到Information Elements 的SSID和Vendor  Specific元素中，使用一个字节的标识符进行数据识别。

[![](https://p3.ssl.qhimg.com/t01fec125a7538757e1.png)](https://p3.ssl.qhimg.com/t01fec125a7538757e1.png)

[![](https://p4.ssl.qhimg.com/t013a614d7629018410.png)](https://p4.ssl.qhimg.com/t013a614d7629018410.png)

[![](https://p0.ssl.qhimg.com/t01f3456ba0a8eafc92.png)](https://p0.ssl.qhimg.com/t01f3456ba0a8eafc92.png)

在控制端，使用到了aircrack-ng项目中的osdep模块，并利用一块具有“监听模式”和“包注入”功能的无线网卡进行数据收发。相关底层原理可参考下图进行了解：

[![](https://p1.ssl.qhimg.com/t0161e9a32c16c6ee9f.png)](https://p1.ssl.qhimg.com/t0161e9a32c16c6ee9f.png)

在Windows被控端中，通过Windows Native WiFi API来操作Windows设备的无线网卡进行数据收发。关于windows的802.11软件架构可参考此图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010afd92da4ce151fe.png)

** 代码架构设计**

控制端和被控端总体依照数据流向采用模块化设计。

[![](https://p3.ssl.qhimg.com/t014830c11d51a119d9.png)](https://p3.ssl.qhimg.com/t014830c11d51a119d9.png)

控制端：

“`

gt_common.h：数据格式等相关定义

gt_server类：负责初始化及总体功能控制

gt_console类：负责控制台的输入输出

edit目录：hostapd项目关于console的操作功能

packet目录：mdk4项目（自家项目）关于802.11数据帧组装部分的功能

libwifi目录：aircrack-ng中osdep数据收发功能，kismet wifi网卡控制功能

“`

Windows被控端：<br>
“`

wtunnel类：数据收发功能<br>
data_handler类：数据处理及功能<br>
“`

通信数据格式如下：

```
```

typedef struct _tunnel_data_header

`{`

           unsigned char flag;                  // tunnel 数据标志

           unsigned char data_type;     // 数据类型

           unsigned char seq;                 // 发送数据包编号

           unsigned char client_id;         // 被控端ID

           unsigned char server_id;       // 控制端ID

           unsigned char length;            // 数据长度

`}`tunnel_data_header;

```
```

基于传输效率的考虑，代码中并没有对数据进行确认及校验，只是对重复的数据进行了过滤。

数据类型定义：

```
```

#define TUNNEL_CON              0x10   // 建立连接

#define TUNNEL_SHELL            0x20   // Shell功能

#define TUNNEL_FILE                0x30   // 文件下载功能

#define DATA_IN_VENDOR   0x80// 发送数据不超过32字节，只填充SSID，超过32字节会填充Vendor  Specific

typedef enum _TUNNEL_DATA_TYPE

`{`

           TUNNEL_CON_CLIENT_REQ = 0x11,

           TUNNEL_CON_SERVER_RES,

           TUNNEL_CON_HEARTBEAT,

           TUNNEL_SHELL_INIT = 0x21,

           TUNNEL_SHELL_ACP,

           TUNNEL_SHELL_DATA,

           TUNNEL_SHELL_QUIT,

           TUNNEL_FILE_GET = 0x31,

           TUNNEL_FILE_INFO,

           TUNNEL_FILE_DATA,

           TUNNEL_FILE_END,

           TUNNEL_FILE_ERROR,

`}`TUNNEL_DATA_TYPE;

```
```

## 4. 后记

在Ghost Tunnel的实现中，我们使用到了以下项目的部分代码，在此对它们表示感谢。

– Aircrack-ng [https://github.com/aircrack-ng/aircrack-ng](https://github.com/aircrack-ng/aircrack-ng)

– hostapd [http://w1.fi/hostapd](http://w1.fi/hostapd)

– Kismet [https://github.com/kismetwireless/kismet](https://github.com/kismetwireless/kismet)

– MDK4 [https://github.com/aircrack-ng/mdk4](https://github.com/aircrack-ng/mdk4)

&gt; PS：MDK4是MDK3项目的新版本，增加了对5GHz WiFi及其他功能的支持，目前由PegasusTeam维护。

[![](https://p1.ssl.qhimg.com/t014659ca69ec0ec320.png)](https://p1.ssl.qhimg.com/t014659ca69ec0ec320.png)

最后分享一些现场照片，让大家感受一下BlackHat的气氛。

Arsenal区入口：

[![](https://p2.ssl.qhimg.com/t01fd12afdcc6cfc245.png)](https://p2.ssl.qhimg.com/t01fd12afdcc6cfc245.png)

认真准备中：

[![](https://p3.ssl.qhimg.com/t01e295aeb74a73c37e.png)](https://p3.ssl.qhimg.com/t01e295aeb74a73c37e.png)

演示进行中：

[![](https://p2.ssl.qhimg.com/t01fc1ac09f53edaa7b.png)](https://p2.ssl.qhimg.com/t01fc1ac09f53edaa7b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c53660a1f9c0182a.png)

[![](https://p0.ssl.qhimg.com/t01ebf7085d591b3ede.png)](https://p0.ssl.qhimg.com/t01ebf7085d591b3ede.png)

现场有一位一直站在最后认真做笔记的小哥哥，我就用他来结束本文吧

[![](https://p2.ssl.qhimg.com/t01a4cd3de1d1b6571f.png)](https://p2.ssl.qhimg.com/t01a4cd3de1d1b6571f.png)
