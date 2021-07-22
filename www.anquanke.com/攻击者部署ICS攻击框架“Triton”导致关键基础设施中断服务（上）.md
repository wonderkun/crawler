> 原文链接: https://www.anquanke.com//post/id/91002 


# 攻击者部署ICS攻击框架“Triton”导致关键基础设施中断服务（上）


                                阅读量   
                                **90491**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Blake Johnson, Dan Caban, Marina Krotofil, Dan Scali, Nathan Brubaker, Christopher Glyer，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html](https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/dm/1024_672_/t01bd2ebd861a9d7ba5.jpg)](https://p4.ssl.qhimg.com/dm/1024_672_/t01bd2ebd861a9d7ba5.jpg)

> 本文是Fireeye针对一次工业安全系统攻击事件的分析，本文是该文章的上半部分，主要介绍了事件摘要、溯源以及过程控制。

## 传送门

[攻击者部署ICS攻击框架“Triton”导致关键基础设施中断服务（下）](https://www.anquanke.com/post/id/90992)



## 一、前言

Mandiant最近参与了一次应急响应事件，在这次攻击事件中，攻击者在某个关键的基础设施组织中部署了恶意软件，目标是操控工业安全系统。被攻击的目标系统提供紧急关闭功能，可以在紧急状态下处置工业生产流程。经过适当评估后，我们认为攻击者正在研发能够造成物理损坏以及随时关闭正常服务的功能。我们将这款恶意软件称之为TRITON，这是一个攻击框架，可以与Triconex安全仪表系统（Safety Instrumented System，SIS）控制器交互。虽然我们并没有将此次攻击事件追踪溯源到具体的某个攻击者，但我们认为此次行动与国家级的攻击准备行为脱不开关系。

现在市面上只有少数几款恶意软件家族专门针对[工业控制系统（industrial control systems，ICS）](https://www.fireeye.com/solutions/industrial-systems-and-critical-infrastructure-security.html)，TRITON正是其中一员。比如，2010年出现了针对伊朗的[Stuxnet](https://www.fireeye.com/company/press-releases/2014/fireeye-reveals-rise-in-advanced-threat-activities-by-iranian-linked-ajax-security-team-in-post-stuxnet-era.html)恶意软件，2016年出现了针对乌克兰的Industroyer恶意软件（我们认为Industroyer的背后主导者为沙虫组织（Sandworm Team））。TRITON与这些攻击活动类似，因为它能阻止安全机制正常发挥作用，造成严重的物理损坏后果。

|恶意软件家族|主要模块|描述
|------
|TRITON|trilog.exe|利用libraries.zip的主执行程序
|TRITON|library.zip|自定义通信库，可以与Triconex控制器交互

表1. TRITON恶意软件



## 二、事件摘要

攻击者首先获得了SIS工程工作站（Engineering Workstation）的远程访问权限，然后部署了TRITON攻击框架对SIS控制器进行重新编程。在此次事件中，某些SIS控制器进入了故障安全状态，该状态会自动关闭正常工业流程，因此也促使相关人员开始调查整个事件。经调查发现，当冗余处理单元之间的程序代码无法通过检验检查过程时，SIS控制器就会启动安全关闭流程，生成MP诊断故障消息。

经过适当评估后，我们有一定的把握认为，这次攻击事件中，攻击者在开发物理损坏攻击能力时，不小心触发了关闭操作，之所以做出这个判断，原因主要包含如下几点：

1、修改SIS会导致其无法正常工作，增加异常工作状态的可能性，造成严重物理后果。

2、攻击者使用TRITON来修改生产环境中SIS控制器上应用程序的内存，这样可能导致无法通过校验检查。

3、故障出现时机与TRITON的活跃时机相符。

4、在此事件发生期间，单从现有状况或者外部条件来看不可能引起安全故障。



## 三、追踪溯源

[FireEye](https://www.fireeye.com/index.html)尚未将此次攻击事件与我们正在跟踪的任何攻击者联系在一起，然而，我们有一定的把握认为这次事件的主导者背后有国家力量的支持。这次攻击事件针对的是关键基础设施，攻击者发起的攻击活动持续周期较长，我们也很难找到攻击者开发这种攻击框架的金钱动力，更何况这种行为需要大量技术资源，种种因素都表明只有实力雄厚的国家才能支撑此次攻击活动。具体而言，我们的结论源自于如下几个事实：

攻击者的目标是SIS，这意味着攻击者希望通过影响力较高的攻击活动造成严重的物理损坏后果，以往的网络犯罪组织通常不具备这种攻击意图。

TRITON需要访问专用的硬件及软件环境，这些环境的使用范围并没有那么广泛，而攻击者在获得SIS系统的访问权限后不久就部署了TRITON，这表明他们之前已经生成并测试过这款工具。TRITON还可以使用专有的TriStation协议进行通信，而该协议并没有官方说明文档，这表明攻击者自己已经逆向分析过这个协议。

此次攻击的目标是扰乱、削弱或者摧毁关键基础设施的正常功能，这与俄罗斯、伊朗、朝鲜、美国和以色列在全球范围开展的国家级别的大量攻击和侦察活动一致。这类入侵行为不一定代表攻击者想立即摧毁目标系统，他们有可能只是在为应急情况做准备。



## 四、关于过程控制及安全仪表系统

[![](https://p4.ssl.qhimg.com/t015dff06f30687d9be.jpg)](https://p4.ssl.qhimg.com/t015dff06f30687d9be.jpg)

图1. ICS架构参考说明

现代的工业过程控制及机动化系统依赖于各种尖端控制系统及安全功能。行业中通常将这些系统及功能称之为[工业控制系统（Industrial Control Systems，ICS）](https://www.fireeye.com/solutions/industrial-systems-and-critical-infrastructure-security.html)或者运营技术（Operational Technology，OT）。

操作人员可以借助分布式控制系统（Distributed Control System，DCS）远程监视及控制工业流程。DCS是由计算机、软件应用程序以及控制器组成的计算机控制系统。工程工作站（Engineering Workstation）是用于配置、维护以及诊断控制系统应用程序以及其他控制系统设备的计算机。

SIS是独立的控制系统，可以独立监视工业流程的状态是否在可控范围内。如果工业流程超过了危险状态参数值，那么SIS就会尝试将该流程恢复到安全状态，或者会以安全方式自动关闭该流程。如果SIS以及DCS无法正常发挥作用，那么整套工业设施本身就是最后一道防线，其中包括设备使用的机械保护设施（如防爆片）、物理报警器、应急响应程序以及其他缓解危险情况的保护机制。

资产方会采用各种方法将工厂的DCS与SIS连接起来。传统的方法中有一个原则，那就是通信基础设施和控制策略需要相互隔离。在过去的十多年中，由于各种原因（比如成本降低、易用性提高以及DCS和SIS信息交互所带来的各种优势），越来越多的设计方案中会将DCS以及SIS集成在一起。这种设计方案允许DCS以及SIS网络主机之间能够双向通信，但也存在安全隐患，我们认为TRITON的出现正是这种安全隐患的典型代表。



## 五、技术分析

技术分析请持续关注安全客。
