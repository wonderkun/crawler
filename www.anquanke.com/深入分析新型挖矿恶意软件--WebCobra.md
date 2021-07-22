> 原文链接: https://www.anquanke.com//post/id/164366 


# 深入分析新型挖矿恶意软件--WebCobra


                                阅读量   
                                **230459**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者McAfee，文章来源：mcafee.com
                                <br>原文地址：[https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/webcobra-malware-uses-victims-computers-to-mine-cryptocurrency/](https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/webcobra-malware-uses-victims-computers-to-mine-cryptocurrency/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t014129b212cda2fb88.jpg)](https://p4.ssl.qhimg.com/t014129b212cda2fb88.jpg)



## 一、前言

MCAfee实验室的研究人员近期发现了一种来自俄罗斯，名为WebCobra的新型恶意软件。它利用感染者的计算机进行挖矿获利。

挖矿恶意软件一般来讲比较难被检测到。一旦计算机被感染，恶意软件就会在后台默默运行，唯一的表象就是受感染者计算机性能会有所下降。且性能下降的程度会随着恶意软件占用计算资源的增多而增加，这也使得受感染者十分厌恶自己的计算机运行这种挖矿软件。此外，最近的一份统计报告显示开采单个比特币所需的能源成本从531美元到26170美元不等。

由于加密货币经济价值的不断攀升，许多网络犯罪分子纷纷选择在受害者不知情的情况下，利用恶意软件窃取他们的计算资源来挖掘加密货币以此获利。

下图展示了挖矿恶意软件的流行程度随门罗币价格变化的具体情况:

[![](https://p3.ssl.qhimg.com/t015f612e6bde1633ea.png)](https://p3.ssl.qhimg.com/t015f612e6bde1633ea.png)

图1:门罗币价格在2018年初达到顶峰，挖矿恶意软件的总样本数还在继续增长。资料来源:[https://coinmarketcap.com/currencies/monero/](https://coinmarketcap.com/currencies/monero/).

McAfee实验室在此前的一篇报告中分析过一种感染文件的挖矿恶意软件—CoinMiner。同时在McAfee的协助下,网络威胁联盟组织发布了一篇关于非法挖矿的威胁报告“The Illicit Cryptocurrency Mining Threat.”最近，我们分析了一款来自俄罗斯的软件WebCobra，发现它会在用户的计算机上释放并安装挖矿程序Cryptonight或是Claymore’s Zcash。具体是哪一种挖矿程序取决于其所在计算机的架构。

我们认为这种恶意软件威胁是通过流氓软件PUP安装器进行传播的。我们在全球范围内的很多地方都看到了它的身影，巴西，南非和美国的感染数量最多。

[![](https://p1.ssl.qhimg.com/t016486c3aef0e5ceb7.png)](https://p1.ssl.qhimg.com/t016486c3aef0e5ceb7.png)

图2:McAfee实验室在9月9日至13日统计的WebCobra感染热图分布。

我们今天要分析的这种挖矿恶意软件与以往出现的有所不同。因为它会根据其感染的计算机的架构和具体配置而释放不同的挖矿程序。我们将会在后文种详细讨论此细节。



## 二、恶意软件行为分析

此次分析的挖矿恶意程序其主要的dropper是一个Microsoft安装程序，用于检查运行环境。如果在x86系统上，它将Cryptonightminer代码注入正在运行的进程并启动进程监视器。如果在x64系统上，它会检查GPU配置，并从服务器端下载执行另一种挖矿程序—Claymore’s Zcash miner。

[![](https://p3.ssl.qhimg.com/t0137508b2bc1c5ef06.png)](https://p3.ssl.qhimg.com/t0137508b2bc1c5ef06.png)

图3:成功启动后，恶意软件会使用以下命令释放并解压一有密码保护的Cabinet归档文件：

[![](https://p3.ssl.qhimg.com/t01353cb79d62329687.png)](https://p3.ssl.qhimg.com/t01353cb79d62329687.png)

图4：解压文件命令。

CAB文件包含以下俩个文件:

> <ul>
- LOC：用于解密data.bin的DLL文件
- bin：包含加密的payload
</ul>

CAB文件使用以下脚本来执行ERDNT.LOC:

[![](https://p0.ssl.qhimg.com/t019df85f266b2d6885.png)](https://p0.ssl.qhimg.com/t019df85f266b2d6885.png)

图5：加载DLL文件ERDNT.LOC的脚本

ERDNT.LOC解密data.bin文件，并通过以下执行流传递给它：

```
[PlainText_Byte] = (([EncryptedData_Byte] + 0x2E) ^ 0x2E) + 0x2E
```

[![](https://p5.ssl.qhimg.com/t016cac7e749e006a38.png)](https://p5.ssl.qhimg.com/t016cac7e749e006a38.png)

图6：解密过程

恶意程序通过检查运行环境以启动相应的挖矿程序的过程，如下图所示：

[![](https://p1.ssl.qhimg.com/t019023b8d38b4ffa61.png)](https://p1.ssl.qhimg.com/t019023b8d38b4ffa61.png)

图7：执行哪一种挖矿程序取决于系统架构

解密并执行data.bin后，它会尝试一些反调试，反虚拟环境以及反沙箱技术的执行，并检查系统上运行的其他安全产品。这些措施使得恶意软件的存活时间更加长久。

大多数安全产品都会hook一些API来监控恶意软件的行为。为了避免被这种技术发现，WebCobra将ntdll.dll和user32.dll作为数据文件加载到内存中，并覆盖这些函数的前8个字节，使得这些API函数无法通过常规手段被hook。



## 三、unhooked ntdll.dll APIs列表
- LdrLoadDll
- ZwWriteVirtualMemory
- ZwResumeThread
- ZwQueryInformationProcess
- ZwOpenSemaphore
- ZwOpenMutant
- ZwOpenEvent
- ZwMapViewOfSection
- ZwCreateUserProcess
- ZwCreateSemaphore
- ZwCreateMutant
- ZwCreateEvent
- RtlQueryEnvironmentVariable
- RtlDecom
- pressBuffer


## 四、unhooked user32.dll APIs列表
- SetWindowsHookExW
- SetWindowsHookExA


## 五、感染x86系统

恶意软件将恶意代码注入svchost.exe，并无限循环地检查所有打开的窗口，并将每个窗口的标题栏文本与以下这些字符串进行比较。这是WebCobra的另一项检查，以确定它是否在专为恶意软件分析而设计的隔离环境中运行。
- adw
- emsi
- avz
- farbar
- glax
- delfix
- rogue
- exe
- asw_av_popup_wndclass
- snxhk_border_mywnd
- AvastCefWindow
- AlertWindow
- UnHackMe
- eset
- hacker
- AnVir
- Rogue
- uVS
- malware
如果前述这些字符串中任何一个显示在Windows标题栏文本中，则打开的窗口将被终止。

[![](https://p4.ssl.qhimg.com/t01eb99bd33bb481b3b.png)](https://p4.ssl.qhimg.com/t01eb99bd33bb481b3b.png)

图8：如果窗口标题栏文本包含特定字符串，则终止进程。

进程监视器执行后，它将miner(释放的挖矿程序)的配置文件指定为参数创建一个svchost.exe实例，并注入Cryptonight miner代码。

[![](https://p2.ssl.qhimg.com/t015dd4ea8eec9b7e28.png)](https://p2.ssl.qhimg.com/t015dd4ea8eec9b7e28.png)

图9：创建svchost.exe实例并执行Cryptonight miner。

最后，恶意软件使得Cryptonight miner进程在后台悄悄运行，并消耗掉几乎所有的CPU资源。

[![](https://p3.ssl.qhimg.com/t01240a20a0636f4d92.png)](https://p3.ssl.qhimg.com/t01240a20a0636f4d92.png)

图10：感染Cryptonight miner的x86计算机。



## 六、感染x64系统

如果发现目标主机上的Wireshark正在运行，恶意软件会终止其感染过程。

[![](https://p3.ssl.qhimg.com/t01c63688e950e3d743.png)](https://p3.ssl.qhimg.com/t01c63688e950e3d743.png)

图11：检查是否有wireshark运行

恶意软件会检查GPU的型号和模式。仅在安装以下GPU时才会运行：
- Radeon
- Nvidia
- Asus
[![](https://p4.ssl.qhimg.com/t01c690a2e81528133e.png)](https://p4.ssl.qhimg.com/t01c690a2e81528133e.png)

图12：检查GPU模式

如果以上检查都已经通过，则恶意软件会创建一个隐藏文件夹，并在其中下载、执行一来自远端服务器的Claymore’s Zcash miner(另一种挖矿程序)。

```
C:\Users\AppData\Local\WIX Toolset 11.2
```

[![](https://p0.ssl.qhimg.com/t01f849fef4385fb4fb.png)](https://p0.ssl.qhimg.com/t01f849fef4385fb4fb.png)

图13：下载Claymore’s Zcash miner的网络请求数据包。

[![](https://p1.ssl.qhimg.com/t0136548b0d6e6e7e69.png)](https://p1.ssl.qhimg.com/t0136548b0d6e6e7e69.png)

图14：Claymore’s miner.

[![](https://p0.ssl.qhimg.com/t01718c72eef7efa39b.png)](https://p0.ssl.qhimg.com/t01718c72eef7efa39b.png)

图15：根据其配置文件执行挖矿程序。

最后，恶意软件在％temp％ – xxxxx.cMD下释放一批处理文件来从[WindowsFolder] `{`DE03ECBA-2A77-438C-8243-0AF592BDBB20`}` **.**中删除主要dropper。

[![](https://p3.ssl.qhimg.com/t0190de8f3f7b40961d.png)](https://p3.ssl.qhimg.com/t0190de8f3f7b40961d.png)

图16：删除dropper的batch文件

挖矿程序的配置文件如下:

[![](https://p1.ssl.qhimg.com/t0166825d67b405473e.png)](https://p1.ssl.qhimg.com/t0166825d67b405473e.png)

图17：Cryptonight’s miner配置文件

配置文件包括：
- 矿池：5.149.254.170
- 用户名：49YfyE1xWHG1vywX2xTV8XZzbzB1E2QHEF9GtzPhSPRdK5TEkxXGRxVdAq8LwbA2Pz7jNQ9gYBxeFPHcqiiqaGJM2QyW64C
- 密码：soft-net
[![](https://p0.ssl.qhimg.com/t016a5bd2d823347a1b.png)](https://p0.ssl.qhimg.com/t016a5bd2d823347a1b.png)

图18：Claymore’s Zcash miner配置文件。

此配置文件包括:
- 矿池：eu.zec.slushpool.com
- 用户名：pavelcom.nln
- 密码：zzz


## 七、总结

由于网络犯罪分子通过这种相对容易的途径可以获得较高的经济效益，我们认为挖矿恶意软件将会继续发展。在其他人的计算机上挖矿相比与勒索软件来说投资更少，承担的风险也更小。此外，挖矿恶意软件不依赖于受害者同意汇款以解除计算机勒索的比例大小，直到受害者发现自己电脑上运行挖矿程序之前，恶意软件方都一直有很大的收获。



## 八、MITRE ATT&amp;CK技术
- 通过C&amp;C隧道传递命令
- 命令行界面
- Hooking
- 来自本地系统的数据
- 文件、目录特征
- 查询注册表
- 系统信息发现
- 特定进程
- 系统时间
- 进程注入
- 数据加密
- 数据混淆
- 多层加密
- 文件删除


## 九、IOC

### IP 地址

```
149.249.13:2224
149.254.170:2223
31.92.212
```

### 域名

```
fee.xmrig.com
fee.xmrig.com
ru
zec.slushpool.com
```

### McAfee 检测

CoinMiner Version 2 in DAT Version 8986; Version 3 in DAT Version 3437

l Version 2 in DAT Version 9001; Version 3 in DAT Version 3452

RDN/Generic PUP.x Version 2 in DAT Version 8996; Version 3 in DAT Version 3447

Trojan-FQBZ, Trojan-FQCB, Trojan-FQCR Versions 2 in DAT Version 9011; Versions 3 in DAT Version 3462

### Hashes (SHA-256)

```
5E14478931E31CF804E08A09E8DFFD091DB9ABD684926792DBEBEA9B827C9F37
2ED8448A833D5BBE72E667A4CB311A88F94143AA77C55FBDBD36EE235E2D9423
F4ED5C03766905F8206AA3130C0CDEDEC24B36AF47C2CE212036D6F904569350
1BDFF1F068EB619803ECD65C4ACB2C742718B0EE2F462DF795208EA913F3353B
D4003E6978BCFEF44FDA3CB13D618EC89BF93DEBB75C0440C3AC4C1ED2472742
06AD9DDC92869E989C1DF8E991B1BD18FB47BCEB8ECC9806756493BA3A1A17D6
615BFE5A8AE7E0862A03D183E661C40A1D3D447EDDABF164FC5E6D4D183796E0
F31285AE705FF60007BF48AEFBC7AC75A3EA507C2E76B01BA5F478076FA5D1B3
AA0DBF77D5AA985EEA52DDDA522544CA0169DCA4AB8FB5141ED2BDD2A5EC16CE
```
