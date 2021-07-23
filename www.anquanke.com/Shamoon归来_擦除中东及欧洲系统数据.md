> 原文链接: https://www.anquanke.com//post/id/168011 


# Shamoon归来：擦除中东及欧洲系统数据


                                阅读量   
                                **172312**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者McAfee，文章来源：securingtomorrow.mcafee.com
                                <br>原文地址：[https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/shamoon-returns-to-wipe-systems-in-middle-east-europe/](https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/shamoon-returns-to-wipe-systems-in-middle-east-europe/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/dm/1024_400_/t0190d5243d48e9efd8.jpg)](https://p0.ssl.qhimg.com/dm/1024_400_/t0190d5243d48e9efd8.jpg)



## 一、前言

多年以来攻击者一直都在使用破坏性恶意软件。通常情况下，这些攻击都有较强针对性，带有意识形态、政治甚至经济方面的目的。

破坏性攻击活动会造成重大经济损失，导致数据丢失或者业务运营受到严重影响。当公司成为目标后，可能损失惨重，需要数周或者数月才能恢复正常，并且期间无法盈利、信誉降低。

从最近的攻击活动中我们可以看到具体的损失程度。在过去一年内，NotPetya影响了全世界多家公司。2月份时，研究人员又发现了针对奥运会组织的OlympicDestroyer。

Shamoon是一款破坏性恶意软件，从出现之日起McAfee就一直在监控这款恶意软件。在本月初时，McAfee Foundstone应急事件响应团队根据客户的反馈，识别出这款软件的最新变种。Shamoon早在2012年就攻击过中东的石油和天然气公司，也在2016年重新攻击这个行业。Shamoon对企业造成非常严重的威胁，我们建议各单位应采取适当措施进行防御。

在过去一周内，我们已经观察到一个新变种攻击了许多部门，其中包括中东和南欧的石油、天然气、能源、电信以及政府组织。

与之前的攻击活动类似，第3版Shamoon变种使用了多种规避技术来绕过安全防御，以便达成攻击目的。然而，变种整体行为与之前版本保持一致，因此大多数反恶意软件引擎处理起来也比较简单。

第3版Shamoon变种与之前变种一样，也会安装一个恶意服务，运行`wiper`组件。一旦`wiper`组件成功运行，就会使用随机的垃圾数据覆盖所有文件，然后重启系统，导致系统蓝屏或者驱动程序错误，使系统无法正常运行。这款变种还能枚举本地网络，但并没有采取进一步措施。变种还存在一些bug，表明这个版本仍是beta版，或仍处于测试阶段。

该版本与早期版本存在一些区别，比如释放恶意文件所使用的文件名列表以及恶意服务名`MaintenaceSrv`（其中“maintenance”单词拼写错误）。`wiper`组件还可以使用如下选项来攻击系统上的所有文件：
- 使用垃圾数据覆盖文件（该版本以及我们分析的样本使用了这种方法）
- 使用某个文件覆盖目标文件（Shamoon版本1及2使用了这种方法）
- 加密文件及主引导记录（该版本没有使用这种方法）
Shamoon是一个模块化恶意软件：`wiper`组件可以作为独立文件加以使用，用于其他攻击活动中，使其威胁等级大大提升。本文介绍了我们的研究成果，包括详细分析过程以及IoC特征。



## 二、整体分析

Shamoon是一款dropper（释放器）程序，包含3个资源文件。dropper负责收集数据、嵌入规避技术（如混淆、反调试或者反取证技巧），需要输入参数才能运行。

解密3个资源后，Shamoon会将这些资源释放到系统的`%System%`目录中，也会创建`MaintenaceSrv`服务，用来运行`wiper`组件。我们可以利用服务名中的拼写错误简化检测过程。

Advanced Threat Research团队多年来一直在跟踪这个服务的变化，具体演变过程如下图所示：

[![](https://p4.ssl.qhimg.com/t012c0f8c9f886b4524.png)](https://p4.ssl.qhimg.com/t012c0f8c9f886b4524.png)

`wiper`使用`ElRawDisk.sys`来访问用户的原始硬盘，覆盖所有目录和磁盘扇区中的所有数据，导致目标主机在最终重启前就处于严重错误状态。

[![](https://p2.ssl.qhimg.com/t0156c2fef1c4e2ac5a.png)](https://p2.ssl.qhimg.com/t0156c2fef1c4e2ac5a.png)

最终导致系统蓝屏或者驱动器错误，使主机无法正常工作。



## 三、大致流程

Shamoon整体工作流程如下图所示：

[![](https://p3.ssl.qhimg.com/t010e8cc7771240b5be.png)](https://p3.ssl.qhimg.com/t010e8cc7771240b5be.png)



## 四、Dropper分析

### <a class="reference-link" name="%E5%8F%AF%E6%89%A7%E8%A1%8C%E6%96%87%E4%BB%B6%E6%A6%82%E8%A6%81"></a>可执行文件概要

[![](https://p0.ssl.qhimg.com/t01116fd692d0a1ea0d.png)](https://p0.ssl.qhimg.com/t01116fd692d0a1ea0d.png)

dropper中包含其他恶意组件，这些组件以加密文件形式内嵌在PE数据区中。

[![](https://p0.ssl.qhimg.com/t01828b26d0b51fc175.png)](https://p0.ssl.qhimg.com/t01828b26d0b51fc175.png)

这些资源数据由dropper解密，具体类型如下：
- MNU：通信模块
- LNG：`wiper`组件
- PIC：64位版dropper
Shamoon 2018需要一个参数才能运行、感染目标主机。Shamoon会在内存中解密多个字符串，收集系统信息，判断是释放32位版还是64位版载荷。

恶意软件耶尔会释放`key8854321.pub`文件（MD5：`41f8cd9ac3fb6b1771177e5770537518`），具体路径为`c:\Windows\Temp\key8854321.pub`。

[![](https://p3.ssl.qhimg.com/t019fa9e7f87856b8cd.png)](https://p3.ssl.qhimg.com/t019fa9e7f87856b8cd.png)

恶意软件随后会解密出需要使用的两个文件：

```
C:\Windows\inf\mdmnis5tQ1.pnf
C:\Windows\inf\averbh_noav.pnf
```

Shamoon会启用`RemoteRegistry`服务，使程序能够远程修改注册表。此外Shamoon还会启用`LocalAccountTokenFilterPolicy`注册表项[禁用远程用户账户控制](https://support.microsoft.com/en-us/help/951016/description-of-user-account-control-and-remote-restrictions-in-windows)。

[![](https://p1.ssl.qhimg.com/t01774f3512ec0d34da.png)](https://p1.ssl.qhimg.com/t01774f3512ec0d34da.png)

恶意软件会检查主机是否存在如下共享，用来复制传播：

```
ADMIN$
C$\WINDOWS
D$\WINDOWS
E$\WINDOWS
```

[![](https://p4.ssl.qhimg.com/t01f2d4c0bdd1524712.png)](https://p4.ssl.qhimg.com/t01f2d4c0bdd1524712.png)

通过查询服务，Shamoon可以获取关于[LocalService](https://docs.microsoft.com/en-us/windows/desktop/services/localservice-account)账户的相关信息。

[![](https://p2.ssl.qhimg.com/t01e813374f5e09f8b2.png)](https://p2.ssl.qhimg.com/t01e813374f5e09f8b2.png)

随后恶意软件读取PE文件中的资源数据，释放攻击组件。Shamoon使用如下代码逻辑查找资源的位置：

[![](https://p4.ssl.qhimg.com/t01ce2111e9a1e62ee8.png)](https://p4.ssl.qhimg.com/t01ce2111e9a1e62ee8.png)

Shamoon创建文件，然后将文件时间设置为2012年8月份，这是一种反取证技巧。这款恶意软件会在所有能破坏的文件上设置这个时间日期。

[![](https://p5.ssl.qhimg.com/t01b678eae10f0a964a.png)](https://p5.ssl.qhimg.com/t01b678eae10f0a964a.png)

这种修改时间方法可以用来规避基于时间戳的检测机制。我们还观察到在某些情况下，修改的时间有所不同，每个文件使用各自的伪造时间。释放到系统中的文件目录为`C:\Windows\System32\`。

在创建恶意服务之前，Shamoon会通过令牌模拟来提升权限。恶意软件首先使用的是`LogonUser`及`ImpersonateLoggedOnUser`，随后使用的是`ImpersonateNamedPipeClient`。Metasploit也使用类似的技术来提升权限。

[![](https://p1.ssl.qhimg.com/t016d512363efd8300b.png)](https://p1.ssl.qhimg.com/t016d512363efd8300b.png)

权限提升对恶意软件来说非常关键，这样才能修改系统配置，正常情况下这种操作会受到各种限制。

Shamoon会创建新的恶意服务：`MaintenaceSrv`，使用`Autostart (StartType: 2)`选项创建服务，然后以进程运行该服务（`ServiceType: 0x10`）。

[![](https://p2.ssl.qhimg.com/t01c914fbddabf8e4cb.png)](https://p2.ssl.qhimg.com/t01c914fbddabf8e4cb.png)

如果该服务之前已经存在，恶意软件会使用新的配置信息修改该服务参数。

[![](https://p0.ssl.qhimg.com/t01b716d6b9db098a6c.png)](https://p0.ssl.qhimg.com/t01b716d6b9db098a6c.png)

最终成功创建`MaintenaceSrv`服务：

[![](https://p3.ssl.qhimg.com/t01610663beb6a7a3ac.png)](https://p3.ssl.qhimg.com/t01610663beb6a7a3ac.png)

[![](https://p1.ssl.qhimg.com/t01c6ee0e517c5e79c1.png)](https://p1.ssl.qhimg.com/t01c6ee0e517c5e79c1.png)

释放到系统中的`wiper`组件可以使用各种名称，如下所示：

[![](https://p1.ssl.qhimg.com/t0152ccbcf6e468eb27.png)](https://p1.ssl.qhimg.com/t0152ccbcf6e468eb27.png)

接下来恶意软件会运行`wiper`，擦除数据。

### <a class="reference-link" name="wiper%E5%88%86%E6%9E%90"></a>wiper分析

`wiper`组件位于`System32`目录中，需要一个参数运行。`wiper`将驱动嵌入在自身资源区中。

[![](https://p1.ssl.qhimg.com/t01a0124ed48ea99f2c.png)](https://p1.ssl.qhimg.com/t01a0124ed48ea99f2c.png)

该资源经过加密处理，如下图所示：

[![](https://p0.ssl.qhimg.com/t01af56aa22164799e4.png)](https://p0.ssl.qhimg.com/t01af56aa22164799e4.png)

这个资源对应的是`ElRawDisk.sys`驱动，该驱动可以用来擦除磁盘。

[![](https://p1.ssl.qhimg.com/t01fc36aeb9f4a7ca28.png)](https://p1.ssl.qhimg.com/t01fc36aeb9f4a7ca28.png)

提取资源的逻辑如下所示：

[![](https://p4.ssl.qhimg.com/t019be1afb6d9b0e405.png)](https://p4.ssl.qhimg.com/t019be1afb6d9b0e405.png)

[![](https://p3.ssl.qhimg.com/t017ab14379393e9af6.png)](https://p3.ssl.qhimg.com/t017ab14379393e9af6.png)

这个文件其实不是恶意文件，但由于是原始驱动程序，因此存在一定风险。

`wiper`会创建一个服务，使用如下参数运行该驱动：

```
sc create hdv_725x type= kernel start= demand binpath= WINDOWShdv_725x.sys 2&gt;&amp;1 &gt;nul
```

[![](https://p4.ssl.qhimg.com/t0114bc65e6315b895d.png)](https://p4.ssl.qhimg.com/t0114bc65e6315b895d.png)

命令执行过程如下：

[![](https://p1.ssl.qhimg.com/t01cb077e64130cbe78.png)](https://p1.ssl.qhimg.com/t01cb077e64130cbe78.png)

恶意软件会覆盖`c:\Windows\System32`目录中的所有文件，使主机处于严重错误状态。系统上的所有文件都会被覆盖。

[![](https://p0.ssl.qhimg.com/t01ed6d99f0992addae.png)](https://p0.ssl.qhimg.com/t01ed6d99f0992addae.png)

负责覆盖操作的进程如下：

[![](https://p2.ssl.qhimg.com/t0156d59a329f378c43.png)](https://p2.ssl.qhimg.com/t0156d59a329f378c43.png)

最后，恶意软件使用如下命令强制系统重启：

```
Shutdown -r -f -t 2
```

[![](https://p5.ssl.qhimg.com/t016dfd1e7cbc3f2e46.png)](https://p5.ssl.qhimg.com/t016dfd1e7cbc3f2e46.png)

一旦系统重启，就会显示蓝屏界面：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01292f6ee21f953429.png)

### <a class="reference-link" name="%E8%A0%95%E8%99%AB%E5%88%86%E6%9E%90"></a>蠕虫分析

恶意软件会从dropper中提取蠕虫组件。破坏性恶意软件通常会使用传播技术来尽快感染其他主机。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f2bc219362877e8f.png)

蠕虫组件会使用如下名称：

[![](https://p0.ssl.qhimg.com/t01a924acead821eef5.png)](https://p0.ssl.qhimg.com/t01a924acead821eef5.png)

我们注意到恶意软件可以扫描本地网络，连接至潜在的控制服务器：

[![](https://p4.ssl.qhimg.com/t0182ad181b9d17e4e7.png)](https://p4.ssl.qhimg.com/t0182ad181b9d17e4e7.png)

虽然蠕虫组件可以传播dropper，连接至远程服务器，但该组件并没有在这版本变种中使用。



## 五、总结

恶意软件能造成严重破坏，并且`wiper`组件还能独立于dropper单独使用，不需要依赖主进程就能执行。我们可以从2018年的Shamoon变种看到模块化开发趋势，这样其他恶意dropper程序就能在Shamoon之外使用`wiper`组件。

Shamoon在不断演变中，但这些技巧无法规避McAfee DAT的检测。我们估计攻击者还会在中东（及其他地区）发起更多攻击活动，我们会继续监控遥测数据，根据了解到的信息更新分析内容。



## 六、MITRE ATT&amp;CK™类别

[![](https://p2.ssl.qhimg.com/t01c425d337e41a4a11.png)](https://p2.ssl.qhimg.com/t01c425d337e41a4a11.png)



## 七、IoC

```
df177772518a8fcedbbc805ceed8daecc0f42fed                    原始dropper x86
ceb7876c01c75673699c74ff7fac64a5ca0e67a1                    Wiper
10411f07640edcaa6104f078af09e2543aa0ca07                    蠕虫模块
43ed9c1309d8bb14bd62b016a5c34a2adbe45943                    key8854321.pub
bf3e0bc893859563811e9a481fde84fe7ecd0684                    RawDisk driver
```



## 八、McAfee检测特征

```
Trojan-Wiper!DE07C4AC94A5
RDN/Generic.dx
Trojan-Wiper
```
