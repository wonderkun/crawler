> 原文链接: https://www.anquanke.com//post/id/86747 


# 【技术分享】以DVRF（路由器漏洞靶机）为例解读JEB固件漏洞利用（Part 1）


                                阅读量   
                                **112867**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pnfsoftware.com
                                <br>原文地址：[https://www.pnfsoftware.com/blog/firmware-exploitation-with-jeb-part-1/](https://www.pnfsoftware.com/blog/firmware-exploitation-with-jeb-part-1/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p0.ssl.qhimg.com/t013e4d849feb634444.jpg)](https://p0.ssl.qhimg.com/t013e4d849feb634444.jpg)**

****

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

在本系列文章中，我会向大家演示如何利用JEB的[**MIPS反编译器[1]**](https://www.pnfsoftware.com/jeb2/mips)来查找并利用嵌入式设备中的软件漏洞。为了完成这一任务，我们需要使用Praetorian提供的[**DVRF**](https://p16.praetorian.com/blog/getting-started-with-damn-vulnerable-router-firmware-dvrf-v0.1)（Damn Vulnerable Router Firmware，路由器漏洞靶机，由[**b1ack0wl**](https://twitter.com/b1ack0wl)开发）来作为练习目标。

DVRF是一个自制的固件，可以运行在Linksys E1550路由器上，这个路由器包含许多内存崩溃漏洞。DVRF的任务是充当漏洞靶机角色，以便让新手学习MIPS架构上的漏洞利用技术。据我所知的是，目前网上还没有与这方面相关的总结文章。

如果读者想要自己挑战任务，我建议大家可以阅读DVRF教程资料，生成[**完整版的MIPSEL Debian QEMU镜像**](https://blahcat.github.io/2017/07/14/building-a-debian-stretch-qemu-image-for-mipsel/)，这个镜像可以承担Linux上的漏洞开发工作流程，不会对工具做任何限制。

<br>

**二、信息搜集**

首先，我使用[**binwalk**](https://github.com/devttys0/binwalk)从固件中提取出二进制文件。然后，我们可以针对第一个挑战收集相关信息：



```
file stack_bof_01
stack_bof_01: ELF 32-bit LSB executable, MIPS, MIPS32 version 1 (SYSV), dynamically linked, interpreter /lib/ld-uClibc.so.0, not stripped
```

在JEB中加载这个文件，我们可以发现几个比较有趣的函数：

[![](https://p0.ssl.qhimg.com/t01521ec2b0aeaffc72.png)](https://p0.ssl.qhimg.com/t01521ec2b0aeaffc72.png)

除了几个经典的比较有趣的libc函数外（如system、strcpy等），我还注意到名为“dat_shell”的一个函数。

[![](https://p2.ssl.qhimg.com/t015233c57589d866ec.png)](https://p2.ssl.qhimg.com/t015233c57589d866ec.png)

从上图中我们可以看到，这个函数首先会恭喜我们解决了这个挑战任务，然后调用system函数来提供一个shell接口。现在我们知道我们的任务是将程序的执行流程重定向到dat_shell函数上。

接下来，我们可以看到程序调用了“strcpy”，这是缓冲区溢出的典型案例。因此，我们可以检查一下main函数中哪个位置调用了strcpy。

[![](https://p4.ssl.qhimg.com/t01e312f0f5d6bc35da.png)](https://p4.ssl.qhimg.com/t01e312f0f5d6bc35da.png)

首先，程序会检查我们是否输入了命令行参数，然后再显示欢迎信息。其次，程序将用户输入复制到本地变量中，打印出我们输入的数据。最后，程序会告诉我们“再来一次（Try Again）”，然后直接返回。幸运的是，strcpy不会检查输入数据的大小，这样会存在栈缓冲区溢出漏洞，正好与这个挑战的名字相呼应。



**三、构建利用程序**

与x86程序的处理过程类似，首先，我们可以在调试器中运行这个二进制程序，通过输入一个巨大的参数来验证溢出漏洞是否存在。

为了完成这一任务，我在自己的QEMU VM中启动了gdbserver，然后将JEB调试器接口附加到gdbserver上（大家可以参考[**调试手册**](https://www.pnfsoftware.com/jeb2/manual/debugging/)了解更多技术细节）。在MIPS ISA中，调用函数的返回地址存储在一个特定的寄存器中，寄存器名为$ra，寄存器的值需要从栈中提取，这一点与x86上的情况类似。然后程序会跳转到已保存的那个返回地址。

[![](https://p3.ssl.qhimg.com/t01b06196ee099d4c15.png)](https://p3.ssl.qhimg.com/t01b06196ee099d4c15.png)

在我们这个二进制程序中，可以确定的是，返回地址可以被用户所控制，具体验证方法是提供一个巨大的参数（一堆0x4F字节），然后在调用strcpy函数后，我们就能看到寄存器的状态。

[![](https://p4.ssl.qhimg.com/t01c14a90db438a6b12.png)](https://p4.ssl.qhimg.com/t01c14a90db438a6b12.png)

现在，来检查一下我们刚刚重构的栈帧（stackframe），以计算适当的填充范围。你可以使用Ctrl+Alt+k来跳转到这个视图。我将buf变量的类型修改成char数组，数组大小为该变量起始地址与下一个变量起始地址之间的距离，也就是200个字节。

[![](https://p4.ssl.qhimg.com/t01ba293445594ce657.png)](https://p4.ssl.qhimg.com/t01ba293445594ce657.png)

var04与var08变量分别对应的是已保存的返回地址以及已保存的主函数的帧指针。偏移地址位于204字节处，因为我们使用了200个字节来填充缓冲区，然后用额外的4个字节来覆盖保存的帧指针。我们可以尝试一下漏洞利用代码，如下所示：



```
#!/usr/bin/python 
padding = "O"* 204 
dat_shell_addr = "x50x09x40" # Partial overwrite with little-endian arch 
payload = padding + dat_shell_addr 
with open("input", "wb") as f:
    f.write(payload)
```



**四、没那么简单**

令人惊讶的是，我们的利用代码会导致程序在0x400970地址处出现segfault错误，这个地址位于dat_shell函数内部。我们可以通过JEB原生视图来观察这个地址：

[![](https://p5.ssl.qhimg.com/t015459b478971f8ce0.png)](https://p5.ssl.qhimg.com/t015459b478971f8ce0.png)

从上图中我们可以看到，程序在访问某个内存地址，这个内存地址由全局指针寄存器$gp的值加上0x801C偏移量计算得出。这里存在的问题是，函数在开头阶段通过$t9寄存器初始化了$gp的值（参考0x4000958那一行的代码）。

那么，$t9中的值从何而来？答案位于MIPS上常用的函数调用机制中（调用约定）：$t9寄存器首先会被设置为目标函数的地址，然后会使用诸如jalr $t9之类的指令进行跳转（参考MIPS ISA[第50页](http://math-atlas.sourceforge.net/devel/assembly/mipsabi32.pdf)的相关资料）。然后全局指针$gp会使用$t9进行初始化，用于计算各种偏移地址，特别是即将被调用的其他函数的偏移地址，因此，我们一定要保证这个值的正确性。

换句话说，当函数执行时，如果$t9的值不等于dat_shell的地址，那么函数执行过程中就会出现无效内存访问错误。为了构建正确的利用代码，我们需要从栈中加载一个任意值到$t9中，然后再跳转到这个值，将其伪造成真实的函数调用过程。

为了完成这一任务，我们需要一个“gadget（指令序列）”，所谓的“gadget”指的就是实现了上述行为的一组指令，以支持我们的跳转操作。为了搜索这个gadget，首先我们需要使用“libs”调试器命令来检查哪些动态库被加载进来。

[![](https://p3.ssl.qhimg.com/t014baf4e3ce5329c34.png)](https://p3.ssl.qhimg.com/t014baf4e3ce5329c34.png)

幸运的是，我们有三个库被加载到固定的内存地址上：libc.so.0、libgcc_s.so.0以及ld-uClibc.so.0。



**五、小插曲：为JEB设计ROP Gadget查找插件**

为了构建ROP（Return-Oriented-Programming，面向返回编程）漏洞利用代码，我们经常需要使用gadget来完成这个任务，因此，我决定开发一个gadget查找插件[[2]](https://www.pnfsoftware.com/blog/firmware-exploitation-with-jeb-part-1/#fn-675-2)。此外，我决定使用JEB中介码（Intermediate Representation，IR），而不是使用原生指令来搜索gadget，这样我就可以在JEB支持的所有架构上搜索gadget。

当在JEB中加载上面提到的三个库时，这个插件可以显示出所有的gadget，最终结果如下图所示：

[![](https://p4.ssl.qhimg.com/t011079bad4f2c64b56.png)](https://p4.ssl.qhimg.com/t011079bad4f2c64b56.png)

输出结果不包含重复的gadget，并以字母顺序进行排序，以便我们查找有价值的gadget。

那么，插件的具体工作原理是什么？通过JEB API的使用，插件将原生代码转化为IR代码，这个IR代码正是我们反编译代码第一阶段所使用的代码。在这个阶段，原生指令没有经过任何优化，会以完整的面貌呈现出来。

为了找到gadget（以跳转结尾的一组指令），我们可以在程序计数器寄存器中搜索赋值操作，并向后迭代搜索，直到找到寄存器上另一个赋值操作为止。最后一步是过滤掉相对跳转指令（漏洞利用过程中无法控制这种指令），然后我们就能得到可以利用的一个ROP gadget清单。

这个方法仅仅用到了IR代码，可以在所有架构上运行。比如，同样的代码对ARMv7二进制文件的执行结果如下图所示：

[![](https://p5.ssl.qhimg.com/t01529cae32c17a9e8b.png)](https://p5.ssl.qhimg.com/t01529cae32c17a9e8b.png)

大家可以访问此链接下载完整版的[**代码**](https://github.com/pnfsoftware/PleaseROP)。



**六、回到主题**

回到我们的任务，通过在libc库上运行我们的插件，我在0x6b20处找到了可用的gadget，如下所示：

[![](https://p0.ssl.qhimg.com/t014353e5fe11f5eaf4.png)](https://p0.ssl.qhimg.com/t014353e5fe11f5eaf4.png)

这个gadget将栈顶的值拷贝到$t9寄存器中，然后再跳转到$t9寄存器，完美的对象！

因此，我们的计划是先利用存在漏洞的strcpy来执行这个gadget，然后，程序会按照正常的调用流程来调用dat_shell地址。当我们在测试主机上禁用地址空间布局随机化（Address Space Layout Randomization，ASLR）机制后，我们可以将之前发现的libc基地址用于漏洞利用代码。最终的漏洞利用代码如下所示：



```
#!/usr/bin/python 
import struct
# LW $t9, 0($sp); JALR $t9; 
gadget_offset = 0x6b20 
libc_base = 0x77eea000 
gadget_addr = struct.pack("&lt;I", libc_base + gadget_offset) 
payload = "" 
payload += "A"*204 # padding 
payload += gadget_addr 
payload += "x50x09x40" 
with open("input", "wb") as f:
    f.write(payload)
```

代码执行结果如下图所示：

[![](https://p2.ssl.qhimg.com/t017d8b1ab1870b0adb.png)](https://p2.ssl.qhimg.com/t017d8b1ab1870b0adb.png)

大功告成，一切非常顺利。

<br>

**七、致谢**

非常感谢[**@b1ack0wl**](https://twitter.com/b1ack0wl)在挑战上给予我的帮助，也感谢[**@yrp604**](https://twitter.com/yrp604)帮忙审查这篇文章。此外，[**@joancalvet**](https://twitter.com/joancalvet)也是本文的联合作者之一。



**八、备注**

[1] 这篇文章中，我们使用的是JEB 2.3.3版，该版本将于8月21日-25日期间公布。

[2] 我将于本周晚些时候将gadget查找插件公布在GitHub上。
