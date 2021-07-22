> 原文链接: https://www.anquanke.com//post/id/152728 


# Edge与localhost网络隔离


                                阅读量   
                                **176652**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：tyranidslair.blogspot.com
                                <br>原文地址：[https://tyranidslair.blogspot.com/2018/07/uwp-localhost-network-isolation-and-edge.html](https://tyranidslair.blogspot.com/2018/07/uwp-localhost-network-isolation-and-edge.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01d06bf9aa96bcbb18.png)](https://p1.ssl.qhimg.com/t01d06bf9aa96bcbb18.png)

## 一、前言

本文介绍了Windows中新增的一个有趣的“功能”，该功能支持Edge浏览器访问本地环回（loopback）网络接口。本文已在Windows 10 1803（Edge 42.17134.1.0 ）以及Windows 10 RS5 17713（Edge 43.17713.1000.0 ）上验证通过。



## 二、具体分析

我非常喜欢微软从Windows 8开始引入的App Container（AC）沙盒概念。该机制将Windows上的沙盒环境从受限令牌（非常难以理解并需要耗费大量精力的东西）迁移到了一个基于功能（capability）的合理模型上，此时除非我们在应用启动时显式赋予了各种功能，否则就会受到种种限制。在Windows 8上，沙盒中只能访问已知的一小部分功能。在Windows 10上，受限范围已大大扩展，应用程序可以定义自己的功能，并且通过Windows访问控制机制来访问这些功能。

我一直在关注AC及其在网络隔离方面的能力，在AC中，若要访问网络，则需要赋予“internetClient”之类的功能。很少有人知道，即便处于非常受限的令牌沙盒中，我们也可以访问raw AFD驱动来打开网络套接字。AC已经非常顺利地解决了这个问题，它并没有阻止我们访问AFD驱动，而是让防火墙检查程序是否具备对应的功能，据此阻止连接请求或者接受套接字。

在构建通用沙盒机制的过程中，这种AC网络隔离原语会碰到一个问题，那就是无论我们赋予AC应用什么功能，它都无法访问localhost网络。比如，在测试过程中，我们可能希望沙盒应用能够访问托管在本地的一个web服务器，或者使用本地代理以MITM方式监听流量。这些场景都无法适用于只具备相应功能的AC沙盒。

之所以阻止沙盒访问localhost，很大程度上是因为潜在的安全风险问题。Windows在本地运行了许多服务（如SMB服务器），这些服务很容易被滥用。其实防火墙服务中存储了一个不受localhost限制的软件包列表，我们可以使用[防火墙API](https://docs.microsoft.com/en-gb/previous-versions/windows/desktop/ics/windows-firewall-with-advanced-security-functions)（如[NetworkIsolationSetAppContainerConfig](https://docs.microsoft.com/en-gb/previous-versions/windows/desktop/api/netfw/nf-netfw-networkisolationsetappcontainerconfig)函数）或者使用Windows中内置的`CheckNetIsolation`工具来访问或者修改这一列表。这种方式听起来比较合理，因为访问loopback接口是开发者会去尝试的选项，正常应用一般不会依赖这一点。我比较好奇的是这个豁免列表中是否已经存在一些AC，大家可以执行`CheckNetIsolation LoopbackExempt -s`命令列出本地系统中不受限制的那些AC。

[![](https://p5.ssl.qhimg.com/t012721930dd6a0d4f8.png)](https://p5.ssl.qhimg.com/t012721930dd6a0d4f8.png)

在我的Windows 10主机上，该列表中共有2个条目，应该没有应用会使用这种开发者功能，这一点比较奇怪。第一个条目的名称为`AppContainer NOT FOUND`，表示已注册的SID与已注册的AC不匹配。第二个条目的使用了看起来毫无意义的名称`001`，这至少表明这是当前系统上的一个应用程序。这究竟是怎么回事？我们可以使用我的[NtObjectManager](https://www.powershellgallery.com/packages/NtObjectManager) PS模块，根据对应的SID值，通过`Get-NtSid` cmdlet来分析`001`这个名字是否可以解析成更容易理解的名称。

[![](https://p4.ssl.qhimg.com/t01b14994f99ee5d8e0.png)](https://p4.ssl.qhimg.com/t01b14994f99ee5d8e0.png)

水落石出，`001`实际上是Edge的一个子AC，我们可以根据SID的长度来猜测。正常的AC SID具备8个子项，而子AC则具备12个子项（基础AC SID后附加4个子项）。回过头来看这个未注册的SID，我们可以发现它是一个Edge AC SID，并且带有尚未注册的子项。`001`这个AC貌似是用于托管Internet内容的AC（我们可以参考X41Sec关于浏览器安全[白皮书](https://github.com/x41sec/browser-security-whitepaper-2017/blob/master/X41-Browser-Security-White-Paper.pdf)的第54页来验证这一点)。

这一点并不奇怪。Edge刚发布时并不能访问localhost资源（比如，IBM在一份[帮助文档](https://www.ibm.com/support/knowledgecenter/en/SSPH29_9.0.3/com.ibm.help.common.infocenter.aps/r_LoopbackForEdge.html)中指导用户如何使用`CheckNetIsolation`来添加例外）。然而，在某个研发阶段中，微软添加了一个`about:flags`选项，允许Edge访问localhost资源，现在这个选项看起来已经变成默认配置，如下图所示（微软仍友情提示启用该选项可能使用户设备面临安全风险）：

[![](https://p4.ssl.qhimg.com/t011c5c2b7523039b1e.png)](https://p4.ssl.qhimg.com/t011c5c2b7523039b1e.png)

比较有趣的是，如果我们禁用这个选项并重启Edge，那么该例外条目就会自动被清除，而再次启用该选项又会自动恢复这个例外条目。为什么这一点比较有趣？这是因为根据以往的经验（比如Eric Lawrence写的这篇[文章](https://blogs.msdn.microsoft.com/fiddler/2011/12/10/revisiting-fiddler-and-win8-immersive-applications/)），我们需要[管理员权限](https://twitter.com/ericlaw)才能修改这个例外列表，也许微软现在修改了这个规则？我们可以验证这个猜测是否准确，使用`CheckNetIsolation`工具，传入`-a -p=SID`参数，具体命令如下：[![](https://p5.ssl.qhimg.com/t01b329c0fdc54727e8.png)](https://p5.ssl.qhimg.com/t01b329c0fdc54727e8.png)

因此，我猜测开发者并没有使用`CheckNetIsolation`工具来添加例外规则，现在这种情况真的让我很感兴趣。由于Edge是操作系统内置的应用，因此微软很有可能添加了一些“安全”检测机制，允许Edge将自己加入例外列表，但具体位置在哪呢？

最简单的一种方法就是利用实现了`NetworkIsolationSetAppContainerConfig`的RPC服务（我反汇编了这个API，因此知道有这样一个RPC服务）。我凭直觉猜测具体实现应该托管于“Windows Defender Firewall”服务中，该服务由MPSSVC DLL负责实现。如下代码为RPC服务器对该API的简化版实现代码：

```
HRESULT RPC_NetworkIsolationSetAppContainerConfig(handle_t handle, 
    DWORD dwNumPublicAppCs,
    PSID_AND_ATTRIBUTES appContainerSids) `{`

  if (!FwRpcAPIsIsPackageAccessGranted(handle)) `{`
    HRESULT hr;
    BOOL developer_mode = FALSE:
    IsDeveloperModeEnabled(&amp;developer_mode);
    if (developer_mode) `{`
      hr = FwRpcAPIsSecModeAccessCheckForClient(1, handle);
      if (FAILED(hr)) `{`
          return hr;
      `}`
    `}`
    else
    `{`
      hr = FwRpcAPIsSecModeAccessCheckForClient(2, handle);
      if (FAILED(hr)) `{`
          return hr;
      `}`
    `}`
  `}`
  return FwMoneisAppContainerSetConfig(dwNumPublicAppCs,
                                       appContainerSids);
`}`
```

如上所示，代码中有个`FwRpcAPIsIsPackageAccessGranted`函数，函数名中包含一个“Package”字符串，表示该函数可能会检查一些AC软件包信息。如果该函数调用成功，则会跳过代码中的安全检查过程，然后调用`FwMoneisAppContainerSetConfig`这个函数。需要注意的是，安全检查过程会根据是否处于开发者模式而有所不同，如果启用了开发者模式，我们还可以绕过管理员检查过程，根据这一点我们可以再次确认这种例外列表主要是为开发者而设计的一种特性。

接下来我们来看一下`FwRpcAPIsIsPackageAccessGranted`的具体实现：

```
const WCHAR* allowedPackageFamilies[] = `{`
  L"Microsoft.MicrosoftEdge_8wekyb3d8bbwe",
  L"Microsoft.MicrosoftEdgeBeta_8wekyb3d8bbwe",
  L"Microsoft.zMicrosoftEdge_8wekyb3d8bbwe"
`}`;

HRESULT FwRpcAPIsIsPackageAccessGranted(handle_t handle) `{`
  HANDLE token;
  FwRpcAPIsGetAccessTokenFromClientBinding(handle, &amp;token);

  WCHAR* package_id;
  RtlQueryPackageIdentity(token, &amp;package_id);
  WCHAR family_name[0x100];
  PackageFamilyNameFromFullName(package_id, family_name)

  for (int i = 0; 
       i &lt; _countof(allowedPackageFamilies); 
       ++i) `{`
      if (wcsicmp(family_name, 
           allowedPackageFamilies[i]) == 0) `{`
        return S_OK;
      `}`
  `}`
  return E_FAIL;
`}`
```

`FwRpcAPIsIsPackageAccessGranted`函数会获取调用者的token信息，查询软件包的Family Name，将该名称与硬编码的列表进行对比。如果调用者位于Edge包（或者某些beta版本）中，则返回成功，使上层函数跳过admin检查过程。这就能解释Edge如何将自己加入例外列表中，现在我们还需要知道需要哪些访问权限才能使用RPC服务器。对ALPC服务器来说存在两项安全检查，分别为连接到ALPC的端口以及一个可选的安全回调例程。我们可以选择逆向分析该服务所对应的二进制程序，但还可以选择更加简单的方法，从ALPC服务器端口进行转储，这一次我们还可以使用我的`NtObjectManager`模块。

[![](https://p0.ssl.qhimg.com/t015d0ef0e518131db9.png)](https://p0.ssl.qhimg.com/t015d0ef0e518131db9.png)

由于RPC服务并没有指定服务的名称，因此RPC库会生成一个随机的名称，格式为`LRPC-XXXXX`。我们通常可以使用`EPMAPPER`来寻找实际名称，但我在`CheckNetIsolation`的`NtAlpcConnectPort`上设置了断点，导出连接名。然后我们就可以在服务进程中找到ALPC端口的句柄，导出安全描述符。该列表中包含`Everyone`以及所有的网络相关功能，因此具备网络访问权限的任何AC进程都可以与这些API交互（包括Edge LPAC在内）。因此所有的Edge进程都可以访问这个功能，添加任意包。Edge中的具体实现位于`emodel!SetACLoopbackExemptions`函数中。

了解这些知识后，现在我们将代码汇总起来，利用这个“功能”来添加任意例外条目。大家可以访问我的[Github](https://gist.github.com/tyranid/dbf0c704c1602929936c21196c0d5079)来下载这个PowerShell脚本。

[![](https://p4.ssl.qhimg.com/t01b50c7f167ccc7921.png)](https://p4.ssl.qhimg.com/t01b50c7f167ccc7921.png)



## 三、总结

我猜测微软之所以采用这种方式来添加localhost访问权限，原因在于这样就不需要去修改内核驱动，只需要在用户模式组件上进行修改。但我有点愤愤不平，这样让Edge在地位上比其他浏览器有所不同。从道理上讲，即便封装了Edge，其他应用也不应该具备添加localhost例外的能力。如果微软能在未来添加相应的功能那再好不过，不过由于目前RS5仍然采用的是这种办法，我对此并不乐观。

这是不是一种安全问题呢？得具体情况具体分析。你可以认为在默认配置下能够访问localhost资源本身就是一种危险行为，但微软又在`about:flags`页面中明确给出了安全风险提示。另一方面所有的浏览器都支持这种功能，所以我也不确定这是不是真的属于安全风险。

具体的实现代码非常粗糙，我惊讶的是这种代码竟能够通过安全审查。这里我们可以列出存在的一些问题：

1、软件包的family检查过程不是特别严格，与RPC服务较弱的权限结合起来后，我们就可以让任意Edge进程具备添加例外的能力；

2、例外范围并没有与调用进程关联起来，因此任意SID都可以添加到例外中。

默认情况，只有面向Internet的AC才能够访问localhost，比如，如果我们攻破了Flash进程（为子AC “006”），那么就可以将自身加入例外列表中，进一步尝试攻击在localhost监听的服务。如果只有微软Edge进程而不是任何进程能够添加例外列表那就更好一些，但最好的还是通过正规的功能来支持这一特性，而不是通过后门的方式来实现，这样每个人都可以利用这一特性。
