
# 基于纯软件环境的AVR逆向分析


                                阅读量   
                                **448852**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



## [![](./img/202256/t010ed2cc167cf1e0d5.jpg)](./img/202256/t010ed2cc167cf1e0d5.jpg)

## 

## 一. 前言

大家好，我是来自银基安全实验室的Cure。 今天与大家分享在纯软件环境下进行AVR固件逆向破解的一些学习与思考。

AVR单片机是Atmel公司于1997年推出的RISC单片机。其中，RISC意为精简指令系统计算机。与CISC（复杂指令系统计算机）不同，RISC优选使用频率最高的简单指令，避免复杂指令，并固定指令宽度，减少指令格式和寻址方式种类，从而缩短指令周期，提升运行速度。一般地，AVR系列单片机具备1MIPS（百万条指令每秒）的高速处理能力。

AVR单片机具有多个系列，包括低档的ATtiny、中档的AT90和高档的ATmega，每个系列又包括多种产品。它们基本结构和原理相互类似，编程方法相同，而在功能和存储容量上则存在很大的差异。AVR单片机系列齐全，能够适用多种不同的场合。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ec15a13b8410ddb0.png)

作为IoT设备与传统嵌入式设备十分常见的处理器芯片，AVR程序的安全问题近年来越发得引起了人们的重视，相应的CTF挑战题目也层出不穷。然而，AVR程序的学习，尤其是其逆向技术的学习，往往需要价格昂贵的硬件开发板和一系列复杂的硬件调试工具链，为初学者带来了诸多的限制。本文通过AVR相关的CTF试题，从纯模拟工具与静态分析工具出发，详细地复现已知的基于模拟工具的解题思路，以为对该领域有兴趣的小伙伴们提供些许参考。



## 二. 工具准备

本文所复现的方法中，主要用到的静态分析工具为radare2，这是一个能够在command环境下运行的二进制分析工具，支持多种平台代码的反汇编，也集成了人性化的命令行界面。

Debian系列Linux环境中，radare2的安装十分便捷：
1. $ sudo apt-get install radare2


本文主要用到的动态分析工具为simavr和avr-gdb。

simavr，如其名称是一个软件的AVR模拟器。该模拟器基于avr-gcc，故尤其适用于Linux环境。simavr已能够比较完善地支持128KB以下大小flash组件的模拟，而对于更大的flash空间也具备一定的支持能力。simavr能够直接加载elf文件运行，也支持hex文件的运行。

Debian系列Linux环境中，simavr的安装步骤如下（推荐采用编译方式安装）
1. $ sudo apt-get install gcc make gcc-avr avr-libc libelf-dev
1. $ git clone https://github.com/buserror/simavr.git
1. $ cd simavr
1. $ make all
avr-gdb则是AVR环境下的gdb调试工具，其使用与常规x86环境下的gdb类似。Debian系列Linux环境中，可以通过apt-get install进行安装。
1. $ sudo apt-get install gdb-avr


其他涉及到的工具主要为binutils-avr，同样可以通过apt install命令进行安装。binutils-avr工具包所包含的avr-objcopy支持对avr文件进行跨格式的复制、转换，例如从hex格式复制为bin格式文件等。binutils-avr中的avr-objdump同样能够将二进制代码反汇编，只是相对于radare2的反汇编效果而言，比较粗糙，且未集成人性化的分析功能组件。



## 三. 探索之旅

本文采用的题目是Flare On 2017年的第9题，其中，给出的素材是一个能够直接加载到开发板进行运行的hex文件。按照CTF题目的惯例，目标是找到解密后的某字符串。



### 3.1 模拟运行

面对该hex文件，首先自然想到的，是使用simavr工具将其加载运行看看具体效果。然而，simavr的执行需要指明所采用的具体处理器型号，以精确地进行模拟，如何获得处理器型号呢？抛开暴力遍历，我们不妨采用以下过程。

**第1步**：使用vim或其他编辑工具打开该hex文件，发现其每行形如 :1000…，这是典型地intel hex格式。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013d924a34fef26312.png)

**第2步**：利用avr-objcopy工具，将hex格式的文件转为bin格式文件。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b1120bc89f601173.png)

**第3步**：利用strings命令，从bin文件中尽可能提取线索性信息。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c6a9633efd11fb16.png)

其中，关键线索为Adruino UNO字符串，Arduino UNO是一个基于ATmega328p处理器、采用Atmel AVR指令集平台，因而，我们提交给simavr的机器型号应是atmega328p。

**第4步**：模拟运行

利用simavr工具中的run_avr子工具，指定机器型号为atmega328p，频率为16000000，成功运行程序。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fde31996a129966d.png)



### 3.2 静态分析

试探性地，我们使用radare2工具加载bin格式文件进行分析，看看能否找到有价值的线索。

**第1步**：加载bin文件

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0110adce4b64a72f65.png)

**第2步**：使用aaaaa命令进行初步分析

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01805644cd2915bf30.png)

**第3步**：使用afl命令列出所有函数（截图中仅给出部分），其中我们感兴趣的是位于0x000000c4（黄色文字）处的entry0函数，它是整个程序的核心入口。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01da59ef918bb429f7.png)

**第4步**：使用radare2的pd @ &lt;function name&gt;功能，对entry0函数进行反汇编，查查看其代码。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011796df3f13e1841f.png)

…

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c34c4ec4b56955ff.png)

…

在进行一些环境、栈相关的初始化之后，entry0呈现了两个线索性的函数调用，分别位于0xcd0和0xbf8。

