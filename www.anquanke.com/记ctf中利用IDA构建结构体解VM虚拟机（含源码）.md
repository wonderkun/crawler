> 原文链接: https://www.anquanke.com//post/id/252573 


# 记ctf中利用IDA构建结构体解VM虚拟机（含源码）


                                阅读量   
                                **24251**
                            
                        |
                        
                                                                                    



[<img class="alignnone size-full wp-image-252719 aligncenter" alt="" width="720" height="370" data-original="https://p3.ssl.qhimg.com/t01aedac2bf56ad8fc3.jpg">](https://p3.ssl.qhimg.com/t01aedac2bf56ad8fc3.jpg)



## VM前言

**简述VM：**

逆向中的虚拟机保护是一种基于虚拟机的代码保护技术。它将基于x86汇编系统中的可执行代码转换为字节码指令系统的代码，来达到不被轻易逆向和篡改的目的。

简单点说就是将程序的代码转换**自定义的操作码**(opcode)，然后在程序执行时再通过**解释这些操作码**，**选择对应的函数执行**，从而实现程序原有的功能。一般是循环语句嵌套if语句或者switch-case语句

**VM虚拟机的基本成员**

一般我们定义一个结构体，来表示虚拟机，包含以下：

**通用寄存器**：自定义几个字节的成员作为寄存器

**eip**：类似汇编中的eip，指向虚拟机下一步要解释运行的opcode

**指令集**：每个指令对应的handle函数，解释自定义指令的功能

**Stack**：我们定义一块内存空间空间，作为虚拟机的堆栈，方便我们的处理数据

[<img class="alignnone size-full wp-image-252704 aligncenter" alt="" width="734" height="530" data-original="https://p1.ssl.qhimg.com/t01c418f4d0741657d6.png">](https://p1.ssl.qhimg.com/t01c418f4d0741657d6.png)

**VM测试**：

这里给了一个ctf中标准的VM虚拟机题**exe**和**C源码**。

源码环境：win10、VC++6.0

> <p>链接：[https://pan.baidu.com/s/1PMdjQ9gvwGFqL0UgHAnA-A](https://pan.baidu.com/s/1PMdjQ9gvwGFqL0UgHAnA-A)<br>
提取码：hzd9</p>

利用IDA构建结构体解VM虚拟机

对应的详细wp在下面。



## ctf-wp：little_vm

### <a class="reference-link" name="0%E3%80%81%E6%9F%BB%E5%A3%B3"></a>0、査壳

[<img class="alignnone size-full wp-image-252705 aligncenter" alt="" width="677" height="330" data-original="https://p0.ssl.qhimg.com/t0115afaf75f5f6fec9.png">](https://p0.ssl.qhimg.com/t0115afaf75f5f6fec9.png)

无壳

### <a class="reference-link" name="1%E3%80%81IDA%E6%89%93%E5%BC%80"></a>1、IDA打开

IDA打开后，查看主函数，整体结构比较清晰，但有两个关键函数，，

[<img class="alignnone size-full wp-image-252706 aligncenter" alt="" width="1747" height="1191" data-original="https://p3.ssl.qhimg.com/t01e28d9b942de66884.png">](https://p3.ssl.qhimg.com/t01e28d9b942de66884.png)

很显然要分析这两个函数`v4=sub_401028()`和`sub_40100A((int)v4)`

### <a class="reference-link" name="2%E3%80%81%E5%88%86%E6%9E%90sub_401028()"></a>2、分析sub_401028()

**<a class="reference-link" name="%EF%BC%881%EF%BC%89%E8%BF%9B%E5%85%A5%E5%88%86%E6%9E%90"></a>（1）进入分析**

进入`sub_401028()`函数

[<img class="aligncenter" alt="image-20210720225332001" data-original="https://gitee.com/cht1/Image/raw/master/img_1/image-20210720225332001.png">](https://gitee.com/cht1/Image/raw/master/img_1/image-20210720225332001.png)

可以发现这个函数的功能就是对v1指向内存的配置，可以概括为初始化initialize。

> 一般这种对一块内存的设置，我们可以把它看做结构体，且IDA内可以构造结构体

可以对v1指向的内存看做结构体，根据他这初始化的过程，我们可以构造对应的结构体。

（这里很显然就是虚拟机）

**<a class="reference-link" name="%EF%BC%882%EF%BC%89IDA%E7%BB%93%E6%9E%84%E4%BD%93%E5%AE%9A%E4%B9%89"></a>（2）IDA结构体定义**

> IDA构造结构体快捷键
Shift+f9：来到构造结构体的页面
insert：插入一个结构体
在结构体内按d键：添加一个成员
d键：更改成员的大小 db dw dd
n键：更改成员名字
重要：y键：更改成员类型：（与C语言类型一致）（定义函数int (**)(int **) ）
u键：删除成员
(右键列表里有相关设置)

[<img class="alignnone size-full wp-image-252707 aligncenter" alt="" width="1747" height="1191" data-original="https://p0.ssl.qhimg.com/t0182e56463f8b2bec6.png">](https://p0.ssl.qhimg.com/t0182e56463f8b2bec6.png)

> 结构体各类型设置
int r1
int r2
int r3
byte *epi
vm_opcode op_list[4]
byte opcode
int (__stdcall func_addr)(int )

然后返回函数y键更改数据类型为结构体（类型为我们自定义的cpu*）

[<img class="alignnone size-full wp-image-252708 aligncenter" alt="" width="1747" height="1191" data-original="https://p3.ssl.qhimg.com/t016571104ac52dcd24.png">](https://p3.ssl.qhimg.com/t016571104ac52dcd24.png)

上面的&amp;unk_4284F8应该就是虚拟机的opcode

下面的内存空间dword_428E28暂时还不知道什么意思，但是一般虚拟机都有一个堆栈，猜测这一块开辟的内存是虚拟机的堆栈。

**<a class="reference-link" name="%EF%BC%883%EF%BC%89%E5%85%B3%E9%94%AE%E6%84%8F%E4%B9%89"></a>（3）关键意义**

**这是一个虚拟机!**

r1、r2、r3代表寄存器

eip执行要执行的opcode

有四种指令（F1，F2，F5，F9）分别对应4个函数，即代表四种指令的意义

**<a class="reference-link" name="%EF%BC%884%EF%BC%89%E7%BB%93%E8%AE%BA"></a>（4）结论**

sub_40100A((int)v4);这个函数可以命名为initialize，（以下2称其为初始化函数）

返回值v1即为我们定义的cpu结构体指针，

我们知道有四个指令即可，先摸清大致思路，细节等下分析

先分析主程序的第二函数sub_40100A((int)v4)

### <a class="reference-link" name="3%E3%80%81%E5%88%86%E6%9E%90sub_40100A((int)v4);"></a>3、分析sub_40100A((int)v4);

这里参数v4是初始化函数的返回值，即为我们定义的cpu结构体指针，

还是按y键改变其类型（这里要改变函数类型，才能改变参数类型）

[<img class="alignnone size-full wp-image-252709 aligncenter" alt="" width="1747" height="1191" data-original="https://p4.ssl.qhimg.com/t012463ad23aa7f3586.png">](https://p4.ssl.qhimg.com/t012463ad23aa7f3586.png)

**<a class="reference-link" name="%EF%BC%881%EF%BC%89%E8%BF%9B%E5%85%A5%E5%88%86%E6%9E%90"></a>（1）进入分析**

由于实现改变了函数类型（为了改变参数类型为cpu*），可以发现这一块也很清晰

[<img class="alignnone size-full wp-image-252710 aligncenter" alt="" width="1747" height="1191" data-original="https://p1.ssl.qhimg.com/t0103f7c17268ba114e.png">](https://p1.ssl.qhimg.com/t0103f7c17268ba114e.png)

（这里的if语句判断指令为f4即终止循环，而先前的指令集里面没有f4）

进入虚拟机的opcode：&amp;unk_4284F8，

[<img class="alignnone size-full wp-image-252711 aligncenter" alt="" width="1747" height="1191" data-original="https://p0.ssl.qhimg.com/t0129906de5c4169796.png">](https://p0.ssl.qhimg.com/t0129906de5c4169796.png)

下一步分析虚拟机分发器中的sub_401032((int)a1)函数

**<a class="reference-link" name="%EF%BC%882%EF%BC%89%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%88%86%E5%8F%91%E5%99%A8%E4%B8%AD%E7%9A%84sub_401032((int)a1)%E5%87%BD%E6%95%B0"></a>（2）虚拟机分发器中的sub_401032((int)a1)函数**

这里同样要更y键改函数的类型（为了更改参数类型为cpu*）

进来之后发现这里大概是识别我们opcode里的指令

[<img class="alignnone size-full wp-image-252712 aligncenter" alt="" width="1747" height="1191" data-original="https://p5.ssl.qhimg.com/t01698da53803f7c97b.png">](https://p5.ssl.qhimg.com/t01698da53803f7c97b.png)

**<a class="reference-link" name="%EF%BC%883%EF%BC%89%E7%BB%93%E8%AE%BA"></a>（3）结论**

现在整个虚拟机的大致执行框架已经分析完了，大致熟悉了

[<img class="alignnone size-full wp-image-252713 aligncenter" alt="" width="1525" height="763" data-original="https://p0.ssl.qhimg.com/t010777f49db4964210.png">](https://p0.ssl.qhimg.com/t010777f49db4964210.png)

现在就可以分析四个指令了。

### <a class="reference-link" name="3%E3%80%81%E5%88%86%E6%9E%90%E5%9B%9B%E4%B8%AA%E6%8C%87%E4%BB%A4"></a>3、分析四个指令

回到初始化函数中，分析指令（0xF1、0xF2、0xF5、0xF9）

```
//这里是虚拟机的初始化函数
cpu *sub_401070()
`{`
  cpu *cpu; // [esp+4Ch] [ebp-4h]

  cpu = (cpu *)malloc(0x30u);
  cpu-&gt;r1 = 0;
  cpu-&gt;r2 = 0;
  cpu-&gt;r3 = 0;
  cpu-&gt;epi = (byte *)&amp;unk_4284F8;
  cpu-&gt;op_list[0].opcode = 0xF1;
  cpu-&gt;op_list[0].func_addr = (int (__stdcall *)(int))sub_40102D;
  cpu-&gt;op_list[1].opcode = 0xF2;
  cpu-&gt;op_list[1].func_addr = (int (__stdcall *)(int))sub_40101E;
  cpu-&gt;op_list[2].opcode = 0xF5;
  cpu-&gt;op_list[2].func_addr = (int (__stdcall *)(int))sub_40100F;
  cpu-&gt;op_list[3].opcode = 0xF9;
  cpu-&gt;op_list[3].func_addr = (int (__stdcall *)(int))sub_401005;
  dword_428E28 = malloc(0x512u);
  memset(dword_428E28, 0, 0x512u);
  return cpu;
`}`
```

分析四个函数，为了方便分析，我把指令对应函数名字稍微改一下

|指令|函数|更改函数名
|------
|0xF1|sub_40102D|Func_0xF1
|0xF2|sub_40101E|Func_0xF2
|0xF5|sub_40100F|Func_0xF5
|0xF9|sub_401005|Func_0xF9

**注意更改每个函数的类型（更改函数的参数类型为cpu*）**

Shift+E提取出opcode

```
unsigned char ida_chars[] =
`{`
  0xF5, 0xF1, 0xE5, 0x97, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x00, 
  0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x20, 0x00, 0x00, 0x00, 
  0xF1, 0xE1, 0x01, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x21, 
  0x00, 0x00, 0x00, 0xF1, 0xE1, 0x02, 0x00, 0x00, 0x00, 0xF2, 
  0xF1, 0xE4, 0x22, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x03, 0x00, 
  0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x23, 0x00, 0x00, 0x00, 0xF1, 
  0xE1, 0x04, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x24, 0x00, 
  0x00, 0x00, 0xF1, 0xE1, 0x05, 0x00, 0x00, 0x00, 0xF2, 0xF1, 
  0xE4, 0x25, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x06, 0x00, 0x00, 
  0x00, 0xF2, 0xF1, 0xE4, 0x26, 0x00, 0x00, 0x00, 0xF1, 0xE1, 
  0x07, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x27, 0x00, 0x00, 
  0x00, 0xF1, 0xE1, 0x08, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 
  0x28, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x09, 0x00, 0x00, 0x00, 
  0xF2, 0xF1, 0xE4, 0x29, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x0A, 
  0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x2A, 0x00, 0x00, 0x00, 
  0xF1, 0xE1, 0x0B, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x2B, 
  0x00, 0x00, 0x00, 0xF9, 0xF4, 0x00, 0x00, 0x00
`}`;
```

分析虚拟机指令集有个技巧，就是**根据opcode中的指令顺序来分析指令含义**

所以先分析F5指令

**<a class="reference-link" name="%EF%BC%881%EF%BC%89%E5%88%86%E6%9E%90%E6%8C%87%E4%BB%A40xF5%E5%AF%B9%E5%BA%94sub_40100F%E5%87%BD%E6%95%B0"></a>（1）分析指令0xF5对应sub_40100F函数**

[<img class="alignnone size-full wp-image-252714 aligncenter" alt="" width="1747" height="1191" data-original="https://p2.ssl.qhimg.com/t018a00114d0f4091ed.png">](https://p2.ssl.qhimg.com/t018a00114d0f4091ed.png)

这里验证了dword_428E28大概就是堆栈内存，所以n键改名为stack

|指令（操作码）|操作数|功能
|------
|F5|无|将输入字符串Str2压入堆栈

按照opcode字节码序列，下一个指令是F1

**此时虚拟机执行的功能为将输入字符串Str2压入堆栈。**

**<a class="reference-link" name="%EF%BC%882%EF%BC%89%E5%88%86%E6%9E%90%E6%8C%87%E4%BB%A40xF1%E5%AF%B9%E5%BA%94sub_40102D%E5%87%BD%E6%95%B0"></a>（2）分析指令0xF1对应sub_40102D函数**

[<img class="alignnone size-full wp-image-252715 aligncenter" alt="" width="2443" height="1191" data-original="https://p0.ssl.qhimg.com/t01762c93f3c8d5f924.png">](https://p0.ssl.qhimg.com/t01762c93f3c8d5f924.png)

这个指令0xF1可以大致理解为mov的升级版MovPro，

IDA中最下面的这两行代码，说明F1指令的长度为6

```
result = &amp;a1-&gt;r1;
  a1-&gt;epi += 6;
```

<th style="text-align: right;">指令（操作码）</th>|操作数1（1byte）|操作数2（4byte）|功能（对应汇编指令）
|------
<td style="text-align: right;">0xF1</td>|0xE1|x|mov r1，stack[x]
<td style="text-align: right;"></td>|0xE2|x|mov r2，stack[x]
<td style="text-align: right;"></td>|0xE3|x|mov r3，stack[x]
<td style="text-align: right;"></td>|0xE4|x|mov stack[x] , r1
<td style="text-align: right;"></td>|0xE5|x|mov r2，x

所以0xF1指令有两个操作数，操作数1只占1字节，操作数2占4字节，指令总共占6字节。

**此时虚拟机执行的功能是设置寄存器的值为0x97**

执行完之后，下一个指令也是0xF1，<code>0xF1, 0xE1, 0x00,<br>
0x00, 0x00, 0x00,</code>这里分析了，宽度6字节，对应含义为`mov r1，stack[0]`

找到下一条指令为F2

**<a class="reference-link" name="%EF%BC%883%EF%BC%89%E5%88%86%E6%9E%90%E6%8C%87%E4%BB%A40xF2%E5%AF%B9%E5%BA%94sub_40101E%E5%87%BD%E6%95%B0"></a>（3）分析指令0xF2对应sub_40101E函数**

[<img class="alignnone size-full wp-image-252716 aligncenter" alt="" width="1747" height="1191" data-original="https://p1.ssl.qhimg.com/t01f671734584364422.png">](https://p1.ssl.qhimg.com/t01f671734584364422.png)

|指令（操作码）|操作数|功能
|------
|0xF1|无|寄存器取值加密 结果存储与r1中 a1-&gt;r1 = ~(a1-&gt;r2 ^ a1-&gt;r1) ^ 0x12

**此时虚拟机执行的功能是取出寄存器r1、r2中的数，进行简易加密，结果存储与r1中**

最后只有一个指令了，直接分析即可

**<a class="reference-link" name="%EF%BC%883%EF%BC%89%E5%88%86%E6%9E%90%E6%8C%87%E4%BB%A40xF9%E5%AF%B9%E5%BA%94%20sub_401005%E5%87%BD%E6%95%B0"></a>（3）分析指令0xF9对应 sub_401005函数**

[<img class="alignnone size-full wp-image-252717 aligncenter" alt="" width="1747" height="1191" data-original="https://p0.ssl.qhimg.com/t014f3057e7842fa682.png">](https://p0.ssl.qhimg.com/t014f3057e7842fa682.png)

|指令（操作码）|操作数|功能
|------
|0xF9|无|把堆栈地址&amp;stack[32]处的数据复制到Str2中

猜测应该是最后调用这个数据，取出虚拟机加密的数据

**<a class="reference-link" name="%EF%BC%885%EF%BC%89%E7%BB%93%E8%AE%BA"></a>（5）结论**

最后，分析程序运行的框架，又分析了虚拟机指令集，最后要做的，就是挨着看虚拟机的opcode，把虚拟机运行流程给分析出来。

### <a class="reference-link" name="4%E3%80%81%E5%88%86%E6%9E%90opcode"></a>4、分析opcode

```
unsigned char ida_chars[] =
`{`
  0xF5, 0xF1, 0xE5, 0x97, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x00, 
  0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x20, 0x00, 0x00, 0x00, 
  0xF1, 0xE1, 0x01, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x21, 
  0x00, 0x00, 0x00, 0xF1, 0xE1, 0x02, 0x00, 0x00, 0x00, 0xF2, 
  0xF1, 0xE4, 0x22, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x03, 0x00, 
  0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x23, 0x00, 0x00, 0x00, 0xF1, 
  0xE1, 0x04, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x24, 0x00, 
  0x00, 0x00, 0xF1, 0xE1, 0x05, 0x00, 0x00, 0x00, 0xF2, 0xF1, 
  0xE4, 0x25, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x06, 0x00, 0x00, 
  0x00, 0xF2, 0xF1, 0xE4, 0x26, 0x00, 0x00, 0x00, 0xF1, 0xE1, 
  0x07, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x27, 0x00, 0x00, 
  0x00, 0xF1, 0xE1, 0x08, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 
  0x28, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x09, 0x00, 0x00, 0x00, 
  0xF2, 0xF1, 0xE4, 0x29, 0x00, 0x00, 0x00, 0xF1, 0xE1, 0x0A, 
  0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x2A, 0x00, 0x00, 0x00, 
  0xF1, 0xE1, 0x0B, 0x00, 0x00, 0x00, 0xF2, 0xF1, 0xE4, 0x2B, 
  0x00, 0x00, 0x00, 0xF9, 0xF4, 0x00, 0x00, 0x00
`}`;
```

对应前面分析的指令集，先将opcode分组，

```
//每一排代表一个指令及其操作数
0xF5, 
0xF1, 0xE5, 0x97, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x00, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x20, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x01, 0x00, 0x00, 0x00,
0xF2, 
0xF1, 0xE4, 0x21, 0x00, 0x00, 0x00,
0xF1, 0xE1, 0x02, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x22, 0x00, 0x00, 0x00,
0xF1, 0xE1, 0x03, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x23, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x04, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x24, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x05, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x25, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x06, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x26, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x07, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x27, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x08, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x28, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x09, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x29, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x0A, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x2A, 0x00, 0x00, 0x00, 
0xF1, 0xE1, 0x0B, 0x00, 0x00, 0x00, 
0xF2, 
0xF1, 0xE4, 0x2B, 0x00, 0x00, 0x00, 
0xF9, 
0xF4, 0x00, 0x00, 0x00//退出
```

可以写出大致流程

```
//用伪代码表示虚拟机功能流程

    strcpy &amp;stack[0],str2

    MOV R2,0x97

    MOV R1,stack[0]
    R1 = ~(r2 ^ r1) ^ 0x12
       MOV stack[0x20],R1

    MOV R1,stack[1]
    R1 = ~(r2 ^ r1) ^ 0x12
       MOV stack[0x21],R1

    MOV R1,stack[2]
    R1 = ~(r2 ^ r1) ^ 0x12
       MOV stack[0x22],R1

    MOV R1,stack[3]
    R1 = ~(r2 ^ r1) ^ 0x12
       MOV stack[0x23],R1        

    …………

    MOV R1,stack[0xb]
    R1 = ~(r2 ^ r1) ^ 0x12
       MOV stack[0x2b],R1

    strcpy str2,&amp;stack[0x2b]        

//至此，这个虚拟机的功能大致完成
```

所以这个虚拟机的大致流程就是，将输入的之字符串，进行一个`~(flag ^ 0x97) ^ 0x12`这样的简易加密

主函数中有`strcmp`对加密的数据进行比较

```
//strcmp的比较数据
unsigned char ida_chars[] =
`{`
  0x1C, 0x16, 0x1B, 0x1D, 0x01, 0x3F, 0x4E, 0x09, 0x03, 0x2C, 
  0x17, 0x07
`}`;
```

最后直接写脚本即可

### <a class="reference-link" name="5%E3%80%81%E9%80%86%E5%90%91%E8%84%9A%E6%9C%AC"></a>5、逆向脚本

```
//C语言
#include&lt;stdio.h&gt;
int main()
`{`
    char k[20] = `{`  0x1C, 0x16, 0x1B, 0x1D, 0x01, 0x3F, 0x4E, 0x09, 0x03, 0x2C, 0x17, 0x07`}`;
    char flag[20]=`{`0`}`;
    int i;
    for(i=0;k[i];i++)`{`
        flag[i] = (~(k[i]^0x12))^0x97;
    `}`
    for( i=0;flag[i];i++)`{`
        printf("%c",flag[i]);
    `}`
    putchar('\n');
    return 0;
`}`
```

[<img class="alignnone size-full wp-image-252718 aligncenter" alt="" width="671" height="207" data-original="https://p5.ssl.qhimg.com/t01c8f6fc0c8dc1947f.png">](https://p5.ssl.qhimg.com/t01c8f6fc0c8dc1947f.png)

flag`{`E4syVm`}`
