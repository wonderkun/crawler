
# 【技术分享】如何利用Windows默认内核调试配置实现代码执行并获取管理员权限


                                阅读量   
                                **87044**
                            
                        |
                        
                                                                                                                                    ![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blogspot.co.uk
                                <br>原文地址：[https://tyranidslair.blogspot.co.uk/2017/03/getting-code-execution-on-windows-by.html](https://tyranidslair.blogspot.co.uk/2017/03/getting-code-execution-on-windows-by.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85773/t01f622517697583340.jpg)](./img/85773/t01f622517697583340.jpg)**

****

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

本文来自于很久以前我的一次现场渗透测试工作成果。在等待其他测试工作完成间隙，客户对我能否在某个Windows工作站上执行代码很感兴趣（原因在这里并不重要）。在测试现场，我拥有测试机的物理访问权限，因此这件事情不难完成。我最终的解决方案是利用Windows默认内核调试配置，在不对系统配置做出永久性修改的前提下实现了任意代码执行。

这种技术的优点在于它所使用的工具集很小，可以在工作中随身携带以防万一。然而，它要求目标设备存在已启用的COM1串口，且未使用TPM型Bitlocker或类似机制，这一条件不一定能得到满足。

有人可能会对此不以为然，因为能够物理访问目标机器意味着攻击目标已基本达成，这也是我为什么认为这种方法是Windows设备中存在的末日型漏洞。然而，内核调试配置是系统的默认设置，管理员可能不知道如何修改。从客户角度来看，这种方法让我们这些人看起来像是那种混蛋黑客，毕竟使用命令行CDB比WinDBG看起来更酷一些。

为了避免读者误解本文初衷，在此强调：这并不是一个Windows漏洞！

现在，让我们来看一下技术细节。

<br>

**二、应用场景**

你发现自己身处一个布满Windows工作站的房间中（希望是个合法场景），你的任务是在其中一台机器上获得代码执行权。首先映入你脑海的有以下几种办法：

1、更改启动设置，从CD/USB设备中启动，修改HDD

2、打开机器外壳，拉出HDD，修改其中内容并重新插入

3、滥用Firewire DMA访问来读写内存

4、滥用机箱后面的网络连接，尝试进行PXE引导或者对本机的网络/域流量开展MitM（中间人）攻击。

仔细观察工作站，你发现机器引导顺序第一位是硬盘硬盘引导，而BIOS密码的存在使你无法修改此顺序（假设本机BIOS不存在漏洞）。此外，此例中工作站机箱上有个物理锁，你无法打开它的外壳。最后，工作站没有Firewire或其他外部PCI总线来DMA攻击。我没有测试网络攻击场景，但进行PXE启动攻击或MitM攻击可能会遇到IPSec问题，导致攻击难以奏效。

这些工作站存在一个经典的9针串行接口。藉此我想到了Windows在COM1上有个默认配置的内核调试接口，然而内核调试在本案例中并没有启用。那么有没有一种办法使我们在不具备管理员权限下启用系统的内核调试功能呢？本文的答案是肯定的。接下来让我们来研究如何在这种场景下完成这一任务。

<br>

**三、环境准备**

在开始工作前，首先你的手头上需要具备以下几样东西：

1、测试机的串口（这是必要条件）。驱动安装正常的串口转接USB也行。

2、本地安装的Windows。这么要求主要是为了操作便利。现如今也许有工具可以在Linux/macOS上进行完整的Windows内核调试，但我对此表示怀疑。

3、一条调制解调器线缆。你需要这个东西来连接测试机器的串口与工作站的串口。

现在确保你的测试机上环境准备就绪，设置WinDBG使用本地COM口来进行内核调试。只需要打开WinDBG，在菜单中依次选择“文件”、“内核调试”或者按下CTRL+K组合键。你可以看到如下对话框：

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dca7a9deaad9cb99.png)

在Port一栏填入正确的COM口值（即你的USB转串口值）你不需要修改波特率，保留Windows的默认值115200即可。你可以在另一个系统上以管理员运行“bcdedit /dbgsettings”命令来检查这个值是否设置正确。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://4.bp.blogspot.com/-wUwr_tUvzpE/WMUo9gh8IvI/AAAAAAAAA6U/Aj_eAqjgu84CBU5iZgsrnUV-nRKeEnRGQCLcB/s400/dbgsettingas.PNG)

你也可以通过这个命令来完成同样工作：

```
windbg -k com:port=COMX,baud=115200
```

**<br>**

**四、在Windows 7上启用的内核调试功能**

在Windows 7上启用内核调试功能十分简单（Vista上也是如此，但现在应该没多少人用了吧？）。重启工作站，在BIOS屏幕加载完毕后按下F8键，顺利的话你可以看到如下界面：

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://4.bp.blogspot.com/-117yqgre5nU/WMUpeF1K10I/AAAAAAAAA6Y/T_fbX51m6y4G9vgq1lD_ZbtqiCvIR1p-ACLcB/s640/VirtualBox_Windows%2B7_12_03_2017_10_56_35.png)

使用方向键，选择调试模式并回车，Windows开始启动。希望你转到WinDBG界面时可以看到界面上显示的系统启动信息。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f53b4634bc54d2a8.png)

