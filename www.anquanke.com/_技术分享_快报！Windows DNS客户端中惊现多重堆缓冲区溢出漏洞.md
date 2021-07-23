> 原文链接: https://www.anquanke.com//post/id/86990 


# 【技术分享】快报！Windows DNS客户端中惊现多重堆缓冲区溢出漏洞


                                阅读量   
                                **100225**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：bishopfox.com
                                <br>原文地址：[https://www.bishopfox.com/blog/2017/10/a-bug-has-no-name-multiple-heap-buffer-overflows-in-the-windows-dns-client/](https://www.bishopfox.com/blog/2017/10/a-bug-has-no-name-multiple-heap-buffer-overflows-in-the-windows-dns-client/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01caf4e96300d7bd4e.jpg)](https://p4.ssl.qhimg.com/t01caf4e96300d7bd4e.jpg)

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**介绍**

****

微软已经在2017年10月份正式修复了漏洞**CVE-2017-11779**，该漏洞包含Windows DNS客户端中的多个内存崩溃漏洞，运行了Windows 8/Server 2012以及更新版本操作系统的计算机都将会受到该问题的影响，攻击者将能够通过恶意DNS响应来触发这些漏洞。在这个漏洞的帮助下，攻击者将能够在发送DNS请求的应用程序之中实现任意命令执行。

这也就意味着，如果攻击者能够控制你的DNS服务器（例如通过中间人攻击或恶意WiFi热点），那么他们就能够获得你系统的访问权。受该问题影响的不仅仅是你的Web浏览器，因为你的计算机系统会在后台不停地发送DNS查询请求，而攻击者只需要响应用户的查询请求就可以触发这些漏洞并实施攻击了。

研究人员在下面这个视频中对漏洞CVE-2017-11779进行了简单介绍，如果你想了解更多技术细节的话，请继续阅读本文。

视频：<br>





**漏洞概述**

****

在Windows 8/Windows Server 2012系统中，微软给Windows DNS客户端扩展了DNSSEC支持，相关代码存在于**DNSAPI.dll**文件中。其中一个引入用来支持DNSSEC的DNS资源记录（RRs）为NSEC3记录，该信息由**Nsec3_RecordRead**函数负责处理。

**CVE-2017-11779**所包含的漏洞均与**Nsec3_RecordRea**d函数有关，因为该函数无法安全地解析NSEC3 RRs，并进一步导致了多重写入越界问题。使用**DNSAPI.dll**文件的一般都是**DnsCache**服务，该服务的运行依赖于**svchost.exe**，并能够给Windows系统的DNS客户端提供DNS缓存服务。除此之外，还有很多其他需要发送DNS查询请求的应用程序也会引入该服务。

需要注意的是，由于这种记录是存在安全问题的，因此它理应是无法通过任何正常的DNS解析器的。正因如此，所以只有当目标用户直接从攻击者所控制的服务器中接受DNS响应的情况下，这些漏洞才有可能被触发。一般来说，**这里需要攻击者实现主动的中间人攻击**。

本文主要涉及到的是存在漏洞的DNS记录-NSEC3，NSEC3记录主要用来帮助DNS解析器识别记录名并验证DNSSEC有效性。

<br>

**漏洞介绍**

****

当你在看网页、听音乐或者什么都不做的时候，你的电脑都会发送DNS请求。除此之外，类似检测Windows系统更新的后台活动同样也会发送这种请求。绝大多数情况下，应用程序在发送这类请求时是不会直接查看到响应数据的，因为响应内容需要先到达DNS缓存服务并存储下来以便后续使用，这种特性可以帮助系统减少发送DNS请求的次数。

**DNS是一种明文协议，并且无法抵御中间人攻击**。正是由于这种特殊性质，所以微软才引入了DNSSEC（域名安全）扩展。这种扩展引入了多种新的DNS记录，并能够向DNS客户端以及服务器传递更多的信息。DNSSEC的目的是尝试解决某些现存的安全问题，但你可能已经猜到了，它的出现也带来了新的安全问题。

微软在Windows8和Server 2012及其之后的操作系统版本中为DNSSEC添加了客户端功能，随之一起的还有多种新的DNS记录。但是这种功能中有一条存在漏洞的DNS记录，即NSEC3。当Windows DNS客户端在处理包含NSEC3记录的DNS响应时，**它并不没有进行必要的数据过滤或清洗**。恶意的NSEC3记录将能够触发这种漏洞，并导致DNS客户端出现内存崩溃问题。如果攻击者技术足够好的话，他们甚至还可以在目标系统中实现任意代码执行。

由于这种记录本身的恶意性，因此它无法通过正常的DNS系统。服务器在接收到这种记录时将会直接丢弃，因为它并不符合NSEC3记录的标准规范。所以，如果攻击者想要利用该漏洞实施攻击的话，他们的位置必须在目标用户和DNS服务器之间（中间人攻击）。比如说，你现在在用咖啡店的WiFi上网，然后某人想要对你实施攻击，如果他们可以入侵你的路由器，那么他们就能够修改你所接收到的DNS响应了。

<br>

**受影响的系统以及如何修复该问题**

****

**从Windows 8/Windows Server 2012到Windows 10/Windows Server 2016的所有版本WIndows操作系统都会受到这些漏洞的影响，但Windows 8之前的操作系统不会受此影响。**

如果你的计算机操作系统版本是上述系统其中之一的话，我们建议用户**立刻安装微软在2017年10月份发布的安全更新补丁**。

<br>

**技术细节**

****

**DNSAPI.dll**中的这三个堆缓冲区溢出漏洞可以通过一台恶意DNS服务器或中间人攻击来触发，即发送恶意形式的NSEC3响应记录（RR）来对DNS请求予以响应。研究人员此次分析的是**DNSAPI.dll **v6.3.9600.18512 (x86, Windows 8.1)，该问题也已经在v10.0.14393.206 (x64, Windows 10)中得到了确认。

<br>

**缓冲区空间分配**

****

**Nsec3_RecordRead**函数负责通过调用**DNSAPI!DNS_AllocateRecordEx**来为NSEC3响应数据分配目的缓冲区（destbuf），destbuf的分配大小是由一个16位的受用户控制的数据长度域控制的，即一条DNS资源记录中的通用数据域。通过修改数据长度域，攻击者就能够控制destbuf的大小，然后进行越界读写攻击了。

下图为WireShark捕获到的一条NSEC3资源记录，其中用蓝色部分标记的就是数据长度域：

[![](https://p5.ssl.qhimg.com/t01adf5a7f43171c618.png)](https://p5.ssl.qhimg.com/t01adf5a7f43171c618.png)

DNSAPI可以从**Dns_ReadRecordStructureFromPacket**函数中获取到这个值，然后**Nsec3_RecordRead**函数将根据这个值来决定缓冲区空间的分配大小。

**堆缓冲区溢出漏洞 #1-NSEC3 Salt_Length**

第一个堆缓冲区溢出漏洞位于**DNSAPI!Nsec3_RecordRead+0xB9**，这里它会将用户提供的8位Salt Length值当作**memcpy**的拷贝大小。在我们分析的NSEC3资源记录样本中，NSEC3 Salt Length值的位置如下图所示：

[![](https://p1.ssl.qhimg.com/t01f404ffe65af5b38e.png)](https://p1.ssl.qhimg.com/t01f404ffe65af5b38e.png)

如果攻击者能够控制NSEC3 Salt Length的大小，并让其超过destbuf的大小，那么攻击者就能够利用这个堆缓冲区溢出漏洞来实现越界写入操作了。

接下来，Nsec3_RecordRead函数将会使用空直接提供的NSEC3 Salt Length数据来作为memcpy的size参数，具体如下列代码所示：



```
.text:742574D4         mov     bh, [esi+4]    ; User-controlled NSEC3 Salt Length size
.text:742574D7         add     esi, 5               ; Start of NSEC3 Salt data in RR
.text:742574DA         mov     eax, [ebp+var_4]
.text:742574DD         mov     [edi+1Ch], bh      
.text:742574E0         add     eax, 20h
.text:742574E3         movzx   edi, bh
.text:742574E6         push    edi          ; Size (user-controlled)
.text:742574E7         push    esi           ; Src (NSEC3 RR data)
.text:742574E8         push    eax          ; Dst (size of buf is user-controlled)
.text:742574E9         call    memcpy            ; Nsec3_RecordRead+0xB9
```

其中的memcpy操作会将攻击者提供的DNS资源记录（0xff字节）拷贝到destbuf之中。

**堆缓冲区溢出漏洞 #2-NSEC3 Hash Length**

第二个堆缓冲区溢出漏洞存在于**Nsec3_RecordRead+0xD9**，具体如下列代码所示：



```
.text:742574EE         mov     eax, [ebp+var_4]
.text:742574F1         add     esi, edi
.text:742574F3         mov     bl, [esi]              ; User-controlled NSEC3 Hash Length size
.text:742574F5         inc     esi
.text:742574F6         mov     [ebp+Src], esi  ; Start of NSEC3 Hash data in RR
.text:742574F9         mov     [eax+1Dh], bl
.text:742574FC         add     eax, 20h
.text:742574FF         movzx   esi, bl
.text:74257502         add     eax, edi
.text:74257504         push    esi             ; Size (user-controlled)
.text:74257505         push    [ebp+Src]       a      ; Src  (data in NSEC3 RR)
.text:74257508         push    eax             ; Dst  (size of buf is user-controlled)
.text:74257509         call    memcpy          ; Nsec3RecordRead+0xD9
```

在第一个堆缓冲区溢出漏洞那里，memcpy会将用户提供的值作为size参数值。而在第二个堆溢出漏洞中，目的缓冲区的大小跟例子一中由用户控制的缓冲区（destbuf）大小是一样的。在我们分析的NSEC3资源记录样本中，NSEC3 Hash Length域所处的位置如下图所示：

[![](https://p0.ssl.qhimg.com/t017a0aead53bd396a8.png)](https://p0.ssl.qhimg.com/t017a0aead53bd396a8.png)

**堆缓冲区溢出漏洞 #3-Integer Underflow**

最后一个，也是最有用的一个堆缓冲区溢出漏洞并不会直接使用用户提供的length域，它会先进行一些计算（减法计算）。该漏洞位于**Nsec3_RecordRead+0x106**，具体如下列代码所示：



```
.text:7425750E         mov     ecx, [ebp+var_C] ; User-supplied NSEC3 RR size
.text:74257511         movzx   eax, bl                      ; NSEC3 Hash length (from ex #2)
.text:74257514         sub     cx, ax                         ; Potential underflow #1
.text:74257517         movzx   eax, bh                     ; NSEC3 Salt length (from ex #1)
.text:7425751A         mov     ebx, [ebp+var_4]
.text:7425751D         sub     cx, ax                        ; Potential underflow #2
.text:74257520         movzx   eax, cx
.text:74257523         push    eax                   ; Size (user-controlled, wrapped)
.text:74257524         mov     eax, [ebp+Src]
.text:74257527         add     eax, esi
.text:74257529         mov     [ebx+1Eh], cx
.text:7425752D         push    eax                            ; Src (NSEC3 RR data)
.text:7425752E         lea     eax, [edi+20h]
.text:74257531         add     eax, esi
.text:74257533         add     eax, ebx
.text:74257535         push    eax                   ; Dst (size of buf is user-controlled)
.text:74257536         call    memcpy                      ; Nsec3_RecordRead+0x106
```

我们用下列伪代码来演示计算的执行过程:



```
saved_record_len = DNS_RR_Size – 6 // performed outside this basic block
nsec3_nho_len = saved_record_len - nsec3_hash_len - nsec3_salt_len
```

接下来，我们可以使用下列值来创建一个PoC，并尝试实现越界读写操作：



```
saved_record_len of 0x00f9 (a.k.a DNS_RR_Size of 0xff – 0x6)
nsec3_hash_len of 0xf8
nsec3_salt_len of 0x6
```



**异常例子**

****

在下面给出的例子中，攻击者控制的数据将会用于资源寄存器及目的寄存器**eax**和**edx**之中：



```
eax=30303030 
ebx=0000251e 
ecx=00000000 
edx=02f839e8 
esi=00000001 
edi=000001de
eip=7433d37f 
esp=0394fb8c 
ebp=0394fb94 
iopl=0&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp; nv up ei pl nz na pe nc
cs=001b&amp;nbsp; ss=0023&amp;nbsp; ds=0023&amp;nbsp; es=0023&amp;nbsp; fs=003b&amp;nbsp; gs=0000&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp; efl=00010206 
dnsapi!coalesceRemoveFromGroup+0x58:
7433d37f 895004&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp; mov&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp; dword ptr [eax+4],edx ds:0023:30303034=????????
0:008&gt; dd edx
02f839e8&amp;nbsp; 30303030 30303030 02f839f0 02f839f0
02f839f8&amp;nbsp; 30303030 30303030 30303030 30303030
02f83a08&amp;nbsp; 30303030 00000001 00000001 30303030
02f83a18&amp;nbsp; 30303030 30303030 30303030 30303030
02f83a28&amp;nbsp; 30303030 30303030 30303030 30303030
02f83a38&amp;nbsp; 30303030 30303030 30303030 30303030
02f83a48&amp;nbsp; 30303030 30303030 30303030 30303030
02f83a58&amp;nbsp; 30303030 30303030 30303030 30303030
0:008&gt; kv
ChildEBP RetAddr&amp;nbsp; Args to Child&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;
0394fb94 7433d300 02f83490 7432ef50 0000251e dnsapi!coalesceRemoveFromGroup+0x58 (FPO: [Non-Fpo])
0394fbbc 7432e635 743894ac 02fa2578 0000251e dnsapi!Coalesce_Complete+0x17e (FPO: [Non-Fpo])
0394fc24 7434021b 02f495f0 00000000 02f495f0 dnsapi!Send_AndRecvComplete+0x26b (FPO: [Non-Fpo])
0394fc48 743404d4 02f495f0 00000000 02f7a1f8 dnsapi!Send_AndRecvTcpComplete+0xef (FPO: [Non-Fpo])
0394fc68 74340105 7432dbf0 02f49cf0 02f78dd0 dnsapi!Recv_TcpCallbackCompletion+0xe9 (FPO: [Non-Fpo])
0394fc7c 74e688da 0394fd64 02f495f0 02f7a2cc dnsapi!Recv_IoCompletionCallback+0x109 (FPO: [Non-Fpo])
…omitted for brevity…
```

为了触发这种异常，第一个响应会设置‘truncated’ DNS比特，并强迫客户端通过TCP执行第二次DNS查询，此时攻击者就可以向目标主机发送更多的Payload了。如果能够对目标系统中的堆内存进行小心操作的话，攻击者甚至还可以向内存中写入包含函数指针的对象，并在目标系统中执行任意代码。

<br>

**总结**

****

对于攻击者而言，这三个漏洞的优势就在于：漏洞可以在不需要任何用户交互的情况下被触发；它们可以影响不同权限级别（包括SYSTEM）的运行进程；svchost.exe下的DnsCache服务将无法正常重启。这也就意味着，攻击者可以先终止DnsCache服务的运行，然后可以确切地了解到堆内存空间的状态，接下来再多次利用这些漏洞来绕过ASLR，最终向目标主机发送攻击Payload。
