> 原文链接: https://www.anquanke.com//post/id/167384 


# “毒针”行动 - 针对“俄罗斯总统办所属医疗机构”发起的0day攻击


                                阅读量   
                                **208835**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01c0c38f17aad9675f.jpg)](https://p1.ssl.qhimg.com/t01c0c38f17aad9675f.jpg)

## 概述

近年来，乌克兰和俄罗斯两国之间围绕领土问题的争执不断，发生了克里米亚半岛问题、天然气争端、乌克兰东部危机等事件。伴随着两国危机事件愈演愈烈之时，在网络空间中发生的安全事件可能比现实更加激烈。2015年圣诞节期间乌克兰国家电力部门受到了APT组织的猛烈攻击，使乌克兰西部的 140 万名居民在严寒中遭遇了大停电的煎熬，城市陷入恐慌损失惨重，而相应的俄罗斯所遭受的APT攻击，外界却极少有披露。

2018年11月25日，乌俄两国又突发了“刻赤海峡”事件，乌克兰的数艘海军军舰在向刻赤海峡航行期间，与俄罗斯海军发生了激烈冲突，引发了全世界的高度关注。在2018年11月29日，“刻赤海峡”事件后稍晚时间，360高级威胁应对团队就在全球范围内第一时间发现了一起针对俄罗斯的APT攻击行动。值得注意的是此次攻击相关样本来源于乌克兰，攻击目标则指向俄罗斯总统办公室所属的医疗机构。攻击者精心准备了一份俄文内容的员工问卷文档，该文档使用了最新的Flash 0day漏洞cve-2018-15982和带有自毁功能的专属木马程序进行攻击，种种技术细节表明该APT组织不惜代价要攻下目标，但同时又十分小心谨慎。在发现攻击后，我们第一时间将0day漏洞的细节报告了Adobe官方，Adobe官方及时响应后在12月5日加急发布了新的Flash 32.0.0.101版本修复了此次的0day漏洞。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016dfcaf773befa7f5.png)

图1：漏洞文档内容

