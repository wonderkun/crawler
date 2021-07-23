> 原文链接: https://www.anquanke.com//post/id/151357 


# 针对一个Uroburos恶意软件新样本的分析


                                阅读量   
                                **156523**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exatrack.com
                                <br>原文地址：[https://exatrack.com/public/Uroburos_EN.pdf](https://exatrack.com/public/Uroburos_EN.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t016b200f785f93319f.jpg)](https://p5.ssl.qhimg.com/t016b200f785f93319f.jpg)

Uroburos是在APT攻击中出现的一种恶意软件，于2014年被发现，并对计算机安全领域构成了很大的威胁。它的与众不同之处在于它的64位Windows驱动程序（Rootkit），包括一个PatchGuard的旁路。此外，驱动程序没有经过签名，恶意软件利用第三方驱动程序中的漏洞实现内核执行。有关这个恶意软件在过去研究中的更多细节，你可以阅读Andrzej Dereszowski和Matthieu Kaczmarek发表的[文章](http://artemonsecurity.com/uroburos.pdf)。

几个月前，我们发现了一个从2017年开始传播的Uroburos/Turla样本。在调查之后，其中的驱动程序被证明是基于2014年的改进版本。我们看了一下这个新的驱动程序，发现它与原来的驱动程序有一些很大的差异，尽管有一个共同的基础。在本文中，我们将分析这个64位Rootkit的一些新特性。我们的分析将集中在如何从内存转储（memory dump）中识别这个Rootkit（正如我们在搜索威胁时所做的那样），然后我们将研究其新的通信协议。我们的目标是希望能够远程识别Rootkit的存在，而无需在服务器上进行身份验证。应该注意的是，Rootkit只针对服务器。

我们要分析的代码位于：[https://www.virustotal.com/en/file/f28f406c2fcd5139d8838b52da703fc6ffb8e5c00261d86aec90c28a20cfaa5b/analysis](https://www.virustotal.com/en/file/f28f406c2fcd5139d8838b52da703fc6ffb8e5c00261d86aec90c28a20cfaa5b/analysis)

为了在服务器上进行威胁搜索，我们使用了Comae DumpIt工具（https://www.comae.io/），并分析了该工具生成的故障转储（crush dump）。



## 识别内核威胁

驱动程序在内核空间中隐藏得很好，它不存在于已加载模块列表中，而且其他模块的完整性也都保持良好。

为了辅助分析，我们将使用ExaTrack开发的一个内部工具，该工具旨在检查内核的完整性，并提示当前潜在的异常问题。

Windows回调（callback）系统是我们检查的关键组件之一，它允许在某些事件（例如进程创建）中调用任意函数。在我们的样本中，通过观察它们，我们发现了一个异常：

```
&gt;&gt;&gt; ccb 

# Check CallBacks 

[*] Checking CallbackTcpConnectionCallbackTemp : 0xfffffa8002f38360 

[*] Checking CallbackTcpTimerStarvationCallbackTemp : 0xfffffa8004dfd640 

[*] Checking CallbackLicensingData : 0xfffffa80024bc2f0 

[...] 

[*] PspLoadImageNotifyRoutine 

[*] PspCreateProcessNotifyRoutine 

Callback fffffa8004bc2874 -&gt; SUSPICIOUS ***Unknown*** 48895c2408574881ec30010000488bfa
```

在创建过程时，会调用PspCreateProcessNotifyRoutine列表中的回调函数。向它添加一个条目是非常有趣的，可以修改新进程的数据和行为。在前面的命令中，该工具识别了一个被认为可疑的条目，因为它指向一个未分配给驱动程序的内存地址。

在回调中还存在第二个异常，它不太明显，因为它不会对系统的操作造成很深的影响，但会对其进行略微的改动。

```
[...] 

[*] IopNotifyShutdownQueueHead 

 Name : Null 

 Driver Object : fffffa80032753e0 

   Driver : DriverNull 

   Address: fffff88001890000 

   Driver : Null.SYS 

 Name : 000000a6 

 Driver Object : fffffa8003d2adb0 

   Driver : Driverusbhub 

   Address: fffff88000da6000 

   Driver : usbhub.sys 

[...] 

&gt;&gt;&gt; cirp DriverNull 

Driver : DriverNull 

Address: fffff88001890000 

Driver : Null.SYS 

DriverUnload : fffff88001895100 c:windowssystem32driversnull.sys 

IRP_MJ_CREATE fffff88001895008 Null.SYS 

IRP_MJ_CREATE_NAMED_PIPE fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_CLOSE fffff88001895008 Null.SYS 

IRP_MJ_READ fffff88001895008 Null.SYS 

IRP_MJ_WRITE fffff88001895008 Null.SYS 

IRP_MJ_QUERY_INFORMATION fffff88001895008 Null.SYS 

IRP_MJ_SET_INFORMATION fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_QUERY_EA fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_SET_EA fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_FLUSH_BUFFERS fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_QUERY_VOLUME_INFORMATION fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_SET_VOLUME_INFORMATION fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_DIRECTORY_CONTROL fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_FILE_SYSTEM_CONTROL fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_DEVICE_CONTROL fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_INTERNAL_DEVICE_CONTROL fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_SHUTDOWN fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_LOCK_CONTROL fffff88001895008 Null.SYS 

IRP_MJ_CLEANUP fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_CREATE_MAILSLOT fffff80002abb1d4 ntoskrnl.exe 

IRP_MJ_QUERY_SECURITY fffff80002abb1d4 ntoskrnl.exe
```

当系统关闭时，要调用的模块列表中会引用“DriverNull”驱动程序。但实际上，这个驱动程序本不应该出现在这个列表中。但是它的IRP表似乎没有被修改，甚至指向ntoskrnl（对于IRP_MJ_SHUTDOWN接口）。我们没有发现这种行为有什么真正的用处。

让我们继续进行故障排除，Windows在其输入输出（IO）处理程序中有许多过滤系统。在这些IO中，网络被分成了几个部分，我们将会对其中一个进行深入研究，即NetIO。

NetIo也提供了一个回调系统，允许对交换的网络数据进行操作，这些回调被称为“Callout”。但由于进行的是网络回调，因此这些结构没有被记录，也没有出现在Windows符号文件中。这些特性使它成为植入恶意软件的好地方。在转储中，我们可以找到5个回调，这些回调指向不属于任何驱动程序的代码。

```
&gt;&gt;&gt; cnetio 

[*] NetIo Callouts (callbacks) : fffffa8004965000 (4790) 

Callback fffffa8004bd9580 -&gt; SUSPICIOUS ***Unknown*** 488bc448895808488950105556574154 

Callback fffffa8004bca6b0 -&gt; SUSPICIOUS ***Unknown*** 33c0c3cc40534883ec20488b89500100 

Callback fffffa8004bd9af8 -&gt; SUSPICIOUS ***Unknown*** 4883ec286683f91474066683f916750f 

Callback fffffa8004bd9ca0 -&gt; SUSPICIOUS ***Unknown*** 48895c24084889742410574883ec4048 

Callback fffffa8004bd9de0 -&gt; SUSPICIOUS ***Unknown*** 4c8bdc49895b0849896b104989731857
```

我们将在文档的后面部分更详细地研究这些函数中的其中一个。

最后，我们将搜索试图隐藏在Windows中的已加载的驱动程序。

```
&gt;&gt;&gt; pe 

[...] 

[OK] fffff88001899000 : SystemRootSystem32DriversBeep.SYS 

[OK] fffff88000da6000 : SystemRootsystem32DRIVERSusbhub.sys 

[NO] fffffa8004bb8000 (Header overwritten) 

[OK] fffff88006a00000 : SystemRootsystem32DRIVERSE1G6032E.sys 

[OK] fffff880017d2000 : SystemRootSystem32DriversNpfs.SYS

[...] 

&gt;&gt;&gt; dq fffffa8004bb8000 100 

FFFFFA8004BB8000 0000000300000000 0000FFFF00000004 ....?...?...¦¦.. 

FFFFFA8004BB8010 00000000000000B8 0000000000000040 ........@....... 

FFFFFA8004BB8020 0000000000000000 0000000000000000 ................ 

FFFFFA8004BB8030 0000000000000000 000000D800000000 ................ 

FFFFFA8004BB8040 CD09B4000EBA1F0E 685421CD4C01B821 ??.?....!.?L.!Th 

FFFFFA8004BB8050 72676F7270207369 6F6E6E6163206D61 is program canno 

FFFFFA8004BB8060 6E75722065622074 20534F44206E6920 t be run in DOS

FFFFFA8004BB8070 0A0D0D2E65646F6D 0000000000000024 mode....$....... 

FFFFFA8004BB8080 095520395A3B417D 0955203909552039 `}`A;Z9 U.9 U.9 U. 

FFFFFA8004BB8090 095520A609542039 0955203C092E28A6 9 T.. U..(..&lt; U. 

FFFFFA8004BB80A0 0955203B0928E61E 095520510938E61E ?.(.; U.?.8.Q U. 

FFFFFA8004BB80B0 09552038092FE61E 09552038092DE61E ?./.8 U.?.-.8 U. 

FFFFFA8004BB80C0 0955203968636952 0000000000000000 Rich9 U......... 

FFFFFA8004BB80D0 0000000000000000 0006866400000000 ............d.?. 

FFFFFA8004BB80E0 000000005900F3CF 202200F000000000 ...Y.........." 

FFFFFA8004BB80F0 00042E000008020B 000000000001BC00 ??....?...?..... 

&gt;&gt;&gt; list fffffa8004bb8000 fffffa8004bbb000 

FFFFFA8004BB8000 rwx- 

FFFFFA8004BB9000 rwx- 

FFFFFA8004BBA000 rwx-
```

在这里，一个重要的异常是可以观察到的。一个驱动程序存在于内存中，并且已经覆盖了它的MZ和PE标头，可能是为了隐藏自己，使其不受原始内存搜索的影响。它的寻址对应于我们之前的回调，并以RWX权限进行映射。

目前发现的所有证据都表明了该恶意软件是从内核运行的。现在，我们将分析它的一些代码（主要是网络通信），以了解它是如何工作的。



## 驱动程序分析

### 入口点

在初始化过程中，驱动程序将迅速瞄准“空（Null）”设备。它检索指向对象的指针，并将其注册到前面提到的“关机（shutdown）”回调列表中。另外，它还在进程创建期间注册了调用的回调函数。

```
[...] 

  if ( (unsigned int)get_top_deviceObjet(L"\Device\Null", &amp;device_obj_null) 

    &amp;&amp; (result = get_top_deviceObjet(L"\Device\Beep", &amp;device_obj_null), (_DWORD)result) ) 

  `{` 

    __asm `{` xchg rbx, qword ptr cs:isNullDeviceFailed `}` 

  `}` 

  else

  `{` 

    v5 = IoRegisterShutdownNotification(device_obj_null); 

    if ( v5 || (drvobj_null = device_obj_null-&gt;DriverObject, (v5 = sub_4E21C(byte_1188D)) != 0) ) 

[...] 

      PsSetCreateProcessNotifyRoutine(cbCreateProcess, 0i64); 

[...]
```

### 加密字符串

为了避免容易被反病毒软件识别，所有与Uroburos相关的字符串都被加密。每个加密数据块的大小都是0x40字节，并用前一个0x40字节执行异或（XOR）操作。

[![](https://p5.ssl.qhimg.com/t0138afa653f924da28.jpg)](https://p5.ssl.qhimg.com/t0138afa653f924da28.jpg) 

解密函数见下面。基于此，破译完整的攻击链是可能的。

```
Python&gt;def decrypt(addr, clen): return ''.join(chr(b) for b in

[struct.unpack('B'*clen,idaapi.get_many_bytes(addr,64))[a] ^

struct.unpack('B'*clen,idaapi.get_many_bytes(addr-clen,clen))[a] for a in xrange(clen)])

Python&gt;[decrypt( 0x53530 + (i*0x80) , 0x40).replace("x00",'') for i in xrange(38)]

['system', 'isapi_http', 'isapi_log', 'isapi_dg', 'isapi_openssl', 'shell.`{`F21EDC09-85D3-

4eb9-915F-1AFA2FF28153`}`', 'Hd1', 'Hd2', 'RawDisk1', 'RawDisk2', 'wininet_activate',

'dmtev', 'Ultra3', 'Ultra3', 'services_control', 'fixdata.dat', '$NtUninstallQ817473$',

'fdisk.sys', 'fdisk_mon.exe', '400', '16', '`{`AAAA1111-2222-BBBB-CCCC-DDDD3333EEEE`}`',

'~WA434.tmp', '~WA4276.tmp', '.', '~WA356.tmp', 'rasmon.dll', 'rasman.dll', 'user',

'internat', 'NTUSER.DAT', 'ntuser.dat.LOG1', '.', 'mscrt.dll', 'msvcrt.dll', '0', '1',

'.']
```

在附录中，我们提供了加密函数的YARA规则。

### 网络拦截

如上所示，网络回调已经被安装。它们将通过函数“FwpsCalloutRegister0”（允许添加网络过滤器）注册，并能够控制驱动程序传输或不传输接收到的数据。

```
v20 = addCalloutAddress(

    &amp;stru_14930,

    &amp;a2,

    DeviceObject,

    (__int64)intercept_packet,

    (__int64)&amp;ret_null,

    (__int64)a6,

    (__int64)&amp;v47,

    (__int64)&amp;v34,

    &amp;a9,

&amp;a10);
```

“intercept_packet”函数（位于内存转储中的地址fffa8004bd9580处）将分析经过网络连接的数据。有趣的是，它不会查看经过139端口的数据。对于其他端口，它将只查看接收到的数据，并且只在主机是服务器的情况下。

```
if ( v9 || LOWORD(a1-&gt;layerId) == 20 &amp;&amp; a1-&gt;pIP_infos-&gt;src_port == 139 )

    return;

if ( LOWORD(a1-&gt;layerId) == 22 &amp;&amp; a1-&gt;pIP_infos-&gt;src_port == 139 )

    return;

[...]

    fwpsCopyStreamDataToBuffer0(v8, datas_tcp_buffer, *(_QWORD *)(v8 + 48), &amp;v31);

[...]

    buffer_type_2 = find_and_decode_datas(datas_tcp_buffer, v24, *((_DWORD *)v11 + 0x1FF) == 0, &amp;a4a);
```

“find_and_decode_datas”函数负责测试不同的已接受的通信协议。在我们的样本中，我们将研究HTTP通信。我们的目标是想看看，是否有可能远程确认服务器是否被Uroburos入侵。

恶意软件会验证接收到的消息是否是一个标准的HTTP请求。然后，它将在HTTP标头的一个参数中查找隐藏的消息。

```
if ( space_offset_1 != 3i64

    || ((v18 = *(_WORD *)Buf &lt; (unsigned __int16)str_GET, *(_WORD *)Buf !=

(_WORD)str_GET)

    || (v19 = Buf[2], v18 = (unsigned __int8)v19 &lt; BYTE2(str_GET), v19 != BYTE2(str_GET)) ? (v20 = -v18 - (v18 - 1)) : (v20 = 0), v20) )

    `{`

        if ( space_offset_1 != 4 || *(_DWORD *)Buf != str_POST )

            return 0i64;

    `}`

[...]

    if ( *(_DWORD *)start_word_2 != *(_DWORD *)"http://"

[...]

    if ( v33 != *(_DWORD *)"HTTP/" || (v35 = v32[4], v34 = v35 &lt; aHttp_0[4], v35 !=

aHttp_0[4]) )

[...]

    || !(unsigned int)check_and_decode_buffer(&amp;Buf[nextline], v14, response_tag, out_decoded_b64, v7) )

[...]

“check_and_decode_buffer”函数将查找第一个“:”字符，并尝试在相应的HTTP参数中找到一个隐藏的消息。

v15 = memchr(v10, ':', (unsigned int)(v14 - 1));

if ( !v15 || *((_BYTE *)v15 + 1) != ' ' )

    return (unsigned int)v5;
```

然后，通过几个校验和（checksum）来检查信息。

```
v10 = get_checksum(datas, 12);

result = (unsigned __int64)reverse_littleendian(v10) == *(_DWORD *)v4;

校验和函数使用的是一个经修改后的“threefish256”算法。

crypto_it(v3, v6, (v5 - 1) &gt;&gt; 5, 32);

[...]

memcpy((void *)(v3 + *(_QWORD *)(v3 + 8) + 64), v6, v5);

*(_QWORD *)(v3 + 8) += v5;
```

该过程会运行三次散列函数，以获得最终的散列值。第一次使用允许初始化数据的静态缓冲区，第二次使用要散列的数据，最后一次使用该数据的散列值。最终获得的散列值将会以4字节为单位进行截断，并以此作为校验和。一个密钥被初始化，我们猜测针对每个目标都会有一个不同的密钥。它将用于计算散列值，但不会在请求中发送。

要传递的信息包含在每一行的末尾，它的格式为7个节的容+1个节的校验和，而校验和只是前7个字节的总和。随后，恶意软件会对这8个字节进行Base64编码。

HTTP请求数据将按如下方式进行调整：

[![](https://p0.ssl.qhimg.com/t01620e9015ae44d800.jpg)](https://p0.ssl.qhimg.com/t01620e9015ae44d800.jpg)有趣的是，“代码（Code）”元素并没有出现在最终的查询中。实际上可以使用四个值，它们是在验证过程中被恶意软件强制使用的。

当服务器与此类请求（在已打开的端口上）进行联系时，应答我们的是Rootkit （数据不会转移到用户空间）。

如果收到的信息对应于预期的格式，驱动程序将发送一个可变大小的响应，并采用随机字节填充。

```
if ( reply_datas[6] &amp; 2 )

`{`

    v8 = 8 * (rand() % -32);

    v4 = v8;

    v9 = &amp;v21[-v8];

    if ( v8 )

    `{`

        v10 = v8;

        do 

        `{` 

            *v9++ = rand(); 

            --v10; 

        `}` 

        while ( v10 ); 

    `}` 

`}` 

*(_BYTE *)(v7 + 0xBE0); 

sprintf(Dest, "HTTP/1.1 200 OKrnContent-Length: %urnConnection: %srnrn",(unsigned int)(v4 + 8));
```

只有前8个字节响应特定的格式，其他所有数据都是随机的。针对该内容的完整性由前7个字节之间的额外校验和执行，结果存储在第8个字节中。这个校验和过程类似于上面提到的。基于此，我们可以开发一个PoC，来远程检查服务器是否被这个版本的恶意软件入侵：

```
&gt; request_builder.py 192.168.48.133 8080 

datas : 

0000000000000000 E8 F6 E8 4E 72 61 03 EA C8 B3 DD 8D 25 D0 26 12 ...Nra♥.....%.&amp; 

0000000000000010 B7 F9 50 E5 8C D2 01 62 A0 37 2F FB AD C8 91 DA ..P...b.7/..... 

0000000000000020 44 A5 53 C7 1D 76 0E 4D AC AF F7 18 F4 12 57 A2 D.S.↔v♫M...↑.W. 

0000000000000030 A0 75 3B 0F 50 C5 6C 55 31 4B A1 9F D0 2E F4 F4 .u;☼P.lU1K...... 

0000000000000040 30 39 93 13 1A DF B8 A2 B4 7C DB 88 55 DE 26 98 09.→....|..U.&amp;. 

0000000000000050 98 04 29 6F AF 25 CF 9F FA F5 90 0D D8 23 E9 97 .♦)o.%.......#.. 

[*] checksum OK – Host is compromised
```

这个[PoC](http://www.exatrack.com/public/uroburos_poc.py)可以在我们的网站上找到。



## 2014年与2017年Uroburos的异同点

与2014年的恶意软件相比，有一些相同和相同的地方。以下这个列表并不完整，但是可以让你了解到这个恶意软件目前的状态。

<!-- [if !supportLists]-->l  <!--[endif]-->文件的名称和服务的名称保持不变，这使得任何IOC都可以很容易地检测到它。

<!-- [if !supportLists]-->l  <!--[endif]-->驱动程序总是加载VirtualBox漏洞利用方法。因此，在每次重新引导系统时都会进行内核漏洞利用。

<!-- [if !supportLists]-->l  <!--[endif]-->PatchGuard旁路已经被删除，这必然会限制对内核的修改。

```
Driver 2014: 

    if ( v2 ) 

        installService(v3);

    v4 = PG_bypass(); 

    if ( v4 )

        goto LABEL_16; 

    ObjectAttributes.Length = 48; 

    ObjectAttributes.RootDirectory = 0i64;
```

```
Driver 2017: 

    if ( v2 ) 

        installService(cp_DriverObject); 

    ObjectAttributes.RootDirectory = 0i64; 

    ObjectAttributes.SecurityDescriptor = 0i64;
```

<!-- [if !supportLists]-->l  <!--[endif]-->仍然使用DriverNull驱动程序，并且DeviceFWPMCALLOUT设备仍然会附加到该驱动程序之中。

```
&gt;&gt;&gt; drv_stack DriverNull 

- Stack of device name : DeviceFWPMCALLOUT 

Driver Object : fffffa80032753e0 

    Driver : DriverNull 

    Address: fffff88001890000 

    Driver : Null.SYS 

- Stack of device name : DeviceNull 

Driver Object : fffffa80032753e0 

    Driver : DriverNull 

    Address: fffff88001890000 

    Driver : Null.SYS
```

<!-- [if !supportLists]-->l  <!--[endif]-->字符串加密机制保持不变。在IopNotifyShutdownQueueHead中注册“Null”驱动程序本身就是一个非常有效的思路，但是我们还没有看到它的使用。这个回调函数的一个可能用途是在关机时写入注册表项，从而保证持久性。

<!-- [if !supportLists]-->l  <!--[endif]-->校验和机制得到改进，恶意软件使用了Threefish算法，消息的格式也在2014年版本上进行了调整。其目的可能是为了改变恶意软件的特征，以逃避检测。

总的来说，Rootkit仍然具备很大的威胁，但也有一些疏漏。例如，文件的名称和注册表项保持不变，这可能表明它将只在隔离的服务器上运行。尽管受欢迎的程度明显降低，但这个内核恶意软件仍然存在，并且似乎并没有准备退出舞台，因为它们的存在比位于用户空间组件中的恶意软件更加难以识别。



## YARA规则

```
rule Sig 

`{` 
    strings: 

        $strings_crypt = `{` 4d 8b c1 41 ba 40 00 00 00 41 ?? ?? ?? 41 ?? ?? 49 83 c0 01 49 83 ea 01 75 ??`}` 

        $hash_part1 = `{` 49 c1 c3 0e 4e ?? ?? ?? 4c 33 dd 4c 03 c7 4c 03 c1 48 c1 c0 10 49 33 c0 4d 03 c3 48 03 e8 48 c1 c8 0c 48 33 c5 49 c1 cb 07 4d 33 d8 4c 03 c0 49 03 eb 49 c1 c3 17 4c 33 dd 48 c1 c8 18 49 33 c0 4d 03 c3 48 03 e8 49 c1 cb 1b 4d 33 d8 4c 03 df 4c 03 d9 48 c1 c0 05 48 33 c5 4a ?? ?? ?? ??`}` 

    condition: 

        1 of them 
`}`
```

审核人：yiwang   编辑：边边
