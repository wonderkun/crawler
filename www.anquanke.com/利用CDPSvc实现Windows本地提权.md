> 原文链接: https://www.anquanke.com//post/id/195008 


# 利用CDPSvc实现Windows本地提权


                                阅读量   
                                **1445560**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者itm4n.github.io，文章来源：
                                <br>原文地址：[github](github)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01e5752d05b022f8a9.png)](https://p5.ssl.qhimg.com/t01e5752d05b022f8a9.png)



## 0x00 前言

CDPSvc服务中存在一个DLL劫持漏洞，微软今年至少2次收到了该漏洞的反馈报告。根据官方策略，涉及`PATH`目录的DLL劫持并不属于安全风险范围，也就是说该问题（至少在短期内）不会被解决。这个问题与Windows Vista/7/8中的IKEEXT服务问题比较类似，最大的不同点在于CDPSvc以`LOCAL SERVICE`而不是`SYSTEM`权限运行，因此想获得较高权限还需要经过一些操作。



## 0x01 CDPSvc DLL劫持

大家应该都比较熟悉DLL劫持技术，这是Windows系统中最古老、可能也是最基本的权限提升技术。此外，[Nafiez](https://twitter.com/zeifan)也在一篇[文章](https://nafiez.github.io/security/eop/2019/11/05/windows-service-host-process-eop.html)中详细解释过CDPSvc服务存在的问题。

简而言之，CDPSvc（Connected Devices Platform Service，连接设备平台服务）是运行在`NT AUTHORITY\LOCAL SERVICE`上下文中的一个服务，该服务在启动时会调用`LoadLibrary()`，尝试加载系统中并不存在的一个DLL（`cdpsgshims.dll`），并且没有指定该DLL的绝对路径。

[![](https://p4.ssl.qhimg.com/t0172e12418cad0b681.png)](https://p4.ssl.qhimg.com/t0172e12418cad0b681.png)

因此，根据Windows的DLL搜索顺序，该服务首先会从`system`目录尝试加载DLL，然后遍历`PATH`环境变量中存储的目录。因此，如果其中某个服务权限配置不严格，我们就可以植入“恶意”DLL，然后在主机重启时实现在`NT AUTHORITY\LOCAL SERVICE`上下文中执行任意代码。

[![](https://p3.ssl.qhimg.com/t0171dec542f1951837.png)](https://p3.ssl.qhimg.com/t0171dec542f1951837.png)

> 注意：最后一个`PATH`变量与当前用户有关，这意味着如果我们在Windows 10中查看自己相关的`PATH`变量，总能找到可写的这个目录。如果想查看系统的`PATH`变量，可以使用如下命令来查看注册表相关减值：
<pre><code class="hljs nginx">reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /V Path
</code></pre>

以上内容比较啰嗦，下面我们来讨论Windows的一些内部原理以及大家比较少用到的一些利用技术。



## 0x02 Tokens及Impersonation

在之前的文章中，我分析了不具备模拟（Impersonation）特权的服务账户。结果表明，CDPSvc并属于该类别，因此我们可以利用这一点。然而我发现这方面内容我没有解释清楚，虽然内容不是很复杂，但因为涉及的点太多，容易被人忽视。

我研究了许多工具的内部原理，比如[RottenPotato](https://github.com/foxglovesec/RottenPotato)以及[JuicyPotato](https://github.com/ohpe/juicy-potato)，因此我想尽可能以比较清晰的方式与大家分享我学到的知识。如果大家对这方面比较了解，可以直接跳到下一部分内容。

### <a class="reference-link" name="%E4%BB%A4%E7%89%8C%E7%B1%BB%E5%9E%8B"></a>令牌类型

首先来讲一下令牌（Token）。Windows中有2种类型的令牌：`Primary`令牌及`Impersonation`令牌。`Primary`令牌代表进程的安全信息，而`Impersonation`令牌代表另一个用户在线程中的安全上下文。
<li>
`Primary`令牌：每个进程1个；</li>
<li>
`Impersonation`令牌：每个线程1个，用来模拟另一个用户。</li>
> 注意：我们可以调用`DuplicateTokenEx()`，将`Impersonation`令牌转换为`Primary`令牌。

### <a class="reference-link" name="%E6%A8%A1%E6%8B%9F%E7%BA%A7%E5%88%AB"></a>模拟级别

`Impersonation`令牌具有特定的模拟级别，分别为`Anonymous`、`Identification`、`Impersonation`或者`Delegation`。只有当某个令牌关联`Impersonation`或者`Delegation`级别时，我们才能使用令牌进行模拟。
<li>
`Anonymous`：服务器无法模拟或者识别客户端；</li>
<li>
`Identification`：服务器可以识别并获取客户端特权信息，但无法模拟客户端；</li>
<li>
`Impersonation`：服务端可以在本地系统中模拟客户端的安全上下文；</li>
<li>
`Delegation`：服务端可以在远程系统中模拟客户端的安全上下文。</li>
目前据我所知，在Windows中我们可以通过3种不同的方法以其他用户的身份来创建进程，具体如下：

1、`CreateProcessWithLogon()`（[参考文档](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createprocesswithlogonw)）。

该函数不需要任何特殊特权，任何用户都可以调用该函数，然而我们必须知道目标账户的密码。这也是`runas`所使用的方法。

2、`CreateProcessWithToken()`（[参考文档](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createprocesswithtokenw)）。

该函数需要`SeImpersonatePrivilege`特权，（`LOCAL SERVICE`账户中）该特权默认处于启用状态。调用该函数时我们需要提供一个`Primary`令牌。

3、`CreateProcessAsUser()`（[参考文档](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessasusera)）。

该函数需要`SeAssignPrimaryTokenPrivilege`以及`SeIncreaseQuotaPrivilege`特权，（`LOCAL SERVICE`账户中）该特权默认处于禁用状态，但实际上我们只需要启用`SeAssignPrimaryTokenPrivilege`即可。在API调用过程中，`SeIncreaseQuotaPrivilege`会自动被禁用或者启用，对用户透明。调用该函数时我们也需要提供`Primary`令牌。

总结如下：

<th style="text-align: center;">API函数</th><th style="text-align: center;">Privilege(s) required</th><th style="text-align: center;">Input</th>
|------
<td style="text-align: center;">`CreateProcessWithLogon()`</td><td style="text-align: center;">无</td><td style="text-align: center;">域/用户名/密码</td>
<td style="text-align: center;">`CreateProcessWithToken()`</td><td style="text-align: center;">`SeImpersonatePrivilege`</td><td style="text-align: center;">Primary令牌</td>
<td style="text-align: center;">`CreateProcessAsUser()`</td><td style="text-align: center;">`SeAssignPrimaryTokenPrivilege` 以及`SeIncreaseQuotaPrivilege`</td><td style="text-align: center;">Primary令牌</td>

### <a class="reference-link" name="CDPSvc"></a>CDPSvc

从下图中可知，CDPSvc具备我们刚提到过的3种特权，因此只要我们有某个本地用户的有效令牌，该服务就可以通过`CreateProcessWithToken()`或者`CreateProcessAsUser()`来模拟任何本地用户。

[![](https://p3.ssl.qhimg.com/t01252a221c378374c0.png)](https://p3.ssl.qhimg.com/t01252a221c378374c0.png)

因此，我们已经具备相应的特权来模拟`NT AUTHORITY\SYSTEM`。那么接下来我们还需要一个有效的令牌，但如何解决该问题呢？



## 0x03 Token Kidnapping

在早期版本的Windows中，所有服务都以`SYSTEM`权限运行，这意味着当其中某个服务被攻破，其他所有服务及宿主程序本身都会被攻破。因此，微软后续添加了一些隔离机制，引入了权限较低的两个账户：`NETWORK SERVICE`及`LOCAL SERVICE`。

不幸的是，这种防御机制并不完美。如果以`LOCAL SERVICE`身份运行的服务被攻破，攻击者就可以在使用相同用户账户运行的其他服务中执行代码、访问内存空间以及提取特权模拟令牌：这种技术称之为“Token Kidnapping”（令牌绑架），最早在2008年由Cesar Cerrudo在多次会议上[公开](https://dl.packetstormsecurity.net/papers/presentations/TokenKidnapping.pdf)。

为了应对这种方法，微软必须重新设计适用于服务的安全模型。微软部署的主要机制为服务隔离（Service Isolation），核心思想是让每个服务都以专用的安全描述符（SID）运行。比如，如果服务`A`的描述符为`SID_A`，服务`B`的描述符为`SID_B`，那么由于两个进程现在使用不同的标识符运行（虽然对应同一个账户），但服务`A`将无法访问服务`B`的资源。

以下内容摘抄自微软的[官方文档](https://blogs.iis.net/nazim/token-kidnapping-in-windows)：

> 要解决的第一个问题就是确保以相同身份运行的两个服务不能自由访问彼此的令牌。在Windows Vista及更高版本中，我们通过服务加固解决了该问题。在调查该问题的过程中，我们找到了一些脆弱点，系统需要做些修改来进一步强化服务安全机制。

通过前面分析，可能大家会认为因为服务隔离的存在，Token Kidnapping技术已不再有效，我们已无路可走。

需要注意的是，默认情况下，当主机内存小于3.5GB时，CDPSvc服务就会在共享进程中运行（参考Windows 10中的Service Host（即`svchost.exe`）的[改动](https://docs.microsoft.com/en-us/windows/application-management/svchost-service-refactoring)）。这里的问题在于，这些服务中是否存在能够泄露令牌句柄的某些服务？

[![](https://p0.ssl.qhimg.com/t0190aa3baa1bcfa805.png)](https://p0.ssl.qhimg.com/t0190aa3baa1bcfa805.png)

再来观察一下该进程的属性。通过Process Hacker，我们可以方便查看相关属性，分析指定进程中打开的所有句柄（`Handle`）。

[![](https://p0.ssl.qhimg.com/t014454eacec25268bf.png)](https://p0.ssl.qhimg.com/t014454eacec25268bf.png)

似乎目前该进程中有5个打开的句柄关联到于`SYSTEM`账户的`Impersonation`令牌，这正好满足我们的条件，那下一步我们该怎么做？

句柄是对某个对象（比如进程、线程、文件或者令牌等）的引用，但其中并没有直接保存对象的地址。句柄只是系统内部维护表（其中“实际”存放着对象地址）中存储的一个条目，可以当成ID值来看待，很容易被暴力枚举，这也是Token Kidnapping技术的主要思路。

Token Kidnapping技术利用过程中会打开另一个进程，然后在当前进程中复制目标句柄，通过这种方式来暴力枚举已打开的句柄。检查到有效句柄后，我们可以检查该句柄是否关联到某个令牌，如果不满足条件，就继续处理下一个句柄。

如果找到了有效的令牌句柄，我们必须检查其是否满足如下3个条件：

1、对应的账户是否为`SYSTEM`？

2、是否为`Impersonation`令牌？

3、令牌的模拟级别是否至少为`Impersonation`？

当然，由于服务隔离，这种技术无法应用于运行在不同进程中的其他服务。然而，如果我们可以将DLL“注入”到其中某个服务，我们就可以不受限制，自由访问对应进程的内存空间。因此，我们可以从当前进程内发起相同的暴力枚举攻击。此外，一旦我们找到了合适的模拟令牌，就可以复制该令牌，使用Windows API以`NT AUTHORITY\SYSTEM`权限创建进程。整个过程就是这么简单。

大家可以访问此处下载本文使用的[PoC](https://github.com/itm4n/CDPSvcDllHijacking)。

攻击过程可参考下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://itm4n.github.io/assets/2019-12-11-cdpsvc-dll-hijacking/00_demo_2.gif)



## 0x04 参考资料
<li>(MSRC Case 54347) Microsoft Windows Service Host (svchost) – Elevation of Privilege<br>[https://nafiez.github.io/security/eop/2019/11/05/windows-service-host-process-eop.html](https://nafiez.github.io/security/eop/2019/11/05/windows-service-host-process-eop.html)
</li>
<li>Windows 10 Persistence via PATH directories – CDPSvc<br>[https://www.a12d404.net/windows/2019/01/13/persistance-via-path-directories.html](https://www.a12d404.net/windows/2019/01/13/persistance-via-path-directories.html)
</li>
<li>Cesar Cerrudo – Token Kidnapping<br>[https://dl.packetstormsecurity.net/papers/presentations/TokenKidnapping.pdf](https://dl.packetstormsecurity.net/papers/presentations/TokenKidnapping.pdf)
</li>
<li>MS Blog – Token Kidnapping in Windows<br>[https://blogs.iis.net/nazim/token-kidnapping-in-windows](https://blogs.iis.net/nazim/token-kidnapping-in-windows)
</li>
<li>MSRC – Triaging a DLL planting vulnerability<br>[https://msrc-blog.microsoft.com/2018/04/04/triaging-a-dll-planting-vulnerability/](https://msrc-blog.microsoft.com/2018/04/04/triaging-a-dll-planting-vulnerability/)
</li>
<li>MSDN – Access Tokens<br>[https://docs.microsoft.com/en-us/windows/win32/secauthz/access-tokens](https://docs.microsoft.com/en-us/windows/win32/secauthz/access-tokens)
</li>
<li>MSDN – Impersonation Levels<br>[https://docs.microsoft.com/en-us/windows/win32/secauthz/impersonation-levels](https://docs.microsoft.com/en-us/windows/win32/secauthz/impersonation-levels)
</li>