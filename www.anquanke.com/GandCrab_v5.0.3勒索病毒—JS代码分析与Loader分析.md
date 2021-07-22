> 原文链接: https://www.anquanke.com//post/id/163626 


# GandCrab_v5.0.3勒索病毒—JS代码分析与Loader分析


                                阅读量   
                                **185514**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01aa1595fe75a292d7.png)](https://p4.ssl.qhimg.com/t01aa1595fe75a292d7.png)



## 概述

Gandcrab家族算是勒索病毒中最“出名”的了，它仅仅在半年的时间了就发布了从v1.0到v5.0.3，截止到我分析前，已经出现了v5.0.5版本了，我这个分析的是v5.0.3的JS脚本产生的勒索病毒。勒索病毒的最终执行的Payload部分我就不分析了，因为和之前的版本上没有太大的改变，但是这个Loader很有意思，用到了在2017年BlackHat大会上提到的ProcessDopplegänging技术，有兴趣的可以看看。

该JS脚本的功能：

(1)对抗Avast杀软

(2)对抗Windows Defender

(3)对抗MSC微软安全客户端

(4)对抗Ahnlab安博士杀软

(5)生成GandCrabV5.0.3勒索病毒变种样本并执行



## 详细分析

下图是经JS格式转换后的混淆脚本，需要通过Chrome浏览器动态调试得到源码，在hrodjgengsl函数处下断，查看参数信息即是解混淆后的JS源码了

[![](https://p1.ssl.qhimg.com/dm/1024_219_/t0111b3fbd2a96d3aa6.png)](https://p1.ssl.qhimg.com/dm/1024_219_/t0111b3fbd2a96d3aa6.png)

经JS格式化后的JS源码部分（两张图）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01184649f5a7ab6292.png)

[![](https://p1.ssl.qhimg.com/t01a33ec5b09b1cd5c4.png)](https://p1.ssl.qhimg.com/t01a33ec5b09b1cd5c4.png)

### 1、检查avast杀毒服务是否运行，如处于运行状态，生成kyoxks.js脚本并运行，脚本内容如下：

[![](https://p0.ssl.qhimg.com/dm/1024_504_/t012ffe2c96ac50ddfa.png)](https://p0.ssl.qhimg.com/dm/1024_504_/t012ffe2c96ac50ddfa.png)

脚本功能：

1、首先在注册表HKEY_CURRENT_USERSOFTWAREycsdrrpvrylqzhlnv下写一段base64加密的powershell脚本

2、通过创建计划任务以固定间隔时间调PowerShell运行它。

解密之后的powershell代码如下，这其中有一段C#代码：

[![](https://p3.ssl.qhimg.com/t0129e5a3038e21e0e1.png)](https://p3.ssl.qhimg.com/t0129e5a3038e21e0e1.png)

C#代码—————————————————————————————————————————————————————————————————————————————————————

[![](https://p3.ssl.qhimg.com/dm/1024_903_/t0186594131c4c5aa69.png)](https://p3.ssl.qhimg.com/dm/1024_903_/t0186594131c4c5aa69.png)

[![](https://p1.ssl.qhimg.com/t011539c7037b589212.png)](https://p1.ssl.qhimg.com/t011539c7037b589212.png)

————————————————————————————————————————————————————————————————————————————————————–

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014b168f8ccf86817e.png)

第一段Powershell脚本主要功能：

1、首先拷贝对应的文件到临时目录

2、找到对应路径下Avast更新程序并且动

3、清除对应路径下缓存数据

第二段C#代码主要功能：

C#代码中定义了类：a12，其中在a12这个类中定义了a10、a11、a13、a14四个方法

第三段Powershell脚本主要功能：

执行调用C#代码中方法

a10方法主要是找到Avast进程得到有效句柄后从死循环中break退出。

a11和a13方法主要是向Avast程序发送消息，按下Tab键、空格键，释放Tab键、空格键。

a14方法主要是将Avast窗口程序隐藏

### 2、检查WdNisSvc、WinDefend服务是否运行，如处于运行状态，生成nykvwcajm.js脚本并运行，脚本内容如下：

[![](https://p0.ssl.qhimg.com/dm/1024_570_/t010af5343856118ffe.png)](https://p0.ssl.qhimg.com/dm/1024_570_/t010af5343856118ffe.png)

主要功能：

1、利用打开fodhelper.exe进程使cmd.exe Bypass UAC的目的，进而关闭Windows Defender杀毒功能及强制结束Windows Defender服务程序MSASCui.exe。

判断是否是Win 10系统，如是通过将cmd.exe /C “powershell Set-MpPreference -DisableRealtimeMonitoring $true &amp;&amp; taskkill /im MSASCui* /f /t命令写入到HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\注册表中，并以隐藏窗口的形式打开fodhelper.exe，这时就会执行上述注册表中写入的命令。同时最小化桌面上的所有窗口。再删除相应的注册表HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\。

2、利用打开eventvwr.exe进程使cmd.exe Bypass UAC的目的，进而关闭Windows Defender杀毒功能及强制结束Windows Defender服务程序MSASCui.exe。

判断是否是Win 7系统，如是通过将cmd.exe /C “sc stop WinDefend &amp;&amp; taskkill /im MSASCui* /f /t命令写入到HKEY_CURRENT_USER\Software\Classes\mscfile\shell\open\command\注册表中，并以隐藏窗口的形式打开eventvwr.exe。这时就会执行上述注册表中写入的命令。执行完后再删除注册表HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\。

3、如果WdNisSvc或WinDefend服务存在，则持续检测20s。

## 3、检查NisSrv服务是否运行，如处于运行状态，生成bervcptyvulur.js脚本并运行，脚本内容如下：

[![](https://p5.ssl.qhimg.com/dm/1024_924_/t014234c9072d2ae01e.png)](https://p5.ssl.qhimg.com/dm/1024_924_/t014234c9072d2ae01e.png)

NIsSrv指的是微软网络实时检测服务，是微软在系统开机时启动的一个用来检测网络的反病毒服务。卸载Microsoft Security Client程序命令：MsiExec.exe /X`{`2AA3C13E-0531-41B8-AE48-AE28C940A809`}`

1、利用打开fodhelper.exe进程使MsiExec.exe Bypass UAC的目的，进而以最小化的方式静默卸载Microsoft Security Client程序。

判断是否是Win 10系统，如是通过将MsiExec.exe /X `{`2AA3C13E-0531-41B8-AE48-AE28C940A809`}` ACCEPT=YES /qr+ /quiet命令写入到HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\注册表中。并以隐藏窗口的形式传入C:Windowsfodhelper.exe参数打开explorer.exe。这时就会执行上述注册表中写入的命令。再删除注册表项HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\。

2、利用打开eventvwr.exe进程使MsiExec.exe Bypass UAC的目的，进而以最小化的方式静默卸载Microsoft Security Client程序。

判断是否是Win 7系统，如是通过将MsiExec.exe /X `{`2AA3C13E-0531-41B8-AE48-AE28C940A809`}` ACCEPT=YES /qr+ /quiet命令写入到HKEY_CURRENT_USER\Software\Classes\mscfile\shell\open\command\注册表中，并以隐藏窗口的形式传入C:Windowseventvwr.exe打开explorer.exe。这时就会执行上述注册表中写入的命令。再删除相应的注册表项HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\。

3、如果NisSrv服务存在，则持续检测90s。

### 4、检查V3 Service服务是否运行，如处于运行状态，再检查tgydmilslvp.txt文件是否存在%USERPROFILE%目录下，如存在就生成recjyzcz.js脚本并运行，不存在该txt文件就生成内容是777的tgydmilslvp.txt，脚本内容如下：

[![](https://p0.ssl.qhimg.com/dm/1024_737_/t015c28719af791afef.png)](https://p0.ssl.qhimg.com/dm/1024_737_/t015c28719af791afef.png)

主要功能：

1、利用打开fodhelper.exe进程使Powershell.exe Bypass UAC的目的，进而执行写在注册表中的Powershell脚本。

判断是否是Win 10系统，如是通过将djziapwzi变量所赋的值（Powershell脚本）写入到HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\注册表中，并以隐藏窗口的形式传入C:Windowsfodhelper.exe参数打开explorer.exe。这时就会执行上述注册表中写入的命令。再删除相应的注册表项HKEY_CURRENT_USER\Software\Classes\ms-settings\shell\open\command\。

2、利用打开eventvwr.exe进程使Powershell.exe Bypass UAC的目的，进而关闭Windows Defender杀毒功能及强制结束Windows Defender服务程序MSASCui.exe。

判断是否是Win 7系统，如是通过将djziapwzi变量所赋的值（Powershell脚本）写入到HKEY_CURRENT_USER\Software\Classes\mscfile\shell\open\command\注册表中，并以隐藏窗口的形式传入C:Windowseventvwr.exe打开explorer.exe。这时就会执行上述注册表中写入的命令。再删除相应的注册表项HKEY_CURRENT_USER\Software\Classes\mscfile\shell\open\command\。

3、如果WdNisSvc或WinDefend服务存在，则持续检测60s。

解密后Powershell脚本：

[![](https://p1.ssl.qhimg.com/t017a45ce5d265ba8da.png)](https://p1.ssl.qhimg.com/t017a45ce5d265ba8da.png)

主要功能：

查找Ahnlab安博士杀软的卸载程序，拷贝到指定位置后并执行。

### 5、解密Payload并写入到dsoyaltj.exe文件中后执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01eaccc94b5bb66d53.png)

以上是比较详细的脚本分析内容。

### 6、ProcessDoppelgänging技术与Process Hollowing技术交叉使用的恶意Loader

Loader流程图如下：

[![](https://p0.ssl.qhimg.com/t015ef607d521967784.png)](https://p0.ssl.qhimg.com/t015ef607d521967784.png)

首先简单说一下ProcessDoppelgänging攻击技术，这个技术是2017年欧洲BlackHat大会上由网络安全公司enSilo两名研究人员提出的新型在野攻击，其中还用到了NTFS文件系统事务回滚机制，相关的BlackHatPDF文档在最后会添加到附件。

ProcessDoppelgänging攻击技术：

1、创建一个新事务并这个事务中直接创建一个新文件

2、将新创建的文件映射到进程新创建的section中

3、利用NTFS文件系统事务回滚机制，回滚到之前的无创建文件状态

4、再跳转执行内存中的section部分的payload

上述介绍的是常规ProcessDoppelgänging攻击技术，本Loader结合使用了Process Hollowing技术，配合使用后较为复杂。以下是详细分析：

[![](https://p4.ssl.qhimg.com/t0149d0edf56fd7edea.png)](https://p4.ssl.qhimg.com/t0149d0edf56fd7edea.png)

以上程序经动态调试之后首先发现该程序通过申请空间并解密出PE文件，然后随机创建挂起原始文件状态的合法进程（本文是wermgr.exe，还有可能是svchost.exe），这种操作让我们想起了Process Hollowing技术常用的创建傀儡进程的手法。我们了解下两种技术不同点，就能知道该样本作者如何将两种技术交叉使用的。

与Process Hollowing技术不同点：

1、在ProcessDopplegänging技术中，创建进程的操作需要很长时间，并使用官方未公开的API：NtCreateProcessEx。

2、在ProcessDoppelgänging技术中，新进程不是从原始文件创建的，而是从特殊缓冲区（section）创建的。

如下图所示：

[![](https://p0.ssl.qhimg.com/t01555ac8d4bbdda60d.png)](https://p0.ssl.qhimg.com/t01555ac8d4bbdda60d.png)

[![](https://p2.ssl.qhimg.com/t01cc953a6a80b1e5fd.png)](https://p2.ssl.qhimg.com/t01cc953a6a80b1e5fd.png)

因为NTDLL是一个特殊的低级DLL。基本上，它只是系统调用的一个包装器。它与系统中的其他DLL没有任何依赖关系。由于这个原因，它可以方便地加载，而无需填充其导入表。其他系统DLL（如Kernel32）在很大程度上依赖于从NTDLL导出的函数。所以许多用户层监视工具Hook并拦截NTDLL导出的函数。恶意程序作者知道这一点，所以有时为了躲过这种机制，他们会选择加载一个新的NTDLL副本。查看内存映射表，我们看到附加的ntdll_1作为映像加载，和其他DLL一样，这种类型的映射是使用NTDLL的。但是NTDLL默认加载到每个可执行文件中，并且官方的API无法加载相同的DLL两次。在这里它们使用一种比较好的解决方式：调用以下函数将文件以一个section的方式加载

1、ntdll.NtCreateFile – 打开ntdll.dll文件

2、ntdll.NtCreateSection – 在ntdll文件中创建一个section

3、ntdll.ZwMapViewOfSection – 将section映射到进程地址空间，ntdll模块文件就能映射进内存了。

[![](https://p5.ssl.qhimg.com/t01983f63aaabe2583b.png)](https://p5.ssl.qhimg.com/t01983f63aaabe2583b.png)

这种方式非常聪明，因为DLL映射类型为Image，所以它看起来像是以普通的方式加载，这样的操作可以绕过各种安全产品的检测与拦截。又以同样的方式映射了wermgr.exe文件。

[![](https://p0.ssl.qhimg.com/t01e7308e628971ae1c.png)](https://p0.ssl.qhimg.com/t01e7308e628971ae1c.png)

### 7、使用NTFS事务创建新文件

简要介绍一下NTFS事务是什么，这种机制通常在数据库上运行时使用，它们存在于NTFS文件系统中。NTFS事务将一系列操作封装到一个单元中。在事务内部创建文件时，在提交事务之前，外部任何人都无法访问它。ProcessDoppelgänging使用它们来创建不可见的Payload文件，加载程序创建一个新事务，在该事务中创建一个新文件。首先，调用NTDLL中的函数ZwCreateTransaction。再调用RtlSetCurrentTransaction和ZwCreateFile（所创建的文件是％TEMP％\ Liebert.bmp）。然后调用ZwWriteFile将缓冲区内容写入文件。我们可以看到正在写入的缓冲区中包含新的PE文件：第二阶段Payload。通常，对于此技术，文件仅在事务中可见，并且不能由其他进程（如AV扫描程序）打开。

[![](https://p5.ssl.qhimg.com/t019030553d16706e09.png)](https://p5.ssl.qhimg.com/t019030553d16706e09.png)

然后使用此事务处理文件创建一个section。只能通过调用API：ZwCreateSection / NtCreateSection来实现此操作的功能。创建该部分后，不再需要该文件。事务将调用ZwRollbackTransaction回滚到之前的状态，并且对文件的更改永远不会保存在磁盘上。通过使用NTDLL副本调用的低级别函数，使这些操作更加隐蔽，不易被杀软发现。

[![](https://p1.ssl.qhimg.com/t01968df8c6fd24e77b.png)](https://p1.ssl.qhimg.com/t01968df8c6fd24e77b.png)

### 8、从section到Process

如果这是典型的ProcessDoppelgänging技术，那么将带有映射Payload的section直接创建进程的这种情况永远不会发生。继续单步执行后可以看到在回滚事务之后调用以下函数：

```
ntdll_1.ZwQuerySection
ntdll.NtClose
ntdll.NtClose
ntdll_1.ZwMapViewOfSection
ntdll_1.ZwProtectVirtualMemory
ntdll_1.ZwWriteVirtualMemory
ntdll_1.ZwProtectVirtualMemory
ntdll_1.ZwWriteVirtualMemory
ntdll_1.ZwResumeThread
```

1、将新创建的section（PE文件）作为附加模块映射到新进程中。

[![](https://p0.ssl.qhimg.com/t0127a91dedaf493528.png)](https://p0.ssl.qhimg.com/t0127a91dedaf493528.png)

2、修改内存属性后调用ZwWriteVirtualMemory 重定向远程进程OEP处代码，跳转重定向到注入模块的入口点。

[![](https://p4.ssl.qhimg.com/t0162f76cd618234096.png)](https://p4.ssl.qhimg.com/t0162f76cd618234096.png)

修改前：

[![](https://p4.ssl.qhimg.com/t013ebbaecdcc3ba706.png)](https://p4.ssl.qhimg.com/t013ebbaecdcc3ba706.png)

[![](https://p2.ssl.qhimg.com/t01008aaa8a906ac7ca.png)](https://p2.ssl.qhimg.com/t01008aaa8a906ac7ca.png)

修改后：

[![](https://p3.ssl.qhimg.com/t01859d44eef71f254c.png)](https://p3.ssl.qhimg.com/t01859d44eef71f254c.png)

3、再修改内存属性，调用ZwWriteVirtualMemory 重定向远程进程的PEB+8处代码（ImageBaseAddress），改为之前映射的section位置处：400000（PE文件）。

[![](https://p3.ssl.qhimg.com/t01968a0fc701306b1e.png)](https://p3.ssl.qhimg.com/t01968a0fc701306b1e.png)

4、调用ResumeThread恢复远程进程，执行后运行的就是400000地址处PE文件OEP的代码：

[![](https://p2.ssl.qhimg.com/t01cae5f2ba619b1597.png)](https://p2.ssl.qhimg.com/t01cae5f2ba619b1597.png)

如果使用以上方法修补入口点失败，则用第二个方法，在线程上下文中设置新地址（ZwGetThreadContext – &gt; ZwSetThreadContext），这是Process Hollowing中使用的经典技术。

[![](https://p1.ssl.qhimg.com/t0151be5efaf090dc74.png)](https://p1.ssl.qhimg.com/t0151be5efaf090dc74.png)

至此Loader部分就分析完成了。



## 总结

因为使用ProcessDoppelgänging技术的样本还是很少见的，而且这次GandCrab样本使用到了这项技术，自己之前也没研究过ProcessDoppelgänging技术，为了弄得更明白一些就多花了些时间，所以我就写的稍微详细一些，图文并茂，希望各位大佬勿喷。

### 参考文章链接

[https://xz.aliyun.com/t/2885](https://xz.aliyun.com/t/2885)（JS样本源）

[https://blog.malwarebytes.com/threat-analysis/2018/08/process-doppelganging-meets-process-hollowing_osiris/](https://blog.malwarebytes.com/threat-analysis/2018/08/process-doppelganging-meets-process-hollowing_osiris/)（ProcessDoppelgänging技术相关）

[https://yunpan.360.cn/surl_ymnNmItfhUZ](https://yunpan.360.cn/surl_ymnNmItfhUZ) BH PPT链接
