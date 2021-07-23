> 原文链接: https://www.anquanke.com//post/id/86144 


# 【技术分享】Bitdefender在处理PE代码签名的organizationName字段时存在缓冲区溢出漏洞


                                阅读量   
                                **74739**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blogs.securiteam.com
                                <br>原文地址：[https://blogs.securiteam.com/index.php/archives/3211](https://blogs.securiteam.com/index.php/archives/3211)

译文仅供参考，具体内容表达以及含义原文为准

 [![](https://p1.ssl.qhimg.com/t014e1384d916523c6b.jpg)](https://p1.ssl.qhimg.com/t014e1384d916523c6b.jpg)



翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：110RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、漏洞概要**

本文描述了Bitdefender PE引擎中存在的一个缓冲区溢出漏洞。

Bitdefender提供了“反恶意软件（antimalware）”引擎，该引擎可以集成到其他安全厂商的产品中，Bitdefender在自家产品中（如Bitdefender Internet Security 2017及以下版本）也使用了该引擎。在安全产品的众多功能中，反恶意软件引擎是核心功能，用于扫描潜在的恶意便携式可执行文件（portable executable，PE）。

<br>

**二、漏洞细节**



PE文件可以使用X.509证书进行签名。签名机制可确保可执行文件内容没被篡改，且文件来自于可信来源。

证书信息存放在PE数据的某个目录中，该目录由IMAGE_NT_HEADERS.IMAGE_OPTIONAL_HEADER字段进行定义。

PE文件中的IMAGE_NT_HEADERS结构体以特征字符“PE”开始：



```
typedef struct _IMAGE_NT_HEADERS `{`
    DWORD Signature; "PE"
    IMAGE_FILE_HEADER FileHeader;
    IMAGE_OPTIONAL_HEADER OptionalHeader;
`}` IMAGE_NT_HEADERS32, *PIMAGE_NT_HEADERS32;
```

IMAGE_OPTIONAL_HEADER结构体的最后部分包含若干个类型为IMAGE_DATA_DIRECTORY的DataDirectory结构体：



```
WORD                               Magic
BYTE                                 MajorLinkerVersion
...
DWORD                             LoaderFlags
DWORD                                   NumberOfRvaAndSizes
IMAGE_DATA_DIRECTORY    DataDirectory[16]
----------------------------------------------------
typedef struct _IMAGE_DATA_DIRECTORY `{`
    DWORD   VirtualAddress;     // RVA of the data
    DWORD   Size;               // Size of the data
`}`;
```

DataDirectory[4]代表的是IMAGE_DIRECTORY_ENTRY_SECURITY，指向一个包含WIN_CERTIFICATE结构体的列表。VirtualAddress字段指的是文件偏移量，而不是RVA（相对虚拟地址，Relative Virtual Address）。

**WIN_CERTIFICATE结构体**的定义如下所示：



```
typedef struct _WIN_CERTIFICATE `{`
  DWORD dwLength;
  WORD  wRevision;
  WORD  wCertificateType;
  BYTE  bCertificate[ANYSIZE_ARRAY];
`}` WIN_CERTIFICATE, *PWIN_CERTIFICATE;
```

vsserv.exe是Bitdefender的系统服务，该进程会自动扫描PE文件，通过cevakrnl.rv8模块分析PE文件的数字签名。cevakrnl.rv8模块是一个压缩模块，位于“%ProgramFiles%Common FilesBitdefenderBitdefender Threat ScannerAntivirus_…Plugins”目录。

Bitdefender服务启动时，会解压cevakrnl.rv8模块，并将其加载为可执行代码。当处理经过签名的PE文件时，cevakrnl.rv8!sub_40ACFF0()函数就会被调用。



```
cevakrnl.rv8:040AE691                 lea     eax, [ebp+var_2C]
cevakrnl.rv8:040AE694                 push    eax             ; &amp;(ebp-0x2C) - object placed on the stack
cevakrnl.rv8:040AE695                 call    sub_40ACFF0     ; call here
 
cevakrnl.rv8!sub_40ACFF0() extracts the IMAGE_DIRECTORY_ENTRY_SECURITY offset and size fields.
 
cevakrnl.rv8:040ACFF0 sub_40ACFF0     proc near               ; CODE XREF: sub_40AE5C0+D5p
cevakrnl.rv8:040ACFF0
...
cevakrnl.rv8:040AD007                 mov     edi, [ebp+arg_0]
...
cevakrnl.rv8:040AD025                 mov     eax, [edi+4]    ; eax = IMAGE_NT_HEADERS
cevakrnl.rv8:040AD025                                         ; contains at
cevakrnl.rv8:040AD025                                         ; offset  0x0: DWORD Signature ("PE");
cevakrnl.rv8:040AD025                                         ; offset  0x4: IMAGE_FILE_HEADER FileHeader;
cevakrnl.rv8:040AD025                                         ; offset 0x18: IMAGE_OPTIONAL_HEADER32 OptionalHeader;
cevakrnl.rv8:040AD028                 mov     [ebp+arg_0_bkup], edi
cevakrnl.rv8:040AD02E                 mov     [ebp+numofcrcs], ecx
cevakrnl.rv8:040AD034                 mov     [ebp+var_1F0], ecx
cevakrnl.rv8:040AD03A                 mov     esi, [eax+9Ch]  ; attribute certificate size
cevakrnl.rv8:040AD03A                                         ; OptionalHeader.DataDirectory+0x24
cevakrnl.rv8:040AD03A                                         ; = IMAGE_DIRECTORY_ENTRY_SECURITY.Size
cevakrnl.rv8:040AD040                 mov     edx, [eax+98h]  ; attribute certificate offset
cevakrnl.rv8:040AD040                                         ; OptionalHeader.DataDirectory+0x20
cevakrnl.rv8:040AD040                                         ; = IMAGE_DIRECTORY_ENTRY_SECURITY.Offset
cevakrnl.rv8:040AD040                                         ; "Points to a list of WIN_CERTIFICATE structures, defined in WinTrust.H"
```

程序会从先前定义的偏移量处读取不超过0x2400个字节的数据，并将该数据载入到堆缓冲区中。



```
cevakrnl.rv8:040AD092                 cmp     esi, 2400h      ; maximum size
cevakrnl.rv8:040AD098                 jbe     short @max
cevakrnl.rv8:040AD09A                 mov     esi, 2400h
cevakrnl.rv8:040AD09F @max:                                   ; CODE XREF: sub_40ACFF0+A8j
...
cevakrnl.rv8:040AD0C4                 lea     eax, [ebp+var_1C4]
cevakrnl.rv8:040AD0CA                 push    eax             ; int
cevakrnl.rv8:040AD0CB                 push    esi             ; size
cevakrnl.rv8:040AD0CC
cevakrnl.rv8:040AD0CC loc_40AD0CC:                            ; CODE XREF: sub_40ACFF0+CEj
cevakrnl.rv8:040AD0CC                 mov     ebx, [ebp+buf]
cevakrnl.rv8:040AD0D2                 mov     edi, [ebp+arg_0_bkup]
cevakrnl.rv8:040AD0D8                 push    ebx             ; buf
cevakrnl.rv8:040AD0D9                 push    edx             ; offset
cevakrnl.rv8:040AD0DA                 push    edi             ; int
cevakrnl.rv8:040AD0DB                 call    readatoffset    ; read all structures
cevakrnl.rv8:040AD0DB                                         ;   typedef struct _WIN_CERTIFICATE `{`
cevakrnl.rv8:040AD0DB                                         ;     DWORD dwLength;
cevakrnl.rv8:040AD0DB                                         ;     WORD wRevision;
cevakrnl.rv8:040AD0DB                                         ;     WORD wCertificateType;
cevakrnl.rv8:040AD0DB                                         ;     BYTE bCertificate[ANYSIZE_ARRAY];
cevakrnl.rv8:040AD0DB                                         ;   `}` WIN_CERTIFICATE,*LPWIN_CERTIFICATE;
```

经过一些无关紧要的操作后，Bitdefender开始在待处理数据中搜索X.509中的“organizationName”属性。程序会搜索0x0A045503这个dword来定位该属性，这个dword是organizationName OID 2.5.4.10的ASN.1表示形式。



```
cevakrnl.rv8:040AD320 @startloop:                             ; CODE XREF: sub_40ACFF0+326j
cevakrnl.rv8:040AD320                                         ; sub_40ACFF0+728j
cevakrnl.rv8:040AD320                 mov     ecx, [ebp+buf]
cevakrnl.rv8:040AD326                 mov     eax, [ecx+esi]  ; current dword
cevakrnl.rv8:040AD329                 lea     ebx, [ecx+esi]
cevakrnl.rv8:040AD32C                 mov     [ebp+var_208], ebx
cevakrnl.rv8:040AD332                 cmp     eax, 0A045503h  ; 55:04:0A = X.509 "id-at-organizationName" attribute
cevakrnl.rv8:040AD337                 jz      short @found
```

当程序找到“organizationName”时，该字段对应的字符串值会经某个调用传递给负责计算CRC32校验码的函数，该函数会返回该字符串经反转处理（即按位取非（NOT））后的CRC32校验值。

请注意，在“organizationName”中，只有可打印的ASCII字符（0x20-0x7E）才会被认为是有效字符。



```
cevakrnl.rv8:040AD3B8 @found:                                 ; CODE XREF: sub_40ACFF0+347j
cevakrnl.rv8:040AD3B8                                         ; sub_40ACFF0+357j
cevakrnl.rv8:040AD3B8                 mov     bl, [ecx+esi+5] ; value string length
cevakrnl.rv8:040AD3BC                 movzx   eax, bl
cevakrnl.rv8:040AD3BF                 mov     [ebp+var_20C], eax
cevakrnl.rv8:040AD3C5                 add     eax, 6
cevakrnl.rv8:040AD3C8                 add     eax, esi
cevakrnl.rv8:040AD3CA                 mov     [ebp+var_1E8], 0
cevakrnl.rv8:040AD3D4                 mov     [ebp+var_40], 0
cevakrnl.rv8:040AD3D8                 mov     [ebp+savedcrc], 0
cevakrnl.rv8:040AD3E2                 mov     [ebp+after_value_string], eax ; offset to next data
...
cevakrnl.rv8:040AD444                 mov     eax, [ebp+buf]
cevakrnl.rv8:040AD44A                 add     eax, 6
cevakrnl.rv8:040AD44D                 mov     [ebp+edi+var_40], 0
cevakrnl.rv8:040AD452                 add     eax, esi        ; offset + 6
cevakrnl.rv8:040AD452                                         ; points to value string
cevakrnl.rv8:040AD454                 push    edi             ; length of string
cevakrnl.rv8:040AD455                 push    eax             ; Organization in certificate
cevakrnl.rv8:040AD456                 call    crc32           ; crc32
cevakrnl.rv8:040AD45B                 add     esp, 8          ; this returns ~crc32
cevakrnl.rv8:040AD45B                                         ; ~crc32("31TZnp") = 0xdeadbeef
```

如果之前没处理过该CRC值：



```
cevakrnl.rv8:040AD480 @checkduplicate:                        ; CODE XREF: sub_40ACFF0+488j
cevakrnl.rv8:040AD480                                         ; sub_40ACFF0+4A0j
cevakrnl.rv8:040AD480                 cmp     [ebp+ecx*4+crc32results], eax ; array of already saved CRCs
cevakrnl.rv8:040AD487                 jz      @duplicate
cevakrnl.rv8:040AD48D                 inc     ecx
cevakrnl.rv8:040AD48E                 cmp     ecx, ebx
cevakrnl.rv8:040AD490                 jb      short @checkduplicate
```

该值会存放在某个大小为8个dwords的本地栈数组中。对于每个不同的CRC值，这个数据的索引都会相应地增加，但程序却没有检查数组的大小限制。这样一来，如果程序在处理过程中遇到数量足够的不同的“organizationName”值时，就会导致基于栈的缓冲区溢出漏洞。



```
-000001B8 crc32results    dd 8 dup(?)
-00000198 var_198         db 256 dup(?)
...
cevakrnl.rv8:040AD51E                 mov     eax, [ebp+savedcrc]
cevakrnl.rv8:040AD524                 mov     [ebp+ebx*4+crc32results], eax ; buffer overflow
cevakrnl.rv8:040AD524                                         ; [ebp+ebx*4-0x1B8] = eax
cevakrnl.rv8:040AD52B                 inc     ebx
cevakrnl.rv8:040AD52C                 mov     [ebp+numofcrcs], ebx
```

攻击者可以利用这个漏洞将大量任意数据覆盖到栈中。通过逆向CRC32算法可知，我们可以构造某个ASCII字符串，生成我们需要的CRC值，从而将任意数据写入栈中。

虽然存在该漏洞的函数会在返回时检查某个cookie值，我们还是可以在函数返回之前，将某个对象放置于栈中，从而实现代码执行。

该对象作为第一个参数传递给存在漏洞的函数，位于0x1C偏移处（PoC中该值更改为0xdeadbeef）的字段会被传递给global_function0()函数。



```
cevakrnl.rv8:040AD750                 mov     ebx, [ebp+arg_0_bkup] ; ebx points to the stack of the caller function, 
                                                                                                                       ; which is above crc32results
...
cevakrnl.rv8:040AD785                 push    0
cevakrnl.rv8:040AD787                 push    1
cevakrnl.rv8:040AD789                 push    41C40Eh
cevakrnl.rv8:040AD78E                 push    6
cevakrnl.rv8:040AD790                 push    dword ptr [ebx+1Ch] ; corrupted
cevakrnl.rv8:040AD793                 call    global_function0
```

global_function0()函数会调用sub_2F70B90()，并将[0xdeadbeef+0x22C]处数据作为当前对象传递给调用的函数。



```
seg001:02F5D69F                 mov     ecx, [ecx+22Ch] ; crash here
seg001:02F5D69F                                         ; ecx is controlled
seg001:02F5D6A5                 push    [ebp+arg_4]
seg001:02F5D6A8                 call    sub_2F70B90
```

sub_2F70B90()函数会从当前对象指针中提取一个dowrd：



```
seg001:02F70BFA                 mov     edi, [esi+eax*4] ; eax - fixed offset = 0x560
```

最终该数据会作为当前对象传递给sub_2F6F120()函数：



```
seg001:02F70D45                 mov     ecx, edi
seg001:02F70D47                 call    sub_2F6F120
```

sub_2F6F120()最终会从某个指针中提取一个dword，这个指针有可能是攻击者构造的任意指针，这样会导致程序跳转到某个任意地址上。



```
seg001:02F6F132                 mov     eax, [edi+4]
seg001:02F6F135                 push    ebx
seg001:02F6F136                 push    dword ptr [esi+4]
seg001:02F6F139                 push    edi
seg001:02F6F13A                 call    eax
```

能否跳转到任意地址取决于攻击者能否将构造的内容存放到某个固定的地址中。攻击者可以通过堆喷射（heap spraying）技术实现这一目标。根据Bitdefender引擎的复杂度，我们认为这种可能性是存在的。

<br>

**三、其他说明**

感谢独立安全研究员Pagefault将该漏洞报告给SecuriTeam安全披露项目。

Bitdenfender已经在7.71417版中修复了该漏洞。


