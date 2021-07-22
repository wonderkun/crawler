> 原文链接: https://www.anquanke.com//post/id/87273 


# 【技术分享】利用Outlook的CreateObject及DotNetToJScript实现横向渗透


                                阅读量   
                                **112462**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://enigma0x3.net/2017/11/16/lateral-movement-using-outlooks-createobject-method-and-dotnettojscript/](https://enigma0x3.net/2017/11/16/lateral-movement-using-outlooks-createobject-method-and-dotnettojscript/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01e61fba5f83fe942d.jpg)](https://p3.ssl.qhimg.com/t01e61fba5f83fe942d.jpg)

译者：[eridanus96](http://bobao.360.cn/member/contribute?uid=2857535356)

预估稿费：130RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**



在以前，我在博客中曾经探讨了利用Windows中的分布式组件对象模型（DCOM）进行横向渗透的多种方法，链接为：

[https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/](https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/) 。

在本文，我们将研究如何利用Outlook的CreateObject()方法来实现横向渗透。

如果你不熟悉CreatObject()方法，可以先参考微软的官方文档，链接为：

[https://msdn.microsoft.com/en-us/library/aa262700(v=vs.60).aspx](https://msdn.microsoft.com/en-us/library/aa262700(v=vs.60).aspx) 。

**实际上，这一方法会允许你实例化一个任意的COM对象。**要利用DCOM应用进行横向渗透，通常会有一个问题，就是我们可能难以满足该方法所需的前提要求。大多情况下，我们需要借助**ShellExecute**（或者类似的）方法来启动任意进程，或是在目标主机上打开恶意文件。**但有一个重要的前提，就是需要预先在本地磁盘（或网络共享）中放置一个载荷。**虽然这种横向渗透的技术十分有效，但综合考虑到利用的条件，这种方案并不理想。

举例来说，ShellBrowser/ShellBrowserWindow应用只允许启动带有参数的进程，这样就导致我们还要去考虑命令行日志记录的因素。那么，通过Run()方法来执行宏呢？同样，也需要先在本地或者共享目录下有一个包含恶意宏的文件，这显然也不是一个理想的方案。

那么，有没有方法能通过DCOM直接执行Shellcode，而无须向目标主机上传文件或启动PowerShell或regsvr32这类的进程呢？答案是肯定的，我们可以借助Outlook的DCOM来实现。



**实现过程**



首先，我们需要远程实例化Outlook：



```
$com = [Type]::GetTypeFromProgID('Outlook.Application’,’192.168.99.152’)
$object = [System.Activator]::CreateInstance($com)
```



[![](https://p4.ssl.qhimg.com/t010a2ba459493952d4.png)](https://p4.ssl.qhimg.com/t010a2ba459493952d4.png)

上一步完成之后，我们就可以使用CreateObject()方法了：

[![](https://p4.ssl.qhimg.com/t01f4bf687b6f03afa1.png)](https://p4.ssl.qhimg.com/t01f4bf687b6f03afa1.png)

如上所述，**这个方法提供了在远程主机上实例化任何COM对象的能力。**那么我们如何用它去执行Shellcode呢？通过使用CreatObject方法，我们可以实例化ScriptControl COM对象，该对象允许通过AddCode()方法来执行任意VBScript或者JavaScript：

```
$RemoteScriptControl = $object.CreateObject(“ScriptControl”)
```

[![](https://p4.ssl.qhimg.com/t016eff2bda48ef767e.png)](https://p4.ssl.qhimg.com/t016eff2bda48ef767e.png)

如果我们使用James Forshaw的DotNetToJScript技术，**在VBS或JS中反序列化一个.NET程序集，我们便可以在VBS或JS代码传递给AddCode()方法后，通过ScriptControl来实现Shellcode的执行。**由于ScriptControl对象是通过Outlook的CreateObject()方法远程实例化的，因此传递的任何代码都能够在远程主机上执行。

关于更详细的DotNetToJScript技术，请参考James的Github： 

[https://github.com/tyranid/DotNetToJScript](https://github.com/tyranid/DotNetToJScript) 。

为了证明这一点，我将使用一个简单的程序集来启动计算器。我们用C#语言编写的PoC如下：

[![](https://p1.ssl.qhimg.com/t01ea81430bcd7b9d88.png)](https://p1.ssl.qhimg.com/t01ea81430bcd7b9d88.png)

在编译载荷之后，就可以将其传递给DotNetToJScript，并返回一些可爱的JS或VBS。在本文的样例中，我们选择了JS。

[![](https://p3.ssl.qhimg.com/t018dc7894a4486e7ab.png)](https://p3.ssl.qhimg.com/t018dc7894a4486e7ab.png)

现在已经生成了有效载荷，它可以传递到远程主机上Outlook的CreateObject方法创建的ScriptControl COM对象。我们通过将整个JS/VBS代码块存储在PowerShell的变量中来完成。如下所示，我们将它存储在一个名为“$code”的变量中：

[![](https://p0.ssl.qhimg.com/t014a94febc1d725117.png)](https://p0.ssl.qhimg.com/t014a94febc1d725117.png)

最后一步，我们需要做的是将ScriptControl对象上的“Language”属性设置为我们要执行的语言（JS/VBS），然后将“AddCode()”方法作为参数，调用“$code”变量：



```
$RemoteScriptControl.Language = “JScript”
$RemoteScriptControl.AddCode($code)
```

[![](https://p3.ssl.qhimg.com/t01f58d4a12b675b33b.png)](https://p3.ssl.qhimg.com/t01f58d4a12b675b33b.png)

在调用“AddCode()”方法之后，我们的JavaScript将会在远程主机上执行：

[![](https://p4.ssl.qhimg.com/t01644fb5565f89ba26.png)](https://p4.ssl.qhimg.com/t01644fb5565f89ba26.png)

如你所见，此时calc.exe已经在远程主机上启动，我们由此就完成了借助Outlook的横向。

<br>



**检测与缓解方式**

如果你仔细观察上面的截图，会发现OUTLOOK.EXE在这里变成了svchost.exe的一个子进程。**这就说明，Outlook应用程序正在通过DCOM进行远程实例化，所以我们可以通过这一点来检测是否受到了这一方法的攻击。****在大多情况下，正在启动的进程会在命令行的显示中包含“-embedding”（嵌入），这也是远程实例化的一个标志。**

除此之外，vbscript.dll或jscript/jscript9.dll的模块加载也不同寻常。在通常情况下，加载这些的并不是Outlook，而是所使用的ScriptControl对象的指示器。

在本文的例子中，载荷是作为Outlook.exe的子进程运行的，这就显得十分奇怪。**需要强调的是，如果一个.NET程序集正在执行，就意味着我们一定可以进行Shellcode注入。**攻击者可以编写一个将Shellcode注入另一个进程的程序集，并借此来绕过进程父子关系的检测，而不是直接地启动进程。**此外，启用Windows防火墙后将会阻挡此类攻击，因为防火墙会阻止DCOM的使用。**
