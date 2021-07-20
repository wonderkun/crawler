> 原文链接: https://www.anquanke.com//post/id/145076 


# 对投递Grobios木马的RIG EK的深入分析


                                阅读量   
                                **99212**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.fireeye.com/
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2018/05/deep-dive-into-rig-exploit-kit-delivering-grobios-trojan.html](https://www.fireeye.com/blog/threat-research/2018/05/deep-dive-into-rig-exploit-kit-delivering-grobios-trojan.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01f2f44fb20a9724af.jpg)](https://p5.ssl.qhimg.com/t01f2f44fb20a9724af.jpg)

## 概述

正如在此前博客（ [https://www.fireeye.com/blog/threat-research/2017/10/magniber-ransomware-infects-only-the-right-people.html](https://www.fireeye.com/blog/threat-research/2017/10/magniber-ransomware-infects-only-the-right-people.html) ）中所讨论的，自2016年下半年以来，漏洞利用工具包（Exploit Kit）的相关活动一直呈下降趋势。不过，我们仍然在持续监测这一领域的发展状况，同时也一直在观察RIG Exploit Kit（EK）的持续活动情况。尽管根据我们监测的结果，该组织在野通信量持续下降，但它仍然保持活跃状态，并且与相当广泛的恶意软件Payload存在关联。<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig1.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig1.png)<br>
我们首次监测到与该组织相关的情报，是在3月10日发现域名latorre[.]com[.]au被入侵，发现该域名通过注入恶意iframe的方式，被重定向到RIG EK组织所掌控的地址。<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig2.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig2.png)<br>
在这里，iframe会加载一个使用SSL进行通信的恶意域名（证书如下图所示），并转向能加载恶意Flash文件的RIG EK的页面。<br>
恶意SSL流：<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig3.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig3.png)<br>
RIG EK SWF下载请求：<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig4.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig4.png)<br>
当打开Flash文件后，该文件会投放Grobios木马。下图展示了Grobios木马的相关通信内容：<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig5.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig5.png)



## 投放的恶意软件分析

Grobios木马使用了多种技术来逃避检测，并试图在主机上获得持久性，这使得它很难被卸载，也难以在被感染主机上停用。此外，该木马还使用了多种反调试、反分析和反虚拟机技术来隐藏其行为。当木马在被感染主机上成功安装后，它将连接到命令和控制（C&amp;C）服务器，在C&amp;C服务器的响应信息中包含发布的命令。<br>
为了逃避静态检测，木马作者采用了PECompact 2.xx对样本进行加壳。脱壳后的样本在导入表中没有函数项。该木马使用了API哈希加密的方法，用来混淆其调用的API函数名称，并通过分析DLL文件PE头的方式来将函数的名称与其哈希值进行比对。此外，恶意软件也会使用栈字符串。下图是恶意软件使用哈希值调用WinApi的一个示例：<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig6.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig6.png)



## 加载

恶意软件样本会启动自身的副本，根据用户权限级别，将其代码进一步注入到svchost.exe或IEXPLORE.EXE中。在完成注入后，其父进程和子进程都会退出，只有svchost.exe或IEXPLORE.EXE会继续运行。进程树如下：<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig7.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig7.png)



## 持久化

