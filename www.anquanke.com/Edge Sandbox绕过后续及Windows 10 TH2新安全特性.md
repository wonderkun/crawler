> 原文链接: https://www.anquanke.com//post/id/82941 


# Edge Sandbox绕过后续及Windows 10 TH2新安全特性


                                阅读量   
                                **85707**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01716c55d2a02e51ea.jpg)](https://p3.ssl.qhimg.com/t01716c55d2a02e51ea.jpg)

作者：[mj0011](http://blogs.360.cn/blog/author/mj0011/)

在11月6日的韩国PoC(Power of Community)安全会议上,笔者介绍了一些Windows 10 RTM中的一些新安全特性,以及他们在过去的TP版本中发生的安全问题,同时,笔者还重点介绍了一个Windows 10 Edge沙箱的逃逸漏洞,以及如何将其(结合一个RCE漏洞)组装成彻底攻破Edge浏览器的方法和演示,包括笔者同微软长达半年沟通最终促成他们决定修复漏洞的过程。

因为这个漏洞目前仍然是未修复的0day状态,在微软的要求下, 在PoC的演讲中笔者对关键部分做了一些mask,议题Slides也并未公开,因此这里也不会过多讨论这个漏洞。

笔者拿到Windows 10 TH2版本后,周末找了点时间在TH2上测试了下这个漏洞,发现这个版本上微软通过两个方式对这个漏洞做了一些缓和:

1. 将漏洞需要利用的broker接口更换了另一个, 这个很容易绕过,更换接口的CLSID和IID就可以继续调用了

2. 该漏洞利用需要结合针对某些站点的URL跳转漏洞,微软将笔者提交的Exploit中利用的某个特定站点从可用站点列表中删除了,当然,发现一个新的也很容易。**(这里要感谢@黄源小童鞋)**

在解决这两个问题后, 笔者发现新的Exploit仍然无法工作。 笔者调试了一下发现,Edge和Windows 10 TH2里新增了一些安全特性,当然Windows 10 TH2中还开始加入了对Intel SGX技术(Enclave)的支持,也增强了SILO等, 但本文关注在这几个影响笔者的Exploit工作的新特性。

****

**Edge &amp; Windows 10 TH2 新安全特性**

经过调试发现, Edge的render进程(MicrosoftEdgeCP.exe)在加载Exploit DLL时就失败了,追溯到kernel32!LoadLibraryA,发现它直接就返回了ERROR_INVALID_IMAGE_HASH,在进一步跟踪LdrLoadDll/NtCreateSection直到内核,发现Windows 10 TH2中新增了针对三项DLL加载的安全特性:

1. 针对特定进程,禁止加载未签名的DLL(SignatureMitigationOptIn)

2. 针对特定进程, 禁止加载远程DLL(ProhibitRemoteImageMap)

3. 针对特定进程, 禁止加载文件的完整性级别为Low的镜像文件(ProhibitLowILImageMap)

这三项功能都包括在Mitigation Policy中, 这是从Windows 8开始微软存放进程和全局缓和状态的方式,可以通过公开的API SetProcessMitigationPolicy/GetProcessMitigationPolicy(实际是NtQuery/SetInformationProcess-&gt;ProcessMitigationPolicy)来查询和设置进程的状态, Google Chrome也使用了这两个API来增强安全性。Mitigation Policy同时还可以通过IEFO、父进程继承和创建进程时设置StartupInfoEx中的Attributes List来进行设置。

微软目前公开的对于G(S)etProcessMitigationPolicy的文档仅截至到Windows 8为止([https://msdn.microsoft.com/en-us/library/windows/desktop/hh769085(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/hh769085(v=vs.85).aspx)) , 对于Windows 8.1、Windows 10 RTM和TH2中中新增的缓和策略选项并没有文档化, 这里,笔者给出在Windows 10 TH2上最新的所有Mitigation Policy及其数据结构:



```
typedef enum _PROCESS_MITIGATION_POLICY
`{`  
ProcessDEPPolicy,
ProcessASLRPolicy,
ProcessDynamicCodePolicy,
ProcessStrictHandleCheckPolicy,
ProcessSystemCallDisablePolicy,
ProcessMitigationOptionsMask,
ProcessExtensionPointDisablePolicy,
ProcessControlFlowGuardPolicy,
ProcessSignaturePolicy,
ProcessFontDisablePolicy,
ProcessImageLoadPolicy,
MaxProcessMitigationPolicy
`}` PROCESS_MITIGATION_POLICY, *PPROCESS_MITIGATION_POLICY;
```

针对ProcessControlFlowGuardPolicy:

```
typedef struct _PROCESS_MITIGATION_CONTROL_FLOW_GUARD_POLICY `{`
union `{`
DWORD  Flags;
struct `{`
DWORD EnableControlFlowGuard : 1;
DWORD ReservedFlags : 31;
`}`;
`}`;
`}` PROCESS_MITIGATION_CONTROL_FLOW_GUARD_POLICY, *PPROCESS_MITIGATION_CONTROL_FLOW_GUARD_POLICY;
```

针对ProcessSignaturePolicy:

```
typedef struct _PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY
`{`
union `{`
DWORD  Flags;
struct `{`
DWORD MicrosoftSignedOnly : 1;
DWORD StoreSignedOnly : 1;
DWORD MitigationOptIn : 1;
DWORD ReservedFlags : 29;
`}`;
`}`;
`}` PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY, *PPROCESS_MITIGATION_BINARY_SIGNATURE_POLICY;
```

针对ProcessFontDisablePolicy( 在笔者去年关于Windows 10 TP 9926安全性中有提到)

```
typedef struct _PROCESS_MITIGATION_FONT_DISABLE_POLICY `{`
union `{`
DWORD  Flags;
struct `{`
DWORD DisableNonSystemFonts : 1;
DWORD AuditNonSystemFontLoading : 1;
DWORD ReservedFlags : 30;
`}`;
`}`;
`}` PROCESS_MITIGATION_FONT_DISABLE_POLICY, *PPROCESS_MITIGATION_FONT_DISABLE_POLICY;
```

针对ProcessImageLoadPolicy:



```
typedef struct _PROCESS_MITIGATION_IMAGE_LOAD_POLICY
`{`
union `{`
DWORD  Flags;
struct `{`
DWORD NoRemoteImages : 1;
DWORD NoLowMandatoryLabelImages : 1;
DWORD ReservedFlags : 30;
`}`;
`}`;
`}`PROCESS_MITIGATION_IMAGE_LOAD_POLICY, *PPROCESS_MITIGATION_IMAGE_LOAD_POLICY;
```

这里提到的三项安全特性,就分别来自ProcessSignaturePolicy的MitigationOptIn和本次TH2新增的ProcessImageLoadPolicy的NoRemoteImages &amp; NoLowMandatoryLabelImages。

这三个选项都是一旦设置(无论通过IEFO还是继承或创建进程选项指定),就无法再次关闭的,由于策略都在内核中实现,因此即使获得代码执行权限,也无法关闭这三个功能。

对于MitigationOptIn:

该选项实际操作了进程的EPROCESS-&gt;Flags3.SignatureMitigationOptIn 标志。

在加载DLL或EXE镜像时,内核调用NtCreateSection试图创建镜像的Section,此时调用MiCreateSection/MiCreateNewSection,接着会调用SeGetImageRequiredSigningLevel,该函数试图获得当前创建镜像所需要的Signing Level(关于Signing Level , Alex Ionescu在之前介绍Win8.1的文章Protected Processes Part 3 : Windows PKI Internals (Signing Levels, Scenarios, Root Keys, EKUs &amp; Runtime Signers)中有详细介绍,http://www.alex-ionescu.com/?p=146).

在此函数中,会判断EPROCESS-&gt;Flags3.SignatureMitigationOptIn若为TRUE , 则强制要求6(Store)级别以上的Signing Level,即要求镜像存在签名,接着MiCreate(New)Section会使用MiValidateSectionCreate(最终调用CI.DLL中签名验证算法) 来验证镜像的签名 ,如果不符合,则会返回错误,拒绝镜像的Section创建,导致DLL加载失败。

也就是说,设置了SignatureMitigationOptIn的Edge浏览器,加载任意未签名的模块,在创建Section时就会失败。

同时,为了防止某些频繁注入的DLL(例如全局钩子)消耗大量内核资源进行签名验算, Edge浏览器的Shim引擎Eshims.dll挂钩了kernel32!LoadLibraryA等函数, 会缓存已经验证未无效签名的DLL信息, 当再次遇到加载这类DLL时,直接返回ERROR_INVALID_IMAGE_HASH,拒绝加载。

****

**对于ProhibitRemoteImageMap和ProhibitLowILImageMap**

针对这两个的验证存在于镜像的Section映射(而不是创建)的过程中,在MiMapViewOfImageSection函数中, 新增了针对MiAllowImageMap函数的调用,该函数检查:

1.如果进程设置了ProhibitRemoteImageMap(即ProcessLoadImagePolicy.NoRemoteImages) ,则检查Section Object-&gt;RemoteImageFileObject或RemoteDataFileObject是否为TRUE(该域标志了镜像是否从远程加载),针对从远程加载的section,拒绝映射

2.如果进程设置了ProhibitLowILImageMap(即ProcessLoadImagePolicy.NoLowMandatoryLabelImages),则获取对应文件并检查其安全属性的完整性级别是否Low或更低(一般由创建文件的进线程完整性级别决定),如果是由低完整性级别文件创建的Section,就拒绝加载。

目前Edge render进程打开了NoRemoteImages,并未打开NoLowMandatoryLabelImages,而后者其实也可以用于针对一些非沙箱进程设置,阻止他们被攻击导致加载沙箱内进程的DLL。

了解了这三个安全特性,其实可以想到它们只是针对旧的Exploit提升了门槛,只要获得了代码执行能力,针对地只要使用一些特殊方式,或者干脆自己完成DLL映射过程(通过内存分配),还是可以正常加载想要的payload代码,完成攻击。最后,加上前面两个改动和针对这个机制的绕过,笔者针对Edge Sandbox的绕过依然可以在Windows 10 TH2上完整实现攻破Edge浏览器。

但这三个安全特性确实对旧Exploit或者某些特定类型的漏洞攻击提升了门槛甚至可能完全防御,也是本次Windows 10 TH2中值得一看的新安全特性。根据Google安全研究人员的说法,在后续的Chrome版本上,我们也有望看到对这些特性的开启,增强Chrome的安全性。
