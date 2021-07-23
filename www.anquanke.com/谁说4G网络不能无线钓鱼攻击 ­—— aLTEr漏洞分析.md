> 原文链接: https://www.anquanke.com//post/id/150488 


# 谁说4G网络不能无线钓鱼攻击 ­—— aLTEr漏洞分析


                                阅读量   
                                **169987**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/dm/1024_386_/t0124b1e3a858bbd057.jpg)](https://p3.ssl.qhimg.com/dm/1024_386_/t0124b1e3a858bbd057.jpg)

## 一、关于无线钓鱼攻击

想必各位喜欢钻研安全技术的小伙伴们，对于WIFI网络的钓鱼攻击套路已经非常熟悉了。攻击者通过在例如星巴克之类的公共WIFI网络，使用同样的预共享秘钥，同样的SSID搭建一个恶意wifi，通过DNS spoof的方式将受害者访问的站点重定向到自己做的钓鱼站点，从而获取用户的密码等关键信息[1]。

然而，最近披露的一个4G协议漏洞，对于LTE网络，也可以达到与WIFI钓鱼攻击类似的攻击效果，甚至威胁更大。下面且看360独角兽安全团队对该漏洞及攻击技巧的详细解析。



## 二、关于LTE用户面漏洞

GSMA 名人堂6月27日发布了该漏洞，独角兽团队第一时间对该漏洞进行了分析，以便各位同行能快速理解该漏洞精髓。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c3097f4ea90574f2.png)

图 1 GSMA CVD 披露

该漏洞是LTE协议标准漏洞，产生原因是LTE标准在制定时为了提高短报文带宽利用率，对于用户面的数据，空口层面仅仅启用了加密，并没有像控制面数据一样，强制进行完整性保护。 这使得通过对运营商LTE网络中eNodeB与终端（手机等）之间的无线链路进行攻击，远程利用此漏洞，可以篡改用户的IP数据报文，作者将这个漏洞命名为ALTER攻击[2]。威胁更大的是，可以在无线电波层面，对LTE用户进行DNS spoof攻击。



## 三、关于LTE空口的用户面与控制面

LTE的控制面用于传输信令，而数据面则用于传输用户的业务数据，例如承载语音通话，网页浏览的IP报文数据。

LTE中加密和完整性保护在PDCP层实现，下面两个图分别为LTE 空中接口（uu接口）控制面和用户面PDCP层功能示意图。

