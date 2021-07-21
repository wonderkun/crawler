> 原文链接: https://www.anquanke.com//post/id/206579 


# S7CommPlus协议研究


                                阅读量   
                                **207328**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01a7ad8a9554d430d1.jpg)](https://p1.ssl.qhimg.com/t01a7ad8a9554d430d1.jpg)



## 1、概述

最近入手了一个新版本西门子S7-1200PLC，固件版本为V4.2.3，通信协议为S7comm-Plus，已经全面支持通信过程的认证和数据加密。其实，早在2016年4月PLC蠕虫被提出之后，V4.0及其之后的固件版本已全面启用S7comm-Plus协议，安全性有较大的提升，简单粗暴的重放攻击再也不那么凑效了。2019年8月的blackhat大会上，以色列研究人员成功开发出模拟TIA Portal的伪工作站，可成功与新版本的西门子PLC（S7-1200、S7-1500）进行交互，并进行启/停、逻辑篡改等各种操作，这似乎意味着PLC蠕虫在高版本的PLC中同样可以实现。

要实现对新版本PLC的攻击，研究S7comm-Plus协议、理解整个通信握手、认证加密过程是必经之路，国内绿盟、启明已通过对核心通信DLL文件进行逆向分析，实现了对PLC的启/停攻击。通过对blackhat2017、2019的相关论文的研读，发现要理解整个过程还得有点密码学的基础，通过多次试验及对论文的理解，对S7comm-Plus协议有了一些个人理解，形成本文章以供交流学习，不足之处望指正以促共同进步。



## 2、环境配置

整个试验研究的基本环境配置如下：Win7x64虚拟机、

PLC：S7-1200, 6ES7 212-1BE40-0X0B

Firmware: V4.2.3

Software：TIA Portal V14

S7Comm-Plus Wireshark dissector plugin: V0.0.8

[![](https://p1.ssl.qhimg.com/t0123a82df84c651a9a.png)](https://p1.ssl.qhimg.com/t0123a82df84c651a9a.png)

文章中将协议分为了P2-、P2、P3等三个版本，不同版本的TIA Portal软件与不同PLC组合，通信使用了不同的协议版本：

[![](https://p2.ssl.qhimg.com/t015393680af675dd35.png)](https://p2.ssl.qhimg.com/t015393680af675dd35.png)

按照此种分类方法，我的研究环境中使用的是P2-版本协议，但是通信数据中很明显是P3版本的协议：

[![](https://p2.ssl.qhimg.com/t01294fb08d5b7e84c4.png)](https://p2.ssl.qhimg.com/t01294fb08d5b7e84c4.png)

经与作者、西门子求证，新版本的S7-1200PLC均使用了P3版本协议。另外，配置了TIA Portal V13、V14、V14SP1、V15等4个版本进行了比较，得出以下基本结论：1、固件版本为V4.2及其以上的S7-1200PLC，必须使用V14及其以上的TIA Portal进行配置（V13只支持到V4.1版本固件）；2、V13同时支持32位和64位操作系统，V14及其以上只支持64位系统了；3、V14不Win10系统；4、V14、V14SP1版本的核心通信DLL（OMSp_core_managed.dll）版本相同，V15的版本已更新，V13、V14、V15三个版本的TIA Portal对应的此DLL详细信息如下：

[![](https://p4.ssl.qhimg.com/t014e85a0ee54a94846.png)](https://p4.ssl.qhimg.com/t014e85a0ee54a94846.png)

[![](https://p5.ssl.qhimg.com/t01f92b31e3b7cfb506.png)](https://p5.ssl.qhimg.com/t01f92b31e3b7cfb506.png)

[![](https://p0.ssl.qhimg.com/t0127e3ff3530e8e171.png)](https://p0.ssl.qhimg.com/t0127e3ff3530e8e171.png)

因此，可根据目标PLC固件版本选择合适的TIA版本进行安装。



## 3、通信过程分析

### 3.1、握手过程

S7Comm-plus协议的TCP/IP实现依赖于面向块的ISO传输服务，其OSI模型如下：

[![](https://p3.ssl.qhimg.com/t01f832d0cefbf3bf81.png)](https://p3.ssl.qhimg.com/t01f832d0cefbf3bf81.png)

继承了上一个版本中引入“session id”来防重放攻击，新版本的协议中更是引入了密钥保护、数据加密的机制，且对每一个带有操作功能的数据包均实行加密，由此更加有效应对重放攻击、中间人攻击、会话劫持等攻击。上位机（TIA）与PLC通信交互的基本过程如下图所示：

[![](https://p2.ssl.qhimg.com/t014eb86fa7a76aef91.png)](https://p2.ssl.qhimg.com/t014eb86fa7a76aef91.png)

1、Handshake initiation: 通信握手初始化，即CR/CC数据包部分；

2、Challenge: TIA与PLC建立S7Comm-Plus Connection，PLC端生成20个字节随机数，反馈给TIA端；

3、StructSecurityKey: TIA与PLC建立S7Comm-Plus Connection，TIA端根据随机数（Challenge）并结合公钥，生成认证数据；

4、ACK：TIA与PLC建立S7Comm-Plus Connection，PLC端使用私钥对认证数据（StructSecurityKey）进行解密，认证成功后，回复TIA端OK,通信建立成功；

5、Function：TIA端向PLC发送带有功能操作的数据（如PLC启/停）；

以上每一个步骤的数据交互中，均带有相同的“session id”，对通信过程进行抓包，具体数据如下所示：

[![](https://p2.ssl.qhimg.com/t01d6a33d65e1baaca6.png)](https://p2.ssl.qhimg.com/t01d6a33d65e1baaca6.png)

[![](https://p4.ssl.qhimg.com/t01be08b37699ad637d.png)](https://p4.ssl.qhimg.com/t01be08b37699ad637d.png)

对通信建立过程（即S7Comm-Plus connection）中的认证过程进一步分析：

[![](https://p4.ssl.qhimg.com/t012f1c1d3c5ed66957.png)](https://p4.ssl.qhimg.com/t012f1c1d3c5ed66957.png)

1、TIA向PLC发送M1开启会话，使用了“CreateObject”功能码创建了“ClassServerSession”的对象：

[![](https://p5.ssl.qhimg.com/t0143a10f5158672e2d.png)](https://p5.ssl.qhimg.com/t0143a10f5158672e2d.png)

2、PLC响应TIA的请求，回复M2，M2包含 PLC固件版本和20个字节的随机数ServerSessionChallenge，同时包含了session id：

[![](https://p0.ssl.qhimg.com/t01f6896cc4cd4e25e1.png)](https://p0.ssl.qhimg.com/t01f6896cc4cd4e25e1.png)

3、TIA收到M2后，根据随机数（20个字节的随机数，在实际计算的过程中只选取了中间的16个字节，首位各2个未参与实际计算）并结合公钥，使用了复杂的加密算法（包括基本的异或XOR，Hash如SHA-256，MACs如HMAC-SHA-256、CBC-MAC，AES-CTR mode, AES-ECB mode、ECC）生成认证数据，响应PLC并回复M3，认证数据中需要关注的重点部分为“StructSecurityKey”的结构，该结构中长度为180字节的“SecurityKeyEncryptedKey”又为重中之重字段：

[![](https://p0.ssl.qhimg.com/t01fd89286fa143201f.png)](https://p0.ssl.qhimg.com/t01fd89286fa143201f.png)

[![](https://p3.ssl.qhimg.com/t01f5695fb8854ad81a.png)](https://p3.ssl.qhimg.com/t01f5695fb8854ad81a.png)

4、PLC收到M3后，使用私钥对加密数据进行解密、认证，认证成功则向TIA回复M4数据包（上图中长度为86的数据包）。

5、认证成功之后，TIA向PLC发送带有功能操作的数据包，TIA使用私有算法（使用了会话密钥）对数据包内容计算得到32个字节的IntergrityPart字段，PLC收到功能码数据包后，首先校验IntergrityPart字段，验证通过则执行相应功能码动作。

[![](https://p4.ssl.qhimg.com/t0168d9c270d15678c0.png)](https://p4.ssl.qhimg.com/t0168d9c270d15678c0.png)

### 3.2、加密字段

从基本通信过程可以看出，M3数据包中的加密字段生成是与PLC成功建立通信的关键，随后计算IntergrityPart部分是成功操纵PLC的关键。数据加密的过程是一个复杂的密码学算法实践过程，从上图中可以看出，Wireshark插件已经对数据中的大部分字段进行了正确解释，但是少数字段，如“StructSecurityKey”中的“SecurityKeyEncryptedKey”字段未被完全识别，在此结合文章和实际数据包，对180字节的“SecurityKeyEncryptedKey”中的进行具体识别。

Wireshark识别的结构和文章中对该字段的分解如下图所示：

[![](https://p4.ssl.qhimg.com/t0136cbb5bf744a763e.png)](https://p4.ssl.qhimg.com/t0136cbb5bf744a763e.png)

[![](https://p4.ssl.qhimg.com/t0124e95591379ce361.png)](https://p4.ssl.qhimg.com/t0124e95591379ce361.png)

对实际数据进行进一步分解与对应：

0000ad de e1 feb4 00 00 00 01 00 00 00 01 00 00 00

0010d1 58 ff a4 13 13 c0 7b 01 01 00 00 00 00 00 00

00201a 73 08 1f 09 6b 42 bd 10 01 00 00 00 00 00 00

0030a7 c0 65 16 c5 af f4 ff c6 b8 cb 5d b3 35 3d 44

00404d 48 3b 5da5 48 81 cc 82 85 fd 1a f5 5d 3e 3c

005086 c5 6f ae 5d 59 cb bee6 c9 99 fa 39 f6 3d ac

00603a 12 a5 4d 93 b1 f3 8d c7 46 7a f973 86 90 c0

0070fd 56 f2 ea 4f 7d 7b d7 1d 67 f0 1aa9 9b 46 89

008030 5b d1 bf e8 7e c5 b2 96 5e 55 cd72 4a 96 cc

0090e1 5a 1a 0e 9d 79 12 4f a4 46 f9 0e 4b d7 05 a7

00a0cc 4a a4 3f61 0c c3 b5 d5 bd dd 70 b2 be f0 be

00b0e2 a9 93 ca

Magic byte:0xFEE1DEAD为magic，4个字节为固定不变，且为小端模式；

Length:字段的长度，即为180；

Symmetric key checksum:8个字节，即文章中提到的KDK ID Header；

Public key checksum:8个字节，即文章中提到的Public key ID Header；

此8个字节，对于所有相同型号和固件的S7-1200PLC计算出的结果均相同，因为西门子对同类同型号的PLC使用了相的Public key，而此处的checksum即是Public key计算SHA-256并取前8个字节。在实验中，通过动态调试可以获取S7-1200PLC的Public key如下图内容所示的40个字节：

[![](https://p1.ssl.qhimg.com/t016fff850cb85a95cc.png)](https://p1.ssl.qhimg.com/t016fff850cb85a95cc.png)

文章中亦指明了PLC的Public key信息存储于TIA的安装目录：Siemens/Automation/Portal V14/Data/Hwcn/Custom/Keys) ，但其文件为加密方式存放。

EG1:20个字节；

EG2:20个字节；

通信过程中，TIA随机生成20字节作为PreKey，使用类椭圆曲线加密算法和PLC的Public key加密PreKey，等到内容即为EG1和EG2的内容；

Kxv3:20个字节，此处的内容未被完全理解，即文章中标注的Nonce;

IV:16个字节，AES Counter模式加密的初始数据；

Encrypted Challenge:16个字节，此内容为使用AES-CTR mode对M2中的20个字节随机数中的16个字节，连同IV部分进行加密的结果，即：AES-CTR（Challenge,KEK,IV）

Encrypted KDK：24个字节，使用AES-CTR（Challenge,KDK,IV）计算得到；

Encrypted Checksum: 16个字节，使用AES-ECB（Checksum,ECK），其中，Checksum=TB-HASH（CS,Encrypted KDK,Encrypted Challenge）

对各个加密数据字段进行一一对应和识别之后，回过头再来看整个密钥生成算法和交换过程，思路慢慢变得清晰稍许：

[![](https://p0.ssl.qhimg.com/t014b962bb1e36c19c9.png)](https://p0.ssl.qhimg.com/t014b962bb1e36c19c9.png)

[![](https://p4.ssl.qhimg.com/t015a5c9d7573b285c7.png)](https://p4.ssl.qhimg.com/t015a5c9d7573b285c7.png)

梳理一下整个过程中的关键点：

1、识别输入数据：最明显的输入数据是PLC Public key，这个是可以直接获取的，另外是PreKey,PreKey为TIA随机生成的20个字节随机数，可在动态调试中从内存中抓取；Challenge，可从M2数据中获取；

2、各种复杂的密码算法：关于其中的类椭圆曲线加密算法，使用了一个固定的40个字节key,代表了160位的椭圆曲线点，椭圆曲线的基点G硬编码于OMSp_core_managed.dll文件中，动态调试过程中亦可从内存抓取，S7-1500和S7-1200的分别G如下所示：

[![](https://p0.ssl.qhimg.com/t013a1cf86b8b003507.png)](https://p0.ssl.qhimg.com/t013a1cf86b8b003507.png)

[![](https://p1.ssl.qhimg.com/t01bdd217e2ba528089.png)](https://p1.ssl.qhimg.com/t01bdd217e2ba528089.png)



## 4、总结

基于对西门子最新的S7Comm-Plus通信协议的初步分析，整个过程使用了非常复杂的认证加密手段，想要破解和绕过并非一件简单的事情。但是，由于通信过程中认证是单方面的，即TIA对PLC进行了认证，而PLC未对TIA进行认证，因此可以伪造TIA与PLC建立通信；另外，相类型、固件版本的PLC使用了相同的private-public密钥对，则意味着完成对一个S7-1200的成功攻击，即实现了对所有S7-1200的攻击。

虽然通信过程中的认证加密异常复杂，文章中已经实现了对新版本S7-1500PLC的攻击，攻击思路总结如下：

1、通过动态调试抓取加密认证所需要的输入数据，如TIA产生的随机数和M2返回的Challenge；

2、定位到相应的加密函数；

3、使用加密函数对输入数据进行计算，得到正确的数据包字段，对字段进行组合成完整数据包发往PLC校验。（此处有两种思路：① 文章中指出使用Python的Ctypes模块包裹核心通信DLL：OMSp_core_managed.dll，构造正确的输入参数，实现整个加密认证过程； ② 对加密过程进行动态调试，厘清加密认证过程，定位相关功能函数，同时配合逆向分析将功能函数抠取，构造函数的输入参数，完成整个加密认证过程。）

参考资料：

[1] https://i.blackhat.com/USA-19/Thursday/us-19-Bitan-Rogue7-Rogue-Engineering-Station-Attacks-On-S7-Simatic-PLCs-wp.pdf

[2] https://i.blackhat.com/USA-19/Thursday/us-19-Bitan-Rogue7-Rogue-Engineering-Station-Attacks-On-S7-Simatic-PLCs.pdf
