> 原文链接: https://www.anquanke.com//post/id/156299 


# 如何防御Mimikatz


                                阅读量   
                                **266459**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：medium.com
                                <br>原文地址：[https://medium.com/blue-team/preventing-mimikatz-attacks-ed283e7ebdd5](https://medium.com/blue-team/preventing-mimikatz-attacks-ed283e7ebdd5)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01ce92d809a7140a2e.jpg)](https://p0.ssl.qhimg.com/t01ce92d809a7140a2e.jpg)

## 一、前言

[Mimikatz](https://github.com/gentilkiwi/mimikatz)能够从内存中提取出明文形式的密码，因此在内部渗透测试或者红队行动中被广泛应用，攻击者也会在攻击活动中大量使用这款工具。尽管微软推出了一个[安全补丁](https://docs.microsoft.com/en-us/security-updates/SecurityAdvisories/2016/2871997)，该补丁同样适用于版本较老的操作系统（如Windows 2008 Server），但Mimikatz同样能正常工作，并且在许多情况下依旧能够实现横向渗透以及域提升。需要注意的是，Mimikatz只有在以特权用户（如本地管理员）的上下文中运行才能导出凭据以及密码。



## 二、Debug权限

根据微软的说法，debug（调试）权限用来确定哪些用户可以将调试器附加到任意进程或者内核上。默认情况下本地管理员组成员具备此权限。然而，除非本地管理员是个系统程序员，否则他很大概率上不需要具备该权限。

[![](https://p2.ssl.qhimg.com/t0139bce9fd6f353314.png)](https://p2.ssl.qhimg.com/t0139bce9fd6f353314.png)

图1. Debug programs权限，赋予本地管理员组成员

默认安装的Windows Server 2016并没有设置这条组策略，这意味着只有本地管理员组成员才能具备该权限。

[![](https://p5.ssl.qhimg.com/t011b4ae1f507cd5f26.png)](https://p5.ssl.qhimg.com/t011b4ae1f507cd5f26.png)

图2. 组策略中的Debug programs权限

攻击者可以在Mimikatz中执行如下命令确认是否具备该权限：

```
privilege::debug
```

[![](https://p1.ssl.qhimg.com/t01e55e18b817588bb1.png)](https://p1.ssl.qhimg.com/t01e55e18b817588bb1.png)

图3. 检查是否具备调试权限

Mimikatz需要该权限来与LSASS之类的进程交互，因此我们需要限制该权限，只赋予真正需要该权限的人，在本地管理员组中删除该权限。我们可以设置组策略，删除包含的用户或组成员，禁用`SeDebugPrivilege`：

```
Group Policy Management Editor -&gt; Windows Settings -&gt; Security Settings -&gt; Local Policies -&gt; User Rights Assignment -&gt; Debug programs -&gt; Define these policy settings:
```

[![](https://p4.ssl.qhimg.com/t0163b941fab0cbafd4.png)](https://p4.ssl.qhimg.com/t0163b941fab0cbafd4.png)

图4. 禁用SeDebugPrivilege

当全域都部署该策略后，即使攻击者成功提升成为本地管理员，也无法使用这个权限。Mimikatz会返回如下错误消息：

[![](https://p4.ssl.qhimg.com/t0100cae3a0fe9cbb68.png)](https://p4.ssl.qhimg.com/t0100cae3a0fe9cbb68.png)

图5. Mimikatz返回调试权限被禁用消息



## 三、WDiget

Windows从XP起开始引入[WDigest](https://technet.microsoft.com/pt-pt/library/cc778868%28v=ws.10%29.aspx?f=255&amp;MSPPError=-2147217396)协议，其目的是与HTTP协议配合用于身份验证。微软在多个版本的Windows中都会默认启用该协议（从Windows XP到Windows 8.0，Windowser Server 2003到Server 2012），这意味着明文密码会存储在LSASS（Local Security Authority Subsystem Service）中。Mimikatz可以与LSASS交互，使得攻击者可以通过如下命令获取这些凭据：

```
sekurlsa::wdigest
```

[![](https://p3.ssl.qhimg.com/t0167e8d6d4119df292.png)](https://p3.ssl.qhimg.com/t0167e8d6d4119df292.png)

图6. Mimikatz中的WDigest命令

微软在Windows 8.1、Windows 10、Windows Server 2012 R2以及Server 2016中默认禁用了该协议。如果用户所在的单位在使用类似Windows 7以及Windows Server 2008等老版本系统，微软也提供了一个[补丁](https://support.microsoft.com/en-us/kb/2871997)（KB2871997），允许管理员启用或者禁用WDigest协议。打上该补丁后，我们可以通过注册表来确认WDigest是否处于禁用状态。

```
HKEY_LOCAL_MACHINESystemCurrentControlSetControlSecurityProvidersWDigest
```

[![](https://p3.ssl.qhimg.com/t01abf5034b8a28be09.png)](https://p3.ssl.qhimg.com/t01abf5034b8a28be09.png)

图7. WDigest处于禁用状态

我们需要将`Negotiate`以及`UseLogonCredential`键值设为0，以禁用该协议。需要注意的是，在新版操作系统（Windows Server 2016、Windows 10等）中，注册表中并没有`UseLogonCredential`这个键值。根据[Dave Kennedy](https://twitter.com/hackingdave)的这篇[文章](https://www.trustedsec.com/2015/04/dumping-wdigest-creds-with-meterpreter-mimikatzkiwi-in-windows-8-1/)，具备本地管理员权限的攻击者可以修改注册表，启用WDigest，抓取这些凭据。因此，如果禁用该协议后这些键值被设置为1，那么表示系统已受到攻击。我们应该一直监控对注册表的修改，以便在早期就得到警报，捕获攻击行为。

如果该协议被禁用，攻击者尝试从WDigest中获取明文密码时会看到如下错误信息：

[![](https://p5.ssl.qhimg.com/t01b6080495ea0c0770.png)](https://p5.ssl.qhimg.com/t01b6080495ea0c0770.png)

图8. 禁用WDigest后的Mimikatz信息



## 四、保护LSA

LSASS（Local Security Authority Server Service）会在本地及远程登录过程中验证用户身份并部署本地安全策略。微软在Windows 8.1及更高版本的系统中为LSA提供了增强防护机制，避免不可信的进程读取该进程内存或者注入代码。攻击者可以执行如下Mimmikatz命令与LSA交互，获取存储在LSA内存中的明文密码：

```
sekurlsa::logonPasswords
```

[![](https://p1.ssl.qhimg.com/t0130375a078deb5736.png)](https://p1.ssl.qhimg.com/t0130375a078deb5736.png)

图9. Mimikatz与LSA交互

我们建议Windows Server 2012 R2以及Windows 8.1之前的系统启用LSA保护机制，避免Mimikatz读取LSASS进程的特定内存空间。我们可以在注册表中创建`RunAsPPL`键值，并将该值设为1启动保护：

```
HKEY_LOCAL_MACHINESYSTEMCurrentControlSetControlLSA
```

[![](https://p3.ssl.qhimg.com/t0192763ffcc165f20c.png)](https://p3.ssl.qhimg.com/t0192763ffcc165f20c.png)

图10. 启用LSA保护

启用LSA保护后，攻击者会看到如下错误：

[![](https://p2.ssl.qhimg.com/t01c5b2fa72b6c8bf74.png)](https://p2.ssl.qhimg.com/t01c5b2fa72b6c8bf74.png)

图11. 启用LSA保护后的Mimikatz



## 五、受限管理员模式

微软自Windows Server 2012 R2开始引入了一个新功能，可以避免LSASS在RDP会话中以明文形式存储本地管理员的凭据。虽然LSA防护机制能够避免Mimikatz获取相关凭据，官方还是推荐使用这个新增功能，避免攻击者通过禁用LSA防护来获取密码。

在注册表中，创建一个`DisableRestrictedAdmin`键值并设置为0，就可以在受限管理员模式下接收RDP会话。此外，我们也应该创建一个`DisableRestrictedAdminOutboundCreds`键值并将其设置为1，避免已使用受限管理员模式的RDP会话执行自动化网络身份认证操作。如果不设置该键值，那么就会启用管理员出站凭据。

```
HKEY_LOCAL_MACHINESystemCurrentControlSetControlLsa
```

[![](https://p2.ssl.qhimg.com/t017e962250f620ca11.png)](https://p2.ssl.qhimg.com/t017e962250f620ca11.png)

图12. 启用受限管理员模式

我们需要在域中强制启用“Restrict delegation of credentials to remote servers”（限制对远程服务器的凭据委派）策略，以确保所有出站RDP会话都使用受限管理员模式，避免泄露凭据。

[![](https://p0.ssl.qhimg.com/t013e0110602a8ff791.png)](https://p0.ssl.qhimg.com/t013e0110602a8ff791.png)

图13. 组策略限制凭据委派

需要使用`Require Restricted Admin`设置来启用该策略。

[![](https://p0.ssl.qhimg.com/t0181d82f5cae0d16c7.png)](https://p0.ssl.qhimg.com/t0181d82f5cae0d16c7.png)

图14. 限制凭据委派，启用受限管理员

一旦启用该策略，管理员可以通过“运行”对话框，使用如下参数以受限管理员方式RDP远程登陆到工作站及服务器上。

[![](https://p5.ssl.qhimg.com/t01f820ef73ef0fd4c6.png)](https://p5.ssl.qhimg.com/t01f820ef73ef0fd4c6.png)

图15. 以受限管理员方式运行mstsc

也可以通过命令行来执行。

[![](https://p1.ssl.qhimg.com/t01c531b1d84d7f93d5.png)](https://p1.ssl.qhimg.com/t01c531b1d84d7f93d5.png)

图16. 命令行下以受限管理员方式运行mstsc

如果系统版本早于Windows 2012 R2或者Windows 8.1，可以打上微软的KB2871997补丁。



## 六、凭据缓存

如果域控制器处于不可用状态，微软会检查最近已缓存的密码哈希值，以便认证用户身份。这些密码哈希存放于如下注册表路径中：

```
HKEY_LOCAL_MACHINESECURITYCache
```

可以运行如下命令利用Mimikatz获取这些哈希：

```
lsadump::cache
```

默认情况下Windows会缓存最近10个密码哈希。建议修改如下安全设置，将本地密码缓存数设置为0：

```
Computer Configuration -&gt; Windows Settings -&gt; Local Policy -&gt; Security Options -&gt; Interactive Logon: Number of previous logons to cache -&gt; 0
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cec8cc0f64b5e193.png)

图17. 交互式登录不缓存哈希

如果攻击者尝试使用Mimikatz获取这些哈希，则会看到如下错误：

[![](https://p0.ssl.qhimg.com/t01359d740d959749fe.png)](https://p0.ssl.qhimg.com/t01359d740d959749fe.png)

图18. 禁用凭据缓存时Mimikatz的错误信息



## 七、受保护的用户组

微软在Windows Server 2012及更高版本系统中引入了名为“Protected Users”（受保护用户）的安全组。这个组使得域管理员能够保护该组内的特权用户（如本地管理员）及其他用户仅通过Kerberos来进行域认证。这样就可以防止LSASS中的NTLM密码哈希或者明文凭据被攻击者窃取。

我们可以在活动目录用户及计算机中找到“Protected Users”安全组。

[![](https://p4.ssl.qhimg.com/t01f64e19254def3ed2.png)](https://p4.ssl.qhimg.com/t01f64e19254def3ed2.png)

图19. 活动目录中受保护用户安全组

位于该安全组内的账户会自动部署Kerberos认证策略，默认配置如下：

[![](https://p1.ssl.qhimg.com/t01148666b55fa103a3.png)](https://p1.ssl.qhimg.com/t01148666b55fa103a3.png)

图20. Kerberos默认策略

我们也可以在PowerShell中执行如下命令将其他用户添加到“Protected Users”组内：

```
Add-ADGroupMember –Identity 'Protected Users' –Members Jane
```

[![](https://p0.ssl.qhimg.com/t016e91b677731f2b46.png)](https://p0.ssl.qhimg.com/t016e91b677731f2b46.png)

图21. 通过PowerShell添加账户至受保护用户组中

像Windows Server 2008之类的老版本系统也可以打上KB2871997补丁，拥有这个安全组。



## 八、总结

我们可以使用有效的端点防护解决方案，同时配合上类似AppLocker之类的应用白名单机制来阻止可执行文件、PowerShell以及命令行被恶意执行，添加一个新的安全防护层。即使攻击者成功绕过这些控制机制，他们需要修改注册表（蓝队应该监控某些注册表键值）才能完全发挥Mimikatz的功能，以窃取凭据，而这个过程会生成许多事件，有助于我们检测攻击行为。
