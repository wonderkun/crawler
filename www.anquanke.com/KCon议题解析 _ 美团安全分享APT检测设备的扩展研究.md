> 原文链接: https://www.anquanke.com//post/id/185101 


# KCon议题解析 | 美团安全分享APT检测设备的扩展研究


                                阅读量   
                                **405686**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01a27a703b214b0ec3.jpg)](https://p0.ssl.qhimg.com/t01a27a703b214b0ec3.jpg)



8月23日-25日，一年一度的KCon 黑客大会在北京昆泰嘉瑞文化中心成功举办，本届大会以「无界」为主题，通过汇聚全球黑客的智慧，探索技术的无穷奥秘，突破边界外的边界，创造不可能的可能。

作为安全领域内拥有丰富实战经验和技术积累的安全团队，美团安全研究院成员受邀参加KCon黑客大会，并针对目前主流厂商在移动平台（iOS、Android）的APT检测设备明显不足的现状，分享了关于「APT检测设备的扩展研究」的议题。

现场议题围绕业界现状分析、C相关设备的动态沙箱（蜜罐）技术等几个方面，充分展示美团安全团队对APT检测设备的扩展研究成果。

[![](https://p5.ssl.qhimg.com/t01d0aca04204038cf8.jpg)](https://p5.ssl.qhimg.com/t01d0aca04204038cf8.jpg)

[![](https://p1.ssl.qhimg.com/t0104950c4989af0873.jpg)](https://p1.ssl.qhimg.com/t0104950c4989af0873.jpg)

[![](https://p4.ssl.qhimg.com/t01b640208edc20b162.jpg)](https://p4.ssl.qhimg.com/t01b640208edc20b162.jpg)



## 议题解读「APT检测设备的扩展研究」

演讲者 | JU ZHU

目前就职于美团（高级安全研究员），有着9+年的安全研究经验，其中7+年主要从事高级威胁的研究，包括0Day、nDay 和漏洞挖掘。他一直致力于使用自动化系统来 Hunt 野外的高级威胁，曾多次获得 CVE，且受到 Google、Apple、Facebook 等厂商的致谢，也多次作为 Speaker 受邀参加 BlackHat、CodeBlue、CSS 等国内外的顶级安全会议。



## 1. 现状分析

### <!-- [if !supportLists]-->1.1<!--[endif]--> 业界主流APT检测设备选型对比

APT检测设备的选择一般是参考Gartner报告挑出备选，再结合实际情况做适应性检测对比。

平台支持性：

我们统计了某天内网接入设备的操作系统类型（见图1），并根据这些类型对三个备选厂商进行了平台相关性检测（见图2）。

[![](https://p1.ssl.qhimg.com/t014d8c96ec9d0e1eac.png)](https://p1.ssl.qhimg.com/t014d8c96ec9d0e1eac.png)

图1 内网接入设备的操作系统类型统计 
<td width="95"> </td><td width="95">Windows</td><td width="95">MacOS</td><td width="95">iOS</td><td width="95">Android</td><td width="95">其它</td>

Windows

iOS

其它
<td width="95">厂商1</td><td width="95">✔</td><td width="95">✘</td><td width="95">✘</td><td width="95">✘</td><td width="95">✘</td>

✔

✘

✘
<td width="95">厂商2</td><td width="95">✔</td><td width="95">✘</td><td width="95">✘</td><td width="95">✘</td><td width="95">✘</td>

✔

✘

✘
<td width="95">厂商3</td><td width="95">✔</td><td width="95">✘</td><td width="95">✘</td><td width="95">✔</td><td width="95">✘</td>

✔

✘

✘

图2 各厂商的平台支持对比

从图1和图2可以看出，大部分厂商只是对Windows平台的支持比较好，或者也提供Android沙箱。然而这和内网接入设备的多元化还有很大差距，需要我们自己进行进一步的扩展开发。

文件类型支持性：

有些厂商对于平台的支持可能受到某些限制，所以他们通过更多的文件类型支持来进行能力补充（见图3）。
<td width="81"> </td><td width="81">PE</td><td width="81">Office</td><td width="81">PDF</td><td width="81">Mach-O</td><td width="81">plist</td><td width="81">APK</td>

PE

PDF

plist
<td width="81">厂商1</td><td width="81">✔</td><td width="81">✔</td><td width="81">✔</td><td width="81">✘</td><td width="81">✘</td><td width="81">✘</td>

✔

✔

✘
<td width="81">厂商2</td><td width="81">✔</td><td width="81">✔</td><td width="81">✘</td><td width="81">✘</td><td width="81">✘</td><td width="81">✘</td>

✔

✘

✘
<td width="81">厂商3</td><td width="81">✔</td><td width="81">✔</td><td width="81">✘</td><td width="81">✔</td><td width="81">✘</td><td width="81">✔</td>

✔

✘

✘

图3 各厂商的文件类型支持对比

在选型测试中，我们特地增加了plist文件格式的样本，这源于之前发现的在野的iOS Ransomware（Death Profile[<!-- [if !supportFootnotes]-->[1]<!--[endif]-->](/Users/xuting16/Desktop/SRC/Kcon/%E7%BE%8E%E5%9B%A2%E5%AE%89%E5%85%A8Kcon%E9%BB%91%E5%AE%A2%E5%A4%A7%E4%BC%9A-20190826%E7%BB%88%E7%89%88.docx#_ftn1)）。它是一种基于iOS的Configuration Profile，常用于企业为办公设备推送各类配置信息（如Wi-Fi、VPN设置等），是一种常见的公司内部交换文件格式。

从图3看，各厂商几乎覆盖了基于Windows平台的文件格式（诸如PE、Office等），只有少量厂商支持基于MacOS/iOS平台的Mach-O文件（经过实测，他们基本上采用的是静态分析方式），而plist格式目前并未有厂商支持。因此对于文件格式的支持性，还有很大的空间可提升。

### <!-- [if !supportLists]-->1.2 可参考的解决方案对比

对于甲方来说，APT检测的解决方案一般以采购为主，但也不乏根据实际情况进行部分自研。我们选取了一些可参考的（除Windows外）动态沙箱技术解决方案来进行对比（见图4）。
<td width="142"> </td><td width="142">MacOS</td><td width="142">iOS</td><td width="142">Android</td>

MacOS

Android
<td width="142">可参考的动态沙箱</td><td width="142">Darling或Cuckoo Sandbox</td><td width="142">Corellium</td><td width="142">Anbox或Cuckoo Droid</td>

Darling

Cuckoo Sandbox

Anbox

Cuckoo Droid
<td width="142">使用方式（云或本地）</td><td width="142">本地</td><td width="142">云</td><td width="142">本地</td>

本地

本地
<td width="142">开源？</td><td width="142">是</td><td width="142">否</td><td width="142">是</td>

是

是
<td width="142">实现成本</td><td width="142">中</td><td width="142">极高</td><td width="142">中</td>

中

中

图4 可参考的动态沙箱技术解决方案对比

MacOS：

Darling是一种比较轻量级的基于Linux的MacOS App运行环境，主要是做了一个转换层，将App的函数调用重定向到了Linux。Darling可以运行在Docker上，方便大规模部署和维护。Cuckoo Sandbox是比较重量级的，它运行在MacOS上，一般采用VisualBox来部署，性能会差些。

因此可以采用阶梯式部署方式：Darling完成大部分指标检测，而剩下的少部分，则由Cuckoo Sandbox来完成（如图5）。

[![](https://p2.ssl.qhimg.com/t018ac44ef38ddc09bf.png)](https://p2.ssl.qhimg.com/t018ac44ef38ddc09bf.png)

图5 MacOS动态沙箱技术解决方案

iOS：

Corellium拥有一套比较完整的iOS虚拟机，不过目前他们只提供云服务，对于内网审计是个很大的挑战。对于很多甲方公司来说，内网的数据是不能外传的，所以我们更倾向于使用本地沙箱方式。

Android：

Anbox是一个轻量级完整模拟Android的系统， Cuckoo Droid是一个比较成熟的检测Android Malware的沙箱系统，且它们都是开源的，比较符合甲方的需求，不需要再做拓展研究。

综上所述，大部分可参考的动态沙箱技术解决方案，基本都可实现本地部署，且开源方便二次开发。唯有iOS动态沙箱需要重新设计和开发。



## 2.  iOS动态沙箱（蜜罐）技术

### 2.1<!--[endif]-->总体架构流程

为了能检测出未知Malware（0 Day等），同时又能知晓影响面（版本、位数等），我们首先需要提取iOS App中的Mach-O文件，再根据32位或者64位来进行相应的检测。

[![](https://p5.ssl.qhimg.com/t01bb6b65b672b87ac3.png)](https://p5.ssl.qhimg.com/t01bb6b65b672b87ac3.png)

图6 针对Mach-O的流程

如图6所示，首先解开IPA文件，再分解Fat文件为32位Mach-O和64位Mach-O。由于基于Aarch 64的硬件服务器架构不能直接运行Arm 32位的程序，我们进行了分流设计：将32位的Mach-O送入模拟Arm v7的Qemu，而64位的Mach-O则送入基于Aarch 64的Docker。

另外，存在像Death Profile这样的攻击，我们还需要检测流量中plist格式的文件或者内容（如图7）。

[![](https://p0.ssl.qhimg.com/t0147c3fa5855e51d62.png)](https://p0.ssl.qhimg.com/t0147c3fa5855e51d62.png)

图7 针对plist的流程

### 2.2 轻量级虚拟化设计

Corellium的虚拟化方案虽然非常完备，但对于我们的需求来说过重，且开发成本极高。因此我们更倾向于类似Darling（或者Wine）的轻量级解决方案。

我们采用API重定向的方式，将Mach-O完整地在Qemu（或者Docker）中模拟运行起来。
<td colspan="4" width="568">Loader &amp; Run Mach-O</td>
<td colspan="2" width="284">Foundation</td><td colspan="2" width="284">。。。</td>

。。。
<td width="142">libobjc.so</td><td width="142">libxml2.so</td><td width="142">libdispatch.so</td><td width="142">。。。</td>

libxml2.so

。。。
<td width="142">libc.so</td><td width="142">libc++abi.so</td><td width="142">libc++.so</td><td width="142">。。。</td>

libc++abi.so

。。。
<td colspan="2" width="284">Qemu（Arm v7）</td><td colspan="2" width="284">Docker（Aarch 64）</td>

Docker（Aarch 64）
<td colspan="4" width="568">Linux（Aarch 64）</td>
<td colspan="4" width="568">Hardware（Aarch 64）</td>

图8 轻量级的虚拟化设计

图8是我们提出的轻量级虚拟化设计，最底层硬件和操作系统都是基于Aarch 64（或者Arm v8），在它们上面使用Qemu以实现Arm v7的支持。而Docker用于直接对Arm 64的支持。

在Qemu（或者Docker）内，我们部署安装了一些基础库（诸如libc、libc++等），还编译了libobjc、libdispatch等开源库，以对更上层的API重定向库提供支持。

最后，我们实现了类似Foundation.framework的API重定向库，以支撑Mach-O的正常运行，运行效果见图9、图10。

[![](https://p0.ssl.qhimg.com/t01a76a91decbbd86fe.jpg)](https://p0.ssl.qhimg.com/t01a76a91decbbd86fe.jpg)

图9 Qemu（Arm v7）的运行效果

[![](https://p5.ssl.qhimg.com/t014fd768029895e8c9.jpg)](https://p5.ssl.qhimg.com/t014fd768029895e8c9.jpg)

图10 Docker（Arm 64）的运行效果

### 2.3实现

正常来说，我们运行一个Mach-O文件，需要实现一个类似dyld的Loader程序，来用于解析和加载Mach-O，并导入相关的依赖库。这里我们需要自己实现这个过程。

整个实现过程分为六个部分：解析和加载、导入相关依赖库、地址修正、地址（API）重定向、运行、回调。

[![](https://p3.ssl.qhimg.com/t01d76e155ca365dafe.jpg)](https://p3.ssl.qhimg.com/t01d76e155ca365dafe.jpg)

图11 整个运行过程

[![](https://p2.ssl.qhimg.com/t0144a9e54d22c622b2.png)](https://p2.ssl.qhimg.com/t0144a9e54d22c622b2.png)

图12 运行效果

解析和加载：

我们通过解析Mach-O文件中Load Commands的Segment信息，将所有的Segment数据（除PageZero）按地址顺序逐一加载到虚拟内存。由于程序启动时会在进程空间加上一段偏移量（slide），我们需要计算记录下slide的结果，用于之后运行时的起始地址计算（如图13）。

slide = text_real_vm_addr – text_vm_addr

其中text_real_vm_addr是TEXT段的实际虚拟内存地址，text_vm_addr是Mach-O文件中TEXT段的VM地址。

另外，在映射时，可按实际VM Protection值来设置所映射的虚拟内存VMP属性。

 [![](https://p0.ssl.qhimg.com/t010398426228370402.png)](https://p0.ssl.qhimg.com/t010398426228370402.png)
<td colspan="2" width="189">slide + text_vm_addr</td><td colspan="4" rowspan="2" width="379"> </td>

 
<td width="95"> </td><td width="95"> </td>

 
<td width="95"> </td><td width="95">TEXT</td><td width="95">DATA</td><td width="95">LLVM</td><td width="95">LINKEDIT</td><td width="95">。。。</td>

TEXT

LLVM

。。。
<td colspan="6" width="568">Loader &amp; Run</td>

图13 所有Segment数据（除PageZero）映射到虚拟内存的实际地址分布情况

导入相关依赖库：

通过解析Mach-O文件中Load Commands的LC_LOAD_DYLIB数据，可获取所有依赖库的信息，并做模拟实现。这样就可以将Mach-O中的API调用重定向到我们希望调用的函数中去。

事实上，在实现某个依赖库（比如Foundation）时，可能会存在更多的依赖库需要实现，其工作量将是巨大的（如图14）。

[![](https://p4.ssl.qhimg.com/t0147472632ccc17be5.jpg)](https://p4.ssl.qhimg.com/t0147472632ccc17be5.jpg)

图14 Foundation的实现

地址修正：

如果要正常运行main函数，Mach-O文件中Rebase所描述地址的数据还需要做修正，如Lazy Symbol Pointer数据和CFString数据等。
<td width="142"> </td><td width="142">原数据（Pointer）</td><td width="142"> </td><td width="142">新数据（Pointer）</td>

原数据（Pointer）

新数据（Pointer）
<td width="142">Lazy Symbol Pointer</td><td width="142">0x100007F9C</td><td width="142">-&gt;</td><td width="142">slide + 0x100007F9C</td>

0x100007F9C

slide + 0x100007F9C
<td width="142">CFString</td><td width="142">0x100007FA8</td><td width="142">-&gt;</td><td width="142">slide + 0x100007FA8</td>

0x100007FA8

slide + 0x100007FA8

图15 Mach-O文件中Rebase所描述地址的数据修正 

地址（API）重定向：

对于Lazy Symbol Pointer这类数据，我们还需要再做一次修正，那就是使用我们模拟实现的函数地址来替换该数据（Pointer）。
<td width="142"> </td><td width="142">原地址</td><td width="142"> </td><td width="142">新地址</td>

原地址

新地址
<td width="142">NSLog</td><td width="142">slide + 0x100007F9C</td><td width="142">-&gt;</td><td width="142">NSLog@libFoundation.so</td>

slide + 0x100007F9C

NSLog@libFoundation.so

图16 地址（API）重定向

[![](https://p0.ssl.qhimg.com/t01b3e2f9b82adfc8ce.jpg)](https://p0.ssl.qhimg.com/t01b3e2f9b82adfc8ce.jpg)

图17 API重定向流程

运行：

如果我们希望运行某个函数，只需要找到它的入口地址，即可直接运行。比如main函数，我们通过解析Mach-O文件中Load Commands的LC_MAIN数据，从而获得它的相对入口地址，再加上之前我们获得的slide和text_vm_addr，就可以算出它的绝对（真实）入口地址。

[![](https://p0.ssl.qhimg.com/t017f8298e25d8b4f99.jpg)](https://p0.ssl.qhimg.com/t017f8298e25d8b4f99.jpg)

图18 算出main函数的绝对（真实）入口地址，并直接运行它

回调

Delegate是iOS开发常用的设计模式，所以我们也需要实现相应的回调。我们通过解析Mach-O文件中ObjC2 Class的数据，来获得Delegate类。然后，再解析它（比如AppDelegate）的Protocol数据，来获得Framework里对应的类（比如UIKit的UIApplication）最后，再解析它的Method数据，并注册到NSNotificationCenter。

[![](https://p2.ssl.qhimg.com/t01933063e4571976ad.jpg)](https://p2.ssl.qhimg.com/t01933063e4571976ad.jpg)

图19 回调流程

[![](https://p3.ssl.qhimg.com/t01fe1a752fa0564a4f.jpg)](https://p3.ssl.qhimg.com/t01fe1a752fa0564a4f.jpg)

图20 运行效果

2.4部署

最初研究或小批量试验，可以使用一些厂商的云服务，或者采用低成本的树莓派集群。而我们为了更好的匹配重新设计的动态沙箱（蜜罐）系统，采用了公司现有的ODM（Original Design Manufacturer）专用Aarch 64服务器。

[![](https://p3.ssl.qhimg.com/t0195a7fd70c604e66e.jpg)](https://p3.ssl.qhimg.com/t0195a7fd70c604e66e.jpg)

图21 自研服务器

### 团队介绍

美团安全部的大多数核心人员，拥有多年互联网以及安全领域实践经验，很多同学参与过大型互联网公司的安全体系建设，其中也不乏全球化安全运营人才，具备百万级IDC规模攻防对抗的经验。安全部也不乏CVE“挖掘圣手”，有受邀在Black Hat等国际顶级会议发言的讲者，当然还有很多漂亮的运营妹子。

目前，美团安全部涉及的技术包括渗透测试、Web防护、二进制安全、内核安全、分布式开发、大数据分析、安全算法等等，同时还有全球合规与隐私保护等策略制定。我们正在建设一套百万级IDC规模、数十万终端接入的移动办公网络自适应安全体系，这套体系构建于零信任架构之上，横跨多种云基础设施，包括网络层、虚拟化/容器层、Server 软件层（内核态/用户态）、语言虚拟机层（JVM/JS V8）、Web应用层、数据访问层等，并能够基于“大数据+机器学习”技术构建全自动的安全事件感知系统，努力打造成业界最前沿的内置式安全架构和纵深防御体系。

随着美团的高速发展，业务复杂度不断提升，安全部门面临更多的机遇和挑战。我们希望将更多代表业界最佳实践的安全项目落地，同时为更多的安全从业者提供一个广阔的发展平台，并提供更多在安全新兴领域不断探索的机会。

### 招聘

美团安全2019年招聘火热进行中~

如果你想加入我们，欢迎简历请发至邮箱zhaoyan17@meituan.com。

[具体职位信息，可点击“这里”进行查看。](http://mp.weixin.qq.com/s?__biz=MzI5MDc4MTM3Mg==&amp;mid=2247483981&amp;idx=1&amp;sn=773534f644dfb9bbe4c010bbd8d3347f&amp;chksm=ec1be39edb6c6a88b1be288dc2240e902a0d93779e5cdb0522be66f6c5184a8d38071edad7f6&amp;scene=21#wechat_redirect)
