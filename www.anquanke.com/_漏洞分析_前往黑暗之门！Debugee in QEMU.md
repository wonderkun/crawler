> 原文链接: https://www.anquanke.com//post/id/86636 


# 【漏洞分析】前往黑暗之门！Debugee in QEMU


                                阅读量   
                                **189926**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p5.ssl.qhimg.com/t01e45b1ccfb08b8d92.jpg)](https://p5.ssl.qhimg.com/t01e45b1ccfb08b8d92.jpg)**



作者：[k0shl](http://bobao.360.cn/member/contribute?uid=1353169030)

预估稿费：600RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

** **

**0x00 前言**

好久没给安全客投稿了，最近刚刚接触漏洞挖掘，一直在读一些经典的fuzzer源码，同时也开始接触虚拟化逃逸这块的内容，在这个时候正巧碰到了两个非常经典的漏洞利用，相信很多小伙伴也已经看过了，phrack前段时间刚刚更新了关于这个漏洞的详细利用过程。

我后来对这个漏洞进行了动态调试，并且通过phrack的paper恶补了一些关于虚拟机的工作原理，Guest OS和Host OS之间的一些知识。

[![](https://p2.ssl.qhimg.com/t01df23cda2c7badcba.png)](https://p2.ssl.qhimg.com/t01df23cda2c7badcba.png)

在调试的过程中，我愈发觉得这两个漏洞作为前往黑暗之门入门再合适不过，通过对两个漏洞的分析和利用的调试，可以熟悉这类虚拟化漏洞的调试原理。今天，我将和大家分享QEMU虚拟化逃逸的调试环境搭建，关于CVE-2015-5165和CVE-2015-7504漏洞动态调试分析，以及补丁对比。

在此之前，我默认阅读此文的小伙伴们已经看过了phrack.org关于VM Escape Case Study的文章，并且已经了解虚拟机工作的基本原理，包括但不限于内存管理机制，REALTEK网卡、PCNET网卡的数据包结构，Tx、Rx缓冲区等等。关于phrack.org的文章以及看雪翻译版分析文章的链接我将在文末给出。下面我们一起出发前往黑暗之门吧！

[![](https://p5.ssl.qhimg.com/t011062251e2ae4005e.png)](https://p5.ssl.qhimg.com/t011062251e2ae4005e.png)



**0x01 QEMU环境搭建**

在调试QEMU虚拟化逃逸漏洞之前，我们需要搭建虚拟化逃逸的环境，首先通过git clone下载QEMU，并且通过git check设定分支（如果要调试以前版本的话）。



```
$ git clone git://git.qemu-project.org/qemu.git
$ cd qemu
$ mkdir -p bin/debug/native
$ cd bin/debug/native
$ ../../../configure --target-list=x86_64-softmmu --enable-debug --disable-werror
$ make
```

在make的时候，Host OS会需要一些库的安装，可以通过apt-get来下载安装，比如zlib，glib-2.22等（其中glib-2.22也需要一些依赖，同时需要去网站下载，网站地址：[http://ftp.gnome.org/pub/gnome/sources/glib/2.22/](http://ftp.gnome.org/pub/gnome/sources/glib/2.22/) ）。

安装完毕后，会在/path/to/qemu/bin/debug/native/下生成一个x86_64-softmmu目录，在此之前，需要安装一个qcow2的系统文件，所以需要通过qemu-img来生成一个qcow2系统文件。

```
$ qemu-img create -f qcow2 ubuntu.qcow2 20G
```

之后首先通过qemu-system-x86_64完成对qcow2系统文件中系统的安装，需要用-cdrom对iso镜像文件进行加载。同时，需要安装vncviewer，这样可以通过vncviewer对qemu启动的vnc端口进行连接。



```
$ qemu-system-x86_64 -enable-kvm -m 2048 -hda /path/to/ubuntu.qcow2 -cdrom /path/to/ubuntu.iso
$ apt-get install xvnc4viewer
```

通过vnc连接qemu之后，根据镜像文件提示进行安装，这里推荐还是用server.iso，因为安装比较快，用desktop的话可能会稍微卡顿一些，安装完成后就获得了一个有系统的qcow2文件，之后就可以用包含漏洞的rlt8139和pcnet网卡硬件启动了。

```
$ ./qemu-system-x86_64 -enable-kvm -m 2048 -display vnc=:89 -netdev user,id=t0, -device rtl8139,netdev=t0,id=nic0 -netdev user,id=t1, -device pcnet,netdev=t1,id=nic1 -drive  file=/path/to/ubuntu.qcow2,format=qcow2,if=ide,cache=writeback
```

启动之后，这里我为了省事，直接用NAT的方法共享宿主机网络，然后在本地通过SimpleHTTPServer建立一个简单的HTTP Server，通过wget方法获得两个漏洞的PoC，这两个漏洞PoC可以通过gcc -static的方法在本地编译后直接上传，然后运行即可。

之后在宿主机通过ps -ef|grep qemu找到qemu的启动进程，通过gdb attach pid的方法附加，按c继续运行就可以了，可以通过b function的方法下断点，方便跟踪调试。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0157b37844ab48f026.jpg)



**0x02 CVE-2015-5165漏洞分析**

CVE-2015-5165是一个内存泄露漏洞，由于对于ip-&gt;ip_len和hlen长度大小没有进行控制，导致两者相减计算为负时，由于ip_data_len变量定义是unsigned类型，导致这个值会非常大，从而产生内存泄露。漏洞文件在/path/to/qemu/hw/net/rtl8139.c。

首先根据漏洞描述，漏洞发生在rtl8139_cplus_transmit_one函数中，通过b rtl8139_cplus_transmit_one的方法在该函数下断点，之后运行PoC，命中函数后，首先函数会传入一个RTL8139State结构体变量。继续单步跟踪，会执行到一处if语句，这里会比较当前数据包头部是否是IPV4的头部。



```
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0x4 
[-------------------------------------code-------------------------------------]
   0x55b25db58480 &lt;rtl8139_cplus_transmit_one+1854&gt;:shr    al,0x4
   0x55b25db58483 &lt;rtl8139_cplus_transmit_one+1857&gt;:movzx  eax,al
   0x55b25db58486 &lt;rtl8139_cplus_transmit_one+1860&gt;:and    eax,0xf
=&gt; 0x55b25db58489 &lt;rtl8139_cplus_transmit_one+1863&gt;:cmp    eax,0x4
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db584892173                if (IP_HEADER_VERSION(ip) != IP_HEADER_VERSION_4) `{`
```

可见此时确实是IPv4的结构，随后进入if语句的代码逻辑，在其中会调用be16_to_cpu对ip-&gt;ip_len进行转换，ip-&gt;ip_len的长度为0x1300，转换后长度为0x13。



```
[----------------------------------registers-----------------------------------]
RAX: 0x1300 
RDI: 0x1300 //ip-&gt;ip_len
EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x55b25db584f7 &lt;rtl8139_cplus_transmit_one+1973&gt;:
    movzx  eax,WORD PTR [rax+0x2]
   0x55b25db584fb &lt;rtl8139_cplus_transmit_one+1977&gt;:movzx  eax,ax
   0x55b25db584fe &lt;rtl8139_cplus_transmit_one+1980&gt;:mov    edi,eax
=&gt; 0x55b25db58500 &lt;rtl8139_cplus_transmit_one+1982&gt;:
    call   0x55b25db54a37 &lt;be16_to_cpu&gt;
   0x55b25db58505 &lt;rtl8139_cplus_transmit_one+1987&gt;:mov    edx,eax
Guessed arguments:
arg[0]: 0x1300 //ip-&gt;ip_len=0x1300
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db585002181                    ip_data_len = be16_to_cpu(ip-&gt;ip_len) - hlen;
      
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
RAX: 0x13 //经过be16_to_cpu()之后返回值为0x13
[-------------------------------------code-------------------------------------]
   0x55b25db584fb &lt;rtl8139_cplus_transmit_one+1977&gt;:movzx  eax,ax
   0x55b25db584fe &lt;rtl8139_cplus_transmit_one+1980&gt;:mov    edi,eax
   0x55b25db58500 &lt;rtl8139_cplus_transmit_one+1982&gt;:
    call   0x55b25db54a37 &lt;be16_to_cpu&gt;
=&gt; 0x55b25db58505 &lt;rtl8139_cplus_transmit_one+1987&gt;:mov    edx,eax
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db585052181                    ip_data_len = be16_to_cpu(ip-&gt;ip_len) - hlen;
```

转换后，会将转换后的值和hlen相减。



```
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0x14 //hlen=0x14
RDX: 0x13 //be16_to_cpu(ip-&gt;ip_len)=0x13
[-------------------------------------code-------------------------------------]
   0x55b25db58500 &lt;rtl8139_cplus_transmit_one+1982&gt;:
    call   0x55b25db54a37 &lt;be16_to_cpu&gt;
   0x55b25db58505 &lt;rtl8139_cplus_transmit_one+1987&gt;:mov    edx,eax
   0x55b25db58507 &lt;rtl8139_cplus_transmit_one+1989&gt;:
    mov    eax,DWORD PTR [rbp-0x13c]
=&gt; 0x55b25db5850d &lt;rtl8139_cplus_transmit_one+1995&gt;:sub    edx,eax
   0x55b25db5850f &lt;rtl8139_cplus_transmit_one+1997&gt;:mov    eax,edx
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db5850d2181                    ip_data_len = be16_to_cpu(ip-&gt;ip_len) - hlen;
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RDX: 0xffffffff //相减之后为0xffffffff，这个变量是一个unsigned类型，此值极大
[-------------------------------------code-------------------------------------]
   0x55b25db5850d &lt;rtl8139_cplus_transmit_one+1995&gt;:sub    edx,eax
=&gt; 0x55b25db5850f &lt;rtl8139_cplus_transmit_one+1997&gt;:mov    eax,edx
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db5850f2181                    ip_data_len = be16_to_cpu(ip-&gt;ip_len) - hlen;
```

相减后，这个值为0xffffffff，而这个值是一个16位无符号数，也就是是一个极大值0xffff，我们可以通过源码看到关于这个变量的定义。



```
uint16_t ip_data_len = 0;
……
ip_data_len = be16_to_cpu(ip-&gt;ip_len) - hlen;
```

接下来继续单步跟踪，会发现ip_data_len这个极大值会被用来计算tcp_data_len，也就是tcp数据的长度，随后还有一个tcp_chunk_size，这个chunk_size限制了一个数据包的最大值，当tcp数据的长度超过chunk_size的时候，则会分批发送。



```
//计算tcp_data_len
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0xffff //ip_data_len
[-------------------------------------code-------------------------------------]
=&gt; 0x55b25db586c2 &lt;rtl8139_cplus_transmit_one+2432&gt;:
    sub    eax,DWORD PTR [rbp-0x10c]//hlen的大小是0x14
   0x55b25db586c8 &lt;rtl8139_cplus_transmit_one+2438&gt;:
    mov    DWORD PTR [rbp-0x108],eax
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db586c22231                    int tcp_data_len = ip_data_len - tcp_hlen;
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0xffeb //相减后tcp_data_len长度是0xffeb
[-------------------------------------code-------------------------------------]
   0x55b25db586c2 &lt;rtl8139_cplus_transmit_one+2432&gt;:
    sub    eax,DWORD PTR [rbp-0x10c]
=&gt; 0x55b25db586c8 &lt;rtl8139_cplus_transmit_one+2438&gt;:
    mov    DWORD PTR [rbp-0x108],eax
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db586c82231                    int tcp_data_len = ip_data_len - tcp_hlen;
//计算chunk_size = 0x5b4      
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
RAX: 0x5b4 
[-------------------------------------code-------------------------------------]
   0x55b25db586ce &lt;rtl8139_cplus_transmit_one+2444&gt;:mov    eax,0x5dc
   0x55b25db586d3 &lt;rtl8139_cplus_transmit_one+2449&gt;:
    sub    eax,DWORD PTR [rbp-0x13c]//ETH_MTU-hlen
   0x55b25db586d9 &lt;rtl8139_cplus_transmit_one+2455&gt;:
    sub    eax,DWORD PTR [rbp-0x10c]//-tcp_hlen
=&gt; 0x55b25db586df &lt;rtl8139_cplus_transmit_one+2461&gt;:
    mov    DWORD PTR [rbp-0x104],eax
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db586df2232                    int tcp_chunk_size = ETH_MTU - hlen - tcp_hlen;
```

随后rtl8139_cplus_transmit_one函数会进入一个for循环处理，这个for循环会计算每一个chunk_size是达到整个tcp_data_len的末尾，如果没有则处理整个chunk_size并发送。



```
int tcp_data_len = ip_data_len - tcp_hlen;//tcp_data_len = 0xffff-0x14=0xffeb
int tcp_chunk_size = ETH_MTU - hlen - tcp_hlen;//chunk_size = 0x5b4
for (tcp_send_offset = 0; tcp_send_offset &lt; tcp_data_len; tcp_send_offset += tcp_chunk_size)//0xffeb/0x5b4 = 43
`{`
                        uint16_t chunk_size = tcp_chunk_size;//0x5b4
                        /* check if this is the last frame */
                        if (tcp_send_offset + tcp_chunk_size &gt;= tcp_data_len)//if packet length &gt; tcp data length
                        `{`
                            is_last_frame = 1;
                            chunk_size = tcp_data_len - tcp_send_offset;
                        `}`
                        DPRINTF("+++ C+ mode TSO TCP seqno %08xn",
                            be32_to_cpu(p_tcp_hdr-&gt;th_seq));
                        /* add 4 TCP pseudoheader fields */
                        /* copy IP source and destination fields */
                        memcpy(data_to_checksum, saved_ip_header + 12, 8);
                        DPRINTF("+++ C+ mode TSO calculating TCP checksum for "
                            "packet with %d bytes datan", tcp_hlen +
                            chunk_size);
                        if (tcp_send_offset)
                        `{`
                            memcpy((uint8_t*)p_tcp_hdr + tcp_hlen, (uint8_t*)p_tcp_hdr + tcp_hlen + tcp_send_offset, chunk_size);//disclouse key!!!p_tcp_hdr = ip_header   p_tcp_hdr+tcp_hlen = data section
                            //
                        `}`
                        /* keep PUSH and FIN flags only for the last frame */
                        if (!is_last_frame)
                        `{`
                            TCP_HEADER_CLEAR_FLAGS(p_tcp_hdr, TCP_FLAG_PUSH|TCP_FLAG_FIN);
                        `}`
                        /* recalculate TCP checksum */
                        ip_pseudo_header *p_tcpip_hdr = (ip_pseudo_header *)data_to_checksum;
                        p_tcpip_hdr-&gt;zeros      = 0;
                        p_tcpip_hdr-&gt;ip_proto   = IP_PROTO_TCP;
                        p_tcpip_hdr-&gt;ip_payload = cpu_to_be16(tcp_hlen + chunk_size);
                        p_tcp_hdr-&gt;th_sum = 0;
                        int tcp_checksum = ip_checksum(data_to_checksum, tcp_hlen + chunk_size + 12);
                        DPRINTF("+++ C+ mode TSO TCP checksum %04xn",
                            tcp_checksum);
                        p_tcp_hdr-&gt;th_sum = tcp_checksum;
                        /* restore IP header */
                        memcpy(eth_payload_data, saved_ip_header, hlen);
                        /* set IP data length and recalculate IP checksum */
                        ip-&gt;ip_len = cpu_to_be16(hlen + tcp_hlen + chunk_size);
                        /* increment IP id for subsequent frames */
                        ip-&gt;ip_id = cpu_to_be16(tcp_send_offset/tcp_chunk_size + be16_to_cpu(ip-&gt;ip_id));
                        ip-&gt;ip_sum = 0;
                        ip-&gt;ip_sum = ip_checksum(eth_payload_data, hlen);
                        DPRINTF("+++ C+ mode TSO IP header len=%d "
                            "checksum=%04xn", hlen, ip-&gt;ip_sum);
                        int tso_send_size = ETH_HLEN + hlen + tcp_hlen + chunk_size;
                        DPRINTF("+++ C+ mode TSO transferring packet size "
                            "%dn", tso_send_size);
                        rtl8139_transfer_frame(s, saved_buffer, tso_send_size,
                            0, (uint8_t *) dot1q_buffer);
                        /* add transferred count to TCP sequence number */
                        p_tcp_hdr-&gt;th_seq = cpu_to_be32(chunk_size + be32_to_cpu(p_tcp_hdr-&gt;th_seq));
                        ++send_count;
                    `}`
```

在for循环中，会有一处if语句判断tcp_send_offset是否为0，当tcp_send_offset不为0时，会执行memcpy操作，拷贝目标缓冲区进入待发送的tcp_buffer中，这个memcpy拷贝的就是buffer，而每轮都会拷贝一个chunk_size，之后再加一个chunk_size，这样就会超过原本buffer的大小，而考到缓冲区外的空间，造成内存泄露。首先来看memcpy第一回合。



```
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RDX: 0x5b4 //size
RSI: 0x7f49f003adfa --&gt; 0x9000000000000000//src 
RDI: 0x7f49f003a846 --&gt; 0x0 //dst
[-------------------------------------code-------------------------------------]
   0x55b25db5880e &lt;rtl8139_cplus_transmit_one+2764&gt;:add    rcx,rdx
   0x55b25db58811 &lt;rtl8139_cplus_transmit_one+2767&gt;:mov    rdx,rax
   0x55b25db58814 &lt;rtl8139_cplus_transmit_one+2770&gt;:mov    rdi,rcx
=&gt; 0x55b25db58817 &lt;rtl8139_cplus_transmit_one+2773&gt;:call   0x55b25d9361a8//memcpy
Guessed arguments:
arg[0]: 0x7f49f003a846 --&gt; 0x0 
arg[1]: 0x7f49f003adfa --&gt; 0x9000000000000000 
arg[2]: 0x5b4 
arg[3]: 0x7f49f003a846 --&gt; 0x0 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Thread 3 "qemu-system-x86" hit Breakpoint 4, 0x000055b25db58817 in rtl8139_cplus_transmit_one (s=0x55b26083d430)
    at /home/sh1/Desktop/qemu/hw/net/rtl8139.c:2267
2267                            memcpy((uint8_t*)p_tcp_hdr + tcp_hlen, (uint8_t*)p_tcp_hdr + tcp_hlen + tcp_send_offset, chunk_size);
gdb-peda$ x/50x 0x7f49f003adfa//src
0x7f49f003adfa:0x90000000000000000x100000007f49e7c7
0x7f49f003ae0a:0xc0000000000000000x100000007f49e456
0x7f49f003ae1a:0x80000000000000000x100000007f49ef8b
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
RAX: 0x7f49f003a846 --&gt; 0x9000000000000000 
[-------------------------------------code-------------------------------------]
   0x55b25db58811 &lt;rtl8139_cplus_transmit_one+2767&gt;:mov    rdx,rax
   0x55b25db58814 &lt;rtl8139_cplus_transmit_one+2770&gt;:mov    rdi,rcx
   0x55b25db58817 &lt;rtl8139_cplus_transmit_one+2773&gt;:call   0x55b25d9361a8
=&gt; 0x55b25db5881c &lt;rtl8139_cplus_transmit_one+2778&gt;:
    cmp    DWORD PTR [rbp-0x130],0x0
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
2271                        if (!is_last_frame)
gdb-peda$ x/50x 0x7f49f003a846//target dst
0x7f49f003a846:0x90000000000000000x100000007f49e7c7
0x7f49f003a856:0xc0000000000000000x100000007f49e456
0x7f49f003a866:0x80000000000000000x100000007f49ef8b
//memcpy(0x7f49f003a846,0x7f49f003adfa,lenth)
```

这里注意一下目前我们拷贝的缓冲区起始地址是：0x7f49f003adfa，拷贝到目标缓冲区后，单步跟踪，会发现for循环中会调用rtl8139_tansfer_frame函数将saved_buffer送回缓冲区。而saved_buffer的内容就包含了我们拷贝的内容。



```
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0x55b26083d430 --&gt; 0x55b25f178400 --&gt; 0x55b25f15eda0 --&gt; 0x55b25f15ef20 --&gt; 0x393331386c7472 ('rtl8139')
RBX: 0x1 
RCX: 0x0 
RDX: 0x5ea 
RSI: 0x7f49f003a810 --&gt; 0x5452563412005452 
RDI: 0x55b26083d430 --&gt; 0x55b25f178400 --&gt; 0x55b25f15eda0 --&gt; 0x55b25f15ef20 --&gt; 0x393331386c7472 ('rtl8139')
[-------------------------------------code-------------------------------------]
   0x55b25db58a3a &lt;rtl8139_cplus_transmit_one+3320&gt;:mov    r8,rcx
   0x55b25db58a3d &lt;rtl8139_cplus_transmit_one+3323&gt;:mov    ecx,0x0
   0x55b25db58a42 &lt;rtl8139_cplus_transmit_one+3328&gt;:mov    rdi,rax
=&gt; 0x55b25db58a45 &lt;rtl8139_cplus_transmit_one+3331&gt;:
    call   0x55b25db5776d &lt;rtl8139_transfer_frame&gt;
Guessed arguments:
arg[0]: 0x55b26083d430 --&gt; 0x55b25f178400 --&gt; 0x55b25f15eda0 --&gt; 0x55b25f15ef20 --&gt; 0x393331386c7472 ('rtl8139')
arg[1]: 0x7f49f003a810 --&gt; 0x5452563412005452 
arg[2]: 0x5ea 
arg[3]: 0x0 
arg[4]: 0x0 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db58a452307                        rtl8139_transfer_frame(s, saved_buffer, tso_send_size,
gdb-peda$ x/50x  0x7f49f003a810//save_buffer
0x7f49f003a810:0x54525634120054520x0045000856341200
0x7f49f003a820:0x06400040aededc050xa8c0010108c0b9d3
0x7f49f003a830:0xfecaefbeadde02010x1050bebafeca72c0
0x7f49f003a840:0x00000000f015adde0xe7c7900000000000
0x7f49f003a850:0x0000100000007f490xe456c00000000000
0x7f49f003a860:0x0000100000007f490xef8b800000000000
0x7f49f003a870:0x0000100000007f490xe43ce00000000000
0x7f49f003a880:0x0000100000007f490xe369c00000000000
```

随后我们第二轮再次命中memcpy函数，注意一下源缓冲区的值。



```
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0x5b4 
RBX: 0x5b4 
RCX: 0x7f49f003a846 --&gt; 0x9000000000000000 
RDX: 0x5b4 
RSI: 0x7f49f003b3ae --&gt; 0x7f49cc0de0000000 
RDI: 0x7f49f003a846 --&gt; 0x9000000000000000 
EFLAGS: 0x202 (carry parity adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x55b25db5880e &lt;rtl8139_cplus_transmit_one+2764&gt;:add    rcx,rdx
   0x55b25db58811 &lt;rtl8139_cplus_transmit_one+2767&gt;:mov    rdx,rax
   0x55b25db58814 &lt;rtl8139_cplus_transmit_one+2770&gt;:mov    rdi,rcx
=&gt; 0x55b25db58817 &lt;rtl8139_cplus_transmit_one+2773&gt;:call   0x55b25d9361a8//memcpy
Guessed arguments:
arg[0]: 0x7f49f003a846 --&gt; 0x9000000000000000 
arg[1]: 0x7f49f003b3ae --&gt; 0x7f49cc0de0000000 
arg[2]: 0x5b4 
arg[3]: 0x7f49f003a846 --&gt; 0x9000000000000000 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Thread 3 "qemu-system-x86" hit Breakpoint 4, 0x000055b25db58817 in rtl8139_cplus_transmit_one (s=0x55b26083d430)
    at /home/sh1/Desktop/qemu/hw/net/rtl8139.c:2267
2267                            memcpy((uint8_t*)p_tcp_hdr + tcp_hlen, (uint8_t*)p_tcp_hdr + tcp_hlen + tcp_send_offset, chunk_size);
```

这一次是 0x7f49f003b3ae – 0x7f49f003adfa = 0x5b4 确实是一个chunk的大小，如此一来，每一轮memcpy都会加上一个chunk_size，当超出了buffer，就造成了信息泄露，可以拷贝当前buffer之外的内容。而我们只需要从Rx Buffer中读取，这样就会造成信息泄露了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0181b5e651ad3b09f7.png)



**0x03 CVE-2015-7504漏洞分析**

CVE-2015-7504是一个堆溢出漏洞，这个漏洞形成的原因涉及到一个PCNetState_st结构体，这个结构体中有一个buffer变量长度大小定义为4096，然而在PCNET网卡的pcnet_receive函数中处理buffer时会在结尾增加一个4字节的CRC校验，这时当我们对传入buffer长度控制为4096的话，4字节的CRC校验会覆盖超出4096长度的4字节位置，而这4字节正好是PCNetState_st结构体中的一个irq关键结构，进一步我们可以利用irq结构控制rip，漏洞文件在/path/to/qemu/hw/net/pcnet.c。

接下来我们在pcnet_receive函数入口下断点，函数入口处会传入PCNetState_st结构体对象，这里我筛选部分跟此漏洞有关的结构体变量。



```
gdb-peda$ p *(struct PCNetState_st*)0x55b25f34a1a0
$1 = `{`
  ……
  buffer = "RT002264VRT002264Vb", '00', 
  irq = 0x55b2603bc910, 
  ……
  looptest = 0x1
`}`
```

随后单步跟踪，这里首先会获取s-&gt;buffer的值。



```
//store s-&gt;buffer to src
[----------------------------------registers-----------------------------------]
RAX: 0x55b25f34a1a0 --&gt; 0x55b2603bca00 --&gt; 0x55b2603bca20 --&gt; 0x55b25e13d940 --&gt; 0x1 
[-------------------------------------code-------------------------------------]
   0x55b25db4e537 &lt;pcnet_receive+952&gt;:mov    WORD PTR [rax+0x212c],dx
   0x55b25db4e53e &lt;pcnet_receive+959&gt;:
    jmp    0x55b25db4effb &lt;pcnet_receive+3708&gt;
   0x55b25db4e543 &lt;pcnet_receive+964&gt;:mov    rax,QWORD PTR [rbp-0xa8]
=&gt; 0x55b25db4e54a &lt;pcnet_receive+971&gt;:add    rax,0x2290//offset
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db4e54a1062            uint8_t *src = s-&gt;buffer;
```

随后会到达一处if语句判断，这里会判断looptest的值，当此值为非0值时，会进入else语句处理。



```
//looptest
[----------------------------------registers-----------------------------------]
RAX: 0x1 //s-&gt;looptest
[-------------------------------------code-------------------------------------]
   0x55b25db4e587 &lt;pcnet_receive+1032&gt;:mov    DWORD PTR [rbp-0xd8],0x0
   0x55b25db4e591 &lt;pcnet_receive+1042&gt;:mov    rax,QWORD PTR [rbp-0xa8]
   0x55b25db4e598 &lt;pcnet_receive+1049&gt;:mov    eax,DWORD PTR [rax+0x32b4]
=&gt; 0x55b25db4e59e &lt;pcnet_receive+1055&gt;:test   eax,eax
   0x55b25db4e5a0 &lt;pcnet_receive+1057&gt;:
    jne    0x55b25db4e635 &lt;pcnet_receive+1206&gt;
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db4e59e1067            if (!s-&gt;looptest) `{`
//s-&gt;looptest = PCNET_LOOPTEST_CRC
[----------------------------------registers-----------------------------------]
RAX: 0x1 [-------------------------------------code-------------------------------------]
=&gt; 0x55b25db4e645 &lt;pcnet_receive+1222&gt;:
    je     0x55b25db4e66c &lt;pcnet_receive+1261&gt;
   0x55b25db4e647 &lt;pcnet_receive+1224&gt;:mov    rax,QWORD PTR [rbp-0xa8]
   0x55b25db4e64e &lt;pcnet_receive+1231&gt;:movzx  eax,WORD PTR [rax+0x206a]
   0x55b25db4e655 &lt;pcnet_receive+1238&gt;:movzx  eax,ax
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db4e6451075            `}` else if (s-&gt;looptest == PCNET_LOOPTEST_CRC ||
```

随后会进入else语句处理，在else语句处理中会有一处while循环进行CRC校验。



```
else if (s-&gt;looptest == PCNET_LOOPTEST_CRC ||
                       !CSR_DXMTFCS(s) || size &lt; MIN_BUF_SIZE+4) `{`
                uint32_t fcs = ~0;
                uint8_t *p = src;
                while (p != &amp;src[size])
                    CRC(fcs, *p++);
                *(uint32_t *)p = htonl(fcs);
                size += 4;
            `}`
```

这处循环CRC校验会处理4096大小的数据。



```
[----------------------------------registers-----------------------------------]
RAX: 0x55b25f34c430 --&gt; 0x5452563412005452 //buffer
RBX: 0x1000//大小 
[-------------------------------------code-------------------------------------]
   0x55b25db4e66c &lt;pcnet_receive+1261&gt;:mov    DWORD PTR [rbp-0xd4],0xffffffff
   0x55b25db4e676 &lt;pcnet_receive+1271&gt;:mov    rax,QWORD PTR [rbp-0x98]
   0x55b25db4e67d &lt;pcnet_receive+1278&gt;:mov    QWORD PTR [rbp-0xb8],rax
=&gt; 0x55b25db4e684 &lt;pcnet_receive+1285&gt;:
    jmp    0x55b25db4e6ce &lt;pcnet_receive+1359&gt;
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Thread 3 "qemu-system-x86" hit Breakpoint 10, pcnet_receive (
    nc=0x55b2603bca20, buf=0x55b25f34c430 "RT", size_=0x1000)
    at /home/sh1/Desktop/qemu/hw/net/pcnet.c:1080
1080                while (p != &amp;src[size])
```

每一轮循环p都会自加1，循环结束后p会到0x1000的位置，随后会进行一处赋值，赋值的内容是htonl(fcs)，长度是4字节，而这4字节的内容会超过s-&gt;buffer的大小，可以回头看一下之前我发的关于PCNetState_st结构体的值，在s-&gt;buffer之后跟的是irq结构。

根据之前我们跟踪对*src = s-&gt;buffer的汇编代码，我们可以看到buffer的偏移是0x2290，而buffer的长度是0x1000，buffer 的下一个变量是irq结构，buffer是0x2290 + 0x1000 = 0x3290 + 0x55b25f34a1a0 = 0x55b25f34d430



```
gdb-peda$ x/10x 0x55B25F34D400
0x55b25f34d400:0x00000000000000000x0000000000000000
0x55b25f34d410:0x00000000000000000x0000000000000000
0x55b25f34d420:0x00000000000000000xfe7193d400000000
0x55b25f34d430:0x000055b2603bc910
```

可以看到0x55b25f34d430位置存放的正是irq的指针（结合我之前发的结构体中irq变量的值），接下来我们来看p=htonl(fcs)赋值操作。这里fcs是可控的，我们把它的值设置为0xdeadbeef，因为是PoC仅用于验证，而真实利用，请参考phrack文中的利用方法。



```
[----------------------------------registers-----------------------------------]
RAX: 0xdeadbeef //eax的值是deadbeef
RBX: 0x1000 
[-------------------------------------code-------------------------------------]
   0x55b25db4e6f2 &lt;pcnet_receive+1395&gt;:call   0x55b25d936078
=&gt; 0x55b25db4e6f7 &lt;pcnet_receive+1400&gt;:mov    edx,eax
   0x55b25db4e6f9 &lt;pcnet_receive+1402&gt;:mov    rax,QWORD PTR [rbp-0xb8]
 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db4e6f71082                *(uint32_t *)p = htonl(fcs);
[----------------------------------registers-----------------------------------]
RAX: 0x55b25f34d430 --&gt; 0x55b2603bc910 --&gt; 0x55b25f18a3f0 --&gt; 0x55b25f1564a0 --&gt; 0x55b25f156620 --&gt; 0x717269 ('irq')//目标地址
RDX: 0xdeadbeef //拷贝内容
[-------------------------------------code-------------------------------------]
=&gt; 0x55b25db4e700 &lt;pcnet_receive+1409&gt;:mov    DWORD PTR [rax],edx
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055b25db4e7001082                *(uint32_t *)p = htonl(fcs);
gdb-peda$ x/10x 0x55b25f34d430//拷贝前
0x55b25f34d430:0x000055b2603bc9100x000055b25db4be11
0x55b25f34d440:0x000055b25db4bdd90x000055b25f349920
0x55b25f34d450:0x00000001000000010x000055b25f182850
0x55b25f34d460:0x00000000000000000x000055b25ff0d760
0x55b25f34d470:0x000055b2603bc7300x0000000000000001
gdb-peda$ si//拷贝后
[----------------------------------registers-----------------------------------]
RAX: 0x55b25f34d430 --&gt; 0x55b2deadbeef 
RDX: 0xdeadbeef [-------------------------------------code-------------------------------------]
   0x55b25db4e700 &lt;pcnet_receive+1409&gt;:mov    DWORD PTR [rax],edx
=&gt; 0x55b25db4e702 &lt;pcnet_receive+1411&gt;:add    DWORD PTR [rbp-0xe4],0x4
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
1083                size += 4;
gdb-peda$ x/10x 0x55b25f34d430//拷贝结束后deadbeef覆盖了irq结构
0x55b25f34d430:0x000055b2deadbeef0x000055b25db4be11
```

当我们覆盖irq结构后，在pcnet_receive函数结束时更新irq结构，调用关系是pcnet_receive()-&gt;pcnet_update_irq()-&gt;qemu_set_irq()



```
RDI: 0x55b2deadbeef 
   0x55b25db4d31d &lt;pcnet_update_irq+497&gt;:mov    esi,edx
   0x55b25db4d31f &lt;pcnet_update_irq+499&gt;:mov    rdi,rax
=&gt; 0x55b25db4d322 &lt;pcnet_update_irq+502&gt;:
    call   0x55b25daf6c86 &lt;qemu_set_irq&gt;
```

这时，irq的值已经被覆盖了，我们跟入qemu_set_irq，这个函数在/path/to/qemu/hw/core/irq.c中。



```
gdb-peda$ disas qemu_set_irq
Dump of assembler code for function qemu_set_irq:
   0x000055b25daf6c86 &lt;+0&gt;:push   rbp
   0x000055b25daf6c87 &lt;+1&gt;:mov    rbp,rsp
   0x000055b25daf6c8a &lt;+4&gt;:sub    rsp,0x10
   0x000055b25daf6c8e &lt;+8&gt;:mov    QWORD PTR [rbp-0x8],rdi
   0x000055b25daf6c92 &lt;+12&gt;:mov    DWORD PTR [rbp-0xc],esi
   0x000055b25daf6c95 &lt;+15&gt;:cmp    QWORD PTR [rbp-0x8],0x0
   0x000055b25daf6c9a &lt;+20&gt;:je     0x55b25daf6cbd &lt;qemu_set_irq+55&gt;
=&gt; 0x000055b25daf6c9c &lt;+22&gt;:mov    rax,QWORD PTR [rbp-0x8]
   0x000055b25daf6ca0 &lt;+26&gt;:mov    rax,QWORD PTR [rax+0x30]
   0x000055b25daf6ca4 &lt;+30&gt;:mov    rdx,QWORD PTR [rbp-0x8]
   0x000055b25daf6ca8 &lt;+34&gt;:mov    esi,DWORD PTR [rdx+0x40]
   0x000055b25daf6cab &lt;+37&gt;:mov    rdx,QWORD PTR [rbp-0x8]
   0x000055b25daf6caf &lt;+41&gt;:mov    rcx,QWORD PTR [rdx+0x38]
   0x000055b25daf6cb3 &lt;+45&gt;:mov    edx,DWORD PTR [rbp-0xc]
   0x000055b25daf6cb6 &lt;+48&gt;:mov    rdi,rcx
   0x000055b25daf6cb9 &lt;+51&gt;:call   rax
   0x000055b25daf6cbb &lt;+53&gt;:jmp    0x55b25daf6cbe &lt;qemu_set_irq+56&gt;
   0x000055b25daf6cbd &lt;+55&gt;:nop
   0x000055b25daf6cbe &lt;+56&gt;:leave  
   0x000055b25daf6cbf &lt;+57&gt;:ret    
End of assembler dump.
```

这里rax会作为s-&gt;irq被引用，+0x30位置存放的是handler，这个值会作为一个函数被引用，可以看上面汇编call rax，这也正是我们可以通过构造fake irq结构体来控制rip的方法，而这里由于0xdeadbeef的覆盖，引用的是无效地址，从而引发了异常，导致qemu崩溃。



```
gdb-peda$ x/10x 0x55b2deadbeef 
0x55b2deadbeef:Cannot access memory at address 0x55b2deadbeef
gdb-peda$ si
Thread 3 "qemu-system-x86" received signal SIGSEGV, Segmentation fault.
```



**0x04 补丁对比**

QEMU针对这两个CVE漏洞进行了修补，首先是CVE-2015-5165的patch，在rtl8139_cplus_transmit_one函数中，在be16_to_cpu(ip-&gt;ip_len)-hlen之间做了一个判断，首先是单独执行be16_to_cpu()。



```
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RDI: 0x1300 //ip-&gt;ip_len
[-------------------------------------code-------------------------------------]
   0x5599f558bd83 &lt;rtl8139_cplus_transmit_one+2020&gt;:movzx  eax,ax
   0x5599f558bd86 &lt;rtl8139_cplus_transmit_one+2023&gt;:mov    edi,eax
=&gt; 0x5599f558bd88 &lt;rtl8139_cplus_transmit_one+2025&gt;:
    call   0x5599f55881f7 &lt;be16_to_cpu&gt;
   0x5599f558bd8d &lt;rtl8139_cplus_transmit_one+2030&gt;:
    mov    WORD PTR [rbp-0x14a],ax
   0x5599f558bd94 &lt;rtl8139_cplus_transmit_one+2037&gt;:
    movzx  eax,WORD PTR [rbp-0x14a]
   0x5599f558bd9b &lt;rtl8139_cplus_transmit_one+2044&gt;:
    cmp    eax,DWORD PTR [rbp-0x118]
   0x5599f558bda1 &lt;rtl8139_cplus_transmit_one+2050&gt;:
    jl     0x5599f558c5d5 &lt;rtl8139_cplus_transmit_one+4150&gt;
Guessed arguments:
arg[0]: 0x1300 
Legend: code, data, rodata, value
0x00005599f558bd882126            ip_data_len = be16_to_cpu(ip-&gt;ip_len);
```

在be16_to_cpu之后，值仍然会变成0x13，但是不会直接和hlen相减，而是和hlen做了一个判断。



```
Legend: code, data, rodata, value
0x00005599f558bd9b2127            if (ip_data_len &lt; hlen || ip_data_len &gt; eth_payload_len) `{`
gdb-peda$ info register eax
eax            0x130x13
gdb-peda$ x 0x7f1f47693830-0x118
0x7f1f47693718:0x0000080000000014
```

如果小于，则会跳转到skip offload分支，直接将save_buffer交还缓冲区，并且增加计数，而不会进行后续处理。



```
gdb-peda$ si
[-------------------------------------code-------------------------------------]
   0x5599f558c5d1 &lt;rtl8139_cplus_transmit_one+4146&gt;:nop
   0x5599f558c5d2 &lt;rtl8139_cplus_transmit_one+4147&gt;:
    jmp    0x5599f558c5d5 &lt;rtl8139_cplus_transmit_one+4150&gt;
   0x5599f558c5d4 &lt;rtl8139_cplus_transmit_one+4149&gt;:nop
=&gt; 0x5599f558c5d5 &lt;rtl8139_cplus_transmit_one+4150&gt;:
    mov    rax,QWORD PTR [rbp-0x158]
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
2330        ++s-&gt;tally_counters.TxOk;
skip_offload:
        /* update tally counter */
        ++s-&gt;tally_counters.TxOk;
……
```

来看一下补丁前后的对比。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a5f7c81dc736a960.png)

关于CVE-2015-7504的修补在那个位置的上面增加了一处判断。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b53114b567643dd0.png)

这里对size的大小进行了判断，给4096字节的buffer留出了4字节存放fcs的值，这里有个比较有意思的事情，就是刚开始我以为这里修补了漏洞，但是我在这个函数下断点的时候，却意外的发现没有命中而是直接退出了。

所以好奇跟了一下，发现实际上真正封堵这个漏洞的是在外层调用pcnet_transmit函数中，在外层函数中会有另外一处判断。



```
gdb-peda$ p *(struct PCNetState_st*)0x55e53ecafc80
$2 = `{`
  ……
  xmit_pos = 0x0, 
  ……`}`
//关键判断
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0x1000 //bcnt
RDX: 0x0 //s-&gt;xmit_pos
EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x55e53c39cc26 &lt;pcnet_transmit+704&gt;:mov    rax,QWORD PTR [rbp-0x58]
   0x55e53c39cc2a &lt;pcnet_transmit+708&gt;:mov    edx,DWORD PTR [rax+0x218c]
   0x55e53c39cc30 &lt;pcnet_transmit+714&gt;:mov    eax,DWORD PTR [rbp-0x3c]
=&gt; 0x55e53c39cc33 &lt;pcnet_transmit+717&gt;:add    eax,edx
   0x55e53c39cc35 &lt;pcnet_transmit+719&gt;:cmp    eax,0xffc
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055e53c39cc331250        if (s-&gt;xmit_pos + bcnt &gt; sizeof(s-&gt;buffer) - 4) `{`
```

这里s-&gt;buffer的大小为4096，为它留出4字节的空间给CRC校验，也就是当我们长度设置为4096，这里xmit_pos为0，bcnt为4096，那么是不满足要求的，则在这里就进入异常处理。



```
[-------------------------------------code-------------------------------------]
   0x55e53c39cc35 &lt;pcnet_transmit+719&gt;:cmp    eax,0xffc
   0x55e53c39cc3a &lt;pcnet_transmit+724&gt;:
    jbe    0x55e53c39cc4f &lt;pcnet_transmit+745&gt;
   0x55e53c39cc3c &lt;pcnet_transmit+726&gt;:mov    rax,QWORD PTR [rbp-0x58]
=&gt; 0x55e53c39cc40 &lt;pcnet_transmit+730&gt;:
    mov    DWORD PTR [rax+0x218c],0xffffffff
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055e53c39cc401251            s-&gt;xmit_pos = -1;
gdb-peda$ p *(struct PCNetState_st*)0x55e53ecafc80
$2 = `{`
  ……
  xmit_pos = 0xffffffff, 
  ……`}`
```

而在后面的代码逻辑中，最后传入漏洞函数的size大小，就是s-&gt;xmit_pos+bcnt，因此外层函数一定满足size&lt;=4092的条件，似乎里面的修补显得没有那么必要了。因此我也不太明白为什么会修补了两处，但至少这样做，彻底将这里的Heap Buffer Overflow修补了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011692caa3ff2dc633.png)

这样我们完成了对PoC的调试，关于利用在phrack上的描述已经非常详细，只需要按照调试PoC的思路构造可控结构体，就可以完成最后的利用了。

[![](https://p0.ssl.qhimg.com/t01f87905823bd7aa25.png)](https://p0.ssl.qhimg.com/t01f87905823bd7aa25.png)

从虚拟机逃逸到宿主机获得宿主机权限的整个过程还是很有意思的，真的像从黑暗之门穿越到另一个世界，在内存中寻寻觅觅，最后一举突破的感觉非常棒。也希望自己未来能够挖到更多更强更高危的漏洞吧，请师傅们多多指正，感谢阅读！





**参考文章**

[http://www.phrack.org/papers/vm-escape-qemu-case-study.html](http://www.phrack.org/papers/vm-escape-qemu-case-study.html)

[http://bbs.pediy.com/thread-217997.htm](http://bbs.pediy.com/thread-217997.htm)

[http://bbs.pediy.com/thread-218045.htm](http://bbs.pediy.com/thread-218045.htm)

[http://bbs.pediy.com/thread-217999.htm](http://bbs.pediy.com/thread-217999.htm)

[http://www.freebuf.com/articles/87949.html](http://www.freebuf.com/articles/87949.html)
