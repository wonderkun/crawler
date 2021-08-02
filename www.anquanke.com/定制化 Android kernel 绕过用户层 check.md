> 原文链接: https://www.anquanke.com//post/id/248648 


# 定制化 Android kernel 绕过用户层 check


                                阅读量   
                                **23901**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01b8b2cf2cfacb5587.png)](https://p1.ssl.qhimg.com/t01b8b2cf2cfacb5587.png)



## 背景

Android 加固厂商针对运行环境进行诸多检测，常见的有设备Root，是否开启开发者模式或adb，更过(s)分(bi)可能会检测是否连接充电线。当检测未通过往往会终止进程，说到终止进程看似易实现，实则大有文章。因为从一个分析者的角度而言，可以忽略你的所有检测逻辑，只要保证程序正常运行即可，所以最容易想到的思路就是直接对程序检测后的处理逻辑进行插桩修改。与之对应的开发者也会对这一部分代码进行保护。常见的是利用系统 syscall 实现，这样可以避免对API插桩的方式进行绕过。当然利用 syscall 具体如何使得程序退出也有很多思路，常见的比如调用 kill。这次遇到的情况检测比较严格，对环境进行诸多修改仍未能阻止程序的闪退，日志如下：

[![](https://p5.ssl.qhimg.com/t012bd92f2602fd6df4.png)](https://p5.ssl.qhimg.com/t012bd92f2602fd6df4.png)

因为设备已解锁 bootloader，刷新内核比较方便，所以萌生了 patch kernel 去绕过的想法。



## Android kernel 下载与编译

该部分主要参考了[基于nexus6修改android内核](https://blog.csdn.net/u011649400/article/details/78705594)不过替换了它原文的代码源，更换为了清华源，链接如下<br>
git://mirrors.ustc.edu.cn/aosp/kernel/msm.git<br>
这样就不需要翻Q，而且速度也比较快。配置环境进行编译，主要指令如下：

```
msm# export ARCH=arm
msm# export CROSS_COMPILE=arm-eabi-
msm# export PATH=path/arm-eabi-4.8/bin/:$PATH
msm# make -j32
```

下图即表示编译成功

[![](https://p4.ssl.qhimg.com/t01dabbb8c89801de49.png)](https://p4.ssl.qhimg.com/t01dabbb8c89801de49.png)

### <a class="reference-link" name="Linux%20kernel%20%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90"></a>Linux kernel 源码分析

分析具体源码之前首先简单介绍一下 ARM 平台下的软中断到内核函数的调用。ARM CPU 有7种模式，分别是User、FIQ、IRQ、Supervisor(SVC)、Abort、Undef 和 System。具体处于何种模式在 CPSR 寄存器进行保存。ARM 平台 CPU 切换到内核是利用 SVC 指令（SVC 也是一条汇编指令），SVC 指令执行后 CPU 处理器会进入 Supervisor 模式，在此模式实现内核函数的执行。<br>
应用层实际要调用那个内核函数是由传入的系统调用号决定，ARM 平台系统调用号定义在 arch/arm/include/asm/unistd.h，与之相对应的在 kernel 中有一个 handler 来处理不同的系统调用号(system call handler)。要分析调用号与handler 的关系就需要从内核入口进行分析，内核入口代码由汇编实现，不同平台实现也不同（包括系统调用号）对于 ARM 定义在 arch/arm/kernel/entry-common.S，ARM64 定义在 arch/arm64/kernel/entry.S，此文主要以 ARM 平台为例，entry-common.S 主要汇编代码如下，关键部分都有注释：

```
/*=============================================================================
 * SWI handler
 *-----------------------------------------------------------------------------
 */

    .align    5
ENTRY(vector_swi)
    ...
    zero_fp

    /*
     * Get the system call number.
     */

#if defined(CONFIG_OABI_COMPAT)
    ...
#ifdef CONFIG_ARM_THUMB
    tst    r8, #PSR_T_BIT
    movne    r10, #0                @ no thumb OABI emulation
    ldreq    r10, [lr, #-4]            @ get SWI instruction
#else
    ldr    r10, [lr, #-4]            @ get SWI instruction
#endif
...

#elif defined(CONFIG_AEABI)

    /*
     * Pure EABI user space always put syscall number into scno (r7).
     */
#elif defined(CONFIG_ARM_THUMB)
    tst    r8, #PSR_T_BIT            @ this is SPSR from save_user_regs
    addne    scno, r7, #__NR_SYSCALL_BASE    @ put OS number in
    ldreq    scno, [lr, #-4]
#else
    /* Legacy ABI only. */
    ldr    scno, [lr, #-4]            @ get SWI instruction
#endif

#ifdef CONFIG_ALIGNMENT_TRAP
    ...
#endif
    ...
    adr    tbl, sys_call_table        @ load syscall table pointer

#if defined(CONFIG_OABI_COMPAT)
    bics    r10, r10, #0xff000000
    eorne    scno, r10, #__NR_OABI_SYSCALL_BASE
    ldrne    tbl, =sys_oabi_call_table
#elif !defined(CONFIG_AEABI)
    bic    scno, scno, #0xff000000        @ mask off SWI op-code
    eor    scno, scno, #__NR_SYSCALL_BASE    @ check OS number
#endif

local_restart:
    ...
    ldrcc    pc, [tbl, scno, lsl #2]        @ call sys_* routine
```

（ SWI 是 SVC 指令的前身）<br>
这部分代码逻辑不复杂，简单概括就是获取 R7 寄存器保存的syscall number，同时获取 syscall table 指针，做一些 check 后最终调用 syscall table 中的 sys*** 函数。Handler 的具体实现在 SYSCALL_DEFINE1/2/3/4/5/6(##name, …)函数中，如 kernel/sys.c 和/root/android-kernel/signal.c。SYSCALL_DEFINE 与 sys*** 的关系查看 include/linux/syscalls.h 中的宏定义即可明白，宏定义如下：

```
#define SYSCALL_DEFINE1(name, ...) SYSCALL_DEFINEx(1, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE2(name, ...) SYSCALL_DEFINEx(2, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE3(name, ...) SYSCALL_DEFINEx(3, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE4(name, ...) SYSCALL_DEFINEx(4, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE5(name, ...) SYSCALL_DEFINEx(5, _##name, __VA_ARGS__)
#define SYSCALL_DEFINE6(name, ...) SYSCALL_DEFINEx(6, _##name, __VA_ARGS__)

#define SYSCALL_DEFINEx(x, sname, ...)                \
    SYSCALL_METADATA(sname, x, __VA_ARGS__)            \
    __SYSCALL_DEFINEx(x, sname, __VA_ARGS__)

#define __SYSCALL_DEFINEx(x, name, ...)                    \
    asmlinkage long sys##name(__MAP(x,__SC_DECL,__VA_ARGS__));    \
    static inline long SYSC##name(__MAP(x,__SC_DECL,__VA_ARGS__));    \
    asmlinkage long SyS##name(__MAP(x,__SC_LONG,__VA_ARGS__))    \
    `{`                                \
        ...                        \
    `}`                                \
    SYSCALL_ALIAS(sys##name, SyS##name);                \
    static inline long SYSC##name(__MAP(x,__SC_DECL,__VA_ARGS__))
```



## kernel 代码修改

根据日志进程是接收到了一个 SIGSEGV 信号后退出了，而且是由于 PC 寄存器指向了错误的地址导致的。Kill syscall 也可以发送 SIGSEGV 信号，根据历史经验直接 Patch Linux #37 syscall。根据之前的 kernel 源码分析，可以迅速定位 kill 的 Handler

```
/**
 *  sys_kill - send a signal to a process
 *  @pid: the PID of the process
 *  @sig: signal to be sent
 */
SYSCALL_DEFINE2(kill, pid_t, pid, int, sig)
```

这里采用了比较暴力的做法，直接 return。

```
static int kill_something_info(int sig, struct siginfo *info, pid_t pid)
`{`
    // int ret;
    return 0;
```

同时因为 PC 寄存器指向错误地址为了程序不崩溃退出所以暴力的忽略 SIGSEGV 信号，这部分代码定义在arch/arm/kernel/signal.c，做了如下 patch

```
static void handle_signal(struct ksignal *ksig, struct pt_regs *regs)
`{`
    sigset_t *oldset = sigmask_to_save();
    int ret;
    if (ksig -&gt; sig == SIGSEGV)`{`
        return;
    `}`
```



## 刷入设备

将新 kernel 刷入设备也参考了[基于nexus6修改android内核](https://blog.csdn.net/u011649400/article/details/78705594)文章的方式，unmkbootimg -i boot.img 命令执行完会输出 rebuild boot image 的指令，如下：

```
To rebuild this boot image, you can use the command:
  mkbootimg --base 0 --pagesize 2048 --kernel_offset 0x00008000 --ramdisk_offset 0x02000000 --second_offset 0x00f00000 --tags_offset 0x01e00000 --cmdline 'console=ttyHSL0,115200,n8 androidboot.console=ttyHSL0 androidboot.hardware=shamu msm_rtb.filter=0x37 ehci-hcd.park=3 utags.blkdev=/dev/block/platform/msm_sdcc.1/by-name/utags utags.backup=/dev/block/platform/msm_sdcc.1/by-name/utagsBackup coherent_pool=8M' --kernel kernel --ramdisk ramdisk.cpio.gz -o boot.img
```

将 —kernel 的文件替换为编译出来的 zImage-dtb 即可得到定制化的 boot.img ,使用 fastboot flash 输入即可，参考文章很多不再赘述。



## 小结

·本文的重点只是介绍通过 patch kernel 实现应用层棘手情况处理的思路，以及 ARM 架构下 Linux syscall 部分源码分析。实际所改的代码比较暴力并未做准确的判断，适用性仅限于遇到的情形，并未考虑通用型。
