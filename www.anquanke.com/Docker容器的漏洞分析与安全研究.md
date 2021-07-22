> 原文链接: https://www.anquanke.com//post/id/229487 


# Docker容器的漏洞分析与安全研究


                                阅读量   
                                **112333**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ieee，文章来源：ieeexplore.ieee.org
                                <br>原文地址：[https://ieeexplore.ieee.org/document/9236837﻿](https://ieeexplore.ieee.org/document/9236837%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01e248229f23f4b2e8.jpg)](https://p5.ssl.qhimg.com/t01e248229f23f4b2e8.jpg)



## 摘要

Docker是一个开源的应用容器引擎，它可以让用户将应用打包，并依赖包到可移植的容器中。然而，Docker也存在着安全问题。本文从文件系统隔离、进程和通信隔离、设备管理和主机资源约束、网络隔离和镜像传输等四个方面入手，对Docker的漏洞进行分析。与Linux内核的安全模块进行交互，采取积极有效的措施来提高Docker的安全性。本文介绍了当前Docker安全研究的概况，探讨和展望了Docker安全研究的发展趋势，为Docker在生产中更好的应用奠定了良好的基础。



## 第一节.Docker简介

云计算能够提供灵活机动的服务，具有快速部署和可移植的特点，在当今计算领域占据了大部分的市场份额[1]。其中，资源虚拟化技术[2]在实现云计算基础设施服务的按需分配方面发挥了重要作用。传统的Vmware、Xen、KVM和Microsoft Hyper -v等硬件层面的虚拟化，必须通过虚拟一个完整的操作系统层来降低资源利用率。为了寻找更高效的隔离技术替代，Docker在2013年3月推出了一些开源容器项目Docker[3]。为了寻找更高效的隔离技术替代方案，Docker已经成功地在各种场景中得到了广泛的应用。它的广泛应用使得对Docker安全的研究更加迫切和实用。

Docker[3]是一个开源引擎。Docker，可以自动将开发应用部署到容器中。在虚拟化的容器执行环境中，增加了一个应用部署引擎。该引擎的目标是提供一个轻量级、快速的环境，可以运行开发者的程序，并将程序从开发者的笔记本上方便、高效地部署到测试环境中。然后部署到生产环境中。

A. Docker主机的漏洞分析

Docker使用客户端服务器（client-server）模式。Docker客户端与Docker守护进程通信，Docker守护进程处理复杂繁重的任务，如构建、运行、发布Docker容器。Docker客户端和守护进程可以运行在同一个系统上。你也可以使用Docker客户端来连接远程Docker守护进程。Docker客户端和守护进程通过socket或RESTful API进行通信[4]。Docker Client作为通信客户端与Docker Daemon daemon进行通信，从而管理Docker。

Docker模式如图1所示。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9236788/9236789/9236837/9236837-fig-1-source-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9236788/9236789/9236837/9236837-fig-1-source-large.gif)

Fig.1.Docker schema diagram. – Docker模式图

B. Docker远程API和Dockerswarm

Docker Remote API[5]是代替rcli（远程命令行接口）的REST API，帮助发送请求、获取和发送数据、检索信息。

Swarm是Docker在2014年12月初推出的一个比较简单的工具，用于管理Docker集群。Swarm将一组Docker主机[6]转化为一个单一的虚拟主机。Swarm采用标准的Docker API接口作为其前端访问入口，即各种形式的Docker Client(Docker,Docker),Docker等都可以直接与Swarm通信，Swarm的结构图如图2所示。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9236788/9236789/9236837/9236837-fig-2-source-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9236788/9236789/9236837/9236837-fig-2-source-large.gif)

图2.Swarm的结构图 swarm的结构图



## 第二部分.Docker漏洞分析

Docker的漏洞主要体现在文件系统隔离、进程与通信隔离、设备管理与主机资源限制、网络隔离和镜像传输四个方面。对Docker的漏洞进行研究，可以为寻找有针对性的安全加固措施提供依据。

A. 文件系统隔离

Docker中隔离文件功能的实现是基于Mount命名空间的。不同的文件[7]存放在不同的命名空间中，以避免文件结构之间的交互。但容器中的root权限与主机root用户的权限相似，特别是当主机中安装了RW mount，且容器具有root权限时，容器中的root权限就更大了。一旦容器执行 “Chmod a +s[程序文件]”，运行程序的用户就可以获得root权限，从而大大增加了相关信息泄露的概率。

B. 远程隔离和通信隔离

