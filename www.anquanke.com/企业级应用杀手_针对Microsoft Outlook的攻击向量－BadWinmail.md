> 原文链接: https://www.anquanke.com//post/id/83206 


# 企业级应用杀手：针对Microsoft Outlook的攻击向量－BadWinmail


                                阅读量   
                                **89258**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://0b3dcaf9-a-62cb3a1a-s-sites.googlegroups.com/site/zerodayresearch/BadWinmail.pdf?attachauth=ANoY7cpruTOb5V9O6YtXlZ4orNs2PuaKoyPWWR6OebVrkwUPWcMZMfgNRYa1BjEsiM5uwtXMQ-lNF2zNB02DJnBN5o1YG4xlXcJncrC-3fEAQMvaAZadi2L95YgXHD5LTtPhc-aVwDdA5vhBs_EiZ2DrN6n-KyWI3prxyxWPHNWX-2e_fTEaAnZ877oQ6KLAh2Wed7UaoV5HTkXTCrV2e-x0QfW0x6drcg%3D%3D&amp;attredirects=0](https://0b3dcaf9-a-62cb3a1a-s-sites.googlegroups.com/site/zerodayresearch/BadWinmail.pdf?attachauth=ANoY7cpruTOb5V9O6YtXlZ4orNs2PuaKoyPWWR6OebVrkwUPWcMZMfgNRYa1BjEsiM5uwtXMQ-lNF2zNB02DJnBN5o1YG4xlXcJncrC-3fEAQMvaAZadi2L95YgXHD5LTtPhc-aVwDdA5vhBs_EiZ2DrN6n-KyWI3prxyxWPHNWX-2e_fTEaAnZ877oQ6KLAh2Wed7UaoV5HTkXTCrV2e-x0QfW0x6drcg%3D%3D&amp;attredirects=0)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01bcc86f81246b5ee6.png)](https://p0.ssl.qhimg.com/t01bcc86f81246b5ee6.png)

**介绍**

