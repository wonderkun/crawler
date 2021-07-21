> 原文链接: https://www.anquanke.com//post/id/235716 


# 猫鼠游戏：Windows内核提权样本狩猎思路分享


                                阅读量   
                                **240060**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t017b8ecc0910cc177f.jpg)](https://p3.ssl.qhimg.com/t017b8ecc0910cc177f.jpg)



## 0x01 背景

随着Windows平台的几大主流浏览器(Chrome, Edge, IE)和文字处理软件(Office, Adobe Reader)相继引入沙箱机制，Windows内核提权漏洞的需求也随之上升。在这个背景下，近几年披露的Windows内核提权0day攻击事件也居于高位。下表展示了2017年-2021年(至今)全球范围内披露的Windows内核提权在野0day编号及对应的披露厂商，从表中可以直观地感受到上述现象。
<td class="ql-align-center" data-row="1">统计</td><td class="ql-align-center" data-row="1">披露年份</td><td class="ql-align-center" data-row="1">CVE编号</td><td class="ql-align-center" data-row="1">漏洞模块</td><td class="ql-align-center" data-row="1">披露厂商</td>
<td class="ql-align-center" data-row="2">2</td><td class="ql-align-center" data-row="2">2017</td><td class="ql-align-center" data-row="2">CVE-2017-0005</td><td class="ql-align-center" data-row="2">win32k</td><td class="ql-align-center" data-row="2">Lockheed Martin</td>
<td class="ql-align-center" data-row="3">2017</td><td class="ql-align-center" data-row="3">CVE-2017-0263</td><td class="ql-align-center" data-row="3">win32k</td><td class="ql-align-center" data-row="3">FireEye, ESET</td>
<td class="ql-align-center" data-row="4">4</td><td class="ql-align-center" data-row="4">2018</td><td class="ql-align-center" data-row="4">CVE-2018-8120</td><td class="ql-align-center" data-row="4">win32k</td><td class="ql-align-center" data-row="4">ESET</td>
<td class="ql-align-center" data-row="5">2018</td><td class="ql-align-center" data-row="5">CVE-2018-8453</td><td class="ql-align-center" data-row="5">win32k</td><td class="ql-align-center" data-row="5">Kaspersky</td>
<td class="ql-align-center" data-row="6">2018</td><td class="ql-align-center" data-row="6">CVE-2018-8589</td><td class="ql-align-center" data-row="6">win32k</td><td class="ql-align-center" data-row="6">Kaspersky</td>
<td class="ql-align-center" data-row="7">2018</td><td class="ql-align-center" data-row="7">CVE-2018-8611</td><td class="ql-align-center" data-row="7">nt/tm</td><td class="ql-align-center" data-row="7">Kaspersky</td>
<td class="ql-align-center" data-row="8">6</td><td class="ql-align-center" data-row="8">2019</td><td class="ql-align-center" data-row="8">CVE-2019-0797</td><td class="ql-align-center" data-row="8">win32k</td><td class="ql-align-center" data-row="8">Kaspersky</td>
<td class="ql-align-center" data-row="9">2019</td><td class="ql-align-center" data-row="9">CVE-2019-0803</td><td class="ql-align-center" data-row="9">win32k</td><td class="ql-align-center" data-row="9">Alibaba</td>
<td class="ql-align-center" data-row="10">2019</td><td class="ql-align-center" data-row="10">CVE-2019-0808</td><td class="ql-align-center" data-row="10">win32k</td><td class="ql-align-center" data-row="10">Google</td>
<td class="ql-align-center" data-row="11">2019</td><td class="ql-align-center" data-row="11">CVE-2019-0859</td><td class="ql-align-center" data-row="11">win32k</td><td class="ql-align-center" data-row="11">Kaspersky</td>
<td class="ql-align-center" data-row="12">2019</td><td class="ql-align-center" data-row="12">CVE-2019-1132</td><td class="ql-align-center" data-row="12">win32k</td><td class="ql-align-center" data-row="12">ESET</td>
<td class="ql-align-center" data-row="13">2019</td><td class="ql-align-center" data-row="13">CVE-2019-1458</td><td class="ql-align-center" data-row="13">win32k</td><td class="ql-align-center" data-row="13">Kaspersky</td>
<td class="ql-align-center" data-row="14">3</td><td class="ql-align-center" data-row="14">2020</td><td class="ql-align-center" data-row="14">CVE-2020-0938</td><td class="ql-align-center" data-row="14">atmfd</td><td class="ql-align-center" data-row="14">Google</td>
<td class="ql-align-center" data-row="15">2020</td><td class="ql-align-center" data-row="15">CVE-2020-1027</td><td class="ql-align-center" data-row="15">sxssrv</td><td class="ql-align-center" data-row="15">Google</td>
<td class="ql-align-center" data-row="16">2020</td><td class="ql-align-center" data-row="16">CVE-2020-17087</td><td class="ql-align-center" data-row="16">cng</td><td class="ql-align-center" data-row="16">Google</td>
<td class="ql-align-center" data-row="17">1(截止3月)</td><td class="ql-align-center" data-row="17">2021</td><td class="ql-align-center" data-row="17">CVE-2021-1732</td><td class="ql-align-center" data-row="17">win32k</td><td class="ql-align-center" data-row="17">DBAPPSecurity(安恒信息)</td>

这些Windows内核提权零日漏洞成本高昂，因此其背后一般都是水平高超或实力雄厚的APT组织。对威胁情报部门来说，如何有效狩猎这些在野的Windows内核提权漏洞样本已经变为一个需要深入思考的问题。

关于这个问题，Kaspersky作为Windows内核提权0day狩猎方面的先行者，已经公开分享过一些他们在这方面的经验；CheckPoint在最近半年也分享了3篇关于内核提权样本狩猎的研究文章，非常值得学习(对这些资料的引用将会列举在本文的最后，供读者参考)。

本文将分享安恒威胁情报中心猎影实验室在这方面的一些思考，讨论侧重点为内存破坏类内核提权漏洞，这一块我们尚处在摸索阶段，不足之处敬请斧正。



## 0x02 内存破坏类内核提权漏洞

内存破坏类内核提权漏洞一般由C/C++语言的不安全操作引发，最为常见的是win32k组件中由于Callback机制导致的UAF漏洞。

### **为什么win32k组件容易出问题？**

为什么win32k组件中的UAF漏洞这么多？这要从Windows NT的设计历史说起。在Windows操作系统设计初期，win32k子系统是在用户态的(实线的上半部分)，如下：

[![](https://p5.ssl.qhimg.com/t0157951474fb84be47.png)](https://p5.ssl.qhimg.com/t0157951474fb84be47.png)

但从Windows NT4开始，这部分代码被移到了内核态(实线的下半部分)，内核态新增了一个win32k.sys模块：

[![](https://p2.ssl.qhimg.com/t01f28dc62d25cb9bbb.png)](https://p2.ssl.qhimg.com/t01f28dc62d25cb9bbb.png)

上述重新设计引入了如下3个不安全因素：
1. 新的系统调用 (1100+ syscalls)
1. 用户模式回调 (User-mode Callback)
1. 用户态和内核态之间的共享数据 (Shared data)
重新设计后，上述3点都可能引发新的安全漏洞，Windows内核团队也意识到了这几点，所以针对性地进行了加固，但安全研究人员还是不断从中找出安全漏洞。

在2011年Blackhat USA大会上，Tarjei Mandt公开了他对Win32k User-Mode Callback机制的研究成果，从此大量研究人员开始关注win32k模块中的User-Mode Callback攻击面，并发现了许多新的win32k模块UAF漏洞。



## 0x03 如何狩猎内核提权利用样本

有过漏洞研究基础的同学都知道，一个典型的漏洞利用过程大概有这几个环节：
1. 触发漏洞
1. 堆喷射(非必需)
1. 信息泄露
1. 构造读写原语
1. 代码执行
我们可以从上述每一个阶段入手，分别思考一下每一阶段潜在的一些狩猎点。

### **触发漏洞阶段**

静态层面，首先，我们可以检查PE文件的导入表中是否导入了user32.dll中的下面几个函数，因为大部分win32k漏洞利用都需要创建窗口或菜单：
1. CreateWindowExA / CreateWindowExW
1. RegisterClassExA / RegisterClassExW
1. DestroyWindow
1. CreateMenu
1. CreatePopupMenu
其次，Win32k User-Mode Callback漏洞一定存在Hook回调表的操作，这是一个可疑行为(64位样本会存在和下面很像的一个代码片段)：

mov rax, gs:[60h]

lea rax, [rax+58h]

mov rax, [rax]

ret

动态层面，对于UAF漏洞和部分越界读写漏洞，可以通过开启Driver Virifier进行检测，UAF漏洞样本在开启Driver Virifier的环境中会触发蓝屏异常，判定0day最简单的标准就是：
1. 全补丁环境蓝屏 = 0day
当然，有一些内存破坏类内核提权漏洞无法通过Driver Virifier检测到，一个典型例子就是我们捕获的CVE-2021-1732。

### **堆喷射阶段(非必须)**

堆喷射阶段变化比较多，可以创建多个Windows或多个Bitmaps，例如CVE-2018-8453的在野利用；也可以创建多个加速表(CreateAcceleratorTable)，例如CVE-2017-8465的开源利用代码；也可以创建多个tagCLS结构，比如《LPE vulnerabilities exploitation on Windows 10 Anniversary Update》这个PPT第36页提出的方法。

### **信息泄露阶段**

关于Windows内核信息泄露技巧，Github上有一个项目(项目地址列举在文末)总结得较为完整。项目中有一张表格，该表格详细列出了Windows内核信息泄露的各种技巧，并且通过不同的图标展示了这些技巧在各版本Windows操作系统中的可用性。

[![](https://p5.ssl.qhimg.com/t01a401d424e3fd9601.png)](https://p5.ssl.qhimg.com/t01a401d424e3fd9601.png)

这张表格只将操作系统写到Windows 1703(Redstone 2)，但仅根据表格内信息我们也可发现：只有HMValidateHandle这一技巧一直稳定存在(从1803开始也进行了缓解)。

静态层面，我们可以通过查找HMValidateHandle的代码特征来发现内核信息泄露的线索。以下是一段查找HMValidateHandle的典型代码，如果在静态分析时遇到类似代码片段，就应值得留意：

```
PVOID find_HMValidateHandle(PVOID pIsMenu)

`{`

ULONG HMValidateHandleAddr = 0;

while (TRUE)

`{`

if (*(BYTE*)pIsMenu == 0xE8)

`{`

HMValidateHandleAddr = *(DWORD*)((ULONG)pIsMenu + 1);

HMValidateHandleAddr += (ULONG)pIsMenu + 0x05 - 0x100000000;

return (PVOID)HMValidateHandleAddr;

`}`

pIsMenu = (BYTE*)pIsMenu + 1;

`}`

return 0;

`}`
```

动态分析层面，由于HMValidateHandle是一个未导出函数，系统在正常调用这个函数时，对其调用的地址来自user32.dll内部；但当这个函数被用于信息泄露时，对其调用的地址位于漏洞利用模块，这个地址并不位于user32.dll模块。我们可以借助这一原理进行运行时检测：将来自user32.dll外的对HMValidateHandle的调用标记为可疑行为并记录。这方面已经有国外的研究员做了样例，一并列举在文末。

### **构造读写原语阶段**

在Windows内核利用的历史中，相继有操作tagWND，Bitmap，Palette，Menu等相关结构体的API登场，发展到现在，已经公开且还没有被完全缓解的任意地址读写原语辅助函数已经只剩SetWindowLong*系列函数和Menu相关函数，所以查看导入表中是否有user32.dll中的下面几个函数是一种思路：
1. SetWindowLongA / SetWindowLongW
1. SetWindowLongPtrA / SetWindowLongPtrW
1. GetMenuItemRect / SetMenuItemInfo
1. GetMenuBarInfo (CVE-2021-1732在野利用中首次发现)
除了上述API，早期版本的一些利用代码还可以包括下面这些导入函数：
1. GetBitmapBits / SetBitmapBits / CreateCompatibleBitmap / CreateBitmapIndirect / CreateDiscardableBitmap / CreateDIBitmap
1. GetPaletteEntries / SetPaletteEntries
1. SetWindowTextA / SetWindowTextW / InternalGetWindowText
1. NtUserDefSetText
### **代码执行阶段**

对于Windows内核提权漏洞而言，其主要目的是为了提升权限，而提升权限的主要手法就是进行Token替换，因此可以通过以下几个特征点进行检查：
1. 在实现任意地址读写原语后，是否有借助泄露的内核地址进行结构查找的操作，例如遍历EPROCESS链
1. 在合适的时间点(如当前进程退出前)检查当前的进程的Token是否已被替换为其他高权限进程(例如System进程)的Token，或者查看当前进程创建的子进程的Token是否为System权限


## 0x04 Windows内核漏洞利用攻防史

Windows内核团队和漏洞缓解团队一直致力于减少Windows内核的漏洞&amp;利用攻击面，简单了解Windows系统中的内核安全攻防时间线有助于我们对Windows内核利用历史的了解和对Windows内核利用趋势的预测，这些对狩猎都有帮助。

### **Windows 7**
1. KASLR
1. 需要额外的内核信息泄露来绕过KASLR
1. 绕过方式：https[:]//github.com/sam-b/windows_kernel_address_leaks
### **Windows 8.1**
1. SMEP (Supervisor Mode Execution Prevention)
1. 需要处理器支持(2011年引入)， CR4寄存器的第20位作为开关
1. 当CPU处于Ring0模式时，如果执行了Ring3的代码，就会触发页错误
1. **绕过方式：CVE-2015-2360 Duqu 2.0在野利用样本**
1. 禁止使用0地址页
1. 之前的内核空指针引用漏洞利用方式：申请0地址，借助0地址进行任意地址读写
1. 之后的内核空指针引用漏洞利用：0地址页无法申请，无法完成利用，例如CVE-2018-8120不能在Windows 8及以上版本进行利用
### **Windows 10 1607 (Redstone 1)**
1. 提升Bypass KASLR的难度
1. 将GDI_CELL结构的pKernelAddress成员置为空，通过GdiSharedHandleTable进行内核信息泄露的方式被缓解
1. 缓解通过SetWindowText操纵tagWND.strName进行任意内核地址读写的利用方式
1. 限制tagWND.strName指针只能指向桌面堆 (缓解CVE-2015-2360和CVE-2016-7255这两个漏洞的在野利用方式)
1. 将字体解析模块拆为独立组件，并将其权限限制为AppContainer
1. 缓解win32k字体解析类提权漏洞，限制这类漏洞利用过程中的文件读写(缓解CVE-2016-7256和CVE-2020-0938这些字体漏洞的在Windows 10上的利用)
### **Windows 10 1703 (Redstone 2)**
1. 提升Bypass KASLR的难度
1. 缓解通过gSharedInfo进行pvScan0内核指针信息泄露的方式
1. 缓解通过桌面堆进行内核信息泄露的方式：Win32ClientInfo结构体内的ulClientDelta指针被移除，无法再通过ulClientDelta进行内核信息泄露
1. 缓解借助tagWND构造任意地址读写原语的方式
1. SetWindowLongPtr操作的ExtraBytes内存指针被移到用户态，无法再借助它对tagWND.strName进行修改
1. 缓解借助Bitmap进行利用的方式
1. Bitmap对象头部大小增加了8字节
### **Windows 10 1709 (Redstone 3)**
1. Win32k Type Isolation for Bitmap：将Bitmap header与Bitmap data分开
1. 进一步缓解借助Bitmap对象构造任意地址读写原语的方式
1. 绕过方式：借助Palette对象构造任意地址读写原语，参考《Demystifying Windows Kernel Exploitation by Abusing GDI Objects》
### **Windows 10 1803 (Redstone 4)**
1. Win32k Type Isolation for Palette
1. 缓解借助Palette对象构造任意地址读写原语的方式
<li data-list="bullet">
**绕过Type Isolation缓解措施的提权样本：CVE-2018-8453在野利用样本，**具体细节参考《Overview of the latest Windows OS kernel exploits found in the wild》</li>
1. 缓解通过HMValidateHandle进行内核信息泄露的方式
1. 通过HMValidateHandle泄露的内核tagWND副本中，相关指针值不复存在
### **Windows 10 1809 (Redstone 5)**
1. 继续提升Bypass KASLR的难度
1. 创建多个桌面堆，对相关API进行大幅修改
1. 绕过方式：用一种新的方式泄漏并计算包含内核模式指针的对象的绝对地址，可参考《DEVELOPMENT OF A NEW WINDOWS 10 KASLR BYPASS (IN ONE WINDBG COMMAND)》这篇文章
### **Windows 10 1903**
1. 进一步缓解内核漏洞利用的攻击面
<li class="ql-indent-1" data-list="bullet">
**绕过方式：CVE-2021-1732在野利用样本，**借助spmenu进行内核信息泄露，借助GetMenuBarInfo/SetWindowLong函数实现任意地址读写，可在最新版Windows 20H2系统上完成利用</li>


## 0x05 主流浏览器与win32k漏洞的攻防史

### **Chrome/Edge(Chromium-based)**
1. Win32k Lockdown
1. Chrome于2016年首先引入，在Chrome+Windows 8.1及以上环境中禁止调用win32k模块的API
1. 绕过方式：采用win32k模块以外的内核漏洞，例如CVE-2018-8611和CVE-2020-17087这类在野利用样本
### **Edge(Chakra)**
1. Win32k System Call Filter
1. Windows 8.1开始支持
1. 限制对部分win32k API进行调用：在RS3中Edge可以调用349个win32k API；而在RS4中，Edge能调用的win32k API数量减少为78个，所有GDI对象都无法在Edge中创建
1. 绕过方式：使用那些没有被过滤的win32k API的漏洞，例如DirectX漏洞，可以参考《Subverting Direct X Kernel For Gaining Remote System》


## 0x06 Windows内核提权漏洞趋势预测
1. Windows 10上的内核漏洞挖掘难度也许变化不大，但利用难度已经变得非常大
1. 主流浏览器/文档处理软件相继引入Sandbox机制，APT组织对沙箱逃逸/提权漏洞的需求会越来越大
1. 传统的win32k组件内核提权漏洞逐渐被主流浏览器拒之门外
1. 非win32k模块内核提权漏洞的需求在APT市场上会继续增加，但成本会越来越高，类似CVE-2018-8611这种高度复杂漏洞利用接下来还会出现
1. 逻辑类提权漏洞的数量会稍有增加(作为内存破坏类漏洞的替代品)
1. 浏览器自身组件的沙箱逃逸漏洞数量也会增加，这类漏洞是浏览器自己的漏洞，但也可以实现沙箱逃，可以从Low提权到Medium，比如Chrome Mojo组件的沙箱逃逸漏洞和Windows打印机提权漏洞
更多内容请前往微信公众号：**安恒威胁情报中心**

**安恒威胁情报中心介绍**

安恒威胁情报中心汇聚了海量威胁情报，支持多点渠道数据输入，支持自动情报数据产出，能实现网络安全的高效赋能。平台使用者可通过自定义策略进行威胁监控、威胁狩猎，并对输入数据进行自动化的生产加工，同时支持人工分析团队对情报进行复核整理。
