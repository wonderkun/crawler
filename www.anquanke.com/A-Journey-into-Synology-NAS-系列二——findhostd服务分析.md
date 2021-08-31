> 原文链接: https://www.anquanke.com//post/id/251909 


# A-Journey-into-Synology-NAS-系列二——findhostd服务分析


                                阅读量   
                                **24713**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0114a0d4fa50481a90.jpg)](https://p1.ssl.qhimg.com/t0114a0d4fa50481a90.jpg)



## 前言

上一篇文章主要对群晖`NAS`进行了简单介绍，并给出了搭建群晖`NAS`环境的方法。在前面的基础上，本篇文章将从局域网的视角出发，对群晖`NAS`设备上开放的部分服务进行分析。由于篇幅原因，本文将重点对`findhostd`服务进行分析，介绍对应的通信机制和协议格式，并分享在其中发现的部分安全问题。



## 服务探测

由于`NAS`设备是网络可达的，假设我们与其处于同一个局域网中，首先对设备上开放的端口和服务进行探测。简单起见，这里直接通过`netstat`命令进行查看，如下。

[![](https://p4.ssl.qhimg.com/t01851015447d58cfe1.png)](https://p4.ssl.qhimg.com/t01851015447d58cfe1.png)

可以看到，除了一些常见的服务如`smbd`、`nginx`、`minissdpd`和`snmpd`等，还有一些自定义的服务如`synovncrelayd`、`iscsi_snapshot_comm_core`、`synosnmpd`和`findhostd`等。与常见服务相比，这些自定义的服务可能`less tested and more vulnerable`，因此这里主要对这些自定义服务进行分析，包括`findhostd`和`iscsi_snapshot_comm_core`。



## findhostd服务分析

`findhostd`服务主要负责和`Synology Assistant`进行通信，而`Synology Assistant`则用于在局域网内搜索、配置和管理对应的`DiskStation`，比如安装`DSM`系统、设置管理员账号/密码、设置设备获取`IP`地址的方式，以及映射网络硬盘等。

通过抓包分析可知，`Synology Assistant`和`findhostd`之间主要通过`9999/udp`端口(`9998/udp`、`9997/udp`)进行通信，一个简单的通信流程如下。具体地，`Synology Assistant`首先发送一个广播`query`数据包，之后`findhostd`会同时发送一个广播包和单播包作为响应。在发现对应的设备后，`Synology Assistant`可以进一步发送其他广播包如`quickconf`、`memory test`等，同样`findhostd`会发送一个广播包和单播包作为响应。

[![](https://p5.ssl.qhimg.com/t010d3dc9738c3dbf77.png)](https://p5.ssl.qhimg.com/t010d3dc9738c3dbf77.png)

抓取的部分数据包如上图右侧所示。可以看到，两者之间通过`9999/udp`端口进行通信，且数据似乎以明文方式进行传输，其中包括`mac`地址、序列号和型号等信息。

### <a class="reference-link" name="%E5%8D%8F%E8%AE%AE%E6%A0%BC%E5%BC%8F%E5%88%86%E6%9E%90"></a>协议格式分析

为了了解具体的协议格式，需要对`findhostd`(或`Synology Assistant`客户端)进行逆向分析和调试。经过分析可知，消息开头部分是`magic` (`\x12\x34\x56\x78\x53\x59\x4e\x4f`)，然后存在一大段与协议格式相关的数据`grgfieldAttribs`，表明消息剩余部分的格式和含义。具体地，下图右侧中的每一行对应结构`data_chunk`，其包含6个字段。其中，`pkt_id`字段表明对应数据的含义，如数据包类型、用户名、`mac`地址等；`offset`字段对应将数据放到内部缓冲区的起始偏移；`max_length`字段则表示对应数据的最大长度。

[![](https://p4.ssl.qhimg.com/t01150e698e70529c40.png)](https://p4.ssl.qhimg.com/t01150e698e70529c40.png)

根据上述信息，可以将数据包按下图格式进行解析。具体地，消息开头部分为`magic` (`\x12\x34\x56\x78\x53\x59\x4e\x4f`)，后面的部分由一系列的`TLV`组成，`TLV`分别对应`pkt_id`、`data_length`和`data`。

[![](https://p5.ssl.qhimg.com/t01829414c19af1960b.png)](https://p5.ssl.qhimg.com/t01829414c19af1960b.png)

进一步地，为了更方便地对数据包格式进行分析，编写了一个`wireshark`协议解析插件[syno_finder](https://github.com/cq674350529/pocs_slides/tree/master/scripts/wireshark_plugins/syno_finder)，便于在`wireshark`中直接对数据包进行解析，效果如下图所示。

[![](https://p2.ssl.qhimg.com/t01e2b0e66614e158e2.png)](https://p2.ssl.qhimg.com/t01e2b0e66614e158e2.png)

需要说明的是，在较新版本的`Synology Assistant`和`DSM`中，增加了对数据包加密的支持(因为其中可能会包含敏感信息)。对应地，存在两个`magic`，分别用于标识明文消息和密文消息。同时，引入了几个新的`pkt_id`，用于传递与加解密相关的参数。

```
// magic
#define magic_plain “\x12\x34\x56\x78\x53\x59\x4e\x4f”
#define magic_encrypted “\x12\x34\x55\x66\x53\x59\x4e\x4f” // introduced recently

// new added
000000c3  00000001  00002f48  00000004  00000000  00000000      # support_onsite_tool
000000c4  00000000  00002f4c  00000041  00000000  00000000      # public key
000000c5  00000001  00002f90  00000004  00000000  00000000      # randombytes
000000c6  00000001  00002f94  00000004  00000000  00000000
```

### <a class="reference-link" name="%E5%8D%8F%E8%AE%AEfuzzing"></a>协议fuzzing

在了解了协议的格式之后，为了测试协议解析代码的健壮性，很自然地会想到采用`fuzz`的方式。这里采用`Kitty`和`Scapy`框架，来快速构建一个基于生成的黑盒`fuzzer`。`Scapy`是一个强大的交互式数据包处理程序，借助它可以方便快速地定义对应的协议格式，示例如下。

```
class IDPacket(Packet):
    fields_desc = [
        XByteField('id', 0x01),
        FieldLenField('length', None, length_of='value', fmt='B', adjust=lambda pkt,x:x),
        StrLenField('value', '\x01\x00\x00\x00', length_from=lambda x:x.length)
    ]

    # ...

    def post_build(self, pkt, pay):
        if pkt[1] != 4 and pkt[1] != 0xff:
            packet_max_len = self._get_item_max_len(pkt[0])
            if len(pkt[2:]) &gt;= packet_max_len:
                if packet_max_len == 0:
                    pkt = bytes([pkt[0], 0])
                else:
                    pkt = bytes([pkt[0], packet_max_len-1])+ pkt[2:2+packet_max_len]
        return pkt + pay

class FindHostPacket(Packet):
    fields_desc = [
        StrLenField('magic_plain', '\x12\x34\x56\x78\x53\x59\x4e\x4f'),
        PacketListField('id_packets', [], IDPacket)
    ]
```

[Kitty](https://github.com/cisco-sas/kitty)是一个开源、模块化且易于扩展的`fuzz`框架，灵感来自于`Sulley`和`Peach Fuzzer`。基于前面定义的协议格式，借助`Kitty`框架，可以快速地构建一个基于生成的黑盒`fuzzer`。另外，考虑到`findhostd`和`Synology Assistant`之间的通信机制，可以同时对两端进行`fuzz`。

```
host = '&lt;broadcast&gt;'
port = 9999
RANDSEED = 0x11223344

packet_id_a4 = qh_nas_protocols.IDPacket(id=0xa4, value='\x00\x00\x02\x01')
# ...
packet_id_2a = qh_nas_protocols.IDPacket(id=0x2a, value=RandBin(size=240))
# ...
pakcet_id_rand1 = qh_nas_protocols.IDPacket(id=RandByte(), value=RandBin(size=0xff))
pakcet_id_rand2 = qh_nas_protocols.IDPacket(id=RandChoice(*qh_nas_protocols.PACKET_IDS), value=RandBin(size=0xff))

findhost_packet = qh_nas_protocols.FindHostPacket(id_packets=[packet_id_a4, packet_id_2a, ..., packet_id_rand1, packet_id_rand2])

findhost_template = Template(name='template_1', fields=[ScapyField(findhost_packet, name='scapy_1', seed=RANDSEED, fuzz_count=100000)])

model = GraphModel()
model.connect(findhost_template)

target = UdpTarget(name='qh_nas', host=host, port=port, timeout=2)

fuzzer = ServerFuzzer()
fuzzer.set_interface(WebInterface(host='0.0.0.0', port=26001))
fuzzer.set_model(model)
fuzzer.set_target(target)
fuzzer.start()
```

此外，基于前面定义好的协议格式，也可以实现一个简易的`Synology Assistant`客户端。

```
class DSAssistantClient:
    # ...
    def add_pkt_field(self, pkt_id, value):
        self.pkt_fields.append(qh_nas_protocols.IDPacket(id=pkt_id, value=value))

    def clear_pkt_fields(self):
        self.pkt_fields = []

    def find_target_nas(self):
        self.clear_pkt_fields()

        self.add_pkt_field(0xa4, '\x00\x00\x02\x01')
        self.add_pkt_field(0xa6, '\x78\x00\x00\x00')
        self.add_pkt_field(0x01, p32(0x1))    # packet type
        # ...
        self.add_pkt_field(0xb9, '\x00\x00\x00\x00\x00\x00\x00\x00')
        self.add_pkt_field(0x7c, '00:50:56:c0:00:08')

        self.build_send_packet()

    def quick_conf(self):
        self.clear_pkt_fields()

        self.add_pkt_field(0xa4, '\x00\x00\x02\x01')
        self.add_pkt_field(0xa6, '\x78\x00\x00\x00')
        self.add_pkt_field(0x01, p32(0x4))    # packet type
        self.add_pkt_field(0x20, p32(0x1))    # packet subtype

        self.add_pkt_field(0x19, '00:11:32:8f:64:3b')
        self.add_pkt_field(0x2a, 'BnvPxUcU5P1nE01UG07BTUen1XPPKPZX')
        self.add_pkt_field(0x21, 'NAS_NEW')
        # ...
        self.add_pkt_field(0xb9, "\x00\x00\x00\x00\x00\x00\x00\x00")
        # ...
        self.add_pkt_field(0x7c, "00:50:56:c0:00:08")

        self.build_send_packet()

    # ...

if __name__ == "__main__":
    ds_assistant = DSAssistantClient("ds_assistant")
    ds_assistant.find_target_nas()
    # ...
```

### <a class="reference-link" name="%E5%AE%89%E5%85%A8%E9%97%AE%E9%A2%98"></a>安全问题

<a class="reference-link" name="%E5%AF%86%E7%A0%81%E6%B3%84%E9%9C%B2"></a>**密码泄露**

前面提到，`pkt_id`字段表明对应数据的含义，如数据包类型、用户名、`mac`地址等。其中，`pkt_id`为`0x1`时对应的值表示整个数据包的类型，常见的数据包类型如下。其中，`netsetting`、`quickconf`和`memory test`数据包中包含加密后的管理员密码信息，对应的`pkt_id`为`0x2a`。

[![](https://p5.ssl.qhimg.com/t01a9e65dcd3fb68961.png)](https://p5.ssl.qhimg.com/t01a9e65dcd3fb68961.png)

[![](https://p0.ssl.qhimg.com/t01432a6e15885c7e13.png)](https://p0.ssl.qhimg.com/t01432a6e15885c7e13.png)

以`quickconf`数据包为例，如上图所示。可以看到，`pkt_id`为`0x1`时对应的值为`0x4`，同时`pkt_id`为`0x2a`时对应的内容为`BnvPxUcU5P1nE01UG07BTUen1XPPKPZX`。通过逆向分析可知，函数`MatrixDecode()`用于对加密后的密码进行解密。因此，可以很容易地获取到管理员的明文密码。

```
~/DSM_DS3617xs_15284/hda1$ sudo chroot . ./call_export_func -d BnvPxUcU5P1nE01UG07BTUen1XPPKPZX
MatrixDecode(BnvPxUcU5P1nE01UG07BTUen1XPPKPZX) result: HITB2021AMS
```

由于`Synology Assistant`和`findhostd`之间以广播的方式进行通信，且数据包以明文形式进行传输，在某些情形下，通过监听广播数据包，局域网内的用户可以很容易地获取到管理员的明文密码。

<a class="reference-link" name="%E5%AF%86%E7%A0%81%E7%AA%83%E5%8F%96"></a>**密码窃取**

在对`findhostd`进行`fuzz`的过程中，注意到`Synology Assistant`中显示的`DiskStation`状态变为了`"Not configured"`。难道是某些畸形数据包对`DiskStation`进行了重置？经过分析后发现，是由于某些数据包欺骗了`Synology Assistant`：`DiskStation`是正常的，而`Synology Assistant`却认为其处于未配置状态。

[![](https://p1.ssl.qhimg.com/t01e06e94a2dc6829f1.png)](https://p1.ssl.qhimg.com/t01e06e94a2dc6829f1.png)

通常情况下，管理员会选择通过`Synology Assistant`对设备进行重新配置，并设置之前用过的用户名和密码。此时，由于`Synology Assistant`和`findhostd`之间以广播的方式进行通信，且数据包以明文形式进行传输，故密码泄露问题又出现了。因此，在某些情形下，通过发送特定的广播数据包，局域网内的用户可以欺骗管理员对`DiskStation`进行”重新配置”，通过监听局域网内的广播数据包，从而窃取管理员的明文密码。另外，即使`Synology Assistant`和`DSM`版本都支持通信加密，由于向下兼容性，这种方式针对最新的版本仍然适用。

<a class="reference-link" name="null%20byte%20off-by-one"></a>**null byte off-by-one**

这个问题同样也和`Synology Assistant`有关。在`fuzz`的过程中，发现`Synology Assistant`中显示的一些内容比较奇怪。其中，`"%n"`、`"%x"`和`"%p"`等是针对`string`类型预置的一些`fuzz`元素。注意到，在`"Server name"`中显示的内容除了`"%n"`之外，尾部还有一些额外的内容如`"00:11:32:8Fxxx"`，这些多余的内容对应的是`"MAC address"`。正常情况下，`"MAC address"`对应的内容不会显示到`"Server name"`中。

[![](https://p2.ssl.qhimg.com/t01742891d3b982f566.png)](https://p2.ssl.qhimg.com/t01742891d3b982f566.png)

通过对`6.1-15030`版本的`DSAssistant.exe`进行分析和调试，函数`sub_1272E10()`负责对`string`类型的数据进行处理，将其从接收的数据包中拷贝到对应的内部缓冲区。前面提到过，针对每个`pkt_id`项，都有一个对应的`offset`字段和`max_length`字段。当对应数据长度的大小正好为`max_length`时，额外的`'\x00'`在`(1)`处被追加到缓冲区末尾，而此时该`'\x00'`其实是写入了邻近缓冲区的起始处，从而造成`null byte off-by-one`。

```
size_t __cdecl sub_1272E10(int a1, _BYTE *a2, int a3, int a4, size_t a5, int a6, int a7)
`{`
  // ...
  v7 = (unsigned __int8)*a2;
  if ( (int)v7 &gt; a3 - 1 )
    return 0;
  if ( !*a2 )
    return 1;
  if ( a5 &lt; v7 )
    return 0;
  snprintf((char *)(a4 + a7 * a5), v7, "%s", a2 + 1);    // 将string类型的数据拷贝到内部缓冲区的指定偏移处
  *(_BYTE *)(v7 + a4) = 0;   // (1) null byte off-by-one
  return v7 + 1;
`}`
```

> The `_snprintf()` function formats and stores count or fewer characters and values (including a terminating null character that is always appended **unless count is zero or the formatted string length is greater than or equal to count characters**) in buffer. // Windows
The functions `snprintf()` and `vsnprintf()` **write at most size bytes (including the terminating null byte (‘\0’))** to str. // Linux

因此，对于某些在内部缓冲区中处于邻近的`pkt_id`(如`0x5b`和`0x5c`)，通过构造特殊的数据包，可以使得前一项内容末尾的`'\x00'`被下一项内容覆盖，从而可能会泄露邻近缓冲区中的内容。

```
pkt_id            offset  max_len
0000005a 00000000 00000aa8 00000080 00000000 00000000
0000005b 00000000 00000b28 00000080 00000000 00000000    &lt;===
0000005c 00000000 00000ba8 00000004 00000000 00000000
```



## 小结

本文从局域网的视角出发，对群晖`NAS`设备上的`findhostd`服务进行了分析，包括`Synology Assistant`与`findhostd`之间的通信机制、`syno_finder`协议格式的解析、协议`fuzzing`等。最后，分享了在其中发现的部分问题。



## 相关链接
- [Create Wireshark Dissector in Lua](https://cq674350529.github.io/2020/09/03/Create-Wireshark-Dissector-in-Lua/)
- [syno_finder](https://github.com/cq674350529/pocs_slides/tree/master/scripts/wireshark_plugins/syno_finder)
- [Kitty Fuzzing Framework](https://github.com/cisco-sas/kitty)
- [Synology-SA-19:38 Synology Assistant](https://www.synology.cn/zh-cn/security/advisory/Synology_SA_19_38)