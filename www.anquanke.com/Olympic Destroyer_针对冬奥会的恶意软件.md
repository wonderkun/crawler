> 原文链接: https://www.anquanke.com//post/id/98495 


# Olympic Destroyer：针对冬奥会的恶意软件


                                阅读量   
                                **161310**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者 WARREN MERCER，文章来源：blog.talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2018/02/olympic-destroyer.html](http://blog.talosintelligence.com/2018/02/olympic-destroyer.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0185db3af69b1e4bf2.jpg)](https://p1.ssl.qhimg.com/t0185db3af69b1e4bf2.jpg)



## 一、前言

今年的冬奥会正在韩国平昌举行。来自英国卫报的一篇[报道](https://www.theguardian.com/sport/2018/feb/10/winter-olympics-investigating-if-technical-problems-were-cyber-attack)称，奥运会的计算机系统在开幕式期间遇到了一些技术问题。经奥运会官员确认，某些非关键系统的确出现了一些技术问题，但维护人员已经在12小时内完成恢复操作。2月11日（星期天），奥运会官员[证实](https://www.theguardian.com/sport/2018/feb/11/winter-olympics-was-hit-by-cyber-attack-officials-confirm)系统曾遭受网络攻击，但没有进一步发表评论或推测结果。

Talos团队已经识别出了本次攻击活动中所涉及的样本。目前我们仍未找出感染路径，但会继续调查核实。攻击者并没有使用我们发现的这些样本来收集奥运会竞争对手的相关信息，相反，他们的目标是破坏这次运动会。根据分析结果，这些样本似乎只会执行破坏性功能。攻击过程中并没有任何数据遭到泄露。对样本的分析结果表明，攻击者又开始使用合法软件，因为我们在样本中识别出了PsExec模块。这款恶意软件会删除卷影副本（shadows copies）、事件日志来破坏系统正常功能，也会尝试使用PsExec以及WMI在目标环境中继续渗透。之前我们也在[BadRabbit](http://blog.talosintelligence.com/2017/10/bad-rabbit.html)以及[Nyetya](http://blog.talosintelligence.com/2017/06/worldwide-ransomware-variant.html)中看到过类似行为。



## 二、工作流程

### <a class="reference-link" name="2.1%20%E5%88%9D%E5%A7%8B%E9%98%B6%E6%AE%B5"></a>2.1 初始阶段

最早样本的哈希值为`edb1ff2521fb4bf748111f92786d260d40407a2e8463dcd24bb09f908ee13eb9`，这是一个二进制文件，当该样本执行时，会将多个文件释放到受害者的主机上。这些文件以资源形式嵌入恶意软件中（经过混淆处理）。攻击者使用随机生成的文件名来命名这些文件，然而，我们在多次实验后发现，写入磁盘的这些文件具有相同的哈希值。目前我们尚未发现攻击者最开始使用的感染途径，由于这是一个二进制文件，因此攻击者可能使用多种方法成功完成初始恶意软件的投递。

释放出来的文件中，攻击者会使用两个参数来执行其中的两个文件（即凭据窃取模块），这两个参数分别为`123`以及一个命名管道。命名管道可以作为初始阶段载荷以及释放出的可执行文件的通信通道。BadRabbit以及Nyetya中也用到了这种技术。

初始阶段载荷负责在目标环境中继续扩散。攻击者使用如下两种技术来发现周围网络环境：

1、使用GetIPNetTable这个Windows API来检查ARP表。

2、在WMI（使用WQL）中使用如下请求：`SELECT ds_cn FROM ds_computer`。这个请求可以列出当前环境/目录中的所有系统。

恶意软件使用PsExec以及WMI（通过Win32_Process类）在网络中扩散。远程执行的代码如下所示：

[![](https://p1.ssl.qhimg.com/t01ae28ab58b098552c.png)](https://p1.ssl.qhimg.com/t01ae28ab58b098552c.png)

这段代码的目的是将初始阶段载荷拷贝到远程系统的`%ProgramData%%COMPUTERNAME%.exe`，然后通过VBScript执行这个载荷。

为了实现横向渗透，恶意软件需要有效的凭据。恶意软件使用了2个窃取器（下文会介绍）以及二进制文件中硬编码的凭据来完成这一任务。

[![](https://p1.ssl.qhimg.com/t019a3f94f1a0c3aeeb.png)](https://p1.ssl.qhimg.com/t019a3f94f1a0c3aeeb.png)

如你所见，恶意软件所使用的域名与`Pyeonchang 2018（平昌2018）`有关。这款恶意软件的作者对奥运会的基础设施细节了如指掌，比如用户名、域名、服务器名以及密码。我们在二进制文件中总共识别出了44个不同的账户信息。

### <a class="reference-link" name="2.2%20%E9%87%8A%E6%94%BE%E5%87%BA%E7%9A%84%E6%96%87%E4%BB%B6"></a>2.2 释放出的文件

**浏览器凭据窃取器**

Olympic Destroyer会释放出一个浏览器凭据窃取器（Browser Stealer）。最终的攻击载荷嵌入在经过混淆处理的资源中，恶意软件样本必须使用前面提到的2个参数才能正确执行攻击载荷。这款窃取器支持IE、Firefox以及Chrome浏览器。恶意软件会解析注册表，查询sqlite文件，获取所需的浏览器凭据信息。样本中集成了SQLite功能，如下所示：

[![](https://p0.ssl.qhimg.com/t0133b4d469e6dfb735.png)](https://p0.ssl.qhimg.com/t0133b4d469e6dfb735.png)

**系统凭据窃取器**

除了浏览器凭据窃取器以外，Olympic Destroyer还会释放并执行一款系统凭据窃取器（System Stealer）。这款窃取器试图使用与Mimikatz类似的技术，从LSASS中窃取凭据信息。初始阶段载荷所解析出来的输出格式如下所示：

[![](https://p0.ssl.qhimg.com/t016a15bc9cc9b02ef1.png)](https://p0.ssl.qhimg.com/t016a15bc9cc9b02ef1.png)

**摧毁器（destructor）**

恶意软件刚在受害者主机上运行时 ，就已经开始执行破坏活动。如前文所述，刚开始执行时，恶意软件会将多个文件写入磁盘中。随后，恶意软件开始踏上破坏之旅。恶意软件首先会借助主机上的`cmd.exe`，利用`vssadmin`删除所有可能存在的卷影副本，如下所示：

```
C:Windowssystem32cmd.exe /c c:Windowssystem32vssadmin.exe delete shadows /all /quiet
```

接下来，恶意软件再次利用主机上的`cmd.exe`，通过[`wbadmin.exe`](https://en.wikipedia.org/wiki/WBAdmin)来删除编录（catalog）数据（wbadmin是现代操作系统中ntbackup的替代品）。

```
C:Windowssystem32cmd.exe /c wbadmin.exe delete catalog -quiet
```

之所以执行这个步骤，就是想让文件恢复更加艰难。WBAdmin可以用来恢复单个文件、目录以及整个驱动器数据，因此系统管理员可以利用这个工具来辅助文件恢复。

接下来，攻击者会配合使用`cmd.exe`以及`bcdedit`（用于配置启动数据信息的一款工具），以确保Windows的恢复控制台不会尝试恢复主机上的任何数据。

```
C:Windowssystem32cmd.exe /c bcdedit.exe /set `{`default`}` bootstatuspolicy ignoreallfailures &amp; bcdedit /set `{`default`}` recoveryenabled no
```

经过这些操作，想恢复受影响主机上的数据已经非常困难。为了进一步掩盖行踪，攻击者会删除Windows上的System以及Security日志，增加安全分析的难度。

```
C:Windowssystem32cmd.exe /c wevtutil.exe cl System

C:Windowssystem32cmd.exe /c wevtutil.exe cl Security
```

恶意软件会执行这些擦除操作，表明攻击者根本不想让主机保持正常使用状态。这款恶意软件的目的是摧毁目标主机、使计算机系统离线并擦除远程数据。

[![](https://p4.ssl.qhimg.com/t01f1c0526ef55624c3.png)](https://p4.ssl.qhimg.com/t01f1c0526ef55624c3.png)

此外，恶意软件也会禁用系统上的所有服务：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010483f5fb2f59d0cf.png)

恶意软件使用ChangeServiceConfigW这个API，将服务的启动类型改成4，意思是“已禁用：不启动指定服务”。

此外，恶意软件会列出已映射的文件共享，然后清除每个共享中所有可写的文件（使用未初始化的数据或者0x00来填充，根据文件大小决定填充方式）。

最后，在修改完所有的系统配置选项后，这款恶意软件会关闭已破坏的目标系统。

**合法文件**

除恶意载荷外，Olympic Destroyer也会释放出合法的、经过数字签名的PsExec文件，利用微软出品的这款工具实现横向渗透。攻击者经常将合法的工具添加到自己的武器库中。使用类似PsExec之类的工具，攻击者可以节省自己开发工具的时间。在这种情况下，在自己的恶意软件中集成免费的替代工具显然是更加明智的选择。



## 三、总结

在摧毁型攻击活动中，攻击者往往带有的明确目的性。本文分析的这次攻击活动显然以破坏为行动宗旨，因此我们有十足的把握认为此次攻击的幕后黑手想让奥组委在开幕式中出个大糗。

有许多服务受到此次攻击影响，比如奥运会官网处于离线状态，也就是说用户无法打印自己的门票。由于开幕式现场记者无法使用WiFi，因此关于开幕式的报道数量有所下降。另外，攻击者在这次攻击者用到了硬编码的凭据信息，这表明奥运会的基础设施此前可能已经被攻陷过，导致这些凭据被泄露给攻击者。

目前我们还不清楚恶意软件的传播机制，这意味着感染方式可能各种各样，但如果攻击者事先已具备目标环境的访问权限，那么攻击者很有可能远程发起攻击。这样一来，攻击者可以精准定位开幕式时间，控制攻击活动所能造成的影响范围。



## 四、IoC

**Olympic Destroyer：**

```
edb1ff2521fb4bf748111f92786d260d40407a2e8463dcd24bb09f908ee13eb9
```

**浏览器凭据窃取器：**

```
19ab44a1343db19741b0e0b06bacce55990b6c8f789815daaf3476e0cc30ebea
```

处于封装状态时的哈希值：

```
ab5bf79274b6583a00be203256a4eacfa30a37bc889b5493da9456e2d5885c7f
```

**系统凭据窃取器：**

```
f188abc33d351c2254d794b525c5a8b79ea78acd3050cd8d27d3ecfc568c2936
```

处于封装状态时的哈希值：

```
a7d6dcdf5ca2c426cc6c447cff76834d97bc1fdff2cd14bad0b7c2817408c334
```

**摧毁器：**

```
ae9a4e244a9b3c77d489dee8aeaf35a7c3ba31b210e76d81ef2e91790f052c85
```

**合法的Psexec模块：**

```
3337e3875b05e0bfba69ab926532e3f179e8cfbf162ebb60ce58a0281437a7ef
```

**其他Olympic Destroyer样本：**

```
D934CB8D0EADB93F8A57A9B8853C5DB218D5DB78C16A35F374E413884D915016
EDB1FF2521FB4BF748111F92786D260D40407A2E8463DCD24BB09F908EE13EB9
3E27B6B287F0B9F7E85BFE18901D961110AE969D58B44AF15B1D75BE749022C2
28858CC6E05225F7D156D1C6A21ED11188777FA0A752CB7B56038D79A88627CC
```
