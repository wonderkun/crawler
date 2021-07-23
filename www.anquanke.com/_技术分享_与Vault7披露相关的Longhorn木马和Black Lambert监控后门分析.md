> 原文链接: https://www.anquanke.com//post/id/86295 


# 【技术分享】与Vault7披露相关的Longhorn木马和Black Lambert监控后门分析


                                阅读量   
                                **131968**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：adelmas.com
                                <br>原文地址：[http://adelmas.com/blog/longhorn.php](http://adelmas.com/blog/longhorn.php)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t018d4dfa3b7305ed15.jpg)](https://p5.ssl.qhimg.com/t018d4dfa3b7305ed15.jpg)

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**0x00 前言**

几个星期前，我偶然发现了赛门铁克的这篇文章：Longhorn: Tools used by cyberespionage group linked to Vault 7。我迫不及待的想逆向这个恶意软件，因为最近的Shadowbrokers的泄漏都覆盖比较全了，并且我找不到任何其他东西，除了恶心的勒索软件。

我分析的这个样本是R136a1 防御Kernelmode.info上面的。非常感谢他的分享。

我们将看到这个木马如何工作的并且它是如何被确认与Vault7泄漏有关：

所有的泄漏文档：https://fdik.org/wikileaks/year0/vault7/cms/space_11763715.html

网络操作，内存代码执行：https://fdik.org/wikileaks/year0/vault7/cms/files/ICE-Spec-v3-final-SECRET.pdf

主要的分析是Longhorn木马加载器和它的内存DLL加载功能，其被用于执行下载的payload，并且表示攻击者不想留下痕迹。这个功能恰恰在CIA泄漏的文档中有描述，并且我们可以看到确实按照这些规范制作。然后，我们更深入分析，隐蔽的监控后门payload（Black Lambert）被用于针对性的攻击，并且与CIA工具包有关。

下面是Longhorn Trojan加载器和模块payload（Black Lambert）的哈希：

[![](https://p1.ssl.qhimg.com/t01cb2d3f16a473aca5.png)](https://p1.ssl.qhimg.com/t01cb2d3f16a473aca5.png)

[https://virustotal.com/en/file/21f727338a4f51d79ade48fdfd9e3e32e3b458719bf90745de31b898a80aaa65/analysis/](https://virustotal.com/en/file/21f727338a4f51d79ade48fdfd9e3e32e3b458719bf90745de31b898a80aaa65/analysis/)

[https://virustotal.com/en/file/2156adcaae541ea1718ea52ce07bd1555cdcf25e9919f3208958f8c195f34286/analysis/](https://virustotal.com/en/file/2156adcaae541ea1718ea52ce07bd1555cdcf25e9919f3208958f8c195f34286/analysis/)

<br>

**0x01 Longhorn加载器的分析：Trojan.LH1**

1. 持久性

加载器将它自身注册为Windows服务（服务名：BiosSrv）：

[![](https://p0.ssl.qhimg.com/t019d228e9825a461de.png)](https://p0.ssl.qhimg.com/t019d228e9825a461de.png)

服务例程启动主线程，连接C&amp;C并且等待指令：

[![](https://p2.ssl.qhimg.com/t0136b8c2e5b931c175.png)](https://p2.ssl.qhimg.com/t0136b8c2e5b931c175.png)

2. 注册表

使用UuidCreate()和UuidToStringW()生成ClientID，然后将其写入HKLMSOFTWAREBiosInnovationsClientID：

[![](https://p0.ssl.qhimg.com/t0140ab4ac20fd17b7d.png)](https://p0.ssl.qhimg.com/t0140ab4ac20fd17b7d.png)

3. 通信

木马在资源“BINARY”下存储了两个资源：

101：SSL证书

102：C&amp;C服务器域名

Longhorn使用WinHTTP API来解析用户代理设置，并且通过SSL与C&amp;C通信。

[![](https://p1.ssl.qhimg.com/t01d03d3b1088e9c17f.png)](https://p1.ssl.qhimg.com/t01d03d3b1088e9c17f.png)

**安装证书**

为了和C&amp;C服务器通信，Longhorn木马从它的资源中释放出一个SSL证书，并且使用CertAddCertificateContextToStore()函数安装。

这个证书被用于和C&amp;C通信。它校验了服务端，并且如果没有证书，访问C&amp;C将显示一个错误页面。

[![](https://p2.ssl.qhimg.com/t01480020aa32160964.png)](https://p2.ssl.qhimg.com/t01480020aa32160964.png)

**C&amp;C**

用类似的方式，C&amp;C域名也从资源节中提取出来。在这个样本中是mercury-vapor.net：

[![](https://p2.ssl.qhimg.com/t01d80c608d2035eca9.png)](https://p2.ssl.qhimg.com/t01d80c608d2035eca9.png)

一旦证书安装完毕和C&amp;C域名提取，木马启动一个线程来连接C&amp;C，接受指令并得到文件。Longhorn使用随机延迟来尝试请求，尽量保持隐蔽，这是值得注意的：

[![](https://p3.ssl.qhimg.com/t01b103aee228b788c3.png)](https://p3.ssl.qhimg.com/t01b103aee228b788c3.png)

下面是URL：

[![](https://p3.ssl.qhimg.com/t0166010114433f504a.png)](https://p3.ssl.qhimg.com/t0166010114433f504a.png)

我们将在下文看到他们是什么意思。

4. 命令

checkin

get-scanner

put-scan

put-file

destroy-agent

5. 内存payload加载

得到并解压payload

加载器的主要目的是下载一个扫描器，在内存中执行并得到输出。下面是get-scanner的伪代码：

[![](https://p2.ssl.qhimg.com/t0110d455e21d33d2a9.png)](https://p2.ssl.qhimg.com/t0110d455e21d33d2a9.png)

扫描器是用LZ压缩的，加载器使用RtlDecompressBuffer解压它：

[![](https://p4.ssl.qhimg.com/t0172d3fe3cf6546c52.png)](https://p4.ssl.qhimg.com/t0172d3fe3cf6546c52.png)

现在，加载器在内存中执行模块。我们将下文解释如何做到。

在Longhorn加载器中内存代码执行（ICE）

我不想描述整个过程，和这个代码类似：https://github.com/fancycode/MemoryModule/blob/master/MemoryModule.c。主要步骤如下：

Mapping PE header

Mapping sections

Mapping IAT

Fixing memory permissions

Calling EntryPoint and main exported function

下面是加载扫描器模块DLL并在内存中执行（参见下文MODULE_REMOTE_ARGS结构）：

[![](https://p4.ssl.qhimg.com/t01bd23c2663e645aec.png)](https://p4.ssl.qhimg.com/t01bd23c2663e645aec.png)

**和Vault7的ICE规范类似**

在这部分，我们将指出和Vault7泄漏规范中所有的类似的地方。我们可以看到赛门铁克没有建议更多细节，加载器使用了文档的多种规范。

首先，我们能找到不同模块行为（ICE_FIRE, ICE_FIRE_AND_FORGET, ICE_FIRE_AND_COLLECT和 ICE_FIRE_AND_INTERACT）的精确描述（称为功能集）。因为Longhorn加载器简单的称为模块的导出函数，并且等待它的返回和输出，没有创建管道或者发送输入，我们研究了一个“Fire和Collect”模块：

[![](https://p5.ssl.qhimg.com/t012b93d032b21eeec4.png)](https://p5.ssl.qhimg.com/t012b93d032b21eeec4.png)

关于这个模块，它是木马的内存加载的恶意软件，在我们的例子中是神秘的扫描器，下面是CIA的实现描述：

[![](https://p3.ssl.qhimg.com/t01833e738c7a66275c.png)](https://p3.ssl.qhimg.com/t01833e738c7a66275c.png)

这就是我们的加载器：通过ordianl(1)得到导出函数。而且，正如我们所见，一个结构被填充，传递给模块的导出函数。这个结构在文档中有详细描述：

[![](https://p1.ssl.qhimg.com/t0153c4268bce9dd1bd.png)](https://p1.ssl.qhimg.com/t0153c4268bce9dd1bd.png)

在文档的历史版本中，我们找到了Longhorn使用的结构体和扫描器模块的的完美的匹配：

[![](https://p2.ssl.qhimg.com/t01ad84b99934f7eaa4.png)](https://p2.ssl.qhimg.com/t01ad84b99934f7eaa4.png)

尽管文档指定加载器在加载他们到内存后不应该修改模块的SEH，我们在下部分能看到Longhorn修改了它。

[![](https://p2.ssl.qhimg.com/t01ed8ad6dd3e0a5efa.png)](https://p2.ssl.qhimg.com/t01ed8ad6dd3e0a5efa.png)

**修改SEH**

当尝试从使用SEH的内存中加载dll时，Windows将弹出异常框。我们可以看到Longhorn在它的ICE加载例程中修改了它。

Windows X86使用的SEH验证例程在这篇文章中有描述：https://www.blackhat.com/presentations/bh-usa-08/Sotirov_Dowd/bh08-sotirov-dowd.pdf

基本检查标记ExecuteDispatchEnable和ImageDispatchEnable是否是进程标记，并且是将返回TRUE，否则返回FALSE或者ACCESS_VIOLATION。Windows在NTDLL函数RtlIsValidHandler()中实现这个验证过程。反汇编，我们能看到它用参数lpProcessInformationClass = 0x22调用NtQueryInformationProcess()来得到ProcessExecuteFlags。然后检查是否包含ImageDispatchEnable | ExecuteDispatchEnable = 0x30。

[![](https://p0.ssl.qhimg.com/t01e8cf6db997c48672.png)](https://p0.ssl.qhimg.com/t01e8cf6db997c48672.png)

下面是内存加载DLL的主函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010dd58feec17f82dc.png)

SEH修改发生在hook_fix_seh()函数中。通过5字节Jmp的方式HOOK了NtQueryInformationProcess()，指向hooker_NtQueryProcessInformation()。下面是ntdll中的该函数的反汇编：

[![](https://p4.ssl.qhimg.com/t0192f94d1a6e86080b.png)](https://p4.ssl.qhimg.com/t0192f94d1a6e86080b.png)

正如我们所见，第一条指令是mov eax， IMM，可以简单的使用一个jmp来覆盖。下面是加载器的新函数的伪代码：

[![](https://p5.ssl.qhimg.com/t019374f6835913af26.png)](https://p5.ssl.qhimg.com/t019374f6835913af26.png)

将强制NtQueryProcessInformation总是返回ImageDispatchEnable | ExecuteDispatchEnable，使得RtlIsValidHandler()总是返回TRUE，因此Windows认为SEH是正确的，因此不会显示错误。

**扫描器的输出**

扫描器的输出存储在一个文件中，路径由加载器的-o命令指定。当扫描器完成了，加载器使用MapViewOfFile()映射输出文件到内存中(在map_file_mem)，并且通过POST请求发送给下面网页： https://[CnC Domain]/agent/put-scan。

[![](https://p1.ssl.qhimg.com/t01feb4904cb926d261.png)](https://p1.ssl.qhimg.com/t01feb4904cb926d261.png)

<br>

**0x02 逆向Vault7的监控后门：Black Lambert**

卡巴斯基写了篇文章关于Lambert恶意软件家族，并且和CIA工具包有关：https://securelist.com/blog/research/77990/unraveling-the-lamberts-toolkit/。  我们将分析其中之一Balck Lambert。

1. ICE模块

Black Lambert（是一个ICE模块payload），通过ordinal(1)导出了它的入口点，其名字没有可疑。根据Vault7的规范（上文）。注意原始的恶意软件名是winlib.dll。

[![](https://p2.ssl.qhimg.com/t015b465e696cfc0c06.png)](https://p2.ssl.qhimg.com/t015b465e696cfc0c06.png)

而且，这个函数的参数完美匹配了MODULE_REMOTE_ARGS结构体，下面是导出函数的伪代码。这证明两个恶意软件是相同的一部分。

[![](https://p5.ssl.qhimg.com/t015e563b4887183381.png)](https://p5.ssl.qhimg.com/t015e563b4887183381.png)

2. 解密字符串

在恶意软件中的大部分字符串是加密的，通过偏移0x10029C20处的函数解密。我将解释解密过程，并提供IDAPython脚本来解密字符串并注释。

**解密过程**

加密字符串被存储在DWORD块中。第一个DWORD是加密字符串的个数。

[![](https://p0.ssl.qhimg.com/t01a53a7811cd415b71.png)](https://p0.ssl.qhimg.com/t01a53a7811cd415b71.png)

字符串的个数通过与0x90E7B322异或解码得到：

[![](https://p4.ssl.qhimg.com/t017a3a79e934047c62.png)](https://p4.ssl.qhimg.com/t017a3a79e934047c62.png)

主要字符串的解密是多个逻辑运算符的组合：

[![](https://p1.ssl.qhimg.com/t01c670af25c917ba01.png)](https://p1.ssl.qhimg.com/t01c670af25c917ba01.png)

进一步分析表明Black Lambert存储了命令的列表，结构体如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016348359432c679d1.png)

因为有超过50个结构体，解密加密的字段将帮助我们了解后门的种类，我就提供IDAPython脚本解密所有的加密字符串和命令。

**IDAPython脚本**

下面是用于解密字符串并注释的IDAPython脚本。我也增加了一个函数来解密并重命名木马实现的命令：https://gist.github.com/adelmas/678d3274c2656b91888e6aa903e05df6

[![](https://p5.ssl.qhimg.com/t0156b0b34e51694112.png)](https://p5.ssl.qhimg.com/t0156b0b34e51694112.png)

得到下面的字符串：https://gist.github.com/adelmas/9a35488337ea33d935333ef11f16ec37

[![](https://p4.ssl.qhimg.com/t011a8332e72ebd0dae.png)](https://p4.ssl.qhimg.com/t011a8332e72ebd0dae.png)

恶意软件中注释了超过1000个解密的字符串。在payload做每个操作后发送消息字符串（并清空），因此这使得逆向很快。

现在我们有了解码的字符串，我们能找到下面的与Black Lambert相关的构建数字（参见卡巴斯基的文章）。

[![](https://p5.ssl.qhimg.com/t0115dd5bcf7bdb45f7.png)](https://p5.ssl.qhimg.com/t0115dd5bcf7bdb45f7.png)

3. 命令

前面的解混淆的脚本也解密了命令并在IDA中重命名了。正如我们所见，脚本的输出如下，在BlackLambert中有大量的命令：

[![](https://p1.ssl.qhimg.com/t01b50c03ca9d349e07.png)](https://p1.ssl.qhimg.com/t01b50c03ca9d349e07.png)

这些命令和Vault7中CIA工具有关：https://wikileaks.org/vault7/document/Athena-v1_0-UserGuide/Athena-v1_0-UserGuide.pdf。同时，看下命令的列表和他们的实现让我想起了Duqu2.0，Balck Lambert确实被Avira和Windows的AV标记为Duqu2.

[![](https://p5.ssl.qhimg.com/t0122981371c9251218.png)](https://p5.ssl.qhimg.com/t0122981371c9251218.png)

大部分命令有一个很好理解的名字。

cmd_cat* : 横向移动 (参见下文)

cmd_wincontrol : 发送消息和窗口对象 (参见下文)

cmd_idlewatch : 获取当前用户的上次输入(参见下文)

cmd_hash : 使用CryptHashData()计算文件哈希

cmd_at : 使用NetScheduleJobAdd()添加计划任务

接下来，我们快速浏览下有趣的命令和Black Lambert和Duqu2中常见的功能。

4. 横向移动

Catinstall命令：安装DCOM加载器

后门被用于通过网络共享感染本地网络。它将连接远程计算机，添加如下防火墙规则，创建$IPC和$ADMIN共享，释放恶意软件的拷贝，并且最终移除共享。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a3850a6c95144166.png)

[![](https://p2.ssl.qhimg.com/t019f28ea61609af708.png)](https://p2.ssl.qhimg.com/t019f28ea61609af708.png)

Clsid参考值：`{`b7867b64-a163-4e5d-93bb-76e0cef7153b`}`

[![](https://p0.ssl.qhimg.com/t017105cfb2e915133e.png)](https://p0.ssl.qhimg.com/t017105cfb2e915133e.png)

5. 监控后门的功能

**远程桌面管理**

Cmd_idleWatch命令使用GetLastInputInfo()得到上次输入时间：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0155bffe245908768d.png)

然后，根据上次输入时间戳，发送下面的字符串通知攻击者：

[![](https://p5.ssl.qhimg.com/t01eb18cfe22b449ed7.png)](https://p5.ssl.qhimg.com/t01eb18cfe22b449ed7.png)

Cmd_screenshot：标准截屏功能

Cmd_winlist：得到打开的窗口列表，以便准备下条命令。

Cmd_winControl：使用SendInput()发送鼠标事件，并且使用PostMessage()、SendMessageTimeout()直接访问窗口对象。联合BalckLambert使用CreateDesktopW()创建的隐藏桌面，这使得攻击者在受害者看不见的情况下控制任何GUI应用。下面是一些窗口消息：

0x188 : LB_GETCURSEL

0x18A : LB_GETTEXTLEN

0x189 : LB_GETTEXT

0x149 : CB_GETLBTEXTLEN

0x147 : CB_GETCURSEL

0x148 : CB_GETLBTEXT

0x111 : WM_COMMAND

0x010 : WM_CLOSE

0x00D : WM_GETTEXT

而且， BlackLambert能移动鼠标指针并左击（通过发送MOUSEEVENTF_*命令）：

[![](https://p3.ssl.qhimg.com/t014243a5f1092430a3.png)](https://p3.ssl.qhimg.com/t014243a5f1092430a3.png)

**ModLoad命令**

这个命令是从内存加载DLL，并调用DllMain()。注意它没使用ICE模块规范。

[![](https://p2.ssl.qhimg.com/t0140b0618cd1684e40.png)](https://p2.ssl.qhimg.com/t0140b0618cd1684e40.png)

**网络和文件命令**

这里没啥有趣的，命令名字很明显。

**信息收集命令**

当然，这是网络间谍恶意软件都有的数据收集命令。他们很标准：

检测是否进程运行与VMWare或者Virtual PC，可能收到该文启发：https://www.codeproject.com/Articles/9823/Detect-if-your-program-is-running-inside-a-Virtual

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01eb486e1b522add9e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fd1f313e743a415e.png)

使用cmd_strings查找字符串，使用cmd_match查找文件名匹配

然后，使用cmd_get命令得到文件

<br>

**0x03 Yara规则**

下面的Yara规则用于检测Longhorn木马和BlackLambert。注意我没有在我的恶意软件转储中发现更多的样本，这两个恶意软件可能用于感染特定的计算机和网络，数量有限。

[![](https://p0.ssl.qhimg.com/t01b06442a84a97a170.png)](https://p0.ssl.qhimg.com/t01b06442a84a97a170.png)
