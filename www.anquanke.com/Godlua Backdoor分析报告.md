> 原文链接: https://www.anquanke.com//post/id/181367 


# Godlua Backdoor分析报告


                                阅读量   
                                **227059**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t016ab45b25144edf47.jpg)](https://p5.ssl.qhimg.com/t016ab45b25144edf47.jpg)



## 背景介绍

2019年4月24号，360Netlab未知威胁检测系统发现一个可疑的ELF文件，目前有一部分杀软误识别为挖矿程序。通过详细分析，我们确定这是一款Lua-based Backdoor，因为这个样本加载的Lua字节码文件幻数为“God”，所以我们将它命名为Godlua Backdoor。

Godlua Backdoor会使用硬编码域名，Pastebin.com，GitHub.com和DNS TXT记录等方式，构建存储C2地址的冗余机制。同时，它使用HTTPS加密下载Lua字节码文件，使用DNS over HTTPS获取C2域名解析，保障Bot与Web Server和C2之间的安全通信。

我们观察到Godlua Backdoor实际上存在2个版本，并且有在持续更新。我们还观察到攻击者会通过Lua指令，动态运行Lua代码，并对一些网站发起HTTP Flood 攻击。

## 概览

目前，我们看到的Godlua Backdoor主要存在2个版本，201811051556版本是通过遍历Godlua下载服务器得到，我们没有看到它有更新。当前Godlua Backdoor活跃版本为20190415103713 ~ 2019062117473，并且它还在持续更新。它们都是通过C语言开发实现的Backdoor，不过后者能够适应更多的计算机平台以及支持更多的功能，以下是它们的详细对比图。

[![](https://p5.ssl.qhimg.com/t01f7204006e57ec230.png)](https://p5.ssl.qhimg.com/t01f7204006e57ec230.png)



## Godlua Backdoor逆向分析

### version 201811051556

这是我们发现Godlua Backdoor 早期实现的版本(201811051556)，它主要针对Linux平台，并支持2种C2指令，分别是执行Linux系统命令和自定义文件。

样本信息
- MD5: 870319967dba4bd02c7a7f8be8ece94f
ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.6.32, dynamically linked (uses shared libs), for GNU/Linux 2.6.32, stripped

**C2冗余机制**

我们发现它通过硬编码域名和Github项目描述2种方式来存储C2地址，这其实是一种C2冗余机制。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f3132980f9cbc073.png)

它的硬编码C2域名是: d.heheda.tk

[![](https://p1.ssl.qhimg.com/t01b98d82bb727873f7.png)](https://p1.ssl.qhimg.com/t01b98d82bb727873f7.png)

硬编码Github项目地址，并将C2信息存储在项目描述位置

[![](https://p0.ssl.qhimg.com/t01a8482f5f4b026b96.png)](https://p0.ssl.qhimg.com/t01a8482f5f4b026b96.png)

**C2指令**

cmd_call， 执行Linux系统命令

[![](https://p5.ssl.qhimg.com/t01e4e8f554c9a4a1d3.png)](https://p5.ssl.qhimg.com/t01e4e8f554c9a4a1d3.png)

cmd_shell，执行自定义文件

[![](https://p1.ssl.qhimg.com/t0105abf012351540e8.png)](https://p1.ssl.qhimg.com/t0105abf012351540e8.png)

**C2协议分析**

数据包格式

<td valign="bottom">LENGTH</td><td valign="bottom">TYPE</td><td valign="bottom">DATA</td>
|------
<td valign="bottom">Little endian,2 bytes</td><td valign="bottom">1 bytes</td><td valign="bottom">(Length -3) bytes</td>

1 bytes

**加密算法**

XOR 的Key是随机产生的16 bytes数据，算法为

[![](https://p5.ssl.qhimg.com/t01e480b63e83012f8a.png)](https://p5.ssl.qhimg.com/t01e480b63e83012f8a.png)

**数据包概览**



```
cmd_handshake

packet[0:31]:

24 00 02 ec 86 a3 23 fb d0 d1 e9 e8 5f 23 6f 6d

70 b5 95 24 44 e0 fc 2e 00 00 00 6c 69 6e 75 78

2d 78 38 36

Length:     packet[0:1]               ---&gt;0x0024

Type: packet[2]                 ---&gt;0x02,handshake

Data: packet[3:31]

            Data

            Data[0:15]                  ----&gt;xor key

            Data[16:23]                 ----&gt;version,hardcoded,little endian.

            Data[24:31]                 ----&gt;arch,hardcoded.

 

cmd_heartbeat

packet[0:10]:

0b 00 03 87 19 45 cb 91 d1 d1 a9

Length:             packet[0:1]                 ---&gt;0x000b

Type:         packet[2]                   ---&gt;0x03,heartbeat

Data:         packet[3:10]                ---&gt;xored clock64()
```

### version 20190415103713 ~ 20190621174731

它是Godlua Backdoor当前活跃版本，主要针对Windows和Linux平台，通过Lua实现主控逻辑并主要支持5种C2指令。

**样本信息**

version 20190415103713
- MD5: c9b712f6c347edde22836fb43b927633
ELF 64-bit LSB executable, AMD x86-64, version 1 (SYSV), statically linked, stripped

version 20190621174731
- MD5: 75902cf93397d2e2d1797cd115f8347a
ELF 64-bit LSB executable, AMD x86-64, version 1 (SYSV), statically linked, stripped

**C2冗余机制**

[![](https://p1.ssl.qhimg.com/t0183690b31210d98c1.png)](https://p1.ssl.qhimg.com/t0183690b31210d98c1.png)

**Stage-1 URL**

Stage-1 URL存储有3种冗余机制，分别是将该信息通过硬编码密文，Github项目描述和Pastebin文本存储。在解密得到Stage-1 URL后会下载start.png文件，它实际上是Lua字节码。Bot会把它加载到内存中并运行然后获取Stage-2 URL。

**加密算法**
- AES，CBC模式
- key：13 21 02 00 31 21 94 E2 F2 F1 35 61 93 4C 4D 6A
- iv：2B 7E 15 16 28 AE D2 01 AB F7 15 02 00 CF 4F 3C
**硬编码密文**

version 20190415103713
- AES密文：03 13 84 29 CC 8B A5 CA AB 05 9E 2F CB AF 5E E6 02 5A 5F 17 74 34 64 EA 5B F1 38 5B 8D B9 A5 3E
- Stage-1 URL明文：https://d.heheda.tk/%s.png
version 20190621174731
- AES密文：F1 40 DB B4 E1 29 D9 DC 8D 78 45 B9 37 2F 83 47 F1 32 3A 11 01 41 07 CD DB A3 7B 1F 44 A7 DE 6C 2C 81 0E 10 E9 D8 E1 03 38 68 FC 51 81 62 11 DD
- Stage-1 URL明文数据：https://img0.cloudappconfig.com/%s.png
**Github项目描述**
- AES密文：EC 76 44 29 59 3D F7 EE B3 01 90 A9 9C 47 C8 96 53 DE 86 CB DF 36 68 41 60 5C FA F5 64 60 5A E4 AE 95 C3 F5 A6 04 47 CB 26 47 A2 23 80 C6 5F 92
- Github URL明文：https://api.github.com/repos/helegedada/heihei
- 解密流程:
- [![](https://p2.ssl.qhimg.com/t01e9412fc012cd2dec.png)](https://p2.ssl.qhimg.com/t01e9412fc012cd2dec.png)
- Github项目描述密文: oTre1RVbmjqRn2kRrv4SF/l2WfMRn2gEHpqJz77btaDPlO0R9CdQtMM82uAes+Fb
- Stage-1 URL明文数据：https://img1.cloudappconfig.com/%s.png
**Pastebin文本**
<li>AES密文：19 31 21 32 BF E8 29 A8 92 F7 7C 0B DF DC 06 8E 8E 49 F0 50 9A 45 6C 53 77 69 2F 68 48<br>
DC 7F 28 16 EB 86 B3 50 20 D3 01 9D 23 6C A1 33 62 EC 15</li>
- Pastebin URL明文：https://pastebin.com/raw/vSDzq3Md
- 解密流程:
- [![](https://p5.ssl.qhimg.com/t012d770cb77faa1447.png)](https://p5.ssl.qhimg.com/t012d770cb77faa1447.png)
- Pastebin 文本密文：G/tbLY0TsMUnC+iO9aYm9yS2eayKlKLQyFPOaNxSCnZpBw4RLGnJOPcZXHaf/aoj
- Stage-1 URL明文数据：https://img2.cloudappconfig.com/%s.png
**Stage-2 URL**

Stage-2 URL存储有2种冗余机制，分别是将该信息通过Github项目文件和DNS TXT存储。在解密得到Stage-2 URL后会下载run.png文件，它也是Lua字节码。Bot会把它加载到内存中并运行然后获取Stage-3 C2。

**加密算法**
- AES，CBC模式
- key：22 85 16 13 57 2d 17 90 2f 00 49 18 5f 17 2b 0a
- iv：0d 43 36 41 86 41 21 d2 41 4e 62 00 41 19 4a 5c
**Github项目文件**
<li>Github URL明文存储在Lua字节码文件中（start.png），通过反汇编得到以下信息：<br>[![](https://p5.ssl.qhimg.com/t01d4ef72e814a4a315.png)](https://p5.ssl.qhimg.com/t01d4ef72e814a4a315.png)
</li>
<li>Github 文件密文：<br>
kI7xf+Q/fXC0UT6hCUNimtcH45gPgG9i+YbNnuDyHyh2HJqzBFQStPvHGCZH8Yoz9w02njr41wdl5VNlPCq18qTZUVco5WrA1EIg3zVOcY8=</li>
- Stage-2 URL明文数据：`{`“u”:”https:\/\/dd.heheda.tk\/%s.png”,”c”:”dd.heheda.tk::198.204.231.250:”`}`
DNS TXT
<li>DNS TXT信息存储在Lua字节码文件中（start.png），通过反汇编得到以下信息：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015e5527bf21b717fe.png)
</li>
<li>通过DNS over HTTPS请求获取DNS TXT记录：<br>[![](https://p2.ssl.qhimg.com/t019da76d805609d80a.png)](https://p2.ssl.qhimg.com/t019da76d805609d80a.png)
</li>
- DNS TXT密文： 6TmRMwDw5R/sNSEhjCByEw0Vb44nZhEUyUpUR4LcijfIukjdAv+vqqMuYOFAoOpC7Ktyyr6nUOqO9XnDpudVmbGoTeJD6hYrw72YmiOS9dX5M/sPNmsw/eY/XDYYzx5/
- Stage-2 URL明文数据：`{`“u”:”http:\/\/img1.cloudappconfig.com\/%s.png”,”c”:”img1.cloudappconfig.com::43.224.225.220:”`}`
**Stage-3 C2**

Stage-3 C2硬编码在Lua字节码文件中（run.png），通过反汇编得到以下信息

version 20190415103713

[![](https://p3.ssl.qhimg.com/t013bdff294c3e7346c.png)](https://p3.ssl.qhimg.com/t013bdff294c3e7346c.png)

version 20190621174731

[![](https://p0.ssl.qhimg.com/t01c2057f02e2b1392e.png)](https://p0.ssl.qhimg.com/t01c2057f02e2b1392e.png)

通过DNS Over HTTPS请求获取C2域名A记录

[![](https://p5.ssl.qhimg.com/t016196e37b645e698c.png)](https://p5.ssl.qhimg.com/t016196e37b645e698c.png)

**C2指令**

| CMD       | Type |

| ——— | —- |

| HANDSHAKE | 1    |

| HEARTBEAT | 2    |

| LUA       | 3    |

| SHELL     | 4    |

| UPGRADE   | 5    |

| QUIT      | 6    |

| SHELL2    | 7    |

| PROXY     | 8    |

**C2协议分析**

**数据包格式**

<td valign="bottom">TYPE</td><td valign="bottom">LENGTH</td><td valign="bottom">DATA</td>
|------
<td valign="bottom">1byte</td><td valign="bottom">Big endian,2 bytes</td><td valign="bottom">Length bytes</td>

Big endian,2 bytes

**数据包概览**
<li>HANDSHAKE<br>[![](https://p2.ssl.qhimg.com/t01dbf85c36fc13d40e.png)](https://p2.ssl.qhimg.com/t01dbf85c36fc13d40e.png)
</li>
Type: packet[0]         —&gt;0x01,HANDSHAKE

LENGTH:     packet[1:2]       —&gt;0x0010

Data: packet[3:end]

data[0:7]                  —&gt;Session

data[8:end]                —&gt;version,0x00125cfecd8bcb-&gt;20190621174731
<li>HEARTBEAT<br>[![](https://p4.ssl.qhimg.com/t01f824014651729d05.png)](https://p4.ssl.qhimg.com/t01f824014651729d05.png)
</li>
- Send:
-       Type:              packet[0]        —&gt;0x02,HEARTBEAT
-       Length:                 packet[1:2]      —&gt;0x4
-       Data:             packet[3:end]    —&gt;time,0x5d13779b,1561556891
- Replay:
-       Type:             packet[0]        —&gt;0x02,HEARTBEAT
-       Length:                 packet[1:2]      —&gt;0x4
-       Data:             packet[3:end]    —&gt;1561556891
<li>LUA Payload<br>[![](https://p1.ssl.qhimg.com/t01092196492ca8b0c6.png)](https://p1.ssl.qhimg.com/t01092196492ca8b0c6.png)
</li>
- Type:     packet[0]            —&gt;0x03,LUA
- Length:   packet[1:2]          —&gt;0x00ab
- Data:     packet[3:end]        —&gt;Lua script
我们可以观察到攻击者正在对www.liuxiaobei.top进行HTTP Flood攻击

[![](https://p0.ssl.qhimg.com/t011ef97788e80894a2.png)](https://p0.ssl.qhimg.com/t011ef97788e80894a2.png)

**Lua脚本分析**

Godlua Backdoor Bot样本在运行中会下载许多Lua脚本，可以分为运行，辅助，攻击3大类
- 运行：start.png,run.png,quit.png,watch.png,upgrade.png,proxy.png
- 辅助：packet.png,curl.png,util.png,utils.png
- 攻击：VM.png,CC.png
**加密算法**
- AES，CBC模式
- key：13 21 02 00 31 21 94 E2 F2 F1 35 61 93 4C 4D 6A
- iv：2B 7E 15 16 28 AE D2 01 AB F7 15 02 00 CF 4F 3C
**Lua幻数**

解密后的文件以upgrade.png为例，是pre-compiled code,高亮部分为文件头。

[![](https://p0.ssl.qhimg.com/t0133faa016b4d916a2.png)](https://p0.ssl.qhimg.com/t0133faa016b4d916a2.png)

可以发现幻数从Lua变成了God，虽然样本中有”$LuaVersion: God 5.1.4 C$$LuaAuthors: R. $”字串，但事实上，所采用的版本并不是5.1.4，具体版本无法确定，但可以肯定的是大于5.2。

**反编译**

为了反编译上述脚本，必须知道样本对Lua进行了哪些修改。经过分析，修改分为两大块，分别是：Lua Header 和 Lua Opcode。

通过Luadec[[1]](https://github.com/viruscamp/luadec)反编译效果图

[![](https://p0.ssl.qhimg.com/t0143e2f644658e0581.png)](https://p0.ssl.qhimg.com/t0143e2f644658e0581.png)



## 处置建议

我们还没有完全看清楚Godlua Backdoor的传播途径，但我们知道一些Linux用户是通过Confluence漏洞利用（CVE-2019-3396）感染的。如果我们的读者有更多的信息，欢迎联系我们。

我们建议读者对Godluad Backdoor相关IP，URL和域名进行监控和封锁。

### 联系我们

感兴趣的读者，可以在 [twitter](https://twitter.com/360Netlab) 或者在微信公众号 360Netlab 上联系我们。



## IoC list

### 样本MD5

870319967dba4bd02c7a7f8be8ece94f

c9b712f6c347edde22836fb43b927633

75902cf93397d2e2d1797cd115f8347a

### URL

https://helegedada.github.io/test/test

https://api.github.com/repos/helegedada/heihei

http://198.204.231.250/linux-x64

http://198.204.231.250/linux-x86

https://dd.heheda.tk/i.jpg

https://dd.heheda.tk/i.sh

https://dd.heheda.tk/x86_64-static-linux-uclibc.jpg

https://dd.heheda.tk/i686-static-linux-uclibc.jpg

https://dd.cloudappconfig.com/i.jpg

https://dd.cloudappconfig.com/i.sh

https://dd.cloudappconfig.com/x86_64-static-linux-uclibc.jpg

https://dd.cloudappconfig.com/arm-static-linux-uclibcgnueabi.jpg

https://dd.cloudappconfig.com/i686-static-linux-uclibc.jpg

http://d.cloudappconfig.com/i686-w64-mingw32/Satan.exe

http://d.cloudappconfig.com/x86_64-static-linux-uclibc/Satan

http://d.cloudappconfig.com/i686-static-linux-uclibc/Satan

http://d.cloudappconfig.com/arm-static-linux-uclibcgnueabi/Satan

https://d.cloudappconfig.com/mipsel-static-linux-uclibc/Satan

### C2 Domain

d.heheda.tk

dd.heheda.tk

c.heheda.tk

d.cloudappconfig.com

dd.cloudappconfig.com

c.cloudappconfig.com

f.cloudappconfig.com

t.cloudappconfig.com

v.cloudappconfig.com

img0.cloudappconfig.com

img1.cloudappconfig.com

img2.cloudappconfig.com

### IP

198.204.231.250          United States             ASN 33387                 DataShack, LC

104.238.151.101          Japan               ASN 20473           Choopa, LLC

43.224.225.220      Hong Kong             ASN 22769             DDOSING NETWORK
