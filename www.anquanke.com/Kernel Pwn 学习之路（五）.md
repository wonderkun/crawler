> 原文链接: https://www.anquanke.com//post/id/203399 


# Kernel Pwn 学习之路（五）


                                阅读量   
                                **375488**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t012b90699683ce2270.jpg)](https://p4.ssl.qhimg.com/t012b90699683ce2270.jpg)



## 0x01 前言

由于关于Kernel安全的文章实在过于繁杂，本文有部分内容大篇幅或全文引用了参考文献，若出现此情况的，将在相关内容的开头予以说明，部分引用参考文献的将在文件结尾的参考链接中注明。

Kernel的相关知识以及一些实例在Kernel中的利用已经在`Kernel Pwn 学习之路(一)(二)`给予了说明

Kernel中内存管理的相关知识已经在`Kernel Pwn 学习之路(三)`给予了说明

本文主要接续`Kernel Pwn 学习之路(四)`，继续研究内核中断的相关机制。本文涉及到的所有`Linux Kernel`相关代码均基于`5.6.2`版本。

限于篇幅的原因，本文仅介绍了异常中断前处理，下一篇文章将深入中断服务函数，介绍其内部实现~

【传送门】：[Kernel Pwn 学习之路(一)](https://www.anquanke.com/post/id/201043)

【传送门】：[Kernel Pwn 学习之路(二)](https://www.anquanke.com/post/id/201454)

【传送门】：[Kernel Pwn 学习之路(三)](https://www.anquanke.com/post/id/202371)

【传送门】：[Kernel Pwn 学习之路(四)](https://www.anquanke.com/post/id/202988)



## 0x02 通用内核代码中的IDT相关处理

在上一篇文章的分析中，处理机进入了保护模式以及长模式，在平台相关代码中完成了`IDT`的初始化。在那之后流程将转移到通用内核代码，接下来我们进行分析通用内核代码中的IDT相关处理代码。

入口函数在`/source/init/main.c`中实现(这里省略不分析的函数)，这个函数将完成内核以`pid - 1`运行第一个`init`进程 之前的所有初始化工作。

```
asmlinkage __visible void __init start_kernel(void)
`{`
    char *command_line;
    char *after_dashes;

    ......

    local_irq_disable(); // Line 12
    early_boot_irqs_disabled = true;

    /*
     * Interrupts are still disabled. Do necessary setups, then
     * enable them.
     */

    ......

    setup_arch(&amp;command_line);  // Line 23

    ......

    boot_init_stack_canary();  // Line 123

    ......

    early_boot_irqs_disabled = false;
    local_irq_enable();   // Line 133

    ......

`}`
```

### 为中断栈设置`Stack Canary`

在`start_kernel()`的`line 123`调用了`boot_init_stack_canary()`来设置[canary](http://en.wikipedia.org/wiki/Stack_buffer_overflow#Stack_canaries)值来缓解中断栈溢出。

此函数在`/source/arch/x86/include/asm/stackprotector.h#L61`处实现

```
/* SPDX-License-Identifier: GPL-2.0 */
/*
 * GCC stack protector support.
 *
 * Stack protector works by putting predefined pattern at the start of
 * the stack frame and verifying that it hasn't been overwritten when
 * returning from the function.  The pattern is called stack canary
 * and unfortunately gcc requires it to be at a fixed offset from %gs.
 * On x86_64, the offset is 40 bytes and on x86_32 20 bytes.  x86_64
 * and x86_32 use segment registers differently and thus handles this
 * requirement differently.
 *
 * On x86_64, %gs is shared by percpu area and stack canary.  All
 * percpu symbols are zero based and %gs points to the base of percpu
 * area.  The first occupant of the percpu area is always
 * fixed_percpu_data which contains stack_canary at offset 40.  Userland
 * %gs is always saved and restored on kernel entry and exit using
 * swapgs, so stack protector doesn't add any complexity there.
 *
 * On x86_32, it's slightly more complicated.  As in x86_64, %gs is
 * used for userland TLS.  Unfortunately, some processors are much
 * slower at loading segment registers with different value when
 * entering and leaving the kernel, so the kernel uses %fs for percpu
 * area and manages %gs lazily so that %gs is switched only when
 * necessary, usually during task switch.
 *
 * As gcc requires the stack canary at %gs:20, %gs can't be managed
 * lazily if stack protector is enabled, so the kernel saves and
 * restores userland %gs on kernel entry and exit.  This behavior is
 * controlled by CONFIG_X86_32_LAZY_GS and accessors are defined in
 * system.h to hide the details.
 */

#ifndef _ASM_STACKPROTECTOR_H
#define _ASM_STACKPROTECTOR_H 1

#ifdef CONFIG_STACKPROTECTOR

#include &lt;asm/tsc.h&gt;
#include &lt;asm/processor.h&gt;
#include &lt;asm/percpu.h&gt;
#include &lt;asm/desc.h&gt;

#include &lt;linux/random.h&gt;
#include &lt;linux/sched.h&gt;

/*
 * 24 byte read-only segment initializer for stack canary.  Linker
 * can't handle the address bit shifting.  Address will be set in
 * head_32 for boot CPU and setup_per_cpu_areas() for others.
 */
#define GDT_STACK_CANARY_INIT                        
    [GDT_ENTRY_STACK_CANARY] = GDT_ENTRY_INIT(0x4090, 0, 0x18),

/*
 * Initialize the stackprotector canary value.
 *
 * NOTE: this must only be called from functions that never return,
 * and it must always be inlined.
 */
static __always_inline void boot_init_stack_canary(void)
`{`
    u64 canary;
    u64 tsc;

/* 
 * 如果设置了内核配置选项 CONFIG_X86_64 ，那么一开始将检查结构体 fixed_percpu_data 的状态
 * 这个结构体代表了 per-cpu 中断栈，其与 stack_canary 值中间有 40 个字节的 offset
 */
#ifdef CONFIG_X86_64
    BUILD_BUG_ON(offsetof(struct fixed_percpu_data, stack_canary) != 40);
#endif
    /*
     * We both use the random pool and the current TSC as a source
     * of randomness. The TSC only matters for very early init,
     * there it already has some randomness on most systems. Later
     * on during the bootup the random pool has true entropy too.
     * 使用随机数和时戳计数器计算新的 canary 值
     */
    get_random_bytes(&amp;canary, sizeof(canary));
    tsc = rdtsc();
    canary += tsc + (tsc &lt;&lt; 32UL);
    canary &amp;= CANARY_MASK;

    current-&gt;stack_canary = canary;
#ifdef CONFIG_X86_64
    // 通过 this_cpu_write 宏将 canary 值写入了 fixed_percpu_data 中:
    this_cpu_write(fixed_percpu_data.stack_canary, canary);
#else
    this_cpu_write(stack_canary.canary, canary);
#endif
`}`
......
#else    /* STACKPROTECTOR */
......
#endif    /* _ASM_STACKPROTECTOR_H */
```

它的实现取决于 `CONFIG_STACKPROTECTOR` 这个内核配置选项。如果该选项没有置位，那该函数将是一个空函数。

### <a class="reference-link" name="%E7%A6%81%E7%94%A8/%E5%90%AF%E7%94%A8%E6%9C%AC%E5%9C%B0%E4%B8%AD%E6%96%AD"></a>禁用/启用本地中断

在`start_kernel()`的`line 12`调用了`local_irq_disable()`来禁用本地中断。

在`start_kernel()`的`line 133`调用了`local_irq_enable()`来启用本地中断。

`local_irq_enable()`是一个宏定义，它定义在`/source/include/linux/irqflags.h#L109`

`local_irq_disable()`是一个宏定义，它定义在`/source/include/linux/irqflags.h#L111`

```
/*
 * The local_irq_*() APIs are equal to the raw_local_irq*()
 * if !TRACE_IRQFLAGS.
 */
#ifdef CONFIG_TRACE_IRQFLAGS
#define local_irq_enable() 
    do `{` trace_hardirqs_on(); raw_local_irq_enable(); `}` while (0)
#define local_irq_disable() 
    do `{` raw_local_irq_disable(); trace_hardirqs_off(); `}` while (0)

......

#else /* !CONFIG_TRACE_IRQFLAGS */

#define local_irq_enable()    do `{` raw_local_irq_enable(); `}` while (0)
#define local_irq_disable()    do `{` raw_local_irq_disable(); `}` while (0)

......

#endif /* CONFIG_TRACE_IRQFLAGS */
```

当 `CONFIG_TRACE_IRQFLAGS_SUPPORT` 选项置位时， `local_irq_*` 宏将同时调用 `trace_hardirqs_*` 函数。在Linux死锁检测模块[lockdep](http://lwn.net/Articles/321663/)中有一项功能 `irq-flags tracing`，它可以追踪 `hardirq` 和 `softirq` 的状态。在这种情况下， `lockdep` 死锁检测模块可以提供系统中关于硬/软中断的开/关事件的相关信息。

函数 `trace_hardirqs_*` 的定义位于`/source/kernel/trace/trace_preemptirq.c#L22`

```
void trace_hardirqs_on(void)
`{`
    if (this_cpu_read(tracing_irq_cpu)) `{`
        if (!in_nmi())
            trace_irq_enable_rcuidle(CALLER_ADDR0, CALLER_ADDR1);
        tracer_hardirqs_on(CALLER_ADDR0, CALLER_ADDR1);
        this_cpu_write(tracing_irq_cpu, 0);
    `}`

    lockdep_hardirqs_on(CALLER_ADDR0);
`}`
EXPORT_SYMBOL(trace_hardirqs_on);
NOKPROBE_SYMBOL(trace_hardirqs_on);

void trace_hardirqs_off(void)
`{`
    if (!this_cpu_read(tracing_irq_cpu)) `{`
        this_cpu_write(tracing_irq_cpu, 1);
        tracer_hardirqs_off(CALLER_ADDR0, CALLER_ADDR1);
        if (!in_nmi())
            trace_irq_disable_rcuidle(CALLER_ADDR0, CALLER_ADDR1);
    `}`

    lockdep_hardirqs_off(CALLER_ADDR0);
`}`
EXPORT_SYMBOL(trace_hardirqs_off);
NOKPROBE_SYMBOL(trace_hardirqs_off);
```

可见它只是调用了 `lockdep_hardirqs_*` 函数。 `lockdep_hardirqs_*` 函数,该函数检查了当前进程的 `hardirqs_enabled` 域，如果本次 `local_irq_disable` 调用是冗余的话，便使 `redundant_hardirqs_off` 域的值增长，否则便使 `hardirqs_off_events` 域的值增加。这两个域或其它与死锁检测模块 `lockdep` 统计相关的域定义在`/source/kernel/locking/lockdep_internals.h#L168`处的 `lockdep_stats` 结构体中:

```
/*
 * Various lockdep statistics.
 * We want them per cpu as they are often accessed in fast path
 * and we want to avoid too much cache bouncing.
 */
struct lockdep_stats `{`
    unsigned long  chain_lookup_hits;
    unsigned int   chain_lookup_misses;
    unsigned long  hardirqs_on_events;
    unsigned long  hardirqs_off_events;
    unsigned long  redundant_hardirqs_on;
    unsigned long  redundant_hardirqs_off;
    unsigned long  softirqs_on_events;
    unsigned long  softirqs_off_events;
    unsigned long  redundant_softirqs_on;
    unsigned long  redundant_softirqs_off;
    int            nr_unused_locks;
    unsigned int   nr_redundant_checks;
    unsigned int   nr_redundant;
    unsigned int   nr_cyclic_checks;
    unsigned int   nr_find_usage_forwards_checks;
    unsigned int   nr_find_usage_backwards_checks;

    /*
     * Per lock class locking operation stat counts
     */
    unsigned long lock_class_ops[MAX_LOCKDEP_KEYS];
`}`;
```

如果开启了 `CONFIG_DEBUG_LOCKDEP` 内核配置选项，`lockdep_stats_debug_show`函数会将所有的调试信息写入 `/proc/lockdep` 文件中。

接下来来分析 `raw_local_irq_disable` ，这个宏定义在`/source/include/linux/irqflags.h#L79`处实现，其展开后的样子是:

```
/*
 * Wrap the arch provided IRQ routines to provide appropriate checks.
 */
#define raw_local_irq_disable()        arch_local_irq_disable()
#define raw_local_irq_enable()        arch_local_irq_enable()

// In /source/arch/x86/include/asm/irqflags.h#L87

static inline notrace void arch_local_irq_disable(void)
`{`
    native_irq_disable();
`}`

static inline notrace void arch_local_irq_enable(void)
`{`
    native_irq_enable();
`}`

// In /source/arch/x86/include/asm/irqflags.h#L47

static inline void native_irq_disable(void)
`{`
    asm volatile("cli": : :"memory");
`}`

static inline void native_irq_enable(void)
`{`
    asm volatile("sti": : :"memory");
`}`
```

`cli/sti` 指令将清除/设置[IF](http://en.wikipedia.org/wiki/Interrupt_flag)标志位，这个标志位控制着处理器是否响应中断或异常。

早期版本的内核中提供了一个叫做 `cli` 的函数来禁用所有处理器的中断，该函数已经被移除，替代它的是 `local_irq_`{`enabled,disable`}`` 宏，用于禁用或启用当前处理器的中断。我们在调用 `local_irq_disable` 宏禁用中断以后，接着设置了变量值:

```
early_boot_irqs_disabled = true;
```

变量 `early_boot_irqs_disabled` 定义在文件`/source/include/linux/kernel.h`中:

```
extern bool early_boot_irqs_disabled;
```

并在另外的地方使用。例如在`/source/kernel/smp.c`中的 `smp_call_function_many` 函数中，通过这个变量来检查当前是否由于中断禁用而处于死锁状态:

```
WARN_ON_ONCE(cpu_online(this_cpu) &amp;&amp; irqs_disabled()
                     &amp;&amp; !oops_in_progress &amp;&amp; !early_boot_irqs_disabled);
```

### 早期 `trap gate` 初始化

在`start_kernel()`的`line 23`调用了`setup_arch()`来完成很多[架构相关的初始化工作](http://0xax.gitbooks.io/linux-insides/content/Initialization/linux-initialization-4.html)。

在 `setup_arch` 函数中与中断相关的第一个函数是 `idt_setup_early_traps`函数，其对`IDT`进行了中断服务函数入口的填充。

#### `idt_setup_early_traps`函数分析

`idt_setup_early_traps`函数于`/source/arch/x86/kernel/idt.c#L253`处实现

```
/**
 * idt_setup_early_traps - Initialize the idt table with early traps
 *
 * On X8664 these traps do not use interrupt stacks as they can't work
 * before cpu_init() is invoked and sets up TSS. The IST variants are
 * installed after that.
 */
void __init idt_setup_early_traps(void)
`{`
    idt_setup_from_table(idt_table, early_idts, ARRAY_SIZE(early_idts), true);
    load_idt(&amp;idt_descr);
`}`

// In /source/arch/x86/kernel/idt.c#L58

/*
 * Early traps running on the DEFAULT_STACK because the other interrupt
 * stacks work only after cpu_init().
 */
static const __initconst struct idt_data early_idts[] = `{`
    INTG(X86_TRAP_DB,        debug),
    SYSG(X86_TRAP_BP,        int3),
#ifdef CONFIG_X86_32
    INTG(X86_TRAP_PF,        page_fault),
#endif
`}`;

// In /source/arch/x86/kernel/idt.c#L218

static void idt_setup_from_table(gate_desc *idt, const struct idt_data *t, int size, bool sys)
`{`
    gate_desc desc;

    for (; size &gt; 0; t++, size--) `{`
        // 初始化 desc 的各个成员变量
        idt_init_desc(&amp;desc, t);
        // 将 desc 填入 idt
        write_idt_entry(idt, t-&gt;vector, &amp;desc);
        if (sys)
            set_bit(t-&gt;vector, system_vectors);
    `}`
`}`

// In /source/arch/x86/kernel/idt.c#L203

static inline void idt_init_desc(gate_desc *gate, const struct idt_data *d)
`{`
    unsigned long addr = (unsigned long) d-&gt;addr;

    gate-&gt;offset_low    = (u16) addr;
    gate-&gt;segment        = (u16) d-&gt;segment;
    gate-&gt;bits        = d-&gt;bits;
    gate-&gt;offset_middle    = (u16) (addr &gt;&gt; 16);
#ifdef CONFIG_X86_64
    gate-&gt;offset_high    = (u32) (addr &gt;&gt; 32);
    gate-&gt;reserved        = 0;
#endif
`}`
```

在`idt_setup_from_table`中，首先调用了`idt_init_desc`初始化了一个表示 `IDT` 入口项的 `gate_desc` 类型的结构体。

然后把这个中断门通过 `write_idt_entry` 宏填入了 `IDT` 中。这个宏展开后是 `native_write_idt_entry` ，其将中断门信息通过索引拷贝到了 `idt_table` 之中

```
// In /source/arch/x86/include/asm/desc.h#L128

#define write_idt_entry(dt, entry, g)        native_write_idt_entry(dt, entry, g)

// In /source/arch/x86/include/asm/desc.h#L141

static inline void native_write_idt_entry(gate_desc *idt, int entry, const gate_desc *gate)
`{`
    memcpy(&amp;idt[entry], gate, sizeof(*gate));
`}`
```

#### 关于 `gate_desc` 结构体

`gate_desc` 结构体是一个在 `x86` 中被称为门的 16 字节数组。它拥有下面的结构：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-09-%E5%9B%BE%E7%89%87.png)

`gate_desc`在`/source/arch/x86/include/asm/desc_defs.h#L88`中定义

```
typedef struct gate_struct gate_desc;
```

`gate_struct`在`/source/arch/x86/include/asm/desc_defs.h#L77`中定义

```
struct gate_struct `{`
    u16        offset_low;
    u16        segment;
    struct idt_bits    bits;
    u16        offset_middle;
#ifdef CONFIG_X86_64
    u32        offset_high;
    u32        reserved;
#endif
`}` __attribute__((packed));

struct idt_bits `{`
    u16        ist    : 3,
            zero    : 5,
            type    : 5,
            dpl    : 2,
            p    : 1;
`}` __attribute__((packed));
```

为了能从中断号得到对应的`IDT`，处理器把异常和中断向量分为 16 个级别。处理器处理异常和中断的发生就像它看到 `call` 指令时处理一个程序调用一样。处理器使用中断或异常的唯一的识别码(即中断号)作为索引来寻找对应的 `IDT` 的条目。

在`IDT`中的 `IDT` 条目由下面的域组成：
<li>
`0-15` bits – 段选择器偏移，处理器用它作为中断处理程序的入口指针基址。</li>
<li>
`16-31` bits – 段选择器基址，包含中断处理程序入口指针。</li>
<li>
`IST` – 在 `x86_64` 上的一个新的机制。</li>
<li>
`Type` – 描述了 `IDT` 条目的类型。(即：中断门、任务门、陷阱门)</li>
<li>
`DPL` – 描述符特权等级。</li>
<li>
`P` – 段存在标志。</li>
<li>
`48-63` bits – 中断处理程序基址的第二部分。</li>
<li>
`64-95` bits – 中断处理程序基址的第三部分。</li>
<li>
`96-127` bits – CPU 保留位。</li>


## 0x03 异常处理前处理

我们在之前讨论了`IDT`的初始化过程，现在我们来详细的看一看异常处理究竟是如何执行的。

首先我们注意到给`idt_setup_from_table`传入的参数有一项为`early_idts`数组，其中定义了`DEBUG`、`INT3`(、`page_fault`)两种异常(`32`位架构时，额外定义`page_fault`异常)。也就是说，在`cpu_init()`执行前，内核就已经能够处理这两种异常，那么我们就以这两种异常为例进行分析。

### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E5%BC%82%E5%B8%B8%E5%92%8C%E6%96%AD%E7%82%B9%E5%BC%82%E5%B8%B8"></a>调试异常和断点异常

第一个异常 —— `debug`异常(助记符为`#DB`)，通常在在调试事件发生异常时报告。

例如：尝试更改[调试寄存器](http://en.wikipedia.org/wiki/X86_debug_register)的内容。(调试寄存器是`x86`从[英特尔80386](http://en.wikipedia.org/wiki/Intel_80386)处理器开始出现在处理器中的特殊寄存器，从此它的名称可以确定这些寄存器的主要用途是调试)这些寄存器允许在代码上设置断点，并读取或写入数据以对其进行跟踪。**调试寄存器只能在特权模式下访问，以任何其他特权级别执行时尝试读取或写入调试寄存器都会导致[一般保护错误异常(General_protection_fault)](https://en.wikipedia.org/wiki/General_protection_fault)。**因此使用`set_intr_gate_ist`初始化`#DB`异常，而不是`set_system_intr_gate_ist`。

`#DB`异常的`Verctor`编号为`1`(也称为`X86_TRAP_DB`），并且正如我们在规范中看到的那样，该异常没有错误代码

<th style="text-align: center;">Verctor 编号</th><th style="text-align: center;">异常助记符</th><th style="text-align: center;">异常描述</th><th style="text-align: center;">异常类型</th><th style="text-align: center;">错误代码</th>
|------
<td style="text-align: center;">1</td><td style="text-align: center;">#DB</td><td style="text-align: center;">Reserved</td><td style="text-align: center;">F/T</td><td style="text-align: center;">NO</td>

第二个异常 —— `breakpoint`异常(助记符为`#BP`)，当处理器执行[int 3](http://en.wikipedia.org/wiki/INT_(x86_instruction)#INT_3)指令时发生异常。与`DB`异常不同，该`#BP`异常可能发生在用户空间中。我们可以将其添加到代码中的任何位置，例如，让我们看一下简单的程序：

```
// breakpoint.c
#include &lt;stdio.h&gt;

int main() `{`
    int i;
    while (i &lt; 6)`{`
        printf("i equal to: %dn", i);
        __asm__("int3");
        ++i;
    `}`
`}`
```

如果我们编译并运行该程序，我们将看到以下输出：

```
$ gcc breakpoint.c -o breakpoint
i equal to: 0
Trace/breakpoint trap
```

但是，如果将其与gdb一起运行，我们将看到断点并可以继续执行程序：

```
$ gdb breakpoint
...
...
...
(gdb) run
Starting program: /home/alex/breakpoints 
i equal to: 0

Program received signal SIGTRAP, Trace/breakpoint trap.
0x0000000000400585 in main ()
=&gt; 0x0000000000400585 &lt;main+31&gt;:    83 45 fc 01    add    DWORD PTR [rbp-0x4],0x1
(gdb) c
Continuing.
i equal to: 1

Program received signal SIGTRAP, Trace/breakpoint trap.
0x0000000000400585 in main ()
=&gt; 0x0000000000400585 &lt;main+31&gt;:    83 45 fc 01    add    DWORD PTR [rbp-0x4],0x1
(gdb) c
Continuing.
i equal to: 2

Program received signal SIGTRAP, Trace/breakpoint trap.
0x0000000000400585 in main ()
=&gt; 0x0000000000400585 &lt;main+31&gt;:    83 45 fc 01    add    DWORD PTR [rbp-0x4],0x1
...
...
...
```

### <a class="reference-link" name="%E5%BC%82%E5%B8%B8%E5%A4%84%E7%90%86%E7%A8%8B%E5%BA%8F%E8%B0%83%E7%94%A8%E5%89%8D%E5%87%86%E5%A4%87"></a>异常处理程序调用前准备

`#DB`和`#BP`的异常处理程序位于`/source/arch/x86/include/asm/traps.h#L13`

```
asmlinkage void divide_error(void);
asmlinkage void debug(void);
asmlinkage void nmi(void);
asmlinkage void int3(void);
asmlinkage void overflow(void);
asmlinkage void bounds(void);
asmlinkage void invalid_op(void);
asmlinkage void device_not_available(void);
```

`asmlinkage`是[gcc](http://en.wikipedia.org/wiki/GNU_Compiler_Collection)的[特殊说明符](http://en.wikipedia.org/wiki/GNU_Compiler_Collection)。实际上，对于`C`从汇编码中调用的函数，我们需要显式声明函数调用约定。如果函数使用`asmlinkage`描述符创建，`gcc`将从堆栈中检索参数以编译该函数。

因此，两个处理程序都在带有`idtentry`宏的`/arch/x86/entry/entry_64.S`中定义：

```
idtentry debug do_debug has_error_code=0 paranoid=1 shift_ist=IST_INDEX_DB ist_offset=DB_STACK_OFFSET
idtentry int3 do_int3 has_error_code=0 create_gap=1
```

每个异常处理程序可以由两部分组成：
- 第一部分是通用部分，所有异常处理程序都相同。异常处理程序应将[通用寄存器](https://en.wikipedia.org/wiki/Processor_register)保存在堆栈上，如果异常来自用户空间，则应切换到内核堆栈，并将控制权转移到异常处理程序的第二部分。
- 异常处理程序的第二部分完成的工作取决于具体的异常。例如，页面错误异常处理程序应找到给定地址的虚拟页面，无效的操作码异常处理程序应发送`SIGILL` [信号](https://en.wikipedia.org/wiki/Unix_signal)等。
现在来分析`idtentry`宏的实现。如我们所见，该宏采用七个参数：
<li>
`sym` – 定义全局符号，该符号`.globl name`将作为异常处理程序的入口。</li>
<li>
`do_sym` – 符号名称，这表示异常处理程序的辅助条目。</li>
<li>
`has_error_code` – 异常是否存在错误代码。</li>
最后四个参数是可选的：
<li>
`paranoid` – 非零表示可以使用用户`GSBASE`和/或用户`CR3`从内核模式调用此中断向量。</li>
<li>
`shift_ist` – 如果内核模式下的中断条目使用`IST`堆栈，以便使得嵌套的中断条目获得新的中断栈，则置位。 (这是针对#DB的，它具有递归的逻辑。(这很糟糕！))</li>
<li>
`create_gap` – 从内核模式进入此中断处理程序时，创建一个6字大小的堆栈间隙。</li>
<li>
`read_cr2` – 在调用任何C代码之前，将CR2加载到第3个参数中</li>
`.idtentry`宏的定义：(实现在`/source/arch/x86/entry/entry_64.S#L970`)

```
/**
 * idtentry - Generate an IDT entry stub
 * @sym:        Name of the generated entry point
 * @do_sym:        C function to be called
 * @has_error_code:    True if this IDT vector has an error code on the stack
 * @paranoid:        non-zero means that this vector may be invoked from
 *            kernel mode with user GSBASE and/or user CR3.
 *            2 is special -- see below.
 * @shift_ist:        Set to an IST index if entries from kernel mode should
 *            decrement the IST stack so that nested entries get a
 *            fresh stack.  (This is for #DB, which has a nasty habit
 *            of recursing.)
 * @create_gap:        create a 6-word stack gap when coming from kernel mode.
 * @read_cr2:        load CR2 into the 3rd argument; done before calling any C code
 *
 * idtentry generates an IDT stub that sets up a usable kernel context,
 * creates struct pt_regs, and calls @do_sym.  The stub has the following
 * special behaviors:
 *
 * On an entry from user mode, the stub switches from the trampoline or
 * IST stack to the normal thread stack.  On an exit to user mode, the
 * normal exit-to-usermode path is invoked.
 *
 * On an exit to kernel mode, if @paranoid == 0, we check for preemption,
 * whereas we omit the preemption check if @paranoid != 0.  This is purely
 * because the implementation is simpler this way.  The kernel only needs
 * to check for asynchronous kernel preemption when IRQ handlers return.
 *
 * If @paranoid == 0, then the stub will handle IRET faults by pretending
 * that the fault came from user mode.  It will handle gs_change faults by
 * pretending that the fault happened with kernel GSBASE.  Since this handling
 * is omitted for @paranoid != 0, the #GP, #SS, and #NP stubs must have
 * @paranoid == 0.  This special handling will do the wrong thing for
 * espfix-induced #DF on IRET, so #DF must not use @paranoid == 0.
 *
 * @paranoid == 2 is special: the stub will never switch stacks.  This is for
 * #DF: if the thread stack is somehow unusable, we'll still get a useful OOPS.
 */
.macro idtentry sym do_sym has_error_code:req paranoid=0 shift_ist=-1 ist_offset=0 create_gap=0 read_cr2=0
SYM_CODE_START(sym)
    UNWIND_HINT_IRET_REGS offset=has_error_code*8

    /* Sanity check */
    .if shift_ist != -1 &amp;&amp; paranoid != 1
    .error "using shift_ist requires paranoid=1"
    .endif

    .if create_gap &amp;&amp; paranoid
    .error "using create_gap requires paranoid=0"
    .endif

    ASM_CLAC

    .if has_error_code == 0
    pushq    $-1                /* ORIG_RAX: no syscall to restart */
    .endif

    .if paranoid == 1
    testb    $3, CS-ORIG_RAX(%rsp)        /* If coming from userspace, switch stacks */
    jnz    .Lfrom_usermode_switch_stack_@
    .endif

    .if create_gap == 1
    /*
     * If coming from kernel space, create a 6-word gap to allow the
     * int3 handler to emulate a call instruction.
     */
    testb    $3, CS-ORIG_RAX(%rsp)
    jnz    .Lfrom_usermode_no_gap_@
    .rept    6
    pushq    5*8(%rsp)
    .endr
    UNWIND_HINT_IRET_REGS offset=8
.Lfrom_usermode_no_gap_@:
    .endif

    idtentry_part do_sym, has_error_code, read_cr2, paranoid, shift_ist, ist_offset

    .if paranoid == 1
    /*
     * Entry from userspace.  Switch stacks and treat it
     * as a normal entry.  This means that paranoid handlers
     * run in real process context if user_mode(regs).
     */
.Lfrom_usermode_switch_stack_@:
    idtentry_part do_sym, has_error_code, read_cr2, paranoid=0
    .endif

_ASM_NOKPROBE(sym)
SYM_CODE_END(sym)
.endm
```

在分析`idtentry`宏的内部实现之前，首先明确，这是发生异常时的堆栈状态：

```
+------------+
+40 | %SS        |
+32 | %RSP       |
+24 | %RFLAGS    |
+16 | %CS        |
 +8 | %RIP       |
  0 | ERROR CODE | &lt;-- %RSP
    +------------+
```

然后结合`#DB`和`#BP`的异常处理程序定义来看`idtentry`宏的内部实现：

```
idtentry debug do_debug has_error_code=0 paranoid=1 shift_ist=IST_INDEX_DB ist_offset=DB_STACK_OFFSET
idtentry int3 do_int3 has_error_code=0 create_gap=1
```
<li>编译器将生成带有`debug`和`int3`名称的两个例程，并且经过一些准备后，这两个异常处理程序将分别调用`do_debug`和`do_int3`辅助处理程序。第三个参数定义了错误代码是否存在，此处的两个异常都没有错误代码。如上面的堆栈结构所示，如果有异常，处理器会将错误代码压入堆栈。那么我们可以很直观的看出，对于提供错误代码的异常和未提供错误代码的异常，堆栈的外观会有所不同。这就是为什么`idtentry`宏的实现中，在异常未提供错误代码的情况下将会把”伪造”的错误代码放入堆栈：
<pre><code class="lang-assembly">.if has_error_code == 0
pushq    $-1                /* ORIG_RAX: no syscall to restart */
.endif
</code></pre>
但这不仅仅是一个”伪造”的错误代码，`-1`还会代表无效的系统调用号，因此这不会触发系统调用的重新启动逻辑。
</li>
- 接下来的第一个可选参数 – `shift_ist`参数将表征异常处理程序是否使用了`IST`栈。系统中的每个内核线程都有自己的堆栈。除了这些堆栈外，还有一些专用堆栈与系统中的每个处理器相关联，异常栈就是这类专用堆栈之一。[x86_64](https://en.wikipedia.org/wiki/X86-64)架构提供了一个新机制，它被称为`Interrupt Stack Table`(`IST`机制)。此机制允许在发生指定事件时(例如`double fault`之类的原子异常等)切换到新堆栈。`shift_ist`参数就用来标识是否需要使用`IST`机制为异常处理程序创建一个新的堆栈。
<li>第二个可选参数 – `paranoid`定义了一种方法，可以帮助我们知道服务程序的调用是来自用户空间还是来自异常处理程序。确定这一点的最简单方法是通过在`CS`段寄存器中的`CPL`(`Current Privilege Level`)。如果等于`3`，则来自用户空间，如果为零，则来自内核空间。
<pre><code class="lang-asm">   .if paranoid == 1
     testb    $3, CS-ORIG_RAX(%rsp)        /* If coming from userspace, switch stacks */
     jnz    .Lfrom_usermode_switch_stack_@
   .endif
</code></pre>
但是不幸的是，这种方法不能提供100％的保证。如内核文档中所述：
<blockquote>如果我们处于 NMI/MCE/DEBUG 以及其他任何 super-atomic 入口上下文中，那么在正常入口将CS写入堆栈之后，执行SWAPGS之前可能已经触发异常，那么检查GS的唯一安全方法是一种速度较慢的方法：RDMSR。</blockquote>
换言之，例如`NMI`(不可屏蔽中断)发生在[swapgs](http://www.felixcloutier.com/x86/SWAPGS.html)指令的内部。这样的话，我们应该检查`MSR_GS_BASE`的值，该寄存器存储指向每个cpu区域开始的指针。因此，要检查我们是否来自用户空间，我们应该检查`MSR_GS_BASE`，如果它是负数，则我们来自内核空间，否则我们来自用户空间：
<pre><code class="lang-assembly">  movl $MSR_GS_BASE,%ecx
  rdmsr
  testl %edx,%edx
  js 1f
</code></pre>
在前两行代码中，我们将`MSR_GS_BASE`的值按`edx:eax`成对读取，我们不能为用户空间中的`gs`寄存器设置负值。但是从另一方面说，我们知道物理内存的直接映射是从`0xffff880000000000`虚拟地址开始的。这样，`MSR_GS_BASE`将包含从`0xffff880000000000`到的地址`0xffffc7ffffffffff`。而后`rdmsr`指令将被执行，`%edx`寄存器中可能的最小值将会是`0xffff8800`也就是`-30720`(`unsigned 4 bytes`)。这就是`gs`指向`per-cpu`区域开始的内核空间包含负值的原因。
</li>
- 在为通用寄存器分配空间之后，我们进行一些检查以了解异常是否来自用户空间，如果是，则应移回中断的进程堆栈或保留在异常堆栈上：
```
.if paranoid
    .if paranoid == 1
        testb    $3, CS(%rsp)
        jnz    1f
    .endif
    call    paranoid_entry
.else
    call    error_entry
.endif
```

让我们考虑一下所有这些情况。

### <a class="reference-link" name="%E5%BD%93%E7%94%A8%E6%88%B7%E7%A9%BA%E9%97%B4%E4%B8%AD%E5%8F%91%E7%94%9F%E5%BC%82%E5%B8%B8%E6%97%B6"></a>当用户空间中发生异常时

可以看到，当用户空间中发生异常时，内核会执行如下处理逻辑：

```
.if paranoid == 1
    testb    $3, CS-ORIG_RAX(%rsp)        /* If coming from userspace, switch stacks */
    jnz    .Lfrom_usermode_switch_stack_@
.endif
.if paranoid == 1
    /*
     * Entry from userspace.  Switch stacks and treat it
     * as a normal entry.  This means that paranoid handlers
     * run in real process context if user_mode(regs).
     */
.Lfrom_usermode_switch_stack_@:
    idtentry_part do_sym, has_error_code, read_cr2, paranoid=0
.endif
```

也就是核心是执行`idtentry_part do_sym, has_error_code, read_cr2, paranoid=0`

那么关于`idtentry_part`在`/source/arch/x86/entry/entry_64.S#L868`处实现

```
/*
 * Exception entry points.
 */
#define CPU_TSS_IST(x) PER_CPU_VAR(cpu_tss_rw) + (TSS_ist + (x) * 8)

.macro idtentry_part do_sym, has_error_code:req, read_cr2:req, paranoid:req, shift_ist=-1, ist_offset=0

    .if paranoid
        call    paranoid_entry
    /* returned flag: ebx=0: need swapgs on exit, ebx=1: don't need it */
    .else
        call    error_entry
    .endif
    UNWIND_HINT_REGS

    .if read_cr2
    /*
     * Store CR2 early so subsequent faults cannot clobber it. Use R12 as
     * intermediate storage as RDX can be clobbered in enter_from_user_mode().
     * GET_CR2_INTO can clobber RAX.
     */
    GET_CR2_INTO(%r12);
    .endif

    .if shift_ist != -1
    TRACE_IRQS_OFF_DEBUG            /* reload IDT in case of recursion */
    .else
    TRACE_IRQS_OFF
    .endif

    .if paranoid == 0
    testb    $3, CS(%rsp)
    jz    .Lfrom_kernel_no_context_tracking_@
    CALL_enter_from_user_mode
.Lfrom_kernel_no_context_tracking_@:
    .endif

    movq    %rsp, %rdi            /* pt_regs pointer */

    .if has_error_code
    movq    ORIG_RAX(%rsp), %rsi        /* get error code */
    movq    $-1, ORIG_RAX(%rsp)        /* no syscall to restart */
    .else
    xorl    %esi, %esi            /* no error code */
    .endif

    .if shift_ist != -1
    subq    $ist_offset, CPU_TSS_IST(shift_ist)
    .endif

    .if read_cr2
    movq    %r12, %rdx            /* Move CR2 into 3rd argument */
    .endif

    call    do_sym

    .if shift_ist != -1
    addq    $ist_offset, CPU_TSS_IST(shift_ist)
    .endif

    .if paranoid
    /* this procedure expect "no swapgs" flag in ebx */
    jmp    paranoid_exit
    .else
    jmp    error_exit
    .endif

.endm
```

#### <a class="reference-link" name="error_entry%E5%A4%84%E7%90%86%E5%88%86%E6%9E%90"></a>error_entry处理分析

假设我们此时进入了`error_entry`的处理逻辑，它在`/source/arch/x86/entry/entry_64.S#L1287`处实现：

```
/*
 * Save all registers in pt_regs, and switch GS if needed.
 */
SYM_CODE_START_LOCAL(error_entry)
    UNWIND_HINT_FUNC
    cld
    PUSH_AND_CLEAR_REGS save_ret=1
    ENCODE_FRAME_POINTER 8
    testb    $3, CS+8(%rsp)
    jz    .Lerror_kernelspace

    /*
     * We entered from user mode or we're pretending to have entered
     * from user mode due to an IRET fault.
     */
    SWAPGS
    FENCE_SWAPGS_USER_ENTRY
    /* We have user CR3.  Change to kernel CR3. */
    SWITCH_TO_KERNEL_CR3 scratch_reg=%rax

.Lerror_entry_from_usermode_after_swapgs:
    /* Put us onto the real thread stack. */
    popq    %r12                /* save return addr in %12 */
    movq    %rsp, %rdi            /* arg0 = pt_regs pointer */
    call    sync_regs
    movq    %rax, %rsp            /* switch stack */
    ENCODE_FRAME_POINTER
    pushq    %r12
    ret

.Lerror_entry_done_lfence:
    FENCE_SWAPGS_KERNEL_ENTRY
.Lerror_entry_done:
    ret

    /*
     * There are two places in the kernel that can potentially fault with
     * usergs. Handle them here.  B stepping K8s sometimes report a
     * truncated RIP for IRET exceptions returning to compat mode. Check
     * for these here too.
     */
.Lerror_kernelspace:
    leaq    native_irq_return_iret(%rip), %rcx
    cmpq    %rcx, RIP+8(%rsp)
    je    .Lerror_bad_iret
    movl    %ecx, %eax            /* zero extend */
    cmpq    %rax, RIP+8(%rsp)
    je    .Lbstep_iret
    cmpq    $.Lgs_change, RIP+8(%rsp)
    jne    .Lerror_entry_done_lfence

    /*
     * hack: .Lgs_change can fail with user gsbase.  If this happens, fix up
     * gsbase and proceed.  We'll fix up the exception and land in
     * .Lgs_change's error handler with kernel gsbase.
     */
    SWAPGS
    FENCE_SWAPGS_USER_ENTRY
    SWITCH_TO_KERNEL_CR3 scratch_reg=%rax
    jmp .Lerror_entry_done

.Lbstep_iret:
    /* Fix truncated RIP */
    movq    %rcx, RIP+8(%rsp)
    /* fall through */

.Lerror_bad_iret:
    /*
     * We came from an IRET to user mode, so we have user
     * gsbase and CR3.  Switch to kernel gsbase and CR3:
     */
    SWAPGS
    FENCE_SWAPGS_USER_ENTRY
    SWITCH_TO_KERNEL_CR3 scratch_reg=%rax

    /*
     * Pretend that the exception came from user mode: set up pt_regs
     * as if we faulted immediately after IRET.
     */
    mov    %rsp, %rdi
    call    fixup_bad_iret
    mov    %rax, %rsp
    jmp    .Lerror_entry_from_usermode_after_swapgs
SYM_CODE_END(error_entry)
```

##### <a class="reference-link" name="%E4%BF%9D%E5%AD%98%E7%8E%B0%E5%9C%BA(%E5%82%A8%E5%AD%98%E6%89%80%E6%9C%89%E9%80%9A%E7%94%A8%E5%AF%84%E5%AD%98%E5%99%A8)"></a>保存现场(储存所有通用寄存器)

首先内核会把返回地址保存在`R12`寄存器中，随即会调用PUSH_AND_CLEAR_REGS将通用寄存器的值存储在中断栈上：

首先内核会调用`PUSH_AND_CLEAR_REGS`将通用寄存器的值存储在中断栈上：

```
.macro PUSH_AND_CLEAR_REGS rdx=%rdx rax=%rax save_ret=0
    /*
     * Push registers and sanitize registers of values that a
     * speculation attack might otherwise want to exploit. The
     * lower registers are likely clobbered well before they
     * could be put to use in a speculative execution gadget.
     * Interleave XOR with PUSH for better uop scheduling:
     */
    .if save_ret
    pushq    %rsi        /* pt_regs-&gt;si */
    movq    8(%rsp), %rsi    /* temporarily store the return address in %rsi */
    movq    %rdi, 8(%rsp)    /* pt_regs-&gt;di (overwriting original return address) */
    .else
    pushq   %rdi        /* pt_regs-&gt;di */
    pushq   %rsi        /* pt_regs-&gt;si */
    .endif
    pushq    rdx        /* pt_regs-&gt;dx */
    xorl    %edx, %edx    /* nospec   dx */
    pushq   %rcx        /* pt_regs-&gt;cx */
    xorl    %ecx, %ecx    /* nospec   cx */
    pushq   rax        /* pt_regs-&gt;ax */
    pushq   %r8        /* pt_regs-&gt;r8 */
    xorl    %r8d, %r8d    /* nospec   r8 */
    pushq   %r9        /* pt_regs-&gt;r9 */
    xorl    %r9d, %r9d    /* nospec   r9 */
    pushq   %r10        /* pt_regs-&gt;r10 */
    xorl    %r10d, %r10d    /* nospec   r10 */
    pushq   %r11        /* pt_regs-&gt;r11 */
    xorl    %r11d, %r11d    /* nospec   r11*/
    pushq    %rbx        /* pt_regs-&gt;rbx */
    xorl    %ebx, %ebx    /* nospec   rbx*/
    pushq    %rbp        /* pt_regs-&gt;rbp */
    xorl    %ebp, %ebp    /* nospec   rbp*/
    pushq    %r12        /* pt_regs-&gt;r12 */
    xorl    %r12d, %r12d    /* nospec   r12*/
    pushq    %r13        /* pt_regs-&gt;r13 */
    xorl    %r13d, %r13d    /* nospec   r13*/
    pushq    %r14        /* pt_regs-&gt;r14 */
    xorl    %r14d, %r14d    /* nospec   r14*/
    pushq    %r15        /* pt_regs-&gt;r15 */
    xorl    %r15d, %r15d    /* nospec   r15*/
    UNWIND_HINT_REGS
    .if save_ret
    pushq    %rsi        /* return address on top of stack */
    .endif
.endm
```

执行后，堆栈将如下所示：

```
+------------+
+160 | %SS        |
+152 | %RSP       |
+144 | %RFLAGS    |
+136 | %CS        |
+128 | %RIP       |
+120 | ERROR CODE |
     |------------|
+112 | %RDI       |
+104 | %RSI       |
 +96 | %RDX       |
 +88 | %RCX       |
 +80 | %RAX       |
 +72 | %R8        |
 +64 | %R9        |
 +56 | %R10       |
 +48 | %R11       |
 +40 | %RBX       |
 +32 | %RBP       |
 +24 | %R12       |
 +16 | %R13       |
  +8 | %R14       |
  +0 | %R15       | &lt;- %RSP
     +------------+
```

##### 再次检查`CPL`

内核将通用寄存器保存在堆栈中之后，因为正如官方文档中描述的那样，一旦发生`%RIP`中断，则有可能发生错误，我们应该使用以下命令再次检查是否来自用户空间空间：

```
testb  $3, CS+8(%rsp)
jz  .Lerror_kernelspace
```

##### &lt;a name=”初始化`GS`寄存器” class=”reference-link”&gt;初始化`GS`寄存器

接下来将执行[SWAPGS](http://www.felixcloutier.com/x86/SWAPGS.html)指令，这将会交换`MSR_KERNEL_GS_BASE`和`MSR_GS_BASE`中的值。从这一刻起，`%gs`寄存器将指向内核结构的基址。

##### 获取运行栈的栈指针(`sync_regs`函数分析)

接下来将会进入`.Lerror_entry_from_usermode_after_swapgs:`中：

```
movq    %rsp, %rdi
call    sync_regs
```

在这里，我们将堆栈的基址指针置入`%rdi`寄存器这将作为`sync_regs`函数的参数。

接下来我们来分析`sync_regs`函数：(在`/source/arch/x86/kernel/traps.c#L613`中实现)

```
/*
 * Help handler running on a per-cpu (IST or entry trampoline) stack
 * to switch to the normal thread stack if the interrupted code was in
 * user mode. The actual stack switch is done in entry_64.S
 */
asmlinkage __visible notrace struct pt_regs *sync_regs(struct pt_regs *eregs)
`{`
    struct pt_regs *regs = (struct pt_regs *)this_cpu_read(cpu_current_top_of_stack) - 1;
    if (regs != eregs)
        *regs = *eregs;
    return regs;
`}`
NOKPROBE_SYMBOL(sync_regs);

// In /source/include/linux/percpu-defs.h#L507

#define this_cpu_read(pcp)        __pcpu_size_call_return(this_cpu_read_, pcp)
```

这将会获取运行栈的栈指针将其存储在中断栈中并返回，这意味着异常处理程序将在实际流程上下文中运行。

##### <a class="reference-link" name="%E6%A0%88%E5%88%87%E6%8D%A2"></a>栈切换

接下来我们进行栈切换操作

正如我们来自用户空间一样，这意味着异常处理程序将在实际流程上下文中运行。从堆栈指针中获取堆栈指针后，`sync_regs`我们切换堆栈：

```
movq    %rax, %rsp
```

然后内核从`R12`中取出返回地址，返回上级函数

#### <a class="reference-link" name="%E5%8F%AF%E9%80%89%E5%8F%82%E6%95%B0%E9%80%BB%E8%BE%91%E5%88%86%E6%9E%90"></a>可选参数逻辑分析

在用户空间发生异常的处理逻辑下，接下来只需要处理以下三个选项`has_error_code, read_cr2, paranoid=0`

```
.if read_cr2
    /*
     * Store CR2 early so subsequent faults cannot clobber it. Use R12 as
     * intermediate storage as RDX can be clobbered in enter_from_user_mode().
     * GET_CR2_INTO can clobber RAX.
     */
    GET_CR2_INTO(%r12);
    .endif

    .if shift_ist != -1
        ......(代码省略)
    .endif

    .if paranoid == 0
    testb    $3, CS(%rsp)
    jz    .Lfrom_kernel_no_context_tracking_@
    CALL_enter_from_user_mode
.Lfrom_kernel_no_context_tracking_@:
    .endif

    movq    %rsp, %rdi            /* pt_regs pointer */

    .if has_error_code
    movq    ORIG_RAX(%rsp), %rsi        /* get error code */
    movq    $-1, ORIG_RAX(%rsp)        /* no syscall to restart */
    .else
    xorl    %esi, %esi            /* no error code */
    .endif

    .if shift_ist != -1
        ......(代码省略)
    .endif

    .if read_cr2
    movq    %r12, %rdx            /* Move CR2 into 3rd argument */
    .endif

    call    do_sym

    .if shift_ist != -1
    addq    $ist_offset, CPU_TSS_IST(shift_ist)
    .endif

    .if paranoid
    /* this procedure expect "no swapgs" flag in ebx */
    jmp    paranoid_exit
    .else
    jmp    error_exit
    .endif
```

##### &lt;a name=”若`read_cr2`被设置” class=”reference-link”&gt;若`read_cr2`被设置

`read_cr2`相关的逻辑有两处，第一处是

```
.if read_cr2
    /*
     * Store CR2 early so subsequent faults cannot clobber it. Use R12 as
     * intermediate storage as RDX can be clobbered in enter_from_user_mode().
     * GET_CR2_INTO can clobber RAX.
     */
    GET_CR2_INTO(%r12);
.endif

# In /source/arch/x86/entry/calling.h#L365

#define GET_CR2_INTO(reg) GET_CR2_INTO_AX ; _ASM_MOV %_ASM_AX, reg
```

作用是存储`CR2`寄存器的值到`R12`寄存器。

第二处逻辑是

```
.if read_cr2
    movq    %r12, %rdx            /* Move CR2 into 3rd argument */
.endif
```

作用是存储`R12`寄存器的值到`RDX`寄存器，也就是把`CR2`寄存器的值存储到`RDX`寄存器作为接下来调用函数的第三个参数。

##### 若`has_error_code`被设置

```
.if has_error_code
    movq    ORIG_RAX(%rsp), %rsi
    movq    $-1, ORIG_RAX(%rsp)
.else
    xorl    %esi, %esi
.endif
```

作用是将错误代码传递给`RSI`寄存器，这将作为将是异常处理程序的第二个参数，在那之后将其设置`-1`以防止再次启动系统调用，另外，如果异常不提供错误代码，将会清空`ESI`寄存器。

#### <a class="reference-link" name="%E6%94%B6%E5%B0%BE%E9%80%BB%E8%BE%91%E5%88%86%E6%9E%90"></a>收尾逻辑分析

最后一定会执行的逻辑是：

```
.if paranoid == 0
    testb    $3, CS(%rsp)
    jz    .Lfrom_kernel_no_context_tracking_@
    CALL_enter_from_user_mode
.Lfrom_kernel_no_context_tracking_@:
.endif

movq    %rsp, %rdi            /* pt_regs pointer */
```

首先再次检查`CPL`以确保异常来自用户控件，然后将`pt_regs`(存储了保存的”现场”)赋值给`RDI`，这将作为中断服务程序的第一个参数，最后调用辅助异常处理程序

```
call  do_sym
```

若是`debug`异常，则调用：

```
dotraplinkage void do_debug(struct pt_regs *regs, long error_code);
```

若是`int3`异常，则调用：

```
dotraplinkage void notrace do_int3(struct pt_regs *regs, long error_code);
```

### <a class="reference-link" name="%E5%BD%93%E5%86%85%E6%A0%B8%E7%A9%BA%E9%97%B4%E4%B8%AD%E5%8F%91%E7%94%9F%E5%BC%82%E5%B8%B8%E6%97%B6"></a>当内核空间中发生异常时

当内核空间中发生异常且`paranoid &gt; 0`时，内核将进入`paranoid_entry`进行处理

#### `paranoid_entry`处理分析

`paranoid_entry`的处理逻辑在`/source/arch/x86/entry/entry_64.S#L1218`处实现：

```
/*
 * Save all registers in pt_regs, and switch gs if needed.
 * Use slow, but surefire "are we in kernel?" check.
 * Return: ebx=0: need swapgs on exit, ebx=1: otherwise
 */
SYM_CODE_START_LOCAL(paranoid_entry)
    UNWIND_HINT_FUNC
    cld
    PUSH_AND_CLEAR_REGS save_ret=1
    ENCODE_FRAME_POINTER 8
    movl    $1, %ebx
    movl    $MSR_GS_BASE, %ecx
    rdmsr
    testl    %edx, %edx
    js    1f                /* negative -&gt; in kernel */
    SWAPGS
    xorl    %ebx, %ebx

1:
    /*
     * Always stash CR3 in %r14.  This value will be restored,
     * verbatim, at exit.  Needed if paranoid_entry interrupted
     * another entry that already switched to the user CR3 value
     * but has not yet returned to userspace.
     *
     * This is also why CS (stashed in the "iret frame" by the
     * hardware at entry) can not be used: this may be a return
     * to kernel code, but with a user CR3 value.
     */
    SAVE_AND_SWITCH_TO_KERNEL_CR3 scratch_reg=%rax save_reg=%r14

    /*
     * The above SAVE_AND_SWITCH_TO_KERNEL_CR3 macro doesn't do an
     * unconditional CR3 write, even in the PTI case.  So do an lfence
     * to prevent GS speculation, regardless of whether PTI is enabled.
     */
    FENCE_SWAPGS_KERNEL_ENTRY

    ret
SYM_CODE_END(paranoid_entry)
```

正如之前所说明的那样，这个入口将会以较慢的方式来获取有关被中断任务的先前状态以检查异常是否真的来自内核空间，可以看到我们首先执行的操作和`error_entry`逻辑相同，首先保存现场，然后使用较慢的方式检查异常的来源，随即返回到上级函数。



## 0x04 一个简单内核模块的编写

事实上，本篇文章的内容到`0x03`就已经结束了，我们将在下一篇文章介绍具体的中断服务函数的实现。

但是在这里我想添加一点内容，就是如何去编译一个简易的内核模块并运行。

### <a class="reference-link" name="%E7%BC%96%E8%AF%91Linux%20Kernel"></a>编译Linux Kernel

这个部分已经在`Kernel Pwn 学习之路(一)`给予了说明故此处不再赘述

这里需要注意一点，因为我们想要在使用`QEMU`启动时使其支持`9p`协议，因此我们需要需要修改`.config`文件，需要将文件里的

```
CONFIG_NET_9P=m
CONFIG_NET_9P_VIRTIO=m
CONFIG_NET_9P_XEN=m
CONFIG_NET_9P_RDMA=m
# CONFIG_NET_9P_DEBUG is not set
......
CONFIG_9P_FS=m
CONFIG_9P_FSCACHE=y
CONFIG_9P_FS_POSIX_ACL=y
CONFIG_9P_FS_SECURITY=y
```

替换为

```
CONFIG_NET_9P=y
CONFIG_NET_9P_VIRTIO=y
CONFIG_NET_9P_XEN=m
CONFIG_NET_9P_RDMA=m
CONFIG_NET_9P_DEBUG=y (Optional)
......
CONFIG_9P_FS=y
CONFIG_9P_FSCACHE=y
CONFIG_9P_FS_POSIX_ACL=y
CONFIG_9P_FS_SECURITY=y
```

⚠：如果执行`make`编译后无法在`/arch/x86/boot`中找到`bzImage`，请尝试执行`make -jx bzImage`(`x`是你期望使用的核数)直至看到以下提示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-17-134309.png)

### <a class="reference-link" name="%E6%9E%84%E5%BB%BA%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F"></a>构建文件系统

首先找一个已经构建好的文件系统解包(可以直接利用`Busybox`生成)，重点是`bin`、`sbin`、`usr`这三个文件夹以及根目录下的`linuxrc`文件，其他文件夹均可暂时置空，然后在`/etc`下建立`passwd`文件以建立用户，内容如下：

```
root:x:0:0:root:/root:/bin/sh
error404:x:1000:1000:error404:/home/error404:/bin/sh
```

然后可以继续建立`profile`文件，内容如下：

```
alias ll='ls -al '
alias l='ls '
if [ $(id -u) == 0 ]; then 
    COLOR="31"  
else
    COLOR="34"
    cd /home/user
fi
export PS1="e[01;$`{`COLOR`}`m $(whoami)@my-kernel [33[00m]:[33[36m]w[33[00m]$ "
```

最后在根目录下建立最重要的`init`文件：

```
#!/bin/sh

mount -t devtmpfs none /dev
mount -t proc proc /proc
mount -t sysfs sysfs /sys

#
# module
#
insmod /lib/modules/*/error404/*.ko
chmod 666 /dev/Test
# mmap_min_addr to 0 for the challenge to be simpler for now ;)
echo 0 &gt; /proc/sys/vm/mmap_min_addr

#
# shell
#
echo "Hello!"
export ENV=/etc/profile
setsid cttyhack setuidgid 1000 sh

umount /proc
umount /sys
umount /dev

poweroff -f
```

### <a class="reference-link" name="%E5%86%85%E6%A0%B8%E6%A8%A1%E5%9D%97%E4%BB%A3%E7%A0%81"></a>内核模块代码

这是一个相当简单的内核模块代码

```
#include &lt;linux/init.h&gt;
#include &lt;linux/module.h&gt;
#include &lt;linux/cred.h&gt;
#include &lt;linux/tty.h&gt;
#include &lt;linux/tty_driver.h&gt;

MODULE_LICENSE("Dual BSD/GPL");

static int hello_init(void)
`{`
    printk(KERN_ALERT "[ERROR404]My First Module！");
    printk(KERN_ALERT "[ERROR404]sizeof cred   : %d", sizeof(struct cred));
    printk(KERN_ALERT "[ERROR404]sizeof tty    : %d", sizeof(struct tty_struct));
    printk(KERN_ALERT "[ERROR404]sizeof tty_op : %d", sizeof(struct tty_operations));
    return 0;
`}`

static void hello_exit(void)
`{`
    printk(KERN_ALERT "[ERROR404]Bye!");
`}`

module_init(hello_init);
module_exit(hello_exit);
```

我们首先需要在代码的同目录下写一个`makefile`，内容如下：

```
obj-m := Test.o
KERNELBUILD := /home/error404/Desktop/Mac_desktop/Linux-Kernel/SourceCode/linux-5.5.6
CURDIR := /home/error404/Desktop/Mac_desktop/Linux-Kernel/build/Test

modules:
    make -C $(KERNELBUILD) M=$(CURDIR) modules
clean:
    make -C $(KERNELBUILD) M=$(CURDIR) clean
```

执行`make`进行编译，将编译出的文件放在`/lib/modules/5.5.6/error404/`下即可

### <a class="reference-link" name="%E5%90%AF%E5%8A%A8QEMU"></a>启动QEMU

建立`Start_Kernel.sh`文件，内容如下：

```
#！sh

qemu-system-x86_64   
        -kernel ./bzImage 
        -initrd ./rootfs.cpio  
        -append 'console=ttyS0 loglevel=0 pti=off oops=panic panic=1 nokaslr' 
        -nographic
```

直接运行`Start_Kernel.sh`即可，紧接着运行`dmesg`即可看到结果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-17-144852.png)

在下一篇文章的末尾将会展示带交互的内核模块的编写~



## 0x05 参考链接

[【原】GitBook – Linux Inside – 0xax](https://legacy.gitbook.com/book/0xax/linux-insides/details)

[【原】Linux-内核编译–咲夜南梦](https://196011564.github.io/2020/02/26/Linux-%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91/#%E6%89%A7%E8%A1%8C%E4%BB%A5%E4%B8%8B%E5%91%BD%E4%BB%A4%E4%B8%8B%E8%BD%BDkernel%E6%BA%90%E7%A0%81)
