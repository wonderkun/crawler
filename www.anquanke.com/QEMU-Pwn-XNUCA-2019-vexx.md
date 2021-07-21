> 原文链接: https://www.anquanke.com//post/id/194937 


# QEMU-Pwn-XNUCA-2019-vexx


                                阅读量   
                                **1415844**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t01d41d622b02bb931a.jpg)](https://p5.ssl.qhimg.com/t01d41d622b02bb931a.jpg)



## 描述

官方给了下载链接，然后一段描述给了用户名和密码：

```
user: root
pass: goodluck
Try to escape the QEMU world!
```

压缩包下载下来，看目录：

```
$ ll
-rw-r--r-- 1 raycp raycp 4.2M Aug  6 01:42 bzImage
-rwxr-xr-x 1 raycp raycp  228 Aug 23 19:04 launch.sh
drwxr-xr-x 6 raycp raycp 4.0K Aug  6 01:42 pc-bios
-rwxr-xr-x 1 raycp raycp  58M Aug  6 01:42 qemu-system-x86_64
-rw-r--r-- 1 raycp raycp  60M Aug  6 01:42 rootfs.ext2
```

`launch.sh`内容：

```
#!/bin/sh
./qemu-system-x86_64 -hda rootfs.ext2 -kernel bzImage -m 64M -append "console=ttyS0 root=/dev/sda oops=panic panic=1" -L ./pc-bios -netdev user,id=mynet0 -device rtl8139,netdev=mynet0 -nographic -device vexx -snapshot
```

根据参数`-device vexx`，多半是要去找`vexx`里面的漏洞。



## 分析

`sudo ./launch.sh`把虚拟机跑起来，然后将`qemu-system-x86_64`拖进IDA里面。

在函数里面搜索`vexx`，查看相关函数：

[![](https://p3.ssl.qhimg.com/t01771f8b351b156019.png)](https://p3.ssl.qhimg.com/t01771f8b351b156019.png)

查看`vexx_class_init`函数，知道了`vendor_id`是`0x11E91234`，`realize`函数是`pci_vexx_realize`。

```
# lspci
00:01.0 Class 0601: 8086:7000
00:04.0 Class 00ff: 1234:11e9
...
# cat /sys/devices/pci0000:00/0000:00:04.0/resource
0x00000000febd6000 0x00000000febd6fff 0x0000000000040200
0x00000000febd0000 0x00000000febd3fff 0x0000000000140204
...
# cat /proc/iomem
...
  febd0000-febd3fff : 0000:00:04.0
...
  febd6000-febd6fff : 0000:00:04.0
...
```

通过命令知道了该设备有两个MMIO地址空间，一个地址为`0xfebd0000`，大小为`0x4000`；另一个则地址为`0xfebd6000`，大小为`0x1000`。

去看`pci_vexx_realize`函数：

```
void __fastcall pci_vexx_realize(VexxState *pdev, Error_0 **errp)
`{`
  ...
  if ( !msi_init(&amp;pdev-&gt;pdev, 0, 1u, 1, 0, errp) )
  `{`
    timer_init_full(&amp;v2-&gt;vexxdma.dma_timer, 0LL, QEMU_CLOCK_VIRTUAL, 1000000, 0, (QEMUTimerCB *)vexx_dma_timer, v2); //注册 vexx_dma_timer
    ...
    memory_region_init_io(&amp;v2-&gt;mmio, &amp;v2-&gt;pdev.qdev.parent_obj, &amp;vexx_mmio_ops, v2, "vexx-mmio", 0x1000uLL);  //注册大小为0x1000的mmio
    memory_region_init_io(&amp;v2-&gt;cmb, &amp;v2-&gt;pdev.qdev.parent_obj, &amp;vexx_cmb_ops, v2, "vexx-cmb", 0x4000uLL);        //注册大小为0x4000的mmio
    portio_list_init(&amp;v2-&gt;port_list, &amp;v2-&gt;pdev.qdev.parent_obj, vexx_port_list, v2, "vexx"); 
    v3 = pci_address_space_io(&amp;pdev-&gt;pdev);
    portio_list_add(&amp;v2-&gt;port_list, v3, 0x230u); //添加pmio，端口为0x230，信息在vexx_port_list结构体中
    pci_register_bar(&amp;pdev-&gt;pdev, 0, 0, &amp;v2-&gt;mmio);
    pci_register_bar(&amp;pdev-&gt;pdev, 1, 4u, &amp;v2-&gt;cmb);
  `}`
```

可以看到相应的存在两个mmio空间一个pmio空间，接下来具体去分析几个io函数。

先看`vexx_mmio_ops`中的`vexx_mmio_read`以及`vexx_mmio_write`。这个结构对应的mmio地址是`0xfebd6000`，空间大小为`0x1000`。这两个函数没啥作用，基本上就是对dma进行的操作。需要知道的是在`vexx_mmio_write`里面`addr`为0x98可以触发`dma_timer`。漏洞不在这里，想对dma有进一步了解，可以去看之前写的htib2017的babyqemu的[writeup](https://ray-cp.github.io/archivers/qemu-pwn-hitb-gesc-2017-babyqemu-writeup)。

然后是`vexx_cmb_ops`中的`vexx_cmb_read`以及`vexx_cmb_write`。`vexx_cmb_read`关键代码如下：

```
uint64_t __fastcall vexx_cmb_read(VexxState *opaque, hwaddr addr, unsigned int size)
`{`
  uint32_t memorymode; // eax
  uint64_t result; // rax

  memorymode = opaque-&gt;memorymode;
  if ( memorymode &amp; 1 )
  `{`
    result = 0xFFLL;
    if ( addr &gt; 0x100 )
      return result;
    LODWORD(addr) = opaque-&gt;req.offset + addr;
    goto LABEL_4;
  ...
LABEL_4:
    result = *(_QWORD *)&amp;opaque-&gt;req.req_buf[(unsigned int)addr];
  `}`
  return result;
```

`req.req_buf`的定义为如下：

```
00000000 VexxRequest     struc ; (sizeof=0x108, align=0x4, copyof_4574)
00000000                                         ; XREF: VexxState/r
00000000 state           dd ?
00000004 offset          dd ?
00000008 req_buf         db 256 dup(?)
00000108 VexxRequest     ends
```

可以看到当`opaque-&gt;memorymode`为1的时候，如果我们可以控制`req.offset`就可以实现对`req.req_buf`的越界读。

再看`vexx_cmb_write`函数关键代码：

```
void __fastcall vexx_cmb_write(VexxState *opaque, hwaddr addr, uint64_t val, unsigned int size)
`{`
  uint32_t memorymode; // eax
  hwaddr v5; // rax

  memorymode = opaque-&gt;memorymode;
  if ( memorymode &amp; 1 )
  `{`
    if ( addr &gt; 0x100 )
      return;
    LODWORD(addr) = opaque-&gt;req.offset + addr;
    goto LABEL_4;
  `}`
  ...
LABEL_4:
    *(_QWORD *)&amp;opaque-&gt;req.req_buf[(unsigned int)addr] = val;
`}`
```

同理我们可以控制`req.offset`就可以实现对`req.req_buf`的越界写。

如果可以控制`req.offset`的话，我们可以越界读写什么：

```
00000000 VexxState       struc ; (sizeof=0x1CF0, align=0x10, copyof_4575)
00000000 pdev            PCIDevice_0 ?
000008E0 mmio            MemoryRegion_0 ?
000009D0 cmb             MemoryRegion_0 ?
00000AC0 port_list       PortioList_0 ?
00000B00 thread          QemuThread_0 ?
00000B08 thr_mutex       QemuMutex_0 ?
00000B38 thr_cond        QemuCond_0 ?
00000B70 stopping        db ?
00000B71                 db ? ; undefined
00000B72                 db ? ; undefined
00000B73                 db ? ; undefined
00000B74 addr4           dd ?
00000B78 fact            dd ?
00000B7C status          dd ?
00000B80 irq_status      dd ?
00000B84 memorymode      dd ?
00000B88 req             VexxRequest ?   //req结构体
00000C90 vexxdma         VexxDma ?      // Vexxdma结构体
00001CF0 VexxState       ends
00000000 ; ---------------------------------------------------------------------------
00000000
00000000 VexxDma         struc ; (sizeof=0x1060, align=0x8, copyof_4573)
00000000                                         ; XREF: VexxState/r
00000000 state           dd ?
00000004                 db ? ; undefined
00000005                 db ? ; undefined
00000006                 db ? ; undefined
00000007                 db ? ; undefined
00000008 dma             dma_state ?
00000028 dma_timer       QEMUTimer_0 ?
00000058 dma_buf         db 4096 dup(?)
00001058 dma_mask        dq ?
00001060 VexxDma         ends
00001060
00000000 ; ---------------------------------------------------------------------------
00000000
00000000 dma_state       struc ; (sizeof=0x20, align=0x8, copyof_4571)
00000000                                         ; XREF: VexxDma/r
00000000 src             dq ?
00000008 dst             dq ?
00000010 cnt             dq ?
00000018 cmd             dq ?
00000020 dma_state       ends
00000020
00000000 ; ---------------------------------------------------------------------------
00000000
00000000 QEMUTimer_0     struc ; (sizeof=0x30, align=0x8, copyof_1099)
00000000                                         ; XREF: VexxDma/r
00000000 expire_time     dq ?
00000008 timer_list      dq ?                    ; offset
00000010 cb              dq ?                    ; offset
00000018 opaque          dq ?                    ; offset
00000020 next            dq ?                    ; offset
00000028 attributes      dd ?
0000002C scale           dd ?
00000030 QEMUTimer_0     ends
```

可以看到`req`结构体后面紧跟的是`VexxDma`结构体，看到该结构体中存在`QEMUTimer`结构体，因为`qwb 2018 final`里面也出现过痛过覆盖`QEMUTimer`来实现逃逸的题，所以瞬间看到了希望。

接下来要搞定的就是看下`req.offset`是否可控以及能否将`opaque-&gt;memorymode`设置为1。

最后还剩下`vexx_port_list`结构体中的`vexx_ioport_read`和`vexx_ioport_write`没有分析，相关线索应该也会在它们中。

`vexx_ioport_read`函数会返回`req.offset`等参数。关键的是`vexx_ioport_write`函数：

```
void __fastcall vexx_ioport_write(VexxState *opaque, uint32_t addr, uint32_t val)
`{`
  if ( addr - 0x230 &lt;= 0x20 )
  `{`
    switch ( addr )
    `{`
      case 0x240u:
        opaque-&gt;req.offset = val; //设置req.offset
        break;
      case 0x250u:
        opaque-&gt;req.state = val;
        break;
      case 0x230u:
        opaque-&gt;memorymode = val; //设置opaque-&gt;memorymode
        break;
    `}`
  `}`
`}`
```

可以看到该函数正好满足了我们的需求，当访问的端口是`0x240`的时候可以设置`req.offset`；当端口`addr`是`0x230`的时候可以设置`opaque-&gt;memorymode`。

至此漏洞就比较明显了，利用`vexx_ioport_write`设置`req.offset`以及`opaque-&gt;memorymode`。然后利用`vexx_cmb_read`和`vexx_cmb_write`对`req.req_buf`进行越界读写，通过`QEMUTimer`来实现泄漏与利用。



## 利用

整个利用包含三个部分。

第一部分是为了能够触发漏洞代码，需要设置`opaque-&gt;memorymode`以及`req.offset`，这一步可以通过PMIO调用`vexx_ioport_write`函数实现。

第二部分是泄露。由于程序开了PIE，所以需要泄露地址。可以通过越界读取`req.req_buf`后面`QEMUTimer`结构体中的`opaque`指针来泄露堆地址（`opaque`指针刚好也是`VexxState`对应的那个指针），可以通过读写`QEMUTimer`结构体中的`cb`指针来泄露程序基址（`cb`指针对应的是`vexx_dma_timer`函数的地址），指针如下图所示。

```
$ checksec qemu-system-x86_64
[*] '/home/raycp/work/vm_escape/release/qemu-system-x86_64'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    FORTIFY:  Enabled
```

[![](https://p3.ssl.qhimg.com/t01495f5133345f6dd7.png)](https://p3.ssl.qhimg.com/t01495f5133345f6dd7.png)

第三部分就是控制程序执行流。在`vexx_mmio_write`触发timer的代码流程中，存在一个函数调用链：`timer_mod-&gt;timer_mod_ns-&gt;timerlist_notify-&gt;notify_cb(notify_opaque)`，可以控制执行流程。即将timer结构体中的`cb`覆盖为`system plt`的地址；将`cat ./flag`写入到`req_buf`中，利用堆偏移计算出`req_buf`的地址，再将该地址覆盖到timer结构体的`opaque`处。在最后控制执行流的时候实现`system("cat ./flag")`的调用。

最终执行前结构体被覆盖内容如下：

[![](https://p5.ssl.qhimg.com/t01e5ecbbd03d1303e8.png)](https://p5.ssl.qhimg.com/t01e5ecbbd03d1303e8.png)

真正在写exp的时候有个坑点：
1. 不知道为啥在访问PMIO的时候，不能用`outl`指令，只能用`outw`和`outb`指令，而且用`outw`指令也会变成一个字节一个字节写，可能是和这个设备有关系，对pci设备还是不太了解，需要进一步学习。


## 小结

还是要有系统的概念会更好一些。

相关文件和脚本[链接](https://github.com/ray-cp/vm-escape/blob/master/qemu-escape/xnuca-2019-vxee/vexx.zip)
