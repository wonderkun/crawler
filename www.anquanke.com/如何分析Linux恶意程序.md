> 原文链接: https://www.anquanke.com//post/id/213433 


# 如何分析Linux恶意程序


                                阅读量   
                                **263444**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01e20ec5ee127da91b.jpg)](https://p4.ssl.qhimg.com/t01e20ec5ee127da91b.jpg)



## 一、前言

近期接手了不少Linux恶意程序的分析任务，在处理任务的过程中，当然会参考网络中的一些技术文档，于是就发现了一个问题：在各大平台上，关于Linux恶意程序的分析介绍相对较少；所以，自己就想对这方面的知识进行一些弥补，把自己对Linux恶意程序的分析方法和思路提炼分享出来，供大家参考交流。<br>
本篇文章中提到的所有方法均是在本人实际工作中接触使用并提炼出来的，例如：当遇到的rootkit会从自身解密ELF模块，并将其加载进内存中时，才发现详细了解ELF文件结构是多么的重要；当使用IDA远程调试，代码执行逻辑有些混乱时，才发现使用GDB进行调试才是最靠谱的；当需要对嵌入在内核中的内核代码进行调试时，才发现原来使用IDA进行内核调试是多么的方便。



## 二、Linux恶意程序的适用范围

Linux存在着许多不同的Linux版本，但它们都使用了Linux内核。Linux可安装在各种计算机硬件设备中，比如：路由器、防火墙、台式计算机及服务器等。<br>
因此，在各种Linux内核的设备中，都能被植入Linux恶意程序。



## 三、ELF文件解析

要反编译Linux恶意程序，首先需要理解Linux恶意程序的二进制结构本身；ELF目前已经成为UNIX和类UNIX操作系统的标准二进制格式。在RedHat、Ubuntu、Kail以及其他操作系统中，ELF格式可用于可执行文件、共享库、目标文件、coredump文件，甚至内核引导镜像文件等。因此，要想更好的分析Linux恶意程序，了解ELF文件结构至关重要。

### <a class="reference-link" name="1%EF%BC%8EELF%E6%96%87%E4%BB%B6%E7%9A%84%E7%BC%96%E8%AF%91%E9%93%BE%E6%8E%A5"></a>1．ELF文件的编译链接

通过对编译链接过程中生成的不同文件进行分析对比，可以辅助我们更好的理解ELF文件结构。<br>
Linux下ELF文件的编译链接过程主要分为：预处理、编译、汇编、链接；在链接过程中，我们可以根据需求采用静态链接或动态链接。

[![](https://p3.ssl.qhimg.com/t0167ab0b6ff8b40fe4.png)](https://p3.ssl.qhimg.com/t0167ab0b6ff8b40fe4.png)

[![](https://p2.ssl.qhimg.com/t01dec299bf41850443.png)](https://p2.ssl.qhimg.com/t01dec299bf41850443.png)

a.预处理：将要包含(include)的文件插入原文件中、将宏定义展开、根据条件编译命令选择要使用的代码，最后将这些代码输出到一个“.i”文件中等待进一步处理。<br>
gcc -E -o sum.i sum.c<br>
gcc -E -o main.i main.c<br>
b.编译：把C/C++代码(比如上面的”.i”文件)“翻译”成汇编代码。<br>
gcc -S -o sum.s sum.i<br>
gcc -S -o main.s main.i<br>
c.汇编：将第二步输出的汇编代码翻译成符合一定格式的机器代码，在Linux系统上一般表现位ELF目标文件(OBJ文件)。<br>
gcc -c -o sum.o sum.s<br>
gcc -c -o main.o main.s<br>
d.链接：将汇编生成的OBJ文件、系统库的OBJ文件、库文件链接起来，最终生成可以在特定平台运行的可执行程序。<br>
gcc -o prog main.o sum.o<br>
e.动态链接：使用动态链接库进行链接，生成的程序在执行的时候需要加载所需的动态库才能运行。动态链接生成的程序体积较小，但是必须依赖所需的动态库，否则无法执行。<br>
gcc -o prog_dynamic main.o sum.o<br>
f.静态链接：使用静态库进行链接，生成的程序包含程序运行所需要的全部库，可以直接运行，不过静态链接生成的程序体积较大。<br>
gcc -static -o prog_static main.o sum.o

[![](https://p4.ssl.qhimg.com/t01e31505f3f5424c38.png)](https://p4.ssl.qhimg.com/t01e31505f3f5424c38.png)

### <a class="reference-link" name="2%EF%BC%8EELF%E6%96%87%E4%BB%B6%E7%B1%BB%E5%9E%8B"></a>2．ELF文件类型

ELF文件类型主要有：可重定位目标文件、可执行目标文件、共享目标文件。<br>
a.可重定位目标文件<br>
包含二进制代码和数据，其形式可以在编译时与其他可重定位目标文件合并起来，创建一个可执行目标文件。一般有扩展名为：“.o”

[![](https://p5.ssl.qhimg.com/t01893e4690d3c99ed4.png)](https://p5.ssl.qhimg.com/t01893e4690d3c99ed4.png)

b.可执行目标文件<br>
包含二进制代码和数据，其形式可以被直接复制到内存并执行。

[![](https://p0.ssl.qhimg.com/t01e9f674c345cd5fe8.png)](https://p0.ssl.qhimg.com/t01e9f674c345cd5fe8.png)

c.共享目标文件<br>
一种特殊类型的可重定位目标文件，可以在加载或者运行时被动态地加载进内存并链接。

[![](https://p0.ssl.qhimg.com/t01eb3b6794693de348.png)](https://p0.ssl.qhimg.com/t01eb3b6794693de348.png)

### <a class="reference-link" name="3%EF%BC%8EELF%E7%BB%93%E6%9E%84%E8%A7%A3%E6%9E%90"></a>3．ELF结构解析

<a class="reference-link" name="%EF%BC%881%EF%BC%89%E5%B7%A5%E5%85%B7_010editor"></a>**（1）工具_010editor**

为了辅助我们对ELF文件的二进制数据进行查看，我们可以借助010editor工具进行ELF文件分析。<br>
在010editor中使用ELF模板，即可对ELF文件进行结构解析。

[![](https://p5.ssl.qhimg.com/t019dac0437e222ec58.png)](https://p5.ssl.qhimg.com/t019dac0437e222ec58.png)

[![](https://p1.ssl.qhimg.com/t015b2221290b8e7235.png)](https://p1.ssl.qhimg.com/t015b2221290b8e7235.png)

<a class="reference-link" name="%EF%BC%882%EF%BC%89ELF%E6%96%87%E4%BB%B6%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84"></a>**（2）ELF文件数据结构**

通过查看ELF.h文件可以找到ELF文件的数据结构信息，在ELF.h文件中，数据类型主要有以下几种：

[![](https://p5.ssl.qhimg.com/t015fd585da902560dd.png)](https://p5.ssl.qhimg.com/t015fd585da902560dd.png)

ELF目标文件格式的最前部是ELF文件头，它定义了ELF魔数、文件机器字节长度、数据存储方式、版本、运行平台、ABI版本、ELF重定位类型、硬件平台、硬件平台版本、入口地址、程序头入口和长度、段表的位置和长度、段的数量。<br>
数据结构如下：

[![](https://p3.ssl.qhimg.com/t0189d9bb8e72e1a822.png)](https://p3.ssl.qhimg.com/t0189d9bb8e72e1a822.png)

[![](https://p0.ssl.qhimg.com/t0118c4ab68132e90d5.png)](https://p0.ssl.qhimg.com/t0118c4ab68132e90d5.png)

[![](https://p3.ssl.qhimg.com/t0188bff487e12e051c.png)](https://p3.ssl.qhimg.com/t0188bff487e12e051c.png)

ELF程序头是对二进制文件中段的描述，是程序装载必需的一部分。段是在内核装载时被解析的，描述了磁盘上可执行文件的内存布局以及如何映射到内存中。<br>
程序头数据结构如下：

[![](https://p5.ssl.qhimg.com/t0123250e797014cc4e.png)](https://p5.ssl.qhimg.com/t0123250e797014cc4e.png)

[![](https://p1.ssl.qhimg.com/t01bb254d1aba120bb0.png)](https://p1.ssl.qhimg.com/t01bb254d1aba120bb0.png)

[![](https://p4.ssl.qhimg.com/t0109dd268f78213e3d.png)](https://p4.ssl.qhimg.com/t0109dd268f78213e3d.png)

段是程序执行的必要组成部分，在每个段中，会有代码或者数据被划分为不同的节。节头表是对这些节的位置和大小的描述，主要用于链接和调试。<br>
节头表数据结构如下：

[![](https://p5.ssl.qhimg.com/t0148f8129828d84dbb.png)](https://p5.ssl.qhimg.com/t0148f8129828d84dbb.png)

[![](https://p4.ssl.qhimg.com/t01499d362b9135fa3c.png)](https://p4.ssl.qhimg.com/t01499d362b9135fa3c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015213c7dddce6072d.png)

符号表保存了程序实现或使用的所有(全局)变量和函数（包含了程序的导入导出符号）。<br>
符号表数据结构如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0141ca4ccc9646cc54.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a8722f4055aebcc4.png)

[![](https://p5.ssl.qhimg.com/t01b586e3f2794ca006.png)](https://p5.ssl.qhimg.com/t01b586e3f2794ca006.png)

[![](https://p3.ssl.qhimg.com/t01597a30c63aeca089.png)](https://p3.ssl.qhimg.com/t01597a30c63aeca089.png)

[![](https://p0.ssl.qhimg.com/t016e803a71485d4336.png)](https://p0.ssl.qhimg.com/t016e803a71485d4336.png)

[![](https://p0.ssl.qhimg.com/t01e0b3653c678e9835.png)](https://p0.ssl.qhimg.com/t01e0b3653c678e9835.png)

ELF文件中还有很多节类型，例如：.text、.got、.plt等，这里暂不一一介绍，网络中有很多分析说明，大家可以自行研究。



## 四、Linux恶意程序分析方法

由于笔者只是对Linux恶意程序的分析方法进行梳理，因此，暂不使用真实样本进行分析对比；故在这里，我们生成一个正常的ELF文件，用于分析比较。

[![](https://p1.ssl.qhimg.com/t011f7b62ba8748c898.png)](https://p1.ssl.qhimg.com/t011f7b62ba8748c898.png)

[![](https://p0.ssl.qhimg.com/t010bdf4ad200589191.png)](https://p0.ssl.qhimg.com/t010bdf4ad200589191.png)

### <a class="reference-link" name="1%EF%BC%8E%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90"></a>1．静态分析

在分析Linux恶意程序前，我们需要尽可能多的掌握恶意代码的基本情况，才能便于我们选择合适的分析环境，采用适当的分析方法进行分析。<br>
在Linux系统中，提供了多种命令辅助我们对Linux恶意程序进行静态分析，例如：“file”、“readelf”、“ldd”、“strings”、“nm”、“objdump”、“hexdump”命令等。

<a class="reference-link" name="%EF%BC%881%EF%BC%89file%E5%91%BD%E4%BB%A4"></a>**（1）file命令**

在分析Linux样本前，首先需要辨识文件类型，可以通过“file”命令查看文件的类型（可执行文件？位数？链接方式？）。

[![](https://p4.ssl.qhimg.com/t01e7397f1c295d8e4b.png)](https://p4.ssl.qhimg.com/t01e7397f1c295d8e4b.png)

通过file命令，我们可以确定此文件是一个32位的ELF文件，由动态链接库链接而成。

<a class="reference-link" name="%EF%BC%882%EF%BC%89readelf%E5%91%BD%E4%BB%A4"></a>**（2）readelf命令**

除了使用“file”命令辨识文件类型，我们也可以使用“readelf”命令查看文件的详细格式信息（程序头表、节头表、符号表等）。<br>
备注：在Linux恶意程序分析过程中，恶意程序可能会没有节头表，因为节头对于程序的执行来说不是必需的，没有节头表，恶意程序仍可以运行。

<a class="reference-link" name="%EF%BC%883%EF%BC%89ldd%E5%91%BD%E4%BB%A4"></a>**（3）ldd命令**

“ldd”命令可以用来查看程序运行所需的共享库,常用来解决程序因缺少某个库文件而不能运行的一些问题。<br>
备注：恶意程序可通过静态编译的方式解决对共享库的依赖，例如：路由器或防火墙中运行的恶意代码。

[![](https://p1.ssl.qhimg.com/t0192647b12ca37c2a7.png)](https://p1.ssl.qhimg.com/t0192647b12ca37c2a7.png)

### <a class="reference-link" name="%EF%BC%884%EF%BC%89strings%E5%91%BD%E4%BB%A4"></a>（4）strings命令

通过“strings”命令可以查看Linux样本中的所有字符串：

[![](https://p3.ssl.qhimg.com/t01c0c7017a101f3001.png)](https://p3.ssl.qhimg.com/t01c0c7017a101f3001.png)

/lib/ld-linux.so.2<br>
libc.so.6<br><em>IO<em>stdin<em>used<br>
puts<br>**libc_start_main<br>**gmon_start</em></em><br>
GLIBC_2.0<br>
PTRh<br>
UWVS<br>
t$,U<br>
[^</em>]<br>
hello world!<br>
;*2$”(<br>
GCC: (Ubuntu 5.4.0-6ubuntu1~16.04.11) 5.4.0 20160609<br>
crtstuff.c<br>**JCR_LIST**<br>
deregister<em>tm<em>clones<br><strong>do_global_dtors_aux<br>
completed.7209<br></strong>do<em>global<em>dtors<em>aux_fini_array_entry<br>
frame_dummy<br><strong>frame_dummy_init_array_entry<br>
helloworld.c<br></strong>FRAME_END</em></em><br>
__JCR_END</em></em><br><strong>init_array_end<br>
_DYNAMIC<br></strong>init_array_start<br>
__GNU_EH_FRAME_HDR<br>
_GLOBAL_OFFSET_TABLE</em><br><strong>libc_csu_fini<br>
_ITM_deregisterTMCloneTable<br></strong>x86.get<em>pc<em>thunk.bx<br><em>edata<br><strong>data_start<br>
puts@[@GLIBC_2](https://github.com/GLIBC_2).0<br></strong>gmon**start**</em><br><strong>dso_handle<br>
_IO_stdin_used<br></strong>libc_start_main@[@GLIBC_2](https://github.com/GLIBC_2).0<br><strong>libc_csu_init<br>
_fp_hw<br></strong>bss_start<br>
main<br>
_Jv_RegisterClasses<br>
__TMC_END</em></em><br>
_ITM_registerTMCloneTable<br>
.symtab<br>
.strtab<br>
.shstrtab<br>
.interp<br>
.note.ABI-tag<br>
.note.gnu.build-id<br>
.gnu.hash<br>
.dynsym<br>
.dynstr<br>
.gnu.version<br>
.gnu.version_r<br>
.rel.dyn<br>
.rel.plt<br>
.init<br>
.plt.got<br>
.text<br>
.fini<br>
.rodata<br>
.eh_frame_hdr<br>
.eh_frame<br>
.init_array<br>
.fini_array<br>
.jcr<br>
.dynamic<br>
.got.plt<br>
.data<br>
.bss<br>
.comment

前两行显示了Linux样本使用的库，中间部分可以看到编译器信息为GCC，后面部分为程序各部分的名称。

<a class="reference-link" name="%EF%BC%885%EF%BC%89nm%E5%91%BD%E4%BB%A4"></a>**（5）nm命令**

“nm”命令可以用来列出目标文件的符号清单（.dynsym节、.symtab节）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0159d4ec43b71ecb66.png)

<a class="reference-link" name="%EF%BC%886%EF%BC%89objdump%E5%B7%A5%E5%85%B7"></a>**（6）objdump工具**

分析Linux样本的反汇编代码，最常见的分析工具是IDA，如果Linux样本代码比较简单，也可以使用“objdump”工具：

[![](https://p0.ssl.qhimg.com/t01b412300ed919e323.png)](https://p0.ssl.qhimg.com/t01b412300ed919e323.png)

[![](https://p5.ssl.qhimg.com/t01ea4e03bbd43bb840.png)](https://p5.ssl.qhimg.com/t01ea4e03bbd43bb840.png)

<a class="reference-link" name="%EF%BC%887%EF%BC%89hexdump%E5%B7%A5%E5%85%B7"></a>**（7）hexdump工具**

查看Linux样本的16进制数据，可以使用“hexdump”工具：

[![](https://p3.ssl.qhimg.com/t01adee41672529bce8.png)](https://p3.ssl.qhimg.com/t01adee41672529bce8.png)

[![](https://p5.ssl.qhimg.com/t016b682bea6b62533f.png)](https://p5.ssl.qhimg.com/t016b682bea6b62533f.png)

### <a class="reference-link" name="2%EF%BC%8E%E5%8A%A8%E6%80%81%E5%88%86%E6%9E%90"></a>2．动态分析

Linux平台提供了多种工具支持对Linux样本进行动态分析，我们可以通过调用ltrace和strace对程序调用进行监控；ltrace能够跟踪进程的库函数调用，它会显现出哪个库函数被调用，而strace则是跟踪程序的每个系统调用。

<a class="reference-link" name="%EF%BC%881%EF%BC%89ltrace"></a>**（1）ltrace**

用ltrace跟踪Linux样本，如下：

[![](https://p2.ssl.qhimg.com/t0144dc2442cc964137.png)](https://p2.ssl.qhimg.com/t0144dc2442cc964137.png)

我们看到程序调用了puts库函数做了输出，同时0x804840b即是反汇编代码中对应函数地址；

[![](https://p1.ssl.qhimg.com/t012530751a2142b6b2.png)](https://p1.ssl.qhimg.com/t012530751a2142b6b2.png)

<a class="reference-link" name="%EF%BC%882%EF%BC%89strace"></a>**（2）strace**

用strace跟踪Linux样本，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011149c34848fb2e2d.png)

我们看到程序调用write()系统调用做了输出，同时strace还把程序运行时所做的系统调用都打印出来了。

<a class="reference-link" name="%EF%BC%883%EF%BC%89ftrace"></a>**（3）ftrace**

除了ltrace和strace，我们还可以使用基于ptrace编写的相关分析工具，例如：ftrace工具；（[https://github.com/elfmaster/ftrace）](https://github.com/elfmaster/ftrace%EF%BC%89)

[![](https://p2.ssl.qhimg.com/t01296983ede4fc8715.png)](https://p2.ssl.qhimg.com/t01296983ede4fc8715.png)

### <a class="reference-link" name="3%EF%BC%8E%E5%8A%A8%E6%80%81%E8%B0%83%E8%AF%95"></a>3．动态调试

<a class="reference-link" name="%EF%BC%881%EF%BC%89GDB"></a>**（1）GDB**

在Linux中调试样本，最常见的调试方法就是使用GDB进行调试，GDB调试可以分为两种情况：<br>
a.调试有调试信息的程序；（使用gcc编译加-g选项）<br>
b.调试没有调试信息的程序；（针对Linux恶意程序的分析，基本都是采用没有调试信息的调试方式。）<br>
有调试信息的程序，如下：

[![](https://p5.ssl.qhimg.com/t01a2b52f428982414f.png)](https://p5.ssl.qhimg.com/t01a2b52f428982414f.png)

[![](https://p0.ssl.qhimg.com/t012241690127899712.png)](https://p0.ssl.qhimg.com/t012241690127899712.png)

无调试信息的程序，如下：

[![](https://p3.ssl.qhimg.com/t01cea431da2d02349e.png)](https://p3.ssl.qhimg.com/t01cea431da2d02349e.png)

[![](https://p1.ssl.qhimg.com/t01cca8e2d93bd5e9ff.png)](https://p1.ssl.qhimg.com/t01cca8e2d93bd5e9ff.png)

在对无调试信息的Linux样本进行分析时，我们首先需要将反汇编语法设置为intel，因为GDB的默认汇编语法是AT&amp;T格式，使用起来可能会有点不习惯；<br>
语法如下：<br>
set disassembly-flavor intel：将汇编指令格式设置为intel格式

[![](https://p3.ssl.qhimg.com/t01973c4dcde58e8421.png)](https://p3.ssl.qhimg.com/t01973c4dcde58e8421.png)

针对部分Linux样本在运行过程中，会执行fork系统调用，我们还可以通过设置follow-fork-mode允许我们选择程序在执行fork系统调用后是继续调试父进程还是调试子进程。其语法如下：<br>
set follow-fork-mode parent：程序执行fork系统调用后调试父进程<br>
set follow-fork-mode child：程序执行fork系统调用后调试子进程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c3b65e45300334e7.png)

在进入正式调试前，我们可以使用“disass”命令查看指定功能的反汇编：

[![](https://p5.ssl.qhimg.com/t01e4def9ff59be2960.png)](https://p5.ssl.qhimg.com/t01e4def9ff59be2960.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fdc39477cb16d7f5.png)

然后通过“b main”、“r”、“display /i $pc”命令运行被调试的程序：<br>
b main：在main函数处下断点；<br>
r：运行被调试的程序；<br>
display /i $pc：每次程序中断后可以看到即将被执行的下一条汇编指令；

[![](https://p2.ssl.qhimg.com/t0159078718742f66af.png)](https://p2.ssl.qhimg.com/t0159078718742f66af.png)

在调试过程中，通过执行“i r”命令获取寄存器信息：

[![](https://p3.ssl.qhimg.com/t01aff3d15975ee07d6.png)](https://p3.ssl.qhimg.com/t01aff3d15975ee07d6.png)

在调试过程中，通过执行“si”、“ni”命令进行调试：<br>
si：相当于其它调试器中的“Step Into (单步跟踪进入)”；<br>
ni：相当于其它调试器中的“Step Over (单步跟踪)”<br>
在进入函数前，可以通过“x /10xw $esp”命令查看寄存器信息：

[![](https://p2.ssl.qhimg.com/t017b8e8cac460ca980.png)](https://p2.ssl.qhimg.com/t017b8e8cac460ca980.png)

GDB调试Linux木马常见命令如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b6bee073c679716a.png)

<a class="reference-link" name="%EF%BC%882%EF%BC%89IDA%E8%BF%9C%E7%A8%8B%E8%B0%83%E8%AF%95"></a>**（2）IDA远程调试**

除了使用GDB进行Linux样本调试外，我们还可以使用IDA远程调试对Linux样本进行分析。使用IDA远程调试比使用GDB调试更方便，分析效率更高，但还是有一些局限性，例如：<br>
对具有fork调用的Linux样本，无法设置后续调试模式；<br>
若调试指令运行过快，有时会导致数据通信出错，随即会导致调试流程出错；<br>
IDA远程调试很简单，网上也有很多教程资料，因此这里就简单描述一下步骤即可：<br>
1．用IDA打开Linux样本；<br>
2．在IDA的安装路径（IDA 7.0\dbgsrv\）里找到linux_server或linux_server64，并在Linux环境中运行；<br>
3．在IDA中，选择菜单栏&gt;Debugger&gt;Select a debugger(或者是switch debugger)&gt;选择Remote linux debugger&gt;ok；<br>
4．设置各种参数(调试文件路径，远程Linux虚拟机的ip地址及端口)<br>
5．在IDA中下断点；<br>
6．在IDA中开始调试；



## 五、linux内核分析

GDB调试和IDA远程调试方法只适用于用户态调试，如果需要调试内核数据，则需要寻求专门的内核调试方法。<br>
使用IDA+Vmware进行内核调试是目前我觉得最方便的分析方法；因此在这里以redhat5.5_i386_2.6.18主机作为案例进行简单演示操作。

[![](https://p0.ssl.qhimg.com/t01b4da8166f46f0f34.png)](https://p0.ssl.qhimg.com/t01b4da8166f46f0f34.png)

### <a class="reference-link" name="1%EF%BC%8E%E4%BF%AE%E6%94%B9vmx%E6%96%87%E4%BB%B6"></a>1．修改vmx文件

首先，将虚拟机关机，然后根据虚拟机的不同系统位数，在vmx文件末尾添加以下代码：<br>
32位：<br>
debugStub.listen.guest32 = “TRUE”<br>
debugStub.hideBreakpoints = “TRUE”<br>
debugStub.listen.guest32.remote = “TRUE”<br>
monitor.debugOnStartGuest64 = “TRUE”<br>
64位：<br>
debugStub.listen.guest64 = “TRUE”<br>
debugStub.hideBreakpoints = “TRUE”<br>
debugStub.listen.guest64.remote = “TRUE”<br>
monitor.debugOnStartGuest64 = “TRUE”

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01214e4f8cb807ebe4.png)

### <a class="reference-link" name="2%EF%BC%8E%E5%BC%80%E5%90%AF%E8%99%9A%E6%8B%9F%E6%9C%BA"></a>2．开启虚拟机

直接将虚拟机系统开机即可；

### <a class="reference-link" name="3%EF%BC%8EIDA%E8%BF%9E%E6%8E%A5"></a>3．IDA连接

如果是32位系统，则使用ida.exe，在IDA界面中点击：【Debugger】-&gt;【Attach】-&gt;【Remote GDB debugger】，连接localhost主机的8832端口。<br>
如果是64位系统，则使用ida64.exe，连接localhost主机的8864端口。<br>
32位系统：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017031c76e7b7bd6d9.png)

[![](https://p2.ssl.qhimg.com/t01813258645ca6822f.png)](https://p2.ssl.qhimg.com/t01813258645ca6822f.png)

[![](https://p4.ssl.qhimg.com/t017705edaff37a13b7.png)](https://p4.ssl.qhimg.com/t017705edaff37a13b7.png)

64位系统：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d918d48537553cc0.png)

### <a class="reference-link" name="4%EF%BC%8E%E7%94%A8%E6%88%B7%E6%80%81%E4%B8%8E%E5%86%85%E6%A0%B8%E6%80%81%E7%9A%84%E5%88%87%E6%8D%A2"></a>4．用户态与内核态的切换

IDA连接成功后，虚拟机系统将中断在内核地址中，此时即可对内核中的恶意程序进行断点调试。

[![](https://p2.ssl.qhimg.com/t01d3eed3380e08092e.png)](https://p2.ssl.qhimg.com/t01d3eed3380e08092e.png)

[![](https://p1.ssl.qhimg.com/t01d684a82a260ff228.png)](https://p1.ssl.qhimg.com/t01d684a82a260ff228.png)

若需要对恶意程序的用户态代码进行调试，只需在IDA中的以下两个按钮间进行切换即可：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d28686e7102b6c80.png)

[![](https://p5.ssl.qhimg.com/t01476a0f0e8bff96e7.png)](https://p5.ssl.qhimg.com/t01476a0f0e8bff96e7.png)

通过这种方法，我们即可实现对Linux恶意程序的用户态代码、内核态注入代码的全面分析。

### <a class="reference-link" name="5%EF%BC%8E%E6%9F%A5%E7%9C%8B%E5%86%85%E6%A0%B8%E4%BB%A3%E7%A0%81"></a>5．查看内核代码

在Linux系统中，/boot/System.map包含了整个内核的所有符号；内核地址是从0xC0000000开始的。

### <a class="reference-link" name="%EF%BC%881%EF%BC%89%E6%9F%A5%E7%9C%8BLinux%E7%B3%BB%E7%BB%9F%E8%B0%83%E7%94%A8%E8%A1%A8"></a>（1）查看Linux系统调用表

在Linux主机中，通过查看System.map文件，可以获取系统调用表地址：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014dcb77348869eb5a.png)

在IDA的Hex View界面中，可以查看Linux主机中系统调用表中的所有系统调用地址：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016bff4431cb5b972c.png)

### <a class="reference-link" name="%EF%BC%882%EF%BC%89%E6%9F%A5%E7%9C%8B%E7%B3%BB%E7%BB%9F%E8%B0%83%E7%94%A8%E5%87%BD%E6%95%B0%E4%BB%A3%E7%A0%81"></a>（2）查看系统调用函数代码

通过查看System.map文件，可以获取系统调用函数的地址，例如，sys_read函数的内核地址为0xc04765aa；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0120ef50590db469ba.png)

在IDA中，直接跳转至对应地址处即可查看sys_read函数的内核代码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016ce4f052c8fb9251.png)

### <a class="reference-link" name="%EF%BC%883%EF%BC%89HOOK"></a>（3）HOOK

病毒木马程序在执行过程中，可通过修改系统调用表中对应系统调用函数的函数地址，即可实现对系统调用函数的HOOK，例如：修改0xC06224F4处的数据。

[![](https://p5.ssl.qhimg.com/t013bd3f5ea1553abdc.png)](https://p5.ssl.qhimg.com/t013bd3f5ea1553abdc.png)



## 六、总结

在对Windows恶意样本进行分析的时候，有大量的成熟的界面化工具可以供我们使用；然而在对Linux恶意样本进行分析的时候，此类工具相对较少，并且大部分工具均是命令行操作，因此需要我们熟悉各种命令，才能提升我们的分析效率，达到事半功倍的效果。<br>
在这片文章中，笔者只是对Linux恶意样本的分析方法进行了简单的梳理，后续笔者还会对Linux恶意样本的病毒技术进行梳理，还望大家多多指教。
