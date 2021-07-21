> 原文链接: https://www.anquanke.com//post/id/185912 


# 针对Android的高级SMS钓鱼技术研究


                                阅读量   
                                **458820**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者checkpoint，文章来源：research.checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/advanced-sms-phishing-attacks-against-modern-android-based-smartphones/](https://research.checkpoint.com/advanced-sms-phishing-attacks-against-modern-android-based-smartphones/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01d5f890a641d19ccf.jpg)](https://p0.ssl.qhimg.com/t01d5f890a641d19ccf.jpg)

## 0x00 前言

Check Point研究人员最近发现针对某些Android手机的高级钓鱼攻击技术，涉及到的厂商包括Samsung、Huawei、LG以及Sony。在这种攻击场景中，远程代理可以诱骗用户接受新的手机设置，然后进行后续攻击，比如将互联网流量通过攻击者控制的代理进行路由。

这种攻击技术依赖于OTA配置（over-the-air provisioning）机制，移动网络运营商通常会使用这种机制向新入网的手机部署特定的网络配置。然而在本文中我们可以看到，任何人其实都可以发送OTA Provisioning信息。

OTA Provisioning的行业标准为Open Mobile Alliance Client Provisioning（OMA CP，开放移动联盟客户端配置），其中包括相当有限的一些认证方法，接收端无法验证对方建议的设置是否来自于网络运营商或者来自于仿冒者。我们调查后发现，Samsung、Huawei、LG以及Sony生产的手机（根据2018年的[统计信息](http://gs.statcounter.com/vendor-market-share/mobile/worldwide/)，这几家厂商占有Android手机50%以上的市场份额）允许用户接收基于弱认证的恶意配置信息。与此同时，Samsung手机也允许未认证的OMA CP信息。

我们在3月份向受影响的厂商报告了研究成果。Samsung在5月份的安全维护发行版（SVE-2019-14073）中修复了这种钓鱼漏洞，LG在7月份（LVE-SMP-190006）发布了补丁，Huawei准备在下一代的Mate系列或者P系列手机中加入针对OMA CP的特殊UI提示，Sony拒绝承认该漏洞，表示他们生产的设备遵循OMA CP规范。目前OMA将该问题标记为OPEN-7587，正在跟踪处理。



## 0x01 攻击过程

为了发送OMA CP消息，攻击者需要一个GSM调制解调器（10美元的USB设备或者以调制解调器模式运行的一部手机），利用GSM调制解调器来发送二进制SMS消息。此外还需要一个简单的脚本或者现成的软件，来组装OMA CP消息。

攻击者可以精心筛选CP钓鱼消息，比如通过针对性的自定义文本消息来缩小收件方范围，或者大量发送钓鱼消息，在不引起怀疑的情况下使部分用户上钩。

攻击者可以使用OMA CP，通过OTA方式修改手机端的如下设置：
- MMS消息服务器
- 代理地址
- 浏览器主页及书签
- 邮件服务器
- 用来同步联系人和日历的目录服务器
等等。

在如下演示场景中，我们假设攻击者尝试诱骗受害者将所有流量通过攻击者控制的代理进行路由。

### <a class="reference-link" name="%E6%9C%AA%E8%AE%A4%E8%AF%81%EF%BC%88Samsung%EF%BC%89"></a>未认证（Samsung）

为了攻击使用Samsung手机的用户，攻击者可以向这些用户发送未认证的OMA CP消息，其中指定攻击者控制的一个代理地址。这里要强调的是，攻击者不需要解决身份认证问题，用户只要接受CP请求就会被成功攻击。

[![](https://p0.ssl.qhimg.com/t0182aefb1d2faccd13.png)](https://p0.ssl.qhimg.com/t0182aefb1d2faccd13.png)

图1. Samsung用户看到的未认证CP消息

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8IMSI%E8%BF%9B%E8%A1%8C%E8%AE%A4%E8%AF%81"></a>使用IMSI进行认证

如果攻击者拿到了Huawei、LG或者Sony手机用户的IMSI（International Mobile Subscriber Identity，国际移动用户识别码）信息，那么就可以像攻击Samsung手机用户那样对这些用户发起钓鱼攻击。

IMSI是移动网络上与每部设备的对应的一个64位标识符，从GSM到3G时代一直在使用。该号码用于路由，大致相当于计算机网络中的IP地址概念。用户所使用的IMSI有一定的机密性，但具备如下特点：
- IMSI码需要适用于所有网络运营商，因为路由数据时或者呼叫某个移动用户时需要将移动号码解析为IMSI码。
- 因此，转发和解析IMSI查询（将移动号码转成IMSI，或者相反操作）对于商业供应商来说易如反掌。
- 恶意的Android应用可以通过标准API（`(TelephonyManager)getSystemService(Context.TELEPHONY_SERVICE)).getSubscriberId()`）来读取用户IMSI码（只要应用具备`permission.READ_PHONE_STATE`权限）。在过去3年中，有1/3的Android应用会请求这个权限，因此该操作不会引起用户怀疑。
- 大家可以观察SIM卡，上面会刻有或者印有ICCID信息，而ICCID通常与IMSI相匹配。
OMA CP消息中有一个可选的安全头部，可以用来验证CP的真实性。当使用接收方的IMSI码验证CP后，Huawei、LG以及Sony手机就允许安装恶意设置。需要注意的是，这些手机在提示用户安装CP时，并不会显示该CP的详细信息，并且没有以任何方式来标识CP的发送方。

[![](https://p5.ssl.qhimg.com/t017de29860b6536806.png)](https://p5.ssl.qhimg.com/t017de29860b6536806.png)

图2. Sony用户看到的经过NETWPIN认证的CP消息

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8PIN%E8%BF%9B%E8%A1%8C%E8%AE%A4%E8%AF%81"></a>使用PIN进行认证

如果攻击者无法获得IMSI码，攻击者可以向每个受害者发送两条消息。第一条是文本消息，假装消息来自于网络运营商，要求用户接受经过PIN保护的OMA CP，并且将PIN设置为任意的4位数字。接下来，攻击者向受害者发送经过相同PIN码认证的OMA CP消息。通过这种方式，只要受害者接受CP，输入正确的PIN码，攻击者可以在不掌握IMSI信息的情况下安装CP。

[![](https://p0.ssl.qhimg.com/t01ef957ff96b13e40a.jpg)](https://p0.ssl.qhimg.com/t01ef957ff96b13e40a.jpg)

图3. Huawei用户看到的经过USERPIN认证的CP消息



## 0x02 技术背景

Provisioning是一种配置过程，可以对特定环境中需要正常运行的设备进行配置。OTA Provisioning的最初应用场景就是用来部署运营商指定的配置，比如运营商MMS服务中心地址等。企业也可以使用该功能来部署配置信息，比如向雇员设备部署邮件服务器地址。OMA CP是OMA为OTA配置场景推出的两个标准之一，最早可以追溯到2001年，最新的标准由2009年推出。

我们研究后发现，即使经过十多年的发展，OMA CP中仍然存在一些安全问题。Android的基础版本并不能处理OMA CP消息，但由于OMA CP是OTA Provisioning的行业标准，因此许多厂商定制版支持该功能。该标准中允许（但没有强制要求）CP消息使用USERPIN、NETWPIN或者其他方法进行认证，但这种场景比较少使用。

任何SMS消息（文本消息、MMS、语音邮件通知或者其他消息）都会使用SM-TP（Short Message Transfer Protocol，短消息传输协议，即GSM 03.40）指定的PDU（Protocol Data Unit，协议数据单元）进行发送。GSM PDU中包含OMA CP载荷（payload），其中包括：
- 位于`bearer`层的SM-TP头，指定收件方的手机号码及数据编码方案。
<li>位于`transport`层的UDH（User Data Header，用户数据头），包括：
<ul>
- WDP（Wireless Datagram Protocol，无线数据报协议）头，指定目标端口`2948`（`wap-push`）以及源端口`9200`（`wap-wsp`）；
- 可选的连接信息头：每个PDU对应的用户数据大小限制为140个字节，更长的消息必须被分段传输。
在前面的演示场景中，我们针对Samsung手机设计的（未经认证的）最初PoC中包含如下XML载荷，其中代理地址及端口号已在下图中高亮标出：

[![](https://p3.ssl.qhimg.com/t014933e7ff1ba27a9a.png)](https://p3.ssl.qhimg.com/t014933e7ff1ba27a9a.png)

图4. OMA CP XML载荷

承载该载荷的完整OMA CP会被切分成两条SMS消息，如下图所示：

[![](https://p3.ssl.qhimg.com/t01f7ca619a372c2bdc.png)](https://p3.ssl.qhimg.com/t01f7ca619a372c2bdc.png)

图5. 被切分的OMA CP消息

在WBXML字符串中，代理地址及端口号（使用与图4相同的颜色高亮标出）以非空ASCII字符串形式表示，而字符串定义位于XML中。比如在WBXML中，元素名、`type`及`name`属性值均采用固定大小的1字节值来表示。

WBXML载荷紧跟在WSP头之后，该头部中包括消息认证码，认证码为ASCII十六进制字符串，使用收件方的IMSI计算得出。



## 0x03 总结

在本文中，我们介绍了针对Android手机的一种高级钓鱼技术。攻击者只要拥有廉价的USB调制解调器，就可以利用这种攻击技术，诱骗用户在手机上安装恶意配置。为了攻击存在漏洞的手机，攻击者需要知道受害者的IMSI码。如果Android应用具备`READ_PHONE_STATE`权限，就可以获取IMSI信息。

我们在Huawei P10、LG G6、Sony Xperia XZ Premium以及Samsung Galaxy系列手机上（包括S9）验证了PoC。
