> 原文链接: https://www.anquanke.com//post/id/170364 


# Kutaki恶意软件绕过网关窃取用户凭证


                                阅读量   
                                **183853**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者cofense，文章来源：cofense.com
                                <br>原文地址：[https://cofense.com/kutaki-malware-bypasses-gateways-steal-users-credentials/](https://cofense.com/kutaki-malware-bypasses-gateways-steal-users-credentials/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t014d686295b2d4caa0.jpg)](https://p1.ssl.qhimg.com/t014d686295b2d4caa0.jpg)



## 前言

这是一个恶意软件在用户眼皮底下进行攻击的案例。最近我们发现了一起网络钓鱼攻击活动，该活动通过将Kutaki恶意软件隐藏在合法的应用程序中来绕过电子邮件网关，从而获取用户凭据信息。

虽然Kutaki窃密软件使用的反沙箱和反调试技术略显落后，但不要小看它。它对未硬件化虚拟机及其他一些分析工具具有很好的对抗性。可以绕过很多常规的检测手段。

可以通过点击这里了解[Cofense Intelligence](https://cofense.com/product-services/phishing-intelligence/)的IT团队如何在诸如此次活动在内的网络钓鱼活动和恶意软件威胁方面处于行业领先地位。



## 细节

Cofense Intelligence最近发现了一起小范围的网络钓鱼活动，这起活动在合法的[Visual Basic](https://github.com/marifrahman/RMS/tree/master/CODE)应用中隐藏Kutaki窃取软件和键盘记录器，将其作为OLE包放置在Offic文档中来完成分发。

Kutaki使用了一系列反虚拟化和反分析技术，但看起来这些技术都是从2010年至2011年的一些博客中借鉴而来。Kutaki 窃密软件可以从键盘，鼠标，剪贴板，麦克风和屏幕（以屏幕截图形式）等途径来收集用户输入的信息。我们还发现 Kutaki通过在Windows中执行[cURL](https://curl.haxx.se/windows/)来检索目标主机是否带有SecurityXploded推出的[BrowserPasswordDump](https://securityxploded.com/browser-password-dump.php)工具。

虽然它使用的逃避检测技术不够先进，但在对抗检测和分析方面，仍有不少亮点。



## 藏在眼皮底下：混淆

这个Kutaki变种将恶意内容隐藏在Visual Basic培训应用中。试图通过隐藏在看似正常的Visual Basic培训应用中这种手段来使自己处于白名单，并且轻而易举的绕过静态签名检测。

[![](https://p1.ssl.qhimg.com/t01e9c14578c596d1ee.jpg)](https://p1.ssl.qhimg.com/t01e9c14578c596d1ee.jpg)

图1：项目详情

[![](https://p3.ssl.qhimg.com/t01424fdd84b11f35b9.jpg)](https://p3.ssl.qhimg.com/t01424fdd84b11f35b9.jpg)

图2：项目代码块

即使不是专业的程序员，也看的出这里有些程序看起来似乎放在了错误的分支下，除此之外还可以看到到表单（GUI元素）和控制它们的程序之间存在紧密关联。图3展现了他们的映射关系。

[![](https://p3.ssl.qhimg.com/t0163666b6633eba68d.jpg)](https://p3.ssl.qhimg.com/t0163666b6633eba68d.jpg)

图3:表单元素与其代码相对应

通过对程序进行检查，可以发现应用被安装了后门。如图4，将合法程序结构和被注入了后门的程序进行了对比。

[![](https://p3.ssl.qhimg.com/t0166e88c9ad2329ea2.jpg)](https://p3.ssl.qhimg.com/t0166e88c9ad2329ea2.jpg)

图4：”ff”和”frmLogin”是原生程序，而”chee”、”saamneao”、”dewani”以及”ende”是注入的后门

我们不仅看出命名上的差异（大部分合法程序以”frm“开头），还可推断出注入程序采用的随机命名的方式。除此之外，那些被注入了后门的函数，函数名无法解析，只是由解码器临时分配。

注入这种后门时使用了混淆技术，通过 rtcStrReverse函数可以解码经反转的二进制字符串。如图5，即为一个混淆实例。

[![](https://p0.ssl.qhimg.com/t017faa68352f8477c1.jpg)](https://p0.ssl.qhimg.com/t017faa68352f8477c1.jpg)

图5：3个使用rtcStrReverse对混淆字符串进行解码的实例

在隐藏可疑API调用时，使用了很多类似的字符串混淆。图6展示了对于[Sleep](https://docs.microsoft.com/en-us/windows/desktop/api/synchapi/nf-synchapi-sleep)和 [ShellExecuteA](https://docs.microsoft.com/en-us/windows/desktop/api/shellapi/nf-shellapi-shellexecutea)字符串的混淆。

[![](https://p2.ssl.qhimg.com/t016c71731a064e2740.jpg)](https://p2.ssl.qhimg.com/t016c71731a064e2740.jpg)

图6：Sleep和ShellExecuteA字符串

这些字符串是DllFunctionCall（Visual Basic应用中，一种可以特定DLL文件从检索函数地址的方法）中一个很小的结构体。如下所示：

```
typedef struct _DllFunctionCallDataStruct `{`
void * lpLibName;
void * lpExportName;
`}` DllFunctionCallDataStruct;
```

在图6中，我们可以看到这些结构是如何进行映射的。对于DLLFunctionCall的调用，封装在类似的代码段中，如图7所示。

[![](https://p3.ssl.qhimg.com/t01d94804664ee549e8.jpg)](https://p3.ssl.qhimg.com/t01d94804664ee549e8.jpg)

图7：典型封装：DllFunctionCall调用

通过仔细分析，我们找到了18个以这种方法进行混淆的API，详见图8：

[![](https://p5.ssl.qhimg.com/t01c298f6e54d3c4946.jpg)](https://p5.ssl.qhimg.com/t01c298f6e54d3c4946.jpg)

图8：对Kutaki执行恶意行为时调用的API进去去混淆



## 反虚拟化

Kutaki使用了一些基本的检测和对比来验证自身是否运行在虚拟化环境中。首先它会读取注册表值`HKLMSystemCurrentControlSetServicesDiskEnum`,并将返回结果与“undesirable”字符串进行比较。图9为读取注册表代码。

[![](https://p3.ssl.qhimg.com/t015d1369e5fd9b890f.jpg)](https://p3.ssl.qhimg.com/t015d1369e5fd9b890f.jpg)

图9：Kutaki从注册表读取磁盘信息

这个注册表表值中包含了当前计算机的磁盘信息。第一个磁盘对应的值为“0”，第二个磁盘对应的值为“1”，依此类推。在该分析VM的实例中，值0包含图10中观察到的数据。如图10，为分析反VM功能时，该计算机注册表值为0的实例。

[![](https://p3.ssl.qhimg.com/t01e164995a16886fac.jpg)](https://p3.ssl.qhimg.com/t01e164995a16886fac.jpg)

图10：DisksEnum注册表值实例

上图中突出显示的部分说明了该磁盘属于[VirtualBox VM](https://www.virtualbox.org/)。图11和图12对两种用来识别不同类型虚拟机的进行了比较。而图13展示了Kutaki使用的所有虚拟化检测字符串。

[![](https://p5.ssl.qhimg.com/t016939604c938176e2.jpg)](https://p5.ssl.qhimg.com/t016939604c938176e2.jpg)

图11：检测注册表值中是否包含“VIRTUAL”字符串

[![](https://p0.ssl.qhimg.com/t01cecce076bf5733ea.jpg)](https://p0.ssl.qhimg.com/t01cecce076bf5733ea.jpg)

图12：检测注册表值中是否包含“VBOX”字符串

[![](https://p2.ssl.qhimg.com/t01c6e2a83912b64d08.jpg)](https://p2.ssl.qhimg.com/t01c6e2a83912b64d08.jpg)

图13：进行虚拟化检测的字符串

图12中的字符串比较结果将与图10中注册表值进行匹配。匹配成功后，Kutaki不会立刻退出，而是继续进行其他虚拟化检测。只有当所有检测完成后，它才会判断是否继续运行。图14展示了该机制的执行流程，有关检测器的细节将在后文进行详细说明。

[![](https://p0.ssl.qhimg.com/t01677a526ae9c4553b.jpg)](https://p0.ssl.qhimg.com/t01677a526ae9c4553b.jpg)

图14：反分析/虚拟化流程

为了完善磁盘检测。Kutaki 将[CreateToolhelp32Snapshot](https://docs.microsoft.com/en-us/windows/desktop/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot), [Module32First ](https://docs.microsoft.com/en-us/windows/desktop/api/tlhelp32/nf-tlhelp32-module32first)和 [Module32Next](https://docs.microsoft.com/en-us/windows/desktop/api/tlhelp32/nf-tlhelp32-module32next)结合，来确定沙盒及调试工具相关模块是否已经注入到内存地址中。这些API会对正在运行的进程进行快照（包括堆、模块等），找到第一个模块后，会对已经映射到进程的后续模块进行迭代。图15展示了Kutaki设置快照并对指向第一个模块的指针进行检索。

[![](https://p3.ssl.qhimg.com/t013b5a3ccbbd3307eb.jpg)](https://p3.ssl.qhimg.com/t013b5a3ccbbd3307eb.jpg)

图15：Kutaki建立模块识别循环

Kutaki 会对sbiedll.dll和dbghelp.dll这两个分别属于[Sandboxie](https://www.sandboxie.com/SBIE_DLL_API)和[Microsoft](https://docs.microsoft.com/en-us/windows/desktop/debug/debug-help-library)的dll文件进行检测，图16展示了对dbghelp.dll的去混淆及对比检测。

[![](https://p4.ssl.qhimg.com/t01c9df83ef30a7119f.jpg)](https://p4.ssl.qhimg.com/t01c9df83ef30a7119f.jpg)

图16：对Windows Debug DLL的去混淆及对比检测

对比的结果将保存在数据结构体中，之后由_check_anti_analysis进行检测。

在最终的反虚拟化检测之前，Kutaki会再次读取注册表值`HKEY_CURRENT_USERSoftwareMicrosoftWindowsCurrentVersion`，来检查CurrentVersion项中是否存在一些特殊的 ProductID值。图17展示了该技术。

[![](https://p1.ssl.qhimg.com/t01d6260a0e3df31fd9.jpg)](https://p1.ssl.qhimg.com/t01d6260a0e3df31fd9.jpg)

图17：打开注册表项进行值比较

Kutaki尝试寻找名为“ProductID”的值。如果找到一个具有该值的键，会将其与三个字符串进行比较，来识别当前环境为哪种沙箱平台。以下为大致描述此过程的伪代码：

```
p_id = RegQueryValueExA(“ProductID”)

if (p_id))`{`

if (p_id == ‘76487-337-8429955-22614’) `{`

return “Anubis”

`}`

elif (p_id == ‘76487-644-3177037-23510’) `{`

return “CWSandbox”

`}`

elif (p_id == ‘55274-640-2673064-23950’) `{`

return “JoeSandbox”

`}`

else `{`

return None

`}`

`}`
```

图18为Kutaki使用的这种循环嵌套。

[![](https://p4.ssl.qhimg.com/t014734ae2a3d4ef44b.jpg)](https://p4.ssl.qhimg.com/t014734ae2a3d4ef44b.jpg)

图18：使用嵌套循环来检测沙箱

当所有的检测完成后，Kutaki会解析得到的结果，来确定是终止主循环还是继续进行。解析程序会解析每一个“非0”的返回值（即检测到某些东西），如果得到这种返回值，则退出主循环。图19为检测实例：

[![](https://p1.ssl.qhimg.com/t0162f874eaa6f3e6ab.jpg)](https://p1.ssl.qhimg.com/t0162f874eaa6f3e6ab.jpg)

图19：对获取的反分析检查结果进行解析



## 行为

一旦Kutaki确定它没有被发现，它将继续进行窃取主机数据的行为。在窃取过程中，Kutaki先从资源中提取对应的图片，将其放到用户主机的临时文件夹中，然后使用`ShellExecuteA（“cmd.exe / c C： Users  admin  AppData  Local  Temp  images1.png”）`来打开它。这是一个诱饵图片，来欺骗使用户，使他们相信自己点击只是一个图片（实际为OLE包）。

该图片是一个发票模板，然而攻击者很少使用这个诱饵图片，因为使用谷歌快速搜索对“税务详细信息发票”关键词进行检索，这张图片就排在第二个。 实际上，攻击者真正使用的是这张图片：`hxxp：// batayneh [。] me / invoice-with-bank-details-template / invoice-with-bank-details-template-blank-tax-luxury /`

显示文档后，Kutaki会检查当前的可执行文件名称是否与字符串“hyuder”匹配，如果不匹配，将进行自我拷贝，并重命名为<br>`C:Users&lt;username&gt;AppDataRoamingMicrosoftWindowsStart MenuProgramsStartuphyuder.exe`

图20为使用调试器中进行检查。 如果启动了新进程，父进程将不会退出，而是处于挂起状态。

[![](https://p3.ssl.qhimg.com/t015dadb277126efec8.jpg)](https://p3.ssl.qhimg.com/t015dadb277126efec8.jpg)

图20：Kutaki将当前名称与所需名称进行比较

图21为Kutaki构建的文件路径，它会把自己的副本拷贝到该路径。 放置在启动文件夹中，从而实现持久性。

[![](https://p4.ssl.qhimg.com/t0171beb130a3d83bbb.jpg)](https://p4.ssl.qhimg.com/t0171beb130a3d83bbb.jpg)

图21：Kutaki构建了用于拷贝自身副本并实现持久性的字符串

Kutaki继续执行其主要恶意功能。 这里要注意一下：可能有些读者会产生疑问，如果只是简单的重命名可执行文件“hyuder.exe”，是否会阻止它删除自己的副本？答案是会的。如果为定义好的文件名，它将直接执行而不会删除任何内容。其余的代码有点没有什么可研究之处，主要是因为几乎所有的发生的恶意行为都与二进制文件没有太大关联。

在继续进一步操作之前，Kutaki将与C2服务器进行通信，告知C2服务器又感染了一台新的主机。 图22是分析时观察到的相关流量

[![](https://p0.ssl.qhimg.com/t017c7f68400516ba68.jpg)](https://p0.ssl.qhimg.com/t017c7f68400516ba68.jpg)

图22：Kutaki的C2服务器处于离线状态

Kutaki还携带了一个cURL( 一个从Linux移植而来的应用程序)，通过它可以使用命令行对联网资源进行访问。

虽然Kutaki可以像之前那样直接和C2建立连接来下载payload，然而在这个阶段它却使用了cURL来连接C2服务器下载此时所需的payload。虽然其中缘由不得而知，但可以确定的是使用cURL是攻击者所设定好的，因为Kutaki直接请求下载其他payload时C2服务器会出现拒绝连接，而当User Agent为cURL时则可成功执行。图23记录了使用cURL与C2建立连接，获取第二阶段payload。

[![](https://p5.ssl.qhimg.com/t0194e353393959634e.jpg)](https://p5.ssl.qhimg.com/t0194e353393959634e.jpg)

图23：Kutaki使用cURL下载并执行下一阶段的payload。 请注意User-Agent字符串“curl / 7.47.1”。

此时，下载的payload为SecurityXploded推出的BrowserPasswordDump工具。 此工具可以从以下浏览器中检索密码：

Firefox<br>
Google Chrome<br>
Microsoft Edge<br>
Internet Explorer<br>
UC Browser<br>
Torch Browser<br>
Chrome Canary/SXS Cool<br>
Novo Browser<br>
Opera Browser<br>
Apple Safari

由于C2服务器已经下线，所以我们无法得知由于使用BrowserPasswordDump工具而导致的数据泄露情况。



## 历久弥新

虽然Kutaki使用了一些传统的，已经被广泛使用的技术来检测沙箱和调试。 这些对于未硬件化的虚拟机和其他一些分析工具仍然有效。 此外，通过将后门写入合法应用的手法可以绕过很多常规的检测技术。

要了解有关最近恶意软件趋势的更多信息，请阅读[2018年年终报告](https://cofense.com/)。

**ProductID检测**

```
76487-337-8429955-22614 // Anubis Sandbox
76487-644-3177037-23510 // CW Sandbox
55274-640-2673064-23950    // Joe Sandbox
```

<a class="reference-link" name="AntiVM%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>**AntiVM字符串**

```
VIRTUAL
VBOX
*VMW
sbiedll.dll
Dbghelp.dll
```

**IoCs**

```
hxxp://babaobadf[.]club/kera/kera3x[.]php
hxxp://janawe[.]bid/FF/om2[.]exe
```

**hash**

```
89D45698E66587279460F77BA19AE456
A69A799E2773F6D9D24D0ECF58DBD9E3
70bf5dd41548e37550882eba858c84fa
8e4aa7c4adec20a48fe4127f3cf2656d
```
