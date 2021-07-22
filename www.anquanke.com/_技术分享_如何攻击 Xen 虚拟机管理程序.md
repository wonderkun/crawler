> 原文链接: https://www.anquanke.com//post/id/86051 


# 【技术分享】如何攻击 Xen 虚拟机管理程序


                                阅读量   
                                **94812**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：googleprojectzero.blogspot.tw
                                <br>原文地址：[https://googleprojectzero.blogspot.tw/2017/04/pandavirtualization-exploiting-xen.html](https://googleprojectzero.blogspot.tw/2017/04/pandavirtualization-exploiting-xen.html)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p5.ssl.qhimg.com/t01551539b06892630c.png)](https://p5.ssl.qhimg.com/t01551539b06892630c.png)

翻译：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**预估稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、概述**

2017年3月14日，我向Xen安全团队报告了一个[漏洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=1184)，该漏洞允许攻击者在控制半虚拟化（paravirtualized，PV）x86-64架构的Xen客户机（guest）内核的条件下，能够突破Xen的虚拟机管理程序（hypervisor），获取宿主机物理内存的完全控制权限。Xen项目组于2017年4月4日公布了一份[安全公告](https://xenbits.xen.org/xsa/advisory-212.html)以及一个[补丁](https://xenbits.xen.org/xsa/xsa212.patch)，解决了这个问题。

为了演示这个问题所造成的影响，我写了一个漏洞利用工具，当工具以root权限运行在一个64位PV客户机上时，可以获取同一宿主机上其他所有64位PV客户机（包括dom0）的root权限的shell。

<br>

**二、背景**

**（一）access_ok()**

在x86-64架构上，Xen PV客户机与hypervisor共享虚拟地址空间。大致的内存布局如下图所示:

[![](https://p3.ssl.qhimg.com/t01216c2633828467d0.png)](https://p3.ssl.qhimg.com/t01216c2633828467d0.png)

Xen允许客户机内核执行超级调用	（hypercall），hypercall本质上就是普通的系统调用，使用了System V AMD64 ABI实现从客户机内核到hypervisor的过渡。hypercall使用指令执行，寄存器中传递的参数最多不超过6个。与普通的syscall类似，Xen的hypercall经常将客户机指针作为参数使用。由于与hypervisor共享地址空间，客户机只需要简单传入其虚拟指针（guest-virtual pointer）即可。

与其他内核一样，Xen必须确保客户机的虚拟指针在解除引用前不能指向hypervisor所拥有的内存。Xen通过使用类似于Linux内核的用户空间访问器（userspace accessor）来实现这一点，例如：

1、使用access_ok(addr, size)，检查是否能够安全访问客户机所提供的虚拟内存区域，换句话说，它会检查访问这片内存是否导致hypervisor内存被修改。

2、使用__copy_to_guest(hnd, ptr, nr)，从hypervisor的ptr地址拷贝nr字节数据到客户机的hnd地址，但并不检查hnd是否是安全的。

3、使用copy_to_guest(hnd, ptr, nr)，如果hnd是安全的，则从hypervisor的ptr地址拷贝nr字节数据到客户机的hnd地址。

在Linux内核中，access_ok()宏会使用任意内存访问模式，检查是否可以安全访问从addr到addr+size-1的内存区域。然而，Xen的access_ok()宏并不能保证这一点：



```
/*
 * Valid if in +ve half of 48-bit address space, or above Xen-reserved area.
 * This is also valid for range checks (addr, addr+size). As long as the
 * start address is outside the Xen-reserved area then we will access a
 * non-canonical address (and thus fault) before ever reaching VIRT_START.
 */
#define __addr_ok(addr) 
    (((unsigned long)(addr) &lt; (1UL&lt;&lt;47)) || 
     ((unsigned long)(addr) &gt;= HYPERVISOR_VIRT_END))
#define access_ok(addr, size) 
    (__addr_ok(addr) || is_compat_arg_xlat_range(addr, size))
```

Xen通常只会检查addr指针指向的是用户区域或者内核区域，而不检查size值。如果实际访问的客户机内存起始于addr地址附近，在不跳过大量内存空间的前提下，Xen对内存地址进行线性检查，一旦客户机内存访问失败则退出检查过程，此时由于大量非标准（non-canonical）地址的存在（这些地址可以当作守护区域），只检查addr值的确已经足够。然而，如果某个hypercall希望访问客户机中以64位偏移量开始的缓冲区，它需要确保access_ok()的检查过程中使用的是正确的偏移量，此时只检查整个用户空间的缓冲区并不安全！

Xen提供了access_ok()的封装函数，用来访问客户机内存中的数组。如果要确认访问某个从0开始的数组是否安全，你可以使用guest_handle_okay(hnd, nr)。然而，如果要确认访问某个从其他元素开始的数组是否安全，你需要使用guest_handle_subrange_okay(hnd, first, last)。

当我看到access_ok()的定义时，我并不能直观地看出这种不安全性会带来什么影响，因此我开始搜索它的调用函数，查看是否存在对access_ok()的不安全调用。

**（二）Hypercall抢占**

当某个任务调度时钟触发时，Xen需要具备从当前执行的vCPU快速切换到另一个虚拟机（VM）vCPU的能力。然而，简单中断某个hypercall的执行并不能做到这一点（比如hypercall可能正处于自旋锁（spinlock）状态），因此，与其他操作系统类似，Xen需要使用某种机制，延迟vCPU的切换，直到可以安全进行状态切换。

在Xen中，hypercall的抢占通过自愿抢占（voluntary preemption）机制实现，即：任何长时间运行的hypercall代码都应该定期调用hypercall_preempt_check()来检查调度器是否愿意切换到另一个vCPU。如果这种情况发生，那么hypercall代码会退出，退回到客户机，并向调度器发送信号，表明此时可以安全抢占当前任务的资源。当之前的vCPU重新被调度时，调度器会调整客户机寄存器或客户机内存中的hypercall参数，重新进入hypercall中，执行剩余的任务。Hypercall不会去区分是被正常调用还是在抢占恢复后被重新调用。

Xen之所以使用这种hypercall恢复机制，原因在于Xen并没有为每个vCPU维护一个hypervisor栈，而仅仅为每个物理核心维护一个hypervisor栈。这意味着，虽然其他操作系统（比如Linux）可以在内核栈中存储被中断的syscall状态，但对Xen而言这个任务并不简单。

这种设计意味着对某些hypercall而言，为了能够正常恢复任务状态，客户机内存中需要存储额外的数据，而这种数据可能会被客户机篡改，从而实现对hypervisor的攻击。

**（三）memory_exchange()**

HYPERVISOR_memory_op(XENMEM_exchange, arg)这个hypercall使用了“xen/common/memory.c”文件中的memory_exchange(arg)函数。该函数允许客户机使用当前分配给客户机的物理页面列表进行“交易”，以换取另一个新的连续物理页面。这对希望执行DMA的客户机是非常有用的，因为DMA要求具备物理上连续的缓冲区。

HYPERVISOR_memory_op以xen_memory_exchange这个结构体对象作为参数，结构体的定义如下：



```
struct xen_memory_reservation `{`
    /* [...] */
    XEN_GUEST_HANDLE(xen_pfn_t) extent_start; /* in: physical page list */
    /* Number of extents, and size/alignment of each (2^extent_order pages). */
    xen_ulong_t    nr_extents;
    unsigned int   extent_order;
    /* XENMEMF flags. */
    unsigned int   mem_flags;
    /*
     * Domain whose reservation is being changed.
     * Unprivileged domains can specify only DOMID_SELF.
     */
    domid_t        domid;
`}`;
struct xen_memory_exchange `{`
    /*
     * [IN] Details of memory extents to be exchanged (GMFN bases).
     * Note that @in.address_bits is ignored and unused.
     */
    struct xen_memory_reservation in;
    /*
     * [IN/OUT] Details of new memory extents.
     * We require that:
     *  1. @in.domid == @out.domid
     *  2. @in.nr_extents  &lt;&lt; @in.extent_order == 
     *     @out.nr_extents &lt;&lt; @out.extent_order
     *  3. @in.extent_start and @out.extent_start lists must not overlap
     *  4. @out.extent_start lists GPFN bases to be populated
     *  5. @out.extent_start is overwritten with allocated GMFN bases
     */
    struct xen_memory_reservation out;
    /*
     * [OUT] Number of input extents that were successfully exchanged:
     *  1. The first @nr_exchanged input extents were successfully
     *     deallocated.
     *  2. The corresponding first entries in the output extent list correctly
     *     indicate the GMFNs that were successfully exchanged.
     *  3. All other input and output extents are untouched.
     *  4. If not all input exents are exchanged then the return code of this
     *     command will be non-zero.
     *  5. THIS FIELD MUST BE INITIALISED TO ZERO BY THE CALLER!
     */
    xen_ulong_t nr_exchanged;
`}`;
```

与bug有关的字段是in.extent_start、in.nr_extents、out.extent_start、out.nr_extents以及nr_exchanged。

官方文档表明客户机始终将nr_exchanged的值初始化为0，这是因为这个变量不仅作为返回值使用，同时也被用于hypercall抢占中。当memory_exchange()被抢占时，它将自身进度存储于nr_exchanged中，在恢复工作时，memory_exchange()使用nr_exchanged的值来决定in.extent_start和out.extent_start这两个输入数组应该恢复到哪个位置。

最开始时，memory_exchange()在使用__copy_from_guest_offset()和__copy_to_guest_offset()访问用户空间前，根本就没有检查用户空间数组指针，同时这两个函数内部也没有做任何检查，这样有可能会导致Xen读取和写入位于hypervisor内存范围内的数据，这是个非常严重的bug。这个漏洞在2012年被发现（[XSA-29](https://xenbits.xen.org/xsa/advisory-29.html), CVE-2012-5513），补丁代码如下（[https://xenbits.xen.org/xsa/xsa29-4.1.patch](https://xenbits.xen.org/xsa/xsa29-4.1.patch) ）：



```
diff --git a/xen/common/memory.c b/xen/common/memory.c
index 4e7c234..59379d3 100644
--- a/xen/common/memory.c
+++ b/xen/common/memory.c
@@ -289,6 +289,13 @@ static long memory_exchange(XEN_GUEST_HANDLE(xen_memory_exchange_t) arg)
        goto fail_early;
    `}`
+    if ( !guest_handle_okay(exch.in.extent_start, exch.in.nr_extents) ||
+         !guest_handle_okay(exch.out.extent_start, exch.out.nr_extents) )
+    `{`
+        rc = -EFAULT;
+        goto fail_early;
+    `}`
+
    /* Only privileged guests can allocate multi-page contiguous extents. */
    if ( !multipage_allocation_permitted(current-&gt;domain,
                                         exch.in.extent_order) ||
```



**三、漏洞说明**

从以下代码片段中可以看出，由于Xen hypercall的抢占恢复机制存在缺陷，客户机可以控制nr_exchanged这个64位偏移量，通过该变量从out.extent_start数组中选择一个偏移值，这个偏移值可以是hypervisor写入的值。



```
static long memory_exchange(XEN_GUEST_HANDLE_PARAM(xen_memory_exchange_t) arg)
`{`
    [...]
    /* Various sanity checks. */
    [...]
    if ( !guest_handle_okay(exch.in.extent_start, exch.in.nr_extents) ||
         !guest_handle_okay(exch.out.extent_start, exch.out.nr_extents) )
    `{`
        rc = -EFAULT;
        goto fail_early;
    `}`
    [...]
    for ( i = (exch.nr_exchanged &gt;&gt; in_chunk_order);
          i &lt; (exch.in.nr_extents &gt;&gt; in_chunk_order);
          i++ )
    `{`
        [...]
        /* Assign each output page to the domain. */
        for ( j = 0; (page = page_list_remove_head(&amp;out_chunk_list)); ++j )
        `{`
            [...]
            if ( !paging_mode_translate(d) )
            `{`
                [...]
                if ( __copy_to_guest_offset(exch.out.extent_start, (i &lt;&lt; out_chunk_order) + j, &amp;mfn, 1) )
                    rc = -EFAULT;
            `}`
        `}`
        [...]
    `}`
    [...]
`}`
```

然而，guest_handle_okay()只是检查能否安全访问客户机中从第0个元素开始的exch.out.extent_start数组，这里本应该使用的是guest_handle_subrange_okay()来进行检查。这意味着攻击者可以通过以下方式，将一个8字节数值写入hypervisor内存中的任意地址：

1、将exch.in.extent_order和exch.out.extent_order设为0（将物理内存块更换为新的页面大小的内存块）。

2、修改exch.out.extent_start以及exch.nr_exchanged的值，使exch.out.extent_start指向用户空间内存，而exch.out.extent_start+8*exch.nr_exchanged指向hypervisor内存中的目标地址（target_addr），此时exch.out.extent_start的值接近于NULL。这两个值可以通过公式计算出来，exch.out.extent_start=target_addr%8，exch.nr_exchanged=target_addr/8。

3、修改exch.in.nr_extents，同时将exch.out.nr_extents的值修改为exch.nr_exchanged+1。

4、将exch.in.extent_start值修改为input_buffer-8*exch.nr_exchanged（这里input_buffer是一个合法的客户机内核指针，指向当前客户机拥有的物理页号）。Xen认为exch.in.extent_start始终指向客户机的用户空间（因而能够通过access_ok()的检查），因为exch.out.extent_start大致指向了用户空间的起始地址，且hypervisor和客户机内核的地址空间的大小加起来才与用户空间大小相近。

攻击者最终写入的数据是一个物理页号（即物理地址除以页面大小的结果）：

<br>

**四、漏洞利用：获得页表（pagetable）控制权**

****

对于事务繁忙的操作系统来说，控制由内核写入的页号可能比较困难。因此，为了能够稳定利用该漏洞，我们可以将8字节数据重复写入被控内存地址，其中那些最为关键的比特为0（这是因为我们受限于物理内存的大小），其他比特可以稍微随机一些。我决定在8字节的第1个字节写入可控值，剩下的7个字节用垃圾数据填充。

事实证明，对x86-64架构的PV型客户机来说，这种简单的利用方式足以稳定攻击hypervisor，原因如下：

1、x86-64 PV客户机掌握它们能够访问的所有页面的实际物理页号。

2、x86-64 PV客户机可以将所属域的活动页表映射为只读页表，而Xen只能防止它们被映射为可写页表。

3、Xen将所有物理内存在0xffff830000000000处映射为可写内存（换句话说，hypervisor可以无视物理页面的保护机制，将数据写入到physical_address+0xffff830000000000地址处，从而实现将数据写入任意物理页面）。

攻击的目标是将一个活动的3级页表(我称之为”受害者页表”)中的某个条目指向客户机具备写访问权限的页面（我称之为“虚假页表”）。这意味着攻击者必须将一个包含虚假页表的物理页号和其他标志的8字节值写入到受害者页表中的一个条目中，并且确保8字节之后的页表条目处于禁用状态（例如，攻击者可以将紧随其后的页表条目的首字节设为0）。本质上来说，攻击者需要写入可控的9个字节，加上7个无关紧要的字节。

因为所有相关页面的物理页号以及所有映射为可写内存的物理内存对于客户机来说都是已知的，因此确定写入的位置和写入的值不是件难事，那么唯一剩下的问题就是如何利用我们前面分析的原理实际写入数据。

攻击者希望将一个8字节数值写入内存，其中第1个字节为有效数据，剩下7个字节为垃圾数据，攻击者可以往内存中重复写入一个随机字节并读取该值，直到该值正确。通过这种方式将字节写入连续的内存地址，完成数据写入任务。

任务完成后，攻击者可以控制活动的页表，因此攻击者可以将任意物理内存映射为客户机的虚拟地址空间。这意味着攻击者可以稳定读取并写入hypervisor和其他所有虚拟机的内存中的代码和数据。

<br>

**五、在其他虚拟机上运行shell命令**

此时，攻击者已经完全控制了主机，权限与hypervisor权限一致，攻击者可以通过搜索物理内存轻松窃取秘密信息，此外，现实点的黑客应该不满足于仅仅将代码注入到虚拟机中，而更在意如何开展更多攻击。

对我来说，在其他虚拟机中运行任意shell命令会让该漏洞的直观感受更为明显，因此我决定修改利用工具，使其可以将shell命令注入到其他64位PV域中。

首先，我需要具备在hypervisor上下文中稳定执行代码的能力。考虑到我们现在可以读取和写入物理内存，我们可以使用一种独立于操作系统（或hypervisor）、使用内核或hypervisor权限调用任意地址的方法，具体来说就是使用非特权SIDT指令定位中断描述符表（Interrupt Descriptor Table, IDT），DPL设置为3（DPL即Descriptor Privilege Level，3级代表特权模式），往IDT中写入一个条目并触发中断。Xen支持SMEP以及SMAP，因此我们不能直接将IDT条目指向客户机内存，但我们可以通过写入页表表项，将带有hypervisor上下文shellcode的客户机页面映射为non-user-accessilbe页面，这样我们就可以绕过SMEP执行shellcode。

之后，在hypervisor上下文中，我们可以通过读取和写入IA32_LSATAR MSR来hook syscall调用的入口点。在客户机的用户空间以及客户机内核中的hypercall都利用到了syscall入口点。攻击者可以将已控制的页面映射为guest-user-accessible内存，修改寄存器状态，调用sysret，这样就可以将执行客户机用户空间的代码转换为执行任意客户机用户的shellcode，并且独立于hypervisor或者客户机操作系统。

我的漏洞利用工具可以将shellcode注入到所有使用write()系统调用的客户机用户空间进程中。每当shellcode执行时，它会检查自身是否以root权限运行，检查客户机文件系统中是否不存在某个锁定文件（lockfile），如果这些条件全部满足，它会使用clone()系统调用创建子进程，运行任意shell命令。

这里需要注意的是，我的漏洞利用工具并没有实现清理功能，因此当攻击结束后，被hook的入口点会迅速导致hypervisor崩溃。

下图是成功攻击Qubes OS 3.2的屏幕截图，这里的Qubes OS使用了Xen作为其虚拟机管理程序。漏洞利用程序运行于“test124”非特权域中，从下图可知，我们可以将代码注入到dom0以及firewallvm中。

[![](https://p5.ssl.qhimg.com/t01ee485d091f305374.png)](https://p5.ssl.qhimg.com/t01ee485d091f305374.png)

<br>

**六、结论**

我认为这个问题的根本原因在于access_ok()函数中存在的安全隐患。当前版本的access_ok()于2005年编写完成，刚好是第一版Xen发布的两年后，也远远早于第一版XSA的发布时间。看起来似乎老代码往往比新代码包含更多脆弱点，因为程序人员疏于对老代码做安全评估，通常会把它们遗忘在历史角落中。

在优化与安全有关的代码时，我们必须注意避免原来的安全设计理念因为优化工作而失效。使用access_ok()函数的目的是检查整个hypervisor内存，避免内存错误，然而，在2005年，程序人员提交了一次[代码改动](https://xenbits.xen.org/gitweb/?p=xen.git;a=blobdiff;f=xen/include/asm-x86/x86_64/uaccess.h;h=bb23ae81a4456cc5f76ee741b71f944485c7300f;hp=da3d8f5c1f848004d97ddf16f4fce910b88b5e26;hb=f87f8a7110e5dd57091b8484685953414693e2a3;hpb=196c87d1574c5ce7dca4ff78990e3168a4dcad27;ds=sidebyside)，将x86_64架构上的access_ok()代码修改为当前版本。当时这个改动没有立刻引发MEMOP_increase_reservation以及MEMOP_decrease_reservation这两个hypercall中存在的漏洞，唯一的原因在于do_dom_mem_op()的nr_extents参数只有32比特大小，这种防御机制真的非常脆弱。

虽然人们已经发现了Xen的几个漏洞，但这些漏洞仅影响PV客户机，因为HVM客户机不会涉及到存在问题的代码，我坚信本文分析的这个漏洞不属于这些漏洞中的任何一个。对PV客户机来说，访问客户机虚拟内存远远比访问HVM客户机虚拟内存简单得多。对PV客户机来说，raw_copy_from_guest()调用了copy_from_user()，后者只是执行了边界检查，随后使用经过缺页异常修正（pagefault fixup）处理后的memcpy函数，这也是普通操作系统内核在访问用户空间内存时的处理流程。对于HVM客户机来说，raw_copy_from_guest()调用了copy_from_user_hvm()，后者必须执行逐页复制操作（因为内存区域在物理上可能是不连续的，也没有映射为hypervisor中连续的虚拟内存）、遍历客户机页表、查找每个页面中的客户机页帧（frame）和引用计数、将客户机页面映射为hypervisor内存以及进行各项检查工作（比如防止HVM客户机写入只读授权映射内存）。因此对于HVM客户机来说，处理客户机内存访问的复杂性远远高于PV客户机。

对于安全研究人员而言，半虚拟化分析工作并没有比普通内核分析工作难度大，从本文对该漏洞的分析过程就可以看出这一点。如果你之前已经做过内核代码审计工作，你会发现hypercall的调用路径（位于“xen/arch/x86/x86_64/entry.S”中的lstar_enter和int80_direct_trap）以及hypercall的基本设计（对于x86架构的PV客户机，可以在“xen/arch/x86/pv/hypercall.c”文件中的pv_hypercall_table找到相关内容）看起来与普通的syscall差不多。
