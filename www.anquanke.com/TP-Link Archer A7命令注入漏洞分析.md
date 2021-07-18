
# TP-Link Archer A7命令注入漏洞分析


                                阅读量   
                                **470477**
                            
                        |
                        
                                                                                                                                    ![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者thezdi，文章来源：thezdi.com
                                <br>原文地址：[https://www.thezdi.com/blog/2020/4/6/exploiting-the-tp-link-archer-c7-at-pwn2own-tokyo](https://www.thezdi.com/blog/2020/4/6/exploiting-the-tp-link-archer-c7-at-pwn2own-tokyo)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/202671/t0165f9cf2afadc9b3d.jpg)](./img/202671/t0165f9cf2afadc9b3d.jpg)



## 0x00 前言

在2019年Pwn2Own Tokyo比赛中，有研究人员使用了TP-Link Archer A7中的一个命令注入漏洞，本文介绍了该漏洞的具体细节。

该漏洞位于`tdpServer`（`/usr/bin/tdpServer`）守护进程中，这是运行在TP-Link Archer A7（AC1750）路由器上的一个进程，这款设备的硬件版本号为5，采用MIPS架构，固件版本为190726。攻击者必须处于路由器的LAN网络中才能利用该漏洞，但利用过程不需要经过身份认证。漏洞利用成功后，攻击者可以以`root`权限执行任意命令，包括下载和执行二进制程序。该漏洞对应的编号为CVE-2020-10882，TP-Link官方发布了[A7(US)_V5_200220](https://www.tp-link.com/us/support/download/archer-a7/)版固件，修复了该漏洞。

本文研究的固件版本为190726，涉及到的所有函数偏移地址及代码片段均以`/usr/bin/tdpServer`作为参考。



## 0x01 tdpServer

`tdpServer`进程的监听地址为`0.0.0.0`，使用UDP端口`20002`。目前我们尚未完全澄清该守护进程的所有功能，但这并不影响漏洞利用。该进程似乎是用来建立TP-Link移动应用以及路由器之间的桥梁，以便用户能从移动应用端控制路由器。

该进程会使用UDP数据包与移动应用通信，数据包载荷经过加密处理。我们还原出了数据包格式，如下所示：

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01140c4ef557e585d3.png)

图1. 逆向出的`tdpServer`数据包格式

数据包类型用来决定守护进程中哪个服务将会被调用。如果类型为`1`，则进程会调用`tdpd`服务，该服务将简单返回带有特定`TETHER_KEY`哈希值的响应数据包。由于这与漏洞不相关，因此我们并没有深入分析这方面内容。

其他可能使用的类型值为`0xf0`，该值将会调用`onemesh`服务，这也正是漏洞所在的服务。

[OneMesh](https://www.tp-link.com/us/onemesh/compatibility/)似乎是TP-Link在最近几款路由器最新固件中引入的一种专有mesh（网格）技术。

关于数据包中其他字段的功能，大家可参考上图中的注释部分。



## 0x02 漏洞成因

当设备启动时，首先会调用的第一个相关函数就是`tdpd_pkt_handler_loop()`（offset `0x40d164`），该函数会在`20002`端口上打开UDP监听socket。当收到数据包时，该函数会将数据包传递给`tpdp_pkt_parser()`（`0x40cfe0`），后者对应的代码片段如下所示：

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014de378295c9eb73e.png)

图2. `tdpd_pkt_parser()`代码片段1

在第一个代码片段中，可以看到解析函数首先会检查UDP socket反馈的数据包大小是否大于等于`0x10`（该值为头部结构的大小），随后，该函数会调用`tdpd_get_pkt_len()`（`0x40d620`），后者会返回数据包头部中声明的数据包大小（`len`字段）。如果数据包长度超过了`0x410`，则该函数会返回`-1`。

最后，解析函数会调用`tdpd_pkt_sanity_checks()`（`0x40c9d0`），执行最后一个检查步骤。该步骤涉及到2处验证，这里为简洁起见，我们没有列出相关代码。代码首先会检查数据包版本（`version`字段，即数据包的第1个字节）是否等于`1`，然后使用自定义的校验和函数（`tpdp_pkt_calc_checksum()`，offset `0x4037f0`）来计算数据包的校验和。

为了更好理解这个过程，我们来看一下`calc_checksum()`函数，如下所示，该函数是`lao_bomb`漏洞利用代码中的一个函数。这个函数理解起来比较简单，因此我们没有直接放出`tpdp_pkt_calc_checksum()`的代码。

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b350701af4a88463.png)

图3. `lao_bomb`利用代码中的`calc_checksum()`函数

校验和计算过程其实比较简单。首先，代码会将数据包`checksum`字段的值设置为一个魔术值`0x5a6b7c8d`，然后使用了`reference_tbl`（大小为`1024`字节的一张表），以便处理整个数据包（包括头部）来计算校验和。

当检查完校验和，一切正确后，`tdpd_pkt_sanity_checks()`会返回`0`，然后再回到`tdpd_pkt_parser()`后续代码。

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012cd30af7e6854257.png)

