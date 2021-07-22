> 原文链接: https://www.anquanke.com//post/id/100744 


# UnicornTeam：对近期4G LTE曝光多个漏洞的危害解读


                                阅读量   
                                **73895**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0153bed215b6f7de74.png)](https://p5.ssl.qhimg.com/t0153bed215b6f7de74.png)

原文在此：[wp.internetsociety.org](http://wp.internetsociety.org/ndss/wp-content/uploads/sites/25/2018/02/ndss2018_02A-3_Hussain_paper.pdf)

NDSS这篇论文在安全圈引起了广泛的关注和讨论。我们仔细研读了这篇论文，在此表达一些观点。

这是篇学术论文，它的亮点是它提出了一种方法论，用这种方法来分析LTE协议的安全性。这个方法论是非常好的，这也是该论文能入选NDSS的原因。主要是一种协议的符号分析方法。论文中也是这样说的：“To the best of our knowledge, in the context of 4G LTE, the use of symbolic model checking and a cryptographic protocol verifier to reason about rich temporal trace properties is novel. ”。这是论文创新点的核心。

Github上公开的代码，就是这种分析方法的代码。在此不详细讨论这种分析方法。我们主要聊一下发现的漏洞和危害程度。

[![](https://s.secrss.com/images/1db91bfd8b3055b782c2185af4db206a.png)](https://s.secrss.com/images/1db91bfd8b3055b782c2185af4db206a.png)

论文中的Table III列举了通过这种分析方法发现的漏洞，[总共是10个](https://www.secrss.com/articles/1190)。其中有6个，A-1, A-3, P-1, P-2, P-4, D-1，这些都属于拒绝服务攻击。

DoS类攻击，是长期无法解决的问题，即使在5G系统中，仍然有一些不能解决。3GPP曾经讨论过在5G引入证书体系，防止手机连接伪基站。也就是说伪基站发出的广播消息都要携带签名，手机终端能识别出来哪些是伪基站，于是就不会尝试连接，连初始连接的第一条消息都不会发出。但是大部分运营商和设备厂商都认为这个方案太“重”了，没有采用。可能6G的时候还会再讨论。

对于专网设备、物联网设备则考虑拒绝服务攻击引发的问题，毕竟常规的手机等UE设备在掉线后可以通过开启、关闭飞行模式等操作再次连上基站；而专网设备、物联网设备则存在无人值守的问题，一旦遭到拒绝服务攻击，很有可能出现长时间掉线的情况，在部分特殊的场景中设备如果掉线可能会产生比较严重的后果。

另外有三个（A-2， A-4， P-5）可以划分到追踪类威胁。我们知道在2G, 3G, 4G中都有IMSI Catcher, 5G将要解决IMSI Catcher的问题。

特别说一下A-4攻击，Authentication Relay，鉴权中继攻击。这种手法可以伪造手机在网络中的位置，这个是可以被个人利用的。这是中继攻击的原理。就相当于手机与真实网络中间加了两个中继器，真实网络只知道中继器在哪里，不知道手机在哪里。中继攻击的原理在无线安全中经常被用到。比如我们团队之前有做过：<br>[汽车无钥匙进入系统的中继攻击](https://www.wired.com/2017/04/just-pair-11-radio-gadgets-can-steal-car/)<br>[NFC中继攻击](https://media.defcon.org/DEF%20CON%2025/DEF%20CON%2025%20presentations/DEFCON-25-Haoqi-Shan-and-Jian-Yuan-Man-in-the-NFC.pdf)

但是鉴权中继攻击，只能伪造手机的位置，手机的完整性保护和加密保护仍然是没有攻破的，中继器不能解出手机发送的数据内容。原文中也是这样说明的：

> “Unlike a typical man-in-the-middle attack, the adversary in this attack can neither decrypt the encrypted traffic between the victim UE and the core networks, nor can inject valid encrypted traffic unless the service provider blatantly disregards the standard’s security recommendations and choose a weak-/no- security context during connection establishment.”

最后还有一种漏洞，是P-3，,发送假的灾害警报，这个在安全圈是已经知道的，肯定是可以实现的。但此种攻击一般没人做，因为一旦做了，很容易被发现。属于扰乱公共安全的严重行为了。前阵子有个夏威夷的虚假导弹警报的例子，在媒体上可以找到。这种服务叫做ETWS (Earthquake and Tsunami Warning System)，恩……国内目前没有这种服务，所以如果有人在国内收到了这种消息，一定是假的。:D

总的来说，这批漏洞的危害并不是很大，公众不需要过于紧张。



声明：本文来自UnicornTeam，版权归作者所有。文章内容仅代表作者独立观点，不代表安全内参立场，转载目的在于传递更多信息。如需转载，请联系原作者获取授权。
