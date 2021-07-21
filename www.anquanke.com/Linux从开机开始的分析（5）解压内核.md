> 原文链接: https://www.anquanke.com//post/id/233115 


# Linux从开机开始的分析（5）解压内核


                                阅读量   
                                **223546**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0xax，文章来源：0xax.gitbooks.io
                                <br>原文地址：[https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html](https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01bd5a70de59495861.png)](https://p3.ssl.qhimg.com/t01bd5a70de59495861.png)



## 内核解压

接下来开始进行内核的解压系列,上一部分完成了对64-bit的转换,下面我们将看到内核解压之前的准备工作,重定位,以及解压流程本身



## 对解压本身的准备

上一部分我们的函数流程在`64-bit`入口点, `startup_64` 处停下. 这一部分源代码在 [arch/x86/boot/compressed/head_64.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_64.S)

在这之前我们已经加载了`GDT`表并且CPU也已经进入了新的处理模式,在`startup_64`函数中我们重新设置了段寄存器

```
.code64
    .org 0x200
ENTRY(startup_64)
    xorl    %eax, %eax
    movl    %eax, %ds
    movl    %eax, %es
    movl    %eax, %ss
    movl    %eax, %fs
    movl    %eax, %gs
```

除了`cs`寄存器以外的全部段寄存器都被重新设置,

下一步是计算内核编译时被指定加载的位置与它实际位置之间的差别

```
#ifdef CONFIG_RELOCATABLE
    leaq    startup_32(%rip), %rbp
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
    movl    BP_init_size(%rsi), %ebx
    subl    $_end, %ebx
    addq    %rbp, %rbx
```

`rbp`里写入解压内核的初始地址,在代码执行后,`rbx`寄存器会包含解压内核的代码被重定向后的地址.这是在上一部分中已经做过.但是在这里需要重新再计算一次,,因为现在bootloader可以使用64位的协议,而且`startup_32`不再被执行.

在下一步中,我们设置栈指针,重新设置标志位,再次从`64-bit`协议中设置`GDT`来覆盖`32-bit`中的特殊值

```
leaq    boot_stack_end(%rbx), %rsp

    leaq    gdt(%rip), %rax
    movq    %rax, gdt64+2(%rip)
    lgdt    gdt64(%rip)

    pushq    $0
    popfq
```

在`lgdt gdt64(%rip)`后有另外的代码,这些代码创建了允许5级页表的空间(如果需要的话).我们这里只考虑4级页表

`rbx`包含了解压器代码的初始地址,我们只将这个地址加上`boot_stack_end`放在`rsp`寄存器里.即栈顶位置修改.这样栈就被矫正.你可以在[arch/x86/boot/compressed/head_64.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_64.S)的最后看到`bootstack_end`的定义

```
.bss
    .balign 4
boot_heap:
    .fill BOOT_HEAP_SIZE, 1, 0
boot_stack:
    .fill BOOT_STACK_SIZE, 1, 0
boot_stack_end:
```

它位于`.bss`段末尾,`.pgtable`前,如果你深入阅读[arch/x86/boot/compressed/vmlinux.lds.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/vmlinux.lds.S)链接脚本,你能在其中找到这两个的定义

栈现在已经被调整,在计算出重定位后的地址,我们拷贝压缩的内核到我们得到的地址,在更深一步讨论前,先看一看接下来的代码

```
pushq    %rsi
    leaq    (_bss-8)(%rip), %rsi
    leaq    (_bss-8)(%rbx), %rdi
    movq    $_bss, %rcx
    shrq    $3, %rcx
    std
    rep    movsq
    cld
    popq    %rsi
```

这些指令将压缩的内核拷贝到合适的地址

首先将`rsi`的值压入栈来保存它的值,因为这个寄存器现在保存着指向`boot_params`即实模式结构体,包含了引导相关的信息,(记住,这个结构体在内核设置阶段很重要) 在执行完我们的代码后,这个值需要被返回到`rsi`寄存器

接下来的两个`leaq`指令计算出`rip` `rbx`有效的地址通过`_bss-8`的偏移.并把结果放入`rsi` `rdi`寄存器中,为什么我们计算这些地址,压缩过的内核镜像位于当前代码(现在的地址到`startup_32`间)与解压代码之间.在链接脚本中可以看到- [arch/x86/boot/compressed/vmlinux.lds.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/vmlinux.lds.S):

```
. = 0;
    .head.text : `{`
        _head = . ;
        HEAD_TEXT
        _ehead = . ;
    `}`
    .rodata..compressed : `{`
        *(.rodata..compressed)
    `}`
    .text :    `{`
        _text = .;     /* Text */
        *(.text)
        *(.text.*)
        _etext = . ;
    `}`
```

注意`.head.text`段包含了`startup_32`

`.text`段包含了解压代码

```
.text
relocated:
...
...
...
/*
 * Do the decompression, and jump to the new kernel..
 */
...
```

`.rodata..compressed`包含了压缩的内核镜像,因此`rsi`包含`_bss-8`绝对地址,`rdi`包含了

`rdi`包含了`_bss-8`重定位相关地址.在链接器你看到的一样,它位于所有段之后.

然后开始复制从`rsi`到`rdi`里,用`movq`指令 8byte一次,

注意在我们执行复制数据前的`std`语句 ,这设置了`DF`标志位,这意味着`rsi`和`rdi`会减少,换句话说,我们会向后复制.最后清除`DF`位,重新储存`boot_params`结构体到`rsi`寄存器

现在我们有了指向`.text`地址的指针,跳转到那里

```
leaq    relocated(%rbx), %rax
    jmp    *%rax
```



## 在内核解压前 最后操作

在前一段中我们看到`.text`段以`relocated`标签开始,我们先清理`.bss`段

```
xorl    %eax, %eax
    leaq    _bss(%rip), %rdi
    leaq    _ebss(%rip), %rcx
    subq    %rdi, %rcx
    shrq    $3, %rcx
    rep    stosq
```

我们需要初始化`.bss`段,因为很快就跳转到c语言代码处,这里我们只清理`eax` 将`_bss`地址放在`rdi`中 `_ebss`放在`rcx`中, 用`rep stosp`将`.bss`段清零.

最后,我们能看到一个对`extract_kernel`的调用

```
pushq    %rsi
    movq    %rsi, %rdi
    leaq    boot_heap(%rip), %rsi
    leaq    input_data(%rip), %rdx
    movl    $z_input_len, %ecx
    movq    %rbp, %r8
    movq    $z_output_len, %r9
    call    extract_kernel
    popq    %rsi
```

像之前一样,`rsi`入栈来保存`boot_params`,将rsi的值赋给rdi ,然后我们让rsi指向内核被解压到的地址,最后一步是为`extract_kernel`准备参数,然后调用它来解压内核,这个函数定义在[arch/x86/boot/compressed/misc.c](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/misc.c) 以及带有6个参数
<li>
`rmode` -指针 指向`boot_params`结构体</li>
<li>
`heap` 指向`boot_heap` 的指针 代表引导堆区的地址</li>
<li>
`input_data` 指向压缩内核,或者说指向`arch/x86/boot/compressed/vmlinux.bin.bz2` 文件</li>
<li>
`input_len` 压缩内核大小</li>
<li>
`out_put` 解压内核的开始地址</li>
<li>
`output_len` 解压内核的大小</li>
这些参数通过寄存器传递,到这里完成准备,并进行解压



## 内核解压

前一段中,`extract_kernel`函数定义在[arch/x86/boot/compressed/misc.c](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/misc.c) 六个参数 .这个函数和视频/窗口初始化开始,我们需要再次进行初始化因为我们不知道是否是我们从实模式开始,还是我们使用的引导器 开始

在初始化完成第一步,我们保存指向空闲内存的开始点,以及结束点

```
free_mem_ptr     = heap;
free_mem_end_ptr = heap + BOOT_HEAP_SIZE;
```

这里 heap是该函数的第二个参数

```
leaq    boot_heap(%rip), %rsi

boot_heap:
    .fill BOOT_HEAP_SIZE, 1, 0
```

`BOOT_HEAP_SIZE`是一个宏,展开后是`0x10000`(如果是`bzip2`内核的话是`0x400000`)

初始化堆指针后,下一步是调用`choose_random_location`函数 在 [arch/x86/boot/compressed/kaslr.c](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/kaslr.c) 里.从函数名称猜测 , 他选择了一个内存地址来写入解压后的内核.这可能有些奇怪,我们选择那里来解压内核镜像 .但是为了安全,linux内核支持`KASLR` 允许解压内核到随即地址,为了安全.

我们会在下一部分看一看内核加载地址是如何进行随机化的

现在我们会到 `misc.c` 在获取到地址后,我们需要检查随机地址是否正确的偏移,或者说,没有出错

```
if ((unsigned long)output &amp; (MIN_KERNEL_ALIGN - 1))
    error("Destination physical address inappropriately aligned");

if (virt_addr &amp; (MIN_KERNEL_ALIGN - 1))
    error("Destination virtual address inappropriately aligned");

if (heap &gt; 0x3fffffffffffUL)
    error("Destination address too large");

if (virt_addr + max(output_len, kernel_total_size) &gt; KERNEL_IMAGE_SIZE)
    error("Destination virtual address is beyond the kernel mapping area");

if ((unsigned long)output != LOAD_PHYSICAL_ADDR)
    error("Destination address does not match LOAD_PHYSICAL_ADDR");

if (virt_addr != LOAD_PHYSICAL_ADDR)
    error("Destination virtual address changed when not relocatable");
```

在这些检查过后,我们会看见一条很熟悉的信息

```
Decompressing Linux...
```

现在我们调用 `__decompress`函数来解压内核

```
__decompress(input_data, input_len, NULL, NULL, output, output_len, NULL, error);
```

`__decompress`的声明取决于选择什么算法来解压内核

```
#ifdef CONFIG_KERNEL_GZIP
#include "../../../../lib/decompress_inflate.c"
#endif

#ifdef CONFIG_KERNEL_BZIP2
#include "../../../../lib/decompress_bunzip2.c"
#endif

#ifdef CONFIG_KERNEL_LZMA
#include "../../../../lib/decompress_unlzma.c"
#endif

#ifdef CONFIG_KERNEL_XZ
#include "../../../../lib/decompress_unxz.c"
#endif

#ifdef CONFIG_KERNEL_LZO
#include "../../../../lib/decompress_unlzo.c"
#endif

#ifdef CONFIG_KERNEL_LZ4
#include "../../../../lib/decompress_unlz4.c"
#endif
```

在内核解压后,`parse_elf`和`handle_relocations`这两个函数被调用,要点是将解压后的啮合移动到内存中合适的位置,,我们已经知道的,内核是可执行的`ELF`文件,`parse_elf`的主要目标是将可定位的段放到合适的地址,我们能看到内核的可加载段.

```
readelf -l vmlinux

Elf file type is EXEC (Executable file)
Entry point 0x1000000
There are 5 program headers, starting at offset 64

Program Headers:
  Type           Offset             VirtAddr           PhysAddr
                 FileSiz            MemSiz              Flags  Align
  LOAD           0x0000000000200000 0xffffffff81000000 0x0000000001000000
                 0x0000000000893000 0x0000000000893000  R E    200000
  LOAD           0x0000000000a93000 0xffffffff81893000 0x0000000001893000
                 0x000000000016d000 0x000000000016d000  RW     200000
  LOAD           0x0000000000c00000 0x0000000000000000 0x0000000001a00000
                 0x00000000000152d8 0x00000000000152d8  RW     200000
  LOAD           0x0000000000c16000 0xffffffff81a16000 0x0000000001a16000
                 0x0000000000138000 0x000000000029b000  RWE    200000
```

`parse_elf`函数的目标是加载这些段到`output`地址(我们通过`choose_random_location`获取到的地址)该函数开始于检查和`ELF`标志位

```
Elf64_Ehdr ehdr;
Elf64_Phdr *phdrs, *phdr;

memcpy(&amp;ehdr, output, sizeof(ehdr));

if (ehdr.e_ident[EI_MAG0] != ELFMAG0 ||
    ehdr.e_ident[EI_MAG1] != ELFMAG1 ||
    ehdr.e_ident[EI_MAG2] != ELFMAG2 ||
    ehdr.e_ident[EI_MAG3] != ELFMAG3) `{`
        error("Kernel is not a valid ELF file");
        return;
`}`
```

如果ELF头不对,便输出错误信息.如果elf头合法,就遍历所有的给出ELF头的程序,以2mb偏移复制所有的可加载段到输出缓冲区

```
for (i = 0; i &lt; ehdr.e_phnum; i++) `{`
        phdr = &amp;phdrs[i];

        switch (phdr-&gt;p_type) `{`
        case PT_LOAD:
#ifdef CONFIG_X86_64
            if ((phdr-&gt;p_align % 0x200000) != 0)
                error("Alignment of LOAD segment isn't multiple of 2MB");
#endif
#ifdef CONFIG_RELOCATABLE
            dest = output;
            dest += (phdr-&gt;p_paddr - LOAD_PHYSICAL_ADDR);
#else
            dest = (void *)(phdr-&gt;p_paddr);
#endif
            memmove(dest, output + phdr-&gt;p_offset, phdr-&gt;p_filesz);
            break;
        default:
            break;
        `}`
    `}`
```

从这里开始 所有的可加载段都处于正确的位置,

下一步是调用`handle_relocations`,这函数的定义取决于`CONFIG_X86_NEED_RELOCS`内核选项.

如果是被允许的,函数矫正内核镜像的地址 , 这个函数在`CONFIG_RANDOMIZE_BASE`被设置时也会被第调用.

`handle_relocations`的声明足够简单,函数将基础加载地址减去`LOAD_PHYSICAL_ADDR`,由此我们获得了内核实际地址和被编译时地址的差值.之后,我们可以重定位内核,因为我们知道了实际地址和链接运行的地址.以及重定位表.

在内核重定位后 返回到解压函数[arch/x86/boot/compressed/head_64.S](https://github.com/torvalds/linux/blob/v4.16/arch/x86/boot/compressed/head_64.S).

内核的地址会被放在rax中,

```
jmp *%rax
```

然后,我们进入内核



## Links
- [address space layout randomization](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [initrd](https://en.wikipedia.org/wiki/Initrd)
- [long mode](https://en.wikipedia.org/wiki/Long_mode)
- [bzip2](http://www.bzip.org/)
- [RdRand instruction](https://en.wikipedia.org/wiki/RdRand)
- [Time Stamp Counter](https://en.wikipedia.org/wiki/Time_Stamp_Counter)
- [Programmable Interval Timers](https://en.wikipedia.org/wiki/Intel_8253)