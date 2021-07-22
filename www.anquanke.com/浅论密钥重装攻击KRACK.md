> 原文链接: https://www.anquanke.com//post/id/152210 


# 浅论密钥重装攻击KRACK


                                阅读量   
                                **251313**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t012721ba67edbbaba1.png)](https://p2.ssl.qhimg.com/t012721ba67edbbaba1.png)

KRACK即为Key Reinstallation Attacks，中文译为密钥重装攻击。是由比利时鲁汶大学信息安全研究人员Mathy Vanhoef提出的一种针对WPA2的攻击方式。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01df52df687ed64930.png)<!--[endif]-->

Mathy Vanhoef

## 时间线
<td valign="top" width="568"><!-- [if !supportLists]-->•      <!--[endif]-->2017.5.19   论文被提交<!-- [if !supportLists]-->•      <!--[endif]-->2017.6.16   向攻击涉及的供应商发出通告<!-- [if !supportLists]-->•      <!--[endif]-->2017.8.28   CERT/CC向所有供应商发出通告<!-- [if !supportLists]-->•      <!--[endif]-->2017.10.15  作者在https://www.krackattacks.com公开披露细节，并演示了一个攻击实例<!-- [if !supportLists]-->•      <!--[endif]-->2017.11.1 论文在CCS会议报告</td>

<!-- [if !supportLists]-->•      <!--[endif]-->2017.8.28   CERT/CC向所有供应商发出通告

<!-- [if !supportLists]-->•      <!--[endif]-->2017.11.1 论文在CCS会议报告

 

## 灵感的来源
<td valign="top" width="568">“Ha. I wonder what happens if that function is called twice.”      athy在写另一篇论文时，注意到WiFi标准中一个安装密钥的函数，通常只会被调用一次，他猜想调用两次将会重置相关参数。</td>

