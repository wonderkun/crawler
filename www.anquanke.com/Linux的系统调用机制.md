> 原文链接: https://www.anquanke.com//post/id/252373 


# Linux的系统调用机制


                                阅读量   
                                **18688**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0126b2d1c1ca565d8a.jpg)](https://p0.ssl.qhimg.com/t0126b2d1c1ca565d8a.jpg)



## 概述

处于用户态的程序只能执行非特权指令, 如果需要使用某些特权指令, 比如: 通过io指令与硬盘交互来读取文件, 则必须通过系统调用向内核发起请求, 内核会检查请求是否安全, 从而保证用户态进程不会威胁整个系统

write(1, ptr, 0x10)系统调用为例子, 汇编可以写为如下, 内核收到请求后会向显存中写入数据, 从而在显示器上显示出来

```
mov rax, 1
mov rdi, 1
mov rsi, ptr
mov rdx, 0x10
syscall
```

C库会首先实现一个write的包裹函数, 为这个系统调用进行一些简单的参数检查和错误处理

由于write的功能十分简单, 不方面使用因此还会根据write衍生出更高级的函数printf()供用户使用

整体结构如下:

[![](https://p2.ssl.qhimg.com/t0199f5b1ae7be6c698.png)](https://p2.ssl.qhimg.com/t0199f5b1ae7be6c698.png)

接下来我们主要研究系统调用是怎么进入和退出的, 并不研究具体处理函数的实现



## i386下处理系统调用

i386的系统调用是通过中断实现的, 因此放在了arch/i386/traps.c里面, 通过system_call()处理int 0x80的中断

[![](https://p0.ssl.qhimg.com/t0157ff32ced78fc021.png)](https://p0.ssl.qhimg.com/t0157ff32ced78fc021.png)

system_call()声明

[![](https://p1.ssl.qhimg.com/t0144fd5d00b0318cc0.png)](https://p1.ssl.qhimg.com/t0144fd5d00b0318cc0.png)

system_call()定义

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f539725ff1b66942.png)

sys_call_table就是一个函数指针数组, 定义在arch/i386/syscall.c中, 通过包含文件完成数组的初始化

[![](https://p5.ssl.qhimg.com/t011c57578f518094a6.png)](https://p5.ssl.qhimg.com/t011c57578f518094a6.png)

unistd.h中定义了系统调用号与处理函数的句柄, 这个文件位于源码顶层, 是所有架构都必须满足的, 处理函数的举报由各个架构自己实现

[![](https://p2.ssl.qhimg.com/t01cdb5cd72cd6215fd.png)](https://p2.ssl.qhimg.com/t01cdb5cd72cd6215fd.png)

总结

[![](https://p1.ssl.qhimg.com/t01c0bf9d944f375a53.png)](https://p1.ssl.qhimg.com/t01c0bf9d944f375a53.png)



## 预备知识

### <a class="reference-link" name="%E6%AE%B5%E9%80%89%E6%8B%A9%E5%AD%90"></a>段选择子

[![](https://p5.ssl.qhimg.com/t0113f9c00c96d39510.png)](https://p5.ssl.qhimg.com/t0113f9c00c96d39510.png)

实模式下下: 实际物理地址 = (段地址&lt;&lt;4) + 偏移地址

保护模式下: 逻辑地址由两部分组成
- 段标识符: 16位字段, 放在段寄存器中, 为全局段表的索引
- 段内偏移: 32位
保护模式下寻址过程
- 先根据段寄存器找到段选择子(16bit)
- 再根据GDT找到段表, 用选择子作为索引, 从而找到段描述符(64bit)
- 根据段描述符找到段基址
- 段基址+ 偏移地址 得到线性地址
<li>线性地址到物理地址:
<ul>
- 如果没有分页那么线性地址就是物理地址,
- 如果启用了分页, 那么还要通过页表得到物理地址
[![](https://p1.ssl.qhimg.com/t01bd99ced0dfb9bab8.png)](https://p1.ssl.qhimg.com/t01bd99ced0dfb9bab8.png)

段选择子/段描述符索引
- 为 段描述表 中 段描述符 的 序号
- 由于一共13bit可用, 因此可以区分8192个段
<li>TI: Table Indicator, 引用描述表的指示位
<ul>
- T1 = 0表示从全局段表GDT中读取
- TI = 1 表示从局部段表LDT中读取
由于分页机制比分段机制更加灵活, 因此现在的操作系统并不开启分段, 但是处于兼容性的考虑, 段寄存器还是被保留了下来

对于分段linux采用平坦模式, 也就是说所有的段的基址都是0, 地址空间相同, 分段只用于鉴权: 每当执行某些特权指令时CPU就会自动检查CS寄存器的RPL
- 如果为0则说明当前是内核态, 允许执行
- 如果不为0则说明是用户态, CPU会抛出一个异常, 交由内核的异常处理程序处理, 通常会向此用户进程发送SIGSEV信号
因此狭义上来说陷入内核态就是CPU令CS的RPL为0, 从而可以执行特权指令. 切换到内核态的执行环境则就是后话了

### <a class="reference-link" name="syscall%E6%8C%87%E4%BB%A4"></a>syscall指令

64位下的系统调用就和中断没关系了, 主要依赖于syscall指令的支持, syscall指令依靠MSR寄存器找到处理系统的入口点

MSR寄存器用来对CPU进行设置, 通过WRMSR和RDMSR指令读写

[![](https://p4.ssl.qhimg.com/t012558e0d2dabde002.png)](https://p4.ssl.qhimg.com/t012558e0d2dabde002.png)

x86_64寄存器架构

[![](https://p3.ssl.qhimg.com/t0179c794f2732cd0c9.png)](https://p3.ssl.qhimg.com/t0179c794f2732cd0c9.png)

当syscall指令执行时, 有如下操作
- RCX保存用户态的RIP
- 从MSR寄存器中的IA32_LASAR获取RIP
- R11保存标志寄存器
- 用IA32_STAR[47:32]设置CS的选择子, 同时把RPL设置为0, 表示现在开始执行内核态代码, 这是进入内核态的第一步, 由CPU完成
- 用IA32_STAR[47:32]+8设置SS的选择子, 这也就要求GDT中栈段描述符就在代码段描述符上面
[![](https://p1.ssl.qhimg.com/t0149995eff6ad6f1be.png)](https://p1.ssl.qhimg.com/t0149995eff6ad6f1be.png)

指令操作

[![](https://p3.ssl.qhimg.com/t01e1fb351bf197cf56.png)](https://p3.ssl.qhimg.com/t01e1fb351bf197cf56.png)

[https://www.felixcloutier.com/x86/syscall.html](https://www.felixcloutier.com/x86/syscall.html)

### <a class="reference-link" name="swapgs%E6%8C%87%E4%BB%A4"></a>swapgs指令

swapgs指令: 把gs的值与IA32_KERNEL_GS_BASE MSR进行交换

[![](https://p5.ssl.qhimg.com/t01d25bd950c1628068.png)](https://p5.ssl.qhimg.com/t01d25bd950c1628068.png)

[https://www.felixcloutier.com/x86/swapgs](https://www.felixcloutier.com/x86/swapgs)

刚刚切换到内核态时, 所有的通用寄存器与段寄存器都被用户使用, 内核需要想办法找到内核相关信息, 解决方法为:
- 令gs指向描述每个cpu相关的数据结构
- 当要切换到用户态时就调用swapgs把值保存在MSR寄存器中. 由于操作MSR的指令为特权指令, 因此用户态下是无法修改的MSR


## x86_64下处理系统调用

kernel初始化时, 调用arch/x86/kernel/s.c:syscall_init()对MSR进行初始化, 设置entry_SYSCALL_64为处理系统调用的入口点

[![](https://p0.ssl.qhimg.com/t010a46866637757995.png)](https://p0.ssl.qhimg.com/t010a46866637757995.png)

由于有些指令entry_SYSCALL_64的任务可以分为三部分
- 进入路径: 汇编实现, 目的是保存syscall的现场, 切换到内核态的执行环境, 创建一个适当的环境, 然后调用处理程序
- 处理程序: C实现, 负责具体的处理工作
- 退出路径: 汇编实现, 目的是从中断环境中退出, 切换到用户态, 恢复用户态的程序执行
进入路径部分:
<li>先通过swapgs指令切换到内核态的gs, 并保存用户态的gs
<ul>
- 这是一个特权指令, 但是CPU处理system指令时已经把CS的RPL设为00, 因此现在运行在内核态, 可以执行特权指令
[![](https://p3.ssl.qhimg.com/t01714d2d2c3aac5a37.png)](https://p3.ssl.qhimg.com/t01714d2d2c3aac5a37.png)

接下来涉及到slow_path和fast_path相关, 这只是一个优化, 其本质工作就是下面这条指令

[![](https://p2.ssl.qhimg.com/t010c1bc1cc3e59dd87.png)](https://p2.ssl.qhimg.com/t010c1bc1cc3e59dd87.png)

sys_call_table是一个函数指针数组, 指向各个系统调用的处理函数

[![](https://p3.ssl.qhimg.com/t018dbc1e770bb6a506.png)](https://p3.ssl.qhimg.com/t018dbc1e770bb6a506.png)

[![](https://p2.ssl.qhimg.com/t017569f141220d5ff2.png)](https://p2.ssl.qhimg.com/t017569f141220d5ff2.png)

处理函数结束后会ret到entry_SYSCALL_64中, 进入退出路径部分, 这部分进行的工作为
- 把处理函数的返回值写入到内核栈上的pt_regs中
- 利用pt_regs结构恢复用户态的执行环境
- 交换gs, 切回用户态的gs, 并把内核态的gs保存在MSR中
- sysretq, 从syscall中退出
[![](https://p5.ssl.qhimg.com/t01ed0180a9396cd06a.png)](https://p5.ssl.qhimg.com/t01ed0180a9396cd06a.png)

[![](https://p0.ssl.qhimg.com/t01e8671dd061495cfb.png)](https://p0.ssl.qhimg.com/t01e8671dd061495cfb.png)



## 总结

i386:

[![](https://p0.ssl.qhimg.com/t01fb66b4b1b4be078e.png)](https://p0.ssl.qhimg.com/t01fb66b4b1b4be078e.png)

x86_64

[![](https://p4.ssl.qhimg.com/t0142a7afa20ea48677.png)](https://p4.ssl.qhimg.com/t0142a7afa20ea48677.png)
