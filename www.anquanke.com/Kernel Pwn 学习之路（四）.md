
# Kernel Pwn 学习之路（四）


                                阅读量   
                                **335129**
                            
                        |
                        
                                                                                                                                    ![](./img/202988/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/202988/t012b90699683ce2270.jpg)](./img/202988/t012b90699683ce2270.jpg)



## 0x01 前言

由于关于Kernel安全的文章实在过于繁杂，本文有部分内容大篇幅或全文引用了参考文献，若出现此情况的，将在相关内容的开头予以说明，部分引用参考文献的将在文件结尾的参考链接中注明。

Kernel的相关知识以及一些实例在Kernel中的利用已经在Kernel Pwn 学习之路(一)(二)给予了说明

Kernel中内存管理的相关知识已经在Kernel Pwn 学习之路(三)给予了说明

本文以及接下来的几篇文章将主要以系统调用为例介绍内核中的中断处理机制。本文涉及到的所有`Linux Kernel`相关代码均基于`5.6.2`版本。

限于篇幅的原因，本文仅介绍了`IDT`的初始化，下一篇文章将更多的涉及中断服务函数的内容~

【传送门】：[Kernel Pwn 学习之路(一)](https://www.anquanke.com/post/id/201043)

【传送门】：[Kernel Pwn 学习之路(二)](https://www.anquanke.com/post/id/201454)

【传送门】：[Kernel Pwn 学习之路(三)](https://www.anquanke.com/post/id/202371)



## 0x02 中断的概述

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E4%B8%AD%E6%96%AD"></a>什么是中断

中断是指在CPU正常运行期间，由于内外部事件或由程序预先安排的事件引起的CPU暂时停止正在运行的程序，转而为该内部或外部事件或预先安排的事件服务的程序中去，服务完毕后再返回去继续运行被暂时中断的程序。

这里我们可以举一个比较实际的例子🌰：

比如说我正在厨房用煤气烧一壶水，这样就只能守在厨房里，苦苦等着水开——如果水溢出来浇灭了煤气，有可能就要发生一场灾难了。等啊等啊，外边突然传来了惊奇的叫声“怎么不关水龙头？”，于是我惭愧的发现，刚才接水之后只顾着抱怨这份无聊的差事，居然忘了这事，于是慌慌张张的冲向水管，三下两下关了龙头，声音又传到耳边，“怎么干什么都是这么马虎？”。伸伸舌头，这件小事就这么过去了，我落寞的眼神又落在了水壶上。

门外忽然又传来了铿锵有力的歌声，我最喜欢的古装剧要开演了，真想夺门而出，然而，听着水壶发出“咕嘟咕嘟”的声音，我清楚：除非等到水开，否则没有我享受人生的时候。在这个场景中，我是唯一具有处理能力的主体，不管是烧水、关水龙头还是看电视，同一个时间点上我只能干一件事情。但是，在我专心致志干一件事情时，总有许多或紧迫或不紧迫的事情突然出现在面前，都需要去关注，有些还需要我停下手头的工作马上去处理。只有在处理完之后，方能回头完成先前的任务，“把一壶水彻底烧开！”

中断机制不仅赋予了我处理意外情况的能力，如果我能充分发挥这个机制的妙用，就可以“同时”完成多个任务了。回到烧水的例子，实际上，无论我在不在厨房，煤气灶总是会把水烧开的，我要做的，只不过是及时关掉煤气灶而已，为了这么一个一秒钟就能完成的动作，却让我死死地守候在厨房里，在10分钟的时间里不停地看壶嘴是不是冒蒸气，怎么说都不划算。我决定安下心来看电视。当然，在有生之年，我都不希望让厨房成为火海，于是我上了闹钟，10分钟以后它会发出“尖叫”，提醒我炉子上的水烧开了，那时我再去关煤气也完全来得及。我用一个中断信号——闹铃——换来了10分钟的欢乐时光，心里不禁由衷地感叹：中断机制真是个好东西。

**正是由于中断机制，我才能有条不紊地“同时”完成多个任务，中断机制实质上帮助我提高了并发“处理”能力。**它也能给计算机系统带来同样的好处：如果在键盘按下的时候会得到一个中断信号，CPU就不必死守着等待键盘输入了；如果硬盘读写完成后发送一个中断信号，CPU就可以腾出手来集中精力“服务大众”了——无论是人类敲打键盘的指尖还是来回读写介质的磁头，跟CPU的处理速度相比，都太慢了。没有中断机制，就像我们苦守厨房一样，计算机谈不上有什么并行处理能力。

跟人相似，CPU也一样要面对纷繁芜杂的局面——现实中的意外是无处不在的——有可能是用户等得不耐烦，猛敲键盘；有可能是运算中碰到了0除数；还有可能网卡突然接收到了一个新的数据包。这些都需要CPU具体情况具体分析，要么马上处理，要么暂缓响应，要么置之不理。无论如何应对，都需要CPU暂停“手头”的工作，拿出一种对策，只有在响应之后，方能回头完成先前的使命，“把一壶水彻底烧开！”

### <a class="reference-link" name="%E4%B8%AD%E6%96%AD%E7%9A%84%E7%B1%BB%E5%9E%8B"></a>中断的类型

概括地说，可以将中断分为两个主要类别：
- 外部或硬件产生的中断（异步中断）
- 软件生成的中断（同步中断）
异步中断是通过由 `Local APIC` 或者与 `Local APIC` 连接的处理器针脚接收。

同步中断是由处理器自身的特殊情况引起(有时使用特殊架构的指令)。一个常见的例子是是`division by zero`（除零错误），另一个示例是使用`syscall`指令退出程序。

如前所述，中断可以在任何时间因为超出代码和 CPU 控制的原因而发生。对于同步中断，还可以分为三类：
<li>
`Faults`（故障）—— 这是在执行“不完善的”指令之前报告的异常，中断服务程序运行结束后允许恢复被中断的程序。</li>
<li>
`Traps`（陷门）—— 这是在执行`trap`指令之后即刻报告的异常，中断服务程序运行结束后允许恢复被中断的程序。</li>
<li>
`Aborts`（终止）—— 这种异常从不报告引起异常的精确指令，中断服务程序运行结束不允许恢复被中断的程序。</li>
另外，中断又可分为可屏蔽中断(`Maskable interrupt`)和非屏蔽中断(`Nomaskable interrupt`)。

对于可屏蔽中断，在`x86_64`架构中，可以使用`cli`命令阻止中断信号的发送。

```
/* In /source/arch/x86/include/asm/irqflags.h#L47 */

static inline void native_irq_disable(void)
{
    asm volatile("cli": : :"memory");
}

static inline void native_irq_enable(void)
{
    asm volatile("sti": : :"memory");
}
```

可屏蔽中断能否发送取决于中断寄存器中的`IF`标志位。

`cli`命令会将在这个标志位清除，而`sti`命令会将这个标志位置位。

非屏蔽中断将会始终进行报告，**通常，硬件产生的任何错误都将作为非屏蔽中断进行报告！**

### <a class="reference-link" name="%E4%B8%AD%E6%96%AD%E7%9A%84%E4%BA%A7%E7%94%9F"></a>中断的产生

简化起见，假定每一个物理硬件都有一根连接 CPU 的中断线。设备可以使用它向CPU发出中断信号。但是，这个中断信号并不会直接发送给CPU。在老旧的机器中，有一个[PIC](http://en.wikipedia.org/wiki/Programmable_Interrupt_Controller)芯片，负责顺序处理来自各种设备的各种中断请求。在新机器中，有一个通常被称为 `APIC`的[高级可编程中断控制器](https://en.wikipedia.org/wiki/Advanced_Programmable_Interrupt_Controller)。一个`APIC` 由两个互相独立的设备组成：
<li>
`Local APIC`(本地控制器)</li>
<li>
`I/O APIC`(IO控制器)`Local APIC`位于每个CPU核心中，它负责处理特定于 CPU 的中断配置。</li>
`Local APIC`常被用于管理来自`APIC`时钟(`APIC-timer`)、热敏元件和其他与`I/O`设备连接的设备的中断。

`I/O APIC`提供多核处理器的中断管理，它被用来在所有的 CPU 核心中分发外部中断。

中断可以随时发生。发生中断时，操作系统必须立即处理它。处理逻辑的概述如下：
1. 内核必须暂停执行当前进程。（抢占当前任务）
1. 内核必须搜索中断处理程序并且转交控制权（执行中断处理程序）
1. 中断处理程序执行结束后，被中断的进程可以恢复执行。（交还控制流，解除抢占）
当然，在处理中断的过程中涉及许多复杂问题。但是以上三个步骤构成了该过程的基本框架。

每个中断处理程序的地址都被保存在一个特殊的位置，这个位置被称为`IDT(Interrupt Descriptor Table,中断描述符表)`。

如果同时发生多个异常或中断，则处理器将按照其预定义的优先级顺序对其进行处理。优先级如下所示：
1. 硬件**重置**或**机器检查**(`Hardware Reset and Machine Checks`)
1. 任务调度时触发陷门(`Trap on Task Switch`) —— `TSS`中的`T`标志位被置位时发生
<li>外部硬件干预(External Hardware Interventions) —— 发生下列指令之一时报告
<ul>
<li>
`FLUSH` —— 刷新</li>
<li>
`STOPCLK` —— 时钟发出终止信号</li>
<li>
`SMI` —— 系统管理中断(`System Management Interrupt`)</li>
<li>
`INIT` —— 初始化</li>
</ul>
</li>
1. 指令陷门(`Traps on the Previous Instruction`) —— 常见于断点(`BreakPoint`)和调试异常(`Debug Trap Exceptions`)
1. 非屏蔽中断(`Nonmaskable Interrupts`)
1. 可屏蔽的硬件中断(`Maskable Hardware Interrupts`)
1. 代码断点错误(`Code Breakpoint Fault`)
<li>以下三种异常或中断均属于第八优先级
<ul>
1. 获取下一条指令时出错(`Faults from Fetching Next Instruction`)
1. 违反代码段限制(`Code-Segment Limit Violation`)
1. 代码页错误(`Code Page Fault`)
</ul>
</li>
<li>以下四种异常或中断均属于第九优先级
<ul>
1. 对下一条指令解码时出错(`Faults from Decoding the Next Instruction`)
1. 指令长度大于16个字节(`Instruction length &gt; 15 bytes`)
<li>
`OP Code`不合法(`Invalid Opcode`)</li>
1. 协处理器不可用(`Coprocessor Not Available`)
</ul>
</li>
<li>以下几种异常或中断均属于第十优先级
<ul>
1. 运行指令时出错(`Faults on Executing an Instruction`)
1. 溢出(`Instruction length &gt; 15 bytes`)
1. 绑定错误(`Bound error`)
1. 任务状态段不合法(`Invalid TSS(Task State Segment)`)
1. 段不存在(`Segment Not Present`)
1. 堆栈错误(`Stack fault`)
1. 一般保护(`General Protection`)
1. 数据页错误(`Data Page Fault`)
1. 对齐验证(`Alignment Check`)
1. x87 FPU浮点异常(`x87 FPU Floating-point exception`)
1. SIMD FPU浮点异常(`SIMD floating-point exception`)
1. 虚拟化异常(`Virtualization exception`)
</ul>
</li>- 获取下一条指令时出错(`Faults from Fetching Next Instruction`)
- 违反代码段限制(`Code-Segment Limit Violation`)
- 代码页错误(`Code Page Fault`)- 运行指令时出错(`Faults on Executing an Instruction`)
- 溢出(`Instruction length &gt; 15 bytes`)
- 绑定错误(`Bound error`)
- 任务状态段不合法(`Invalid TSS(Task State Segment)`)
- 段不存在(`Segment Not Present`)
- 堆栈错误(`Stack fault`)
- 一般保护(`General Protection`)
- 数据页错误(`Data Page Fault`)
- 对齐验证(`Alignment Check`)
- x87 FPU浮点异常(`x87 FPU Floating-point exception`)
- SIMD FPU浮点异常(`SIMD floating-point exception`)
- 虚拟化异常(`Virtualization exception`)
### <a class="reference-link" name="%E4%B8%AD%E6%96%AD%E5%8F%B7%E4%B8%8E%E4%B8%AD%E6%96%AD%E5%90%91%E9%87%8F"></a>中断号与中断向量

处理器使用唯一的编号来识别中断或异常的类型，这个编号被称为中断号( `vector number`)。它将作为`IDT(Interrupt Descriptor Table,中断描述符表)`的索引值，中断号的取值范围是从`0`到`255`。在`Linux Kernel`中关于中断设置的地方可以找到这样的检查：

```
/* In /source/arch/x86/kernel/idt.c#L230 */

static void set_intr_gate(unsigned int n, const void *addr)
{
    struct idt_data data;

    BUG_ON(n &gt; 0xFF);

    memset(&amp;data, 0, sizeof(data));
    data.vector    = n;
    data.addr    = addr;
    data.segment    = __KERNEL_CS;
    data.bits.type    = GATE_INTERRUPT;
    data.bits.p    = 1;

    idt_setup_from_table(idt_table, &amp;data, 1, false);
}
```

**从`0`到`31`的前32个中断号由处理器保留，用于处理体系结构定义的异常和中断。**

|Vector|Mnemonic|Description|Type|Error Code|Source
|------
|0|#DE|Divide Error|Fault|NO|DIV and IDIV
|1|#DB|Reserved|F/T|NO|
|2|—-|NMI|INT|NO|external NMI
|3|#BP|Breakpoint|Trap|NO|INT 3
|4|#OF|Overflow|Trap|NO|INTO instruction
|5|#BR|Bound Range Exceeded|Fault|NO|BOUND instruction
|6|#UD|Invalid Opcode|Fault|NO|UD2 instruction
|7|#NM|Device Not Available|Fault|NO|Floating point or [F]WAIT
|8|#DF|Double Fault|Abort|YES|An instruction which can generate NMI
|9|—-|Reserved|Fault|NO|
|10|#TS|Invalid TSS|Fault|YES|Task switch or TSS access
|11|#NP|Segment Not Present|Fault|NO|Accessing segment register
|12|#SS|Stack-Segment Fault|Fault|YES|Stack operations
|13|#GP|General Protection|Fault|YES|Memory reference
|14|#PF|Page fault|Fault|YES|Memory reference
|15|—-|Reserved||NO|
|16|#MF|x87 FPU fp error|Fault|NO|Floating point or [F]Wait
|17|#AC|Alignment Check|Fault|YES|Data reference
|18|#MC|Machine Check|Abort|NO|
|19|#XM|SIMD fp exception|Fault|NO|SSE[2,3] instructions
|20|#VE|Virtualization exc.|Fault|NO|EPT violations
|21-31|—-|Reserved|INT|NO|External interrupts

从 `32` 到 `255` 的中断标识码设计为用户定义中断并且不被系统保留。这些中断通常分配给外部`I/O`设备，使这些设备可以发送中断给处理器。

如前所述，`IDT`存储中断和异常处理程序的入口点，其结构与`Global Descriptor Table`结构类似。`IDT`的表项被称为门(`gates`)的成员，它可以是以下类型之一：
- Interrupt gates(中断门)
- Task gates(任务门)
- Trap gates(陷阱门)
在`x86`架构下，仅能使用[长模式](http://en.wikipedia.org/wiki/Long_mode)下的`Interrupt gates`或`Trap gates`能在`x86_64`中被引用。就像 `GDT`(全局描述符表)，`IDT` 在 `x86` 上是一个 8 字节数组门，而在 `x86_64` 上是一个 16 字节数组门。

`IDT` 可以在线性地址空间和基址的任何地方被加载。同时，它需要在 `x86` 上以 8 字节对齐，在 `x86_64` 上以 16 字节对齐。`IDT` 的基址存储在一个特殊的寄存器——`IDTR`中。

在 `x86` 上有两个指令`LIDT(Load Interrupt Descriptor Table`)、`SIDT(Store Interrupt Descriptor Table)`来修改 `IDTR` 寄存器的值。

指令 `LIDT` 用来加载 `IDT` 的基址，即将指定操作数存在 `IDTR`中。

指令 `SIDT` 用来在读取 `IDTR` 的内容并将其存储在指定操作数中。

在 `x86` 上 `IDTR` 寄存器是 48 位，包含了下面的信息：

```
47                                16 15                    0
+-----------------------------------+----------------------+
|     Base address of the IDT       |   Limit of the IDT   |
+-----------------------------------+----------------------+
```



## 0x03 IDT 的初始化

`IDT`由`setup_idt`函数进行建立及初始化操作

### 处理器准备进入保护模式(`go_to_protected_mode`函数分析)

对IDT的配置在`go_to_protected_mode`函数中完成，该函数首先调用了 `setup_idt`函数配置了IDT，然后将处理器的工作模式从实模式环境中脱离进入[保护模式](http://en.wikipedia.org/wiki/Protected_mode)。保护模式(`Protected Mode`，或有时简写为 `pmode`)是一种`80286`系列和之后的`x86`兼容`CPU`操作模式。保护模式有一些新的特色，设计用来增强多功能和系统稳定度，像是内存保护，分页系统，以及硬件支援的虚拟内存。大部分的现今`x86`操作系统都在保护模式下运行，包含`Linux`、`FreeBSD`、以及微软 `Windows 2.0`和之后版本。

`setup_idt`函数在`go_to_protected_mode`函数中调用，`go_to_protected_mode`函数在`/source/arch/x86/boot/pm.c#L102`中实现：

```
/*
 * Actual invocation sequence
 */
void go_to_protected_mode(void)
{
    /* Hook before leaving real mode, also disables interrupts */
    // 首先进行Hook操作进而从实模式中脱离，禁用中断
    realmode_switch_hook();

    /* Enable the A20 gate */
    // 启动 A20 门
    if (enable_a20()) {
        puts("A20 gate not responding, unable to boot...n");
        die();
    }

    /* Reset coprocessor (IGNNE#) */
    // 重置协处理器
    reset_coprocessor();

    /* Mask all interrupts in the PIC */
    // 在 PIC 中标记所有的中断
    mask_all_interrupts();

    /* Actual transition to protected mode... */
    // 开始过渡到保护模式
    setup_idt();
    setup_gdt();
    // 正式进入保护模式
    protected_mode_jump(boot_params.hdr.code32_start,(u32)&amp;boot_params + (ds() &lt;&lt; 4));
}
```

#### 初始化`IDTR`寄存器(`setup_idt`函数分析)

`setup_idt` 在`/source/arch/x86/boot/pm.c#L93`中实现

`go_to_protected_mode`将仅加载一个NULL表项在`IDT`中

```
/*
 * Set up the IDT
 */
static void setup_idt(void)
{
    // 准备一个 null_idt
    static const struct gdt_ptr null_idt = {0, 0};
    // 使用 lidt 指令把它加载到 IDTR 寄存器
    asm volatile("lidtl %0" : : "m" (null_idt));
}
```

`gdt_ptr` 类型表示了一个48-bit的特殊功能寄存器 `GDTR`，其包含了全局描述符表 `Global Descriptor Table`的基地址，其在`/source/arch/x86/boot/pm.c#L59`中定义：

```
/*
 * Set up the GDT
 */

struct gdt_ptr {
    u16 len;
    u32 ptr;
} __attribute__((packed));
```

这就是 `IDTR` 结构的定义，就像我们在之前的示意图中看到的一样，由 2 字节和 4 字节(共 48 位)的两个域组成。显然，在此处的 `gdt_prt`不是代表 `GDTR`寄存器而是代表 `IDTR`寄存器，因为我们将其设置到了中断描述符表中。之所以在`Linux`内核代码中没有`idt_ptr`结构体，是因为其与`gdt_prt`具有相同的结构而仅仅是名字不同，因此没必要定义两个重复的数据结构。可以看到，内核在此处并没有填充`Interrupt Descriptor Table`，这是因为此刻处理任何中断或异常还为时尚早，因此我们仅仅以`NULL`来填充`IDT`。

#### 处理器正式进入保护模式(`protected_mode_jump`函数分析)

在设置完`IDT`、`GDT`和其他一些东西以后，内核调用`protected_mode_jump`正式进入保护模式。

这部分代码在`/source/arch/x86/boot/pmjump.S#L24`中实现。

```
/*
 * The actual transition into protected mode
 */

#include &lt;asm/boot.h&gt;
#include &lt;asm/processor-flags.h&gt;
#include &lt;asm/segment.h&gt;
#include &lt;linux/linkage.h&gt;

    .text
    .code16

/*
 * void protected_mode_jump(u32 entrypoint, u32 bootparams);
 */
SYM_FUNC_START_NOALIGN(protected_mode_jump)
    movl    %edx, %esi        # Pointer to boot_params table

    xorl    %ebx, %ebx
    movw    %cs, %bx
    shll    $4, %ebx
    addl    %ebx, 2f
    jmp    1f            # Short jump to serialize on 386/486
1:

    movw    $__BOOT_DS, %cx
    movw    $__BOOT_TSS, %di

    movl    %cr0, %edx
    orb    $X86_CR0_PE, %dl    # Protected mode
    movl    %edx, %cr0

    # Transition to 32-bit mode
    .byte    0x66, 0xea        # ljmpl opcode
2:    .long    .Lin_pm32        # offset
    .word    __BOOT_CS        # segment
SYM_FUNC_END(protected_mode_jump)
```

其中 `in_pm32`包含了对32-bit入口的跳转语句:

```
.code32
    .section ".text32","ax"
SYM_FUNC_START_LOCAL_NOALIGN(.Lin_pm32)
    # Set up data segments for flat 32-bit mode
    movl    %ecx, %ds
    movl    %ecx, %es
    movl    %ecx, %fs
    movl    %ecx, %gs
    movl    %ecx, %ss
    # The 32-bit code sets up its own stack, but this way we do have
    # a valid stack if some debugging hack wants to use it.
    addl    %ebx, %esp

    # Set up TR to make Intel VT happy
    ltr    %di

    # Clear registers to allow for future extensions to the
    # 32-bit boot protocol
    xorl    %ecx, %ecx
    xorl    %edx, %edx
    xorl    %ebx, %ebx
    xorl    %ebp, %ebp
    xorl    %edi, %edi

    # Set up LDTR to make Intel VT happy
    lldt    %cx

    jmpl    *%eax            # Jump to the 32-bit entrypoint
SYM_FUNC_END(.Lin_pm32)
```

`32-bit`的入口地址位于汇编文件`/source/arch/x86/boot/compressed/head_64.S`中，尽管它的名字包含 `_64`后缀。我们可以在 `/source/arch/x86/boot/compressed`目录下看到两个相似的文件:
<li>
`/source/arch/x86/boot/compressed/head_32.S`.</li>
<li>
`/source/arch/x86/boot/compressed/head_64.S`;</li>
然而`32-bit`模式的入口位于第二个文件中，而第一个文件在 `x86_64`配置下不会参与编译。

我们可以查看`/source/arch/x86/boot/compressed/Makefile#L76`

```
vmlinux-objs-y := $(obj)/vmlinux.lds $(obj)/kernel_info.o $(obj)/head_$(BITS).o 
    $(obj)/misc.o $(obj)/string.o $(obj)/cmdline.o $(obj)/error.o 
    $(obj)/piggy.o $(obj)/cpuflags.o
```

代码中的 `head_*`取决于 `$(BITS)` 变量的值，而该值由”架构”决定。我们可以在`/source/arch/x86/Makefile#L64`找到相关代码:

```
ifeq ($(CONFIG_X86_32),y)
        BITS := 32
        ......
else
        BITS := 64
        ......
```

### 处理器进入长模式(`startup_32`函数分析)

现在程序从`protected_mode_jump`来到了`startup_32`中，这个函数将为处理器进入长模式`long mode`做好准备，并且直接跳转进入长模式：

```
.code32
    .text

#include &lt;linux/init.h&gt;
#include &lt;linux/linkage.h&gt;
#include &lt;asm/segment.h&gt;
#include &lt;asm/boot.h&gt;
#include &lt;asm/msr.h&gt;
#include &lt;asm/processor-flags.h&gt;
#include &lt;asm/asm-offsets.h&gt;
#include &lt;asm/bootparam.h&gt;
#include "pgtable.h"

/*
 * Locally defined symbols should be marked hidden:
 */
    .hidden _bss
    .hidden _ebss
    .hidden _got
    .hidden _egot

    __HEAD
    .code32
SYM_FUNC_START(startup_32)
    /*
     * 32bit entry is 0 and it is ABI so immutable!
     * 32bit 的条目是 0 ，它是 Application binary interface ，因此它的值是静态的！
     * If we come here directly from a bootloader,
     * kernel(text+data+bss+brk) ramdisk, zero_page, command line
     * all need to be under the 4G limit.
     */
    cld
    /*
     * Test KEEP_SEGMENTS flag to see if the bootloader is asking
     * us to not reload segments
     */
    testb $KEEP_SEGMENTS, BP_loadflags(%esi)
    jnz 1f

    cli
    movl    $(__BOOT_DS), %eax
    movl    %eax, %ds
    movl    %eax, %es
    movl    %eax, %ss
1:

/*
 * Calculate the delta between where we were compiled to run
 * at and where we were actually loaded at.  This can only be done
 * with a short local call on x86.  Nothing  else will tell us what
 * address we are running at.  The reserved chunk of the real-mode
 * data at 0x1e4 (defined as a scratch field) are used as the stack
 * for this calculation. Only 4 bytes are needed.
 */
    leal    (BP_scratch+4)(%esi), %esp
    call    1f
1:    popl    %ebp
    subl    $1b, %ebp

/* setup a stack and make sure cpu supports long mode. */
    movl    $boot_stack_end, %eax
    addl    %ebp, %eax
    movl    %eax, %esp

    call    verify_cpu
    testl    %eax, %eax
    jnz    .Lno_longmode

/*
 * Compute the delta between where we were compiled to run at
 * and where the code will actually run at.
 *
 * %ebp contains the address we are loaded at by the boot loader and %ebx
 * contains the address where we should move the kernel image temporarily
 * for safe in-place decompression.
 */

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
1:

    /* Target address to relocate to for decompression */
    movl    BP_init_size(%esi), %eax
    subl    $_end, %eax
    addl    %eax, %ebx

/*
 * Prepare for entering 64 bit mode
 */

    /* Load new GDT with the 64bit segments using 32bit descriptor */
    addl    %ebp, gdt+2(%ebp)
    lgdt    gdt(%ebp)

    /* Enable PAE mode */
    movl    %cr4, %eax
    orl    $X86_CR4_PAE, %eax
    movl    %eax, %cr4

 /*
  * Build early 4G boot pagetable
  */
    /*
     * If SEV is active then set the encryption mask in the page tables.
     * This will insure that when the kernel is copied and decompressed
     * it will be done so encrypted.
     */
    call    get_sev_encryption_bit
    xorl    %edx, %edx
    testl    %eax, %eax
    jz    1f
    subl    $32, %eax    /* Encryption bit is always above bit 31 */
    bts    %eax, %edx    /* Set encryption mask for page tables */
1:

    /* Initialize Page tables to 0 */
    leal    pgtable(%ebx), %edi
    xorl    %eax, %eax
    movl    $(BOOT_INIT_PGT_SIZE/4), %ecx
    rep    stosl

    /* Build Level 4 */
    leal    pgtable + 0(%ebx), %edi
    leal    0x1007 (%edi), %eax
    movl    %eax, 0(%edi)
    addl    %edx, 4(%edi)

    /* Build Level 3 */
    leal    pgtable + 0x1000(%ebx), %edi
    leal    0x1007(%edi), %eax
    movl    $4, %ecx
1:    movl    %eax, 0x00(%edi)
    addl    %edx, 0x04(%edi)
    addl    $0x00001000, %eax
    addl    $8, %edi
    decl    %ecx
    jnz    1b

    /* Build Level 2 */
    leal    pgtable + 0x2000(%ebx), %edi
    movl    $0x00000183, %eax
    movl    $2048, %ecx
1:    movl    %eax, 0(%edi)
    addl    %edx, 4(%edi)
    addl    $0x00200000, %eax
    addl    $8, %edi
    decl    %ecx
    jnz    1b

    /* Enable the boot page tables */
    leal    pgtable(%ebx), %eax
    movl    %eax, %cr3

    /* Enable Long mode in EFER (Extended Feature Enable Register) */
    movl    $MSR_EFER, %ecx
    rdmsr
    btsl    $_EFER_LME, %eax
    wrmsr

    /* After gdt is loaded */
    xorl    %eax, %eax
    lldt    %ax
    movl    $__BOOT_TSS, %eax
    ltr    %ax

    /*
     * Setup for the jump to 64bit mode
     *
     * When the jump is performend we will be in long mode but
     * in 32bit compatibility mode with EFER.LME = 1, CS.L = 0, CS.D = 1
     * (and in turn EFER.LMA = 1).    To jump into 64bit mode we use
     * the new gdt/idt that has __KERNEL_CS with CS.L = 1.
     * We place all of the values on our mini stack so lret can
     * used to perform that far jump.
     */
    pushl    $__KERNEL_CS
    leal    startup_64(%ebp), %eax
#ifdef CONFIG_EFI_MIXED
    movl    efi32_boot_args(%ebp), %edi
    cmp    $0, %edi
    jz    1f
    leal    efi64_stub_entry(%ebp), %eax
    movl    %esi, %edx
    movl    efi32_boot_args+4(%ebp), %esi
1:
#endif
    pushl    %eax

    /* Enter paged protected Mode, activating Long Mode */
    movl    $(X86_CR0_PG | X86_CR0_PE), %eax /* Enable Paging and Protected mode */
    movl    %eax, %cr0

    /* Jump from 32bit compatibility mode into 64bit mode. */
    lret
SYM_FUNC_END(startup_32)
```

处理器进入长模式后将跳入`startup_64`函数

```
.code64
    .org 0x200
SYM_CODE_START(startup_64)
    /*
     * 64bit entry is 0x200 and it is ABI so immutable!
     * We come here either from startup_32 or directly from a
     * 64bit bootloader.
     * If we come here from a bootloader, kernel(text+data+bss+brk),
     * ramdisk, zero_page, command line could be above 4G.
     * We depend on an identity mapped page table being provided
     * that maps our entire kernel(text+data+bss+brk), zero page
     * and command line.
     */

    /* Setup data segments. */
    xorl    %eax, %eax
    movl    %eax, %ds
    movl    %eax, %es
    movl    %eax, %ss
    movl    %eax, %fs
    movl    %eax, %gs

    /*
     * Compute the decompressed kernel start address.  It is where
     * we were loaded at aligned to a 2M boundary. %rbp contains the
     * decompressed kernel start address.
     *
     * If it is a relocatable kernel then decompress and run the kernel
     * from load address aligned to 2MB addr, otherwise decompress and
     * run the kernel from LOAD_PHYSICAL_ADDR
     *
     * We cannot rely on the calculation done in 32-bit mode, since we
     * may have been invoked via the 64-bit entry point.
     */

    /* Start with the delta to where the kernel will run at. */
#ifdef CONFIG_RELOCATABLE
    leaq    startup_32(%rip) /* - $startup_32 */, %rbp
    movl    BP_kernel_alignment(%rsi), %eax
    decl    %eax
    addq    %rax, %rbp
    notq    %rax
    andq    %rax, %rbp
    cmpq    $LOAD_PHYSICAL_ADDR, %rbp
    jge    1f
#endif
    movq    $LOAD_PHYSICAL_ADDR, %rbp
1:

    /* Target address to relocate to for decompression */
    movl    BP_init_size(%rsi), %ebx
    subl    $_end, %ebx
    addq    %rbp, %rbx

    /* Set up the stack */
    leaq    boot_stack_end(%rbx), %rsp

    /*
     * paging_prepare() and cleanup_trampoline() below can have GOT
     * references. Adjust the table with address we are running at.
     *
     * Zero RAX for adjust_got: the GOT was not adjusted before;
     * there's no adjustment to undo.
     */
    xorq    %rax, %rax

    /*
     * Calculate the address the binary is loaded at and use it as
     * a GOT adjustment.
     */
    call    1f
1:    popq    %rdi
    subq    $1b, %rdi

    call    .Ladjust_got

    /*
     * At this point we are in long mode with 4-level paging enabled,
     * but we might want to enable 5-level paging or vice versa.
     *
     * The problem is that we cannot do it directly. Setting or clearing
     * CR4.LA57 in long mode would trigger #GP. So we need to switch off
     * long mode and paging first.
     *
     * We also need a trampoline in lower memory to switch over from
     * 4- to 5-level paging for cases when the bootloader puts the kernel
     * above 4G, but didn't enable 5-level paging for us.
     *
     * The same trampoline can be used to switch from 5- to 4-level paging
     * mode, like when starting 4-level paging kernel via kexec() when
     * original kernel worked in 5-level paging mode.
     *
     * For the trampoline, we need the top page table to reside in lower
     * memory as we don't have a way to load 64-bit values into CR3 in
     * 32-bit mode.
     *
     * We go though the trampoline even if we don't have to: if we're
     * already in a desired paging mode. This way the trampoline code gets
     * tested on every boot.
     */

    /* Make sure we have GDT with 32-bit code segment */
    leaq    gdt(%rip), %rax
    movq    %rax, gdt64+2(%rip)
    lgdt    gdt64(%rip)

    /*
     * paging_prepare() sets up the trampoline and checks if we need to
     * enable 5-level paging.
     *
     * paging_prepare() returns a two-quadword structure which lands
     * into RDX:RAX:
     *   - Address of the trampoline is returned in RAX.
     *   - Non zero RDX means trampoline needs to enable 5-level
     *     paging.
     *
     * RSI holds real mode data and needs to be preserved across
     * this function call.
     */
    pushq    %rsi
    movq    %rsi, %rdi        /* real mode address */
    call    paging_prepare
    popq    %rsi

    /* Save the trampoline address in RCX */
    movq    %rax, %rcx

    /*
     * Load the address of trampoline_return() into RDI.
     * It will be used by the trampoline to return to the main code.
     */
    leaq    trampoline_return(%rip), %rdi

    /* Switch to compatibility mode (CS.L = 0 CS.D = 1) via far return */
    pushq    $__KERNEL32_CS
    leaq    TRAMPOLINE_32BIT_CODE_OFFSET(%rax), %rax
    pushq    %rax
    lretq
trampoline_return:
    /* Restore the stack, the 32-bit trampoline uses its own stack */
    leaq    boot_stack_end(%rbx), %rsp

    /*
     * cleanup_trampoline() would restore trampoline memory.
     *
     * RDI is address of the page table to use instead of page table
     * in trampoline memory (if required).
     *
     * RSI holds real mode data and needs to be preserved across
     * this function call.
     */
    pushq    %rsi
    leaq    top_pgtable(%rbx), %rdi
    call    cleanup_trampoline
    popq    %rsi

    /* Zero EFLAGS */
    pushq    $0
    popfq

    /*
     * Previously we've adjusted the GOT with address the binary was
     * loaded at. Now we need to re-adjust for relocation address.
     *
     * Calculate the address the binary is loaded at, so that we can
     * undo the previous GOT adjustment.
     */
    call    1f
1:    popq    %rax
    subq    $1b, %rax

    /* The new adjustment is the relocation address */
    movq    %rbx, %rdi
    call    .Ladjust_got

/*
 * Copy the compressed kernel to the end of our buffer
 * where decompression in place becomes safe.
 */
    pushq    %rsi
    leaq    (_bss-8)(%rip), %rsi
    leaq    (_bss-8)(%rbx), %rdi
    movq    $_bss /* - $startup_32 */, %rcx
    shrq    $3, %rcx
    std
    rep    movsq
    cld
    popq    %rsi

/*
 * Jump to the relocated address.
 */
    leaq    .Lrelocated(%rbx), %rax
    jmp    *%rax
SYM_CODE_END(startup_64)
```

在这里将完成内核解压的准备工作。内核解压的主函数代码位于`/source/arch/x86/boot/compressed/misc.c`中的 `decompress_kernel`函数中，此处不再分析。

内核解压完成以后，程序返回`secondary_startup_64`函数(实现于`/source/arch/x86/kernel/head_64.S`)。在这个函数中，我们开始构建 `identity-mapped pages`，并在那之后检查NX位，配置 `Extended Feature Enable Register`，使用 `lgdt`指令更新早期的`Global Descriptor Table`。

```
SYM_CODE_START(secondary_startup_64)
    UNWIND_HINT_EMPTY
    /*
     * At this point the CPU runs in 64bit mode CS.L = 1 CS.D = 0,
     * and someone has loaded a mapped page table.
     *
     * %rsi holds a physical pointer to real_mode_data.
     *
     * We come here either from startup_64 (using physical addresses)
     * or from trampoline.S (using virtual addresses).
     *
     * Using virtual addresses from trampoline.S removes the need
     * to have any identity mapped pages in the kernel page table
     * after the boot processor executes this code.
     */

    /* Sanitize CPU configuration */
    call verify_cpu

    /*
     * Retrieve the modifier (SME encryption mask if SME is active) to be
     * added to the initial pgdir entry that will be programmed into CR3.
     */
    pushq    %rsi
    call    __startup_secondary_64
    popq    %rsi

    /* Form the CR3 value being sure to include the CR3 modifier */
    addq    $(init_top_pgt - __START_KERNEL_map), %rax
1:

    /* Enable PAE mode, PGE and LA57 */
    movl    $(X86_CR4_PAE | X86_CR4_PGE), %ecx
#ifdef CONFIG_X86_5LEVEL
    testl    $1, __pgtable_l5_enabled(%rip)
    jz    1f
    orl    $X86_CR4_LA57, %ecx
1:
#endif
    movq    %rcx, %cr4

    /* Setup early boot stage 4-/5-level pagetables. */
    addq    phys_base(%rip), %rax
    movq    %rax, %cr3

    /* Ensure I am executing from virtual addresses */
    movq    $1f, %rax
    ANNOTATE_RETPOLINE_SAFE
    jmp    *%rax
1:
    UNWIND_HINT_EMPTY

    /* Check if nx is implemented */
    movl    $0x80000001, %eax
    cpuid
    movl    %edx,%edi

    /* Setup EFER (Extended Feature Enable Register) */
    movl    $MSR_EFER, %ecx
    rdmsr
    btsl    $_EFER_SCE, %eax    /* Enable System Call */
    btl    $20,%edi        /* No Execute supported? */
    jnc     1f
    btsl    $_EFER_NX, %eax
    btsq    $_PAGE_BIT_NX,early_pmd_flags(%rip)
1:    wrmsr                /* Make changes effective */

    /* Setup cr0 */
    movl    $CR0_STATE, %eax
    /* Make changes effective */
    movq    %rax, %cr0

    /* Setup a boot time stack */
    movq initial_stack(%rip), %rsp

    /* zero EFLAGS after setting rsp */
    pushq $0
    popfq

    /*
     * We must switch to a new descriptor in kernel space for the GDT
     * because soon the kernel won't have access anymore to the userspace
     * addresses where we're currently running on. We have to do that here
     * because in 32bit we couldn't load a 64bit linear address.
     */
    lgdt    early_gdt_descr(%rip)

    /* set up data segments */
    xorl %eax,%eax
    movl %eax,%ds
    movl %eax,%ss
    movl %eax,%es

    /*
     * We don't really need to load %fs or %gs, but load them anyway
     * to kill any stale realmode selectors.  This allows execution
     * under VT hardware.
     */
    movl %eax,%fs
    movl %eax,%gs

    /* Set up %gs.
     *
     * The base of %gs always points to fixed_percpu_data. If the
     * stack protector canary is enabled, it is located at %gs:40.
     * Note that, on SMP, the boot cpu uses init data section until
     * the per cpu areas are set up.
     */
    movl    $MSR_GS_BASE,%ecx
    movl    initial_gs(%rip),%eax
    movl    initial_gs+4(%rip),%edx
    wrmsr

    /* rsi is pointer to real mode structure with interesting info.
       pass it to C */
    movq    %rsi, %rdi

.Ljump_to_C_code:
    /*
     * Jump to run C code and to be on a real kernel address.
     * Since we are running on identity-mapped space we have to jump
     * to the full 64bit address, this is only possible as indirect
     * jump.  In addition we need to ensure %cs is set so we make this
     * a far return.
     *
     * Note: do not change to far jump indirect with 64bit offset.
     *
     * AMD does not support far jump indirect with 64bit offset.
     * AMD64 Architecture Programmer's Manual, Volume 3: states only
     *    JMP FAR mem16:16 FF /5 Far jump indirect,
     *        with the target specified by a far pointer in memory.
     *    JMP FAR mem16:32 FF /5 Far jump indirect,
     *        with the target specified by a far pointer in memory.
     *
     * Intel64 does support 64bit offset.
     * Software Developer Manual Vol 2: states:
     *    FF /5 JMP m16:16 Jump far, absolute indirect,
     *        address given in m16:16
     *    FF /5 JMP m16:32 Jump far, absolute indirect,
     *        address given in m16:32.
     *    REX.W + FF /5 JMP m16:64 Jump far, absolute indirect,
     *        address given in m16:64.
     */
    pushq    $.Lafter_lret    # put return address on stack for unwinder
    xorl    %ebp, %ebp    # clear frame pointer
    movq    initial_code(%rip), %rax
    pushq    $__KERNEL_CS    # set correct cs
    pushq    %rax        # target address in negative space
    lretq
.Lafter_lret:
SYM_CODE_END(secondary_startup_64)
```

这里我们着重关心设置 `gs`寄存器的代码:

```
/* Set up %gs.
*
* The base of %gs always points to fixed_percpu_data. If the
* stack protector canary is enabled, it is located at %gs:40.
* Note that, on SMP, the boot cpu uses init data section until
* the per cpu areas are set up.
*/
movl    $MSR_GS_BASE,%ecx
movl    initial_gs(%rip),%eax
movl    initial_gs+4(%rip),%edx
wrmsr
```

`wrmsr`指令将`edx:eax`寄存器指定的地址中的数据写入到由`ecx`寄存器指定的`model specific register`中。由代码可以看到，`ecx`中的值是`$MSR_GS_BASE`，该值在`/source/arch/x86/include/uapi/asm/msr-index.h`中定义:

```
#define MSR_GS_BASE 0xc0000101
```

由此可见，`MSR_GS_BASE`定义了 `model specific register`的编号。由于 `cs`, `ds`, `es`,和 `ss`在64-bit模式中不再使用，这些寄存器中的值将会被忽略，但我们可以通过 `fs`和 `gs`寄存器来访问内存空间。`model specific register`提供了一种后门 `back door`来访问这些段寄存器，也让我们可以通过段寄存器 `fs`和 `gs`来访问64-bit的基地址。看起来这部分代码映射在 `GS.base`域中。再看到 `initial_gs`函数的定义:

```
// In /source/arch/x86/kernel/head_64.S#L265
SYM_DATA(initial_gs,    .quad INIT_PER_CPU_VAR(fixed_percpu_data))
```

可以发现，`initial_gs` 指向 `fixed_percpu_data`，这段代码将 `fixed_percpu_data`传递给 `INIT_PER_CPU_VAR`宏，后者只是给输入参数添加了 `init_per_cpu__`前缀而已。在此得出了符号 `init_per_cpu__fixed_percpu_data`。再看到`/source/arch/x86/kernel/vmlinux.lds.S`中有如下定义:

```
/*
 * Per-cpu symbols which need to be offset from __per_cpu_load
 * for the boot processor.
 */
#define INIT_PER_CPU(x) init_per_cpu__##x = ABSOLUTE(x) + __per_cpu_load
INIT_PER_CPU(gdt_page);
INIT_PER_CPU(fixed_percpu_data);
INIT_PER_CPU(irq_stack_backing_store);
```

这段代码告诉我们符号 `init_per_cpu__fixed_percpu_data`的地址将会是 `fixed_percpu_data + __per_cpu_load`。

`fixed_percpu_data`的定义出现在`/source/arch/x86/include/asm/processor.h#L437`中，其中的 `DECLARE_INIT_PER_CPU`宏展开后又调用了 `init_per_cpu_var`宏:

```
#ifdef CONFIG_X86_64
struct fixed_percpu_data {
    /*
     * GCC hardcodes the stack canary as %gs:40.  Since the
     * irq_stack is the object at %gs:0, we reserve the bottom
     * 48 bytes of the irq stack for the canary.
     */
    char        gs_base[40];
    // stack_canary 对于中断栈来说是一个用来验证栈是否已经被修改的栈保护者(stack protector)。
    // gs_base 是一个 40 字节的数组，GCC 要求 stack canary在被修正过的偏移量上
    // gs 的值在 x86_64 架构上必须是 40，在 x86 架构上必须是 20。
    unsigned long    stack_canary;
};

DECLARE_PER_CPU_FIRST(struct fixed_percpu_data, fixed_percpu_data) __visible;
DECLARE_INIT_PER_CPU(fixed_percpu_data);

// In /source/arch/x86/include/asm/percpu.h#L77
#define DECLARE_INIT_PER_CPU(var) 
       extern typeof(var) init_per_cpu_var(var)

// In /source/arch/x86/include/asm/percpu.h#L81
#ifdef CONFIG_X86_64_SMP
#define init_per_cpu_var(var)  init_per_cpu__##var
#else
#define init_per_cpu_var(var)  var
#endif

```

将所有的宏展开之后我们可以得到与之前相同的名称 `init_per_cpu__fixed_percpu_data`，但此时它不再只是一个符号，而成了一个变量。请注意表达式 `typeof(var)`,在此时 `var`是 `fixed_percpu_data`。

到此为止，我们定义了`ABSOLUTE(x) + __per_cpu_load`的第一个变量并且知道了它的地址。再看到第二个符号 `__per_cpu_load`，该符号定义在`/source/include/asm-generic/sections.h#L42`，这个符号定义了一系列 `per-cpu`变量:

```
extern char __per_cpu_load[], __per_cpu_start[], __per_cpu_end[];
```

这些符号代表了这一系列变量的数据区域的基地址，回到之前的代码中：

```
movl    $MSR_GS_BASE,%ecx
movl    initial_gs(%rip),%eax
movl    initial_gs+4(%rip),%edx
wrmsr
```

这里通过 `MSR_GS_BASE`指定了一个平台相关寄存器，然后将 `initial_gs`的64-bit地址放到了 `edx:eax`段寄存器中，然后执行 `wrmsr`指令，将 `init_per_cpu__fixed_percpu_data`的基地址放入了 `gs`寄存器，而这个地址将是中断栈的栈底地址。

在此之后我们将进入 `x86_64_start_kernel`函数中，此函数定义在`/source/arch/x86/kernel/head64.c`。在这个函数中，将完成最后的准备工作，之后就要进入到与平台无关的通用内核代码，在这个过程中，会将中断服务程序入口地址填写到早期 `Interrupt Descriptor Table`中。

### 中断服务程序入口地址关联( `x86_64_start_kernel`函数分析)

```
asmlinkage __visible void __init x86_64_start_kernel(char * real_mode_data)
{
    /*
     * Build-time sanity checks on the kernel image and module
     * area mappings. (these are purely build-time and produce no code)
     */
    BUILD_BUG_ON(MODULES_VADDR &lt; __START_KERNEL_map);
    BUILD_BUG_ON(MODULES_VADDR - __START_KERNEL_map &lt; KERNEL_IMAGE_SIZE);
    BUILD_BUG_ON(MODULES_LEN + KERNEL_IMAGE_SIZE &gt; 2*PUD_SIZE);
    BUILD_BUG_ON((__START_KERNEL_map &amp; ~PMD_MASK) != 0);
    BUILD_BUG_ON((MODULES_VADDR &amp; ~PMD_MASK) != 0);
    BUILD_BUG_ON(!(MODULES_VADDR &gt; __START_KERNEL));
    MAYBE_BUILD_BUG_ON(!(((MODULES_END - 1) &amp; PGDIR_MASK) ==
                (__START_KERNEL &amp; PGDIR_MASK)));
    BUILD_BUG_ON(__fix_to_virt(__end_of_fixed_addresses) &lt;= MODULES_END);

    cr4_init_shadow();

    /* Kill off the identity-map trampoline */
    reset_early_page_tables();

    clear_bss();

    clear_page(init_top_pgt);

    /*
     * SME support may update early_pmd_flags to include the memory
     * encryption mask, so it needs to be called before anything
     * that may generate a page fault.
     */
    sme_early_init();

    kasan_early_init();

    idt_setup_early_handler();

    copy_bootdata(__va(real_mode_data));

    /*
     * Load microcode early on BSP.
     */
    load_ucode_bsp();

    /* set init_top_pgt kernel high mapping*/
    init_top_pgt[511] = early_top_pgt[511];

    x86_64_start_reservations(real_mode_data);
}
```

可以发现，这个过程和`IDT`初始化相关的逻辑位于`idt_setup_early_handler()`，我们接下来来看这个函数：

```
// In /source/arch/x86/kernel/idt.c#L331

/**
 * idt_setup_early_handler - Initializes the idt table with early handlers
 */
void __init idt_setup_early_handler(void)
{
    int i;

    for (i = 0; i &lt; NUM_EXCEPTION_VECTORS; i++)
        set_intr_gate(i, early_idt_handler_array[i]);
#ifdef CONFIG_X86_32
    for ( ; i &lt; NR_VECTORS; i++)
        set_intr_gate(i, early_ignore_irq);
#endif
    load_idt(&amp;idt_descr);
}

extern const char early_idt_handler_array[NUM_EXCEPTION_VECTORS][EARLY_IDT_HANDLER_SIZE];
```

可以发现，中断服务程序的入口地址以数组的形式存储，其中 `NUM_EXCEPTION_VECTORS` 和 `EARLY_IDT_HANDLER_SIZE` 的定义如下:

```
#define NUM_EXCEPTION_VECTORS 32
#define EARLY_IDT_HANDLER_SIZE 9
```

因此，数组 `early_idt_handler_array` 存放着中断服务程序入口，其中每个入口占据9个字节。`early_idt_handlers` 定义在文件`/source/arch/x86/kernel/head_64.S`中。`early_idt_handler_array`也定义在这个文件中:

```
SYM_CODE_START(early_idt_handler_array)
    i = 0
    .rept NUM_EXCEPTION_VECTORS
    .if ((EXCEPTION_ERRCODE_MASK &gt;&gt; i) &amp; 1) == 0
        UNWIND_HINT_IRET_REGS
        pushq $0    # Dummy error code, to make stack frame uniform
    .else
        UNWIND_HINT_IRET_REGS offset=8
    .endif
    pushq $i        # 72(%rsp) Vector number
    jmp early_idt_handler_common
    UNWIND_HINT_IRET_REGS
    i = i + 1
    .fill early_idt_handler_array + i*EARLY_IDT_HANDLER_SIZE - ., 1, 0xcc
    .endr
    UNWIND_HINT_IRET_REGS offset=16
SYM_CODE_END(early_idt_handler_array)
```

这里使用 `.rept NUM_EXCEPTION_VECTORS` 填充了 `early_idt_handler_array` ，其中也包含了 `early_make_pgtable` 的中断服务函数入口。现在我们已经分析完了所有`x86-64`平台相关的代码，即将进入通用内核代码中。当然，我们之后还会在 `setup_arch` 函数中重新回到平台相关代码，但这已经是 `x86_64` 平台早期代码的最后部分。



## 0x04 参考链接

[【原】Linux内核中断系统处理机制-详细分析 – Bystander_J](https://blog.csdn.net/weixin_42092278/article/details/819894497)

[【原】GitBook – Linux Inside – 0xax](https://legacy.gitbook.com/book/0xax/linux-insides/details)

[【疑】中断解析](http://www.kerneltravel.net/journal/viii/01.htm)

(自本篇文章起，将会对所有的引用链接标注‘【原】’、‘【转/译】’、‘【疑】’三种标识，以表示引用的文章是否标明了原创或转载，若引用了其他作者转载的文章，将不再追溯至其原创作者，请注意，并非标明【疑】的均为非原创文章，仅表示文章出处未显示原创性，凡引用个人博客文章，除非文章标明转载或翻译，一律视为博主原创。)