在正式开始介绍之前，为了便于理解，我先给出一些名词。
<td valign="top" width="568"><!-- [if !supportLists]-->•       <!--[endif]-->成对临时密钥(Pairwise Transient Key ,PTK)作为会话密钥。<!-- [if !supportLists]-->•       <!--[endif]-->成对主密钥 (Pairwise Master Key, PMK)<!-- [if !supportLists]-->•       <!--[endif]-->接入端 随机数Anonce<!-- [if !supportLists]-->•       <!--[endif]-->客户端随机数Snonce<!-- [if !supportLists]-->•       <!--[endif]-->临时密钥(Temporal KEY, TK)<!-- [if !supportLists]-->•       <!--[endif]-->预共用密钥(PSK) 同一无线路由器底下的每个用户都使用同一把密钥，区别于[802.1X](https://zh.wikipedia.org/wiki/802.1X)认证服务器来分发不同的密钥给各个终端用户<!-- [if !supportLists]-->•       <!--[endif]-->接收计数器(Receive Sequence Counter,RSC)<!-- [if !supportLists]-->•       <!--[endif]-->信息完整性校验码(MIC)</td>

<!-- [if !supportLists]-->•       <!--[endif]-->接入端 随机数Anonce

<!-- [if !supportLists]-->•       <!--[endif]-->临时密钥(Temporal KEY, TK)

<!-- [if !supportLists]-->•       <!--[endif]-->接收计数器(Receive Sequence Counter,RSC)

 接下来正式开始介绍



## 1  背景知识

### 1.1  WPA的产生

WPA全名为Wi-Fi Protected Access，有WPA和WPA2两个标准，是一种保护[无线网络](https://zh.wikipedia.org/wiki/%E7%84%A1%E7%B7%9A%E7%B6%B2%E8%B7%AF)安全的系统。它是研究者为了解决在前一代的[有线等效加密](https://zh.wikipedia.org/wiki/%E6%9C%89%E7%B7%9A%E7%AD%89%E6%95%88%E5%8A%A0%E5%AF%86)（WEP）系统中找到的几个严重的弱点：
<td valign="top" width="568"><!-- [if !supportLists]-->•        <!--[endif]-->WEP不是强制使用的，使得许多设施根本就没有启动WEP<!-- [if !supportLists]-->•        <!--[endif]-->WEP并不包含[钥匙管理协定](https://zh.wikipedia.org/w/index.php?title=Key_management_protocol&amp;action=edit&amp;redlink=1)，却在用户间共用一个[秘密钥匙](https://zh.wikipedia.org/w/index.php?title=%E7%A7%98%E5%AF%86%E9%91%B0%E5%8C%99&amp;action=edit&amp;redlink=1)。<!-- [if !supportLists]-->•        <!--[endif]-->RC4所用的24比特的IV（初始向量）并没有长到足以担保不会重复</td>

<!-- [if !supportLists]-->•        <!--[endif]-->RC4所用的24比特的IV（初始向量）并没有长到足以担保不会重复

而产生的。商业联盟 Wi-Fi Alliance制定了WPA标准，对WPA标准的实际运用检验从[2003年4月](https://zh.wikipedia.org/wiki/2003%E5%B9%B44%E6%9C%88)开始，并于[2003年11月](https://zh.wikipedia.org/wiki/2003%E5%B9%B411%E6%9C%88)变成强制性。

### 1.2  WPA与802.11i的关系

由于WEP已被证明不够安全，人们需要更安全的加密标准，但制定802.11i的工作比原先预期的久了很多，在大家越来越关心无线安全的同时，该标准的制定花费了四年才完成。芯片厂商已经迫不及待的需要一种更为安全的算法，并能成功兼容之前的硬件，所以，WPA包含了与WEP兼容的802.11i子集合,实现了[IEEE](https://zh.wikipedia.org/wiki/IEEE) [802.11i](https://zh.wikipedia.org/wiki/802.11i)标准的大部分，先于完整的802.11i推出。在完整的802.11i标准于[2004年6月](https://zh.wikipedia.org/wiki/2004%E5%B9%B46%E6%9C%88)通过之后，Wi-Fi Alliance于[2004年9月](https://zh.wikipedia.org/wiki/2004%E5%B9%B46%E6%9C%88)推出了实现了802.11i强制性元素的WPA2。

### 1.3  WPA2的改进

WEP所使用的CRC（[循环冗余校验](https://zh.wikipedia.org/wiki/%E5%BE%AA%E7%8E%AF%E5%86%97%E4%BD%99%E6%A0%A1%E9%AA%8C)）先天就不安全，在不知道WEP密钥的情况下，要篡改所载数据和对应的CRC是可能的，而WPA使用了名为“Michael”的更安全的[消息认证码](https://zh.wikipedia.org/wiki/%E8%A8%8A%E6%81%AF%E8%AA%8D%E8%AD%89%E7%A2%BC)（在WPA中叫做[消息完整性查核](https://zh.wikipedia.org/w/index.php?title=%E8%A8%8A%E6%81%AF%E5%AE%8C%E6%95%B4%E6%80%A7%E6%9F%A5%E6%A0%B8&amp;action=edit&amp;redlink=1)，MIC），WPA2采用了计数器模式密码块链消息完整码协议CCMP（Counter CBC-MAC Protocol），其安全性已被严格地证明了。

WPA仍使用RC4，使用可以动态改变密钥的“临时密钥完整性协议”（Temporal Key Integrity Protocol，[TKIP](https://zh.wikipedia.org/wiki/TKIP)），以及48位的IV。WPA2中RC4被AES取代。



## 2  攻击原理

### 2.1  四次握手

WPA和WPA2均使用802.11i中定义的四次握手，客户端（Station, STA）和接入点（Access Point, AP）通过四次握手相互验证和协商名为成对临时密钥（Pairwise Transient Key, PTK）的会话密钥。PTK通过成对主密钥（Pairwise Master Key, PMK）、AP随机数ANonce、STA随机数SNonce和双方MAC地址等计算生成，其中PMK由登录密码等双方均已知的信息计算生成。而后续正常数据加密所使用的临时密钥（Temporal KEY, TK）即派生自PTK。各密钥、参数的关系如下图所示。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t01c435682741268756.png)](https://p3.ssl.qhimg.com/t01c435682741268756.png)<!--[endif]-->

图 2-1 四次握手中各密钥、参数关系

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p5.ssl.qhimg.com/t012d144e1667499efc.png)](https://p5.ssl.qhimg.com/t012d144e1667499efc.png)<!--[endif]-->

图 2-2 四次握手中所用数据报文格式 <!-- [if !vml]-->[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cb48c9878142f24a.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

图 2-3 四次握手过程

消息1,2与攻击关系不大，略过不提，WPA2所遵循的802.11i标准中规定，AP在发起连接时就安装组密钥GTK,客户端接收到消息3将安装PTK和组密钥GTK,发送消息4作为回应，AP收到消息4安装PTK,未收到消息4将重发消息3.

为了完成密钥重装，攻击者需要嗅探、重放四次握手过程中的第3个消息报文，强制重置协议加密使用到的nonce值及重放计数，重安装加密密钥。而会话密钥与双方MAC地址有关，所以，普通的中间人攻击是无法奏效的，需要运用channel-based MitM技术，伪造同名同MAC不同信道热点。



## 3  不同场景的攻击

### 3.1  接受明文重传消息3，不安装全0密钥<!-- [if !vml]-->[![](https://p0.ssl.qhimg.com/t01b4752dcce8148a82.png)](https://p0.ssl.qhimg.com/t01b4752dcce8148a82.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

攻击者作为中间人，首先放行消息1,2,3，阻塞客户端对消息3的回复消息4。此时客户端安装了PTK,将发送以此PTK加密的数据，nonce为1，攻击者将此数据阻塞。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p5.ssl.qhimg.com/t0190d290912b193be3.png)](https://p5.ssl.qhimg.com/t0190d290912b193be3.png)<!--[endif]-->

AP未接收到消息4，将重发消息3，攻击者将其转发给客户端。客户端重装PTK,此时，攻击者将先前拦下的消息4发送给AP，此后发送的加密数据将重用PTK,且nonce被重置为1

nonce重用引发的后果与所采用的数据保密协议密切相关。三种数据保密协议：
<td valign="top" width="568"><!-- [if !supportLists]-->•      <!--[endif]--> 临时密钥完整性协议TKIP<!-- [if !supportLists]-->•      <!--[endif]--> 计数器模式密码块链消息完整码协议CCMP<!-- [if !supportLists]-->•      <!--[endif]--> 伽罗瓦/计数器模式协议GCMP</td>

<!-- [if !supportLists]-->•      <!--[endif]--> 伽罗瓦/计数器模式协议GCMP

所采用的数据加密算法分别为流密码RC4、认证加密算法AES-CCM和认证加密算法AES-GCM，其中AES-CCM和AES-GCM的加密部分都是基于CTR模式的流式加密。明文数据与算法生成的密钥流按比特逐位异或后得到密文数据。流式加密的问题是在密钥固定的条件下重用nonce时总会生成相同的密钥流。这一特性可以被利用来解密数据包。

    用KeyStream表示密钥流，P1和P2表示两组明文数据，KeyStream，P1，P2具有相同的比特长度，则两组明文对应的密文分别为：

<!-- [if !supportLists]-->•      <!--[endif]--> C1 = P1 ⊕ KeyStream

<!-- [if !supportLists]-->•      <!--[endif]--> C2 = P2 ⊕ KeyStream

攻击者可以通过网络收集到密文C1和C2，如果攻击者知道密文C1对应的明文P1，则可以据此恢复明文P2的信息：

<!-- [if !supportLists]-->•      <!--[endif]-->P2 = C2 ⊕ keystream = C2 ⊕(P1 ⊕ C1)

在实际情况中，通常能找到已知内容的数据包，所以可以认为在密钥固定的条件下重用nonce时获得密文数据包可根据上述过程解密。即使已知内容的数据包确实无法获得，当对消息类型有足够的知识（比如消息为英文字符）的条件下，也可能解密还原出明文。

    WAIT!!!!!!!! AP安装PTK了吗?[![](https://p1.ssl.qhimg.com/t0190d290912b193be3.png)](https://p1.ssl.qhimg.com/t0190d290912b193be3.png)<!--[endif]-->

客户端重装PTK之后，发送的消息4将被加密,而此时AP尚未安装PTK,无法识别，消息4将被丢弃，攻击失败了吗？

    802.11标准表述存在瑕疵：
<td valign="top" width="568">“On reception of message 4, the Authenticator verifies that the Key Replay Counter field value is one that it used on this 4-way handshake.”</td>

注意其表述为“one”，也就是只要先前用过的都行。凡是照此实现的算法，均可用之前的消息4取代。使得攻击者可以完成一个完整的四次握手过程，使AP安装PTK。进而实现对通信数据包的解密。此时，攻击者并不知道实际安装的密钥。



### 3.2  接受明文重传消息3，安装全0密钥

在Linux和Android系统中，实现WPA2的是wpa_supplicant.由于其2.3版本以上对协议的错误实现

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p4.ssl.qhimg.com/t013fe12a4a7fc393ac.png)](https://p4.ssl.qhimg.com/t013fe12a4a7fc393ac.png)<!--[endif]-->

使得安装PTK后将TK置0，客户端再次收到消息3重装密钥时，会从内存中取回TK。在这种情况下，则会导致安装全0密钥TK，使得攻击者不仅能解密数据包，还能进行流量劫持。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t0180b1411c3070f9d5.png)](https://p3.ssl.qhimg.com/t0180b1411c3070f9d5.png)<!--[endif]-->

基本步骤与前例一致，区别只在于此时安装的TK是全0，攻击者知道了TK,可以进行流量劫持，监控并篡改客户端发出的全部数据

### 

### 3.3  接受加密重传消息3（转变为接受明文重传）

在Linux和Android系统中，虽然设定为接受加密重传的消息3，但其也会接受明文重传的消息3，只要重传的消息3紧跟在原始消息3之后。

    无线网卡会将其送入CPU的接收队列中。

    CPU先处理第一条消息3，发出第一条消息4后,发出命令，让无线网卡安装密钥。

    CPU再处理第二条消息3，发出第二条消息4 ，无线网卡使用PTK对其加密。CPU发出命令,无线网卡重装密钥，nonce被重用为1。被转化为接收明文重传消息3。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p2.ssl.qhimg.com/t010cdfd9b2b597deff.png)](https://p2.ssl.qhimg.com/t010cdfd9b2b597deff.png)<!--[endif]-->

图2-7       接受加密重传消息3（被转变为接受明文）

### 3.4  仅接受加密重传消息3

攻击者先等待客户端完成一次完整的四次握手，在第二次的四次握手过程中，阻塞消息3，等待AP重传的消息3到来，一起交付给客户端的无线网卡。

    无线网卡使用当前的PTK将其解密，送入CPU的接收队列。

    CPU先处理第一条消息3，发出第一条消息4后, 发出命令，让无线网卡安装新的密钥PTK’。

    系统并不对对消息3加密的密钥进行检查，所以尽管第二条消息3是用以前的PTK进行的加密，对其不加区别。所以CPU直接发出第二条消息4 ，发出命令，让无线网卡重装密钥，nonce被重用为1.

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t0156763ab3c96abd6a.png)](https://p3.ssl.qhimg.com/t0156763ab3c96abd6a.png)<!--[endif]-->

### 3.5  不听话的孩子幸免于难？<!-- [if !vml]-->[![](https://p4.ssl.qhimg.com/t01dbef04da921814e3.png)](https://p4.ssl.qhimg.com/t01dbef04da921814e3.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

Windows和iOS 违背802.11标准，不接受消息3重传，所以其免疫四次握手攻击。

但是，组密钥握手攻击，Fast BSS（Basic ServiceSet） Transition（FT）握手攻击然有效。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b2c7ef0725697600.png)<!--[endif]-->

最后，我们一起来看一个攻击实例,视频演示可在[https://www.krackattacks.com](https://www.krackattacks.com/)查看

 

## 4 攻击实例

利用安卓设备存在的可被强制安装全0密钥漏洞，获取用户登录名及密码等敏感的个人信息

### 4.1  工具

工具

<!-- [if !supportLists]-->•      <!--[endif]-->探测漏洞是否可用的脚本，

<!-- [if !supportLists]-->•      <!--[endif]-->漏洞利用脚本

<!-- [if !supportLists]-->•      <!--[endif]-->https降级工具sslstrip

<!-- [if !supportLists]-->•      <!--[endif]-->抓包工具wireshark

### 4.2  攻击过程

安卓手机在没有恶意设备接入时连接到WPA2加密的无线网络

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p1.ssl.qhimg.com/t0133bfdbd7b676127f.png)](https://p1.ssl.qhimg.com/t0133bfdbd7b676127f.png)<!--[endif]-->

图4-1       接入加密网络

手机访问macth.com,安卓手机默认开启SSL（安全套接层）

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p5.ssl.qhimg.com/t013963be1c1e38499c.png)](https://p5.ssl.qhimg.com/t013963be1c1e38499c.png)<!--[endif]-->

图4-2       网站开启SSL

启动攻击脚本krack-all-zero-tk.py，各项信息如下
<td valign="top" width="568">真实热点Real AP：Ssid： testnetworkMAC：bc:ae:c5:88:8c:20Channel：6被攻击客户端target：MAC: 90:18:7c:6e:6b:20伪造同名同MAC热点（Rouge AP）：Ssid： testnetworkMAC：bc:ae:c5:88:8c:20Channel：1</td>

MAC：bc:ae:c5:88:8c:20

被攻击客户端target：

伪造同名同MAC热点（Rouge AP）：

MAC：bc:ae:c5:88:8c:20

 <!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t0169ddcc343d325999.png)](https://p3.ssl.qhimg.com/t0169ddcc343d325999.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

图4-3       启动攻击脚本

启动enable_internet_forwarding.sh脚本，使得钓鱼热点可用

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p2.ssl.qhimg.com/t01b676c35b3ee47f5f.png)](https://p2.ssl.qhimg.com/t01b676c35b3ee47f5f.png)<!--[endif]-->

图4-4       使钓鱼热点可用

启动sslstrip,去除SSL保护<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t018f10193aa1831c36.png)](https://p3.ssl.qhimg.com/t018f10193aa1831c36.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

图4-5       去除SSL保护

接下来，使用wireshark抓包，手机再次连接无线网络。<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t01a470d55e438499ed.png)](https://p3.ssl.qhimg.com/t01a470d55e438499ed.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

图4-6       再次连接

此时，手机首先依然连接到真实热点，通过构造CSA(Channel Switch Announcement 信道切换公告)信标(beacon)的方式来强制切换到钓鱼热点。<!--[endif]-->

[![](https://p5.ssl.qhimg.com/t0189818f262c92841c.jpg)](https://p5.ssl.qhimg.com/t0189818f262c92841c.jpg)

<!-- [if gte vml 1]&gt;-->

图4-7       CSA元素格式

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p0.ssl.qhimg.com/t016c986beb4248272f.png)](https://p0.ssl.qhimg.com/t016c986beb4248272f.png)<!--[endif]-->

图4-8       攻击成功

手机再次连接网页，SSL保护已去除<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t01dadd9b35b9e80447.png)](https://p3.ssl.qhimg.com/t01dadd9b35b9e80447.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

图4-9       SSL保护已去除

输入账号密码登录[![](https://p2.ssl.qhimg.com/t01a4c8908e6784c5d4.png)](https://p2.ssl.qhimg.com/t01a4c8908e6784c5d4.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

图4-10 登录

查看wireshark捕获数据<!-- [if !vml]-->[![](https://p0.ssl.qhimg.com/t014a8247ac47102fec.png)](https://p0.ssl.qhimg.com/t014a8247ac47102fec.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

图4-11   WPA2保护已被绕过

审核人：yiwang   编辑：边边 
