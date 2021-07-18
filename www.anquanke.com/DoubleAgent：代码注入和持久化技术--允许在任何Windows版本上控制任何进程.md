
# DoubleAgent：代码注入和持久化技术--允许在任何Windows版本上控制任何进程


                                阅读量   
                                **131464**
                            
                        |
                        
                                                                                                                                    ![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：cybellum.com
                                <br>原文地址：[https://cybellum.com/doubleagentzero-day-code-injection-and-persistence-technique/](https://cybellum.com/doubleagentzero-day-code-injection-and-persistence-technique/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85775/t01f0962d690d28c9fd.jpg)](./img/85775/t01f0962d690d28c9fd.jpg)**

****

翻译：[pwn_361](http://bobao.360.cn/member/contribute?uid=2798962642)

稿费：260RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、概述**

我们想介绍一种新的用于代码注入和保持对机器持久化控制的0-day技术，叫做“DoubleAgent”。

DoubleAgent技术可以利用到：

1.任何Windows版本(从XP到WIN 10)。

2.任何Windows架构(X86和X64)。

3.任何Windows用户(系统/管理员等)的任何目标进程，包括特权进程(操作系统/杀毒软件等)。

DoubleAgent技术利用了在Windows中已经存在15年的一个未公开但合法的功能，因此还不能被修补。

**代码注入：**

利用DoubleAgent技术，攻击者有能力将任何DLL注入到任何进程中。在受害者的进程启动过程中，该代码注入过程发生在很早的阶段，这使得攻击者可以完全控制该进程，该进程无法有效的保护好自己。

该代码注入技术是具有革命性的，因为任何杀毒软件都无法探测或阻止它。

**持久化：**

即使在用户重新启动系统或安装修补程序和更新后，DoubleAgent技术还是可以断续注入代码，这使它成为了一个完美的持久化技术。

一旦攻击者决定将一个DLL注入到一个进程中，它们将永远被强制绑定。即使受害者完全卸载和重新安装了它的应用程序，攻击者的DLL仍然会在该进程每次重启时被注入。

**<br>**

**二、攻击向量**

1、攻击反病毒软件&amp;下一代反病毒软件：通过将代码注入到反病毒软件中，完全控制任何反病毒软件，同时绕过其自我保护机制。这种攻击方法在大部分反病毒软件中已经被证实有效，包括下面的反病毒产品，但不限于这些：Avast，AVG，Avira，Bitdefender，Comodo，ESET，F-Secure，Kaspersky，Malwarebytes，McAfee，Norton，Panda，Quick Heal和Trend Micro。

2、安装持久化恶意软件：安装恶意软件，即使是重启系统也能“存活”的恶意软件。

3、劫持权限：劫持一个现有信任进程的权限，伪装成信任进程执行一些恶意操作，如窃取数据、C2通信、横向运动、偷取和解密敏感数据。

4、改变进程行为：修改进程行为，如安装后门、降低加密算法，等等。

5、攻击其他用户会话：将代码注入到其他用户会话的进程中(系统、管理员等等)。

6、更多其它情况。

<br>

**三、技术详情**

**1.微软应用验证器提供者**

微软通过[微软应用程序验证器](https://msdn.microsoft.com/en-us/library/ms220948(v=vs.90).aspx)提供者DLL，提供了一个标准的方法，用于为本机代码安装运行时验证工具。验证器提供者DLL是一个DLL，会被加载到进程中，并负责为应用程序执行运行时验证。

为了注册一个新的应用程序验证器提供者DLL，需要创建一个验证器提供者DLL，并通过在注册表中创建一组键值来注册它。

一旦将该DLL注册为某个进程的验证器提供者DLL，在每次启动该进程时，该DLL将被Windows加载者长期注入到这个进程中，即使是在重启/更新/重装/打补丁之后，也同样有效。

**2.注册**

应用程序验证器提供者会被注册为一个可执行文件名，意味着每个DLL会绑定到一个特定的可执行文件名上，并且带有该注册名的进程在每一次启动新进程时，该DLL就会被注入到该进程中。

例如，如果将DoubleAgentDll.dll注册到cmd.exe上，当启动“C:-cmd.exe”和“C:-Windows-System32-cmd.exe” 时，DoubleAgentDll.dll就会被注入到这两个进程中。

一旦被注册，每次使用该注册名称创建新进程时，操作系统就会自动进行注入。该注入将会持续发生，不论重启/更新/重装/补丁，或其它任何情况。

可以通过使用我们公开的[DoubleAgent](https://github.com/Cybellum/DoubleAgent)项目，注册一个新的应用程序验证器提供者。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018b55430afd95e6f8.png)

或者使用我们的[验证模块](https://github.com/Cybellum/DoubleAgent/blob/master/DoubleAgent/Verifier.h)，将注册能力整合到一个存在的项目中。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0114fe23640549bf6b.png)

在底层，注册进程将会在下面的注册表项中创建两个注册表键值：

```
“HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsNTCurrentVersionImage File Execution OptionsPROCESS_NAME”
```

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019d95eec4e0005986.png)

最终的结果应该是：

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ed70558336bb7f9e.png)

一些反病毒软件会尝试保护“Image File Execution Options”中它们的进程对应的键值。如一款反病毒软件可能会尝试阻止任何对“Image File Execution OptionsANTIVIRUS_NAME”的访问。

对于这种简单的保护机制，通过稍微修改一下注册表路径，就可以轻松的绕过去。如，我们不需要访问“Image File Execution OptionsANTIVIRUS_NAME”，我们首先可以对“Image File Execution Options”重新命名成一个临时的名称，如“Image File Execution Options Temp”，然后，在“Image File Execution Options TempANTIVIRUS_NAME”下，创建一个新的注册表键值，最后，再将这个临时名称重命名成原来的名称“Image File Execution Options”。

因为我们创建的新注册表键值是在“Image File Execution Options TempANTIVIRUS_NAME”下，不是在“Image File Execution OptionsANTIVIRUS_NAME”下，因此，这足以绕过反病毒软件的自我保护机制。

在我们测试的所有反病毒软件中，只有个别几款反病毒软件会尝试保护它们的注册表键值，不过，我们使用“重命名技巧”可以绕过所有的反病毒软件。

这个“重命名技巧”已经运用到了我们的[验证模块](https://github.com/Cybellum/DoubleAgent/blob/master/DoubleAgent/Verifier.h)中。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e8deb880e9a18cb4.png)

**3.注入**

每一个进程启动时，操作系统会通过调用ntdll的LdrInitializeThunk函数，将控制权从内核模式转向用户模式。从这一刻起，ntdll开始负责该进程的初始化过程(初始化全局变量、加载输入、等)，并且最终将控制权转到该执行程序的主函数。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01663be457b10352b2.png)

在该进程处于一个早期阶段时，此时，只加载了ntdll.dll模块和该可执行文件(NS.EXE)。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010ad34de3da3432a8.png)

随后，Ntdll开始对该进程进行初始化，大部分初始化过程发生在ntdll的LdrpInitializeProcess函数过程中。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018bc51b734a9d09cb.png)

通常，初始化过程中，第一个被加载的DLL是[kernel32.dll](https://en.wikipedia.org/wiki/Microsoft_Windows_library_files#KERNEL32.DLL)。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0161df47cd22994581.png)

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d1045d17af69f47e.png)

但是如果存在应用程序验证器，ntdll的LdrpInitializeProcess函数会调用AVrfInitializeVerifier函数，调用该函数的结果是：在加载kernel32前，我们的[验证器提供者DLL](https://github.com/Cybellum/DoubleAgent/tree/master/DoubleAgentDll)会首先被加载。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0166dde890cfcda66a.png)

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018500bc0ccedb7e46.png)

该DLL在任何其它系统DLL加载前被加载，其结果就是：将该进程的绝对控制权交给了我们。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d57d66bf3658f39f.png)

一旦我们的DLL被ntdll加载，我们的DLLMain函数就会被调用，从而，在受害进程中，我们就可以自由的做我们想做的事情了。

[![](./img/85775/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d31363acf7c90196.png)

<br>

**四、如何缓解**

微软为杀毒厂商提供了全新的设计概念，叫做“受保护进程”。这个新概念是专门为反病毒服务设计的。反病毒进程可以作为“受保护进程”被创建，并且这个“受保护进程的基础设施”只允许那些受信任的、签名的代码去加载，并且内置了代码注入攻击防御功能。这意味着即使一个攻击者发现了一个新的零日代码注入技术，它也不能被用于对抗反病毒软件，因为它的代码没有被签名。但是，目前没有哪个反病毒软件应用了这种设计概念(除了微软的Defender)，尽管微软在3年前就已经推出了这个设计概念。

需要注意的重要一点是，即使反病毒厂商会阻止注册企图，代码注入技术和持久化技术还是会永远存在，因为它是操作系统的合法功能。

<br>

**五、源代码**

你可以在我们公司的公共[Github](https://github.com/Cybellum/DoubleAgent)上找到DoubleAgent技术的源代码。

<br>

**六、总结**

攻击者总是会不断进化、并发现新的零日攻击。我们需要付出更多的努力去探测和阻止这些攻击，并且不要盲目相信传统的安全解决方案，正如这里所演示的，它不仅对零日攻击无效，而且还为攻击者创造复杂和致命攻击打开了新的机会。