如果启动信息没有显示，可能是COM口被禁用、内核调试配置发生改变或者你的USB转串口适配器工作不正常。

<br>

**五、在Windows 8-10上启用内核调试功能**

接下来看新版本的Windows上如何操作，你会发现按下F8时没有发生任何变化。这是因为微软自Windows 8以后对引导过程做的一个修改。随着SSD的流行以及Windows启动过程机制的更改，微软已逐渐摒弃F8键功能。此功能依然存在，但你需要在类似UEFI的菜单中进行配置。

现在有个问题，之前我们假设我们无法访问BIOS配置，因此我们也无法访问UEFI配置选项，你能做到的只是进入设置界面，选择重启后进入高级启动模式选项，或者在命令行中利用shutdown命令配合/r /o参数完成这一任务。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://4.bp.blogspot.com/--gGyw6vD3Bo/WMUtHko5Q-I/AAAAAAAAA60/6TInoXyIbqQ3UKEwHP4q0IdKxVz_9j2RACLcB/s1600/advanced_options.PNG)

这些方法对我们来说都不适用。幸运的是有个[文档](https://www.howtogeek.com/126016/three-ways-to-access-the-windows-8-boot-options-menu/)中描述了另一种方法：在开始菜单中选择重启的同时按住Shift键，这样系统将在重启时进入高级启动选项模式。听起来此方法也不怎么有效，因为你还是得进入系统才能选择菜单。幸运的是在那台工作站的登录界面有个重启选项，而按住Shift这个技巧在这个界面还是可以正常工作。在登录界面右下角点击电源选项，按住Shift同时选择重启，一切顺利的话你可以看到如下界面：

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://4.bp.blogspot.com/-00IbgsMacyY/WMUwffsmzLI/AAAAAAAAA7A/lWZtEx6vR3IJJRlRLVSeqszp6ZU6RbbMgCEw/s640/windows_10_advanced_options.png)

选择“故障排除”选项，进入下一界面。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fa8292d49cb2bdac.png)

在这里选择“高级选项”，进入下一界面。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01266c62de1862d54a.png)

在此界面中，选择“启动设置”选项，进入如下界面。前面那个界面中你第一反应可能认为应该选择“命令行”选项以获取系统命令提示符，但这种情况下你还是需要一个本地管理员用户的密码。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://4.bp.blogspot.com/-5c5AcYrac54/WMUyonDHZhI/AAAAAAAAA7Y/e00GOo0S6TYKq2B4st-cebK3DH3n6X7MQCLcB/s640/windows_10_startup_settings.png)

选择“重启”后工作站将会重启，你可以看到如下提示界面。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0125cf870e3dcc9515.png)

最后，按下F1启动内核调试功能。现在，F8的功能又回来了，一切按照计划进行的话，你可以在WinDBG中看到熟悉的启动信息。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://4.bp.blogspot.com/-ED7sRtqwx1s/WMUzYoepXbI/AAAAAAAAA7k/IjGuOTToytE-goac6jq2FaoQPp5QO9YegCLcB/s640/wnidbg_output_win10.PNG)

<br>

**六、代码执行**

现在你拥有了附加到工作站的一个内核调试器，最后一个工作就是绕过登录界面。使用Firewire DMA攻击时的一个常见技巧是在内存中搜索与LSASS的密码检查相对应的对应模块（Pattern）并将其终止，然后任何登录密码都可以进入系统。这是一个办法，但并不完美（比如你会在系统日志中留下登录记录）。此外，很有可能本地管理员账号已经重命名过，那么你还需要知道一个可用的用户名。

与此相反，我们准备发起一个更有针对性的攻击。我们拥有的是系统可用的内核视图，而不是物理内存视图，因此还是有希望的。登录界面中有个辅助工具选项，使用这个选项会以SYSTEM权限创建一个新进程。我们可以劫持该进程创建过程以获得命令提示符，来完成攻击任务。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0169c0bcd9b38bc9d2.png)

首先，我们要对目标主机配置符号链接。没有符号链接我们无法通过枚举必要的内核结构以查找要攻击的系统数据。确保符号链接配置正确的最简单的一个方法是在命令调试窗口中输入“!symfix+”然后输入“!reload”即可。输入“ !process 0 0 winlogon.exe”命令，查找负责登录窗口显示的进程。一个成功的输出如下所示：

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fdf6502eb09989cb.png)

上图标红部分值即为EPROCESS结构的内核地址。复制该值，使用“.process /i EPROCESS”命令获得一个交互式调试会话。输入“g”，按下F5或回车，你可以看到以下信息：

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019278506231fc75e3.png)

