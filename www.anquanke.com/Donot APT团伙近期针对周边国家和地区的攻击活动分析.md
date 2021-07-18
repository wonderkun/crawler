
# Donot APT团伙近期针对周边国家和地区的攻击活动分析


                                阅读量   
                                **498407**
                            
                        |
                        
                                                                                    



[![](./img/204095/t01f0701c2a21678b3b.jpg)](./img/204095/t01f0701c2a21678b3b.jpg)



## 概述

Donot“肚脑虫”（APT-C-35）是疑似具有南亚背景的APT组织，其主要以周边国家的政府机构为目标进行网络攻击活动，通常以窃密敏感信息为目的。该组织具备针对Windows与Android双平台的攻击能力。

自2017年开始，奇安信威胁情报中心对该组织一直保持着持续跟踪，并多次公开披露过其攻击活动。近期，奇安信红雨滴和奇安信APT实验室在日常的跟踪过程中，再次监测到该组织开展了新一轮攻击活动。此次攻击活动中，该组织采用的技战术手法并未发生大的变化，只是在代码中做了些轻微改动：例如下载器中将字符串简单加密处理、Android样本中将C2等信息简单加密处理等。红雨滴团队对新捕获到的样本进行了详细分析。



## 样本分析

此次捕获的攻击样本均为宏利用样本，基本信息如下
<td style="width: 113.15pt;" valign="top">**文件名**</td><td style="width: 166.35pt;" valign="top">**MD5**</td><td style="width: 43.4pt;" valign="top">**作者**</td><td style="width: 91.9pt;" valign="top">**修改时间**</td>
<td style="width: 113.15pt;" valign="top">**22 Apr 2020.xls**</td><td style="width: 166.35pt;" valign="top">107d25c7399b17ad6b7c05993b65c18e</td><td style="width: 43.4pt;" valign="top">Testing</td><td style="width: 91.9pt;" valign="top">2020:03:17 10:42:38</td>
<td style="width: 113.15pt;" valign="top">**List of new items.xls**</td><td style="width: 166.35pt;" valign="top">a9d6d2d93eda11e89ed2ca034b81e6ef</td><td style="width: 43.4pt;" valign="top">Testing</td><td style="width: 91.9pt;" valign="top">2020/02/24 06:00</td>
<td style="width: 113.15pt;" valign="top">**Invoice.xls**</td><td style="width: 166.35pt;" valign="top">22be6422e8cc09bda69843acc405f104</td><td style="width: 43.4pt;" valign="top">Testing</td><td style="width: 91.9pt;" valign="top">2020:01:08 07:07:06</td>
<td style="width: 113.15pt;" valign="top">**RegistrationForm.xls**</td><td style="width: 166.35pt;" valign="top">554a72999435c81ceedf79db6a911142</td><td style="width: 43.4pt;" valign="top">Testing</td><td style="width: 91.9pt;" valign="top">2019:10:18 09:33:17</td>

以”22 Apr 2020.xls”为例，打开文档时便会弹出窗口提示启用宏

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011de3d763a13b0507.png)

一旦受害者启用宏，恶意宏将故意弹出一个报错窗口，以迷惑受害者

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016dbbcc1908c89ec3.png)

而恶意宏将在释放一个恶意dll以及一个bat到受害者计算机，并通过创建计划任务将bat文件执行起来

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f7639e2032fade18.png)

创建的计划任务信息如下

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f8ca91a77d7fb12e.png)

通过计划任务触发执行的bat文件将创建多个目录，并将这些目录属性设置为隐藏

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a052d4c95f6fbf9d.png)

之后获取计算机名和5位随机数字组成字符串保存到%USERPROFILE%\Printers\Net\profiles\irina，同时将dll文件移到%USERPROFILE%\Check\Netspeed\Data\目录下重命名为inet.dll

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018b071e0685d4471a.png)

最后再创建两个计划任务”Internet”，”Data_log”,其中”Internet”用于执行inet.dll

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0159c5777d7beaffd0.png)

样本运行流程可通过奇安信在线云沙箱运行查看，整体行为流程如图所示

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012731583fad049363.png)
<td style="width: 77.75pt;" valign="top">**文件名**</td><td style="width: 7.0cm;" valign="top">**inet.dll**</td>
<td style="width: 77.75pt;" valign="top">**MD5**</td><td style="width: 7.0cm;" valign="top">D140F63FF050C572398DA196F587775C</td>

该dll是一个downloader,主要用于下载后续木马执行，运行后，首先通过长时间sleep从而使一些沙箱无法执行后续行为

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f0178f1d666e6783.png)

