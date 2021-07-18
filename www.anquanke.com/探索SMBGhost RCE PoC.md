
# 探索SMBGhost RCE PoC


                                阅读量   
                                **400535**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ricercasecurity，文章来源：ricercasecurity.blogspot.com
                                <br>原文地址：[https://ricercasecurity.blogspot.com/2020/04/ill-ask-your-body-smbghost-pre-auth-rce.html](https://ricercasecurity.blogspot.com/2020/04/ill-ask-your-body-smbghost-pre-auth-rce.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/203683/t018f420669be3f7ff7.jpg)](./img/203683/t018f420669be3f7ff7.jpg)



## 0x00 前言

3月11日，微软公布了SMBGhost漏洞的相关信息，这是内核驱动`srv2.sys`中SMBv3.1.1消息解压缩过程中的一个整数溢出漏洞。由于SMBGhost漏洞可能导致RCE以及“蠕虫传播”效果，因此受到人们广泛关注。

虽然现在网上有许多[公开资料](https://blog.zecops.com/vulnerabilities/exploiting-smbghost-cve-2020-0796-for-a-local-privilege-escalation-writeup-and-poc/)以及实现[LPE](https://github.com/ZecOps/CVE-2020-0796-LPE-POC)（本地权限提升）的PoC，然而目前并没有实现RCE的PoC出现。这可能是因为远程内核利用与本地利用区别较大，攻击者无法利用某些有用的操作系统函数，如创建用户态进程、引用PEB、发起系统调用等。此外，Windows 10中引入了一些缓解机制，也导致RCE的实现更加具有挑战性。

在本文中，我将介绍如何实现RCE、突破限制条件及缓解机制，其中比较有趣的一点是我们成功获取了随机化的地址信息（也就是实现了“读原语”）。我本人之前还未使用或看到过这种技术，因此认为值得与大家分享。



## 0x01 漏洞根源及实现任意写入

许多公开资料已经提到过，SMBGhost是`srv2!Srv2DecompressData`中存在的一个整数溢出漏洞，该函数用来解压缩请求数据包。在研究如何利用该漏洞之前，我们需要先分析漏洞根源，思考如何滥用该缺陷。

简化版的`srv2!Srv2DecompressData`代码如下：

```
signed __int64 __fastcall Srv2DecompressData(SRV2_WORKITEM *workitem)
{
  // declarations omitted
  ...
  request = workitem-&gt;psbhRequest;
  if ( request-&gt;dwMsgSize &lt; 0x10 )
    return 0xC000090Bi64;
  compressHeader = *(CompressionTransformHeader *)request-&gt;pNetRawBuffer;
  ...
  // (A) an integer overflow occurs here
  newHeader = SrvNetAllocateBuffer((unsigned int)(compressHeader.originalCompressedSegSize + compressHeader.offsetOrLength), 0i64);
  if ( !newHeader )
    return 0xC000009Ai64;
  // (B) the first subsequent buffer overflow occurs in SmbCompressionDecompress
  if ( SmbCompressionDecompress(
        compression_type,
        &amp;workitem-&gt;psbhRequest-&gt;pNetRawBuffer[compressHeader.offsetOrLength + 16],
        workitem-&gt;psbhRequest-&gt;dwMsgSize - compressHeader.offsetOrLength - 16,
        &amp;newHeader-&gt;pNetRawBuffer[compressHeader.offsetOrLength],
        compressHeader.OriginalCompressedSegSize,
        &amp;finalDecompressedSize) &lt; 0
      || finalDecompressedSize != compressHeader.originalCompressedSegSize) )
  {
    SrvNetFreeBuffer(newHeader);
    return 0xC000090Bi64;
  }
  if ( compressHeader.offsetOrLength )
  {
    // (C) the second buffer overflow occurs here
    memmove(newHeader-&gt;pNetRawBuffer, workitem-&gt;psbhRequest-&gt;pNetRawBuffer + 16, compressHeader.offsetOrLength);
  }
  newHeader-&gt;dwMsgSize = compressHeader.OffsetOrLength + fianlDecompressedSize;
  Srv2ReplaceReceiveBuffer(workitem, newHeader);
  return 0i64;
}
```

如上述代码所示，我们可以在“(A)”处看到最主要的整数溢出问题。由于攻击者可以控制`compressHeader.originalCompressedSegSize`以及`compressHeader.offsetOrLength`，因此这个漏洞非常直观。此外，如果我们将`compressHeader.originalCompressedSegSize`设置为一个非常大的值（比如`0xffffffff`），那么“(B)”处还存在一个缓冲区溢出问题。为了澄清我们可以使用该缓冲区溢出哪些数据，我们需要找到该缓冲区附近存在的数据。

来看一下`srvnet!SrvNetAllocateBufferFromPool`的代码（在`srvnet!SrvNetAllocateBuffer`中被调用）：

```
struct __declspec(align(8)) SRVNET_BUFFER_HDR
{
  LIST_ENTRY List;
  USHORT Flag;
  BYTE unknown0[4];
  WORD unknown1;
  PBYTE pNetRawBuffer;
  DWORD dwNetRawBufferSize;
  DWORD dwMsgSize;
  DWORD dwNonPagedPoolSize;
  DWORD dwPadding;
  PVOID pNonPagedPoolAddr;
  PMDL pMDL1; // points to mdl1
  DWORD dwByteProcessed;
  BYTE unknown2[4];
  _QWORD unknown3;
  PMDL pMDL2; // points to mdl2
  PSRVNET_RECV pSrvNetWskStruct;
  DWORD unknown4;
  char unknown5[12];
  char unknown6[32];
  MDL mdl1; // variable size
  MDL mdl2; // variable size
};

PSRVNET_BUFFER_HDR __fastcall SrvNetAllocateBufferFromPool(__int64 unused_size, unsigned __int64 size)
{
  // declarations omitted
  ...
  sizeOfHeaderAndBuf = (unsigned int)size + 0xE8i64;
  ...
  sizeOfMDL = MmSizeOfMdl(0i64, (unsigned int)size + 0xE8i64);
  sizeOfMDLAligned = sizeOfMDL + 8;
  ...
  sizeOfMDLs = 2 * sizeOfMDLAligned;
  ...
  allocSize = sizeOfMDLs + sizeOfHeaderAndBuf;
  ...
  pNonPagedPoolAddr = (BYTE *)ExAllocatePoolWithTag((POOL_TYPE)512, allocSize, 0x3030534Cu);
  ...

  // the buffer is located above the header(!)
  pNetRawBuffer = (signed __int64)(pNonPagedPoolAddr + 0x50);
  srbHeader = (PSRVNET_BUFFER_HDR)((unsigned __int64)&amp;pNonPagedPoolAddr[size + 0x57] &amp; 0xFFFFFFFFFFFFFFF8ui64);
  srbHeader-&gt;pNonPagedPoolAddr = pNonPagedPoolAddr;
  srbHeader-&gt;pMDL2 = (PMDL)(((unsigned __int64)&amp;srbHeader-&gt;mdl1 + sizeOfMDLAligned + 7) &amp; 0xFFFFFFFFFFFFFFF8ui64);
  pMDL1 = (_MDL *)(((unsigned __int64)&amp;srbHeader-&gt;mdl1 + 7) &amp; 0xFFFFFFFFFFFFFFF8ui64);
  srbHeader-&gt;pNetRawBuffer = pNonPagedPoolAddr + 0x50;
  srbHeader-&gt;pMDL1 = pMDL1;
  ...
  return srbHeader;
}
```

从代码可知，由于某些原因，该缓冲区直接位于头部上方。我不清楚为什么微软开发者会设计出这种内存布局。正是因为这种布局的存在，我们的漏洞利用过程会更加轻松。因此，我们可以利用“(B)”处的缓冲区溢出来覆盖`SRVNET_BUFFER_HDR`。

在构建写原语时，这一点非常重要。简而言之，如果我们在“(B)”处覆盖`pNetRawBuffer`，那么就能在“(C)”处实现任意写入。如果想了解更多细节，我建议大家阅读[ZecOps](https://blog.zecops.com/vulnerabilities/exploiting-smbghost-cve-2020-0796-for-a-local-privilege-escalation-writeup-and-poc/)之前公布的研究报告及[LPE PoC](https://blog.zecops.com/vulnerabilities/exploiting-smbghost-cve-2020-0796-for-a-local-privilege-escalation-writeup-and-poc/)。

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0148b8e5bd21c29533.png)

大家可能会认为，如果将`compressHeader.originalCompressedSegSize`设置为错误的值，那么`finalDecompressedSize != compressHeader.originalCompressedSegSize`条件将返回`true`，解压缩操作将失败，代码无法执行到“(C)”处。

然而，如ZecOps报告中所述，由于某些原因，`srvnet!SmbCompressionDecompress`会将`finalDecompressedSize`赋值为`originalCompressedSegSize`，该过程只涉及几处检查。因此，该函数可以被当成写原语来使用，足以实现LPE。

目前我们已经讨论过漏洞根源，以及如何构建写原语，这些信息在许多公开报告中也提到过，现在我们可以更进一步分析。为了获得读原语，我们需要用到Lookaside List以及`KUSER_SHARED_DATA`。

### <a class="reference-link" name="Lookaside%20List"></a>Lookaside List

Lookaside List是Windows内核中提供的一种机制（或者API），用来缓存经常分配和释放的数据结构。由于每次调用`ExAllocatePoolWithTag`及`ExFreePoolWithTag`都会花费大量时间，因此内核驱动经常会有对应其数据结构的一个Lookaside List。

由于这个点不是特别重要，因此这里我不会详细介绍这方面内容。这里我们只需要记住系统引入Lookaside List的目的是提高效率。因此，当数据结构由Lookaside List来维护时，相应的初始化及析构操作通常会被跳过。由于Lookaside List中的元素之前应该已经初始化过，因此在大多数情况下，当从列表中获取元素时，我们不需要再次执行初始化操作。

当然，这种情况同样适用于`SRVNET_BUFFER_HDR`。`srvnet!SrvNetAllocateBuffer`的默认行为是为`SRVNET_BUFFER_HDR`提供Lookaside List（我们可以通过注册表修改该行为），而当头部来自于List时，大部分初始化操作会被跳过。这意味着我们可以破坏头部，将其加入List中，然后在后续请求中将其从List中取回，从而保持头部结构处于损坏状态。在构造读原语时，我们需要依赖这种方式，将任意读操作分成2个请求。

### <a class="reference-link" name="KUSER_SHARED_DATA"></a>KUSER_SHARED_DATA

在最新版的Windows 10中，几乎所有虚拟地址都被随机化处理过，包括栈、堆（甚至HAL堆）、PTE等。目前据我所知，唯一例外的是`KUSER_SHARED_DATA`，这是映射到用户态和内核态中的一个结构（及页面），其地址为`0x7ffe0000`以及`0xfffff78000000000`，用户模式及内核模式下的标志分别为`r--`及`rw-`。

由于我们已经拿到了写原语，我们可以将任意数据写入`KUSER_SHARED_DATA`的映射地址。这一点对我们而言非常有用，可以用来伪造一些结构。此外，由于该映射同时存在于两个空间中，因此我们还可以将用户态及内核态的shellcode存放在该位置，从而可以方便地构造用户态shellcode。



## 0x02 地址随机化及实现任意读取

这是利用过程中最有趣的一部分。我曾多次提到过，在攻击最新版的Windows时，我们需要知道确切的地址。由于我们目前无法利用可攻击的头部立即获取一些信息，我们需要找到一种巧妙的方法，完成该任务。

### <a class="reference-link" name="%E7%AC%AC%E4%B8%80%E6%AC%A1%E5%B0%9D%E8%AF%95"></a>第一次尝试

我们碰到的第一个问题在于，被破坏的头部对应的是请求报文，而非响应报文。这表明实现任意读取并不像覆盖`pNetRawBuffer`或其他成员那样简单。如果简单执行覆盖操作，服务端将保持沉默，或者最多返回正常的响应包。

幸运的是，`srv2.sys`提供了一个非常方便的函数：`srv2!Srv2SetResponseBufferToReceiveBuffer`。

```
struct __declspec(align(16)) SRV2_WORKITEM
{ 
  ...
  PSRVNET_BUFFER_HDR psbhRequest; // offset +0xf0
  PSRVNET_BUFFER_HDR psbhResponse; // offset +0xf8
  ...
};

void __fastcall Srv2SetResponseBufferToReceiveBuffer(SRV2_WORKITEM *workitem)
{
  ...
  workitem-&gt;psbhResponse = workitem-&gt;psbhRequest;
  ...
}
```

由于请求和响应报文在payload中共享许多常用数据，因此该函数可以有效地复用这些缓冲区。实际上，当使用`srv2!Srv2SetResponseBufferToReceiveBuffer`来处理响应缓冲区时，`srv2.sys`并不会初始化响应缓冲区。因此，如果我们能够在破坏请求缓冲区后调用该函数，那么就能得到被破坏的响应缓冲区。

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018d90e38af99a4492.png)

此外，`srv2!Smb2SetError`函数中还会调用`srv2!Srv2SetResponseBufferToReceiveBuffer`，而当`srv2.sys`想发送错误消息时就会调用该函数。因此这里总结一下，我们可以精心发送一个请求，使服务端将其识别为“正常但存在错误的”请求，这样就能破坏响应缓冲区。

### <a class="reference-link" name="Memory%20Descriptor%20List"></a>Memory Descriptor List

但现在我们还碰到一个问题：拿到被破坏的缓冲区后我们该怎么做？这里我们选择使用MDL（Memory Descriptor List，内存描述符列表）来解决该问题。由于`tcpip.sys`最终会依赖DMA（Direct Memory Access，直接内存访问）来传输数据包，因此驱动会在MDL中维护缓冲区的物理地址。即使微软在官方文档中没有提到物理地址，但MDL结构中实际上会通过8个成员来包含物理地址：

```
struct _MDL {
  struct _MDL      *Next;
  CSHORT           Size;
  CSHORT           MdlFlags;
  struct _EPROCESS *Process;
  PVOID            MappedSystemVa;
  PVOID            StartVa;
  ULONG            ByteCount;
  ULONG            ByteOffset; 
  // Actually physical addresses follow. 
  // Therefore, the size of this struct is variable
} MDL, *PMDL;
```

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f65dd44bd9ef773c.png)

