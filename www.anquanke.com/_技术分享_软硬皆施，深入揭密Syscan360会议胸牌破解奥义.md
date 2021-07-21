> 原文链接: https://www.anquanke.com//post/id/85108 


# 【技术分享】软硬皆施，深入揭密Syscan360会议胸牌破解奥义


                                阅读量   
                                **102485**
                            
                        |
                        
                                                                                    



**![](https://p3.ssl.qhimg.com/t01989be81f1e6fc946.jpg)**

**<br>**

**作者：阿里安全IoT安全研究 谢君**

**背景**



有幸参加今年11月份的上海Syscan360安全会议，会议期间有一个亮点就是360的独角兽团队设计了一款电子badge(胸牌)供参加人员进行破解尝试，类似于美国Defcon上面的那种解密puzzle的比赛，在参会现场的人都可以参加这种破解，总共9道题，规则是现场会给每道题谜面，在这块胸牌上面输入正确的谜底才能进入下一题，解题需要开脑洞，有好些人参与破解，而且有好些人都解出来了，今天笔者从这块胸牌的硬件和软件层面去揭密这个胸牌的一些有意思的功能和如何在不需要知道谜面的情况下，快速解密答案，算是硬件破解方面抛砖引玉。

 

**初识篇**



我这边看到有两块板，一块黑色一块红色，其中黑色如下：

![](https://p1.ssl.qhimg.com/t010254304e0f729e06.png)![](https://p2.ssl.qhimg.com/t01fcdd6c2eff216684.png)

**硬件配置如下：**

MCU: 德州仪器TI CC1310 型号（CC1310F64RGZ）VQFN (48) 7.00 mm × 7.00 mm

ARM Cortex-M3处理器,时钟速度高达48Mhz

64KB片上可编程flash，20KB静态内存SRAM，30个GPIO口

RF Core支持收发1Ghz以下的无线信号

外置存储器: Winbond 25Q32bvsig

32Mbits存储空间

一个LCD液晶屏

四个led灯，若干电阻和电容，6个按键和开关，所有的这些构成一个小型的嵌入式系统

**使用方法：**

6个按键，分别负责切换不同的可打印的ASCII码，删除，进入和返回等功能。

只有所有的关卡通过后才能出现控制闪灯和产生红外信号去关闭遥控电视的功能，这是后话，后面细讲。

 

**硬件篇**

要想了解里面的原理和功能，必须得拿到里面的代码逻辑。通过查阅MCU CC1310芯片的数据手册，我们发现它支持jtag仿真调试，我们只需要外挂支持ARM的仿真器，就可以进行整个内存空间的访问和片上动态调试，这一点对于我们逆向来讲非常有帮助，CC1310芯片布局如下。

![](https://p2.ssl.qhimg.com/t0140e98970a764c00e.png)



```
DIO_16 26 Digital I/O GPIO, JTAG_TDO, high-drive capability
DIO_17 27 Digital I/O GPIO, JTAG_TDI, high-drive capability
```

我们知道要进行jtag调试需要至少4根信号线分别是TMS,TCK,TDI,TDO，(RST可选)最后是GND(接地), 具体JTAG的定义和各个信号线的定义大家可以网上搜索，我就不赘述了，找到这几个信号线接到相应的仿真器上就可以进行调试了。

从该MCU的电子手册我们得知这四个信号线的Pin脚位置如下。    

```
TMS                     24
          TCK                    25
          TDO                    26
          TDI                     27
```

然后我们可以通过万电表量出这几个引脚引出来的位置，刚好这板子已经把这几个信号脚引出来了，也省去我们不少麻烦。

![](https://p4.ssl.qhimg.com/t01e43cdc45c9d0ef01.png)

好了，焊好线后，需要我们的仿真器出场了，笔者使用的ft2232h mini module，当然大家也可以选用别的仿真器，像jlink之类的，简单说一下这个mini module，它是一个多硬件协议(MPSSE)集一身的小模块，比如SPI/JTAG/I2C等，共用GPIO口，非常方便，接下来就是连线了，连接图如下。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

右边是mini module CN-2接口Pin脚，左边是CC1310的引脚，GND随便找一个板子接地的地方接上就好了。

下面就是ft2232h mini module。

![](https://p3.ssl.qhimg.com/t01845e444e14a9c639.png)

好了，接下来就是激动人心的时刻了。

<br>

**软件篇**



硬件连接准备就绪后，我们开始驱动仿真器来进行片上调试。

调试工具准备如下：

OpenOCD (开源的硬件调试软件)

Arm-none-eabi-gdb (arm版的gdb)

在使用openocd之前需要准备好cc1310的调试配置文件cc1310.cfg，在

[http://openocd.zylin.com/gitweb?p=openocd.git;a=blob;f=tcl/target/cc1310.cfg;h=8f86bd4b965a02922ae1abc98f53c8a4c65f9711;hb=27c749394270555698e3f5413082d5c6898d8151 ](http://openocd.zylin.com/gitweb?p=openocd.git;a=blob;f=tcl/target/cc1310.cfg;h=8f86bd4b965a02922ae1abc98f53c8a4c65f9711;hb=27c749394270555698e3f5413082d5c6898d8151%BF%C9%D2%D4%D5%D2%B5%BD) 可以找到。

一切准备妥当，接下来就可以开始见证奇迹的时刻了。

![](https://p0.ssl.qhimg.com/t0151ecfafee5f0099f.png)

运行telnet localhost 4444进行命令行来控制操作cpu或者内存空间，在这里我们可把cpu halt暂停下来，cpu重置，设置断点等操作。

在这里我们执行halt命令，cpu就断下来了，效果如下

这个时侯我的gdb就可以远程attach上去进行动态调试与内存空间访问了。

![](https://p4.ssl.qhimg.com/t013480a54bd9e324f3.png)

运行arm-none-eabi-gdb，gdb里面执行target remote localhost:3333

进行远程调试连接，可以内存空间访问与动态调试。

![](https://p3.ssl.qhimg.com/t011c8f6189a0f7dd3e.png)

好了，我们可以内存空间访问了，先把固件，flash，和内存数据dump出来，静态分析一下吧。

如下是cc13xx芯片的内存空间地址映射表，它可以让我们知道dump哪些有用的数据。

![](https://p0.ssl.qhimg.com/t0198d632c21fafd150.png)

0地址开始到0x10000是我们CC1310F64型号的flash的地址空间

BootROM是从0x10000000到0x10020000

SRAM地址从0x20000000到0x20005000

好了，我们就dump这三块位置。

在gdb里面运行如下命令：



```
dump binary memory cc1310_flash.bin 0 0x10000
dump binary memory cc1310_brom.bin 0x10000000 0x10020000
dump binary memory cc1310_sram.bin 0x20000000 0x20005000
```

好了，合并这三个文件用IDA进行反汇编，不同的段进行地址重定位，可以做到地址精确引用，如下。

![](https://p1.ssl.qhimg.com/t01329e62d4a3048ae2.png)

好了，接下来就是逆向篇了，如何找到答案和分析其代码逻辑等等。

<br>

**逆向篇**



我们通过IDA里面的一些字符串获得一些线索。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

然后我们很快找到每一道题的答案了。

![](https://p2.ssl.qhimg.com/t01f0f8ab66248f8af1.png)

解释一下这里面的一些逻辑。

这里面每一道题的提示和答案，还有用户自定义ID存储在flash 0xe000开始的区域里面，总共长度0xe2个字节，运行时会把这块区域数据读到SRAM里面，在SRAM里面进行操作，然后把SRAM结果写回到0xe000这块区域里，以保证下次设备重启数据和进度不会丢失，其结构如下。

0xe000 —0xe010 存储用户设置的ID

0xe014 — 0xe015 存储用户过了多少关了（直接改成9就通关了：），修改SRAM里面相应的存储的数据，然后通过ID设置来触发写回到0xe014，这样就生效了）

如下是不同关卡的提示和答案：

![](https://p5.ssl.qhimg.com/t0169867153f03c1c5d.png)

![](https://p4.ssl.qhimg.com/t01367bb254fdff6727.png)

比较每一个关卡的用户输入答案，并进行更新

![](https://p5.ssl.qhimg.com/t01884f3774235bc621.png)

0x20001060存储着flash地址0xe000里面的数据

偏移0x14就是用户当前所在关卡数，如果答案比较相等，这个关卡数加1并写回到flash里面，并在屏幕上显示『right!』。

**总共9道题的答案分别是：**



```
UR1NMYW0RLD!
42
ORDREDUTEMPLE
FQJPVDPOK
VYTX
LOYAL
GNILCS
FIBONACHI
WORLD
```

通关最后的结果如下：

![](https://p5.ssl.qhimg.com/t01f20649f41be60337.png)

如果你只想知道答案，看到这里就可以了，接下来会讲讲里面的一些其它功能。

<br style="text-align: left">

**探密TVB Gone功能篇**



当所有的关卡都通过后，会多出来两项列表，分别是：<br>

6. Led Light

7. TVB Gone
 进入Led Light前置的两个led灯可以显示3种颜色，这里是通过设置12号GPIO和19号GPIO口，对应在芯片上的引脚是18和29.
 这里我们重点关注这个TVB Gone功能，这个一个可以通过红外信号远程关闭很多不同品牌的电视的小应用，具体介绍参考[https://en.wikipedia.org/wiki/TV-B-Gone](https://en.wikipedia.org/wiki/TV-B-Gone)
我们知道我们家里面使用的电视的遥控器，一般都是发射的红外信号，来控制电视的开关，调台等操作，这个TVB Gone的功能就是通过发射不同品牌和不同频率的控制信息来达到关闭遥控电视的目的。
红外控制信号通过一定频率的PWM(脉冲宽度调制)调制方式输出给led灯，led灯产生的红外信号影响遥控电视。
研究发现这个板子里面存储了80组红外控制信号源数据，通过特定的数据结构来存储，例如如下。
![](https://p0.ssl.qhimg.com/t01f41f7dd7550b64ba.png)
如下是存储每一组数据的地方指针列表
![](https://p3.ssl.qhimg.com/t011c660b270886cb60.png)
我们挑选其中一组来看
![](https://p1.ssl.qhimg.com/t011205d0ece70bbe35.png)
解释一下每个字段的含义：
0x9600：表示这种数据的发射频率38400Hz
0x1a：表示有多少对数据需要发送出去
0x02：表示每发送一对信号里面承载着2个bit数据
0x9e38：表示存储时间对的指针地址
0x97b4：表示要发送的数据的指针地址
地址0x97b4在存储的数据如下：
`{`0xe2, 0x20, 0x80,0x78,0x88,0x20,x10`}`
上面有讲这些数据需要发送26次，每次是2个bit，总共就是52个bit
上面是7个字节，总共是56个bit，还有4个bit怎么办，后面再说。
这个时候我们需要说说存储时间对的指针了。
地址0x9e38存储的时间对：

<pre><code class="hljs">`{`60，60，
60，2700，
120，60，
240，60`}`</code></pre>
这个时间对分别是time on和time off
解释这两个概念时先计算一下PWM调制的周期时间
1/38400=26μs（微秒）
该MCU的系统时钟是46Mhz，这里使用了一个16位的通用定时器GPT TimerB
我们通过代码得知该PWM调制的占空比（duty cycle）是33.3%，什么是占空比，就是在一个PWM周期里面高电平占总电平的比例，如下图：
![](https://p5.ssl.qhimg.com/t01d0da9619e567e900.png)
这个PWM的周期是26μs，高电平是8.84μs，所以占空比就是8.84/26=33.3%，也就是1/3，我们从代码里面也能看到。
![](https://p1.ssl.qhimg.com/t011896eb669001e019.png)
这个PWM输出使用的是4号GPIO口，地址0x40022090是设置各个GPIO口置bit1的地方，这里赋值0x10刚好是置4号GPIO口bit1，也就是高电平，地址0x4001002c设置定时器时间，也就是这个高电平持续多长时间，后面0x400220a0是设置各个GPIO口清除bit1，也就是置bit0，这个是0x10，表示置4号GPIO口bit0，也就是进入低电平，设置定时器长度在地址0x4001002c，时长是高电平的2倍，这就是一个周期time on的状态，通过计算我们能够得出一个周期高电平的时长。
系统时钟周期1/46000000
(46000000/38400/3.0)*( 1/46000000)=8.67μs
 好了，继续回来上面的时间对Time on和time off

<pre><code class="hljs">`{`60，60，
60，2700，
120，60，
240，60`}`</code></pre>
把每个数字乘以10，时间单位是微秒，这个10怎么来的，代码里面看到的，不知道原因（搞硬件的同学帮忙解释下）。
![](https://p3.ssl.qhimg.com/t01ddcf01da36c805ae.png)

<pre><code class="hljs">`{`600，600，
600，27000，
1200，600，
2400，600`}`</code></pre>
每对数字前的数字表示Time on，就是在这个数字的时间内，PWM信号周期性出现，后面的数字Time Off表示低电平没有PWM周期性变化。
这两个组合在一起的PWM信号就是表示数字信号里面的2个bit位，上面有提到
`{`600，600，代表bit 位『0 0』
600，27000，代表bit 位『0 1』
1200，600，代表bit 位『1 0』
2400，600`}` ，代表bit 位『1 1』
所以这个红外信号就是通过PWM的这种方法调制发射出去的，继续上面的例子，我们要发送的数据如下。
<pre>``{`0xe2, 0x20,0x80,0x78,0x88,0x20,x10`}``</pre>
发送数据的顺序是LSB，就是从左到右开始发，比如0xe2的比特数据是
“ 11100010 ”
先发11，10，00，10对应的发送时间序列对就是
2400，600
1200，600
600， 600
1200，600
我们可以通过逻辑分析仪来看这些信号发送的情况
第一组发送的比特11
Time on 2400微秒（也就是2.4毫秒），我们观察到按照周期性变化的PWM信号长度就是2.4毫秒，低电平的时长就是600微秒左右
![](https://p3.ssl.qhimg.com/t018fd8288b07ebc006.png)
第二组发送的比特10
time on时长1200微秒，time off时长600微秒
![](https://p0.ssl.qhimg.com/t014502f3dea0aebe17.png)
第三组发送的比特00
time on时长600，time off时长600
![](https://p2.ssl.qhimg.com/t01765be140560a1407.png)
第四组发送的比特10
time on时长1200微秒，time off 600微秒
![](https://p0.ssl.qhimg.com/t01af948e0297c01a7b.png)
好了，上面我们有提到要发送的数据是7个字节，56bit，但是只发送了26对也就是52bit，还有4bit怎么办，我们看最后一个字节0x10对应的比特位是00010000
因为最后4位都是bit0，所以直接低电平补位了（猜测）。
最后在14秒左右遍历了80组红外信号来尝试关闭远端的摇控电视
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
** <br>**
**外置Flash篇**

我们似乎忘记了那个4MB的winbond的外置flash了，它的功能如下：
<li>
1. 存储一些文字介绍信息
</li>
<li>
2. 存储LCD文字显示映射码
</li>
<li>
3. 存储启动的图片
</li>
<li>
4. 存储了一个变量
</li>
如果dump外置flash？

先祭出我的神器FT2232h Min Module，用热风枪把外置flash吹下来，

然后夹住，连线如下图，SPI接口一一对应好就可以了。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

通过软件flashrom来读取flash里面的内容

运行flashrom –p ft2232_spi:type=2232H,port=A –r flash_cc.bin<br style="text-align: left">

![](https://p3.ssl.qhimg.com/t0101da08c1cf89222f.png)

LCD显示是通过硬件I2C协议写入数据，ASCII码和UNICODE显示逻辑如下<br style="text-align: left">

![](https://p1.ssl.qhimg.com/t01dfdc0d967aec9f28.png)

汉字通过UTF8解码然后GBK编码后存储<br style="text-align: left">

![](https://p5.ssl.qhimg.com/t017b87f4aa09b60984.png)

所以想在显示屏上面显示中文汉字，只需要把汉字UTF8解码然后GBK编码后放到相应的位置就可以了，例如<br style="text-align: left">

&gt;&gt;&gt; '谢君'.decode('utf8').encode('gbk')

'xd0xbbxbexfd'

这四个字节写入地址0x20001060处，然后写回内置flash就出来如下效果了。<br style="text-align: left">

![](https://p0.ssl.qhimg.com/t019af47f349f683e13.png)

**<br>**

**无线通信篇（RF）**



该板子带一个无线收发功能，中心频率是433.92Mhz，速率50Kbps，2-GFSK方式调制，该无线功能一直处于监听状态，当收到服务端发过来的相应命令的数据包时，会做相应的解析，并且发相应的包响应。

**这个无线功能有如下一些功能**，我就挑选了几个：

广播请求客户端提交你们的用户id信息

广播请求客户端提交你们的通过关卡数的信息

**服务端器发送无线数据格式如下：**

0x00 0xaa无线通信前导码(preamble)

0x01 数据包payload长度

0x02 请求命令

0x03-0x04 header 0x5555或者0x2b2

0x05 序列号(seq)

0x06 地址

0x07 子命令

end 两个字节的数据包校验和

**客户端发送数据格式如下：**

0x00 0xaa前导码

0x01 数据包长

0x02 请求命令

0x03-0x04头部header 0x02 0xb2

0x05 对应服务端发过来的地址

0x06 子命令

0x7—需要提交的一些数据

end两个字节的校验和

**校验和算法：**

把字段数据包长度后面的数据，不包括校验和字段，每个字节数据相加结果再和校验和作比较。

我节选了几个数据交互对，由于我们现在不可能收到服务器发的数据，所以只能根据逆向代码来判断发送的内容是什么样的：

recv是来自服务器发的，send是我们的板子响应发出去的。

Seq是序列号，add是地址，各占一个字节

**请求提交你过了多少关：**



```
recv 0xaa 0x06  0x02 0x55 0x55 seq add 0x01 chk1 chk2  
send 0xaa 0x08 0x03 seq 0x02 0xb2 add 0x01 0xff 0x09 chk1 chk2
```

**请求提交板子的用户id，名字长度是16个字节：**



```
recv 0xaa 0x06 0x02 0x55 0x55 seq add 0x03 chk1 chk2
send 0x0a 0x16 0x03 seq 0x02 0xb2 add 0x03 username chk1 chk2
```

**其它：**



```
recv  0xaa 0x06 0x04 0x02 0xb2 seq add  0x01 chk1 chk2
send 0xaa 0x05 0x05 seq 0x02 0xb2 add chk1 chk2
```



**结论**



当然还有改进的空间，比如在解题算法代码上面，不要用明文存储答案，经过一些算法混淆处理，可以提高代码分析的门槛。
<li>
硬件上面的一些反调试对抗，可以考虑一些芯片硬件特性的支持，比如今年defcon上面使用的intel在quark d2000 x86芯片，里面有一个jtag的disable的OTP比特位，烧录设置后jtag硬件调试就不能用了。
</li>
<li>
相信他们在设计这块板子的时候也是付出了很多精力，逆向也是一个学习的过程，感谢。
</li>
<li>
<br style="text-align: left">
</li>
<br style="text-align: left">
