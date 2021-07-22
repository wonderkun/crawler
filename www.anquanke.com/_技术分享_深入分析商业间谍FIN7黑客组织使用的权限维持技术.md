> 原文链接: https://www.anquanke.com//post/id/86024 


# 【技术分享】深入分析商业间谍FIN7黑客组织使用的权限维持技术


                                阅读量   
                                **96534**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2017/05/fin7-shim-databases-persistence.html](https://www.fireeye.com/blog/threat-research/2017/05/fin7-shim-databases-persistence.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01b2bfe43e88fceb28.jpg)](https://p2.ssl.qhimg.com/t01b2bfe43e88fceb28.jpg)

****

翻译：[**童话**](http://bobao.360.cn/member/contribute?uid=2782911444)

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

**今年年初，Mandiant（美国麦迪安网络安全公司）发现了多起网络攻击事件，我们认为这些攻击事件为FIN7黑客组织所为，这是一个经济利益驱使的黑客组织**，该组织的恶意攻击行为最早可追溯到2015年。在各种不同的环境中，FIN7利用CARBANAK后门，该组织在以前的攻击场景中经常使用该后门。

**该黑客组织发起的攻击事件的独特之处在于如何安装CARBANAK后门进行权限维持。**Mandiant（美国麦迪安网络安全公司）分析发现**该组织利用shim数据库在不同的系统环境下实现权限维持。**shim将恶意的内存补丁注入到服务控制管理器（“services.exe”）进程中，然后产生一个CARBANAK后门进程。

Mandiant（美国麦迪安网络安全公司）分析指出，FIN7还使用这种技术来安装payment card采集工具用于权限维持。这是FIN7黑客组织以前的方法，为了注入恶意进程维持权限会先安装一个恶意的Windows服务。

<br>

**Shim功能概要（解决古老的程序兼容问题）**

引用Microsoft的官方说明，[程序兼容Shim](https://technet.microsoft.com/en-us/library/dd837644(v=ws.10).aspx)（application compatibility shim）是一个可以通过hook透明拦截API的小型函数库，可以[篡改传输函数的参数值](https://blogs.technet.microsoft.com/askperf/2011/06/17/demystifying-shims-or-using-the-app-compat-toolkit-to-make-your-old-stuff-work-with-your-new-stuff/)，可以处理一些自己的操作，也可以执行其他的操作（例如存储在当前系统中的其他位置的代码）。

**现如今，Shim的存在主要解决的问题是处理一些古老应用程序的兼容性问题（译者注：部分古老的应用程序采用一些过时或已被弃用的API，都过Shim可以hook这些API替换为较流行的函数，进而解决程序的兼容性问题）。**可以看到，Shim是一个合法的功能，出于一个善意的目的，去解决系统迭代产生的问题，由于技术的两面性，其功能有可能被滥用执行一些恶意的操作。Mandiant（美国麦迪安网络安全公司）的安全顾问曾经在[BruCon](http://files.brucon.org/2015/Tomczak_and_Ballenthin_Shims_for_the_Win.pdf)和[BlackHat](https://www.blackhat.com/docs/asia-14/materials/Erickson/Asia-14-Erickson-Persist-It-Using-And-Abusing-Microsofts-Fix-It-Patches.pdf)讨论过Shim数据库被滥用可能产生的安全问题。

<br>

**Shim数据库注册表**

在当前操作系统上注册shim数据库有多种方式，其中一种方法就是使用系统内置的“sdbinst.exe”命令行工具。图1展示的就是使用“sdbinst.exe”命令行工具注册shim时创建的两个注册表键。

[![](https://p0.ssl.qhimg.com/t01fedf8b2e262a83a1.png)](https://p0.ssl.qhimg.com/t01fedf8b2e262a83a1.png)

图1：Shim数据库注册表键

一旦shim数据库在系统上成功注册，shim数据库文件（后缀名为“.sdb”）将被复制到"C:WindowsAppPatchCustom"(32位shim)目录下（64位shim将被复制到"C:WindowsAppPatchCustomCustom64"目录下)。

<br>

**恶意Shim数据库安装**

在操作系统上安装和注册恶意shim数据库，FIN7使用自定义经过Base64编码的PowerShell脚本，该脚本的功能是运行“sdbinst.exe”命令行工具注册一个经过修改插入恶意代码的shim数据库，图2为经过还原的FIN7 PowerShell脚本中解码的部分截图，列出了执行的命令及参数。

[![](https://p3.ssl.qhimg.com/t013eecd842618e1afe.png)](https://p3.ssl.qhimg.com/t013eecd842618e1afe.png)

图2：FIN7 PowerShell脚本安装自定义Shim数据库文件的部分截图

FIN7黑客组织使用“sdbinst.exe”命令行工具在目标操作系统上创建和注册不同命名规则的shim数据库文件。但有一个共同点是，都会创建一个后缀名为“.tmp”的Shim数据库文件（如图3所示）。

[![](https://p3.ssl.qhimg.com/t01d72b7fa6afd43407.png)](https://p3.ssl.qhimg.com/t01d72b7fa6afd43407.png)

图3：恶意Shim数据库文件示例

当前的恶意shim数据库文件再操作系统上注册后，一个后缀名为“.sdb”，文件名为随机GUID值的shim数据库文件（恶意文件）将在其64位的默认目录（"C:WindowsAppPatchCustomCustom64"）下创建，如图4所示。该shim数据库文件具有与最初在“C:WindowsTemp”目录下创建的文件具有相同的MD5 hash值。

[![](https://p2.ssl.qhimg.com/t012f607ffc5790a943.png)](https://p2.ssl.qhimg.com/t012f607ffc5790a943.png)

图4：注册后的shim数据库文件

除此之外，与之相关的注册表键也将在shim数据库注册表中创建。图5展示了与此shim安装相关的注册表键值关系。

[![](https://p3.ssl.qhimg.com/t0140c63282d5a336b1.png)](https://p3.ssl.qhimg.com/t0140c63282d5a336b1.png)

图5：注册表键值关系

用于shim数据库注册表的数据库描述（DatabaseDescription）“Microsoft KB2832077”是很有意思的，因为这个KB编号不是一个Microsoft官方发布的更新补丁编号。如图6所示，该描述出现在受影响的操作系统中的Windows控制面板的已安装程序列表中。

[![](https://p2.ssl.qhimg.com/t01a985aaf7c0c986f1.png)](https://p2.ssl.qhimg.com/t01a985aaf7c0c986f1.png)

图6：作为已安装应用程序的Shim数据库

<br>

**恶意Shim数据库细节分析**

经过研究分析，Mandiant（美国麦迪安网络安全公司）分析出FIN7黑客组织向全版本操作系统（32位、64位）中的“services.exe”中注入自定义的Shim数据库（将原生Shim数据库文件植入CARBANAK后门payload）。当操作系统启动“services.exe”进程执行时，CARBANAK后门payload将会执行。shim数据库文件包含第一阶段加载的shellcode，其余的shellcode payload存储在注册表键中。图7列出了FIN7黑客组织利用的[解析](https://github.com/williballenthin/python-sdb)shim数据库文件。

[![](https://p0.ssl.qhimg.com/t01847e2d415f5334bb.png)](https://p0.ssl.qhimg.com/t01847e2d415f5334bb.png)

图7：解析shim数据库

对于第一阶段加载的程序，FIN7黑客组织改写了services.exe进程中相对虚拟地址 (RVA)“0x0001407c”对应“ScRegisterTCPEndpoint” 函数的代码，执行带有恶意shellcode的shim数据库。新的“ScRegisterTCPEndpoint”函数（shellcode）包含了对“REGISTRYMACHINESOFTWAREMicrosoftDRM”路径的引用。该路径下的内容为存贮在操作系统中其余的恶意shellcode和CARBANAK DLL（FIN7黑客组织使用的后门程序）payload。

图8展示了在恢复的shim数据库文件中解析补丁结构的部分截图

[![](https://p3.ssl.qhimg.com/t0183206b58dc51d63f.png)](https://p3.ssl.qhimg.com/t0183206b58dc51d63f.png)

图8：从shim数据库文件中解析补丁结构

存储在注册表“HKLMSOFTWAREMicrosoftDRM”中的shellcode可以利用ntdll中的API函数“RtlDecompressBuffer”进行解压缩出payload。该程序在执行CARBANAK DLL（FIN7黑客组织使用的后门程序）payload的入口函数之前会休眠4分钟。一旦payload加载进内存，就会创建一个包含CARBANAK DLL名为“svchost.exe”的新进程。

<br>

**总结一下完整的攻击过程**

图9是一个完整的行为流程图，利用shim数据库向64位的“services.exe”进程中注入shellcode最终实现权限维持。

[![](https://p5.ssl.qhimg.com/t01495f6a5b7a624645.png)](https://p5.ssl.qhimg.com/t01495f6a5b7a624645.png)

图9：Shim数据库代码注入过程

<br>

**如何检测电脑是否被该恶意代码感染？**

Mandiant（美国麦迪安网络安全公司）推荐了以下几种方式检测操作系统是否受到这种恶意Shim数据库的感染。

**1.监控默认shim数据库下新创建的shim数据库文件：“C:WindowsAppPatchCustom”（32位），“C:WindowsAppPatchCustomCustom64”（64位）**

**2.监控以下注册表键的创建或修改事件：“HKLMSOFTWAREMicrosoftWindows NTCurrentVersionAppCompatFlagsCustom”和“HKLMSOFTWAREMicrosoftWindows NTCurrentVersionAppCompatFlagsInstalledSDB”**

**3.监控进程执行事件和恶意使用“sdbinst.exe”命令行工具执行的参数的异常行为。**