图. `MmBuildMdlForNonPagedPool`中存放的物理地址

在`SRVNET_BUFFER_HDR`中，`pMDL1`及`pMDL2`为指向MDL结构的指针，描述了由`tcpip.sys`发送给客户端的内存数据。

### <a class="reference-link" name="%E4%BC%AA%E9%80%A0MDL%E7%BB%93%E6%9E%84"></a>伪造MDL结构

现在我们的利用思路逐渐清晰起来。我们希望覆盖请求头中指向MDL的指针，以泄露物理内存信息。然而，这里我们还会面临第三个问题。如果我们像写原语（一个典型的缓冲区溢出）那样覆盖`pMDL`，那么将导致crash，使漏洞无法正常利用。这是因为溢出缓冲区和`pMDL1`之间存在`pNonPagedPoolAddr`，如果我们通过这种方式覆盖`pMDL1`，那么不可避免地也会覆盖掉`pNonPagedPoolAddr`。当`pNonPagedPoolAddr`为无效地址时，由于`srvnet!SrvNetFreeBuffer`迟早会调用`ExFreePoolWithTag(header-&gt;pNonPagedPoolAddr, 0x3030534Cu)`，因此将导致SEGV。

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ef06c6b978c09f3c.png)

图. 错误的方法

如果我们将`pNonPagedPoolAddr`设置为`KUSER_SHARED_DATA`中的某个位置，有可能避免出现crash，但这种方法太过复杂，几乎不可能完成。此外，即使我们凑巧成功释放了该地址，但由于`ExAllocatePoolWithTag`可能返回`KUSER_SHARED_DATA`中的地址（可能导致crash），因此这种方法也不是很方便。

