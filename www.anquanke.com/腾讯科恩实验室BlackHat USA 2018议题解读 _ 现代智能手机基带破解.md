> 原文链接: https://www.anquanke.com//post/id/156596 


# 腾讯科恩实验室BlackHat USA 2018议题解读 | 现代智能手机基带破解


                                阅读量   
                                **187096**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01700b33ca2249e300.jpg)](https://p1.ssl.qhimg.com/t01700b33ca2249e300.jpg)

## 1、议题概要

据估计，全球有超过30亿的智能手机，而基带是智能手机的重要组成部分，负责处理和与移动无线网络(如2G、3G、4G等)通信。因此对基带进行安全性评估的重要性不容小觑。由于目前有关基带的研究主要是用于灰色产业，因此公开的研究资料非常有限。此外，无线电协议和软件的复杂性也导致基带研究的门槛非常高。基带可以在无需任何用户交互的情况下从无线网络远程访问，这个特性也让它具有非常高的研究价值。本议题将讨论现代智能手机基带设计以及安全对策。该议题将以Mobile Pwn2Own 2017基带项目中使用的0day漏洞为例，阐述腾讯安全科恩实验室发现并利用该漏洞实现远程代码执行的过程和细节。通过利用该漏洞，腾讯安全科恩实验室最终完成了在更新后的华为Mate 9 Pro上无用户交互条件下的远程代码执行，并在该项目上赢得了10万美元奖金。华为也在第一时间响应并打补丁解决了这个问题，展现了企业非常专业的合作精神与责任担当。更多详细信息欢迎关注腾讯科恩实验室官方微信号：KeenSecurityLab，回复“基带安全”即可获得《现代智能手机基带破解》研究技术细节白皮书！

[![](https://p4.ssl.qhimg.com/t01a8f208681e822900.jpg)](https://p4.ssl.qhimg.com/t01a8f208681e822900.jpg)



## 2、作者简介

Marco Grassi，腾讯科恩实验室高级研究员，研究涉猎iOS、Safari、VMWare、基带等多个方向，多次作为核心成员参与Pwn2Own、Mobile Pwn2Own并获得冠军，多次在国际安全会议上进行演讲，包括Black Hat USA, DEF CON, CanSecWest, ZeroNights, Codegate, HITB and ShakaCon等。

[![](https://p0.ssl.qhimg.com/t012b612867458183e7.jpg)](https://p0.ssl.qhimg.com/t012b612867458183e7.jpg)

刘穆清，腾讯科恩实验室安全研究员，主要研究固件安全、二进制分析、安全研究工具开发，同时也是CTF选手，作为腾讯eee战队及0ops战队队员曾多次参与CTF比赛，并和A*0*E联队成员一起参与了今年的DEF CON CTF。

[![](https://p2.ssl.qhimg.com/t011a676016daa5d563.jpg)](https://p2.ssl.qhimg.com/t011a676016daa5d563.jpg)

谢天忆，腾讯科恩实验室高级研究员，CTF选手，腾讯eee战队及A*0*E联队队长，Pwn2Own 2017 VMware项目冠军队伍成员，Mobile Pwn2Own 2017 Baseband项目及“Master of Pwn”冠军队伍成员。

[![](https://p2.ssl.qhimg.com/t0184e0b3763d61af23.jpg)](https://p2.ssl.qhimg.com/t0184e0b3763d61af23.jpg)



## 3、议题解析

现代智能手机是一个非常复杂的系统，它包含一个主CPU以及许多次级CPU，这些CPU共同协作完成各项任务。其中，主CPU也可以称为AP(应用程序处理器)。在这些CPU中，我们可以找到Wi-Fi SoC模块和基带模块。[![](https://p2.ssl.qhimg.com/t015b17fba4acbf3c56.png)](https://p2.ssl.qhimg.com/t015b17fba4acbf3c56.png)

AP运行各种操作系统(如Android或iOS)，而基带运行RTOS(实时操作系统)。它们作为系统独立存在，通常通过USB、PCI-e、共享内存或其他机制进行通信。如果仅在基带上实现代码执行，并不意味着可以在AP上实现代码执行。

[![](https://p5.ssl.qhimg.com/t01b6144d5ec48f4832.png)](https://p5.ssl.qhimg.com/t01b6144d5ec48f4832.png)

事实上，让我们决定将研究目标定位在基带模块的原因有许多，主要原因如下:

1、基带不太容易理解并且攻击面审计比较少；

2、基带可以在远距离且在无需用户交互的情况下远程破解；

3、基带在漏洞利用的缓解措施方面，相比较现代操作系统(如Android和iOS)要落后一些。

4、由于基带一般是来自第三方，因此设备制造商没有办法审计基带源代码。

5、基带是一个非常复杂的系统。

基带基本上就是一个在手机独立的CPU中运行的固件黑盒。在某些方面，它和物联网设备类似，其上运行一个实时操作系统(RTOS)，负责调度系统组件的各种任务。由于基带芯片需要支持多种协议栈，其实现通常非常复杂。相关的协议规范文档通常就有数万页之多。

一般来说，在系统中，每个网络层都有一个任务与其对应,例如MM任务,SM任务等。通过定位无线电消息被解析和处理的地方可以更容易地找到消息处理程序，之后就可以开始寻找消息处理程序的内存泄露错误。

[![](https://p4.ssl.qhimg.com/t0143f443da735c102c.png)](https://p4.ssl.qhimg.com/t0143f443da735c102c.png)

作为第一步，我们需要找到并分析固件。由于我们将华为作为一个研究案例进行展示，所以我们将重点关注该固件。

[![](https://p4.ssl.qhimg.com/t01e22d9eabbec01b61.png)](https://p4.ssl.qhimg.com/t01e22d9eabbec01b61.png)

我们可以在Android phone文件系统中找到文件名为“sec_balong_modem.bin”的固件文件。 该文件由Android内核加载并传递给TEE(可信执行环境)进行签名检查，再将其加载到基带中。我们使用IDA Pro对其进行逆向分析。

在分析过程中，我们迅速注意到华为基带缺乏ASLR和栈cookie，此外，其他许多厂商也缺乏这些保护措施。第二步我们收集运行时信息。之前是通过使用“cshell”在基带上获得有限的调试能力，但最近它被移除了。

我们尝试后发现当基带崩溃时，它会将有用的日志输出给AP用来进行日志记录。除此之外，当我们在Android内核中运行代码，我们可以在物理内存0x80400000地址开始读取数据来获取基带内存数据。这为我们后续调试基带利用方案提供很大帮助。

我们还可以找到一个描述NVRAM格式的开源项目，开源项目地址为:https://github.com/forth32/balong-nvtool。

网上其他的信息也非常有用。我们花了一些时间做调研，还在GitHub发现一个泄漏的旧版本华为基带源代码。尽管代码并不是最新的，但这份源代码对于逆向工程起到很大的帮助作用。此外，我们还在网上找到理解无线电协议所需的所有3GPP规范。

但是我们究竟是如何攻击基带呢?

毋庸置疑的是我们一定是通过无线电通信进行攻击的。这种攻击的“传统”思路是模拟一个假基站，然后攻击手机。

[![](https://p2.ssl.qhimg.com/t015d5b31bc6f45cf80.png)](https://p2.ssl.qhimg.com/t015d5b31bc6f45cf80.png)

最常见的方法是使用SDR(软件定义无线电)。一方面，SDR的价格在可接受的范围内，另一方面，一些开源工程为我们的研究提供了帮助。这些积极因素有效地降低了我们的研究难度。SDR可以是USRP(通用软件无线电外设)或BladeRF(USB 3.0超高速软件定义无线电)。一台带有SDR的笔记本电脑就可以模拟一个基站(BS)。由于一些无线电技术没有采用相互认证的方式，因此手机会连接到那些恶意构造的伪基站。

但实际真的那么好利用吗？事实并没有想象的那么简单，我们并不能直接使用SDR和开源软件。我们Pwn2Own漏洞实际是在华为基带的CDMA(码分多址)部分。CDMA是一种3g网络，在部分地区也有使用UMTS(通用移动通信系统)进行3G网络传输。

我们使用的bug是在CDMA 1x SMS传输层消息部分中一个负责解析PRL(出国优选漫游列表)消息的函数中。这个bug的简化版本如下:

[![](https://p3.ssl.qhimg.com/t012d389a9d800565e3.png)](https://p3.ssl.qhimg.com/t012d389a9d800565e3.png)

这里我们注意到了一个函数：memcpy_s。这个函数和memcpy一样，可以将指定长度的数据复制到另一块内存区域中，但和memcpy不同，除了原有的三个参数（源地址、目的地址和源数据长度）外，该函数还增加了一个size_t类型的参数，用来表示目的地址的存储空间大小。利用这个参数，在复制时，memcpy_s函数可以检查被拷贝的数据大小不会超过目的地址的大小，从而在无意中避免了很多bug。

但这并不会影响我们要利用的漏洞，因为我们控制拷贝数据的目的地址而不是长度。我们在了解memcpy_s的基础上再来查看这个bug，可以看到消息处理器在解析消息时，会提取部分偏移量/长度，然后在没有检查的情况下，它们被添加到byte_pos，从而导致可利用的栈溢出。

[![](https://p5.ssl.qhimg.com/t01a6624d9b2482f1dd.png)](https://p5.ssl.qhimg.com/t01a6624d9b2482f1dd.png)

那么我们该如何触发这个bug呢?首先需要建立一个CDMA网络。但这并不容易。目前并没有公开的实现方法可以在SDR上运行运行CDMA 1x基站。我们也没有时间自己再实现一遍，所以我们想出了一个不走寻常路的解决方案。我们购买并更改了一台Rohde&amp;Schwarz CMU200设备。

[![](https://p2.ssl.qhimg.com/t01b53f20a081e58cee.png)](https://p2.ssl.qhimg.com/t01b53f20a081e58cee.png)

[![](https://p4.ssl.qhimg.com/t01b117e0feedfb34ba.jpg)](https://p4.ssl.qhimg.com/t01b117e0feedfb34ba.jpg)

这台设备本身是用来测试设备的信令和非信令功能。它还支持CDMA 1x标准，我们将通过逆向工程以及打补丁的方式使用这台设备完成发送任意数据包的需求。

[![](https://p5.ssl.qhimg.com/t01034ff9e033ced179.png)](https://p5.ssl.qhimg.com/t01034ff9e033ced179.png)

这台设备常规的工作流程如下:

[![](https://p5.ssl.qhimg.com/t0102bd9e0dc48ada9b.png)](https://p5.ssl.qhimg.com/t0102bd9e0dc48ada9b.png)

但我们希望设备可以直接转发PDU而不对其进行编码和数据包组装：

[![](https://p5.ssl.qhimg.com/t0151284c81426b1cba.png)](https://p5.ssl.qhimg.com/t0151284c81426b1cba.png)

那么该怎么做才能实现这样的目标呢？CMU 200运行在MS-DOS和Windows 3.x版本系统上，用户可以在UI图形界面中发送短消息。我们首先研究设备的文件系统以及逆向PE文件。

[![](https://p1.ssl.qhimg.com/t01948459c6b46f643a.png)](https://p1.ssl.qhimg.com/t01948459c6b46f643a.png)

[![](https://p4.ssl.qhimg.com/t0104d3edb399fe0962.png)](https://p4.ssl.qhimg.com/t0104d3edb399fe0962.png)

我们找到一个名称为“C2KMS.DL3”的文件，这个文件会读取短消息的文件内容，并将短消息传送到B83 CDMA模块进行发送。我们在这里更改了一个长度检查，但是我们不能完全控制数据。

[![](https://p0.ssl.qhimg.com/t01b13d8a167a45e20c.png)](https://p0.ssl.qhimg.com/t01b13d8a167a45e20c.png)

[![](https://p5.ssl.qhimg.com/t0175ecbc5d66125cce.png)](https://p5.ssl.qhimg.com/t0175ecbc5d66125cce.png)

所以我们需要进一步修改B83模块固件。我们在文件系统中找到了B83固件，在恢复文件格式之后，对它进行逆向分析。

[![](https://p3.ssl.qhimg.com/t01144b7f7df96c3f99.png)](https://p3.ssl.qhimg.com/t01144b7f7df96c3f99.png)

非常幸运的是，首先B83子板基于PowerPC平台(一种精简指令集RISC的中央处理器架构)，而我们也有其固件对应的反编译器。其次，固件本身没有进行签名检查，只有CRC(循环冗余校验)。此外，二进制文件中符号表数据也保留着!

[![](https://p2.ssl.qhimg.com/t017b26fddc706193b2.png)](https://p2.ssl.qhimg.com/t017b26fddc706193b2.png)

我们继续定位“buildSmsMsg”函数，并修改函数使得可以携带任意数据。然后我们刷新B83模块，此时我们就可以发送任意的PDU(协议数据单元)了。

[![](https://p5.ssl.qhimg.com/t01169577bbe3a188f0.png)](https://p5.ssl.qhimg.com/t01169577bbe3a188f0.png)

[![](https://p3.ssl.qhimg.com/t012682122927032f22.png)](https://p3.ssl.qhimg.com/t012682122927032f22.png)

现在我们将要尝试触发bug并使基带crash!我们该如何利用这个bug呢?这个过程也并不像看起来那么简单! 攻击payload是一条畸形的CDMA 1x SMS传输层消息。其SMS_MSG_TYPE字段必须是00000000，表示SMS点对点消息。[![](https://p3.ssl.qhimg.com/t01e9573d7265cac132.png)](https://p3.ssl.qhimg.com/t01e9573d7265cac132.png)

该消息由TLV格式的参数组成，其中一些参数必须被设置正确才能确保抵达有漏洞的函数，包括:

Teleservice Identifier(PARAMETER_ID 00000000)

Originating Address(PARAMETER_ID 00000010)

[![](https://p5.ssl.qhimg.com/t01f353ee880c609b9d.png)](https://p5.ssl.qhimg.com/t01f353ee880c609b9d.png)

在这些参数中，Bearer Data(PARAMETER_ID 00001000)会在漏洞函数中被解析：

[![](https://p3.ssl.qhimg.com/t01b447f0f2bea34c9d.png)](https://p3.ssl.qhimg.com/t01b447f0f2bea34c9d.png)

Bearer Data(PARAMETER_ID 00001000)在漏洞函数中被解析为由TLV格式的子参数组成的结构。为此我们必须适当地配置子参数以表示该消息为PRL消息。

[![](https://p0.ssl.qhimg.com/t01a852923ec096a491.png)](https://p0.ssl.qhimg.com/t01a852923ec096a491.png)

类型为Message Display Mode (SUBPARAMETER_ID 00001111)的子参数最为关键，其中：
- MSG_DISPLAY_MODE字段必须设为0x03
- RESERVED字段必须设为0x10
[![](https://p1.ssl.qhimg.com/t0103c4e458fe8cb49a.png)](https://p1.ssl.qhimg.com/t0103c4e458fe8cb49a.png)

[![](https://p3.ssl.qhimg.com/t01c65358f213168b2c.png)](https://p3.ssl.qhimg.com/t01c65358f213168b2c.png)

漏洞代码的基本功能是对Bearer Data中的子参数进行排序，缓冲区溢出就发生在该部分代码中。乍一看，这种利用似乎非常容易，因为没有NX/ASLR/Stack Canary等保护措施，看起来就像90年代的典型栈溢出利用。但这是真的吗?

事实上，尽管有多条路径可以触发漏洞函数，但并不是所有的路径都可以通过空口消息触发。其中有一条路径可以通过空口消息触发，但是此时能够被溢出的那个缓冲区并不在栈上，而是在全局变量段中。还有另一条将缓冲区放在栈上的路径，但限制条件是只有当手机从USIM卡中读取短消息的时候才能触发，看上去对远程利用这个漏洞没什么帮助。到这里为止，所有的可能性都被考虑过了，但仍然没有发现任何明显可行的方法，似乎前方是一条没有出口的死路。

[![](https://p1.ssl.qhimg.com/t014c9658eb596449f4.jpg)](https://p1.ssl.qhimg.com/t014c9658eb596449f4.jpg)

但永不放弃始终是我们的信条。通过对该部分逻辑更深刻地理解，我们最终找到了一条非常深但是十分稳定的路径。

基带处理PRL消息的整个过程如下：

-通过空口接收信息

-解码消息(第一次触发漏洞函数，但缓冲区不在栈上)

-编码消息

-将消息写入USIM卡

-从USIM卡中读出信息

-解码消息(第二次触发漏洞函数并且缓冲区在栈上)

Payload必须能通过第一次解码和编码的过程，并在第二次解码的过程中溢出栈缓冲区。为了构造这样的payload，我们需要一些简单的数学上的抽象：
- Payload:x
- 解码函数——dec(x)
- 编码函数——enc(x)
- 栈溢出ROP链:p
- 目标:对于给定的p，找到一个x使得p = dec(enc(dec(x)))
让我们用更优雅、更数学的方法来解决这个数学问题。

我们的目标变为: 对给定的p，找到一个x，使得p = dec(x)且x = enc(dec(x))
- 这里的x也称为复合函数enc(dec(x))的不动点
因此可以很容易导出p = dec(x) = dec(enc(dec(x)))，正是我们想要的结果。通过这种方法构造的payload适用于任意多次的解码和编码过程，而不仅仅是一两次。此外，CMU200设备限制TP层消息（也就是我们的payload）的长度必须小于等于130字节，更给我们的构造过程增加了难度。

事实证明，构造这个Payload并不是一帆风顺的，但它是可以实现的! 更多细节请阅读我们的白皮书! 我们也把这个漏洞的利用过程改编成了今年TCTF预选赛中的一道pwnable题目——Mighty Dragon，其名字正是来源于基带的代号“霸龙”。在当时的比赛中仅有一支队伍解出了这道题目，可见这道题是非常有挑战性的，欢迎感兴趣的小伙伴踊跃尝试，关注微信号“KeenSecurityLab”并回复“Mighty Dragon”获取题目下载链接。

那么，在我们实现漏洞利用之后，我们如何展示呢?我们不能像在Windows上那样运行一个calc.exe计算器可执行程序来进行演示。最终，我们决定将手机IMEI修改成1337XXX，这样我们可以从手机设置UI看到修改后的变化。

在成功得到基带中的代码执行能力后，我们可以得到很多信息，比如间谍短信，电话，互联网流量，甚至可以修改这些信息。尽管比赛没有要求完成基带绕过，但许多其他研究人员的研究结果表明这是可以实现的。例如Project Zero的Gal使用WiFi芯片中的DMA来修改内核内存，Comsecuris使用MTK基带中的路径遍历来覆盖AP中的文件。这也和浏览器漏洞类似，在实现第一个RCE(远程代码执行)之后，你可以结合沙箱逃逸漏洞构建完整的攻击链。基带在实现第一个RCE之后，也可以构建一条基带逃逸攻击链，并得到完整的系统控制。

最后，我们想和大家说的是，只要你足够坚定，在现代基带实现远程终端控制是完全有可能的。这种攻击也是真实的存在的。究其根本，一方面基带是由内存不安全的语言编写的，因此无法避免内存破坏问题，另一方面，基带安全也一直没有受到重视。

[![](https://p0.ssl.qhimg.com/t019ca7ffed6ab1723e.jpg)](https://p0.ssl.qhimg.com/t019ca7ffed6ab1723e.jpg)

我们也希望基带在未来的部署中可以考虑更多安全缓解措施，也许将来也会用内存安全的语言编写基带。

更多详细信息欢迎关注腾讯科恩实验室官方微信号：KeenSecurityLab，并回复“基带安全”即可获得《现代智能手机基带破解》研究技术细节白皮书！

[![](https://p0.ssl.qhimg.com/t01e937ed1654bf5a7a.jpg)](https://p0.ssl.qhimg.com/t01e937ed1654bf5a7a.jpg)
