> 原文链接: https://www.anquanke.com//post/id/211930 


# 对Hypervisor进行模糊测试


                                阅读量   
                                **258424**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t0178475238d8992c58.png)](https://p5.ssl.qhimg.com/t0178475238d8992c58.png)



作者：Demesne[@360](https://github.com/360)云安全研究院

## 前言

对软件进行模糊测试是发现漏洞的重要途径之一。Hypervisor（或VMM）是云环境中的核心部件，用于实现虚拟化、构建虚拟机，功能包括CPU虚拟化、内存虚拟化、IO虚拟化、硬件设备模拟等，常见的Hypervisor如QEMU-KVM、Xen、Vmware EXSi、Vmware workstation、Virtualbox等。由于Hypervisor功能与架构的复杂性，直接采用普通软件的fuzz方法对其进行模糊测试难以得到很好的效果。<br>
本文选取几项对Hypervisor进行模糊测试的相关成果进行综述，fuzz对象以QEMU/KVM为主。在此仅抛砖引玉，如有问题或建议欢迎随时交流~

注：本文为综述类文章，大部分图片选取至论文原文，可参见正文中引用标志。



## 目录

以时间先后排序，几项相关成果如下：<br>
① When virtualization encounter AFL-A Portable virtual device fuzzing framework with AFL(2016)<br>
② VDF: Targeted Evolutionary Fuzz Testing of Virtual Devices(2017)<br>
③ 使用syzkaller对vhost内核模块进行模糊测试(2018)<br>
④ 使用AFL fuzz virtio-blk&amp;SPDK(2019)<br>
⑤ Qtest结合libfuzzer对QEMU设备进行FUZZ(2020)<br>
⑥ HYPER-CUBE: High-Dimensional Hypervisor Fuzzing(2020)

将以上分为四个大类，分别为：<br>**一、 fuzz多个Hypervisor的通用方法：**<br>
① When virtualization encounter AFL: A Portable virtual device fuzzing framework with AFL(2016)<br>
② HYPER-CUBE: High-Dimensional Hypervisor Fuzzing(2020)<br>**二、纯QEMU硬件模拟IO fuzz：**<br>
③ VDF: Targeted Evolutionary Fuzz Testing of Virtual Devices(2017)<br>**三、QEMU-KVM/virtio fuzz：**<br>
④ 使用AFL fuzz virtio-blk(2019)<br>
⑤ Qtest结合libfuzzer对QEMU设备进行FUZZ(2020)<br>**四、vhost内核模块 fuzz：**<br>
⑥ 使用syzkaller对vhost内核模块进行模糊测试(2018)

<a class="reference-link" name="%E6%AD%A3%E6%96%87"></a>正文



## 一、 fuzz多个Hypervisor的通用方法：

<strong>① When virtualization encounter AFL: A Portable virtual device fuzzing framework with AFL(2016)[1]<br>
Jack Tang and Moony Li @ Trend Micro, Blackhat Europe 2016</strong><br>
本文提出一个针对虚拟硬件设备的fuzz系统，特点为可移植性和代码覆盖率指导，适用于开源和闭源的Hypervisor。系统由三部分组成：定制的guest BIOS（Customized BIOS System，CBS）、设备控制客户端（Device Control Clients，DCC）和集成的AFL-fuzz。

[![](https://p5.ssl.qhimg.com/t017f42e17d0c875d9c.png)](https://p5.ssl.qhimg.com/t017f42e17d0c875d9c.png)

1.定制的guest BIOS（称其为CBS组件）：比操作系统更轻量级，是与设备进行IO交互的接口。<br>
a) 功能：发现fuzz的目标设备；初始化设备工作环境；运行一个内存和IO操作的代理服务器（Memory and IO space Operation Proxy Server,MIOPS）<br>
b) 实现：基于Seabios定制。<br>
BIOS一般有三个运行阶段：开机自检阶段（初始化内部状态、外部接口、检测和启动硬件）、启动阶段（将boot loader载入内存执行、启动操作系统）、BIOS运行时服务阶段（提供基本的运行时服务）。<br>
本文中的CBS组件只保留开机自检阶段，在该阶段检测物理内存、启动硬件设备、识别fuzz目标设备，然后启动MIOPS服务器。<br>
MIOPS服务器接收设备控制客户端（DCC）发送的包含IO操作的请求（称其为MIOA请求，即Memory IO Access请求），并执行IO操作。MIOPS和DCC之间使用虚拟串口通信。<br>
一个MIOA请求使用伪代码的形式定义，如：

```
inb &lt;address&gt;
inw &lt;address&gt;
inl &lt;address&gt;
outb &lt;address&gt; &lt;value&gt;
outw &lt;address&gt; &lt;value&gt;
outl &lt;address&gt; &lt;value&gt;
write &lt;address&gt; &lt;value&gt; &lt;length&gt;
read &lt;address&gt; &lt;length&gt;
```

当MIOPS接收到MIOA请求时，会解析该请求，并执行IO操作，解析过程很像QEMU的qtest框架，示例代码如：

[![](https://p1.ssl.qhimg.com/t01160d03d5e2e83fa5.png)](https://p1.ssl.qhimg.com/t01160d03d5e2e83fa5.png)

2) 设备控制客户端（称其为DCC组件）<br>
a) 功能：DCC运行在host端。主要负责启动VMM进程，解析AFL-fuzz生成的DCD（Device Control Data）至MIOA请求，将MIOA请求发送至MIOPS服务器。<br>
b) 实现：定义和解析DCD文件。<br>
以USB XHCI设备为例，DCD文件如下：

[![](https://p1.ssl.qhimg.com/t018024553e0bdd6f38.png)](https://p1.ssl.qhimg.com/t018024553e0bdd6f38.png)

该DCD文件包含两个USB XHCI命令，分别以命令id 0x0B和0x0C开头（绿色下划线），接下来的内容为该命令的参数（红色下划线）。<br>
对应的结构体定义如下：

```
typedef struct _command_entry
`{`
u32 _slotid;
u32 _command_id; //对应绿色下划线内容
void* _inctx; 
u8 _input_buf[32]; //对应红色下划线内容
`}`command_entry_t;
```

再举一个例子，软盘设备的DCD格式定义如下：

```
struct fdc_command
`{`
unsigned char cid; //命令的id号
unsigned int args_count;//命令的参数数量
unsigned int args[0];//参数列表
`}`;
```

如：

```
struct fdc_command
`{`
cid = 0x8e
args_count = 0x5
args[] = [0x45, 0x12, 0x34, 0x7f, 0x98]
`}`;
```

将会解析为以下MIOA请求（0x3f5为软盘控制器的IO端口号）：

```
outb 0x3f5 0x8e
outb 0x3f5 0x45
outb 0x3f5 0x12
outb 0x3f5 0x34
outb 0x3f5 0x7f
outb 0x3f5 0x98
```

上面这个例子比较简单，但有一些命令的翻译过程会更复杂。比如在USB XHCI的MIOA请求生成的时候需要查看USB XHCI的标准，同时也需要额外属性，比如XHCI命令队列映射的物理内存地址，XHCI事件队列映射的物理内存地址等，这些信息需要在初始化USB XHCI设备时获取。<br>
3) 集成的AFL

[![](https://p5.ssl.qhimg.com/t016225a5871504a475.png)](https://p5.ssl.qhimg.com/t016225a5871504a475.png)

简化后的AFL相关架构如上图。<br>
a) 插桩：若VMM开源，使用AFL-gcc编译目标虚拟设备的源码；若VMM不开源，逆向二进制代码，对目标虚拟设备二进制指令进行patch。<br>
b) 输入：使用DCD文件作为输入，使用AFL的算法随机变异。

使用该系统fuzz QEMU的磁盘控制器，重新发现了Venom漏洞（CVE-2015-3456）。过程如下：<br>
a) 用afl-gcc编译fdc.c，修改rules.mak文件如下：

[![](https://p2.ssl.qhimg.com/t010c53d32ddf855cc0.png)](https://p2.ssl.qhimg.com/t010c53d32ddf855cc0.png)

b) 定义输入文件格式：

```
struct fdc_command
`{`
unsigned char cid; //command id
unsigned int args_count;
unsigned int args[0];
`}`;
```

c) 准备了30个输入样例。<br>
d) 开启DCC客户端，DCC开启VMM和MIOPS，创建管道用于通信：

