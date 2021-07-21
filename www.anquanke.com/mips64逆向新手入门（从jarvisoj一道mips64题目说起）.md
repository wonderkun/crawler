> 原文链接: https://www.anquanke.com//post/id/169503 


# mips64逆向新手入门（从jarvisoj一道mips64题目说起）


                                阅读量   
                                **237204**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t014790240d1397ddf9.jpg)](https://p1.ssl.qhimg.com/t014790240d1397ddf9.jpg)



CTF比赛的逆向已经发展到向arm和mips等嵌入式架构发展了，国内可以看到关于mips逆向的一些基础文章，但是对于mips64却介绍比较少，这里通过jarvisoj一道mips64的题目（来自于某强网杯）来看看mips64的一些坑，以及介绍新手如何入门逆向mips64。

题目链接 [Here](https://dn.jarvisoj.com/challengefiles/mips64.a85474526ff22aa84be8bf2c5a1c0f4f)

file一下程序，是mips64 rel2，静态编译且没有符号的。

```
root@kali:/mnt/hgfs/ctfsample/jarvisoj/mips64# file mips64
mips64: ELF 64-bit MSB executable, MIPS, MIPS64 rel2 version 1 (SYSV), statically linked, BuildID[sha1]=1fd09709a4c48cd14efe9454d332d16c1b096fd0, for GNU/Linux 3.2.0, stripped
```

拖入IDA64（7.0版本）分析，看到一堆sub函数，但是没有符号信息。

[![](https://i.imgur.com/2sQQNc6.png)](https://i.imgur.com/2sQQNc6.png)

也能看到关键的字符串，但是无法交叉引用查找调用点

[![](https://i.imgur.com/bf8v3Fw.png)](https://i.imgur.com/bf8v3Fw.png)

[![](https://i.imgur.com/qxW4vHb.png)](https://i.imgur.com/qxW4vHb.png)



## 准备调试环境

### <a class="reference-link" name="%E5%AE%89%E8%A3%85qemu"></a>安装qemu

在linux中安装qemu

```
sudo apt-get install qemu qemu-system qemu-user-static
```

然后尝试执行mips64的程序

```
qemu-mips64 ./mips64
```

可以看到程序运行效果如下

[![](https://i.imgur.com/uT4XpvS.png)](https://i.imgur.com/uT4XpvS.png)

### <a class="reference-link" name="%E7%BC%96%E8%AF%91mips64-linux-gdb"></a>编译mips64-linux-gdb

我是从源码编译mips64版的gdb开始，环境是kali2008(如下），默认配置gdb 8.1.1，所以选择同版本的gdb源码进行编译。

```
Linux kali 4.17.0-kali1-amd64 #1 SMP Debian 4.17.8-1kali1 (2018-07-24) x86_64 GNU/Linux
```

1.从gdb官网[http://www.gnu.org/software/gdb/download/下载[gdb-8.1.1.tar.gz](https://ftp.gnu.org/gnu/gdb/gdb-8.1.1.tar.gz](http://www.gnu.org/software/gdb/download/%E4%B8%8B%E8%BD%BD%5Bgdb-8.1.1.tar.gz%5D(https://ftp.gnu.org/gnu/gdb/gdb-8.1.1.tar.gz))

2.将gdb-8.1.1.tar.gz 拷贝到任何你愿意的Linux目录下, 解压

```
tar -zxvf gdb-8.1.1.tar.gz
```

3.编译mips64-linux-gdb

到目录gdb-8.1.1下，编译命令

```
cd gdb-8.1.1
./configure --target=mips64-linux --prefix=/usr/local/mips64-gdb -v
make
make install
```

安装成功后，可以在 /usr/local/mips64-gdb/bin 目录中看到这两个文件

mips64-linux-gdb mips64-linux-run

4.运行mips64-linux-gdb

```
root@kali:/usr/local/mips64-gdb/bin# /usr/local/mips64-gdb/bin/mips64-linux-gdb
GNU gdb (GDB) 8.1.1
Copyright (C) 2018 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later &lt;http://gnu.org/licenses/gpl.html&gt;
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "--host=x86_64-pc-linux-gnu --target=mips64-linux".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
&lt;http://www.gnu.org/software/gdb/bugs/&gt;.
Find the GDB manual and other documentation resources online at:
&lt;http://www.gnu.org/software/gdb/documentation/&gt;.
For help, type "help".
Type "apropos word" to search for commands related to "word".
(gdb)
```

5.一些说明
- 使用IDA7.0 也可以链接gdbserver，可以设置断点，但是在调试过程中，F8（单步执行）经常跑飞，所以IDA会作为静态分析，就像pwn那样。
- 网上还有介绍使用 gdb-multiarch 调试的，直接apt-get可以安装，效果应该与源码编译雷同，有兴趣的朋友可以试试。
### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%20gdb%20%E8%B0%83%E8%AF%95qemu"></a>使用 gdb 调试qemu

启动qemu时，使用-g 9999 开启 gdbserver ，9999是调试端口号，gdb中用这个端口号链接gdbserver。

```
# qemu-mips64 -g 9999 ./mips64
```

然后在mips64-linux-gdb中链接gdbserver调试
- file 指定被调试的文件
- set architecture 根据目标程序的类型选择，参看之前file的结果，也可以用tab查看可以设置为什么类型。
- target remote 是链接远程gdbserver，链接后程序停在 0x0000000120003c50 ，这是程序的入口地址，用IDA可以验证
```
(gdb) file mips64
Reading symbols from mips64...(no debugging symbols found)...done.
(gdb) set architecture mips:isa64r2
The target architecture is assumed to be mips:isa64r2
(gdb) target remote localhost:9999
Remote debugging using localhost:9999
0x0000000120003c50 in ?? ()
```

[![](https://i.imgur.com/1OkhSiN.png)](https://i.imgur.com/1OkhSiN.png)

mips64-linux-gdb调试指令和gdb是一样的，常用的有：

```
i r #查看所有寄存器
i fl #查看所有fpu
c  #继续程序到下一个断点
ni #单步执行
x /10i $pc #查看当前指令情况
```



## mips64基础知识

可以参考附录里面各种mips汇编指令的介绍，这里重点介绍几点与x86逆向调试不同的地方，了解了这些会让逆向事半功倍。

1.函数的输入参数分别在寄存器a0,a1,a2…中，关注这几个寄存器的值，就可以知道某个函数如sub_120022504(a0,a1,a2)的输入参数<br>
2.mips64的跳转指令时（b开头的指令），会执行跳转后一条语句之后再跳，这叫分支延迟。

如下面的代码片段，bc1f是跳转指令，满足条件跳转至 loc_120003B24 。无论是否满足跳转条件，都会先执行 ld $t9, -0x7F68($gp) 那条指令，再跳到 loc_120003B24 或者 ld $a0, -0x7F78($gp) 。gdb断点只能下到 0x120003C24 或 0x120003C2C，无法下到0x120003C28。

```
.text:0000000120003C20 loc_120003C20:
.text:0000000120003C20                 c.lt.s  $fcc6, $f1, $f0
.text:0000000120003C24                 bc1f    $fcc6, loc_120003B24
.text:0000000120003C28                 ld      $t9, -0x7F68($gp)
.text:0000000120003C2C                 ld      $a0, -0x7F78($gp)
.text:0000000120003C30                 ld      $a1, -0x7F58($gp)
```

3.本程序涉及大量的fpu操作（浮点运算单元），可在gdb中使用`i fl`（info float）指令查看fpu，下文的f0、f12等都是fpu。

[![](https://i.imgur.com/wDo8bqR.png)](https://i.imgur.com/wDo8bqR.png)

4.fpu会有single（单精度）和double（双精度）表示，以上图f0为例，其单精度值（flt)为4，双精度值(dbl)为13.000001922249794。如果汇编指令是 c.lt.s (最后的s表示以单精度的计算），会判断 $f1（flt) &lt; $f0（flt)，即4是否小于0.5，而不是13是否小于122。

```
.text:0000000120003BA8                 c.lt.s  $f1, $f0         
.text:0000000120003BAC                 bc1f    loc_120003BCC    
.text:0000000120003BB0                 ld      $v0, -0x7F78($gp)  
.text:0000000120003BB4                 lwc1    $f1, -0x116C($v0)
```

c.lt.s 意思大概是 compare less than in single ( c.lt.d 则是在double，即双精度范围计算）<br>
bc1f : jump if compare result is false （f表示false，bc1t 表示 true才跳）

5.程序中多次出现以下片段，多次出现的`-0x7f78`是程序里面一个基地址，将基地址赋值给$v0寄存器，第二句再根据这个基地址（$v0），取一个常量到寄存器或fpu（$f1 = [$v0-0x1164])。

```
ld      $v0, -0x7F78($gp)
lwc1    $f1, -0x1164($v0)
```



## 逆向过程

qemu使用-strace参数，让程序输出更多的调试信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/lDVkDCl.png)

可以看到系统使用了write(1,0x200b97d0,40)来输出“Welcome to QWB, Please input your flag:”这40个字符，联想到x64架构1表示stdout,0x200b97d0表示字符串地址，40表示输出长度

从write(1,0x200b97d0,40)到write(1,0x200b97d0,12)之间，有一个Linux(0,4832599008,1024,0,4832599008,4)，猜测就是一个read函数系统调用了，要逆向就要知道read函数到输出Wrong Flag！之间发生什么，调用了哪些函数。



## 定位输入点

由于gdbserver调试不能用ctrl+c中断再下断点，所以从IDA将所有可能是函数的地址复制出来

[![](https://i.imgur.com/t6O3Jcy.png)](https://i.imgur.com/t6O3Jcy.png)

编辑成为gdb断点的格式，并粘贴到gdb中，大约600多个断点

[![](https://i.imgur.com/ddMYlfh.png)](https://i.imgur.com/ddMYlfh.png)

[![](https://i.imgur.com/3yhtu9c.png)](https://i.imgur.com/3yhtu9c.png)

用qemu-mips64 -strace -g 9999 ./mips64启动程序，在gdb侧链接gdbserver后不停的按c，直至程序堵塞等待输入，这是看到最后一个触发的断点是：0x0000000120022404，说明输入在这里附近

[![](https://i.imgur.com/uRS0PLK.png)](https://i.imgur.com/uRS0PLK.png)

然后在程序随便输入内容，如1234回车，让程序继续执行。在gdb一路c，直到看到程序输出Wrong Flag!，记录这段时间的断点。

[![](https://i.imgur.com/X8tC6uc.png)](https://i.imgur.com/X8tC6uc.png)

```
0x0000000120014740 in ?? ()
0x0000000120014740 in ?? ()
0x000000012001f110 in ?? ()
0x000000012000d6b0 in ?? ()
0x000000012001f110 in ?? () 
0x00000001200206e0 in ?? () 
0x00000001200138a0 in ?? () 
0x0000000120012978 in ?? ()
0x0000000120012120 in ?? () 
0x000000012000ffc8 in ?? () 
0x00000001200112f0 in ?? () 
0x0000000120022504 in ?? ()
```

gdb中按d清理所有断点，重新设置断点为上述函数

```
b* 0x0000000120014740
b* 0x0000000120014740
b* 0x000000012001f110
b* 0x000000012000d6b0
b* 0x000000012001f110
b* 0x00000001200206e0
b* 0x00000001200138a0
b* 0x0000000120012978
b* 0x0000000120012120
b* 0x000000012000ffc8
b* 0x00000001200112f0
b* 0x0000000120022504
```

我们从后开始看，看到函数0x0000000120022504执行时，其输入参数是（1，0x1200b97d0, 0xc），查看内存，是输出Wrong Flag的函数。a1已经指向WrongFlag字符串了。

```
Breakpoint 618, 0x0000000120022504 in ?? ()
(gdb) i r
...
                    a0               a1               a2               a3
 R4   0000000000000001 00000001200b97d0 000000000000000c fffffffffbad2a84 

(gdb) x/s $a1
0x1200b97d0:    "Wrong Flag!nWB, Please input your flag: "
```

用同样的方法一路往前看在进入0x12000d6b0时，a0已经是WrongFlag字符串，而进入 0x12001f110 时，a0指向用户输入的字符串，说明 0x12001f110 是关键函数，用于判断用户输入是否正确的。



## 定位关键

在0x12001f110函数中逐行调试（ni指令），返回到了 0x120003ac0 (sub_120003AC0)，有这么一段指令，这是调用0x12001f110的地方，`beq $v0, $v1`是将输入长度和0x10进行比较

```
.text:0000000120003B10                 bal     sub_12001F110  # a0为用户输入
.text:0000000120003B14                 ld      $a0, -0x7F58($gp)
.text:0000000120003B18                 li      $v1, 0x10  # sub_12001f110+110时返回到这里
.text:0000000120003B1C                 beq     $v0, $v1, key  # v0=len(input),v1=0x10
.text:0000000120003B20                 ld      $t9, -0x7F40($gp)
```

[![](https://i.imgur.com/aflec7D.png)](https://i.imgur.com/aflec7D.png)

如果比较不相等，则一路调用sub_12000D6B0（根据上面的回溯分析，调用时a0已经是指向WrongFlag字符串了），所以**输入长度是16个字符**

确定输入长度后，可以使用 `qemu-mips64 -strace -g 9999 ./mips64 &lt;1.payload` 来启动程序，在同目录的1.payload文件中输入1234567890abcdef

输入16个字符，程序会走另一个分支。在0x120003B5C的代码片段中，调用了4个**关键函数**(sub_120003EB0、sub_120004278、sub_120004640 和 sub_120004A08)。每个函数调用返回后，都会对fpu的f24/f25/f26和f0操作，最终可以看成是f0等于4个函数执行的结果。

[![](https://i.imgur.com/OotuUSY.png)](https://i.imgur.com/OotuUSY.png)

```
f0 = sub_120003EB0(...) + sub_120004278(...) + sub_120004640(...) + sub_120004A08(...)
```

断点设置在 0x120003BA8，f0(值为0,因为指令是c.lt.s，s表示单精度）与0.5比较

```
Breakpoint 619, 0x0000000120003ba8 in ?? ()
(gdb) i fl
fpu type: double-precision
reg size: 64 bits
...
f0:  0x4018000000000000 flt: 0                 dbl: 6                       
f1:  0x404cc0003f000000 flt: 0.5               dbl: 57.500007510185242
```

运行至0x120003BD0，f0 与 1.5比较；<br>
运行至0x120003bf8，f0 与 2.5比较；<br>
运行至0x120003c20，f0 与 3.5比较，如果此时f0小于3.5，则跳转到粉红色区域，即输出WrongFlag的函数。

所以逆向的目标就是让f0大于3.5（ctf老司机可能意识到就是让f0=4.0，上面4个函数都输出1.0，加起来就是4.0了）



## 逆向算法

以第一个函数 sub_120003EB0 为例，查看其执行时输入a0为输入字符串

```
Breakpoint 620, 0x0000000120003eb0 in ?? ()
(gdb) i r
                  zero               at               v0               v1
 R0   0000000000000000 0000000000000001 0000000000000010 0000000000000010 
                    a0               a1               a2               a3
 R4   00000001200b6140 0000000000000000 ffffffffffffffff 8080808080808080 

...
(gdb) x/s $a0
0x1200b6140:    "1234567812345678"
```

单步执行，发现程序读取了输入的前4字节（想想有4个函数，一次读取4个字节处理，正好16字节）

根据上面在“mips64基础知识”提及的调试经验，在`-0x7F78($gp)`这个基础地址之上，读取了两个偏移值，为47.5和57.5，与输入比较，比较明显的在判断输入的上下界。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/srFnGCX.png)

然后看到将输入f0 = input[0] – 48.0，48是ascii的’0’字符串。看到判断上下界和减去0操作，逆向老司机会相当熟悉，这就是**字符转数字**，定义为digit[0]。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/qkVkQ5O.png)

然后继续跟踪看到是将 f12 = digit[0]*16+digit[2] = 19.0 (以输入1234567890abcdef为例），就是在转换16进制数。这个过程中有较多的浮点数计算和精度转换指令，需要耐心跟踪。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/sUJ54Ce.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/2LmSnSM.png)

然后在0x120004138 进入了函数 sub_120004EB0，从函数返回后，有明显的f0和f1比较。

```
.text:0000000120004134 loc_120004134:                           # CODE XREF: sub_120003EB0:loc_120004198↓j
.text:0000000120004134                                          # sub_120003EB0+368↓j ...
.text:0000000120004134                 ld      $t9, -0x7F70($gp)
.text:0000000120004138                 bal     sub_120004EB0
.text:000000012000413C                 nop
.text:0000000120004140                 ld      $v0, -0x7F78($gp)
.text:0000000120004144                 lwc1    $f1, -0x1190($v0)
.text:0000000120004148                 c.eq.s  $f0, $f1
.text:000000012000414C                 bc1f    loc_120004178
.text:0000000120004150                 ld      $ra, 0x20+var_18($sp)
.text:0000000120004154                 add.d   $f12, $f25, $f24
.text:0000000120004158                 ld      $t9, -0x7F70($gp)
.text:000000012000415C                 bal     sub_120004EB0
.text:0000000120004160                 cvt.s.d $f12, $f12
.text:0000000120004164                 ld      $v0, -0x7F78($gp)
.text:0000000120004168                 lwc1    $f1, -0x118C($v0)
.text:000000012000416C                 c.eq.s  $fcc1, $f0, $f1
.text:0000000120004170                 bc1t    $fcc1, loc_1200041B0
.text:0000000120004174                 ld      $ra, 0x20+var_18($sp)
```

设置断点0x120004148观察fpu，因为比较的是用c.eq.s指令，用单精度进行比较，所以是19和83（f1的值，从全局变量中加载，是个常量）比较

```
Breakpoint 621, 0x0000000120004148 in ?? ()
(gdb) i fl
fpu type: double-precision
...
f0:  0x4010000041980000 flt: 19                dbl: 4.0000009774230421      
f1:  0x404cc00042a60000 flt: 83                dbl: 57.500007945112884      
f2:  0x0000000000000000 flt: 0                 dbl: 0
```

直觉告诉我们需要让其相等，以继续运行

```
19/16 = 1 &lt;==&gt;  83/16 = 5
19%16 = 3 &lt;==&gt;  83%16 = 3
```

所以原来输入（1234…)，要对应修改为5234..(1改成5，3改成3）

修改输入后重新执行程序，原来不执行的0x12000415C也执行了，第二次进入函数 sub_120004EB0，函数返回后在0x12000416C进行了比较

```
Breakpoint 622, 0x000000012000416c in ?? ()
(gdb) i fl
fpu type: double-precision
reg size: 64 bits
...
f0:  0x4010000042100000 flt: 36                dbl: 4.0000009844079614      
f1:  0x404cc00042880000 flt: 68                dbl: 57.500007931143045      
f2:  0x0000000000000000 flt: 0                 dbl: 0
```

同理

```
36/16 = 2 &lt;==&gt;  68/16 = 4
36%16 = 4 &lt;==&gt;  68%16 = 4
```

所以原来输入（5234…)，要对应修改为5434…(2改成4，4改成4）

在修改了前4字节后，在原来 0x120003BA8 设置断点，就是4个关键函数返回值之和与0.5比较的地方，此时我们可以看到f0已经变成1

```
Breakpoint 623, 0x0000000120003ba8 in ?? ()
(gdb) i fl
fpu type: double-precision
reg size: 64 bits
cond    : 1 2 3 4 5 6 7
cause   :
mask    :
flags   :
rounding: nearest
flush   : no
nan2008 : no
abs2008 : no

f0:  0x401800003f800000 flt: 1                 dbl: 6.0000009462237358      
f1:  0x404cc0003f000000 flt: 0.5               dbl: 57.500007510185242
```

这时候在IDA中查找函数 sub_120004EB0 的交叉引用，函数被调用了8次，上述提及的4个关键函数都各调用了2次，说明规律是类似的。只要在这8个地方附近设置断点，用同样的规律修改输入，即可让4个关键函数之和为4。

[![](https://i.imgur.com/bnCEl0x.png)](https://i.imgur.com/bnCEl0x.png)

输入正确时，程序提示正确

[![](https://i.imgur.com/KtqTuoX.png)](https://i.imgur.com/KtqTuoX.png)



## 总结
1. mips64 目前缺乏分析工具（此题使用jeb和retdec都无法反编译），IDA对字符串的交叉引用也无法工作，让逆向难度加大。
1. 此题根据较为原始的调试方法也可以定位出read和write等常见函数，也可以考虑使用Rizzo等工具恢复符号。
1. 原本此程序的算法可以在整数域上进行，偏偏在浮点数域上编写，使得程序中使用了大量浮点数计算和转换，这些都增加了逆向难度。
1. 注意mips64的分支延时等与x86不同的特性，才能更好的迁移x86逆向知识到mips逆向中。


## 附录

由于mips指令和x86指令差异较大，需要查阅网上mips指令的相关说明，结合动态调试理解。
- [https://people.cs.pitt.edu/~childers/CS0447/lectures/SlidesLab92Up.pdf](https://people.cs.pitt.edu/~childers/CS0447/lectures/SlidesLab92Up.pdf)
- [https://www.d.umn.edu/~gshute/mips/data-comparison.xhtml#fp-compare](https://www.d.umn.edu/~gshute/mips/data-comparison.xhtml#fp-compare)
- [https://www.doc.ic.ac.uk/lab/secondyear/spim/node20.html](https://www.doc.ic.ac.uk/lab/secondyear/spim/node20.html)
- [https://stackoverflow.com/questions/22770778/how-to-set-a-floating-point-register-to-0-in-mips-or-clear-its-value](https://stackoverflow.com/questions/22770778/how-to-set-a-floating-point-register-to-0-in-mips-or-clear-its-value)
- [http://www.mrc.uidaho.edu/mrc/people/jff/digital/MIPSir.html](http://www.mrc.uidaho.edu/mrc/people/jff/digital/MIPSir.html)
- [https://scc.ustc.edu.cn/zlsc/lxwycj/200910/W020100308600769158777.pdf](https://scc.ustc.edu.cn/zlsc/lxwycj/200910/W020100308600769158777.pdf)