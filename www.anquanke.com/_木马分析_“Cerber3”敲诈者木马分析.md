> 原文链接: https://www.anquanke.com//post/id/84662 


# 【木马分析】“Cerber3”敲诈者木马分析


                                阅读量   
                                **97081**
                            
                        |
                        
                                                                                    



**一、  前言**

**近日，360互联网安全中心捕获到一款名为“cerber3”的敲诈者木马。**该敲诈者木马会加密计算机中的重要文件，加密的文件类型包括但不限于.doc,.ppt,.xls.,.jpg,.zip,.pdf等180多种类型。被加密后的文件将无法正常打开且被加上“cerber3”扩展名，用户必须访问相应网站支付赎金才可恢复文件，对数据安全有巨大威胁。



[![](https://p1.ssl.qhimg.com/t01eabce3468234789c.png)](https://p1.ssl.qhimg.com/t01eabce3468234789c.png)

图1 感染“cerber3”后的桌面背景

[![](https://p1.ssl.qhimg.com/t01259b7e92abecc013.png)](https://p1.ssl.qhimg.com/t01259b7e92abecc013.png)

图2 勒索信内容

[![](https://p3.ssl.qhimg.com/t0190ae8f71d264d675.png)](https://p3.ssl.qhimg.com/t0190ae8f71d264d675.png)

图3 被加密的文件

而此次木马的传播**除了以往的邮件附件传播外，也大量使用网站挂马，word宏病毒等手段传播**，这也造成大批普通网民中招。

[![](https://p0.ssl.qhimg.com/t0178d128f2b75e8baa.png)](https://p0.ssl.qhimg.com/t0178d128f2b75e8baa.png)

[![](https://p3.ssl.qhimg.com/t01715cb5db060c2958.png)](https://p3.ssl.qhimg.com/t01715cb5db060c2958.png)

文档打开之后，如果宏被执行的话，宏代码会调用Powershell做为下载器下载木马执行：

[![](https://p2.ssl.qhimg.com/t01846e7d352eea9f36.png)](https://p2.ssl.qhimg.com/t01846e7d352eea9f36.png)

**<br>**

**二、  加密流程解析**

**“cerber3”敲诈者使用RSA搭配随机数进行加密操作。**首先使用RSA公钥加密随机数作为本机专有加密密钥，在对每个文件进行加密时再产生一组随机数并使用该随机数加密文件，最后用本机专有密钥加密该随机数后存放到文件中，同时也将本机专有密钥也通过RSA加密后存到文件中。此种加密方法保证每个文件加密密钥不同并且每台计算机的专有密钥不同，就算暴力破解出其中一组随机数也只能解密一个文件，只有获得RSA私钥才能恢复所有文件。加密流程如下所示。

[![](https://p4.ssl.qhimg.com/t011b30330d9477154a.png)](https://p4.ssl.qhimg.com/t011b30330d9477154a.png)

使用这种分级加密方式，每一个文件中都存储有加密文件使用的密钥，攻击者可以对单个文件实施解密操作。在攻击者提供的付款页面中也提供了“免费解密单个文件”的功能。

[![](https://p2.ssl.qhimg.com/t011df9c8a1ff5b2293.png)](https://p2.ssl.qhimg.com/t011df9c8a1ff5b2293.png)

市面上可以看到有不少用户中招之后，交付赎金解密的案例

[![](https://p3.ssl.qhimg.com/t011ac9bd67c2ab3b2c.png)](https://p3.ssl.qhimg.com/t011ac9bd67c2ab3b2c.png)

**<br>**

**三、  代码分析**

和其他来自国外的“敲诈者”木马相同，“cerber3”敲诈者木马对反静态分析下了很大的功夫。**它通过在申请的虚拟空间中执行数据解密操作，并通过内存卸载和重新映射两个步骤将解密得到的数据写回内存中，从而完成一个“狸猫换太子”的任务。**处理完的程序和原先的程序完全不同，因此可以躲过绝大多数的静态扫描。

[![](https://p1.ssl.qhimg.com/t01711a649abacdb0fa.png)](https://p1.ssl.qhimg.com/t01711a649abacdb0fa.png)

图4 使用push retn更改执行流程至开辟的虚拟内存中

[![](https://p1.ssl.qhimg.com/t0185663b8b7918303e.png)](https://p1.ssl.qhimg.com/t0185663b8b7918303e.png)

图5 解除文件映射

程序将数据段读取的内容解密之后映射到内存中，从而完成整个程序内容的转换，至此真正的加密工作才开始进行。

加密工作的第一步就是用存储在文件中的RSA公钥加密一组随机数，作为本机唯一的初始密钥。

[![](https://p1.ssl.qhimg.com/t013fbf13a8a58a59a1.png)](https://p1.ssl.qhimg.com/t013fbf13a8a58a59a1.png)

图6 RSA公钥

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a502ed31717c96f9.png)

图7 公钥加密随机数函数

[![](https://p2.ssl.qhimg.com/t0123576777f7703b2b.png)](https://p2.ssl.qhimg.com/t0123576777f7703b2b.png)

图8 加密得到的本机统一密钥

获得本机初始密钥之后，将会使用该密钥去加密每个文件对应的唯一随机数，然后再对文件进行加密，完整的加密流程如下图所示。

[![](https://p1.ssl.qhimg.com/t01928c678bc0d440ce.png)](https://p1.ssl.qhimg.com/t01928c678bc0d440ce.png)

图9 加密流程

     然后将加密后的随机数密钥和加密后的本机专有密钥也存放到文件中。受害者交付赎金后，作者通过私钥解密得到本机专有密钥，再使用本机专有密钥分别解密每个文件使用的随机数密钥，最后解密每个文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c1dd40a0c39b8573.png)

图10 将两组密钥存放到文件中

<br>

**四、  总结**

“cerber3”敲诈者会破坏用户计算机中的重要文档，必须向其支付一定数额比特币才能对文档进行恢复，又由于对方所提供的地址都来自于暗网，因此国内用户计算机一旦感染此病毒将难以解决文件恢复的问题。

对于普通网民来说，可以从下面几个方面预防这类病毒：

**1.  对重要数据及时做备份，将备份存在多个位置，预防数据损坏丢失。**

**2.  打好系统和软件补丁，预防各类挂马和漏洞攻击。**

**3.  养成良好的上网习惯，不轻易打开陌生人发来的邮件附件。**

**4.  最重要的，用户应该选择一款可靠的安全软件，保护计算机不受各类木马病毒侵害。**

**并且对此360安全卫士开通了“反勒索服务”，并向用户公开承诺：使用360安全卫士并开启该服务后，仍然感染敲诈者病毒的话，360将提供最高3个比特币（约13000元人民币）的赎金帮助用户恢复数据，让用户远离财物及文档的损失。**

**<br>**
