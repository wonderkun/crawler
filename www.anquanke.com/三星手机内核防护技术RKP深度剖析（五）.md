> 原文链接: https://www.anquanke.com//post/id/229235 


# 三星手机内核防护技术RKP深度剖析（五）


                                阅读量   
                                **80449**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者longterm，文章来源：longterm.io
                                <br>原文地址：[https://blog.longterm.io/samsung_rkp.html](https://blog.longterm.io/samsung_rkp.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01cfc8691d635a4be5.png)](https://p5.ssl.qhimg.com/t01cfc8691d635a4be5.png)



在本系列文章中，我们将为读者深入讲解三星手机的内核防护技术。在上一篇文章中，我们为读者介绍了系统的异常处理过程，以及RKP机制相关的命令。在本文中，将继续为读者呈现更多精彩内容！

**（接上文）**



## 页表的处理

下面展示的是Android设备上的Linux内存布局（4KB内存页+3级）： 

[![](https://p0.ssl.qhimg.com/t01b2ba8fe8b39fb3a8.png)](https://p0.ssl.qhimg.com/t01b2ba8fe8b39fb3a8.png)

下面是相应的转换表查找过程： 

[![](https://p5.ssl.qhimg.com/t0157c33493fef00a2e.png)](https://p5.ssl.qhimg.com/t0157c33493fef00a2e.png)

因此，请记住，在这一部分，PGD = PUD = VA[38:30]。

下面是第0级、1级和2级描述符的格式： 

[![](https://p2.ssl.qhimg.com/t019279f9e584477e16.png)](https://p2.ssl.qhimg.com/t019279f9e584477e16.png)

下面是第3级描述符的格式： 

[![](https://p0.ssl.qhimg.com/t010710b927ef8b5a27.png)](https://p0.ssl.qhimg.com/t010710b927ef8b5a27.png)

### 第一级

第一级表的处理由rkp_l1pgt_process_table函数完成。 

```
int64_t rkp_l1pgt_process_table(int64_t pgd, uint32_t high_bits, uint32_t is_alloc) `{`

// ...



if (high_bits == 0x1FFFFFF) `{`

if (pgd != INIT_MM_PGD &amp;&amp; (!TRAMP_PGD || pgd != TRAMP_PGD) || rkp_deferred_inited) `{`

rkp_policy_violation("only allowed on kerenl PGD or tramp PDG! l1t : %lx", pgd);

return -1;

`}`

`}` else `{`

if (ID_MAP_PGD == pgd)

return 0;

`}`

rkp_phys_map_lock(pgd);

if (is_alloc) `{`

if (is_phys_map_l1(pgd)) `{`

rkp_phys_map_unlock(pgd);

return 0;

`}`

if (high_bits)

type = KERNEL | L1;

else

type = L1;

res = rkp_phys_map_set(pgd, type);

if (res &lt; 0) `{`

rkp_phys_map_unlock(pgd);

return res;

`}`

res = rkp_s2_page_change_permission(pgd, 0x80, 0, 0);

if (res &lt; 0) `{`

uh_log('L', "rkp_l1pgt.c", 63, "Process l1t failed, l1t addr : %lx, op : %d", pgd, 1);

rkp_phys_map_unlock(pgd);

return res;

`}`

`}` else `{`

if (!is_phys_map_l1(pgd)) `{`

rkp_phys_map_unlock(pgd);

return 0;

`}`

res = rkp_phys_map_set(pgd, FREE);

if (res &lt; 0) `{`

rkp_phys_map_unlock(pgd);

return res;

`}`

res = rkp_s2_page_change_permission(pgd, 0, 1, 0);

if (res &lt; 0) `{`

uh_log('L', "rkp_l1pgt.c", 80, "Process l1t failed, l1t addr : %lx, op : %d", pgd, 0);

rkp_phys_map_unlock(pgd);

return res;

`}`

`}`

offset = 0;

entry = 0;

start_addr = high_bits &lt;&lt; 39;

do `{`

desc_p = pgd + entry;

desc = *desc_p;

if ((desc &amp; 3) != 3) `{`

if (desc)

set_pxn_bit_of_desc(desc_p, 1);

`}` else `{`

addr = start_addr &amp; 0xFFFFFF803FFFFFFF | offset;

res += rkp_l2pgt_process_table(desc &amp; 0xFFFFFFFFF000, addr, is_alloc);

if (!(start_addr &gt;&gt; 39))

set_pxn_bit_of_desc(desc_p, 1);

`}`

entry += 8;

offset += 0x40000000;

start_addr = addr;

`}` while (entry != 0x1000);

rkp_phys_map_unlock(pgd);

return res;

`}`
```

函数rkp_l1pgt_process_table的作用如下所示：

如果为其提供的是内核空间的PGD(TTBR1_EL1)。

它必须是tramp_pg_dir或swapper_pg_dir。

它也必须没有被延迟初始化。

如果为其提供的是用户空间的PGD（TTBR0_EL1）。

如果是idmap_pg_dir，则提前返回。

对于内核和用户空间。

如果PGD正在被收回。

在physmap中查找标记为PGD的空间。

在physmap中将其标记为free。

在第2阶段使其成为RWX（如果初始化则不允许）。

如果PGD正在被引入。

在physmap中查找尚未标记为PGD的空间。

在physmap中将其标记为PGD。

在第2阶段使其成为RO（如果初始化则不允许）。

然后在这两种情况下，对于PGD的每个条目。

对于块，设置其PXN位。

对于表，调用rkp_l2pgt_process_table。

如果VA&lt;0x8000000000，也设置其PXN位。

### 第二级

第二级表的处理由rkp_l2pgt_process_table函数完成。

```
int64_t rkp_l2pgt_process_table(int64_t pmd, uint64_t start_addr, uint32_t is_alloc) `{`

// ...



if (!(start_addr &gt;&gt; 39)) `{`

if (!pmd_allocated_by_rkp) `{`

if (page_allocator_is_allocated(pmd) == 1)

pmd_allocated_by_rkp = 1;

else

pmd_allocated_by_rkp = -1;

`}`

if (pmd_allocated_by_rkp == -1)

return 0;

`}`

rkp_phys_map_lock(pmd);

if (is_alloc) `{`

if (is_phys_map_l2(pmd)) `{`

rkp_phys_map_unlock(pmd);

return 0;

`}`

if (start_addr &gt;&gt; 39)

type = KERNEL | L2;

else

type = L2;

res = rkp_phys_map_set(pmd, (start_addr &gt;&gt; 23) &amp; 0xFF80 | type);

if (res &lt; 0) `{`

rkp_phys_map_unlock(pmd);

return res;

`}`

res = rkp_s2_page_change_permission(pmd, 0x80, 0, 0);

if (res &lt; 0) `{`

uh_log('L', "rkp_l2pgt.c", 98, "Process l2t failed, %lx, %d", pmd, 1);

rkp_phys_map_unlock(pmd);

return res;

`}`

`}` else `{`

if (!is_phys_map_l2(pmd)) `{`

rkp_phys_map_unlock(pgd);

return 0;

`}`

if (table_addr &gt;= 0xFFFFFF8000000000)

rkp_policy_violation("Never allow free kernel page table %lx", pmd);

if (is_phys_map_kernel(pmd))

rkp_policy_violation("Entry must not point to kernel page table %lx", pmd);

res = rkp_phys_map_set(pmd, FREE);

if (res &lt; 0) `{`

rkp_phys_map_unlock(pgd);

return 0;

`}`

res = rkp_s2_page_change_permission(pmd, 0, 1, 0);

if (res &lt; 0) `{`

uh_log('L', "rkp_l2pgt.c", 123, "Process l2t failed, %lx, %d", pmd, 0);

rkp_phys_map_unlock(pgd);

return 0;

`}`

`}`

offset = 0;

for (i = 0; i != 0x1000; i += 8) `{`

addr = offset | start_addr &amp; 0xFFFFFFFFC01FFFFF;

res += check_single_l2e(pmd + i, addr, is_alloc);

offset += 0x200000;

`}`

rkp_phys_map_unlock(pgd);

return res;

`}`
```

函数rkp_l2pgt_process_table用于完成以下操作：

如果pmd_allocated_by_rkp为0（默认值）。

如果PMD是由RKP页分配器分配的，则将其设置为1，否则，将pmd_allocated_by_rkp设置为0(默认值)。

否则，将pmd_allocated_by_rkp设为-1。

如果VA&lt;0x8000000000且pmd_allocated_by_rkp为-1，则提前返回。

如果PMD正在被收回（retired）。

在physmap中查找标记为PMD的空间。

在physmap中确认找到的空间并非内核PMD。

在physmap中标记为free。

在第2阶段使其成为RWX（如果初始化则不允许）。

如果PMD正在被引入。

在physmap中查找已经标记为PMD的空间。

在physmap中将其标记为PMD。

在第2阶段，使其成为RO（如果初始化则不允许）。

然后，在这两种情况下，对于PMD的每个条目。

它都会调用check_single_l2e函数。

```
int64_t check_single_l2e(int64_t* desc_p, uint64_t start_addr, signed int32_t is_alloc) `{`

// ...



if (executable_regions_contains(start_addr, 2)) `{`

if (!is_alloc) `{`

uh_log('L', "rkp_l2pgt.c", 36, "RKP_61acb13b %lx, %lx", desc_p, *desc_p);

uh_log('L', "rkp_l2pgt.c", 37, "RKP_4083e222 %lx, %d, %d", start_addr, (start_addr &gt;&gt; 30) &amp; 0x1FF,

(start_addr &gt;&gt; 21) &amp; 0x1FF);

rkp_policy_violation("RKP_d60f7274");

`}`

protect = 1;

`}` else `{`

set_pxn_bit_of_desc(desc_p, 2);

protect = 0;

`}`

desc = *desc_p;

type = *desc &amp; 3;

if (type == 1)

return 0;

if (type != 3) `{`

if (desc)

uh_log('L', "rkp_l2pgt.c", 64, "Invalid l2e %p %p %p", desc, is_alloc, desc_p);

return 0;

`}`

if (protect)

uh_log('L', "rkp_l2pgt.c", 56, "L3 table to be protected, %lx, %d, %d", desc, (start_addr &gt;&gt; 21) &amp; 0x1FF,

(start_addr &gt;&gt; 30) &amp; 0x1FF);

if (!is_alloc &amp;&amp; start_addr &gt;= 0xFFFFFF8000000000) `{`

uh_log('L', "rkp_l2pgt.c", 58, "l2 table FREE-1 %lx, %d, %d", *desc_p, (start_addr &gt;&gt; 30) &amp; 0x1FF,

(start_addr &gt;&gt; 21) &amp; 0x1FF);

uh_log('L', "rkp_l2pgt.c", 59, "l2 table FREE-2 %lx, %d, %d", desc_p, 0x1FFFFFF, 0);

`}`

return rkp_l3pgt_process_table(*desc_p &amp; 0xFFFFFFFFF000, start_addr, is_alloc, protect);

`}`
```

函数check_single_l2e将执行以下操作：

如果VA位于executable_regions memlist中。

如果PMD正在被收回，则触发违规。

否则，将保护标志设为1。

否则，设置描述符的PXN位，并将protection设为0。

在这两种情况下，如果它是一个表，则调用rkp_l3pgt_process_table函数。

### 第三级

第三级表的处理由rkp_l3pgt_process_table函数完成。 

```
int64_t rkp_l3pgt_process_table(int64_t pte, uint64_t start_addr, uint32_t is_alloc, int32_t protect) `{`

// ...



cs_enter(&amp;l3pgt_lock);

if (!stext_ptep &amp;&amp; ((TEXT ^ start_addr) &amp; 0x7FFFE00000) == 0) `{`

stext_ptep = pte + 8 * ((TEXT &gt;&gt; 12) &amp; 0x1FF);

uh_log('L', "rkp_l3pgt.c", 74, "set stext ptep %lx", stext_ptep);

`}`

cs_exit(&amp;l3pgt_lock);

if (!protect)

return 0;

rkp_phys_map_lock(pte);

if (is_alloc) `{`

if (is_phys_map_l3(pte)) `{`

uh_log('L', "rkp_l3pgt.c", 87, "Process l3t SKIP %lx, %d, %d", pte, 1, start_addr &gt;&gt; 39);

rkp_phys_map_unlock(pte);

return 0;

`}`

if (start_addr &gt;&gt; 39)

type = KERNEL | L3;

else

type = L3;

res = rkp_phys_map_set(pte, type);

if (res &lt; 0) `{`

rkp_phys_map_unlock(pte);

return res;

`}`

res = rkp_s2_page_change_permission(pte, 0x80, 0, 0);

if (res &lt; 0) `{`

uh_log('L', "rkp_l3pgt.c", 102, "Process l3t failed %lx, %d", pte, 1);

rkp_phys_map_unlock(pte);

return res;

`}`

offset = 0;

desc_p = pte;

do `{`

addr = offset | start_addr &amp; 0xFFFFFFFFFFE00FFF;

if (addr &gt;&gt; 39) `{`

desc = *desc_p;

if (desc) `{`

if ((desc &amp; 3) != 3)

rkp_policy_violation("Invalid l3e, %lx, %lx, %d", desc, desc_p, 1);

if (!executable_regions_contains(addr, 3))

set_pxn_bit_of_desc(desc_p, 3);

`}`

`}` else `{`

uh_log('L', "rkp_l3pgt.c", 37, "L3t not kernel range, %lx, %d, %d", desc_p, (addr &gt;&gt; 30) &amp; 0x1FF,

(addr &gt;&gt; 21) &amp; 0x1FF);

`}`

offset += 0x1000;

++desc_p;

`}` while (offset != 0x200000);

`}` else `{`

if (!is_phys_map_l3(pte)) `{`

uh_log('L', "rkp_l3pgt.c", 110, "Process l3t SKIP, %lx, %d, %d", pte, 0, start_addr &gt;&gt; 39);

rkp_phys_map_unlock(pte);

return 0;

`}`

res = rkp_phys_map_set(pte, FREE);

if (res &lt; 0) `{`

rkp_phys_map_unlock(pte);

return res;

`}`

rkp_policy_violation("Free l3t not allowed, %lx, %d, %d", pte, 0, start_addr &gt;&gt; 39);

res = rkp_s2_page_change_permission(pte, 0, 1, 0);

if (res &lt; 0) `{`

uh_log('L', "rkp_l3pgt.c", 127, "Process l3t failed, %lx, %d", pte, 0);

rkp_phys_map_unlock(pte);

return res;

`}`

offset = 0;

desc_p = pte;

do `{`

addr = offset | start_addr &amp; 0xFFFFFFFFFFE00FFF;

if (addr &gt;&gt; 39) `{`

desc = *desc_p;

if (desc) `{`

if ((desc &amp; 3) != 3)

rkp_policy_violation("Invalid l3e, %lx, %lx, %d", *desc, desc_p, 0);

if (executable_regions_contains(addr, 3))

rkp_policy_violation("RKP_b5438cb1");

`}`

`}` else `{`

uh_log('L', "rkp_l3pgt.c", 37, "L3t not kernel range, %lx, %d, %d", desc_p, (addr &gt;&gt; 30) &amp; 0x1FF,

(addr &gt;&gt; 21) &amp; 0x1FF);

`}`

offset += 0x1000;

++desc_p;

`}` while (offset != 0x200000);

`}`

rkp_phys_map_unlock(pte);

return 0;

`}`
```

函数rkp_l3pgt_process_table的作用如下所示：

设置stext_ptep（text区段起始页表入口指针?），如果这个PTE和内核的text区段有相同的PGD/PUD/PMD索引，因此如果这个表覆盖内核的text区段。

如果保护标志为0，提前返回，否则继续。

如果正在引入PTE。

在physmap中查找尚未标记为PTE的空间。

将physmap中的这些空间标记为PTE。

它在第2阶段使其成为RO（如果初始化则不允许）。

对于PTE的每个条目。

如果它不是一个页面，则触发违规。

如果VA不在可执行区段内，则设置PXN位。

如果PTE正在收回。

在physmap中查找标记为PTE的空间。

将physmap中的这些空间标记为free。

触发违规。

在第2阶段使其成为RWX（如果初始化则不允许）。

对于PTE的每个条目。

如果它不是一个页面，则触发违规。

如果VA在可执行区段内，则触发违规。

如果页表处理函数发现了它们认为是违反策略的东西，它们就会调用rkp_policy_violation，并以描述违规的字符串作为第一个参数。 

```
int64_t rkp_policy_violation(const char* message, ...) `{`

// ...



res = rkp_log(0x4C, "rkp.c", 108, message, /* variable arguments */);

if (rkp_panic_on_violation)

uh_panic();

return res;

`}`
```

正常情况下，rkp_policy_violation函数将调用rkp_log；如果rkp_panic_on_violation已经启用，则调用uh_panic。函数rkp_log是函数uh_log的一个包装器，它将当前时间和CPU号码添加到消息中，并且，它还会调用bigdata_store_rkp_string函数将消息复制到分析区域。



## 阶段回顾

为了更好地了解RKP内部结构和管理程序控制的页表在启动完成后的整体状态，我们来回顾一下所有的结构体及其所包含的内容。 

Memlist dynamic_regions
1. 通过uh_init进行初始化。
1. S-Boot通过init_cmd_add_dynamic_region添加相关区域。
1. 通过init_cmd_initialize_dynamic_heap删除动态堆区域。 
Memlist protected_ranges
1. 通过pa_restrict_init进行初始化。
1. 通过pa_restrict_init添加0x87000000-0x87200000区域(uH区域)。
1. 通过init_cmd_initialize_dynamic_heap添加physmap的所有bitmap。 
Memlist page_allocator.list
1. 通过init_cmd_initialize_dynamic_heap进行初始化。
1. 通过init_cmd_initialize_dynamic_heap添加动态堆区域。
Memlist executable_regions
1. 通过rkp_start进行初始化。
1. 通过rkp_start添加TEXT-ETEXT。
1. 通过rkp_start添加TRAMP_VALIAS页面。
1. (通过dynamic_load_ins添加某些数值)
1. (通过dynamic_load_rm删除某些数值) 
Memlist dynamic_load_regions
1. 通过Rkp_start进行初始化。
1. （通过dynamic_load_add_dynlist添加某些值）
1. （通过dynamic_load_rm_dynlist删除某些值） 
Sparsemap physmap（基于dynamic_regions）
1. 通过init_cmd_initialize_dynamic_heap进行初始化。
1. 通过rkp_paging_init设置为TEXT-ETEXT。
1. 通过rkp_l1pgt_process_table将PGD(TTBR0_EL1)设置为L1。
1. 通过rkp_l2pgt_process_table将PMD(TTBR0_EL1)设置为L2。
1. 通过rkp_l3pgt_process_table将PTE(TTBR0_EL1)设置为L3，其中VA位于executable_regions中。
1. 通过rkp_l1pgt_process_table将PGD(swapper|tramp_pg_dir)设置为KERNEL|L1。
1. 通过rkp_l2pgt_process_table将PMD(swapper|tramp_pg_dir)设置为KERNEL|L2。
1. 通过rkp_l3pgt_process_table将PTE(swapper|tramp_pg_dir)设置为KERNEL|L3，其中VA位于executable_regions中。
1. (通过rkp_lxpgt_process_table对某些值进行修改)
1. (通过set_range_to_pxn|rox_l3对某些值进行修改)
1. (通过rkp_set_pages_ro, rkp_ro_free_pages对某些值进行修改) 
Sparsemap ro_bitmap（基于动态区域）
1. 通过init_cmd_initialize_dynamic_heap进行初始化。
1. 通过rkp_set_kernel_rox将ETEXT-ERODATA设置为1。
1. (通过rkp_s2_page_change_permission对某些值进行修改)
1. (通过rkp_s2_range_change_permission对某些值进行修改)
Sparsemap dbl_bitmap（基于动态区域）
1. 通过init_cmd_initialize_dynamic_heap进行初始化。
1. (通过rkp_set_map_bitmap对某些值进行修改)
Sparsemap robuf/page_allocator.map（基于动态区域）
1. 通过init_cmd_initialize_dynamic_heap进行初始化。
1. (通过page_allocator_alloc_page对某些值进行修改)
1. (通过page_allocator_free_page对某些值进行修改) 
第1阶段EL2的页表
<li data-list="bullet">
通过memory_init将0x87100000-0x87140000 (日志区域)映射为RW。</li>
1. 通过uh_init_bigdata将0x870FF000-0x87100000 (bigdata 区域) 映射为RW。
1. 通过S-Boot添加各个区域的结束位置，通过init_cmd_initialize_dynamic_heap解除0xA00000000的映射。
1. 通过rkp_paging_init将TEXT-ETEXT映射为RO。
1. 通过rkp_paging_init将swapper_pg_dir 页映射为RW。
1. (此列表不包括启动后的变化情况) 
第2阶段EL1的页表
1. 通过init_cmd_initialize_dynamic_heap将动态堆区域映射为RW。
1. 通过S-Boot添加各个区域的结束位置，通过init_cmd_initialize_dynamic_heap解除0xA00000000的映射。
1. 通过rkp_paging_init解除0x87000000-0x87200000(uH区域)的映射。
1. 通过rkp_paging_init将empty_zero_page映射为RWX。
1. 通过rkp_set_kernel_rox将TEXT-ERODATA(来自rkp_paging_init)映射为RWX。
1. 通过rkp_paging_init将0x87100000-0x87140000(日志区域)映射为ROX。
1. 通过rkp_paging_init将动态堆区域映射ROX。
1. 通过rkp_l1pgt_process_table将PGD(TTBR0_EL1)映射为RO。
1. 在块描述符上设置PXN位。
1. 在表描述符上设置PXN位，其中VA&lt;0x8000000000。
1. 通过rkp_l2pgt_process_table将PMD(TTBR0_EL1)映射为RO。
1. 通过check_single_l2e设置VA不在executable_regions中的描述符的PXN位。
1. 通过rkp_l3pgt_process_table将PTE(TTBR0_EL1)映射为RO，其中VA位于executable_regions中。
1. 通过rkp_set_kernel_rox (来自rkp_deferred_start)将TEXT-ERODATA映射为ROX。
1. 通过rkp_l1pgt_process_table将PGD(swapper|tramp_pg_dir)映射为RO。
1. 在块描述符上设置PXN位
1. 在表描述符上设置PXN位，其中VA&lt;0x8000000000。
1. 通过rkp_l2pgt_process_table将PMD(swapper|tramp_pg_dir)映射为RO。
1. 通过check_single_l2e设置VA不在executable_regions中的描述符的PXN位。
1. 通过rkp_l3pgt_process_table将PTE(swapper|tramp_pg_dir)映射为RO，其中VA位于executable_regions中。
1. 设置VA不在executable_regions中的描述符的PXN位。
1. (此列表不包括启动后的变化情况) 


## 小结

在本系列文章中，我们将为读者深入讲解三星手机的内核防护技术。在本文中，我们为读者详细介绍了页表的处理过程，并对前面的内容进行了阶段性的总结，在后续的文章中，会有更多精彩内容呈现给大家，敬请期待！

**（未完待续）**
