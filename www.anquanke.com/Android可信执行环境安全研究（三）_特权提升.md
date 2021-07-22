> 原文链接: https://www.anquanke.com//post/id/239181 


# Android可信执行环境安全研究（三）：特权提升


                                阅读量   
                                **92926**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者riscure，文章来源：riscure.com
                                <br>原文地址：[https://www.riscure.com/blog/samsung-investigation-part3﻿](https://www.riscure.com/blog/samsung-investigation-part3%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01098fe9eecf1113ec.jpg)](https://p4.ssl.qhimg.com/t01098fe9eecf1113ec.jpg)



## 0x00 概述

在前两篇系列文章中，我们首先介绍了三星的TEE OS TEEGRIS，然后介绍了如何针对可信应用程序（TA）实现漏洞利用并获得运行时控制权。

在最后一篇文章中，我们将进一步研究如何获得对TEE内核的运行时控制。我们将展示内核是如何公开可被特权TA使用的驱动程序，以将物理内存映射到TA内存空间。我们将利用HDCP TA中的驱动程序来映射安全寄存器，并取消TEE内存的保护机制。最后，我们将使用相同的HDCP TA来修改管理程序（Hypervisor）页表，并允许Android应用程序通过完全的读/写访问权限来映射（已经不受保护的）TEE内存。



## 0x01 寻找漏洞

此前，将物理内存直接映射到TA的功能一直是TEE漏洞利用中经常被用到的漏洞。对于S7机型来说，其中存在的问题是内核没有对要映射到TA中的物理内存区域执行足够的检查，从而允许将诸如EL3代码这样的敏感位置映射到TA内存中。

对于我们来说，深入研究TEEGRIS的实现方式，并检查是否存在类似漏洞是非常有意义的。我们很快就找到了一个在内存中运行的驱动程序，可以通过`phys://`访问。

`pays`处理程序注册：

[![](https://p3.ssl.qhimg.com/t019cb7af9eebc91d27.png)](https://p3.ssl.qhimg.com/t019cb7af9eebc91d27.png)

`phys`驱动程序与`/dev/mem`Linux设备非常相似，可以通过一些系统调用来访问，其中最值得关注的是`open`和`mmap`。`phys://`的`open`系统调用处理程序会执行以下操作。

`open`系统调用处理程序中的TA权限检查：

[![](https://p1.ssl.qhimg.com/t0177efae0812e88f73.png)](https://p1.ssl.qhimg.com/t0177efae0812e88f73.png)

在第9-13行，代码会检查TA是否有权映射五个潜在区域中的至少一个，分别是内部RAM、内部引导ROM、安全DRAM、非安全DRAM和寄存器。如果有权限，则会成功执行。

在第一篇文章中，我们知道权限是静态分配给每个组的。幸运的是，我们可以实现运行时控制的HDCP TA是属于高特权的`samsung_drv`组，这个组可以访问`phys`驱动程序。实际上，TA需要`phys`驱动程序来执行其中的一个命令，因此HDCT TA自然就属于`samsung_drv`组。

既然我们知道TA可以访问该应用程序，那么接下来可以分析mmap处理程序，并查看进行了哪些检查。

`phys mmap`处理程序：

[![](https://p5.ssl.qhimg.com/t016949d42650bfa74c.png)](https://p5.ssl.qhimg.com/t016949d42650bfa74c.png)

在第16行，调用了函数`get_memory_type`，会将提供的范围作为参数传递。随后，会将值`1`左移`get_memory_type`函数的返回值。在其余的代码中，我们看到函数会检查结果是否为8（对应非安全RAM，在图中以绿色表示）、16（对应寄存器，在图中以红色表示）、1（对应ROM，在图中以蓝色表示）。看来安全RAM和内部RAM（运行EL3代码）从不会映射到TA中，尽管它们都在TA可以拥有的权限列表之中。

我们在这里不过于详细地讨论`get_memory_type`函数。由于`samsung_drv`组没有映射ROM的权限，因此似乎只能在HDCP TA中映射非安全的RAM和寄存器。在这两个区域中，我们不太关注非安全RAM，REE中的特权提升可能会滥用它。我们对TEE更感兴趣，因为它完全位于安全RAM之中。而站在攻击者的角度，可能会更加关注寄存器，因为其中包含用于配置外围设备的所有寄存器，包括用于配置TrustZone的寄存器。

现在我们知道了要访问的内容，就可以创建一个面向返回编程（Return Oriented Programming）的Payload，从而允许映射和访问这些内存区域。为此，我们选择创建一个通用的物理内存到物理内存副本的Payload，具体执行以下操作：

（1）打开`phys`驱动程序的句柄；<br>
（2）调用`mmap`两次，映射源缓冲区和目标缓冲区；<br>
（3）跳到`memcpy`。

利用上述原语，我们可以选择将`memcpy`源设置为寄存器内存，将目标设置为非安全内存，来读取寄存器；或者也可以将`memcpy`源设置为非安全内存，将目标设置为寄存器，从而在Android应用中对其实现修改。

在实现ROP Payload之后，我们就要考虑要复制什么内容，以及在哪里复制。



## 0x02 ION缓冲区

第一步，我们必须找到一种方法，能让Android上运行的CA和TEE上运行的存在漏洞的HDCP TA之间共享物理内存。这个过程并不简单，因为通常情况下，常规的Android应用程序不知道缓冲区映射到的物理地址。

为此，我们使用了Android提供的ION机制，这个机制可以理解为一种共享内存管理器，在两个实体之间共享数据时删除内存中的副本。我们可以在Android应用程序访问这些缓冲区，因此就可以在客户端应用程序中使用它们。分配器将保证将内存映射到已知的物理地址。可以通过与`/dev/ion`进行交互来访问这个子系统，这个子系统允许执行`open`调用以获取文件描述符，然后通过ioctl请求ION缓冲区。

我们下载了与三星某设备固件版本相匹配的Android源代码，并通过查看设备树源码（Device Tree Sources）找到了一个符合要求的ION缓冲区。以下名为`exynos9820-beyond0lte_common.dtsi`的文件片段包含有关这个缓冲区的一些详细信息，例如起始地址（0x99000000）和大小（0xE400000）：

```
camera `{`
compatible = "exynos9820-ion";
ion,heapname = "camera_heap";
reg = &lt;0x0 0x99000000 0xE400000&gt;;
ion,recyclable;
`}`;
```

这意味着，如果我们在CA中映射整个`camera_heap ION`缓冲区，并在HDCP TA中映射物理地址0x99000000，那么我们应该拥有同一内存的两个视图。



## 0x03 修改TZASC

解决了这个问题之后，我们还剩下的唯一一个问题就是找到要映射的寄存器和将其映射到的位置。在第一批文章中，我们提到了两个通常用于配置TrustZone的寄存器：`TZASC`和`TZPC`。如果TA可以访问其中的任何一个，就可以读取寄存器的内容，同时也可以对其写入，从而取消对内存区域或外围设备的保护。原则上，修改二者中的任何一个都可以允许REE访问TEE，最终影响了TEE原本的安全性。但是，根据我们的经验，针对`TZASC`进行操作会更加容易，因为`TZPC`的结构往往取决于设备（当前没有公开发布的S10 Exynos芯片的相关文档），但`TZASC`已经在一定程度实现了标准化。

通过对TEEGRIS内核代码进行逆向，我们发现了与`TZASC`处理相关的函数，并从中发现这个SoC实际上有4个`TZASC`外设，推测是每个DRAM控制器对应一个。

我们首先搜索字符串`tzasc`，然后查看TEE内核二进制文件中是否有匹配项。下图就是我们到达初始化函数的方式，这个函数为我们提供了TZASC处理程序的地址。

`TZASC`驱动程序初始化：

[![](https://p1.ssl.qhimg.com/t0107137d464d0aee53.png)](https://p1.ssl.qhimg.com/t0107137d464d0aee53.png)

可以使用ioctl系统调用来访问`dev://tzasc`设备，该设备最终会调用`tzasc_get_settings_for_range`。

反编译的`tzasc_get_settings_for_range`：

[![](https://p0.ssl.qhimg.com/t01237e0e3d11336abd.png)](https://p0.ssl.qhimg.com/t01237e0e3d11336abd.png)

尽管这个函数看上去与我们要实现的攻击并不太相关，但我们注意到其中引用了一个名为`tzasc_physical_addresses`的结构，其中包含我们怀疑是4种不同的TZASC外设的物理地址。

4个TZASC外设的物理地址：

[![](https://p4.ssl.qhimg.com/t012b0700e4f8c20c89.png)](https://p4.ssl.qhimg.com/t012b0700e4f8c20c89.png)

为了验证我们的假设，我们通过读取`/proc/iomem`将此信息与从Android收集的每个物理设备的物理内存映射相关联。这个验证背后的思路是，TEE的物理范围不应该与REE的物理范围重叠。下面的列表显示了REE `mcinfo`寄存器位置之间存在间隔，这就为TZASC寄存器留出了空间。需要注意的是，`TZASC`字符串是手动添加的，以便读取输出，它不在正常的`iomem`输出中。

```
beyond0:/data/local/tmp # cat /proc/iomem
…
1bc3004c-1bc3004f : /mcinfo@1BC300000
-----TZASC1:0x1BC40000-----
1bd3004c-1bd3004f : /mcinfo@1BC300000
-----TZASC2:0x1BD40000-----
1be3004c-1be3004f : /mcinfo@1BC300000
-----TZASC3:0x1BE40000-----
1bf3004c-1bf3004f : /mcinfo@1BC300000
-----TZASC4:0x1BF40000-----
```

在收集了所有必须的信息之后，我们最终就可以尝试漏洞利用是否有效。我们首先尝试读取`TZASC`的内容，可以按照以下步骤：

（1）找到一个Android应用程序，可以映射`camera_heap`缓冲区，并将其初始化为一个固定的已知值。<br>
（2）同时，进行HDCP TA漏洞利用，针对0x1BC40000（第一个`TZASC`的地址）到0x99000000（`camera_heap`的地址）之间的0x1000字节（`TZASC`寄存器大小），将物理内存转到物理内存副本。<br>
（3）在Android应用中，连续监视`camera_heap`。如果其内容更改，则证明TA漏洞利用成功。<br>
（4）将缓冲区内容保存到文件中，以供进一步分析。

实际上，在几秒钟后，执行完成，并且将`TZASC`的转储保存到文件中。随后，我们使用十六进制编辑器对转储的内容进行分析。

`TZASC`范围内的转储：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0118edab419ba670c1.png)

在系统中四个`TZASC`控制器的配置非常相似，这里我们仅举例分析一个。上图中绿色标出的代表区域0，这是我们在第一篇文章中说明的默认基础区域（0x0000000000000000-0x000000fffffff000）。紫色表示的是系统在特定时间配置的所有安全范围。每个安全范围包含两个8字节（低字节序），接下来是该属性的另外16个字节。最后，红色标出的区域是安全范围的开始和结束地址，这是TEE OS的范围（0x00000000bab00000- 0x00000000bffff000）。这也与`/proc/iomem`提供的信息相匹配：

```
80000000-baafffff : System RAM
80090000-8197ffff : Kernel code
82380000-831b0fff : Kernel data
c0000000-dfffffff : System RAM
```

可以看出，由于REE无法访问该内存，因此TEE区域留有间隔。

接下来，我们微调漏洞利用代码，以实现覆盖4个TZASC，而不再仅仅是读取。我们可以使用相同的物理ROP Payload，但是可以将源地址和目标地址交换过来。我们以TEE OS安全范围的起始地址为目标，将其设置为大于结束地址的值。这样一来，范围就无效了，将会被忽略，并且整个TEE内存都会被配置为非安全的。



## 0x04 访问TEE内存

至此，我们就有了一个正在运行的系统，其中所有的TEE内存都是非安全的，可以被REE访问。这给我们提供了最后的阻碍——如何访问该内存？

如前所述，HDCP TA无法访问它，因为`phys`驱动程序会拒绝对安全内存的访问（即使现在将范围重新配置为安全）。因此，必须从Android应用程序来访问。但是，在正常情况下，Linux内核将允许映射这一范围，因为它是为TEE保留的。因此，在我们的漏洞利用过程中，该TA仍然可以访问整个非安全内存。这样一来，就找到了解决问题的思路。

可能有几种不同的思路，最后我们决定利用三星的管理程序RKP来实现。关于ARMv8-A特权级别的介绍，请参考第一篇文章。三星官方提供了下图，用以说明其实现的安全功能。

RKP只读页面保护：

[![](https://p4.ssl.qhimg.com/t01700f49454bd7a317.png)](https://p4.ssl.qhimg.com/t01700f49454bd7a317.png)

当ARMv8-A系统中存在管理程序时，会存在另一个阶段的转换表，其初衷是允许系统中具有多个guest操作系统。因此，攻击过程分为两个阶段。第一阶段是Linux内核执行，从虚拟地址转换为所谓的中间物理地址（IPA）。第二阶段是管理程序将IPA转换为最终的物理地址（PA）。

下图展示了两个阶段的内存转换过程：

[![](https://p5.ssl.qhimg.com/t015936460200b7a4c2.png)](https://p5.ssl.qhimg.com/t015936460200b7a4c2.png)

管理程序可以限制内存权限，这意味着，如果在第二阶段将某个页面映射为只读，那么即使该页面使用写权限映射，Linux内核也无法修改其内容。使用RKP，可以强制Linux内核内存中的某些安全相关结构只读，即使攻击者在内核上下文中执行了任意代码，也无法对其进行修改。

然后，我们的攻击思路是找到与`camera_heap ION`缓冲区对应的系统管理程序的转换表，并将其更改为指向TEE内核物理地址。请注意，可以通过修改Linux内核自身内的结构，从而忽略管理程序，并获得对TEE内存的访问权限。但是，与Linux内核相比，管理程序的复杂度要低很多，因此我们希望将管理程序作为目标。我们假设第二阶段页表将映射到固定的物理地址，并且永远不会修改，因此，我们就不需要解析复杂的结果来查找需要进行修改的确切内存位置。

为了确认我们的假设是否正确，我们必须在系统RAM中找到并提取管理程序内存。为了获得有关系统内存布局的信息，我们对`/proc/iomem`的信息进行了转储，在该信息中展示了三个主要的RAM范围。我们通过漏洞利用来转储每个范围区间的物理内存，然后搜索`RKP`之类的字符串。搜索结果显示，管理程序从第一个RAM范围的物理地址0x87000000开始。

第二项任务是在系统管理程序的内存中查找与`camera_heap ION`缓冲区相对应的页表条目。

原则上，我们可以对管理程序的二进制文件进行逆向，从而查找到TTBR寄存器是如何初始化和解析表的。但是，由于我们在运行时转储了管理程序的内存，因此我们决定对其进行检查，尝试能不能直接找到页表。找到页表的前提是我们熟悉其结构。ARM有一份关于ARMv8-A地址转换的文档，其中说明了转换表描述符针对块条目和表条目的格式。下图是块条目的格式。

块页表条目的格式：

[![](https://p1.ssl.qhimg.com/t01c6bf14a0ab3bab1f.png)](https://p1.ssl.qhimg.com/t01c6bf14a0ab3bab1f.png)

我们利用这一信息，在内存转储中找到了与下图所示的ION缓冲区相对应的块条目。

`camera_heap`缓冲区的块条目：

[![](https://p5.ssl.qhimg.com/t01f06ebc3e74464749.png)](https://p5.ssl.qhimg.com/t01f06ebc3e74464749.png)

上图标记出来的条目设置为0x990004FD（低字节序）。由于我们只想修改地址，因此可以忽略其中的属性，因此输出块地址就变成了0x99000000，对应`camera_heap`的地址。

最后一步是修改我们的Payload，以便将`camera_heap`的页表条目替换为TEE内核的条目。这样一来，当从REE访问`camera_heap`时，CA实际上访问的是TEE内存。为此，我们将安全范围增加2MB（每个块页表条目的大小），并保留了低字节以保存`camera_heap`设置的属性（即FD 04）。

这样一来，就能实现对安全范围的成功转储。在其中，我们发现了几个二进制文件，例如共享库、已加载的TA（包括用于漏洞利用的HDCP TA）以及TEE内核本身。现在，在我们的控制之下，可以使用页表将内存映射到REE中，因此页面的权限没有限制，这意味着所有内存（包括代码）都是可写的。所有修改都会反映在TEE具有相同内存的视图中。

总而言之，我们回顾一下，为了完全访问TEE内存，我们组合利用了许多漏洞：

（1）HDCP TA中缺少GP参数检查，导致我们可以在TA中进行任意读取/写入。<br>
（2）可以利用基于栈的缓冲区溢出来在TA上下文中获得任意代码执行。<br>
（3）Antirollback不适用于TA，这意味着三星即使正确修复了TA漏洞，我们仍然可以加载旧版本存在漏洞的TA。<br>
（4）基于组的权限分配机制粒度过大，实际上HDCP TA仅需要访问非安全内存，但权限设置后它仍然可以映射寄存器。<br>
（5）针对允许访问寄存器的TA，内核将允许映射例如`TZASC`和`TZPC`的寄存器。这些寄存器可能会完全破坏TrustZone技术提供的安全性，因此TA不应该有权限访问到它们。



## 0x05 总结

至此，我们就形成了完整的漏洞利用链。在这一阶段，我们成功将所有TEE内存映射到Android应用程序中。内存是完全可读和可写的，这意味着攻击者可以：

（1）修改TA和TEE内核的代码，因为权限控制不适用于Android应用程序。<br>
（2）在内核中实现KASLR、PAN和PXN的绕过。

一旦攻击者完全控制了TEE，就可以进一步实现各类攻击，例如修改TEE中实现的设备指纹或面部识别解锁功能，以绕过屏幕锁定。
