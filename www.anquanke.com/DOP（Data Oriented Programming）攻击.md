> 原文链接: https://www.anquanke.com//post/id/196547 


# DOP（Data Oriented Programming）攻击


                                阅读量   
                                **1151798**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t0118a20fdc6a6d0682.jpg)](https://p3.ssl.qhimg.com/t0118a20fdc6a6d0682.jpg)



围绕内存漏洞的攻防博弈已经持续了近三十年，控制流劫持攻击也越来越多的成为攻击者的常用手段。随着防护技术的发展，针对控制流的攻击变得愈发困难。而不通过劫持控制流，而是针对数据流来进行攻击的方式，如Non-control data（非控制数据）攻击虽然显示出了其潜在的危害性，但目前对针对数据流的攻击还知之甚少，长久以来该攻击手段可实现的攻击目标一直被认为是有限的。实际上，非控制数据攻击可以是图灵完备的，这就是我将为大家介绍的攻击DOP攻击。



## 背景知识：Non-control data（非控制数据）攻击

控制流保护机制旨在保护目标程序控制流不被篡改，但是控制流转移指令（如 ret , jmp）往往不直接使用内存变量，这就意味着控制流保护机制（如CFI）往往无法将内存变量纳入保护。非控制数据攻击就利用了这一点，攻击者直接控制数据流来实施相应攻击。比如鼎鼎大名的的心脏出血（heartbleed）漏洞就是典型的非控制数据攻击。又比如下图代码：

[![](https://p3.ssl.qhimg.com/t012a878e9367744931.png)](https://p3.ssl.qhimg.com/t012a878e9367744931.png)

如果攻击者能够控制pw_uid变量，就能够实现提权操作。



## DOP相关概念

DOP全称为 Data Oriented Programming，是新加坡国立大学的胡宏等人于2016年提出来的一种针对数据流的非控制数据攻击方式，核心思想是用各种各样的内存行为来模拟相应操作。

正如前述所提到的那样，非控制数据攻击往往只能用来实现信息泄露（心脏出血）或者是提权，其本身不能实现复杂的操作。但DOP打破了这一成见，证明了非控制数据攻击本身就能实现图灵完备的攻击。

类似于ROP，DOP攻击的实现也依赖于gadgets。但二者有以下两点不同：
1. DOP的gadgets只能使用内存来传递操作的结果，而ROP的gadgets可以使用寄存器。
1. DOP的gadgets必须符合控制流图（CFG），不能发生非法的控制流转移，而且无需一个接一个的执行。而ROP的gadgets必须成链，顺序执行。
为了更好的说明DOP的gadgets特性，胡宏等人定义了如下语言MINDOP:

[![](https://p2.ssl.qhimg.com/t01653f6dfb8059f12f.png)](https://p2.ssl.qhimg.com/t01653f6dfb8059f12f.png)

其展示了DOP的gadgets如何在受限制的语义下实现算术、逻辑、赋值、加载、存储、跳转、条件跳转等操作。正如前述所提到的，DOP的gadgets不能使用寄存器，所以DOP转而用内存来模拟寄存器（也就是上图中的*p等就对应了一个虚拟的寄存器）及各种操作。接下来将结合ProFTPD（一个开源的FTP服务器软件，也是之后实际进行攻击时的目标程序）源码来进行说明。

1.算术运算

1）加减法

用gadgets来模拟加减法是比较容易的，因为目标程序中存在大量的目标代码片段。<a name="_Hlk28861604"></a>比如如下代码：

[![](https://p4.ssl.qhimg.com/t016a005cda2216963d.png)](https://p4.ssl.qhimg.com/t016a005cda2216963d.png)

通过该代码就能完成一次加法，减法同理。

2）乘法

乘法的模拟较为复杂，但是如果存在条件跳转，则乘法的模拟也可以完成。比如要完成a×b，可以将b进行比特位的分解，根据当前比特位来进行相应的跳转，同时在每一步都进行a的自加（可用左移位来实现）即可。简单来说就是用加法来实现乘法。

2.赋值

DOP中的赋值操作相当于是从内存某地值读取数据存储到另一地址中，比如如下代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ce0150722aaa1729.png)

就完成了一次赋值操作。

3.加载和存储

由于DOP不能使用寄存器，所以加载和存储操作都是通过指针解引用来模拟的。如以下代码：

[![](https://p0.ssl.qhimg.com/t01f4505b445f3a7b3c.png)](https://p0.ssl.qhimg.com/t01f4505b445f3a7b3c.png)

其实现了加载操作。

又比如以下代码，其实现了存储操作：

[![](https://p4.ssl.qhimg.com/t01921a6de8498c8639.png)](https://p4.ssl.qhimg.com/t01921a6de8498c8639.png)

4.跳转操作

跳转操作的实现需要依赖于一个内存错误（如栈溢出）的发生。关键就是要通过某处内存来模拟处一个虚拟的指令寄存器（pc），使得通过该内存来进行“跳转（并非真实跳转，只是转而执行某处代码）”。比如以下代码：

[![](https://p5.ssl.qhimg.com/t01fd76e8be20a5ebb8.png)](https://p5.ssl.qhimg.com/t01fd76e8be20a5ebb8.png)

pubf -&gt; current指向了恶意输入的缓冲区。在每一次循环迭代中，代码从该缓冲区读取一行，然后在循环体中处理它，因此这个指针可以用来模拟虚拟PC指针。如果pbuf-&gt;current被控制，精心构造相应的值，那么buf处就会发生相应的改变，进而影响其相邻位置，最终使得函数参数cmd被控制，执行相应操作。

同ROP类似，DOP也需要有一个gadgets调度器（dispatcher）。DOP中的调度器指的是能够让攻击者重复的调用gadgets，并且<a name="_Hlk28881873"></a>让攻击者选择具体的调用哪一个gadget的指令序列。比较常见的就是带有一个选择器（selecor, 让攻击者选择具体的调用哪一个gadget,通常是一处内存错误发生点）。每次迭代将会使用前一次的迭代中使用的gadget输出，并且将本轮迭代使用的gadget的输出输入到下次迭代，同时选择器改变下次迭代的加载地址为本次迭代的存储地址。选择器由攻击者通过内存错误控制。如上图中第2-7行，它将循环的处理cmd请求，通过构造相应的cmd，就能引入相应的gadgets。

接下来以如下代码片段对各个模拟出的操作效果进行说明：

[![](https://p4.ssl.qhimg.com/t0164bb5b89d3da52cd.png)](https://p4.ssl.qhimg.com/t0164bb5b89d3da52cd.png)

可以看到，该代码片段没有调用任何敏感的代码指针。其CFG图如下：

[![](https://p4.ssl.qhimg.com/t0178cd6411c85824ef.png)](https://p4.ssl.qhimg.com/t0178cd6411c85824ef.png)

6、7行即为调度器,其中第7行为选择器。即使通过第7行的栈溢出进行覆盖，看起来似乎也并没有什么威胁。但是再考虑如下代码：

[![](https://p5.ssl.qhimg.com/t016aae9355763cdbb9.png)](https://p5.ssl.qhimg.com/t016aae9355763cdbb9.png)

buf处的内存排布如图：

[![](https://p3.ssl.qhimg.com/t01e4952f1af44c5801.png)](https://p3.ssl.qhimg.com/t01e4952f1af44c5801.png)

通过栈溢出可以将其变为：

[![](https://p3.ssl.qhimg.com/t01539cac1d8edb1547.png)](https://p3.ssl.qhimg.com/t01539cac1d8edb1547.png)

假如p是list地址，q是addend地址，n是srv地址的话，就会执行如下操作：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ca5743c90ad741e8.png)

而进行如下覆盖；

[![](https://p3.ssl.qhimg.com/t019e0ed171e617c290.png)](https://p3.ssl.qhimg.com/t019e0ed171e617c290.png)

令m是STREAM字符串地址的话，就等效于：

[![](https://p4.ssl.qhimg.com/t01a91470bcd5ab5b74.png)](https://p4.ssl.qhimg.com/t01a91470bcd5ab5b74.png)

如果再循环体中各自进行一次，最终效果等效于：

```
while(condition)    
`{`    
 if(list==NULL) break:    
 srv=list;    
list-&gt;prop+=addend;    
list=list-&gt;next;    
`}`
```

实际上就实现了通过控制数据流来“调用”updateList函数，但实际的控制流并未发生转移，因为并没有一个真正的函数被调用了，控制流仍处在循环体内。

至此，DOP的模型已经明确了，如下图所示：

[![](https://p1.ssl.qhimg.com/t011e33c62048045d30.png)](https://p1.ssl.qhimg.com/t011e33c62048045d30.png)

内存错误将会激活调度器，在循环loop中通过控制选择器来选择执行相应的gadgets。



## DOP的准备工作

经过前述的说明，DOP的基本概念已经清晰，接下来要解决的就是以下几个问题：
1. 如何定位gadgets
1. 如何寻找调度器
1. gadgets的拼接
对于前两点来说，一个静态分析工具的实现是可能的。因为DOP的gadgets的特征是非常明确的，其必须符合MINDOP语义，而且必须是如下模式：

加载-其他操作-存储

而调度器也有明显特征。

为了避免对源码进行分析，可以把目标程序编译成LLVM IR形式，然后通过胡宏等人提供的工具DOP-StaticAssist（https://github.com/melynx/DOP-StaticAssist）进行gadget（包括调度器）的定位。

对于最后一点来说，暂时只能依靠直觉（胡宏等人的原话，瞬间玄学）来进行不断的尝试。



## DOP攻击的构造

DOP的准备工作已经完成，接下来就是具体攻击的构造。由以下几个步骤组成：
1. 从目标程序中定位发生内存错误的函数，然后寻找包含该函数的调度器，收集用于攻击的gadgets。
1. 以预期的恶意MINDOP操作作为模板，每个MINDOP操作可以通过相应的功能类别的任何gadgets来实现。可以根据优先级来进行选择。
1. 一旦我们得到了实现所需的功能的gadgets，接下来要做的就是验证每个拼接。构造输入到程序，触发内存错误，激活gadgets。如果攻击不成功，我们回滚到步骤2，选择不同的gadgets，并尝试再次拼接


## 攻击ProFTPD

为了直观的感受DOP攻击能够实现的目标，接下来将会对ProFTPD进行两种不同的攻击。该程序存在栈溢出漏洞（cve 2006-5815）。攻击时使用metasploit来进行，脚本可以在作者提供的虚拟机中查看（https://drive.google.com/file/d/0B_6p5h2gdgmoTV9ON0xYZWpMRTg/view）。要自己解决的问题只有一个：选择一个当前进程空间中的以0xb开头的可写地址，且内容不能为\0。所有攻击均在ASLR和DEP开启的情况下进行。

### 泄露密钥

该程序使用一个ssh密钥，DOP攻击可以泄露这个密钥。

开启ProFTPD服务：

[![](https://p4.ssl.qhimg.com/t01a127975a0054a9d4.png)](https://p4.ssl.qhimg.com/t01a127975a0054a9d4.png)

可以看到，地址随机化已经开启。

进入msfconsole,输入如下命令：

```
use exploit/windows/ftp/proftp_sreplace_dop

      set ftpuser ftptest

      set ftppass ftptest

      set rhost 127.0.0.1
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0120c51a5423103f7d.png)

然后进行如下操作：

此处0xb77430001即为上述所需地址。

密钥成功泄露：

[![](https://p2.ssl.qhimg.com/t01b3123389799b9fe6.png)](https://p2.ssl.qhimg.com/t01b3123389799b9fe6.png)

实际密钥可以通过以下命令查看（字节逆序）：

[![](https://p1.ssl.qhimg.com/t014ad4e0f5004c8418.png)](https://p1.ssl.qhimg.com/t014ad4e0f5004c8418.png)

可以看到，泄露出的确实是真实密钥。

### 修改代码段内容为int 3

启动目标程序

[![](https://p0.ssl.qhimg.com/t016144119ba8b8d741.png)](https://p0.ssl.qhimg.com/t016144119ba8b8d741.png)

地址随机化已经开启，LD_PRELOAD用于给gdb传递信息。

进入msfconsole,输入如下命令：

```
use exploit/windows/ftp/proftp_sreplace_dlopen

      set ftpuser ftptest

      set ftppass ftptest

      set rhost 127.0.0.1
```

[![](https://p2.ssl.qhimg.com/t0132f6cbf0f343c322.png)](https://p2.ssl.qhimg.com/t0132f6cbf0f343c322.png)

将gdb附着（attach）到正在运行的进程：

设置follow-fork-mode为child(调试子进程，父进程不受影响)：

[![](https://p0.ssl.qhimg.com/t01b36c77b20fddde52.png)](https://p0.ssl.qhimg.com/t01b36c77b20fddde52.png)

然后进行以下操作：

[![](https://p2.ssl.qhimg.com/t0106d6926ca44b077a.png)](https://p2.ssl.qhimg.com/t0106d6926ca44b077a.png)

这里选用了另外一个地址0xb76a6001。

攻击完成：

[![](https://p0.ssl.qhimg.com/t019de2b24383213c9e.png)](https://p0.ssl.qhimg.com/t019de2b24383213c9e.png)

查看当前代码段位置，已经被修改为int 3：

[![](https://p4.ssl.qhimg.com/t017e3e81ca6bb1eaf7.png)](https://p4.ssl.qhimg.com/t017e3e81ca6bb1eaf7.png)

而目标程序相应位置处应为ret:

[![](https://p5.ssl.qhimg.com/t0112e27c0d5204ddce.png)](https://p5.ssl.qhimg.com/t0112e27c0d5204ddce.png)

对目标程序代码段（不可写）的修改成功。
