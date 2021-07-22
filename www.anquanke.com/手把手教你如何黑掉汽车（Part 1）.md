> 原文链接: https://www.anquanke.com//post/id/106409 


# 手把手教你如何黑掉汽车（Part 1）


                                阅读量   
                                **129049**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://console-cowboys.blogspot.com
                                <br>原文地址：[https://console-cowboys.blogspot.com/2018/04/hacking-all-cars-part-1.html](https://console-cowboys.blogspot.com/2018/04/hacking-all-cars-part-1.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t011346f83630251fc2.jpg)](https://p5.ssl.qhimg.com/t011346f83630251fc2.jpg)

## 一、前言

我一直想学习如何黑掉汽车。与往常一样，我在互联网上搜了一圈，并没有找到关于这方面的完整内容，只有零散且重复的只言片语，非常令人沮丧。我并不是一个汽车黑客专家，只是将黑客技术当成我的爱好而已。在本系列文章中，我们面对的是一个模拟实验环境，也就是说只需要5分钟，大家就能跟着教程一步一步走，在不破坏女票汽车的前提下黑掉汽车。毕竟如果女票有辆普锐斯，我们完全没必要去攻击自己的兰博基尼。

本系列教程的主要内容如下，大家可以决定是否需要继续阅读：

1、搭建测试用的虚拟环境。

2、嗅探CAN通信数据。

3、解析CAN通信数据。

4、逆向分析CAN ID。

5、拒绝服务攻击。

6、重放/注入通信流量。

7、使用python编写自己的CAN Socket工具。

8、面向汽车组件的针对性攻击。

9、攻击带有硬件设施的真实汽车。

在学习了解汽车黑客技术之前（比如了解什么是CAN），我们要做的第一件事情就是启动并运行实验环境。我们需要运行一个简单的模拟CAN Bus网络，该网络可以控制模拟汽车的各种功能。多说不如多做，只是简单地背诵汽车网络术语肯定比不上亲自动手去学习。

我也不希望你们现在就去买一大堆的硬件和千斤顶，其实只需要跟着这个教程学习下去，我们现在就能开始攻击汽车环境。这样我们也能先理解一些概念，不用担心去攻击真实的汽车。

大家可以访问[此链接](https://youtu.be/y4R3RizWN_8?list=PLCwnLq3tOElrdkQy_daR4wr9lJCt8c_C6)观看系列教学视频。



## 二、搭建模拟环境

首先我们安装一个Ubuntu VMware环境并运行该环境。我们也可以选择使用Kali虚拟机，不过我遇到了复制粘贴问题，并且Kayak安装时也出现了一些错误。所以如果你喜欢的话可以选择使用Kali。虽然如此，我知道Kali可以与OpenGarages虚拟汽车正常配合，因此如果手头刚好有这种环境，那么就可以快速上手。

<a class="reference-link" name="%E5%AE%89%E8%A3%85%E4%BE%9D%E8%B5%96%E5%BA%93"></a>**安装依赖库**

虚拟环境启动后，我们就需要安装CAN相关工具以及一些依赖库，只需要几条命令apt-get命令即可，如下所示：

```
sudo apt-get update
sudo apt-get install libsdl2-dev libsdl2-image-dev can-utils
```

然后获取ICSimulator源代码：

```
git clone https://github.com/zombieCraig/ICSim.git
```

<a class="reference-link" name="%E5%90%AF%E5%8A%A8%E6%A8%A1%E6%8B%9F%E5%99%A8"></a>**启动模拟器**

下载完毕后，我们可以将目录切换至已下载的代码目录，运行如下两条命令，设置虚拟的CAN接口以及模拟器GUI：

运行setup脚本启动vcan0接口：

```
root@kali:~/ICSim# ./setup_vcan.sh 
root@kali:~/ICSim# ./icsim vcan0
```

在终端的另一个标签页上，我们可以使用如下命令打开模拟器控制器：

```
root@kali:~/ICSim#./controls vcan0
```

注意：我们在GUI中必须选中控制器，才能向模拟器发送按键命令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01121545ea18a8685d.png)

[![](https://p5.ssl.qhimg.com/t0164bab62d71e83c9a.png)](https://p5.ssl.qhimg.com/t0164bab62d71e83c9a.png)



## 三、使用模拟器

模拟器上有速度仪表盘（speedometer）、左右车灯、车门等。当控制面板获得焦点后，我们可以使用如下命令来控制模拟器。大家可以逐个尝试一下，同时注意模拟器的变化。
- 上下键（Up、Down）控制车速表
- 左右键（Left、Right）控制车灯
- 右Shift（Right Shift） + X、A或B打开车门
- 左Shift（Left Shift） + X、A或B关闭车门
比如，大家可以尝试一下Right Shift +X，你就可以看到车门打开界面。

感谢OpenGarages，现在我们已经有辆自己的汽车，随时可以开始黑掉它。

在前面的命令中，我们使用的是VCan0接口。运行`ifconfig`命令，我们可以看到这个接口的确存在，可以与CAN网络交互。

```
ficti0n@ubuntu:~/Desktop/ICSim$ ifconfig vcan0
vcan0     Link encap:UNSPEC  HWaddr 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  
          UP RUNNING NOARP  MTU:16  Metric:1
          RX packets:558904 errors:0 dropped:0 overruns:0 frame:0
          TX packets:558904 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1 
          RX bytes:3663935 (3.6 MB)  TX bytes:3663935 (3.6 MB)
```

汽车网络运行在各种协议上，最主要的还是CAN。你可以将CAN Bus看成一个老式的网络中心，每个人都能看到其他人的流量。这个类比在某种程度上是正确的，如果某辆车没有连入你已连接的特定总线的话，你将无法看到所有汽车的流量。你可以认为CAN流量与UDP流量类似，因为它也没有保存报文发送状态，但这两者最主要的区别在于部分CAN Bus网络并没有地址字段，所有数据都基于仲裁ID（Arbitration ID）以及优先级来运行。对我们来说了解这些背景知识已经足够。

了解这些知识后，现在我们来看一下能否通过CanDump工具看到属于我们虚拟汽车的CAN流量（CanDump是前面安装过的CanUtils软件包的一部分组件）。在`vcans0`接口上运行如下命令，我们就能看到一系列流量：

```
ficti0n@ubuntu:~/Desktop/ICSim$ candump vcan0
```

[![](https://p4.ssl.qhimg.com/t0197bd5b15f1488740.png)](https://p4.ssl.qhimg.com/t0197bd5b15f1488740.png)

上图中我们可以看到一堆CAN数据帧，如果我们对车辆执行某些操作，可以发现CanDump输出数据也会相应地发生变化。然而这种变化可能转瞬即逝，我们无法看到数据变化是否一一对应某些操作（比如解锁模拟的车门）。汽车在IDLE状态下数据也会一直变化，某个小字段发生改变可能并不足以引起我们的注意，屏幕滚动太快的话我们也无法抓住这个变化。



## 四、捕获并重放CAN操作

为了解决上述问题，一种可选方案就是执行某种操作然后重放流量，如果重放的流量与我们的设备处于同一个总线网络中，那么我们应该能看到同样的操作再次出现。汽车上有各种网络，我们无法保证我们的网络完美契合，比如某个OBD2端口插件并没有连接到我们开门的那个网络，或者车门根本就没连接到网络中（取决于具体车型、车龄以及车的配置情况）。

CanUtil软件包中包含的另一个有用的工具就是CanPlayer，这个工具可以用来重放流量。如果我们尝试捕捉的汽车功能与接入汽车的适配器处于同一总线上，或者使用的是虚拟的CAN接口，我们就可以使用CanDump来将流量保存为一个文件，然后就可以使用CanPlayer在网络上重放流量。比如，我们可以运行CanDump，打开车门，然后使用CanPlayer重放这一操作。

操作如下：

1、运行CanDump

2、使用Right Shift + X打开车门

3、停止运行CanDump（ctrl+c）

4、使用Left Shift + X关闭车门

5、运行CanPlayer打开已保存的文件，这样就能重放流量并打开车门

使用如下命令记录车门打开时的流量：（`-l`用来记录日志）：

```
ficti0n@ubuntu:~/Desktop/ICSim$ candump -l vcan0
```

重放CanDump文件：（使用刚创建的CanDump文件）

```
ficti0n@ubuntu:~/Desktop/ICSim$ canplayer -I candump-2018-04-06_154441.log
```

如果一切顺利，我们应该能够看到车门已再次打开。如果攻击实际生活中的汽车时没有顺利出现这种情况，可以再次重放流量即可。CAN网络与TCP/IP不同，更像UDP，发送请求后无法确保能得到响应数据。因此如果数据丢失，我们需要再次发送。此时可能网络上有优先级更高的流量正在发送，我们重放的流量只能沦为配角。

[![](https://p3.ssl.qhimg.com/t018eb3f15ecb0a4f35.png)](https://p3.ssl.qhimg.com/t018eb3f15ecb0a4f35.png)



## 五、与Can Bus交互并逆向流量

前面做的事情挺酷，但如果想理解这个流量的具体含义，CanDump就不能发挥太大的作用，只能让我们有个大致的了解。为了完成这个任务，我们可以使用CanSniffer，这个工具的数据可以用其他颜色标记出发生变化的字节。CanSniffer的使用如下所述。

我们可以使用如下命令运行CanSniffer：

```
ficti0n@ubuntu:~/Desktop/ICSim$ cansniffer -c vcan0
```

[![](https://p1.ssl.qhimg.com/t01e0dd3b0dc8005982.png)](https://p1.ssl.qhimg.com/t01e0dd3b0dc8005982.png)

我们可以看到3个字段：Time、ID以及Data。这三个字段非常好理解，含义与名称一一对应。在本文中这里最为重要的字段就是ID以及Data字段。

ID字段是数据帧的ID，以较为松散的方式与网络上的设备相关联，对应正在发送的数据包。ID同样可以用来确定网络上数据帧的优先级。CAN-ID的数字越低，它在网络上的优先级就越高，很有可能会被优先处理。Data字段是正在发送的数据，这些数据可以修改汽车的某些参数，比如解锁车门或者更新输出。你可能会注意到某些字节被红色标记出来，这些字节代表当前idle状态下发生改变的一些值。

<a class="reference-link" name="%E5%88%A4%E6%96%AD%E6%8E%A7%E5%88%B6%E6%B2%B9%E9%97%A8ID%E5%8F%8A%E5%AD%97%E8%8A%82"></a>**判断控制油门ID及字节**

打开嗅探窗口后，现在让模拟器以及控制器回到前台，点击并选择控制器窗口。在点击向上按钮时，注意观察CanSniffer的输出，查找原先为白色但现在为红色的那些值，观察油门加大时哪些值也随着变大。想注意到这些数据我们可能得花上好几分钟。

如下两张图分别对应处于IDLE状态下的ID 244报文以及提速后的ID244报文（按下向上键即可）。你可以发现某个字节会变成红色，并正在逐渐增大（十六进制下从0到F）。这个值会不断增大，直到达到最大速度为止。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016040b2049accd1fa.png)

[![](https://p4.ssl.qhimg.com/t010d3bb253e216ec89.png)](https://p4.ssl.qhimg.com/t010d3bb253e216ec89.png)

ID 244中正在变化的字节与油门被踩下的动作相对应，所以244以某种方式与汽车加速相关。使用油门值来上手比较好，踩下油门时这个值会不断增大，这样在CanSniffer的输出结果中我们观察起来也更加方便。

<a class="reference-link" name="%E4%BD%BF%E7%94%A8%E8%BF%87%E6%BB%A4%E5%99%A8%E7%AD%9B%E9%80%89%E5%80%BC"></a>**使用过滤器筛选值**

如果我们想筛选出油门值，可以点击终端窗口，输入`-000000`然后按下回车，这样就能清掉正在滚动的所有值。然后输入`+244`再按下回车，这样就能重新添加油门ID。现在我们可以再次点击控制器，使用向上按钮提高速度，不用担心其他值干扰我们的视线。这样输出窗口中只会显示ID 244，如下所示：

[![](https://p3.ssl.qhimg.com/t01450d8ef24c5d7467.png)](https://p3.ssl.qhimg.com/t01450d8ef24c5d7467.png)

如果想取回所有的ID，可以点击终端窗口，输入`+000000`然后按下回车。现在我们就能像之前那样看到所有的输出。`000000`代表的是一切数据，但如果前面多了个`-`号，就会过滤掉所有信息，清空终端窗口。

<a class="reference-link" name="%E5%88%A4%E6%96%AD%E8%BD%A6%E7%81%AFID"></a>**判断车灯ID**

现在我们来找出车灯ID。如果我们选中控制器窗口，按下左右箭头按钮，我们就可以看到输出列表中出现了一个新的ID，如下图所示的ID 188，这个ID与车灯有关：

[![](https://p3.ssl.qhimg.com/t015709222641c0a91d.png)](https://p3.ssl.qhimg.com/t015709222641c0a91d.png)

这个ID之前并没有出现在输出数据中，因为前面没使用过，直到我们开始控制车灯为止。我们可以先输入`-000000`然后输入`+188`来单独过滤出这个值，这个数据的初始值为`00`。

当我们按下左右车灯按钮时，可以发现第一个字节从`00`变成了`01`或者`02`。如果两个按钮都没按，那么该值将变成`00`。想让控制器处在前台的同时又观察输出结果是比较困难的一件事，不过在可见窗口中，ID的数据值将保持在`00`，直到超时、未激活时从列表中消失。当然，我们可以使用上面那个过滤条件，这样就能更好地观察，不让ID消失。

<a class="reference-link" name="%E9%80%86%E5%90%91%E5%8D%8F%E8%AE%AE"></a>**逆向协议**

利用这个实验环境，大家可以理解如何逆向分析汽车的所有功能，将每个动作与正确的ID及字节数据关联起来。通过这种方式，我们可以好好规划一下想改变汽车的哪些功能。前面我已带领大家简单过一遍如何识别与某个操作关联的具体字节以及ID，现在在攻击单个组件之前，大家可以自己把剩下的功能挖掘出来。

我的建议如下：

1、拿出一张纸和笔

2、尝试打开和关闭车门，记下控制这个动作的ID（记得使用过滤器）

3、尝试打开每扇门，记下打开车门所需的字节

4、尝试关闭每扇门，观察哪些字节发生变化以及具体的值，记下这些信息

5、对于左右车灯重复相同步骤（因为这些值可能与我前面测试的不一致）

6、车速表使用的是哪个ID？哪个字节会修改速度值？



## 六、直接攻击某个功能

找到所有功能的映射信息后，现在我们可以在不与控制器GUI交互的情况下，直接攻击网络中的各种设备。这种情况下，可能我们已经通过OnStar蜂窝数据网络接入汽车，或者通过以某种方式连接CAN网络的中央控制台单元台BLE连接来接入汽车。

通过某种方式接入CAN网络后，现在我们已经准备就绪，可以开始执行操作。接入方式很多，比如我们可以将某款无线设备安装到仪表盘下的OBD2端口，这样就能远程访问这辆汽车。

结合前面我们在CAN网络中收集的数据，我们可以使用正确的CAN-ID以及字节直接调用这些动作。由于我们跟目标隔空相望，我们不能直接抓住方向盘或者踩下油门，而需要发送CAN数据包来执行这些动作。

想完成这个任务，一种方法就是使用CanSend工具。我们可以使用在前面收集到的信息，将ID 188的第一个字节变成01，表示左转向灯按钮被按下，这样就能让左转向信号灯开始闪烁。CanSend使用的格式为`ID#Data`。使用CanSend发送转向信号时，我们可以看到如下输出：

```
ficti0n@ubuntu:~/Desktop/ICSim$ cansend vcan0 188#01000000
```

[![](https://p1.ssl.qhimg.com/t015a4094fa9ad2f1a4.png)](https://p1.ssl.qhimg.com/t015a4094fa9ad2f1a4.png)

现在你应该能看到左转向信号灯开始闪烁，如果没有闪烁，请确保我们使用了正确的ID并修改了正确的字节。接下来我们来试一下油门，使用ID 244（前面分析过这个ID与油门有关）来调节速度。

```
ficti0n@ubuntu:~/Desktop/ICSim$ cansend vcan0 244#00000011F6
```

我猜测执行这条命令不会得到我们想要的结果，因为速度太快了，指针没办法跳到正确的值。因此我们可以在循环中，不断尝试这个操作，每次发送的油门值为11（大约等于30英里每小时（mph））：

```
ficti0n@ubuntu:~/Desktop/ICSim$ while true; do cansend vcan0 244#00000011F6;  done
```

[![](https://p1.ssl.qhimg.com/t012f85acc13cee935c.png)](https://p1.ssl.qhimg.com/t012f85acc13cee935c.png)

这样处理会好一些，你可能会注意到指针在来回不断跳动。之所以会来回跳动， 是因为总线上还有正常的CAN通信流量，告诉汽车真实的速度其实应该设为00。我们知道这种方法行之有效，的确可以改变速度，并且可以在不操控闪光灯控制器的情况下让车灯闪烁，这是非常酷的一件事。



## 七、监控CAN Bus并实时反馈

完成这个任务的另一种方法是监控CAN网络，当发现某个ID时就自动发送带有不同值的对应的ID。现在我们可以试一下，通过监控来修改速度的输出值。如下所示，我们可以运行CanDump，解析输出日志中的ID 244（与油门对应）。当汽车中的某个设备报告ID 244及对应的值时，我们需要立即发送自己的值，告诉汽车此时的速度值为30mph（对应的数值为11）。具体命令如下：

```
ficti0n@ubuntu:~/Desktop/ICSim$ candump vcan0 | grep " 244 " | while read line; do cansend vcan0 244#00000011F6; done
```

这条命令运行几秒钟后，一旦工具从网络中抓到合法的CAN-ID 244流量，就会发送自己修改后的值，然后我们就可以看到速度已经被调整到30mph。

非常好，现在让这条命令继续运行，再次点击控制器窗口，按住向上箭头。大约几秒钟后，当仪表盘上速度超过30mph时，你可以看到指针在来回跳动，想调节回30mph，因为我们的命令仍在后跳运行，不断干扰正常的速度值。

这种方法可以监听网络，然后根据监控结果以较为粗鲁的方式来做出反应。如果你担心某些人盗窃你的车，此时可以监控开门事件，一旦有人尝试开门就可以立即将他们锁在车内。



## 八、总结

我并不是专业的汽车黑客，但我希望你喜欢这篇文章。在接下来的文章中，我想给大家分享如何编写python代码，以类似方式操控CAN网络。使用自己编写的代码后，我们可以不限于这些工具提供的功能，自由度更大一些，这种方法比使用CanUtils预定义的工具来说功能更加强大。在后续文章中，如果你想在实际的汽车上尝试攻击，我还会介绍硬件方面的内容，不过实际操作更加复杂，也可能出现错误。


