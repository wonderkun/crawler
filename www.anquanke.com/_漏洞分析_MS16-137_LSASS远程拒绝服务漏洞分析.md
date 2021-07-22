> 原文链接: https://www.anquanke.com//post/id/85324 


# 【漏洞分析】MS16-137：LSASS远程拒绝服务漏洞分析


                                阅读量   
                                **93829**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：coresecurity.com
                                <br>原文地址：[https://www.coresecurity.com/blog/unpatched-lsass-remote-denial-service-ms16-137](https://www.coresecurity.com/blog/unpatched-lsass-remote-denial-service-ms16-137)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p5.ssl.qhimg.com/t01dd0d587ab083e760.jpg)](https://p5.ssl.qhimg.com/t01dd0d587ab083e760.jpg)**

**翻译：**[**shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：140RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

<br>

**前言**

在2016年11月8日，Microsoft发布了Windows身份验证方法（MS16-137）的安全更新，其中包括3个CVE：

虚拟安全模式信息泄露漏洞[CVE-2016-7220](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-7220)

本地安全机构子系统的拒绝服务漏洞[CVE-2016-7237](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-7237)

Windows NTLM特权提升漏洞[CVE-2016-7238](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-7238)

<br>

**CVE-2016-7237**

具体CVE-2016-7237而言，相应的补丁被应用到影响LSASS服务的“lsasrv.dll”上面。

该漏洞影响所有Windows版本（包括32位和64位），并且在修补程序发布的同一天，LaurentGaffié（[@PythonResponder](https://twitter.com/PythonResponder)）同步提供了更为详细的报告。同时，他还发布了触发该漏洞的概念验证（PoC）代码。

关于更加详细的说明，请访问：

[http://g-laurent.blogspot.com.ar/2016/11/ms16-137-lsass-remote-memory-corruption.html](http://g-laurent.blogspot.com.ar/2016/11/ms16-137-lsass-remote-memory-corruption.html)

 下面是PoC的下载地址：

[https://github.com/lgandx/PoC/tree/master/LSASS](https://github.com/lgandx/PoC/tree/master/LSASS)

 通过利用这个PoC，我们发现在Windows Server 2008 R2和Windows 7也存在这个漏洞：

[![](https://p4.ssl.qhimg.com/t011f0b0005ab5ff4bc.png)](https://p4.ssl.qhimg.com/t011f0b0005ab5ff4bc.png)

**<br>**

**漏洞分析**

简而言之，该漏洞被报告为远程拒绝服务，其中崩溃是NULL指针引用所导致的。

当LSASS服务崩溃时，攻击目标将在60秒后自动重新启动，对于生产服务器来说，这是无法忍受的。

下面文字引自该报告：

“这允许攻击者远程分配一个巨大的内存块，用来存放不超过20000字符的消息…”

当攻击目标能够接收如此巨大（具体由“Simple Protected Negotiation”确定）的博文时，攻击者基本上就可以通过“Session Setup Request”数据包，使用SMB1或SMB2来利用这个漏洞。

通过下图可以看出，它的具体大小为0x80808080：

[![](https://p0.ssl.qhimg.com/t0190d858e7a371f4a3.png)](https://p0.ssl.qhimg.com/t0190d858e7a371f4a3.png)

 这个尺寸（当然是不怀好意的）将被“NegGetExpectedBufferLength”函数所读取，它是“NegAcceptLsaModeContext”的后继：

[![](https://p4.ssl.qhimg.com/t01017e87cd55bb0d64.png)](https://p4.ssl.qhimg.com/t01017e87cd55bb0d64.png)

 如果这个函数的返回值为0x90312（SEC_I_CONTINUE_NEEDED），那么"LsapAllocateLsaHeap"函数就会据此分配一个硕大的内存块。

[![](https://p3.ssl.qhimg.com/t01c780dcda2fafa057.png)](https://p3.ssl.qhimg.com/t01c780dcda2fafa057.png)

 由于分配的内存块接近4GB，所以可能会失败。

如果分配失败，就为出现NULL指针引用创造了一个必要条件。

<br>

**代码对比**

通过将“lsasrv.dll”的v6.1.7601.23545版本与v6.1.7601.23571版本进行比对，我们可以在“NegpBuildMechListFromCreds”函数中找到CVE-2016-7237的修复代码：

[![](https://p4.ssl.qhimg.com/t01eef0891e7983ec70.png)](https://p4.ssl.qhimg.com/t01eef0891e7983ec70.png)

 简单来说，修复代码会检查包含指向CRITICAL_SECTION对象的指针的结构指针是否为NULL。

由此看来，修复代码的人对于该漏洞存在一些误解，因为根据LaurentGaffié发布的PoC来看，安全问题不在结构指针中，而是在这个结构指向的CRITICAL_SECTION对象的一个字段中，当分配过大的内存块失败的时候，它就会变成NULL！

所以，NULL指针的检查应该在这里：

[![](https://p1.ssl.qhimg.com/t016ac1f2894c2cedb8.png)](https://p1.ssl.qhimg.com/t016ac1f2894c2cedb8.png)



**能触发Windows 8.1/10中的漏洞吗？**

虽然公开的PoC无法在Windows 8.1或Windows 10中触发该漏洞，但研究人员和Microsoft也做出声明，指出这些Windows版本也容易受到攻击。

让我们看看这到底是为什么。

正如我前面所说，“NegGetExpectedBufferLength”函数会从SMB数据包读取这个邪恶的尺寸值。 

然后，该函数必须返回0x90312值（SEC_I_CONTINUE_NEEDED），从而造成分配的内存过大而失败。

不幸的是，在最新的Windows版本中，已经在此函数中添加了一个额外的检查，即将这些恶意的尺寸与0xffff（64KB）进行比较。

如果恶意尺寸大于0xffff（64KB），那么这个函数不会返回0x90312值，而是返回0xC00000BB值（STATUS_NOT_SUPPORTED），这样，就不会引起内存分配失败了，所以这个漏洞就不会触发。

另一方面，如果我们使用小于或等于0xffff（64KB）的恶意尺寸，内存分配也不会失败，自然也不会触发该漏洞。

那么，为什么Windows 8.1和Windows 10易受攻击呢？

虽然内存分配失败时会触发这个bug，但这并不意味着分配的内存必须是巨大的，关键在于LSASS服务没有足够的可用内存来进行分配。

实验证明，只要在Windows 7和2008 R2中建立几个SMB连接并发送值为0x1000000（16 MB）的恶意内存尺寸，就会触发这个漏洞。

问题是，对于最新的Windows版本来说，是不会使用这种尺寸的，因为正如我前面所说的，其上限为64KB。 

因此，触发这个漏洞的唯一方法应该是在LSASS服务中耗尽其内存。为了达到这个目的，可以这样做：在LSASS认证过程中找出可控制的malloc，并创建大量连接来耗尽其内存，直到“LsapAllocateLsaHeap”函数失败为止。也许，这种内存耗尽方法可以很容易地在本地情况下实现。



**结束语**

当我理解了公开的PoC对Windows 10无效的原因之后，我突然意识到，发布的这个漏洞补丁根本就不起作用。

令人惊讶的是，公开漏洞利用代码公布至今已经两个多月了，有那么多的Windows用户在使用这个补丁来提供保护，但是根本没有人注意到这个问题。

直到1月10日，Microsoft发布了一个新的安全公告，其中包括受MS17-004漏洞影响的系统的补丁。

如果我们对比最新的“lsasrv.dll”版本（v6.1.7601.23642），我们可以看到，它是通过修改“NegGetExpectedBufferLength”函数来修复该漏洞的。

简单来说，Windows 8.1和Windows 10上针对数据包的64KB上限的安全检查，现在已添加到其余的Windows版本上了，并且同样使用64KB作为数据包大小的上限。

[![](https://p2.ssl.qhimg.com/t0123e395ddac2dd662.png)](https://p2.ssl.qhimg.com/t0123e395ddac2dd662.png)
