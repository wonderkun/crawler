> 原文链接: https://www.anquanke.com//post/id/196769 


# 在Tesla Model S上实现Wi-Fi协议栈漏洞的利用


                                阅读量   
                                **1098740**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01d13ab5bf0fc4de13.jpg)](https://p0.ssl.qhimg.com/t01d13ab5bf0fc4de13.jpg)





## 介绍



## PARROT模块

[![](https://mmbiz.qpic.cn/mmbiz_png/zZKnUibvoericlmO25dyjL8ibMnNBRlcLUUicticKMhePQEqfh5gGshg6NfBoZ98hLicw1R5j2HicSVX6o44feia8gnJvQ/640?wx_fmt=png)](https://p5.ssl.qhimg.com/t0182977fed6055085f.png)[![](https://p3.ssl.qhimg.com/t01f5a00f9abf94f2a2.jpg)](https://p3.ssl.qhimg.com/t01f5a00f9abf94f2a2.jpg)

Parrot模块的引脚定义也在这份datasheet中。Linux系统的shell可以通过Debug UART引脚得到。

[![](https://mmbiz.qpic.cn/mmbiz_png/zZKnUibvoericlmO25dyjL8ibMnNBRlcLUUA3d3W9L0IAgQiaj0cwoDyJfz1zophoQrlH925zRibrcfHPhQfibhJaHhg/640?wx_fmt=png)](https://p5.ssl.qhimg.com/t0182977fed6055085f.png)[![](https://p1.ssl.qhimg.com/t01cf9df346b05d3742.jpg)](https://p1.ssl.qhimg.com/t01cf9df346b05d3742.jpg)

其中的reset引脚连到到CID的GPIO上，因此CID有能力通过下列命令重置整个Parrot模块

```
echo 1 &gt; /sys/class/gpio/gpio171/value

sleep 1

echo 0 &gt;   /sys/class/gpio/gpio171/value
```



## Marvell 无线芯片

[![](https://p1.ssl.qhimg.com/dm/1024_439_/t012af1859fae8220a9.jpg)](https://p1.ssl.qhimg.com/dm/1024_439_/t012af1859fae8220a9.jpg)

Marvell 88W8688包含了一个嵌入式高性能Marvell Ferocean ARM9处理器。通过修改固件，我们获得了Main ID寄存器中的数值0x11101556，据此推断88W8688使用的处理器型号可能是Feroceon 88FR101 rev 1。在Parrot模块上，Marvell 88w8688芯片通过SDIO接口与主机系统相连。

Marvell 88W8688的内存区域如下：

## 芯片固件

```
struct fw_chunk `{`

int chunk_type;

int addr;

unsigned int length;

unsigned int crc32;

unsigned char [1];

`}` __packed;
```

在逆向识别出所有的ThreadX API之后，各个任务的信息便可以得到。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_448_/t01e621822156c1cce6.png)

同时，内存池的相关信息也可以得到。

[![](https://mmbiz.qpic.cn/mmbiz_png/zZKnUibvoericlTuxU68ibXsCrRjAPUoICufjs8iajJg4CMWdHA5TaYs7YicOP9vwwM4rnaQ5iaxF8ZqvTGlHI3qpSyA/640?wx_fmt=png)](https://p4.ssl.qhimg.com/t0182977fed6055085f.png)[![](https://p0.ssl.qhimg.com/dm/1024_468_/t017ed4db562a1c1653.jpg)](https://p0.ssl.qhimg.com/dm/1024_468_/t017ed4db562a1c1653.jpg)



## 日志及调试

所以我们修改了固件，并自己实现了这些异常处理过程。这些处理过程会记录固件崩溃时的一些寄存器信息，包括通用寄存器，系统模式及中断模式下的状态寄存器和链接寄存器。通过这种方式，我们可以知道崩溃时系统模式或中断模式下的一些寄存器信息。

[![](https://mmbiz.qpic.cn/mmbiz_png/zZKnUibvoericlmO25dyjL8ibMnNBRlcLUUKSWb7pPhiaezCI8JOhEk0nJ3NJTKlJOl6sgkFP6XI8WgfT6IbvuBGJw/640?wx_fmt=png)](https://p4.ssl.qhimg.com/t0182977fed6055085f.png)[![](https://p1.ssl.qhimg.com/t01ebfb218a167b7898.png)](https://p1.ssl.qhimg.com/t01ebfb218a167b7898.png)

我们将这些寄存器信息写到末使用的内存区域，例如0x52100~0x5FFFF。这样，这些信息在芯片重置后仍然可以被读取。

在实现了undefine异常处理过程及修改一些指令为undefine指令后，我们可以在固件运行时获取或设置寄存器的内容。用这种方式，我们可以调试固件。

将新的固件下载到芯片中运行，可在内核驱动中发送命令HostCmd_CMD_SOFT_RESET到芯片。随后芯片会重置，新的固件会下载。



## 固件中的漏洞

ADDTS的整个过程如下：当系统想要发送ADDTS请求时，内核驱动会发送HostCmd_CMD_WMM_ADDTS_REQ命令给芯片，然后芯片将ADDTS请求通过无线协议发送出去。当芯片收到ADDTS response后，将该回复信息去掉Action帧头部复制到HostCmd_CMD_WMM_ADDTS_REQ结构体，作为ADDTS_REQ命令的结果在HostCmd_DS_COMMAND结构体中返回给内核驱动。内核驱动来实际处理ADDTS response。

```
struct _HostCmd_DS_COMMAND

`{`

    u16 Command;

    u16 Size;

    u16 SeqNum;

    u16 Result;

    union

    `{`

        HostCmd_DS_GET_HW_SPEC hwspec;

        HostCmd_CMD_WMM_ADDTS_REQ;

        …….

     `}`

`}`
```

## 驱动中的漏洞

命令处理的过程大致如下。驱动接收到用户态程序如ck5050、wpa_supplicant发来的指令，在函数wlan_prepare_cmd()中初始化HostCmd_DS_COMMAND结构体，该函数的最后一个参数pdata_buf指向与命令有关的结构，函数wlan_process_cmdresp()负责处理芯片返回的结果并将相关信息复制到pdata_buf指向的结构中。

```
int

wlan_prepare_cmd(wlan_private * priv,

u16 cmd_no,
u16 cmd_action,
u16 wait_option, WLAN_OID cmd_oid, void *pdata_buf);
```

## 芯片内代码执行

[![](https://p3.ssl.qhimg.com/dm/1024_306_/t0174b34488bc4937aa.png)](https://p3.ssl.qhimg.com/dm/1024_306_/t0174b34488bc4937aa.png)

源地址及目的地址均位于RAM内存区域0xC0000000~0xC003FFFF，但是内存地址0xC0000000到0xCFFFFFFF都是合法的。结果就是，读或写下面这些内存区域会得到完全一样的效果。

[![](https://p4.ssl.qhimg.com/t0180bc5300f79e1e57.png)](https://p4.ssl.qhimg.com/t0180bc5300f79e1e57.png)

因为内存区域0xC0000000到0xCFFFFFFF都是可读可写的，所以复制过程几乎不会碰到内存的边界。在复制了0x40000个字节后，整个内存可被看作是整体移位了，其中有些数据被覆盖并且丢失了。

[![](https://p1.ssl.qhimg.com/t012a9da2b8c32f2927.png)](https://p1.ssl.qhimg.com/t012a9da2b8c32f2927.png)

88w8688中的CPU是单核的，所以复制过程中芯片不会崩溃直到有中断产生。因为这时内存已被破坏，在大多数情况下，芯片崩溃在中断过程中。

中断控制器给中断系统提供了一个接口。当一个中断产生时，固件可从寄存器中获取中断事件类型并调用相应的中断处理过程。

[![](https://mmbiz.qpic.cn/mmbiz_png/zZKnUibvoericlmO25dyjL8ibMnNBRlcLUUxNIKeY6BN42KuRaApoD9bK2DHs9GDLavAiafLsyMQzsGtvFiaDtfbIWA/640?wx_fmt=png)](https://p5.ssl.qhimg.com/t0182977fed6055085f.png)[![](https://p0.ssl.qhimg.com/dm/1024_814_/t017a47dd8f1318a3ef.jpg)](https://p0.ssl.qhimg.com/dm/1024_814_/t017a47dd8f1318a3ef.jpg)

中断源有很多，所以漏洞触发后，芯片可能崩溃在多个位置。

一个可能性是中断0x15的处理过程中，函数0x26580被调用。0xC000CC08是一个链表指针，这个指针在漏洞触发后可能会被篡改。然而，对这个链表的操作很难给出获得代码执行的机会。

[![](https://mmbiz.qpic.cn/mmbiz_png/zZKnUibvoericlmO25dyjL8ibMnNBRlcLUUTOwe1crRAV2LfslpLk2Y3zwGstmI7vgGx4TNgriaWSxyMCTG5GcTkxg/640?wx_fmt=png)](https://p5.ssl.qhimg.com/t0182977fed6055085f.png)[![](https://p0.ssl.qhimg.com/t01b52e256bb33b15b6.jpg)](https://p0.ssl.qhimg.com/t01b52e256bb33b15b6.jpg)

另一个崩溃位置在时钟中断的处理过程中。处理过程有时会进行线程的切换，这时其他任务会被唤醒，那么复制过程就会被暂停。然后芯片可能崩溃在其他任务恢复运行之后。在这种情况下，固件通常崩溃在函数0x4D75C中。

[![](https://mmbiz.qpic.cn/mmbiz_png/zZKnUibvoericlmO25dyjL8ibMnNBRlcLUU9s9zfFCufXTNKJCegrCp3HO8lCTXwbpbchum845vSeCyrNHslWbQLg/640?wx_fmt=png)](https://p2.ssl.qhimg.com/t0182977fed6055085f.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e2bc020ea22f48dc.png)

这个函数会读取一个指针0xC000D7DC，它指向结构TX_SEMAPHORE。触发漏洞后，我们可以覆盖这个指针，使其指向一个伪造的TX_SEMAPHORE结构。

```
typedef struct TX_SEMAPHORE_STRUCT

`{`

ULONG       tx_semaphore_id;
CHAR_PTR    tx_semaphore_name;
ULONG       tx_semaphore_count;
struct TX_THREAD_STRUCT  *tx_semaphore_suspension_list;
ULONG       tx_semaphore_suspended_count;
struct       TX_SEMAPHORE_STRUCT *tx_semaphore_created_next; 
struct       TX_SEMAPHORE_STRUCT *tx_semaphore_created_previous;
`}` TX_SEMAPHORE;
```

我们可以直接将“BL os_semaphore_put”指令的下一条指令改成跳转指令来实现任意代码执行，因为ITCM内存区域是RWX的。困难在于我们需要同时在内存中堆喷两种结构TX_SEMAPHORE和TX_THREAD_STRUCT，并且还要确保指针 tx_semaphore_suspension_list 指向TX_THREAD_STRUCT结构。这些条件可以被满足，但是利用成功率会非常低。

我们主要关注第三个崩溃位置，在MCU中断的处理过程中。指向struct_interface 结构的指针g_interface_sdio会被覆盖。

```
struct struct_interface

`{`

  int field_0;

  struct struct_interface *next;

  char *name_ptr;

  int sdio_idx;

  int fun_enable;

  int funE;

  int funF;

  int funD;

  int funA;

  int funB; // 0x24

  int funG;

  int field_2C;

`}`;
```

这是当函数interface_call_funB()中的指令“BX R3” 在地址0x3CD4E执行时的一份寄存器日志信息。此时，g_interface_sdio被覆盖成了0xabcd1211。

函数interface_call_funB()在地址0x4E3D0处被MCU中断的处理过程使用。

[![](https://mmbiz.qpic.cn/mmbiz_png/zZKnUibvoericlmO25dyjL8ibMnNBRlcLUUU3m0OIy1Od1yxs69sqF3oOqhpm4QIFCLysvPfhX0ZQwqUOrB95PAmQ/640?wx_fmt=png)](https://p1.ssl.qhimg.com/t0182977fed6055085f.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d8dadb8dba6c0427.png)

当复制的源地址到达0xC0040000时，整个内存可被看作是做了一次偏移。当复制的源地址到达0xC0080000时，整个内存偏移了两次。每次偏移的距离如下。

```
0xC0016478-0xC000DC9B=0x87DD

0xC0016478-0xC000E49B=0x7FDD

0xC0016478-0xC000EC9B=0x77DD

0xC0016478-0xC000F49B=0x6FDD
```

```
0xC000B818+0x87DD*1=0xC0013FF5

0xC000B818+0x87DD*2=0xC001C7D2

0xC000B818+0x87DD*3=0xC0024FAF

0xC000B818+0x87DD*4=0xC002D78C

…

0xC000B818+0x7FDD*1=0xC00137F5

0xC000B818+0x7FDD*2=0xC001B7D2

0xC000B818+0x7FDD*3=0xC00237AF

0xC000B818+0x7FDD*4=0xC004B700

…

0xC000B818+0x77DD*1=0xC0012FF5

0xC000B818+0x77DD*2=0xC001A7D2

0xC000B818+0x77DD*3=0xC0021FAF

0xC000B818+0x77DD*4=0xC002978C

…

0xC000B818+0x6FDD*1=0xC00127F5

0xC000B818+0x6FDD*2=0xC00197D2

0xC000B818+0x6FDD*3=0xC00207AF

0xC000B818+0x6FDD*4=0xC002778C

…
```

为了堆喷伪造的指针，我们可以发送许多正常的802.11数据帧给芯片，其中填满了伪造的指针。DMA buffer非常大，因此shellcode也可以直接放在数据帧中。为了提高利用的成功率，我们用了Egg Hunter在内存中查找真正的shellcode。

[![](https://p2.ssl.qhimg.com/dm/1024_216_/t015252175076623ef9.png)](https://p2.ssl.qhimg.com/dm/1024_216_/t015252175076623ef9.png)

如果g_interface_sdio被成功的覆盖。Shellcode或egg hunter会非常的接近0xC000B818。我们所使用的伪造指针是0x41954，因为在地址0x41954+0x24处有一个指针0xC000B991。这样，我们可以劫持$PC到0xC000B991。同时，指针0x41954可被作为正常的指令执行。

```
54 19 ADDS            R4, R2, R5

04 00 MOVS            R4, R0
```

## 攻击主机系统

这种情况下，pdata_buf指向的buffer由kmalloc()分配，所以这是一个内核堆溢出。在真实环境中函数wlan_get_firmware_mem()不会被用到，并且堆溢出的利用较复杂。

然而，一个被攻陷的芯片在返回某个命令的结果时可以更改命令ID。因此漏洞可以在许多命令的处理过程中被触发。这时，根据pdata_buf指向的位置，漏洞即可以是堆溢出也可以是栈溢出。我们找到了函数wlan_enable_11d()，它把局部变量enable的地址作为pdata_buf。因此我们可以触发一个栈溢出。

[![](https://p1.ssl.qhimg.com/t011e7192c0c67505d5.jpg)](https://p1.ssl.qhimg.com/t011e7192c0c67505d5.jpg)

函数wlan_enable_11d()被wlan_11h_process_join()调用。显然HostCmd_CMD_802_11_SNMP_MIB会在与AP的连接过程中被使用。固件中的漏洞只能在Parrot已经加入AP后使用。为了触发wlan_enable_11d()中的栈溢出，芯片需要欺骗内核驱动芯片已经断开与AP的连接。接着，驱动会发起重连，在这个过程中HostCmd_CMD_802_11_SNMP_MIB会发送给芯片。于是，为了触发重连过程，芯片需要发送EVENT_DISASSOCIATED事件给驱动。

当在芯片中触发漏洞并获得代码执行之后芯片不能再正常工作。所以我们的shellcode需要自己处理重连过程中的一系列命令并返回相应的结果。在命令HostCmd_CMD_802_11_SNMP_MIB来到之前，唯一一个我们要构造返回结果的命令是HostCmd_CMD_802_11_SCAN。下面是断开连接到触发内核漏洞的整个过程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019e919fc915bf2cf6.png)

SDIO接口上事件和命令数据包的发送可直接通过操作寄存器SDIO_CardStatus和SDIO_SQReadBaseAddress0来完成。SDIO接口上获得内核发来的数据可借助SDIO_SQWriteBaseAddress0寄存器。



## Linux系统中命令执行



## 远程获取shell
<td colspan="1" rowspan="1" width="10.0000%"><section>1</section></td><td colspan="1" rowspan="1" width="90.0000%"><section>在向内核发送完payload之后，我们通过如下命令重置了芯片。在这之后，内核驱动会重新发现芯片然后重新下载固件。<pre class="pure-highlightjs">`*(unsigned int *)0x8000201c|=2;*(unsigned int *)0x8000a514=0;*(unsigned int *)0x80003034=1;`</pre></section></td>
<td colspan="1" rowspan="1" width="10.0000%"><section>2</section></td><td colspan="1" rowspan="1" width="90.0000%"><section>在shellcode的函数fun_ret()中调用内核函数rtnl_unlock()来解开rtnl_mutex锁。否则Linux的无线功能会无法正常功能，导致Parrot被CID重启。</section></td>
<td colspan="1" rowspan="1" width="10.0000%"><section>3</section></td><td colspan="1" rowspan="1" width="90.0000%"><section>在shellcode的函数fun_ret()中调用do_exit()来终止用户态进程wpa_supplicant并重新运行，这样就不需要修复内核栈。</section></td>
<td colspan="1" rowspan="1" width="10.0000%"><section>4</section></td><td colspan="1" rowspan="1" width="90.0000%"><section>杀掉进程ck5050并重新运行，否则稍后ck5050会因芯片重置而崩溃，导致Parrot被CID重启。</section></td>

为了远程获取shell，我们强制让Parrot连入我们自己的AP并修改iptables规则。之后，便可通过23端口访问到Parrot的shell。

最终拿到shell的成功率在10%左右。



## 完整的利用过程

[![](https://p3.ssl.qhimg.com/t015faf0b40ea591db2.png)](https://p3.ssl.qhimg.com/t015faf0b40ea591db2.png)

## 总结

## 负责任的漏洞披露
<li>
<section>[https://www.cnvd.org.cn/flaw/show/CNVD-2019-44105](https://www.cnvd.org.cn/flaw/show/CNVD-2019-44105)</section>
</li>
<li>
<section>[http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201911-1040](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201911-1040)</section>
</li>
<li>
<section>[http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201911-1038](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201911-1038)</section>
</li>
<li>
<section>[https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-13581](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-13581)</section>
</li>
<li>
<section>[https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-13582](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-13582)</section>
</li>


## 参考文献

[3][https://www.marvell.com/wireless/assets/Marvell-88W8688-SoC.pdf](https://www.marvell.com/wireless/assets/Marvell-88W8688-SoC.pdf)

[4][https://www.marvell.com/documents/ioaj5dntk2ubykssa78s/](https://www.marvell.com/documents/ioaj5dntk2ubykssa78s/)