Docker使用PID命名空间[8]来隔离进程，分离进程的PID. 有一个单独的计数程序。系统内核通过树来实现PID命名空间的维护，其中根命名空间处于顶层，父节点可以获取子节点信息，但子节点无法获取父节点信息。但需要明确的是：当其为1时，PID被终止，导致容器完全停止，拒绝服务。

C. 设备管理和主机资源约束

Docker容器中域名和主机名的隔离是通过UTS命名空间实现的，而Cgroups[9]是用来限制资源的使用。但默认情况下是封闭的，容易增加设备资源、网络带宽和内存空间的耗尽概率。另外，考虑到用户可以在容器中获取资源，用户定义代码没有得到适当限制。会造成主机拒绝服务，特别是在使用SaaS、PaaS、IaaS时，应引起足够重视，防止拒绝服务的发生。

D. 网络隔离和图像传输

Docker中的网络命名空间负责隔离网络资源，如IP路由表、TCP/IP协议、网络设备的隔离等。但默认情况下，Docker为容器指定IP和网络命名空间，然后用网桥连接。这种方式是只转发流量，不进行过滤，将面临较大的MAC Flooding风险。镜像传输时，Docker不会检查拉回的镜像。如果更换了一些数据，可能会出现中间人攻击。



## 第三节 Docker和内核安全系统

一些内核安全系统的存在可以用来增强Docker和内核的安全性，包括Linux函数[10]和Linux安全模块（LSM）。Linux函数限制了分配给每个进程的权限。LSM提供了一个框架，允许Linux内核支持不同的安全模型。LSM已被集成到Linux官方内核中，包括AppArmor、SELinux和AppArmor。

A. Linux功能

Docker容器运行在与主机系统共享的内核上，因此大多数任务都可以由主机处理。因此，在大多数情况下，没有必要为容器提供完整的root权限。因此，删除容器中的一些根功能，既不会影响容器的可用性和功能，又能有效提高系统的安全性。例如，可以从容器中删除CAP_来修改系统的网络功能。由于Docker在启动容器之前，所有的网络配置都可以由Docker守护进程来处理，因此，Docker在启动容器之前，可以将.NET_ADMIN功能删除。

Docker允许配置可以被容器使用的函数。默认情况下，即使入侵者获得了容器中的root访问权限，Docker也可以禁止其容器中的大量Linux函数，以防止入侵者破坏主机系统。一些被Docker禁用的功能。Docker容器的功能如TABLE I所示，可以在Linux手册页面中找到。

表一 被docker容器禁用的部分功能

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9236788/9236789/9236837/9236837-table-1-source-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9236788/9236789/9236837/9236837-table-1-source-large.gif)

B. Apparmor

AppArmor[11]也是一种基于强制访问控制的Linux安全增强模型（如SELinux），但它将范围限制在单个程序上。它允许管理员在每个程序中加载安全配置文件，从而限制了程序的功能。

在启用AppArmor的系统上，Docker提供了一个接口，可以在启动新容器时加载预定义的AppArmor配置文件。配置文件将以强制模式加载到容器中，以确保容器中的进程受到配置文件的限制。如果管理员在启动容器时没有指定配置文件，Docker守护进程会自动将默认的配置文件加载到容器中，这样会拒绝访问主机上的重要文件系统，如Isys/fs/cgroups/和/sys/kerne/security/。

C. 能力机制

能力机制使Linux的权限划分更加细化，改变了以往root用户所有权限的现象。能力机制将权限细分为37种不同的能力，涵盖了文档、进程、网络、系统、设备等操作权限。Docker在沉默识别的条件下，为容器提供有限的能力。用户也可以根据实际需求，在运行时增加或减少能力权限。能力机制存在的问题是，在某些方面分权还是不够，不能很好的满足容器限制的要求，CAP _ SYS _ADMIN涵盖了很多权限，需要进一步细分。在为容器分配权限时，很难知道容器中需要哪些权限。为此，Docker提供的默认能力权限列表包含的范围更广。从安全的角度来看，这不是一个好的策略。

D. Seccomp

Seccomp[12]可以限制用户进程的系统调用，过滤系统调用参数。系统调用是用户状态和内核状态之间最重要的接口。通过对其进行限制，可以在很大程度上保证进程在安全可控的范围内运行。Docker默认采用的是白名单机制，通过Seccomp配置文件来指定哪些系统调用是允许的，超过50个系统就会被屏蔽。在特定的参数下也会屏蔽一些系统调用。在配置文件下，大部分容器可以正常运行。

E. 强制准入控制

