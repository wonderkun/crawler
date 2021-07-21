> 原文链接: https://www.anquanke.com//post/id/152956 


# 使用 PtH 攻击 NTLM 认证的 Web 应用


                                阅读量   
                                **186994**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：labs.mwrinfosecurity.com
                                <br>原文地址：[ https://labs.mwrinfosecurity.com/blog/pth-attacks-against-ntlm-authenticated-web-applications/](https://labs.mwrinfosecurity.com/blog/pth-attacks-against-ntlm-authenticated-web-applications/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0166f37eafa6268948.jpg)](https://p1.ssl.qhimg.com/t0166f37eafa6268948.jpg)

本文详细介绍了在Windows/Active Directory环境中使用PtH攻击NTLM认证的web应用的详细步骤。该技术细节来源于Alva ‘Skip’ Duckwall 和Chris Campbell在2012年blackhat中名为“Still Passing the Hash 15 Years Later…”的演讲主题。

 

## 简介

Windows Active Directory环境的主要优点是它使用Kerberos 或者 NTLM认证来实现企业级单点登录（SSO）。这些方法通常用于各种企业资源的访问控制，从文件共享到Web应用程序，例如SharePoint，OWA或用于特定业务的内部Web应用程序。在Web应用程序的方面，IWA（Integrated Windows Authentication）允许用户通过Kerberos 或者 NTLM认证对Web应用程序进行自动身份验证，比如用于Web应用程序的Windows SSO。众所周知，NTLM身份验证协议的设计可能存在PtH攻击，用户使用哈希密码而不需原始密码就能进行身份验证。自1997年开始，这种攻击的公共工具已经存在，当时Paul Ashton发布了一个改进的SMB客户端，该客户端使用LanMan哈希来访问网络共享。



## 背景

多年来，PtH针对Windows环境的攻击已经得到了充分的证明。下面是选取的一些有价值的参考文献：

<!-- [if !supportLists]-->1.     <!--[endif]-->Microsoft的官方文档详细说明了在尝试NTLM身份验证之前，“客户端计算出一个哈希密码，丢弃掉实际密码”的过程。在Windows环境中可能更有助于理解NTLM身份验证为什么存在PtH攻击：[ https://docs.microsoft.com/en-us/windows/desktop/secauthn/microsoft-ntlm](/docs.microsoft.com/en-us/windows/desktop/secauthn/microsoft-ntlm)

<!-- [if !supportLists]-->2.     <!--[endif]-->Hernan Ochoa’s的幻灯片讨论了PtH最初的工具包：[https://www.coresecurity.com/system/files/publications/2016/05/Ochoa_2008-Pass-The-Hash.pdf](https://www.coresecurity.com/system/files/publications/2016/05/Ochoa_2008-Pass-The-Hash.pdf) 。文章讲述了一种从2000年开发的针对Windows机器的PtH攻击方法。

<!-- [if !supportLists]-->3.     <!--[endif]-->所有关于PtH的文章中，最感兴趣的是pth-suite Linux工具（这工具最初的发布是为Backtrack Linux编写的。所有的工具在Kali Linux中都有了新的位置，有一个需注意的例外，对写这篇博客非常有用，后面会详细说明）: [https://passing-the-hash.blogspot.com/](https://passing-the-hash.blogspot.com/)

<!-- [if !supportLists]-->4.     <!--[endif]-->“Pass-the-Hash Is Dead: Long Live LocalAccountTokenFilterPolicy”讨论的是本地用户账户的PtH，以及自Windows Vista的对PtH增加的额外限制：[https://www.harmj0y.net/blog/redteaming/pass-the-hash-is-dead-long-live-localaccounttokenfilterpolicy/](https://www.harmj0y.net/blog/redteaming/pass-the-hash-is-dead-long-live-localaccounttokenfilterpolicy/)

<!-- [if !supportLists]-->5.     <!--[endif]-->使用Metasploit中的PsExec模块利用PtH： https://www.offensive-security.com/metasploit-unleashed/psexec-pass-hash/

<!-- [if !supportLists]-->6.     <!--[endif]-->Mimikatz中PtH模块的GitHub文档：[https://github.com/gentilkiwi/mimikatz/wiki/module-~-sekurlsa#pth](https://github.com/gentilkiwi/mimikatz/wiki/module-~-sekurlsa#pth)

我一直对这种攻击技术感兴趣主要是因为可以使用PtH攻击NTLM认证的Web应用。由于Windows Active Directory环境无处不在，大量的企业内部Web应用都用此验证方案进行登陆，允许从公司工作站无缝SSO（Single Sign-On）到公司资源。因此，如果能够在Windows环境中对这些网站完成PtH攻击，就可以在后续对其进行更加深入有效的利用。当一个域名全部使用这种方案时，攻击的影响就非常明显了，比如一个给定域名在完整域名hashdump之后，会包含所有员工用户账户相关的NT哈希。在这种情况下，PtH不需要破解任何哈希密码就可以模拟任意公司员工登陆。这意味着即使对于那些具有安全意识的用户，他们可能使用了20多个字符长度的密码，也无法避免攻击者在企业的Web应用程序上模拟登陆。



## 使用PtH攻击NTLM认证的Web应用

那么实际中如何对NTLM认证的网站进行攻击？很长一段时间以来，我用谷歌搜索这个主题的结果，并没有找到对这种攻击方法详细的介绍（大约在2015-2018年）。在研究Kali Linux的PtH工具集（pth-suite）时，有个很奇怪的问题。大部分原来的pth-suite工具在2015年整合到了Kali Linux中，我之前提到的有一个不同，就是pth-firefox，顾名思义就是用于修改Firefox中NTLM认证代码以便能够允许Pth的工具。由于这些Linux工具对我没什么用，我就把注意力转移到了研究在Windows主机上使用Mimikatz进行同样的攻击的技术上。

在我自己发现一个可用的技术之后，我最近又偶然发现了由Alva ‘Skip’ Duckwall 和Chris Campbell在Blackhat 2012发表的[“Still Passing the Hash 15 Years Later…”](https://labs.mwrinfosecurity.com/blog/pth-attacks-against-ntlm-authenticated-web-applications/#Ref1)幻灯片的第30页。它详细介绍了一种方法，在使用Hernan Ochoa的Windows凭据编辑器（WCE）直接注入详细NT哈希到内存后，使IE（或者其他使用Windows内置“Internet Options”的浏览器）能够通过IWA进行认证。他们在演讲中的第[18分29](https://youtu.be/O7WRojkYR00?t=1109)秒给出了[这种技术](https://labs.mwrinfosecurity.com/blog/pth-attacks-against-ntlm-authenticated-web-applications/#Ref3)的演示。我花了很多时间才找到这些信息，并为实际利用的相关步骤写了文档，这篇博客的后续内容将介绍在Windows10主机中如何使用Mimikatz进行攻击。



## 攻击

### 配置环境

为了演示使用NTLM身份验证的Web应用程序，我是用了Exchange 2013服务器，配置为专门使用IWA进行OWA。在Exchange服务器上运行PowerShell配置命令如下：

Set-OwaVirtualDirectory -Identity “owa (Default Web Site)” -FormsAuthentication $false -WindowsAuthentication $true

Set-EcpVirtualDirectory -Identity “ecp (Default Web Site)” -FormsAuthentication $false -WindowsAuthentication $true

其它预先准备的条件：

<!-- [if !supportLists]-->l  <!--[endif]-->Exchange服务器已加入test.com域。在此域上，使用复杂的密码和相应的邮箱创建名为TESTpath的用户。计算此用户密码的NT哈希值，以便稍后攻击使用。NT哈希生成如下：

```
python -c 'import hashlib,binascii; print binascii.hexlify(hashlib.new("md4", "Strong,hardtocrackpassword1".encode("utf-16le")).digest())'

57f5f9f45e6783753407ae3a8b13b032
```

<!-- [if !supportLists]-->l  <!--[endif]-->在此之后，在未入域的Windows 10主机上下载最新版本的Mimikatz，该主机与Exchange服务器连接的网络相同。我们为了能够使用Exchange服务器的域名而不是IP地址，将此独立计算机上的DNS服务器设置为test.com的域名控制器。

### 攻击

假设我们的OWA Web应用程序可以在[https://exchange.test.com/owa](https://exchange.test.com/owa)上访问，通常浏览到OWA会有以下提示：

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p2.ssl.qhimg.com/t015770cfbf0f7ecc92.png)](https://p2.ssl.qhimg.com/t015770cfbf0f7ecc92.png)<!--[endif]-->

因为计算机在内存中没有任何域凭据，从网站收到的WWW-Authenticate头指定它可以接受NTLM身份验证。

以管理员身份运行Mimikatz，我们可以在TESTpth用户的上下文中启动命令提示符，方法是使用Mimikatz中的Pass-the-Hash模块-sekurlsa::pth-并提供用户的NT哈希作为参数：

```
privilege::debug

sekurlsa::pth /user:pth /ntlm:57f5f9f45e6783753407ae3a8b13b032 /domain:TEST /run:cmd.exe
```

这样不会改变计算机的本地权限，但是如果我们尝试从新生成的命令提示符访问任何网络资源，它将在我们注入的证书的上下文中完成。

 为了确保我们的浏览器在这些注入的凭据下运行，我们在命令提示符中通过运行“C:Program Filesinternet exploreriexplore.exe”这个命令生成IE进程

 检查“Internet选项”对话框中“本地Intranet”区域的“安全设置”，我们可以看到默认情况下，只对Intranet区域中的网站自动进行身份验证（使用SSO）。如下图所示：

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p1.ssl.qhimg.com/t0198a584d06e95a79e.png)](https://p1.ssl.qhimg.com/t0198a584d06e95a79e.png)<!--[endif]-->

因此，为了在Windows上使用PtH攻击Internet Explorer，必须将目标站点添加到“本地Intranet区域”。可以使用一个单独的通配符域来代替单独添加网站到这个域，在这种情况下，“*.test.com”将匹配“Test.com”的所有子域。配置如下面的截图：<!-- [if !vml]-->[![](https://p1.ssl.qhimg.com/t01ee794ea4380e22a7.png)](https://p1.ssl.qhimg.com/t01ee794ea4380e22a7.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

配置完成后，当浏览到[https://exchange.test.com/owa](https://exchange.test.com/owa)。TESTpth用户将通过NTLM认证自动进行身份验证，然后OWA加载成功。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p2.ssl.qhimg.com/t01866bc630a461af6b.png)](https://p2.ssl.qhimg.com/t01866bc630a461af6b.png)<!--[endif]-->



## 潜在的影响

在域名泄露之后，对任何支持IWA的公司，PtH攻击Web应用程序将变得非常高效，可以模拟任何员工获取权限。虽然这可能主要包括的是微软Web服务，比如SharePoint和OWA（如果IWA是专门启用的），但是各种定制的内部财务程序，包括那些用来外部支付的应用程序，也是一样的。现在行业开始转向云服务环境，通常涉及ADFS联合身份验证，一般默认情况下，[ADFS在提供Internet explorer用户代理时支持IWA](https://labs.mwrinfosecurity.com/blog/pth-attacks-against-ntlm-authenticated-web-applications/#Ref4)。在这种情况下，意味着可以通过PtH访问公司的云端资源。



## 建议

虽然这篇文章的主要目的不是讨论保护Windows Active Directory环境的问题，但我们不能只在一个点上说问题，应该给感兴趣的人提供一些解决这些攻击的更深层次的思考。更多的细节没有在这篇文章讨论，可以在以前的文章中找到：[Planting the Red Forest: Improving AD on the Road to ESAE](https://www.mwrinfosecurity.com/our-thinking/planting-the-red-forest-improving-ad-on-the-road-to-esae/).

Windows环境中的Pth问题无法自己本身解决。Active Directory用于SSO的两种协议都能发生Pth类型的攻击。最好的建议就是首先要防止密码哈希和Kerberos密钥的泄露。最重要的是域名控制器，域管理员控制，或其他在Active Directory作用包含保存凭据信息的部分不被泄露，这些都将直接导致所有存储的密码哈希和Kerberos密钥的泄露。在Windows10和Server 2016中，可使用Credential Guard来保护内存中保存的凭据信息不受到窃取攻击。

在单独查看Web应用程序的IWA时，确保在登陆过程中使用多重身份验证（MFA）会有很好效果。有一个特例，在ADFS和Office 365一起使用时，通过IWA进行初始身份验证，为了完整整个验证还需要请求第二个因素，之后才能授权访问公司资源。但不幸这种方法不能通用的解决Pth问题，因为不是所有协议都支持它，比如SMB不支持MFA，但还提供允许远程代码执行的功能，这就使攻击者可以不受阻碍地使用PtH在企业环境中横冲直撞。



## 最后说明：Kerberos认证的 “PtH”

PtH背后的概念是，一旦凭证存储被泄露，就可以使用被盗存储的凭证材料（绝不应该是明文密码），模拟用户进行身份验证，而无需获取该用户的相应明文密码。

在参考Microsoft关于实现Kerberos协议的文档时，描述了如何使用“Kerberos与身份验证”来获取Kerberos票证授权（TGT）。这个过程要求用户给域控制器发送一个“验证信息”，使用从用户登录的密码派生的主密钥加密。然后，该文档解释了当DC收到TGT请求时，“它在其数据库中查找用户，获取关联用户的主密钥，解密预身份验证数据，并评估内部的时间戳。”这意味着秘钥本身用于用户的身份验证而不是作为用户的明文密码。用户的密码派生秘钥存储在AD数据库中，意味着如果此数据库遭到破坏（比如：当攻击者获得与管理员权限时候），则可以恢复存储的秘钥以及用户存储的NT哈希。由于只需要存储的秘钥来创建有效的验证信息，而Kerberos身份验证的作用就是“传递秘钥”。Alva Duckwall和Benjamin Delpy将此攻击称为“超越哈希”，而surklsa::pth Mimikatz模块只支持使用Kerberos密钥来编写Kerberos预认证请求。

当然这意味着Web应用程序或任何其他公司支持直接使用AD进行Kerberos身份验证，则可以使用OTH对其进行攻击。
