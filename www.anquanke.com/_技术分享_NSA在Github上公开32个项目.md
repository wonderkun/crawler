> 原文链接: https://www.anquanke.com//post/id/86306 


# 【技术分享】NSA在Github上公开32个项目


                                阅读量   
                                **131485**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：nationalsecurityagency.github.io
                                <br>原文地址：[https://nationalsecurityagency.github.io/](https://nationalsecurityagency.github.io/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t010e58dad55e697fee.png)](https://p1.ssl.qhimg.com/t010e58dad55e697fee.png)

下面所谈到的技术都是**美国国家安全局（NSA）**开发的，现以开源软件的方式向公众公开。NSA 技术转化计划（TTP）希望与通过合作的方式与有创新的机构将他们的技术转化到商业市场。开源软件（OSS）通过协作的方式进行技术开发。鼓励大家使用和采用相关项目。通过采用，改进或者商业化软件等方式，使公众受益。政府也会受益于开源社区对技术的改进。

NSA的官方github账号：

[https://github.com/nationalsecurityagency](https://github.com/nationalsecurityagency)

负责NSA信息保障任务：

[https://github.com/nationalsecurityagency](https://github.com/nationalsecurityagency) 

**<br>**

**项目介绍**

****

**APACHE ACCUMULO**

[https://accumulo.apache.org/](https://accumulo.apache.org/)

一种经过分类的分布式密钥/值存储项目，提供强大的，可扩展的数据存储和检索。它添加了基于单元的访问控制和服务器端编程机制，可以在数据管理过程中的各个点修改键/值对。

**CASA**

[https://github.com/iadgov/certificate-authority-situational-awareness](https://github.com/iadgov/certificate-authority-situational-awareness)

在Windows系统上标识意外和禁止的证书颁发机构。

**CONTROL FLOW INTEGRITY RESEARCH（控制流程完整性研究）**

[https://github.com/iadgov/control-flow-integrity](https://github.com/iadgov/control-flow-integrity)

一种提出的基于硬件的方法，用于阻止在“IT生态系统的硬件控制流完整性”研究论文中描述的已知的内存损坏利用技术。

**DCP**

[https://github.com/nationalsecurityagency/dcp](https://github.com/nationalsecurityagency/dcp)

一个用于减少为了法庭取证分析进行复制硬件驱动器所需时间的程序。

**EOWS**

一个启用Web的原型工具，实现了开放式清单交互语言（OCIL）功能。它主要用于创建，管理和答复调查问卷。

**FEMTO**

[https://github.com/femto-dev/femto](https://github.com/femto-dev/femto)

一个用于对字节序列进行查询的索引和搜索系统。它可以对任意格式的数据提供轻量快速搜索。

**GOSECURE**

[https://github.com/iadgov/gosecure](https://github.com/iadgov/gosecure)

一个在Linux和Raspberry Pi 3上安装的易于使用和便携式的虚拟专用网络系统。

**GRASSMARLIN**

[https://github.com/iadgov/grassmarlin](https://github.com/iadgov/grassmarlin)

提供工业控制系统（ICS）、数据采集与监视控制（SCADA）网络的态势感知确保网络安全。

**JAVA PATHFINDER MANGO (JPF-MANGO)**

[https://babelfish.arc.nasa.gov/trac/jpf/wiki/projects/jpf-mango](https://babelfish.arc.nasa.gov/trac/jpf/wiki/projects/jpf-mango)

一种使用“formal ”方法进行分析的静态代码分析工具。它是NASA Ames Java PathFinder项目的一部分，该项目是一个用于验证可执行Java字节码的系统。

**LEMONGRAPH/LEMONGRENADE**

[https://github.com/nationalsecurityagency/lemongraph](https://github.com/nationalsecurityagency/lemongraph)

[https://github.com/nationalsecurityagency/lemongrenade](https://github.com/nationalsecurityagency/lemongrenade)

基于日志的事务图数据库引擎由单个文件支持。主要用例是支持流种子集扩展，迭代相关和递归文件处理。

**LOCKLEVEL**

[https://github.com/iadgov/locklevel](https://github.com/iadgov/locklevel)

一个快速构建的原型，演示了一种评估Windows系统如何实现前10个信息保障缓解策略的一些方法。

**MAPLESYRUP**

[https://github.com/iadgov/maplesyrup](https://github.com/iadgov/maplesyrup)

通过检查处理器的系统寄存器接口来评估基于ARM的设备的安全状态。

**APACHE NIFI**

自动化系统之间的数据流。NiFi实现了基于流程编程的概念，解决了企业面临的常见数据流问题。

[https://nifi.apache.org/](https://nifi.apache.org/)

**ONOP**

一个用于网络监控，配置，部署和操作的开源平台。通过在OpenFlow的网络控制器上的SDN应用程序，大大简化了企业网络的操作。

[https://github.com/onop](https://github.com/onop)

**OPAL**

管理和标准化现有的商用硬盘

**OpenAttestation 开放认证系统**

[https://github.com/openattestation/openattestation](https://github.com/openattestation/openattestation)

通过建立系统的可信平台模块（TPM）的基线测量并监控该测量中的变化来验证系统的完整性。 最初是基于NSA的启动主机完整性（HIS）软件。

该项目提供一个云管理工具SDK源码和二进制文件

主要功能包括: 对主流Linux主机操作系统的支持, 基于PCR的报告模式和策略规则,基于RESTful的Query API, 参考门户网站/ GUI实现, 历史PCR数据跟踪/比较, 白名单管理, 认证服务器的灵活访问控制支持tomcat 2-way SSL/TLS的Query APIs,为ISVs通过HOOK实现自定义访问控制, 资产标签, SAML报告, 使用资产标记Open Stack扩展

**OZONE Widget Framework (OWF)**

[https://github.com/ozoneplatform/owf-framework](https://github.com/ozoneplatform/owf-framework)

小部件框架（OWF）是一种框架，允许来自不同服务器的数据在浏览器窗口内进行通信，而不会将信息发送回相应的服务器. 这种独特的功能允许OWF web平台提供分布式数据处理.它包含一个安全的,  in-browser ，pub-sub事件系统允许部件来自不同域的信息共享。集合分散的内容和in-browser消息.这使得OWF特别适合于需要组合能力的传统大型分布式enterprises, 用它快速链接应用程序并制作整合工具。

**APACHE PIRK**

[https://incubator.apache.org/projects/pirk.html](https://incubator.apache.org/projects/pirk.html)

允许用户私下和安全地从他们访问的数据集中获取信息，而不向数据集所有者或观察者透露关于所查询的问题或所获得结果的任何信息。

**PRESSUREWAVE**

Couples corporate对象存储功能，具有灵活的策略语言，用于在同一系统中定制访问控制、保留和存储数据。

**REDHAWK**

[https://github.com/redhawksdr](https://github.com/redhawksdr)

软件定义无线电（SDR）框架旨在支持实时软件无线电应用的开发，部署和管理。 

**SAMI**

[https://github.com/iadgov/splunk-assessment-of-mitigation-implementations](https://github.com/iadgov/splunk-assessment-of-mitigation-implementations)

测量在Windows系统上部署前10个IA缓解策略的具体评级。

**SCAP SECURITY GUIDE (SSG)**

[https://fedorahosted.org/scap-security-guide](https://fedorahosted.org/scap-security-guide)

使用安全内容自动化协议（SCAP）提供安全指导，基准和相关的验证机制，以增强红帽产品。

**SECURE HOST BASELINE (SHB)**

[https://github.com/iadgov/secure-host-baseline](https://github.com/iadgov/secure-host-baseline)

组策略对象，配置文件，合规性检查 和 支持Windows 10 实现DoD Secure Host Baseline(国防部安全基线)的脚本。

**SECURITY-ENHANCED LINUX (SELINUX)**

[https://github.com/SELinuxProject](https://github.com/SELinuxProject)

检查在标准自由访问控制之后,检查允许的操作的Linux内核中的强制访问控制机制。 它可以根据定义的策略对Linux系统中的文件和进程及其执行的操作 执行规则。 SELinux自2.6.0版以来一直是Linux内核的一部分。

**SECURITY ENHANCEMENTS FOR ANDROID (SE ANDROID)**

[https://source.android.com/security/selinux](https://source.android.com/security/selinux)

通过对所有Android进程执行强制访问控制来限制基于安全策略的特权进程。SE Android已经是Android 4.3的一部分。

**SIMON AND SPECK**

[https://github.com/iadgov/simon-speck](https://github.com/iadgov/simon-speck)

轻量级的分组密码:Simon和Speck家族

**SYSTEM INTEGRITY MANAGEMENT PLATFORM (SIMP)**

[https://github.com/nationalsecurityagency/simp](https://github.com/nationalsecurityagency/simp)

自动化系统的系统配置和LINUX合规性操作，因此，它们符合行业最佳实践。

**TIMELY**

[https://github.com/nationalsecurityagency/timely](https://github.com/nationalsecurityagency/timely)

提供对Accumulo中存储的时间序列数据的安全访问。

**UNFETTER**

[https://github.com/iadgov/unfetter/](https://github.com/iadgov/unfetter/)

为网络维护者，安全专业人员和决策者提供一个定量测量其安全状态有效性的机制。

**WALKOFF **

[https://github.com/iadgov/walkoff](https://github.com/iadgov/walkoff)

一个活跃网络防御开发框架，使用者编写一次，然后支持部署在启用WALKOFF的业务流程工具中。

**WATERSLIDE**

[https://github.com/waterslidelts/waterslide](https://github.com/waterslidelts/waterslide)

用于处理元数据的体系结构，其设计用于从多个源接收一组流事件，通过一组模块进行处理，并返回有价值的输出。

**WELM**

检索Windows事件日志消息中嵌入操作系统的二进制文件的定义。