按照被攻击医疗机构的网站（[http://www.p2f.ru）](http://www.p2f.ru%29/) 介绍，该医疗机构成立于1965年，创始人是俄罗斯联邦总统办公室，是专门为俄罗斯联邦最高行政、立法、司法当局的工作人员、科学家和艺术家提供服务的专业医疗机构。由于这次攻击属于360在全球范围内的首次发现，结合被攻击目标医疗机构的职能特色，我们将此次APT攻击命名为“毒针”行动。目前我们还无法确定攻击者的动机和身份，但该医疗机构的特殊背景和服务的敏感人群，使此次攻击表现出了明确的定向性，同时攻击发生在“刻赤海峡”危机的敏感时段，也为攻击带上了一些未知的政治意图。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cfe866266b874b2c.png)

图2： 该医院机构介绍

## 攻击过程分析

攻击者通过投递rar压缩包发起攻击，打开压缩包内的诱饵文档就会中招。完整攻击流程如下：

[![](https://p3.ssl.qhimg.com/t019232a2e67c2d9ce4.png)](https://p3.ssl.qhimg.com/t019232a2e67c2d9ce4.png)

图3： 漏洞文档攻击过程

当受害者打开员工问卷文档后，将会播放Flash 0day文件。

[![](https://p4.ssl.qhimg.com/t01d562bd9ac412b69a.png)](https://p4.ssl.qhimg.com/t01d562bd9ac412b69a.png)

图4： 播放Flash 0day漏洞

触发漏洞后， winrar解压程序将会操作压缩包内文件，执行最终的PE荷载backup.exe。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018523a1b6ab1c8fbb.png)

图5： 漏洞执行进程树

## 0day漏洞分析

通过分析我们发现此次的CVE-2018-15982 0day漏洞是flash包com.adobe.tvsdk.mediacore.metadata中的一个UAF漏洞。Metadata类的setObject在将String类型（属于RCObject）的对象保存到Metadata类对象的keySet成员时，没有使用DRCWB（Deferred Reference Counted, with Write Barrier）。攻击者利用这一点，通过强制GC获得一个垂悬指针，在此基础上通过多次UAF进行多次类型混淆，随后借助两个自定义类的交互操作实现任意地址读写，在此基础上泄露ByteArray的虚表指针，从而绕过ASLR，最后借助HackingTeam泄露代码中的方式绕过DEP/CFG，执行shellcode。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019e6000767dd37fd2.png)

### 漏洞成因分析

在漏洞的触发过程，flash中Metadata的实例化对象地址，如下图所示。

[![](https://p1.ssl.qhimg.com/t019818ab763692ffe0.png)](https://p1.ssl.qhimg.com/t019818ab763692ffe0.png)

循环调用Metadata的setObject方法后，Metadata对象的keySet成员，如下图所示。

[![](https://p5.ssl.qhimg.com/t018b20355d39f9e0b0.png)](https://p5.ssl.qhimg.com/t018b20355d39f9e0b0.png)

keySet成员的部分值，如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d711d9fc9beef218.png)

强制垃圾回收后keySet成员被释放的内存部分，如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a31fcb1696279ea7.png)

在new Class5重用内存后，将导致类型混淆。如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015a9a016c43d0a6e8.png)

后续攻击者还通过判断String对象的length属性是否为24来确定漏洞利用是否成功。（如果利用成功会造成类型混淆，此时通过获取String对象的length属性实际为获取Class5的第一个成员变量的值24）。

通过进一步反编译深入分析，我们可以发现Metadata类的setObject对应的Native函数如下图所示，实际功能存在于setObject_impl里。

[![](https://p1.ssl.qhimg.com/t012343aef5fc39fbd7.png)](https://p1.ssl.qhimg.com/t012343aef5fc39fbd7.png)

在Object_impl里，会直接将传入的键（String对象）保存到Metadata的keySet成员里。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0165197410d1e43e41.png)

Buffer结构体定义如下（keySet成员的结构体有一定差异）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01591af34adec46803.png)

add_keySet中保存传入的键(String对象)，如下代码所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01db747f11068f0c13.png)

这个时候垃圾回收机制认为传入的键未被引用，从而回收相应内存，然而Metadata对象的keySet成员中仍保留着被回收的内存的指针，后续通过new Class5来重用被回收的内存，造成UAF漏洞。

### 漏洞利用分析

在实际的攻击过程中，利用代码首先申请0x1000个String对象，然后立即释放其中的一半，从而造成大量String对象的内存空洞，为后面的利用做准备。

[![](https://p3.ssl.qhimg.com/t01095f027222cfbaa9.png)](https://p3.ssl.qhimg.com/t01095f027222cfbaa9.png)

随后，利用代码定义了一个Metadata对象，借助setObject方法将key-value对保存到该对象中，Metadata对象的keySet成员保存着一个指向一片包含所有key(以String形式存储)的内存区域的指针。紧接着强制触发GC，由于keySet成员没有使用DRCWB，keySet成员内保存着一个指向上述内存区域的垂悬指针，随后读取keySet到arr_key数组，供后面使用。

[![](https://p4.ssl.qhimg.com/t016e8273b37c960827.png)](https://p4.ssl.qhimg.com/t016e8273b37c960827.png)

得到垂悬指针后，利用代码立即申请0x100个Class5类对象保存到vec5（vec5是一个向量对象），由于Class5类对象的内存大小和String对象的内存大小一致（32位下均为0x30字节），且相关对象分配在同一个堆内，根据mmgc内存分配算法，会有Class5对象占据之前被释放的String对象的内存空间。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019781e7f402c5bb55.png)

其中Class5对象定义如下，可以看到该Class5有2个uint类型的成员变量，分别初始化为0x18和2200(0x898)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0146cf94ec24747e73.png)

随后遍历key_arr数组，找到其中长度变为为0x18的字符串对象（在内存中，String对象的length字段和Class5的m_1成员重合），在此基础上判断当前位于32位还是64位环境，据此进入不同的利用分支。

[![](https://p2.ssl.qhimg.com/t01d5b92f86d0bd3aa9.png)](https://p2.ssl.qhimg.com/t01d5b92f86d0bd3aa9.png)

接上图，可以看到：在找到被Class5对象占用的String索引后，利用代码将arr_key的相关属性清零，这使得arr_key数组内元素（包括已占位Class5对象）的引用计数减少变为0，在MMgc中，对象在引用计数减为0后会立刻进入ZCT（zero count table）。随后利用代码强制触发GC，把ZCT中的内存回收，进入后续利用流程。下面我们主要分析32位环境下的利用流程。

下面我们主要分析32位环境下的利用流程，在32位分支下，在释放了占位的Class5对象后，利用代码立即申请256个Class3对象并保存到另一个向量对象vec3中，此过程会重用之前被释放的某个（或若干）Class5对象的内存空间。

[![](https://p4.ssl.qhimg.com/t01beb1cf9c6135d552.png)](https://p4.ssl.qhimg.com/t01beb1cf9c6135d552.png)

其中Class3对象的定义如下，它和Class5非常相似，两者在内存中都占用0x30字节。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01862b0f53c8a115ba.png)

可以看到Class3有一个m_ba成员和一个m_Class1成员，m_ba被初始化为一个ByteArray对象，m_Class1被初始化为一个Class1对象，Class1对象定义如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01134ad25e77d4525e.png)

Class3对象占位完成后，利用代码立即遍历vec5寻找一个被Class3对象占用内存的原Class5对象。找到后，保存该Class5对象的索引到this.index_1，并保存该对象（已经变为Class3对象）的m_Class1成员到this.ori_cls1_addr，供后续恢复使用。

[![](https://p3.ssl.qhimg.com/t01de38b88be0231142.png)](https://p3.ssl.qhimg.com/t01de38b88be0231142.png)

两轮UAF之后，利用代码紧接着利用上述保存的index_1索引，借助vec5[index_1]去修改被重用的Class3对象的m_Class1成员。随后立即遍历vec3去寻找被修改的Class3对象，将该对象在vec3中的索引保存到this.index_2。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bd54ee56aa6bec88.png)

到目前为止，利用代码已经得到两个可以操纵同一个对象的vector(vec5和vec3)，以及该对象在各自vec中的索引(index_1和index_2)。接下来利用代码将在此基础上构造任意地址读写原语。

我们来看一下32位下任意地址读写原语的实现，从下图可以看到，借助两个混淆的Class对象，可以实现任意地址读写原语，相关代码在上图和下图的注释中已经写得很清楚，此处不再过多描述。关于减去0x10的偏移的说明，可以参考我们之前对cve-2018-5002漏洞的分析文章。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010ddfbd38e56ee59e.png)

64位下的任意地址读写原语和32位下大同小异，只不过64位下将与Class5混淆的类对象换成了Class2和Class4。此外还构造了一个Class0用于64位下的地址读取。

以下是这三个类的定义。

[![](https://p4.ssl.qhimg.com/t0110038e048ce07816.png)](https://p4.ssl.qhimg.com/t0110038e048ce07816.png)

[![](https://p1.ssl.qhimg.com/t01c182f4757a2f1e10.png)](https://p1.ssl.qhimg.com/t01c182f4757a2f1e10.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01286f8cb5bb186167.png)

以下是64位下的任意地址读写原语，64位下的读写原语一次只能读写32位，所以对一个64位地址需要分两次读写。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cb976d82804d8fce.png)

利用代码借助任意地址读写构造了一系列功能函数，并借助这些功能函数最终读取kernel32.dll的VirtualProtect函数地址，供后面Bypass DEP使用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014f1c7d0252153e78.png)

利用最终采用与HackingTeam完全一致的手法来Bypass DEP/CFG。由于相关过程在网上已有描述，此处不再过多解释。32和64位下的shellcode分别放在的Class6和Class7两个类内， shellcode最终调用cmd启动WINRAR相关进程，相关命令行参数如下：

[![](https://p2.ssl.qhimg.com/t018e701ebdb5c9936e.png)](https://p2.ssl.qhimg.com/t018e701ebdb5c9936e.png)

### 漏洞补丁分析

Adobe官方在12月5日发布的Flash 32.0.0.101版本修复了此次的0day漏洞，我们通过动态分析发现该次漏洞补丁是用一个Array对象来存储所有的键，而不是用类似Buffer结构体来存储键，从而消除引用的问题。

1、某次Metadata实例化对象如下图所示，地址为0x7409540。

[![](https://p5.ssl.qhimg.com/t0161a6f3437cf68fbb.png)](https://p5.ssl.qhimg.com/t0161a6f3437cf68fbb.png)

2、可以看到Metadata对象的偏移0x1C处不再是类似Buffer结构体的布局，而是一个Array对象，通过Array对象来存储键值则不会有之前的问题。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0188f552f495beced5.png)

3、循环调用setObject设置完键值后keySet中的值如下所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b73b98560d3e0fb1.png)

4、强制垃圾回收发现保存的ketSet中的指针仍指向有效地字符串，说明强制垃圾回收并没有回收键值对象。

[![](https://p1.ssl.qhimg.com/t01083d5b55e33461f2.png)](https://p1.ssl.qhimg.com/t01083d5b55e33461f2.png)

## 最终荷载分析

PE荷载backup.exe将自己伪装成了NVIDIA显卡控制台程序，并拥有详细文件说明和版本号。

[![](https://p5.ssl.qhimg.com/t0175458179a4c7ecbc.png)](https://p5.ssl.qhimg.com/t0175458179a4c7ecbc.png)

文件使用已被吊销的证书进行了数字签名。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0185cff583f60cdeaa.png)

PE荷载backup.exe启动后将在本地用户的程序数据目录释放一个NVIDIAControlPanel.exe。该文件和backup.exe文件拥有同样的文件信息和数字签名，但文件大小不同。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e7df4a29d1a568bb.png)

经过进一步的分析，我们发现PE荷载是一个经过VMP强加密的后门程序，通过解密还原，我们发现主程序主要功能为创建一个窗口消息循环，有8个主要功能线程，其主要功能如下：

### 线程功能：

<td>编号</td><td>描述</td><td>功能</td>
|------
|0|分析对抗线程|检验程序自身的名称是否符合哈希命名规则,如符合则设置自毁标志。

分析对抗线程
|1|唤醒线程|监控用户活动情况，如果用户有键盘鼠标活动则发送0x401消息（创建注册计划任务线程）。

唤醒线程
|2|休眠线程|随机休眠，取当前时钟数进行比较，随机发送 WM_COPYDATA消息（主窗口循环在接收这一指令后，会休眠一定时间）。

休眠线程
|3|定时自毁线程|将程序中的时间字符串与系统时间进行比较，如果当前系统时间较大，则设置标志位，并向主窗口发送0x464消息（执行自毁）；如果自毁标志被设置，则直接发送0x464消息。

定时自毁线程
|4|通信线程|收集机器信息并发送给C&amp;C，具有执行shellcode、内存加载PE和下载文件执行的代码。

通信线程
|5|注册自启动线程|判断当前程序路径与之前保存的路径是否相同，并在注册表中添加启动项。

注册自启动线程
|6|注册计划任务线程|检测是否存在杀软，若检测到则执行自毁；将自身拷贝到其他目录并添加伪装成英伟达控制面板的计划任务启动。

注册计划任务线程
|7|自毁线程|停止伪装成英伟达控制面板的计划任务，清理相关文件，执行自毁。

自毁线程

### 主消息循环功能：

<td>消息类型</td><td>功能</td>
|------
|WM_CREATE|创建唤醒、休眠和定时自毁线程，并创建全局Event对象

创建唤醒、休眠和定时自毁线程，并创建全局Event对象
|WM_DESTROY、WM_SIZE、WM_PAINT|默认消息循环

默认消息循环
|WM_CLOSE|发送退出消息

发送退出消息
|WM_QUIT|关闭句柄，调用注册自启动线程

关闭句柄，调用注册自启动线程
|WM_ENDSESSION|调用注册自启动线程

调用注册自启动线程
|WM_COPYDATA|执行主消息循环线程休眠

执行主消息循环线程休眠
|WM_USER（0x400）|创建通信线程

创建通信线程
|WM_USER + 1 （0x401）|创建注册计划任务线程

创建注册计划任务线程
|WM_USER + 2 （0x402）|MessageBox消息弹窗

MessageBox消息弹窗
|WM_USER + 3 （0x403）|Sleep休眠一定时间

Sleep休眠一定时间
|WM_USER + 4 （0x404）|默认消息循环

默认消息循环
|WM_USER + 5 （0x405）|创建注册表自启动线程

创建注册表自启动线程
|WM_USER + 0x63 （0x463）|通知全局Event，然后等待旧线程3工作结束（0.5秒），重新创建新的线程3

通知全局Event，然后等待旧线程3工作结束（0.5秒），重新创建新的线程3
|WM_USER + 0x64 （0x464）|创建自毁线程

创建自毁线程

[![](https://p1.ssl.qhimg.com/t01280724f7cc14ef77.png)](https://p1.ssl.qhimg.com/t01280724f7cc14ef77.png)

### 线程功能分析

#### 0 分析对抗线程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0193eba3e671f32bb2.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016684b040db2f2069.png)

检验程序自身的名称是否符合哈希命名规则,如符合则设置自毁标志。

#### 1 唤醒线程

监控用户活动情况，如果用户有键盘鼠标活动则发送0x401消息给主窗口程序，唤醒创建注册计划任务线程。

[![](https://p2.ssl.qhimg.com/t014fdf233df2f57549.png)](https://p2.ssl.qhimg.com/t014fdf233df2f57549.png)

#### 2 休眠线程

取当前TickCount 进行比较，低位小于100则发送 WM_COPYDATA指令 主窗口循环在接收这一指令后，会休眠一定时间

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01af162937e19fc0fc.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016d4edd09df05d5a6.png)

#### 3 定时自毁线程

解密程序中的时间字符串与当前系统时间进行比较，如果当前系统时间较大，则设置标志位，并向主窗口发送0x464消息（执行自毁）。

[![](https://p3.ssl.qhimg.com/t013d07105277ad897f.png)](https://p3.ssl.qhimg.com/t013d07105277ad897f.png)

#### 4 通信线程

获取机器信息 包括CPU型号,内存使用情况,硬盘使用情况,系统版本,系统语言,时区 用户名,SID,安装程序列表等信息。

[![](https://p2.ssl.qhimg.com/t011ffa107836f8cbdd.png)](https://p2.ssl.qhimg.com/t011ffa107836f8cbdd.png)

向 188.241.58.68 发送POST

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0185c0b0fa7a760eb6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b225baa77ca2663b.png)

连接成功时,继续向服务器发送数据包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018dcc3a10663bfb18.png)

符合条件时,进入RunPayload函数（实际并未捕获到符合条件的情况）

[![](https://p5.ssl.qhimg.com/t010072106ff7932e1f.png)](https://p5.ssl.qhimg.com/t010072106ff7932e1f.png)

RunPayload函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014954a5984d2c532e.png)

LoadPE

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0122ed99fc9b5ff634.png)

RunShellCode

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01816f2e732ffca4f1.png)

#### 5 注册自启动线程

1、首先拿到线程6中保存的AppData\Local目录下的NVIDIAControlPanel文件路径，使用该路径或者该路径的短路径与当前文件模块路径判断是否相同。

[![](https://p3.ssl.qhimg.com/t010d983a904af5afff.png)](https://p3.ssl.qhimg.com/t010d983a904af5afff.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c16a14bb9fee2d86.png)

2、随后尝试打开注册表HKEY_CURRENT_USER下SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c21dc5b4149a9aef.png)

3、查询当前注册表路径下NVIDIAControlPanel键值是否存在，如果不存在或者为禁用状态则设置键值为启用的键值02,00,00,00,00,00,00,00,00,00,00,00。

[![](https://p3.ssl.qhimg.com/t016d56d9bc3ec32deb.png)](https://p3.ssl.qhimg.com/t016d56d9bc3ec32deb.png)

#### 6 注册计划任务线程

检查自身是否运行在System进程

如果运行在system进程, 则弹出Aborting消息, 退出进程,并清理环境

[![](https://p0.ssl.qhimg.com/t01b3bdb8705a03649e.png)](https://p0.ssl.qhimg.com/t01b3bdb8705a03649e.png)

并不断向 Windows Update窗口投递退出消息

[![](https://p2.ssl.qhimg.com/t014b96a65b56203c7b.png)](https://p2.ssl.qhimg.com/t014b96a65b56203c7b.png)

三种文件拷贝方式
- 其使用了三种不同的方式去拷贝自身文件：- 在监测到杀软相关进程之后, 会使用Bits_IBackgroundCopyManager方式进行自拷贝
- 如果没有相关杀软进程, 会使用iFileOperation 方式进行自拷贝
- 如果在以上工作方式之行结束, 仍未有文件拷贝到目标目录, 则执行释放BAT方式进行自拷贝
Bits_IBackgroundCopyManager

(5ce34c0d-0dc9-4c1f-897c-daa1b78cee7c)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f0fc09c01bdd2d9d.png)

[![](https://p2.ssl.qhimg.com/t010f7bb4972b785990.png)](https://p2.ssl.qhimg.com/t010f7bb4972b785990.png)

iFileOperation

`{`3ad05575-8857-4850-9277-11b85bdb8e09`}`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018ef4262c6c759b83.png)

批处理文件释放

创建批处理文件，拷贝自身来释放文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e343b6246834a9d1.png)

[![](https://p4.ssl.qhimg.com/t0191577cd5cb262352.png)](https://p4.ssl.qhimg.com/t0191577cd5cb262352.png)

固定释放常驻后门: F951362DDCC37337A70571D6EAE8F122

检测杀软

检测的杀软包括F-Secure, Panda, ESET, Avira, Bitdefender, Norton, Kaspersky 通过查找名称和特定驱动文件实现

[![](https://p3.ssl.qhimg.com/t01688a0a7cce8d30e3.png)](https://p3.ssl.qhimg.com/t01688a0a7cce8d30e3.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018080624cde5854c9.png)

[![](https://p5.ssl.qhimg.com/t0147bbd5739b9e0e82.png)](https://p5.ssl.qhimg.com/t0147bbd5739b9e0e82.png)

检测的杀软之后会执行自毁流程

添加计划任务

[![](https://p0.ssl.qhimg.com/t012e3edb6eda80b5fc.png)](https://p0.ssl.qhimg.com/t012e3edb6eda80b5fc.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011d1a0f55a9e82fa1.png)

#### 7 自毁线程

判断系统版本后分别使用ITask和ITaskService 停止NVIDIAControlPanel这个计划任务

Win7以前采用ITask接口：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0195d64efc83b857c1.png)

[![](https://p2.ssl.qhimg.com/t014b32072f2ce276d3.png)](https://p2.ssl.qhimg.com/t014b32072f2ce276d3.png)

Win7和Win7以后采用ITaskService接口：

[![](https://p1.ssl.qhimg.com/t0194e359f778c622cf.png)](https://p1.ssl.qhimg.com/t0194e359f778c622cf.png)

在完成后清理文件。

## 附录IOC

### MD5：

92b1c50c3ddf8289e85cbb7f8eead077

1cbc626abbe10a4fae6abf0f405c35e2

2abb76d71fb1b43173589f56e461011b

### C&amp;C：

188.241.58.68