由微软公司所开发的Microsoft Outlook是Microsoft Office办公套件的一部分,这个软件已经成为当今计算机世界中最流行的应用程序之一了,尤其是在企业应用环境之中。很多企业的员工几乎每天都会使用Outlook来发送和接受电子邮件。除此之外,他们还会使用Outlook来管理类似日程表和会议邀请等信息。如果你想要了解更多有关Microsoft Outlook的信息,请点击查看[维基百科](https://en.wikipedia.org/wiki/Microsoft_Outlook)的相关介绍。

**Outlook的安全缓解/增强方案**

考虑到Outlook是一个如此重要的应用程序,微软公司理所应当地采取了很多安全缓解和增强措施以保证Outlook在使用过程中的数据安全,这些措施包括:

针对某些文件类型,例如那些直接附带有可执行代码的文件,Outlook会自动将其屏蔽。比如说,在用户对信息做进一步确认之前,系统会自动屏蔽附件中的.exe文件,具体情况如下图所示:

[![](https://p3.ssl.qhimg.com/t010e081f32c31ccc5f.png)](https://p3.ssl.qhimg.com/t010e081f32c31ccc5f.png)

针对那些可能会给用户带来潜在安全风险的文件,当用户尝试打开此类附件的时候,Outlook会弹出一个警告对话框来提醒用户。当用户尝试打开一个.html文件时,系统会弹出如下图所示的警告对话框。用户是无法直接打开这种类型的附件的。

[![](https://p3.ssl.qhimg.com/t01f13f73bec05c057b.png)](https://p3.ssl.qhimg.com/t01f13f73bec05c057b.png)

对于类似Word,PowerPoint,或者Excel等类型的Office文档而言,用户可以直接通过双击文件来打开此类附件,用户甚至还可以通过直接单击附件图标来快速浏览此类文档的内容。下图显示的是用户在Outlook 2016中快速浏览一份Word文档内容的界面截图:

[![](https://p2.ssl.qhimg.com/t015d75ec543cb37cf5.png)](https://p2.ssl.qhimg.com/t015d75ec543cb37cf5.png)

无论这份文档是通过快速浏览的方式打开的,还是通过双击直接打开的,系统都会将这份文档转存到“Office沙盒”之中,Office的这个功能也叫“[保护浏览](https://support.office.com/en-nz/article/What-is-Protected-View-d6f09ac7-e6b9-4495-8e43-2bbcdbcb6653)”功能。根据[MWR实验室的研究报告](https://labs.mwrinfosecurity.com/system/assets/1015/original/Understanding_The_Microsoft_Office_2013_Protected_View_Sandbox.pdf),Office的沙盒是十分健壮的,这也就使得Office的终端用户能够避免绝大部分由Outlook所带来的安全风险。

然而,研究人员在对Outlook进行了更加深入的分析之后发现,Outlook中还存在很多非常严重的安全问题,这些安全问题很可能会被攻击者利用来绕过我们之前所提到的那些安全缓解措施。除此之外,研究人员还发现了一种针对Outlook的新型攻击方式,通过这种攻击方式,匿名攻击者仅通过一封电子邮件就能够获得目标主机的控制权。我们将会在接下来的章节中进行更加深入的探讨。

**OLE机制**

正如我们所知,微软公司在Office Word,Excel,PowerPoint,以及WordPad等应用程序中广泛使用了对象链接与嵌入(OLE)技术。如果你想要了解更多关于Office文档OLE功能的信息,请点击查看这篇发表于2015年美国黑帽黑客大会上的[报告](https://sites.google.com/site/zerodayresearch/Attacking_Interoperability_OLE_BHUSA2015.pdf)。

然而,之前所发表的研究报告只对Office(或RTF)文件中的OLE功能进行了讨论,却没有对Outlook或者电子邮件的OLE功能进行论述。作者发现,Outlook同样支持OLE功能,但Outlook中的OLE功能却暴露出来了非常严重的安全问题。

**企业级应用杀手-TNEF格式**

传输中性封装格式(TNEF)是微软公司专为Outlook设计的电子邮件格式(作者怀疑,也许只有Outlook支持这种格式)。如果你想要了解更多关于TNEF格式的详细信息,请点击查看[维基百科](https://en.wikipedia.org/wiki/Transport_Neutral_Encapsulation_Format)的相关介绍。

一封“TNEF”格式的电子邮件,其初始内容一般如下图所示:

[![](https://p4.ssl.qhimg.com/t0138cde067def11485.png)](https://p4.ssl.qhimg.com/t0138cde067def11485.png)

如上图所示,“Content-Type(邮件内容类型)”的值被设置为了“application/ms-tnef”,文件名通常为“winmail.dat”。“content(邮件内容)”通常是一个经过base64编码方式解码的“TNEF”文件。微软公司对TNEF文件格式进行了非常详细的解释和说明,具体信息请点击[这里](https://msdn.microsoft.com/en-us/library/cc425498(v=exchg.80).aspx)进行查看。

顺便在此提一提,作者将这种新型的攻击向量取名为“BadWinmail”,因为在“TNEF”格式的电子邮件中存在一个特殊的文件名-“winmail.dat”。

正如TNEF的解释文档所描述的那样,当“PidTagAttachMethod”被设置为了“ATTACH_OLE”之后,“附件文件(winmail.dat文件所包含的另一个文件)”将会被系统存储为一个OLE对象,在[MSDN网站](https://msdn.microsoft.com/en-us/library/cc815439(v=office.12).aspx)上也可以找到相关的描述信息。

下图显示的是一个结构极其简单的winmail.dat文件:

[![](https://p1.ssl.qhimg.com/t01727b16bbc562e615.png)](https://p1.ssl.qhimg.com/t01727b16bbc562e615.png)

一个恶意的winmail.dat文件会包含一个OLE对象,这个对象很有可能也会带有下列字节数据。根据“[MS-OXTNEF](http://download.microsoft.com/download/5/D/D/5DD33FDF-91F5-496D-9884-0A0B0EE698BB/%5BMS-OXTNEF%5D.pdf)”说明文档中的介绍(章节2.1.3.3.15-attAttachRendData属性),其中的一些字节数据代表了下列属性(作者的注释写在了右侧):

[![](https://p2.ssl.qhimg.com/t014be21c650d17edad.png)](https://p2.ssl.qhimg.com/t014be21c650d17edad.png)

“02 00”表示的是winmail.dat文件中的“附件流”,这部分数据会被系统视作一个OLE对象。

这样一来,我们就可以“构建”一个TNEF格式的电子邮件,并将其发送给目标用户了。当用户读取这封电子邮件时,嵌入在这封电子邮件中的OLE对象将会被自动加载。在下面给出的例子中,当用户阅读这封电子邮件时,Excel的OLE对象将会被自动加载。

[![](https://p1.ssl.qhimg.com/t01e3d9c56146a96bee.png)](https://p1.ssl.qhimg.com/t01e3d9c56146a96bee.png)

当我们右键点击一个操作对象时,我们可以从弹出的Excel菜单中看到OLE对象已经成功地加载了。

作者的研究测试结果显示,有很多的OLE对象可以通过电子邮件来进行加载。这也就暴露出了一个非常严重的安全漏洞。正如我们之前所讨论的,Outlook已经屏蔽了很多不安全的附件了,但它却允许用户在其沙盒之中打开和查看Office文档,这一功能就让之前所有的安全措施形同虚设了。我已经进行了大量的研究和测试,并且发现Flash OLE对象(CLSID: D27CDB6E-AE6D-11cf-96B8- 444553540000)也可以通过这一功能来进行加载。将一个Flash漏洞封装在一个带有OLE对象的TNEF邮件之后,只要目标用户读取了这封电子邮件,攻击者就可以在目标用户的计算机上执行任意代码了。

我们之所以会使用Flash OLE对象来举例说明,是因为攻击者往往都能够轻而易举地获取到Flash的0 day漏洞信息。但是请注意,还有很多其他的OLE对象也是攻击者可以利用的,不仅是Flash OLE对象,Outlook还可以加载很多其他类型的OLE对象。

**其他的攻击向量-MSG文件格式**

除此之外,作者还发现了另一种嵌入OLE对象的方式:即.msg文件格式。在默认设置下,Outlook会将一个.msg附件文件视作是安全的,因此,即便用户只是想要快速浏览附件的内容,Outlook程序也会直接打开这个.msg文件。

微软公司对[MSG格式](http://download.microsoft.com/download/5/D/D/5DD33FDF-91F5-496D-9884-0A0B0EE698BB/%5BMS-OXMSG%5D.pdf)也进行了非常详尽的描述,在其说明文档中,章节“2.2.2.1-嵌入式消息对象存储”, “2.2.2.2-自定义附件存储” ,以及“3.3-自定义附件存储”都向用户详细介绍了在.msg文件中定义OLE对象的方法。

**影响:这是一种完美的APT攻击技术**

正如大家所知,Flash是一个非常不安全的应用程序,时间也已经证明了这一切。这些年来,我们已经发现了大量的Flash漏洞,而且还有大量的Flash 0 day漏洞被攻击者广泛地利用了。为了降低和缓解Flash内容所带来的安全风险,现代浏览器的开发商们正在研究能够将Flash内容在沙盒环境中打开的方法。比如说,在谷歌的Chrome浏览器中,Flash是以Pepeer Flash的形式运行在Chrome沙盒之中的。在IE11浏览器中,用户是在浏览器的[保护模式](https://msdn.microsoft.com/en-us/library/bb250462(v=vs.85).aspx)下查看Flash的内容,这同样也是一种应用程序沙盒。在微软公司为Windows 10操作系统所发布的新型Edge浏览器中,所有的Flash内容都是在[加强型保护模式](http://blogs.msdn.com/b/ieinternals/archive/2012/03/23/understanding-ie10-enhanced-protected-mode-network-security-addons-cookies-metro-desktop.aspx)下运行的,这种模式的沙盒要比之前普通的保护模式更加的健壮。

Office文档同样也可以嵌入Flash内容,这也就使得Office文档变得没那么安全了。然而,微软公司也有相应的对策-从互联网上下载下来的Office文档或者通过电子邮件附件接收到的Flash文件都将会在Office沙盒中运行,这也就降低了恶意Office文件所带来的安全风险,我们在之前的章节已经对这种机制进行过论述了。

然而,微软公司却没有为Outlook设置沙盒。当Outlook以“中等”安全模式运行并处理电子邮件时,根本就没有沙盒存在。

[![](https://p5.ssl.qhimg.com/t01122401ec44fb21b5.png)](https://p5.ssl.qhimg.com/t01122401ec44fb21b5.png)

 这意味着什么?这也就意味着,如果攻击者能够将一封嵌入了Flash漏洞(通过“TNEF”格式)的电子邮件发送给目标用户,而且只要目标用户读取(或者我们也可以说是“预览”)这封邮件,嵌入在邮件中的Flash漏洞将会在“outlook.exe”进程中执行,攻击者便能够获取目标主机当前用户的相同权限,这是一种非常完美的获取目标系统控制权的方法!

既然Outlook会在程序启动之后自动预览最新接收到的电子邮件,那么这也就意味着如果最新接收到的一封电子邮件是一封攻击邮件,那么目标用户在面对这次攻击时就没有任何的选择了-他或她甚至都不需要读取或预览这封攻击邮件的内容。

下面的截图显示的是目标用户预览收件箱中的电子邮件时所发生的情况:

1.     系统自带的计算器程序将会弹出,这也就意味着攻击者成功地利用了Flash漏洞。

2.     Outlook进程以及计算器的calc.exe进程都会一同运行,这也就意味着Outlook中并不存在沙盒。

3.     Flash的二进制代码(Flash.ocx)将会在Outlook进程中进行加载。

[![](https://p0.ssl.qhimg.com/t016f4cb8970023943f.png)](https://p0.ssl.qhimg.com/t016f4cb8970023943f.png)

更加糟糕的是,从Windows 8操作系统开始,微软公司默认将Flash Player(ActiveX版本)整合进了操作系统之中,这也就意味着所有版本的Windows 8,Windows 8.1,Windows 10操作系统在默认配置下都将会受到这种攻击向量的影响。

这也就意味着,攻击者如果得到了一个Flash 0 day漏洞(鉴于这些年来发生了如此之多的与Flash 0 day攻击有关的事件,相比这也并不是什么困难的要求了),那么他就可以对任意一个正在Windows 8/8.1/10操作系统上使用Outlook客户端的用户进行攻击了,当然了,如果你在Windows 7操作系统上也安装了Flash ActiveX,那么你也逃脱不了黑客的攻击。

所有的攻击者都必须知道目标用户的电子邮件地址;

所有的目标用户需要做的就是读取或预览攻击者所发送的电子邮件信息;

你可以想想看,攻击者只需要一个Flash 0 day漏洞,就可以控制一家商业公司CEO的计算机,,而且大多数的企业员工每天都会使用Outlook,那么他或她就可以读取所有的机密邮件了,而且攻击者能做的远远不仅于此。这是一种非常完美的有针对性的攻击方式。

除此之外,攻击者还可以利用这种攻击方式来发动蠕虫攻击,但这种情况自从Vista的发布之后就很少发生在Windows操作系统之中了。当攻击者通过电子邮件向目标主机发动了蠕虫攻击之后,蠕虫病毒会将目标主机中所有的通信地址进行整合,然后将病毒通过电子邮件传播出去。

**演示**

为了帮助读者更好地对这种攻击方式进行分析,并且了解此类攻击的影响。读者专门制作了一个小视频,用于给读者讲解“BadWinmail”攻击向量的严重性。用户可以点击后面的链接来观看这个在线视频([https://youtu.be/ngWVbcLDPm8](https://youtu.be/ngWVbcLDPm8))。在演示视频中,作者使用的Flash漏洞是由Hacking Team泄漏出来的,其版本较老,CVE-ID应该是CVE-2015-5122。因此,为了保证能够成功利用这个Flash漏洞,Windows中的Flash版本应低于18.0.0.203。如需获取更多具体的信息,请观看演示视频。

这种攻击方式适用于所有安装了Office套件的Windows操作系统之中,其中包括安装了Outlook 2007/2010/2013/2016的Windows 7/8/8.1/10操作系统。

**补丁和解决方案**

自从这个问题于2015年10月底被发现并且报告之后,作者就与微软公司进行了合作,并一同努力解决这个存在于Outlook之中的严重安全问题。微软公司于2015年12月8日成功修复了这一安全问题,具体信息可以查看微软公司的安全公MS15-1310(CVE-2015-6172)。微软公司强烈建议用户立刻安装修复补丁。

由于某些特殊原因,可能有的用户无法安装官方的补丁程序,这些用户可以参考公告MS15-131中所提供的解决方案,微软公司建议此类用户尽可能只读取电子邮件中的明文内容。除此之外,作者还建议用户在注册表中设置一个“Office Kill-bit”项,来防止Outlook加载“高风险”的Flash内容(CLSID为D27CDB6E-AE6D-11cf-96B8-444553540000)。作者在进行了测试之后,已经证实了下列注册表项的确能够防止Outlook客户端加载Flash内容(请注意:如果你使用的是64位的Windows操作系统,那么你需要设置相应的注册表项,下列注册表项仅适用于32位操作系统)。

Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINESOFTWAREMicrosoftOfficeCommonCOM Compatibility`{`D27CDB6E-AE6D- 11cf-96B8-444553540000`}`]

"Compatibility Flags"=dword:00000400

**结论**

在这篇报告中,作者披露了一种能够攻击Outlook的新型攻击向量,攻击者能够通过电子邮件来对目标用户进行攻击,作者将其命名为“BadWinmail”。除此之外,攻击者还可以将Flash漏洞封装进一个TNEF格式的电子邮件(或MSG附件)。只要Outlook的用户读取或预览电子邮件中的附件内容,那么将会给用户带来严重的影响。因为Outlook中并没有沙盒,这将允许攻击者迅速地获取目标主机的控制权限。

BadWinmail是一种完美的攻击方式。由于其严重性,以及基于电子邮件的攻击特性,攻击者只需要知道目标用户的电子邮箱地址,就可以对目标发动攻击。
