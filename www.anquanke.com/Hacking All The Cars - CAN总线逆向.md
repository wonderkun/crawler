> 原文链接: https://www.anquanke.com//post/id/209141 


# Hacking All The Cars - CAN总线逆向


                                阅读量   
                                **224904**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01bc3505681f449721.png)](https://p3.ssl.qhimg.com/t01bc3505681f449721.png)



大家好，我是来自银基Tiger Team的BaCde。本文主要是通过ICSim(Instrument Cluster Simulator)模拟CAN协议通信，通过实践对CAN总线协议进行逆向分析。在实践过程中踩过一些坑，这里跟大家分享交流。



## 简介

CAN(Controller Area Network)总线是制造业和汽车产业中使用的一种简单协议，为ISO国际标准化的串行通信协议。在现代汽车中的小型嵌入式系统和ECU能够使用CAN协议进行通信，其通信是采用的广播机制，与TCP协议中的UDP差不多。各个系统或ECU（电子控制单元）都可以收发控制消息。1996年起该协议成了美国轿车和轻型卡车的标准协议之一，但是直到2008年才成为强制标准（2001年成为欧洲汽车标准）。当然1996年之前的也有可能使用CAN总线。现在，汽车的电子组件均通过CAN总线连接，针对汽车的攻击最终也都会通过CAN总线来实现。对于研究汽车安全，CAN总线协议是必须要掌握的。



## 环境与准备
- CAN总线模拟—ICSim
- 分析工具— can-utils、Kayak、Wireshark
- 系统—Kali Linux 2020 语言为中文（非root权限）
### <a class="reference-link" name="ICSim%E7%BC%96%E8%AF%91"></a>ICSim编译

ICSim(Instrument Cluster Simulator)，是由Open Garages推出的工具。它可以产生多个CAN信号，同时会产生许多背景噪声，让我们可以在没有汽车或不改造汽车的情况下即可练习CAN总线的逆向技术。

GITHUB地址：[https://github.com/zombieCraig/ICSim](https://github.com/zombieCraig/ICSim)

ICSim目前仅可运行在linux系统下，在Kali linux上按照github提供的安装方法，会出现“libsdl2-dev 未满足的依赖关系”的错误，错误如下图。

[![](https://p1.ssl.qhimg.com/t0108e075fc23454fc4.png)](https://p1.ssl.qhimg.com/t0108e075fc23454fc4.png)

可以通过aptitude安装来解决，具体安装步骤如下：

```
sudo apt-get update 
sudo apt-get install aptitude
sudo aptitude install libibus-1.0-dev
sudo apt-get install gcc
git clone https://github.com/zombieCraig/ICSim
cd ICSim
make
```

至此ICSim安装完成，目录内容如下：

[![](https://p3.ssl.qhimg.com/t012c81b11ee13908a0.png)](https://p3.ssl.qhimg.com/t012c81b11ee13908a0.png)

切换到ICSim目录，执行如下命令。

```
./setup_vcan.sh         #初始化，每次重启后都要重新运行
./icsim vcan0           #模拟器
./controls vcan0        #控制面
```

运行后可以看到如下界面，像游戏手柄的界面是控制面板（这里可以插入USB游戏手柄进行控制，笔者这里没有，有USB手柄的大家可自行测试）。另外有仪表盘的窗口是模拟器，速度表停在略高于0mph的位置，如果指针有摆动就说明ICSim工作正常。

[![](https://p4.ssl.qhimg.com/t01ffdc6dd4e1d1e56f.png)](https://p4.ssl.qhimg.com/t01ffdc6dd4e1d1e56f.png)

其控制器的按键说明如下：

|功能|按键
|------
|加速|上方向键
|左转向|左方向键
|右转向|右方向键
|开/关左车门（前）锁|右/左shift+A
|开/关右车门（前）锁|右/左shift+B
|开/关左车门（后）锁|右/左shift+X
|开/关右车门（后）锁|右/左shift+Y
|开启所有车门锁|右shift+左shift
|关闭所有车门锁|左shift+右shift

上面的`setup_vcan.sh` 主要功能是加载CAN和vCAN（virtual controller area network）网络模块。并创建名为vcan0的网络设备并打开连接。<br>`setup_vcan.sh`文件内容如下：

```
sudo modprobe can
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

运行后，我们可以使用ifconfig来查看网络接口，发现会多出来一个vcan0的网络接口。

[![](https://p5.ssl.qhimg.com/t01cd5ca29d841c211e.png)](https://p5.ssl.qhimg.com/t01cd5ca29d841c211e.png)

### <a class="reference-link" name="can-utils%E5%AE%89%E8%A3%85"></a>can-utils安装

can-utils是CAN实用的工具套件，包含了许多实用程序。

GITHUB地址：[https://github.com/linux-can/can-utils](https://github.com/linux-can/can-utils)

经常用到的几个程序如下，更多命令可以看github地址：
- candump : 显示、过滤和记录CAN数据到文件。candump并不会解码数据。
- canplayer : 对记录的CAN数据进行重放。
- cansend : 发送CAN数据。
- cansniffer : 显示CAN数据并高亮显示变化的字节。
当前环境使用的Kali Linux 2020直接使用如下命令安装即可。如果你的系统不支持，则可以直接下载github上的源码，使用make命令进行编译安装。

```
sudo apt-get install can-utils
```

### <a class="reference-link" name="Kayak"></a>Kayak

Kayak可以直接通过github下载release版本的。但是，该工具的使用需要配合socketcand。
<li>socketcand安装
<pre><code class="hljs sql">sudo apt install automake
git clone https://github.com/linux-can/socketcand.git
cd socketcand
./autogen.sh
./configure
make
sudo make install
</code></pre>
</li>
<li>Kayak下载<br>
GITHUB下载：[https://github.com/dschanoeh/Kayak/releases](https://github.com/dschanoeh/Kayak/releases)
</li>
解压缩后，bin文件夹下有windows版本和linux的运行程序。Kali下直接在terminal下运行./kayak 即可。当然这里也可以下载源代码，并使用maven编译。



## 前置知识

上面已经准备好了环境，在真正开始分析之前，先简单说一些前置知识。

### <a class="reference-link" name="CAN%E6%80%BB%E7%BA%BF"></a>CAN总线
1. CAN运行在两条线路上：CAN高电平（CANHI）和CAN低电平（CANLO）。
1. CAN bus 有四种帧类型
|帧类型|用途
|------
|数据帧（Data Frame）|包含要传输的节点数据的帧
|远程帧（Remote Frame）|请求传输特定标识符的帧
|错误帧（Remote Frame）|任何检测到错误的节点发送的帧
|重载帧（Overload Frame）|在数据或远程帧之间插入延迟的帧
1. CAN有两种类型的消息(帧)格式：标准（基础）帧格式和扩展帧格式。标准（基础）帧有11位标识符，扩展帧格式有29位标识符。CAN标准帧格式和CAN扩展帧格式之间的区别是通过使用IDE位进行的，IDE位在11位帧的情况下以显性方式传输，而在29位帧的情况下以隐性方式进行传输。支持扩展帧格式消息的CAN控制器也能够以CAN基本帧格式发送和接收消息。<li>标准帧格式<br>
说一下主要的4个元素，其他的大家感兴趣可自行去了解：
<ul>
- 仲裁ID（Arbitration ID）：仲裁ID是一种广播消息，用来识别正视图通信的设备的ID，其实也代表发送消息的地址。任何的设备都可以发送多个仲裁ID。在总线中同时发送的消息，低仲裁ID的消息拥有优先权。
- 标识符扩展（IDE）：标准帧格式该位始终是0。
- 数据长度码（DLC）：表示数据的大小，番位是0字节到8字节。
- 数据（Data）：总线传输数据本身。一个标准的数据帧可携带最大尺寸为8字节。有些系统中会强制要求8字节，不满8字节则填充为8字节。
[![](https://p1.ssl.qhimg.com/t012f6fcd1baa40a15f.png)](https://p1.ssl.qhimg.com/t012f6fcd1baa40a15f.png)
<li>扩展帧格式<br>
扩展帧格式与标准帧格式类似，扩展帧格式可以连接在一起，形成更长的ID。拓展帧格式可包含标准帧格式。拓展帧格式的标识符扩展IDE被设置为1。扩展帧有一个18位的标识符，是标准的11位标识符的第二部分。</li>
### <a class="reference-link" name="CAN%E6%80%BB%E7%BA%BF%E5%A8%81%E8%83%81"></a>CAN总线威胁

根据CAN总线的特性，我们则可以了解CAN面临的威胁：
1. CAN总线通信是广播的方式，所以数据是可以被监听和获取的。
1. CAN总线协议中ID代表报文优先级，协议中没有原始地址信息。也就是说任何人都可以伪造和发送虚假或恶意的报文。
另外拒绝服务攻击在CAN总线协议中也是存在的。但是我们主要是分析和逆向CAN总线。这里不做相关说明。

### <a class="reference-link" name="%E7%9B%91%E5%90%ACCAN%E6%B5%81%E9%87%8F"></a>监听CAN流量

监听CAN流量有多种方法。首先请保证启动ICSim。
<li>can-utils 工具包监听
<pre><code class="hljs nginx">candump -l vcan0
</code></pre>
<p>输入该命令后会监听流量并以candump-YYYY-MM-DD_time.log格式的文件名保存到当前目录下。如candump-2020-06-22_103240.log。按ctrl+c停止监听。<br>
打开文件，数据格式如下：</p>
<pre><code class="hljs css">(1592836523.941032) vcan0 164#0000C01AA8000022
(1592836523.941168) vcan0 17C#0000000010000003
(1592836523.941285) vcan0 18E#00004D
(1592836523.941387) vcan0 1CF#80050000000F
(1592836523.941745) vcan0 1DC#0200000C
(1592836523.943317) vcan0 183#0000000E0000100D
(1592836523.943545) vcan0 143#6B6B00C2
</code></pre>
括号内的是时间戳，vcan0为我们的虚拟can接口。后面的是ID和数据，ID和数据以#号分割。
</li>
[![](https://p4.ssl.qhimg.com/t01b672639867e53755.png)](https://p4.ssl.qhimg.com/t01b672639867e53755.png)

也可以去掉-l选项，直接在屏幕上可以打印数据包。

candump是监听并记录原始数据，会有很多对我们无用的数据。can-utils工具包中还有一款可以根据仲裁ID进行分组显示，并对变化的数据以红色显示，它就是cansniffer。<br>
命令：

```
cansniffer -c vcan0
```

[![](https://p0.ssl.qhimg.com/t01ae91fe1caf0be3b1.png)](https://p0.ssl.qhimg.com/t01ae91fe1caf0be3b1.png)

cansniffer可以通过发送按键来过滤显示数据包。注意，当输入按键时，并不会在终端中显示，输入完成后按回车键（一定要记得按）。如下例子则是先关闭所有数据包显示（-000000），然后仅显示ID133和ID244的数据包。

```
-000000
+133
+244
```
<li>Wireshark 监听<br>
wireshark功能简直太强大了，它也可以捕获CAN数据报文。打开wireshark，选择vcan0接口即可监听流量。info列中可以看到ID和数据。wireshark也是原始流量，并为进行去重。<br>[![](https://p5.ssl.qhimg.com/t01f244f261e0e195c2.png)](https://p5.ssl.qhimg.com/t01f244f261e0e195c2.png)
</li>
<li>Kayak监听
<ul>
1. 运行socketcand -i vcan0，socketcand可以挂接多个CAN设备，接口名使用逗号分割即可。
1. 然后切换到Kayak的bin目录下，运行./kayak。
1. 单击File菜单-&gt;new project(或者ctrl+n快捷键)，输入project名字。
1. 展开右下角connections窗口中的auto discovery，将下面的内容拖到新建的project中并输入一个名字。
1. 右键上一步中创建的bus，选择OPEN Raw View。
<li>单击工具栏中的play 按钮。开始捕获CAN总线流量。点击colorize可以对有变化的数据以不同颜色。同时还可以暂停和停止监听流量操作。<br>[![](https://p0.ssl.qhimg.com/t019d504620fd505278.png)](https://p0.ssl.qhimg.com/t019d504620fd505278.png)
</li>
</ul>
</li>
candump和wireshark监听的流量都是原始流量，我们看到的数据非常多。而Kayak可以按照仲裁ID来进行分组显示，并对不同的

### <a class="reference-link" name="%E9%87%8D%E6%94%BECAN%E6%B5%81%E9%87%8F"></a>重放CAN流量

canplayer程序可以重放candump记录的流量内容。<br>
输入如下命令即可重放。

```
canplayer -i candump的log文件
```

重放时，可以观察下ICSim仪表盘是否有变化。

对于CAN分析的工具不仅只有这几个，也可以多尝试其他网络上的工具。



## CAN消息逆向

在实战中，各个制造商和车型都有自己唯一的CAN数据包格式，而分析通信数据主要是目的是找到某个特定的信号，例如开车门锁，启动车等。通过上面监听数据，可以看到会有很多数据，这主要由于汽车本身会有很多设备会按照制定的间隔发送数据，这些数据可以称为噪音，这对分析某个具体动作带来麻烦。所以需要对CAN消息进行逆向分析。

### <a class="reference-link" name="%E4%BA%8C%E5%88%86%E6%B3%95"></a>二分法
<li>首先通过candump监听数据。
<pre><code class="hljs nginx">candump -l vcan0
</code></pre>
</li>
1. 回到控制器界面，进行开门锁操作，然后在关闭车门锁。
1. 停止监听数据。数据保存到执行`mv candump-2020-06-22_140718.log source` (文件名根据实际情况修改)
1. 关车门锁操作，执行`canplayer -I source` 重放数据。确认车门锁是否开启。如果没有，请重复上面的步骤。
1. 输入 `wc -l source` 命令查看文件行数。笔者这里结果为11407行。
1. 输入 `split -l 6000 source c1` 将source文件分成两个文件。
1. 使用canplayer重放两个分割后的文件，查看重放的哪个文件打开来车门锁。每次重放前都要执行 `canplayer -I source`。主要是保证每次重放分割的文件前车门锁是关闭的。
1. 根据第6和7的步骤对包含重放命令的文件进行。这里要注意每次split命令分割的行数减少1倍。例如第二次执行的名为 `split -l 3000 c1aa c2` 。重放命令为 `canplayer -I c2aa`和`canplayer -I c2ab`。这样一直重复知道发现最终的数据包。
经过上面的重复，在13ab的文件中定位到来了ID值和发送的数据。使用 `cansend vcan0 19B#00000E000000` 进行验证。打开车门锁成功。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01070f3b96da292d31.png)

### <a class="reference-link" name="%E7%BB%9F%E8%AE%A1%E6%B3%95"></a>统计法

对于一些只有在进行操作时才会产生的动作，可以通过选择特定的次数，对其发送的次数进行筛选。
1. 使用 `candump -l vcan0` 捕获数据包。
1. 在控制器界面中操作5次车门锁操作。
1. 停止candump。获得保存文件，这里为`candump-2020-06-22_151059.log`。
1. 通过编写好的脚本，运行 `python3 can.py candump-2020-06-22_151059.log`获得结果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019248468c787ec30c.png)

脚本很简单，主要就是遍历所有数据，对ID进行计数统计并显示最终结果，输入ID值可显示对应的数据内容。使用python 20行代码就可以搞定。大家可以自己编写下。

### <a class="reference-link" name="%E8%A7%82%E5%AF%9F%E6%B3%95"></a>观察法

有了上面的一些经验积累后，借助可视化界面来对数据进行观察也可以逆向出其总线ID。<br>
按照上面启动Kayak的方法，启动监听数据。工具已经对ID进行来分组。将模拟器，控制器和Kayak放在同一个屏幕上。

[![](https://p4.ssl.qhimg.com/t01908719cea2669673.png)](https://p4.ssl.qhimg.com/t01908719cea2669673.png)

在控制器界面按下左键，模拟器界面左转向灯闪了一下，观察Kayak界面数据变化，在左转向灯闪时（也就是按下左键时），看哪一个值变了又变会原值，并保持原值。最终定位ID值为188。

现在在进行另外一个例子，在汽车加速过程中，转速表是一直在上升。这就可以通过观察哪一个值是在持续上升的。这里通过控制器界面，按住上方向键，观察哪一个值是在持续增加的。最终定位ID值为244。

可以通过cansend来进行验证，是否成功。

当然除了使用Kayak外，也可以尝试cansniffer。



## ICSim难度设置

以上介绍的几种方法各有利弊，不能满足所有情况，实际的情况会非常复杂，需根据实际情况进行选择。<br>
对于CAN总线的分析，ICSim支持从0到3的4个级别，默认难度为1级，0为最简单，3是最难。还可以设置随机化的种子值。<br>
输入 `./icsim -r vcan0` 命令可以显示出随机的种子值。当然也可以使用 `./icsim -s 1419525411 vcan0` 来设置种子值，这样仿真器就可以选择不同的ID和目标字节位置了。<br>
输入 `./icsim -l 3 vcan0` 命令设置挑战难度。<br>
大家可以自行尝试增加难度来进行挑战。



## 总结

本文主要以ICSim模拟CAN总线数据，通过多种方式来对CAN总线进行逆向分析，重在方法和工具使用。部分内容并未过多提及，如果一旦拓展开来，需要写的内容实在太多。感兴趣的大家可自行进行深入学习和了解。如果在进行实车的分析和测试也要注意自身安全，提前做好计划和保障。



## 参考或引用来源
1. [https://github.com/zombieCraig/ICSim](https://github.com/zombieCraig/ICSim)
1. [https://github.com/linux-can/can-utils](https://github.com/linux-can/can-utils)
1. [https://github.com/dschanoeh/Kayak/releases](https://github.com/dschanoeh/Kayak/releases)
1. [https://tryhackme.com/room/carhacking101](https://tryhackme.com/room/carhacking101)
1. [https://www.securitynewspaper.com/2018/05/03/hack-car-tool/](https://www.securitynewspaper.com/2018/05/03/hack-car-tool/)
1. [https://github.com/jaredthecoder/awesome-vehicle-security#python](https://github.com/jaredthecoder/awesome-vehicle-security#python)
1. [https://dschanoeh.github.io/Kayak/tutorial.html](https://dschanoeh.github.io/Kayak/tutorial.html)
1. [https://www.hackers-arise.com/post/2017/08/08/automobile-hacking-part-2-the-can-utils-or-socketcan](https://www.hackers-arise.com/post/2017/08/08/automobile-hacking-part-2-the-can-utils-or-socketcan)
1. [https://www.hackers-arise.com/post/2017/08/04/automobile-hacking-part-1-the-can-protocol](https://www.hackers-arise.com/post/2017/08/04/automobile-hacking-part-1-the-can-protocol)
1. [https://en.wikipedia.org/wiki/CAN_bus](https://en.wikipedia.org/wiki/CAN_bus)
1. [https://mp.weixin.qq.com/s/jvzLn2ZTmId4cfqBNJxYyg](https://mp.weixin.qq.com/s/jvzLn2ZTmId4cfqBNJxYyg)


## 参考书籍或文档
1. 《智能网联汽车安全》
1. 《汽车黑客大曝光》
1. 《Car Hacking: Accessing and Exploiting the CAN Bus Protocol》