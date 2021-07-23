> 原文链接: https://www.anquanke.com//post/id/84270 


# VirLock敲诈者新变种分析及解密方法


                                阅读量   
                                **93563**
                            
                        |
                        
                                                                                    



**前言**

**2016年6月开始,360安全中心发现VirLock的新变种的查杀量呈现上升趋势,通过分析,发现其新变种采用了多种手段来对抗杀软。**

**虽然宣称数据被加密,但原始数据随着病毒体的运行可以被释放,因此断定被加密的文件是可以恢复的,360安全中心第一时间对样本进行了分析,并针对此变种开发了恢复工具,是国内唯一可以解密VirLock新变种的厂商。**

有关VirLock的基本行为,在2015年1月的播报中已经有所阐述( [http://bobao.360.cn/learning/detail/227.html](http://bobao.360.cn/learning/detail/227.html) ),本次播报将就亮点部分进行分析。

<br>

**基本信息**

MD5:D832508B53BB3B55C2288F23B4FB6C2C

大小:850944字节

                                             

[![](https://p0.ssl.qhimg.com/t01f8f776baa8455f3d.png)](https://p0.ssl.qhimg.com/t01f8f776baa8455f3d.png)



<a name="_Toc455420980"></a>

**行为简述**

1.在**%UserProfile%**与**%AllUsersProfile%**释放文件,文件名为随机生成,使用CreateProcessW创建进程。



[![](https://p0.ssl.qhimg.com/t0149da5dbca46800be.png)](https://p0.ssl.qhimg.com/t0149da5dbca46800be.png)



2.第一个被启动的进程会再次生成一个随机文件名的文件,这三个文件互为守护进程,当其中任何一个被杀死之后,都会被其他“兄弟”创建,病毒以此手段避免进程被杀死。



[![](https://p1.ssl.qhimg.com/t0194ddc2c5d2fca1ca.png)](https://p1.ssl.qhimg.com/t0194ddc2c5d2fca1ca.png)



3.设置注册表,使隐藏文件,文件扩展名不可见。



[![](https://p2.ssl.qhimg.com/t01610800ffd43c7068.png)](https://p2.ssl.qhimg.com/t01610800ffd43c7068.png)



4.加密文件,被加密的文件变为EXE,图标和加密前一致。

5.感染文件类型,包括但不限于:

文档:DOC、XLS、PDF、PPT等;

图片:PNG、GIF、BMP、JPG等;

压缩文件:RAR、ZIP、7z等;

可执行文件:EXE、SCR等。

6.弹出勒索提示,需要支付价值约$250的比特币作为赎金。

<br>

**病毒发作之后截图**

[![](https://p5.ssl.qhimg.com/t010d5938c55cfc6c90.png)](https://p5.ssl.qhimg.com/t010d5938c55cfc6c90.png)

图:告警信息,提示用户使用了盗版软件,需要支付罚金。恫吓用户,若不支付赎金,可能会被判处5年徒刑。

[![](https://p2.ssl.qhimg.com/t01fa193788b72d9094.png)](https://p2.ssl.qhimg.com/t01fa193788b72d9094.png)

图:向用户介绍支付流程。

[![](https://p4.ssl.qhimg.com/t018efdc9a9f0e55bef.png)](https://p4.ssl.qhimg.com/t018efdc9a9f0e55bef.png)



图:附近ATM的位置



**相对上一版本的亮点**

**亮点之一,代码执行**

新变种相对老变种相比,变化最大的就在于代码执行方式。

病毒体在解密之后,执行方式就不是顺序执行,而是采取一种特殊的方式来执行,以此来对抗杀毒虚拟机,增加分析难度。

流程大致如下:

(A)新申请一块新的内存区域,作为STUB,以供病毒体执行;

(B)将公共代码放入STUB中,公共代码中间以NOP填充;

(C)解密另一区域的数据,按照格式,将代码复制到公共代码的NOP位置;

(D)执行STUB,清空STUB;

(E)循环执行(B)。

其中STUB的代码如下:

结构如下,STUB主要由三部分组成:



[![](https://p3.ssl.qhimg.com/t01770b13efd81386b3.png)](https://p3.ssl.qhimg.com/t01770b13efd81386b3.png)



保存环境;

设置新的ESP与EBP值;

执行代码;

恢复ESP与EBP的值;

恢复环境;

这样一来,每执行一条“核心指令”,就要多执行上百条负责解密,循环控制的指令。

增加了病毒体积,与执行步数,也给调试带来一些不便。

填充的指令由指令表与跳转表组成。

**指令表:**

通过XOR算法,可解密出指令表:



[![](https://p1.ssl.qhimg.com/t015654b5f7946309bb.png)](https://p1.ssl.qhimg.com/t015654b5f7946309bb.png)



解密之后的数据如下(蓝色数据部分):



[![](https://p3.ssl.qhimg.com/t012b2fc4e1b00e91f1.png)](https://p3.ssl.qhimg.com/t012b2fc4e1b00e91f1.png)



整理之后可以看出,数据由数据前缀与指令组成:

指令前缀由两部分组成:代码标志与代码长度,代码标志为00表示普通指令。

[![](https://p3.ssl.qhimg.com/t0111bc7706a246b696.jpg)](https://p3.ssl.qhimg.com/t0111bc7706a246b696.jpg)

代码的执行按照此顺序执行,包括条件跳转;**顺序表:**

解密方式也是XOR:



[![](https://p3.ssl.qhimg.com/t014d90054901f4b115.png)](https://p3.ssl.qhimg.com/t014d90054901f4b115.png)



部分数据如下:



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d181bd50fc0a1bbd.png)



0000 0100 0200 0300 0400 0500 0600 0700 0800

**D500** 0900 0A00 **D600** 0B00 **D500** 0900 0A00 **D700**

0C00 0D00 0E00 0F00 1000 1100 1200 **D500** 0900

0A00 **D800** 1300 **D500** 0900 0A00 **D900** 1400 **D500**

其中D5到E9解密后如下,标志位为(01,表示跳转),跳转条件均为JNZ,后面的数值表示跳转相对偏移:

[![](https://p5.ssl.qhimg.com/t01a9f9cbe08c66576e.jpg)](https://p5.ssl.qhimg.com/t01a9f9cbe08c66576e.jpg)

**亮点之二,数据解密**

随着程序的执行,病毒会主动将文件解密后落地,因此被VirLock加密的数据,在逆向其基本算法后,是可以恢复数据的。

数据解密主要分为三个部分:

第一部分解密:

第一部分的解密方式为XOR,位置为ESI,密钥为EDX,长度为ECX:



[![](https://p4.ssl.qhimg.com/t01921893a16e27607a.png)](https://p4.ssl.qhimg.com/t01921893a16e27607a.png)



第二部分解密:

这部分解密的位置信息,位于代码表中:

[![](https://p3.ssl.qhimg.com/t01737750e64f32f8cb.jpg)](https://p3.ssl.qhimg.com/t01737750e64f32f8cb.jpg)

解密方式:XOR,ROR

在执行完第二部分解密之后,开始第三部分解密,这层解密主要针对被加密文件。第三部分解密:



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01626f489b93049a3c.png)



恢复文件



[![](https://p1.ssl.qhimg.com/t01ef021860ff552591.png)](https://p1.ssl.qhimg.com/t01ef021860ff552591.png)



图:解密之后的数据,红色部分表示原始文件名,蓝色部分表示原始数据。

针对VirLock系列敲诈者病毒,360杀毒独家提供文件恢复功能。如果用户不慎中招,可以使用360杀毒扫描恢复原文件。

扫描病毒:



[![](https://p2.ssl.qhimg.com/t016b8945026732300e.png)](https://p2.ssl.qhimg.com/t016b8945026732300e.png)



修复文件:

[![](https://p5.ssl.qhimg.com/t01f2476b40bbfcbe5e.png)](https://p5.ssl.qhimg.com/t01f2476b40bbfcbe5e.png)





文件恢复效果示例:



[![](https://p2.ssl.qhimg.com/t017243bff87059b59f.png)](https://p2.ssl.qhimg.com/t017243bff87059b59f.png)



<a name="_Toc455420985"></a>

**亮点之三,勒索金额的变化**

在2015年1月,360安全中心发布的第一版VirLock的分析报告([http://bobao.360.cn/learning/detail/227.html](http://bobao.360.cn/learning/detail/227.html))显示,当时勒索的金额,为价值150美元的比特币,当时约0.71BTC:



[![](https://p0.ssl.qhimg.com/t01241e1637c7199de9.png)](https://p0.ssl.qhimg.com/t01241e1637c7199de9.png)



而新版本勒索的金额,为价值250美元左右的BTC,按现在的价格,约0.392BTC:



[![](https://p1.ssl.qhimg.com/t01b8b3470c99146827.png)](https://p1.ssl.qhimg.com/t01b8b3470c99146827.png)
