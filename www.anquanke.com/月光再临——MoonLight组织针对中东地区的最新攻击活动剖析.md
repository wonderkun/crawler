> 原文链接: https://www.anquanke.com//post/id/193844 


# 月光再临——MoonLight组织针对中东地区的最新攻击活动剖析


                                阅读量   
                                **1184783**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01b1fce01e7727e1bf.jpg)](https://p5.ssl.qhimg.com/t01b1fce01e7727e1bf.jpg)



## 一、概述

自2019年4月以来，奇安信APT实验室在日常威胁狩猎过程中监测到一批针对巴勒斯坦及加沙地区的有组织的、持续性的网络攻击行为，攻击面广、受害范围大，产生了严重的网络安全威胁，对此我们时刻保持高度关注并深入分析。

同时观察到近期部分安全厂商发布多篇定性为“拍拍熊”（APT-C-37）的最新活动报告，诸多报告内容与我们此次披露的“月光再临”行动存在高度重合。本着严谨、求实的研究态度，奇安信APT实验室对该批次攻击活动进行持续追踪跟进挖掘，最终研判结果指向了另一个在加沙地区活动多年，疑似与哈马斯武装力量存在关联的MoonLight组织。该组织经常使用钓鱼邮件攻击，其攻击手法和C&amp;C命名规则与本次攻击活动存在诸多吻合点，因此我们本着“求同存异”和技术交流分享的原则公布此次分析溯源过程。



## 二、攻击组织背景介绍

### 1.  MoonLight组织介绍

Vectra Networks称其为Moonlight，但其他名称包括Gaza Hacker Team，Gaza Cyber gang，DownExecute，XtremeRAT，Molerats和DustSky。安全公司ClearSky在2016年6月表示，该组织可能与哈马斯组织有联系[1]。

该组织是出于政治动机的阿拉伯语网络威胁组织，针对中东和北非（MENA）地区，特别是巴勒斯坦领土。

在对该攻击组织2018年持续跟进过程中，识别出中东和北非地区非常相似的攻击者所使用的不同技术，但针对目标有时一致。该发现区分了加沙赛博帮内部运作的三个攻击组：

Group 1（经典的低预算小组），也称为MoleRAT；Gaza Cybergang Group2（中级复杂程度），与已知的”Desert Falcons”有联系； Group3（最高复杂度），其活动以前被称为” Operation Parliament”[2]。

### 2.  地缘问题、组织冲突剖析

地缘政治背景：法塔赫与哈马斯间的角力

法塔赫希望建立的是一个以耶路撒冷为首都的民族国家，而哈马斯则希望建立的是一个伊斯兰神权国家。双方在意识形态上就有着非常大的区别。其次，在对待以色列的态度上，法塔赫的态度更加务实，希望承认以色列，在对话的基础上解决巴以冲突。而哈马斯则更为极端，拒不承认以色列，主张坚持武装斗争。双方在对以斗争的路线上存在着巨大的分歧[3]。

2006年，“哈马斯”赢得巴立法委员会选举，但已经代表巴勒斯坦民众意见近半个世纪的“法塔赫”拒绝承认选举结果，双方发生武装冲突，2007年6月“哈马斯”夺取了加沙地带控制区，“法塔赫”退守约旦河西岸。如今的哈马斯和法塔赫虽然达成和解，但一直未按约履行。

态度转变的埃及政府：埃及前总统穆尔西曾是穆斯林兄弟会组织成员，而哈马斯也与穆斯林兄弟会有密切联系，因此哈马斯得到一部分阿拉伯国家支持，但因为该组织模糊了抵抗运动和恐怖组织之间的界限，很多人对该组织也呈反对态度。前总统穆尔西在位期间埃及对哈马斯武装力量提供了大量的资源和支持，利用埃及的地中海口岸和地道该武装力量得以从外界购买大量武器装备进入加沙地区。

但自2014年埃及总统塞西上台，为肃清与前总统相关的党羽派系，塞西坚决打击哈马斯力量，埃及政府对于哈马斯武装组织的态度呈现180度反转，腹背受敌的哈马斯组织也面临资源受限之境。

[![](https://p3.ssl.qhimg.com/t01b1bf0d74fba51deb.png)](https://p3.ssl.qhimg.com/t01b1bf0d74fba51deb.png)

图2.1：埃及对哈马斯的态度转变

2016年，MoonLight组织曾被安全公司ClearSky披露可能与哈马斯武装力量存在关联，通过简要了解中东地区错综复杂的局势发现该武装力量存在众多地缘冲突问题，如：法塔赫与哈马斯的派系斗争、巴勒斯坦与以色列间的国土冲突、埃及政府对哈马斯组织态度的转变等等，而这些冲突对象恰恰对应了该组织散布诱饵文件中众多话题信息。

结合样本武器中时区、位置信息和MoonLight组织的历史活动，与我们此次监测到的攻击活动存在大量相似之处，基于此，奇安信APT实验室将此次攻击活动研判为MoonLight组织所为。



## 三、网络武器分析梳理

### 1.  初始恶意载荷释放

**1.1     伪装的自解压可执行文件**

该批次捕获的样本初始恶意载荷都是通过将自解压文件（SFX）伪装为doc、jpg等文本图片形式，从而达到混淆视听的目的：

[![](https://p4.ssl.qhimg.com/t01f5c81bad85edb8e1.png)](https://p4.ssl.qhimg.com/t01f5c81bad85edb8e1.png)

图3.1样本挖掘时间线

**1.2     静默释放自身**

该类压缩包双击执行后将会按照预先设置的参数静默执行命令：
- 将自身解压到temp目录或Appdata目录下；
- 调用mstha或Wscript程序执行恶意脚本或恶意URL；
- 为受害者展示诱饵文档；
- 创建执行恶意脚本的快捷方式。
### 2.  攻击脚本手段变化

**2.1   解压执行恶意脚本**

2019年4月至8月，该组织的SFX自解压程序中包含了一个作为下载器的恶意脚本，该脚本会完成一系列下载任务，多次去混淆后执行真正的后门程序。

[![](https://p5.ssl.qhimg.com/t01b687de6535cc3367.png)](https://p5.ssl.qhimg.com/t01b687de6535cc3367.png)

图3.2自解压参数

[![](https://p3.ssl.qhimg.com/t01da1fea385c734b9e.png)](https://p3.ssl.qhimg.com/t01da1fea385c734b9e.png)

图3.3 d.vbs动态获取回连信息

**2.2   快捷方式访问URL**

在2019年8月的某样本中包含了一个VBS脚本和一个快捷方式：作为Loader的VBS脚本将会执行history.ink，而该ink会将恶意URL作为参数调用mstha程序完成了下载功能。这种访问方式也可看做为后续攻击手法升级的标志之一。

[![](https://p0.ssl.qhimg.com/t017167fb00f3d39087.png)](https://p0.ssl.qhimg.com/t017167fb00f3d39087.png)

图3.4 history快解方式

**2.3   mstha访问URL下载恶意脚本**

自2019年9月以来，该组织所使用的样本武器中只包含诱饵文档从而达到很好的免杀效果，通过在自解压过程中调用mstha访问恶意URL后下载带包含后门的混淆恶意脚本，并利用Powershell加载执行完成自身解密后展示最终的后门：

[![](https://p4.ssl.qhimg.com/t01ee29d858a1d93b8f.png)](https://p4.ssl.qhimg.com/t01ee29d858a1d93b8f.png)

[![](https://p1.ssl.qhimg.com/t01eb98e45a20d004db.png)](https://p1.ssl.qhimg.com/t01eb98e45a20d004db.png)

图3.5 自解压参数

[![](https://p3.ssl.qhimg.com/t019abe333576df0552.png)](https://p3.ssl.qhimg.com/t019abe333576df0552.png)

图3.6 adamnews.for.ug/2020内容

**2.4  该组织常用的混淆脚本**

[![](https://p4.ssl.qhimg.com/t01cb0f941df06ee908.png)](https://p4.ssl.qhimg.com/t01cb0f941df06ee908.png)

图3.7 done.jse

[![](https://p4.ssl.qhimg.com/t0160a6fef8ba376912.png)](https://p4.ssl.qhimg.com/t0160a6fef8ba376912.png)

图3.8 cr.zip

[![](https://p3.ssl.qhimg.com/t01e65ec10007ac55bd.png)](https://p3.ssl.qhimg.com/t01e65ec10007ac55bd.png)

图3.9 asd.jse

### 3.  精简的H-Worm后门

上述样本经过解混淆最终都会释放H-Worm后门程序，但是该组织所使用版本删去了Sleep等休眠命令，只保留了核心功能。也表明该组织后续或许会利用其它程序对受害者进一步控制：

**3.1   H-Worm功能分析**

[![](https://p5.ssl.qhimg.com/t01cea3bb514404786a.png)](https://p5.ssl.qhimg.com/t01cea3bb514404786a.png)

图3.10 H-Worm后门程序
<td valign="top">指令</td><td valign="top">功能</td>

功能
<td valign="top">execute</td><td valign="top">执行服务端命令</td>

执行服务端命令
<td valign="top">send</td><td valign="top">下载文件</td>

下载文件
<td valign="top">recv</td><td valign="top">上传数据</td>

上传数据
<td valign="top">enum-driver</td><td valign="top">枚举驱动</td>

枚举驱动
<td valign="top">enum-faf</td><td valign="top">枚举指定目录下的文件</td>

枚举指定目录下的文件
<td valign="top">enum-process</td><td valign="top">枚举进程</td>

枚举进程
<td valign="top">delete</td><td valign="top">删除文件</td>

删除文件
<td valign="top">exit-process</td><td valign="top">结束进程</td>

结束进程

表3.1 H-Worm命令

**3.2   回连信息：显示计算机信息**

[![](https://p1.ssl.qhimg.com/t01aa56ee7ad3f4c0e9.png)](https://p1.ssl.qhimg.com/t01aa56ee7ad3f4c0e9.png)

图3.11 回连信息使用&lt;|&gt;分割

**3.3   H-Worm后门介绍**

H-WORM作者ID为Houdini，使用VBS编写以实现远控蠕虫功能，能够通过感染U盘传播，出现的时间最早可以追溯到2013年7月。因为其简洁有效的远控功能、非PE脚本易于免杀、便于修改等特性，一直被恶意组织所青睐且活跃至今，Fireeye曾在其博客中有过介绍[4]，因此不再赘述。

### 4.  后门升级，全新版本

APT实验室分析人员通过对整体流程进行复盘，挖掘到曾被忽略的关键点：

在2019年8月的某样本中意外的存在两个脚本文件，其中包含了一个关键恶意URL：hxxp://fateh.aba.ae/xyzx.zip，该地址目前已经失效，通过对海量样本进行筛选挖掘，捕获到该文件。

[![](https://p5.ssl.qhimg.com/t01dd9e26edd8deced6.png)](https://p5.ssl.qhimg.com/t01dd9e26edd8deced6.png)

图3.12 自解压参数

[![](https://p1.ssl.qhimg.com/t0182ee746c9d1771cc.png)](https://p1.ssl.qhimg.com/t0182ee746c9d1771cc.png)

图3.13 down2.js

**4.1   xyzx.zip分析**
<td valign="top">项</td><td valign="top">值</td>
<td valign="top">文件名</td><td valign="top">xyzx</td>
<td valign="top">文件大小</td><td valign="top">3755 KB</td>
<td valign="top">文件类型</td><td valign="top">JavaScript 文件</td>
<td valign="top">MD5</td><td valign="top">1D3E3E419B174B2C52C7A5485AAAB7E4</td>
<td valign="top">加载方式</td><td valign="top">SFX调用mstha启动</td>

表3.2 xyzx.zip样本摘要

与其他脚本相比，该脚本十分庞大，并且执行流程更为复杂，经过多次循环解密后得到其最终后门脚本。最终程序将会设置注入的系统进程ctfmon.exe、释放路径（%temp%）、执行程序（Wscript）等。

[![](https://p2.ssl.qhimg.com/t01dfad4b6d83606b91.png)](https://p2.ssl.qhimg.com/t01dfad4b6d83606b91.png)

图3.14 xyzx.js初始化部分

然后该程序将会在temp路径下创建IMG.DB文件，并调用regsvr32程序对其注册：

[![](https://p4.ssl.qhimg.com/t01c10c6e5bb0f87bb6.png)](https://p4.ssl.qhimg.com/t01c10c6e5bb0f87bb6.png)

图3.15 调用部分

通过对该文件的分析我们了解到该文件实为DynamicWrapperX文件，该文件由Yuri Popov于2008年编写[5]，可以帮助脚本语言调用Windows API从而完成更多操作：

[![](https://p4.ssl.qhimg.com/t01481c9b393ca3a92a.png)](https://p4.ssl.qhimg.com/t01481c9b393ca3a92a.png)

图3.16 IMG.DB注册信息

[![](https://p0.ssl.qhimg.com/t0112d9da3eebd7699a.png)](https://p0.ssl.qhimg.com/t0112d9da3eebd7699a.png)

图3.17 DynamicWrapperX

在后续的代码中声明了CallWindowProcW和VirtualAll函数，也表明了其对该DLL的用法：

[![](https://p5.ssl.qhimg.com/t01ecdb05aa7f116727.png)](https://p5.ssl.qhimg.com/t01ecdb05aa7f116727.png)

图3.18 xyzx函数声明

脚本两次调用VirtualAlloc函数shellcode写入内存，并在内存中声明CreatePorcessW、SetThreadContext等函数用作进程注入，最后调用CallWindowProcW函数跳转到第一个参数的Shellcode处继续执行程序：

[![](https://p5.ssl.qhimg.com/t0169e5759ec5a23c10.png)](https://p5.ssl.qhimg.com/t0169e5759ec5a23c10.png)

图3.19 第一次VirtualAlloc中的内存

[![](https://p1.ssl.qhimg.com/t0118642fab96a76c64.png)](https://p1.ssl.qhimg.com/t0118642fab96a76c64.png)

图3.20 执行CallWindowProcW函数跳转至shellcode

在对该手法溯源过程中我们发现了相关报告[6]，其描述的攻击手法与该样本完全一致，都使用了H-Worm的“Beta”版本；此外文中提到的组织的整体攻击流程和目标与本次活动高度一致：中东、SFX、H-worm 。这些特点都为我们后续的溯源过程提供了佐证。

[![](https://p0.ssl.qhimg.com/t010e0c510105fea706.png)](https://p0.ssl.qhimg.com/t010e0c510105fea706.png)

图3.21 SFX攻击载荷，同样针对中东

### 5.  本次攻击活动规律总结
<td valign="top"></td><td valign="top">初始调用程序</td><td valign="top">后续调用程序</td><td valign="top">脚本语言</td><td valign="top">落地方式</td>
<td valign="top">第一阶段</td><td valign="top">wscript</td><td valign="top">wscript</td><td valign="top">js内嵌Vbs</td><td valign="top">压缩包释放脚本</td>
<td valign="top">第二阶段</td><td valign="top">mstha</td><td valign="top">wscript</td><td valign="top">Vbs</td><td valign="top">启动ink访问URL</td>
<td valign="top">第三阶段</td><td valign="top">mstha</td><td valign="top">powershell</td><td valign="top">JS内嵌Vbs</td><td valign="top">mstha访问URL</td>

表3.3 攻击武器特征

## 四、攻击组织溯源分析

### 1.  诱饵文档针对性

该组织的恶意载荷中都会包含一个单纯的诱饵，形式为文档或图片，而且其标题和内容都极具吸引力，且针对对象广泛：

[![](https://p2.ssl.qhimg.com/t01ae64897628b65aa2.png)](https://p2.ssl.qhimg.com/t01ae64897628b65aa2.png)

图4.1 诱饵文档一：巴勒斯坦人民斗争阵线

[![](https://p2.ssl.qhimg.com/t01128f0e4dd841db0f.png)](https://p2.ssl.qhimg.com/t01128f0e4dd841db0f.png)

图4.2 诱饵文档二：哈马斯问题

[![](https://p5.ssl.qhimg.com/t01540a4df796565bfd.png)](https://p5.ssl.qhimg.com/t01540a4df796565bfd.png)

图4.3 诱饵文档三：埃及问题

### 2.  诱饵文档可能针对的目标
<td valign="top">地区</td>
<td valign="top">阿拉伯国家</td>
<td valign="top">加沙地区</td>
<td valign="top">北非</td>
<td valign="top">国家</td>
<td valign="top">埃及</td>
<td valign="top">巴勒斯坦</td>
<td valign="top">组织/人群</td>
<td valign="top">巴勒斯坦解放组织</td>
<td valign="top">法塔赫</td>
<td valign="top">巴勒斯坦人民斗争阵线（PSF）</td>
<td valign="top">关注哈马斯的组织或人员</td>

### 3.  诱饵文档作者信息
<td valign="top">作者名</td><td valign="top">出现频次</td>
<td valign="top">hh4</td><td valign="top">6次</td>
<td valign="top">kk</td><td valign="top">1次</td>
<td valign="top">admin</td><td valign="top">1次</td>
<td valign="top">Hotmail support</td><td valign="top">1次</td>
<td valign="top">Canon MF8000C Series （佳能扫描设备）</td><td valign="top">1次</td>

表4.1 诱饵文档作者信息统计

### 4.  工作时区分析

通过对样本信息进行汇总，我们获取了一定数量的样本时间信息，后续对其归类发现该组织主要工作时间集中在北京时间UTC +8的（13:00—20:00）内，按照正常作息时间（早八晚五），基本可以确定此次攻击来自于（UTC +2—UTC+3）时区内：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016952c392b318393a.png)

图4.4 样本时间戳汇总

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010011f401004a6870.png)

图4.5 世界时区

### 5.  域名相似性

根据本次活动相关的域名，我们也总结出了一定的规律：一方面该组织通常租用一些小型运营商的云主机作为回连域名，从而很好的保障组织的安全性；另一方面，该组织的云主机名一般命名为“国家 +news”，伪装成主流新闻媒体网址，从而误导受害者。
<td valign="top">域名</td><td valign="top">疑似意义</td><td valign="top">所属区域</td>
<td valign="top">adamnews.for.ug</td><td valign="top">adam新闻</td><td valign="top">ug  乌干达</td>
<td valign="top">martnews.aba.ae</td><td valign="top">尼日利亚新闻</td><td valign="top">ae  阿联酋</td>
<td valign="top">fateh.aba.ae</td><td valign="top">法塔赫</td><td valign="top">ae  阿联酋</td>
<td valign="top">israanews.zz.com.ve</td><td valign="top">伊斯兰新闻</td><td valign="top">ve  委内瑞拉</td>

表4.2域名特征

基于以上线索结合大量数据资料的搜集整理，关联到一个频繁活跃在中东数年之久的APT组织：MoonLight，该组织曾使用的域名也具有上述规律且所有攻击手法都与该批次攻击活动相似：

[![](https://p5.ssl.qhimg.com/t01dcd0123e5b6c36f0.png)](https://p5.ssl.qhimg.com/t01dcd0123e5b6c36f0.png)

图4.6相似的域名规律

除此之外，在近期捕获的样本中，我们还发现了一份与MoonLight组织早期所使用的高度相似的诱饵文档。以上内容表现出太多的相似之处，我们不愿意相信这都是巧合，因此我们判断该批次攻击活动仍是MoonLight组织所为。

[![](https://p5.ssl.qhimg.com/t01fbb8d0bba343527f.png)](https://p5.ssl.qhimg.com/t01fbb8d0bba343527f.png)

图4.7 相似的诱饵文档

## 五、总结

阿拉伯古书中曾记载：“人间若有天堂，大马士革必在其中；天堂若在天空，大马士革必与之齐名。”而反观叙利亚的现状，或许说是“人间炼狱”也不为过，而这只是如今中东复杂局势下的一个小小缩影：宗教差异、政权斗争、大国势力干预等多方因素早已让曾经的富庶之地变得千疮百孔、人们颠沛流离，而网络空间攻击的到来更无异于雪上加霜。针对MoonLight组织发动的大规模网络攻击所用的武器及网络基础设施，我们予以分析研判形成此报告。

近期多个安全厂商发布了定性为“拍拍熊”组织的相关活动报告，其所发布的公开报告并未对攻击组织研判过程予以精确呈现。为了追寻“拍拍熊”的最初来源，我们只发现了某twitter用户的评论，而该用户也仅仅使用了“maybe”字样。

[![](https://p2.ssl.qhimg.com/t01dd92d5c20a9c8ee6.png)](https://p2.ssl.qhimg.com/t01dd92d5c20a9c8ee6.png)

图5.1 APT-C-37引用来源

难题的答案或许只有一个，但是问题的选项或许可以由一百种。。我们不怕犯错，也不怕被批评，只希望能发出我们的声音，因为这将记录并证明我们的思考。在此也希望广大奋斗在网络安全一线战场的同志们能够坚定信念，不停探索，不忘初心。



## 六、参考文献

[1] https://news.softpedia.com/news/moonlight-apt-uses-h-worm-backdoor-to-spy-on-middle-eastern-targets-509667.shtml

[2]   https://securelist.com/gaza-cybergang-group1-operation-sneakypastes/90068/

[3]   http://www.sohu.com/a/252565992_100166177

[4]   https://www.fireeye.com/blog/threat-research/2013/09/now-you-see-me-h-worm-by-houdini.html

[5]   https://www.script-coding.com/dynwrapx_eng.html

[6]   https://www.vectra.ai/blogpost/moonlight-middle-east-targeted-attacks



## 七、IOCs
- MD5
75ea74251fa57750681c8e6f99696b1b

d38592133501622f7a649a2b16d0d1d6

74ef1c5905200ea664a603a67554422b

9130aa7170a3663cd781010c7261171d

0992b87c510d4cd135e02e432fcb492b

e2448384afff94f2cc825d0a6c285e35

bef000aa7ccfd79b76a645ed60462ed1

bf14b74f212cf642c83a34f633732b5d

95194b04018a200d1413f501ff31ecf1

6e62856152eb198b457487e1eed94d76

4fa306739fd3ecc75b0ee202a614061d
- C&amp;C
hxxp://adamnews.for.ug/2020

hxxp://fateh.aba.ae/xyzx.zip

hxxp://fateh.aba.ae/abc.zip

hxxp://martnews.aba.ae/linkshw.txt

hxxp://192.119.111.4/xx/dv

hxxp://192.119.111.4/xx/f_Skoifa.vbs

hxxp://adamnews.for.ug/hwdownhww

hxxp://israanews.zz.com.ve/cr.zip

hxxp://72.21.245.117/files/hw.zip.zip

hxxp://192.119.111.4/xx/me325noew.zip

hxxp://192.119.111.4/xx/f_Skoifa.vbs?/

hxxp://192.119.111.4:4587/IS-enum-FAF

hxxp://192.119.111.4:4587/IS-enum-Driver

hxxp://192.119.111.4:4587/is-ready

hxxp://192.119.111.4/xx/

hxxp://mslove.mypressonline.com/linkshw.txt

new2019.mine.nu:4422

webhoptest.webhop.info:4433

mmksba100.linkpc.net/is-ready

mmksba100.linkpc.net:4424/is-ready

israanews.zz.com.ve/hw.zip.zip

mmksba.dyndns.org:4455/is-ready

adamnews.for.ug/303030.zip

94.102.56.143:22

192.119.111.4:4587

192.119.111.4:4521

72.21.245.117

85.17.26.65

### <a name="_Toc25848112"></a>附录一：关于奇安信APT实验室

奇安信APT实验室作为一支专注于国家级网络对抗的内部安全研究团队，长期耕植于APT现场应急取证回溯分析、攻击方组织定性、国家级APT攻击组织背景溯源等方向。此次借助威胁情报平台首次对外发声，希望有志之士加入我们的研究团队，携手服务于国家网络安全事业。也欢迎相关业务人员进行交流指导，共同提升APT领域的分析挖掘及背景溯源能力。