样本中的关键字符串采用简单的加密处理

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016b697d338b77393a.png)

样本经过长时间的休眠 之后，将尝试从远程服务器supportsession[.]live/192362/x2d34x3获取文件，若成功获取则写入到%USERPROFILE%\\Look\\Drive\\wmi\\hostcom.exe

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0137fd5f35c60c4779.png)
<td style="width: 99.0pt;" valign="top">文件名</td><td style="width: 315.8pt;" valign="top">hostcom.exe</td>
<td style="width: 99.0pt;" valign="top">MD5</td><td style="width: 315.8pt;" valign="top">8b640d71f6eda4bdddeab75b7a1d2e12</td>

该文件成功获取后，将通过bat创建的计划任务”Data_log”加载执行。

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01432589516f45ac1a.png)

该样本采用了与inet.dll相同的简单加密，执行后，会尝试从\Printers\Net\profiles\irina中获取“计算机名-随机数“

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0112fb869ada3b7bef.png)

之后将以参数orderme/计算机名-随机数与c2: requestupdate.live进行通信

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f8725355a0e69a46.png)

与c2通信获取信息执行，当返回数据中包含“Content-Type: xDvsds “以及”Content-Type: Bw11eW”时，将远程获取命令保存到\Printers\Net\net\test.bat中执行

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b0bf3c2997fd0a94.png)

若都没有，则尝试读取数据写入\Printers\Net\net\wuaupdt.exe执行

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014838193d683ca771.png)

遗憾的是，在分析的过程中，c2服务器已经失效，无法获取到后续木马。



## 溯源关联

奇安信威胁情报中心红雨滴团队通过对宏特征，bat特征，木马特征等信息进行关联分析发现，此次捕获的样本均出自南亚APT组织Donot。

### 与Donot APT团伙的关联

此次捕获样本释放执行的bat文件与奇安信威胁情报中心《Donot（APT-C-35）组织对在华巴基斯坦商务人士的定向攻击活动分析》**<sup>[1]</sup>**一文中的bat文件基本一致，都创建多个隐藏目录，并获取计算机名加随机数组成字符串保存到文件。

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017a21aa9aabfacc0b.png)

hostcom.exe与Plugin-Downloader – wlidsvcc.exe也基本一致，同样以参数”orderme/计算机名-随机数”与c2通信，且下载的后续木马文件名保存为wuaupdt.exe

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b487b18a93dd03a6.png)

同时，其c2命名方式也与donot基本一致，且奇安信ALPHA威胁分析平台已有Donot相关标签

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010d599da8cb5bba16.png)

### 代码更新

同时，该APT组织也对其攻击武器进行了简单的更新，以逃过一些安全研究人员的追踪，例如之前通过注册表启动项启动后续木马，到如今的利用计划任务实现持久化。

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018481dbd4218b47cb.png)

明文路径等也加上了简单的加密，此方法可能时为了逃避字符串相关规则

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013080c9e06eb43b82.png)

同样的，其Android端也对c2增加了简单的加密处理

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01070110b0ae6182e1.png)

[![](./img/204095/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d0266fb166b32189.png)



## 总结

APT组织不会因为安全研究人员对其进行披露而停止攻击活动，从Donot组织样本代码更新可以看出，APT组织也会不断改进其攻击武器，改变其攻击手法，更有甚者会模仿其他APT组织展开攻击活动，从而躲避安全研究人员的跟踪。

奇安信威胁情报中心再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括威胁情报平台（TIP）、天眼高级威胁检测系统、NGSOC、奇安信态势感知等，都已经支持对此APT攻击团伙攻击活动的精准检测。



## IOC

**MD5**

107d25c7399b17ad6b7c05993b65c18e

fa86464d6fa281d6bec6df62d5f2ba4f

22be6422e8cc09bda69843acc405f104

554a72999435c81ceedf79db6a911142

fa86464d6fa281d6bec6df62d5f2ba4f

22be6422e8cc09bda69843acc405f104

554a72999435c81ceedf79db6a911142

A9D6D2D93EDA11E89ED2CA034B81E6EF

d140f63ff050c572398da196f587775c

428C9AEA62D8988697DB6E96900D5439

a0e985519bf45379495ed9087e0c9e45

**C2**

requestupdate.live

linkrequest.live

supportsession.live

rythemsjoy.club

mailsession.online



## 参考链接：

[1] [https://ti.qianxin.com/blog/articles/donot-group-is-targeting-pakistani-businessman-working-in-china/](https://ti.qianxin.com/blog/articles/donot-group-is-targeting-pakistani-businessman-working-in-china/)