图4. `tdpd_pkt_parser()`代码片段2

这里代码会检查数据包的第2个字节（`type`字段），判断该字段是否等于`0`（`tdpd`）或者`0xf0`（`onemesh`）。在下一个分支中，代码还会检查全局变量`onemesh_flag`是否设置为`1`（这也是默认值）。我们需要跟进这个分支，然后我们会进入`onemesh_main()`函数（`0x40cd78`）。

这里为了简洁起见，我们并没有列出`onemesh_main()`的代码。该函数的任务是根据数据包的`opcode`字段来调用另一个函数。为了执行到存在漏洞的函数，`opcode`字段值必须设置为`6`，`flags`字段值必须设置为`1`。在这种情况下，代码会调用`onemesh_slave_key_offer()`函数（`0x414d14`）。

这也是我们发现的存在漏洞的函数，并且代码比较长，我们只列出了相关的部分代码。

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dc026ab373bacfbd.png)

图5. `onemesh_slave_key_offer()`代码片段1

在`onemesh_slave_key_offer()`的第1个代码片段中，可以看到代码会将数据包载荷传递给`tpapp_aes_decrypt()`（`0x40b190`）。这里我们就不展示这个函数代码了，大家根据函数名及参数很容易能猜出该函数的功能。该函数会使用AES算法来解密数据包载荷，密钥为`TPONEMESH_Kf!xn?gj6pMAt-wBNV_TDP`。

在`lao_bomb`利用代码中的加密过程比较复杂，后面我们会详细说明。

现在，我们可以先认为`tpapp_aes_decrypt`已经成功解密处数据包，因此可以转到`onemesh_slave_key_offer()`中其他相关代码：

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01aa9b996ce32c5990.png)

图6. `onemesh_slave_key_offer()`代码片段2

在这个代码片段中，当调用其他函数后（主要是关于`onemesh`对象的初始化操作），代码开始解析实际的数据包载荷。

代码希望处理的载荷为JSON对象，格式如下所示：

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014cbe3c04ebb9cf46.png)

图7. `onemesh_slave_key_offer()`涉及的典型JSON载荷

在图6中，我们可以看到代码首先会获取`method` JSON键值，然后开始解析`data` JSON对象。

如下代码片段所示，`data`对象的每个键都会被顺序处理。如果所需的某个键不存在，函数就会直接退出。

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011d6100c7d8ba9a4c.png)

图8. `onemesh_slave_key_offer()`代码片段3

如上图所示，每个JSON键的值都会被解析，然后拷贝到一个栈变量中（如`slaveMac`、`slaveIp`等）。

解析完成JSON对象后，函数会调用`create_csjon_obj()`（`0x405fe8`），开始准备响应数据包。

从此处开始，函数会对收到的数据执行各种操作。比较关键的部分如下所示：

