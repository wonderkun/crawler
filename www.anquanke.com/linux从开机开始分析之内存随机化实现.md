> 原文链接: https://www.anquanke.com//post/id/235482 


# linux从开机开始分析之内存随机化实现


                                阅读量   
                                **134358**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0xax，文章来源：0xax.gitbooks.io
                                <br>原文地址：[https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html](https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01bd5a70de59495861.png)](https://p3.ssl.qhimg.com/t01bd5a70de59495861.png)



上一部分我们进入内核启动进程的最后阶段,但是跳过了一些重要的部分

linux内核的入口点是定义在`main.c`源代码中的`start_kernel`函数,该函数在内存中储存在`LOAD_PHYSICAL_ADDR`.该地址取决于 `CONFIG_PHYSICAL_START` 内核选项,默认是`0x1000000`

```
config PHYSICAL_START
    hex "Physical address where the kernel is loaded" if (EXPERT || CRASH_DUMP)
    default "0x1000000"
    ---help---
      This gives the physical address where the kernel is loaded.
      ...
      ...
      ...
```

这个值可以在配置时被改变,如果需要这个功能,内核配置选项中`CONFIG_RANDOMIZE_BASE`应该被打开

现在,linux内核解压到的物理地址以及加载地址会是随机的.这个选项有一部分是为了安全性考虑



## 页表初始化

在解压器找到一个随机内存范围来解压内核之前,身份映射页表应该被初始化.如果加载器使用16位或32位启动协议,页表会正常初始化.但是如果解压器选择的内存范围仅能在64位的上下文中使用,这时就会出现问题.这是为什么需要再次更新页表

随机化内核加载地址的第一步是建立新的身份映射页表,但首先,我们看看如何获取地址点

前一部分中,在切换到长模式以及跳转到到解压器入口点`extract_kernel`函数.随机内存以对`choose_random_location`函数的调用开始

```
void choose_random_location(unsigned long input,
                            unsigned long input_size,
                            unsigned long *output,
                            unsigned long output_size,
                            unsigned long *virt_addr)
`{``}`
```

该函数的有五个参数
- `input`
<li>
`input_size`
<ul>
<li>
`output`;</li>
<li>
`output_isze`;</li>
<li>
`virt_addr`.</li>
```
asmlinkage __visible void *extract_kernel(void *rmode, memptr heap,
                                          unsigned char *input_data,
                                          unsigned long input_len,
                                          unsigned char *output,
                                          unsigned long output_len)
`{`
  ...
  ...
  ...
  choose_random_location((unsigned long)input_data, input_len,
                         (unsigned long *)&amp;output,
                         max(output_len, kernel_total_size),
                         &amp;virt_addr);
  ...
  ...
  ...
`}`
```

这些参数通过汇编指令传递

```
leaq    input_data(%rip), %rdx
```

`input_data`由一个小项目`mkpiggy`生成.如果你自己尝试过编译linux内核.你会发现输出由该项目生成`linux/arch/x86/boot/compressed/piggy.S`.在这里,这个项目看起来是这样的

```
.section ".rodata..compressed","a",@progbits
.globl z_input_len
z_input_len = 6988196
.globl z_output_len
z_output_len = 29207032
.globl input_data, input_data_end
input_data:
.incbin "arch/x86/boot/compressed/vmlinux.bin.gz"
input_data_end:
```

如你所见,它包含了4个全局符号,前两个是`z_input_len`和`z_output_len`,这两个代表压缩的和解压后的`vmlinux.bin.gz`大小.第三个是`input_data`参数,指向linux内核镜像二进制文件(已经去除了debug信息,重定位信息)最后一个参数是`input_data_end` 指向镜像文件的末尾.

所以,在`choose_random_location`函数中,第一个参数是指向压缩内核镜像的指针.

第二个参数是`z_input_len`

第三第四个参数是解压内核镜像的地址和它需要的大小,这个地址来自于 [arch/x86/boot/compressed/head_64.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_64.S) ,是`startup_32`地址通过2mb边界对齐的结果.

大小由`z_output_len`决定,同样在`piggy.s`中

最后一个参数是内核加载的虚拟地址,默认同步于物理加载地址

```
unsigned long virt_addr = LOAD_PHYSICAL_ADDR;
```

物理加载地址在配置选项中定义

```
#define LOAD_PHYSICAL_ADDR ((CONFIG_PHYSICAL_START \
                + (CONFIG_PHYSICAL_ALIGN - 1)) \
                &amp; ~(CONFIG_PHYSICAL_ALIGN - 1))
```

我们覆盖了`choose-random_location`的参数,因此我们看一看它的实现

首先检查命令行中`nokaslr`选项

```
if (cmdline_find_option_bool("nokaslr")) `{`
    warn("KASLR disabled: 'nokaslr' on cmdline.");
    return;
`}`
```

如果`nokaslr`被设置,则不适用随机地址;在内核文档中能看到对于这方面的信息.

```
kaslr/nokaslr [X86]

Enable/disable kernel and module base offset ASLR
(Address Space Layout Randomization) if built into
the kernel. When CONFIG_HIBERNATION is selected,
kASLR is disabled by default. When kASLR is enabled,
hibernation will be disabled.
```

假设我们不使用`nokaslr`参数, `CONFIG_RANDOMIZE_BASE` 选项可用,则将`kaslr`标志位加到内核加载标志中

```
boot_params-&gt;hdr.loadflags |= KASLR_FLAG;
```

接下来调用`initialize_identity_maps()`函数[arch/x86/boot/compressed/kaslr_64.c](https://github.com/torvalds/linux/blob/master/arch/x86/boot/compressed/kaslr_64.c)

`initialize_identity_maps()`首先初始化`x86_mapping_info`结构体 ,命名为`mapping_info`

```
mapping_info.alloc_pgt_page = alloc_pgt_page;
mapping_info.context = &amp;pgt_data;
mapping_info.page_flag = __PAGE_KERNEL_LARGE_EXEC | sev_me_mask;
mapping_info.kernpg_flag = _KERNPG_TABLE;
```

该结构体定义在 [arch/x86/include/asm/init.h](https://github.com/torvalds/linux/blob/v4.16/arch/x86/include/asm/init.h)头文件中.

```
struct x86_mapping_info `{`
    void *(*alloc_pgt_page)(void *);
    void *context;
    unsigned long page_flag;
    unsigned long offset;
    bool direct_gbpages;
    unsigned long kernpg_flag;
`}`;
```

结构体提供了内存映射的信息,在上一部分,我们已经覆盖`0`–`4g`的页表,但是这些页表在超出4g范围后就无法使用.因此`initialize_identity_maps()`函数为新的内存页表入口初始化内存.因此首先看看`x86-mapping_info`的定义.

`alloc_pgt_page`是一个用来获取使用空间的回调函数.`context`是是一个`alloc_pgt_data`的实例.通过它来追踪使用的页表. `page-flag`和`kernpg_flag`属于页的标志.第一个flag设置`PMD`或`PUD`入口.`kernpg_flag`提供为内核提供重写接口.`offset`代表虚拟地址和物理地址之间的差

`alloc_pgt_page`用来为页表入口点分配内存,检查一个新页的空间,分配它到`alloc_pgt_data`的`pgt_buf`区.并返回新页的地址

```
entry = pages-&gt;pgt_buf + pages-&gt;pgt_buf_offset;
pages-&gt;pgt_buf_offset += PAGE_SIZE;
```

`alloc_pgt_data`结构体

```
struct alloc_pgt_data `{`
    unsigned char *pgt_buf;
    unsigned long pgt_buf_size;
    unsigned long pgt_buf_offset;
`}`;
```

`initialize_identity_maps` 函数的最后目标是初始化`pgdt_buf_size`和`pgt_buf_offset`我们只在初始化阶段,因此将偏移设置成0;

```
pgt_data.pgt_buf_offset = 0;
```

`pgt-buf_size`被设置成 `77824` 或 `69632`,这取决于使用的引导器是32位还是64位.对于`pgt_buf`也是同样的原则.如果引导器在`startup_32`加载内核,`pgdt_buf`指向已初始化页表的末尾,

```
pgt_data.pgt_buf = _pgtable + BOOT_INIT_PGT_SIZE;
```

这里,`_pgtable`指向[_pgtable](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/vmlinux.lds.S)开头,

另外,如果使用`startup_64` 页表已经被引导自身处理完毕.`_pgtable`只需要指向这些表

```
pgt_data.pgt_buf = _pgtable
```

页表的缓存被初始化,我们返回到`choose_random_location`中



## 保留内存

在验证初始化页表后,选择一段随机的内存地址解压内核镜像,但我们不能随意选择内存地址,因为内存中有一部分保留空间.例如[initrd](https://en.wikipedia.org/wiki/Initial_ramdisk)和命令行所占的空间必须保留.这些保留空间由`mem-avoid_init`函数来实现.

```
mem_avoid_init(input, input_size, *output);
```

所有不安全的内存地区被收集在一个叫`memavoid`的数组里

```
struct mem_vector `{`
    unsigned long long start;
    unsigned long long size;
`}`;

static struct mem_vector mem_avoid[MEM_AVOID_MAX];
```

`MEM_AVOID_MAX`是`mem_avoid_index`枚举类型

```
enum mem_avoid_index `{`
    MEM_AVOID_ZO_RANGE = 0,
    MEM_AVOID_INITRD,
    MEM_AVOID_CMDLINE,
    MEM_AVOID_BOOTPARAMS,
    MEM_AVOID_MEMMAP_BEGIN,
    MEM_AVOID_MEMMAP_END = MEM_AVOID_MEMMAP_BEGIN + MAX_MEMMAP_REGIONS - 1,
    MEM_AVOID_MAX,
`}`;
```

这两个都定义在 [arch/x86/boot/compressed/kaslr.c](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/kaslr.c)中

在`mem_avoid_init`函数的实现中,主要目标是让`mem_avoid`数组通过`mem_avoid_index`的储存的保留地址信息

为新的映射缓冲区创建新的页.在`mem_avoid_index`函数中也是这么做的.

```
mem_avoid[MEM_AVOID_ZO_RANGE].start = input;
mem_avoid[MEM_AVOID_ZO_RANGE].size = (output + init_size) - input;
add_identity_map(mem_avoid[MEM_AVOID_ZO_RANGE].start,
         mem_avoid[MEM_AVOID_ZO_RANGE].size);
```

`mem_avoid_init`函数首先尝试禁止被解压内核占用的内存地址,将`mem_avoid[MEM_AVOID_ZO_RANG]`填充为入口点,以及所需内存的大小.随后调用`add_indentity_map`函数,该函数这一片内存设置认证.

```
void add_identity_map(unsigned long start, unsigned long size)
`{`
    unsigned long end = start + size;

    start = round_down(start, PMD_SIZE);
    end = round_up(end, PMD_SIZE);
    if (start &gt;= end)
        return;

    kernel_ident_mapping_init(&amp;mapping_info, (pgd_t *)top_level_pgt,
                  start, end);
`}`
```

​ `round_up``round_down`函数用来矫正开始和结束的地址偏移为2mb.

`add_identity_map`在最后调用`kernel_ident_mapping_init`.参数为已经初始化好的`mapping_info`实例.最高级页表的地址,,以及应该被新建的内存实例的开始结束地址.

`kernel_ident_mapping_init`函数为新页设置默认的标志位

```
if (!info-&gt;kernpg_flag)
    info-&gt;kernpg_flag = _KERNPG_TABLE;
```

然后开始建立新的2mb页入口(如果使用5级页表 则`PGD -&gt; P4D -&gt; PUD -&gt; PMD` ,如果是4级页表,则 `PGD -&gt; PUD -&gt; PMD`)并连接到给定的地址.

```
for (; addr &lt; end; addr = next) `{`
    p4d_t *p4d;

    next = (addr &amp; PGDIR_MASK) + PGDIR_SIZE;
    if (next &gt; end)
        next = end;

    p4d = (p4d_t *)info-&gt;alloc_pgt_page(info-&gt;context);
    result = ident_p4d_init(info, p4d, addr, next);

    return result;
`}`
```

在这个循环中首先为给定的地址寻找`PGD`,如果入口点的地址比给定地区的结束地址大,那么将大小设置为`end`

然后我们通过`x86_mapping_info`函数分配一个新页.调用`ident_p4d_init`函数,这个函数会为低一级的页表分配新页

到此

我们拥有了新的页入口接下来只需要为`initrd`和其他的一些数据建立页就行了

结束后返回`choose_random_location`函数



## 物理地址随机化

在保留内存被放在了`mem_avoid`后,为它们建立身份映射页表,我们选择最低的可用地址来进行解压

```
min_addr = min(*output, 512UL &lt;&lt; 20);
```

该地址应该在第一个512mb之内,之所以选择512是为了避免低内存地址中的一些数据的干扰

然后开始选择物理地址和虚拟地址来加载内核

第一个物理地址是

```
random_addr = find_random_phys_addr(min_addr, output_size);
```

`find_random_phys_addr()`定义在 [kasl,c](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/kaslr.c) 中.

```
static unsigned long find_random_phys_addr(unsigned long minimum,
                                           unsigned long image_size)
`{`
    minimum = ALIGN(minimum, CONFIG_PHYSICAL_ALIGN);

    if (process_efi_entries(minimum, image_size))
        return slots_fetch_random();

    process_e820_entries(minimum, image_size);
    return slots_fetch_random();
`}`
```

`process_efi_entries`函数的主要目标是寻找合适的可用的内存空间.如果编译内核或者是启动系统时没有EFI支持.我们会继续在e820空间中寻找这样的空间.所有被找到的可用的地址空间都被放在`slot_areas`中.

```
struct slot_area `{`
    unsigned long addr;
    int num;
`}`;

#define MAX_SLOT_AREA 100

static struct slot_area slot_areas[MAX_SLOT_AREA];
```

内核会选择一个随机的下标.这个选择的程序在`slots_fetch_random`中实现.该函数能在 `slot_areas`结构中选择出一个随机的内存范围

```
slot = kaslr_get_random_long("Physical") % slot_max;
```

`kaslr_get_random_long`定义在[arch/x86/lib/kaslr.c](https://github.com/torvalds/linux/blob/v4.16/arch/x86/lib/kaslr.c) ,返回随机数.这个数字能以很多种方式获取(如 :使用时间戳,rdrand等)



## 虚拟地址随机化

物理地址随机选择后,我们从身份验证页表为获取地址

```
random_addr = find_random_phys_addr(min_addr, output_size);

if (*output != random_addr) `{`
        add_identity_map(random_addr, output_size);
        *output = random_addr;
`}`
```

从现在开始,`output`储存内存区域的基地址,现在我们只随机化了物理地址.也能像在`x86_64`架构下一样,随机化虚拟地址

```
if (IS_ENABLED(CONFIG_X86_64))
    random_addr = find_random_virt_addr(LOAD_PHYSICAL_ADDR, output_size);

*virt_addr = random_addr;
```

在其他架构下,物理地址和虚拟地址的随机化也是同样的流程,`find_random_virt_addr`找出需要的大小范围,它调用`kaslr_get_random_long` 来进行更深一层的工作.



## Links
- [Address space layout randomization](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Linux kernel boot protocol](https://github.com/torvalds/linux/blob/v4.16/Documentation/x86/boot.txt)
- [long mode](https://en.wikipedia.org/wiki/Long_mode)
- [initrd](https://en.wikipedia.org/wiki/Initial_ramdisk)
- [Enumerated type](https://en.wikipedia.org/wiki/Enumerated_type#C)
- [four-level page tables](https://lwn.net/Articles/117749/)
- [five-level page tables](https://lwn.net/Articles/717293/)
- [EFI](https://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface)
- [e820](https://en.wikipedia.org/wiki/E820)
- [time stamp counter](https://en.wikipedia.org/wiki/Time_Stamp_Counter)
- [rdrand](https://en.wikipedia.org/wiki/RdRand)
- [x86_64](https://en.wikipedia.org/wiki/X86-64)