> 原文链接: https://www.anquanke.com//post/id/251582 


# 再探MS-SAMR协议


                                阅读量   
                                **18960**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0177f12f5954fa96ad.jpg)](https://p3.ssl.qhimg.com/t0177f12f5954fa96ad.jpg)



作者：Loong716@[Amulab](https://github.com/Amulab)

## 0x00 前言

在前一篇《利用MS-SAMR协议修改用户密码》中介绍了利用MS-SAMR修改用户密码并还原的技巧。在本篇文章中，我们继续介绍MS-SAMR协议的一些其它利用。



## 0x01 利用

### <a class="reference-link" name="1.%20%E6%B7%BB%E5%8A%A0%E6%9C%AC%E5%9C%B0%E7%94%A8%E6%88%B7"></a>1. 添加本地用户

在渗透测试过程中，我们经常会遇到在目标机器添加账户但被杀软拦截掉的情况。现在较为通用的绕过方法是通过调用`NetUserAdd()`等API来添加用户

[![](https://p5.ssl.qhimg.com/t01e219bc5422657b4f.png)](https://p5.ssl.qhimg.com/t01e219bc5422657b4f.png)

我们同样也可以利用MS-SAMR协议中的`SamrCreateUser2InDomain()`来添加用户（其实调用MS-SAMR是`NetUserAdd()`等API的底层实现）

[![](https://p1.ssl.qhimg.com/t01895eb17c0f9b3ae8.png)](https://p1.ssl.qhimg.com/t01895eb17c0f9b3ae8.png)

需要注意的有两点，一点是Windows操作系统（域控除外）中的“域”分为**内置域（Builtin Domain）**和**账户域（Account Domain）**
<li>
**内置域（Builtin Domain）**：包含在安装操作系统时建立的默认本地组，例如管理员组和用户组</li>
<li>
**账户域（Account Domain）**：包含用户、组和本地组帐户。管理员帐户在此域中。在工作站或成员服务器的帐户域中定义的帐户仅限于访问位于该帐户所在物理计算机上的资源</li>
因此我们需要在账户域中添加普通用户，然后在内置域中找到Administrators组，再将该用户添加到内置域中的Administrators中

第二个需要注意的是，利用`SamrCreateUser2InDomain()`添加的账户默认是禁用状态，因此我们需要调用`SamrSetInformationUser()`在用户的userAccountControl中清除禁用标志位：

```
// Clear the UF_ACCOUNTDISABLE to enable account
userAllInfo.UserAccountControl &amp;= 0xFFFFFFFE;
userAllInfo.UserAccountControl |= USER_NORMAL_ACCOUNT;
userAllInfo.WhichFields |= USER_ALL_USERACCOUNTCONTROL;
RtlInitUnicodeString(&amp;userAllInfo.NtOwfPassword, password.Buffer);

// Set password and userAccountControl
status = SamSetInformationUser(hUserHandle, UserAllInformation, &amp;userAllInfo);
```

在实现时，如果直接调用MS-SAMR的话在设置用户密码时会非常复杂，涉及到加密算法并且可能需要SMB Session Key（用impacket很好实现，但impacket不支持当前用户身份执行）

但我们可以调用samlib.dll的导出函数，在上一篇文章中提到过这些导出函数其实是封装了协议的调用，实现会更简单一些，代码Demo：[https://github.com/loong716/CPPPractice/tree/master/AddUserBypass_SAMR](https://github.com/loong716/CPPPractice/tree/master/AddUserBypass_SAMR)

[![](https://p5.ssl.qhimg.com/t0136878663716cc2ee.png)](https://p5.ssl.qhimg.com/t0136878663716cc2ee.png)

### <a class="reference-link" name="2.%20%E8%A7%A3%E5%86%B3%E5%AF%86%E7%A0%81%E8%BF%87%E6%9C%9F%E9%99%90%E5%88%B6"></a>2. 解决密码过期限制

假设在渗透测试过程中，我们收集到一台服务器的用户账户，但当想要访问目标SMB资源时，发现该账户密码已过期。此处以psexec横向为例，目标显示**STATUS_PASSWORD_MUST_CHANGE**错误：

[![](https://p0.ssl.qhimg.com/t015dc195ff2ff94aa3.png)](https://p0.ssl.qhimg.com/t015dc195ff2ff94aa3.png)

此时我们可以利用samba中的smbpasswd来修改该用户的密码

[![](https://p5.ssl.qhimg.com/t01d88dcd7473a0ab44.png)](https://p5.ssl.qhimg.com/t01d88dcd7473a0ab44.png)

修改之后使用新密码就可以正常访问目标的SMB资源了：

[![](https://p5.ssl.qhimg.com/t016a8004892b6735dc.png)](https://p5.ssl.qhimg.com/t016a8004892b6735dc.png)

实际上smbpasswd调用的是MS-SAMR的`SamrUnicodeChangePasswordUser2()`，**该方法不需要上下文句柄，并且支持SMB空会话（Null Session）调用**

[https://github.com/samba-team/samba/blob/e742661bd2507d39dfa47e40531dc1dca636cbbe/source3/libsmb/passchange.c#L192](https://github.com/samba-team/samba/blob/e742661bd2507d39dfa47e40531dc1dca636cbbe/source3/libsmb/passchange.c#L192)

[![](https://p0.ssl.qhimg.com/t0194c8477b09c7643c.png)](https://p0.ssl.qhimg.com/t0194c8477b09c7643c.png)

另外impacket之前也更新了该方法的example，并且该脚本支持hash传递：

[https://github.com/SecureAuthCorp/impacket/blob/master/examples/smbpasswd.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/smbpasswd.py)

### <a class="reference-link" name="3.%20%E4%BF%A1%E6%81%AF%E6%94%B6%E9%9B%86/%E4%BF%AE%E6%94%B9"></a>3. 信息收集/修改

MS-SAMR协议在信息收集/修改方面能做的事情很多，如枚举/修改对象的ACL、用户&amp;组信息、枚举密码策略等。此处以**枚举本地管理员组账户**为例

通常进行本地管理员组账户的枚举会调用`NetLocalGroupGetMembers()`这一API，前面提到过这类API底层也是调用MS-SAMR协议，先来看一下正常调用的过程：
<li>
**SamrConnect**：获取Server对象的句柄</li>
<li>
**SamrOpenDomain**：打开目标内置域的句柄</li>
<li>
**SamrLookupNamesInDomain**：在内置域中搜索Administrators的RID</li>
<li>
**SamrOpenAlias**：根据Administrators的RID打开别名句柄</li>
<li>
**SamrGetMembersInAlias**：枚举别名对象中的成员SID</li>
[![](https://p3.ssl.qhimg.com/t01a9239c8b5ec29d65.png)](https://p3.ssl.qhimg.com/t01a9239c8b5ec29d65.png)

此时我们如果想要开发自动化的信息收集工具（如SharpHound），那么我们需要考虑工具的通用性，比如在第3步调用`SamrLookupNamesInDomain()`时，我们需要传入**“Administrators”**，但在某些系统中管理员组的名字可能有差异，如部分非英文操作系统中该组名为**“Administradors”**，或者运维修改了本地管理员组名称，这样我们直接调用`NetLocalGroupGetMembers()`便不合适了

此时我们可以考虑优化这一操作，我们可以注意到本地管理员组在不同Windows系统上的RID始终为544

[![](https://p5.ssl.qhimg.com/t01e1e8152f8aa6ffa8.png)](https://p5.ssl.qhimg.com/t01e1e8152f8aa6ffa8.png)

那么我们可以这样调用：
<li>
**SamrConnect**：获取Server对象的句柄</li>
<li>
**SamrOpenDomain**：打开目标内置域的句柄</li>
<li>
**SamrOpenAlias**：打开RID为544对象的别名句柄</li>
<li>
**SamrGetMembersInAlias**：枚举该别名对象中的成员SID</li>
按此思路，我们可以将MS-SAMR的API利用到我们自己工具的武器化or优化上

### <a class="reference-link" name="4.%20%E6%B7%BB%E5%8A%A0%E5%9F%9F%E5%86%85%E6%9C%BA%E5%99%A8%E8%B4%A6%E6%88%B7"></a>4. 添加域内机器账户

调用`SamCreateUser2InDomain()`时指定AccountType为**USER_WORKSTATION_TRUST_ACCOUNT**可以在域内添加机器账户

```
// Create computer in domain
status = SamCreateUser2InDomain(hDomainHandle, &amp;computerName, USER_WORKSTATION_TRUST_ACCOUNT, USER_ALL_ACCESS | DELETE | WRITE_DAC, &amp;hUserHandle, &amp;grantAccess, &amp;relativeId);
```

impacket的addcomputer.py包含了该方法，因为LDAPS需要证书的不稳定所以添加了SAMR（SAMR是Windows GUI环境添加机器使用的协议）

[![](https://p3.ssl.qhimg.com/t010b2b6930836e6f38.png)](https://p3.ssl.qhimg.com/t010b2b6930836e6f38.png)

这个地方感觉还是有一些误区的，通过LDAP修改`unicodePwd`确实需要在加密的连接中操作，但LDAPS并不是必须的，像powermad.ps1在加密LDAP中添加机器账户同样可以成功，并且非常稳定

[![](https://p1.ssl.qhimg.com/t019190969d904f1e0d.png)](https://p1.ssl.qhimg.com/t019190969d904f1e0d.png)

我们实战中大多数情况下添加机器账户都是在利用基于资源约束委派时，为了拿到一个有SPN的账户所以才选择添加机器账户。但我实际测试中发现该方法并不会自动为机器账户添加SPN，而通过LDAP或其他RPC为机器账户添加SPN又感觉有些画蛇添足，只能先作为一种添加机器账户的实现方法，如果其他方法不成功时可以尝试



## 0x02 参考

[https://docs.microsoft.com/zh-cn/openspecs/windows_protocols/ms-samr/4df07fab-1bbc-452f-8e92-7853a3c7e380](https://docs.microsoft.com/zh-cn/openspecs/windows_protocols/ms-samr/4df07fab-1bbc-452f-8e92-7853a3c7e380)

[https://github.com/SecureAuthCorp/impacket/](https://github.com/SecureAuthCorp/impacket/)

[https://snovvcrash.rocks/2020/10/31/pretending-to-be-smbpasswd-with-impacket.html](https://snovvcrash.rocks/2020/10/31/pretending-to-be-smbpasswd-with-impacket.html)

[https://blog.cptjesus.com/posts/sharphoundtechnical](https://blog.cptjesus.com/posts/sharphoundtechnical)
