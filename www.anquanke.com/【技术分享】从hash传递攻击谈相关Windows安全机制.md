
# 【技术分享】从hash传递攻击谈相关Windows安全机制


                                阅读量   
                                **230644**
                            
                        |
                        
                                                                                                                                    ![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85995/t0181521cfcfd2d0637.jpg)](./img/85995/t0181521cfcfd2d0637.jpg)**

作者：existX@Syclover（三叶草安全技术小组）

预估稿费：400RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

**path-the-hash,中文直译过来就是hash传递，在域中是一种比较常用的攻击方式。**在网上所找到的资料，大多数是介绍如何实现此类攻击，但对于它背后所隐藏的关于Windows安全机制的一些知识，却鲜有探讨。**本文的目的就是从pass-the-hash这一古老的话题切入，由攻击过程中Windows的行为引出它背后的安全机制，让大家对Windows有更深入的了解。**

<br>

**攻击方式**

通常来说，pass-the-hash的攻击模式是这样的：

**获取一台域主机高权限**

**利用mimikatz等工具导出密码hash**

**用导出的hash尝试登陆其他域主机**

下面简单演示一下一般的攻击方法：

**mimikatz抓取密码**

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0138fc46a2e527a667.png)

**传递hash**

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0194f31e8f60b9e0db.png)

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f2088eb476258378.png)

可以看到，已经能够访问到远程的机器了。 

<br>

**一个试验引出的问题**

虽然pth是一个比较老的套路了，但实际上关于这个话题能谈到的还有很多。其中值得注意的包括微软发布的补丁kb2871997。据说这个补丁能够阻止pth，并且还能阻止mimikatz抓取明文密码。 

有意思的是，事情并不是那么简单，我们做一个实验：

**攻击机:192.168.1.109 **

**windows server 2008 r2**

**靶机:192.168.1.103 **

**windows server 2008 r2 **

这里有两点需要注意，一是pth所使用的账户User并不是RID为500的账户，但它是本地管理员组的成员，二是这并非在域环境中进行实验，所有的账户都不是域账户

首先在靶机上查看一下补丁情况

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018d97b92dd6376fc8.png)

可以看到，没有安装kb2871997

然后在攻击机上传递hash

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d6d3db4414364aeb.png)

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0173e1043033cf6153.png)

提示拒绝访问 

接下来我们再尝试以RID为500的Administrator用户pth，

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01117b5cfb627c0ba3.png)

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fd1b4addb1e60d8c.png)

这下成功了。那如果我们在域环境下，使用域账户情况又如何呢？

这次使用域账户User，User是一个RID非500的域管理员组成员

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0176403b2a92331267.png)

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01afef9bcd81aebe60.png)

从上面的实验中我们可以得出一个结论：即便没有打KB2871997，windows server 2008 r2依然阻止了RID非500，也即非内置管理员账户的远程登陆，但这条规则对于域账户并不适用。下面我们来深入探究原因。

<br>

**UAC与令牌完整性**