该恶意软件的持久化方法非常具有攻击性，具体采用了以下技术：<br>
1、该恶意软件将其自身的副本保存在%APPDATA%文件夹，伪装成安装在被感染主机上的合法软件，并在Windows启动（Startup）文件夹中创建一个自动运行的注册表项和一个快捷方式。经过我们的分析，快捷方式指向路径%APPDATA%Googlev2.1.13554&lt;RandomName&gt;.exe。该路径可能会根据恶意软件在%APPDATA%中发现的文件夹而有所变化。<br>
2、该恶意软件将自身的多个副本保存在程序的子文件夹中，目录为%ProgramFiles%/%PROGRAMFILES(X86)%会再次伪装成另一个版本的已安装程序，并设置自动运行注册表项或创建计划任务。<br>
3、该恶意软件将自身的副本保存在%Temp%文件夹中，并创建一个计划任务来运行这个副本。<br>
在受感染的系统上，恶意软件会创建两个计划任务，如下图所示。<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig8.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig8.png)<br>
恶意软件会将其所有副本的创建、修改和访问时间修改为ntdll.dll的上一次修改时间。同时，为了绕过“此文件是从Internet下载”的警告提示，恶意软件会使用DeleteFile API删除:Zone.Identifier标志，如下图所示。<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig9.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig9.png)<br>
该恶意软件的另外一个行为特征是，它会使用EFS（Windows加密文件系统）保护其在%TEMP%文件夹中的副本，如下图所示。<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig10.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig10.png)



## 检测虚拟机和恶意软件分析工具

在连接到C&amp;C服务器之前，恶意软件会执行一系列检查来检测是否存在虚拟机或恶意软件分析环境。该恶意软件可以检测几乎所有知名的虚拟机产品，包括Xen、QEMU、VMWare、Virtualbox、Hyper-V等。以下是该恶意软件在被感染主机上执行的检查列表：<br>
1、使用FindWindowEx API，检查系统中是否有任何分析工具正在运行。

```
Analysis Tools
PacketSniffer
FileMon
WinDbg
Process Explorer
OllyDbg
SmartSniff
cwmonitor
Sniffer
Wireshark
```

2、恶意软件中包含一个黑名单进程的哈希值列表，会检查系统正在运行进程的哈希值是否与黑名单上的哈希值匹配，如下图所示。<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig11.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig11.png)<br>
根据上述哈希值，我们找到了对应的黑名单进程。

```
283ADE38h    vmware.exe
8A64214Bh    vmount2.exe
13A5F93h    vmusrvc.exe
0F00A9026h    vmsrvc.exe
0C96B0F73h    vboxservice.exe
0A1308D40h    vboxtray.exe
0E7A01D35h    xenservice.exe
205FAB41h    joeboxserver.exe
6F651D58h    joeboxcontrol.exe
8A703DD9h    wireshark.exe
1F758DBh    Sniffhit.exe
0CEF3A27Ch    sysAnalyzer.exe
6FDE1C18h    Filemon.exe
54A04220h    procexp.exe
0A17C90B4h    Procmon.exe
7215026Ah    Regmon.exe
788FCF87h    autoruns.exe
0A2BF507Ch   ?
0A9046A7Dh    ?
```

3、对以下路径中的注册表项进行遍历，检查其中是否包含单词xen或VBOX：

```
HKLMHARDWAREACPIDSDT
HKLMHARDWAREACPIFADT
HKLMHARDWAREACPIRSDT
```

4、检查系统上安装的服务是否包含下表中的任意关键字：

```
vmmouse
vmdebug
vmicexchange
vmicshutdown
vmicvss
vmicheartbeat
msvmmouf
VBoxMouse
vpcuhub
vpc-s3
vpcbus
vmx86
vmware
VMMEMCTL
VMTools
XenVMM
xenvdb
xensvc
xennet6
xennet
xenevtchn
VBoxSF
VBoxGuest
```

5、检查用户名是否包含关键词MALWARE、VIRUS、SANDBOX、MALTEST。<br>
6、使用FindFirstFile/FindNextFile API，遍历Windows驱动程序目录%WINDIR%system32drivers，检查驱动程序名称是否与黑名单中的驱动名称哈希值相匹配：

```
0E687412Fh    hgfs.sys
5A6850A1h    vmhgfs.sys
0CA5B452h    prleth.sys
0F9E3EE20h    prlfs.sys
0E79628D7h    prlmouse.sys
68C96B8Ah    prlvideo.sys
0EEA0F1C2h    prl_pv32.sys
443458C9h    vpcs3.sys
2F337B97h    vmsrvc.sys
4D95FD80h    vmx86.sys
0EB7E0625h    vmnet.sys
```