[![](https://p3.ssl.qhimg.com/t011b7bac8873b337c3.png)](https://p3.ssl.qhimg.com/t011b7bac8873b337c3.png)图 2 LTE 控制面PDCP层功能示意图

[![](https://p2.ssl.qhimg.com/t01c306d7f25147ca13.png)](https://p2.ssl.qhimg.com/t01c306d7f25147ca13.png)

图 3 LTE 用户面 PDCP 层功能示意图

对比这两个图，我用红框标记部分，可以看到在LTE空中接口的控制面有加密和完整性保护，而在用户面则只有加密。事实上这个用户面加密在LTE标准中是可选的，当然运营商在部署时通常都会启用加密，但是该漏洞却与是否加密没有任何关系，即便运营商启用了用户面的加密，攻击依然可以成功进行。



## 四、攻击过程及原理

### 4.1   硬件平台[![](https://p4.ssl.qhimg.com/t01593c97d78446cb21.png)](https://p4.ssl.qhimg.com/t01593c97d78446cb21.png)

图 4 LTE 恶意中继示意图

实现这个攻击核心组件是LTE中继（Relay），即在运营商eNodeB 和手机之间插入一个LTE恶意中继，恶意中继由一个伪eNodeB和一个伪UE（终端，类似手机）组成。下行链路中，运营商eNodeB给真实UE（用户手机）发送的数据被伪UE接收，通过伪eNodeB发送给真实UE。上行链路中，真实UE给运营商eNodeB发送的数据则被伪eNodeB接收，通过伪UE发送给运营商的eNodeB。 这样所有真实UE与运营商之间的数据都会通过中继。

### 4.2   实现原理

当LTE网路启用用户面加密时，要发起攻击，首先需要解决的是在空口上绕过加密算法，修改IP报文数据。

**4.2.1    LTE加密原理**

从常规思维看，分组对称加密算法的密文只要被修改一个bit，会导致在解密时，分组中至少一半以上的bits放生变化，这是评价加密算法好坏的一个标准。从这个角度看，在LTE用户面启用加密时，似乎针对密文进行修改，并不会带来什么危害，数据顶多在恶意中继那透明的通过，恶意中继也无法解密，也无法受控的通过篡改密文达到修改明文的目的。然而这个思路对于流式加密并不适用，而LTE用户面数据恰好采用的是流式加密。

[![](https://p4.ssl.qhimg.com/t01bc42584542480b8d.png)](https://p4.ssl.qhimg.com/t01bc42584542480b8d.png)

图 5 LTE 用户面数据加密/解密示意图

如图所示，LTE 的流式加密过程中，秘钥流生成器利用AS key等一系列的参数产生密钥流，秘钥流与明文流异或后得到密文c。解密时则用秘钥流和密文流c异或得到明文m。

加密

Keystream XOR m = c；

解密

Keystream XOR c= m；

发送端和接收端使用相同的AES key 即相同的算法产生keystream。

**4.2.2        绕过加密任意篡改数据包**[![](https://p5.ssl.qhimg.com/t011b1e36c864550ec4.png)](https://p5.ssl.qhimg.com/t011b1e36c864550ec4.png)

图 6 插入攻击者之后的 LTE 用户面数据加密/解密示意图

图6为插入攻击者之后的LTE用户面数据加解密示意图，假定用特定的掩码mask和密文流c异或的到密文流c’，解密的时候得到的明文流为m’。

这个过程可以描述为

mask XOR c = c’;

Keystream XOR c’ = m’;

经过简单推导

Keystream XOR c’ XOR m = m’ XOR m;

Keystream XOR c’ XOR ( Keystream XOR c) = m’ XOR m;

Keystream XOR (Mask XOR c) XOR ( Keystream XOR c) = m’ XOR m;

可得到

Mask = m’ XOR m;

如果知道数据报文的原始明文，就可以得到篡改掩码Mask。 而对于移动数据网络，同一个运营商，同一个区域的DNS一般是固定的，很容易得到，所以大致可以猜测出DNS数据包的明文。然而，要做到DNS spoof攻击，只需要修改UE发送的DNS请求中的IP地址而已，而IP地址在PDCP数据包中的偏移也是固定的，这使得修改操作更容易。现在遗留的问题变为怎么在众多PDCP帧中定位到DNS数据包。

**4.2.3        定位DNS数据包**

DNS请求数据一般比较短，可以尝试通过长度来区分，但是需要注意的是如何将同样短的TCP SYN请求与DNS请求区分开来，作者通过大数据的方式，统计了移动网络中DNS请求的长度分布，分布图如下

[![](https://p0.ssl.qhimg.com/t01bb3dfb04b3e5ca90.png)](https://p0.ssl.qhimg.com/t01bb3dfb04b3e5ca90.png)

图 7 PDCP IP 报文长度分布图

从这个图中可以看到下行DNS请求回应的长度与PDCP其他帧的长度有非常明显的区分度，毫不费力的可以区分出来，而对于上行的DNS请求，则可以通过猜测的方式，即对疑似DNS请求报文修改目标IP地址到自己控制的恶意DNS服务器，观察是否检测到DNS请求回应，如果收到回应，则说明修改的是一个DNS包，这个方法准确率很高。

**4.2.4        IP头检验和的处理**

修改IP后，会导致IP包的校验和改变，这里还得处理校验和，这里作者使用了修改TTL去补偿IP变动以保证整个IP头校验和不变的方法。我们知道TTL会随着IP包经过的路由逐跳减小。而对于上行链路空口截获的IP包从UE出来之后显然还没有经过任何路由，所以TTL还是默认值，这个默认值可以从UE操作系统的TCP/IP协议栈的默认设置中得到。而对于下行链路，我们不知道IP报文从我们的恶意DNS服务器发出后经过了多少路由，修改TTL补偿校验和的方式行不通，这里作者通过修改IP头中的标识区域来做补偿。

**4.2.5        UDP校验和处理**

对于上行链路，由于最终计算UDP校验和的程序显然在攻击者控制的恶意DNS 服务器上，因此可以通过修改协议栈源码的方式直接忽略。

对于下行链路，修改DNS服务器协议栈将UDP校验和直接设为0，DNS回应依然有效。

到此校验和问题解决。篡改LTE用户面数据的坑已经填完，整个攻击的原理也阐述完毕。



## 五、攻击演示

下面是攻击视频关键部分，即获取到受害者用户名，密码的部分

[![](https://p5.ssl.qhimg.com/t0114e51259c3130f71.png)](https://p5.ssl.qhimg.com/t0114e51259c3130f71.png)

图 8 攻击结果图片，获取到受害者用户名及密码

原始视频地址：[https://www.youtube.com/watch?time_continue=1&amp;v=3d6lzSRBHU8](https://www.youtube.com/watch?time_continue=1&amp;v=3d6lzSRBHU8)

<video style="width: 654px; height: 369px;" src="http://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/RGVtb25zdHJhdGlvbiBvZiB0aGUgYUxURXIgYXR0YWNrIGluIGEgY29tbWVyY2lhbCBMVEUgbmV0d29yay5NUDQ=" controls="controls" width="300" height="150">﻿﻿﻿﻿<br>
您的浏览器不支持video标签<br></video>



## 六、威胁范围

由于该漏洞由LTE标准引入，针对于所有从LTE 演变而来的其他网络，例如NB-IOT, LTE-V， 以及未来的5G（依然没有启动强制性的用户面完整性保护），都有影响。

与WIFI下的DNS spoof钓鱼攻击相比，LTE空口DNS spoof实现难度虽然要大得多，但攻击范围却比WIFI要大，LTE攻击并不需要像WIFI攻击一样，需要先破解预共享秘钥，因此抛开实现难度问题，成功率和覆盖面都比WIFI下的钓鱼攻击要强，威胁也更大。

由于该攻击发生于数据链路层，任何上层协议针对DNS可用的防护措施，例如DNSSEC，DTLS等在这里都将失效。唯一解决方案是修改LTE标准。



## 参考文献

[1] 360 PegasusTeam， 聊聊wifi攻击

[http://www.freebuf.com/articles/wireless/145259.html](http://www.freebuf.com/articles/wireless/145259.html)

[2] Breaking LTE on Layer Two David Rupprecht等

[https://www.alter-attack.net/media/breaking_lte_on_layer_two.pdf](https://www.alter-attack.net/media/breaking_lte_on_layer_two.pdf)

[3] LTE用户面介绍  华为技术有限公司

审核人：yiwang   编辑：边边