微软在文章[Description of User Account Control and remote restrictions in Windows Vista](https://support.microsoft.com/en-us/help/951016/description-of-user-account-control-and-remote-restrictions-in-windows-vista)中提到：

When a user who is a member of the local administrators group on the target remote computer establishes a remote administrative connection…they will not connect as a full administrator. The user has no elevation potential on the remote computer, and the user cannot perform administrative tasks. If the user wants to administer the workstation with a Security Account Manager (SAM) account, the user must interactively log on to the computer that is to be administered with Remote Assistance or Remote Desktop.

根据微软的描述，当一个本地管理员组的用户远程登陆时，它不是以一个“完全”的管理员身份登陆。什么是“完全”呢？ 

在[Pass-the-Hash Is Dead](https://www.harmj0y.net/blog/redteaming/pass-the-hash-is-dead-long-live-localaccounttokenfilterpolicy/)（强烈推荐！）中，有这么一段话：

for any non-RID 500 local admin account remotely connecting to a Windows Vista+ machine, whether through WMI, PSEXEC, or other methods, the token returned is “filtered” (i.e. medium integrity) even though the user is a local administrator. Since there isn’t a method to remotely escalate to a high-integrity context, except through RDP (which needs a plaintext password unless ‘Restricted Admin’ mode is enabled) the token remains medium integrity. So when the user attempts to access a privileged resource remotely, e.g. ADMIN$, they receive an “Access is Denied” message despite technically having administrative access. I’ll get to the RID 500 exception in a bit

以作者的观点来看，返回的令牌被过滤了，它仅有一个“中等完整性”。也就是说，这个令牌不是“完全”的。这里的完全，就是指令牌的完整性级别。

<br>

**完整性级别**

“……完整性级别能够修改自主访问行为，以便区分以同一用户身份运行，并被同一用户拥有的不同进程和对象，从而提供在同一用户账户内隔离代码和数据的能力。强制完整性级别（MIC,mandatory integrity control）机制通过把调用者关联到一个完整性级别，让SRM能够得到调用者自身属性的更详细信息。它给要访问的对象定义了一个完整性级别，从而指出了要访问该对象的调用者必须拥有的信任信息。” ——《深入解析windows操作系统 第六版（上册)》.P.487

以我的理解来讲，当一个用户登陆到windows操作系统中时，所属他的进程在访问不同的对象时，操作系统必须确认它有访问此对象的权限。通过赋予完整性级别这一属性，各对象能够被区分开，并能控制访问的行为。完整性级别是通过一个SID来指定的，系统使用了五个主要级别：

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012728f864eee5587c.png)

既然以SID的方式定义了完整性级别，那么它就应该存在于用户的令牌中。一个访问令牌的基本结构如下：

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013468e0bc79312bbe.png)

实际上，代表完整性级别的SID包含在组SID中。一个进程或线程拥有一个令牌，当它请求访问一个对象时，Windows内核中的SeAccessCheck函数会进行完整性检查。如果它的完整性级别等于或高于请求的对象，它就可以对此对象进行写入操作。但当一个进程或线程想要打开另一个进程或线程时，它不仅要满足完整性检查，还要拥有DACL的授权。

进程与对象的访问权

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dd4e70945ffd96b4.png)

<br>

**UAC**

UAC大家应该都很熟悉。简单来说，UAC的目的就是让用户以标准的权限，而非管理员权限来执行操作。它能够在一定程度上阻止恶意软件的运行。在我们的印象中，UAC似乎只是对本地使用计算机进行了限制，但事实上，微软也考虑了UAC对远程登陆的安全限制。在微软的知识库文章中，它认为应该保护本地管理员免受来自网络的攻击，因此对网络施加了UAC限制。同时，微软也提到了：

A user who has a domain user account logs on remotely to a Windows Vista computer. And, the domain user is a member of the Administrators group. In this case, the domain user will run with a full administrator access token on the remote computer, and UAC will not be in effect.

在我们的实验中，由于UAC的限制，我们无法以一个高完整性的令牌来登陆远程主机，因而pth攻击并不会成功；而在域环境中，我们以管理员组身份远程登陆时，将会得到一个高完整性的令牌，UAC对我们的行为并不加以限制。文章中也提到了解决问题的方法，通过设置LocalAccountTokenFilterPolicy的值为1来取消UAC的限制。这个键默认并不存在，需要在HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionPoliciesSystem下手动创建。顺便一提，UAC的设置就保存在HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionPoliciesSystem中。通常我们要更改UAC设置并不需要直接修改注册表，而是通过控制面板中的更改用户账户控制设置来更改。下图即为更改用户账户控制设置：

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019b4466456b83d0d4.png)

可以看到有四个等级：最高一档（始终通知）、第二档、第三档、最低一档（从不通知）。不同的等级将会影响到注册表中键的值：

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017c36c404c17b9fb4.png)

