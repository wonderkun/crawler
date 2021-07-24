> 原文链接: https://www.anquanke.com//post/id/200429 


# 刺向巴勒斯坦的致命毒针——双尾蝎 APT 组织的攻击活动分析与总结


                                阅读量   
                                **641562**
                            
                        |
                        
                                                                                    



## [![](https://p1.ssl.qhimg.com/t011035d66cda9ef048.png)](https://p1.ssl.qhimg.com/t011035d66cda9ef048.png)

## 

## 一.前言

**双尾蝎**APT组织(又名: APT-C-23 ),该组织从 2016 年 5 月开始就一直对巴勒斯坦教育机构、军事机构等重要领域展开了有组织、有计划、有针对性的长时间不间断攻击.其在2017年的时候其攻击活动被360企业    安全进行了披露,并且其主要的攻击区域为中东,其中以色列与巴勒斯坦更受该组织的青睐。

攻击平台主要包括 Windows 与Android :

其中针对windows 的平台,其比较常见的手法有投放带有” *.exe “或” *.scr “文件后缀的**释放者**文件,在目标用户打开后释放对应的诱饵文档,并且释放下一步的**侦查者****(Recon)**.持久存在的方式也不唯一,一般    通过写入注册表启动项以及释放指向持久化远控的快捷方式到自启动文件夹下.其侦查者会收集当前机器  的相关信息包含(**系统版本****,****计算名****,****杀毒软件信息****,****当前文件所在路径****,****恶意软件当前版本**),以及其解析   C2 的回显指令,并执行.比如:**远程****shell,****截屏和文件下载**。

同时根据别的安全厂商的报告,我们也得知该组织拥有于攻击Android  平台的组件,拥有**定位、短信拦截、电话录音等，并且还会收集文档、图片、联系人、短信等情报信息；****PC ****端后门程序功能包括收集用户信息上传到指定服务器**的功能、远程下载文件能力.

近日check point 安全厂商披露了该组织自导自演,给以色列士兵手上安装恶意软件的攻击活动.可以从中看出该团伙的攻击设计之巧妙,准备之充分。但最后结果还是被以色列给反制了一波…………

Gcow安全团队**追影小组**于 2019.12 月初开始监测到了**双尾蝎**APT组织通过投递带有诱饵文件的相关可执行文件针对**巴勒斯坦**的部门  进行了相应的攻击活动,这些诱饵文件涉及教育,科技,政治等方面的内容,其攻击活动一直持续到了 2020.2 月底.**追影小组**对该组织进行了一定时间的追踪.遂写成此报告还请各位看官欣赏.



## 二.样本信息介绍以及分析

### 1. 样本信息介绍

在本次**双尾蝎**APT组织针对**巴勒斯坦**的活动中,Gcow安全团队**追影小组**一共捕获了 14 个样本,均为

windows 样本,其中 12 个样本是释放诱饵文档的可执行文件, 2 个样本是带有恶意宏的诱饵文档