那么我们该怎么办呢？我们应该将`offsetOrLength`设置为较大的一个值，这样`&amp;newHeader-&gt;pNetRawBuffer[compressHeader.offsetOrLength]`将直接指向`pMDL1`的地址，这种方法可以避免`pNonPagedPoolAddr`（至少在“(B)”处的缓冲区溢出点）被覆盖。

但我们还没有完成任务。观察“(C)”处的第二个缓冲区溢出点，由于`&amp;newHeader-&gt;pNetRawBuffer[compressHeader.offsetOrLength-8]`指向`pNonPagedPoolAddr`，因此`memmove`会覆盖`pNonPagedPoolAddr`。我们必须避免出现这种情况，因此我们故意使`srvnet!SmbCompressionDecompress`返回失败，这样将执行`SrvNetFreeBuffer(newHeader)`，但被释放的缓冲区在Lookaside List中依然保持被破坏状态，可以稍后取出使用。

使`srvnet!SmbCompressionDecompress`失败的最简单的一种方法是发送格式错误的`LZNT1` payload，这需要稍微逆向分析`nt!RtlDecompressBufferLZNT1`，但也不难实现。即使我们向`nt!RtlDecompressBufferLZNT1`提供错误的payload，该函数将继续解压缩payload，直至找到无效的chunk为止。因此，我们既可以覆盖`pMDL`，又能同时让解压缩操作失败。

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010bd7186618be421c.png)

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016d314773a4633e81.png)

