> 原文链接: https://www.anquanke.com//post/id/227940 


# Linux流程分析——从开机那一刻开始


                                阅读量   
                                **127942**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0xax，文章来源：0xax.gitbooks.io
                                <br>原文地址：[https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html](https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01bd5a70de59495861.png)](https://p3.ssl.qhimg.com/t01bd5a70de59495861.png)



## 在按下电源键后 ,发生了什么

在按下电源键后,电脑开始工作,主板发送信号给电源供应设备,在接受信号后,电源为电脑提供合适的电力.一旦主板得到了成功启动电源的信号后,启动cpu ,cpu清除在寄存器上的残留数据,并且重新将寄存器设置为预存的值.

80386 以及以后的cpu中预设寄存器值

```
IP          0xfff0
CS selector 0xf000
CS base     0xffff0000
```

处理器开始以实模式运行,下面了解一下在实模式运行时的内存段;

实模式在所有的x86体系下的处理器都有支持.包括从8086cpu一直到现代的intel64位cpu.8086处理器有20位地址总线,这意味着它能在0-0xFFFF (或者说1mb)的地址空间内工作.但是他只有16位的寄存器 这意味着只有`2^16 - 1` or `0xffff` (64 kilobytes)的寻址能力

内存分段技术使地址空间全部可用,所有的内存被分割成固定大小(64kb)的片段,因为我们在16位的寄存器下无法直接定位更大的空间.

一个地址由两部分组成: 一个有着基地址的段选择器,和对于该地址的偏移.在实模式下,相关的基地址由段选择器左移4位得到.因此我们的物理地址以如下方法得到

```
PhysicalAddress = Segment Selector &lt;&lt; 4 + Offset
```

例如 `CS:IP` is `0x2000:0x0010` ,他的物理地址为

```
0x2000&lt;&lt;4 + 0x0010 = 0x20010
```

但是 ,如果选择器和偏移均取最大值 0xffff:0xffff 相应的值

```
(0xffff &lt;&lt; 4) + 0xffff = 0x10ffef
```

但由于实模式下只有1mb可用, 0x10ffef变为0x00ffef 并且使[A_20](https://zh.wikipedia.org/wiki/A20%E6%80%BB%E7%BA%BF)总线不可用

了解了一点关于实模式和它的内存机制后,下面继续讨论重新设置后的寄存器

cs寄存器由两部分组成,可视的段选择器和隐式的基地址,实模式下,基地址**通常**由16位选择器左移4位来构造20bit的基地址

然而,当在硬件重置段选择器时,cs寄存器被设置为0xf000 ,基地址被加载为0xffff0000,处理器在cs寄存器改变之前一直使用该地址

开始地址由基地址和eip寄存器值相加取得

```
0xffff0000 + 0xfff0 = 0xfffffff0
```

即0xfffffff0 ,这个地址被叫做重置向量( [reset vector](https://en.wikipedia.org/wiki/Reset_vector)),这是cpu在重置后寻找到第一条执行指令的地址

它包括了(jmp)跳转指令,通常指向BIOS入口地址,例如 如果在 [coreboot](https://www.coreboot.org/)源代码里看(`src/cpu/x86/16bit/reset16.inc`)

```
.section ".reset", "ax", %progbits
    .code16
.globl    _start
_start:
    .byte  0xe9
    .int   _start16bit - ( . + 2 )
    ...
```

这里我们看到jmp的机器码0xe9以及它的目的地址 `_start16bit - ( . + 2 )`

也能看到reset段是16byte 而且被编译成从0xfffffff0处开始

```
SECTIONS `{`
    /* Trigger an error if I have an unuseable start address */
    _bogus = ASSERT(_start16bit &gt;= 0xffff0000, "_start16bit too low. Please report.");
    _ROMTOP = 0xfffffff0;
    . = _ROMTOP;
    .reset . : `{`
        *(.reset);
        . = 15;
        BYTE(0x00);
    `}`
`}`
```

BIOS启动,在初始化以及检查硬件后,BIOS需要一个可启动的设备,BIOS设置里储存了引导顺序,这给顺序控制BIOS应该从哪一个设备开始引导.

BIOS尝试从硬盘里开始引导时,尝试寻找引导向量(boot sector).在存在MBR(主引导记录)的硬盘分区里,每一个部分由512byte组成,引导向量储存在头446byte部分

最后由0x55和0xaa2byte结束 ,这两位指定了该设备是可启动的.一旦BIOS找到了第一个引导向量,BIOS复制它到0x7c00,跳转到那里然后开始执行它.

例:

```
;
; Note: this example is written in Intel Assembly syntax
;
[BITS 16]

boot:
    mov al, '!'
    mov ah, 0x0e
    mov bh, 0x00
    mov bl, 0x07

    int 0x10
    jmp $

times 510-($-$$) db 0

db 0x55
db 0xaa
```

执行实验

```
nasm -f bin boot.nasm &amp;&amp; qemu-system-x86_64 boot
```

这会引导qemu使用boot作为磁盘映像来启动,由于文件通过汇编编写并且满足引导向量的格式 qemu会将该二进制文件当作磁盘的主引导记录(MBR)区域

注意:当提供 boot binary image 给qemu时,设定[org 0x7c00]就不是必须的了

实验结果如下

[![](https://p2.ssl.qhimg.com/t01b882804a07658e7c.png)](https://p2.ssl.qhimg.com/t01b882804a07658e7c.png)

在此次测试中 ,我们看到代码在实模式下被执行,开始后,通过执行0x10号中断,打印出`!` ,剩下的部分由0填充,并以0xaa,0x55 结束

真正实模式下的代码用于继续启动流程,和储存分区表.从这里开始BIOS把控制流交给启动器

注意: 上面提到过的 ,实模式下的cpu计算地址的方法如下;

```
PhysicalAddress = Segment Selector * 16 + Offset
```

当取最大值时 物理地址将会变为

```
(0xffff * 16) + 0xffff =0x10ffef
```

0x10ffef = 1mb +64kb -16b -1

然而8086处理器(第一代使用实模式) , 只有20位地址总线,这意味着只有1mb空间可用.

实模式下,一般的内存空间如下

```
0x00000000 - 0x000003FF - Real Mode Interrupt Vector Table
0x00000400 - 0x000004FF - BIOS Data Area
0x00000500 - 0x00007BFF - Unused
0x00007C00 - 0x00007DFF - Our Bootloader
0x00007E00 - 0x0009FFFF - Unused
0x000A0000 - 0x000BFFFF - Video RAM (VRAM) Memory
0x000B0000 - 0x000B7777 - Monochrome Video Memory
0x000B8000 - 0x000BFFFF - Color Video Memory
0x000C0000 - 0x000C7FFF - Video ROM BIOS
0x000C8000 - 0x000EFFFF - BIOS Shadow Area
0x000F0000 - 0x000FFFFF - System BIOS
```

本文的开头,已经说明第一条被执行的代码在`0xffffff0`处,这比处理器能达到的界限大很多,那么cpu如何在实模式下访问这个地址? 答案在 [coreboot](https://www.coreboot.org/Developer_Manual/Memory_map)文件里

```
0xFFFE_0000 - 0xFFFF_FFFF: 128 kilobyte ROM mapped into address space
```

当执行开始时,BIOS在ROM而不是RAM里



## 引导装载程序(bootloader)

有多种可用来启动linux的引导装载程序,例如[GRUB 2](https://www.gnu.org/software/grub/)和[syslinux](http://www.syslinux.org/wiki/index.php/The_Syslinux_Project) . linux内核里有一个引导协议,[Boot protocol](https://github.com/torvalds/linux/blob/v4.16/Documentation/x86/boot.txt)

从BIOS将控制权转移给引导装载程序后继续,从boot.img开始执行,由于内存空间的限制,这里代码很简单,包括一个指向GRUB2核心文件的指针.核心文件(core image)从diskboot.img开始,通常存储在第一个分区之前第一个扇区之后未使用的空间中.上面的代码加载剩下的核心文件,包括GRUB2的内核以及文件系统的驱动到内存中.之后执行`grub_main`函数

`grub_main`函数进行初始化控制台,为模块的加载获取基地址,设置root device 加载grub配置文件,加载模块等操作

在运行的最后,`grub_main`函数将grub改为normal模式.`grub_normal_execute`函数完成最后的最后的准备,并显示出一个操作系统的选择菜单,在选择一个grub入口后, `grub_menu_execute_entry`函数启动,执行grub`boot`命令,启动所选的操作系统.

引导装载程序 读取并填充某些内核启动的数据,这些数据储存在从内核启动代码偏移0x01f1处.可以通过链接脚本来证实偏移的值,内核头开始于

```
.globl hdr
hdr:
    setup_sects: .byte 0
    root_flags:  .word ROOT_RDONLY
    syssize:     .long 0
    ram_size:    .word 0
    vid_mode:    .word SVGA_MODE
    root_dev:    .word 0
    boot_flag:   .word 0xAA55
```

引导程序必须填充这个和剩下的头部(在协议中仅被标注为可写).这些值来自于命令行或者在引导过程中由计算得到.(在这里不会复习内核重置头的全部内容,但是会在讲内核会如何使用他们时详细谈一谈,你可以在[Boot protocol](https://github.com/torvalds/linux/blob/v4.16/Documentation/x86/boot.txt)里找到全部的详细解释)

在加载内核后,内存会被映射成如下

```
| Protected-mode kernel  |
100000   +------------------------+
         | I/O memory hole        |
0A0000   +------------------------+
         | Reserved for BIOS      | Leave as much as possible unused
         ~                        ~
         | Command line           | (Can also be below the X+10000 mark)
X+10000  +------------------------+
         | Stack/heap             | For use by the kernel real-mode code.
X+08000  +------------------------+
         | Kernel setup           | The kernel real-mode code.
         | Kernel boot sector     | The kernel legacy boot sector.
       X +------------------------+
         | Boot loader            | &lt;- Boot sector entry point 0x7C00
001000   +------------------------+
         | Reserved for MBR/BIOS  |
000800   +------------------------+
         | Typically used by MBR  |
000600   +------------------------+
         | BIOS use only          |
000000   +------------------------+
```

当引导程序将控制权转向内核 从(x+sizeof(Kernel boot sector) + 1)处开始<br>
x是内核被装载时的地址

[![](https://p3.ssl.qhimg.com/t01d371f34da9195294.png)](https://p3.ssl.qhimg.com/t01d371f34da9195294.png)

引导器装载linux内核到内存中,接下来进入内核设置代码



## 内核设置的开始

终于 ,我们在技术上到达了内核阶段,但是内核现在还没有开始运行.内核的设置部分需要先配置一些例如解压器,与内存管理相关的配置等.

之后 内核设置部分解压真正内核,跳转到那里. 这一段相关代码在 [arch/x86/boot/header.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/header.S) 的_start段中

第一眼看上去可能有些怪异 ,因为在这段代码之前还有许多指令 . 很久之前,linux有自己的引导器.然而现在 如果使用以下命令

```
qemu-system-x86_64 vmlinuz-3.18-generic
```

你会看见

[![](https://p3.ssl.qhimg.com/t0171feeebd395cabb0.png)](https://p3.ssl.qhimg.com/t0171feeebd395cabb0.png)

事实上,`header.s`文件以魔数MZ开头,

```
#ifdef CONFIG_EFI_STUB
# "MZ", MS-DOS header
.byte 0x4d
.byte 0x5a
#endif
...
...
...
pe_header:
    .ascii "PE"
    .word 0
```

他需要这些去加载操作系统,通过[UEFI](https://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface)的帮助,以后再深入解释这一部分

真正的内核设置入口点是

```
// header.S line 292
.globl _start
_start:
```

引导程序(GRUB 2或者其他)知道这个入口点(在从’MZ’偏移0x200处)并且直接跳转到这里,尽管header.s从.bstext段开始,该段打印出一段错误信息

```
//
// arch/x86/boot/setup.ld
//
. = 0;                    // current position
.bstext : `{` *(.bstext) `}`  // put .bstext section to position 0
.bsdata : `{` *(.bsdata) `}`
```

内核设置入口点内容

```
// header.S line 292
.globl _start
_start:
.byte  0xeb
    .byte  start_of_setup-1f
1:
    //
    // rest of the header
    //
```

这里有jmp的机器码(0xeb),跳转到 `start_of_setup-1f` .在符号`NF`,如`2f` .代表本地标签`2:`,

在这里,它是标签`1:`,在跳转之后我们看见`.entrytext`段,在`start_of_setup`标签开始处.

这是实际运行的第一段语句(当然,除了提前的跳转语句).在内核设置部分从引导器手中接过控制流后,第一个`jmp`语句定位在从内核实模式开始处,偏移为`0x200`的地方.在最初的512byte后.下面的这一段代码能在Linux内核启动协议 和GRUB 2源代码里看到

```
segment = grub_linux_real_target &gt;&gt; 4;
state.gs = state.fs = state.es = state.ds = state.ss = segment;
state.cs = segment + 0x20;
```

在这里 ,内核被加载在物理地址`0x10000`处,这意味着段寄存器的值应该是下面的状况在内核启动设置后

```
gs = fs = es = ds = ss = 0x1000
cs = 0x1020
```

在跳转到`start_of_setup`后,内核需要做下面的几件事
- 确定好所有的段寄存器的值相等
- 如果需要的话,设定好一个正确的栈空间
- 设立bss段
<li>跳转到c代码[arch/x86/boot/main.c](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/main.c)
</li>
下面看看这些是如何实现的



## 校准段寄存器

首先,内核确保 `ds`和`es`段寄存器指向同样的地址,然后用`cld`让flag复位

```
movw    %ds, %ax
movw    %ax, %es
cld
```

正如前面所写,grub 2 默认加载内核代码到`0x10000` . 但`cs`值为`0x1020`因为并不从文件的开始处执行而是跳转到这里

```
_start:
    .byte 0xeb
    .byte start_of_setup-1f
```

从 `4d 5a`的512byte偏移,我们需要校准`cs`为`0x1000`,其他段寄存器也是这样.然后我们设置栈.

```
pushw   %ds
    pushw   $6f
    lretw
```

将`ds`寄存器的值压入栈中.在lable`6`后.执行`lretw`.当`lretw`执行后,加载lable`6`

进入 [instruction pointer](https://en.wikipedia.org/wiki/Program_counter)指令指针寄存器.加载`cs`为`ds`的值,于是,`cs`和`ds`有相同的值



## 栈设置

几乎所有的设置代码都是为了C语言在实模式下的执行环境服务,下一步是检查`ss`寄存器的值 ,如果`ss`值出现错误,重新设置.

```
movw    %ss, %dx
    cmpw    %ax, %dx
    movw    %sp, %dx
    je      2f
```

这里会出现3个不同场景
<li>
`ss`有合法值为`0x1000` 像所有其他寄存器一样(除了`cs`)</li>
<li>
`ss`不合法 且`CAN_USE_HEAP`flag位被设置</li>
<li>
`ss`不合法 且`CAN_USE_HEAP`flag位未被设置</li>
依次分析三种情况
<li>
`ss`有合法值为`0x1000` 此时,跳转到label2:</li>
```
2:  andw    $~3, %dx
    jnz     3f
    movw    $0xfffc, %dx
3:  movw    %ax, %ss
    movzwl  %dx, %esp
    sti
```

这里设定`dx`的偏移(被引导器设定`sp`的值)为4byte 检查它是否为0.如果是,设置`dx`为`0xfffc`(在64kb的段中最后4byte对齐).如果不是,则继续使用`sp`的值

然后,将`ax`的值放入`ss`中,现在我们有了正确的栈空间

[![](https://p4.ssl.qhimg.com/t0137c56580327ea8b8.png)](https://p4.ssl.qhimg.com/t0137c56580327ea8b8.png)
- 第二种情况 (`ss`!=`ds`),首先将setup代码段的最后地址放入`dx`中.检查`loadflags`头文件来确定我们能否使用堆空间.`loadflag`是一张位图定义如下:
```
#define boot     (1&lt;&lt;0)
#define QUIET_FLAG      (1&lt;&lt;5)
#define KEEP_SEGMENTS   (1&lt;&lt;6)
#define CAN_USE_HEAP    (1&lt;&lt;7)
```

正如在引导协议里看到的

```
Field name: loadflags

  This field is a bitmask.

  Bit 7 (write): CAN_USE_HEAP
    Set this bit to 1 to indicate that the value entered in the
    heap_end_ptr is valid.  If this field is clear, some setup code
    functionality will be disabled.
```

如果`CAN_USE_HEAP`位被设定,将 `heap_end_addr`放入`ds`(指向`_end`)

添加`STACK_SIZE`(最小值为1024byte)之后,跳转到label2,创建正确的栈空间

[![](https://p0.ssl.qhimg.com/t01c5d752b19c3c5628.png)](https://p0.ssl.qhimg.com/t01c5d752b19c3c5628.png)
- 当`CAN_USE_HEAP`位没有被设定,我们只用最小的栈空间 ,从`_end`到`_end+STACK_SIZE`:
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01998b569959cb7512.png)



## BSS段

为进入c主函数做的最后两步准备是建立BSS段,和检查’magic’标志位

首先,标志位检查

```
cmpl    $0x5a5aaa55, setup_sig
    jne     setup_bad
```

这是一个对比,简单地将`setup_sig`和magic number `0x5a5aaa55`作比较,如果不同,报告一个致命的错误.

如果魔数匹配正确,则确定我们有了正确的段寄存器和栈.我们只需要设置BSS段即可.

BSS段被用于储存静态变量,未初始化的数据.LInux通过下面的方式小心地保证该区域全为0

```
movw    $__bss_start, %di
    movw    $_end+3, %cx
    xorl    %eax, %eax
    subw    %di, %cx
    shrw    $2, %cx
    rep; stosl
```

首先,`_bss_start`地址存入`di`,`_end+3`(+3 – 4byte偏移)存入`cx` ,eax寄存器被清零 ,计算bss段大小(`cx-di`)并放入`cx`,`cx`被分为4段, `stosl`被循环调用

将 eax值(即为0)放入`di`指向地址.最终从`__bss_start`到`_end`这段区域全部清零

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e157a06803e3943c.png)



## 跳转到main函数

```
calll main
```

main函数在[arch/x86/boot/main.c](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/main.c).在下一部分详细讲解



## 链接

```
本文为对英文文章的翻译,加上自己的部分理解,如有不恰当地方,恳求指正。
```
- [Intel 80386 programmer’s reference manual 1986](http://css.csail.mit.edu/6.858/2014/readings/i386.pdf)
- [Minimal Boot Loader for Intel® Architecture](https://www.cs.cmu.edu/~410/doc/minimal_boot.pdf)
- [Minimal Boot Loader in Assembler with comments](https://github.com/Stefan20162016/linux-insides-code/blob/master/bootloader.asm)
- [8086](https://en.wikipedia.org/wiki/Intel_8086)
- [80386](https://en.wikipedia.org/wiki/Intel_80386)
- [Reset vector](https://en.wikipedia.org/wiki/Reset_vector)
- [Real mode](https://en.wikipedia.org/wiki/Real_mode)
- [Linux kernel boot protocol](https://www.kernel.org/doc/Documentation/x86/boot.txt)
- [coreboot developer manual](https://www.coreboot.org/Developer_Manual)
- [Ralf Brown’s Interrupt List](http://www.ctyme.com/intr/int.htm)
- [Power supply](https://en.wikipedia.org/wiki/Power_supply)
- [Power good signal](https://en.wikipedia.org/wiki/Power_good_signal)