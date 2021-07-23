> 原文链接: https://www.anquanke.com//post/id/175513 


# 木马作者主动提交Tatoo远控后门程序


                                阅读量   
                                **338710**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">13</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01aa9e509591336b21.jpg)](https://p4.ssl.qhimg.com/t01aa9e509591336b21.jpg)



## 一、    概述

近日，360核心安全团队发现一个伪装商业软件的木马程序，该程序拥有有效的数字签名《南充市庆达商贸有限公司》，该木马作者主动提交的软件“单据打印系统”，企图通过正规渠道来躲避安全软件的查杀。该木马拥有云控功能，可以在云端关闭或开启工作流程，通过对该木马的深入分析，最终发现开启工作流程后会安装一个远控后门程序长期潜伏在受害者的机器中。



## 二、    木马分析

#### 工作流程

该木马作者主动提交的“单据打印系统”除了正常的功能代码之外，还包含了一些加密信息，解密后会得到木马云控地址。根据后续代码流程可以知道从云端下发的文件是一个DLL模块，该模块将在内存中被加载，并执行名为“MainThread”的导出函数。运行了该DLL功能后，会继续释放其他恶意文件，对用户电脑进行安装布置，直至完全控制用户电脑。

[![](https://p5.ssl.qhimg.com/t013743bca6ace996a7.png)](https://p5.ssl.qhimg.com/t013743bca6ace996a7.png)

木马工作流程

#### 详细分析

运行木马作者提交的“单据打印系统”软件程序，该程序首先会检测云控地址是否开启工作流程，如果没有开启那么软件将会运行无害的流程，显示正常的程序功能。但是如果云端开启工作指示，那么该软件就会运行潜伏工作，常驻在用户电脑中造成危害。

[![](https://p0.ssl.qhimg.com/t0150e930773ff715b0.png)](https://p0.ssl.qhimg.com/t0150e930773ff715b0.png)

云控未开启的运行状态

木马程序检测到云端开启工作流程后下载DLL模块并在内存加载执行的代码如下。

[![](https://p0.ssl.qhimg.com/t0173b7ab052fd9daf2.png)](https://p0.ssl.qhimg.com/t0173b7ab052fd9daf2.png)

云控开启后的木马流程

由于木马作者提交的软件版本中云控地址（hxxp://www.ohmytatoo.com/Tatoo.html）暂未开放，所以并未开始投入使用。不过通过360安全大脑感知，我们却发现了相同C&amp;C域名的木马在野传播案例。如下图所示，在野木马程序功能与上述提交的软件版本基本一致，都是通过云控地址下载恶意文件，但与之前版本不同的是，在野木马中还多了一个加密的恶意程序，在调用“MainThread”导出函数时，会直接加载运行该恶意程序。

[![](https://p0.ssl.qhimg.com/t01e50805152bd6dbe5.png)](https://p0.ssl.qhimg.com/t01e50805152bd6dbe5.png)

在野木马程序

对比在野木马和提交审核版本的云控流程，发现C&amp;C地址可以相互替换，运行流程是一致的，两个程序调用恶意DLL的代码部分基本相同。

[![](https://p3.ssl.qhimg.com/t0127bac977d349ccd4.png)](https://p3.ssl.qhimg.com/t0127bac977d349ccd4.png)

企图认证的程序                                                 恶意程序

从在野木马云控地址（hxxp://www.ohmytatoo.com/dll.jpg）下载的文件，主要功能是在C盘根目录下创建一个Microsoftxxxxx的目录（目录后5位是随机字符），并将加密恶意模块写入到该目录下的文件“bugrpt.log”，同时再释放一些辅助模块，文档结构如下图所示。

[![](https://p5.ssl.qhimg.com/t01ee9f1332997eabab.png)](https://p5.ssl.qhimg.com/t01ee9f1332997eabab.png)

木马释放的文件

其中“schedule.exe”是被木马利用的”窗口隐藏工具”，可以通过更改同目录下的配置文件让该程序来完成添加自启动项的任务。

[![](https://p0.ssl.qhimg.com/t01d41c66ddf8c5a1c6.png)](https://p0.ssl.qhimg.com/t01d41c66ddf8c5a1c6.png)

白利用设置自启动

接着木马程序会通过命令行调用”temp.exe”（实为WinRAR解压程序）对 “temp.txt”文件进行解压，解压密码为”123”。此步骤释放出来的两个重要文件是一组典型的白利用，用于躲避安全软件的查杀，其中白文件是腾讯的漏洞扫描程序，被重命名为“schedule.exe”用以替换刚刚添加自启动项的”窗口隐藏工具”，而黑文件则命名成“qmipc.dll”以便在系统自启白文件“schedule.exe”时自动被加载。

[![](https://p5.ssl.qhimg.com/t01d44e44e9d7c09c70.png)](https://p5.ssl.qhimg.com/t01d44e44e9d7c09c70.png)

进程链

“qmipc.dll”模块的主要任务是对加密恶意模块bugrpt.log进行解密和内存加载，并启动名为“Torchwood”的导出函数。解密的恶意模块即为Torchwood远控的核心程序。

[![](https://p5.ssl.qhimg.com/t01c171d8e6f4d46957.png)](https://p5.ssl.qhimg.com/t01c171d8e6f4d46957.png)

PELoader模块

进一步对该后门程序进行分析，得到木马远控的上线地址为120.24.231.105:7363。

[![](https://p5.ssl.qhimg.com/t018ea6c62ea1bc25f9.png)](https://p5.ssl.qhimg.com/t018ea6c62ea1bc25f9.png)

木马上线地址

至此，该木马程序就完成了其安装工作的任务，可以长期潜伏在受害用户的电脑中，并实时处于木马作者的监控之中。下图是木马作者云端使用的后门管理软件。

[![](https://p5.ssl.qhimg.com/t01b9f3142729ff3c8e.png)](https://p5.ssl.qhimg.com/t01b9f3142729ff3c8e.png)

木马控制端

该木马拥有的都是常规的远控程序功能，包括文件管理，键盘记录，屏幕控制，语音监听等等功能。其中部分操作指令及对应的功能如下：

[![](https://p2.ssl.qhimg.com/t012ad0d278f0b694d4.png)](https://p2.ssl.qhimg.com/t012ad0d278f0b694d4.png)

远控部分指令



## 三、      寻踪溯源

由于360安全大脑的实时监测和持续查杀，导致该系列木马存活率低，于是作者铤而走险，妄想通过伪装成正规公司来提交软件，企图蒙混过关。软件审核过程中该作者还多次通过电话和邮箱催促，一再强调自己是正常软件，实在是“此地无银三百两”。

[![](https://p5.ssl.qhimg.com/t010122bbc2cd7bad90.png)](https://p5.ssl.qhimg.com/t010122bbc2cd7bad90.png)

木马作者邮件

根据提交的资料，我们整理了木马作者的相关信息

[![](https://p0.ssl.qhimg.com/t01db96184f2c160085.png)](https://p0.ssl.qhimg.com/t01db96184f2c160085.png)

木马作者信息

查看木马作者的QQ：

[![](https://p2.ssl.qhimg.com/t01143c8bbdd9eb5c28.png)](https://p2.ssl.qhimg.com/t01143c8bbdd9eb5c28.png)

木马作者QQ

根据360安全大脑的监测数据，我们发现木马作者经常活跃的城市主要有两个，一个是江苏无锡，正好对应QQ号的归属地址，另一个是四川的南充，则对应作者提交的公司地址。

[![](https://p2.ssl.qhimg.com/t01dea1a858d5848429.png)](https://p2.ssl.qhimg.com/t01dea1a858d5848429.png)

木马作者活跃地址-江苏

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0145e2a6c48a4ddbb3.png)

木马作者活跃地址-南充

查询该公司的营业执照，发现此公司确实存在。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a9884c3b8d804987.png)

签名公司的营业执照

除了“正规”的营业执照，木马作者还特定为该公司申请了合法有效的数字签名。

[![](https://p0.ssl.qhimg.com/t01080583f4dcc35981.png)](https://p0.ssl.qhimg.com/t01080583f4dcc35981.png)

木马的签名信息

进一步挖掘后发现，该系列远控木马与曾经多次出现的Torchwood木马是同一家族，早在2017年的一篇报告中我们就披露了Torchwood木马作者的部分信息（“hxxps://www.anquanke.com/post/id/87775”），与这次木马作者企图混白时提供的信息比较发现，拥有相同的手机号码和qq号，因此认为是同一人或团伙所为。该木马作者在上次被曝光后并未收手，持续对木马进行更新，对抗安全软件的查杀。（下图中为我们追踪到的不同版本的Torchwood木马控制端）。

[![](https://p1.ssl.qhimg.com/t018dfdf16d0f7256d4.png)](https://p1.ssl.qhimg.com/t018dfdf16d0f7256d4.png)

木马控制端



## 四、    总结

360安全大脑一直以来都会对监测到最新木马病毒第一时间进行查杀，并通过多种技术手段防御和发现最新木马病毒，保证用户信息的安全。

[![](https://p0.ssl.qhimg.com/t01b4b868f04b473b15.png)](https://p0.ssl.qhimg.com/t01b4b868f04b473b15.png)



## 五、    附录

**Hashs**

[![](https://p1.ssl.qhimg.com/t01f6c407b3620a33a2.png)](https://p1.ssl.qhimg.com/t01f6c407b3620a33a2.png)