现在我们已经可以轻松实现读原语：我们只需要使用写原语，在`KUSER_SHARED_DATA`中伪造一个`MDL`结构，然后将`pMDL`指向伪造结构的地址即可。



## 0x03 搞定PML4随机化

现在我们已经能够任意读取物理内存，但现代内核大多数不会直接与物理页面打交道，而是通过MMU提供了一种分页机制，对内存数据（除了某些特例外）的所有访问操作都需要通过分页来完成。内核会跟踪可用的物理页面，根据需要将其链接到虚拟地址。我们可以将分页看成一种分配器，因此无法确定哪个物理页面的具体用处。

然而凡事都有例外，这种规则并不适用于启动过程初始阶段分配的物理内存。在这些页面中，我们重点关注分配给PML4的页面，这是分页机制中的顶层转换表。

需要注意的是，Windows分页机制有个独有的特性：self-reference（自引用）。自引用允许PML4作为PDP（Page Directory Pointer）、PD（Page Directory）以及PT（Page Table）来使用。这种技术的主要优点在于，如果设置了自引用条目的索引，由于PTE的所有虚拟地址都会被立即固定，因此我们可以根据给给定的虚拟地址算出PTE的虚拟地址。这方面内容我建议大家阅读Core Security关于[Windows分页机制](https://www.coresecurity.com/blog/getting-physical-extreme-abuse-of-intel-based-paging-systems-part-2-windows)的相关报告了解更多细节。

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0115591414223ad2b0.png)

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a43801c8dba501a5.png)