```
$ mkfifo jack_pipe
$ mkfifo jack_pipe1
$ qemu-system-x86_64 -bios out/bios.bin -serial pipe:jack_pipe -serial pipe:jack_pipe1
```

e) 开始fuzz：

```
$ afl-fuzz -t 99000 -m 2048 -i IN/ -o OUT/ &lt;DCC command&gt; @@
```

对QEMU2.3版本，在8G内存，4核CPU上运行，约1.5小时后复现了Venom漏洞。

<strong>② HYPER-CUBE: High-Dimensional Hypervisor Fuzzing(2020)[2][3]<br>
Sergej Schumilo, Cornelius Aschermann, Ali Abbasi, Simon W¨orner and Thorsten Holz, NDSS 2020</strong><br>
本文提出了HYPER-CUBE，一个针对Hypervisor的fuzz工具，可以适用于开源和闭源的Hypervisor。本方法基于定制的操作系统，部署了一个定制的字节码解释器，与其他fuzzer不同的是，本系统不采用覆盖率引导的fuzz方式，但能够达到高吞吐、高效率和高代码覆盖率。该系统可以在5分钟之内重新发现Venom漏洞（CVE-2015-3456），一共发现了54个bug，获得43个CVE号。<br>
系统由以下几个部分组成：<br>
a) 定制的guest操作系统：HYPER-CUBE OS。<br>
b) guest内运行的字节码解释器：TESSERACT。<br>
c) host上运行的一组工具，用于向TESSERACT发送字节码、语料最小化、监控guest行为等。

