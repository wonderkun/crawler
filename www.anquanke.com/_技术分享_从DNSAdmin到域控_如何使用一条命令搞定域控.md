> 原文链接: https://www.anquanke.com//post/id/86080 


# 【技术分享】从DNSAdmin到域控：如何使用一条命令搞定域控


                                阅读量   
                                **160991**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：medium.com/@esnesenon
                                <br>原文地址：[https://medium.com/@esnesenon/feature-not-bug-dnsadmin-to-dc-compromise-in-one-line-a0f779b8dc83](https://medium.com/@esnesenon/feature-not-bug-dnsadmin-to-dc-compromise-in-one-line-a0f779b8dc83)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p0.ssl.qhimg.com/t019e1458637899057f.jpg)](https://p0.ssl.qhimg.com/t019e1458637899057f.jpg)**

**一、前言**

微软自己有一套DNS服务器解决方案，同时也实现了自己的DNS管理协议，以便结合AD（Active Directory，活动目录）域实现一体化集成和管理。默认情况下，域控也是DNS服务器，在域中，每个域用户都应该能够访问和使用DNS服务器。这样一来，域控就会暴露出一些攻击面，比如DNS协议自身，以及基于RPC的管理协议都可以作为攻击对象。

在本文中，我们会深入研究这个协议的具体实现，并详细介绍一个可爱的功能（注意，这并不是一个bug）。在某些情况下，即使我们不是域管，我们也可以利用这个功能在域控上运行命令。虽然这个功能并不是一个安全漏洞（因此大家没必要恐慌），但正如微软所承认的那样，我们可以在红蓝对抗中使用这个技巧完成AD域提权。

本文所阐述的所有技术细节，主要来自于微软官方的协议规范（[MS-DNSP], [https://msdn.microsoft.com/en-us/library/cc448821.aspx](https://msdn.microsoft.com/en-us/library/cc448821.aspx) ），以及使用IDA逆向分析dns.exe这个二进制程序所得的信息。

<br>

**二、DNS服务器管理协议**

基于RPC的DNS服务器管理协议可以构建在TCP或者命名管道之上。如果你对协议本身或者具体实现感兴趣，你可以好好研究一下域控上的“c:windowssystem32dns.exe”这个程序。协议的RPC接口UUID为“50ABC2A4–574D-40B3–9D66-EE4FD5FBA076”，使用“PIPEDNSSERVER”命名管道进行传输。

微软的DNS服务器是作为域控上的服务来运行的。我们可以运行dnsmgmt.msc，连接到某个AD DNS服务器（通常也是域控），访问管理接口进行管理。管理接口允许用户配置和管理DNS区域（zone），进行DNS的查找、缓存、转发和记录日志等相关操作。在这个层次化结构中，有几个对象与安全有关，比如DNS服务器对象（这些对象不是计算机账户）、区域对象以及区域记录。本文中我们关心的是服务器对象。全新安装的服务器对象的ACL（访问控制列表）应该如下所示：

[![](https://p5.ssl.qhimg.com/t015ffe3a0b112f786a.png)](https://p5.ssl.qhimg.com/t015ffe3a0b112f786a.png)

默认情况下，只有DNS管理员（DnsAdmin）、域管、企业管理员（Enterprise Admins）、本地管理员以及企业域控制器（ENTERPRISE DOMAIN CONTROLLERS）对这个对象有写访问权限。值得注意的是，从攻击者的角度来看，如果我们是这些组（除DnsAdmins之外）的成员，那么我们已经掌握了域的管理权限。因此，让我们来看看，如果我们只是一个DnsAdmin，我们可以做些什么。

<br>

**三、技术细节**

此时我们需要协议规范的帮助了。协议规范的3.1.4节（消息处理事件和排序规则）基本上介绍了服务器需要支持的所有操作。第一个操作是R_DnssrvOperation，这个操作包含一个pszOperation参数，该参数可以决定服务器执行的具体操作。翻阅了pszOperation参数的一大堆可选取值之后，我们找到了这个取值：

[![](https://p5.ssl.qhimg.com/t01b30ac91d48b2f4fa.png)](https://p5.ssl.qhimg.com/t01b30ac91d48b2f4fa.png)

你没看错，我们可以告诉服务器加载我们自己的DLL，听起来非常棒。搜索“ServerLevelPluginDll”，我们找到如下一段有价值的信息：

[![](https://p4.ssl.qhimg.com/t012418c381ea9f6542.png)](https://p4.ssl.qhimg.com/t012418c381ea9f6542.png)

从这段描述中，我们发现服务器似乎没有对这个操作所指定的DLL路径进行任何验证。在开始实践之前，我想肯定有人已经注意到了这一点。使用Google搜索“ServerLevelPluginDll”，我没有找到直接有用的信息，然而我找到了一个非常有用的命令行工具：dnscmd。

幸运的是，dnscmd已经实现了我们所需的一切。快速查看dnscmd的帮助信息，配合官方文档，我们可以看到以下选项：

```
dnscmd.exe /config /serverlevelplugindll \pathtodll
```

首先，我们使用没有特殊权限的普通域用户（这些特殊权限不包括通用读取权限，默认情况下域用户组具备这个权限），在DNS服务器对象上运行这条命令，命令运行失败，返回拒绝访问信息。如果我们让域用户具备这个服务器对象的写访问权限，那么这条命令会运行成功，这意味着DnsAdmins能够成功运行这条命令。<br>

现在还没到使用IDA的时候，我们可以试着在域控上使用DnsAdmins身份运行这条命令，同时运行Process Monitor和Process Explorer工具。我们发现并没有任何DLL被加载到dns.exe的地址空间中。然而，我们可以看到以下注册表键值包含我们所传入的DLL路径：

```
HKEY_LOCAL_MACHINESYSTEMCurrentControlSetservicesDNSParametersServerLevelPluginDll
```

非常好，现在出于测试目的，我们重启DNS服务器所在的服务。情况不妙，DNS服务器无法启动，并且会清除掉与启动有关的注册表键值。显然，我们的DLL中还欠缺一些东西，是时候使用IDA了。

在这种情况下，我们可以使用多种方法快速找到我们需要逆向分析的函数，搜索相关字符串以及相关API函数通常是最简单和最快速的方法。对本文而言，我们搜索LoadLibraryW或者GetProcAddress的交叉引用（xref）即可，也就是说，我们需要查找代码，找到使用LoadLibraryW加载我们DLL文件的函数，以及调用这个函数的父函数。我们会发现，服务器对ServerLevelPluginDll参数的文件路径没有做任何的验证。

我们前面遇到的问题只有一个，那就是如果DLL加载失败，或者DLL没有包含指定的导出函数（DnsPluginInitialize、DnsPluginCleanup或者DnsPluginQuery），那么DNS服务就不能成功启动。我们还需要确保这个DLL所有的导出函数返回值都为0（表示成功返回），否则也会导致服务启动失败。

负责加载DLL的函数伪代码大概如下所示：



```
HMODULE hLib;
if (g_pluginPath &amp;&amp; *g_pluginPath) `{`
  hLib = LoadLibraryW(g_pluginPath);
  g_hndPlugin = hLib;
  if (!hLib) `{`...log and return error...`}`
  g_dllDnsPluginInitialize = GetProcAddress(hLib, "DnsPluginInitialize");
  if (!g_dllDnsPluginInitialize) `{`...log and return error...`}`
  g_dllDnsPluginQuery = GetProcAddress(hLib, "DnsPluginQuery")
  if (!g_dllDnsPluginQuery) `{`...log and return error...`}`
  g_dllDnsPluginCleanup = GetProcAddress(hLib, "DnsPluginCleanup")
  if (!g_dllDnsPluginCleanup) `{`...log and return error...`}`
  if (g_dllDnsPluginInitialize)`{`
    g_dllDnsPluginInitialize(pCallback1, pCallback2);
  `}`
`}`
```

我们可以构造一段简单的PoC代码。在Visual Studio 2015中，满足利用条件的DLL文件代码如下所示：

[![](https://p1.ssl.qhimg.com/t01cde0cb18a1f5fbcc.png)](https://p1.ssl.qhimg.com/t01cde0cb18a1f5fbcc.png)

上述代码中，我们使用“pragma comment”语句设定DLL的导出函数。我们可以使用如下语句验证DLL的导出函数是否正确：

```
dumpbin /exports pathtodll
```

现在我们使用新的DLL，再次尝试dnscmd命令，这次命令运行成功。我们只需要将我们的DLL文件放到某个域控主机账户可以访问的网络路径中即可（dns.exe运行在SYSTEM权限下，只要Everyone SID能够访问这个路径即可），这样我们就能在域控上以SYSTEM权限运行代码，进而控制整个域。

从上文分析中我们知道，如果我们是DnsAdmins的成员，那么我们就有可能控制整个域，但条件不仅限于此，只要我们的账户具备DNS服务器对象的写访问权限也能完成同样任务。以我的经验来说，这些服务器对象的ACL通常不会像域管（或者受AdminSDHolder保护的类似用户组）的ACL那样严格，因此我们还是有机会使用这个技巧实现域权限提升。

正如协议规范中所述，这个技巧适用于大多数Windows Server版本，如下所示：

[![](https://p0.ssl.qhimg.com/t014780584b290f7b48.png)](https://p0.ssl.qhimg.com/t014780584b290f7b48.png)

我们已经向微软的MSRC团队反应了这个问题，他们表示用户可以只允许域控管理员更改ServerLevelPluginDll注册表键值来修复这个问题，并表示有可能会在今后的版本中去除这个功能。

不论如何，dns.exe目前仍然运行在SYSTEM权限下，这样还是会暴露一些可利用的攻击面，因此我们可以从DNS实现角度以及管理接口入手，分析其脆弱性并加以应用。

<br>

**四、时间线**

3月31日，首次向secure@microsoft.com披露此问题

4月1日，问题确认，已转发审查

4月8日，MSRC将该问题标为38121案例

5月2日，微软认为这不是一个漏洞，将来会在安全更新之外修复这个问题

5月5日，讨论如何进一步加固DNS服务器所在的服务

5月8日，研究结果公布。非常感谢MSRC的Daniel处理这个问题，与他合作非常荣幸
