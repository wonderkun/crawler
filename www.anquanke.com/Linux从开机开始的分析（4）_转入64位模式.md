> 原文链接: https://www.anquanke.com//post/id/232201 


# Linux从开机开始的分析（4）：转入64位模式


                                阅读量   
                                **221720**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0xax，文章来源：0xax.gitbooks.io
                                <br>原文地址：[https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html](https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01bd5a70de59495861.png)](https://p3.ssl.qhimg.com/t01bd5a70de59495861.png)



## 向64位的转换

内核启动程序第四阶段,我们将看到在保护模式下进行的每一步,例如,检查cpu是否支持长模式和sse.初始化页表,在最后将cpu转换为长模式处理

前一段中我们停留在跳转到`32位`入口点处[arch/x86/boot/pmjump.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/pmjump.S):

```
jmpl    *%eax
```

eax中储存着入口点地址

[linux kernel x86 boot protocol](https://www.kernel.org/doc/Documentation/x86/boot.txt):

```
When using bzImage, the protected-mode kernel was relocated to 0x100000
```

如下,`32位`入口点时寄存器值

```
eax            0x100000    1048576
ecx            0x0        0
edx            0x0        0
ebx            0x0        0
esp            0x1ff5c    0x1ff5c
ebp            0x0        0x0
esi            0x14470    83056
edi            0x0        0
eip            0x100000    0x100000
eflags         0x46        [ PF ZF ]
cs             0x10    16
ss             0x18    24
ds             0x18    24
es             0x18    24
fs             0x18    24
gs             0x18    24
```

cs寄存器值为0x10,(在前一部分提到过,这是GDT表下标为2的地方),eip值为0x100000,包括代码段在内的所有基址都是0

所以内核加载的物理地址明显是0x100000 或者说是0:0x100000



## 32位入口点

这一部分定义在[arch/x86/boot/compressed/head_64.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_64.S) 中

```
__HEAD
    .code32
ENTRY(startup_32)
....
....
....
ENDPROC(startup_32)
```

首先,为什么该目录名是`compressed`,? `bzimage`是一个gzipped打包的文件

由`vmlinux``header`和`kernel setup code`组成.在前面我们已经看过`kernel set code`这些代码的主要目的就是为进入长模式做准备,进入长模式后解压内核文件.我们将在这一部分逐步展开内核解压的部分.

我们在`arch/x86/boot/compressed`目录下会找到以下两个文件
- [head_32.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_32.S)
- [head_64.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_64.S)
在这里我们只讨论`head_64.S`;

首先看一看`Makefile`文件

```
vmlinux-objs-y := $(obj)/vmlinux.lds $(obj)/head_$(BITS).o $(obj)/misc.o \
    $(obj)/string.o $(obj)/cmdline.o \
    $(obj)/piggy.o $(obj)/cpuflags.o
```

`$(obj)/head_$(BITS).o`.这意味着我们需要通过`$(bits)`选择哪一种文件来设定.而`$(BITS)`的值在 [arch/x86/Makefile](https://github.com/torvalds/linux/blob/16f73eb02d7e1765ccab3d2018e0bd98eb93d973/arch/x86/Makefile)中通过内核选项被定义

```
ifeq ($(CONFIG_X86_32),y)
        BITS := 32
        ...
        ...
else
        BITS := 64
        ...
        ...
endif
```

现在我们知道了从哪里开始,然后继续.



## 重新加载段(如果需要)

像上面所说的,我们在 [arch/x86/boot/compressed/head_64.S](https://github.com/torvalds/linux/blob/16f73eb02d7e1765ccab3d2018e0bd98eb93d973/arch/x86/boot/compressed/head_64.S) 开始,首先看到一个特殊的定义在`startup_32`函数前.

```
__HEAD
    .code32
ENTRY(startup_32)
```

`__HEAD`是一个宏 ,展开后如下

```
#define __HEAD        .section    ".head.text","ax"
```

`.head.text`是该段的名称,`ax`是标记位,这里的标记代表该段是可执行的.这里在链接器脚本中

```
SECTIONS
`{`
    . = 0;
    .head.text : `{`
        _head = . ;
        HEAD_TEXT
        _ehead = . ;
     `}`
     ...
     ...
     ...
`}`
```

如果对`GNU LD`链接器脚本并不熟悉,可以参考[documentation](https://sourceware.org/binutils/docs/ld/Scripts.html#Scripts).简而言之,`.`是一个特殊的链接器脚本变量,位置计数器.这个值标志着跟这一个段相关的偏移.我们将这个值设置为0,意思是我们的代码被链接从0偏移处执行.这一点被表述为如下

```
Be careful parts of head_64.S assume startup_32 is at address 0.
```

现在我们找到了中心,我们看看`startup_32`函数的内容

在`startup_32`函数的开头,我们看到`cld`指令,清除[flags](https://en.wikipedia.org/wiki/FLAGS_register)寄存器的`DF`位.当方向位清除后,所有的字符处理指令`stos``scas`都会增加esi和edi寄存器.我们需要先清除方向位,因为接下来我们会使用字符操作来运行一些例如为页表清除空间的操作

在清除`DF`位后,下一步是检查`Keep_SEGMENTS`位,位于`loadflag`kernel setup header. 在第一段中已经讲述过这一块的内容. 检查`CAN_USE_HEAP`标志位来确定使用堆的能力,.然后我们需要检查`KEEP_SEGMENT`标志位,在引导协议的文档里描述如下:

```
Bit 6 (write): KEEP_SEGMENTS
  Protocol: 2.07+
  - If 0, reload the segment registers in the 32bit entry point.
  - If 1, do not reload the segment registers in the 32bit entry point.
    Assume that %cs %ds %ss %es are all set to flat segments with
        a base of 0 (or the equivalent for their environment).
```

如果`KEEP_SENGMENT`位没有被设置,我们需要设置`ds``ss`和`es`段寄存器为数据段的下标,基址为0;然后

```
testb $KEEP_SEGMENTS, BP_loadflags(%esi)
    jnz 1f

    cli
    movl    $(__BOOT_DS), %eax
    movl    %eax, %ds
    movl    %eax, %es
    movl    %eax, %ss
```

`__BOOT_DS`值为0x18(全局描述符里数据段的下标),如果`KEEP_SEGMENT`被设置,跳转到最近的`1f`标签,如果没有,则通过`__BOOT_DS`更新段寄存器.这一点很简单,但是仍有一些问题:我们已经更新过这些寄存器在前一部分(具体在转换到保护模式之前[arch/x86/boot/pmjump.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/pmjump.S))为什么我们仍需要再次关心这些段寄存器的值.

原因是linux内核也有32位的引导协议,如果引导器使用这个协议去加载内核,所有在`startup_32`之前的代码都会被忽略.这种情况下`startup_32`会成为第一个入口点.此时我们无法确定段寄存器是否在一个确定的值

在确定`KEEP_SEGMENT`位和寄存器都处于正确的状态,下一步是计算内核编译运行的地址和加载进入的地址之间的差别.在`setup.ld.s`里`.head.text`我们知道`.=0`.这意味着代码编译运行在`0`处.`obj-dump`的输出里可以看出

```
arch/x86/boot/compressed/vmlinux:     file format elf64-x86-64


Disassembly of section .head.text:

0000000000000000 &lt;startup_32&gt;:
   0:   fc                      cld
   1:   f6 86 11 02 00 00 40    testb  $0x40,0x211(%rsi)

```

这里看到`startup_32`的地址为`0` 但实际上并非如此,我们需要知道实际地址在哪,

这些在长模式下做起来是很简单的.因为他提供了`rip`,但现在我们在保护模式下,我们使用另外一个方式来寻找地址.我们需要定义一个标签,调用跳转到那里 将栈顶的值pop到一个寄存器中.

```
call label
label: pop %reg
```

之后,寄存器保存`label`的地址.

接下来是用来寻找地址,通过以下代码

```
leal    (BP_scratch+4)(%esi), %esp
        call    1f
1:      popl    %ebp
        subl    $1b, %ebp
```

esi寄存器包含了`boot params`的地址,该结构体的`0x1e4`偏移处是一个为call指令准备的一个暂时的栈区域,我们设置esp为这个栈地址+4的地方,正如描述的那样,他成为了临时的栈空间,同时栈自顶向下增长在x86架构下.因此我们的栈指针指向临时栈空间的顶部,然后我们调用`1f`处标签,将栈顶放入`ebp`中,由于call将返回地址存在栈顶,我们现在有了label1处的地址,通过这个地址,很容易计算出`startup_32`的地址.我们只需要将label1地址减去对应偏移.

```
startup_32 (0x0)     +-----------------------+
                     |                       |
                     |                       |
                     |                       |
                     |                       |
                     |                       |
                     |                       |
                     |                       |
                     |                       |
1f (0x0 + 1f offset) +-----------------------+ %ebp - real physical address
                     |                       |
                     |                       |
                     +-----------------------+
```

在内核引导协议中说保护模式内核的基址为`0x100000`,我们可以用gdb来验证.

如果这是正确的,我们在ebp寄存器里看到的值就应该是`0x100021`

```
$ gdb
(gdb)$ target remote :1234
Remote debugging using :1234
0x0000fff0 in ?? ()
(gdb)$ br *0x100022
Breakpoint 1 at 0x100022
(gdb)$ c
Continuing.

Breakpoint 1, 0x00100022 in ?? ()
(gdb)$ i r
eax            0x18    0x18
ecx            0x0    0x0
edx            0x0    0x0
ebx            0x0    0x0
esp            0x144a8    0x144a8
ebp            0x100021    0x100021
esi            0x142c0    0x142c0
edi            0x0    0x0
eip            0x100022    0x100022
eflags         0x46    [ PF ZF ]
cs             0x10    0x10
ss             0x18    0x18
ds             0x18    0x18
es             0x18    0x18
fs             0x18    0x18
gs             0x18    0x18
```

下一条执行语句 `subl $1b, %ebp`,我们将看到

```
(gdb) nexti
...
...
...
ebp            0x100000    0x100000
...
...
...
```

ok,我们确定了`startup_32`的地址是`0x100000`.在知道了地址后,准备像长模式的转变.接下来开始设置栈,并验证cpu支持长模式和sse.



## 设置栈以及cpu验证

在知道`startup_32`实际地址前我们无法设置栈空间,如果把栈想象为一个数组,栈指针esp必须指向它的尾部,当然,我们也可以在自己的代码里设置一个数组,但是我们必须首先知道实际的地址来正确的配置栈指针.

```
movl    $boot_stack_end, %eax
    addl    %ebp, %eax
    movl    %eax, %esp
```

`boot_stack_end`也是定义在[arch/x86/boot/compressed/head_64.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_64.S) 里,位于.bss段内

```
.bss
    .balign 4
boot_heap:
    .fill BOOT_HEAP_SIZE, 1, 0
boot_stack:
    .fill BOOT_STACK_SIZE, 1, 0
boot_stack_end:
```

首先将`boot_stack_end`值放入eax寄存器中,在链接后eax寄存器储存了`boot_stack_end`的值,即`0x0+boot_stack_end`为了获取真实地址,将`startup_32`的真实地址加上.就是`boot_stack_end`,将esp调整为`boot_stack_end`.栈指针指向正确的栈顶

设立好栈空间后,接下来是cpu的检查,由于我们要转向长模式cpu必须支持长模式和sse,这些通过`verify_cpu`来执行

```
call    verify_cpu
    testl    %eax, %eax
    jnz    no_longmode
```

该函数定义在[arch/x86/kernel/verify_cpu.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/kernel/verify_cpu.S) 而且包含了很多对于`cpuid`的调用.这个指令用来获取关于处理器的信息.在这里,他检查长模式和sse支持情况以及设置eax寄存器为0代表成功,1代表失败.

如果eax不是0,跳转到`no_longmode`,当没有硬件中断时,通过`hlt`语句终止cpu,

```
no_longmode:
1:
    hlt
    jmp     1b
```

如果是0,则一切正常继续



## 计算重定位后的地址

下一步是为解压缩计算重定位后地址.首先我们需要知道对于内核来说可重定位意味着什么,我们已经知道了linux内核中32位地址的入口基址是0x100000,但这是一个32位的入口点,默认的基址在`CONFIG_PHYSICAL_START`内核设置选项中被设定,这个值默认是0x1000000 ,但主要的问题是如果内核崩溃,内核开发人员必须有一个急救内核用来使用`kdump`.

内核提供了一个特殊的选项来解决这个问题:`CONGFIG_RELOCATABLE`,在内核文档中这样描述

```
This builds a kernel image that retains relocation information
so it can be loaded someplace besides the default 1MB.

Note: If CONFIG_RELOCATABLE=y, then the kernel runs from the address
it has been loaded at and the compile time physical address
(CONFIG_PHYSICAL_START) is used as the minimum location.
```



## 重新加载段

在前文中看到

```
#define __HEAD        .section    ".head.text","ax"
```

正常情况下,这意味着带有这个选项的内核可以从不同的地址开始引导.实际上,在编译,这些作为位置独立的代码,在makefile文件中编译选项中`-fpic`

```
KBUILD_CFLAGS += -fno-strict-aliasing -fPIC
```

当我们使用这些代码时,地址会被填充.这也是为什么我们必须要取得`startup_32`物理地址的原因,我们现在的目标是为解压器计算出在内核中重定位后的地址.,计算这个地址依赖于`CONFIG_RELOCATABLE`内核选项

```
#ifdef CONFIG_RELOCATABLE
    movl    %ebp, %ebx
    movl    BP_kernel_alignment(%esi), %eax
    decl    %eax
    addl    %eax, %ebx
    notl    %eax
    andl    %eax, %ebx
    cmpl    $LOAD_PHYSICAL_ADDR, %ebx
    jge    1f
#endif
    movl    $LOAD_PHYSICAL_ADDR, %ebx
```

`ebp`寄存器的值是`startup_32`的地址,如果`CONFIG_RELOCATABLE`设置了,我们将`ebp`的值放入`ebx`,将它按2mb对齐,然后将结果与`LOAD_PHYSICAL_ADDR`宏比较,

```
#define LOAD_PHYSICAL_ADDR ((CONFIG_PHYSICAL_START \
                + (CONFIG_PHYSICAL_ALIGN - 1)) \
                &amp; ~(CONFIG_PHYSICAL_ALIGN - 1))
```

该宏被拓展为`CONFIG_PHYSICAL_ALIGN` 对齐后的值,代表内核地址被加载的地址.

在以上的计算之后,`ebp`会存有内核加载的地址,`ebx`是解压内核重定位后的地址,压缩的内核镜像需要移动到解压缓冲区,

```
1:
    movl    BP_init_size(%esi), %eax
    subl    $_end, %eax
    addl    %eax, %ebx
```

#### <a class="reference-link" name="%E5%87%86%E5%A4%87%E8%BD%AC%E5%85%A5%E9%95%BF%E6%A8%A1%E5%BC%8F"></a>准备转入长模式

获取到重定位后的解压地址后,我们需要在能进入64位做最后一步.

首先,将全局描述符表更新到64位.因为可重定位的内核可以在512GB下的任何地址运行.

```
addl    %ebp, gdt+2(%ebp)
    lgdt    gdt(%ebp)
```

这里,我们矫正GDT表的基地址为我们实际上加载内核的地址.通过`lgdt`加载全局描述符表

为了了解`gdt`偏移的魔数,我们看一看它的定义

```
.data
gdt64:
    .word    gdt_end - gdt
    .long    0
    .word    0
    .quad   0
gdt:
    .word    gdt_end - gdt
    .long    gdt
    .word    0
    .quad    0x00cf9a000000ffff    /* __KERNEL32_CS */
    .quad    0x00af9a000000ffff    /* __KERNEL_CS */
    .quad    0x00cf92000000ffff    /* __KERNEL_DS */
    .quad    0x0080890000000000    /* TS descriptor */
    .quad   0x0000000000000000    /* TS continued */
gdt_end:
```

`gdt`位于`.data`,包含了五个描述符,第一个是`32-bit`描述符为内核代码段

内核`64-bit`代码段,内核数据段,两个任务描述符

我们在之前已经加载了`Global Descriptor Table`,现在我们会再做一次基本一样的事情.不同的是我们设置描述符时让`CS.L = 1` `CS.D = 0` ,这里是为了64位的执行.`gdt`以一个2byte的值开始,`gdt_end - gdt`,代表`gdt`表的最后byte,或者说是表的限制地址.接下来4byte包含了gdt表的基址.

在通过`lgdt`加载`GDT`表后,我们通过将`cr4`寄存器的值放入eax中来启用`PAE`

```
movl    %cr4, %eax
    orl    $X86_CR4_PAE, %eax
    movl    %eax, %cr4
```

下一步是建立页表,在这之前了解一下长模式

#### <a class="reference-link" name="%E9%95%BF%E6%A8%A1%E5%BC%8F"></a>长模式

长模式是`x86-64`架构下的原生模式,首先看看`x86-64`与`x86`的区别

64位下提供以下的特性
<li>8个新的寄存器`r8-r15`
</li>
- 所有寄存器改为64bit
- 64位的rip
- 新的寻址模式
- 64位地址和操作数
- rip相关地址
长模式是保护模式的一个拓展,有两种相加的模式
- 64位模式
- 兼容模式
转入64-bit需要以下几个条件
- 支持PAE
- 建立页表以及加载最高级页表到cr3寄存器
<li>支持`EDER.LME`
</li>
- 支持页
在前一部分我们已经打开了’PAE’,接下来就是为页建造结构.

#### <a class="reference-link" name="%E9%A1%B5%E8%A1%A8%E7%9A%84%E6%97%A9%E6%9C%9F%E5%88%9D%E5%A7%8B%E5%8C%96"></a>页表的早期初始化

**NOTE** :**这里暂时不会讨论虚拟内存**

linux内核使用4级页缓存,我们一般建立6个页表
- 一个`PML4`或者说 `Page Map Level 4`表,带有一个入口点
- 一个`PDP` 或者说 `Page Directory Pointer`,带有四个入口点
- 4个页表 一共`2048`个入口
看看这些是如何定义的,首先,清理内存中页表的缓冲区,每一个表`4096`byte,所以我们需要清理一个`24`kb的缓冲区

```
leal    pgtable(%ebx), %edi
    xorl    %eax, %eax
    movl    $(BOOT_INIT_PGT_SIZE/4), %ecx
    rep    stosl
```

将`pgtable`的地址和`ebx`的偏移放入`edi`寄存器中,清理`eax`寄存器,将`ecx`寄存器值设置为`6144`

`rep stosl`会将`eax`寄存器的值写入`edi`所指的内存处,`edi`加4,`ecx`减1

这个操作重复执行直到`ecx`寄存器值为0,这是为什么eax被设定为 `BOOT_INIT_PGT_SIZE/4`也就是`6144`

`pgtable`定义在 [arch/x86/boot/compressed/head_64.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_64.S)的最后

```
.section ".pgtable","a",@nobits
    .balign 4096
pgtable:
    .fill BOOT_PGT_SIZE, 1, 0
```

它的大小由`CONFIG_X86_VERBOSE_BOOTUP`选项决定,

```
#  ifdef CONFIG_X86_VERBOSE_BOOTUP
#   define BOOT_PGT_SIZE    (19*4096)
#  else /* !CONFIG_X86_VERBOSE_BOOTUP */
#   define BOOT_PGT_SIZE    (17*4096)
#  endif
# else /* !CONFIG_RANDOMIZE_BASE */
#  define BOOT_PGT_SIZE        BOOT_INIT_PGT_SIZE
# endif
```

有了`pgtable`的缓冲区后,我们开始建立`PML4`

```
leal    pgtable + 0(%ebx), %edi
    leal    0x1007 (%edi), %eax
    movl    %eax, 0(%edi)
```

我们将`pgtable`与`ebx`关联后的结果放到`edi`中,(`ebx`是`startup_32`基地址)

然后将这个地址加上0x1007偏移放入eax寄存器. `0x1007`是`PML4`的size加上`7`

在这里`7`代表一些`PML4`入口的标志位.在这里这些标志是`PRESENT+RW+USER`

最后,将第一个`PDp`入口点写入`PML4`表中

接下来在’`Page Directory Pointer`表中’建立4个`Page Directory`入口,使用`PRESENT+RW+USE`标志位.

```
leal    pgtable + 0x1000(%ebx), %edi
    leal    0x1007(%edi), %eax
    movl    $4, %ecx
1:  movl    %eax, 0x00(%edi)
    addl    $0x00001000, %eax
    addl    $8, %edi
    decl    %ecx
    jnz    1b
```

设置`edi`为`页目录`指针,(pgtable + 0x1000(%ebx))

`eax`为第1个页目录指针的偏移.

`ecx`设置为`4`作为接下来循环的计数器

将第一个页目录指针写入edi寄存器,然后`edi`会包含第一个页目录指针地址(带有标志位0x7)

计算接下来页目录指针的地址,每一个指针8byte,将他们值写入eax

最后一步为`2Mbyte`页表建立`2048`个入口点

```
leal    pgtable + 0x2000(%ebx), %edi
    movl    $0x00000183, %eax
    movl    $2048, %ecx
1:  movl    %eax, 0(%edi)
    addl    $0x00200000, %eax
    addl    $8, %edi
    decl    %ecx
    jnz    1b
```

这一步基本与之前的两个步骤相同,所有的入口点都通过这些标志联系.`$0x00000183` – `PRESENT + WRITE + MBZ`

最后,我们得到2048个2mb的页,一共4gb内存

我们只完成了建立早期的页表结构,映射了4gb的内存,我们可以将高级页表的地址放到`cr3`控制寄存器中

```
leal    pgtable(%ebx), %eax
    movl    %eax, %cr3
```

接下来就是转入64位了

#### <a class="reference-link" name="%E8%BD%AC%E5%85%A564%E4%BD%8D"></a>转入64位

首先我们需要设置`EFER.LME`标志在[MSR](http://en.wikipedia.org/wiki/Model-specific_register) 为`0xC0000080`:

```
movl    $MSR_EFER, %ecx
    rdmsr
    btsl    $_EFER_LME, %eax
    wrmsr
```

我们将`MSR_EFER`标志位([arch/x86/include/asm/msr-index.h](https://github.com/torvalds/linux/blob/v4.16/arch/x86/include/asm/msr-index.h))放入`ecx`,

执行`rdmsr` 语句,来读取`MSR`寄存器,之后,将获得结果的数据会储存在`edx:eax`中

检查当前的`EFER_LME`bit位,转移它到携带标志位,更新bit位.这些通过`btsl`语句执行.然后我们`ebx:eax`值写回`MSR`寄存器

在下一步中,将内核段地址压入栈中,将`startup_64`地址放入`eax`中

```
pushl    $__KERNEL_CS
    leal    startup_64(%ebp), %eax
```

然后,将`eax`压入栈中,通过设置`PG`标志位来启用页.将`PE`bits放入`cr0`寄存器

然后执行`lret`

```
lret
```

我们已经将`startup_64`函数地址放入栈中,CPU提取该地址并跳转到这里

最终经过一系列的设置,我们进入了64位模式

```
.code64
    .org 0x200
ENTRY(startup_64)
....
....
....
```



## Links
- [Protected mode](http://en.wikipedia.org/wiki/Protected_mode)
- [Intel® 64 and IA-32 Architectures Software Developer’s Manual 3A](http://www.intel.com/content/www/us/en/processors/architectures-software-developer-manuals.html)
- [GNU linker](http://www.eecs.umich.edu/courses/eecs373/readings/Linker.pdf)
- [SSE](http://en.wikipedia.org/wiki/Streaming_SIMD_Extensions)
- [Paging](http://en.wikipedia.org/wiki/Paging)
- [Model specific register](http://en.wikipedia.org/wiki/Model-specific_register)
- [.fill instruction](http://www.chemie.fu-berlin.de/chemnet/use/info/gas/gas_7.html)
- [Previous part](https://github.com/0xAX/linux-insides/blob/v4.16/Booting/linux-bootstrap-3.md)
- [Paging on osdev.org](http://wiki.osdev.org/Paging)
- [Paging Systems](https://www.cs.rutgers.edu/~pxk/416/notes/09a-paging.html)
- x86 Paging Tutorial