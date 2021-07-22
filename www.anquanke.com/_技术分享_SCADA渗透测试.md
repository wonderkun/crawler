> 原文链接: https://www.anquanke.com//post/id/86319 


# 【技术分享】SCADA渗透测试


                                阅读量   
                                **101907**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：research.aurainfosec.io
                                <br>原文地址：[http://research.aurainfosec.io/scada-penetration-testing/](http://research.aurainfosec.io/scada-penetration-testing/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t01940cf734c13b658f.png)](https://p4.ssl.qhimg.com/t01940cf734c13b658f.png)**

****

译者：[myh0st_2015](http://bobao.360.cn/member/contribute?uid=1371972097)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**SCADA简介**

SCADA（Supervisory Control And Data Acquisition）即数据采集与监视控制系统。SCADA系统是以计算机为基础的DCS与电力自动化监控系统;它应用领域很广，可以应用于电力、冶金、石油、化工、燃气、铁路等领域的数据采集与监视控制以及过程控制等诸多领域。

近年来，SCADA系统已经从专有，封闭的网络和系统转移到开放系统和TCP / IP网络。 这暴露了这些网络与传统计算机网络面临的相同风险。 然而，这并不一定意味着SCADA评估的安全评估方法仍然是一样的。

根据我们在进行SCADA评估的经验，我们注意到每次评估都是不同的，每一次都需要基于系统功能和行业类型的独特方法。在这篇博文中，我将分享我的 进行SCADA评估的经验，并讨论哪些最佳方法和工具最适合评估这些高度敏感的系统。

<br>

**我们从协议层看SCADA**

SCADA系统支持各种协议，如DNP3，ModBus，IEC 60870，BACnet，LonWorks和EPICS。在这篇博文中，我们将继续讨论ModBus over TCP协议，因为它仍然广泛应用于控制系统。

ModBus是用于与可编程逻辑控制器（PLC）通信的串行通信协议，可以通过TCP（端口502）使用。要使用Modbus进行通信的每个设备都有一个唯一的地址。设备使用主从模型进行通信，只有一个设备（主站或从站）才能启动事务（称为“查询”）。从站通常是SCADA网络上的终端设备（阀门，传感器或仪表读取），处理信息并将其输出发送给主站。

ModBus帧由目标设备地址（或广播地址），定义请求动作的功能代码，数据字段和错误检查字段组成。默认情况下，ModBus没有身份验证和加密，但可以通过SSL / TLS传输，以防止嗅探，欺骗和重播攻击。

<br>

**一个典型的SCADA网络**

站在攻击者的角度可以从网络架构图中看出攻击面以及与网络中其他部分的隔离程度。下一代的SCADA网络将会设计IoT（物联网），从而增加维护和集成的便利来降低基础架构成本。

[![](https://p0.ssl.qhimg.com/t011be4702968471e2e.png)](https://p0.ssl.qhimg.com/t011be4702968471e2e.png)

从架构图可以看出，SCADA网络与企业网络是通过防火墙隔开的，防火墙配置正确，不允许访问SCADA网络。

SCADA涉及三个主要关键点：

1 人操作的接口与控制平台：通常使用windows工作站通过软件来管理和控制网络上的PLC。如果工作站被攻击了，那么SCADA网络中的所有内容都可以被访问。

2 PLC（Programmable Logic Controller-可编程逻辑控制器）：可编程逻辑控制器是种专门为在工业环境下应用而设计的数字运算操作电子系统。它采用一种可编程的存储器，在其内部存储执行逻辑运算、顺序控制、定时、计数和算术运算等操作的指令，通过数字式或模拟式的输入输出来控制各种类型的机械设备或生产过程。我们可以通过网路浏览器、Telnet、SSH访问PLC，这样PLC就可能受到各种应用程序和网络层的攻击。一旦遭到攻击，那么攻击者就可以操纵输入/输出设备，并对组织造成损害。

3 终端设备（传感器，阀门或泵）：终端设备安装在远程站点。他们可以通过无线电、串型接口、以太网或调制解调器等通信链路向PLC反馈。如果受到攻击可能损害环境的完整性。

注意：上述组件是每个SCADA网络的标准配置，又是你也会发现其他设备比如数据库服务器，串行设备接口等。

<br>

**渗透测试方法**

**准备工作**

通常，组织很少会把SCADA测试放在QA环境。所以假设必须要对SCADA网络进行实时评估，那我们要考虑所有可能的情况。建议在做测试之前做好准备，并确保每个测试阶段所有涉及到的部门都应该通知到。

**熟悉目标**

做任何评估的第一个先决条件。渗透测试者需要了解SCADA的作用：有什么关键任务、提供什么功能、最终用户是谁以及他对组织的作用。研究系统文档，对实施的产品和供应商进行自己的研究，挖掘已知产品漏洞，并且在此阶段记录默认口令。这是就可以做威胁建模。

**研究网络架构**

研究网络架构的主要目的是在逻辑上了解SCADA环境的每个组件如何相互关联（这个是非常复杂的）。还应该了解设计哪些组件以及他们如何隔离，如何连接或暴露在更加广泛的网络中。这个阶段还涉及网络中存在的各种子网的识别。了解企业网络与SCADA网络是否分离是非常重要的。这个阶段就可以确定我的攻击面。

**探索网络**

有了上述阶段的信息，可以对网络进行探索了，但是前提是要在客户同意的情况下。首选的方法是对知名的端口进行慢速扫描，列出SCADA相关的网络协议和服务。

尝试选择不同的时间选项来确保不会占用带宽或造成DOS攻击，由于SCADA系统是非常脆弱的很容易造成DOS的情况。这个阶段也快尝试使用wireshark来嗅探流量，看是否存在任何明文传输的问题。在这个阶段要经常与利益相关者进行沟通。

**攻击计划**

以上阶段应该已经提供了足够的信息让你知道该如何测试以及测试哪些应用。在攻击之前应该记录所有测试的方法步骤，这样在后面测试敏感和脆弱的系统时更有条理。

**实施攻击（不要暴力攻击）**

对每个漏洞单独测试利用可以帮助我们确定漏洞的根本原因，以防任何设备出现故障的意外。如果发生这种情况应该及时与客户沟通。应该利用SCADA网络中的每个组件，即网络基础设施、主机操作系统、PLC、HMI、工作站等。

<br>

**SCADA渗透测试列表**

出厂默认设置是否修改

是否设置了访问PLC的白名单

SCADA网络与其他网络是否隔离

是否可以通过物理方式访问SCADA控制中心

控制机器是否可以访问互联网

SCADA的网络传输是否是明文形式

组织是否遵循严格的密码策略

控制器、工作站以及服务器是否打了最新补丁

是否运行有防病毒软件并且设置应用程序白名单

<br>

**工具列表**

smod（https://github.com/enddo/smod）：Modbus渗透测试框架

plcscan（https://github.com/yanlinlin82/plcscan）：扫描PLC的Python脚本

NMAP Scripts（https://nmap.org/book/man-nse.html）：扫描PLC的nmap脚本

Wireshark（https://www.wireshark.org/）：网络嗅探器

mbtget（https://github.com/sourceperl/mbtget）：读取PLC的Perl脚本

plcinject（https://github.com/SCADACS/PLCinject）：向PLC注入代码的工具

参考工具列表（https://github.com/hslatman/awesome-industrial-control-system-security）


