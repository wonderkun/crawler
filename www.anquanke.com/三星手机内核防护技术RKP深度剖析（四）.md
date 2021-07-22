> 原文链接: https://www.anquanke.com//post/id/229038 


# 三星手机内核防护技术RKP深度剖析（四）


                                阅读量   
                                **120681**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者longterm，文章来源：longterm.io
                                <br>原文地址：[https://blog.longterm.io/samsung_rkp.html](https://blog.longterm.io/samsung_rkp.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01cfc8691d635a4be5.png)](https://p5.ssl.qhimg.com/t01cfc8691d635a4be5.png)



在本系列文章中，我们将为读者深入讲解三星手机的内核防护技术。在上一篇文章中，我们为读者介绍了系统的初始化过程，以及应用程序的初始化过程。在本文中，将继续为读者呈现更多精彩内容！

**（接上文）**



### APP_RKP

为APP_RKP注册的命令处理程序包括： 

[![](https://p5.ssl.qhimg.com/t0106b6be835b3372c2.png)](https://p5.ssl.qhimg.com/t0106b6be835b3372c2.png)

[![](https://p2.ssl.qhimg.com/t01aaa5b9b59376f1de.png)](https://p2.ssl.qhimg.com/t01aaa5b9b59376f1de.png)

让我们来看看uH在启动过程中调用的命令#0（command #0）。 

```
int64_t rkp_cmd_init() `{`

rkp_panic_on_violation = 1;

rkp_init_cmd_counts();

cs_init(&amp;rkp_start_lock);

return 0;

`}`
```

实际上，APP_RKP的命令#0处理程序也非常简单：它通过调用rkp_init_cmd_counts来设置一个命令的最大调用次数（由“检查器”函数强制执行），并初始化“start”和“deferred start”命令所使用的临界区段（后面会详细介绍）。 



## 异常处理

管理程序的一个重要组成部分就是其异常处理代码。这些处理函数要在内核非法内存访问、内核执行HVC指令时等被调用。通过查看VBAR_EL2寄存器中指定的向量表就能找到这些函数。我们在vmm_init中已经看到，这些向量表位于vmm_vector_table中；从ARMv8的规范来看，其结构如下所示： 

[![](https://p5.ssl.qhimg.com/t01690efb0f9c6ceeac.png)](https://p5.ssl.qhimg.com/t01690efb0f9c6ceeac.png)

我们的设备上使用的是一个运行在EL1上的64位内核，所以命令调度将交由vmm_vector_table+0x400处的异常处理程序完成，但所有的处理程序最终还是会调用相同的函数： 

```
void exception_handler(...) `{`

// ...



// Save registers x0 to x30, sp_el1, elr_el2, spsr_el2

// ...

vmm_dispatch(&lt;level&gt;, &lt;type&gt;, &amp;regs);

asm("clrex");

asm("eret");

`}`
```

vmm_dispatch作为参数给出了已经发生的异常的级别和类型。 

```
int64_t vmm_dispatch(int64_t level, int64_t type, saved_regs_t* regs) `{`

// ...



if (has_panicked)

vmm_panic(level, type, regs, "panic on another core");

switch (type) `{`

case 0x0:

if (vmm_synchronous_handler(level, type, regs))

vmm_panic(level, type, regs, "syncronous handler failed");

break;

case 0x80:

uh_log('D', "vmm.c", 1132, "RKP_e3b85960");

break;

case 0x100:

uh_log('D', "vmm.c", 1135, "RKP_6d732e0a");

break;

case 0x180:

uh_log('D', "vmm.c", 1149, "RKP_3c71de0a");

break;

default:

return 0;

`}`

return 0;

`}`
```

在出现同步异常的情况下，vmm_dispatch函数将调用vmm_synchronous_handler函数。 

```
int64_t vmm_synchronous_handler(int64_t level, int64_t type, saved_regs_t* regs) `{`

// ...



esr_el2 = get_esr_el2();

switch (esr_el2 &gt;&gt; 26) `{`

case 0x12: /* HVC instruction execution in AArch32 state */

case 0x16: /* HVC instruction execution in AArch64 state */

if ((regs-&gt;x0 &amp; 0xFFFFF000) == 0xC300C000) `{`

cmd_id = regs-&gt;x1;

app_id = regs-&gt;x0;

cpu_num = get_current_cpu();

if (cpu_num &lt;= 7)

uh_state.injections[cpu_num] = 0;

uh_handle_command(app_id, cmd_id, regs);

`}`

return 0;

case 0x18: /* Trapped MSR, MRS or Sys. ins. execution in AArch64 state */

if ((esr_el2 &amp; 1) == 0 &amp;&amp; !other_msr_mrs_system(&amp;regs-&gt;x0, esr_el2_1 &amp; 0x1FFFFFF))

return 0;

vmm_panic(level, type, regs, "other_msr_mrs_system failure");

return 0;

case 0x20: /* Instruction Abort from a lower EL */

cs_enter(&amp;s2_lock);

el1_va_to_ipa(get_elr_el2(), &amp;ipa);

get_s2_1gb_page(ipa, &amp;fld);

print_s2_fld(fld);

if ((fld &amp; 3) == 3) `{`

get_s2_2mb_page(ipa, &amp;sld);

print_s2_sld(sld);

if ((sld &amp; 3) == 3) `{`

get_s2_4kb_page(ipa, &amp;tld);

print_s2_tld(tld);

`}`

`}`

cs_exit(&amp;s2_lock);

if (should_skip_prefetch_abort() == 1)

return 0;

if (!esr_ec_prefetch_abort_from_a_lower_exception_level("-snip-")) `{`

print_vmm_registers(regs);

return 0;

`}`

vmm_panic(level, type, regs, "esr_ec_prefetch_abort_from_a_lower_exception_level");

return 0;

case 0x21: /* Instruction Abort taken without a change in EL */

uh_log('L', "vmm.c", 920, "esr abort iss: 0x%x", esr_el2 &amp; 0x1FFFFFF);

vmm_panic(level, type, regs, "esr_ec_prefetch_abort_taken_without_a_change_in_exception_level");

case 0x24: /* Data Abort from a lower EL */

if (!rkp_fault(regs))

return 0;

if ((esr_el2 &amp; 0x3F) == 7)// Translation fault, level 3

`{`

va = rkp_get_va(get_hpfar_el2() &lt;&lt; 8);

cs_enter(&amp;s2_lock);

res = el1_va_to_pa(va, &amp;ipa);

if (!res) `{`

uh_log('L', "vmm.c", 994, "Skipped data abort va: %p, ipa: %p", va, ipa);

cs_exit(&amp;s2_lock);

return 0;

`}`

cs_exit(&amp;s2_lock);

`}`

if ((esr_el2 &amp; 0x7C) == 76)// Permission fault, any level

`{`

va = rkp_get_va(get_hpfar_el2() &lt;&lt; 8);

at_s12e1w(va);

if ((get_par_el1() &amp; 1) == 0) `{`

print_el2_state();

invalidate_entire_s1_s2_el1_tlb();

return 0;

`}`

`}`

el1_va_to_ipa(get_elr_el2(), &amp;ipa);

get_s2_1gb_page(ipa, &amp;fld);

print_s2_fld(fld);

if ((fld &amp; 3) == 3) `{`

get_s2_2mb_page(ipa, &amp;sld);

print_s2_sld(sld);

if ((sld &amp; 3) == 3) `{`

get_s2_4kb_page(ipa, &amp;tld);

print_s2_tld(tld);

`}`

`}`

if (esr_ec_prefetch_abort_from_a_lower_exception_level("-snip-"))

vmm_panic(level, type, regs, "esr_ec_data_abort_from_a_lower_exception_level");

else

print_vmm_registers(regs);

return 0;

case 0x25: /* Data Abort taken without a change in EL */

vmm_panic(level, type, regs, "esr_ec_data_abort_taken_without_a_change_in_exception_level");

return 0;

default:

return -1;

`}`

`}`
```

函数vmm_synchronous_handler首先通过读取ESR_EL2寄存器来获取异常类。

如果是在AArch32或AArch64状态下执行的HVC指令，则调用uh_handle_command函数，app_id在X0中，cmd_id在X1中。

如果是在AArch64状态下的陷阱系统寄存器访问，如果是写入操作，则调用其他_msr_mrs_system函数，函数中包含被写入的寄存器。

other_msr_mrs_system函数将从保存的寄存器中获取被写入的值。

检查被写入的寄存器是否允许写入操作：如果该寄存器不允许被写入，它要么调用uh_panic函数，要么检查新的值是否有效（如果特定位有一个固定的值的话）。

更新ELR_EL2寄存器，使其指向下一条指令。

如果是来自较低异常级别的指令异常。

调用should_skip_prefetch_abort函数。

如果IFSC==0b000111（地址转换错误，第3级）&amp;&amp; S1PTW==1（地址转换错误，第2级）&amp;&amp; EA==0（不是外部异常）&amp;&amp; FnV=0b0（FAR有效）&amp;&amp; SET=0b00（可恢复状态）。

并且如果跳过的预取异常次数小于9。

那么should_skip_prefetch_abort函数将返回1，否则返回0。

如果没有跳过，则调用esr_ec_prefetch_abort_from_a_lower_exception_level函数。

该函数检查故障地址是否为0。

如果是，则将故障注入到EL1中。

同时将CPU编号记录到uh_state的injections数组中。

如果地址不是0，则会死机。

它是来自较低异常级别的数据异常。

它将调用rkp_fault函数来检测RKP故障。

发生故障的指令必须位于内核的text区段中。

发生故障的指令必须是str x2，[x1]。

x1必须指向一个页表项。

如果是第1级PTE，则调用rkp_l1pgt_write函数。

如果是第2级PTE，则调用rkp_l2pgt_write函数。

如果是第3级PTE，则调用rkp_l3pgt_write函数。

让PC指向下一条指令并返回。

如果不是RKP故障，则检查数据故障状态码。

如果DFSC==0b000111（地址转换错误，第3级）。

但它可以对s12e1(r|w)这个故障地址进行转换，则不会死机。

如果DFSC==0b0011xx（权限错误，任何级别）。

但它可以转换出s12e1w的故障地址，则宣布TLB无效。

否则，调用esr_ec_prefetch_abort_from_a_lower_exception_level函数。

和上面一样，注入EL1为0，否则就死机。

如果是来自EL2的指令异常或数据异常，则死机。 

```
crit_sec_t* vmm_panic(int64_t level, int64_t type, saved_regs_t* regs, char* message) `{`

// ...



uh_log('L', "vmm.c", 1171, "&gt;&gt;vmm_panic&lt;&lt;");

cs_enter(&amp;panic_cs);

uh_log('L', "vmm.c", 1175, "message: %s", message);

switch (level) `{`

case 0x0:

uh_log('L', "vmm.c", 1179, "level: VMM_EXCEPTION_LEVEL_TAKEN_FROM_CURRENT_WITH_SP_EL0");

break;

case 0x200:

uh_log('L', "vmm.c", 1182, "level: VMM_EXCEPTION_LEVEL_TAKEN_FROM_CURRENT_WITH_SP_ELX");

break;

case 0x400:

uh_log('L', "vmm.c", 1185, "level: VMM_EXCEPTION_LEVEL_TAKEN_FROM_LOWER_USING_AARCH64");

break;

case 0x600:

uh_log('L', "vmm.c", 1188, "level: VMM_EXCEPTION_LEVEL_TAKEN_FROM_LOWER_USING_AARCH32");

break;

default:

uh_log('L', "vmm.c", 1191, "level: VMM_UNKNOWN\n");

break;

`}`

switch (type) `{`

case 0x0:

uh_log('L', "vmm.c", 1197, "type: VMM_EXCEPTION_TYPE_SYNCHRONOUS");

break;

case 0x80:

uh_log('L', "vmm.c", 1200, "type: VMM_EXCEPTION_TYPE_IRQ_OR_VIRQ");

break;

case 0x100:

uh_log('L', "vmm.c", 1203, "type: VMM_SYSCALL\n");

break;

case 0x180:

uh_log('L', "vmm.c", 1206, "type: VMM_EXCEPTION_TYPE_SERROR_OR_VSERROR");

break;

default:

uh_log('L', "vmm.c", 1209, "type: VMM_UNKNOWN\n");

break;

`}`

print_vmm_registers(regs);

if ((get_sctlr_el1() &amp; 1) == 0 || type != 0 || (level == 0 || level == 0x200)) `{`

has_panicked = 1;

cs_exit(&amp;panic_cs);

if (!strcmp(message, "panic on another core"))

exynos_reset(0x8800);

uh_panic();

`}`

uh_panic_el1(uh_state.fault_handler, regs);

return cs_exit(&amp;panic_cs);

`}`
```

vmm_panic函数会记录死机消息，异常级别和类型，如果发生下面的某种情形：
1. MMU被禁用；
1. 异常不同步；
1. 异常来自EL2；
则调用uh_panic函数，否则，就调用uh_panic_el1函数。 

```
void uh_panic() `{`

uh_log('L', "main.c", 482, "uh panic!");

print_state_and_reset();

`}`



void print_state_and_reset() `{`

uh_log('L', "panic.c", 29, "count state - page_ro: %lx, page_free: %lx, s2_breakdown: %lx", page_ro, page_free,

s2_breakdown);

print_el2_state();

print_el1_state();

print_stack_contents();

bigdata_store_data();

has_panicked = 1;

exynos_reset(0x8800);

`}`
```

uh_panic函数会记录EL1和EL2系统寄存器的值、管理程序和内核堆栈的内容，并将这些内容的文本版本复制到“bigdata”区域，然后重新启动设备。 

```
int64_t uh_panic_el1(uh_handler_list_t* fault_handler, saved_regs_t* regs) `{`

// ...



uh_log('L', "vmm.c", 111, "&gt;&gt;uh_panic_el1&lt;&lt;");

if (!fault_handler) `{`

uh_log('L', "vmm.c", 113, "uH handler did not registered");

uh_panic();

`}`

print_el2_state();

print_el1_state();

print_stack_contents();

cpu_num = get_current_cpu();

if (cpu_num &lt;= 7) `{`

something = cpu_num - 0x21530000;

if (uh_state.injections[cpu_num] == something)

uh_log('D', "vmm.c", 99, "Injection locked");

uh_state.injections[cpu_num] = something;

`}`

handler_data = &amp;fault_handler-&gt;uh_handler_data[cpu_num];

handler_data-&gt;esr_el2 = get_esr_el2();

handler_data-&gt;elr_el2 = get_elr_el2();

handler_data-&gt;hcr_el2 = get_hcr_el2();

handler_data-&gt;far_el2 = get_far_el2();

handler_data-&gt;hpfar_el2 = get_hpfar_el2() &lt;&lt; 8;

if (regs)

memcpy(fault_handler-&gt;uh_handler_data[cpu_num].regs.regs, regs, 272);

set_elr_el2(fault_handler-&gt;uh_handler);

return 0;

`}`
```

uh_panic_el1函数用于填充APP_INIT的命令#0指定的结构体。同时，它还将ELR_EL2设置为相应的处理函数，以便在执行ERET指令时调用它。



## 深入了解RKP

### 启动过程

RKP的启动分两个阶段进行，为此将使用两个不同的命令：
1. 命令#1 (启动)：由内核在start_kernel函数中调用, 它位于mm_init函数之后；
1. 命令#2（延迟启动）：由内核在kernel_init函数中调用，刚好在启动init之前调用。 
### RKP的启动命令

在内核端，这个命令在rkp_init函数中调用的，具体代码位于init/main.c中。 

```
rkp_init_t rkp_init_data __rkp_ro = `{`

.magic = RKP_INIT_MAGIC,

.vmalloc_start = VMALLOC_START,

.no_fimc_verify = 0,

.fimc_phys_addr = 0,

._text = (u64)_text,

._etext = (u64)_etext,

._srodata = (u64)__start_rodata,

._erodata = (u64)__end_rodata,

.large_memory = 0,

`}`;



static void __init rkp_init(void)

`{`

// ...

rkp_init_data.vmalloc_end = (u64)high_memory;

rkp_init_data.init_mm_pgd = (u64)__pa(swapper_pg_dir);

rkp_init_data.id_map_pgd = (u64)__pa(idmap_pg_dir);

rkp_init_data.tramp_pgd = (u64)__pa(tramp_pg_dir);

#ifdef CONFIG_UH_RKP_FIMC_CHECK

rkp_init_data.no_fimc_verify = 1;

#endif

rkp_init_data.tramp_valias = (u64)TRAMP_VALIAS;

rkp_init_data.zero_pg_addr = (u64)__pa(empty_zero_page);

// ...

uh_call(UH_APP_RKP, RKP_START, (u64)&amp;rkp_init_data, (u64)kimage_voffset, 0, 0);

`}`



asmlinkage __visible void __init start_kernel(void)

`{`

// ...

rkp_init();

// ...

`}`
```

在管理程序端，相应的命令处理程序如下所示： 

```
int64_t rkp_cmd_start(saved_regs_t* regs) `{`

// ...



cs_enter(&amp;rkp_start_lock);

if (rkp_inited) `{`

cs_exit(&amp;rkp_start_lock);

uh_log('L', "rkp.c", 133, "RKP is already started");

return -1;

`}`

res = rkp_start(regs);

cs_exit(&amp;rkp_start_lock);

return res;

`}`



rkp_cmd_start calls rkp_start which does the real work.



int64_t rkp_start(saved_regs_t* regs) `{`

// ...



KIMAGE_VOFFSET = regs-&gt;x3;

rkp_init_data = rkp_get_pa(regs-&gt;x2);

if (rkp_init_data-&gt;magic - 0x5AFE0001 &gt;= 2) `{`

uh_log('L', "rkp_init.c", 85, "RKP INIT-Bad Magic(%d), %p", regs-&gt;x2, rkp_init_data);

return -1;

`}`

if (rkp_init_data-&gt;magic == 0x5AFE0002) `{`

rkp_init_cmd_counts_test();

rkp_test = 1;

`}`

INIT_MM_PGD = rkp_init_data-&gt;init_mm_pgd;

ID_MAP_PGD = rkp_init_data-&gt;id_map_pgd;

ZERO_PG_ADDR = rkp_init_data-&gt;zero_pg_addr;

TRAMP_PGD = rkp_init_data-&gt;tramp_pgd;

TRAMP_VALIAS = rkp_init_data-&gt;tramp_valias;

VMALLOC_START = rkp_init_data-&gt;vmalloc_start;

VMALLOC_END = rkp_init_data-&gt;vmalloc_end;

TEXT = rkp_init_data-&gt;_text;

ETEXT = rkp_init_data-&gt;_etext;

TEXT_PA = rkp_get_pa(TEXT);

ETEXT_PA = rkp_get_pa(ETEXT);

SRODATA = rkp_init_data-&gt;_srodata;

ERODATA = rkp_init_data-&gt;_erodata;

TRAMP_PGD_PAGE = TRAMP_PGD &amp; 0xFFFFFFFFF000;

INIT_MM_PGD_PAGE = INIT_MM_PGD &amp; 0xFFFFFFFFF000;

LARGE_MEMORY = rkp_init_data-&gt;large_memory;

page_ro = 0;

page_free = 0;

s2_breakdown = 0;

pmd_allocated_by_rkp = 0;

NO_FIMC_VERIFY = rkp_init_data-&gt;no_fimc_verify;

if (rkp_bitmap_init() &lt; 0) `{`

uh_log('L', "rkp_init.c", 150, "Failed to init bitmap");

return -1;

`}`

memlist_init(&amp;executable_regions);

memlist_set_field_14(&amp;executable_regions);

memlist_add(&amp;executable_regions, TEXT, ETEXT - TEXT);

if (TRAMP_VALIAS)

memlist_add(&amp;executable_regions, TRAMP_VALIAS, 0x1000);

memlist_init(&amp;dynamic_load_regions);

memlist_set_field_14(&amp;dynamic_load_regions);

put_last_dynamic_heap_chunk_in_static_heap();

if (rkp_paging_init() &lt; 0) `{`

uh_log('L', "rkp_init.c", 169, "rkp_pging_init fails");

return -1;

`}`

rkp_inited = 1;

if (rkp_l1pgt_process_table(get_ttbr0_el1() &amp; 0xFFFFFFFFF000, 0, 1) &lt; 0) `{`

uh_log('L', "rkp_init.c", 179, "processing l1pgt fails");

return -1;

`}`

uh_log('L', "rkp_init.c", 183, "[*] HCR_EL2: %lx, SCTLR_EL2: %lx", get_hcr_el2(), get_sctlr_el2());

uh_log('L', "rkp_init.c", 184, "[*] VTTBR_EL2: %lx, TTBR0_EL2: %lx", get_vttbr_el2(), get_ttbr0_el2());

uh_log('L', "rkp_init.c", 185, "[*] MAIR_EL1: %lx, MAIR_EL2: %lx", get_mair_el1(), get_mair_el2());

uh_log('L', "rkp_init.c", 186, "RKP Activated");

return 0;

`}`
```

让我们来深入分析一下这个函数：
1. 它将第二个参数保存到全局变量KIMAGE_VOFFSET中。
1. 就像我们将看到的大多数命令处理程序一样，它将第一个参数rkp_init_data从虚拟地址转换为物理地址，这一步是通过调用rkp_get_pa函数来实现的。
1. 然后，检查其magic字段。如果它是测试模式的magic，则调用rkp_init_cmd_counts_test函数，从而允许测试命令0x81-0x88被无限次调用。
1. 将rkp_init_data的各个字段保存到全局变量中。
1. 初始化一个名为executable_regions的新memlist实例，并将内核的text区段添加到其中，并在提供TRAMP_VALIAS页面时执行相同的操作。
1. 初始化一个名为dynamic_load_regions的新memlist实例，这个memlist用于RKP的“动态可执行文件加载”功能（我们将在后文对此进行详细介绍）。
1. 调用put_last_dynamic_chunk_in_heap函数（在我们的设备上，最终的结果是静态堆获取了所有未使用的动态内存，而动态堆没有获得任何剩余的内存）。
1. 调用rkp_paging_init和rkp_l1pgt_process_table函数，我们将在下面详细介绍。
1. 记录一些EL2系统寄存器的值并返回。 
```
int64_t rkp_paging_init() `{`

// ...



if (!TEXT || (TEXT &amp; 0xFFF) != 0) `{`

uh_log('L', "rkp_paging.c", 637, "kernel text start is not aligned, stext : %p", TEXT);

return -1;

`}`

if (!ETEXT || (ETEXT &amp; 0xFFF) != 0) `{`

uh_log('L', "rkp_paging.c", 642, "kernel text end is not aligned, etext : %p", ETEXT);

return -1;

`}`

if (TEXT_PA &lt;= get_base() &amp;&amp; ETEXT_PA &gt; get_base())

return -1;

if (s2_unmap(0x87000000, 0x200000))

return -1;

if (rkp_phys_map_set_region(TEXT_PA, ETEXT - TEXT, TEXT) &lt; 0) `{`

uh_log('L', "rkp_paging.c", 435, "physmap set failed for kernel text");

return -1;

`}`

if (s1_map(TEXT_PA, ETEXT - TEXT, UNKN1 | READ)) `{`

uh_log('L', "rkp_paging.c", 447, "Failed to make VMM S1 range RO");

return -1;

`}`

if (INIT_MM_PGD &gt;= TEXT_PA &amp;&amp; INIT_MM_PGD &lt; ETEXT_PA &amp;&amp; s1_map(INIT_MM_PGD, 0x1000, UNKN1 | WRITE | READ)) `{`

uh_log('L', "rkp_paging.c", 454, "failed to make swapper_pg_dir RW");

return -1;

`}`

rkp_phys_map_lock(ZERO_PG_ADDR);

if (rkp_s2_page_change_permission(ZERO_PG_ADDR, 0, 1, 1) &lt; 0) `{`

uh_log('L', "rkp_paging.c", 462, "Failed to make executable for empty_zero_page");

return -1;

`}`

rkp_phys_map_unlock(ZERO_PG_ADDR);

if (rkp_set_kernel_rox(0))

return -1;

if (rkp_s2_range_change_permission(0x87100000, 0x87140000, 0x80, 1, 1) &lt; 0) `{`

uh_log('L', "rkp_paging.c", 667, "Failed to make UH_LOG region RO");

return -1;

`}`

if (!uh_state.dynamic_heap_inited)

return 0;

if (rkp_s2_range_change_permission(uh_state.dynamic_heap_base,

uh_state.dynamic_heap_base + uh_state.dynamic_heap_size, 0x80, 1, 1) &lt; 0) `{`

uh_log('L', "rkp_paging.c", 685, "Failed to make dynamic_heap region RO");

return -1;

`}`

return 0;

`}`
```

我们也来分析一下rkp_paging_init函数：
1. 对内核的text区段进行一些安全检查。
1. 在phys_map中把内核的text区段标记为TEXT（名字是我们自己起的）。
1. 在EL2的第1阶段，将内核的text区段映射为RO。
1. 在EL2的第1阶段，将swapper_pg_dir映射为RW。
1. 在EL1的第2阶段，将empty_zero_page映射为ROX。
1. 调用rkp_set_kernel_rox函数，我们将在后面对其进行详细的介绍。
1. 在EL1的第2阶段，将日志区段设置为ROX。
1. 在EL1的第2阶段，将动态堆区段设置为ROX。 
```
int64_t rkp_set_kernel_rox(int64_t access) `{`

// ...



erodata_pa = rkp_get_pa(ERODATA);

if (rkp_s2_range_change_permission(TEXT_PA, erodata_pa, access, 1, 1) &lt; 0) `{`

uh_log('L', "rkp_paging.c", 392, "Failed to make Kernel range ROX");

return -1;

`}`

if (access)

return 0;

if (((erodata_pa | ETEXT_PA) &amp; 0xFFF) != 0) `{`

uh_log('L', "rkp_paging.c", 158, "start or end addr is not aligned, %p - %p", ETEXT_PA, erodata_pa);

return 0;

`}`

if (ETEXT_PA &gt; erodata_pa) `{`

uh_log('L', "rkp_paging.c", 163, "start addr is bigger than end addr %p, %p", ETEXT_PA, erodata_pa);

return 0;

`}`

paddr = ETEXT_PA;

while (sparsemap_set_value_addr(&amp;uh_state.ro_bitmap, addr, 1) &gt;= 0) `{`

paddr += 0x1000;

if (paddr &gt;= erodata_pa)

return 0;

uh_log('L', "rkp_paging.c", 171, "set_pgt_bitmap fail, %p", paddr);

`}`

return 0;

`}`
```

在EL1的第2阶段，函数rkp_set_kernel_rox会将[kernel text start; rodata end]之间的内存设置为RWX（是的，RWX对应的访问参数为0，但稍后将使用0x80再次调用该函数，使其变为RO），然后，它更新ro_bitmap，从而把[kernel text end; rodata end]之间的内存标记为RO。

在rkp_paging_init之后，rkp_start函数将调用rkp_l1pgt_process_table来处理页表（主要把3级表变成只读的）。它会根据TTBR0_EL1寄存器的值调用该函数。

### RKP的延迟启动命令

在内核端，这个命令将被include/linux/rkp.h文件中的rkp_deferred_init函数所调用。 

```
// from include/linux/rkp.h

static inline void rkp_deferred_init(void)`{`

uh_call(UH_APP_RKP, RKP_DEFERRED_START, 0, 0, 0, 0);

`}`



// from init/main.c

static int __ref kernel_init(void *unused)

`{`

// ...

rkp_deferred_init();

// ...

`}`
```

在管理程序端，相应的命令处理程序如下所示： 

```
int64_t rkp_cmd_deferred_start() `{`

return rkp_deferred_start();

`}`



int64_t rkp_deferred_start() `{`

uh_log('L', "rkp_init.c", 193, "DEFERRED INIT START");

if (rkp_set_kernel_rox(0x80))

return -1;

if (rkp_l1pgt_process_table(INIT_MM_PGD, 0x1FFFFFF, 1) &lt; 0) `{`

uh_log('L', "rkp_init.c", 198, "Failed to make l1pgt processing");

return -1;

`}`

if (TRAMP_PGD &amp;&amp; rkp_l1pgt_process_table(TRAMP_PGD, 0x1FFFFFF, 1) &lt; 0) `{`

uh_log('L', "rkp_init.c", 204, "Failed to make l1pgt processing");

return -1;

`}`

rkp_deferred_inited = 1;

uh_log('L', "rkp_init.c", 217, "DEFERRED INIT IS DONE\n");

memory_fini();

return 0;

`}`
```

函数rkp_cmd_deferred_start和rkp_deferred_start将执行以下操作： 
1. 再次调用函数rkp_set_kernel_rox（第一次是在正常启动时调用），但这次是以0x80（只读）作为参数，所以内核的text + rodata区段将在第2阶段被标记为 RO。
1. 根据swapper_pg_dir调用rkp_l1pgt_process_table。
1. 根据tramp_pg_dir(如果已经设置了的话)调用rkp_l1pgt_process_table。
1. 最后调用memory_fini。
### RKP的Bitmap命令

内核在启动期间还调用了另外3条RKP命令。

其中有两条命令也是在位于init/main.c文件中的rkp_init函数中调用的： 

```
// from init/main.c

sparse_bitmap_for_kernel_t* rkp_s_bitmap_ro __rkp_ro = 0;

sparse_bitmap_for_kernel_t* rkp_s_bitmap_dbl __rkp_ro = 0;



static void __init rkp_init(void)

`{`

// ...

rkp_s_bitmap_ro = (sparse_bitmap_for_kernel_t *)

uh_call(UH_APP_RKP, RKP_GET_RO_BITMAP, 0, 0, 0, 0);

rkp_s_bitmap_dbl = (sparse_bitmap_for_kernel_t *)

uh_call(UH_APP_RKP, RKP_GET_DBL_BITMAP, 0, 0, 0, 0);

// ...

`}`



// from include/linux/rkp.h

typedef struct sparse_bitmap_for_kernel `{`

u64 start_addr;

u64 end_addr;

u64 maxn;

char **map;

`}` sparse_bitmap_for_kernel_t;



static inline u8 rkp_is_pg_protected(u64 va)`{`

return rkp_check_bitmap(__pa(va), rkp_s_bitmap_ro);

`}`



static inline u8 rkp_is_pg_dbl_mapped(u64 pa)`{`

return rkp_check_bitmap(pa, rkp_s_bitmap_dbl);

`}`
```

我们来看看RKP_GET_RO_BITMAP的命令处理程序。 

```
int64_t rkp_cmd_get_ro_bitmap(saved_regs_t* regs) `{`

// ...



if (rkp_deferred_inited)

return -1;

bitmap = dynamic_heap_alloc(0x20, 0);

if (!bitmap) `{`

uh_log('L', "rkp.c", 302, "Fail alloc robitmap for kernel");

return -1;

`}`

memset(bitmap, 0, sizeof(sparse_bitmap_for_kernel_t));

res = sparsemap_bitmap_kernel(&amp;uh_state.ro_bitmap, bitmap);

if (res) `{`

uh_log('L', "rkp.c", 309, "Fail sparse_map_bitmap_kernel");

return res;

`}`

regs-&gt;x0 = rkp_get_va(bitmap);

if (regs-&gt;x2)

*virt_to_phys_el1(regs-&gt;x2) = regs-&gt;x0;

uh_log('L', "rkp.c", 322, "robitmap:%p", bitmap);

return 0;

`}`
```

函数rkp_cmd_get_ro_bitmap将从动态堆中分配一个sparse_bitmap_for_kernel_t结构体，并将其清零，然后传给sparsemap_bitmap_kernel函数，该函数将利用ro_bitmap中的信息来填充该结构体。然后，它将VA放到X0中，如果X2中提供了一个指针，它也将把它放到那里（使用virt_to_phys_el1）。 

```
int64_t sparsemap_bitmap_kernel(sparsemap_t* map, sparse_bitmap_for_kernel_t* kernel_bitmap) `{`

// ...



if (!map || !kernel_bitmap)

return -1;

kernel_bitmap-&gt;start_addr = map-&gt;start_addr;

kernel_bitmap-&gt;end_addr = map-&gt;end_addr;

kernel_bitmap-&gt;maxn = map-&gt;count;

bitmaps = dynamic_heap_alloc(8 * map-&gt;count, 0);

if (!bitmaps) `{`

uh_log('L', "sparsemap.c", 202, "kernel_bitmap does not allocated : %lu", map-&gt;count);

return -1;

`}`

if (map-&gt;private) `{`

uh_log('L', "sparsemap.c", 206, "EL1 doesn't support to get private sparsemap");

return -1;

`}`

memset(bitmaps, 0, 8 * map-&gt;count);

kernel_bitmap-&gt;map = (bitmaps - PHYS_OFFSET) | 0xFFFFFFC000000000;

index = 0;

do `{`

bitmap = map-&gt;entries[index].bitmap;

if (bitmap)

bitmaps[index] = (bitmap - PHYS_OFFSET) | 0xFFFFFFC000000000;

++index;

`}` while (index &lt; kernel_bitmap-&gt;maxn);

return 0;

`}`
```

函数sparsemap_bitmap_kernel将接收一个sparsemap，并将所有bitmap的物理地址转换为虚拟地址，然后再将它们复制到sparse_bitmap_for_kernel_t结构体中。

实际上，函数rkp_cmd_get_dbl_bitmap和rkp_cmd_get_ro_bitmap非常相似，区别在于：前者发送的不是ro_bitmap的bitmap，而是dbl_bitmap的bitmap。

第三条命令rkp_cmd_get_rkp_get_buffer_bitmap也是用来检索sparsemap，即page_allocator.map。它是被内核中的rkp_robuffer_init函数（位于init/main.c文件中）所调用的。 

```
sparse_bitmap_for_kernel_t* rkp_s_bitmap_buffer __rkp_ro = 0;



static void __init rkp_robuffer_init(void)

`{`

rkp_s_bitmap_buffer = (sparse_bitmap_for_kernel_t *)

uh_call(UH_APP_RKP, RKP_GET_RKP_GET_BUFFER_BITMAP, 0, 0, 0, 0);

`}`



asmlinkage __visible void __init start_kernel(void)

`{`

// ...

rkp_robuffer_init();

// ...

rkp_init();

// ...

`}`



// from include/linux/rkp.h

static inline unsigned int is_rkp_ro_page(u64 va)`{`

return rkp_check_bitmap(__pa(va), rkp_s_bitmap_buffer);

`}`
```

综上所述，这些bitmap被内核用来检查某些数据是否受到RKP的保护（分配在只读内存页上），如果是这样的话，内核就需要调用相应的RKP命令进行相应的修改。



## 小结

在本系列文章中，我们将为读者深入讲解三星手机的内核防护技术。在本文中，我们为读者介绍了系统的异常处理过程，以及RKP机制相关的命令，在后续的文章中，会有更多精彩内容呈现给大家，敬请期待！

**（未完待续）**
