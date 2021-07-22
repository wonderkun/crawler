> 原文链接: https://www.anquanke.com//post/id/85457 


# 【技术分享】Satan勒索软件即服务（RaaS）模式分析


                                阅读量   
                                **195591**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.cylance.com
                                <br>原文地址：[https://blog.cylance.com/threat-spotlight-satan-raas](https://blog.cylance.com/threat-spotlight-satan-raas)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t01e616469294c4dd1b.jpg)](https://p5.ssl.qhimg.com/t01e616469294c4dd1b.jpg)**

****

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**



勒索软件可能是当前最流行的网络敲诈形式，这种方式虽然早已存在多年，但最近勒索软件的变体数量呈显著增加的趋势。由于勒索软件的臭名远扬和潜在的高支付率特点，网络犯罪分子纷纷开发新的勒索软件分发方式以获取不菲回报。

在过去的几年里，恶意软件作者将其专有技术封装打包成昂贵的攻击套装并在地下市场上进行销售，网络犯罪分子购买恶意软件，在感染受害者电脑前首先得支付高额的前期成本。

勒索软件正在悄然改变恶意软件作者和网络犯罪分子的交互方式。加密货币的存在使得勒索软件作者无需提前收费，而只需从成功的犯罪赎金中进行抽成即可，这也将大大增加勒索软件势力范围的扩张。我们最近发现了一个名为Satan（撒旦）的RaaS（ransomware-as-a-service，勒索软件即服务）网站，它向我们展示了网络犯罪分子是如何轻而易举就可以构建复杂的勒索软件并进行分发感染。

**<br>**

**初识Satan RaaS**



在深入了解RaaS模式之前，我们可以先了解一下Satan勒索软件。

根据攻击者选择的恶意软件分发方式，Satan可以作为钓鱼邮件的附件或通过常用的电子邮件活动附件（如Word, Excel, JS脚本，VB脚本）自动下载等等。

真正的Satan二进制载荷经过加密，包含许多反调试和反分析技术以加大对它的静态和动态分析难度。恶意软件作者很有可能掌握一个随时可用的技术库，因为这些技术已经在其他恶意软件中被发现过。

**<br>**

**反调试技术**



在Satan中可以发现以下反调试技术：

BlockInput()函数的调用：该函数在调试会话期间有效，当函数被调用时，鼠标和键盘将会被禁用，而这在实际执行中不会发生。

IsDebuggerPresent()和CheckRemoteDebuggerPresent()函数的调用。

将无效句柄推送到ntdll.NtClose()或CloseHandle()：非常古老且被人熟知的调试器检测方法。

LoadLibrary()或LdrLoadDll()函数的调用：使调试会话崩溃。

NtQueryInformationProcess()函数的调用：使用ProcessDebugPort类来检查程序是否被调试。

OpenProcess()函数和csrss.exe：搜索正在运行的csrss.exe并将其进程ID传递给OpenProcess()以检测程序是否正在被调试。

以下代码片段显示了上面提到的一些反调试技术的使用情况。

[![](https://p4.ssl.qhimg.com/t01238ad60b316a1cb7.png)](https://p4.ssl.qhimg.com/t01238ad60b316a1cb7.png)

图1. 反调试技术

**<br>**

**反分析技巧<br style="text-align: left">**



除了反调试技术，Satan还采用了以下技巧以增加对它的分析难度：

1）检查avghookx.dll和avghooka.dll文件的存在。这两个文件是AVG反病毒软件的一部分。

2）调用调用FindWindowW()函数来搜索当前打开的包含以下标题的窗口：

```
OLLYDBG
WinDbgFrameClass
Immunity Debugger
Zeta Debugger
Rock Debugger
ObsidianGui
```

3）使用GetModuleHandle()函数检查以下动态链接库（DLL）文件是否存在。这些DLL文件与一些最广泛使用的恶意软件分析工具（包括在沙箱或虚拟机环境中使用的工具）有关。

```
SbieDll.dll
dbghelp.dll 
snxhk.dll
api_log.dll
dir_watch.dll
vmcheck.dll
wpespy.dll
pstorec.dll
```

4）枚举并检查当前运行的所有进程，查找以下任何进程是否存在。这些进程同样与恶意软件分析工具有关。

```
ollydbg.exe
ProcessHacker.exe
Tcpview.exe
autoruns.exe
autorunsc.exe
filemon.exe
procmon.exe
procexp.exe
idaq.exe
idaq64.exe
ImmunityDebugger.exe
Wireshark.exe
dumpcap.exe
HookExplorer.exe
ImportRec.exe
PETools.exe
LordPE.exe
Sysinspector.exe
proc_analyzer.exe
sysanalyzer.exe
sniff_hit.exe
windbg.exe
joeboxcontrol.exe
joeboxserver.exe
netmon.exe
```

下图显示了Satan如何执行上述检查过程。

[![](https://p4.ssl.qhimg.com/t0138f6845de04c8155.png)](https://p4.ssl.qhimg.com/t0138f6845de04c8155.png)

图2. 枚举当前进程

图3展示了Satan反分析技术中涉及到的字符串，这些字符串经过加密，不容易在二进制文件中查看，我们在内存中对它们进行了还原。

[![](https://p2.ssl.qhimg.com/t013fc13368549b72a8.png)](https://p2.ssl.qhimg.com/t013fc13368549b72a8.png)

图3. 内存中经解密后的字符串

Satan采用以下方法来检查其是否在沙盒环境中运行。

1）检查wine_get_unix_file_name()函数是否在“Wine”沙盒环境中运行。

2）检查所使用的文件名是否是“sample.exe”，是否在“C:insideTM”文件夹中运行。这两点是Anubis沙箱环境的特点。

3）检查登陆用户是否使用以下用户名，这些用户名是沙盒环境常用的用户名：

```
SANDBOX
MALTEST
MALWARE
VIRUS
TEQUILABOOMBOOM
```

4）检查所在文件夹名称中是否包含以下字符串。这些字符串同样是沙盒环境常用的文件夹名称：

```
SAMPLE
VIRUS
SANDBOX
```

一旦Satan验证其未在沙盒环境中被调试、分析或运行，首先会使用自己的文件名创建一个挂起进程，该进程留待后续使用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01be130fcbf52ca2b4.png)

图4. 创建挂起进程

接下来Satan将另一个可执行二进制文件加载到内存中，该二进制被打包加密存储在主文件中，经过一系列解密工作后，该二进制文件被加载到特定的内存位置。

新的二进制文件是Satan的主体功能文件，此时它不会保存为磁盘文件，而是被载入到刚才创建的挂起进程中。这种“进程持续”技术也是恶意软件使用的另一种反分析技术。

Satan使用ZwReadVirualMemory()函数读取新的可执行文件，然后调用ZwWriteVirtualMemory()将其写入挂起的进程中。一旦写入成功，Satan将调用NtResumeThread()函数恢复挂起的进程，恢复成功后进程将继续执行。

[![](https://p2.ssl.qhimg.com/t01e120a0225ecc511b.png)](https://p2.ssl.qhimg.com/t01e120a0225ecc511b.png)

图5. 进程持续技术：在另一个进程空间中执行可执行映像

Satan将自己的副本存放在%appdata%目录下，创建一个自启动注册表项以伴随Windows启动运行。Satan创建一个随机名称的文件夹存放自身的副本，副本也采用随机生成的文件名。

**一个示例：**

释放文件：

```
C:Users&lt;UserName&gt;AppDataRoamingAqugifyso.exe
```

创建注册表项：

```
HKCUSoftwareMicrosoftWindowsCurrentVersionRun`{`2D077B8E-5F2F-1906-3EF3-8C5D6B12D4F0`}` = “C:Users&lt;UserName&gt;AppDataRoamingAqugifyso.exe –t”
```

Satan尝试连接到C&amp;C服务器，发送感染成功信息。

```
https://dcwqsuh6dxn&lt;xxxxx&gt;.onion.lu/g(dot)php
```

此时Satan将开始搜索和加密具有特定扩展名的文件通过枚举所有本地和远程映射驱动器，Satan递归扫描文件夹和子文件夹中具有以下扩展名的文件：

[![](https://p1.ssl.qhimg.com/t01dc759ce6314631af.png)](https://p1.ssl.qhimg.com/t01dc759ce6314631af.png)

图6. 目标文件扩展名

Satan将跳过扫描位于系统文件夹（如C:Windows，C:Program Files和C:Program Files（x86））中的文件，以保证系统在重启后还能正常工作。

当Satan找到目标文件后，它将使用RSA-2048和AES-256对文件进行加密。经过加密的所有文件的文件名将被随机更改，并以“.stn”作为扩展名。

例如，“my_document.docx”将被改名为"erwirydj.stn"。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0180a115860086323b.png)

图7. 被感染后的文件

成功加密文件夹中的一个或多个文件后，Satan将在当前文件夹中创建一个名为“HELP_DECRYPT_FILES.html”的文件，显示勒索信息以及如何付款信息。

[![](https://p2.ssl.qhimg.com/t01f67fc830c90e2a8a.png)](https://p2.ssl.qhimg.com/t01f67fc830c90e2a8a.png)

图8. HELP_DECRYPT_FILES.html文件

点击页面中的任一链接后，受害者将转到另一个页面，其中包含如何注册比特币（BTC）钱包、购买比特币以及如何使用比特币支付赎金的说明。

[![](https://p4.ssl.qhimg.com/t017a2243ef5bd6a748.png)](https://p4.ssl.qhimg.com/t017a2243ef5bd6a748.png)

图9. 赎金支付页面

当然，即使受害者支付赎金后，也不能保证他们能顺利恢复文件。

**<br>**

**勒索软件即服务（Ransomware-as-a-Service，RaaS）**



Satan的开发者设置了一个网站，允许用户生成自己的Satan变种，他们可以使用自己的方法进行软件投放，可以指定他们想要的赎金所对应的比特币数量。他们可以创建任意多数量的变种，可以很容易地监测通过该网站被感染和支付赎金的受害者状态。Satan开发者将从受害者所支付的赎金中抽成30%作为回报。

[![](https://p4.ssl.qhimg.com/t017c8bbc64bbd1fa3b.png)](https://p4.ssl.qhimg.com/t017c8bbc64bbd1fa3b.png)

图10. Satan RaaS介绍页

用户在网站上注册和登陆后，将被转到主页面，在填写必要表单信息后就可以制作Satan变种，该页面同时还显示变种的感染及赎金获取状态报告。

[![](https://p0.ssl.qhimg.com/t019bd273808b66c5e9.png)](https://p0.ssl.qhimg.com/t019bd273808b66c5e9.png)

图11. 变种制作页面

变种创建完毕后，用户可以从页面底部的下载区域下载该变种。

[![](https://p1.ssl.qhimg.com/t01d49743dad101052a.png)](https://p1.ssl.qhimg.com/t01d49743dad101052a.png)

图12. 页面的下载区域

现在用户可以自行决定如何分发自己的勒索软件。事实上，该页面还提供了一个工具以制作携带勒索软件的CHM或带宏脚本的Word文档。用户首先需要利用页面提供的Powershell或Python脚本，使用自己的密钥对二进制可执行文件进行加密（脚本采用简单的异或加密算法）。用户将加密后的文件上传到某个托管Web服务器，获取文件链接，在图13的下载器创建页面中，用户需要提供该链接及所使用的加密密钥。

[![](https://p5.ssl.qhimg.com/t013ad50955686c631b.png)](https://p5.ssl.qhimg.com/t013ad50955686c631b.png)

图13. 下载器创建页面

点击“生成”按钮后，网页将为用户提供CHM和带宏脚本Word文档的下载器生成脚本，以及脚本的使用方法。例如，网页可以指导用户创建一个带有名为“Autoopen”宏的Word文档，宏内容通过复制/粘贴网页代码填充即可。网页生成的脚本都比较简单，高级用户可以通过混淆处理以规避传统的防病毒软件引擎。

[![](https://p3.ssl.qhimg.com/t01f506c6587d621eeb.png)](https://p3.ssl.qhimg.com/t01f506c6587d621eeb.png)

图14. 下载器脚本生成页面

**<br>**

**结论**



随着RaaS模式的兴起，我们认为勒索犯将采用这种模式来激励恶意软件的制作、分发及销售，勒索软件的准入门槛也将降低，具备广泛分销网络的复杂犯罪组织也将介入勒索软件市场，而那些技术不够的脚本小子们也很容易开始传播恶意软件来牟取暴利。

**<br>**

**攻击指示器（IOCs，Indicators of Compromise）**



SHA-256哈希值

```
189317E4CA2591D2036956FC35A45F6ACDC27D6D99029D1A75305FAA233DB55C
275149352D185B624418AB0531FD276EC1522F841721AE6FB6505DFC0A07E541
3D7273CD598B064AD1BBDC3CAC08D5BA94B9F1C8875A2C9EF8F80D3A88B2AC4E
3F8ED321E43E191A5E15063BB26131C5D122C1FB9CDB2856BE1B1B542BAA4E4C
423F21E066F9041AA95F5CDF10CBD6DF0ECD2BDEB180A2F105F9CAFD1D8FD56D
497A8324D6A49B4088E4C2D06A90C752BC67993F10C391CA958532EE1F38C22D
50D6E779D77AACB0757870777F0AA18E3389B54799FEB0B357926BFD21293166
527E19E930885AE43AF08571A2FDF6C09F8975BE3F590B0D2526991981686086
54C61111C6247A7B7609104EE9E68C68072176553262FB5CE2AC62C30287333E
551898DE2E40E82AE4ACB882B67FB766B8CB52E33C1586D68C25658165D9A359
559830A0E8F704EE0784B80A219244AE400B84FFD806216E58F58FAE8E3D82D8
60E13B438270B73297420928EF9CE3EC2DDF745C13786111684CF039D139B1F6
683A09DA219918258C58A7F61F7DC4161A3A7A377CF82A31B840BAABFB9A4A96
6926BF0A681E279B82F7BE90E6A3F2C89E4FE0E8735A71EFD19A8AF7763432F7
73D8E669166428C158A250ED03307D2609772DB22199AA0B270AA47539192DFC
7AF31E78745297A013C129049EC198ADE6BE589A2E37BC53FBBA0B8CD31EB499
7E183B7AEF1CCAE6671687898A4EA7A366296AACE32F9BDF980446DA3BC1BA4E
81D844B7B717DF31EF9F48B5F45C4F79BEB1FFE98FF72404DA53A5B1C9CDDAEA
84DD7AFBFC63272EEA2C55B6D079EF1897971516E3A7359AA932FEC10EA6D4B6
9691B6330C5D7B30ECB5F8521AF8FFA841708715E793CA8EAE2268D8FDF8F376
9874815AA0B629DB4CC25F76DCA3D307B9A92C139B4CE2209957772F7E6D7F98
9A10F8079E85E6CE401CA864058CA0C6261551E3283EB5976B77F6D45583C6BE
9B85261A80B53E084581411281E8BC33580933A9CFA615E352DC9E2DA9028400
A7A8E0E8B35E7CDDF63CF099C37AF5B3DDB7F517B5A485EE56B66BB5F450326C
A884AB79BCE95D99C67A10CF5E3A671460E5EBF7A00CDCE478DCC5A226698A4E
B38B4C1DCF6D6ECD1BBFC236B43C37C18044C2F42F11E5088384F4BD0751929C
B87B696A5497EF13FCAFDD3B9A608D8F8B0582EA2CECB3D42AE18918B6E2B9B4
BB83B4AFE9F8F27888ABEE0C63CEC3E73496AC191B954F348916DF0C6CC9A25F
C04836696D715C544382713EEBF468AEFF73C15616E1CD8248CA8C4C7E931505
C45F2A7B82BA48F40997FA8E9C3B036BC50D2B63885F07EE51EC454E896C5CF6
CB6C4933515181096583A9F85813526096D5B135C461393D288077EC8FA28A57
CCF384FA1A757B0FAC7F4D1AED45279B28AA755BB9238C57F1B6AD23BCE8C4DB
CD00EECD9D0DE87953ED0E905A82C013BB6E954680D80EA1B7FC77B8DBF5A127
D274F3F8C7D4E69622F9B71AED62D94454C25D6FA368BFE4218EAAC4F6AF0B3A
E5BE3D2DD286D51F22D36227D360EFA790A9E17A6FD0C13AD601B8BDB6CBA4DA
E6E27A9DCAB0187CC81B71EBD08EE4CF3E061B5A7C34B2E64F3C27C51152D04F
EA2C169529E782994BE5296C81FF4668DBA2B77A805BD057B53E5952C65AAF72
EBB1AF5E17B7B776C0461E823B13C06C7745F65D10A0E267C37E327CD8C146AD
ECBC409F32F4F8025050DCC195C707D1908BF65C8EEABFDD4D3EF97D6C07CA89
ED84A7185BD3DECFE9104FA3F6DAD24BB0A0FF27A1A792A05EF0F2B010BF7B9B
EE937717EFE9A2E076B9497498B628BEB0C84A8476BD288105A59C5AEEA01F3D
F4F756C4E00B828FEE02AFF2C8D58F0CC84395690BC713045AB50B00AD61C537
F814DC77EDBDB4B36895C5BF3415EA8DBA9A341E10CA664A3B5CECFD29938232
FBAD2A39C9B33BABF306204A1794752C2057BA265F3916497697A9E73CFE76B4
```


