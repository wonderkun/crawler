> 原文链接: https://www.anquanke.com//post/id/85325 


# 【木马分析】针对升级后Shifu银行木马的深度分析


                                阅读量   
                                **123380**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：researchcenter.paloaltonetworks.com
                                <br>原文地址：[http://researchcenter.paloaltonetworks.com/2017/01/unit42-2016-updates-shifu-banking-trojan/](http://researchcenter.paloaltonetworks.com/2017/01/unit42-2016-updates-shifu-banking-trojan/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t011e4b4ebfd45efbd4.jpg)](https://p4.ssl.qhimg.com/t011e4b4ebfd45efbd4.jpg)

****

**翻译：**[**myswsun******](http://bobao.360.cn/member/contribute?uid=2775084127)

**预估稿费：260RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**0x00 前言**

银行木马Shifu在2015年首次被披露。Shifu是基于Shiz的代码整合了Zeus的技术。攻击者用Shifu盗取俄罗斯、英国、意大利等其他国家的网上银行的网站的证书。

Palo Alto Networks Unit 42研究发现Shifu的作者在2016年更新了。我们的研究发现Shifu整合了多种新技术和躲避检测技术。有些如下：

利用Windows的CVE-2016-0167的提权漏洞获得SYSTEM权限。之前的Shifu使用CVE-2015-0003达到相同的目的

用一个Windows的atom来判断之前版本是否感染。

用“push-calc-ret”API混淆技术在恶意软件分析时隐藏函数调用

用可变的.bit域名

我们也确认了新的链接暗示了Shifu可能不是基于Shiz木马，但是可能是最新版Shiz的变种。

本文主要的目的是介绍Shifu的新特征。下面是新特征的概述，在最后的附录包括详细的技术细节。

<br>

**0x01 Shifu的开发与新特征**

本文分析的Shifu是由几步payload组成，在2016年编译的。下图说明了在执行后解密的原始loader包含的不同的文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d75b742bd36c1f0d.png)

图1. Shifu的文件结构

原始的混淆的loader（x86 exe）包含加密的二级injector（x86 exe）。它用了3层解密，子过程用函数VirtualAlloc()为下一层分配内存。二级injector被解密到内存中并且原始loader覆写它。接下来节标志被调整和IAT重建。最后跳转到二级injector的入口点执行。

二级injector包含两个CVE-2016-0167（x86/x64）的利用，编译于2016年2月。在这个编译的时间这个漏洞的补丁还不存在。然而这个恶意程序的编译时间是2016年6月。这个可能暗示在这个版本之后有人在那时能获得0day利用。这个利用用了一个有趣的技术使复制原始数据到内存成为可能。为了使可执行文件能在内存中执行，它用了一个自定义的shellcode型PE加载器作为PE overlay数据追加在这两个版本的利用后面。Shellcode充分调整内存数据以获得一个可靠的可执行文件的内存映像并执行利用。这么做，文件只需要被拷贝进内存中，通过shellcode就能执行。

我们也发现多种其他的独立版本的利用（x86/x64），但是也是像Shifu一样被嵌入在injector中。另外，我们确定一个版本的Vawtrak包含了早期的利用，根据编译时间可以追溯到2015年11月。这个Vawtrak样本自己的编译时间是2016年1月，因此是第一个为我们知道的利用这个漏洞的样本。

二级injector包含了集中反分析技巧，由于之前版本相同。它也包含两种命令行参数说明这个恶意程序还在开发中。另外，二级injector用一个atom校验系统是否已经被感染，而不是使用现在最常用的互斥量。Atom的用法不是一个新的技术但是没有被广泛使用。

Main payload加密压缩的存储与二级injector的.tls节中。它首先用aPlib库解密解压。Main payload把原始loader拷贝到AppData目录并在启动目录创建一个Jscript文件。二级injector将main payload注入到32位的svchost实例中，用一个混淆技术给它的API函数打补丁，使得静态和动态分析变得更加困难。

和前一个版本比较，这个main payload包含了一些更新。包括在受害者系统上搜索的字符串、浏览器列表、命令。Main payload用顶级域名.bit作为C&amp;C服务器。域名、user-agent字符串和URL参数用修改版的RC4算法加密。域名暗示了攻击者可能位于乌克兰或有乌克兰背景。

不幸的是，在分析时这个C&amp;C服务器不能响应任何命令了，因此进一步的分析不太可能。这个信息被正常的下载到受害者的磁盘上。功能上，这个main payload挂钩svchost.exe进程的一些API函数。而且，它用Apache服务器做web注入。如果成功的从C&amp;C服务器，恶意软件利用分层服务挂钩winsock API，用于拦截和修改出入的网络流量。它也使用在其他银行木马中发现的正常的方法挂钩到浏览器网络函数。

二级injector和main payload都包含了大量的从没使用过的字符串。这个说明作者不是匆忙编译了恶意程序就是开发过程缓慢。

“IntelPowerAgent6”能在上个版本看见，这个版本没看见有“IntelPowerAgent32“。为了二级injector能够创建一个用来校验系统是否被感染的atom，这个main payload也创建了一个基于相同方法的互斥量（详见附录）。然而这个互斥量用了一个硬编码的前缀“DAN6J0-”放在一个字节序列的前面：“`{`DAN6J0-ae000000d2000000e100`}`”。

[![](https://p5.ssl.qhimg.com/t017fd1288c87daa022.png)](https://p5.ssl.qhimg.com/t017fd1288c87daa022.png)

图2. Shifu的互斥量和相关的svchost进程

<br>

**0x02 Shifu,Shiz和其他相关的工具**

银行木马Shifu是基于一个目前还存活的比较老的名为Shiz/iBank的源码。Shiz首先被发现于2006年，已经发展了好几代。它以前专注于俄罗斯经融机构。后来变得国际化转向了意大利的银行。过去5年我们跟踪到了多个版本：2代到4代（2011年），5代（2013年/2014年）。上一次看到还是在2014年（内部版本是5.6.25）,并且它的代码风格不同于第4代。它看起来像是另一个人开发的，可能说明代码被卖或分享。连接C&amp;C服务器的查询字符串很好的支持了我们的想法：

```
botid=%s&amp;ver=5.0.1&amp;up=%u&amp;os=%03u&amp;ltime=%s%d&amp;token=%d&amp;cn=reborn&amp;av=%s
```

我们看到组织名包含字符串“reborn”（重生）。

Shifu首先被发现于2015年中期，并且我们认为Shiz发展了5代，变得更加国际化。

过去几年我们不仅跟踪了Shiz，也发现了几个号称来自相同作者的其他的恶意工具。收集样本说明了作者已经开发了一整套金融相关的恶意程序。不清楚作者是不是为一个组织工作或者他们自己单独行动。这些工具主要第五代Shiz的代码。

我们能将这些工具联系在一起，因为他们都包含相同根目录的PDB路径：

```
Z:coding…
```

而且，大部分工具也是基于Shiz代码的，因为代码风格和使用的API很相似。同时用bindiff比较工具代码也高度相似。这些工具网络功相关的字符串也和Shiz连接C&amp;C服务器的类似。

根据去年来自FireEye的同事描述，PDB路径也是如下：

```
Z:codingprojectmainpayloadpayload.x86.pdb
```

其他工具有以下的PDB路径，很像来自同一个作者：



```
Z:codingcryptorReleasecrypted.pdb
Z:codingmalwaretestsReleasecryptoshit.pdb
Z:codingmalwareRDPoutputReleaserdp_bot.pdb
Z:codingmalwareScanBotReleasebot.pdb
```

内部名为“cryptor”的恶意程序包含了一个加密的样本“BifitAgent”，这个恶意程序攻击金融业软件。BifitAgent的作者也可能是同一个，不过我们没有发现一些证据。根据编译时间，大部分样本创建于2013年的10月和11月。

名为“rdp_bot”是一个用远程桌面协议获取访问计算机的权限的恶意程序。它用和Shifu一样的被修改的RC4加密算法。这个工具可能和Shiz一起使用，因为攻击者能够直接用受害者的电脑做欺诈行为。通过这么做，能够欺骗银行的校验IP地址、浏览器指纹或键盘布局的反欺诈系统。这个工具基于Alisa Esage的RDP研究。这个样本可以追溯到2013年11月。

名为“cryptoshit”的工具包含了加密的rdp_bot样本，并且用了相同的修改版RC4加密算法。这个样本追溯到2013年9月和10月，2014年的1月。

内部名为“ScanBot”的恶意程序是一个小的后门程序，它使用了一个超级轻量的正则库来扫描受害者电脑的文件。这个样本追溯到2013年6月。

<br>

**0x03 样本**

Initial obfuscated loader



```
d3f9c4037f8b4d24f2baff1e0940d2bf238032f9343d06478b5034d0981b2cd9
368b23e6d9ec7843e537e9d6547777088cf36581076599d04846287a9162652b
e7e154c65417f5594a8b4602db601ac39156b5758889f708dac7258e415d4a18
f63ec1e5752eb8b9a07104f42392eebf143617708bfdd0fe31cbf00ef12383f9
```

Second stage injector



```
003965bd25acb7e8c6e16de4f387ff9518db7bcca845502d23b6505d8d3cec01
1188c5c9f04658bef20162f3001d9b89f69c93bf5343a1f849974daf6284a650
```

Exploit injector

```
e7c1523d93154462ed9e15e84d3af01abe827aa6dd0082bc90fc8b58989e9a9a
```

CVE-2016-0167 exploit (x86)

```
5124f4fec24acb2c83f26d1e70d7c525daac6c9fb6e2262ed1c1c52c88636bad
```

CVE-2016-0167 exploit (x64)

```
f3c2d4090f6f563928e9a9ec86bf0f1c6ee49cdc110b7368db8905781a9a966e
```

Main payload



```
e9bd4375f9b0b95f385191895edf81c8eadfb3964204bbbe48f7700fc746e4dc
5ca2a9de65c998b0d0a0a01b4aa103a9410d76ab86c75d7b968984be53e279b6
```



**0x04 附录——技术细节**

**Second Stage Injector 分析**

这个second stage injector是包含了一个利用injector（x86 DLL），继而包含两个内嵌的CVE-2016-0167利用（x86/x64 DLL）。second stage injector也包含一个加密的并用aPlib压缩的main payload（x86 DLL），位于它的.tls节区。为了解密，它用一个修改版RC4加密算法解密存储在.rsrc节的数据。重要的字符串在.data节，并用密码0x8D异或加密。解密后的字符串如下：



```
AddMandatoryAce
ADVAPI
Advapi32.dlladvapi32.dllws2_32.dll
WPUCloseEvent
WPUCloseSocketHandleWPUCreateEvent
WPUCreateSocketHandle
WPUFDIsSet
WPUGetProviderPath
WPUModifyIFSHandle
WPUPostMessage
WPUQueryBlockingCallbackWPUQuerySocketHandleContext
WPUQueueApc
WPUResetEvent
WPUSetEvent
WPUOpenCurrentThreadWPUCloseThread
WSPStartup
 &gt; %1rndel %0
software\microsoft\windows\currentversion\run
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/echo 
rundll32.exe shell32.dll, ShellExec_RunDLL %s
Microsoft\Microsoft AntimalwareSoftware\Coranti
Software\risingSoftware\TrendMicroSoftware\Symantec
Software\ComodoGroup
Software\Network Associates\TVD
Software\Data Fellows\F-SecureSoftware\Eset\Nod
Software\Softed\ViGUARD
Software\Zone Labs\ZoneAlarm
Software\Avg
Software\VBA32
Software\Doctor WebSoftware\G DataSoftware\Avira
Software\AVAST Software\Avast
Software\KasperskyLab\protected
Software\Bitdefender
Software\Panda SoftwareSoftware\Sophos.bat\\.\%C:
|$$$`}`rstuvwxyz`{`$$$$$$$&gt;?@ABCDEFGHIJKLMNOPQRSTUVW$$$$$$XYZ[\]^_`abcdefghijklmnopq
conhost
CreateProcessInternalW
ConvertStringSecurityDescriptorToSecurityDescriptorWContent-Type: multipart/form-data; boundary=---------------------------%srn
Content-Type: application/x-www-form-urlencodedrn
Host: %srn%d.%d.%d.%d
%d.%d.%d.%d.%x
%temp%\debug_file.txt
[%u][%s:%s:%u][0x%x;0x%x] %sDnsFlushResolverCache
\*.*
dnsapi.dll
DnsGetCacheDataTable.dll.exedownload.windowsupdate.com
vk.com
yandex.ru
HTTP/1.1https://http://%s
IsWow64Process
kernel
kernel32.dllLdrGetProcedureAddress
Microsoft
NtAllocateVirtualMemory
CLOSED
LAST_ACKTIME_WAIT
DELETE_TCB
LISTEN
SYN_SENTSYN_RCVDESTAB
FIN_WAIT1
FIN_WAIT2
CLOSE_WAIT
CLOSING
TCPt%s:%dt%s:%dt%sn
netstatnPrototLocal addresstRemote addresstStaten
ntdll.dll
NtResumeProcess
NtSuspendProcess\\?\globalroot\systemroot\system32\drivers\null.sys
NtWriteVirtualMemoryopenRegisterApplicationRestart
RtlCreateUserThread
ResetSR
RtlComputeCrc32
rundll32SeDebugPrivilegeSystemDrive
\StringFileInfo\%04x%04x\ProductName
software\microsoft\windows nt\currentversion\winlogon
shell
Sleep
srclient.dllSeShutdownPrivilege
"%s"
%dt%sntaskmgrnPIDtProcess namennet usern
the computer is joined to a domainn..
\VarFileInfo\Translation
%windir%\system32\%windir%\syswow64\POST*.exe
%SystemDrive%\
*SYSTEM*%02x%s:Zone.Identifier
GetProcessUserModeExceptionPolicy
SetProcessUserModeExceptionPolicy
%ws\%wsn
WORKGROUP
HOMESoftware\Microsoft\Windows\CurrentVersion\Policies\ExplorerDisableCurrentUserRun
%s.dat
software\microsoft\windows%OS%_%NUMBER_OF_PROCESSORS%
S:(ML;;NRNWNX;;;LW)D:(A;;GA;;;WD)
S:(ML;;NRNWNX;;;LW)D:(A;;GA;;;WD)(A;;GA;;;AC)
\\.\AVGIDSShim
FFD3\\.\NPF_NdisWanIpc:\sample\pos.exe
ANALYSERS
SANDBOX
VIRUS
MALWARE
FORTINETMALNETVMc:\analysis\sandboxstarter.exec:\analysisc:\insidetmc:\windows\system32\drivers\vmmouse.sys
c:\windows\system32\drivers\vmhgfs.sys
c:\windows\system32\drivers\vboxmouse.sys
c:\iDEFENSEc:\popupkiller.exe
c:\tools\execute.exe
c:\Perlc:\Python27api_log.dll
dir_watch.dll
pstorec.dll
dbghelp.dll
Process32NextW
Software\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3
1406.bitMiniDumpWriteDump
rnReferer: %srn
\Google\Chrome\User Data\Default\Cache
var %s = new ActiveXObject("WScript.Shell"); %s.Run("%s");
IntelPowerAgent32
%OS%_%NUMBER_OF_PROCESSORS%
%scmd.exe
ComSpec
ConsoleWindowClass
.exekernel32.dllntdll.dll
ZwQuerySystemInformationZwAllocateVirtualMemory
PsLookupProcessByProcessId
PsReferencePrimaryToken
Class
Window
open "%s" -q%windir%\system32\sdbinst.exe
 /c "start "" "%s" -d"
%windir%\system32\sndvol.exe
 "%s" -u /c "%s\SysWOW64\SysSndVol.exe /c "start "" "%s" -d""
%temp%\%u
%u.tmp
Wow64DisableWow64FsRedirection
Wow64RevertWow64FsRedirection
runas.exe
%systemroot%\system32\svchost.exe
%systemroot%\system32\wscript.exe
snxhk.dll
sbiedll.dll
 /c start "" "%s" " "
cmd.exe
runas
 --crypt-test
It work's!
 --vm-test
```

**内嵌CVE-2016-0167利用的exploit injector**

Exploit injector被用来在被感染的主机上面获取SYSTEM权限。这个注入器同时包含x86和x64利用。“MZ”字符用null字节替换用来防止被检测。

Second stage injector会校验当前京城的完整性级别和操作系统版本。如果进程的完整性级别是低并且操作系统版本是6.1（Windows 7/Windows Server 2008 R2），second stage injector将exploit injector文件写入内存。然后在exploit injector中搜索0x99999999。当地址被找到时，12个字节被添加并且second stage injector跳转到PE loader中。调用到shellcode的如下：



```
00401EF5   pusha
00401EF6   add esi, 0Ch
00401EF9   call esi   -&gt; PE loader shellcode in overlay
00401EFB   popa
```

**自定义PE loader**

它首先获得shellcode的结尾，用来扫描exploit injector文件的“MZ“：



```
00077174   jmp short 00077178
00077176   pop eax
00077177   retn
00077178   call 00077176
```

接下来，一个自己写的GetProcAddress()函数用来获取VirtualAllocEx()函数地址。然后，VirtualAllocEx()用来分配一个内存空间，能够将exploit injector节信息以适当的内存对齐的方式写入该内存。必要的地址重定位调整，API函数地址重新解析，IAT重新填充。最后shellcode跳转到新创建的exploit injector的DLL的入口点。

**Exploit injector**

首先，字符串“kernel32.dll”，“LoadLibrary“，”GetProcAddress“被创建。然后kernel32.dll的模块地址被搜索到，继而得到LoadLibrary()和GetProcAddress()的地址。在这些函数的帮助下，exploit injector的IAT被重建。这个功能的目的不清楚，因为它已经被second stage injector完成了。然后，用CreateThread()函数创建一个新的线程。

这个线程调用IsWow64Process()，根据结果决定x86还是x64版本的利用文件被写入内存。“MZ”写入利用文件的开始。然后，一个名为“WaitEventX”的事件被创建，这个事件稍后被利用使用。最后这个主利用加载函数被调用。

这个主利用加载函数搜索以下进程，这些进程是趋势安全软件的一部分：



```
“uiSeAgnt.exe”
“PtSessionAgent.exe”
“PwmSvc.exe”
“coreServiceShell.exe”
```

如果有一个进程被找到，一个挂起的wuauclt.exe被创建。否则，一个挂起的svchost.exe被创建。在两种情况下，都使用命令行参数“-k netsvc”，但是只被svchost.exe使用。应该注意到的是这个功能在x64版本的趋势安全软件安装的情况下总是失败的。代码（x86）在x64进程中调用调用CreateToolhelp32Snapshot()函数将导致ERROR_PARTIAL_COPY错误。而且，它也总是会失败，因为没有没有权限访问趋势进程。

接下来，它用CreateFileMapping()和MapViewOfFile()函数将x86或x64的利用文件映射进内存并在内存中填充利用字节。最终，节被用ZwMapViewOfSection()函数映射到挂起的进程svchost.exe或wuauclt.exe中。如果系统版本是5.2（Windows Server2003和Windows XP 64位版本）将直接退出。然后，两个内存空间被创建，一个shellcode被写入内存中。第一个混淆的shellcode调用第二个shellcode。接下来，调用ResumeThread()函数恢复挂起的进程，利用就被执行了。

Second stage injector验证利用成功与否，通过检验完整性等级是否一直是SECURITY_MANDATORY_LOW_RID。如果不是，利用成功的话将提权至SECURITY_MANDATORY_SYSTEM_RID，并且继续main payload的注入。如果利用失败，它将尝试自己用cmd.exe和runas.exe来运行自身获取SYSTEM的权限。

**Atom字符串的创建**

代替当今常用的互斥量，second stage injector创建了一个atom和校验这个全局atom表来判断Shifu是否已经运行。

首先，它用字符串“%OS%_%NUMBER_OF_PROCESSORS%”调用ExpandEnvironmentStrings()函数来获取Windows版本和处理器数目。例如在1个处理器的Windows 7上面结果就是“Windows_NT_1”。这个字符串被用来调用RtlComputeCrc32()函数计算4个CRC32哈希值，四个初始值如下：



```
0xFFFFFFFF
0xEEEEEEEE
0xAAAAAAAA
0x77777777
```

字符串“Windows_NT_1”的哈希结果如下：



```
0x395693AE
0xB24495D2
0xF39F86E1
0xBAE0B5C8
```

接下来，每个CRC哈希的最后一个字节在栈上面是以DWORD存储的：



```
0xAE000000
0xD2000000
0xE1000000
0xC8000000
```

字节序列如下：

```
AE 00 00 00 D2 00 00 00 E1 00 00 00 C8 00 00 00
```

这个atom字符串用snprintf()函数转化前8个字节到ASCII字符串中，结果如下：

```
“ae000000d2000000”
```

最后，调用GlobalFindAtom()函数是否存在，如果不存在则调用GlobalAddAtom()添加。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0151f24bab470feb82.png)

图3. 在全局atom表中的Shifu的atom

**命令行参数**

Second stage injector有两个命令行，但是只有一个起作用。他们在将来可能有一个新功能或者只是忘了删除了。

```
-crypt-test
```

只有一个包含“It work’s!”的消息框显示：

```
-vm-test
```

没啥功能

**反分析技巧**

反Sandboxie和Avast，Shifu在它自己的进程内调用GetModuleHandleA()函数校验snxhk.dll(Avast)或者sbiedll.dll(Sandboxie)是否存在，如果存在将调用Sleep()永久休眠。

所有的下面的检测手段都是32位操作系统下的。

**进程名检测**

枚举运行的进程名，转化为小写，计算那些名字的CRC32哈希值，按下面列表比较：



```
0x99DD4432 – ?
0x1F413C1F – vmwaretray.exe
0x6D3323D9 – vmusrvc.exe
0x3BFFF885 – vmsrvc.exe
0x64340DCE – ?
0x63C54474 – vboxtray.exe
0x2B05B17D – ?
0xF725433E – ?
0x77AE10F7 – ?
0xCE7D304E – dumpcap.exe
0xAF2015F2 – ollydbg.exe
0x31FD677C – importrec.exe
0x6E9AD238 – petools.exe
0xE90ACC42 – idag.exe
0x4231F0AD – sysanalyzer.exe
0xD20981E0 – sniff_hit.exe
0xCCEA165E – scktool.exe
0xFCA978AC – proc_analyzer.exe
0x46FA37FB – hookexplorer.exe
0xEEBF618A – multi_pot.exe
0x06AAAE60 – idaq.exe
0x5BA9B1FE – procmon.exe
0x3CE2BEF3 – regmon.exe
0xA945E459 – procexp.exe
0x877A154B – peid.exe
0x33495995 – autoruns.exe
0x68684B33 – autorunsc.exe
0xB4364A7A – ?
0x9305F80D – imul.exe
0xC4AAED42 – emul.exe
0x14078D5B – apispy.exe
0x7E3DF4F6 – ?
0xD3B48D5B – hookanaapp.exe
0x332FD095 – fortitracer.exe
0x2D6A6921 – ?
0x2AAA273B – joeboxserver.exe
0x777BE06C – joeboxcontrol.exe
0x954B35E8 – ?
0x870E13A2 – ?
```

**文件名检测**

Shifu校验下面文件或文件夹是否存在，如果存在则调用Sleep()永久休眠：



```
c:samplepos.exe
c:analysissandboxstarter.exe
c:analysis
c:insidetm
c:windowssystem32driversvmmouse.sys
c:windowssystem32driversvmhgfs.sys
c:windowssystem32driversvboxmouse.sys
c:iDEFENSE
c:popupkiller.exe
c:toolsexecute.exe
c:Perl
c:Python27
```

**调试器检测**

调用IsDebuggerPresent()判断调试器是否存在。同时，调用ZwQueryInformationSystem()判断ProcessDebugPort和ProcessDebugObjectHandle。如果调试器被检测到则调用Sleep()永久休眠。

**Wireshark检测**

调用CreateFile()尝试打开\.NPF_NdisWanIp，如果过成功则调用Sleep()永久休眠。

**自我检验**

校验自己的名字长度，如果长于30个字符则调用Sleep()永久休眠。同时用CRC32哈希值校验自己的进程名：



```
0xE84126B8 – sample.exe
0x0A84E285 – ?
0x3C164BED – ?
0xC19DADCE – ?
0xA07ACEDD – ?
0xD254F323 – ?
0xF3C4E556 – ?
0xF8782263 – ?
0xCA96016D – ?
```

而且，判断自己的进程中是否有来自GFI沙箱的模块：



```
api_log.dll
dir_watch.dll
pstorec.dll
```

**未知的反分析技巧**

用了一个不知道目的的技巧。它获取Process32NextW()函数的地址，前五个字节和序列0x33C0C220800比较：



```
33C0  XOR EAX,EAX
C2 0800   RETN 8
```

这些代码只能在32位的Windows XP使用，因为Unicode版本的函数可能还没实现。如果代码序列被检测到，将调用Sleep()永久休眠。

**Windows域名校验**

用NetServerGetinfo()和NetWkstaGetInfo()判断计算机工作组名是否是“WORKGROUP”或“HOME”。如果不是则永久休眠。接下来判断是否是”ANALYSERS”，如果是则永久休眠。

**计算机和用户名校验**

用GetComputerName()和GetUserName()获取计算机名和用户名，判断是否是如下字符串：



```
SANDBOX
FORTINET
VIRUS
MALWARE
MALNETVM
```

如果被发现一个，则永久休眠。

**进程结束特征**

Second stage injector枚举所有运行的进程，将名字转化为小写，计算CRC32的哈希值：



```
0xD2EFC6C4 – python.exe
0xE185BD8C – pythonw.exe
0xDE1BACD2 – perl.exe
0xF2EAA55E – autoit3.exe
0xB8BED542 – ?
```

如果有一个被匹配到，尝试打开进程并结束进程。如果过失败，将尝试用ZwClose关闭进程的主窗口句柄。然后以所有权限打开进程，用ZwUnmapViewOfSection()函数卸载它。最后，被卸载的进程的主窗口句柄被关闭。

**Main payload解密、解压和注入**

为了解密main payload，second stage injector从.rsrc节获取解密算法需要用到的数据。它使用一个修改版的RC4算法，之前获得的值与256字节数组的每个字节异或。加密过的数组用来解密位于.tls节的main payload。解密的main payload还被aPlib库压缩了。

如果原始的loader作为一个中等级或高等级的进程运行，计算atom字符串的方法再次被调用。这次只有4个字节被用来创建字符串，例如“ae000000”。接下来，哈希值被计算出来，并通过从0x0到0xFF与另一个256字节的数组异或。这个加密的字符串再次被用来加密和解密main payload。为了持续性，加密的数据被写入注册表“HKCUsoftwaremicrosoftwindows”键值中，如”f4e64d63”。同时，“ae000000”也被创建并用空字符串和原始的loader的路径填充。最后临时加密的main payload再次被解密。

[![](https://p1.ssl.qhimg.com/t016d2d97f5fe29306b.png)](https://p1.ssl.qhimg.com/t016d2d97f5fe29306b.png)

图4. 加密的main payload和原始loader的路径被存储在Windows注册表中

接下来，main payload在内存中被解压。然后，一个挂起的svchost.exe(x86)被以和父进程相同的完整性等级创建。Main payload被映射到进程中并且“MZ”被修改掉。Svchost进程恢复则main payload被执行。最后，一个批处理文件被创建在%TEMP%文件夹中。

**Main payload 分析**

Main payload的模块的IAT函数与0xFF异或加密使得静态分析更加困难。在.data节中的重要的字符串也与0x8D异或加密，解密字符串如下：



```
AddMandatoryAce
ADVAPI
Advapi32.dlladvapi32.dllws2_32.dll
WPUCloseEvent
WPUCloseSocketHandleWPUCreateEvent
WPUCreateSocketHandle
WPUFDIsSet
WPUGetProviderPath
WPUModifyIFSHandle
WPUPostMessage
WPUQueryBlockingCallbackWPUQuerySocketHandleContext
WPUQueueApc
WPUResetEvent
WPUSetEvent
WPUOpenCurrentThreadWPUCloseThread
WSPStartup
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/echo 
 &gt; %1rndel %0
rundll32.exe shell32.dll, ShellExec_RunDLL %s
software\microsoft\windows\currentversion\run
Microsoft\Microsoft AntimalwareSoftware\Coranti
Software\risingSoftware\TrendMicroSoftware\Symantec
Software\ComodoGroup
Software\Network Associates\TVD
Software\Data Fellows\F-SecureSoftware\Eset\Nod
Software\Softed\ViGUARD
Software\Zone Labs\ZoneAlarm
Software\Avg
Software\VBA32
Software\Doctor WebSoftware\G DataSoftware\Avira
Software\AVAST Software\Avast
Software\KasperskyLab\protected
Software\Bitdefender
Software\Panda SoftwareSoftware\Sophos.bat|$$$`}`rstuvwxyz`{`$$$$$$$&gt;?@ABCDEFGHIJKLMNOPQRSTUVW$$$$$$XYZ[\]^_`abcdefghijklmnop
q
\\.\%C:
conhost
CreateProcessInternalW
ConvertStringSecurityDescriptorToSecurityDescriptorWContent-Type: application/x-www-form-urlencodedrn
Content-Type: multipart/form-data; boundary=---------------------------%srn
Host: %srn%d.%d.%d.%d
%d.%d.%d.%d.%x
%temp%\debug_file.txt
[%u][%s:%s:%u][0x%x;0x%x] %sDnsFlushResolverCache
\*.*
dnsapi.dll
DnsGetCacheDataTable.dll.exedownload.windowsupdate.com
vk.com
yandex.ru
HTTP/1.1https://http://%s
IsWow64Process
kernel
kernel32.dllLdrGetProcedureAddress
Microsoft
NtAllocateVirtualMemory
CLOSED
LAST_ACKTIME_WAIT
DELETE_TCB
LISTEN
SYN_SENTSYN_RCVDESTAB
FIN_WAIT1
FIN_WAIT2
CLOSE_WAIT
CLOSING
TCPt%s:%dt%s:%dt%sn
netstatnPrototLocal addresstRemote addresstStaten
ntdll.dll
NtResumeProcess
NtSuspendProcess\\?\globalroot\systemroot\system32\drivers\null.sys
NtWriteVirtualMemoryopenRegisterApplicationRestart
RtlCreateUserThread
ResetSR
RtlComputeCrc32
rundll32SeDebugPrivilegeSystemDrive
\StringFileInfo\%04x%04x\ProductName
software\microsoft\windows nt\currentversion\winlogon
shell
Sleep
srclient.dllSeShutdownPrivilege
"%s"
%dt%sntaskmgrnPIDtProcess namennet usern
the computer is joined to a domainn..
\VarFileInfo\Translation
%windir%\system32\%windir%\syswow64\POST*.exe
%SystemDrive%\
*SYSTEM*%02x%s:Zone.Identifier
GetProcessUserModeExceptionPolicy
SetProcessUserModeExceptionPolicy
%ws\%wsn
WORKGROUP
HOMEsoftware\microsoft\windowsSoftware\Microsoft\Windows\CurrentVersion\Policies\ExplorerDisableCurrentUserRun
%s.dat
%OS%_%NUMBER_OF_PROCESSORS%
S:(ML;;NRNWNX;;;LW)D:(A;;GA;;;WD)
S:(ML;;NRNWNX;;;LW)D:(A;;GA;;;WD)(A;;GA;;;AC)
\\.\AVGIDSShim
FFD3\\.\NPF_NdisWanIpc:\sample\pos.exe
ANALYSERS
SANDBOX
VIRUS
MALWARE
FORTINETMALNETVMc:\analysis\sandboxstarter.exec:\analysisc:\insidetmc:\windows\system32\drivers\vmmouse.sys
c:\windows\system32\drivers\vmhgfs.sys
c:\windows\system32\drivers\vboxmouse.sys
c:\iDEFENSEc:\popupkiller.exe
c:\tools\execute.exe
c:\Perlc:\Python27api_log.dll
dir_watch.dll
pstorec.dll
dbghelp.dll
Process32NextW
1406Software\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3
.bitMiniDumpWriteDump
rnReferer: %srn
\Google\Chrome\User Data\Default\Cache
var %s = new ActiveXObject("WScript.Shell"); %s.Run("%s");
GenuineIntelAuthenticAMDCentaurHauls7z
fnbqooqdaixfueangywblgabirdgvkewdyqgfqaioluesyrpryfkjerfsouemaxnavrkguxmcmhckwprunurmhehclermtufwiyjbqhwlunbun
uumeowfjmerxppxrgaxukyx
PowerManager_M5VKII_%d
[type=ftp]n[botid=%s]n[proc=%s]n[data=%s]n
[type=pop3]n[botid=%s]n[proc=%s]n[data=%s]n
%OS%_%NUMBER_OF_PROCESSORS%
[type=post]n[botid=%s]n[url=%s]n[ua=%s]n[proc=%s]n[ref=%s]n[keys=%s]n[data=%s]n
name=%s&amp;ok=%s&amp;id=%d&amp;res_code=%d&amp;res_text=%s_%x
name=%s&amp;ok=%s&amp;id=%d&amp;res_code=%d&amp;res_text=%s
botid=%s&amp;ver=%s.%u&amp;up=%u&amp;os=%u&amp;ltime=%s%d&amp;token=%d&amp;cn=%s&amp;av=%s&amp;dmn=%s&amp;mitm=%u
java.exe|javaw.exe|plugin-container.exe|acrobat.exe|acrod32.exe
tellerplus|bancline|fidelity|micrsolv|bankman|vanity|episys|jack 
henry|cruisenet|gplusmain|silverlake|v48d0250s1Root|TrustedPeople|SMS|Remote Desktop|REQUEST
TREASURE|BUH|BANK|ACCOUNT|CASH|FINAN|MONEY|MANAGE|OPER|DIRECT|ROSPIL|CAPO|BOSS|TRADEactive_bc
-----------------------------%srnContent-Disposition: form-data; name="pcname"rnrn%s!%srn-----------------------------
%srnContent-Disposition: form-data; name="file"; filename="report"rnContent-Type: text/plainrnrn%srn--------------
---------------%s--rn
%domain%deactivebc
inject
kill_os
loadactive_sk
deactive_sk
wipe_cookiesmitm_modmitm_script
mitm_geterr
get_keylog
get_sols!active_bc[(d+)] (S+) (d+)
!deactive_bc[(d+)]
!inject[(d+)] (S+)
!kill_os[(d+)]
!get_keylog[(d+)]!load[(d+)] (S+)!update[(d+)] (S+)
!wipe_cookies[(d+)]
!active_sk[(d+)] (S+) (d+)
!deactive_sk[(d+)]
!mitm_mod[(d+)] (S+) (d+) (S+)!mitm_script[(d+)] (S+)
!mitm_geterr[(d+)]
!get_sols[(d+)]
ATCASH
ATLOCAL
CERTCERTX
COLVCRAIF
CRYPT
CTERM
SCREEN
INTER
ELBALOCAL
ELBAWEB
ELBAWEB
ELBAWEB
PUTTY
VNCVIEW
MCLOCAL
MCSIGN
OPENVPN
PIPEK
PIPEK
PIPEK
PIPEK
POSTSAP
chrome.dll
mxwebkit.dlldragon_s.dlliron.dllvivaldi.dll
nspr4.dll
nss3.dllbrowser.dll
Advapi32.dllrsaenh.dll
kernel32.dllIprivLibEx.dll
cryptui.dll
crypt32.dll
ntdll.dll
ssleay32.dllurlmon.dll
user32.dll
Wininet.dll
Ws2_32.dll
PSAPI.dll
NzBrco.dll
VirtualProtect
LoadLibraryExW
ZwQuerySystemInformationWSARecv
WSASend
ZwDeviceIoControlFile
URLDownloadToCacheFileW
URLDownloadToFileW
TranslateMessageSSL_get_fd
SSL_write
PFXImportCertStore
CryptEncryptCPExportKey
CreateProcessInternalW
CreateDialogParamW
GetClipboardDatagetaddrinfo
gethostbyname
GetAddrInfoExW
GetMessageA
GetMessageW
DeleteFileA
GetModuleBaseNameW
bad port value
can't find plug-in path
can't get bot path
can't download file
can't encrypt file
can't save inject config to filecan't get temp file
file is not valid PEcan't delete original file
can't replace original file
can't close handle
can't protect file
original file not found
can't execute file
can't create directory
can't unzip file #1
can't unzip file #2
mitm_mod is inactivehttpd.exe is anactive
microsoft.com
dropbox.com
KEYGRAB
PasswordTELEMACOScelta e Login dispositivo
TLQ Web
db Corporate Banking WebSecureStoreCSP - enter PIN
google.com
Software\SimonTatham\PuTTYreg.txt
Software\Microsoft\Internet Explorer\MainTabProcGrowth
Temp\Low
 crc32[%x]
ACCT 
AUTHINFO PASS 
AUTHINFO USER 
Authorization
:BA:[bks]
%X!%X!%08X
btc_path.txtbtc_wallet.dat
bitcoin\wallet.dat
%s%s\%u_cert.pfx
cmdline.txt
1.3.6.1.5.5.7.3.3
CodeSignn
Software\Microsoft\Windows NT\CurrentVersion
[del]
Default
.exeELBA5\ELBA_dataftp://anonymous:ftp://%s:%s@%s:%dn
HBPData\hbp.profileHH:mm:ssdd:MMM:yyyy
I_CryptUIProtect\exe\
infected.exx%s%s\%u_info.txt
[ins]
InstallDate
%02u.jpg%s\%02d.jpgKEYLOG
%s\keylog.txt
[TOKEN ON]
nn[%s (%s-%s) - %s (%s)]n[pst]%s[/pst]
ltcd_path.txt
ltcd_wallet.dat
litecoind\wallet.dat
ltc_path.txtltc_wallet.dat
litecoin\wallet.dat\MacromediaMultiCash@Sign
C:\Omikron\MCSign
[ML][MR]Global\`{`4C470E-%08x-%08x-%08x`}`
Global\`{`DAN6J0-%s`}`
noneopera.exe
PASS 
password.txt\\.\pipe\%s
pop3://%s:%s@%s:%dn%PROCESSOR_ARCHITECTURE%Referer
[ret]
%08x\system32\rstrui.exe
\scrs\send%s%s%s%d%s:%s
sysinfo.txt
[tab]
data.txt&lt;unnamed&gt;
&lt;untitled&gt;
update
USER 
User-agent
vkeys
%xrn
rn%x%x%x.tmp
\*.txt
%02x%2b
torrent
-config config.vnc
--config 
config.ovpn
data.txt[type=post]n
CreateFileW
pos.exe
bank.exePOS
secure.
.mozgoogle.com
CertVerifyCertificateChainPolicyCertGetCertificateChain
SSL_AuthCertificateHook
USERNAMESoftware\ESET\ESET Security\CurrentVersion\Info
C8FFAD27AE1BBE28BE24DDF20AF36EF901C609968930ED82CEFBC64808BA34102C4FABA0560523FB4CCBF33684F77C8401DFB
3A7D2D598E872DD78033E7F900B78A0C710CDF0941662FF7745A435D4BC18D5661E0582B21B2DB8FCA1C0CA3401D0FC9F051
85A558AB6A76A010F606CD77B35A480B6B7176F0903299B91F1BBD141B4D33615849C35557357DAB819BC3D4A8722BB433DE
B66C7A326BE859BD94930331B37DEE6EF4C475EA4B33DE4699FFDBCD34E196E19FE630E631D2C612705048620183BCF56709B
484A4380C4B00D8D94D131C31DB53AE6BCDCCC14131BAC99A68C59A604D0AE9116E9196F7FA3EA5F86F67E9B175CC09D3E17
997728B7D
10001
get=1
COMPNAMEAppDataDir
updfiles\upd.ver
updfiles\lastupd.ver
SYSTEM\CurrentControlSet\services\Avg\SystemValues
Local AppData
Avg2015
Avg2014
Avg2013
Avg2012
Avg2011
update
Software\Microsoft\Windows\CurrentVersion\explorer\Browser Helper Objects\`{`8CA7E745-EF75-4E7B-BB86-
8065C0CE29CA`}`
Software\Microsoft\Windows\CurrentVersion\explorer\Browser Helper Objects\`{`BB62FFF4-41CB-4AFC-BB8C-
2A4D4B42BBDC`}`
Software\Microsoft\Internet Explorer\MainEnable Browser Extensions
httpd.exe
%s\httpd.exe
connect
data\index.php
logs\error.log
error.log
&lt;?n';n$bot_id = '
$bot_net = '$key_log_file = '
$process_file = '
127.0.0.1
Listen %s:%un
conf\httpd.confSSL_PORT%u&gt;n
[type=post]n
[type=screen]n
[type=knock]n
74??834E0440B832FFFFFF
74??834E04405F5EB832FFFFFF
DEBUG
memory.dmp
config.xml
php5ts.dll
zend_stream_fixup
zend_compile_file
index.php
config.php
content.php
iexplore.exe|firefox.exe|chrome.exe|opera.exe|browser.exe|dragon.exe|epic.exe|sbrender.exe|vivaldi.exe|maxthon.exe|ybr
owser.exe|microsoftedgecp.exe
InternetQueryDataAvailable
InternetReadFileInternetReadFileExA
InternetReadFileExW
InternetSetStatusCallbackA
InternetSetStatusCallbackW
HttpSendRequestAHttpSendRequestExA
HttpSendRequestExW
HttpSendRequestWrn0rnrn
.rdata
rnrnHTTP/1.
Transfer-Encoding
chunked
Content-Length
close
Proxy-ConnectionHostAccept-Encoding
x-xss-protectionx-content-security-policy
x-frame-options
x-content-type-options
If-Modified-Since
If-None-Match
content-security-policy
x-webkit-cspConnection
http://
https://NSS layer
Content-TypeBasic 
PR_ClosePR_Connect
PR_GetNameForIdentity
PR_Read
PR_SetError
PR_WriteReferer: 
Accept-Encoding:rn1406SOFTWAREMicrosoftWindowsCurrentVersionInternet SettingsZones3
data_afterndata_beforen
data_enddata_injectn
set_url %BOTID%
%BOTNET%InternetCloseHandle
HTMLc:\inject.txt
Dalvik/1.6.0 (Linux; U; Android 4.1.2; GT-N7000 Build/JZO54K)
xxx_process_0x%08x
Common.js
```

**API混淆**

Main payload用Push-Calc-Ret混淆的技术混淆API。在main payload注入到svchost进程中后真实API函数的调用被修改。当一个函数被调用时，用一个计算真实函数地址的跳板函数代替。所有的跳板函数被存储在数组中。

例如，main payload想要调用CreateFile()，但是调用已经被修改了。现在将调用跳板函数如下：



```
00846110   PUSH 2B464C25
00846115   PUSHFD
00846116   XOR DWORD PTR SS:[ESP+4], 5DB5E13F
0084611E   POPFD
0084611F   RETN
```

首先，一个值被压栈。然后把标志寄存器都压栈，因为XOR指令会影响很多标志寄存器。然后之前压栈的值与另一个值异或得到真实的API地址。最后恢复标致寄存器，用RETN执行真实的函数地址。

**持续性的方法**

Main payload拷贝原始混淆的loader文件到%ProgramData%文件夹中，文件名用GetTickCount()函数获得。然后，它在当前用户的启动目录创建一个“Common.js”的JScript文件。文件包含以下代码，能在系统重启后自动运行原始loader：



```
var yqvltidpue = new ActiveXObject("WScript.Shell");
yqvltidpue.Run("C:\PROGRA~3\930d4a6d.exe")
```

**main payload与前一个版本的变化**

之前版本的Shifu被FireEye和Fortinet报告过。

在和之前版本的比较中，用计算机名、用户名、安装日期和系统磁盘序列号创建的字符串变多了：



```
TREASURE
BUH
BANK
ACCOUNT
CASH
FINAN
MONEY
MANAGE
OPER
DIRECT
ROSPIL
CAPO
BOSS
TRADE
```

更新的命令：



```
active_sk
deactive_sk
deactivebc
get_keylog
get_sols
inject
kill_os
load
mitm_geterr
mitm_mod
mitm_script
wipe_cookies
```

目标浏览器更新：



```
iexplore.exe
firefox.exe
chrome.exe
opera.exe
browser.exe
dragon.exe
epic.exe
sbrender.exe
vivaldi.exe
maxthon.exe
ybrowser.exe
microsoftedgecp.exe
```

main payload将从C&amp;C服务器下载Apache的httpd.exe服务器，存储在磁盘上用来web注入。比较之前的版本，main payload也包含了暗示Zend PHP框架功能的字符串：



```
zend_stream_fixup
zend_compile_file
```

**在svchost中挂钩函数**

和之前版本一样，恶意程序挂钩一些API函数来重定向URL，捕捉网络流量和键盘记录。它用5字节inline hook方法挂钩 API。被挂钩的API如下：



```
NtDeviceIoControlFile (ntdll.dll)
ZwDeviceIoControlFile (ntdll.dll)
GetClipboardData (user32.dll)
GetMessageA (user32.dll)
GetMessageW (user32.dll)
TranslateMessage (user32.dll)
GetAddrInfoExW (ws2_32.dll)
gethostbyname (ws2_32.dll)
getaddrinfo (ws2_32.dll)
```

**网络功能**

Main payload用顶级域名.bit，它是一个基于Namecoin架构的分散的DNS系统。恶意程序请求的IP地址如下：



```
92.222.80.28
78.138.97.93
77.66.108.93
```

C&amp;C服务器域名名字，user-agent字符串和URL参数被修改版RC4算法加密。解密字符串如下：



```
klyatiemoskali.bit
slavaukraine.bit
Mozilla/5.0 (Windows; U; Windows NT 5.2 x64; en-US; rv:1.9a1) Gecko/20061007 Minefield/3.0a1
L9mS3THljZylEx46ymJ2eqIdsEguKC15KnyQdfx4RTcVu8gCT
https://www.bing.com
/english/imageupload.php
/english/userlogin.php
/english/userpanel.php
1brz
```

加密的字符串用下面的格式存储在.data节中：

```
&lt;LengthOfString&gt;&lt;EncryptedString&gt;
```

“klyatiemoskali“简单翻译的意思是希望坏事降临莫斯科。第二个字符串“slavaukraine”意思是保佑乌克兰。RC4的密码“L9mS3THljZylEx46ymJ2eqIdsEguKC15KnyQdfx4RTcVu8gCT”被用于加密网络流量。

在分析时，只有下面的DNS服务器还有响应：

```
77.66.108.93 (ns1.dk.dns.d0wn.biz)
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b9dbdc77066ae871.png)

图5. 77.66.108.93 Namecoin DNS服务器信息

下图是分析Shifu的网络流量的截图：

[![](https://p0.ssl.qhimg.com/t010629f70e7be7fa3a.png)](https://p0.ssl.qhimg.com/t010629f70e7be7fa3a.png)

图6. Wireshark捕获流量的截图

我们能看见访问klyatiemoskali.bit能获得IP地址。在C&amp;C服务器响应后，使用TLS握手协议开启一个加密通道。最后，它发送加密数据并获得加密结果。然而，没有更多的网络流量被捕获到了。klyatiemoskali.bit and slavaukraine.bit都被解析到103.199.16.106的IP地址。

因为.bit顶级域名依赖的Namecoin系统是基于比特币系统的，每个业务都能被跟踪。因此，我们用一个Namecoin浏览器查看.bit域名和所属的IP地址。例如，如果我们用网络服务namecha.in，我们得到关于klyatiemaskali.bit的信息：

[![](https://p2.ssl.qhimg.com/t0134eeafac1cbc82fa.png)](https://p2.ssl.qhimg.com/t0134eeafac1cbc82fa.png)

我们同样能看到关于slavaukraine.bit的信息：

[![](https://p1.ssl.qhimg.com/t01c5a593b7414fda79.png)](https://p1.ssl.qhimg.com/t01c5a593b7414fda79.png)

所有的域名都是在2016-06-03注册的，只有一个IP地址与他们对应。这个IP地址符合我们捕捉到的网络流量。而且我们能看见这个域名似乎还存活着。

**与C&amp;C服务器的查询字符串**

Main payload包含了一个查询字符串的模版，用来向C&amp;C服务器发送受害者的信息：

```
botid=%s&amp;ver=%s.%u&amp;up=%u&amp;os=%u&amp;ltime=%s%d&amp;token=%d&amp;cn=%s&amp;av=%s&amp;dmn=%s&amp;mitm=%u
```

我们能够看到一些动态获取的信息（bot标识，更新时间，操作系统版本，本地时间戳，令牌，反病毒软件，工作站域名，中间人拦截检测），同时也能看到一些像bot版本和campaign名的静态值，例子如下：

```
botid=26C47136!A5A4B18A!F2F924F2&amp;ver=1.759&amp;up=18294&amp;os=6110&amp;ltime=-8&amp;token=0&amp;cn=1brz&amp;av=&amp;dmn=&amp;mitm=0
```

我们能看到Shifu的内部版本是“1.759”和campaign名为“1brz”。

如果我们将Shifu的查询字符串和2014年2月发现的最新版本的Shiz（内部版本是5.6.25）的比较，我们能看见相似之处：

```
botid=%s&amp;ver=5.6.25&amp;up=%u&amp;os=%03u&amp;ltime=%s%d&amp;token=%d&amp;cn=sochi&amp;av=%s
```

**修改的RC4加密算法**

Shifu使用了一个修改过的RC4加密算法。我们用Python重构了算法并以“klyatiemoskali.bit”域名的加密展示为例：



```
import os
import binascii
###initial values##########
string = "klyatiemoskali.bit"
seed = 
"fnbqooqdaixfueangywblgabirdgvkewdyqgfqaioluesyrpryfkjerfsouemaxnavrkguxmcmhckwprunurmhehclermtufwi
yjbqhwlunbunuumeowfjmerxppxrgaxukyx"
buffer = [0] * (len(string))
table_encr = [0] * 0x102
table_encr[0x100] = 1
table_encr[0x101] = 0
###########################
###string2buffer###########
i = 0
while (i&lt;len(string)):
    char_1 = string[i]
    int_1 = ord (char_1)
    buffer[i] = int_1
    i += 1
###string2buffer###########
###encryption table########
i = 0
while (i &lt; 0x100):
    table_encr[i] = 0x000000ff&amp;i
    i += 1
i = 0
j = 0
while (i &lt; 0x100):
    char_1 = seed[j]
    int_2 = ord (char_1)
    table_encr[i] ^= int_2
    i += 1
    j += 1
    if (j == len(seed)):
        j = 0
###########################
###encryption##############
size_1 = len(string)
i = 0
while (size_1 != 0):
    byte_buf = buffer[i]
    ind_1 = table_encr[0x100]
    ind_2 = table_encr[ind_1]
    ind_3 = 0x000000ff&amp;(ind_2 + table_encr[0x101])
    ind_4 = 0x000000ff&amp;(table_encr[ind_3])
    table_encr[ind_1] = ind_4
    table_encr[ind_3] = ind_2
    buffer[i] = 0x000000ff&amp;(table_encr[0x000000ff&amp;(ind_2 + ind_4)] ^ byte_buf)
    table_encr[0x100] = 0x000000ff&amp;(ind_1 + 1)
    table_encr[0x101] = ind_3
    i += 1
    size_1 -= 1
i = 0
str_1 = ""
while (i &lt; len(string)):
    str_1 = str_1 + chr(buffer[i])
    i += 1
###########################
###output##################
print ("Cleartext string: %s" % string)
print ("Encrypted: 0x%s" % binascii.hexlify(str_1)) 
###########################
```
