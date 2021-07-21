> 原文链接: https://www.anquanke.com//post/id/101017 


# 爱国者HDD硬盘破解教程（上集）


                                阅读量   
                                **125135**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://syscall.eu
                                <br>原文地址：[https://syscall.eu/blog/2018/03/12/aigo_part1/](https://syscall.eu/blog/2018/03/12/aigo_part1/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0124c230a2f4364176.png)](https://p0.ssl.qhimg.com/t0124c230a2f4364176.png)

## 介绍

长期以来，我个人的爱好就是分析和破解外部加密HDD硬盘驱动器。在此之前，我和我的同事Joffery Czarny以及Julien Lenoir曾经对下面这几款型号的设备进行过分析测试：<br>
-Zalman VE-400<br>
-Zalman ZM-SHE500<br>
-Zalman ZM-VE500<br>
而在今天的这篇文章中，我将会跟大家分享我对爱国者SK8671移动硬盘的分析成果。这块移动硬盘是我的一名同事给我的，它符合外部加密HDD的传统设计理念，并带有LCD信息显示屏以及一块用来输入密码的物理键盘。<br>
注：本系列文章中的所有研究内容都是我个人在闲暇时间完成的，与我的公司没有任何关系。<br>
硬件设备图如下所示：<br>[![](https://p5.ssl.qhimg.com/t01890baf4734232741.jpg)](https://p5.ssl.qhimg.com/t01890baf4734232741.jpg)<br>
爱国者SK8671移动硬盘外包装如下图所示：<br>[![](https://p1.ssl.qhimg.com/t01b8a074ab93deeb04.jpg)](https://p1.ssl.qhimg.com/t01b8a074ab93deeb04.jpg)<br>
用户必须输入密码才可以访问移动硬盘内的数据，而硬盘内的数据理应是经过加密处理的。<br>
需要注意的是，硬盘本身提供的操作选项非常有限：<br>
-在解锁之前按下F1键，可修改PIN码。<br>
-PIN码必须为长度在6-9位之间的数字。<br>
-采用了错误PIN码计数器，输入密码错误十五次之后会销毁硬盘中的所有数据。

## 硬件设计

当然了，我们首先要做的就是把设备的外壳拆开，然后看看电路板上都有哪些组件。拆开外壳的过程就是各种拧螺丝，然后拆开塑料外壳。最后，我们得到了如下图所示的组件：<br>[![](https://p5.ssl.qhimg.com/t012b604dfec0c04261.png)](https://p5.ssl.qhimg.com/t012b604dfec0c04261.png)

## 主PCB板

这款设备的主PCB板设计其实非常简单：<br>[![](https://p1.ssl.qhimg.com/t01889733061cb9fb4b.png)](https://p1.ssl.qhimg.com/t01889733061cb9fb4b.png)<br>
我们从上往下看，最重要的部分分别为：<br>
1． 连接LCD PCB板（CN1）的连接器；<br>
2． 蜂鸣器（SP1）；<br>
3． Pm25LD010 SPI闪存（U2）；<br>
4． Jmicron JMS539 USB-SATA控制器（U1）；<br>
5． USB 3连接器（J1）；<br>
其中，SPI闪存存储的是JMS539固件以及其他的一些设置信息。

## LCD PCB板

LCD显示屏的PCB板其实没什么特别的，其结构图如下所示：<br>[![](https://p3.ssl.qhimg.com/t01b400262d7da08b32.png)](https://p3.ssl.qhimg.com/t01b400262d7da08b32.png)<br>[![](https://p5.ssl.qhimg.com/t018bb102b3af63f4be.png)](https://p5.ssl.qhimg.com/t018bb102b3af63f4be.png)<br>
电路板上的组件如下：
1. 一个未知品牌的LCD字符显示屏（可能为中国产），带有串行控制接口；
<li>一个连接键盘PCB板的带状连接器；<br><h3 name="h3-4" id="h3-4">
<a class="reference-link" name="%E9%94%AE%E7%9B%98PCB%E6%9D%BF"></a>键盘PCB板</h3>
<p>当我们开始分析键盘PCB板之后，有意思的地方就来了：<br>[![](https://p3.ssl.qhimg.com/t016427a836dfa1f1d5.png)](https://p3.ssl.qhimg.com/t016427a836dfa1f1d5.png)<br>
在键盘PCB板的背面，我们可以看到一个带状连接器和一个Cypress CY8C21434 PSoC 1 微型控制器（我一般把它称作“µC”或“PSoC”）：<br>[![](https://p5.ssl.qhimg.com/t012682f7a1cd855f1a.png)](https://p5.ssl.qhimg.com/t012682f7a1cd855f1a.png)<br>
CY8C21434使用了M8C指令集，这种指令集在这份【汇编语言用户指南】中有详细介绍。<br>
根据爱国者官方网站产品页上的介绍，这款产品支持CapSense，即Cypress的电容式键盘技术。你可以从一开始的电路板整体图片中看到，我焊接的是标准ISSP编程Header。</p>
<h3 name="h3-5" id="h3-5">
<a class="reference-link" name="%E7%94%B5%E8%B7%AF%E5%88%86%E6%9E%90"></a>电路分析</h3>
<p>在分析一款硬件设备时，了解设备电路的连接情况可以很好地帮助我们对设备的运行机制进行分析。这款设备的电路板有一个相对比较“庞大”的连接器，我们可以使用一个连续测试模式下的万用表来识别电路板中的线路连接情况：<br>[![](https://p3.ssl.qhimg.com/t01c08ef7607d30d62d.png)](https://p3.ssl.qhimg.com/t01c08ef7607d30d62d.png)<br>
可能这样看的话电路板就有些乱了，所以我们给大家提供以下描述来帮助大家更好地理解：</p>
</li>
1. PSoC代表的是数据表；
1. 右边下一个连接器为ISSP头，网上的资料非常完整，这里就不再进行赘述；
1. 最右边的连接器是连接到键盘PCB上的带状数据线；
<li>加粗黑色框中画的是主PCB 板上的CN1连接器，它的线缆连接的是LCD的PCB板。P11、P13和P4连接的是PSoC针脚11、13和4；<br><h3 name="h3-6" id="h3-6">
<a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%AD%A5%E9%AA%A4"></a>攻击步骤</h3>
既然现在我们已经知道了这款设备的内部结构以及各个组件的情况，那么接下来我们就要对这款设备进行攻击分析了，而这里所采用的基本步骤跟我们之前分析设备时所采用的是一样的：
</li>
1. 确保使用了基本的加密功能；
1. 了解加密密钥的生成方法和存储方式；
<li>寻找验证用户PIN码的位置（代码或功能组件）；<br>
但是在我们实际的分析过程中，我们的主要精力并不会放在破解该设备的安全性身上，我们的目标只是娱乐为主。我的实验操作过程如下：</li>
1. 导出SPI闪存内容；
1. 尝试导出PSoC闪存内存数据；
1. 开始编写测试报告；
1. 通过测试后发现，Cypress PSoC和JMS539之间的通讯数据中包含键盘记录信息；
1. 当密码修改之后，SPI闪存中并不会存储任何信息；
1. 我也懒得对JMS539固件（v8051）进行逆向分析了；
<li>TBD：完成针对该设备的整体安全性分析；<br><h3 name="h3-7" id="h3-7">
<a class="reference-link" name="%E5%AF%BC%E5%87%BASPI%E9%97%AA%E5%AD%98"></a>导出SPI闪存</h3>
<p>导出SPI闪存内容这一步还是比较简单的：<br>
首先，我们要将数据线跟闪存的CLK、MSOI、MISO和EN针脚相连接，然后使用一个逻辑分析工具（我使用的是Saleae Logic Pro 16）来嗅探通信数据。接下来，解码SPI协议并将分析结果以CSV格式输出。最后，使用decode_spi.rb对输出结果进行解析，并得到最终的SPI闪存数据。<br>
需要注意的是，这种操作方法非常适用于JMS539，因为它会在设备的启动过程中从缓存将整个固件全部加载进来。<br>
`$ decode_spi.rb boot_spi1.csv dump<br>
0.039776 : WRITE DISABLE<br>
0.039777 : JEDEC READ ID<br>
0.039784 : ID 0x7f 0x9d 0x21</p>
</li>
### <a class="reference-link" name="%E7%94%B5%E8%B7%AF%E5%88%86%E6%9E%90"></a>电路分析

### <a class="reference-link" name="%E5%AF%BC%E5%87%BASPI%E9%97%AA%E5%AD%98"></a>导出SPI闪存

0.039788 : READ @ 0x0<br>
0x12,0x42,0x00,0xd3,0x22,0x00,<br>
[…]<br>
$ ls —size —block-size=1 dump<br>
49152 dump<br>
$ sha1sum dump<br>
3d9db0dde7b4aadd2b7705a46b5d04e1a1f3b125 dump`<br>
不幸的是，我们在测试过程中这种方法貌似并没那么有效，因为当我们修改了PIN码之后，闪存内容并没有发生改变，而且在设备启动之后闪存内容也没有真正被访问过。所以说，我认为设备可能只存储了JMicron控制器（潜入了一个8051微型控制器）的固件。

## 嗅探通信流量

如果你想要弄清楚每一块芯片具体负责的是哪些任务，最好的方法就是检查其通信数据。我们都知道，USB-SATA控制器是跟屏幕相连接的，并通过CN1连接器和两个带状线缆与Cypress µC相连。所以我们用数据线与这三个相关的针脚进行连接，即P4、P11和P13。<br>[![](https://p3.ssl.qhimg.com/t01b5bbb29156ddc469.jpg)](https://p3.ssl.qhimg.com/t01b5bbb29156ddc469.jpg)<br>
接下来，启动Saleae逻辑分析工具，设置好触发器之后在键盘上输入“123456✓”。接下来，我们将会看到如下图所示的界面：<br>[![](https://p2.ssl.qhimg.com/t013bdf14d0e6c0e0f9.png)](https://p2.ssl.qhimg.com/t013bdf14d0e6c0e0f9.png)<br>
你可以看到三种不同类型的通信数据，在P4信道上是一些短脉冲信号，在P11和P13上大多是连续的交流信号。放大第一个P4脉冲信号（上图中蓝色线条标注的位置）之后，我们得到了如下图所示的数据：<br>[![](https://p0.ssl.qhimg.com/t01a3dac7cb646d3f82.png)](https://p0.ssl.qhimg.com/t01a3dac7cb646d3f82.png)<br>
你可以从上图中看到，P4脉冲信号大多都是70ms的纯规则信号，这种信号规则符合时钟的特征。但是在进行了进一步分析之后，我发现它只是用户每次按下物理键盘按键时发出了“哔哔”声…所以这部分数据对我们来说就没什么价值了，不过我们可以从中了解到PSoC对每一次键盘击键的注册信息。<br>
可能有些细心的同学已经发现了，在第一张P4脉冲信号图中有一个跟其他不同的脉冲信号（“哔哔声”），而它代表的是“错误的PIN码”！放大了左后一个P4脉冲信号之后，我们得到了如下图所示的数据：<br>[![](https://p0.ssl.qhimg.com/t01cef2494adcfb2d57.png)](https://p0.ssl.qhimg.com/t01cef2494adcfb2d57.png)<br>
大家可以看到，这里我们得到的是有规则的电波信号，以及在最后“错误的PIN码”出现之后的信号变化模式。<br>
一般来说，双线协议通常是SPI或I2C，而Cypress数据集表明这些针脚跟I2C有关，这也符合我们的测试情况：<br>[![](https://p1.ssl.qhimg.com/t01751c60c911de87d6.png)](https://p1.ssl.qhimg.com/t01751c60c911de87d6.png)<br>
USB-SATA芯片会不断地让PSoC去读取键位状态，默认情况下为“0”，当用户按下键盘“1”之后，状态值将会改变成“1”。当用户按下“✓”键之后，如果用户已经输入了有效的PIN码，则最终的通讯数据将会发生改变。但是，我现在还没有对实际的传输数据进行测试，不过传输的内容中似乎并没有加密密钥的存在。

## 总结

在本系列文章的上集中，我们对爱国者SK8671移动硬盘的内部构造以及电路板运行情况进行了分析，在本系列文章的下集，我们将会告诉大家如何导出PSoC内部闪存数据，感兴趣的同学请关注《安全客》的最新资讯。
