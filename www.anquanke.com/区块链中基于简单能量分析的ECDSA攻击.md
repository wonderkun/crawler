
# 区块链中基于简单能量分析的ECDSA攻击


                                阅读量   
                                **668314**
                            
                        |
                        
                                                                                                                                    ![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者xilesou，文章来源：link.springer.xilesou.top
                                <br>原文地址：[https://link.springer.xilesou.top/chapter/10.1007/978-3-030-24268-8_12](https://link.springer.xilesou.top/chapter/10.1007/978-3-030-24268-8_12)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/198376/t0171a34c99e8239dc1.jpg)](./img/198376/t0171a34c99e8239dc1.jpg)



## 0x01 Abstract

区块链的安全性依赖于加密算法。然而由于计算能力提升和侧信道方法的高级密码分析，密码原语通常会被破坏或削弱，区块链的密码算法将面临侧通道攻击。为了加强安全性并提高区块链的性能，比特币矿机基于硬件芯片实现，并且可使用FPGA或ASIC在硬件级别应用诸如Hash函数，ECDSA数字签名之类的加密算法。但是，攻击者在区块链硬设备的攻击策略中有多种选择，包括时序分析，简单能量分析（SPA)，差分能量分析（DPA)和相关能量分析（CPA）等。

本文系统地分析了交易数据数字签名被破坏的威胁，提出了一种针对ECDSA的改进简单能量分析（**SPA，Simple Power Analysis** ），并采用了能量特征模型。给出了一个攻击案例，通过使用带有能量追踪的攻击方法可以恢复ECDSA的私钥。然后通过在区块链硬件设备的倍点运算（**point doubling** ）和加法运算中添加空运算来给出原子级等效能量损耗的对策。



## 0x02 Digital Signature

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011334de7d98489afb.png)

上图显示了区块链的基本数据结构。在比特币中，区块链是已发生的所有比特币交易的公共日志，并组合在一起称为区块。交易使用确定代币所有者的脚本语言。

数字签名被赋予每个交易，并与交易一起存储在区块中。区块链协议中的数字签名方案是验证交易数据是由密钥所有者产生的，并且保证交易数据的完整性。比特币中的数字签名方案是带有secp256kl参数的椭圆曲线数字签名算法（**ECDSA，Elliptic Curve Digital Signature Algorithm** ），如下图所示。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01db68ab1769095171.png)

ECDSA的安全性取决于椭圆曲线离散对数问题（**ECDLP，elliptic curve discrete logarithm problem** ）的难度。也就是说，ECDSA在理论上是安全的。但是随着诸如侧信道方法等高级密码分析的提出，密码算法被破解和削弱，出现了以下两种威胁：

威胁1：如果私钥可以被破解，则对手可以假冒用户并将硬币转移到其他帐户。即未来的交易将被模拟。

威胁2：如果可以计算事务数据上的哈希值，则对手可以获得第二个预映像或产生相同哈希值（碰撞）的值。这导致通过从其他交易数据产生相同的哈希值来对交易数据的排列进行签名。



## 0x03 Security of ECDSA

ECDSA是数字签名算法的椭圆曲线版本。下面的算法1显示了如何计算签名。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019faba318e7ef77ae.png)

如果可以得到秘钥d，则ECDSA被称为完整中断。根据算法1，如果已知签名（r，s）的临时密钥k，则可以根据公式（1）和（2）计算秘密密钥d：

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0112ca50fdb4bbe170.png)

对于ECDSA，如果攻击者能够显示临时密钥k，则实践中可能会破坏ECDSA的实现。给定E（Fq）上的点P和整数k，算法1中的步骤2是标量乘法[k]P，这是ECC最重要和最消耗的运算。

标量乘法可以使用基于左至右二进制NAF（非相邻形式）混合坐标乘法的双加法算法来实现。算法2给出了实验中使用的NAF标量乘法的细节。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015a85055956a4405f.png)

为了避免使用仿射坐标的公式，使用了雅可比（Jacobian）或Jacobian-affine混合坐标。雅可比点（X，Y，Z）对应于仿射点（X /Z²，Y/Z²）。在雅可比坐标系中，无穷大的点为O =（1，1，0）。在雅可比投影坐标系中给出倍增公式，令P =（x1，y1，z1），Q = 2P =（x2，y2，z2）计算如下：

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01081d8643ad5fdc21.png)

为了加快加法速度，Cohen等人引入了修正的雅可比坐标。设P =（x1，y1，z1）由雅可比坐标表示，而Q =（x2，y2，z2）由仿射坐标表示。总和R = Q + P =（x3，y3，z3）计算如下：

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d8144a169858cc4d.png)

由于简单能量分析，标量乘法就受到侧信道攻击技术的影响。如果标量乘法的实现泄漏了临时密钥k的信息，则可能允许揭示秘密密钥d。



## 0x04 Countermeasure of Scalar Multiplication

在实际的攻击环境中，电源走线中不可避免存在噪声。然后可以如下确定密码系统的总功耗：

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012aeef212d41cdedf.png)

