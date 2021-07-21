> 原文链接: https://www.anquanke.com//post/id/231029 


# TEE安全攻防之内存隔离


                                阅读量   
                                **169105**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t011e336c0fc02efe4a.png)](https://p0.ssl.qhimg.com/t011e336c0fc02efe4a.png)



## 前言

众所周知，Normal World的用户态与内核态的地址空间隔离是基于MMU分页来实现的，那么Normal World与Secure World的地址空间隔离是如何实现的呢？这篇文章将从CPU和OS的角度进行深入分析，并分析其中存在的安全风险。（**阅读本文需要了解ARM体系结构及TRUSTZONE的基础知识**）



## 硬件隔离机制

阅读ARM TrustZone手册可知，内存的隔离是由TZASC(TrustZone Address Space Controller)来控制 ，TZASC可以把外部DDR分成多个区域 ，每个区域可以单独配置为安全区域或非安全区域 ，Normal World的代码只能访问非安全区域。

[![](https://p2.ssl.qhimg.com/t01dac6149ac26af01d.png)](https://p2.ssl.qhimg.com/t01dac6149ac26af01d.png)

下面以TZC-380这款地址空间控制器来进行说明，其它型号控制器的原理也大同小异。

**通过配置 TZASC的寄存器来设置不同属性的region，一个region表示 一段连续的物理地址空间，TZASC给每个region提供了一个可编程的安全属性域，只有在Secure状态下才允许修改这些寄存器**，TZASC的基址不是固定的，不同厂商实现可能不同，但是每个寄存器的offset是固定的，如下所示：

[![](https://p1.ssl.qhimg.com/t01fb8926099cdb3322.png)](https://p1.ssl.qhimg.com/t01fb8926099cdb3322.png)

结合[OP-TEE代码](https://github.com/OP-TEE/optee_os/blob/9742eed4c9f48b886bd9bd40e7cbd80213baee00/core/drivers/tzc380.c)对配置 TZASC进行分析：

通过**对region对应的控制寄存器进行设置来配置安全内存地址空间**：

```
/*
 * `tzc_configure_region` is used to program regions into the TrustZone
 * controller.
 */
void tzc_configure_region(uint8_t region, vaddr_t region_base, uint32_t attr)
`{`
    assert(tzc.base);

    assert(region &lt; tzc.num_regions);

    /*
     * For region 0, this high/low/size/en field is Read Only (RO).
     * So should not configure those field for region 0.
     */
    if (region) `{`
        // 设置Region Setup Low &lt;n&gt; Register
        // 注意：region n的基址寄存器的[14:0]永远为0，因为 TZASC不允许region size小于32KB
        tzc_write_region_base_low(tzc.base, region,
                      addr_low(region_base));
        // 设置Region Setup High &lt;n&gt; Register,第n个region基址的[63:32]位
        // 和上面的low addr拼成完整的region基址
        tzc_write_region_base_high(tzc.base, region,
                       addr_high(region_base));
        // 设置Region Attributes &lt;n&gt; Register
        // 控制permissions,region size, subregion disable,and region enable
        tzc_write_region_attributes(tzc.base, region, attr);
    `}` else `{`
        // 第0个region的基址不需要设置 ，只需要设置region的属性
        tzc_write_region_attributes(tzc.base, region,
                        attr &amp; TZC_ATTR_SP_MASK);
    `}`
`}`
`
```

```
// 设置Region Setup Low &lt;n&gt; Register的值 
static void tzc_write_region_base_low(vaddr_t base, uint32_t region,
                      uint32_t val)
`{`
    // 定位到第region个Region对应的寄存器，即上图中的region_setup_low_n
    // tzasc基址寄存器+region control寄存器的偏移(0x100)+region n寄存器的size
    io_write32(base + REGION_SETUP_LOW_OFF(region), val);
`}`
```

通过阅读代码可知，tzc_configure_region是对第n个region的基址、大小和属性进行设置 ，其中属性寄存器的格式如下：

[![](https://p4.ssl.qhimg.com/t0189d5b26dc829b324.png)](https://p4.ssl.qhimg.com/t0189d5b26dc829b324.png)

> <p>**sp&lt;n&gt;: 第n个region的权限设置 ，当发生访问region时，sp&lt;n&gt;控制TZASC是否允许访问region。**<br>
size&lt;n&gt;:第n个region的大小 。<br>
subregion_disable&lt;n&gt;: region被划分为8个相同大小的sub-regions，第一位表示相应的subregion是否disabled。<br>
en&lt;n&gt;: 第n个region是否开启。</p>

在imx_configure_tzasc函数中对region进行了配置 ：

```
static TEE_Result imx_configure_tzasc(void)
`{`
    vaddr_t addr[2] = `{`0`}`;
    int end = 1;
    int i = 0;
    // TZASC基址
    addr[0] = core_mmu_get_va(TZASC_BASE, MEM_AREA_IO_SEC);
     ......

    for (i = 0; i &lt; end; i++) `{`
        uint8_t region = 1;
        // 从tzasc的配置寄存器中读取配置信息，包括region数量、地址总线宽度等 
        tzc_init(addr[i]);
        // tzc_auto_configure调用tzc_configure_region按regions_size对齐，并对内存空间进行属性设置
        //第1个region配置为CFG_DRAM_BASE起始的CFG_DDR_SIZE大小的非安全/安全状态可读写的内存
        region = tzc_auto_configure(CFG_DRAM_BASE, CFG_DDR_SIZE,
                 TZC_ATTR_SP_NS_RW, region);
        // 第2个region配置为CFG_TZDRAM_START起始的CFG_TZDRAM_SIZE大小 的安全状态可读写的内存（即安全内存）
        region = tzc_auto_configure(CFG_TZDRAM_START, CFG_TZDRAM_SIZE,
                 TZC_ATTR_SP_S_RW, region);
        // 第3个region配置为CFG_SHMEM_START起始的CFG_SHMEM_SIZE大小 的非安全/安全状态下可读写的内存（即共享内存）
        region = tzc_auto_configure(CFG_SHMEM_START, CFG_SHMEM_SIZE,
                 TZC_ATTR_SP_ALL, region);
        tzc_dump_state();
        if (tzc_regions_lockdown() != TEE_SUCCESS)
            panic("Region lockdown failed!");
    `}`
    return TEE_SUCCESS;
`}`
```

**Region 0用来设置整个地址空间的默认属性，它的基址为0，Size是由AXI_ADDRESS_MSB来配置**，因此Region 0除了安全属性字段之外，其它字段不允许设置。

**下面以第一个region为例，对安全属性进行分析：**<br>
第一个region的属性为TZC_ATTR_SP_NS_RW：

```
#define TZC_SP_NS_W        BIT(0)
#define TZC_SP_NS_R        BIT(1)
#define TZC_SP_S_W        BIT(2)
#define TZC_SP_S_R        BIT(3)

#define TZC_ATTR_SP_SHIFT    28 //属性位[28:31]

#define TZC_ATTR_SP_NS_RW    ((TZC_SP_NS_W | TZC_SP_NS_R) &lt;&lt; \
                TZC_ATTR_SP_SHIFT)
```

根据手册可知，TZC_SP_NS_W(b0001)是Non-secure write和 Secure write，TZC_SP_NS_R(b0010)是Non-secure read和Secure read，所以**TZC_ATTR_SP_NS_RW 表示 Non-secure和Secure状态可读写，即配置了DRAM地址空间的属性为非安全和安全状态都可以读写。**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01eb8da76498a0f8d2.png)

总结：<br>
以上代码配置了CFG_TZDRAM_START开始的CFG_TZDRAM_SIZE大小的地址空间为**安全内存**，即只有安全状态下(TCR.NS=0)可以访问。CFG_DRAM_BASE开始的CFG_DRAM_SIZE大小的地址空间为**普通内存**，安全和非安全状态下都可以访问。CFG_SHMEM_START开始的CFG_SHMEM_SIZE大小的地址空间为共享内存，安全和非安全状态都可以 访问 。

[OP-TEE物理内存布局:](https://github.com/OP-TEE/optee_os/blob/master/core/arch/arm/include/mm/generic_ram_layout.h)

```
* TEE RAM layout without CFG_WITH_PAGER
 *_
 *  +----------------------------------+ &lt;-- CFG_TZDRAM_START
 *  | TEE core secure RAM (TEE_RAM)    |
 *  +----------------------------------+
 *  | Trusted Application RAM (TA_RAM) |
 *  +----------------------------------+
 *  | SDP test memory (optional)       |
 *  +----------------------------------+ &lt;-- CFG_TZDRAM_START + CFG_TZDRAM_SIZE
 *
 *  +----------------------------------+ &lt;-- CFG_SHMEM_START
 *  | Non-secure static SHM            |
 *  +----------------------------------+ &lt;-- CFG_SHMEM_START + CFG_SHMEM_SIZE
```

至此，**已经完成了安全内存的配置**，接下来我们再来看下安全OS是如何使用这些物理内存的。



## TEEOS内存管理

[TEE OS启动时](https://github.com/OP-TEE/optee_os/blob/master/core/arch/arm/kernel/entry_a64.S)会调用core_init_mmu_map对安全内存地址空间进行映射 ：

```
#ifdef CFG_CORE_ASLR
    mov    x0, x20
    bl    get_aslr_seed        # x0用来保存开启aslr的seed
#else
    mov    x0, #0
#endif

    adr    x1, boot_mmu_config
    bl    core_init_mmu_map  # 记录PA和VA的对应关系，并初始化页表

    ......

    bl    __get_core_pos
    bl    enable_mmu           # 设置ttbr0_el1、tcr_el1， 开启分页，在开启页之前 ，VA==PA
```

core_init_mmu_map函数根据编译时注册的物理内存地址信息对页表进行初始化，也就是对物理内存进行内存映射：

```
void __weak core_init_mmu_map(unsigned long seed, struct core_mmu_config *cfg)
`{`
#ifndef CFG_VIRTUALIZATION
    // __nozi_start在链接脚本中指定，一级页表的地址
    vaddr_t start = ROUNDDOWN((vaddr_t)__nozi_start, SMALL_PAGE_SIZE);
#else
    vaddr_t start = ROUNDDOWN((vaddr_t)__vcore_nex_rw_start,
                  SMALL_PAGE_SIZE);
#endif
    vaddr_t len = ROUNDUP((vaddr_t)__nozi_end, SMALL_PAGE_SIZE) - start;
    struct tee_mmap_region *tmp_mmap = get_tmp_mmap();
    unsigned long offs = 0;
    // 检查安全和非安全区域是否有重叠，如果有重叠，则系统panic
    check_sec_nsec_mem_config();
    // static_memory_map记录mmap_region的PA、VA，用来PA/VA转换
    // 第一个mmap_region记录的是一级页表的PA和VA
    static_memory_map[0] = (struct tee_mmap_region)`{`
        .type = MEM_AREA_TEE_RAM,        // region 的内存类型
        .region_size = SMALL_PAGE_SIZE,   // 内存粒度
        .pa = start,  
        .va = start,                                
        .size = len,
        .attr = core_mmu_type_to_attr(MEM_AREA_IDENTITY_MAP_RX),
    `}`;

    COMPILE_TIME_ASSERT(CFG_MMAP_REGIONS &gt;= 13);
    // 初始化内存信息表，即记录下各region的PA/VA，用来PV/VA转换
    // 后面也会根据这些信息对页表进行初始化
    offs = init_mem_map(tmp_mmap, ARRAY_SIZE(static_memory_map), seed);

    check_mem_map(tmp_mmap);
    core_init_mmu(tmp_mmap);  // 初始化页表，进行内存映射
    dump_xlat_table(0x0, 1);
    core_init_mmu_regs(cfg);  // 记录页表基址，用来设置TTBR0
    cfg-&gt;load_offset = offs;
    memcpy(static_memory_map, tmp_mmap, sizeof(static_memory_map));
`}`
```

上面函数首先调用init_mem_map初始化一个内存信息表，**记录下各Region的PA和VA，此表用来物理地址和虚拟地址转换，后面页表初始化时也会根据此表进行填充。**

```
static unsigned long init_mem_map(struct tee_mmap_region *memory_map,
                  size_t num_elems, unsigned long seed)
`{`
    /*
     * @id_map_start and @id_map_end describes a physical memory range
     * that must be mapped Read-Only eXecutable at identical virtual
     * addresses.
     */
    vaddr_t id_map_start = (vaddr_t)__identity_map_init_start;
    vaddr_t id_map_end = (vaddr_t)__identity_map_init_end;
    unsigned long offs = 0;
    size_t last = 0;
    // 根据已注册的物理地址空间信息来设置memory_map中tee_mmap_region的物理地址范围（即PA、SIZE）
    last = collect_mem_ranges(memory_map, num_elems);
    // 设置memory_map中tee_mmap_region的region_size（内存粒度）
    // 如果是tee侧的安全内存，则设置region_size为SMALL_PAGE_SIZE(4K)
    assign_mem_granularity(memory_map);

    /*
     * To ease mapping and lower use of xlat tables, sort mapping
     * description moving small-page regions after the pgdir regions.
     */
    qsort(memory_map, last, sizeof(struct tee_mmap_region),
          cmp_init_mem_map);
    // 添加一个MEM_AREA_PAGER_VASPACE类型的tee_mmap_region
    add_pager_vaspace(memory_map, num_elems, &amp;last);
    if (IS_ENABLED(CFG_CORE_ASLR) &amp;&amp; seed) `{`
        // 如果开启了ASLR，则将安全内存起始地址加上一个随机值
        vaddr_t base_addr = TEE_RAM_START + seed;
        const unsigned int va_width = get_va_width();
        const vaddr_t va_mask = GENMASK_64(va_width - 1,
                           SMALL_PAGE_SHIFT);
        vaddr_t ba = base_addr;
        size_t n = 0;

        for (n = 0; n &lt; 3; n++) `{`
            if (n)
                ba = base_addr ^ BIT64(va_width - n);
            ba &amp;= va_mask;  // 得到一个有效的VA，按页对齐并且高位无效位清零
            if (assign_mem_va(ba, memory_map) &amp;&amp; // 设置memory_map中PA对应的VA为ba，已经随机化
                mem_map_add_id_map(memory_map, num_elems, &amp;last, 
                           id_map_start, id_map_end)) `{` //// 向memory_map数组中添加一个region, PA为id_map_start
                offs = ba - TEE_RAM_START;
                DMSG("Mapping core at %#"PRIxVA" offs %#lx",
                     ba, offs);
                goto out;
            `}` else `{`
                DMSG("Failed to map core at %#"PRIxVA, ba);
            `}`
        `}`
        EMSG("Failed to map core with seed %#lx", seed);
    `}`
    // 未开启ASLR，则设置memory_map中PA对应的VA为TEE_RAM_START,即PA==VA
    // 注意，va和size必须以region_size对齐，memory_map中region的PA可能不是连续的，
    // 但是VA地址空间是连续的
    if (!assign_mem_va(TEE_RAM_START, memory_map))
        panic();

out:
    qsort(memory_map, last, sizeof(struct tee_mmap_region),
          cmp_mmap_by_lower_va);

    dump_mmap_table(memory_map);

    return offs;
`}`
```

其中，collect_mem_ranges根据编译时保存到phys_mem_map节中物理内存信息来设置memory_map中tee_mmap_region的物理地址范围 。

```
// 根据已注册的物理地址空间信息设置memory_map数组中tee_mmap_region的物理地址范围
static size_t collect_mem_ranges(struct tee_mmap_region *memory_map,
                 size_t num_elems)
`{`
    const struct core_mmu_phys_mem *mem = NULL;
    size_t last = 0;
    // 根据phys_mem_map设置memory_map(用于记录region的PA/VA的对应关系）的PA、SIZE和attr
    // phys_mem_map_begin是phys_mem_map数组的起始地址
    for (mem = phys_mem_map_begin; mem &lt; phys_mem_map_end; mem++) `{`
        struct core_mmu_phys_mem m = *mem;

        /* Discard null size entries */
        if (!m.size)
            continue;

        /* Only unmapped virtual range may have a null phys addr */
        assert(m.addr || !core_mmu_type_to_attr(m.type));
        // 根据phy_mem_map设置memory_map的物理地址范围及属性
        add_phys_mem(memory_map, num_elems, &amp;m, &amp;last);
    `}`

#ifdef CFG_SECURE_DATA_PATH
    // 首先检查 phys_sdp_mem地址空间是否有重叠
    // 然后检查 memory_map与phys_sdp_mem的地址空间是否有重叠，有重叠则panic
    verify_special_mem_areas(memory_map, num_elems, phys_sdp_mem_begin,
                 phys_sdp_mem_end, "SDP");
    check_sdp_intersection_with_nsec_ddr();
#endif
    // 检查memory_map与非安全地址空间phys_nsec_addr是否有重叠
    verify_special_mem_areas(memory_map, num_elems, phys_nsec_ddr_begin,
                 phys_nsec_ddr_end, "NSEC DDR");

    // 插入到memory_map中一个MEM_AREA_RES_VASPACE类型的map_region
    // memory_map中的map_region按type从小到大进行了排序 
    add_va_space(memory_map, num_elems, MEM_AREA_RES_VASPACE,
             CFG_RESERVED_VASPACE_SIZE, &amp;last);

    add_va_space(memory_map, num_elems, MEM_AREA_SHM_VASPACE,
             SHM_VASPACE_SIZE, &amp;last);

    memory_map[last].type = MEM_AREA_END;

    return last;
`}`
```

通过 register_phys_mem 这个宏将TEE、非安全的共享内存的物理地址空间编译到phys_mem_map这个section。

```
register_phys_mem(MEM_AREA_TEE_RAM, TEE_RAM_START, TEE_RAM_PH_SIZE);
register_phys_mem(MEM_AREA_TA_RAM, TA_RAM_START, TA_RAM_SIZE);
register_phys_mem(MEM_AREA_NSEC_SHM, TEE_SHMEM_START, TEE_SHMEM_SIZE);
register_sdp_mem(CFG_TEE_SDP_MEM_BASE, CFG_TEE_SDP_MEM_SIZE);
register_phys_mem_ul(MEM_AREA_TEE_RAM_RW, VCORE_UNPG_RW_PA, VCORE_UNPG_RW_SZ);
.....
```

register_phys_mem这个宏使用关键字”section”将修饰的变量按照core_mmu_phys_mem结构体编译到phys_mem_map这个section中。phys_mem_map_begin指向phys_mem_map这个section的起始地址 。collect_mem_ranges会根据这个section的信息初始化static_memory_map内存信息数组,这个数组用来 记录各region的PA、VA、内存属性、地址空间范围等信息。

```
#define register_phys_mem(type, addr, size) \
        __register_memory(#addr, (type), (addr), (size), \
                  phys_mem_map)

#define __register_memory(_name, _type, _addr, _size, _section) \
    SCATTERED_ARRAY_DEFINE_ITEM(_section, struct core_mmu_phys_mem) = \
        `{` .name = (_name), .type = (_type), .addr = (_addr), \
          .size = (_size) `}`
```

值得注意的是，上面注册的TEE_RAM_START开始的物理地址空间就是TZC-380配置的Region 2，**即安全内存地址空间。**

```
#define TEE_RAM_START        TZDRAM_BASE
#define TEE_RAM_PH_SIZE        TEE_RAM_VA_SIZE
#define TZDRAM_BASE        CFG_TZDRAM_START
#define TZDRAM_SIZE        CFG_TZDRAM_SIZE
```

接下来， core_init_mmu调用core_init_mmu_ptn来对整个注册的内存地址空间进行VA到PA的映射，即根据PA和VA填充页表。

```
void core_init_mmu_prtn(struct mmu_partition *prtn, struct tee_mmap_region *mm)
`{`
    size_t n;

    assert(prtn &amp;&amp; mm);

    for (n = 0; !core_mmap_is_end_of_table(mm + n); n++) `{`
        debug_print(" %010" PRIxVA " %010" PRIxPA " %10zx %x",
                mm[n].va, mm[n].pa, mm[n].size, mm[n].attr);

        if (!IS_PAGE_ALIGNED(mm[n].pa) || !IS_PAGE_ALIGNED(mm[n].size))
            panic("unaligned region");
    `}`

    /* Clear table before use */
    memset(prtn-&gt;l1_tables, 0, sizeof(l1_xlation_table));

    for (n = 0; !core_mmap_is_end_of_table(mm + n); n++)
        //如果不是动态虚拟地址空间，则进行填充页表（映射内存）
        if (!core_mmu_is_dynamic_vaspace(mm + n))            
            // 根据PA/VA填充页表，即做内存映射 
            core_mmu_map_region(prtn, mm + n);

    /*
     * Primary mapping table is ready at index `get_core_pos()`
     * whose value may not be ZERO. Take this index as copy source.
     */
     // 根据已设置的页表设置所有核的页表
    for (n = 0; n &lt; CFG_TEE_CORE_NB_CORE; n++) `{`
        if (n == get_core_pos())
            continue;

        memcpy(prtn-&gt;l1_tables[0][n],
               prtn-&gt;l1_tables[0][get_core_pos()],
               XLAT_ENTRY_SIZE * NUM_L1_ENTRIES);
    `}`
`}`
```

到这里，**TEE侧OS已经完成了对物理内存的映射**，包括安全内存和共享内存。在开启分页后，TEEOS就可以访问这些虚拟内存地址空间了。



## 安全侧地址校验

下面以符合GP规范的TEE接口为例，简单介绍下CA和TA的通信流程：

[![](https://p2.ssl.qhimg.com/t010fe7236bd3f3551d.png)](https://p2.ssl.qhimg.com/t010fe7236bd3f3551d.png)

篇幅所限，这里仅分析Secure World侧的调用流程，重点关注TA_InvokeCommandEntryPoint调用流程，此函数用来处理所有来自Normal World侧的请求，安全侧可信应用的漏洞挖掘也是从这个函数开始入手，这里我们只分析地址校验相关流程。

1.在TEEC_OpenSession中会去**加载TA的elf文件**，并设置相应的函数操作表，最终调用目标TA的TA_OpenSessionEntryPoint。

```
__tee_entry_std
    --&gt; entry_open_session
    --&gt; tee_ta_open_session
          --&gt; tee_ta_init_session --&gt; tee_ta_init_user_session --&gt; set_ta_ctx_ops
          --&gt; ctx-&gt;ops-&gt;enter_open_session (user_ta_enter_open_session)
                --&gt; user_ta_enter
                     --&gt; tee_mmu_map_param
                     --&gt; thread_enter_user_mode
                          --&gt; __thread_enter_user_mode // 返回到S_EL0，调用目标TA的TA_OpenSessionEntryPoint
```

2.TA_InvokeCommandEntryPoint调用流程如下，在此函数中会对REE传入的地址进行校验。

```
__tee_entry_std
   --&gt; entry_invoke_command
         --&gt; copy_in_param
              --&gt; set_tmem_param   // 如果是memref类型，则调用set_tmem_param分配共享内存
                  --&gt; msg_param_mobj_from_nocontig
                      --&gt; mobj_mapped_shm_alloc
                           --&gt; mobj_reg_shm_alloc // 最终会调用 core_pbuf_is来检查RRE传入的PA是否在非安全内存地址 范围内
         --&gt; tee_ta_get_session
         --&gt; tee_ta_invoke_command
              --&gt; check_params 
              --&gt; sess-&gt;ctx-&gt;ops-&gt;enter_invoke_cmd (user_ta_enter_invoke_cmd)
                   --&gt; user_ta_enter
                        --&gt; tee_mmu_map_param // 映射用户空间地址 (S_EL0)
                        --&gt; tee_ta_push_current_session
                        --&gt; thread_enter_user_mode // 返回S_EL0相应 的TA中执行TA_InvokeCommandEntryPoint
```

通过以上代码分析可知，在调用TA的TA_InvokeCommandEntryPoint函数之前会对REE侧传入的参数类型进行检查 ，在TA代码中使用REE传入参数作为内存地址的场景下，如果未校验对应的参数类型或者参数类型为TEEC_VALUE_INPUT（与实际使用参数类型不匹配），则会绕过上面core_pbuf_is对REE传入PA的检查 ，可以传入任意值，这个值可以为安全内存PA，这样就可以**导致以S_EL0权限读写任意安全内存**。



## 总结

TEE作为可信执行环境，通常用于运行处理指纹、人脸、PIN码等关键敏感信息的可信应用，即使手机被ROOT，攻击者也无法获取这些敏感数据。因此TEE侧程序的安全至关重要，本文深入分析了TRUSTZONE物理内存隔离、TEEOS内存管理及TEE侧对REE传入地址的校验。在了解了这些原理之后，我们就可以进行漏洞挖掘了， 当然也能写出简单有效的FUZZ工具。只有对漏洞原理、攻击方法进行深入的理解 ，才能进行有效的防御。

PS: 荣耀安全实验室是公司内专注于攻防研究的部门，这里有自由和开放的技术研究氛围，待遇优厚，欢迎有志于移动安全的大牛小牛加入我们！有意请联系：[ryaqgf@gmail.com](mailto:ryaqgf@gmail.com)，工作地点：北京



## 参考

1.TrustZone Address Space Controller TZC-380 Technical Reference Manual<br>
2.GlobalPlatform Device Technology TEE Client API Specification<br>
3.GlobalPlatform Device Technology TEE Internal API Specification<br>
4.Arm Trusted Firmware<br>
5.OP-TEE