根据Core Security另一篇文章的描述，在内核利用中，修改PTE是目前用来创建攻击所需内存空间的一种典型方法，但微软已经已经在Anniversary Update中针对该方法推出了缓解机制。这并不意味着Windows 10不再依赖自引用，Windows只是随机化处理了PML4中自引用条目的索引，这样最终导致PML4及PET虚拟地址的随机化。

前面我们解释了PML4虚拟地址的随机化，那么PML4物理地址是什么情况呢？大家可能能够猜到，该地址并没有经过随机化处理。PML4空间在`ArchpAllocateAndInitializePageTables`中分配，该函数是BIOS/UEFI中实现的一个函数。我们逆向分析了`bootmgr.exe`及`bootmgfw.efi`，确认其中并没有专门设置的随机化过程。需要注意的是，这并不意味着其中为PML4定义了固定的物理地址。因此，我们需要再次在qemu、VMWare、VirtualBox及ThinkPad中检查PML4的物理地址。在测试的每个环境中，PML4的物理地址为`0x1aa000`（BIOS）或者`0x1ad000`（UEFI）。在未测试的其他环境中（比如hypervisor），这个地址可能有所变化，但我们可以认为在大多数情况下PML4的物理地址为固定值。

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014e8a21f28d22c315.png)

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014b85b856680123ab.png)

因此，现在我们可以使用物理读源于来dump PML4。由于我们可以像MMU一样读取物理页面，现在我们也可以读取PDPE、PDE以及PTE，这样我们就能将虚拟地址转化为物理地址，从而实现虚拟读原语。将虚拟地址转化为对应的物理地址后，我们可以使用物理读源于来读取虚拟地址数据。



## 0x04 获取IP及绕过CFG