**第5步**：继续使用pd @ &lt;function name&gt;，对内容相对更丰富、线索性更强的0xbf8处的函数进行考察，找到3个分支函数。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012230792d74be35bb.png)

**第6步**：在探索过程中，发现fcn.00000b40调用了fcn.00000ac6，其中，将r28寄存器的内容录入r24寄存器作为参数。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c21f93609f7a0b9e.png)

而fcn.00000ac6中含有明显的字符串录入（共计23个字符，这里仅给出部分）

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b401e7a2b6c5a175.png)

…

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e9a3b53de99249e3.png)

更重要的是，其后存在有比较明显的校验操作，该操作决定了后续的跳转分支。通过pd &lt;number of lines&gt; @ &lt;line number&gt;，反汇编0x00000aec处的代码，得到以下。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018fe852654aadbc02.png)

下面对这步可能发生的事情进行推断：

① 0xb7a处，将r28内容录入r24，并以r24作为参数，调用fcn.00000a6c；

② fcn.00000a6c中，先通过0x3d和0x3e这两个典型的SPL/SPH I/O寄存器的读写分配了栈空间，再将23个字符录入到该栈空间（此时0x00000ae4执行完毕）；

③ fcn.00000a6c中，继续将r27:r26（也即AVR体系中的x寄存器）设定为0x056c（此时0x00000ae8执行完毕）

④ 0x00000aea起，以r18中存储的0x17（即十进制23）为循环，通过z指针（最初指向栈上首字节，见0x00000a80和0x00000a82代码）分别操作每个栈上的字符，并将结果按顺序录入到由x指定的0x00000576起的空间中。其中，操作过程中eor所使用的r24即0xb7a中传入的参数，可以认为是key，而栈上的原始数据即为密文，整个操作过程即解密过程，解密结果放在0x56c起的空间里。

⑤ 验证解密结果的正确性，具体地，将0x576处的字符（解密结果中的第11个字符）与0x40对比，并根据比对结果决策分支。推测，当key错误时，分支即3.1章节中默认的Pin State输出。



### 3.3 动态调试

使用simavr，通过动态调试方法，尝试改变0x00000b7a处录入到r24中的参数值，考察输出的变化。

**第1步**：使用–gdb选项启动simavr的run_avr子工具。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01af1bee951ee1c666.png)

从输出可以看出，run_avr提供了一个gdb server，其监听的端口是本地的1234端口。

**第2步**：启动avr-gdb工具，并通过target remote :1234与gdb server建立连接。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015329bef162ec155e.png)

**第3步**：通过break命令，在0x00000b7a处设置断点，再通过continue命令，运行至断点处。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017a166f067503d038.png)

**第4步**：查看当前寄存器r28的值，并尝试将该值设置为其他值，并在0x00000afe处设置断点，再通过continue继续执行，以观测效果。以上几步可以通过脚本自动化进行，当输入正确的r28值（0xdb）时，效果如下，此时可以通过输出0x0000056c处的内容获取解密结果。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d788b80074a7dda6.png)

相应地，继续continue，能够看到程序完整输出。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0135a29b869d5fe8b0.png)

至此，获得本题答案为no_r3m0rs3@flare-on.com。



## 四. 头脑风暴

前面的分析中，先使用了纯静态分析铺垫，再使用了动态调试收尾。这是一种方法，但绝非唯一的方法。下面，分别从“动静结合”的角度，阐述一些解决问题过程中的实用技巧。

举例而言，第3.2章节的调试过程中，我们的函数fcn.00000b40实际包含着多个调用，具体为fcn.00000736、fcn.0000068c、fcn.00000664和fcn.00000a6c。而我们则直接将关注点定位到了fcn.00000a6c。

从静态分析的角度，这是因为fcn.00000a6c中含有明显的字符串录入操作；实际上，从动态调试入手，也可以将关注点缩减至相同的位置。

具体地，首先中断在例如0xb5c处，查看fcn.00000736函数的输入参数。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017cff072c1c1cf8c4.png)

显然，r23:r22中包含的是指向Flare-On …字符串的指针，那么，不妨优先猜测，该函数的作用是输出Flare-On … 字符串，并以冒号结尾。于是，接下来的fcn.0000068c则大概率是在输出pin state，即3.1中的111… 。这样，就相对容易地排除了一部分无需关注的函数，减轻了进一步定位关键函数的难度。

## 

## 五. 结语

AVR体系架构由来已久，凭借其精简高效的运行机制，为IoT与嵌入式行业所青睐。目前，业界对AVR体系的逆向研究远不如x86、arm等大牌体系结构深入，但随着近年来智能设备的兴起、汽车零配件的日益复杂化，AVR体系的安全成为了业界越发感兴趣且不得不关注的领域。

本文基于已有的安全考题，对已知的基于纯软件方式的解法进行复现，起到一个抛砖引玉的作用，也期待为苦于没有开发板与硬件工具链但对AVR安全有所兴趣想要学习、尝试的小伙伴提供些许思路。

目前，小伙伴们正在对深圳纽创信安（Open Security Research, OSR）CTF展开相关探索，之后还有更多内容与大家分享、交流。

[![](./img/202256/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fedb427be734cce9.jpg)

## 

## 参考文献

https://github.com/radareorg/radare2

https://github.com/buserror/simavr

http://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf

https://www.fireeye.com/content/dam/fireeye-www/global/en/blog/threat-research/Flare-On%202017/Challenge9.pdf

https://www.systutorials.com/docs/linux/man/1-avr-gdb/