与自由裁量访问控制(DAC)相比，强制访问控制可以提供更严格的保护[13]。由于用户不能改变自己的安全等级和对象的安全属性，只能根据预先定义的用户和数据安全等级匹配结果，通过MAC进行客观具体的决策。这样一来，可以屏蔽用户的主观因素，更好地保护系统的安全。在Linux系统中，强制访问控制通常与DAC配合使用，具体的安全模块是在LSM（Linux安全模块）的框架下实现的。目前已经实现并并入内核主线的安全模块有SELinux、AppArmor、Yama、SMACK和Tomoyo。这些安全模块可以为Docker容器提供增强的安全保护。除了Yama之外，模块之间也会有相互排斥的情况。一般情况下，会根据Linux的不同发行版选择不同的安全模块。Debain系列通常使用自己的AppArmor，Redhat系列则发布SELinux安全模块。

SELinux的主要问题是操作太复杂。开发者和实际生产部门抵制使用SELinux，与BTRFS驱动不兼容。AppArmor的独特之处在于它不关注整个系统的安全性，只对指定的进程进行强制访问控制。其他进程都是在不受控制的状态下工作。LiCShield安全框架是用来整合Linux容器的。该框架通过跟踪和分析容器所需的权限，自动生成AppArmor配置文件，以保证容器的安全可控运行。除了这些安全模块外，用户还可以根据LSM框架设计更多合适的安全模块。

F. 网络框架

在Linux内核中，有一些网络框架可以用来解决Docker的网络安全问题，其中包括Netfilter[14]框架和TC（tracfic controller）框架。其中包括Netfilter[14]框架和TC（tracfic controller）框架。Netfilter，侧重于防火墙数据过滤，而TC侧重于流量带宽控制。Docker可以通过修改配置文件启用Iptable防火墙，配置防火墙策略来控制容器之间的通信。TC可以通过TC限制主机上虚拟网络接口的流量，或者用Cgroups子系统对网络数据包进行标记，利用TC中的分类队列限制容器的流量，从而有效防止独占网络带宽型拒绝服务攻击。

G、完整性保护

Linux内核中的完整性保护技术可以很好地应用到Docker中，保证镜像和容器运行的完整性。涉及的技术包括可信计算开放标准（Trusted Computing Group，TCG）在Linux的一些模块中实现完整性检查功能的dm-verity子模块和Device Mapper。这些技术可以用来实现Docker镜像的完整性保护。

H. 日志审计

Docker虽然在日志可视化审计方面有比较系统的实施方案，但在大规模日志数据挖掘和自动分析方面还有待进一步研究。在运行环境审计方面，可以参考Docker公司和CIS（互联网安全中心）制定的安全评估文档，其具体的评估实现工具是Docker bench for security。

I. 安全威胁检测

在针对Docker的安全威胁检测方面，虽然可以采用传统的基于主机的威胁检测和基于数据流的威胁检测技术，但仍需要结合Docker的特点进一步加强应用。本方法属于将传统的主机威胁检测技术应用于Docker特定环境的一个实例。

J. 精简作业系统

从另一个角度来看，关于Docker的安全问题，有很多研究。例如，为了提供更安全的容器运行环境，提出了一批精简的操作系统项目，包括CoreOS、Ubuntu Core，这些项目更适合容器运行。其中提出了全新的轻量级架构方案，借助定制化的内核，让应用直接运行在裸机上，不再相互共享内核系统。代表方案有Unikernels等。Catuogno对Docker环境下CCRA(common criteria recognition arrangement)提出的容器安全标准模型和Reshetova等安全模型进行了对比和比较，指出了两种安全模型在本质上的等同性。Sharath N等介绍了如何利用Stackelberg模型，通过线性编程的方法，找到一个既能兼顾Docker安全又能保证运行效率的最佳组合点。

K. 其他相关安全加固措施

Docker虽然在日志可视化审计方面有较为系统的实施方案，但在大规模日志数据挖掘和自动分析方面还有待进一步研究。在运行环境审计方面，可以参考Docker公司与CIS(互联网安全中心)制定的安全评估文档，其具体的评估实施工具为Docker bench for security。

在Docker的安全威胁检测方面，虽然可以采用传统的基于主机的威胁检测和基于数据流的威胁检测技术，但如何结合Docker自身的特点进行针对性的应用，还需要进一步加强。Abed A S等详细介绍了如何通过系统调用来检测Docker进程，并对定义的调用频率进行集群分析。该方法属于将传统的主机威胁检测技术应用到Docker特定环境中的一个例子。

