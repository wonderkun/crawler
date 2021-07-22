> 原文链接: https://www.anquanke.com//post/id/212616 


# Bypass Apple内核PPL


                                阅读量   
                                **135707**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者googleprojectzero，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2020/07/the-core-of-apple-is-ppl-breaking-xnu.html](https://googleprojectzero.blogspot.com/2020/07/the-core-of-apple-is-ppl-breaking-xnu.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01958d62724a3e544b.jpg)](https://p1.ssl.qhimg.com/t01958d62724a3e544b.jpg)



在研究单字节利用技术时，我认为有几种方法在获取内核读/写或攻破PAC之前仅使用一个物理地址映射原语就可能绕过Apple的PPL(Page Protection Layer),考虑到PPL比XNU内核的其他部分拥有更高的权限，在XNU“之前”泄露PPL的想法很有吸引力。但最后，我还是无法想出仅使用物理映射原语来突破PPL的方法。

PPL的目标是防止攻击者修改进程的可执行代码或页表，即使是在获取内核读/写/执行特权之后。它通过利用APRR创建保护页表的“kernel inside the kernel”来实现这一点。在正常的内核执行期间，页表和页表数据是只读的，修改页表的代码是不可执行的;内核修改页表的唯一方法是通过调用“PPL routine”进入PPL，这类似于从XNU到PPL的syscall。这样就限制了进入内核代码的入口点，这些入口点仅可以修改那些PPL routine的页表。

我考虑了几种使用单字节技术的物理映射原语来Bypass PPL的想法，包括直接映射页表、映射DART以允许从协处理器修改物理内存，不幸的是，这些想法都没有成功。

但是，这不是Project Zero的作风，所以，在我对设计缺陷进行了彻底的搜索之后，我又回到了内存破坏技术上。可以肯定的是，在IDA中反编译几个PPL函数就足以找到一些内存破坏。

[![](https://p1.ssl.qhimg.com/t01b19b397d80e86b3d.png)](https://p1.ssl.qhimg.com/t01b19b397d80e86b3d.png)

pmap_remove_options_internal()函数是一个PPL routine，是从XNU内核到拥有更高权限PPL的“PPL syscalls”之一。它是通过调用XNU中的pmap_remove_options()来调用的，然后在PPL中调用pmap_remove_options_internal()。它的目的是从进程的物理内存映射(pmap)中unmap所提供的虚拟地址范围。

```
MARK_AS_PMAP_TEXT static int
pmap_remove_options_internal(
        pmap_t pmap,
        vm_map_address_t start,
        vm_map_address_t end,
        int options)

```

删除映射提供虚拟地址范围的转换表条目（TTEs）的实际工作是通过调用pmap_remove_range_options（）来完成的，该方法获取指向TTE起始和结束范围的指针，以便从L3转换表中删除。

```
static int
pmap_remove_range_options(
        pmap_t pmap,
        pt_entry_t *bpte,   // The first L3 TTE to remove
        pt_entry_t *epte,   // The end of the TTEs
        uint32_t *rmv_cnt,
        int options)

```

不幸的是，当pmap_remove_options_internal()调用pmap_remove_range_options()时，似乎所提供的虚拟地址范围不会超过L3转换表边界，因为如果超过了边界，那么计算出来的TTE范围将内存越界:

```
remove_count = pmap_remove_range_options(
                   pmap,
                   &amp;l3_table[(va_start &gt;&gt; 14) &amp; 0x7FF],
                   (u64 *)((char *)&amp;l3_table[(va_start &gt;&gt; 14) &amp; 0x7FF]
                         + ((size &gt;&gt; 11) &amp; 0x1FFFFFFFFFFFF8LL)),
                   &amp;rmv_spte,
                   options);
```

也就是说如果我们有一个任意的核函数调用原语,我们就可以直接调用PPL-entering封装函数,并使用不正确的虚拟地址范围调用pmap_remove_options_internal（），这使得pmap_remove_range_options（）在PPL模式下尝试删除从越界内存读取的“TTE”。由于删除的TTE被置零，也就是说我们可以破坏PPL保护的内存。

[![](https://p4.ssl.qhimg.com/t01a2ad2d11cd481073.png)](https://p4.ssl.qhimg.com/t01a2ad2d11cd481073.png)

将越界的TTE归零将是绕过PPL的一个非常复杂的原语。很多我们想要破坏的数据可能已经被分配到远离页表的地方了，而且PPL的代码基址不够大，我们无法保证可以通过清空内存来完成一些事情，也就是说，PPL可能会检测到试图unmap不存在的TTEs！

因此，我选择关注这种越界处理的一个副作用：TLB不正确无效。

稍后在pmap_remove_options_internal()中，在删除了TTEs之后，需要使TLB（translation lookaside buffer）失效，以确保进程无法继续通过失效的TLB条目访问未映射的页面。

```
flush_mmu_tlb_region_asid_async(va_start, size, pmap);
```

这个TLB刷新发生在提供的虚拟地址范围，而不是删除的TTEs。因此，如果超出边界的区域来自进程地址空间的一个单独区域，则无效的TLB条目和删除的L3节点之间可能存在不一致，从而将失效的TLB条目留给那些超出边界的TTE。

[![](https://p0.ssl.qhimg.com/t0184f18eff3c553f5a.png)](https://p0.ssl.qhimg.com/t0184f18eff3c553f5a.png)

失效的TLB条目将允许进程在该页被取消映射并可能被重新用于页表之后继续访问该物理页。因此，如果一个L3转换表有一个失效的TLB条目，那么我们可以插入L3 TTEs来将任意受ppl保护的页面映射为可写的。

以下是PPL Pypass的原理:
- 1.调用内核函数cpm_allocate（）分配2页连续的物理内存，分别称为A和B。
- 2.调用pmap_mark_page_as_ppl_page()在ppl_page_list的头部插入A和B，这样它们就可以在页表中重用。
- 3.虚拟地址P和Q的page出现了问题，因此A和B被分配为L3 TTs，分别用于映射P和Q。P和Q是不连续的，但有连续的TTEs。
- 4.启动一个单核CPU的spinner线程，该线程从第Q页循环读取数据，以保持TLB条目有效。
- 5.调用pmap_remove_options()删除从虚拟地址P(不包括Q)开始的2个page，也就是说该漏洞删除了P和Q的TTEs，但只有P的TLB条目无效。
- 6.调用pmap_mark_page_as_ppl_page()将page Q插入到ppl_page_list的头部，以便页表可以重用它。
- 7.虚拟地址page R中出现错误，因此即使我们继续为Q提供失效的TLB条目，也将page Q分配为R 的 L3 TT。
- 8.使用失效的TLB条目，写入page Q以插入一个L3 TTE，它将Q本身映射为可写的。
[![](https://p4.ssl.qhimg.com/t016ff72c629ff7d387.gif)](https://p4.ssl.qhimg.com/t016ff72c629ff7d387.gif)

此Bypass报告为[Project Zero issue 2035](https://bugs.chromium.org/p/project-zero/issues/detail?id=2035)，并在iOS 13.6中修复;您可以找到一个POC，它演示了如何将任意物理地址映射到EL0中。关于如何利用TLB更详细的内容，请参考Jann Horn关于这个主题的[文章](https://googleprojectzero.blogspot.com/2019/01/taking-page-from-kernels-book-tlb-issue.html)。

这个bug演示了在以前不存在安全边界的情况下创建安全边界时的一个常见问题。代码很容易对安全模型做一些微妙的假设（比如在哪里进行参数验证，或者什么功能是公开的还是私有的），而这些假设在新模型下不再成立。如果在PPL中看到更多这样的bug，我不会感到惊讶。

总的来说，这次我对PPL的设计更加熟悉，我认为这是一个很好的缓解机制，有明确的安全边界，不会引发更多的攻击面。对我而言，PPL的实际价值尚不明确:PPL可以缓解哪些实际攻击？它是否只是为了进一步完善缓解机制打下的基础？无论答案是什么，我都期待它，感谢Apple提出了一个值得深入研究的缓解机制。
