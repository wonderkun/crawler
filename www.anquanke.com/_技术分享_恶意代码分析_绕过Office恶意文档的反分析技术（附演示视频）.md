> 原文链接: https://www.anquanke.com//post/id/86663 


# 【技术分享】恶意代码分析：绕过Office恶意文档的反分析技术（附演示视频）


                                阅读量   
                                **106058**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：ringzerolabs.com
                                <br>原文地址：[http://www.ringzerolabs.com/2017/08/bypassing-anti-analysis-technique-in.html](http://www.ringzerolabs.com/2017/08/bypassing-anti-analysis-technique-in.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0174647c71830f2b04.png)](https://p0.ssl.qhimg.com/t0174647c71830f2b04.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

****

在本文中，我们会分析一个带有VBA功能的恶意Word文档。文档的作者对文件中的VBA代码采取了密码保护措施，以避免研究人员检查恶意代码。同时，恶意代码开发者针对密码移除技术也做了相应的防护。自动化分析工具无法处理这一样本，但我们依然可以绕过这些反分析障碍，具体细节如下文所述。

大家可以先观看演示视频从直观上了解分析过程。



<br>

**二、样本细节**

****

打开恶意文档后，首先出现在我们眼前的是一则钓鱼信息，声称该文档使用早期版本的Microsoft Office创建，为了查看文档，用户需要启用宏功能。

[![](https://p4.ssl.qhimg.com/t0131dd5b8734e13fce.jpg)](https://p4.ssl.qhimg.com/t0131dd5b8734e13fce.jpg)

启用宏后，样本开始往cfai66.fr地址发送信息。

[![](https://p5.ssl.qhimg.com/t01cce3c610219d9011.jpg)](https://p5.ssl.qhimg.com/t01cce3c610219d9011.jpg)

为了了解具体是什么代码负责往法国地址发送信息，我们必须在“开发者”选项卡中查看文档的宏代码。然而，恶意代码作者对VBA代码做了加密处理，不想让我们检查代码。这种情况下，我们难以从Microsoft Office内部来精确分析VBA脚本。

[![](https://p2.ssl.qhimg.com/t01a6c852e53c18a975.jpg)](https://p2.ssl.qhimg.com/t01a6c852e53c18a975.jpg)

为了继续分析，我们可以尝试使用常见的十六进制编辑技术去掉Office文件中的密码。首先，我们在文档中搜索“DPB”字符串，将其改为“DPx”。某些版本的Office会把这个信息当成损坏的密码哈希。然而，这种方法对这个文档不起作用，我们仍然会看到密码提示框。

接下来，我们自己创建了一个密码保护的启用VBA功能的文档，然后继续尝试将样本文档中的“CMG”、“DPB”以及“GC”的值替换成我们自己文档中对应的值。不幸的是，恶意文档作者有意对“CMG”的值做了处理，使其超过了这个字段的长度值。因此，尝试替换样本的CMG值再次失败。此外，我们也尝试了在CMG引号内部及外部填充数据以保留文件的长度，但依然以失败告终（如下左图是我们构造的新文档，右图是恶意样本）。

[![](https://p4.ssl.qhimg.com/t01b8a4f758faaa45ed.jpg)](https://p4.ssl.qhimg.com/t01b8a4f758faaa45ed.jpg)

由于我们删除密码的尝试均告失败，接下来我们使用了OfficeMalScanner这个常用的Office产品分析工具来分析这个样本。利用这个工具的扫描（scan）/暴破（brute）功能，但没有得到任何结果。

[![](https://p2.ssl.qhimg.com/t013ef527e930a83214.jpg)](https://p2.ssl.qhimg.com/t013ef527e930a83214.jpg)

使用info选项再次运行这个工具，我们得到3个VBA对象：

[![](https://p0.ssl.qhimg.com/t01796bc081f6627f9a.jpg)](https://p0.ssl.qhimg.com/t01796bc081f6627f9a.jpg)

我们使用了ViperMonkey这个工具来动态分析这些VBA对象。ViperMonkey是个VBA仿真引擎，使用Python语言编写，用于Microsoft Office文档（如Word、Excel、PowerPoint、Publisher等）中的恶意VBA宏的分析及去混淆。

然而，ViperMonkey无法完整分析这些VBA，原因有两点：

1）无法识别UBound这个VBA函数。

2）无法分析“i = UserForm1.T.Top”这条语句的变量赋值操作，因为该工具无法定位UserForm1.T.Top的值。

[![](https://p2.ssl.qhimg.com/t01e083c64c78f6d990.jpg)](https://p2.ssl.qhimg.com/t01e083c64c78f6d990.jpg)

看样子我们需要手动分析Module1这个VBA脚本。首先，我们将这个脚本加载到一个新的Word文档中，以便使用内置的VBA调试器对其进行调试。在调试脚本中，我们很快就发现了导致ViperMonkey失效的那段代码。

[![](https://p2.ssl.qhimg.com/t01af64243f4655bcdc.jpg)](https://p2.ssl.qhimg.com/t01af64243f4655bcdc.jpg)

代码之所以无法运行，是因为Form1无法通过OfficeMalScanner工具导出。只有Form1的元数据被导出，导致Form1.T.Top的值无法找到。这种方法非常好，可以干扰自动化VBA分析工具的处理过程，因为密码保护表单的变量无法被获取到（这也是我所关心的变量）。我们不得不手动跟踪代码，逆向分析使用这个变量的函数，来尝试识别变量所对应的值。

[![](https://p0.ssl.qhimg.com/t01c225a7aec7dde842.jpg)](https://p0.ssl.qhimg.com/t01c225a7aec7dde842.jpg)

跟踪i=Form1.T.Top的变量赋值过程，我们发现代码最终将i分配给变量T，我们继续跟踪到代码的56行。

fr变量等于T-11，在第60行，Wet变量等于1-fr。

第62行表明，如果Wet=0，那么rd就等于变量rd的字符表现形式。

如果我们按照相反的逻辑处理顺序来分析这几条语句，我们可以得到以下结论：

为了使rd成为一个Char字符，Wet必须等于0：

```
vb Wet = 0 Wet = 1 - fr(1) = 0 fr = T(12) - 11 = 1 T(12) = i(12) = UserForm1.T.Top(12) UserForm1.T.Top == 12
```

[![](https://p1.ssl.qhimg.com/t01e4ae05194059c762.jpg)](https://p1.ssl.qhimg.com/t01e4ae05194059c762.jpg)

如果我们将UserForm1.T.Top的值替换为12，然后调试脚本，我们可以看到可读文本会逐渐填充到onearm变量中。我们成功逆向出了VBA的代码逻辑，提取出变量中所保存的批处理文件，如下所示：

[![](https://p0.ssl.qhimg.com/t019fdec2f610018980.jpg)](https://p0.ssl.qhimg.com/t019fdec2f610018980.jpg)

这个脚本会从cfai66.fr网站上（我们无法确定这个网站是不是被黑客攻陷的一个无辜网站）下载一个恶意的PNG文件（实际上这是个EXE文件），然后在受害者主机上执行这个文件。这个文件是个通用的木马程序，不属于某个特定的攻击组织。

[![](https://p5.ssl.qhimg.com/t016ffa6ed4b988c088.jpg)](https://p5.ssl.qhimg.com/t016ffa6ed4b988c088.jpg)



**三、总结**

****

这个样本是个非常有趣的包含VBA代码的Word文档，使用了密码保护机制以规避被分析的风险。经过若干次删除密码尝试，使用OfficeMalScanner以及ViperMonkey自动化工具对其分析后，我们最终选择了手动方式来逆向分析VBA函数，以寻找导致脚本调试过程失败的那个变量值，最终成功还原了恶意脚本。

<br>

**四、附录：样本信息**

****

文件名：efax543254456_2156.doc

保护机制：密码保护的VBA程序

MD5值：30B9491821923A1ECB5D221A028208F2

样本地址：点击[此处](https://www.reverse.it/sample/f756ea3c00d7a3dc3ff1c0224add01e8189375a64fbcd5c97f551d64c80cbdba?environmentId=100)下载样本

样本类型：微软Word VBA下载器

释放的文件：i.bat，npzdi.exe

网络流量：cfai66.fr/parabola.png， cfa-noisylegrand.com/parapola.png

在线分析结果：查看[此链接](https://otx.alienvault.com/pulse/599514487e26f94848cf58a2/)了解更多信息