其中**P**total是总能量损耗，**P**op是与操作有关的能量损耗，**P**data是与数据有关的能量损耗，**P**el.noise表示由硬件中的电子噪声产生的能量损耗，**P**const是一些恒定能量损耗耗，具体取决于技术实现方式。

根据标量乘法的实现，倍点运算和加法运算主要包括原子级的大整数的模乘，模加，模减，移位和加载日期。从理论上讲，根据汉明权重能量模型，每个操作的能量特性都不相同。当操作的位跳变更大时，能量损耗也更大。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01be041166f357ec9e.png)

可以根据倍加对原子操作进行细分，包括模乘，模加，模减，移位和加载日期，其中模乘表示为**Pop_mod_mul**(a,b)，模加**Pop_mod_add**(a,b)，模减**Pop_mod_sub**(a,b)，移位**Pop_shift**(a)和加载日期**Pop_load**(a)。根据它们的能量特性，它们可以分为三类，如上表所示。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://pic.downk.cc/item/5e3fef0b2fb38b8c3c5371a1.png)

在算法3中，主要有19个用于原子倍加的原子运算，包括8个模数乘法，2个模数加法，3个模数减法，9个移位。在算法4中，点加法具有21个原子运算，包括13个模乘，5个模加，5个模减，5个移位。加倍运算能力**P**op可以表示如下：

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0184772c81427b3aec.png)

根据不同原子级操作的能量特性，能量损耗**P**op在点加和倍点之间有很大的差异，因此能量损耗**P**total是不同的。可以通过每个点操作的**P**High来区分点加和倍点。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0122addbdeb577cd4b.png)



## 0x05 Feature Analysis and Extraction of Power Traces

已知**P**High，**P**Medium，**P**Low的标量乘法的三种类型的能量特性，下图是标量乘法的三种幂特性。由于负载数据出现在两个操作之间，因此负载数据的能量特性明显低于其他操作。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e88a75cf60f7fd2f.png)

点的加法和倍加可以除以每个段的**P**High数。如果段中有8 **P**High，则操作是倍点；如果有13 **P**High，则是点加法或减法，如下图。另外点减法与点加法具有相同的运算过程，但操作数不同。点减法的一个操作数为-P，点加法的操作数为P。负载数据在点减法中需要增加负运算，因此低能量特性**P**Low较宽。可以通过段的前后能量特性**P**Low来判断段是加还是减。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01842f52e437c5212b.png)



## 0x06 An Attack Based on SPA Against Scalar Multiplication

算法2的第四步可以分为三种类型：倍加，倍减，加倍，如下图。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d4c2255398420e3b.png)

当uj = 0时，该操作加倍。

当uj = 1时，操作是倍加。

当uj = -1时，运算为倍减。

可以通过分析标量能量曲线的倍增、倍减来估算关键的NAF（k）值，如下图所示。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0172c6d4e23f6aa508.png)

然后可以通过特征**P**Low提取能量跟踪的每个分段。每个段都表示为Segi，针对标量乘法的SPA步骤如下：

**Step 1：**首先，根据能量特性PLow对能量追踪进行分段，如Seg = {Seg0，Seg1，……，Segn}。

**Step 2：**对数据集Seg，C = {c0，c1，c3}的三个聚类集进行分类，其中聚类c0是倍点，c1是点加法，c2是点减法。<br>
分类原则：对于每个段Segi，如果其具有8 **P**High，则将Segi分为类c0。如果它具有13 **P**High，则当段的**P**low较窄时，Segi分为类c1，而当段的Plow较宽时，Segi分为类c2。

**Step 3：**设置初始值i = 0，j =0。如下，可以获得NAF（k）的键值：<br>
当Segi+1 ∈ c0时，uj = 0，i = i + 1，j = j + 1<br>
当Segi+1 ∈ c1时，uj = 1，i = i + 2，j = j + 1<br>
当Segi+1 ∈ c2时，uj =-1，i = i + 2，j = j + 1

**Step 4：**根据NAF（k）的值，临时密钥k可以最终被破解。



## 0x07 Countermeasure of SPA on ECC

成功进行简单的标量乘法能量分析的关键是，能量跟踪会泄漏差分点运算的信息。根据算法2，在三点操作和临时密钥k之间存在依赖性。因此，防御必须从标量乘法实现过程的原子级开始。每个操作的能量损耗必须相等。因此，空操作在倍点运算和加法运算情况下会增加。如公式（6）和（7）。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d02a187b813c7621.png)

其中Rand是随机函数，▲表示零模数乘法，★表示零模数加法。

下表显示，加法和乘法分别增加空运算，包括模块化乘法和模块化加法，以实等效的能量消耗，而且可以获得随机延迟。 针对这种情况，基于选择消息的侧信道攻击是无效的。

[![](./img/198376/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0112f73744a3aa5793.png)



## 0x08 Conclution

本文展示了ECDSA在区块链中的攻击案例。 从ECDSA的原子操作分析了倍点和加法运算之间能量差异的主要原因，并通过在倍点和加法运算中添加空运算给出了原子级等效能量损耗的对策。 这是为了保护安全的加密技术，以防止对区块链硬件设备的侧通道攻击。
