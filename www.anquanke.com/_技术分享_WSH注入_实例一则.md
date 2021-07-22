> 原文链接: https://www.anquanke.com//post/id/86631 


# 【技术分享】WSH注入：实例一则


                                阅读量   
                                **106945**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：enigma0x3.net
                                <br>原文地址：[https://enigma0x3.net/2017/08/03/wsh-injection-a-case-study/](https://enigma0x3.net/2017/08/03/wsh-injection-a-case-study/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p4.ssl.qhimg.com/t010b4324a47984272e.png)](https://p4.ssl.qhimg.com/t010b4324a47984272e.png)

译者：[h4d35](http://bobao.360.cn/member/contribute?uid=1630860495)

预估稿费：110RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

****

在2017年举办于纳什维尔的BSides会议上，Casey Smith（[@SubTee](https://twitter.com/subtee)）和我（Matt Nelson，[@enigma0x3](https://twitter.com/enigma0x3)）做了一个题为《[Windows Operating System Archaeology](https://www.youtube.com/watch?v=3gz1QmiMhss)》的演讲。在这个演讲中，我们展示了一些在Windows中利用组件对象模型（Component Object Model，COM）的攻击技术。接下来我将讨论在上述演讲中提到的利用攻击者控制的输入来调用**GetObject()**函数进行攻击的方法。

某些系统环境使用白名单来防止未签名的**Windows Scripting Host（WSH）**文件运行，特别是随着恶意的.js或.vbs脚本文件越来越多。然而，通过将我们的恶意代码注入到一个经过微软签名的WSH脚本中，我们可以绕过这样的限制。

在深入研究那些可以被用于注入的脚本之前，了解一下其中的工作机制很重要。在进行注入攻击时，我们利用攻击者控制的输入作为参数传递给**GetObject()**函数，然后将其与**script:**或**scriptlet:**COM标记相结合。



**GetObject()函数**

此方法允许你访问某个已实例化的COM对象。如果没有该对象的实例（如果以不含COM标记的方式调用），那么该函数调用将会执行失败。例如，通过**GetObject()**函数访问Microsoft Excel的COM对象的方法如下所示：

```
Set obj = GetObject( , "Excel.Application")
```

为了使上述代码工作，必须有一个Excel的实例在运行。[点此](https://ss64.com/vb/getobject.html)了解更多更多关于**GetObject()**函数的信息。 



**COM标记**

虽然GetObject()函数本身很有趣，但它只允许我们访问一个已经实例化的COM对象。为了解决这个问题，我们可以实现一个COM标记来方便我们的payload执行。如果你不熟悉COM标记，可以[点此](https://msdn.microsoft.com/en-us/library/windows/desktop/ms691261(v=vs.85).aspx)阅读更多相关信息。Windows系统中有许多不同的COM标记，允许你以各种方式实例化对象。从攻击的角度来看，你可以使用这些标记来执行恶意代码。不过这是另外一篇博客文章的主题了:-)。

就本文而言，我们将重点介绍**script:**或**scriptlet:**这两个标记。这些特定的标记与scrobj.dll配合，有助于COM脚本的执行，而这将作为我们的Payload。这是由Casey Smith（[@SubTee](https://twitter.com/subtee)）发现的，在[2016年的DerbyCon](http://www.irongeek.com/i.php?page=videos/derbycon6/522-establishing-a-foothold-with-javascript-casey-smith)上进行了讨论，并且发表了[文章](http://www.irongeek.com/i.php?page=videos/derbycon6/522-establishing-a-foothold-with-javascript-casey-smith)。

如下所示是一个COM脚本：



```
&lt;?XML version="1.0"?&gt;
var r = new ActiveXObject("WScript.Shell").Run("calc.exe");
]]&gt;
&lt;/scriptlet&gt;
```

你还可以使用James Forshaw（[@tiraniddo](https://twitter.com/tiraniddo)）开发的工具DotNetToJScript在COM脚本中扩展JScript/VBScript，该工具允许调用Win32 API，甚至执行Shellcode。 当你将这两个COM标记中的任意一个与GetObject()函数的各种调用相结合时，情况将会变得很有趣。

非常简短的COM背景知识介绍已经结束，是时候来看一个实例了。



**PubPrn.vbs**

在Windows 7及更高版本的Windows系统中，有一个名为**PubPrn.vbs**的已被微软签名的WSH脚本，它位于**C:WindowsSystem32Printing_Admin_Scriptsen-US**目录中。看一下这个脚本的代码，很显然，它接收用户提供的输入作为参数（通过命令行参数）并将参数传递给**GetObject()**函数。

[![](https://p5.ssl.qhimg.com/t016407db531a3ed797.png)](https://p5.ssl.qhimg.com/t016407db531a3ed797.png)

这意味着我们可以运行这个脚本并传递它所期望的两个参数。第一个参数可以是任何东西，第二个参数是通过**script:**标记方式传递的Payload。

注意：如果你提供的第一个参数值不是一个有效的网络地址（因为它需要一个ServerName），则可以在调用时为cscript.exe增加**/b**参数，以便抑制额外的错误消息。

[![](https://p3.ssl.qhimg.com/t01c5a3b55967f0823f.png)](https://p3.ssl.qhimg.com/t01c5a3b55967f0823f.png)

由于VBScript依靠COM组件来执行操作，因此它在许多Microsoft签名的脚本中被大量使用。本文仅提供了一个实例进行说明，一定还有其他脚本能够以类似的方式被利用。我鼓励你去继续探索。
