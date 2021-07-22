> 原文链接: https://www.anquanke.com//post/id/84315 


# Xen攻击第一篇：XSA-105--从nobody到root


                                阅读量   
                                **100994**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

原链: [http://blog.quarkslab.com/xen-exploitation-part-1-xsa-105-from-nobody-to-root.html](http://blog.quarkslab.com/xen-exploitation-part-1-xsa-105-from-nobody-to-root.html)

**作者: Jeremie Boutoille**

**译者: Au2o3t/360云安全团队**

**审校: Terence/360云安全团队**

**本文介绍 Xen-105[1]CVE-2014-7155)的利用,介绍并演示在 Linux 4.4.5 上的完整利用开发。**

****

Xen作现代虚拟化平台的一个重要代表,它的安全性值得全世界黑客的关注。本文将在已经披露的编号为XSA-105(CVE-2014-7155)的Xen漏洞的基础上进行攻击尝试,尽管 Andrei Lutas 曾撰文描述过该漏洞的原理和触发方法[2][3][4],但我们并未发现任何该漏洞的公开利用。<br> 所以我们将在本文对该漏洞作详细的介绍并演示如何通过这个漏洞在 4.4.5 的Linux平台下进行完成的漏洞利用(该方法也可能工作在其它版本上),从nobody用户权限到root权限的华丽提升。