[![](https://p3.ssl.qhimg.com/t01fc2040da69c64879.png)](https://p3.ssl.qhimg.com/t01fc2040da69c64879.png)

1) HYPER-CUBE OS<br>
a) 功能：<br>
定制的HYPER-CUBE OS可以支持从GRUB等常见的bootloader启动。该OS有两个主要功能：内存管理和设备枚举。设备枚举和启动TESSERACT需要申请一段内存，OS的内存管理模块分配了一块堆内存用于申请和使用；除此之外，其他交互接口有时会使用物理内存，OS在虚拟地址空间内创建了一对一的线性物理地址映射。<br>
HYPER-CUBE OS最重要的功能是为fuzzing列举不同的接口，如图中所示，有PCI设备、ISA设备等。<br>
b) 实现：<br>
-启动阶段<br>
不同的bootloader加载OS内核的流程不同，为了忽略它们之间的差别，本文使用multiboot2。<br>
初始化中断方面，为了能与外部硬件异步交互，使用了PIC（Programmable Interrupt Controller）和APIC（Advanced Programmable Interrupt Controller）。在启动阶段，HYPER-CUBE OS对PIC和APIC进行配置，安装必需的中断和异常处理句柄。<br>
-内存管理<br>
本文定制了一个堆内存分配器，允许任务在一次分配一个页面，这个设计能够简化实现的复杂性、减少堆上内存碎片，还提高了系统的鲁棒性，但是缺点在于增加了内存消耗。HYPER-CUBE OS在设备列举和与TESSERACT交互中内存分配次数较少，所以这个缺点在实际应用中并不明显。<br>
-设备枚举<br>
像PCI设备、APIC或者HPET（High Precision Event Timer）会将内部寄存器映射至物理地址，系统列举出所有的MMIO和端口IO的地址范围。<br>
2) TESSERACT<br>
TESSERACT是一个指令集解释器。提供的操作码句柄如：

```
write mmio(region id, offset, data)
read mmio(region id, offset)
xor mmio(region id, offset, mask)
hypercall(eax, ebx, ecx, edx, esi)
...

```

TESSERACT的字节码格式定义使用类文本的风格。有两种方式向fuzzer输入字节码指令：如果在host端没有字节码输入，TESSERACT使用伪随机数生成器来生成随机的指令。或者在OS中内置字节码字符串。此外，系统还提供了语料最小化的脚本。



## 二、纯QEMU硬件模拟IO fuzz：