7、计算出ProductId的哈希值，将其与3个列入黑名单中的哈希值进行匹配，以检测其是否在公共沙箱中运行：

```
Hash                Product Id                               Sandbox Name
4D8711F4h      76487-337-8429955-22614    Anubis Sanbox
7EBAB69Ch    76487-644-3177037-23510    CWSandbox
D573F44D       55274-640-2673064-23950    Joe Sandbox
```

8、恶意软件会计算DLL名称的哈希值，并将其与黑名单中的哈希值进行比较。这些DLL通常加载到正在调试的进程中，例如dbhelp.dll和api_log.dll。

```
6FEC47C1h
6C8B2973h
0AF6D9F74h
49A4A30h
3FA86C7Dh
```

下图是检查DLL哈希值是否在黑名单中这一功能的代码流：<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig12.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig12.png)<br>
9、检查HKLMSYSTEMCurrentControlSetServicesDiskEnum和HKLMSYSTEMControlSet001ServicesDiskEnum中存在的注册表项是否包含QEMU、VBOX、VMWARE、VIRTUAL。<br>
10、检查HKLMSOFTWAREMicrosoft和 HKLMSOFTWARE中存在的注册表项是否包含VirtualMachine、vmware、Hyber-V。<br>
11、检查HKLMHARDWAREDESCRIPTIONSystemSystemBiosVersion中存在的注册表项是否包含QEMU、BOCHS、VBOX。<br>
12、检查HKLMHARDWAREDESCRIPTIONSystemVideoBiosVersion中存在的注册表项是否包含VIRTUALBOX字符串。<br>
13、检查HKLMHARDWAREDEVICEMAPScsiScsi Port 0Scsi Bus 0Target Id 0Logical Unit Id 0Identifier中存在的注册表项是否包含QEMU、vbox、vmware。<br>
14、检查系统是否存在注册表项HKLMSOFTWAREOracleVirtualBox Guest Additions。



## 网络通信

该恶意软件以硬编码的方式包含两个混淆后的C&amp;C地址。在对C&amp;C URL进行反混淆后，恶意软件会生成一个20个字符的随机字符串，将其附加到URL的末尾，并发送命令请求。在执行命令之前，恶意软件会验证C&amp;C的身份。它使用CALG_MD5算法计算4个字节数据的散列值，然后使用来自CERT命令的Base64数据作为CryptVerifySignature的公钥来验证散列签名（如下图所示）。如果签名验证成功，恶意软件将会执行命令。<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig13.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig13.png)<br>
经过分析，我们发现该恶意软件支持如下命令：<br>
CERT &lt;Base64数据&gt;：包含用于验证C&amp;C身份的数据。<br>
CONNECT &lt;IP:端口&gt;：连接到指定主机，以获取更多命令。<br>
DISCONNECT：关闭所有连接。<br>
WAIT &lt;秒数&gt;：执行下一个命令之前，等待指定的秒数。<br>
REJECT：一种NOP，等待5秒钟后再继续下一个命令。<br>
下图中展示了C&amp;C服务器发出的命令：<br>[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig14.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/Grobios/Fig14.png)



## 结论

尽管该类活动不断减少，但漏洞利用工具包所造成的风险仍然是不可小觑的，特别是针对于使用旧版本软件的用户。对于企业管理人员来说，务必要确保企业中的所有网络节点都及时打上了补丁。<br>
最后，感谢Mariam Muntaha女士对本文中恶意浏览分析部分做出的贡献。



## IoC

30f03b09d2073e415a843a4a1d8341af<br>
77d5f1d45cd9c8af67eadc490967da35<br>
a43404b5ae1aee40ee98c9fd152d565c<br>
99787d194cbd629d12ef172874e82738<br>
169.239.129[.]17<br>
104.144.207[.]211<br>
grobiosgueng[.]su
