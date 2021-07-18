
# nRF51822 的隐藏技能：嗅探 BLE 连接标识


                                阅读量   
                                **773785**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](./img/199160/t017c8e196691e86f08.jpg)](./img/199160/t017c8e196691e86f08.jpg)



作者：sourcell @安恒安全研究院海特实验室

## 前言

本文分析了 Damien Cauquil 在 btlejack-firmware 中实现的一个有趣的技术。根据他的描述，该技术应该受到了 Travis Goodspeed 所写 Promiscuity is the nRF24L01+’s Duty 一文的启发。Damien Cauquil 对于该技术的描述如下：

[![](./img/199160/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015e7e8796212edece.png)



## 称为隐藏技能的原因

[![](./img/199160/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01add415b15b41498f.png)

但要使用隐藏技能需要将该 field 配置为 1。

```
#include &lt;nrf51.h&gt;
#include &lt;nrf51_bitfields.h&gt;​
NRF_RADIO-&gt;PCNF1 |= 1UL &lt;&lt; RADIO_PCNF1_BALEN_Pos;
```



## Access Address（连接标识）

Access address 是 BLE 连接的标识。如果我们能在 37 个 BLE data channels 上嗅探 access address，那么附近所有的 BLE 连接都能被我们识别。



## nRF51822 接收 Radio Packet 的流程

[![](./img/199160/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e724d61ab5d4d956.png)

下面我们在禁用 CRC 与 (de)whiting 的前提下，讨论 nRF51822 的 address match 机制：

```
NRF_RADIO-&gt;PCNF1 = RADIO_PCNF1_WHITEEN_Disabled &lt;&lt; RADIO_PCNF1_WHITEEN_Pos;
NRF_RADIO-&gt;CRCCNF = 0UL; // Disable CRC
```
1. ANT 在接收到完整的 preamble (0x55 or 0xAA) 后，会立即通知 receiver 开始工作。
1. Receiver 开始工作后，会把空中的 bits 交给 address match 处理。
1. Address match 在处理空中的 bits 时，可能发现 base address 与 prefix 无法匹配。
1. Address match 继续处理空中的 bits，直到 base address 与 prefix 匹配成功。
1. Base address 与 prefix 匹配成功后，将发生 ADDRESS event，NRF_RADIO-&gt;EVENTS_ADDRESS 被置 1。


## 站在 Travis Goodspeed 的肩膀上

> 参考 reference 1、2。

[![](./img/199160/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013216240f8fc97d71.png)

nRF24L01+ 这样做确实是有道理的。Radio 外设要实现接收 radio packet 就必须做一个决策：何时开始匹配 radio packet 定义的字段。nRF24L01+ 的决定是不断从空中采样，直到交替出现 0 和 1（preamble, hi-low toggling），就开始将后续的空中数据与 register 中预设的 address 进行匹配。因此 radio packet 发送方发出的 preamble 对于接收方只是一个开始匹配 address 字段的信号，而不是参与匹配的字段。

之后 btlejack 发现 nRF51822 同 nRF24L01+ 一样，也具有上述特性。nRF51822 的 on-air radio packet 格式如下：

[![](./img/199160/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011bf857193c71f08f.png)

### 正常使用 nRF51822 收发 BLE LL Packet

在 nRF51822 上发送 BLE LL packet 时，发送方会把 radio packet 的 address 字段配置为 4 bytes，用于存储 BLE LL packet 定义的 access address：

```
// len(ADDRESS) 4 B = len(BASE) 3 B + len(PREFIX) 1 B
NRF_RADIO-&gt;PCNF1 &amp;= ~RADIO_PCNF1_BALEN_Msk; // Clear BALEN
NRF_RADIO-&gt;PCNF1 |= 0x3 &lt;&lt; RADIO_PCNF1_BALEN_Pos;
```

发送方确定 address 字段后，待发送的 preamble 会由 radio 外设自动配置好。对于接收方，我们只需与发送方做相同的 address 字段配置就可以匹配到期望的 radio packet。接收方的 radio 外设在匹配 radio packet 的 address 字段时，不论匹配是否成功，nRF51822 都不会将其存入 RAM。就算在匹配 address 成功时，nRF51822 也仅会把 radio packet 的 payload 字段写入 RAM，供我们做后续的处理。

### 使用非法但可用的 Address 字段配置实现 Sniffing

与正常使用 nRF51822 收发 BLE LL packet 不同的是我们想嗅探并从 RAM 中拿到到所有可能的 address 字段，即标识已存在 BLE 连接的 access address。所以我们要求不论接收方的 radio 外设是否成功匹配空中的 address 字段，该字段都要被写入 RAM 中。

让 nRF51822 把 address 字段写入 RAM，可以转换为让 nRF51822 把 address 字段当作 payload 处理。需要注意的是由于 nRF51822 的 CRC 校验自动包含所有的 payload，而 BLE 又规定 access address 不参与 CRC 运算，所以把 address 字段当作 payload 处理后，我们就不能再使能 nRF51822 的 CRC 校验：

```
NRF_RADIO-&gt;CRCCNF = 0x0; // Disable CRC
```

Radio packet 的 address 字段被划为 payload 后，作为接收方的 nRF51822 就只剩 preamble 可以匹配了。于是我们把 preamble 配置为 address 字段，比如 0x00 0xAA：

```
+--------------------+
| BASE | PREFIX      |
|------|-------------| nRF51822 radio packet
| 0x00 | 0xAA        |
+--------------------+--------------------------------+----------+
                     | S0   | LENGTH | S1   | PAYLOAD | STATIC   |
Radio packet in RAM  |------|--------|------|---------|----------|
                     | None | None   | None | None    | 10 Bytes |
                     +-------------------------------------------+
```

代码如下：

```
NRF_RADIO-&gt;PREFIX0 = 0xAA &lt;&lt; RADIO_PREFIX0_AP0_Pos; // 也可以设成 0x55
NRF_RADIO-&gt;BASE0 = 0x00000000;
NRF_RADIO-&gt;PCNF1 &amp;= ~RADIO_PCNF1_BALEN_Msk; // Clear BALEN
NRF_RADIO-&gt;PCNF1 |= 0x1 &lt;&lt; RADIO_PCNF1_BALEN_Pos; // 1 0x00 before Preamble
```

该配置是非法的，因为 nRF51 Series Reference Manual 允许的 ADDRESS 长度最小为 3，而我们把它配置成了 2。Manual 的要求如下：

[![](./img/199160/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01539f0066bf5b18b4.png)

这个配置虽然非法，但仍可以使 nRF51822 的 radio 外设工作起来。

之后，只要空中出现一连串交替 0 和 1（这不一定是 preamble，还可以是 noise），nRF51822 就开始尝试匹配 0x00 0xAA，直到匹配成功，与真正的 BLE preamble 同步。

> 0xAA 是 BLE LL packet 可能的 preamble 之一。后续会分析如何处理另一个可能的 preamble 0x55。

在 BLE preamble 0xAA 前添加一个 0x00 的原因是，当无空中数据时，radio 外设会采样到大量的 0x00 或 0xFF（参考 reference 1，但待亲自观察）。此时 radio 匹配 address 字段的工作不会被触发，因为 0x00 与 0xFF 不是交替出现的 0 或 1。那么可以判断在无 noise 的情况下，preamble 0xAA 之前不是 0x00，就是 0xFF（后面会详细解释有噪声的情况如何处理）。所以这里我们把 0x00 0xAA 配置为待匹配的 address 字段。当然 0xFF 0xAA 作为 address 字段也行，但实际验证发现 0x00 0xAA 效果最好。注意将 address 字段配置成 0x00 0x00 0xAA 等形式均没有 0x00 0xAA 好。因为 0xAA 前有一个 0x00 的可能性肯定比有两个 0x00 的可能性更大，可能性越大就越容易匹配到合适的 address 字段（这里与 access address 等同）。

> 对于接收方而言，空中有无数据取决于信号强度。参考 reference 3 可知 BLE 的 sensitivity level 为 -70 dBm。

一旦 nRF51822 的匹配工作被 noise 触发，并最终与 0x00 0xAA 同步（如果在 0xAA 前出现了一个 0x00 那么我们便幸运的同步了），可能的 access address 就会被存入 RAM。

> Noise 一定会包含可以触发 nRF51822 匹配工作的 0、1 序列。比如若存在 BLE 连接，空中就会出现 0xAA 或 0x55（noise）。该序列出现后，radio 外设就开始匹配 0x00 0xAA，最终可能在下一个 BLE LL packet 中匹配到 0x00 0xAA，于是后续的 access address 便被存入 RAM。



## 处理 Noise 并从 RAM 中提取 Access Address

### 理想情况：不需要移位

理想情况意味着 radio packet address 字段的 base 与 prefix 间没有噪声，而且空中 BLE LL packet 的 preamble 与我们 radio 使用的 0xAA prefix 相同。此时 RAM 中存 储的数据如下：

```
+--------------------+
| BASE | PREFIX      |
|------|-------------| nRF51822 radio packet
| 0x00 | 0xAA        |
+--------------------+--------------------------------+-----------------------+
                     | S0   | LENGTH | S1   | PAYLOAD | STATIC                |
Radio packet in RAM  |------|--------|------|---------|-----------------------|
                     | None | None   | None | None    | 10 Bytes              |
       +-------------+--------------------------------+-----------------------+
       | Preamble    |                                | Access Addr | ... ... |
       |-------------| BLE LL packet                  |-------------|---------|
...0 0 | 0xAA        |                                | 4 Bytes     | 6 Bytes |
       +-------------+                                +-----------------------+
```

此时 RAM 中数据的前 4 个字节就是候选的 access address。

### 理想情况：整体右移 1 bit

BLE LL packet 的 preamble 除了为 0xAA（access address 的 LSBit 为 0），还可能为 0x55（access address 的 LSBit 为 1）。若此时 base 与 prefix 间没有噪声则， RAM 中 存储的数据如下：

```
LSB                      MSB
+---------------------------------+
| BASE | PREFIX                   |
|------|--------------------------| nRF51822 radio packet
| 0x00 | 0   1 0 1 0 1 0 1 (0xAA) |
+---------------------------------+--------------------------------+--------------------------------------+
                                  | S0   | LENGTH | S1   | PAYLOAD | STATIC                               |
Radio packet in RAM               |------|--------|------|---------|--------------------------------------|
                                  | None | None   | None | None    | 10 Bytes                             |
       +--------------------------+--------------------------------+--------------------------------------+
       |   | Preamble without MSB |                                | Preamble MSB | Access Addr | ... ... |
       |--------------------------| BLE LL packet                  |--------------|-------------|---------|
...0 0 | 0 | 1 0 1 0 1 0 1        |                                | 0 (0x55)     | 4 Bytes     | 47 bits |
       +--------------------------+                                +--------------------------------------+
       LSB                      MSB                                LSB                                  MSB
```

此时 RAM 中的 radio packet 会多出一个来自 preamble 0x55 的 MSBit。且这个 preamble MSBit 占用了 RAM 中 radio packet 的 LSBit。所以我们在这种情况下提取 access address 时需要将 RAM 中的 radio packet 整体右移一位，从而去掉 preamble MSBit。之后，RAM 中 radio packet 的前 4 个 bytes 就是候选的 access address。

### 不理想的情况：需要且仅需要右移 2 bits

由于 noise 的存在，radio packet address 字段的 base 与 prefix 可能并不连续。比如，base 0x00 与 prefix 0xAA 间出现了一个噪音 0 1，此时，nRF51822 在匹配 address 的时候可能发生如下情况：

```
LSB                        MSB
+------------------------------------+
| BASE | PREFIX                      |
|------|-----------------------------| nRF51822 radio packet
| 0x00 | 0 1   0 1 0 1 0 1 (0xAA)    |
+------------------------------------+--------------------------------+---------------------------------------+
                                     | S0   | LENGTH | S1   | PAYLOAD | STATIC                                |
Radio packet in RAM                  |------|--------|------|---------|---------------------------------------|
                                     | None | None   | None | None    | 10 Bytes                              |
       +-----------------------------+--------------------------------+---------------------------------------+
       |     | Preamble without MSBs |                                | Preamble MSBs | Access Addr | ... ... |
       |-----------------------------| BLE LL packet                  |---------------|-------------|---------|
...0 0 | 0 1 | 0 1 0 1 0 1           |                                | 0 1 (0xAA)    | 4 Bytes     | 46 bits |
       +-----------------------------+                                +---------------------------------------+
       LSB                         MSB                                LSB                                   MSB
```

在这种情况下 BLE LL packet 的 0xAA preamble 会有两个 bits 进入到 RAM 中。因此我们需要将 RAM 中的 radio packet 整体右移 2 bits，来剔除它们。之后 RAM 中 radio packet 的前 4 bytes 就为候选的 access address。

### 不需要右移更多的 bits

Radio packet address 字段的 base 与 prefix 之间除了 0 1 噪声，还能可能存在很多其他的噪声，比如 0 1 0 1：

```
LSB                             MSB
+----------------------------------------+
| BASE | PREFIX                          |
|------|---------------------------------| nRF51822 radio packet
| 0x00 | 0 1 0 1   0 1 0 1 (0xAA)        |
+----------------------------------------+--------------------------------+----------------------------------------+
                                         | S0   | LENGTH | S1   | PAYLOAD | STATIC                                 |
radio packet in RAM                      |------|--------|------|---------|----------------------------------------|
                                         | None | None   | None | None    | 10 Bytes                               |
       +---------------------------------+--------------------------------+----------------------------------------+
       |         | Preamble without MSBs |                                | Preamble MSBs  | Access Addr | ... ... |
       |---------------------------------| BLE LL packet                  |----------------|-------------|---------|
...0 0 | 0 1 0 1 | 0 1 0 1               |                                | 0 1 0 1 (0xAA) | 4 Bytes     | 46 bits |
       +---------------------------------+                                +----------------------------------------+
       LSB                             MSB                                LSB                                    MSB
```

不过这种情况发生的概率较低，最多为 1/8 * 0.1，不值得我们占用 Cortex-M0 来右移 4 位做进一步处理（后续会对这种情况做进一步解释）。

> 概率数据参考 reference 4。
- 若在 …0 0 与 0 1 0 1 0 1 0 1 之间加入噪声后，无法从头匹配 address（类似 high-low toggling），则匹配窗口会自动忽略它们直到匹配到新的 address。
- 若在 …0 0 与 0 1 0 1 0 1 0 1 之间加入噪声后可以从头匹配 address，则会回归到偶数个噪声 bits 的情况。证明如下：令噪声导致的奇数个比特从 LSB 到 MSB 组成了名为 noise_bits 的 list。为了匹配 address（再次说明类似 high-low toggling），则必须有 noise_bits[0] == 1 and noise_bits[-1] == 1。由于 noise_bits[0] 为 1 时，与 base 中的 MSB 0 再次组成了 high-low toggling（address 的一部分），所以此时 address 将永远不可能从 noise_bits[0] 开始匹配，而会从 …0 0 序列的 MSB 开始匹配，及 noise_bits[0] 匹配了 address 的倒数第二低的 bit。于是噪声 bits 数被加 1。又奇数加 1 必定成为偶数。所以证明了原命题。


## 使用 BLE LL Data Channel Empty PDU 过滤候选的 Access Address
<li>
<section>若真的在 base …0 0 与 prefix 0 1 0 1 0 1 0 1 之间出现了，(0 1)… 这种较小概率噪声怎么办？</section>
</li>
<li>
<section>噪声除了在 base 与 prefix 之间出现，还可能在 prefix 中间以及 access address 或 BLE LL data channel PDU 中出现。这种情况又怎么处理。</section>
</li>


## 情形一

```
+--------------+-------+-----------------------+
| Noise        | Noise | BASE (1 B) | PREFIX   |
|--------------|-------|------------|----------| nRF51822 On-air packet layout
| 0xAA or 0x55 | 'x'   | 0x00       | 0xAA     |
+--------------+-------+-----------------------+--------------------------------+-------------------------------------------+
                                               | S0   | LENGTH | S1   | PAYLOAD | STATIC                                    |
Radio packet in RAM                            |------|--------|------|---------|-------------------------------------------|
                                               | None | None   | None | None    | 10 Bytes                                  |
                                    +----------+--------------------------------+-------------------------------------------+
                                    | Preamble |                                | Access Addr  | PDU Header | Payload | CRC |
BLE LL packet                       |----------|                                |--------------|------------|---------|-----|
                                    | 0xAA     |                                | 4 Bytes      | 2 Bytes    | None    | 3 B |
                                    +----------+                                +-------------------------------------------+
```



## References
1. Promiscuity is the nRF24L01+’s Duty
1. nRF24L01+ Single Chip 2.4GHz Transceiver Product Specification v1.0, 7.3.7 Automatic packet disassembly
1. BLUETOOTH SPECIFICATION Version 4.2, [Vol 6, Part A] page 19, 4 RECEIVER CHARACTERISTICS
1. BLUETOOTH SPECIFICATION Version 4.2, [Vol 6, Part A] page 19, 4.1 ACTUAL SENSITIVITY LEVEL
1. DEF CON 25 – Damien Cauquil – Weaponizing the BBC Micro Bit
1. DEF CON 26 – Damien virtualabs Cauquil – You had better secure your BLE devices
1. virtualabs/btlejack-firmware
1. virtualabs/btlejack