[![](https://p5.ssl.qhimg.com/t01de531472e43e3517.png)](https://p5.ssl.qhimg.com/t01de531472e43e3517.png)

在这 12 个可执行文件样本中,有 7 个样本伪装成pdf 文档文件,有 1 个样本伪装为word 文档文件,有 2 个样本伪装为rar 压缩文件.有 2 个样本伪装成mp3 , mp4 音频文件

[![](https://p0.ssl.qhimg.com/t01cc1aec0c489a3c23.png)](https://p0.ssl.qhimg.com/t01cc1aec0c489a3c23.png)

在这 14 个Windows 恶意样本中,其诱饵文档的题材,政治类的样本数量有 9 个,教育类的样本数量有 1 个,科研类的样本数量有 1 个,未知类的样本数量有 3 个(**注意****:****未知指得是其诱饵文档出现错误无法打开或者其内容属于无关内容**)

[![](https://p3.ssl.qhimg.com/t010b872104ae230a3f.png)](https://p3.ssl.qhimg.com/t010b872104ae230a3f.png)

现在各位看官应该对这批**双尾蝎**组织针对**巴勒斯坦**的攻击活动有了一个大概的认识,但是由于这批样本之  中有一些话题是以色列和巴勒斯坦共有的,这里Gcow 安全团队**追影小组**持该组织主要是攻击**巴勒斯坦**的观点,若各位看官有更多的证据,欢迎联系我们团队.**注意****:****这里只是一家之言****,****还请各位看官须知**。

那下面**追影小组**将以一个恶意样本进行详细分析,其他样本采取略写的形式向各位看官描述此次攻击活  动。**注意****:****因为其他样本的主要逻辑是相同的****,****所以没有必要枉费笔墨**

### 1. 样本分析

**(1).Deﬁne the Internet in government institutions**

**a. 样本信息**

[![](https://p0.ssl.qhimg.com/t01a82f31b6ba1393a5.png)](https://p0.ssl.qhimg.com/t01a82f31b6ba1393a5.png)

[![](https://p2.ssl.qhimg.com/t01d5d1cb35c52cb822.png)](https://p2.ssl.qhimg.com/t01d5d1cb35c52cb822.png)**b.样本分析**

通过对样本的分析我们得知了该样本是兼具**释放者****(Dropper)**与**下载者****(Downloader)**的功能,其**释放者**

**(Dropper)**主要是用以释放诱饵

文档加以伪装以及将自身拷贝到**%ProgramData%**目录下,并且生成执行该文件的快捷方式并且释放于    自启动文件夹下,而**下载者****(Downloader)**

部分主要是通过进行信息收集以及等待C2给予的回显,主要功能有:**远程****shell,****文件下载****,****屏幕截屏**

#### i. 释放者(Dropper)部分:

通过<u>SizeOfResource</u> 函数通过获取资源的地址计算该资源的长度

[![](https://p0.ssl.qhimg.com/t01d99c0afbdba0600b.png)](https://p0.ssl.qhimg.com/t01d99c0afbdba0600b.png)

通过CreateFile 函数在**%temp%**目录下释放诱饵PDF文档**Deﬁne the Internet in government institutions.pdf**

[![](https://p5.ssl.qhimg.com/t01eaf32227bc688f26.png)](https://p5.ssl.qhimg.com/t01eaf32227bc688f26.png)

通过WriteFile 函数将PDF源数据写入创建的诱饵文档内

[![](https://p1.ssl.qhimg.com/t01f008a8dcfd0f03b0.png)](https://p1.ssl.qhimg.com/t01f008a8dcfd0f03b0.png)

[![](https://p3.ssl.qhimg.com/t017c8e9f6a168f4c38.png)](https://p3.ssl.qhimg.com/t017c8e9f6a168f4c38.png)

通过ShellExecute 函数打开PDF诱饵文档,以免引起目标怀疑

[![](https://p4.ssl.qhimg.com/t01235dda6f09b04187.png)](https://p4.ssl.qhimg.com/t01235dda6f09b04187.png)

其PDF诱饵文档内容如图,主要关于其**使用互联网**的**政治类**题材样本,推测应该是**针对政府部门**的活动

[![](https://p3.ssl.qhimg.com/t01b181f4897ecd904b.png)](https://p3.ssl.qhimg.com/t01b181f4897ecd904b.png)

同时利用CopyFileA 函数将自身拷贝到%ProgramData% 目录下并且重命名为SyncDownOptzHostProc.exe

[![](https://p1.ssl.qhimg.com/t01d0ef463aba1008ef.png)](https://p1.ssl.qhimg.com/t01d0ef463aba1008ef.png)

利用CreateFilewW 函数在自启动文件夹下创造指向%ProgramData%\SyncDownOptzHostProc.exe 的快捷方式SyncDownOptzHostProc.lnk

[![](https://p5.ssl.qhimg.com/t01d964603877dcbca9.png)](https://p5.ssl.qhimg.com/t01d964603877dcbca9.png)

[![](https://p2.ssl.qhimg.com/t01719a06f9b23c97fc.png)](https://p2.ssl.qhimg.com/t01719a06f9b23c97fc.png)

**i.  下载者(Downloader)部分:**

通过CreateFile 函数创造%ProgramData%\GUID.bin 文件,内部写入对应本机的GUID .当软件再次运行的时候检查自身是否位于%ProgramData% 文件夹下,若不是则释放pdf文档。若是,则释放lnk 到自启动文件夹

[![](https://p0.ssl.qhimg.com/t0148d3db5c736ba0dd.png)](https://p0.ssl.qhimg.com/t0148d3db5c736ba0dd.png)

[![](https://p0.ssl.qhimg.com/t01a96c537c9c4073b4.png)](https://p0.ssl.qhimg.com/t01a96c537c9c4073b4.png)

**①.信息收集**

1.收集**当前用户名**以及**当前计算机名称**,并且读取 GUID.bin 文件中的**GUID****码**

[![](https://p2.ssl.qhimg.com/t01158ab65afe036ec2.png)](https://p2.ssl.qhimg.com/t01158ab65afe036ec2.png)

再以如下格式拼接信息

```
当前计算机名称_当前用户名_GUID码
```

[![](https://p5.ssl.qhimg.com/t01ecf09d5a1c5f07cd.png)](https://p5.ssl.qhimg.com/t01ecf09d5a1c5f07cd.png)

将这些拼接好的信息利用base64进行编码,组合成cname 报文.

**2.通过 GetVersion 函数收集当前系统版本**

[![](https://p5.ssl.qhimg.com/t01460ede492d245068.png)](https://p5.ssl.qhimg.com/t01460ede492d245068.png)

并且将其结果通过Base64进行编码,组成 osversion 报文

[![](https://p5.ssl.qhimg.com/t01faca535608e25fc5.png)](https://p5.ssl.qhimg.com/t01faca535608e25fc5.png)

通过 WMI 查询本地安装的安全软件 被侦查的安全软件包括 360 , F-secure , Corporate , Bitdefender[![](https://p1.ssl.qhimg.com/t01c72c68944493d1f4.png)](https://p1.ssl.qhimg.com/t01c72c68944493d1f4.png)[![](https://p2.ssl.qhimg.com/t01985cba1de8491e6b.png)](https://p2.ssl.qhimg.com/t01985cba1de8491e6b.png)

如果存在的话,获取结果组成av 报文

3. 通过 GetModuleFile 函数获取当前文件的运行路径

[![](https://p0.ssl.qhimg.com/t018d532820e1eb814d.png)](https://p0.ssl.qhimg.com/t018d532820e1eb814d.png)

将当前程序运行路径信息通过base64编码组成aname 报文

[![](https://p2.ssl.qhimg.com/t011fb1675bbe7ff5ac.png)](https://p2.ssl.qhimg.com/t011fb1675bbe7ff5ac.png)4.后门版本号 ver 报文,本次活动的后门版本号为:**5.HXD.zz.1201**

[![](https://p1.ssl.qhimg.com/t010c95e94c2d0aa207.png)](https://p1.ssl.qhimg.com/t010c95e94c2d0aa207.png)

将这些信息按照如下方式拼接好后,通过Send 方式向URL地址 [htp://nicoledotson.icu/debby/weatherford/yportysnr](htp://nicoledotson.icu/debby/weatherford/yportysnr) 发送上线报文

```
cname=&amp;av=&amp;osversion=&amp;aname=&amp;ver=
```

[![](https://p5.ssl.qhimg.com/t01f4bf57b133f0efa6.png)](https://p5.ssl.qhimg.com/t01f4bf57b133f0efa6.png)[![](https://p5.ssl.qhimg.com/t0119324be1e8cc41fc.png)](https://p5.ssl.qhimg.com/t0119324be1e8cc41fc.png)

**②.获取指令 **

通过[http://nicoledotson.icu/debby/weatherford/ekspertyza](http://nicoledotson.icu/debby/weatherford/ekspertyza) URL获取功能命令(功能为截屏, 远程shell,以及下载文件)

[![](https://p0.ssl.qhimg.com/t018bb1340a9747cb52.png)](https://p0.ssl.qhimg.com/t018bb1340a9747cb52.png)

**③.发送屏幕快照**

向URL地址 [http://nicoledotson.icu/debby/weatherford/Zavantazhyty](http://nicoledotson.icu/debby/weatherford/Zavantazhyty) 发送截屏 截取屏幕快照函数

[![](https://p2.ssl.qhimg.com/t014e3d64449b184a5c.png)](https://p2.ssl.qhimg.com/t014e3d64449b184a5c.png)

** ④.远程shell**

远程shell主要代码

[![](https://p3.ssl.qhimg.com/t01fc1f36a6597edeff.png)](https://p3.ssl.qhimg.com/t01fc1f36a6597edeff.png)[![](https://p1.ssl.qhimg.com/t01ff4c01db469c49ad.png)](https://p1.ssl.qhimg.com/t01ff4c01db469c49ad.png)

**⑤.文件下载**

下载文件,推测应该先另存为base64编码的txt文件再解密另存为为exe文件,最后删除txt文件.由于环境问题我们并没有捕获后续的代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f4b0f7d485400366.png)[![](https://p3.ssl.qhimg.com/t01060f55f7b578e2ab.png)](https://p3.ssl.qhimg.com/t01060f55f7b578e2ab.png)

**⑥.删除命令**

通过URL [http://nicoledotson.icu/debby/weatherford/vydalyty](http://nicoledotson.icu/debby/weatherford/vydalyty) 获取删除指令

[![](https://p2.ssl.qhimg.com/t018644c1572a7f452b.png)](https://p2.ssl.qhimg.com/t018644c1572a7f452b.png)

此外我们还关联到一个与之相似的样本,诱饵文档与之相同故不再赘述

[![](https://p4.ssl.qhimg.com/t016326db64d479fa7c.png)](https://p4.ssl.qhimg.com/t016326db64d479fa7c.png)

(2).Employee-entitlements-2020

**a. 样本信息**

[![](https://p5.ssl.qhimg.com/t01fbfc04bf58652018.png)](https://p5.ssl.qhimg.com/t01fbfc04bf58652018.png)[![](https://p1.ssl.qhimg.com/t01794da2a83a6dccb9.png)](https://p1.ssl.qhimg.com/t01794da2a83a6dccb9.png)

该样本属于包含恶意**宏**的文档,我们打开可以看到其内容关于**财政部关于文职和军事雇员福利的声明**,属  于涉及**政治类**的题材

[![](https://p2.ssl.qhimg.com/t013db61908a0f73f00.png)](https://p2.ssl.qhimg.com/t013db61908a0f73f00.png)

**b. 样本分析**

通过使用olevba dump出其包含的恶意宏代码(如下图所示:) 其主要逻辑为:下载该URL [http://linda-callaghan.icu/Minkowski/brown](http://linda-callaghan.icu/Minkowski/brown) 上的内容到本台机器的%ProgramData%\IntegratedOffice.txt (此时并不是其后门,而且后门文件的base64 编码后的结果)。

通过读取IntegratedOffice.txt 的所有内容将其解码后,把数据流写 入%ProgramData%\IntegratedOffice.exe 中,并且延迟运行%ProgramData%\IntegratedOffice.exe 删除%ProgramData%\IntegratedOffice.txt

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f4d54aea21aed3d2.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bf987f525a79fbe9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b23607c846d7a45f.png)

该样本属于上一个样本中的**下载者****(Downloader)**部分,其还是通过创建 GUID .bin标记感染机器 [![](https://p3.ssl.qhimg.com/t01ad0e575d73ab566d.png)](https://p3.ssl.qhimg.com/t01ad0e575d73ab566d.png)

并且创建指向自身的快捷方式于自启动文件夹中

[![](https://p0.ssl.qhimg.com/t01663d4885a25fb549.png)](https://p0.ssl.qhimg.com/t01663d4885a25fb549.png)

**(3).Brochure-Jerusalem_26082019_pdf**

#### a. 样本信息

[![](https://p0.ssl.qhimg.com/t01b0ed4c58894d05b6.png)](https://p0.ssl.qhimg.com/t01b0ed4c58894d05b6.png)

[![](https://p2.ssl.qhimg.com/t012abe9acb8026d55a.png)](https://p2.ssl.qhimg.com/t012abe9acb8026d55a.png)

通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个PDF 文件[![](https://p4.ssl.qhimg.com/t014f4166368a43d285.png)](https://p4.ssl.qhimg.com/t014f4166368a43d285.png)

通过CreateFile 函数将文件源数据写入%Temp%\Brochure-Jerusalem_26082019.pdf (诱饵文件)中

[![](https://p3.ssl.qhimg.com/t01f8613ceaf240aaba.png)](https://p3.ssl.qhimg.com/t01f8613ceaf240aaba.png)

通过ShellExecute 函数将%Temp%\Brochure-Jerusalem_26082019.pdf 打开

[![](https://p1.ssl.qhimg.com/t01fea5ab048f97f31d.png)](https://p1.ssl.qhimg.com/t01fea5ab048f97f31d.png)

[![](https://p5.ssl.qhimg.com/t01d94ee3083c62ad0f.png)](https://p5.ssl.qhimg.com/t01d94ee3083c62ad0f.png)

之后的行为就和之前的如出一辙了,在此就不必多费笔墨。

**(4).Congratulations_Jan-7_78348966_pdf  ****a.****样本信息**

[![](https://p1.ssl.qhimg.com/t01fa5410c3a76029f7.png)](https://p1.ssl.qhimg.com/t01fa5410c3a76029f7.png)

**b. 样本分析**

通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个PDF 文件

[![](https://p0.ssl.qhimg.com/t010a7c22d3636f42ce.png)](https://p0.ssl.qhimg.com/t010a7c22d3636f42ce.png)

通过CreateFile 函数将文件源数据写入%Temp%\Congratulations_Jan-7.pdf (诱饵文件)中 [![](https://p0.ssl.qhimg.com/t012b1e21077edaf19a.png)](https://p0.ssl.qhimg.com/t012b1e21077edaf19a.png)

通过ShellExecute 函数将%Temp%\Congratulations_Jan-7.pdf 打开

[![](https://p1.ssl.qhimg.com/t01244385bf0b51ec8c.png)](https://p1.ssl.qhimg.com/t01244385bf0b51ec8c.png)

该样本关于**耶路撒冷归属**的话题,属于**政治类**诱饵文档

[![](https://p5.ssl.qhimg.com/t01d3594c0019babbfb.png)](https://p5.ssl.qhimg.com/t01d3594c0019babbfb.png)

之后的行为就和之前的如出一辙了,在此就不必多费笔墨。

**(5).Directory of Government  Services_pdf ****a.****样本信息**

[![](https://p5.ssl.qhimg.com/t018798f3243ba84191.png)](https://p5.ssl.qhimg.com/t018798f3243ba84191.png)[![](https://p3.ssl.qhimg.com/t015c236b39c28947da.png)](https://p3.ssl.qhimg.com/t015c236b39c28947da.png)

**b.样本分析**

通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个PDF 文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f6bc7977b579751f.png)

通过CreateFile 函数将文件源数据写入%Temp%\Directory of Government Services.pdf (诱饵文件)中[![](https://p0.ssl.qhimg.com/t014af52c2d5afa03e9.png)](https://p0.ssl.qhimg.com/t014af52c2d5afa03e9.png)

通过ShellExecute 函数将%Temp%\Directory of Government Services.pdf 打开

[![](https://p2.ssl.qhimg.com/t018dfa95b2196b1ec1.png)](https://p2.ssl.qhimg.com/t018dfa95b2196b1ec1.png)

该样本关于**政府部门秘书处**的话题,属于**政治类**诱饵文档

[![](https://p1.ssl.qhimg.com/t0133144f4f41872355.png)](https://p1.ssl.qhimg.com/t0133144f4f41872355.png)

诱饵内容对应的官网图

[![](https://p3.ssl.qhimg.com/t01c1f43d4262c1473f.png)](https://p3.ssl.qhimg.com/t01c1f43d4262c1473f.png)

**(6).entelaqa_hamas_32_1412_847403867_rar**

**a. 样本信息**

[![](https://p3.ssl.qhimg.com/t015853524f83ff8794.png)](https://p3.ssl.qhimg.com/t015853524f83ff8794.png)[![](https://p3.ssl.qhimg.com/t01f14262fb51499ea5.png)](https://p3.ssl.qhimg.com/t01f14262fb51499ea5.png)**b. 样本分析**通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个RAR 文件

[![](https://p2.ssl.qhimg.com/t012d24415667d6421a.png)](https://p2.ssl.qhimg.com/t012d24415667d6421a.png)

通过CreateFile 函数将文件源数据写入%Temp%\Entelaqa32.rar (诱饵文件)中

[![](https://p2.ssl.qhimg.com/t01d958a5aa977a7172.png)](https://p2.ssl.qhimg.com/t01d958a5aa977a7172.png)  通过ShellExecute 函数将%Temp%\Entelaqa32.rar 打开

[![](https://p0.ssl.qhimg.com/t0173d9c36af29a1107.png)](https://p0.ssl.qhimg.com/t0173d9c36af29a1107.png)   该样本关于哈马斯的话题,属于政治类诱饵文档

[![](https://p4.ssl.qhimg.com/t01180b74a124ba31de.png)](https://p4.ssl.qhimg.com/t01180b74a124ba31de.png)

**(7).ﬁnal_meeting_9659836_299283789235_rar**

**a. 样本信息**

[![](https://p5.ssl.qhimg.com/t015cbdaa5bcae0a8d7.png)](https://p5.ssl.qhimg.com/t015cbdaa5bcae0a8d7.png)

[![](https://p5.ssl.qhimg.com/t0120bdade760104d74.png)](https://p5.ssl.qhimg.com/t0120bdade760104d74.png)

b. 样本分析

通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个rar 文件

[![](https://p3.ssl.qhimg.com/t01ff668fd440e4e790.png)](https://p3.ssl.qhimg.com/t01ff668fd440e4e790.png)

通过CreateFile 函数将rar 文件源数据写入%Temp%\jalsa.rar (诱饵文件)中

[![](https://p2.ssl.qhimg.com/t01b6c2b4ee0450a755.png)](https://p2.ssl.qhimg.com/t01b6c2b4ee0450a755.png)

通过ShellExecute 函数将%Temp%\jalsa.rar 打开

[![](https://p5.ssl.qhimg.com/t01ef8119d3d2646aa1.png)](https://p5.ssl.qhimg.com/t01ef8119d3d2646aa1.png)

其诱饵文件的内容与**第十二届亚洲会议**有关,其主体是**无条件支持巴勒斯坦**,可见可能是利用**亚洲会议**针  对**巴勒斯坦*******的活动,属于**政治类**题材的诱饵样本

[![](https://p5.ssl.qhimg.com/t017a6261d5b4f88c7d.png)](https://p5.ssl.qhimg.com/t017a6261d5b4f88c7d.png)

之后的行为就和之前的如出一辙了,在此就不必多费笔墨

**(8).Meeting Agenda_pdf**

**a. 样本信息**

[![](https://p4.ssl.qhimg.com/t010d5db50426c3102a.png)](https://p4.ssl.qhimg.com/t010d5db50426c3102a.png)

[![](https://p5.ssl.qhimg.com/t01a9b4f596153c10ea.png)](https://p5.ssl.qhimg.com/t01a9b4f596153c10ea.png)

**a. 样本分析**

通过CreateFile 函数将文件源数据写入%Temp%\Meeting Agenda.pdf (诱饵文件)中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011dd2493e38c634da.png)通过ShellExecute 函数将%Temp%\Meeting Agenda.pdf 打开

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01eefc0d8b75d479ab.png)

但由于其塞入数据的错误导致该Meeting Agenda.pdf 文件无法正常打开故此将该样本归因到未知类题材,之后的行为就和之前的如出一辙了,在此就不必多费笔墨。

**(9).Scholarships in Serbia 2019-2020_pdf**

**a. 样本信息 **

** [![](https://p3.ssl.qhimg.com/t01729869da32ca0658.png)](https://p3.ssl.qhimg.com/t01729869da32ca0658.png)[![](https://p2.ssl.qhimg.com/t010bdb8a3aa792844f.png)](https://p2.ssl.qhimg.com/t010bdb8a3aa792844f.png)**

**b. 样本分析**

通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个PDF 文件

[![](https://p1.ssl.qhimg.com/t01aad3318b86fedaae.png)](https://p1.ssl.qhimg.com/t01aad3318b86fedaae.png) 通过CreateFile 函数将文件源数据写入%Temp%\Scholarships in Serbia 2019-2020.pdf (诱饵文件)中

[![](https://p0.ssl.qhimg.com/t013d33f468a44dc494.png)](https://p0.ssl.qhimg.com/t013d33f468a44dc494.png)

通过ShellExecute 函数将%Temp%\Scholarships in Serbia 2019-2020.pdf 打开

[![](https://p0.ssl.qhimg.com/t0144bebac773d32e22.png)](https://p0.ssl.qhimg.com/t0144bebac773d32e22.png)  该样本关于巴勒斯坦在塞尔维亚共和国奖学金的话题,属于教育类诱饵文档

[![](https://p0.ssl.qhimg.com/t0108c89ee3fe4dce66.png)](https://p0.ssl.qhimg.com/t0108c89ee3fe4dce66.png)

诱饵内容对应的官网图片

[![](https://p5.ssl.qhimg.com/t010f094dc4f02bf410.png)](https://p5.ssl.qhimg.com/t010f094dc4f02bf410.png)

之后的行为就和之前的如出一辙了,在此就不必多费笔墨。 ﺗﻘرﯾر ﺣول أھم اﻟﻣﺳﺗﺟدات

**(10).347678363764_ **

**a. 样本信息**

[![](https://p5.ssl.qhimg.com/t01c92176e2789896f3.png)](https://p5.ssl.qhimg.com/t01c92176e2789896f3.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011297902d90560358.png)

** b. 样本分析**

通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个docx 文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012f4c1a6e338e8845.png)

通过CreateFile 函数将docx 文件源数据写入%Temp%\daily_report.docx (诱饵文件)中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01da40ede991b58744.png)

通过ShellExecute 函数将%Temp%\daily_report.docx 打开

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0137dceaa802ed1204.png)

从诱饵样本中的内容我们可以看出其关于巴勒斯坦态势的问题,属于政治类诱饵样本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011a77dd36cbb69cf5.png) 之后的行为就和之前的如出一辙了,在此就不必多费笔墨

**(11).asala-panet-il-music-live-892578923756-mp3 **

**a.样本信息**

[![](https://p2.ssl.qhimg.com/t013fdb2ddc73954e1a.png)](https://p2.ssl.qhimg.com/t013fdb2ddc73954e1a.png)

[![](https://p3.ssl.qhimg.com/t01c5ec276d6658362a.png)](https://p3.ssl.qhimg.com/t01c5ec276d6658362a.png)

**b.样本分析**

通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个unknown 文件

[![](https://p1.ssl.qhimg.com/t017cbcc361dab16033.png)](https://p1.ssl.qhimg.com/t017cbcc361dab16033.png) 通过CreateFile 函数将文件源数据写入%Temp%\asala.mp3 (诱饵文件)中

[![](https://p4.ssl.qhimg.com/t01122165cf83534db1.png)](https://p4.ssl.qhimg.com/t01122165cf83534db1.png)

通过ShellExecute 函数将%Temp%\asala.mp3 打开

[![](https://p0.ssl.qhimg.com/t0102a1290c65a62891.png)](https://p0.ssl.qhimg.com/t0102a1290c65a62891.png) 歌曲挺好听的,但是我们也不知道啥意思,将其归属于未知类题材样本

**(12).artisan-video-5625572889047205-9356297846-mp4**

** a. 样本信息   **

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b9db2614d1b53442.png)[![](https://p4.ssl.qhimg.com/t013f12b63f381e5ab8.png)](https://p4.ssl.qhimg.com/t013f12b63f381e5ab8.png)



** b. 样本分析**

通过FindResource 函数查找资源MYDATA ,通过下图我们可以看出该资源是一个unknown 文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b0c5dc7af5a2e3de.png) 通过CreateFile 函数将文件源数据写入%Temp%\artisan-errors.mp4 (诱饵文件)中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e403c0f69045288a.png)

通过ShellExecute 函数将%Temp%\artisan-errors.mp4 打开

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0155014d02bf3dede8.png)

该样本伪装成视频丢失的404信号,没有实际参考价值,故归入未知类题材样本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d25ac6554c0ca4db.png) 之后的行为就和之前的如出一辙了,在此就不必多费笔墨。

**(13).1اﻟﺳﯾرة اﻟذاﺗﯾﺔ ﻣﻧﺎل **

**a. 样本信息    **

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01af1e2a1e7be286d5.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ef32d15a228c20ca.png)

** b. 样本分析**

其诱饵内容关于在东耶路撒冷(巴勒斯坦)的阿布迪斯大学秘书,属于大学科研类样本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01388ff9b58b9d9b04.png)

同时其包含的恶意宏代码如图所示,由于我们并没有能成功获得下一步的载荷,故没法进行下一步的分析。不过推测其大致功能应该与上文相同

[![](https://p5.ssl.qhimg.com/t0184c635b750ee94b9.png)](https://p5.ssl.qhimg.com/t0184c635b750ee94b9.png)



## 三.组织关联与技术演进

在本次活动中,我们可以清晰的看到**双尾蝎**APT组织的攻击手段,同时Gcow 安全团队**追影小组**也对其进行了一定的组织关联,并且对其技术的演进做了一定的研究。下面我们将分为**组织关联**与**技术演进**这两部分  内容进行详细的叙述。

#### 注意:下文中的时间段仅仅为参考值,并非准确时间。由于在这一时间段内该类样本较多,故此分类。

### **1.组织关联**

**(1).****样本执行流程基本相似**

我们根据对比了从 2017 到 2020 年所有疑似属于**双尾蝎**APT组织的样本,(**注意****:****这里比对的样本主要是**

**windows****平台的可执行文件样本**).在 2017 年到 2019 年的样本中我们可以看出其先在**临时文件夹**下释放诱饵文件,再打开迷惑受害者,再将自身拷贝到%ProgramData% 下.创建指向%ProgramData%下的自拷贝恶意文件的快捷方式于自启动文件夹.本次活动与 2018 年 2019 年的活动所使用样本的流程极为相似.如下图所示.故判断为该活动属于**双尾蝎 **APT组织。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016934273a195406f1.png)

**(2).C&amp;C****中存在名人姓名的痕迹**

根据checkpoint 的报告我们得知,该组织乐于使用一些明星或者名人的名字在其C&amp;C 服务器上.左图是 checkpoint 安全厂商揭露其针对以色列士兵的活动的报告原文,我们可以看到其中含有Jim Morrison , Eliza Dollittle , Gretchen Bleiler 等名字.而右图在带有恶意宏文档的样本中,我们发现了其带有Minkowski 这个字符.通过搜索我们发现其来源于Hermann Minkowski 名字的一部分,勉强地符合了双尾蝎APT组织的特征之一.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eca43a04c24e50e6.png)

### **2.技术演进**

**(1). 在编写语言上的演进**

根据 360 的报告我们可以得知**双尾蝎**APT组织在 2016 年到 2017 年这段时间内该组织主要采用了VC 去编写载荷.再到 2017 年到 2018 年这段时间内该组织主要是以Delphi 来编写其**侦查者****(Recon)**,根据Gcow 安全团队**追影小组**的跟踪,该组织在 2018 年到 2019 年这段时间内也使用了Delphi 编写的恶意载荷。

与 2017 年到 2018 年不同的是: 2017 年到 2018 年所采用的编译器信息是:**Borland Delphi 2014XE6**。而在 2018 年到 2019 年这个时间段内采用的编辑器信息是:**Borland Delphi 2014XE7- S.10**。

同时在本次活动中该组织使用 Pascal 语言来编写载荷。可见该组织一直在不断寻求一些受众面现在越来越小的语言以逃脱杀软对其的监测。





[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a7bec0bc7d3b17da.png)

**(2). 编译时间戳的演进**

根据 360 的报告我们可以得知**双尾蝎**APT组织在 2016 年到 2018 年这个时间段中,该组织所使用的恶意

载荷的时间戳信息大部分时间集中位于北京的下午以及第二天的凌晨,属于中东地区的时间。而在 2019年 7 月份捕获的双尾蝎APT组织样本中该组织的编译戳为 2019.7.14 11:08:48 而在本次活动所捕获的 样本中我们发现该组织将编译时间戳统一改为: 1970.1.1 1:00 ,也就是置0.通过伪造时间戳以阻断安全人员的关联以及对其的地域判断



[![](https://p5.ssl.qhimg.com/t0154530fc66e8e9f81.png)](https://p5.ssl.qhimg.com/t0154530fc66e8e9f81.png)

**(3). 自拷贝方式的演进**

**双尾蝎**APT组织在 2017 年到 2019 年的活动中,擅长使用copy 命令将自身拷贝到%ProgramData% 下.而可能由于copy 指令的敏感或者已经被各大安全厂商识别。在 2019 年 7 月份的时候.该组织恢复了之前采用CopyFile windows API函数的方式将自身拷贝到%ProgramData% 下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0167cf201555774f9a.png)

**(4). 持久化方式的演进**

根据 360 的报告,我们可以得知**双尾蝎**APT组织在 2016 年到 2017 年的活动之中,主要采用的是修改注册

表添加启动项的方式进行权限的持久化存在。而根据**追影小组**的捕获的样本,我们发现在 2017 年到2018 年的这段时间内该组织使用拥有白名单Shortcut.exe 通过命令行的方式在自启动文件夹中添加指向自拷贝后的恶意文件的快捷方式。而在本次活动中,该组织则采用调用CreateFile Windows API 函数的方式在自启动文件夹中创建指向自拷贝后恶意文件的快捷方式以完成持久化存在

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014b0297fabc273e32.png)

**(5).C&amp;C报文的演进**

为了对比的方便,我们只对比**双尾蝎**APT组织 2018 年到 2019 年的上半年的活动与本次活动的C&amp;C 报文的区别。如图所示下图的左上是本次活动的样本的C&amp;C 报文,右下角的是 2018 年到 2019 年上半年活动的样本的C&amp;C 报文。通过下面所给出的解密我们可以得知两个样本所向C&amp;C 收集并发送的信息基本相同。同时值得注意的是该组织逐渐减少明文的直接发送收集到的注意而开始采用比较常见的通过Base64的方式编码后在发送。同时在ver版本中我们发现: 2018 年到 2019 年上半年的样本的后门版本号为: 1.4.2.MUSv1107 (**推测是****2018.11.07****更新的后门**);而在本次活动中后门版本号

为: 5.HXD.zz.1201 (**推测是****2019.12.01****号更新的后门**),由此可见该组织正在随着披露的增加而不断的进行后门的更迭。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b85e9652329ee1c2.png)

## 四.总结

### 1. 概述

Gcow  安全团队**追影小组**针对**双尾蝎**APT组织此次针对巴勒斯坦的活动进行了详细的分析并且通过绘制了一幅样本执行的流程图方便各位看官的理解

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014e6c7cea36414afd.png)

该组织拥有很强的攻击能力,其载荷涵盖较广(**Windows****和****Android****平台**).并且在被**以色列**进行导弹物理   打击后快速恢复其攻击能力.对巴勒斯坦地区进行了一波较为猛烈的攻势,同时我们绘制了一幅本次活动 之中样本与C&amp;C 的关系图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01738715ca1c0d40a8.png)

通过之前的分析我们发现了该组织拥有很强的技术对抗能力,并且其投放的样本一直围绕着与**巴勒斯坦**和**以色列**的敏感话题进行投放,我们对其话题关键字做了统计,方便各位看官了解

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ac5499165ccd206e.png)

### 1. 处置方案:

**删除文件**

```
%TEMP%\*.pdf(*.mp3,*.mp4,*.rar,*.doc)	[诱饵文档]
%ProgramData%\SyncDownOptzHostProc.exe [侦查者主体文件]
%ProgramData%\IntegratedOffice.exe[侦查者主体文件]
%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup\SyncDownOptzHostProc.lnk [指向侦查者主体文件的快捷方式用于权限维持]
%ProgramData%\GUID.bin [标记感染]
```

### **3.结语**

通过本次分析报告,我们相信一定给各位看官提供了一个更加充分了解该组织的机会.我们在前面分析了   该组织的技术特点以及对该组织实施攻击的攻击手法的演进进行了详细的概述。

同时在后面的部分我们  也会贴出该组织最新活动所使用样本的IOCs 供给各位感兴趣的看官交流与学习.同时我们希望各位看官如果有其他的意见欢迎向我们提出。



## 五.IOCs:

### MD5:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018117054843cb03fb.png)

### **URL:**

http[:]//linda-callaghan[.]icu/Minkowski/brown http[:]//linda-callaghan[.]icu/Minkowski/microsoft/utilities http[:]//nicoledotson[.]icu/debby/weatherford/yortysnr

http[:]//nicoledotson[.]icu/debby/weatherford/Zavantazhyty http[:]//nicoledotson[.]icu/debby/weatherford/Ekspertyza

http[:]//nicoledotson[.]icu/debby/weatherford/Vydalyty http[:]//nicoledotson[.]icu/debby/weatherford/pidnimit

### C2:

linda-callaghan[.]icu nicoledotsonp[.]icu

### 释放文件:

%TEMP%\  *.pdf(*.mp3,*.mp4,*.rar,*.doc)

%ProgramData%\SyncDownOptzHostProc.exe

%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup\SyncDownOptzHostProc.lnk

%ProgramData%\GUID.bin

%ProgramData%\IntegratedOﬃce.exe



## 六.相关链接:

<u>[https://www.freebuf.com/articles/system/129223.html](https://www.freebuf.com/articles/system/129223.html)</u>

<u>[https://research.checkpoint.com/2020/hamas-android-malware-on-idf-soldiers-this-is-how-it-hap pened/](https://research.checkpoint.com/2020/hamas-android-malware-on-idf-soldiers-this-is-how-it-happened/)</u>

<u>[https://mp.weixin.qq.com/s/Rfcr-YPIoUUvc89WFrdrnw](https://mp.weixin.qq.com/s/Rfcr-YPIoUUvc89WFrdrnw)</u>
