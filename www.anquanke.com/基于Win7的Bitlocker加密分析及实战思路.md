> 原文链接: https://www.anquanke.com//post/id/167329 


# 基于Win7的Bitlocker加密分析及实战思路


                                阅读量   
                                **243768**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0130ca2028bf232529.gif)](https://p1.ssl.qhimg.com/t0130ca2028bf232529.gif)

> 本文章将深入讲解Bitlocker的加密机制，并提供实战的思路供读者操作，基于的是windows7下未全盘加密的NTFS文件系统。

## 0x01 示例案例：

Windows 7 SP1 x64



## 0x02 Bitlocker加密分析

### <a name="1.%E6%A6%82%E8%BF%B0"></a>1.概述

BitLocker驱动器加密（BDE）是Microsoft Windows在Vista中使用的volume加密。BitLocker驱动器加密（BDE）有多个版本：
- BitLocker Windows Vista
- TODO: BitLocker Windows 2008
- BitLocker Windows 7
- BitLocker To Go
- BitLocker Windows 8
- BitLocker Windows 10
BitLocker Windows Vista和BitLocker Windows 7都旨在加密固定存储介质（如硬盘）上的NTFS卷。BitLocker To Go是在Windows 7中引入的，旨在加密可移动驱动器，例如FAT文件系统的可移动存储设备(U盘)，可移动驱动器上的NTFS卷被视为固定存储介质上的NTFS卷。

BitLocker标识符(GUID):4967d63b-2e29-4ad8-8399-f6a339e3d0

BitLocker To Go标识符(GUID):4967d63b-2e29-4ad8-8399-f6a339e3d01

### <a name="2.%E5%AF%86%E9%92%A5"></a>2.密钥

BitLocker使用不同类型的密钥加密存储介质。

#### <a name="1%EF%BC%89%E5%8D%B7%E4%B8%BB%E5%AF%86%E9%92%A5%EF%BC%88VMK%EF%BC%89"></a>1）卷主密钥（VMK）

卷主密钥(VMK)的大小为256位，存储在多个FVE卷主密钥(VMK)结构中。VMK存储时使用恢复密钥、外部密钥或TPM加密。

VMK也可能不作为加密密钥存储，这样的VMK称为清除密钥。

#### <a name="2%EF%BC%89%E5%85%A8%E5%8D%B7%E5%8A%A0%E5%AF%86%E5%AF%86%E9%92%A5%EF%BC%88FVEK%EF%BC%89"></a>2）全卷加密密钥（FVEK）

全卷加密密钥（FVEK）使用卷主密钥（VMK）加密存储。FVEK的大小取决于使用的加密方法：
- 对于AES 128位，密钥大小为128位
- 对于AES 256位，密钥大小为256位
当使用Elephant Diffuser时，保存FKEV结构的关键数据大小总是512位。第一个256位用于保存FVEK，另一个256位用于保留TWEAK键。当加密方法为AES 128位时，256位中只有128位被使用。

#### <a name="3%EF%BC%89TWEAK%E5%AF%86%E9%92%A5"></a>3）TWEAK密钥

TWEAK使用卷主密钥（VMK）加密存储。TWEAK密钥的大小取决于使用的加密方法：
- 对于AES 128位，密钥是128位大小
- 对于AES 256位，密钥的大小为256位
TWEAK密钥仅在使用Elephant Diffuser时出现。

#### <a name="4%EF%BC%89%E6%81%A2%E5%A4%8D%E5%AF%86%E9%92%A5"></a>4）恢复密钥

BitLocker提供恢复（或数字）密码来解锁加密数据。恢复密码用于确定恢复密钥。

恢复密码示例：

有效的恢复密码由48位数字组成，分为8组，其中每组数字都可以被11整除，余数为0。每组数字除以11的结果是一个16位的值，单独的16位值组成128位的密钥。

#### <a name="5%EF%BC%89%E6%B8%85%E9%99%A4%E5%AF%86%E9%92%A5"></a>5）清除密钥

清除密钥是存储在卷上的未受保护的256位密钥，用于解密VMK。在解密加密卷时使用它。

### <a name="3.%E5%8A%A0%E5%AF%86%E6%96%B9%E6%B3%95"></a>3.加密方法

BitLocker使用不同类型的加密方法，为了加密扇区数据，它使用带有或不带有Elephant Elephant Diffuser的AES-CBC模式。为了加密密钥数据，BitLocker使用AES-CCM模式。

#### <a name="1%EF%BC%89AES-CBC"></a>1）AES-CBC

加密和解密都使用：

AES-CBC与FVEK解密扇区数据

#### <a name="2%EF%BC%89%E5%B8%A6%E6%9C%89Elephant%20Diffuser%E7%9A%84AES-CBC"></a>2）带有Elephant Diffuser的AES-CBC

加密过程：
- 与扇区密钥key异或
- Elephant Elephant Diffuser A
- Elephant Elephant Diffuser B
- AES-CBC with FVEK
解密过程：
- AES-CBC with FVEK
- Elephant Elephant Diffuser B
- Elephant Elephant Diffuser A
- 与扇区密钥key异或
#### <a name="3%EF%BC%89AES-CCM"></a>3）AES-CCM

密钥数据使用初始化向量为0的AES-CCM模式加密。

### <a name="4.%E5%8D%B7%E5%A4%B4"></a>4.卷头

BitLocker Windows 7（及更高版本）卷标题与BitLocker Windows Vista卷标题类似于NTFS卷标题。卷标头大小为512字节，包括：

[![](https://p2.ssl.qhimg.com/t01625292d24f93f17c.png)](https://p2.ssl.qhimg.com/t01625292d24f93f17c.png)

### <a name="5.FVE%E5%85%83%E6%95%B0%E6%8D%AE%E5%9D%97"></a>5.FVE元数据块

BitLocker卷包含3个FVE元数据块。每个FVE元数据块包括：
- 块头
- 元数据标题
- 一组元数据条目
- 填充0字节值(在Windows 8中可见)
#### <a name="1%EF%BC%89FVE%E5%85%83%E6%95%B0%E6%8D%AE%E5%9D%97%E6%A0%87%E5%A4%B4"></a>1）FVE元数据块标头

大小为64字节，包括：

[![](https://p3.ssl.qhimg.com/t01de23cade74ee8583.png)](https://p3.ssl.qhimg.com/t01de23cade74ee8583.png)

解密BitLocker时会从后向前解密。因此，加密的卷大小包含仍然加密（或需要解密）的卷的字节数。

#### <a name="2%EF%BC%89FVE%E5%85%83%E6%95%B0%E6%8D%AE%E6%A0%87%E9%A2%98"></a>2）FVE元数据标题

版本1，大小为48字节，包括：

[![](https://p3.ssl.qhimg.com/t01b8fd8c7857e9aacc.png)](https://p3.ssl.qhimg.com/t01b8fd8c7857e9aacc.png)

#### <a name="3%EF%BC%89FVE%E5%85%83%E6%95%B0%E6%8D%AE%E6%9D%A1%E7%9B%AE"></a>3）FVE元数据条目

版本1，大小可变，包括：

[![](https://p5.ssl.qhimg.com/t014b4f569dad8daa1d.png)](https://p5.ssl.qhimg.com/t014b4f569dad8daa1d.png)

### <a name="6.%20BitLocker%E5%A4%96%E9%94%AE%EF%BC%88BEK%EF%BC%89%E6%96%87%E4%BB%B6"></a>6. BitLocker外键（BEK）文件

BitLocker外键（BEK）文件通常为156字节大小，包括：
- 一个文件头
- 一组元数据条目
#### <a name="1%EF%BC%89BEK%E6%96%87%E4%BB%B6%E5%A4%B4"></a>1）BEK文件头

BEK文件头类似于FVE元数据头，大小为48字节，包括：

[![](https://p5.ssl.qhimg.com/t01084853190e0379f3.png)](https://p5.ssl.qhimg.com/t01084853190e0379f3.png)<br>
文件中的密钥标识符必须与FVE卷主密钥（VMK）中的密钥标识符匹配。

#### <a name="2%EF%BC%89BEK%E5%85%83%E6%95%B0%E6%8D%AE%E6%9D%A1%E7%9B%AE"></a>2）BEK元数据条目

BEK元数据条目的格式类似于FVE元数据条目的格式。

BEK文件中的元数据由FVE外部密钥组成，该外部密钥包含256位未受保护的密钥数据。

VMK的标识符应与BEK文件头中的标识符匹配。



## 0x03 实战思路

通过上述讲解，可知成功解密的关键，是拿到bitlocker的FVEK和TWEAK，我们可以利用volatility的bitlocker插件对休眠文件、内存文件进行分析提取它。这里我用了一个win7硬盘试验，成功解密。

#### <a name="1%EF%BC%89%E7%A1%AE%E5%AE%9A%E5%88%86%E5%8C%BA%E5%B8%83%E5%B1%80%E5%B9%B6%E8%AF%86%E5%88%ABBitLocker%E5%8D%B7"></a>1）确定分区布局并识别BitLocker卷

[![](https://p1.ssl.qhimg.com/t0161fa9b21ee3b066b.png)](https://p1.ssl.qhimg.com/t0161fa9b21ee3b066b.png)

从扇区41947136开始的最后一个分区（该硬盘原有两个分区，C分区和D分区，其中C分区未被加密，D分区是经过bitlocker加密的加密卷）是受BitLocker保护的。可以通过查看文件系统头来验证它。发现“-FVE-FS-”签名。

[![](https://p2.ssl.qhimg.com/t01b11b08e2810393c9.png)](https://p2.ssl.qhimg.com/t01b11b08e2810393c9.png)

#### <a name="2%EF%BC%89%E4%BD%BF%E7%94%A8bitlocker%E6%8F%92%E4%BB%B6%E6%8F%90%E5%8F%96FVEK"></a>2）使用bitlocker插件提取FVEK

该插件扫描内存映像以查找BitLocker加密分配（内存池）并提取AES密钥（FVEK: 完整的卷加密密钥）。

[![](https://p3.ssl.qhimg.com/t01ae89ae9e51addb47.png)](https://p3.ssl.qhimg.com/t01ae89ae9e51addb47.png)

我们可以看到分析出了FVEK以及TWEAK，采取的加密方式为AES-128，如果是win8以上，可能会出现AES-256。

#### <a name="3%EF%BC%89%E8%A7%A3%E5%AF%86%E5%B9%B6%E8%AE%BF%E9%97%AE%E5%8D%B7"></a>3）解密并访问卷

[![](https://p0.ssl.qhimg.com/t016b3e70caa3d30b52.png)](https://p0.ssl.qhimg.com/t016b3e70caa3d30b52.png)

解密成功！
