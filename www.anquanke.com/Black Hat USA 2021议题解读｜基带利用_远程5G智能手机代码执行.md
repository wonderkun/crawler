> 原文链接: https://www.anquanke.com//post/id/249615 


# Black Hat USA 2021议题解读｜基带利用：远程5G智能手机代码执行


                                阅读量   
                                **38510**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t011d5f53f11f7770cf.jpg)](https://p5.ssl.qhimg.com/t011d5f53f11f7770cf.jpg)



近年来，5G蜂窝网络被广泛应用。设备为了加入5G网络，都必须配备一个5G调制解调器，负责调制信号和执行无线电协议。该组件通常也被称为基带。这些组件非常重要，因为它们负责处理来自无线电网络的不可信数据。<br>
在之前的工作中，科恩实验室研究了上一代网络（2G 3G 4G）的安全调制解调器，并实现了远程无接触的0-click代码执行。<br>
本次Black Hat USA 2021，科恩实验室成员Marco与Xingyu Chen在北京时间8月6日凌晨以线上形式分享了议题**《基带利用：远程5G智能手机代码执行》**。该议题探讨了5G网络发生的变化以及安全性方面的改进，并证明了仍然有可能通过无线的方式攻击5G调制解调器完成远程代码执行。

[![](https://p1.ssl.qhimg.com/t01c9b6730ce95fb751.png)](https://p1.ssl.qhimg.com/t01c9b6730ce95fb751.png)

**议题完整白皮书下载见文末**

### <a class="reference-link" name="%E4%BD%9C%E8%80%85%E7%AE%80%E4%BB%8B"></a>作者简介

**Marco：**<br>
腾讯科恩实验室高级研究员，研究涉猎iOS、Safari、VMWare、基带等多个方向，多次作为核心成员参与Pwn2Own、Mobile Pwn2Own并获得冠军，多次在国际安全会议上进行演讲，包括Black Hat USA, DEF CON, CanSecWest, ZeroNights, Codegate, HITB and ShakaCon等。

[![](https://p3.ssl.qhimg.com/t01211174758baa7ab6.png)](https://p3.ssl.qhimg.com/t01211174758baa7ab6.png)

**Xingyu Chen：**<br>
腾讯科恩实验室安全研究员。主要研究虚拟化和移动安全，曾在不同的云产品和智能手机的低级固件中发现了许多关键漏洞。曾作为A*0*E联合战队选手参加多场CTF比赛，也是DEF CON 28 CTF 决赛总冠军队伍成员。多次在国内外安全会议上进行演讲，包括OffensiveCon、Zer0Con和Tensec等。

[![](https://p3.ssl.qhimg.com/t0153542328a903bb6e.jpg)](https://p3.ssl.qhimg.com/t0153542328a903bb6e.jpg)



## 议题解读

### <a class="reference-link" name="1.%E8%83%8C%E6%99%AF"></a>1.背景

多年来，5G网络和基带的安全问题一直没有得到全面的讨论。我们之前的工作是研究老一代网络的安全性，并研究了市面上多款调制解调器的实现，安全研究员Amat Cama也发表了一项关于老一代网络的研究，展示了如何在pwn2own竞赛上成功地攻破三星Shannon基带。来自Comsecuris的研究分析了三星和英特尔基带的安全性。<br>
建议读者将上述这些研究作为理解和熟悉本文的参考。我们也将对研究背景和5G网络的新概念进行简单描述。

### <a class="reference-link" name="2.%E7%9B%AE%E6%A0%87%E4%BB%8B%E7%BB%8D"></a>2.目标介绍

我们购买了当时可用的几款5G智能手机，他们都支持5G中的“New Radio”。<br>**5G设备区分：**
- 非独立模式（NSA）：该模式使用了5G新无线电，并利用了4G网络的其他组件。
<li>独立模式（SA）：该模式完全实现并使用了5G New Radio和5G网络规范。由于我们认为未来将使用独立模式（SA）作为标准，因此我们决定专注于该模式的研究。<br>
我们的测试设备的SoC为Exynos 980并具有三星Shannon基带。<br>
基带在其自己的ARM Cortex内核上运行自己的固件和RTOS，与运行Android操作系统的应用处理器 (AP) 分开。 AP和基带可以例如通过PCI-e、共享内存或其他方式进行通信。我们从设备的OTA包中恢复了基带固件。基带固件位于modem.bin二进制文件中。解压并找到加载地址后，我们可以在IDA Pro中加载它并开始寻找漏洞。</li>
### <a class="reference-link" name="3.%E5%AE%A1%E8%AE%A1%E8%8C%83%E5%9B%B4%E5%92%8C%E6%BC%8F%E6%B4%9E%E6%8C%96%E6%8E%98"></a>3.审计范围和漏洞挖掘

经过一段时间的5G相关代码审计，我们发现了多处漏洞，在此我们选择了其中最稳定的一个来分享，希望您也会通过它对基带当前的安全状态有所认识。在审计调制解调器固件时，我们发现它仍然缺少Stack cookie保护。因此，考虑到在这种环境中缺乏调试功能，使用传统的栈溢出将使我们的利用更容易。<br>
本文选择的bug是一个栈溢出。它不仅是栈溢出，而且是基带内部XML解析器中的栈溢出。此 XML解析器负责解析从网络到设备调制解调器的IMS消息。

**<a class="reference-link" name="3.1%20%E6%94%BB%E5%87%BB%E8%83%8C%E6%99%AF"></a>3.1 攻击背景**

IMS是4G和5G网络中的专用架构，常用的语音呼叫建立在其之上，稍后我们将看到为什么这对本研究很重要。基带是一个IMS客户端，负责处理VoLTE、VoNR消息，因此它必须能够处理SIP消息，IMS服务器使用这些消息与基带进行通信。<br>**白皮书内查看INVITE消息示例**<br>
SIP 是一种基于文本的类似HTTP的协议，包括标头和内容。 接收方（在本文中为基带）需要解析来自服务器的消息。对于不同的消息，内容不仅可以是键值对，还可以是XML格式的文本。XML是一种复杂得多的数据格式，通常由专用库处理。 以上都为基带引入了一个新的攻击面。

**<a class="reference-link" name="3.2%20%E6%BC%8F%E6%B4%9E"></a>3.2 漏洞**

我们的OTA RCE漏洞在基带的IMS模块。 在解析SIP协议消息的XML内容时，它会调用函数`IMSPL_XmlGetNextTagName` 。<br>
由于我们的目标基带没有调试符号或信息，所以所有的函数名称、类型和函数签名，都是从日志字符串中提取，或是通过逆向工程手动恢复。<br>
我们在这里提供了一个反编译版本，其中省略了一些代码。

```
int IMSPL_XmlGetNextTagName(char *src, char *dst) `{`
    // 1. Skip space characters
    // 2. Find the beginning mark '&lt;'
    // 3. Skip comments and closing tag
    // omitted code
    find_tag_end((char **)v13);
    v9 = v13[0];
    if (v8 != v13[0]) `{`
        memcpy(dst, (int *)((char *)ptr + 1), v13[0] - v8); // copy tag name to dst
        dst[v9 - v8] = 0;
        v12 = 10601;
        // IMSPL_XmlGetNextTagName: Tag name =
        v11 = &amp;log_struct_437f227c;
        Logs((int *)&amp;v11, (int)dst, -1, -20071784);
        *(unsigned __int8 **)src = v13[0];
        LOBYTE(result) = 1;
        return (unsigned __int8)result;
    `}`
    // omitted code
`}`
```

此函数将从src解析XML标记并将其名称复制到dst ，例如`&lt;meta name="viewport" content="width=device-width, initial-scale=1"&gt;`到目标缓冲区。接下来，我们展示反编译函数`find_tag_end`（手动命名）并解释它是如何工作的：

```
char **find_tag_end(char **result) `{`
    char *i;               // r1
    unsigned int v2;       // r3
    unsigned int cur_char; // r3

    for (i = *result;; ++i) `{`
        cur_char = (unsigned __int8)*i;
        if (cur_char &lt;= 0xD &amp;&amp; ((1 &lt;&lt; cur_char) &amp; 0x2601) != 0) // \0 \t \n \r
            break;
        v2 = cur_char - 32;
        if (v2 &lt;= 0x1F &amp;&amp;
            ((1 &lt;&lt; v2) &amp; (unsigned int)&amp;unk_C0008001) != 0) // space / &gt; ?
            break;
    `}`
    *result = i;
    return result;
`}`
```

该函数通过跳过特殊字符来查找标签的结尾，例如空格、‘/’、‘&gt;’、‘?’。在了解整个功能的工作原理后，我们注意到根本没有安全检查。该函数不知道目标缓冲区和源缓冲区有多长。 因此，该函数的所有调用者都可能被传统的缓冲区溢出所利用。通过交叉引用函数`IMSPL_XmlGetNextTagName`,我们发现了数百个调用位置。<br>
它们中的大多数都容易受到攻击，因为源缓冲区是从OTA 消息中获取的，完全由攻击者控制。

### <a class="reference-link" name="4.%20Exploit"></a>4. Exploit

我们选择栈溢出是为了漏洞利用的便捷和可靠。正如我们之前所说，由于没有栈cookie，所以我们可以简单地溢出缓冲区，控制存储在栈上的返回地址，并获得代码执行。<br>
我们终于通过逆向工程找到了一个很好的候选者：

```
int IMSPL_XmlParser_ContactLstDecode(int *a1, int *a2) `{`
    unsigned __int8 *v4; // r0
    int v5;              // r1
    log_info_s *v7;      // [sp+0h] [bp-98h] BYREF
    int v8;              // [sp+4h] [bp-94h]
    unsigned __int8 *v9; // [sp+8h] [bp-90h] BYREF
    int v10;             // [sp+Ch] [bp-8Ch] BYREF
    char v11[136];       // [sp+10h] [bp-88h] BYREF

    bzero(v11, 100);
    v10 = 0;
    v4 = (unsigned __int8 *)*a1;
    v8 = 10597;
    v9 = v4;
    // ------------------%s----------------------
    v7 = &amp;log_struct_4380937c;
    log_0x418ffa6c(&amp;v7, "IMSPL_XmlParser_ContactLstDecode", -20071784);
    if (IMSPL_XmlGetNextTagName((char *)&amp;v9, v11) != 1) `{`
    LABEL_8:
        *a1 = (int)v9;
        v8 = 10597;
        // Function END
        v7 = &amp;log_struct_43809448;
        log_0x418ffa6c(&amp;v7, -20071784);
        return 1;
    `}`
    // omitted code
`}`
```

我们可以很容易地确认变量v11是栈上大小为100的缓冲区。潜在的栈溢出可能发生在这里。 在临近的函数中也能发现类似的问题，例如`IMSPL_XmlParser_RegLstDecode`，`IMSPL_XmlParser_ContElemChildNodeDecode`。根据函数名，我们可以推断触发的标签应该在元素Contact List内。通过向上交叉引用函数来总结调用栈并不困难。

```
IMSPL_XmlParser_RegInfoDecode --&gt; IMSPL_XmlParser_RegInfoElemDecode --&gt; IMSPL_XmlParser_RegLstDecode --&gt; IMSPL_XmlParser_RegistrationElemDecode --&gt; IMSPL_XmlParser_ContactLstDecode
```

这些函数名称很容易理解。我们可以分辨出变异的payload可以通过SIP协议中的NOTIFY消息传递。 一个能让基带崩溃的简单PoC可以从普通的NOTIFY消息构造。<br>
由于payload是以XML格式发送，因此对payload存在限制。<br>
记得上面提到的find_tag_end函数，它会将标签名中的以下字符列入黑名单：`"\x00\x09\x0a\x0d\x20\x2f\x3e\x3f"`。 因此，在编写ROP链和shellcode时我们不能使用所有可用的字符。除此之外，剩下的是ARM平台上的传统pwnable挑战。

**<a class="reference-link" name="4.1%20Exploitation%20Payload"></a>4.1 Exploitation Payload**

**白皮书内查看详细PoC**<br>
利用点为函数`IMSPL_XmlParser_RegLstDecode`，为了避免在 ROP 执行后修复栈帧，并能让基带仍然正常工作，最好选择一个较深的地方来触发栈溢出。 所以registration中的一个元素标签是个不错的选择。<br>
payload结构：

[![](https://p3.ssl.qhimg.com/t01100c4f31eadbe247.jpg)](https://p3.ssl.qhimg.com/t01100c4f31eadbe247.jpg)

**<a class="reference-link" name="4.2%20%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E7%9A%84%E5%8F%AF%E8%A7%86%E5%8C%96%E6%BC%94%E7%A4%BA"></a>4.2 漏洞利用的可视化演示**

为了验证我们是否在目标设备上获得了RCE,我们可以检查手机的ADB日志。它将显示有关蜂窝处理器(CP)如何崩溃的信息。然而，这既不是一种方便的方式，也不是一种很好的视觉效果。因此，我们选择通过在基带内执行shellcode来修改设备的IMEI。按照设计,IMEI不应在手机分发后进行修改。当我们报告整个利用链时，这也被视为一个bug。NVRAM是Non Volatile Memory，用于存储与基带相关的持久化信息。IMEI是存储在基带NVRAM中的一项，但是要修改它的值，首先要知道它的索引。<br>**白皮书内查看IMSSH_GetImei函数示例**<br>
基带中有多个地方调用函数获取IMEI。可以通过逆向函数GetImei来检索索引。在我们的例子中，IMEI1/2的索引分别是`0x39a4/0x39a5`。有了索引，我们就可以通过在shellcode中调用API `pal_RegItemWrite_File` 来修改IMEI。

### <a class="reference-link" name="5.%E6%89%A7%E8%A1%8C"></a>5.执行

**<a class="reference-link" name="5.1%20%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE"></a>5.1 环境配置**

要触发这个 bug，我们需要先搭建一个提供 IMS 服务的网络，然后向基带发送格式错误的短信。 我们的测试环境至少需要一个LTE网络。 虽然它在技术上是一个影响4G和5G的漏洞，但在2020年初，5G的基础设施还没有成熟到足以支持像我们这样的独立研究人员测试其安全性。因此我们决定建立一个支持VoLTE的LTE网络来测试设备。

<a class="reference-link" name="5.1.1%20SDR%20Choice"></a>**5.1.1 SDR Choice**

作为设置基站的首选硬件，我们选择了Ettus USRP B210，这是一种在研究人员中非常流行的SDR无线电设备。

[![](https://p4.ssl.qhimg.com/t0137a9c917162a3bdb.jpg)](https://p4.ssl.qhimg.com/t0137a9c917162a3bdb.jpg)

<a class="reference-link" name="5.1.2%20LTE%20network%20setup"></a>**5.1.2 LTE network setup**

我们使用了大量开源组件和硬件来完成我们的测试，以下是一些较为重要的:
- srsENB: 这是srsLTE中的eNodeB实现。 它负责直接无线连接到移动手机(UE)。
- Open5GS：我们在LTE网络中使用了它的EPC实现。它们是hss、mme、pcrf、pgw、sgw。
- sysmo-usim-tool&amp;pysim：SIM卡编程工具。
- CoIMS&amp;CoIMS_Wiki：修改手机IMS设置的工具。
- docker_open5gs：用于在docker容器中运行具有VoLTE支持的open5gs。
UE能够在适当的LTE网络设置后连接到网络，然后我们可以继续进行IMS服务器设置。在我们的测试中，几乎所有不同厂商的基带对eNodeB的频率都非常敏感。您可以查看设备官方信息以获取其支持的频段，然后为srsENB选择合适的Downlink EARFCN参数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016cc3bb649ff55c08.png)

**<a class="reference-link" name="5.2%20IMS%20server%20setup%20&amp;%20hack"></a>5.2 IMS server setup &amp; hack**

由于该漏洞只能由提供VoIP服务的恶意IMS服务器触发，因此基本的LTE网络不足以触发该漏洞。不幸的是，满足这种需求的基础设施还远未成熟。现有的开源项目Kamailio满足了我们的需求，但还没有在各种设备（包括我们使用的）上进行很好的测试。 需要付出巨大的努力才能使其工作并成功发送有效payload。<br>
VoLTE服务器的基本组件是Rtpengine、FHOSS、P-CSCF、I-CSCF和S-CSCF。 以下是网络拓扑：

```
SUBNET=172.18.0.0/24
HSS_IP=172.18.0.2
MME_IP=172.18.0.3
SGW_IP=172.18.0.4
PGW_IP=172.18.0.5
PCRF_IP=172.18.0.6
ENB_IP=172.18.0.7
DNS_IP=172.18.0.10
MONGO_IP=172.18.0.11
PCSCF_IP=172.18.0.12
ICSCF_IP=172.18.0.13
SCSCF_IP=172.18.0.14
FHOSS_IP=172.18.0.15
MYSQL_IP=172.18.0.17
RTPENGINE_IP=172.18.0.18
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017e5cbbae8f5ae657.png)

IMS(SIP)消息通过TCP或UDP套接字以IP数据的形式承载。因此,客户端会首先选择IPSec来进行消息传输。XML payload只能通过NOTIFY消息携带，因此我们的客户端必须成功REGISTER和SUBSCRIBE。

[![](https://p0.ssl.qhimg.com/t0100577195edf7f529.png)](https://p0.ssl.qhimg.com/t0100577195edf7f529.png)

在进行初步的搭建后，一加6（non-IPSec）、Google Pixel 3（IPSec）可以成功注册VoLTE服务，这意味着我们的环境在高通的芯片上能够很好地工作。但是在使用三星芯片的手机上，整个流程会在注册时失败。<br>
但是这些设备能够使用当地运营商的普通SIM卡注册VoLTE，这让我们对修改Kamailio配置和代码充满希望。 首先要做的是在电话上捕获成功的注册流量。 幸运的是，三星的Sysdump Utility中有一个内置的IMS调试工具IMS Logger，它允许我们查看来自应用程序的IMS流量。 下面是一个正常的注册消息及其响应：

[![](https://p3.ssl.qhimg.com/t010ab4a0d524e61b4a.jpg)](https://p3.ssl.qhimg.com/t010ab4a0d524e61b4a.jpg)

[![](https://p3.ssl.qhimg.com/t01b8019f7a046270a0.jpg)](https://p3.ssl.qhimg.com/t01b8019f7a046270a0.jpg)

[![](https://p2.ssl.qhimg.com/t01bf141c31ee172aae.png)](https://p2.ssl.qhimg.com/t01bf141c31ee172aae.png)

Kamailio和本地运营商之间存在一些差异。 我们并不真正知道哪个字段是注册失败的关键。 我们方法是让它们看起来尽可能相似。

在对Kamailio进行了一些更改后，我们取得了一点进展，我们收到了第二条注册消息。 那么问题就到了服务器端，它并没有提供STATUS 200响应。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01534510ae2cdf63aa.png)

经过调查，我们发现服务器和客户端之间的IPSec不一致。 我们决定从服务器端强制禁用IPSec。以下是我们打的补丁：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0155a2f2b9a1e3f6dc.png)

[![](https://p3.ssl.qhimg.com/t01a88e3dbb63397fa0.png)](https://p3.ssl.qhimg.com/t01a88e3dbb63397fa0.png)

<a class="reference-link" name="5.2.1%E5%8F%82%E8%80%83"></a>**5.2.1参考**

[VoLTE/IMS Debugging on Samsung Handsets using Sysdump \&amp; Samsung IMS Logger](https://nickvsnetworking.com/volte-ims-debugging-on-samsung-handsets-using-sysdump-samsung-ims-logger/)<br>[Reverse Engineering Samsung Sysdump Utils to Unlock IMS Debug \&amp; TCPdump on Samsung Phones](https://nickvsnetworking.com/reverse-engineering-samsung-sysdump-utils-to-unlock-ims-debug-tcpdump-on-samsung-phones/)

**<a class="reference-link" name="5.3.%20Payload%20Delivery"></a>5.3. Payload Delivery**

一旦UE注册并订阅到SIP服务器，服务器将发送NOTIFY消息以提供网络中的基本信息，比如其他UE的联系方式等。而payload会以XML的格式存在于NOTIFY消息中。该消息的负责模块是S-CSCF。这是要修改以生成任意有效payload的函数：

```
str generate_reginfo_full(udomain_t* _t, str* impu_list, int num_impus, str *explit_dereg_contact, int num_explit_dereg_contact, unsigned int reginfo_version);
```

### <a class="reference-link" name="6.%E7%BB%93%E8%AE%BA"></a>6.结论

在这项研究中，我们展示了下一代Android设备配备的5G基带安全状态。尽管在网络功能方面已经发生了演变，但我们看到在安全性方面仍然没有过多进步。正如我们实际上已经展示的那样，一些基带缺乏最基本的安全措施，例如栈cookie保护，这让攻击者能够使用缓冲区溢出等简单攻击无线攻击它们。我们在三年前进行过安全研究，但是至今情况似乎没有太大改善。 我们希望在三年后我们可以再次展示一些研究，在一个更加严格的环境中。

[点击下载议题白皮书](https://keenlab.tencent.com/zh/whitepapers/us-21-Over-The-Air-Baseband-Exploit-Gaining-Remote-Code-Execution-on-5G-Smartphones-wp.pdf)
