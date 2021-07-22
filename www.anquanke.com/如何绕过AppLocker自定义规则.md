> 原文链接: https://www.anquanke.com//post/id/159892 


# 如何绕过AppLocker自定义规则


                                阅读量   
                                **143471**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0x09AL，文章来源：0x09al.github.io
                                <br>原文地址：[https://0x09al.github.io/security/applocker/bypass/custom/rules/windows/2018/09/13/applocker-custom-rules-bypass.html](https://0x09al.github.io/security/applocker/bypass/custom/rules/windows/2018/09/13/applocker-custom-rules-bypass.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t013b51a58ea0863096.png)](https://p4.ssl.qhimg.com/t013b51a58ea0863096.png)



## 一、前言

在大型组织的安全领域中，AppLocker正在扮演越来越重要的角色。应用AppLocker规则可以显著降低企业的安全风险。不幸的是，对于蓝队来说除了默认规则以外，AppLocker还涉及到许多自定义配置，而这些配置很有可能成为目标安全的突破口。现在已经有许多文章介绍了如何绕过AppLocker的默认规则，而本文将介绍绕过自定义规则的具体步骤，包括如何定位、解析自定义规则，以及如何利用这些信息绕过自定义规则。



## 二、AppLocker自定义规则

AppLocker规则可以应用于目标应用，这些规则也是构成AppLocker策略的基本组件。接下来我们需要了解一下规则集合（Rule Collection）。

**规则集合**

AppLocker控制台以规则集合作为组织单元，这些集合包括可执行文件、脚本、Windows安装文件、封装的应用和应用安装包以及DLL文件。这些规则可以让我们轻松区分开不同类型的应用。

**规则条件**

规则条件（Rule Condition）可以帮助AppLocker识别哪些应用对应哪些规则。三个主要的规则条件分别为应用发布者（Publisher）、路径（Path）以及文件哈希（File hash）。

**类型**

文件路径条件：以应用在系统中的路径作为识别依据；文件发布者条件：以应用的属性或者数字签名作为识别依据；文件哈希条件：以应用的哈希值作为识别依据。

AppLocker支持创建的不同条件如下图所示：

[![](https://p4.ssl.qhimg.com/t01bb976c2afc38ea42.png)](https://p4.ssl.qhimg.com/t01bb976c2afc38ea42.png)



## 三、具体操作

首先也是最关键的一个步骤就是知道当前系统部署了哪些AppLocker规则。大多数情况下，系统会强制部署默认规则，但这里也可能存在一些自定义规则。AppLocker规则通常由GPO强制执行，我们可以查询活动目录（Active Directory）来获取这些信息。

幸运的是，PowerShell中有个AppLocker模块，可以查询当前系统已部署的AppLocker规则。如下一个PowerShell脚本可以按照较清晰的格式输出具体规则，我们可以根据这些信息制定绕过策略。

```
Import-Module AppLocker
[xml]$data = Get-AppLockerPolicy -effective -xml

# Extracts All Rules and print them.
Write-Output "[+] Printing Applocker Rules [+]`n"
($data.AppLockerPolicy.RuleCollection | ? `{` $_.EnforcementMode -match "Enabled" `}`) | ForEach-Object -Process `{`
    Write-Output ($_.FilePathRule | Where-Object `{`$_.Name -NotLike "(Default Rule)*"`}`) | ForEach-Object -Process `{`Write-Output "=== File Path Rule ===`n`n Rule Name : $($_.Name) `n Condition : $($_.Conditions.FilePathCondition.Path)`n Description: $($_.Description) `n Group/SID : $($_.UserOrGroupSid)`n`n"`}`
    Write-Output ($_.FileHashRule) | ForEach-Object -Process `{` Write-Output "=== File Hash Rule ===`n`n Rule Name : $($_.Name) `n File Name :  $($_.Conditions.FileHashCondition.FileHash.SourceFileName) `n Hash type : $($_.Conditions.FileHashCondition.FileHash.Type) `n Hash :  $($_.Conditions.FileHashCondition.FileHash.Data) `n Description: $($_.Description) `n Group/SID : $($_.UserOrGroupSid)`n`n"`}`
    Write-Output ($_.FilePublisherRule | Where-Object `{`$_.Name -NotLike "(Default Rule)*"`}`) | ForEach-Object -Process `{`Write-Output "=== File Publisher Rule ===`n`n Rule Name : $($_.Name) `n PublisherName : $($_.Conditions.FilePublisherCondition.PublisherName) `n ProductName : $($_.Conditions.FilePublisherCondition.ProductName) `n BinaryName : $($_.Conditions.FilePublisherCondition.BinaryName) `n BinaryVersion Min. : $($_.Conditions.FilePublisherCondition.BinaryVersionRange.LowSection) `n BinaryVersion Max. : $($_.Conditions.FilePublisherCondition.BinaryVersionRange.HighSection) `n Description: $($_.Description) `n Group/SID : $($_.UserOrGroupSid)`n`n"`}`
`}`
```

该脚本会尝试查找规则名称不是`Default Rule`的所有AppLocker规则，然后输出`FilePath`、`FilePublisher`以及`FileHash`规则。

比如，一个典型的输出如下图所示：

[![](https://p3.ssl.qhimg.com/t011eefd4ae4b66e31b.png)](https://p3.ssl.qhimg.com/t011eefd4ae4b66e31b.png)

现在我们已经知道哪些是自定义规则，接下来可以尝试如何绕过这些规则。

### <a class="reference-link" name="%E7%BB%95%E8%BF%87%E6%96%87%E4%BB%B6%E5%93%88%E5%B8%8C%E8%A7%84%E5%88%99"></a>绕过文件哈希规则

这是一种我们可以轻松绕过并广泛使用的规则。为了绕过文件哈希规则，我们需要能够攻击SHA256算法的一种攻击方式，因为这是AppLocker默认使用的哈希算法。滥用这种规则的唯一条件是找到已被允许的特定可执行文件，这些可执行文件可以用来加载任意代码（这种情况不是很常见）或者存在DLL劫持漏洞（这种情况比较常见）。

比如，Process Explorer中存在一个DLL劫持漏洞，我们可以滥用该漏洞来加载我们的恶意代码。

观察`ProcExp.exe`的运行过程，我们可以看到程序尝试加载名为`MPR.dll`的一个DLL文件，如下图所示：

[![](https://p5.ssl.qhimg.com/t01d1ecb7058614926d.png)](https://p5.ssl.qhimg.com/t01d1ecb7058614926d.png)

系统中已有一个规则，允许Process Explorer运行，如下图所示：

[![](https://p0.ssl.qhimg.com/t0172ff5e8d83b4eb40.png)](https://p0.ssl.qhimg.com/t0172ff5e8d83b4eb40.png)

我自己构建了一个DLL文件，其中导出了Process Explorer所需的函数，程序中还包含一个函数可以执行`calc.exe`。

[![](https://p2.ssl.qhimg.com/t01aed9afd9575b2e87.png)](https://p2.ssl.qhimg.com/t01aed9afd9575b2e87.png)

在实际攻击场景中，作为攻击载荷，这个DLL需要将自身注入到内存中，避免攻击过程中有任何程序落盘。

只有DLL规则没有部署时这种方法才能奏效，大多数情况下这个条件都可以满足，因为启用这些规则会降低系统的性能。

### <a class="reference-link" name="%E7%BB%95%E8%BF%87%E6%96%87%E4%BB%B6%E8%B7%AF%E5%BE%84%E8%A7%84%E5%88%99"></a>绕过文件路径规则

文件路径规则是我们最常见到的规则之一，也是绕过AppLocker的绝佳突破口。这种条件规则会根据应用在文件系统或者网络中的路径来识别应用，通常情况下，规则中会指定一个路径或者文件位置。比如，在测试环境中我创建了一个示例规则，允许执行`C:\Python27\`目录中的所有可执行文件，如下图所示：

[![](https://p0.ssl.qhimg.com/t01171f23caebdee860.png)](https://p0.ssl.qhimg.com/t01171f23caebdee860.png)

如果该规则指定的目录可写，我们就可以将自己的程序放在该目录中，这样就能绕过AppLocker。

[![](https://p0.ssl.qhimg.com/t018b36113b2357e75f.png)](https://p0.ssl.qhimg.com/t018b36113b2357e75f.png)

### <a class="reference-link" name="%E7%BB%95%E8%BF%87%E6%96%87%E4%BB%B6%E5%8F%91%E5%B8%83%E8%80%85%E8%A7%84%E5%88%99"></a>绕过文件发布者规则

这个条件会根据应用的数字签名以及扩展属性（如果存在扩展属性的话）来识别应用。数字签名中包含创造该应用的公司（发布者）信息。可执行文件、DLL、Windows安装程序、封装的应用以及应用安装包同样包含扩展属性，可以从二进制资源区中获取这些属性。对于可执行文件、DLL以及Windows安装包而言，这些属性中包含文件所对应的产品名称、发布者提供的原始文件名以及文件版本号；对于封装的应用及应用安装包而言，这些扩展属性包含应用包的名称及版本。

这种规则条件是最为安全的条件，绕过手段非常有限。AppLocker会检查签名是否有效，因此我们无法使用不可信的证书来签名攻击程序。SpecterOps的Matt曾研究过如何在Windows系统上生成有效的签名，不过这种方法需要管理员权限，并且要求AppLocker在默认情况下允许管理员执行任何应用。

绕过这种规则的一种方法与前面介绍的哈希规则绕过方法相同，那就是利用DLL劫持漏洞或者可以加载任意代码到内存中的已签名的某个应用。比如，如果规则允许执行经过微软签名的所有程序，那么我们就可以使用Process Explorer实施攻击。Process Explorer是一个经过签名的应用，并且存在DLL劫持漏洞，我们可以利用这一点来绕过AppLocker，具体方法请参考前文介绍的绕过文件哈希规则的过程。



## 四、总结

这是我在实际环境中使用过的一些实用技术，在这里与整个社区一起分享。可能还有其他方法能够绕过自定义规则，我希望本文能抛砖引玉，让更多人能够研究这方面技术。



## 五、参考资料

[https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/applocker/working-with-applocker-rules](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/applocker/working-with-applocker-rules)

[https://msitpros.com/?p=2012](https://msitpros.com/?p=2012)