现在，通过这个交互式会话，输入“ !reload -user”，我们可以枚举用户模块并加载他们的符号链接。我们可以在CreateProcessInternalW上设置断点，这个函数在每次创建新进程时都会用到。不同系统版本中该函数所处位置不一样，在Windows 7上它位于kernel32 DLL中，在Windows 8以上它位于kernelbase DLL中。因此，根据系统版本，使用“bp MODULE!CreateProcessInternalW”命令对相应模块进行替换。

设置断点后，点击登录屏幕上的轻松访问按钮，此时断点条件被触发。现在依次输入“r”和“k”命令，导出当前寄存器值，显示返回地址信息。如下所示：

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c052a57fc708d01b.png)

我们可以在堆栈轨迹中看到与轻松访问貌似有关的调用，如WlAccessibilityStartShortcutTool等。CreateProcessInternalW需要很多参数，但我们真正感兴趣的只有第三个参数，它是一个指向NUL结尾的命令行字符串指针。我们可以修改该指针指向命令提示符以执行命令。首先，使用“dU”命令确保我们已获取正确的字符串，对于x64系统，我们需要使用“dU r8”命令，因为第三个参数存储在r8寄存器中，对于x86系统我们使用的是“dU poi(@esp+c)”命令，因为32位系统上所有的参数都在堆栈上进行传递。如下所示：

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fadf3d65f549200c.png)

可知WinLogon正在试图创建一个utilman.exe的运行实例。现在这个字符串处于可写状态（如果不可写，系统就会崩溃，这是CreateProcess的一个愚蠢行为），我们直接覆盖它即可。使用ezu r8 "cmd"或者ezu poi(@esp+c) "cmd"命令，输入g，回车，命令提示符就会出现在你的眼前。

[![](./img/85773/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b58014c12fecc7d1.png)

**<br>**

**七、缺点分析**

该方法存在多个不足，如：

1、工作站必须有个串口，串口必须配置为COM1，现如今这种情况已不常见。

2、操作中工作站必须重启，这意味着你无法获得任何已登录用户的凭证或内存中的敏感信息。另外如果工作站有个启动密码，你也无法对它采取重启操作。

3、内核调试配置必须处于默认设置状态。

4、在配置了TPM型Bitlocker机器上，你无法在忽略Bitlocker引导条件下改变调试器配置。

最后我想说明的是这种方法的配置成本较低，你只需要随身携带一个USB转串口适配器以及一根闲置调制解调器线缆即可，这并不麻烦。

<br>

**八、防御措施**

有以下一些方法可以防御此类攻击：

1、将默认调试配置改为本地内核调试。这种模式意味着只有以管理员权限运行的本地调试器能够调试内核（且调试功能必须启用）你可以通过启动管理员命令行，输入“bcdedit /dbgsettings LOCAL”更改配置。你也可以通过登录脚本或GPO选项实现自动配置。

2、不要购买带有串口的工作站。听上去不是个好主意，因为很多时候你没法掌握购买权。但仍然不要购买带有无意义接口的设备，据我所知有些供应商仍然生产具有该接口的工作站。

3、如果你的电脑带有串口，请在BIOS中禁用它们。如果无法禁用，请将它们的默认I/O口设置为除0X3F8的其他值。老式COM口不能即插即用，Windows使用了显式I/O口与COM1通信。如果你的COM口未配置为COM1，Windows将无法正确使用它们。如果你安装的是二手市场的COM口设备，同样需要对此项进行修改。

4、最后请使用TPM型Bitlocker。即使之后别人没办法对你的硬盘进行离线修改，这样做也是值得的。Bitlocker结合TPM可以阻止别人在不知道Bitlocker恢复密钥前提下启动系统的调试功能。在Windows 8以上进入系统设置选项前需要对启动选项进行临时修改配置，这会导致TPM引导失败。我没有在Windows 7上测试此项功能，因为启动菜单位于winload.exe启动进程中，此时Bitlocker的密钥已经解密，因此我认为使用F8可能无法修改启动选项。读者可以在配置Bitlocker及TPM的Windows 7机器上进行测试。

另一个有趣的事情是，我在写这篇文章时，最新版的Windows 10（1607周年版）已经将内核调试默认设置为本地调试状态。然而如果你从老系统升级而来，这个选项可能在升级期间未发生改变，你需要核实一下。

<br>

**九、总结**

根据前文分析，这个方法不是一个特别严重的系统缺陷。如果已经有人能够物理访问你的机器，他已经可以采用一些常见手段进行攻击（如HDD访问、BIOS、Firewaire等）。物理攻击法是个好方法，为此你也需要在物理层面对你的机器进行防护。此外你还可以考虑部署Bitlocker，这样别人就难以通过攻击启动过程来危害机器，同时也可以防止电脑被窃后的敏感信息泄露。
