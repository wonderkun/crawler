> 原文链接: https://www.anquanke.com//post/id/85477 


# 【技术分享】基于虚拟化的安全（part1）：引导过程


                                阅读量   
                                **100676**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.amossys.fr
                                <br>原文地址：[http://blog.amossys.fr/virtualization-based-security-part1.html](http://blog.amossys.fr/virtualization-based-security-part1.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01fe5234b67e46fdac.jpg)](https://p3.ssl.qhimg.com/t01fe5234b67e46fdac.jpg)

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**0x00 前言**



本文是覆盖基于虚拟化的安全和设备保护功能的文章的一部分。这些文章的目的是从技术的角度分享这些功能以便更好的理解。这第一篇文章将涵盖系统引导过程，从Windows bootloader到VTL0启动。

**<br>**

**0x01 基于虚拟化的安全**



基于虚拟化的安全（VBS）是微软Windows10和Windows Server2016的一个主要的安全特性。例如，DeviceGuard和CredentialGuard都依赖它。DeviceGuard允许系统阻止任何不受信任的程序。同时CredentialGuard允许系统隔离lsass.exe进程，以便阻止类似Mimikatz等工具内存读取密码。

这个新功能的主要思想是使用硬件虚拟化技术（例如Intel VT-x），以便在两个虚拟机（VM）之间实现强隔离，并且将来功能可能更丰富。这些技术允许虚拟机管理器（VMM）使用扩展页表（EPT）来对物理页设置不同的权限。换句话说，一个VM能够在它的页表入口（PTE）设置一个物理页可写（+W），并且VMM能够通过在它的EPT上设置适当的权限来授权或阻止这种行为。

基于虚拟化的安全依赖Hyper-V技术，其将产生不同虚拟信任等级（VTL）的虚拟机。Hyper-V包括一个hypervisor，并且任何操作系统，甚至主操作系统，都包含在VM中。这个主操作系统（Windows）被认为是根VM。Hyper-V信任它且接受像控制其他VM的管理命令。其他的VM可能是“开明的”，如果这样，则向Hyper-V发送受限消息以便他们自己管理。

VTL是有序号的，更高的是最受信任的。现在有两个VTL：

1.  VTL0，是一个普通的环境，且基本包含标准的Windows操作系统。

2.  VTL1，是一个安全的环境，且包含一个微内核和安全的应用程序，称为trustlet。

[![](https://p2.ssl.qhimg.com/t01fd4d349fdd0f58f8.png)](https://p2.ssl.qhimg.com/t01fd4d349fdd0f58f8.png)

图1 – 基于虚拟化的安全的概览

CredentialGuard安全机制使用这个技术在VTL1 trustlet（lsaiso.exe，上图中“Isolated LSA”）中隔离关键的lsass.exe进程，甚至使得VTL0内核不能访问它的内存。只有消息可以从VTL0转发到隔离的进程，有效的阻止了像Mimikatz这类的密码和哈希收集工具。

DeviceGuard安全机制使得VTL0内核地址空间的W^X内存缓解（物理页不能同时具有可执行和可写权限），并且接受包含授权代码签名者的策略。如果VTL0内核想要使一个物理页可执行，它必须请求VTL1来改变（图中的“HVCI”），它会根据策略校验签名。对于用户模式的代码，这不起作用，只有VTL0内核才请求签名验证。策略在引导启动时加载，且之后不能修改，只有强制用户重启才能加载新的策略。

策略也是被签名的：在这种情况下，授权签名者在UEFI变量中设置，且新的策略将校验这个签名者。UEFI变量设置他们的Setup和Boot标志，意味着在启动后他们将无法被访问和修改。为了清除这些变量，本地用户必须使用一个自定义的微软EFI bootloader重启，在用户交互操作（通过输入密码）后移除他们。

因此，VBS强依赖[SecureBoot](https://technet.microsoft.com/en-us/library/hh824987.aspx)。引导加载器的完整性必须被校验，因为它负责加载策略、Hyper-V和VTL1等等。

如果你对设备保护的细节感兴趣，你能阅读这个MDSN的文章：[https://blogs.technet.microsoft.com/ash/2016/03/02/windows-10-device-guard-and-credential-guard-demystified/](https://blogs.technet.microsoft.com/ash/2016/03/02/windows-10-device-guard-and-credential-guard-demystified/)。

我们也鼓励你阅读Alex lonescu和Rafal Wojtczuk的BlackHat 2015/2016的演讲，将有很大帮助：

[http://www.alex-ionescu.com/blackhat2015.pdf](http://www.alex-ionescu.com/blackhat2015.pdf)

[https://www.youtube.com/watch?v=LqaWIn4y26E](https://www.youtube.com/watch?v=LqaWIn4y26E)

[https://www.blackhat.com/docs/us-16/materials/us-16-Wojtczuk-Analysis-Of-The-Attack-Surface-Of-Windows-10-Virtualization-Based-Security.pdf](https://www.blackhat.com/docs/us-16/materials/us-16-Wojtczuk-Analysis-Of-The-Attack-Surface-Of-Windows-10-Virtualization-Based-Security.pdf)

[https://www.blackhat.com/docs/us-16/materials/us-16-Wojtczuk-Analysis-Of-The-Attack-Surface-Of-Windows-10-Virtualization-Based-Security-wp.pdf](https://www.blackhat.com/docs/us-16/materials/us-16-Wojtczuk-Analysis-Of-The-Attack-Surface-Of-Windows-10-Virtualization-Based-Security-wp.pdf)

[https://www.youtube.com/watch?v=_646Gmr_uo0](https://www.youtube.com/watch?v=_646Gmr_uo0)

本文中，我们将涵盖系统引导过程，从Windows bootloader到VTL0启动。为了分析VBS怎么在引导过程期间初始化自身，下面的Windows 10 1607的一些文件已经被逆向过了：

Bootmgr.efi：EFI引导加载器（一小部分）

Winload.efi：EFI Windows加载器

Hvix.exe：Hyper-V（相当小的一部分）

Ntoskrnl.exe：NTOS内核

Securekernel.exe：安全内核

Ci.dll：VTL0代码完整性

Skci.dll：VTL1代码完整性

因此让我们来深入到VBS引导过程中，从winload.efi的执行开始，到ntoskrnl.exe的入口点执行。

**<br>**

**0x02 引导过程**



引导过程可以总结为5个必须的步骤：

Bootmgr.efi是第一个加载的组件。由SecureBoot验证并执行

Bootmgr.efi加载并校验winload.efi

Winload加载并校验VBS配置

Winload加载并校验Hyper-V和VTL0/VTL1内核组件

Winload退出EFI模式，启动Hyper-V

**Bootmgr.efi**

当系统开始引导，bootmgr.efi是第一个被加载执行的。它的完整性和签名已经由Secure Boot UEFI代码校验过。为了能够识别过期的签名，DBX数据库包含了过期的签名（截至2016年底，这个数据库包含了71个黑名单和未知的SHA256的哈希值）。在bootmgr.efi的最后，执行将转到winload.efi的入口点：OslpMain/OslMain。

OslpMain首先调用OslpPrepareTarget，其是winload.efi的核心函数。它将初始化hypervisor，内核等。但是先会使用OslSetVsmPolicy初始化VBS配置。

**VBS****策略加载**

OslSetVsmPolicy首先校验VbsPolicyDisabled EFI变量的值（参见下面的微软命名空间）。如果设置了，这个变量是0，意味着没有凭据保护配置将要加载。这个EFI变量因此将在引导时禁用凭据保护（并且能够在VTL0 ring3调用设置权限）。如果没有设置，配置将从SYSTEM注册表的hive中加载，并且由BlVsmSetSystemPolicy调用执行，其将读取和更新VbsPolicy EFI 变量。相应的值被存储到全局变量BlVsmpSystemPolicy中。如果UEFI锁开启，这个EFI变量被设置，并且不能通过winload.efi禁用（它不能移除它，只能使用自定义的EFI代码才能）。

函数OslpPrepareTarget也会调用OslpProcessSIPolicy（被调用两次，第一次直接从函数OslInitializeCodeIntegrity中调用）。OslpProcessSIPolicy使用3个EFI变量“pools”来校验SI策略签名。每个pool包含3个EFI变量，第一个包含策略，第二个包含版本，第三个包含授权的策略更新签名者。例如，对于C:WindowsSystem32CodeIntegritySIPolicy.p7b，变量是Si，SiPolicyVersion和SiPolicyUpdateSigners。如果“version”和“update signers”变量被设置，系统将增强SI策略签名：它必须是存在且正确的签名，否则引导将失败。通过BlSiPolicyIsSignedPolicyRequired函数来验证它自己。

3种策略和相关的变量总结如下：

[![](https://p5.ssl.qhimg.com/t01a8764c732db475b1.png)](https://p5.ssl.qhimg.com/t01a8764c732db475b1.png)

我们不确定“revokeSiPolicy”和“skuPolicy”的目的，但是他们似乎和普通的“SiPolicy”使用类似。

**Hyper-V****和内核组件的加载**

执行将转移到OslArchHypervisorSetup函数，其需要使用与执行的步骤相应的参数来调用，从0开始。在第一次，它将初始化Hyper-V（加载hvloader.efi且通过HvlpLaunchHvLoader执行它）。SecureBoot设置通过OslInitializeCodeIntegrity来校验。

OslpPrepareTarget然后加载NTOS内核（ntoskrnl.exe），并且使用OslpLoadAllModules函数来加载hal.dll和mcupdate.dll模块。然后“Local Key”和“Identification Key”由OslVsmProvisionLKey和OslVsmProvisionIdk函数加载。

此时，NTOS内核初始化了但还没哟启动。以步骤“0”为参数的OslVsmSetup被调用（与OslArchHypervisorSetup一样：以“步骤”为参数），首先校验Hyper-V已经启动，然后初始化OslVsmLoaderBlock（参数在初始化期间由安全内核提供）。然后，OslVsmSetup加载安全内核（securekernel.exe），并且通过OslpVsmLoadModules函数加载它依赖的skci.dll（OslLoadImage再次被用来校验他们的签名）。EFI变量OslLoaderIndications第一位被设置为1。

最后，OslVsmSetup函数再次被调用，但是参数是步骤“1”。这个触发了OslVsmLoaderBlock的初始化。

当函数OslpPrepareTarget返回后，VBS参数已经被验证完了，并且NTOS和安全内核都被加载了。他们的入口点地址被存储在全局变量OslpVsmSystemStartup和OslEntryPoint中（securekernel.exe和ntoskrnl.exe）以便将来使用。

<br>

**0x03 微软EFI变量**



VBS EFI变量属于命名空间：`{`0x77FA9ABD, 0x0359, 0x4D32, 0xBD, 0x60, 0x28, 0xF4, 0xE7, 0x8F, 0x78, 0x4B`}`。这些变量有他们的“Boot”和“Setup”属性设置，因此在EFI引导阶段后他们的访问和修改是不被允许的。

然而转储他们是可能的，以便在逆向分析中使用。与VBS相关的EFI变量和他们响应的用法总结如下：

[![](https://p2.ssl.qhimg.com/t01444635085e3b5cb7.png)](https://p2.ssl.qhimg.com/t01444635085e3b5cb7.png)

为了转储这些变量的内容，关闭安全启动和使用一个简单的EFI自定义的引导启动器（gnu-efi和VisualStudio能完美实现）。一些变量转储如下：

[![](https://p2.ssl.qhimg.com/t01de994b14c9469dbc.png)](https://p2.ssl.qhimg.com/t01de994b14c9469dbc.png)

**<br>**

**0x04 Hyper-V和安全内核启动**



回到OslpPrepareTarget，现在开始执行启动Hyper-V和分割VTL0及VTL1空间。这个过程总结如下：

Winload在“第一个“Hyper-V VM中运行

Winload调用安全内核的入口点（EP）

securekernel初始化自身，请求Hyper-V内存保护

securekernel请求VTL1验证

Hyper-V启用VTL1（“第二个“VM），在ShvlpVtlEntry中返回

通过ShvlpVtlReturn，securekernel（现在是VTL1）返回到winload（现在是VTL0）

Winload调用ntoskrnl入口点

下面是securekernel初始化前后的状态（VTL0 VM是蓝色块，VTL1是绿色块，Hyper-V是橙色块）：

[![](https://p0.ssl.qhimg.com/t0167972713d51f771e.png)](https://p0.ssl.qhimg.com/t0167972713d51f771e.png)

图2 – securekernel初始化前后的状态对比

继续执行，通过调用OslFwpKernelSetupPhase1退出EFI模式，并且以“1“参数调用OslArchHypervisorSetup启动Hyper-V。Hvix64通过向HvlpSavedRsp保存的RSP启动并且将HvlReturnFromHypervisor传给hvix64。当HvlpReturnFromHypervisor被命中，使用cpuid指令来验证启动，并且RSP被重置。我们确实处在第一个虚拟机中，其将很快变成VTL1。

OslVsmSetup再次被调用（step“2”）：

校验VBS参数

验证Hyper-V正确运行

修改OslVsmLoaderBlock设置

在相同块中复制OslVsmLKeyArray（Local Key）和OslVsmIdk（“Identification Key”）

调用储存在OslpVsmSystemStartup中的安全内核的入口点，指定OslVsmLoaderBlock和它的大小为参数。

然后安全内核将执行它的初始化，并且将调用SkmiProtectSecureKernelPages以便安装它自己的内存，但是也注册Hyper-V时间拦截例程（HyperGuard和它的Skpg*前缀的例程）。根据[http://www.sandpile.org/x86/msr.htm](http://www.sandpile.org/x86/msr.htm)，对MSR的操作由SkpgxInterceptMsr拦截处理：

**0x1B(APIC_BASE)**

**0x1004(?)**

**0x1005(?)**

**0x1006(?)**

**0x100C(?)**

**0xC0000080(EFER)**

**0xC0000081(STAR)**

**0xC0000082(LSTAR)**

**0xC0000083(CSTAR)**

**0xC0000084(FMASK)**

**0xC0000103(TSC_AUX)**

**0x174(SEP_SEL)**

**0x175(SEP_RSP)**

**0x176(SEP_RIP)**

**0x1a0(MISC_ENABLE)**

我们的假设是这个处理器的设置是为了捕获VTL0中CPL转变，来阻止关键的MSR修改。还有两个其他的例程，SkpgxInterceptRegisters和SkpgInterceptRepHypercall。前者可能是拦截CRXXX注册操作的方法（例如，写CR4能禁用SMEP），后者是拦截未授权的调用（然而这些只是猜测）。

关于HyperGuard，似乎通过SkpgVerifyExtents执行VTL0完整性校验。SkpgHyperguardRuntime被调用，可能是计划执行的（使用SkpgSetTimer）。

HyperGuard处理器和回调函数被复制到SkpgContext（由SkpgAllocateContext和SkpgInitializeContext初始化）。

记住上个章节只是个假设，可能是错误的，因为我们现在没能在VTL1 HyperGuard/PatchGuard例程中花费太多时间。

在初始化的最后，安全内核将执行两个调用：

0x0F，ShvlEnableVpVtl，指定一个ShvlpVtl1Entry函数指针

0x12，ShvlpVtlCall，它不会在任何其他地方使用，并且使用它自己的跳板函数（在下篇文章给出更多细节）。

ShvlpVtl1Entry以SkpPrepareForReturnToNormalMode结束，并且这个过程会使Hyper-V开启VTL0和VTL1，回到ShvlpVtl1Entry，再回到winload.efi进入到VTL0的上下文。

最终，当回到winload.efi的主函数，将通过OslArchTransferToKernel执行NTOS的入口点,它使用OslEntryPoint调用入口点。

然后执行下一个操作，就像Windows在正常环境中启动，只是现在NTOS内核知道了VBS相关的组件（如设备保护）。

<br>

**0x05 总结**



基于虚拟化的安全是Windows10安全功能的一个关键组件。通过VBS的安全内核的初始化，我们希望这个文章将给想要深入分析这个功能的逆向者帮助。

在第二部分，我们将涵盖VTL0和VTL1怎么内核通信和Hyper-V调用怎么实现。