实现读写原语后，我们的漏洞利用也即将成功，我们还需要找到用来控制IP（指令指针）的函数指针。如果大家想复现RCE PoC，这里我提供3种可能采用的策略。

### <a class="reference-link" name="%E7%AD%96%E7%95%A51"></a>策略1

> 我们考虑过这个策略，但并没有采用该策略（但可能还有利用价值）。

由于我们可以根据虚拟地址实现任意读取，为了找到IP，我们可以在内核堆的“垃圾”中查找有用的地址。大家可以采用前文类似的方法来完成该任务。

比如，假设`pNetRawBuffer`的初始值为`X`。首先，我们覆盖掉`pNetRawBuffer`，使其指向某个位置（比如地址`Y`）。随后，`srv2.sys`中的后续操作会引用`Y`，这样`X`将处于未初始化状态。根据前文描述，由于MDL（物理地址为`X`）用来指定被泄露的数据，因此我们可以在内核堆上看到未初始化内存地址`X`的数据。通过这种方式拿到有效地址后，我们可以继续利用虚拟读原语来获取更多地址，知道我们找到待覆盖的函数指针为止。

然而，我们并没有采用这种策略，因为以来未初始化数据并不是特别可靠。如果这是常规的用户态利用场景，那么这种方法可能不会那么随机化，或者不会那么不稳定。然而，由于内核中许多线程在运行时会共享内核堆，因此并不满足这种场景。根据这些信息，我们并不能保证每次都能找到有用的地址。

### <a class="reference-link" name="%E7%AD%96%E7%95%A52"></a>策略2

实际上我们采用的是这个策略，我们在HAL堆上搜索PML4的物理页面。与PML4的物理页面不同，HAL堆的物理地址与操作系统紧密相关。Alex Ionescu在某次演讲中详细解释了这方面内容，后面我也会讨论其中的一些关键点。

虽然HAL堆的物理地址与具体环境紧密相关，但我们可以通过暴力方式来搜索该页面。我们同样在几个环境中测试了物理地址，发现该地址最多为`0x10f000`。

此外，我们还可以检查泄露处的页面是否为真正的HAL堆。我们寻找的是[HalpInterruptController](https://labs.bluefrostsecurity.de/blog/2017/05/11/windows-10-hals-heap-extinction-of-the-halpinterruptcontroller-table-exploitation-technique/)，其中包含指向HAL函数的一些指针。对比泄露地址与这些函数的偏移地址后，我们可以得出准确的结论（虽然这种方法依赖于具体的Windows 10版本，需要我们设定所有可能的偏移地址组合）。

### <a class="reference-link" name="%E7%AD%96%E7%95%A53"></a>策略3

这可能是更通用的一种策略。我们还没有测试过这种策略，因为我在撰写该报告时才发现别人的[演讲资料](https://www.youtube.com/watch?v=RSV3f6aEJFY)，我发现该资料能够提供更可靠的方法。参考该资料，我们可以在大多数系统上读取`0x1000`处的物理地址，从而获取PML4的物理地址以及其他一些有用的虚拟地址。这样漏洞利用起来更快，也更为通用。



## 0x05 最后的障碍

以上就是我们获取IP、执行内核态shellcode的方式。我的内核态shellcode比较普通，[两次调用APC](http://rce4fun.blogspot.com/2019/04/circumventing-windows-defender-atps.html)（异步过程调用）来拿到反弹shell，但一开始我并没有成功运行。

在调试内核和shellcode时，我发现用户态CFG未能正确识别用户态shellcode，会拦截我们的利用操作。如下图所示，在转入用户态shellcode前，`ntdll!KiUserApcDispatch`会调用`ntdll!LdrpValidateUserCallTarget`。

[![](./img/203683/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0177abd081839b3f37.png)

由于我们可以在内核态shellcode中patch `ntdll!LdrpValidateUserCallTarget`，因此可以解决该问题（但也花了我1天的时间来调试）。由于互联网上似乎没人提到过这一点，因此我想在这里与大家分享这个细节。



## 0x06 总结

在本文中，我们引入了一种读原语，成功在最新版Windows上实现了远程内核利用。我们花了很多时间完成此次研究（以及撰写这份报告），因此也很乐意与大家分享。