回到正题。我们来验证一下微软的方案：

在注册表中HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionPoliciesSystem下新建一个DWORDLocalAccountTokenFilterPolicy并将值设置为0

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0129f4f0057960fbe3.png)

**pass-the-hash**

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e30031d0f1f80fb2.png)

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01229bd32812d26e8a.png)

**将LocalAccountTokenFilterPolicy值设置为1，重复攻击过程**

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a50dbae107929502.png)

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a10f2f14632fd6a1.png)

[![](./img/85995/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e572f9caa62bf349.png)

没有问题，说明的确是由于令牌被UAC过滤掉导致无法远程登陆。这里我想再介绍两个概念：**受限制的令牌和已过滤的管理员令牌**。

<br>

**受限制的令牌**

受限制的令牌是通过windows的模仿机制创建的来源令牌的一份拷贝。至于什么是模仿这里暂且不表，感兴趣的同学可以自行google。受限令牌的特征就是能够作为复制品修改源令牌而不对源令牌造成影响。它的修改可以是如下：

**从该令牌的特权数组中删除一些特权**

**可以标记某些SID 为仅仅拒绝（deny-only）**

**可以将SID标记为受限制的（restricted） **

第二点和第三点实际上是对特权做出了限制，但这样的限制并不是直接将特权删除，因为删除特权可能会导致特权覆盖，简单来说就是此令牌不具有某些特权，但如果它的组SID被授予某些权限，那它也将具备这些权限。

<br>

**已过滤的管理员令牌**

UAC会使用受限制的令牌来创建已过滤的管理员令牌。一个已过滤的管理员令牌具有以下特性：

其完整性级别为“中”

管理员SID和管理员类的SID被标记为“仅仅拒绝”

除Change Notify、Shutdown、Undock、Increase Working Set和Time Zone外的特权都被移除

前面我们提到返回的令牌仅有一个“中等完整性”，是由于它是一个已过滤的管理员令牌。根据微软在Vista以后的默认策略，持有此令牌的用户将不得进行远程管理。

<br>

**总结**



经过以上的分析，我们可以大概明白为什么pass-the-hash在不同环境下有着迥异的行为。说的浅一点，就是UAC在作祟；深入探讨的话，则能通过pass-the-hash管窥Windows的庞大安全机制。 

受限于篇幅及主题的限制，我无法将文章中某些出现的概念进行深入地介绍，希望本文能够抛砖引玉，让大家对Windows操作系统进行深入地研究与思考，看待某些安全问题时能够有更新奇的理解。

<br>

**作者：Exist@Syclover（三叶草安全技术小组），新浪微博**[**@三叶草小组Syclover**](http://weibo.com/sycloversyc?is_hot=1)**,欢迎交流分享**

<br>

**参考文章**

[1] Mark Russionovich,David A.Solomon,Alex lonescu.《深入解析Windows操作系统 第6版 （上册）》[M] .第6版.潘爱民，范德成 

[2]Microsoft.《Description of User Account Control and remote restrictions in Windows Vista》.[https://support.microsoft.com/en-us/help/951016/description-of-user-account-control-and-remote-restrictions-in-windows-vista](https://support.microsoft.com/en-us/help/951016/description-of-user-account-control-and-remote-restrictions-in-windows-vista)    

[3]harmj0y.《Pass-the-Hash Is Dead》.[https://www.harmj0y.net/blog/redteaming/pass-the-hash-is-dead-long-live-localaccounttokenfilterpolicy/](https://www.harmj0y.net/blog/redteaming/pass-the-hash-is-dead-long-live-localaccounttokenfilterpolicy/)    

[4]Micrsoft. 《description-of-user-account-control-and-remote-restrictions-in-windows-vista》.[https://support.microsoft.com/en-us/help/951016/description-of-user-account-control-and-remote-restrictions-in-windows-vista](https://support.microsoft.com/en-us/help/951016/description-of-user-account-control-and-remote-restrictions-in-windows-vista) 
