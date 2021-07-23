> 原文链接: https://www.anquanke.com//post/id/84722 


# 【技术分享】通过Exchange ActiveSync访问内部文件共享


                                阅读量   
                                **131236**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://labs.mwrinfosecurity.com/blog/accessing-internal-fileshares-through-exchange-activesync](https://labs.mwrinfosecurity.com/blog/accessing-internal-fileshares-through-exchange-activesync)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01ff7de437eedae530.png)](https://p4.ssl.qhimg.com/t01ff7de437eedae530.png)

**摘要**

Exchange ActiveSync (EAS) 是用于在消息服务器和移动设备之间同步电子邮件、策略和其他内容的协议。

我发现仅仅使用Exchange用户邮箱凭据就可以远程访问Windows 文件共享和内部 SharePoint 站点。我们已经在Exchange 2013和2016版本的默认设置中证实了这一点，尽管在2010版本中已经[删除](https://technet.microsoft.com/en-us/library/aa998911%28EXCHG.140%29.aspx)了 Outlook Web App 文件共享的访问功能。

基于这个研究，MWR[公布](https://labs.mwrinfosecurity.com/tools/peas-access-internal-fileshares-through-exchange-activesync/)了PEAS库，用来协助访问共享文件和执行其他EAS命令。

<br>

**研究**

**目标**

MWR的网络防御顾问会帮助客户设计安全的企业体系结构。作为注重研究的顾问，我们会看中目前企业体系结构中存在的薄弱环节。

Microsoft Exchange是一个广泛使用的企业电子邮件服务器，由于其函数本质，服务器需要从互联网进行访问。外部攻击者会周期性地攻击Exchange，尝试去访问存储在电子邮件中的敏感信息库和目标企业的内部网络。

由于外部接口太多，Exchange存在太多的“攻击面”。电子邮件就是主要的一个，已经有大量的内部电子邮件解析器漏洞报告显示会给Exchange自己带来代码执行类的安全漏洞（从这个[例子](http://blog.talosintel.com/2016/07/vulnerability-spotlight-oracles-outside.html)就可以明显的看出）。最近的新研究还发现攻击者会滥用设置复杂信息处理规定在工作站中实现代码执行。

在这项服务推出的这些年来，已经报告过太多包括Outlook Web Access (OWA)在内的各种问题。

最终，EAS连接器允许手机这类的设备互相连接来交换信息。这份协议相对比较复杂，内容就是加入移动设备的相关规则。

研究的主要目标就是查明EAS中存在的功能性漏洞，尤其是证实远程访问共享文档的可能性（在它被[发现](https://msdn.microsoft.com/en-us/library/cc425499%28EXCHG.80%29.aspx)之后）。为实现这个目标，我将任务分为以下几个子任务：

建立域控制器，并安装Microsoft Exchange 服务器。

测试现有的 Python EAS 项目并适当修改，以提取邮箱中的所有电子邮件。

在安全评估中执行共享文件访问以及其他功能。

**以前的研究**

在之前的文章[《Exchange移动平台的SSL实现弱点》](http://data.openduck.com/wp-posts/2013/12/paper-exchanging/demands.pdf)中，研究人员发现可以利用MitM 远程擦除设备。他们提出的关于访问远程共享文件的几点建议都是无效的，但是他们正确指出了禁用SSL来协助监视EAS信息交换的可行性。

**EAS协议**

可以通过[EAS文件](https://msdn.microsoft.com/en-us/library/cc425499%28EXCHG.80%29.aspx)对该协议做个简单了解。EAS使用XML通过HTTPS编码成WAP 二进制 XML (WBXML)。下面是一个示例：



```
&lt;?xml version="1.0" encoding="utf-8"?&gt; 
&lt;Sync xmlns:airsyncbase="AirSyncBase" xmlns="AirSync"&gt; 
  &lt;Collections&gt; 
    &lt;Collection&gt; 
      &lt;SyncKey&gt;1&lt;/SyncKey&gt; 
      &lt;CollectionId&gt;7&lt;/CollectionId&gt; 
    &lt;/Collection&gt; 
  &lt;/Collections&gt; 
&lt;/Sync&gt;
```

使用十六进制编辑器时，WBXML 看起来是这样的：



```
0000000: 0301 6a00 455c 4f4b 0331 0001 5203 3700 ..j.EOK.1..R.7. 
0000010: 0101 0101 ....
```

这些数据会通过一个 HTTP POST 请求发送到EAS网络站点中，一起被发送的还有呈GET参数形式的用户和设备信息。标头用于授权、会话管理和区分EAS版本。

服务器的响应也是相应的WBXML。

**服务器安装**

虚拟机配置运行的是 Windows 2012 R2 标准 （64 位）。最开始没有足够的RAM来运行OS和Exchange，所以如果想要重复过程，最好使用至少8GB的容量；第二次分配需要10GB，其中正在使用的是7.8GB。

服务器中启用了活动目录，还创建了一个新的目录林，主机也被升级成域控制器。

可以用两个任务来安装Microsoft Exchange Server 2013，这是不同于默认安装的唯一途径。启用“邮箱任务”是因为需要它来控制用户邮箱，这也是Exchange的主要功能。启用”客户端访问任务“是因为这是ActiveSync客户端、Outlook Web Access、 POP3、 IMAP4协议和Web 服务的使用前提。

安装之后，OWA可以通过[https://server-name/owa/](https://server-name/owa/) 访问，EAC可以通过[https://server-name/ecp/](https://server-name/ecp/)访问，这两种访问都依赖于互联网。

最开始就只有一个管理员邮箱。使用EAC可以创建一个新的邮箱，使用OWA可以在新邮箱和管理员邮箱之间成功发送电子邮件。

有关服务器安装的更多详细信息可以在这一研究项目的git存储库中找到。

**测试**

为了对这个协议有一个切实的了解，同时对服务器进行测试，我们在[指南](http://mobilitydojo.net/2010/03/17/digging-into-the-exchange-activesync-protocol/)和协议文件的帮助之下，编写了一个WBXML的HTTP请求，然后利用Python发送给 Exchange 服务器。

用管理员账户发送一个Sync指令的返回值是状态代码126，记录为”UserDisabledForSync“，意思就是ActiveSync 被禁用。尝试使用新的邮箱账户发送相同的命令就没有这样的问题，这就意味着管理员账户在默认情况下存在一些限制行为。

服务器通过互联网响应了EAS请求，不需要进行额外配置。

**现有软件回顾**

我们想要通过搜索Github、Stackoverflow和谷歌来确定一个内容详尽的Python 项目。如果发现现有的 Python 库不适合，其他两个项目就会用来参考编写新软件。

[![](https://p0.ssl.qhimg.com/t01fd37f1b514bc22ef.png)](https://p0.ssl.qhimg.com/t01fd37f1b514bc22ef.png)

[![](https://p2.ssl.qhimg.com/t01a72c8d4e4cfd76c2.png)](https://p2.ssl.qhimg.com/t01a72c8d4e4cfd76c2.png)

只有两个Python项目可以直接与使用EAS的服务器通信：pyActiveSync和py-eas-client。对比这两者的性能评估可以确定哪一个更完整地执行了该协议，哪一个更有利于研究。两个库的包装的编写都是为了创建一个一致的接口，并形成我们此次研究成果中的基础工具。

pyActiveSync

pyActiveSync部分支持EAS 12.1版本，可以执行服务器提供的23个指令中的17个。它附带一些示例代码，但是没有相关文档。

pyActiveSync 需要创建的 Python 源文件被称为 proto_creds.py，其中包含 EAS 服务器地址、 用户名和密码。它会永久地存储在本地数据库中以便于日后恢复。

为了在测试环境下使用库，必须要禁用SSL验证。示例代码试图请求”推荐联系人“，但这是根本不存在的，所以也必须禁用。在此之后，这个库就可以成功地向测试服务器器请求邮件了。

py-eas-client

使用一个恰当的setup.py脚本包就可以成功安装py-eas-client。它只支持23个指令中的4个。

py-eas-client使用 Twisted，也就是说它的功能与 Twisted库的运行方式绑定，这使得扩展变得困难。它还会从 Python 库中生成WBXML，这使得其存在极大的限制，还会为其他用户造成大[问题](http://stackoverflow.com/questions/25433201/create-an-activesync-sendmail-request-in-python)，最终只能选择 libwbxml。

要想在测试环境下使用库，还是需要禁用SSL验证。这会变得更加困难，因为必须要了解Twisted才可以完成。示例代码试图请求索引一个不存在的硬编码，所以这里做了修改，请求所有返回值。在这之后，这个库就可以成功地向测试服务器器请求邮件了。

软件回顾总结

pyActiveSync显然比py-eas-client支持更多的指令，同时更新状态也更佳，还不需要过渡到Twisted。这使得pyActiveSync成为了研究人员的更佳选择。

**潜在攻击**

虽然主要目标是获得共享文件的访问权，我们还是选择使用更全面的方式来调查可能存在的攻击。初步研究表明，Exchange 2010之后的版本都不可能支持共享文件的远程访问，但一定还存在其他的攻击形式。

我们解析了EAS文件，想要整理出每个文档示例部分所支持功能的列表。对于每个示例功能来说，可能的攻击手段应该都使用了STRIDE。

我们做出了一份列表，列出了所有支持功能和潜在攻击。根据研究目标的不同，我们按照优先级别排列潜在攻击。完整表格可以在项目的wiki上查看。

我们打算调查的第一个攻击是是否可以使用EAS指令访问WINDOWS共享文件。

**共享文件访问**

首先在服务器上创建两个windows共享文件。一个设置为需要管理员权限，另一个向所有人开放。将文件放置在两个共享目录下。我们的目标就是远程查看文件内容，并且使用EAS下载文件。

EAS文件表明共享文件内容可以通过搜索指令找到，并且使用ItemOperations指令阅读。要想访问文件，必须将存储类型设置为DocumentLibrary。

因为pyActiveSync不支持搜索功能，所以需要扩充库来实现此功能。

我们使用一个标准的用户邮箱来进行第一次EAS测试。找到一条允许共享的UNC路径，如\test-servershare，但是返回了一个错误代码14，意思就是”需要凭据“。对文档进行进一步检查可以定位到搜索指令[子元素](https://msdn.microsoft.com/en-us/library/gg675461%28v=exchg.80%29.aspx)的用户名和密码元素。发送相同的用户名和密码来验证访问权限，可以获得一份目录列表。

将请求更改为限制管理员权限，状态代码改成5”拒绝访问“。使用管理员凭据再次访问EAS服务器，然后选择搜索，就会看到之前的错误”UserDisabledForSync“。但是使用标准用户账号和管理员凭据再次执行搜索请求就可以顺利地获得目录列表。

下一步利用ItemOperations指令进行提取操作来访问共享文件，这种行为和搜索操作的本质是一致的。

添加一台新的windows7虚拟机到域中来测试是否可以访问不同机器上的共享文件。在此机器上创建一个共享，使用相同的方法，在UNC路径中用计算机名称可以获得共享文件。

此外还发现所有的共享文件都可以通过提供UNC路径来获取，但是使用IP地址或机器的 FQDN 就无法获得。

为了进一步测试权限是否被有效控制，需要启用具体的文件共享。使用ID5145来观察日志内容，可以发现被用于访问共享的账户是搜索选项中提供的账户，而不是另一个具有不同权限的账户。

**<br>**

**阻止Exchange访问共享**

能够下载文件这一功能已经被报告给了Microsoft，MWR相信这是OWA支持功能的遗留代码。Microsoft回应称这种功能是特地设计的，并且指引MWR重写默认允许下载文件的设置。

建议企业禁用访问文件共享。具体做法指南可以[下载](https://technet.microsoft.com/en-us/library/bb123756(v=exchg.160).aspx)，并且将以下这些参数设置成错误：

```
UNCAccessEnabled
WSSAccessEnabled
```

MWR还强烈建议企业在OWA和EAS这样的端点上使用客户凭据。

**<br>**

**检测文件共享访问**

关于攻击者如何利用此功能，研究人员还做了相关调查。

为了鉴别不同的检测手段，创建一个名为filesharetest的新用户邮箱。

如果想要获得共享列表，需要使用下面这些[PEAS](https://labs.mwrinfosecurity.com/tools/peas-access-internal-fileshares-through-exchange-activesync/)指令：

```
python -m peas -u filesharetest -p ChangeMe123 --list-unc='\fictitious-dc' 10.207.7.100
```

想要下载共享文件，需要的指令是：

```
python -m peas -u filesharetest -p ChangeMe123 --dl-unc='\fictitious-dchrpasswords.txt' 10.207.7.100
```

**Exchange管理员中心（EAC）**

EAC显示的是各用户通过EAS访问Exchang e时使用的设备。可以从收件人查看 &gt; 邮箱 &gt; * 特定邮箱 * &gt; 查看详细信息。

使用PEAS工具的结果是带有家庭和模型Python的条目。这就表明如果细节不是伪造的，而是有效的移动设备，这个条目就会很明显。

**Exchange管理shell**

通过web界面进行人工审查在实际操作中会非常耗时。 使用Exchange cmdlet Get-ActiveSyncDevice 列出所有已知设备，然后进行解析、处理和审查会大大提高效率。

**Exchange日志**

从2013版本开始，许多组件都已经默认启用了日志记录。

日志位于&lt;安装驱动&gt;MicrosoftExchange ServerV15Logging。

有以下这些日志文件格式：

```
DateTime,RequestId,MajorVersion,MinorVersion,BuildVersion,RevisionVersion,ClientRequestId,Protocol,UrlStem,ProtocolAction,AuthenticationType,IsAuthenticated,AuthenticatedUser,Organization,AnchorMailbox,UserAgent,ClientIpAddress,ServerHostName,HttpStatus,BackEndStatus,ErrorCode,Method,ProxyAction,TargetServer,,TargetServerVersion,RoutingHint,BackEndCookie,ServerLocatorHost,ServerLocatorLatency,RequestBytes,ResponseBytes,TargetOutstandingRequests,AuthModulePerfContext,HttpPipelineLatency,CalculateTargetBackEndLatency,GlsLatencyBreakup,TotalGlsLatency,AccountForestLatencyBreakup,TotalAccountForestLatency,ResourceForestLatencyBreakup,TotalResourceForestLatency,ADLatency,ActivityContextLifeTime,ModuleToHandlerSwitching,FirstResponseByteReceived,ProxyTime,RequestHandlerLatency,HandlerToModuleSwitching,HttpProxyOverhead,TotalRequestTime,UrlQuery,GenericInfo,GenericErrors
```

列出文件共享



```
日志路径：./HttpProxy/Eas/HttpProxy_2016081619-1.LOG
2016-08-16T19:46:59.920Z,d40cbe9ba27642d280cba142bcc98f4b,15,0,516,25,,Eas,/Microsoft-Server-ActiveSync/default.eas,,Basic,True,FICTITIOUSfilesharetest,,Sid~S-1-5-21-248127371-2460176072-2993231138-1148,Python,10.207.7.213,FICTITIOUS-DC,200,200,,POST,Proxy,fictitious-dc.fictitious.local,15.00.0516.000,CommonAccessToken-Windows,,,,101,576,1,,13,2,,0,1;,1,,0,1,390.6523,46,333,333,337,0,63,396,?Cmd=Search&amp;User=filesharetest&amp;DeviceId=123456&amp;DeviceType=Python,OnBeginRequest=0;,
```

请求的真实目的是Python用户代理和数据库，但是这些都很容易伪造，需要使用很好的设备才能进行正确核对。Cmd = 的搜索字符串表示进行了搜索，但它不区分文件共享搜索与其他类型的搜索。

从共享文件中下载文件



```
日志路径： ./HttpProxy/Eas/HttpProxy_2016081619-1.LOG
2016-08-16T19:56:29.405Z,b9ad62d60d8b4ebc854b75492152a5a4,15,0,516,25,,Eas,/Microsoft-Server-ActiveSync/default.eas,,Basic,True,FICTITIOUSfilesharetest,,Sid~S-1-5-21-248127371-2460176072-2993231138-1148,Python,10.207.7.213,FICTITIOUS-DC,200,200,,POST,Proxy,fictitious-dc.fictitious.local,15.00.0516.000,CommonAccessToken-Windows,,,,103,164,1,,0,0,,0,,0,,0,0,219.0425,60,154,154,156,1,63,217,?Cmd=ItemOperations&amp;User=filesharetest&amp;DeviceId=123456&amp;DeviceType=Python,OnBeginRequest=0;,
```

请求中的Cmd=ItemOperations 字符串表明服务器中有文件被提取，但是不能确定是否是共享文件。

**IIS日志**

IIS日志目录被存储在 C:inetpublogsLogFiles。内容和 Exchange 日志类似。

列出文件共享

日志路径：./W3SVC1/u_ex160816.log

```
2016-08-16 19:46:59 10.207.7.100 POST /Microsoft-Server-ActiveSync/default.eas Cmd=Search&amp;User=filesharetest&amp;DeviceId=123456&amp;DeviceType=Python 443 filesharetest 10.207.7.213 Python - 200 0 0 390
```

日志路径: ./W3SVC2/u_ex160816.log

```
2016-08-16 19:46:59 fe80::2063:570a:9da1:9b71%12 POST /Microsoft-Server-ActiveSync/Proxy/default.eas Cmd=Search&amp;User=filesharetest&amp;DeviceId=123456&amp;DeviceType=Python&amp;Log=PrxFrom:fe80%3a%3a2063%3a570a%3a9da1%3a9b71%2512_V141_HH:fictitious-dc.fictitious.local%3a444_NMS1_Ssnf:T_Srv:6a0c0d0s0e0r0A0sd_SrchP:Doc_As:AllowedG_Mbx:FICTITIOUS-DC.fictitious.local_Dc:FICTITIOUS-DC.fictitious.local_Throttle0_DBL1_CmdHC-813709136_ActivityContextData:Dbl%3aRPC.T%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d104%3bI32%3aROP.C%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d112060104%3bI32%3aMAPI.C%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d405%3bDbl%3aMAPI.T%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d104%3bDbl%3aMBLB.T%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d93068%3bI32%3aRPC.C%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d208%3bDbl%3aBudgUse.T%5b%5d%3d326.487091064453%3bI32%3aADW.C%5bFICTITIOUS-DC%5d%3d4%3bF%3aADW.AL%5bFICTITIOUS-DC%5d%3d2.65195%3bI32%3aADS.C%5bFICTITIOUS-DC%5d%3d9%3bF%3aADS.AL%5bFICTITIOUS-DC%5d%3d1.892422%3bI32%3aADR.C%5bFICTITIOUS-DC%5d%3d3%3bF%3aADR.AL%5bFICTITIOUS-DC%5d%3d1.149233%3bDbl%3aST.T%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d68%3bDbl%3aSTCPU.T%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d60%3bI32%3aMB.C%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d208%3bF%3aMB.AL%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d0.4999998%3bS%3aWLM.Cl%3dCustomerExpectation%3bS%3aWLM.Type%3dEas%3bS%3aWLM.Int%3dTrue%3bS%3aWLM.SvcA%3dFalse%3bS%3aWLM.Bal%3d239706.2_Budget:(D)Owner%3aSid%7eFICTITIOUS%5cfilesharetest%7eEas%7efalse%2cConn%3a1%2cMaxConn%3a10%2cMaxBurst%3a240000%2cBalance%3a239706.2%2cCutoff%3a600000%2cRechargeRate%3a360000%2cPolicy%3aGlobalThrottlingPolicy%5Fcae6aef5-cfdd-4445-992c-d92a88aae1a9%2cIsServiceAccount%3aFalse%2cLiveTime%3a00%3a00%3a00.3264871_ 444 FICTITIOUSfilesharetest fe80::2063:570a:9da1:9b71%12 Python - 200 0 0 326
```

从文件共享中下载文件

日志路径: ./W3SVC1/u_ex160816.log

```
2016-08-16 19:56:29 10.207.7.100 POST /Microsoft-Server-ActiveSync/default.eas Cmd=ItemOperations&amp;User=filesharetest&amp;DeviceId=123456&amp;DeviceType=Python 443 filesharetest 10.207.7.213 Python - 200 0 0 219
```

日志路径: ./W3SVC2/u_ex160816.log

```
2016-08-16 19:56:29 fe80::2063:570a:9da1:9b71%12 POST /Microsoft-Server-ActiveSync/Proxy/default.eas Cmd=ItemOperations&amp;User=filesharetest&amp;DeviceId=123456&amp;DeviceType=Python&amp;Log=PrxFrom:fe80%3a%3a2063%3a570a%3a9da1%3a9b71%2512_V141_HH:fictitious-dc.fictitious.local%3a444_Unc1_Uncb51_ItOfd1_As:AllowedG_Mbx:FICTITIOUS-DC.fictitious.local_Dc:FICTITIOUS-DC.fictitious.local_Throttle0_DBL1_CmdHC1949035196_ActivityContextData:Dbl%3aRPC.T%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d0%3bI32%3aROP.C%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d2742544%3bI32%3aMAPI.C%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d10%3bDbl%3aMAPI.T%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d0%3bI32%3aRPC.C%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d5%3bDbl%3aBudgUse.T%5b%5d%3d140.307403564453%3bI32%3aADS.C%5bFICTITIOUS-DC%5d%3d7%3bF%3aADS.AL%5bFICTITIOUS-DC%5d%3d1.405357%3bI32%3aADR.C%5bFICTITIOUS-DC%5d%3d1%3bF%3aADR.AL%5bFICTITIOUS-DC%5d%3d2.1972%3bI32%3aMB.C%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d5%3bF%3aMB.AL%5bFICTITIOUS-DC.cf3a1fe7-5195-4fb8-b1d6-c2554ecd70c7%5d%3d0%3bS%3aWLM.Cl%3dCustomerExpectation%3bS%3aWLM.Type%3dEas%3bS%3aWLM.Int%3dTrue%3bS%3aWLM.SvcA%3dFalse%3bS%3aWLM.Bal%3d239873.7_Budget:(D)Owner%3aSid%7eFICTITIOUS%5cfilesharetest%7eEas%7efalse%2cConn%3a1%2cMaxConn%3a10%2cMaxBurst%3a240000%2cBalance%3a239873.7%2cCutoff%3a600000%2cRechargeRate%3a360000%2cPolicy%3aGlobalThrottlingPolicy%5Fcae6aef5-cfdd-4445-992c-d92a88aae1a9%2cIsServiceAccount%3aFalse%2cLiveTime%3a00%3a00%3a00.1403074_ 444 FICTITIOUSfilesharetest fe80::2063:570a:9da1:9b71%12 Python - 200 0 0 155
```

**Windows事件日志**

有了详细的文件共享启用日志记录，ID5145创建的事件日志表明访问文件的目标路径。虽然不能确定是否有别于正常访问，但是可以从IIS和Exchange日志中看出一二。

列出文件共享

以下条目在每次共享中都有相应的共享名称。

[![](https://p0.ssl.qhimg.com/t011410f4fbba2f8fbe.png)](https://p0.ssl.qhimg.com/t011410f4fbba2f8fbe.png)

从文件共享中下载文件

[![](https://p1.ssl.qhimg.com/t010c3621a22bb3e2c4.png)](https://p1.ssl.qhimg.com/t010c3621a22bb3e2c4.png)

**<br>**

**建议调查步骤**

解析Exchange cmdlet Get-ActiveSyncDevice 输出，并审查是否存在异常。

解析IIS和Exchange日志的EAS命令条目，特别是包含Cmd=ItemOperations的指令。

确定结果数需要的调查等级。

考虑已知的合法设备和EAS请求是否可以被删除。

参考windows事件日志，以确定EAS指令运行的同时是否可以访问文件共享。

<br>

**结论**

大量企业使用Exchange ActiveSync ，并且可以从外部进行访问。通常企业会控制网络访问权限，比如域控制器网络内的主机以及对敏感数据的控制。

这项研究表明了不架构网络的不安全性。合法功能会被滥用来解压缩文件，远程代码会被执行，攻击者将会成为网络中的霸主。

建议企业仔细设计自己的网络，将其与其他主机隔开，以避免滥用的发生。
