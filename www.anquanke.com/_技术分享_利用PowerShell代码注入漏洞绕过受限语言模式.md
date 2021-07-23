> 原文链接: https://www.anquanke.com//post/id/86738 


# 【技术分享】利用PowerShell代码注入漏洞绕过受限语言模式


                                阅读量   
                                **87714**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exploit-monday.com
                                <br>原文地址：[http://www.exploit-monday.com/2017/08/exploiting-powershell-code-injection.html](http://www.exploit-monday.com/2017/08/exploiting-powershell-code-injection.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01a228a36c83464acf.png)](https://p2.ssl.qhimg.com/t01a228a36c83464acf.png)



译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**0x00 前言**

[**受限语言模式**](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes)是一种非常有效的机制，能阻止在PowerShell中执行任意未签名的代码。当**Device Guard**或者**AppLocker**处于强制模式时，它是最实际有效的强制安全措施，因为未被策略允许的任何脚本或者模块都位于受限语言模式下，这严重限制了攻击者执行未签名的代码。通过限制语言模式限制了**Add-Type**的调用。限制Add-Type明显是考虑到了它能编译并加载任意的C#代码到你的运行空间中去。但策略允许的PowerShell代码运行在“Full Language”模式下，允许执行Add-Type。这样，微软签名的PowerShell的代码就能调用Add-Type。不相信吗？运行下面的命令你就会发现我是正确的。

<a>**<br>**</a>

**0x01 漏洞利用**

现在，想像一下如果下面的PowerShell模块代码（姑且称为“VulnModule”）有微软的签名：

```
ls C:* -Recurse -Include '*.ps1', '*.psm1' |
 Select-String -Pattern 'Add-Type' |
 Sort Path -Unique |
 % `{` Get-AuthenticodeSignature -FilePath $_.Path `}` |
 ? `{` $_.SignerCertificate.Subject -match 'Microsoft' `}`
```

那么有什么可以影响来自受限语言模式的Add-Type的输入呢？

好了，让我们一起思考下吧：

1. Add-Type作为类型定义传递给一个全局变量。因为它是全局的，它可以被任何人访问，包括我们和攻击者。

2. 问题是，签名的代码先于调用Add-Type就定义了全局变量，因此如果我们使用自定义的恶意的C#代码，这将会被合法的代码覆盖。

3. 你知道能用Set-Variable cmdlet来设置变量只读吗？你知道我现在在想什么了吧？

<a>**<br>**</a>

**0x02 武器化利用**

好了，为了从受限语言模式注入代码到Add-Type中，攻击者需要定义他们的恶意代码为一个只读变量，拒绝签名代码设置全局变量“Source”。下面是PoC：

```
$Global:Source = @'
    public class Test `{`
        public static string PrintString(string inputString) `{`
            return inputString;
        `}`
    `}`'@
Add-Type -TypeDefinition $Global:Source
```

简要说明下Add-Type注入缺陷。受限语言模式的一个限制是你不能调用非白名单类的.NET方法，但有两个例外：属性（getter方法）和ToString方法。在上面的PoC中，我选择了实现一个静态的ToString方法，因为ToString允许传递参数（getter不行）。我的类也是静态的，因为.NET类的白名单只在New-Object实例化对象时适用。

那么上面的漏洞代码是否听起来不切实际呢？你可以这么认为，但是[Microsoft.PowerShell.ODataUtils](https://technet.microsoft.com/en-us/library/dn818911.aspx) 模块中的Microsoft.PowerShell.ODataUtils也有这个漏洞。微软在 [CVE-2017-0215](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-0215), [CVE-2017-0216](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-0216), [CVE-2017-0219](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-0219)中修复了它。说实话，我不太记得了。[Matt Nelson](https://twitter.com/enigma0x3) 和我都报告了这些注入bug。

<a>**<br>**</a>

**0x03 阻止措施**

最简单的阻止这种注入攻击的方式是，直接在Add-Type使用单引号的[here-string](https://technet.microsoft.com/en-us/library/ee692792.aspx)给TypeDefinition。单引号的字符串不会扩展任何内嵌的变量或者表达式。当然，这个场景假设了你是编译静态代码。如果你动态生成代码给Add-Type，要特别注意攻击者可能影响你的输入。为了理解影响PowerShell中代码执行的方法，可以参见我在PSConf.EU上的演讲“[Defensive Coding Strategies for a High-Security Environment](https://www.youtube.com/watch?v=O1lglnNTM18)”。

<a>**<br>**</a>

**0x04 缓解措施**

尽管微软在推动解决这个漏洞，我们有什么可以做的呢？

有个关于UMCI绕过二进制的有效的黑名单规则是[文件名规则](https://docs.microsoft.com/en-us/windows/device-security/device-guard/deploy-code-integrity-policies-policy-rules-and-file-rules#code-integrity-file-rule-levels)，其能基于PE文件中版本信息资源中的原始文件名来阻止程序执行。PowerShell很明显不是个PE文件，它是文本文件，因此文件名规则不适用。但是，你可以通过使用哈希规则强制阻止有漏洞的脚本。Okay…要是相同脚本有不止一个漏洞呢？目前为止你只阻止一个哈希。你开始注意这个问题了吗？为了有效的阻止之前所有有漏洞的版本的脚本，你必须知道所有有漏洞的版本的哈希。微软意识到了问题并尽最大努力来扫描所有之前发布的有漏洞脚本，且收集哈希将他们整合到了[黑名单](https://docs.microsoft.com/en-us/windows/device-security/device-guard/deploy-code-integrity-policies-steps#create-a-code-integrity-policy-from-a-golden-computer)中。通过他们的哈希阻止所有版本的有漏洞的脚本有一定挑战性，但能一定程度上阻止攻击。这就是为什么一直迫切需要只允许PowerShell 5的执行并要开启scriptblock日志记录。[Lee Holmes](https://twitter.com/Lee_Holmes) 有篇关于如何有效的阻止老版本的PowerShell的[博文](http://www.leeholmes.com/blog/2017/03/17/detecting-and-preventing-powershell-downgrade-attacks/)。

另一种方式是系统中大部分脚本和二进制都是catalog和Authenticode签名的。Catalog签名不是意味着脚本有内嵌的Authenticode签名，而是它的哈希存储在微软签名的catalog文件中。因此当微软更新时，老版本的哈希将会过期，将不再是被签名的了。现在，一个攻击者也能将老的签名的catalog文件插入到catalog存储中。你不得不提权执行操作，关于这个，有很多方法可以绕过Device Guard UMCI。作为一个搜索有漏洞脚本的研究员，首先要寻找具有内嵌Authenticode签名的有漏洞脚本（有字符串“SIG # Begin signature block”的提示）。Matt Nelson说这种bypass脚本存在。

<a>**<br>**</a>

**0x05 报告**

如果你找到了一种绕过，请将它上报给[secure@microsoft.com](mailto:secure@microsoft.com) ，你将得到一个CVE。PowerShell团队积极解决注入缺陷，但是他们也主动解决用于影响代码执行的一些方式。

**<br>**

**0x06 总结**

尽管受限语言模式能有效的阻止未签名代码的执行，PowerShell和它的签名过的模块或脚本还是有很多攻击面。我鼓励每个人都来寻找更多的注入缺陷，上报他们，通过官方的MSRC获得荣誉，并使得PowerShell生态变得更加安全。同时希望，PowerShell的代码作者要自我检视。

现在我解释了所有的内容，但是因为设计缺陷允许利用竞争条件，所以调用Add-Type还是有[注入的漏洞](http://www.exploit-monday.com/2017/07/bypassing-device-guard-with-dotnet-methods.html)。我希望能继续阐述这些问题，且希望微软将考虑解决这个基础问题。
