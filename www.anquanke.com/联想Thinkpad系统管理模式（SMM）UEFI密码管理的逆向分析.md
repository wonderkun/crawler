> 原文链接: https://www.anquanke.com//post/id/208117 


# 联想Thinkpad系统管理模式（SMM）UEFI密码管理的逆向分析


                                阅读量   
                                **158497**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者synacktiv，文章来源：synacktiv.com
                                <br>原文地址：[https://www.synacktiv.com/posts/reverse-engineering/a-journey-in-reversing-uefi-lenovo-passwords-management.html](https://www.synacktiv.com/posts/reverse-engineering/a-journey-in-reversing-uefi-lenovo-passwords-management.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01462714eddf324bef.jpg)](https://p3.ssl.qhimg.com/t01462714eddf324bef.jpg)



## 一、前言

在上一篇文章中，我重点说明了联想Thinkpad系统管理模式（SMM）代码中存在的漏洞。在进行漏洞分析的过程中，我非常好奇在其中是如何处理UEFI密码的，特别是用于保护BIOS接口的密码。为此，我找到了一些参考文章，但是我更倾向于从软件的角度对其进行研究，以确定是否属于相同的实现方法。根据构造函数的不同，不同设备上对密码的处理方式也有所不同，因此在本文中分析的代码仅适用于联想设备，更确切地说是仅适用于特定ThinkPad型号。但是，由于我尝试了三个不同版本的ThinkPad，发现这部分是通用的，因此我推断大部分ThinkPad可能都会适用。

在这篇文章中，我将重点说明我是如何查看到联想设备中的密码。首先，我们将尝试开展逆向，尝试找到固件中的各种密码，然后再更加深入地研究其中的开机密码和BIOS密码。在这些密码的管理机制中，我们没有发现任何漏洞，但其中的分析过程可能会对大家有所帮助。事不宜迟，我们赶快开始。



## 二、初始逆向过程

联想ThinkPad固件中包含几种不同的密码，最开始我感兴趣的是BIOS设置界面的保护密码。在固件中的一些驱动程序，包含对字符串“password”的引用。最开始，我关注的是`LenovoSetupSecurityDxe`，因为该驱动程序中似乎集中了大多数代码，这些代码允许使用用户界面设置和删除密码。

### <a class="reference-link" name="2.1%20%E9%80%86%E5%90%91HII"></a>2.1 逆向HII

在UEFI中，使用了人机界面基础结构（HII）与用户进行交互，这是一组接口，允许打印内容并从用户那里获取值。其中，`EFI_HII_STRING_PROTOCOL`允许使用`StringId`（一个简单地数字）从“数据库”中检索字符串。基本上这就意味着我们在你想过程中，不可能直接在字符串中使用xref。在数据库中找到的字符串很容易识别，它们都是UTF-16字符串，后面接着一个字节，值为0x14。这个值表明HII数据库的这一元素是字符串。在所有这些字符串的前面，都有一个标头。标头遵循`EFI_HII_STRING_PACKAGE_HDR`结构，该结构中包含一个`StringInfoOffset`字段，该字段指示着字符串的开头。

一旦找到标头，我们就可以找到数据库的初始化。其中，会调用函数`gEfiHiiDatabaseProtocolInterface-&gt;NewPackageList`，该函数允许使用句柄注册数据库字符串。然后，其余代码将使用这个句柄和`StringId`来检索字符串，通常是通过调用`gEfiHiiStringProtocolInterface-&gt;GetString`来实现的。

我们通过追踪字符串的使用情况，就可以确定代码的哪一部分是用于哪些活动，再加之进行一些逆向之后，可以识别出一些值得关注的全局变量。

### <a class="reference-link" name="2.2%20%E8%81%94%E6%83%B3%E5%AF%86%E7%A0%81%E5%8D%8F%E8%AE%AE"></a>2.2 联想密码协议

实际上，用于操作和检查密码的全局变量是一些协议。这些协议可以通过以下伪代码来获取：

```
result = gBootServices-&gt;LocateHandleBuffer(ByProtocol, &amp;LenovoPwdGuid, 0, &amp;NoHandles, &amp;ControllerHandle); // (1)
if (!EFI_ERROR(result))
`{`
  for (i = 0; i &lt; NoHandles; ++i)
  `{`
    if (!EFI_ERROR(gBootServices-&gt;OpenProtocol(ControllerHandle[i], &amp;LenovoPwdGuid, &amp;Interface, AgentHandle, 0, 1)) `{` // (2)
        if (CmpGuid(Interface, Guid1)) `{` // (3)
            global1 = Interface; // (4)
        `}`
        // [...] : Same with other Guid and global
    `}`

  `}`
`}`
// [...]
```

这段代码并不是仅仅搜索一个协议，而是搜索其中的几个协议，所有协议都具有相同的GUID `LenovoPwdGuid`（2846b2a8-77c8-4432-86ec-199f205d37ca）[1]，它会检索每一个接口[2]，并将接口的开头与硬编码的GUID（在这里我们将其称为Guid1）进行比较[3]。根据GUID，使用相应的全局变量来存储该接口[4]。以这样的方式，设置了四个不同的全局变量。

这表明，几个不同的协议都安装了相同的GUID，然后通过比较接口结构开始处存在的另一个GUID来区分这些协议。这些接口中的每一个都代表不同类型的密码，并且在初始GUID之后，提供了用于操作它们的功能。

### <a class="reference-link" name="2.3%20%E5%AF%86%E7%A0%81%E7%B1%BB%E5%9E%8B%E5%92%8C%E6%8E%A5%E5%8F%A3"></a>2.3 密码类型和接口

通过搜索用于比较结构的硬编码GUID，我们仅仅发现了一些二进制文件。这四个驱动程序的名称非常有趣，分别是：LenovoPopManagerDxe、LenovoSvpManagerDxe、LenovoHdpManagerDxe和LenovoSmpManagerDxe。通过查看调试字符串，我们很容易猜出这些缩写的含义：

POP：Power-On Password（开机密码）

SVP：SuperVisor Password（超级管理员密码）

HDP：HardDisk Password（硬盘密码）

SMP：System Management Password（系统管理密码）

更有趣的是，SVP和HDP都具有SMM驱动程序。

我们对其中一个驱动程序的用法和代码进行了逆向，从而对GUID之后第一个函数的用法有了更深的理解：

```
struct LenovoPasswordManager `{`
    EFI_GUID    PwdTypeGuid;
    UINT64      unknown;
    EFI_STATUS  (*get_status)(void *this, UINT64 unused, UINT32 *flag_res);
    EFI_STATUS  (*set_pwd)(void *this, char *pwd);
    EFI_STATUS  (*check_pwd)(char *this, char *pwd);
    EFI_STATUS  (*reset_hash)(void *this);
    EFI_STATUS  (*verify_checksum)(void *this);
    void        *unk_func; // not reverse
    void        *unk_func2; // not reverse
`}`;
```

除了`get_status`之外，该接口的所有函数都会执行一些操作，并更改全局共享位字段，以指示结果的状态（`status`）。`get_status`函数允许检索该位字段的值，从而确定用户是否已经提供密码。

在理解这一点之后，我们就可以着手研究更为深入的工作原理。SMP和SVP密码的工作方式几乎相同，我们稍后会对其进行详细说明。此外，HDP已经在另一篇文章中进行了详细分析，在这里我们暂时略去。那么最后，剩下的就只有POP，也就是开机密码。



## 三、开机密码分析

POP是用户可以设置的密码，每次在计算机启动时都会询问。该密码是由`LenovoPopManagerDxe`驱动程序处理，该驱动程序公开了上文描述过的一个接口。

### <a class="reference-link" name="3.1%20%E5%AF%86%E7%A0%81%E5%93%88%E5%B8%8C%E5%92%8CPCD"></a>3.1 密码哈希和PCD

为了查看密码的存储方式，我们可以关注其中的`set_pwd`和`check_pwd`这两个函数。其中函数`set_pwd`首先从计算哈希密码之前参数中给出的指针中检索`0xC`字节。哈希值是利用在`LenovoCryptService`驱动程序中实现的另一个协议（73e47354-b0c5-4e00-a714-9d0d5a4fdbfd）来计算的。该协议中的第一个函数允许计算SHA-256，并作为用于计算密码哈希值的函数。这里的哈希值经过加盐，而盐值通过平台配置数据库（PCD）获取。

PCD是在UEFI PEI和DXE阶段之间传输、在驱动程序之间共享的通用存储系统，PCD协议的实现在edk2中是开源的。PCD允许通过token ID定义共享内存缓冲区，该token ID在固件编译时自动生成。静态存储由驱动程序（一个用于PEI，一个用于DXE）加载，并保存在固件文件系统（FFS）中。可以通过搜索GUID `PCD_DATA_BASE_SIGNATURE_GUID`来轻松找到该存储，它通常与驱动程序位于同一个“文件”中。该协议还提供了动态存储，可以用于在驱动程序之间共享数据。

其中的盐值是使用动态存储。在最近版本的固件中，盐的大小为0x20字节，但以往版本中盐的大小更短，仅有0xA。我们只需要向PCD协议询问正确的token ID，就可以轻松从UEFI Shell中检索盐值。由于token ID是在编译过程中生成的，因此攻击者必须能够自动化确定这个token，或者通过逆向特定固件的驱动程序以找到这个ID。

需要注意的一点是，在释放该驱动程序中用于存储密码和盐的所有缓冲区之前，会将这部分缓冲区置为0x00。要检索密码的哈希值，这个过程不同于在启动后进行内存转储的方式，接下来我们就来深入分析一下它们的存储方式。

### <a class="reference-link" name="3.2%20%E5%AD%98%E5%82%A8"></a>3.2 存储

这里的密码是通过一个允许在存储区中写入字节的函数来实现存储的，通过阅读该函数的代码就可以很好地了解其功能。

```
UINT8 __fastcall write_rtc_storage(UINT8 pos, UINT8 val)
`{`
  UINT8 result;

  if ( pos &gt;= 0x80u )
  `{`
    __outbyte(0x72u, pos + 0x80);
    result = val;
    __outbyte(0x73u, val);
  `}`
  else
  `{`
    __outbyte(0x70u, pos);
    result = val;
    __outbyte(0x71u, val);
  `}`
  return result;
`}`
```

其中，一个`IOPort`用于指示读取或写入的偏移量，另一个`IOPort`用于写入值。读取的工作方式相同，只不过将值的写入（输出）替换为读取（输入）。四个`IOPort` 0x70到0x73是众所周知的，并且可以在文档中找到，它们用于与实时时钟（RTC）设备进行交互。该设备的主要目的是允许访问时间，但是它也提供了一些通常称为CMOS的存储空间。有关这些`IOPort`的更详细信息，可以参考PCH数据表，也可以参考osdev Wiki上面的相关内容。

关于实时时钟（RTC）设备，我们知道，必须要始终供电，以避免丢失其中存储的数据。通常，计算机上会装有一个小电池（与主供电电池不同），以确保该设备始终处于通电状态。这意味着，具有物理访问权限的攻击者只需要中断各种供电，就可以绕过此密码。联想厂商意识到了这一点，并对此进行了记录。<br>
在快速查看了开机密码后，我们开始研究其他密码。



## 四、BIOS配置密码

还有一个密码我们比较感兴趣，就是保护BIOS配置的密码。实际上，SMP和SVP密码的工作原理几乎先沟通。这两个驱动程序公开了前面所述的密码接口，并使用相同的存储。

对于POP，我们可以通过查看`set_pwd`函数的方式来了解其密码存储方式。这一过程从计算输入的哈希值开始，使用了一个与POP一样的SHA-256。

其中值得关注的是，这个哈希值使用的是与POP相同的盐值，但最值得关注的部分是密码的存储方式。

### <a class="reference-link" name="4.1%20%E6%A8%A1%E6%8B%9FEeprom"></a>4.1 模拟Eeprom

在这里，使用的是GUID为82b244dc-8503-454b-a96a-d0d2e00bf86a的协议进行存储，该协议是由驱动程序`EmulatedEepromDxe`注册。根据其显式名称，我们可以推断出这可能是存储API，有趣的是，联想似乎在计算机中嵌入了eeprom。该协议注册了三个函数，但似乎只有前两个是用于密码管理的，这意味着我们可能同时具有读取和写入函数。第一个函数被检查和设置密码的函数使用，而第二个函数仅在设置密码的函数中使用。这似乎非常直接地表明，第一个函数允许读取，第二个函数则允许写入。现在，更关键的问题是，`EmulatedEepromDxe`驱动程序实际上在哪里存储数据呢？

该协议的第一个函数原型如下：

```
EFI_STATUS EmulEeprom_Read(void *this, UINT64 unk_enum, UINT64 index, UINT8 *pRes)
```

第一个参数（`this`）只是协议接口上的指针，最后一个参数（`pRes`）用于检索读取的值，另外的两个参数清晰地指示了要使用的存储空间。这里的`index`是存储空间中的偏移量，但`unk_enum`尚不清楚。与NOR或NAND闪存相反，Eeprom在擦除大小方面可以保持一个非常精准的力度。但是，用于处理小尺寸擦除的电路占用了原本可用于更多存储的空间，所以擦除过程通常是在重新分组的几个字节上进行的。实际上，这就意味着编程接口实际上与NOR或NAND非常相似。这也就是大多数eeprom如今已经被更便宜的NOR或NAND闪存取代的原因之一。在我们的案例中，`unk_enum`实际上是模拟eeprom的库编号，在代码中，这个库编号被转换并添加到`index`编号中，以计算读取或写入时的偏移量。

`EmulEeprom_Read`函数对提供的值进行一些检查，并使用`bank_num`、`index`和`pRes`调用另一个函数`perform_read`。这实际上是执行实际读取的函数，该函数调用在`IOPort`上读写的其他几个函数。而这就是对固件进行逆向的关键点，如果没有记录`IOPort`，逆向过程会非常复杂。因为在这里，实际使用了三种不同的`IOPort`，第一个是0x1808，仅在读取、循环和x86暂停指令后面使用。根据这些特点，我们很容易就意识到，这实际上是一个PM计时器。而在Linux上，通过简单地进行dmesg就能给我们提示——`ACPI: PM-Timer IO Port: 0x1808`。但是，除此之外，另外的两个`IOPort` 0x1630和0x1634就不那么好理解了。

### <a class="reference-link" name="4.2%20%E9%80%86%E5%90%91IOPort"></a>4.2 逆向IOPort

这两个`IOPort`显然用于读取和写入数据，其中一个是用于读取（输出），另一个是用于写入（输入）。0x1634通常使用常量进行写入，而不依赖于偏移量，读取时通常检查结构是否为位字段。而另一个0x1630用于写入先前计算的偏移量和读取实际结果。在其中的一个函数中，将会对这个`IOPort`进行读取，并将结果丢弃。这是与其他硬件设备连接的一种典型模式：一个IOPort作为“配置”，用于检查另一个设备的状态，指示执行的操作类型。而在这里，就是0x1634。第二个`IOPort`（0x1630）是用于读取和写入数据的端口，在`IOPort`上进行读取可能会对设备产生影响（副作用），因此在丢弃结果的同时执行了一次读取。这是使用IOPort与外部设备进行通信的经典模式，基本上与以SPI闪存进行通信、PCI设备接口的工作方式相同。

因此，在这里，我们知道这些密码的哈希值没有存储在SPI闪存中，而是存储在计算机的另一台设备上，因此现在的问题在于，这里使用的两个`IOPort`是可变的，并不是像用于PCI的`IOPort`那样使用了固定的端口。在不同的系统中，使用的端口号也许是不同的，因此要搜寻使用`IOPort`的设备也通常比较复杂。在这里，我首先搜索PCI设备声明的IOPort Base，但是没找到任何结果。接下来，查看在CPU和PCH数据表中定义的变量`IOPort`，在查找了一段时间后，终于在低引脚（LPC）控制器中找到了这些`IOPort`的注册。

低引脚数总线用于与计算机内部的多个设备进行通信，特别是用于与被称为嵌入式控制器（EC）的设备进行通信，该设备在PCH数据表中被简称为“微控制器1”。EC是一种微控制器，主要负责笔记本电脑的供电。之前，我还观看过Alex Matrosov和Alexandre Gazet的演讲“Breaking Through Another Side”，他们在演讲中说明了EC的安全性问题。回顾他们的演讲，我发现其中还引用了这两个`IOPort`，因此密码的哈希值确实存储在EC中。

EC具有其自己的固件，我们在本文将不对其开展过多的分析。但是，我们可以尝试以与驱动程序相同的方式来读取密码。我使用chipsec实现了与EC交互的小脚本，但是当我尝试读取密码的哈希值时，读取到的只有空字节。因为我能够读取其他模拟“存储区”的内容，所以这看上去似乎是一种保护机制——固件可能在引导阶段完成后，锁定对哈希值的访问。

最后，有一件事引起了我的关注，我之前提到，有一个用于SVP密码的SMM驱动程序`LenovoSvpManagerSmm`。由于SMM是与操作系统并行运行的，因此我对于查看SMM如何检索密码哈希值这一点很感兴趣。在进行逆向之后，我发现这个驱动程序使用了`EmulatedEepromDxe`驱动程序的SMM替代品——EmulatedEepromSmm。该驱动程序与`EmulatedEepromDxe`的工作方式相同，并且在相同的`IOPort`上执行相同的操作。但是，`LenovoSvpManagerSmm`实际上是在初始化期间检索哈希值，并将其存储在SMRAM的缓冲区中。这似乎表明，我上一篇文章中提到的SMM漏洞似乎允许检索这些哈希值。

实际上，BIOS固件密码的哈希值是存储在嵌入式控制器中，并且在引导结束后似乎已经锁定。攻击者理论上可以利用UEFI或SMM漏洞来实现攻击，但这是一项非常复杂的任务，其安全性需要基于EC的安全性去保证，但对于EC的安全性就又是另外一项研究了。



## 五、总结

总而言之，我们在研究过程中，发现联想设备对密码的处理方式较为理想，拥有对计算机的硬件访问权限的攻击者理论上可以绕过这些密码，但绕过的过程却不像是我最初预期的那么容易。

用户可以轻易地重置开机密码，这一点上存在问题，但是在重置后仍然需要硬件访问权限来执行后续的操作，或者也可以利用一个固件中存在的漏洞。BIOS密码并没有存储在SPI闪存中，而是存储在EC闪存中，并且引导后似乎已经锁定了读/写访问权限。这意味着，计算机用户在不物理拆卸计算机的情况下，应该无法轻松删除或更改BIOS密码。

还可以看到一个有趣的趋势——被认为是整个系统信任根的UEFI固件越来越多地被其他固件取代。联想似乎将EC用于其安全性的某些部分（不仅仅是其密码），并且管理引擎（ME）和身份验证代码模块（ACM）现在已经成为UEFI固件的信任根。在实际中，这将使得攻击者的攻击过程更加困难，但也同时为攻击者提供了潜在更为广泛的攻击面，改变信任根可能也改变了问题的本质。



## 六、参考

[1] [http://zmatt.net/unlocking-my-lenovo-laptop-part-1/](http://zmatt.net/unlocking-my-lenovo-laptop-part-1/)<br>
[2] [https://github.com/skysafe/reblog/tree/master/0000-defeating-a-laptops-bios-password#messing-with-nvram](https://github.com/skysafe/reblog/tree/master/0000-defeating-a-laptops-bios-password#messing-with-nvram)<br>
[3] [https://jbeekman.nl/site/blog/2015/03/lenovo-thinkpad-hdd-password/](https://jbeekman.nl/site/blog/2015/03/lenovo-thinkpad-hdd-password/)<br>
[4] [https://jbeekman.nl/site/blog/2015/03/reverse-engineering-uefi-firmware/](https://jbeekman.nl/site/blog/2015/03/reverse-engineering-uefi-firmware/)<br>
[5] [https://i.blackhat.com/USA-19/Thursday/us-19-Matrosov-Breaking-Through-Another-Side-Bypassing-Firmware-Security-Boundaries-From-Embedded-Controller.pdf](https://i.blackhat.com/USA-19/Thursday/us-19-Matrosov-Breaking-Through-Another-Side-Bypassing-Firmware-Security-Boundaries-From-Embedded-Controller.pdf)