[![](./img/202671/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013f7e43bb02e65545.png)

图9. `onemesh_slave_key_offer()`代码片段4

这正是漏洞存在的位置。回到上文图8处，我们可以看到JSON键`slave_mac`的值会被拷贝到栈变量`slaveMac`中。在图9中，`slaveMac`会被`sprintf`拷贝到`systemCmd`变量中，后者会被传递给`system()`函数。



## 0x03 漏洞利用

### <a class="reference-link" name="%E6%89%A7%E8%A1%8C%E5%88%B0%E6%BC%8F%E6%B4%9E%E5%87%BD%E6%95%B0"></a>执行到漏洞函数

首先我们需要澄清如何让进程执行到这个命令注入位置。经过反复试验后，我们发现如果发送图7所示的JSON结构，那么进程总会执行到存在漏洞的代码路径。更具体一些，对应的方法必须为`slave_key_offer`，且`want_to_join`必须为`false`，其他值可以任意选择（虽然字段中如果使用了除`slave_mac`之外的其他特殊字符，可能导致漏洞函数提前退出，不处理我们的注入请求）。

对于数据包头，如前文所述，我们必须将`type`设置为`0xf0`，`opcode`设置为`6`，`flags`设置为`1`，并且要正确填充`checksum`字段。

### <a class="reference-link" name="%E5%8A%A0%E5%AF%86%E6%95%B0%E6%8D%AE%E5%8C%85"></a>加密数据包

如前文所述，数据包会使用AES算法进行加密，密钥固定为`TPONEMESH_Kf!xn?gj6pMAt-wBNV_TDP`。然而这里还有一些信息需要补充。该算法采用CBC模式，IV为固定值：`1234567890abcdef1234567890abcdef`。此外，尽管设备使用的是256位密钥及IV，算法实际使用的是AES-CBC，密钥为128位，因此有一半密钥及IV并没有被使用。

### <a class="reference-link" name="%E5%AE%9E%E7%8E%B0%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C"></a>实现代码执行

现在我们已经知道如何执行到存在漏洞的代码路径，我们能否发送带有命令的一个数据包，实现代码执行？这里我们需要解决两个问题：

1、`strncpy()`只会拷贝`slave_mac_info`中的`0x11`个字节，将其拷贝到`slaveMac`变量，其中还包括用作结尾的null字节。

2、由于`slaveMac`中的值被单引号和双引号封装，因此我们需要执行一些转义操作。

考虑到这2个限制条件，我们实际可用的空间非常有限。

为了转义参数，执行载荷，我们需要添加如下字符：

```
';&lt;PAYLOAD&gt;'
```

这里我们浪费了3个字符空间，因此只剩下13个字节来构造载荷，这种情况下我们几乎不可能执行有意义的命令。

此外，经过测试后，我们发现可用空间实际上会被限制为12个字节。这里我们并不清楚具体原因，但似乎与字符转义有关。

我们的解决方案是多次触发bug，在目标设备上逐字符构建所需的命令文件。然后在最后一次触发bug时，我们将命令文件作为shell脚本来执行。然而即使采用这种方式，整个过程也比我们想象中的要难。

比如，如果我们想将字符`a`附加到名为`z`的文件中，我们可以简单执行如下命令：

```
cat 'a'&gt;&gt;z
```

现在即使这种简单场景也需要使用10个字节。

如果想写入数字，那么就无法使用上述方式。这是因为shell会将数字解析为文件描述符。同样，`.`或者`;`之类的特殊字符也会被shell解释，无法使用上述方法。为了处理这些情况，我们需要执行如下命令：

```
printf '1'&gt;x
```

大家可能会注意到，上述命令不会将字符附加到已有文件中，而是会创建名为`x`的一个新文件（覆盖已有该名称的任意文件），文件内容仅包含字符`1`。由于这个载荷已占用12个字节，因此我们无法再添加`&gt;`字符，也就无法将`1`附加到我们的目标文件中。

然而我们还是有解决方案。每次我们需要输出数字或者特殊字符时，我们首先将字符写入一个新文件，然后使用`cat`命令将该文件的内容附加到正在构建的命令文件中：

```
cat x*&gt;&gt;z*
```

这里大家可能会好奇为什么每个文件名后都需要`*`字符。这是因为尽管我们能转义我们发送的命令，但待执行的lua脚本最后几个字节会以文件名结尾。这意味着当我们尝试创建名为`z`的文件时，实际上该文件会被命名为`‘z”})’`。如果将完整的文件名加到命令中，会占用太多个字节。幸运的是，我们可以使用`*`特殊字符，由shell自动补全该信息。

有些读者可能会注意到我们没有将路径改为`/tmp`，由于许多嵌入式设备文件系统根目录不可写，因此这是必要的一个操作。然而这里我们还是很幸运，设备的根文件系统采用读写方式挂载，这也是TP-Link在安全性上犯下的一个大错。如果文件系统以只读模式挂载（如使用SquashFS文件系统的大多数嵌入式设备一样），此时由于添加`cd tmp`会占用太多字节，我们将无法顺利发起该攻击。

采用这些技术，我们已经准备好执行任意命令所需的所有工具。我们将逐字节发送命令，将命令逐一添加到命令文件`z`中，然后再发送如下载荷：

```
sh z
```

这样我们的命令文件将以`root`权限执行，随后我们就能下载并执行文件，具备路由器的完整控制权限。
