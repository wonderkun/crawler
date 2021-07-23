> 原文链接: https://www.anquanke.com//post/id/164570 


# Oracle数据库勒索病毒RushQL死灰复燃


                                阅读量   
                                **248666**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01eb9daa5d9b5ab016.png)](https://p3.ssl.qhimg.com/t01eb9daa5d9b5ab016.png)

最近，360终端安全实验室陆续接到数起用户反馈，中了Oracle数据库勒索病毒，中毒后的数据库应用界面会弹出下方类似的异常信息：

[![](https://p3.ssl.qhimg.com/t0193c9b2067a84cf51.png)](https://p3.ssl.qhimg.com/t0193c9b2067a84cf51.png)

根据此信息，360终端安全实验室确认该病毒是RushQL数据库勒索病毒，是由于下载使用了破解版PL/SQL导致的。上面的告警声称，病毒是由“SQL RUSH Team”组织发起，因此该病毒被命名为RushQL。此病毒最早在2016年11月出现，期间沉寂了1年多，直到最近，360终端安全实验室又陆续接到数起企业、事业单位用户遭受到此病毒的袭击事件，该病毒突然呈现出死灰复燃之势。



## 技术分析

RushQL病毒样本是在客户现场提取的，该样本是一个PL/SQL自带的AfterConnect.sql自动运行脚本，此文件一般在官方PL/SQL软件中是一个空文件，而该样本提取自破解版PL/SQL是有实际内容的，如下图所示：

[![](https://p3.ssl.qhimg.com/t018e620d3fabaa96e6.png)](https://p3.ssl.qhimg.com/t018e620d3fabaa96e6.png)

此样本伪装成Oracle官方程序：

[![](https://p4.ssl.qhimg.com/t0127c32ce8a2e98370.png)](https://p4.ssl.qhimg.com/t0127c32ce8a2e98370.png)

脚本的关键代码，采用了 Oracle数据库专用代码加密工具wrap进行了加密：

[![](https://p5.ssl.qhimg.com/t01da4b4c4859c3c2a0.png)](https://p5.ssl.qhimg.com/t01da4b4c4859c3c2a0.png)

将该病毒脚本解密，其主要功能是创建4个存储过程和3个触发器，下面分别分析其功能。

PROCEDURE DBMS_SUPPORT_INTERNAL

[![](https://p0.ssl.qhimg.com/t0154232b3101b49348.png)](https://p0.ssl.qhimg.com/t0154232b3101b49348.png)

此存储过程主要功能是：

如果当前日期 – 数据库创建日期 &gt; 1200 天则：
1. 创建并备份sys.tab$表的数据到表 ORACHK || SUBSTR(SYS_GUID,10)；
1. 删除sys.tab$中的数据，条件是所有表的创建者ID 在（0,38）范围；
1. 循环2046次打印日志告警信息，并触发异常告警（见概述中的告警信息）；
PROCEDURE DBMS_STANDARD_FUN9

[![](https://p5.ssl.qhimg.com/t016adbd26a3998abe4.png)](https://p5.ssl.qhimg.com/t016adbd26a3998abe4.png)

此存储过程的主要功能是：

1、动态执行PL/SQL脚本；

PROCEDURE DBMS_SYSTEM_INTERNAL

[![](https://p2.ssl.qhimg.com/t01699208c598ee3a32.png)](https://p2.ssl.qhimg.com/t01699208c598ee3a32.png)

此存储过程主要功能是：

如果当前日期 – 数据表（不含SYSTEM, SYSAUX, EXAMPLE）的最小分析日期 &gt; 1200 天，且当前客户端程序进程名不是“C89238.EXE”（这个“C89238.EXE”推测是制作者搞了个KillSwtich，当收取赎金后，以这个进程名访问数据库将不会导致数据库进入异常，从而为恢复数据提供便利）则：
1. 触发告警信息（见概述中的告警信息）；
PROCEDURE DBMS_CORE_INTERNAL

[![](https://p4.ssl.qhimg.com/t0187f6f1b0903e7254.png)](https://p4.ssl.qhimg.com/t0187f6f1b0903e7254.png)

此存储过程主要功能是：

如果当前日期 – 数据表（不含SYSTEM, SYSAUX, EXAMPLE）的最小分析日期 &gt; 1200 天，则：
1. 删除所有名字不含“$”且名称不是 ORACHK || SUBSTR(SYS_GUID,10)的数据表；1. 如果当前客户端程序进程名不是“C89238.EXE”（这个“C89238.EXE”推测是制作者搞了个KillSwtich，当收取赎金后，以这个进程名访问数据库将不会导致数据库进入异常，从而为恢复数据提供便利）则触发告警信息（见概述中的告警信息）；
TRIGGER DBMS_SUPPORT_INTERNAL

[![](https://p4.ssl.qhimg.com/t010e02ae2554267b60.png)](https://p4.ssl.qhimg.com/t010e02ae2554267b60.png)

此触发器的主要功能是：
1. 在数据库启动时执行存储过程“DBMS_SUPPORT_INTERNAL”
TRIGGER DBMS_SYSTEM_INTERNAL

[![](https://p5.ssl.qhimg.com/t01cf0aa65ea891dcb1.png)](https://p5.ssl.qhimg.com/t01cf0aa65ea891dcb1.png)

此触发器的主要功能是：
1. 在登录数据库时执行存储过程“DBMS_SYSTEM_INTERNAL”
TRIGGER DBMS_CORE_INTERNAL

[![](https://p2.ssl.qhimg.com/t0125cd33f38f9cf47d.png)](https://p2.ssl.qhimg.com/t0125cd33f38f9cf47d.png)

此触发器的主要功能是：
1. 在登录数据库时执行存储过程“DBMS_CORE_INTERNAL”


## 解决方案

从技术分析知道，病毒会根据数据库创建时间、数据库的数据分析时间等因素来判断是否发作，因此会有一个潜伏期，潜伏期病毒不发作时是没有明显症状的，这时该如何自查是否感染这种病毒呢？其实病毒感染数据库主要是通过4个存储过程和3个触发器完成，也即判断是否存在如下存储过程和触发器即可知道是否感染了RushQL病毒：
- 存储过程 DBMS_SUPPORT_INTERNAL
- 存储过程 DBMS_STANDARD_FUN9
- 存储过程 DBMS_SYSTEM_INTERNA
- 存储过程 DBMS_CORE_INTERNAL
- 触发器 DBMS_SUPPORT_INTERNAL
- 触发器 DBMS_ SYSTEM _INTERNAL
- 触发器 DBMS_ CORE _INTERNAL
一旦不幸感染了这种病毒该如何处置？从技术分析知道，病毒删除数据是由存储过程DBMS_SUPPORT_INTERNAL 和 DBMS_CORE_INTERNAL来执行的，他们的执行条件分别是：
1. 当前日期 – 数据库创建日期 &gt; 1200 天
1. 当前日期 – 数据表（不含SYSTEM, SYSAUX, EXAMPLE）的最小分析日期 &gt; 1200 天
当以上条件不满足时，病毒不会触发删除数据的操作，此时删除以上4个存储过程和3个触发器即可。

如果前面的2个条件中任何一个满足，就会出现数据删除操作，下面给出应对措施：
1. （当前日期 – 数据库创建日期 &gt; 1200 天） 且 （当前日期 – 数据表（不含SYSTEM, SYSAUX, EXAMPLE）的最小分析日期 &lt;= 1200 天）
A.删除4个存储过程和3个触发器

B.使用备份把表恢复到truncate之前

C.使用ORACHK开头的表恢复tab$

D.使用DUL恢复（不一定能恢复所有的表，如truncate的空间已被使用）
1. （当前日期 – 数据库创建日期 &gt; 1200 天） 且 （当前日期 – 数据表（不含SYSTEM, SYSAUX, EXAMPLE）的最小分析日期 &gt; 1200 天）
A.删除4个存储过程和3个触发器

B.使用备份把表恢复到truncate之前

C.使用DUL恢复（不一定能恢复所有的表，如truncate的空间已被使用）



## 影响范围统计

下图是我们监控到的该病毒发展趋势：

[![](https://p0.ssl.qhimg.com/t01a3d9b87083be9e3b.png)](https://p0.ssl.qhimg.com/t01a3d9b87083be9e3b.png)

从图中可看到，此病毒在2018年6月开始出现复发趋势，到8月是个小高峰，这和我们接到的反馈次数是大致相符的。

我们还查询了此病毒索要赎金比特币地址交易量：

[![](https://p1.ssl.qhimg.com/t01b6bf7ab3c2421a1b.png)](https://p1.ssl.qhimg.com/t01b6bf7ab3c2421a1b.png)

可以看到，该地址比特币交易量为0 BTC，这说明没有任何受害者向病毒传播者支付赎金。



## 安全建议

本病毒追根溯源是由于用户缺乏软件安全意识，下载了破解版PL/SQL导致的，为此软件供应链安全应为人们所重视，360天擎推出的软件管家可解决此类问题。软件管家背后由专业的安全团队运作，帮助用户把好软件安全关，使得用户下载软件时不必担心软件来源是否安全，免去用户下载软件的不便。

[![](https://p2.ssl.qhimg.com/t014c039451590724ba.png)](https://p2.ssl.qhimg.com/t014c039451590724ba.png)

此外对没有中毒或者希望自查的用户，可以使用360天擎进行扫描排查，目前360天擎支持此病毒的检测和查杀，请将病毒库升级至2018-11-14以后版本（此版本未完全放量，部分用户可能需要延迟一段时间才能升级成功）。

[![](https://p4.ssl.qhimg.com/t018c94faa17ed842f4.png)](https://p4.ssl.qhimg.com/t018c94faa17ed842f4.png)



## 参考链接

[https://blogs.oracle.com/cnsupport_news/%E5%AF%B9%E6%95%B0%E6%8D%AE%E5%BA%93%E7%9A%84%E2%80%9C%E6%AF%94%E7%89%B9%E5%B8%81%E6%94%BB%E5%87%BB%E2%80%9D%E5%8F%8A%E9%98%B2%E6%8A%A4](https://blogs.oracle.com/cnsupport_news/%25E5%25AF%25B9%25E6%2595%25B0%25E6%258D%25AE%25E5%25BA%2593%25E7%259A%2584%25E2%2580%259C%25E6%25AF%2594%25E7%2589%25B9%25E5%25B8%2581%25E6%2594%25BB%25E5%2587%25BB%25E2%2580%259D%25E5%258F%258A%25E9%2598%25B2%25E6%258A%25A4)



## 关于360终端安全实验室

360终端安全实验室由多名经验丰富的恶意代码研究专家组成，重点着力于常见病毒、木马、蠕虫、勒索软件等恶意代码的原理分析和研究，致力为中国政企客户提供快速的恶意代码预警和处置服务，在曾经流行的WannaCry、Petya、Bad Rabbit的恶意代码处置过程中表现优异，受到政企客户的广泛好评。

依托360在互联网为13亿用户提供终端安全防护的经验积累，360终端安全实验室以360天擎新一代终端安全管理系统为依托，为客户提供简单有效的终端安全管理理念、完整的终端解决方案和定制化的安全服务，帮助广大政企客户解决内网安全与管理问题，保障政企终端安全。



## 关于360天擎新一代终端安全管理系统

360天擎新一代终端安全管理系统是360企业安全集团为解决政企机构终端安全问题而推出的一体化解决方案，是中国政企客户3300万终端的信赖之选。系统以功能一体化、平台一体化、数据一体化为设计理念，以安全防护为核心，以运维管控为重点，以可视化管理为支撑，以可靠服务为保障，能够帮助政企客户构建终端防病毒、入侵防御、安全管理、软件分发、补丁管理、安全U盘、服务器加固、安全准入、非法外联、运维管控、主机审计、移动设备管理、资产发现、身份认证、数据加密、数据防泄露等十六大基础安全能力，帮助政企客户构建终端威胁检测、终端威胁响应、终端威胁鉴定等高级威胁对抗能力，为政企客户提供安全规划、战略分析和安全决策等终端安全治理能力。

[![](https://p3.ssl.qhimg.com/t0162de226c86b2fa2c.png)](https://p3.ssl.qhimg.com/t0162de226c86b2fa2c.png)
