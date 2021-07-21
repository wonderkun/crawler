> 原文链接: https://www.anquanke.com//post/id/212163 


# AD域中的ACL攻防探索


                                阅读量   
                                **217496**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01bd1a7feef2372eb6.png)](https://p5.ssl.qhimg.com/t01bd1a7feef2372eb6.png)



## 0x00 前言

关于域内ACL的攻防近两年经常被人所提起，同时也产生了很多关于域内ACL相关的工具和攻击方式，本文将会从ACL的概念谈起，然后介绍几种不同的域内攻击方式以及如何监测和防御对于ACL的攻击。



## 0x01 ACL的概念和作用

### <a class="reference-link" name="ACM%EF%BC%9A"></a>ACM：

​ 首先想要了解ACL首先需要了解Access Control Model（访问控制模型），根据官网（[https://docs.microsoft.com/zh-cn/windows/win32/secauthz/access-control-model）给出的定义：](https://docs.microsoft.com/zh-cn/windows/win32/secauthz/access-control-model%EF%BC%89%E7%BB%99%E5%87%BA%E7%9A%84%E5%AE%9A%E4%B9%89%EF%BC%9A)<br>
访问控制模型能够控制进程访问一些安全对象，或者是控制进程执行各种系统管理任务。原文：The access control model enables you to control the ability of a process to access securable objects or to perform various system administration tasks。<br>
用通俗一点的话来说ACM就是一个判断你在一个档案馆（在这里可以理解为整个域）里是否有权限打开某个档案抽屉（用户对象、用户组对象、Computer对象），并且是否能在这个档案抽屉中取走、存放、修改档案（读、写、修改）的一个模型。<br>
访问模型包含哪些部分：

```
1、Access Tokens（访问tokens）
2、Security Descriptors（安全描述符）
   a、Discretionary Access Control List (DACL)
   b、System Access Control List (SACL)
Access Control Lists（ACL）
Access Control Entries（ACE）
Access Rights and Access Masks（访问权限和访问掩码）
```

### <a class="reference-link" name="Access%20Token%EF%BC%9A"></a>Access Token：

当线程与[安全对象](https://docs.microsoft.com/zh-cn/windows/win32/secauthz/securable-objects)交互或尝试执行需要特权的系统任务时，系统使用访问令牌来标识用户，访问令牌包括用户的SID、所在组的SID等等信息：

```
The security identifier (SID) for the user's account
SIDs for the groups of which the user is a member
A logon SID that identifies the current logon session
A list of the privileges held by either the user or the user's groups
An owner SID
The SID for the primary group
The default DACL that the system uses when the user creates a securable object without specifying a security descriptor
The source of the access token
Whether the token is a primary or impersonation token
An optional list of restricting SIDs
Current impersonation levels
Other statistics
```

### <a class="reference-link" name="Security%20Descriptors%E5%AE%89%E5%85%A8%E6%8F%8F%E8%BF%B0%E7%AC%A6"></a>Security Descriptors安全描述符

SID（Security Identifiers）即安全描述符。<br>
安全描述符标识对象的所有者，并包含以下访问控制列表：<br>
1、Discretionary Access Control List (DACL) 自由访问控制列表<br>
2、System Access Control List (SACL) 系统访问控制列表<br>
每一种控制列表中都存在若干条ACE（Access Control Entries）

[![](https://p2.ssl.qhimg.com/t017636a5352facc9a1.jpg)](https://p2.ssl.qhimg.com/t017636a5352facc9a1.jpg)

用[https://wenku.baidu.com/view/dba5b16e1eb91a37f1115cec.html这个链接下的一个图可以很清晰的说明什么是安全描述符：](https://wenku.baidu.com/view/dba5b16e1eb91a37f1115cec.html%E8%BF%99%E4%B8%AA%E9%93%BE%E6%8E%A5%E4%B8%8B%E7%9A%84%E4%B8%80%E4%B8%AA%E5%9B%BE%E5%8F%AF%E4%BB%A5%E5%BE%88%E6%B8%85%E6%99%B0%E7%9A%84%E8%AF%B4%E6%98%8E%E4%BB%80%E4%B9%88%E6%98%AF%E5%AE%89%E5%85%A8%E6%8F%8F%E8%BF%B0%E7%AC%A6%EF%BC%9A)

[![](https://p5.ssl.qhimg.com/t016a6a0495158eccd4.png)](https://p5.ssl.qhimg.com/t016a6a0495158eccd4.png)

可以看到安全描述符由Header、SID和DACL、SACL组成

#### <a class="reference-link" name="DACL"></a>DACL

高级安全设置中的权限就是DACL的列表

[![](https://p0.ssl.qhimg.com/t018e83efa56cc41916.png)](https://p0.ssl.qhimg.com/t018e83efa56cc41916.png)

#### <a class="reference-link" name="SACL"></a>SACL

高级安全设置中的审核就是SACL的列表

[![](https://p4.ssl.qhimg.com/t01350f54d20f037719.png)](https://p4.ssl.qhimg.com/t01350f54d20f037719.png)

其中红色圈出来的每一条都是一条ACE

#### <a class="reference-link" name="ACE"></a>ACE

ACE是针对特定用户或特定组的单个权限授予（或拒绝权利）的配置结构。ACE有许多不同类型，但是在Active Directory的权限中，只有四种不同的含义，两种分别用于授予和拒绝权限。

1、Access Allowed ACE：

[![](https://p3.ssl.qhimg.com/t01433483786957fa36.jpg)](https://p3.ssl.qhimg.com/t01433483786957fa36.jpg)

这种类型的ACE类型始终为0，设计目的是为了将权限轻松的分配给整个对象。ACE Flags确定这是继承权限还是显式给定的权限。所有此对象的子对象都会继承为ACE Type为0。

2、Access Allowed Object ACE:

[![](https://p2.ssl.qhimg.com/t019b76ee44976bebcb.jpg)](https://p2.ssl.qhimg.com/t019b76ee44976bebcb.jpg)

此类ACE的类型始终为5，用于指定对象的某些属性的权限

3、Access Denied ACE

[![](https://p3.ssl.qhimg.com/t01665353b2c6bc8c14.jpg)](https://p3.ssl.qhimg.com/t01665353b2c6bc8c14.jpg)

此类ACE的值始终为1，用于简单的撤销整个对象的权限。ACE标志确定这是继承还是显示分配的撤销权限，并且所有的子对象都会继承这个权限。

4、Access Denied Object ACE

[![](https://p5.ssl.qhimg.com/t01c5774a917af0189e.jpg)](https://p5.ssl.qhimg.com/t01c5774a917af0189e.jpg)

此类ACE的类型始终为6，此对象可以撤销ACE特殊权限或有限的权限，例如针对某些属性撤销，这里提供的有和类型为5的ACE相同的例子（Object Type GUID），Flags字段指示是否存在对象类型字段或者继承类型字段，或者两者都有。

#### <a class="reference-link" name="Access%20Mask"></a>Access Mask

在ACE中有Access Mask这个字段，它代表着此条ACE所对应的权限，比如完全控制（GenericAll）、修改密码（ResetPassword）、写入属性（WriteMembers）等等。

[![](https://p1.ssl.qhimg.com/t018a65d9da31dcfba0.jpg)](https://p1.ssl.qhimg.com/t018a65d9da31dcfba0.jpg)

#### <a class="reference-link" name="Trustees"></a>Trustees

Trustees的意思为受委托人，受托者是一个ACE所应用到的用户账户，组账户或者是登录会话。也就是说，谁是某一个ACE的受托者，那么这条ACE中的Access Mask所对应的权限（可能是拒绝可能是通过）就会赋予受托者。比如下面这一条的受委托人实际上就是zhangs账号。

[![](https://p0.ssl.qhimg.com/t01ac01b3a7338c0be2.jpg)](https://p0.ssl.qhimg.com/t01ac01b3a7338c0be2.jpg)

### <a class="reference-link" name="%E5%AE%89%E5%85%A8%E6%8F%8F%E8%BF%B0%E7%AC%A6%E6%9E%9A%E4%B8%BE"></a>安全描述符枚举

上面说了什么是安全描述符，那么安全描述符枚举就是在域中如何去枚举某个用户或者是某个域内对象的安全描述符的过程。<br>
通过.NET中的System.DirectoryServices.DirectorySearcher和System.DirectoryServices.SecurityMasks类可以对域内的安全描述符进行枚举，比如下面的这段powershell代码就可以枚举域内用户xiaom的ACE：

```
$Searcher = New-Object System.DirectoryServices.DirectorySearcher('(samaccountname=xxm)')
$Searcher.SecurityMasks = [System.DirectoryServices.SecurityMasks]::Dacl -bor [System.DirectoryServices.SecurityMasks]::Owner
$Result = $Searcher.FindOne()
$Result.Properties.ntsecuritydescriptor[0].gettype()
$ADSecurityDescriptor = New-Object System.DirectoryServices.ActiveDirectorySecurity
$ADSecurityDescriptor.SetSecurityDescriptorBinaryForm($Result.Properties.ntsecuritydescriptor[0])
$ADSecurityDescriptor
$ADSecurityDescriptor.Access
```

这里枚举的是安全描述符中的DACL中的每一个ACE（一共13条，和DACL中对应）：

[![](https://p5.ssl.qhimg.com/t01022949a0b6997c76.png)](https://p5.ssl.qhimg.com/t01022949a0b6997c76.png)

Powerviewer遍历:<br>
在Powerview的结果中不是根据每一条ACE来显示的，而是把每一个ACE中的每一个权限单独显示一条，所以结果的个数不等于DACL列表中的数量。

```
. .\powerview.ps1 Get-DomainObjectAcl -Identity xxm -ResolveGUIDs
```

[![](https://p4.ssl.qhimg.com/t012b9020115cad2cdc.png)](https://p4.ssl.qhimg.com/t012b9020115cad2cdc.png)

任何经过域验证的用户都可以枚举默认域中大多数对象的安全描述符。

### <a class="reference-link" name="%E7%BA%BF%E7%A8%8B%E4%B8%8E%E5%AE%89%E5%85%A8%E5%AF%B9%E8%B1%A1%E4%B9%8B%E9%97%B4%E7%9A%84%E4%BA%A4%E4%BA%92%EF%BC%9A"></a>线程与安全对象之间的交互：

在Access check中，系统将线程访问令牌中的安全信息与安全对象安全描述符中的安全信息进行比较。每一个进程都有一个primary token，用于描述与该进程关联的用户账户的安全上下文。默认情况下，当进程的线程与安全对象进行交互时，系统将使用primary token。<br>
系统检查对象的DACL，查找应用于用户的ACE，并从线程的访问令牌中分组SID，系统会检查每个SID，知道授予或拒绝访问，或者知道没有其他ACE要检查为止。

[![](https://p2.ssl.qhimg.com/t01dbe52559ce1da278.jpg)](https://p2.ssl.qhimg.com/t01dbe52559ce1da278.jpg)

### <a class="reference-link" name="The%20Security%20Reference%20Monitor(SRM%20%E5%AE%89%E5%85%A8%E5%8F%82%E8%80%83%E7%9B%91%E8%A7%86%E5%99%A8)"></a>The Security Reference Monitor(SRM 安全参考监视器)

The Security Reference Monitor直译为SRM 安全参考监视器，在ACL中排列顺序继承等等都可能影响最后的结果，而SRM就是起到对ACE顺序的评估作用。可参考：<br>[https://networkencyclopedia.com/security-reference-monitor/](https://networkencyclopedia.com/security-reference-monitor/)<br>[https://ldapwiki.com/wiki/Security%20Reference%20Monitor](https://ldapwiki.com/wiki/Security%20Reference%20Monitor)<br>
当登录的用户访问对象时，安全性参考监视器将检查对象的安全性描述符，以查看MSFT访问令牌中列出的SID是否与ACE条目匹配。如果存在匹配项，则匹配ACE中列出的安全权限将应用于该用户。<br>
当“域管理员”组的成员请求更改用户密码的能力时，SRM必须决定是否允许该请求。SRM会评估目标用户的DACL，确定“域管理员”组（进而是该组的成员）对用户具有完全控制权。<br>
评估对象的DACL时，SRM将按规范顺序读取ACE，ACE的排序如下：<br>
1.明确定义的DENY ACE。<br>
2.明确定义的ALLOW ACE。<br>
3.继承的DENY ACE。<br>
4.继承的ALLOW ACE。<br>
SRM这个东西知道它的作用就可以了，不需要太深究。<br>
可参考：[https://docs.microsoft.com/zh-cn/windows/win32/secauthz/dacls-and-aces](https://docs.microsoft.com/zh-cn/windows/win32/secauthz/dacls-and-aces)



## 0x02 特殊权限的实例

ACL是一个访问控制列表，是整个访问控制模型（ACM）的实现的总称。所以这里说的特殊权限是指一些非常有利用价值的权限：

```
GenericAll
GenericWrite
WriteOwner(修改所有者)
WriteDACL：写DACL（有一个解释是WriteDACL是在攻击链中启用其他权利的权利）
AllExtendedRights
AddMembers：将任意用户、组或计算机添加到目标组。
ForceChangePassword：强制更改密码，在不知道当前密码的情况下更改目标用户的密码。
```

### <a class="reference-link" name="GenericAll"></a>GenericAll

GenericAll在安全描述符中的Access Mask中进行标识，是包含了所有其他权限的权限。授予对目标对象的完全控制权，包括WriteDacl 和 WriteOwner 特权。可以使用PowerView中的Add-DomainObjectAcl进行利用。下面举例看一下如何给一个User对象添加一条GenericAll的ACE

#### <a class="reference-link" name="GenericAll%20on%20User"></a>GenericAll on User

使用zhangs账户和xxm账户做演示：<br>
两个账户的SID分别为：

```
zhangs:
 S-1-5-21-3305457972-2547556381-742707129-1604
 xxm:
 S-1-5-21-3305457972-2547556381-742707129-1105
```

这里使用zhangs账户，所在的主机是win2012，然后使用PowerView的函数Get-ObjectACL查看对zhangs具有GenericAll权限的项

```
Get-ObjectAcl -SamAccountName zhangs -ResolveGUIDs | ? `{`$_.ActiveDirectoryRights -eq "GenericAll"`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019bf9c89de80a7fb2.png)

在看一下xxm的

```
Get-ObjectAcl -SamAccountName xxm -ResolveGUIDs | ? `{`$_.ActiveDirectoryRights -eq "GenericAll"`}`
```

[![](https://p1.ssl.qhimg.com/t01a17a558ef4827494.png)](https://p1.ssl.qhimg.com/t01a17a558ef4827494.png)

然后在域控dc2012上设置xxm账户的DACL,添加对xxm的完全控制(GenericAll)权限，也可以使用powerviewer命令：

```
Add-DomainObjectAcl -TargetIdentity xxm  -PrincipalIdentity zhangs -Rights All -Verbose
```

[![](https://p3.ssl.qhimg.com/t01b6eb0ce27e506526.png)](https://p3.ssl.qhimg.com/t01b6eb0ce27e506526.png)

再在win2012上使用之前的命令查看ActiveDirectoryRights属性等于GenericAll的acl发现多了一条

[![](https://p1.ssl.qhimg.com/t01157b04f7fabe3241.png)](https://p1.ssl.qhimg.com/t01157b04f7fabe3241.png)

这条ACL的含义是：<br>
zhangs账户对xxm账户具有完全管理(GenericAll)权限<br>
在设置ACL之前和设置之后使用zhangs账户权限设置xxm账户的密码可以看到区别(设置完成之后会立即生效)

```
net user xxm admin123! /domain
```

[![](https://p1.ssl.qhimg.com/t0135d284ebd1fcf91e.png)](https://p1.ssl.qhimg.com/t0135d284ebd1fcf91e.png)

此时再使用已经修改的密码结合runas命令就可以直接创建一个xxm权限的cmd窗口：

```
runas /noprofile /user:test\xxm cmd
```

运行之后会弹出一个xxm权限的cmd窗口，即可使用xxm权限执行任意命令

[![](https://p5.ssl.qhimg.com/t01d608deaf2b926fdb.png)](https://p5.ssl.qhimg.com/t01d608deaf2b926fdb.png)

#### <a class="reference-link" name="GenericAll%20on%20Group"></a>GenericAll on Group

环境和上文相同，GenericAll on Group说的是对一个组有GenericAll权限，查看用户组domain admins：

```
Get-NetGroup "domain admins"
```

[![](https://p3.ssl.qhimg.com/t01c9d6598b9561307c.png)](https://p3.ssl.qhimg.com/t01c9d6598b9561307c.png)

此时zhangs和xxm均为域内普通权限用户，然后在域管理员组domain admins的DACL中加入zhangs的GenericAll权限：

```
Add-DomainObjectAcl  -TargetIdentity "domain admins" -PrincipalIdentity xiaom -Rights  all -Verbose
```

[![](https://p1.ssl.qhimg.com/t01baa8c200335bc570.png)](https://p1.ssl.qhimg.com/t01baa8c200335bc570.png)

然后再win2012上使用命令查看domain admins的权限

```
Get-ObjectAcl  -ResolveGUIDs| ? `{`$_.objectdn -eq "CN=Domain  Admins,CN=Users,DC=test,DC=local"`}`
```

可以看到在结果中有一条SID为zhangs的SID，权限为GenericAll

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016bc4900a13410500.png)

然后尝试将xxm加入domain admins组：

```
net group "domain admins" xxm /add /domain
```

可以看到已经成功将xxm加入管理员组,然后再将xxm移除出domain admins了，并将DACL中的内容删除之后再尝试加入，发现已经被拒绝。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0173b0f2cc0064380f.png)

在zhangs具有这个权限的时候使用Powerviewer能够达到相同的添加用户到某个组的目的，不过使用net命令更方便一点

```
Add-DomainGroupMember -Identity 'Domain Admins' -Members 'test'
```

#### <a class="reference-link" name="GenericAll/GenericWrite/Write%20on%20Computer"></a>GenericAll/GenericWrite/Write on Computer

这个权限能够对Computer的属性进行改写，利用方式是结合Kerberos RDBC来进行攻击这个具有可写权限的计算机。比如此时对Win2012这台主机具有写权限，那么可以使用Powermad工具创建一个假的域内主机testrbcd，然后将Win2012主机的msDS-AllowedToActOnBehalfOfOtherIdentity字段设置为testrbcd$

```
Set-ADComputer win2012 -PrincipalsAllowedToDelegateToAccount testrbcd$
```

然后使用Rubeus工具获取能够访问win2012特定SPN的票据。详情可参考：[http://blog.leanote.com/post/ambition/95dac75ccad8。](http://blog.leanote.com/post/ambition/95dac75ccad8%E3%80%82)

### <a class="reference-link" name="GenericWrite"></a>GenericWrite

GenericWrite也是在Access Mask中进行标识，此权限能够更新目标对象的属性值，可以使用PowerView中的Set-DomainObject方法设置目标属性的值。

[![](https://p5.ssl.qhimg.com/t0119d97f69f3fd5e50.png)](https://p5.ssl.qhimg.com/t0119d97f69f3fd5e50.png)

### <a class="reference-link" name="WriteDacl"></a>WriteDacl

WriteDacl允许委托人修改受影响对象的DACL。这意味着攻击者可以添加或删除特定的访问控制项，从而使他们可以授予自己对对象的完全访问权限。因此，WriteDacl是在链中启用其他权利的权利。

[![](https://p4.ssl.qhimg.com/t015d17a377b571dfc8.jpg)](https://p4.ssl.qhimg.com/t015d17a377b571dfc8.jpg)

### <a class="reference-link" name="Self%20(Self-Membership)%20on%20Group"></a>Self (Self-Membership) on Group

这条权限指的是某个账户能够把自身添加到某个组的权限(需要在某个组的高级权限中添加ACE，也就是说针对的是组对象)

[![](https://p1.ssl.qhimg.com/t01f556acdc2a61ba88.png)](https://p1.ssl.qhimg.com/t01f556acdc2a61ba88.png)

添加完之后可以使用zhangs的权限将zhangs自身添加到Domain Admins组：

```
net group "domain admins" zhangs /add /domain
```

[![](https://p3.ssl.qhimg.com/t01e4f563ab4b16f997.png)](https://p3.ssl.qhimg.com/t01e4f563ab4b16f997.png)

### <a class="reference-link" name="WriteProperty%20(Self-Membership)"></a>WriteProperty (Self-Membership)

WriteProperty直译为写所有权。这个权限利用针对的对象为组对象，能够赋予账户对于某个组的可写权限，在Domain Admins组里设置zhangs账户的WriteProperty权限：

[![](https://p5.ssl.qhimg.com/t018014f2f979f8ea7d.png)](https://p5.ssl.qhimg.com/t018014f2f979f8ea7d.png)

然后使用zhangs账户权限可以将xxm账户加入Domain Admins组：

```
net group "domain admins" xxm /add /domain
```

[![](https://p0.ssl.qhimg.com/t01959c644b4ce95c48.png)](https://p0.ssl.qhimg.com/t01959c644b4ce95c48.png)

### <a class="reference-link" name="WriteProperty%20on%20Group"></a>WriteProperty on Group

WriteProperty on Group说的是对一个组具有WriteProperty权限的情况下，“写入全部属性”除了WriteProperty还包括了其他的权限：<br>
CreateChild, DeleteChild, Self, WriteProperty, ExtendedRight, GenericRead, WriteDacl, WriteOwner

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ca77b82203ed3507.png)

在Domain Admins组的列表中添加写入全部属性，会生成一条新的ACE

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0182a68d9a2e0c56c3.png)

访问被标记为特殊，没有实际显示具体权限，测试添加此条ACE前后：

[![](https://p1.ssl.qhimg.com/t01554a8ffb24849f11.png)](https://p1.ssl.qhimg.com/t01554a8ffb24849f11.png)

### <a class="reference-link" name="WriteOwner"></a>WriteOwner

WriteOwner权限允许委托人修改对象的安全描述符的所有者部分。也就是说，假如用户A对administrator用户有这个权限，那么A能利用这个权限给自己附加其他的权限。

[![](https://p0.ssl.qhimg.com/t01cb30299dd03b9175.jpg)](https://p0.ssl.qhimg.com/t01cb30299dd03b9175.jpg)

Self (Self-Membership) on Group



## 0x03 与ACL相关的攻击方式

### <a class="reference-link" name="Exchange%E7%9B%B8%E5%85%B3"></a>Exchange相关

#### <a class="reference-link" name="Organization%20Management%E7%BB%84"></a>Organization Management组

[![](https://p4.ssl.qhimg.com/t0157723ccc6414b546.png)](https://p4.ssl.qhimg.com/t0157723ccc6414b546.png)

Organization Management组的的组描述为：<br>
此管理角色组成员具有对 Exchange 对象及其在 Exchange 组织中的属性进行管理的权限。另外，成员还可以代表组织中的角色组和管理角色。<br>
在安装Exchange时会创建这个组，赋予其访问Exchange相关活动的权限。除了能访问这些Exchange设置选项之外，该组的成员还可以修改其他Exchange安全组的组成员关系。比如Exchange Trusted Subsystem安全组。这个组是Exchange Windows Permissions安全组的成员之一。<br>
Exchange Windows Permissions安全组具备当前域对象的writeDACL权限。也就是说只要成为Organization Management组的成员，我们就可以提升成为域管理员权限。复现流程可以参考：

[https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-%E4%BD%BF%E7%94%A8Exchange%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%AD%E7%89%B9%E5%AE%9A%E7%9A%84ACL%E5%AE%9E%E7%8E%B0%E5%9F%9F%E6%8F%90%E6%9D%83/](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-%E4%BD%BF%E7%94%A8Exchange%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%AD%E7%89%B9%E5%AE%9A%E7%9A%84ACL%E5%AE%9E%E7%8E%B0%E5%9F%9F%E6%8F%90%E6%9D%83/)

#### <a class="reference-link" name="NTLMRelay%E4%B8%8EDCSync"></a>NTLMRelay与DCSync

NTLMRelay是一个已经存在了很久的攻击方式，在2018年和2019年分别爆出了关于Exchange的SSRF漏洞（CVE-2018-8581）+NTLMRelay攻击、CVE-2019-1040 NTLM协议漏洞的两种利用方式，传播最广泛的利用方式就是通过这两个漏洞对域对象的ACL进行改写，实现DCSync，从而获取krbtgt账户的HASH值。关于CVE-2018-8581和CVE-2019-1040在这里就不再说明，可以参考：<br>[https://paper.seebug.org/833/](https://paper.seebug.org/833/)<br>[https://dirkjanm.io/abusing-exchange-one-api-call-away-from-domain-admin/?from=timeline&amp;isappinstalled=0](https://dirkjanm.io/abusing-exchange-one-api-call-away-from-domain-admin/?from=timeline&amp;isappinstalled=0)<br>[https://mp.weixin.qq.com/s/NEBi8NflfaEDL2qw1WIqZw](https://mp.weixin.qq.com/s/NEBi8NflfaEDL2qw1WIqZw)<br>
下面主要说一下DCSync与ACL的关系。

##### <a class="reference-link" name="DCSync%E9%9C%80%E8%A6%81%E4%BB%80%E4%B9%88%E6%9D%83%E9%99%90"></a>DCSync需要什么权限

一个域内用户想要通过DCSync获取krbtgt的HASH值需要在域对象或者是域内的高权限组中有以下三种权限的其中一个：<br>
复制目录更改Replicating Directory Changes (DS-Replication-Get-Changes) 复制目录更改所有Replicating Directory Changes All (DS-Replication-Get-Changes-All)（Exchange用的就是这个） 正在复制筛选集中的目录更改Replicating Directory Changes In Filtered Set (rare, only required in some environments)<br>
这几个权限在DACL的设置页是可以看到的：

[![](https://p5.ssl.qhimg.com/t014dcea433fe68372e.jpg)](https://p5.ssl.qhimg.com/t014dcea433fe68372e.jpg)

##### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BB%99%E4%B8%80%E4%B8%AA%E7%94%A8%E6%88%B7%E6%B7%BB%E5%8A%A0DCSync%E6%9D%83%E9%99%90"></a>如何给一个用户添加DCSync权限

除了上面的利用方式之外，如果想单纯的尝试给一个账号添加DCSync权限，或者是在有了高权限账号的情况下希望存留DCSync的后门，可以使用powerviewer.ps1的Add-DomainObjectAcl函数实现：

```
Add-DomainObjectAcl -TargetIdentity "DC=test,DC=local" -PrincipalIdentity zhangs -Rights DCSync
```

[![](https://p4.ssl.qhimg.com/t01866180c52cbf0360.png)](https://p4.ssl.qhimg.com/t01866180c52cbf0360.png)

执行之后会在域对象（”DC=test,DC=local”）的DACL中添加一条主体为zhangs的权限为”复制目录更改”的ACE：

[![](https://p5.ssl.qhimg.com/t01f09ee1ed7fe2caa3.png)](https://p5.ssl.qhimg.com/t01f09ee1ed7fe2caa3.png)

然后使用zhangs进行DCSync，这里可以看到添加前后的变化：

```
.\mimikatz.exe "lsadump::dcsync /user:test\krbtgt" "exit"
```

[![](https://p5.ssl.qhimg.com/t01a3f9f4583f18b87e.png)](https://p5.ssl.qhimg.com/t01a3f9f4583f18b87e.png)

注意，这里复制目录更改权限的ACE是添加在域对象DC=test,DC=local上的。

### <a class="reference-link" name="Invoke-ACLPwn"></a>Invoke-ACLPwn

运行时需要.NET 3.5环境，Windows Server 2012安装遇到报错，最后的解决方法(需要在网上下载SxS的安装包[https://pan.baidu.com/share/init?surl=kDgdYerM0lVB32Q_IEqLUw提取码：gwzk)：](https://pan.baidu.com/share/init?surl=kDgdYerM0lVB32Q_IEqLUw%E6%8F%90%E5%8F%96%E7%A0%81%EF%BC%9Agwzk)%EF%BC%9A)

```
dism.exe /online /enable-feature /all /featurename:NetFX3 /Source:F:\Sources\SxS\
```

GitHub地址：[https://github.com/fox-it/Invoke-ACLPwn](https://github.com/fox-it/Invoke-ACLPwn)<br>
背景信息在发布者博客上：[https://blog.fox-it.com/2018/04/26/escalating-privileges-with-acls-in-active-directory/](https://blog.fox-it.com/2018/04/26/escalating-privileges-with-acls-in-active-directory/)<br>
环境需要：

```
.NET 3.5 + sharphound.exe + mimikatz.exe
```

用法示例：

```
.\Invoke-ACL.ps1 -SharpHoundLocation .\sharphound.exe -NoDCSync
.\Invoke-ACL.ps1 -SharpHoundLocation .\sharphound.exe -mimiKatzLocation .\mimikatz.exe
.\Invoke-ACL.ps1 -SharpHoundLocation .\sharphound.exe -mimiKatzLocation .\mimikatz.exe -userAccountToPwn 'Administrator'
.\Invoke-ACL.ps1 -SharpHoundLocation .\sharphound.exe -mimiKatzLocation .\mimikatz.exe -LogToFile
.\Invoke-ACL.ps1 -SharpHoundLocation .\sharphound.exe -mimiKatzLocation .\mimikatz.exe -NoSecCleanup
.\Invoke-ACL.ps1 -SharpHoundLocation .\sharphound.exe -mimiKatzLocation .\mimikatz.exe -Username 'testuser' -Domain 'xenoflux.local' -Password 'Welcome01!'
```

使用第一条标识了-NoDCSync（不会做DCSync的动作，只判断是否能够存在能够DCSync的权限）的命令：

[![](https://p5.ssl.qhimg.com/t01e5278a28029caf2d.png)](https://p5.ssl.qhimg.com/t01e5278a28029caf2d.png)

提示Got WriteDACL permissions.如果加上mimikatz.exe一起使用,可以看到直接获取了krbtgt的HASH值，也就是说已经可以直接生成黄金票据了：

[![](https://p1.ssl.qhimg.com/t019bbd1564b6fd1eb7.png)](https://p1.ssl.qhimg.com/t019bbd1564b6fd1eb7.png)

但是这个工具经过实际测试只适用于小型的域控，在有上百万条ACL的域内会出现跑了几天也跑不出结果的情况

### <a class="reference-link" name="%E9%92%88%E5%AF%B9DACL%E7%9A%84%E9%9A%90%E8%BA%AB%E6%96%B9%E5%BC%8F"></a>针对DACL的隐身方式

通过隐藏账户可以掩盖主体本身，阻止防御者轻易的发现谁实际上拥有ACE中指定的权限。这种方式主要应对的是对于高危的ACL进行扫描行为。

#### <a class="reference-link" name="%E9%9A%90%E8%97%8F%E7%94%A8%E6%88%B7"></a>隐藏用户

1、将要隐藏的用户所有者改为攻击者或者攻击者控制的账户<br>
2、设置一条拒绝完全控制的ACE

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0131d90c456630185e.png)

点击应用之后所有用户都无法在外部访问查看此账户的ACL，包括administrator：

```
Get-DomainObjectAcl -Identity hideuser -domain test.local -Resolve
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eb20c3f565eeb514.png)

但是如上图所示，在ADSI编辑器中还是可以看到的，如果想要在ADSI编辑器中也看不到，那么就要将主体设置为用户本身，或者其他攻击者控制的账户：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019eaff480016f9185.png)

点击应用可以看到，即使在ADSI编辑器中也无法查询到：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0142962c261ca5d444.png)

同时在AD用户和计算机中用户类型会变为未知：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c57e8706b7b3edb7.png)

此时这个账号无法删除和访问属性，但是仍然能够正常使用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eddd901c76f40e21.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0171ef4224bbeee40c.jpg)

#### <a class="reference-link" name="%E9%9A%90%E8%97%8FOU%E4%B8%AD%E6%89%80%E6%9C%89%E7%9A%84%E5%AD%90%E5%AF%B9%E8%B1%A1"></a>隐藏OU中所有的子对象

直接添加一条拒绝Everyone的列出内容权限

[![](https://p3.ssl.qhimg.com/t01b59377cd1ee9c404.png)](https://p3.ssl.qhimg.com/t01b59377cd1ee9c404.png)

然后再查看这个OU的时候会发现所有的用户都不显示。

[![](https://p1.ssl.qhimg.com/t01d1e7e46b9111d680.png)](https://p1.ssl.qhimg.com/t01d1e7e46b9111d680.png)

同样，通过powerviewer也无法查看ACL：

### <a class="reference-link" name="%E5%BD%A2%E5%BD%A2%E8%89%B2%E8%89%B2%E7%9A%84ACL%E5%90%8E%E9%97%A8"></a>形形色色的ACL后门

#### <a class="reference-link" name="AdminSDHolder"></a>AdminSDHolder

AdminSDHolder会将自身的ACL列表每隔一个小时向受保护的组中同步，所以如果在AdminSDHolder中添加一个ACE作为后门，则受保护的组中将会一直被同步策略。受保护的组有[https://docs.microsoft.com/en-us/previous-versions/technet-magazine/ee361593(v=msdn.10)?redirectedfrom=MSDN：](https://docs.microsoft.com/en-us/previous-versions/technet-magazine/ee361593(v=msdn.10)?redirectedfrom=MSDN%EF%BC%9A)

[![](https://p5.ssl.qhimg.com/t01f29553aa20ce68c4.png)](https://p5.ssl.qhimg.com/t01f29553aa20ce68c4.png)

在AdminSDHolder的DACL中设置一条主体为zhangs，权限为完全控制的ACE

```
Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,CN=System,DC=test,DC=local" -PrincipalIdentity zhangs -Rights All
```

[![](https://p4.ssl.qhimg.com/t01f6b653c834f2a181.png)](https://p4.ssl.qhimg.com/t01f6b653c834f2a181.png)

不过这样也有一个坏处就是所有的受保护组的ACL中都会被添加上这一条作为后门的ACE，隐藏其中一个账户并不能起到作用，所以还是比较容易被发现的。并且添加时会产生一条ID为5136的事件日志。

[![](https://p0.ssl.qhimg.com/t016237847e6e1ecd36.png)](https://p0.ssl.qhimg.com/t016237847e6e1ecd36.png)

也可以通过修改注册表设置推送时间，这里设置为60s：

```
reg add hklm\SYSTEM\CurrentControlSet\Services\NTDS\Parameters /v AdminSDProtectFrequency /t REG_DWORD /d 60
```

60秒之后就可以使用xiaom权限添加任意用户到domain admins组<br>[http://www.selfadsi.org/extended-ad/ad-permissions-adminsdholder.htm](http://www.selfadsi.org/extended-ad/ad-permissions-adminsdholder.htm)<br>[https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-AdminSDHolder/](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-AdminSDHolder/)

#### <a class="reference-link" name="%E5%85%B3%E4%BA%8ELAPS%E7%9A%84%E9%9A%90%E8%97%8F%E5%90%8E%E9%97%A8"></a>关于LAPS的隐藏后门

LAPS的全称是Local Administrator Password Solution，主要作用是将域内主机的本地管理员密码存储在LDAP中，作为计算机账户的一个机密属性，配合GPO实现自动定期修改密码，设置密码长度、强度等。LAPS通过首先将Active Directory架构扩展为包括两个新字段ms-MCS-AdmPwd（密码本身）和 ms-MCS-AdmPwdExpirationTime（密码过期时）来完成其方法。<br>
具体的配置和如何查询明文密码可以参考：[http://drops.xmd5.com/static/drops/tips-10496.html](http://drops.xmd5.com/static/drops/tips-10496.html)<br>
此时的环境：一个配置了LAPS的testwin7主机（属于testou）、一个域中的普通的测试账号zhangs

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014d2272f195396393.png)

此时通过命令查看testwin7主机的本地administrator密码：

```
Get-AdmPwdPassword –ComputerName testwin7
```

[![](https://p1.ssl.qhimg.com/t01547ead5f490faef4.png)](https://p1.ssl.qhimg.com/t01547ead5f490faef4.png)

在zhangs登录的主机上使用LAPS UI尝试获取testwin7的本地密码没有成功：

[![](https://p3.ssl.qhimg.com/t0119e241303beabb66.png)](https://p3.ssl.qhimg.com/t0119e241303beabb66.png)

然后在testou中添加zhangs的读取密码的权限：

```
Set-AdmPwdReadPasswordPermission -Identity testou -AllowedPrincipals zhangs
```

此时再在zhangs主机上尝试获取testwin7密码:

[![](https://p5.ssl.qhimg.com/t019c3980c92dda96d9.png)](https://p5.ssl.qhimg.com/t019c3980c92dda96d9.png)

能够成功获取，但是此时的zhangs的权限是能够通过Find-AdmPwdExtendedRights排查到的：

```
Find-AdmPwdExtendedRights -Identity testou -IncludeComputers | fl
```

[![](https://p2.ssl.qhimg.com/t0126def331d80abe53.png)](https://p2.ssl.qhimg.com/t0126def331d80abe53.png)

解决方法是在testou中新建一个msImaging-PSPs类型的对象testmspsps，此类容器的权限不能被Find-AdmPwdExtendedRights所遍历，同时将testwin7移动到testmspsps中，然后在testmspsps的ACL中设置主体为zhangs的完全控制权限：

[![](https://p5.ssl.qhimg.com/t01e2f1fc2896140ffb.png)](https://p5.ssl.qhimg.com/t01e2f1fc2896140ffb.png)

[![](https://p2.ssl.qhimg.com/t016cef84ba6816c1f0.png)](https://p2.ssl.qhimg.com/t016cef84ba6816c1f0.png)

此时在zhangs中就可以获取testwin7的密码，并且不会被Find-AdmPwdExtendedRights这个命令遍历到：

[![](https://p4.ssl.qhimg.com/t0186d5f301635f7fe6.png)](https://p4.ssl.qhimg.com/t0186d5f301635f7fe6.png)

[![](https://p1.ssl.qhimg.com/t0194a61c75997cd775.png)](https://p1.ssl.qhimg.com/t0194a61c75997cd775.png)

这种方式的缺点在于需要移动域内主机所属的组。

#### <a class="reference-link" name="%E9%92%88%E5%AF%B9%E5%9F%9F%E5%AF%B9%E8%B1%A1%E7%9A%84%E5%90%8E%E9%97%A8"></a>针对域对象的后门

上面所说的后门都是针对User Objects或者Group Objects的，这里要说的是针对Domain Objects。通过在Domain对象的DACL中添加ACE能够赋予用户特定的权限。因为实现这个操作需要较高权限，所以可以使用，这里使用powerviewer.ps1的Add-DomainObjectAcl函数实现：

```
Add-DomainObjectAcl -TargetIdentity "DC=test,DC=local" -PrincipalIdentity zhangs -Rights DCSync
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019f425a334b405d21.png)

然后使用zhangs进行DCSync，这里可以看到添加前后的变化：

```
.\mimikatz.exe "lsadump::dcsync /user:test\krbtgt" "exit"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016e31453adca7940e.png)

#### <a class="reference-link" name="%E9%92%88%E5%AF%B9%E7%BB%84%E7%AD%96%E7%95%A5%E5%AF%B9%E8%B1%A1%E7%9A%84ACL"></a>针对组策略对象的ACL

GPO中的ACL同样能够进行权限维持等操作，修改SYSVOL的属性，意味着主体可以修改GPO的设置。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e31369f39e4bc85b.png)

以域控组的组策略为例，可以在组策略管理中的委派选项中进行设置：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f588f3b91087139e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019c985b30e4737132.png)

创建之后在对应的GPO文件夹下可以看到对应的权限：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cf6f4077b72345d6.png)



## 0x04 监测防御

在域内修改ACL时会产生ID为5136的事件日志，可以通过日志分析平台进行检测和发现，可以通过匹配ObjectDN字段判断是否存在域内关键对象的ACL被修改

[![](https://p2.ssl.qhimg.com/t011e425056e6866c1a.jpg)](https://p2.ssl.qhimg.com/t011e425056e6866c1a.jpg)

上图是AdminSDHolder组被修改时的windows事件日志。这里需要兼顾的就是对于ACL对象的选择，确定哪些是关键组，以及是否存在漏掉的关键组。如果一个域里没有配置对域控中ACL日志的检查，那么几乎是没有办法防御的。



## 0x05 小结

本文主要说明了域内的ACL相关攻击手法，有一些已经广为人知，还有一些可能很少在实际的攻击中出现，如果有更好的思路和建议欢迎探讨。在windows的安全体系中ACL是至关重要的一环，并且在本地ACL方面也有很多的利用方式，比如硬链接结合权限问题进行提权的手法，这里不再赘述。



## 参考链接：

[http://www.selfadsi.org/extended-ad/ad-permissions-adminsdholder.htm](http://www.selfadsi.org/extended-ad/ad-permissions-adminsdholder.htm)<br>[https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-AdminSDHolder/](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-AdminSDHolder/)<br>[http://www.harmj0y.net/blog/redteaming/abusing-active-directory-permissions-with-powerview/](http://www.harmj0y.net/blog/redteaming/abusing-active-directory-permissions-with-powerview/)<br>[https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf](https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf)
