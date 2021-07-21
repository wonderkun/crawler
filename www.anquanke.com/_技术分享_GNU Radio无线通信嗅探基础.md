> 原文链接: https://www.anquanke.com//post/id/85189 


# 【技术分享】GNU Radio无线通信嗅探基础


                                阅读量   
                                **156406**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p4.ssl.qhimg.com/t01c1729dd14aa0fc80.png)](https://p4.ssl.qhimg.com/t01c1729dd14aa0fc80.png)**

****

**作者：**[**backahasten******](http://bobao.360.cn/member/contribute?uid=245645961)

**预估稿费：300RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**文章内容简介**

1.使用哪些grc模块完成我们的嗅探工作

2.如何选择参数以获取最完美的波形	

3.如何从波形还原回数据

我接下来会使用电视棒（RTL-SDR）嗅探一个固定码遥控锁开发组件。

[![](https://p0.ssl.qhimg.com/t0197e85dcbbef0d6c1.png)](https://p0.ssl.qhimg.com/t0197e85dcbbef0d6c1.png)

我使用如下的grc流图

[![](https://p3.ssl.qhimg.com/t014549ecad126876d2.png)](https://p3.ssl.qhimg.com/t014549ecad126876d2.png)

<br>

**模块选择与参数设定**

首先，rtlsdr_source中封装有电视棒的底层驱动，可以用它来获取原始的数据信号。

[![](https://p3.ssl.qhimg.com/t011020d6e3e1117972.png)](https://p3.ssl.qhimg.com/t011020d6e3e1117972.png)

samp_rate表示采样率，由于软件无线电使用的是带通采样定理，根据定理，我们的采样率应该为所需采样信号的2倍，这样才能保证信号不失真，使用大的采样率固然有好处，但是会带来巨大的内存和运算消耗。

下面两项分别是频率和频率误差，frequency中填写需要获取信号的中心频率。由于sdr设备，尤其是电视棒的精度并不高，频率选择会有误差，Freq_corr用来修正误差，我没有更高精度的设备来确定这个值，所以写0。

[![](https://p0.ssl.qhimg.com/t018a42ef6545cfa738.png)](https://p0.ssl.qhimg.com/t018a42ef6545cfa738.png)

还有其他一些参数，其中DC offset，IQ Balance  Mode选择自动（Automatic）即可。主要说一下Gain Mode ，RF Gain， IF Gain 和BB Gain 他们用来调整增益，如果不设置增益，信号的强度会很低，处理很麻烦，如果增益过大，信号在噪音中会很难识别出来。一般来说，Gain Mode 填自动即可。

[![](https://p1.ssl.qhimg.com/t016d5bd5f8d062655e.png)](https://p1.ssl.qhimg.com/t016d5bd5f8d062655e.png)

上图是低通滤波器的配置参数，采样率和rtl-sdr source保持一致，cutoff Freq填写一个信号的大概宽度。我们可以先使用gqrx来确定一下。

[![](https://p3.ssl.qhimg.com/t01690d2cba31b8e752.png)](https://p3.ssl.qhimg.com/t01690d2cba31b8e752.png)

我们可以看到一个尖峰，就是信号的位置，对应的瀑布图为红色，表示能量较高。由手册可知，这个模块使用ASK调制，信号范围比较窄，载根据上面的图，我们把截止频率设置为10KHz，就可以把大部分的信号截取下来。transition width为过度带宽，根据博客《利用GRC进行安全研究和审计 – 将无线电信号转换为数据包》的介绍，这个值应该选为信道带宽的百分之40到50，由于这个遥控器只会在一个位置发射，且ASK的信号范围很窄，所以我填了5KHz，它的选择是一个根据实际情况不断试错改正的过程。

接下来，我使用Complex to Mag对信号进行解调，去除载波。一般来说，发射的调制有调幅，调频和调相三种，分别使用能量大小的变化，频率的变化和波相位的变化表示数据，我们先来看看没解调之前的原始无线电信号是什么样的。

我们可以使用scope sink这个模块观察，但是由于计算机性能的问题，波形有很明显的延时和卡顿，所以我使用file_sink把它采集成一个文件，之后使用Audacity进行观察。

使用图：

[![](https://p5.ssl.qhimg.com/t016c763a763ccfbdfa.png)](https://p5.ssl.qhimg.com/t016c763a763ccfbdfa.png)

可以看到波形（注：没使用自动增益，RF，IF，BB增益各为30，对比请向下看）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b93f575b0453476e.png)

Complex to Mag解调之后，会把能量大致为0解为低电平，能量不为0解成高电平，如下图所示。

[![](https://p5.ssl.qhimg.com/t0134278a12091e39aa.png)](https://p5.ssl.qhimg.com/t0134278a12091e39aa.png)

大家可能会注意到，每一段的前几个峰值好像比较高，这是因为我们rtlsdr_source中Gain Mode设置为了自动，没有信号的时候，增益会比较大，以便获取信号，发现信号之后，会调整增益到合适的区间。在原始信号的波形中就没出现这种情况。推荐使用自动增益，这不会干扰后面的数据获取，手动增益有局限性，需要根据距离和发射强度调节，很麻烦。

之后我们使用Threshold进行脉冲信号的整理，

[![](https://p3.ssl.qhimg.com/t0198e51b460fc047c5.png)](https://p3.ssl.qhimg.com/t0198e51b460fc047c5.png)

小于0.2，为0，大一0.5，为一，处理之后波形如下。

[![](https://p3.ssl.qhimg.com/t01fc75208c53f0ef07.png)](https://p3.ssl.qhimg.com/t01fc75208c53f0ef07.png)

我们提取到了基带信号。无论是继续深入解出数字信息，还是进行重放攻击，获取基带信号都是非常大的帮助。只录取原始信号进行重放，无论是信号的强度还是质量都很差，而通过基带信号调制之后再发送，整体信号是可控的，效果会好很多，距离也会增加，也可以导入其他更小巧的设备。

<br>

**我们接下来还原数字信息**

这点一定要注意，不要主观臆断的认为高电平就是1，低电平就是0，数字通信中，基带信号也有很多种表示方法，甚至有的是不能经过Threshold处理（例如双极性归零波形），此时，最正确的方法是阅读芯片手册。

接收器上使用的芯片有两个，分别是LM358和PT2272，LM358是集成运放芯片，主要为信号的放大，对我们没有意义，PT2272是我们要关注的。PT2272详细信息不再赘述，我只说重点：

使用ASK调制（这点从遥控器的说明书我已经知道了）

发出的编码信号由：地址码、数据码、同步码组成一个完整的码字

而信道编码的定义如下：

[![](https://p4.ssl.qhimg.com/t010c5db423d52ed989.png)](https://p4.ssl.qhimg.com/t010c5db423d52ed989.png)

也就是说，a为时钟周期，4a高+12a低+4a高表示bit“0”,12a高+4a低+12a高表示bit“1”,4a高+12a低+12a高表示bit“f”，f只在地址码中使用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0150c3a4880d93e414.png)

这是每一帧的结构，也就是说，默认情况下，9个地址码，3个数据码，一个脉冲作为截断，一个帧携带3bit数据，应该有12*2+1也就是25个脉冲。

我们随意取出一帧波形，是遥控器上按“C”的时候发出的

[![](https://p2.ssl.qhimg.com/t01220f0684bf427a63.png)](https://p2.ssl.qhimg.com/t01220f0684bf427a63.png)

可以解出，数据为“FFFFFFFF0010”，（最后的脉冲是一个隔断）也就是，数据为“010”。

<br>

**一些杂七杂八的事情**

1.grc图集合了集中不同的GUI库，可以自行选择，但是只能选一个，如果发现无法运行，看看图形库的选择是否和模块对应。

2.解调方法我只介绍了ASK，其他请参阅《利用GRC进行安全研究和审计 – 将无线电信号转换为数据包》这篇文章，实战推荐参阅阿里巴巴谢君前辈的《如何远程控制别人的无线鼠标：深度揭露mouseJack内幕 》

3.大家可能感觉这种方式很麻烦，属实很麻烦，发射的时候更麻烦，使用专用芯片无论是从成本上还是复杂度上都很又是，推荐使用Arduino设备驱动芯片进行发射，Arduino就像是硬件届的Python，功能十分强大，编程也比较简单。SDR设备主要可以用来对复杂通讯的嗅探和发射（比如横行的伪基站就是SDR），当然，基础也是很关键的。

4.涉及很多通信的知识，我是学渣，有写错或者理解错的希望前辈留言勘误。

5.挖个坑，争取有时间写一篇使用Arduino进行嗅探的文章。
