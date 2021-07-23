> 原文链接: https://www.anquanke.com//post/id/209744 


# 直播视频公布 | 窥探有方——调试Released SGX Enclave


                                阅读量   
                                **395612**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01139c2c61db7d57f9.jpg)](https://p0.ssl.qhimg.com/t01139c2c61db7d57f9.jpg)



## 直播主题

Intel SGX窥探之旅



## 内容简介

SGX是Intel基于CPU扩展的一种革命性的安全技术，旨在提供具有最小攻击面的硬件辅助的可信执行环境。实际应用时主要用来保护使用中的数据的机密性和完整性。本议题主要是探索SGX的工作原理和安全优势，同时分享我们发现的一个SGX安全漏洞一一可将Released Enclave转换成debug模式以窥视其内部数据。<br style="box-sizing: border-box;">除此之外，本议题也会探索SGX在数据安全领域的一些应用。



## 讲师简介

苏小智

360安全工程院冰刃实验室，安全开发专家。主要研究方向为Linux内核、主动防御、虚拟化及其安全、loT、SGX, 设计并研发了多款终端硬件产品，终端安全和云安全软件产品。

直播视频：

<video style="width: 100%; height: auto;" src="https://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/5a6J5YWo5aSn6K6y5aCC56ys5LiJ5pyfLUludGVsIFNHWCDnqqXmjqLkuYvml4UubXA0" controls="controls" width="300" height="150">﻿您的浏览器不支持video标签 </video>



作者：Suezi@[360安全工程院冰刃实验室](https://www.iceswordlab.com)

Intel Software Guard Extensions (Intel SGX)是基于CPU扩展的一种革命性的安全技术,旨在提供具有最小攻击面的硬件辅助的可信执行环境。它允许应用程序或应用程序的一部分运行在一个称为Enclave的安全容器中，任何应用程序，包括OS、Hypervisor、BIOS均无法访问其内容。Enclave使用的页面和数据结构由CPU内部的MEE加密存储在EPC中，负责映射Enclave页面的页表由OS管理，但OS无法获取其内容，仅Enclave可访问。然而攻击者总是想方设法以直接或间接的方式来获取数据，比如隐私数据，加密密钥，或者篡改代码的执行流。分析SGX的工作模型，设法将Release版本的Enclave转换成Debug版本，再借助SGX开发套件中的sgx-gdb工具，可实现对SGX Enclave的动态调试，之后便可为所欲为。



## 1 引言

当程序运行在某个计算平台，特别是在公有云时，其依赖的运行环境可能存在着安全漏洞甚至系统已被攻破，代码和数据的安全性均无法得到保障。此时建立一个可信计算环境（TEE）是十分必要的安全手段和需求，如ARM平台的Trust Zone，Intel的SGX。SGX自Intel的第5代Xeon E3系列CPU开始可用，Intel在CPU内部提供一个具备最小攻击面的的执行环境——SGX，不管是应用程序还是具备root权限的操作系统还是VMM或者BIOS，都无法直接读取或修改Enclave的内容。

与普通的应用程序开发流程类似，Enclave程序在开发过程分为Debug version、PreRelease version、Release Version，不同的版本在构建时使用的密钥类型不一样，Debug版本可采用自生成的密钥，Release版本必须采用Intel签发的，其中Debug版本支持 sgx-gdb调试。sgx-gdb基于普通gdb添加针对SGX的ptrace，除了不支持少数的gdb指令（info sharedlibrary、charset、gcore）和受限支持next/step、call/print 外，使用和功能上与普通gdb无异。

本文以SGX的工作模型为切入点，主要研究如何将Release模式的Enclave转换成Debug，之后借助sgx-gdb工具完成对正常Enclave的窥探。本文提出并实现静态转换和动态转换的两种Released Enclave to Debug的方法。



## 2 SGX概述

根本上，SGX是Intel指令集架构（ISA）的扩展，设计了一套专用的指令集用于创建一个可信执行环境Enclave，可被应用程序用来保存/运行数据或代码。SGX利用CPU提供的指令在内存中划分一部分区域供Enclave使用，这部分内存称为EPC（Enclave Page Cache）,并且限定每个EPC页面只能分配给一个Enclave，Enclave使用的页面和数据结构由CPU内部的MEE(Memory Encryption Engine)加密存储在EPC中。EPC的访问控制由跟CPU体系相关的硬件EPCM（Enclave Page Cache Map）负责，任何Non-Enclave都不能访问EPC的内容，任何软件均不可访问EPCM。SGX扩展出一个新的CPU模式，叫做Enclave模式，当CPU要访问Enclave中的数据时，需要切换到Enclave模式。Enclave和Non-Enclave通过EENTER和EEXIT指令进行切换，当Enclave运行过程被中断或异常打断时，Enclave通过AEX（Asynchronous Enclave Exit）机制退出到Non-Enclave模式。在模式切换时，其运行状态会保存到SSA（State Save Area）中，并清除TLB。

相比其他TEE，SGX的TCB（Trust Computing Base）更小，仅局限于Enclave 软件本身和CPU及其固件。从攻击面上对比，普通应用程序和SGX应用程序分别如图1和图2<sup>[1]</sup>所示。

[![](https://p5.ssl.qhimg.com/t01eedbd3dcc67077b2.png)](https://p5.ssl.qhimg.com/t01eedbd3dcc67077b2.png)

图1 普通应用程序攻击面

[![](https://p5.ssl.qhimg.com/t013491a09e29e10a7d.png)](https://p5.ssl.qhimg.com/t013491a09e29e10a7d.png)

图2 SGX应用程序的攻击面



## 3 SGX 详述

### **3.1 SGX****术语**

**Enclave**：不同的语境下有不同的含义，可以指SGX可信执行环境，也可以指应用程序里将要在可信执行环境里运行的那部分代码。

**EPC**：Enclave Page Cache，一个加密的内存区域。实现上可以通过BIOS预留计算机中DRAM的一部分做专用内存，再利用CPU的MEE对专用内存进行高效加解密。可有效防止内存嗅探攻击。

**MEE**：Memory Encryption Engine， CPU中的加密引擎。

**EPCM**: Enclave Page Cache Map，为了对每个EPC页进行访问控制，在CPU特定的数据结构中维持EPC entry的有效性和Enclave的访问权限（R/W/X）以及EPC页的类型（PT_SECS/PT_TCS/PT_REG/PT_VA/PT_TRIM）。

**SSA**：State Save Area, 当Enclave切换到Non-Enclave模式时，如Enclave运行中遇到CPU中断，会发生上下文切换，保存Enclave的上下文到EPC中保留区域，这部分区域叫做状态保留区域，在resume时再恢复。

**SECS**：SGX Enclave Control Structure，每个Enclave都对应着一个SECS，它是用于表示Enclave属性的数据结构，存储在EPC内存页，包含了Enclave所需的元数据信息，如存储Enclave构建时的度量值MRENCLAVE，是硬件保护Enclave的关键要素。文中探究的Enclave Debug属性也是包含在该数据结构中的ATTRIBUTES域里。整个数据结构不可被Non-Enclave 软件访问。

**TCS**：Thread Control Structure，每个运行着的Enclave拥有一个或者多个TCS。TCS是硬件进入/退出Enclave时用来存储/恢复线程相关信息的数据结构，保存在EPC内存页。TCS的FLAGS域可被Non-Enclave软件访问,TCS.FLAGS.DBGOPTIN 用于使能Enclave的debug属性(如TF, breakpoints)，Debug模式的Enclave可通过调试器修改该位。

**MRSIGNER**：对Enclave签名密钥对中公钥的SHA-256 值。

**SIGSTRUCT**：Enclave Signature Structure,用于表示Enclave签名相关信息的数据结构。同时也保存着含有Debug 属性的Enclave ATTRIBUTES 域。

**EINITTOKEN**：EINT Token Structure，Enclave EINIT 时用来检验是否允许该Enclave初始化的令牌。也称为Launch token。令牌数据结构中同时也保存着含有Debug 属性的Enclave ATTRIBUTES 域。

**MRENCLAVE**：Enclave的唯一识别码，用于记录Enclave从创建到初始化完成整个过程的256 bit的摘要，代表着Enclave本身的TCB。在ECREATE时初始化，EADD/EEXTEND时更新，EINIT后锁定。

**AEX**：Asynchronous Enclave Exits，Enclave运行时遇到CPU中断等异常事件，退出执行。

### **3.2 SGX ****指令**

SGX指令包括特权指令（ENCLS）和用户指令（ENCLU）两大部分，通过在EAX寄存器指定输入值来和ENCLS/ENCLC编码形成不同功能的子函数（指令），其输入/输出参数通过RBX/RCX/RDX寄存器进行指定。ENCLS相关的指令助记符如表1所示。ENCLU相关的指令助记符如表2所示。

表1 ENCLS 指令
<td style="width: 59.8pt;" valign="top">ECREATE</td><td style="width: 56.0pt;" valign="top">00H(In)</td><td style="width: 80.8pt;" valign="top">PAGEINFO(In, EA)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">在EPC中创建一个SECS页</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">EADD</td><td style="width: 56.0pt;" valign="top">01H(In)</td><td style="width: 80.8pt;" valign="top">PAGEINFO(In, EA)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">增加一个新页到未初始化完成的Enclave</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">EINIT</td><td style="width: 56.0pt;" valign="top">02H(In)</td><td style="width: 80.8pt;" valign="top">SIGSTRUCT(In, EA)</td><td style="width: 73.8pt;" valign="top">SECS(In, EA)</td><td style="width: 83.75pt;" valign="top">EINITTOKEN(In, EA)</td><td style="width: 70.85pt;" valign="top">初始化一个可执行Enclave</td>

(In, EA)

(In, EA)
<td style="width: 59.8pt;" valign="top">EREMOVE</td><td style="width: 56.0pt;" valign="top">03H(In)</td><td style="width: 80.8pt;" valign="top"></td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">从EPC删除一页</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">EDBGRD</td><td style="width: 56.0pt;" valign="top">04H(In)</td><td style="width: 80.8pt;" valign="top">ResultData(Out)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">从Debug Enclave 读取数据</td>

(Out)
<td style="width: 59.8pt;" valign="top">EDBGWR</td><td style="width: 56.0pt;" valign="top">05H(In)</td><td style="width: 80.8pt;" valign="top">SourceData(In)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">向Debug Enclave写入数据</td>

(In)
<td style="width: 59.8pt;" valign="top">EEXTEND</td><td style="width: 56.0pt;" valign="top">06H(In)</td><td style="width: 80.8pt;" valign="top"></td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">扩展未初始化完成的Enclave的度量值</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">ELDB</td><td style="width: 56.0pt;" valign="top">07H(In)</td><td style="width: 80.8pt;" valign="top">PAGEINFO(In, EA)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top">VERSION(In, EA)</td><td style="width: 70.85pt;" valign="top">加载一个EPC页并将其状态标记为blocked</td>

(In, EA)

(In, EA)
<td style="width: 59.8pt;" valign="top">ELDU</td><td style="width: 56.0pt;" valign="top">08H(In)</td><td style="width: 80.8pt;" valign="top">PAGEINFO(In, EA)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top">VERSION(In, EA)</td><td style="width: 70.85pt;" valign="top">加载一个EPC页并将其状态标记为unblocked</td>

(In, EA)

(In, EA)
<td style="width: 59.8pt;" valign="top">EBLOCK</td><td style="width: 56.0pt;" valign="top">09H(In)</td><td style="width: 80.8pt;" valign="top"></td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">将一个EPC页标记为blocked</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">EPA</td><td style="width: 56.0pt;" valign="top">0AH(In)</td><td style="width: 80.8pt;" valign="top">PT_VA(In)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">在EPC中增加Version Array</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">EWB</td><td style="width: 56.0pt;" valign="top">0BH(In)</td><td style="width: 80.8pt;" valign="top">PAGEINFO(In, EA)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top">VERSION(In, EA)</td><td style="width: 70.85pt;" valign="top">使一个EPC页面无效并写回到主内存（DRAM）</td>

(In, EA)

(In, EA)
<td style="width: 59.8pt;" valign="top">ETRACK</td><td style="width: 56.0pt;" valign="top">0CH(In)</td><td style="width: 80.8pt;" valign="top"></td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">激活EBLOCK的检查</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">EAUG</td><td style="width: 56.0pt;" valign="top">0DH(In)</td><td style="width: 80.8pt;" valign="top">PAGEINFO(In, EA)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top">LINADDR</td><td style="width: 70.85pt;" valign="top">为已初始化的Enclave增加一个EPC页</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">EMODPR</td><td style="width: 56.0pt;" valign="top">0EH(In)</td><td style="width: 80.8pt;" valign="top">SECINFO(In, EA)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">为已初始化的Enclave修改EPC页的访问权限</td>

(In, EA)
<td style="width: 59.8pt;" valign="top">EMODT</td><td style="width: 56.0pt;" valign="top">0FH(In)</td><td style="width: 80.8pt;" valign="top">SECINFO(In, EA)</td><td style="width: 73.8pt;" valign="top">EPCPAGE(In, EA)</td><td style="width: 83.75pt;" valign="top"></td><td style="width: 70.85pt;" valign="top">改变EPC页的类型</td>

(In, EA)
<td style="width: 425.0pt;" colspan="6" valign="top">EA:Effective AddressIn:Input parameterOut:Output parameter</td>

Out:Output parameter

表2 ENCLU指令
<td style="width: 86.25pt;" valign="top">指令</td><td style="width: 76.55pt;" valign="top">EAX</td><td style="width: 68.55pt;" valign="top">RBX</td><td style="width: 79.45pt;" valign="top">RCX</td><td style="width: 79.45pt;" valign="top">RDX</td><td style="width: 24.55pt;" valign="top">功能简介</td>
<td style="width: 86.25pt;" valign="top">EREPORT</td><td style="width: 76.55pt;" valign="top">00H(In)</td><td style="width: 68.55pt;" valign="top">TARGETINOF(In,EA)</td><td style="width: 79.45pt;" valign="top">REPORTDATA(In,EA)</td><td style="width: 79.45pt;" valign="top">OUTPUTDATA(In, EA)</td><td style="width: 24.55pt;" valign="top">创建Enclave的加密报告</td>

(In,EA)

(In, EA)
<td style="width: 86.25pt;" valign="top">EGETKEY</td><td style="width: 76.55pt;" valign="top">01H(In)</td><td style="width: 68.55pt;" valign="top">KEYREQUEST(In,EA)</td><td style="width: 79.45pt;" valign="top">KEY(In,EA)</td><td style="width: 79.45pt;" valign="top"></td><td style="width: 24.55pt;" valign="top">检索一个加密密钥</td>

(In,EA)

(In)

(In,EA)

(In,EA)

(Out)

(Out,EA)
<td style="width: 86.25pt;" valign="top">ERESUME</td><td style="width: 76.55pt;" valign="top">03H(In)</td><td style="width: 68.55pt;" valign="top">TCS(In,EA)</td><td style="width: 79.45pt;" valign="top">AEP(In, EA)</td><td style="width: 79.45pt;" valign="top"></td><td style="width: 24.55pt;" valign="top">重进入Enclave模式执行</td>

(In,EA)
<td style="width: 86.25pt;" valign="top">EEXIT</td><td style="width: 76.55pt;" valign="top">04H(In)</td><td style="width: 68.55pt;" valign="top">Target(In,EA)</td><td style="width: 79.45pt;" valign="top">CurrentAEP(Out)</td><td style="width: 79.45pt;" valign="top"></td><td style="width: 24.55pt;" valign="top">退出Enclave模式</td>

(In,EA)

(Out)
<td style="width: 86.25pt;" valign="top">EACCEPT</td><td style="width: 76.55pt;" valign="top">05H(In)</td><td style="width: 68.55pt;" valign="top">SECINFO(In,EA)</td><td style="width: 79.45pt;" valign="top">EPCPAGE(In,EA)</td><td style="width: 79.45pt;" valign="top"></td><td style="width: 24.55pt;" valign="top">接受对EPC页面的更改</td>

(In,EA)
<td style="width: 86.25pt;" valign="top">EMODPE</td><td style="width: 76.55pt;" valign="top">06H(In)</td><td style="width: 68.55pt;" valign="top">SECINFO(In,EA)</td><td style="width: 79.45pt;" valign="top">EPCPAGE(In,EA)</td><td style="width: 79.45pt;" valign="top"></td><td style="width: 24.55pt;" valign="top">扩展EPC页面的权限</td>

(In,EA)
<td style="width: 86.25pt;" valign="top">EACCEPTCOPY</td><td style="width: 76.55pt;" valign="top">07H(In)</td><td style="width: 68.55pt;" valign="top">SECINFO(In,EA)</td><td style="width: 79.45pt;" valign="top">EPCPAGE(In,EA)</td><td style="width: 79.45pt;" valign="top">EPCPAGE(In,EA)</td><td style="width: 24.55pt;" valign="top">将现有EPC页面的内容拷贝到未初始化的EPC页面</td>

(In,EA)

(In,EA)

### **3.3 SGX ****技术实现**

SGX技术实现如图3所示，可总结成如下几点：

[![](https://p5.ssl.qhimg.com/t01db3646c83fad099f.png)](https://p5.ssl.qhimg.com/t01db3646c83fad099f.png)

图3 SGX 技术实现

SGX应用程序切分成Untrusted和Trusted两部分，Trust部分运行在Enclave中；

由Untrusted部分的应用程序通过ioctl系统调用的方式调用ENCLS指令创建出Enclave,并把Trust部分的代码加载到Enclave里执行；

Untrusted部分的应用通过特殊的调用接口Ecalls调用Enclave里函数的执行；

当Enclave里的函数被调用后，仅仅Enclave里的代码可访问其数据，外部的程序——不管是普通的应用程序，还是具备特权的OS、VMM、Bios都无法访问。当Enclave里的函数返回后，其数据仍保留在内存保护区；

Enclave拥有自己的代码和数据区，SGX保证代码和数据的完整和保密性。Enclave的入口点是在编译阶段预定义好，支持多线程，可访问整个Application的内存空间。下一小节详述Enclave.

EPC是SGX的内存管理核心，属于Enclave的相关数据结构和代码以及数据的存放处，是经过MEE加密存储，外部程序无法获取其实际内容，逻辑上如图4所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011f9c221aeb95c669.png)

图4 EPC内部逻辑

### **3.4 Enclave****安全机制**

形式上，Intel SGX 允许以明文形式发布应用程序的受保护部分，也就是说在Enclave建立之前，Enclave的code和data都是可以自由地进行分析检查的，当这部分受保护的程序加载进Enclave时，它的code和data将会被度量，加载完成后，度量值存放于EPC的SECS，不可更改，来自Enclave外的访问将被拒绝。

应用上，Enclave可以向远方证明自己的身份，并且提供必要的构建块（MRENCLAVE）以安全地提供密钥和凭证。应用程序也可以请求特定于Enclave或平台的密钥，这样就支持保护那些希望存储在Enclave之外的密钥和数据。

原理上，当CPU访问Enclave中数据时，首先切换到Enclave模式，Enclave模式会强制对每个内存访问进行额外的基于硬件的安全检查，由于数据是存放在EPC中，而EPC的内存内容都经过MEE加密，只有当EPC的内存内容进入CPU package时才会被解密，一旦返回EPC后立即被加密。因此即使通过各种内存攻击手段，典型的如内存嗅探，获取到EPC的内容，也是无法获知实际内容的密文。Enclave Enter/Exit的流程如图5所示，进入Enclave模式时，首先通过应

[![](https://p2.ssl.qhimg.com/t01a043749739d5e404.png)](https://p2.ssl.qhimg.com/t01a043749739d5e404.png)

图5 Enclave Entry/Exit 流程

用程序调用ENCLC指令EENTER通知CPU切换Enclave模式，之后将应用程序的上下文保存到TCS数据结构，这样CPU就切换到Enclave模式执行。当Enclave主动退出时，Enclave里的程序调用ENCLC指令EEXIT，切换回Non-Enclave模式。EENTER指令将CPU控制权从应用程序转移到Enclave里的预定位置，它会首先检查TCS是否可用，清空TLB条目，然后切换入Enclave模式，并保存好RSP、RBP和XCR0寄存器内容，最后禁用PEBS（Precise Event Based Sampling），使Enclave执行时像一条巨大的指令。EEXIT指令将进程返回其原始模式，并清除Enclave地址的TLB条目，释放TCS数据结构，另外，Enclave退出前会清空CPU寄存器以防止数据泄露。

当Enclave运行过程被中断或异常打断时，CPU通过AEX机制退回到Non-Enclave模式，在模式切换时，其运行状态会保存到EPC的SSA中，并清除TLB，处理完中断或异常利用ERESUME重进入Enclave并从SSA加载数据恢复先前状态.Enclave AEX 流程如图6所示，AEP（Asynchronous Exit Pointer）指向位于应用程序

[![](https://p5.ssl.qhimg.com/t016c3e03edb13063c9.png)](https://p5.ssl.qhimg.com/t016c3e03edb13063c9.png)

图6 Enclave AEX流程

内部的处理程序，在中断服务例程（ISR）处理异常后，该处理程序将继续执行，并决定是否调用ERESUME指令来恢复Enclave的执行。流程上，在Enclave运行过程中，CPU收到了中断/异常，Enclave首先保存其程序上下文后恢复应用程序的上下文，然后操作系统调用ISR处理中断并返回到AEP，若AEP决定要恢复Enclave的执行，它将调用ERESUME指令，Enclave退出前保存的上下文内容将被恢复，最后Enclave从原先退出的地方继续执行。

SGX的内存访问控制流程如图7所示。线性地址转物理地址流程跟传统一样由OS负责，当访问地址指向EPC时，CPU首先检查是否属于Enclave发起的请求，若是再自动到EPCM里检查访问权限是否符合。EPCM检查项包括：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010e504cea33811752.png)

图7 SGX内存访问控制

该内存页是否有效；

该内存页的类型（PT_SECS/PT_TCS/PT_REG,etc.）是否正确；

该内存页是否属于当前的Enclave;

R/W/X访问权限是否匹配；

线性地址是否正确。

Enclave具备如下安全特性：
1. 不管当前特权级别还是CPU模式（Ring3/用户模式，Ring0/内核模式，SMM，VMM，或是其他Enclave）,Enclave安全区内存都无法从外部读取或写入；
1. 在构建Enclave的时候可以设置debug属性，进行debug签名，再借助sgx-gdb 调试器可以像普通调试器调试普通软件一样调试Enclave。产品级（Released）Enclave不允许通过软件或硬件的形式进行调试（这正是本文要攻破的地方），若强行设置debug属性，将会导致Enclave创建失败，表现在EINIT时异常退出；
1. Enclave执行环境的唯一方式是通过EENTER/ERESUME这样的SGX新指令在进行一系列安全检查后进入，像传统的函数调用、跳转、寄存器操控、栈操控等方式均无法进入Enclave执行环境。当然，在Enclave内部进行传统的函数调用是没问题的。
### **3.5 Enclave ****的创建**

从上文描述可见，在外对Enclave内部不可访问，无法修改运行中Enclave的SECS，因此想通过直接修改SECS的debug域是没法实现的。山重水复疑无路，柳暗花明又一村，我们可以从创建Enclave的过程着手。本文重点探究的将Released Enclave改成可debug模式从此开始。创建Enclave可分为两大过程，首先是创建Enclave内容，即编程和编译，其次是创建其执行环境，即加载执行的过程。

**3.5.1 Enclave ****内容的创建**

[![](https://p0.ssl.qhimg.com/t01db5800e02be05a1c.png)](https://p0.ssl.qhimg.com/t01db5800e02be05a1c.png)

图8 SGX 软件开发模型

以Linux系统为例，SGX应用软件发布时在形态上分为App和Enclave.signed.so 两部分，App运行在Non-Enclave模式，属于非可信计算，Enclave.signed.so运行在Enclave模式下，属于可信计算，运行时App利用特定的Enclave接口ECalls调用Enclave.signed.so内函数的执行，同时Enclave.signed.so也可利用特定的接口OCalls来调用App内的函数，典型的如系统调用。SGX软件开发的模型如图8所示，Intel提供了SGX SDK工具包以支持用户快速开发，SDK包含了工具和代码库两大部分，工具包含：用于配置CPUSVN信息的sgx_config_cpusvn、用于解析Enclave Description

Language (EDL) file的sgx_edger8r、用于加密的sgx_encrypt、用于给Enclave.so签名的sgx_sign以及debugger工具sgx-gdb;代码库根据是否属于可信计算分成trusted（如libsgx_trts.a）和untrusted(如libsgx_urts.so)两大部分以及两者间的接口。开发SGX应用时，用户自主决定哪部分代码需要运行在Enclave中，生成Enclave文件的整体操作流程是：

首先需要用户编写期望运行在Enclave中的c/c++代码，并声明在edl文件的”trusted”段中；

然后使用SGX SDK提供的 sgx_edger8r 工具解析edl文件生成Enclave_trust.c文件；

再将Enclave_trust.c和其他c文件编译成enclave.so；

最后使用SGX SDK提供的 sgx_sign 工具对enclave.so进行签名，生成enclave.signed.so。传入sgx_sign工具的文件还包括enclave_private.pem私钥文件和定义有Enclave metadata信息的xml文件，假如要生成产品级Release的Enclave，需要传入的私钥文件是经过Intel进行签发；若是debug版本的可以使用随SGX SDK一起的Samplecode里的Enclave_private.pem。 sgx_sign将所有的metadata数据保存在enclave.signed.so ELF文件里的”.note.sgxmeta”段里。

metadata里保存着Enclave的所有属性，在运行时生成的SECS、TCS关键信息大部分来自于它，包括EINIT所需的EINITTOKEN也是基于它来生成，因此修改metadata里相关信息后可将Enclave由release版本变成可调试的debug版本。下文将重点介绍该部分。

**3.5.2 Enclave ****执行环境的创建**

Enclave的创建由普通应用程序发起，先申请Enclave页，再通过ioctl系统调用执行ENCLS指令，如ECREATE、EADD、EEXTEND、EINIT等，其细节流程如图9所示。首先，应用程序请求加载它的Enclave

[![](https://p4.ssl.qhimg.com/t01ffdc4ea359fda24f.png)](https://p4.ssl.qhimg.com/t01ffdc4ea359fda24f.png)

图9 Enclave 的创建细节

部分到内存中；接着借助ioctl调用ECREATE指令创建文件和SECS数据结构；然后通过EADD指令将Enclave的代码加载进Enclave；每个EPC页的添加到Enclave时要使用EEXTEND指令将其度量值添加到SECS;Enclave代码加载完成后调用EINIT指令完成Enclave的初始化，固化SECS。该过程跟SECS密切相关的有ECREATE和EINIT，即本文探究的将Released Enclave改成可debug的关键所在。ECREATE指令负责创建一个独一无二的Enclave的实例，建立起线性地址的布局，以及设置Enclave的属性。这属性包括debug属性，信息保存在SECS数据结构中。而 SECS 的固化是在EINIT过程中完成，若简单的在ECREATE时修改SECS，将导致EINIT时对SECS的校验失败，从而导致Enclave创建失败。因此，下节重点介绍EINIT。

**3.5.3 Enclave Init**

顾名思义，EINIT指令负责Enclave init，它是创建Enclave时最后需要执行的一个ENCLS指令，执行完EINIT后，Enclave的度量值MRENCLAVE也完成了，此后应用程序可以通过EENTER指令进入Enclave运行。EINIT指令执行如图10所示，需传入3个参数：SECS、SIGSTRUCT、EINITTOKEN，其中SECS仅Enclave本身可访问，另两个

[![](https://p3.ssl.qhimg.com/t0107a36c51821407e7.png)](https://p3.ssl.qhimg.com/t0107a36c51821407e7.png)

图10 EINIT过程

普通程序也可访问。大体执行步骤如下：

验证是否使用随附的公钥对SIGSTRUCT进行了签名；

检查SECS.MRENCLAVE是否等于SIGSTRUCT.HASHENCLAVE；

检查是否SIGSTRUCT.ATTRIBUTES中非保留位设置为1，而SIGSTRUCT.ATTRIBUTESMASK中非保留位设置为设置为0；

检查SIGSTRUCT.ATTRIBUTES中是否未设置仅Intel位，除非SIGSTRUCT由Intel签名；

检查SIGSTRUCT.ATTRIBUTES是否等于对SIGSTRUCT.ATTRIBUTEMASK与SECS.ATTRIBUTES进行逻辑与运算后的结果；

如果EINITTOKEN.VALID为0，则检查SIGSTRUCT是否由Intel签名；

如果EINITTOKEN.VALID为1，则检查EINITTOKEN的有效性；

如果EINITTOKEN.VALID为1，则检查EINITTOKEN.MRENCLAVE是否等于SECS.MRENCLAVE；

如果EINITTOKEN.VALID为1并且EINITTOKEN.ATTRIBUTES.DEBUG为1，则SECS.ATTRIBUTES.DEBUG必须为1；

从SIGSTRUCT取出签名的公钥进行SHA-256的Hash后产生MRSIGNER，将此MRSIGNER与EINITTOKEN.MRSINGER进行检验，通过后将MRSIGNER拷贝到SECS.MRSIGNER。同时基于SIGSTRUCT填写SECS.ISVSVN、SECS.ISVPRODID,完成SECS的初始化，固化SECS。

由上可见，若要调试Enclave，SECS.ATTRIBUTES.DEBUG必须为1，同时EINITTOKEN.ATTRIBUTES.DEBUG和SIGSTRUCT.ATTRIBUTES.DEBUG也必须为1，另外还要保证签名校验的成功。下面分别介绍SECS、SIGSTRUCT、EINITTOKEN的数据结构。

SECS在EPC中是4kB对齐的，数据结构如表3所示。我们比较关心的ATTRIBUTE域如表4所示。

表3 SECS数据结构
<td style="width: 98.75pt;" valign="top">Filed</td><td style="width: 52.8pt;" valign="top">Offset(Bytes)</td><td style="width: 53.75pt;" valign="top">Size(Bytes)</td><td style="width: 209.5pt;" valign="top">简介</td>

(Bytes)
<td style="width: 98.75pt;" valign="top">SIZE</td><td style="width: 52.8pt;" valign="top">0</td><td style="width: 53.75pt;" valign="top">8</td><td style="width: 209.5pt;" valign="top">Enclave的大小</td>
<td style="width: 98.75pt;" valign="top">BASEADDR</td><td style="width: 52.8pt;" valign="top">8</td><td style="width: 53.75pt;" valign="top">8</td><td style="width: 209.5pt;" valign="top">Enclave线性地址的基址</td>
<td style="width: 98.75pt;" valign="top">SSAFRAMESIZE</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 53.75pt;" valign="top">4</td><td style="width: 209.5pt;" valign="top">SSA帧的大小</td>
<td style="width: 98.75pt;" valign="top">MISCSELECT</td><td style="width: 52.8pt;" valign="top">20</td><td style="width: 53.75pt;" valign="top">4</td><td style="width: 209.5pt;" valign="top">位向量，用于指定在AEX时将哪些扩展特征保存到SSA.MISC</td>
<td style="width: 98.75pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">24</td><td style="width: 53.75pt;" valign="top">24</td><td style="width: 209.5pt;" valign="top">预留</td>
<td style="width: 98.75pt;" valign="top">ATTRIBUTES</td><td style="width: 52.8pt;" valign="top">48</td><td style="width: 53.75pt;" valign="top">16</td><td style="width: 209.5pt;" valign="top">Enclave的属性</td>
<td style="width: 98.75pt;" valign="top">MRENCLAVE</td><td style="width: 52.8pt;" valign="top">64</td><td style="width: 53.75pt;" valign="top">32</td><td style="width: 209.5pt;" valign="top">Enclave的度量值</td>
<td style="width: 98.75pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">96</td><td style="width: 53.75pt;" valign="top">32</td><td style="width: 209.5pt;" valign="top">预留</td>
<td style="width: 98.75pt;" valign="top">MRSIGNER</td><td style="width: 52.8pt;" valign="top">128</td><td style="width: 53.75pt;" valign="top">32</td><td style="width: 209.5pt;" valign="top">签名密钥对应公钥的SHA-256</td>
<td style="width: 98.75pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">160</td><td style="width: 53.75pt;" valign="top">96</td><td style="width: 209.5pt;" valign="top">预留</td>
<td style="width: 98.75pt;" valign="top">ISVPRODID</td><td style="width: 52.8pt;" valign="top">256</td><td style="width: 53.75pt;" valign="top">2</td><td style="width: 209.5pt;" valign="top">Enclave的产品ID</td>
<td style="width: 98.75pt;" valign="top">ISVSVN</td><td style="width: 52.8pt;" valign="top">258</td><td style="width: 53.75pt;" valign="top">2</td><td style="width: 209.5pt;" valign="top">Enclave的安全版本号（SVN）</td>
<td style="width: 98.75pt;" valign="top">EID</td><td style="width: 52.8pt;" valign="top">用户设定</td><td style="width: 53.75pt;" valign="top">8</td><td style="width: 209.5pt;" valign="top">Enclave ID</td>
<td style="width: 98.75pt;" valign="top">PADDING</td><td style="width: 52.8pt;" valign="top">用户设定</td><td style="width: 53.75pt;" valign="top">352</td><td style="width: 209.5pt;" valign="top">填充</td>
<td style="width: 98.75pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">260</td><td style="width: 53.75pt;" valign="top">3836</td><td style="width: 209.5pt;" valign="top">预留</td>

表4 ATTRIBUTES数据结构
<td style="width: 99.0pt;" valign="top">Field</td><td style="width: 3.0cm;" valign="top">Bit Posttion</td><td style="width: 230.75pt;" valign="top">简介</td>
<td style="width: 99.0pt;" valign="top">RESERVED</td><td style="width: 3.0cm;" valign="top">0</td><td style="width: 230.75pt;" valign="top">预留</td>
<td style="width: 99.0pt;" valign="top">DEBUG</td><td style="width: 3.0cm;" valign="top">1</td><td style="width: 230.75pt;" valign="top">置1后，enclave允许调试器读写enclave的数据</td>
<td style="width: 99.0pt;" valign="top">MODE64BIT</td><td style="width: 3.0cm;" valign="top">2</td><td style="width: 230.75pt;" valign="top">Enclave运行在64位模式</td>
<td style="width: 99.0pt;" valign="top">RESERVED</td><td style="width: 3.0cm;" valign="top">3</td><td style="width: 230.75pt;" valign="top">必须置0</td>
<td style="width: 99.0pt;" valign="top">PROVISIONKEY</td><td style="width: 3.0cm;" valign="top">4</td><td style="width: 230.75pt;" valign="top">EGETKEY可获取Provisioning Key</td>
<td style="width: 99.0pt;" valign="top">EINITTOKENKEY</td><td style="width: 3.0cm;" valign="top">5</td><td style="width: 230.75pt;" valign="top">EGETKEY可获取EINIT token key</td>
<td style="width: 99.0pt;" valign="top">RESERVED</td><td style="width: 3.0cm;" valign="top">63：6</td><td style="width: 230.75pt;" valign="top">预留</td>
<td style="width: 99.0pt;" valign="top">XFRM</td><td style="width: 3.0cm;" valign="top"></td><td style="width: 230.75pt;" valign="top">XSAVE mask</td>

SIGSTRUCT包含了Enclave的签名信息，SHA-256摘要的ENCLAVEHASH，3072bit长度的MODULUS、SIGNATURE、Q1、Q2，也是必须4kB对齐的。Q1、Q2的算法如下：

Q1 = floor(Signature^2 / Modulus);

Q2 = floor((Signature^3 – q1 * Signature * Modulus) / Modulus);

SIGSTRUCT数据结构如表5所示，表中的“Y”代表该域的数据需要纳入需签名的数据里。

表5 SIGSTRUCT数据结构
<td style="width: 81.95pt;" valign="top">Field</td><td style="width: 52.8pt;" valign="top">OFFSET(Bytes)</td><td style="width: 52.8pt;" valign="top">Size(Bytes)</td><td style="width: 180.75pt;" valign="top">简介</td><td style="width: 46.5pt;" valign="top">Signed</td>

(Bytes)
<td style="width: 81.95pt;" valign="top">HEADER</td><td style="width: 52.8pt;" valign="top">0</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 180.75pt;" valign="top">必须是06000000E10000000000010000000000H</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">VENDOR</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 180.75pt;" valign="top">Intel Enclave: 00008086HNon-Intel Enclave: 00000000H</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">DATE</td><td style="width: 52.8pt;" valign="top">20</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 180.75pt;" valign="top">编译日期:yyyymmdd</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">HEADER2</td><td style="width: 52.8pt;" valign="top">24</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 180.75pt;" valign="top">必须是01010000600000006000000001000000H</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">SWDEFINED</td><td style="width: 52.8pt;" valign="top">40</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 180.75pt;" valign="top">供软件使用</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">44</td><td style="width: 52.8pt;" valign="top">84</td><td style="width: 180.75pt;" valign="top">必须是0</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">MODULUS</td><td style="width: 52.8pt;" valign="top">128</td><td style="width: 52.8pt;" valign="top">384</td><td style="width: 180.75pt;" valign="top">公钥</td><td style="width: 46.5pt;" valign="top">N</td>
<td style="width: 81.95pt;" valign="top">EXPONENT</td><td style="width: 52.8pt;" valign="top">512</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 180.75pt;" valign="top">RSA Exponent=3</td><td style="width: 46.5pt;" valign="top">N</td>
<td style="width: 81.95pt;" valign="top">SIGNATURE</td><td style="width: 52.8pt;" valign="top">516</td><td style="width: 52.8pt;" valign="top">384</td><td style="width: 180.75pt;" valign="top">SIGSTRUCT本身的签名</td><td style="width: 46.5pt;" valign="top">N</td>
<td style="width: 81.95pt;" valign="top">MISCSELECT</td><td style="width: 52.8pt;" valign="top">900</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 180.75pt;" valign="top">用于指定SSA帧扩展特征</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">MISCMASK</td><td style="width: 52.8pt;" valign="top">904</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 180.75pt;" valign="top">MISCSELECT的mask</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">908</td><td style="width: 52.8pt;" valign="top">20</td><td style="width: 180.75pt;" valign="top">必须是0</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">ATTRIBUTES</td><td style="width: 52.8pt;" valign="top">928</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 180.75pt;" valign="top">Enclave的属性</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">ATTRIBUTEMASK</td><td style="width: 52.8pt;" valign="top">944</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 180.75pt;" valign="top">ATTRIBUTES的mask</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">ENCLAVEHASH</td><td style="width: 52.8pt;" valign="top">960</td><td style="width: 52.8pt;" valign="top">32</td><td style="width: 180.75pt;" valign="top">本数据结构产生的MRENCLAVE</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">992</td><td style="width: 52.8pt;" valign="top">32</td><td style="width: 180.75pt;" valign="top">必须是0</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">ISVPRODID</td><td style="width: 52.8pt;" valign="top">1024</td><td style="width: 52.8pt;" valign="top">2</td><td style="width: 180.75pt;" valign="top">Enclave产品ID</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">ISVSVN</td><td style="width: 52.8pt;" valign="top">1026</td><td style="width: 52.8pt;" valign="top">2</td><td style="width: 180.75pt;" valign="top">Enclave安全版本号</td><td style="width: 46.5pt;" valign="top">Y</td>
<td style="width: 81.95pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">1028</td><td style="width: 52.8pt;" valign="top">12</td><td style="width: 180.75pt;" valign="top">必须是0</td><td style="width: 46.5pt;" valign="top">N</td>
<td style="width: 81.95pt;" valign="top">Q1</td><td style="width: 52.8pt;" valign="top">1040</td><td style="width: 52.8pt;" valign="top">384</td><td style="width: 180.75pt;" valign="top">RSA签名校验值1</td><td style="width: 46.5pt;" valign="top">N</td>
<td style="width: 81.95pt;" valign="top">Q2</td><td style="width: 52.8pt;" valign="top">1424</td><td style="width: 52.8pt;" valign="top">384</td><td style="width: 180.75pt;" valign="top">RSA签名校验值2</td><td style="width: 46.5pt;" valign="top">N</td>

EINITTOKEN 又称Launch Token,用来检验该Enclave是否允许启动，512 Bytes对齐，其数据结构如表6所示。EINITTOKEN是由Launch Enclave,简称LE生成，LE属于Architectural Enclave之一，由Intel编写并签名后随SGX SDK一起分发。EINITTOKEN里含有ATTRIBUTES字段，并且采用CPU内部的Launch key进行MAC，这样防止它被其他程序改变EINITTOKEN的值。这是本文需要攻破的另一个点，详见下文。

表6 EINITTOKEN数据结构
<td style="width: 118.8pt;" valign="top">Field</td><td style="width: 52.8pt;" valign="top">OFFSET(Bytes)</td><td style="width: 52.8pt;" valign="top">Size(Bytes)</td><td style="width: 37.6pt;" valign="top">MACed</td><td style="width: 152.8pt;" valign="top">简介</td>

(Bytes)
<td style="width: 118.8pt;" valign="top">VALID</td><td style="width: 52.8pt;" valign="top">0</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 37.6pt;" valign="top">Y</td><td style="width: 152.8pt;" valign="top">Bits 0:1 Valid 0:Debug</td>
<td style="width: 118.8pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 52.8pt;" valign="top">44</td><td style="width: 37.6pt;" valign="top">Y</td><td style="width: 152.8pt;" valign="top">必须是0</td>
<td style="width: 118.8pt;" valign="top">ATTRIBUTES</td><td style="width: 52.8pt;" valign="top">48</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 37.6pt;" valign="top">Y</td><td style="width: 152.8pt;" valign="top">Enclave的属性</td>
<td style="width: 118.8pt;" valign="top">MRENCLAVE</td><td style="width: 52.8pt;" valign="top">64</td><td style="width: 52.8pt;" valign="top">32</td><td style="width: 37.6pt;" valign="top">Y</td><td style="width: 152.8pt;" valign="top">Enclave的MRENCLAVE</td>
<td style="width: 118.8pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">96</td><td style="width: 52.8pt;" valign="top">32</td><td style="width: 37.6pt;" valign="top">Y</td><td style="width: 152.8pt;" valign="top">预留</td>
<td style="width: 118.8pt;" valign="top">MRSIGNER</td><td style="width: 52.8pt;" valign="top">128</td><td style="width: 52.8pt;" valign="top">32</td><td style="width: 37.6pt;" valign="top">Y</td><td style="width: 152.8pt;" valign="top">Enclave的MRSIGNER</td>
<td style="width: 118.8pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">160</td><td style="width: 52.8pt;" valign="top">32</td><td style="width: 37.6pt;" valign="top">Y</td><td style="width: 152.8pt;" valign="top">预留</td>
<td style="width: 118.8pt;" valign="top">CPUSVNLE</td><td style="width: 52.8pt;" valign="top">192</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 37.6pt;" valign="top">N</td><td style="width: 152.8pt;" valign="top">Launch Enclave的CPUSVN</td>
<td style="width: 118.8pt;" valign="top">ISVPRODIDLE</td><td style="width: 52.8pt;" valign="top">208</td><td style="width: 52.8pt;" valign="top">2</td><td style="width: 37.6pt;" valign="top">N</td><td style="width: 152.8pt;" valign="top">Launch Enclave的ISVPRODID</td>
<td style="width: 118.8pt;" valign="top">ISVSVNLE</td><td style="width: 52.8pt;" valign="top">210</td><td style="width: 52.8pt;" valign="top">2</td><td style="width: 37.6pt;" valign="top">N</td><td style="width: 152.8pt;" valign="top">Launch Enclave的ISVSVN</td>
<td style="width: 118.8pt;" valign="top">RESERVED</td><td style="width: 52.8pt;" valign="top">212</td><td style="width: 52.8pt;" valign="top">24</td><td style="width: 37.6pt;" valign="top">N</td><td style="width: 152.8pt;" valign="top">预留</td>
<td style="width: 118.8pt;" valign="top">MASKEDMISCSELECTLE</td><td style="width: 52.8pt;" valign="top">236</td><td style="width: 52.8pt;" valign="top">4</td><td style="width: 37.6pt;" valign="top">N</td><td style="width: 152.8pt;" valign="top">Launch Enclave的MASKEDMISCSELECT</td>
<td style="width: 118.8pt;" valign="top">MASKEDATTRIBUTELE</td><td style="width: 52.8pt;" valign="top">240</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 37.6pt;" valign="top">N</td><td style="width: 152.8pt;" valign="top">Launch Enclave的MASKEDATTRIBUTE</td>
<td style="width: 118.8pt;" valign="top">KEYID</td><td style="width: 52.8pt;" valign="top">256</td><td style="width: 52.8pt;" valign="top">32</td><td style="width: 37.6pt;" valign="top">N</td><td style="width: 152.8pt;" valign="top">Key的保护值</td>
<td style="width: 118.8pt;" valign="top">MAC</td><td style="width: 52.8pt;" valign="top">288</td><td style="width: 52.8pt;" valign="top">16</td><td style="width: 37.6pt;" valign="top">N</td><td style="width: 152.8pt;" valign="top">采用Launch key对EINITTOKEN的MAC</td>



## 4 Released Enclave to Debug静态转换法

上文3.5.1节提到在修改metadata里相关信息后可将Enclave由release版本变成可调试的debug版本，本节将详细探究，这种转换是修改Enclave ELF文件，是在Enclave运行前完成，因此称之为静态转换法。

如上文所述，Enclave的签名工具sgx_sign将所有的metadata数据保存在enclave.signed.so ELF文件里的”.note.sgxmeta”段里。metadata里保存着Enclave的所有属性，在运行时生成的SECS、TCS关键信息大部分来自于它，包括EINIT所需的EINITTOKEN也是基于它来生成，因此修改metadata里相关信息后可将Enclave由release版本变成可调试的debug版本。metadata的数据结构如表7所示，跟当前研究相关的域包括 version、attributes、enclave_css。

表7 metadata数据结构

```
typedef struct _metadata_t 
`{`
    uint64_t            magic_num;  /* The magic number identifying the file as a signed enclave image */
    uint64_t            version;               /* The metadata version */
    uint32_t            size;                  /* The size of this structure */
    uint32_t            tcs_policy;            /* TCS management policy */
    uint32_t            ssa_frame_size;        /* The size of SSA frame in page */
    uint32_t            max_save_buffer_size;  /* Max buffer size is 2632 */
    uint32_t            desired_misc_select;
    uint32_t            tcs_min_pool;          /* TCS min pool*/         
    uint64_t            enclave_size;          /* enclave virtual size */
    sgx_attributes_t    attributes;            /* XFeatureMask to be set in SECS. */
    enclave_css_t       enclave_css;           /* The enclave signature */
    data_directory_t    dirs[DIR_NUM];
    uint8_t             data[18592];
`}`metadata_t;
```

version代表metadata的版本号，如：2.3/2.1/1.4，为了兼容所有的版本，一个enclave.signed.so里包含有三段metadata，据本人实测发现，这三段metadata仅version域不一样外，其他域完全一样，同时在Ubuntu16.04上安装测试版本的PSW_2.2.100.45311仅支持1.4版本，因此本文所述的sgx_repack_tool仅生成一段version为1.4的metadata。

attributes域的sgx_attributes_t数据结构如表8所示，我们需要将flags添加上SGX_FLAGS_DEBUG 属性，即debug位置1。

表8 sgx_attributes_t数据结构

```
typedef struct _attributes_t
`{`
    uint64_t      flags;  /* 包含有debug属性的旗标，各bit含义与Enclave Signature的一致 */
    uint64_t      xfrm;
`}` sgx_attributes_t;

/* Enclave Flags Bit Masks */
#define SGX_FLAGS_INITTED 0x0000000000000001ULL /* If set, then the enclave is initialized */
#define SGX_FLAGS_DEBUG 0x0000000000000002ULL /* If set, then the enclave is debug */
#define SGX_FLAGS_MODE64BIT 0x0000000000000004ULL /* If set, then the enclave is 64 bit */
#define SGX_FLAGS_PROVISION_KEY 0x0000000000000010ULL /* If set, then the enclave has access to provision key */
#define SGX_FLAGS_EINITTOKEN_KEY 0x0000000000000020ULL /* If set, then the enclave has access to EINITTOKEN key */
#define SGX_FLAGS_RESERVED       (~(SGX_FLAGS_INITTED | SGX_FLAGS_DEBUG | SGX_FLAGS_MODE64BIT | SGX_FLAGS_PROVISION_KEY | SGX_FLAGS_EINITTOKEN_KEY))
```

表9 enclave_css_t数据结构

```
typedef struct _enclave_css_t `{`        /* 1808 bytes */
    css_header_t    header;             /* (0) */
    css_key_t       key;                /* (128) */
    css_body_t      body;               /* (900) */
    css_buffer_t    buffer;             /* (1028) */
`}` enclave_css_t;

typedef struct _css_buffer_t `{`         /* 780 bytes */
    uint8_t  reserved[12];         /* (1028) Must be 0 */
    uint8_t  q1[SE_KEY_SIZE];     /* (1040) Q1 value for RSA Signature Verification */
    uint8_t  q2[SE_KEY_SIZE];    /* (1424) Q2 value for RSA Signature Verification */
`}` css_buffer_t;
其中，q1 = floor(Signature^2 / Modulus);
q2 = floor((Signature^3 - q1 * Signature * Modulus) / Modulus);
```

表9 enclave_css_t数据结构（续）

```
typedef struct _css_header_t `{`        /* 128 bytes */
    uint8_t  header[12];       /* (0) must be (06000000E100000000000100H) */
    uint32_t type;            /* (12) bit 31: 0 = prod, 1 = debug; Bit 30-0: Must be zero */
    uint32_t module_vendor;             /* (16) Intel=0x8086, ISV=0x0000 */
    uint32_t date;                      /* (20) build date as yyyymmdd */
    uint8_t  header2[16];   /* (24) must be (01010000600000006000000001000000H) */
    uint32_t hw_version;  /* (40) For Launch Enclaves: HWVERSION != 0. Others, HWVERSION = 0 */
    uint8_t  reserved[84];              /* (44) Must be 0 */
`}` css_header_t;

typedef struct _css_key_t `{`           /* 772 bytes */
    uint8_t modulus[SE_KEY_SIZE];    /* (128) Module Public Key (keylength=3072 bits) */
    uint8_t exponent[SE_EXPONENT_SIZE]; /* (512) RSA Exponent = 3 */
    uint8_t signature[SE_KEY_SIZE];     /* (516) Signature over Header and Body */
`}` css_key_t;

typedef struct _css_body_t `{`            /* 128 bytes */
    sgx_misc_select_t   misc_select;    /* (900) The MISCSELECT that must be set */
    sgx_misc_select_t   misc_mask;      /* (904) Mask of MISCSELECT to enforce */
    uint8_t             reserved[20];   /* (908) Reserved. Must be 0. */
    sgx_attributes_t    attributes;     /* (928) Enclave Attributes that must be set */
    sgx_attributes_t    attribute_mask; /* (944) Mask of Attributes to Enforce */
    sgx_measurement_t   enclave_hash;   /* (960) MRENCLAVE - (32 bytes) */
    uint8_t             reserved2[32];  /* (992) Must be 0 */
    uint16_t            isv_prod_id;    /* (1024) ISV assigned Product ID */
    uint16_t            isv_svn;        /* (1026) ISV assigned SVN */
`}` css_body_t;
```

enclave_css域代表的是Enclave Signature Structure，其代码形式的数据结构enclave_css_t如表9所示。该数据结构中必须修改body域中的attributes及对应的attribute_mask，将attributes的flags置上SGX_FLAGS_DEBUG，将attribute_mask的flags的 SGX_FLAGS_DEBUG清零；同时需要修改header域的type，将其第31位置1，代表需要debug；再将header域的module_vendor置成0，伪装成非Intel发布。因为修改header和body影响了key域的signature签名，所以须对Enclave Signature Structure进行重签名，操作时将key域的modulus置换成Enclave debug 私钥对应的公钥，再使用私钥对Enclave Signature Structure的header和body域进行签名。因为key域的改变，buffer域的q1和q2也需要根据公式

q1 = floor(Signature^2 / Modulus);

q2 = floor((Signature^3 – q1 * Signature * Modulus) / Modulus);

进行修正 。

至此，将Released Enclave转换成debug版本已经呼之欲出，我们通过编写一个sgx_repack_tool工具将上述的修改操作自动化完成，将enclave_release.signed.so的metadata的相应位域修改后生成enclave_debug.signed.so，这样通过SGX SDK发布的sgx-gdb工具可以对enclave_debug.signed.so进行调试。如图11所示，将随同 SGX SDK一起发布Samplecode的Enclave_private.pem和enclave_release.signed.so文件做为输入，经过sgx_repack_tool 工具转换后生成可debug的enclave_debug.signed.so。

[![](https://p4.ssl.qhimg.com/t01feaf37ab0b805199.png)](https://p4.ssl.qhimg.com/t01feaf37ab0b805199.png)

图11 sgx_repack_tool

静态转换法所需的修改点，总结如表11所示。

表11 需要修改的metadata数据域
<td style="width: 213.05pt;" valign="top">序号</td><td style="width: 213.05pt;" valign="top">数据域</td>
<td style="width: 213.05pt;" valign="top">1</td><td style="width: 213.05pt;" valign="top">Metadata.version</td>
<td style="width: 213.05pt;" valign="top">2</td><td style="width: 213.05pt;" valign="top">Metadata.attributes.flags</td>
<td style="width: 213.05pt;" valign="top">3</td><td style="width: 213.05pt;" valign="top">SIGSTRUCT.TYPE</td>
<td style="width: 213.05pt;" valign="top">4</td><td style="width: 213.05pt;" valign="top">SIGSTRUCT.VENDOR</td>
<td style="width: 213.05pt;" valign="top">5</td><td style="width: 213.05pt;" valign="top">SIGSTRUCT. ATTRIBUTES</td>
<td style="width: 213.05pt;" valign="top">6</td><td style="width: 213.05pt;" valign="top">SIGSTRUCT.ATTRIBUTEMASK</td>
<td style="width: 213.05pt;" valign="top">7</td><td style="width: 213.05pt;" valign="top">SIGSTRUCT. MODULUS</td>
<td style="width: 213.05pt;" valign="top">8</td><td style="width: 213.05pt;" valign="top">SIGSTRUCT.SIGNATURE</td>
<td style="width: 213.05pt;" valign="top">9</td><td style="width: 213.05pt;" valign="top">SIGSTRUCT.Q1</td>
<td style="width: 213.05pt;" valign="top">10</td><td style="width: 213.05pt;" valign="top">SIGSTRUCT.Q2</td>



## 5 Released Enclave to Debug动态转换法

静态转换法需要事先拿到enclave_release.sign.so后转换，当运行Enclave的时候还需要在Ring0程序创建Enclave的API sgx_create_enclave将Debug_Flag 参数置1，实现上可通过HOOK Ring0的Application的sgx_create_enclave ，将其Debug_Flag参数置1。但这样使用起来存在一定的局限性，本节探究一种更高级的方法，不需要HOOK Ring0的Application,也不需要修改enclave_release.sign.so，就在用户正常使用SGX Application的时候动态修改，实现debug无感知。我们称这种方法为Released Enclave to Debug动态转换法。

动态转换法的关键是修改Enclave的SECS.ATTRIBUTES.DEBUG,但SECS对Enclave外所有程序不可见。因此从SECS的创建入手，即Enclave的ECREATE和EINIT。ECREATE负责创建SECS的EPC页，在其参数secs上直接修改两处：
1. secs.attributes |= SGX_FLAGS_DEBUG
1. secs.mrsigner 替换成我们自己的debug模式的公钥的sha256
即可。比较复杂的是EINIT，上文分析EINIT过程可见，EINIT所需的参数SIGSTRUCT、EINITTOKEN这两个数据结构对普通应用程序可见，SECS的初始化依赖SIGSTRUCT，如若成功在SIGSTRUCT、EINITTOKEN里修改了DEBUG属性，那么SECS.ATTRIBUTES.DEBUG也将成功被置位，这样Enclave就变得可被debug。SIGSTRUCT的修改轻而易举，修改后仅需注意使用debug 密钥重新生成新的签名即可，关键问题在于EINITTOKEN。EINITTOKEN由LE生成，生成后虽然对普通程序可见，但是其内容经过LE key签名，我们无法获取LE key,意味着修改EINITTOKEN后而没有重签名，在EINIT时对EINITTOKEN的校验将会失败。那么，能不能在EINITTOKEN生成的过程下手，将其内容篡改呢？答案是肯定的。下面分析EINITTOKEN的生成过程。

EINITTOKEN的生成逻辑如图12所示，在Linux版本的SGX中，LE 属于Architectural Enclave，随SDK一起分发，运行时受aesm（Architectural Enclave Service Manager）守护进程管理。需EINITTOKEN时，应用程序将Enclave的MRENCLAVE、MRSIGNER、ATTRIBUTES等以protobuf形式封包，通过socket方式向aesm发起请求，aesm调用LE生成EINITTOKEN，再以protobuf封装EINITTOKEN

[![](https://p4.ssl.qhimg.com/t015ff0b195b551cc56.png)](https://p4.ssl.qhimg.com/t015ff0b195b551cc56.png)

图12 EINITTOKEN生成逻辑

通过socket方式返回给应用程序。如若在此过程中，将MRSIGNER改成我们自己debug密钥对中公钥的SHA-256，同时将ATTRIBUTES的DEBUG置位，那么将可得到具备debug功能的EINITTOKEN。另外，跟静态转换法一样，用同样的debug密钥修改SIGSTRUCT的ATTRIBUTES和相关域。动态转换法可简单的概述为：保持enclave_release.signed.so不变，在其Enclave创建的过程修改debug属性，并用自己可控的debug版本的密钥替换掉原有的released密钥信息来完成ECREATE和EINIT。实测发现，经此修改后仍出现问题，原因在于应用程序使用SGX SDK中的libsgx_urts.so做加载Enclave的初始化相关工作，如sgx_create_enclave/sgx_create_enclave_ex ，欲加载的Enclave是否采用debug模式运行以debug参数的形式传入sgx_create_enclave/sgx_create_enclave_ex  API，而后借助get_misc_attr函数对欲加载的Enclave的attribute进行校验，若Enclave的metadata信息标明该Enclave为release版本，此刻的EINITTOKEN却要使能attribute的debug位，将导致校验失败，从而退出Enclave的初始化加载。因此，还要设法绕过此检测，方法也比较简单，因为函数里仅能检测debug位是否匹配，无法检测EINITTOKEN的签名信息是否正确，所以操作上仅需将生成的带debug功能的EINITTOKEN的debug位清零后供get_misc_attr函数进行校验即可。



[![](https://p2.ssl.qhimg.com/t01e60a44cee50dd3ca.png)](https://p2.ssl.qhimg.com/t01e60a44cee50dd3ca.png)

图13 ECREATE 篡改流程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0108ebd1d8fd0881df.png)

图14 EINIT 篡改流程

综上，动态转换法实现时采取HOOK SGX Driver，同时在Ring3运行SGX Debug Helper的应用程序，SGX应用程序本身不做任何修改。其中HOOK SGX Driver负责捕获请求EINITTOKEN时的报文和转发到SGX Debug Helper,同时HOOK Enclave ECREATE 和 EINIT，修改其指令参数；SGX Debug Helper负责管理签名密钥和篡改来自HOOK SGX Driver的protobuf的报文。ECREATE的流程如图13所示，在SGX Driver中HOOK ECREATE的函数，当SGX应用程序通过ioctl调用ECREATE函数时，向SGX Debug Helper程序请求debug 公钥的MRSIGNER，获取到MRSIGNER后篡改ECREATE参数secs.mrsigner和secs.attributes 。EINIT的流程如图14所示，SGX Driver HOOK socket，当SGX应用程序通过SGX SDK中的GetLauchTokenRequest函数发出请求EINITTOKEN时，将其protobuf报文转发到SGX Debug Helper,由SGX Debug Helper修改报文里的attribute和mrsigner并重新生成新的protobuf报文给SGX HOOK Driver,之后SGX HOOK Driver将新生成的protobuf报文转给aesm，aesm调用LE获取到EINITTOKEN后通过SGX SDK函数GetLaunchTokenResponse将EINITTOKEN以protobuf形式返回，同样此响应的socket被SGX HOOK Driver拦获并转发给SGX Debuge Helper, 由SGX Debuge Helper篡改响应报文——生成real EINITTOKEN和fake EINITTOKEN（针对real EINITTOKEN修改其attribute为not debug）,并将这两个token一并发送给SGX HOOK Driver,SGX HOOK Driver自己留住real EINITTOKEN,将fake EINITTOKEN 以protobuf形式发送给SGX 应用程序，此后SGX应用程序采用fake EINITTOKEN 通过get_misc_attr函数进行校验并成功，最后借助ioctl系统调用执行EINIT指令，此时SGX HOOK Drvier对EINIT参数EINITTOKEN修正为real EINITTOKEN,再篡改SIGSTRUCT参数，EINIT 成功执行，大功告成。

动态转换法的主要思想是在SGX SDK中libsgx_uae_service.so 的 oal_get_launch_token函数通过socket 以protobuf封装参数信息，向aesm请求产生EINITTOKEN前，将protobuf的信息进行篡改以产生支持debug的EINITTOKEN；同时在SGX 驱动中将ECREATE和EINIT的参数SECS和SIGSTRUCT进行修改。

请求生成EINITTOKEN的修改点：
1. signature.key.modules 将其改成我们自己的debug模式的公钥；
1. sgx_attributes_t.flags |= SGX_FLAGS_DEBUG.
ECREATE的修改：

将ECREATE所需参数secs进行如下修改
1. secs.attributes |= SGX_FLAGS_DEBUG;
1. secs.mrsigner 替换成我们自己的debug模式的公钥的sha256.
EINIT的修改：

将EINIT所需的SIGSTRUCT参数进行修改，如表12所示

表12  动态转换时SIGSTRUCT的修改处
<td style="width: 76.3pt;" valign="top">序号</td><td style="width: 349.8pt;" valign="top">数据域</td>
<td style="width: 76.3pt;" valign="top">1</td><td style="width: 349.8pt;" valign="top">SIGSTRUCT.header.header1[1] |=0x1ULL &lt;&lt;63</td>
<td style="width: 76.3pt;" valign="top">2</td><td style="width: 349.8pt;" valign="top">SIGSTRUCT.header.vendor = 0</td>
<td style="width: 76.3pt;" valign="top">3</td><td style="width: 349.8pt;" valign="top">SIGSTRUCT.body.attributes |= SGX_FLAGS_DEBUG</td>
<td style="width: 76.3pt;" valign="top">4</td><td style="width: 349.8pt;" valign="top">SIGSTRUCT.body.attributemask[0] &amp;= ~SGX_FLAGS_DEBUG</td>
<td style="width: 76.3pt;" valign="top">5</td><td style="width: 349.8pt;" valign="top">SIGSTRUCT.modulus</td>
<td style="width: 76.3pt;" valign="top">6</td><td style="width: 349.8pt;" valign="top">SIGSTRUCT.signature</td>
<td style="width: 76.3pt;" valign="top">7</td><td style="width: 349.8pt;" valign="top">SIGSTRUCT.q1</td>
<td style="width: 76.3pt;" valign="top">8</td><td style="width: 349.8pt;" valign="top">SIGSTRUCT.q2</td>



## 6 总结

本文从SGX的工作模型入手，研究了SGX的工作原理，特别是Enclave的保护机制和它的创建过程，从Enclave的创建过程得到启发，实现了静态转换和动态转换不同的两种方法对产品级的Enclave实现了debug调试。研究是在2018年进行，基于Linux操作系统，当时SGX的最新版本是2.2，测试验证工作也是基于2.2版本进行。现在已进入20年代，SGX新版本也到了2.6，在新版本上测试验证工作留给感兴趣的读者自行完成。

## 

## 参考文献

[1]Frank McKeen.Intel® Software Guard Extensions(Intel® SGX) [EB/OL].http://web.stanford.edu/class/ee380/Abstracts/150415-slides.pdf

[2]Intel.Intel® Software Guard Extensions Programming

Reference. OCTOBER 2014

[3] [Alexandre Adamski](https://blog.quarkslab.com/author/alexandre-adamski.html). [Overview of Intel SGX – Part 1, SGX Internals](https://blog.quarkslab.com/overview-of-intel-sgx-part-1-sgx-internals.html) [EB/OL]. [https://blog.quarkslab.com/overview-of-intel-sgx-part-1-sgx-internals.html](https://blog.quarkslab.com/overview-of-intel-sgx-part-1-sgx-internals.html)
