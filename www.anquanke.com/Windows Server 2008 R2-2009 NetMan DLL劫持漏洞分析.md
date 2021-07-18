
# Windows Server 2008 R2-2009 NetMan DLL劫持漏洞分析


                                阅读量   
                                **418912**
                            
                        |
                        
                                                                                                                                    ![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者github，文章来源：itm4n.github.io
                                <br>原文地址：[https://itm4n.github.io/windows-server-netman-dll-hijacking/](https://itm4n.github.io/windows-server-netman-dll-hijacking/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/202803/t01f82e6d03f12d215f.jpg)](./img/202803/t01f82e6d03f12d215f.jpg)



## 0x00 前言

2008 R2到2009的所有Windows Server系统都存在`%PATH%`目录DLL劫持问题，受影响的服务以`NT AUTHORITY\SYSTEM`权限运行，普通用户能跟根据需要决定是否触发DLL加载操作，并且不需要主机重启。由于某些`%PATH%`目录的权限较为脆弱，因此这可能是实现权限提升最直接的一种方法。目前似乎没有公开资料介绍过这一点，我将在本文中与大家分享我的发现。

这里必须澄清一点：[微软](https://msrc-blog.microsoft.com/2018/04/04/triaging-a-dll-planting-vulnerability/)并没有将这种DLL劫持行为当成漏洞，我也比较同意这个观点。因为在默认情况下，即使运行在高权限下的某个进程会从`%PATH%`目录中加载DLL，这种行为也无法被普通用户利用。然而在实际环境（特别是企业环境）中，我们经常能够看到有些第三方应用使用了较为脆弱的文件夹权限。此外，如果这些应用将自身添加到系统的`%PATH%`中，那么整个系统就会存在安全风险。关于这一点，我个人建议微软应当尽可能阻止这种不可控的DLL加载行为，避免单个应用存在的小配置错误演化成影响这个系统的权限提升问题。



## 0x01 使用Procmon搜索DLL劫持

我在某次研究Windows 2008 R2系统时发现了这种行为，虽然该系统已不再受官方支持，但仍然在企业网络中广泛使用，并且我也在寻找一种最简单的方法，来利用我之前发现的[CVE-2020-0668](https://itm4n.github.io/cve-2020-0668-windows-service-tracing-eop/)漏洞。在过去几个月内，我在Windows 10工作站上花了不少时间研究，因此刚回到Windows 7/2008 R2时有点不习惯，忘记了之前掌握的知识，只能从头开始。最开始我的问题是：如何能在Windows 2008 R2上来轻松利用任意文件写入原语。

我最初的想法是从`IKEEXT`服务开始着手。在默认安装的Windows 2008 R2系统上，这个服务处于停止状态，并且该服务在启动时会尝试加载不存在的一个`wlbsctrl.dll`库。正常用户可以尝试发起虚拟VPN连接，就能够轻松触发该服务。然而，启动该服务只会对其启动模式造成一次影响，随后启动模式会从`DEMAND_START`变成`AUTOMATIC`。在这种情况下，利用该服务需要重启主机，导致这个服务利用价值不是特别大，因此我必须寻找其他方法。我注意到研究员Frédéric Bourla在一篇[文章](https://www.reddit.com/r/hacking/comments/b0lr05/a_few_binary_plating_0days_for_windows/)中介绍了另一些DLL劫持方法，但这些方法要么不容易触发，要么利用过程有点随机性。

我决定使用Process Monitor开始研究，检查返回`NAME NOT FOUND`错误的DLL加载事件。在利用任意文件写入的上下文中，我们并不需要局限于`%PATH%`目录，因此我们能找到许多结果。为了进一步研究，我添加了一个约束条件。我想过滤掉尝试从`C:\Windows\System32\`目录加载不存在的DLL的进程，然而又从其他目录中找到了该DLL，以避免出现拒绝服务现象（特别是如果这种DLL是进程必须的库，那更可能出现这种情况）。

我考虑到了3种DLL劫持场景：

1、程序尝试从`C:\Windows\System32\`种加载不存在的一个DLL，但该DLL存在于另一个Windows目录中（比如`C:\Windows\System\`）。由于`C:\Windows\System32\`目录的权限更高，因此是一个潜在的目标。

2、程序尝试加载不存在的一个DLL，但使用了安全的DLL搜索顺序。比如，该程序只会尝试从`C:\Windows\System32\`目录种加载DLL。

3、程序尝试加载不存在的一个DLL，并且使用了不受限制的DLL搜索顺序。

第一种场景可能会导致拒绝服务，所以我暂不考虑。第二种场景比较有趣，但想在Procmon返回的大量结果中准确梳理还是有点困难。第三种场景无疑是最有趣的一种。一旦DLL不存在，劫持DLL时就不大可能发生拒绝服务，并且在Procmon种也很容易发现。

为了完成该任务，我并没有在Process Monitor中添加一个新的过滤器，而是简单添加一条规则，高亮出包含`WindowsPowerShell`的所有路径。为什么使用这个路径呢？在所有版本的（现代）Windows系统中，`C:\Windows\System32\WindowsPowerShell\v1.0\`目录默认情况下位于`%PATH%`中。因此，当我们看到有程序尝试从该目录加载DLL时，可能意味着该程序存在DLL劫持风险。

随后，我尝试启动/停止每个服务或者计划任务，在花了几个小时观察Procmon的输出结果后，我找到了如下信息：

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0111c496dce7c0838f.png)

简直不敢相信，我竟然看到以`NT AUTHORITY\SYSTEM`权限运行的某个服务会加载不存在的一个DLL。我的第一个想法是：如果`wlanhlp.dll`是能被劫持的DLL，那么应该已经有一些公开资料，这里肯定是我犯了一些错误，或者我安装了某些第三方应用导致出现这种情况。然而我使用的是全新安装的Windows Server 2008 R2系统，使用的是专用的虚拟机，唯一一个第三方应用为“VMware Tools”。此外，目前我做的所有研究主要基于工作站版本的Windows，因为这种系统通常更为方便，那这是不是我看到这种事件的原因所在呢？

幸运的是，我也安装了一个Windows 7虚拟机，因此我快速检查了一遍。经过测试后，我发现这个DLL存在于工作站系统中。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019a1507e6edf16163.png)

正如大家所想，`wlanhlp.dll`的确与Wlan功能有关。Wlan API默认情况下只在工作站版本上可用，在Server版本上必须以其他组件形式安装。无论如何，这里我得研究一下。



## 0x02 NetMan及Wlan API

我们先在Procmon中看一下事件属性，了解关于该服务的更多细节。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015268ca33077903fd.png)

该进程以`NT AUTHORITY\SYSTEM`权限运行，这一点对我们而言是一个好消息。进程PID为`972`，因此我们在任务管理器中检查一下对应的服务。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01050cc40f5679b787.png)

该进程中运行着3个服务。在Procmon中看一下事件的调用栈信息，我们应该能够确定尝试加载这个DLL的对象。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ca317f14fbf2a940.png)

其中我们可以看到`netman.dll`的身影，因此对应的服务肯定为`NetMan`（即Network Connections，网络连接）。现在我们已经解决了其中一个疑问。如果我们仔细观察调用栈，还可以注意到其中有多处引用到了`RPCRT4.dll`或者`ole32.dll`。这是一个好兆头，意味着该事件很有可能通过RPC/COM来触发。如果的确是这种情况，我们就有机会通过几行代码，以普通用户身份触发该事件，但我想进一步研究一下。

之所以会出现DLL劫持，原因在于Wlan API默认情况下并没有安装在Server版的Windows 6.1上（即Windows 7/2008 R2）。那么问题在于：这种情况是否适用于其他版本的Windows呢？

幸运的是，我手头上有大量虚拟机，其中就包含Server 2012 R2以及2019，因此测试起来也非常方便。

在Windows Server 2012 R2上，Procmon中并没有发现`wlanhlp.dll`，然而却出现了`wlanapi.dll`。查看该事件的详细信息，我们发现情况完全一致。这意味着Windows 6.3（8.1/2012 R2）上同样存在这种现象。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01400ccd555999e6ac.png)

大家可能觉得这个Windows系统版本有点老，Windows 2019肯定不会存在该问题。我们来测试一下：

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011a9f36b51aecd5cd.png)

Windows Server 2019上同样能看到这种行为。最后我测试了2008到2019之间所有版本的Windows Server系统，得出的结论是所有版本都存在这种DLL劫持问题。唯一的例外是Server 2008，我没办法在该系统上复现该问题。



## 0x03 如何触发DLL劫持事件

稍微总结一下现有信息。在所有版本的Windows Server上，`NetMan`服务运行在`NT AUTHORITY\SYSTEM`上下文中，并且会尝试加载不存在的`wlanhlp.dll`或者`wlanapi.dll`，同时不使用安全的DLL搜索顺序。因此，该服务最后会尝试从系统的`%PATH%`环境变量所指向的目录中加载这个DLL。这个行为对我们而言非常理想。

下面我们要澄清是否能以普通用户身份触发该事件。虽然我已解释过这种行为是因为某些RPC/COM事件，但并不意味着我们能触发该行为。也有可能是因为两个服务彼此间通过RPC进行通信才触发该事件。

无论如何，我们总要怀抱希望，再次检查一下调用栈。这一次我们在使用Procmon时，可以配合使用微软提供的公共符号。为了完成该任务，我切换到日常用于安全研究的Windows 10虚拟机。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011a8e02bc41fa4e18.png)

可以看到这里调用了`CLanConnection::GetProperties()`，而在其他事件中调用的是`CLanConnection::GetPropertiesEx()`。我们来使用[OleViewDotNet](https://github.com/tyranid/oleviewdotnet)，检查`NetMan`公开的COM对象，看能否找到这些方法。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eb8f2c30f5186735.png)

根据类的名称，看上去`LAN Connection Class`似乎是不错的研究目标。因此我创建了该类的一个实例，详细检查`INetConnection`接口。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016c4870e76e3fcca1.png)

找到了！我们看到了`CLanConnection::GetProperties()`方法，我们离目标已经更进一步。

此时我认为进展非常顺利。首先，我看到之前未见过的DLL劫持行为；然后，我发现该行为可以通过RPC/COM事件触发；最后，我发现使用OleViewDotNet我们很容易就能找到相关方法。我们必须抓住这个机会，但现在我们可能会遇到一个问题：COM对象上的限制性权限。

COM对象同样也有安全概念，并且这些对象也包含ACL，定义了谁能够使用这些对象。因此，在继续研究前，我们需要检查这些信息。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011e063c0a95a32886.png)

首先我看到了`Administrators`以及`NT AUTHORITY\...`，这很正常，因为我觉得只有高权限账户能触发该行为，然后我就看到了`NT AUTHORITY\INTERACTIVE`。

这一点意味着，只有当普通用户使用交互式会话进行身份认证时，才可以使用这个COM对象。更具体一点，我们需要本地登录到系统。听上去是不是比较鸡肋？然而事实证明，当我们通过RDP（包括VDI）进行连接时，我们也能获得交互式会话。因此在这种情况下，普通用户就可以使用这个COM对象。如果不满足这些条件，比如如果我们尝试在WinRM会话中使用该对象，就会看到一个“访问被拒绝”的错误。这种情况并没有达到我最初的预期，但看上去依然是一个不错的触发条件。

我们可以在Windows Server 2019的RDP会话中打开一个命令提示符，如下图所示：

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010b0ceb3b0dc6c607.png)

此时整个研究内容已经结束，现在可以开始写代码。幸运的是，官方[公开](https://docs.microsoft.com/en-us/windows/win32/api/netcon/nn-netcon-inetconnection)了`INetConnection`接口，这能大大减轻我们的工作量。其次，在搜索如何使用`INetConnection-&gt;EnumConnections()`来枚举网络接口时，我偶然发现了[Simon Mourier](https://stackoverflow.com/users/403671/simon-mourier)在[StackOverflow](https://stackoverflow.com/questions/5917304/how-do-i-detect-a-disabled-network-interface-connection-from-a-windows-applicati/5942359#5942359)上提供的一个有趣的解决方案，因此我从StackOverflow上复制了一些代码。

最终我们的PoC代码如下：

```
// https://stackoverflow.com/questions/5917304/how-do-i-detect-a-disabled-network-interface-connection-from-a-windows-applicati/5942359#5942359

#include &lt;iostream&gt;
#include &lt;comdef.h&gt;
#include &lt;netcon.h&gt;

int main()
{
    HRESULT hResult;

    typedef void(__stdcall* LPNcFreeNetconProperties)(NETCON_PROPERTIES* pProps);
    HMODULE hModule = LoadLibrary(L"netshell.dll");
    if (hModule == NULL) { return 1; }
    LPNcFreeNetconProperties NcFreeNetconProperties = (LPNcFreeNetconProperties)GetProcAddress(hModule, "NcFreeNetconProperties");

    hResult = CoInitializeEx(0, COINIT_MULTITHREADED);
    if (SUCCEEDED(hResult))
    {
        INetConnectionManager* pConnectionManager = 0;
        HRESULT hResult = CoCreateInstance(CLSID_ConnectionManager, 0, CLSCTX_ALL, __uuidof(INetConnectionManager), (void**)&amp;pConnectionManager);
        if (SUCCEEDED(hResult))
        {
            IEnumNetConnection* pEnumConnection = 0;
            hResult = pConnectionManager-&gt;EnumConnections(NCME_DEFAULT, &amp;pEnumConnection);
            if (SUCCEEDED(hResult))
            {
                INetConnection* pConnection = 0;
                ULONG count;
                while (pEnumConnection-&gt;Next(1, &amp;pConnection, &amp;count) == S_OK)
                {
                    NETCON_PROPERTIES* pConnectionProperties = 0;
                    hResult = pConnection-&gt;GetProperties(&amp;pConnectionProperties);
                    if (SUCCEEDED(hResult))
                    {
                        wprintf(L"Interface: %ls\n", pConnectionProperties-&gt;pszwName);
                        NcFreeNetconProperties(pConnectionProperties);
                    }
                    else
                    {
                        wprintf(L"[-] INetConnection::GetProperties() failed. Error code = 0x%08X (%ls)\n", hResult, _com_error(hResult).ErrorMessage());
                    }
                    pConnection-&gt;Release();
                }
                pEnumConnection-&gt;Release();
            }
            else
            {
                wprintf(L"[-] IEnumNetConnection::EnumConnections() failed. Error code = 0x%08X (%ls)\n", hResult, _com_error(hResult).ErrorMessage());
            }
            pConnectionManager-&gt;Release();
        }
        else
        {
            wprintf(L"[-] CoCreateInstance() failed. Error code = 0x%08X (%ls)\n", hResult, _com_error(hResult).ErrorMessage());
        }
        CoUninitialize();
    }
    else
    {
        wprintf(L"[-] CoInitializeEx() failed. Error code = 0x%08X (%ls)\n", hResult, _com_error(hResult).ErrorMessage());
    }
    wprintf(L"Done\n");
}
```

下图显示了在Windows Server 2008 R2上的运行结果。可以看到，我们只要简单枚举主机上的Ethernet接口，就能触发DLL加载行为。在利用这种技术时，主机上必须至少具备一个Ethernet接口。

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0194b92cc9b13ab619.png)

如果我们在Windows Server 2019上，以普通用户身份通过远程PowerShell会话来运行该程序时，结果如下所示：

[![](./img/202803/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01af4729295d1ce11e.png)



## 0x04 总结

根据此次研究，我认为`NetMan`服务可能是目前我了解的DLL劫持攻击最理想的目标。作为普通用户，我们需要一个交互式会话（RDP/VID），因此如果我们通过远程PowerShell会话登录，那这种方法将无法派上用场。然而还有比较有趣的其他情况，如果我们拿下了以`LOCAL SERVICE`或者`NETWORK SERVICE`运行的其他服务，那么仍然可以触发NetMan服务，将权限提升至`SYSTEM`。

此次研究中我也获得了一些经验，如果将注意力和精力集中在特定的环境中，有时候可能会阻止我们找到有趣的信息。这个经验在渗透测试中非常重要。

最后顺便提一句，我在[PrivescCheck](https://github.com/itm4n/PrivescCheck)（Windows权限提升检查脚本）中集成了这种技术。根据具体的Windows版本，我们能够通过`Invoke-HijackableDllsCheck`函数了解可能通过`%PATH%`目录劫持的DLL，这里还要感谢<a>@1mm0rt41</a>提供的建议。



## 0x05 参考资料
<li>Microsoft Security Response Center (MSRC) – Triaging a DLL planting vulnerability<br>[https://msrc-blog.microsoft.com/2018/04/04/triaging-a-dll-planting-vulnerability/](https://msrc-blog.microsoft.com/2018/04/04/triaging-a-dll-planting-vulnerability/)
</li>
<li>CVE-2020-0668 – A Trivial Privilege Escalation Bug in Windows Service Tracing<br>[https://itm4n.github.io/cve-2020-0668-windows-service-tracing-eop/](https://itm4n.github.io/cve-2020-0668-windows-service-tracing-eop/)
</li>
<li>A few binary planting 0-days for Windows<br>[https://www.reddit.com/r/hacking/comments/b0lr05/a_few_binary_plating_0days_for_windows/](https://www.reddit.com/r/hacking/comments/b0lr05/a_few_binary_plating_0days_for_windows/)
</li>