> 原文链接: https://www.anquanke.com//post/id/204177 


# 深度解构 Bluetooth 设备地址


                                阅读量   
                                **600746**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01fece8e756ae2d575.jpg)](https://p2.ssl.qhimg.com/t01fece8e756ae2d575.jpg)

> Sourcell@海特实验室

所有的 Bluetooth 设备地址 (BD_ADDR) 虽然都固定为 48-bit，但是它们细分下来却有 5 种。下面将分别讨论这 5 种 BD_ADDR。



## BR/EDR 设备地址

在 BR/EDR (Basic Rate/Enhanced Data Rate) 的世界中，每个设备的 BD_ADDR 都应该是唯一的。其格式符合 EUI-48 规范：

```
MSBitLSBit

+-----------------+

|     EUI-48|

+-----------------+

|    OUI    ||

|-----------|-----|

| NAP | UAP | LAP |

|-----|-----------|

||    SAP    |  

|-----|-----------|

|2 B |1 B |3 B |

+-----------------+
```

先简单说明上面的部分字段：
- OUI, Organization Unique Identifier该字段被 IEEE 管理，由 NAP + UAP 组成，用于标识蓝牙设备的厂商。
- NAP, Non-significant Address PartBaseband 定义的 FHS (Frequency Hop Synchronization) packet 会携带 NAP。这个 packet 主要用于在 piconet 信道建立之前或是切换 piconet 时，同步设备间的跳频：
[![](https://p5.ssl.qhimg.com/dm/1024_223_/t01ac7ffa7736554976.png)](https://p5.ssl.qhimg.com/dm/1024_223_/t01ac7ffa7736554976.png)
- UAP, Upper Address Part一些 BR/EDR baseband 定义的重要算法需要 UAP 的参与，比如自适应跳频选择算法的输入值之一就有 UAP（也有 LAP）：
[![](https://p3.ssl.qhimg.com/dm/1024_552_/t01e8a7a9d4405fba0d.png)](https://p3.ssl.qhimg.com/dm/1024_552_/t01e8a7a9d4405fba0d.png)
- SAP, Significant Address PartUAP 与 LAP 组成了与 NAP 对立的字段 SAP。
下面单独说明 LAP 字段。

### LAP

LAP (Lower Address Part) 由厂商分配给自己生产的设备。不过在 LAP 的值域中，有 64 个值被保留使用，它们是 0x9E8B00-0x9E8B3F。

BR/EDR 设备在不同的 link controller 状态中传输 baseband packet 时，将携带不同的 access code。LAP 则会参与这些 access code 的计算。Link controller 状态机如下：

[![](https://p4.ssl.qhimg.com/dm/1024_396_/t01fff359846c071a29.png)](https://p4.ssl.qhimg.com/dm/1024_396_/t01fff359846c071a29.png)

当设备处于 page, page scan 以及 page response 状态时，baseband 上传输的 packet 将携带 DAC (Device Access Code)。该值的计算需要被 page 设备的 BD_ADDR 参与（相当于 LAP 需要参与）。

当设备处于 connection, synchronization train 以及 synchronization scan 状态时，baseband 上传输的 packet 将携带 CAC (Channel Access Code)。该值的计算需要 master 设备地址的 LAP 参与。

当设备处于 inquiry 状态时，若使用 general inquiry，则 baseband 上传输的 packet 需要携带 GIAC (General Inquiry Access Code)。该值与 LAP 保留值 0x9e8b33 相关；若使用 dedicated inquiry，则 packet 需要携带 DIAC (Dedicated Inquiry Access Code)。该值与剩下的 63 个 LAP 保留值相关。



## BLE 设备地址

在 BLE (Bluetooth Low Energy) 的世界中，设备地址有如下 4 种：
- Public Device Address
- Static Device Address
- Resolvable Private Address
- Non-resolvable Private Address
它们之间的关系如下：

[![](https://p1.ssl.qhimg.com/dm/1024_372_/t010d87e5b18ce19309.png)](https://p1.ssl.qhimg.com/dm/1024_372_/t010d87e5b18ce19309.png)

### Public Device Address

Public device address 与 static device address 同属于 identity address。拥有 identity address 是使用 RPA (Resolvable Private Address) 的前提。

Public device address 大体遵循 BR/EDR device address 规范。唯一的不同是 public device address 可以无视 BR/EDR BD_ADDR 规范对 LAP 的限制，除非该地址同时作为 BR/EDR BD_ADDR 使用。

### Static Devcie Address

Static devcie address 的格式如下。其中 random part 需至少有一个为 1 的 bit，也需至少有一个为 0 的 bit：
1. MSBit48-bit LSBit
1. +———————+
1. |1|1| random part |
1. +———————+
如果 BLE 设备使用 static device address，那么在每次上电时它都应该生成一个新的 static device address。而且在一个上电周期中，该地址不应该被改变。Static device address 也有在设备出厂时被写死的情况。在实际场景中，这种地址大概率上可以保证地址的唯一性，同时不像 public device address 需要花钱向 IEEE 购买。

作为远端设备则无法区分一个设备地址是 static device address 还是 public device address。

### Non-resolvable Private Address

这种类型的地址格式如下。其中 random part 中需至少有一个为 1 的 bit，也需至少有一个为 0 的 bit：

```
MSBit48-bit   LSBit

+---------------------+

|1|1| random part |

+---------------------+
```

若 BLE 设备使用 non-resolvable private address，那么它在每次连接时，都需要改变该地址。因此该地址随机性更强，可以保护 BLE 设备的隐私，使其难以被追踪，但同时也让合法的设备难以自动识别自己。

### Resolvable Private Address

Resolvable private address 是 BLE 设备实现隐私策略的关键。若仅使用 identity address，BLE 设备在 advertising 时可能被恶意追踪。因为在一定程度上 identity address 是固定的；若使用 non-resolvable private address 又会导致地址随机化太强，对应用造成不变。Resolvable private address 则可以很好地解决这些问题。其格式如下，其中有 hash = ah(IRK, prand)（IRK 在后面解释）：

```
MSBit48-bit    LSBit

+---------------------+

|0|0| random part |

+---------------------+
```

要使用 resolvable private address 就需要引入 BLE pairing 的概念。当两个 BLE 设备完成配对后，会交换存储各自的 IRK (Identity Resolving Key) 和 identity address：

[![](https://p1.ssl.qhimg.com/dm/1024_415_/t0114f232c82f764f0f.png)](https://p1.ssl.qhimg.com/dm/1024_415_/t0114f232c82f764f0f.png)

之后对端设备收到一个包含 RPA 的 advertising PDU 后，会尝试使用本地存储的 IRK (peer IRK) 计算 localHash = ah(IRK, prand)（其中 prand 从 RPA 中提取），然后将结果 localHash 与 RPA 中包含的 hash 比对。如果两者相同，那么地址解析成功。之后再找到与 peer IRK 对应的 peer device identity address 就可发起连接。

虽然 resolvable private address 也经常发生变化，但结合解析机制后，可以让受信的设备自动识别并连接自己。



## 插曲：BlueZ 定义的 bdaddr_t 类型

BlueZ 为 BD_ADDR 定义了专门的类型 bdaddr_t，并提供了将字符串形式的 BD_ADDR 转为 bdaddr_t 的函数 str2ba：

```
#include&lt;bluetooth/bluetooth.h&gt;

bdaddr_t bdaddr;

str2ba("11:22:33:44:55:66",&amp;bdaddr);
```



## References
1. BLE v4.2: Creating Faster, More Secure, Power-Efficient Designs—Part 2
1. 1.2 BLUETOOTH DEVICE ADDRESSING, BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 2, Part B page 416
1. 蓝牙协议分析(6)_BLE地址类型
1. Bluetooth: Defining NAP + UAP + LAP
1. An Overview of Addressing and Privacy for Laird’s BLE Modules
1. 5.4.5 Privacy feature, BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 1, Part A page 278