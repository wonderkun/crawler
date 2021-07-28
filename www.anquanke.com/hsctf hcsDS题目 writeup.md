> 原文链接: https://www.anquanke.com//post/id/245488 


# hsctf hcsDS题目 writeup


                                阅读量   
                                **20657**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01de890498193d8582.png)](https://p1.ssl.qhimg.com/t01de890498193d8582.png)



在今年的hsctf(“High School Capture the Flag”)里遇到了一个比较少见的nds(任天堂DS)逆向题目,侥幸拿下一血,因为感觉网上整理好的相关资料比较少在这里分享给大家。



## 基本介绍

NDS：任天堂DS，是电玩游戏生产商任天堂公司2004年发售的第三代便携式游戏机。主要的特征包括了双屏幕显示，其中下方的屏幕为触摸屏；并配置有麦克风声音输入装置和 Wi-Fi 无线网络功能。<br>
这里题目提供了一个chall.nds的文件，一个nds的ROM文件,可以在pc上使用模拟器来加载运行,在这里我使用的是DeSmuME模拟器。



## 解题

### <a class="reference-link" name="%E8%A7%82%E5%AF%9F%E9%A2%98%E7%9B%AE%E5%A4%A7%E8%87%B4%E5%8A%9F%E8%83%BD"></a>观察题目大致功能

首先我们使用模拟器加载题目,可以看到是一个需要通过三关才能拿到flag的游戏。如下图所示

[![](https://p1.ssl.qhimg.com/t019bb6b9433c6a15cf.png)](https://p1.ssl.qhimg.com/t019bb6b9433c6a15cf.png)

按下回车后进入第一关

[![](https://p0.ssl.qhimg.com/t01674b1d6be19325de.png)](https://p0.ssl.qhimg.com/t01674b1d6be19325de.png)

可以看到是要输入数据才可以通过下一关。由于DeSmuME并不能下断进行调试，只能看反汇编和寄存器的值这里我们继续考虑静态分析。

### <a class="reference-link" name="%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90%E5%87%86%E5%A4%87"></a>静态分析准备

打开IDA发现并不能识别它的架构程序基址等等，这里我在github上搜到了一个nds的IDA loader插件<br>[https://github.com/EliseZeroTwo/IDA-NDS](https://github.com/EliseZeroTwo/IDA-NDS)<br>
安装插件后即可识别代码。需要注意的是程序中有ARM7和ARM9的代码,如果只识别ARM7则不能在IDA中看到全部函数。插件会弹框告诉你。识别结果如下图。

[![](https://p1.ssl.qhimg.com/t01b6f33b8cf9bf98bf.png)](https://p1.ssl.qhimg.com/t01b6f33b8cf9bf98bf.png)

可以看到识别出了很多的函数，那么下一步就是需要定位到,处理的代码在哪。<br>
这里我们可以通过静态分析或者观察DeSmuME运行时的pc寄存器的值来确定处理数据的代码位置。

### <a class="reference-link" name="%E5%AE%9A%E4%BD%8D%E5%A4%84%E7%90%86%E4%BB%A3%E7%A0%81%E4%BD%8D%E7%BD%AE"></a>定位处理代码位置

在进入第一关之后等待输入时,PC的值为2005B24我们在IDA找到这个位置,位于2005AD0这个函数中。猜测这个函数的功能就是获取输入，这里查看其引用发现上层函数只有一个，再查看上层引用如下图(注:其中的stage1 stage2 stage3是我后来改的函数名,原本的程序是没有符号表的)。

[![](https://p2.ssl.qhimg.com/t01885e5cd80f9e1d79.png)](https://p2.ssl.qhimg.com/t01885e5cd80f9e1d79.png)

我们挨个进入函数查看其功能。在我标记的stage1(0x2000D4C)中发现了这样一段代码。

[![](https://p4.ssl.qhimg.com/t018e0368b28a9d73e4.png)](https://p4.ssl.qhimg.com/t018e0368b28a9d73e4.png)

猜测这里是对我们输入数据的校验。也就是stage1的代码。<br>
再查找stage1的引用定位到函数0x2002e18如下图

[![](https://p1.ssl.qhimg.com/t011f84b6e4070a025f.png)](https://p1.ssl.qhimg.com/t011f84b6e4070a025f.png)

猜测接下来的函数是stage2 stage3 后面验证果然如此

### <a class="reference-link" name="stage1"></a>stage1

观察函数执行流程,确定了此处为比较位置

[![](https://p3.ssl.qhimg.com/t0144d8658ef8fd7494.png)](https://p3.ssl.qhimg.com/t0144d8658ef8fd7494.png)

得到正确的输入cuteblueicecube<br>
输入之后进入stage2

[![](https://p4.ssl.qhimg.com/t01b149958a2723175a.png)](https://p4.ssl.qhimg.com/t01b149958a2723175a.png)

### <a class="reference-link" name="stage2"></a>stage2

第二阶段如下图

[![](https://p4.ssl.qhimg.com/t0173ded44778acac35.png)](https://p4.ssl.qhimg.com/t0173ded44778acac35.png)

猜测是点击图片上的字来通过。<br>
继续分析stage2的代码<br>
在其中发现这样一段代码

[![](https://p1.ssl.qhimg.com/t014fe184bb8a7d646d.png)](https://p1.ssl.qhimg.com/t014fe184bb8a7d646d.png)

可以看到之前在stage1中出现的获取输入的函数<br>
确定输入的位数为8位数也就是说应该点击界面上带数字的小方格八次。<br>
继续看下面可以看到有一段进行验证的代码

[![](https://p2.ssl.qhimg.com/t01ff78bd8a6b5b96cb.png)](https://p2.ssl.qhimg.com/t01ff78bd8a6b5b96cb.png)

代码实现了多个方程,对输入进行校验,其中使用的2014DB8为除法。这里使用Z3解方程,解开后将得到的值在屏幕上点击即可进入下一关,由于出题人并不够严谨导致方程有多个解。通过后进入第三关

[![](https://p1.ssl.qhimg.com/t01497b6901ca078230.png)](https://p1.ssl.qhimg.com/t01497b6901ca078230.png)

### <a class="reference-link" name="stage3"></a>stage3

第三阶段走迷宫需要把鸟移到左下角

[![](https://p1.ssl.qhimg.com/t01ef10b2e580a59ea2.png)](https://p1.ssl.qhimg.com/t01ef10b2e580a59ea2.png)

但在实际中我们移到一半就发现下面有一堵墙,挪不动了,这时候想到小时候玩游戏魂斗罗之类的有作弊码,那作者很有可能也设置了这样的一段代码。这时候我们需要看一下IDA的代码。发现了可疑的一部分，如下图。

[![](https://p3.ssl.qhimg.com/t0143690adc28178424.png)](https://p3.ssl.qhimg.com/t0143690adc28178424.png)

猜测这里就是作弊码，接着看代码如何满足条件进入这里。

[![](https://p1.ssl.qhimg.com/t01da853c4753d0c60c.png)](https://p1.ssl.qhimg.com/t01da853c4753d0c60c.png)

在这里发现需要v76以一定的顺序执行这几个赋值就可以通过检测。通过看代码可知v76是r4寄存器,而后观察模拟器按键设置

[![](https://p4.ssl.qhimg.com/t0194828be9c1324848.png)](https://p4.ssl.qhimg.com/t0194828be9c1324848.png)

按下QWASZX对应的键位即可让r4寄存器产生我们需要的值,接下来就是确定它的顺序。

```
v121 == 50 &amp;&amp; v117 == 30 &amp;&amp; v122 == 60 &amp;&amp; v118 == 70 &amp;&amp; v120 == 40 &amp;&amp; v119==80
```

最终确定按键顺序为xsazwq<br>
按下后中间的墙壁消失了。小鸟成功走到了右下角。

### <a class="reference-link" name="final"></a>final

在通过三个阶段后界面如下图

[![](https://p3.ssl.qhimg.com/t01964a003157567633.png)](https://p3.ssl.qhimg.com/t01964a003157567633.png)

这里把我们的输入拼接成flag即可,需要注意的是第三阶段需要提交的是任天堂游戏机的真正按键,这里我们根据模拟器键位得到真正的游戏机键位。<br>
最终flag为<br>
flag`{`cuteblueicecube_1-16-20-6-21-4-16-18_A-X-Y-B-R-L`}`<br>
由于第二阶段是多解,第二阶段输入为1-16-20-6-21-4-16-18 成功通过



## 小结

题目难点主要是，陌生的架构,以及模拟器不能进行下断调试等(可能有模拟器可以调试?知道的大佬可以提点一下我QAQ)
