> 原文链接: https://www.anquanke.com//post/id/192892 


# 详解令牌篡改攻击（Part 1）


                                阅读量   
                                **1034229**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者niiconsulting，文章来源：niiconsulting.com
                                <br>原文地址：[https://niiconsulting.com/checkmate/2019/11/token-manipulation-attacks-part-1-introduction-to-tokens-and-privileges/](https://niiconsulting.com/checkmate/2019/11/token-manipulation-attacks-part-1-introduction-to-tokens-and-privileges/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t013380d0e0f13e8b0e.png)](https://p3.ssl.qhimg.com/t013380d0e0f13e8b0e.png)



## 0x00 前言

在这一系列文章中，我们将讨论基于Windows令牌（Token）的攻击方式，全面理解令牌、特权（Privilege）等知识点，了解令牌及特权在Windows系统安全架构中的实现机制。

令牌篡改攻击（Token Manipulation Attack）是多个APT组织及恶意软件常用的一种技术，可以用来在受害者系统上获取高权限，或者以其他用户身份执行操作（用户仿冒）。

MITRE上给出了使用该技术的相关APT组织及涉及到的工具：

[![](https://p1.ssl.qhimg.com/t016ddc94bd5388782e.png)](https://p1.ssl.qhimg.com/t016ddc94bd5388782e.png)

令牌篡改实际上并不完全属于漏洞利用范畴，这里我们滥用的是Windows系统自身的功能，通过某些Windows API函数来修改调用进程的安全上下文，以便模拟另一个进程（通常是低权限进程）的安全上下文。模拟过程可以通过目标进程的线程来完成，后面我们再详细讨论这一点。Windows使用这种功能来修改调用进程所属线程的安全上下文，将其修改成其他用户的安全上下文，以执行某些操作。

Windows系统中有各种用户，比如`System`、`Network Service`、`Local Service`以及`Administrator`账户（组）及普通域用户。这些用户账户都运行在不同的安全上下文中，具备一定级别的访问权限。默认情况下，`System`在本地系统中具备最高权限。在大多数情况下，恶意程序希望窃取运行在`System`安全上下文中的进程令牌，以获得最高权限。



## 0x01 令牌

在分析这些技术前，我们先来了解下令牌及特权的基本知识。

令牌（Token）或者访问令牌（Accss Token）是一个内核对象，用来描述进程或线程所使用的安全上下文。

访问令牌中包含各种信息，比如安全标识符（SID，Security Identifier）、令牌类型（Token Type）、用户及组信息、权限、登录会话（Logon Session）等，系统会在用户登录时分配访问令牌。

为了执行各种操作或者使用Windows中的各种资源，进程必须使用Windows句柄打开或者创建对象，才能访问内核对象。内核会根据访问令牌赋予进程匹配的访问权限。

### <a class="reference-link" name="%E8%AE%BF%E9%97%AE%E4%BB%A4%E7%89%8C%E5%88%9B%E5%BB%BA"></a>访问令牌创建

[![](https://p5.ssl.qhimg.com/t0106baa59e86417dd6.png)](https://p5.ssl.qhimg.com/t0106baa59e86417dd6.png)
- 当用户登录主机时，系统会创建访问令牌。
- 检测密码是否正确，执行认证过程。
- 在安全数据库中检查用户详细信息。
- 检查用户是否属于内置的管理员组中，如果满足条件，则生成两个令牌：完整的管理员访问令牌及标准用户访问令牌。
- 如果用户不属于内置管理员组，则只会生成标准用户访问令牌。
访问令牌在Windows系统的UAC（用户访问控制）功能中发挥重要作用。

当属于内置管理员组的用户登录时，系统并没有向用户提供完整的管理员访问令牌。Windows系统会为该用户创建拆分（split）令牌。这里有两种类型的拆分令牌：“Filtered Token”（过滤令牌）及“Elevated Token”（提升令牌）。

当用户分配的是Filtered Token时，基本意味着用户运行在中完整性（medium integrity）级别上，被剔除了管理员组权限及SID，这意味着用户无法直接执行各种管理任务。为了执行管理任务，用户必须通过UAC认证，或者输入正确的凭据。

当用户通过UAC认证或输入正确凭据后，系统会给用户分配Elevated Token，用户就可以执行管理任务。Elevated Token是带有高完整性的令牌，其中包括管理员组的SID及权限。

[![](https://p0.ssl.qhimg.com/t010f422fec952ca563.png)](https://p0.ssl.qhimg.com/t010f422fec952ca563.png)

图. 执行管理任务时弹出确认窗口

[![](https://p1.ssl.qhimg.com/t0138d54b98af227731.png)](https://p1.ssl.qhimg.com/t0138d54b98af227731.png)

图. 用户需输入凭据以执行管理任务

如果正确配置UAC，那就能有效发挥该机制的安全功能。

如果大家想全面理解UAC，可以参考官方提供的[这篇文章](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/how-user-account-control-works)。

### <a class="reference-link" name="%E4%BB%A4%E7%89%8C%E6%9C%BA%E7%90%86"></a>令牌机理

为了进一步理解Windows中的令牌对象，我们来看一下令牌的内部机理（比如令牌对应的内核数据结构）。这里我们使用WinDbg来查看内核数据结构。

首先，我们来观察`TOKEN`结构。

[![](https://p1.ssl.qhimg.com/t017512e7dd2a6780c4.png)](https://p1.ssl.qhimg.com/t017512e7dd2a6780c4.png)

在上图中，我们可以看到`TOKEN`数据的完整结构，该结构中包含其他一些数据结构，这些结构用来定义与令牌有关的各种属性及信息，与登录用户密切相关。

该结构中包含`TokenId`、`Privileges`数组，定义了对应该用户所分配的所有特权，`TokenType`定义了令牌类型：`Primary`或者`Impersonation`等。

接下来观察`TOKEN`结构中的部分数据结构。

[![](https://p3.ssl.qhimg.com/t01420cb3281de3e410.png)](https://p3.ssl.qhimg.com/t01420cb3281de3e410.png)

`SEP_TOKEN_PRIVILEGES`结构中包含与令牌相关的特权的所有信息，其中`Present`为令牌当前可用的权限；`Enabled`为已启用的权限；`EnabledByDefault`为默认情况下已启用的权限。

[![](https://p5.ssl.qhimg.com/t01bc5a61d96481222e.png)](https://p5.ssl.qhimg.com/t01bc5a61d96481222e.png)

`TOKEN_TYPE`为枚举类型，其中定义了令牌类型是否为`Primary`或者`Impersonation`（后续文章中会详细分析这方面内容）。

[![](https://p4.ssl.qhimg.com/t01f5814fdd4fab32d0.png)](https://p4.ssl.qhimg.com/t01f5814fdd4fab32d0.png)

`SECURITY_IMPERSONATION_LEVEL`也是一个枚举类型，其中指定了不同常量，用来决定调用进程可以在哪种级别模拟目标进程。

常量的定义可参考微软[官方文档](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-security_impersonation_level)，具体如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f017b7518835096b.png)

我们将使用`TOKEN_TYPE`及`SECURITY_IMPERSONATION_LEVEL`常量来模拟令牌，可根据具体情况来设置相应值，比如是使用`Primary`令牌来创建进程，或者是使用`Impersonation`令牌来模拟某个进程。

[![](https://p2.ssl.qhimg.com/t015f63bebd3522949a.png)](https://p2.ssl.qhimg.com/t015f63bebd3522949a.png)

`SID_AND_ATTRIBUTES`结构定义了SID（安全标识符）及SID的属性。



## 0x02 特权

一般而言，特权（Privilege）这个词指的是上级单位根据某些条件赋予某人或者某个组织的一种特殊权利。

与之类似，在Windows系统中，管理员可以为用户分配某些特权以执行系统相关的活动。默认情况下系统会给用户分配一些特权，而管理员也可以使用“本地安全策略设置”在本地为用户分配一些特权。

[![](https://p4.ssl.qhimg.com/t016c492c5dea46260f.png)](https://p4.ssl.qhimg.com/t016c492c5dea46260f.png)

特权决定哪个用户可以控制系统资源，以执行系统相关任务，如关机、调试被其他进程使用的进程内存、将驱动载入内存中、备份文件及目录等。

Windows系统中可用的特权常量可参考[此处资料](https://docs.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)。

在上文中，我们提到`SEP_TOKEN_PRIVILEGES`结构中包含`Enabled`及`EnabledByDefault`成员，这意味着分配给用户的所有特权默认情况下不一定处于启用状态，只有某些特权在分配时被启用，如果需要其他特权来执行系统相关任务，则必须通过外部方式启用这些特权。

标准用户已启用的特权如下图所示：

[![](https://p1.ssl.qhimg.com/t0188ba5961df96e061.png)](https://p1.ssl.qhimg.com/t0188ba5961df96e061.png)

如上图所示，只有`SeChangeNotifyPrivilege`特权处于启用状态，分配给用户的其他特权处于禁用状态。为了使用这些特权，我们首先必须执行启用操作。

在本系列文章中，我们将启用`SE_DEBUG_NAME`特权，该特权可以帮我们调试无法访问的进程或者运行在`SYSTEM`账户下的进程。

下面来观察不同用户所对应的令牌，这里我们来观察运行在标准用户及管理员用户安全上下文中的`notepad`进程所对应的令牌。

我们使用WinDbg来查看目标进程（这里为`notepad.exe`）的令牌。

**标准用户的令牌状态如下：**

[![](https://p2.ssl.qhimg.com/t01bb4ba3a248514250.png)](https://p2.ssl.qhimg.com/t01bb4ba3a248514250.png)

上图中可以看到进程对应的`Session ID`（已登录的会话）、`Impersonation Level`、`TokenType`等，该进程的令牌类型为`Primary`。此外上图顶部的输出信息表明对应的线程没有处于模拟状态，使用的是`Primary`令牌。

从图中可知分配给该进程的特权与分配给普通用户的特权一样，因为该进程运行在标准用户的安全上下文中。

`Elevation Type`的值为`3`（`Limited`，受限），这表明这是一个受限令牌，其中剔除了管理员特权，禁用了管理员组。

**管理员用户的令牌状态如下：**

[![](https://p4.ssl.qhimg.com/t014c1dced29abe1809.png)](https://p4.ssl.qhimg.com/t014c1dced29abe1809.png)

上图的令牌信息与标准用户类似，但分配的特权要比标准用户要多得多，基本上所有特权都会分配管理员用户。此外，我们可以看到这里的`Elevation Type`为`2`（`Full`，完整），表明这是提升（Elevated）令牌，没有被剔除某些权限及用户组。

> 备注：只有当UAC启用时，`Elevation Type`才为`2`或者`3`，当UAC禁用或者用户为内置管理员账户或者服务账户时，`Type`等于`1`。



## 0x03 总结

在本文中，我们讨论了访问令牌以及访问令牌的使用场景、生成时间点、`TOKEN`内部结构以及与令牌相关的许多知识点。这些知识点非常重要，可以帮我们理解令牌在Windows系统用户及进程的安全上下文的工作方式。理解这些内容后，在下文中我们将继续研究，使用Windows API来发起令牌篡改攻击。

[![](https://p2.ssl.qhimg.com/t0108effa3c41a9f24e.jpg)](https://p2.ssl.qhimg.com/t0108effa3c41a9f24e.jpg)
