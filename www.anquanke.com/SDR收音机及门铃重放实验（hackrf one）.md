> 原文链接: https://www.anquanke.com//post/id/210399 


# SDR收音机及门铃重放实验（hackrf one）


                                阅读量   
                                **198119**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t012654430027f593e0.png)](https://p5.ssl.qhimg.com/t012654430027f593e0.png)



## 前记

硬件环境需要准备：hackrf，天线(40-860MHz)，门铃。

软件环境:gqrx，ubuntu18.04，audacity，hackrf工具

这里关于软件工具的搭建就不再赘述了，搭建过程有问题的同学可以找我探讨，本人也在学习阶段，欢迎交流！

那么言归正传，HackRF One是Great Scott Gadgets创建和制造的宽带软件定义无线电半双工收发器。注意是半双工，什么是半双工呢？半双工是数据传输指数据可以在一个信号载体的两个方向上传输，但是不能同时传输。也就是说，在同一时间内不能同时进行接收与发送操作，这就比较鸡肋了，但是在blade以及usrp的高昂价格面前这也就不是什么大问题了，哈哈哈哈。



## SDR收听FM广播

下图就是我的hackrf，是PORTAPACK版本所以长得不太一样。

[![](https://p3.ssl.qhimg.com/t01ca38d2eacd93d4cb.png)](https://p3.ssl.qhimg.com/t01ca38d2eacd93d4cb.png)

首先插入hackrf，因为我这边ubuntu是安装在vmware中，所以设备在插入物理机后选择连接到虚拟机中，然后在终端中输入hackrf_info或者SoapySDRUtil —find,如果返回下图中的信息，那么设备就已经连接成功了！

[![](https://p5.ssl.qhimg.com/t0123d62260d45fcaab.png)](https://p5.ssl.qhimg.com/t0123d62260d45fcaab.png)

然后继续在终端中输入gqrx -r开启工具,注意-r参数，因为直接输入gqrx可能会出现异常，当弹出下图窗口后，在Device中选择我们的设备，其他参数不动，然后点击ok进入工具。

[![](https://p5.ssl.qhimg.com/t0190945a2b3ebc345a.png)](https://p5.ssl.qhimg.com/t0190945a2b3ebc345a.png)

开启后，界面如下图。

[![](https://p3.ssl.qhimg.com/t01120c472ebe1366de.png)](https://p3.ssl.qhimg.com/t01120c472ebe1366de.png)

最左侧是频谱图，右侧我们需要重点注意的是Mode,AGC,以及Squelch。将Mode调整为WFM(mono),也就是宽带调频(单声道)，这样的音频质量相较于Narrow FM等要更高。点击左上角的三角形标志开始接收无线电信号。

Mode调整为WFM(mono)<br>
AGC调整至Fast。<br>
Squelch(静噪)进行调整，当听到吱吱的电流声后停止调整。

点击右下方input controls。<br>
将IF(中频)进行向右拖动至32dB<br>
BB(基带调频)拖动至52dB。

通常情况下，FM广播的频段是80-110MHZ,我们将频段调整至100MHZ，发现已经有一些波峰了，一般来讲这些就是广播频段了。

[![](https://p2.ssl.qhimg.com/t01c51a12c092d0b1de.png)](https://p2.ssl.qhimg.com/t01c51a12c092d0b1de.png)

我这里的环境下调整至107.600.000hz时已经听到清楚的广播声了，通过观察各个波峰基本可以找到广播频段。

注意事项:频段可以直接使用滚轮滑动调整。RF为射频增益，IF为中频增益，BB为基带增益。他们之间的关系是 接收：RF-IF-BB。也就是将RF高频信号转换为IF中频再到BB基带处理，经过两次变频。这样操作也是为了减少干扰，保证工作正常稳定。



## 无线门铃重放实验

关于门铃重放实验的原理，无非就是将门铃按钮的发送的信号通过hackrf接收并录制下来然后重放，让门铃收到发送的信号然后响起来。

首先我们需要做的就是确定门铃的发送频率以及接收频率。通过购买门铃时简介我们可以得知门铃按钮的发射频率是433.92MHZ，接收频率是433.92MHZ。

[![](https://p0.ssl.qhimg.com/t01f39b35af15946eb1.png)](https://p0.ssl.qhimg.com/t01f39b35af15946eb1.png)

在确认了频率后，我们总要验证一下不是。然后就去打开gqrx，将频率调整到433.92MHZ然后按下门铃。

[![](https://p0.ssl.qhimg.com/t011febb7b79d0adf14.png)](https://p0.ssl.qhimg.com/t011febb7b79d0adf14.png)

当按下按钮时，频谱图波峰升高，随后消失。从对应频率下方的黄色部分可以看到该频率产生了能量，间断按钮，发现能量的产生也随之中断产生。确定发射端频率为433.92MHZ。

输入命令:

`hackrf_transfer -r door.raw -f 433920000 -g 16 -l 32 -a 1 -s 8000000 -b 4000000`

然后执行，hackrf开始接收录制信号。在此时按下按钮，这里为了方便展示我间歇按了两次。然后Ctrl+c停止录制。

命令参数含义如下:

-r &lt;文件名&gt;＃将数据接收到文件中。<br>
[-f set_freq_hz]＃以Hz设置频率<br>
[-g gain_db]＃RX VGA(基带)增益, 0-62dB, 2dB steps<br>
[-l gain_db]＃设置低噪音放大器，0-40dB，8dB步进<br>
[-a set_amp]＃RX/TX射频放大器1=启用，0=禁用。<br>
[-s sample_rate_hz]＃设置采样率（Hz）（8/10 / 12.5 / 16 / 20MHz）<br>
[-b baseband_filter_bw_hz]＃设置基带滤波器带宽（MHz）。

[![](https://p0.ssl.qhimg.com/t015ebd2f7b8240b363.png)](https://p0.ssl.qhimg.com/t015ebd2f7b8240b363.png)

录制成功后我们打开audacity查看录制的原始文件(door.raw)。开启后弹出的窗口中的值不需要调整。点击文件，然后导入即可。如图我们可以看到有两部分，这就是我们录制两段响铃信号了，说明我们已经录制成功，可能有小伙伴会问为什么要用这个工具看这个文件？不是多此一举吗，这个我们下面再说。

[![](https://p0.ssl.qhimg.com/t01462ecc2e04e26b85.png)](https://p0.ssl.qhimg.com/t01462ecc2e04e26b85.png)

确定了录制文件没有问题后我们继续构建发送信号命令。

输入命令:

`hackrf_transfer -t door.raw -f 433920000 -x 47 -a 1 -s 8000000 -b 4000000`

命令参数含义如下:<br>
-t &lt;文件名&gt;＃从文件传输数据。<br>
[-x gain_db]＃设置TX vga增益，0-47dB，1dB步进

其他同上参数就不一一列举了。

[![](https://p0.ssl.qhimg.com/t014b9a9f534952283a.png)](https://p0.ssl.qhimg.com/t014b9a9f534952283a.png)

无线门铃成功播放，实验结束。

这里可能会出现如下几个问题：

1、因为之前介绍过hackrf是一个半双工的板子，所以有时候无法正常录制可以尝试重启一下设备即可解决。比如:<br>`hackrf_open() failed:Resource busy (-1000)`就是这个问题。

2、还需要注意一下,-f指定频率，上面我们讲到接收端与发送端的频率都是433.92MHZ，所以在我们构建接收或者发送命令时需要注意在自己具体的环境下进行调整。

3、关于其中的一些参数的值比如-s、-b、-x、-g、-l等这些值并不是固定的也可以根据自己具体的环境进行适当调整，上面的参数值仅提供参考。

3、-s指定采样率，采样频率越高，即采样的间隔时间越短，则在单位时间内计算机得到的样本数据就越多，对信号波形的表示也越精确。但这并不代表可以随意调整，仍需注意频率值的条件。

4、为什么要使用audacity来查看录制文件，因为在操作时，我发现有时可能会录制不成功，比如录制结束然后进行重放门铃无反应，这时我们就需要在该工具内通过放大镜查看是否成功录制，如果出现上面图中的信号那说明应该是录制成功了。

5、注意在测试时尽量远离高干扰的设备比如冰柜，大功率发射器等以避免影响实验效果，从而出现不理想的结果。



## 后记

以上就是hackrf收听FM广播以及重放实验的过程了，有问题的同学可以联系我共同学习。本文比较偏向基础，适合刚入门的同学，希望看过这篇文章能够对您有所收获。

祝大家前程似锦，心想事成！
