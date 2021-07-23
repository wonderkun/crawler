> 原文链接: https://www.anquanke.com//post/id/247418 


# Triconex SIS工业安全控制系统常见问题分析


                                阅读量   
                                **27356**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t015a4339ca14a2db69.jpg)](https://p4.ssl.qhimg.com/t015a4339ca14a2db69.jpg)



## 摘要：

随着工业控制系统的迅速发展，安全仪表系统在工业生产的所有领域得到了广泛的使用。工控系统所用到的组态软件在使用过程中，都会出现或多或少的问题。现对我们实验室自己的设备硬件环境Triconex sis系统在使用过程中遇到的问题进行汇总分析并给出相应的解决方法。此次我们进行安全研究测试的对象设备总价值70余万元，期间也挖出了不少未公开0day漏洞。

[![](https://p1.ssl.qhimg.com/t0137243f51f9ba5c47.jpg)](https://p1.ssl.qhimg.com/t0137243f51f9ba5c47.jpg)



## 正文

### <a class="reference-link" name="SIS%E6%98%AF%E4%BB%80%E4%B9%88%EF%BC%9F"></a>SIS是什么？

安全仪表系统（Safety Instrumented Systems，SIS），又被称为工业安全系统，被用来预防工业中出现的事故，比如设备或操作故障，造成损坏、伤害、生命损失或严重的环境损害。极端后果的则是爆炸、火灾、石油泄漏、洪水甚至核系统崩溃。

### <a class="reference-link" name="Triconex%E6%98%AF%E4%BB%80%E4%B9%88%EF%BC%9F"></a>Triconex是什么？

Triconex所属于法国施耐德，作为全球领先的过程安全系统供应商，目前在全球已有超过80 个国家、14300 多套系统分布在全球各地使用，并采用最先进的 TMR 微处理器硬件技术和成熟可靠的TRISTATION 1131软件的三重化冗余容错控制系统。系统高可靠性和高利用率被广泛应用于石化、炼油、石油天然气、化工、电力、轨道交通、航天、核工业等行业。在装置安全联锁系统 ESD 、蒸汽透平控制、燃汽透平控制、压缩机防喘振控制、海上石油平台、火气监测保护（ F&amp;G ）等方面有广泛的业绩。

### <a class="reference-link" name="%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86"></a>工作原理

[![](https://p4.ssl.qhimg.com/t012ef9291b31e261b8.png)](https://p4.ssl.qhimg.com/t012ef9291b31e261b8.png)

三重组合式冗余（TMR）结构保证了设备的容错能力，并能在原部件出现硬实效或者来自内部或外部来源的瞬态故障出现的情况下提供正确的不中断的控制。

每一个I/O模件内都包容有三个独立支路的电路，输入模件上的每一 支路读取过程数据并将这些信息传送给它的相应的主处理器。三个主处理器通过一个适配的高速总线系统，被称作为TRIBUS的系统相互通讯。当每扫描一次，主处理器都通过TRIBUS与其邻居进行通讯和同步化。TRIBUS作为数字式输入数据、比较输出数据、并将模拟输入数据的副本送达每一主处理器。主处理器执行控制程序并把由控制程序所产生的输出送给输出模件。除对输入数据之外，Triconex也输出数据。这是在离现场最近的输出模件上完成的，以便探查出任何错误并予以补偿。



## 控制系统遇到的常见问题如下

主要分为硬件、组态、人为和系统问题。



## 一、硬件问题

这类问题主要出现在硬件安装过程。比如电气安装（强弱电分开、元器件和模块供电额定电压和额定电流）、系统环境温湿度、模块安装是否正确等。

确认安装无问题后，可通电通讯，然后根据现场模块指示灯判断模块问题所在。现场模块指示灯显示如下图：

[![](https://p5.ssl.qhimg.com/t01bdb4b10a9103a502.jpg)](https://p5.ssl.qhimg.com/t01bdb4b10a9103a502.jpg)

图1.1

### <a class="reference-link" name="1%E3%80%81%E7%94%B5%E6%BA%90%E6%A8%A1%E5%9D%97"></a>1、电源模块

电源模件前面的LED指示灯的状态说明：

[![](https://p0.ssl.qhimg.com/t01d7de872d59d717a2.png)](https://p0.ssl.qhimg.com/t01d7de872d59d717a2.png)

表1.1

从图1.1中可以看出，电源模块工作正常但其电池的功率不够。如电力故障，电池不能保持住RAM内的程序。建议处理方法：待停车后更换电池。

下表列出可能发生在电源模块的情况，对每种情况加以说明，并推荐出改正的措施。

[![](https://p5.ssl.qhimg.com/t0198893f1c3591df3e.png)](https://p5.ssl.qhimg.com/t0198893f1c3591df3e.png)

表1.2

### <a class="reference-link" name="2%E3%80%81%E4%B8%BB%E5%A4%84%E7%90%86%E5%99%A8"></a>2、主处理器

主处理器（控制器）前面的LED指示灯的状态说明：

[![](https://p1.ssl.qhimg.com/t014b7c03126102ec9c.png)](https://p1.ssl.qhimg.com/t014b7c03126102ec9c.png)

表1.3

从图1.1中可以看出，主处理器（MP）模块工作正常。ACTIVE指示灯在执行控制程序时每扫描一次闪烁一次。MAINT1灯常亮，是因为电池电量低而触发的。MAINT1是维护灯，在电池电压(更换电池)恢复后MAINT1灯会自动消除掉的，手动消除不了。

下表列出了MP上由维护指示灯所表示的可能的情况，经每种情况以说明，并给出推荐的措施。

[![](https://p1.ssl.qhimg.com/t013303310c70dd877f.png)](https://p1.ssl.qhimg.com/t013303310c70dd877f.png)

表1.4

### <a class="reference-link" name="3%E3%80%81%E5%85%B6%E4%BB%96IO%E6%A8%A1%E5%9D%97"></a>3、其他IO模块

IO模块前面的LED指示灯的状态说明：

[![](https://p4.ssl.qhimg.com/t0154032a46457c310c.png)](https://p4.ssl.qhimg.com/t0154032a46457c310c.png)

表1.5

从图1.1中可以看出，IO模块已运行并正常工作。

下表列出了数字输入模块的PASS、FAULT和ACTIVE各指示灯所表示的可能出现的各种情况，以及对每一情况的说明和建议采取的措施。

[![](https://p4.ssl.qhimg.com/t01bce1d8321cc846a1.png)](https://p4.ssl.qhimg.com/t01bce1d8321cc846a1.png)

表1.6



## 二、软件组态问题

这一类问题是软件本身在组态配置过程引起的错误。一般出现在设计调试阶段，本人根据自身组态配置过程中遇到的问题，以及当时的处理方法进行整理。

1、进行控制器连接时，通讯失败，出现下图错误。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0119e7a28f0f6842f4.png)

图2.1

主要原因是通讯设置出现了问题，处理方法如下：

（1）检查控制器是否已开启，网线是否损坏，接口是否有问题；<br>
（2）检查本地IP地址是否已设置与控制器同一网段；<br>
（3）如果组态软件在虚拟机中，检查虚拟机系统网络设置是否为桥接模式，不要选中“复制物理网络连接状态”；<br>
（4）如果组态软件在虚拟机中，使用网线第一次与控制器连接时，需要断开物理机网络。

2、进行控制器连接时，通讯失败，出现下图错误，连接不上控制器。

[![](https://p5.ssl.qhimg.com/t017c599966d7c7f36f.png)](https://p5.ssl.qhimg.com/t017c599966d7c7f36f.png)

图2.2

主要原因是控制器中安装的主处理器的型号与项目中配置的主处理器的型号不匹配。由于主处理器之间的不匹配，TriStation 1131无法连接到所选的控制器。确保您尝试连接到正确的控制器，或更新项目中的“主处理器”配置，以使其与控制器中安装的“主处理器”相匹配。

3、通讯失败，出现下图错误，连接不上控制器。

[![](https://p3.ssl.qhimg.com/t01b76c4e40edcd0dcd.png)](https://p3.ssl.qhimg.com/t01b76c4e40edcd0dcd.png)

图2.3

原因是项目中配置的底盘类型与控制器中存在的底盘类型不匹配。在连接到控制器之前，更改项目中的底盘类型以匹配控制器的底盘类型。处理办法如下图。

[![](https://p0.ssl.qhimg.com/t01a4996fe52bc0a8a1.png)](https://p0.ssl.qhimg.com/t01a4996fe52bc0a8a1.png)

图2.4

[![](https://p3.ssl.qhimg.com/t01680fad59ba66fef7.png)](https://p3.ssl.qhimg.com/t01680fad59ba66fef7.png)

图2.5

4、当更换底盘后，出现下图的错误。

[![](https://p3.ssl.qhimg.com/t01a7fff45d464552ec.png)](https://p3.ssl.qhimg.com/t01a7fff45d464552ec.png)

图2.6

原因是项目中配置的主处理器模型与增强性能（EP_MAIN）机箱不兼容。 EP_MAIN机箱仅与主处理器型号3008（在Tricon 10.3.x和更高版本的系统中）和3009（在Tricon 11.0.x和更高版本中）兼容。

在用EP_MAIN机箱替换现有的高密度（HD_MAIN）机箱之前，必须将3006 / N或3007型主处理器（如果有）替换为3008或3009型主处理器。如果您拥有目标系统版本早于Tricon 10.3.x的Model 3008主处理器，请将目标系统版本升级到Tricon 10.3.x或更高版本，或将其替换为Model 3009主处理器。处理方法如下图。

[![](https://p0.ssl.qhimg.com/t017f1e8948320faa36.png)](https://p0.ssl.qhimg.com/t017f1e8948320faa36.png)

图2.7

5、连接控制器时，弹出下图警告窗口。

[![](https://p2.ssl.qhimg.com/t01684e0b7f691503d8.png)](https://p2.ssl.qhimg.com/t01684e0b7f691503d8.png)

图2.8

原因是控制器里面已有程序，最后一次下载的项目与现在的项目不一致。可以跳过警告，停止控制器，再进行下载新的项目操作。

6、连接控制器，出现下图的错误。

[![](https://p5.ssl.qhimg.com/t0145b5dd59f4f1c7e9.png)](https://p5.ssl.qhimg.com/t0145b5dd59f4f1c7e9.png)

图2.9

原因是项目与平台的系统版本不一致。处理方法如下图。

[![](https://p2.ssl.qhimg.com/t01aec9a016ca83278b.png)](https://p2.ssl.qhimg.com/t01aec9a016ca83278b.png)

图2.10

7、新建变量时，弹出图12或图13的错误提示窗口。

[![](https://p2.ssl.qhimg.com/t01a32ce75938870e57.png)](https://p2.ssl.qhimg.com/t01a32ce75938870e57.png)

图2.11

[![](https://p2.ssl.qhimg.com/t012a92ffe3007e1958.png)](https://p2.ssl.qhimg.com/t012a92ffe3007e1958.png)

图2.12

原因是输入了无效的名称。名称必须以一个字母字符(从A到Z)开始，最多可以包含31个字母数字字符(包括下划线字符)。

8、编译出现错误，错误信息如下图。

[![](https://p5.ssl.qhimg.com/t01b49cd409f20c1cf8.png)](https://p5.ssl.qhimg.com/t01b49cd409f20c1cf8.png)

图2.13

原因是没有把两个程序段隔开。组态过程中，没有连接关系的程序段，需要用分隔线分开，处理方法如下图。

[![](https://p0.ssl.qhimg.com/t01e548e4d00647118d.png)](https://p0.ssl.qhimg.com/t01e548e4d00647118d.png)

图2.14

9、编译出现下图错误信息。

[![](https://p2.ssl.qhimg.com/t01503c1bb449da0d9c.png)](https://p2.ssl.qhimg.com/t01503c1bb449da0d9c.png)

图2.15

原因是程序中有变量未与功能/功能块连接，或功能/功能块之间未连接。检查连接线，正确连接后再进行编译即可。

10、编译出现下图错误。

[![](https://p1.ssl.qhimg.com/t0184584e49fab437de.png)](https://p1.ssl.qhimg.com/t0184584e49fab437de.png)

图2.16

原因是有未使用的变量未删除，未使用的变量是编程过程中，曾经添加使用过，到最后未使用。删除未使用的变量即可。

11、删除多余子程序时，弹出下图错误窗口。

[![](https://p2.ssl.qhimg.com/t01f3835755c64c4bc0.png)](https://p2.ssl.qhimg.com/t01f3835755c64c4bc0.png)

图2.17

原因是该程序在程序执行列表中，无法删除。程序执行列表在实施文档中。 程序执行列表中的程序已被或指定要下载到控制器。为了删除该程序，必须首先将其从程序执行列表中删除。如下图所示。

[![](https://p2.ssl.qhimg.com/t012a5f476658f24f84.png)](https://p2.ssl.qhimg.com/t012a5f476658f24f84.png)

图2.18

12、在使用Triconex SOE Recorder软件时，创建SED文件显示如下图。状态显示没反应。可能原因是未配置SOE块、SOE配置文件不是最新的或者设置错误。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0196da253245a7b86f.png)

图2.19

处理方法：

（1）配置SOE块。在“Implementation”界面中，展开“SOE Configuration”，配置一个SOE块，具体步骤如下图。

[![](https://p1.ssl.qhimg.com/t01b1a66166e943fa93.png)](https://p1.ssl.qhimg.com/t01b1a66166e943fa93.png)

图2.20

然后添加需要记录变量到SOE块中。

[![](https://p3.ssl.qhimg.com/t01f0562c905275ea97.png)](https://p3.ssl.qhimg.com/t01f0562c905275ea97.png)

图2.21

然后把文件夹C:\Users\Public\Documents\Triconex\TriStation 1131 4.16.0\Projects中的SOE文件复制到文件夹C:\Users\Public\Documents\Triconex\Triconex SOE Recorder\SoeConfig目录下。

[![](https://p5.ssl.qhimg.com/t0139f1afaedb354cbd.png)](https://p5.ssl.qhimg.com/t0139f1afaedb354cbd.png)

图2.22

[![](https://p3.ssl.qhimg.com/t012b1c97ffb8420ddc.png)](https://p3.ssl.qhimg.com/t012b1c97ffb8420ddc.png)

图2.23

（2）确认SOE文件是否最新的。打开文件夹C:\Users\Public\Documents\Triconex\TriStation 1131 4.16.0\Projects和C:\Users\Public\Documents\Triconex\Triconex SOE Recorder\SoeConfig，确认SOE文件是否都是最新的。

[![](https://p1.ssl.qhimg.com/t01aabbea82dfd6ba83.png)](https://p1.ssl.qhimg.com/t01aabbea82dfd6ba83.png)

图2.24

确认最新SOE文件

（3）进入设置界面，确认通讯设置参数。

[![](https://p3.ssl.qhimg.com/t01b3956deab0912cc3.png)](https://p3.ssl.qhimg.com/t01b3956deab0912cc3.png)

图2.25

如果SOE配置文件正确且是最新的，但显示下图，状态显示SOE块还未开始，原因是程序中没写入激活SOE块程序。

[![](https://p3.ssl.qhimg.com/t010ee00c1f834f3677.png)](https://p3.ssl.qhimg.com/t010ee00c1f834f3677.png)

图2.26

处理方法：编写激活SOE块程序，如下图。

[![](https://p1.ssl.qhimg.com/t01e05ba9df25fe14d2.png)](https://p1.ssl.qhimg.com/t01e05ba9df25fe14d2.png)

图2.27 激活SOE块程序

完成后，如果激活SOE块程序为单独子程序，在下载前，必须加入“Execution List”。然后重新配置SOE文件。最后得到下图结果。

[![](https://p2.ssl.qhimg.com/t01c340fa821e5fbeab.png)](https://p2.ssl.qhimg.com/t01c340fa821e5fbeab.png)

图2.28

[![](https://p2.ssl.qhimg.com/t01b26828db1594aa28.png)](https://p2.ssl.qhimg.com/t01b26828db1594aa28.png)

图2.29 运行SOE事件收集

[![](https://p1.ssl.qhimg.com/t0127fb3ac217b26776.png)](https://p1.ssl.qhimg.com/t0127fb3ac217b26776.png)

图2.30 SOE事件



## 三、人为问题

失误原因有很多，有维护人员操作不当、专业水平欠佳、监护不到位、没有进行事故预想、管理有漏洞等原因。在实际运行操作中，有时会出现系统某些功能不能使用，但实际系统配置和组态没问题，问题就出现在操作人员，操作不熟练或操作不当引起的。因此操作人员需要经过专业培训才可以上岗操作。



## 结束语

工业控制系统已成为自动化工程的核心设备，在安装和调试运行中必须安全可靠，尽量做到零失误、零故障、安全生产。控制系统在工业机器运用中是很重要的，所以对其容易出现的故障一定要了解，按照常见故障规律进行判断，应该可以准确迅速地把故障排除掉，恢复开机便能正常运行。

大禹工控<br>
由中国网安·广州三零卫士成立，汇聚国内多名漏洞挖掘、二进制逆向、安全分析、渗透测试、自动化工程师等安全专家组建而成，专注于工业控制系统安全、工业物联网安全、工业威胁情报安全等安全领域，大禹工控安全实验室始终坚持在工业控制系统安全领域进行探索和研究

IRTeam工控安全红队<br>
属于民间工业安全组织，由经验丰富的工控安全研究员组成，一直在学习和研究最新的工控漏洞及漏洞利用和防护，同时开发了Kali ICS工控渗透平台能够提供全方位的工控漏洞挖掘和渗透测试。在工控的协议安全、HMI安全、工业云安全等领域有着丰富的经验和成果