<strong>③ VDF: Targeted Evolutionary Fuzz Testing of Virtual Devices(2017)[4]<br>
Andrew Henderson, Heng Yin, Guang Jin, Hao Han, and Hongmei Deng, RAID 2017</strong><br>
本文提出了工具VDF（Virtual Device Fuzzer），用于对QEMU模拟的硬件设备进行模糊测试。<br>
Fuzz虚拟设备的难度在于设备是有“状态”的，每一个设备需要在初始化之后才能正常工作，正常工作时的行为也有固定的模式，因此直接发送随机的变异数据效果并不好。VDF使用“录制-重放”（Record and Replay）方法，首先收集设备的初始化行为和正常工作的行为，再对正常的工作行为进行变异后重放。VDF工具由三部分组成：<br>
1） 录制。<br>
在QEMU代码中增加的一段录制代码，用于记录虚拟设备的IO读写行为，在guest OS启动，虚拟设备初始化，以及设备正常工作时，VDF会记录guest对虚拟设备控制寄存器的读写操作，生成一个设备行为的数据样例。数据样例包括初始化样例和正常工作的种子样例两部分。VDF定义了录制样本的格式。

[![](https://p1.ssl.qhimg.com/t01cfb4030881ae0a30.png)](https://p1.ssl.qhimg.com/t01cfb4030881ae0a30.png)

2） 插桩及种子变异。<br>
a) 插桩：VDF的插桩功能基于AFL开发，可以做到有选择性的插桩，只对我们关心的虚拟设备部分代码进行插桩。该功能的实现在于在AFL编译工具链中添加了一个编译参数，只有带有该flag的源代码文件才会被插桩。

[![](https://p1.ssl.qhimg.com/t01fac344e1e5c4c23e.png)](https://p1.ssl.qhimg.com/t01fac344e1e5c4c23e.png)

b) 语料最小化：测试样例的预处理过程有三步：去掉不合法的样本、去掉crash/hang之后的样本、去掉复现crash/hang非必要条件的样本。

[![](https://p4.ssl.qhimg.com/t01ecbf7e364244c411.png)](https://p4.ssl.qhimg.com/t01ecbf7e364244c411.png)

3） 重放。基于QEMU的Qtest单元测试框架开发了一个新的QEMU accelerator，大概在QEMU中加入了850行代码，该工具将Qtest的client和server合并到一起，能够使VDF工具在事件发生时直接进行重放样本，节省了进程间通信的时间。

[![](https://p1.ssl.qhimg.com/t0100039555de868f10.png)](https://p1.ssl.qhimg.com/t0100039555de868f10.png)

效果：对18个虚拟设备进行fuzz，在其中6个虚拟设备中发现了超过一千个crash，报了一些CVE。代码覆盖率平均约62.32%。



## 三、 QEMU-KVM/virtio fuzz：

使用QEMU纯软件模拟的方式构建虚拟机的性能较差，云环境中一般会使用QEMU-KVM方案。KVM基于硬件虚拟化辅助技术（如Intel VT-x、AMD-V），可以提供CPU、内存的虚拟化，但IO硬件设备还是由QEMU来模拟的，效率并不高。为了解决这个问题，Rusty Russell开发了virtio框架，virtio是半虚拟化设备，需要在guest中安装对应的驱动程序。virtio在guest和host之间使用共享内存vring结构传递IO数据，极大提高了效率和吞吐率。关于virtio的实现细节在此不再详述，可以参考Rusty Russell的paper[5]。

<strong>④ 使用AFL fuzz virtio-blk(2019)[6]<br>
Virtio Device Fuzzing by Dmitrii Stepanov, KVM Forum 2019</strong><br>
virtio-blk是virtio虚拟存储设备的一种实现，使用QEMU作为后端。SPDK是由intel发起的虚拟化存储优化框架，替代了QEMU的功能，使用vhost用户态程序作为后端。本演讲主要分享了使用AFL对QEMU virtio虚拟化存储后端进行模糊测试。实现方式为在AFL和QEMU之间增加一个软件代理。AFL和代理之间使用Unix socket通信，QEMU和代理之间使用Qtest框架以及QMP协议通信。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01231780024cba2081.png)

1）方法<br>
a) 插桩：使用afl-clang对QEMU中virtio部分代码进行插桩。<br>
b) QEMU状态：AFL fork() QEMU，QEMU进程的运行状态将直接可以由AFL获得。<br>
c) 输入：首先尝试使用guest存储设备的内存进行随机变异，缺点是效率低下，每次都需要重新初始化guest内存；其次使用现有的API修改virtio共享内存的descriptor table，速度快但是没有触及到可能崩溃的路径；最终使用的方法是，对存储设备协议和virtio共享内存的descriptor table都进行随机变异，这个方法在代码覆盖率和效率上都比较好。

[![](https://p1.ssl.qhimg.com/t01b0e8533fe9dcc3b1.png)](https://p1.ssl.qhimg.com/t01b0e8533fe9dcc3b1.png)

2）效果：发现了一些crash和CVE。<br>
3）实现：代码见github[7]<br>
对QEMU修改：<br>
a. virtio-blk代码增加AFL fuzz支持<br>
b. tests/下增加基于Qtest框架的test_proxy程序<br>
对AFL的修改：<br>
增加与test_proxy通信的unix socket模块。

**⑤ Qtest结合libfuzzer对QEMU设备进行FUZZ(2020)**<br>
QEMU5.0.0版本主分支增加了部分fuzz代码。代码源于2019年google的暑期项目[8]，作者是Alexander Oleinik。这部分fuzz代码基于qtest和libfuzzer。qtest是QEMU的单元测试框架，libfuzzer是google开发的一个覆盖率引导的fuzz引擎。本部分首先介绍qtest，然后介绍qtest和libfuzzer结合对QEMU进行模糊测试。<br>
（一） Qtest——QEMU的单元测试框架

[![](https://p4.ssl.qhimg.com/t01e83919516b3cb554.png)](https://p4.ssl.qhimg.com/t01e83919516b3cb554.png)

Qtest是QEMU代码主分支内的一个用于做单元测试的框架，主要用作QEMU模拟的硬件设备的开发人员进行单元测试，源码在qemu/tests/qtest目录。[9][10][11]<br>
Qtest由两部分组成：Qtest client和Qtest server。client和server之间通过unix socket通信，Qtest支持发送PIO、MMIO、中断、QMP指令等。<br>
1.Qtest client。<br>
qtest client是我们编写的测试某个设备的测试程序，按照从底层至上层的封装顺序，它基于：<br>
-glib单元测试框架（2007）。[12]<br>
-libqtest（2012）：对glib test做封装，第一版QEMU的单元测试框架<br>
-libqos（2012）：增加PCI的封装、内存分配，为编写qtest样例提供了一个小的系统库[13][14]<br>
-qgraph（2018 sinceQEMU4.0）：支持多架构；把系统、设备、API抽象成图[15]<br>
一个简单的例子：

```
/* AC97 test case */
static void nop(void) `{` `}`
int main(int argc, char **argv) 
`{` 
int ret;
g_test_init(&amp;argc, &amp;argv, NULL);      //初始化glib测试框架
qtest_add_func("/ac97/nop", nop);   //增加被测试路径和已经定义的测试函数 
qtest_start("-device AC97");         //增加QEMU启动参数
ret = g_test_run();                 //运行测试
qtest_end();
return ret; 
`}`
```

写一个新的测试程序的步骤：<br>
1) 编写测试代码tests/qtest/foo-test.c<br>
2) 在tests/qtest/Makefile.include增加新的源代码：

```
check-qtest-generic-y = tests/qtest/foo-test$(EXESUF)
tests/qtest/foo-test$(EXESUF): tests/qtest/foo-test.o $(libqos-obj-y)
```

3) 编译测试程序

```
$ make tests/qtest/foo-test
```

4) 运行测试程序：

```
$ QTEST_LOG=1 QTEST_QEMU_BINARY=\
       i386-softmmu/qemu-system-i386 tests/qtest/foo-test
```

2.Qtest server。<br>
qtest server注册为QEMU的一种accelerator，在启动QEMU时添加以下参数：

```
qemu-system-x86_64 -qtest unix:xxx 
            -qtest-log xxx 
            -chardev socket,path=xxx,id=char0
            -mon chardev=char0,mode=control
            -machine accel=qtest
            -display none
```

正如TCG、KVM也是QEMU的accelerator，qtest承担的角色与他们类似。在普通使用场景中（如图左），VCPU和虚拟硬件交互；在qtest使用场景中，qtest直接与虚拟硬件交互（如图右）。[13]

[![](https://p2.ssl.qhimg.com/t01144c2776665cea00.png)](https://p2.ssl.qhimg.com/t01144c2776665cea00.png)

-qtest server的启动流程：

```
client fork()
    qemu-system-x86_64
        qtest_init();
            qtest_process_command();
                cpu_inb();          //PIO
                address_space_rw();  //MMIO
                QMP();             //QMP
```

-代码分析：<br>
在libqtest.c中，qtest_init_without_qmp_handshake()启动QEMU作为子进程，在QEMU的启动主函数vl.c中，设置accelerator为qtest将会调用qtest_init()，qtest_init()在qtest.c中定义。<br>
tests/libqos/libqtest.c为client端部分，将以以下qtest参数启动QEMU:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e1247914ed1cb8ab.png)

vl.c是QEMU启动的入口代码，解析QEMU命令行参数:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019821b6b4daa87a20.png)

qtest_init()初始化qtest server：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0129704ccf5aaf6ee4.png)

qtest_init()定义在qtest.c中。<br>
qtest.c中创建了一个qtest的字符设备，绑定了几个handler：

[![](https://p3.ssl.qhimg.com/t01243ab2445027c40a.png)](https://p3.ssl.qhimg.com/t01243ab2445027c40a.png)

函数原型为：

```
void qemu_chr_add_handlers(CharDriverState *s,
                           IOCanReadHandler *fd_can_read,
                           IOReadHandler *fd_read,
                           IOEventHandler *fd_event,
                           void *opaque)

```

对应的IOReadHandler为qtest_read；IOEventHandler为qtest_event。

```
qtest_read()-&gt;qtest_process_inbuf()-&gt;qtest_process_command()-&gt;命令解析和执行
```

qtest_event()中有两种case：CHR_EVENT_OPENED和CHR_EVENT_CLOSED，定义开启和关闭字符设备时的操作，将log写入qtest log文件中。

（二）使用qtest+libfuzzer对QEMU设备进行模糊测试<br>
实现方式为：在qgraph库的基础上，增加libfuzzer部分代码。关于libfuzzer网上有很多资料[16]，在此不再展开叙述。<br>
1.代码实现<br>
代码路径在tests/qtest/fuzz，在fuzz.c中定义了libfuzzer的入口函数：

```
//在fuzz之前运行一次，用于初始化。在本函数中初始化qgraph，输出命令行usage，根据用户输入调用针对不同设备的fuzz模块。
int LLVMFuzzerInitialize(int *argc, char ***argv, char ***envp)
//运行一次输入，参数是输入的数据和数据大小。该函数还负责设备初始化、调用fuzz目标函数以及重置程序状态。
int LLVMFuzzerTestOneInput(const unsigned char *Data, size_t Size)

```

2.使用<br>
1）安装编译

```
$ sudo apt-get install clang-8 lldb-8 lld-8 libfuzzer-8-dev libglib2.0-0 libglib2.0-dev libpixman-1-dev
$ mkdir build
$ cd build
$ CC=clang-8 CXX=clang++-8 ../configure --enable-fuzzing
$ make i386-softmmu/fuzz
```

2）运行：

[![](https://p0.ssl.qhimg.com/t01fcc9aad9ec6e5116.png)](https://p0.ssl.qhimg.com/t01fcc9aad9ec6e5116.png)

目前支持8个fuzz目标,如图所示。<br>
3）对virtio-net-socket进行fuzz：<br>
设置-print_final_stats=1输出最终统计数据，-max_total_time设置fuzz运行时间（秒）。

[![](https://p0.ssl.qhimg.com/t0138cff65c94001708.png)](https://p0.ssl.qhimg.com/t0138cff65c94001708.png)

4） 运行截图

[![](https://p3.ssl.qhimg.com/t01b86c7983bc23d0f1.png)](https://p3.ssl.qhimg.com/t01b86c7983bc23d0f1.png)

5） 精简语料集：<br>
增加-merge=1参数，CORPUS_MIN为精简后的语料路径，CORPUS为原语料路径。

[![](https://p4.ssl.qhimg.com/t0180f1184dc1b7e461.png)](https://p4.ssl.qhimg.com/t0180f1184dc1b7e461.png)

3.增加生成代码覆盖率报告<br>
生成代码覆盖率报告有利于清晰了解fuzz状态，QEMU主分支中fuzz部分目前还没有这个功能，因此笔者自行添加了该功能，方法如下：<br>
1）编译时添加-fprofile-instr-generate -fcoverage-mapping参数。该参数用于增加clang的代码覆盖率支持。[17]

[![](https://p1.ssl.qhimg.com/t013396332a9351d0fc.png)](https://p1.ssl.qhimg.com/t013396332a9351d0fc.png)

然后编译运行：

```
$ make i386-softmmu/fuzz
$ ./qemu-fuzz-i386 --fuzz-target=virtio-scsi-fuzz -max_total_time=300 -print_final_stats=1 CORPUS
```

2） 运行后会在当前目录下生成一个default.profraw文件。<br>
3） 使用llvm工具将profraw文件转换成profdata格式：

```
$ llvm-profdata-8 merge -sparse *.profraw -o default.profdata
```

4） 使用llvm-cov工具查看代码覆盖率报告：

```
$ llvm-cov-8 report qemu-fuzz-i386 -instr-profile=default.prodata
```

5） 输出代码覆盖率报告：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0158aabff01aa6914b.png)



## 四、vhost内核模块 fuzz：

在前面提到的virtio框架的基础上，vhost将virtio后端从QEMU改为内核，在内核中加入了vhost模块，进一步减少用户态和内核态之间的切换，使得IO数据可以在内核态得到处理，进一步提高IO吞吐率和效率。（PS：后来为了适配Open vSwitch等虚拟交换机软件等SDN场景，提高效率，又将virtio后端重新从内核移到了用户态，也就是vhost-user和DPDK，本文不再详细讨论）<br>**⑥使用syzkaller对vhost内核模块进行模糊测试(2018)**<br>
syzkaller是google安全研究人员开发的基于代码覆盖率的内核API模糊测试工具，用户可以通过自定义描述脚本对内核的系统调用进行fuzz。[18]vhost内核模块也可以使用suzkaller进行fuzz。在vhost内核模块的CVE中，就有使用syzkaller的自动化fuzz系统syzbot发现的漏洞。[19]<br>
关于syzkaller，在此仅简单叙述。官方文档中的架构图如下：

[![](https://p0.ssl.qhimg.com/t0129d136e9f325b7c4.png)](https://p0.ssl.qhimg.com/t0129d136e9f325b7c4.png)

syzkaller主要由三部分组成：<br>
1)syz-manager:运行在host宿主机上，用于开启、监控和重启虚拟机，在虚拟机中启动syz-fuzzer进程，管理语料及crash。<br>
2)syz-fuzzer:运行在guest虚拟机中，负责fuzz进程的生成输入、变异、语料最小化等，把触发新代码覆盖的输入通过RPC回传给syz-manager。在这个过程中，会开启syz-executor进程。<br>
3)syz-executor:执行一次输入，把结果回传。每个输入都是一串系统调用（使用syzkaller的格式定义）。

此外，收集内核的代码覆盖率需要内核支持kcov。在Linux内核版本4.6中开始支持kcov，可以通过配置内核参数来启用。对于较旧版本的内核,需要在内核中添加KCOV覆盖率代码。

-syzbot<br>
syzbot是一个基于syzkaller的自动化fuzz系统。它能持续不停的运行syzkaller，对linux内核各个分支进行模糊测试，自动报告crash，作者是google的Dmitry Vyukov。[20]syzbot还会监控bug的当前状态（是否已被修复等），监测对于bug的patch是否有效，完成发现-报告-复现-修复的整个流程。<br>
下图为syzbot报告的vhost内核模块的漏洞。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015584bff21590337c.png)

##### <a class="reference-link" name="%E5%8F%82%E8%80%83%E6%96%87%E6%A1%A3%EF%BC%9A"></a>参考文档：

[1] When virtualization encounters AFL<br>[https://www.blackhat.com/docs/eu-16/materials/eu-16-Li-When-Virtualization-Encounters-AFL-A-Portable-Virtual-Device-Fuzzing-Framework-With-AFL.pdf](https://www.blackhat.com/docs/eu-16/materials/eu-16-Li-When-Virtualization-Encounters-AFL-A-Portable-Virtual-Device-Fuzzing-Framework-With-AFL.pdf)<br>
[2] HYPER-CUBE:High-Dimensional Hypervisor Fuzzing<br>[https://www.ei.ruhr-uni-bochum.de/media/emma/veroeffentlichungen/2020/02/07/Hyper-Cube-NDSS20.pdf](https://www.ei.ruhr-uni-bochum.de/media/emma/veroeffentlichungen/2020/02/07/Hyper-Cube-NDSS20.pdf)<br>
[3] Slides: HYPER-CUBE:High-Dimensional Hypervisor Fuzzing<br>[https://www.ndss-symposium.org/wp-content/uploads/23096-slides.pdf](https://www.ndss-symposium.org/wp-content/uploads/23096-slides.pdf)<br>
[4] VDF: Targeted Evolutionary Fuzz Testing of Virtual Devices<br>[https://link.springer.com/chapter/10.1007/978-3-319-66332-6_1](https://link.springer.com/chapter/10.1007/978-3-319-66332-6_1)<br>
[5] virtio: Towards a De-Facto Standard For Virtual I/O Devices<br>
[6] [2019] Virtio Device Fuzzing by Dmitrii Stepanov<br>[https://www.youtube.com/watch?v=dk6SUD8ovXw](https://www.youtube.com/watch?v=dk6SUD8ovXw)<br>
[7] Virtio Device Fuzzing by Dmitrii Stepanov on Github<br>[https://github.com/yandex/qemu/commit/3b82cea6af0f1640b81966e7200a816e4198340b](https://github.com/yandex/qemu/commit/3b82cea6af0f1640b81966e7200a816e4198340b)<br>
[8] [Qemu-devel] [RFC 00/19] Add virtual device fuzzing support<br>[https://lists.sr.ht/~philmd/qemu/%3C20190725032321.12721-1-alxndr%40bu.edu%3E](https://lists.sr.ht/~philmd/qemu/%3C20190725032321.12721-1-alxndr%40bu.edu%3E)<br>
[9] Features/QTest<br>[https://wiki.qemu.org/Features/QTest](https://wiki.qemu.org/Features/QTest)<br>
[10] QEMU on GitHub<br>[https://github.com/qemu/qemu](https://github.com/qemu/qemu)<br>
[11] Testing in QEMU<br>[https://github.com/qemu/qemu/blob/master/docs/devel/testing.rst](https://github.com/qemu/qemu/blob/master/docs/devel/testing.rst)<br>
[12] 理解 GLib 的单元测试框架<br>[https://segmentfault.com/a/1190000003996312](https://segmentfault.com/a/1190000003996312)<br>
[13] Integrated Testing in QEMU- An overview of qtest and qemu-test<br>[https://www.linux-kvm.org/images/8/89/2012-forum-Liguori-qtest.pdf](https://www.linux-kvm.org/images/8/89/2012-forum-Liguori-qtest.pdf)<br>
[14] Testing QEMU emulated devices using qtest<br>[https://www.linux-kvm.org/images/4/43/03×09-TestingQEMU.pdf](https://www.linux-kvm.org/images/4/43/03x09-TestingQEMU.pdf)<br>
[15] Features/qtest driver framework<br>[https://wiki.qemu.org/Features/qtest_driver_framework](https://wiki.qemu.org/Features/qtest_driver_framework)<br>
[16] libFuzzer Tutorial<br>[https://github.com/google/fuzzing/blob/master/tutorial/libFuzzerTutorial.md](https://github.com/google/fuzzing/blob/master/tutorial/libFuzzerTutorial.md)<br>
[17] Clang 8 documentation<br>[https://releases.llvm.org/8.0.0/tools/clang/docs/SourceBasedCodeCoverage.html](https://releases.llvm.org/8.0.0/tools/clang/docs/SourceBasedCodeCoverage.html)<br>
[18] syzkaller – kernel fuzzer<br>[https://github.com/google/syzkaller](https://github.com/google/syzkaller)<br>
[19] KASAN: use-after-free Read in vhost_transport_send_pkt – CVE-2018-14625<br>[https://syzkaller.appspot.com/bug?extid=bd391451452fb0b93039](https://syzkaller.appspot.com/bug?extid=bd391451452fb0b93039)<br>
[20] syzbot<br>[https://syzkaller.appspot.com/](https://syzkaller.appspot.com/)

#### <a class="reference-link" name="%E4%B8%8B%E9%9D%A2%E6%98%AF%E5%B9%BF%E5%91%8A%E6%97%B6%E9%97%B4%EF%BC%9A"></a>下面是广告时间：

#### [lifangrun1@360.cn](mailto:lifangrun1@360.cn)

#### <a class="reference-link" name="%E6%AF%94%E5%BF%83~(%C2%B4%E2%96%BD%60%CA%83%E2%99%A1%C6%AA)"></a>比心~(´▽`ʃ♡ƪ)
