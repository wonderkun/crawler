> 原文链接: https://www.anquanke.com//post/id/86511 


# 【病毒分析】Petya变种勒索蠕虫启动代码分析


                                阅读量   
                                **93023**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01d934428202cd2edc.jpg)](https://p2.ssl.qhimg.com/t01d934428202cd2edc.jpg)

**<br>**

**作者：360天眼实验室**



**背景**

****

继5月的WannaCry勒索蠕虫事件以后，2017年6月又出现了Petya变种勒索蠕虫，除了利用永恒之蓝漏洞和加密勒索以后，Petya变种与WannaCry有比较大的差别。WannaCry会加密机器上的文件，导致数据损毁，而Petya更为激进，它会加密系统的MBR直接导致机器无法启动，本文对其执行的MBR及文件系统的加密机制做详细的分析。

<br>

**恶意代码分析**

****

由于执行恶意操作的指令并不是以文件形式存在，我们使用WinHex工具提取受攻击机器的磁盘前23个扇区的数据进行分析，对应代码数据的Hash为 841e12729f200a5620859f2958e2d484。

**相关数据结构**

计算机启动时执行完BIOS的启动代码，检查各硬件设备正常后，JMP到MBR的引导代码进行执行；然后由MBR引导至活动分区的DBR，再由DBR引导操作系统。如：DBR调用NTLDR，再由NTLDR调用系统内核。

Petya病毒修改了系统的MBR，病毒在Bios加载后获得执行机会，病毒将加载存储在0x1扇区后的大小为0x20大小的病毒代码加载执行，这些代码会还原出真实的MBR，通过对还原出来的MBR解析，得到系统的DBR，通过DBR解析到系统的MFT结构，遍历所有的MFT，根据MFT找到文件内容所在的扇区后，读取该扇区加密内容后再写回到扇区中，从而实现对文件的加密。要完整的了解整个的加密过程，首先就是熟悉系统的MBR、DBR、MFT等结构的含义与功能。

MBR

Petya病毒修改了系统的MBR，病毒在Bios加载后获得执行机会，病毒将加载存储在0x1扇区后的大小为0x20大小的病毒代码加载执行，这些代码会还原出真实的MBR。在加密文件的过程中，Petya病毒会使用到MBR中。

MBR扇区由以下四部分组成：

引导代码：引导代码占MBR分区的前440字节，负责整个系统启动。如果引导代码被破坏，系统将无法启动。

Windows磁盘签名：占引导代码后面的4字节，是Windows初始化磁盘写入的磁盘标签，如果此标签被破坏，则系统会提示“初始化磁盘”。

MBR分区表：占Windows磁盘标签后面的64个字节，是整个硬盘的分区表。

MBR结束标志：占MBR扇区最后2个字节，一直为“55 AA”。

MBR结构如下：

```
;====================================================================
;    主引导记录(MBR)结构
;====================================================================
typedef struct _MASTER_BOOT_RECORD
`{`
 UCHAR    BootCode[446];
 PARTITION_ENTRY  Partition[4];
 USHORT    Signature;
`}`MASTER_BOOT_RECORD,*PMASTER_BOOT_RECORD;
;
;====================================================================
;====================================================================
;     分区表项结构(16字节)
;====================================================================
;
 typedef struct _PARTITION_ENTRY
 `{`
  UCHAR BootIndicator;  // 能否启动标志
  UCHAR StartHead;   // 该分区起始磁头号
  UCHAR StartSector;  // 起始柱面号高2位：6位起始扇区号
  UCHAR StartCylinder;  // 起始柱面号低8位
  UCHAR PartitionType;  // 分区类型
  UCHAR EndHead;   // 该分区终止磁头号
  UCHAR EndSector;   // 终止柱面号高2位：6位终止扇区号
  UCHAR EndCylinder;  // 终止柱面号低8位
  ULONG StartLBA;   // 起始扇区号
  ULONG TotalSector;  // 分区尺寸（总扇区数）
 `}`PARTITION_ENTRY,*PPARTITION_ENTRY;
```

对于其中的PartitionType 字段，Windows下可识别的分区类型主要有：

0x07 表示普通分区(Windows分区、数据分区。默认分区类型)。

0xEE 表示该分区表是PMBR，紧随其后的应该是GPT分区表头和GPT分区表，因此这是一块GPT硬盘。

0xEF 表示EFI系统分区

<br>

Petya在解密出原始的MBR后，解析MBR结构，得到起始扇区号，并根据起始扇区定位到DBR。

病毒解析MBR时，会对分区类型做判断，如果PMBR和EFI类型的系统分区，默认会不做处理。

在010editor工具中查看

 [![](https://p1.ssl.qhimg.com/t01d7390fb26543d5cf.png)](https://p1.ssl.qhimg.com/t01d7390fb26543d5cf.png)

判断分区类型，取了这两个字段：开始扇区与扇区大小：

 [![](https://p0.ssl.qhimg.com/t0112b2220a0f230456.png)](https://p0.ssl.qhimg.com/t0112b2220a0f230456.png)

在启动扇区（也就是63扇区）处，读一个扇区的内容，就是DBR结构

从MBR中可以定位到MBR分区表,根据分区表的属性就可以得到活动分区的扇区地址，也就得到了DBR结构地址。

**DBR**

DBR中存放着关于文件系统的重要参数信息以及系统引导代码。病毒解析到DBR后，只是为了取的DBR结构中的MftStartLcn字段(这个字段表明了MFT结构所在的扇区地址)，以便能进一步定位文件系统。

DBR的结构如下：

```
1.	////////////////////////////////////////////////////////////////////////////  
2.	//  
3.	//  NTFS 的DBR 数据结构  
4.	//  
5.	////////////////////////////////////////////////////////////////////////////  
6.	typedef struct _BIOS_PARAMETER_BLOCK `{`  
7.	  
8.	 /*+0x0B*/    uint16  BytesPerSector;    // 字节/扇区一般为0x0200 即512  
9.	 /*+0x0D*/    uchar   SectorsPerCluster; // 扇区/簇   
10.	 /*+0x0E*/    uint16  ReservedSectors;   // 保留扇区  
11.	 /*+0x0F*/    uchar   Fats;              //   
12.	 /*+0x11*/    uint16  RootEntries;       //   
13.	 /*+0x13*/    uint16  Sectors;           //   
14.	 /*+0x15*/    uchar   Media;             // 媒介描述  
15.	 /*+0x16*/    uint16  SectorsPerFat;     //   
16.	 /*+0x18*/    uint16  SectorsPerTrack;   // 扇区/磁轨  
17.	 /*+0x1A*/    uint16  Heads;             // 头  
18.	 /*+0x1C*/    uint32  HiddenSectors;     // 隐藏扇区  
19.	 /*+0x20*/    uint32  LargeSectors;      // checked when volume is mounted  
20.	  
21.	`}`BIOS_PARAMETER_BLOCK, *pBIOS_PARAMETER_BLOCK;  


typedef struct _NTFS_Boot_Sector`{`  
1.	 /*+0x00*/  uchar    JmpCode[3];        // 跳转指令  
2.	 /*+0x03*/  char     OemID[8];          // 文件系统ID  
3.	 /*+0x0B*/  BIOS_PARAMETER_BLOCK PackedBpb;   // BPB  
4.	 /*+0x24*/  uchar    Unused[4];           // 未使用,总是为  
5.	 /*+0x28*/  uint64   NumberSectors;       // 扇区总数  
6.	 /*+0x30*/  lcn      MftStartLcn;        // 开始C# $MFT  (簇) 乘以 BIOS_PARAMETER_BLOCK.SectorsPerCluster 值得到扇区号  
7.	 /*+0x38*/  lcn      Mft2StartLcn;       // 开始C# $MFTMirr (簇)  
8.	 /*+0x40*/  uchar    ClustersPerFileRecordSegment;  // 文件记录大小指示器  
9.	 /*+0x41*/  uchar   Reserved0[3];       // 未使用  
10.	 /*+0x44*/  uchar DefaultClustersPerIndexAllocationBuffer;     // 簇/索引块  
11.	 /*+0x45*/  uchar   Reserved1[3];       // 未使用  
12.	 /*+0x48*/  uint64  SerialNumber;       // 64位序列号  
13.	 /*+0x50*/  uint32  Checksum;           // 校验和  
14.	 /*+0x54*/  uchar   BootStrap[426];     // 启动代码  
15.	 /*+0x1FE*/ uint16  RecordEndSign;      // 0xAA55 结束标记  
16.	`}`NTFS_Boot_Sector, *pNTFS_Boot_Sector;
```



其中，定位MFT时，最重要的结构为MftStartLcn表示起始簇号，乘以BIOS_PARAMETER_BLOCK.SectorsPerCluster（在我的机器上这个值为8，表示一个簇由8个扇区组成）后就得到起始扇区号。

**MFT**

**简介**

MFT，即主文件表（Master File Table）的简称，它是NTFS文件系统的核心。MFT由一个个MFT项（也称为文件记录）组成。每个MFT项的前部为0x10字节的头结构，用来描述本MFT项的相关信息。后面节存放着属性。每个文件和目录的信息都包含在MFT中，每个文件和目录至少有一个MFT项。除了引导扇区外，访问其他任何一个文件前都需要先访问MFT，在MFT中找到该文件的MFT项，根据MFT项中记录的信息找到文件内容并对其进行访问。

MFT结构分为两种：元文件与普通文件。

元文件对于用户是不能直接访问的，MFT将开头的16个文件记录块保留用于这些元数据文件，除此之外的文件记录块才用于普通的用户文件和目录。

**16个元文件**

```
#defineMFT_IDX_MFT0
#defineMFT_IDX_MFT_MIRR1
#defineMFT_IDX_LOG_FILE2
#defineMFT_IDX_VOLUME3
#defineMFT_IDX_ATTR_DEF4
#defineMFT_IDX_ROOT5
#defineMFT_IDX_BITMAP6
#defineMFT_IDX_BOOT7
#defineMFT_IDX_BAD_CLUSTER8
#defineMFT_IDX_SECURE9
#defineMFT_IDX_UPCASE10
#defineMFT_IDX_EXTEND11
#defineMFT_IDX_RESERVED1212
#defineMFT_IDX_RESERVED1313
#defineMFT_IDX_RESERVED1414
#defineMFT_IDX_RESERVED1515
#defineMFT_IDX_USER16
```

这16个原文件本身也是MFT结构的模式，可以理解为记录了MFT信息的MFT结构。

**怎么解析这16个原文件的MFT结构呢？**

换句话说，通过MBR定位到DBR,通过DBR定位到MFT，此时的MFT就对应着索引为MFT_IDX_MFT的MFT，向后偏移文件记录大小的地方，就存放着索引为MFT_IDX_MFT_MIRR的MFT。再向后偏移文件记录大小的地方，就存放着索引为MFT_IDX_LOG_FILE的MFT

**解析这16个原文件的MFT结构有什么用？**

如对于MFT_IDX_VOLUME 这个MFT结构，解析这个MFT结构中的ATTR_TYPE_VOLUME_INFORMATION（对应着0x70）就可以得到NTFS卷的版本信息,解析这个MFT结构中的ATTR_TYPE_VOLUME_NAME属性（对应着0x60）就可以得到NTFS卷名信息。

再如，对于MFT_IDX_MFT 这个MFT结构，解析这个MFT结构中的ATTR_TYPE_DATA（对应0x80）的属性RealSize，就表示整个卷所有的文件记录的大小信息。利用这个大小信息是以字节表示的，用这个大小信息除以每个文件记录所占用的字节就得到了卷占有的文件记录数量。计算出来的文件记录数量是将元文件也计算在内的。

依次遍历每个文件记录数量，读取这个文件记录的内容就是MFT结构，解析这个MFT的对应属性就可以解析出文件名、文件属性、文件内容等。

**普通MFT**

遍历文件时，从第16个文件记录开始向后遍历，才会得到普通的用户文件和目录信息及内容。

**数据结构**

MFT的直观结构如下，

// 文件记录体

// 属性1

// 属性2

// …………

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019c1b045eb1394645.png)

每个MFT的结构如下：

```
// 文件记录头  
typedef struct _FILE_RECORD_HEADER  
`{`  
 /*+0x00*/  uint32 Type;            // 固定值'FILE'  
 /*+0x04*/  uint16 UsaOffset;       // 更新序列号偏移, 与操作系统有关  
 /*+0x06*/  uint16 UsaCount;        // 固定列表大小Size in words of Update Sequence Number &amp; Array (S)  
 /*+0x08*/  uint64 Lsn;             // 日志文件序列号(LSN)  
`}` FILE_RECORD_HEADER, *PFILE_RECORD_HEADER;  

// 文件记录体  
typedef struct _FILE_RECORD`{`  
 /*+0x00*/  FILE_RECORD_HEADER Ntfs;  // MFT表头  
 /*+0x10*/  uint16  SequenceNumber;   // 序列号(用于记录文件被反复使用的次数)  
 /*+0x12*/  uint16  LinkCount;        // 硬连接数  
 /*+0x14*/  uint16  AttributeOffset;  // 第一个属性偏移  
 /*+0x16*/  uint16  Flags;            // falgs, 00表示删除文件,01表示正常文件,02表示删除目录,03表示正常目录  
 /*+0x18*/  uint32  BytesInUse;       // 文件记录实时大小(字节) 当前MFT表项长度,到FFFFFF的长度+4  
 /*+0x1C*/  uint32  BytesAllocated;   // 文件记录分配大小(字节)  
 /*+0x20*/  uint64  BaseFileRecord;   // = 0 基础文件记录 File reference to the base FILE record  
 /*+0x28*/  uint16  NextAttributeNumber; // 下一个自由ID号  
 /*+0x2A*/  uint16  Pading;           // 边界  
 /*+0x2C*/  uint32  MFTRecordNumber;  // windows xp中使用,本MFT记录号  
 /*+0x30*/  uint32  MFTUseFlags;      // MFT的使用标记  
`}`FILE_RECORD, *pFILE_RECORD;
```

根据FILE头部数据找到下面的一个个属性,接下来分析的就是一个个属性了，属性由属性头跟属性体组成,属性头的结构定义如下：

```
// 属性头  
typedef struct  
`{`  
 /*+0x00*/  ATTRIBUTE_TYPE AttributeType;    // 属性类型  
 /*+0x04*/  uint16 RecordLength;             // 总长度(Header+body长度)  
 /**0x06*/  uint16 unknow0;  
 /*+0x08*/  uchar Nonresident;               // 非常驻标志  
 /*+0x09*/  uchar NameLength;                // 操作属性名长度  
  
                                          // 0X0001为压缩标记  
                                        // 0X4000为加密标记  
                                        // 0X8000为系数文件标志  
 /*+0x0A*/  uint16 NameOffset;           // 属性名偏移(从属性起始位置的偏移)  
                                              // NameLength 如果不为零,则用这个值去寻址数据偏移  
 /*+0x0C*/  uint16 Flags;                    // ATTRIBUTE_xxx flags.  
 /*+0x0E*/  uint16 AttributeNumber;          // The file-record-unique attribute instance number for this attribute.  
`}` ATTRIBUTE, *PATTRIBUTE;  
  
// 属性头   
typedef struct _RESIDENT_ATTRIBUTE  
`{`  
 /*+0x00*/  ATTRIBUTE Attribute;   // 属性  
 /*+0x10*/  uint32 ValueLength;    // Data部分长度  
 /*+0x14*/  uint16 ValueOffset;    // Data内容起始偏移  
 /*+0x16*/  uchar Flags;           // 索引标志  
 /*+0x17*/  uchar Padding0;        // 填充  
`}` RESIDENT_ATTRIBUTE, *PRESIDENT_ATTRIBUTE;
```

Petya中涉及到MFT的属性

```
// 属性类型定义 
AttributeFileName = 0x30,  
AttributeData = 0x80, 
这两个属性的定义如下：
// 文件属性ATTRIBUTE.AttributeType == 0x30  
typedef struct  
`{`  
 /*+0x00*/  uint64 DirectoryFile:48;    // 父目录记录号(前个字节)  
 /*+0x06*/  uint64 ReferenceNumber:16;  // +序列号(与目录相关)  
 /*+0x08*/  uint64 CreationTime;        // 文件创建时间  
 /*+0x10*/  uint64 ChangeTime;          // 文件修改时间          
 /*+0x18*/  uint64 LastWriteTime;       // MFT更新的时间  
 /*+0x20*/  uint64 LastAccessTime;      // 最后一次访问时间  
 /*+0x28*/  uint64 AllocatedSize;       // 文件分配大小  
 /*+0x30*/  uint64 DataSize;            // 文件实际大小  
 /*+0x38*/  uint32 FileAttributes;      // 标志,如目录压缩隐藏等  
 /*+0x3C*/  uint32 AlignmentOrReserved; // 用于EAS和重解析  
 /*+0x40*/  uchar NameLength;      // 以字符计的文件名长度,没字节占用字节数由下一字节命名空间确定  
  
            // 文件名命名空间, 0 POSIX大小写敏感,1 win32空间,2 DOS空间, 3 win32&amp;DOS空间  
 /*+0x41*/  uchar NameType;          
 /*+0x42*/  wchar Name[1];         // 以Unicode方式标识的文件名  
`}` FILENAME_ATTRIBUTE, *PFILENAME_ATTRIBUTE;

// 数据流属性 ATTRIBUTE.AttributeType == 0x80   
typedef struct _NONRESIDENT_ATTRIBUTE  
`{`  
    /*+0x00*/   ATTRIBUTE Attribute;    
  
    /*+0x10*/   uint64 StartVcn;     // LowVcn 起始VCN  起始簇号  
    /*+0x18*/   uint64 LastVcn;      // HighVcn  结束VCN  结束簇号  
  
    /*+0x20*/   uint16 RunArrayOffset;    // 数据运行的偏移，非常重要 
    /*+0x22*/   uint16 CompressionUnit;   // 压缩引擎  
    /*+0x24*/   uint32  Padding0;       // 填充  
    /*+0x28*/   uint32  IndexedFlag;    // 为属性值分配大小(按分配的簇的字节数计算)  
    /*+0x30*/   uint64 AllocatedSize;   // 属性值实际大小  
    /*+0x38*/   uint64 DataSize;     // 属性值压缩大小  
    /*+0x40*/   uint64 InitializedSize;   // 实际数据大小  
    /*+0x48*/   uint64 CompressedSize;    // 压缩后大小  
`}` NONRESIDENT_ATTRIBUTE, *PNONRESIDENT_ATTRIBUTE;
```

**对于0x30属性：**

对于MFT中的0x30属性的直观认识，如下：

黄色部分对应着上表中的ATTRIBUTE结构，红色部分对应着上表中的NONRESIDENT_ATTRIBUTE结构。选中部分对应着FILENAME_ATTRIBUTE结构内容，这里面包含了文件的各种时间属性和文件名等内容。



 [![](https://p0.ssl.qhimg.com/t0123690677a1e10c71.png)](https://p0.ssl.qhimg.com/t0123690677a1e10c71.png)

Petya病毒在遍历MFT时，会通过判断当前MFT的AttributeFileName属性判断是否加密该MFT。

**对于0x80属性：**

对于MFT中的0x80属性的直观认识，如下：

黄色部分对应着上表中的ATTRIBUTE结构，红色部分对应着上表中的NONRESIDENT_ATTRIBUTE结构。绿色部分对应着RUN-LIST结构内容。

 [![](https://p3.ssl.qhimg.com/t01b1806f888abc79c0.png)](https://p3.ssl.qhimg.com/t01b1806f888abc79c0.png)

80H属性是文件数据属性，该属性容纳着文件的内容，文件的大小一般指的就是未命名数据流的大小。该属性没有最大最小限制，最小情况是该属性为常驻属性。常驻属性就不做多的解释了，如下是一个非常驻的80H属性。

该属性的“Run List”值为“32 0C 1B 00 00 0C”，其具体含义如下：

 [![](https://p4.ssl.qhimg.com/t0158a3a2686e4efffe.png)](https://p4.ssl.qhimg.com/t0158a3a2686e4efffe.png)

Petya病毒在加密文件内容时，会通过Run List定位到文件内容所在的真正扇区加密文件，如果文件内容大于2个扇区，则只加密前两个扇区。

**恶意代码加载过程**

**1 加载代码到0x8000执行**

从第一个扇区开始，读取0x20个扇区到0x8000地址处，随后跳到0x8000处执行

循环读取0x20个扇区代码片段：

 [![](https://p1.ssl.qhimg.com/t012ac8b56a69ddd46a.png)](https://p1.ssl.qhimg.com/t012ac8b56a69ddd46a.png)



在循环里使用int 13读取磁盘内容

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015f82fea4155f4f4a.png)



**2 调用函数读取硬盘参数**

读取硬盘参数

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014de69af87b3cf3bd.png)

比较“FA 31 C0 8E”硬编码，判断当前的第一个扇区的内容是不是病毒写入的内容。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019e8f14e49c204db0.png)

**3 判断加密标志**

读取0x20扇区的内容（该扇区保存了病毒的配置信息），判断该扇区的第一个字节是不是1，如果是1，表示mbr已经被加过密，就来到显示勒索界面的流程;如果不为1，表示还未对MBR和MFT进行加密，进入加密流程。 

[![](https://p3.ssl.qhimg.com/t01d97ccf3fd6c4ee0e.png)](https://p3.ssl.qhimg.com/t01d97ccf3fd6c4ee0e.png)

**加密过程**

**1 打印修复磁盘信息，设置加密标志**

打印出虚假的“Repairing file system on C:”信息，读取0x20扇区中的配置信息到内存，并将读取到的配置信息的加密标志设置为1。随后，将修改过加密标志的内容写入到扇区中，为了保证写入成功，这里循环写了0x20次。

打印的磁盘修复信息如下：

 **[![](https://p0.ssl.qhimg.com/t011e2b0ee8c9167bdf.png)](https://p0.ssl.qhimg.com/t011e2b0ee8c9167bdf.png)**

 [![](https://p5.ssl.qhimg.com/t016f39a8615c481359.png)](https://p5.ssl.qhimg.com/t016f39a8615c481359.png)

**2 加密验证扇区**

加密验证扇区的方法为：读取0x21扇区的内容（这个扇区保存的全是0x07数据），使用从配置信息扇区读取的key与n做为加密参数，调用salsa加密该读到的0x07内容，并将加密后的内容写入到0x21扇区中

 [![](https://p3.ssl.qhimg.com/t0173994279fe9c5873.png)](https://p3.ssl.qhimg.com/t0173994279fe9c5873.png)

[![](https://p5.ssl.qhimg.com/t01f4091a29872d00ea.png)](https://p5.ssl.qhimg.com/t01f4091a29872d00ea.png)

显示虚假的“CHKDSK is repairing sector”界面，实际在后台正在加密MFT数据。

 [![](https://p2.ssl.qhimg.com/t01e8a46f4c9e47c485.png)](https://p2.ssl.qhimg.com/t01e8a46f4c9e47c485.png)

**3 加密操作**

**文件遍历的原理**

Petya病毒通过解析MBR，DBR得到MFT地址。解析MFT索引为0的元文件，得到属性为DATA的属性内容，取出属性中的RUN-LIST结构中的簇数量与起始扇区，根据这两个字段遍历所有的MFT就得到了当前文件系统中所有的文件信息。

解析MBR

解析原始MBR数据的代码片段：

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0174bb7fec62f8ee59.png)

判断MBR中的分区类型：

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e56ae96cd35811cd.png)

判断从mbr中读取到的StartLBA字段不为空

  [![](https://p3.ssl.qhimg.com/t012f2c3f70460943d8.png)](https://p3.ssl.qhimg.com/t012f2c3f70460943d8.png)

从mbr中解析到StartLBA字段，并读取该字段对应的扇区，此扇区的内容就为DBR相关的内容：

 [![](https://p3.ssl.qhimg.com/t016136c167d805a735.png)](https://p3.ssl.qhimg.com/t016136c167d805a735.png)



读取到DBR后，解析出MftStartLcn字段，该字段就表示 MFT地址：

 [![](https://p4.ssl.qhimg.com/t01b6c3721926e4da36.png)](https://p4.ssl.qhimg.com/t01b6c3721926e4da36.png)



得到MFT地址后，该地址就是索引为0的MFT元文件地址,从该元文件结构中取出属性为0x80（DATA）的内容。

首先读取到$MFT的扇区内容：

 [![](https://p4.ssl.qhimg.com/t01e47eca964cc8b458.png)](https://p4.ssl.qhimg.com/t01e47eca964cc8b458.png)

解析属性，判断是不是0x80(DATA)属性类型

 [![](https://p3.ssl.qhimg.com/t01f5291057f95d6189.png)](https://p3.ssl.qhimg.com/t01f5291057f95d6189.png)

对$MFT属性0x80中的解析，得到下面信息：

run_data_cluster*sector/cluster + 0x20(0x20为元文件占用的扇区大小)+mbr. arg_StartLBA，作为普通 MFT扇区的起始扇区，这样是保证加密的过程中不会加密元文件扇区与mbr相关的扇区。

（run_data_num_clusters * sector/cluster）- 0x20(0x20为元文件占用的扇区大小)，做为普通MFT的扇区大小。

[![](https://p1.ssl.qhimg.com/t015c310cac5f2701e3.png)](https://p1.ssl.qhimg.com/t015c310cac5f2701e3.png)



随后，就来到遍历用户MFT的函数：

 [![](https://p1.ssl.qhimg.com/t01ccd4a09d181e8e9e.png)](https://p1.ssl.qhimg.com/t01ccd4a09d181e8e9e.png)

**遍历普通MFT结构**

遍历普通MFT结构的函数在00008FA6处，该函数为病毒代码中最为主要的函数。

下面对这个函数进行详细分析:

在调试的过程中，parse_User_MFT函数的参数内容为：80 C6 5F 00 60 00 20 C6  00 00 3F 00 00 00 3F 00 60 00 08 C6 2C 67 4A 67  8B 77 52 9C 01,结合调试时传递的参数内容，对函数作出说明。

[![](https://p1.ssl.qhimg.com/t01e6f3566ea728be9f.png)](https://p1.ssl.qhimg.com/t01e6f3566ea728be9f.png)



该函数主要功能为：对扇区中的MFT遍历，对不符合MFT头部标志(FILE)的扇区，会直接调用SALSA20算法进行加密该扇区，对符合MFT头部标志的扇区，判断0x30属性中的文件名判断是不是元文件，如果不是元文件名格式，则直接加密该扇区。其他情况下，判断MFT结构0x80属性中的常驻内存属性，如果是非常驻内存属性，就解析文件内容的前二个扇区，取出该扇区的内容后，使用salsa20算法进行加密。

1.先打印出“CHKDSK is repairing sector”，显示虚假的磁盘修复界面

 [![](https://p3.ssl.qhimg.com/t01ec1678ac553caed6.png)](https://p3.ssl.qhimg.com/t01ec1678ac553caed6.png)

2.对当前MFT头是不是“FILE”,如果不是”FILE”的话，则直接加密这个扇区

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a5c76acb10617254.png)

3.如果是FILE，接着遍历mft的各个属性：

如果属性为AttributeFileName（0x30），判断文件名字长度是不是1，如果长度为1，直接加密，如果长度不为1，则看文件名字是不是以$开头(以$开头的是NTFS文件系统的元文件)，如果是元文件，则加密当前MFT.

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013909464db1c60b95.png)

如果属性为AttributeData文件数据属性（0x80），则首先根据属性头判断是不是非常驻内存，如果是常驻内存属性就跳过，不进行加密。如果是非常驻内存属性，则通过RUNLIST结构遍历到存储数据的真正的扇区位置。

 [![](https://p5.ssl.qhimg.com/t012c01eea93ad2e5eb.png)](https://p5.ssl.qhimg.com/t012c01eea93ad2e5eb.png)

解析RUNLIST

 [![](https://p0.ssl.qhimg.com/t010ffdbd87283cc1b4.png)](https://p0.ssl.qhimg.com/t010ffdbd87283cc1b4.png)

根据RUNLIST中的起始簇乘以MBR中保存的每簇对应的扇区数，得到数据真正所在的扇区。

 [![](https://p3.ssl.qhimg.com/t012366db3e73668a12.png)](https://p3.ssl.qhimg.com/t012366db3e73668a12.png)

随后，判断上面计算出的文件内容对应扇区数量是不是大于2，如果大于2，只加密前2个扇区。

 [![](https://p5.ssl.qhimg.com/t013c47b517ade7b68c.png)](https://p5.ssl.qhimg.com/t013c47b517ade7b68c.png)

读取该MFT文件对应的文件内容的前两个分区，通过直接使用int 13中断从扇区读取到文件内容，使用salsa20加密后，将密文直接写入的扇区中文件中。

 [![](https://p4.ssl.qhimg.com/t013657a687f1383fd3.png)](https://p4.ssl.qhimg.com/t013657a687f1383fd3.png)

在动态调试时，可以看到加密了文件内容，加密文件内容前的数据

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01deabf7143a250b0c.png)

被加密后的文件内容：

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01acfcd6f23704dd69.png)

**加密函数**

对文件的加密使用了SALSA20算法，该算法属于流加密，在知道key和iv的情况下，加密函数和解密函数可以为相同的函数代码。

加密函数

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012a5889cc518a1ef9.png)



在密钥扩展的函数中，Petya将原始的常数“expand 16-byte k”更改成了“1nvald s3ct”

扩展密钥函数代码：

 [![](https://p5.ssl.qhimg.com/t015b12476130209766.png)](https://p5.ssl.qhimg.com/t015b12476130209766.png)

Salsa20加密时使用的key和iv来自于配置信息扇区（0x20扇区）

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0195527a1b1abd280d.png)



将明文与生成的keystream异或，实现加密

 [![](https://p5.ssl.qhimg.com/t01a6a952577ed4ed67.png)](https://p5.ssl.qhimg.com/t01a6a952577ed4ed67.png)

**解密过程**

在开机启动过程中，MBR引导后，加载扇区中的恶意代码后，恶意代码会判断配置信息第1个BYTE是不是1，1表示已经加密过，则进入相应的解密过程中

**1 打印勒索信息**

打印出勒索信息

 [![](https://p5.ssl.qhimg.com/t01edca150abf7ab3a2.png)](https://p5.ssl.qhimg.com/t01edca150abf7ab3a2.png)

也就是显示如下的内容

 [![](https://p2.ssl.qhimg.com/t011fba72e925625d0b.png)](https://p2.ssl.qhimg.com/t011fba72e925625d0b.png)

**2 读取用户输入的key**

清空内存，读取用户输入的key

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0169011bbd4c2d5bb8.png)

**3 验证用户的key**

在验证KEY的过程中，首先比较输入的key的长度，必须大于0x20长度

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018f8a4cbadd67c9ef.png)



将输入的key通过自定义算法的转换0x21次

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015e237a13561729c4.png)

使用转换过的key，使用salsa20算法解密0x21扇区的内容（这个扇区的内容为加密过的0x7内容），比较解密出来的内容是不是0x7，如果是则表明解密密码正确。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0130db97cc651e741d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e3c064a44c50dd54.png)

密码验证通过后，会使用这个key做为参数调用DecryptProc 函数(并非勒索软件作者定义的函数名)，

 [![](https://p2.ssl.qhimg.com/t01f81eb71d4380336a.png)](https://p2.ssl.qhimg.com/t01f81eb71d4380336a.png)



在DecryptProc函数中调用与加密时相同的函数进行对MFT结构进行遍历后解密，

[![](https://p3.ssl.qhimg.com/t014b3011e43b487d2a.png)](https://p3.ssl.qhimg.com/t014b3011e43b487d2a.png)

在解密完成后，打印“Please reboot your computer!”信息

 [![](https://p4.ssl.qhimg.com/t0196c78726eee95343.png)](https://p4.ssl.qhimg.com/t0196c78726eee95343.png)

**总结**

本文对Petya变种勒索蠕虫的扇区启动代码进行了详细分析，分析显示Petya变种勒索蠕虫并不仅会加密MBR和MFT结构，也会将MFT对应的文件内容的前两个扇区进行加密。换句话说，Petya变种勒索蠕虫在系统启动时MBR中的代码执行时也会进行全盘文件的加密操作。结合RING3级别的勒索代码功能，Petya会对文件执行两次加密操作，第一次为Petya勒索蠕虫执行时，使用RSA与AES算法遍历文件系统对指定扩展名的文件加密，第二次为系统启动时，启动扇区的代码会通过遍历MFT结构定位文件内容并对文件使用salsa20算法进行加密。对于RING3级别的文件加密过程，解密密钥可以通过勒索蠕虫作者的RSA私钥进行解密获得，而启动扇区级别的文件加密过程使用了随机密码进行，启动扇区级别的文件加密无法解密。

**参考**

[http://dengqi.blog.51cto.com/5685776/1351300](http://dengqi.blog.51cto.com/5685776/1351300)

[https://github.com/alexwebr/salsa20/blob/master/salsa20.c](https://github.com/alexwebr/salsa20/blob/master/salsa20.c)

[http://blog.csdn.net/enjoy5512/article/details/50966009](http://blog.csdn.net/enjoy5512/article/details/50966009)

[http://bobao.360.cn/learning/detail/4039.html](http://bobao.360.cn/learning/detail/4039.html)