从不同的角度来看，对于Docker的安全问题，有很多研究。例如，为了提供更安全的容器运行环境，开发了一批精简的操作系统项目，包括CoreOS、Ubuntu Core，这些项目更适合容器运行。提出了全新的轻量级架构方案，借助定制化的内核，让应用直接运行在裸机上，不再相互共享内核系统。代表方案有Unikernels等。Catuogno对Docker环境下CCRA(Common Criteria Recognition Arrangement)[15]提出的容器安全标准模型和Reshetova等安全模型进行了对比和比较，指出了两种安全模型在本质上的等同性。Sharath N等人介绍了如何利用Stackelberg模型(Stackelberg Model)通过线性编程来寻找Docker安全和运行效率的最佳组合。



## 第四节. 结论

随着容器应用的日益普及，越来越多的敏感应用将被迁移到容器上。如何在提供便捷部署和高资源利用率的同时，提升容器的安全性将成为人们越来越关注的问题。首先，本文简单介绍了Docker的主要结构，然后梳理了Docker的漏洞。指出它主要体现在文件系统隔离、进程与通信隔离、设备管理与主机资源限制、网络隔离和镜像传输四个方面。然后，对Docker和内核安全体系进行了总结，并对目前Docker的安全研究措施进行了总结。与传统虚拟技术相比，Docker容器的安全性还有待提高。这两种容器不是相对的。在同样的虚拟隔离效果下，它们也起到了互补的作用。尝试补齐Docker安全的短板，将充分发挥Docker在虚拟容器中的优势。



## 引用

1.T. Bui “Analysis of Docker Security[J]” Computer ence 2015.

2.T Combe A Martin and R D. Pietro “To Docker or Not to Docker: A Security Perspective[J]” Cloud Computing IEEE vol. 3 no. 5 pp. 54-62 2016.

3.A R Manu Jitendra Kumar Patel and Shakil Akhtar “A study analysis and deep dive on cloud PAAS security in terms of Docker container security[C]//“ International Conference on Circuit 2016.

4.Holger Gantikow Christoph Reich and Martin Knahl “Providing Security in Container-Based HPC Runtime Environments [C]//“ International Conference on High Performance Computing 2016.

5.Yasrab R. Mitigating Docker Security Issues[J] 2018.

6.S Garg and S. Garg “Automated Cloud Infrastructure Continuous Integration and Continuous Delivery using Docker with Robust Container Security[C]//“ Automated Cloud Infrastructure Continuous Integration &amp; Continuous Delivery Using Docker with Robust Container Security 2019.

7.D Sever and T. Kisasondi “Efficiency and security of docker based honeypot systems[C]//“ International Convention on Information &amp; Communication Technology Electronics &amp; Microelectronics 2018.

8.L I Fuling and H E. Haoxian “Implementation of online evaluation system security based on Docker[J]” Journal of North China Institute of Science and Technology 2018.

9.L I Chun-Lin L Zheng-Jun W Ye et al. “ModifiedConstruction Method of Docker-based Network Security Experimental Platform[J]” Communications Technology 2019.

10.Fotis LoukidisAndreou Ioannis Giannakopoulos and Katerina Doka “Docker-Sec: A Fully Automated Container Security Enhancement Mechanism[C]//“ Ieee International Conference on Distributed Computing Systems 2018.

11.A Zerouali T Mens G Robles et al. On The Relation Between Outdated Docker Containers Severity Vulnerabilities and Bugs[J] 2018.

12.Chin – Wei Tien Tse – Yung Huang Chia – Wei Tien et al. “KubAnomaly: Anomaly detection for the Docker orchestration platform with neural network approaches[J]” Engineering Reports vol. 1 no. 5 2019.

13.A Martin S Raponi T Combe et al. “Docker ecosystem – Vulnerability Analysis[J]” Computer Communications pp. 30-43 2018.

14.J Xiang and L. Chen “[ACM Press the 2nd International Conference – Guiyang China (2018.03.16–2018.03.19)]” Proceedings of the 2nd International Conference on Cryptography Security and Privacy – ICCSP 2018 – A Method of Docker Container Forensics Based on API[J] pp. 159-164 2018.

15.M P Amith Raj A Kumar S J Pai et al. “Enhancing security of Docker using Linux hardening techniques [C]//“ International Conference on Applied &amp; Theoretical Computing &amp; Communication Technology 2016.

16.Fathollah Bistouni and Mohsen Jahanshahi “Evaluation of Reliability in Component-Based System Using Architecture Topology” Journal of the Institute of Electronics and Computer vol. 2 pp. 57-71 2020.
