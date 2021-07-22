> 原文链接: https://www.anquanke.com//post/id/86334 


# 【技术分享】Shellcode编程之特征搜索定位GetProcAddress


                                阅读量   
                                **101824**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：modexp.wordpress.com
                                <br>原文地址：[https://modexp.wordpress.com/2017/06/21/shellcode-getprocaddress/](https://modexp.wordpress.com/2017/06/21/shellcode-getprocaddress/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t010b5e166e05acdc29.jpg)](https://p2.ssl.qhimg.com/t010b5e166e05acdc29.jpg)

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**0x00 前言<br>**



最近， Alex lonescu表明Windows的发布版本中将包含将增强缓解措施工具包（EMET）编译到内核中。

[![](https://p2.ssl.qhimg.com/t01b73e7ba818905007.png)](https://p2.ssl.qhimg.com/t01b73e7ba818905007.png)

因为更多的缓解措施出现于MSVC和Windows操作系统中，定位API来利用内存崩溃漏洞变得越来越困难。

我就在想，如果导入地址表和导出地址表都不能访问了，是否有其他的方式来获得GetProcAddress？

下面你看到的就是我几个小时研究的成果，但没有铺开来研究IAT和EAT无法访问时如何获得GetProcAddress。

<br>

**0x01 特征检测**



用于检测恶意软件的每种算法可以重新利用来检测包括GetProcAddress在内的任何代码。

恶意代码的检测范围可以从简单的搜索字符串、常量（包括加密）或者代码字节序列到类似仿真和统计分析的高级方式。

通过特征定位GetProcAddress是一种尝试，因为它是唯一的返回错误码STATUS_ORDINAL_NOT_FOUND的函数。

从WindowsNT到Windows10，使用这个常量搜索kernel32.dll或者kernelbase.dll来定位GetProcAddress是很有可能的。

<br>

**0x02 搜索算法**



搜索算法的伪代码如下：

[![](https://p4.ssl.qhimg.com/t0111a9c8ee14fd95c8.png)](https://p4.ssl.qhimg.com/t0111a9c8ee14fd95c8.png)

理论上很简单，并且对于32位是有效的。

然而，如果对于一些DLL（尤其是64位的版本）中GetProcAddress使用函数块，那么就无效了。

在Windows7中，在kernelbase中定位我们的常量，是在代码块中。

[![](https://p0.ssl.qhimg.com/t013559118744384f74.png)](https://p0.ssl.qhimg.com/t013559118744384f74.png)

减去0x3FFFFEC8得到0xC0000138。

在Windows10中，常量在相同的GetProcAddress代码中，因此入口通过简单的搜索就能找到。

[![](https://p1.ssl.qhimg.com/t017ec79d3c37d151ed.png)](https://p1.ssl.qhimg.com/t017ec79d3c37d151ed.png)

为了能适应Windows7，我建议使用一个长度反汇编引擎（LDE）来模拟相关的跳转知道你定位到GetProcAddress，但是没有64位版本的LDE能独立的操作内存。也可能不需要？

因为我们搜索kernel32或者kernelbase的节，我们检查下PE节头结构，有个有趣的成员。

[![](https://p3.ssl.qhimg.com/t012303c6dc30692182.png)](https://p3.ssl.qhimg.com/t012303c6dc30692182.png)

**Misc.VirtualSize**

加载到内存的节的大小（字节），如果这个值大于SizeOfRawData，节将被填充0。这个字段只针对可执行映像有效，并且对于obj文件应该置为0.

**VirtualAddress**

加载到内存的节的第一个字节的地址（RVA）。对于obj文件，这是在重定位之前的第一个字节的地址。

**Characteristics**

映像的特征。因为我们搜索可执行代码，我们能测试这个值是否有IMAGE_SCN_CNT_CODE 或 IMAGE_SCN_MEM_EXECUTE。

一旦我们找到一个可执行区域，我们简单的搜索我们的特征，是一个4字节的序列：0x38, 0x01, 0x00, 0xC0。

如果找到了，我们假设我们在GetProcAddress的代码中，因此我们往回扫描内存来找到函数序言0x55, 0x8B, 0xEC（32位）和0x48, 0x89, 0x5C, 0x24, 0x08（64位）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01279d917cc9359647.png)

尽管从XP SP2开始大部分的32位的API在序言前有mov edi,edi以便热补丁，但是我们可以跳过它。

[![](https://p1.ssl.qhimg.com/t01bf6538731f5477e4.png)](https://p1.ssl.qhimg.com/t01bf6538731f5477e4.png)

64位上找到入口点的另一种方式是搜索编译器添加的填充（不同的编译器填充不同）。

函数是16字节对齐，会在GetProcAddress前后填充。

在Windows7上，使用0x90，在x86上是NOP指令。

[![](https://p1.ssl.qhimg.com/t0121b68c771e99fcb2.png)](https://p1.ssl.qhimg.com/t0121b68c771e99fcb2.png)

在Windows10中，使用0xCC，是软件中断（INT 3）。

[![](https://p0.ssl.qhimg.com/t01671dc9a17b87f1ab.png)](https://p0.ssl.qhimg.com/t01671dc9a17b87f1ab.png)

我提到它是因为在不同的搜索算法中这会很有用。

<br>

**0x03 C代码**



对于PEB中的每个DLL；

找到kernel32或者kernelbase；

[![](https://p2.ssl.qhimg.com/t0161da5c85f04fb476.png)](https://p2.ssl.qhimg.com/t0161da5c85f04fb476.png)

针对这个dll的每个节；

[![](https://p4.ssl.qhimg.com/t01502b7b3e3c688385.png)](https://p4.ssl.qhimg.com/t01502b7b3e3c688385.png)

找到特征，并反向扫描函数序言。

[![](https://p2.ssl.qhimg.com/t0143cf2ea9a99b3c3b.png)](https://p2.ssl.qhimg.com/t0143cf2ea9a99b3c3b.png)

<br>

**0x04 总结**



对于大部分32位的操作系统，他都能很好的工作，因为STATUS_ORDINAL_NOT_FOUND是在GetProcAddress函数的序言和结语之间的。但是在Windows7 x64上不能起作用，因为常量在外面。

**Windows7 32位（可以）**

[![](https://p5.ssl.qhimg.com/t01c7244107f946fd53.png)](https://p5.ssl.qhimg.com/t01c7244107f946fd53.png)

第一个地址偏了2字节，但是那是mov edi,edi指令，可以安全跳过

**Windows7 64位（不可以）**

[![](https://p4.ssl.qhimg.com/t01b6fe79c732b6ae3e.png)](https://p4.ssl.qhimg.com/t01b6fe79c732b6ae3e.png)

**Windows10 64位（可以）**

[![](https://p4.ssl.qhimg.com/t0134dccb101450f971.png)](https://p4.ssl.qhimg.com/t0134dccb101450f971.png)


