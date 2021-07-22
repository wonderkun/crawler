> 原文链接: https://www.anquanke.com//post/id/184944 


# 2019年Pwn2Own上用于攻破 VMware 的虚拟机逃逸漏洞分析


                                阅读量   
                                **436268**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者zerodayinitiative，文章来源：zerodayinitiative.com
                                <br>原文地址：[https://www.zerodayinitiative.com/blog/2019/5/7/taking-control-of-vmware-through-the-universal-host-controller-interface-part-1](https://www.zerodayinitiative.com/blog/2019/5/7/taking-control-of-vmware-through-the-universal-host-controller-interface-part-1)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01721a3c44d9ca2697.jpg)](https://p4.ssl.qhimg.com/t01721a3c44d9ca2697.jpg)



在今年的温哥华Pwn2Own比赛期间，Fluoroacetate团队展示了他们通过利用VMware Workstation从客户机虚拟机逃逸到物理机。他们利用虚拟USB 1.1 UHCI（通用主机控制器接口）中的越界读/写漏洞来达到此目的。

Fluoroacetate 通过此漏洞赢得了Pwn2Own温哥华的Pwn Smrter大奖，总奖金为340,000美元，还得到了一个全新的Tesla Model 3。他们为VMware编写了两个漏洞利用程序，都是针对通用主机控制器接口（UHCI）的。第一个是基于堆的溢出，另一个是一个条件竞争漏洞。这两个漏洞都需要guest虚拟机操作系统上的Admin权限才能利用成功。

在这篇分析中，我将介绍基于堆的缓冲区溢出漏洞，这是我最喜欢的Pwn2Own漏洞之一。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E6%8F%8F%E8%BF%B0"></a>漏洞描述

在处理发送到批量端点的特定UHCI请求时存在一个堆溢出漏洞，这些端点主要用于传输大量数据，这个漏洞也可用于触发一个越界写。

首先，当端点接收到用于处理的帧时，它会从相应的帧中提取传输描述符（TD），检查是否存在URB对象。如果不存在对象，则通过名为“NewUrb”的函数分配新的URB对象。

URB对象简述：英特尔UHCI规范提到的URB对象是USB中的一个请求块，研究发现，从`NewUrb`函数返回的对象是一个围绕有效规范USB请求块（URB）的包装器结构。检查TD的类型以及缓冲区大小后，如果TD类型是0xE1（USB_PID_OUT），那么TD缓冲区被复制到从中返回的对象内的缓冲区`NewUrb`函数。如果TD对象的类型不是0xE1，则它会传递缓冲区指针（在代码中引用`purb_data_cursor`）。

[![](https://p1.ssl.qhimg.com/t01fdd7cdd686c92903.png)](https://p1.ssl.qhimg.com/t01fdd7cdd686c92903.png)

触发漏洞并不难，只要创建一个TD对象，在token属性中设置正确的长度以及`0x1E/USB_PID_OUT`类型就可以触发。

可以参阅下面的PoC代码：

[![](https://p5.ssl.qhimg.com/t0182a3659ad60e6939.png)](https://p5.ssl.qhimg.com/t0182a3659ad60e6939.png)

WinDbg附加的崩溃结果显示，已经控制了程序流程：

[![](https://p5.ssl.qhimg.com/t01d096a605574e8c8c.png)](https://p5.ssl.qhimg.com/t01d096a605574e8c8c.png)

上面的崩溃现场是一个基于堆的缓冲区溢出漏洞。但是，如果想要达到越界写，那么必须创建更多不同类型的TD，这对于利用此漏洞至关重要。之后再创建另一个类型为USB_PID_OUT的TD对象来触发写入。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

为了允许VMware客户计算机访问USB设备，VMware会安装guest虚拟机中指定的内核设备驱动程序`uhci_hcd`，“hcd”代表“主机控制器驱动程序”。此驱动程序允许guest虚拟机与主机端的主机控制器接口（HCI）进行通信，主机端是主机用于与物理USB端口通信的硬件接口。通过向USB设备定义的各种端点发送或接收USB请求块（URB）分组来完成通信。USB设备的每个端点用于接收来自主机（OUT）的数据包，或者将数据包发送到主机（IN）。通过将特制的OUT数据包发送到称为批量端点的特定端点来触发此漏洞。

由`uhci_hcd`驱动程序处理的数据包由`uhci_td`（传输描述符）结构在内存中表示如下：

[![](https://p3.ssl.qhimg.com/t015425f953553cfa7c.png)](https://p3.ssl.qhimg.com/t015425f953553cfa7c.png)

该`token`字段包含不可见的某些位对齐子字段，最低的8位表示“分组ID”，它定义了分组的类型。前10位是一个名为MaxLen的长度字段。

要触发此漏洞，guest虚拟机必须发送精心构造的TD结构，将Packet ID设置为OUT（0xE1）。此外，由`MaxLen`子字段指示的TD的缓冲区长度必须大于0x40字节才能溢出堆上的对象。通过将windbg附加到vmware-vmx.exe并触发漏洞，会收到以下漏洞崩溃场景：

[![](https://p0.ssl.qhimg.com/t01d1c72eab718c356f.png)](https://p0.ssl.qhimg.com/t01d1c72eab718c356f.png)

回溯调用堆栈显示了一系列处理UHCI请求的函数：

[![](https://p2.ssl.qhimg.com/t01cfda1d6f98c041dd.png)](https://p2.ssl.qhimg.com/t01cfda1d6f98c041dd.png)

`memcpy`崩溃进程的调用是在从TD的缓冲区复制数据的过程中发生的：

[![](https://p4.ssl.qhimg.com/t01f0b65ec5d9924018.png)](https://p4.ssl.qhimg.com/t01f0b65ec5d9924018.png)

这是`memcpy`从TD缓冲区复制到堆中的内容：

[![](https://p4.ssl.qhimg.com/t01480e6e6c42a0de79.png)](https://p4.ssl.qhimg.com/t01480e6e6c42a0de79.png)

让我们看看目标缓冲区大小是多少：

[![](https://p1.ssl.qhimg.com/t016d33a2ee7443250b.png)](https://p1.ssl.qhimg.com/t016d33a2ee7443250b.png)

缓冲区的大小为0x58，因为`vmware-vmx`分配了[number_of_TD_structures]**0x40+0x18大小的目标缓冲区。现在只发送了一个TD结构，缓冲区大小是`1**0x40+0x18=0x58`字节。

在这个`memcpy`调用中，我们可以精确地确定要复制的字节数。为此，我们将`MaxLen`OUT TD的`token`字段（从21位到31位）中的子字段设置为所需的`memcpy`大小减1。

现在就可以溢出堆布局了，除了溢出堆之外还能利用此漏洞执行其他越界写。调用函数`NewURB()`（位于`vmware_vmx+0x165710`）以处理传入的URB数据包。每次函数`NewURB()`接收TD时，它都会将TD的`MaxLen`值添加到cursor 变量中。cursor 变量指向函数接收TD结构时应该写入的位置，以这种方式，该`MaxLen`字段可用于在处理后续TD时控制目的地址。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

为了利用此漏洞，必须进行`vmware-vmx`进程堆的布局。漏洞利用主要依赖于客户端上的SVGA3D协议，它用于通过SVGA FIFO与主机通信。在后端VMware使用DX11Renderer组件处理请求。漏洞利用代码从初始化阶段开始，初始化SVGA FIFO内存，然后分配SVGA3D对象表。

利用该漏洞可以尝试创建未分配内存块，每个都具有0x158字节的大小。这正是将一定数量的TD与缓冲区头一起分配所需的大小。TD可能会在其中一个漏洞内分配，在每个漏洞之后，漏洞利用尝试放置一个称为“资源容器”的0x150字节结构表示数据。

漏洞利用代码使用以下步骤准备堆内存：<br>
定义并绑定大小为0x5000的Context内存对象。<br>
定义SPRAY_OBJ大小为0x1000 的内存对象（），利用漏洞重复绑定结构。<br>
定义大小为0x158的2400个着色器，将它们绑定到SPRAY_OBJ。之后，该漏洞利用代码用于SVGA_3D_CMD_SET_SHADER在主机中。<br>
执行以下操作：<br>
—-取消分配每个偶数编号的容器。<br>
—-创建一个表，分配一个大小为0x150的资源容器。此外，主机将分配大小为0x160的关联数据缓冲区。由于大小不同，这些数据缓冲区将位于低碎片堆（LFH）的单独区域中。每个0x150字节的资源容器将包含指向其关联的0x160字节数据缓冲区的指针。<br>
—-再创建两个表，分配另外两个大小为0x160的资源容器。由于它们的大小，在此步骤中分配的资源容器将位于上一步骤的0x160字节数据缓冲区附近的内存中。下面将解释这些“相邻”资源容器的目的。<br>
释放所有剩余容器，释放大小为0x158的块。这些大小为0x158的块将与大小为0x150的资源容器交替放置。

#### <a class="reference-link" name="%E8%B6%8A%E7%95%8C%E5%86%99%E5%85%A5"></a>越界写入

在分析漏洞利用的结构之前，我们先看一下触发漏洞的WriteOOB函数。`WriteOOB`在整个漏洞利用期间，为了不同的目的会被多次调用，例如泄漏`vmware-vmx.exe`和`kernel32.dll`基址，以及最终的代码执行步骤。函数的参数如下：

`WriteOOB()(void * data, size_t data_size, uint32_t offset)`

该`data`参数是一个指向缓冲区的指针，该缓冲区包含我们打算写入主机堆栈的数据。该`size`参数指定数据的长度。最后，该`offset`参数指定要写入数据的位置，相对于将被损坏的资源容器的头部。

该函数首先分配和初始化帧列表和五个TD结构。此函数发送五个TD结构，因此堆上分配的缓冲区大小将为`5*0x40+0x18=0x158`。

`link`除了最后的TD结构之外，每个TD结构使用该字段链接到下一个TD结构。对于前三个TD结构，`MaxLen`子字段设置为0x40。前三个TD结构的分组ID子字段被设置为`USB_PID_SOF`，因此对于每个TD结构，cursor将被往前送0x41字节。第四TD结构的分组ID也被设置为`USB_PID_SOF`，但是对于该TD，`MaxLen`被设置为从`offset`参数计算的值。这使cursor前进了一个可控量。在第五TD中，分组ID被设置为`USB_PID_OUT`，以便将`data`缓冲器的内容写入cursor位置。

#### <a class="reference-link" name="%E5%86%85%E5%AD%98%E6%B3%84%E6%BC%8F%E5%B9%B6%E7%BB%95%E8%BF%87ASLR"></a>内存泄漏并绕过ASLR

既然漏洞利用原语已经写好，那么利用的第一步就是泄漏vmware-vmx.exe的基址。可以通过在TD之后立即破坏资源容器中数据缓冲区的指针来完成的。该指针位于资源容器内的偏移量0x138处，该漏洞通过将其替换为0x00来破坏数据指针的最低有效字节。当引用损坏的指针时，它不再指向数据缓冲区，它会指向位于数据缓冲区附近的0x160字节“相邻”资源容器之一。在这些资源容器中有一些函数指针，因此当数据被复制回guest虚拟机时，`vmware-vmx.exe`会显示基址：

[![](https://p1.ssl.qhimg.com/t0127e31e689ea26ac7.png)](https://p1.ssl.qhimg.com/t0127e31e689ea26ac7.png)

为了精确修改数据指针，需要移动cursor 的字节数如下：<br>
·最初，cursor指向大小为0x158的缓冲区的开头，考虑到第一个0x18字节被保留为缓冲区头，我们只能控制0x140字节。<br>
·0x8字节由以下资源容器的堆块头占用。<br>
·资源容器中数据指针的偏移量为0x138。

总和为0x140 + 0x8 + 0x138 = 0x280，这是cursor必须移动的字节数，指向我们打算修改的字节。

为了将泄漏的函数指针写回到guest虚拟机，该漏洞利用迭代2400个字节堆喷并使用每个映射获取数据`SVGA_3D_CMD_SURFACE_COPY`。然后继续迭代，直到找到泄露的显示`vmware-vmx.exe`基址的函数指针。

为了找到`kernel32.dll`基址，该漏洞利用相同的过程和用于查找的vmware-vmx.exe基址偏移，有一些不同的是，它不是修改指针的单个字节，而是覆盖整个数据指针`vmware_vmx_base_address+0x7D42D8`，这是地址`Kernel32!MultiByteToWideCharStub`存储在导入地址表中的地方。这里就是`kernel32.dll`基地址。

#### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C"></a>代码执行

为了实现代码执行，漏洞再次覆盖堆上的资源容器。这次，漏洞会覆盖资源容器的0x120字节。这个过程完成了三件事：

​ 1 – 将字符串写入`calc.exe`资源容器。<br>
​ 2 – 填写资源容器的某些必要字段。<br>
​ 3 – 覆盖资源容器中偏移量0x120处的函数指针，指向`kernel32!WinExec`。

损坏的资源容器在损坏后的样子：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0169721efb4ef7f5e7.png)

结果是当guest调用`SVGA_3D_CMD_SURFACE_COPY`此损坏的资源容器时，`WinExec`将调用函数指针，将`calc.exe`字符串的地址作为第一个参数传递。该漏洞必须遍历所有2400个表面，以确保使用损坏的资源容器。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E6%80%BB%E7%BB%93"></a>漏洞利用总结

总结如下漏洞利用：

​ 1.堆风水：<br>
​ 分配大小为0x158的2400个shader。<br>
​ 释放大小为0x158的备用shader。<br>
​ 对于每个解除分配的shader，使用大小为0x150的资源容器填充。在此资源容器中，将有一个指向大小为0x160的关联数据缓冲区的指针。还要创建另外两个shader，分配两个大小为0x160且与数据缓冲区相邻的资源容器。<br>
​ 2.泄漏vmware-vmx.exe基地址（迭代64次，直到找到地址）：<br>
​ 调用`WriteOOB`破坏大小为0x150的资源容器并将指针的最低有效字节修改到其数据缓冲区，以便它指向相邻的0x160字节资源容器。该内存包含一些函数指针。<br>
​ 遍历2400个shader并使用数据将数据写回到客户端，`SVGA_3D_CMD_SURFACE_COPY`直到找到泄漏的指针。<br>
​ 3.泄漏kernel32.dll基地址（迭代64次，直到找到地址）：<br>
​ 调用`WriteOOB`破坏大小为0x150的资源容器，并`kernel32.dll`使用导入表中的函数地址修改指向其数据缓冲区的指针VMWare的vmx.exe。<br>
​ 遍历2400个shader并使用数据将数据写回来`SVGA_3D_CMD_SURFACE_COPY`直到找到泄漏的指针。<br>
​ 4.虚拟机逃逸并获得代码执行权限（迭代64次，直到我们执行）：<br>
​ 调用`WriteOOB`以破坏大小为0x150的资源容器。编写“calc.exe”字符串并使用地址修补函数指针`kernel32!WinExec`。<br>
​ `WinExec`通过迭代穿过2400个shader并使用它们将它们写回guest来触发`SVGA_3D_CMD_SURFACE_COPY`。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E6%80%BB%E7%BB%93"></a>漏洞总结

对于某些内存损坏漏洞，可以通过执行VMware guest-to-host，利用漏洞可以通过采用半暴力方式获得代码执行。在VMware中发现可利用的漏洞仍然是一个挑战，但一旦发现漏洞，利用难度也不会很大。VMware SVGA提供各种操作和对象，例如资源容器和shader。根据它们的可调整大小以及它们存储的数据和函数指针，这些在漏洞利用的角度来看是很有用的。
