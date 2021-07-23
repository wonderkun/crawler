> 原文链接: https://www.anquanke.com//post/id/173477 


# Kerberos协议探索系列之委派篇


                                阅读量   
                                **277366**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/dm/1024_711_/t01d27427941c02946c.jpg)](https://p4.ssl.qhimg.com/dm/1024_711_/t01d27427941c02946c.jpg)



## 0x00前言

在前两节中说到了关于Kerberos的扫描和Kerberoasting以及金票的利用，本文主要说明一下在kerberos体系中关于委派的利用方式，委派在域环境中其实是一个很常见的功能，对于委派的利用相较于先前说的几种攻击方式较为“被动”，但是一旦利用也会有很大的危害。



## 0x01什么是委派

在域中如果出现A使用Kerberos身份验证访问域中的服务B，而B再利用A的身份去请求域中的服务C，这个过程就可以理解为委派。

例：

[![](https://p3.ssl.qhimg.com/t0140aa71969cc62d5a.png)](https://p3.ssl.qhimg.com/t0140aa71969cc62d5a.png)

User访问主机s2上的HTTP服务，而HTTP服务需要请求其他主机的SQLServer数据库，但是S2并不知道User是否有权限访问SQLServer，这时HTTP服务会利用User的身份去访问SQLServer，如果User有权限访问SQLServer服务才能访问成功。

而委派主要分为非约束委派（Unconstrained delegation）和约束委派（Constrained delegation）两个方式，下面分别介绍两种方式如何实现。

### 1 非约束委派

非约束委派在Kerberos中实现时，User会将从KDC处得到的TGT发送给访问的service1（可以是任意服务），service1拿到TGT之后可以通过TGT访问域内任意其他服务，所以被称为非约束委派。

[![](https://p2.ssl.qhimg.com/t01d2ad05c9388a6596.png)](https://p2.ssl.qhimg.com/t01d2ad05c9388a6596.png)

流程：
1. 用户通过发送KRB_AS_REQ消息请求可转发 TGT（forwardable TGT，为了方便我们称为TGT1）。
1. KDC在KRB_AS_REP消息中返回TGT1。
1. 用户再通过TGT1向KDC请求转发TGT（forwarded TGT，我们称为TGT2）。
1. 4在KRB_TGS_REP消息中返回转发TGT2。
1. 5、用户使用TGT1向KDC申请访问Service1的ST（Service Ticket）。
1. TGS返回给用户一个ST。
1. 用户发送KRB_AP_REQ请求至Service1，这个请求中包含了TGT1和ST、TGT2、TGT2的SessionKey。
1. Service1使用用户的TGT2通过KRB_TGS_REQ发送给KDC，以用户的名义请求能够访问Service2的票据。
1. KDC在KRB_TGS_REP消息中返回Service2到Service1的票据。
1. Service1以用户的名义像Service2发送KRB_AP_REQ请求。
1. Service2响应步骤10中Service1的请求。
1. Service1响应步骤7中用户的请求。
1. 在这个过程中的TGT转发机制，没有限制Service1对TGT2的使用，也就是说Service1可以通过TGT2来请求任意服务。
1. KDC返回步骤13中请求的票据。
15和16即为Service1通过模拟用户来访问其他Service。

可以看到在前5个步骤中User向KDC申请了两个TGT（步骤2和4），一个用于访问Service1一个用于访问Service2，并且会将这两个都发给Service1。并且Service1会将TGT2保存在内存中。

非约束委派的设置：

Windows域中可以直接在账户属性中设置：

[![](https://p1.ssl.qhimg.com/t01430e57c40354646e.png)](https://p1.ssl.qhimg.com/t01430e57c40354646e.png)

### 2 约束委派

由于非约束委派的不安全性，微软在windows2003中发布了约束委派的功能。约束委派在Kerberos中User不会直接发送TGT给服务，而是对发送给service1的认证信息做了限制，不允许service1代表User使用这个TGT去访问其他服务。这里包括一组名为S4U2Self（Service for User to Self）和S4U2Proxy（Service for User to Proxy）的Kerberos协议扩展。

从下图可以看到整个过程其实可以分为两个部分，第一个是S4U2Self的过程（流程1-4），第二个是S4U2Proxy的过程（流程5-10）。

[![](https://p3.ssl.qhimg.com/t017e3d9fb481f8b1fe.png)](https://p3.ssl.qhimg.com/t017e3d9fb481f8b1fe.png)

流程：
1. 用户向Service1发送请求。
1. 这时在官方文档中的介绍是在这一流程开始之前Service1已经通过KRB_AS_REQ得到了用户用来访问Service1的TGT，然后通过S4U2self扩展模拟用户向KDC请求ST。
1. KDC这时返回给Service1一个用于用户验证Service1的ST（我们称为ST1），并且Service1用这个ST1完成和用户的验证过程。
1. Service1在步骤3使用模拟用户申请的ST1完成与用户的验证，然后响应用户。
注：这个过程中其实Service1是获得了用户的TGT和ST1的，但是S4U2Self扩展不允许Service1代表用户去请求其他的服务。
1. 用户再次向Service1发起请求，此时Service1需要以用户的身份访问Service2。这里官方文档提到了两个点：1. Service1已经验证通过，并且有一个有效的TGT。
1. Service1有从用户到Service1的forwardable ST（可转发ST）。个人认为这里的forwardable ST其实也就是ST1。1. Service1代表用户向Service2请求一个用于认证Service2的ST（我们称为ST2）。用户在ST1中通过cname（client name）和crealm（client realm）字段标识。
1. KDC在接收到步骤6中Service1的请求之后，会验证PAC（特权属性证书，在第一篇中有说明）的数字签名。如果验证成功或者这个请求没有PAC（不能验证失败），KDC将返回ST2给Service1，不过这个ST2中cname和crealm标识的是用户而不是Service1。
1. Service1代表用户使用ST2请求Service2。Service2判断这个请求来自已经通过KDC验证的用户。
1. Service2响应Service1的请求。
1. Service1响应用户的请求。
在这个过程中，S4U2Self扩展的作用是让Service1代表用户向KDC验证用户的合法性，并且得到一个可转发的ST1。S4U2Proxy的作用可以说是让Service1代表用户身份通过ST1重新获取ST2，并且不允许Service1以用户的身份去访问其他服务。更多的细节可以参考官方的文档，和RFC4120的内容。

同时注意forwardable字段，有forwardable标记为可转发的是能够通过S4U2Proxy扩展协议进行转发的，如果没有标记则不能进行转发。

[https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/3bff5864-8135-400e-bdd9-33b552051d94](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/3bff5864-8135-400e-bdd9-33b552051d94)

约束委派的配置：

可以在账户属性中将tsvc的委派方式更改为约束委派

[![](https://p4.ssl.qhimg.com/t01236e9898c6e4eea5.png)](https://p4.ssl.qhimg.com/t01236e9898c6e4eea5.png)



## 0x02发现域中的委派主机或账户

在域中，可以通过PowerView脚本来搜索开启了委派的主机和用户。查询非约束委派主要是通过搜索userAccountControl属性包含ADS_UF_TRUSTED_FOR_DELEGATION的主机或账户。而约束委派则通过查询userAccountControl属性包含TRUSTED_TO_AUTH_FOR_DELEGATION的主机或用户。

### 1 非约束委派

通过Import-Module PowerView.ps1加载PowerView脚本之后使用下面的命令进行查询。

查询域中配置非约束委派的账户：

Get-NetUser -Unconstrained -Domain yunying.lab

[![](https://p5.ssl.qhimg.com/t012fa78ec49aa2726e.png)](https://p5.ssl.qhimg.com/t012fa78ec49aa2726e.png)

查询域中配置非约束委派的主机：

Get-NetComputer -Unconstrained -Domain yunying.lab

[![](https://p0.ssl.qhimg.com/t0172e7e1986b482c31.png)](https://p0.ssl.qhimg.com/t0172e7e1986b482c31.png)

在另一个版本的PowerView中采用的是Get-DomainComputer

Get-DomainComputer -Unconstrained -Properties distinguishedname,useraccountcontrol -Verbose | ft -a

[![](https://p0.ssl.qhimg.com/t019265129c3967be96.png)](https://p0.ssl.qhimg.com/t019265129c3967be96.png)

### 2 约束委派

查询域中配置约束委派的账户：

Get-DomainUser –TrustedToAuth -Properties distinguishedname,useraccountcontrol,msds-allowedtodelegateto| fl

[![](https://p0.ssl.qhimg.com/t0177c043009e3da9dd.png)](https://p0.ssl.qhimg.com/t0177c043009e3da9dd.png)

Get-DomainUser -TrustedToAuth -Domain yunying.lab查看设置了约束委派的用户

[![](https://p3.ssl.qhimg.com/t011cf1b55ea99b6513.png)](https://p3.ssl.qhimg.com/t011cf1b55ea99b6513.png)

查询域中配置约束委派的主机:

Get-DomainComputer -TrustedToAuth -Domain yunying.lab

[![](https://p2.ssl.qhimg.com/t0116306567947ecc88.png)](https://p2.ssl.qhimg.com/t0116306567947ecc88.png)



## 0x03非约束委派的利用

上文中说明了两种委派方式，下面结合实验说明针对两种委派的利用方式。

实验

首先环境和前两篇文章相同。假设我们已经获取了一个已经配置了委派的账户权限或者是密码，现在我们通过这些条件来攻击其他账户。

[![](https://p4.ssl.qhimg.com/t017d336281505b6700.png)](https://p4.ssl.qhimg.com/t017d336281505b6700.png)

实验环境：

域：YUNYING.LAB

域控：Windows Server 2008 R2 x64(DC)：用户Administrator

域内主机：Windows Server 2008 R2 x64(s2)：用户tsvc

所需工具：

Mimikatz

实验流程：

在域中只有服务账户才能有委派功能，所以先把用户tsvc设置为服务账号。

setspn -U -A variant/golden tsvc

通过setspn -l tsvc查看配置成功。

[![](https://p3.ssl.qhimg.com/t0116cc69cfbe1508da.png)](https://p3.ssl.qhimg.com/t0116cc69cfbe1508da.png)

然后在“AD用户和计算机”中将tsvc设置为非约束委派模式

[![](https://p5.ssl.qhimg.com/t01edfdd085c94da900.png)](https://p5.ssl.qhimg.com/t01edfdd085c94da900.png)

此时在域控上使用Administrator访问tsvc所在主机S2的SMB服务。

[![](https://p4.ssl.qhimg.com/t011706434b11b22c9e.png)](https://p4.ssl.qhimg.com/t011706434b11b22c9e.png)

我们在S2上通过mimikatz可以导出Administrator发送过来的TGT内容。这里需要使用管理员权限打开mimikatz，然后通过privilege::debug命令提升权限，如果没有提升权限会报kuhl_m_sekurlsa_acquireLSA错误。再使用sekurlsa::tickets /export命令导出内存中所有的票据。

[![](https://p5.ssl.qhimg.com/t01f4f770c71bdb8da3.png)](https://p5.ssl.qhimg.com/t01f4f770c71bdb8da3.png)

可以看到名称为[0;9bec9]-2-0-60a00000-Administrator@krbtgt-YUNYING.LAB.kirbi的这一条即为Administrator发送的TGT。

此时访问域控被拒绝。

[![](https://p3.ssl.qhimg.com/t0150c35d789a3b078f.png)](https://p3.ssl.qhimg.com/t0150c35d789a3b078f.png)

通过kerberos::ptt [0;9bec9]-2-0-60a00000-Administrator@krbtgt-YUNYING.LAB.kirbi命令将TGT内容导入到当前会话中，其实这也是一次Pass The Ticket攻击（有兴趣的可以了解一下）。

通过kerberos::list查看当前会话可以看到票据已经导入到当前会话。

[![](https://p1.ssl.qhimg.com/t01b2d2cd929532629d.png)](https://p1.ssl.qhimg.com/t01b2d2cd929532629d.png)

导入之后已经可以访问域控的共享目录。也就是说每当存在用户访问tsvc的服务时，tsvc的服务就会将访问者的TGT保存在内存中，可以通过这个TGT访问这个TGT所属用户的所有服务。非约束委派的原理相对简单，就是通过获取到的administrator的TGT进行下一步的访问。

这里有一个点就是sekurlsa::tickets是查看内存中所有的票据，而kerberos::list只是查看当前会话中的kerberos票据。更多的mimikatz的使用可以参考[https://github.com/gentilkiwi/mimikatz/wiki](https://github.com/gentilkiwi/mimikatz/wiki)

Print Spooler服务+非约束委派提升至域控权限：

在2018年的DerbyCon中Will Schroeder（@ Harmj0y），Lee Christensen（@Tifkin_）和Matt Nelson（@ enigma0x3）提到了关于非约束委派的新方式，通过域控的Print Spooler服务和非约束委派账户提升至域控权限（[https://adsecurity.org/?p=4056](https://adsecurity.org/?p=4056)），主要的原理就是通过Print Spooler服务使用特定POC让域控对设置了非约束委派的主机发起请求，获取域控的TGT，从而提升权限。



## 0x04约束委派的利用

约束委派由于只指定了特定的服务，所以利用起来相对非约束委派更加复杂，本实验的条件是配置了约束委派的账号，并且已知当前配置了约束委派的当前账户的密码（tsvc的密码）。

### 1 实验

这里环境和上文中不变，依然使用普通域账号tsvc和域Administrator账户。不过增加了一个新的工具kekeo，他和mimikatz是同一个作者。

1）、确认账号tsvc设置了约束委派。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018634fa23befbd99f.png)

通过工具PowerView的查询可以看到域内配置了约束委派的列表：

[![](https://p3.ssl.qhimg.com/t0172d6bd0164e4542e.png)](https://p3.ssl.qhimg.com/t0172d6bd0164e4542e.png)

2）、使用kekeo对域控发起申请TGT的请求。

通过已知的账户名和明文密码对KDC发起请求，得到TGT。

[![](https://p0.ssl.qhimg.com/t01d66c063727a4a5f3.png)](https://p0.ssl.qhimg.com/t01d66c063727a4a5f3.png)

Kekeo# tgt::ask /user:tsvc /domain:yunying.lab /password:admin1234! /ticket:tsvc.kirbi

/user:当前用户名

/domain:所在域名

/password:当前用户名的密码

/ticket:生成票据名称，上图里生成的没有按参数设定的来命名，不重要，也可以直接跳过这个参数

3）、使用kekeo申请TGS票据

[![](https://p0.ssl.qhimg.com/t011db7a79cdaf1e6d9.png)](https://p0.ssl.qhimg.com/t011db7a79cdaf1e6d9.png)

Kekeo#tgs::s4u /tgt:TGT_filename /user:administrator@yunying.lab /service:cifs/dc.yunying.lab

/tgt:上一步通过kekeo生成的tgt票据

/user:想要伪造的用户名写全称（用户名@域名）

/service:想要伪造访问的服务名（服务名/主机的FQDN名称）

4）、从kekeo中使用exit命令退出，然后使用mimikatz将生成的TGS文件导入到Kerberos凭据列表中

[![](https://p0.ssl.qhimg.com/t01e8cc05aeb529961e.png)](https://p0.ssl.qhimg.com/t01e8cc05aeb529961e.png)

这时可以看到导入之后已经能够成功访问域控的共享文件（严格来说应该是非约束委派中设置的SPN的权限）。而且在这个过程中是不需要管理员权限的，只是用当前账户的权限就可以完成，因为不需要从内存中导出票据。

### 2 原理

下面看一下在非约束委派中是如何实现通过非约束委派去获得所设置的SPN的权限的。实验过程其实主要是三个步骤：
1. 请求TGT
1. 请求TGS
1. 将TGS导入内存
主要看1、2两个步骤，第1步中使用Kekeo发起AS-REQ请求去请求TGT。

Kekeo# tgt::ask /user:tsvc /domain:yunying.lab /password:admin1234! /ticket:tsvc.kirbi

[![](https://p2.ssl.qhimg.com/t019fda5a6092948208.png)](https://p2.ssl.qhimg.com/t019fda5a6092948208.png)

这时tsvc获取到了一个TGT，并且kekeo工具将其保存为一个kirbi格式的文件。

第2步，再使用这个TGT申请两个ST文件，上文中说到过在约束委派实现的过程中分为两个部分，分别是S4U2Self扩展和S4U2Proxy扩展。S4U2Self中Service1会代替用户向KDC申请一张用于访问自身的TGS，这个TGS也就是生成的两个TGS中的一个（TGS_administrator@yunying.lab@YUNYING.LAB_tsvc@YUNYING.LAB.kirbi）还有一个TGS是用于访问非受限委派中设置的SPN的TGS（TGS_administrator@yunying.lab@YUNYING.LAB_cifs~dc.yunying.lab@YUNYING.LAB.kirbi）。

[![](https://p0.ssl.qhimg.com/t011db7a79cdaf1e6d9.png)](https://p0.ssl.qhimg.com/t011db7a79cdaf1e6d9.png)

我们抓包也可以看到这里是发起了两次TGS_REQ请求，在第一个TGS_REQ请求的包里面可以看到KRB5-PADATA-S4U2SSELF的标识。并且cname和sname都是tsvc，也是侧面说明这个TGS其实就是拿来验证自身的。

[![](https://p1.ssl.qhimg.com/t01931f79239a3e6d16.png)](https://p1.ssl.qhimg.com/t01931f79239a3e6d16.png)

再看第二个TGS_REQ请求，sname的值为cifs/dc.yunying.lab，也就是截图中非约束委派中“可由此账户提供委派凭据的服务”一栏中添加的SPN。而这个其实就是S4U2Proxy扩展中所申请的TGS票据。

[![](https://p4.ssl.qhimg.com/t01a191721a3ff12b87.png)](https://p4.ssl.qhimg.com/t01a191721a3ff12b87.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01965552a2cc3acee7.png)

关于约束委派的这种攻击方式就是通过在Service1（tsvc）中将自己伪造成用户，然后获取允许约束委派的SPN的TGS的一个过程。



## 0x05委派攻击的防御

通过上文中说到设置了非约束委派的账户权限如果被窃取那么攻击者可能获取非常多其他账户的TGT，所以最好是不要在域中使用非约束委派这种功能。

域中不需要使用委派的账户特别是administrator账户，设置为“敏感用户不能被委派”。

[![](https://p2.ssl.qhimg.com/t018dca1be7cfce0931.png)](https://p2.ssl.qhimg.com/t018dca1be7cfce0931.png)

如果是win2012的系统也可以通过设置受保护的用户组来缓解委派所带来的危害。



## 0x06总结

在两种方式的委派中，非约束委派的实验获取的权限更大，能够通过TGT直接获取目标主机的所有服务权限，而约束委派实验主要是通过TGS来获取约束委派列表中设置的SPN的TGS来获得相应的SPN的权限。

同时在今年有国外的安全人员提出来基于NTLMRelay和约束委派结合进行权限提升的攻击方式，详情可参考下面链接，此处不再赘述：

[https://dirkjanm.io/worst-of-both-worlds-ntlm-relaying-and-kerberos-delegation/](https://dirkjanm.io/worst-of-both-worlds-ntlm-relaying-and-kerberos-delegation/)

这几篇文章也是通过实验来说明分析每一种Kerberos攻击方式的原理和如何实现，个人认为在Kerberos的攻击还是需要结合其他攻击方式才能发挥更大的作用，关于更多Kerberos的不同意见及看法欢迎留言交流，本文暂时到此完结，希望对你有所帮助。

实验工具

[https://github.com/gentilkiwi/mimikatz/releases/tag/2.1.1-20181209](https://github.com/gentilkiwi/mimikatz/releases/tag/2.1.1-20181209)

[https://github.com/gentilkiwi/kekeo/releases/](https://github.com/gentilkiwi/kekeo/releases/)



## 参考链接

[https://adsecurity.org/?p=1667](https://adsecurity.org/?p=1667)

[https://xz.aliyun.com/t/2931#toc-6](https://xz.aliyun.com/t/2931#toc-6)

[http://www.harmj0y.net/blog/activedirectory/s4u2pwnage/](http://www.harmj0y.net/blog/activedirectory/s4u2pwnage/)

[https://docs.microsoft.com/zh-cn/windows-server/security/credentials-protection-and-management/protected-users-security-group#BKMK_HowItWorks](https://docs.microsoft.com/zh-cn/windows-server/security/credentials-protection-and-management/protected-users-security-group#BKMK_HowItWorks)

[https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/1fb9caca-449f-4183-8f7a-1a5fc7e7290a](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/1fb9caca-449f-4183-8f7a-1a5fc7e7290a)

[https://labs.mwrinfosecurity.com/blog/trust-years-to-earn-seconds-to-break/](https://labs.mwrinfosecurity.com/blog/trust-years-to-earn-seconds-to-break/)