(视频见:https://asciinema.org/a/b1xnd4fyy4krquxvrppbttvff)

**[![](https://p3.ssl.qhimg.com/t0138cb7c8a3541416d.png)](https://p3.ssl.qhimg.com/t0138cb7c8a3541416d.png)**

**环境**

该漏洞所需的Xen版本至少需要要在3.2.x以上,这里我们选择 4.1.6.1 无补丁版。目前我们了解到该漏洞能在HVM模式客户机(HVM[5])上提权(普通用户到root用户)。

参照 Xen 术语,HVM客户机是基于如 Intel VT 或 AMD-V 虚拟化扩展的完全虚拟化。 另一种则是半虚拟化(PV)。运行在虚拟机管理器上的内核通常在启动时即检测到 Xen,并出于效率采用名为 PVOPS[6] 的半虚拟化扩展。由于 Linux 内核的默认编译选项启用了这个 PVOPS 扩展,所以我们要禁用这个选项,编译一个自定义的内核。

**<br>**

**Dom0**

Dom0[7][8]是由 Xen 启动加载的初始虚拟机。它是权限最大的客户机,其可以进行 Xen 管理。我们的Dom0选择 Debian 7.9.0。

一些编译依赖:

apt-get build-dep xen

接着,编译和安装:

make install -j4 &amp;&amp; update-grub

重启 Dom0,在 grub 中选择Xen模式启动。为使用 xl 命令,必须调整链接路径。且 xencommons 服务必须启动:

echo "/usr/lib64" &gt;&gt; /etc/ld.so.conf

insserv xencommons

service xencommons start

**<br>**

**DomU**

第二步需要创建一个 HVM 客户机。因 PVOPS 扩展是默认启用的,大多数 Linux 发行版其实上是PV模式的。我们选择用Archlinux [9]安装为 HVM 客户机。在编译选项中禁用 PVOPS:“Processor type and features -&gt; Linux guest support (CONFIG_HYPERVISOR_GUEST=n)”。



[![](https://p0.ssl.qhimg.com/t01029c323540fe6134.png)](https://p0.ssl.qhimg.com/t01029c323540fe6134.png)



加载 HVM DomU 的 xl 配置文件比较简单。为了能够成功进行漏洞利用,我们的HVM虚拟机设置为包含2个(或以上)CPU。为便于演示,在我们的例子里,客户机由一个直接在物理机中创建的 qcow 格式镜像加载。其网络接口选择与虚拟机管理器网络桥接,这样我们可以通过 SSH 连接我们的客户机。配置文件如下:

kernel = '/usr/lib/xen/boot/hvmloader'

builder='hvm'

memory = 1024

name = 'hvm_arch'

vcpus = 2

vif = ['bridge=xenbr0']

disk = ['tap:qcow:/root/VM2.img.qcow,xvda,w']

device_model_version = 'qemu-xen-traditional'

sdl=0

serial='pty'

vnc=1

vnclisten="0.0.0.0"

vncpasswd=""

****<br>****

****XSA-105********

****描述****

**该漏洞位于对 hlt****,lgdt****,lidt ****和 lmsw ****指令的仿真[1]****:**

**问题描述**

**对 HLT****,LGDT****,LIDT ****和 LMSW ****指令的仿真未能正确执行特权模式权限检查。**

**然而,这些指令通常不由模拟器处理。 **

**除非:**

**– ****这些指令的内存操作数(若有)存在于(仿真的或通过模式的)内存映射的 IO ****空间,**

**– ****客户机运行在32****位PAE****模式下,当此指令(在执行流中)在四个指令中且其中一个指令是做页表更新操作的,**

**– ****当客户机发出无效操作码异常,且其(可能恶意的)修改此指令为受影响的指令之一。**

**恶意的客户机用户模式代码可能利用该漏洞来安装自己的中断描述符表(IDT****)。**

我们从上文得知两点:

·对 HLT,LGDT,LIDT 和 LMSW 指令的仿真未能正确执行特权模式权限检查。因此,一个非特权代码(3环)可能运行这些指令。

·这些指令通常不被模拟,这意味着我们必须找到一种方法来模拟它们。第三个条件似乎是最容易实现的,这也是 Andrei Lutas[2] 所采用的解决方案。

Andrei Lutas 已经在他的论文[2]中提供了一份出色的漏洞代码讲解,需要的话,一定要读他的论文。

**<br>**

**利用**

在存在漏洞的这几个指令中,只有两个可能导致潜在的提权:lgdt 和 lidt。它们分别允许改变全局描述符表寄存器(GDTR)和中断描述符表寄存器的值(IDRT)。GDTR 和 IDTR 格式相同:高位包含基址,低位定义长度[10]。这些值定义全局描述符表(GDT)和中断描述符表(IDT)地址。



[![](https://p3.ssl.qhimg.com/t0109d72404fcc95480.png)](https://p3.ssl.qhimg.com/t0109d72404fcc95480.png)



根据Intel 手册,不允许非特权代码执行这些指令(lgdt,lidt)。若用户可以加载自己的 GDT 或 IDT,将导致任意代码执行和特权提升。见下文。

**<br>**

**中断描述符表(****IDT****)**

IDT 是 x86中的 中断向量表[10],它是一个基本的表,它将一个中断号与一个中断处理程序关联起来。由条目号决定中断号,且每个条目都包含一些字段如:类型、段选择器、偏移量、特权等级等。中断处理程序地址是通过段基址(由段选择器决定)和偏移量相加得来的。



[![](https://p1.ssl.qhimg.com/t01873cd71641ca298d.png)](https://p1.ssl.qhimg.com/t01873cd71641ca298d.png)



若用户可以加载自己的 IDT,那么他就可以指定一个恶意的条目,使用内核代码段选择器将一个中断连接到他自己的处理程序。为避免稳定性问题,中断必须转发到原来的中断处理程序处。因为处理程序运行在内核空间,这是可以做到的,它可以从原 IDT 处读取条目。使用 sidt 指令前必须预先保存原 IDT,因为必须在返回用户空间前恢复它。但是,我们并没有测试它。

Andrei Lutas 采用 IDT 的解决方案[2],我们选择采用GDT 方法。

**<br>**

**全局描述符表(****GDT****)**

GDT 是用于定义内存段的。每一个条目包含:基址,限制,类型,权限描述符(DPL),读写位等等:



```
struct desc_struct `{`
        union `{`
                struct `{`
                        unsigned int a;
                        unsigned int b;
                `}`;
                struct `{`
                        unsigned short limit0;
                        unsigned short base0;
                        unsigned int base1: 8, type: 4, s: 1, dpl: 2, p: 1;
                        unsigned int limit: 4, avl: 1, l: 1, d: 1, g: 1, base2: 8;
                `}`;
        `}`;
`}` __attribute__((packed));
```

如今,平坦模型是最为常用的内存分段模式。每个描述符以不同的权限和标志映射整个内存(所有的安全检查以分页进行)。

大多数情况下,至少有6个 GDT 条目:

·32-bit 内核代码段 (dpl = 0)

·64-bit 内核代码段 (dpl = 0)

·内核数据段 (dpl = 0)

·32-bit 用户代码段 (dpl = 3)

·64-bit 用户代码段 (dpl = 3)

·用户数据段 (dpl = 3)

当前内存段由段寄存器指定。常见的段选择寄存器包括代码选择器,堆栈选择器,数据选择器等。每个段选择器有16位长。第3到15位作为 GDT 索引,第2位表示是 LDT还是GDT 选择器,第0和1位表示请求权限(RPL)。



[![](https://p4.ssl.qhimg.com/t0167bf8ac9a910b6d2.png)](https://p4.ssl.qhimg.com/t0167bf8ac9a910b6d2.png)





[![](https://p5.ssl.qhimg.com/t010f8f27cc44da4822.png)](https://p5.ssl.qhimg.com/t010f8f27cc44da4822.png)



我们的实验中还有另一种非常有趣的条目:调用门。调用门的目的是为了协助不同权限级之间的转移。这种条目是内存描述符的两倍大(64位模式下)且另有其它字段:

·一个段选择器

·偏移量

·权限描述符(DPL)



[![](https://p5.ssl.qhimg.com/t01783442d2ab504542.png)](https://p5.ssl.qhimg.com/t01783442d2ab504542.png)



要访问一个调用门,用户必须执行一个远程调用。此远程调用必须指定调用选择器。这个选择器与其它选择器具有相同的格式(GDT中的索引,LDT 或 GDT 选择器,段请求权限)。

 CPU 根据调用门条目中指定的段选择器得到段基址,加上调用门偏移,达到程序入口点。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016f266793d4a96762.png)



当然,这里也有一些权限检查,涉及4个权限级:

·当前权限级(CPL)

·远程调用选择器中的请求权限级(RPL)

·调用门描述符权限级(CDPL)

·段描述符权限级(SDPL)

必须满足三个条件:

·CPL &lt;= CDPL

·RPL &lt;= CDPL

·SDPL &lt;= CPL

满足这些条件,调用门程序才会执行。我们需用创建一个DPL=3的调用门,段选择器指向内核代码段,以及一段提权代码。那么:

·CPL = 3

·RPL = 0

·CDPL = 3

·SDPL = 0

·CPL &lt;= CDPL == True

·RPL &lt;= CDPL == True

·SDPL &lt;= CPL == True

整合起来

利用过程:

1. 构造一个GDT,使用平坦分割模型,包含一个 DPL=3 的调用门。

2. 保存当前的 GDTR 。

3. 创建2个互相等待的线程(仅用于同步)。

4. 第一个线程执行一个 ud2 指令,同时第二个线程以 lgdt [rbx] 指令修补 ud2 指令(详情见 Andrei Lutas 的论文[2])。

5. 如果我们不是太慢,lgdt [rbx] 指令的仿真应该发生了。

6. 远程调用

7. #



[![](https://p4.ssl.qhimg.com/t01333c799596a7d150.png)](https://p4.ssl.qhimg.com/t01333c799596a7d150.png)



远程调用程序首先重新加载原来的 GDTR ;然后执行commit_creds(prepare_kernel_cred(0));,这个函数在调用任何内核函数和返回用户空间之前必须调用一个 swapgs ;以 retf 指令退出。

<br>

**演示和利用见,**

演示:[https://asciinema.org/a/b1xnd4fyy4krquxvrppbttvff](https://asciinema.org/a/b1xnd4fyy4krquxvrppbttvff)

利用:[http://blog.quarkslab.com/resources/2016-05-25_xsa-105/code/xsa105_exploit.tar.gz](http://blog.quarkslab.com/resources/2016-05-25_xsa-105/code/xsa105_exploit.tar.gz)

<br>

**结论**

此漏洞能造成具有多CPU 的HVM客户机的提权。我们利用调用门机制来实现任意代码执行,而 Andrei Lutas 则是利用中断处理程序。这只是个 PoC,需要满足一定的前提条件。因为调用门处理程序在用户内存空间,guest 中不能开启 SMEP。利用代码通过调用

commit_creds(prepare_kernel_cred(0))获取根权限,如果设置了 kptr_restrict,我们将无法通过 /proc/kallsyms 获取函数地址。

这是我第一次进行Xen的漏洞分析,这是非常有趣的,我鼓励任何有兴趣的人做同样的事:查看一个漏洞公告,并且写出利用,把它拿去赚钱或者公开 😉

之后的博文将谈论从客户机到宿主机的逃逸及利用过程,敬请关注!

[1]    (1, 2) [http://xenbits.xen.org/xsa/advisory-105.html](http://xenbits.xen.org/xsa/advisory-105.html)

[2]    (1, 2, 3, 4, 5, 6) [https://labs.bitdefender.com/wp-content/uploads/downloads/2014/10/Gaining-kernel-privileges-using-the-Xen-emulator.pdf](https://labs.bitdefender.com/wp-content/uploads/downloads/2014/10/Gaining-kernel-privileges-using-the-Xen-emulator.pdf)

[3]    [https://www.cert-ro.eu/files/doc/896_20141104131145076318500_X.pdf](https://www.cert-ro.eu/files/doc/896_20141104131145076318500_X.pdf)

[4]    [https://labs.bitdefender.com/2014/10/from-ring3-to-ring0-xen-emulator-flaws/](https://labs.bitdefender.com/2014/10/from-ring3-to-ring0-xen-emulator-flaws/)

[5]    [http://wiki.xen.org/wiki/Xen_Project_Software_Overview#Guest_Types](http://wiki.xen.org/wiki/Xen_Project_Software_Overview#Guest_Types)

[6]    [http://wiki.xenproject.org/wiki/XenParavirtOps](http://wiki.xenproject.org/wiki/XenParavirtOps)

[7]    [http://wiki.xen.org/wiki/Dom0](http://wiki.xen.org/wiki/Dom0)

[8]    [http://wiki.xen.org/wiki/Dom0_Kernels_for_Xen](http://wiki.xen.org/wiki/Dom0_Kernels_for_Xen)

[9]    [https://wiki.archlinux.org/index.php/installation_guide](https://wiki.archlinux.org/index.php/installation_guide)

[10]  (1, 2) [http://download.intel.com/design/processor/manuals/253668.pdf](http://download.intel.com/design/processor/manuals/253668.pdf)
