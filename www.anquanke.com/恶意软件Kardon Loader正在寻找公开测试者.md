> 原文链接: https://www.anquanke.com//post/id/149544 


# 恶意软件Kardon Loader正在寻找公开测试者


                                阅读量   
                                **87006**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t014753ddebda811a1a.jpg)](https://p5.ssl.qhimg.com/t014753ddebda811a1a.jpg)

 

## 主要发现

<!-- [if !supportLists]-->l  <!--[endif]-->ASERT的研究人员发现Kardon Loader在地下论坛被广告宣传；

<!-- [if !supportLists]-->l  <!--[endif]-->Kardon Loader的功能特点是允许客户开设自己的僵尸商店（botshop），使得购买者有能力重建bot并出售给其他人；

<!-- [if !supportLists]-->l  <!--[endif]-->Kardon Loader目前处于开发初期阶段，公开测试阶段；

<!-- [if !supportLists]-->l  <!--[endif]-->合并了大量的反分析检查以阻止分析。

[![](https://p2.ssl.qhimg.com/t01b2dd07859921f89e.png)](https://p2.ssl.qhimg.com/t01b2dd07859921f89e.png) 图1：Kardon Loader的广告



## 概要

Kardon Loader是一款在地下论坛上作为付费公开测试版本进行广告宣传的恶意软件下载器（downloader），这个恶意软件已经被一个用户名为Yattaze的用户出售。从四月下旬开始，该恶意行为者将恶意软件作为一个独立版本销售，并为每次额外的重新构建或建立一个botshop的能力收费。在这种情况下，任何客户都可以建立自己的经营网络，进一步出售获得一个新的客户基础。

恶意软件作者和分销商利用下载器恶意软件和botshop来构建恶意软件分发网络。恶意软件分发网络通常被网络犯罪分子用来创建僵尸网络，以分发额外的有效载荷，如凭证盗取恶意软件、勒索软件、银行木马等。这些分发网络通常由第三方运营商运营，并在地下市场作为服务提供。



## 历史

2018年4月21日，威胁参与者Yattaze开始宣传一款名为Kardon Loader的下载器公开测试版，售价50美元。恶意软件家族的描述表明，该恶意软件由ZeroCool僵尸网络重命名而来，该僵尸网络之前是由同一威胁参与者开发的。这位威胁参与者自2017年4月起就在论坛上注册了账号，并获得了对该产品的多个担保。这个Loader的广告有专业的外观与自己的logo （图1和图2）。

[![](https://p0.ssl.qhimg.com/t01565449b60b9fa02d.png)](https://p0.ssl.qhimg.com/t01565449b60b9fa02d.png)图2：Kardon Loader的定价

威胁参与者提供了一份声明，声明不应将此软件用于恶意目的（图3）。

[![](https://p0.ssl.qhimg.com/t01e6bc8cdba122a824.png)](https://p0.ssl.qhimg.com/t01e6bc8cdba122a824.png)图3：Kardon Loader的免责声明

此外，威胁参与者上传了一个YouTube视频，用于演示管理面板的功能（图4）。

[![](https://p2.ssl.qhimg.com/t01548cb91bc2f9b569.png)](https://p2.ssl.qhimg.com/t01548cb91bc2f9b569.png)图4：Kardon Loader YouTube演示（[https://youtu.be/8m1BOoHtcNo](https://youtu.be/8m1BOoHtcNo)）



## 分发

从论坛帖子中获得的评论表明，这位威胁参与者最初是利用一个著名的botshop “Pink Panther’s automated loads shop (Pink)”进行测试的。来自威胁参与者的评论显示，这个bot目前还没有广泛分发。在威胁参与者发布的Loader测试网络的屏幕截图中，只有124个感染显示（图5）。 [![](https://p3.ssl.qhimg.com/t0170a7b0a331d79281.png)](https://p3.ssl.qhimg.com/t0170a7b0a331d79281.png)

图5：Kardon Loader管理面板显示感染情况



## 分析

威胁参与者声称Kardon Loader提供或即将提供以下功能：

<!-- [if !supportLists]-->l  <!--[endif]-->Bot功能

<!-- [if !supportLists]-->l  <!--[endif]-->下载并执行任务

<!-- [if !supportLists]-->l  <!--[endif]-->更新任务

<!-- [if !supportLists]-->l  <!--[endif]-->卸载任务

<!-- [if !supportLists]-->l  <!--[endif]-->用户模式 Rootkit

<!-- [if !supportLists]-->l  <!--[endif]-->RC4加密（尚未实施）

<!-- [if !supportLists]-->l  <!--[endif]-->调试和分析保护

<!-- [if !supportLists]-->l  <!--[endif]-->TOR支持

<!-- [if !supportLists]-->l  <!--[endif]-->域名生成算法（DGA）

ASERT发现许多功能在所审查的样本中是不存在的。分析的所有样本都使用硬编码的命令和控制（C2）URL，而不是DGA。在二进制文件中也没有TOR或用户模式rootkit功能的证据。



## 反分析技术

Kardon Loader使用了一些反分析技术，例如试图获取以下DLL的模块句柄：

<!-- [if !supportLists]-->l  <!--[endif]-->avghookx.dll

<!-- [if !supportLists]-->l  <!--[endif]-->avghooka.dll

<!-- [if !supportLists]-->l  <!--[endif]-->snxhk.dll

<!-- [if !supportLists]-->l  <!--[endif]-->sbiedll.dll

<!-- [if !supportLists]-->l  <!--[endif]-->dbghelp.dll

<!-- [if !supportLists]-->l  <!--[endif]-->api_log.dll

<!-- [if !supportLists]-->l  <!--[endif]-->dir_watch.dll

<!-- [if !supportLists]-->l  <!--[endif]-->pstorec.dll

<!-- [if !supportLists]-->l  <!--[endif]-->vmcheck.dll

<!-- [if !supportLists]-->l  <!--[endif]-->wpespy.dll

如果返回上述任何一个DLL句柄，它将退出该进程。这些DLL与杀毒、分析工具和虚拟化相关联。Kardon Loader还会枚举CPUID Vendor ID值，并将其与以下字符串进行比较：

<!-- [if !supportLists]-->l  <!--[endif]-->KVMKVMKVM

<!-- [if !supportLists]-->l  <!--[endif]-->Microsoft Hv

<!-- [if !supportLists]-->l  <!--[endif]-->VMwareVMware

<!-- [if !supportLists]-->l  <!--[endif]-->XenVMMXenVMM

<!-- [if !supportLists]-->l  <!--[endif]-->prl hyperv

<!-- [if !supportLists]-->l  <!--[endif]-->VBoxVBoxVBox

这些是已知的与虚拟机相关的CPUID Vendor ID值。如果检测到其中一个值，恶意软件也会退出。



## 命令与控制

Kardon Loader使用基于HTTP的C2基础设施和base64编码的URL参数。执行后，Kardon Loader将发送HTTP POST到C2，其中包含以下字段：

<!-- [if !supportLists]-->l  <!--[endif]-->ID =识别码

<!-- [if !supportLists]-->l  <!--[endif]-->OS=操作系统

<!-- [if !supportLists]-->l  <!--[endif]-->PV=用户权限

<!-- [if !supportLists]-->l  <!--[endif]-->IP=初始有效荷载（完整路径）

<!-- [if !supportLists]-->l  <!--[endif]-->CN=计算机名称

<!-- [if !supportLists]-->l  <!--[endif]-->UN=用户名

<!-- [if !supportLists]-->l  <!--[endif]-->CA=处理器体系结构

在执行时，从Kardon Loader样本执行时发送的POST有效载荷示例可以从（图6）看到：

[![](https://p4.ssl.qhimg.com/t01d1cecdbc32a69f6f.png)](https://p4.ssl.qhimg.com/t01d1cecdbc32a69f6f.png)图6：Kardon Loader POST 请求

一旦发出请求，C2服务器将提供不同的反馈，这将导致下载和执行额外的有效载荷、访问网站、升级当前有效载荷或卸载自身。等待命令的C2服务器响应格式是：

<!-- [if !supportLists]-->l  <!--[endif]-->notask

其他命令包括下载和执行功能使用以下格式：

<!-- [if !supportLists]-->l  <!--[endif]-->newtask`##`＃&lt;URL&gt;

<!-- [if !supportLists]-->n  <!--[endif]-->Hashmarks表示两个字符的任务ID和一个字符的任务值

接下来，受感染的主机会以与以下附加字段相同的格式向C2发回确认消息：

<!-- [if !supportLists]-->l  <!--[endif]-->TD=任务标识符（由命令和控制提供）

<!-- [if !supportLists]-->l  <!--[endif]-->OP=任务输出（如果成功则为1，否则为2）

对各种样本的分析揭示了另一个用于卸载由C2引导的loader的参数：

<!-- [if !supportLists]-->l  <!--[endif]-->UN=卸载

威胁参与者在他们的广告主题上发布的帖子表明，将来这个家族的C2通信将被改为RC4加密。另外，如果威胁参与者真正实现了DGA，可能会将其用作C2的回退机制。



## 管理面板

[![](https://p2.ssl.qhimg.com/t01c91dbb2cb385dcd6.png)](https://p2.ssl.qhimg.com/t01c91dbb2cb385dcd6.png)图7：Kardon Loader 管理面板

Kardon Loader面板采用了一个简单的设计，由bot分发仪表板和安装统计信息组成。该面板的一个显著特点是bot商店功能，允许bot管理员为客户生成访问密钥，从而使他们能够根据预定义的参数执行任务（图8）。 [![](https://p4.ssl.qhimg.com/t01dafe78ff38784c7b.png)](https://p4.ssl.qhimg.com/t01dafe78ff38784c7b.png)

图8：Kardon Loader 商店

用户可以指定一个URL，然后提供任务类型和执行次数，以便将命令分发给网络上的bot。威胁参与者在YouTube视频中展示了这一点（图4）。



## 结论和建议

本文概述了称为Kardon Loader的下载器恶意软件。Kardon Loader是一个全功能的下载器，可以下载和安装其他恶意软件。例如，银行木马/凭证窃取软件等。下载器是恶意软件生态系统的重要组成部分，通常由专家开发并独立于木马进行销售，这是该活动的目标。虽然只有在公开测试版阶段，该恶意软件才具有bot商店功能，允许购买者使用此平台开设自己的botshop。但这位威胁参与者在四月底开始为此Loader做广告，并表示今后将会在这个Loader的基础上进行进一步的开发，包括加密的C2通信。

至少组织应该利用本报告中包含的指标来阻止与Kardon Loader相关的恶意活动。研究人员还可以利用下面的Yara规则来寻找Kardon Loader的其他副本来，以提取其他用于阻止恶意活动的IOC。



## Yara规则

<!-- [if !supportLists]-->l  <!--[endif]-->[https://gist.github.com/arbor-asert/2ad9c7d715f41efc9d59ed8c425d10d3](https://gist.github.com/arbor-asert/2ad9c7d715f41efc9d59ed8c425d10d3)



## Hashes

<!-- [if !supportLists]-->l  <!--[endif]-->fd0dfb173aff74429c6fed55608ee99a24e28f64ae600945e15bf5fce6406aee

<!-- [if !supportLists]-->l  <!--[endif]-->b1a1deaacec7c8ac43b3dad8888640ed77b2a4d44f661a9e52d557e7833c7a21

<!-- [if !supportLists]-->l  <!--[endif]-->3c64d7dbef4b7e0dd81a5076172451334fe9669800c40c895567226f7cb7cdc7



## C&amp;C URLs

<!-- [if !supportLists]-->l  <!--[endif]-->Kardon[.]ddns[.]net

<!-- [if !supportLists]-->l  <!--[endif]-->Jhuynfrkijucdxiu[.]club

<!-- [if !supportLists]-->l  <!--[endif]-->Kreuzberg[.]ru

<!-- [if !supportLists]-->l  <!--[endif]-->Cryptdrop[.]xyz

审核人：yiwang   编辑：边边
