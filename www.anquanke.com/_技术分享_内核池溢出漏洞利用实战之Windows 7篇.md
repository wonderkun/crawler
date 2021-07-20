> 原文链接: https://www.anquanke.com//post/id/86557 


# 【技术分享】内核池溢出漏洞利用实战之Windows 7篇


                                阅读量   
                                **115738**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://trackwatch.com/kernel-pool-overflow-exploitation-in-real-world-windows-7/](http://trackwatch.com/kernel-pool-overflow-exploitation-in-real-world-windows-7/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p2.ssl.qhimg.com/t01b83a31515a596aeb.jpg)](https://p2.ssl.qhimg.com/t01b83a31515a596aeb.jpg)**

译者：[an0nym0u5](http://bobao.360.cn/member/contribute?uid=578844650)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**一、前言**

****

本文重点围绕HitmanPro独立扫描版（版本**3.7.15-build 281**）的内核池溢出漏洞（**CVE-2017-6008**）展开。这个工具是反病毒软件Hitman.Alert解决方案的一部分，并以SophosClean可执行文件的方式集成在了英国公司Sophos的解决方案中。早在2017年2月，Sophos公司就收到了此漏洞的报告并在2017年5月发布3.7.20-Build 286版本更新了补丁。我们使用**Ioctfuzzer**（[https://github.com/Cr4sh/ioctlfuzzer](https://github.com/Cr4sh/ioctlfuzzer)）发现了首次crash。Ioctfuzzer是一款对输入输出请求包（以下简称IRP）进行模糊测试的强大易用的工具，我们利用此工具捕获到了API函数DeviceIoControlFile并利用该函数作为中间人代理。对于收到的每一个IRP包，它都会先行发送几个伪造的IRP包然后再转发原始IRP包。扫描伊始就出现了崩溃，崩溃发生在**BAD_POOL_HEADER**代码初始化阶段。阅读下文之前，我们强烈建议读者了解一些windows下的IOCTL和IRP知识。MSDN文档提供了大量可以帮助你更好地理解本文的信息。本文将要利用的是64位系统下的情景，这比32位系统下更难利用。

<br>

**二、详细分析**

****

**2.1 崩溃数据分析**

首先需要弄清楚**BAD_POOL_HEADER**错误码的含义，池是内核中动态分配的常见场所，此代码意味着处理池头部时出现了问题。池头是位于块开头的提供块有关信息的结构，如图1所示。

 [![](https://p0.ssl.qhimg.com/t010839953592fa180d.png)](https://p0.ssl.qhimg.com/t010839953592fa180d.png)

图1 池头结构图

池头很可能已经损坏才导致崩溃，为了验证此设想，我们利用调试器、转储工具还有测试器产生的日志快速找到了有缺陷的IRP包如下：

```
IOCTL Code: 0x0022e100
Outbuff: 0x03ffe1f4, Outsize: 0x00001050
Inbuff : 0x03ffd988, Insize: 0x00000200
//Device/Hitman Pro 37 [/??/C:/Windows/system32/drivers/hitmanpro37.sys]
```

这里有几点关键信息：

**C:/Windows/system32/drivers/hitmanpro37.sys**：处理IRP的驱动程序。由于池损坏导致了崩溃，因此该驱动一定与崩溃有关。

**IOCTL Code: 0x0022e100**：该IOCTL代码提供了大量信息，稍后会作分析。通过逆向还可以获知以上驱动是如何处理IRP的。

**Outsize / Insize**：用来在池中分配一些缓冲区，也可能与池损坏有关。

参考[MSDN文档](https://msdn.microsoft.com/en-us/library/windows/hardware/ff543023(v=vs.85).aspx)，从IOCTL代码中可以得到如下信息：

```
DeviceType = 0x22
Access = 0x3
Function = 0x840
Method = 0x0
Method 0x0=METHOD_BUFFERED
```

“对于METHOD_BUFFERED这种传输类型，IRP提供了一个指向位于Irp-&gt;AssociatedIrp.SystemBuffer的缓冲区的指针，该缓冲区代表调用DeviceIoControl和IoBuildDeviceIoControlRequest时的输入缓冲区和输出缓冲区，驱动器就在输入输出缓冲区之间传输数据。

对于输入数据，缓冲区大小由驱动器IO_STACK_LOCATION结构中的DeviceIoControl.InputBufferLength参数指定。

对于输出数据，缓冲区大小由驱动器IO_STACK_LOCATION结构中的DeviceIoControl.OutputputBufferLength参数指定。

系统为单个输入/输出缓冲区分配的空间大小是两个值中较大的那个。“

最后，为了弄清楚在正常情况下IOCTL是如何发送的，我们逆向了HitmanPro.exe可执行文件，利用IOCTL代码和逆向工具IDA快速定位到了问题函数。

 [![](https://p0.ssl.qhimg.com/t01de35bef34ba51b2d.png)](https://p0.ssl.qhimg.com/t01de35bef34ba51b2d.png)

可见，分配给DeviceIoControl的Outsize和Insize与崩溃数据吻合，这种情况下，IRP管理器分配的系统缓冲区大小在正常情况下至少为**0x1050**字节。

**2.2 逆向驱动器**

我们已经掌握了很多崩溃有关的信息，是时候逆向驱动器**hitmanpro37.sys**来看看IOCTL的句柄了。首先，参照IOCTL代码定位调度IRP的函数，通常它是包括一些switch跳转的庞大函数，还好该驱动器并不大我们很快找到了调度器：

 [![](https://p3.ssl.qhimg.com/t011b866e6a6089481c.png)](https://p3.ssl.qhimg.com/t011b866e6a6089481c.png)[![](https://p4.ssl.qhimg.com/t0176dbfc3d6646d30f.png)](https://p4.ssl.qhimg.com/t0176dbfc3d6646d30f.png)

 

跟踪跳转逻辑，我们找到了处理存在漏洞的IOCTL的函数，IRP提供的SystemBuffer首先被传给**IoGetDeviceObjectPointer**函数的ObjectName参数：

 [![](https://p2.ssl.qhimg.com/t0129fbdb7bfb2b6375.png)](https://p2.ssl.qhimg.com/t0129fbdb7bfb2b6375.png)

然后，

 [![](https://p5.ssl.qhimg.com/t0182ebe7eb201b4fb6.png)](https://p5.ssl.qhimg.com/t0182ebe7eb201b4fb6.png)

非常不错进行到这里了，还记得IOCTL用到的**METHOD_BUFFERED**方法吗？

“系统为单个输入/输出缓冲区分配的空间大小是两个值中较大的那个。”

这意味着我们完美控制了SystemBuffer的值，驱动器使用硬编码的值**0x1050**调用memset，如果SystemBuffer值小于**0x1050**，调用memset会使池损坏进而导致崩溃，这里我们称之为**内核池溢出漏洞**。虽然这么说，但是我们到目前为止还没有任何办法控制往此缓冲区写入。它被设置为0然后被DeviceObject中的地址和名字填充，这只有管理员权限才能控制得了，因此此漏洞只会导致操作系统崩溃，该漏洞编号是**CVE-2017-6007**。

**2.3 扭转**

到此我们并不甘心，又逆向了更多的处理程序，我们随机挑选了一个处理程序，这真的很有趣：

 [![](https://p5.ssl.qhimg.com/t0164bcb5fe36e82970.png)](https://p5.ssl.qhimg.com/t0164bcb5fe36e82970.png)

SystemBuffer（我们的输入）参数用在了一个子函数中，如果子函数返回正确的值，一些数据会通过mwmcpy拷贝到SystemBuffer中，此函数的控制码是**0x00222000**：

```
DeviceType = 0x22
Access = 0x0
Function = 0x0
Method = 0x0
```

还是利用了同样的方法：**METHOD_BUFFERED**。

如果我们足够幸运的话，这里可能会有类似的漏洞出现，然而，驱动器的这部分代码非同寻常：

**a**.我们没有在可执行程序HitmanPro中找到任何利用控制码**0x0022200**发送IRP的函数，因此在驱动器的这个位置下断点不会触发任何异常。

**b**.我们无法确定这个函数的确切功能，但我们找到了一个漏洞，这已经足够啦。

因此，逆向之旅又开始了。处理驱动后写成了如下伪代码：

 [![](https://p3.ssl.qhimg.com/t010a32a4be08bc21b0.png)](https://p3.ssl.qhimg.com/t010a32a4be08bc21b0.png)

[![](https://p0.ssl.qhimg.com/t0180fd5546bf25df6e.png)](https://p0.ssl.qhimg.com/t0180fd5546bf25df6e.png)

驱动器利用SystemBuffer提供的句柄获取到FILE_OBJECT，如果FILE_OBJECT空闲就会调用**ObQueryNameString**来获取FILE_OBJECT指向的文件名并存放在临时缓冲区，然后从临时缓冲区复制文件名到SystemBuffer。

驱动器通过如下参数调用**memcpy**：

**a. dest** = SystemBuffer ; 大小由我们控制

**b. src** = 我们提供的句柄文件名，写入和大小均可控

**c. n** = src缓冲区的大小；

唯一的限制就是**ObQueryNameString**函数，该函数是受保护的，如果源太大就不会复制任何内容到目标区域。

由于目标区域是硬编码0x400大小的缓冲区，我们就不能给出大于0x400的文件名，当然，0x400个字节对于利用缓冲区溢出已经足够了。

<br>

**三、利用**

****

**3.1 介绍**

既然是**内核池溢出漏洞**，我们就有很多攻击方式可以利用了。要想利用此漏洞，**Tarjei Mandt**的[文章](http://www.mista.nu/research/MANDT-kernelpool-PAPER.pdf)思路再好不过了，如果你想完全了解下一步发生了什么，它将是你必读的文章。这里我们采用的攻击方式是**配额进程指针覆盖**，我们选择它是因为这是最优雅的方式之一，32位和64位系统均能实现利用，在此攻击中，我们必须覆盖下一个块的进程指针。

 [![](https://p1.ssl.qhimg.com/t014c307cfd4ef6888b.png)](https://p1.ssl.qhimg.com/t014c307cfd4ef6888b.png)

该池头的最后4个字节有一个指向**EPROCESS**结构的指针，当有池块被释放时，如果**PoolType**设置了**Quota bit**，该指针会减小某些与EPROCESS对象有关的值：

**a**. 该对象的**引用计数**（一个进程是一个对象）

**b**.** QuotaBlock**字段指向的值

减值之前会有一些检查，我们不可以直接利用对象的ReferenceCount，不过可以伪造一个**EPROCESS**结构，并在QuotaBlock字段设置任意指针以减随机的值（内核空间也可以哦）。

```
kd&gt; dt nt!_EPROCESS
 +0x000 Pcb : _KPROCESS
 +0x098 ProcessLock : _EX_PUSH_LOCK
 +0x0a0 CreateTime : _LARGE_INTEGER
 +0x0a8 ExitTime : _LARGE_INTEGER
 +0x0b0 RundownProtect : _EX_RUNDOWN_REF
 +0x0b4 UniqueProcessId : Ptr32 Void
 +0x0b8 ActiveProcessLinks : _LIST_ENTRY
 +0x0c0 ProcessQuotaUsage : [2] Uint4B
 +0x0c8 ProcessQuotaPeak : [2] Uint4B
 +0x0d0 CommitCharge : Uint4B
 +0x0d4 QuotaBlock : Ptr32 _EPROCESS_QUOTA_BLOCK 
 [...]

typedef struct _EPROCESS_QUOTA_BLOCK `{`
   EPROCESS_QUOTA_ENTRY QuotaEntry[3];
   LIST_ENTRY QuotaList;
   ULONG ReferenceCount;
   ULONG ProcessCount;
 `}` EPROCESS_QUOTA_BLOCK, *PEPROCESS_QUOTA_BLOCK;
```

**3.2 溢出实现**

为了实现**配额进程指针溢出**攻击，我们需要利用我们的溢出覆盖两个东西：

a.下一个块的**池类型**，因为我们需要确定已经设置了**Quota bit**

b.下一块的**进程指针**，用一个指向伪造的**EPROCESS**结构的指针替换它

因为我们必须获取到下一块的进程指针，所以无论如何必须要覆盖下一块的整个池头，然而我们不能往池头发随机的数据否则会触发BSOD。

我们必须确定如下字段是正确的：

**a**.块大小

**b**.前一个块大小

**c**.池类型

满足此条件的唯一方式是准确获取要覆盖的块，这可以通过**池喷射技术**来实现。

这里不会详细阐述如何实现池喷射，但基本思路就是获取这种类型的池：

 [![](https://p1.ssl.qhimg.com/t01590170fb8df99bc7.png)](https://p1.ssl.qhimg.com/t01590170fb8df99bc7.png)

看起来类似这样：

 [![](https://p0.ssl.qhimg.com/t012fe92c01b2ffb6d0.png)](https://p0.ssl.qhimg.com/t012fe92c01b2ffb6d0.png)

我们的溢出效果：

溢出前：

 [![](https://p3.ssl.qhimg.com/t010a3ed3c4ec102b5c.png)](https://p3.ssl.qhimg.com/t010a3ed3c4ec102b5c.png)

溢出后：

 [![](https://p4.ssl.qhimg.com/t016369ec7f4bb54a7d.png)](https://p4.ssl.qhimg.com/t016369ec7f4bb54a7d.png)

**3.3 Payload**

好了，我们可以在任何地址实现减任何值了，下一步做什么呢？我们搜索到了一篇很好的Cesar Cerrudo[4]的文章，文中讲述了几种提权的技术。还有一点也很有趣，在TOKEN结构中有一个Privileges字段：

```
typedef struct _TOKEN 
 `{`
 [...]
 /*0x040*/ typedef struct _SEP_TOKEN_PRIVILEGES
           `{`
               UINT64 Present;
 /*0x048*/     UINT64 Enabled;
               UINT64 EnabledByDefault;
           `}` SEP_TOKEN_PRIVILEGES, *PSEP_TOKEN_PRIVILEGES;
 [...]
 `}`TOKEN, *PTOKEN;
```

该字段是包含位掩码的结构体，位掩码**Enabled**定义了进程可执行的操作。该位掩码默认值为0x80000000，具有SeChangeNotifyPrivilege权限，从该位掩码中去掉一位变成了0x7fffffff，就拥有了更大的权限，MSDN文档提供了该位掩码的可用的权限列表：

[https://msdn.microsoft.com/fr-fr/library/windows/desktop/bb530716(v=vs.85).aspx](https://msdn.microsoft.com/fr-fr/library/windows/desktop/bb530716(v=vs.85).aspx)

但是我们没有_TOKEN结构的地址，我们也不应该有因为那是内核地址。幸运的是，我们可以利用众所周知的**NtQuerySystemInformation**通过其句柄获取任何对象的内核地址。还可以通过调用OpenProcessToken()函数为我们的token赋予句柄，如果你想更深入了解**NtQuerySystemInformation()**函数和常见的内核地址溢出你应该参考[这里](https://recon.cx/2013/slides/Recon2013-Alex%20Ionescu-I%20got%2099%20problems%20but%20a%20kernel%20pointer%20ain't%20one.pdf)。

我们决定触发这个漏洞以获取SeDebugPrivilege权限，该权限可以实现控制系统所有进程，你可以获取任何你想要的权限。**SeDebugPrivilege**权限可以允许我们在系统进程中启动线程并反弹一个系统shell。

<br>

**四、结论**

****

注意，这个exploit不能在windows 8及更高版本系统中使用，毕竟微软在防御内核漏洞方面做了大量工作。实际上，虽然此exploit不能用在windows 8及更高系统版本上并不意味着这些版本不能被攻破，你可以在[github](https://github.com/cbayet/Exploit-CVE-2017-6008)上看到我的exploit源代码，windows 10系统下如何利用类似的漏洞这是**Nuit du Hack XV**大会的主题。

<br>

**五、参考文献**

****

[1] [https://github.com/Cr4sh/ioctlfuzzer](https://github.com/Cr4sh/ioctlfuzzer)– Simple ioctl fuzzer

[2][https://msdn.microsoft.com/en-us/library/windows/hardware/ff543023(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/hardware/ff543023(v=vs.85).aspx) – Defining IOCTL code

[3] [http://www.mista.nu/research/MANDT-kernelpool-PAPER.pdf](http://www.mista.nu/research/MANDT-kernelpool-PAPER.pdf)– Tarjei Mandt paper

[4][http://media.blackhat.com/bh-us-12/Briefings/Cerrudo/BH_US_12_Cerrudo_Windows_Kernel_WP.pdf](http://media.blackhat.com/bh-us-12/Briefings/Cerrudo/BH_US_12_Cerrudo_Windows_Kernel_WP.pdf) – Easy local Windows Kernel exploitation by Cesar Cerrudo.

[5][https://recon.cx/2013/slides/Recon2013-Alex%20Ionescu-I%20got%2099%20problems%20but%20a%20kernel%20pointer%20ain't%20one.pdf](https://recon.cx/2013/slides/Recon2013-Alex%20Ionescu-I%20got%2099%20problems%20but%20a%20kernel%20pointer%20ain%E2%80%99t%20one.pdf)— Leaking Kernel Addresses

[6] [https://github.com/fishstiqz/poolinfo](https://github.com/fishstiqz/poolinfo)– This extension is great for investigating the pool state

[7] [https://github.com/cbayet/Exploit-CVE-2017-6008](https://github.com/cbayet/Exploit-CVE-2017-6008)– Source code of the exploit
